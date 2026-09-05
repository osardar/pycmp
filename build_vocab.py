"""Build a global syntax-type feature vocabulary for pycmp.

A *global feature vocabulary* is a single, fixed mapping from syntax-type label
-> index, built once and reused for every graph. This is what lets one shared GCN
interpret its one-hot node features identically across files.

Two sources are supported:

  * ``--from-grammar``  Build from the tree-sitter-python grammar's
    ``node-types.json`` -- the authoritative, complete, corpus-independent list
    of every label the parser can emit (recommended). Default path:
    ``tree_sitter_python_node_types.json``.
  * (default)           Build from the union of labels found in one or more
    ``.graphml`` files (useful for inspecting what a small corpus actually uses).

This script needs no third-party dependencies: it uses only the standard library.

Usage:
    python3 build_vocab.py --from-grammar [node-types.json]
    python3 build_vocab.py [file.graphml ...]

Output:
    vocab.json  -- the persisted vocabulary (label_to_idx + metadata).
"""
from __future__ import annotations

import glob
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter

UNKNOWN = "<unknown>"
OUTPUT = "vocab.json"
DEFAULT_GRAMMAR = "tree_sitter_python_node_types.json"
# Must match the tree-sitter-python version pinned in requirements.txt, so the
# vocab lines up with the parser that produces the labels.
GRAMMAR_VERSION = "0.23.4"


def _local(tag: str) -> str:
    """Strip an XML namespace from a tag, e.g. '{ns}node' -> 'node'."""
    return tag.split("}", 1)[-1]


def extract_labels(path: str) -> list[str]:
    """Return the list of node ``label`` values in a .graphml file.

    Resolves the ``<key>`` whose ``attr.name == 'label'`` and collects the text
    of every ``<data>`` element that references it.
    """
    root = ET.parse(path).getroot()

    label_key_id = None
    for el in root.iter():
        if _local(el.tag) == "key" and el.get("for") == "node" \
                and el.get("attr.name") == "label":
            label_key_id = el.get("id")
    if label_key_id is None:
        raise ValueError(f"{path}: no node 'label' key found")

    return [(el.text or "").strip() for el in root.iter()
            if _local(el.tag) == "data" and el.get("key") == label_key_id]


def load_grammar_types(path: str) -> tuple[list[str], list[str]]:
    """Return ``(named, anonymous)`` type lists from a ``node-types.json`` file."""
    with open(path) as f:
        node_types = json.load(f)
    named = sorted(t["type"] for t in node_types if t.get("named"))
    anonymous = sorted(t["type"] for t in node_types if not t.get("named"))
    return named, anonymous


def make_label_to_idx(labels: list[str]) -> dict[str, int]:
    """Deterministic mapping: ``<unknown>`` at 0, then sorted labels from 1.

    Sorting makes the mapping independent of source order / which file was seen
    first, so the vocab is stable and reproducible.
    """
    label_to_idx = {UNKNOWN: 0}
    for i, label in enumerate(sorted(set(labels)), start=1):
        label_to_idx[label] = i
    return label_to_idx


def _write(vocab: dict) -> str:
    with open(OUTPUT, "w") as f:
        json.dump(vocab, f, indent=2)
        f.write("\n")
    return os.path.abspath(OUTPUT)


def build_from_grammar(grammar_path: str) -> dict:
    """Build the vocab from the full grammar (named + anonymous node types)."""
    named, anonymous = load_grammar_types(grammar_path)
    label_to_idx = make_label_to_idx(named + anonymous)
    vocab = {
        "version": 1,
        "source": "grammar",
        "grammar_version": GRAMMAR_VERSION,
        "unknown_token": UNKNOWN,
        "size": len(label_to_idx),
        "label_to_idx": label_to_idx,
        "named_types": named,
        "anonymous_types": anonymous,
        "source_files": [os.path.basename(grammar_path)],
    }
    out = _write(vocab)
    print(f"Built vocabulary from grammar: {os.path.basename(grammar_path)} "
          f"(tree-sitter-python {GRAMMAR_VERSION})")
    print(f"Named types:      {len(named)}")
    print(f"Anonymous types:  {len(anonymous)}")
    print(f"Total vocab size: {vocab['size']}  (incl. '{UNKNOWN}')")
    print(f"Wrote: {out}")
    return vocab


def build_from_corpus(paths: list[str]) -> dict:
    """Build the vocab from the union of labels in the given .graphml files."""
    counts: Counter[str] = Counter()
    for path in paths:
        counts.update(label for label in extract_labels(path) if label)

    label_to_idx = make_label_to_idx(counts)
    vocab = {
        "version": 1,
        "source": "corpus",
        "unknown_token": UNKNOWN,
        "size": len(label_to_idx),
        "label_to_idx": label_to_idx,
        "counts": dict(sorted(counts.items())),
        "source_files": [os.path.basename(p) for p in paths],
    }
    out = _write(vocab)
    print(f"Built vocabulary from: {', '.join(vocab['source_files'])}")
    print(f"Distinct syntax types: {vocab['size'] - 1}  (+ 1 reserved '{UNKNOWN}')")
    print(f"Total vocab size:      {vocab['size']}")
    print(f"Wrote: {out}")
    print()
    print(f"{'idx':>4}  {'count':>6}  label")
    print(f"{'-' * 4}  {'-' * 6}  {'-' * 20}")
    idx_to_label = {i: l for l, i in vocab["label_to_idx"].items()}
    for idx in range(vocab["size"]):
        label = idx_to_label[idx]
        print(f"{idx:>4}  {vocab['counts'].get(label, 0):>6}  {label}")
    return vocab


def main(argv: list[str]) -> None:
    if argv and argv[0] == "--from-grammar":
        grammar_path = argv[1] if len(argv) > 1 else DEFAULT_GRAMMAR
        if not os.path.exists(grammar_path):
            sys.exit(f"Grammar file not found: {grammar_path}")
        build_from_grammar(grammar_path)
    else:
        paths = argv or sorted(glob.glob("*.graphml"))
        if not paths:
            sys.exit("No .graphml files found (or pass --from-grammar).")
        build_from_corpus(paths)


if __name__ == "__main__":
    main(sys.argv[1:])
