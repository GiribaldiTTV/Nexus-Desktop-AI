import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .saved_action_source import (
    inspect_saved_action_source,
    write_saved_action_source,
)
from .shared_action_model import (
    CommandAction,
    CommandActionCatalog,
    CommandGroup,
    DEFAULT_COMMAND_ACTIONS,
    SUPPORTED_ACTION_TARGET_KINDS,
    build_saved_action_callable_phrases,
    build_default_command_action_catalog,
    coerce_saved_command_action_record,
    coerce_saved_command_actions_from_records,
    coerce_saved_command_group_record,
    coerce_saved_command_groups_from_records,
    normalize_command_text,
    normalize_saved_action_custom_triggers,
    normalize_saved_action_invocation_mode,
    normalize_saved_action_trigger_mode,
    reload_default_command_action_catalog,
    validate_saved_action_target,
)


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_GROUPS_UNCHANGED = object()


@dataclass(frozen=True)
class CallableGroupDraft:
    title: str
    aliases: tuple[str, ...]
    member_action_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class SavedActionDraft:
    title: str
    target_kind: str
    target: str
    aliases: tuple[str, ...] = ()
    invocation_mode: str = "aliases_only"
    trigger_mode: str = ""
    custom_triggers: tuple[str, ...] = ()
    group_ids: tuple[str, ...] = ()
    inline_group: CallableGroupDraft | None = None


@dataclass(frozen=True)
class SavedActionCreateResult:
    path: Path
    record: dict[str, Any]
    catalog: CommandActionCatalog


@dataclass(frozen=True)
class SavedActionUpdateResult:
    path: Path
    record: dict[str, Any]
    catalog: CommandActionCatalog


@dataclass(frozen=True)
class SavedActionDeleteResult:
    path: Path
    record: dict[str, Any]
    catalog: CommandActionCatalog


@dataclass(frozen=True)
class CallableGroupCreateResult:
    path: Path
    record: dict[str, Any]
    catalog: CommandActionCatalog


@dataclass(frozen=True)
class CallableGroupUpdateResult:
    path: Path
    record: dict[str, Any]
    catalog: CommandActionCatalog


@dataclass(frozen=True)
class CallableGroupDeleteResult:
    path: Path
    record: dict[str, Any]
    catalog: CommandActionCatalog


@dataclass(frozen=True)
class SavedActionAuthoringState:
    path: Path
    existing_records: tuple[dict[str, Any], ...]
    existing_actions: tuple[CommandAction, ...]
    existing_group_records: tuple[dict[str, Any], ...] = ()
    existing_groups: tuple[CommandGroup, ...] = ()
    group_status_kind: str = "template_only"
    group_status_text: str = ""


class SavedActionAuthoringError(ValueError):
    pass


class SavedActionDraftValidationError(SavedActionAuthoringError):
    pass


class SavedActionUnsafeSourceError(SavedActionAuthoringError):
    pass


class CallableGroupAuthoringError(ValueError):
    pass


class CallableGroupDraftValidationError(CallableGroupAuthoringError):
    pass


class CallableGroupUnsafeSourceError(CallableGroupAuthoringError):
    pass


def _normalize_group_title(title: Any) -> str:
    if not isinstance(title, str):
        raise CallableGroupDraftValidationError("Callable group name must be a string.")
    normalized = re.sub(r"\s+", " ", title.strip())
    if not normalized:
        raise CallableGroupDraftValidationError("Callable group name must not be empty.")
    return normalized


def _normalize_group_aliases(aliases: Any) -> tuple[str, ...]:
    if aliases in (None, "", (), []):
        raise CallableGroupDraftValidationError("Callable groups require at least one exact alias.")
    if not isinstance(aliases, (list, tuple)):
        raise CallableGroupDraftValidationError("Callable group aliases must be a list of strings.")

    normalized_aliases: list[str] = []
    seen_aliases: set[str] = set()
    for alias in aliases:
        if not isinstance(alias, str):
            raise CallableGroupDraftValidationError("Callable group aliases must contain only strings.")

        normalized_alias = re.sub(r"\s+", " ", alias.strip())
        if not normalized_alias:
            raise CallableGroupDraftValidationError("Callable group aliases must not be empty.")

        normalized_key = normalize_command_text(normalized_alias)
        if not normalized_key:
            raise CallableGroupDraftValidationError("Callable group aliases must normalize to non-empty phrases.")
        if normalized_key in seen_aliases:
            raise CallableGroupDraftValidationError("Callable group aliases must stay unique.")

        seen_aliases.add(normalized_key)
        normalized_aliases.append(normalized_alias)

    return tuple(normalized_aliases)


