"""Lossless AST field evidence and conservative lexical binding candidates.

No program execution or dynamic import resolution occurs here. Scope candidates
are not reaching definitions, runtime call targets, or a control-flow analysis.
"""
from __future__ import annotations

import ast
import builtins
import hashlib
import json
from dataclasses import dataclass, field


def typed_value(value):
    if isinstance(value, ast.AST):
        return {"ast": type(value).__name__}
    if isinstance(value, list):
        return [typed_value(v) for v in value]
    if isinstance(value, tuple):
        return {"type": "tuple", "value": [typed_value(v) for v in value]}
    if isinstance(value, bytes):
        return {"type": "bytes", "value": value.hex()}
    if isinstance(value, int) and not isinstance(value, bool):
        return {"type": "int", "value": hex(value)}
    if isinstance(value, float):
        return {"type": "float", "value": value.hex()}
    if isinstance(value, complex):
        return {"type": "complex", "value": [value.real.hex(), value.imag.hex()]}
    if value is Ellipsis:
        return {"type": "ellipsis"}
    return {"type": type(value).__name__, "value": value}


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


# All fields are retained in ast_fields. These spellings are deliberately absent
# from scalar identity features; canonical lexical bindings carry their meaning.
LOCAL_FIELDS = {
    "Name": {"id"}, "arg": {"arg"}, "FunctionDef": {"name"},
    "AsyncFunctionDef": {"name"}, "ClassDef": {"name"}, "alias": {"asname"},
    "ExceptHandler": {"name"}, "Global": {"names"}, "Nonlocal": {"names"},
    "MatchAs": {"name"}, "MatchStar": {"name"}, "MatchMapping": {"rest"},
    "TypeVar": {"name"}, "ParamSpec": {"name"}, "TypeVarTuple": {"name"},
}


def field_evidence(node: ast.AST) -> dict:
    fields = {name: typed_value(value) for name, value in ast.iter_fields(node)}
    selected = {}
    for name, value in ast.iter_fields(node):
        if name in LOCAL_FIELDS.get(type(node).__name__, set()):
            continue
        if isinstance(node, ast.Constant) and name == "value":
            # Keep literal evidence independently maskable; do not duplicate its
            # value inside the general scalar fingerprint.
            continue
        # Positions, null slots, empty lists and AST-child kinds remain encoded;
        # scalar values are never silently skipped by traversal.
        selected[name] = typed_value(value)
    result = {"ast_fields": fields, "scalar_identity": digest(selected)}
    if isinstance(node, ast.Constant):
        result.update(literal_type=type(node.value).__name__,
                      literal_identity=digest(typed_value(node.value)))
    return result


def field_inventory() -> list[dict]:
    rows = []
    for name in sorted(dir(ast)):
        cls = getattr(ast, name)
        if isinstance(cls, type) and issubclass(cls, ast.AST) and getattr(cls, "_fields", ()):
            for key in cls._fields:
                rows.append({"node": name, "field": key, "storage": "ast_fields",
                             "encoding": "literal_type_and_identity" if name == "Constant" and key == "value" else
                             "binding_or_unresolved_metadata" if key in LOCAL_FIELDS.get(name, set()) else
                             "scalar_identity_and_child_edges"})
    return rows


@dataclass
class Scope:
    index: int
    kind: str
    parent: Scope | None
    slots: dict[str, int] = field(default_factory=dict)
    writes: dict[str, int] = field(default_factory=dict)
    imports: dict[str, str] = field(default_factory=dict)
    globals: set[str] = field(default_factory=set)
    nonlocals: set[str] = field(default_factory=set)
    dynamic: bool = False

    def declare(self, name: str):
        self.slots.setdefault(name, len(self.slots))
        self.writes[name] = self.writes.get(name, 0) + 1


