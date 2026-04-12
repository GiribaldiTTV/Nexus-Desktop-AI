import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse, unquote

from .saved_action_source import (
    load_saved_action_source,
    resolve_default_saved_action_source_path,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SAVED_ACTION_SOURCE_PATH = resolve_default_saved_action_source_path()
DEFAULT_SAVED_ACTION_SOURCE_FOLDER = DEFAULT_SAVED_ACTION_SOURCE_PATH.parent


@dataclass(frozen=True)
class CommandAction:
    id: str
    title: str
    target_kind: str
    target: str
    aliases: tuple[str, ...]


DEFAULT_COMMAND_ACTIONS = (
    CommandAction(
        id="open_jarvis_workspace",
        title="Open Nexus Workspace",
        target_kind="folder",
        target=str(ROOT_DIR),
        aliases=(
            "open nexus workspace",
            "open nexus folder",
            "open workspace",
            "open jarvis workspace",
            "open jarvis folder",
        ),
    ),
    CommandAction(
        id="open_jarvis_docs",
        title="Open Nexus Docs",
        target_kind="folder",
        target=str(ROOT_DIR / "docs"),
        aliases=(
            "open nexus docs",
            "open docs",
            "open jarvis docs",
            "open jarvis folder",
            "open nexus folder",
        ),
    ),
    CommandAction(
        id="open_windows_explorer",
        title="Open Windows Explorer",
        target_kind="app",
        target="explorer.exe",
        aliases=("open windows explorer", "open file explorer", "windows explorer"),
    ),
    CommandAction(
        id="open_saved_actions_file",
        title="Open Saved Actions File",
        target_kind="file",
        target=str(DEFAULT_SAVED_ACTION_SOURCE_PATH),
        aliases=(
            "open saved actions file",
            "open saved actions json",
            "open saved actions config",
            "edit saved actions file",
        ),
    ),
    CommandAction(
        id="open_saved_actions_folder",
        title="Open Saved Actions Folder",
        target_kind="folder",
        target=str(DEFAULT_SAVED_ACTION_SOURCE_FOLDER),
        aliases=(
            "open saved actions folder",
            "open saved actions directory",
            "show saved actions folder",
        ),
    ),
)

SUPPORTED_ACTION_TARGET_KINDS = frozenset({"app", "folder", "file", "url"})
SUPPORTED_SAVED_ACTION_URL_SCHEMES = frozenset({"http", "https"})
LEGACY_SAVED_ACTIONS_ACCESS_ACTION_IDS = frozenset(
    {"open_saved_actions_file", "open_saved_actions_folder"}
)


class CommandActionCatalog:
    def __init__(self, actions: Iterable[CommandAction] = DEFAULT_COMMAND_ACTIONS):
        self._actions = tuple(actions)

    @property
    def actions(self) -> tuple[CommandAction, ...]:
        return self._actions

    def normalize_text(self, text: str) -> str:
        return normalize_command_text(text)

    def resolve_actions(self, text: str) -> tuple[CommandAction, ...]:
        return tuple(resolve_command_actions(text, self._actions))

    def format_target_display(self, target_kind: str, target: str, max_length: int = 72) -> str:
        return format_command_target_display(target_kind, target, max_length=max_length)


def normalize_command_text(text: str) -> str:
    normalized = (text or "").strip().casefold()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[.!?]+$", "", normalized)
    return normalized.strip()


def _normalized_action_phrases(action: CommandAction) -> set[str]:
    normalized_phrases: set[str] = set()
    for phrase in (action.title, *action.aliases):
        normalized = normalize_command_text(phrase)
        if not normalized:
            raise ValueError("Action phrases must be non-empty.")
        normalized_phrases.add(normalized)
    return normalized_phrases


LEGACY_SAVED_ACTIONS_ACCESS_ACTION_PHRASES = frozenset(
    normalized_phrase
    for action in DEFAULT_COMMAND_ACTIONS
    if action.id in LEGACY_SAVED_ACTIONS_ACCESS_ACTION_IDS
    for normalized_phrase in _normalized_action_phrases(action)
)


def _require_saved_action_string(record: dict, field_name: str) -> str:
    value = record.get(field_name)
    if not isinstance(value, str):
        raise ValueError(f"Saved action field '{field_name}' must be a string.")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"Saved action field '{field_name}' must not be empty.")
    return normalized


def _coerce_saved_action_aliases(record: dict) -> tuple[str, ...]:
    aliases = record.get("aliases", ())
    if aliases in (None, ""):
        return ()

    if not isinstance(aliases, (list, tuple)):
        raise ValueError("Saved action aliases must be a list of strings.")

    normalized_aliases: list[str] = []
    for alias in aliases:
        if not isinstance(alias, str):
            raise ValueError("Saved action aliases must contain only strings.")
        normalized = alias.strip()
        if not normalized:
            raise ValueError("Saved action aliases must not be empty.")
        normalized_aliases.append(normalized)

    return tuple(normalized_aliases)


def _validate_saved_action_target(target_kind: str, target: str) -> str:
    if target_kind != "url":
        return target

    if any(char.isspace() for char in target):
        raise ValueError("Saved action URL targets must not contain whitespace.")

    parsed = urlparse(target)
    if parsed.scheme.casefold() not in SUPPORTED_SAVED_ACTION_URL_SCHEMES or not parsed.netloc:
        raise ValueError("Saved action URL target must be an absolute http or https URL.")

    return target


