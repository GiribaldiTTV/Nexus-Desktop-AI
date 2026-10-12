# NEXUS-SOURCE-OWNER: schema=source-owner-v1; owner=GOV-SOURCE-TRUTH; ledger=SRCOWN-FIRSTPASS-VALIDATOR-010; surface=governance-efficiency-validator; status=shared
"""Validate the governance efficiency operating model.

This helper is intentionally small and report-only. It checks that the compact
governance reform model exists, is discoverable from the routing docs, and keeps
backlog/roadmap from absorbing detailed runtime-branch planning narrative.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATING_MODEL = Path("Docs/governance_efficiency_operating_model.md")
DOCS_INVENTORY_AUDIT = Path("Docs/governance_docs_full_inventory_reform_audit.md")
DOCS_REFORM_REVIEW_INDEX = Path("Docs/governance_docs_reform_user_review_index.md")
NEXUS_VISION = Path("Docs/nexus_vision.md")
FAMILY_VISION_INDEX = Path("Docs/family_visions/README.md")
BRANCH_PLAN_RETIREMENT_INDEX = Path("Docs/branch_plans/retirement_index.md")
USER_REVIEW_BUNDLE_HELPER = Path("dev/orin_user_review_bundle.py")

REQUIRED_MODEL_PHRASES = (
    "Rule ID And Owner Model",
    "Repo Docs Index-Only Contract",
    "Source-Truth Ownership Matrix",
    "Docs Source-Truth Reform Model",
    "Derived Live Truth Versus Historical Receipt",
    "Duplicate Live-State Guard",
    "Current Summary And Historical Appendix Split",
    "Phase Alias UX",
    "Branch Planning UX Standard",
    "Branch Record / Plan / Workstream Fold-Down Model",
    "Product Vision Contract Model",
    "Vision-To-Plan Interaction Loop",
    "USER Feedback Disposition Model",
    "USER Review Integration Decisions",
    "USER Review Hub Rule",
    "Standing Governance Ledger Compaction",
    "Release Ownership UX",
    "Public Language Mapping",
    "Validator Modularization Boundary",
    "Validation Runner And Registry Query Rule",
    "Naming Drift Scan Rule",
    "Reform Pass Completion Model",
)

POINTER_REQUIREMENTS = {Path('Docs/development_rules.md'): ('Docs/governance_efficiency_operating_model.md', 'Rule ID'), Path('Docs/codex_modes.md'): ('Docs/governance_efficiency_operating_model.md', 'smallest legal'), Path('Docs/validation_helper_registry.md'): ('dev/orin_governance_efficiency_validation.py', 'dev/orin_user_review_bundle.py', 'governance efficiency operating model'), Path('Docs/branch_records/index.md'): ('Docs Source-Truth Reform Model: Compact Pointer Layer', 'Current Summary And Historical Appendix Split', 'PR Readiness fold-down'), Path('Docs/branch_plans/README.md'): ('Docs Source-Truth Reform Model: Compact Pointer Layer', 'Fold-Down Model', 'PR Fold-Down Packet:', 'USER Feedback Disposition', 'No-Action Reason:', 'Docs/branch_plans/retirement_index.md'), Path('Docs/workstreams/index.md'): ('Docs Source-Truth Reform Model: Compact Pointer Layer', 'Package And Slice Trace Ownership', 'Package Trace and Slice Trace detail belongs here'), Path('Docs/worktree_slots.md'): ('Docs Source-Truth Reform Model: Compact Pointer Layer', 'This file does not own', 'Assigned slot does not equal active branch authority'), Path('Docs/governance_process_efficiency_reform_plan.md'): ('Consolidated Governance Reform Pass', 'Docs/governance_efficiency_operating_model.md', 'Marker-first governance scaffolding implemented', 'USER Feedback Disposition')}

BACKLOG_ROADMAP_COMPACTNESS_FORBIDDEN = (
    "Package Trace:",
    "Slice Trace:",
    "Per-Seam Implementation Checklist:",
    "Per-Seam Validation Checklist:",
    "Per-Seam User-Facing Proof Checklist:",
    "Plan-To-Implementation Traceability Table:",
    "Hardening Comparison Checklist:",
    "Live Validation Proof Or Waiver Checklist:",
    "PR Readiness Fold-Down / Retention Checklist:",
    "Release Readiness Public-Scope Translation Checklist:",
)

BACKLOG_ROADMAP_CURRENT_STATE_SECTIONS = (
    "## Current Decision Surface",
    "## Current Branch Execution Posture",
    "## Selected Next Workstream",
    "## Future Planning Pointers",
)

BACKLOG_ROADMAP_CURRENT_STATE_FORBIDDEN = (
    "Latest Public Prerelease Recorded In Source Truth:",
    "Latest Public Prerelease:",
    "Latest Public Release Commit:",
    "Latest Public Prerelease Publication:",
    "Release Candidate Anchor:",
    "Release Window Contributor Inventory:",
    "Merged-Unreleased PRs:",
    "Active Runtime Branch: Branch-local",
    "Active Runtime Branch:",
    "Current Active Workstream: Branch-local",
    "Current active workstream: Branch-local",
    "PR Readiness Stage 2 / PR creation",
    "PR Readiness Stage 2 execution gate",
    "Branch Creation Status: No branch created",
    "No branch created",
    "No live PR",
)

BACKLOG_ROADMAP_POINTER_FORBIDDEN = (
    "PR Readiness Stage 1 Ready For Stage 2",
    "PR creation pending",
    "PR Creation Approval: Pending",
    "Stage 2 PR Creation: Pending",
    "No live PR",
)

BACKLOG_ROADMAP_CURRENT_STATE_BRANCH_FIELDS = (
    "Selected Next Implementation Branch",
    "Current Carrier Branch",
    "Branch Creation Status",
    "Branch",
)

BACKLOG_ROADMAP_CURRENT_STATE_FORBIDDEN_PATTERNS = (
    (
        r"(?i)\bPR\s+#\d+\s+is\s+open\b",
        "current-state text records an open live PR",
    ),
    (
        r"(?mi)^\s*Live PR(?:\s|:)",
        "current-state text records live PR state",
    ),
    (
        r"(?mi)^\s*(?:Current-Main Reconciliation Update|Release Scope|Release Artifacts|Post-Release Truth):",
        "current-state text records release or branch execution receipt detail",
    ),
    (
        r"\b[0-9a-f]{40}\b",
        "current-state text pins an exact commit hash",
    ),
)

WORKTREE_SLOT_FORBIDDEN = (
    "Latest Public Prerelease Recorded In Source Truth:",
    "Release Candidate Anchor:",
    "Release Window Contributor Inventory:",
    "Merged-Unreleased PRs:",
    "Live PR State:",
    "Review Decision:",
    "PR Readiness Stage 1 Ready For Stage 2",
    "PR creation pending",
    "PR Creation Approval: Pending",
    "Stage 2 PR Creation: Pending",
    "No live PR",
)

BRANCH_RECORD_INDEX_REQUIRED = (
    "Branch records are authority and structured traceability receipt surfaces",
    "Branch records must not become durable family dossiers",
    "Package Trace and Slice Trace detail belongs",
)

BRANCH_PLAN_README_REQUIRED = (
    "Repo branch-plan files are not the long-term place to maintain active ledger rows",
    "At PR Readiness, the `PR Fold-Down Packet:` must classify plan content",
    "It must not preserve stale active phase",
    "USER Feedback Disposition",
    "UFD-<scope>-YYYYMMDD-NNN",
    "No-Action Reason:",
    "Docs/branch_plans/retirement_index.md",
)

EXPECTED_FAMILY_VISION_FILES = (
    Path("Docs/family_visions/FAM-001_boot_interface.md"),
    Path("Docs/family_visions/FAM-002_desktop_interface.md"),
    Path("Docs/family_visions/FAM-003_interaction_and_actions.md"),
    Path("Docs/family_visions/FAM-004_voice_and_audio.md"),
    Path("Docs/family_visions/FAM-005_external_integrations.md"),
    Path("Docs/family_visions/FAM-006_monitoring_and_hud.md"),
    Path("Docs/family_visions/FAM-007_local_ai_and_capability_packs.md"),
    Path("Docs/family_visions/FAM-008_packaging_and_install_experience.md"),
)

EXPECTED_PENDING_FOLD_SOURCE_FILES = (
    Path("Docs/family_visions/FAM-009_workspace_and_data.md"),
    Path("Docs/family_visions/FAM-010_safety_and_privacy.md"),
)

USER_REVIEW_BUNDLE_REQUIRED_FIELDS = ()  # External publication owner owns this contract.

USER_REVIEW_HUB_TIMESTAMPED_ZIP_REQUIRED_PHRASES = ()  # External publication owner owns this contract.

WORKSTREAM_INDEX_REQUIRED = (
    "workstreams and family dossiers own durable package trace, slice trace",
    "workstreams and family dossiers must not mirror live Git/GitHub state",
    "Do not promote:",
)

CORE_GOVERNANCE_MIRROR_DOCS = (
    Path("Docs/Main.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/orin_task_template.md"),
)

CORE_GOVERNANCE_DUPLICATE_POLICY_FORBIDDEN = (
    "Release Readiness Candidate Anchor: require",
    "Release Window Aggregation Ownership: merge order does not decide release ownership",
)

AUDIT_REQUIRED_SECTIONS = (
    "## Executive Summary",
    "## How To Review This Dossier",
    "## What Was Completed",
    "## What Remains External",
    "## What Requires USER Decision",
    "## USER Review Intake Model",
    "## USER Response Integration Matrix",
    "## Single-PR Staged Execution Plan",
    "## Disposition Changes From USER Review",
    "## High-Risk Files",
    "## Files Safe To Leave For Now",
    "## Files Needing Future Migration",
    "## Files That May Be Retired Later",
    "## Completed / External Decision Matrix",
    "## Source-Truth Ownership Map",
    "## Complete Docs Manifest",
    "## Complete Docs Cleanup / Disposition Table",
    "## Ambiguity Pass",
    "## Structure Pass",
    "## File-by-File Review Table",
    "## Fact-Class Ownership Table",
    "## Duplicate Truth Map",
    "## Backlog Final Schema",
    "## Roadmap Final Schema",
    "## Branch Records Final Schema",
    "## Branch Plans Lifecycle And Retirement Rule",
    "## Branch Runtime Engineering Plan Lifecycle Proof",
    "## Workstreams / Family Dossier Schema",
    "## Worktree Slots Schema",
    "## Governance Docs Ownership Table",
    "## Git / GitHub / Helper-Derived Truth Plan",
    "## Validator Enforcement Table",
    "## File Retirement / Delete Candidate Table",
    "## File-By-File Review Dossier",
    "## PR Readiness Checklist",
    "## Deferred USER Decisions",
    "## Next Legal Phase",
)

INDEX_REQUIRED_SECTIONS = (
    "## Start Here",
    "## Review Proof",
    "## Suggested Review Order",
    "## Decision Checklist",
    "## User Response Intake Status",
    "## USER Response Integration Summary",
    "## Single-PR Staged Execution Plan",
    "## Disposition Changes From USER Review",
    "## Files Needing USER Decision",
    "## Ambiguity Review Queue",
    "## Structure Review Queue",
    "## High-Risk Review Queue",
    "## Future Migration Queue",
    "## Safe To Leave For Now",
    "## Exact USER Decision This Index Supports",
)


def _read(relative_path: Path) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""

    rest = text[start + len(heading) :]
    next_heading = re.search(r"(?m)^##\s+", rest)
    if next_heading:
        return text[start : start + len(heading) + next_heading.start()]
    return text[start:]


def _git_output(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, cwd=ROOT).strip()
    except Exception:
        return ""


def _branch_name_to_plan_path(branch: str) -> str:
    return f"Docs/branch_plans/{branch.replace('-', '_').replace('/', '_')}.md"


def _retired_branch_plan_paths(retirement_text: str) -> set[str]:
    retired_section = _section(retirement_text, "## Retired Branch Plans")
    return set(
        re.findall(
            r"`(Docs/branch_plans/[^`]+\.md)`\s*\|\s*Retired from active planning posture",
            retired_section,
        )
    )


def _field_value(line: str, field: str) -> str | None:
    prefix = f"{field}:"
    stripped = line.strip()
    if not stripped.startswith(prefix):
        return None
    return stripped[len(prefix) :].strip().strip("`").strip()


def _is_empty_branch_state(value: str) -> bool:
    normalized = value.casefold()
    return normalized.startswith("none") or normalized.startswith("not created")


def _docs_file_count() -> int:
    docs_root = ROOT / "Docs"
    return sum(1 for path in docs_root.rglob("*") if path.is_file())


def _all_text_files() -> list[Path]:
    candidates: list[Path] = []
    for root_name in ("Docs", "dev"):
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if root_name == "dev" and path.relative_to(root).parts[:1] == ("logs",):
                continue
            if path.is_file() and path.suffix.lower() in {".md", ".py", ".ps1", ".txt"}:
                candidates.append(path)
    readme = ROOT / "README.md"
    if readme.is_file():
        candidates.append(readme)
    return candidates


def _non_historical_stale_vision_refs() -> list[str]:
    offenders: list[str] = []
    allowed_context = "former `Docs/orin_vision.md` path"
    for path in _all_text_files():
        relative = path.relative_to(ROOT)
        if relative == Path("dev/orin_governance_efficiency_validation.py"):
            continue
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if "Docs/orin_vision.md" in line and allowed_context not in line:
                offenders.append(f"{relative}:{line_number}")
    return offenders


def _branch_plan_requires_retirement_index_row(text: str) -> bool:
    """Return true only for plans that declare folded/historical posture.

    Active branches carry active planning in the External Operational State
    Store after transition. Repo branch-plan files are schema/transition or
    historical receipt surfaces; the retirement index should not force
    transition evidence to become historical by inertia.
    """

    status_lines = [
        line
        for line in text.splitlines()
        if re.match(r"(?i)^\s*(?:Engineering Plan Status|Plan Status):", line)
    ]
    historical_markers = (
        "historical",
        "folded",
        "retired",
        "merged",
        "cleanup",
        "pr readiness stage 1 result",
    )
    if any(
        marker in line.casefold()
        for line in status_lines
        for marker in historical_markers
    ):
        return True

    global_retirement_markers = (
        "retired after",
        "historical / folded",
        "historical -",
        "merged in pr #",
        "branch cleanup",
        "folded down",
    )
    return any(marker in text.casefold() for marker in global_retirement_markers)


def validate_historical() -> list[str]:
    failures: list[str] = []

    model_text = _read(OPERATING_MODEL)
    if not model_text:
        failures.append(f"{OPERATING_MODEL}: missing governance efficiency operating model")
    else:
        for phrase in REQUIRED_MODEL_PHRASES:
            if phrase not in model_text:
                failures.append(
                    f"{OPERATING_MODEL}: missing required section or phrase {phrase!r}"
                )
        desktop_bundle_section = _section(model_text, "## USER Review Hub Rule")
        for phrase in USER_REVIEW_BUNDLE_REQUIRED_FIELDS:
            if phrase not in desktop_bundle_section:
                failures.append(
                    f"{OPERATING_MODEL}: USER Review Hub Rule missing "
                    f"required START_HERE review field {phrase!r}"
                )
        for phrase in USER_REVIEW_HUB_TIMESTAMPED_ZIP_REQUIRED_PHRASES:
            if phrase.casefold() not in desktop_bundle_section.casefold():
                failures.append(
                    f"{OPERATING_MODEL}: USER Review Hub Rule missing "
                    f"timestamped ZIP policy phrase {phrase!r}"
                )

    bundle_helper_text = _read(USER_REVIEW_BUNDLE_HELPER)
    if not bundle_helper_text:
        failures.append(f"{USER_REVIEW_BUNDLE_HELPER}: missing USER review bundle helper")
    else:
        for phrase in USER_REVIEW_BUNDLE_REQUIRED_FIELDS:
            if phrase not in bundle_helper_text:
                failures.append(
                    f"{USER_REVIEW_BUNDLE_HELPER}: missing required START_HERE review field {phrase!r}"
                )
        for phrase in USER_REVIEW_HUB_TIMESTAMPED_ZIP_REQUIRED_PHRASES:
            if phrase.casefold() not in bundle_helper_text.casefold():
                failures.append(
                    f"{USER_REVIEW_BUNDLE_HELPER}: missing timestamped ZIP policy phrase {phrase!r}"
                )

    for path, required_phrases in POINTER_REQUIREMENTS.items():
        text = _read(path)
        if not text:
            failures.append(f"{path}: missing required pointer document")
            continue
        for phrase in required_phrases:
            if phrase not in text:
                failures.append(f"{path}: missing governance efficiency pointer {phrase!r}")

    if not (ROOT / NEXUS_VISION).is_file():
        failures.append(f"{NEXUS_VISION}: missing Nexus Vision contract")
    else:
        vision_text = _read(NEXUS_VISION)
        for phrase in (
            "Nexus Vision Contract",
            "project-wide product vision contract",
            "Docs/family_visions/",
        ):
            if phrase not in vision_text:
                failures.append(f"{NEXUS_VISION}: missing vision contract phrase {phrase!r}")

    if not (ROOT / FAMILY_VISION_INDEX).is_file():
        failures.append(f"{FAMILY_VISION_INDEX}: missing family vision index")
    else:
        family_index_text = _read(FAMILY_VISION_INDEX)
        for family_path in EXPECTED_FAMILY_VISION_FILES:
            if not (ROOT / family_path).is_file():
                failures.append(f"{family_path}: missing family vision record")
            if str(family_path).replace("\\", "/") not in family_index_text:
                failures.append(
                    f"{FAMILY_VISION_INDEX}: missing family vision pointer {family_path}"
                )
        for fold_source_path in EXPECTED_PENDING_FOLD_SOURCE_FILES:
            if not (ROOT / fold_source_path).is_file():
                failures.append(f"{fold_source_path}: missing pending fold-source record")
            if str(fold_source_path).replace("\\", "/") not in family_index_text:
                failures.append(
                    f"{FAMILY_VISION_INDEX}: missing pending fold-source pointer {fold_source_path}"
                )

    stale_vision_refs = _non_historical_stale_vision_refs()
    if stale_vision_refs:
        failures.append(
            "stale Docs/orin_vision.md references remain outside former-path migration "
            f"context: {', '.join(stale_vision_refs[:10])}"
        )

    if not (ROOT / BRANCH_PLAN_RETIREMENT_INDEX).is_file():
        failures.append(f"{BRANCH_PLAN_RETIREMENT_INDEX}: missing branch plan retirement index")
    else:
        retirement_text = _read(BRANCH_PLAN_RETIREMENT_INDEX)
        branch_plan_root = ROOT / "Docs" / "branch_plans"
        for branch_plan in sorted(branch_plan_root.glob("*.md")):
            relative = branch_plan.relative_to(ROOT)
            if relative in {Path("Docs/branch_plans/README.md"), BRANCH_PLAN_RETIREMENT_INDEX}:
                continue
            branch_plan_text = branch_plan.read_text(encoding="utf-8")
            if not _branch_plan_requires_retirement_index_row(branch_plan_text):
                continue
            if str(relative).replace("\\", "/") not in retirement_text:
                failures.append(
                    f"{BRANCH_PLAN_RETIREMENT_INDEX}: missing retired plan row for {relative}"
                )

    audit_text = _read(DOCS_INVENTORY_AUDIT)
    if not audit_text:
        failures.append(f"{DOCS_INVENTORY_AUDIT}: missing full Docs reform audit dossier")
    else:
        for section in AUDIT_REQUIRED_SECTIONS:
            if section not in audit_text:
                failures.append(
                    f"{DOCS_INVENTORY_AUDIT}: missing required review section {section!r}"
                )
        docs_count_match = re.search(r"Audit File Count:\s*(\d+)\s+files under `Docs/`", audit_text)
        docs_count = int(docs_count_match.group(1)) if docs_count_match else -1
        audit_count_match = re.search(
            r"Audit File Count:\s*(\d+)\s+files under `Docs/`",
            audit_text,
        )
        manifest_count_match = re.search(r"Manifest Files Enumerated:\s*(\d+)", audit_text)
        audit_count = int(audit_count_match.group(1)) if audit_count_match else -1
        manifest_count = int(manifest_count_match.group(1)) if manifest_count_match else -1
        if audit_count != docs_count:
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: Audit File Count {audit_count} does not "
                f"match dated inventory count {docs_count}"
            )
        if manifest_count != docs_count:
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: Manifest Files Enumerated {manifest_count} "
                f"does not match dated inventory count {docs_count}"
            )
        dossier_entries = len(
            re.findall(r"(?m)^###\s+\d+\.\s+`Docs/", audit_text)
        )
        if dossier_entries != docs_count:
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: File-By-File Review Dossier has "
                f"{dossier_entries} entries, expected {docs_count}"
            )
        disposition_rows = len(
            re.findall(
                r"(?m)^\| `Docs/",
                _section(audit_text, "## Complete Docs Cleanup / Disposition Table"),
            )
        )
        if disposition_rows != docs_count:
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: cleanup/disposition table has "
                f"{disposition_rows} file rows, expected {docs_count}"
            )
        ambiguity_rows = len(
            re.findall(r"(?m)^\| `Docs/", _section(audit_text, "## Ambiguity Pass"))
        )
        if ambiguity_rows != docs_count:
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: Ambiguity Pass has "
                f"{ambiguity_rows} file rows, expected {docs_count}"
            )
        structure_rows = len(
            re.findall(r"(?m)^\| `Docs/", _section(audit_text, "## Structure Pass"))
        )
        if structure_rows != docs_count:
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: Structure Pass has "
                f"{structure_rows} file rows, expected {docs_count}"
            )
        if "dev/orin_docs_inventory_reform_audit.py" not in audit_text:
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: missing generator helper reference"
            )
        if str(DOCS_REFORM_REVIEW_INDEX).replace("\\", "/") not in audit_text:
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: missing user review index pointer"
            )
        audit_identity = _section(audit_text, "## Audit Identity")
        if re.search(r"(?m)^-\s*Audit Branch:\s*`[^`]+`", audit_identity):
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: Audit Identity must not store a live branch name"
            )
        if re.search(r"(?m)^-\s*Audit Workspace:\s*`[A-Za-z]:\\", audit_identity):
            failures.append(
                f"{DOCS_INVENTORY_AUDIT}: Audit Identity must not store a live worktree path"
            )

    index_text = _read(DOCS_REFORM_REVIEW_INDEX)
    if not index_text:
        failures.append(f"{DOCS_REFORM_REVIEW_INDEX}: missing user review index")
    else:
        for section in INDEX_REQUIRED_SECTIONS:
            if section not in index_text:
                failures.append(
                    f"{DOCS_REFORM_REVIEW_INDEX}: missing required review section {section!r}"
                )
        if str(DOCS_INVENTORY_AUDIT).replace("\\", "/") not in index_text:
            failures.append(
                f"{DOCS_REFORM_REVIEW_INDEX}: missing full dossier pointer"
            )
        docs_count_match = re.search(r"Audit File Count:\s*(\d+)\s+files under `Docs/`", audit_text)
        docs_count = int(docs_count_match.group(1)) if docs_count_match else -1
        index_count_match = re.search(r"Docs files covered:\s*(\d+)", index_text)
        index_count = int(index_count_match.group(1)) if index_count_match else -1
        if index_count != docs_count:
            failures.append(
                f"{DOCS_REFORM_REVIEW_INDEX}: Docs files covered {index_count} "
                f"does not match dated inventory count {docs_count}"
            )
        if re.search(r"(?m)^-\s*Source branch:\s*`[^`]+`", index_text):
            failures.append(
                f"{DOCS_REFORM_REVIEW_INDEX}: must not store a live source branch"
            )
        if re.search(r"Current execution model:.*`[^`]*(?:feature/|codex/|\bmain\b)[^`]*`", index_text):
            failures.append(
                f"{DOCS_REFORM_REVIEW_INDEX}: current execution model must not store a live branch"
            )
        exact_decision = _section(index_text, "## Exact USER Decision This Index Supports")
        if re.search(r"`[^`]*(?:feature/|codex/|\bmain\b)[^`]*`", exact_decision):
            failures.append(
                f"{DOCS_REFORM_REVIEW_INDEX}: exact decision must not pin a live branch"
            )
        user_decision_section = _section(index_text, "## Files Needing USER Decision")
        user_decision_rows = len(re.findall(r"(?m)^\| `Docs/", user_decision_section))
        user_decision_count_match = re.search(
            r"Total USER decision rows:\s*(\d+)",
            user_decision_section,
        )
        if user_decision_count_match:
            user_decision_count = int(user_decision_count_match.group(1))
            if user_decision_count != user_decision_rows:
                failures.append(
                    f"{DOCS_REFORM_REVIEW_INDEX}: Files Needing USER Decision declares "
                    f"{user_decision_count} rows but lists {user_decision_rows}"
                )
        retirement_text = _read(BRANCH_PLAN_RETIREMENT_INDEX)
        retired_plan_paths = _retired_branch_plan_paths(retirement_text)
        user_decision_paths = set(
            re.findall(r"(?m)^\| `(Docs/[^`]+)`", user_decision_section)
        )
        for retired_plan_path in sorted(retired_plan_paths):
            if retired_plan_path not in user_decision_section:
                failures.append(
                    f"{DOCS_REFORM_REVIEW_INDEX}: Files Needing USER Decision missing "
                    f"retired plan row for {retired_plan_path}"
                )
        for user_decision_path in sorted(
            path for path in user_decision_paths if path.startswith("Docs/branch_plans/")
        ):
            if user_decision_path not in retired_plan_paths:
                failures.append(
                    f"{DOCS_REFORM_REVIEW_INDEX}: Files Needing USER Decision lists "
                    f"{user_decision_path}, but that file is not listed in "
                    f"{BRANCH_PLAN_RETIREMENT_INDEX}'s retired branch-plan table"
                )

    for path in (Path("Docs/feature_backlog.md"), Path("Docs/prebeta_roadmap.md")):
        text = _read(path)
        if not text:
            failures.append(f"{path}: missing compact current-state owner")
            continue
        for phrase in BACKLOG_ROADMAP_COMPACTNESS_FORBIDDEN:
            if phrase in text:
                failures.append(
                    f"{path}: detailed source-truth marker {phrase!r} belongs in "
                    "Docs/workstreams, Docs/branch_plans, or folded historical receipts, "
                    "not backlog/roadmap"
                )
        if "Docs Source-Truth Reform Model: Compact Pointer Layer" not in text:
            failures.append(
                f"{path}: missing Docs Source-Truth Reform Model compact pointer marker"
            )
        if "index" not in text.lower():
            failures.append(
                f"{path}: compact pointer surface must explicitly identify itself as an index/reference surface, not an operational ledger"
            )
        for phrase in BACKLOG_ROADMAP_POINTER_FORBIDDEN:
            if phrase in text:
                failures.append(
                    f"{path}: compact pointer surface retains stale pre-PR/PR-creation "
                    f"wording {phrase!r}; use merged-unreleased, released/closed, "
                    "historical receipt, external operational state, or Git/GitHub/helper-derived truth instead"
                )

        current_state_text = "\n".join(
            _section(text, heading) for heading in BACKLOG_ROADMAP_CURRENT_STATE_SECTIONS
        )
        for phrase in BACKLOG_ROADMAP_CURRENT_STATE_FORBIDDEN:
            if phrase in current_state_text:
                failures.append(
                    f"{path}: current-state section carries branch-local/live-state phrase "
                    f"{phrase!r}; backlog/roadmap must stay compact and route active branch "
                    "identity to external operational state, Git/GitHub/helper-derived truth, or historical receipts"
                )
        for line in current_state_text.splitlines():
            for field in BACKLOG_ROADMAP_CURRENT_STATE_BRANCH_FIELDS:
                value = _field_value(line, field)
                if value is not None and not _is_empty_branch_state(value):
                    failures.append(
                        f"{path}: current-state field {field!r} carries branch-local/live-state "
                        "identity; backlog/roadmap must stay compact and route active branch "
                        "identity to external operational state, Git/GitHub/helper-derived truth, or historical receipts"
                    )
        for pattern, label in BACKLOG_ROADMAP_CURRENT_STATE_FORBIDDEN_PATTERNS:
            if re.search(pattern, current_state_text):
                failures.append(
                    f"{path}: current-state section carries branch-local/live-state pattern "
                    f"{label!r}; backlog/roadmap must stay compact and route active branch "
                    "identity to external operational state, Git/GitHub/helper-derived truth, or historical receipts"
                )

    worktree_slots_text = _read(Path("Docs/worktree_slots.md"))
    for phrase in WORKTREE_SLOT_FORBIDDEN:
        if phrase in worktree_slots_text:
            failures.append(
                "Docs/worktree_slots.md: slot registry must not carry live release, "
                f"release-window, PR, or review-state field {phrase!r}"
            )
    if re.search(r"\b[0-9a-f]{40}\b", _section(worktree_slots_text, "Standing Slot Receipts")):
        failures.append(
            "Docs/worktree_slots.md: standing slot receipts must not pin exact live commit hashes"
        )

    branch_record_index_text = _read(Path("Docs/branch_records/index.md"))
    for phrase in BRANCH_RECORD_INDEX_REQUIRED:
        if phrase not in branch_record_index_text:
            failures.append(
                f"Docs/branch_records/index.md: missing branch-record reform rule {phrase!r}"
            )

    branch_plan_readme_text = _read(Path("Docs/branch_plans/README.md"))
    for phrase in BRANCH_PLAN_README_REQUIRED:
        if phrase not in branch_plan_readme_text:
            failures.append(
                f"Docs/branch_plans/README.md: missing branch-plan fold-down rule {phrase!r}"
            )

    workstream_index_text = _read(Path("Docs/workstreams/index.md"))
    for phrase in WORKSTREAM_INDEX_REQUIRED:
        if phrase not in workstream_index_text:
            failures.append(
                f"Docs/workstreams/index.md: missing workstream trace ownership rule {phrase!r}"
            )

    for path in CORE_GOVERNANCE_MIRROR_DOCS:
        text = _read(path)
        for phrase in CORE_GOVERNANCE_DUPLICATE_POLICY_FORBIDDEN:
            if phrase in text:
                failures.append(
                    f"{path}: duplicate full release-readiness policy {phrase!r} "
                    "belongs in Docs/phase_governance.md; mirror docs should point to "
                    "the owner instead of repeating full policy prose"
                )

    return failures


def validate(changed_files=()) -> list[str]:
    """Current owner routes and affected state boundaries, not historical prose."""
    failures=[]
    router=_read(Path('Docs/Main.md'))
    for owner in ('Docs/governance_efficiency_operating_model.md','Docs/phase_governance.md','Docs/branch_plans/README.md','Docs/workstreams/index.md'):
        if owner not in router or not _read(Path(owner)).lstrip().startswith('#'):
            failures.append('missing current owner route: '+owner)
    affected={str(path).replace(chr(92),'/')for path in changed_files}
    for name in ('Docs/feature_backlog.md','Docs/prebeta_roadmap.md'):
        if name not in affected:continue
        text=_read(Path(name))
        if not text:failures.append('missing affected pointer owner: '+name);continue
        current='\n'.join(_section(text,heading)for heading in BACKLOG_ROADMAP_CURRENT_STATE_SECTIONS)
        for line in current.splitlines():
            for field in BACKLOG_ROADMAP_CURRENT_STATE_BRANCH_FIELDS:
                value=_field_value(line,field)
                if value is not None and not _is_empty_branch_state(value):
                    failures.append(name+': live branch identity belongs to its operational owner: '+field)
    return failures


def main() -> int:
    import argparse
    parser=argparse.ArgumentParser(description='Affected current efficiency contracts; historical inventories are explicit diagnostics.')
    parser.add_argument('--historical-diagnostic',action='store_true')
    parser.add_argument('--changed-file',action='append',default=None)
    args=parser.parse_args()
    if args.changed_file is None and not args.historical_diagnostic:
        import subprocess
        result=subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false','-C',str(ROOT),'diff','--name-only','origin/main'],capture_output=True,text=True)
        if result.returncode:raise ValueError('current changed-file selection unavailable')
        args.changed_file=result.stdout.splitlines()
    failures=validate_historical()if args.historical_diagnostic else validate(args.changed_file or ())
    print(('BLOCK'if failures else 'PASS')+': '+('historical diagnostic, no current admission'if args.historical_diagnostic else 'current source routes; execution not authorized'))
    for failure in failures:print('- '+failure)
    return 1 if failures else 0


if __name__ == '__main__':raise SystemExit(main())
