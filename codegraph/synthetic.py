"""Conservative, evidence-preserving training transformations."""
from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import io
import re
import tokenize
import unicodedata
import warnings

from .source_evidence import Bindings


@dataclass(frozen=True)
class TransformResult:
    source: str
    status: str
    reason: str = ""
    changed_bindings: int = 0


def _parse(source: str) -> ast.Module:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(source, type_comments=True)


def format_result(source: str) -> TransformResult:
    tree = _parse(source)
    formatted = ast.unparse(tree) + "\n"
    # Includes type comments, type-ignore locations, literal kinds and scalar
    # fields. If round-tripping discards evidence, do not emit a positive.
    if ast.dump(tree) != ast.dump(_parse(formatted)):
        return TransformResult(source, "unsupported", "ast_roundtrip_changes_evidence")
    return TransformResult(formatted, "applied" if formatted != source else "unchanged",
                           "" if formatted != source else "already_formatted")


def formatted_view(source: str) -> str:
    return format_result(source).source


def rename_result(source: str, *, seed_material: str) -> TransformResult:
    tree = _parse(source)
    nodes = list(ast.walk(tree))
    # These can observe local spellings. Dynamic/annotation scopes are excluded
    # rather than described as verified behavior-preserving positives.
    reflection = {"eval", "exec", "locals", "globals", "vars", "dir"}
    if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in reflection for n in nodes):
        return TransformResult(source, "unsupported", "dynamic_or_reflective_call")
    if any(isinstance(n, ast.Attribute) and n.attr in {"f_locals", "f_globals", "__code__", "_getframe", "currentframe"} for n in nodes):
        return TransformResult(source, "unsupported", "frame_or_code_introspection")
    if any(getattr(n, "type_params", ()) for n in nodes):
        return TransformResult(source, "unsupported", "annotation_scope_unverified")
    bindings = Bindings(tree)
    if any(s.dynamic for s in bindings.scopes):
        return TransformResult(source, "unsupported", "dynamic_scope")
    # Never rename public interfaces, imports, exception/pattern captures or
    # global/nonlocal targets. A lexical identity, not a spelling, is the key.
    blocked = set()
    blocked_names = set()
    for n in nodes:
        # String annotations, type comments and string-mediated lookup can refer
        # to local names without an ast.Name node. Leave those spellings alone.
        text = n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else getattr(n, "type_comment", None)
        if text:
            blocked_names.update(re.findall(r"\b\w+\b", text))
        if isinstance(n, (ast.Global, ast.Nonlocal)):
            blocked_names.update(n.names)
        if isinstance(n, ast.Name) and bindings.at[id(n)].kind == "class":
            blocked_names.add(n.id)  # class-body lookup is execution-order dependent
        if id(n) in bindings.declarations and not isinstance(n, ast.Name):
            blocked.add(bindings.attributes(n).get("binding_identity"))
    candidates = set()
    for n in nodes:
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            scope = bindings.at[id(n)]
            identity = bindings.attributes(n)["binding_identity"]
            if scope.kind == "function" and n.id not in blocked_names and identity not in blocked:
                candidates.add(identity)
    candidates = {c for c in candidates if c.startswith("scope:")}
    if not candidates:
        return TransformResult(source, "unchanged", "no_eligible_local_bindings")
    occupied = {unicodedata.normalize("NFKC", t.string) for t in tokenize.generate_tokens(io.StringIO(source).readline)
                if t.type == tokenize.NAME}
    mapping = {}
    index = 0
    for identity in sorted(candidates, key=lambda c: hashlib.sha256((seed_material+c).encode()).digest()):
        while f"local_{index}" in occupied:
            index += 1
        mapping[identity] = f"local_{index}"
        occupied.add(mapping[identity])
        index += 1
    # Patch only selected identifier spans in the original UTF-8 source. This
    # retains comments/type ignores, source lines, literal spelling and f-strings.
    lines = source.encode("utf-8").splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    raw = source.encode("utf-8")
    replacements = []
    expected = deepcopy(tree)
    expected_nodes = list(ast.walk(expected))
    for n, clone in zip(nodes, expected_nodes):
        if not isinstance(n, ast.Name):
            continue
        identity = bindings.attributes(n)["binding_identity"]
        if identity not in mapping:
            continue
        start = offsets[n.lineno-1] + n.col_offset
        end = offsets[n.end_lineno-1] + n.end_col_offset
        if unicodedata.normalize("NFKC", raw[start:end].decode()) != n.id:
            return TransformResult(source, "unsupported", "identifier_span_mismatch")
        replacements.append((start, end, mapping[identity].encode()))
        clone.id = mapping[identity]
    for start, end, replacement in sorted(set(replacements), reverse=True):
        raw = raw[:start] + replacement + raw[end:]
    renamed = raw.decode("utf-8")
    result_tree = _parse(renamed)
    if ast.dump(expected) != ast.dump(result_tree):
        return TransformResult(source, "unsupported", "unexpected_ast_change")
    after = Bindings(result_tree)
    # Check lexical correspondence independently after parsing the edited source.
    for a, b in zip(nodes, ast.walk(result_tree)):
        if isinstance(a, ast.Name):
            old, new = bindings.attributes(a), after.attributes(b)
            if any(old.get(k) != new.get(k) for k in ("binding_identity", "external_identity")):
                return TransformResult(source, "unsupported", "binding_correspondence_changed")
    return TransformResult(renamed, "applied", changed_bindings=len(mapping))


def renamed_view(source: str, *, seed_material: str) -> str:
    return rename_result(source, seed_material=seed_material).source


def damaged_view(source: str, *, severity: int = 1) -> str:
    """Create incomplete reconstruction, never a positive semantic clone."""
    lines = source.splitlines()
    keep = max(1, len(lines) - max(1, severity))
    return "\n".join(lines[:keep]) + "\n"