def _normalize_group_member_ids(
    member_action_ids: Any,
    *,
    allow_empty: bool,
    error_type: type[Exception],
) -> tuple[str, ...]:
    if member_action_ids in (None, "", (), []):
        if allow_empty:
            return ()
        raise error_type("Callable groups must contain at least one member.")
    if not isinstance(member_action_ids, (list, tuple)):
        raise error_type("Callable group members must be a list of action ids.")

    normalized_member_ids: list[str] = []
    seen_member_ids: set[str] = set()
    for member_id in member_action_ids:
        if not isinstance(member_id, str):
            raise error_type("Callable group members must contain only action ids.")

        normalized_member_id = member_id.strip()
        if not normalized_member_id:
            raise error_type("Callable group members must not contain empty ids.")

        normalized_key = normalized_member_id.casefold()
        if normalized_key in seen_member_ids:
            raise error_type("Callable group members must stay unique.")

        seen_member_ids.add(normalized_key)
        normalized_member_ids.append(normalized_member_id)

    return tuple(normalized_member_ids)


def _coerce_callable_group_draft(
    draft: CallableGroupDraft | dict[str, Any],
    *,
    allow_empty_members: bool = False,
) -> CallableGroupDraft:
    if isinstance(draft, CallableGroupDraft):
        raw_title = draft.title
        raw_aliases = draft.aliases
        raw_member_action_ids = draft.member_action_ids
    elif isinstance(draft, dict):
        raw_title = draft.get("title", "")
        raw_aliases = tuple(draft.get("aliases", ()) or ())
        raw_member_action_ids = tuple(draft.get("member_action_ids", ()) or ())
    else:
        raise CallableGroupDraftValidationError(
            "Callable group draft must be an object with title, aliases, and member ids."
        )

    return CallableGroupDraft(
        title=_normalize_group_title(raw_title),
        aliases=_normalize_group_aliases(raw_aliases),
        member_action_ids=_normalize_group_member_ids(
            raw_member_action_ids,
            allow_empty=allow_empty_members,
            error_type=CallableGroupDraftValidationError,
        ),
    )


def _coerce_draft(draft: SavedActionDraft | dict[str, Any]) -> SavedActionDraft:
    if isinstance(draft, SavedActionDraft):
        return draft
    if isinstance(draft, dict):
        inline_group = draft.get("inline_group")
        if isinstance(inline_group, (dict, CallableGroupDraft)):
            inline_group = _coerce_callable_group_draft(inline_group, allow_empty_members=True)
        else:
            inline_group = None
        return SavedActionDraft(
            title=draft.get("title", ""),
            target_kind=draft.get("target_kind", ""),
            target=draft.get("target", ""),
            aliases=tuple(draft.get("aliases", ()) or ()),
            invocation_mode=draft.get("invocation_mode", "aliases_only"),
            trigger_mode=draft.get("trigger_mode", ""),
            custom_triggers=tuple(draft.get("custom_triggers", ()) or ()),
            group_ids=tuple(draft.get("group_ids", ()) or ()),
            inline_group=inline_group,
        )
    raise SavedActionDraftValidationError("Saved action draft must be an object with title, target kind, and target.")


def _normalize_title(title: Any) -> str:
    if not isinstance(title, str):
        raise SavedActionDraftValidationError("Saved action title must be a string.")
    normalized = title.strip()
    if not normalized:
        raise SavedActionDraftValidationError("Saved action title must not be empty.")
    return normalized


