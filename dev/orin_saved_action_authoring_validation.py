import json
import os
import sys
import tempfile
from pathlib import Path


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import desktop.saved_action_source as saved_action_source_mod
from desktop.saved_action_authoring import (
    SavedActionDraft,
    SavedActionDraftValidationError,
    SavedActionUnsafeSourceError,
    create_saved_action_from_draft,
    load_saved_action_draft_for_edit,
    prepare_saved_action_record_for_create,
    update_saved_action_from_draft,
)
from desktop.saved_action_source import DEFAULT_SAVED_ACTION_TEMPLATE
from desktop.shared_action_model import build_default_command_action_catalog


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _test_create_persists_saved_action_and_preserves_template_fields():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        result = create_saved_action_from_draft(
            SavedActionDraft(
                title="Open Reports",
                target_kind="folder",
                target=r"C:\Reports",
                aliases=("show reports", "view reports"),
            ),
            source_path,
        )

        payload = json.loads(source_path.read_text(encoding="utf-8"))
        actions = payload.get("actions") or []

        _assert(source_path.is_file(), "successful authoring should persist the saved-action source file")
        _assert(payload.get("schema_version") == 1, "successful authoring should preserve schema version 1")
        _assert(
            payload.get("examples") == DEFAULT_SAVED_ACTION_TEMPLATE["examples"],
            "successful authoring should preserve starter examples in the saved-action source",
        )
        _assert(len(actions) == 1, "successful authoring should write one saved action")
        _assert(actions[0]["id"] == "open_reports", "successful authoring should generate a stable id from the title")
        _assert(
            len(result.catalog.saved_action_inventory.actions) == 1,
            "successful authoring should return a reloaded catalog that includes the new saved action",
        )
        _assert(
            result.catalog.actions[-1].id == "open_reports",
            "successful authoring should append the new saved action to the effective shared catalog",
        )


def _test_id_generation_avoids_existing_saved_ids():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_reports",
                        "title": "Show Reports Hub",
                        "target_kind": "folder",
                        "target": r"C:\Reports\Hub",
                        "aliases": ["show reports hub"],
                    }
                ],
            },
        )

        record = prepare_saved_action_record_for_create(
            SavedActionDraft(
                title="Open Reports",
                target_kind="folder",
                target=r"C:\Reports",
                aliases=("view reports",),
            ),
            source_path,
        )

        _assert(
            record["id"] == "open_reports_2",
            "id generation should avoid collisions with existing saved-action ids",
        )


def _test_create_supports_all_persisted_target_kinds():
    with tempfile.TemporaryDirectory() as temp_dir:
        cases = [
            ("Open Notepad", "app", "notepad.exe"),
            ("Open Reports Folder", "folder", r"C:\Reports"),
            ("Open Reports File", "file", r"C:\Reports\weekly.txt"),
            ("Open Docs Site", "url", "https://example.com/docs"),
        ]

        for index, (title, target_kind, target) in enumerate(cases, start=1):
            source_path = Path(temp_dir) / f"saved_actions_{index}.json"
            result = create_saved_action_from_draft(
                SavedActionDraft(
                    title=title,
                    target_kind=target_kind,
                    target=target,
                    aliases=(f"alias {index}",),
                ),
                source_path,
            )

            payload = json.loads(source_path.read_text(encoding="utf-8"))
            action = (payload.get("actions") or [])[0]
            _assert(
                action["target_kind"] == target_kind,
                "authoring foundation should preserve supported persisted target kinds on write",
            )
            _assert(
                action["target"] == target,
                "authoring foundation should preserve the provided target on write",
            )
            _assert(
                result.catalog.actions[-1].target_kind == target_kind,
                "authoring foundation should reload the saved action into the catalog with the same target kind",
            )


