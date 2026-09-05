"""Deduplicated local tickets for unsupported decompilation cases."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class DecompilerGap:
    bytecode_version: str
    tool_version: str
    failure_class: str
    sample_hash: str
    message: str

    @property
    def key(self) -> str:
        return hashlib.sha256("\0".join((self.bytecode_version, self.tool_version,
                                           self.failure_class, self.sample_hash)).encode()).hexdigest()


def append_gap(path: str | Path, gap: DecompilerGap) -> bool:
    path = Path(path)
    seen = set()
    if path.exists():
        for line in path.read_text().splitlines():
            if line:
                seen.add(json.loads(line)["key"])
    if gap.key in seen:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as output:
        output.write(json.dumps({"key": gap.key, **asdict(gap)}, sort_keys=True) + "\n")
    return True