def _normalize_aliases(aliases: Any, *, title: str, invocation_mode: str) -> tuple[str, ...]:
    if aliases in (None, ""):
        if invocation_mode == "aliases_only":
            raise SavedActionDraftValidationError("Saved action aliases must contain at least one callable phrase.")
        return ()
    if not isinstance(aliases, (list, tuple)):
        raise SavedActionDraftValidationError("Saved action aliases must be a list of strings.")

    normalized_title = normalize_command_text(title)
    seen_alias_phrases: set[str] = set()
    normalized_aliases: list[str] = []
    for alias in aliases:
        if not isinstance(alias, str):
            raise SavedActionDraftValidationError("Saved action aliases must contain only strings.")

        normalized_alias = alias.strip()
        if not normalized_alias:
            raise SavedActionDraftValidationError("Saved action aliases must not be empty.")

        normalized_phrase = normalize_command_text(normalized_alias)
        if not normalized_phrase:
            raise SavedActionDraftValidationError("Saved action aliases must normalize to non-empty phrases.")
        if invocation_mode != "aliases_only" and normalized_phrase == normalized_title:
            raise SavedActionDraftValidationError("Saved action aliases must not duplicate the title.")
        if normalized_phrase in seen_alias_phrases:
            raise SavedActionDraftValidationError("Saved action aliases must stay unique.")

        seen_alias_phrases.add(normalized_phrase)
        normalized_aliases.append(normalized_alias)

    return tuple(normalized_aliases)


def _normalize_target_kind(target_kind: Any) -> str:
    if not isinstance(target_kind, str):
        raise SavedActionDraftValidationError("Saved action target kind must be a string.")

    normalized = target_kind.strip().casefold()
    if normalized not in SUPPORTED_ACTION_TARGET_KINDS:
        raise SavedActionDraftValidationError("Saved action target kind is unsupported.")
    return normalized


def _normalize_target(target: Any, *, target_kind: str) -> str:
    if not isinstance(target, str):
        raise SavedActionDraftValidationError("Saved action target must be a string.")

    normalized = target.strip()
    if not normalized:
        raise SavedActionDraftValidationError("Saved action target must not be empty.")
    try:
        return validate_saved_action_target(target_kind, normalized)
    except ValueError as exc:
        raise SavedActionDraftValidationError(str(exc)) from exc


def _normalize_trigger_fields(
    draft: SavedActionDraft,
    *,
    target_kind: str,
    invocation_mode: str,
) -> tuple[str, tuple[str, ...]]:
    try:
        trigger_mode = normalize_saved_action_trigger_mode(
            draft.trigger_mode,
            target_kind=target_kind,
            allow_empty=(invocation_mode == "legacy"),
        )
        custom_triggers = normalize_saved_action_custom_triggers(
            draft.custom_triggers,
            trigger_mode=trigger_mode,
        )
    except ValueError as exc:
        raise SavedActionDraftValidationError(str(exc)) from exc
    return trigger_mode, custom_triggers


def _normalize_invocation_mode(draft: SavedActionDraft) -> str:
    try:
        return normalize_saved_action_invocation_mode(
            draft.invocation_mode,
            allow_empty=False,
        )
    except ValueError as exc:
        raise SavedActionDraftValidationError(str(exc)) from exc


def _normalize_group_ids(
    group_ids: Any,
    *,
    error_type: type[Exception],
) -> tuple[str, ...]:
    if group_ids in (None, "", (), []):
        return ()
    if not isinstance(group_ids, (list, tuple)):
        raise error_type("Callable group selection must be a list of group ids.")

    normalized_group_ids: list[str] = []
    seen_group_ids: set[str] = set()
    for group_id in group_ids:
        if not isinstance(group_id, str):
            raise error_type("Callable group selection must contain only group ids.")

        normalized_group_id = group_id.strip()
        if not normalized_group_id:
            raise error_type("Callable group selection must not contain empty ids.")

        normalized_key = normalized_group_id.casefold()
        if normalized_key in seen_group_ids:
            raise error_type("Callable group selection must stay unique.")

        seen_group_ids.add(normalized_key)
        normalized_group_ids.append(normalized_group_id)

    if len(normalized_group_ids) > 1:
        raise error_type("Tasks can be assigned to only one callable group at a time.")

    return tuple(normalized_group_ids)