def _test_new_saved_actions_persist_default_trigger_modes():
    with tempfile.TemporaryDirectory() as temp_dir:
        cases = [
            ("app", "notepad.exe", "launch"),
            ("folder", r"C:\Reports", "open"),
            ("file", r"C:\Reports\weekly.txt", "open"),
            ("url", "https://example.com/docs", "open"),
        ]

        for index, (target_kind, target, expected_trigger_mode) in enumerate(cases, start=1):
            source_path = Path(temp_dir) / f"saved_actions_trigger_{index}.json"
            result = create_saved_action_from_draft(
                SavedActionDraft(
                    title=f"Nexus {index}",
                    target_kind=target_kind,
                    target=target,
                    aliases=(f"ndai {index}",),
                ),
                source_path,
            )

            action = (json.loads(source_path.read_text(encoding="utf-8")).get("actions") or [])[0]
            _assert(
                action["trigger_mode"] == expected_trigger_mode,
                "new saved actions should persist the default trigger mode for their target kind",
            )
            _assert(
                action["invocation_mode"] == "aliases_only",
                "new saved actions should persist aliases_only invocation mode by default",
            )
            _assert(
                result.catalog.actions[-1].trigger_mode == expected_trigger_mode,
                "reloaded saved actions should surface the persisted default trigger mode",
            )
            _assert(
                result.catalog.actions[-1].invocation_mode == "aliases_only",
                "reloaded saved actions should surface the aliases_only invocation mode",
            )


def _test_generated_trigger_phrases_resolve_for_saved_actions():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        result = create_saved_action_from_draft(
            SavedActionDraft(
                title="Open Nexus",
                target_kind="app",
                target="notepad.exe",
                aliases=("Nexus", "NDAI"),
                trigger_mode="launch_and_open",
            ),
            source_path,
        )

        catalog = result.catalog
        expected_id = result.record["id"]
        for phrase in ("Nexus", "NDAI", "Open Nexus", "Launch Nexus", "Open NDAI", "Launch NDAI"):
            matches = catalog.resolve_actions(phrase)
            _assert(
                tuple(action.id for action in matches) == (expected_id,),
                f"generated callable phrase '{phrase}' should resolve to the saved action exactly once",
            )
        _assert(
            tuple(action.id for action in catalog.resolve_actions("Open Open Nexus")) == (),
            "new alias-root tasks should not generate trigger phrases from the title label alone",
        )


def _test_custom_trigger_phrases_persist_and_resolve():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        result = create_saved_action_from_draft(
            SavedActionDraft(
                title="Open Nexus",
                target_kind="url",
                target="https://example.com/docs",
                aliases=("Nexus", "NDAI"),
                trigger_mode="custom",
                custom_triggers=("Force Open", "Duck Duck Goose"),
            ),
            source_path,
        )

        action = (json.loads(source_path.read_text(encoding="utf-8")).get("actions") or [])[0]
        _assert(
            action["custom_triggers"] == ["Force Open", "Duck Duck Goose"],
            "custom trigger phrases should persist separately from aliases",
        )
        _assert(
            action["aliases"] == ["Nexus", "NDAI"],
            "generated trigger phrases should not be persisted into aliases",
        )

        expected_id = result.record["id"]
        for phrase in ("Force Open Nexus", "Force Open NDAI", "Duck Duck Goose Nexus", "Duck Duck Goose NDAI"):
            matches = result.catalog.resolve_actions(phrase)
            _assert(
                tuple(action.id for action in matches) == (expected_id,),
                f"custom trigger phrase '{phrase}' should resolve to the saved action exactly once",
            )
        _assert(
            tuple(action.id for action in result.catalog.resolve_actions("Force Open Open Nexus")) == (),
            "custom trigger phrases should be generated from aliases only for new-model tasks",
        )


