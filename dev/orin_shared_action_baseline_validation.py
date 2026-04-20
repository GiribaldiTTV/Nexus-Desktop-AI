import os
import sys


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import desktop.shared_action_model as shared_action_mod
from desktop.shared_action_model import (
    CommandAction,
    CommandActionCatalog,
    DEFAULT_COMMAND_ACTIONS,
    SUPPORTED_ACTION_TARGET_KINDS,
    normalize_command_text,
)


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _ids(actions):
    return tuple(action.id for action in actions)


def _build_resolution_catalog():
    return CommandActionCatalog(
        (
            CommandAction(
                id="open_reports_primary",
                title="Open Reports",
                target_kind="folder",
                target=r"C:\Reports\Primary",
                aliases=("show reports", "open reporting workspace"),
            ),
            CommandAction(
                id="open_reports_archive",
                title="Open Reports Archive",
                target_kind="folder",
                target=r"C:\Reports\Archive",
                aliases=("show reports", "open archived reports"),
            ),
            CommandAction(
                id="open_tools",
                title="Open Tools",
                target_kind="folder",
                target=r"C:\Tools",
                aliases=("show tools",),
            ),
        )
    )


def _test_normalization_contract():
    _assert(
        normalize_command_text("  Open   File Explorer!!! ") == "open file explorer",
        "normalization should casefold, collapse whitespace, and trim trailing punctuation",
    )
    _assert(
        normalize_command_text("Open Saved Actions File??") == "open saved actions file",
        "normalization should trim question-mark punctuation as part of the exact-match contract",
    )
    _assert(normalize_command_text("") == "", "empty text should normalize to empty text")


def _test_exact_match_contract_on_custom_catalog():
    catalog = _build_resolution_catalog()

    _assert(
        _ids(catalog.resolve_actions("open reports")) == ("open_reports_primary",),
        "exact title matches should return one exact resolved action",
    )
    _assert(
        _ids(catalog.resolve_actions("SHOW TOOLS!!!")) == ("open_tools",),
        "exact alias matches should work after normalization",
    )
    _assert(
        catalog.resolve_actions("open report") == (),
        "near-miss phrasing should not resolve under the exact-match baseline",
    )
    _assert(
        catalog.resolve_actions("launch report center") == (),
        "semantic intent should not be inferred under the current baseline",
    )


def _test_ambiguous_match_contract_on_custom_catalog():
    catalog = _build_resolution_catalog()
    matches = catalog.resolve_actions("show reports")

    _assert(len(matches) == 2, "shared-action resolution should preserve explicit ambiguity when two actions match")
    _assert(
        _ids(matches) == ("open_reports_primary", "open_reports_archive"),
        "ambiguous resolution should preserve the matched action set in catalog order",
    )


def _test_builtin_catalog_integrity():
    built_in_ids = set()

    _assert(DEFAULT_COMMAND_ACTIONS, "the built-in shared action catalog should not be empty")
    for action in DEFAULT_COMMAND_ACTIONS:
        _assert(action.id and action.id.strip(), "built-in action ids must be non-empty")
        _assert(action.id not in built_in_ids, "built-in action ids must stay unique")
        built_in_ids.add(action.id)

        _assert(action.title and action.title.strip(), f"{action.id} should keep a non-empty title")
        _assert(
            action.target_kind in SUPPORTED_ACTION_TARGET_KINDS,
            f"{action.id} should keep a supported target kind",
        )
        _assert(action.origin == "built_in", f"{action.id} should preserve built-in origin metadata")
        _assert(action.target and str(action.target).strip(), f"{action.id} should keep a non-empty target")

        normalized_title = normalize_command_text(action.title)
        _assert(normalized_title, f"{action.id} title should normalize to a non-empty phrase")
        for alias in action.aliases:
            _assert(normalize_command_text(alias), f"{action.id} aliases should normalize to non-empty phrases")


