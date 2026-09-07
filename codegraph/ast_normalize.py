"""Normalize Python's authoritative AST into the common semantic graph."""
from __future__ import annotations

import ast
import hashlib
import sys
import warnings
from collections.abc import Iterable

from .semantic import GraphEdge, GraphNode, ProgramGraph


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
        units: list[tuple[ast.AST, str, str]] = [(tree, "module", "<module>")]

        def collect(body: list[ast.stmt], prefix: str = "") -> None:
            for node in body:
                if isinstance(node, ast.ClassDef):
                    qualified = f"{prefix}.{node.name}" if prefix else node.name
                    units.append((node, "class", qualified))
                    collect(node.body, qualified)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    qualified = f"{prefix}.{node.name}" if prefix else node.name
                    units.append((node, "function", qualified))
                    collect(node.body, qualified)

        collect(tree.body)
        return [
            self._graph_for(node, origin=origin, name=name, unit_kind=kind,
                            extra_metadata=extra_metadata)
            for node, kind, name in units
        ]

    # Kept as a compatibility name; callers now receive all comparable units,
    # including the module and classes.
    function_graphs = unit_graphs

    def _graph_for(
        self, root: ast.AST, *, origin: str, name: str, unit_kind: str,
        extra_metadata: dict[str, object] | None,
    ) -> ProgramGraph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        definitions: dict[str, str] = {}

        def visit(node: ast.AST, parent: str | None = None, field: str | None = None,
                  position: int | None = None) -> str:
            # CPython shares singleton Load/Store/operator objects. Object IDs
            # therefore cannot be used to allocate graph IDs.
            node_id = f"n{len(nodes)}"
            attrs: dict[str, object] = {"ast_type": type(node).__name__, "semantic_kind": _semantic_kind(node)}
            available = ["ast_type", "semantic_kind"]
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
                if isinstance(node.ctx, ast.Load) and node.id in definitions:
                    edges.append(GraphEdge(definitions[node.id], node_id, "def_use",
                                           ("identifier_hash",)))
                elif isinstance(node.ctx, ast.Store):
                    definitions[node.id] = node_id
            elif isinstance(node, ast.arg):
                attrs["identifier_hash"] = _digest(node.arg)
                attrs["name_context"] = "Parameter"
                available.extend(("identifier_hash", "name_context"))
                definitions[node.arg] = node_id
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                attrs["identifier_hash"] = _digest(node.name)
                available.append("identifier_hash")
                definitions[node.name] = node_id
            elif isinstance(node, ast.Constant):
                attrs["constant_category"] = _constant_category(node.value)
                available.append("constant_category")
            elif isinstance(node, ast.Attribute):
                attrs["attribute_hash"] = _digest(node.attr)
                available.append("attribute_hash")
            nodes.append(GraphNode(node_id, f"core:{attrs['semantic_kind']}", attrs, tuple(available)))
            if parent is not None:
                edge_attrs = {} if position is None else {"position": position}
                edge_available = ("ast_field",) if position is None else ("ast_field", "position")
                edges.append(GraphEdge(parent, node_id, f"ast_field:{field}", edge_available, edge_attrs))

            # A parent unit records a nested declaration, not a duplicate copy
            # of that declaration's entire implementation.
            if node is not root and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                return node_id
            fields = list(ast.iter_fields(node))
            # Assignment values are evaluated before their targets become new
            # bindings, unlike the storage-oriented field order exposed by AST.
            if isinstance(node, ast.Assign):
                fields.sort(key=lambda item: 0 if item[0] == "value" else 1)
            elif isinstance(node, ast.AnnAssign):
                fields.sort(key=lambda item: 1 if item[0] == "target" else 0)
            for child_field, value in fields:
                if isinstance(value, ast.AST):
                    visit(value, node_id, child_field)
                elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                    for index, item in enumerate(value):
                        if isinstance(item, ast.AST):
                            visit(item, node_id, child_field, index)
            return node_id

        visit(root)
        metadata: dict[str, object] = {
            "lane": self.lane,
            "origin": origin,
            "parser": "python.ast",
            "parser_runtime": f"{sys.version_info.major}.{sys.version_info.minor}",
            "parse_status": "valid",
            "binding_analysis": "lexical_order_approximation",
            "qualified_name": name,
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        graph = ProgramGraph(f"{origin}:{name}:{getattr(root, 'lineno', 1)}", unit_kind, nodes, edges, metadata)
        graph.validate()
        return graph
