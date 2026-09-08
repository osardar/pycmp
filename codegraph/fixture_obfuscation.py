"""Deterministic transformations scoped to the owned similarity fixtures.

These are not a general Python obfuscator: dynamic name lookup is outside the
fixture contract. The runner checks every output against executable oracles.
"""
from __future__ import annotations

import ast
import builtins
import hashlib


def obfuscate(modules: dict[str, str], *, level: str, seed: int) -> tuple[dict[str, str], dict]:
    if level not in {"light", "structural"}:
        raise ValueError("unknown obfuscation level")
    trees = {name: ast.parse(source) for name, source in modules.items()}
    names, reserved = set(), set(dir(builtins)) | {"run", "payload", "self", "cls"}
    # One injective map over the complete owned project preserves shadowing and
    # captured bindings. Imported external names and methods retain their APIs.
    for tree in trees.values():
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    reserved.add(alias.asname or alias.name.split(".")[0])
            if isinstance(node, ast.ClassDef):
                reserved.update(child.name for child in node.body
                                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)))
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                names.add(node.id)
            elif isinstance(node, ast.arg):
                names.add(node.arg)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
    mapping = {name: "_v" + hashlib.sha256(("%s:%s" % (seed, name)).encode()).hexdigest()[:12]
               for name in sorted(names - reserved)}
    if set(mapping.values()) & (names | reserved):
        raise ValueError("generated identifier collision")
    helper = "_identity_" + str(seed)

    class Transform(ast.NodeTransformer):
        def visit_Name(self, node):
            node.id = mapping.get(node.id, node.id)
            return node

        def visit_arg(self, node):
            node.arg = mapping.get(node.arg, node.arg)
            return self.generic_visit(node)

        def visit_keyword(self, node):
            node.arg = mapping.get(node.arg, node.arg)
            return self.generic_visit(node)

        def visit_ExceptHandler(self, node):
            node.name = mapping.get(node.name, node.name)
            return self.generic_visit(node)

        def visit_Global(self, node):
            node.names = [mapping.get(name, name) for name in node.names]
            return node

        visit_Nonlocal = visit_Global

        def definition(self, node):
            node.name = mapping.get(node.name, node.name)
            if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                node.body.pop(0)
                if not node.body:
                    node.body = [ast.Pass()]
            return self.generic_visit(node)

        visit_FunctionDef = definition
        visit_AsyncFunctionDef = definition
        visit_ClassDef = definition

        def visit_If(self, node):
            node = self.generic_visit(node)
            if level == "structural" and node.orelse:
                node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
                node.body, node.orelse = node.orelse, node.body
            return node

        def visit_Return(self, node):
            node = self.generic_visit(node)
            if level == "structural" and node.value is not None:
                node.value = ast.Call(func=ast.Name(id=helper, ctx=ast.Load()),
                                      args=[node.value], keywords=[])
            return node

        def visit_Match(self, node):
            # Pattern keys must remain literal strings; transform only guards
            # and bodies, which are normal expressions/statements.
            node.subject = self.visit(node.subject)
            for case in node.cases:
                for pattern in ast.walk(case.pattern):
                    if isinstance(pattern, (ast.MatchAs, ast.MatchStar)) and pattern.name:
                        pattern.name = mapping.get(pattern.name, pattern.name)
                if case.guard:
                    case.guard = self.visit(case.guard)
                case.body = [self.visit(statement) for statement in case.body]
            return node

        def visit_Constant(self, node):
            if level != "structural" or not isinstance(node.value, str):
                return node
            return ast.parse("''.join(chr(n) for n in %r)" %
                             [ord(character) for character in node.value], mode="eval").body

    output = {}
    for name, tree in trees.items():
        if (tree.body and isinstance(tree.body[0], ast.Expr) and
                isinstance(tree.body[0].value, ast.Constant) and
                isinstance(tree.body[0].value.value, str)):
            tree.body.pop(0)
        tree = Transform().visit(tree)
        if level == "structural":
            tree.body.extend(ast.parse("def %s(value):\n    return value\n" % helper).body)
        ast.fix_missing_locations(tree)
        rendered = ast.unparse(tree)
        # Compact indentation is valid in every targeted Python runtime.
        output[name] = "\n".join(
            " " * ((len(line) - len(line.lstrip())) // 4) + line.lstrip()
            for line in rendered.splitlines() if line.strip()) + "\n"
    return output, {"level": level, "seed": seed, "identifiers": mapping,
                    "transforms": ["identifier_rename", "layout", "remove_docstrings"] +
                    (["string_encoding", "conditional_inversion", "identity_helper"]
                     if level == "structural" else [])}


def negative_control(modules: dict[str, str]) -> dict[str, str]:
    """Near-copy control with one changed arithmetic result where possible."""
    output = dict(modules)
    tree = ast.parse(output["main.py"])
    changed = False
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
            node.op = ast.Sub() if isinstance(node.op, ast.Add) else ast.Add()
            changed = True
            break
    if changed:
        output["main.py"] = ast.unparse(tree) + "\n"
    else:
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "run":
                node.name = "_original_run"
        tree.body.extend(ast.parse(
            "def run(payload):\n    return [_original_run(payload), 'changed']\n").body)
        output["main.py"] = ast.unparse(tree) + "\n"
    return output