def _test_task_manager_builtin_catalog_entry():
    matches = tuple(action for action in DEFAULT_COMMAND_ACTIONS if action.id == "open_task_manager")

    _assert(len(matches) == 1, "the Task Manager built-in should exist exactly once")
    action = matches[0]
    _assert(action.title == "Open Task Manager", "the Task Manager built-in should keep the intended title")
    _assert(action.target_kind == "app", "the Task Manager built-in should use the existing app target kind")
    _assert(action.target == "taskmgr.exe", "the Task Manager built-in should launch taskmgr.exe")
    _assert(action.origin == "built_in", "the Task Manager built-in should preserve built-in origin metadata")
    _assert(
        action.aliases == ("open task manager", "task manager", "launch task manager"),
        "the Task Manager built-in should expose the approved exact aliases",
    )

    catalog = CommandActionCatalog()
    for phrase in ("open task manager", "task manager", "launch task manager"):
        _assert(
            _ids(catalog.resolve_actions(phrase)) == ("open_task_manager",),
            f"{phrase!r} should resolve to the Task Manager built-in",
        )


def _test_calculator_builtin_catalog_entry():
    matches = tuple(action for action in DEFAULT_COMMAND_ACTIONS if action.id == "open_calculator")

    _assert(len(matches) == 1, "the Calculator built-in should exist exactly once")
    action = matches[0]
    _assert(action.title == "Open Calculator", "the Calculator built-in should keep the intended title")
    _assert(action.target_kind == "app", "the Calculator built-in should use the existing app target kind")
    _assert(action.target == "calc.exe", "the Calculator built-in should launch calc.exe")
    _assert(action.origin == "built_in", "the Calculator built-in should preserve built-in origin metadata")
    _assert(
        action.aliases == ("open calculator", "calculator", "launch calculator"),
        "the Calculator built-in should expose the approved exact aliases",
    )

    catalog = CommandActionCatalog()
    for phrase in ("open calculator", "calculator", "launch calculator"):
        _assert(
            _ids(catalog.resolve_actions(phrase)) == ("open_calculator",),
            f"{phrase!r} should resolve to the Calculator built-in",
        )


def _test_notepad_builtin_catalog_entry():
    matches = tuple(action for action in DEFAULT_COMMAND_ACTIONS if action.id == "open_notepad")

    _assert(len(matches) == 1, "the Notepad built-in should exist exactly once")
    action = matches[0]
    _assert(action.title == "Open Notepad", "the Notepad built-in should keep the intended title")
    _assert(action.target_kind == "app", "the Notepad built-in should use the existing app target kind")
    _assert(action.target == "notepad.exe", "the Notepad built-in should launch notepad.exe")
    _assert(action.origin == "built_in", "the Notepad built-in should preserve built-in origin metadata")
    _assert(
        action.aliases == ("open notepad", "notepad", "launch notepad"),
        "the Notepad built-in should expose the approved exact aliases",
    )

    catalog = CommandActionCatalog()
    for phrase in ("open notepad", "notepad", "launch notepad"):
        _assert(
            _ids(catalog.resolve_actions(phrase)) == ("open_notepad",),
            f"{phrase!r} should resolve to the Notepad built-in",
        )


def _test_paint_builtin_catalog_entry():
    matches = tuple(action for action in DEFAULT_COMMAND_ACTIONS if action.id == "open_paint")

    _assert(len(matches) == 1, "the Paint built-in should exist exactly once")
    action = matches[0]
    _assert(action.title == "Open Paint", "the Paint built-in should keep the intended title")
    _assert(action.target_kind == "app", "the Paint built-in should use the existing app target kind")
    _assert(action.target == "mspaint.exe", "the Paint built-in should launch mspaint.exe")
    _assert(action.origin == "built_in", "the Paint built-in should preserve built-in origin metadata")
    _assert(
        action.aliases == ("open paint", "paint", "launch paint"),
        "the Paint built-in should expose the approved exact aliases",
    )

    catalog = CommandActionCatalog()
    for phrase in ("open paint", "paint", "launch paint"):
        _assert(
            _ids(catalog.resolve_actions(phrase)) == ("open_paint",),
            f"{phrase!r} should resolve to the Paint built-in",
        )