def _normalize_draft_fields(
    draft: SavedActionDraft,
) -> tuple[str, tuple[str, ...], str, str, str, str, tuple[str, ...], tuple[str, ...], CallableGroupDraft | None]:
    title = _normalize_title(draft.title)
    invocation_mode = _normalize_invocation_mode(draft)
    aliases = _normalize_aliases(draft.aliases, title=title, invocation_mode=invocation_mode)
    target_kind = _normalize_target_kind(draft.target_kind)
    target = _normalize_target(draft.target, target_kind=target_kind)
    trigger_mode, custom_triggers = _normalize_trigger_fields(
        draft,
        target_kind=target_kind,
        invocation_mode=invocation_mode,
    )
    group_ids = _normalize_group_ids(
        draft.group_ids,
        error_type=SavedActionDraftValidationError,
    )
    inline_group = None
    if draft.inline_group is not None:
        try:
            inline_group = _coerce_callable_group_draft(draft.inline_group, allow_empty_members=True)
        except CallableGroupDraftValidationError as exc:
            raise SavedActionDraftValidationError(str(exc)) from exc
    if group_ids and inline_group is not None:
        raise SavedActionDraftValidationError(
            "Tasks can be assigned to one existing group or one newly created group, not both."
        )
    return (
        title,
        aliases,
        target_kind,
        target,
        invocation_mode,
        trigger_mode,
        custom_triggers,
        group_ids,
        inline_group,
    )


def _available_actions_for_state(
    state: SavedActionAuthoringState,
    saved_actions: tuple[CommandAction, ...] | None = None,
) -> tuple[CommandAction, ...]:
    return (*DEFAULT_COMMAND_ACTIONS, *(saved_actions or state.existing_actions))


def _normalized_action_phrases(action: CommandAction) -> set[str]:
    return {
        normalized
        for normalized in (
            normalize_command_text(phrase)
            for phrase in build_saved_action_callable_phrases(
                action.title,
                action.aliases,
                invocation_mode=action.invocation_mode,
                trigger_mode=action.trigger_mode,
                custom_triggers=action.custom_triggers,
            )
        )
        if normalized
    }


def _reject_builtin_phrase_collision_for_authoring(action: CommandAction):
    built_in_phrases: set[str] = set()
    for built_in_action in DEFAULT_COMMAND_ACTIONS:
        built_in_phrases.update(_normalized_action_phrases(built_in_action))

    if _normalized_action_phrases(action) & built_in_phrases:
        raise SavedActionDraftValidationError(
            "Saved action title, alias, or trigger phrase collides with an existing built-in action."
        )


def _load_saved_action_authoring_state(
    source_path: str | Path | None = None,
) -> SavedActionAuthoringState:
    inspection = inspect_saved_action_source(source_path)
    if inspection.status == "invalid_source":
        raise SavedActionUnsafeSourceError(
            "Saved actions are unavailable because the source file could not be read cleanly."
        )

    if inspection.status == "loaded":
        existing_records = tuple(deepcopy(record) for record in inspection.actions)
        existing_group_records = tuple(deepcopy(record) for record in inspection.groups)
    else:
        existing_records = ()
        existing_group_records = ()

    try:
        existing_actions = coerce_saved_command_actions_from_records(existing_records)
    except ValueError as exc:
        raise SavedActionUnsafeSourceError(
            "Saved actions are unavailable because one or more existing source entries are invalid or colliding."
        ) from exc

    existing_groups: tuple[CommandGroup, ...] = ()
    group_status_kind = "template_only"
    group_status_text = "No custom groups are active yet."
    if existing_group_records:
        try:
            existing_groups = coerce_saved_command_groups_from_records(
                existing_group_records,
                available_actions=(*DEFAULT_COMMAND_ACTIONS, *existing_actions),
            )
            group_status_kind = "loaded"
            group_status_text = "Custom groups are available."
        except ValueError:
            existing_groups = ()
            group_status_kind = "invalid_groups"
            group_status_text = (
                "Custom groups are unavailable because one or more existing group entries are invalid, empty, or colliding."
            )

    return SavedActionAuthoringState(
        path=inspection.path,
        existing_records=existing_records,
        existing_actions=existing_actions,
        existing_group_records=existing_group_records,
        existing_groups=existing_groups,
        group_status_kind=group_status_kind,
        group_status_text=group_status_text,
    )


def generate_saved_action_id(title: str, existing_ids: set[str] | tuple[str, ...] | list[str]) -> str:
    normalized_title = normalize_command_text(title)
    candidate_base = _NON_ALNUM_RE.sub("_", normalized_title).strip("_")
    if not candidate_base:
        candidate_base = "saved_action"

    normalized_existing_ids = {existing_id.casefold() for existing_id in existing_ids}
    candidate = candidate_base
    suffix = 2
    while candidate.casefold() in normalized_existing_ids:
        candidate = f"{candidate_base}_{suffix}"
        suffix += 1
    return candidate


