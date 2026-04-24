import json
import re
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

PHASES = (
    "Branch Readiness",
    "Workstream",
    "Hardening",
    "Live Validation",
    "PR Readiness",
    "Release Readiness",
)

BRANCH_CLASSES = (
    "implementation",
    "docs/governance",
    "emergency canon repair",
    "release packaging",
)

PROMPT_CONTRACT_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/orin_task_template.md"),
)

CURRENT_STATE_OWNER_DOCS = (
    Path("Docs/Main.md"),
    Path("Docs/feature_backlog.md"),
    Path("Docs/prebeta_roadmap.md"),
    Path("Docs/workstreams/index.md"),
    Path("Docs/closeout_index.md"),
)

AUXILIARY_GUIDANCE_DOCS = (
    Path("Docs/closeout_guidance.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/orin_task_template.md"),
)

OLD_PHASE_TERMS = (
    "Workstream Analysis",
    "Approved Execution",
    "Validation / Hardening",
    "Docs / Canon Sync",
    "Post-Release Canon Sync",
    "post-release canon sync",
)

BANNED_BRANCH_CLASS_SPELLINGS = (
    "docs-governance",
    "emergency-canon-repair",
    "release-packaging",
)

STALE_CURRENT_STATE_TERMS = (
    "pending merge",
    "Promoted for pre-implementation setup",
    "Current Selected Workstream",
    "until merged-canon repair and release-debt handling are complete",
    "merged-canon repair and release-debt handling remain outstanding",
    "merged canon still carries stale active or pre-implementation",
)

STALE_AUXILIARY_TERMS = (
    "v1.2.8-prebeta",
)

REQUIRED_WORKSTREAM_HEADINGS = (
    "## Current Phase",
    "## Phase Status",
    "## Branch Class",
    "## Blockers",
    "## Entry Basis",
    "## Exit Criteria",
    "## Rollback Target",
    "## Next Legal Phase",
)

REQUIRED_BRANCH_READINESS_DURABILITY_HEADINGS = (
    "## Branch Objective",
    "## Target End-State",
    "## Expected Seam Families And Risk Classes",
    "## User Test Summary Strategy",
    "## Later-Phase Expectations",
    "## Initial Workstream Seam Sequence",
    "## Active Seam",
)

REQUIRED_BRANCH_READINESS_FIRST_SEAM_MARKERS = (
    "Seam 1:",
    "Goal:",
    "Scope:",
    "Non-Includes:",
)

SUCCESSOR_LOCK_WAIVER_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
)

SUCCESSOR_LOCK_WAIVER_PHRASE = (
    "If post-merge truth will resolve to `No Active Branch` because `Release Debt` "
    "or another repo-level admission blocker remains open"
)

NO_ACTIVE_BRANCH_STEADY_STATE_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

NO_ACTIVE_BRANCH_STEADY_STATE_PHRASE = "steady-state `No Active Branch`"

DOCS_GOVERNANCE_ADMISSION_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_user_guide.md"),
)

GOVERNANCE_ONLY_BLOCK_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/closeout_guidance.md"),
)

GOVERNANCE_ONLY_BLOCK_PHRASES = (
    "governance-only branch",
    "between-branch",
)

MULTI_SEAM_CONTRACT_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/Main.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

MULTI_SEAM_CONTRACT_PHRASES = (
    "bounded multi-seam workflow",
    "Next-Seam Continuation Required",
    "entry seam, not a terminal boundary",
    "Perform all admitted seams in the bounded multi-seam workflow unless an explicit `Single-Seam Mode Waiver` is raised or a named bounded stop condition is recorded.",
    "Single-Seam Mode Waiver",
    "bounded stop condition",
    "Single-Seam Fallback",
    "reporting `Next Safe Move` is not a substitute for execution",
    "A `continue` decision must be acted on immediately",
)

MULTI_SEAM_PRIMARY_REPAIR_PHRASES = (
    "Category labels are not stop conditions by themselves.",
    "`Single-Seam Fallback` is legacy terminology for `Single-Seam Mode Waiver`.",
    "Single-seam mode is waiver-only.",
    "A bounded stop condition blocks the workflow. It does not by itself authorize single-seam mode.",
    "Perform all admitted seams in the bounded multi-seam workflow unless an explicit `Single-Seam Mode Waiver` is raised or a named bounded stop condition is recorded.",
)

MULTI_SEAM_PROHIBITED_CATEGORY_STOP_PHRASES = (
    "single-seam fallback is required for bug fixes",
    "Use single-seam fallback for:",
    "Do not use this recipe for bug fixes, hotfixes",
    "unclear or high-risk seams, cross-subsystem changes, settings/protocol/launcher/UI-model changes",
    "settings, protocol, launcher-policy, or UI-model changes",
)

MULTI_SEAM_PROHIBITED_THROTTLE_PHRASES = (
    "do not encode a single-seam stop unless",
    "use `single-seam fallback` only when",
    "canon-valid `single-seam fallback`",
    "unless owning canon supplies `single-seam fallback`",
)

MULTI_SEAM_PROMPT_DOCS = (
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/nexus_startup_contract.md"),
)

MULTI_SEAM_PROMPT_PHRASES = (
    "Seam Sequence",
    "continue-or-stop",
    "Next-Seam Continuation Required",
    "entry seam, not a terminal boundary",
    "Perform all admitted seams in the bounded multi-seam workflow unless an explicit `Single-Seam Mode Waiver` is raised or a named bounded stop condition is recorded.",
    "Single-Seam Mode Waiver",
    "Single-Seam Fallback",
    "reporting Next Safe Move is not a substitute for execution",
    "continue decision must be acted on immediately",
)

REQUIRED_WORKSTREAM_CONTINUATION_MARKERS = (
    "Continue Decision:",
    "Next Active Seam:",
    "Stop Condition:",
    "Continuation Action:",
)

WORKSTREAM_TO_PR_DEFAULT_GUARD_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/codex_user_guide.md"),
)

WORKSTREAM_TO_PR_DEFAULT_GUARD_PHRASES = (
    "There is no default direct `Workstream` -> `PR Readiness` transition.",
    "The normal next legal phase is `Hardening`, then `Live Validation`, then `PR Readiness`.",
    "Do not prompt Codex to treat Workstream completion as direct `PR Readiness`.",
)

PRE_PR_DURABILITY_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

PRE_PR_DURABILITY_PHRASES = (
    "DO THIS ALWAYS",
    "Pre-PR Durability Rule",
    "Release Readiness is file-frozen",
    "block ANY",
    "before `PR Readiness`",
    "commit and push",
    "uncommitted state",
    "Durability Waiver",
    "self-imposed blocker",
    "automatically commit and push",
)

PLANNING_LOOP_GUARDRAIL_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/nexus_startup_contract.md"),
)

PLANNING_LOOP_GUARDRAIL_PHRASES = (
    "Branch Readiness owns planning, framing, affected-surface mapping, implementation delta classification, and admitted-slice definition before Workstream begins.",
    "Workstream must execute an admitted implementation slice unless the USER explicitly approves a docs-only bypass.",
    "Docs-only Workstreams require explicit USER approval.",
    "Planning-Loop Bypass User Approval: APPROVED",
    "Planning-Loop Bypass Reason:",
    "Release-bearing implementation work with no runtime/user-facing, backend/runtime, or developer-tooling delta is blocked unless the USER explicitly approves that release window.",
)

PLANNING_LOOP_ACTIVE_PHASES = (
    "Branch Readiness",
    "Workstream",
    "Hardening",
    "Live Validation",
    "PR Readiness",
)

PLANNING_LOOP_DELTA_CLASS_LABEL = "Implementation Delta Class"
PLANNING_LOOP_DOCS_ONLY_LABEL = "Docs-Only Workstream"
PLANNING_LOOP_BYPASS_APPROVAL_LABEL = "Planning-Loop Bypass User Approval"
PLANNING_LOOP_BYPASS_REASON_LABEL = "Planning-Loop Bypass Reason"
PLANNING_LOOP_DOCS_ONLY_DELTA = "docs-only"
REAL_IMPLEMENTATION_DELTA_CLASSES = frozenset(
    {"runtime/user-facing", "backend/runtime", "developer-tooling"}
)
ALLOWED_IMPLEMENTATION_DELTA_CLASSES = REAL_IMPLEMENTATION_DELTA_CLASSES | frozenset(
    {PLANNING_LOOP_DOCS_ONLY_DELTA}
)

LIVE_VALIDATION_REUSE_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/Main.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

LIVE_VALIDATION_REUSE_PHRASES = (
    "reuse",
    "existing",
    "one-off",
)

LIVE_VALIDATION_STALL_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/Main.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

LIVE_VALIDATION_STALL_PHRASES = (
    "10s",
    "no-progress",
    "last confirmed",
)

LIVE_VALIDATION_HELPER_CONTRACTS = {
    Path("dev/orin_launcher_live_window_audit.ps1"): (
        "NoProgressTimeoutSeconds",
        "Fb037Validation",
        "Write-AuditStep",
        "Last confirmed progress",
        "step_log",
        "failure_message",
        "cleanup_notes",
    ),
}

VALIDATION_HELPER_REGISTRY = Path("Docs/validation_helper_registry.md")

VALIDATION_HELPER_STANDARD_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/validation_helper_registry.md"),
)

VALIDATION_HELPER_STANDARD_PHRASES = (
    "Docs/validation_helper_registry.md",
    "Helper Status:",
    "Workstream-scoped",
    "Consolidation Target",
    "Temporary probe",
)

PR_READINESS_BLOCKER_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

PR_READINESS_BLOCKER_PHRASES = (
    "stale-canon",
    "post-merge",
    "dirty",
    "docs-sync",
    "next-workstream",
    "desktop-shortcut",
    "User Test Summary Results Pending",
    "PR Readiness Scope Missed",
    "Release Window Audit Incomplete",
    "Between-Branch Canon Repair Attempt",
    "Next Branch Created Too Early",
)

RELEASE_WINDOW_AUDIT_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/nexus_startup_contract.md"),
)

RELEASE_WINDOW_AUDIT_PHRASES = (
    "Release Window Audit",
    "Release Window Audit Incomplete",
    "Remaining Known Release Blockers: None",
    "Another Pre-Release Repair PR Required: NO",
    "Release Window Split Waiver: None",
)

PR_READINESS_RESPONSE_CONTRACT_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

PR_READINESS_RESPONSE_CONTRACT_PHRASES = (
    "## Next Branch",
    "Next Legal Branch Type:",
    "Next Branch Name:",
    "Branch Class:",
    "Creation Status:",
    "Creation Gate:",
    "Selected Next Workstream:",
    "Selected Next Implementation Branch:",
    "May Create Now: YES / NO",
    "## PR Creation Details",
    "### PR Title",
    "### Base Branch",
    "### Head Branch",
    "### PR Summary",
    "inclusion-only",
    "defensive scope language",
)

RELEASE_OPERATOR_OUTPUT_CONTRACT_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

RELEASE_OPERATOR_OUTPUT_CONTRACT_PHRASES = (
    "## Release Package Details",
    "### Release Title",
    "### Release Tag",
    "### Target Commit",
    "### Release Notes",
    "## Release Summary",
    "## Release Overview",
    "## Release Highlights",
    "## What's Changed",
    "**Full Changelog**:",
    "GitHub-generated release notes",
    "previous release",
    "must not start with or repeat the release title as `# <release title>`",
    "inclusion-only",
    "what was built",
    "what capabilities exist",
    "how the system behaves",
    "defensive wording",
)

PR_LIVE_STATE_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/incident_patterns.md"),
)

PR_LIVE_STATE_PHRASES = (
    "PR package ready",
    "PR Creation Pending",
    "PR Validation Pending",
    "PR State Unknown",
)

POST_MERGE_PR_BLOCKERS = (
    "PR Creation Pending",
    "PR Validation Pending",
    "PR State Unknown",
)

UTS_RESULTS_BLOCKER_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/user_test_summary_guidance.md"),
)

UTS_RESULTS_BLOCKER_PHRASES = (
    "User Test Summary Results Pending",
    "User Test Summary Results:",
    "Live Validation green requires an exact `## User Test Summary` state before final green.",
    "Final phase advancement is BLOCKED",
)

UTS_RESULTS_BLOCKER = "User Test Summary Results Pending"
UTS_RESULT_LABEL = "User Test Summary Results:"
UTS_WAIVER_REASON_LABEL = "User Test Summary Waiver Reason:"
UTS_RESULT_VALUES = ("PENDING", "PASS", "FAIL", "WAIVED")
UTS_CLEAR_RESULT_VALUES = ("PASS", "WAIVED")

USER_FACING_SHORTCUT_GATE_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/user_test_summary_guidance.md"),
)

USER_FACING_SHORTCUT_GATE_PHRASES = (
    "User-Facing Shortcut Live Validation Gate",
    "User-Facing Shortcut Validation:",
    "User-Facing Shortcut Path:",
    "before User Test Summary",
)

USER_FACING_SHORTCUT_BLOCKER = "User-Facing Shortcut Validation Pending"
USER_FACING_SHORTCUT_RESULT_LABEL = "User-Facing Shortcut Validation:"
USER_FACING_SHORTCUT_PATH_LABEL = "User-Facing Shortcut Path:"
USER_FACING_SHORTCUT_WAIVER_REASON_LABEL = "User-Facing Shortcut Waiver Reason:"
USER_FACING_SHORTCUT_RESULT_VALUES = ("PENDING", "PASS", "FAIL", "WAIVED")
USER_FACING_SHORTCUT_CLEAR_VALUES = ("PASS", "WAIVED")

RELEASE_READINESS_TARGET_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

RELEASE_READINESS_TARGET_PHRASES = (
    "Release Target Undefined",
    "Release Target:",
    "Release Floor:",
    "Version Rationale:",
    "Release Scope:",
    "Release Artifacts:",
    "Release Branch: No",
)

