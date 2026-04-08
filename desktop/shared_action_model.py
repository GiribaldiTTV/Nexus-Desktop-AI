import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse, unquote


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


DEFAULT_COMMAND_ACTION_CATALOG = CommandActionCatalog()


def normalize_command_text(text: str) -> str:
    normalized = (text or "").strip().casefold()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[.!?]+$", "", normalized)
    return normalized.strip()


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
