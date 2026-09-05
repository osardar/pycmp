"""Tree-sitter recovery ingestion for source that cannot form a Python AST."""
from __future__ import annotations

import hashlib

from .semantic import GraphEdge, GraphNode, ProgramGraph


def recovery_graph(source: bytes, *, origin: str, reason: str) -> ProgramGraph:
    """Return a deliberately lower-confidence graph without pretending it is AST.

    Tree-sitter is error tolerant: ERROR nodes stay visible as recovery facts.
    This function is intentionally not a CST-to-AST conversion.
    """
    try:
        import tree_sitter_python
        from tree_sitter import Language, Parser
    except ImportError as exc:  # pragma: no cover - dependency error is actionable
        raise RuntimeError("tree-sitter-python is required for recovery ingestion") from exc
    parser = Parser(Language(tree_sitter_python.language()))
    tree = parser.parse(source)
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    errors = 0

    def visit(node, parent: str | None = None) -> None:
        nonlocal errors
        node_id = f"n{len(nodes)}"
        is_error = node.type == "ERROR" or node.is_missing
        if is_error:
            errors += 1
        attrs = {
            "syntax_type": node.type,
            "semantic_kind": "recovery_error" if is_error else "recovery_syntax",
            "byte_range": [node.start_byte, node.end_byte],
        }
        if node.type == "identifier":
            attrs["identifier_hash"] = hashlib.sha256(node.text).hexdigest()[:16]
        nodes.append(GraphNode(node_id, f"core:{attrs['semantic_kind']}", attrs,
                               tuple(attrs.keys())))
        if parent is not None:
            edges.append(GraphEdge(parent, node_id, "recovery_child", ("recovery",)))
        for child in node.children:
            visit(child, node_id)

    visit(tree.root_node)
    return ProgramGraph(
        f"{origin}:recovery", "function", nodes, edges,
        {
            "lane": "recovery",
            "origin": origin,
            "parser": "tree-sitter-python",
            "parse_status": "recovered",
            "parse_reason": reason,
            "error_count": errors,
            "confidence": "low",
        },
    )