def _test_custom_trigger_validation_is_bounded():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"

        try:
            create_saved_action_from_draft(
                SavedActionDraft(
                    title="Nexus",
                    target_kind="app",
                    target="notepad.exe",
                    aliases=("NDAI",),
                    trigger_mode="custom",
                    custom_triggers=("Force Open", "force open"),
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("custom trigger phrases should stay unique after normalization")

        _assert(
            not source_path.exists(),
            "invalid custom trigger phrases should fail closed before write",
        )


def _test_new_alias_root_tasks_require_at_least_one_alias():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"

        try:
            create_saved_action_from_draft(
                SavedActionDraft(
                    title="Open Nexus",
                    target_kind="app",
                    target="notepad.exe",
                    aliases=(),
                ),
                source_path,
            )
        except SavedActionDraftValidationError as exc:
            _assert(
                "at least one callable phrase" in str(exc).casefold(),
                "new alias-root tasks should explain that aliases are required",
            )
        else:
            raise AssertionError("new alias-root tasks should require at least one alias before write")

        _assert(
            not source_path.exists(),
            "missing aliases for a new alias-root task should fail closed before write",
        )


def _test_invalid_inputs_are_rejected_before_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"

        try:
            create_saved_action_from_draft(
                SavedActionDraft(
                    title="Open Docs URL",
                    target_kind="url",
                    target="example.com/docs",
                    aliases=("view docs url",),
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("invalid url targets should be rejected before write")

        _assert(
            not source_path.exists(),
            "rejecting invalid input should not create or modify the saved-action source file",
        )


def _test_invalid_non_url_targets_are_rejected_before_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        cases = [
            ("app", "notepad.exe --help"),
            ("folder", r"Reports\Daily"),
            ("file", r"C:\Reports\weekly?.txt"),
        ]

        for index, (target_kind, target) in enumerate(cases, start=1):
            source_path = Path(temp_dir) / f"saved_actions_{index}.json"
            try:
                create_saved_action_from_draft(
                    SavedActionDraft(
                        title=f"Task {index}",
                        target_kind=target_kind,
                        target=target,
                        aliases=(f"alias {index}",),
                    ),
                    source_path,
                )
            except SavedActionDraftValidationError:
                pass
            else:
                raise AssertionError(f"invalid {target_kind} targets should be rejected before write")

            _assert(
                not source_path.exists(),
                f"rejecting invalid {target_kind} targets should not create or modify the saved-action source file",
            )


def _test_builtin_collisions_are_rejected_before_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"

        try:
            create_saved_action_from_draft(
                SavedActionDraft(
                    title="Explorer Helper",
                    target_kind="app",
                    target="explorer.exe",
                    aliases=("Open Windows Explorer",),
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("built-in collisions should be rejected before write")

        _assert(
            not source_path.exists(),
            "rejecting a built-in collision should not create or modify the saved-action source file",
        )


def _test_generated_trigger_phrase_collides_with_built_in_before_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"

        try:
            create_saved_action_from_draft(
                SavedActionDraft(
                    title="Workspace Helper",
                    target_kind="folder",
                    target=r"C:\Workspace",
                    aliases=("Workspace",),
                    trigger_mode="open",
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("generated trigger phrases that collide with built-ins should be rejected before write")

        _assert(
            not source_path.exists(),
            "built-in trigger-phrase collisions should fail closed before write",
        )


def _test_existing_saved_action_phrase_collisions_are_rejected_before_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "show_reports_hub",
                        "title": "Show Reports Hub",
                        "target_kind": "folder",
                        "target": r"C:\Reports\Hub",
                        "aliases": ["open reports hub"],
                    }
                ],
            },
        )
        original_text = source_path.read_text(encoding="utf-8")

        try:
            create_saved_action_from_draft(
                SavedActionDraft(
                    title="Reports Viewer",
                    target_kind="folder",
                    target=r"C:\Reports",
                    aliases=("Open Reports Hub",),
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("existing saved-action phrase collisions should be rejected before write")

        _assert(
            source_path.read_text(encoding="utf-8") == original_text,
            "rejecting an existing saved-action collision should leave the source untouched",
        )


def _test_generated_trigger_phrase_collides_with_existing_saved_action_before_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "workspace_hub",
                        "title": "Workspace Hub",
                        "target_kind": "folder",
                        "target": r"C:\Workspace",
                        "aliases": [],
                        "invocation_mode": "legacy",
                        "trigger_mode": "open",
                    }
                ],
            },
        )
        original_text = source_path.read_text(encoding="utf-8")

        try:
            create_saved_action_from_draft(
                SavedActionDraft(
                    title="Workspace Secondary Label",
                    target_kind="folder",
                    target=r"C:\Workspace\Secondary",
                    aliases=("Workspace Hub",),
                    trigger_mode="launch",
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("generated trigger phrases should collide with existing saved-action callable phrases")

        _assert(
            source_path.read_text(encoding="utf-8") == original_text,
            "generated saved-action trigger collisions should leave the source untouched",
        )


def _test_existing_saved_actions_without_trigger_fields_remain_bare_only():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "knowledge_base",
                        "title": "Knowledge Base",
                        "target_kind": "url",
                        "target": "https://example.com/docs",
                        "aliases": ["KB Docs"],
                    }
                ],
            },
        )

        catalog = build_default_command_action_catalog(source_path)
        _assert(
            tuple(action.id for action in catalog.resolve_actions("Knowledge Base")) == ("knowledge_base",),
            "legacy saved actions without trigger fields should still resolve by bare title",
        )
        _assert(
            tuple(action.id for action in catalog.resolve_actions("KB Docs")) == ("knowledge_base",),
            "legacy saved actions without trigger fields should still resolve by bare alias",
        )
        _assert(
            tuple(action.id for action in catalog.resolve_actions("Open Knowledge Base")) == (),
            "legacy saved actions without trigger fields should stay bare-only until they are rewritten through the new model",
        )