def _find_existing_saved_action_record(
    state: SavedActionAuthoringState,
    saved_action_id: str,
    *,
    operation_label: str = "editing",
) -> tuple[int, dict[str, Any]]:
    if not isinstance(saved_action_id, str) or not saved_action_id.strip():
        raise SavedActionDraftValidationError(f"Saved action id must be provided for {operation_label}.")

    normalized_id = saved_action_id.strip().casefold()
    for index, record in enumerate(state.existing_records):
        record_id = record.get("id")
        if isinstance(record_id, str) and record_id.strip().casefold() == normalized_id:
            return index, deepcopy(record)

    raise SavedActionDraftValidationError(f"Saved action could not be found for {operation_label}.")


def _find_existing_callable_group_record(
    state: SavedActionAuthoringState,
    group_id: str,
    *,
    operation_label: str = "editing",
) -> tuple[int, dict[str, Any]]:
    if not isinstance(group_id, str) or not group_id.strip():
        raise CallableGroupDraftValidationError(f"Callable group id must be provided for {operation_label}.")

    normalized_id = group_id.strip().casefold()
    for index, record in enumerate(state.existing_group_records):
        record_id = record.get("id")
        if isinstance(record_id, str) and record_id.strip().casefold() == normalized_id:
            return index, deepcopy(record)

    raise CallableGroupDraftValidationError(f"Callable group could not be found for {operation_label}.")


def _persist_records_with_optional_groups(
    records: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    source_path: str | Path | None = None,
    group_records: object = _GROUPS_UNCHANGED,
):
    write_kwargs = {}
    if group_records is not _GROUPS_UNCHANGED:
        write_kwargs["groups"] = group_records
    return write_saved_action_source(records, source_path, **write_kwargs)


def _require_group_authoring_ready(state: SavedActionAuthoringState):
    if state.group_status_kind == "invalid_groups":
        raise CallableGroupUnsafeSourceError(state.group_status_text)


def _build_saved_action_record_for_create(
    draft: SavedActionDraft,
    state: SavedActionAuthoringState,
) -> dict[str, Any]:
    (
        title,
        aliases,
        target_kind,
        target,
        invocation_mode,
        trigger_mode,
        custom_triggers,
        _group_ids,
        _inline_group,
    ) = _normalize_draft_fields(draft)

    existing_ids = {action.id for action in DEFAULT_COMMAND_ACTIONS}
    existing_ids.update(action.id for action in state.existing_actions)
    existing_ids.update(group.id for group in state.existing_groups)
    record_id = generate_saved_action_id(title, existing_ids)

    record = {
        "id": record_id,
        "title": title,
        "target_kind": target_kind,
        "target": target,
        "aliases": list(aliases),
        "invocation_mode": invocation_mode,
        "trigger_mode": trigger_mode,
    }
    if custom_triggers:
        record["custom_triggers"] = list(custom_triggers)

    try:
        _reject_builtin_phrase_collision_for_authoring(coerce_saved_command_action_record(record))
        coerce_saved_command_actions_from_records((*state.existing_records, record))
    except ValueError as exc:
        raise SavedActionDraftValidationError(str(exc)) from exc

    return record


def _build_callable_group_record_for_create(
    draft: CallableGroupDraft,
    state: SavedActionAuthoringState,
    *,
    available_actions: tuple[CommandAction, ...],
) -> dict[str, Any]:
    draft = _coerce_callable_group_draft(draft)
    existing_ids = {action.id for action in DEFAULT_COMMAND_ACTIONS}
    existing_ids.update(action.id for action in state.existing_actions)
    existing_ids.update(group.id for group in state.existing_groups)
    record_id = generate_saved_action_id(draft.title, existing_ids)
    record = {
        "id": record_id,
        "title": draft.title,
        "aliases": list(draft.aliases),
        "member_action_ids": list(draft.member_action_ids),
    }
    try:
        coerce_saved_command_groups_from_records(
            (*state.existing_group_records, record),
            available_actions=available_actions,
        )
    except ValueError as exc:
        raise CallableGroupDraftValidationError(str(exc)) from exc
    return record


