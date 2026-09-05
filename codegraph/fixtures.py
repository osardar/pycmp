"""Extract labeled Python snippets from common upstream fixture containers."""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FixtureInput:
    identifier: str
    source: str
    metadata: dict[str, object]


def _labels(source: str) -> dict[str, object]:
    return {
        "expected_outcome": "diagnostic" if re.search(r"#\s*(?:E:|error\b)", source, re.I) else "accepted",
        "parse_expectation": "invalid" if "# invalid" in source.lower() else "unknown",
    }


def _mypy_cases(text: str) -> list[FixtureInput]:
    sections = list(re.finditer(r"(?m)^\[case\s+([^\]]+)\]\s*$", text))
    fixtures: list[FixtureInput] = []
    for position, match in enumerate(sections):
        body = text[match.end():sections[position + 1].start() if position + 1 < len(sections) else len(text)]
        # Expected output and auxiliary-file sections are metadata, not source.
        body = re.split(r"(?m)^\[(?:out|file |fixture |builtins |typing )[^\]]*\]\s*$", body)[0].strip()
        if body:
            fixtures.append(FixtureInput(match.group(1), body, {"fixture_case": match.group(1), **_labels(body)}))
    return fixtures


def _markdown_blocks(text: str) -> list[FixtureInput]:
    fixtures: list[FixtureInput] = []
    for number, match in enumerate(re.finditer(r"(?ms)^```(?:python|py)\s*\n(.*?)^```\s*$", text), 1):
        source = match.group(1).strip()
        if source:
            fixtures.append(FixtureInput(f"block-{number}", source, {"fixture_case": f"block-{number}", **_labels(source)}))
    return fixtures


def _black_pair(text: str) -> list[FixtureInput]:
    parts = re.split(r"(?m)^#\s*output\s*$", text, maxsplit=1)
    if len(parts) != 2:
        return [FixtureInput("input", text, {"fixture_case": "input", **_labels(text)})]
    return [
        FixtureInput("input", parts[0].strip(), {"fixture_case": "input", "pair_role": "input", **_labels(parts[0])}),
        FixtureInput("output", parts[1].strip(), {"fixture_case": "output", "pair_role": "output", **_labels(parts[1])}),
    ]


def _call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _cpython_embedded(text: str) -> list[FixtureInput]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    fixtures: list[FixtureInput] = []
    for number, call in enumerate((node for node in ast.walk(tree) if isinstance(node, ast.Call)), 1):
        name = _call_name(call.func).lower()
        if not any(token in name for token in ("compile", "parse", "syntax", "exec", "eval")):
            continue
        for argument in call.args:
            if not isinstance(argument, ast.Constant) or not isinstance(argument.value, str):
                continue
            source = argument.value.strip()
            if "\n" not in source and not re.search(r"\b(?:def|class|import|assert|return|=)\b", source):
                continue
            metadata = {"fixture_case": f"embedded-{number}", "container_call": name, **_labels(source)}
            if "syntax" in name:
                metadata["parse_expectation"] = "invalid"
            fixtures.append(FixtureInput(f"embedded-{number}", source, metadata))
    return fixtures


def extract_fixture(kind: str, text: str) -> list[FixtureInput]:
    """Return independent snippets; unknown kinds intentionally fail closed."""
    extractors = {
        "mypy": _mypy_cases,
        "markdown": _markdown_blocks,
        "black": _black_pair,
        "cpython": _cpython_embedded,
    }
    if kind not in extractors:
        raise ValueError(f"unknown fixture extractor {kind!r}")
    return [fixture for fixture in extractors[kind](text) if fixture.source.strip()]