def _test_legacy_saved_actions_keep_title_callability_when_edited():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "knowledge_base",
                        "title": "Knowledge Base",
                        "target_kind": "url",
                        "target": "https://example.com/docs",
                        "aliases": ["KB Docs"],
                    }
                ],
            },
        )

        update_saved_action_from_draft(
            "knowledge_base",
            SavedActionDraft(
                title="Knowledge Base",
                target_kind="url",
                target="https://example.com/docs/v2",
                aliases=("KB Docs", "KB"),
                invocation_mode="legacy",
                trigger_mode="open",
            ),
            source_path,
        )

        payload = json.loads(source_path.read_text(encoding="utf-8"))
        record = (payload.get("actions") or [])[0]
        _assert(
            record["invocation_mode"] == "legacy",
            "editing an existing legacy task should preserve its legacy invocation mode",
        )

        catalog = build_default_command_action_catalog(source_path)
        _assert(
            tuple(action.id for action in catalog.resolve_actions("Knowledge Base")) == ("knowledge_base",),
            "legacy tasks should keep title callability after edit when their invocation mode stays legacy",
        )
        _assert(
            tuple(action.id for action in catalog.resolve_actions("Open Knowledge Base")) == ("knowledge_base",),
            "legacy tasks should preserve trigger-plus-title behavior after edit when they remain legacy",
        )


def _test_invalid_existing_saved_actions_block_write_completely():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        original_text = json.dumps(
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_reports",
                        "title": "Open Reports",
                        "target_kind": "folder",
                        "target": r"C:\Reports",
                        "aliases": ["show reports"],
                    },
                    {
                        "id": "open_reports_archive",
                        "title": "Open Reports Archive",
                        "target_kind": "folder",
                        "target": r"C:\Reports\Archive",
                        "aliases": ["show reports"],
                    },
                ],
            },
            indent=2,
        ) + "\n"
        source_path.write_text(original_text, encoding="utf-8")

        try:
            create_saved_action_from_draft(
                SavedActionDraft(
                    title="Open Tools",
                    target_kind="folder",
                    target=r"C:\Tools",
                    aliases=("view tools",),
                ),
                source_path,
            )
        except SavedActionUnsafeSourceError:
            pass
        else:
            raise AssertionError("invalid existing saved-action states should block writes completely")

        _assert(
            source_path.read_text(encoding="utf-8") == original_text,
            "blocking an unsafe source should leave the original saved-action source untouched",
        )


