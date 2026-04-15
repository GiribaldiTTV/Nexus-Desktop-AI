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
    DEFAULT_COMMAND_ACTIONS,
    SUPPORTED_ACTION_TARGET_KINDS,
    build_default_command_action_catalog,
    coerce_saved_command_action_record,
    coerce_saved_command_actions_from_records,
    default_saved_action_trigger_mode,
    normalize_command_text,
    normalize_saved_action_custom_triggers,
    normalize_saved_action_invocation_mode,
    normalize_saved_action_trigger_mode,
    reload_default_command_action_catalog,
    validate_saved_action_target,
)


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class SavedActionDraft:
    title: str
    target_kind: str
    target: str
    aliases: tuple[str, ...] = ()
    invocation_mode: str = "aliases_only"
    trigger_mode: str = ""
    custom_triggers: tuple[str, ...] = ()


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
class SavedActionAuthoringState:
    path: Path
    existing_records: tuple[dict[str, Any], ...]
    existing_actions: tuple[CommandAction, ...]


class SavedActionAuthoringError(ValueError):
    pass


class SavedActionDraftValidationError(SavedActionAuthoringError):
    pass


class SavedActionUnsafeSourceError(SavedActionAuthoringError):
    pass


def _coerce_draft(draft: SavedActionDraft | dict[str, Any]) -> SavedActionDraft:
    if isinstance(draft, SavedActionDraft):
        return draft
    if isinstance(draft, dict):
        return SavedActionDraft(
            title=draft.get("title", ""),
            target_kind=draft.get("target_kind", ""),
            target=draft.get("target", ""),
            aliases=tuple(draft.get("aliases", ()) or ()),
            invocation_mode=draft.get("invocation_mode", "aliases_only"),
            trigger_mode=draft.get("trigger_mode", ""),
            custom_triggers=tuple(draft.get("custom_triggers", ()) or ()),
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
) -> tuple[str, tuple[str, ...]]:
    try:
        trigger_mode = normalize_saved_action_trigger_mode(
            draft.trigger_mode,
            target_kind=target_kind,
            allow_empty=False,
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


def _normalize_draft_fields(
    draft: SavedActionDraft,
) -> tuple[str, tuple[str, ...], str, str, str, str, tuple[str, ...]]:
    title = _normalize_title(draft.title)
    invocation_mode = _normalize_invocation_mode(draft)
    aliases = _normalize_aliases(draft.aliases, title=title, invocation_mode=invocation_mode)
    target_kind = _normalize_target_kind(draft.target_kind)
    target = _normalize_target(draft.target, target_kind=target_kind)
    trigger_mode, custom_triggers = _normalize_trigger_fields(draft, target_kind=target_kind)
    return title, aliases, target_kind, target, invocation_mode, trigger_mode, custom_triggers


def _load_saved_action_authoring_state(
    source_path: str | Path | None = None,
) -> SavedActionAuthoringState:
    inspection = inspect_saved_action_source(source_path)
    if inspection.status == "invalid_source":
        raise SavedActionUnsafeSourceError(
            "Saved actions are unavailable because the source file could not be read cleanly."
        )

    existing_records: tuple[dict[str, Any], ...]
    if inspection.status == "loaded":
        existing_records = tuple(deepcopy(record) for record in inspection.actions)
    else:
        existing_records = ()

    try:
        existing_actions = coerce_saved_command_actions_from_records(existing_records)
    except ValueError as exc:
        raise SavedActionUnsafeSourceError(
            "Saved actions are unavailable because one or more existing source entries are invalid or colliding."
        ) from exc

    return SavedActionAuthoringState(
        path=inspection.path,
        existing_records=existing_records,
        existing_actions=existing_actions,
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


def _build_saved_action_record_for_create(
    draft: SavedActionDraft,
    state: SavedActionAuthoringState,
) -> dict[str, Any]:
    title, aliases, target_kind, target, invocation_mode, trigger_mode, custom_triggers = _normalize_draft_fields(draft)

    existing_ids = {action.id for action in DEFAULT_COMMAND_ACTIONS}
    existing_ids.update(action.id for action in state.existing_actions)
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
        coerce_saved_command_actions_from_records((*state.existing_records, record))
    except ValueError as exc:
        raise SavedActionDraftValidationError(str(exc)) from exc

    return record


def draft_from_saved_action_record(record: dict[str, Any]) -> SavedActionDraft:
    action = coerce_saved_command_action_record(record)
    return SavedActionDraft(
        title=action.title,
        target_kind=action.target_kind,
        target=action.target,
        aliases=action.aliases,
        invocation_mode=action.invocation_mode,
        trigger_mode=action.trigger_mode,
        custom_triggers=action.custom_triggers,
    )


def load_saved_action_draft_for_edit(
    saved_action_id: str,
    source_path: str | Path | None = None,
) -> SavedActionDraft:
    state = _load_saved_action_authoring_state(source_path)
    _index, record = _find_existing_saved_action_record(state, saved_action_id)
    return draft_from_saved_action_record(record)


def _build_saved_action_record_for_update(
    saved_action_id: str,
    draft: SavedActionDraft,
    state: SavedActionAuthoringState,
) -> tuple[int, dict[str, Any]]:
    index, existing_record = _find_existing_saved_action_record(state, saved_action_id)
    title, aliases, target_kind, target, invocation_mode, trigger_mode, custom_triggers = _normalize_draft_fields(draft)

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
        coerce_saved_command_actions_from_records(updated_records)
    except ValueError as exc:
        raise SavedActionDraftValidationError(str(exc)) from exc

    return index, record


def prepare_saved_action_record_for_create(
    draft: SavedActionDraft | dict[str, Any],
    source_path: str | Path | None = None,
) -> dict[str, Any]:
    draft = _coerce_draft(draft)
    state = _load_saved_action_authoring_state(source_path)
    return _build_saved_action_record_for_create(draft, state)


def create_saved_action_from_draft(
    draft: SavedActionDraft | dict[str, Any],
    source_path: str | Path | None = None,
) -> SavedActionCreateResult:
    draft = _coerce_draft(draft)
    state = _load_saved_action_authoring_state(source_path)
    record = _build_saved_action_record_for_create(draft, state)
    payload = write_saved_action_source((*state.existing_records, record), source_path)

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
    index, record = _build_saved_action_record_for_update(saved_action_id, draft, state)
    updated_records = list(deepcopy(state.existing_records))
    updated_records[index] = record
    payload = write_saved_action_source(updated_records, source_path)

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
    payload = write_saved_action_source(updated_records, source_path)

    if source_path is None:
        catalog = reload_default_command_action_catalog()
    else:
        catalog = build_default_command_action_catalog(source_path)

    return SavedActionDeleteResult(
        path=payload.path,
        record=record,
        catalog=catalog,
    )