class Bindings:
    def __init__(self, tree: ast.Module):
        self.scopes = [Scope(0, "module", None)]
        self.at = {}
        self.declarations = {}
        self.dynamic_calls = []
        self.walk(tree, self.scopes[0])
        for scope, name in self.dynamic_calls:
            if self.resolve(scope, name)[1] == "builtins." + name:
                scope.dynamic = True

    def child(self, kind, parent):
        scope = Scope(len(self.scopes), kind, parent)
        self.scopes.append(scope)
        return scope

    def declare(self, node, scope, name):
        scope.declare(name)
        self.declarations[id(node)] = (scope, name)

    def walk(self, node, scope, conditional=False):
        self.at[id(node)] = scope
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            if hasattr(node, "name"):
                self.declare(node, scope, node.name)
            child = self.child("class" if isinstance(node, ast.ClassDef) else "function", scope)
            if isinstance(node, ast.ClassDef):
                outer = [*node.bases, *node.keywords, *node.decorator_list]
            else:
                outer = [*getattr(node, "decorator_list", []), *node.args.defaults,
                         *[v for v in node.args.kw_defaults if v is not None]]
                if getattr(node, "returns", None):
                    outer.append(node.returns)
                self.at[id(node.args)] = child
                for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs,
                            *([node.args.vararg] if node.args.vararg else []),
                            *([node.args.kwarg] if node.args.kwarg else [])]:
                    self.at[id(arg)] = child
                    self.declare(arg, child, arg.arg)
                    if arg.annotation:
                        self.walk(arg.annotation, scope)
            for value in outer:
                self.walk(value, scope, conditional)
            for value in getattr(node, "type_params", []):
                self.walk(value, child)
            body = node.body if isinstance(node.body, list) else [node.body]
            for value in body:
                self.walk(value, child)
            return
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            child = self.child("comprehension", scope)
            for index, gen in enumerate(node.generators):
                self.at[id(gen)] = child
                self.walk(gen.iter, scope if index == 0 else child, conditional)
                self.walk(gen.target, child)
                for condition in gen.ifs:
                    self.walk(condition, child, True)
            for value in ([node.key, node.value] if isinstance(node, ast.DictComp) else [node.elt]):
                self.walk(value, child, True)
            return
        if isinstance(node, ast.NamedExpr) and scope.kind == "comprehension":
            owner = scope
            while owner.kind == "comprehension":
                owner = owner.parent
            self.walk(node.value, scope, conditional)
            self.walk(node.target, owner, conditional)
            return
        if isinstance(node, ast.Global):
            scope.globals.update(node.names)
        elif isinstance(node, ast.Nonlocal):
            scope.nonlocals.update(node.names)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            self.declare(node, scope, node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                self.at[id(alias)] = scope
                if alias.name == "*":
                    scope.dynamic = True
                    continue
                local = alias.asname or (alias.name.split(".")[0] if isinstance(node, ast.Import) else alias.name)
                self.declare(alias, scope, local)
                target = (alias.name if alias.asname else alias.name.split(".")[0]) if isinstance(node, ast.Import) else (
                    "." * node.level + (node.module or "") + "." + alias.name)
                if not conditional:
                    scope.imports[local] = target
            return
        elif isinstance(node, ast.ExceptHandler) and node.name:
            self.declare(node, scope, node.name)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            self.declare(node, scope, node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            self.declare(node, scope, node.rest)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"exec", "eval"}:
            # Decide only after all lexical declarations are known: a parameter
            # named eval/exec is not necessarily the dynamic builtin.
            self.dynamic_calls.append((scope, node.func.id))
        for child in ast.iter_child_nodes(node):
            self.walk(child, scope, conditional or isinstance(node, (ast.If, ast.For, ast.While, ast.Try,
                                                                    ast.TryStar, ast.Match, ast.AsyncFor)))

    def resolve(self, scope, name):
        origin = scope
        if name in scope.globals:
            scope = self.scopes[0]
        elif name in scope.nonlocals:
            scope = scope.parent
            while scope and (scope.kind == "class" or name not in scope.slots):
                scope = scope.parent
            if scope is None or scope.kind == "module":
                return "unresolved_nonlocal:" + name, None
        while scope:
            if scope.dynamic:
                return "dynamic_unresolved:" + name, None
            if name in scope.slots:
                binding = f"scope:{scope.index}:{scope.kind}:slot:{scope.slots[name]}"
                external = scope.imports.get(name) if scope.writes[name] == 1 else None
                return binding, external
            parent = scope.parent
            while parent and parent.kind == "class" and origin.kind != "class":
                parent = parent.parent
            scope = parent
        if name in vars(builtins):
            return "builtin:" + name, "builtins." + name
        return "unresolved:" + name, None

    def attributes(self, node):
        scope = self.at.get(id(node), self.scopes[0])
        names = []
        if id(node) in self.declarations:
            scope, name = self.declarations[id(node)]
            names = [name]
        elif isinstance(node, ast.Name):
            names = [node.id]
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            names = node.names
        result = {"scope_kind": scope.kind} if names else {}
        if names:
            resolved = [self.resolve(scope, name) for name in names]
            result["binding_identity"] = "|".join(binding for binding, _ in resolved)
            if len(resolved) == 1 and resolved[0][1]:
                result["external_identity"] = resolved[0][1]
            result["resolution"] = "lexical_candidate_not_runtime"
        if isinstance(node, ast.Attribute):
            base, attrs = node, []
            while isinstance(base, ast.Attribute):
                attrs.append(base.attr)
                base = base.value
            if isinstance(base, ast.Name):
                _, target = self.resolve(self.at.get(id(base), scope), base.id)
                if target:
                    result["external_identity"] = target + "." + ".".join(reversed(attrs))
                    result["resolution"] = "lexical_candidate_not_runtime"
        return result
