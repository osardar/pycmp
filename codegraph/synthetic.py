"""Deterministic source transformations used as labeled training views."""
from __future__ import annotations

import ast
import hashlib
import random


def formatted_view(source: str) -> str:
    """AST round-trip; validates syntax without executing the source."""
    return ast.unparse(ast.parse(source)) + "\n"


class _LocalRenamer(ast.NodeTransformer):
    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)
        self.mapping: dict[str, str] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.mapping = {arg.arg: f"arg_{index}" for index, arg in enumerate(node.args.args)}
        return self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Name(self, node: ast.Name):
        if node.id in self.mapping:
            node.id = self.mapping[node.id]
        return node


def renamed_view(source: str, *, seed_material: str) -> str:
    tree = ast.parse(source)
    seed = int.from_bytes(hashlib.sha256(seed_material.encode()).digest()[:8], "big")
    tree = _LocalRenamer(seed).visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree) + "\n"


def damaged_view(source: str, *, severity: int = 1) -> str:
    """Create a deterministic incomplete reconstruction, never a positive semantic clone."""
    lines = source.splitlines()
    keep = max(1, len(lines) - max(1, severity))
    return "\n".join(lines[:keep]) + "\n"