def _test_saved_actions_override_builtin_phrase_collisions():
    saved_action = CommandAction(
        id="personal_task_manager",
        title="Task Manager",
        target_kind="app",
        target="notepad.exe",
        aliases=("open task manager", "launch task manager"),
        origin="saved",
    )
    catalog = CommandActionCatalog((*DEFAULT_COMMAND_ACTIONS, saved_action))

    for phrase in ("task manager", "open task manager", "launch task manager"):
        resolved = catalog.resolve_actions(phrase)
        _assert(
            _ids(resolved) == ("personal_task_manager",),
            f"saved actions should override built-in phrase collisions for {phrase!r}",
        )
        _assert(
            resolved[0].origin == "saved",
            "saved-action phrase collisions should resolve to saved origin metadata",
        )

    _assert(
        _ids(catalog.resolve_actions("open file explorer")) == ("open_windows_explorer",),
        "built-ins should remain the fallback when no saved action matches the phrase",
    )


def _test_saved_actions_override_calculator_builtin_phrase_collisions():
    saved_action = CommandAction(
        id="personal_calculator",
        title="Calculator",
        target_kind="app",
        target="notepad.exe",
        aliases=("open calculator", "launch calculator"),
        origin="saved",
    )
    catalog = CommandActionCatalog((*DEFAULT_COMMAND_ACTIONS, saved_action))

    for phrase in ("calculator", "open calculator", "launch calculator"):
        resolved = catalog.resolve_actions(phrase)
        _assert(
            _ids(resolved) == ("personal_calculator",),
            f"saved actions should override Calculator built-in phrase collisions for {phrase!r}",
        )
        _assert(
            resolved[0].origin == "saved",
            "Calculator phrase collisions should resolve to saved origin metadata",
        )

    _assert(
        _ids(catalog.resolve_actions("open file explorer")) == ("open_windows_explorer",),
        "built-ins should remain the fallback after the Calculator saved-action override check",
    )


def _test_saved_actions_override_notepad_builtin_phrase_collisions():
    saved_action = CommandAction(
        id="personal_notepad",
        title="Notepad",
        target_kind="app",
        target="calc.exe",
        aliases=("open notepad", "launch notepad"),
        origin="saved",
    )
    catalog = CommandActionCatalog((*DEFAULT_COMMAND_ACTIONS, saved_action))

    for phrase in ("notepad", "open notepad", "launch notepad"):
        resolved = catalog.resolve_actions(phrase)
        _assert(
            _ids(resolved) == ("personal_notepad",),
            f"saved actions should override Notepad built-in phrase collisions for {phrase!r}",
        )
        _assert(
            resolved[0].origin == "saved",
            "Notepad phrase collisions should resolve to saved origin metadata",
        )

    _assert(
        _ids(catalog.resolve_actions("open file explorer")) == ("open_windows_explorer",),
        "built-ins should remain the fallback after the Notepad saved-action override check",
    )


def _test_saved_actions_override_paint_builtin_phrase_collisions():
    saved_action = CommandAction(
        id="personal_paint",
        title="Paint",
        target_kind="app",
        target="notepad.exe",
        aliases=("open paint", "launch paint"),
        origin="saved",
    )
    catalog = CommandActionCatalog((*DEFAULT_COMMAND_ACTIONS, saved_action))

    for phrase in ("paint", "open paint", "launch paint"):
        resolved = catalog.resolve_actions(phrase)
        _assert(
            _ids(resolved) == ("personal_paint",),
            f"saved actions should override Paint built-in phrase collisions for {phrase!r}",
        )
        _assert(
            resolved[0].origin == "saved",
            "Paint phrase collisions should resolve to saved origin metadata",
        )

    _assert(
        _ids(catalog.resolve_actions("open file explorer")) == ("open_windows_explorer",),
        "built-ins should remain the fallback after the Paint saved-action override check",
    )


