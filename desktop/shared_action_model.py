import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Iterable
from urllib.parse import urlparse, unquote

from .saved_action_source import (
    inspect_saved_action_source,
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
    invocation_mode: str = "legacy"
    trigger_mode: str = ""
    custom_triggers: tuple[str, ...] = ()
    origin: str = "built_in"


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
SUPPORTED_APP_TARGET_EXTENSIONS = frozenset({".exe", ".com", ".bat", ".cmd"})
SUPPORTED_SAVED_ACTION_TRIGGER_MODES = frozenset({"launch", "open", "launch_and_open", "custom"})
SUPPORTED_SAVED_ACTION_INVOCATION_MODES = frozenset({"legacy", "aliases_only"})
LEGACY_SAVED_ACTIONS_ACCESS_ACTION_IDS = frozenset(
    {"open_saved_actions_file", "open_saved_actions_folder"}
)
INVALID_WINDOWS_PATH_CHARACTERS = frozenset('<>:"|?*')
RESERVED_WINDOWS_PATH_NAMES = frozenset(
    {
        "con",
        "prn",
        "aux",
        "nul",
        "conin$",
        "conout$",
        *(f"com{index}" for index in range(1, 10)),
        *(f"lpt{index}" for index in range(1, 10)),
    }
)
APP_COMMAND_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$", re.IGNORECASE)
DEFAULT_TRIGGER_MODE_BY_TARGET_KIND = {
    "app": "launch",
    "folder": "open",
    "file": "open",
    "url": "open",
}


@dataclass(frozen=True)
class SavedActionInventoryState:
    visible: bool = False
    status_kind: str = "hidden"
    status_text: str = ""
    guidance_text: str = ""
    path: str = ""
    actions: tuple[CommandAction, ...] = ()


@dataclass(frozen=True)
class CommandGroup:
    id: str
    title: str
    aliases: tuple[str, ...]
    member_action_ids: tuple[str, ...]
    member_actions: tuple[CommandAction, ...]
    origin: str = "saved"
    is_protected: bool = False


@dataclass(frozen=True)
class SavedGroupInventoryState:
    visible: bool = False
    status_kind: str = "hidden"
    status_text: str = ""
    guidance_text: str = ""
    path: str = ""
    groups: tuple[CommandGroup, ...] = ()


def format_action_origin_label(origin: str) -> str:
    if (origin or "").strip().casefold() == "saved":
        return "Saved"
    return "Built-in"


class CommandActionCatalog:
    def __init__(
        self,
        actions: Iterable[CommandAction] = DEFAULT_COMMAND_ACTIONS,
        *,
        saved_action_inventory: SavedActionInventoryState | None = None,
        groups: Iterable[CommandGroup] = (),
        saved_group_inventory: SavedGroupInventoryState | None = None,
    ):
        self._actions = tuple(actions)
        self._saved_action_inventory = saved_action_inventory or SavedActionInventoryState()
        self._groups = tuple(groups)
        self._saved_group_inventory = saved_group_inventory or SavedGroupInventoryState()

    @property
    def actions(self) -> tuple[CommandAction, ...]:
        return self._actions

    @property
    def saved_action_inventory(self) -> SavedActionInventoryState:
        return self._saved_action_inventory

    @property
    def groups(self) -> tuple[CommandGroup, ...]:
        return self._groups

    @property
    def saved_group_inventory(self) -> SavedGroupInventoryState:
        return self._saved_group_inventory

    def normalize_text(self, text: str) -> str:
        return normalize_command_text(text)

    def resolve_actions(self, text: str) -> tuple[CommandAction, ...]:
        return tuple(resolve_command_actions(text, self._actions))

    def resolve_group(self, text: str) -> CommandGroup | None:
        return resolve_command_group(text, self._groups)

    def format_target_display(self, target_kind: str, target: str, max_length: int = 72) -> str:
        return format_command_target_display(target_kind, target, max_length=max_length)


def normalize_command_text(text: str) -> str:
    normalized = (text or "").strip().casefold()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[.!?]+$", "", normalized)
    return normalized.strip()


def default_saved_action_trigger_mode(target_kind: str) -> str:
    return DEFAULT_TRIGGER_MODE_BY_TARGET_KIND.get((target_kind or "").strip().casefold(), "open")


def normalize_saved_action_trigger_mode(
    trigger_mode: object,
    *,
    target_kind: str,
    allow_empty: bool = False,
) -> str:
    if trigger_mode in (None, ""):
        if allow_empty:
            return ""
        return default_saved_action_trigger_mode(target_kind)

    if not isinstance(trigger_mode, str):
        raise ValueError("Saved action trigger mode must be a string.")

    normalized = trigger_mode.strip().casefold()
    if not normalized:
        if allow_empty:
            return ""
        return default_saved_action_trigger_mode(target_kind)
    if normalized not in SUPPORTED_SAVED_ACTION_TRIGGER_MODES:
        raise ValueError("Saved action trigger mode is unsupported.")
    return normalized


def normalize_saved_action_custom_triggers(
    custom_triggers: object,
    *,
    trigger_mode: str,
) -> tuple[str, ...]:
    if trigger_mode != "custom":
        if custom_triggers in (None, "", (), []):
            return ()
        if not isinstance(custom_triggers, (list, tuple)):
            raise ValueError("Saved action custom triggers must be a list of strings.")
        if any((str(item).strip() if isinstance(item, str) else item) for item in custom_triggers):
            raise ValueError("Saved action custom triggers require trigger mode 'custom'.")
        return ()

    if custom_triggers in (None, "", (), []):
        raise ValueError("Saved action custom triggers must contain at least one phrase.")
    if not isinstance(custom_triggers, (list, tuple)):
        raise ValueError("Saved action custom triggers must be a list of strings.")

    normalized_triggers: list[str] = []
    seen_normalized: set[str] = set()
    for phrase in custom_triggers:
        if not isinstance(phrase, str):
            raise ValueError("Saved action custom triggers must contain only strings.")

        normalized_phrase = re.sub(r"\s+", " ", phrase.strip())
        if not normalized_phrase:
            raise ValueError("Saved action custom triggers must not be empty.")

        normalized_key = normalize_command_text(normalized_phrase)
        if not normalized_key:
            raise ValueError("Saved action custom triggers must normalize to non-empty phrases.")
        if normalized_key in seen_normalized:
            raise ValueError("Saved action custom triggers must stay unique.")

        seen_normalized.add(normalized_key)
        normalized_triggers.append(normalized_phrase)

    return tuple(normalized_triggers)


def normalize_saved_action_invocation_mode(
    invocation_mode: object,
    *,
    allow_empty: bool = False,
) -> str:
    if invocation_mode in (None, ""):
        if allow_empty:
            return ""
        return "legacy"

    if not isinstance(invocation_mode, str):
        raise ValueError("Saved action invocation mode must be a string.")

    normalized = invocation_mode.strip().casefold()
    if not normalized:
        if allow_empty:
            return ""
        return "legacy"
    if normalized not in SUPPORTED_SAVED_ACTION_INVOCATION_MODES:
        raise ValueError("Saved action invocation mode is unsupported.")
    return normalized


def _trigger_prefixes_for_action(
    *,
    trigger_mode: str,
    custom_triggers: Iterable[str],
) -> tuple[str, ...]:
    if trigger_mode == "launch":
        return ("Launch",)
    if trigger_mode == "open":
        return ("Open",)
    if trigger_mode == "launch_and_open":
        return ("Launch", "Open")
    if trigger_mode == "custom":
        return tuple(re.sub(r"\s+", " ", phrase.strip()) for phrase in custom_triggers if phrase and phrase.strip())
    return ()


def build_saved_action_callable_phrases(
    title: str,
    aliases: Iterable[str] = (),
    *,
    invocation_mode: str = "legacy",
    trigger_mode: str = "",
    custom_triggers: Iterable[str] = (),
) -> tuple[str, ...]:
    phrases: list[str] = []
    seen_normalized: set[str] = set()

    def add_phrase(value: str):
        normalized_display = re.sub(r"\s+", " ", (value or "").strip())
        if not normalized_display:
            return
        normalized_key = normalize_command_text(normalized_display)
        if not normalized_key or normalized_key in seen_normalized:
            return
        seen_normalized.add(normalized_key)
        phrases.append(normalized_display)

    if invocation_mode == "aliases_only":
        base_phrases = tuple(phrase for phrase in tuple(aliases) if isinstance(phrase, str))
    else:
        base_phrases = tuple(phrase for phrase in (title, *tuple(aliases)) if isinstance(phrase, str))
    for phrase in base_phrases:
        add_phrase(phrase)

    for prefix in _trigger_prefixes_for_action(trigger_mode=trigger_mode, custom_triggers=custom_triggers):
        normalized_prefix = normalize_command_text(prefix)
        if not normalized_prefix:
            continue
        for phrase in base_phrases:
            normalized_phrase = normalize_command_text(phrase)
            if not normalized_phrase:
                continue
            if normalized_phrase == normalized_prefix or normalized_phrase.startswith(f"{normalized_prefix} "):
                add_phrase(phrase)
            else:
                add_phrase(f"{prefix} {phrase}")

    return tuple(phrases)


def build_callable_group_phrases(
    aliases: Iterable[str] = (),
) -> tuple[str, ...]:
    phrases: list[str] = []
    seen_normalized: set[str] = set()
    for alias in tuple(aliases):
        if not isinstance(alias, str):
            continue
        normalized_display = re.sub(r"\s+", " ", alias.strip())
        if not normalized_display:
            continue
        normalized_key = normalize_command_text(normalized_display)
        if not normalized_key or normalized_key in seen_normalized:
            continue
        seen_normalized.add(normalized_key)
        phrases.append(normalized_display)
    return tuple(phrases)


def _normalized_action_phrases(action: CommandAction) -> set[str]:
    normalized_phrases: set[str] = set()
    for phrase in build_saved_action_callable_phrases(
        action.title,
        action.aliases,
        invocation_mode=action.invocation_mode,
        trigger_mode=action.trigger_mode,
        custom_triggers=action.custom_triggers,
    ):
        normalized = normalize_command_text(phrase)
        if not normalized:
            raise ValueError("Action phrases must be non-empty.")
        normalized_phrases.add(normalized)
    return normalized_phrases


def _normalized_group_phrases(group: CommandGroup) -> set[str]:
    normalized_phrases: set[str] = set()
    for phrase in build_callable_group_phrases(group.aliases):
        normalized = normalize_command_text(phrase)
        if not normalized:
            raise ValueError("Callable group aliases must be non-empty.")
        normalized_phrases.add(normalized)
    return normalized_phrases


def _build_default_command_groups() -> tuple[CommandGroup, ...]:
    action_by_id = {
        action.id.casefold(): action
        for action in DEFAULT_COMMAND_ACTIONS
    }
    member_ids = tuple(
        action.id
        for action in DEFAULT_COMMAND_ACTIONS
        if action.id in {
            "open_jarvis_workspace",
            "open_jarvis_docs",
            "open_windows_explorer",
            "open_saved_actions_file",
            "open_saved_actions_folder",
        }
    )
    member_actions = tuple(
        action_by_id[action_id.casefold()]
        for action_id in member_ids
        if action_id.casefold() in action_by_id
    )
    return (
        CommandGroup(
            id="nexus_core_tasks",
            title="Nexus Core Tasks",
            aliases=(
                "nexus core tasks",
                "ndai core tasks",
                "nexus default tasks",
            ),
            member_action_ids=member_ids,
            member_actions=member_actions,
            origin="built_in",
            is_protected=True,
        ),
    )


DEFAULT_COMMAND_GROUPS = _build_default_command_groups()


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


def _coerce_saved_action_invocation_mode(record: dict) -> str:
    return normalize_saved_action_invocation_mode(
        record.get("invocation_mode", ""),
        allow_empty=False,
    )


def _coerce_saved_action_trigger_mode(record: dict, *, target_kind: str) -> str:
    return normalize_saved_action_trigger_mode(
        record.get("trigger_mode", ""),
        target_kind=target_kind,
        allow_empty=True,
    )


def _coerce_saved_action_custom_triggers(record: dict, *, trigger_mode: str) -> tuple[str, ...]:
    return normalize_saved_action_custom_triggers(
        record.get("custom_triggers", ()),
        trigger_mode=trigger_mode,
    )


def _validate_saved_action_target(target_kind: str, target: str) -> str:
    if target_kind == "url":
        if any(char.isspace() for char in target):
            raise ValueError("Saved action URL targets must not contain whitespace.")

        parsed = urlparse(target)
        if parsed.scheme.casefold() not in SUPPORTED_SAVED_ACTION_URL_SCHEMES or not parsed.netloc:
            raise ValueError("Saved action URL target must be an absolute http or https URL.")

        return target

    if target_kind == "app":
        return _validate_saved_action_app_target(target)

    if target_kind == "folder":
        return _validate_saved_action_folder_target(target)

    if target_kind == "file":
        return _validate_saved_action_file_target(target)

    return target


def validate_saved_action_target(target_kind: str, target: str) -> str:
    if not isinstance(target_kind, str):
        raise ValueError("Saved action target kind must be a string.")
    if not isinstance(target, str):
        raise ValueError("Saved action target must be a string.")

    normalized_target = target.strip()
    if not normalized_target:
        raise ValueError("Saved action target must not be empty.")

    return _validate_saved_action_target(target_kind.strip().casefold(), normalized_target)


def _normalize_non_url_target_text(target: str) -> str:
    normalized = target.strip()
    if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {'"', "'"}:
        normalized = normalized[1:-1].strip()
    return normalized


def _validate_windows_path_part(part: str, *, label: str):
    if not part:
        raise ValueError(f"Saved action {label} targets must not contain empty path segments.")
    if part in {".", ".."}:
        raise ValueError(f"Saved action {label} targets must not contain relative path segments.")
    if part[-1] in {" ", "."}:
        raise ValueError(f"Saved action {label} targets must not end path segments with spaces or dots.")
    if any(ord(char) < 32 for char in part):
        raise ValueError(f"Saved action {label} targets must not contain control characters.")
    if any(char in INVALID_WINDOWS_PATH_CHARACTERS for char in part):
        raise ValueError(f"Saved action {label} targets must not contain illegal Windows path characters.")

    reserved_name = part.rstrip(" .").split(".", 1)[0].casefold()
    if reserved_name in RESERVED_WINDOWS_PATH_NAMES:
        raise ValueError(f"Saved action {label} targets must not use reserved Windows path names.")


def _validate_absolute_windows_path_target(
    target: str,
    *,
    label: str,
    require_leaf: bool,
) -> str:
    normalized = _normalize_non_url_target_text(target)
    if not normalized:
        raise ValueError(f"Saved action {label} target must not be empty.")
    if any(char in normalized for char in "\r\n\t"):
        raise ValueError(f"Saved action {label} targets must stay on one line.")

    path = PureWindowsPath(normalized)
    if not path.is_absolute():
        raise ValueError(f"Saved action {label} targets must be absolute Windows paths.")

    anchor = path.anchor
    for part in path.parts:
        if part == anchor:
            continue
        _validate_windows_path_part(part, label=label)

    if require_leaf:
        if normalized.endswith(("\\", "/")) or not path.name:
            raise ValueError(f"Saved action {label} targets must include a final file name.")
    return str(path)


def _validate_saved_action_folder_target(target: str) -> str:
    return _validate_absolute_windows_path_target(target, label="folder", require_leaf=False)


def _validate_saved_action_file_target(target: str) -> str:
    return _validate_absolute_windows_path_target(target, label="file", require_leaf=True)


def _validate_saved_action_app_target(target: str) -> str:
    normalized = _normalize_non_url_target_text(target)
    if not normalized:
        raise ValueError("Saved action application target must not be empty.")
    if any(char in normalized for char in "\r\n\t"):
        raise ValueError("Saved action application targets must stay on one line.")

    looks_like_path = any(separator in normalized for separator in ("\\", "/")) or (
        len(normalized) >= 2 and normalized[1] == ":"
    )
    if looks_like_path:
        normalized_path = _validate_absolute_windows_path_target(
            normalized,
            label="application",
            require_leaf=True,
        )
        if PureWindowsPath(normalized_path).suffix.casefold() not in SUPPORTED_APP_TARGET_EXTENSIONS:
            raise ValueError(
                "Saved action application targets must point to an .exe, .com, .bat, or .cmd file."
            )
        return normalized_path

    if any(char.isspace() for char in normalized):
        raise ValueError(
            "Saved action application targets must be a bare command like notepad.exe or an absolute Windows executable path."
        )
    if not APP_COMMAND_RE.fullmatch(normalized):
        raise ValueError(
            "Saved action application command targets may contain only letters, numbers, dots, hyphens, and underscores."
        )
    return normalized


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
    invocation_mode = _coerce_saved_action_invocation_mode(record)
    aliases = _coerce_saved_action_aliases(record)
    invocation_mode = _coerce_saved_action_invocation_mode(record)
    if invocation_mode == "aliases_only" and not aliases:
        raise ValueError("Saved action aliases must contain at least one callable phrase.")
    trigger_mode = _coerce_saved_action_trigger_mode(record, target_kind=target_kind)
    custom_triggers = _coerce_saved_action_custom_triggers(record, trigger_mode=trigger_mode)

    return CommandAction(
        id=_require_saved_action_string(record, "id"),
        title=_require_saved_action_string(record, "title"),
        target_kind=target_kind,
        target=target,
        aliases=aliases,
        invocation_mode=invocation_mode,
        trigger_mode=trigger_mode,
        custom_triggers=custom_triggers,
        origin="saved",
    )


def coerce_saved_command_action_record(record: object) -> CommandAction:
    return _command_action_from_saved_record(record)


def _build_saved_action_access_guidance() -> str:
    file_action = next(
        (action.title for action in DEFAULT_COMMAND_ACTIONS if action.id == "open_saved_actions_file"),
        "Open Saved Actions File",
    )
    folder_action = next(
        (action.title for action in DEFAULT_COMMAND_ACTIONS if action.id == "open_saved_actions_folder"),
        "Open Saved Actions Folder",
    )
    return f'Use "{file_action}" or "{folder_action}" to inspect the source.'


def _build_saved_group_access_guidance() -> str:
    return _build_saved_action_access_guidance()


def _load_saved_command_actions_from_records(records: Iterable[object]) -> tuple[CommandAction, ...]:
    built_in_ids = {action.id.casefold() for action in DEFAULT_COMMAND_ACTIONS}
    built_in_phrases: set[str] = set()
    for action in DEFAULT_COMMAND_ACTIONS:
        built_in_phrases.update(_normalized_action_phrases(action))

    seen_saved_ids: set[str] = set()
    saved_actions: list[CommandAction] = []
    for record in records:
        action = _command_action_from_saved_record(record)
        normalized_id = action.id.casefold()
        normalized_phrases = _normalized_action_phrases(action)
        if normalized_id in seen_saved_ids:
            raise ValueError("Saved action id collides with another saved action.")

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
                raise ValueError("Saved action title, alias, or trigger phrase collides with an existing action.")
            continue

        seen_saved_ids.add(normalized_id)
        saved_actions.append(action)

    return tuple(saved_actions)


def coerce_saved_command_actions_from_records(records: Iterable[object]) -> tuple[CommandAction, ...]:
    return _load_saved_command_actions_from_records(records)


def _require_saved_group_string(record: dict, field_name: str) -> str:
    value = record.get(field_name)
    if not isinstance(value, str):
        raise ValueError(f"Callable group field '{field_name}' must be a string.")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"Callable group field '{field_name}' must not be empty.")
    return normalized


