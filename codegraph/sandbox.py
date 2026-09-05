"""Fail-closed Docker worker for all untrusted bytecode operations."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class SandboxUnavailable(RuntimeError):
    pass


def docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    probe = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=False)
    return probe.returncode == 0


def run_isolated(*, image: str, input_path: str | Path, command: list[str], timeout_seconds: int = 30) -> subprocess.CompletedProcess[str]:
    """Run a worker without network or writable host mounts.

    The image is intentionally caller-selected so a corpus can pin a worker per
    bytecode era. The input parent is mounted read-only at `/input`.
    """
    if not docker_available():
        raise SandboxUnavailable("Docker daemon is required for untrusted bytecode ingestion")
    source = Path(input_path).resolve()
    docker = [
        "docker", "run", "--rm", "--network", "none", "--read-only", "--user", "65534:65534",
        "--pids-limit", "64", "--memory", "512m", "--cpus", "1", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "-v", f"{source.parent}:/input:ro", image,
    ] + command
    return subprocess.run(docker, capture_output=True, text=True, check=False, timeout=timeout_seconds)
