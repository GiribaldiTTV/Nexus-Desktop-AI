import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_SAVED_ACTION_FILENAME = "saved_actions.json"


@dataclass(frozen=True)
class SavedActionSourcePayload:
    path: Path
    actions: tuple[dict[str, Any], ...]


def resolve_default_saved_action_source_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        return Path(local_app_data) / "Nexus Desktop AI" / DEFAULT_SAVED_ACTION_FILENAME

    return Path.home() / "AppData" / "Local" / "Nexus Desktop AI" / DEFAULT_SAVED_ACTION_FILENAME


def load_saved_action_source(
    source_path: str | os.PathLike[str] | None = None,
) -> SavedActionSourcePayload | None:
    path = (
        Path(source_path)
        if source_path is not None
        else resolve_default_saved_action_source_path()
    )

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