def _coerce_saved_group_aliases(record: dict) -> tuple[str, ...]:
    aliases = record.get("aliases", ())
    if aliases in (None, "", (), []):
        raise ValueError("Callable groups require at least one exact alias.")

    if not isinstance(aliases, (list, tuple)):
        raise ValueError("Callable group aliases must be a list of strings.")

    normalized_aliases: list[str] = []
    seen_aliases: set[str] = set()
    for alias in aliases:
        if not isinstance(alias, str):
            raise ValueError("Callable group aliases must contain only strings.")

        normalized = re.sub(r"\s+", " ", alias.strip())
        if not normalized:
            raise ValueError("Callable group aliases must not be empty.")

        normalized_key = normalize_command_text(normalized)
        if not normalized_key:
            raise ValueError("Callable group aliases must normalize to non-empty phrases.")
        if normalized_key in seen_aliases:
            raise ValueError("Callable group aliases must stay unique.")

        seen_aliases.add(normalized_key)
        normalized_aliases.append(normalized)

    return tuple(normalized_aliases)


def _coerce_saved_group_member_ids(record: dict) -> tuple[str, ...]:
    member_action_ids = record.get("member_action_ids", ())
    if member_action_ids in (None, "", (), []):
        raise ValueError("Callable groups must contain at least one member.")

    if not isinstance(member_action_ids, (list, tuple)):
        raise ValueError("Callable group member ids must be a list of strings.")

    normalized_member_ids: list[str] = []
    seen_member_ids: set[str] = set()
    for member_id in member_action_ids:
        if not isinstance(member_id, str):
            raise ValueError("Callable group member ids must contain only strings.")

        normalized = member_id.strip()
        if not normalized:
            raise ValueError("Callable group member ids must not be empty.")

        normalized_key = normalized.casefold()
        if normalized_key in seen_member_ids:
            raise ValueError("Callable group members must stay unique.")

        seen_member_ids.add(normalized_key)
        normalized_member_ids.append(normalized)

    return tuple(normalized_member_ids)


