"""Deterministic curation and reporting for the CPU-first corpus release."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import tempfile
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .fixtures import FixtureInput, extract_fixture
from .manifest import CorpusProject, artifact_id, load_manifest


IGNORED_PARTS = frozenset({".git", ".venv", "build", "dist", "node_modules", "vendor", "vendored", "third_party", "site-packages", "__pycache__"})


@dataclass(frozen=True)
class CuratedInput:
    project: CorpusProject
    relative: str
    fixture: FixtureInput
    source_hash: str
    split: str
    raw_hash: str = ""


@dataclass
class CurationReport:
    release: str
    projects: int
    retained_units: int = 0
    excluded: Counter[str] = field(default_factory=Counter)
    by_project: Counter[str] = field(default_factory=Counter)
    splits: dict[str, list[str]] = field(default_factory=dict)
    matched_paths: Counter[str] = field(default_factory=Counter)
    ledger: list[dict] = field(default_factory=list, repr=False)

    def as_dict(self) -> dict:
        return {"release": self.release, "projects": self.projects, "retained_units": self.retained_units,
                "excluded": dict(sorted(self.excluded.items())), "by_project": dict(sorted(self.by_project.items())),
                "matched_paths": dict(sorted(self.matched_paths.items())), "splits": self.splits}


def canonical_hash(source: str) -> str:
    """Hash syntax structure when possible, otherwise the exact invalid input."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            value = ast.dump(ast.parse(source), annotate_fields=True, include_attributes=False)
    except SyntaxError:
        value = source
    return hashlib.sha256(value.encode()).hexdigest()