def _command_action_from_saved_record(record: object) -> CommandAction:
    if not isinstance(record, dict):
        raise ValueError("Saved action records must be objects.")

    target_kind = _require_saved_action_string(record, "target_kind").casefold()
    if target_kind not in SUPPORTED_ACTION_TARGET_KINDS:
        raise ValueError("Saved action target_kind is unsupported.")

    target = _validate_saved_action_target(
        target_kind,
        _require_saved_action_string(record, "target"),
    )

    return CommandAction(
        id=_require_saved_action_string(record, "id"),
        title=_require_saved_action_string(record, "title"),
        target_kind=target_kind,
        target=target,
        aliases=_coerce_saved_action_aliases(record),
    )


def load_saved_command_actions(
    source_path: str | os.PathLike[str] | None = None,
) -> tuple[CommandAction, ...]:
    payload = load_saved_action_source(source_path)
    if payload is None:
        return ()

    try:
        built_in_ids = {action.id.casefold() for action in DEFAULT_COMMAND_ACTIONS}
        built_in_phrases: set[str] = set()
        for action in DEFAULT_COMMAND_ACTIONS:
            built_in_phrases.update(_normalized_action_phrases(action))

        seen_saved_ids: set[str] = set()
        seen_saved_phrases: set[str] = set()
        saved_actions: list[CommandAction] = []
        for record in payload.actions:
            action = _command_action_from_saved_record(record)
            normalized_id = action.id.casefold()
            normalized_phrases = _normalized_action_phrases(action)
            if normalized_id in seen_saved_ids:
                raise ValueError("Saved action id collides with another saved action.")
            if normalized_phrases & seen_saved_phrases:
                raise ValueError("Saved action title or alias collides with another saved action.")

            built_in_phrase_collisions = normalized_phrases & built_in_phrases
            if normalized_id in built_in_ids or built_in_phrase_collisions:
                # Preserve backward compatibility for users who already added these
                # same file/folder helpers manually before they became built-ins.
                incompatible_id_collision = (
                    normalized_id in built_in_ids
                    and normalized_id not in LEGACY_SAVED_ACTIONS_ACCESS_ACTION_IDS
                )
                incompatible_phrase_collision = bool(
                    built_in_phrase_collisions
                    - LEGACY_SAVED_ACTIONS_ACCESS_ACTION_PHRASES
                )
                if incompatible_id_collision or incompatible_phrase_collision:
                    raise ValueError("Saved action title or alias collides with an existing action.")
                continue

            seen_saved_ids.add(normalized_id)
            seen_saved_phrases.update(normalized_phrases)
            saved_actions.append(action)

        return tuple(saved_actions)
    except ValueError:
        return ()


def build_default_command_action_catalog(
    source_path: str | os.PathLike[str] | None = None,
) -> CommandActionCatalog:
    saved_actions = load_saved_command_actions(source_path)
    if not saved_actions:
        return CommandActionCatalog(DEFAULT_COMMAND_ACTIONS)

    return CommandActionCatalog((*DEFAULT_COMMAND_ACTIONS, *saved_actions))


DEFAULT_COMMAND_ACTION_CATALOG = build_default_command_action_catalog()


def resolve_command_actions(text: str, actions=DEFAULT_COMMAND_ACTIONS):
    normalized = normalize_command_text(text)
    if not normalized:
        return []

    matches = []
    for action in actions:
        candidates = (action.title, *action.aliases)
        if any(normalize_command_text(candidate) == normalized for candidate in candidates):
            matches.append(action)
    return matches


def launch_command_action(action: CommandAction):
    if action.target_kind == "url":
        os.startfile(action.target)
        return

    target = os.path.normpath(action.target)

    if action.target_kind == "app":
        subprocess.Popen([target], shell=False)
        return

    if action.target_kind == "folder":
        subprocess.Popen(["explorer.exe", target], shell=False)
        return

    os.startfile(target)


def format_command_target_display(target_kind: str, target: str, max_length: int = 72) -> str:
    target = (target or "").strip()
    if not target:
        return ""

    if target_kind in {"folder", "file"}:
        path = Path(target)
        normalized = str(path)
        if len(normalized) <= max_length:
            return normalized

        anchor = path.anchor
        parts = [part for part in path.parts if part and part != anchor]
        if not parts:
            return normalized

        tail_parts = parts[-3:] if len(parts) >= 3 else parts
        tail = "\\".join(tail_parts)
        if anchor:
            return f"{anchor}...\\{tail}"
        return f"...\\{tail}"

    if target_kind == "url":
        parsed = urlparse(target)
        if parsed.scheme and parsed.netloc:
            path = unquote(parsed.path or "")
            compact = f"{parsed.netloc}{path}"
            if parsed.query:
                compact += "?"
            if len(compact) <= max_length:
                return compact
            trimmed = path[-max(0, max_length - len(parsed.netloc) - 4):]
            return f"{parsed.netloc}...{trimmed}"

    if target_kind == "app":
        return Path(target).name or target

    if len(target) <= max_length:
        return target
    return f"{target[: max_length - 3]}..."
