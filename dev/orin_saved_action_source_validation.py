import json
import os
import sys
import tempfile
from pathlib import Path


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from desktop.saved_action_source import load_saved_action_source, resolve_default_saved_action_source_path
from desktop.shared_action_model import (
    DEFAULT_COMMAND_ACTIONS,
    build_default_command_action_catalog,
    load_saved_command_actions,
)


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict):
    _write_text(path, json.dumps(payload, indent=2) + "\n")


def _with_local_app_data(temp_path: str):
    class _LocalAppDataContext:
        def __enter__(self_inner):
            self_inner._original = os.environ.get("LOCALAPPDATA")
            os.environ["LOCALAPPDATA"] = temp_path
            return self_inner

        def __exit__(self_inner, exc_type, exc, tb):
            if self_inner._original is None:
                os.environ.pop("LOCALAPPDATA", None)
            else:
                os.environ["LOCALAPPDATA"] = self_inner._original

    return _LocalAppDataContext()


def _builtin_ids():
    return tuple(action.id for action in DEFAULT_COMMAND_ACTIONS)


def _test_default_source_bootstraps_template_without_actions():
    with tempfile.TemporaryDirectory() as temp_dir:
        with _with_local_app_data(temp_dir):
            path = resolve_default_saved_action_source_path()
            payload = load_saved_action_source()

            _assert(payload is None, "the default starter template should not count as active saved actions")
            _assert(path.is_file(), "loading the default source should bootstrap the starter JSON file")

            raw = json.loads(path.read_text(encoding="utf-8"))
            _assert(raw.get("schema_version") == 1, "the bootstrapped template should preserve schema version 1")
            _assert(isinstance(raw.get("examples"), list), "the bootstrapped template should preserve starter examples")


def _test_missing_custom_source_falls_back_to_built_ins_only():
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_path = Path(temp_dir) / "missing" / "saved_actions.json"

        _assert(load_saved_action_source(custom_path) is None, "a missing custom source should not produce a payload")
        _assert(load_saved_command_actions(custom_path) == (), "a missing custom source should resolve to no saved actions")

        catalog = build_default_command_action_catalog(custom_path)
        _assert(
            tuple(action.id for action in catalog.actions) == _builtin_ids(),
            "a missing custom source should leave the effective catalog at built-ins only",
        )


def _test_empty_or_invalid_custom_sources_fail_closed():
    with tempfile.TemporaryDirectory() as temp_dir:
        empty_path = Path(temp_dir) / "empty.json"
        invalid_path = Path(temp_dir) / "invalid.json"

        _write_text(empty_path, "   \n")
        _write_text(invalid_path, "{ not valid json")

        _assert(load_saved_action_source(empty_path) is None, "an empty custom source should not produce a payload")
        _assert(load_saved_command_actions(empty_path) == (), "an empty custom source should fail closed to no saved actions")
        _assert(load_saved_action_source(invalid_path) is None, "invalid JSON should not produce a payload")
        _assert(load_saved_command_actions(invalid_path) == (), "invalid JSON should fail closed to no saved actions")


def _test_valid_saved_actions_extend_the_effective_catalog():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "valid_saved_actions.json"
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
                        "aliases": ["open reports", "show reports"],
                    }
                ],
            },
        )

        payload = load_saved_action_source(source_path)
        saved_actions = load_saved_command_actions(source_path)
        catalog = build_default_command_action_catalog(source_path)

        _assert(payload is not None and len(payload.actions) == 1, "a valid custom source should load one payload action")
        _assert(len(saved_actions) == 1 and saved_actions[0].id == "open_reports", "a valid saved action should become one effective saved action")
        _assert(
            len(catalog.actions) == len(DEFAULT_COMMAND_ACTIONS) + 1,
            "a valid saved action should extend the effective catalog above the built-ins",
        )
        _assert(
            tuple(action.id for action in catalog.actions[:-1]) == _builtin_ids(),
            "extending the catalog should preserve built-in actions ahead of saved actions",
        )