def raw_hash(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def load_release(manifest_paths: list[str | Path]) -> list[CorpusProject]:
    records = [record for path in manifest_paths for record in load_manifest(path)]
    names = [record.name for record in records]
    if len(names) != len(set(names)):
        raise ValueError("release manifests contain duplicate project record names")
    return records


def stratified_splits(projects: list[CorpusProject]) -> dict[str, str]:
    """Stable group-level 70/15/15 assignment across broad corpus strata."""
    groups: dict[str, list[CorpusProject]] = defaultdict(list)
    for project in projects:
        groups[project.split_group or project.name].append(project)
    strata: dict[str, list[str]] = defaultdict(list)
    for group, members in groups.items():
        explicit = {member.partition for member in members if member.partition != "auto"}
        if len(explicit) > 1:
            raise ValueError(f"split group {group!r} has conflicting partitions")
        if explicit:
            continue
        tiers = {member.research_tier for member in members}
        roles = {member.corpus_role for member in members}
        category = ("defensive_security" if "defensive_security" in tiers else
                    "analysis_fixtures" if "analysis_fixtures" in tiers or "fixture" in roles else
                    "production")
        strata[category].append(group)
    mapping: dict[str, str] = {}
    for group, members in groups.items():
        explicit = {member.partition for member in members if member.partition != "auto"}
        if explicit:
            mapping[group] = explicit.pop()
    for group_names in strata.values():
        ordered = sorted(group_names, key=artifact_id)
        count = len(ordered)
        validation = max(1, round(count * 0.15)) if count >= 3 else 0
        test = max(1, round(count * 0.15)) if count >= 3 else 0
        train_end = count - validation - test
        for position, group in enumerate(ordered):
            mapping[group] = ("train" if position < train_end else
                              "validation" if position < count - test else "test")
    return mapping


def curated_inputs(projects: list[CorpusProject], checkout_root: Path, *, cap: int = 250,
                   release: str = "v0.2") -> tuple[list[CuratedInput], CurationReport]:
    splits = stratified_splits(projects)
    report = CurationReport(release, len(projects), splits={key: [] for key in ("train", "validation", "test")})
    candidates: list[tuple[CorpusProject, str, FixtureInput, str, str]] = []
    matched: Counter[str] = Counter()
    ledger_by_id: dict[str, dict] = {}
    for project in projects:
        checkout = checkout_root / project.name
        if not checkout.exists():
            raise FileNotFoundError(f"missing pinned checkout for {project.name}: {checkout}")
        from .corpus_builder import _tracked_source_paths
        for path in _tracked_source_paths(project, checkout):
            relative = path.relative_to(checkout).as_posix()
            if any(part in IGNORED_PARTS for part in Path(relative).parts):
                report.excluded["generated_or_vendor_path"] += 1
                report.ledger.append({"project": project.name, "path": relative,
                                      "disposition": "excluded", "reason": "generated_or_vendor_path"})
                continue
            matched[project.name] += 1
            report.matched_paths[project.name] += 1
            container = path.read_text(encoding="utf-8", errors="replace")
            inputs = extract_fixture(project.fixture_extractor, container) if project.fixture_extractor else [FixtureInput("source", container, {})]
            for fixture in inputs:
                structural, exact = canonical_hash(fixture.source), raw_hash(fixture.source)
                candidates.append((project, relative, fixture, structural, exact))
                ledger_id = artifact_id(project.name, relative, fixture.identifier)
                entry = {"id": ledger_id, "project": project.name, "path": relative,
                         "fixture": fixture.identifier, "raw_hash": exact,
                         "structural_hash": structural, "disposition": "candidate"}
                report.ledger.append(entry)
                ledger_by_id[ledger_id] = entry
        if not matched[project.name] and not project.allow_empty:
            raise ValueError(f"{project.name}: include patterns retained no source files")
        if not matched[project.name]:
            report.excluded["documented_empty_project"] += 1
            report.ledger.append({"project": project.name, "disposition": "excluded",
                                  "reason": "documented_empty_project",
                                  "detail": project.empty_reason})
    # Exact duplicates across projects are discarded deterministically. Same-project
    # fixture pairs remain available as labeled transformations.
    seen: dict[str, str] = {}
    retained_by_repository: dict[str, list[tuple[CorpusProject, str, FixtureInput, str, str]]] = defaultdict(list)
    for candidate in sorted(candidates, key=lambda item: artifact_id(item[0].name, item[1], item[2].identifier)):
        project, relative, fixture, digest, _exact = candidate
        repository = project.url.removesuffix(".git").lower()
        owner = seen.get(digest)
        if owner and owner != repository:
            report.excluded["cross_project_duplicate"] += 1
            key = artifact_id(project.name, relative, fixture.identifier)
            ledger_by_id[key].update(
                disposition="excluded", reason="cross_project_duplicate", duplicate_owner=owner)
            continue
        seen[digest] = repository
        retained_by_repository[repository].append(candidate)
    output: list[CuratedInput] = []
    selected_by_project: dict[str, list[tuple[CorpusProject, str, FixtureInput, str, str]]] = defaultdict(list)
    for repository, values in retained_by_repository.items():
        # Give each manifest role for a shared repository a floor before filling
        # unused capacity globally. This keeps implementation and fixture roles
        # represented without granting the repository multiple caps.
        by_record: dict[str, list[tuple[CorpusProject, str, FixtureInput, str, str]]] = defaultdict(list)
        for item in values:
            by_record[item[0].name].append(item)
        floor = cap // len(by_record)
        selected: list[tuple[CorpusProject, str, FixtureInput, str, str]] = []
        leftovers: list[tuple[CorpusProject, str, FixtureInput, str, str]] = []
        for name in sorted(by_record):
            ordered = sorted(by_record[name], key=lambda item: artifact_id(
                item[0].name, item[1], item[2].identifier))
            selected.extend(ordered[:floor])
            leftovers.extend(ordered[floor:])
        capacity = cap - len(selected)
        selected.extend(sorted(leftovers, key=lambda item: artifact_id(
            item[0].name, item[1], item[2].identifier))[:capacity])
        report.excluded["repository_cap"] += max(0, len(values) - len(selected))
        selected_ids = {artifact_id(item[0].name, item[1], item[2].identifier) for item in selected}
        for item in values:
            key = artifact_id(item[0].name, item[1], item[2].identifier)
            if key not in selected_ids:
                ledger_by_id[key].update(
                    disposition="excluded", reason="repository_cap")
        for candidate in selected:
            selected_by_project[candidate[0].name].append(candidate)
    for project in projects:
        selected = selected_by_project[project.name]
        split = splits[project.split_group or project.name]
        report.splits[split].append(project.name)
        for _, relative, fixture, digest, exact in selected:
            output.append(CuratedInput(project, relative, fixture, digest, split, exact))
            key = artifact_id(project.name, relative, fixture.identifier)
            ledger_by_id[key].update(
                disposition="retained", split=split)
            report.by_project[project.name] += 1
    report.retained_units = len(output)
    return output, report


def write_report(path: str | Path, report: CurationReport) -> None:
    path = Path(path)
    def atomic(target: Path, value: str) -> None:
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, target)
        finally:
            Path(temporary_name).unlink(missing_ok=True)
    atomic(path, json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n")
    ledger_path = path.with_name("curation-ledger.jsonl")
    atomic(ledger_path, "".join(json.dumps(item, sort_keys=True) + "\n"
                                for item in report.ledger))
    lines = [f"# Corpus curation {report.release}", "", f"- Manifest records: {report.projects}",
             f"- Retained source units: {report.retained_units}", "", "## Split records", ""]
    lines.extend(f"- {split}: {len(projects)} project records" for split, projects in sorted(report.splits.items()))
    lines.extend(["", "## Exclusions", ""])
    lines.extend(f"- {reason}: {count}" for reason, count in sorted(report.excluded.items()))
    atomic(path.with_suffix(".md"), "\n".join(lines) + "\n")