def _test_atomic_write_failure_preserves_existing_source():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        original_payload = {
            "schema_version": 1,
            "actions": [
                {
                    "id": "show_reports_hub",
                    "title": "Show Reports Hub",
                    "target_kind": "folder",
                    "target": r"C:\Reports\Hub",
                    "aliases": ["show reports hub"],
                }
            ],
        }
        _write_json(source_path, original_payload)
        original_text = source_path.read_text(encoding="utf-8")

        original_replace = saved_action_source_mod.os.replace
        saved_action_source_mod.os.replace = lambda *_args, **_kwargs: (_ for _ in ()).throw(
            OSError("replace failed")
        )
        try:
            try:
                create_saved_action_from_draft(
                    SavedActionDraft(
                        title="Open Reports",
                        target_kind="folder",
                        target=r"C:\Reports",
                        aliases=("view reports",),
                    ),
                    source_path,
                )
            except saved_action_source_mod.SavedActionSourceWriteBlocked:
                pass
            else:
                raise AssertionError("atomic replace failure should raise a safe write-blocked error")
        finally:
            saved_action_source_mod.os.replace = original_replace

        _assert(
            source_path.read_text(encoding="utf-8") == original_text,
            "atomic replace failure should preserve the original saved-action source contents",
        )
        _assert(
            not any(path.suffix == ".tmp" for path in source_path.parent.iterdir()),
            "atomic replace failure should not leave orphaned temp files behind",
        )


def _test_edit_loads_existing_saved_action_draft():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_reports",
                        "title": "Open Reports",
                        "target_kind": "folder",
                        "target": r"C:\Reports",
                        "aliases": ["show reports", "view reports"],
                    }
                ],
            },
        )

        draft = load_saved_action_draft_for_edit("open_reports", source_path)

        _assert(draft.title == "Open Reports", "edit loading should preload the existing title")
        _assert(draft.target_kind == "folder", "edit loading should preload the existing target kind")
        _assert(draft.target == r"C:\Reports", "edit loading should preload the existing target")
        _assert(
            draft.aliases == ("show reports", "view reports"),
            "edit loading should preload the existing aliases",
        )


def _test_valid_edit_updates_existing_record_and_preserves_id():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_reports",
                        "title": "Open Reports",
                        "target_kind": "folder",
                        "target": r"C:\Reports",
                        "aliases": ["show reports"],
                    }
                ],
            },
        )

        result = update_saved_action_from_draft(
            "open_reports",
            SavedActionDraft(
                title="Open Weekly Reports",
                target_kind="file",
                target=r"C:\Reports\weekly.txt",
                aliases=("weekly reports",),
            ),
            source_path,
        )

        payload = json.loads(source_path.read_text(encoding="utf-8"))
        actions = payload.get("actions") or []

        _assert(len(actions) == 1, "valid edit should preserve the number of saved actions")
        _assert(actions[0]["id"] == "open_reports", "valid edit should preserve the existing saved-action id")
        _assert(actions[0]["title"] == "Open Weekly Reports", "valid edit should update the title in place")
        _assert(actions[0]["target_kind"] == "file", "valid edit should update the target kind in place")
        _assert(
            actions[0]["target"] == r"C:\Reports\weekly.txt",
            "valid edit should update the target in place",
        )
        _assert(
            actions[0]["aliases"] == ["weekly reports"],
            "valid edit should replace aliases safely in place",
        )
        _assert(
            result.catalog.saved_action_inventory.actions[0].id == "open_reports",
            "valid edit should reload the updated action without changing its identity",
        )