def _test_url_target_support_is_first_class():
    _assert("url" in SUPPORTED_ACTION_TARGET_KINDS, "url targets should be a supported action target kind")

    catalog = CommandActionCatalog(
        (
            CommandAction(
                id="open_nexus_docs_site",
                title="Open Nexus Docs Site",
                target_kind="url",
                target="https://example.com/docs/start",
                aliases=("open docs site",),
                origin="saved",
            ),
        )
    )

    _assert(
        _ids(catalog.resolve_actions("open docs site")) == ("open_nexus_docs_site",),
        "url actions should resolve through the same exact-match shared action catalog",
    )
    _assert(
        catalog.resolve_actions("open docs site")[0].origin == "saved",
        "url saved actions should preserve saved origin metadata inside the shared catalog",
    )
    _assert(
        catalog.format_target_display("url", "https://example.com/docs/start") == "example.com/docs/start",
        "url actions should surface a compact confirm-target display",
    )


def _test_url_launch_uses_system_handler_without_path_normalization():
    launches = []
    original_startfile = shared_action_mod.os.startfile
    original_popen = shared_action_mod.subprocess.Popen
    shared_action_mod.os.startfile = lambda target: launches.append(target)
    shared_action_mod.subprocess.Popen = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        AssertionError("url launches should not go through subprocess Popen")
    )

    try:
        shared_action_mod.launch_command_action(
            CommandAction(
                id="open_nexus_docs_site",
                title="Open Nexus Docs Site",
                target_kind="url",
                target="https://example.com/docs/start",
                aliases=(),
            )
        )
    finally:
        shared_action_mod.os.startfile = original_startfile
        shared_action_mod.subprocess.Popen = original_popen

    _assert(
        launches == ["https://example.com/docs/start"],
        "url launches should use the original URL string through the system handler",
    )


def _test_default_catalog_wrapper_preserves_builtin_catalog():
    catalog = CommandActionCatalog()

    _assert(
        len(catalog.actions) == len(DEFAULT_COMMAND_ACTIONS),
        "the default catalog wrapper should expose the current built-in catalog without dropping actions",
    )
    _assert(
        tuple(action.id for action in catalog.actions) == tuple(action.id for action in DEFAULT_COMMAND_ACTIONS),
        "the default catalog wrapper should preserve built-in catalog ordering",
    )


def main():
    tests = [
        ("normalization contract", _test_normalization_contract),
        ("exact match contract", _test_exact_match_contract_on_custom_catalog),
        ("ambiguous match contract", _test_ambiguous_match_contract_on_custom_catalog),
        ("built-in catalog integrity", _test_builtin_catalog_integrity),
        ("task manager built-in catalog entry", _test_task_manager_builtin_catalog_entry),
        ("calculator built-in catalog entry", _test_calculator_builtin_catalog_entry),
        ("notepad built-in catalog entry", _test_notepad_builtin_catalog_entry),
        ("paint built-in catalog entry", _test_paint_builtin_catalog_entry),
        ("saved actions override built-in phrase collisions", _test_saved_actions_override_builtin_phrase_collisions),
        ("saved actions override Calculator built-in phrase collisions", _test_saved_actions_override_calculator_builtin_phrase_collisions),
        ("saved actions override Notepad built-in phrase collisions", _test_saved_actions_override_notepad_builtin_phrase_collisions),
        ("saved actions override Paint built-in phrase collisions", _test_saved_actions_override_paint_builtin_phrase_collisions),
        ("url target support", _test_url_target_support_is_first_class),
        ("url launch path", _test_url_launch_uses_system_handler_without_path_normalization),
        ("default catalog wrapper", _test_default_catalog_wrapper_preserves_builtin_catalog),
    ]

    for name, fn in tests:
        fn()
        print(f"PASS: {name}")

    print("SHARED ACTION BASELINE VALIDATION: PASS")


if __name__ == "__main__":
    raise SystemExit(main())
