"""Deterministic source transformations used as labeled training views."""
from __future__ import annotations

import ast
import hashlib
import warnings


def _parse(source: str) -> ast.Module:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(source)


def formatted_view(source: str) -> str:
    """AST round-trip; validates syntax without executing the source."""
    return ast.unparse(_parse(source)) + "\n"


class _LocalRenamer(ast.NodeTransformer):
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.scopes: list[dict[str, str]] = []

    def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        assigned: set[str] = set()
        blocked: set[str] = set()
        for statement in node.body:
            for child in ast.walk(statement):
                if child is not statement and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                    assigned.add(child.id)
                elif isinstance(child, (ast.Global, ast.Nonlocal)):
                    blocked.update(child.names)
        parameters = {
            arg.arg for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        }
        if node.args.vararg:
            parameters.add(node.args.vararg.arg)
        if node.args.kwarg:
            parameters.add(node.args.kwarg.arg)
        names = sorted(assigned - blocked - parameters)
        self.scopes.append({name: f"local_{index}" for index, name in enumerate(names)})
        node = self.generic_visit(node)
        self.scopes.pop()
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        return self._function(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Name(self, node: ast.Name):
        for mapping in reversed(self.scopes):
            if node.id in mapping:
                node.id = mapping[node.id]
                break
        return node


def renamed_view(source: str, *, seed_material: str) -> str:
    tree = _parse(source)
    seed = int.from_bytes(hashlib.sha256(seed_material.encode()).digest()[:8], "big")
    tree = _LocalRenamer(seed).visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree) + "\n"


def damaged_view(source: str, *, severity: int = 1) -> str:
    """Create a deterministic incomplete reconstruction, never a positive semantic clone."""
    lines = source.splitlines()
    keep = max(1, len(lines) - max(1, severity))
    return "\n".join(lines[:keep]) + "\n"