def _command_group_from_saved_record(
    record: object,
    *,
    available_actions: Iterable[CommandAction],
) -> CommandGroup:
    if not isinstance(record, dict):
        raise ValueError("Callable group records must be objects.")

    action_by_id = {
        action.id.casefold(): action
        for action in tuple(available_actions)
    }
    member_action_ids = _coerce_saved_group_member_ids(record)
    member_actions: list[CommandAction] = []
    for member_id in member_action_ids:
        action = action_by_id.get(member_id.casefold())
        if action is None:
            raise ValueError("Callable group member ids must resolve to built-in or saved actions.")
        member_actions.append(action)

    return CommandGroup(
        id=_require_saved_group_string(record, "id"),
        title=_require_saved_group_string(record, "title"),
        aliases=_coerce_saved_group_aliases(record),
        member_action_ids=member_action_ids,
        member_actions=tuple(member_actions),
        origin="saved",
        is_protected=bool(record.get("is_protected", False)),
    )


def coerce_saved_command_group_record(
    record: object,
    *,
    available_actions: Iterable[CommandAction],
) -> CommandGroup:
    return _command_group_from_saved_record(record, available_actions=available_actions)


def _load_saved_command_groups_from_records(
    records: Iterable[object],
    *,
    available_actions: Iterable[CommandAction],
) -> tuple[CommandGroup, ...]:
    available_actions = tuple(available_actions)
    action_phrases: set[str] = set()
    for action in available_actions:
        action_phrases.update(_normalized_action_phrases(action))

    seen_group_ids: set[str] = {
        group.id.casefold()
        for group in DEFAULT_COMMAND_GROUPS
    }
    seen_group_aliases: set[str] = set()
    for group in DEFAULT_COMMAND_GROUPS:
        seen_group_aliases.update(_normalized_group_phrases(group))
    groups: list[CommandGroup] = []
    for record in records:
        group = _command_group_from_saved_record(record, available_actions=available_actions)
        normalized_id = group.id.casefold()
        normalized_aliases = _normalized_group_phrases(group)
        if normalized_id in seen_group_ids:
            raise ValueError("Callable group id collides with another group.")
        if normalized_aliases & action_phrases:
            raise ValueError("Callable group aliases must not collide with built-in or saved-task phrases.")
        if normalized_aliases & seen_group_aliases:
            raise ValueError("Callable group aliases must stay unique across groups.")

        seen_group_ids.add(normalized_id)
        seen_group_aliases.update(normalized_aliases)
        groups.append(group)

    return tuple(groups)