def _test_edit_rejects_builtin_collisions_without_writing():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_reports",
                        "title": "Open Reports",
                        "target_kind": "folder",
                        "target": r"C:\Reports",
                        "aliases": ["show reports"],
                    }
                ],
            },
        )
        original_text = source_path.read_text(encoding="utf-8")

        try:
            update_saved_action_from_draft(
                "open_reports",
                SavedActionDraft(
                    title="Explorer Helper",
                    target_kind="app",
                    target="explorer.exe",
                    aliases=("Open Windows Explorer",),
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("editing into a built-in collision should be rejected")

        _assert(
            source_path.read_text(encoding="utf-8") == original_text,
            "rejecting a built-in collision during edit should leave the source untouched",
        )


def _test_edit_rejects_other_saved_action_collisions_without_self_collision():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_reports",
                        "title": "Open Reports",
                        "target_kind": "folder",
                        "target": r"C:\Reports",
                        "aliases": ["show reports"],
                    },
                    {
                        "id": "open_docs",
                        "title": "Open Knowledge Base",
                        "target_kind": "url",
                        "target": "https://example.com/knowledge",
                        "aliases": ["show knowledge base"],
                    },
                ],
            },
        )
        original_text = source_path.read_text(encoding="utf-8")

        result = update_saved_action_from_draft(
            "open_reports",
            SavedActionDraft(
                title="Open Reports",
                target_kind="folder",
                target=r"C:\Reports\Archive",
                aliases=("show reports",),
            ),
            source_path,
        )
        _assert(
            result.record["id"] == "open_reports",
            "editing a record without changing its phrases should not self-collide",
        )

        try:
            update_saved_action_from_draft(
                "open_reports",
                SavedActionDraft(
                    title="Reports Label",
                    target_kind="folder",
                    target=r"C:\Reports",
                    aliases=("show knowledge base",),
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("editing into another saved-action phrase should be rejected")

        _assert(
            json.loads(source_path.read_text(encoding="utf-8"))["actions"][0]["id"] == "open_reports",
            "edit collisions should not change the saved-action identity",
        )
        _assert(
            json.loads(source_path.read_text(encoding="utf-8"))["actions"][1]["id"] == "open_docs",
            "edit collisions should not disturb other saved actions",
        )


def _test_invalid_edit_input_is_rejected_before_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_docs",
                        "title": "Open Knowledge Base",
                        "target_kind": "url",
                        "target": "https://example.com/knowledge",
                        "aliases": ["show knowledge base"],
                    }
                ],
            },
        )
        original_text = source_path.read_text(encoding="utf-8")

        try:
            update_saved_action_from_draft(
                "open_docs",
                SavedActionDraft(
                    title="Open Knowledge Base",
                    target_kind="url",
                    target="example.com/docs",
                    aliases=("show knowledge base",),
                ),
                source_path,
            )
        except SavedActionDraftValidationError:
            pass
        else:
            raise AssertionError("invalid edit inputs should be rejected before write")

        _assert(
            source_path.read_text(encoding="utf-8") == original_text,
            "rejecting invalid edit input should leave the saved-action source untouched",
        )


def _test_invalid_non_url_edit_targets_are_rejected_before_write():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_reports",
                        "title": "Open Reports",
                        "target_kind": "folder",
                        "target": r"C:\Reports",
                        "aliases": ["show reports"],
                    }
                ],
            },
        )
        original_text = source_path.read_text(encoding="utf-8")

        for target_kind, target in (
            ("app", r"C:\Program Files\Notepad"),
            ("folder", r"C:\Reports\Bad|Folder"),
            ("file", r"Reports\weekly.txt"),
        ):
            try:
                update_saved_action_from_draft(
                    "open_reports",
                    SavedActionDraft(
                        title="Open Reports",
                        target_kind=target_kind,
                        target=target,
                        aliases=("show reports",),
                    ),
                    source_path,
                )
            except SavedActionDraftValidationError:
                pass
            else:
                raise AssertionError(f"invalid {target_kind} edit targets should be rejected before write")

            _assert(
                source_path.read_text(encoding="utf-8") == original_text,
                f"rejecting invalid {target_kind} edit targets should leave the saved-action source untouched",
            )


