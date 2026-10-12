# NEXUS-SOURCE-OWNER: schema=source-owner-v1; owner=GOV-SOURCE-TRUTH; ledger=SRCOWN-FIRSTPASS-VALIDATOR-010; surface=user-review-bundle-helper; status=shared
"""Create a USER-facing local review bundle from selected repo files.

This helper copies review files to a stable worktree-labeled folder under
``C:\\Nexus USER`` and creates a timestamped upload ZIP beside that folder so
each ChatGPT upload has a unique artifact name. Legacy same-name upload ZIPs
and previous same-label timestamped upload ZIPs are removed during generation.
It never edits repo files.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Mapping

from nexus_paths import USER_HUB_ROOT


ROOT = Path(__file__).resolve().parents[1]
WINDOWS_USER_HUB_ROOT_TEXT = str(USER_HUB_ROOT)
DEFAULT_USER_HUB_ROOT = USER_HUB_ROOT
DEFAULT_REVIEW_ROOT_NAME = ""
CUSTOM_REVIEW_PATH_NONE = "None - stable review root enforced"
PUBLIC_REVIEW_BUNDLE_LEAK_PREVENTION_STATUS = (
    "PASS - copied file list and START_HERE file-list metadata are repo-relative "
    "and exclude Owner/Dev private path patterns; copied file content remains "
    "source truth for USER inspection."
)
REVIEW_EXPORT_ZIP_STALE_GUARD_STATUS = (
    "PASS - helper cleared the stable worktree review folder, copied fresh "
    "source-truth files, wrote START_HERE for this source-truth snapshot, and atomically "
    "created a timestamped review zip from that refreshed folder after removing previous "
    "same-label upload zips."
)
USER_BRANCH_PLAN_REVIEW_FILE = "USER_BRANCH_PLAN_REVIEW.md"
USER_BRANCH_VISION_REVIEW_FILE = "USER_BRANCH_VISION_REVIEW.md"
PR_READINESS_STAGE1_REVIEW_FILE = "PR_READINESS_STAGE1_REVIEW.md"
PR_STAGE1_OUTCOME_REPAIR = "PR Readiness Stage 1 Repair Required"
PR_STAGE1_OUTCOME_READY = "Stage 1 Ready For Stage 2"
USER_REVIEW_DIR_NAME = "USER Review"
REVIEW_AIDS_DIR_NAME = "Review Aids"
SOURCE_TRUTH_CONTEXT_DIR_NAME = "Source Truth Context"
PACKET_VALIDATION_MODE_ACTIVE_REVIEW = "active-review"
PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL = "accepted-historical"
PACKET_VALIDATION_MODE_NEXT_GATE = "next-gate"
PACKET_VALIDATION_MODES = (
    PACKET_VALIDATION_MODE_ACTIVE_REVIEW,
    PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL,
    PACKET_VALIDATION_MODE_NEXT_GATE,
)


def _is_dev_owner_live_validation_lv1_packet(
    source_branch: str,
    normalized_decision: str,
) -> bool:
    return (
        source_branch == "feature/fam-007-dev-owner-skeleton-readiness"
        and "approve bounded pr readiness stage 1" in normalized_decision
    )


def _is_pr_readiness_stage2_packet(
    *,
    source_branch: str,
    normalized_decision: str,
    stage1_outcome: str | None = None,
) -> bool:
    """Classify an actual Stage 2 approval before the Stage 1 fallback."""

    return (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
        and "approve pr readiness stage 2" in normalized_decision
        and stage1_outcome == PR_STAGE1_OUTCOME_READY
    )


def _is_fam007_breakpoint2_live_validation_lv1_packet(
    *,
    source_branch: str,
    normalized_decision: str,
) -> bool:
    """Keep the legacy FAM-007 LV1-green route out of PR Stage 1."""

    return (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
        and "approve bounded pr readiness stage 1" in normalized_decision
    )


def _is_pr_readiness_stage1_packet(
    *,
    source_branch: str,
    normalized_decision: str,
    stage1_outcome: str | None,
) -> bool:
    """Classify Stage 1 packets without stealing later-gate packet flows."""

    has_stage2_wording = "pr readiness stage 2" in normalized_decision
    if has_stage2_wording and stage1_outcome != PR_STAGE1_OUTCOME_READY:
        return False
    return (
        stage1_outcome in {PR_STAGE1_OUTCOME_READY, PR_STAGE1_OUTCOME_REPAIR}
        and (
            "pr readiness stage 1" in normalized_decision
            or "pr readiness stage 2" in normalized_decision
        )
        and not _is_pr_readiness_stage2_packet(
            source_branch=source_branch,
            normalized_decision=normalized_decision,
            stage1_outcome=stage1_outcome,
        )
        and not _is_fam007_breakpoint2_live_validation_lv1_packet(
            source_branch=source_branch,
            normalized_decision=normalized_decision,
        )
        and not _is_dev_owner_live_validation_lv1_packet(
            source_branch,
            normalized_decision,
        )
    )
LOCAL_USER_PACKET_ROOT_FILES = {"START_HERE.md"}
LOCAL_USER_PACKET_REQUIRED_DIRS = (
    USER_REVIEW_DIR_NAME,
    REVIEW_AIDS_DIR_NAME,
    SOURCE_TRUTH_CONTEXT_DIR_NAME,
)


PRIVATE_REVIEW_BUNDLE_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "owner-private-path",
        re.compile(
            r"(?:^|[\\/ _.-])(?:owner[-_ ]?private(?![-_ ]?boundary)|private[-_ ]?owner|"
            r"nexus[-_ ]?desktop[-_ ]?ai[-_ ]?owner|owner[-_ ]?edition)(?:[\\/ _.-]|$)",
            re.IGNORECASE,
        ),
    ),
    (
        "dev-private-path",
        re.compile(
            r"(?:^|[\\/ _.-])(?:private[-_ ]?dev|dev[-_ ]?private|"
            r"private[-_ ]?orin|dev[-_ ]?orin)(?:[\\/ _.-]|$)",
            re.IGNORECASE,
        ),
    ),
    (
        "private-artifact-path",
        re.compile(
            r"(?:^|[\\/ _.-])private[-_ ]?"
            r"(?:prompt|memory|log|eval|screenshot|automation|handoff|artifact|model|capability)"
            r"(?:[\\/ _.-]|$)",
            re.IGNORECASE,
        ),
    ),
    (
        "private-repo-path",
        re.compile(
            r"(?:^|[\\/ _.-])(?:owner|dev)[-_ ]?repo(?:[\\/ _.-]|$)|"
            r"(?:^|[\\/])\.codex[\\/](?:worktrees|private|owner|dev)(?:[\\/]|$)",
            re.IGNORECASE,
        ),
    ),
)

WORKSTREAM_ENTRY_PACKET_REQUIRED_FILES: tuple[str, ...] = (
    "START_HERE.md",
    "USER_REVIEW_FOLDER_AND_FILE_DIGEST.md",
    "GOVERNANCE_REQUIRED_FILES_SCAN.md",
    "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md",
    "BRANCH_VISION_VALIDATION_CHECKLIST.md",
)

WORKSTREAM_ENTRY_PACKET_DECISION_FILES: tuple[str, ...] = (
    "START_HERE.md",
    "USER_REVIEW_FOLDER_AND_FILE_DIGEST.md",
    "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md",
    "BRANCH_VISION_VALIDATION_CHECKLIST.md",
)

PR_READINESS_STAGE1_PACKET_REQUIRED_FILES: tuple[str, ...] = (
    "START_HERE.md",
    USER_BRANCH_VISION_REVIEW_FILE,
    USER_BRANCH_PLAN_REVIEW_FILE,
    "PR_READINESS_STAGE1_COVERAGE_DIGEST.md",
    "PR_READINESS_STAGE1_SOURCE_COVERAGE.md",
    "PR_READINESS_STAGE1_CONTRADICTION_CHECKLIST.md",
)

PR_READINESS_STAGE1_PACKET_DECISION_FILES: tuple[str, ...] = (
    "START_HERE.md",
    "PR_READINESS_STAGE1_COVERAGE_DIGEST.md",
    "PR_READINESS_STAGE1_CONTRADICTION_CHECKLIST.md",
)

DECISION_STATUS_IMPLEMENTATION_READY = "implementation-ready"
DECISION_STATUS_BP1_BRANCH_VISION_REVIEW = "bp1-branch-vision-review"
DECISION_STATUS_BP2_BRANCH_PLAN_REVIEW = "bp2-branch-plan-review"
DECISION_STATUS_BP3_ORCHESTRATION_REVIEW = "bp3-orchestration-review"
DECISION_STATUS_WORKSTREAM_IMPLEMENTATION_APPROVAL_REVIEW = (
    "workstream-implementation-approval-review"
)
DECISION_STATUS_WORKSTREAM_ENTRY_REVIEW = "workstream-entry-final-review"
DECISION_STATUS_HARDENING_REVIEW = "hardening-final-review"
DECISION_STATUS_LIVE_VALIDATION_REVIEW = "live-validation-final-review"
DECISION_STATUS_PR_READINESS_STAGE1_REVIEW = "pr-readiness-stage1-review"
DECISION_STATUS_PR_READINESS_STAGE2_REVIEW = "pr-readiness-stage2-review"
DECISION_STATUS_REPAIR_REVALIDATION = "repair-revalidation"
DECISION_STATUS_UNKNOWN = "unknown"
BRANCH_PLANNING_PACKET_REVIEWABILITY_VALUES = {
    "missing",
    "generated",
    "validation failed",
    "reviewable",
    "stale",
    "superseded",
}
BRANCH_PLANNING_USER_GATE_VALUES = {
    "pending user review",
    "user revision requested",
    "user accepted",
    "user approved",
    "user waived",
    "user rejected",
    "user blocked",
    "superseded",
}
BRANCH_PLANNING_PENDING_USER_GATE_VALUES = {
    "pending user review",
    "user revision requested",
    "user rejected",
    "user blocked",
}
BRANCH_PLANNING_IMPLEMENTATION_REQUEST_MARKERS = (
    "approve complete bounded workstream package implementation",
    "approve complete bounded workstream implementation",
    "complete bounded workstream package implementation",
    "complete bounded workstream implementation",
    "approve bounded workstream package implementation",
    "approve bounded workstream implementation",
    "bounded workstream package implementation",
    "workstream package implementation approval",
    "approve workstream implementation",
    "workstream implementation approval",
    "implementation approval",
)
BRANCH_PLANNING_IMPLEMENTATION_BLOCKING_MARKERS = (
    "implementation remains blocked",
    "implementation not yet authorized",
    "pending separate user approval",
    "pending user approval",
    "implementation approval state: pending",
    "does not authorize workstream implementation",
    "does not request bp3 implementation approval",
    "not a workstream implementation approval",
    "workstream implementation remains pending",
)
FAM006_WORKSTREAM_IMPLEMENTATION_APPROVAL_REVIEW_MARKERS = (
    "prepare the separate bounded workstream/runtime implementation approval packet",
    "workstream implementation approval packet",
    "does user approve bounded fam-006 workstream/runtime implementation",
    "approve bounded fam-006 workstream/runtime implementation",
)
FAM007_WORKSTREAM_PACKAGE_APPROVAL_BRANCHES = {
    "feature/fam-007-dev-owner-skeleton-readiness",
    "feature/fam-007-owner-ai-operational-foundation-gates",
}


def _is_fam006_workstream_implementation_approval_review(
    normalized_decision: str,
    *,
    is_fam006_recording: bool,
) -> bool:
    return (
        is_fam006_recording
        and any(
            marker in normalized_decision
            for marker in FAM006_WORKSTREAM_IMPLEMENTATION_APPROVAL_REVIEW_MARKERS
        )
        and any(
            marker in normalized_decision
            for marker in BRANCH_PLANNING_IMPLEMENTATION_BLOCKING_MARKERS
        )
    )


UNRESOLVED_TEMPLATE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("shell-variable-branch", re.compile(r"(?<![A-Za-z0-9_])\$branch\b")),
    ("shell-variable-head", re.compile(r"(?<![A-Za-z0-9_])\$head\b")),
    ("shell-variable-origin-main", re.compile(r"(?<![A-Za-z0-9_])\$originMain\b")),
    ("shell-variable-packet", re.compile(r"(?<![A-Za-z0-9_])\$packet\b")),
    ("shell-variable-zip", re.compile(r"(?<![A-Za-z0-9_])\$zip\b")),
    ("unevaluated-shell-expression", re.compile(r"\$\([^)\n]+\)")),
)
BUNDLE_COUNT_FIELDS: tuple[str, ...] = (
    "Bundle File Count",
    "Expected File Count",
    "Copied File Count",
    "Extra Bundle File Count",
)
USER_FACING_GENERATED_FILES: tuple[str, ...] = (
    "START_HERE.md",
    USER_BRANCH_VISION_REVIEW_FILE,
    USER_BRANCH_PLAN_REVIEW_FILE,
    PR_READINESS_STAGE1_REVIEW_FILE,
    "USER_REVIEW_FOLDER_AND_FILE_DIGEST.md",
    "GOVERNANCE_REQUIRED_FILES_SCAN.md",
    "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md",
    "BRANCH_VISION_VALIDATION_CHECKLIST.md",
    "PR_READINESS_STAGE1_COVERAGE_DIGEST.md",
    "PR_READINESS_STAGE1_SOURCE_COVERAGE.md",
    "PR_READINESS_STAGE1_CONTRADICTION_CHECKLIST.md",
)
USER_FACING_TECHNICAL_METADATA_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("head-token", re.compile(r"\bHEAD\b", re.IGNORECASE)),
    ("source-head", re.compile(r"\bSource HEAD\b", re.IGNORECASE)),
    ("origin-main", re.compile(r"\borigin/main\b", re.IGNORECASE)),
    ("merge-base", re.compile(r"\bmerge base\b|\bmerge-base\b", re.IGNORECASE)),
    ("ahead-behind", re.compile(r"\bahead/behind\b|\bAhead/Behind\b", re.IGNORECASE)),
    ("zip-hash", re.compile(r"\b(?:ZIP|packet|upload)\s+(?:SHA256|hash)\b", re.IGNORECASE)),
    ("review-export-zip", re.compile(r"\bReview Export Zip\b", re.IGNORECASE)),
    (
        "desktop-onedrive-active-upload",
        re.compile(
            r"(?:\b(?:Desktop|OneDrive)\b[^\n]*(?:active\s+)?(?:upload|review)\s+"
            r"(?:source|path|folder|bundle))|"
            r"(?:(?:upload|review)\s+(?:source|path|folder|bundle)[^\n]*"
            r"\b(?:Desktop|OneDrive)\b)",
            re.IGNORECASE,
        ),
    ),
    ("upstream-field", re.compile(r"^Upstream\s*:", re.IGNORECASE | re.MULTILINE)),
    ("source-branch-field", re.compile(r"^Source Branch\s*:", re.IGNORECASE | re.MULTILINE)),
    ("branch-status", re.compile(r"\bbranch status\b|\bCurrent Branch State\b", re.IGNORECASE)),
    ("validation-status", re.compile(r"\bvalidation status\b|\bValidation Summary\b", re.IGNORECASE)),
    ("pr-state", re.compile(r"\bPR state\b", re.IGNORECASE)),
    ("worktree-status", re.compile(r"\bworktree status\b", re.IGNORECASE)),
    ("sha-like-proof", re.compile(r"\b[0-9a-f]{40}\b", re.IGNORECASE)),
)
MIN_PRIMARY_REVIEW_WORDS = 80
MIN_PRIMARY_REVIEW_CHARACTERS = 500
_FALSE_GREEN_ACCEPTANCE_TARGET = (
    r"(?:USER\s+visual\s+acceptance|USER\s+acceptance|USER\s+accepted|"
    r"product\s+acceptance|product\s+accepted|visual\s+acceptance|"
    r"visual\s+accepted|accepted|acceptance)\b"
)
_FALSE_GREEN_PENDING_NEGATION = (
    r"(?!\s*(?:[,;:.-]\s*)?(?:which\s+)?"
    r"(?:remains|stays|is\s+pending|pending|requires|only\s+after|after|until|separate))"
)
FALSE_GREEN_STALE_ACTIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "stale-dev-owner-skeleton-accepted",
        re.compile(r"Accepted by USER\s*-\s*integrated Option A Dev/Owner Skeleton Readiness", re.IGNORECASE),
    ),
    (
        "stale-dev-owner-skeleton-vision",
        re.compile(r"Dev/Owner Skeleton Readiness Branch Vision", re.IGNORECASE),
    ),
    (
        "stale-governance-pr-readiness-stage-1",
        re.compile(r"Governance\s*/\s*PR Readiness Stage 1|PR Readiness Stage 1 analysis", re.IGNORECASE),
    ),
    (
        "stale-approve-pr-readiness",
        re.compile(r"approve\s+PR Readiness Stage 1|USER\s+approves?\s+PR Readiness Stage 1", re.IGNORECASE),
    ),
    (
        "packet-validation-as-acceptance",
        re.compile(
            r"(?:packet validation|validation pass(?:ed)?)\s+(?:proves|equals|is|means)\s+"
            + _FALSE_GREEN_ACCEPTANCE_TARGET
            + _FALSE_GREEN_PENDING_NEGATION,
            re.IGNORECASE,
        ),
    ),
    (
        "packet-reviewability-as-product-acceptance",
        re.compile(
            r"(?:"
            r"(?:packet reviewability|reviewable packet|reviewable status|reviewability status|packet status)\s+"
            r"(?:proves|equals|is|means)\s+"
            + _FALSE_GREEN_ACCEPTANCE_TARGET
            + _FALSE_GREEN_PENDING_NEGATION
            + r")",
            re.IGNORECASE,
        ),
    ),
    (
        "screenshot-as-visual-acceptance",
        re.compile(
            r"(?:screenshot(?:s|\s+(?:paths?|existence|exists))?\s+"
            r"(?:prove(?:s)?|equals|mean(?:s)?|is|therefore)\s+"
            + _FALSE_GREEN_ACCEPTANCE_TARGET
            + _FALSE_GREEN_PENDING_NEGATION
            + r"|"
            r"screenshot exists therefore accepted)",
            re.IGNORECASE,
        ),
    ),
    (
        "helper-green-as-visual-acceptance",
        re.compile(
            r"(?:(?:helper|validator)(?:\s+(?:output|result|validation))?"
            r"\s+(?:green|pass(?:ed)?)|validation\s+pass(?:ed)?)\s+"
            r"(?:proves|equals|means|is|therefore)\s+"
            + _FALSE_GREEN_ACCEPTANCE_TARGET
            + _FALSE_GREEN_PENDING_NEGATION,
            re.IGNORECASE,
        ),
    ),
    (
        "css-similarity-as-visual-family-proof",
        re.compile(
            r"css(?:\s+marker)?\s+similarity\s+(?:proves|equals|means|is)\s+visual family",
            re.IGNORECASE,
        ),
    ),
    (
        "uiref-citation-as-visual-proof",
        re.compile(
            r"(?:UIREF citation alone is sufficient|reference cited but not compared|"
            r"(?:UIREF|reference)\s+citation\s+(?:alone\s+)?(?:proves|equals|means|is)\s+"
            r"(?:(?:visual|product)\s+)?(?:acceptance|accepted|proof|sufficient)"
            + _FALSE_GREEN_PENDING_NEGATION
            + r")",
            re.IGNORECASE,
        ),
    ),
)
REQUIRED_FAM007_LIVE_PROOF_CHECKS: tuple[str, ...] = (
    "dashboardHubParentOnly",
    "doorwayButtonsDeferredNoFakeActions",
    "parentVisualMetrics",
    "returnedDensityAndButtonPlacementRepaired",
    "returnedTitleSubtitleWrapRepaired",
    "titleDescriptionProseWordWrapProven",
    "titleDescriptionWindowsCursorProseWrapProven",
    "acceptedReferenceComparisonProven",
    "exhaustiveMainRuntimeVisualGrammarComparisonProven",
    "deterministicStatusRowsAndTitlePill",
    "titleStatusPillGroupWrapProven",
    "titleStatusPillNoEarlyWrapAt580Proven",
    "titleStatusPillWindowsCursorWrapProven",
    "deterministicTitleColumnSizingProven",
    "sharedStatusValueColumnProven",
    "fixedColumnGutterAndUniformValueColumnProven",
    "rowStackVerticalGutterProven",
    "windowControlEdgeGutterProven",
    "titleCardBackingLayerRemoved",
    "rowTitleStatusTextSizeParityProven",
    "belowTitleTextWeights720Proven",
    "resizeEdgeHitZoneProven",
    "dashboardHorizontalResizeMinimumWorks",
    "defaultScrollIntentProven",
    "runtimeCopyIsProductFacing",
    "fullDesktopProofNotDuplicated",
    "settingsCogRemovedAndDeferred",
    "settingsOptionBSelectionDispositionProven",
    "noInlineWorkspaceActions",
    "childLifecycleBehavior",
    "dashboardResizeStillWorks",
    "providerExecutionStillBlocked",
)
IMAGE_PROOF_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
FAM007_REQUIRED_LIVE_PROOF_SCREENSHOT_CLASSES = {
    "dashboard_initial",
    "dashboard_scrolled_bottom",
    "dashboard_horizontal_shrink",
    "dashboard_resized",
}
FAM007_LIVE_PROOF_MANIFEST_NAME = "live_resize_manifest.json"
FAM007_UDL_IMAGE_PROOF_IDS = ("F7-UDL-006", "F7-UDL-007", "F7-UDL-016")
USER_BRANCH_PLAN_STALE_BP1_WORDING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "old-product-design-planning-gate",
        re.compile(r"required user-facing product/design planning gate", re.IGNORECASE),
    ),
    (
        "old-do-i-like-prompt",
        re.compile(r"Do I actually like what Codex is about to build", re.IGNORECASE),
    ),
    (
        "old-product-design-contract",
        re.compile(r"USER Branch Plan Contract:\s*a required user-facing product/design", re.IGNORECASE),
    ),
)
BP1_PACKET_STALE_LANGUAGE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "workstream-entry-final-decision-path",
        re.compile(r"workstream entry final decision review", re.IGNORECASE),
    ),
    (
        "bp1-compatibility-status",
        re.compile(r"BP1 Branch Vision Review compatibility status", re.IGNORECASE),
    ),
    (
        "compatibility-digest",
        re.compile(r"compatibility digest", re.IGNORECASE),
    ),
    (
        "must-not-do-heading",
        re.compile(r"##\s*Must-Not-Do\s*/\s*Regression-Risk Rules", re.IGNORECASE),
    ),
    (
        "command-wall-do-not-bullet",
        re.compile(r"^\s*-\s*Do not\b", re.IGNORECASE | re.MULTILINE),
    ),
)
USER_BRANCH_VISION_TEMPLATE_SHELL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "project-context-process-shell",
        re.compile(r"must explain how this branch supports", re.IGNORECASE),
    ),
    (
        "family-context-process-shell",
        re.compile(r"Family Vision Context:\s*This BP1 review asks whether\b", re.IGNORECASE),
    ),
    (
        "project-context-instruction",
        re.compile(r"Review `Docs/nexus_vision\.md`.*before accepting this Branch Vision", re.IGNORECASE),
    ),
    (
        "family-context-instruction",
        re.compile(r"Review the relevant `Docs/family_visions/` owner", re.IGNORECASE),
    ),
    (
        "generic-branch-goal-instruction",
        re.compile(r"Confirm that this branch goal is the right product direction", re.IGNORECASE),
    ),
    (
        "generic-end-state-instruction",
        re.compile(r"Describe the intended user-visible or source-truth end state", re.IGNORECASE),
    ),
    (
        "generic-copied-file-flow",
        re.compile(r"Review the copied branch-specific files and note any changes", re.IGNORECASE),
    ),
    (
        "generic-accept-revise-waive-reject-options",
        re.compile(
            r"Accept the proposed Branch Vision.*Revise the Branch Vision.*Waive BP1.*Reject this branch direction",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "generic-design-question",
        re.compile(r"Does this Branch Vision match what the USER wants this branch to become", re.IGNORECASE),
    ),
    (
        "process-only-accepted-vision-goal",
        re.compile(r"Create an accepted USER-facing branch vision", re.IGNORECASE),
    ),
    (
        "process-only-bp1-closeout",
        re.compile(r"When BP1 closes", re.IGNORECASE),
    ),
    (
        "process-only-bp1-mechanics",
        re.compile(r"BP1 captures", re.IGNORECASE),
    ),
    (
        "process-only-product-options",
        re.compile(
            r"Option A accepts the vision.*option B revises it.*option C waives",
            re.IGNORECASE | re.DOTALL,
        ),
    ),
    (
        "process-only-packet-decision",
        re.compile(r"Use this packet to decide", re.IGNORECASE),
    ),
    (
        "generic-outcome-question",
        re.compile(r"what exact outcome should USER expect to see", re.IGNORECASE),
    ),
    (
        "process-centered-user-hub-packet",
        re.compile(r"USER will see a local USER hub packet", re.IGNORECASE),
    ),
    (
        "process-centered-accepted-bp1-target",
        re.compile(r"The accepted BP1 vision will become the target for BP2", re.IGNORECASE),
    ),
    (
        "process-centered-user-reads-packet",
        re.compile(r"USER reads the FAM-007 packet", re.IGNORECASE),
    ),
)
USER_BRANCH_VISION_MINIMUM_SUBSTANTIVE_SECTIONS: tuple[tuple[str, int], ...] = (
    ("Project Vision Context", 18),
    ("Family Vision Context", 18),
    ("Feature Vision Context", 18),
    ("Branch Goal", 18),
    ("End-State Vision", 20),
    ("What Will I Actually See, And Where Will I See It?", 18),
    ("How It Will Function", 20),
    ("User Experience Flow", 18),
    ("Surface Map", 24),
    ("Product Options / Design Paths", 30),
    ("Codex Recommendations", 36),
    ("Why This Fits The Nexus Vision", 18),
    ("USER Design Questions", 24),
)


@dataclass(frozen=True)
class WorkstreamEntryPacketDecisionPathResult:
    """Machine-readable result for Workstream Entry packet decision-path checks."""

    status: str
    failures: list[str]

    @property
    def implementation_ready(self) -> bool:
        return self.status == DECISION_STATUS_IMPLEMENTATION_READY and not self.failures

    @property
    def blocks_implementation(self) -> bool:
        return self.status in {
            DECISION_STATUS_BP1_BRANCH_VISION_REVIEW,
            DECISION_STATUS_BP2_BRANCH_PLAN_REVIEW,
            DECISION_STATUS_BP3_ORCHESTRATION_REVIEW,
            DECISION_STATUS_WORKSTREAM_IMPLEMENTATION_APPROVAL_REVIEW,
            DECISION_STATUS_WORKSTREAM_ENTRY_REVIEW,
            DECISION_STATUS_HARDENING_REVIEW,
            DECISION_STATUS_LIVE_VALIDATION_REVIEW,
            DECISION_STATUS_PR_READINESS_STAGE1_REVIEW,
            DECISION_STATUS_PR_READINESS_STAGE2_REVIEW,
            DECISION_STATUS_REPAIR_REVALIDATION,
            DECISION_STATUS_UNKNOWN,
        }


@dataclass(frozen=True)
class LocalUserPacketValidationResult:
    """Machine-readable result for local USER hub folder/ZIP validation."""

    packet_dir: Path
    export_zip: Path
    label: str
    validation_mode: str
    folder_file_count: int
    zip_file_count: int
    primary_user_review_files: tuple[str, ...]
    failures: list[str]


def _desktop_path() -> Path:
    if os.name != "nt":
        raise RuntimeError(
            "The local USER hub path is Windows-only: "
            f"{WINDOWS_USER_HUB_ROOT_TEXT}. Run this helper from Windows so "
            "review packets stay outside the repo worktree."
        )
    if not DEFAULT_USER_HUB_ROOT.is_absolute():
        raise RuntimeError(
            "The local USER hub root must be an absolute filesystem path: "
            f"{WINDOWS_USER_HUB_ROOT_TEXT}"
        )
    return DEFAULT_USER_HUB_ROOT


def _sanitize_folder_name(name: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*]+', "_", name).strip(" .")
    sanitized = re.sub(r"\s+", " ", sanitized)
    if not sanitized:
        raise ValueError("Review bundle folder name is empty after sanitization")
    return sanitized


def _worktree_label(explicit_label: str | None) -> str:
    if explicit_label:
        return _sanitize_folder_name(explicit_label)
    return _sanitize_folder_name(ROOT.name)


def _safe_target(desktop: Path, review_root_name: str, worktree_label: str) -> tuple[Path, Path]:
    if not desktop.is_absolute():
        raise ValueError(f"Local USER hub root must be absolute: {desktop}")
    if review_root_name:
        review_root = (desktop / _sanitize_folder_name(review_root_name)).resolve()
    else:
        review_root = desktop.resolve()
    target = (review_root / _sanitize_folder_name(worktree_label)).resolve()
    desktop_resolved = desktop.resolve()
    if review_root != desktop_resolved and desktop_resolved not in review_root.parents:
        raise ValueError(f"Refusing to write review root outside local USER hub: {review_root}")
    if target == review_root or review_root not in target.parents:
        raise ValueError(f"Refusing to write outside local USER hub: {target}")
    return review_root, target


def _clear_readonly(function, path: str, _exc_info) -> None:
    os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    function(path)


def _clear_target(target: Path) -> None:
    raise RuntimeError("Retired publication mutation route; use the installed selected USER publication owner.")
    try:
        shutil.rmtree(target, onexc=_clear_readonly)
    except TypeError:
        shutil.rmtree(target, onerror=_clear_readonly)


def _flat_copy_name(relative_file: str) -> str:
    normalized = Path(relative_file).as_posix().replace("\\", "/")
    return normalized.replace("/", "__")


def _copy_names(files: list[str]) -> list[str]:
    basename_counts = Counter(Path(file_name).name for file_name in files)
    names: list[str] = []
    used: set[str] = set()
    for file_name in files:
        basename = Path(file_name).name
        copy_name = basename if basename_counts[basename] == 1 else _flat_copy_name(file_name)
        if copy_name in used:
            copy_name = _flat_copy_name(file_name)
        if copy_name in used:
            raise ValueError(f"Review bundle filename collision: {copy_name}")
        used.add(copy_name)
        names.append(copy_name)
    return names


def _copy_file(
    relative_file: str,
    target: Path,
    copy_name: str,
    *,
    subdir: str | None = None,
) -> tuple[str, str]:
    source = (ROOT / relative_file).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Review source file not found: {relative_file}")
    if ROOT.resolve() not in source.parents:
        raise ValueError(f"Review source file is outside repo: {relative_file}")

    destination = target / subdir / copy_name if subdir else target / copy_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return source.relative_to(ROOT).as_posix(), destination.relative_to(target).as_posix()


def _git_output(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "UNKNOWN"


def _markdown_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- None recorded."]
    return [f"- {item}" for item in items]


def _extract_marker_from_text(text: str, marker: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(marker)}\s*(.+)$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1].strip()
    return value or None


def _source_marker(relative_file: str, marker: str) -> str | None:
    source = (ROOT / relative_file).resolve()
    if not source.is_file() or ROOT.resolve() not in source.parents:
        return None
    return _extract_marker_from_text(source.read_text(encoding="utf-8"), marker)


def _bundle_files(target: Path) -> set[Path]:
    return {path for path in target.rglob("*") if path.is_file()}


def _packet_file_basename(file_name: str) -> str:
    return PurePosixPath(file_name.replace("\\", "/")).name


def _packet_file_items(
    packet_files: Mapping[str, str],
    file_name: str,
) -> list[tuple[str, str]]:
    matches = [
        (path, text)
        for path, text in sorted(packet_files.items())
        if _packet_file_basename(path) == file_name
    ]
    preferred_paths = (
        file_name,
        f"USER Review/{file_name}",
        f"{REVIEW_AIDS_DIR_NAME}/{file_name}",
    )

    def sort_key(item: tuple[str, str]) -> tuple[int, str]:
        path = item[0].replace("\\", "/")
        if path in preferred_paths:
            return (preferred_paths.index(path), path)
        if path.startswith(f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/"):
            return (10, path)
        return (5, path)

    return sorted(matches, key=sort_key)


def _packet_file_text(packet_files: Mapping[str, str], file_name: str) -> str:
    if file_name in packet_files:
        return packet_files[file_name]
    matches = _packet_file_items(packet_files, file_name)
    return matches[0][1] if matches else ""


def _packet_file_path(packet_files: Mapping[str, str], file_name: str) -> str:
    if file_name in packet_files:
        return file_name
    matches = _packet_file_items(packet_files, file_name)
    return matches[0][0] if matches else file_name


def _packet_file_present(packet_files: Mapping[str, str], file_name: str) -> bool:
    return bool(_packet_file_text(packet_files, file_name))


def _primary_user_review_file(
    exact_user_decision: str,
    *,
    source_branch: str | None = None,
    stage1_outcome: str | None = None,
) -> str:
    normalized = re.sub(r"\s+", " ", exact_user_decision).casefold()
    if source_branch and (
        _is_dev_owner_live_validation_lv1_packet(source_branch, normalized)
        or _is_fam007_breakpoint2_live_validation_lv1_packet(
            source_branch=source_branch,
            normalized_decision=normalized,
        )
    ):
        return USER_BRANCH_PLAN_REVIEW_FILE
    if (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
        and re.search(r"\bpr readiness stage 2\b", normalized)
    ):
        return "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    # A green Stage 1 packet normally carries the exact Stage 2 approval text
    # as its next USER decision. Keep the current-gate artifact primary rather
    # than letting the later-stage wording fall through to the BP2 selector.
    if (
        stage1_outcome == PR_STAGE1_OUTCOME_READY
        and re.search(r"\bpr readiness stage 2\b", normalized)
    ):
        return PR_READINESS_STAGE1_REVIEW_FILE
    stage_patterns = (
        (
            PR_READINESS_STAGE1_REVIEW_FILE,
            0,
            (r"\bpr readiness stage 1\b",),
        ),
        (
            "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md",
            1,
            (
                r"\bbp3\b",
                r"\borchestration\b",
                r"\bworkstream entry\b",
                r"\bworkstream package implementation\b",
                r"\bbounded workstream package\b",
                r"\bworkstream implementation\b",
                r"\bimplementation approval\b",
            ),
        ),
        (USER_BRANCH_PLAN_REVIEW_FILE, 2, (r"\bbp2\b", r"\bbranch plan\b")),
        (USER_BRANCH_VISION_REVIEW_FILE, 3, (r"\bbp1\b", r"\bbranch vision\b")),
    )
    action_match = re.search(
        r"\b(?:approve|approves|approved|approval|green-light|greenlight)\b",
        normalized,
    )
    if action_match:
        action_text = normalized[action_match.start() :]
        requested_matches: list[tuple[int, int, str]] = []
        for file_name, priority, patterns in stage_patterns:
            for pattern in patterns:
                match = re.search(pattern, action_text)
                if match:
                    requested_matches.append((match.start(), priority, file_name))
        if requested_matches:
            return sorted(requested_matches)[0][2]

    matches: list[tuple[int, int, str]] = []
    for file_name, priority, patterns in stage_patterns:
        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                matches.append((match.start(), priority, file_name))
    if matches:
        return sorted(matches)[0][2]
    return USER_BRANCH_PLAN_REVIEW_FILE


def _move_primary_user_review_file(
    *,
    target: Path,
    review_aids_dir: Path,
    user_review_dir: Path,
    primary_file_name: str,
) -> Path:
    source = review_aids_dir / primary_file_name
    if not source.is_file():
        source = target / primary_file_name
    if not source.is_file():
        raise FileNotFoundError(f"Primary USER review file was not generated: {primary_file_name}")
    destination = user_review_dir / primary_file_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.move(str(source), str(destination))
    return destination.resolve()


def _timestamped_zip_stamp(created_at: datetime) -> str:
    return created_at.strftime("%Y%m%d-%H%M%S")


def _export_zip_path(review_root: Path, label: str, created_at: datetime) -> Path:
    stamp = _timestamped_zip_stamp(created_at)
    return (review_root / f"{_sanitize_folder_name(label)}-{stamp}.zip").resolve()


def _legacy_stable_export_zip_path(review_root: Path, label: str) -> Path:
    return (review_root / f"{_sanitize_folder_name(label)}.zip").resolve()


def _remove_stale_same_label_export_zips(review_root: Path, label: str, export_zip: Path) -> None:
    raise RuntimeError("Retired publication mutation route; use the installed selected USER publication owner.")
    safe_label = _sanitize_folder_name(label)
    timestamped_name = re.compile(rf"^{re.escape(safe_label)}-\d{{8}}-\d{{6}}\.zip$")
    candidates = [_legacy_stable_export_zip_path(review_root, label)]
    candidates.extend(
        path.resolve()
        for path in review_root.glob("*.zip")
        if timestamped_name.fullmatch(path.name)
    )
    for candidate in sorted(set(candidates)):
        if candidate == export_zip:
            continue
        if candidate.exists():
            if not candidate.is_file():
                raise ValueError(f"Refusing to remove non-file stale review zip path: {candidate}")
            candidate.unlink()


def _remove_legacy_stable_export_zip(review_root: Path, label: str) -> None:
    legacy_zip = _legacy_stable_export_zip_path(review_root, label)
    if legacy_zip.exists():
        if not legacy_zip.is_file():
            raise ValueError(f"Refusing to remove non-file legacy review zip path: {legacy_zip}")
        legacy_zip.unlink()


def _timestamped_export_zip_name_failures(export_zip: Path, expected_label: str) -> list[str]:
    safe_label = re.escape(_sanitize_folder_name(expected_label))
    pattern = re.compile(rf"^{safe_label}-\d{{8}}-\d{{6}}\.zip$")
    if pattern.fullmatch(export_zip.name):
        return []
    return [
        "Review export zip filename must include the creation timestamp: "
        f"expected {_sanitize_folder_name(expected_label)}-YYYYMMDD-HHMMSS.zip, "
        f"got {export_zip.name}"
    ]


def _write_export_zip(target: Path, export_zip: Path) -> None:
    raise RuntimeError("Retired publication mutation route; use the installed selected USER publication owner.")
    if target in export_zip.parents or export_zip == target:
        raise ValueError(f"Refusing to write review zip inside bundle folder: {export_zip}")
    export_zip.parent.mkdir(parents=True, exist_ok=True)
    temp_zip = export_zip.with_name(f".{export_zip.name}.{os.getpid()}.tmp")
    if temp_zip.exists():
        temp_zip.unlink()
    try:
        with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(_bundle_files(target)):
                archive.write(path, path.relative_to(target).as_posix())
        temp_zip.replace(export_zip)
    except Exception:
        if temp_zip.exists():
            temp_zip.unlink()
        raise


def _start_here_contract_failures(start_here: str) -> list[str]:
    failures: list[str] = []
    if "Review Purpose:" not in start_here:
        failures.append("Review export zip is missing Review Purpose in START_HERE.md")
    if "USER Decision This Packet Supports:" not in start_here:
        failures.append("Review export zip is missing USER Decision This Packet Supports in START_HERE.md")
    return failures


def _validate_export_zip(
    export_zip: Path,
    *,
    source_branch: str,
    source_head: str,
    origin_main: str,
    expected_label: str,
    expected_entries: set[str],
) -> None:
    name_failures = _timestamped_export_zip_name_failures(export_zip, expected_label)
    if name_failures:
        raise ValueError(
            "Review export zip filename validation failed:\n"
            + "\n".join(f"- {failure}" for failure in name_failures)
        )
    packet_files: dict[str, str] = {}
    packet_binary_files: dict[str, bytes] = {}
    with zipfile.ZipFile(export_zip, "r") as archive:
        entries = {entry.filename for entry in archive.infolist() if not entry.is_dir()}
        try:
            start_here = archive.read("START_HERE.md").decode("utf-8")
        except KeyError as exc:
            raise ValueError(f"Review export zip is missing START_HERE.md: {export_zip}") from exc
        for entry in sorted(entries):
            packet_binary_files[entry] = archive.read(entry)
            try:
                packet_files[entry] = packet_binary_files[entry].decode("utf-8")
            except UnicodeDecodeError:
                continue
    stage1_packet = (
        f"{USER_REVIEW_DIR_NAME}/{PR_READINESS_STAGE1_REVIEW_FILE}" in start_here
    )
    if stage1_packet:
        if not _packet_file_text(packet_files, PR_READINESS_STAGE1_REVIEW_FILE):
            raise ValueError(
                f"Review export zip is missing {PR_READINESS_STAGE1_REVIEW_FILE}: {export_zip}"
            )
        for support_file in (
            f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_VISION_REVIEW_FILE}",
            f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_PLAN_REVIEW_FILE}",
        ):
            if support_file not in packet_files or not packet_files[support_file].strip():
                raise ValueError(
                    f"Review export zip is missing Stage 1 supporting planning context: {support_file}"
                )
    else:
        user_vision = _packet_file_text(packet_files, USER_BRANCH_VISION_REVIEW_FILE)
        if not user_vision:
            raise ValueError(
                f"Review export zip is missing {USER_BRANCH_VISION_REVIEW_FILE}: {export_zip}"
            )
        user_review = _packet_file_text(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
        if not user_review:
            raise ValueError(
                f"Review export zip is missing {USER_BRANCH_PLAN_REVIEW_FILE}: {export_zip}"
            )
    if entries != expected_entries:
        missing = sorted(expected_entries - entries)
        extra = sorted(entries - expected_entries)
        raise ValueError(
            "Review export zip file-list guard failed: "
            f"missing={missing or 'none'} extra={extra or 'none'}"
        )
    generated_packet_files = {
        name: text
        for name, text in packet_files.items()
        if not name.startswith(f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/")
    }
    artifact_failures = [
        *_unresolved_template_placeholder_failures(generated_packet_files),
        *_packet_identity_failures(
            packet_files,
            packet_binary_files=packet_binary_files,
            expected_branch=source_branch,
            expected_head=source_head,
            expected_origin_main=origin_main,
        ),
        *_packet_count_consistency_failures(
            packet_files,
            actual_file_count=len(entries),
        ),
        *_user_facing_technical_metadata_failures(generated_packet_files),
        *_user_branch_plan_stale_bp1_wording_failures(generated_packet_files),
        *_fam007_dev_owner_lv1_substantive_failures(generated_packet_files),
        *_fam007_bp2_plan_substantive_failures(generated_packet_files),
        *_fam007_bp2_support_bp1_context_failures(generated_packet_files),
        *_bp1_packet_phase_language_failures(generated_packet_files),
        *_fam006_bp3_support_context_failures(generated_packet_files),
        *_user_branch_vision_substantive_failures(generated_packet_files),
        *_branch_planning_review_gate_state_failures(generated_packet_files),
        *_pr_stage1_review_failures(generated_packet_files),
        *_pr_stage1_packet_coherence_failures(generated_packet_files),
        *_pr_stage1_source_coverage_failures(
            packet_files,
            packet_entries=entries,
        ),
    ]
    if artifact_failures:
        raise ValueError(
            "Review export zip artifact validation failed:\n"
            + "\n".join(f"- {failure}" for failure in artifact_failures)
        )
    start_here_contract_failures = _start_here_contract_failures(start_here)
    if start_here_contract_failures:
        raise ValueError(
            "Review export zip START_HERE contract validation failed:\n"
            + "\n".join(f"- {failure}" for failure in start_here_contract_failures)
        )
    if stage1_packet:
        return
    for required_heading in (
        "## Review Status",
        "## Contract Status",
        "## Packet Reviewability State",
        "## USER Gate State",
        "## Contract Revision",
        "## Project Vision Context",
        "## Family Vision Context",
        "## Feature Vision Context",
        "## Branch Goal",
        "## End-State Vision",
        "## What Will I Actually See, And Where Will I See It?",
        "## How It Will Function",
        "## User Experience Flow",
        "## Surface Map",
        "## Product Options / Design Paths",
        "## Codex Recommendations",
        "## Why This Fits The Nexus Vision",
        "## USER Design Questions",
        "## USER Response",
        "## Codex Digest",
        "## USER Response Proof",
        "## USER Response Digested",
        "## Accepted Branch Vision",
        "## Family-Vision Versus Branch-Only Vision Impact",
        "## Must-Have Behavior",
        "## Future-Gated Decisions And Regression-Risk Controls",
        "## Deferred And Future-Gated Ideas",
        "## Vision Question Queue",
        "## Design Assumption Ledger",
        "## Acceptance / Revision / Rejection / Waiver Decision",
    ):
        if required_heading not in user_vision:
            raise ValueError(
                f"Review export zip USER_BRANCH_VISION_REVIEW.md is missing {required_heading}"
            )
    for required_heading in (
        "## Contract Status",
        "## Packet Reviewability State",
        "## USER Gate State",
        "## USER Response Proof",
        "## USER Response Digested",
        "## Acceptance / Waiver / Revision / Rejection Receipt",
        "## Contract Version / Revision",
        "## Plain-English Branch Summary",
        "## What Will I Actually See, And Where Will I See It?",
        "## End-State Vision",
        "## Visual / Functional Walkthrough",
        "## Surface Map",
        "## Implementation Options",
        "## Recommended Direction",
        "## Why This Fits The Nexus Vision",
        "## USER Plan Review Decision",
        "## USER Decisions Needed",
        "## USER Response",
        "## Codex Response Digest",
        "## Implementation Constraints Created By USER Response",
        "## USER Rejected / Deferred Ideas",
        "## Vision Delta / Source-Truth Impact",
        "## Contract Change Log",
        "## Current Branch Scope",
        "## Future-Gated Scope",
        "## Implementation Staging Notes",
        "## Workstream Entry Result",
        "## Contract Completion Checklist",
    ):
        if required_heading not in user_review:
            raise ValueError(
                f"Review export zip USER_BRANCH_PLAN_REVIEW.md is missing {required_heading}"
            )
    contract_status = _section(user_review, "Contract Status").strip().casefold()
    if not any(
        contract_status.startswith(prefix)
        for prefix in (
            "draft",
            "pending user response",
            "pending codex digest",
            "pending user confirmation",
            "future preview only",
            "complete",
            "waived by user",
        )
    ):
        raise ValueError(
            "Review export zip USER_BRANCH_PLAN_REVIEW.md has invalid Contract Status"
        )
    exact_decision = _section(user_review, "Exact USER Decision Supported").casefold()
    if contract_status.startswith(
        (
            "draft",
            "pending user response",
            "pending codex digest",
            "pending user confirmation",
            "future preview only",
        )
    ) and (
        "approve bounded slc" in exact_decision
        or "approve workstream implementation" in exact_decision
        or "implementation approval" in exact_decision
    ):
        raise ValueError(
            "Review export zip cannot request implementation approval while "
            "USER_BRANCH_PLAN_REVIEW.md Contract Status is blocking"
        )


def _packet_text_files(packet_dir: Path) -> dict[str, str]:
    packet_files: dict[str, str] = {}
    for path in sorted(_bundle_files(packet_dir)):
        if path.suffix.lower() not in {".md", ".txt", ".json"}:
            continue
        packet_files[path.relative_to(packet_dir).as_posix()] = path.read_text(
            encoding="utf-8"
        )
    return packet_files


def _zip_text_files(export_zip: Path) -> dict[str, str]:
    packet_files: dict[str, str] = {}
    with zipfile.ZipFile(export_zip) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            if PurePosixPath(name).suffix.lower() not in {".md", ".txt", ".json"}:
                continue
            packet_files[name] = archive.read(info).decode("utf-8")
    return packet_files


def _packet_binary_files(packet_dir: Path) -> dict[str, bytes]:
    return {
        path.relative_to(packet_dir).as_posix(): path.read_bytes()
        for path in sorted(_bundle_files(packet_dir))
    }


def _zip_binary_files(export_zip: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(export_zip) as archive:
        return {
            info.filename.replace("\\", "/"): archive.read(info)
            for info in archive.infolist()
            if not info.is_dir()
        }


def _primary_review_substantive_failures(
    packet_files: Mapping[str, str],
    primary_files: tuple[str, ...],
) -> list[str]:
    if len(primary_files) != 1:
        return []
    primary_path = primary_files[0]
    text = packet_files.get(primary_path, "")
    stripped = text.strip()
    failures: list[str] = []
    if not stripped:
        return [f"{primary_path}: primary USER review file is empty"]
    if len(stripped) < MIN_PRIMARY_REVIEW_CHARACTERS or _review_word_count(stripped) < MIN_PRIMARY_REVIEW_WORDS:
        failures.append(
            f"{primary_path}: primary USER review file is not meaningful enough for a current-gate decision "
            f"(requires at least {MIN_PRIMARY_REVIEW_WORDS} words and {MIN_PRIMARY_REVIEW_CHARACTERS} characters)"
        )
    if "## " not in stripped:
        failures.append(f"{primary_path}: primary USER review file must include decision-section headings")

    start_here = packet_files.get("START_HERE.md", "")
    if start_here and primary_path not in start_here:
        failures.append(f"START_HERE.md: does not identify the primary USER review file {primary_path}")

    gate_match = re.search(r"^Current Gate:\s*`?([^`\n]+)`?\s*$", start_here, re.MULTILINE)
    if gate_match:
        gate_words = {
            word
            for word in re.findall(r"[A-Za-z0-9]+", gate_match.group(1).casefold())
            if len(word) >= 4
            and word not in {"current", "gate", "user", "review", "packet", "after", "with"}
        }
        primary_words = set(re.findall(r"[A-Za-z0-9]+", stripped.casefold()))
        missing_gate_words = sorted(gate_words - primary_words)
        if len(gate_words) >= 3 and len(missing_gate_words) > max(1, len(gate_words) // 2):
            failures.append(
                f"{primary_path}: primary USER review file does not match START_HERE.md Current Gate "
                f"(missing gate terms: {', '.join(missing_gate_words)})"
            )
    return failures


def _is_pr_stage1_packet_posture(packet_files: Mapping[str, str]) -> bool:
    """Detect Stage 1 from the current-gate route, not only the primary file."""

    start_here = packet_files.get("START_HERE.md", "")
    primary_marker = f"{USER_REVIEW_DIR_NAME}/{PR_READINESS_STAGE1_REVIEW_FILE}"
    if primary_marker in start_here:
        return True
    current_gate = re.sub(
        r"\s+",
        " ",
        _field_value(start_here, "Current Gate"),
    ).casefold()
    decision_path = re.sub(
        r"\s+",
        " ",
        _field_value(start_here, "Decision Path Summary"),
    ).casefold()
    current_gate_is_stage1 = bool(
        re.search(r"\bpr readiness stage\s*1\b", current_gate)
        or re.search(r"\bstage\s*1 ready for stage\s*2\b", current_gate)
    )
    decision_path_is_stage1 = bool(
        re.search(r"\bpr readiness stage\s*1\b", decision_path)
        and re.search(r"\b(?:approval|repair) review\b", decision_path)
    )
    return current_gate_is_stage1 or decision_path_is_stage1


def _pr_stage1_review_failures(packet_files: Mapping[str, str]) -> list[str]:
    """Validate the dedicated PR Readiness Stage 1 current-gate artifact."""

    start_here = packet_files.get("START_HERE.md", "")
    primary_marker = f"{USER_REVIEW_DIR_NAME}/{PR_READINESS_STAGE1_REVIEW_FILE}"
    if not _is_pr_stage1_packet_posture(packet_files):
        return []
    failures: list[str] = []
    if primary_marker not in start_here:
        failures.append(
            "START_HERE.md: PR Stage 1 packet must identify "
            f"{primary_marker} as the primary USER review file"
        )
    text = _packet_file_text(packet_files, PR_READINESS_STAGE1_REVIEW_FILE)
    display_name = _packet_file_path(packet_files, PR_READINESS_STAGE1_REVIEW_FILE)
    if not text:
        failures.append(f"{display_name}: PR Readiness Stage 1 primary artifact is missing")
        return failures
    for heading in (
        "## Review Status",
        "## Contract Status",
        "## Packet Reviewability State",
        "## USER Gate State",
        "## Current-Gate Purpose",
        "## Scope And Authority",
        "## Transition-Safety Review",
        "## Adversarial And False-Green Review",
        "## Stage 1 Outcome",
        "## Exact USER Decision Supported",
    ):
        if heading not in text:
            failures.append(f"{display_name}: PR Stage 1 artifact is missing {heading}")
    for support_file in (
        f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_VISION_REVIEW_FILE}",
        f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_PLAN_REVIEW_FILE}",
    ):
        if not packet_files.get(support_file, "").strip():
            failures.append(
                f"{support_file}: Stage 1 supporting planning context is missing"
            )
    normalized = text.casefold()
    if "pr readiness stage 1 repair required" not in normalized and "stage 1 ready for stage 2" not in normalized:
        failures.append(
            f"{display_name}: PR Stage 1 artifact is missing an allowed Stage 1 outcome"
        )
    if "bp2 branch plan contract" in normalized and "supporting planning context" not in normalized:
        failures.append(
            f"{display_name}: PR Stage 1 artifact presents BP2 as the current-gate contract"
        )
    if f"{USER_REVIEW_DIR_NAME}/{USER_BRANCH_PLAN_REVIEW_FILE}" in start_here:
        failures.append(
            "START_HERE.md: PR Stage 1 packet still identifies the BP2 Branch Plan file as primary"
        )
    return failures


def _pr_stage1_packet_coherence_failures(packet_files: Mapping[str, str]) -> list[str]:
    """Reject mixed current-gate language in a PR Stage 1 packet."""

    start_here = packet_files.get("START_HERE.md", "")
    primary_marker = f"{USER_REVIEW_DIR_NAME}/{PR_READINESS_STAGE1_REVIEW_FILE}"
    if not _is_pr_stage1_packet_posture(packet_files):
        return []
    failures: list[str] = []
    if primary_marker not in start_here:
        failures.append(
            "PR Stage 1 packet: START_HERE.md identifies a different primary "
            f"USER review file; expected {primary_marker}"
        )
    primary = _packet_file_text(packet_files, PR_READINESS_STAGE1_REVIEW_FILE)
    if not primary:
        return failures
    summary = _field_value(start_here, "Decision Path Summary")
    normalized_summary = re.sub(r"\s+", " ", summary).casefold()
    normalized_primary = re.sub(r"\s+", " ", primary).casefold()
    expected_summary_phrase = (
        "pr readiness stage1 repair review"
        if "pr readiness stage 1 repair required" in normalized_primary
        else "pr readiness stage1 approval review"
    )
    stage1_ready = "stage 1 ready for stage 2" in normalized_primary
    if expected_summary_phrase not in normalized_summary:
        failures.append(
            "START_HERE.md: Stage 1 packet Decision Path Summary must identify the "
            f"current Stage 1 posture ({expected_summary_phrase})"
        )
    if "stage 1 ready for stage 2" in normalized_primary:
        if "stage 1 ready for stage 2" not in normalized_summary:
            failures.append(
                "START_HERE.md: Decision Path Summary does not match the primary "
                "Stage 1 Ready For Stage 2 outcome"
            )
    if re.search(r"workstream\s+entry|workstream\s+implementation", normalized_summary):
        failures.append(
            "START_HERE.md: Workstream Entry or implementation is presented as the "
            "current Stage 1 decision path"
        )
    if re.search(
        r"(?:primary|active|current\s+(?:decision|gate)).{0,100}"
        r"(?:user_branch_plan_review\.md|user_branch_vision_review\.md|"
        r"workstream_entry_analysis_digest\.md)",
        normalized_summary + " " + normalized_primary,
    ):
        failures.append(
            "PR Stage 1 packet: a BP or Workstream artifact is named as the "
            "primary/current decision surface"
        )

    support_files = {
        name: text
        for name, text in packet_files.items()
        if name.startswith(f"{REVIEW_AIDS_DIR_NAME}/")
    }
    stage1_planning_support_files = {
        f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_VISION_REVIEW_FILE}",
        f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_PLAN_REVIEW_FILE}",
    }
    for file_name, text in sorted(support_files.items()):
        normalized = re.sub(r"\s+", " ", text).casefold()
        if re.search(r"decision path\s*:\s*workstream\s+entry", normalized):
            failures.append(
                f"{file_name}: active Workstream Entry decision path conflicts with PR Stage 1"
            )
        if re.search(
            r"(?:primary|active|current\s+(?:decision|gate)).{0,100}"
            r"(?:user_branch_plan_review\.md|user_branch_vision_review\.md|"
            r"workstream_entry_analysis_digest\.md)",
            normalized,
        ):
            failures.append(
                f"{file_name}: names a BP or Workstream artifact as the current decision file"
            )
        if re.search(
            r"(?:bp1|bp2|bp3).{0,80}(?:remains?\s+pending|pending\s+user|"
            r"pending\s+acceptance|pending\s+review)",
            normalized,
        ):
            failures.append(
                f"{file_name}: presents a BP gate as the active pending gate in a Stage 1 packet"
            )
        if (
            stage1_ready
            and file_name not in stage1_planning_support_files
            and re.search(
                r"(?:approve|begin|start|request).{0,80}pr\s+readiness\s+stage\s*1",
                normalized,
            )
        ):
            failures.append(
                f"{file_name}: requests or recommends Stage 1 after Stage 1 completion"
            )
    return failures


def _pr_stage1_source_coverage_failures(
    packet_files: Mapping[str, str],
    *,
    packet_entries: set[str] | None = None,
) -> list[str]:
    """Ensure the Stage 1 source-coverage aid matches the copied file set."""

    if not _is_pr_stage1_packet_posture(packet_files):
        return []
    failures: list[str] = []
    coverage_name = f"{REVIEW_AIDS_DIR_NAME}/PR_READINESS_STAGE1_SOURCE_COVERAGE.md"
    coverage = packet_files.get(coverage_name, "")
    if not coverage:
        return [f"{coverage_name}: Stage 1 source-coverage aid is missing"]
    actual = {
        name
        for name in (packet_entries if packet_entries is not None else packet_files)
        if name.startswith(f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/")
    }
    listed = set(
        re.findall(
            rf"`({re.escape(SOURCE_TRUTH_CONTEXT_DIR_NAME)}/[^`\n]+)`",
            coverage,
        )
    )
    missing = sorted(actual - listed)
    extra = sorted(listed - actual)
    if missing:
        failures.append(
            f"{coverage_name}: copied source files missing from coverage list: "
            + ", ".join(missing)
        )
    if extra:
        failures.append(
            f"{coverage_name}: coverage list claims absent files: " + ", ".join(extra)
        )
    count_match = re.search(r"Copied Source Count:\s*`?(\d+)`?", coverage)
    if count_match and int(count_match.group(1)) != len(actual):
        failures.append(
            f"{coverage_name}: Copied Source Count does not match the packet "
            f"({count_match.group(1)} vs {len(actual)})"
        )
    return failures


def _active_review_aid_false_green_failures(packet_files: Mapping[str, str]) -> list[str]:
    failures: list[str] = []
    primary_paths = {
        name
        for name in packet_files
        if name.startswith(f"{USER_REVIEW_DIR_NAME}/")
    }
    primary_names = {_packet_file_basename(name) for name in primary_paths}
    primary_name = next(iter(primary_names), "")
    user_facing_prefixes = (
        "START_HERE.md",
        f"{USER_REVIEW_DIR_NAME}/",
        f"{REVIEW_AIDS_DIR_NAME}/",
    )
    start_here = packet_files.get("START_HERE.md", "")
    stage1_pending_marker = re.search(
        r"(?:PR\s+Readiness\s+Stage\s+1\s+analysis\s+remains\s+pending\s+USER\s+approval|"
        r"Stage\s+1\s+remains\s+in\s+repair-required\s+posture|"
        r"Stage\s+1\s+Outcome\s*:\s*PR\s+Readiness\s+Stage\s+1\s+Repair\s+Required)",
        start_here,
        re.IGNORECASE,
    )
    stage1_blocked_transition = re.search(
        r"(?:does\s+not\s+authorize|remains\s+separately\s+gated).*"
        r"(?:PR\s+Stage\s+2|PR\s+creation|merge|release)|"
        r"Stage\s+2\s+is\s+not\s+supported",
        start_here,
        re.IGNORECASE | re.DOTALL,
    )
    stage1_repair_primary = bool(
        primary_name == PR_READINESS_STAGE1_REVIEW_FILE
        and re.search(
            r"PR\s+Readiness\s+Stage\s+1\s+Repair\s+Required",
            _packet_file_text(packet_files, PR_READINESS_STAGE1_REVIEW_FILE),
            re.IGNORECASE,
        )
    )
    stage1_pending_posture = bool(
        stage1_pending_marker
        and stage1_blocked_transition
        and not re.search(
            r"PR\s+Readiness\s+Stage\s+1\s+(?:accepted|approved|complete|green)",
            start_here,
            re.IGNORECASE,
        )
    ) or stage1_repair_primary
    stage1_current_posture = stage1_pending_posture or bool(
        primary_name == PR_READINESS_STAGE1_REVIEW_FILE
        and re.search(
            r"Stage\s+1\s+Ready\s+For\s+Stage\s+2",
            _packet_file_text(packet_files, PR_READINESS_STAGE1_REVIEW_FILE),
            re.IGNORECASE,
        )
    )
    stage1_current_artifacts = {
        "START_HERE.md",
        f"{USER_REVIEW_DIR_NAME}/{PR_READINESS_STAGE1_REVIEW_FILE}",
        f"{REVIEW_AIDS_DIR_NAME}/PR_READINESS_STAGE1_COVERAGE_DIGEST.md",
        f"{REVIEW_AIDS_DIR_NAME}/PR_READINESS_STAGE1_SOURCE_COVERAGE.md",
        f"{REVIEW_AIDS_DIR_NAME}/PR_READINESS_STAGE1_CONTRADICTION_CHECKLIST.md",
        f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_VISION_REVIEW_FILE}",
        f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_PLAN_REVIEW_FILE}",
    }
    for file_name, text in sorted(packet_files.items()):
        normalized = file_name.replace("\\", "/")
        if not (
            normalized == user_facing_prefixes[0]
            or normalized.startswith(user_facing_prefixes[1])
            or normalized.startswith(user_facing_prefixes[2])
        ):
            continue
        for reason, pattern in FALSE_GREEN_STALE_ACTIVE_PATTERNS:
            if stage1_pending_posture and reason in {
                "stale-governance-pr-readiness-stage-1",
                "stale-approve-pr-readiness",
            }:
                continue
            if reason == "stale-governance-pr-readiness-stage-1" and stage1_current_posture:
                normalized_file = file_name.replace("\\", "/")
                if normalized_file in stage1_current_artifacts:
                    continue
                if re.search(
                    r"\b(?:historical|accepted\s+context|not\s+applicable|"
                    r"receipt[- ]only)\b",
                    text,
                    re.IGNORECASE,
                ) and not re.search(
                    r"\b(?:approve|begin|start|request|remains?\s+pending)\b",
                    text,
                    re.IGNORECASE,
                ):
                    continue
            if pattern.search(text):
                failures.append(f"{file_name}: active USER packet text contains stale false-green marker {reason}")
        if primary_name and normalized != f"{USER_REVIEW_DIR_NAME}/{primary_name}":
            for stale_primary in (
                USER_BRANCH_PLAN_REVIEW_FILE,
                USER_BRANCH_VISION_REVIEW_FILE,
                "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md",
            ):
                if stale_primary == primary_name:
                    continue
                if normalized == f"{REVIEW_AIDS_DIR_NAME}/{stale_primary}":
                    stage1_support_context = (
                        stage1_current_posture
                        and normalized in {
                            f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_VISION_REVIEW_FILE}",
                            f"{REVIEW_AIDS_DIR_NAME}/{USER_BRANCH_PLAN_REVIEW_FILE}",
                        }
                        and re.search(
                            r"\b(?:context\s+complete|support(?:ing|[- ]only)?\s+context)\b",
                            text,
                            re.IGNORECASE,
                        )
                    )
                    if stage1_support_context:
                        continue
                if re.search(
                    rf"{re.escape(stale_primary)}[^\n]{{0,80}}\b(?:primary|active|decision)\b|"
                    rf"\b(?:primary|active|decision)[^\n]{{0,80}}{re.escape(stale_primary)}",
                    text,
                    re.IGNORECASE,
                ):
                    failures.append(
                        f"{file_name}: active support text points to stale primary/current decision file {stale_primary}"
                    )
    return failures


def _current_branch_external_state_dir() -> Path | None:
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, OSError):
        return None
    if not branch:
        return None
    branch_state_dir = re.sub(r"[^A-Za-z0-9]+", "_", branch).strip("_")
    return Path(r"C:\Nexus Governance State\branches") / branch_state_dir


def _accepted_historical_context_posture_failures(
    packet_files: Mapping[str, str],
    export_zip: Path,
    copied_to_live: Mapping[str, Path | None],
) -> list[str]:
    failures: list[str] = []
    state_name = f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_state.md"
    plan_name = f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_plan.md"
    state_text = packet_files.get(state_name, "")
    plan_text = packet_files.get(plan_name, "")
    live_state_path = copied_to_live.get(state_name)
    live_plan_path = copied_to_live.get(plan_name)
    live_state_text = live_state_path.read_text(encoding="utf-8") if live_state_path and live_state_path.is_file() else ""
    live_plan_text = live_plan_path.read_text(encoding="utf-8") if live_plan_path and live_plan_path.is_file() else ""

    expected_zip = _normalize_windows_path_text(str(export_zip))
    accepted_historical_zips = _accepted_historical_same_label_export_zip_paths(
        _sanitize_folder_name(export_zip.stem.rsplit("-", 2)[0])
    )
    copied_zip_values = _markdown_field_values(state_text, "USER Review ZIP")
    live_zip_values = _markdown_field_values(live_state_text, "USER Review ZIP")
    if not copied_zip_values:
        failures.append(
            f"{state_name}: accepted historical packet mode requires a copied USER Review ZIP pointer"
        )
    elif _normalize_windows_path_text(copied_zip_values[0]) != expected_zip:
        failures.append(
            f"{state_name}: accepted historical packet mode USER Review ZIP "
            f"{copied_zip_values[0]} does not match final ZIP {export_zip}"
        )
    if (
        export_zip.resolve() not in accepted_historical_zips
        and live_zip_values
        and _normalize_windows_path_text(live_zip_values[0]) != expected_zip
    ):
        failures.append(
            f"{state_name}: accepted historical packet mode is invalid because live external state "
            f"does not point to or preserve this accepted packet; live USER Review ZIP is {live_zip_values[0]}"
        )

    acceptance_text = f"{live_state_text}\n{live_plan_text}"
    if not re.search(r"\bUSER accepted\b.*\breviewable\b|\breviewable proof packet accepted\b", acceptance_text, re.IGNORECASE | re.DOTALL):
        failures.append(
            "Accepted historical packet mode requires a live external-state acceptance receipt "
            "for this reviewable evidence packet"
        )

    state_heads = _markdown_field_values(state_text, "Source Repo HEAD")
    plan_heads = _markdown_field_values(plan_text, "Source Repo HEAD")
    if not state_heads:
        failures.append(f"{state_name}: accepted historical packet mode requires copied Source Repo HEAD")
    if not plan_heads:
        failures.append(f"{plan_name}: accepted historical packet mode requires copied Source Repo HEAD")
    if state_heads and plan_heads and state_heads[0] != plan_heads[0]:
        failures.append(
            f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}: accepted historical packet copied branch state Source Repo HEAD "
            f"{state_heads[0]} disagrees with copied branch plan Source Repo HEAD {plan_heads[0]}"
        )
    return failures


def _source_truth_context_currentness_failures(
    packet_files: Mapping[str, str],
    *,
    validation_mode: str,
    export_zip: Path,
) -> list[str]:
    failures: list[str] = []
    external_state_dir = _current_branch_external_state_dir()
    copied_to_live = {
        f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_state.md": (
            external_state_dir / "branch_state.md" if external_state_dir else None
        ),
        f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_plan.md": (
            external_state_dir / "branch_plan.md" if external_state_dir else None
        ),
    }
    for copied_name, live_path in copied_to_live.items():
        copied_text = packet_files.get(copied_name)
        if copied_text is None:
            continue
        if re.search(r"PENDING_REGENERATION|Pending regeneration", copied_text, re.IGNORECASE):
            failures.append(
                f"{copied_name}: copied Source Truth Context still says packet regeneration is pending"
            )
        if re.search(r"USER Review ZIP:\s*`?PENDING", copied_text, re.IGNORECASE):
            failures.append(
                f"{copied_name}: copied Source Truth Context has no concrete current USER Review ZIP pointer"
            )
        if live_path is None or not live_path.is_file():
            failures.append(f"{copied_name}: live external-state source is missing for current branch")
            continue
        live_text = live_path.read_text(encoding="utf-8")
        if (
            validation_mode != PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL
            and _normalized_packet_text(copied_text) != _normalized_packet_text(live_text)
        ):
            failures.append(f"{copied_name}: copied Source Truth Context does not match live external state {live_path}")
    if validation_mode == PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL:
        failures.extend(
            _accepted_historical_context_posture_failures(
                packet_files,
                export_zip,
                copied_to_live,
            )
        )
    return failures


def _git_text(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, OSError):
        return None


def _markdown_field_values(text: str, field_name: str) -> list[str]:
    pattern = re.compile(
        rf"^{re.escape(field_name)}:\s*`?([^`\n]+?)`?\s*$",
        re.MULTILINE,
    )
    return [match.group(1).strip() for match in pattern.finditer(text)]


def _normalize_windows_path_text(text: str) -> str:
    return text.strip().strip("`").replace("/", "\\").casefold()


def _final_zip_active_metadata_failures(
    packet_files: Mapping[str, str],
    export_zip: Path,
    *,
    validation_mode: str,
) -> list[str]:
    failures: list[str] = []
    live_head = _git_text("rev-parse", "HEAD")
    source_truth_mismatch = False
    context_files = (
        f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_state.md",
        f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_plan.md",
    )

    for context_file in context_files:
        text = packet_files.get(context_file)
        if text is None:
            continue
        source_heads = _markdown_field_values(text, "Source Repo HEAD")
        if context_file.endswith("current_external_branch_state.md") and not source_heads:
            failures.append(f"{context_file}: copied current Source Truth Context is missing Source Repo HEAD")
            source_truth_mismatch = True
        if validation_mode != PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL and live_head:
            for source_head in source_heads:
                if source_head != live_head:
                    failures.append(
                        f"{context_file}: copied current Source Truth Context Source Repo HEAD "
                        f"{source_head} does not match live HEAD {live_head}"
                    )
                    source_truth_mismatch = True

    state_text = packet_files.get(f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_state.md", "")
    plan_text = packet_files.get(f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_plan.md", "")
    state_heads = _markdown_field_values(state_text, "Source Repo HEAD")
    plan_heads = _markdown_field_values(plan_text, "Source Repo HEAD")
    if state_heads and plan_heads and state_heads[0] != plan_heads[0]:
        failures.append(
            f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}: copied branch state Source Repo HEAD "
            f"{state_heads[0]} disagrees with copied branch plan Source Repo HEAD {plan_heads[0]}"
        )
        source_truth_mismatch = True

    review_zip_values = _markdown_field_values(state_text, "USER Review ZIP")
    if review_zip_values:
        expected_zip = _normalize_windows_path_text(str(export_zip))
        for review_zip in review_zip_values[:1]:
            if _normalize_windows_path_text(review_zip) != expected_zip:
                failures.append(
                    f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/current_external_branch_state.md: "
                    f"USER Review ZIP {review_zip} does not match final ZIP {export_zip}"
                )
                source_truth_mismatch = True

    ledger_text = packet_files.get(f"{REVIEW_AIDS_DIR_NAME}/FAM_007_UNIFIED_DEFECT_LEDGER.md", "")
    if source_truth_mismatch and re.search(
        r"^\|.*F7-UDL-003.*CLOSED_WITH_PROOF.*\|",
        ledger_text,
        re.MULTILINE,
    ):
        failures.append(
            f"{REVIEW_AIDS_DIR_NAME}/FAM_007_UNIFIED_DEFECT_LEDGER.md: "
            "F7-UDL-003 is CLOSED_WITH_PROOF while final ZIP Source Truth Context is stale or inconsistent"
        )

    return failures


def _proof_manifest_false_green_failures(packet_files: Mapping[str, str]) -> list[str]:
    manifest_items = [
        (name, text)
        for name, text in sorted(packet_files.items())
        if _packet_file_basename(name) == "live_resize_manifest.json"
    ]
    if not manifest_items:
        return []
    failures: list[str] = []
    manifest_name, manifest_text = manifest_items[0]
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"{manifest_name}: live proof manifest is not valid JSON: {exc}"]

    checks = manifest.get("checks")
    if not isinstance(checks, dict):
        return [f"{manifest_name}: live proof manifest is missing checks object"]
    for check_name in REQUIRED_FAM007_LIVE_PROOF_CHECKS:
        if checks.get(check_name) is not True:
            failures.append(f"{manifest_name}: required false-green proof check is not true: {check_name}")

    child_probe = manifest.get("childChromeProbe")
    if isinstance(child_probe, dict):
        for child_name, probe in sorted(child_probe.items()):
            if not isinstance(probe, dict):
                failures.append(f"{manifest_name}: childChromeProbe.{child_name} is not an object")
                continue
            expected_pairs = {
                "nativeChrome": "true",
                "osChrome": "rejected",
                "shellConformance": "ndai-webview-rounded-window-shell",
                "moveBehavior": "header-drag",
                "resizeBehavior": "edge-corner-resize",
            }
            for key, expected in expected_pairs.items():
                if probe.get(key) != expected:
                    failures.append(
                        f"{manifest_name}: childChromeProbe.{child_name}.{key} expected {expected!r} got {probe.get(key)!r}"
                    )
    else:
        failures.append(f"{manifest_name}: live proof manifest is missing childChromeProbe object")
    return failures


def _image_signature_valid(data: bytes, suffix: str) -> bool:
    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        return True
    except ImportError:
        pass
    except Exception:
        return False

    suffix = suffix.lower()
    if suffix == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8") and data.rstrip().endswith(b"\xff\xd9")
    if suffix == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return True


def _archive_file_entries(archive: zipfile.ZipFile) -> set[str]:
    return {entry.filename for entry in archive.infolist() if not entry.is_dir()}


def _archive_text(archive: zipfile.ZipFile, entry: str) -> str | None:
    try:
        return archive.read(entry).decode("utf-8")
    except KeyError:
        return None
    except UnicodeDecodeError:
        return None


def _proof_image_basename(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    windows_name = PureWindowsPath(text).name
    posix_name = PurePosixPath(text).name
    return windows_name if len(windows_name) <= len(posix_name) else posix_name


def _manifest_image_expectations(
    archive: zipfile.ZipFile,
) -> tuple[set[str], set[str], bool]:
    expected_entries: set[str] = set()
    screenshot_classes: set[str] = set()
    manifest_found = False
    for entry in _archive_file_entries(archive):
        if PurePosixPath(entry).name != FAM007_LIVE_PROOF_MANIFEST_NAME:
            continue
        text = _archive_text(archive, entry)
        if text is None:
            continue
        try:
            manifest = json.loads(text)
        except json.JSONDecodeError:
            continue
        screenshots = manifest.get("screenshots")
        if not isinstance(screenshots, dict):
            continue
        manifest_found = True
        for screenshot_class, paths in screenshots.items():
            if not isinstance(paths, dict):
                continue
            screenshot_classes.add(str(screenshot_class))
            focused_name = _proof_image_basename(paths.get("focusedWindow"))
            full_name = _proof_image_basename(paths.get("fullDesktop"))
            if focused_name:
                expected_entries.add(
                    f"{REVIEW_AIDS_DIR_NAME}/Inspectable Evidence/focused_window_screenshots/{focused_name}"
                )
            if full_name:
                expected_entries.add(
                    f"{REVIEW_AIDS_DIR_NAME}/Inspectable Evidence/full_desktop_screenshots/{full_name}"
                )
    return expected_entries, screenshot_classes, manifest_found


def _proof_index_image_failures(
    archive: zipfile.ZipFile,
    zip_entries: set[str],
    zip_image_entries: set[str],
) -> list[str]:
    failures: list[str] = []
    image_basenames = {PurePosixPath(entry).name for entry in zip_image_entries}
    image_reference_pattern = re.compile(
        r"(?P<path>[A-Za-z]:\\[^\s)`]+|[\w./ -]+?\.(?:png|jpg|jpeg|webp))",
        re.IGNORECASE,
    )
    for entry in sorted(zip_entries):
        if not entry.startswith(f"{REVIEW_AIDS_DIR_NAME}/") or PurePosixPath(entry).suffix.lower() != ".md":
            continue
        text = _archive_text(archive, entry)
        if not text:
            continue
        for match in image_reference_pattern.finditer(text):
            reference = match.group("path").strip("`.,;:)")
            basename = _proof_image_basename(reference)
            if not basename or PurePosixPath(basename).suffix.lower() not in IMAGE_PROOF_EXTENSIONS:
                continue
            if re.match(r"^[A-Za-z]:\\", reference):
                failures.append(f"{entry}: proof index references local-only image path {basename}")
            if basename not in image_basenames and reference.replace("\\", "/") not in zip_entries:
                failures.append(f"{entry}: proof index references image proof not present in final ZIP {basename}")
    return failures


def _image_proof_failures(
    packet_dir: Path,
    export_zip: Path,
    folder_entries: set[str],
    *,
    validate_folder_images: bool = True,
) -> list[str]:
    failures: list[str] = []
    folder_image_entries = sorted(
        entry
        for entry in folder_entries
        if PurePosixPath(entry).suffix.lower() in IMAGE_PROOF_EXTENSIONS
    )
    if validate_folder_images:
        for entry in folder_image_entries:
            data = (packet_dir / PurePosixPath(entry)).read_bytes()
            if not _image_signature_valid(data, PurePosixPath(entry).suffix):
                failures.append(f"{entry}: image proof file has invalid binary signature")

    with zipfile.ZipFile(export_zip, "r") as archive:
        zip_entries = _archive_file_entries(archive)
        zip_image_entries = sorted(
            entry
            for entry in zip_entries
            if PurePosixPath(entry).suffix.lower() in IMAGE_PROOF_EXTENSIONS
        )
        manifest_expected_entries, screenshot_classes, manifest_found = _manifest_image_expectations(archive)
        for entry in zip_image_entries:
            data = archive.read(entry)
            if not _image_signature_valid(data, PurePosixPath(entry).suffix):
                failures.append(f"{entry}: ZIP image proof file has invalid binary signature")
        if manifest_expected_entries and not zip_image_entries:
            failures.append(
                "Inspectable Evidence: live proof manifest references screenshots but final ZIP contains zero image proof files"
            )
        missing_expected_entries = sorted(manifest_expected_entries.difference(zip_entries))
        if missing_expected_entries:
            preview = ", ".join(missing_expected_entries[:5])
            if len(missing_expected_entries) > 5:
                preview += f", ... total_missing={len(missing_expected_entries)}"
            failures.append(
                "Inspectable Evidence: final ZIP is missing manifest-referenced screenshot proof files "
                f"entries=[{preview}]"
            )
        if manifest_expected_entries and len(zip_image_entries) < len(manifest_expected_entries):
            failures.append(
                "Inspectable Evidence: final ZIP image proof count is lower than manifest expectation "
                f"zip_images={len(zip_image_entries)} expected_images={len(manifest_expected_entries)}"
            )
        if manifest_found:
            missing_classes = sorted(FAM007_REQUIRED_LIVE_PROOF_SCREENSHOT_CLASSES.difference(screenshot_classes))
            if missing_classes:
                failures.append(
                    "Inspectable Evidence: live proof manifest is missing required screenshot classes "
                    f"missing={', '.join(missing_classes)}"
                )
        zip_hashes_by_group: dict[str, dict[str, str]] = {}
        for entry in zip_image_entries:
            if entry.startswith(f"{REVIEW_AIDS_DIR_NAME}/Inspectable Evidence/full_desktop_screenshots/"):
                zip_hashes_by_group.setdefault("full_desktop_screenshots", {})[entry] = hashlib.sha256(
                    archive.read(entry)
                ).hexdigest()
        failures.extend(_proof_index_image_failures(archive, zip_entries, set(zip_image_entries)))
        udl_text = _archive_text(archive, f"{REVIEW_AIDS_DIR_NAME}/FAM_007_UNIFIED_DEFECT_LEDGER.md") or ""
        image_proof_missing = bool(manifest_expected_entries and (not zip_image_entries or missing_expected_entries))
        if image_proof_missing:
            for defect_id in FAM007_UDL_IMAGE_PROOF_IDS:
                if any(defect_id in line and "CLOSED_WITH_PROOF" in line for line in udl_text.splitlines()):
                    failures.append(
                        f"{defect_id} is CLOSED_WITH_PROOF while final ZIP screenshot proof is missing"
                    )

    full_desktop = sorted(
        entry
        for entry in zip_image_entries
        if entry.startswith(f"{REVIEW_AIDS_DIR_NAME}/Inspectable Evidence/full_desktop_screenshots/")
    )
    focused = sorted(
        entry
        for entry in zip_image_entries
        if entry.startswith(f"{REVIEW_AIDS_DIR_NAME}/Inspectable Evidence/focused_window_screenshots/")
    )
    if focused and not full_desktop:
        failures.append("Inspectable Evidence: focused/cropped window screenshots exist without full-desktop proof")
    if focused and full_desktop and len(full_desktop) < len(focused):
        failures.append(
            "Inspectable Evidence: full-desktop proof count is lower than focused/cropped proof count "
            f"focused={len(focused)} full_desktop={len(full_desktop)}"
        )
    full_hash_counts = Counter(zip_hashes_by_group.get("full_desktop_screenshots", {}).values())
    duplicate_hashes = sorted(digest for digest, count in full_hash_counts.items() if count > 1)
    if duplicate_hashes:
        failures.append(
            "Inspectable Evidence: duplicate full-desktop screenshot bytes detected "
            f"duplicate_hash_count={len(duplicate_hashes)}"
        )
    return failures


def _zip_file_entries(export_zip: Path) -> set[str]:
    with zipfile.ZipFile(export_zip, "r") as archive:
        return {entry.filename for entry in archive.infolist() if not entry.is_dir()}


def _folder_file_hashes(packet_dir: Path) -> dict[str, str]:
    file_hashes: dict[str, str] = {}
    for path in sorted(_bundle_files(packet_dir)):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        file_hashes[path.relative_to(packet_dir).as_posix()] = digest
    return file_hashes


def _zip_file_hashes(export_zip: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    with zipfile.ZipFile(export_zip, "r") as archive:
        entries = [entry for entry in archive.infolist() if not entry.is_dir()]
        entry_counts = Counter(entry.filename for entry in entries)
        duplicate_entries = tuple(
            sorted(name for name, count in entry_counts.items() if count > 1)
        )
        file_hashes = {
            entry.filename: hashlib.sha256(archive.read(entry)).hexdigest()
            for entry in entries
        }
        return file_hashes, duplicate_entries


def _same_label_export_zip_paths(review_root: Path, label: str) -> set[Path]:
    safe_label = _sanitize_folder_name(label)
    timestamped_name = re.compile(rf"^{re.escape(safe_label)}-\d{{8}}-\d{{6}}\.zip$")
    paths = {_legacy_stable_export_zip_path(review_root, label).resolve()}
    paths.update(path.resolve() for path in review_root.glob("*.zip") if timestamped_name.fullmatch(path.name))
    return paths


def _accepted_historical_same_label_export_zip_paths(label: str) -> set[Path]:
    external_state_dir = _current_branch_external_state_dir()
    if external_state_dir is None:
        return set()
    accepted_paths: set[Path] = set()
    safe_label = _sanitize_folder_name(label)
    patterns = (
        re.compile(r"Accepted Historical(?: Evidence)? Packet:\s*`([^`\n]+\.zip)`", re.IGNORECASE),
        re.compile(r"\baccepted\b[^\n`]*`([^`\n]+\.zip)`[^\n]*\bhistorical evidence\b", re.IGNORECASE),
    )
    for file_name in ("branch_state.md", "branch_plan.md"):
        path = external_state_dir / file_name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in patterns:
            for match in pattern.finditer(text):
                candidate = Path(match.group(1).strip()).resolve()
                if candidate.name.startswith(f"{safe_label}-") and candidate.suffix.lower() == ".zip":
                    accepted_paths.add(candidate)
    return accepted_paths


def _generic_user_facing_technical_metadata_failures(
    packet_files: Mapping[str, str],
) -> list[str]:
    """Check only generated USER-facing surfaces, not copied source-truth context."""

    failures: list[str] = []
    for file_name, text in sorted(packet_files.items()):
        normalized = file_name.replace("\\", "/")
        if (
            normalized.startswith(f"{REVIEW_AIDS_DIR_NAME}/Unified Defect Ledger/")
            and normalized.endswith(".json")
        ):
            continue
        if normalized.startswith(f"{REVIEW_AIDS_DIR_NAME}/Validation Outputs/"):
            continue
        if normalized.startswith(f"{REVIEW_AIDS_DIR_NAME}/Final Clean Proof/"):
            continue
        if (
            normalized != "START_HERE.md"
            and not normalized.startswith(f"{USER_REVIEW_DIR_NAME}/")
            and not normalized.startswith(f"{REVIEW_AIDS_DIR_NAME}/")
        ):
            continue
        for label, pattern in USER_FACING_TECHNICAL_METADATA_PATTERNS:
            if pattern.search(text):
                failures.append(f"{file_name}: USER-facing file contains technical metadata: {label}")
    return failures


def _local_user_packet_layout_failures(
    packet_dir: Path,
    folder_entries: set[str],
) -> tuple[list[str], tuple[str, ...]]:
    failures: list[str] = []
    if "START_HERE.md" not in folder_entries:
        failures.append("START_HERE.md is missing from the packet root")

    for directory_name in LOCAL_USER_PACKET_REQUIRED_DIRS:
        directory = packet_dir / directory_name
        if not directory.is_dir():
            failures.append(f"{directory_name}/ folder is missing from the packet")

    allowed_top_level = set(LOCAL_USER_PACKET_REQUIRED_DIRS) | LOCAL_USER_PACKET_ROOT_FILES
    for entry in sorted(folder_entries):
        first_part = PurePosixPath(entry).parts[0]
        if first_part not in allowed_top_level:
            failures.append(f"{entry}: file is outside approved USER packet layout")

    primary_files = tuple(
        sorted(
            entry
            for entry in folder_entries
            if entry.startswith(f"{USER_REVIEW_DIR_NAME}/")
        )
    )
    if len(primary_files) != 1:
        failures.append(
            f"{USER_REVIEW_DIR_NAME}/ must contain exactly one primary USER review file; "
            f"found {len(primary_files)}"
        )
    elif PurePosixPath(primary_files[0]).suffix.lower() != ".md":
        failures.append(f"{primary_files[0]}: primary USER review file must be Markdown")
    return failures, primary_files


def _fam003_lv1_visual_retest_packet_detected(packet_files: Mapping[str, str]) -> bool:
    combined = "\n".join(
        (
            packet_files.get("START_HERE.md", ""),
            packet_files.get("USER Review/FAM003_LV1_VISUAL_RETEST_REVIEW.md", ""),
            packet_files.get("Review Aids/LV1_RETEST_PACKET_FILE_DIGEST.md", ""),
        )
    ).casefold()
    return (
        "fam-003" in combined
        and "lv1 visual retest" in combined
        and "global settings" in combined
        and "quick access" in combined
    )


FAM003_VISUAL_UDL_IDS = tuple(f"UDL-VIS-{index:03d}" for index in range(1, 15))
FAM003_VISUAL_UDL_REQUIRED_FIELDS = (
    "Defect ID",
    "Origin",
    "Exact USER wording where applicable",
    "Source-truth basis",
    "Expected behavior",
    "Actual behavior",
    "Evidence path or screenshot reference",
    "Affected files/surfaces",
    "Owner/family boundary",
    "Impact",
    "Root cause",
    "Validator/proof gap",
    "Adjacent-defect sweep result",
    "Exact repair target",
    "Acceptance criteria",
    "Required proof",
    "Validation required",
    "Status",
    "Closure proof when closed",
)
FAM003_VISUAL_UDL_ALLOWED_STATUSES = {
    "OPEN",
    "REPRODUCED",
    "IN_REPAIR",
    "FIXED_PENDING_PROOF",
    "PROOF_FAILED",
    "REOPENED",
    "CLOSED_WITH_PROOF",
    "BLOCKED_SOURCE_TRUTH",
    "OUT_OF_SCOPE_USER_APPROVAL_REQUIRED",
}
FAM003_RECURRING_DEFECT_IDS = (
    "F3-LV1-UI-001",
    "F3-LV1-UI-016",
    "F3-LV1-UI-020",
    "F3-LV1-UI-021",
    "F3-LV1-PROOF-002",
    "F3-LV1-UI-030",
    "F3-LV1-UI-031",
    "F3-LV1-UI-032",
    "F3-LV1-UI-033",
    "F3-LV1-UI-034",
    "F3-LV1-UI-035",
    "F3-LV1-UI-036",
    "F3-LV1-UI-037",
    "F3-LV1-UI-038",
    "F3-LV1-UI-043",
    "F3-LV1-UI-044",
    "F3-LV1-UI-045",
    "F3-LV1-UI-046",
    "F3-LV1-UI-047",
    "F3-LV1-UI-048",
    "F3-LV1-UI-049",
    "F3-LV1-UI-050",
    "F3-LV1-UI-051",
)
FAM003_LOOP_BREAKER_DEFECT_ID = "F3-LV1-PROOF-003"
FAM003_PACKET_IMAGE_INTEGRITY_DEFECT_ID = "F3-LV1-PROOF-004"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_SIGNATURE_HEX = "89 50 4E 47 0D 0A 1A 0A"


def _fam003_recurrence_ledger_failures(recurrence_text: str) -> list[str]:
    failures: list[str] = []
    if FAM003_LOOP_BREAKER_DEFECT_ID not in recurrence_text:
        failures.append(f"{FAM003_LOOP_BREAKER_DEFECT_ID} is missing from recurrence ledger")
    if "Result: `PASS - WOULD BLOCK`" not in recurrence_text:
        failures.append("recurrence ledger lacks prior-packet blockability proof")
    if "Retest Candidate Gate: `BLOCKED`" in recurrence_text:
        failures.append("same-defect recurrence gate is BLOCKED; packet cannot be a retest candidate")

    table_statuses: dict[str, str] = {}
    table_pattern = re.compile(
        r"^\|\s*`(F3-LV1-(?:UI|PROOF|FUNC)-\d{3})`\s*\|\s*`([^`]+)`\s*\|",
        re.MULTILINE,
    )
    for match in table_pattern.finditer(recurrence_text):
        table_statuses[match.group(1)] = match.group(2).strip()

    for defect_id in (*FAM003_RECURRING_DEFECT_IDS, FAM003_LOOP_BREAKER_DEFECT_ID):
        status = table_statuses.get(defect_id)
        if not status:
            failures.append(f"{defect_id} is missing from recurrence table")
        elif status != "CLOSED_WITH_PROOF":
            failures.append(f"{defect_id} recurrence status is not CLOSED_WITH_PROOF: {status}")
    return failures


def _fam003_visual_udl_schema_failures(visual_udl_text: str) -> list[str]:
    failures: list[str] = []
    if "| ID | Status | Defect / Risk |" in visual_udl_text:
        failures.append("visual UDL is still a compact summary table")

    section_pattern = re.compile(
        r"^##\s+(UDL-VIS-\d{3})\b(?P<body>.*?)(?=^##\s+UDL-VIS-\d{3}\b|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    field_pattern = re.compile(r"^-\s+([^:]+):\s*(.*)$")
    sections: dict[str, dict[str, str]] = {}
    for match in section_pattern.finditer(visual_udl_text):
        defect_id = match.group(1)
        fields: dict[str, str] = {}
        current_field: str | None = None
        for raw_line in match.group("body").splitlines():
            field_match = field_pattern.match(raw_line)
            if field_match:
                current_field = field_match.group(1).strip()
                fields[current_field] = field_match.group(2).strip()
            elif current_field and raw_line.startswith("  "):
                fields[current_field] = f"{fields[current_field]} {raw_line.strip()}".strip()
            else:
                current_field = None
        sections[defect_id] = fields

    for defect_id in FAM003_VISUAL_UDL_IDS:
        fields = sections.get(defect_id)
        if not fields:
            failures.append(f"{defect_id} missing detailed section")
            continue
        missing_fields = [
            field
            for field in FAM003_VISUAL_UDL_REQUIRED_FIELDS
            if not fields.get(field) or fields.get(field) in {"TODO", "`TODO`", "TBD", "`TBD`"}
        ]
        if missing_fields:
            failures.append(f"{defect_id} missing fields: {', '.join(missing_fields)}")
        status = fields.get("Status", "").strip("` ")
        if status not in FAM003_VISUAL_UDL_ALLOWED_STATUSES:
            failures.append(f"{defect_id} has illegal status {fields.get('Status', '<missing>')}")
        elif status != "CLOSED_WITH_PROOF":
            failures.append(f"{defect_id} is not CLOSED_WITH_PROOF: {status}")
        if status == "CLOSED_WITH_PROOF":
            for closure_field in (
                "Evidence path or screenshot reference",
                "Acceptance criteria",
                "Validation required",
                "Closure proof when closed",
            ):
                if not fields.get(closure_field):
                    failures.append(f"{defect_id} missing closure field {closure_field}")
    return failures


def _fam003_latest_defect_statuses(udl_text: str) -> dict[str, str]:
    """Return the latest recorded status per FAM-003 packet/visual defect row."""

    statuses: dict[str, str] = {}
    section_pattern = re.compile(
        r"^##\s+((?:UDL-\d{3})|(?:F3-LV1-(?:UI|PROOF|FUNC)-\d{3}))\b(?P<body>.*?)(?="
        r"^##\s+(?:UDL-\d{3}|F3-LV1-(?:UI|PROOF|FUNC)-\d{3})\b|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for match in section_pattern.finditer(udl_text):
        status_match = re.search(
            r"^Status:\s*`?([^`\n]+)`?",
            match.group("body"),
            re.MULTILINE,
        )
        if status_match:
            statuses[match.group(1)] = status_match.group(1).strip()
    return statuses


def _posix_entry_path(base_dir: Path, entry: str) -> Path:
    return base_dir.joinpath(*PurePosixPath(entry).parts)


def _png_image_decode(data: bytes) -> tuple[bool, str, int, int]:
    if data[:8] != PNG_SIGNATURE:
        return False, f"invalid PNG signature {data[:8].hex(' ').upper()}", 0, 0
    if len(data) < 24 or data[12:16] != b"IHDR":
        return False, "PNG IHDR chunk is missing or truncated", 0, 0

    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            image.verify()
        if width <= 0 or height <= 0:
            return False, f"Pillow decoded zero-size PNG {width}x{height}", width, height
        return True, "Pillow", width, height
    except ImportError:
        pass
    except Exception as exc:
        pillow_error = f"Pillow decode failed: {exc}"
    else:
        pillow_error = ""

    try:
        from PySide6.QtGui import QImage

        image = QImage.fromData(data, "PNG")
        if image.isNull():
            return False, "QImage decode failed: null PNG image", 0, 0
        width, height = image.width(), image.height()
        if width <= 0 or height <= 0:
            return False, f"QImage decoded zero-size PNG {width}x{height}", width, height
        return True, "QImage", width, height
    except ImportError:
        pass
    except Exception as exc:
        qimage_error = f"QImage decode failed: {exc}"
    else:
        qimage_error = ""

    if "pillow_error" in locals():
        return False, pillow_error, 0, 0
    if "qimage_error" in locals():
        return False, qimage_error, 0, 0
    width, height = struct.unpack(">II", data[16:24])
    return False, f"no normal image decoder available; IHDR-only size {width}x{height}", width, height


def _fam003_manifest_png_entries(
    manifest_text: str,
    *,
    settings_prefix: str,
    known_settings_entries: set[str],
) -> tuple[set[str], list[str]]:
    if not manifest_text.strip():
        return set(), []

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return set(), [f"settings visual manifest is not valid JSON: {exc}"]

    png_values: list[str] = []
    artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if isinstance(artifact, Mapping):
                path_value = artifact.get("path")
                if isinstance(path_value, str) and path_value.casefold().endswith(".png"):
                    png_values.append(path_value)

    manage_guard = (
        manifest.get("manageMonitorsDirtyGuardReference")
        if isinstance(manifest, Mapping)
        else None
    )
    if isinstance(manage_guard, Mapping):
        for key in ("image", "sideBySide"):
            path_value = manage_guard.get(key)
            if isinstance(path_value, str) and path_value.casefold().endswith(".png"):
                png_values.append(path_value)

    entries: set[str] = set()
    failures: list[str] = []
    for raw_value in png_values:
        normalized = raw_value.replace("\\", "/")
        match = re.search(
            r"fam003_settings_repair_visual_validation/\d{8}-\d{6}/(.+?\.png)$",
            normalized,
            re.IGNORECASE,
        )
        if match:
            entries.add(settings_prefix + match.group(1))
            continue

        basename = PurePosixPath(normalized).name
        matches = sorted(
            entry for entry in known_settings_entries if PurePosixPath(entry).name == basename
        )
        if len(matches) == 1:
            entries.add(matches[0])
        else:
            failures.append(
                "FAM-003 LV1 packet image integrity failed: manifest PNG reference "
                f"{raw_value!r} cannot be mapped to exactly one packet artifact"
            )
    return entries, failures


def _fam003_receipt_has_pass_row(receipt_text: str, artifact_tail: str) -> bool:
    escaped = re.escape(artifact_tail)
    pattern = re.compile(
        rf"^\|\s*`?(?:{escaped}|.*?/{escaped})`?\s*\|[^\n]*\bPASS\b",
        re.MULTILINE,
    )
    return bool(pattern.search(receipt_text))


def _fam003_packet_image_integrity_failures(
    packet_dir: Path,
    *,
    export_zip: Path,
    settings_prefix: str,
    normalized_entries: set[str],
    required_image_artifacts: tuple[str, ...],
    packet_files: Mapping[str, str],
) -> list[str]:
    failures: list[str] = []
    settings_png_entries = {
        entry
        for entry in normalized_entries
        if entry.startswith(settings_prefix) and entry.casefold().endswith(".png")
    }
    required_image_entries = {settings_prefix + artifact for artifact in required_image_artifacts}
    manifest_text = packet_files.get(settings_prefix + "fam003_settings_visual_fail_repair_manifest.json", "")
    manifest_entries, manifest_failures = _fam003_manifest_png_entries(
        manifest_text,
        settings_prefix=settings_prefix,
        known_settings_entries=settings_png_entries | required_image_entries,
    )
    failures.extend(manifest_failures)

    image_entries = sorted(settings_png_entries | required_image_entries | manifest_entries)
    receipt_entry = settings_prefix + "IMAGE_INTEGRITY_RECEIPT.md"
    receipt_text = packet_files.get(receipt_entry, "")
    if not receipt_text.strip():
        failures.append(
            "FAM-003 LV1 packet image integrity failed: IMAGE_INTEGRITY_RECEIPT.md is missing"
        )

    try:
        with zipfile.ZipFile(export_zip, "r") as archive:
            zip_entries = {entry.filename for entry in archive.infolist() if not entry.is_dir()}
            zip_bytes = {
                entry: archive.read(entry)
                for entry in image_entries
                if entry in zip_entries
            }
    except zipfile.BadZipFile as exc:
        return [f"FAM-003 LV1 packet image integrity failed: ZIP unreadable: {exc}"]

    for entry in image_entries:
        artifact_tail = entry.removeprefix(settings_prefix)
        folder_path = _posix_entry_path(packet_dir, entry)
        if entry not in normalized_entries or not folder_path.is_file():
            failures.append(
                "FAM-003 LV1 packet image integrity failed: missing folder PNG artifact "
                f"{entry}"
            )
            continue
        folder_data = folder_path.read_bytes()
        ok, decoder, width, height = _png_image_decode(folder_data)
        if not ok:
            failures.append(
                "FAM-003 LV1 packet image integrity failed: folder PNG invalid "
                f"{entry}: {decoder}"
            )
        elif width <= 0 or height <= 0:
            failures.append(
                "FAM-003 LV1 packet image integrity failed: folder PNG has zero dimensions "
                f"{entry}: {width}x{height}"
            )

        if entry not in zip_bytes:
            failures.append(
                "FAM-003 LV1 packet image integrity failed: ZIP PNG artifact missing "
                f"{entry}"
            )
            continue
        zip_data = zip_bytes[entry]
        zip_ok, zip_decoder, zip_width, zip_height = _png_image_decode(zip_data)
        if not zip_ok:
            failures.append(
                "FAM-003 LV1 packet image integrity failed: ZIP PNG invalid "
                f"{entry}: {zip_decoder}"
            )
        elif zip_width <= 0 or zip_height <= 0:
            failures.append(
                "FAM-003 LV1 packet image integrity failed: ZIP PNG has zero dimensions "
                f"{entry}: {zip_width}x{zip_height}"
            )

        if folder_data != zip_data:
            failures.append(
                "FAM-003 LV1 packet image integrity failed: folder/ZIP PNG bytes differ "
                f"{entry}"
            )
        if receipt_text and not _fam003_receipt_has_pass_row(receipt_text, artifact_tail):
            failures.append(
                "FAM-003 LV1 packet image integrity failed: image integrity receipt "
                f"lacks PASS row for {artifact_tail}"
            )
    return failures


def _fam003_lv1_visual_retest_semantic_failures(
    packet_files: Mapping[str, str],
    packet_dir: Path,
    folder_entries: set[str],
    export_zip: Path,
) -> list[str]:
    """FAM-003-local semantic proof checks for the LV1 visual retest packet."""

    if not _fam003_lv1_visual_retest_packet_detected(packet_files):
        return []

    failures: list[str] = []
    normalized_entries = {entry.replace("\\", "/") for entry in folder_entries}
    expected_zip_name = export_zip.name
    settings_prefix = "Source Truth Context/Proof Artifacts/Settings Visual Proof/"
    required_settings_artifacts = (
        "01_default_global_settings_shell.png",
        "02_top_level_chrome_control_cluster.png",
        "03_window_control_focus_pressed_state.png",
        "03a_window_moved_by_chrome.png",
        "03b_window_resized.png",
        "03d_window_wide_size.png",
        "03c_window_minimum_size.png",
        "04_left_settings_organizer.png",
        "04a_left_nav_active_child.png",
        "04a1_quick_access_child_pill_no_clip_focus.png",
        "04a2_quick_access_child_pill_focus_pressed_state.png",
        "04d_left_pane_compressed_horizontal_overflow.png",
        "04e_left_pane_wide.png",
        "05_row_action_default_disabled_state.png",
        "05_tray_parent_page.png",
        "06_dirty_quick_access.png",
        "07_dropdown_list_state.png",
        "08_close_guard.png",
        "09_defaults_staged.png",
        "10_max_slots_unclipped.png",
        "11_post_save_clean_state.png",
        "12_reference_conformance_contact_sheet.png",
        "13a_accepted_manage_monitors_dirty_guard_reference.png",
        "13_accepted_ai_control_center_default.png",
        "14_glyph_control_closeup.png",
        "15_left_pane_resize_affordance_closeup.png",
        "16_defect_closure_contact_sheet.png",
        "17_red_team_review_sheet.png",
        "18_manage_monitors_dirty_guard_side_by_side.png",
        "19_stress_size_684x500.png",
        "19_stress_size_700x500.png",
        "19_stress_size_780x500.png",
        "19_stress_size_840x530.png",
        "19_stress_size_840x610.png",
        "22_row_count_1_of_4.png",
        "22_row_count_2_of_4.png",
        "22_row_count_3_of_4.png",
        "22_row_count_4_of_4.png",
        "26_four_row_dirty_state.png",
        "27_four_row_dropdown_open.png",
        "28_four_row_dirty_close_guard_intercept.png",
        "29_dirty_close_cancel_preserves_window.png",
        "REFERENCE_CONFORMANCE_CONTACT_SHEET.png",
        "ARTIFACT_TO_SURFACE_LEDGER.md",
        "DEFECT_CLOSURE_PROOF_LEDGER.md",
        "DIRTY_CLOSE_INTERCEPT_MATRIX.md",
        "ELEMENT_GROUP_REFERENCE_CONFORMANCE_LEDGER.md",
        "FAIL_CAPABLE_DEFECT_LEDGER.md",
        "FAM003_SETTINGS_REPAIR_VISUAL_VALIDATION.md",
        "IMAGE_INTEGRITY_RECEIPT.md",
        "MANAGE_MONITORS_DIRTY_GUARD_REFERENCE.md",
        "fam003_settings_visual_fail_repair_manifest.json",
        "resident_access_settings.json",
    )
    forbidden_settings_artifacts = (
        "19_stress_size_1100x720.png",
        "19_stress_size_920x520.png",
        "19_stress_size_620x360.png",
        "19_stress_size_660x424.png",
        "19_stress_size_748x434.png",
        "19_stress_size_860x560.png",
        "19_stress_size_780x560.png",
        "19_stress_size_780x460.png",
        "19_stress_size_720x406.png",
        "19_stress_size_590x338.png",
        "19_stress_size_700x360.png",
        "19_stress_size_640x340.png",
        "19_stress_size_560x318.png",
        "19_stress_size_620x466.png",
        "19_stress_size_660x466.png",
        "19_stress_size_748x466.png",
        "19_stress_size_820x500.png",
        "19_stress_size_820x590.png",
    )
    required_image_artifacts = tuple(
        artifact for artifact in required_settings_artifacts if artifact.casefold().endswith(".png")
    )
    settings_files = sorted(
        entry for entry in normalized_entries if entry.startswith(settings_prefix)
    )
    if not settings_files:
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: Settings Visual Proof folder is empty"
        )
    for artifact in required_settings_artifacts:
        expected_entry = settings_prefix + artifact
        if expected_entry not in normalized_entries:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: missing settings proof artifact "
                f"{expected_entry}"
            )
    for artifact in forbidden_settings_artifacts:
        forbidden_entry = settings_prefix + artifact
        if forbidden_entry in normalized_entries:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: stale or mislabeled live/stress proof artifact present "
                f"{forbidden_entry}"
            )
    failures.extend(
        _fam003_packet_image_integrity_failures(
            packet_dir,
            export_zip=export_zip,
            settings_prefix=settings_prefix,
            normalized_entries=normalized_entries,
            required_image_artifacts=required_image_artifacts,
            packet_files=packet_files,
        )
    )

    review_text = packet_files.get("USER Review/FAM003_LV1_VISUAL_RETEST_REVIEW.md", "")
    if "The packet includes focused screenshots" in review_text and not settings_files:
        failures.append(
            "USER Review/FAM003_LV1_VISUAL_RETEST_REVIEW.md: claims focused screenshots are included, "
            "but Settings Visual Proof contains no files"
        )

    missing_source_text = packet_files.get(
        "Source Truth Context/MISSING_SOURCE_FILES.md", ""
    )
    if missing_source_text.strip():
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: MISSING_SOURCE_FILES.md is present; "
            "source-truth copy claims must be reconciled before USER review"
        )

    current_uiref_files = (
        "Source Truth Context/Repo Source Truth/UIREF-003_control_state_and_selector_grammar.md",
        "Source Truth Context/Repo Source Truth/UIREF-004_dialog_status_recovery_and_doorway_surfaces.md",
        "Source Truth Context/Repo Source Truth/UIREF-005_design_token_and_shared_rule_baseline.md",
        "Source Truth Context/Repo Source Truth/UIREF-006_negative_example_and_enforcement_contract.md",
    )
    for entry in current_uiref_files:
        if entry not in normalized_entries:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: missing current UIREF source snapshot "
                f"{entry}"
            )
    stale_uiref_name_patterns = (
        "UIREF-003_spacing_density.md",
        "UIREF-004_control_states.md",
        "UIREF-005_menu_dropdown_list_behavior.md",
        "UIREF-006_visual_proof_and_reference_usage.md",
    )
    stale_uiref_mentions = [
        name for name in stale_uiref_name_patterns if name in missing_source_text
    ]
    if stale_uiref_mentions:
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: stale UIREF filenames listed as missing "
            f"{stale_uiref_mentions}"
        )

    uts_text = packet_files.get("Source Truth Context/UTS Context/UTS - FAM-003.txt", "")
    if not uts_text.strip():
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: UTS context snapshot is missing"
        )
    else:
        packet_refs = sorted(set(re.findall(r"FAM-003-\d{8}-\d{6}\.zip", uts_text)))
        stale_packet_refs = [ref for ref in packet_refs if ref != expected_zip_name]
        if stale_packet_refs:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: UTS context references stale packet(s) "
                f"{stale_packet_refs}; expected {expected_zip_name}"
            )
        sha_refs = sorted(set(re.findall(r"\b[A-Fa-f0-9]{64}\b", uts_text)))
        if sha_refs:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: UTS context contains ZIP SHA256 value(s); "
                "packet-internal UTS must use an outside-packet final receipt model"
            )
        commit_sha_refs = sorted(set(re.findall(r"\b[A-Fa-f0-9]{40}\b", uts_text)))
        if commit_sha_refs:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: UTS context contains commit SHA value(s); "
                "packet-internal UTS must not carry live HEAD receipts"
            )

    file_digest = packet_files.get("Review Aids/LV1_RETEST_PACKET_FILE_DIGEST.md", "")
    proof_root_match = re.search(
        r"fam003_settings_repair_visual_validation[\\/](\d{8}-\d{6})",
        file_digest,
        re.IGNORECASE,
    )
    expected_proof_stamp = proof_root_match.group(1) if proof_root_match else ""
    if not expected_proof_stamp:
        failures.append(
            "Review Aids/LV1_RETEST_PACKET_FILE_DIGEST.md: current settings proof root is missing"
        )
    elif uts_text:
        uts_proof_stamps = sorted(
            set(
                re.findall(
                    r"fam003_settings_repair_visual_validation[\\/](\d{8}-\d{6})",
                    uts_text,
                    re.IGNORECASE,
                )
            )
        )
        stale_proof_stamps = [
            stamp for stamp in uts_proof_stamps if stamp != expected_proof_stamp
        ]
        if stale_proof_stamps:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: UTS context references stale proof root(s) "
                f"{stale_proof_stamps}; expected {expected_proof_stamp}"
            )

    incident_entries = [
        entry
        for entry in normalized_entries
        if "false_green_incident" in PurePosixPath(entry).name.lower()
    ]
    if not incident_entries:
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: false-green incident record is missing"
        )

    stale_output_incident_entries = [
        entry
        for entry in normalized_entries
        if "stale_output_false_green_incident" in PurePosixPath(entry).name.lower()
    ]
    if not stale_output_incident_entries:
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: stale-output false-green incident record is missing"
        )

    recurrence_entries = [
        entry
        for entry in normalized_entries
        if "same_defect_recurrence_ledger" in PurePosixPath(entry).name.lower()
    ]
    if not recurrence_entries:
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: same-defect recurrence ledger is missing"
        )
    else:
        recurrence_text = "\n".join(packet_files.get(entry, "") for entry in recurrence_entries)
        for recurrence_failure in _fam003_recurrence_ledger_failures(recurrence_text):
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: " + recurrence_failure
            )

    udl_entries = [
        entry
        for entry in normalized_entries
        if "unified_defect_ledger" in PurePosixPath(entry).name.lower()
    ]
    if not udl_entries:
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: Unified Defect Ledger is missing"
        )
    else:
        udl_text = "\n".join(packet_files.get(entry, "") for entry in udl_entries)
        required_udl_ids = (
            "UDL-001",
            "UDL-002",
            "UDL-003",
            "UDL-004",
            "UDL-005",
            "UDL-006",
            "UDL-007",
            "UDL-008",
            "UDL-009",
            "UDL-010",
            "UDL-011",
            "F3-LV1-UI-001",
            "F3-LV1-UI-015",
            "F3-LV1-UI-016",
            "F3-LV1-UI-017",
            "F3-LV1-UI-018",
            "F3-LV1-UI-019",
            "F3-LV1-UI-020",
            "F3-LV1-UI-021",
            "F3-LV1-UI-022",
            "F3-LV1-UI-023",
            "F3-LV1-UI-024",
            "F3-LV1-UI-025",
            "F3-LV1-UI-026",
            "F3-LV1-UI-027",
            "F3-LV1-UI-028",
            "F3-LV1-UI-029",
            "F3-LV1-UI-030",
            "F3-LV1-UI-031",
            "F3-LV1-UI-032",
            "F3-LV1-UI-033",
            "F3-LV1-UI-034",
            "F3-LV1-UI-035",
            "F3-LV1-UI-036",
            "F3-LV1-UI-037",
            "F3-LV1-UI-038",
            "F3-LV1-UI-043",
            "F3-LV1-UI-044",
            "F3-LV1-UI-045",
            "F3-LV1-UI-046",
            "F3-LV1-UI-047",
            "F3-LV1-UI-048",
            "F3-LV1-UI-049",
            "F3-LV1-UI-050",
            "F3-LV1-UI-051",
            "F3-LV1-UI-052",
            "F3-LV1-UI-053",
            "F3-LV1-UI-054",
            "F3-LV1-UI-055",
            "F3-LV1-UI-056",
            "F3-LV1-UI-057",
            "F3-LV1-UI-058",
            "F3-LV1-UI-059",
            "F3-LV1-UI-060",
            "F3-LV1-UI-061",
            "F3-LV1-FUNC-001",
            "F3-LV1-FUNC-002",
            "F3-LV1-PROOF-001",
            "F3-LV1-PROOF-002",
            "F3-LV1-PROOF-005",
            "F3-LV1-PROOF-006",
            FAM003_LOOP_BREAKER_DEFECT_ID,
            FAM003_PACKET_IMAGE_INTEGRITY_DEFECT_ID,
        )
        for defect_id in required_udl_ids:
            if defect_id not in udl_text:
                failures.append(
                    f"FAM-003 LV1 packet semantic proof failed: {defect_id} is missing from the UDL"
                )
        latest_statuses = _fam003_latest_defect_statuses(udl_text)
        non_closed_statuses = sorted(
            f"{defect_id}={latest_statuses.get(defect_id, '<missing>')}"
            for defect_id in required_udl_ids
            if latest_statuses.get(defect_id) != "CLOSED_WITH_PROOF"
        )
        if non_closed_statuses:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: latest current-owned UDL rows are not closed "
                f"{non_closed_statuses}"
            )

    visual_udl_entries = [
        entry
        for entry in normalized_entries
        if "unified_visual_defect_ledger" in PurePosixPath(entry).name.lower()
    ]
    if not visual_udl_entries:
        failures.append(
            "FAM-003 LV1 packet semantic proof failed: visual Unified Defect Ledger is missing"
        )
    else:
        visual_udl_text = "\n".join(packet_files.get(entry, "") for entry in visual_udl_entries)
        if "VISUAL-UDL-SCHEMA-RETEST-STOP" not in visual_udl_text:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: visual UDL lacks the 125842 schema retest-stop receipt"
            )
        for schema_failure in _fam003_visual_udl_schema_failures(visual_udl_text):
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: " + schema_failure
            )
        rejected_current_packet_markers = (
            "Current regenerated USER retest packet: `C:\\Nexus USER\\FAM-003-20260623-125842.zip`",
            "Current packet is C:\\Nexus USER\\FAM-003-20260623-125842.zip",
            "Upload file: C:\\Nexus USER\\FAM-003-20260623-125842.zip",
        )
        for marker in rejected_current_packet_markers:
            if marker in visual_udl_text:
                failures.append(
                    "FAM-003 LV1 packet semantic proof failed: visual UDL still names rejected 125842 packet as current"
                )
                break

    fail_ledger_text = packet_files.get(
        "Source Truth Context/Proof Artifacts/Settings Visual Proof/FAIL_CAPABLE_DEFECT_LEDGER.md",
        "",
    )
    if fail_ledger_text and "Actual visual/product conformance | PASS" in fail_ledger_text:
        visual_udl_text = "\n".join(packet_files.get(entry, "") for entry in visual_udl_entries)
        if not visual_udl_entries or "UDL-VIS-014" not in visual_udl_text:
            failures.append(
                "FAM-003 LV1 packet semantic proof failed: visual PASS lacks visual UDL closure mapping"
            )

    return failures


def validate_local_user_packet(
    packet_dir: Path,
    *,
    export_zip: Path,
    worktree_label: str | None = None,
    validation_mode: str = PACKET_VALIDATION_MODE_ACTIVE_REVIEW,
    expected_branch: str | None = None,
    expected_head: str | None = None,
    expected_origin_main: str | None = None,
) -> LocalUserPacketValidationResult:
    if validation_mode not in PACKET_VALIDATION_MODES:
        raise ValueError(
            f"Unsupported packet validation mode {validation_mode!r}; "
            f"expected one of {', '.join(PACKET_VALIDATION_MODES)}"
        )
    label = _sanitize_folder_name(worktree_label or packet_dir.name)
    packet_dir = packet_dir.resolve()
    export_zip = export_zip.resolve()
    failures: list[str] = []

    if validation_mode == PACKET_VALIDATION_MODE_ACTIVE_REVIEW:
        missing_identity = [
            name
            for name, value in (
                ("expected branch", expected_branch),
                ("expected HEAD", expected_head),
                ("expected origin/main", expected_origin_main),
            )
            if not value or value.strip().upper() == "UNKNOWN"
        ]
        if missing_identity:
            failures.append(
                "Active-review packet validation requires explicit identity expectations: "
                + ", ".join(missing_identity)
            )

    if not packet_dir.is_dir():
        failures.append(f"Local USER packet folder is missing: {packet_dir}")
        return LocalUserPacketValidationResult(
            packet_dir=packet_dir,
            export_zip=export_zip,
            label=label,
            validation_mode=validation_mode,
            folder_file_count=0,
            zip_file_count=0,
            primary_user_review_files=(),
            failures=failures,
        )
    if not export_zip.is_file():
        failures.append(f"Timestamped USER packet ZIP is missing: {export_zip}")
        return LocalUserPacketValidationResult(
            packet_dir=packet_dir,
            export_zip=export_zip,
            label=label,
            validation_mode=validation_mode,
            folder_file_count=len(_bundle_files(packet_dir)),
            zip_file_count=0,
            primary_user_review_files=(),
            failures=failures,
        )

    review_root = packet_dir.parent.resolve()
    if export_zip.parent.resolve() != review_root:
        failures.append(
            "Timestamped USER packet ZIP must live beside the packet folder: "
            f"expected parent={review_root} actual parent={export_zip.parent.resolve()}"
        )
    name_failures = _timestamped_export_zip_name_failures(export_zip, label)
    failures.extend(name_failures)

    same_label_paths = _same_label_export_zip_paths(review_root, label)
    stale_siblings = sorted(path for path in same_label_paths if path != export_zip)
    if validation_mode != PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL:
        for stale_zip in stale_siblings:
            if stale_zip.exists():
                failures.append(f"Stale same-label USER packet ZIP remains: {stale_zip}")

    stable_zip = _legacy_stable_export_zip_path(review_root, label)
    if stable_zip.exists():
        failures.append(f"Stable-name USER packet ZIP is not allowed: {stable_zip}")

    folder_hashes = _folder_file_hashes(packet_dir)
    folder_entries = set(folder_hashes)
    folder_binary_files = _packet_binary_files(packet_dir)
    zip_packet_files: dict[str, str] = {}
    zip_binary_files: dict[str, bytes] = {}
    try:
        zip_hashes, duplicate_zip_entries = _zip_file_hashes(export_zip)
        zip_entries = set(zip_hashes)
        zip_packet_files = _zip_text_files(export_zip)
        zip_binary_files = _zip_binary_files(export_zip)
    except zipfile.BadZipFile as exc:
        failures.append(f"Review export ZIP is not readable: {export_zip}: {exc}")
        zip_hashes = {}
        duplicate_zip_entries = ()
        zip_entries = set()

    if duplicate_zip_entries:
        failures.append(
            "Folder/ZIP parity failed: duplicate ZIP entries are not allowed "
            f"entries={list(duplicate_zip_entries)}"
        )

    parity_entries_match = folder_entries == zip_entries
    if validation_mode != PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL and not parity_entries_match:
        missing = sorted(folder_entries - zip_entries)
        extra = sorted(zip_entries - folder_entries)
        failures.append(
            "Folder/ZIP parity failed: "
            f"missing from ZIP={missing or 'none'} extra in ZIP={extra or 'none'}"
        )
    elif validation_mode != PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL:
        content_mismatches = sorted(
            entry
            for entry in folder_entries
            if folder_hashes.get(entry) != zip_hashes.get(entry)
        )
        if content_mismatches:
            failures.append(
                "Folder/ZIP parity failed: matching file list but content hash mismatch "
                f"for entries={content_mismatches}"
            )

    embedded_zip_entries = sorted(
        entry
        for entry in folder_entries | zip_entries
        if PurePosixPath(entry).suffix.lower() == ".zip"
    )
    if embedded_zip_entries:
        failures.append(
            "Local USER packet must not embed ZIP artifacts; reference prior packets by "
            f"digest/receipt instead: entries={embedded_zip_entries}"
        )

    layout_entries = zip_entries if validation_mode == PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL else folder_entries
    layout_failures, primary_files = _local_user_packet_layout_failures(packet_dir, layout_entries)
    failures.extend(layout_failures)

    folder_packet_files = _packet_text_files(packet_dir)
    packet_files = zip_packet_files if validation_mode == PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL else (zip_packet_files or folder_packet_files)
    if validation_mode in {
        PACKET_VALIDATION_MODE_ACTIVE_REVIEW,
        PACKET_VALIDATION_MODE_NEXT_GATE,
    } and not any(
        "requires explicit identity expectations" in failure for failure in failures
    ):
        identity_mode_label = (
            "active-review"
            if validation_mode == PACKET_VALIDATION_MODE_ACTIVE_REVIEW
            else "next-gate"
        )
        identity_kwargs = {
            "expected_branch": expected_branch or "",
            "expected_head": expected_head or "",
            "expected_origin_main": expected_origin_main or "",
        }
        failures.extend(
            f"Folder {identity_mode_label} identity: {failure}"
            for failure in _packet_identity_failures(
                folder_packet_files,
                packet_binary_files=folder_binary_files,
                **identity_kwargs,
            )
        )
        if zip_packet_files:
            failures.extend(
                f"ZIP {identity_mode_label} identity: {failure}"
                for failure in _packet_identity_failures(
                    zip_packet_files,
                    packet_binary_files=zip_binary_files,
                    **identity_kwargs,
                )
            )
    failures.extend(_primary_review_substantive_failures(packet_files, primary_files))
    generated_packet_files = {
        name: text
        for name, text in packet_files.items()
        if not name.startswith(f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/")
    }
    failures.extend(_unresolved_template_placeholder_failures(generated_packet_files))
    failures.extend(_packet_count_consistency_failures(packet_files, actual_file_count=len(folder_entries)))
    failures.extend(_generic_user_facing_technical_metadata_failures(packet_files))
    failures.extend(_user_facing_technical_metadata_failures(generated_packet_files))
    failures.extend(_user_branch_plan_stale_bp1_wording_failures(generated_packet_files))
    failures.extend(_fam007_bp2_plan_substantive_failures(generated_packet_files))
    failures.extend(_fam007_bp2_support_bp1_context_failures(generated_packet_files))
    failures.extend(_bp1_packet_phase_language_failures(generated_packet_files))
    failures.extend(_user_branch_vision_substantive_failures(generated_packet_files))
    failures.extend(_branch_planning_review_gate_state_failures(generated_packet_files))
    failures.extend(_pr_stage1_review_failures(packet_files))
    failures.extend(_pr_stage1_packet_coherence_failures(packet_files))
    failures.extend(
        _pr_stage1_source_coverage_failures(
            packet_files,
            packet_entries=layout_entries,
        )
    )
    failures.extend(
        _fam003_lv1_visual_retest_semantic_failures(
            packet_files,
            packet_dir,
            folder_entries,
            export_zip,
        )
    )
    failures.extend(_active_review_aid_false_green_failures(packet_files))
    failures.extend(
        _source_truth_context_currentness_failures(
            packet_files,
            validation_mode=validation_mode,
            export_zip=export_zip,
        )
    )
    failures.extend(
        _final_zip_active_metadata_failures(
            packet_files,
            export_zip,
            validation_mode=validation_mode,
        )
    )
    if not any("Review export ZIP is not readable" in failure for failure in failures):
        failures.extend(
            _image_proof_failures(
                packet_dir,
                export_zip,
                layout_entries,
                validate_folder_images=validation_mode != PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL,
            )
        )
    failures.extend(_proof_manifest_false_green_failures(packet_files))

    return LocalUserPacketValidationResult(
        packet_dir=packet_dir,
        export_zip=export_zip,
        label=label,
        validation_mode=validation_mode,
        folder_file_count=len(folder_entries),
        zip_file_count=len(zip_entries),
        primary_user_review_files=primary_files,
        failures=failures,
    )


def _format_local_user_packet_validation_result(result: LocalUserPacketValidationResult) -> str:
    parity_failed = any("Folder/ZIP parity failed" in failure for failure in result.failures)
    lines = [
        f"USER Review Packet Finding: {'FAIL' if result.failures else 'PASS'}",
        f"Packet Folder: {result.packet_dir}",
        f"Review Export Zip: {result.export_zip}",
        f"Worktree Label: {result.label}",
        f"Packet Validation Mode: {result.validation_mode}",
        f"Folder File Count: {result.folder_file_count}",
        f"ZIP File Count: {result.zip_file_count}",
        "Primary USER Review Files: "
        + (", ".join(result.primary_user_review_files) if result.primary_user_review_files else "none"),
        "Timestamped ZIP: " + ("FAIL" if _timestamped_export_zip_name_failures(result.export_zip, result.label) else "PASS"),
        "Folder/ZIP Parity: "
        + (
            "FAIL"
            if parity_failed
            else "PASS"
            if result.folder_file_count == result.zip_file_count
            else "CHECK REQUIRED"
        ),
    ]
    if result.failures:
        lines.append("Failures:")
        lines.extend(f"- {failure}" for failure in result.failures)
    elif result.validation_mode == PACKET_VALIDATION_MODE_ACCEPTED_HISTORICAL:
        lines.append(
            "Final Packet Proof: PASS - accepted historical ZIP artifact validation used the timestamped ZIP "
            "as the immutable evidence record; current local folder parity is not required for historical ZIPs."
        )
    else:
        lines.append("Final Packet Proof: PASS - clean folder, timestamped ZIP, stale same-label ZIP cleanup, stable ZIP rejection, file-class layout, one-primary USER review file, folder/ZIP file-list plus content-hash parity, and FAM-003 LV1 PNG image-integrity gates where applicable are validated.")
    return "\n".join(lines)


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    start = text.find("\n", start)
    if start < 0:
        return ""
    next_heading = text.find("\n## ", start + 1)
    if next_heading < 0:
        return text[start:].strip()
    return text[start:next_heading].strip()


def _field_int(text: str, field_name: str) -> int | None:
    match = re.search(rf"^{re.escape(field_name)}:\s*(\d+)\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def _unresolved_template_placeholder_failures(packet_files: Mapping[str, str]) -> list[str]:
    failures: list[str] = []
    for file_name, text in sorted(packet_files.items()):
        for reason, pattern in UNRESOLVED_TEMPLATE_PATTERNS:
            matches = sorted({match.group(0) for match in pattern.finditer(text)})
            if matches:
                joined = ", ".join(matches)
                failures.append(f"{file_name}: unresolved template placeholder {reason}: {joined}")
    return failures


def _packet_count_consistency_failures(
    packet_files: Mapping[str, str],
    *,
    actual_file_count: int | None = None,
) -> list[str]:
    start_here = packet_files.get("START_HERE.md", "")
    if not start_here:
        return []
    parsed = {field: _field_int(start_here, field) for field in BUNDLE_COUNT_FIELDS}
    if all(value is None for value in parsed.values()):
        return []

    failures: list[str] = []
    for field, value in parsed.items():
        if value is None:
            failures.append(f"START_HERE.md: packet count field '{field}' is missing")

    bundle_file_count = parsed["Bundle File Count"]
    expected_file_count = parsed["Expected File Count"]
    copied_file_count = parsed["Copied File Count"]
    extra_bundle_file_count = parsed["Extra Bundle File Count"]
    if actual_file_count is None:
        actual_file_count = len(packet_files)

    if bundle_file_count is not None and bundle_file_count != actual_file_count:
        failures.append(
            "START_HERE.md: Bundle File Count "
            f"{bundle_file_count} does not match actual packet file count {actual_file_count}"
        )
    if (
        expected_file_count is not None
        and copied_file_count is not None
        and expected_file_count != copied_file_count
    ):
        failures.append(
            "START_HERE.md: Expected File Count "
            f"{expected_file_count} does not match Copied File Count {copied_file_count}"
        )
    if (
        bundle_file_count is not None
        and copied_file_count is not None
        and extra_bundle_file_count is not None
        and bundle_file_count != copied_file_count + extra_bundle_file_count + 1
    ):
        failures.append(
            "START_HERE.md: Bundle File Count must equal Copied File Count "
            f"+ Extra Bundle File Count + START_HERE.md; got {bundle_file_count}, "
            f"{copied_file_count}, {extra_bundle_file_count}"
        )
    return failures


def _user_facing_technical_metadata_failures(packet_files: Mapping[str, str]) -> list[str]:
    failures: list[str] = []
    for file_name in USER_FACING_GENERATED_FILES:
        text = _packet_file_text(packet_files, file_name)
        if not text:
            continue
        display_name = _packet_file_path(packet_files, file_name)
        for reason, pattern in USER_FACING_TECHNICAL_METADATA_PATTERNS:
            if pattern.search(text):
                failures.append(
                    f"{display_name}: USER-facing generated file contains technical metadata {reason}"
                )
    return failures


def _user_branch_plan_stale_bp1_wording_failures(packet_files: Mapping[str, str]) -> list[str]:
    text = _packet_file_text(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
    if not text:
        return []
    failures: list[str] = []
    display_name = _packet_file_path(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
    for reason, pattern in USER_BRANCH_PLAN_STALE_BP1_WORDING_PATTERNS:
        if pattern.search(text):
            failures.append(
                f"{display_name}: BP2 review contains stale BP1/product-design wording {reason}"
            )
    return failures


def _fam007_dev_owner_lv1_packet_detected(packet_files: Mapping[str, str]) -> bool:
    combined = "\n".join(
        (
            packet_files.get("START_HERE.md", ""),
            _packet_file_text(packet_files, USER_BRANCH_PLAN_REVIEW_FILE),
            _packet_file_text(packet_files, "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"),
            _packet_file_text(packet_files, "BRANCH_VISION_VALIDATION_CHECKLIST.md"),
        )
    ).casefold()
    return (
        "fam-007 dev/owner skeleton readiness" in combined
        and "live validation lv1 is green" in combined
        and "pr readiness stage 1 remains pending user approval" in combined
    )


def _fam007_dev_owner_lv1_substantive_failures(packet_files: Mapping[str, str]) -> list[str]:
    if not _fam007_dev_owner_lv1_packet_detected(packet_files):
        return []

    text = _packet_file_text(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
    combined = "\n".join(
        _packet_file_text(packet_files, file_name)
        for file_name in USER_FACING_GENERATED_FILES
    ).casefold()
    display_name = _packet_file_path(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
    failures: list[str] = []
    required_headings = (
        "## Live Validation LV1 No-Visible-Runtime Proof",
        "## UTS Waiver Evidence",
        "## PR Readiness Stage 1 Preview",
        "## Future USER Gate Matrix",
    )
    for heading in required_headings:
        if heading not in text:
            failures.append(f"{display_name}: FAM-007 LV1 packet is missing {heading}")

    required_markers = (
        "no visible surface changed",
        "uts is waived",
        "stage 1 must not create a pr",
        "provider/model/runtime/cache/memory",
        "private dev/owner setup",
    )
    for marker in required_markers:
        if marker not in combined:
            failures.append(f"{display_name}: FAM-007 LV1 packet is missing marker '{marker}'")

    forbidden_markers = (
        "live validation lv1 remains pending",
        "approve bounded live validation lv1",
        "hardening final decision review",
        "workstream entry final decision review",
    )
    for marker in forbidden_markers:
        if marker in combined:
            failures.append(f"{display_name}: FAM-007 LV1 packet contains stale marker '{marker}'")
    return failures


def _fam007_bp2_plan_substantive_failures(packet_files: Mapping[str, str]) -> list[str]:
    """Block FAM-007 BP2-primary packets that still read like BP2 previews."""

    start_here = packet_files.get("START_HERE.md", "")
    if "USER Review/USER_BRANCH_PLAN_REVIEW.md" not in start_here:
        return []

    text = _packet_file_text(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
    combined = f"{start_here}\n{text}".casefold()
    owner_ai_foundation_packet = (
        "owner ai operational foundation gates" in combined
        or "feature/fam-007-owner-ai-operational-foundation-gates" in combined
    )
    dev_owner_skeleton_packet = (
        "fam-007 dev/owner skeleton readiness" in combined
        or "dev/owner skeleton readiness" in combined
    )
    if not owner_ai_foundation_packet and not dev_owner_skeleton_packet:
        return []
    if _fam007_dev_owner_lv1_packet_detected(packet_files):
        return []

    failures: list[str] = []
    display_name = _packet_file_path(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
    forbidden_patterns: tuple[tuple[str, re.Pattern[str]], ...] = (
        (
            "bp2-preview-future-gated",
            re.compile(r"\bBP2 preview\b.*\bfuture-gated\b", re.IGNORECASE | re.DOTALL),
        ),
        (
            "review-accepted-bp1-first-preview",
            re.compile(r"Review accepted BP1 first; this BP2 preview", re.IGNORECASE),
        ),
        (
            "pending-accepted-or-waived-bp1-trace",
            re.compile(r"Pending accepted or waived BP1 trace", re.IGNORECASE),
        ),
        (
            "bp2-pending-until-bp1",
            re.compile(r"BP2 is pending until BP1 is accepted", re.IGNORECASE),
        ),
        (
            "cannot-green-while-bp1-pending",
            re.compile(r"cannot become green while BP1 is pending", re.IGNORECASE),
        ),
        (
            "generic-product-feedback-prompt",
            re.compile(
                r"visual direction,\s*workflow changes,\s*window behavior,\s*"
                r"output-file expectations",
                re.IGNORECASE,
            ),
        ),
    )
    for reason, pattern in forbidden_patterns:
        if pattern.search(text):
            failures.append(f"{display_name}: FAM-007 BP2 packet contains stale preview wording {reason}")

    external_plan_section = _section(
        text, "Active External Branch Plan / Historical Branch Plan Files"
    ).casefold()
    if "none recorded" in external_plan_section:
        failures.append(
            f"{display_name}: FAM-007 BP2 packet must name active external branch plan/state context"
        )

    required_headings = (
        (
            "## Owner AI Foundation Gate Matrix",
            "## Protected Artifact Exclusion Matrix",
            "## Consent / Runtime Disabled-State Matrix",
            "## Memory / Cache Consent Matrix",
            "## Capability Install-Intent Matrix",
            "## Developer / Owner Lane Readiness Matrix",
            "## Owner AI Memory / Agent Schema Matrix",
            "## Proof / Validation Matrix",
            "## Future USER Gate Matrix",
            "## Per-SLC / Per-Seam Engineering Plan",
            "## Cross-Slice Dependencies And Execution Order",
            "## Expanded Open Engineering Risks",
            "## H1 / Hardening Expectations By Slice",
            "## Live Validation / UTS Inspection Expectations",
            "## BP3 Verification Checklist By SLC",
            "## Branch-Size Route-Back Criteria",
        )
        if owner_ai_foundation_packet
        else (
            "## Integrated Dev/Owner Readiness Matrix",
            "## Edition / Lane Matrix",
            "## Dev Readiness Matrix",
            "## Owner Readiness Matrix",
            "## Private Root / Remote Matrix",
            "## GitHub Desktop Binding Matrix",
            "## Backup / Import Matrix",
            "## Provider / Runtime / Cache / Memory Deferral Matrix",
            "## Watermark / Identity Matrix",
            "## Proof / Validation Matrix",
            "## Future USER Gate Matrix",
        )
    )
    for heading in required_headings:
        if heading not in text:
            failures.append(f"{display_name}: FAM-007 BP2 packet is missing {heading}")

    if owner_ai_foundation_packet:
        required_owner_ai_markers = (
            "SLC-001 / Seam 1",
            "SLC-001 / Seam 2",
            "SLC-002 / Seam 1",
            "SLC-002 / Seam 2",
            "SLC-003 / Seam 1",
            "SLC-003 / Seam 2",
            "SLC-004 / Seam 1",
            "SLC-004 / Seam 2",
            "SLC-005 / Seam 1",
            "SLC-005 / Seam 2",
            "SLC-006 / Seam 1",
            "SLC-006 / Seam 2",
            "Likely files / surfaces",
            "Concrete behavior or control target",
            "Disabled / no-execution proof",
            "Stop / report condition",
            "protected-class drift",
            "fake disabled states",
            "cache wording masquerading as memory",
            "branch-size route-back",
        )
        for marker in required_owner_ai_markers:
            if marker.casefold() not in text.casefold():
                failures.append(
                    f"{display_name}: FAM-007 Owner AI BP2 packet missing required detail marker {marker!r}"
                )

    accepted_trace = _section(text, "Accepted Branch Vision Summary").casefold()
    accepted_trace_ok = (
        "bp1 accepted" in accepted_trace
        and "owner ai operational foundation gates" in accepted_trace
        if owner_ai_foundation_packet
        else "bp1 accepted" in accepted_trace and "option a" in accepted_trace
    )
    if not accepted_trace_ok:
        failures.append(
            f"{display_name}: FAM-007 BP2 packet missing accepted BP1 trace"
        )
    return failures


def _fam007_bp2_support_bp1_context_failures(packet_files: Mapping[str, str]) -> list[str]:
    """Block BP2 packets whose supporting BP1 file still reads as pending BP1."""

    start_here = packet_files.get("START_HERE.md", "")
    if "USER Review/USER_BRANCH_PLAN_REVIEW.md" not in start_here:
        return []

    primary = _packet_file_text(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
    combined = f"{start_here}\n{primary}".casefold()
    if "fam-007 dev/owner skeleton readiness" not in combined:
        return []
    if _fam007_dev_owner_lv1_packet_detected(packet_files):
        return []

    support = _packet_file_text(packet_files, USER_BRANCH_VISION_REVIEW_FILE)
    display_name = _packet_file_path(packet_files, USER_BRANCH_VISION_REVIEW_FILE)
    if not support:
        return [f"{display_name}: BP2 packet is missing supporting accepted BP1 context"]

    failures: list[str] = []
    contract_status = _section(support, "Contract Status").casefold()
    user_gate_state = _section(support, "USER Gate State").casefold()
    accepted_vision = _section(support, "Accepted Branch Vision").casefold()
    if not contract_status.startswith(("complete", "waived by user")):
        failures.append(
            f"{display_name}: supporting BP1 context Contract Status must be Complete or Waived by USER for a BP2-primary packet"
        )
    if not user_gate_state.startswith(("user accepted", "user waived")):
        failures.append(
            f"{display_name}: supporting BP1 context USER Gate State must record USER Accepted or USER Waived for a BP2-primary packet"
        )
    if "accepted by user" not in accepted_vision and "waived by user" not in accepted_vision:
        failures.append(
            f"{display_name}: supporting BP1 context Accepted Branch Vision must record accepted or waived BP1 context"
        )

    forbidden_patterns: tuple[tuple[str, re.Pattern[str]], ...] = (
        (
            "draft-contract-status",
            re.compile(r"Draft - update to Complete or Waived by USER", re.IGNORECASE),
        ),
        (
            "pending-bp1-user-gate",
            re.compile(r"Pending USER Review - USER must accept, revise, waive, reject, or block BP1", re.IGNORECASE),
        ),
        (
            "final-bp1-acceptance-pending",
            re.compile(r"Final BP1 acceptance remains pending", re.IGNORECASE),
        ),
        (
            "bp1-remains-open",
            re.compile(r"BP1 remains open", re.IGNORECASE),
        ),
        (
            "pending-user-acceptance-or-waiver",
            re.compile(r"Pending USER acceptance or waiver", re.IGNORECASE),
        ),
        (
            "not-final-bp1-acceptance",
            re.compile(r"not final BP1 acceptance", re.IGNORECASE),
        ),
    )
    for reason, pattern in forbidden_patterns:
        if pattern.search(support):
            failures.append(
                f"{display_name}: supporting BP1 context contains stale pending-BP1 wording {reason}"
            )
    return failures


def _bp1_packet_phase_language_failures(packet_files: Mapping[str, str]) -> list[str]:
    combined = "\n".join(
        _packet_file_text(packet_files, file_name)
        for file_name in USER_FACING_GENERATED_FILES
    ).casefold()
    if "bp1 branch vision" not in combined or "authorize bp2 user branch plan review only" not in combined:
        return []

    failures: list[str] = []
    for file_name in USER_FACING_GENERATED_FILES:
        text = _packet_file_text(packet_files, file_name)
        if not text:
            continue
        for reason, pattern in BP1_PACKET_STALE_LANGUAGE_PATTERNS:
            if pattern.search(text):
                failures.append(
                    f"{_packet_file_path(packet_files, file_name)}: BP1 packet contains stale phase/boundary language {reason}"
                )
    return failures


def _is_fam006_bp3_orchestration_packet(packet_files: Mapping[str, str]) -> bool:
    start_here = packet_files.get("START_HERE.md", "")
    workstream_digest = _packet_file_text(packet_files, "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md")
    combined = f"{start_here}\n{workstream_digest}".replace("\\", "/").casefold()
    return (
        "bp3 orchestration review" in combined
        and "fam-006" in combined
        and "recording" in combined
        and "option c" in combined
    )


def _fam006_bp3_support_context_failures(packet_files: Mapping[str, str]) -> list[str]:
    if not _is_fam006_bp3_orchestration_packet(packet_files):
        return []

    stale_patterns = (
        (
            "bp2-remains-pending",
            re.compile(r"\bBP2 remains Pending USER Review\b", re.IGNORECASE),
        ),
        (
            "active-response-bp2",
            re.compile(r"active USER response now belongs to the BP2 Branch Plan Review", re.IGNORECASE),
        ),
        (
            "primary-decision-bp2-file",
            re.compile(r"primary active decision is USER Review/USER_BRANCH_PLAN_REVIEW\.md", re.IGNORECASE),
        ),
        (
            "bp2-must-answer-option-c",
            re.compile(r"BP2 must answer whether Option C", re.IGNORECASE),
        ),
        (
            "bp3-may-be-prepared-after-bp2",
            re.compile(r"BP3 may be prepared only after BP2 is accepted or waived", re.IGNORECASE),
        ),
        (
            "prepared-bp2-around-option-c",
            re.compile(r"prepared BP2 around Option C", re.IGNORECASE),
        ),
        (
            "accepted-for-bp2-planning",
            re.compile(r"Accepted for BP2 planning", re.IGNORECASE),
        ),
        (
            "bp2-reviewability-boundary",
            re.compile(r"Keep BP2 reviewability separate from USER acceptance", re.IGNORECASE),
        ),
    )

    failures: list[str] = []
    for file_name, text in sorted(packet_files.items()):
        normalized_path = file_name.replace("\\", "/")
        if normalized_path.startswith(f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/"):
            continue
        if _packet_file_basename(file_name) not in USER_FACING_GENERATED_FILES:
            continue
        for reason, pattern in stale_patterns:
            if pattern.search(text):
                failures.append(
                    f"{file_name}: FAM-006 BP3 generated support file contains stale BP2-active wording {reason}"
                )
    return failures


def _review_word_count(value: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", value))


def _user_branch_vision_substantive_failures(packet_files: Mapping[str, str]) -> list[str]:
    text = _packet_file_text(packet_files, USER_BRANCH_VISION_REVIEW_FILE)
    if not text:
        return []
    failures: list[str] = []
    display_name = _packet_file_path(packet_files, USER_BRANCH_VISION_REVIEW_FILE)
    start_here = _packet_file_text(packet_files, "START_HERE.md")
    normalized_start_here = start_here.casefold()
    normalized_text = text.casefold()
    current_bp1_decision_packet = (
        "bp1 branch vision review" in normalized_start_here
        and "authorize bp2 user branch plan review only if bp1" in normalized_start_here
    )
    if current_bp1_decision_packet:
        for reason, pattern in (
            (
                "accepted-user-state",
                re.compile(r"\bAccepted by USER\b", re.IGNORECASE),
            ),
            (
                "active-bp2-state",
                re.compile(r"\bactive BP2\b|\bBP2 is the active gate\b", re.IGNORECASE),
            ),
            (
                "supporting-accepted-bp1-context",
                re.compile(r"supporting accepted BP1 context|accepted BP1 context", re.IGNORECASE),
            ),
        ):
            if pattern.search(text):
                failures.append(
                    f"{display_name}: current BP1 packet must not contain {reason}"
                )
    private_boundary_packet = (
        "feature/fam-007-dev-owner-private-boundary-setup" in normalized_start_here
        or "private-boundary setup" in normalized_start_here
    )
    if private_boundary_packet:
        for reason, pattern in (
            (
                "prior-active-skeleton-carrier",
                re.compile(r"Dev/Owner Skeleton Readiness carrier", re.IGNORECASE),
            ),
            (
                "prior-skeleton-branch-vision",
                re.compile(r"Dev/Owner Skeleton Readiness Branch Vision", re.IGNORECASE),
            ),
            (
                "prior-accepted-option-a-trace",
                re.compile(r"accepted BP1 Option A|USER selected the integrated Option A", re.IGNORECASE),
            ),
        ):
            if pattern.search(text):
                failures.append(
                    f"{display_name}: private-boundary BP1 packet contains stale {reason}"
                )
    if current_bp1_decision_packet and "pending user" not in normalized_text:
        failures.append(
            f"{display_name}: current BP1 packet must keep USER acceptance pending until USER responds"
        )
    owner_ai_foundation_packet = (
        "feature/fam-007-owner-ai-operational-foundation-gates" in normalized_start_here
        or "owner ai operational foundation gates" in normalized_start_here
        or "operational foundation gates" in normalized_start_here
    )
    if owner_ai_foundation_packet:
        for reason, pattern in (
            (
                "prior-private-boundary-carrier",
                re.compile(r"feature/fam-007-dev-owner-private-boundary-setup", re.IGNORECASE),
            ),
            (
                "prior-private-boundary-route",
                re.compile(r"private-boundary setup|private boundary setup", re.IGNORECASE),
            ),
            (
                "prior-skeleton-route",
                re.compile(r"Dev/Owner Skeleton Readiness|skeleton readiness", re.IGNORECASE),
            ),
        ):
            if pattern.search(text):
                failures.append(
                    f"{display_name}: Owner AI foundation BP1 packet contains stale {reason}"
                )

    for field_name in (
        "Packet Reviewability State",
        "USER Gate State",
        "USER Response Proof",
        "USER Response Digested",
    ):
        if not _field_value(text, field_name) and not _section(text, field_name):
            failures.append(
                f"{display_name}: BP1 substantive review artifact missing {field_name}"
            )

    for section_name, minimum_words in USER_BRANCH_VISION_MINIMUM_SUBSTANTIVE_SECTIONS:
        value = _section(text, section_name)
        if _review_word_count(value) < minimum_words:
            failures.append(
                f"{display_name}: {section_name} is too shallow for BP1 substantive review"
            )

    for reason, pattern in USER_BRANCH_VISION_TEMPLATE_SHELL_PATTERNS:
        if pattern.search(text):
            failures.append(
                f"{display_name}: template-shell BP1 wording remains ({reason})"
            )

    surface_map = _section(text, "Surface Map")
    normalized_surface_map = re.sub(r"\s+", " ", surface_map).casefold()
    if " copied as " in normalized_surface_map and not any(
        term in normalized_surface_map
        for term in (
            "decision surface",
            "experience surface",
            "review surface",
            "user will see",
            "owner",
        )
    ):
        failures.append(
            f"{display_name}: copied-file list cannot be the BP1 Surface Map"
        )

    user_questions = _section(text, "USER Design Questions")
    question_count = user_questions.count("?")
    if question_count < 2:
        failures.append(
            f"{display_name}: USER Design Questions must ask branch-specific decision-driving questions"
        )

    recommendations = _section(text, "Codex Recommendations")
    normalized_recommendations = recommendations.casefold()
    if "recommendation" not in normalized_recommendations or not any(
        term in normalized_recommendations for term in ("tradeoff", "risk", "because")
    ):
        failures.append(
            f"{display_name}: Codex Recommendations must be branch-specific line-item recommendations with rationale and tradeoffs"
        )
    return failures


def _start_here_file_mappings(start_here: str) -> dict[str, str]:
    mappings: dict[str, str] = {}
    row_pattern = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", re.MULTILINE)
    for source_path, copied_path in row_pattern.findall(start_here):
        mappings[source_path.replace("\\", "/")] = copied_path.replace("\\", "/")
    return mappings


def _git_file_text(ref: str, source_path: str) -> str | None:
    data = _git_file_bytes(ref, source_path)
    return data.decode("utf-8", errors="replace") if data is not None else None


def _git_file_bytes(ref: str, source_path: str) -> bytes | None:
    try:
        return subprocess.check_output(
            ["git", "show", f"{ref}:{source_path}"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None


def _normalized_packet_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _requires_source_context_mapping(path: str) -> bool:
    """Distinguish copied repo files from generated evidence context."""

    prefix = f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/"
    if not path.startswith(prefix):
        return False
    relative = path[len(prefix) :]
    if relative.startswith("current_external_"):
        return False
    if relative.startswith("Proof Artifacts/"):
        return False
    if relative.startswith("UTS Context/"):
        return False
    if relative == "MISSING_SOURCE_FILES.md":
        return False
    return True


def _packet_identity_failures(
    packet_files: Mapping[str, str],
    *,
    packet_binary_files: Mapping[str, bytes] | None = None,
    expected_branch: str,
    expected_head: str,
    expected_origin_main: str,
) -> list[str]:
    failures: list[str] = []
    current_branch = _git_output("rev-parse", "--abbrev-ref", "HEAD")
    current_head = _git_output("rev-parse", "HEAD")
    current_origin_main = _git_output("rev-parse", "origin/main")

    if current_branch != expected_branch:
        failures.append(
            "Packet identity: expected branch "
            f"{expected_branch!r} does not match current branch {current_branch!r}"
        )
    if current_head != expected_head:
        failures.append(
            "Packet identity: expected HEAD "
            f"{expected_head!r} does not match current HEAD {current_head!r}"
        )
    if current_origin_main != expected_origin_main:
        failures.append(
            "Packet identity: expected origin/main "
            f"{expected_origin_main!r} does not match current origin/main {current_origin_main!r}"
        )

    start_here = packet_files.get("START_HERE.md", "")
    file_mappings = _start_here_file_mappings(start_here)
    if not file_mappings:
        failures.append("START_HERE.md: source/copy file mapping table is missing")
        return failures

    mapped_paths = set(file_mappings.values())
    packet_paths = set(packet_files)
    if packet_binary_files is not None:
        packet_paths.update(packet_binary_files)
    unmapped_source_context = sorted(
        path
        for path in packet_paths
        if _requires_source_context_mapping(path)
        and path not in mapped_paths
    )
    failures.extend(
        "Packet identity: copied Source Truth Context file is not mapped in START_HERE.md: "
        f"{path}"
        for path in unmapped_source_context
    )

    for source_path, copied_path in file_mappings.items():
        if (
            packet_binary_files is not None
            and copied_path in packet_binary_files
            and PurePosixPath(copied_path).suffix.lower() not in {".md", ".txt", ".json"}
        ):
            expected_bytes = _git_file_bytes(expected_head, source_path)
            if expected_bytes is None:
                failures.append(
                    "Packet identity: copied source path is not present at expected HEAD: "
                    f"{source_path}"
                )
                continue
            if packet_binary_files[copied_path] != expected_bytes:
                failures.append(
                    "Packet identity: copied file does not match expected HEAD content: "
                    f"{copied_path} from {source_path}"
                )
            continue
        packet_text = packet_files.get(copied_path)
        if packet_text is None:
            if packet_binary_files is not None:
                failures.append(
                    "Packet identity: mapped copied source path is missing from packet: "
                    f"{copied_path} from {source_path}"
                )
            continue
        expected_text = _git_file_text(expected_head, source_path)
        if expected_text is None:
            failures.append(
                "Packet identity: copied source path is not present at expected HEAD: "
                f"{source_path}"
            )
            continue
        if _normalized_packet_text(packet_text) != _normalized_packet_text(expected_text):
            failures.append(
                "Packet identity: copied file does not match expected HEAD content: "
                f"{copied_path} from {source_path}"
            )
    return failures


def _user_facing_decision_text(exact_user_decision: str) -> str:
    """Keep USER files decision-focused while chat/helper output carries byte proof."""

    text = re.sub(
        r"\b[0-9a-f]{40}\b",
        "[current commit recorded in Codex chat digest]",
        exact_user_decision,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bHEAD\b",
        "current commit recorded in Codex chat digest",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\borigin/main(?:@[A-Za-z0-9_.-]+)?\b",
        "current main baseline recorded in Codex chat digest",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\blive PR state\b|\bPR state\b",
        "PR-readiness review posture",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\bvalidation health\b|\bvalidation status\b",
        "validation review expectations",
        text,
        flags=re.IGNORECASE,
    )
    return text


def _is_repo_relative_review_path(path: str) -> bool:
    if not isinstance(path, str) or not path:
        return False
    if "://" in path or path.startswith("~"):
        return False
    if Path(path).is_absolute() or PurePosixPath(path).is_absolute():
        return False
    windows_path = PureWindowsPath(path)
    if windows_path.is_absolute() or windows_path.drive or windows_path.root:
        return False
    parts = set(PurePosixPath(path).parts) | set(windows_path.parts)
    return ".." not in parts


def _public_review_bundle_file_list_failures(paths: list[str]) -> list[str]:
    failures: list[str] = []
    for path in paths:
        normalized = path.replace("\\", "/")
        if not _is_repo_relative_review_path(path):
            failures.append(f"{path}: public review bundle file list must stay repo-relative")
        for reason, pattern in PRIVATE_REVIEW_BUNDLE_PATH_PATTERNS:
            if pattern.search(normalized):
                failures.append(f"{path}: public review bundle file list matched {reason}")
    return failures


def _write_user_branch_vision_review(
    *,
    target: Path,
    title: str,
    review_purpose: str,
    exact_user_decision: str,
    pending_user_decisions: list[str],
    copied: list[tuple[str, str]],
) -> Path:
    source_file_names = [source_rel for source_rel, _copied_rel in copied]
    copied_context = ", ".join(f"`{source_rel}`" for source_rel in source_file_names[:5])
    if len(source_file_names) > 5:
        copied_context += f", plus {len(source_file_names) - 5} more source-truth files"
    if not copied_context:
        copied_context = "the selected source-truth files"
    decision_text = exact_user_decision.casefold()
    review_profile_text = " ".join([title, review_purpose, exact_user_decision]).casefold()
    current_bp1_review_packet = (
        "bp1 branch vision review" in review_profile_text
        and (
            "authorize bp2 user branch plan review only if bp1" in decision_text
            or "authorize bp2 user branch plan review preparation only" in decision_text
            or "authorize bp2 preparation only" in decision_text
        )
    )
    pr_readiness_context_packet = "pr readiness stage 1 analysis" in decision_text
    bp2_context_packet = (
        (
            "bp2 user branch plan review" in decision_text
            or "bp2 branch plan review" in decision_text
        )
        and not current_bp1_review_packet
    )
    bp3_context_packet = (
        not current_bp1_review_packet
        and (
            "bp3" in decision_text
            or "workstream entry / orchestration" in decision_text
            or "orchestration validation" in decision_text
        )
    )
    hardening_h1_context_packet = (
        "approve bounded hardening h1" in decision_text
        and (
            "feature/fam-007-dev-owner-skeleton-readiness" in decision_text
            or "dev/owner skeleton readiness" in decision_text
        )
    )
    live_validation_context_packet = (
        "approve bounded live validation lv1" in decision_text
        and (
            "feature/fam-007-dev-owner-skeleton-readiness" in decision_text
            or "dev/owner skeleton readiness" in decision_text
        )
    )
    fam006_workstream_approval_context_packet = (
        _is_fam006_workstream_implementation_approval_review(
            decision_text,
            is_fam006_recording=True,
        )
    )
    bp2_or_later_context_packet = (
        bp2_context_packet
        or bp3_context_packet
        or fam006_workstream_approval_context_packet
        or hardening_h1_context_packet
        or live_validation_context_packet
    )
    active_planning_gate = (
        "Workstream implementation approval"
        if fam006_workstream_approval_context_packet
        else
        "Live Validation LV1"
        if live_validation_context_packet
        else
        "Hardening H1"
        if hardening_h1_context_packet
        else "BP3"
        if bp3_context_packet
        else "BP2"
    )
    review_status = (
        "Context Complete - this packet uses BP1 as review context for PR Readiness Stage 1; "
        "it does not request a new Branch Vision decision."
        if pr_readiness_context_packet
        else (
            "Accepted by USER - this packet uses the accepted BP1 Branch Vision as "
            f"supporting context for {active_planning_gate}; it does not request "
            "a new BP1 decision."
        )
        if bp2_or_later_context_packet
        else "Needs USER Decision unless this packet records an explicit USER acceptance or waiver."
    )
    contract_status = (
        "Complete - Branch Vision context is recorded for this PR Readiness review packet; "
        "implementation remains outside this decision."
        if pr_readiness_context_packet
        else (
            "Complete - BP1 Branch Vision accepted by USER and used as accepted "
            f"context for this {active_planning_gate} packet."
        )
        if bp2_or_later_context_packet
        else "Draft - update to Complete or Waived by USER only after USER accepts or waives BP1 for this branch."
    )
    user_response = (
        "No new BP1 response requested by this packet; PR Readiness Stage 1 analysis remains the next USER decision."
        if pr_readiness_context_packet
        else (
            f"BP1 accepted by USER; {active_planning_gate} is the active USER decision in this packet."
        )
        if bp2_or_later_context_packet
        else "Pending USER response or explicit waiver."
    )
    packet_reviewability_state = (
        "Reviewable - context packet for later-phase review; no new BP1 decision is requested by this helper output."
        if pr_readiness_context_packet
        else (
            f"Reviewable - supporting accepted BP1 context for the active {active_planning_gate} packet."
        )
        if bp2_or_later_context_packet
        else "Reviewable - BP1 packet is ready for USER Branch Vision Review, but acceptance is not recorded."
    )
    user_gate_state = (
        "Superseded - context-only BP1 copy for later-phase review; rely on the accepted branch record or external state for the original BP1 receipt."
        if pr_readiness_context_packet
        else (
            f"USER Accepted - BP1 Branch Vision accepted by USER; {active_planning_gate} is the active gate."
        )
        if bp2_or_later_context_packet
        else "Pending USER Review - USER must accept, revise, waive, reject, or block BP1 before BP2 preparation can be green."
    )
    codex_digest = (
        "Codex records this BP1 file as a context aid for the governance lifecycle reform packet. "
        "Accepted outcomes must fold into durable source-truth owners or external operational state."
        if pr_readiness_context_packet
        else (
            "Codex records the accepted BP1 Option A direction as the planning basis for BP2: "
            "integrated Dev/Owner readiness, future private Dev repo direction after approval, "
            "Owner local-private baseline, GitHub Desktop safety, backup/import lane posture, "
            "provider/runtime/cache/memory deferral, proof expectations, and lane identity labels."
        )
        if bp2_or_later_context_packet
        else "Pending USER response digest."
    )
    accepted_vision = (
        "Accepted context: Governance Phase Lifecycle Reform and local USER hub model are represented by the copied source-truth files."
        if pr_readiness_context_packet
        else (
            "Accepted by USER - integrated Option A Dev/Owner Skeleton Readiness Branch Vision. "
            "Dev and Owner readiness stay planned together in one public-safe trust-boundary package; "
            "future Dev is private-repo-oriented after approval; Owner remains local-private by default; "
            "GitHub Desktop/public-upstream safety, backup/import posture, provider/runtime/cache/memory "
            "deferral, proof expectations, and lane identity labels are BP2 planning requirements."
        )
        if bp2_or_later_context_packet
        else "Pending USER acceptance or waiver."
    )
    if fam006_workstream_approval_context_packet:
        lines = [
            f"# USER Branch Vision Review - {title}",
            "",
            "## Review Status",
            "",
            "Accepted BP1 Context - this file supports the active Workstream implementation approval packet and does not request a new BP1 decision.",
            "",
            "## Contract Status",
            "",
            "Complete - USER accepted the revised FAM-006 Recording Branch Vision after Option F planning solidification.",
            "",
            "## Packet Reviewability State",
            "",
            "Reviewable - accepted BP1 context for the active Workstream implementation approval review packet.",
            "",
            "## USER Gate State",
            "",
            "USER Accepted - BP1 Branch Vision accepted by USER; BP2 and BP3 are also accepted; Workstream/runtime implementation approval remains Pending USER Review.",
            "",
            "## Accepted Branch Vision",
            "",
            "- USER Accepted - BP1 Branch Vision accepted by USER after Option F planning solidification.",
            "- BP2 answered: Option C was accepted by USER as the Branch Plan.",
            "- BP3 answered: Option C was accepted by USER as one coherent bounded Workstream package.",
            "- Dashboard Recording Card remains the compact quick-access/status surface.",
            "- Recording Studio is admitted as the focused recording control/status surface.",
            "- Minimal Log Viewer Studio launch/folder shell is admitted only where it supports native/export log access.",
            "- Native/export log boundary, open-folder pre-session usability, and issue #258 target reliability stay inside the accepted Option C package.",
            "- SLC-051 / Seam 1 target reliability may be the first entry checkpoint, but Single-seam or single-slice authority is not granted.",
            "",
            "## Workstream Approval Boundary",
            "",
            "Workstream/runtime implementation remains pending until USER approves the primary Workstream implementation approval packet. A green first seam is continuation proof, not package completion.",
            "",
            "## Exact USER Decision Supported",
            "",
            exact_user_decision,
            "",
        ]
        review_path = target / USER_BRANCH_VISION_REVIEW_FILE
        review_path.write_text("\n".join(lines), encoding="utf-8")
        return review_path.resolve()
    profile_text = " ".join(
        [title, review_purpose, exact_user_decision, *source_file_names]
    ).casefold().replace("_", "-")
    fam007_dev_owner_bp1_packet = (
        "fam-007" in profile_text
        and (
            "dev-owner-skeleton-readiness" in profile_text
            or "dev/owner skeleton readiness" in profile_text
        )
        and not pr_readiness_context_packet
    )
    fam007_private_boundary_bp1_packet = (
        "fam-007" in profile_text
        and (
            "dev-owner-private-boundary-setup" in profile_text
            or "private-boundary setup" in profile_text
            or "private boundary setup" in profile_text
        )
        and not pr_readiness_context_packet
    )
    fam007_owner_ai_foundation_bp1_packet = (
        "fam-007" in profile_text
        and (
            "owner-ai-operational-foundation-gates" in profile_text
            or "owner ai operational foundation gates" in profile_text
            or "operational foundation gates" in profile_text
        )
        and not pr_readiness_context_packet
    )
    if fam007_owner_ai_foundation_bp1_packet and bp2_or_later_context_packet:
        lines = [
            f"# {title} - Accepted BP1 Branch Vision Context",
            "",
            "USER Branch Vision Review: BP1",
            "",
            "## Review Status",
            "",
            f"Accepted BP1 context for the active {active_planning_gate} packet.",
            "",
            "## Contract Status",
            "",
            "Complete - USER accepted the repaired FAM-007 Owner AI Operational Foundation Gates Branch Vision for BP2 generation.",
            "",
            "## Packet Reviewability State",
            "",
            f"Reviewable - supporting accepted BP1 context for the active {active_planning_gate} packet.",
            "",
            "## USER Gate State",
            "",
            f"USER Accepted - BP1 Branch Vision accepted by USER; {active_planning_gate} is the active gate.",
            "",
            "## Contract Revision",
            "",
            "v2 - accepted repaired BP1 Branch Vision context for FAM-007 Owner AI Operational Foundation Gates.",
            "",
            "## Project Vision Context",
            "",
            "Nexus is Windows-first, local-first, modular, inspectable, privacy-aware, and USER-controlled. The accepted Branch Vision supports that project direction by requiring visible gates, deterministic disabled states, and reviewable public-safe controls before any private setup, provider execution, runtime cache, persistent memory, real agents, backup/import execution, PR, merge, release, or cleanup action exists.",
            "",
            "## Family Vision Context",
            "",
            "FAM-007 owns local AI, capability packs, provider readiness, consent posture, provider-visible data boundaries, execution gates, memory and cache boundaries, and User/Public, Developer, and Owner lane separation. The accepted BP1 applies that family vision to a public-safe gate package that prepares later Owner AI work without activating private repositories, provider behavior, memory, cache, or agents.",
            "",
            "## Feature Vision Context",
            "",
            "The accepted feature route is Owner AI Operational Foundation Gates. The branch is implementation-bearing because later Workstream can create or enforce concrete public-safe controls: protected artifact exclusion, disabled provider/runtime consent shells, memory/cache consent gates, install-intent gates, Developer/Owner lane readiness gates, and Owner AI memory/agent foundation gate schemas.",
            "",
            "## Codex Understanding",
            "",
            "Codex understands this file as supporting BP1 context for BP2. The accepted vision says the branch should make future Owner AI safer by defining a public-safe control plane that blocks leakage, names consent states, separates cache from memory, makes capability installation intentional, distinguishes lanes, and describes future memory/agent prerequisites as schemas and gates rather than live Owner AI behavior.",
            "",
            "## Branch Goal",
            "",
            "The accepted BP1 goal is to proceed with BP2 engineering planning for a grouped Owner AI foundation-gate package while preserving private setup, runtime execution, provider/model behavior, persistent memory, real agents, backup/import execution, PR, merge, release, cleanup, issue mutation, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work as later USER decisions.",
            "",
            "## End-State Vision",
            "",
            "The accepted end-state vision is a coherent control-plane package for future Owner AI readiness. BP2 should plan where protected artifacts are excluded, where consent-shell disabled states appear, how memory and cache consent stay separate, how capability-pack install intent is recorded before execution, how Developer and Owner lane readiness is checked before setup, and how Owner AI memory/agent schemas describe prerequisites without creating real memory or agents.",
            "",
            "## What Will I Actually See, And Where Will I See It?",
            "",
            "- BP2 is the primary decision file for the current packet.",
            "- This BP1 file is supporting accepted-vision context.",
            "- USER should see six accepted vision areas: artifact exclusion controls, consent-shell disabled states, memory/cache consent gates, capability install-intent gates, Developer/Owner lane readiness gates, and Owner AI memory/agent foundation gate schemas.",
            "- Source-truth context remains available for Nexus vision, FAM-007 family vision, AI edition boundaries, AI runtime/trust architecture, phase governance, branch planning rules, validation registry, and branch receipt.",
            "",
            "## How It Will Function",
            "",
            "BP1 has supplied the accepted vision. BP2 now plans concrete implementation surfaces, likely files, validators, helper behavior, fixture coverage, proof requirements, rollback/safety handling, H1 expectations, LV/UTS expectations, and route-back questions. BP3 may later verify orchestration readiness. Workstream may later implement accepted public-safe controls only after BP1 and BP2 are accepted or waived, BP3 is green or waived, and USER separately approves bounded implementation.",
            "",
            "## User Experience Flow",
            "",
            "1. USER reads the BP2 plan as the primary current decision.",
            "2. USER may inspect this BP1 file to confirm what vision BP2 is required to build.",
            "3. USER checks whether the BP2 engineering route preserves the accepted public-safe Owner AI gate direction.",
            "4. USER chooses accept, revise, waive, hold, reject, or route back before BP3.",
            "",
            "## Surface Map",
            "",
            "- BP2 decision surface: USER Review/USER_BRANCH_PLAN_REVIEW.md.",
            "- Accepted BP1 context surface: Review Aids/USER_BRANCH_VISION_REVIEW.md.",
            "- Public-safe control surface: later BP2/BP3 may plan repo-visible controls, validators, fixtures, helper behavior, manifests, schemas, and disabled-state enforcement.",
            "- Artifact boundary surface: protected artifact exclusion keeps Owner/Developer private material, prompts, memory, secrets, model artifacts, private automation, and private screenshots out of public repo and public review outputs.",
            "- Consent-state surface: provider/runtime shell, memory/cache gates, and install-intent gates keep unavailable actions visibly blocked until USER approves setup or execution.",
            "- Future schema surface: Owner AI memory/agent foundation schemas may describe prerequisites and blocked states while real memory, real agents, provider execution, cache activation, and private Owner data stay future-gated.",
            "",
            "## Product Options / Design Paths",
            "",
            "- Accepted path: one grouped Owner AI Operational Foundation Gates vision because the slices share one FAM, one package objective, one route, one worktree, aligned timing, and one validation path.",
            "- BP2 revision path: if engineering planning changes the accepted vision, route back to BP1 rather than treating BP2 as a new vision owner.",
            "- Hold path: USER may hold BP2 for more examples or proof models before BP3.",
            "",
            "## Codex Recommendations",
            "",
            "- Recommendation 1: keep the grouped route if USER still agrees these gates belong together because shared trust-boundary proof lowers drift risk. USER response:",
            "- Recommendation 2: require BP2 to give every slice a concrete implemented-control target, expected changed surfaces, validator/helper proof, and future-gated boundary because proof packets alone are not the feature. USER response:",
            "- Recommendation 3: keep private setup and runtime execution outside this branch until USER grants a later exact action gate because the public branch should prepare controls before private Owner or provider behavior exists. USER response:",
            "- Recommendation 4: preserve cache and memory as separate consent states because cache is operational and clearable while memory is durable personal knowledge requiring separate consent. USER response:",
            "",
            "## Why This Fits The Nexus Vision",
            "",
            "The accepted vision fits Nexus because it grows AI capability through explicit, inspectable, local-first, consent-aware controls. It keeps ORIN and future Owner AI trustworthy by making privacy, provider state, cache, memory, capability installation, and lane identity visible before sensitive runtime or private setup begins.",
            "",
            "## USER Design Questions",
            "",
            "- Does the BP2 plan preserve the accepted grouped Owner AI Operational Foundation Gates vision?",
            "- Does any BP2 line item change the accepted BP1 vision enough to require route-back?",
            "- Are the protected artifact classes, consent states, cache/memory boundary, install-intent gates, lane-readiness checks, and Owner AI schema fields concrete enough for BP3?",
            "",
            "## USER Response",
            "",
            "Accepted by USER for BP2 generation.",
            "",
            "## Codex Digest",
            "",
            "Codex digested the accepted BP1 vision into BP2 planning context. BP2 is now the active USER gate; BP3 and Workstream remain future-gated.",
            "",
            "## USER Response Proof",
            "",
            "Accepted by USER through the BP2 generation approval and current rebaseline/reconciliation approval.",
            "",
            "## USER Response Digested",
            "",
            "Yes - accepted BP1 context is digested for BP2 planning.",
            "",
            "## Accepted Branch Vision",
            "",
            "Accepted by USER - Owner AI Operational Foundation Gates Branch Vision. The accepted vision groups protected artifact exclusion controls, provider/runtime disabled-state consent shell, memory-vs-cache consent-state enforcement gates, capability-pack install-intent gates, Developer/Owner lane readiness gates, and Owner AI memory/agent foundation gate schemas as one public-safe FAM-007 control-plane package.",
            "",
            "## Family-Vision Versus Branch-Only Vision Impact",
            "",
            "Branch-only by default: this accepted vision applies existing Nexus vision, FAM-007 family vision, AI edition trust boundaries, and AI runtime/trust architecture to one selected FAM-007 route. Any USER change that alters reusable lane policy, protected asset policy, provider/cache/memory policy, capability-pack architecture, or durable Owner AI direction must route to the proper durable source-truth owner before BP3 relies on it.",
            "",
            "## Must-Have Behavior",
            "",
            "- BP2 must build the accepted BP1 vision rather than redefining it.",
            "- Each planned slice must name concrete control behavior, affected surfaces, proof lanes, rollback expectations, and future-gated boundaries.",
            "- Private setup, provider/model execution, downloads, runtime cache activation, durable memory, real agents, backup/import execution, PR, merge, release, cleanup, issue mutation, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain pending USER decisions.",
            "- USER-facing files remain decision-focused; live repo state and byte-proof metadata remain in helper output, validator output, Codex digest, Git/GitHub, or external state.",
            "",
            "## Future-Gated Decisions And Regression-Risk Controls",
            "",
            "- Future-gated decision: BP3 Workstream Entry / Orchestration Validation after BP2 acceptance or waiver.",
            "- Future-gated decision: bounded Workstream implementation after BP1/BP2/BP3 gates and separate USER approval.",
            "- Future-gated decision: private Developer setup, Owner setup, private repos, private roots, private remotes, and GitHub Desktop private binding.",
            "- Future-gated decision: backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, issue mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
            "- Regression-risk control: reviewability, packet validation, or helper PASS cannot substitute for USER acceptance.",
            "",
            "## Deferred And Future-Gated Ideas",
            "",
            *_markdown_lines(pending_user_decisions),
            "",
            "## Vision Question Queue",
            "",
            "- None blocking for BP2 generation; route back to BP1 if USER changes the accepted branch vision during BP2 review.",
            "",
            "## Design Assumption Ledger",
            "",
            "- Accepted by USER: the public branch may contain public-safe controls, schemas, manifests, validators, fixtures, helper behavior, and review proof.",
            "- Accepted by USER: private repo URLs, private root paths, secrets, tokens, prompts, model artifacts, memory, private automation, private screenshots, provider execution, runtime cache activation, and real agents stay outside this packet and branch phase.",
            "",
            "## Acceptance / Revision / Rejection / Waiver Decision",
            "",
            "- Accepted BP1 context: USER accepted the Branch Vision for BP2 generation.",
            "- Current BP2 decision: USER may accept, revise, waive, hold, reject, or route back after reviewing the engineering plan.",
            "",
            exact_user_decision,
            "",
        ]
        review_path = target / USER_BRANCH_VISION_REVIEW_FILE
        review_path.write_text("\n".join(lines), encoding="utf-8")
        return review_path.resolve()
    if fam007_owner_ai_foundation_bp1_packet:
        lines = [
            f"# {title} - USER Branch Vision Review",
            "",
            "USER Branch Vision Review: BP1",
            "",
            "## Review Status",
            "",
            "Needs USER Decision - this BP1 packet is ready for USER review, but acceptance, revision, waiver, rejection, or hold has not been recorded.",
            "",
            "## Contract Status",
            "",
            "Draft - update to Complete or Waived only after USER accepts or explicitly waives this Owner AI Operational Foundation Gates Branch Vision.",
            "",
            "## Packet Reviewability State",
            "",
            "Reviewable - BP1 Branch Vision Review packet generated for the active FAM-007 Owner AI Operational Foundation Gates carrier.",
            "",
            "## USER Gate State",
            "",
            "Pending USER Review - BP2 cannot be green until this BP1 vision is accepted or explicitly waived.",
            "",
            "## Contract Revision",
            "",
            "v1 - generated BP1 Branch Vision Review for FAM-007 Owner AI Operational Foundation Gates.",
            "",
            "## Project Vision Context",
            "",
            "Nexus is a Windows-first, local-first, modular, inspectable, privacy-aware, USER-controlled assistant experience. This branch vision supports that project direction by making future Owner AI capability depend on visible gates, deterministic disabled states, and reviewable public-safe controls before any private setup, provider execution, runtime cache, persistent memory, real agents, backup/import execution, PR, merge, release, or cleanup action exists.",
            "",
            "## Family Vision Context",
            "",
            "FAM-007 owns local AI, capability packs, provider readiness, consent posture, provider-visible data boundaries, execution gates, memory and cache boundaries, and Public/Developer/Owner lane separation. This BP1 packet applies that family vision to one public-safe gate package that prepares future Owner AI work without activating private repositories, model/provider behavior, memory, cache, or agent execution.",
            "",
            "## Feature Vision Context",
            "",
            "The selected feature route is Owner AI Operational Foundation Gates. The branch is implementation-bearing because later Workstream can create or enforce concrete public-safe controls: artifact exclusion checks, disabled-state consent shells, memory/cache consent gates, install-intent gates, Developer/Owner lane readiness gates, and Owner AI memory/agent foundation gate schemas. The feature is the control behavior itself, not only a proof packet or planning label.",
            "",
            "## Codex Understanding",
            "",
            "Codex understands this BP1 as the Branch Vision for the active FAM-007 Owner AI Operational Foundation Gates carrier. The branch should make future Owner AI safer by defining the public-safe control plane that blocks leakage, names consent states, separates cache from memory, makes capability installation intentional, distinguishes User/Public, Developer, and Owner lanes, and describes future memory/agent prerequisites as schemas and gates rather than live Owner AI behavior.",
            "",
            "## Branch Goal",
            "",
            "Define the USER-reviewable vision for a grouped Owner AI foundation-gate package. The goal is to let USER decide whether the branch should proceed to BP2 engineering planning for public-safe controls that make future Developer lane and Owner lane AI work safer, while preserving private setup, runtime execution, provider/model behavior, persistent memory, real agents, backup/import execution, PR, merge, release, cleanup, issue mutation, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work as later USER decisions.",
            "",
            "## End-State Vision",
            "",
            "If USER accepts this BP1 vision, the branch should become a coherent control-plane package for future Owner AI readiness. The later engineering plan should be able to name where protected artifacts are excluded, where consent-shell disabled states appear, how memory and cache consent remain separate, how capability-pack install intent is recorded before execution, how Developer and Owner lane readiness is checked before setup, and how Owner AI memory/agent schemas describe prerequisites without creating real memory or agents.",
            "",
            "## What Will I Actually See, And Where Will I See It?",
            "",
            "- A primary BP1 decision file in the local USER hub that explains the Owner AI Operational Foundation Gates vision in plain language.",
            "- A slice-by-slice vision for artifact exclusion controls, consent-shell disabled states, memory/cache consent gates, capability install-intent gates, Developer/Owner lane readiness gates, and Owner AI memory/agent foundation gate schemas.",
            "- Review aids that summarize the branch route, public-safe scope, proof expectations, risks, and future USER gates.",
            "- Source-truth context copies for Nexus vision, FAM-007 family vision, AI edition boundaries, AI runtime/trust architecture, phase governance, branch planning rules, validation registry, and the active branch receipt.",
            "- Future BP2 preview context that shows the engineering plan must derive from accepted or waived BP1 and remain public-safe.",
            "",
            "## How It Will Function",
            "",
            "BP1 sets the branch vision only. If USER accepts or waives it, BP2 may later plan concrete implementation surfaces, likely files, validators, helper behavior, fixture coverage, proof requirements, rollback/safety handling, H1/LV/UTS expectations, and route-back questions. BP3 may later verify orchestration readiness. Workstream may later implement the accepted public-safe controls only after BP1 and BP2 are accepted or waived, BP3 is green or waived, and USER separately approves bounded implementation.",
            "",
            "## User Experience Flow",
            "",
            "1. USER opens the FAM-007 packet and reads the BP1 Branch Vision first.",
            "2. USER checks whether the grouped gate package is the right public-safe direction for future Owner AI readiness.",
            "3. USER reviews each candidate slice for value, public-safe behavior, proof expectation, and future USER gate.",
            "4. USER chooses accept, request revision, waive a specific issue, hold, reject the route, or ask Codex to digest changes.",
            "5. If BP1 is accepted or waived, Codex may request or generate BP2 only after the next legal USER approval.",
            "",
            "## Surface Map",
            "",
            "- Decision surface: USER Review/USER_BRANCH_VISION_REVIEW.md is the primary BP1 file and records the vision decision options.",
            "- Public-safe control surface: later BP2 may plan repo-visible controls, validators, fixtures, helper behavior, manifests, schemas, and disabled-state enforcement that prove future private/runtime actions remain gated.",
            "- Artifact boundary surface: protected artifact exclusion should keep Owner/Developer private material, private paths, prompts, memory, secrets, model artifacts, private automation, and private screenshots out of public repo and public review bundles.",
            "- Consent-state surface: provider/runtime shell, memory/cache gates, and install-intent gates should make unavailable actions visibly blocked until USER approves setup or execution.",
            "- Lane-readiness surface: User/Public, Developer, and Owner lanes should remain distinguishable without creating private repos, roots, remotes, or GitHub Desktop private binding in BP1.",
            "- Future schema surface: Owner AI memory/agent foundation schemas may describe prerequisites and blocked states, while real memory, real agents, provider execution, cache activation, and private Owner data stay future-gated.",
            "",
            "## Product Options / Design Paths",
            "",
            "- Option A - accept one grouped Owner AI Operational Foundation Gates vision. Pros: one coherent FAM-007 package, shared validation path, less drift across related gates; tradeoff: BP2 will be broader and must keep each slice traceable. Risk: low if private/runtime actions stay future-gated.",
            "- Option B - revise toward an artifact-exclusion-first branch. Pros: strongest immediate public/private leak prevention; tradeoff: consent, cache/memory, install-intent, and lane readiness would need later routes. Risk: medium because related gates may diverge.",
            "- Option C - revise toward a consent-shell-first branch. Pros: centers visible disabled states and USER consent posture; tradeoff: protected artifact exclusion and lane readiness may lag. Risk: medium for public/private separation.",
            "- Option D - hold BP1 until more concrete examples are added. Pros: clearer USER visualization before BP2; tradeoff: route progress waits. Risk: low.",
            "- Option E - waive BP1 and move to BP2 with less accepted vision detail. Pros: faster; tradeoff: BP2 may need route-back if the controls or boundaries are not what USER wants. Risk: medium to high for trust-boundary work.",
            "",
            "## Codex Recommendations",
            "",
            "- Recommendation 1: accept the grouped route if USER agrees these gates belong together because they share one trust-boundary model, one FAM, one worktree, one package objective, and one validation path. USER response:",
            "- Recommendation 2: require BP2 to give every slice a concrete implemented-control target, expected changed surfaces, validator/helper proof, and future-gated boundary because proof packets alone are not the feature. USER response:",
            "- Recommendation 3: keep private setup and runtime execution out of this branch vision unless USER later grants an exact action gate, because the public branch should prepare safe controls before any private Owner or provider behavior exists. USER response:",
            "- Recommendation 4: preserve the distinction between cache and memory in BP2 because cache is operational and clearable, while memory is durable personal knowledge requiring separate consent. USER response:",
            "- Recommendation 5: require BP3 to prove whole-package orchestration, not first-slice readiness only, because the six candidate slices are mutually reinforcing controls. USER response:",
            "",
            "## Why This Fits The Nexus Vision",
            "",
            "This branch vision fits Nexus because it grows AI capability through explicit, inspectable, local-first, consent-aware controls. It keeps ORIN and future Owner AI trustworthy by making privacy, provider state, cache, memory, capability installation, and lane identity visible before any sensitive runtime or private setup begins.",
            "",
            "## USER Design Questions",
            "",
            "- Does USER accept the grouped Owner AI Operational Foundation Gates route as one BP1 vision, or should one slice become the narrow branch focus?",
            "- Which artifact classes must BP2 treat as protected before any public review bundle, public artifact, or public repo path can include them?",
            "- What should a disabled provider/runtime consent shell visibly communicate to USER before provider/model execution is approved?",
            "- How should BP2 separate operational cache consent from durable memory consent so the product does not blur cache and memory?",
            "- What capability-pack install-intent proof should exist before any download, setup, or execution path can run?",
            "- What lane-readiness checks should distinguish User/Public, Developer, and Owner lanes before private roots, remotes, or GitHub Desktop binding are approved?",
            "- What schema fields should future Owner AI memory/agent foundations expose while real Owner memory and real agents remain pending?",
            "",
            "## USER Response",
            "",
            "Pending USER response or explicit waiver.",
            "",
            "## Codex Digest",
            "",
            "Pending USER response digest. If USER accepts, revises, waives, rejects, or holds this BP1 vision, Codex should digest the decision into the external branch plan and regenerate or advance the packet only within the next approved scope.",
            "",
            "## USER Response Proof",
            "",
            "Pending USER response. Packet reviewability is not USER acceptance.",
            "",
            "## USER Response Digested",
            "",
            "No - BP1 remains pending until USER accepts, revises, waives, rejects, or holds this Branch Vision.",
            "",
            "## Accepted Branch Vision",
            "",
            "Pending USER acceptance or explicit waiver.",
            "",
            "## Family-Vision Versus Branch-Only Vision Impact",
            "",
            "Branch-only by default: this packet applies existing Nexus vision, FAM-007 family vision, AI edition trust boundaries, and AI runtime/trust architecture to one selected FAM-007 route. If USER changes reusable Public/Developer/Owner lane policy, protected asset policy, provider/cache/memory policy, capability-pack architecture, or durable Owner AI direction, Codex must route the accepted change to the proper durable source-truth owner before BP2 relies on it.",
            "",
            "## Must-Have Behavior",
            "",
            "- BP1 remains a USER gate before BP2.",
            "- BP2 remains pending until USER accepts or explicitly waives BP1.",
            "- The branch vision centers public-safe controls, schemas, manifests, disabled-state enforcement, validators, fixtures, helper behavior, and proof surfaces.",
            "- Private setup, provider/model execution, downloads, runtime cache activation, durable memory, real agents, backup/import execution, PR, merge, release, cleanup, issue mutation, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain pending USER decisions.",
            "- USER-facing files remain decision-focused; live repo state and byte-proof metadata remain in helper output, validator output, Codex digest, Git/GitHub, or external state.",
            "",
            "## Future-Gated Decisions And Regression-Risk Controls",
            "",
            "- Future-gated decision: BP2 USER Branch Plan Review after BP1 acceptance or waiver.",
            "- Future-gated decision: BP3 Workstream Entry / Orchestration Validation after BP2 acceptance or waiver.",
            "- Future-gated decision: bounded Workstream implementation after BP1/BP2/BP3 gates and separate USER approval.",
            "- Future-gated decision: private Developer lane setup, Owner lane setup, private repos, private roots, private remotes, and GitHub Desktop private binding.",
            "- Future-gated decision: backup/import behavior, provider/model/runtime/cache/memory behavior, real Owner memory, real agents, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, issue mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
            "- Regression-risk control: reviewability, packet validation, or helper PASS cannot substitute for USER acceptance.",
            "- Regression-risk control: a proof, readiness matrix, or boundary-control label is insufficient unless BP2 names the exact control behavior that Workstream would create or enforce.",
            "- Regression-risk control: copied historical FAM-007 source-truth files are context only and must not reclassify this active carrier as a prior branch.",
            "",
            "## Deferred And Future-Gated Ideas",
            "",
            *_markdown_lines(pending_user_decisions),
            "",
            "## Vision Question Queue",
            "",
            "- Confirm whether the grouped six-slice gate package is the accepted BP1 vision.",
            "- Name any gate slice that should be removed, split, merged, or emphasized before BP2.",
            "- Name protected asset classes, consent states, cache/memory boundaries, install-intent proof, lane readiness checks, or Owner AI schema fields that BP2 must include.",
            "- Name any future private/runtime/provider/cache/memory decision that must stay explicitly blocked in BP2 and BP3.",
            "",
            "## Design Assumption Ledger",
            "",
            "- Assumption: this branch may create or enforce public-safe controls, schemas, manifests, validators, fixtures, helper behavior, review packets, and disabled-state proof only after later gates approve implementation.",
            "- Assumption: protected Owner/Developer material stays out of public repo paths, public artifacts, public review bundles, and public commits unless later USER-approved sanitization says otherwise.",
            "- Assumption: provider-visible data remains none, sentToProvider remains false, canAcceptPrompts remains false, downloads/network/external calls remain blocked, runtime cache remains inactive, and memory/learning/personalization remain inactive until later approval.",
            "- Assumption: a public-safe gate can be a real implementation route when BP2 names the exact behavior or enforcement that Workstream will create.",
            "",
            "## Acceptance / Revision / Rejection / Waiver Decision",
            "",
            "- Accept: USER accepts this BP1 Branch Vision and authorizes BP2 packet generation only.",
            "- Revise: USER requests changes to route scope, slice grouping, control behavior, proof expectations, or future-gated decisions before BP2.",
            "- Hold / More Options: USER wants additional examples or options before deciding.",
            "- Reject: USER rejects this branch vision or routes FAM-007 to another candidate.",
            "- Waive: USER explicitly waives BP1 and accepts the risk of BP2 planning without a fully accepted Branch Vision.",
            "",
            exact_user_decision,
            "",
        ]
        review_path = target / USER_BRANCH_VISION_REVIEW_FILE
        review_path.write_text("\n".join(lines), encoding="utf-8")
        return review_path.resolve()
    if fam007_private_boundary_bp1_packet:
        lines = [
            f"# {title} - USER Branch Vision Review",
            "",
            "USER Branch Vision Review: BP1",
            "",
            "## Review Status",
            "",
            "Needs USER Decision - this BP1 packet is ready for USER review, but acceptance, revision, waiver, rejection, or hold has not been recorded.",
            "",
            "## Contract Status",
            "",
            "Draft - update to Complete or Waived only after USER accepts or explicitly waives this private-boundary Branch Vision.",
            "",
            "## Packet Reviewability State",
            "",
            "Reviewable - BP1 Branch Vision Review packet generated for the active FAM-007 private-boundary setup carrier.",
            "",
            "## USER Gate State",
            "",
            "Pending USER Review - BP2 cannot be green until this BP1 vision is accepted or explicitly waived.",
            "",
            "## Contract Revision",
            "",
            "v1 - generated BP1 Branch Vision Review for FAM-007 Dev/Owner private-boundary setup.",
            "",
            "## Project Vision Context",
            "",
            "Nexus is Windows-first, local-first, modular, inspectable, privacy-aware, and USER-controlled. This branch vision keeps private Dev and Owner setup decisions visible before any private roots, remotes, provider behavior, model downloads, runtime cache behavior, memory, backup/import execution, or private automation exists.",
            "",
            "## Family Vision Context",
            "",
            "FAM-007 owns local AI, capability packs, Public/Dev/Owner separation, public/private trust boundaries, provider readiness, consent posture, provider-visible data, execution gates, and memory or learning boundaries. This BP1 review applies those family rules to a public-safe private-boundary setup direction.",
            "",
            "## Feature Vision Context",
            "",
            "The feature vision is not private setup. It is a decision-ready public planning layer for the Dev and Owner boundary: what can be reviewed in Main, what must remain future-gated, what later BP2 must plan, and what proof must exist before any private setup or runtime/provider behavior can be considered.",
            "",
            "## Codex Understanding",
            "",
            "Codex understands this BP1 as the Branch Vision for the active FAM-007 Dev/Owner private-boundary setup carrier. The branch should define a safe future direction for Dev private-boundary setup, Owner private-boundary setup, public-upstream safety, private-origin expectations, GitHub Desktop private binding decisions, backup/import consent, provider/runtime/cache/memory deferral, and proof expectations without executing any private or runtime action.",
            "",
            "## Branch Goal",
            "",
            "Define the public-safe branch vision for Dev/Owner private-boundary setup so USER can decide whether BP2 should plan the engineering route. The branch should make private setup choices understandable before creating private repositories, local-only private roots, private remotes, GitHub Desktop private bindings, backup/import paths, provider/model execution, cache behavior, memory, learning, personalization, PR, merge, release, or cleanup work.",
            "",
            "## End-State Vision",
            "",
            "If USER accepts this BP1 vision, the next BP2 packet should be able to plan clear decision matrices for Public, Dev, and Owner lanes; private root and remote choices; public-upstream and private-origin safety; GitHub Desktop binding posture; backup/import consent timing; provider-visible data and model execution deferral; runtime cache and memory deferral; lane identity labels; validation proof; and the exact USER gates that must stay closed until later approval.",
            "",
            "## What Will I Actually See, And Where Will I See It?",
            "",
            "- A BP1 decision file in the local USER hub that explains the active private-boundary setup vision in plain language.",
            "- A Dev boundary direction describing future private Dev repo/root/remote choices, contributor-only expectations, public-upstream safety, and GitHub Desktop private binding as later decisions.",
            "- An Owner boundary direction describing local-private control, local version-history expectations, no default public exposure path, and any future Owner remote as a later decision.",
            "- A public-safe proof direction that keeps provider-visible data at none, sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads blocked, runtime cache inactive, and memory/learning/personalization inactive.",
            "- Review aids and source-truth context that support the BP1 review without becoming USER acceptance or implementation authority.",
            "",
            "## How It Will Function",
            "",
            "BP1 sets the product and trust-boundary direction only. If USER accepts or waives it, BP2 may later convert this vision into an engineering plan with seams, likely files, validators, proof requirements, rollback expectations, and route-back questions. BP3 may later validate orchestration. Workstream implementation and private/runtime work remain separate future gates.",
            "",
            "## User Experience Flow",
            "",
            "1. USER opens the local FAM-007 review packet and reads this BP1 Branch Vision first.",
            "2. USER decides whether the public-safe private-boundary setup direction is right, too broad, too narrow, or missing options.",
            "3. USER accepts, revises, waives, rejects, or holds BP1.",
            "4. If BP1 is accepted or waived, Codex may generate BP2 only after separate USER approval.",
            "5. BP2, BP3, Workstream, private setup, provider/runtime behavior, PR, merge, release, and cleanup remain blocked until their own gates are reached and approved.",
            "",
            "## Surface Map",
            "",
            "- Review surface: USER Review/USER_BRANCH_VISION_REVIEW.md is the single primary BP1 decision file.",
            "- Decision surface: USER chooses the Dev/Owner private-boundary direction, revision needs, waiver, rejection, or hold.",
            "- Context surface: Source Truth Context contains project vision, FAM-007 family vision, AI runtime/trust architecture, phase governance, review-bundle rules, historical FAM-007 receipts, and validators for inspection.",
            "- Future BP2 surface: later engineering plan may define matrices, seams, likely files, validators, proof requirements, and rollback plans only after BP1 acceptance or waiver.",
            "- Future proof surface: later validators and packets should prove private/runtime/provider/cache/memory actions remain gated and public-safe.",
            "",
            "## Product Options / Design Paths",
            "",
            "- Option A - accept one integrated Dev/Owner private-boundary setup vision. This keeps Dev and Owner decisions together because they share public/private trust-boundary proof; tradeoff is a broader BP2, but the risk of inconsistent gates is lower.",
            "- Option B - revise toward Dev-first planning. This prioritizes future private Dev repo/root/remote and GitHub Desktop posture; tradeoff is that Owner local-private safety may need a later route-back.",
            "- Option C - revise toward Owner-first planning. This prioritizes Owner local-private control, local version history, and no default remote; tradeoff is slower Dev private-boundary readiness.",
            "- Option D - hold BP1 for more examples before BP2. This lowers planning ambiguity; tradeoff is slower branch progress.",
            "- Option E - waive BP1 and allow BP2 planning to proceed with less accepted vision detail. This is faster but riskier because BP2 may need route-back if private-boundary assumptions are wrong.",
            "",
            "## Codex Recommendations",
            "",
            "- Recommendation 1: accept Option A if USER agrees the Dev and Owner boundaries should be planned together. Placement should stay in this public FAM-007 carrier; behavior stays review and planning only; tradeoff is a larger BP2, but shared proof prevents split-lane drift. USER response:",
            "- Recommendation 2: require BP2 to make the Public, Dev, and Owner lane matrix explicit. This gives USER concrete future choices about roots, remotes, public-upstream, private-origin, GitHub Desktop binding, backup/import consent, provider/runtime deferral, cache deferral, memory deferral, and lane identity. USER response:",
            "- Recommendation 3: keep all private/runtime actions future-gated. This protects the public repo from private paths, tokens, private URLs, prompts, model artifacts, memory, backup/import data, or private automation; tradeoff is slower setup but stronger trust. USER response:",
            "- Recommendation 4: require direct validator or fixture proof in BP2/BP3 before Workstream can be requested. This reduces false-green packet risk because reviewability, helper output, and USER acceptance stay separate. USER response:",
            "",
            "## Why This Fits The Nexus Vision",
            "",
            "This vision fits Nexus because it keeps AI capability growth controlled, local-first, inspectable, and privacy-aware. It gives USER a clear private-boundary decision before engineering planning or implementation creates paths that could leak private state or blur Main, Dev, and Owner responsibilities.",
            "",
            "## USER Design Questions",
            "",
            "- Should Dev and Owner private-boundary setup be planned together in one BP2 packet, or should BP1 revise toward Dev-first or Owner-first planning?",
            "- What future Dev private repo, local root, private remote, public-upstream, and GitHub Desktop expectations should BP2 make visible without executing them?",
            "- Should Owner default to local-only private control, local Git/version history, and no remote unless USER later approves a safer private remote model?",
            "- What backup/import consent and rollback posture should BP2 plan for Public, Dev, and Owner lanes?",
            "- What proof should show provider-visible data remains none and provider/model/cache/memory behavior remains inactive?",
            "- What lane identity labels or review artifact labels would help USER distinguish Public, Dev, and Owner proof later?",
            "",
            "## USER Response",
            "",
            "Pending USER response or explicit waiver.",
            "",
            "## Codex Digest",
            "",
            "Pending USER response digest. If USER accepts or waives this BP1 vision, Codex should digest the decision into the external branch plan and then generate BP2 only within the approved scope.",
            "",
            "## USER Response Proof",
            "",
            "Pending USER response. Packet reviewability is not USER acceptance.",
            "",
            "## USER Response Digested",
            "",
            "No - BP1 remains pending until USER accepts, revises, waives, rejects, or holds this Branch Vision.",
            "",
            "## Accepted Branch Vision",
            "",
            "Pending USER acceptance or explicit waiver.",
            "",
            "## Family-Vision Versus Branch-Only Vision Impact",
            "",
            "Branch-only by default: this carrier applies existing FAM-007 and AI runtime/trust architecture to private-boundary setup planning. If USER changes Public/Dev/Owner policy, provider/cache/memory policy, private/public promotion rules, lane identity standards, or durable family-level AI edition direction, Codex must route that change to the proper durable source-truth owner before BP2 relies on it.",
            "",
            "## Must-Have Behavior",
            "",
            "- BP1 remains a USER gate before BP2.",
            "- BP2 must not claim green unless this BP1 vision is accepted or explicitly waived.",
            "- Private setup, provider/model execution, downloads, runtime cache, memory, backup/import execution, GitHub Desktop private binding, PR, merge, release, cleanup, and sibling-worktree mutation remain future-gated.",
            "- USER-facing files remain decision-focused; live repo state and byte-proof metadata remain in helper output, validator output, Codex digest, Git/GitHub, or external state.",
            "",
            "## Future-Gated Decisions And Regression-Risk Controls",
            "",
            "- Future-gated decision: BP2 USER Branch Plan Review after BP1 acceptance or waiver.",
            "- Future-gated decision: BP3 Workstream Entry / Orchestration Validation after BP2 acceptance or waiver.",
            "- Future-gated decision: bounded Workstream implementation after BP1/BP2/BP3 gates and separate USER approval.",
            "- Future-gated decision: private Dev skeleton setup, Owner skeleton setup, private repos, private roots, private remotes, and GitHub Desktop private binding.",
            "- Future-gated decision: backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, issue mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
            "- Regression-risk control: reviewability, packet validation, or helper PASS cannot substitute for USER acceptance.",
            "- Regression-risk control: copied historical FAM-007 source-truth files are context only and must not reclassify this active carrier as a prior branch.",
            "",
            "## Deferred And Future-Gated Ideas",
            "",
            *_markdown_lines(pending_user_decisions),
            "",
            "## Vision Question Queue",
            "",
            "- Confirm whether the active private-boundary setup carrier should use integrated Dev/Owner planning.",
            "- Name any Dev or Owner boundary options that should be added before BP2.",
            "- Name any private setup, backup/import, provider/runtime, cache, memory, identity, or proof expectations that BP2 must treat as blocked or explicitly future-gated.",
            "",
            "## Design Assumption Ledger",
            "",
            "- Assumption: the public branch may contain public-safe planning, context, validators, fixtures, and review proof, but no private repo URLs, private root paths, secrets, tokens, prompts, model artifacts, memory, private automation, or private artifacts.",
            "- Assumption: Dev and Owner setup choices should be visible to USER before engineering planning begins.",
            "- Assumption: provider-visible data remains none, sentToProvider remains false, canAcceptPrompts remains false, downloads/network/external calls remain blocked, runtime cache remains inactive, and memory/learning/personalization remain inactive until later approval.",
            "",
            "## Acceptance / Revision / Rejection / Waiver Decision",
            "",
            "- Accept: USER accepts this BP1 Branch Vision and authorizes BP2 packet generation only.",
            "- Revise: USER requests changes to the private-boundary vision, options, proof expectations, or future-gated decisions before BP2.",
            "- Hold / More Options: USER wants additional examples or options before deciding.",
            "- Reject: USER rejects this branch vision or routes FAM-007 to another candidate.",
            "- Waive: USER explicitly waives BP1 and accepts the risk of BP2 planning without a fully accepted Branch Vision.",
            "",
            exact_user_decision,
            "",
        ]
        review_path = target / USER_BRANCH_VISION_REVIEW_FILE
        review_path.write_text("\n".join(lines), encoding="utf-8")
        return review_path.resolve()
    if fam007_dev_owner_bp1_packet:
        lines = [
            f"# {title} - USER Branch Vision Review",
            "",
            "USER Branch Vision Review: BP1",
            "",
            "## Review Status",
            "",
            review_status,
            "",
            "## Contract Status",
            "",
            contract_status,
            "",
            "## Packet Reviewability State",
            "",
            packet_reviewability_state,
            "",
            "## USER Gate State",
            "",
            user_gate_state,
            "",
            "## Contract Revision",
            "",
            (
                f"v8 - Accepted BP1 Branch Vision context for {active_planning_gate}: integrated Dev/Owner readiness, "
                "Dev private repo future direction, Owner local-private baseline, GitHub Desktop safety, "
                "backup/import lane posture, provider/runtime/cache/memory deferral, and identity labeling."
                if bp2_or_later_context_packet
                else "v6 - USER/ChatGPT BP1 review direction digested: integrated Dev/Owner readiness, Dev private repo future direction, Owner local-private baseline, GitHub Desktop safety, backup/import lane posture, and identity labeling."
            ),
            "",
            "## Project Vision Context",
            "",
            "Nexus is meant to stay Windows-first, local-first, modular, inspectable, privacy-aware, and USER-controlled even as AI capability grows. This Branch Vision keeps the public repo as the place where future Dev and Owner skeleton setup is made understandable before any private roots, remotes, provider behavior, cache behavior, memory, or automation exists.",
            "",
            "## Family Vision Context",
            "",
            "FAM-007 owns local AI, capability packs, Public/Dev/Owner separation, public/private trust boundaries, provider readiness, consent posture, provider-visible data, execution gates, and memory or future learning boundaries. The branch should turn those family rules into a concrete Dev/Owner readiness direction while keeping the base public product useful and safe without local LLM or provider execution.",
            "",
            "## Feature Vision Context",
            "",
            "This successor carrier follows the merged Breakpoint 2 action-gate proof and the Governance USER Review Gate repair. USER selected the integrated Option A direction: Dev and Owner skeleton readiness should be planned together as one public-safe trust-boundary package. The feature vision is not private setup; it is the public-safe readiness layer that lets USER decide how Dev private repo readiness, Owner local-private control, GitHub Desktop posture, backup/import timing, provider/model deferral, runtime cache deferral, memory deferral, and lane identity should be represented before later gates authorize any implementation.",
            "",
            "## Codex Understanding",
            "",
            "Codex understands this BP1 as a product and trust-boundary vision review for the FAM-007 Dev/Owner Skeleton Readiness carrier. The branch should prepare a decision-ready public package for future Dev and Owner skeleton setup, preserve every private/runtime action gate, and give BP2 a concrete accepted vision to translate into an engineering plan. The updated direction keeps Dev and Owner together for planning, treats future Dev as likely private-repo backed after approval, treats Owner as local-private and controlled by default, and requires BP2 to make GitHub Desktop, public-upstream, backup/import, proof, and identity propagation explicit.",
            "",
            "## Branch Goal",
            "",
            "Define a public-safe Dev/Owner skeleton readiness and decision layer around one integrated trust-boundary package. The branch should make future Dev and Owner setup choices understandable before private repositories, local-only roots, private remotes, backup/import behavior, provider or model execution, runtime cache behavior, memory, learning, personalization, or release work exists. BP2 should plan the route toward a future private Dev repo, Owner local Git/version-history safety, optional later Owner remote evaluation, public-upstream safety, and lane identity labels without creating any of those private/runtime surfaces.",
            "",
            "## End-State Vision",
            "",
            "When this branch is complete, USER should have durable source truth, decision matrices, future-gate definitions, proof expectations, validation gates, and review artifacts that name the Dev readiness path, Owner readiness path, public-to-private boundary, private root and remote decision points, GitHub Desktop safety posture, backup/import timing choices, provider/model/cache/memory deferral, lane watermark/identity labels, artifact identity propagation, and later USER action gates. It should be obvious what BP2 is allowed to plan next, what belongs only in a future private Dev repo, what stays Owner-local by default, and what still needs separate approval.",
            "",
            "## What Will I Actually See, And Where Will I See It?",
            "",
            "- An integrated Dev/Owner readiness matrix that treats Dev and Owner as one public-safe trust-boundary package for BP2 planning.",
            "- A Dev readiness matrix that names future private Dev repo direction, local-root staging choices, public-upstream relationship, private-origin expectation, contributor-only boundaries, and future GitHub Desktop private binding after approval.",
            "- A Dev asset inventory posture that asks BP2 to plan how dev-related launchers, assets, and tools are inventoried, classified, transferred, recreated, or removed from the normal User/Public lane over time.",
            "- An Owner readiness matrix that keeps Owner private and controlled, defaults to local Git/version history and no remote, and evaluates a private Owner remote only as a future option if BP2 proves it safer and USER later approves it.",
            "- A private root and remote decision matrix for User/Public, Dev, and Owner lanes covering local-only roots, private hosting, GitHub Desktop binding, private `origin`, fetch-only `public-upstream`, remote identity proof, and public push prevention.",
            "- A backup/import timing choice set for User/Public settings/preferences/config backup, Dev private development recovery tied to the future private Dev repo, and Owner local/private/encrypted recovery with rollback as the safest baseline.",
            "- A provider/runtime/cache/memory deferral proof surface showing provider-visible data remains none, prompt acceptance remains disabled, downloads stay blocked, runtime cache stays inactive, and memory or personalization stays inactive.",
            "- A watermark and identity posture: User/Public should present as `Nexus Desktop AI` or `Nexus Desktop AI · Pre-Beta`, Dev as `Nexus Desktop AI · DEV PRIVATE`, and Owner as `Nexus Owner · Local Private` unless a later approved Owner remote model changes that wording.",
            "- Identity propagation requirements for UI, launchers, diagnostics, logs, review packets, screenshots/proof, backup/export packages, and generated manifests so Dev and Owner proof artifacts are visibly marked where appropriate.",
            "- These surfaces are review and proof targets only; this BP1 vision creates no private repos, roots, remotes, provider calls, cache behavior, memory, runtime UI, GitHub Desktop binding, backup/import execution, or launcher migration.",
            "",
            "## How It Will Function",
            "",
            "The readiness layer should prevent premature private/runtime work while preparing a clear future setup path. It should define action gates, public-safe proof surfaces, decision matrices, and validator expectations that show each private, provider-facing, backup/import, GitHub Desktop, identity-propagation, or launcher/assets action is still pending, with no activation path until later USER approval.",
            "",
            "## User Experience Flow",
            "",
            "1. USER reviews Dev readiness and Owner readiness together as one public-safe trust-boundary package.",
            "2. USER confirms whether BP2 should plan the integrated Option A matrix with Dev private repo direction, Owner local-private baseline, GitHub Desktop posture, backup/import lane posture, and identity/watermark propagation.",
            "3. USER names the private root, private remote, public-upstream, GitHub Desktop, backup/import, provider/cache/memory, launcher/assets, and artifact identity proof expectations that BP2 must make concrete.",
            (
                f"4. USER has accepted this BP1 Branch Vision as the basis for the active {active_planning_gate} review."
                if bp2_or_later_context_packet
                else "4. USER accepts, revises, holds for more options, rejects, or explicitly waives this BP1 Branch Vision."
            ),
            (
                "5. BP2 and BP3 are accepted, Workstream proof is complete, Hardening H1 is green, and Live Validation LV1 is the active no-visible-runtime proof decision."
                if live_validation_context_packet
                else
                "5. BP2 and BP3 are accepted, Workstream proof is complete, and Hardening H1 is the active proof-comparison decision."
                if hardening_h1_context_packet
                else
                "5. BP2 is accepted; BP3 now validates orchestration before any Workstream implementation can be requested."
                if bp3_context_packet
                else "5. BP2 now turns the accepted vision into an engineering plan, and BP3 later validates orchestration before any Workstream implementation can be requested."
                if bp2_context_packet
                else "5. BP2 later turns only the accepted or waived vision into an engineering plan, and BP3 later validates orchestration before any Workstream implementation can be requested."
            ),
            "",
            "## Surface Map",
            "",
            "- Edition/Lane Matrix: User/Public remains normal `Nexus Desktop AI` or `Nexus Desktop AI · Pre-Beta`; Dev is visibly private; Owner is visibly local-private unless later changed by approved remote policy.",
            "- Dev/Owner Readiness Matrix: Dev and Owner stay together as the accepted planning direction, while their actual private setup remains separately gated.",
            "- Dev readiness surface: a future BP2 matrix should state future private Dev repo direction, local-root staging choices, public-upstream relationship, private-origin expectation, contributor-only boundaries, and dev launcher/assets/tool inventory or migration posture.",
            "- Owner readiness surface: a future BP2 matrix should state Owner local Git/version-history baseline, no default public exposure path, no default remote path, no default GitHub Desktop private remote binding, and the future conditions under which a private Owner remote could be evaluated.",
            "- Private Root / Remote Matrix: public root, future Dev private repo/root, future Owner local/private root, private `origin`, fetch-only `public-upstream`, remote identity proof, and push-prevention need explicit later decisions.",
            "- GitHub Desktop Binding Matrix: User/Public binding stays normal public repo posture; future Dev may use GitHub Desktop with a private Dev repo after approval; Owner defaults to local Git/no remote unless BP2 proves a safer private remote model and USER later approves it.",
            "- Backup / Import Matrix: User/Public should stay product-safe settings/preferences/config backup only; Dev should plan private development recovery that can integrate with the future private Dev repo; Owner should plan local/private/encrypted recovery and rollback as the safest baseline.",
            "- Provider / Runtime / Cache / Memory Deferral Matrix: provider-visible data none, sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, runtime cache inactive, and memory/learning/personalization inactive.",
            "- Watermark / Identity Matrix: UI, launchers, diagnostics, logs, review packets, screenshots/proof, backup/export packages, and generated manifests should carry the right lane identity when BP2 later plans proof.",
            "- Proof and Validation Matrix: later validators and packet checks should prove no private repo, private root, private remote, GitHub Desktop private binding, backup/import execution, provider/model execution, runtime cache behavior, memory behavior, token, secret, prompt, model artifact, private automation, or private artifact enters the public branch.",
            "- Future USER Gate Matrix: BP2, BP3, Workstream implementation, private Dev/Owner setup, backup/import execution, provider/runtime/cache/memory behavior, PR, merge, release, cleanup, AI Product Contract import, Private Dev ORIN import, and v1.8.0 remain separate future decisions.",
            "",
            "## Product Options / Design Paths",
            "",
            "- Option A - selected direction: integrated Dev and Owner readiness matrix. This keeps Dev private repo direction, Owner local-private control, public-upstream safety, GitHub Desktop posture, backup/import posture, provider/model deferral, cache deferral, memory deferral, and identity propagation in one public-safe trust-boundary package. Tradeoff: BP2 is broader, but the gates stay consistent.",
            "- Option B - Dev-private-repo-first planning inside the same package. This emphasizes future private Dev repo, Dev GitHub Desktop posture, and dev launcher/assets migration first. Tradeoff: Owner version-control and no-public-exposure rules could lag unless BP2 keeps the shared matrix.",
            "- Option C - Owner-local-private-first planning inside the same package. This emphasizes local Git/version history, local/private/encrypted recovery, no default remote, no public exposure, and Owner identity first. Tradeoff: Dev private repo and launcher/assets migration could lag.",
            "- Option D - root/remote/GitHub Desktop safety package first. This focuses on public-upstream, private `origin`, remote identity proof, push prevention, and binding proof across User/Public, Dev, and Owner lanes. Tradeoff: backup/import and identity propagation still need matrix detail.",
            "- Option E - backup/import and identity package first. This prioritizes User/Public settings backup, Dev private development recovery, Owner encrypted rollback, lane labels, and artifact identity propagation. Tradeoff: private repo topology and provider/runtime deferral still need expansion.",
            "- Option F - provider/runtime deferral-first package. This proves provider-visible data none, sentToProvider=false, canAcceptPrompts=false, downloads/network blocked, cache inactive, and memory inactive before private setup. Tradeoff: it may under-answer private repo/root topology until BP2 expands it.",
            "",
            "## Codex Recommendations",
            "",
            "- Recommendation 1: keep the USER-selected Option A direction and make BP2 plan Dev plus Owner readiness in one integrated matrix. Placement should stay in the public FAM-007 carrier because the shared trust boundary is the product problem; behavior should stay planning/proof only; tradeoff is a wider BP2, but the risk of inconsistent private gates is lower.",
            "  USER response:",
            "- Recommendation 2: record future Dev as private-repo-oriented after approval and ask BP2 to inventory dev-related launchers, assets, and tools that should not remain in the normal User/Public version long-term. BP2 should plan classification, transfer, recreation, or removal paths without moving files or creating private repos in BP1.",
            "  USER response:",
            "- Recommendation 3: set Owner's default safety model to local Git/version history, local/private/encrypted recovery, no public exposure path, no default remote path, and no default GitHub Desktop private remote binding. A private Owner remote should stay a future option only if BP2 proves it is safer and USER later approves it.",
            "  USER response:",
            "- Recommendation 4: require BP2 to produce Edition/Lane, Dev/Owner Readiness, Private Root/Remote, GitHub Desktop Binding, Backup/Import, Provider/Runtime/Cache/Memory Deferral, Watermark/Identity, Proof and Validation, and Future USER Gate matrices before BP3 can ask for implementation.",
            "  USER response:",
            "- Recommendation 5: keep backup/import execution, provider SDKs, model downloads, provider/model execution, runtime cache behavior, memory, learning, personalization, voice/Core sync, shortcut/installer work, PR, merge, release, and cleanup deferred until named future gates. This protects Main and keeps provider-visible data at none; tradeoff is slower private setup.",
            "  USER response:",
            "- Recommendation 6: require public-safe proof and fixture/validator checks before any later private setup is considered. The proof should cover no private paths, remotes, tokens, secrets, prompts, memory, model artifacts, provider calls, downloads, cache activation, backup/import execution, GitHub Desktop private binding, private automation, or private artifacts in public review output.",
            "  USER response:",
            "",
            "## Why This Fits The Nexus Vision",
            "",
            "The branch fits Nexus because it makes powerful AI-edition work deliberate instead of ambient. It keeps the public app local-first and inspection-friendly, preserves the FAM-007 family rule that provider/model/cache/memory behavior needs explicit gates, and gives USER a clear way to choose future Dev/Owner boundaries before any sensitive setup exists.",
            "",
            "## USER Design Questions",
            "",
            "- Does USER confirm Option A as the BP1 vision direction: Dev and Owner skeleton readiness planned together as one integrated public-safe trust-boundary package?",
            "- For the Dev side, should BP2 treat a future private Dev repo as the preferred long-term path while repo creation and GitHub Desktop private binding remain future-gated?",
            "- Which existing or future dev launchers, assets, tools, diagnostics, logs, manifests, or proof artifacts should BP2 inventory as candidates for transfer, recreation, or removal from the normal User/Public lane?",
            "- For the Owner side, does USER accept local Git/version history, no default remote, no public exposure path, and no default GitHub Desktop private remote binding as the baseline?",
            "- What criteria would make a future private Owner remote safer than local-only Owner version history?",
            "- What exact public-upstream, private-origin, remote naming, remote identity proof, fetch/reconcile posture, and push-prevention expectations should BP2 make visible for GitHub Desktop?",
            "- Should backup/import readiness be planned before private roots exist, after private roots exist, or only after Dev/Owner skeleton setup is separately approved?",
            "- What is enough proof for User/Public settings backup, Dev private development recovery, and Owner local/private/encrypted rollback?",
            "- What evidence should prove provider/model execution, downloads, runtime cache behavior, and memory/personalization remain inactive?",
            "- Are the proposed identity labels acceptable: `Nexus Desktop AI` or `Nexus Desktop AI · Pre-Beta` for User/Public, `Nexus Desktop AI · DEV PRIVATE` for Dev, and `Nexus Owner · Local Private` for Owner?",
            "- What proof bar should be required before any later private setup: matrix only, validator fixtures, no-leak scan, provider-state proof, packet walkthrough, visual walkthrough, artifact identity proof, or a combination?",
            "",
            "## USER Response",
            "",
            (
                "USER accepted the updated Option A BP1 Branch Vision: Dev and Owner skeleton readiness stay planned together as one public-safe trust-boundary package; future Dev is private-repo-oriented after approval; dev-related launchers/assets/tools should leave the normal User/Public lane long-term; Owner remains private and controlled with local Git/version history as the baseline; GitHub Desktop safety, public-upstream posture, backup/import lane posture, proof expectations, and lane identity labels must be planned by BP2."
                if bp2_or_later_context_packet
                else "Revision direction received from USER/ChatGPT review: Option A is the selected BP1 direction; Dev should eventually have a private repo; dev-related launchers/assets/tools should leave the normal User/Public lane long-term; Owner should remain private and controlled with local Git/version history as the baseline; GitHub Desktop safety, public-upstream posture, backup/import lane posture, proof expectations, and lane identity labels must be planned by BP2. Final BP1 acceptance remains pending."
            ),
            "",
            "## Codex Digest",
            "",
            (
                f"Codex records this file as accepted BP1 context for the active {active_planning_gate} packet. The accepted vision is one integrated Dev/Owner readiness package with future private Dev repo planning, Dev asset inventory/migration planning, Owner local-private version-control safety, explicit GitHub Desktop binding rules, public-upstream push-prevention proof, backup/import posture for User/Public, Dev, and Owner lanes, provider/runtime/cache/memory deferral proof, and visible lane identity labels."
                if bp2_or_later_context_packet
                else "Codex digested the USER/ChatGPT BP1 review direction into this v6 Branch Vision. The updated vision recommends one integrated Dev/Owner readiness package, future private Dev repo planning, Dev asset inventory/migration planning, Owner local-private version-control safety, explicit GitHub Desktop binding rules, public-upstream push-prevention proof, backup/import posture for User/Public, Dev, and Owner lanes, provider/runtime/cache/memory deferral proof, and visible lane identity labels. This digest is a revision update, not final BP1 acceptance."
            ),
            "",
            "## USER Response Proof",
            "",
            (
                f"Accepted by USER - BP1 Branch Vision acceptance is recorded in external branch planning state and used by this {active_planning_gate} packet as supporting context."
                if bp2_or_later_context_packet
                else "USER/ChatGPT BP1 review direction is recorded in this v6 packet. Final BP1 acceptance, revision, waiver, rejection, or hold remains pending USER decision."
            ),
            "",
            "## USER Response Digested",
            "",
            (
                f"Digested - accepted BP1 direction is preserved as required {active_planning_gate} traceability context."
                if bp2_or_later_context_packet
                else "Partially - USER/ChatGPT revision direction has been digested into v6, but BP1 remains open until USER explicitly accepts, revises, waives, rejects, or holds the updated Branch Vision."
            ),
            "",
            "## Accepted Branch Vision",
            "",
            accepted_vision,
            "",
            "## Family-Vision Versus Branch-Only Vision Impact",
            "",
            "Branch-only by default: this carrier applies existing FAM-007 and AI runtime/trust architecture to Dev/Owner skeleton readiness. The v6 direction may affect future edition identity, Dev asset placement, Owner version-control posture, GitHub Desktop safety, backup/import posture, and proof expectations. If USER changes edition boundaries, provider/cache/memory policy, public/private promotion rules, or the durable Public/Dev/Owner naming model, Codex must route that change to the proper durable family or architecture owner before BP2 relies on it.",
            "",
            "## Must-Have Behavior",
            "",
            (
                f"- BP1 acceptance is recorded; {active_planning_gate} must keep tracing to this accepted Dev/Owner skeleton readiness vision and integrated Option A direction."
                if bp2_or_later_context_packet
                else "- BP1 acceptance or explicit waiver is required before BP2 can claim the engineering plan is valid."
            ),
            "- BP2 must trace every seam or SLC to this accepted Dev/Owner skeleton readiness vision and its integrated Option A direction.",
            "- BP2 must include Edition/Lane, Dev/Owner Readiness, Private Root/Remote, GitHub Desktop Binding, Backup/Import, Provider/Runtime/Cache/Memory Deferral, Watermark/Identity, Proof and Validation, and Future USER Gate matrices.",
            "- The branch must preserve public-safe proof and avoid creating or activating private/runtime/provider/cache/memory behavior, private GitHub Desktop binding, backup/import execution, or dev asset migration.",
            "- USER-facing review files must stay decision-focused while technical proof remains in helper output, validator output, Codex digest, or external operational state.",
            "",
            "## Future-Gated Decisions And Regression-Risk Controls",
            "",
            "- Future-gated decision: private Dev skeleton setup, private Owner skeleton setup, private Dev repo creation, private Owner repo or remote creation, local-only private roots, private remotes, and GitHub Desktop private binding.",
            "- Future-gated decision: dev launcher/assets/tool inventory execution, transfer, recreation, removal from the User/Public lane, or import into a private Dev path.",
            "- Future-gated decision: backup/import behavior, public-to-private import, User/Public backup implementation, Dev recovery implementation, Owner encrypted recovery or rollback implementation, provider SDKs, model downloads, provider/model execution, runtime provider execution, cache behavior, memory, learning, indexing, retrieval, and personalization.",
            "- Future-gated decision: voice/Core sync, shortcut or installer work, PR creation, merge, release, cleanup, issue mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
            "- Regression-risk control: reviewability is not USER acceptance, and packet validation cannot approve BP2, BP3, or Workstream implementation.",
            "- Regression-risk control: any future private, GitHub Desktop, backup/import, identity, or provider-facing proof must be public-safe, synthetic where needed, and free of private paths, secrets, tokens, prompts, memory, model artifacts, private automation, private repository URLs, and private artifacts.",
            "",
            "## Deferred And Future-Gated Ideas",
            "",
            *_markdown_lines(pending_user_decisions),
            "",
            "## Vision Question Queue",
            "",
            (
                "- Use integrated Dev/Owner readiness as the accepted BP1 direction while reviewing whether the BP2 engineering plan faithfully builds it."
                if bp2_context_packet
                else "- Confirm integrated Dev/Owner readiness as the accepted BP1 direction or revise it before BP2."
            ),
            "- Decide the future Dev private repo posture and the dev launcher/assets/tool inventory or migration questions BP2 must answer.",
            "- Decide whether Owner stays local Git/no remote by default and what criteria would justify evaluating a private Owner remote later.",
            "- Decide which public-upstream, private origin, GitHub Desktop binding, backup/import, provider/cache/memory, identity/watermark, artifact-propagation, and public-to-private promotion questions BP2 must answer.",
            "- Decide what proof format USER wants before any future private setup, backup/import execution, GitHub Desktop private binding, provider/runtime behavior, cache behavior, or memory behavior can be considered.",
            "",
            "## Design Assumption Ledger",
            "",
            "- Assumption: the public branch may define readiness, decisions, fixtures, validators, and review proof, but it may not contain private Dev or Owner assets, private repo URLs, private root paths, real private screenshots, private prompts, or private automation.",
            "- Assumption: User/Public remains normal Nexus branding, while Dev and Owner artifacts should be visibly marked where appropriate once BP2 plans identity propagation.",
            "- Assumption: provider-visible data remains none, sentToProvider remains false, canAcceptPrompts remains false, downloads/network/external calls remain blocked, memory and cache runtime behavior remain inactive, and voice/Core sync remains gated until later USER approval.",
            "- Assumption: accepted BP1 changes that alter family, architecture, or edition-boundary policy must fold into the durable source-truth owner before BP2 treats them as implementation scope.",
            "",
            "## Acceptance / Revision / Rejection / Waiver Decision",
            "",
            "- Accept: USER accepts this FAM-007 Dev/Owner Skeleton Readiness Branch Vision and authorizes BP2 preparation only.",
            "- Revise: USER requests specific changes to readiness surfaces, options, proof expectations, private-boundary wording, or future-gated decisions before BP2.",
            "- Hold / More Options: USER wants additional product options, examples, or proof models before accepting or rejecting BP1.",
            "- Reject: USER rejects this branch vision or routes FAM-007 to a different successor candidate.",
            "- Waive: USER explicitly waives BP1 and accepts the risk of planning without a fully accepted Branch Vision.",
            "",
            exact_user_decision,
            "",
        ]
        review_path = target / USER_BRANCH_VISION_REVIEW_FILE
        review_path.write_text("\n".join(lines), encoding="utf-8")
        return review_path.resolve()
    lines = [
        f"# {title} - USER Branch Vision Review",
        "",
        "USER Branch Vision Review: BP1",
        "",
        "## Review Status",
        "",
        review_status,
        "",
        "## Contract Status",
        "",
        contract_status,
        "",
        "## Packet Reviewability State",
        "",
        packet_reviewability_state,
        "",
        "## USER Gate State",
        "",
        user_gate_state,
        "",
        "## Contract Revision",
        "",
        "v3 - generated by the local USER hub helper with applied BP1 review sections.",
        "",
        "## Project Vision Context",
        "",
        f"`{title}` should keep Nexus USER-controlled, inspectable, and local-first by naming the branch outcome in plain language before engineering planning begins. The copied context ({copied_context}) supports that outcome, but the branch vision must stand on its own as a readable USER decision aid.",
        "",
        "## Family Vision Context",
        "",
        f"`{title}` belongs to the family or governance lane represented by the copied source-truth files. If the USER chooses a direction that changes reusable family behavior, Codex must route that accepted change to the durable owner before BP2 relies on it.",
        "",
        "## Feature Vision Context",
        "",
        f"The selected packet context is `{review_purpose}`. BP1 should settle the feature or governance outcome USER expects from this branch, the boundaries that stay future-gated, and which copied owners are context only rather than active operational ledgers.",
        "",
        "## Codex Understanding",
        "",
        review_purpose,
        "",
        "## Branch Goal",
        "",
        f"Name the concrete branch outcome for `{title}` before engineering planning. The goal is to translate `{review_purpose}` into a clear branch direction: what the branch is meant to accomplish, what USER will inspect, and what remains blocked until later approved gates.",
        "",
        "## End-State Vision",
        "",
        f"When this branch reaches its intended end state, USER should be able to point to the accepted outcome for `{title}`, the surfaces or governance behaviors that should exist, the proof expectations that make the outcome trustworthy, and the deferred outcomes that still require later approval.",
        "",
        "## What Will I Actually See, And Where Will I See It?",
        "",
        f"USER should see an applied explanation of `{title}`, a concrete outcome description, named review surfaces, real decision paths, branch-specific recommendations, and design questions that can change BP2. The copied context files remain supporting evidence rather than the vision itself.",
        "",
        "## How It Will Function",
        "",
        f"The branch vision functions as the product and governance target for `{title}`. It names the expected outcome, the surfaces USER will inspect, the boundaries that remain future-gated, and the proof expectations that later planning must preserve.",
        "",
        "## User Experience Flow",
        "",
        f"1. USER reads the branch outcome and the surfaces affected by `{title}`.\n2. USER compares the design paths and tradeoffs.\n3. USER answers the branch-specific questions that control future planning.\n4. Codex digests the response before any later engineering plan treats the vision as accepted.",
        "",
        "## Surface Map",
        "",
        f"- Review surface: `USER_BRANCH_VISION_REVIEW.md` explains the `{title}` branch vision in plain language for USER decision-making.",
        f"- Context surface: `START_HERE.md` maps copied files such as {copied_context} back to repo source truth without making the copy list the vision.",
        "- Decision surface: `USER Response`, `Codex Digest`, and `Acceptance / Revision / Rejection / Waiver Decision` record whether BP1 closes or returns for revision.",
        "- Future proof surface: BP2 and BP3 may use this accepted vision for traceability, but they cannot replace it with engineering convenience or implementation readiness.",
        "",
        "## Product Options / Design Paths",
        "",
        f"- Option A - strongest implied `{title}` outcome: keep the branch focused on the most concrete product, governance, or source-truth result described by the review purpose. Tradeoff: fastest route to BP2, but only safe when USER can clearly visualize the outcome.",
        "- Option B - narrower surface path: reduce the branch to the subset of surfaces USER can confidently approve now. Tradeoff: less risk of overreach, but later branches may need to reconnect deferred surfaces.",
        "- Option C - broader owner/family impact path: treat the branch as changing reusable family or project direction. Tradeoff: stronger long-term alignment, but it may require source-truth fold-down before BP2.",
        "",
        "## Codex Recommendations",
        "",
        f"- Recommendation: Choose the most concrete `{title}` outcome USER can visualize and make that outcome the BP2 target. Tradeoff: this keeps planning grounded, but it may require revising vague branch language before engineering starts.",
        "  USER response:",
        f"- Recommendation: Require any revision to name the expected USER-visible, governance, or source-truth surface for `{title}`. Tradeoff: stricter response digestion takes more care, but it gives BP2 a real contract to build from.",
        "  USER response:",
        "- Recommendation: Treat copied files as context evidence, not as the Branch Vision itself. Tradeoff: USER may inspect fewer raw lines first, but the decision becomes easier to reason about and harder for a template shell to pass.",
        "  USER response:",
        "",
        "## Why This Fits The Nexus Vision",
        "",
        f"This BP1 structure protects the Nexus pattern of USER-controlled, inspectable, local-first planning by making `{title}` explain its purpose before implementation. It keeps project and family vision above seams, helpers, and validators, while still giving Codex enough branch-specific direction to plan the next gate.",
        "",
        "## USER Design Questions",
        "",
        f"- For `{title}`, which concrete outcome should USER expect to see, inspect, or rely on when this branch is complete?",
        "- Which option above best matches the desired direction, and what specific change would make the branch vision feel correct before BP2?",
        "- Are there family-level, architecture-level, policy-level, experience-level, or future-gated boundaries that Codex must preserve instead of folding into this branch?",
        "",
        "## USER Response",
        "",
        user_response,
        "",
        "## Codex Digest",
        "",
        codex_digest,
        "",
        "## USER Response Proof",
        "",
        user_response,
        "",
        "## USER Response Digested",
        "",
        "No - BP1 remains open until Codex digests an explicit USER response or waiver."
        if not pr_readiness_context_packet
        else "Not applicable - this is a later-phase context copy, not a new BP1 gate.",
        "",
        "## Accepted Branch Vision",
        "",
        accepted_vision,
        "",
        "## Family-Vision Versus Branch-Only Vision Impact",
        "",
        "Branch-only unless USER response creates a reusable family or project-wide standard that must fold into the proper durable owner.",
        "",
        "## Must-Have Behavior",
        "",
        "- BP1 must be accepted or explicitly waived before BP2/BP3 can authorize implementation.",
        "- SLCs must trace to an accepted Branch Vision requirement.",
        "",
        "## Future-Gated Decisions And Regression-Risk Controls",
        "",
        "- Regression-risk control: SLCs remain engineering route details inside an accepted branch, not automatic separate branches.",
        "- Regression-risk control: Workstream remains blocked until BP1 and BP2 are accepted or explicitly waived and BP3 is green.",
        "- Regression-risk control: USER-facing review files stay focused on vision, plan context, options, risks, proof expectations, and USER decisions rather than mutable operational metadata.",
        "",
        "## Deferred And Future-Gated Ideas",
        "",
        *_markdown_lines(pending_user_decisions),
        "",
        "## Vision Question Queue",
        "",
        "Pending USER review.",
        "",
        "## Design Assumption Ledger",
        "",
        "- Assumption: USER-facing Branch Vision acceptance is required unless explicitly waived.",
        "- Assumption: accepted branch vision changes fold into durable source-truth owners only after USER-approved digest.",
        "",
        "## Acceptance / Revision / Rejection / Waiver Decision",
        "",
        exact_user_decision,
        "",
    ]
    review_path = target / USER_BRANCH_VISION_REVIEW_FILE
    review_path.write_text("\n".join(lines), encoding="utf-8")
    return review_path.resolve()


def _write_pr_readiness_stage1_review(
    *,
    target: Path,
    title: str,
    review_purpose: str,
    exact_user_decision: str,
    pending_user_decisions: list[str],
    copied: list[tuple[str, str]],
    stage1_outcome: str,
) -> Path:
    """Write the dedicated current-gate artifact for PR Readiness Stage 1."""

    copied_sources = "\n".join(
        f"- `{copied_rel}`" for _source_rel, copied_rel in copied
    ) or "- No copied context files were supplied."
    pending = "\n".join(f"- {decision}" for decision in pending_user_decisions) or "- None recorded."
    lines = [
        f"# {title} - PR Readiness Stage 1 Review",
        "",
        "This is the primary current-gate review artifact for PR Readiness Stage 1. "
        "BP1, BP2, and BP3 files remain supporting planning context; they are not this "
        "gate's decision surface.",
        "",
        "## Review Status",
        "",
        "Reviewable - this packet presents the current PR Readiness Stage 1 analysis "
        "and its repair posture for USER inspection.",
        "",
        "## Contract Status",
        "",
        "Complete - the current-gate artifact class is distinct from the BP2 Branch Plan "
        "Contract and does not imply Stage 2 approval, PR creation, merge, or release.",
        "",
        "## Packet Reviewability State",
        "",
        "Reviewable - structural parity and current-gate content must still be validated "
        "against the generated folder and timestamped upload artifact.",
        "",
        "## USER Gate State",
        "",
        "Pending USER Review - USER may accept, revise, waive, reject, or hold the Stage 1 "
        "analysis. This state is not a USER acceptance receipt.",
        "",
        "## Current-Gate Purpose",
        "",
        review_purpose,
        "",
        "## Scope And Authority",
        "",
        "This review covers only the approved Governance repair. Durable phase law, "
        "source ownership, transition rules, and validation contracts remain governed by "
        "the routed repository owners. Live branch, packet, and external projection facts "
        "remain evidence owned by the helper and external operational state.",
        "",
        "## Transition-Safety Review",
        "",
        "The Stage 1 decision must account for target-currentness, alias disagreement, "
        "pre-write snapshots, no-loss recovery, atomic replacement, complete audit fields, "
        "and the distinction between a target-scoped PASS and a root-wide PASS.",
        "",
        "## Adversarial And False-Green Review",
        "",
        "A green packet requires adversarial coverage for intervening target edits, stale or "
        "wrong-root snapshots, missing target copies, conflicting field aliases, path aliases, "
        "added and replaced fields, stale current-gate artifacts, and BP2-primary misclassification. "
        "Structural ZIP parity alone is not PR Readiness proof.",
        "",
        "## Supporting Source-Truth Context",
        "",
        copied_sources,
        "",
        "## Remaining USER Decisions",
        "",
        pending,
        "",
        "## Stage 1 Outcome",
        "",
        (
            f"{stage1_outcome} - all bounded repair, generated packet, external projection, "
            "and validation prerequisites are recorded in the current Stage 1 digest."
            if stage1_outcome == PR_STAGE1_OUTCOME_READY
            else f"{stage1_outcome} - the current-gate review remains held until the bounded "
            "repair, generated packet, external projections, and full validation are green."
        ),
        "",
        "## Exact USER Decision Supported",
        "",
        exact_user_decision,
        "",
    ]
    review_path = target / PR_READINESS_STAGE1_REVIEW_FILE
    review_path.write_text("\n".join(lines), encoding="utf-8")
    return review_path.resolve()


def _write_pr_readiness_stage1_packet_digests(
    *,
    target: Path,
    stage1_outcome: str,
    exact_user_decision: str,
    copied: list[tuple[str, str]],
    pending_user_decisions: list[str],
) -> list[Path]:
    """Write only current-gate support aids for a PR Stage 1 packet.

    BP and Workstream artifacts are useful in their own gates, but retaining
    their active pending language in a completed PR Stage 1 packet creates a
    false current-gate signal. This profile is intentionally source-list
    driven and phase-specific.
    """

    normalized_decision = re.sub(r"\s+", " ", exact_user_decision).strip()
    copied_paths = [copied_rel for _source_rel, copied_rel in copied]
    copied_lines = "\n".join(f"- `{path}`" for path in copied_paths) or "- None."
    pending_lines = "\n".join(
        f"- {decision}" for decision in pending_user_decisions
    ) or "- None recorded."
    outcome_line = (
        "Stage 1 is complete and the packet supports the separate Stage 2 USER decision."
        if stage1_outcome == PR_STAGE1_OUTCOME_READY
        else "Stage 1 remains in repair-required posture; Stage 2 is not supported."
    )
    common = (
        "Current Gate: PR Readiness Stage 1\n"
        f"Stage 1 Outcome: {stage1_outcome}\n"
        "Primary Current-Gate File: `USER Review/PR_READINESS_STAGE1_REVIEW.md`\n"
        "Next Decision: PR Readiness Stage 2 only when Stage 1 is ready.\n"
    )
    files: dict[str, str] = {
        "PR_READINESS_STAGE1_COVERAGE_DIGEST.md": (
            "# PR Readiness Stage 1 Coverage Digest\n\n"
            f"{common}\n"
            f"{outcome_line}\n\n"
            "This aid is the current-gate digest for the Governance PR Readiness "
            "Stage 1 result. It does not reopen BP1, BP2, or BP3, and it does not "
            "authorize Workstream implementation, PR creation, merge, release, "
            "issue mutation, or sibling-worktree mutation.\n\n"
            "## Review Order\n\n"
            "Open the primary Stage 1 review first. Use this digest for the bounded "
            "repair outcome, then use the source coverage and contradiction checklist.\n\n"
            "## Stage 1 Result\n\n"
            f"{stage1_outcome}. The exact next USER decision is:\n\n"
            f"{normalized_decision}\n\n"
            "## Current-Gate Boundary\n\n"
            "Stage 1 is the current review surface. Stage 2 remains a separate USER "
            "decision. BP1, BP2, BP3, Workstream, Hardening, Live Validation, "
            "Release Readiness, merge, release, and sibling adoption are not current "
            "decision paths in this packet.\n\n"
            "## Pending USER Decisions\n\n"
            f"{pending_lines}\n"
        ),
        "PR_READINESS_STAGE1_SOURCE_COVERAGE.md": (
            "# PR Readiness Stage 1 Source Coverage\n\n"
            f"{common}\n"
            "The following list is generated directly from the files copied into "
            "this packet. No additional backlog, roadmap, family vision, edition, "
            "runtime, or worktree-slot coverage is implied unless it appears below.\n\n"
            "## Copied Source-Truth Files\n\n"
            f"{copied_lines}\n\n"
            f"Copied Source Count: `{len(copied_paths)}`\n"
            "Coverage Rule: every source-coverage claim in this packet must resolve "
            "to one of these copied paths.\n"
        ),
        "PR_READINESS_STAGE1_CONTRADICTION_CHECKLIST.md": (
            "# PR Readiness Stage 1 Contradiction Checklist\n\n"
            f"{common}\n"
            "## Required Current-Gate Conditions\n\n"
            "- PASS: the Stage 1 review is the only primary USER decision artifact.\n"
            "- PASS: START_HERE and all current-gate aids route to Stage 1 / Stage 2.\n"
            "- PASS: no active Workstream Entry decision path is emitted.\n"
            "- PASS: no BP1, BP2, or BP3 gate is presented as the current pending gate.\n"
            "- PASS: copied-source coverage is limited to the actual packet file set.\n"
            "- PASS: Stage 2 remains pending and is not treated as accepted.\n\n"
            "## Exact Decision Boundary\n\n"
            f"{normalized_decision}\n"
        ),
    }
    written: list[Path] = []
    for name, text in files.items():
        path = target / name
        path.write_text(text, encoding="utf-8")
        written.append(path.resolve())
    return written


def _write_stage1_ready_support_context(
    *,
    target: Path,
    title: str,
    review_purpose: str,
    exact_user_decision: str,
    pending_user_decisions: list[str],
    copied: list[tuple[str, str]],
) -> Path:
    """Write BP2-named context without reopening a completed Stage 1 gate."""

    copied_sources = "\n".join(
        f"- `{source_rel}` copied as `{copied_rel}`"
        for source_rel, copied_rel in copied
    ) or "- No copied context files were supplied."
    pending = "\n".join(
        f"- {decision}" for decision in pending_user_decisions
    ) or "- None recorded."
    lines = [
        f"# USER Branch Plan Review - {title}",
        "",
        "## Contract Status",
        "",
        "Context Only - PR Readiness Stage 1 is ready for the separate Stage 2 USER decision; "
        "this BP2-named file is supporting context, not a current gate.",
        "",
        "## Packet Reviewability State",
        "",
        "Reviewable - this file supports the dedicated Stage 1 primary review artifact.",
        "",
        "## USER Gate State",
        "",
        "Context Only - this file is not a USER gate and records no new BP2 acceptance.",
        "",
        "## Review Purpose",
        "",
        review_purpose,
        "",
        "## Stage 1 / Stage 2 Boundary",
        "",
        "Stage 1 is ready for the separate Stage 2 USER decision. Open "
        f"`{PR_READINESS_STAGE1_REVIEW_FILE}` as the only Stage 1 decision artifact.",
        "",
        "Stage 2 remains pending USER approval. This support context does not authorize "
        "PR creation, implementation, merge, release, cleanup, runtime, private, or sibling work.",
        "",
        "## BP2 Context",
        "",
        "This file preserves lifecycle, engineering-plan, proof, rollback, and source-truth "
        "context for the completed Stage 1 review. It does not ask USER to accept BP2 or "
        "re-accept Stage 1.",
        "",
        "## Review Order",
        "",
        f"1. Open `{PR_READINESS_STAGE1_REVIEW_FILE}` first.",
        "2. Use this file only as supporting context.",
        "3. Use the separate Stage 2 decision before any PR mutation.",
        "",
        "## Supporting Source-Truth Files",
        "",
        copied_sources,
        "",
        "## Future-Gated Boundaries",
        "",
        "- PR Readiness Stage 2, PR creation, merge, release, cleanup, runtime, provider/model, cache/memory, private setup, and sibling mutation remain separately gated.",
        "- No implementation seam is authorized by this supporting context file.",
        "",
        "## Pending USER Decisions",
        "",
        pending,
        "",
        "## Exact USER Decision Supported",
        "",
        exact_user_decision,
        "",
    ]
    review_path = target / USER_BRANCH_PLAN_REVIEW_FILE
    review_path.write_text("\n".join(lines), encoding="utf-8")
    return review_path.resolve()


def _write_user_branch_plan_review(
    *,
    target: Path,
    title: str,
    review_purpose: str,
    source_branch: str,
    source_head: str,
    upstream: str,
    origin_main: str,
    exact_user_decision: str,
    pending_user_decisions: list[str],
    copied: list[tuple[str, str]],
    stage1_outcome: str | None = None,
) -> Path:
    is_active_overlay_recording = any(
        "active_overlay_recording_runtime_foundation" in source_rel
        for source_rel, _copied_rel in copied
    )
    is_fam007_breakpoint_2 = (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
    )
    is_fam007_owner_ai_foundation = (
        source_branch == "feature/fam-007-owner-ai-operational-foundation-gates"
    )
    is_fam007_dev_owner_skeleton = source_branch == "feature/fam-007-dev-owner-skeleton-readiness"
    is_fam007_private_boundary_setup = (
        source_branch == "feature/fam-007-dev-owner-private-boundary-setup"
    )
    normalized_decision = exact_user_decision.casefold()
    is_fam006_recording = (
        source_branch == "feature/fam-006-dashboard-recording-start-stop-local-file"
    )
    fam006_workstream_approval_review_packet = (
        _is_fam006_workstream_implementation_approval_review(
            normalized_decision,
            is_fam006_recording=is_fam006_recording,
        )
    )
    if fam006_workstream_approval_review_packet:
        copied_sources = "\n".join(
            f"- `{source_rel}` copied as `{copied_rel}`" for source_rel, copied_rel in copied
        )
        pending = "\n".join(f"- {decision}" for decision in pending_user_decisions) or "- None recorded."
        lines = [
            f"# {title} - Workstream Implementation Approval Review",
            "",
            "USER Branch Plan Review: Accepted BP2 context for Workstream implementation approval",
            "",
            "## Review Status",
            "",
            "Reviewable - this support file preserves accepted BP2 planning context for the primary Workstream implementation approval review.",
            "",
            "## Contract Status",
            "",
            "Complete - BP2 Option C Branch Plan was accepted by USER; implementation remains pending until USER approves the primary packet.",
            "",
            "## Packet Reviewability State",
            "",
            "Reviewable - Workstream implementation approval packet support context.",
            "",
            "## USER Gate State",
            "",
            "Pending USER Review - Workstream/runtime implementation remains pending until USER approves the primary packet.",
            "",
            "## Accepted Implementation Package",
            "",
            "- Dashboard Recording Card as the compact quick-access/status surface.",
            "- Recording Studio as the focused recording control/status surface.",
            "- Minimal Log Viewer Studio launch/folder shell where it directly supports native/export log access.",
            "- Native/export log boundary with native NDAI logs as the normal product artifact and exported logs as USER-requested export artifacts.",
            "- Open-folder pre-session usability.",
            "- Issue #258 target reliability as a distinct admitted repair line item.",
            "",
            "## Entry Checkpoint And Continuation Guard",
            "",
            "SLC-051 / Seam 1 target reliability may start the package. A green first seam is continuation proof, not package completion. Single-seam or single-slice authority is not granted.",
            "",
            "## Workstream Approval Boundary",
            "",
            "Workstream/runtime implementation remains pending until USER approves the primary Workstream implementation approval packet.",
            "",
            "## Supporting Source-Truth Files",
            "",
            copied_sources or "- None copied.",
            "",
            "## Pending USER Decisions",
            "",
            pending,
            "",
            "## Exact USER Decision Supported",
            "",
            exact_user_decision,
            "",
        ]
        review_path = target / USER_BRANCH_PLAN_REVIEW_FILE
        review_path.write_text("\n".join(lines), encoding="utf-8")
        return review_path.resolve()
    workstream_package_approval_packet = any(
        marker in normalized_decision
        for marker in BRANCH_PLANNING_IMPLEMENTATION_REQUEST_MARKERS
    ) and not any(
        marker in normalized_decision
        for marker in BRANCH_PLANNING_IMPLEMENTATION_BLOCKING_MARKERS
    )
    dev_owner_workstream_green_packet = (
        is_fam007_dev_owner_skeleton
        and not is_fam007_breakpoint_2
        and "approve bounded hardening h1" in normalized_decision
    )
    dev_owner_hardening_h1_packet = (
        is_fam007_dev_owner_skeleton
        and not is_fam007_breakpoint_2
        and "approve bounded live validation lv1" in normalized_decision
    )
    dev_owner_live_validation_lv1_packet = (
        is_fam007_dev_owner_skeleton
        and not is_fam007_breakpoint_2
        and "approve bounded pr readiness stage 1" in normalized_decision
    )
    pr_readiness_stage1_packet = (
        _is_pr_readiness_stage1_packet(
            source_branch=source_branch,
            normalized_decision=normalized_decision,
            stage1_outcome=stage1_outcome,
        )
        if stage1_outcome is not None
        else (
            "pr readiness stage 1 analysis" in normalized_decision
            and not dev_owner_live_validation_lv1_packet
        )
    )
    stage1_ready_support_context = (
        pr_readiness_stage1_packet
        and stage1_outcome == PR_STAGE1_OUTCOME_READY
        and not is_fam007_breakpoint_2
    )
    if stage1_ready_support_context:
        return _write_stage1_ready_support_context(
            target=target,
            title=title,
            review_purpose=review_purpose,
            exact_user_decision=exact_user_decision,
            pending_user_decisions=pending_user_decisions,
            copied=copied,
        )
    bp1_branch_vision_packet = (
        "bp1 branch vision" in normalized_decision
        and any(
            marker in normalized_decision
            for marker in (
                "authorize bp2 user branch plan review only",
                "authorize bp2 user branch plan review preparation only",
                "authorize bp2 preparation only",
            )
        )
    )
    bp3_orchestration_packet = (
        not workstream_package_approval_packet
        and (
            "bp3" in normalized_decision
            or "workstream entry / orchestration" in normalized_decision
            or "orchestration validation" in normalized_decision
        )
    )
    bp2_branch_plan_packet = (
        not bp1_branch_vision_packet
        and not bp3_orchestration_packet
        and (
            "bp2 user branch plan review" in normalized_decision
            or "bp2 branch plan review" in normalized_decision
        )
    )
    active_branch_files = [
        copied_rel
        for source_rel, copied_rel in copied
        if "active_overlay_recording_runtime_foundation" in source_rel
    ]
    rollback_context_files = [
        copied_rel
        for source_rel, copied_rel in copied
        if "recording_profile_runtime_foundation" in source_rel
    ]
    source_truth_files = [
        copied_rel
        for source_rel, copied_rel in copied
        if source_rel
        in {
            "Docs/feature_backlog.md",
            "Docs/prebeta_roadmap.md",
            "Docs/branch_records/index.md",
            "Docs/branch_plans/README.md",
            "Docs/family_visions/FAM-006_monitoring_and_hud.md",
            "Docs/ai_runtime_and_trust_architecture.md",
            "Docs/family_visions/FAM-007_local_ai_and_capability_packs.md",
            "Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md",
        }
    ]
    extra_plan_sections: list[str] = []
    user_response_text: str | None = None
    likely_files_lines = [
        f"`{source_rel}` copied as `{copied_rel}`" for source_rel, copied_rel in copied
    ]
    user_decisions_intro = (
        "USER may answer in order or respond generally. Useful feedback includes visual "
        "direction, workflow changes, window behavior, output-file expectations, "
        "deferred scope, or anything that would make the branch plan feel wrong before "
        "implementation planning begins."
    )
    if is_active_overlay_recording:
        active_plan_source = next(
            (
                source_rel
                for source_rel, _copied_rel in copied
                if source_rel.endswith(
                    "Docs/branch_plans/feature_fam_006_active_overlay_recording_runtime_foundation.md"
                )
            ),
            None,
        )
        accepted_user_response = (
            _source_marker(active_plan_source, "USER Review Response:") if active_plan_source else None
        )
        codex_response_digest = (
            _source_marker(active_plan_source, "Codex Response Digest:") if active_plan_source else None
        )
        workstream_entry_result = (
            _source_marker(active_plan_source, "Workstream Entry Result:") if active_plan_source else None
        )
        contract_status = (
            _source_marker(active_plan_source, "Contract Status:") if active_plan_source else None
        ) or "Pending USER Confirmation - Codex revised this review into the closed-loop BP2 Branch Plan Contract; USER must confirm the revised contract or explicitly waive it before implementation."
        contract_version = (
            _source_marker(active_plan_source, "Contract Version / Revision:") if active_plan_source else None
        ) or "v3 - USER recording product-model revision."
        what_user_sees = (
            "HUD Overlay card: a compact recording launcher and target/status preview inside the "
            "existing card, showing the active Overlay Profile name, a Recording Target / Active "
            "Recording Target label, a concise target summary, future-gated status, and a future "
            "Open Recording Control action. Recording Control window: a later compact standalone "
            "normal Windows/NDAI window for target summary and future controls/settings, with "
            "secondary settings windows when details would make the main control bulky. Native Log "
            "Loader: a separate future graph/log viewer, not the recording control surface."
        )
        why_nexus = (
            "This fits Nexus because it keeps recording intuitive, avoids a confusing second profile "
            "system, keeps the HUD lightweight, gives the user a compact normal OS window for ongoing "
            "control, keeps graph/log viewing separate from recording control, and protects future "
            "log quality by preserving per-overlay effective polling policy as architecture before "
            "recording execution exists."
        )
        design_ballot = [
            "Accept Codex recommendation.",
            "Accept with changes.",
            "Choose another option.",
            "Request hybrid option.",
            "Reject and ask for more options.",
            "Pause / unclear.",
        ]
        response_structure = [
            "Decision.",
            "Required changes.",
            "Must-have behavior.",
            "Future-gated boundary controls.",
            "Future-gated ideas.",
            "General response.",
        ]
        digest_structure = [
            "USER intent summary.",
            "Accepted USER decisions.",
            "Rejected or deferred USER ideas.",
            "Implementation constraints created from USER response.",
            "Source-truth updates required.",
            "Review packet updates required.",
            "Open questions.",
            "Contract Status after digest.",
            "Next USER decision needed.",
        ]
        implementation_constraints = [
            "This planning/governance branch must not implement SLC-051 or any runtime/user-facing recording work.",
            "Future SLC-051 remains state/proof-only and must not add recording execution, file writing, or real Start/Stop behavior.",
            "Recording target derives only from active Overlay Profile membership and must cover null, empty, selected, switched, deleted/stale, duplicate/stale-ID, and high-volume membership states.",
            "No separate Recording Profile system or recording-specific sensor chooser is admitted.",
            "Start/Stop behavior remains future-gated until an approved seam admits execution; any later placeholder must be clearly disabled or future-gated.",
            "Native Log Loader remains future planning input unless USER separately approves durable source-truth mutation or implementation.",
            "Per-overlay effective polling policy remains future planning/source-truth constraint and SLC-051 must not design against it.",
            "Overlay Profile, Overlay Display, Monitor Group, Dashboard, Manage Monitors, and Sensor Command Center behavior must remain preserved.",
        ]
        rejected_deferred = [
            "Rejected for this branch direction: separate profile-loaded Recording Profile system.",
            "Rejected as the desired long-term polling model: duplicate CPU FAST / CPU SLOW Monitor Groups solely to vary polling cadence.",
            "Deferred: recording execution, file writing, real Start/Stop controls, tray controls, export/share, provider/model work, broad theme/skin work, FAM-007 work, old branch cleanup/deletion, per-overlay effective polling policy implementation, and durable Native Log Loader source-truth mutation.",
        ]
        source_truth_impact = [
            "Family vision: record per-overlay effective polling policy as a future FAM-006 planning constraint and keep Native Log Loader as future graph/log viewer input only.",
            "Active external branch plan and branch record: record the accepted v3/v4 planning-governance posture, USER vision digest, implementation constraints, Workstream skip, and PR Readiness Stage 1 as the next legal phase.",
            "Backlog/roadmap: record planning-governance PR-readiness posture rather than runtime implementation posture.",
            "Review packet: refresh whenever contract status, response, digest, constraints, source-truth impact, or copied source-truth inputs change.",
            "Workstream seam order: target model remains future implementation staging, not current branch work.",
        ]
        contract_change_log = [
            "v1 - USER-facing Branch Plan Review packet introduced with end-state/options sections.",
            "v2 - Hardened into BP2 Branch Plan Contract with closed-loop response/digest, implementation constraints, source-truth impact, confirmation loop, and waiver semantics.",
            "v3 - Digested USER recording product-model feedback: HUD Overlay launcher/target preview, standalone Recording Control window, Native Log Loader separation, future per-overlay effective polling policy, and target-model-first SLC-051.",
            "v4 - USER accepted the plan and redirected this branch to planning/governance PR Readiness with Workstream skipped and runtime implementation deferred to a future USER-approved carrier.",
        ]
        completion_checklist = [
            "Contract Status is Complete or Waived by USER.",
            "USER response is present, attached, or explicitly waived.",
            "Codex Response Digest is present.",
            "Implementation Constraints Created By USER Response are present.",
            "Vision Delta / Source-Truth Impact is resolved.",
            "USER Rejected / Deferred Ideas are recorded.",
            "Contract Change Log is current.",
            "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
            "Workstream Entry Result is present only after response/digest or waiver.",
            "Exact implementation approval text cites completed or waived contract status.",
        ]
        plain_english_summary = (
            "This branch is setting up the corrected FAM-006 recording direction: "
            "recording should be driven by the currently active Overlay Profile, "
            "not by loading a separate Recording Profile. The intended future "
            "feature uses the HUD Overlay card as the launcher and target/status "
            "preview, a compact standalone Recording Control window as the control "
            "surface, and a separate future Native Log Loader for graph/log viewing."
        )
        end_state_vision = (
            "When this branch's admitted package is complete, the HUD Overlay card should make "
            "recording feel tied to the overlay the user already chose. The user should understand "
            "which active Overlay Profile members are the intended recording target, launch a compact "
            "standalone Recording Control window from the HUD Overlay card, and keep graph/log viewing "
            "separate in a future Native Log Loader. Actual file writing and real Start/Stop remain "
            "separately approved."
        )
        walkthrough = [
            "Dashboard / HUD Overlay card: the recording area should sit inside the existing HUD Overlay card as launcher and target/status preview before Start/Stop execution is admitted.",
            "Active Overlay Profile membership: the selected overlay's active members become the future recording target; no separate Recording Profile selector is introduced.",
            "Target visibility: SLC-051 should prove null, empty, selected, switched, deleted/stale, duplicate/stale-ID, and high-volume target states before visible controls depend on that model.",
            "Recording Control window: later seams plan a small independent NDAI/Windows window that can be moved, minimized, taskbar-restored, and kept open outside Dashboard child-window lifetime.",
            "Secondary settings/details windows: bulky or advanced settings should open outside the compact control surface when USER later approves them.",
            "Output contract and Native Log Loader: later seams plan graph/plot-ready files, while Native Log Loader remains a separate future viewer unless USER separately admits it.",
        ]
        surface_map = [
            "HUD Overlay card: launcher and active target/status preview surface.",
            "Recording Control window: compact standalone control surface for future target summary, Start/Stop, and path/status controls after approval.",
            "Dashboard: hosts the HUD Overlay card and must not regress existing Dashboard behavior.",
            "Manage Monitors / Sensor Command Center: remain monitor/source management owners; recording target proof must not mutate their state.",
            "Overlay Profile / Overlay Display: remain display and membership owners; recording reads active membership without taking ownership.",
            "Monitor Group: reusable sensor/source group; future per-overlay effective polling policy should avoid duplicate FAST/SLOW group workarounds.",
            "Files/output: future graph/plot-ready recording contract only after explicit approval.",
            "Native Log Loader: future separate graph/log viewer for completed recordings.",
            "Tray/export/provider/theme/FAM-007: future-gated surfaces outside this branch unless USER separately approves.",
        ]
        implementation_options = [
            "Option A - Target model proof first: prove the active-overlay recording target model before visible controls depend on it. Pros: safest foundation; Cons: least visible at first; Risk: low. Codex recommends this first.",
            "Option B - Target preview in HUD card: show active target/status preview in the HUD Overlay card after or alongside safe target proof. Pros: strong user clarity; Cons: needs visual proof; Risk: low to medium.",
            "Option C - Standalone Recording Control window shell first: build the compact OS-level window before target proof is complete. Pros: validates window feel early; Cons: weaker target-model foundation; Risk: medium.",
            "Option D - Live Start/Stop planning later: plan real controls only after recording execution and file writing are admitted. Pros: avoids fake execution; Cons: later visible payoff; Risk: low when deferred.",
        ]
        recommended_direction = (
            "Codex recommends Option A first: establish the active Overlay Profile target model, "
            "then use later seams for HUD target preview, the standalone Recording Control window, "
            "output-file contract, and live/user proof. For future recording execution, Codex "
            "recommends snapshot-at-recording-start by default unless USER revises it, while SLC-051 "
            "proves the live current active-overlay target because no recording is occurring yet."
        )
        current_scope = [
            "Preserve the accepted active-overlay recording end-state as maintained source truth.",
            "Record that active Overlay Profile membership is the source of truth for future recording targets.",
            "Keep future SLC-051 target-model-first and avoid blocking future per-overlay effective polling policy.",
            "Confirm this branch does not change Dashboard, Manage Monitors, Sensor Command Center, Overlay Profile, Overlay Display, Monitor Group, or recording runtime behavior.",
            "Proceed only to PR Readiness Stage 1 after USER approval; runtime implementation belongs to a later USER-approved carrier.",
        ]
        future_scope = [
            "Recording execution and file writing remain blocked until an approved seam admits them.",
            "Tray recording controls, export/share/import, provider/model work, broad theme/skin work, FAM-007 work, old branch cleanup, PR, merge, release, and issue mutation remain separate USER decisions.",
            "Native Log Loader is early USER input only unless USER separately approves durable source-truth mutation.",
            "Per-overlay effective polling policy is future FAM-006 architecture unless USER separately admits implementation.",
        ]
        slc_package_plan = [
            "Implementation staging note, not the USER decision surface: Codex uses SLC-051 through SLC-055 internally to sequence the accepted end-state safely.",
            "Target model comes first because every later UI/control/output behavior depends on knowing what would be recorded.",
            "HUD target preview, Recording Control window, output contract, and validation/live proof follow as staged implementation only after the end-state and boundaries are accepted.",
        ]
        user_decisions = [
            "Does USER approve PR Readiness Stage 1 analysis for this planning/governance branch?",
            "Does USER agree that no runtime/user-facing recording work, SLC-051 implementation, Workstream implementation, H1, LV1, or UTS is claimed by this branch?",
            "Does USER agree that the accepted active-overlay product contract is preserved for a future implementation carrier?",
            "Does USER want a revision before PR Readiness, or should PR Readiness inspect this no-runtime closeout?",
        ]
    elif is_fam007_breakpoint_2:
        seam1_approval_packet = "approve bounded workstream implementation" in exact_user_decision.casefold()
        seam1_completion_packet = "approve or revise seam 2" in exact_user_decision.casefold()
        workstream_green_packet = "approve bounded hardening h1" in exact_user_decision.casefold()
        hardening_h1_packet = "approve bounded live validation lv1" in exact_user_decision.casefold()
        lv1_green_packet = "approve bounded pr readiness stage 1" in exact_user_decision.casefold()
        pr_stage2_packet = "approve pr readiness stage 2" in exact_user_decision.casefold()
        accepted_user_response = (
            "Status: USER Accepted - USER approved this repaired branch contract as the "
            "decision-path basis for bounded Seam 1 implementation approval."
            if seam1_approval_packet
            else (
                "Status: Workstream Green - this packet records all admitted public-safe "
                "Breakpoint 2 Workstream proof seams and asks USER to approve or revise Hardening H1."
            )
            if workstream_green_packet
            else (
                "Status: Seam 1 Complete - this packet records public-safe action-gate "
                "registry proof and asks USER to approve or revise Seam 2."
            )
            if seam1_completion_packet
            else (
                "Status: Pending USER Acceptance Or Waiver - this repaired contract is ready for "
                "USER to accept, revise, reject, or explicitly waive before Seam 1 implementation."
            )
        )
        codex_response_digest = (
            "Workstream is green for the FAM-007 Breakpoint 2 Dev/Owner skeleton action-gate "
            "readiness carrier. Codex recorded Seams 1 through 4 as public-safe proof, "
            "added direct validator fixture proof, folded source truth down, and preserved "
            "all private/runtime/provider/cache/memory action gates. Codex recommends "
            "Hardening H1 next."
            if workstream_green_packet
            else
            "Seam 1 is complete for the FAM-007 Breakpoint 2 Dev/Owner skeleton action-gate "
            "readiness carrier. Codex recorded the action-gate registry, exact USER decision proof, "
            "source-truth fold-down, and direct validator fixture proof without performing any gated "
            "private/runtime action. Codex recommends Seam 2 next: private/public boundary and "
            "private remote safety proof."
            if seam1_completion_packet
            else (
                "Workstream Entry analysis is green for the FAM-007 Breakpoint 2 Dev/Owner skeleton "
                "action-gate readiness carrier. Codex recommends Seam 1 first: action-gate registry "
                "and exact USER decision proof. Seam 1 should create public-safe proof of the private "
                "Dev repo, private Owner repo, local-only private root, private remote, backup/import, "
                "provider/model/runtime/cache/memory, voice/Core, shortcut/installer, PR/merge/release, "
                "cleanup, AI Product Contract import, Private Dev ORIN import, and v1.8.0 gates without "
                "performing any gated action."
            )
        )
        if hardening_h1_packet:
            accepted_user_response = (
                "Status: Hardening H1 Green - this packet records bounded proof comparison, "
                "H1-scoped drift repair, and asks USER to approve or revise Live Validation LV1."
            )
            codex_response_digest = (
                "Hardening H1 is green for the FAM-007 Breakpoint 2 Dev/Owner skeleton "
                "action-gate readiness carrier. Codex compared Seams 1 through 4 against "
                "source truth, validators, fixtures, packet proof, and external-state boundaries; "
                "repaired stale duplicate Workstream-pending ledger wording; and preserved all "
                "private/runtime/provider/cache/memory action gates. Codex recommends bounded "
                "Live Validation LV1/no-visible-runtime proof next."
            )
        if lv1_green_packet:
            accepted_user_response = (
                "Status: Live Validation LV1 Green - this packet records no-visible-runtime proof, "
                "UTS waiver evidence, and asks USER to approve or revise PR Readiness Stage 1 analysis."
            )
            codex_response_digest = (
                "Live Validation LV1 is green for the FAM-007 Breakpoint 2 Dev/Owner skeleton "
                "action-gate readiness carrier. Codex recorded no-visible-runtime proof, waived UTS "
                "and user-facing shortcut validation because no app UI/runtime/provider/model/cache/"
                "memory/private/backup/import/voice/Core/shortcut/installer surface changed, preserved "
                "all private/runtime/provider/cache/memory action gates, and recommends bounded PR "
                "Readiness Stage 1 analysis next."
            )
        if pr_stage2_packet:
            accepted_user_response = (
                "Status: PR Readiness Stage 1 Ready For Stage 2 - this packet records no live PR, "
                "Stage 2 PR creation pending USER approval, merge-stable historical/no-active projection, "
                "no-release-debt posture, selected-next default/defer posture, and preserved private/runtime gates."
            )
            codex_response_digest = (
                "PR Readiness Stage 1 is green for the FAM-007 Breakpoint 2 Dev/Owner skeleton "
                "action-gate readiness carrier. Codex recorded no-live-PR posture, pending Stage 2 PR "
                "creation approval, folded repo-tracked active authority to historical/no-active projection, "
                "refreshed packet/source-truth evidence, preserved no-release-debt posture, and recommends "
                "PR Readiness Stage 2 PR creation only after explicit USER approval."
            )
        if pr_stage2_packet:
            workstream_status_text = (
                "Status: PR Readiness Stage 1 Ready For Stage 2 - no live PR exists; "
                "PR Readiness Stage 2 PR creation remains pending USER approval.\n\n"
            )
        elif workstream_green_packet:
            workstream_status_text = (
                "Status: Workstream Green - Seams 1 through 4 are implemented as public-safe "
                "proof only; Hardening H1 remains pending USER decision.\n\n"
            )
        elif lv1_green_packet:
            workstream_status_text = (
                "Status: Live Validation LV1 Green - no visible runtime surface changed; "
                "UTS and user-facing shortcut validation are waived; PR Readiness Stage 1 "
                "remains pending USER approval.\n\n"
            )
        elif hardening_h1_packet:
            workstream_status_text = (
                "Status: Hardening H1 Green - Seams 1 through 4 were compared against "
                "source truth, fixtures, validators, packet proof, and external-state boundaries; "
                "Live Validation LV1 remains pending USER decision.\n\n"
            )
        elif seam1_completion_packet:
            workstream_status_text = (
                "Status: Seam 1 Complete - action-gate registry and exact USER decision proof "
                "are implemented as public-safe proof only; Seam 2 remains pending USER decision.\n\n"
            )
        elif seam1_approval_packet:
            workstream_status_text = (
                "Status: Workstream Entry Green - USER accepted the repaired branch contract; "
                "Seam 1 is approved as the first bounded Workstream implementation seam: "
                "Action-gate registry and exact USER decision proof.\n\n"
            )
        else:
            workstream_status_text = (
                "Status: Workstream Entry Green - recommended first seam is Seam 1, "
                "Action-gate registry and exact USER decision proof.\n\n"
            )
        workstream_entry_result = (
            workstream_status_text
            + (
            "Affected surfaces: active external branch plan, active branch record, USER review packet, packet "
            "bundle helper, validation helper registry when helper behavior changes, and any public-safe "
            "fixtures or validators needed to prove action-gate preservation.\n\n"
            "Validators and fixtures: branch governance, worktree confinement, release-readiness health, "
            "governance efficiency, source-owner markers, release body, AI provider state, public leak "
            "prevention, branch-readiness planning fixtures, external state validation when present, "
            "packet decision-path validation, compileall, and worktree rebaseline audit.\n\n"
            "USER-facing proof expectations: refreshed START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, "
            "USER_REVIEW_FOLDER_AND_FILE_DIGEST.md, GOVERNANCE_REQUIRED_FILES_SCAN.md, "
            "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md, BRANCH_VISION_VALIDATION_CHECKLIST.md, exported ZIP, "
            "and review evidence digest must all agree on decision path, USER decision, and "
            "pending gates.\n\n"
            f"Exact implementation approval text: {exact_user_decision}"
            )
        )
        contract_status = (
            "Complete for PR Readiness Stage 1 - Stage 2 PR creation remains pending USER approval."
            if pr_stage2_packet
            else
            "Complete - USER accepted the repaired branch-specific Workstream Entry contract for "
            "bounded Seam 1 implementation approval."
            if seam1_approval_packet
            else (
                "Complete for Live Validation LV1 - no-visible-runtime proof and UTS waiver "
                "evidence are green and this packet routes USER to approve or revise PR "
                "Readiness Stage 1 analysis."
            )
            if lv1_green_packet
            else (
                "Complete for Hardening H1 - proof comparison is green and this packet routes "
                "USER to approve or revise Live Validation LV1."
            )
            if hardening_h1_packet
            else (
                "Complete for Workstream - all admitted public-safe proof seams are implemented "
                "and this packet routes USER to approve or revise Hardening H1."
            )
            if workstream_green_packet
            else (
                "Complete for Seam 1 - action-gate registry proof is implemented and this packet "
                "routes USER to approve or revise Seam 2."
            )
            if seam1_completion_packet
            else (
                "Complete - branch-specific Workstream Entry contract repaired and ready for USER "
                "acceptance or waiver; Seam 1 implementation remains pending until USER sends the exact "
                "approval text."
            )
        )
        contract_version = (
            "v7 - FAM-007 Breakpoint 2 PR Readiness Stage 1 packet."
            if pr_stage2_packet
            else
            "v6 - FAM-007 Breakpoint 2 Live Validation LV1 packet."
            if lv1_green_packet
            else
            "v5 - FAM-007 Breakpoint 2 Hardening H1 packet."
            if hardening_h1_packet
            else
            "v4 - FAM-007 Breakpoint 2 Workstream Green packet."
            if workstream_green_packet
            else "v2 - FAM-007 Breakpoint 2 Workstream Entry contract repair."
        )
        what_user_sees = (
            "USER will inspect the active Breakpoint 2 branch plan, the branch record, the public-safe "
            "action-gate registry/proof path, validator or fixture expectations, the refreshed review "
            "packet, and the source-truth fold-down path. USER will not see private repositories, "
            "private roots, private remotes, backup/import execution, provider/model execution, runtime "
            "cache behavior, memory behavior, voice/Core sync, shortcut/installer work, PR creation, "
            "merge, release, cleanup, FAM-006 or Governance mutation, AI Product Contract import, "
            "Private Dev ORIN import, or v1.8.0 execution."
        )
        why_nexus = (
            "This fits Nexus because it turns Breakpoint 2 into a decision-ready, public-safe proof "
            "carrier before any private or runtime action occurs. It preserves the AI Runtime And Trust "
            "Architecture boundaries, keeps provider and memory behavior disabled, and makes each USER "
            "action gate explicit before Dev/Owner skeleton setup can begin."
        )
        design_ballot = [
            "Accept Seam 1 as recommended.",
            "Revise Seam 1 proof expectations before implementation.",
            "Waive unresolved review questions and approve Seam 1.",
            "Reject this branch contract and request a narrower carrier.",
        ]
        response_structure = [
            "Decision: accept, revise, waive, or reject.",
            "Required changes to Seam 1 proof expectations, if any.",
            "Must-have action-gate proof.",
            "Future-gated boundary controls.",
            "Explicit waiver language, if USER wants to waive unresolved questions.",
            "General response.",
        ]
        digest_structure = [
            "USER intent summary.",
            "Accepted or waived contract state.",
            "Approved Seam 1 scope.",
            "Rejected or deferred proof expectations.",
            "Implementation constraints created from USER response.",
            "Source-truth or packet updates required.",
            "Open questions.",
            "Next USER decision needed.",
        ]
        implementation_constraints = [
            (
                "USER accepted this contract for Seam 1; the approved work is limited to public-safe "
                "action-gate registry/proof, deterministic fixtures or validators, source-truth "
                "fold-down, packet refresh, and validation."
                if seam1_approval_packet
                else (
                    "Workstream is green; Hardening H1 remains blocked until USER approves or revises "
                    "the proof-comparison hardening seam."
                )
                if workstream_green_packet
                else (
                    "Seam 1 is complete; if the same-branch Workstream package remains in progress, "
                    "continuation must move to Seam 2 unless a real blocker, explicit waiver, or "
                    "backlog split is recorded."
                )
                if seam1_completion_packet
                else (
                    "Until USER accepts or waives this contract and approves bounded Workstream "
                    "implementation, the entry seam and later same-branch seams remain blocked."
                )
            ),
            "The Workstream entry seam is public-safe action-gate registry/proof, deterministic fixtures or validators, source-truth fold-down, packet refresh, and validation; later admitted same-branch seams continue under Workstream governance until Workstream Green, a real blocker, or an explicit USER waiver.",
            "No private Dev repo, private Owner repo, local-only private root, private remote, GitHub Desktop private remote, backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006 mutation, Governance mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is authorized by this packet.",
            "Provider-visible data must remain none; sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, memory/learning/personalization inactive, and runtime cache behavior not implemented.",
        ]
        rejected_deferred = [
            "Deferred: private Dev repo creation, private Owner repo creation, local-only private root creation, GitHub Desktop private remote configuration, off-boot backup or recovery root implementation, and Public-to-Dev import implementation.",
            "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, PR creation, merge, release, cleanup, FAM-006/Governance/sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0-prebeta execution.",
            "Rejected for the Workstream entry seam: any hidden private setup, silent provider enablement, cache/memory runtime behavior, or action that would make a USER gate look already completed.",
        ]
        source_truth_impact = [
            "Active external branch plan and branch record should preserve Breakpoint 2 as a real FAM-007 product/workstream carrier.",
            "AI Runtime And Trust Architecture remains the cross-family owner for provider boundaries, permission-state, deterministic routing, Trust Journal, AI Operational Cache Governance, local-only proof, and capability-pack readiness.",
            "Review packet should remain branch-specific, freshness-verified, count-consistent, placeholder-free, and explicit that Workstream approval covers the admitted same-branch package with Seam 1 as the entry proof checkpoint, not a one-seam stop.",
            "Source-truth fold-down during Seam 1 should record proof of action-gate preservation without executing gated private/runtime actions.",
        ]
        contract_change_log = [
            "v1 - Stage 2 review packet generated with generic USER Branch Plan Review language.",
            "v2 - Repaired into a branch-specific FAM-007 Breakpoint 2 engineering contract with Workstream Entry result, recommended Seam 1, proof expectations, pending gates, and exact approval text.",
        ]
        completion_checklist = [
            "Contract Status is Complete or Waived by USER.",
            "Workstream Entry Result records green analysis and recommended Seam 1.",
            "USER response is present in chat, copied into the packet later, or explicitly waived.",
            "Exact implementation approval text names bounded Workstream package execution with Seam 1 as the entry checkpoint.",
            "Implementation Constraints Created By USER Response preserve all private/runtime/provider/cache/memory gates.",
            "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
            "Packet digest files agree that Workstream Entry is green and Workstream approval covers the admitted same-branch package with Seam 1 as the entry proof checkpoint.",
            "No unresolved packet placeholders or packet count mismatches remain.",
            "Validation results are green before Seam 1 starts.",
        ]
        if seam1_completion_packet:
            design_ballot = [
                "Approve Seam 2 as recommended.",
                "Revise Seam 2 private-boundary proof expectations before implementation.",
                "Pause after Seam 1 and keep the branch open.",
                "Reject later seams and request a narrower closeout path.",
            ]
            response_structure = [
                "Decision: approve, revise, pause, or reject.",
                "Required changes to Seam 2 proof expectations, if any.",
                "Must-have private-boundary or remote-safety proof.",
                "Future-gated boundary controls.",
                "General response.",
            ]
            digest_structure = [
                "USER intent summary.",
                "Seam 1 completion acceptance or concerns.",
                "Approved or revised Seam 2 scope.",
                "Implementation constraints created from USER response.",
                "Next USER decision needed.",
            ]
            contract_change_log = [
                "v1 - Stage 2 review packet generated with generic USER Branch Plan Review language.",
                "v2 - Repaired into a branch-specific FAM-007 Breakpoint 2 engineering contract with Workstream Entry result, recommended Seam 1, proof expectations, pending gates, and exact approval text.",
                "v3 - Seam 1 action-gate registry and exact USER decision proof implemented with direct validator fixture proof.",
            ]
            completion_checklist = [
                "Seam 1 source-truth fold-down is present in the branch plan and branch record.",
                "Direct validator fixture proof covers the action-gate registry and exact USER decision proof.",
                "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
                "Packet digest files agree that Seam 1 is complete and Seam 2 remains pending USER approval.",
                "No unresolved packet placeholders or packet count mismatches remain.",
            ]
        plain_english_summary = (
            "This FAM-007 branch prepares Breakpoint 2 for a future Dev/Owner skeleton setup decision. "
            "Its job is not to create private repos or turn on AI runtime behavior; its job is to make "
            "the exact action gates, proof files, validation expectations, and USER decisions clear "
            "enough that the next implementation seam can safely prove readiness."
        )
        end_state_vision = (
            "When this readiness work is complete, USER should have a public-safe proof package showing "
            "which Dev/Owner skeleton actions remain blocked, which exact approvals would unlock them, "
            "which validators prove the gates stayed closed, and how the branch can hand off to the "
            "future private setup decision without ambiguity."
        )
        walkthrough = [
            "Open START_HERE.md first and review the plain-language file map and USER decision.",
            "Open USER_BRANCH_PLAN_REVIEW.md and review this contract, especially Seam 1, action-gate proof expectations, and pending gates.",
            "Open the active external branch plan to verify the product/workstream carrier posture and Breakpoint 2 scope.",
            "Inspect the action-gate registry/proof surface once Seam 1 is implemented; each gated action should say pending, blocked, or USER-required rather than completed.",
            "Review validator or fixture outputs proving no private repo, private root, private remote, backup/import behavior, provider/model/runtime/cache/memory behavior, or PR/merge/release work occurred.",
            "Upload the matching timestamped ZIP beside the local USER hub folder after reviewing the packet.",
        ]
        surface_map = [
            "USER review packet: START_HERE.md, USER_BRANCH_VISION_REVIEW.md, USER_BRANCH_PLAN_REVIEW.md, folder/file digest, governance scan, Workstream Entry digest, branch vision checklist, and ZIP export.",
            "Active external branch plan: C:\\Nexus Governance State\\branches\\feature_fam_007_breakpoint_2_dev_owner_skeleton_action_gate_readiness\\branch_plan.md.",
            "Branch record: Docs/branch_records/feature_fam_007_breakpoint_2_dev_owner_skeleton_action_gate_readiness.md.",
            "Architecture owner: Docs/ai_runtime_and_trust_architecture.md.",
            "FAM-007 owners: Docs/family_visions/FAM-007_local_ai_and_capability_packs.md and Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md.",
            "Validation surfaces: dev/orin_user_review_bundle.py, dev/orin_public_leak_prevention_validation.py, dev/orin_branch_readiness_planning_fixture_validation.py, dev/orin_branch_governance_validation.py, and Docs/validation_helper_registry.md.",
            "External operational state: records branch authority and packet posture outside the repo when current governance requires it.",
        ]
        implementation_options = [
            "Approve the bounded Workstream package with Seam 1 as the entry checkpoint: implement public-safe action-gate registry and exact USER decision proof first, then continue through admitted same-branch seams until Workstream Green, a real blocker, or an explicit USER waiver. Pros: clearest readiness foundation; Cons: no private setup yet; Risk: low.",
            "Revise Workstream proof expectations before implementation. Pros: lets USER tune proof wording, validator expectations, or seam order; Cons: adds packet/source-truth repair; Risk: low.",
            "Waive unresolved review questions and approve bounded Workstream package execution. Pros: unblocks bounded proof work; Cons: records less design feedback; Risk: medium if important proof expectations are not named.",
            "Reject this branch contract and request a narrower carrier. Pros: maximum scope control; Cons: delays Breakpoint 2 readiness; Risk: low but slower.",
        ]
        recommended_direction = (
            "Codex recommends accepting the repaired branch contract and approving bounded Workstream "
            "package execution when USER agrees that the public-safe proof path is correct. Seam 1 is "
            "the entry checkpoint for action-gate and decision-text proof; it is not stop authority "
            "while admitted same-branch Workstream work remains."
        )
        current_scope = [
            "Branch-specific Workstream Entry contract repair.",
            "Completed Workstream Entry result recorded in the packet.",
            "Recommended first seam recorded as Seam 1, Action-gate registry and exact USER decision proof.",
            "Local USER hub packet and timestamped ZIP refreshed; helper output carries technical freshness proof and USER-facing files carry the decision path.",
            "Validation before any Seam 1 file mutation begins.",
        ]
        future_scope = [
            "Seam 1 approval is limited to public-safe action-gate registry and exact USER decision proof.",
            "Private Dev/Owner repo creation, local-only private roots, private remotes, backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain future-gated.",
        ]
        slc_package_plan = [
            "Seam 1: action-gate registry and exact USER decision proof.",
            "Later seams may add private-boundary readiness, local-only/private-root readiness, private remote safety, public-to-private separation, and provider/model/runtime/cache/memory deferral proof only after USER approves them.",
            "No seam may execute the private/runtime action it is proving as gated.",
        ]
        if workstream_green_packet:
            walkthrough = [
                "Open START_HERE.md first and review the plain-language file map and USER decision.",
                "Open USER_BRANCH_PLAN_REVIEW.md and confirm the contract is Workstream Green with Hardening H1 as the next decision.",
                "Open the active external branch plan and branch record to verify Seams 1 through 4 are recorded as public-safe proof only.",
                "Review the fixture and validator proof showing all private/runtime/provider/cache/memory gates remain pending.",
                "Upload the matching timestamped ZIP beside the local USER hub folder after reviewing or revising Hardening H1.",
            ]
            implementation_options = [
                "Approve Hardening H1 as recommended: compare all public-safe Workstream proof against source truth, fixtures, validators, packet proof, and external-state boundaries. Pros: moves the branch into the required proof-comparison phase; Cons: no PR/merge/release yet; Risk: low.",
                "Revise Hardening H1 proof expectations before implementation. Pros: lets USER tune pressure-test criteria; Cons: adds packet/source-truth repair; Risk: low.",
                "Pause at Workstream Green and keep the branch open. Pros: preserves the green Workstream proof without expanding scope; Cons: delays closeout; Risk: low.",
                "Reject Hardening and request a narrower Workstream closeout repair. Pros: maximum scope control; Cons: may leave proof comparison incomplete; Risk: low but slower.",
            ]
            design_ballot = [
                "Approve Hardening H1 as recommended.",
                "Revise Hardening H1 proof expectations before implementation.",
                "Pause at Workstream Green.",
                "Reject and request a narrower closeout repair.",
            ]
            response_structure = [
                "Decision: approve, revise, pause, or reject.",
                "Required changes to Hardening H1 proof expectations, if any.",
                "Must-have proof-comparison or pressure-test criteria.",
                "Future-gated boundary controls.",
                "General response.",
            ]
            digest_structure = [
                "USER intent summary.",
                "Workstream Green acceptance or concerns.",
                "Approved or revised Hardening H1 scope.",
                "Implementation constraints created from USER response.",
                "Next USER decision needed.",
            ]
            contract_change_log = [
                "v1 - Stage 2 review packet generated with generic USER Branch Plan Review language.",
                "v2 - Repaired into a branch-specific FAM-007 Breakpoint 2 engineering contract with Workstream Entry result, recommended Seam 1, proof expectations, pending gates, and exact approval text.",
                "v3 - Seam 1 action-gate registry and exact USER decision proof implemented with direct validator fixture proof.",
                "v4 - Seams 2 through 4 implemented as public-safe proof and Workstream Green candidate recorded.",
            ]
            completion_checklist = [
                "Seams 1 through 4 source-truth fold-down is present in the branch plan and branch record.",
                "Direct validator fixture proof covers action gates, private/public boundary, backup/import planning gates, provider/runtime/cache/memory deferral, and Hardening handoff readiness.",
                "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
                "Packet digest files agree that Workstream is green and Hardening H1 remains pending USER approval.",
                "No unresolved packet placeholders or packet count mismatches remain.",
            ]
            recommended_direction = (
                "Codex recommends approving Hardening H1 only if USER agrees the next proof should "
                "pressure-test the completed public-safe Workstream proof without executing private, "
                "runtime, provider, cache, memory, PR, merge, release, cleanup, or v1.8.0 actions."
            )
            current_scope = [
                "Seam 1 action-gate registry proof implemented.",
                "Seam 2 private/public boundary and private remote safety proof implemented.",
                "Seam 3 backup/recovery and Public-to-Dev import planning proof implemented.",
                "Seam 4 provider/model/runtime/cache/memory deferral and local-only handoff proof implemented.",
                "Local USER hub packet and timestamped ZIP refreshed; helper output carries technical freshness proof and USER-facing files carry the Hardening H1 next decision.",
            ]
            future_scope = [
                "Hardening H1 approval is limited to proof comparison and pressure testing.",
                "Private Dev/Owner repo creation, local-only private roots, private remotes, backup/import execution, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain future-gated.",
            ]
            slc_package_plan = [
                "Seams 1 through 4 complete as public-safe proof.",
                "Hardening H1 next: compare all proof against source truth, fixtures, validators, packet proof, and external-state boundaries.",
                "No hardening step may execute the private/runtime action it is pressure-testing as gated.",
            ]
            implementation_constraints = [
                "Workstream is green; Hardening H1 remains blocked until USER approves or revises the proof-comparison hardening seam.",
                "Hardening H1 is limited to comparison, pressure testing, validation, and H1-scoped source-truth/validator/packet repairs if required.",
                "No private Dev repo, private Owner repo, local-only private root, private remote, GitHub Desktop private remote, backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006 mutation, Governance mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is authorized by this packet.",
                "Provider-visible data must remain none; sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, memory/learning/personalization inactive, and runtime cache behavior not implemented.",
            ]
            rejected_deferred = [
                "Deferred: private Dev repo creation, private Owner repo creation, local-only private root creation, GitHub Desktop private remote configuration, off-boot backup or recovery root implementation, and Public-to-Dev import implementation.",
                "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, PR creation, merge, release, cleanup, FAM-006/Governance/sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0-prebeta execution.",
                "Rejected for Hardening H1: executing the private/runtime action being pressure-tested as gated, silently enabling provider/cache/memory behavior, or turning proof comparison into PR/merge/release work.",
            ]
            source_truth_impact = [
                "Active external branch plan and branch record preserve Breakpoint 2 as a real FAM-007 product/workstream carrier.",
                "AI Runtime And Trust Architecture remains the cross-family owner for provider boundaries, permission-state, deterministic routing, Trust Journal, AI Operational Cache Governance, local-only proof, and capability-pack readiness.",
                "Review packet remains branch-specific, freshness-verified, count-consistent, placeholder-free, and explicit that Hardening H1 approval covers only proof comparison and H1-scoped repair.",
                "Source-truth fold-down records Seams 1 through 4 as public-safe proof without executing gated private/runtime actions.",
            ]
        if hardening_h1_packet:
            walkthrough = [
                "Open START_HERE.md first and review the plain-language file map and USER decision.",
                "Open USER_BRANCH_PLAN_REVIEW.md and confirm the contract is Hardening H1 Green with Live Validation LV1 as the next decision.",
                "Open the active external branch plan and branch record to verify the H1 comparison receipt and stale-ledger repair.",
                "Review validator proof showing stale Workstream-pending phrases are rejected and all private/runtime/provider/cache/memory gates remain pending.",
                "Upload the matching timestamped ZIP beside the local USER hub folder after reviewing or revising LV1/no-visible-runtime proof.",
            ]
            implementation_options = [
                "Approve Live Validation LV1 as recommended: digest no-visible-runtime proof and UTS waiver evidence from source-truth, fixtures, validators, packet proof, and external-state boundaries. Pros: moves the branch toward PR Readiness without pretending runtime was exercised; Cons: no PR/merge/release yet; Risk: low.",
                "Revise LV1 proof expectations before validation. Pros: lets USER tune waiver/evidence criteria; Cons: adds packet/source-truth repair; Risk: low.",
                "Pause at Hardening H1 Green and keep the branch open. Pros: preserves the H1 proof without expanding scope; Cons: delays closeout; Risk: low.",
                "Reject LV1 and request a narrower H1 closeout repair. Pros: maximum scope control; Cons: may leave Live Validation evidence incomplete; Risk: low but slower.",
            ]
            design_ballot = [
                "Approve Live Validation LV1 as recommended.",
                "Revise LV1/no-visible-runtime proof expectations before validation.",
                "Pause at Hardening H1 Green.",
                "Reject and request a narrower closeout repair.",
            ]
            response_structure = [
                "Decision: approve, revise, pause, or reject.",
                "Required changes to LV1/no-visible-runtime proof expectations, if any.",
                "Must-have waiver or validation evidence.",
                "Future-gated boundary controls.",
                "General response.",
            ]
            digest_structure = [
                "USER intent summary.",
                "Hardening H1 acceptance or concerns.",
                "Approved or revised LV1/no-visible-runtime scope.",
                "Implementation constraints created from USER response.",
                "Next USER decision needed.",
            ]
            contract_change_log = [
                "v1 - Stage 2 review packet generated with generic USER Branch Plan Review language.",
                "v2 - Repaired into a branch-specific FAM-007 Breakpoint 2 engineering contract with Workstream Entry result, recommended Seam 1, proof expectations, pending gates, and exact approval text.",
                "v3 - Seam 1 action-gate registry and exact USER decision proof implemented with direct validator fixture proof.",
                "v4 - Seams 2 through 4 implemented as public-safe proof and Workstream Green candidate recorded.",
                "v5 - Hardening H1 compared proof, repaired stale ledger wording, and routed the packet to Live Validation LV1.",
            ]
            completion_checklist = [
                "Hardening H1 comparison receipt is present in the branch plan and branch record.",
                "Direct validator proof rejects stale Workstream-pending ledger phrases.",
                "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
                "Packet digest files agree that Hardening H1 is green and Live Validation LV1 remains pending USER approval.",
                "No unresolved packet placeholders or packet count mismatches remain.",
            ]
            recommended_direction = (
                "Codex recommends approving bounded Live Validation LV1 only if USER agrees the next proof "
                "should digest no-visible-runtime and UTS waiver evidence without executing private, runtime, "
                "provider, cache, memory, PR, merge, release, cleanup, or v1.8.0 actions."
            )
            current_scope = [
                "Hardening H1 proof comparison complete.",
                "Stale duplicate Workstream-pending ledger wording repaired.",
                "Direct validator guard added for stale Breakpoint 2 Workstream-pending phrases.",
                "Local USER hub packet and timestamped ZIP refreshed; helper output carries technical freshness proof and USER-facing files carry the Live Validation LV1 next decision.",
            ]
            future_scope = [
                "Live Validation LV1 approval is limited to no-visible-runtime proof and UTS waiver digestion.",
                "Private Dev/Owner repo creation, local-only private roots, private remotes, backup/import execution, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain future-gated.",
            ]
            slc_package_plan = [
                "Hardening H1 complete as public-safe proof comparison.",
                "Live Validation LV1 next: digest no-visible-runtime proof and UTS waiver evidence.",
                "No LV1 step may execute the private/runtime action it is proving absent.",
            ]
            implementation_constraints = [
                "Hardening H1 is green; Live Validation LV1 remains blocked until USER approves or revises the no-visible-runtime proof seam.",
                "LV1 is limited to no-visible-runtime proof, UTS waiver digestion, validation, and LV1-scoped source-truth/validator/packet repairs if required.",
                "No private Dev repo, private Owner repo, local-only private root, private remote, GitHub Desktop private remote, backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006 mutation, Governance mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is authorized by this packet.",
                "Provider-visible data must remain none; sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, memory/learning/personalization inactive, and runtime cache behavior not implemented.",
            ]
            rejected_deferred = [
                "Deferred: private Dev repo creation, private Owner repo creation, local-only private root creation, GitHub Desktop private remote configuration, off-boot backup or recovery root implementation, and Public-to-Dev import implementation.",
                "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, PR creation, merge, release, cleanup, FAM-006/Governance/sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0-prebeta execution.",
                "Rejected for LV1: executing runtime/private/provider/cache/memory behavior just to prove it did not change.",
            ]
            source_truth_impact = [
                "Active external branch plan and branch record preserve Breakpoint 2 as a real FAM-007 product/workstream carrier.",
                "AI Runtime And Trust Architecture remains the cross-family owner for provider boundaries, permission-state, deterministic routing, Trust Journal, AI Operational Cache Governance, local-only proof, and capability-pack readiness.",
                "Review packet remains branch-specific, freshness-verified, count-consistent, placeholder-free, and explicit that LV1 approval covers only no-visible-runtime proof and UTS waiver digestion.",
                "Source-truth fold-down records H1 Green without executing gated private/runtime actions.",
            ]
        if lv1_green_packet:
            walkthrough = [
                "Open START_HERE.md first and review the plain-language file map and USER decision.",
                "Open USER_BRANCH_PLAN_REVIEW.md and confirm the contract is Live Validation LV1 Green with PR Readiness Stage 1 as the next decision.",
                "Open the active external branch plan and branch record to verify the LV1/no-visible-runtime proof receipt and UTS waiver.",
                "Review validator proof showing LV1 source-truth phrases are present and stale H1/LV1-pending phrases are rejected.",
                "Upload the matching timestamped ZIP beside the local USER hub folder after reviewing or revising PR Readiness Stage 1 analysis.",
            ]
            implementation_options = [
                "Approve PR Readiness Stage 1 as recommended: analyze PR readiness for the completed public-safe Breakpoint 2 proof carrier. Pros: moves toward PR creation review; Cons: no PR/merge/release yet; Risk: low.",
                "Revise PR Readiness Stage 1 inspection criteria before analysis. Pros: lets USER tune PR readiness proof; Cons: adds packet/source-truth repair; Risk: low.",
                "Pause at Live Validation LV1 Green and keep the branch open. Pros: preserves the LV1 proof without expanding scope; Cons: delays PR readiness; Risk: low.",
                "Reject PR Readiness and request a narrower LV1 closeout repair. Pros: maximum scope control; Cons: may leave PR path incomplete; Risk: low but slower.",
            ]
            design_ballot = [
                "Approve PR Readiness Stage 1 as recommended.",
                "Revise PR Readiness Stage 1 inspection criteria before analysis.",
                "Pause at Live Validation LV1 Green.",
                "Reject and request a narrower closeout repair.",
            ]
            response_structure = [
                "Decision: approve, revise, pause, or reject.",
                "Required changes to PR Readiness Stage 1 inspection criteria, if any.",
                "Must-have PR readiness proof.",
                "Future-gated boundary controls.",
                "General response.",
            ]
            digest_structure = [
                "USER intent summary.",
                "LV1 Green acceptance or concerns.",
                "Approved or revised PR Readiness Stage 1 scope.",
                "Implementation constraints created from USER response.",
                "Next USER decision needed.",
            ]
            contract_change_log = [
                "v1 - Stage 2 review packet generated with generic USER Branch Plan Review language.",
                "v2 - Repaired into a branch-specific FAM-007 Breakpoint 2 engineering contract with Workstream Entry result, recommended Seam 1, proof expectations, pending gates, and exact approval text.",
                "v3 - Seam 1 action-gate registry and exact USER decision proof implemented with direct validator fixture proof.",
                "v4 - Seams 2 through 4 implemented as public-safe proof and Workstream Green candidate recorded.",
                "v5 - Hardening H1 compared proof, repaired stale ledger wording, and routed the packet to Live Validation LV1.",
                "v6 - Live Validation LV1 recorded no-visible-runtime proof, UTS waiver, and PR Readiness Stage 1 as the next gate.",
            ]
            completion_checklist = [
                "Live Validation LV1 receipt is present in the branch plan and branch record.",
                "Direct validator proof requires LV1 no-visible-runtime, UTS waiver, and PR Readiness Stage 1 routing phrases.",
                "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
                "Packet digest files agree that Live Validation LV1 is green and PR Readiness Stage 1 remains pending USER approval.",
                "No unresolved packet placeholders or packet count mismatches remain.",
            ]
            recommended_direction = (
                "Codex recommends approving bounded PR Readiness Stage 1 only if USER agrees the next "
                "step should analyze readiness without creating a PR, merging, releasing, cleaning up, "
                "or executing any private/runtime/provider/cache/memory action."
            )
            current_scope = [
                "Workstream Seams 1 through 4 complete as public-safe proof.",
                "Hardening H1 proof comparison complete.",
                "Live Validation LV1 no-visible-runtime proof complete.",
                "UTS and user-facing shortcut validation waived because no visible runtime or shortcut surface changed.",
                "Local USER hub packet and timestamped ZIP refreshed; helper output carries technical freshness proof and USER-facing files carry the PR Readiness Stage 1 next decision.",
            ]
            future_scope = [
                "PR Readiness Stage 1 approval is limited to analysis only.",
                "PR creation, merge, release, cleanup, private Dev/Owner repo creation, private roots/remotes, backup/import execution, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain future-gated.",
            ]
            slc_package_plan = [
                "Workstream, H1, and LV1 are complete as public-safe proof.",
                "PR Readiness Stage 1 next: inspect source-truth fold-down, packet proof, external-state posture, no-release-debt posture, and PR-readiness review expectations.",
                "No PR Readiness Stage 1 step may create a PR, merge, release, clean up, or execute private/runtime actions.",
            ]
            implementation_constraints = [
                "Live Validation LV1 is green; PR Readiness Stage 1 remains blocked until USER approves or revises the analysis scope.",
                "PR Readiness Stage 1 is limited to analysis, validation review, source-truth inspection, packet proof, and decision packet generation.",
                "No private Dev repo, private Owner repo, local-only private root, private remote, GitHub Desktop private remote, backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR creation, merge, release, cleanup, FAM-006 mutation, Governance mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is authorized by this packet.",
                "Provider-visible data must remain none; sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, memory/learning/personalization inactive, and runtime cache behavior not implemented.",
            ]
            rejected_deferred = [
                "Deferred: PR creation, merge, release, branch/worktree cleanup, and release artifact execution.",
                "Deferred: private Dev repo creation, private Owner repo creation, local-only private root creation, GitHub Desktop private remote configuration, off-boot backup or recovery root implementation, and Public-to-Dev import implementation.",
                "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, FAM-006/Governance/sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0-prebeta execution.",
            ]
            source_truth_impact = [
                "Active external branch plan and branch record preserve Breakpoint 2 as a real FAM-007 product/workstream carrier completed through LV1.",
                "AI Runtime And Trust Architecture remains the cross-family owner for provider boundaries, permission-state, deterministic routing, Trust Journal, AI Operational Cache Governance, local-only proof, and capability-pack readiness.",
                "Review packet remains branch-specific, placeholder-free, decision-path-consistent, and explicit that PR Readiness Stage 1 approval covers analysis only.",
                "Source-truth fold-down records LV1 Green without executing gated private/runtime actions.",
            ]
        elif seam1_completion_packet:
            implementation_options = [
                "Approve Seam 2 as recommended: implement public-safe private/public boundary and private remote safety proof. Pros: continues the same gated readiness path; Cons: still no private setup; Risk: low.",
                "Revise Seam 2 proof expectations before implementation. Pros: lets USER tune boundary or remote-safety evidence; Cons: adds packet/source-truth repair; Risk: low.",
                "Pause after Seam 1 and keep the branch open. Pros: preserves the green Seam 1 proof without expanding scope; Cons: delays Breakpoint 2 readiness; Risk: low.",
                "Reject later seams and request a narrower closeout path. Pros: maximum scope control; Cons: may leave Breakpoint 2 readiness incomplete; Risk: low but slower.",
            ]
            recommended_direction = (
                "Codex recommends approving Seam 2 only if USER agrees the next proof should focus "
                "on private/public boundary and private remote safety without configuring private "
                "remotes or creating private roots."
            )
            current_scope = [
                "Seam 1 action-gate registry proof implemented.",
                "Exact USER decision proof implemented.",
                "Direct fixture and validator proof added.",
                "Branch plan and branch record folded down for Seam 1.",
                "Local USER hub packet and timestamped ZIP refreshed with the current decision path, file list, and next decision.",
            ]
            future_scope = [
                "Seam 2 approval is limited to private/public boundary and private remote safety proof.",
                "Private Dev/Owner repo creation, local-only private roots, private remotes, backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain future-gated.",
            ]
            slc_package_plan = [
                "Seam 1 complete: action-gate registry and exact USER decision proof.",
                "Seam 2 next candidate: private/public boundary and private remote safety proof.",
                "No seam may execute the private/runtime action it is proving as gated.",
            ]
        if pr_stage2_packet:
            plain_english_summary = (
                "This FAM-007 packet records that the Breakpoint 2 public-safe proof carrier has "
                "completed Workstream, H1, LV1, and PR Readiness Stage 1 repair. It does not create "
                "a PR by itself; it asks USER whether Stage 2 may create the PR and establish the "
                "required watcher/review path."
            )
            end_state_vision = (
                "After Stage 2 approval, the branch can be opened as a PR to main with the completed "
                "public-safe action-gate proof, while merge, release, cleanup, private setup, provider/"
                "model/runtime/cache/memory behavior, and v1.8.0 work remain separately gated."
            )
            what_user_sees = (
                "USER will inspect the refreshed Stage 1 packet, branch plan, branch record, no-live-PR "
                "posture, no-release-debt posture, merge-stable authority projection, and exact Stage 2 "
                "PR creation approval text. USER will not see private repositories, private roots, "
                "private remotes, backup/import execution, provider/model execution, runtime cache "
                "behavior, memory behavior, voice/Core sync, shortcut/installer work, merge, release, "
                "cleanup, FAM-006 or Governance mutation, AI Product Contract import, Private Dev ORIN "
                "import, or v1.8.0 execution."
            )
            walkthrough = [
                "Open START_HERE.md first and review the plain-language file map and Stage 2 PR creation decision.",
                "Open USER_BRANCH_PLAN_REVIEW.md and confirm the contract is PR Readiness Stage 1 Ready For Stage 2.",
                "Open the branch record PR Readiness Stage 1 Analysis Packet and verify no live PR, Stage 2 pending, no-release-debt posture, selected-next default/defer posture, and merge-stable authority projection.",
                "Open the branch plan PR Readiness Stage 1 Repair Receipt and confirm Stage 2 remains blocked until USER approval.",
                "Upload the matching timestamped ZIP beside the local USER hub folder after reviewing or revising Stage 2.",
            ]
            implementation_options = [
                "Approve PR Readiness Stage 2 as recommended: create the PR, verify PR creation and review posture, provision/update watcher, request/monitor Codex bot review, and stop before merge unless later approval exists. Pros: moves the completed proof carrier into review; Cons: no merge/release yet; Risk: low when validation remains green.",
                "Revise Stage 2 PR creation expectations before PR creation. Pros: lets USER tune PR body, watcher, or bot-review requirements; Cons: adds packet/source-truth repair; Risk: low.",
                "Pause at Stage 1 Ready For Stage 2. Pros: preserves clean proof without creating a PR; Cons: delays review; Risk: low.",
                "Reject PR creation and request a narrower closeout. Pros: maximum scope control; Cons: delays branch completion; Risk: low but slower.",
            ]
            design_ballot = [
                "Approve PR Readiness Stage 2 as recommended.",
                "Revise Stage 2 PR creation expectations.",
                "Pause at Stage 1 Ready For Stage 2.",
                "Reject and request a narrower closeout.",
            ]
            response_structure = [
                "Decision: approve, revise, pause, or reject.",
                "Required changes to PR body, watcher, or bot-review expectations, if any.",
                "Must-have PR readiness proof.",
                "Future-gated boundary controls.",
                "General response.",
            ]
            digest_structure = [
                "USER intent summary.",
                "Stage 1 readiness acceptance or concerns.",
                "Approved or revised Stage 2 PR creation scope.",
                "Implementation constraints created from USER response.",
                "Next USER decision needed.",
            ]
            recommended_direction = (
                "Codex recommends approving PR Readiness Stage 2 only if USER agrees the completed "
                "public-safe proof carrier should enter PR review now. Stage 2 may create and watch the "
                "PR, but merge, release, cleanup, private setup, provider/model/runtime/cache/memory "
                "behavior, and v1.8.0 work stay blocked."
            )
            current_scope = [
                "Workstream Seams 1 through 4 complete as public-safe proof.",
                "Hardening H1 proof comparison complete.",
                "Live Validation LV1 no-visible-runtime proof complete.",
                "PR Readiness Stage 1 repair complete with no live PR and Stage 2 pending.",
                "Local USER hub packet and timestamped ZIP refreshed; helper output carries technical freshness proof and USER-facing files carry the Stage 2 next decision.",
            ]
            future_scope = [
                "PR Readiness Stage 2 approval is limited to PR creation, live PR validation, watcher provisioning/update, Codex bot review request/monitoring, and in-scope Codex comment repair if needed.",
                "Merge, release, cleanup, private Dev/Owner repo creation, private roots/remotes, backup/import execution, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain future-gated.",
            ]
            slc_package_plan = [
                "Workstream, H1, LV1, and PR Readiness Stage 1 repair are complete as public-safe proof.",
                "PR Readiness Stage 2 next: verify no live PR or bind to one if it appears, rerun validation, create PR, provision/update watcher, request/monitor Codex bot review, and stop before merge absent later approval.",
                "No Stage 2 step may merge, release, clean up, or execute private/runtime actions.",
            ]
            implementation_constraints = [
                "PR Readiness Stage 1 is green; Stage 2 PR creation remains blocked until USER approves or revises the PR creation scope.",
                "Stage 2 is limited to PR creation, live PR validation, watcher provisioning/update, Codex bot review request/monitoring, in-scope Codex comment repair if needed, packet/source-truth repair if required, and validation.",
                "No private Dev repo, private Owner repo, local-only private root, private remote, GitHub Desktop private remote, backup/import behavior, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, merge, release, cleanup, FAM-006 mutation, Governance mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is authorized by this packet.",
                "Provider-visible data must remain none; sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, memory/learning/personalization inactive, and runtime cache behavior not implemented.",
            ]
            rejected_deferred = [
                "Deferred: merge, release, branch/worktree cleanup, and release artifact execution.",
                "Deferred: private Dev repo creation, private Owner repo creation, local-only private root creation, GitHub Desktop private remote configuration, off-boot backup or recovery root implementation, and Public-to-Dev import implementation.",
                "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, FAM-006/Governance/sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0-prebeta execution.",
            ]
            source_truth_impact = [
                "Branch plan and branch record preserve Breakpoint 2 as a completed FAM-007 product/workstream proof carrier ready for PR creation approval.",
                "Branch record index projects no active non-standing branch authority on merged main; live operational state comes from Git, GitHub, helpers, and external state.",
                "Review packet remains branch-specific, placeholder-free, decision-path-consistent, and explicit that Stage 2 approval covers PR creation only.",
                "Source-truth fold-down records PR Readiness Stage 1 without executing gated private/runtime actions.",
            ]
            contract_change_log = [
                "v1 - Stage 2 review packet generated with generic USER Branch Plan Review language.",
                "v2 - Repaired into a branch-specific FAM-007 Breakpoint 2 engineering contract with Workstream Entry result, recommended Seam 1, proof expectations, pending gates, and exact approval text.",
                "v3 - Seam 1 action-gate registry and exact USER decision proof implemented with direct validator fixture proof.",
                "v4 - Seams 2 through 4 implemented as public-safe proof and Workstream Green candidate recorded.",
                "v5 - Hardening H1 compared proof, repaired stale ledger wording, and routed the packet to Live Validation LV1.",
                "v6 - Live Validation LV1 recorded no-visible-runtime proof, UTS waiver, and PR Readiness Stage 1 as the next gate.",
                "v7 - PR Readiness Stage 1 repair recorded no live PR, pending Stage 2 approval, no-release-debt posture, selected-next default/defer posture, and merge-stable authority projection.",
            ]
            completion_checklist = [
                "PR Readiness Stage 1 Analysis Packet is present in the branch record.",
                "PR Readiness Stage 1 Repair Receipt is present in the branch plan.",
                "Branch record index projects this branch as historical and keeps only standing Governance active authority.",
                "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
                "Packet digest files agree that Stage 1 is ready for Stage 2 and PR creation remains pending USER approval.",
                "No unresolved packet placeholders or packet count mismatches remain.",
            ]
        user_decisions = [
            "Does USER accept or explicitly waive this repaired USER Branch Plan Review contract?",
            "Does USER approve Seam 1 implementation only: action-gate registry and exact USER decision proof?",
            "Does USER require any change to direct proof expectations before Seam 1 begins?",
            "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
        ]
        if pr_stage2_packet:
            user_decisions = [
                "Does USER approve PR Readiness Stage 2 PR creation?",
                "Does USER require any change to PR body, watcher, or Codex bot-review expectations before Stage 2 begins?",
                "Does USER confirm merge, release, cleanup, and all private/runtime/provider/cache/memory gates remain pending?",
            ]
        elif hardening_h1_packet:
            user_decisions = [
                "Does USER approve bounded Live Validation LV1/no-visible-runtime proof?",
                "Does USER require any change to LV1 waiver or evidence expectations before it begins?",
                "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
            ]
        elif lv1_green_packet:
            user_decisions = [
                "Does USER approve bounded PR Readiness Stage 1 analysis?",
                "Does USER require any change to PR Readiness Stage 1 inspection criteria before it begins?",
                "Does USER confirm PR creation, merge, release, cleanup, and all private/runtime/provider/cache/memory gates remain pending?",
            ]
        elif workstream_green_packet:
            user_decisions = [
                "Does USER approve bounded Hardening H1 proof comparison?",
                "Does USER require any change to Hardening H1 pressure-test expectations before it begins?",
                "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
            ]
        elif seam1_completion_packet:
            user_decisions = [
                "Does USER approve Seam 2 implementation only: private/public boundary and private remote safety proof?",
                "Does USER require any change to direct proof expectations before Seam 2 begins?",
                "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
            ]
    else:
        accepted_user_response = None
        codex_response_digest = None
        workstream_entry_result = None
        contract_status = (
            "Complete - BP2 engineering plan context is recorded for this PR Readiness Stage 1 packet; "
            "this packet does not request Workstream implementation approval."
            if pr_readiness_stage1_packet
            else "Pending USER Response - USER must accept, revise, reject, request more options, or waive this BP2 engineering plan before implementation."
        )
        contract_version = "v2 - Generated BP2 Branch Plan Review."
        what_user_sees = (
            "USER sees a local USER hub review packet containing the governance lifecycle context plan, "
            "phase law, branch artifact rules, helper/validator ownership, branch authority routing, and "
            "supporting source-truth files needed before PR Readiness Stage 1."
            if pr_readiness_stage1_packet
            else "USER should see the planned implementation surfaces, affected files, validators, proof requirements, and future-gated boundaries before implementation begins."
        )
        why_nexus = (
            "This keeps Branch Vision, Branch Plan, Workstream, Hardening, Live Validation, PR Readiness, "
            "and Release Readiness in separate governance layers while keeping USER review artifacts readable."
            if pr_readiness_stage1_packet
            else "The recommendation should explain how the branch builds the accepted Branch Vision, keeps scope bounded, and preserves user-facing clarity."
        )
        design_ballot = [
            "Accept the BP2 engineering plan as written.",
            "Accept with engineering-plan changes.",
            "Route back to BP1 because the plan changes the accepted Branch Vision.",
            "Explicitly waive remaining BP2 questions.",
            "Reject and request a narrower branch or plan.",
            "Pause / unclear.",
        ]
        response_structure = [
            "Decision.",
            "Required changes.",
            "Must-have behavior.",
            "Future-gated boundary controls.",
            "Future-gated ideas.",
            "General response.",
        ]
        digest_structure = [
            "USER intent summary.",
            "Accepted USER decisions.",
            "Rejected or deferred USER ideas.",
            "Implementation constraints created from USER response.",
            "Source-truth updates required.",
            "Review packet updates required.",
            "Open questions.",
            "Contract Status after digest.",
            "Next USER decision needed.",
        ]
        implementation_constraints = (
            [
                "PR Readiness Stage 1 is analysis-only.",
                "PR creation, merge, release, cleanup, runtime implementation, provider/model/cache/memory/private actions, sidecar artifacts, and separate Review/Upload taxonomy remain pending USER decisions; timestamped ZIP naming is mandatory active policy.",
                "Accepted outcomes from this packet must fold into durable repo owners or approved external operational state, not the temporary USER review folder.",
            ]
            if pr_readiness_stage1_packet
            else ["Pending USER response or explicit waiver."]
        )
        rejected_deferred = (
            [
                "Sidecar artifact model remains pending USER decision.",
                "Uniquely named ZIP artifact model remains pending USER decision.",
                "Separate Review / Upload top-level folder taxonomy remains pending USER decision.",
                "Cloud-backed mirrors remain convenience-only unless USER changes the artifact model.",
            ]
            if pr_readiness_stage1_packet
            else ["Pending USER response or explicit waiver."]
        )
        source_truth_impact = (
            [
                "Lifecycle law remains owned by Docs/phase_governance.md.",
                "Branch artifact rules remain owned by Docs/branch_plans/README.md.",
                "USER hub helper enforcement remains owned by Docs/validation_helper_registry.md.",
                "Active operational proof remains in Codex chat digest, helper output, validator output, or external governance state.",
            ]
            if pr_readiness_stage1_packet
            else ["Pending USER response or explicit waiver."]
        )
        contract_change_log = ["v2 - Generated as BP2 engineering-plan review rather than BP1 product/design contract."]
        completion_checklist = [
            "Contract Status is Complete or Waived by USER.",
            "Accepted or waived BP1 trace is present or this packet is a later-phase context review.",
            "Implementation package summary, seam/SLC plan, affected surfaces, validators/helpers, proof requirements, H1/LV/UTS expectations, rollback/safety plan, risks, and future-gated boundaries are represented.",
            "Helper output verifies packet freshness while USER-facing files stay focused on context, plan, risks, proof expectations, and decisions.",
            "BP3 / Workstream Entry may approve implementation only when BP1 and BP2 are accepted or explicitly waived.",
            "PR Readiness Stage 1 approval remains analysis-only when this packet is a PR Readiness review packet.",
        ]
        plain_english_summary = (
            "This BP2 Branch Plan Review summarizes how the accepted or waived Branch Vision "
            "will be built, validated, hardened, live-validated, reviewed, and rolled back. "
            "For this packet, it serves as engineering-plan context for PR Readiness Stage 1."
            if pr_readiness_stage1_packet
            else
            "This BP2 Branch Plan Review summarizes how the accepted or waived Branch Vision "
            "will be implemented, validated, hardened, live-validated, reviewed, and rolled back "
            "before BP3 may authorize Workstream implementation."
        )
        end_state_vision = (
            "The completed governance repair leaves lifecycle law, BP1/BP2/BP3 artifact roles, "
            "the local USER hub model, external-state split, helper/validator enforcement, and "
            "pending artifact-model decisions in their proper owners."
            if pr_readiness_stage1_packet
            else
            "When BP2 is accepted or waived, USER should understand which implementation surfaces "
            "are affected, which validators prove them, which risks remain, and what stays future-gated."
        )
        walkthrough = [
            "Review the copied context plan for the lifecycle and USER hub model.",
            "Review phase governance, branch artifact rules, and helper registry for owner boundaries.",
            "Review the copied branch authority record for standing Governance routing context.",
            "Use this packet to decide whether PR Readiness Stage 1 analysis should begin.",
        ]
        surface_map = [
            "Docs/phase_governance.md: lifecycle law.",
            "Docs/branch_plans/README.md: BP1/BP2/BP3 artifact rules.",
            "Docs/validation_helper_registry.md: helper and validator enforcement.",
            "Docs/branch_records/index.md and Governance branch record: branch routing law.",
            "C:\\Nexus USER\\Governance and C:\\Nexus USER\\Governance-YYYYMMDD-HHMMSS.zip: temporary USER review aids.",
        ]
        implementation_options = [
            "Option A - Approve PR Readiness Stage 1 analysis as recommended. Pros: moves the Governance reform toward PR creation review; Cons: no PR is created yet; Risk: low.",
            "Option B - Revise the PR Readiness Stage 1 inspection criteria before analysis. Pros: lets USER tune the review; Cons: adds packet/source-truth repair; Risk: low.",
            "Option C - Pause and request another governance hardening scan. Pros: maximum caution; Cons: delays PR readiness; Risk: low.",
        ]
        recommended_direction = (
            "Codex recommends approving PR Readiness Stage 1 only after the local USER hub packet, "
            "source-truth owners, helper/validator rules, and technical-metadata boundaries read cleanly."
            if pr_readiness_stage1_packet
            else
            "Codex recommends accepting BP2 only when the engineering plan clearly builds the accepted BP1 vision, "
            "names its affected surfaces, validators, proof path, rollback plan, and pending boundaries."
        )
        current_scope = [
            "Governance Phase Lifecycle Reform source-truth and helper hardening.",
            "Local USER hub packet refresh under C:\\Nexus USER.",
            "Technical proof metadata remains outside USER-facing review content.",
            "PR Readiness Stage 1 remains pending USER approval.",
        ]
        future_scope = [
            "PR creation, merge, release, cleanup, runtime work, FAM-006/FAM-007 mutation, private/provider/cache/memory actions, sidecars, and separate Review/Upload taxonomy remain pending USER decisions; timestamped ZIP naming is mandatory active policy.",
        ]
        slc_package_plan = [
            "SLCs remain engineering route details inside an accepted branch; they do not automatically become separate branches.",
            "Workstream implementation is not part of this PR Readiness Stage 1 packet.",
        ]
        user_decisions = [
            "Does USER approve PR Readiness Stage 1 analysis for this Governance branch?",
            "Does USER require any change to PR Readiness Stage 1 inspection criteria before analysis?",
            "Does USER confirm PR creation, merge, release, cleanup, runtime/provider/cache/memory/private actions, and artifact-model changes remain pending?",
        ]
        if bp1_branch_vision_packet:
            contract_status = (
                "Future Preview Only - BP1 Branch Vision remains pending USER acceptance, "
                "revision, waiver, rejection, or hold. BP2 review is not active."
            )
            contract_version = "v2 - Future BP2 preview aid for BP1 packet; not active BP2 review."
            what_user_sees = (
                "USER should use USER_BRANCH_VISION_REVIEW.md as the only primary decision file. "
                "This supporting aid previews the kind of engineering-plan questions that may be "
                "asked later if BP1 is accepted or waived; it does not make BP2 reviewable."
            )
            why_nexus = (
                "This keeps Branch Vision and Branch Plan gates separate so a readable preview "
                "cannot be mistaken for USER acceptance, implementation approval, or Workstream readiness."
            )
            design_ballot = [
                "Do not decide BP2 from this preview.",
                "Use this preview to note BP2 questions after BP1.",
                "Route back to BP1 if the preview changes the Branch Vision.",
                "Pause / unclear.",
            ]
            user_decisions_intro = (
                "USER should decide only the BP1 Branch Vision from this packet. "
                "Any BP2 notes are future preview feedback and do not make BP2 active."
            )
            implementation_constraints = [
                "BP1 is the only active USER decision in this packet.",
                "BP2 review, BP3, Workstream implementation, PR, merge, release, and runtime/provider/private/cache/memory actions remain blocked.",
                "This preview must not be treated as USER acceptance or waiver."
            ]
            rejected_deferred = [
                "BP2 acceptance is deferred until BP1 acceptance or waiver exists and a later USER-approved BP2 packet is generated.",
                "BP3 and Workstream implementation remain deferred to later gates.",
            ]
            source_truth_impact = [
                "No source-truth owner should treat this BP1 packet as accepted or implementation-ready.",
                "Any later BP2 packet must regenerate from current source truth after BP1 is accepted or waived.",
            ]
            contract_change_log = [
                "v2 - Generated as a future BP2 preview aid inside a BP1 packet to preserve validator compatibility without implying BP2 reviewability."
            ]
            completion_checklist = [
                "BP1 acceptance or waiver exists before any later BP2 packet becomes active.",
                "Later BP2 packet regenerates from current source truth and names affected surfaces, validators/helpers, proof requirements, H1/LV/UTS expectations, rollback/safety plan, risks, and future-gated boundaries.",
                "Helper output verifies packet freshness while USER-facing files keep packet reviewability separate from USER acceptance.",
                "BP3 / Workstream Entry may approve implementation only after BP1 and BP2 are accepted or explicitly waived and BP3 is separately approved or waived.",
            ]
            plain_english_summary = (
                "This is not the active BP2 review. It is a supporting preview included in a BP1 "
                "packet so USER can see what engineering-plan questions may come later after the "
                "Branch Vision is accepted or waived."
            )
            end_state_vision = (
                "If BP1 is later accepted or waived, a regenerated BP2 packet should make the "
                "implementation surfaces, validators, risks, proof path, rollback plan, and blocked "
                "future gates clear before any BP3 or Workstream decision."
            )
            walkthrough = [
                "Read USER_BRANCH_VISION_REVIEW.md first and decide BP1.",
                "Use this supporting aid only to preview later BP2 engineering-plan concerns.",
                "Do not treat this supporting aid as BP2 acceptance, BP3 approval, or implementation approval.",
            ]
            surface_map = [
                "USER_BRANCH_VISION_REVIEW.md: active BP1 decision file.",
                "USER_BRANCH_PLAN_REVIEW.md: supporting future BP2 preview only.",
                "Source Truth Context: copied source-truth references for USER inspection.",
            ]
            implementation_options = [
                "Option A - Decide BP1 first. Pros: keeps gates deterministic; Cons: BP2 waits; Risk: low.",
                "Option B - Revise BP1 before BP2. Pros: fixes vision drift early; Cons: requires packet repair; Risk: low.",
                "Option C - Hold BP1. Pros: preserves caution; Cons: blocks BP2; Risk: low.",
            ]
            recommended_direction = (
                "Codex recommends deciding BP1 first, then regenerating a later BP2 packet only "
                "after BP1 acceptance or waiver is recorded."
            )
            current_scope = [
                "BP1 Branch Vision Review only.",
                "Supporting BP2 preview aid is not an active decision.",
            ]
            future_scope = [
                "BP2, BP3, Workstream implementation, PR, merge, release, runtime/provider/private/cache/memory actions, and cleanup remain pending USER decisions.",
            ]
            slc_package_plan = [
                "SLCs remain candidate Slice-level planning details for later BP2/BP3.",
                "No SLC or seam is implementation-approved by this BP1 packet.",
            ]
            user_decisions = [
                "Does USER accept, revise, waive, reject, or hold the BP1 Branch Vision?",
                "Does USER want any previewed BP2 concern considered before a later BP2 packet is generated?",
                "Does USER confirm BP2, BP3, Workstream implementation, and all runtime/provider/private/cache/memory gates remain blocked?",
            ]
    if is_fam007_private_boundary_setup:
        plain_english_summary = (
            "This BP2 support file is preview/context only because BP1 is still pending. "
            "If USER accepts or explicitly waives the BP1 Branch Vision, BP2 should plan "
            "the public-safe engineering route for FAM-007 Dev/Owner private-boundary setup: "
            "Dev and Owner boundary matrices, private root and remote decisions, public-upstream "
            "safety, GitHub Desktop private binding posture, backup/import consent, provider/runtime "
            "deferral, cache and memory deferral, proof requirements, and rollback expectations."
        )
        end_state_vision = (
            "When BP2 is later accepted or waived, USER should understand which public-safe "
            "source-truth, helper, fixture, validator, packet, H1, LV/UTS, rollback, and proof "
            "surfaces will prepare future Dev/Owner private-boundary setup while every private "
            "or runtime action remains separately gated."
        )
        what_user_sees = (
            "USER should see the current BP1 Branch Vision as the only primary decision file. "
            "This BP2 support file exists only to preview the likely engineering-plan shape if BP1 "
            "is accepted or waived; it does not close BP2 and does not authorize Workstream work."
        )
        why_nexus = (
            "This fits Nexus because FAM-007 private-boundary setup is a trust-boundary problem. "
            "Planning Dev, Owner, public-upstream, private origins, backup/import consent, provider "
            "deferral, cache deferral, memory deferral, and lane identity together keeps the public "
            "repo local-first, inspectable, and USER-controlled."
        )
        implementation_constraints = [
            "BP2 is pending until BP1 is accepted or explicitly waived.",
            "BP2 may plan public-safe source-truth, fixture, validator, helper, packet, and proof surfaces only.",
            "Private Dev repo creation, Owner repo creation, local-only roots, private remotes, GitHub Desktop private binding, backup/import behavior, provider/model execution, runtime cache behavior, memory behavior, PR, merge, release, cleanup, and v1.8.0 work remain future USER decisions.",
            "Provider-visible data must remain none; sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, memory/learning/personalization inactive, and runtime cache behavior inactive.",
        ]
        rejected_deferred = [
            "Deferred: BP2 acceptance, BP3, Workstream implementation, actual private Dev setup, and actual Owner setup.",
            "Deferred: private repo/root/remote creation, GitHub Desktop private binding, backup/import execution, and public-to-private import.",
            "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
        ]
        source_truth_impact = [
            "FAM-007 family vision and AI runtime/trust architecture remain the durable policy context.",
            "The FAM-007 branch record and external branch plan remain the branch-specific planning owners.",
            "BP2 must fold any USER revision that changes edition boundaries, private/public promotion, provider/cache/memory policy, or proof expectations into the proper source-truth owner before BP3.",
        ]
        contract_change_log = [
            "v1 - BP2 support file generated as future-gated preview for the active FAM-007 private-boundary setup BP1 packet.",
        ]
        completion_checklist = [
            "BP1 is accepted or explicitly waived before BP2 is treated as a plan gate.",
            "Accepted or waived BP1 trace is present.",
            "Implementation package summary names Dev boundary, Owner boundary, private root/remote gates, public-upstream safety, backup/import deferral, provider/model/runtime/cache/memory deferral, validation proof, packet proof, H1, LV/UTS, and rollback/safety expectations.",
            "All private/runtime/provider/cache/memory/PR/merge/release/cleanup boundaries remain pending USER decisions.",
            "BP3 / Workstream Entry remains blocked until BP2 is accepted or explicitly waived and orchestration validation is green.",
        ]
        walkthrough = [
            "Review USER Review/USER_BRANCH_VISION_REVIEW.md first; this BP2 file cannot become green while BP1 is pending.",
            "Confirm whether BP2 should keep Dev and Owner private-boundary setup in one public-safe branch.",
            "Confirm which private root, private remote, GitHub Desktop, backup/import, provider/cache/memory, and public-to-private promotion decisions need matrix proof.",
            "Confirm the required no-leak, provider-state, packet, fixture, validator, H1, and LV/UTS proof before implementation.",
        ]
        surface_map = [
            "USER packet: BP1 primary vision file now; future BP2 engineering plan only after BP1 acceptance or waiver.",
            "Branch record and external branch plan: branch-specific FAM-007 private-boundary authority and planning owners.",
            "FAM-007 family vision and AI runtime/trust architecture: provider, model, cache, memory, permission, and public/private boundary owners.",
            "Validation surfaces: public leak-prevention, provider-state, branch-planning fixture validation, packet validation, and branch governance validation.",
            "Future proof surfaces: H1 implementation-vs-plan comparison, Live Validation or UTS waiver/proof, and PR Readiness only after later approvals.",
        ]
        implementation_options = [
            "Option A - Plan one public-safe Dev/Owner private-boundary setup package in BP2. Pros: keeps coupled trust-boundary gates consistent; Cons: broader BP2; Risk: low when all private/runtime actions stay gated.",
            "Option B - Split Dev and Owner private-boundary setup after BP1. Pros: smaller future packets; Cons: higher risk of inconsistent private/public gates; Risk: medium unless USER wants different timelines.",
            "Option C - Plan only an action-gate registry first. Pros: narrowest engineering scope; Cons: delays Dev/Owner private-boundary detail; Risk: low but less useful.",
            "Option D - Require BP2 to include a full decision matrix and proof map. Pros: strongest USER clarity; Cons: more planning detail before Workstream; Risk: low.",
        ]
        recommended_direction = (
            "Codex recommends Option A with the Option D decision matrix: keep Dev and Owner "
            "private-boundary setup together for BP2, require explicit proof for each private/runtime "
            "gate, and leave actual setup or execution for later USER-approved phases."
        )
        current_scope = [
            "BP1 Branch Vision Review is the current USER decision.",
            "BP2 content in this packet is preview/context only and cannot close the BP2 gate.",
            "The branch remains public-safe and does not create private roots, remotes, provider behavior, cache behavior, memory, or runtime work.",
        ]
        future_scope = [
            "BP2 should plan Dev boundary, Owner boundary, private root/remote gates, public-upstream safety, backup/import deferral, provider/model/runtime/cache/memory deferral, proof requirements, H1, LV/UTS, and rollback/safety.",
            "BP3, Workstream implementation, private setup, provider/model/runtime/cache/memory behavior, PR, merge, release, cleanup, and v1.8.0 remain pending USER decisions.",
        ]
        slc_package_plan = [
            "SLCs remain future engineering route details inside the accepted branch vision.",
            "Candidate future seam families: Dev private-boundary readiness, Owner private-boundary readiness, private remote/public-upstream safety, backup/import deferral, and provider/model/runtime/cache/memory deferral.",
            "No future seam may execute the private/runtime action it is proving as gated without a separate USER approval.",
        ]
        user_decisions = [
            "Does USER accept, revise, waive, reject, or hold the BP1 private-boundary setup Branch Vision?",
            "If BP1 is accepted or waived, should BP2 plan one combined Dev/Owner private-boundary setup package or split Dev and Owner later?",
            "Which private root, private remote, GitHub Desktop, backup/import, provider/cache/memory, and public-to-private promotion decisions must BP2 prove?",
            "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
        ]
    if is_fam007_owner_ai_foundation and not bp2_branch_plan_packet and not bp3_orchestration_packet:
        plain_english_summary = (
            "This BP2 support file is preview/context only because BP1 is still pending. "
            "If USER accepts or explicitly waives BP1, BP2 should plan the public-safe "
            "engineering route for FAM-007 Owner AI Operational Foundation Gates: "
            "artifact exclusion controls, consent-shell disabled states, memory/cache "
            "consent gates, capability install-intent gates, Developer/Owner lane "
            "readiness gates, Owner AI memory/agent foundation gate schemas, direct "
            "validator/helper proof, and future-gated private/runtime boundaries."
        )
        end_state_vision = (
            "When BP2 is later accepted or waived, USER should understand which "
            "public-safe source-truth, helper, fixture, validator, packet, H1, "
            "LV/UTS, rollback, and proof surfaces will implement or enforce the "
            "selected controls while every private setup, provider execution, "
            "runtime cache activation, durable memory, and real agent action remains "
            "separately gated."
        )
        what_user_sees = (
            "USER should see the current BP1 Branch Vision as the only primary "
            "decision file. This BP2 support file previews the later engineering "
            "shape if BP1 is accepted or waived; it does not close BP2 and does not "
            "authorize Workstream work."
        )
        why_nexus = (
            "This fits Nexus because future Owner AI needs explicit, inspectable, "
            "local-first trust controls before sensitive capability exists. The "
            "public branch can implement gate behavior, disabled states, schemas, "
            "validators, and proof while provider/model/runtime/cache/memory "
            "activation and private Owner material remain USER-gated."
        )
        implementation_constraints = [
            "BP2 is pending until BP1 is accepted or explicitly waived.",
            "BP2 may plan public-safe controls, schemas, manifests, validators, fixtures, helper behavior, packet proof, and disabled-state enforcement only.",
            "Private Developer lane setup, Owner lane setup, private repo/root/remote creation, GitHub Desktop private binding, backup/import behavior, provider/model execution, runtime cache activation, persistent memory, real Owner memory, real agents, PR, merge, release, cleanup, and v1.8.0 work remain future USER decisions.",
            "Provider-visible data must remain none; sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, memory/learning/personalization inactive, and runtime cache behavior inactive.",
        ]
        rejected_deferred = [
            "Deferred: BP2 acceptance, BP3, Workstream implementation, and actual private Developer or Owner setup.",
            "Deferred: private repo/root/remote creation, GitHub Desktop private binding, backup/import execution, model downloads, provider setup, and capability-pack installation execution.",
            "Deferred: provider SDK/model execution, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, real Owner agents, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
        ]
        source_truth_impact = [
            "FAM-007 family vision, AI edition trust-boundary plan, and AI runtime/trust architecture remain the durable policy context.",
            "The FAM-007 branch record and external branch plan remain the branch-specific route and planning owners.",
            "BP2 must fold any USER revision that changes edition boundaries, protected asset policy, provider/cache/memory policy, capability-pack architecture, or proof expectations into the proper source-truth owner before BP3.",
        ]
        contract_change_log = [
            "v1 - BP2 support file generated as future-gated preview for the active FAM-007 Owner AI Operational Foundation Gates BP1 packet.",
        ]
        completion_checklist = [
            "BP1 is accepted or explicitly waived before BP2 is treated as a plan gate.",
            "Accepted or waived BP1 trace is present.",
            "Implementation package summary names artifact exclusion controls, consent-shell disabled states, memory/cache consent gates, capability install-intent gates, Developer/Owner lane readiness gates, Owner AI memory/agent foundation gate schemas, validation proof, packet proof, H1, LV/UTS, and rollback/safety expectations.",
            "Each slice has a concrete implemented-control target rather than only proof, readiness, or boundary-label language.",
            "All private/runtime/provider/cache/memory/PR/merge/release/cleanup boundaries remain pending USER decisions.",
            "BP3 / Workstream Entry remains blocked until BP2 is accepted or explicitly waived and orchestration validation is green.",
        ]
        walkthrough = [
            "Review USER Review/USER_BRANCH_VISION_REVIEW.md first; this BP2 file cannot become green while BP1 is pending.",
            "Confirm whether BP2 should keep all six Owner AI foundation gate slices in one public-safe branch.",
            "Confirm the control behavior, affected surfaces, validator/helper proof, and rollback/safety plan expected for each slice.",
            "Confirm the required no-leak, provider-state, packet, fixture, branch-planning, H1, and LV/UTS proof before implementation.",
        ]
        surface_map = [
            "USER packet: BP1 primary vision file now; future BP2 engineering plan only after BP1 acceptance or waiver.",
            "Branch record and external branch plan: branch-specific FAM-007 Owner AI foundation route and planning owners.",
            "FAM-007 family vision, AI edition plan, and AI runtime/trust architecture: provider, model, cache, memory, permission, protected asset, and Public/Developer/Owner lane owners.",
            "Validation surfaces: public leak-prevention, provider-state, branch-planning fixture validation, packet validation, source-owner validation, and branch governance validation.",
            "Future proof surfaces: H1 implementation-vs-plan comparison, Live Validation or UTS waiver/proof, and PR Readiness only after later approvals.",
        ]
        implementation_options = [
            "Option A - Plan one public-safe Owner AI Operational Foundation Gates package in BP2. Pros: keeps coupled trust-boundary gates consistent; Cons: broader BP2; Risk: low when all private/runtime actions stay gated.",
            "Option B - Split artifact exclusion into its own later branch. Pros: narrower immediate engineering plan; Cons: consent, memory/cache, install-intent, and lane readiness may drift. Risk: medium.",
            "Option C - Split consent-shell and memory/cache gates into the first BP2 path. Pros: centers visible consent posture; Cons: protected artifact exclusion may lag. Risk: medium.",
            "Option D - Require a full slice-control matrix and proof map. Pros: strongest USER clarity and deterministic validation target; Cons: more planning detail before Workstream. Risk: low.",
        ]
        recommended_direction = (
            "Codex recommends Option A with the Option D control matrix: keep the six "
            "Owner AI foundation gates together for BP2, require a concrete control "
            "target for each slice, and leave actual private setup, provider execution, "
            "runtime cache activation, memory, and agents for later USER-approved phases."
        )
        current_scope = [
            "BP1 Branch Vision Review is the current USER decision.",
            "BP2 content in this packet is preview/context only and cannot close the BP2 gate.",
            "The branch remains public-safe and does not create private roots, remotes, provider behavior, cache behavior, memory, agents, or runtime work.",
        ]
        future_scope = [
            "BP2 should plan artifact exclusion controls, consent-shell disabled states, memory/cache consent gates, capability install-intent gates, Developer/Owner lane readiness gates, Owner AI memory/agent foundation gate schemas, proof requirements, H1, LV/UTS, and rollback/safety.",
            "BP3, Workstream implementation, private setup, provider/model/runtime/cache/memory behavior, real Owner memory, real agents, PR, merge, release, cleanup, and v1.8.0 remain pending USER decisions.",
        ]
        slc_package_plan = [
            "SLCs remain future engineering route details inside the accepted branch vision.",
            "Candidate future slices: artifact exclusion controls, consent-shell disabled states, memory/cache consent gates, capability install-intent gates, Developer/Owner lane readiness gates, and Owner AI memory/agent foundation gate schemas.",
            "No future slice may execute the private/runtime action it is proving as gated without a separate USER approval.",
        ]
        user_decisions = [
            "Does USER accept, revise, waive, reject, or hold the BP1 Owner AI Operational Foundation Gates Branch Vision?",
            "If BP1 is accepted or waived, should BP2 plan all six gate slices together or narrow the first engineering package?",
            "Which protected artifact classes, consent states, cache/memory boundaries, install-intent gates, lane-readiness checks, and Owner AI schema fields must BP2 prove?",
            "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
        ]
    if is_fam007_owner_ai_foundation and (
        bp2_branch_plan_packet
        or bp3_orchestration_packet
        or workstream_package_approval_packet
    ):
        accepted_user_response = (
            "BP1, BP2, and BP3 accepted - USER accepted the repaired FAM-007 "
            "Owner AI Operational Foundation Gates Branch Vision, engineering "
            "plan, and Workstream Entry / Orchestration Validation; this packet "
            "supports complete bounded Workstream implementation approval."
            if workstream_package_approval_packet
            else
            "BP1 and BP2 accepted - USER accepted the repaired FAM-007 Owner AI "
            "Operational Foundation Gates Branch Vision and engineering plan; BP3 "
            "is now the active Workstream Entry / Orchestration Validation packet."
            if bp3_orchestration_packet
            else
            "BP1 accepted - USER accepted the repaired FAM-007 Owner AI Operational "
            "Foundation Gates Branch Vision for BP2 generation as the Option A "
            "grouped gate route. BP2 may plan the public-safe engineering route "
            "for artifact exclusion controls, provider/runtime disabled-state "
            "consent shells, memory/cache consent gates, capability-pack "
            "install-intent gates, Developer/Owner lane readiness gates, and "
            "Owner AI memory/agent foundation gate schemas."
        )
        user_response_text = (
            "Status: Accepted by USER for BP1/BP2/BP3 - this BP2 support file is "
            "closed as accepted engineering-plan context for the complete bounded "
            "Workstream implementation approval packet."
            if workstream_package_approval_packet
            else
            "Status: Accepted by USER - this BP2 support file is closed as the "
            "accepted engineering-plan context for the active BP3 Workstream Entry "
            "/ Orchestration Validation packet."
            if bp3_orchestration_packet
            else
            "Status: Pending USER Response - this BP2 engineering plan is ready for "
            "USER to accept, revise, waive, hold, reject, or route back. BP3, "
            "Workstream implementation, private setup, provider/model/runtime/"
            "cache/memory activation, real Owner memory, real agents, PR, merge, "
            "release, cleanup, sibling-worktree mutation, AI Product Contract "
            "import, Private Dev ORIN import, and v1.8.0 work remain pending."
        )
        codex_response_digest = (
            "Codex digested accepted BP1, accepted BP2, and accepted BP3 into "
            "Workstream approval context. The approval packet preserves all six "
            "Owner AI foundation gate Slice/SLC deliverables, all eighteen accepted "
            "seams, and SLC-001 / Seam 1 as the entry checkpoint."
            if workstream_package_approval_packet
            else
            "Codex digested USER BP2 acceptance into BP3 readiness context. BP3 "
            "must verify that the accepted BP2 plan implements the accepted BP1 "
            "vision, that all six Slice/SLCs trace to both contracts, and that "
            "Workstream implementation remains blocked until USER later approves "
            "a bounded Workstream package."
            if bp3_orchestration_packet
            else
            "Codex digested the accepted BP1 vision into a BP2 engineering plan. "
            "The plan keeps all six Owner AI foundation gate slices in one "
            "public-safe package, names concrete control behavior for each slice, "
            "and leaves private/runtime/provider/cache/memory behavior future-gated."
        )
        workstream_entry_result = (
            "Implementation-ready packet - BP1, BP2, and BP3 are accepted; USER "
            "is reviewing complete bounded Workstream implementation for the "
            "same-branch Owner AI Operational Foundation Gates package."
            if workstream_package_approval_packet
            else
            "BP3 active - Workstream Entry / Orchestration Validation is the "
            "current review gate. BP3 may recommend SLC-001 / Seam 1 - Define "
            "protected classes and public-safe exclusion contract as the first "
            "bounded Workstream seam, but this packet does not authorize "
            "Workstream implementation."
            if bp3_orchestration_packet
            else
            "BP3 not started - Workstream Entry / Orchestration Validation remains "
            "pending until USER accepts or explicitly waives this BP2 plan."
        )
        contract_status = (
            "Complete - USER accepted the BP2 Branch Plan Contract; BP3 is "
            "accepted; this file supports complete bounded Workstream "
            "implementation approval."
            if workstream_package_approval_packet
            else
            "Complete - USER accepted the BP2 Branch Plan Contract; BP3 is the "
            "active Workstream Entry / Orchestration Validation gate."
            if bp3_orchestration_packet
            else
            "Pending USER Response - USER must accept, revise, reject, hold, route "
            "back, or explicitly waive this BP2 engineering plan before BP3."
        )
        contract_version = (
            "v5 - accepted BP1/BP2/BP3 digested into FAM-007 Owner AI "
            "Operational Foundation Gates Workstream approval support context."
            if workstream_package_approval_packet
            else
            "v4 - BP2 acceptance digested into FAM-007 Owner AI Operational "
            "Foundation Gates BP3 orchestration-readiness support context."
            if bp3_orchestration_packet
            else
            "v2 - accepted repaired BP1 vision digested into FAM-007 Owner AI "
            "Operational Foundation Gates BP2 engineering plan."
        )
        plain_english_summary = (
            "This support file records the accepted engineering plan for the "
            "FAM-007 Owner AI Operational Foundation Gates carrier. The active "
            "packet asks USER whether Codex may execute the complete accepted "
            "public-safe Workstream package: SLC-001 through SLC-006 and all "
            "eighteen accepted seams."
            if workstream_package_approval_packet
            else
            "This support file records the accepted BP2 engineering plan for the "
            "FAM-007 Owner AI Operational Foundation Gates carrier. The active "
            "packet is BP3: it checks whether the accepted vision and accepted "
            "plan are ready to become a bounded Workstream implementation request "
            "later."
            if bp3_orchestration_packet
            else
            "This BP2 Branch Plan Review explains how Codex would build the "
            "accepted Owner AI Operational Foundation Gates vision without starting "
            "Workstream implementation. The plan is public-safe: it maps six gate "
            "slices to concrete controls, likely source surfaces, validators, proof "
            "requirements, rollback expectations, H1/LV/UTS expectations, and "
            "future USER gates."
        )
        end_state_vision = (
            "When BP2 is accepted or waived, USER should understand the engineering "
            "route for protected artifact exclusion, disabled provider/runtime "
            "states, cache-versus-memory consent, capability install intent, "
            "Developer/Owner lane readiness, and Owner AI memory/agent schemas. "
            "No private setup, provider/model execution, runtime cache activation, "
            "durable memory, or real agent behavior is approved by this packet."
        )
        what_user_sees = (
            "The primary BP3 decision file lives under USER Review. This BP2 file "
            "is supporting context under Review Aids: it shows the accepted plan "
            "that BP3 must trace, including six Slice/SLCs, proof lanes, H1/LV/UTS "
            "expectations, rollback posture, and future-gated private/runtime "
            "boundaries."
            if bp3_orchestration_packet
            else
            "USER sees one primary BP2 decision file under the local USER hub. It "
            "names the implementation package, Slice/SLC plan, seam checkpoints, "
            "affected surfaces, proof lanes, risks, rollback plan, and exact next "
            "decision options. Supporting BP1 context appears as review aid only."
        )
        why_nexus = (
            "This fits Nexus because Owner AI readiness must be explicit, "
            "inspectable, local-first, and consent-aware before sensitive capability "
            "exists. The branch can implement or enforce public-safe gates later "
            "without exposing private artifacts or activating provider/runtime/"
            "cache/memory behavior."
        )
        walkthrough = [
            "Open USER Review/USER_BRANCH_PLAN_REVIEW.md first and review the six-slice engineering plan.",
            "Confirm that every slice names concrete control behavior rather than proof-only or boundary-label work.",
            "Check the public/private leakage controls, disabled-state/no-execution rules, H1 expectations, LV/UTS expectations, rollback plan, and route-back limits.",
            "Choose accept, revise, waive, hold, reject, or route back before BP3.",
        ]
        surface_map = [
            "Primary USER decision file: USER Review/USER_BRANCH_PLAN_REVIEW.md.",
            "Supporting accepted BP1 context: Review Aids/USER_BRANCH_VISION_REVIEW.md.",
            "Branch record: durable FAM-007 route receipt and external-state pointers.",
            "External branch plan/state: active BP2 posture, accepted BP1 trace, packet pointer, and next-gate routing.",
            "Reusable helpers and validators: packet generation, packet validation, public leak-prevention, provider-state validation, source-owner validation, branch governance validation, and branch-planning fixture validation.",
        ]
        implementation_options = [
            "Option A - accept the grouped six-slice BP2 plan as written. Pros: one coherent trust-boundary package; Cons: broader BP3 and Workstream; Risk: low when future-gated boundaries stay explicit.",
            "Option B - accept with specific slice or proof changes. Pros: tunes the plan before BP3; Cons: requires packet/source-truth refresh; Risk: low.",
            "Option C - route back to BP1 if the plan changes the accepted vision. Pros: safest for vision drift; Cons: delays BP3; Risk: low.",
            "Option D - split the package before BP3. Pros: smaller later implementation packages; Cons: higher drift risk across coupled gates; Risk: medium.",
            "Option E - waive remaining BP2 questions and proceed to BP3. Pros: faster; Cons: weaker planning proof; Risk: medium for trust-boundary work.",
            "Option F - hold for more examples, risks, or proof models. Pros: improves confidence; Cons: delays implementation; Risk: low.",
        ]
        recommended_direction = (
            "Codex recommends accepting the grouped BP2 plan if USER agrees the six "
            "gates share one FAM, one trust-boundary route, one worktree, aligned "
            "timing, and one validation path. BP3 should then verify whole-package "
            "orchestration before any Workstream implementation approval is requested."
        )
        current_scope = [
            "BP2 engineering planning for the accepted Owner AI Operational Foundation Gates vision.",
            "Public-safe control, schema, helper, validator, fixture, packet, proof, H1, LV/UTS, and rollback planning.",
            "No Workstream implementation and no private/runtime/provider/cache/memory action.",
        ]
        future_scope = [
            (
                "Workstream implementation is pending USER acceptance of this complete bounded Workstream approval packet."
                if workstream_package_approval_packet
                else
                "Workstream implementation remains pending a later explicit USER decision after BP3 review."
                if bp3_orchestration_packet
                else
                "BP3 Workstream Entry / Orchestration Validation remains pending USER acceptance or waiver of BP2."
            ),
            (
                "Accepted BP1/BP2/BP3 already govern the requested implementation package; execution still waits for USER to approve this Workstream packet."
                if workstream_package_approval_packet
                else
                "Workstream implementation remains pending BP1/BP2 acceptance or waiver, BP3 green or waiver, and separate bounded USER implementation approval."
            ),
            "Private setup, provider/model/runtime/cache/memory activation, real Owner memory, real agents, PR, merge, release, cleanup, issue mutation, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain pending USER decisions.",
        ]
        slc_package_plan = [
            "SLC-001 - protected artifact exclusion controls: protected-class manifest, public bundle/repo exclusion checks, and negative leak fixtures.",
            "SLC-002 - provider/runtime disabled-state consent shell: disabled-state schema, USER-facing disabled copy, and no-execution proof.",
            "SLC-003 - memory-vs-cache consent gates: separate cache and memory markers, blocked persistence states, and validator proof.",
            "SLC-004 - capability-pack install-intent gates: install-intent state, pending-install blocked state, and no-download/no-setup proof.",
            "SLC-005 - Developer/Owner lane readiness gates: lane identity model, private setup blocked state, and readiness proof.",
            "SLC-006 - Owner AI memory/agent foundation gate schemas: prerequisite schema, blocked-state descriptions, and no-real-memory/no-real-agent proof.",
        ]
        likely_files_lines = [
            "This section is a compact index only; the concrete file/surface expectations are mapped per SLC and per seam below.",
            "Docs/branch_records/feature_fam_007_owner_ai_operational_foundation_gates.md remains the durable route receipt if accepted BP2 outcomes later need fold-down context.",
            "C:\\Nexus Governance State\\branches\\feature_fam_007_owner_ai_operational_foundation_gates\\branch_plan.md owns active BP2 posture, accepted BP1 trace, Slice/SLC plan, and next-gate routing.",
            "C:\\Nexus Governance State\\branches\\feature_fam_007_owner_ai_operational_foundation_gates\\branch_state.md owns external branch posture and packet pointer.",
            "dev/orin_user_review_bundle.py owns packet generation and stale-output validation when reusable packet behavior changes.",
            "Route-specific validators, fixtures, and source-truth files are named in the per-seam table so BP3 can verify exact surface coverage.",
        ]
        active_branch_files = [
            "Active external branch plan exists at C:\\Nexus Governance State\\branches\\feature_fam_007_owner_ai_operational_foundation_gates\\branch_plan.md; it owns active BP2 planning posture, accepted BP1 trace, Slice/SLC plan, external-state pointer, and next-gate routing.",
            "Active external branch state exists at C:\\Nexus Governance State\\branches\\feature_fam_007_owner_ai_operational_foundation_gates\\branch_state.md; it records the current carrier posture and packet pointer outside repo-tracked source truth.",
            "Durable repo branch record remains Docs/branch_records/feature_fam_007_owner_ai_operational_foundation_gates.md; it is route receipt/context and not active operational state.",
        ]
        user_decisions_intro = (
            "USER may answer in order or respond generally. Useful BP2 feedback "
            "includes slice changes, proof-lane changes, protected artifact classes, "
            "consent-state wording, cache/memory boundary expectations, capability "
            "install-intent gates, lane-readiness checks, Owner AI schema fields, "
            "rollback requirements, future-gated boundaries, or anything that would "
            "make this Owner AI foundation engineering plan wrong before BP3."
        )
        implementation_constraints = [
            "BP2 may plan public-safe source-truth, helper, fixture, validator, packet, H1, LV/UTS, rollback, and proof surfaces.",
            "BP2 may not implement Workstream changes or execute the private/runtime actions it describes as future gates.",
            "BP2 may not create private repos, private roots, private remotes, GitHub Desktop private binding, backup/import execution, provider/model/runtime/cache/memory behavior, real Owner memory, or real agents.",
            "Provider-visible data remains none; sentToProvider=false; canAcceptPrompts=false; prompt/provider/model execution remains disabled; downloads/network/external calls remain blocked; runtime cache behavior remains inactive; memory/learning/personalization remains inactive.",
            "Any USER change that alters edition boundaries, protected-asset policy, provider/cache/memory policy, capability-pack architecture, or reusable lane identity must fold into the proper durable source-truth owner before BP3 relies on it.",
        ]
        rejected_deferred = [
            "Deferred: BP3, Workstream implementation, and actual private Developer or Owner setup.",
            "Deferred: private repo/root/remote creation, GitHub Desktop private binding, backup/import execution, model downloads, provider setup, and capability-pack installation execution.",
            "Deferred: provider SDK/model execution, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, real Owner agents, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
        ]
        source_truth_impact = [
            (
                "External branch plan records BP1, BP2, and BP3 accepted with complete bounded Workstream approval pending USER decision as active planning posture."
                if workstream_package_approval_packet
                else
                "External branch plan records BP1 and BP2 accepted with BP3 pending USER review as active planning posture."
                if bp3_orchestration_packet
                else
                "External branch plan records BP1 accepted and BP2 pending review as active planning posture."
            ),
            "Branch record remains durable authority/history and should not become a mutable live ledger.",
            "FAM-007 family vision, AI edition plan, and AI runtime/trust architecture remain reusable policy owners; accepted reusable changes route there only if USER changes family-level policy.",
            "Review packet is a temporary USER review aid; accepted BP2 outcomes later fold into durable repo owners or approved external operational state.",
        ]
        contract_change_log = [
            "v1 - BP1 generated for Owner AI Operational Foundation Gates.",
            "v2 - USER accepted repaired BP1 and BP2 generated as engineering-plan-first review.",
            "v3 - post-rebaseline BP2 generator repaired to avoid BP1-pending preview wording in BP2 packets.",
        ]
        completion_checklist = [
            "Accepted BP1 trace is present.",
            "BP2 implementation package summary, branch scope size test, Slice/SLC plan, affected surfaces, likely files, validators/helpers, proof requirements, H1/LV/UTS expectations, rollback/safety plan, risks, future gates, and exact next decision text are present.",
            "Each slice has a concrete implemented-control target rather than only proof, readiness, or boundary-label language.",
            "USER-facing files avoid live operational ledgers, raw commit values, upload byte-proof values, mutable validator run state, live pull-request posture, and command-wall boundary wording.",
            (
                "Complete bounded Workstream execution remains blocked until USER accepts this Workstream approval packet."
                if workstream_package_approval_packet
                else
                "BP3 and Workstream implementation remain blocked until BP2 is accepted or explicitly waived and later gates are green and approved."
            ),
        ]
        user_decisions = [
            *(
                [
                    "Does USER approve complete bounded Workstream implementation for SLC-001 through SLC-006 and all eighteen accepted seams?",
                    "Does USER agree execution starts at SLC-001 / Seam 1 - Define protected classes and public-safe exclusion contract?",
                    "Does USER want any seam-order, validator, proof, rollback, H1, LV/UTS, or stop-condition revision before implementation?",
                    "Does USER confirm all private/runtime/provider/cache/memory/backup-import-execution/PR/merge/release gates remain pending?",
                ]
                if workstream_package_approval_packet
                else
                [
                    "Does USER approve, revise, waive, reject, or hold BP3 Workstream Entry / Orchestration Validation?",
                    "Does USER agree SLC-001 / Seam 1 - Define protected classes and public-safe exclusion contract should be the first future Workstream seam after separate implementation approval?",
                    "Does USER agree the accepted BP2 plan implements the accepted BP1 vision without changing the Owner AI Operational Foundation Gates route?",
                    "Does USER confirm all private/runtime/provider/cache/memory/backup-import-execution/PR/merge/release gates remain pending?",
                ]
                if bp3_orchestration_packet
                else
                [
                    "Does USER accept the FAM-007 Owner AI Operational Foundation Gates BP2 engineering plan as written?",
                    "Does any slice, proof lane, affected surface, or rollback expectation need to be added, removed, or narrowed before BP3?",
                    "Are the named proof lanes sufficient for BP3: provider-state, public leak-prevention, external-state, branch-readiness planning fixtures, USER review packet validation, source-owner marker validation, and source-truth owner checks?",
                    "Does USER confirm all private/runtime/provider/cache/memory/backup-import-execution/PR/merge/release gates remain pending?",
                ]
            ),
        ]
        design_ballot = [
            *(
                [
                    "Approve complete bounded Workstream implementation as recommended.",
                    "Approve with a revised seam order or proof requirement.",
                    "Waive a specific unresolved Workstream approval question and proceed under the accepted package constraints.",
                    "Hold the branch before Workstream execution.",
                    "Reject or route back to BP3/BP2 if the accepted orchestration or plan needs repair.",
                ]
                if workstream_package_approval_packet
                else
                [
                    "Approve BP3 as recommended.",
                    "Approve BP3 with changes.",
                    "Revise BP3 and regenerate the packet.",
                    "Waive unresolved BP3 questions.",
                    "Reject or hold BP3.",
                ]
                if bp3_orchestration_packet
                else
                [
                    "Accept BP2 as written and authorize BP3 Workstream Entry / Orchestration Validation only.",
                    "Accept BP2 with listed changes, then regenerate the BP2 packet for confirmation.",
                    "Route back to BP1 because the plan changes the accepted vision.",
                    "Explicitly waive remaining BP2 questions and authorize BP3 only.",
                    "Reject this branch plan and request a narrower or different carrier.",
                    "Hold for more examples, risks, or proof models.",
                ]
            ),
        ]
        extra_plan_sections = [
            "## Owner AI Foundation Gate Matrix",
            "",
            "| Slice | Planned control behavior | Current BP2 scope | Future gate | Proof needed |",
            "| --- | --- | --- | --- | --- |",
            "| Protected artifact exclusion | Define controls that keep protected Owner/Developer/private artifacts out of public repo, public packets, upload ZIPs, and public artifacts. | Plan controls, manifests, fixtures, and validators only. | Any private artifact migration or private root setup. | Protected-class manifest, negative leak fixtures, and public bundle/repo exclusion proof. |",
            "| Provider/runtime disabled-state consent shell | Define disabled states and copy for provider/runtime surfaces before execution exists. | Plan schema, wording, and no-execution proof only. | Provider/model/runtime activation. | Provider-state validation and disabled-state fixture proof. |",
            "| Memory/cache consent gates | Separate operational cache consent from durable memory consent. | Plan state markers and blocked persistence states only. | Runtime cache activation or persistent memory. | Cache marker, memory marker, and separation validator proof. |",
            "| Capability install intent | Require explicit install intent before any capability setup path can proceed. | Plan install-intent state and blocked pending-install state only. | Download, setup, or execution. | No-download/no-setup proof and install-intent fixture. |",
            "| Developer/Owner lane readiness | Define readiness gates before private lanes or roots exist. | Plan lane identity, blocked setup states, and validation proof only. | Private Developer or Owner setup. | Lane-readiness validator proof and no private path leakage. |",
            "| Owner AI memory/agent schemas | Define future prerequisite schemas and blocked states without real memory or agents. | Plan schema and no-real-agent/no-real-memory proof only. | Real Owner memory or real agents. | Schema validation and no-execution proof. |",
            "",
            "## Per-SLC / Per-Seam Engineering Plan",
            "",
            "Each SLC is a Slice-level deliverable. Each seam is a later execution or validation checkpoint inside that slice; seam work starts only after BP2 is accepted or waived, BP3 is green or waived, and USER separately approves bounded Workstream implementation.",
            "",
            "### SLC-001 - Protected Artifact Exclusion Controls",
            "",
            "| Seam | Seam purpose | Likely files / surfaces | Concrete behavior or control target | Expected validator / proof command | Fixture expectation | Disabled / no-execution proof | Rollback / repair posture | USER gate preserved | Stop / report condition |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "| SLC-001 / Seam 1 | Define protected classes and public-safe exclusion contract. | C:\\Nexus Governance State\\branches\\feature_fam_007_owner_ai_operational_foundation_gates\\branch_plan.md; Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md; Docs/ai_runtime_and_trust_architecture.md | Public branch recognizes protected artifact classes such as private roots, remotes, secrets, private prompts, memory, private screenshots, model artifacts, private automation, Owner data, and Developer/Owner lane artifacts. | python dev\\orin_public_leak_prevention_validation.py; python dev\\orin_branch_governance_validation.py | Positive fixture names allowed public placeholders; negative fixture names protected classes and blocked public inclusion. | No private path, token, model, memory, Owner data, or private artifact is created, copied, exported, or uploaded. | Revert the manifest/policy row and restore the prior accepted protected-class list; route family-level changes back to source-truth owners. | Private artifact migration and private root/remote setup stay pending USER decisions. | Stop if protected-class drift changes durable policy or requires real private paths/data. |",
            "| SLC-001 / Seam 2 | Enforce public packet/repo/bundle exclusion checks. | dev/orin_public_leak_prevention_validation.py; dev/fixtures/fam007_public_leak_prevention; dev/orin_user_review_bundle.py; C:\\Nexus USER\\FAM-007 | Public bundle, review packet, repo scan, and upload ZIP paths reject protected classes and stale same-label artifacts. | python dev\\orin_public_leak_prevention_validation.py; packet validator against C:\\Nexus USER\\FAM-007 | Negative fixture injects private path/secret/model/memory markers and must fail. | Proof is static scan/no-export; no private artifact is accessed to prove exclusion. | Remove the offending scan rule or generated copy path and regenerate the packet/ZIP. | Sidecar, unique non-timestamp ZIP, private upload, and artifact-model changes stay pending unless separately approved. | Stop if exclusion cannot be proven without reading or moving private material. |",
            "| SLC-001 / Seam 3 | Preserve acceptance/fold-down boundary for protected-asset policy. | Docs/branch_records/feature_fam_007_owner_ai_operational_foundation_gates.md; external branch plan/state; Docs/validation_helper_registry.md | Accepted branch-local exclusion outcomes remain branch-local until PR fold-down decides durable owner placement. | python dev\\orin_source_owner_marker_validation.py; python dev\\orin_external_state_validation.py --root C:\\Nexus Governance State --repo C:\\Nexus Worktrees\\FAM-007 --require-root --require-stage4-records | Fixture proves active state remains external and repo receipt does not become a live ledger. | No PR/merge/release action is implied by BP2 fold-down planning. | Roll back branch-record receipt text to pointer-only language if it starts tracking live state. | PR creation, merge, release, issue mutation, and cleanup stay pending. | Stop if repo docs start carrying live commit identity, live branch state, validation state, or upload byte-proof metadata. |",
            "",
            "### SLC-002 - Provider / Runtime Disabled-State Consent Shell",
            "",
            "| Seam | Seam purpose | Likely files / surfaces | Concrete behavior or control target | Expected validator / proof command | Fixture expectation | Disabled / no-execution proof | Rollback / repair posture | USER gate preserved | Stop / report condition |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "| SLC-002 / Seam 1 | Define disabled provider/runtime state contract. | Docs/ai_runtime_and_trust_architecture.md; Docs/family_visions/FAM-007_local_ai_and_capability_packs.md; external branch plan | Provider/model/runtime surfaces have explicit unavailable states and consent prerequisites without activation. | python dev\\orin_ai_provider_state_validation.py | Fixture must show sentToProvider=false, canAcceptPrompts=false, provider execution disabled, and downloads blocked. | No provider SDK call, model prompt, download, network setup, runtime start, or cache activation occurs. | Revert disabled-state copy/schema to previous inactive posture and rerun provider-state validation. | Provider/model/runtime activation remains pending USER decision. | Stop if copy/schema implies execution is available or provider-visible data can be sent. |",
            "| SLC-002 / Seam 2 | Plan USER-facing disabled-state copy and review packet wording. | dev/orin_user_review_bundle.py; C:\\Nexus USER\\FAM-007\\USER Review\\USER_BRANCH_PLAN_REVIEW.md; Review Aids | USER can inspect why provider/runtime actions are disabled, what consent is missing, and what future gate would be needed. | packet validator; direct USER-facing stale-language and metadata scan | Fixture rejects fake enabled states, implementation-ready wording, and provider execution implied by copy. | Disabled copy is informational only; no button/action path executes provider/runtime work. | Regenerate USER packet from helper after removing misleading copy. | Runtime/provider setup and Workstream implementation remain later gates. | Stop if USER-facing copy makes a disabled state look like a runnable feature. |",
            "| SLC-002 / Seam 3 | Add no-execution proof linkage for BP3. | dev/orin_ai_provider_state_validation.py; dev/orin_branch_readiness_planning_fixture_validation.py; external branch plan | BP3 can prove planned disabled-state changes preserve no-execution posture before implementation begins. | python dev\\orin_ai_provider_state_validation.py; python dev\\orin_branch_readiness_planning_fixture_validation.py | Fixture covers provider disabled, prompt rejected, downloads blocked, and runtime action deferred. | Static validation only; runtime execution stays future-gated unless a later USER approval changes that boundary. | Remove new action hooks or state transitions that bypass disabled state. | Workstream execution follows the active accepted package approval packet and preserves provider/runtime future gates. | Stop if validating the disabled state requires launching provider/model/runtime behavior. |",
            "",
            "### SLC-003 - Memory-Versus-Cache Consent-State Enforcement Gates",
            "",
            "| Seam | Seam purpose | Likely files / surfaces | Concrete behavior or control target | Expected validator / proof command | Fixture expectation | Disabled / no-execution proof | Rollback / repair posture | USER gate preserved | Stop / report condition |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "| SLC-003 / Seam 1 | Separate cache consent from memory consent. | Docs/ai_runtime_and_trust_architecture.md; FAM-007 family vision; external branch plan | Cache state and memory state are separate labels, markers, and gates; cache wording cannot masquerade as memory. | python dev\\orin_ai_provider_state_validation.py; python dev\\orin_branch_governance_validation.py | Fixture fails when cache implies durable memory, learning, personalization, retrieval, indexing, or replay. | Cache inactive and memory inactive remain proof states; no persistence path runs. | Restore separate markers and remove ambiguous combined wording. | Runtime cache activation and durable memory approval stay pending. | Stop if implementation would persist, replay, learn, index, retrieve, or personalize data. |",
            "| SLC-003 / Seam 2 | Plan blocked persistence states and consent error states. | dev/orin_ai_provider_state_validation.py; dev/fixtures; USER packet copy | A blocked state explains what is inactive and which future consent gate is missing. | python dev\\orin_ai_provider_state_validation.py; packet validator | Negative fixture proves blocked memory/cache state cannot transition to active through labels alone. | No file/database/state-store writes for memory or cache activation. | Remove or hard-disable any state transition that can flip memory/cache active. | Memory/cache behavior remains pending USER decision. | Stop if planned copy or state makes cache/memory behavior appear accepted by BP2. |",
            "| SLC-003 / Seam 3 | Preserve source-truth placement for future memory/cache policy. | Docs/ai_runtime_and_trust_architecture.md; Docs/family_visions/FAM-007_local_ai_and_capability_packs.md; external branch plan | Branch-local plan may reference future policy but durable family/architecture policy changes require USER-approved owner updates. | python dev\\orin_source_owner_marker_validation.py; python dev\\orin_branch_governance_validation.py | Fixture rejects branch packet treating itself as durable memory policy owner. | No private data or runtime memory proof is generated. | Route durable policy changes back to the right owner before BP3 depends on them. | Durable memory policy mutation remains separate if USER changes scope. | Stop if BP2 would change reusable memory/cache policy without a source-truth owner. |",
            "",
            "### SLC-004 - Capability-Pack Install-Intent Gates",
            "",
            "| Seam | Seam purpose | Likely files / surfaces | Concrete behavior or control target | Expected validator / proof command | Fixture expectation | Disabled / no-execution proof | Rollback / repair posture | USER gate preserved | Stop / report condition |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "| SLC-004 / Seam 1 | Define explicit install-intent state model. | Docs/family_visions/FAM-007_local_ai_and_capability_packs.md; Docs/ai_runtime_and_trust_architecture.md; external branch plan | Capability setup requires a visible intent state before any download, install, provider setup, or execution path. | python dev\\orin_ai_provider_state_validation.py; python dev\\orin_branch_readiness_planning_fixture_validation.py | Fixture proves no-intent and intent-pending states remain blocked. | No download, setup, provider activation, package install, or external call occurs. | Revert intent-state schema/copy and restore blocked default. | Capability-pack setup and model downloads stay pending USER decisions. | Stop if any install path can run from no-intent or pending-intent state. |",
            "| SLC-004 / Seam 2 | Plan blocked pending-install state and visible route-back. | dev/orin_user_review_bundle.py; USER packet; possible future UI/source surfaces | USER can see what is missing before installation, and BP3 can route back if install intent is underspecified. | packet validator; python dev\\orin_branch_governance_validation.py | Fixture rejects silent install, auto-download, provider activation, or vague setup-approved wording. | Pending-install copy is static only and cannot execute setup. | Remove install affordance or mark it blocked until future approval. | Download/setup execution remains pending USER decision. | Stop if install-intent bypass appears in helper, copy, schema, or fixture. |",
            "| SLC-004 / Seam 3 | Link install-intent gates to protected artifact and provider-state proof. | dev/orin_public_leak_prevention_validation.py; dev/orin_ai_provider_state_validation.py | Install-intent planning cannot leak protected artifacts or imply provider execution. | python dev\\orin_public_leak_prevention_validation.py; python dev\\orin_ai_provider_state_validation.py | Fixture combines install-intent bypass with private artifact leakage and must fail. | No protected package, model artifact, provider token, or setup output is copied. | Revert any install-intent path that touches protected/public boundary incorrectly. | Private import/export and provider setup stay pending. | Stop if install planning requires private artifacts or provider credentials. |",
            "",
            "### SLC-005 - Developer / Owner Lane Readiness Gates",
            "",
            "| Seam | Seam purpose | Likely files / surfaces | Concrete behavior or control target | Expected validator / proof command | Fixture expectation | Disabled / no-execution proof | Rollback / repair posture | USER gate preserved | Stop / report condition |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "| SLC-005 / Seam 1 | Define lane identity without private setup. | Docs/family_visions/FAM-007_local_ai_and_capability_packs.md; Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md; external branch plan | User/Public lane, Developer lane, and Owner lane are labels/readiness states only; they create no private roots/remotes. | python dev\\orin_public_leak_prevention_validation.py; python dev\\orin_branch_governance_validation.py | Fixture rejects private path leakage, old Developer-lane terminology drift, and lane labels that imply setup complete. | No private repo, root, remote, GitHub Desktop binding, or private folder is created. | Revert lane readiness wording to public-safe blocked-state labels. | Private Developer and Owner setup remain pending USER decisions. | Stop if lane labels leak private assumptions or imply private setup exists. |",
            "| SLC-005 / Seam 2 | Plan readiness gates for later private setup approval. | external branch plan/state; Docs/branch_records/feature_fam_007_owner_ai_operational_foundation_gates.md | Later setup must name root/repo/remote/binding/backup/import scope before action; current branch only plans the gate. | python dev\\orin_external_state_validation.py --root C:\\Nexus Governance State --repo C:\\Nexus Worktrees\\FAM-007 --require-root --require-stage4-records | Fixture proves external state can record pending setup without repo live-state leakage. | No setup command, private remote, or GitHub Desktop private binding runs. | Remove active setup posture from repo docs and keep only external pending-state pointer. | Private setup remains pending exact USER approval. | Stop if BR/BP/Workstream text tries to admit private setup by inertia. |",
            "| SLC-005 / Seam 3 | Validate lane-readiness copy in USER-facing packet. | dev/orin_user_review_bundle.py; C:\\Nexus USER\\FAM-007 | USER sees lanes as future-gated readiness states, not product version numbers or live private environments. | packet validator; direct stale-language scan | Fixture rejects copy that treats Developer/Owner lanes as active private roots. | Review packet contains no private path/status/credential proof. | Regenerate packet after correcting lane wording. | Private lane setup and private artifact import stay pending. | Stop if USER-facing copy could be read as approval to create private lanes. |",
            "",
            "### SLC-006 - Owner AI Memory / Agent Foundation Gate Schemas",
            "",
            "| Seam | Seam purpose | Likely files / surfaces | Concrete behavior or control target | Expected validator / proof command | Fixture expectation | Disabled / no-execution proof | Rollback / repair posture | USER gate preserved | Stop / report condition |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "| SLC-006 / Seam 1 | Define future prerequisite schema names and blocked states. | Docs/ai_runtime_and_trust_architecture.md; FAM-007 family vision; external branch plan | Schema describes prerequisites for future Owner memory/agent capability without storing memory or running agents. | python dev\\orin_ai_provider_state_validation.py; python dev\\orin_source_owner_marker_validation.py | Fixture rejects schema fields that imply active real memory, active agents, autonomous execution, or Owner data import. | No real memory, agent runtime, autonomous action, indexing, retrieval, or provider prompt occurs. | Revert schema wording to blocked-state prerequisites only. | Real Owner memory and real agents remain pending USER decisions. | Stop if schema wording is mistaken for real memory/agents or creates execution hooks. |",
            "| SLC-006 / Seam 2 | Plan no-real-memory/no-real-agent proof and public-safe examples. | dev/orin_ai_provider_state_validation.py; dev/orin_public_leak_prevention_validation.py; USER packet | Examples stay synthetic/public-safe and prove future-gated posture only. | python dev\\orin_ai_provider_state_validation.py; python dev\\orin_public_leak_prevention_validation.py | Fixture includes synthetic schema examples and negative private Owner data examples. | No Owner data, private memory, model artifact, agent plan, or execution trace is copied. | Remove non-synthetic examples and rerun leak/provider validators. | Owner data import/export and real Owner AI behavior stay pending. | Stop if proof requires real Owner data, private artifacts, or model/provider execution. |",
            "| SLC-006 / Seam 3 | Link schema gates to BP3 whole-package orchestration. | external branch plan; dev/orin_branch_readiness_planning_fixture_validation.py; dev/orin_user_review_bundle.py | BP3 verifies schema gates only after BP2 acceptance/waiver and does not convert schemas into runtime authority. | python dev\\orin_branch_readiness_planning_fixture_validation.py; packet validator | Fixture rejects BP3 implementation approval while BP2 pending or schema gates ambiguous. | BP3 remains orchestration validation, not runtime execution. | Route back to BP2 or BP1 when schema scope changes the accepted branch vision. | BP3 and Workstream implementation stay pending until USER approves the next gate. | Stop if schema gates change branch vision or widen private/runtime scope. |",
            "",
            "## Cross-Slice Dependencies And Execution Order",
            "",
            "Recommended execution order after BP2 acceptance, BP3 approval, and separate Workstream approval:",
            "",
            "1. SLC-001 / Seam 1 - Define protected classes and public-safe exclusion contract, because all later slices and seams depend on knowing what cannot enter public repo, packet, or upload paths.",
            "2. SLC-002 provider/runtime disabled-state consent shell, because no-execution copy and state must be stable before memory/cache or install-intent gates reference it.",
            "3. SLC-003 memory-vs-cache consent-state enforcement gates, because consent separation depends on disabled provider/runtime posture and protects later schema language.",
            "4. SLC-004 capability-pack install-intent gates, because install/setup must stay blocked before Developer/Owner lane readiness can safely describe future capability work.",
            "5. SLC-005 Developer/Owner lane readiness gates, because lane readiness should consume protected-class, disabled-state, consent, and install-intent proof instead of inventing new private setup authority.",
            "6. SLC-006 Owner AI memory/agent foundation gate schemas, because schemas must sit on the fully proven public/private, provider, cache/memory, install-intent, and lane-readiness boundary.",
            "",
            "Cross-slice dependencies: SLC-001 protects every other slice from leakage; SLC-002 protects SLC-003, SLC-004, and SLC-006 from implied execution; SLC-003 protects SLC-006 from memory/cache confusion; SLC-004 protects SLC-005 and SLC-006 from install/setup bypass; SLC-005 protects SLC-006 from private-lane assumption drift.",
            "",
            "## Protected Artifact Exclusion Matrix",
            "",
            "| Protected class | BP2 plan | Exclusion proof | Future boundary |",
            "| --- | --- | --- | --- |",
            "| Private roots and remotes | Keep paths and URLs out of public packet/repo outputs. | Public leak-prevention scan and negative fixtures. | Private root/remote creation remains pending. |",
            "| Secrets, tokens, prompts, memory, private screenshots, private automation, and model artifacts | Classify as protected and excluded from public review/export paths. | Protected-class manifest plus bundle/repo exclusion proof. | Any private import/export remains pending. |",
            "| Owner/Developer artifacts | Keep artifact examples abstract or synthetic unless later USER approves private handling. | No private artifact fixture. | Private artifact migration remains pending. |",
            "",
            "## Consent / Runtime Disabled-State Matrix",
            "",
            "| Surface | Disabled state | BP2 proof | Future gate |",
            "| --- | --- | --- | --- |",
            "| Provider/model execution | Disabled and unavailable. | Provider-state validator. | Provider/model activation approval. |",
            "| Runtime actions | Blocked behind USER consent. | No-execution fixture. | Workstream and runtime approval. |",
            "| Downloads/network/setup | Blocked. | No-download/no-setup proof. | Capability install/setup approval. |",
            "",
            "## Memory / Cache Consent Matrix",
            "",
            "| State | Meaning | BP2 proof | Future gate |",
            "| --- | --- | --- | --- |",
            "| Cache inactive | Operational cache is not active or replaying data. | Cache-state marker proof. | Runtime cache approval. |",
            "| Memory inactive | Durable memory/learning/personalization is not active. | Memory-state marker proof. | Memory approval. |",
            "| Separation required | Cache cannot masquerade as memory and memory cannot start through cache wording. | Separation validator/fixture proof. | BP3 and later implementation approval. |",
            "",
            "## Capability Install-Intent Matrix",
            "",
            "| Install state | BP2 plan | Blocked action | Proof |",
            "| --- | --- | --- | --- |",
            "| No intent | No setup path can run. | Downloads, setup, execution. | Install-intent fixture. |",
            "| Intent pending | USER-visible pending state only. | Silent install or provider activation. | Pending-install blocked-state proof. |",
            "| Future approved setup | Separate later gate. | Not in BP2. | Future validation. |",
            "",
            "## Developer / Owner Lane Readiness Matrix",
            "",
            "| Lane | BP2 readiness plan | Current branch scope | Future USER gate |",
            "| --- | --- | --- | --- |",
            "| User/Public | Preserve public-safe proof and current public branch context. | Planning and review only. | None for private setup. |",
            "| Developer | Define readiness gate before private Developer setup. | Lane label, blocked setup state, no private path proof. | Private Developer lane setup. |",
            "| Owner | Define readiness gate before Owner private/local setup. | Lane label, blocked setup state, no Owner private data. | Owner lane setup, Owner memory, Owner agents. |",
            "",
            "## Owner AI Memory / Agent Schema Matrix",
            "",
            "| Schema area | BP2 plan | Explicit non-action | Proof |",
            "| --- | --- | --- | --- |",
            "| Memory prerequisites | Define required future consent and protected-state fields. | No real memory, learning, indexing, retrieval, or personalization. | No-memory proof. |",
            "| Agent prerequisites | Define future gate schema and blocked-state language. | No real agents or autonomous execution. | No-agent/no-execution proof. |",
            "| Owner data boundary | Keep Owner-private data out of public branch and packet. | No Owner data import/export. | Public leak-prevention proof. |",
            "",
            "## Proof / Validation Matrix",
            "",
            "| Proof class | Required proof | Candidate validator/helper |",
            "| --- | --- | --- |",
            "| Branch planning packet | Primary BP2 file, accepted BP1 support context, timestamped ZIP, no stale BP1-pending text, no metadata drift. | dev/orin_user_review_bundle.py |",
            "| Protected artifact safety | No private path, token, remote URL, prompt, memory, model artifact, private automation, or private artifact in public branch. | dev/orin_public_leak_prevention_validation.py |",
            "| Provider/runtime deferral | Provider-visible data none, prompt/model execution disabled, downloads blocked, cache/memory inactive. | dev/orin_ai_provider_state_validation.py |",
            "| Planning gate proof | BP2 requires accepted BP1 trace; BP3 blocks while BP2 remains pending. | dev/orin_branch_readiness_planning_fixture_validation.py |",
            "| External-state consistency | External branch plan/state records BP2 reviewability and pending USER gate without making repo files live ledgers. | dev/orin_external_state_validation.py |",
            "| Source owner integrity | Durable source-truth owners keep valid ownership markers. | dev/orin_source_owner_marker_validation.py |",
            "",
            "## Future USER Gate Matrix",
            "",
            "| Future gate | Required before action |",
            "| --- | --- |",
            "| BP3 | USER accepts, revises into confirmation, or explicitly waives BP2. |",
            "| Workstream implementation | BP1 and BP2 accepted or waived, BP3 green or waived, and separate bounded implementation approval. |",
            "| Private Developer / Owner setup | Separate USER approval naming root/repo/remote/setup scope. |",
            "| Provider/model/cache/memory behavior | Separate USER approval plus provider-state proof. |",
            "| Real Owner memory / agents | Separate USER approval plus schema, consent, privacy, and no-leak proof. |",
            "| PR / merge / release / cleanup | Separate phase approvals after implementation, H1, and LV gates. |",
            "",
            "## Expanded Open Engineering Risks",
            "",
            "- Protected-class drift: branch-local wording could quietly narrow protected artifact classes; mitigation is SLC-001 manifest proof and source-truth owner routing.",
            "- Private artifact leakage: public packets, upload ZIPs, fixtures, copied context, or examples could include private paths, remotes, prompts, data, or artifacts; mitigation is public leak-prevention validation and negative fixtures.",
            "- Fake disabled states: UI/copy/schema could say disabled while an action path still runs; mitigation is provider-state validation plus no-execution fixtures.",
            "- Provider execution implied by copy/schema: disabled copy could accidentally imply provider setup is available or accepted; mitigation is direct USER-facing text scan and provider-state validation.",
            "- Cache wording masquerading as memory: cache consent could be described like durable memory, learning, retrieval, or personalization; mitigation is separate cache/memory markers and fixture rejection.",
            "- Install-intent bypass: pending-install wording or setup affordances could imply downloads/setup may run without USER approval; mitigation is no-download/no-setup proof.",
            "- Developer/Owner lane labels leaking private assumptions: lane readiness could be mistaken for private roots/remotes already existing; mitigation is lane wording scan and external-state posture proof.",
            "- Owner AI schema mistaken for real memory or agents: prerequisite schemas could be read as runtime authority; mitigation is no-real-memory/no-real-agent proof and route-back if schema scope changes vision.",
            "- Broad grouped branch drift: six slices may widen beyond one coherent trust-boundary package; mitigation is branch-size route-back criteria and BP3 whole-package verification.",
            "- Cross-slice validation gaps: one validator may prove only one slice while another slice regresses; mitigation is BP3 per-SLC checklist plus direct folder/ZIP scan.",
            "",
            "## H1 / Hardening Expectations By Slice",
            "",
            "- SLC-001 H1 compares implemented exclusion controls against protected-class manifest, public bundle/repo packet outputs, and negative fixtures.",
            "- SLC-002 H1 pressure-tests disabled provider/runtime states against no-execution proof and misleading-copy risk.",
            "- SLC-003 H1 verifies cache and memory stay separate in state markers, copy, fixtures, and source-truth references.",
            "- SLC-004 H1 attempts install-intent bypass paths and confirms downloads/setup/execution remain blocked.",
            "- SLC-005 H1 checks lane-readiness language, private path leakage, and external-state placement for setup posture.",
            "- SLC-006 H1 checks schema examples, blocked-state wording, no-real-memory/no-real-agent proof, and Owner data exclusion.",
            "",
            "## Live Validation / UTS Inspection Expectations",
            "",
            "Live Validation is future-gated. If later Workstream creates user-facing disabled states or packet-visible controls, USER should inspect only public-safe surfaces such as disabled provider/runtime copy, blocked install-intent copy, cache-versus-memory consent wording, lane readiness labels, and schema prerequisite wording. USER should not be asked to run providers, download models, create private roots/remotes, import Owner data, activate cache/memory, or exercise real agents during this branch unless a later USER approval explicitly changes the scope.",
            "",
            "Expected UTS review prompts, if LV later applies:",
            "",
            "- Is each disabled state understandable and clearly blocked until a future USER approval?",
            "- Does any surface imply provider/model/runtime/cache/memory/agent behavior is already active?",
            "- Are protected/private artifacts absent from public packet and visible examples?",
            "- Are cache and memory described as separate states?",
            "- Are Developer/Owner lanes presented as readiness gates rather than active private environments?",
            "- Are Owner AI schemas clearly prerequisites/blocked states rather than real memory or agents?",
            "",
            "## BP3 Verification Checklist By SLC",
            "",
            "- SLC-001: BP3 must verify protected-class list, exclusion surfaces, leak-prevention fixtures, rollback path, and private-artifact future gate.",
            "- SLC-002: BP3 must verify provider/runtime disabled-state schema/copy, no-execution fixture, provider-state validation, and runtime activation future gate.",
            "- SLC-003: BP3 must verify cache/memory marker separation, blocked persistence states, fixture coverage, and no memory/cache activation.",
            "- SLC-004: BP3 must verify install-intent state, pending-install blocked state, no-download/no-setup proof, and install/setup future gate.",
            "- SLC-005: BP3 must verify User/Public, Developer, and Owner lane readiness labels, no private path leakage, external-state placement, and private setup future gate.",
            "- SLC-006: BP3 must verify schema prerequisite scope, no-real-memory/no-real-agent proof, synthetic examples only, and route-back if schema scope changes accepted vision.",
            "- Whole package: BP3 must verify all six slices trace to accepted BP1, BP2 accepted/waived state exists, Workstream entry names only the first approved seam sequence, and continuation remains bounded until Workstream Green, a real blocker, or explicit USER waiver.",
            "",
            "## Branch-Size Route-Back Criteria",
            "",
            "- Split before BP3 if any slice needs a different FAM, package objective, owner/worktree, release timing, validation path, private/runtime/provider action gate, or risk class.",
            "- Hold before BP3 if any protected-class, provider-state, cache/memory, install-intent, lane-readiness, or Owner AI schema decision is still too ambiguous for deterministic verification.",
            "- Route back to BP1 if BP2 changes what the branch is meant to become, adds real private/runtime/provider/cache/memory/agent behavior, changes product/family vision, or reframes the accepted grouped route.",
            "- Request a USER decision before implementation if the branch cannot keep all six slices public-safe, if proof requires private artifacts/data, if a validator blind spot remains material, or if the grouped branch stops being the largest safe coherent package.",
            "",
        ]
        response_structure = [
            "Decision: accept, revise, route back to BP1, waive, reject, or hold.",
            "Slice, proof-lane, or surface changes requested.",
            "Must-have proof requirements.",
            "Future-gated boundary controls.",
            "Questions before BP3.",
            "General response.",
        ]
        digest_structure = [
            "USER BP2 disposition.",
            "Accepted BP2 line items.",
            "Revised BP2 line items.",
            "Rejected or deferred ideas.",
            "Implementation constraints created from USER response.",
            "Source-truth updates required.",
            "Review packet updates required.",
            "Whether BP3 may begin.",
            "Next USER decision needed.",
        ]
        if workstream_package_approval_packet:
            accepted_user_response = (
                "BP1, BP2, and BP3 accepted - USER accepted the repaired FAM-007 "
                "Owner AI Operational Foundation Gates Branch Vision, accepted the "
                "engineering Branch Plan, and accepted BP3 Workstream Entry / "
                "Orchestration Validation for the complete public-safe SLC-001 "
                "through SLC-006 package."
            )
            user_response_text = (
                "Status: Accepted by USER for BP1/BP2/BP3. This BP2 support file "
                "now supports the complete bounded Workstream implementation approval "
                "packet for the accepted Owner AI Operational Foundation Gates package."
            )
            codex_response_digest = (
                "Codex digested accepted BP1, accepted BP2, and accepted BP3 into "
                "Workstream approval context. The approval packet preserves all six "
                "Slice/SLC deliverables, all eighteen accepted seams, SLC-001 / Seam "
                "1 as the entry checkpoint, and every future-gated private/runtime/"
                "provider/cache/memory boundary."
            )
            workstream_entry_result = (
                "Implementation-ready packet - BP1, BP2, and BP3 are accepted; "
                "USER is reviewing complete bounded Workstream implementation for "
                "the same-branch Owner AI Operational Foundation Gates package with "
                "SLC-001 / Seam 1 as the entry checkpoint."
            )
            contract_status = (
                "Complete - USER accepted the BP2 Branch Plan Contract; BP3 is "
                "accepted; this file is supporting context for the complete bounded "
                "Workstream implementation approval packet."
            )
            contract_version = (
                "v5 - accepted BP1/BP2/BP3 digested into FAM-007 Owner AI "
                "Operational Foundation Gates Workstream approval support context."
            )
            plain_english_summary = (
                "This support file records the accepted engineering plan for the "
                "FAM-007 Owner AI Operational Foundation Gates carrier. The active "
                "packet asks USER whether Codex may execute the complete accepted "
                "public-safe Workstream package: SLC-001 through SLC-006, all "
                "eighteen accepted seams, starting at SLC-001 / Seam 1 - Define "
                "protected classes and public-safe exclusion contract."
            )
            end_state_vision = (
                "When the approval is accepted, Workstream should implement or "
                "enforce public-safe controls for protected artifact exclusion, "
                "provider/runtime disabled states, cache-versus-memory consent, "
                "capability install intent, Developer/Owner lane readiness, and "
                "Owner AI memory/agent prerequisite schemas without creating private "
                "roots/remotes, executing providers/models, activating cache or "
                "memory, or running real Owner agents."
            )
            what_user_sees = (
                "The primary decision file is USER Review/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md. "
                "This BP2 file remains a Review Aids support file showing the accepted "
                "engineering plan, SLC/seam order, affected surfaces, validators, "
                "proof requirements, rollback posture, and future-gated boundaries "
                "that Workstream execution must follow."
            )
            walkthrough = [
                "Open USER Review/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md first and confirm the complete bounded Workstream package.",
                "Check that SLC-001 / Seam 1 is the entry checkpoint, not the terminal scope.",
                "Confirm SLC-001 through SLC-006 and all eighteen seams remain in order.",
                "Confirm private setup, provider/model/runtime/cache/memory activation, real Owner memory, real agents, PR, merge, release, cleanup, issue mutation, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 remain future-gated.",
            ]
            implementation_options = [
                "Approve complete bounded Workstream implementation as recommended.",
                "Approve with a revised seam order or proof requirement.",
                "Waive a specific unresolved Workstream approval question and proceed under the accepted package constraints.",
                "Hold the branch before Workstream execution.",
                "Reject or route back to BP3/BP2 if the accepted orchestration or plan needs repair.",
            ]
            recommended_direction = (
                "Codex recommends approving the complete bounded Workstream package "
                "only if USER agrees the accepted BP1/BP2/BP3 contracts still govern, "
                "SLC-001 / Seam 1 is the first execution checkpoint, and later "
                "Workstream execution continues through the accepted SLC/seam order "
                "until Workstream Green, a real named blocker, validation failure "
                "requiring route-back, or explicit USER waiver."
            )
            current_scope = [
                "Complete bounded Workstream implementation approval packet generation for FAM-007 Owner AI Operational Foundation Gates.",
                "Accepted BP1, accepted BP2, and accepted BP3 traceability proof.",
                "Executable Workstream scope, if USER accepts this approval packet: SLC-001 through SLC-006 and all eighteen accepted seams in the approved sequence.",
                "Entry checkpoint: SLC-001 / Seam 1 - Define protected classes and public-safe exclusion contract.",
            ]
            future_scope = [
                "Hardening, Live Validation, PR Readiness, PR creation, merge, release, cleanup, issue mutation, sibling-worktree mutation, and v1.8.0 remain later USER-gated phases.",
                "Private Developer setup, Owner setup, private repo/root/remote creation, GitHub Desktop private binding, backup/import execution, provider/model/runtime/cache/memory activation, real Owner memory, real agents, AI Product Contract import, and Private Dev ORIN import remain future-gated.",
            ]
            user_decisions = [
                "Does USER approve complete bounded Workstream implementation for SLC-001 through SLC-006 and all eighteen accepted seams?",
                "Does USER agree execution starts at SLC-001 / Seam 1 - Define protected classes and public-safe exclusion contract?",
                "Does USER want any seam-order, validator, proof, rollback, H1, LV/UTS, or stop-condition revision before implementation?",
                "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release/cleanup gates remain future-gated?",
            ]
            user_decisions_intro = (
                "USER is reviewing Workstream approval now. Useful feedback names "
                "approval, revision, waiver, hold, rejection, or route-back before "
                "any Workstream execution starts."
            )
            design_ballot = [
                "Approve complete bounded Workstream implementation.",
                "Request a Workstream approval packet revision.",
                "Waive a specific Workstream approval issue.",
                "Hold before Workstream execution.",
                "Reject or route back to BP3/BP2.",
            ]
            response_structure = [
                "Decision: approve, revise, waive, hold, reject, or route back.",
                "Scope or seam-order changes, if any.",
                "Proof, validator, rollback, H1, LV/UTS, or stop-condition changes, if any.",
                "Future-gated boundary confirmations.",
                "General response.",
            ]
            digest_structure = [
                "USER Workstream approval disposition.",
                "Accepted or revised SLC/seam sequence.",
                "Approved entry checkpoint and continuation constraints.",
                "Implementation constraints created by USER response.",
                "Source-truth, external-state, packet, helper, validator, or fixture updates required.",
                "Next USER decision needed.",
            ]
            implementation_constraints = [
                "Workstream execution may start only after USER accepts this Workstream approval packet.",
                "Execution starts at SLC-001 / Seam 1 - Define protected classes and public-safe exclusion contract.",
                "Later execution continues one active same-branch seam at a time through all eighteen accepted seams until Workstream Green, a real named blocker, validation failure requiring repair or route-back, or explicit USER waiver.",
                "No private setup, provider/model/runtime/cache/memory activation, real Owner memory, real agents, PR, merge, release, cleanup, issue mutation, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is included.",
            ]
            rejected_deferred = [
                "Deferred: private Developer lane setup, Owner lane setup, private repos/roots/remotes, GitHub Desktop private binding, backup/import execution, model downloads, provider setup, runtime activation, cache/memory activation, real Owner memory, and real Owner agents.",
                "Deferred: PR creation, merge, release, cleanup, issue mutation, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
            ]
            source_truth_impact = [
                "Accepted BP1/BP2/BP3 remain the Workstream implementation route authority for this branch.",
                "External branch/worktree state records active packet pointers and mutable posture outside repo-tracked live ledgers.",
                "Durable repo owners retain public-safe source truth, helper/validator behavior, fixtures, and historical receipts only.",
            ]
            completion_checklist = [
                "BP1 Branch Vision is accepted or waived.",
                "BP2 Branch Plan is accepted or waived.",
                "BP3 Workstream Entry / Orchestration Validation is accepted or waived.",
                "SLC-001 through SLC-006 trace to accepted BP1 and accepted BP2.",
                "All eighteen accepted seams trace to BP3 orchestration.",
                "SLC-001 / Seam 1 is named as the first execution checkpoint.",
                "Future-gated private/runtime/provider/cache/memory boundaries are preserved.",
            ]
    if is_fam007_dev_owner_skeleton and not is_fam007_breakpoint_2:
        plain_english_summary = (
            "This BP2 preview is future-gated until USER accepts or explicitly waives BP1. "
            "If BP1 is accepted, BP2 should plan the public-safe Dev/Owner skeleton readiness "
            "package: Dev readiness, Owner readiness, private root and remote decisions, "
            "public-upstream safety, backup/import deferral, provider/model/runtime/cache/memory "
            "deferral, review-packet proof, and direct validator coverage."
        )
        end_state_vision = (
            "When BP2 is later accepted or waived, USER should understand which public-safe "
            "source-truth, helper, fixture, validator, packet, H1, LV/UTS, rollback, and proof "
            "surfaces will prepare future Dev/Owner skeleton setup while every private/runtime "
            "action remains separately gated."
        )
        what_user_sees = (
            "USER should see a branch-specific engineering plan derived from the accepted BP1 "
            "Dev/Owner skeleton readiness vision, not a Governance PR Readiness plan and not "
            "private setup. The BP2 packet should name the exact future readiness seams and the "
            "proof expected before implementation."
        )
        why_nexus = (
            "This fits Nexus because it keeps AI-edition growth local-first, visible, and "
            "permission-gated. The public branch plans decision and proof surfaces while private "
            "Dev/Owner roots, provider/model behavior, cache behavior, memory, and promotion back "
            "to Main stay under explicit USER control."
        )
        implementation_constraints = [
            "BP2 is pending until BP1 is accepted or explicitly waived.",
            "BP2 may plan public-safe source-truth, fixture, validator, helper, packet, and proof surfaces only.",
            "Private Dev repo creation, Owner repo creation, local-only roots, private remotes, GitHub Desktop private binding, backup/import behavior, provider/model execution, runtime cache behavior, memory behavior, PR, merge, release, cleanup, and v1.8.0 work remain future USER decisions.",
            "Provider-visible data must remain none; sentToProvider=false, canAcceptPrompts=false, prompt/provider/model execution disabled, downloads/network/external calls blocked, memory/learning/personalization inactive, and runtime cache behavior inactive.",
        ]
        rejected_deferred = [
            "Deferred: actual private Dev skeleton setup and Owner skeleton setup.",
            "Deferred: private repo/root/remote creation, GitHub Desktop private binding, backup/import execution, and Public-to-Dev import.",
            "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
        ]
        source_truth_impact = [
            "FAM-007 family vision and AI runtime/trust architecture remain the durable policy context.",
            "The FAM-007 branch record and external branch plan remain the branch-specific planning owners.",
            "BP2 must fold any USER revision that changes edition boundaries, private/public promotion, provider/cache/memory policy, or proof expectations into the proper source-truth owner before BP3.",
        ]
        contract_change_log = [
            "v1 - BR2 admitted the FAM-007 Dev/Owner Skeleton Readiness carrier.",
            "v2 - BP1 packet generated as Branch Vision Review with BP2 remaining future-gated.",
            "v3 - BP1 primary vision file repaired into applied FAM-007 Dev/Owner readiness content.",
        ]
        completion_checklist = [
            "BP1 is accepted or explicitly waived before BP2 is treated as a plan gate.",
            "Accepted BP1 trace is present.",
            "Implementation package summary names Dev readiness, Owner readiness, private root/remote gates, public-upstream safety, backup/import deferral, provider/model/runtime/cache/memory deferral, validation proof, packet proof, H1, LV/UTS, and rollback/safety expectations.",
            "All private/runtime/provider/cache/memory/PR/merge/release/cleanup boundaries remain pending USER decisions.",
            "BP3 / Workstream Entry remains blocked until BP2 is accepted or explicitly waived and orchestration validation is green.",
        ]
        walkthrough = [
            "Review accepted BP1 first; this BP2 preview cannot become green while BP1 is pending.",
            "Confirm whether BP2 should keep Dev and Owner skeleton readiness in one public-safe branch.",
            "Confirm which private root, private remote, GitHub Desktop, backup/import, provider/cache/memory, and public-to-private promotion decisions need matrix proof.",
            "Confirm the required no-leak, provider-state, packet, fixture, validator, H1, and LV/UTS proof before implementation.",
        ]
        surface_map = [
            "USER packet: BP1 primary vision file now; future BP2 engineering plan only after BP1 acceptance or waiver.",
            "Branch record and external branch plan: branch-specific FAM-007 readiness authority and planning owners.",
            "FAM-007 family vision and AI runtime/trust architecture: provider, model, cache, memory, permission, and public/private boundary owners.",
            "Validation surfaces: public leak-prevention, provider-state, branch-planning fixture validation, packet validation, and branch governance validation.",
            "Future proof surfaces: H1 implementation-vs-plan comparison, Live Validation or UTS waiver/proof, and PR Readiness only after later approvals.",
        ]
        implementation_options = [
            "Option A - Plan one public-safe Dev/Owner readiness package in BP2. Pros: keeps coupled trust-boundary gates consistent; Cons: broader BP2; Risk: low when all private/runtime actions stay gated.",
            "Option B - Split Dev and Owner readiness after BP1. Pros: smaller future packets; Cons: higher risk of inconsistent private/public gates; Risk: medium unless USER wants different timelines.",
            "Option C - Plan only an action-gate registry first. Pros: narrowest engineering scope; Cons: delays Dev/Owner skeleton readiness detail; Risk: low but less useful.",
            "Option D - Require BP2 to include a full decision matrix and proof map. Pros: strongest USER clarity; Cons: more planning detail before Workstream; Risk: low.",
        ]
        recommended_direction = (
            "Codex recommends Option A with the Option D decision matrix: keep Dev and Owner "
            "readiness together for BP2, require explicit proof for each private/runtime gate, and "
            "leave actual setup or execution for later USER-approved phases."
        )
        current_scope = [
            "BP1 Branch Vision Review is the current USER decision.",
            "BP2 content in this packet is preview/context only and cannot close the BP2 gate.",
            "The branch remains public-safe and does not create private roots, remotes, provider behavior, cache behavior, memory, or runtime work.",
        ]
        future_scope = [
            "BP2 should plan Dev readiness, Owner readiness, private root/remote gates, public-upstream safety, backup/import deferral, provider/model/runtime/cache/memory deferral, proof requirements, H1, LV/UTS, and rollback/safety.",
            "BP3, Workstream implementation, private setup, provider/model/runtime/cache/memory behavior, PR, merge, release, cleanup, and v1.8.0 remain pending USER decisions.",
        ]
        slc_package_plan = [
            "SLCs remain future engineering route details inside the accepted branch vision.",
            "Candidate future seam families: Dev skeleton readiness, Owner skeleton readiness, private remote/public-upstream safety, backup/import deferral, and provider/model/runtime/cache/memory deferral.",
            "No future seam may execute the private/runtime action it is proving as gated without a separate USER approval.",
        ]
        user_decisions = [
            "Does USER accept, revise, waive, reject, or hold the BP1 Dev/Owner skeleton readiness Branch Vision?",
            "If BP1 is accepted or waived, should BP2 plan one combined Dev/Owner readiness package or split Dev and Owner later?",
            "Which private root, private remote, GitHub Desktop, backup/import, provider/cache/memory, and public-to-private promotion decisions must BP2 prove?",
            "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
        ]
    if (
        is_fam007_dev_owner_skeleton
        and not is_fam007_breakpoint_2
        and (bp2_branch_plan_packet or bp3_orchestration_packet)
    ):
        accepted_user_response = (
            "BP1 accepted - USER accepted the updated FAM-007 Dev/Owner Skeleton "
            "Readiness Branch Vision as the integrated Option A direction. BP2 may "
            "plan Dev and Owner readiness together, with future Dev oriented toward "
            "a private repo after approval, Owner kept local-private by default, "
            "GitHub Desktop/public-upstream safety made explicit, backup/import "
            "timing planned, provider/runtime/cache/memory behavior deferred, and "
            "lane identity labels carried into proof expectations."
        )
        user_response_text = (
            "Status: Pending USER Response - this BP2 engineering plan is ready for "
            "USER to accept, revise, hold for more options, reject, or explicitly "
            "waive. BP3 and Workstream implementation remain blocked until that "
            "USER disposition is recorded and digested."
        )
        codex_response_digest = (
            "Codex digested the accepted BP1 vision into a BP2 engineering plan. "
            "The plan keeps Dev and Owner skeleton readiness in one public-safe "
            "package, names matrix proof for each private/runtime gate, and keeps "
            "all setup or execution work future-gated until later USER approval."
        )
        workstream_entry_result = (
            "BP3 not started - Workstream Entry / Orchestration Validation remains "
            "pending until USER accepts or explicitly waives this BP2 plan."
        )
        contract_status = (
            "Pending USER Response - USER must accept, revise, reject, request more "
            "options, hold, or explicitly waive this BP2 engineering plan before BP3."
        )
        contract_version = (
            "v5 - USER/ChatGPT BP2 review conditions digested into the integrated "
            "Dev/Owner readiness engineering plan."
        )
        plain_english_summary = (
            "This BP2 plan keeps the selected route as integrated Dev/Owner Skeleton "
            "Readiness and turns the accepted BP1 vision into a public-safe engineering "
            "route. Dev continues toward future private-repo readiness after approval. "
            "Owner defaults to local Git/version history plus local/private/encrypted "
            "rollback, with an Owner private remote only as a future evaluated option. "
            "The branch plans decision and proof surfaces without creating private repos, "
            "private roots, private remotes, GitHub Desktop private binding, backup/import "
            "execution, provider or model execution, cache behavior, memory behavior, PRs, "
            "merges, releases, or cleanup."
        )
        end_state_vision = (
            "When the BP2 plan is accepted and later implemented through approved phases, "
            "USER should have durable source truth, direct validators, fixtures, packet "
            "proof, and no-leak evidence that make future Dev and Owner skeleton setup "
            "decision-ready. The public branch should say which lane owns each decision, "
            "which files or validators prove it, how rollback works, and which future "
            "USER gate is required before any private or runtime action starts."
        )
        what_user_sees = (
            "USER will inspect one primary BP2 decision file under the local USER hub. "
            "It describes the integrated Dev/Owner implementation package, seam plan, "
            "likely future edit/proof surfaces, named validator lanes, backup/import "
            "planning by lane, watermark/identity propagation, rollback plan, risks, "
            "options, and exact BP3 approval text. It is not a private setup script, "
            "not backup/import execution, and not a Workstream implementation approval."
        )
        why_nexus = (
            "This fits Nexus because Dev/Owner AI-edition readiness is a trust-boundary "
            "problem. Planning Dev, Owner, remotes, backups, provider deferral, cache "
            "deferral, memory deferral, and lane identity together keeps the public repo "
            "local-first, inspectable, and USER-controlled while preventing accidental "
            "private or provider-facing activation."
        )
        slc_package_plan = [
            "Seam 1 - action-gate registry and exact USER decision proof: record every future private/runtime action gate and make the BP2/BP3 approval text machine-checkable.",
            "Seam 2 - Dev/Owner readiness matrices: encode Dev private-repo readiness after approval, Owner local Git/version history plus local/private/encrypted rollback as the default baseline, Owner private remote evaluation as optional future work, and public-safe lane boundaries.",
            "Seam 3 - private root/remote and GitHub Desktop safety proof: plan public-upstream, private origin, remote identity proof, fetch/reconcile posture, and public push-prevention checks without configuring remotes or binding GitHub Desktop to a private repo.",
            "Seam 4 - backup/import and provider/runtime deferral proof: plan User/Public settings/preferences/config backup scope, Dev private development recovery, Owner local/private/encrypted backup and rollback, restore proof, and provider-visible-data/cache/memory inactivity proof.",
            "Seam 5 - packet, fixture, validator, and fold-down proof: refresh USER review packet evidence, add direct fixtures where needed, and update source-truth owners only inside approved public-safe scope.",
        ]
        surface_map = [
            "FAM-007 repo branch record receipt: durable branch identity and historical context only; active BP2 posture and future-gate tracking live in external operational state.",
            "Active FAM-007 branch plan/receipt and external FAM-007 branch plan/state: active BP2 planning posture, accepted BP1 trace, review-gate state, seam map, proof expectations, and future gates.",
            "USER review bundle helper: packet layout, primary BP2 decision-file routing, support-file phase state, timestamped ZIP creation, placeholder scans, packet count checks, and USER-facing metadata exclusion when packet behavior changes.",
            "Validation helper registry and branch-readiness planning fixtures: reusable proof lanes and false-green prevention when validator coverage changes.",
            "Provider-state, public leak-prevention, external-state, source-owner, USER review packet, and branch-governance validators: named proof lanes for BP3 and later Workstream decisions.",
            "AI runtime/trust architecture: durable trust-boundary wording only if USER changes provider-visible data, prompt acceptance, provider execution, downloads, cache, memory, learning, or personalization policy.",
            "FAM-007 family vision files: family-level direction only if USER changes Public/Dev/Owner edition strategy, capability-pack policy, private/public promotion, or lane identity standards.",
        ]
        likely_files_lines = [
            "FAM-007 repo branch record receipt only if durable historical context or accepted-gate receipt wording changes.",
            "Active FAM-007 external branch plan and branch state for BP2 review posture, accepted BP1 trace, USER response digestion, and next-gate routing.",
            "Review bundle helper if packet behavior, timestamped ZIP generation, support-file phase state, or primary BP2 routing changes.",
            "Validation helper registry if reusable validator/helper coverage changes.",
            "Branch-readiness planning fixtures for accepted BP1 trace, BP2 engineering-plan substance, BP3 blocking while BP2 remains pending, and future root/remote/GitHub Desktop matrix false-green coverage if needed.",
            "Provider-state and public leak-prevention validators/fixtures for no provider execution, no private artifacts, no private paths, and no private remotes.",
            "External-state validation for active branch plan/state consistency.",
            "Source-owner marker validation for any durable source-truth owner touched by later implementation.",
            "AI runtime/trust architecture only if durable provider/cache/memory trust-boundary policy changes.",
            "FAM-007 family vision files only if USER changes family-level edition, private/public, capability-pack, or lane identity direction.",
        ]
        active_branch_files = [
            "Active external branch plan exists at C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_plan.md; it owns active BP2 planning posture, accepted BP1 trace, review-gate state, seam map, proof expectations, and future gates outside the USER-facing packet.",
            "Active external branch state exists at C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_state.md; it records the current carrier posture and packet pointer outside repo-tracked source truth.",
            "Historical repo branch record remains Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md; it is durable receipt/context and not active authority or a mutable live-state ledger.",
        ]
        user_decisions_intro = (
            "USER may answer in order or respond generally. Useful BP2 feedback includes "
            "Dev/Owner matrix changes, private root or remote posture, GitHub Desktop "
            "binding assumptions, backup/import lane split, watermark/identity "
            "propagation, named proof lanes, future-gated actions, or anything that "
            "would make this FAM-007 Dev/Owner engineering plan wrong before BP3."
        )
        walkthrough = [
            "Open the primary BP2 file and confirm the accepted BP1 Option A trace matches the integrated Dev/Owner readiness direction.",
            "Review the seam plan from action-gate registry through matrix proof, root/remote safety, backup/import deferral, provider/runtime deferral, and packet/validator proof.",
            "Review each matrix and mark any lane, future gate, proof expectation, or rollback rule that needs revision before BP3.",
            "Confirm that the plan stays public-safe and prepares proof only; any private setup or runtime action remains a later USER gate.",
            "Choose accept, revise, route back to BP1, waive, reject, or hold for more examples before BP3.",
        ]
        implementation_options = [
            "Option A - accept the integrated Dev/Owner BP2 plan as written. Pros: keeps coupled private/public trust decisions in one branch; Cons: broader BP2 and BP3 review; Risk: low when all private/runtime actions stay gated.",
            "Option B - accept with changes to a specific matrix or seam. Pros: tunes the plan before BP3; Cons: requires packet/source-truth refresh; Risk: low.",
            "Option C - route back to BP1. Pros: safest if the engineering plan changes the accepted vision; Cons: delays BP3; Risk: low.",
            "Option D - split Dev and Owner into separate future branches. Pros: smaller packages; Cons: higher risk of inconsistent remote, backup, provider, and identity gates; Risk: medium.",
            "Option E - explicitly waive BP2 details and proceed to BP3. Pros: faster; Cons: accepts less planning detail; Risk: medium to high for private-boundary work.",
            "Option F - hold for more examples or proof models. Pros: improves confidence; Cons: delays implementation; Risk: low.",
        ]
        recommended_direction = (
            "Codex recommends accepting the integrated Dev/Owner readiness route after "
            "reviewing the strengthened proof lanes: keep Dev private-repo readiness as "
            "the future direction, keep Owner local Git/version history plus "
            "local/private/encrypted rollback as the default baseline, treat Owner remote "
            "as future evaluated only, require named validator/fixture proof before BP3, "
            "and keep actual private setup, GitHub Desktop private binding, provider/model "
            "work, backup/import execution, cache, memory, PR, merge, release, and cleanup "
            "under later gates."
        )
        current_scope = [
            "Public-safe source-truth, helper, fixture, validator, packet, and proof planning only.",
            "Accepted BP1 trace, BP2 engineering package, seam/SLC route, affected surfaces, proof expectations, H1/LV/UTS expectations, rollback, risks, and exact BP3 approval text.",
            "No private repo, private root, private remote, GitHub Desktop private binding, backup/import execution, provider/model execution, cache behavior, memory behavior, PR, merge, release, cleanup, or sibling-worktree mutation.",
        ]
        future_scope = [
            "BP3 Workstream Entry / Orchestration Validation after BP2 acceptance or waiver.",
            "Workstream implementation only after BP1 and BP2 are accepted or waived, BP3 is green or waived, and USER separately approves bounded Workstream execution for the admitted same-branch package or explicitly named initial seam sequence.",
            "Private Dev skeleton setup, Owner skeleton setup, private repos, private roots, private remotes, GitHub Desktop private binding, backup/import execution, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, issue mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain later USER decisions.",
        ]
        implementation_constraints = [
            "BP2 may plan public-safe source-truth, helper, fixture, validator, packet, H1, LV/UTS, rollback, and proof surfaces.",
            "BP2 may not execute the private/runtime actions it describes as future gates.",
            "BP2 may not create private repos, private roots, private remotes, GitHub Desktop private binding, backup/import execution, provider/model/runtime/cache/memory behavior, or Dev launcher/assets migration execution.",
            "Provider-visible data remains none; sentToProvider=false; canAcceptPrompts=false; prompt/provider/model execution remains disabled; downloads/network/external calls remain blocked; runtime cache behavior remains inactive; memory/learning/personalization remains inactive.",
            "Any USER change that alters edition boundaries, public-to-private promotion, provider/cache/memory policy, or reusable lane identity must fold into the proper durable source-truth owner before BP3 relies on it.",
        ]
        rejected_deferred = [
            "Deferred: private Dev skeleton setup, private Owner skeleton setup, private Dev repo creation, private Owner repo or remote creation, local-only private roots, private remotes, and GitHub Desktop private binding.",
            "Deferred: dev launcher/assets/tool transfer, recreation, removal from User/Public, or import into a private Dev path.",
            "Deferred: backup/import execution, public-to-private import, User/Public backup implementation, Dev recovery implementation, Owner encrypted recovery or rollback implementation.",
            "Deferred: provider SDKs, model downloads, provider/model execution, runtime provider execution, cache behavior, memory, learning, indexing, retrieval, personalization, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, issue mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work.",
        ]
        source_truth_impact = [
            "External branch plan should record BP1 accepted and BP2 pending review as active planning posture.",
            "Branch record remains durable authority/history and should not become a mutable live ledger.",
            "FAM-007 family vision and AI runtime/trust architecture remain reusable policy owners; accepted reusable changes route there only if USER changes family-level policy.",
            "Review packet is a temporary USER review aid; accepted BP2 outcomes later fold into durable repo owners or approved external operational state.",
        ]
        contract_change_log = [
            "v1 - BR2 admitted the FAM-007 Dev/Owner Skeleton Readiness carrier.",
            "v2 - BP1 packet generated as Branch Vision Review.",
            "v3 - BP1 repaired into applied integrated Dev/Owner Option A vision.",
            "v4 - USER accepted BP1; BP2 generated as engineering-plan-first review with required matrices and future-gated boundaries.",
            "v5 - USER/ChatGPT BP2 review conditions digested: strengthened future edit/proof surfaces, named validator lanes, backup/import lane details, Owner rollback baseline, Owner remote evaluation boundary, and watermark/identity propagation.",
        ]
        completion_checklist = [
            "Accepted BP1 Option A trace is present.",
            "BP2 implementation package summary, branch scope size test, seams/SLCs, affected surfaces, likely files, validators/helpers, proof requirements, H1/LV/UTS expectations, rollback/safety plan, risks, future gates, and exact BP3 approval text are present.",
            "Edition/Lane, Dev Readiness, Owner Readiness, Private Root/Remote, GitHub Desktop, Backup/Import, Provider/Runtime/Cache/Memory, Watermark/Identity, Proof/Validation, and Future USER Gate matrices are present.",
            "USER-facing files avoid live operational ledgers, raw commit values, upload byte-proof values, mutable validator run state, live pull-request posture, and command-wall boundary wording.",
            "BP3 and Workstream implementation remain blocked until BP2 is accepted or explicitly waived and later gates are green and approved.",
        ]
        user_decisions = [
            "Does USER accept the updated integrated Dev/Owner BP2 engineering plan as written?",
            "Does any listed future implementation/edit surface need to be added, removed, or narrowed before BP3?",
            "Are the named proof lanes sufficient for BP3: provider-state, public leak-prevention, external-state, branch-readiness planning fixtures, USER review packet validation, source-owner marker validation, and future root/remote/GitHub Desktop false-green fixture coverage if needed?",
            "Does USER accept Owner local Git/version history plus local/private/encrypted rollback as the default baseline, with Owner private remote only as a future evaluated option?",
            "Does USER accept the backup/import lane split and watermark/identity propagation requirements as BP2 planning constraints?",
            "Does USER confirm all private/runtime/provider/cache/memory/backup-import-execution/PR/merge/release gates remain pending?",
        ]
        design_ballot = [
            "Accept BP2 as written and authorize BP3 Workstream Entry / Orchestration Validation only.",
            "Accept BP2 with listed changes, then regenerate the BP2 packet for confirmation.",
            "Route back to BP1 because the plan changes the accepted vision.",
            "Explicitly waive remaining BP2 questions and authorize BP3 only.",
            "Reject this branch plan and request a narrower or different carrier.",
            "Hold for more examples, risks, or proof models.",
        ]
        response_structure = [
            "Decision: accept, revise, route back to BP1, waive, reject, or hold.",
            "Matrix or seam changes requested.",
            "Must-have proof requirements.",
            "Future-gated boundary controls.",
            "Questions before BP3.",
            "General response.",
        ]
        digest_structure = [
            "USER BP2 disposition.",
            "Accepted BP2 line items.",
            "Revised BP2 line items.",
            "Rejected or deferred ideas.",
            "Implementation constraints created from USER response.",
            "Source-truth updates required.",
            "Review packet updates required.",
            "Whether BP3 may begin.",
            "Next USER decision needed.",
        ]
        extra_plan_sections = [
            "## Integrated Dev/Owner Readiness Matrix",
            "",
            "| Lane | BP2 planned outcome | Current branch scope | Future USER gate | Proof needed |",
            "| --- | --- | --- | --- | --- |",
            "| Dev | Future private-repo-oriented readiness with public-upstream safety and dev asset inventory planning. | Public-safe plan, fixtures, validators, and review proof only. | Private Dev repo/root/remote creation and GitHub Desktop binding. | Action-gate registry, no-leak scan, public-upstream push-prevention plan, and fixture coverage. |",
            "| Owner | Local-private baseline with local Git/version history, no public exposure, and no default remote. | Public-safe plan and proof of gated Owner choices only. | Owner private root/remote choice, encrypted recovery, and any remote evaluation. | Matrix proof, no private path/remote/token leakage, rollback plan, and future-gate wording. |",
            "",
            "## Edition / Lane Matrix",
            "",
            "| Edition / Lane | Identity posture | Source control posture | Public branch role | Future boundary |",
            "| --- | --- | --- | --- | --- |",
            "| User/Public | Nexus Desktop AI or Nexus Desktop AI - Pre-Beta. | Normal public repo posture. | Keep public-safe product and proof context. | No private assets or provider execution. |",
            "| Dev | Nexus Desktop AI - DEV PRIVATE after approval. | Future private Dev repo with fetch-only public-upstream plan. | Plan readiness and gates only. | Repo/root/remote creation remains future-gated. |",
            "| Owner | Nexus Owner - Local Private unless later revised. | Local Git/version-history baseline; no default remote. | Plan Owner privacy gates only. | Remote or shared backup model remains future-gated. |",
            "",
            "## Dev Readiness Matrix",
            "",
            "| Dev item | BP2 plan | Likely proof | Future USER decision |",
            "| --- | --- | --- | --- |",
            "| Private Dev repo direction | Treat as preferred future path after approval. | Branch plan row and gate registry. | Create private Dev repo/root/remote. |",
            "| Dev launcher/assets/tools inventory | Classify transfer, recreation, removal, or future import candidates. | Public-safe inventory schema or fixture; no private paths. | Execute transfer/import/removal. |",
            "| Public-upstream relationship | Plan fetch/reconcile from public Main and public push prevention. | Validator fixture and packet proof. | Configure private remotes or GitHub Desktop binding. |",
            "",
            "## Owner Readiness Matrix",
            "",
            "| Owner item | BP2 plan | Likely proof | Future USER decision |",
            "| --- | --- | --- | --- |",
            "| Local Git/version history | Baseline Owner safety model. | Branch plan and H1 comparison. | Create Owner root or repo. |",
            "| No public exposure path | Preserve Owner-private boundary. | Public leak-prevention and no private artifact checks. | Any Owner remote or sharing path. |",
            "| Optional private Owner remote | Evaluate only if BP2/BP3 prove it safer than local-only. | Risk matrix and explicit future gate. | Configure Owner private remote. |",
            "",
            "## Private Root / Remote Matrix",
            "",
            "| Surface | Current branch scope | Future gate | Proof / validation |",
            "| --- | --- | --- | --- |",
            "| Private roots | Plan labels and constraints only. | Local-only private root creation. | No private path leakage and gate registry row. |",
            "| Private origin | Plan naming and safety posture only. | Private remote configuration. | Remote identity proof plan and public push-prevention fixture. |",
            "| Public-upstream | Plan fetch-only relationship. | Actual private repo configuration. | Public/upstream terminology checks and no private URL output. |",
            "",
            "## GitHub Desktop Binding Matrix",
            "",
            "| Lane | Default posture | BP2 plan | Future gate |",
            "| --- | --- | --- | --- |",
            "| User/Public | Public repo binding. | Preserve normal binding. | None in BP2. |",
            "| Dev | No binding yet. | Plan private Dev binding proof and safeguards. | GitHub Desktop private remote configuration. |",
            "| Owner | Local Git/no remote baseline. | Evaluate private remote only as future option. | Owner private binding approval. |",
            "",
            "## Backup / Import Matrix",
            "",
            "| Lane | BP2 plan | Current scope | Future gate | Restore / exclusion proof |",
            "| --- | --- | --- | --- | --- |",
            "| User/Public | Settings/preferences/config backup posture and product-safe export/import scope. | Plan and proof only. | Backup/import implementation. | Restore proof must use public-safe settings/config fixtures and exclude private Dev/Owner material. |",
            "| Dev | Private development recovery posture tied to the future private Dev repo relationship. | Plan and proof only. | Dev recovery implementation or Public-to-Dev import. | Dev backup material and private test fixtures must remain outside User/Public output and public review packets. |",
            "| Owner | Local/private/encrypted backup baseline plus local Git rollback expectation. | Plan and proof only. | Owner backup/recovery root execution or future remote evaluation. | Restore proof must preserve Owner-only privacy, stay outside User/Public and Dev, and define criteria before any Owner remote is evaluated. |",
            "",
            "## Provider / Runtime / Cache / Memory Deferral Matrix",
            "",
            "| Boundary | Required BP2 state | Proof |",
            "| --- | --- | --- |",
            "| Provider-visible data | none | Provider-state validator fixture. |",
            "| Prompt acceptance | canAcceptPrompts=false | Provider-state validator fixture. |",
            "| Provider/model execution | disabled | Provider-state and no network/download assertions. |",
            "| Runtime cache | inactive | Source-truth and fixture proof. |",
            "| Memory/learning/personalization | inactive | Memory/private artifact leak-prevention proof. |",
            "",
            "## Watermark / Identity Matrix",
            "",
            "| Artifact / surface | User/Public label | Dev label | Owner label | Propagation proof |",
            "| --- | --- | --- | --- | --- |",
            "| UI/window title | Nexus Desktop AI / Pre-Beta | Nexus Desktop AI - DEV PRIVATE after approval | Nexus Owner - Local Private after approval | UI proof or manifest row before any private lane UI exists. |",
            "| Launcher identity | Public launcher identity | Dev launcher identity after future setup | Owner local launcher identity after future setup | Launcher/shortcut manifest proof; no launcher migration execution in BP2. |",
            "| Diagnostics | Public-safe diagnostic labels | Dev-private diagnostic labels after approval | Owner-local diagnostic labels after approval | Diagnostic sample/fixture excludes private paths and secrets. |",
            "| Logs | Public-safe log labels | Dev-private log labels after approval | Owner-local log labels after approval | Log proof excludes private prompts, memory, tokens, and private paths. |",
            "| Screenshots/proof | Public-safe proof context | Dev proof only after future approval | Owner proof only after future approval | Review-proof labels show lane without exposing private artifacts. |",
            "| Review packets | Public FAM-007 packet labels | Dev packet labels only after future private approval | Owner packet labels only after future private approval | USER packet validation rejects private artifacts in public branch. |",
            "| Backup/export packages | Public-safe export label | Dev-private export label after approval | Owner-local/private export label after approval | Export manifest proof preserves lane and excludes cross-lane leakage. |",
            "| Generated manifests | Public-safe manifest owner | Dev-private manifest owner after approval | Owner-local manifest owner after approval | Manifest fixtures prove lane identity and future-gate state. |",
            "",
            "## Proof / Validation Matrix",
            "",
            "| Proof class | Required proof | Candidate validator/helper |",
            "| --- | --- | --- |",
            "| Branch planning packet | Primary BP2 file, timestamped ZIP, no stale preview text, no metadata drift. | dev/orin_user_review_bundle.py |",
            "| Private-boundary safety | No private path, token, remote URL, prompt, memory, model artifact, private automation, or private artifact in public branch. | dev/orin_public_leak_prevention_validation.py |",
            "| Provider deferral | Provider-visible data none, prompt/model execution disabled, downloads blocked, cache/memory inactive. | dev/orin_ai_provider_state_validation.py |",
            "| Planning gate proof | BP2 requires accepted BP1 trace; BP3 blocks while BP2 pending. | dev/orin_branch_readiness_planning_fixture_validation.py |",
            "| External-state consistency | External branch plan/state records BP2 reviewability and pending USER gate without making repo files live ledgers. | dev/orin_external_state_validation.py |",
            "| Source owner integrity | Any touched durable source-truth owner keeps valid ownership markers. | dev/orin_source_owner_marker_validation.py |",
            "| Future root/remote/GitHub Desktop matrix | Add false-green fixture coverage if BP3 or later implementation introduces root, remote, or GitHub Desktop proof rows. | dev/orin_branch_readiness_planning_fixture_validation.py |",
            "",
            "## Future USER Gate Matrix",
            "",
            "| Future gate | Required before action |",
            "| --- | --- |",
            "| BP3 | USER accepts, revises into confirmation, or explicitly waives BP2. |",
            "| Workstream implementation | BP1 and BP2 accepted or waived, BP3 green or waived, and separate bounded implementation approval. |",
            "| Private Dev / Owner setup | Separate USER approval naming root/repo/remote scope. |",
            "| Provider/model/cache/memory behavior | Separate USER approval plus provider-state proof. |",
            "| PR / merge / release / cleanup | Separate phase approvals after implementation, H1, and LV gates. |",
            "",
        ]
    if (
        is_fam007_dev_owner_skeleton
        and not is_fam007_breakpoint_2
        and (bp3_orchestration_packet or workstream_package_approval_packet)
    ):
        accepted_user_response = (
            "BP2 accepted - USER accepted the cleaned FAM-007 Dev/Owner Skeleton "
            "Readiness engineering plan. The accepted plan keeps Dev and Owner "
            "readiness together, points Dev toward future private-repo readiness "
            "after approval, keeps Owner local-private by default, evaluates any "
            "Owner private remote only as future work, and preserves every "
            "private/runtime/provider/cache/memory gate."
        )
        user_response_text = (
            "Status: Accepted by USER - this BP2 support file is closed as accepted "
            "engineering-plan context for the implementation-ready Workstream package "
            "approval packet."
            if workstream_package_approval_packet
            else
            "Status: Accepted by USER - this BP2 support file is closed as the "
            "accepted engineering-plan context for the active BP3 Workstream Entry / "
            "Orchestration Validation packet."
        )
        codex_response_digest = (
            "Codex digested USER BP2 acceptance through BP3 acceptance into Workstream "
            "package approval context. The accepted BP2 plan remains the engineering "
            "basis for the bounded same-branch Workstream package, with Seam 1 as "
            "the entry checkpoint and continuation governed until Workstream Green."
            if workstream_package_approval_packet
            else
            "Codex digested USER BP2 acceptance into BP3 readiness context. BP3 "
            "must verify that the accepted BP2 plan implements the accepted BP1 "
            "vision, that seams/SLCs trace to both contracts, and that Workstream "
            "implementation remains blocked until USER later approves a bounded seam."
        )
        workstream_entry_result = (
            "Implementation-ready - BP1, BP2, and BP3 are accepted; bounded "
            "Workstream package implementation is approved by this packet with "
            "Seam 1 as the entry checkpoint and continuation governed until "
            "Workstream Green, a real blocker, or explicit USER waiver."
            if workstream_package_approval_packet
            else
            "BP3 active - Workstream Entry / Orchestration Validation is the "
            "current review gate. BP3 may recommend the first bounded Workstream "
            "seam, but this packet does not authorize Workstream implementation."
        )
        contract_status = (
            "Complete - USER accepted the BP2 Branch Plan Contract; BP3 is accepted "
            "and this packet records bounded Workstream package implementation approval."
            if workstream_package_approval_packet
            else
            "Complete - USER accepted the BP2 Branch Plan Contract; BP3 is the "
            "active Workstream Entry / Orchestration Validation gate."
        )
        contract_version = (
            "v7 - BP2 acceptance digested through BP3 acceptance into Workstream "
            "implementation-ready support context."
            if workstream_package_approval_packet
            else
            "v6 - BP2 acceptance digested into BP3 orchestration-readiness support context."
        )
        plain_english_summary = (
            "This support file records the accepted BP2 engineering plan for the "
            "FAM-007 Dev/Owner Skeleton Readiness carrier. The active packet is "
            "implementation-ready: BP3 has been accepted and USER is approving the "
            "bounded same-branch Workstream package with Seam 1 as the entry checkpoint."
            if workstream_package_approval_packet
            else
            "This support file records the accepted BP2 engineering plan for the "
            "FAM-007 Dev/Owner Skeleton Readiness carrier. The active packet is BP3: "
            "it checks whether the accepted vision and accepted plan are ready to "
            "become a bounded Workstream implementation request later."
        )
        what_user_sees = (
            "The primary Workstream approval decision file lives under USER Review. "
            "This BP2 file is supporting context under Review Aids: it shows the "
            "accepted plan that the approved Workstream package must follow, including "
            "Dev/Owner readiness matrices, root/remote gates, GitHub Desktop safety, "
            "backup/import deferral, provider/runtime/cache/memory deferral, proof "
            "expectations, H1/LV/UTS expectations, and rollback posture."
            if workstream_package_approval_packet
            else
            "The primary BP3 decision file lives under USER Review. This BP2 file "
            "is supporting context under Review Aids: it shows the accepted plan "
            "that BP3 must trace, including Dev/Owner readiness matrices, root/remote "
            "gates, GitHub Desktop safety, backup/import deferral, provider/runtime/"
            "cache/memory deferral, proof expectations, H1/LV/UTS expectations, and "
            "rollback posture."
        )
        current_scope = [
            (
                "Bounded same-branch Workstream package implementation approval with "
                "Seam 1 as the entry checkpoint."
                if workstream_package_approval_packet
                else
                "BP3 Workstream Entry / Orchestration Validation packet generation and reviewability."
            ),
            "Accepted BP1 and accepted BP2 traceability proof.",
            (
                "Workstream continuation must proceed one active same-branch seam at a "
                "time until Workstream Green, a real blocker, or explicit USER waiver."
                if workstream_package_approval_packet
                else
                "Whole-package Workstream orchestration review only; no Workstream implementation."
            ),
        ]
        future_scope = [
            (
                "Hardening, Live Validation, PR, merge, release, cleanup, and any "
                "post-Workstream phase remain future USER-gated phases."
                if workstream_package_approval_packet
                else
                "Workstream implementation remains pending a later explicit USER decision after BP3 review."
            ),
            "Private Dev/Owner setup, private roots/remotes, GitHub Desktop private binding, backup/import execution, provider/model/runtime/cache/memory behavior, PR, merge, release, cleanup, sibling mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0 work remain future-gated.",
        ]
        user_decisions = [
            (
                "Does USER approve bounded Workstream package implementation with Seam 1 "
                "as the entry checkpoint and continuation until Workstream Green?"
                if workstream_package_approval_packet
                else
                "Does USER approve, revise, waive, reject, or hold BP3 Workstream Entry / Orchestration Validation?"
            ),
            "Does USER agree the accepted BP2 plan implements the accepted BP1 vision without changing the Dev/Owner direction?",
            (
                "Does USER agree Seam 1 starts the approved Workstream package rather "
                "than limiting the package to Seam 1 only?"
                if workstream_package_approval_packet
                else
                "Does USER agree Seam 1 should be the entry implementation checkpoint for the bounded Workstream package after separate Workstream approval?"
            ),
            "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
        ]
        completion_checklist = [
            "BP1 Contract Status is Complete or Waived by USER.",
            "BP2 Contract Status is Complete or Waived by USER.",
            (
                "BP3 is accepted or waived and Workstream package approval is recorded "
                "separately from BP3 reviewability."
                if workstream_package_approval_packet
                else
                "BP3 packet reviewability is Reviewable while BP3 USER approval remains pending."
            ),
            "Seam/SLC traceability to BP1 and BP2 is present.",
            (
                "Bounded Workstream package implementation is approved with Seam 1 as "
                "the entry checkpoint."
                if workstream_package_approval_packet
                else
                "Workstream implementation remains pending separate USER approval."
            ),
        ]
        implementation_options = [
            *(
                [
                    "Approve bounded Workstream package implementation as recommended.",
                    "Revise the entry checkpoint, seam order, or proof expectations before Workstream execution continues.",
                    "Waive unresolved Workstream approval questions and proceed under the accepted same-branch package constraints.",
                    "Reject or hold Workstream approval and keep the branch before implementation.",
                ]
                if workstream_package_approval_packet
                else
                [
                    "Approve BP3 as reviewable and green, then request the separate bounded Workstream package implementation approval packet with the entry seam named.",
                    "Revise BP3 orchestration order, proof expectations, or first-seam recommendation before implementation approval is considered.",
                    "Waive unresolved BP3 questions and proceed to a separate bounded Workstream approval packet.",
                    "Reject or hold BP3 and keep the branch in Branch Planning.",
                ]
            ),
        ]
        recommended_direction = (
            "Codex recommends approving the bounded Workstream package only if USER "
            "agrees BP3 is accepted, Seam 1 is the entry checkpoint rather than a "
            "terminal slice, and all private/runtime/provider/cache/memory actions "
            "remain future-gated."
            if workstream_package_approval_packet
            else
            "Codex recommends BP3 approval only if USER agrees the accepted BP2 plan "
            "faithfully implements BP1, the first Workstream seam starts with "
            "public-safe action-gate registry and exact USER decision proof, and all "
            "private/runtime/provider/cache/memory actions remain future-gated."
        )
        user_decisions_intro = (
            "USER is reviewing bounded Workstream package approval now. This support "
            "file confirms BP2 is accepted and BP3 is accepted; the active decision "
            "is whether Codex may execute the admitted same-branch Workstream package "
            "starting at Seam 1."
            if workstream_package_approval_packet
            else
            "USER is reviewing BP3 now. This support file confirms BP2 is accepted; "
            "the active decision is whether BP3 orchestration is correct before any "
            "later bounded Workstream approval is requested."
        )
        design_ballot = [
            *(
                [
                    "Approve bounded Workstream package implementation as recommended.",
                    "Approve Workstream package implementation with changes.",
                    "Revise the Workstream approval packet.",
                    "Waive unresolved Workstream approval questions.",
                    "Reject or hold Workstream approval.",
                ]
                if workstream_package_approval_packet
                else
                [
                    "Approve BP3 as recommended.",
                    "Approve BP3 with changes.",
                    "Revise BP3 and regenerate the packet.",
                    "Waive unresolved BP3 questions.",
                    "Reject or hold BP3.",
                ]
            ),
        ]
        response_structure = [
            (
                "Decision: approve, revise, waive, reject, or hold bounded Workstream package implementation."
                if workstream_package_approval_packet
                else
                "Decision: approve, revise, waive, reject, or hold BP3."
            ),
            "Required orchestration, seam, or proof changes, if any.",
            "First-seam preference or constraints.",
            "Future-gated boundary controls.",
            "General response.",
        ]
        digest_structure = [
            (
                "USER Workstream package approval disposition."
                if workstream_package_approval_packet
                else
                "USER BP3 disposition."
            ),
            "Accepted or revised orchestration and seam order.",
            (
                "Approved entry checkpoint and continuation constraints."
                if workstream_package_approval_packet
                else
                "First bounded Workstream seam approved for a later packet, if any."
            ),
            "Implementation constraints created by USER response.",
            "Source-truth or packet updates required.",
            "Next USER decision needed.",
        ]
    if is_fam007_dev_owner_skeleton and not is_fam007_breakpoint_2 and dev_owner_workstream_green_packet:
        accepted_user_response = (
            "BP1 accepted Option A for FAM-007 Dev/Owner Skeleton Readiness: Dev and "
            "Owner readiness stay planned together in one public-safe trust-boundary "
            "package, future Dev is private-repo-oriented after approval, Owner remains "
            "local-private by default, and GitHub Desktop/public-upstream safety, "
            "backup/import posture, provider/runtime/cache/memory deferral, proof "
            "expectations, and lane identity labels are required planning context. "
            "Workstream Green - USER approved the bounded Workstream package, and Codex "
            "completed the admitted public-safe proof seams without executing private "
            "setup or runtime behavior."
        )
        user_response_text = (
            "Status: Workstream Green - this packet asks USER to approve, revise, "
            "pause, or reject bounded Hardening H1 proof comparison only."
        )
        codex_response_digest = (
            "Codex implemented the public-safe FAM-007 Dev/Owner Skeleton Readiness "
            "Workstream proof package: action-gate registry and exact USER decision "
            "proof, Dev/Owner readiness matrices, private root/remote and GitHub "
            "Desktop safety proof, backup/import and provider/runtime/cache/memory "
            "deferral proof, plus packet, fixture, validator, and source-truth "
            "fold-down. All private/runtime/provider/cache/memory gates remain "
            "pending USER decisions. Codex recommends bounded Hardening H1 next."
        )
        workstream_entry_result = (
            "Workstream Green - all admitted public-safe same-branch proof seams "
            "are complete; Hardening H1 remains pending USER approval."
        )
        contract_status = (
            "Complete - Workstream Green for the FAM-007 Dev/Owner Skeleton "
            "Readiness public-safe proof package; Hardening H1 is the next legal "
            "USER decision."
        )
        contract_version = "v7 - Workstream implementation proof completed and routed to Hardening H1 approval."
        plain_english_summary = (
            "This branch has now completed the public-safe Workstream part of the "
            "Dev/Owner Skeleton Readiness plan. It proves that future Dev and Owner "
            "setup decisions are named, gated, and validator-backed, while private "
            "repos, private roots/remotes, backup/import execution, provider/model/"
            "runtime/cache/memory behavior, PR, merge, release, cleanup, and "
            "v1.8.0 remain blocked until later USER decisions."
        )
        what_user_sees = (
            "USER sees a Workstream Green handoff packet. It is not a private setup "
            "packet and not runtime proof; it is the public-safe proof package that "
            "makes Hardening H1 comparison possible."
        )
        why_nexus = (
            "This fits Nexus because Dev/Owner AI-edition readiness must be decision-ready "
            "and leak-safe before private roots, remotes, provider behavior, cache behavior, "
            "memory, backup/import, or release work can be trusted."
        )
        slc_package_plan = [
            "Seam 1 complete: action-gate registry and exact USER decision proof.",
            "Seam 2 complete: Dev/Owner readiness matrices.",
            "Seam 3 complete: private root/remote and GitHub Desktop safety proof.",
            "Seam 4 complete: backup/import and provider/runtime/cache/memory deferral proof.",
            "Seam 5 complete: packet, fixture, validator, and source-truth fold-down proof.",
            "Next phase is Hardening H1, limited to proof comparison and pressure testing after USER approval.",
        ]
        surface_map = [
            "Public leak-prevention fixture and validator: direct proof that all private/runtime gates remain pending and no protected material is present.",
            "FAM-007 branch record: durable Workstream completion receipt and Hardening H1 handoff.",
            "External branch plan/state: active operational posture updated to Workstream Green with Hardening H1 pending.",
            "USER review bundle helper: current packet status and timestamped ZIP generation.",
            "AI runtime/trust architecture and FAM-007 family vision: unchanged policy context for provider, cache, memory, and private/public boundaries.",
        ]
        likely_files_lines = [
            "dev/fixtures/fam007_public_leak_prevention/public_leak_prevention_fixture_set.json",
            "dev/orin_public_leak_prevention_validation.py",
            "dev/orin_user_review_bundle.py",
            "Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md",
            "C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_plan.md",
            "C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_state.md",
            "C:\\Nexus USER\\FAM-007 and matching timestamped ZIP",
        ]
        active_branch_files = [
            "Active external branch plan exists at C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_plan.md; it owns Workstream Green posture, accepted BP1/BP2/BP3 traceability, completed proof seams, proof expectations, and future gates outside repo-tracked source truth.",
            "Active external branch state exists at C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_state.md; it records the current carrier posture, Workstream Green disposition, and Hardening H1 pending USER decision outside repo-tracked source truth.",
            "Repo branch record remains Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md as durable receipt/context only; it is not active authority or a mutable live-state ledger.",
        ]
        implementation_constraints = [
            "Workstream is green; Hardening H1 remains blocked until USER approves or revises the proof-comparison seam.",
            "Hardening H1 is limited to comparing implementation proof against BP1, BP2, BP3, fixtures, validators, packet proof, branch record, and external-state boundaries.",
            "No private Dev repo, private Owner repo, local-only private root, private remote, GitHub Desktop private binding, backup/import execution, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is authorized by this packet.",
            "Provider-visible data remains none; sentToProvider=false; canAcceptPrompts=false; prompt/provider/model execution disabled; downloads/network/external calls blocked; runtime cache inactive; memory/learning/personalization inactive.",
        ]
        rejected_deferred = [
            "Deferred: private Dev repo creation, private Owner repo creation, local-only private root creation, GitHub Desktop private remote configuration, off-boot backup or recovery root implementation, and Public-to-Dev import implementation.",
            "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, PR creation, merge, release, cleanup, FAM-006/Governance/sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0-prebeta execution.",
            "Rejected for Hardening H1: executing the private/runtime action being pressure-tested as gated, silently enabling provider/cache/memory behavior, or turning proof comparison into PR/merge/release work.",
        ]
        source_truth_impact = [
            "Active external branch plan and state now route the branch from accepted BP3 into Workstream Green and Hardening H1 pending USER approval.",
            "Repo branch record carries a durable Workstream completion receipt without becoming a live operational ledger.",
            "Review packet remains branch-specific, timestamped, placeholder-free, and explicit that Hardening H1 approval covers proof comparison only.",
            "Source-truth fold-down records all admitted public-safe proof seams complete without executing gated private/runtime actions.",
        ]
        completion_checklist = [
            "All admitted same-branch Workstream proof seams are recorded complete.",
            "Direct public leak-prevention validator proof covers action gates, Dev/Owner matrices, private root/remote safety, backup/import deferral, provider/runtime/cache/memory deferral, and Hardening H1 handoff readiness.",
            "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
            "Packet digest files agree that Workstream is green and Hardening H1 remains pending USER approval.",
            "No unresolved packet placeholders or packet count mismatches remain.",
        ]
        walkthrough = [
            "Open START_HERE.md first and review the plain-language file map and USER decision.",
            "Open USER_BRANCH_PLAN_REVIEW.md and confirm the contract says Workstream Green with Hardening H1 next.",
            "Open the Workstream digest to confirm all public-safe proof seams are complete.",
            "Review the fixture and validator proof showing all private/runtime/provider/cache/memory gates remain pending.",
            "Approve or revise Hardening H1 only after reviewing this Workstream Green handoff.",
        ]
        implementation_options = [
            "Approve Hardening H1 as recommended: compare the completed public-safe Workstream proof against source truth, fixtures, validators, packet proof, and external-state boundaries. Pros: moves the branch into the required pressure-test phase; Cons: no PR/merge/release yet; Risk: low.",
            "Revise Hardening H1 proof expectations before implementation. Pros: lets USER tune comparison criteria; Cons: adds packet/source-truth repair; Risk: low.",
            "Pause at Workstream Green and keep the branch open. Pros: preserves the proof without expanding scope; Cons: delays closeout; Risk: low.",
            "Reject Hardening and request a narrower Workstream closeout repair. Pros: maximum scope control; Cons: may leave proof comparison incomplete; Risk: low but slower.",
        ]
        recommended_direction = (
            "Codex recommends approving bounded Hardening H1 only if USER agrees the next proof should compare "
            "the completed public-safe Workstream package without executing private, runtime, provider, cache, "
            "memory, PR, merge, release, cleanup, or v1.8.0 actions."
        )
        current_scope = [
            "FAM-007 Dev/Owner Skeleton Readiness Workstream proof is green.",
            "All admitted public-safe proof seams are complete.",
            "Local USER hub packet and timestamped ZIP refreshed with Hardening H1 as the next decision.",
        ]
        future_scope = [
            "Hardening H1 approval is limited to proof comparison and pressure testing.",
            "Live Validation, PR Readiness, PR creation, merge, release, cleanup, private setup, provider/model/runtime/cache/memory behavior, AI Product Contract import, Private Dev ORIN import, and v1.8.0 remain later USER decisions.",
        ]
        user_decisions = [
            "Does USER approve bounded Hardening H1 proof comparison for the FAM-007 Dev/Owner Skeleton Readiness Workstream Green package?",
            "Does USER require any change to Hardening H1 pressure-test expectations before it begins?",
            "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
        ]
        user_decisions_intro = (
            "USER is reviewing the Workstream Green handoff now. Useful feedback names "
            "Hardening H1 proof-comparison changes, pressure-test criteria, future-gated "
            "boundary controls, or a pause/rejection reason before Hardening begins."
        )
        design_ballot = [
            "Approve Hardening H1 as recommended.",
            "Revise Hardening H1 proof expectations before implementation.",
            "Pause at Workstream Green.",
            "Reject and request a narrower closeout repair.",
        ]
        response_structure = [
            "Decision: approve, revise, pause, or reject.",
            "Required changes to Hardening H1 proof expectations, if any.",
            "Must-have proof-comparison or pressure-test criteria.",
            "Future-gated boundary controls.",
            "General response.",
        ]
        digest_structure = [
            "USER intent summary.",
            "Workstream Green acceptance or concerns.",
            "Approved or revised Hardening H1 scope.",
            "Implementation constraints created from USER response.",
            "Next USER decision needed.",
        ]
        extra_plan_sections = [
            "## Integrated Dev/Owner Readiness Matrix",
            "",
            "| Lane | Accepted BP1/BP2 basis | Workstream proof completed | Future USER gate |",
            "| --- | --- | --- | --- |",
            "| Dev | Future private-repo-oriented readiness after approval, with public-upstream safety. | Action-gate proof and Dev readiness matrix recorded; no private Dev setup executed. | Private Dev repo/root/remote creation and GitHub Desktop binding. |",
            "| Owner | Local-private baseline with local Git/version history, no public exposure, and no default remote. | Owner readiness matrix recorded; no Owner private root or remote created. | Owner private root/remote choice, encrypted recovery, and any remote evaluation. |",
            "",
            "## Edition / Lane Matrix",
            "",
            "| Edition / Lane | Identity posture | Workstream proof | Future boundary |",
            "| --- | --- | --- | --- |",
            "| User/Public | Nexus Desktop AI or Nexus Desktop AI - Pre-Beta. | Public branch remains source-truth and proof-only. | No private assets or provider execution. |",
            "| Dev | Nexus Desktop AI - DEV PRIVATE after approval. | Future private Dev path is named and gated. | Repo/root/remote creation remains future-gated. |",
            "| Owner | Nexus Owner - Local Private unless later revised. | Owner local-private default is named and gated. | Remote or shared backup model remains future-gated. |",
            "",
            "## Dev Readiness Matrix",
            "",
            "| Dev item | Workstream proof | Future USER decision |",
            "| --- | --- | --- |",
            "| Private Dev repo direction | Preferred future path after approval is recorded as proof-only. | Create private Dev repo/root/remote. |",
            "| Public-upstream relationship | Public-upstream safety and push-prevention expectations are recorded. | Configure private remotes or GitHub Desktop binding. |",
            "| Dev launcher/assets/tools inventory | Inventory/migration remains future-gated and unexecuted. | Execute transfer/import/removal. |",
            "",
            "## Owner Readiness Matrix",
            "",
            "| Owner item | Workstream proof | Future USER decision |",
            "| --- | --- | --- |",
            "| Local-private baseline | Local Git/version-history and no default remote are recorded. | Create Owner private root or remote. |",
            "| Remote evaluation | Owner remote remains future-evaluated only. | Approve any Owner remote model. |",
            "| Recovery posture | Local/private/encrypted recovery and rollback remain planned only. | Implement backup/import/recovery. |",
            "",
            "## Private Root / Remote Matrix",
            "",
            "| Surface | Workstream proof | Future USER gate |",
            "| --- | --- | --- |",
            "| Public root | Remains the current public branch/worktree. | None for private setup. |",
            "| Dev private root/remote | Named as future-gated; not created. | Private Dev setup approval. |",
            "| Owner private root/remote | Named as future-gated; not created. | Owner setup approval. |",
            "",
            "## GitHub Desktop Binding Matrix",
            "",
            "| Lane | Workstream proof | Future USER gate |",
            "| --- | --- | --- |",
            "| User/Public | Normal public repo posture remains unchanged. | None. |",
            "| Dev | Private binding remains pending and requires private remote proof. | GitHub Desktop private remote configuration. |",
            "| Owner | Local Git/no remote remains default; private remote evaluation is future-gated. | Owner remote approval. |",
            "",
            "## Backup / Import Matrix",
            "",
            "| Lane | Workstream proof | Future USER gate |",
            "| --- | --- | --- |",
            "| User/Public | Product-safe backup remains a future proof target only. | Backup/import implementation. |",
            "| Dev | Private development recovery is named but not executed. | Public-to-Dev import and recovery approval. |",
            "| Owner | Local/private/encrypted rollback is named but not executed. | Owner backup/recovery approval. |",
            "",
            "## Provider / Runtime / Cache / Memory Deferral Matrix",
            "",
            "| Boundary | Workstream proof | Required value |",
            "| --- | --- | --- |",
            "| Provider-visible data | Recorded as none. | none |",
            "| sentToProvider | Recorded as false. | false |",
            "| canAcceptPrompts | Recorded as false. | false |",
            "| Provider/model execution | Recorded as disabled. | disabled |",
            "| Downloads/network/external calls | Recorded as blocked. | blocked |",
            "| Runtime cache behavior | Recorded as inactive. | inactive |",
            "| Memory/learning/personalization | Recorded as inactive. | inactive |",
            "",
            "## Watermark / Identity Matrix",
            "",
            "| Lane | Accepted identity posture | Workstream proof |",
            "| --- | --- | --- |",
            "| User/Public | Nexus Desktop AI or Nexus Desktop AI - Pre-Beta. | Public identity stays unchanged. |",
            "| Dev | Nexus Desktop AI - DEV PRIVATE after approval. | Future identity is named and gated. |",
            "| Owner | Nexus Owner - Local Private unless later revised. | Future identity is named and gated. |",
            "",
            "## Proof / Validation Matrix",
            "",
            "| Proof lane | Workstream surface | Hardening H1 comparison target |",
            "| --- | --- | --- |",
            "| Action gates | FAM-007 public leak-prevention fixture. | All pending USER gates remain present and unexecuted. |",
            "| Validator proof | dev/orin_public_leak_prevention_validation.py. | Direct assertions fail on missing gate or unsafe field. |",
            "| Packet proof | dev/orin_user_review_bundle.py and C:\\Nexus USER\\FAM-007. | Packet routes to Hardening H1 only. |",
            "| Source truth | Branch record and external state. | Workstream Green fold-down matches accepted planning. |",
            "",
            "## Future USER Gate Matrix",
            "",
            "| Gate | Workstream status |",
            "| --- | --- |",
            "| Hardening H1 | Pending USER approval. |",
            "| Private Dev/Owner setup | Pending USER approval. |",
            "| Private roots/remotes and GitHub Desktop binding | Pending USER approval. |",
            "| Backup/import execution | Pending USER approval. |",
            "| Provider/model/runtime/cache/memory behavior | Pending USER approval. |",
            "| PR, merge, release, cleanup, AI Product Contract import, Private Dev ORIN import, v1.8.0 | Pending USER approval. |",
        ]
    if is_fam007_dev_owner_skeleton and not is_fam007_breakpoint_2 and dev_owner_hardening_h1_packet:
        accepted_user_response = (
            "BP1 accepted Option A for FAM-007 Dev/Owner Skeleton Readiness, BP2 and BP3 "
            "were accepted, and Workstream completed the admitted public-safe proof package. "
            "Hardening H1 compared that implementation against accepted planning, fixture "
            "proof, validator proof, packet proof, branch record, and external-state "
            "boundaries without executing private setup or runtime behavior."
        )
        user_response_text = (
            "Status: Hardening H1 Green - this packet asks USER to approve, revise, "
            "pause, or reject bounded Live Validation LV1/no-visible-runtime proof only."
        )
        codex_response_digest = (
            "Codex completed the bounded H1 proof comparison for FAM-007 Dev/Owner "
            "Skeleton Readiness. The completed Workstream proof matches accepted BP1, "
            "BP2, BP3, branch record, external branch plan/state, fixture, validator, "
            "and packet boundaries. No private Dev/Owner setup, private root/remote, "
            "backup/import execution, provider/model/runtime/cache/memory behavior, "
            "PR, merge, release, cleanup, AI Product Contract import, Private Dev ORIN "
            "import, or v1.8.0 work was executed. Codex recommends bounded LV1 next."
        )
        workstream_entry_result = (
            "Hardening H1 Green - implementation-vs-plan proof comparison is complete; "
            "Live Validation LV1 remains pending USER approval."
        )
        contract_status = (
            "Complete - Hardening H1 proof comparison is green for the FAM-007 Dev/Owner "
            "Skeleton Readiness public-safe proof package; Live Validation LV1 is the "
            "next legal USER decision."
        )
        contract_version = "v8 - Hardening H1 proof comparison completed and routed to Live Validation LV1."
        plain_english_summary = (
            "This branch has completed the H1 pressure-test of the public-safe Dev/Owner "
            "Skeleton Readiness proof. H1 confirmed the proof package still matches the "
            "accepted BP1 vision, BP2 engineering plan, BP3 orchestration, branch record, "
            "external state, fixture, validator, and packet expectations while all private "
            "and runtime actions remain blocked."
        )
        what_user_sees = (
            "USER sees a Hardening H1 handoff packet. It is not a private setup packet, "
            "runtime test, PR packet, merge packet, or release packet; it prepares the "
            "branch for LV1 no-visible-runtime proof and UTS waiver review."
        )
        why_nexus = (
            "This fits Nexus because the Dev/Owner AI-edition boundary must be pressure-tested "
            "before USER is asked to validate or waive the lack of visible runtime behavior."
        )
        slc_package_plan = [
            "Workstream complete: all admitted public-safe proof seams are implemented.",
            "Hardening H1 complete: branch record, external state, fixture, validator, packet, and source-truth proof were compared against accepted BP1/BP2/BP3.",
            "Next phase is Live Validation LV1, limited to no-visible-runtime proof and UTS waiver digestion after USER approval.",
        ]
        surface_map = [
            "Public leak-prevention fixture and validator: direct proof that all private/runtime gates remain pending and no protected material is present.",
            "FAM-007 branch record: durable H1 comparison receipt and Live Validation LV1 handoff.",
            "External branch plan/state: active operational posture updated to H1 Green with LV1 pending.",
            "USER review bundle helper: current packet status and timestamped ZIP generation for the LV1 decision.",
            "AI runtime/trust architecture and FAM-007 family vision: unchanged policy context for provider, cache, memory, and private/public boundaries.",
        ]
        likely_files_lines = [
            "dev/fixtures/fam007_public_leak_prevention/public_leak_prevention_fixture_set.json",
            "dev/orin_public_leak_prevention_validation.py",
            "dev/orin_user_review_bundle.py",
            "Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md",
            "C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_plan.md",
            "C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_state.md",
            "C:\\Nexus USER\\FAM-007 and matching timestamped ZIP",
        ]
        active_branch_files = [
            "Active external branch plan exists at C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_plan.md; it owns H1 Green posture, accepted BP1/BP2/BP3 traceability, completed proof seams, proof expectations, and future gates outside repo-tracked source truth.",
            "Active external branch state exists at C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_state.md; it records the current carrier posture, H1 Green disposition, and Live Validation LV1 pending USER decision outside repo-tracked source truth.",
            "Repo branch record remains Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md as durable receipt/context only; it is not active authority or a mutable live-state ledger.",
        ]
        implementation_constraints = [
            "Hardening H1 is green; Live Validation LV1 remains blocked until USER approves or revises the no-visible-runtime proof seam.",
            "LV1 is limited to no-visible-runtime proof, UTS waiver digestion, validation, and LV1-scoped source-truth/validator/packet repairs if required.",
            "No private Dev repo, private Owner repo, local-only private root, private remote, GitHub Desktop private binding, backup/import execution, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR, merge, release, cleanup, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is authorized by this packet.",
            "Provider-visible data remains none; sentToProvider=false; canAcceptPrompts=false; prompt/provider/model execution disabled; downloads/network/external calls blocked; runtime cache inactive; memory/learning/personalization inactive.",
        ]
        rejected_deferred = [
            "Deferred: private Dev repo creation, private Owner repo creation, local-only private root creation, GitHub Desktop private remote configuration, off-boot backup or recovery root implementation, and Public-to-Dev import implementation.",
            "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, PR creation, merge, release, cleanup, FAM-006/Governance/sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0-prebeta execution.",
            "Rejected for LV1: executing runtime/private/provider/cache/memory behavior just to prove it did not change.",
        ]
        source_truth_impact = [
            "Active external branch plan and state now route the branch from Workstream Green into Hardening H1 Green and Live Validation LV1 pending USER approval.",
            "Repo branch record carries a durable H1 comparison receipt without becoming a live operational ledger.",
            "Review packet remains branch-specific, timestamped, placeholder-free, and explicit that LV1 approval covers no-visible-runtime proof and UTS waiver digestion only.",
            "Source-truth fold-down records H1 Green without executing gated private/runtime actions.",
        ]
        completion_checklist = [
            "Hardening H1 comparison receipt is present in the branch plan and branch record.",
            "Direct public leak-prevention validator proof covers the H1 comparison receipt and all private/runtime/provider/cache/memory gates.",
            "Helper output verifies packet freshness; USER-facing files stay focused on the plan and decision.",
            "Packet digest files agree that Hardening H1 is green and Live Validation LV1 remains pending USER approval.",
            "No unresolved packet placeholders or packet count mismatches remain.",
        ]
        walkthrough = [
            "Open START_HERE.md first and review the plain-language file map and USER decision.",
            "Open USER_BRANCH_PLAN_REVIEW.md and confirm the contract says Hardening H1 Green with Live Validation LV1 next.",
            "Open the H1 digest to confirm the public-safe Workstream proof was compared against accepted BP1/BP2/BP3.",
            "Review the validator proof showing all private/runtime/provider/cache/memory gates remain pending.",
            "Approve or revise LV1 only after reviewing this H1 handoff.",
        ]
        implementation_options = [
            "Approve Live Validation LV1 as recommended: digest no-visible-runtime proof and UTS waiver evidence from source truth, fixtures, validators, packet proof, and external-state boundaries. Pros: moves the branch toward PR Readiness without pretending runtime was exercised; Cons: no PR/merge/release yet; Risk: low.",
            "Revise LV1 proof expectations before validation. Pros: lets USER tune waiver/evidence criteria; Cons: adds packet/source-truth repair; Risk: low.",
            "Pause at Hardening H1 Green and keep the branch open. Pros: preserves the H1 proof without expanding scope; Cons: delays closeout; Risk: low.",
            "Reject LV1 and request a narrower H1 closeout repair. Pros: maximum scope control; Cons: may leave Live Validation evidence incomplete; Risk: low but slower.",
        ]
        recommended_direction = (
            "Codex recommends approving bounded Live Validation LV1 only if USER agrees the next proof "
            "should digest no-visible-runtime and UTS waiver evidence without executing private, runtime, "
            "provider, cache, memory, PR, merge, release, cleanup, or v1.8.0 actions."
        )
        current_scope = [
            "FAM-007 Dev/Owner Skeleton Readiness Hardening H1 proof comparison is green.",
            "All admitted public-safe proof seams remain complete and matched to accepted planning.",
            "Local USER hub packet and timestamped ZIP refreshed with Live Validation LV1 as the next decision.",
        ]
        future_scope = [
            "Live Validation LV1 approval is limited to no-visible-runtime proof and UTS waiver digestion.",
            "PR Readiness, PR creation, merge, release, cleanup, private setup, provider/model/runtime/cache/memory behavior, AI Product Contract import, Private Dev ORIN import, and v1.8.0 remain later USER decisions.",
        ]
        user_decisions = [
            "Does USER approve bounded Live Validation LV1/no-visible-runtime proof for the FAM-007 Dev/Owner Skeleton Readiness H1 Green package?",
            "Does USER require any change to LV1 waiver or evidence expectations before it begins?",
            "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
        ]
        user_decisions_intro = (
            "USER is reviewing the Hardening H1 handoff now. Useful feedback names "
            "LV1 no-visible-runtime proof changes, UTS waiver criteria, future-gated "
            "boundary controls, or a pause/rejection reason before LV1 begins."
        )
        design_ballot = [
            "Approve Live Validation LV1 as recommended.",
            "Revise LV1/no-visible-runtime proof expectations before validation.",
            "Pause at Hardening H1 Green.",
            "Reject and request a narrower H1 closeout repair.",
        ]
        response_structure = [
            "Decision: approve, revise, pause, or reject.",
            "Required changes to LV1/no-visible-runtime proof expectations, if any.",
            "Must-have waiver or validation evidence.",
            "Future-gated boundary controls.",
            "General response.",
        ]
        digest_structure = [
            "USER intent summary.",
            "Hardening H1 acceptance or concerns.",
            "Approved or revised LV1/no-visible-runtime scope.",
            "Implementation constraints created from USER response.",
            "Next USER decision needed.",
        ]
        extra_plan_sections = [
            "## Integrated Dev/Owner Readiness Matrix",
            "",
            "| Lane | Accepted basis | H1 result | Future USER gate |",
            "| --- | --- | --- | --- |",
            "| Dev | Future private-repo-oriented readiness after approval, with public-upstream safety. | PASS - public-safe proof only; no private Dev setup. | Private Dev repo/root/remote creation and GitHub Desktop binding. |",
            "| Owner | Local-private baseline with local Git/version history, no public exposure, and no default remote. | PASS - public-safe proof only; no Owner private root or remote. | Owner private root/remote choice, encrypted recovery, and any remote evaluation. |",
            "",
            "## Edition / Lane Matrix",
            "",
            "| Edition / Lane | Identity posture | H1 result |",
            "| --- | --- | --- |",
            "| User/Public | Nexus Desktop AI or Nexus Desktop AI - Pre-Beta. | PASS - public identity unchanged. |",
            "| Dev | Nexus Desktop AI - DEV PRIVATE after approval. | PASS - future identity named and gated. |",
            "| Owner | Nexus Owner - Local Private unless later revised. | PASS - future identity named and gated. |",
            "",
            "## Dev Readiness Matrix",
            "",
            "| Dev item | H1 result | Future USER decision |",
            "| --- | --- | --- |",
            "| Private Dev repo direction | PASS - preferred future path remains proof-only. | Create private Dev repo/root/remote. |",
            "| Public-upstream relationship | PASS - safety and push-prevention expectations remain recorded. | Configure private remotes or GitHub Desktop binding. |",
            "| Dev launcher/assets/tools inventory | PASS - inventory/migration remains future-gated and unexecuted. | Execute transfer/import/removal. |",
            "",
            "## Owner Readiness Matrix",
            "",
            "| Owner item | H1 result | Future USER decision |",
            "| --- | --- | --- |",
            "| Local-private baseline | PASS - local Git/version-history and no default remote remain recorded. | Create Owner private root or remote. |",
            "| Remote evaluation | PASS - Owner remote remains future-evaluated only. | Approve any Owner remote model. |",
            "| Recovery posture | PASS - local/private/encrypted recovery and rollback remain planned only. | Implement backup/import/recovery. |",
            "",
            "## Private Root / Remote Matrix",
            "",
            "| Surface | H1 result | Future USER gate |",
            "| --- | --- | --- |",
            "| Public root | PASS - remains current public branch/worktree. | None for private setup. |",
            "| Dev private root/remote | PASS - named as future-gated; not created. | Private Dev setup approval. |",
            "| Owner private root/remote | PASS - named as future-gated; not created. | Owner setup approval. |",
            "",
            "## GitHub Desktop Binding Matrix",
            "",
            "| Lane | H1 result | Future USER gate |",
            "| --- | --- | --- |",
            "| User/Public | PASS - normal public repo posture unchanged. | None. |",
            "| Dev | PASS - private binding remains pending. | GitHub Desktop private remote configuration. |",
            "| Owner | PASS - local Git/no remote remains default. | Owner remote approval. |",
            "",
            "## Backup / Import Matrix",
            "",
            "| Lane | H1 result | Future USER gate |",
            "| --- | --- | --- |",
            "| User/Public | PASS - product-safe backup remains future proof target only. | Backup/import implementation. |",
            "| Dev | PASS - private development recovery named but not executed. | Public-to-Dev import and recovery approval. |",
            "| Owner | PASS - local/private/encrypted rollback named but not executed. | Owner backup/recovery approval. |",
            "",
            "## Provider / Runtime / Cache / Memory Deferral Matrix",
            "",
            "| Boundary | H1 result | Required value |",
            "| --- | --- | --- |",
            "| Provider-visible data | PASS | none |",
            "| sentToProvider | PASS | false |",
            "| canAcceptPrompts | PASS | false |",
            "| Provider/model execution | PASS | disabled |",
            "| Downloads/network/external calls | PASS | blocked |",
            "| Runtime cache behavior | PASS | inactive |",
            "| Memory/learning/personalization | PASS | inactive |",
            "",
            "## Watermark / Identity Matrix",
            "",
            "| Lane | Accepted identity posture | H1 result |",
            "| --- | --- | --- |",
            "| User/Public | Nexus Desktop AI or Nexus Desktop AI - Pre-Beta. | PASS - public identity unchanged. |",
            "| Dev | Nexus Desktop AI - DEV PRIVATE after approval. | PASS - future identity gated. |",
            "| Owner | Nexus Owner - Local Private unless later revised. | PASS - future identity gated. |",
            "",
            "## Proof / Validation Matrix",
            "",
            "| Proof lane | H1 comparison target | H1 result |",
            "| --- | --- | --- |",
            "| Action gates | All pending USER gates present and unexecuted. | PASS |",
            "| Validator proof | Direct assertions fail on missing gate or unsafe field. | PASS |",
            "| Packet proof | Packet routes to LV1 only. | PASS |",
            "| Source truth | H1 fold-down matches accepted planning. | PASS |",
            "",
            "## H1 Proof Comparison Matrix",
            "",
            "| Proof lane | Accepted plan target | H1 comparison result |",
            "| --- | --- | --- |",
            "| Action gates | Every private/runtime/provider/cache/memory action remains pending USER decision. | PASS - fixture and branch record preserve pending gate state. |",
            "| Dev/Owner matrices | Dev is future private-repo-oriented; Owner remains local-private by default. | PASS - matrices match accepted BP1/BP2/BP3. |",
            "| Private root / remote safety | No private root, private remote, or GitHub Desktop private binding exists. | PASS - public-safe proof only. |",
            "| Backup / import deferral | Backup/import and Public-to-Dev migration remain future-gated. | PASS - no execution occurred. |",
            "| Provider/runtime/cache/memory deferral | providerVisibleData none; sentToProvider=false; canAcceptPrompts=false; execution disabled; cache/memory inactive. | PASS - validator asserts required values. |",
            "| Packet/source truth | Packet routes only to LV1 and source-truth fold-down matches H1. | PASS - helper/validator and direct packet checks support this route. |",
            "",
            "## Live Validation LV1 Preview",
            "",
            "- LV1 should prove or waive visible/runtime validation for this proof-only branch.",
            "- Expected LV1 path is no-visible-runtime proof plus UTS waiver digestion unless USER revises the LV1 expectations.",
            "- LV1 must not execute private setup, provider/model/runtime/cache/memory behavior, PR, merge, release, or cleanup.",
            "",
            "## Future USER Gate Matrix",
            "",
            "| Gate | H1 status |",
            "| --- | --- |",
            "| Live Validation LV1 | Pending USER approval. |",
            "| Private Dev/Owner setup | Pending USER approval. |",
            "| Private roots/remotes and GitHub Desktop binding | Pending USER approval. |",
            "| Backup/import execution | Pending USER approval. |",
            "| Provider/model/runtime/cache/memory behavior | Pending USER approval. |",
            "| PR, merge, release, cleanup, AI Product Contract import, Private Dev ORIN import, v1.8.0 | Pending USER approval. |",
        ]
    if is_fam007_dev_owner_skeleton and not is_fam007_breakpoint_2 and dev_owner_live_validation_lv1_packet:
        accepted_user_response = (
            "BP1, BP2, BP3, Workstream, and Hardening H1 are complete for the "
            "FAM-007 Dev/Owner Skeleton Readiness public-safe proof package. "
            "Live Validation LV1 recorded no-visible-runtime proof and UTS waiver "
            "evidence because no app UI, shortcut, provider, model, runtime, cache, "
            "memory, private root, private remote, backup/import, or installer "
            "surface changed."
        )
        user_response_text = (
            "Status: Live Validation LV1 Green - this packet asks USER to approve, "
            "revise, pause, or reject bounded PR Readiness Stage 1 analysis only."
        )
        codex_response_digest = (
            "Codex completed bounded Live Validation LV1/no-visible-runtime proof "
            "for FAM-007 Dev/Owner Skeleton Readiness. LV1 records that the branch "
            "has no user-visible runtime surface to exercise, that UTS is waived "
            "for this proof-only phase, and that all private/runtime/provider/cache/"
            "memory gates remain pending USER decisions. Codex recommends bounded "
            "PR Readiness Stage 1 analysis next."
        )
        workstream_entry_result = (
            "Live Validation LV1 Green - no-visible-runtime proof and UTS waiver "
            "evidence are complete; PR Readiness Stage 1 remains pending USER approval."
        )
        contract_status = (
            "Complete - Live Validation LV1 no-visible-runtime proof is green for "
            "the FAM-007 Dev/Owner Skeleton Readiness public-safe proof package; "
            "PR Readiness Stage 1 analysis is the next legal USER decision."
        )
        contract_version = "v9 - Live Validation LV1 completed and routed to PR Readiness Stage 1."
        plain_english_summary = (
            "This branch has completed the user-proof phase without launching or "
            "changing runtime surfaces. LV1 confirms the proof package is intentionally "
            "source-truth, fixture, validator, packet, and external-state only; there "
            "is nothing visible for USER to click or screenshot yet."
        )
        what_user_sees = (
            "USER sees an LV1 closeout packet. It is not a PR creation packet, merge "
            "packet, release packet, private setup packet, runtime test, shortcut test, "
            "or provider/cache/memory execution packet."
        )
        why_nexus = (
            "This fits Nexus because no-visible-runtime proof keeps the Dev/Owner "
            "skeleton boundary honest: visible/manual validation is not faked when "
            "the approved branch only created public-safe proof and preserved gates."
        )
        slc_package_plan = [
            "Workstream complete: all admitted public-safe proof seams are implemented.",
            "Hardening H1 complete: implementation-vs-plan proof comparison is green.",
            "Live Validation LV1 complete: no-visible-runtime proof and UTS waiver evidence are recorded.",
            "Next phase is PR Readiness Stage 1 analysis after USER approval.",
        ]
        surface_map = [
            "Branch record: durable LV1 receipt and PR Readiness Stage 1 handoff.",
            "External branch plan/state: active operational posture updated to LV1 Green with PR Readiness Stage 1 pending.",
            "Public leak-prevention fixture and validator: direct proof that no private/runtime/provider/cache/memory gate was executed.",
            "USER review bundle helper: current packet status and timestamped ZIP generation for the PR Readiness Stage 1 decision.",
        ]
        likely_files_lines = [
            "dev/fixtures/fam007_public_leak_prevention/public_leak_prevention_fixture_set.json",
            "dev/orin_public_leak_prevention_validation.py",
            "dev/orin_user_review_bundle.py",
            "Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md",
            "C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_plan.md",
            "C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_state.md",
            "C:\\Nexus USER\\FAM-007 and matching timestamped ZIP",
        ]
        active_branch_files = [
            "Active external branch plan exists at C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_plan.md; it owns LV1 Green posture, no-visible-runtime proof, UTS waiver evidence, and future gates outside repo-tracked source truth.",
            "Active external branch state exists at C:\\Nexus Governance State\\branches\\feature_fam_007_dev_owner_skeleton_readiness\\branch_state.md; it records the current carrier posture, LV1 Green disposition, and PR Readiness Stage 1 pending USER decision outside repo-tracked source truth.",
            "Repo branch record remains Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md as durable receipt/context only; it is not active authority or a mutable live-state ledger.",
        ]
        implementation_constraints = [
            "Live Validation LV1 is green; PR Readiness Stage 1 remains blocked until USER approves or revises the analysis scope.",
            "PR Readiness Stage 1 is limited to analysis, validation review, source-truth inspection, packet proof, and decision packet generation.",
            "No private Dev repo, private Owner repo, local-only private root, private remote, GitHub Desktop private binding, backup/import execution, provider/model/runtime/cache/memory behavior, voice/Core sync, shortcut/installer work, PR creation, merge, release, cleanup, FAM-006/Governance mutation, AI Product Contract import, Private Dev ORIN import, or v1.8.0 work is authorized by this packet.",
            "Provider-visible data remains none; sentToProvider=false; canAcceptPrompts=false; prompt/provider/model execution disabled; downloads/network/external calls blocked; runtime cache inactive; memory/learning/personalization inactive.",
        ]
        rejected_deferred = [
            "Deferred: PR creation, merge, release, branch/worktree cleanup, and release artifact execution.",
            "Deferred: private Dev repo creation, private Owner repo creation, local-only private root creation, GitHub Desktop private remote configuration, off-boot backup or recovery root implementation, and Public-to-Dev import implementation.",
            "Deferred: provider SDK/model execution, model downloads, runtime provider execution, runtime cache behavior, memory/learning/indexing/retrieval/personalization, voice/Core sync, shortcut/installer work, FAM-006/Governance/sibling-worktree mutation, AI Product Contract import, Private Dev ORIN import, and v1.8.0-prebeta execution.",
        ]
        source_truth_impact = [
            "Active external branch plan and state route the branch from H1 Green into LV1 Green and PR Readiness Stage 1 pending USER approval.",
            "Repo branch record carries a durable LV1 no-visible-runtime receipt without becoming a live operational ledger.",
            "Review packet remains branch-specific, timestamped, placeholder-free, and explicit that PR Readiness Stage 1 approval covers analysis only.",
            "Source-truth fold-down records LV1 Green without executing gated private/runtime actions.",
        ]
        completion_checklist = [
            "Live Validation LV1 receipt is present in the branch plan and branch record.",
            "No-visible-runtime proof records that no app UI, provider prompt surface, shortcut, installer, private root, private remote, backup/import workflow, cache behavior, memory behavior, or runtime execution surface changed.",
            "UTS waiver evidence records that manual USER test execution is not applicable for this proof-only LV1.",
            "Direct public leak-prevention validator proof covers LV1 no-visible-runtime and all private/runtime/provider/cache/memory gates.",
            "Packet digest files agree that Live Validation LV1 is green and PR Readiness Stage 1 remains pending USER approval.",
        ]
        walkthrough = [
            "Open START_HERE.md first and review the plain-language file map and USER decision.",
            "Open USER_BRANCH_PLAN_REVIEW.md and confirm the contract says Live Validation LV1 Green with PR Readiness Stage 1 next.",
            "Open the LV1 digest to confirm no-visible-runtime proof and UTS waiver evidence.",
            "Review validator proof showing all private/runtime/provider/cache/memory gates remain pending.",
            "Approve or revise PR Readiness Stage 1 only after reviewing this LV1 handoff.",
        ]
        implementation_options = [
            "Approve PR Readiness Stage 1 as recommended: analyze PR readiness for the completed public-safe Dev/Owner Skeleton Readiness carrier. Pros: moves toward PR creation review; Cons: no PR/merge/release yet; Risk: low.",
            "Revise PR Readiness Stage 1 inspection criteria before analysis. Pros: lets USER tune PR readiness proof; Cons: adds packet/source-truth repair; Risk: low.",
            "Pause at Live Validation LV1 Green and keep the branch open. Pros: preserves the LV1 proof without expanding scope; Cons: delays PR readiness; Risk: low.",
            "Reject PR Readiness and request a narrower LV1 closeout repair. Pros: maximum scope control; Cons: may leave PR path incomplete; Risk: low but slower.",
        ]
        recommended_direction = (
            "Codex recommends approving bounded PR Readiness Stage 1 only if USER agrees "
            "the next step should analyze readiness without creating a PR, merging, "
            "releasing, cleaning up, or executing any private/runtime/provider/cache/"
            "memory action."
        )
        current_scope = [
            "FAM-007 Dev/Owner Skeleton Readiness Workstream is green.",
            "Hardening H1 proof comparison is green.",
            "Live Validation LV1 no-visible-runtime proof and UTS waiver evidence are green.",
            "Local USER hub packet and timestamped ZIP refreshed with PR Readiness Stage 1 as the next decision.",
        ]
        future_scope = [
            "PR Readiness Stage 1 approval is limited to analysis only.",
            "PR creation, merge, release, cleanup, private setup, provider/model/runtime/cache/memory behavior, AI Product Contract import, Private Dev ORIN import, and v1.8.0 remain later USER decisions.",
        ]
        user_decisions = [
            "Does USER approve bounded PR Readiness Stage 1 analysis for the FAM-007 Dev/Owner Skeleton Readiness LV1 Green package?",
            "Does USER require any change to PR readiness inspection criteria before analysis begins?",
            "Does USER confirm all private/runtime/provider/cache/memory/PR/merge/release gates remain pending?",
        ]
        user_decisions_intro = (
            "USER is reviewing the LV1 handoff now. Useful feedback names PR Readiness "
            "Stage 1 inspection changes, future-gated boundary controls, or a pause/"
            "rejection reason before PR Readiness begins."
        )
        design_ballot = [
            "Approve PR Readiness Stage 1 as recommended.",
            "Revise PR Readiness Stage 1 inspection criteria before analysis.",
            "Pause at Live Validation LV1 Green.",
            "Reject and request a narrower LV1 closeout repair.",
        ]
        response_structure = [
            "Decision: approve, revise, pause, or reject.",
            "Required changes to PR Readiness Stage 1 inspection criteria, if any.",
            "Must-have PR readiness proof.",
            "Future-gated boundary controls.",
            "General response.",
        ]
        digest_structure = [
            "USER intent summary.",
            "LV1 Green acceptance or concerns.",
            "Approved or revised PR Readiness Stage 1 scope.",
            "Implementation constraints created from USER response.",
            "Next USER decision needed.",
        ]
        extra_plan_sections = [
            "## Live Validation LV1 No-Visible-Runtime Proof",
            "",
            "| Surface | LV1 result | Evidence basis |",
            "| --- | --- | --- |",
            "| App UI / runtime surface | No visible surface changed. | Workstream and H1 changed source-truth, fixture, validator, helper, packet, and external-state proof only. |",
            "| Provider prompt / model execution | Not executed. | providerVisibleData none; sentToProvider=false; canAcceptPrompts=false; prompt/provider/model execution disabled. |",
            "| Cache / memory behavior | Not executed. | runtime cache inactive; memory/learning/personalization inactive. |",
            "| Private roots / remotes / GitHub Desktop binding | Not created or configured. | Public-safe proof keeps all private setup gates pending. |",
            "| Backup / import / recovery | Not executed. | Backup/import remains a future USER decision. |",
            "",
            "## UTS Waiver Evidence",
            "",
            "- Formal USER Test Summary execution is waived for LV1 because the approved branch has no visible runtime surface, shortcut, installer, provider, cache, memory, private root, private remote, or backup/import behavior for USER to exercise.",
            "- The waiver is limited to this no-visible-runtime LV1 proof. Future runtime, UI, shortcut, installer, provider, cache, memory, private setup, or backup/import work will require its own Live Validation proof or USER waiver.",
            "",
            "## PR Readiness Stage 1 Preview",
            "",
            "- PR Readiness Stage 1 should analyze readiness only.",
            "- Stage 1 must inspect source-truth fold-down, release-debt posture, current-main freshness, merge-stable projection needs, packet proof, validation proof, and remaining private/runtime gates.",
            "- Stage 1 must not create a PR, merge, release, clean up, or execute private/runtime actions.",
            "",
            "## Future USER Gate Matrix",
            "",
            "| Gate | LV1 status |",
            "| --- | --- |",
            "| PR Readiness Stage 1 | Pending USER approval. |",
            "| PR creation / Stage 2 | Pending USER approval. |",
            "| Merge / release / cleanup | Pending USER approval. |",
            "| Private Dev/Owner setup | Pending USER approval. |",
            "| Private roots/remotes and GitHub Desktop binding | Pending USER approval. |",
            "| Backup/import execution | Pending USER approval. |",
            "| Provider/model/runtime/cache/memory behavior | Pending USER approval. |",
        ]
    if stage1_ready_support_context:
        contract_status = (
            "Context Only - PR Readiness Stage 1 is ready for the separate Stage 2 USER "
            "decision; this BP2-named file is supporting context, not a current gate."
        )
        contract_version = "v3 - Generated Stage 1-ready support context."
        what_user_sees = (
            "USER sees supporting context for the completed Stage 1 review, the remaining "
            "Stage 2 PR-creation decision, and the still-pending merge, release, cleanup, "
            "runtime, and private boundaries."
        )
        why_nexus = (
            "This keeps the dedicated Stage 1 artifact authoritative while preserving useful "
            "BP2 context without reopening or duplicating the Stage 1 USER gate."
        )
        design_ballot = [
            "Review the Stage 1 support context and the separate Stage 2 decision artifact.",
            "Request a repair to the Stage 1 packet or its support context.",
            "Pause before Stage 2 PR creation.",
            "Reject the proposed Stage 2 path and request a narrower closeout.",
        ]
        response_structure = [
            "Stage 2 decision: approve, revise, pause, or reject.",
            "Required changes to PR creation or review expectations, if any.",
            "Must-have Stage 2 proof.",
            "Future-gated boundary controls.",
            "General response.",
        ]
        digest_structure = [
            "Stage 1 readiness result.",
            "Stage 2 approval or concerns.",
            "Implementation constraints created from USER response.",
            "Next USER decision needed.",
        ]
        implementation_constraints = [
            "PR Readiness Stage 1 is ready; this support file does not reopen Stage 1 or authorize Stage 2.",
            "PR Readiness Stage 2 remains pending the separate primary USER decision.",
            "Merge, release, cleanup, runtime, provider/model/cache/memory, private setup, and sibling mutation remain pending.",
        ]
        rejected_deferred = [
            "Deferred: PR creation until the separate Stage 2 USER decision.",
            "Deferred: merge, release, cleanup, runtime/private actions, and sibling-worktree mutation.",
        ]
        source_truth_impact = [
            "The dedicated PR_READINESS_STAGE1_REVIEW.md remains the only Stage 1 decision surface.",
            "This USER_BRANCH_PLAN_REVIEW.md file is supporting context only and must not claim BP2 acceptance.",
            "Live technical freshness remains helper, validator, GitHub, or external-state evidence rather than USER-facing canon.",
        ]
        contract_change_log = [
            "v3 - Stage 1-ready support context is rendered without reopening Stage 1 or presenting BP2 as the current gate.",
        ]
        completion_checklist = [
            "The dedicated Stage 1 primary artifact remains the only current decision file.",
            "This support context routes USER to the separate Stage 2 decision.",
            "No stale Stage 1 approval request or BP2 acceptance request is emitted.",
            "Merge, release, cleanup, runtime, private, and sibling boundaries remain explicit.",
        ]
        plain_english_summary = (
            "This file is supporting context for a completed PR Readiness Stage 1 review. "
            "It does not ask USER to accept Stage 1 again or accept BP2; it points to the "
            "separate Stage 2 PR-creation decision."
        )
        end_state_vision = (
            "The packet presents one authoritative Stage 1 decision surface, one supporting "
            "context aid, and a clear separate Stage 2 decision without reopening earlier gates."
        )
        walkthrough = [
            "Open the dedicated PR_READINESS_STAGE1_REVIEW.md primary artifact first.",
            "Use this file only for supporting BP2/lifecycle context.",
            "Review the separate Stage 2 PR-creation decision before any PR mutation.",
        ]
        implementation_options = [
            "Approve Stage 2 through the dedicated primary decision artifact.",
            "Revise the Stage 2 PR creation or review expectations.",
            "Pause at Stage 1 Ready For Stage 2.",
            "Reject and request a narrower closeout.",
        ]
        recommended_direction = (
            "Keep the dedicated Stage 1 artifact authoritative and use this file only as "
            "supporting context while Stage 2 remains pending USER approval."
        )
        current_scope = [
            "Stage 1 analysis and bounded repair are complete and represented by the dedicated primary artifact.",
            "This file preserves supporting lifecycle, source-truth, and proof context only.",
        ]
        future_scope = [
            "Stage 2 PR creation and review remain pending the separate USER decision.",
            "Merge, release, cleanup, runtime/private actions, and sibling mutation remain future-gated.",
        ]
        slc_package_plan = [
            "No implementation seam is authorized by this supporting context file.",
            "Stage 2 may proceed only from the dedicated primary decision artifact after USER approval.",
        ]
        accepted_user_response = (
            "Stage 1-ready context is preserved; no new BP2 acceptance is recorded here."
        )
        user_response_text = None
        codex_response_digest = (
            "Stage 1 is ready for the separate Stage 2 USER decision. This support context "
            "does not reopen Stage 1, accept BP2, authorize implementation, or authorize merge/release."
        )
        workstream_entry_result = (
            "Status: Context Only - Workstream implementation is not requested by this support file."
        )
        user_decisions = [
            "Does USER approve PR Readiness Stage 2 PR creation through the dedicated primary artifact?",
            "Does USER require changes to PR body, review, or proof expectations before Stage 2?",
            "Does USER confirm merge, release, cleanup, runtime/private, and sibling gates remain pending?",
        ]

    normalized_contract_status = contract_status.casefold()
    if stage1_ready_support_context:
        user_gate_state = (
            "Context Only - Stage 1 is ready for the separate Stage 2 USER decision; "
            "this support file is not a USER gate."
        )
        user_response_proof = (
            "Context preserved - Stage 1 readiness is represented by the dedicated primary artifact."
        )
        user_response_digested = (
            "Context only - no new BP2 acceptance or Stage 1 acceptance is recorded here."
        )
    elif normalized_contract_status.startswith("waived by user"):
        user_gate_state = "USER Waived - explicit USER waiver recorded for this BP2 gate."
        user_response_proof = "Waived by USER - BP2 gate has explicit USER waiver proof."
        user_response_digested = "Digested - waiver preserved as implementation constraint."
    elif normalized_contract_status.startswith("complete"):
        user_gate_state = "USER Accepted - USER accepted the final BP2 Branch Plan Contract."
        user_response_proof = "Accepted by USER - BP2 gate has USER acceptance proof."
        user_response_digested = "Digested - USER response converted into implementation constraints."
    else:
        user_gate_state = "Pending USER Review - packet is reviewable but USER has not accepted or waived this gate."
        user_response_proof = "Pending USER Response - BP2 gate remains open."
        user_response_digested = "Pending USER Response - Codex has not digested a final USER disposition."
    bp3_approval_text = (
        "BP3 is accepted for FAM-007 Owner AI Operational Foundation Gates. The "
        "active decision is complete bounded Workstream implementation approval "
        "for SLC-001 through SLC-006 and all eighteen accepted seams, starting at "
        "SLC-001 / Seam 1 - Define protected classes and public-safe exclusion "
        "contract, while private setup, provider/model/runtime/cache/memory "
        "activation, real Owner memory, real agents, PR, merge, release, cleanup, "
        "issue mutation, sibling-worktree mutation, AI Product Contract import, "
        "Private Dev ORIN import, and v1.8.0 stay future-gated."
        if workstream_package_approval_packet
        else
        "Live Validation LV1 is green for the admitted FAM-007 Dev/Owner Skeleton Readiness package. The next decision is bounded PR Readiness Stage 1 analysis only; this packet does not authorize PR creation, private/runtime/provider/cache/memory behavior, merge, release, or cleanup."
        if dev_owner_live_validation_lv1_packet
        else
        "Workstream is green for the admitted FAM-007 Dev/Owner Skeleton Readiness package. The next decision is bounded Hardening H1 proof comparison only; this packet does not authorize private/runtime/provider/cache/memory behavior, PR, merge, release, or cleanup."
        if dev_owner_workstream_green_packet
        else
        "Hardening H1 is green for the admitted FAM-007 Dev/Owner Skeleton Readiness package. The next decision is bounded Live Validation LV1/no-visible-runtime proof only; this packet does not authorize private/runtime/provider/cache/memory behavior, PR, merge, release, or cleanup."
        if dev_owner_hardening_h1_packet
        else
        "BP3 approval text applies only when BP1 and BP2 are accepted or explicitly waived and BP3 validation is green. This PR Readiness packet does not request BP3 implementation approval."
        if pr_readiness_stage1_packet
        else (
            "BP3 is the active Workstream Entry / Orchestration Validation packet. "
            "BP3 may recommend an entry Workstream seam for a later USER "
            "decision, but this packet does not authorize Workstream implementation."
        )
        if bp3_orchestration_packet
        else (
            "BP3 may begin only after USER accepts or explicitly waives this BP2 engineering plan. This BP2 packet does not start BP3 and does not authorize Workstream implementation."
        )
    )

    lines = [
        f"# USER Branch Plan Review - {title}",
        "",
        "## Contract Status",
        "",
        contract_status,
        "",
        "## Packet Reviewability State",
        "",
        "Reviewable - helper generated this packet for USER inspection.",
        "",
        "## USER Gate State",
        "",
        user_gate_state,
        "",
        "## USER Response Proof",
        "",
        user_response_proof,
        "",
        "## USER Response Digested",
        "",
        user_response_digested,
        "",
        "## Acceptance / Waiver / Revision / Rejection Receipt",
        "",
        user_response_proof,
        "",
        "## Contract Version / Revision",
        "",
        contract_version,
        "",
        "## Plain-English Branch Summary",
        "",
        plain_english_summary,
        "",
        "This file is the BP2 engineering-plan review. It should help USER answer whether the plan correctly builds the accepted or waived BP1 Branch Vision, whether the proof path is sufficient, and whether anything must route back to BP1 before implementation.",
        "",
        "## Accepted Branch Vision Summary",
        "",
        accepted_user_response
        or ("BP1 context is treated as already represented for this later-phase PR Readiness packet." if pr_readiness_stage1_packet else "Pending accepted or waived BP1 trace."),
        "",
        "## Implementation Package Summary",
        "",
        plain_english_summary,
        "",
        "## Branch Scope Size Test",
        "",
        "The branch package should be the largest coherent feature-focused implementation package that can be validated, hardened, live-validated, reviewed, and rolled back safely without mixing unrelated product areas.",
        "",
        "## SLC / Seam Plan",
        "",
        *_markdown_lines(slc_package_plan),
        "",
        "## Affected Surfaces",
        "",
        *_markdown_lines(surface_map),
        "",
        "## Likely Files",
        "",
        *_markdown_lines(likely_files_lines),
        "",
        "## Validators / Helpers",
        "",
        "- Reuse registered validators and helpers before creating new ones.",
        "- USER review packet generation must use the local USER hub helper.",
        "",
        "## Proof Requirements",
        "",
        "- Direct validation must prove the accepted plan or admitted later-phase review boundary.",
        "- USER-facing packet files must avoid mutable technical proof metadata.",
        "",
        "## Element-To-Phase Proof Matrix",
        "",
        "- BP1 owns branch vision acceptance or waiver.",
        "- BP2 owns engineering plan acceptance or waiver.",
        "- BP3 validates BP2 against BP1 before implementation approval.",
        "- Workstream owns runtime/code implementation only.",
        "- Hardening owns pressure-test and implementation-vs-plan verification.",
        "- Live Validation owns user-facing proof and UTS handling.",
        "",
        *extra_plan_sections,
        "## H1 Expectations",
        "",
        "- H1 must compare implementation or source-truth changes against the accepted plan and repair defects only inside approved scope.",
        "",
        "## LV / UTS Expectations",
        "",
        "- Live Validation and UTS handling remain separate phase gates when applicable.",
        "",
        "## Rollback / Safety Plan",
        "",
        "- Keep changes bounded to approved source-truth/helper/validator/fixture surfaces.",
        "- Preserve pending USER gates for PR creation, merge, release, cleanup, runtime/private actions, and artifact-model changes.",
        "",
        "## Open Engineering Risks",
        "",
        "- Stale review-packet wording can confuse BP1, BP2, BP3, and PR Readiness boundaries if not regenerated through the helper.",
        "",
        "## Future-Gated Boundaries",
        "",
        *_markdown_lines(future_scope),
        "",
        "## Line-Item USER Plan Review",
        "",
        *_markdown_lines(user_decisions),
        "",
        "## Plan Acceptance Checklist",
        "",
        *_markdown_lines(completion_checklist),
        "",
        "## Exact BP3 Approval Text When Ready",
        "",
        bp3_approval_text,
        "",
        "## What Will I Actually See, And Where Will I See It?",
        "",
        what_user_sees,
        "",
        "## End-State Vision",
        "",
        end_state_vision,
        "",
        "## Visual / Functional Walkthrough",
        "",
        *_markdown_lines(walkthrough),
        "",
        "## Surface Map",
        "",
        *_markdown_lines(surface_map),
        "",
        "## Implementation Options",
        "",
        *_markdown_lines(implementation_options),
        "",
        "## Recommended Direction",
        "",
        recommended_direction,
        "",
        "## Why This Fits The Nexus Vision",
        "",
        why_nexus,
        "",
        "## USER Plan Review Decision",
        "",
        "Choose one of these paths, then add any notes or changes you want:",
        "",
        *_markdown_lines(design_ballot),
        "",
        "## USER Decisions Needed",
        "",
        user_decisions_intro,
        "",
        *_markdown_lines(user_decisions),
        "",
        "## USER Response",
        "",
        user_response_text
        or accepted_user_response
        or "Status: Pending USER Response - Workstream implementation remains blocked until USER answers, revises, rejects, accepts, or explicitly waives this contract.",
        "",
        "Required USER Response structure:",
        "",
        *_markdown_lines(response_structure),
        "",
        "## Codex Response Digest",
        "",
        codex_response_digest
        or "Status: Pending USER Response - Codex has not yet digested USER answers for this contract. Workstream implementation requires a later digest or an explicit USER waiver.",
        "",
        "Required Codex Response Digest structure:",
        "",
        *_markdown_lines(digest_structure),
        "",
        "## Implementation Constraints Created By USER Response",
        "",
        *_markdown_lines(implementation_constraints),
        "",
        "## USER Rejected / Deferred Ideas",
        "",
        *_markdown_lines(rejected_deferred),
        "",
        "## Vision Delta / Source-Truth Impact",
        "",
        *_markdown_lines(source_truth_impact),
        "",
        "## Contract Change Log",
        "",
        *_markdown_lines(contract_change_log),
        "",
        "## Current Branch Scope",
        "",
        *_markdown_lines(current_scope),
        "",
        "## Future-Gated Scope",
        "",
        *_markdown_lines(future_scope),
        "",
        "## Implementation Staging Notes",
        "",
        *_markdown_lines(slc_package_plan),
        "",
        "## Review Scope",
        "",
        "- Review the copied source-truth files, Branch Vision, Branch Plan, decision options, risks, proof expectations, and pending USER gates.",
        "- Technical freshness proof for the branch, commit, baseline, validation, and ZIP export stays in Codex chat digest, helper output, validator output, or external operational state.",
        "",
        "## Workstream Entry Result",
        "",
        workstream_entry_result
        or "Status: Pending USER Response - first seam, affected files, validators, proof requirements, USER-facing proof, and exact implementation approval text must be returned only after USER response/digest or explicit waiver.",
        "",
        "## Contract Completion Checklist",
        "",
        *_markdown_lines(completion_checklist),
        "",
        "## Codex Recommendations And Implementation Options",
        "",
        "This compatibility section is retained for older packet validators. See Implementation Options and Recommended Direction above.",
        "",
        *_markdown_lines(implementation_options),
        "",
        "## USER Plan Review Questions",
        "",
        "This section summarizes BP2 plan-review questions. See USER Decisions Needed above.",
        "",
        *_markdown_lines(user_decisions),
        "",
        "## Appendix - Legacy Validator Compatibility",
        "",
        "Legacy compatibility sections are retained only for older validators and should not replace the contract sections above.",
        "",
        "## Active External Branch Plan / Historical Branch Plan Files",
        "",
        *_markdown_lines(active_branch_files),
        "",
        "## Historical / Rollback Context Files",
        "",
        *_markdown_lines(rollback_context_files),
        "",
        "## Supporting Source-Truth Files",
        "",
        *_markdown_lines(source_truth_files),
        "",
        "## Pending USER Decisions",
        "",
        *_markdown_lines(pending_user_decisions),
        "",
        "## Exact USER Decision Supported",
        "",
        exact_user_decision,
        "",
    ]
    review_path = target / USER_BRANCH_PLAN_REVIEW_FILE
    review_path.write_text("\n".join(lines), encoding="utf-8")
    return review_path.resolve()


def _write_workstream_entry_packet_digests(
    *,
    target: Path,
    source_branch: str,
    source_head: str,
    origin_main: str,
    packet_folder: Path,
    export_zip: Path,
    copied: list[tuple[str, str]],
    extra_bundle_files: list[str],
    bundle_file_count: int,
    expected_count: int,
    copied_count: int,
    exact_user_decision: str,
    pending_user_decisions: list[str],
    stage1_outcome: str | None = None,
) -> list[Path]:
    normalized_decision = exact_user_decision.casefold()
    pr_stage1_packet = _is_pr_readiness_stage1_packet(
        source_branch=source_branch,
        normalized_decision=normalized_decision,
        stage1_outcome=stage1_outcome,
    )
    if pr_stage1_packet:
        return _write_pr_readiness_stage1_packet_digests(
            target=target,
            stage1_outcome=stage1_outcome,
            exact_user_decision=exact_user_decision,
            copied=copied,
            pending_user_decisions=pending_user_decisions,
        )
    is_fam007_breakpoint_2 = (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
    )
    is_fam007_owner_ai_foundation = (
        source_branch == "feature/fam-007-owner-ai-operational-foundation-gates"
    )
    seam1_approval_packet = (
        is_fam007_breakpoint_2
        and "approve bounded workstream implementation" in exact_user_decision.casefold()
    )
    seam1_completion_packet = (
        is_fam007_breakpoint_2
        and "approve or revise seam 2" in exact_user_decision.casefold()
    )
    workstream_green_packet = (
        is_fam007_breakpoint_2
        and "approve bounded hardening h1" in exact_user_decision.casefold()
    )
    hardening_h1_packet = (
        is_fam007_breakpoint_2
        and "approve bounded live validation lv1" in exact_user_decision.casefold()
    )
    lv1_green_packet = _is_fam007_breakpoint2_live_validation_lv1_packet(
        source_branch=source_branch,
        normalized_decision=normalized_decision,
    )
    pr_stage2_packet = _is_pr_readiness_stage2_packet(
        source_branch=source_branch,
        normalized_decision=normalized_decision,
        stage1_outcome=stage1_outcome,
    )
    pr_stage1_packet = _is_pr_readiness_stage1_packet(
        source_branch=source_branch,
        normalized_decision=normalized_decision,
        stage1_outcome=stage1_outcome,
    )
    workstream_package_approval_packet = (
        source_branch in FAM007_WORKSTREAM_PACKAGE_APPROVAL_BRANCHES
        and any(
            marker in normalized_decision
            for marker in BRANCH_PLANNING_IMPLEMENTATION_REQUEST_MARKERS
        )
        and not any(
            marker in normalized_decision
            for marker in BRANCH_PLANNING_IMPLEMENTATION_BLOCKING_MARKERS
        )
    )
    is_fam006_recording = (
        source_branch == "feature/fam-006-dashboard-recording-start-stop-local-file"
    )
    fam006_workstream_approval_review_packet = (
        _is_fam006_workstream_implementation_approval_review(
            normalized_decision,
            is_fam006_recording=is_fam006_recording,
        )
    )
    bp3_packet = (
        source_branch
        in {
            "feature/fam-007-dev-owner-skeleton-readiness",
            "feature/fam-007-owner-ai-operational-foundation-gates",
            "feature/fam-006-dashboard-recording-start-stop-local-file",
        }
        and not workstream_package_approval_packet
        and not fam006_workstream_approval_review_packet
        and (
            "bp3" in normalized_decision
            or "workstream entry / orchestration" in normalized_decision
            or "orchestration validation" in normalized_decision
        )
    )
    dev_owner_workstream_green_packet = (
        source_branch == "feature/fam-007-dev-owner-skeleton-readiness"
        and "approve bounded hardening h1" in normalized_decision
    )
    dev_owner_hardening_h1_packet = (
        source_branch == "feature/fam-007-dev-owner-skeleton-readiness"
        and "approve bounded live validation lv1" in normalized_decision
    )
    dev_owner_live_validation_lv1_packet = _is_dev_owner_live_validation_lv1_packet(
        source_branch,
        normalized_decision,
    )
    bp1_packet = (
        "bp1 branch vision" in normalized_decision
        and any(
            marker in normalized_decision
            for marker in (
                "authorize bp2 user branch plan review only",
                "authorize bp2 user branch plan review preparation only",
                "authorize bp2 preparation only",
            )
        )
    )
    bp2_packet = (
        not bp1_packet
        and not bp3_packet
        and (
            "bp2 user branch plan review" in normalized_decision
            or "bp2 branch plan review" in normalized_decision
        )
    )
    packet_status = (
        "bp1 branch vision review - BP1 Branch Vision Review remains pending "
        "USER acceptance, revision, waiver, rejection, or hold; BP2 remains pending."
        if bp1_packet
        else
        "bp2 branch plan review - accepted BP1 Branch Vision is the planning basis; "
        "BP2 USER Branch Plan Review packet is Reviewable; USER acceptance, revision, "
        "waiver, rejection, or hold remains pending; BP3 remains pending."
        if bp2_packet
        else
        "workstream implementation approval review - BP1, BP2, and BP3 are "
        "accepted; bounded FAM-006 Workstream/runtime implementation approval "
        "packet is Reviewable; USER implementation approval remains pending; "
        "a green first seam is continuation proof, not package completion."
        if fam006_workstream_approval_review_packet
        else
        "implementation-ready - BP1, BP2, and BP3 are accepted; bounded Workstream "
        "package implementation is approved by this packet with Seam 1 as the entry "
        "checkpoint and continuation governed until Workstream Green, a real blocker, "
        "or explicit USER waiver."
        if workstream_package_approval_packet
        else
        "workstream entry final decision review - Workstream Green review; admitted "
        "FAM-007 Dev/Owner proof seams are complete and Hardening H1 remains pending "
        "USER approval."
        if dev_owner_workstream_green_packet
        else
        "hardening final decision review - Hardening H1 is green; Live Validation LV1 "
        "remains pending USER approval."
        if dev_owner_hardening_h1_packet
        else
        "live validation final decision review - Live Validation LV1 is green; "
        "PR Readiness Stage 1 remains pending USER approval."
        if dev_owner_live_validation_lv1_packet
        else
        "bp3 orchestration review - accepted BP1 Branch Vision and accepted BP2 "
        "Branch Plan are the traceability basis; BP3 Workstream Entry / "
        "Orchestration Validation packet is Reviewable; USER BP3 approval, "
        "revision, waiver, rejection, or hold remains pending; Workstream "
        "implementation remains pending separate USER approval."
        if bp3_packet
        else
        "pr readiness stage1 approval review - PR Readiness Stage 1 analysis "
        "remains pending USER approval; PR creation remains pending USER approval."
        if pr_stage1_packet
        else
        "pr readiness stage2 review - PR Readiness Stage 1 Ready For Stage 2; "
        "PR creation remains pending USER approval."
        if pr_stage2_packet
        else
        "workstream implementation approval - Seam 1 public-safe action-gate registry "
        "and exact USER decision proof is approved by this packet decision path."
        if seam1_approval_packet
        else (
            "live validation final decision review - Live Validation LV1 is green; "
            "PR Readiness Stage 1 remains pending USER approval."
        )
        if lv1_green_packet
        else (
            "hardening final decision review - Hardening H1 is green; Live Validation LV1 "
            "remains pending USER approval."
        )
        if hardening_h1_packet
        else (
            "workstream entry final decision review - Workstream Green review; Seams 1 through 4 "
            "are complete and Hardening H1 remains pending USER approval."
        )
        if workstream_green_packet
        else (
            "workstream entry final decision review - seam 1 completion review; action-gate registry and exact USER decision "
            "proof are complete; Seam 2 remains pending USER approval."
        )
        if seam1_completion_packet
        else (
            "workstream entry final decision review - Workstream implementation "
            "remains pending USER approval."
        )
    )
    bp3_readiness_contract = ""
    if bp1_packet:
        analysis_status = (
            "Analysis Summary: BP1 Branch Vision Review packet for the active "
            "Branch Planning carrier."
        )
        implementation_posture = (
            "Implementation Posture: BP2, BP3, Workstream implementation, "
            "private setup, runtime/provider/cache/memory behavior, PR, merge, "
            "release, cleanup, and sibling-worktree mutation remain pending "
            "USER decisions."
        )
        recommended_seam = (
            "Recommended Next Phase: BP1 USER decision, then BP2 USER Branch "
            "Plan Review only if USER accepts or explicitly waives BP1."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the project vision, FAM-007 "
            "family vision, Public/Dev/Owner boundary plan, AI Runtime And Trust "
            "Architecture, active branch authority record, branch artifact rules, "
            "phase governance, execution rules, validation registry, backlog, and "
            "roadmap context needed for the BP1 Branch Vision decision."
        )
        checklist_status = (
            "Checklist Focus: BP1 Branch Vision Review - project, family, feature, "
            "branch goal, end-state vision, user-facing review surfaces, options, "
            "recommendations, future-gated decisions, and regression-risk controls "
            "are represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_VISION_REVIEW.md, "
            "USER_BRANCH_PLAN_REVIEW.md as BP2 preview only, required digest/"
            "checklist files, and copied source-truth files are loaded and "
            "digestible for USER review; BP1 remains pending USER decision."
        )
    elif bp2_packet:
        analysis_status = (
            "Analysis Summary: BP2 USER Branch Plan Review packet for the active "
            "Branch Planning carrier."
        )
        implementation_posture = (
            "Implementation Posture: BP2 is reviewable but not accepted; BP3, "
            "Workstream implementation, private setup, runtime/provider/cache/memory "
            "behavior, PR, merge, release, cleanup, and sibling-worktree mutation "
            "remain pending USER decisions."
        )
        recommended_seam = (
            "Recommended Next Phase: BP2 USER decision; BP3 Workstream Entry / "
            "Orchestration Validation may be prepared only if USER accepts or "
            "explicitly waives BP2."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes accepted BP1 Branch Vision context, "
            "FAM-007 family vision, Public/Dev/Owner boundary plan, AI Runtime And "
            "Trust Architecture, active branch authority record, branch artifact rules, "
            "phase governance, execution rules, validation registry, backlog, roadmap, "
            "and worktree-slot context needed for the BP2 engineering-plan decision."
        )
        checklist_status = (
            "Checklist Focus: BP2 Branch Plan Review - accepted BP1 trace, branch "
            "scope size, seam/SLC route, affected surfaces, likely files, validators, "
            "proof requirements, H1/LV/UTS expectations, rollback, risks, future-gated "
            "decisions, and exact BP3 approval text are represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md as the primary "
            "BP2 decision file, USER_BRANCH_VISION_REVIEW.md as supporting accepted "
            "vision context, required digest/checklist files, and copied source-truth "
            "files are loaded and digestible for USER review; BP2 remains pending USER "
            "acceptance, revision, waiver, rejection, or hold."
        )
    elif bp3_packet and is_fam006_recording:
        bp3_readiness_contract = (
            "\n## Plain-Language BP3 Readiness Summary\n\n"
            "BP3 is the final Branch Planning readiness check before a later "
            "Workstream implementation approval can be considered. For FAM-006 "
            "Recording, BP3 verifies that accepted BP2 Option C remains one coherent "
            "bounded package: Dashboard Recording Card plus Recording Studio plus a "
            "minimal Log Viewer Studio launch/folder shell. This packet does not "
            "authorize runtime implementation.\n\n"
            "## Accepted BP1 Vision Traceability\n\n"
            "- BP1 accepted the Recording vision after Option F planning solidification.\n"
            "- The accepted vision keeps Recording tied to the active Overlay Profile, "
            "native NDAI logs as the product artifact, readable files as USER-requested "
            "exports, and new/affected FAM-006 UI inheriting the existing Dashboard "
            "visual system.\n"
            "- Full Log Viewer Studio, previous-log selection, export customization, "
            "tray controls, keybinds, full settings, and Native Log Loader full "
            "implementation remain future-gated.\n\n"
            "## Accepted BP2 Plan Traceability\n\n"
            "- BP2 accepted Option C as the current-branch implementation shape: "
            "Dashboard Recording Card, Recording Studio, and minimal Log Viewer "
            "Studio launch/folder shell.\n"
            "- BP2 kept issue #258 Overlay Profile persistence as a target-reliability "
            "line item where it affects recording target trust.\n"
            "- BP2 preserved open native/export folder behavior before active-session "
            "recording exists, while keeping export customization future-gated.\n\n"
            "## Option C Whole-Package Coherence Test\n\n"
            "PASS with boundaries: Option C remains one coherent bounded FAM-006 "
            "Workstream package if Recording Studio stays focused on recording "
            "control/status, the Log Viewer Studio surface stays a minimal native/"
            "export folder shell, issue #258 remains target-reliability repair rather "
            "than broad Dashboard persistence, and all proof shares the same Dashboard/"
            "HUD implementation route, validation path, rollback plan, release timing, "
            "and risk class.\n\n"
            "## Surface Admit / Split / Defer Findings\n\n"
            "- Admit: Dashboard Recording Card as compact quick-access/status surface.\n"
            "- Admit: Recording Studio as focused control/status surface.\n"
            "- Admit: minimal Log Viewer Studio shell for native/export folder access "
            "only; no previous-log selection, full in-app viewer, export customization, "
            "or Native Log Loader implementation.\n"
            "- Admit: native NDAI log save/readback path and no automatic CSV/Excel "
            "normal product output.\n"
            "- Admit: open native/export folder behavior before active-session recording.\n"
            "- Admit: issue #258 only where Overlay Profile persistence protects "
            "recording target reliability.\n"
            "- Defer: full Log Viewer Studio, previous-log selection, export "
            "customization, tray controls, keybinds, full settings, Native Log Loader "
            "full implementation, provider/model/private work, sibling-family work, "
            "PR, merge, release, issue closeout, and cleanup.\n"
            "- Return to BP2 if any admitted surface requires a product-direction "
            "change, full settings/export/viewer design, new visual grammar, or "
            "broader Dashboard persistence package.\n\n"
            "## Proposed Slice / SLC / Seam Sequence\n\n"
            "1. SLC-051 / Seam 1 - target reliability and active Overlay Profile "
            "contract: issue #258 persistence, target mirroring, and snapshot/readiness "
            "preflight.\n"
            "2. SLC-052 / Seam 2 - Dashboard Recording Card: compact quick access, "
            "state labels, visual-system inheritance, and open-folder pre-session "
            "entry points.\n"
            "3. SLC-053 / Seam 3 - Recording Studio: focused non-child control/status "
            "surface, no tray/keybind/settings creep.\n"
            "4. SLC-054 / Seam 4 - native/export log boundary and minimal Log Viewer "
            "Studio shell: native log readback, exported-folder access, and no "
            "automatic readable export.\n"
            "5. SLC-055 / Seam 5 - validation, Hardening, Live Validation, UTS, "
            "rollback, and visual proof readiness for the full admitted package.\n\n"
            "## Direct Proof Plan\n\n"
            "- Dashboard Recording Card proof: focused screenshots, hover/focus/"
            "disabled states, compact spacing, target/status text, and no full-studio "
            "layout inside the card.\n"
            "- Recording Studio proof: open/focus/close/minimize behavior for the "
            "admitted minimal surface, recording state mirror, and no tray/keybind/"
            "settings implementation by inertia.\n"
            "- Log Viewer shell proof: native-log folder and exported-log folder buttons "
            "work, folders can be created/opened before a recording, and no previous-log "
            "selection, full viewer, or export customization exists.\n"
            "- Native/export boundary proof: normal recording produces native NDAI output "
            "and validation readback; readable CSV/Excel/JSON files appear only as "
            "validation/export evidence or future USER-requested export.\n"
            "- Issue #258 proof: create/switch/restart/reselect Overlay Profiles and "
            "prove recording target reliability is preserved.\n\n"
            "## Rollback And Reversibility Posture\n\n"
            "The route stays reversible because each admitted surface can be disabled "
            "or removed in layers: Dashboard card entry points, Recording Studio "
            "launch/control shell, Log Viewer shell/folder access, native/export "
            "boundary hooks, and issue #258 persistence repair.\n\n"
            "## Validation / H1 / Live Validation / UTS Plan\n\n"
            "- Workstream validation: targeted unit/helper/sandbox proof for target "
            "state, folder behavior, native output/readback, visual inheritance, and "
            "future-gated boundaries.\n"
            "- Hardening H1: compare implemented behavior against accepted BP1, BP2, "
            "and BP3; pressure-test negative states, rollback, visual mismatch, issue "
            "#258 regression, and no automatic export.\n"
            "- Live Validation: validate new or affected elements only, plus previous "
            "elements whose dependencies changed; capture focused screenshots for "
            "Dashboard Recording Card, Recording Studio, minimal Log Viewer shell, "
            "folder states, and issue #258 proof.\n"
            "- UTS: refresh `C:\\Nexus USER\\UTS - FAM-006.txt` as the active "
            "worktree-specific handoff during Live Validation, not during BP3.\n\n"
            "## Visual-System Inheritance Proof\n\n"
            "Every new Recording card row, button, divider, window surface, hover/focus/"
            "disabled state, spacing rule, glow/effect, typography choice, and density "
            "choice must sample existing FAM-006 Dashboard/HUD surfaces. Helper PASS "
            "and DOM presence are not enough; Codex must inspect focused screenshots "
            "and return REPAIR if new elements do not belong in the existing visual "
            "system.\n\n"
            "## Deferred Carryforward Applicability\n\n"
            "- Recording Studio: applies now only as focused control/status; tray-backed "
            "minimize, keybind behavior, and warning dismissal settings remain deferred.\n"
            "- Log Viewer Studio: applies now only as launch/folder shell; full viewer, "
            "previous-log selection, export customization, and Native Log Loader remain "
            "deferred.\n"
            "- Native log model: applies now as normal product artifact and readback path.\n"
            "- Exported log model: applies now only as folder boundary; export flow stays "
            "future-gated.\n"
            "- Overlay Profile persistence: applies now only as target reliability and "
            "issue #258 proof.\n\n"
            "## Exact BP3 USER Decision Options\n\n"
            "- Accept BP3: confirm Option C is the accepted Workstream Entry / "
            "Orchestration Validation contract and allow Codex to request separate "
            "bounded Workstream implementation approval next.\n"
            "- Revise BP3: name any surface, seam order, proof, rollback, Live "
            "Validation, UTS, or deferred-boundary change needed before implementation "
            "approval can be considered.\n"
            "- Waive BP3: explicitly waive remaining BP3 concerns and allow a separate "
            "Workstream approval packet next.\n"
            "- Reject BP3: stop this current package route and request a different "
            "FAM-006 branch shape.\n"
            "- Hold BP3: keep the branch in BP3 USER review.\n"
        )
        analysis_status = (
            "Analysis Summary: FAM-006 Recording BP3 Workstream Entry / "
            "Orchestration Validation packet for the active Branch Planning carrier.\n"
            "BP1 Contract Status: Complete - USER accepted the revised FAM-006 "
            "Recording Branch Vision after Option F planning solidification.\n"
            "BP2 Contract Status: Complete - USER accepted the Option C Branch Plan.\n"
            "BP1 USER Gate State: USER Accepted\n"
            "BP2 USER Gate State: USER Accepted\n"
            "BP3 Packet Reviewability State: Reviewable\n"
            "BP3 USER Gate State: Pending USER Review\n"
            "Branch Package Size: PASS - Option C remains the largest safe coherent "
            "FAM-006 Recording package if Studio and Log Viewer shell stay minimal.\n"
            "SLC Traceability: Complete\n"
            "Implementation Approval: Pending separate USER approval after BP3 review."
        )
        implementation_posture = (
            "Implementation Posture: BP3 is reviewable but USER BP3 approval is "
            "pending; Workstream implementation, runtime mutation, issue closeout, "
            "PR, merge, release, cleanup, and future-gated Recording ecosystem work "
            "remain pending USER decisions."
        )
        recommended_seam = (
            "Recommended First Bounded Workstream Seam: SLC-051 / Seam 1, target "
            "reliability and active Overlay Profile contract, followed by Dashboard "
            "Recording Card proof, Recording Studio proof, Log Viewer shell/native-"
            "export boundary proof, and full validation/live/UTS readiness."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes accepted BP1 and BP2 context, "
            "FAM-006 family vision, FAM-006 Recording Family Feature Vision, active "
            "branch plan/receipt context, branch artifact rules, phase governance, "
            "development rules, validation registry, incident patterns, feature "
            "backlog, Nexus vision, and helper context needed for FAM-006 Option C "
            "BP3 orchestration."
        )
        checklist_status = (
            "Checklist Focus: FAM-006 BP3 Workstream Entry / Orchestration Validation "
            "- accepted BP1/BP2 traceability, Option C coherence, split/defer triggers, "
            "surface sequencing, Element-to-Phase proof, rollback, validation, H1, "
            "Live Validation, UTS, visual-system inheritance, and future-gated "
            "boundaries are represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md as "
            "the primary BP3 decision file, USER_BRANCH_VISION_REVIEW.md and "
            "USER_BRANCH_PLAN_REVIEW.md as supporting accepted BP1/BP2 context, "
            "required digest/checklist files, and copied source-truth files are "
            "loaded and digestible for USER review; BP3 remains pending USER "
            "approval, revision, waiver, rejection, or hold."
        )
    elif bp3_packet:
        bp3_readiness_contract = (
            "\n## Plain-Language BP3 Readiness Summary\n\n"
            "BP3 is the final Branch Planning readiness check before a later "
            "Workstream implementation approval can be considered. This packet "
            "confirms that the accepted BP1 Branch Vision and accepted BP2 Branch "
            "Plan give Codex enough public-safe direction to prepare a Workstream "
            "route, while Workstream implementation itself remains a separate "
            "future USER decision.\n\n"
            "The branch vision and plan stay focused on FAM-007 Dev/Owner Skeleton "
            "Readiness: public-safe proof that future Dev and Owner skeleton setup "
            "can be made decision-ready without creating private repos, private "
            "roots, private remotes, provider execution, runtime cache behavior, "
            "memory behavior, backup/import execution, PR work, merge work, release "
            "work, cleanup, or sibling-worktree mutation during BP3.\n\n"
            "## Accepted BP1 Vision Traceability\n\n"
            "- BP1 established the product direction: make Dev/Owner skeleton "
            "readiness understandable, reviewable, and gated before any private "
            "setup occurs.\n"
            "- BP1 kept the public repo as the place for public-safe readiness "
            "contracts, proof expectations, and USER decisions.\n"
            "- BP1 preserved future-gated boundaries for Dev private repo setup, "
            "Owner local-private setup, private remotes, backup/import behavior, "
            "provider/model/runtime/cache/memory behavior, voice/Core sync, "
            "shortcuts/installers, PR, merge, release, cleanup, AI Product "
            "Contract import, Private Dev ORIN import, and v1.8.0 work.\n\n"
            "## Accepted BP2 Plan Traceability\n\n"
            "- BP2 converted the accepted vision into an engineering route: one "
            "coherent FAM-007 branch with sequenced seams instead of separate "
            "single-control branches.\n"
            "- BP2 identified the source-truth fold-down, helper, validator, "
            "fixture, packet, and external-state proof surfaces needed before "
            "implementation can be requested.\n"
            "- BP2 kept Workstream scope public-safe: proof artifacts and validators "
            "may be prepared, while actual private setup, runtime activation, "
            "provider calls, cache/memory behavior, backup/import execution, and "
            "release actions stay future-gated.\n\n"
            "## Proposed Workstream Implementation Order\n\n"
            "1. Seam 1 - Action-gate registry and exact USER decision proof: create "
            "the public-safe registry that lists every gated Dev, Owner, private, "
            "runtime, provider, backup/import, PR, merge, release, cleanup, and "
            "sibling-worktree action with its pending USER decision.\n"
            "2. Seam 2 - Dev/Owner readiness matrices: add public-safe matrices that "
            "show what future Dev and Owner skeleton readiness will require, "
            "without creating private repos, roots, remotes, or runtime behavior.\n"
            "3. Seam 3 - Private root/remote and GitHub Desktop safety proof: prove "
            "that private roots, private remotes, GitHub Desktop private binding, "
            "and related credentials remain absent until USER explicitly approves "
            "that future setup.\n"
            "4. Seam 4 - Backup/import and provider/runtime/cache/memory deferral "
            "proof: prove backup/import, provider/model execution, downloads, "
            "runtime execution, cache behavior, memory, learning, indexing, "
            "retrieval, personalization, and voice/Core sync remain inactive.\n"
            "5. Seam 5 - Packet, fixture, validator, and fold-down proof: fold the "
            "accepted constraints into durable owners, add deterministic validation, "
            "and refresh the USER packet without turning review files into live "
            "operational ledgers.\n\n"
            "## Seam / SLC Readiness Assessment\n\n"
            "- Seam 1 readiness: ready to request after BP3 acceptance because it is "
            "public-safe, decision-proof centered, and reversible.\n"
            "- Seam 2 readiness: depends on Seam 1 registry names and exact pending "
            "decision wording so the matrices trace to accepted gates.\n"
            "- Seam 3 readiness: depends on registry and matrix proof so absence of "
            "private roots/remotes and GitHub Desktop private binding can be checked "
            "directly.\n"
            "- Seam 4 readiness: depends on prior gate proof so backup/import and "
            "provider/runtime/cache/memory deferral can be asserted without runtime "
            "activation.\n"
            "- Seam 5 readiness: depends on completed proof surfaces so fixtures, "
            "validators, packet refresh, and source-truth fold-down can check the "
            "whole accepted route.\n\n"
            "## Expected Files / Helpers / Validators / Fixtures / Review Artifacts\n\n"
            "- Source-truth surfaces: FAM-007 family vision, AI runtime and trust "
            "architecture, phase governance, branch artifact rules, validation "
            "registry, active branch authority, external branch plan, and external "
            "branch state.\n"
            "- Helper surfaces: USER review bundle generation and packet decision-path "
            "checks for BP1, BP2, BP3, Workstream, Hardening, Live Validation, PR "
            "Readiness, and Release Readiness separation.\n"
            "- Validator and fixture surfaces: branch-readiness planning fixtures, "
            "public leak prevention, provider-state inactivity, external-state "
            "validation, governance efficiency checks, source-owner markers, release "
            "body checks, and branch governance checks.\n"
            "- USER review artifacts: START_HERE.md as the plain-language index, this "
            "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md as the primary BP3 decision file, "
            "accepted BP1/BP2 review aids, source-truth context copies, and the "
            "timestamped upload ZIP generated from the local USER hub.\n\n"
            "## Direct Proof Plan\n\n"
            "- No-private-action proof: every private Dev/Owner repo, root, remote, "
            "credential, private artifact, and GitHub Desktop private binding remains "
            "future-gated.\n"
            "- Public-leak prevention: proof artifacts contain public-safe descriptions "
            "only and exclude private URLs, tokens, secrets, private paths, prompt "
            "payloads, model artifacts, memory content, and private automation data.\n"
            "- Provider-state inactivity: provider-visible data remains none, "
            "sentToProvider remains false, canAcceptPrompts remains false, and "
            "prompt/provider/model execution remains disabled until a future USER "
            "decision changes that gate.\n"
            "- Runtime/cache/memory deferral: downloads, network/external calls, runtime "
            "provider execution, cache behavior, memory, learning, indexing, retrieval, "
            "and personalization remain inactive.\n"
            "- GitHub Desktop binding absence: private remote setup and GitHub Desktop "
            "private binding remain pending USER decisions, with proof based on "
            "absence of created private remotes or configured private roots.\n"
            "- Backup/import deferral: off-boot backup roots, recovery roots, and "
            "public-to-private import execution remain pending USER decisions.\n"
            "- Artifact identity proof: packet folder and timestamped ZIP are generated "
            "as a matched pair from the local USER hub without sidecars or reused ZIP "
            "names.\n"
            "- External-state proof: mutable active posture remains in external state, "
            "helper output, validator output, or Codex digest rather than durable repo "
            "docs.\n\n"
            "## Rollback And Reversibility Posture\n\n"
            "The proposed Workstream route is reversible because the first seams create "
            "public-safe source-truth, helper, fixture, validator, packet, and external "
            "state proof only. If a seam introduces drift, Codex can revert the focused "
            "commit, regenerate the local USER packet, and restore the prior external "
            "state receipt without undoing private setup or runtime behavior because "
            "those actions are outside this route.\n\n"
            "## Drift Controls\n\n"
            "- User/Public lane: keep USER review files readable and decision-focused; "
            "technical proof stays in helper output, validator output, Codex digest, or "
            "external state.\n"
            "- Dev lane: keep Dev private repo, private root, private remote, provider "
            "SDK/model execution, downloads, and runtime activation behind explicit "
            "future USER gates.\n"
            "- Owner lane: keep Owner local-private setup, backup/recovery roots, "
            "public-to-private import behavior, memory behavior, voice/Core sync, and "
            "installer/shortcut behavior behind explicit future USER gates.\n"
            "- Governance lane: keep BP1 as vision, BP2 as engineering plan, BP3 as "
            "orchestration validation, Workstream as implementation, Hardening as "
            "pressure-testing, Live Validation as USER proof, and PR/Release as "
            "separate approval boundaries.\n\n"
            "## Unresolved Blockers And Pending USER Decisions\n\n"
            "No BP3 file repair authorizes implementation. USER still decides whether "
            "to accept, revise, waive, reject, or hold BP3. Workstream implementation "
            "requires a separate later approval after BP3 is accepted or waived. Every "
            "private setup, provider/runtime/cache/memory action, backup/import action, "
            "PR, merge, release, cleanup, sibling mutation, AI Product Contract import, "
            "Private Dev ORIN import, and v1.8.0 action remains future-gated.\n\n"
            "## Codex Readiness Recommendation\n\n"
            "Codex recommends accepting BP3 as a Branch Planning readiness contract "
            "only if USER agrees that the accepted BP1 vision and accepted BP2 plan "
            "are still the right traceability basis and that Seam 1 should be the "
            "first future Workstream request. This recommendation is not Workstream "
            "implementation approval.\n\n"
            "## Specific USER Readiness Questions\n\n"
            "- Does the accepted BP1 vision still describe the FAM-007 Dev/Owner "
            "Skeleton Readiness end-state USER wants?\n"
            "- Does the accepted BP2 plan still describe the correct public-safe "
            "engineering route for that vision?\n"
            "- Is Seam 1 the right first future Workstream seam, or should another "
            "proof surface come first?\n"
            "- Are the Dev, Owner, private, provider, runtime, cache, memory, backup, "
            "import, PR, merge, release, and cleanup gates preserved clearly enough?\n"
            "- Is there any extra proof USER wants before later Workstream approval?\n\n"
            "## Exact BP3 USER Decision Options\n\n"
            "- Accept BP3: confirm BP3 is the accepted Workstream Entry / Orchestration "
            "Validation contract and allow Codex to return a separate bounded "
            "Workstream implementation approval packet next.\n"
            "- Revise BP3: identify the readiness question, seam order, proof plan, "
            "rollback posture, drift control, or pending gate that needs correction.\n"
            "- Waive BP3: explicitly waive remaining BP3 concerns and allow Codex to "
            "return a separate bounded Workstream implementation approval packet next.\n"
            "- Reject BP3: stop this carrier route and request a different FAM-007 "
            "successor path.\n"
            "- Hold BP3: keep the branch in BP3 USER review while USER or ChatGPT "
            "continues packet inspection.\n"
        )
        analysis_status = (
            "Analysis Summary: BP3 Workstream Entry / Orchestration Validation "
            "packet for the active Branch Planning carrier.\n"
            "BP1 Contract Status: Complete - USER accepted the integrated FAM-007 "
            "Dev/Owner Skeleton Readiness Branch Vision.\n"
            "BP2 Contract Status: Complete - USER accepted the cleaned FAM-007 "
            "Dev/Owner Skeleton Readiness engineering plan.\n"
            "BP1 USER Gate State: USER Accepted\n"
            "BP2 USER Gate State: USER Accepted\n"
            "BP3 Packet Reviewability State: Reviewable\n"
            "BP3 USER Gate State: Pending USER Review\n"
            "Branch Plan Matches Accepted Branch Vision: PASS - BP2 keeps Dev "
            "and Owner skeleton readiness integrated, preserves Dev private-repo "
            "future direction, Owner local-private baseline, GitHub Desktop safety, "
            "backup/import posture, provider/runtime/cache/memory deferral, and "
            "lane identity proof without changing the accepted BP1 direction.\n"
            "Branch Package Size: PASS - one FAM-007 branch remains the largest "
            "safe coherent package because Dev readiness, Owner readiness, private "
            "root/remote safety, backup/import posture, provider-state deferral, "
            "packet proof, and validation proof share the same trust boundary.\n"
            "SLC Traceability: Complete\n"
            "Future-Gated Boundaries: PASS - private Dev/Owner setup, private "
            "repos/roots/remotes, GitHub Desktop private binding, backup/import "
            "execution, provider/model/runtime/cache/memory behavior, PR, merge, "
            "release, cleanup, AI Product Contract import, Private Dev ORIN import, "
            "and v1.8.0 remain pending USER decisions.\n"
            "First Bounded Workstream Seam: Seam 1 should create public-safe "
            "action-gate registry and exact USER decision proof before later "
            "Dev/Owner matrices, private root/remote safety, backup/import, "
            "provider deferral, packet, fixture, validator, and fold-down proof.\n"
            "Implementation Approval: Pending separate USER approval after BP3 "
            "review; this packet does not authorize Workstream implementation."
        )
        implementation_posture = (
            "Implementation Posture: BP3 is reviewable but USER BP3 approval is "
            "pending; Workstream implementation, private setup, runtime/provider/"
            "cache/memory behavior, PR, merge, release, cleanup, and sibling-worktree "
            "mutation remain pending USER decisions."
        )
        recommended_seam = (
            "Recommended First Bounded Workstream Seam: Seam 1, action-gate "
            "registry and exact USER decision proof, to be considered only after "
            "USER approves or waives BP3 and separately approves Workstream implementation."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes accepted BP1 Branch Vision "
            "context, accepted BP2 Branch Plan context, FAM-007 family vision, "
            "Public/Dev/Owner boundary plan, AI Runtime And Trust Architecture, "
            "active branch authority record, external branch plan/state context, "
            "branch artifact rules, phase governance, execution rules, validation "
            "registry, backlog, roadmap, and worktree-slot context needed for BP3."
        )
        checklist_status = (
            "Checklist Focus: BP3 Workstream Entry / Orchestration Validation - "
            "accepted BP1/BP2 traceability, whole-package seam order, first-seam "
            "recommendation, proof plan, H1/LV/UTS expectations, rollback posture, "
            "drift controls, and future-gated private/runtime decisions are represented "
            "for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md "
            "as the primary BP3 decision file, USER_BRANCH_VISION_REVIEW.md and "
            "USER_BRANCH_PLAN_REVIEW.md as supporting accepted BP1/BP2 context, "
            "required digest/checklist files, and copied source-truth files are "
            "loaded and digestible for USER review; BP3 remains pending USER "
            "approval, revision, waiver, rejection, or hold."
        )
        if is_fam007_owner_ai_foundation:
            bp3_readiness_contract = (
                "\n## Plain-Language BP3 Readiness Summary\n\n"
                "BP3 is the final Branch Planning readiness check before a later "
                "Workstream implementation approval can be considered. This packet "
                "confirms that the accepted BP1 Branch Vision and accepted BP2 Branch "
                "Plan give Codex enough public-safe direction to prepare a bounded "
                "Workstream route for FAM-007 Owner AI Operational Foundation Gates. "
                "It does not authorize Workstream implementation.\n\n"
                "## Accepted BP1 Vision Traceability\n\n"
                "- BP1 selected the Owner AI Operational Foundation Gates route as "
                "one coherent public-safe control-plane package.\n"
                "- The accepted vision covers protected artifact exclusion, "
                "provider/runtime disabled-state consent shells, memory-versus-cache "
                "consent gates, capability-pack install-intent gates, Developer/Owner "
                "lane readiness gates, and Owner AI memory/agent foundation schemas.\n"
                "- BP1 preserved private setup, real Owner memory, real agents, "
                "provider/model/runtime/cache/memory activation, backup/import "
                "execution, PR, merge, release, cleanup, AI Product Contract import, "
                "Private Dev ORIN import, and v1.8.0 as future USER decisions.\n\n"
                "## Accepted BP2 Plan Traceability\n\n"
                "- BP2 converted the accepted vision into six Slice/SLC deliverables "
                "with concrete surfaces, likely files, validators, fixtures, proof "
                "lanes, rollback posture, H1/LV/UTS expectations, and route-back "
                "rules.\n"
                "- BP2 kept the package public-safe: it plans controls and proof, "
                "while private roots/remotes, provider execution, runtime activation, "
                "cache behavior, memory behavior, backup/import execution, and real "
                "agents remain inactive until future USER approval.\n"
                "- BP2 records SLCs as Slice-level deliverables inside one branch, "
                "not automatic separate branches.\n\n"
                "## Whole-Package Orchestration Map\n\n"
                "1. SLC-001 - Protected Artifact Exclusion Controls: first future "
                "Workstream seam because it protects every later lane from private "
                "artifact leakage.\n"
                "2. SLC-002 - Provider/Runtime Consent-Shell Disabled States: follows "
                "artifact exclusion so disabled states can be public-safe and no-exec.\n"
                "3. SLC-003 - Memory-Versus-Cache Consent Gates: follows disabled "
                "state proof so memory and cache stay separate and inactive.\n"
                "4. SLC-004 - Capability-Pack Install-Intent Gates: follows consent "
                "proof so installation intent can be recorded without execution.\n"
                "5. SLC-005 - Developer / Owner Lane Readiness Gates: follows the "
                "earlier gate proof so lane readiness stays explicit and future-gated.\n"
                "6. SLC-006 - Owner AI Memory / Agent Foundation Gate Schemas: final "
                "schema seam because it depends on all earlier exclusion, consent, "
                "install-intent, and lane-readiness proof.\n\n"
                "## Per-SLC Readiness Verdicts\n\n"
                "| SLC | Readiness Verdict | BP3 Reason | Route-Back / Blocker |\n"
                "| --- | --- | --- | --- |\n"
                "| SLC-001 - Protected Artifact Exclusion Controls | READY FOR FIRST WORKSTREAM SEAM | Accepted BP2 names protected classes, exclusion checks, public leak prevention, and rollback; this is the safest entry because every later SLC depends on keeping protected Owner/Developer material out of public repo, packet, and upload paths. | Route back to BP2 if protected classes, exclusion surfaces, or public leak fixtures are incomplete. |\n"
                "| SLC-002 - Provider/Runtime Consent-Shell Disabled States | READY AFTER SLC-001 ENTRY PROOF | Accepted BP2 names disabled provider/runtime state, USER-facing copy, and no-execution proof; it depends on SLC-001 because disabled-state artifacts must already be protected from leakage. | Hold before SLC-002 if SLC-001 has not proven public-safe exclusion. |\n"
                "| SLC-003 - Memory-Versus-Cache Consent Gates | READY AFTER DISABLED-STATE PROOF | Accepted BP2 separates cache consent from memory consent and keeps memory/cache behavior inactive; it depends on SLC-002 because provider/runtime disabled-state proof guards the no-execution posture. | Route back to BP2 if cache and memory consent cannot be explained as separate states. |\n"
                "| SLC-004 - Capability-Pack Install-Intent Gates | READY AFTER CONSENT-GATE PROOF | Accepted BP2 defines install intent without download, setup, provider calls, or execution; it depends on prior consent and protected-artifact proof. | Hold if install-intent wording could be mistaken for install execution or capability enablement. |\n"
                "| SLC-005 - Developer / Owner Lane Readiness Gates | READY AFTER INSTALL-INTENT PROOF | Accepted BP2 defines lane identity and later private setup readiness without creating private repos, roots, remotes, or GitHub Desktop private binding. | Route back to BP2 if lane readiness begins to imply private setup approval. |\n"
                "| SLC-006 - Owner AI Memory / Agent Foundation Gate Schemas | READY AFTER LANE-READINESS PROOF | Accepted BP2 names prerequisite schemas and blocked states for future Owner memory/agents while preserving no-real-memory and no-real-agent boundaries. | Hold if schema examples require real Owner memory, real agents, prompt routing, or provider execution. |\n\n"
                "## Per-Seam Readiness Verdicts\n\n"
                "| Seam | Readiness Verdict | BP3 Proof Basis | Exact Blocker / Route-Back Statement |\n"
                "| --- | --- | --- | --- |\n"
                "| SLC-001 / Seam 1 - Define protected classes and public-safe exclusion contract | READY - recommended first bounded Workstream seam | Accepted BP2 names the protected-asset contract as the first concrete control needed before any other gate can be safely implemented. | No blocker. Route back only if USER changes protected classes or public-safe exclusion policy. |\n"
                "| SLC-001 / Seam 2 - Enforce public packet/repo/bundle exclusion checks | READY AFTER SLC-001 / Seam 1 | Enforcement depends on the protected-class contract produced in Seam 1. | Blocked until Seam 1 defines the classes and exclusion contract. |\n"
                "| SLC-001 / Seam 3 - Preserve acceptance/fold-down boundary for protected-asset policy | READY AFTER SLC-001 / Seam 2 | Fold-down depends on proved exclusion checks and accepted policy placement. | Blocked until Seam 2 proves packet/repo/bundle exclusion. |\n"
                "| SLC-002 / Seam 1 - Define disabled provider/runtime state contract | READY AFTER SLC-001 / Seam 1 | The disabled-state contract can be drafted once protected classes are defined. | Blocked if provider/runtime wording would imply execution approval. |\n"
                "| SLC-002 / Seam 2 - Plan USER-facing disabled-state copy and review packet wording | READY AFTER SLC-002 / Seam 1 | Copy depends on the disabled-state contract and must remain review-focused. | Route back if copy makes a disabled state look runnable. |\n"
                "| SLC-002 / Seam 3 - Add no-execution proof linkage for BP3 | READY AFTER SLC-002 / Seam 2 | Proof linkage depends on disabled-state copy and provider-state validator expectations. | Hold if proof requires provider/model/runtime execution. |\n"
                "| SLC-003 / Seam 1 - Separate cache consent from memory consent | READY AFTER SLC-002 / Seam 3 | Consent separation depends on proved no-execution and inactive provider/runtime posture. | Route back if cache is described as memory or memory consent is implicit. |\n"
                "| SLC-003 / Seam 2 - Plan blocked persistence states and consent error states | READY AFTER SLC-003 / Seam 1 | Blocked states depend on the cache-vs-memory consent split. | Hold if blocked states imply persistence, indexing, learning, retrieval, or personalization. |\n"
                "| SLC-003 / Seam 3 - Preserve source-truth placement for future memory/cache policy | READY AFTER SLC-003 / Seam 2 | Source-truth placement depends on clear blocked states and accepted future-gate boundaries. | Route back if policy ownership changes family or architecture-level memory/cache law. |\n"
                "| SLC-004 / Seam 1 - Define explicit install-intent state model | READY AFTER SLC-003 / Seam 1 | Install intent can be modeled once consent gates are separated and no-execution posture is preserved. | Hold if install intent is treated as download, setup, install, or execution. |\n"
                "| SLC-004 / Seam 2 - Plan blocked pending-install state and visible route-back | READY AFTER SLC-004 / Seam 1 | Pending-install copy depends on the install-intent state model. | Route back if pending-install state hides the approval needed for real installation. |\n"
                "| SLC-004 / Seam 3 - Link install-intent gates to protected artifact and provider-state proof | READY AFTER SLC-004 / Seam 2 | Linkage depends on protected artifact proof and provider no-execution proof. | Blocked until SLC-001 and SLC-002 proof exists. |\n"
                "| SLC-005 / Seam 1 - Define lane identity without private setup | READY AFTER SLC-001 / Seam 1 | Lane identity can be defined once protected public/private boundaries are explicit. | Hold if lane identity creates private repo/root/remote or GitHub Desktop binding work. |\n"
                "| SLC-005 / Seam 2 - Plan readiness gates for later private setup approval | READY AFTER SLC-005 / Seam 1 | Readiness gates depend on lane identity and future-gated private setup language. | Route back if readiness gates approve private setup instead of naming future approval needs. |\n"
                "| SLC-005 / Seam 3 - Validate lane-readiness copy in USER-facing packet | READY AFTER SLC-005 / Seam 2 | USER-facing validation depends on readiness-gate copy and packet metadata boundaries. | Hold if review files contain live technical metadata or private path leakage. |\n"
                "| SLC-006 / Seam 1 - Define future prerequisite schema names and blocked states | READY AFTER SLC-003 / Seam 1 AND SLC-005 / Seam 1 | Schema names depend on consent separation and lane identity. | Route back if schemas require real memory, real agents, prompt routing, or provider execution. |\n"
                "| SLC-006 / Seam 2 - Plan no-real-memory/no-real-agent proof and public-safe examples | READY AFTER SLC-006 / Seam 1 | Proof examples depend on schema names and blocked states. | Hold if examples include Owner-private memory, prompts, private data, or agent execution. |\n"
                "| SLC-006 / Seam 3 - Link schema gates to BP3 whole-package orchestration | READY AFTER SLC-006 / Seam 2 | Whole-package linkage depends on all prior SLC gate proofs and future-gated boundaries. | Blocked until SLC-001 through SLC-006 prior seams are satisfied or explicitly waived. |\n\n"
                "## Whole-Package Readiness Verdict\n\n"
                "BP3 Verdict: REVIEWABLE AND READY FOR USER BP3 DECISION. The accepted "
                "BP1 vision and accepted BP2 plan provide enough route, SLC, seam, "
                "proof, rollback, and future-gate detail for USER to decide BP3. "
                "The package is not implementation-approved. If USER accepts BP3, "
                "the next legal request should be a separate bounded Workstream "
                "implementation approval packet for exactly `SLC-001 / Seam 1 - "
                "Define protected classes and public-safe exclusion contract`.\n\n"
                "No seam is classified as impossible or route-blocked at BP3. Later "
                "seams are readiness-ordered, not approved for execution. Any seam "
                "that requires private setup, provider/model/runtime/cache/memory "
                "activation, real Owner memory, real agents, PR, merge, release, "
                "cleanup, or sibling mutation remains blocked until its future USER "
                "approval exists.\n\n"
                "## BP3 Verification Checklist By SLC\n\n"
                "- SLC-001 must prove protected artifact classes, private path "
                "exclusions, review-packet exclusion behavior, public-leak prevention, "
                "and rollback for accidental public exposure.\n"
                "- SLC-002 must prove provider/model/runtime actions stay unavailable, "
                "disabled copy is clear, sentToProvider remains false, canAcceptPrompts "
                "remains false, and no runtime action is created.\n"
                "- SLC-003 must prove cache and memory are separate consent surfaces, "
                "memory remains inactive, cache behavior remains inactive, and no "
                "learning/indexing/retrieval/personalization starts.\n"
                "- SLC-004 must prove install intent is a gate record, not execution, "
                "download, provider call, package activation, or capability enablement.\n"
                "- SLC-005 must prove Developer and Owner readiness gates are "
                "public-safe and preserve private repo/root/remote, GitHub Desktop "
                "private binding, backup/import, and lane identity boundaries.\n"
                "- SLC-006 must prove memory/agent schemas describe prerequisites only; "
                "real Owner memory, real agents, prompt routing, and provider execution "
                "remain future-gated.\n\n"
                "## Recommended First Workstream Seam\n\n"
                "Codex recommends `SLC-001 / Seam 1 - Define protected classes and "
                "public-safe exclusion contract` as the exact first future Workstream "
                "seam. The first SLC is SLC-001, but the first bounded Workstream "
                "approval packet should cover only Seam 1 unless USER explicitly "
                "approves a larger Workstream scope. Grouping all of SLC-001 as the "
                "first Workstream scope is not recommended by default because Seam 2 "
                "and Seam 3 depend on the protected-class contract produced by Seam 1.\n\n"
                "## Proof / Validation Matrix\n\n"
                "- Packet proof: validate the local USER folder and timestamped ZIP "
                "directly; reviewability remains separate from USER acceptance.\n"
                "- Branch planning proof: run branch-readiness planning fixtures for "
                "accepted BP1/BP2 traceability, BP3 no-implementation posture, technical "
                "metadata exclusion, and stale wording prevention.\n"
                "- Public leak proof: run public leak prevention validation for private "
                "paths, secrets, tokens, private URLs, private automation data, prompts, "
                "model artifacts, private screenshots, and memory content.\n"
                "- Provider-state proof: run provider-state validation for no provider "
                "execution, no model calls, no downloads, no prompt acceptance, no cache "
                "activation, and no memory activation.\n"
                "- Source-truth proof: run governance, source-owner, external-state, "
                "release-body, governance-efficiency, docs-inventory, and compile checks "
                "required by the active validation registry.\n\n"
                "## Route-Back And Blocker Rules\n\n"
                "- Route back to BP1 if USER changes the accepted product direction, "
                "vision scope, lane model, Owner AI end-state, or future-gated boundary.\n"
                "- Route back to BP2 if USER changes SLC order, affected surfaces, "
                "validator coverage, proof expectations, rollback posture, H1/LV/UTS "
                "expectations, or implementation constraints.\n"
                "- Hold BP3 if any future private/runtime/provider/cache/memory action "
                "would be needed to prove readiness.\n"
                "- Keep Workstream implementation pending until BP3 is accepted or "
                "waived and USER separately approves bounded implementation.\n\n"
                "## Exact Workstream Approval Packet Target After BP3 Acceptance\n\n"
                "If USER accepts or waives BP3, the next packet should ask only for "
                "bounded Workstream implementation approval for `SLC-001 / Seam 1 - "
                "Define protected classes and public-safe exclusion contract`. That "
                "packet must preserve the full eighteen-seam orchestration map, but "
                "its executable scope should stay on the first seam unless USER grants "
                "an explicit wider Workstream waiver.\n\n"
                "## Exact BP3 USER Decision Options\n\n"
                "- Accept BP3 as written and request a separate bounded Workstream "
                "implementation approval packet next.\n"
                "- Revise BP3 and name the exact orchestration, SLC, seam, proof, "
                "rollback, or future-gate change needed.\n"
                "- Waive remaining BP3 concerns and request a separate bounded "
                "Workstream implementation approval packet next.\n"
                "- Reject this carrier route and request a different FAM-007 path.\n"
                "- Hold BP3 for more review.\n"
            )
            analysis_status = (
                "Analysis Summary: BP3 Workstream Entry / Orchestration Validation "
                "packet for FAM-007 Owner AI Operational Foundation Gates.\n"
                "BP1 Contract Status: Complete - USER accepted the Owner AI "
                "Operational Foundation Gates Branch Vision.\n"
                "BP2 Contract Status: Complete - USER accepted the Owner AI "
                "Operational Foundation Gates Branch Plan.\n"
                "BP1 USER Gate State: USER Accepted\n"
                "BP2 USER Gate State: USER Accepted\n"
                "BP3 Packet Reviewability State: Reviewable\n"
                "BP3 USER Gate State: Pending USER Review\n"
                "SLC Traceability: Complete - SLC-001 through SLC-006 trace to "
                "accepted BP1 and accepted BP2.\n"
                "Seam Traceability: Complete - all eighteen accepted BP2 seams have "
                "BP3 readiness verdicts.\n"
                "Whole-Package Readiness Verdict: Reviewable and ready for USER BP3 "
                "decision; not implementation-approved.\n"
                "First Bounded Workstream Seam: SLC-001 / Seam 1 - Define protected "
                "classes and public-safe exclusion contract.\n"
                "Implementation Approval: Pending separate USER approval after BP3; "
                "this packet does not authorize Workstream implementation."
            )
            implementation_posture = (
                "Implementation Posture: BP3 is reviewable while USER BP3 approval "
                "is pending. Workstream implementation, private setup, real Owner "
                "memory, real agents, provider/model/runtime/cache/memory behavior, "
                "backup/import execution, PR, merge, release, cleanup, issue mutation, "
                "sibling-worktree mutation, AI Product Contract import, Private Dev "
                "ORIN import, and v1.8.0 remain pending USER decisions."
            )
            recommended_seam = (
                "Recommended First Bounded Workstream Seam: SLC-001 / Seam 1 - "
                "Define protected classes and public-safe exclusion contract, to "
                "be considered only after USER accepts or waives BP3 and separately "
                "approves Workstream implementation."
            )
            scan_result = (
                "Source-Truth Coverage: packet includes accepted BP1 Branch Vision "
                "context, accepted BP2 Branch Plan context, FAM-007 family vision, "
                "AI Runtime And Trust Architecture, active branch authority record, "
                "external branch plan/state context, branch artifact rules, phase "
                "governance, execution rules, validation registry, backlog, roadmap, "
                "and worktree-slot context needed for BP3."
            )
            checklist_status = (
                "Checklist Focus: BP3 validates accepted BP1/BP2 traceability, "
                "whole-package SLC order, first-seam recommendation, proof and "
                "validation lanes, public/private leak safety, provider no-exec "
                "posture, rollback posture, route-back criteria, and future-gated "
                "private/runtime decisions."
            )
            digest_status = (
                "Review Summary: START_HERE.md, WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md "
                "as the primary BP3 decision file, USER_BRANCH_VISION_REVIEW.md and "
                "USER_BRANCH_PLAN_REVIEW.md as supporting accepted BP1/BP2 context, "
                "required digest/checklist files, and copied source-truth files are "
                "loaded and digestible for USER review; BP3 remains pending USER "
                "approval, revision, waiver, rejection, or hold."
            )
    elif pr_stage1_packet:
        analysis_status = (
            "Analysis Summary: Governance Phase Lifecycle Reform packet is ready "
            "for PR Readiness Stage 1 analysis approval."
        )
        implementation_posture = (
            "Implementation Posture: this packet remains analysis-only; PR creation, "
            "merge, release, cleanup, runtime, provider, private, sidecar, and upload "
            "taxonomy actions remain pending USER approval."
        )
        recommended_seam = (
            "Recommended Next Phase: PR Readiness Stage 1 analysis for the "
            "Governance Phase Lifecycle Reform branch."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the lifecycle reform context "
            "plan, phase governance, execution mirrors, branch authority routing, "
            "USER hub model, branch artifact rules, validation registry, and review "
            "context needed for the PR Readiness Stage 1 decision."
        )
        checklist_status = (
            "Checklist Focus: for Governance PR Readiness Stage 1 approval review - "
            "lifecycle ownership, BP1/BP2/BP3 separation, local USER hub behavior, "
            "external-state split, mandatory timestamped ZIP uploads, sidecar deferral, and USER-facing "
            "metadata boundaries are represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_VISION_REVIEW.md, "
            "USER_BRANCH_PLAN_REVIEW.md, required digest/checklist files, and copied "
            "source-truth files are loaded and digestible for USER review; PR "
            "Readiness Stage 1 analysis remains pending USER approval."
        )
    elif pr_stage2_packet:
        analysis_status = (
            "Analysis Summary: PR Readiness Stage 1 Ready For Stage 2 for the "
            "FAM-007 Breakpoint 2 Dev/Owner skeleton action-gate readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: Stage 1 recorded no live PR, no-release-debt posture, "
            "merge-stable authority projection, and pending Stage 2 PR creation approval."
        )
        recommended_seam = (
            "Recommended Next Phase: PR Readiness Stage 2, PR creation and watcher/bot-review setup."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, branch index, branch record, branch plan, worktree slots, "
            "AI Runtime And Trust Architecture, FAM-007 family vision, AI Edition plan, "
            "branch-plan README, phase governance, development rules, codex modes, "
            "validation helper registry, and Stage 1 repair proof surfaces needed for "
            "the Stage 2 PR creation decision."
        )
        checklist_status = (
            "Checklist Focus: for PR Readiness Stage 1 repair review - branch identity, "
            "source-truth context, FAM-007 ownership, Breakpoint 2 product/workstream "
            "posture, no-live-PR posture, no-release-debt posture, merge-stable authority "
            "projection, backlog taxonomy, and private/runtime/provider/cache/memory exclusions "
            "are represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "digest/checklist files, and copied source-truth files are loaded and digestible "
            "for USER review; the contract records PR Readiness Stage 1 complete and "
            "Stage 2 PR creation as the next USER decision."
        )
    elif fam006_workstream_approval_review_packet:
        bp3_readiness_contract = (
            "\n## Plain-Language Workstream Approval Review Summary\n\n"
            "USER accepted BP1, BP2, and BP3 for the FAM-006 Dashboard Recording "
            "Start/Stop To Local File branch. This packet is the separate "
            "Workstream/runtime implementation approval review requested after "
            "BP3. It is reviewable, but Workstream/runtime implementation remains "
            "pending until USER approves this packet.\n\n"
            "## Accepted Planning Basis\n\n"
            "- BP1 answered: Option F planning solidified the Recording ecosystem "
            "vision and USER accepted the revised BP1 Branch Vision.\n"
            "- BP2 answered: Option C was accepted by USER as the Branch Plan.\n"
            "- BP3 answered: Option C was accepted by USER as one coherent bounded "
            "Workstream package.\n"
            "- The admitted package includes Dashboard Recording Card, Recording "
            "Studio, minimal Log Viewer Studio launch/folder shell, native/export "
            "log boundary, open-folder pre-session usability, issue #258 target "
            "reliability, deferred carryforward applicability, Element-to-Phase "
            "proof, rollback, validation, H1, Live Validation, UTS, visual-system "
            "inheritance, and slice/SLC/seam sequencing.\n\n"
            "## Complete Bounded Workstream Scope\n\n"
            "1. Dashboard Recording Card as the compact quick-access/status surface.\n"
            "2. Recording Studio as the focused recording control/status surface.\n"
            "3. Minimal Log Viewer Studio launch/folder shell for native/export "
            "folder access that directly supports Recording.\n"
            "4. Native NDAI logs as the normal product artifact and exported logs "
            "as USER-requested export artifacts.\n"
            "5. Open native/export folder behavior usable before a recording exists "
            "in the active session.\n"
            "6. Issue #258 Overlay Profile persistence as target-reliability proof "
            "for recording target correctness.\n\n"
            "## First Checkpoint And Continuation Rule\n\n"
            "SLC-051 / Seam 1 target reliability is the recommended first checkpoint "
            "because Recording target correctness depends on the active Overlay "
            "Profile contract. A green first seam is continuation proof, not package "
            "completion. Single-seam or single-slice authority is not granted. "
            "Continuation remains bounded by the admitted Option C package and must "
            "continue until Workstream Green, the approved scope is exhausted, a real "
            "named blocker appears, or USER explicitly waives the remaining package.\n\n"
            "## Future-Gated Boundaries\n\n"
            "Full Log Viewer Studio implementation, previous-log selection, export "
            "customization, tray recording controls, keybind implementation, full "
            "settings implementation, Native Log Loader full implementation, "
            "provider/model/private work, PR Readiness, issue closeout, merge, "
            "release, branch cleanup, Governance/FAM-007/neutral-main mutation, and "
            "unrelated runtime scope remain pending USER decisions.\n\n"
            "## Exact Workstream USER Decision Options\n\n"
            "- Approve bounded FAM-006 Workstream/runtime implementation for the "
            "accepted Option C package, starting with SLC-051 / Seam 1 target "
            "reliability and continuing under the bounded package rule.\n"
            "- Request a revision to package scope, sequencing, proof, validators, "
            "rollback, H1, Live Validation, UTS, or stop conditions.\n"
            "- Waive a specific approval issue while preserving the accepted package "
            "constraints.\n"
            "- Hold before Workstream/runtime implementation.\n"
            "- Reject or route back to BP3/BP2/BP1 if the accepted branch vision, "
            "engineering plan, or orchestration needs repair.\n"
        )
        analysis_status = (
            "Analysis Summary: Workstream/runtime implementation approval review "
            "packet for FAM-006 Dashboard Recording Start/Stop To Local File.\n"
            "BP1 USER Gate State: USER Accepted\n"
            "BP2 USER Gate State: USER Accepted\n"
            "BP3 USER Gate State: USER Accepted\n"
            "Workstream Approval Packet Reviewability State: Reviewable\n"
            "Workstream/runtime implementation approval remains Pending USER Review\n"
            "Workstream Approval Target: complete bounded Option C package.\n"
            "Entry Checkpoint: SLC-051 / Seam 1 target reliability."
        )
        implementation_posture = (
            "Implementation Posture: Workstream/runtime implementation remains "
            "pending until USER approves this packet. If approved, execution is "
            "bounded to the complete admitted Option C package and starts with "
            "SLC-051 / Seam 1 target reliability; a green first seam is "
            "continuation proof, not package completion."
        )
        recommended_seam = (
            "Entry Checkpoint: SLC-051 / Seam 1 target reliability and active "
            "Overlay Profile contract before Dashboard Recording Card, Recording "
            "Studio, minimal Log Viewer Studio shell, native/export boundary, "
            "and validation/Live Validation/UTS readiness."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes accepted BP1, accepted BP2, "
            "accepted BP3, FAM-006 Recording feature vision, family vision, active "
            "branch record/plan context, branch artifact rules, phase governance, "
            "development rules, codex modes, validation registry, backlog, roadmap, "
            "and worktree-slot context needed for FAM-006 Workstream approval review."
        )
        checklist_status = (
            "Checklist Focus: FAM-006 Workstream approval review - accepted BP1/BP2/"
            "BP3 traceability, complete Option C package scope, SLC-051 / Seam 1 "
            "entry checkpoint, continuation latch, native/export log boundary, "
            "open-folder pre-session usability, issue #258 target reliability, "
            "visual-system inheritance, H1/LV/UTS expectations, rollback posture, "
            "and future-gated boundaries."
        )
        digest_status = (
            "Review Summary: START_HERE.md, WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md, "
            "supporting accepted BP1/BP2 review files, required digest/checklist "
            "files, and copied source-truth files are loaded for USER review; packet "
            "wording treats SLC-051 / Seam 1 as the entry checkpoint for the complete "
            "accepted Option C package and keeps implementation approval pending."
        )
    elif workstream_package_approval_packet and is_fam007_owner_ai_foundation:
        bp3_readiness_contract = (
            "\n## Plain-Language Workstream Approval Summary\n\n"
            "USER accepted BP3 for FAM-007 Owner AI Operational Foundation Gates. "
            "This packet asks whether Codex may begin the complete bounded "
            "Workstream package that BP1, BP2, and BP3 already accepted: SLC-001 "
            "through SLC-006 and all eighteen accepted seams.\n\n"
            "The Workstream package starts at `SLC-001 / Seam 1 - Define protected "
            "classes and public-safe exclusion contract`. That seam is the first "
            "execution checkpoint, not the terminal scope. Later execution is expected "
            "to continue through the accepted same-branch SLC/seam sequence until "
            "Workstream Green, a real named blocker, validation failure requiring "
            "repair or route-back, or explicit USER waiver.\n\n"
            "## Accepted Planning Basis\n\n"
            "- BP1 accepted the Owner AI Operational Foundation Gates Branch Vision.\n"
            "- BP2 accepted the engineering plan for six public-safe gate/control "
            "deliverables.\n"
            "- BP3 accepted the orchestration map for SLC-001 through SLC-006 and "
            "all eighteen seams.\n"
            "- Workstream may implement public-safe controls, schemas, helper/"
            "validator behavior, fixtures, packet enforcement, and source-truth "
            "fold-down only inside that accepted package.\n\n"
            "## Complete Bounded Workstream Scope\n\n"
            "1. SLC-001 - Protected Artifact Exclusion Controls.\n"
            "2. SLC-002 - Provider/Runtime Consent-Shell Disabled States.\n"
            "3. SLC-003 - Memory-Versus-Cache Consent Gates.\n"
            "4. SLC-004 - Capability-Pack Install-Intent Gates.\n"
            "5. SLC-005 - Developer / Owner Lane Readiness Gates.\n"
            "6. SLC-006 - Owner AI Memory / Agent Foundation Gate Schemas.\n\n"
            "## Accepted Seam Sequence\n\n"
            "| Seam | Workstream intent |\n"
            "| --- | --- |\n"
            "| SLC-001 / Seam 1 - Define protected classes and public-safe exclusion contract | Name protected classes and the public-safe exclusion contract before any other gate references protected material. |\n"
            "| SLC-001 / Seam 2 - Enforce public packet/repo/bundle exclusion checks | Add direct exclusion checks for public repo, packet, bundle, and upload paths. |\n"
            "| SLC-001 / Seam 3 - Preserve acceptance/fold-down boundary for protected-asset policy | Keep accepted branch-local exclusion outcomes in the correct durable owner or external-state lane. |\n"
            "| SLC-002 / Seam 1 - Define disabled provider/runtime state contract | Define disabled provider/runtime states without creating executable provider/runtime behavior. |\n"
            "| SLC-002 / Seam 2 - Plan USER-facing disabled-state copy and review packet wording | Make disabled states understandable in USER-facing packet/review surfaces. |\n"
            "| SLC-002 / Seam 3 - Add no-execution proof linkage for BP3 | Link disabled state proof to provider-state and no-execution validation. |\n"
            "| SLC-003 / Seam 1 - Separate cache consent from memory consent | Keep cache and memory consent as separate blocked states. |\n"
            "| SLC-003 / Seam 2 - Plan blocked persistence states and consent error states | Define blocked persistence and consent-error states without persistence behavior. |\n"
            "| SLC-003 / Seam 3 - Preserve source-truth placement for future memory/cache policy | Route durable memory/cache policy to the proper source-truth owner. |\n"
            "| SLC-004 / Seam 1 - Define explicit install-intent state model | Define install intent as a gate record, not setup or execution. |\n"
            "| SLC-004 / Seam 2 - Plan blocked pending-install state and visible route-back | Make pending install state visible and reversible. |\n"
            "| SLC-004 / Seam 3 - Link install-intent gates to protected artifact and provider-state proof | Tie install intent to leak prevention and provider no-execution proof. |\n"
            "| SLC-005 / Seam 1 - Define lane identity without private setup | Define User/Public, Developer, and Owner readiness labels without creating private lanes. |\n"
            "| SLC-005 / Seam 2 - Plan readiness gates for later private setup approval | Name future setup gates without executing setup. |\n"
            "| SLC-005 / Seam 3 - Validate lane-readiness copy in USER-facing packet | Keep lane-readiness copy review-focused and metadata-safe. |\n"
            "| SLC-006 / Seam 1 - Define future prerequisite schema names and blocked states | Define prerequisite schemas for future memory/agent work without runtime authority. |\n"
            "| SLC-006 / Seam 2 - Plan no-real-memory/no-real-agent proof and public-safe examples | Keep examples synthetic/public-safe and prove no real memory or agent behavior. |\n"
            "| SLC-006 / Seam 3 - Link schema gates to BP3 whole-package orchestration | Connect schema gates back to the accepted whole-package route. |\n\n"
            "## Protected Artifact Classes And Public-Safe Exclusion Outcome\n\n"
            "Workstream should define and enforce a protected-class contract for private "
            "roots, private remotes, secrets, tokens, private prompts, memory content, "
            "private screenshots, private automation, model artifacts, Owner data, "
            "Developer lane artifacts, and Owner lane artifacts. The expected outcome "
            "is public repo, packet, bundle, and upload exclusion that can be proven "
            "without reading, moving, exporting, or uploading private material.\n\n"
            "## Likely Files And Surfaces\n\n"
            "- FAM-007 family vision and AI runtime/trust architecture for durable "
            "public/private, provider, cache, memory, permission, and lane policy.\n"
            "- Branch record as durable receipt/context only.\n"
            "- External branch plan/state and worktree state for mutable packet and "
            "phase posture.\n"
            "- USER review bundle helper for packet generation, timestamped ZIPs, "
            "metadata exclusion, stale wording checks, and packet validation.\n"
            "- Public leak-prevention, provider-state, branch-planning, external-state, "
            "source-owner, release-body, governance, docs-inventory, and compile "
            "validation surfaces.\n"
            "- Public-safe fixtures under the registered FAM-007 fixture surfaces when "
            "a seam needs negative proof.\n\n"
            "## Validators, Fixtures, And Proof Commands\n\n"
            "- `python dev\\orin_user_review_bundle.py --validate-workstream-entry-packet ... --require-implementation-ready`\n"
            "- `python dev\\orin_branch_governance_validation.py`\n"
            "- `python dev\\orin_branch_governance_validation.py --worktree-confinement-gate`\n"
            "- `python dev\\orin_branch_readiness_planning_fixture_validation.py`\n"
            "- `python dev\\orin_external_state_validation.py --root C:\\Nexus Governance State --repo C:\\Nexus Worktrees\\FAM-007 --require-root --require-stage4-records`\n"
            "- `python dev\\orin_ai_provider_state_validation.py`\n"
            "- `python dev\\orin_public_leak_prevention_validation.py`\n"
            "- `python dev\\orin_source_owner_marker_validation.py`\n"
            "- `python dev\\orin_release_body_validation.py`\n"
            "- `python dev\\orin_governance_efficiency_validation.py`\n"
            "- `python dev\\orin_docs_inventory_reform_audit.py`\n"
            "- `python -m compileall -q dev desktop Audio main.py nexus_visual`\n\n"
            "## Public / Private Leak Prevention Posture\n\n"
            "Workstream must keep private roots, private remotes, private paths, secrets, "
            "tokens, private prompts, private memory, private screenshots, model "
            "artifacts, private automation data, Owner data, and Developer/Owner "
            "lane artifacts out of public repo, packet, bundle, and upload surfaces. "
            "Proof must be public-safe, synthetic where examples are needed, and "
            "validator-backed.\n\n"
            "## Disabled-State And No-Execution Boundaries\n\n"
            "Provider-visible data remains none, sentToProvider remains false, "
            "canAcceptPrompts remains false, prompt/provider/model execution stays "
            "disabled, downloads/network/external calls stay blocked, runtime cache "
            "behavior stays inactive, memory/learning/personalization stays inactive, "
            "and real Owner memory and real agents stay future-gated. This package "
            "may create gates, schemas, disabled states, copy, fixtures, and validators; "
            "it may not activate the gated behavior.\n\n"
            "## Rollback / Repair Posture\n\n"
            "Each seam should be committed and validated as a reversible public-safe "
            "control change. If a seam creates drift, Codex should repair inside the "
            "active seam, regenerate the USER packet when packet-relevant, rerun "
            "validation, and route back to BP3/BP2 only when the accepted orchestration "
            "or plan changes.\n\n"
            "## Stop / Report Conditions\n\n"
            "- Main baseline advances and rebaseline/reconciliation is required.\n"
            "- A seam needs private setup, private roots/remotes, provider execution, "
            "runtime activation, cache/memory activation, real Owner memory, real "
            "agents, backup/import execution, PR, merge, release, cleanup, issue "
            "mutation, sibling-worktree mutation, AI Product Contract import, "
            "Private Dev ORIN import, or v1.8.0 work.\n"
            "- A validator fails and cannot be repaired inside the active accepted seam.\n"
            "- The accepted BP1/BP2/BP3 route changes and needs route-back.\n"
            "- USER-facing packet files would contain live operational state or "
            "technical byte-proof metadata.\n\n"
            "## USER Gates Preserved\n\n"
            "Hardening, Live Validation, PR Readiness, PR creation, merge, release, "
            "cleanup, issue mutation, sibling-worktree mutation, private setup, "
            "provider/model/runtime/cache/memory activation, backup/import execution, "
            "real Owner memory, real agents, AI Product Contract import, Private Dev "
            "ORIN import, and v1.8.0 remain future-gated.\n\n"
            "## Exact Workstream USER Decision Options\n\n"
            "- Approve complete bounded Workstream implementation for SLC-001 through "
            "SLC-006 and all eighteen accepted seams, starting at SLC-001 / Seam 1.\n"
            "- Request a revision to scope, seam order, proof, validators, rollback, "
            "H1/LV/UTS expectations, or stop conditions.\n"
            "- Waive a specific Workstream approval issue and keep the accepted package "
            "constraints.\n"
            "- Hold before Workstream execution.\n"
            "- Reject or route back to BP3/BP2 if orchestration or plan authority needs "
            "repair.\n"
        )
        analysis_status = (
            "Analysis Summary: Workstream implementation approval packet for FAM-007 "
            "Owner AI Operational Foundation Gates.\n"
            "BP1 USER Gate State: USER Accepted\n"
            "BP2 USER Gate State: USER Accepted\n"
            "BP3 USER Gate State: USER Approved\n"
            "Workstream Approval Packet Reviewability State: Reviewable\n"
            "Workstream Approval Target: complete bounded package across SLC-001 "
            "through SLC-006 and all eighteen accepted seams.\n"
            "Entry Checkpoint: SLC-001 / Seam 1 - Define protected classes and "
            "public-safe exclusion contract."
        )
        implementation_posture = (
            "Implementation Posture: complete bounded Workstream package approval "
            "is requested by this packet. The executable package is SLC-001 through "
            "SLC-006 and all eighteen accepted seams, starting at SLC-001 / Seam 1 "
            "and continuing until Workstream Green, a real named blocker, validation "
            "failure requiring repair or route-back, or explicit USER waiver."
        )
        recommended_seam = (
            "Entry Checkpoint: SLC-001 / Seam 1 - Define protected classes and "
            "public-safe exclusion contract."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes accepted BP1, accepted BP2, "
            "accepted BP3, FAM-007 family vision, AI Runtime And Trust Architecture, "
            "active branch receipt, external branch plan/state context, branch "
            "artifact rules, phase governance, development rules, codex modes, "
            "validation registry, backlog, roadmap, and worktree-slot context needed "
            "for complete bounded Workstream approval."
        )
        checklist_status = (
            "Checklist Focus: complete Workstream approval - accepted BP1/BP2/BP3 "
            "traceability, six-SLC package scope, all eighteen seams, entry checkpoint, "
            "protected artifact exclusion outcome, proof commands, rollback posture, "
            "future-gated private/runtime boundaries, and phase closeout expectation."
        )
        digest_status = (
            "Review Summary: START_HERE.md, WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md, "
            "supporting accepted BP1/BP2 review files, required digest/checklist "
            "files, and copied source-truth files are loaded for USER review; packet "
            "wording treats SLC-001 / Seam 1 as the entry checkpoint for the complete "
            "accepted package."
        )
    elif workstream_package_approval_packet:
        analysis_status = (
            "Analysis Summary: BP3 is accepted; USER is approving bounded Workstream "
            "package implementation for the admitted same-branch package."
        )
        implementation_posture = (
            "Implementation Posture: bounded Workstream package implementation is approved "
            "by this packet decision path with Seam 1 as the entry checkpoint. Continuation "
            "must proceed one active same-branch seam at a time until Workstream Green, a "
            "real named blocker, or explicit USER waiver."
        )
        recommended_seam = (
            "Entry Checkpoint: Seam 1, public-safe action-gate registry and exact USER "
            "decision proof."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, active branch plan "
            "context, worktree slots, AI Runtime And Trust Architecture, FAM-007 family "
            "vision, AI Edition plan, branch-plan README, phase governance, development "
            "rules, codex modes, validation helper registry, and review surfaces needed "
            "for bounded Workstream package approval."
        )
        checklist_status = (
            "Checklist Focus: Workstream package approval - accepted BP1/BP2/BP3 posture, "
            "entry seam proof, continuation latch, future-gated private/runtime/provider/"
            "cache/memory boundaries, and next lawful phase boundary to Hardening only "
            "after Workstream Green."
        )
        digest_status = (
            "Review Summary: START_HERE.md, WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md, "
            "supporting BP1/BP2 review files, required digest/checklist files, and copied "
            "source-truth files are loaded and digestible for USER review; packet wording "
            "treats Seam 1 as entry checkpoint, not terminal Workstream authority."
        )
    elif dev_owner_workstream_green_packet:
        analysis_status = (
            "Analysis Summary: Workstream Green for the FAM-007 Dev/Owner Skeleton "
            "Readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: all admitted public-safe Workstream proof seams "
            "are complete; Hardening H1 remains pending USER approval."
        )
        recommended_seam = (
            "Recommended Next Phase: Hardening H1, proof comparison and pressure testing."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, active external branch "
            "plan context, worktree slots, AI Runtime And Trust Architecture, FAM-007 "
            "family vision, AI Edition plan, branch-plan README, phase governance, "
            "development rules, codex modes, validation helper registry, and Workstream "
            "Green proof surfaces needed for the Hardening H1 decision."
        )
        checklist_status = (
            "Checklist Focus: Workstream Green review - action-gate registry, Dev/Owner "
            "readiness matrices, private root/remote safety, GitHub Desktop safety, "
            "backup/import deferral, provider/runtime/cache/memory deferral, packet/"
            "fixture/validator fold-down, and Hardening H1 boundary."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, "
            "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md, supporting BP1/BP2 review files, "
            "required digest/checklist files, and copied source-truth files are loaded "
            "and digestible for USER review; the contract records Workstream Green and "
            "routes only to Hardening H1 approval."
        )
    elif seam1_approval_packet:
        analysis_status = (
            "Analysis Summary: Workstream Entry Green; USER accepted the repaired "
            "branch contract for bounded Seam 1 implementation approval."
        )
        implementation_posture = (
            "Implementation Posture: Seam 1 is approved only for public-safe "
            "action-gate registry and exact USER decision proof."
        )
        recommended_seam = (
            "Approved First Seam: Seam 1, Action-gate registry and exact USER "
            "decision proof."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, branch plan, "
            "worktree slots, AI Runtime And Trust Architecture, FAM-007 family "
            "vision, AI Edition plan, branch-plan README, phase governance, "
            "development rules, codex modes, validation helper registry, and "
            "review surfaces needed for bounded Seam 1 approval."
        )
        checklist_status = (
            "Checklist Focus: for Workstream Entry decision-path repair - "
            "branch context, source-truth context, FAM-007 ownership, "
            "Breakpoint 2 product/workstream posture, approved Seam 1 proof path, "
            "AI Runtime And Trust Architecture placement, backlog taxonomy, and "
            "private/runtime/provider/cache/memory exclusions are represented for "
            "USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "Workstream Entry digest/checklist files, and copied source-truth files "
            "are loaded and digestible for USER review; the contract is branch-specific "
            "and records the bounded Seam 1 implementation approval boundary."
        )
    elif lv1_green_packet:
        analysis_status = (
            "Analysis Summary: Live Validation LV1 Green for the FAM-007 Breakpoint 2 "
            "Dev/Owner skeleton action-gate readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: LV1 recorded no-visible-runtime proof, UTS waiver, "
            "and user-facing shortcut validation waiver; PR Readiness Stage 1 remains "
            "pending USER approval."
        )
        recommended_seam = (
            "Recommended Next Phase: PR Readiness Stage 1 analysis."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, branch plan, "
            "worktree slots, AI Runtime And Trust Architecture, FAM-007 family "
            "vision, AI Edition plan, branch-plan README, phase governance, "
            "development rules, codex modes, validation helper registry, and "
            "LV1 no-visible-runtime proof surfaces needed for the next USER decision."
        )
        checklist_status = (
            "Checklist Focus: for Live Validation LV1 review - branch identity, "
            "source-truth context, FAM-007 ownership, Breakpoint 2 product/workstream "
            "posture, LV1 waiver proof, AI Runtime And Trust Architecture placement, "
            "backlog taxonomy, and private/runtime/provider/cache/memory exclusions are "
            "represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "digest/checklist files, and copied source-truth files are loaded and digestible "
            "for USER review; the contract records the Live Validation LV1 boundary and PR "
            "Readiness Stage 1 next decision."
        )
    elif dev_owner_live_validation_lv1_packet:
        analysis_status = (
            "Analysis Summary: Live Validation LV1 Green for the FAM-007 Dev/Owner "
            "Skeleton Readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: LV1 recorded no-visible-runtime proof and UTS "
            "waiver evidence for a proof-only branch; PR Readiness Stage 1 remains "
            "pending USER approval."
        )
        recommended_seam = (
            "Recommended Next Phase: PR Readiness Stage 1 analysis."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, worktree slots, AI "
            "Runtime And Trust Architecture, FAM-007 family vision, AI Edition plan, "
            "branch-plan README, phase governance, development rules, codex modes, "
            "validation helper registry, public leak-prevention validator, and LV1 "
            "no-visible-runtime proof surfaces needed for the next USER decision."
        )
        checklist_status = (
            "Checklist Focus: Live Validation LV1 review - no-visible-runtime proof, "
            "UTS waiver evidence, action gates, Dev/Owner matrices, private root/remote "
            "safety, backup/import deferral, provider/runtime/cache/memory deferral, "
            "packet/fixture/validator/source-truth fold-down, external state proof, and "
            "PR Readiness Stage 1 analysis-only boundary are represented."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "digest/checklist files, and copied source-truth files are loaded and "
            "digestible for USER review; the contract records the Live Validation LV1 "
            "boundary and PR Readiness Stage 1 next decision."
        )
    elif dev_owner_hardening_h1_packet:
        analysis_status = (
            "Analysis Summary: Hardening H1 Green for the FAM-007 Dev/Owner "
            "Skeleton Readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: Hardening H1 compared the completed public-safe "
            "Workstream proof against accepted BP1, BP2, BP3, fixture, validator, "
            "packet, branch-record, and external-state boundaries; Live Validation "
            "LV1 remains pending USER approval."
        )
        recommended_seam = (
            "Recommended Next Phase: Live Validation LV1, no-visible-runtime proof and UTS waiver digestion."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, worktree slots, AI "
            "Runtime And Trust Architecture, FAM-007 family vision, AI Edition plan, "
            "branch-plan README, phase governance, development rules, codex modes, "
            "validation helper registry, public leak-prevention validator, and H1 "
            "proof surfaces needed for the next USER decision."
        )
        checklist_status = (
            "Checklist Focus: Hardening H1 review - action gates, Dev/Owner matrices, "
            "private root/remote safety, backup/import deferral, provider/runtime/cache/"
            "memory deferral, packet/fixture/validator/source-truth fold-down, external "
            "state proof, and LV1 no-visible-runtime boundary are represented."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "digest/checklist files, and copied source-truth files are loaded and "
            "digestible for USER review; the contract records the Hardening H1 boundary "
            "and Live Validation LV1 next decision."
        )
    elif hardening_h1_packet:
        analysis_status = (
            "Analysis Summary: Hardening H1 Green for the FAM-007 Breakpoint 2 Dev/Owner "
            "skeleton action-gate readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: Hardening H1 compared all public-safe proof and repaired "
            "stale duplicate ledger wording; Live Validation LV1 remains pending USER approval."
        )
        recommended_seam = (
            "Recommended Next Phase: Live Validation LV1, no-visible-runtime proof and UTS waiver digestion."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, branch plan, "
            "worktree slots, AI Runtime And Trust Architecture, FAM-007 family "
            "vision, AI Edition plan, branch-plan README, phase governance, "
            "development rules, codex modes, validation helper registry, and "
            "Hardening H1 proof surfaces needed for the next USER decision."
        )
        checklist_status = (
            "Checklist Focus: for Hardening H1 review - branch identity, "
            "source-truth context, FAM-007 ownership, Breakpoint 2 product/workstream "
            "posture, H1 comparison proof, AI Runtime And Trust Architecture placement, "
            "backlog taxonomy, and private/runtime/provider/cache/memory exclusions are "
            "represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "digest/checklist files, and copied source-truth files are loaded and digestible "
            "for USER review; the contract records the Hardening H1 boundary and Live "
            "Validation LV1 next decision."
        )
    elif workstream_green_packet:
        analysis_status = (
            "Analysis Summary: Workstream Green for the FAM-007 Breakpoint 2 Dev/Owner "
            "skeleton action-gate readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: Seams 1 through 4 are implemented as public-safe proof "
            "only; Hardening H1 remains pending USER approval."
        )
        recommended_seam = (
            "Recommended Next Phase: Hardening H1, Workstream proof comparison."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, branch plan, "
            "worktree slots, AI Runtime And Trust Architecture, FAM-007 family "
            "vision, AI Edition plan, branch-plan README, phase governance, "
            "development rules, codex modes, validation helper registry, and "
            "Workstream Green proof surfaces needed for the next USER decision."
        )
        checklist_status = (
            "Checklist Focus: for Workstream Green review - branch identity, "
            "source-truth context, FAM-007 ownership, Breakpoint 2 product/workstream "
            "posture, Seams 1 through 4 proof, AI Runtime And Trust Architecture placement, "
            "backlog taxonomy, and private/runtime/provider/cache/memory exclusions are "
            "represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "Workstream Entry digest/checklist files, and copied source-truth files "
            "are loaded and digestible for USER review; the contract records the "
            "Workstream Green boundary and Hardening H1 next decision."
        )
    elif seam1_completion_packet:
        analysis_status = (
            "Analysis Summary: Seam 1 complete for the FAM-007 Breakpoint 2 Dev/Owner "
            "skeleton action-gate readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: Seam 1 action-gate registry and exact USER decision "
            "proof are implemented as public-safe proof only; Seam 2 remains pending USER approval."
        )
        recommended_seam = (
            "Recommended Next Seam: Seam 2, Private/public boundary and private remote safety proof."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, branch plan, "
            "worktree slots, AI Runtime And Trust Architecture, FAM-007 family "
            "vision, AI Edition plan, branch-plan README, phase governance, "
            "development rules, codex modes, validation helper registry, and "
            "Seam 1 proof surfaces needed for the next USER decision."
        )
        checklist_status = (
            "Checklist Focus: for Seam 1 completion review - branch identity, "
            "source-truth context, FAM-007 ownership, Breakpoint 2 product/workstream "
            "posture, Seam 1 proof, AI Runtime And Trust Architecture placement, backlog "
            "taxonomy, and private/runtime/provider/cache/memory exclusions are represented "
            "for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "Workstream Entry digest/checklist files, copied source-truth files, branch "
            "plan, branch record, fixture proof, and validator proof are loaded and "
            "digestible for USER review; Seam 2 remains governed by Workstream continuation, not a new per-seam approval, unless a real blocker, explicit waiver, or backlog split is recorded."
        )
    elif is_fam007_breakpoint_2:
        analysis_status = (
            "Analysis Summary: Workstream Entry analysis is complete/green for the "
            "FAM-007 Breakpoint 2 Dev/Owner skeleton action-gate readiness carrier."
        )
        implementation_posture = (
            "Implementation Posture: Workstream implementation remains pending USER "
            "approval and is not authorized by this packet until USER accepts or "
            "waives the repaired USER_BRANCH_PLAN_REVIEW.md contract and approves "
            "bounded Workstream package execution with Seam 1 as the entry checkpoint."
        )
        recommended_seam = (
            "Recommended First Seam: Seam 1, Action-gate registry and exact USER "
            "decision proof."
        )
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, branch plan, "
            "worktree slots, AI Runtime And Trust Architecture, FAM-007 family "
            "vision, AI Edition plan, branch-plan README, phase governance, "
            "development rules, codex modes, validation helper registry, and "
            "review surfaces needed for Workstream Entry contract repair."
        )
        checklist_status = (
            "Checklist Focus: for Workstream Entry packet repair - branch "
            "source-truth context, FAM-007 ownership, Breakpoint 2 "
            "product/workstream posture, Seam 1 proof path, AI Runtime And Trust "
            "Architecture placement, backlog taxonomy, and private/runtime/provider/"
            "cache/memory exclusions are represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "Workstream Entry digest/checklist files, and copied source-truth files "
            "are loaded and digestible for USER review; the contract is branch-specific "
            "and records the recommended Seam 1 approval boundary."
        )
    else:
        analysis_status = (
            "Analysis Summary: Stage 2 setup is green; this packet supports "
            "Workstream Entry final decision review only."
        )
        implementation_posture = (
            "Implementation Posture: Workstream implementation remains pending "
            "USER approval and is not authorized by this packet."
        )
        recommended_seam = ""
        scan_result = (
            "Source-Truth Coverage: packet includes the Main router, feature backlog, "
            "prebeta roadmap, active branch index, branch record, branch plan, "
            "worktree slots, AI Runtime And Trust Architecture, FAM-007 family "
            "vision, AI Edition plan, branch-plan README, phase governance, "
            "development rules, codex modes, validation helper registry, and "
            "governance inventory review surfaces selected for Stage 2 inspection."
        )
        checklist_status = (
            "Checklist Focus: for Stage 2 packet review - branch identity, "
            "source-truth context, FAM-007 ownership, AI Runtime And Trust "
            "Architecture placement, backlog taxonomy, product/workstream carrier "
            "posture, and private/runtime/provider/cache/memory exclusions are "
            "represented for USER inspection."
        )
        digest_status = (
            "Review Summary: START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, required "
            "Workstream Entry digest/checklist files, and copied source-truth files "
            "are loaded and digestible for USER review."
        )
    copied_sources = "\n".join(f"- `{source_rel}` -> `{copied_rel}`" for source_rel, copied_rel in copied)
    pending = "\n".join(f"- {decision}" for decision in pending_user_decisions) or "- None recorded."
    common = (
        f"Decision Path: {packet_status}\n"
        f"USER Decision: {exact_user_decision}\n"
    )
    if bp3_packet:
        common += (
            "BP3 Packet Reviewability State: Reviewable\n"
            "BP3 USER Gate State: Pending USER Review\n"
        )
    files: dict[str, str] = {
        "USER_REVIEW_FOLDER_AND_FILE_DIGEST.md": (
            "# USER Review Folder And File Digest\n\n"
            f"{common}"
            f"Folder: `{packet_folder}`\n"
            f"Upload ZIP: `{export_zip}`\n"
            f"{digest_status}\n\n"
            "## Copied Repo Files\n\n"
            f"{copied_sources}\n"
        ),
        "GOVERNANCE_REQUIRED_FILES_SCAN.md": (
            "# Governance Required Files Scan\n\n"
            f"{common}"
            f"{scan_result}\n"
        ),
        "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md": (
            "# Workstream Entry Analysis Digest\n\n"
            f"{common}"
            f"{analysis_status}\n"
            f"{implementation_posture}\n"
            f"{recommended_seam}"
            f"{bp3_readiness_contract}\n\n"
            "## Pending Gates\n\n"
            f"{pending}\n"
        ),
        "BRANCH_VISION_VALIDATION_CHECKLIST.md": (
            "# Branch Vision Validation Checklist\n\n"
            f"{common}"
            f"{checklist_status}\n"
        ),
    }
    written: list[Path] = []
    for name, text in files.items():
        path = target / name
        path.write_text(text, encoding="utf-8")
        written.append(path.resolve())
    return written


def _packet_text_status(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).casefold()
    bp1_markers = (
        "bp1 branch vision review",
        "user_branch_vision_review.md",
        "user branch vision review gate",
    )
    bp2_markers = (
        "bp2 branch plan review",
        "user_branch_plan_review.md",
        "user branch plan review gate",
    )
    bp3_markers = (
        "bp3 orchestration",
        "workstream entry / orchestration",
        "workstream entry orchestration",
    )
    pending_gate_markers = (
        "user gate state: pending user review",
        "user gate state: user revision requested",
        "user gate state: user rejected",
        "user gate state: user blocked",
    )
    reviewable_without_closed_gate = (
        "packet reviewability state: reviewable" in normalized
        and not any(
            marker in normalized
            for marker in (
                "user gate state: user accepted",
                "user gate state: user approved",
                "user gate state: user waived",
            )
        )
    )
    if any(marker in normalized for marker in pending_gate_markers) or reviewable_without_closed_gate:
        if any(marker in normalized for marker in bp3_markers):
            return DECISION_STATUS_BP3_ORCHESTRATION_REVIEW
        if any(marker in normalized for marker in bp2_markers):
            return DECISION_STATUS_BP2_BRANCH_PLAN_REVIEW
        if any(marker in normalized for marker in bp1_markers):
            return DECISION_STATUS_BP1_BRANCH_VISION_REVIEW

    implementation_markers = (
        "approve complete bounded workstream package implementation",
        "approve complete bounded workstream implementation",
        "complete bounded workstream package implementation",
        "complete bounded workstream implementation",
        "approve bounded workstream package implementation",
        "approve bounded workstream implementation",
        "bounded workstream package implementation",
        "workstream package implementation approval",
        "approve workstream implementation",
        "workstream implementation approval",
    )
    blocking_markers = (
        "implementation remains blocked",
        "implementation not yet authorized",
        "does not approve bounded workstream implementation",
        "does not approve workstream implementation",
        "do not approve bounded workstream implementation",
        "do not approve workstream implementation",
        "not approve bounded workstream implementation",
        "not approve workstream implementation",
        "does not authorize workstream implementation",
        "blocks workstream implementation",
        "before workstream implementation",
        "workstream implementation remains pending",
        "workstream implementation remains a pending user decision",
        "pending user decision: workstream implementation",
    )
    if any(marker in normalized for marker in implementation_markers) and not any(
        marker in normalized for marker in blocking_markers
    ):
        return DECISION_STATUS_IMPLEMENTATION_READY

    repair_markers = (
        "branch readiness stage 2 repair/revalidation",
        "repair/revalidation",
        "repair before workstream implementation",
        "returning to branch readiness",
    )
    if any(marker in normalized for marker in repair_markers):
        return DECISION_STATUS_REPAIR_REVALIDATION

    bp1_review_markers = (
        "bp1 branch vision review",
        "bp1 user branch vision review",
        "bp1 review packet",
    )
    bp1_decision_markers = (
        "authorize bp2 user branch plan review only",
        "bp2 remains pending",
        "bp2 user branch plan review remains pending",
    )
    if any(marker in normalized for marker in bp1_review_markers) and any(
        marker in normalized for marker in bp1_decision_markers
    ):
        return DECISION_STATUS_BP1_BRANCH_VISION_REVIEW

    bp2_review_markers = (
        "bp2 branch plan review",
        "bp2 user branch plan review",
        "user_branch_plan_review.md as the primary bp2 decision file",
    )
    bp2_decision_markers = (
        "accepted bp1 branch vision is the planning basis",
        "bp2 user branch plan review packet is reviewable",
        "bp2 remains pending user acceptance",
        "bp3 remains pending",
    )
    if any(marker in normalized for marker in bp2_review_markers) and any(
        marker in normalized for marker in bp2_decision_markers
    ):
        return DECISION_STATUS_BP2_BRANCH_PLAN_REVIEW

    final_review_markers = (
        "workstream entry final decision review",
        "final workstream entry decision",
    )
    if any(marker in normalized for marker in final_review_markers):
        return DECISION_STATUS_WORKSTREAM_ENTRY_REVIEW

    workstream_approval_review_markers = (
        "workstream implementation approval review",
        "workstream/runtime implementation remains pending until user approves",
        "bounded fam-006 workstream/runtime implementation approval packet",
        "does user approve bounded fam-006 workstream/runtime implementation",
    )
    if any(marker in normalized for marker in workstream_approval_review_markers):
        return DECISION_STATUS_WORKSTREAM_IMPLEMENTATION_APPROVAL_REVIEW

    live_validation_review_markers = (
        "live validation final decision review",
        "live validation lv1 is green",
        "pr readiness stage 1 remains pending user approval",
    )
    if any(marker in normalized for marker in live_validation_review_markers):
        return DECISION_STATUS_LIVE_VALIDATION_REVIEW

    pr_stage1_review_markers = (
        "pr readiness stage1 approval review",
        "pr readiness stage1 repair review",
        "pr readiness stage 1 analysis remains pending user approval",
        "pr readiness stage 1 analysis approval",
    )
    if any(marker in normalized for marker in pr_stage1_review_markers):
        return DECISION_STATUS_PR_READINESS_STAGE1_REVIEW

    pr_stage2_review_markers = (
        "pr readiness stage2 review",
        "pr readiness stage 1 ready for stage 2",
        "pr readiness stage 2 pr creation",
        "stage 2 pr creation remains pending user approval",
    )
    if any(marker in normalized for marker in pr_stage2_review_markers):
        return DECISION_STATUS_PR_READINESS_STAGE2_REVIEW

    hardening_review_markers = (
        "hardening final decision review",
        "hardening h1 is green",
        "live validation lv1 remains pending user approval",
    )
    if any(marker in normalized for marker in hardening_review_markers):
        return DECISION_STATUS_HARDENING_REVIEW

    return DECISION_STATUS_UNKNOWN


def _field_present(text: str, field_name: str) -> bool:
    pattern = re.compile(rf"^{re.escape(field_name)}\s*:", re.IGNORECASE | re.MULTILINE)
    return bool(pattern.search(text))


def _field_value(text: str, field_name: str) -> str:
    pattern = re.compile(
        rf"^{re.escape(field_name)}\s*:\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _review_marker_or_section_value(text: str, marker: str) -> str:
    line_value = _field_value(text, marker)
    if line_value:
        return line_value
    return _section(text, marker.removesuffix(":")).strip()


def _normalized_gate_value(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value).strip().casefold()
    return normalized.split(" - ", 1)[0].strip()


def _exact_decision_text(packet_files: Mapping[str, str]) -> str:
    return "\n".join(
        text
        for file_name, text in sorted(packet_files.items())
        if _packet_file_basename(file_name) in WORKSTREAM_ENTRY_PACKET_DECISION_FILES
        or _packet_file_basename(file_name)
        in {
            USER_BRANCH_VISION_REVIEW_FILE,
            USER_BRANCH_PLAN_REVIEW_FILE,
            PR_READINESS_STAGE1_REVIEW_FILE,
        }
    )


def _branch_planning_review_gate_state_failures(
    packet_files: Mapping[str, str],
) -> list[str]:
    failures: list[str] = []
    generated_files = {
        file_name: text
        for file_name, text in packet_files.items()
        if _packet_file_basename(file_name) in USER_FACING_GENERATED_FILES
    }
    all_review_text = _exact_decision_text(packet_files)
    normalized_all_review_text = re.sub(r"\s+", " ", all_review_text).casefold()
    branch_planning_context = any(
        marker in normalized_all_review_text
        for marker in (
            "bp1",
            "bp2",
            "bp3",
            "user_branch_vision_review.md",
            "user_branch_plan_review.md",
            "user branch vision review",
            "user branch plan review",
            "workstream entry / orchestration",
        )
    )
    if not branch_planning_context:
        return failures

    reviewability_values: list[tuple[str, str]] = []
    user_gate_values: list[tuple[str, str]] = []
    for file_name, text in sorted(generated_files.items()):
        reviewability_value = _field_value(text, "Packet Reviewability State")
        if reviewability_value:
            normalized = _normalized_gate_value(reviewability_value)
            reviewability_values.append((file_name, normalized))
            if normalized not in BRANCH_PLANNING_PACKET_REVIEWABILITY_VALUES:
                failures.append(
                    f"{file_name}: invalid Packet Reviewability State '{reviewability_value}'"
                )
        user_gate_value = _field_value(text, "USER Gate State")
        if user_gate_value:
            normalized = _normalized_gate_value(user_gate_value)
            user_gate_values.append((file_name, normalized))
            if normalized not in BRANCH_PLANNING_USER_GATE_VALUES:
                failures.append(f"{file_name}: invalid USER Gate State '{user_gate_value}'")

    if reviewability_values and not user_gate_values:
        failures.append(
            "USER Review Packet Phase-State Conflict: Packet Reviewability State "
            "appears without USER Gate State"
        )
    if user_gate_values and not reviewability_values:
        failures.append(
            "USER Review Packet Phase-State Conflict: USER Gate State appears "
            "without Packet Reviewability State"
        )

    implementation_requested = any(
        marker in normalized_all_review_text
        for marker in BRANCH_PLANNING_IMPLEMENTATION_REQUEST_MARKERS
    ) and not any(
        marker in normalized_all_review_text
        for marker in BRANCH_PLANNING_IMPLEMENTATION_BLOCKING_MARKERS
    )
    pending_gate_files = [
        file_name
        for file_name, normalized in user_gate_values
        if normalized in BRANCH_PLANNING_PENDING_USER_GATE_VALUES
    ]
    if pending_gate_files and implementation_requested:
        failures.append(
            "Packet Validation Treated As USER Acceptance: implementation approval "
            "wording appears while USER Gate State is still pending, revision-requested, "
            f"rejected, or blocked in {', '.join(pending_gate_files)}"
        )

    for file_name in (USER_BRANCH_VISION_REVIEW_FILE, USER_BRANCH_PLAN_REVIEW_FILE):
        text = _packet_file_text(packet_files, file_name)
        if not text:
            continue
        display_name = _packet_file_path(packet_files, file_name)
        reviewability_state = _normalized_gate_value(
            _review_marker_or_section_value(text, "Packet Reviewability State:")
        )
        user_gate_state = _normalized_gate_value(
            _review_marker_or_section_value(text, "USER Gate State:")
        )
        if reviewability_state and reviewability_state not in BRANCH_PLANNING_PACKET_REVIEWABILITY_VALUES:
            failures.append(
                f"{display_name}: invalid Packet Reviewability State "
                f"'{reviewability_state}'"
            )
        if user_gate_state and user_gate_state not in BRANCH_PLANNING_USER_GATE_VALUES:
            failures.append(f"{display_name}: invalid USER Gate State '{user_gate_state}'")
        if (
            implementation_requested
            and user_gate_state in BRANCH_PLANNING_PENDING_USER_GATE_VALUES
        ):
            failures.append(
                "Review Gate Bypass: implementation approval wording appears while "
                f"{display_name} USER Gate State is '{user_gate_state}'"
            )

    branch_plan_review = _packet_file_text(packet_files, USER_BRANCH_PLAN_REVIEW_FILE)
    if branch_plan_review:
        contract_status = _normalized_gate_value(
            _review_marker_or_section_value(branch_plan_review, "Contract Status:")
        )
        blocking_contract = contract_status.startswith(
            (
                "draft",
                "pending user response",
                "pending codex digest",
                "pending user confirmation",
            )
        )
        if blocking_contract and implementation_requested:
            failures.append(
                "Packet Validation Treated As USER Acceptance: implementation approval "
                "wording appears while USER_BRANCH_PLAN_REVIEW.md Contract Status "
                f"is '{contract_status}'"
            )
    return failures


def _validate_workstream_entry_packet_decision_path(
    packet_files: Mapping[str, str],
    *,
    expected_branch: str,
    expected_head: str,
    expected_origin_main: str,
    require_implementation_ready: bool = False,
    enforce_identity: bool = False,
    actual_file_count: int | None = None,
) -> WorkstreamEntryPacketDecisionPathResult:
    failures: list[str] = []
    failures.extend(_unresolved_template_placeholder_failures(packet_files))
    if enforce_identity:
        failures.extend(
            _packet_identity_failures(
                packet_files,
                expected_branch=expected_branch,
                expected_head=expected_head,
                expected_origin_main=expected_origin_main,
            )
        )
    failures.extend(
        _packet_count_consistency_failures(
            packet_files,
            actual_file_count=actual_file_count,
        )
    )
    failures.extend(_user_facing_technical_metadata_failures(packet_files))
    failures.extend(_user_branch_plan_stale_bp1_wording_failures(packet_files))
    failures.extend(_fam007_dev_owner_lv1_substantive_failures(packet_files))
    failures.extend(_fam007_bp2_plan_substantive_failures(packet_files))
    failures.extend(_fam007_bp2_support_bp1_context_failures(packet_files))
    failures.extend(_bp1_packet_phase_language_failures(packet_files))
    failures.extend(_fam006_bp3_support_context_failures(packet_files))
    failures.extend(_branch_planning_review_gate_state_failures(packet_files))
    failures.extend(_pr_stage1_review_failures(packet_files))
    failures.extend(_user_branch_vision_substantive_failures(packet_files))
    for required_file in WORKSTREAM_ENTRY_PACKET_REQUIRED_FILES:
        if not _packet_file_present(packet_files, required_file):
            failures.append(f"{required_file}: required Workstream Entry packet file is missing")

    start_here = packet_files.get("START_HERE.md", "")
    if not _field_present(start_here, "USER Decision This Packet Supports"):
        failures.append("START_HERE.md: USER Decision This Packet Supports field is missing")
    workstream_digest = _packet_file_text(packet_files, "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md")
    if "USER Decision" not in workstream_digest:
        failures.append("WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md: USER Decision field is missing")

    file_statuses: dict[str, str] = {}
    for file_name in WORKSTREAM_ENTRY_PACKET_DECISION_FILES:
        text = _packet_file_text(packet_files, file_name)
        if not text:
            continue
        display_name = _packet_file_path(packet_files, file_name)
        status = _packet_text_status(text)
        file_statuses[display_name] = status
        if status == DECISION_STATUS_UNKNOWN:
            failures.append(f"{display_name}: next legal phase / implementation posture is not machine-readable")

    distinct_statuses = {status for status in file_statuses.values() if status != DECISION_STATUS_UNKNOWN}
    if len(distinct_statuses) > 1:
        joined = ", ".join(f"{file_name}={status}" for file_name, status in sorted(file_statuses.items()))
        failures.append(f"Workstream Entry packet decision-path conflict: {joined}")

    if len(distinct_statuses) == 1:
        status = next(iter(distinct_statuses))
    else:
        status = DECISION_STATUS_UNKNOWN

    if require_implementation_ready and status != DECISION_STATUS_IMPLEMENTATION_READY:
        joined = ", ".join(f"{file_name}={status_value}" for file_name, status_value in sorted(file_statuses.items()))
        failures.append(
            "Workstream Entry packet blocks implementation approval: "
            f"status={status}; files={joined}"
        )

    return WorkstreamEntryPacketDecisionPathResult(status=status, failures=failures)


def validate_workstream_entry_packet_folder(
    packet_dir: Path,
    *,
    expected_branch: str,
    expected_head: str,
    expected_origin_main: str,
    require_implementation_ready: bool = False,
) -> WorkstreamEntryPacketDecisionPathResult:
    packet_files: dict[str, str] = {}
    all_files = (
        sorted(path for path in packet_dir.rglob("*") if path.is_file())
        if packet_dir.exists()
        else []
    )
    for path in all_files:
        if path.suffix.lower() not in {".md", ".txt", ".json"}:
            continue
        packet_files[path.relative_to(packet_dir).as_posix()] = path.read_text(encoding="utf-8")
    return _validate_workstream_entry_packet_decision_path(
        packet_files,
        expected_branch=expected_branch,
        expected_head=expected_head,
        expected_origin_main=expected_origin_main,
        require_implementation_ready=require_implementation_ready,
        enforce_identity=True,
        actual_file_count=len(all_files),
    )


def build_bundle(
    *,
    review_root_name: str,
    worktree_label: str | None,
    allow_custom_review_path: bool,
    custom_review_path_reason: str | None,
    files: list[str],
    title: str,
    clear: bool,
    review_purpose: str,
    validation_summary: str,
    review_order: list[str],
    exact_user_decision: str,
    pending_user_decisions: list[str],
    expected_file_count: int | None,
    review_export_zip: Path | None,
    stage1_outcome: str,
) -> tuple[Path, Path]:
    raise RuntimeError("Retired publication mutation route; use the installed selected USER publication owner.")
    custom_root = review_root_name != DEFAULT_REVIEW_ROOT_NAME
    custom_label = worktree_label is not None
    if (custom_root or custom_label) and not allow_custom_review_path:
        raise ValueError(
            "Custom review paths are blocked by default. Use the stable "
            r"C:\Nexus USER\<worktree-label> destination, or pass "
            "--allow-custom-review-path with --custom-review-path-reason."
        )
    if allow_custom_review_path and not custom_review_path_reason:
        raise ValueError("--custom-review-path-reason is required with --allow-custom-review-path")

    desktop = _desktop_path()
    label = _worktree_label(worktree_label)
    review_root, target = _safe_target(desktop, review_root_name, label)
    if target.exists():
        _clear_target(target)
    target.mkdir(parents=True, exist_ok=True)
    user_review_dir = target / USER_REVIEW_DIR_NAME
    review_aids_dir = target / REVIEW_AIDS_DIR_NAME
    source_context_dir = target / SOURCE_TRUTH_CONTEXT_DIR_NAME
    user_review_dir.mkdir(parents=True, exist_ok=True)
    review_aids_dir.mkdir(parents=True, exist_ok=True)
    source_context_dir.mkdir(parents=True, exist_ok=True)

    copied = [
        _copy_file(file_name, target, copy_name, subdir=SOURCE_TRUTH_CONTEXT_DIR_NAME)
        for file_name, copy_name in zip(files, _copy_names(files), strict=True)
    ]
    copied_count = len(copied)
    copied_targets = {(target / copied_rel).resolve() for _source_rel, copied_rel in copied}
    expected_count = expected_file_count if expected_file_count is not None else copied_count
    if expected_count != copied_count:
        raise ValueError(
            "Review bundle file count mismatch: "
            f"expected {expected_count} repo files, copied {copied_count}"
        )
    created_at_dt = datetime.now()
    created_at = created_at_dt.isoformat(timespec="seconds")

    source_branch = _git_output("branch", "--show-current")
    source_head = _git_output("rev-parse", "HEAD")
    upstream = _git_output("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    origin_main = _git_output("rev-parse", "origin/main")
    export_zip = _export_zip_path(review_root, label, created_at_dt)
    if review_export_zip is not None:
        requested_export_zip = review_export_zip.resolve()
        if requested_export_zip.parent != review_root.resolve():
            raise ValueError(
                "Review export zip override must live beside the local USER hub folder: "
                f"expected parent={review_root.resolve()} actual parent={requested_export_zip.parent}"
            )
        name_failures = _timestamped_export_zip_name_failures(requested_export_zip, label)
        if name_failures:
            raise ValueError("; ".join(name_failures))
        export_zip = requested_export_zip
    normalized_decision = exact_user_decision.casefold()
    workstream_package_approval_packet = (
        source_branch in FAM007_WORKSTREAM_PACKAGE_APPROVAL_BRANCHES
        and any(
            marker in normalized_decision
            for marker in BRANCH_PLANNING_IMPLEMENTATION_REQUEST_MARKERS
        )
        and not any(
            marker in normalized_decision
            for marker in BRANCH_PLANNING_IMPLEMENTATION_BLOCKING_MARKERS
        )
    )
    is_fam006_recording = (
        source_branch == "feature/fam-006-dashboard-recording-start-stop-local-file"
    )
    fam006_workstream_approval_review_packet = (
        _is_fam006_workstream_implementation_approval_review(
            normalized_decision,
            is_fam006_recording=is_fam006_recording,
        )
    )
    seam1_approval_packet = (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
        and "approve bounded workstream implementation" in normalized_decision
    )
    seam1_completion_packet = (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
        and "approve or revise seam 2" in exact_user_decision.casefold()
    )
    workstream_green_packet = (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
        and "approve bounded hardening h1" in exact_user_decision.casefold()
    )
    dev_owner_workstream_green_packet = (
        source_branch == "feature/fam-007-dev-owner-skeleton-readiness"
        and "approve bounded hardening h1" in normalized_decision
    )
    dev_owner_hardening_h1_packet = (
        source_branch == "feature/fam-007-dev-owner-skeleton-readiness"
        and "approve bounded live validation lv1" in normalized_decision
    )
    dev_owner_live_validation_lv1_packet = _is_dev_owner_live_validation_lv1_packet(
        source_branch,
        normalized_decision,
    )
    hardening_h1_packet = (
        source_branch == "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
        and "approve bounded live validation lv1" in exact_user_decision.casefold()
    )
    lv1_green_packet = _is_fam007_breakpoint2_live_validation_lv1_packet(
        source_branch=source_branch,
        normalized_decision=normalized_decision,
    )
    pr_stage2_packet = _is_pr_readiness_stage2_packet(
        source_branch=source_branch,
        normalized_decision=normalized_decision,
        stage1_outcome=stage1_outcome,
    )
    pr_stage1_packet = _is_pr_readiness_stage1_packet(
        source_branch=source_branch,
        normalized_decision=normalized_decision,
        stage1_outcome=stage1_outcome,
    )
    bp3_packet = (
        source_branch
        in {
            "feature/fam-007-dev-owner-skeleton-readiness",
            "feature/fam-007-owner-ai-operational-foundation-gates",
            "feature/fam-006-dashboard-recording-start-stop-local-file",
        }
        and not workstream_package_approval_packet
        and not fam006_workstream_approval_review_packet
        and (
            "bp3" in exact_user_decision.casefold()
            or "workstream entry / orchestration" in exact_user_decision.casefold()
            or "orchestration validation" in exact_user_decision.casefold()
        )
    )
    bp1_packet = (
        "bp1 branch vision" in normalized_decision
        and any(
            marker in normalized_decision
            for marker in (
                "authorize bp2 user branch plan review only",
                "authorize bp2 user branch plan review preparation only",
                "authorize bp2 preparation only",
            )
        )
    )
    bp2_packet = (
        not bp1_packet
        and not bp3_packet
        and (
            "bp2 user branch plan review" in exact_user_decision.casefold()
            or "bp2 branch plan review" in exact_user_decision.casefold()
        )
    )
    machine_readable_packet_status = (
        "pr readiness stage1 approval review - Stage 1 Ready For Stage 2; "
        "PR Readiness Stage 2 remains pending separate USER approval."
        if pr_stage1_packet and stage1_outcome == PR_STAGE1_OUTCOME_READY
        else
        "pr readiness stage1 repair review - PR Readiness Stage 1 remains in "
        "repair-required posture; PR Readiness Stage 2 is not supported."
        if pr_stage1_packet
        else
        "bp1 branch vision review - BP1 Branch Vision Review remains pending "
        "USER acceptance, revision, waiver, rejection, or hold; BP2 remains pending."
        if bp1_packet
        else
        "bp2 branch plan review - accepted BP1 Branch Vision is the planning basis; "
        "BP2 USER Branch Plan Review packet is Reviewable; USER acceptance, revision, "
        "waiver, rejection, or hold remains pending; BP3 remains pending."
        if bp2_packet
        else
        "bp3 orchestration review - accepted BP1 Branch Vision and accepted BP2 "
        "Branch Plan are the traceability basis; BP3 Workstream Entry / "
        "Orchestration Validation packet is Reviewable; USER BP3 approval, "
        "revision, waiver, rejection, or hold remains pending; Workstream "
        "implementation remains pending separate USER approval."
        if bp3_packet
        else
        "workstream implementation approval review - BP1, BP2, and BP3 are "
        "accepted; bounded FAM-006 Workstream/runtime implementation approval "
        "packet is Reviewable; USER implementation approval remains pending; "
        "a green first seam is continuation proof, not package completion."
        if fam006_workstream_approval_review_packet
        else
        "workstream entry final decision review - Workstream Green review; admitted "
        "FAM-007 Dev/Owner proof seams are complete and Hardening H1 remains pending "
        "USER approval."
        if dev_owner_workstream_green_packet
        else
        "hardening final decision review - Hardening H1 is green; Live Validation LV1 "
        "remains pending USER approval."
        if dev_owner_hardening_h1_packet
        else
        "live validation final decision review - Live Validation LV1 is green; "
        "PR Readiness Stage 1 remains pending USER approval."
        if dev_owner_live_validation_lv1_packet
        else
        "implementation-ready - BP1, BP2, and BP3 are accepted; bounded Workstream "
        "package implementation is approved by this packet with Seam 1 as the entry "
        "checkpoint and continuation governed until Workstream Green, a real blocker, "
        "or explicit USER waiver."
        if workstream_package_approval_packet
        else
        "pr readiness stage1 approval review - PR Readiness Stage 1 analysis "
        "remains pending USER approval; PR creation remains pending USER approval."
        if pr_stage1_packet
        else
        "pr readiness stage2 review - PR Readiness Stage 1 Ready For Stage 2; "
        "PR creation remains pending USER approval."
        if pr_stage2_packet
        else
        "workstream implementation approval - Seam 1 public-safe action-gate registry "
        "and exact USER decision proof is approved by this packet decision path."
        if seam1_approval_packet
        else (
            "live validation final decision review - Live Validation LV1 is green; "
            "PR Readiness Stage 1 remains pending USER approval."
        )
        if lv1_green_packet
        else (
            "hardening final decision review - Hardening H1 is green; Live Validation LV1 "
            "remains pending USER approval."
        )
        if hardening_h1_packet
        else (
            "workstream entry final decision review - Workstream Green review; Seams 1 through 4 "
            "are complete and Hardening H1 remains pending USER approval."
        )
        if workstream_green_packet
        else (
            "workstream entry final decision review - seam 1 completion review; action-gate registry and exact USER decision "
            "proof are complete; Seam 2 remains pending USER approval."
        )
        if seam1_completion_packet
        else (
            "workstream entry final decision review - Workstream implementation "
            "remains pending USER approval."
        )
    )
    user_facing_decision = _user_facing_decision_text(exact_user_decision)
    primary_user_review_file_name = _primary_user_review_file(
        exact_user_decision,
        source_branch=source_branch,
        stage1_outcome=stage1_outcome,
    )
    user_vision_file: Path | None = None
    user_review_file: Path | None = None
    user_vision_file = _write_user_branch_vision_review(
        target=review_aids_dir,
        title=title,
        review_purpose=review_purpose,
        exact_user_decision=user_facing_decision,
        pending_user_decisions=pending_user_decisions,
        copied=copied,
    )
    user_review_file = _write_user_branch_plan_review(
        target=review_aids_dir,
        title=title,
        review_purpose=review_purpose,
        source_branch=source_branch,
        source_head=source_head,
        upstream=upstream,
        origin_main=origin_main,
        exact_user_decision=user_facing_decision,
        pending_user_decisions=pending_user_decisions,
        copied=copied,
        stage1_outcome=stage1_outcome,
    )
    pr_stage1_review_file = None
    if primary_user_review_file_name == PR_READINESS_STAGE1_REVIEW_FILE:
        pr_stage1_review_file = _write_pr_readiness_stage1_review(
            target=review_aids_dir,
            title=title,
            review_purpose=review_purpose,
            exact_user_decision=user_facing_decision,
            pending_user_decisions=pending_user_decisions,
            copied=copied,
            stage1_outcome=stage1_outcome,
        )
    if allow_custom_review_path:
        custom_review_path_waiver = "Granted"
        custom_review_path_reason_value = custom_review_path_reason or "Not recorded"
    else:
        custom_review_path_waiver = CUSTOM_REVIEW_PATH_NONE
        custom_review_path_reason_value = "Not applicable"
    start_here = (target / "START_HERE.md").resolve()
    digest_required_files = (
        PR_READINESS_STAGE1_PACKET_REQUIRED_FILES
        if pr_stage1_packet
        else WORKSTREAM_ENTRY_PACKET_REQUIRED_FILES
    )
    digest_paths = {
        (review_aids_dir / name).resolve()
        for name in digest_required_files
        if name != "START_HERE.md"
    }
    expected_generated_paths = {
        *digest_paths,
    }
    if user_vision_file is not None:
        expected_generated_paths.add(user_vision_file.resolve())
    if user_review_file is not None:
        expected_generated_paths.add(user_review_file.resolve())
    if pr_stage1_review_file is not None:
        expected_generated_paths.add(pr_stage1_review_file.resolve())
    primary_source_path = (review_aids_dir / primary_user_review_file_name).resolve()
    primary_destination_path = (user_review_dir / primary_user_review_file_name).resolve()
    if primary_source_path in expected_generated_paths:
        expected_generated_paths.remove(primary_source_path)
    expected_generated_paths.add(primary_destination_path)
    actual_bundle_files = copied_targets | expected_generated_paths | {start_here}
    extra_bundle_files = sorted(
        path.relative_to(target).as_posix()
        for path in actual_bundle_files
        if path not in copied_targets and path != start_here
    )
    bundle_file_count = len(actual_bundle_files)
    leak_prevention_failures = _public_review_bundle_file_list_failures(
        [
            *(source_rel for source_rel, _copied_rel in copied),
            *(copied_rel for _source_rel, copied_rel in copied),
            *extra_bundle_files,
        ]
    )
    if leak_prevention_failures:
        raise ValueError(
            "Public review bundle leak-prevention failed:\n"
            + "\n".join(f"- {failure}" for failure in leak_prevention_failures)
        )

    _write_workstream_entry_packet_digests(
        target=review_aids_dir,
        source_branch=source_branch,
        source_head=source_head,
        origin_main=origin_main,
        packet_folder=target,
        export_zip=export_zip,
        copied=copied,
        extra_bundle_files=extra_bundle_files,
        bundle_file_count=bundle_file_count,
        expected_count=expected_count,
        copied_count=copied_count,
        exact_user_decision=user_facing_decision,
        pending_user_decisions=pending_user_decisions,
        stage1_outcome=stage1_outcome,
    )
    primary_user_review_file = _move_primary_user_review_file(
        target=target,
        review_aids_dir=review_aids_dir,
        user_review_dir=user_review_dir,
        primary_file_name=primary_user_review_file_name,
    )

    effective_review_order = list(review_order)
    if primary_user_review_file_name == PR_READINESS_STAGE1_REVIEW_FILE:
        effective_review_order = [
            f"Open `{USER_REVIEW_DIR_NAME}/{PR_READINESS_STAGE1_REVIEW_FILE}` first; it is the current PR Readiness Stage 1 decision surface.",
            f"Then inspect `{REVIEW_AIDS_DIR_NAME}/PR_READINESS_STAGE1_COVERAGE_DIGEST.md` for the current-gate digest.",
            f"Then inspect `{REVIEW_AIDS_DIR_NAME}/PR_READINESS_STAGE1_SOURCE_COVERAGE.md` for the exact copied-source set.",
            f"Then inspect `{REVIEW_AIDS_DIR_NAME}/PR_READINESS_STAGE1_CONTRADICTION_CHECKLIST.md` for coherence proof.",
            "Use Source Truth Context files only as supporting evidence; BP1, BP2, BP3, and Workstream aids are not current-gate artifacts in this packet.",
        ]
    readme_lines: list[str] = [
        f"# {title}",
        "",
        "## Review Packet",
        "",
        f"Review Purpose: {review_purpose}",
        "Review Location: Open this folder in the local USER hub and upload the matching timestamped ZIP beside it.",
        f"Local USER Hub Folder: `{target}`",
        f"Custom Review Path Waiver: {custom_review_path_waiver}",
        f"Custom Review Path Reason: {custom_review_path_reason_value}",
        "Review Safety Note: Copied files are selected repo source-truth and "
        "review-context files for USER inspection; technical freshness proof "
        "stays in Codex chat digest, helper output, validator output, or external state.",
        f"Primary USER Review File: `{primary_user_review_file.relative_to(target).as_posix()}`",
        f"Source Truth Context Folder: `{SOURCE_TRUTH_CONTEXT_DIR_NAME}`",
        f"Review Aids Folder: `{REVIEW_AIDS_DIR_NAME}`",
        f"USER Decision This Packet Supports: {user_facing_decision}",
        "",
        "## Pending USER Decisions",
        "",
        *_markdown_lines(pending_user_decisions),
        "",
        "## Review Order",
        "",
        *_markdown_lines(effective_review_order),
        "",
        "## Extra Bundle Files",
        "",
        *_markdown_lines(extra_bundle_files),
        "",
        "## Files",
        "",
        "| Source path | Copied path |",
        "| --- | --- |",
    ]
    for source_rel, copied_rel in copied:
        readme_lines.append(f"| `{source_rel}` | `{copied_rel}` |")
    readme_lines.append("")
    readme_lines.extend(
        [
            "## Decision Path",
            "",
            f"Decision Path Summary: {machine_readable_packet_status}",
            f"USER Decision: {user_facing_decision}",
        "",
        ]
    )
    if bp3_packet:
        readme_lines.extend(
            [
                "BP3 Packet Reviewability State: Reviewable",
                "BP3 USER Gate State: Pending USER Review",
                "",
            ]
        )
    if fam006_workstream_approval_review_packet:
        readme_lines.extend(
            [
                "Workstream Approval Packet Reviewability State: Reviewable",
                "Workstream Approval USER Gate State: Pending USER Review",
                "Packet Reviewability State: Reviewable",
                "USER Gate State: Pending USER Review - Workstream/runtime implementation approval remains pending",
                "",
            ]
        )

    (target / "START_HERE.md").write_text("\n".join(readme_lines), encoding="utf-8")
    bundle_paths = _bundle_files(target)
    packet_files = {
        path.relative_to(target).as_posix(): path.read_text(encoding="utf-8")
        for path in bundle_paths
        if path.suffix.lower() in {".md", ".txt", ".json"}
    }
    generated_packet_files = {
        name: text
        for name, text in packet_files.items()
        if not name.startswith(f"{SOURCE_TRUTH_CONTEXT_DIR_NAME}/")
    }
    artifact_failures = [
        *_unresolved_template_placeholder_failures(generated_packet_files),
        *_packet_count_consistency_failures(
            packet_files,
            actual_file_count=len(bundle_paths),
        ),
        *_user_facing_technical_metadata_failures(generated_packet_files),
        *_user_branch_plan_stale_bp1_wording_failures(generated_packet_files),
        *_fam007_bp2_plan_substantive_failures(generated_packet_files),
        *_fam007_bp2_support_bp1_context_failures(generated_packet_files),
        *_bp1_packet_phase_language_failures(generated_packet_files),
        *_fam006_bp3_support_context_failures(generated_packet_files),
        *_user_branch_vision_substantive_failures(generated_packet_files),
        *_branch_planning_review_gate_state_failures(generated_packet_files),
        *_pr_stage1_review_failures(generated_packet_files),
    ]
    if artifact_failures:
        raise ValueError(
            "Review bundle artifact validation failed:\n"
            + "\n".join(f"- {failure}" for failure in artifact_failures)
        )
    expected_zip_entries = {path.relative_to(target).as_posix() for path in bundle_paths}
    _remove_stale_same_label_export_zips(review_root, label, export_zip)
    _write_export_zip(target, export_zip)
    _validate_export_zip(
        export_zip,
        source_branch=source_branch,
        source_head=source_head,
        origin_main=origin_main,
        expected_label=label,
        expected_entries=expected_zip_entries,
    )
    return target, export_zip


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--review-root-name",
        default=DEFAULT_REVIEW_ROOT_NAME,
        help="Optional subfolder under C:\\Nexus USER. Custom values require --allow-custom-review-path.",
    )
    parser.add_argument(
        "--worktree-label",
        help="Optional worktree child folder label. Defaults to the current worktree folder name.",
    )
    parser.add_argument(
        "--folder-name",
        help=(
            "Legacy alias for --worktree-label. New governance expects a stable "
            "local USER hub with an auto-derived worktree label. Requires "
            "--allow-custom-review-path."
        ),
    )
    parser.add_argument(
        "--allow-custom-review-path",
        action="store_true",
        help="USER-approved waiver allowing a custom review root or worktree label.",
    )
    parser.add_argument(
        "--custom-review-path-reason",
        help="Required reason when --allow-custom-review-path is used.",
    )
    parser.add_argument("--title", default="Nexus Review Bundle", help="Title for START_HERE.md.")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Legacy compatibility flag; the helper always clears the local USER hub packet folder before copying.",
    )
    parser.add_argument("--review-purpose", help="Why USER is reviewing this bundle.")
    parser.add_argument("--validation-summary", help="Validation proof or status supporting the review bundle.")
    parser.add_argument(
        "--review-order",
        action="append",
        default=[],
        help="Repeatable suggested review step for START_HERE.md.",
    )
    parser.add_argument("--exact-user-decision", help="Exact USER decision this bundle is meant to support.")
    parser.add_argument(
        "--pending-user-decision",
        action="append",
        default=[],
        help="Repeatable pending USER decision that remains outside this bundle.",
    )
    parser.add_argument(
        "--expected-file-count",
        type=int,
        help="Expected count of repo files copied into the review bundle.",
    )
    parser.add_argument(
        "--validate-workstream-entry-packet",
        type=Path,
        help="Validate an existing Branch Planning / Workstream Entry packet decision path.",
    )
    parser.add_argument(
        "--validate-local-user-packet",
        type=Path,
        help="Validate an existing local USER hub packet folder against deterministic folder/ZIP rules.",
    )
    parser.add_argument(
        "--review-export-zip",
        type=Path,
        help=(
            "Timestamped upload ZIP to validate with --validate-local-user-packet, or "
            "the exact timestamped ZIP path to generate when building a review bundle."
        ),
    )
    parser.add_argument(
        "--packet-validation-mode",
        choices=PACKET_VALIDATION_MODES,
        default=PACKET_VALIDATION_MODE_ACTIVE_REVIEW,
        help=(
            "Currentness mode for --validate-local-user-packet: active-review and next-gate "
            "must match live external state; accepted-historical validates the immutable "
            "accepted packet snapshot against its copied context and live acceptance receipt."
        ),
    )
    parser.add_argument(
        "--expected-branch",
        help=(
            "Expected source branch for active-review packet identity validation. "
            "Required with active-review local packet validation."
        ),
    )
    parser.add_argument(
        "--expected-head",
        help=(
            "Expected source HEAD for active-review packet identity validation. "
            "Required with active-review local packet validation."
        ),
    )
    parser.add_argument(
        "--expected-origin-main",
        help=(
            "Expected origin/main for active-review packet identity validation. "
            "Required with active-review local packet validation."
        ),
    )
    parser.add_argument(
        "--require-implementation-ready",
        action="store_true",
        help="Fail if the packet is branch-correct but still blocks Workstream implementation approval.",
    )
    parser.add_argument(
        "--stage1-outcome",
        choices=(PR_STAGE1_OUTCOME_REPAIR, PR_STAGE1_OUTCOME_READY),
        default=PR_STAGE1_OUTCOME_REPAIR,
        help="Current PR Readiness Stage 1 outcome for the dedicated primary artifact.",
    )
    parser.add_argument("files", nargs="*", help="Repo-relative files to copy into the local USER hub packet.")
    args = parser.parse_args()

    if args.validate_local_user_packet:
        if args.review_export_zip is None:
            parser.error("--review-export-zip is required with --validate-local-user-packet")
        result = validate_local_user_packet(
            args.validate_local_user_packet,
            export_zip=args.review_export_zip,
            worktree_label=args.worktree_label or args.folder_name,
            validation_mode=args.packet_validation_mode,
            expected_branch=args.expected_branch,
            expected_head=args.expected_head,
            expected_origin_main=args.expected_origin_main,
        )
        print(_format_local_user_packet_validation_result(result))
        return 1 if result.failures else 0

    if args.validate_workstream_entry_packet:
        for field_name in ("expected_branch", "expected_head", "expected_origin_main"):
            if getattr(args, field_name) is None:
                parser.error(f"--{field_name.replace('_', '-')} is required with --validate-workstream-entry-packet")
        result = validate_workstream_entry_packet_folder(
            args.validate_workstream_entry_packet,
            expected_branch=args.expected_branch,
            expected_head=args.expected_head,
            expected_origin_main=args.expected_origin_main,
            require_implementation_ready=args.require_implementation_ready,
        )
        if result.failures:
            print("FAIL: Workstream Entry packet decision-path validation failed.")
            print(f"Packet status: {result.status}")
            for failure in result.failures:
                print(f"- {failure}")
            return 1
        if result.blocks_implementation:
            print("PASS: Workstream Entry packet is self-consistent and blocks implementation approval.")
            print(f"Packet status: {result.status}")
        else:
            print("PASS: Workstream Entry packet is self-consistent and implementation-ready.")
            print(f"Packet status: {result.status}")
        return 0

    for required_arg in ("review_purpose", "validation_summary", "exact_user_decision"):
        if getattr(args, required_arg) is None:
            parser.error(f"--{required_arg.replace('_', '-')} is required when building a review bundle")
    if not args.files:
        parser.error("at least one repo-relative file is required when building a review bundle")

    target, export_zip = build_bundle(
        review_root_name=args.review_root_name,
        worktree_label=args.worktree_label or args.folder_name,
        allow_custom_review_path=args.allow_custom_review_path,
        custom_review_path_reason=args.custom_review_path_reason,
        files=args.files,
        title=args.title,
        clear=args.clear,
        review_purpose=args.review_purpose,
        validation_summary=args.validation_summary,
        review_order=args.review_order,
        exact_user_decision=args.exact_user_decision,
        pending_user_decisions=args.pending_user_decision,
        expected_file_count=args.expected_file_count,
        review_export_zip=args.review_export_zip,
        stage1_outcome=args.stage1_outcome,
    )
    print(f"Review bundle: {target}")
    print(f"Review export zip: {export_zip}")
    primary_file = _primary_user_review_file(
        args.exact_user_decision,
        source_branch=_git_output("branch", "--show-current"),
        stage1_outcome=args.stage1_outcome,
    )
    if primary_file == PR_READINESS_STAGE1_REVIEW_FILE:
        print(
            "USER Review Packet Finding: PASS - START_HERE.md, "
            f"{PR_READINESS_STAGE1_REVIEW_FILE}, Stage 1-specific coverage/"
            "contradiction aids, and the timestamped export zip were generated "
            "and validated against the current source-truth snapshot."
        )
    else:
        print(
            "USER Review Packet Finding: PASS - START_HERE.md, "
            f"{USER_BRANCH_VISION_REVIEW_FILE}, {USER_BRANCH_PLAN_REVIEW_FILE}, and exported zip were generated and "
            "validated against current source-truth snapshot."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
