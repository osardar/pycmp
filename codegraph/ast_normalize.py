"""Normalize Python's authoritative AST into the common semantic graph."""
from __future__ import annotations

import ast
import hashlib
import sys
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
        return ast.parse(source, mode="exec", **kwargs)

    def function_graphs(
        self, source: str, *, origin: str, python_minor: int | None = None,
        extra_metadata: dict[str, object] | None = None,
    ) -> list[ProgramGraph]:
        tree = self.parse(source, python_minor)
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if not functions:
            return [self._graph_for(tree, origin=origin, name="<module>", extra_metadata=extra_metadata)]
        return [self._graph_for(node, origin=origin, name=node.name, extra_metadata=extra_metadata) for node in functions]

    def _graph_for(
        self, root: ast.AST, *, origin: str, name: str,
        extra_metadata: dict[str, object] | None,
    ) -> ProgramGraph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        ids: dict[int, str] = {}
        definitions: dict[str, str] = {}

        def visit(node: ast.AST, parent: str | None = None, field: str | None = None) -> str:
            node_id = f"n{len(ids)}"
            ids[id(node)] = node_id
            attrs: dict[str, object] = {"ast_type": type(node).__name__, "semantic_kind": _semantic_kind(node)}
            available = ["ast_type", "semantic_kind", "location"]
            if isinstance(node, ast.Name):
                attrs["identifier_hash"] = _digest(node.id)
                attrs["name_context"] = type(node.ctx).__name__
                available.extend(("identifier_hash", "name_context"))
                if isinstance(node.ctx, ast.Store):
                    definitions[node.id] = node_id
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                attrs["identifier_hash"] = _digest(node.name)
                available.append("identifier_hash")
                definitions[node.name] = node_id
            elif isinstance(node, ast.Constant):
                attrs["constant_category"] = _constant_category(node.value)
                available.append("constant_category")
            nodes.append(GraphNode(node_id, f"core:{attrs['semantic_kind']}", attrs, tuple(available)))
            if parent is not None:
                edges.append(GraphEdge(parent, node_id, f"ast_field:{field}", ("ast_field",)))
            for child_field, value in ast.iter_fields(node):
                if isinstance(value, ast.AST):
                    visit(value, node_id, child_field)
                elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                    for item in value:
                        if isinstance(item, ast.AST):
                            visit(item, node_id, child_field)
            return node_id

        visit(root)
        for node in nodes:
            identifier_hash = node.attributes.get("identifier_hash")
            if node.attributes.get("name_context") == "Load" and identifier_hash is not None:
                # Hashes prevent source identifiers becoming an accidental raw-data store.
                for raw_name, definition in definitions.items():
                    if _digest(raw_name) == identifier_hash:
                        edges.append(GraphEdge(definition, node.id, "def_use", ("identifier_hash",)))
                        break
        metadata: dict[str, object] = {
            "lane": self.lane,
            "origin": origin,
            "parser": "python.ast",
            "parser_runtime": f"{sys.version_info.major}.{sys.version_info.minor}",
            "parse_status": "valid",
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        return ProgramGraph(f"{origin}:{name}:{getattr(root, 'lineno', 1)}", "function", nodes, edges, metadata)
