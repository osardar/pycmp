"""Dose-controlled static source recipes for the corpus similarity benchmark.

These recipes never execute source.  They are intentionally separate from the
owned-fixture obfuscator and from the production graph pipeline.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
import hashlib
import io
import math
import re
import tokenize
import unicodedata

from .source_evidence import Bindings
from .synthetic import format_result


RECIPE_VERSION = "corpus-related-v1"
DOSES = (0.1, 0.3, 0.6)
SEEDS = (0, 1, 2)
FAMILIES = ("rename", "literal", "operator", "structural", "partial", "combined")


@dataclass
class RecipeResult:
    source: str
    family: str
    seed: int | None = None
    requested_dose: float | None = None
    status: str = "applied"
    reason: str = ""
    eligible_count: int = 0
    actual_edit_count: int = 0
    changed_spans: list[dict] = field(default_factory=list)
    stages: list[dict] = field(default_factory=list)
    recipe_version: str = RECIPE_VERSION

    def record(self) -> dict:
        value = asdict(self)
        value.pop("source")
        return value


def _parse(source: str) -> ast.Module:
    return ast.parse(source, type_comments=True)


def _stable_key(seed: int, identity: str) -> bytes:
    return hashlib.sha256(f"{RECIPE_VERSION}\0{seed}\0{identity}".encode()).digest()


def select_nested(identities: list[str], dose: float, seed: int, *, maximum: int | None = None) -> set[str]:
    """Select a deterministic prefix, making the 10/30/60% sets nested."""
    if dose not in DOSES:
        raise ValueError(f"unsupported dose: {dose}")
    ordered = sorted(set(identities), key=lambda value: (_stable_key(seed, value), value))
    count = min(len(ordered), max(1, math.ceil(len(ordered) * dose))) if ordered else 0
    if maximum is not None:
        count = min(count, maximum)
    return set(ordered[:count])


def _line_offsets(source: str) -> tuple[bytes, list[int]]:
    raw = source.encode("utf-8")
    offsets = [0]
    for line in raw.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return raw, offsets


def _span(node: ast.AST, offsets: list[int]) -> tuple[int, int]:
    return (offsets[node.lineno - 1] + node.col_offset,
            offsets[node.end_lineno - 1] + node.end_col_offset)


def _patch(source: str, replacements: list[tuple[int, int, bytes, str]]) -> tuple[str, list[dict]]:
    raw = source.encode("utf-8")
    spans = []
    for start, end, replacement, identity in sorted(replacements, reverse=True):
        before = raw[start:end]
        raw = raw[:start] + replacement + raw[end:]
        spans.append({"start_byte": start, "end_byte": end, "identity": identity,
                      "before_sha256": hashlib.sha256(before).hexdigest(),
                      "after_sha256": hashlib.sha256(replacement).hexdigest()})
    return raw.decode("utf-8"), sorted(spans, key=lambda row: row["start_byte"])


def _finish(result: RecipeResult) -> RecipeResult:
    if result.actual_edit_count == 0 and result.status == "applied":
        result.status, result.reason = "unchanged", "no_selected_change"
    if result.status == "applied":
        try:
            _parse(result.source)
        except (SyntaxError, ValueError) as exc:
            result.status, result.reason = "validation_failed", type(exc).__name__
    return result


def unchanged(source: str) -> RecipeResult:
    _parse(source)
    return RecipeResult(source, "unchanged", status="unchanged", reason="control")


def formatting(source: str) -> RecipeResult:
    transformed = format_result(source)
    return RecipeResult(transformed.source, "formatting", status=transformed.status,
                        reason=transformed.reason, actual_edit_count=int(transformed.source != source))


def _rename_candidates(tree: ast.Module) -> tuple[Bindings, list[ast.AST], dict[str, list[ast.Name]], str]:
    nodes = list(ast.walk(tree))
    reflection = {"eval", "exec", "locals", "globals", "vars", "dir"}
    if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in reflection for n in nodes):
        return Bindings(tree), nodes, {}, "dynamic_or_reflective_call"
    if any(isinstance(n, ast.Attribute) and n.attr in
           {"f_locals", "f_globals", "__code__", "_getframe", "currentframe"} for n in nodes):
        return Bindings(tree), nodes, {}, "frame_or_code_introspection"
    bindings = Bindings(tree)
    if any(scope.dynamic for scope in bindings.scopes):
        return bindings, nodes, {}, "dynamic_scope"
    blocked_names: set[str] = set()
    blocked: set[str | None] = set()
    for node in nodes:
        text = (node.value if isinstance(node, ast.Constant) and isinstance(node.value, str)
                else getattr(node, "type_comment", None))
        if text:
            blocked_names.update(re.findall(r"\b\w+\b", text))
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            blocked_names.update(node.names)
        if isinstance(node, ast.Name) and bindings.at[id(node)].kind == "class":
            blocked_names.add(node.id)
        if id(node) in bindings.declarations and not isinstance(node, ast.Name):
            blocked.add(bindings.attributes(node).get("binding_identity"))
    candidates: dict[str, list[ast.Name]] = {}
    declared: set[str] = set()
    for node in nodes:
        if isinstance(node, ast.Name):
            identity = bindings.attributes(node).get("binding_identity", "")
            scope = bindings.at[id(node)]
            if (isinstance(node.ctx, ast.Store) and scope.kind == "function" and
                    node.id not in blocked_names and identity not in blocked and identity.startswith("scope:")):
                declared.add(identity)
    for node in nodes:
        if isinstance(node, ast.Name):
            identity = bindings.attributes(node).get("binding_identity", "")
            if identity in declared:
                candidates.setdefault(identity, []).append(node)
    return bindings, nodes, candidates, ""


def rename(source: str, dose: float, seed: int) -> RecipeResult:
    tree = _parse(source)
    bindings, _nodes, candidates, gap = _rename_candidates(tree)
    result = RecipeResult(source, "rename", seed, dose, eligible_count=len(candidates))
    if gap:
        result.status, result.reason = "unsupported", gap
        return result
    selected = select_nested(list(candidates), dose, seed)
    occupied = {unicodedata.normalize("NFKC", token.string) for token in
                tokenize.generate_tokens(io.StringIO(source).readline) if token.type == tokenize.NAME}
    mapping: dict[str, str] = {}
    index = 0
    for identity in sorted(selected, key=lambda value: (_stable_key(seed, value), value)):
        while f"related_{seed}_{index}" in occupied:
            index += 1
        mapping[identity] = f"related_{seed}_{index}"
        occupied.add(mapping[identity])
        index += 1
    raw, offsets = _line_offsets(source)
    replacements = []
    for identity, occurrences in candidates.items():
        if identity not in mapping:
            continue
        for node in occurrences:
            start, end = _span(node, offsets)
            if unicodedata.normalize("NFKC", raw[start:end].decode()) != node.id:
                result.status, result.reason = "validation_failed", "identifier_span_mismatch"
                return result
            replacements.append((start, end, mapping[identity].encode(), identity))
    result.source, result.changed_spans = _patch(source, replacements)
    result.actual_edit_count = len(selected)
    parsed = _parse(result.source)
    after = Bindings(parsed)
    for old, new in zip(ast.walk(tree), ast.walk(parsed)):
        if isinstance(old, ast.Name) and isinstance(new, ast.Name):
            if bindings.attributes(old).get("binding_identity") != after.attributes(new).get("binding_identity"):
                result.status, result.reason = "validation_failed", "binding_correspondence_changed"
                return result
    return _finish(result)


def _excluded_constants(tree: ast.Module) -> set[int]:
    excluded: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (isinstance(body, list) and body and isinstance(body[0], ast.Expr) and
                isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str)):
            excluded.add(id(body[0].value))
        for field in ("annotation", "returns"):
            value = getattr(node, field, None)
            if isinstance(value, ast.AST):
                excluded.update(id(item) for item in ast.walk(value) if isinstance(item, ast.Constant))
        if isinstance(node, ast.MatchValue):
            excluded.update(id(item) for item in ast.walk(node.value) if isinstance(item, ast.Constant))
        if isinstance(node, ast.MatchMapping):
            for key in node.keys:
                excluded.update(id(item) for item in ast.walk(key) if isinstance(item, ast.Constant))
    return excluded


def _changed_literal(value: object, seed: int) -> object:
    if isinstance(value, bool) or value is None or value is Ellipsis:
        return value
    if isinstance(value, int):
        return value + seed + 1
    if isinstance(value, float):
        return value + (seed + 1) / 10
    if isinstance(value, complex):
        return value + complex(seed + 1, 0)
    if isinstance(value, str):
        return value + f"__related_{seed}"
    if isinstance(value, bytes):
        return value + bytes([65 + seed])
    return value


def literal(source: str, dose: float, seed: int) -> RecipeResult:
    tree = _parse(source)
    raw, offsets = _line_offsets(source)
    excluded = _excluded_constants(tree)
    candidates = []
    for number, node in enumerate(n for n in ast.walk(tree) if isinstance(n, ast.Constant)):
        changed = _changed_literal(node.value, seed)
        if id(node) not in excluded and changed != node.value and hasattr(node, "end_lineno"):
            start, end = _span(node, offsets)
            candidates.append((f"literal:{start}:{end}:{number}", node, changed))
    selected = select_nested([item[0] for item in candidates], dose, seed)
    replacements = []
    for identity, node, changed in candidates:
        if identity in selected:
            start, end = _span(node, offsets)
            replacements.append((start, end, repr(changed).encode("utf-8"), identity))
    result = RecipeResult(source, "literal", seed, dose, eligible_count=len(candidates),
                          actual_edit_count=len(replacements))
    result.source, result.changed_spans = _patch(source, replacements)
    return _finish(result)


_OPERATORS = {"+": "-", "-": "+", "*": "//", "//": "*", "==": "!=", "!=": "==",
              "<": ">=", ">=": "<", ">": "<=", "<=": ">"}


def operator(source: str, dose: float, seed: int) -> RecipeResult:
    tree = _parse(source)
    raw, offsets = _line_offsets(source)
    candidates = []
    for node in ast.walk(tree):
        regions = []
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv)):
            regions.append((_span(node.left, offsets)[1], _span(node.right, offsets)[0]))
        elif isinstance(node, ast.Compare):
            left = node.left
            for op_node, right in zip(node.ops, node.comparators):
                if isinstance(op_node, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                    regions.append((_span(left, offsets)[1], _span(right, offsets)[0]))
                left = right
        for start, end in regions:
            text = raw[start:end].decode("utf-8")
            matches = [(m.start(), m.end(), m.group()) for m in re.finditer(r"//|==|!=|<=|>=|[+*<>-]", text)
                       if m.group() in _OPERATORS]
            if len(matches) == 1:
                begin, finish, token = matches[0]
                identity = f"operator:{start + begin}:{start + finish}:{token}"
                candidates.append((identity, start + begin, start + finish, _OPERATORS[token]))
    selected = select_nested([item[0] for item in candidates], dose, seed)
    replacements = [(start, end, replacement.encode(), identity)
                    for identity, start, end, replacement in candidates if identity in selected]
    result = RecipeResult(source, "operator", seed, dose, eligible_count=len(candidates),
                          actual_edit_count=len(replacements))
    result.source, result.changed_spans = _patch(source, replacements)
    return _finish(result)


def _indented_unparse(node: ast.AST, column: int) -> bytes:
    prefix = " " * column
    return ("\n".join(prefix + line if number else line
                      for number, line in enumerate(ast.unparse(node).splitlines()))).encode("utf-8")


def structural(source: str, dose: float, seed: int) -> RecipeResult:
    tree = _parse(source)
    _raw, offsets = _line_offsets(source)
    parents = {id(child): parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    def nested_in_if(node):
        parent = parents.get(id(node))
        while parent is not None:
            if isinstance(parent, ast.If):
                return True
            parent = parents.get(id(parent))
        return False
    # Excluding nested if-statements makes every dose prefix non-overlapping,
    # so independently selected source-span replacements cannot corrupt one another.
    candidates = [("if:%s:%s" % _span(node, offsets), node) for node in ast.walk(tree)
                  if isinstance(node, ast.If) and node.body and node.orelse and not nested_in_if(node)]
    selected = select_nested([item[0] for item in candidates], dose, seed)
    replacements = []
    for identity, node in candidates:
        if identity not in selected:
            continue
        changed = ast.If(test=ast.UnaryOp(op=ast.Not(), operand=node.test), body=node.orelse,
                         orelse=node.body)
        ast.copy_location(changed, node)
        start, end = _span(node, offsets)
        replacements.append((start, end, _indented_unparse(changed, node.col_offset), identity))
    result = RecipeResult(source, "structural", seed, dose, eligible_count=len(candidates),
                          actual_edit_count=len(replacements))
    result.source, result.changed_spans = _patch(source, replacements)
    return _finish(result)


def partial(source: str, dose: float, seed: int) -> RecipeResult:
    tree = _parse(source)
    _raw, offsets = _line_offsets(source)
    definitions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    candidates = [("definition:%s:%s" % _span(node, offsets), node) for node in definitions]
    selected = select_nested([item[0] for item in candidates], dose, seed,
                             maximum=max(0, len(definitions) - 1))
    replacements = []
    for identity, node in candidates:
        if identity in selected:
            start, end = _span(node, offsets)
            decorators = getattr(node, "decorator_list", ())
            if decorators:
                start = offsets[min(item.lineno for item in decorators) - 1]
            replacements.append((start, end, b"", identity))
    result = RecipeResult(source, "partial", seed, dose, eligible_count=len(candidates),
                          actual_edit_count=len(replacements))
    result.source, result.changed_spans = _patch(source, replacements)
    return _finish(result)


def combined(source: str, dose: float, seed: int) -> RecipeResult:
    current = source
    stages = []
    total = eligible = 0
    spans = []
    applied = False
    for function in (rename, structural, literal):
        stage = function(current, dose, seed)
        stages.append(stage.record())
        eligible += stage.eligible_count
        total += stage.actual_edit_count
        spans.extend({**span, "stage": stage.family} for span in stage.changed_spans)
        if stage.status == "validation_failed":
            return RecipeResult(source, "combined", seed, dose, "validation_failed",
                                f"{stage.family}:{stage.reason}", eligible, total, spans, stages)
        if stage.status == "applied":
            current, applied = stage.source, True
    return RecipeResult(current, "combined", seed, dose,
                        "applied" if applied else "unchanged",
                        "" if applied else "no_stage_applied", eligible, total, spans, stages)


REGISTRY = {"rename": rename, "literal": literal, "operator": operator,
            "structural": structural, "partial": partial, "combined": combined}


def transform(source: str, family: str, dose: float, seed: int) -> RecipeResult:
    if family not in REGISTRY:
        raise ValueError(f"unknown corpus recipe: {family}")
    return REGISTRY[family](source, dose, seed)