def coerce_saved_command_groups_from_records(
    records: Iterable[object],
    *,
    available_actions: Iterable[CommandAction],
) -> tuple[CommandGroup, ...]:
    return _load_saved_command_groups_from_records(records, available_actions=available_actions)


def inspect_saved_action_inventory(
    source_path: str | os.PathLike[str] | None = None,
) -> SavedActionInventoryState:
    guidance_text = _build_saved_action_access_guidance()
    inspection = inspect_saved_action_source(source_path)
    source_path_text = str(inspection.path)

    if inspection.status == "missing":
        return SavedActionInventoryState(
            visible=True,
            status_kind="missing",
            status_text="Saved actions source is missing. Built-in actions remain available.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    if inspection.status == "template_only":
        return SavedActionInventoryState(
            visible=True,
            status_kind="template_only",
            status_text="No saved actions are active yet. The starter source is ready when you want it.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    if inspection.status == "invalid_source":
        return SavedActionInventoryState(
            visible=True,
            status_kind="invalid_source",
            status_text="Saved actions are unavailable because the source file could not be read cleanly.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    try:
        saved_actions = coerce_saved_command_actions_from_records(inspection.actions)
    except ValueError:
        return SavedActionInventoryState(
            visible=True,
            status_kind="invalid_saved_actions",
            status_text="Saved actions are unavailable because one or more source entries are invalid or colliding.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    if not saved_actions:
        return SavedActionInventoryState(
            visible=True,
            status_kind="template_only",
            status_text="No saved actions are active yet. The starter source is ready when you want it.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    count = len(saved_actions)
    noun = "action" if count == 1 else "actions"
    return SavedActionInventoryState(
        visible=True,
        status_kind="loaded",
        status_text=f"{count} saved {noun} loaded from the current source.",
        guidance_text=guidance_text,
        path=source_path_text,
        actions=saved_actions,
    )


def inspect_saved_group_inventory(
    source_path: str | os.PathLike[str] | None = None,
) -> SavedGroupInventoryState:
    guidance_text = _build_saved_group_access_guidance()
    inspection = inspect_saved_action_source(source_path)
    source_path_text = str(inspection.path)

    if inspection.status == "missing":
        return SavedGroupInventoryState(
            visible=True,
            status_kind="missing",
            status_text="Custom groups source is missing. Built-in and saved tasks remain available.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    if inspection.status == "template_only":
        return SavedGroupInventoryState(
            visible=True,
            status_kind="template_only",
            status_text="No custom groups are active yet. The starter source is ready when you want it.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    if inspection.status == "invalid_source":
        return SavedGroupInventoryState(
            visible=True,
            status_kind="invalid_source",
            status_text="Custom groups are unavailable because the source file could not be read cleanly.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    try:
        saved_actions = coerce_saved_command_actions_from_records(inspection.actions)
    except ValueError:
        return SavedGroupInventoryState(
            visible=True,
            status_kind="invalid_saved_actions",
            status_text="Custom groups are unavailable because one or more saved-task entries are invalid or colliding.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    try:
        saved_groups = coerce_saved_command_groups_from_records(
            inspection.groups,
            available_actions=(*DEFAULT_COMMAND_ACTIONS, *saved_actions),
        )
    except ValueError:
        return SavedGroupInventoryState(
            visible=True,
            status_kind="invalid_groups",
            status_text="Custom groups are unavailable because one or more group entries are invalid, empty, or colliding.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    if not saved_groups:
        return SavedGroupInventoryState(
            visible=True,
            status_kind="template_only",
            status_text="No custom groups are active yet. Create a group when you want a callable member set.",
            guidance_text=guidance_text,
            path=source_path_text,
        )

    count = len(saved_groups)
    noun = "group" if count == 1 else "groups"
    return SavedGroupInventoryState(
        visible=True,
        status_kind="loaded",
        status_text=f"{count} custom {noun} loaded from the current source.",
        guidance_text=guidance_text,
        path=source_path_text,
        groups=saved_groups,
    )


def load_saved_command_actions(
    source_path: str | os.PathLike[str] | None = None,
) -> tuple[CommandAction, ...]:
    return inspect_saved_action_inventory(source_path).actions


def load_saved_command_groups(
    source_path: str | os.PathLike[str] | None = None,
) -> tuple[CommandGroup, ...]:
    return inspect_saved_group_inventory(source_path).groups


def build_default_command_action_catalog(
    source_path: str | os.PathLike[str] | None = None,
) -> CommandActionCatalog:
    saved_action_inventory = inspect_saved_action_inventory(source_path)
    saved_group_inventory = inspect_saved_group_inventory(source_path)
    if not saved_action_inventory.actions:
        return CommandActionCatalog(
            DEFAULT_COMMAND_ACTIONS,
            saved_action_inventory=saved_action_inventory,
            groups=(*DEFAULT_COMMAND_GROUPS, *saved_group_inventory.groups),
            saved_group_inventory=saved_group_inventory,
        )

    return CommandActionCatalog(
        (*DEFAULT_COMMAND_ACTIONS, *saved_action_inventory.actions),
        saved_action_inventory=saved_action_inventory,
        groups=(*DEFAULT_COMMAND_GROUPS, *saved_group_inventory.groups),
        saved_group_inventory=saved_group_inventory,
    )


DEFAULT_COMMAND_ACTION_CATALOG = build_default_command_action_catalog()


def reload_default_command_action_catalog() -> CommandActionCatalog:
    global DEFAULT_COMMAND_ACTION_CATALOG
    DEFAULT_COMMAND_ACTION_CATALOG = build_default_command_action_catalog()
    return DEFAULT_COMMAND_ACTION_CATALOG


def resolve_command_actions(text: str, actions=DEFAULT_COMMAND_ACTIONS):
    normalized = normalize_command_text(text)
    if not normalized:
        return []

    matches = []
    for action in actions:
        candidates = build_saved_action_callable_phrases(
            action.title,
            action.aliases,
            invocation_mode=action.invocation_mode,
            trigger_mode=action.trigger_mode,
            custom_triggers=action.custom_triggers,
        )
        if any(normalize_command_text(candidate) == normalized for candidate in candidates):
            matches.append(action)
    return matches


def resolve_command_group(text: str, groups: Iterable[CommandGroup] = ()):
    normalized = normalize_command_text(text)
    if not normalized:
        return None

    for group in tuple(groups):
        if any(normalize_command_text(candidate) == normalized for candidate in build_callable_group_phrases(group.aliases)):
            return group
    return None


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
