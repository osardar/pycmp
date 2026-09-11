"""Normalize Python's authoritative AST into the common semantic graph."""
from __future__ import annotations

import ast
import hashlib
import sys
import warnings
from collections.abc import Iterable

from .semantic import GraphEdge, GraphNode, ProgramGraph
from .source_evidence import Bindings, field_evidence


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _semantic_kind(node: ast.AST) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        return "function"
    if isinstance(node, ast.ClassDef):
        return "class"
    if isinstance(node, ast.Call):
        return "call"
    if isinstance(node, ast.Name):
        return "symbol"
    if isinstance(node, ast.Constant):
        return "constant"
    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
        return "assignment"
    if isinstance(node, (ast.If, ast.IfExp, ast.Match)):
        return "branch"
    if isinstance(node, (ast.For, ast.AsyncFor, ast.While, ast.comprehension)):
        return "loop"
    if isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom, ast.Raise)):
        return "transfer"
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return "import"
    return "operation"


def _constant_category(value: object) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float, complex)):
        return "number"
    if isinstance(value, (str, bytes)):
        return "string"
    return type(value).__name__


class ASTNormalizer:
    """Creates a graph without preserving source-only syntax details."""

    lane = "ast"

    def parse(self, source: str, python_minor: int | None = None) -> ast.Module:
        kwargs: dict[str, object] = {"type_comments": True}
        if python_minor is not None:
            # CPython documents this as best effort. Exact old-version parsing is
            # performed by selecting a matching parser runtime at deployment.
            kwargs["feature_version"] = (3, python_minor)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            return ast.parse(source, mode="exec", **kwargs)

    def unit_graphs(
        self, source: str, *, origin: str, python_minor: int | None = None,
        extra_metadata: dict[str, object] | None = None,
    ) -> list[ProgramGraph]:
        tree = self.parse(source, python_minor)
        bindings = Bindings(tree)
        units: list[tuple[ast.AST, str, str]] = [(tree, "module", "<module>")]
        counts = {}
        def collect(node: ast.AST, prefix: str = "") -> None:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                local = getattr(node, "name", "<lambda>")
                qualified = f"{prefix}.{local}" if prefix else local
                counts[qualified] = counts.get(qualified, 0) + 1
                if counts[qualified] > 1:
                    qualified += "#" + str(counts[qualified])
                units.append((node, "class" if isinstance(node, ast.ClassDef) else "function", qualified))
                prefix = qualified
            for child in ast.iter_child_nodes(node):
                collect(child, prefix)

        collect(tree)
        references = {id(node): name for node, _, name in units}
        return [
            self._graph_for(node, origin=origin, name=name, unit_kind=kind,
                            extra_metadata=extra_metadata, bindings=bindings, references=references)
            for node, kind, name in units
        ]

    # Kept as a compatibility name; callers now receive all comparable units,
    # including the module and classes.
    function_graphs = unit_graphs

    def _graph_for(
        self, root: ast.AST, *, origin: str, name: str, unit_kind: str,
        extra_metadata: dict[str, object] | None,
        bindings: Bindings,
        references: dict[int, str],
    ) -> ProgramGraph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        definitions: dict[str, list[tuple[str, bool]]] = {}
        uses: list[tuple[str, str]] = []

        def visit(node: ast.AST, parent: str | None = None, field: str | None = None,
                  position: int | None = None) -> str:
            # CPython shares singleton Load/Store/operator objects. Object IDs
            # therefore cannot be used to allocate graph IDs.
            node_id = f"n{len(nodes)}"
            attrs: dict[str, object] = {"ast_type": type(node).__name__, "semantic_kind": _semantic_kind(node)}
            available = ["ast_type", "semantic_kind"]
            evidence = {**field_evidence(node), **bindings.attributes(node)}
            attrs.update(evidence)
            available.extend(evidence)
            if id(node) in references:
                attrs["unit_ref"] = references[id(node)]
                available.append("unit_ref")
            if hasattr(node, "lineno"):
                attrs.update(
                    line=getattr(node, "lineno"), column=getattr(node, "col_offset", 0),
                    end_line=getattr(node, "end_lineno", getattr(node, "lineno")),
                    end_column=getattr(node, "end_col_offset", getattr(node, "col_offset", 0)),
                )
                available.extend(("line", "column", "end_line", "end_column"))
            if isinstance(node, ast.Name):
                attrs["identifier_hash"] = _digest(node.id)
                attrs["name_context"] = type(node.ctx).__name__
                available.extend(("identifier_hash", "name_context"))
                if isinstance(node.ctx, ast.Load):
                    uses.append((attrs["binding_identity"], node_id))
            elif isinstance(node, ast.arg):
                attrs["identifier_hash"] = _digest(node.arg)
                attrs["name_context"] = "Parameter"
                available.extend(("identifier_hash", "name_context"))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                attrs["identifier_hash"] = _digest(node.name)
                available.append("identifier_hash")
            elif isinstance(node, ast.Constant):
                attrs["constant_category"] = _constant_category(node.value)
                available.append("constant_category")
            elif isinstance(node, ast.Attribute):
                attrs["attribute_hash"] = _digest(node.attr)
                available.append("attribute_hash")
            nodes.append(GraphNode(node_id, f"core:{attrs['semantic_kind']}", attrs, tuple(available)))
            if id(node) in bindings.declarations:
                definitions.setdefault(attrs["binding_identity"], []).append((node_id, isinstance(node, ast.arg)))
            if parent is not None:
                edge_attrs = {} if position is None else {"position": position}
                edge_available = ("ast_field",) if position is None else ("ast_field", "position")
                edges.append(GraphEdge(parent, node_id, f"ast_field:{field}", edge_available, edge_attrs))

            # A parent unit records a nested declaration, not a duplicate copy
            # of that declaration's entire implementation.
            nested = node is not root and id(node) in references
            fields = list(ast.iter_fields(node))
            # Assignment values are evaluated before their targets become new
            # bindings, unlike the storage-oriented field order exposed by AST.
            if isinstance(node, ast.Assign):
                fields.sort(key=lambda item: 0 if item[0] == "value" else 1)
            elif isinstance(node, ast.AnnAssign):
                fields.sort(key=lambda item: 1 if item[0] == "target" else 0)
            for child_field, value in fields:
                if nested and child_field == "body":
                    continue
                if isinstance(value, ast.AST):
                    visit(value, node_id, child_field)
                elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                    for index, item in enumerate(value):
                        if isinstance(item, ast.AST):
                            visit(item, node_id, child_field, index)
            return node_id

        visit(root)
        for binding, use in uses:
            for declaration, parameter in definitions.get(binding, []):
                if declaration != use:
                    edges.append(GraphEdge(declaration, use, "def_use" if parameter else "may_def_use",
                                           ("lexical_binding",), {"analysis": "not_reaching_definitions"}))
        metadata: dict[str, object] = {
            "lane": self.lane,
            "origin": origin,
            "parser": "python.ast",
            "parser_runtime": f"{sys.version_info.major}.{sys.version_info.minor}",
            "parse_status": "valid",
            "binding_analysis": "scope_candidates_not_reaching_definitions",
            "unresolved_analysis": ["branch_sensitive_dataflow", "runtime_dispatch", "annotation_scope_versions"],
            "field_policy": "all_ast_fields_retained_v1",
            "qualified_name": name,
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        graph = ProgramGraph(f"{origin}:{name}:{getattr(root, 'lineno', 1)}", unit_kind, nodes, edges, metadata)
        graph.validate()
        return graph