def _test_invalid_existing_saved_actions_block_edit_completely():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "saved_actions.json"
        original_text = json.dumps(
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_reports",
                        "title": "Open Reports",
                        "target_kind": "folder",
                        "target": r"C:\Reports",
                        "aliases": ["show reports"],
                    },
                    {
                        "id": "open_reports_archive",
                        "title": "Open Reports Archive",
                        "target_kind": "folder",
                        "target": r"C:\Reports\Archive",
                        "aliases": ["show reports"],
                    },
                ],
            },
            indent=2,
        ) + "\n"
        source_path.write_text(original_text, encoding="utf-8")

        try:
            update_saved_action_from_draft(
                "open_reports",
                SavedActionDraft(
                    title="Open Reports Folder",
                    target_kind="folder",
                    target=r"C:\Reports",
                    aliases=("view reports",),
                ),
                source_path,
            )
        except SavedActionUnsafeSourceError:
            pass
        else:
            raise AssertionError("invalid existing saved-action states should block edits completely")

        _assert(
            source_path.read_text(encoding="utf-8") == original_text,
            "blocking unsafe edit sources should leave the original saved-action source untouched",
        )


def main():
    tests = [
        ("create persists saved action and preserves template fields", _test_create_persists_saved_action_and_preserves_template_fields),
        ("id generation avoids existing saved ids", _test_id_generation_avoids_existing_saved_ids),
        ("create supports all persisted target kinds", _test_create_supports_all_persisted_target_kinds),
        ("new saved actions persist default trigger modes", _test_new_saved_actions_persist_default_trigger_modes),
        ("generated trigger phrases resolve for saved actions", _test_generated_trigger_phrases_resolve_for_saved_actions),
        ("custom trigger phrases persist and resolve", _test_custom_trigger_phrases_persist_and_resolve),
        ("custom trigger validation stays bounded", _test_custom_trigger_validation_is_bounded),
        ("new alias-root tasks require at least one alias", _test_new_alias_root_tasks_require_at_least_one_alias),
        ("invalid inputs rejected before write", _test_invalid_inputs_are_rejected_before_write),
        ("invalid non-url targets rejected before write", _test_invalid_non_url_targets_are_rejected_before_write),
        ("built-in collisions rejected before write", _test_builtin_collisions_are_rejected_before_write),
        ("generated trigger phrases collide with built-ins before write", _test_generated_trigger_phrase_collides_with_built_in_before_write),
        ("existing saved-action collisions rejected before write", _test_existing_saved_action_phrase_collisions_are_rejected_before_write),
        ("generated trigger phrases collide with saved actions before write", _test_generated_trigger_phrase_collides_with_existing_saved_action_before_write),
        ("legacy saved actions remain bare-only without trigger fields", _test_existing_saved_actions_without_trigger_fields_remain_bare_only),
        ("legacy saved actions keep title callability when edited", _test_legacy_saved_actions_keep_title_callability_when_edited),
        ("invalid existing saved actions block write", _test_invalid_existing_saved_actions_block_write_completely),
        ("atomic write failure preserves existing source", _test_atomic_write_failure_preserves_existing_source),
        ("edit loads existing saved action draft", _test_edit_loads_existing_saved_action_draft),
        ("valid edit updates existing record and preserves id", _test_valid_edit_updates_existing_record_and_preserves_id),
        ("edit rejects built-in collisions without write", _test_edit_rejects_builtin_collisions_without_writing),
        ("edit rejects other saved-action collisions without self-collision", _test_edit_rejects_other_saved_action_collisions_without_self_collision),
        ("invalid edit input is rejected before write", _test_invalid_edit_input_is_rejected_before_write),
        ("invalid non-url edit targets rejected before write", _test_invalid_non_url_edit_targets_are_rejected_before_write),
        ("invalid existing saved actions block edit", _test_invalid_existing_saved_actions_block_edit_completely),
    ]

    for name, fn in tests:
        fn()
        print(f"PASS: {name}")

    print("SAVED ACTION AUTHORING VALIDATION: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