def _test_valid_url_saved_actions_extend_the_effective_catalog():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "valid_url_saved_actions.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_nexus_docs_site",
                        "title": "Open Nexus Docs Site",
                        "target_kind": "url",
                        "target": "https://example.com/docs/start",
                        "aliases": ["open docs site"],
                    }
                ],
            },
        )

        saved_actions = load_saved_command_actions(source_path)
        catalog = build_default_command_action_catalog(source_path)

        _assert(
            len(saved_actions) == 1 and saved_actions[0].target_kind == "url",
            "a valid url saved action should be accepted into the effective saved-action catalog",
        )
        _assert(
            saved_actions[0].target == "https://example.com/docs/start",
            "accepted url saved actions should preserve their original target string",
        )
        _assert(
            catalog.actions[-1].id == "open_nexus_docs_site" and catalog.actions[-1].target_kind == "url",
            "valid url saved actions should extend the effective catalog as first-class actions",
        )


def _test_unsupported_target_kind_fails_closed():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "unsupported_target_kind.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_docs_url",
                        "title": "Open Docs URL",
                        "target_kind": "routine",
                        "target": "https://example.com/docs",
                        "aliases": ["open docs url"],
                    }
                ],
            },
        )

        _assert(
            load_saved_command_actions(source_path) == (),
            "unsupported saved-action target kinds should fail closed to no saved actions",
        )


def _test_invalid_url_targets_fail_closed():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "invalid_url_target.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_docs_url",
                        "title": "Open Docs URL",
                        "target_kind": "url",
                        "target": "example.com/docs",
                        "aliases": ["open docs url"],
                    }
                ],
            },
        )

        _assert(
            load_saved_command_actions(source_path) == (),
            "invalid url saved-action targets should fail closed to no saved actions",
        )


def _test_duplicate_saved_ids_fail_closed():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "duplicate_ids.json"
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
                        "aliases": ["open reports"],
                    },
                    {
                        "id": "open_reports",
                        "title": "Open Reports Backup",
                        "target_kind": "folder",
                        "target": r"C:\Reports\Backup",
                        "aliases": ["open reports backup"],
                    },
                ],
            },
        )

        _assert(
            load_saved_command_actions(source_path) == (),
            "duplicate saved-action ids should fail closed to no saved actions",
        )


def _test_duplicate_saved_phrases_fail_closed():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "duplicate_phrases.json"
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
                        "id": "open_reports_archive",
                        "title": "Open Reports Archive",
                        "target_kind": "folder",
                        "target": r"C:\Reports\Archive",
                        "aliases": ["show reports"],
                    },
                ],
            },
        )

        _assert(
            load_saved_command_actions(source_path) == (),
            "duplicate saved-action titles or aliases should fail closed to no saved actions",
        )


def _test_builtin_collisions_fail_closed():
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / "builtin_collision.json"
        _write_json(
            source_path,
            {
                "schema_version": 1,
                "actions": [
                    {
                        "id": "open_windows_explorer",
                        "title": "Open Explorer Again",
                        "target_kind": "app",
                        "target": "explorer.exe",
                        "aliases": ["open explorer again"],
                    }
                ],
            },
        )

        _assert(
            load_saved_command_actions(source_path) == (),
            "collisions against built-in ids or phrases should fail closed to no saved actions",
        )


def main():
    tests = [
        ("default source bootstrap", _test_default_source_bootstraps_template_without_actions),
        ("missing custom source fallback", _test_missing_custom_source_falls_back_to_built_ins_only),
        ("empty and invalid source fallback", _test_empty_or_invalid_custom_sources_fail_closed),
        ("valid saved actions extend catalog", _test_valid_saved_actions_extend_the_effective_catalog),
        ("valid url saved actions extend catalog", _test_valid_url_saved_actions_extend_the_effective_catalog),
        ("unsupported target kind fails closed", _test_unsupported_target_kind_fails_closed),
        ("invalid url targets fail closed", _test_invalid_url_targets_fail_closed),
        ("duplicate saved ids fail closed", _test_duplicate_saved_ids_fail_closed),
        ("duplicate saved phrases fail closed", _test_duplicate_saved_phrases_fail_closed),
        ("built-in collisions fail closed", _test_builtin_collisions_fail_closed),
    ]

    for name, fn in tests:
        fn()
        print(f"PASS: {name}")

    print("SAVED ACTION SOURCE VALIDATION: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