def draft_from_saved_action_record(
    record: dict[str, Any],
    *,
    group_ids: tuple[str, ...] = (),
) -> SavedActionDraft:
    action = coerce_saved_command_action_record(record)
    return SavedActionDraft(
        title=action.title,
        target_kind=action.target_kind,
        target=action.target,
        aliases=action.aliases,
        invocation_mode=action.invocation_mode,
        trigger_mode=action.trigger_mode,
        custom_triggers=action.custom_triggers,
        group_ids=group_ids,
    )


def draft_from_callable_group_record(
    record: dict[str, Any],
    *,
    available_actions: tuple[CommandAction, ...],
) -> CallableGroupDraft:
    group = coerce_saved_command_group_record(record, available_actions=available_actions)
    return CallableGroupDraft(
        title=group.title,
        aliases=group.aliases,
        member_action_ids=group.member_action_ids,
    )


def _build_task_membership_group_records(
    state: SavedActionAuthoringState,
    *,
    task_action: CommandAction,
    selected_group_ids: tuple[str, ...],
    inline_group: CallableGroupDraft | None,
) -> tuple[dict[str, Any], ...] | object:
    if not selected_group_ids and inline_group is None:
        return _GROUPS_UNCHANGED
    if state.group_status_kind == "invalid_groups":
        raise SavedActionDraftValidationError(state.group_status_text)

    normalized_selected = {group_id.casefold() for group_id in selected_group_ids}
    updated_group_records = [deepcopy(record) for record in state.existing_group_records]
    existing_group_ids = {
        str(record.get("id") or "").strip().casefold()
        for record in updated_group_records
    }
    if any(group_id not in existing_group_ids for group_id in normalized_selected):
        raise SavedActionDraftValidationError("One or more selected custom groups could not be found.")

    normalized_task_id = task_action.id.casefold()
    for record in updated_group_records:
        record_id = str(record.get("id") or "").strip()
        members = [
            str(member_id).strip()
            for member_id in tuple(record.get("member_action_ids", ()) or ())
            if str(member_id).strip()
        ]
        filtered_members = [
            member_id
            for member_id in members
            if member_id.casefold() != normalized_task_id
        ]
        if record_id.casefold() in normalized_selected:
            filtered_members.append(task_action.id)
        if not filtered_members:
            title = str(record.get("title") or record_id or "this group")
            raise SavedActionDraftValidationError(
                f'Removing this task would leave callable group "{title}" empty. Edit or delete the group directly instead.'
            )
        record["member_action_ids"] = filtered_members

    if inline_group is not None:
        inline_group = _coerce_callable_group_draft(inline_group, allow_empty_members=True)
        inline_record = {
            "id": generate_saved_action_id(
                inline_group.title,
                {
                    *(action.id for action in DEFAULT_COMMAND_ACTIONS),
                    *(action.id for action in state.existing_actions),
                    *(group.id for group in state.existing_groups),
                },
            ),
            "title": inline_group.title,
            "aliases": list(inline_group.aliases),
            "member_action_ids": [task_action.id],
        }
        updated_group_records.append(inline_record)

    try:
        available_actions = tuple(
            existing_action
            for existing_action in state.existing_actions
            if existing_action.id.casefold() != normalized_task_id
        )
        coerce_saved_command_groups_from_records(
            updated_group_records,
            available_actions=(*DEFAULT_COMMAND_ACTIONS, *available_actions, task_action),
        )
    except ValueError as exc:
        raise SavedActionDraftValidationError(str(exc)) from exc

    return tuple(updated_group_records)


def _build_group_records_after_task_delete(
    state: SavedActionAuthoringState,
    *,
    deleted_action_id: str,
) -> tuple[dict[str, Any], ...] | object:
    if state.group_status_kind != "loaded":
        return _GROUPS_UNCHANGED

    normalized_deleted_id = deleted_action_id.casefold()
    updated_group_records: list[dict[str, Any]] = []
    for record in state.existing_group_records:
        copied = deepcopy(record)
        members = [
            str(member_id).strip()
            for member_id in tuple(copied.get("member_action_ids", ()) or ())
            if str(member_id).strip() and str(member_id).strip().casefold() != normalized_deleted_id
        ]
        if not members:
            continue
        copied["member_action_ids"] = members
        updated_group_records.append(copied)

    return tuple(updated_group_records)


