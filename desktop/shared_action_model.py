import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse, unquote

from .saved_action_source import load_saved_action_source


ROOT_DIR = Path(__file__).resolve().parent.parent


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
)

SUPPORTED_ACTION_TARGET_KINDS = frozenset({"app", "folder", "file", "url"})


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


def _command_action_from_saved_record(record: object) -> CommandAction:
    if not isinstance(record, dict):
        raise ValueError("Saved action records must be objects.")

    target_kind = _require_saved_action_string(record, "target_kind").casefold()
    if target_kind not in SUPPORTED_ACTION_TARGET_KINDS:
        raise ValueError("Saved action target_kind is unsupported.")

    return CommandAction(
        id=_require_saved_action_string(record, "id"),
        title=_require_saved_action_string(record, "title"),
        target_kind=target_kind,
        target=_require_saved_action_string(record, "target"),
        aliases=_coerce_saved_action_aliases(record),
    )


def load_saved_command_actions(
    source_path: str | os.PathLike[str] | None = None,
) -> tuple[CommandAction, ...]:
    payload = load_saved_action_source(source_path)
    if payload is None:
        return ()

    try:
        seen_ids = {action.id.casefold() for action in DEFAULT_COMMAND_ACTIONS}
        seen_phrases: set[str] = set()
        for action in DEFAULT_COMMAND_ACTIONS:
            seen_phrases.update(_normalized_action_phrases(action))

        saved_actions: list[CommandAction] = []
        for record in payload.actions:
            action = _command_action_from_saved_record(record)
            normalized_id = action.id.casefold()
            if normalized_id in seen_ids:
                raise ValueError("Saved action id collides with an existing action.")

            normalized_phrases = _normalized_action_phrases(action)
            if normalized_phrases & seen_phrases:
                raise ValueError("Saved action title or alias collides with an existing action.")

            seen_ids.add(normalized_id)
            seen_phrases.update(normalized_phrases)
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
