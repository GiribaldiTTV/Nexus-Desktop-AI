import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_SAVED_ACTION_FILENAME = "saved_actions.json"
DEFAULT_SAVED_ACTION_TEMPLATE = {
    "schema_version": 1,
    "actions": [],
    "examples": [
        {
            "id": "open_notepad",
            "title": "Open Notepad",
            "target_kind": "app",
            "target": "notepad.exe",
            "aliases": ["open notepad"],
        },
        {
            "id": "open_downloads",
            "title": "Open Downloads",
            "target_kind": "folder",
            "target": r"C:\Users\YourName\Downloads",
            "aliases": ["open downloads", "show downloads"],
        },
        {
            "id": "open_nexus_docs_site",
            "title": "Open Nexus Docs Site",
            "target_kind": "url",
            "target": "https://example.com/docs",
            "aliases": ["open nexus docs site", "open docs site"],
        },
    ],
}


@dataclass(frozen=True)
class SavedActionSourcePayload:
    path: Path
    actions: tuple[dict[str, Any], ...]


def resolve_default_saved_action_source_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        return Path(local_app_data) / "Nexus Desktop AI" / DEFAULT_SAVED_ACTION_FILENAME

    return Path.home() / "AppData" / "Local" / "Nexus Desktop AI" / DEFAULT_SAVED_ACTION_FILENAME


def _default_saved_action_source_text() -> str:
    return json.dumps(DEFAULT_SAVED_ACTION_TEMPLATE, indent=2) + "\n"


def ensure_saved_action_source_bootstrap(
    source_path: str | os.PathLike[str] | None = None,
) -> Path | None:
    path = (
        Path(source_path)
        if source_path is not None
        else resolve_default_saved_action_source_path()
    )

    try:
        if path.exists():
            return path if path.is_file() else None
    except OSError:
        return None

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_default_saved_action_source_text(), encoding="utf-8")
    except OSError:
        return None

    return path


def load_saved_action_source(
    source_path: str | os.PathLike[str] | None = None,
) -> SavedActionSourcePayload | None:
    path = (
        Path(source_path)
        if source_path is not None
        else resolve_default_saved_action_source_path()
    )

    # Bootstrap only the default runtime source so users get an explicit starter
    # file without widening fallback behavior for custom or validation-only paths.
    if source_path is None:
        bootstrapped_path = ensure_saved_action_source_bootstrap()
        if bootstrapped_path is not None:
            path = bootstrapped_path

    try:
        if not path.exists() or not path.is_file():
            return None
    except OSError:
        return None

    try:
        raw_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None

    if not raw_text.strip():
        return None

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    actions = payload.get("actions")
    if not isinstance(actions, list) or not actions:
        return None

    return SavedActionSourcePayload(path=path, actions=tuple(actions))
