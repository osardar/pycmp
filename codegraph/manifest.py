"""Curated, reproducible corpus manifests and artifact identifiers."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class CorpusProject:
    name: str
    url: str
    revision: str
    license: str
    python_min: str = "3.4"
    python_max: str = "3.14"
    include: tuple[str, ...] = ("**/*.py",)
    exclude: tuple[str, ...] = ()
    research_tier: str = "standard"
    execution_policy: str = "static_only"

    def validate(self) -> None:
        if not self.name or not self.url or not self.revision:
            raise ValueError("manifest records require name, url, and immutable revision")
        permissive = {"MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC", "PSF-2.0"}
        special_tiers = {"defensive_security", "analysis_fixtures"}
        if self.license not in permissive and self.research_tier not in special_tiers:
            raise ValueError(f"{self.name}: non-permissive licenses require a static-only research tier")
        if self.research_tier in special_tiers and self.execution_policy != "static_only":
            raise ValueError(f"{self.name}: research-tier entries must be static_only")


def load_manifest(path: str | Path) -> list[CorpusProject]:
    records: list[CorpusProject] = []
    for line_number, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            raw = json.loads(line)
            for field in ("include", "exclude"):
                if field in raw:
                    raw[field] = tuple(raw[field])
            project = CorpusProject(**raw)
            project.validate()
            records.append(project)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
    names = [record.name for record in records]
    if len(names) != len(set(names)):
        raise ValueError("manifest project names must be unique")
    return records


def artifact_id(*parts: str) -> str:
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()[:24]


def write_lock(path: str | Path, projects: list[CorpusProject]) -> None:
    values = [asdict(project) for project in projects]
    Path(path).write_text(json.dumps({"format": 1, "projects": values}, indent=2, sort_keys=True) + "\n")