RELEASE_READINESS_SCOPE_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
)

RELEASE_READINESS_SCOPE_PHRASES = (
    "Release Readiness is not",
    "docs-sync",
)

RELEASE_READINESS_FILE_FREEZE_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/incident_patterns.md"),
)

RELEASE_READINESS_FILE_FREEZE_PHRASES = (
    "Release Readiness File Mutation Attempt",
    "analysis-only",
    "return to `PR Readiness`",
    "next active branch's `Branch Readiness`",
)

PROTECTED_MAIN_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
    Path("Docs/closeout_guidance.md"),
    Path("Docs/incident_patterns.md"),
)

PROTECTED_MAIN_PHRASES = (
    "main` is protected",
    "Main Write Attempt",
    "no emergency direct-main",
)

MERGED_UNRELEASED_CONTRACT_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/Main.md"),
    Path("Docs/incident_patterns.md"),
)

MERGED_UNRELEASED_CONTRACT_PHRASES = (
    "Merged-Unreleased Release-Debt Owner:",
    "Repo State: No Active Branch",
    "Release Target:",
    "Release Floor:",
    "Version Rationale:",
    "Release Scope:",
    "Release Artifacts:",
    "Post-Release Truth:",
    "Selected Next Workstream:",
    "Next-Branch Creation Gate:",
)

REQUIRED_RELEASE_BEARING_MARKERS = (
    "Release Target:",
    "Release Scope:",
    "Release Artifacts:",
)

REQUIRED_MERGED_UNRELEASED_MARKERS = (
    "Merged-Unreleased Release-Debt Owner:",
    "Repo State: No Active Branch",
    "Release Target:",
    "Release Floor:",
    "Version Rationale:",
    "Release Scope:",
    "Release Artifacts:",
    "Post-Release Truth:",
    "Selected Next Workstream:",
    "Next-Branch Creation Gate:",
)

PATCH_PRERELEASE_FLOOR = "patch prerelease"
MINOR_PRERELEASE_FLOOR = "minor prerelease"
SEMANTIC_RELEASE_FLOORS = (PATCH_PRERELEASE_FLOOR, MINOR_PRERELEASE_FLOOR)
MINOR_RELEASE_CAPABILITY_MARKERS = (
    "executable",
    "runtime capability",
    "operator-facing",
    "user-facing",
    "materially expanded product capability",
    "product behavior expansion",
)
MINOR_RELEASE_CAPABILITY_NEGATION_RE = re.compile(
    r"\b(?:no|not|without|lacks?|lacking|neither|nor|does not|doesn't|did not|didn't|must not|cannot|can't)\b"
    r"[^.;:\n]{0,220}"
    r"\b(?:executable|runtime(?: capability| behavior| implementation)?|operator-facing|user-facing|"
    r"materially expanded product capability|product behavior expansion|capability lane)\b"
    r"[^.;:\n]*"
)
MINOR_RELEASE_CAPABILITY_POSITIVE_PATTERNS = (
    r"\bnew\s+(?:pre-beta\s+)?capability lane\b",
    r"\b(?:adds?|delivers?|creates?|introduces?)\s+[^.;:\n]{0,80}?\bcapability lane\b",
    r"\b(?:new|added|delivered|introduced)\s+[^.;:\n]{0,40}?\bexecutable\b",
    r"\bexecutable\s+(?:capability|product behavior|lane)\b",
    r"\bruntime\s+(?:capability|implementation|behavior|boundary|lane)\b",
    r"\boperator-facing\b[^.;:\n]{0,80}\b(?:capability|surface|behavior|workflow|path|feature|lane)\b",
    r"\buser-facing\b[^.;:\n]{0,80}\b(?:capability|surface|behavior|workflow|path|feature|lane)\b",
    r"\bmaterially expanded product capability\b",
    r"\bproduct behavior expansion\b",
)
PATCH_FLOOR_DEFAULT_MARKERS = (
    "architecture-only",
    "planning",
    "admission contract",
    "validation-only",
    "non-user-facing",
    "documentation/canon repair",
    "governance repair",
)
PREBETA_RELEASE_TITLE_TEMPLATE = "Pre-Beta v<major>.<minor>.<patch>"
FB038_RELEASE_TAG = "v1.4.1-prebeta"
FB038_RELEASE_TITLE = "Pre-Beta v1.4.1"
FB038_CANONICAL_PATH = "Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md"

RELEASE_TITLE_FORMAT_DOCS = (
    Path("Docs/closeout_guidance.md"),
    Path("Docs/incident_patterns.md"),
)

RELEASE_TITLE_FORMAT_PHRASES = (
    PREBETA_RELEASE_TITLE_TEMPLATE,
    "inclusion-only release notes",
)

NON_RELEASE_BRANCH_MARKER = "Release Branch: No"
RELEASE_BEARING_BRANCH_CLASSES = ("release packaging",)
NON_RELEASE_WAIVER_BRANCH_CLASSES = (
    "docs/governance",
    "emergency canon repair",
)

EMERGENCY_CANON_REPAIR_BRANCH_CLASS = "emergency canon repair"
REPAIR_ONLY_BRANCH_HANDLING_LABEL = "Repair-Only Branch Handling"

BRANCH_RECORD_INDEX = Path("Docs/branch_records/index.md")

NEXT_WORKSTREAM_SELECTION_MARKER = "Next Workstream: Selected"
NEXT_WORKSTREAM_MINIMAL_SCOPE_LABEL = "Minimal Scope:"
NEXT_WORKSTREAM_BRANCH_NOT_CREATED_PHRASES = (
    "Branch: Not created",
    "Branch: Deferred to Branch Readiness",
    "No branch created",
    "not branched",
)

VALID_NEXT_WORKSTREAM_RECORD_STATES = (
    "Registry-only",
    "Promoted",
)

DEFERRED_BACKLOG_CONTEXT_LABELS = (
    "Deferred Since",
    "Deferred Because",
    "Selection / Unblock",
)

REQUIRED_BRANCH_RECORD_HEADINGS = (
    "## Current Phase",
    "## Phase Status",
    "## Branch Class",
    "## Blockers",
    "## Entry Basis",
    "## Exit Criteria",
    "## Rollback Target",
    "## Next Legal Phase",
)


def _read_text(relative_path: Path) -> str:
    return (ROOT_DIR / relative_path).read_text(encoding="utf-8")


def _line_number(text: str, needle: str) -> int:
    index = text.find(needle)
    if index < 0:
        return 0
    return text.count("\n", 0, index) + 1


def _section(text: str, heading: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text)
    return match.group(1).strip() if match else ""


def _subsection(text: str, heading_prefix: str) -> str:
    match = re.search(rf"(?ms)^### {re.escape(heading_prefix)}.*?\n(.*?)(?=^### |\Z)", text)
    return match.group(0).strip() if match else ""