def prepare_saved_action_record_for_create(
    draft: SavedActionDraft | dict[str, Any],
    source_path: str | Path | None = None,
) -> dict[str, Any]:
    draft = _coerce_draft(draft)
    state = _load_saved_action_authoring_state(source_path)
    return _build_saved_action_record_for_create(draft, state)


def load_saved_action_draft_for_edit(
    saved_action_id: str,
    source_path: str | Path | None = None,
) -> SavedActionDraft:
    state = _load_saved_action_authoring_state(source_path)
    _index, record = _find_existing_saved_action_record(state, saved_action_id)
    group_ids = ()
    if state.group_status_kind == "loaded":
        normalized_action_id = saved_action_id.strip().casefold()
        matched_group_ids = tuple(
            group.id
            for group in state.existing_groups
            if any(member_id.casefold() == normalized_action_id for member_id in group.member_action_ids)
        )
        group_ids = tuple(matched_group_ids[:1])
    return draft_from_saved_action_record(record, group_ids=group_ids)


def create_saved_action_from_draft(
    draft: SavedActionDraft | dict[str, Any],
    source_path: str | Path | None = None,
) -> SavedActionCreateResult:
    draft = _coerce_draft(draft)
    state = _load_saved_action_authoring_state(source_path)
    record = _build_saved_action_record_for_create(draft, state)
    task_action = coerce_saved_command_action_record(record)
    (
        _title,
        _aliases,
        _target_kind,
        _target,
        _invocation_mode,
        _trigger_mode,
        _custom_triggers,
        group_ids,
        inline_group,
    ) = _normalize_draft_fields(draft)
    group_records = _build_task_membership_group_records(
        state,
        task_action=task_action,
        selected_group_ids=group_ids,
        inline_group=inline_group,
    )
    payload = _persist_records_with_optional_groups(
        (*state.existing_records, record),
        source_path=source_path,
        group_records=group_records,
    )

    if source_path is None:
        catalog = reload_default_command_action_catalog()
    else:
        catalog = build_default_command_action_catalog(source_path)

    return SavedActionCreateResult(
        path=payload.path,
        record=record,
        catalog=catalog,
    )


def update_saved_action_from_draft(
    saved_action_id: str,
    draft: SavedActionDraft | dict[str, Any],
    source_path: str | Path | None = None,
) -> SavedActionUpdateResult:
    draft = _coerce_draft(draft)
    state = _load_saved_action_authoring_state(source_path)
    index, existing_record = _find_existing_saved_action_record(state, saved_action_id)
    (
        title,
        aliases,
        target_kind,
        target,
        invocation_mode,
        trigger_mode,
        custom_triggers,
        group_ids,
        inline_group,
    ) = _normalize_draft_fields(draft)

    record = deepcopy(existing_record)
    record["title"] = title
    record["target_kind"] = target_kind
    record["target"] = target
    record["aliases"] = list(aliases)
    record["invocation_mode"] = invocation_mode
    record["trigger_mode"] = trigger_mode
    if custom_triggers:
        record["custom_triggers"] = list(custom_triggers)
    else:
        record.pop("custom_triggers", None)

    updated_records = list(deepcopy(state.existing_records))
    updated_records[index] = record
    try:
        _reject_builtin_phrase_collision_for_authoring(coerce_saved_command_action_record(record))
        updated_actions = coerce_saved_command_actions_from_records(updated_records)
    except ValueError as exc:
        raise SavedActionDraftValidationError(str(exc)) from exc

    updated_action = next(
        action for action in updated_actions
        if action.id.casefold() == saved_action_id.strip().casefold()
    )
    group_records = _build_task_membership_group_records(
        state,
        task_action=updated_action,
        selected_group_ids=group_ids,
        inline_group=inline_group,
    )
    payload = _persist_records_with_optional_groups(
        updated_records,
        source_path=source_path,
        group_records=group_records,
    )

    if source_path is None:
        catalog = reload_default_command_action_catalog()
    else:
        catalog = build_default_command_action_catalog(source_path)

    return SavedActionUpdateResult(
        path=payload.path,
        record=record,
        catalog=catalog,
    )


