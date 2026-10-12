from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from nexus_paths import EXTERNAL_STATE_ROOT

DEFAULT_EXTERNAL_STATE_ROOT = EXTERNAL_STATE_ROOT if os.name == "nt" else Path.home() / "Nexus Governance State"
DEFAULT_SCHEMA_VERSION = "external-state-v1"

STATE_DIRECTORIES = [
    "schemas",
    "locks",
    "central",
    "worktrees",
    "branches",
    "release_windows",
    "review_bundles",
    "cross_worktree_lessons",
    "governance_candidates",
    "promotion_packets",
    "acknowledgements",
    "snapshots",
    "audit_log",
]

REQUIRED_STATE_FIELDS = [
    "External State Schema",
    "State Version",
    "Last Updated",
    "Last Updated By",
    "Worktree",
    "Branch",
    "Source Repo HEAD",
]


class ExternalStateError(RuntimeError):
    """Raised when the external-state scaffold detects an unsafe operation."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_branch(repo: Path) -> str:
    try:
        return run_git(repo, "branch", "--show-current") or "DETACHED"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "UNKNOWN"


def git_head(repo: Path) -> str:
    try:
        return run_git(repo, "rev-parse", "HEAD")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "UNKNOWN"


def find_enclosing_git_root(path: Path) -> Path | None:
    current = resolve_path(path)
    candidates = [current, *current.parents]
    for candidate in candidates:
        if (candidate / ".git").exists():
            return candidate
    return None


def validate_canonical_root(root: Path, repo_paths: Iterable[Path] = ()) -> list[str]:
    issues: list[str] = []
    root = resolve_path(root)
    enclosing_git_root = find_enclosing_git_root(root)
    if enclosing_git_root is not None:
        issues.append(
            "External Root Location: INVALID - canonical root is inside a Git worktree "
            f"({enclosing_git_root})"
        )

    for repo_path in repo_paths:
        repo_path = resolve_path(repo_path)
        if is_relative_to(root, repo_path):
            issues.append(
                "External Root Location: INVALID - canonical root is inside supplied repo "
                f"({repo_path})"
            )

    root_name = root.name.lower()
    if root_name in {".nexus_state", ".nexus_local_state", ".nexus_state_staging"}:
        issues.append(
            "External Root Location: INVALID - repo-root ignored state folders are staging/scratch only"
        )

    return issues


def validate_initialized_root(root: Path, expected_schema: str = DEFAULT_SCHEMA_VERSION) -> list[str]:
    issues: list[str] = []
    root = resolve_path(root)
    manifest_path = root / "state_manifest.json"
    if not manifest_path.exists():
        return ["External State Missing: state_manifest.json missing - initialize root before applied operations"]

    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # noqa: BLE001 - report corrupt local state without traceback
        return [f"External State Corrupt: {manifest_path}: {exc}"]

    for field in REQUIRED_STATE_FIELDS:
        if field not in manifest:
            issues.append(f"External State Corrupt: state_manifest.json missing field: {field}")
    schema = manifest.get("External State Schema")
    if schema != expected_schema:
        issues.append(f"External State Schema Conflict: expected {expected_schema}, found {schema or 'MISSING'}")
    return issues


def state_manifest_payload(
    root: Path,
    worktree_label: str,
    repo: Path,
    branch: str,
    schema: str,
    created_by: str,
    initialization_scope: str,
) -> dict[str, object]:
    return {
        "External State Schema": schema,
        "State Version": 1,
        "Last Updated": utc_now(),
        "Last Updated By": created_by,
        "Worktree": worktree_label,
        "Branch": branch,
        "Source Repo HEAD": git_head(repo),
        "Root": str(resolve_path(root)),
        "Initialization Scope": initialization_scope,
        "Generated Index Rule": "state_index.md is generated report, not primary state",
    }


def atomic_write_text(path: Path, content: str) -> None:
    raise ExternalStateError("Retired legacy mutation route; use the selected checked Control Plane owner. --apply is not authority.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        delete=False,
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    ) as handle:
        handle.write(content)
        temp_name = handle.name
    os.replace(temp_name, path)


def atomic_write_bytes(path: Path, content: bytes) -> None:
    raise ExternalStateError("Retired legacy mutation route; use the selected checked Control Plane owner. --apply is not authority.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "wb",
        delete=False,
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    ) as handle:
        handle.write(content)
        temp_name = handle.name
    os.replace(temp_name, path)


def atomic_write_json(path: Path, payload: object) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ExternalStateError(f"{path} must contain a JSON object")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_state_files(root: Path) -> list[Path]:
    root = resolve_path(root)
    if not root.exists():
        return []
    state_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        directory = Path(dirpath)
        if directory == root:
            dirnames[:] = [dirname for dirname in dirnames if dirname != "snapshots"]
        for filename in filenames:
            if ".tmp" in filename:
                continue
            path = directory / filename
            if path.is_file():
                state_files.append(path)
    return sorted(state_files)


def copy_tree_snapshot(source: Path, destination: Path) -> list[dict[str, str]]:
    raise ExternalStateError("Retired legacy mutation route; use the selected checked Control Plane owner. --apply is not authority.")
    source = resolve_path(source)
    destination = resolve_path(destination)
    copied: list[dict[str, str]] = []
    for source_file in iter_state_files(source):
        relative = source_file.relative_to(source)
        target_file = destination / relative
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_file)
        copied.append(
            {
                "path": relative.as_posix(),
                "sha256": sha256_file(source_file),
            }
        )
    return copied


def new_lock_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