def _extract_backtick_values(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", text)


def _extract_first_backtick_value(text: str) -> str:
    values = _extract_backtick_values(text)
    return values[0] if values else ""


def _normalize_status(value: str) -> str:
    lowered = value.strip().lower()
    if "merged unreleased" in lowered:
        return "merged unreleased"
    if "released" in lowered:
        return "released"
    if "closed" in lowered:
        return "closed"
    if "active" in lowered:
        return "active"
    if "deferred" in lowered:
        return "deferred"
    return lowered


def _parse_backlog_sections(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    matches = list(re.finditer(r"^### \[ID: (?P<id>FB-\d+)\] (?P<title>.+)$", text, flags=re.M))
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        entries.append(
            {
                "id": match.group("id"),
                "title": match.group("title").strip(),
                "block": block,
                "status": _extract_colon_value(block, "Status"),
                "record_state": _extract_colon_value(block, "Record State"),
                "canonical_path": _extract_colon_value(block, "Canonical Workstream Doc"),
            }
        )
    return entries


def _is_open_backlog_candidate(entry: dict[str, str]) -> bool:
    status = entry["status"].strip().casefold()
    normalized_status = _normalize_status(entry["status"])
    return (
        entry["record_state"] != "Closed"
        and normalized_status not in {"released", "closed", "merged unreleased"}
        and not status.startswith("implemented")
    )


def _extract_colon_value(block: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", block, flags=re.M)
    return match.group(1).strip() if match else ""


def _clean_release_value(value: str) -> str:
    return value.strip().strip("`").strip()


def _latest_public_prerelease(roadmap_text: str) -> str:
    return _clean_release_value(_extract_colon_value(roadmap_text, "- latest public prerelease"))


def _parse_prebeta_version(value: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)-prebeta", _clean_release_value(value))
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _expected_prerelease_target(latest_public: str, release_floor: str) -> str:
    parsed = _parse_prebeta_version(latest_public)
    if parsed is None:
        return ""

    major, minor, patch = parsed
    normalized_floor = _clean_release_value(release_floor).casefold()
    if normalized_floor == PATCH_PRERELEASE_FLOOR:
        return f"v{major}.{minor}.{patch + 1}-prebeta"
    if normalized_floor == MINOR_PRERELEASE_FLOOR:
        return f"v{major}.{minor + 1}.0-prebeta"
    return ""


def _expected_prebeta_release_title(release_tag: str) -> str:
    parsed = _parse_prebeta_version(release_tag)
    if parsed is None:
        return ""
    major, minor, patch = parsed
    return f"Pre-Beta v{major}.{minor}.{patch}"


def _entry_by_id(entries: list[dict[str, str]], workstream_id: str) -> dict[str, str] | None:
    for entry in entries:
        if entry.get("id") == workstream_id:
            return entry
    return None


def _git_prebeta_tags() -> list[str]:
    completed = subprocess.run(
        ("git", "tag", "--list", "v*-prebeta"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [
        line.strip()
        for line in completed.stdout.splitlines()
        if _parse_prebeta_version(line.strip()) is not None
    ]


def _git_remote_prebeta_tags() -> list[str]:
    completed = subprocess.run(
        ("git", "ls-remote", "--tags", "origin", "refs/tags/v*-prebeta"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return []

    tags: list[str] = []
    for line in completed.stdout.splitlines():
        match = re.search(r"refs/tags/(v\d+\.\d+\.\d+-prebeta)(?:\^\{\})?$", line.strip())
        if match and _parse_prebeta_version(match.group(1)) is not None:
            tags.append(match.group(1))
    return tags


def _highest_known_prebeta_tag() -> str:
    tags = sorted(set(_git_prebeta_tags()) | set(_git_remote_prebeta_tags()))
    if not tags:
        return ""
    return max(tags, key=lambda tag: _parse_prebeta_version(tag) or (0, 0, 0))


def _workstream_target_version(workstream_text: str) -> str:
    return _clean_release_value(_extract_first_backtick_value(_section(workstream_text, "Target Version")))


def _minor_release_rationale_has_capability(rationale_text: str) -> bool:
    lowered = rationale_text.casefold()
    rationale_without_negated_capabilities = MINOR_RELEASE_CAPABILITY_NEGATION_RE.sub(
        " ",
        lowered.replace("non-user-facing", " "),
    )
    return any(
        re.search(pattern, rationale_without_negated_capabilities)
        for pattern in MINOR_RELEASE_CAPABILITY_POSITIVE_PATTERNS
    )


def _release_debt_owner_claim(workstream_id: str) -> str:
    return f"merged-unreleased release-debt owner: {workstream_id.casefold()}"


def _parse_workstream_doc(text: str) -> dict[str, object]:
    record_state = _extract_first_backtick_value(_section(text, "Record State"))
    status = _extract_first_backtick_value(_section(text, "Status"))
    canonical_branch = _extract_first_backtick_value(_section(text, "Canonical Branch"))
    current_phase_section = _section(text, "Current Phase")
    current_phase_match = re.search(r"Phase:\s*`([^`]+)`", current_phase_section)
    current_phase = current_phase_match.group(1) if current_phase_match else ""
    branch_class = _extract_first_backtick_value(_section(text, "Branch Class"))
    blockers = _extract_backtick_values(_section(text, "Blockers"))
    rollback_target = _extract_first_backtick_value(_section(text, "Rollback Target"))
    next_legal_phase = _extract_first_backtick_value(_section(text, "Next Legal Phase"))
    governance_audit = _section(text, "Governance Drift Audit")
    return {
        "record_state": record_state,
        "status": status,
        "canonical_branch": canonical_branch,
        "current_phase": current_phase,
        "branch_class": branch_class,
        "blockers": blockers,
        "rollback_target": rollback_target,
        "next_legal_phase": next_legal_phase,
        "governance_audit": governance_audit,
    }


def _extract_branch_identity_branch(text: str) -> str:
    match = re.search(r"^\s*-\s*Branch:\s*`([^`]+)`\s*$", text, flags=re.M)
    return match.group(1).strip() if match else ""


def _count_field_occurrences(block: str, label: str) -> int:
    return len(re.findall(rf"^{re.escape(label)}:\s*.+$", block, flags=re.M))


def _branch_record_branch_sets(
    active_branch_record_paths: set[str],
    historical_branch_record_paths: set[str],
    current_branch: str,
) -> tuple[dict[str, str], set[str], set[str]]:
    branch_class_map: dict[str, str] = {}
    all_repair_branch_names: set[str] = set()
    active_repair_branch_names: set[str] = set()
    for branch_record_path in active_branch_record_paths | historical_branch_record_paths:
        record_path = ROOT_DIR / Path(branch_record_path)
        if not record_path.is_file():
            continue
        record_text = _read_text(Path(branch_record_path))
        branch_name = _extract_branch_identity_branch(record_text)
        branch_class = str(_parse_workstream_doc(record_text)["branch_class"])
        if not branch_name or not branch_class:
            continue
        prefixed_branch_name = f"origin/{branch_name}"
        if branch_class == EMERGENCY_CANON_REPAIR_BRANCH_CLASS:
            all_repair_branch_names.add(branch_name)
            all_repair_branch_names.add(prefixed_branch_name)
            if branch_record_path in active_branch_record_paths:
                active_repair_branch_names.add(branch_name)
                active_repair_branch_names.add(prefixed_branch_name)
        branch_class_map[branch_name] = branch_class
        branch_class_map[prefixed_branch_name] = branch_class
    return branch_class_map, all_repair_branch_names, active_repair_branch_names


def _user_test_summary_section(text: str) -> str:
    return _section(text, "User Test Summary")


def _extract_marker_value(block: str, label: str) -> str:
    matches = re.findall(
        rf"^\s*(?:-\s*)?{re.escape(label)}:?\s*`?(.+?)`?\s*$",
        block,
        flags=re.M,
    )
    if not matches:
        return ""
    return matches[-1].strip().strip("`").strip()


def _parse_delta_classes(value: str) -> set[str]:
    return {part.strip().casefold() for part in value.split(",") if part.strip()}


def _validate_planning_loop_guardrail(
    require,
    source_path: str,
    text: str,
    *,
    branch_class: str,
    current_phase: str,
    normalized_status: str,
) -> None:
    if branch_class != "implementation":
        return
    if current_phase not in PLANNING_LOOP_ACTIVE_PHASES and normalized_status != "merged unreleased":
        return

    require(
        "## Planning-Loop Guardrail" in text,
        f"{source_path}: implementation lane is missing '## Planning-Loop Guardrail'",
    )
    guardrail_section = _section(text, "Planning-Loop Guardrail")
    delta_value = _extract_marker_value(guardrail_section, PLANNING_LOOP_DELTA_CLASS_LABEL)
    docs_only_value = _extract_marker_value(guardrail_section, PLANNING_LOOP_DOCS_ONLY_LABEL)
    bypass_approval = _extract_marker_value(guardrail_section, PLANNING_LOOP_BYPASS_APPROVAL_LABEL)
    bypass_reason = _extract_marker_value(guardrail_section, PLANNING_LOOP_BYPASS_REASON_LABEL)
    delta_classes = _parse_delta_classes(delta_value)
    normalized_docs_only = docs_only_value.strip().casefold()
    normalized_bypass = bypass_approval.strip().upper()
    normalized_reason = bypass_reason.strip().casefold()
    has_real_delta = bool(delta_classes & REAL_IMPLEMENTATION_DELTA_CLASSES)

    require(
        bool(delta_value),
        f"{source_path}: Planning-Loop Guardrail is missing '{PLANNING_LOOP_DELTA_CLASS_LABEL}:'",
    )
    require(
        bool(docs_only_value),
        f"{source_path}: Planning-Loop Guardrail is missing '{PLANNING_LOOP_DOCS_ONLY_LABEL}:'",
    )
    require(
        bool(bypass_approval),
        f"{source_path}: Planning-Loop Guardrail is missing '{PLANNING_LOOP_BYPASS_APPROVAL_LABEL}:'",
    )
    require(
        bool(bypass_reason),
        f"{source_path}: Planning-Loop Guardrail is missing '{PLANNING_LOOP_BYPASS_REASON_LABEL}:'",
    )

    if not delta_classes:
        require(
            False,
            f"{source_path}: Planning-Loop Guardrail must declare at least one implementation delta class",
        )
        return

    invalid_delta_classes = sorted(delta_classes - ALLOWED_IMPLEMENTATION_DELTA_CLASSES)
    require(
        not invalid_delta_classes,
        (
            f"{source_path}: {PLANNING_LOOP_DELTA_CLASS_LABEL} contains unsupported value(s): "
            f"{', '.join(invalid_delta_classes)}"
        ),
    )
    require(
        not (
            PLANNING_LOOP_DOCS_ONLY_DELTA in delta_classes
            and len(delta_classes) > 1
        ),
        (
            f"{source_path}: {PLANNING_LOOP_DELTA_CLASS_LABEL} must not mix "
            f"'{PLANNING_LOOP_DOCS_ONLY_DELTA}' with runtime-bearing delta classes"
        ),
    )
    require(
        normalized_docs_only in {"yes", "no"},
        f"{source_path}: {PLANNING_LOOP_DOCS_ONLY_LABEL} must be Yes or No",
    )

    if has_real_delta:
        admitted_slice = _section(text, "Admitted Implementation Slice")
        require(
            "## Admitted Implementation Slice" in text and bool(admitted_slice),
            f"{source_path}: implementation lane is missing '## Admitted Implementation Slice'",
        )
        require(
            normalized_docs_only == "no",
            (
                f"{source_path}: runtime-bearing implementation delta requires "
                f"'{PLANNING_LOOP_DOCS_ONLY_LABEL}: No'"
            ),
        )
        require(
            normalized_bypass in {"", "NONE", "NO"},
            (
                f"{source_path}: runtime-bearing implementation delta must not carry "
                "a planning-loop bypass approval"
            ),
        )
        require(
            normalized_reason in {"", "none", "n/a", "na"},
            (
                f"{source_path}: runtime-bearing implementation delta must not carry "
                "a planning-loop bypass reason"
            ),
        )
    else:
        require(
            normalized_docs_only == "yes",
            (
                f"{source_path}: docs-only implementation lane requires "
                f"'{PLANNING_LOOP_DOCS_ONLY_LABEL}: Yes'"
            ),
        )
        require(
            normalized_bypass == "APPROVED",
            (
                f"{source_path}: docs-only implementation lane is blocked by "
                "'Planning-Loop Guardrail' until explicit USER approval is recorded"
            ),
        )
        require(
            normalized_reason not in {"", "none", "n/a", "na"},
            (
                f"{source_path}: docs-only implementation lane requires an explicit "
                f"'{PLANNING_LOOP_BYPASS_REASON_LABEL}:'"
            ),
        )

    if normalized_status == "merged unreleased":
        require(
            has_real_delta or normalized_bypass == "APPROVED",
            (
                f"{source_path}: release-bearing implementation work with no real runtime, "
                "backend/runtime, or developer-tooling delta requires explicit USER approval"
            ),
        )


def _validate_release_window_audit(require, source_path: str, text: str) -> None:
    audit_section = _section(text, "Release Window Audit")
    require(
        bool(audit_section),
        f"{source_path}: PR Readiness requires a Release Window Audit section",
    )
    if not audit_section:
        return

    audit_state = _extract_marker_value(audit_section, "Release Window Audit")
    remaining_blockers = _extract_marker_value(audit_section, "Remaining Known Release Blockers")
    another_repair_pr = _extract_marker_value(
        audit_section, "Another Pre-Release Repair PR Required"
    )
    split_waiver = _extract_marker_value(audit_section, "Release Window Split Waiver")
    split_waiver_reason = _extract_marker_value(
        audit_section, "Release Window Split Waiver Reason"
    )

    require(
        audit_state.upper() == "PASS",
        f"{source_path}: Release Window Audit must report PASS before PR green",
    )
    require(
        bool(remaining_blockers),
        f"{source_path}: Release Window Audit is missing 'Remaining Known Release Blockers'",
    )
    require(
        bool(another_repair_pr),
        (
            f"{source_path}: Release Window Audit is missing "
            "'Another Pre-Release Repair PR Required'"
        ),
    )
    require(
        bool(split_waiver),
        f"{source_path}: Release Window Audit is missing 'Release Window Split Waiver'",
    )

    normalized_remaining = remaining_blockers.casefold()
    normalized_another = another_repair_pr.strip().upper()
    normalized_waiver = split_waiver.strip().upper()

    if normalized_waiver in {"", "NONE", "NO"}:
        require(
            normalized_remaining == "none",
            (
                f"{source_path}: without a Release Window Split Waiver, "
                "Remaining Known Release Blockers must be None"
            ),
        )
        require(
            normalized_another == "NO",
            (
                f"{source_path}: without a Release Window Split Waiver, "
                "Another Pre-Release Repair PR Required must be NO"
            ),
        )
    else:
        require(
            normalized_waiver == "APPROVED",
            (
                f"{source_path}: Release Window Split Waiver must be None or APPROVED; "
                f"found '{split_waiver}'"
            ),
        )
        require(
            normalized_another == "YES",
            (
                f"{source_path}: Release Window Split Waiver APPROVED requires "
                "Another Pre-Release Repair PR Required: YES"
            ),
        )
        require(
            bool(split_waiver_reason),
            (
                f"{source_path}: Release Window Split Waiver APPROVED requires "
                "'Release Window Split Waiver Reason'"
            ),
        )


def _parse_uts_result_state(text: str) -> str:
    section = _user_test_summary_section(text)
    matches = re.findall(rf"{re.escape(UTS_RESULT_LABEL)}\s*`?([A-Za-z]+)`?", section)
    if not matches:
        return ""
    return matches[-1].strip().upper()


def _parse_uts_waiver_reason(text: str) -> str:
    return _extract_marker_value(_user_test_summary_section(text), UTS_WAIVER_REASON_LABEL)


def _parse_user_facing_shortcut_state(text: str) -> str:
    section = _user_test_summary_section(text)
    matches = re.findall(
        rf"{re.escape(USER_FACING_SHORTCUT_RESULT_LABEL)}\s*`?([A-Za-z]+)`?",
        section,
    )
    if not matches:
        return ""
    return matches[-1].strip().upper()


def _parse_user_facing_shortcut_path(text: str) -> str:
    return _extract_marker_value(_user_test_summary_section(text), USER_FACING_SHORTCUT_PATH_LABEL)


def _parse_user_facing_shortcut_waiver_reason(text: str) -> str:
    return _extract_marker_value(
        _user_test_summary_section(text),
        USER_FACING_SHORTCUT_WAIVER_REASON_LABEL,
    )


def _has_user_test_summary(text: str) -> bool:
    return bool(_user_test_summary_section(text))


def _requires_user_facing_shortcut_gate(text: str) -> bool:
    section = _user_test_summary_section(text)
    if not section:
        return False
    if USER_FACING_SHORTCUT_RESULT_LABEL in section or USER_FACING_SHORTCUT_PATH_LABEL in section:
        return True
    section_lower = section.casefold()
    desktop_surface_markers = (
        "desktop",
        "tray",
        "taskbar",
        "shortcut",
        "launcher",
        "user-facing",
    )
    return any(marker in section_lower for marker in desktop_surface_markers)


def _collect_active_index_paths(text: str) -> set[str]:
    active_section = _subsection(text, "Active")
    return set(re.findall(r"Docs/workstreams/[A-Za-z0-9._-]+\.md", active_section))


def _collect_closed_index_paths(text: str) -> set[str]:
    closed_section = _subsection(text, "Closed")
    return set(re.findall(r"Docs/workstreams/[A-Za-z0-9._-]+\.md", closed_section))


def _collect_release_debt_index_paths(text: str) -> set[str]:
    release_debt_section = _subsection(text, "Merged / Release Debt Owners")
    return set(re.findall(r"Docs/workstreams/[A-Za-z0-9._-]+\.md", release_debt_section))


def _collect_branch_record_paths(text: str, heading_prefix: str) -> set[str]:
    section = _section(text, heading_prefix)
    return set(re.findall(r"Docs/branch_records/[A-Za-z0-9._-]+\.md", section))


def _roadmap_section_for_id(text: str, workstream_id: str) -> str:
    match = re.search(rf"(?ms)^### {re.escape(workstream_id)}.*?(?=^### |\Z)", text)
    return match.group(0).strip() if match else ""


def _phase_index(phase_name: str) -> int:
    return PHASES.index(phase_name)


def _git_status_porcelain(*, tracked_only: bool = False) -> str:
    command = ["git", "status", "--porcelain"]
    if tracked_only:
        command.append("--untracked-files=no")
    completed = subprocess.run(
        command,
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return f"__GIT_STATUS_ERROR__ {completed.stderr.strip()}"
    return completed.stdout.strip()


def _git_current_branch() -> str:
    completed = subprocess.run(
        ("git", "branch", "--show-current"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _git_branch_names() -> tuple[list[str], str]:
    names: list[str] = []
    errors: list[str] = []
    for args in (
        ("git", "branch", "--format=%(refname:short)"),
        ("git", "branch", "-r", "--format=%(refname:short)"),
    ):
        completed = subprocess.run(
            args,
            cwd=ROOT_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            errors.append(completed.stderr.strip())
            continue
        names.extend(line.strip() for line in completed.stdout.splitlines() if line.strip())
    return sorted(set(names)), "; ".join(error for error in errors if error)


def _gh_pr_view_for_branch(branch_name: str) -> tuple[dict[str, object] | None, str]:
    fields = (
        "id,number,state,mergeable,mergeStateStatus,reviewDecision,isDraft,"
        "headRefName,baseRefName,title,url"
    )
    completed = subprocess.run(
        ("gh", "pr", "view", branch_name, "--json", fields),
        cwd=ROOT_DIR,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return None, completed.stderr.strip() or completed.stdout.strip() or "gh pr view failed"
    try:
        return json.loads(completed.stdout), ""
    except json.JSONDecodeError as exc:
        return None, f"could not parse gh pr view JSON: {exc}"


def _gh_unresolved_codex_threads(pr_node_id: str) -> tuple[list[str], str]:
    if not pr_node_id:
        return [], "PR node id is missing"

    query = """
query($id: ID!) {
  node(id: $id) {
    ... on PullRequest {
      reviewThreads(first: 100) {
        nodes {
          isResolved
          comments(first: 20) {
            nodes {
              author { login }
              body
            }
          }
        }
      }
    }
  }
}
"""
    completed = subprocess.run(
        ("gh", "api", "graphql", "-f", f"query={query}", "-F", f"id={pr_node_id}"),
        cwd=ROOT_DIR,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return [], completed.stderr.strip() or completed.stdout.strip() or "gh api graphql failed"

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return [], f"could not parse gh review-thread JSON: {exc}"

    nodes = (((payload.get("data") or {}).get("node") or {}).get("reviewThreads") or {}).get("nodes") or []
    unresolved: list[str] = []
    for thread in nodes:
        if thread.get("isResolved"):
            continue
        comments = ((thread.get("comments") or {}).get("nodes")) or []
        for comment in comments:
            author = ((comment.get("author") or {}).get("login") or "").casefold()
            body = (comment.get("body") or "").casefold()
            if "codex" in author or "openai" in author or "codex" in body:
                unresolved.append(author or "unknown-author")
                break
    return unresolved, ""


def _selected_next_workstream_entries(backlog_entries: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        entry
        for entry in backlog_entries
        if re.search(rf"^{re.escape(NEXT_WORKSTREAM_SELECTION_MARKER)}\s*$", entry["block"], flags=re.M)
    ]


def _next_workstream_roadmap_section(roadmap_text: str) -> str:
    return _section(roadmap_text, "Selected Next Workstream")


def _selected_next_ignored_branch_names(
    current_branch: str,
    all_repair_branch_names: set[str],
    active_repair_branch_names: set[str],
) -> set[str]:
    if current_branch == "main" or current_branch in active_repair_branch_names:
        return set(all_repair_branch_names)
    return set()


def _selected_next_repair_only_branch_handling(blocks: list[str]) -> bool:
    for block in blocks:
        marker = _extract_marker_value(block, REPAIR_ONLY_BRANCH_HANDLING_LABEL)
        marker_lower = marker.casefold()
        if (
            marker
            and "repair-only" in marker_lower
            and "does not imply branch readiness admission" in marker_lower
            and "active branch truth" in marker_lower
        ):
            return True
    return False


def _branch_names_for_workstream(
    branch_names: list[str],
    workstream_id: str,
    ignored_branch_names: set[str] | None = None,
) -> list[str]:
    canonical = workstream_id.casefold()
    compact = canonical.replace("-", "")
    matching = [
        branch_name
        for branch_name in branch_names
        if canonical in branch_name.casefold() or compact in branch_name.casefold().replace("-", "")
    ]
    if not ignored_branch_names:
        return matching
    return [
        branch_name
        for branch_name in matching
        if branch_name not in ignored_branch_names
    ]


def _root_dev_helper_paths() -> list[str]:
    helper_dir = ROOT_DIR / "dev"
    if not helper_dir.is_dir():
        return []
    return sorted(
        path.relative_to(ROOT_DIR).as_posix()
        for path in helper_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".py", ".ps1"}
        and path.name.startswith("orin_")
    )


def _registry_line_for_path(registry_text: str, helper_path: str) -> str:
    needle = f"`{helper_path}`"
    for line in registry_text.splitlines():
        if needle in line:
            return line
    return ""


def _run_uts_results_pr_gate(require, backlog_entries: list[dict[str, str]]) -> None:
    for entry in backlog_entries:
        if entry.get("record_state") != "Promoted":
            continue

        canonical_path = entry.get("canonical_path", "")
        if not canonical_path:
            continue

        workstream_path = Path(canonical_path)
        if not (ROOT_DIR / workstream_path).is_file():
            continue

        workstream_text = _read_text(workstream_path)

        workstream_info = _parse_workstream_doc(workstream_text)
        current_phase = str(workstream_info["current_phase"])
        if current_phase not in {"Live Validation", "PR Readiness"}:
            continue

        require(
            _has_user_test_summary(workstream_text),
            (
                "PR readiness gate: User Test Summary Results Pending blocker is active; "
                f"{canonical_path} must include an exact '## User Test Summary' section before PR READY: YES"
            ),
        )

        uts_result = _parse_uts_result_state(workstream_text)
        blockers = list(workstream_info["blockers"])
        if _requires_user_facing_shortcut_gate(workstream_text):
            shortcut_result = _parse_user_facing_shortcut_state(workstream_text)
            require(
                bool(shortcut_result),
                (
                    "PR readiness gate: User-Facing Shortcut Validation Pending blocker is active; "
                    f"{canonical_path} must declare '{USER_FACING_SHORTCUT_RESULT_LABEL}' before PR READY: YES"
                ),
            )
            if shortcut_result:
                require(
                    shortcut_result in USER_FACING_SHORTCUT_CLEAR_VALUES
                    and USER_FACING_SHORTCUT_BLOCKER not in blockers,
                    (
                        "PR readiness gate: User-Facing Shortcut Validation gate is not clear; "
                        f"{canonical_path} reports {USER_FACING_SHORTCUT_RESULT_LABEL} {shortcut_result}; "
                        "the declared user-facing shortcut or equivalent entrypoint must pass or be waived "
                        "before PR READY: YES"
                    ),
                )
                if shortcut_result == "WAIVED":
                    require(
                        bool(_parse_user_facing_shortcut_waiver_reason(workstream_text)),
                        (
                            "PR readiness gate: User-Facing Shortcut Validation waiver is incomplete; "
                            f"{canonical_path} must declare '{USER_FACING_SHORTCUT_WAIVER_REASON_LABEL}'"
                        ),
                    )

        require(
            bool(uts_result),
            (
                "PR readiness gate: User Test Summary Results Pending blocker is active; "
                f"{canonical_path} must declare '{UTS_RESULT_LABEL}' before PR READY: YES"
            ),
        )
        if not uts_result:
            continue

        require(
            uts_result in UTS_CLEAR_RESULT_VALUES and UTS_RESULTS_BLOCKER not in blockers,
            (
                "PR readiness gate: User Test Summary Results Pending blocker is active; "
                f"{canonical_path} reports {UTS_RESULT_LABEL} {uts_result}; returned results "
                "must be submitted or waived, digested, and reevaluated before PR READY: YES"
            ),
        )
        if uts_result == "WAIVED":
            require(
                bool(_parse_uts_waiver_reason(workstream_text)),
                (
                    "PR readiness gate: User Test Summary waiver is incomplete; "
                    f"{canonical_path} must declare '{UTS_WAIVER_REASON_LABEL}'"
                ),
            )


def _run_next_workstream_gate(
    require,
    backlog_entries: list[dict[str, str]],
    roadmap_text: str,
    ignored_branch_names: set[str],
    branch_record_class_map: dict[str, str],
) -> None:
    selected_entries = _selected_next_workstream_entries(backlog_entries)
    require(
        len(selected_entries) == 1,
        (
            "PR readiness gate: Next Workstream Undefined blocker is active; exactly one backlog "
            f"entry must declare '{NEXT_WORKSTREAM_SELECTION_MARKER}' before PR READY: YES"
        ),
    )
    if len(selected_entries) != 1:
        return

    selected = selected_entries[0]
    selected_id = selected["id"]
    selected_record_state = selected["record_state"]
    selected_block = selected["block"]
    selected_scope = _extract_colon_value(selected_block, "Minimal Scope")
    roadmap_section = _next_workstream_roadmap_section(roadmap_text)
    repair_only_handling = _selected_next_repair_only_branch_handling(
        [selected_block, roadmap_section]
    )

    require(
        selected_record_state in VALID_NEXT_WORKSTREAM_RECORD_STATES,
        (
            "PR readiness gate: Next Workstream Undefined blocker is active; "
            f"{selected_id} has invalid Record State '{selected_record_state}'"
        ),
    )
    require(
        bool(selected_scope),
        (
            "PR readiness gate: Next Workstream Undefined blocker is active; "
            f"{selected_id} must define '{NEXT_WORKSTREAM_MINIMAL_SCOPE_LABEL}' in Docs/feature_backlog.md"
        ),
    )
    require(
        bool(roadmap_section),
        (
            "PR readiness gate: Next Workstream Undefined blocker is active; "
            "Docs/prebeta_roadmap.md must contain a 'Selected Next Workstream' section"
        ),
    )
    if roadmap_section:
        require(
            selected_id in roadmap_section,
            (
                "PR readiness gate: Next Workstream Undefined blocker is active; "
                f"Docs/prebeta_roadmap.md selected-next section does not name {selected_id}"
            ),
        )
        require(
            selected_record_state in roadmap_section,
            (
                "PR readiness gate: Next Workstream Undefined blocker is active; "
                f"Docs/prebeta_roadmap.md selected-next section does not record {selected_id} Record State"
            ),
        )
        require(
            NEXT_WORKSTREAM_MINIMAL_SCOPE_LABEL.casefold() in roadmap_section.casefold(),
            (
                "PR readiness gate: Next Workstream Undefined blocker is active; "
                "Docs/prebeta_roadmap.md selected-next section must define Minimal Scope"
            ),
        )
        if not repair_only_handling:
            require(
                any(phrase.casefold() in roadmap_section.casefold() for phrase in NEXT_WORKSTREAM_BRANCH_NOT_CREATED_PHRASES),
                (
                    "PR readiness gate: Successor Lock Missing blocker is active; "
                    "Docs/prebeta_roadmap.md must record that no branch exists yet for the selected next workstream"
                ),
            )

    branch_names, branch_error = _git_branch_names()
    require(
        not branch_error,
        f"PR readiness gate: could not inspect branch names for selected next workstream: {branch_error}",
    )
    matching_branches = _branch_names_for_workstream(branch_names, selected_id, ignored_branch_names)
    non_repair_matching_branches = [
        branch_name
        for branch_name in matching_branches
        if branch_record_class_map.get(branch_name) != EMERGENCY_CANON_REPAIR_BRANCH_CLASS
    ]
    if repair_only_handling and not non_repair_matching_branches:
        matching_branches = []
    else:
        if not non_repair_matching_branches and any(
            branch_record_class_map.get(branch_name) == EMERGENCY_CANON_REPAIR_BRANCH_CLASS
            for branch_name in matching_branches
        ):
            require(
                repair_only_handling,
                (
                    "PR readiness gate: Successor Lock Missing blocker is active; "
                    f"{selected_id} only has repair-only branch(es): {', '.join(matching_branches)}, "
                    "but roadmap/backlog do not explicitly declare that repair-only branch existence "
                    "does not imply Branch Readiness admission or active branch truth"
                ),
            )
        matching_branches = non_repair_matching_branches or matching_branches
    require(
        not matching_branches,
        (
            "PR readiness gate: Successor Lock Missing blocker is active; "
            f"{selected_id} already has branch(es): {', '.join(matching_branches)}"
        ),
        )


def _run_open_backlog_selection_governance(require, backlog_entries: list[dict[str, str]]) -> None:
    for entry in backlog_entries:
        if not _is_open_backlog_candidate(entry):
            continue

        workstream_id = entry["id"]
        block = entry["block"]
        require(
            bool(_extract_colon_value(block, "Priority")),
            f"Docs/feature_backlog.md: {workstream_id} open backlog candidate must define Priority",
        )
        require(
            not bool(_extract_colon_value(block, "Target Version")),
            (
                f"Docs/feature_backlog.md: {workstream_id} open backlog candidate must not carry "
                "Target Version; use Priority and deferred-context fields for backlog selection"
            ),
        )

        if _normalize_status(entry["status"]) == "deferred":
            for label in DEFERRED_BACKLOG_CONTEXT_LABELS:
                require(
                    bool(_extract_colon_value(block, label)),
                    (
                        f"Docs/feature_backlog.md: {workstream_id} deferred backlog candidate "
                        f"must define {label}:"
                    ),
                )


def _run_pr_live_state_gate(require) -> None:
    branch_name = _git_current_branch()
    require(
        bool(branch_name),
        "PR readiness gate: PR State Unknown blocker is active; current branch could not be determined",
    )
    if not branch_name:
        return

    pr_info, pr_error = _gh_pr_view_for_branch(branch_name)
    require(
        bool(pr_info),
        (
            "PR readiness gate: PR Creation Pending / PR State Unknown blocker is active; "
            f"could not inspect a GitHub PR for branch '{branch_name}': {pr_error}"
        ),
    )
    if not pr_info:
        return

    pr_url = str(pr_info.get("url") or "")
    pr_state = str(pr_info.get("state") or "")
    pr_head = str(pr_info.get("headRefName") or "")
    pr_base = str(pr_info.get("baseRefName") or "")
    mergeable = str(pr_info.get("mergeable") or "")
    merge_state = str(pr_info.get("mergeStateStatus") or "")
    review_decision = str(pr_info.get("reviewDecision") or "")

    require(
        pr_state == "OPEN",
        f"PR readiness gate: PR Validation Pending blocker is active; PR {pr_url or pr_info.get('number')} state is '{pr_state}'",
    )
    require(
        not bool(pr_info.get("isDraft")),
        f"PR readiness gate: PR Validation Pending blocker is active; PR {pr_url or pr_info.get('number')} is still draft",
    )
    require(
        pr_head == branch_name,
        (
            "PR readiness gate: PR Validation Pending blocker is active; "
            f"PR head '{pr_head}' does not match current branch '{branch_name}'"
        ),
    )
    require(
        pr_base == "main",
        (
            "PR readiness gate: PR Validation Pending blocker is active; "
            f"PR base '{pr_base}' does not match merge-target canon 'main'"
        ),
    )
    require(
        mergeable == "MERGEABLE",
        (
            "PR readiness gate: PR Validation Pending blocker is active; "
            f"PR mergeability is '{mergeable or 'UNKNOWN'}'"
        ),
    )
    require(
        merge_state not in {"BLOCKED", "DIRTY", "UNKNOWN", "DRAFT"},
        (
            "PR readiness gate: PR Validation Pending blocker is active; "
            f"PR merge state is '{merge_state or 'UNKNOWN'}'"
        ),
    )
    require(
        review_decision not in {"CHANGES_REQUESTED", "REVIEW_REQUIRED"},
        (
            "PR readiness gate: PR Validation Pending blocker is active; "
            f"PR review decision is '{review_decision or 'UNKNOWN'}'"
        ),
    )

    unresolved_codex_threads, thread_error = _gh_unresolved_codex_threads(str(pr_info.get("id") or ""))
    require(
        not thread_error,
        (
            "PR readiness gate: PR State Unknown blocker is active; "
            f"could not inspect Codex review threads for PR {pr_url or pr_info.get('number')}: {thread_error}"
        ),
    )
    require(
        not unresolved_codex_threads,
        (
            "PR readiness gate: PR Validation Pending blocker is active; "
            "unresolved Codex comments/issues remain on the PR"
        ),
    )


def _run_pr_readiness_gate(
    require,
    backlog_entries: list[dict[str, str]],
    roadmap_text: str,
    ignored_branch_names: set[str],
    branch_record_class_map: dict[str, str],
) -> None:
    status_output = _git_status_porcelain()
    require(
        not status_output,
        (
            "PR readiness gate: Dirty Branch blocker is active; worktree must be clean "
            "and required branch truth must be durable in commit history before PR READY: YES"
        ),
    )
    _run_uts_results_pr_gate(require, backlog_entries)
    _run_next_workstream_gate(
        require,
        backlog_entries,
        roadmap_text,
        ignored_branch_names,
        branch_record_class_map,
    )
    _run_pr_live_state_gate(require)


def main() -> int:
    pr_readiness_gate = "--pr-readiness-gate" in sys.argv[1:]
    errors: list[str] = []
    checks = 0

    backlog_text = _read_text(Path("Docs/feature_backlog.md"))
    roadmap_text = _read_text(Path("Docs/prebeta_roadmap.md"))
    index_text = _read_text(Path("Docs/workstreams/index.md"))
    branch_record_index_text = _read_text(BRANCH_RECORD_INDEX)
    main_text = _read_text(Path("Docs/Main.md"))
    main_canonical_workstream_routes = _subsection(main_text, "Canonical Workstream Records")

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    for relative_path in PROMPT_CONTRACT_DOCS:
        text = _read_text(relative_path)
        for old_term in OLD_PHASE_TERMS:
            require(
                old_term not in text,
                f"{relative_path}: deprecated phase term '{old_term}' is still present (line {_line_number(text, old_term)})",
            )
        for bad_spelling in BANNED_BRANCH_CLASS_SPELLINGS:
            require(
                bad_spelling not in text,
                f"{relative_path}: deprecated branch-class spelling '{bad_spelling}' is still present (line {_line_number(text, bad_spelling)})",
            )

    for relative_path in CURRENT_STATE_OWNER_DOCS:
        text = _read_text(relative_path)
        for stale_term in STALE_CURRENT_STATE_TERMS:
            require(
                stale_term not in text,
                f"{relative_path}: stale current-state term '{stale_term}' is still present (line {_line_number(text, stale_term)})",
            )

    for relative_path in AUXILIARY_GUIDANCE_DOCS:
        text = _read_text(relative_path)
        for stale_term in STALE_AUXILIARY_TERMS:
            require(
                stale_term not in text,
                f"{relative_path}: stale auxiliary current-state term '{stale_term}' is still present (line {_line_number(text, stale_term)})",
            )

    template_text = _read_text(Path("Docs/orin_task_template.md"))
    for field_label in ("Mode:", "Phase:", "Workstream:", "Branch:", "Branch Class:"):
        require(
            field_label in template_text,
            f"Docs/orin_task_template.md: required prompt field '{field_label}' is missing",
        )

    user_guide_text = _read_text(Path("Docs/codex_user_guide.md"))
    for field_label in ("Mode:", "Phase:", "Workstream:", "Branch:"):
        require(
            field_label in user_guide_text,
            f"Docs/codex_user_guide.md: exact prompt contract no longer mentions '{field_label}'",
        )

    for relative_path in SUCCESSOR_LOCK_WAIVER_DOCS:
        text = _read_text(relative_path)
        require(
            SUCCESSOR_LOCK_WAIVER_PHRASE in text,
            (
                f"{relative_path}: successor-lock waiver for post-merge `No Active Branch` "
                "state due to `Release Debt` or another admission blocker is missing"
            ),
        )

    for relative_path in NO_ACTIVE_BRANCH_STEADY_STATE_DOCS:
        text = _read_text(relative_path)
        require(
            NO_ACTIVE_BRANCH_STEADY_STATE_PHRASE in text,
            f"{relative_path}: blocked-versus-steady-state `No Active Branch` handling is missing",
        )

    for relative_path in DOCS_GOVERNANCE_ADMISSION_DOCS:
        text = _read_text(relative_path)
        require(
            "docs/governance" in text,
            f"{relative_path}: docs/governance historical branch-class guidance is missing",
        )

    for relative_path in GOVERNANCE_ONLY_BLOCK_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in GOVERNANCE_ONLY_BLOCK_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: governance-only / between-branch repair blocker guidance is missing '{required_phrase}'",
            )

    for relative_path in MULTI_SEAM_CONTRACT_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in MULTI_SEAM_CONTRACT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: canonical bounded multi-seam workflow contract is missing '{required_phrase}'",
            )
        for prohibited_phrase in MULTI_SEAM_PROHIBITED_CATEGORY_STOP_PHRASES:
            require(
                prohibited_phrase not in text,
                f"{relative_path}: bounded seam workflow must not recreate category-based Single-Seam Fallback stop authority via '{prohibited_phrase}'",
            )
        for prohibited_phrase in MULTI_SEAM_PROHIBITED_THROTTLE_PHRASES:
            require(
                prohibited_phrase not in lower_text,
                f"{relative_path}: bounded seam workflow must not recreate single-seam throttling authority via '{prohibited_phrase}'",
            )

    phase_governance_text = _read_text(Path("Docs/phase_governance.md"))
    for required_phrase in MULTI_SEAM_PRIMARY_REPAIR_PHRASES:
        require(
            required_phrase in phase_governance_text,
            f"Docs/phase_governance.md: primary seam governance is missing category-stop repair phrase '{required_phrase}'",
        )

    for relative_path in MULTI_SEAM_PROMPT_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in MULTI_SEAM_PROMPT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: multi-seam prompt scaffold is missing '{required_phrase}'",
            )
        for prohibited_phrase in MULTI_SEAM_PROHIBITED_THROTTLE_PHRASES:
            require(
                prohibited_phrase not in lower_text,
                f"{relative_path}: prompt scaffold must not recreate single-seam throttling authority via '{prohibited_phrase}'",
            )

    for relative_path, guard_phrase in zip(WORKSTREAM_TO_PR_DEFAULT_GUARD_DOCS, WORKSTREAM_TO_PR_DEFAULT_GUARD_PHRASES):
        text = _read_text(relative_path)
        require(
            guard_phrase in text,
            f"{relative_path}: direct Workstream-to-PR default guard is missing",
        )

    for relative_path in PRE_PR_DURABILITY_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PRE_PR_DURABILITY_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Pre-PR Durability Rule is missing '{required_phrase}'",
            )

    for relative_path in PLANNING_LOOP_GUARDRAIL_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PLANNING_LOOP_GUARDRAIL_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: planning-loop guardrail guidance is missing '{required_phrase}'",
            )

    for relative_path in LIVE_VALIDATION_REUSE_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in LIVE_VALIDATION_REUSE_PHRASES:
            require(
                required_phrase in lower_text,
                f"{relative_path}: Live Validation reuse-first helper guidance is missing '{required_phrase}'",
            )

    for relative_path in LIVE_VALIDATION_STALL_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in LIVE_VALIDATION_STALL_PHRASES:
            require(
                required_phrase in lower_text,
                f"{relative_path}: Live Validation no-progress/stall guidance is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in LIVE_VALIDATION_HELPER_CONTRACTS.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: reusable Live Validation helper is missing '{required_phrase}'",
            )

    registry_path = ROOT_DIR / VALIDATION_HELPER_REGISTRY
    require(
        registry_path.is_file(),
        f"{VALIDATION_HELPER_REGISTRY}: validation helper registry is missing",
    )
    registry_text = _read_text(VALIDATION_HELPER_REGISTRY) if registry_path.is_file() else ""

    for relative_path in VALIDATION_HELPER_STANDARD_DOCS:
        text = _read_text(relative_path)
        for required_phrase in VALIDATION_HELPER_STANDARD_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: validation helper standardization guidance is missing '{required_phrase}'",
            )

    if registry_text:
        for helper_path in _root_dev_helper_paths():
            helper_line = _registry_line_for_path(registry_text, helper_path)
            require(
                bool(helper_line),
                f"{VALIDATION_HELPER_REGISTRY}: root dev helper '{helper_path}' is not registered",
            )
            if helper_line:
                require(
                    "Helper Status:" in helper_line,
                    f"{VALIDATION_HELPER_REGISTRY}: helper '{helper_path}' is missing Helper Status",
                )
                if re.search(r"dev/orin_fb\d+_", helper_path):
                    require(
                        "Helper Status: Workstream-scoped" in helper_line,
                        (
                            f"{VALIDATION_HELPER_REGISTRY}: workstream helper '{helper_path}' "
                            "must be marked Helper Status: Workstream-scoped"
                        ),
                    )
                    require(
                        re.search(r"consolidat|fold|promot", helper_line, flags=re.I) is not None,
                        (
                            f"{VALIDATION_HELPER_REGISTRY}: workstream helper '{helper_path}' "
                            "must name a consolidation or promotion target"
                        ),
                    )

    for relative_path in PR_READINESS_BLOCKER_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in PR_READINESS_BLOCKER_PHRASES:
            require(
                required_phrase.casefold() in text,
                f"{relative_path}: PR Readiness blocker guidance is missing '{required_phrase}'",
            )

    for relative_path in RELEASE_WINDOW_AUDIT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in RELEASE_WINDOW_AUDIT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: release-window audit guidance is missing '{required_phrase}'",
            )

    for relative_path in PR_READINESS_RESPONSE_CONTRACT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PR_READINESS_RESPONSE_CONTRACT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: PR Readiness response contract is missing '{required_phrase}'",
            )

    for relative_path in RELEASE_OPERATOR_OUTPUT_CONTRACT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in RELEASE_OPERATOR_OUTPUT_CONTRACT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Release operator output contract is missing '{required_phrase}'",
            )

    for relative_path in PR_LIVE_STATE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PR_LIVE_STATE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: PR live-state completion contract is missing '{required_phrase}'",
            )

    for relative_path in UTS_RESULTS_BLOCKER_DOCS:
        text = _read_text(relative_path)
        for required_phrase in UTS_RESULTS_BLOCKER_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: User Test Summary results blocker guidance is missing '{required_phrase}'",
            )

    for relative_path in USER_FACING_SHORTCUT_GATE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in USER_FACING_SHORTCUT_GATE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: user-facing shortcut Live Validation gate guidance is missing '{required_phrase}'",
            )

    for relative_path in RELEASE_READINESS_TARGET_DOCS:
        text = _read_text(relative_path)
        for required_phrase in RELEASE_READINESS_TARGET_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Release Readiness target gate guidance is missing '{required_phrase}'",
            )

    for relative_path in RELEASE_READINESS_SCOPE_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in RELEASE_READINESS_SCOPE_PHRASES:
            require(
                required_phrase.casefold() in text,
                f"{relative_path}: Release Readiness docs-sync scope boundary is missing '{required_phrase}'",
            )

    for relative_path in RELEASE_READINESS_FILE_FREEZE_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in RELEASE_READINESS_FILE_FREEZE_PHRASES:
            require(
                required_phrase.casefold() in text,
                f"{relative_path}: Release Readiness file-freeze guidance is missing '{required_phrase}'",
            )

    for relative_path in RELEASE_TITLE_FORMAT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in RELEASE_TITLE_FORMAT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Pre-Beta release title format guidance is missing '{required_phrase}'",
            )

    for relative_path in PROTECTED_MAIN_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in PROTECTED_MAIN_PHRASES:
            require(
                required_phrase.casefold() in text,
                f"{relative_path}: protected-main governance is missing '{required_phrase}'",
            )

    for relative_path in MERGED_UNRELEASED_CONTRACT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in MERGED_UNRELEASED_CONTRACT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: merged-unreleased release-debt contract is missing '{required_phrase}'",
            )

    if _git_current_branch() == "main":
        status_output = _git_status_porcelain(tracked_only=True)
        require(
            not status_output,
            "Main Write Attempt blocker is active; Codex must not leave tracked file mutations on protected main",
        )

    active_index_paths = _collect_active_index_paths(index_text)
    closed_index_paths = _collect_closed_index_paths(index_text)
    release_debt_index_paths = _collect_release_debt_index_paths(index_text)
    active_branch_record_paths = _collect_branch_record_paths(branch_record_index_text, "Active Branch Authority Records")
    historical_branch_record_paths = _collect_branch_record_paths(branch_record_index_text, "Historical Branch Authority Records")
    current_git_branch = _git_current_branch()
    branch_record_class_map, all_repair_branch_names, active_repair_branch_names = _branch_record_branch_sets(
        active_branch_record_paths,
        historical_branch_record_paths,
        current_git_branch,
    )
    ignored_selected_next_branch_names = _selected_next_ignored_branch_names(
        current_git_branch,
        all_repair_branch_names,
        active_repair_branch_names,
    )
    merged_no_active_branch_truth = (
        "Repo State: No Active Branch" in backlog_text or "Repo State: No Active Branch" in roadmap_text
    )
    if current_git_branch == "main" and merged_no_active_branch_truth:
        require(
            not active_branch_record_paths,
            (
                "Docs/branch_records/index.md: merged current-state canon declares `No Active Branch`, "
                "so `Active Branch Authority Records` must be empty on main"
            ),
        )

    backlog_entries = _parse_backlog_sections(backlog_text)
    for entry in backlog_entries:
        post_release_truth_count = _count_field_occurrences(entry["block"], "Post-Release Truth")
        require(
            post_release_truth_count <= 1,
            (
                f"Docs/feature_backlog.md: {entry['id']} must not define multiple "
                "`Post-Release Truth:` fields"
            ),
        )
    _run_open_backlog_selection_governance(require, backlog_entries)
    latest_public_prerelease = _latest_public_prerelease(roadmap_text)
    highest_known_prebeta_tag = _highest_known_prebeta_tag()
    if highest_known_prebeta_tag:
        require(
            latest_public_prerelease == highest_known_prebeta_tag,
            (
                "Docs/prebeta_roadmap.md: latest public prerelease must match the latest "
                f"local or remote prebeta tag '{highest_known_prebeta_tag}', found '{latest_public_prerelease}'"
            ),
        )

    fb038_entry = _entry_by_id(backlog_entries, "FB-038")
    require(bool(fb038_entry), "Docs/feature_backlog.md: FB-038 backlog entry is missing")
    if highest_known_prebeta_tag == FB038_RELEASE_TAG and fb038_entry:
        require(
            fb038_entry["record_state"] == "Closed",
            f"Docs/feature_backlog.md: FB-038 must be Closed after {FB038_RELEASE_TAG} release",
        )
        require(
            _normalize_status(fb038_entry["status"]) == "released",
            f"Docs/feature_backlog.md: FB-038 must be Released after {FB038_RELEASE_TAG} release",
        )
        require(
            _clean_release_value(_extract_colon_value(fb038_entry["block"], "Target Version")) == FB038_RELEASE_TAG,
            f"Docs/feature_backlog.md: FB-038 Target Version must remain {FB038_RELEASE_TAG}",
        )
        require(
            _clean_release_value(_extract_colon_value(fb038_entry["block"], "Release Title")) == FB038_RELEASE_TITLE,
            f"Docs/feature_backlog.md: FB-038 Release Title must be '{FB038_RELEASE_TITLE}'",
        )
        require(
            FB038_CANONICAL_PATH in closed_index_paths,
            "Docs/workstreams/index.md: FB-038 must be listed under Closed after v1.4.1-prebeta release",
        )
        require(
            FB038_CANONICAL_PATH not in release_debt_index_paths,
            "Docs/workstreams/index.md: FB-038 must not remain under Merged / Release Debt Owners after release",
        )
        roadmap_lower = roadmap_text.casefold()
        require(
            "merged-unreleased release-debt owner: fb-038" not in roadmap_lower,
            "Docs/prebeta_roadmap.md: FB-038 release must not remain the release-debt owner",
        )
        fb038_workstream_path = ROOT_DIR / Path(FB038_CANONICAL_PATH)
        require(
            fb038_workstream_path.is_file(),
            f"{FB038_CANONICAL_PATH}: FB-038 workstream doc does not exist",
        )
        if fb038_workstream_path.is_file():
            fb038_text = _read_text(Path(FB038_CANONICAL_PATH))
            fb038_info = _parse_workstream_doc(fb038_text)
            require(
                fb038_info["record_state"] == "Closed",
                f"{FB038_CANONICAL_PATH}: Record State must be Closed after {FB038_RELEASE_TAG} release",
            )
            require(
                _normalize_status(str(fb038_info["status"])) == "released",
                f"{FB038_CANONICAL_PATH}: Status must be Released after {FB038_RELEASE_TAG} release",
            )
            require(
                f"Latest Public Prerelease: {FB038_RELEASE_TAG}" in fb038_text,
                f"{FB038_CANONICAL_PATH}: released-state canon must record latest public prerelease {FB038_RELEASE_TAG}",
            )
            require(
                f"Release Title: {FB038_RELEASE_TITLE}" in fb038_text,
                f"{FB038_CANONICAL_PATH}: released-state canon must record release title '{FB038_RELEASE_TITLE}'",
            )

    if highest_known_prebeta_tag:
        expected_latest_title = _expected_prebeta_release_title(highest_known_prebeta_tag)
        latest_release_owner_entries = [
            entry
            for entry in backlog_entries
            if _clean_release_value(_extract_colon_value(entry["block"], "Target Version"))
            == highest_known_prebeta_tag
        ]
        for entry in latest_release_owner_entries:
            workstream_id = entry["id"]
            canonical_path = entry["canonical_path"]
            normalized_status = _normalize_status(entry["status"])
            require(
                entry["record_state"] == "Closed",
                (
                    "Post-release canon closure drift: "
                    f"{workstream_id} targets published tag {highest_known_prebeta_tag} "
                    f"but backlog Record State is '{entry['record_state']}', not 'Closed'"
                ),
            )
            require(
                normalized_status == "released",
                (
                    "Post-release canon closure drift: "
                    f"{workstream_id} targets published tag {highest_known_prebeta_tag} "
                    f"but backlog Status is '{entry['status']}', not Released"
                ),
            )
            release_title = _clean_release_value(_extract_colon_value(entry["block"], "Release Title"))
            if release_title:
                require(
                    release_title == expected_latest_title,
                    (
                        "Post-release canon closure drift: "
                        f"{workstream_id} Release Title '{release_title}' must be "
                        f"'{expected_latest_title}' for {highest_known_prebeta_tag}"
                    ),
                )
            require(
                bool(canonical_path),
                f"Post-release canon closure drift: {workstream_id} is missing Canonical Workstream Doc",
            )
            if not canonical_path:
                continue

            require(
                canonical_path in closed_index_paths,
                (
                    "Post-release canon closure drift: "
                    f"{canonical_path} must be listed under Closed after {highest_known_prebeta_tag}"
                ),
            )
            require(
                canonical_path not in release_debt_index_paths,
                (
                    "Post-release canon closure drift: "
                    f"{canonical_path} must not remain under Merged / Release Debt Owners "
                    f"after {highest_known_prebeta_tag}"
                ),
            )
            require(
                canonical_path not in active_index_paths,
                (
                    "Post-release canon closure drift: "
                    f"{canonical_path} must not remain under Active after {highest_known_prebeta_tag}"
                ),
            )

            release_debt_claim = _release_debt_owner_claim(workstream_id)
            for source_name, source_text in (
                ("Docs/feature_backlog.md", backlog_text),
                ("Docs/prebeta_roadmap.md", roadmap_text),
            ):
                require(
                    release_debt_claim not in source_text.casefold(),
                    (
                        "Post-release canon closure drift: "
                        f"{source_name} still claims {workstream_id} as merged-unreleased release debt "
                        f"after {highest_known_prebeta_tag}"
                    ),
                )

            workstream_path = ROOT_DIR / Path(canonical_path)
            require(
                workstream_path.is_file(),
                f"Post-release canon closure drift: {canonical_path} does not exist",
            )
            if workstream_path.is_file():
                workstream_text = _read_text(Path(canonical_path))
                workstream_info = _parse_workstream_doc(workstream_text)
                require(
                    workstream_info["record_state"] == "Closed",
                    (
                        "Post-release canon closure drift: "
                        f"{canonical_path} Record State must be Closed after {highest_known_prebeta_tag}"
                    ),
                )
                require(
                    _normalize_status(str(workstream_info["status"])) == "released",
                    (
                        "Post-release canon closure drift: "
                        f"{canonical_path} Status must be Released after {highest_known_prebeta_tag}"
                    ),
                )
                require(
                    f"Latest Public Prerelease: {highest_known_prebeta_tag}" in workstream_text,
                    (
                        "Post-release canon closure drift: "
                        f"{canonical_path} must record Latest Public Prerelease: {highest_known_prebeta_tag}"
                    ),
                )
                require(
                    f"Release Title: {expected_latest_title}" in workstream_text,
                    (
                        "Post-release canon closure drift: "
                        f"{canonical_path} must record Release Title: {expected_latest_title}"
                    ),
                )
                require(
                    release_debt_claim not in workstream_text.casefold(),
                    (
                        "Post-release canon closure drift: "
                        f"{canonical_path} still claims {workstream_id} as merged-unreleased release debt "
                        f"after {highest_known_prebeta_tag}"
                    ),
                )

            roadmap_section = _roadmap_section_for_id(roadmap_text, workstream_id)
            require(
                bool(roadmap_section),
                (
                    "Post-release canon closure drift: "
                    f"Docs/prebeta_roadmap.md is missing released section for {workstream_id}"
                ),
            )
            if roadmap_section:
                roadmap_status = _extract_first_backtick_value(roadmap_section)
                require(
                    _normalize_status(roadmap_status) == "released",
                    (
                        "Post-release canon closure drift: "
                        f"Docs/prebeta_roadmap.md status for {workstream_id} must be released"
                    ),
                )
                require(
                    canonical_path in roadmap_section,
                    (
                        "Post-release canon closure drift: "
                        f"Docs/prebeta_roadmap.md released section for {workstream_id} "
                        f"must cite {canonical_path}"
                    ),
                )

    if pr_readiness_gate:
        _run_pr_readiness_gate(
            require,
            backlog_entries,
            roadmap_text,
            ignored_selected_next_branch_names,
            branch_record_class_map,
        )

    selected_entries = _selected_next_workstream_entries(backlog_entries)
    if len(selected_entries) == 1 and not pr_readiness_gate:
        selected = selected_entries[0]
        selected_id = selected["id"]
        roadmap_section = _next_workstream_roadmap_section(roadmap_text)
        branch_names, branch_error = _git_branch_names()
        require(
            not branch_error,
            f"Selected next workstream branch check: could not inspect branch names: {branch_error}",
        )
        if not branch_error and roadmap_section:
            matching_branches = _branch_names_for_workstream(
                branch_names,
                selected_id,
                ignored_selected_next_branch_names,
            )
            if matching_branches:
                repair_only_handling = _selected_next_repair_only_branch_handling(
                    [selected["block"], roadmap_section]
                )
                non_repair_matching_branches = [
                    branch_name
                    for branch_name in matching_branches
                    if branch_record_class_map.get(branch_name) != EMERGENCY_CANON_REPAIR_BRANCH_CLASS
                ]
                if repair_only_handling and not non_repair_matching_branches:
                    matching_branches = []
                else:
                    if not non_repair_matching_branches and any(
                        branch_record_class_map.get(branch_name) == EMERGENCY_CANON_REPAIR_BRANCH_CLASS
                        for branch_name in matching_branches
                    ):
                        require(
                            repair_only_handling,
                            (
                                "Selected next workstream branch truth is ambiguous: "
                                f"{selected_id} only has repair-only branch(es) {', '.join(matching_branches)}, "
                                "but roadmap/backlog do not explicitly declare that repair-only branch existence "
                                "does not imply Branch Readiness admission or active branch truth"
                            ),
                        )
                    matching_branches = non_repair_matching_branches or matching_branches
            if matching_branches:
                current_branch = current_git_branch
                roadmap_lower = roadmap_section.casefold()
                claims_not_created = any(
                    phrase.casefold() in roadmap_lower
                    for phrase in NEXT_WORKSTREAM_BRANCH_NOT_CREATED_PHRASES
                )
                require(
                    not claims_not_created,
                    (
                        "Next Branch Created Too Early / current-state claim drift: "
                        f"{selected_id} has branch(es) {', '.join(matching_branches)} but roadmap still claims no branch exists"
                    ),
                )
                require(
                    current_branch in matching_branches and current_branch in roadmap_section,
                    (
                        "Selected next workstream branch truth is ambiguous: "
                        f"{selected_id} has branch(es) {', '.join(matching_branches)}, "
                        "but the current branch is not recorded as the Branch Readiness branch in roadmap"
                    ),
                )
                require(
                    "Branch Readiness" in selected["block"] or "Branch Readiness" in roadmap_section,
                    (
                        "Selected next workstream branch truth is ambiguous: "
                        f"{selected_id} branch exists but Branch Readiness-only admission state is not explicit"
                    ),
                )

    promoted_entries = [
        entry
        for entry in backlog_entries
        if entry.get("record_state") == "Promoted"
    ]
    if not promoted_entries:
        require(
            not active_index_paths,
            "Docs/workstreams/index.md: Active list must be empty when no backlog workstream is Promoted",
        )

    fb041_entries = [entry for entry in backlog_entries if entry.get("id") == "FB-041"]
    require(bool(fb041_entries), "Docs/feature_backlog.md: FB-041 backlog entry is missing")
    if fb041_entries:
        fb041_entry = fb041_entries[0]
        fb041_path = fb041_entry["canonical_path"]
        require(
            fb041_entry["record_state"] == "Closed",
            "Docs/feature_backlog.md: FB-041 must be Closed after v1.3.1-prebeta release",
        )
        require(
            _normalize_status(fb041_entry["status"]) == "released",
            "Docs/feature_backlog.md: FB-041 must be Released after v1.3.1-prebeta release",
        )
        require(
            fb041_path in closed_index_paths,
            "Docs/workstreams/index.md: FB-041 must be listed under Closed after v1.3.1-prebeta release",
        )
        require(
            fb041_path not in active_index_paths,
            "Docs/workstreams/index.md: FB-041 must not remain under Active after v1.3.1-prebeta release",
        )

        if fb041_path:
            fb041_doc_path = Path(fb041_path)
            require(
                (ROOT_DIR / fb041_doc_path).is_file(),
                f"{fb041_path}: FB-041 workstream doc does not exist",
            )
            if (ROOT_DIR / fb041_doc_path).is_file():
                fb041_text = _read_text(fb041_doc_path)
                fb041_info = _parse_workstream_doc(fb041_text)
                require(
                    fb041_info["record_state"] == "Closed",
                    f"{fb041_path}: Record State must be Closed after v1.3.1-prebeta release",
                )
                require(
                    _normalize_status(str(fb041_info["status"])) == "released",
                    f"{fb041_path}: Status must be Released after v1.3.1-prebeta release",
                )

        fb041_roadmap_section = _roadmap_section_for_id(roadmap_text, "FB-041")
        require(
            bool(fb041_roadmap_section),
            "Docs/prebeta_roadmap.md: FB-041 release section is missing",
        )
        if fb041_roadmap_section:
            require(
                fb041_path in fb041_roadmap_section,
                "Docs/prebeta_roadmap.md: FB-041 release section must cite the canonical workstream doc",
            )
            require(
                "release state: `released`" in fb041_roadmap_section,
                "Docs/prebeta_roadmap.md: FB-041 release state must be `released`",
            )

    for entry in promoted_entries:
        workstream_id = entry["id"]
        canonical_path = entry["canonical_path"]
        require(
            bool(canonical_path),
            f"Docs/feature_backlog.md: promoted workstream {workstream_id} is missing Canonical Workstream Doc",
        )
        if not canonical_path:
            continue

        require(
            canonical_path in main_canonical_workstream_routes,
            (
                "Docs/Main.md: promoted workstream "
                f"{canonical_path} is missing from the Canonical Workstream Records routing list"
            ),
        )

        workstream_path = Path(canonical_path)
        require(
            (ROOT_DIR / workstream_path).is_file(),
            f"{canonical_path}: promoted workstream doc for {workstream_id} does not exist",
        )
        if not (ROOT_DIR / workstream_path).is_file():
            continue

        workstream_text = _read_text(workstream_path)
        workstream_info = _parse_workstream_doc(workstream_text)

        require(
            workstream_info["record_state"] == entry["record_state"],
            (
                f"{canonical_path}: Record State '{workstream_info['record_state']}' does not match "
                f"backlog '{entry['record_state']}' for {workstream_id}"
            ),
        )
        require(
            _normalize_status(str(workstream_info["status"])) == _normalize_status(entry["status"]),
            (
                f"{canonical_path}: Status '{workstream_info['status']}' does not match "
                f"backlog status '{entry['status']}' for {workstream_id}"
            ),
        )

        for heading in REQUIRED_WORKSTREAM_HEADINGS:
            require(
                heading in workstream_text,
                f"{canonical_path}: required heading '{heading}' is missing",
            )

        current_phase = str(workstream_info["current_phase"])
        branch_class = str(workstream_info["branch_class"])
        canonical_branch = str(workstream_info["canonical_branch"])
        rollback_target = str(workstream_info["rollback_target"])
        next_legal_phase = str(workstream_info["next_legal_phase"])
        blockers = list(workstream_info["blockers"])

        require(
            current_phase in PHASES,
            f"{canonical_path}: Current Phase '{current_phase}' is not in the canonical phase enum",
        )
        require(
            branch_class in BRANCH_CLASSES,
            f"{canonical_path}: Branch Class '{branch_class}' is not in the canonical branch-class enum",
        )
        require(
            rollback_target in PHASES,
            f"{canonical_path}: Rollback Target '{rollback_target}' is not in the canonical phase enum",
        )
        require(
            next_legal_phase in PHASES,
            f"{canonical_path}: Next Legal Phase '{next_legal_phase}' is not in the canonical phase enum",
        )
        if blockers and current_phase in PHASES and next_legal_phase in PHASES:
            require(
                _phase_index(next_legal_phase) <= _phase_index(current_phase),
                (
                    f"{canonical_path}: blockers are present ({', '.join(blockers)}) but "
                    f"Next Legal Phase advances from '{current_phase}' to '{next_legal_phase}'"
                ),
            )

        if current_phase == "Branch Readiness":
            for heading in REQUIRED_BRANCH_READINESS_DURABILITY_HEADINGS:
                require(
                    heading in workstream_text,
                    (
                        f"{canonical_path}: Branch Readiness durability scaffold is missing "
                        f"required heading '{heading}'"
                    ),
                )

            initial_seam_sequence = _section(workstream_text, "Initial Workstream Seam Sequence")
            for marker in REQUIRED_BRANCH_READINESS_FIRST_SEAM_MARKERS:
                require(
                    marker in initial_seam_sequence,
                    (
                        f"{canonical_path}: Initial Workstream Seam Sequence must define a first seam "
                        f"with '{marker}'"
                    ),
                )

            active_seam_section = _section(workstream_text, "Active Seam")
            require(
                "Active seam:" in active_seam_section,
                f"{canonical_path}: Active Seam section must clearly identify the active seam",
            )

        if current_phase == "Workstream":
            continuation_section = _section(workstream_text, "Seam Continuation Decision")
            require(
                bool(continuation_section),
                f"{canonical_path}: active Workstream record must include '## Seam Continuation Decision'",
            )
            for marker in REQUIRED_WORKSTREAM_CONTINUATION_MARKERS:
                require(
                    marker in continuation_section,
                    f"{canonical_path}: Seam Continuation Decision is missing '{marker}'",
                )

        if current_phase in {"Live Validation", "PR Readiness"}:
            require(
                _has_user_test_summary(workstream_text),
                (
                    f"{canonical_path}: active '{current_phase}' workstream must include an exact "
                    "'## User Test Summary' section; '## User Test Summary Strategy' is not the "
                    "canonical UTS artifact"
                ),
            )
            uts_result = _parse_uts_result_state(workstream_text)
            require(
                bool(uts_result),
                (
                    f"{canonical_path}: active '{current_phase}' workstream must declare "
                    f"'{UTS_RESULT_LABEL}'"
                ),
            )
            if uts_result:
                require(
                    uts_result in UTS_RESULT_VALUES,
                    (
                        f"{canonical_path}: {UTS_RESULT_LABEL} '{uts_result}' must be one of "
                        f"{', '.join(UTS_RESULT_VALUES)}"
                    ),
                )
                if uts_result == "PENDING":
                    require(
                        UTS_RESULTS_BLOCKER in blockers,
                        (
                            f"{canonical_path}: {UTS_RESULT_LABEL} PENDING requires "
                            f"'{UTS_RESULTS_BLOCKER}' under Blockers"
                        ),
                    )
                    require(
                        next_legal_phase == current_phase,
                        (
                            f"{canonical_path}: {UTS_RESULT_LABEL} PENDING must keep Next Legal Phase "
                            f"at '{current_phase}' until returned results are digested"
                        ),
                    )
                if uts_result == "FAIL":
                    require(
                        UTS_RESULTS_BLOCKER in blockers or blockers,
                        (
                            f"{canonical_path}: {UTS_RESULT_LABEL} FAIL must keep an explicit blocker "
                            "and route back before advancement"
                        ),
                    )
                if uts_result in UTS_CLEAR_RESULT_VALUES:
                    require(
                        UTS_RESULTS_BLOCKER not in blockers,
                        (
                            f"{canonical_path}: {UTS_RESULTS_BLOCKER} must clear after "
                            f"{UTS_RESULT_LABEL} {uts_result}"
                        ),
                    )
                if uts_result == "WAIVED":
                    require(
                        bool(_parse_uts_waiver_reason(workstream_text)),
                        (
                            f"{canonical_path}: {UTS_RESULT_LABEL} WAIVED requires "
                            f"'{UTS_WAIVER_REASON_LABEL}' in the exact '## User Test Summary' section"
                        ),
                    )
                if current_phase == "PR Readiness":
                    require(
                        uts_result in UTS_CLEAR_RESULT_VALUES,
                        (
                            f"{canonical_path}: PR Readiness requires {UTS_RESULT_LABEL} PASS or WAIVED; "
                            f"current value is {uts_result}"
                        ),
                    )

        if current_phase in {"Live Validation", "PR Readiness"} and _requires_user_facing_shortcut_gate(
            workstream_text
        ):
            shortcut_result = _parse_user_facing_shortcut_state(workstream_text)
            shortcut_path = _parse_user_facing_shortcut_path(workstream_text)
            require(
                bool(shortcut_result),
                (
                    f"{canonical_path}: active desktop user-facing '{current_phase}' workstream must declare "
                    f"'{USER_FACING_SHORTCUT_RESULT_LABEL}' before User Test Summary handoff"
                ),
            )
            if shortcut_result:
                require(
                    shortcut_result in USER_FACING_SHORTCUT_RESULT_VALUES,
                    (
                        f"{canonical_path}: {USER_FACING_SHORTCUT_RESULT_LABEL} '{shortcut_result}' must be one of "
                        f"{', '.join(USER_FACING_SHORTCUT_RESULT_VALUES)}"
                    ),
                )
                if shortcut_result != "WAIVED":
                    require(
                        bool(shortcut_path),
                        (
                            f"{canonical_path}: {USER_FACING_SHORTCUT_RESULT_LABEL} {shortcut_result} requires "
                            f"'{USER_FACING_SHORTCUT_PATH_LABEL}'"
                        ),
                    )
                if shortcut_result == "PENDING":
                    require(
                        USER_FACING_SHORTCUT_BLOCKER in blockers,
                        (
                            f"{canonical_path}: {USER_FACING_SHORTCUT_RESULT_LABEL} PENDING requires "
                            f"'{USER_FACING_SHORTCUT_BLOCKER}' under Blockers"
                        ),
                    )
                    require(
                        next_legal_phase == current_phase,
                        (
                            f"{canonical_path}: {USER_FACING_SHORTCUT_RESULT_LABEL} PENDING must keep "
                            f"Next Legal Phase at '{current_phase}' until shortcut evidence is digested"
                        ),
                    )
                if shortcut_result == "FAIL":
                    require(
                        blockers,
                        (
                            f"{canonical_path}: {USER_FACING_SHORTCUT_RESULT_LABEL} FAIL must keep an explicit "
                            "blocker and route back before advancement"
                        ),
                    )
                if shortcut_result in USER_FACING_SHORTCUT_CLEAR_VALUES:
                    require(
                        USER_FACING_SHORTCUT_BLOCKER not in blockers,
                        (
                            f"{canonical_path}: {USER_FACING_SHORTCUT_BLOCKER} must clear after "
                            f"{USER_FACING_SHORTCUT_RESULT_LABEL} {shortcut_result}"
                        ),
                    )
                if shortcut_result == "WAIVED":
                    require(
                        bool(_parse_user_facing_shortcut_waiver_reason(workstream_text)),
                        (
                            f"{canonical_path}: {USER_FACING_SHORTCUT_RESULT_LABEL} WAIVED requires "
                            f"'{USER_FACING_SHORTCUT_WAIVER_REASON_LABEL}' in the exact "
                            "'## User Test Summary' section"
                        ),
                    )
                uts_result_for_shortcut = _parse_uts_result_state(workstream_text)
                if uts_result_for_shortcut in UTS_CLEAR_RESULT_VALUES:
                    require(
                        shortcut_result in USER_FACING_SHORTCUT_CLEAR_VALUES,
                        (
                            f"{canonical_path}: {UTS_RESULT_LABEL} {uts_result_for_shortcut} requires "
                            f"{USER_FACING_SHORTCUT_RESULT_LABEL} PASS or WAIVED first"
                        ),
                    )
                if current_phase == "PR Readiness":
                    require(
                        shortcut_result in USER_FACING_SHORTCUT_CLEAR_VALUES,
                        (
                            f"{canonical_path}: PR Readiness requires "
                            f"{USER_FACING_SHORTCUT_RESULT_LABEL} PASS or WAIVED; current value is {shortcut_result}"
                        ),
                    )

        if current_phase in {"PR Readiness", "Release Readiness"}:
            governance_audit = str(workstream_info["governance_audit"])
            require(
                bool(governance_audit),
                f"{canonical_path}: Governance Drift Audit section is required before or during '{current_phase}'",
            )
            require(
                "Governance Drift Found:" in governance_audit,
                f"{canonical_path}: Governance Drift Audit is missing 'Governance Drift Found:'",
            )

        if current_phase == "Release Readiness" and _git_current_branch() == "main":
            status_output = _git_status_porcelain(tracked_only=True)
            require(
                not status_output,
                (
                    f"{canonical_path}: Release Readiness File Mutation Attempt blocker is active; "
                    "tracked files are dirty while Current Phase is Release Readiness"
                ),
            )

        if current_phase == "PR Readiness":
            post_merge_state = _section(workstream_text, "Post-Merge State")
            require(
                bool(post_merge_state),
                f"{canonical_path}: PR Readiness requires a Post-Merge State section",
            )
            require(
                ("No Active Branch" in post_merge_state)
                or ("successor" in post_merge_state.casefold()),
                (
                    f"{canonical_path}: PR Readiness Post-Merge State must encode either "
                    "No Active Branch handling or successor-branch handling"
                ),
            )
            _validate_release_window_audit(require, canonical_path, workstream_text)

        phase_status_section = _section(workstream_text, "Phase Status")
        normalized_workstream_status = _normalize_status(str(workstream_info["status"]))
        _validate_planning_loop_guardrail(
            require,
            canonical_path,
            workstream_text,
            branch_class=branch_class,
            current_phase=current_phase,
            normalized_status=normalized_workstream_status,
        )
        if (
            current_git_branch == "main"
            and branch_class == "implementation"
            and normalized_workstream_status == "active"
            and canonical_branch
            and canonical_branch != "main"
        ):
            require(
                False,
                (
                    f"{canonical_path}: post-merge current-state drift is active; "
                    "main must not carry active implementation workstream truth for a canonical "
                    f"branch outside main ('{canonical_branch}'). After merge, the workstream must "
                    "be represented as merged-unreleased release debt or closed state."
                ),
            )
        if normalized_workstream_status == "merged unreleased":
            require(
                current_phase == "Release Readiness",
                (
                    f"{canonical_path}: merged-unreleased release-debt owner "
                    "must use `Release Readiness` as Current Phase"
                ),
            )
            require(
                "`No Active Branch`" in phase_status_section,
                (
                    f"{canonical_path}: merged-unreleased release-debt owner "
                    "must declare `No Active Branch` in Phase Status"
                ),
            )
            require(
                "`Active Branch`" not in phase_status_section,
                (
                    f"{canonical_path}: merged-unreleased release-debt owner "
                    "must not still declare `Active Branch` in Phase Status"
                ),
            )
            stale_pr_blockers = sorted(set(blockers) & set(POST_MERGE_PR_BLOCKERS))
            require(
                not stale_pr_blockers,
                (
                    f"{canonical_path}: merged-unreleased release-debt owner "
                    "must not keep pre-merge PR blockers active after merge: "
                    f"{', '.join(stale_pr_blockers)}"
                ),
            )
            require(
                "Current PR blocker state:" not in workstream_text,
                (
                    f"{canonical_path}: merged-unreleased release-debt owner "
                    "must not describe pre-merge PR blockers as current state"
                ),
            )
            require(
                "Current PR state: not created" not in workstream_text,
                (
                    f"{canonical_path}: merged-unreleased release-debt owner "
                    "must not describe the merged PR as currently uncreated"
                ),
            )
            require(
                "Merged Canon Drift" not in blockers and "Current-State Claim Drift" not in blockers,
                (
                    f"{canonical_path}: merged-unreleased release-debt owner "
                    "must not keep resolved current-state drift blockers active"
                ),
            )

        if normalized_workstream_status == "merged unreleased":
            roadmap_section = _roadmap_section_for_id(roadmap_text, workstream_id)
            for required_marker in REQUIRED_MERGED_UNRELEASED_MARKERS:
                require(
                    required_marker in workstream_text,
                    f"{canonical_path}: merged-unreleased release-debt owner is missing '{required_marker}'",
                )
            require(
                "merged unreleased non-doc implementation debt exists: yes" in roadmap_text,
                (
                    "Docs/prebeta_roadmap.md: merged-unreleased workstream exists but "
                    "release posture does not declare implementation release debt"
                ),
            )
            require(
                "current active workstream: none" in roadmap_text,
                (
                    "Docs/prebeta_roadmap.md: merged-unreleased release-debt state "
                    "must clear active workstream truth"
                ),
            )
            require(
                "Merged-Unreleased Release-Debt Owner:" in backlog_text,
                "Docs/feature_backlog.md: merged-unreleased release-debt owner contract is missing",
            )
            for required_marker in REQUIRED_MERGED_UNRELEASED_MARKERS:
                require(
                    required_marker in roadmap_text,
                    f"Docs/prebeta_roadmap.md: merged-unreleased release-debt state is missing '{required_marker}'",
                )
                require(
                    required_marker in backlog_text,
                    f"Docs/feature_backlog.md: merged-unreleased release-debt state is missing '{required_marker}'",
                )
            latest_public_prerelease = _latest_public_prerelease(roadmap_text)
            require(
                bool(latest_public_prerelease),
                "Docs/prebeta_roadmap.md: latest public prerelease is missing",
            )
            require(
                _parse_prebeta_version(latest_public_prerelease) is not None,
                (
                    "Docs/prebeta_roadmap.md: latest public prerelease must use "
                    "v<major>.<minor>.<patch>-prebeta"
                ),
            )

            release_sources = (
                ("Docs/feature_backlog.md", entry["block"]),
                ("Docs/prebeta_roadmap.md", roadmap_section),
                (canonical_path, workstream_text),
            )
            release_floors = [
                _clean_release_value(_extract_colon_value(source_text, "Release Floor")).casefold()
                for _, source_text in release_sources
            ]
            release_floor = release_floors[0] if release_floors else ""
            for source_name, source_text in release_sources:
                source_floor = _clean_release_value(_extract_colon_value(source_text, "Release Floor")).casefold()
                source_rationale = _clean_release_value(_extract_colon_value(source_text, "Version Rationale"))
                require(
                    source_floor in SEMANTIC_RELEASE_FLOORS,
                    (
                        f"{source_name}: Release Target Undefined blocker is active; "
                        f"Release Floor must be one of {', '.join(SEMANTIC_RELEASE_FLOORS)}"
                    ),
                )
                require(
                    bool(source_rationale),
                    (
                        f"{source_name}: Release Target Undefined blocker is active; "
                        "Version Rationale is required for semantic release target validation"
                    ),
                )
                require(
                    source_floor == release_floor,
                    (
                        f"{source_name}: Release Target Undefined blocker is active; "
                        "Release Floor must match backlog release floor"
                    ),
                )
                if source_floor == MINOR_PRERELEASE_FLOOR:
                    source_scope = _extract_colon_value(source_text, "Release Scope")
                    rationale_context = f"{source_rationale} {source_scope}"
                    require(
                        _minor_release_rationale_has_capability(rationale_context),
                        (
                            f"{source_name}: Release Target Undefined blocker is active; "
                            "`minor prerelease` requires a new executable, runtime, "
                            "operator-facing, user-facing, or materially expanded product "
                            "capability rationale; architecture-only or non-user-facing "
                            "planning/admission work must use `patch prerelease`"
                        ),
                    )

            expected_release_target = _expected_prerelease_target(latest_public_prerelease, release_floor)
            require(
                bool(expected_release_target),
                (
                    f"{canonical_path}: Release Target Undefined blocker is active; "
                    "cannot derive semantic release target from latest public prerelease and Release Floor"
                ),
            )

            if expected_release_target:
                expected_release_title = _expected_prebeta_release_title(expected_release_target)
                backlog_target_version = _clean_release_value(
                    _extract_colon_value(entry["block"], "Target Version")
                )
                require(
                    backlog_target_version == expected_release_target,
                    (
                        "Docs/feature_backlog.md: Release Target Undefined blocker is active; "
                        f"Target Version '{backlog_target_version}' must be '{expected_release_target}'"
                    ),
                )
                workstream_target_version = _workstream_target_version(workstream_text)
                require(
                    workstream_target_version == expected_release_target,
                    (
                        f"{canonical_path}: Release Target Undefined blocker is active; "
                        f"Target Version '{workstream_target_version}' must be '{expected_release_target}'"
                    ),
                )

                for source_name, source_text in release_sources:
                    source_target = _clean_release_value(_extract_colon_value(source_text, "Release Target"))
                    source_artifacts = _extract_colon_value(source_text, "Release Artifacts")
                    source_post_release = _extract_colon_value(source_text, "Post-Release Truth")
                    require(
                        source_target == expected_release_target,
                        (
                            f"{source_name}: Release Target Undefined blocker is active; "
                            f"Release Target '{source_target}' must be '{expected_release_target}' "
                            f"for {release_floor}"
                        ),
                    )
                    require(
                        expected_release_target in source_artifacts,
                        (
                            f"{source_name}: Release Target Undefined blocker is active; "
                            f"Release Artifacts must reference '{expected_release_target}'"
                        ),
                    )
                    require(
                        expected_release_title in source_artifacts,
                        (
                            f"{source_name}: Release Target Undefined blocker is active; "
                            "Release Artifacts must use the canonical Pre-Beta release title "
                            f"'{expected_release_title}'"
                        ),
                    )
                    require(
                        expected_release_target in source_post_release,
                        (
                            f"{source_name}: Release Target Undefined blocker is active; "
                            f"Post-Release Truth must reference '{expected_release_target}'"
                        ),
                    )
            require(
                canonical_path in release_debt_index_paths,
                (
                    f"Docs/workstreams/index.md: promoted merged-unreleased workstream "
                    f"{canonical_path} is missing from the Merged / Release Debt Owners list"
                ),
            )
            require(
                canonical_path not in active_index_paths,
                (
                    f"Docs/workstreams/index.md: promoted merged-unreleased workstream "
                    f"{canonical_path} must not remain under Active"
                ),
            )
        else:
            require(
                canonical_path in active_index_paths,
                f"Docs/workstreams/index.md: promoted workstream {canonical_path} is missing from the Active list",
            )
        require(
            canonical_path not in closed_index_paths,
            f"Docs/workstreams/index.md: promoted workstream {canonical_path} is incorrectly listed under Closed",
        )

        roadmap_section = _roadmap_section_for_id(roadmap_text, workstream_id)
        require(
            bool(roadmap_section),
            f"Docs/prebeta_roadmap.md: promoted workstream {workstream_id} is missing from the roadmap",
        )
        if roadmap_section:
            require(
                canonical_path in roadmap_section,
                f"Docs/prebeta_roadmap.md: roadmap section for {workstream_id} does not cite {canonical_path}",
            )
            roadmap_status = _extract_first_backtick_value(roadmap_section)
            require(
                _normalize_status(roadmap_status) == _normalize_status(entry["status"]),
                (
                    f"Docs/prebeta_roadmap.md: roadmap status '{roadmap_status}' does not match "
                    f"backlog status '{entry['status']}' for {workstream_id}"
                ),
            )

    governance_text = _read_text(Path("Docs/phase_governance.md"))
    require(
        "python dev/orin_branch_governance_validation.py" in governance_text,
        "Docs/phase_governance.md: Governance Validator section does not cite python dev/orin_branch_governance_validation.py",
    )

    require(
        "Docs/branch_records/" in branch_record_index_text,
        "Docs/branch_records/index.md: expected branch-record paths in the index",
    )
    all_branch_names, all_branch_name_error = _git_branch_names()
    require(
        not all_branch_name_error,
        f"Could not inspect branch names for branch-record validation: {all_branch_name_error}",
    )

    for branch_record_path in active_branch_record_paths | historical_branch_record_paths:
        record_path = ROOT_DIR / Path(branch_record_path)
        require(
            record_path.is_file(),
            f"{branch_record_path}: branch authority record listed in Docs/branch_records/index.md does not exist",
        )
        if not record_path.is_file():
            continue

        record_text = _read_text(Path(branch_record_path))
        branch_name = _extract_branch_identity_branch(record_text)
        phase_status_section = _section(record_text, "Phase Status")
        for heading in REQUIRED_BRANCH_RECORD_HEADINGS:
            require(
                heading in record_text,
                f"{branch_record_path}: required heading '{heading}' is missing",
            )

        info = _parse_workstream_doc(record_text)
        normalized_record_status = _normalize_status(str(info["status"]))
        require(
            str(info["current_phase"]) in PHASES,
            f"{branch_record_path}: Current Phase '{info['current_phase']}' is not in the canonical phase enum",
        )
        require(
            str(info["branch_class"]) in BRANCH_CLASSES,
            f"{branch_record_path}: Branch Class '{info['branch_class']}' is not in the canonical branch-class enum",
        )
        branch_class = str(info["branch_class"])
        has_non_release_marker = NON_RELEASE_BRANCH_MARKER in record_text
        if branch_class in RELEASE_BEARING_BRANCH_CLASSES:
            for required_marker in REQUIRED_RELEASE_BEARING_MARKERS:
                require(
                    required_marker in record_text,
                    f"{branch_record_path}: release-bearing branch record is missing '{required_marker}'",
                )
            require(
                not has_non_release_marker,
                (
                    f"{branch_record_path}: release-bearing branch class '{branch_class}' "
                    f"must not use '{NON_RELEASE_BRANCH_MARKER}'"
                ),
            )
        if has_non_release_marker:
            require(
                branch_record_path in historical_branch_record_paths,
                (
                    f"{branch_record_path}: '{NON_RELEASE_BRANCH_MARKER}' is only allowed for "
                    "preserved historical records"
                ),
            )
        require(
            str(info["rollback_target"]) in PHASES,
            f"{branch_record_path}: Rollback Target '{info['rollback_target']}' is not in the canonical phase enum",
        )
        require(
            str(info["next_legal_phase"]) in PHASES,
            f"{branch_record_path}: Next Legal Phase '{info['next_legal_phase']}' is not in the canonical phase enum",
        )
        if branch_record_path in active_branch_record_paths:
            _validate_planning_loop_guardrail(
                require,
                branch_record_path,
                record_text,
                branch_class=branch_class,
                current_phase=str(info["current_phase"]),
                normalized_status=normalized_record_status,
            )
        if branch_record_path in active_branch_record_paths and str(info["current_phase"]) == "Release Readiness":
            status_output = _git_status_porcelain(tracked_only=True)
            require(
                not status_output,
                (
                    f"{branch_record_path}: Release Readiness File Mutation Attempt blocker is active; "
                    "tracked files are dirty while Current Phase is Release Readiness"
                ),
            )
        if branch_record_path in active_branch_record_paths and str(info["current_phase"]) in {
            "PR Readiness",
            "Release Readiness",
        }:
            governance_audit = _section(record_text, "Governance Drift Audit")
            require(
                bool(governance_audit),
                (
                    f"{branch_record_path}: Governance Drift Audit section is required before or during "
                    f"'{info['current_phase']}'"
                ),
            )
            require(
                "Governance Drift Found:" in governance_audit,
                f"{branch_record_path}: Governance Drift Audit is missing 'Governance Drift Found:'",
            )
        if branch_record_path in active_branch_record_paths and str(info["current_phase"]) == "PR Readiness":
            post_merge_state = _section(record_text, "Post-Merge State")
            require(
                bool(post_merge_state),
                f"{branch_record_path}: PR Readiness requires a Post-Merge State section",
            )
            require(
                ("No Active Branch" in post_merge_state)
                or ("successor" in post_merge_state.casefold()),
                (
                    f"{branch_record_path}: PR Readiness Post-Merge State must encode either "
                    "No Active Branch handling or successor-branch handling"
                ),
            )
            _validate_release_window_audit(require, branch_record_path, record_text)
        if branch_record_path in active_branch_record_paths:
            require(
                "`Active Branch`" in phase_status_section,
                f"{branch_record_path}: active branch record must declare `Active Branch` in Phase Status",
            )
            require(
                bool(branch_name),
                f"{branch_record_path}: active branch record must declare a Branch in Branch Identity",
            )
            require(
                (branch_name in all_branch_names) or (f"origin/{branch_name}" in all_branch_names),
                (
                    f"{branch_record_path}: active branch record points to missing branch "
                    f"'{branch_name}'"
                ),
            )
        if branch_record_path in historical_branch_record_paths:
            require(
                "`Active Branch`" not in phase_status_section,
                f"{branch_record_path}: historical branch record must not still declare `Active Branch` in Phase Status",
            )
            require(
                "historical" in phase_status_section.lower(),
                f"{branch_record_path}: historical branch record should make its historical merged posture explicit",
            )

    if errors:
        print(f"FAIL: branch governance validation found {len(errors)} issue(s).")
        for issue in errors:
            print(f"- {issue}")
        return 1

    print(f"PASS: branch governance validation passed {checks} checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