def delete_saved_action(
    saved_action_id: str,
    source_path: str | Path | None = None,
) -> SavedActionDeleteResult:
    state = _load_saved_action_authoring_state(source_path)
    index, record = _find_existing_saved_action_record(
        state,
        saved_action_id,
        operation_label="deleting",
    )
    updated_records = list(deepcopy(state.existing_records))
    updated_records.pop(index)
    group_records = _build_group_records_after_task_delete(
        state,
        deleted_action_id=saved_action_id.strip(),
    )
    payload = _persist_records_with_optional_groups(
        updated_records,
        source_path=source_path,
        group_records=group_records,
    )

    if source_path is None:
        catalog = reload_default_command_action_catalog()
    else:
        catalog = build_default_command_action_catalog(source_path)

    return SavedActionDeleteResult(
        path=payload.path,
        record=record,
        catalog=catalog,
    )


def prepare_callable_group_record_for_create(
    draft: CallableGroupDraft | dict[str, Any],
    source_path: str | Path | None = None,
) -> dict[str, Any]:
    draft = _coerce_callable_group_draft(draft)
    state = _load_saved_action_authoring_state(source_path)
    _require_group_authoring_ready(state)
    return _build_callable_group_record_for_create(
        draft,
        state,
        available_actions=_available_actions_for_state(state),
    )


def load_callable_group_draft_for_edit(
    group_id: str,
    source_path: str | Path | None = None,
) -> CallableGroupDraft:
    state = _load_saved_action_authoring_state(source_path)
    _require_group_authoring_ready(state)
    _index, record = _find_existing_callable_group_record(state, group_id)
    return draft_from_callable_group_record(
        record,
        available_actions=_available_actions_for_state(state),
    )


def create_callable_group_from_draft(
    draft: CallableGroupDraft | dict[str, Any],
    source_path: str | Path | None = None,
) -> CallableGroupCreateResult:
    draft = _coerce_callable_group_draft(draft)
    state = _load_saved_action_authoring_state(source_path)
    _require_group_authoring_ready(state)
    record = _build_callable_group_record_for_create(
        draft,
        state,
        available_actions=_available_actions_for_state(state),
    )
    payload = _persist_records_with_optional_groups(
        state.existing_records,
        source_path=source_path,
        group_records=(*state.existing_group_records, record),
    )

    if source_path is None:
        catalog = reload_default_command_action_catalog()
    else:
        catalog = build_default_command_action_catalog(source_path)

    return CallableGroupCreateResult(
        path=payload.path,
        record=record,
        catalog=catalog,
    )


def update_callable_group_from_draft(
    group_id: str,
    draft: CallableGroupDraft | dict[str, Any],
    source_path: str | Path | None = None,
) -> CallableGroupUpdateResult:
    draft = _coerce_callable_group_draft(draft)
    state = _load_saved_action_authoring_state(source_path)
    _require_group_authoring_ready(state)
    index, existing_record = _find_existing_callable_group_record(state, group_id)

    record = deepcopy(existing_record)
    record["title"] = draft.title
    record["aliases"] = list(draft.aliases)
    record["member_action_ids"] = list(draft.member_action_ids)

    updated_group_records = list(deepcopy(state.existing_group_records))
    updated_group_records[index] = record
    try:
        coerce_saved_command_groups_from_records(
            updated_group_records,
            available_actions=_available_actions_for_state(state),
        )
    except ValueError as exc:
        raise CallableGroupDraftValidationError(str(exc)) from exc

    payload = _persist_records_with_optional_groups(
        state.existing_records,
        source_path=source_path,
        group_records=updated_group_records,
    )

    if source_path is None:
        catalog = reload_default_command_action_catalog()
    else:
        catalog = build_default_command_action_catalog(source_path)

    return CallableGroupUpdateResult(
        path=payload.path,
        record=record,
        catalog=catalog,
    )


def delete_callable_group(
    group_id: str,
    source_path: str | Path | None = None,
) -> CallableGroupDeleteResult:
    state = _load_saved_action_authoring_state(source_path)
    _require_group_authoring_ready(state)
    index, record = _find_existing_callable_group_record(
        state,
        group_id,
        operation_label="deleting",
    )
    updated_group_records = list(deepcopy(state.existing_group_records))
    updated_group_records.pop(index)
    payload = _persist_records_with_optional_groups(
        state.existing_records,
        source_path=source_path,
        group_records=updated_group_records,
    )

    if source_path is None:
        catalog = reload_default_command_action_catalog()
    else:
        catalog = build_default_command_action_catalog(source_path)

    return CallableGroupDeleteResult(
        path=payload.path,
        record=record,
        catalog=catalog,
    )
