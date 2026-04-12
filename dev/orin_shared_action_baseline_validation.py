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
