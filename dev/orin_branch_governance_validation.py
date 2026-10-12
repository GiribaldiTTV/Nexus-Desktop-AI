# NEXUS-SOURCE-OWNER: schema=source-owner-v1; owner=GOV-SOURCE-TRUTH; ledger=SRCOWN-FIRSTPASS-VALIDATOR-010; surface=branch-governance-validator; status=shared
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from nexus_paths import EXTERNAL_STATE_ROOT, NEUTRAL_MAIN_ROOT

ROOT_DIR = Path(__file__).resolve().parent.parent
NEUTRAL_MAIN_WORKSPACE = NEUTRAL_MAIN_ROOT
GITHUB_API_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "orin-branch-governance-validation",
}
GITHUB_API_TIMEOUT_SECONDS = 20
_GITHUB_API_TOKEN = ""
_GITHUB_API_TOKEN_LOADED = False

PHASES = (
    "Branch Readiness",
    "Branch Planning",
    "Workstream",
    "Hardening",
    "Live Validation",
    "PR Readiness",
    "Release Readiness",
)
HISTORICAL_TRACEABILITY_PHASE = "Historical Traceability"

BRANCH_CLASSES = (
    "implementation",
    "docs/governance",
    "emergency canon repair",
    "repair/dev-tooling-governance",
    "release packaging",
    "standing governance intake",
)

BLOCKED_FUTURE_ACTIVE_BRANCH_CLASSES = (
    "docs/governance",
    "emergency canon repair",
)

PROHIBITED_ACTIVE_BRANCH_PREFIXES = (
    "codex/",
)

PROMPT_CONTRACT_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/codex_user_guide.md'), Path('Docs/orin_task_template.md'),)

CURRENT_STATE_OWNER_DOCS = (Path('Docs/feature_backlog.md'), Path('Docs/prebeta_roadmap.md'), Path('Docs/workstreams/index.md'), Path('Docs/closeout_index.md'),)

PUBLISHED_RELEASE_CLOSURE_SCAN_PATHS = (
    Path("Docs/feature_backlog.md"),
    Path("Docs/prebeta_roadmap.md"),
    Path("Docs/worktree_slots.md"),
    Path("Docs/workstreams/index.md"),
)

PUBLISHED_RELEASE_CLOSURE_SCAN_DIRS = (
    Path("Docs/branch_records"),
    Path("Docs/branch_plans"),
    Path("Docs/family_visions"),
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
    "## Backlog Completion Strategy",
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

REQUIRED_BRANCH_READINESS_COMPLETION_MARKERS = (
    "Branch Completion Goal:",
    "Known Future-Dependent Blockers:",
    "Branch Closure Rule:",
)

PRODUCT_DEFINITION_PLAN_HEADING = "Product Definition Plan"
RUNTIME_ENGINEERING_CONTRACT_HEADING = "Runtime Branch Engineering Contract"
USER_VISION_QUESTION_PACKET_HEADING = "USER Vision Question Packet"
USER_VISION_INPUT_HANDOFF_HEADING = "USER Vision Input Handoff"
USER_VISION_INPUT_ARTIFACT_PATH = Path(r"C:\Users\anden\OneDrive\Desktop\User Vision Input.txt")
PRODUCT_PLANNING_ENFORCED_PHASES = {
    "Branch Readiness",
    "Branch Planning",
    "Workstream",
    "Hardening",
    "Live Validation",
    "PR Readiness",
}
RUNTIME_ENGINEERING_CONTRACT_ENFORCED_PHASES = PRODUCT_PLANNING_ENFORCED_PHASES | {
    "Release Readiness",
}
PRODUCT_PLANNING_EXECUTION_PHASES = PRODUCT_PLANNING_ENFORCED_PHASES - {
    "Branch Readiness",
}
REQUIRED_PRODUCT_SYSTEM_PLANNING_MARKERS = (
    "Project-Wide Vision Alignment:",
    "Branch-Specific Vision Alignment:",
    "System Concept Model:",
    "Entity / Profile Model:",
    "User Workflow Model:",
    "Scale / Data Volume Model:",
    "Configuration And State Model:",
    "Expected User-Facing Outcomes:",
    "Codex Additional Recommendations:",
    "USER Critique Loop:",
    "USER Decision Ledger:",
    "Deferred Ideas / Future Package Ledger:",
    "Planning Adequacy Review:",
    "Rejected Shallow Plan:",
    "Alternatives And Tradeoffs Reviewed:",
    "Whole-System Interaction Map:",
    "Minimum Viable vs Full System Boundary:",
    "Open Questions / USER Decision Points:",
)
PRODUCT_SYSTEM_PLANNING_MIN_WORDS = 8
RUNTIME_ENGINEERING_CONTRACT_MIN_WORDS = 8
PRODUCT_SYSTEM_PLANNING_HANDWAVE_VALUES = {
    "tbd",
    "todo",
    "pending",
    "none",
    "n/a",
    "na",
    "not applicable",
    "same as above",
    "see above",
    "simple",
    "basic",
    "minimal",
    "placeholder",
}
RUNTIME_ENGINEERING_NEGATIVE_APPROVAL_TERMS = (
    "not approved",
    "not accepted",
    "not granted",
    "not waived",
    "not yet approved",
    "approval missing",
    "user approval missing",
    "missing approval",
    "approval pending",
    "pending approval",
    "unapproved",
    "denied",
    "rejected",
)
REQUIRED_RUNTIME_ENGINEERING_CONTRACT_MARKERS = (
    "Engineering Contract Status:",
    "USER Engineering Planning Review:",
    "Runtime Implementation Approval:",
    "Branch Purpose:",
    "Current Runtime Baseline:",
    "Planned Runtime Delta:",
    "User-Facing Runtime Delta:",
    "State / Config / Schema Delta:",
    "Validator / Helper Delta:",
    "Expected Changed Files / Surfaces:",
    "Approval-Boundary Audit:",
    "Future-Gated Items:",
    "Workstream Seam Map:",
    "Proof Expectations:",
    "Risk Forecast:",
    "Recommendations And Alternatives:",
    "Plan Version / Revision Status:",
    "Plan-To-Implementation Traceability:",
)
RUNTIME_ENGINEERING_CONTRACT_DETAIL_MARKERS = (
    "Branch Purpose:",
    "Current Runtime Baseline:",
    "Planned Runtime Delta:",
    "User-Facing Runtime Delta:",
    "State / Config / Schema Delta:",
    "Validator / Helper Delta:",
    "Expected Changed Files / Surfaces:",
    "Approval-Boundary Audit:",
    "Future-Gated Items:",
    "Workstream Seam Map:",
    "Proof Expectations:",
    "Risk Forecast:",
    "Recommendations And Alternatives:",
    "Plan-To-Implementation Traceability:",
)
BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING = "Branch Runtime Engineering Plan"
BRANCH_RUNTIME_ENGINEERING_PLAN_POINTER_LABEL = "Branch Runtime Engineering Plan:"
BRANCH_RUNTIME_ENGINEERING_PLAN_PATH_LABEL = "Branch Runtime Engineering Plan Path:"
BRANCH_RUNTIME_ENGINEERING_PLAN_DIRECTORY = "Docs/branch_plans/"
EXTERNAL_BRANCH_RUNTIME_ENGINEERING_PLAN_DIRECTORY = f"{EXTERNAL_STATE_ROOT.as_posix()}/branches/"
EXTERNAL_BRANCH_RUNTIME_ENGINEERING_PLAN_FILE = "branch_plan.md"
EXTERNAL_BRANCH_OPERATIONAL_STATE_FILE = "branch_state.md"
BRANCH_RUNTIME_ENGINEERING_PLAN_MIN_WORDS = 8
BRANCH_RUNTIME_ENGINEERING_PLAN_STATUS_TERMS = (
    "required",
    "proposed",
    "present",
    "accepted",
    "revised",
    "folded",
    "historical",
)
REQUIRED_BRANCH_RUNTIME_ENGINEERING_PLAN_MARKERS = (
    "Plan Identity:",
    "Owning Branch:",
    "Worktree Path:",
    "Branch Authority Record Pointer:",
    "Current Phase:",
    BRANCH_RUNTIME_ENGINEERING_PLAN_POINTER_LABEL,
    "Engineering Plan Status:",
    "Current Runtime Baseline:",
    "Branch Purpose:",
    "Planned Runtime Delta:",
    "User-Facing Delta:",
    "Source-Truth Delta:",
    "State / Config / Schema Delta:",
    "Validator / Helper Delta:",
    "Expected Changed Files / Surfaces:",
    "Workstream / Seam Map:",
    "Per-Seam Implementation Checklist:",
    "Per-Seam Validation Checklist:",
    "Per-Seam User-Facing Proof Checklist:",
    "Future-Gated Items:",
    "Approval-Boundary Audit:",
    "FAM / Shared-Surface Overlap Forecast:",
    "Open Questions:",
    "Feature Vision Context:",
    "Deferred Feature Carryforward Review:",
    "USER Planning Decisions:",
    "Plan Revision History:",
    "Plan-To-Implementation Traceability Table:",
    "Hardening Comparison Checklist:",
    "Live Validation Proof Or Waiver Checklist:",
    "Runtime Observability Decision Matrix:",
    "Exact USER Desktop Launcher Path:",
    "Launcher Parity Proof Plan:",
    "Photo / Video Proof Plan:",
    "Manual USER Validation Plan:",
    "Troubleshooting Mode Decision:",
    "USER Packet Evidence Plan:",
    "PR Readiness Fold-Down / Retention Checklist:",
    "Release Readiness Public-Scope Translation Checklist:",
    "USER Planning Review:",
    "PR Fold-Down Packet:",
    "Runtime Implementation Approval:",
)
BRANCH_RUNTIME_ENGINEERING_PLAN_DETAIL_MARKERS = (
    "Current Runtime Baseline:",
    "Branch Purpose:",
    "Planned Runtime Delta:",
    "User-Facing Delta:",
    "Source-Truth Delta:",
    "State / Config / Schema Delta:",
    "Validator / Helper Delta:",
    "Expected Changed Files / Surfaces:",
    "Workstream / Seam Map:",
    "Per-Seam Implementation Checklist:",
    "Per-Seam Validation Checklist:",
    "Per-Seam User-Facing Proof Checklist:",
    "Future-Gated Items:",
    "Approval-Boundary Audit:",
    "FAM / Shared-Surface Overlap Forecast:",
    "Feature Vision Context:",
    "Deferred Feature Carryforward Review:",
    "Plan-To-Implementation Traceability Table:",
    "Hardening Comparison Checklist:",
    "Live Validation Proof Or Waiver Checklist:",
    "Runtime Observability Decision Matrix:",
    "Exact USER Desktop Launcher Path:",
    "Launcher Parity Proof Plan:",
    "Photo / Video Proof Plan:",
    "Manual USER Validation Plan:",
    "Troubleshooting Mode Decision:",
    "USER Packet Evidence Plan:",
    "PR Readiness Fold-Down / Retention Checklist:",
    "Release Readiness Public-Scope Translation Checklist:",
)
BRANCH_RUNTIME_ENGINEERING_PLAN_DETAIL_TERMS = {
    "Current Runtime Baseline:": (
        "state",
        "config",
        "schema",
        "ui",
        "desktop",
        "provider",
        "validator",
        "helper",
        "file",
        "surface",
        "runtime",
    ),
    "Planned Runtime Delta:": (
        "state",
        "config",
        "schema",
        "ui",
        "copy",
        "validator",
        "helper",
        "fixture",
        "file",
        "surface",
        "runtime",
        "delta",
    ),
    "User-Facing Delta:": (
        "user",
        "visible",
        "ui",
        "copy",
        "status",
        "label",
        "interaction",
        "workflow",
        "disabled",
        "future-gated",
    ),
    "State / Config / Schema Delta:": (
        "state",
        "config",
        "schema",
        "field",
        "metadata",
        "settings",
        "persistence",
        "manifest",
        "provenance",
    ),
    "Validator / Helper Delta:": (
        "validator",
        "helper",
        "fixture",
        "proof",
        "test",
        "gate",
        "audit",
        "validation",
    ),
    "Expected Changed Files / Surfaces:": (
        "file",
        "surface",
        "desktop",
        "docs",
        "dev",
        "ui",
        "runtime",
        "validator",
    ),
    "Workstream / Seam Map:": (
        "seam",
        "ws",
        "slice",
        "implementation",
        "validation",
        "hardening",
        "live validation",
    ),
    "Per-Seam Implementation Checklist:": (
        "seam",
        "implementation",
        "checklist",
        "runtime",
        "file",
        "state",
        "ui",
    ),
    "Per-Seam Validation Checklist:": (
        "seam",
        "validation",
        "validator",
        "fixture",
        "proof",
        "check",
    ),
    "Per-Seam User-Facing Proof Checklist:": (
        "seam",
        "user",
        "visible",
        "proof",
        "screenshot",
        "uts",
        "waiver",
    ),
    "Future-Gated Items:": (
        "future",
        "gated",
        "approval",
        "blocked",
        "pending",
        "defer",
    ),
    "Approval-Boundary Audit:": (
        "approval",
        "boundary",
        "pending",
        "blocked",
        "user",
        "separate",
    ),
    "Feature Vision Context:": (
        "project vision",
        "family vision",
        "family feature vision",
        "branch vision",
        "feature vision",
        "deferred",
        "proof",
    ),
    "Deferred Feature Carryforward Review:": (
        "deferred",
        "carryforward",
        "dependency",
        "trigger",
        "grouping",
        "future-gated",
        "proof",
    ),
    "Plan-To-Implementation Traceability Table:": (
        "planned",
        "actual",
        "implementation",
        "trace",
        "file",
        "proof",
    ),
    "Hardening Comparison Checklist:": (
        "hardening",
        "plan",
        "implementation",
        "copy",
        "validator",
        "future-gated",
    ),
    "Live Validation Proof Or Waiver Checklist:": (
        "live validation",
        "proof",
        "waiver",
        "user",
        "static",
        "runtime",
    ),
    "Runtime Observability Decision Matrix:": (
        "launcher",
        "troubleshooting",
        "parity",
        "photo",
        "video",
        "manual",
        "packet",
    ),
    "Exact USER Desktop Launcher Path:": (
        "nexus desktop launcher.lnk",
        "exact",
        "desktop",
        "launcher",
        "user",
        "waiver",
    ),
    "Launcher Parity Proof Plan:": (
        "parity",
        "troubleshooting",
        "same product runtime",
        "same build",
        "same data roots",
        "user consent",
    ),
    "Photo / Video Proof Plan:": (
        "photo",
        "video",
        "frame",
        "screenshot",
        "visible",
        "user-facing",
    ),
    "Manual USER Validation Plan:": (
        "manual",
        "user validation",
        "waiver",
        "blocker",
        "unphotographable",
        "cannot be proven",
    ),
    "Troubleshooting Mode Decision:": (
        "troubleshooting",
        "diagnostic",
        "user consent",
        "supporting evidence",
        "parity",
        "normal launcher",
    ),
    "USER Packet Evidence Plan:": (
        "user packet",
        "review hub",
        "evidence",
        "pass",
        "fail",
        "blocked",
        "unproven",
    ),
    "PR Readiness Fold-Down / Retention Checklist:": (
        "pr readiness",
        "fold",
        "retention",
        "historical",
        "promote",
        "receipt",
    ),
    "Release Readiness Public-Scope Translation Checklist:": (
        "release readiness",
        "public",
        "scope",
        "excluded",
        "future-gated",
        "release",
    ),
}
BRANCH_RUNTIME_ENGINEERING_PLAN_COMPACTNESS_FORBIDDEN_MARKERS = (
    "Per-Seam Implementation Checklist:",
    "Per-Seam Validation Checklist:",
    "Per-Seam User-Facing Proof Checklist:",
    "Plan-To-Implementation Traceability Table:",
    "Hardening Comparison Checklist:",
    "Live Validation Proof Or Waiver Checklist:",
    "PR Readiness Fold-Down / Retention Checklist:",
    "Release Readiness Public-Scope Translation Checklist:",
)
ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING = "Element-to-Phase Proof Matrix"
ELEMENT_TO_PHASE_MATRIX_REQUIRED_MARKERS = (
    "Matrix Status:",
    "USER Review Status:",
    "Open Element Questions:",
    "Element Coverage Owner:",
    "Element Validation Ledger Owner:",
)
ELEMENT_TO_PHASE_MATRIX_MARKER_ALLOWED_PREFIXES = {
    "Matrix Status:": (
        "required",
        "present",
        "accepted",
        "blocked",
        "folded",
        "historical",
        "not required with reason",
    ),
    "USER Review Status:": (
        "pending",
        "accepted",
        "revised",
        "waived",
        "needs user decision",
    ),
    "Open Element Questions:": (
        "none",
        "queued",
        "blocking",
        "deferred with waiver",
    ),
}
ELEMENT_TO_PHASE_MATRIX_OWNER_MARKERS = (
    "Element Coverage Owner:",
    "Element Validation Ledger Owner:",
)
ELEMENT_TO_PHASE_MATRIX_COLUMNS = (
    "Element ID",
    "Element / Surface",
    "Element Classification",
    "Workstream Implementation Plan",
    "Workstream Proof Plan",
    "Hardening Proof Plan",
    "Live Validation Proof / Waiver Plan",
    "UTS / USER Acceptance Path",
    "Future / Deferred Boundary",
    "USER Decision State",
    "Source Owner / Ledger Owner",
)
ELEMENT_TO_PHASE_CURRENT_CLASS_TERMS = (
    "planned",
    "created",
    "touched",
    "affected",
)
ELEMENT_TO_PHASE_BOUNDARY_CLASS_TERMS = (
    "deferred",
    "future",
    "dependency-only",
    "dependency only",
    "non-gating",
    "non gating",
)
ELEMENT_TO_PHASE_DECISION_TERMS = (
    "accepted",
    "revised",
    "deferred",
    "waiver",
    "waived",
    "proposed",
    "needs user",
    "pending user",
    "rejected",
    "superseded",
)
USER_BRANCH_PLAN_REVIEW_HEADING = "USER Branch Plan Review Gate"
USER_BRANCH_PLAN_REVIEW_REQUIRED_MARKERS = (
    "USER Branch Plan Review:",
    "Review Status:",
    "Contract Status:",
    "Packet Reviewability State:",
    "USER Gate State:",
    "USER Response Proof:",
    "USER Response Digested:",
    "Acceptance / Waiver / Revision / Rejection Receipt:",
    "Contract Version / Revision:",
    "USER Review Hub Packet:",
    "USER Review Packet Finding:",
    "Plain-Language Branch Goal:",
    "What Will I Actually See, And Where Will I See It?:",
    "Planned User-Facing Outcome:",
    "End-State Vision:",
    "Visual / Behavioral Description:",
    "Visual / Functional Walkthrough:",
    "Surface Map:",
    "Implementation Breakdown:",
    "Element-to-Phase Proof Matrix:",
    "Hardening Plan:",
    "Live Validation / UTS Plan:",
    "Open USER Questions:",
    "USER Plan Review Questions:",
    "Codex Recommendations:",
    "Implementation Options:",
    "Recommended Direction:",
    "Why This Fits The Nexus Vision:",
    "USER Plan Review Decision:",
    "Current Branch Scope:",
    "Future-Gated Scope:",
    "Implementation Staging Notes:",
    "USER Decisions Needed:",
    "Alternatives / Tradeoffs:",
    "USER Review Response:",
    "Codex Response Digest:",
    "Implementation Constraints Created By USER Response:",
    "USER Rejected / Deferred Ideas:",
    "Vision Delta / Source-Truth Impact:",
    "Contract Change Log:",
    "Workstream Entry Result:",
    "Contract Completion Checklist:",
    "Accepted Scope:",
    "Deferred Scope:",
    "Rejected Scope:",
    "Exact USER Decision Needed:",
    "Implementation Approval:",
)
USER_BRANCH_PLAN_REVIEW_MARKER_ALIASES = {
    "USER Plan Review Questions:": ("USER Design Review Questions:",),
    "USER Plan Review Decision:": ("USER Design Direction Decision:",),
}
USER_BRANCH_PLAN_REVIEW_STATUS_PREFIXES = (
    "accepted by user",
    "revised by user",
    "deferred with waiver",
    "rejected by user",
    "needs user decision",
)
USER_BRANCH_PLAN_CONTRACT_STATUS_PREFIXES = (
    "draft",
    "pending user response",
    "pending codex digest",
    "pending user confirmation",
    "complete",
    "waived by user",
)
USER_BRANCH_PLAN_CONTRACT_BLOCKING_PREFIXES = (
    "draft",
    "pending user response",
    "pending codex digest",
    "pending user confirmation",
)
USER_BRANCH_PLAN_PACKET_REVIEWABILITY_PREFIXES = (
    "missing",
    "generated",
    "validation failed",
    "reviewable",
    "stale",
    "superseded",
)
USER_BRANCH_PLAN_USER_GATE_STATE_PREFIXES = (
    "pending user review",
    "user revision requested",
    "user accepted",
    "user approved",
    "user waived",
    "user rejected",
    "user blocked",
    "superseded",
)
USER_BRANCH_PLAN_USER_GATE_BLOCKING_PREFIXES = (
    "pending user review",
    "user revision requested",
    "user rejected",
    "user blocked",
)
USER_BRANCH_PLAN_REVIEW_SCOPE_MARKERS = (
    "Accepted Scope:",
    "Deferred Scope:",
    "Rejected Scope:",
)
USER_BRANCH_PLAN_REVIEW_RESPONSE_TERMS = (
    "accepted by user",
    "revised by user",
    "deferred with waiver",
    "waived",
    "rejected by user",
    "attached",
    "inserted",
    "digested",
    "needs user response",
    "pending user response",
)
USER_REVIEW_PACKET_FINDING_REQUIRED_TERMS = (
    ("START_HERE.md",),
    ("USER_BRANCH_PLAN_REVIEW.md",),
    ("zip", ".zip"),
    ("Source HEAD", "packet source HEAD", "review zip source HEAD"),
    ("current branch HEAD", "current HEAD"),
    ("loaded", "waived"),
    ("digested", "waived"),
    ("fresh", "match", "stale", "missing", "blocking", "waived"),
)
BRANCH_VISION_CONTRACT_HEADING = "Branch Vision Contract Snapshot"
BRANCH_VISION_CONTRACT_REQUIRED_MARKERS = (
    "Vision Contract Required:",
    "Vision Contract Requirement Reason:",
    "Branch Vision Snapshot Status:",
    "Open Vision Questions:",
    "USER Vision Green:",
    "Implementation Scope:",
    "Seam Map:",
    "Stop Conditions:",
    "Design Assumption Ledger:",
    "Vision Question Queue:",
    "Question Severity Policy:",
    "Vision-to-Implementation Traceability:",
    "Branch Plan Revision Packet:",
)
BRANCH_VISION_SAFE_STATE_TERMS = (
    "accepted by user",
    "accepted",
    "revised by user",
    "revised",
    "deferred with waiver",
    "waived",
    "not required",
)
BRANCH_VISION_UNSAFE_STATE_TERMS = (
    "proposed by codex",
    "recommended by chatgpt",
    "needs user decision",
    "pending user",
    "unanswered",
    "blocking",
)
BRANCH_VISION_TRACEABILITY_TERMS = (
    "vision",
    "branch",
    "seam",
    "file",
    "validator",
    "proof",
)
USER_FEEDBACK_DISPOSITION_HEADING = "USER Feedback Disposition"
USER_FEEDBACK_DISPOSITION_LEDGER_MARKERS = (
    "USER Feedback Disposition Required:",
    "UFD Ledger Status:",
    "UFD Ledger Owner:",
    "Open UFD Count:",
    "Blocking UFD Count:",
    "Fold-Down Status:",
)
USER_FEEDBACK_DISPOSITION_ITEM_MARKERS = (
    "Feedback ID:",
    "Feedback Summary:",
    "Feedback Source:",
    "Feedback Phase:",
    "Disposition Type:",
    "USER Decision State:",
    "Owner Class:",
    "Canonical Owner File:",
    "Workstream Severity:",
    "Status:",
    "Fold-Down Target:",
    "Pointer Locations:",
)
USER_FEEDBACK_DISPOSITION_ALLOWED_STATES = (
    "proposed by codex",
    "recommended by chatgpt",
    "accepted by user",
    "revised by user",
    "rejected by user",
    "deferred by user",
    "deferred with waiver",
    "superseded",
    "needs user decision",
)
USER_FEEDBACK_DISPOSITION_ALLOWED_STATUSES = (
    "open",
    "queued",
    "blocking",
    "closed",
    "folded down",
    "deferred",
    "superseded",
)
USER_FEEDBACK_DISPOSITION_LEDGER_STATUSES = (
    *USER_FEEDBACK_DISPOSITION_ALLOWED_STATUSES,
    "pending",
    "complete",
    "not required",
    "not applicable",
)
USER_FEEDBACK_DISPOSITION_FOLD_DOWN_STATUSES = (
    "pending",
    "complete",
    "required",
    "folded",
    "folded down",
    "retired",
    "historical",
    "not required",
    "not applicable",
)
USER_FEEDBACK_DISPOSITION_OWNER_CLASSES = (
    "branch plan",
    "branch record",
    "backlog pointer",
    "roadmap pointer",
    "nexus vision",
    "family vision",
    "dossier",
    "workstream doc",
    "governance receipt",
    "no durable owner needed",
)
USER_FEEDBACK_DISPOSITION_TYPES = (
    "current branch requirement",
    "current seam blocker",
    "current seam non-blocking queue",
    "branch plan revision required",
    "future branch candidate",
    "family vision update candidate",
    "nexus vision update candidate",
    "backlog pointer candidate",
    "branch receipt item",
    "workstream / family dossier item",
    "workstream",
    "family dossier",
    "rejected / no action",
    "rejected",
    "no action",
)
USER_FEEDBACK_DISPOSITION_SEVERITY_TERMS = (
    "level 1",
    "level 2",
    "level 3",
    "non-blocking",
    "seam-blocking",
    "workstream-breaking",
)
BRANCH_CHANGE_INTENT_HEADING = "Branch Change Intent Ledger"
BRANCH_CHANGE_INTENT_ITEM_HEADING_RE = r"(?ms)^### Changed Surface:\s*([^\n]+)\n(.*?)(?=^### Changed Surface:|\Z)"
BRANCH_CHANGE_INTENT_MARKERS = (
    "Surface Class:",
    "Change Intent:",
    "Why This File Was Touched:",
    "Owned Behavior / Fact Class:",
    "Canonical Owner / Source Owner:",
    "Resolution Owner:",
    "Shared Surface:",
    "Overlap Risk:",
    "Expected Conflict Risk:",
    "Semantic Merge Risk:",
    "Regression / Gating Impact:",
    "Conflict Resolution Rule:",
    "Rebaseline Handling:",
    "Validation Proof:",
    "Fallback Evidence:",
    "USER Decision / Waiver:",
    "Fold-Down Target:",
)
BRANCH_CHANGE_INTENT_SURFACE_CLASSES = (
    "governance/source-truth",
    "runtime",
    "desktop/ui",
    "core visual",
    "validator/helper",
    "fixture/test",
    "configuration/state/schema",
    "release/public-output",
    "prompt/template",
    "automation/watcher",
    "build/packaging",
    "documentation/reference",
    "asset/media",
)
BRANCH_CHANGE_INTENT_HIGH_RISK_CLASSES = (
    "governance/source-truth",
    "runtime",
    "desktop/ui",
    "core visual",
    "validator/helper",
    "fixture/test",
    "configuration/state/schema",
    "release/public-output",
    "prompt/template",
    "automation/watcher",
    "build/packaging",
)
BRANCH_CHANGE_INTENT_SEMANTIC_RISK_VALUES = (
    "none",
    "low",
    "medium",
    "high",
    "unknown",
)
BRANCH_CHANGE_INTENT_REGRESSION_GATING_VALUES = (
    "none",
    "low",
    "medium",
    "high",
    "unknown",
)
BRANCH_CHANGE_INTENT_RESOLUTION_OWNERS = (
    "current branch",
    "incoming/folded owner",
    "originating lane",
    "standing governance",
    "user decision",
    "future branch",
)
RUNTIME_ENGINEERING_DETAIL_TERMS = {
    "Current Runtime Baseline:": (
        "state",
        "config",
        "schema",
        "ui",
        "desktop",
        "provider",
        "validator",
        "helper",
        "file",
        "surface",
        "runtime",
    ),
    "Planned Runtime Delta:": (
        "state",
        "config",
        "schema",
        "ui",
        "copy",
        "validator",
        "helper",
        "fixture",
        "file",
        "surface",
        "runtime",
        "delta",
    ),
    "User-Facing Runtime Delta:": (
        "user",
        "visible",
        "ui",
        "copy",
        "status",
        "label",
        "interaction",
        "workflow",
        "disabled",
        "future-gated",
    ),
    "State / Config / Schema Delta:": (
        "state",
        "config",
        "schema",
        "field",
        "metadata",
        "settings",
        "persistence",
        "manifest",
        "provenance",
    ),
    "Validator / Helper Delta:": (
        "validator",
        "helper",
        "fixture",
        "proof",
        "test",
        "gate",
        "audit",
        "validation",
    ),
    "Expected Changed Files / Surfaces:": (
        "file",
        "surface",
        "desktop",
        "docs",
        "dev",
        "ui",
        "runtime",
        "validator",
    ),
    "Workstream Seam Map:": (
        "seam",
        "ws",
        "slice",
        "implementation",
        "validation",
        "hardening",
        "live validation",
    ),
    "Proof Expectations:": (
        "proof",
        "validator",
        "fixture",
        "screenshot",
        "user test",
        "compile",
        "validation",
        "evidence",
    ),
    "Recommendations And Alternatives:": (
        "recommend",
        "alternative",
        "option",
        "safer",
        "larger",
        "risk",
        "tradeoff",
    ),
    "Plan-To-Implementation Traceability:": (
        "planned",
        "implementation",
        "trace",
        "actual",
        "seam",
        "proof",
        "validator",
    ),
}
PRODUCT_SYSTEM_SCALE_TERMS = (
    "scale",
    "multiple",
    "many",
    "several",
    "hundred",
    "thousand",
    "items",
    "records",
    "sources",
    "profiles",
    "states",
    "windows",
    "users",
    "files",
    "monitors",
)
PRODUCT_SYSTEM_RECOMMENDATION_TERMS = (
    "recommend",
    "consider",
    "option",
    "alternative",
    "additional",
    "also",
    "should",
)
PRODUCT_SYSTEM_USER_CRITIQUE_TERMS = (
    "approve",
    "change",
    "defer",
    "critique",
    "feedback",
    "review",
)
PRODUCT_SYSTEM_USER_DECISION_TERMS = (
    "approved",
    "pending",
    "deferred",
    "changed",
    "waived",
    "accepted",
    "rejected",
)
PRODUCT_SYSTEM_ADEQUACY_TERMS = (
    "not shallow",
    "whole system",
    "full system",
    "end-to-end",
    "because",
    "covers",
)
PRODUCT_SYSTEM_REJECTED_SHALLOW_TERMS = (
    "rejected",
    "not enough",
    "insufficient",
    "too shallow",
    "simple",
    "minimal",
)
PRODUCT_SYSTEM_TRADEOFF_TERMS = (
    "alternative",
    "tradeoff",
    "risk",
    "option",
    "instead",
)
PRODUCT_SYSTEM_BOUNDARY_TERMS = (
    "minimum",
    "viable",
    "full",
    "future",
    "boundary",
    "deferred",
)
REQUIRED_PRODUCT_DEFINITION_MARKERS = (
    "Product Vision:",
    "User-Facing Goal:",
    "USER Vision Questions:",
    "Codex Product Interpretation:",
    "Codex Implementation Recommendation:",
    "USER/ChatGPT Review Checkpoint:",
    "Full Feature Element Breakdown:",
    "Current Branch vs Future Package Boundaries:",
    "Affected Surfaces:",
    "Data/Control Model:",
    *REQUIRED_PRODUCT_SYSTEM_PLANNING_MARKERS,
    "Branch Reach / Package-Size Review:",
    "Why Branch Is Large Enough:",
    "Why Not Split Into Tiny Branches:",
    "Acceptance Criteria:",
    "Validation Proof Requirements:",
    "Screenshot / Live / User Test Summary Proof Requirements:",
    "Implementation Sequence Proposal:",
    "Planning Blockers:",
    "USER Decisions Needed:",
    "Planning Packet Status:",
    "Planning Revalidation Status:",
    "User Test Summary Strategy:",
)
REQUIRED_USER_VISION_QUESTION_PACKET_MARKERS = (
    "Question ID",
    "Category",
    "Decision needed",
    "Why this matters",
    "Feature area affected",
    "Codex recommendation",
    "Why Codex recommends it",
    "Alternatives/options",
    "Tradeoffs/risks",
    "Current-branch impact",
    "Future-package impact",
    "Safe default if USER is unsure",
    "Required before implementation",
    "May waive/defer",
    "Exact response format requested",
)
REQUIRED_USER_VISION_QUESTION_PACKET_CATEGORIES = (
    "Product goal / user outcome",
    "Visual identity / style",
    "Layout / placement",
    "Information hierarchy",
    "Data/source model",
    "Controls/settings model",
    "Fail-safe/no-data/degraded behavior",
    "Interaction model",
    "Accessibility/readability",
    "Privacy/security boundaries",
    "Performance constraints",
    "Validation proof standard",
    "User Test Summary acceptance criteria",
    "Current-branch vs future-package boundaries",
    "Release impact",
)
FAM_006_USER_VISION_PACKET_MARKERS = (
    "HUD form factor",
    "HUD placement",
    "always-visible vs reveal/toggle behavior",
    "visual style",
    "first useful status content",
    "telemetry depth",
    "controls/settings behavior",
    "fail-safe/no-data/degraded copy",
    "screenshot proof standard",
    "UTS acceptance standard",
    "current branch work vs future package work",
)
PRODUCT_PLANNING_INCOMPLETE_BLOCKER = "Branch Readiness Planning Incomplete"
PRODUCT_PLANNING_WAIVER_MARKER = "Planning Completion Waiver:"
PRODUCT_PLANNING_COMPLETE_VALUES = {"complete", "waived"}
PRODUCT_PLANNING_INCOMPLETE_VALUES = {"incomplete", "pending", "blocked"}
USER_VISION_INPUT_PENDING_BLOCKER = "USER Vision Input Pending"
USER_VISION_INPUT_FILE_MISSING_BLOCKER = "USER Vision Input File Missing"
USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER = "USER Vision Input Answers Pending"
USER_VISION_INPUT_DIGEST_PENDING_BLOCKER = "USER Vision Input Digest Pending"
LEGACY_PRODUCT_NAME_DRIFT_BLOCKER = "Legacy Product Name Drift"
LEGACY_RETIRED_PRODUCT_NAME = "".join(chr(code) for code in (74, 97, 114, 118, 105, 115))
LEGACY_PRODUCT_NAME_EXTRA_TOKENS = (
    "".join(chr(code) for code in (77, 97, 114, 118, 101, 108)),
    "".join(chr(code) for code in (83, 116, 97, 114, 107)),
)
HARDWARE_TELEMETRY_PROVIDER_PENDING_BLOCKER = "Hardware Telemetry Provider Selection Pending"
POLLING_FLOOR_UNDECIDED_BLOCKER = "Polling Floor Undecided"
WARNING_DELIVERY_MODALITY_PENDING_BLOCKER = "Warning Delivery Modality Pending"
EXTERNAL_TELEMETRY_PRIVACY_MODEL_MISSING_BLOCKER = "External Telemetry Privacy Model Missing"
AUDIO_WARNING_CROSS_FAMILY_APPROVAL_MISSING_BLOCKER = (
    "Audio Warning Cross-Family Approval Missing"
)
PERSONA_SWITCH_SCOPE_BOUNDARY_PENDING_BLOCKER = (
    "Persona Switch Scope Boundary Pending"
)
FAM006_BRANCH = "feature/fam-006-monitoring-hud-product-surface"
FAM006_BRANCH_RECORD = Path(
    "Docs/branch_records/feature_fam_006_monitoring_hud_product_surface.md"
)
FAM006_ELEMENT_LEDGER = Path(
    "Docs/branch_records/feature_fam_006_monitoring_hud_product_surface_element_ledger.md"
)
FAM006_STAGE2_R6_HEADING = "Stage 2-R6 Product Scope Boundary And Acceptance Criteria"
FAM006_STAGE2_R7_HEADING = "Stage 2-R7 Planning Revalidation Closeout And WS7 Handoff"
FAM006_STAGE2_R8_HEADING = "Stage 2-R8 Legacy Product Name Blocker And USER Vision Input Refresh"
FAM006_STAGE2_R9_HEADING = "Stage 2-R9 USER Vision Input Digest And FAM-006 Scope Rebaseline"
FAM006_STAGE2_R10_HEADING = "Stage 2-R10 Scope Rebaseline Closeout And WS7 Handoff"
FAM006_STAGE2_R11_HEADING = (
    "Branch Readiness Stage 2-R11 HUD Dashboard And Minimal HUD Source-Truth Repair"
)
FAM006_STAGE2_R12_HEADING = (
    "Branch Readiness Stage 2-R12 Interface Release Boundary Governance And Dashboard-First Source-Truth Repair"
)
FAM006_STAGE2_R13_HEADING = (
    "Branch Readiness Stage 2-R13 Dashboard-First Revalidation Closeout And Workstream Handoff"
)
FAM006_WS31_HEADING = (
    "Workstream WS31 Dashboard Control Panel Acceptance Baseline And Overlay Deferral Enforcement"
)
FAM006_WS31_NEXT_SEAM = (
    "Workstream WS32 - Dashboard Standalone Window Movement Clipping And Core Overlay Decoupling Proof"
)
FAM006_WS32_HEADING = (
    "Workstream WS32 Dashboard Standalone Window Movement Clipping And Core Overlay Decoupling Proof"
)
FAM006_WS32_NEXT_SEAM = (
    "Workstream WS33 - Dashboard Settings Control Content Polish And Monitor Management Clarity"
)
FAM006_WS33_HEADING = (
    "Workstream WS33 Dashboard Settings Control Content Polish And Monitor Management Clarity"
)
FAM006_WS33_NEXT_SEAM = (
    "Workstream WS34 - Dashboard Provider Setup No-Data Degraded Truth And Warning Posture Controls"
)
FAM006_WS34_HEADING = (
    "Workstream WS34 Dashboard Provider Setup No-Data Degraded Truth And Warning Posture Controls"
)
FAM006_WS34_NEXT_SEAM = (
    "Workstream WS35 - Dashboard Specific Static Live Proof Screenshots And Live Validation UTS Boundary"
)
FAM006_WS35_HEADING = (
    "Workstream WS35 Dashboard Specific Static Live Proof Screenshots And Live Validation UTS Boundary"
)
FAM006_WS35_NEXT_SEAM = (
    "Workstream WS36 - Workstream Completion Review And Hardening Handoff Reconciliation"
)
FAM006_WS36_HEADING = (
    "Workstream WS36 Workstream Completion Review And Hardening Handoff Reconciliation"
)
FAM006_WS36_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS37_HEADING = (
    "Workstream WS37 Dashboard Runtime Window Tray Safety And NCP Regression Isolation"
)
FAM006_WS37_NEXT_SEAM = (
    "Workstream WS38 - Dashboard Window Ownership Focus Movement Safety"
)
FAM006_WS38_HEADING = (
    "Workstream WS38 Dashboard Window Ownership Focus Movement Safety"
)
FAM006_WS38_NEXT_SEAM = (
    "Workstream WS39 - Dashboard Shell Layout Frame Resize And Readability Repair"
)
FAM006_WS39_HEADING = (
    "Workstream WS39 Dashboard Shell Layout Frame Resize And Readability Repair"
)
FAM006_WS39_NEXT_SEAM = (
    "Workstream WS40 - Dashboard IA Content Naming And Control Hub Repair"
)
FAM006_WS40_HEADING = (
    "Workstream WS40 Dashboard IA Content Naming And Control Hub Repair"
)
FAM006_WS40_NEXT_SEAM = (
    "Workstream WS41 - Dashboard Child-Window Scope Implementation If Admitted"
)
FAM006_WS41_HEADING = (
    "Workstream WS41 Dashboard Child-Window Scope Deferred To Future Branch"
)
FAM006_WS41_NEXT_SEAM = (
    "Workstream WS42 - Dashboard Specific Static Live Proof And LV1 Handoff Readiness"
)
FAM006_WS42_HEADING = (
    "Workstream WS42 Dashboard Specific Static Live Proof And LV1 Handoff Readiness"
)
FAM006_WS42_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS43_HEADING = (
    "Workstream WS43 Dashboard Runtime Tray Shutdown Safety Repair"
)
FAM006_WS43_NEXT_SEAM = (
    "Workstream WS44 - Dashboard Frame Scroll Resize Visual Shell Repair"
)
FAM006_WS44_HEADING = (
    "Workstream WS44 Dashboard Frame Scroll Resize Visual Shell Repair"
)
FAM006_WS44_NEXT_SEAM = (
    "Workstream WS45 - Dashboard IA Naming Action Cleanup"
)
FAM006_WS45_HEADING = (
    "Workstream WS45 Dashboard IA Naming Action Cleanup"
)
FAM006_WS45_NEXT_SEAM = (
    "Workstream WS46 - Dashboard Returned-Feedback Static Live Proof Readiness"
)
FAM006_WS46_HEADING = (
    "Workstream WS46 Dashboard Returned-Feedback Static Live Proof Readiness"
)
FAM006_WS46_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_STAGE2_REAL_CLIENT_HEADING = (
    "Branch Readiness Stage 2 FAM-006 Returned LV1 Real-Client Failure Source-Truth "
    "Issue Register And Ledger Disposition Repair"
)
FAM006_STAGE2_REAL_CLIENT_NEXT_SEAM = (
    "Workstream WS47 - Dashboard Real-Client Tray Shortcut And Proof-Governance Repair"
)
FAM006_WS47_HEADING = (
    "Workstream WS47 Dashboard Real-Client Tray Shortcut And Proof-Governance Repair"
)
FAM006_WS47_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS48_HEADING = (
    "Returned LV1 Denial And WS48 Human-Client Validation Closeout"
)
FAM006_WS48_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS49_HEADING = (
    "Workstream WS49 Dashboard NCP Interaction Isolation And Tray Action Safety Repair"
)
FAM006_WS49_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS50_HEADING = (
    "Workstream WS50 Dashboard Scrollbar Boundary And Native Window Chrome Repair"
)
FAM006_WS50_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS51_HEADING = (
    "Workstream WS51 Dashboard Resize Hit Zone Scrollbar Inset And HUD State Persistence Repair"
)
FAM006_WS51_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS52_HEADING = "Workstream WS52 Dashboard Real Resize Recovery Repair"
FAM006_WS52_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS53_HEADING = "Workstream WS53 Dashboard Resize Edge Discoverability Repair"
FAM006_WS53_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS54_HEADING = "Workstream WS54 Dashboard Standard Resize Cursor Alignment Repair"
FAM006_WS54_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS55_HEADING = "Workstream WS55 Dashboard Resize Action Recovery After Cursor Alignment Repair"
FAM006_WS55_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_WS56_HEADING = "Workstream WS56 Dashboard Pre-Click Resize Cursor And Fluidity Repair"
FAM006_WS56_NEXT_SEAM = "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun"
FAM006_H1_HEADING = "Hardening H1 Dashboard-First Product Surface Rerun"
FAM006_H1_NEXT_SEAM = (
    "Live Validation LV1 - Monitoring HUD Product Surface Live Validation Rerun"
)
FAM006_ACTIVE_OVERLAY_H1_HEADING = (
    "Hardening H1 Active Overlay Recording Runtime Implementation"
)
FAM006_ACTIVE_OVERLAY_H1_NEXT_SEAM = (
    "Live Validation LV1 - FAM-006 Active Overlay Recording Runtime Implementation"
)
FAM006_ACTIVE_OVERLAY_H1_REQUIRED_PHRASES = (
    "H1 Admission:",
    "PASS - USER explicitly admitted Hardening H1",
    "H1 Result:",
    "Green - SLC-051 through SLC-055 implementation matches accepted BP1/BP2/BP3",
    "Accepted BP Trace:",
    "PASS - BP1 Branch Vision, BP2 Branch Plan, and BP3 Workstream Entry / Orchestration Validation are accepted or approved",
    "SLC-051 Pressure-Test:",
    "active Overlay Profile target/session truth markers",
    "SLC-052 Pressure-Test:",
    "HUD Overlay launcher and target preview markers",
    "SLC-053 Pressure-Test:",
    "standalone Recording Control window foundation markers",
    "SLC-054 Pressure-Test:",
    "output contract schema/readback and blocked execution markers",
    "SLC-055 Pressure-Test:",
    "Workstream Green proof and H1/LV1/UTS routing markers",
    "Future-Gated Boundary Check:",
    "recording execution, file writing, real Start/Stop controls, tray controls, export/share, provider/model work, Native Log Loader implementation, and FAM-007 mutation remain blocked",
    "UTS Phase Boundary:",
    "Formal User Test Summary export is exclusive to Live Validation Stage 1",
    "Helper Proof:",
    "python dev\\orin_fam006_hardening_h1.py",
    "Next Active Seam:",
    FAM006_ACTIVE_OVERLAY_H1_NEXT_SEAM,
)
FAM006_STAGE2_R6_REQUIRED_MARKERS = (
    "Current-Branch Scope Final:",
    "Future-Package Scope Final:",
    "Provider Path:",
    "Polling Posture:",
    "Warning Modality:",
    "External Telemetry Privacy:",
    "Audio/FAM-004 Boundary:",
    "Legacy/Nexus Naming Handling:",
    "Acceptance Criteria Final:",
    "Proof Standard Final:",
    "Validator Enforcement:",
    "Workstream Gate:",
)
FAM006_STAGE2_R6_REQUIRED_PHRASES = (
    "Nexus/NDAI-branded standalone Monitoring HUD shell/module",
    "full HWInfo/HWMonitor-level sensor coverage",
    "WS7 is provider-contract-first",
    "Fake CPU/GPU/thermal values are blocked",
    "No polling until a provider is selected",
    "first practical default is 1s-2s",
    "500ms minimum requires performance proof",
    "1ms per-card polling remains unsafe",
    "UI repaint cadence stays decoupled",
    "visual/non-invasive",
    "Screen flash needs accessibility review",
    "Audio/spoken warnings require later FAM-004/cross-family approval",
    "External/plugin telemetry remains future-package scope",
    "consent, provenance, source labeling, privacy warnings, and validation",
    "Current/future user-facing product copy should use Nexus",
    "active tracked source, runtime paths, validators, docs, generated-user surfaces, and user-facing copy must not carry retired legacy product identity",
    "Legacy Product Name Drift blocks Workstream",
    "no fake telemetry values presented as real",
    "Marker/DOM proof is supporting evidence only",
    "Stage 2-R9 now supersedes",
)
FAM006_STAGE2_R7_REQUIRED_PHRASES = (
    "Stage 1-R4 Result:",
    "PASS - finalized Stage 2-R6 product scope boundaries",
    "Planning Blocker Closeout:",
    "Branch Readiness Planning Incomplete is cleared",
    "WS7 Handoff:",
    "WS7 - Monitoring HUD Product Visibility And Acceptance Baseline",
    "PKG-006 remains In Progress",
    "package completion remains unclaimed",
    "Visible user-facing proof, full-desktop screenshot proof, and User Test Summary acceptance remain required",
)
FAM006_STAGE2_R8_REQUIRED_PHRASES = (
    "All retired legacy product naming is invalid for the current Nexus Desktop AI direction",
    "Workstream WS7 is blocked until legacy naming is removed or migrated",
    "Legacy Product Name Drift blocks Workstream implementation",
    "User Vision Input.txt was refreshed",
    "The artifact is not repo source truth until a later digest pass",
    "WS7 remains blocked on Legacy Product Name Drift",
)
FAM006_STAGE2_R9_REQUIRED_PHRASES = (
    "Refreshed USER Vision Input Digest:",
    "Cleared Blockers:",
    "Legacy Product Name Drift; USER Vision Input Pending",
    "Remaining Blockers:",
    "Persona Switch Scope Boundary Pending",
    "ORIN is the shipped/default persona",
    "ARIA is beta-facing locked/coming soon",
    "full HUD",
    "draggable/resizable category cards",
    "fastest practical/default polling rate is 1s",
    "visual/non-invasive warning posture",
    "fake telemetry remains blocked",
    "WS7 remains blocked until Stage 1-R6",
)
FAM006_STAGE2_R10_REQUIRED_PHRASES = (
    "Stage 1-R6 Result:",
    "PASS - refreshed USER Vision Input digest",
    "Planning Blocker Closeout:",
    "Branch Readiness Planning Incomplete is cleared",
    "Branch Reach Unproven is cleared",
    "Current Branch vs Future Package Boundary Missing is cleared",
    "Hardware Telemetry Provider Selection Pending is converted",
    "External Telemetry Privacy Model Missing is deferred",
    "Persona Switch Scope Boundary Pending is deferred",
    "Backlog Completion Unproven remains active",
    "WS7 Handoff:",
    "Workstream WS7 - Monitoring HUD Product Visibility And Acceptance Baseline",
    "PKG-006 remains In Progress",
    "package completion remains unclaimed",
)
FAM006_STAGE2_R11_REQUIRED_PHRASES = (
    "Stage 1-R7 Finding Recorded:",
    "LV1 State:",
    "FAIL / red",
    "Dashboard / Configuration Surface:",
    "Minimal Anchored HUD Overlay:",
    "ORIN/Core Non-Interference Expectation:",
    "Dashboard Repair Findings:",
    "Affected Slices:",
    "SLC-016 reopened",
    "SLC-026 reopened",
    "SLC-027 reopened",
    "SLC-028 reopened",
    "SLC-029 reopened",
    "Acceptance Criteria Updates:",
    "Dashboard and minimal HUD must be separate product surfaces",
    "minimal HUD is the anchored desktop overlay",
    "Validator / Proof Plan:",
    "OS-level click-through/non-blocking evidence",
    "Core visual transparency/non-interference evidence",
    "fresh full-desktop proof root",
    "Legal Repair Sequence:",
    "Stage 1-R8 source-truth revalidation",
    "bounded Workstream repair seams",
    "Hardening rerun",
    "Live Validation rerun",
)
FAM006_STAGE2_R12_REQUIRED_PHRASES = (
    "Interface Release Boundary:",
    "Primary Interface Release Surface:",
    "Monitoring HUD Dashboard / control panel",
    "Interface Bundle User Approval:",
    "Not granted",
    "Dashboard-First Scope:",
    "Overlay/Display Classification:",
    "Deferred / dormant / non-gating",
    "Core Repair Classification:",
    "Dependency repair only",
    "Source-Truth Downgrade:",
    "Dashboard Acceptance Pending",
    "Overlay Scope Deferred",
    "Core Repair Dependency Only",
    "Branch Readiness Interface Planning Incomplete",
    "Next Legal Seam:",
    "Branch Readiness Stage 1-R10 - Dashboard-First Interface Boundary Revalidation",
)
FAM006_STAGE2_R13_REQUIRED_PHRASES = (
    "Stage 1-R10 PASS Recording:",
    "PASS - Dashboard-first interface boundary is sufficient",
    "Phase Handoff:",
    "Current phase returns to Workstream",
    "Next Legal Seam:",
    "Workstream WS31 - Dashboard Control Panel Acceptance Baseline And Overlay Deferral Enforcement",
    "Branch Readiness Interface Planning Incomplete Closeout:",
    "Cleared",
    "Interface Acceptance Missing Closeout:",
    "Dashboard Acceptance Pending remains the Workstream product acceptance gap",
    "Dashboard-First Handoff:",
    "Dashboard/control panel remains the primary current-branch interface release surface",
    "Overlay/Display Classification:",
    "Deferred / dormant / non-gating",
    "Core Dependency Classification:",
    "Dependency repair only",
    "Bounded Workstream Sequence:",
    "WS31 Dashboard-only acceptance baseline",
)
FAM006_WS31_REQUIRED_PHRASES = (
    "WS31 Result:",
    "Green - Dashboard-first acceptance baseline recorded",
    "Dashboard-First Acceptance Baseline:",
    "Dashboard/control panel is the only current-branch interface release gate",
    "Overlay Deferral Enforcement:",
    "deferred / dormant / non-gating",
    "Validator / Proof Path:",
    "Dashboard-specific proof may pass without Overlay/display acceptance",
    "Package Status:",
    "PKG-006 remains In Progress",
    "Package Completion:",
    "Unclaimed",
    "LV1 / PR Status:",
    "LV1 remains historical red",
    "Next Active Seam:",
    FAM006_WS31_NEXT_SEAM,
)
FAM006_WS32_REQUIRED_PHRASES = (
    "WS32 Result:",
    "Green - Dashboard standalone window movement, clipping boundary, and Core/Overlay decoupling proof recorded",
    "Dashboard Standalone Movement:",
    "dashboard native window moves across the virtual desktop",
    "Clipping Boundary:",
    "within the target monitor and full virtual desktop",
    "Core / Overlay Decoupling:",
    "Core geometry and Overlay/display geometry remain unchanged",
    "Runtime Markers:",
    "MONITORING_HUD_DASHBOARD_STANDALONE_WINDOW_TRAVEL_READY",
    "MONITORING_HUD_DASHBOARD_CLIPPING_BOUNDARY_READY",
    "MONITORING_HUD_DASHBOARD_CORE_OVERLAY_DECOUPLING_READY",
    "Overlay Classification:",
    "deferred/non-gating",
    "Core Classification:",
    "dependency-only",
    "Package Completion:",
    "Unclaimed",
    "Next Active Seam:",
    FAM006_WS32_NEXT_SEAM,
)
FAM006_WS33_REQUIRED_PHRASES = (
    "WS33 Result:",
    "Green - Dashboard settings/control content polish and monitor-management clarity recorded",
    "Dashboard Settings Content Polish:",
    "Dashboard/control panel copy now presents a settings/control surface",
    "Monitor Management Clarity:",
    "Monitor groups are organizational settings objects",
    "Overlay Non-Gating Copy:",
    "Overlay/display remains deferred/non-gating",
    "Runtime Markers:",
    "MONITORING_HUD_DASHBOARD_SETTINGS_CONTENT_READY",
    "MONITORING_HUD_DASHBOARD_MONITOR_GROUP_CLARITY_READY",
    "MONITORING_HUD_DASHBOARD_OVERLAY_NON_GATING_COPY_READY",
    "Dashboard Runtime Contract:",
    'data-dashboard-content-polish="ws33-settings-control-clarity"',
    'data-monitor-group-model="organizational-groups-settings-only"',
    'data-dashboard-monitor-card-policy="overlay-display-owns-monitor-cards"',
    "Dashboard Acceptance Pending remains active",
    "Package Completion:",
    "Unclaimed",
    "Next Active Seam:",
    FAM006_WS33_NEXT_SEAM,
)
FAM006_WS34_REQUIRED_PHRASES = (
    "WS34 Result:",
    "Green - Dashboard provider/setup/no-data/degraded truth and visual warning posture controls recorded",
    "Provider Truth:",
    "provider-contract-first telemetry",
    "No-Data / Degraded State Model:",
    "setup, no-data, degraded, and ready",
    "Warning Posture Controls:",
    "visual/non-invasive warning posture controls only",
    "Runtime Markers:",
    "MONITORING_HUD_DASHBOARD_PROVIDER_TRUTH_READY",
    "MONITORING_HUD_DASHBOARD_STATE_MODEL_READY",
    "MONITORING_HUD_DASHBOARD_WARNING_CONTROLS_READY",
    "Dashboard Runtime Contract:",
    'data-dashboard-provider-truth="provider-contract-first"',
    'data-dashboard-state-model="setup-no-data-degraded-warning"',
    'data-dashboard-warning-controls="visual-non-invasive-only"',
    'data-dashboard-fake-telemetry-policy="blocked"',
    "Dashboard Acceptance Pending remains active",
    "Package Completion:",
    "Unclaimed",
    "Next Active Seam:",
    FAM006_WS34_NEXT_SEAM,
)
FAM006_WS35_REQUIRED_PHRASES = (
    "WS35 Result:",
    "Green - Dashboard-specific static/live proof, screenshots, and Live Validation UTS boundary recorded",
    "Dashboard-Specific Proof Refresh:",
    "Dashboard/control panel remains the only current-branch interface release gate",
    "Screenshot Proof:",
    "fresh before/after full virtual-desktop screenshots",
    "USER-Inspectable Screenshot Folder:",
    "Live Validation UTS Boundary:",
    "formal User Test Summary export is Live Validation Stage 1 only",
    "Desktop UTS Export State:",
    "Not generated in Workstream",
    "Returned UTS Results:",
    "Reserved for Live Validation Stage 1/Stage 2 gate",
    "Overlay Classification:",
    "deferred/non-gating",
    "Core Classification:",
    "dependency-only",
    "Package Completion:",
    "Unclaimed",
    "Next Active Seam:",
    FAM006_WS35_NEXT_SEAM,
)
FAM006_WS36_REQUIRED_PHRASES = (
    "WS36 Result:",
    "Green - Dashboard-focused Workstream completion review passed and Hardening handoff recorded",
    "Workstream Completion Review:",
    "Dashboard-first current-branch scope is green for Hardening rerun",
    "Hardening Handoff:",
    "Hardening H1 - Monitoring HUD Product Surface Hardening Rerun",
    "Dashboard Acceptance Pending:",
    "returned UTS acceptance remains reserved for Live Validation Stage 1/Stage 2 gate",
    "Overlay Classification:",
    "deferred/non-gating",
    "Core Classification:",
    "dependency-only",
    "Package Completion:",
    "Unclaimed",
    "Next Active Seam:",
    FAM006_WS36_NEXT_SEAM,
)
FAM006_WS37_REQUIRED_PHRASES = (
    "WS37 Result:",
    "Green for runtime safety repair",
    "Startup Repair:",
    "MONITORING_HUD_STARTUP_SUPPRESSED",
    "HUD Feature Off / Tray Repair:",
    "Enable HUD Feature",
    "HUD Overlay Deferred",
    "Focus / Topmost / Z-Order Repair:",
    "Dashboard / Overlay Isolation:",
    "NCP Regression Proof:",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Next Legal Seam:",
    FAM006_WS37_NEXT_SEAM,
)
FAM006_WS38_REQUIRED_PHRASES = (
    "WS38 Result:",
    "Green for Dashboard window ownership/focus/movement safety",
    "Window Ownership Repair:",
    "OS-native system move",
    "Focus / Topmost Proof:",
    "Movement Model Proof:",
    "Control Hit-Target Guard:",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Next Legal Seam:",
    FAM006_WS38_NEXT_SEAM,
)
FAM006_WS39_REQUIRED_PHRASES = (
    "WS39 Result:",
    "Green for Dashboard shell/layout/frame/resize/readability repair",
    "Title / Header Repair:",
    "HUD Dashboard",
    "Sticky Header Repair:",
    "Frame / Scrollbar Repair:",
    "Resize Repair:",
    "os-edge-corner-resize",
    "Readability Repair:",
    "Button Hierarchy Repair:",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Next Legal Seam:",
    FAM006_WS39_NEXT_SEAM,
)
FAM006_WS40_REQUIRED_PHRASES = (
    "WS40 Result:",
    "Green for Dashboard IA/content/naming/control-hub repair",
    "Control Hub Repair:",
    "Monitor Groups",
    "Data Sources",
    "HUD Display",
    "Warning Notifications",
    "Proof / Debug Reroute:",
    "validator artifacts, not Dashboard home content",
    "Polling Placement Repair:",
    "Monitor Group Create/Edit",
    "Child-Window Boundary:",
    "WS41 if admitted",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Next Legal Seam:",
    FAM006_WS40_NEXT_SEAM,
)
FAM006_WS41_REQUIRED_PHRASES = (
    "WS41 Admission Decision:",
    "Deferred - USER agreed with Codex's scope determination",
    "WS41 Result:",
    "Green for source-truth deferral only",
    "Deferral Scope:",
    "Create/Edit Monitor Group",
    "Data Sources/Provider Setup",
    "HUD Display Settings",
    "Current-Branch Boundary:",
    "not part of current FAM-006 Dashboard acceptance",
    "Element Ledger Update:",
    "FAM006-DASH-CHILD-WINDOW-049 is deferred/future",
    "USER Admission Handling:",
    "cleared by deferral, not by implementation or waiver",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Next Legal Seam:",
    FAM006_WS41_NEXT_SEAM,
)
FAM006_WS42_REQUIRED_PHRASES = (
    "WS42 Admission:",
    "bounded Workstream continuation from WS41 deferral",
    "WS42 Result:",
    "Green - Dashboard-specific static/live proof readiness passed",
    "Proof Standard:",
    "formal User Test Summary export remains Live Validation Stage 1 only",
    "Runtime / Proof Helper Update:",
    "Dashboard-first proof readiness",
    "Static Validation:",
    "PASS - dev/orin_monitoring_hud_surface_validation.py",
    "Internal Sandbox Proof:",
    "dev/logs/fam_006_monitoring_hud_internal_sandbox/20260509_001414_manifest.json",
    "Live Helper Proof:",
    "dev/logs/fam_006_monitoring_hud_live_validation/20260509_001424_797",
    "Live Helper Manifest:",
    "manifest.json",
    "Interaction Manifest:",
    "monitoring_hud_live_client_interaction_manifest.json",
    "Screenshot Proof Root:",
    "USER-Inspectable Screenshot Folder:",
    "Dashboard Proof Findings:",
    "PASS - Dashboard control hub identity",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Formal UTS Boundary:",
    "Not generated in Workstream",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Workstream Completion Status:",
    "Green",
    "Continue Decision:",
    "Stop at phase boundary",
    "Continuation Execution Latch:",
    "Inactive - WS42 is Green",
    "Stop Basis:",
    "Phase Boundary",
    "Next Legal Seam:",
    FAM006_WS42_NEXT_SEAM,
)
FAM006_WS43_REQUIRED_PHRASES = (
    "WS43 Admission:",
    "USER approved bounded Workstream WS43",
    "WS43 Result:",
    "Green for Dashboard runtime tray shutdown safety repair",
    "Runtime / Tray Repair:",
    "separate from Dashboard window visibility",
    "Tray HUD Enable Flash Repair:",
    "MONITORING_HUD_TRAY_ENABLE_RENDER_STABLE_READY",
    "Tray HUD Enable / Disable State Repair:",
    "Enable HUD Feature -> Disable HUD Feature roundtrip",
    "Dashboard Tray Open / Close Repair:",
    "MONITORING_HUD_TRAY_DASHBOARD_OPEN_CLOSE_READY",
    "Disable-HUD Recovery Repair:",
    "MONITORING_HUD_DISABLE_RECOVERY_READY",
    "#25 Current-vs-Future Classification:",
    "tray Exit NDAI confirmation",
    "NCP / Saved-Action Regression Proof:",
    "dev/orin_saved_action_authoring_ui_validation.py",
    "Validator / Helper Updates:",
    "desktop entrypoint validation now exercises tray HUD lifecycle actions",
    "Element Rows Updated:",
    "FAM006-HUD-TRAY-FLASH-051",
    "FAM006-HUD-TRAY-STATE-LOCK-052",
    "FAM006-DASH-TRAY-OPEN-CLOSE-053",
    "FAM006-HUD-DISABLE-UNUSABLE-054",
    "FAM006-TRAY-SHUTDOWN-CONFIRM-055",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Formal UTS Boundary:",
    "WS43 does not generate, refresh, or digest",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Active - next bounded Workstream seam is WS44",
    "Next Legal Seam:",
    FAM006_WS43_NEXT_SEAM,
)
FAM006_WS44_REQUIRED_PHRASES = (
    "WS44 Admission:",
    "bounded Workstream continuation latch",
    "WS44 Result:",
    "Green for Dashboard frame/scroll/resize/visual shell repair",
    "Frame / Scroll Repair:",
    "monitoring-hud__chrome",
    "Haze / Square Frame Repair:",
    "single-rounded-dashboard-chrome",
    "Native Resize Repair:",
    "MONITORING_HUD_NATIVE_WINDOW_RESIZE_FALLBACK_STARTED",
    "Deadzone Repair:",
    "auto-height",
    "Checkered Pattern Scope:",
    "control-hub cards",
    "Sticky Header Occlusion Repair:",
    "opaque scroll mask",
    "Validator / Helper Updates:",
    "MONITORING_HUD_DASHBOARD_VISUAL_SHELL_READY",
    "Element Rows Updated:",
    "FAM006-DASH-FRAME-HAZE-056",
    "FAM006-DASH-RESIZE-057",
    "FAM006-DASH-DEADZONE-058",
    "FAM006-DASH-STICKY-OCCLUSION-059",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Formal UTS Boundary:",
    "WS44 does not generate, refresh, or digest",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Active - next bounded Workstream seam is WS45",
    "Next Legal Seam:",
    FAM006_WS44_NEXT_SEAM,
)
FAM006_WS45_REQUIRED_PHRASES = (
    "WS45 Admission:",
    "bounded Workstream continuation latch",
    "WS45 Result:",
    "Green for Dashboard IA/naming/action cleanup",
    "Provider Hero Slab Removal:",
    "provider/native CPU hero slab is removed",
    "Quick Access Cleanup:",
    "warning-notifications-only",
    "Monitor Groups Action Cleanup:",
    "card-local action IDs",
    "Data Sources Deferred Action:",
    "Data Sources Window Deferred",
    "HUD Overlay Terminology:",
    "removes HUD Display terminology",
    "Card Order / Redundancy Cleanup:",
    "01 HUD Overlay",
    "Validator / Helper Updates:",
    "WS45 IA model markers",
    "Element Rows Updated:",
    "FAM006-DASH-QUICK-ACCESS-060",
    "FAM006-DASH-DEFERRED-BUTTON-061",
    "FAM006-DASH-HUD-OVERLAY-COPY-062",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Formal UTS Boundary:",
    "WS45 does not generate, refresh, or digest",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Active - next bounded Workstream seam is WS46",
    "Next Legal Seam:",
    FAM006_WS45_NEXT_SEAM,
)
FAM006_WS46_REQUIRED_PHRASES = (
    "WS46 Admission:",
    "bounded Workstream continuation from WS45",
    "WS46 Result:",
    "Green for Dashboard returned-feedback static/live proof readiness",
    "Static Proof:",
    "PASS - dev/orin_monitoring_hud_surface_validation.py",
    "Internal Sandbox Proof:",
    "PASS - dev/orin_monitoring_hud_internal_sandbox_validation.py",
    "Active-Client Live Proof:",
    "dev/logs/fam_006_monitoring_hud_live_validation/20260509_130205_061",
    "Interaction Manifest:",
    "monitoring_hud_live_client_interaction_manifest.json",
    "Proof Harness Repair:",
    "tray-owned Dashboard close/open path",
    "Live Helper Manifest Fields:",
    "dashboardUserTestSummaryExportRefreshed=false",
    "elementLedgerAlignedUserTestSummary=false",
    "Formal UTS Boundary:",
    "WS46 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Package Completion:",
    "Unclaimed",
    "Continue Decision:",
    "Stop at phase boundary",
    "Continuation Execution Latch:",
    "Inactive - Workstream is green; Hardening phase-boundary stop",
    "Stop Basis:",
    "Workstream Green",
    "Next Legal Seam:",
    FAM006_WS46_NEXT_SEAM,
)
FAM006_H1_REQUIRED_PHRASES = (
    "H1 Admission:",
    "PASS - USER explicitly admitted Hardening H1",
    "WS56 Workstream Green phase-boundary stop",
    "H1 Result:",
    "Green - Dashboard-first Monitoring HUD product surface hardening rerun passed after WS56",
    "Dashboard-First Hardening Scope:",
    "WS56 Pre-Click Resize Cursor Pressure-Test:",
    "90ms hover delay",
    "right inside offset 13px",
    "WS56 Resize Fluidity Pressure-Test:",
    "cornerUniqueSizes=28",
    "rightUniqueWidths=28",
    "bottomUniqueHeights=28",
    "Resize Geometry Evidence:",
    "20260511_134958_847/human_client_manifest.json",
    "corner resize 780x1060 to 860x1130",
    "right-edge width 860 to 936",
    "bottom-edge height 1130 to 1206",
    "Event Loop / Responsiveness Check:",
    "desktop entrypoint/tray validation and saved-action/NCP validation passed after the 8ms resize polling repair",
    "Dashboard Chrome / Scrollbar Boundary Pressure-Test:",
    "one rounded native window boundary",
    "square translucent outer haze removal",
    "rounded-window-clipped scrollbar posture",
    "Live Helper Timeout Repair:",
    "fresh active-client proof after WS56",
    "Overlay Classification:",
    "deferred/non-gating",
    "Core Classification:",
    "dependency-only",
    "UTS Phase Boundary:",
    "formal User Test Summary export, handoff refresh, and returned-result digestion are Live Validation Stage 1 only",
    "Static Validation:",
    "PASS - dev/orin_monitoring_hud_surface_validation.py",
    "Internal Sandbox Proof:",
    "20260511_141234_manifest.json",
    "Desktop Entrypoint / Startup / Tray Proof:",
    "DesktopEntrypointValidationReport_20260511_135702.txt",
    "Human-Client Proof:",
    "20260511_134958_847/human_client_manifest.json",
    "Live Helper Proof:",
    "20260511_135242_250/manifest.json",
    "Interaction Manifest:",
    "20260511_135242_250/monitoring_hud_live_client_interaction_manifest.json",
    "Screenshot Proof Root:",
    "20260511_135242_250",
    "USER-Inspectable Screenshot Folder:",
    "Package Status:",
    "PKG-006 remains In Progress",
    "Package Completion:",
    "Unclaimed",
    "LV1 / PR Status:",
    "LV1 rerun is required after explicit USER Live Validation admission",
    "Next Active Seam:",
    FAM006_H1_NEXT_SEAM,
)
FAM006_STAGE2_REAL_CLIENT_REQUIRED_PHRASES = (
    "Stage 2 Admission:",
    "Returned Real-Client Failure State:",
    "Real-Client Finding RUI-039:",
    "Real-Client Finding RUI-040:",
    "Governance Finding RUI-041:",
    "Proof Class Correction:",
    "User-Facing Shortcut Rule:",
    "Codex Precheck Rule:",
    "Fake/Offscreen Proof Rule:",
    "LV2 Status:",
    "Dashboard Acceptance State:",
    "Package Status:",
    "PKG-006 remains In Progress",
    "Package Completion:",
    "Unclaimed",
    "PR Readiness:",
    "Blocked",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Next Legal Seam:",
    FAM006_STAGE2_REAL_CLIENT_NEXT_SEAM,
)
FAM006_WS47_REQUIRED_PHRASES = (
    "WS47 Admission:",
    "USER approved bounded Workstream WS47",
    "WS47 Result:",
    "Green for real-client tray shortcut and proof-governance repair",
    "Runtime / Tray Repair:",
    "Tray Exit Confirmation Repair:",
    "Real Shortcut Precheck Proof:",
    "real_client_tray_precheck_manifest.json",
    "Precheck Step Results:",
    "Enable HUD Feature opened the real HUD Dashboard",
    "Proof Class Separation:",
    "fake/offscreen",
    "realUserOperatedTrayProof remains USER_LV1_REQUIRED",
    "Validator / Helper Updates:",
    "dev/orin_desktop_entrypoint_validation.py",
    "Element Rows Updated:",
    "FAM006-TRAY-SHUTDOWN-CONFIRM-055",
    "FAM006-DASH-TRAY-OPEN-CLOSE-053",
    "Returned USER Issue Register Updates:",
    "Formal UTS Boundary:",
    "WS47 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continue Decision:",
    "Stop at phase boundary",
    "Continuation Execution Latch:",
    "Inactive - WS47 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS47_NEXT_SEAM,
)
FAM006_WS48_REQUIRED_PHRASES = (
    "Returned USER Result:",
    "USER denied the LV1 handoff",
    "LV1 Disposition:",
    "Stale / denied for acceptance",
    "FAM006-RUI-042",
    "FAM006-RUI-043",
    "Human-client validation manifest",
    "dev/logs/fam_006_human_client_validation/20260510_034725_127/human_client_manifest.json",
    "Tray Controller Refactor:",
    "desktop/tray_controller.py",
    "Real-Client Proof Summary:",
    "actual desktop shortcut launch",
    "visible native tray menu",
    "visible shortcut launch",
    "visible tray/menu actions",
    "mouse movement/click/drag/resize",
    "Formal UTS Boundary:",
    "must not be refreshed again until USER admits Hardening",
    "Dashboard Acceptance State:",
    "Blocked",
    "LV2 Status:",
    "Blocked - do not proceed as PASS digestion",
    "Stop Basis:",
    "Workstream Green",
    "Next Legal Seam:",
    FAM006_WS48_NEXT_SEAM,
)
FAM006_WS49_REQUIRED_PHRASES = (
    "WS49 Admission:",
    "bounded Workstream continuation",
    "WS49 Result:",
    "Green for Dashboard NCP interaction isolation and tray action safety",
    "FAM006-RUI-044",
    "FAM006-RUI-045",
    "FAM006-RUI-046",
    "FAM006-RUI-047",
    "Runtime / Tray Repair:",
    "desktop/tray_controller.py",
    "Dashboard / NCP Interaction Repair:",
    "Dashboard native-panel mouse handling",
    "Authoring Dialog Safety Repair:",
    "TRAY_CREATE_CUSTOM_TASK_ABORTED",
    "Helper / Proof Repair:",
    "native tray popup",
    "Human-Client Validation Manifest:",
    "dev/logs/fam_006_human_client_validation/20260510_121038_854/human_client_manifest.json",
    "Real-Client Proof Summary:",
    "NCP Create Custom Task/Create Custom Group/Manage Custom Tasks/Manage Custom Groups",
    "tray Create Custom Task duplicate guard",
    "Element Rows Updated:",
    "FAM006-TRAY-ACTION-ORDER-067",
    "FAM006-DASH-NCP-MOUSE-068",
    "FAM006-TRAY-AUTHORING-DIALOG-GUARD-069",
    "FAM006-TRAY-EXIT-PROMPT-VISUAL-070",
    "Formal UTS Boundary:",
    "WS49 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continue Decision:",
    "Stop at phase boundary",
    "Continuation Execution Latch:",
    "Inactive - WS49 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS49_NEXT_SEAM,
)
FAM006_WS50_REQUIRED_PHRASES = (
    "WS50 Admission:",
    "bounded Workstream repair",
    "WS50 Result:",
    "Green for focused Dashboard scrollbar/native-window boundary repair",
    "Returned USER Evidence:",
    "Scrollbar.png",
    "Window border.png",
    "Runtime / CSS Repair:",
    "fills the native HUD window",
    "clips the root and .monitoring-hud__chrome to one 28px rounded boundary",
    "Scrollbar Boundary Repair:",
    "rounded-window-clipped",
    "Validator / Helper Updates:",
    'data-scrollbar-boundary="rounded-window-clipped"',
    'data-outer-frame-haze="removed-no-square-layer"',
    "Active-Client Proof:",
    "dev/logs/fam_006_monitoring_hud_live_validation/20260510_165507_981",
    "Element Rows Updated:",
    "FAM006-DASH-SCROLL-007",
    "FAM006-DASH-FRAME-HAZE-056",
    "Returned USER Issue Rows Updated:",
    "FAM006-RUI-026",
    "FAM006-RUI-027",
    "Formal UTS Boundary:",
    "WS50 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Inactive - WS50 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS50_NEXT_SEAM,
)
FAM006_WS51_REQUIRED_PHRASES = (
    "WS51 Admission:",
    "bounded Workstream repair",
    "WS51 Result:",
    "Green for focused Dashboard resize hit-zone, scrollbar inset, and HUD feature persistence repair",
    "Returned USER Evidence:",
    "resize hit zone inconsistent/unreliable",
    "scrollbar vertical part slightly out of range",
    "HUD Feature enabled state resets after app relaunch",
    "Runtime Resize Repair:",
    "WM_NCHITTEST",
    "30px",
    "Scrollbar Inset Repair:",
    "6px",
    "52px",
    "HUD Feature Persistence Repair:",
    "desktop/monitoring_hud_state.py",
    "Validator / Helper Updates:",
    "NEXUS_MONITORING_HUD_STATE_PATH",
    "Element Rows Updated:",
    "FAM006-DASH-RESIZE-057",
    "FAM006-DASH-STATE-PERSIST-013",
    "Returned USER Issue Rows Updated:",
    "FAM006-RUI-048",
    "FAM006-RUI-049",
    "FAM006-RUI-050",
    "Prior Proof Staleness:",
    "Post-WS50 H1 and LV1 are stale",
    "Formal UTS Boundary:",
    "WS51 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Inactive - WS51 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS51_NEXT_SEAM,
)
FAM006_WS52_REQUIRED_PHRASES = (
    "WS52 Admission:",
    "post-WS51 Bug 1",
    "WS52 Result:",
    "Green for focused Dashboard real resize recovery repair",
    "Returned USER Evidence:",
    "you can no longer resize the window",
    "Runtime Resize Repair:",
    "fallback geometry resizing",
    "MONITORING_HUD_NATIVE_WINDOW_RESIZE_FALLBACK_STARTED",
    "MONITORING_HUD_NATIVE_WINDOW_RESIZE_READY",
    "Proof Correction:",
    "WS51 native WM_NCHITTEST/startSystemResize proof is superseded",
    "Validator / Helper Updates:",
    "actual Dashboard size delta",
    "Validation Proof:",
    "20260511_060551_693",
    "780x1060 to 858x1128",
    "Element Rows Updated:",
    "FAM006-DASH-RESIZE-057",
    "FAM006-GOV-HUMAN-CLIENT-065",
    "Returned USER Issue Rows Updated:",
    "FAM006-RUI-051",
    "Prior Proof Staleness:",
    "WS51 native resize proof",
    "Formal UTS Boundary:",
    "WS52 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Inactive - WS52 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS52_NEXT_SEAM,
)
FAM006_WS53_REQUIRED_PHRASES = (
    "WS53 Admission:",
    "edge/corner rail remains too difficult",
    "WS53 Result:",
    "Green for focused Dashboard resize edge discoverability repair",
    "Returned USER Evidence:",
    "resize edge is inconsistent and hard to find",
    "Runtime Resize Repair:",
    "58px",
    "mouse tracking",
    "Validator / Helper Updates:",
    "corner, right-edge, and bottom-edge resize rails",
    "Validation Proof:",
    "20260511_062804_831",
    "corner resize from 780x1020 to 886x1116",
    "right-edge resize width from 886 to 996",
    "bottom-edge resize height from 1116 to 1226",
    "Element Rows Updated:",
    "FAM006-DASH-RESIZE-057",
    "FAM006-GOV-HUMAN-CLIENT-065",
    "Returned USER Issue Rows Updated:",
    "FAM006-RUI-052",
    "Prior Proof Staleness:",
    "WS52 proves resize recovery but is insufficient",
    "Formal UTS Boundary:",
    "WS53 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Inactive - WS53 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS53_NEXT_SEAM,
)
FAM006_WS54_REQUIRED_PHRASES = (
    "WS54 Admission:",
    "standard resize cursor appear too far inside",
    "WS54 Result:",
    "Green for focused Dashboard standard resize cursor-alignment repair",
    "Returned USER Evidence:",
    "explorer_Kwqy4JkDv7.mp4",
    "Runtime Resize Cursor Repair:",
    "cursor-aligned 12px",
    "real Windows non-client edge hit-tests",
    "Validator / Helper Updates:",
    "10px visible rail",
    "28px interior/outside",
    "Validation Proof:",
    "20260511_094825_007",
    "rightEdge10px=htright",
    "bottomEdge10px=htbottom",
    "corner10px=htbottomright",
    "Element Rows Updated:",
    "FAM006-DASH-RESIZE-057",
    "FAM006-GOV-HUMAN-CLIENT-065",
    "Returned USER Issue Rows Updated:",
    "FAM006-RUI-053",
    "Prior Proof Staleness:",
    "Post-WS53 H1 and LV1 are stale for RUI-053",
    "Formal UTS Boundary:",
    "WS54 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Inactive - WS54 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS54_NEXT_SEAM,
)
FAM006_WS55_REQUIRED_PHRASES = (
    "WS55 Admission:",
    "can no longer resize the window",
    "WS55 Result:",
    "Green for focused Dashboard resize action recovery",
    "Returned USER Evidence:",
    "Runtime Resize Action Repair:",
    "Windows owns the cursor state",
    "cursor-hit-test-owned-geometry-resize",
    "Validator / Helper Updates:",
    "dashboard_resize_cursor_transition_discovery",
    "discovered Windows resize cursor transition",
    "Validation Proof:",
    "Element Rows Updated:",
    "FAM006-DASH-RESIZE-057",
    "FAM006-GOV-HUMAN-CLIENT-065",
    "Returned USER Issue Rows Updated:",
    "FAM006-RUI-054",
    "Prior Proof Staleness:",
    "Post-WS54 H1 and LV1 are stale for RUI-054",
    "Formal UTS Boundary:",
    "WS55 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Inactive - WS55 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS55_NEXT_SEAM,
)
FAM006_WS56_REQUIRED_PHRASES = (
    "WS56 Admission:",
    "left-click hold",
    "choppy",
    "WS56 Result:",
    "Green for focused Dashboard pre-click resize cursor and fluidity repair",
    "Returned USER Evidence:",
    "Runtime Resize Hover Repair:",
    "WM_SETCURSOR",
    "Runtime Resize Fluidity Repair:",
    "preclick-hover-cursor-owned-fluid-geometry-resize",
    "8ms",
    "Validator / Helper Updates:",
    "dashboard_resize_cursor_transition_discovery",
    "dashboard_resize_fluidity",
    "pre-click",
    "Validation Proof:",
    "20260511_124952_135",
    "28 unique geometry samples",
    "Element Rows Updated:",
    "FAM006-DASH-RESIZE-057",
    "FAM006-GOV-HUMAN-CLIENT-065",
    "Returned USER Issue Rows Updated:",
    "FAM006-RUI-055",
    "FAM006-RUI-056",
    "Prior Proof Staleness:",
    "Post-WS55 H1 and LV1 are stale for RUI-055 and RUI-056",
    "Formal UTS Boundary:",
    "WS56 does not generate, refresh, or digest",
    "Overlay Status:",
    "Deferred/dormant/non-gating",
    "Core Status:",
    "Dependency-only",
    "Dashboard Acceptance State:",
    "Still blocked",
    "Package Completion:",
    "Unclaimed",
    "Continuation Execution Latch:",
    "Inactive - WS56 is Green / Hardening phase-boundary stop",
    "Next Legal Seam:",
    FAM006_WS56_NEXT_SEAM,
)
FAM006_WORKSTREAM_CONTINUATION_REQUIRED_PHRASES = (
    "multi-slice HUD implementation continuation",
    "WS8 - Monitoring HUD Internal Sandbox Harness And State Matrix Baseline",
    "WS9 - Monitoring HUD Shell Module And Product Surface Extraction",
    "WS10 - Panel Movement Anchoring And Click-Through Runtime Behavior",
    "WS11 - Task-Tray Toggle And Unanchor Control Path",
    "WS12 - Category Card Layout Drag Resize And Snapping",
    "WS13 - Sensor Membership And Category Card Configuration Model",
    "WS14 - Safe Native Telemetry Provider Proof",
    "WS15 - Polling Cadence And Performance Guardrail",
    "WS16 - Visual Warning Baseline And Threshold Posture",
    "WS17 - Workstream Product Proof Refresh And Completion Review",
    "Formal User Test Summary export is exclusive to Live Validation Stage 1",
)
FAM006_FORBIDDEN_WORKSTREAM_UTS_PHRASES = (
    "Workstream WS8 - Monitoring HUD User Test Summary And Product Acceptance Digest",
    "WS8 User Test Summary blocker active",
    "User Test Summary Results Pending` is a named Workstream blocker",
    "Workstream is stopped on `User Test Summary Results Pending`",
    "WS8 blocked on User Test Summary",
)
USER_VISION_INPUT_HANDOFF_MARKERS = (
    "USER Vision Input Artifact Path:",
    "USER Vision Input Artifact State:",
    "USER Vision Input Answer State:",
    "USER Vision Input Digest State:",
    "Repo Source Truth Update Rule:",
)
PRODUCT_PLANNING_BLOCKERS = (
    "Product Vision Input Missing",
    "USER Vision Question Packet Missing",
    "USER Vision Recommendation Missing",
    "USER Vision Questions Unanswered",
    USER_VISION_INPUT_PENDING_BLOCKER,
    USER_VISION_INPUT_FILE_MISSING_BLOCKER,
    USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER,
    USER_VISION_INPUT_DIGEST_PENDING_BLOCKER,
    LEGACY_PRODUCT_NAME_DRIFT_BLOCKER,
    "Project-Wide Vision Alignment Missing",
    "Branch-Specific Vision Alignment Missing",
    "System Concept Model Missing",
    "Entity / Profile Model Missing",
    "User Workflow Model Missing",
    "Scale / Data Volume Model Missing",
    "Configuration And State Model Missing",
    "Expected User-Facing Outcomes Missing",
    "Codex Additional Recommendations Missing",
    "USER Critique Loop Missing",
    "USER Decision Ledger Missing",
    "Deferred Ideas / Future Package Ledger Missing",
    "Planning Adequacy Review Missing",
    "Rejected Shallow Plan Missing",
    "Alternatives And Tradeoffs Missing",
    "Whole-System Interaction Map Missing",
    "Minimum Viable vs Full System Boundary Missing",
    "Open Questions / USER Decision Points Missing",
    HARDWARE_TELEMETRY_PROVIDER_PENDING_BLOCKER,
    POLLING_FLOOR_UNDECIDED_BLOCKER,
    WARNING_DELIVERY_MODALITY_PENDING_BLOCKER,
    EXTERNAL_TELEMETRY_PRIVACY_MODEL_MISSING_BLOCKER,
    AUDIO_WARNING_CROSS_FAMILY_APPROVAL_MISSING_BLOCKER,
    PERSONA_SWITCH_SCOPE_BOUNDARY_PENDING_BLOCKER,
    "Branch Reach Unproven",
    "Feature Element Breakdown Missing",
    "Element Validation Ledger Missing",
    "Created Element Untracked",
    "Touched Element Proof Missing",
    "Affected Element Validation Missing",
    "User-Facing Element Acceptance Missing",
    "Deferred Element Boundary Missing",
    "Element Proof Stale",
    "Marker-Only Element Proof",
    "Element Ledger Placement Drift",
    "Feature Element Source Marker Orphaned",
    "High-Risk Element Source Owner Missing",
    "Feature Element Marker Proof Insufficient",
    "Feature Element Source Marker Stale",
    "Feature Element Source Marker Mismatch",
    "Acceptance Criteria Missing",
    "User-Facing Proof Standard Missing",
    "Current Branch vs Future Package Boundary Missing",
    PRODUCT_PLANNING_INCOMPLETE_BLOCKER,
)
VISIBLE_USER_FACING_PROOF_REQUIRED_LABEL = "Visible User-Facing Proof Required:"
VISIBLE_USER_FACING_PROOF_LABEL = "Visible User-Facing Proof:"
VISIBLE_USER_FACING_PROOF_PASS_VALUES = {"pass", "waived"}

ELEMENT_VALIDATION_LEDGER_REQUIRED_PHRASES = {Path('Docs/workstreams/index.md'): ('Element Validation Ledger rows live in the owning traceability surface by default', 'promoted workstreams keep the active ledger inside the canonical workstream doc', '`Registry-only` active branches keep the active ledger inside the active branch authority record', 'a large active Element Validation Ledger may use a companion file only when the owning workstream doc or branch authority record contains the canonical pointer', 'created, touched, affected, deferred, future, dependency-only, and non-gating supporting product elements', '`## Element Validation Ledger` or a canonical pointer'), Path('Docs/development_rules.md'): ('Element Validation Ledger = row-level created/touched/affected/deferred/future element proof tracking', '`Source-Truth Placement Preflight`', '`No Existing Owner Fits`', 'Full Feature Element Breakdown` must feed the owning `Element Validation Ledger`', 'created, touched, affected, deferred, future, dependency-only, and non-gating supporting elements', '`Element Ledger Placement Drift`', '`Created Element Untracked`', '`Touched Element Proof Missing`', '`Affected Element Validation Missing`'), Path('Docs/codex_modes.md'): ('`Source-Truth Placement Preflight`', '`Element Validation Ledger Owner`', 'run `Element Delta Capture`', 'create a parallel active source-truth artifact for element tracking'), Path('Docs/orin_task_template.md'): ('Source-Truth Placement Preflight:', 'Element Validation Ledger Owner:', 'Element Delta Capture:', '`Element Validation Ledger` is row-level created/touched/affected/deferred/future element proof tracking'), Path('Docs/codex_user_guide.md'): ('run `Source-Truth Placement Preflight`', 'owning `Element Validation Ledger`', 'Element Validation Ledger rows belong in the existing authority owner by default', 'Do not prompt Codex to create a parallel active ledger unless the owning record records `No Existing Owner Fits`')}

FAM006_ELEMENT_VALIDATION_LEDGER_REQUIRED_PHRASES = (
    "## Element Validation Ledger Governance",
    "Source-Truth Placement Preflight: `PASS - existing authority owner fits",
    "Existing Authority Owner: `Docs/branch_records/feature_fam_006_monitoring_hud_product_surface.md`",
    "Placement Decision: `Extend existing branch authority record first`",
    "No Existing Owner Fits: `Not claimed`",
    "Companion File Rule: `Active - completed FAM-006 ledger rows live in Docs/branch_records/feature_fam_006_monitoring_hud_product_surface_element_ledger.md",
    "Canonical Companion Ledger: `Docs/branch_records/feature_fam_006_monitoring_hud_product_surface_element_ledger.md`",
    "Element Delta Capture Rule:",
    "High-Risk Source Owner Marker Posture:",
    "Future Repo-Wide Marker Adoption Recommendation:",
    "## Element Validation Ledger",
    "Ledger Backfill Status: `Backfilled",
    "LV2 Gate: `Complete by explicit USER waiver",
    "FAM006-DASH-SURFACE-001",
    "FAM006-DASH-WINDOW-002",
    "FAM006-DASH-SCROLL-003",
    "FAM006-DASH-CONTENT-004",
    "FAM006-DASH-PROVIDER-005",
    "FAM006-DASH-WARNING-006",
    "FAM006-PROOF-LV-007",
    "FAM006-OVERLAY-DEFER-008",
    "FAM006-CORE-DEP-009",
    "FAM006-SRCMARK-FUTURE-010",
    "Source-owner-not-applicable until future marker adoption",
    "Returned USER Issue Register",
    "FAM006-RUI-039",
    "FAM006-RUI-040",
    "FAM006-RUI-041",
    "FAM006-RUI-042",
    "FAM006-RUI-043",
    "FAM006-RUI-044",
    "FAM006-RUI-045",
    "FAM006-RUI-046",
    "FAM006-RUI-047",
    "actual desktop shortcut",
    "Codex Precheck",
)

FAM006_ELEMENT_LEDGER_REQUIRED_PHRASES = (
    "# FAM-006 Element Validation Ledger",
    "Owner Record: `Docs/branch_records/feature_fam_006_monitoring_hud_product_surface.md`",
    "Ledger Status:",
    "Live Validation LV2 Green",
    "Current Gate:",
    "H1 pressure-tested",
    "USER WAIVED/PASSABLE",
    "Prior Gate Superseded: `Returned refreshed User Test Summary results required before LV2 returned User Test Summary digestion`",
    "LV2 returned User Test Summary digestion did not proceed from Codex proof alone",
    "Branch Readiness Stage 1 revalidation passed",
    "Historical superseded finding: `No Hardening rerun is required by the ledger closeout alone`",
    "## Dashboard-First Elements",
    "FAM006-DASH-SURFACE-001",
    "FAM006-DASH-WINDOW-002",
    "FAM006-DASH-MOVE-003",
    "FAM006-DASH-CLIP-004",
    "FAM006-DASH-LAYOUT-005",
    "FAM006-DASH-VISUAL-006",
    "FAM006-DASH-SCROLL-007",
    "FAM006-DASH-CONTENT-008",
    "FAM006-DASH-MONITOR-GROUP-009",
    "FAM006-DASH-MONITOR-ENABLE-010",
    "FAM006-DASH-MONITOR-POLLING-011",
    "FAM006-DASH-AFFORDANCE-COPY-012",
    "FAM006-DASH-STATE-PERSIST-013",
    "FAM006-DASH-NO-KEYBIND-014",
    "FAM006-DASH-PROVIDER-015",
    "FAM006-DASH-NOFAKE-016",
    "FAM006-DASH-WARNING-017",
    "## Dashboard USER Feedback Repair Rows",
    "FAM006-DASH-STARTUP-045",
    "FAM006-HUD-FEATURE-TRAY-046",
    "FAM006-DASH-FOCUS-047",
    "FAM006-NCP-REGRESSION-048",
    "FAM006-DASH-CHILD-WINDOW-049",
    "FAM006-DEV-INTERFACE-REVIEW-050",
    "## Returned LV1 Feedback #20-#38 Disposition Overlay",
    "FAM006-HUD-TRAY-FLASH-051",
    "FAM006-HUD-TRAY-STATE-LOCK-052",
    "FAM006-DASH-TRAY-OPEN-CLOSE-053",
    "FAM006-HUD-DISABLE-UNUSABLE-054",
    "FAM006-TRAY-SHUTDOWN-CONFIRM-055",
    "FAM006-DASH-FRAME-HAZE-056",
    "FAM006-DASH-RESIZE-057",
    "FAM006-DASH-DEADZONE-058",
    "FAM006-DASH-STICKY-OCCLUSION-059",
    "FAM006-DASH-QUICK-ACCESS-060",
    "FAM006-DASH-DEFERRED-BUTTON-061",
    "FAM006-DASH-HUD-OVERLAY-COPY-062",
    "## Deferred Overlay / Minimal HUD Elements",
    "FAM006-OVERLAY-DEFER-018",
    "FAM006-OVERLAY-MINIMAL-019",
    "FAM006-OVERLAY-DISPLAY-020",
    "FAM006-OVERLAY-CANVAS-021",
    "FAM006-OVERLAY-ANCHOR-022",
    "FAM006-OVERLAY-MONITOR-CARDS-023",
    "FAM006-OVERLAY-POSITION-024",
    "## Core Dependency Elements",
    "FAM006-CORE-DEP-025",
    "FAM006-CORE-PRESET-026",
    "FAM006-CORE-NONMOVABLE-027",
    "FAM006-CORE-WORKERW-028",
    "FAM006-CORE-TRANSPARENCY-029",
    "FAM006-CORE-ISOLATION-030",
    "## Proof, Validation, And Governance Elements",
    "FAM006-PROOF-STATIC-031",
    "FAM006-PROOF-SANDBOX-032",
    "FAM006-PROOF-LIVEHELPER-033",
    "FAM006-PROOF-SCREENSHOT-034",
    "FAM006-PROOF-INTERACTION-035",
    "FAM006-PROOF-UTS-EXPORT-036",
    "FAM006-PROOF-UTS-DIGEST-037",
    "FAM006-PROOF-NAMING-038",
    "FAM006-GOV-SOURCE-TRUTH-039",
    "FAM006-GOV-SRCMARK-040",
    "FAM006-GOV-REAL-CLIENT-PROOF-063",
    "FAM006-GOV-RUI-REGISTER-064",
    "FAM006-GOV-HUMAN-CLIENT-065",
    "FAM006-GOV-UI-ISSUE-DISCOVERY-066",
    "FAM006-TRAY-ACTION-ORDER-067",
    "FAM006-DASH-NCP-MOUSE-068",
    "FAM006-TRAY-AUTHORING-DIALOG-GUARD-069",
    "FAM006-TRAY-EXIT-PROMPT-VISUAL-070",
    "FAM006-FUTURE-PROVIDER-041",
    "FAM006-FUTURE-EXTERNAL-042",
    "FAM006-FUTURE-AUDIO-043",
    "FAM006-FUTURE-PERSONA-044",
    "## UTS Coverage Map",
    "Current Coverage Status: `Released historical traceability - RUI-001 through RUI-057 remain issue-grounded; the actual desktop shortcut targeted the FAM-006 worktree for final proof; WS56 resize/cursor/fluidity rows were revalidated; current LV1 handoff was refreshed; LV2 digested explicit USER waiver/passable acceptance; PR #118 merged; PR #119 repaired pre-release canon drift; v1.7.0-prebeta published the package; later issue-thread creation requires separate USER approval`",
    "## Proof Rebaseline Summary",
    "Returned Step 2 Tray enable/disable/open Dashboard",
    "Returned Step 3 Tray Exit NDAI",
    "Codex Precheck",
    "Marker-only proof remains supporting only",
)

SOURCE_OWNER_MARKER_ADOPTION_NEXT_BRANCH_REQUIRED_PHRASES = {
    FAM006_BRANCH_RECORD: (
        "Post-FAM-006 Required Marker Adoption Candidate:",
        "Repo-Wide High-Risk Source Owner Marker Adoption",
        "feature/repo-wide-source-owner-marker-adoption",
        "required post-FAM-006 governance/package candidate",
        "Branch creation and package admission remain blocked until the appropriate later readiness path",
        "Dev Toolkit Interface Review Mode adoption is included and tabled",
        "NCP, Core visualization, Dashboard, Overlay/display when admitted",
        "Ledger remains canonical; markers and review badges are backlinks/inspection aids only",
    ),
    Path("Docs/prebeta_roadmap.md"): (
        "required post-FAM-006 governance/package candidate:",
        "Repo-Wide High-Risk Source Owner Marker Adoption",
        "feature/repo-wide-source-owner-marker-adoption",
        "does not create/admit the branch",
        "plan Dev Toolkit Interface Review Mode dispositions for existing and future USER-facing elements",
        "NCP, Core visualization, Dashboard, Overlay/display when admitted",
        "while preserving the ledger as canonical and markers/review badges as dev-only backlinks or inspection aids only",
        "The Dev Toolkit design is tabled for that future pass",
    ),
    Path("Docs/feature_backlog.md"): (
        "Post-FAM-006 Required Governance/Package Candidate:",
        "Repo-Wide High-Risk Source Owner Marker Adoption",
        "feature/repo-wide-source-owner-marker-adoption",
        "not as an active selected-next implementation branch or newly admitted package",
        "Later readiness must decide the legal carrier",
        "plan repo-wide Dev Toolkit Interface Review Mode dispositions for existing and future USER-facing elements",
        "The Dev Toolkit design is tabled for that future pass",
    ),
}
FAM006_REAL_CLIENT_PROOF_GOVERNANCE_REQUIRED_PHRASES = {
    Path("Docs/user_test_summary_guidance.md"): (
        "actual desktop shortcut path is mandatory when feasible",
        "Static proof, sandbox proof, fake/offscreen model proof, callback-only proof, active-client screenshot proof, and real user-operated tray proof are separate proof classes",
        "per-step precheck manifest",
        "Codex Precheck: NOT TESTED",
        "Fake windows, hidden clients, direct callbacks, and offscreen model assertions can support implementation confidence but cannot be recorded as the sole PASS",
        "app-side precheck code that calls tray handlers directly is not a human-client pass",
        "human-client manifest",
    ),
    Path("Docs/validation_helper_registry.md"): (
        "actual desktop shortcut equivalence proof",
        "real user-operated tray action proof",
        "per-step Codex precheck manifest support",
        "Fake/callback/offscreen proof must be labeled separately from real-client proof",
        "real-client proof-class separation",
        "per-step Codex Precheck PASS/FAIL/NOT TESTED/WAIVED output",
        "dev/orin_monitoring_hud_human_client_validation.ps1",
        "human-client manifest is PASS",
    ),
}

SUCCESSOR_LOCK_WAIVER_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'),)

SUCCESSOR_LOCK_WAIVER_PHRASE = "no USER-approved selected-next truth exists"

NO_ACTIVE_BRANCH_STEADY_STATE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

NO_ACTIVE_BRANCH_STEADY_STATE_PHRASE = "steady-state `No Active Branch`"

DOCS_GOVERNANCE_ADMISSION_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_user_guide.md'),)

GOVERNANCE_ONLY_BLOCK_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/closeout_guidance.md'),)

GOVERNANCE_ONLY_BLOCK_PHRASES = (
    "governance-only branch",
    "between-branch",
)

STANDING_GOVERNANCE_INTAKE_BRANCH = "feature/release-readiness-source-truth-intake"
STANDING_GOVERNANCE_INTAKE_BRANCH_CLASS = "standing governance intake"
STANDING_GOVERNANCE_INTAKE_RECORD = Path(
    "Docs/branch_records/feature_release_readiness_source_truth_intake.md"
)
STANDING_GOVERNANCE_INTAKE_RECORD_PATH = STANDING_GOVERNANCE_INTAKE_RECORD.as_posix()
STANDING_GOVERNANCE_INTAKE_EXTERNAL_STATE_POINTER = str(
    EXTERNAL_STATE_ROOT / "branches" / "feature_release_readiness_source_truth_intake" / "branch_state.md"
)
STANDING_GOVERNANCE_INTAKE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'),)
STANDING_GOVERNANCE_INTAKE_PHRASES = (
    "Standing Governance Intake Branch",
    "feature/release-readiness-source-truth-intake",
    "Release Readiness digest",
    "automation/worktree governance intake",
    "phase-gate governance intake",
    "Waiting For Governance Intake",
    "Return Digest",
    "Neutral Main Workspace Rebaseline",
    "Pre-Rebaseline Impact Audit",
    "RRI-YYYYMMDD-NNN",
    "One Active Cycle",
    "Sync Rule",
)
GOVERNANCE_INTAKE_DIGEST_STANDARD_DOC = Path(
    "Docs/governance_intake_triage_and_digest_profiles.md"
)
GOVERNANCE_INTAKE_DIGEST_POINTER_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'), Path('Docs/governance_process_efficiency_reform_plan.md'),)
GOVERNANCE_INTAKE_DIGEST_POINTER_PHRASES = (
    "Governance Intake Triage Packet",
    "Digest Profile",
)
GOVERNANCE_INTAKE_DIGEST_STANDARD_PHRASES = ()
WORKTREE_REBASELINE_AUDIT_HELPER = Path("dev/orin_worktree_rebaseline_audit.py")
WORKTREE_REBASELINE_AUDIT_DOCS = (
    Path("Docs/validation_helper_registry.md"),
    Path("Docs/governance_process_efficiency_reform_plan.md"),
    Path("Docs/branch_records/feature_release_readiness_source_truth_intake.md"),
)
WORKTREE_REBASELINE_AUDIT_PHRASES = (
    "dev/orin_worktree_rebaseline_audit.py",
    "report-only",
    "Pre-Rebaseline Impact Audit",
    "Current-Main Reconciliation Identity Guard",
    "Rebaseline Mutation Approval",
    "Rebaseline Mutation Status",
)
WORKTREE_REBASELINE_AUDIT_SOURCE_PHRASES = (
    "report-only",
    "Pre-Rebaseline Impact Audit:",
    "Current-Main Reconciliation Identity Guard:",
    "Recommendation Only:",
    "Rebaseline Mutation Approval:",
    "Rebaseline Mutation Status:",
    "no fetch, merge, rebase, checkout, reset, or file mutation",
    'f"{merge_base}..{target_ref}"',
    'branch_match.group(1).strip() == branch',
)
VALIDATION_SUITE_HELPER = Path("dev/orin_validation_suite.py")
VALIDATION_SUITE_DOCS = (
    Path("Docs/validation_helper_registry.md"),
    Path("Docs/governance_process_efficiency_reform_plan.md"),
    Path("Docs/branch_records/feature_release_readiness_source_truth_intake.md"),
)
VALIDATION_SUITE_PHRASES = (
    "dev/orin_validation_suite.py",
    "report-only",
    "Recommended Validation Suite:",
    "--phase",
    "--changed-file",
    "does not execute",
)
VALIDATION_SUITE_SOURCE_PHRASES = (
    "Recommended Validation Suite:",
    "report-only - helper recommends commands but does not execute them",
    "--phase",
    "--changed-file",
    "git diff",
    "rationale",
)
GOVERNANCE_EFFICIENCY_OPERATING_MODEL = Path(
    "Docs/governance_efficiency_operating_model.md"
)
GOVERNANCE_EFFICIENCY_VALIDATION_HELPER = Path(
    "dev/orin_governance_efficiency_validation.py"
)
GOVERNANCE_EFFICIENCY_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/validation_helper_registry.md'), Path('Docs/governance_process_efficiency_reform_plan.md'), Path('Docs/branch_records/index.md'), Path('Docs/branch_records/feature_release_readiness_source_truth_intake.md'),)
GOVERNANCE_EFFICIENCY_OPERATING_MODEL_PHRASES = (
    "Rule ID And Owner Model",
    "Source-Truth Ownership Matrix",
    "Docs Source-Truth Reform Model",
    "Derived Live Truth Versus Historical Receipt",
    "Duplicate Live-State Guard",
    "Current Summary And Historical Appendix Split",
    "Phase Alias UX",
    "Branch Planning UX Standard",
    "Standing Governance Ledger Compaction",
    "Release Ownership UX",
    "Public Language Mapping",
    "Validator Modularization Boundary",
    "Validation Runner And Registry Query Rule",
    "Naming Drift Scan Rule",
    "Reform Pass Completion Model",
)
GOVERNANCE_EFFICIENCY_POINTER_PHRASES = (
    "Docs/governance_efficiency_operating_model.md",
    "governance efficiency",
)
GOVERNANCE_EFFICIENCY_SOURCE_PHRASES = (
    "governance efficiency validation",
    "REQUIRED_MODEL_PHRASES",
    "POINTER_REQUIREMENTS",
    "BACKLOG_ROADMAP_COMPACTNESS_FORBIDDEN",
    "report-only",
)
DOCS_SOURCE_TRUTH_REFORM_MARKER = "Docs Source-Truth Reform Model: Compact Pointer Layer"
POINTER_ONLY_FORBIDDEN_MARKERS = (
    "Package Trace:",
    "Slice Trace:",
    "Latest Public Prerelease Recorded In Source Truth:",
    "Latest Public Prerelease:",
    "Latest Public Release Commit:",
    "Latest Public Prerelease Publication:",
    "Merged-Unreleased PRs:",
)
COMPACT_BACKLOG_REQUIRED_FIELDS = (
    "Status",
    "Record State",
    "Registry Class",
    "Family Anchor",
    "Priority",
    "Family Scope",
    "Package Summary",
    "Package Admission State",
    "Admitted Slice Count",
    "Package Completion State",
    "Single-Slice Package User Approval",
    "Canonical Detail Owner",
)
CURRENT_DECISION_SURFACE_DOCS = (
    Path("Docs/feature_backlog.md"),
    Path("Docs/prebeta_roadmap.md"),
)
CURRENT_DECISION_SURFACE_PHRASES = (
    "## Current Decision Surface",
    "Latest Public Prerelease Recorded In Source Truth:",
    "Published Release Pending Canon Closure:",
    "Merged-Unreleased PRs:",
    "Active Runtime Branch:",
    "Active Governance Branch:",
    "Selected-Next Posture:",
    "Release Blockers:",
    "Next Legal Phase:",
)
CURRENT_DECISION_SURFACE_POINTER_DOCS = (
    Path("Docs/governance_process_efficiency_reform_plan.md"),
    Path("Docs/branch_records/feature_release_readiness_source_truth_intake.md"),
)
STANDING_GOVERNANCE_INTAKE_ALLOWED_DEV_FILES = {
    "dev/orin_branch_governance_validation.py",
    "dev/orin_branch_readiness_planning_fixture_validation.py",
    "dev/orin_pr_review_churn_validation.py",
    "dev/orin_rar_issue_candidate_durability_validation.py",
    "dev/orin_worktree_rebaseline_audit.py",
    "dev/orin_validation_suite.py",
    "dev/orin_user_review_bundle.py",
    "dev/orin_governance_efficiency_validation.py",
    "dev/orin_docs_inventory_reform_audit.py",
    "dev/orin_external_state_common.py",
    "dev/orin_external_state_init.py",
    "dev/orin_external_state_lock.py",
    "dev/orin_external_state_promote.py",
    "dev/orin_external_state_promote_preview.py",
    "dev/orin_external_state_report.py",
    "dev/orin_external_state_snapshot.py",
    "dev/orin_external_state_validation.py",
    "dev/orin_external_state_lock_release.py",
    "dev/orin_external_state_target_reconcile.py",
    "dev/orin_external_state_target_currentness_fixture_validation.py",
    "dev/orin_user_review_bundle_false_green_fixture_validation.py",
    "dev/orin_repo_live_state_leakage_scan.py",
    "dev/orin_state_fold_down_preview.py",
    "dev/automation_observability_report.py",
    "dev/orin_ai_provider_state_validation.py",
    "dev/orin_monitoring_hud_internal_sandbox_validation.py",
    "dev/orin_monitoring_hud_surface_validation.py",
    "dev/orin_pr_body_quality_audit.py",
    "dev/orin_public_leak_prevention_validation.py",
    "dev/orin_release_body_validation.py",
}
STANDING_GOVERNANCE_INTAKE_CONTRACT_MARKERS = (
    "Standing Branch",
    "Worktree",
    "Intake Source",
    "Cycle ID Format",
    "Active RRI Cycle",
    "One Active Cycle",
    "Sync Rule",
    "Pre-Rebaseline Impact Audit",
    "Bootstrap Exception Limit",
    "Return Digest",
    "Originating Lane Pause",
)
STANDING_GOVERNANCE_INTAKE_RETURN_DIGEST_MARKERS = (
    "Originating Branch",
    "Originating Worktree",
    "Operating Workspace",
    "Expected Branch",
    "RRI Cycle ID",
    "Governance PR",
    "Merge Commit",
    "Updated origin/main",
    "Neutral Main Workspace Rebaseline",
    "Pre-Rebaseline Impact Audit",
    "Files Changed",
    "Blockers Cleared",
    "Blockers Remaining",
    "Validations",
    "Rebaseline Instructions",
    "Next Legal Phase",
)


def _is_standing_governance_intake_branch(branch_name: str) -> bool:
    return branch_name == STANDING_GOVERNANCE_INTAKE_BRANCH
STANDING_GOVERNANCE_RETURN_DIGEST_IDENTITY_GUARD_MARKERS = (
    "Originating Branch Source",
    "Originating Worktree Source",
    "Operating Workspace Requirement",
    "Default Workspace Ban",
    "Return Digest Origin Identity Missing",
    "Thread / Worktree Identity Mismatch",
)

ASSIGNED_WORKTREE_CONFINEMENT_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'),)
ASSIGNED_WORKTREE_CONFINEMENT_PHRASES = (
    "Assigned Worktree Confinement",
    "Active Thread Owner",
    "Thread Assignment Status",
    "Worktree Ownership Ledger",
    "Intended Write Set",
    "Same Worktree / Same Branch Collision Check",
    "Dirty Worktree Collision Check",
    "Dirty Worktree Recovery Packet",
    "Off-Worktree Work Routing",
    "Governance Routing Barrier",
    "New Worktree Decision Gate",
    "Worktree Escape User Waiver: Granted",
    "Worktree Escape User Waiver Missing",
    "Prompt-Ingress Lane Lock",
    "Prompt-Ingress Lane Mismatch",
    "Expected Worktree Root:",
    "Actual Worktree Root:",
    "No Cross-Worktree Mutation",
    "GitHub Desktop-bound worktree",
)
ASSIGNED_WORKTREE_CONFINEMENT_RECORD_MARKERS = (
    "Assigned Worktree Confinement",
    "Active Thread Owner",
    "Thread Assignment Status",
    "Worktree Ownership Ledger",
    "Intended Write Set",
    "Same Worktree / Same Branch Collision Check",
    "Dirty Worktree Collision Check",
    "Dirty Worktree Recovery Packet",
    "Off-Worktree Work Routing",
    "Governance Routing Barrier",
    "New Worktree Decision Gate",
    "Expected Worktree Root",
    "Actual Worktree Root",
    "No Cross-Worktree Mutation",
    "GitHub Desktop-bound worktree",
    "Worktree Escape User Waiver",
    "Worktree Escape User Waiver Missing",
)

FAMILY_SCOPED_BRANCH_READINESS_DOCS = (Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'),)
FAMILY_SCOPED_BRANCH_READINESS_PHRASES = (
    "Family-Scoped Branch Readiness Confinement",
    "Target Family",
    "Sibling Worktree Candidate Exclusion",
    "Sibling worktrees are overlap context only",
    "not successor authority",
)

MULTI_SEAM_CONTRACT_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

MULTI_SEAM_CONTRACT_PHRASES = ()

BRANCH_SLICE_SLC_SEAM_TERMINOLOGY_REQUIRED_PHRASES = {Path('Docs/branch_plans/README.md'): ('`Slice` is the canonical package deliverable unit.', '`SLC` is the current branch-planning alias', 'Multi-slice branches are legal', 'Every Slice/SLC must trace'), Path('Docs/workstreams/index.md'): ('SLC is the current branch-planning alias', 'a seam is the current execution checkpoint'), Path('Docs/feature_backlog.md'): ('`SLC` = branch-planning alias', '`Seam` = execution or validation checkpoint'), Path('Docs/validation_helper_registry.md'): ('invalid SLC/Slice/Seam terminology ambiguity packet', 'valid multi-slice implementation carrier', 'SLC treated as a seam')}

MULTI_SEAM_PRIMARY_REPAIR_PHRASES = (
    "Category labels are not stop conditions by themselves.",
    "Legacy `Single-Seam Fallback` and `Single-Seam Mode Waiver` terms are retired and must not be used in active source-of-truth.",
    "A bounded stop condition blocks the workflow. It does not by itself authorize splitting the backlog item across branches.",
    "Stopping after the first slice or splitting the backlog item across branches requires an explicit `Backlog-Split User Approval` or a named bounded stop condition.",
    "Bounded means one active seam at a time, not one-seam Workstream authority.",
    "A single-seam Workstream requires explicit USER waiver before Workstream may stop after one seam while the package or slice remains incomplete.",
    "Single-seam or single-slice Workstream authority is forbidden unless explicit USER waiver text is recorded.",
    "If only one seam or one slice is planned or visible, stop immediately on `Single-Seam Or Single-Slice Workstream Blocker` until Branch Readiness expands the plan or USER grants a waiver.",
    "Only USER can grant a single-seam or single-slice Workstream waiver; Codex, ChatGPT, validators, prompt wording, clean validation, or a green seam cannot infer it.",
    "A Workstream with `Completion Status: In Progress` and no waiver must show remaining same-branch implementable work beyond the current seam.",
    "when a slice turns green during `Workstream`, advance immediately to the next admitted slice while `Completion Status` remains `In Progress`",
    "`Completion Status: Red` means a named blocker or waiver currently stops bounded Workstream continuation",
)

MANDATORY_BOUNDED_STATE_REQUIRED_PHRASES = {Path('Docs/development_rules.md'): ('Bounded State is mandatory before execution', 'Bounded State Missing', 'Bounded State User Waiver: Granted', 'Bounded State Waiver Missing', 'Broad work requests do not authorize implementation', 'Clean validation, clean git state, branch existence, prior broad approval, prompt wording, Codex discretion, or ChatGPT review cannot infer a bounded-state waiver'), Path('Docs/codex_modes.md'): ('Workflow mode is legal only inside a proven `Bounded State:` unless USER grants an explicit bounded-state waiver', 'Bounded State Missing', 'Bounded State User Waiver: Granted', 'Bounded State Waiver Missing', 'Broad work requests do not authorize implementation', 'Clean validation, branch existence, prompt wording, Codex discretion, or ChatGPT wording cannot infer a waiver'), Path('Docs/branch_records/index.md'): ('Bounded State Missing', 'Bounded State User Waiver: Granted', 'Bounded State Waiver Missing', 'broad work requests do not authorize implementation', 'clean validation, branch existence, prompt wording, Codex discretion, or ChatGPT wording cannot infer a bounded-state waiver'), Path('Docs/orin_task_template.md'): ('Bounded State:', 'Bounded State User Waiver:', 'Bounded State Missing', 'Bounded State Waiver Missing', 'Broad work requests do not authorize implementation'), Path('Docs/codex_user_guide.md'): ('Bounded State:', 'Bounded State User Waiver:', 'Bounded State Missing', 'Bounded State Waiver Missing', 'Broad work requests do not authorize implementation')}

FAM007_BOUNDED_STATE_RECORD_REQUIRED_PHRASES = (
    "## Bounded State Lock",
    "Bounded State: `Complete - PR Readiness Stage 1 / feature/fam-007-provider-boundary-no-provider-shell / PKG-007 / all admitted branch-material seams SLC-017, SLC-018, SLC-031, SLC-032, SLC-033, SLC-034, SLC-035, and SLC-036 green, H1 proof reviewed, UTS applicability waived, LV1 green, PR-readiness scope validated, and next legal phase PR Readiness Stage 2 only`",
    "Bounded State User Waiver: Granted",
    "Bounded State Waiver Scope: `USER explicitly approved executing all relevant same-branch bounded Workstream tasks for all remaining admitted branch-material seams before Hardening",
    "Hardening H1 USER Approval: `Granted - USER approved Hardening H1 proof review",
    "Current Hardening Seam: `Hardening H1 - FAM-007 Provider Boundary And No-Provider Shell Local-Only Scaffold Chain`",
    "Current Hardening Seam Status: `Green - H1 proof review found no runtime defect repair required`",
    "Live Validation LV1 USER Approval: `Granted - USER approved Live Validation LV1",
    "Current Live Validation Seam: `Live Validation LV1 - FAM-007 Provider Boundary And No-Provider Shell Applicability And No-Provider Surface Proof`",
    "Current Live Validation Seam Status: `Green - LV1 classifies formal UTS, screenshot, shortcut, and live-client self-QA as waived",
    "User Test Summary Results: `WAIVED`",
    "Codex Live Client Self-QA: `WAIVED`",
    "PR Readiness Stage 1 USER Approval: `Granted",
    "PR Readiness Execution User Approval Missing",
    "Broad Work Request Handling:",
    "Bounded State Missing Stop:",
    "Bounded State Waiver Missing Stop:",
    "Clean validation, branch existence, prompt wording, Codex discretion, or ChatGPT wording cannot infer a waiver",
)

INTERFACE_RELEASE_BOUNDARY_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

INTERFACE_RELEASE_BOUNDARY_PHRASES = (
    "Interface Release Boundary",
    "Primary Interface Release Surface:",
    "Interface Bundle User Approval",
    "Multiple Interface Release Drift",
    "Branch Readiness Interface Planning Incomplete",
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
    "use `single-seam mode waiver` only when",
    "single-seam workstream by default",
    "stop after one seam by default",
    "bounded seam is a terminal boundary",
    "bounded means single seam",
    "bounded means one seam",
    "one-seam workflow",
    "approved seam sequence",
    "approved sequence",
    "next planned seam",
    "additional slices needed to finish the backlog item on the current branch",
    "additional slices needed to complete the backlog item on the same branch",
    "starting the next seam in the approved sequence",
    "Once the current slice is green, report green status and await the next instruction instead of auto-starting a new slice or later phase.",
)

MULTI_SEAM_PROMPT_DOCS = (Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

MULTI_SEAM_PROMPT_PHRASES = ()

REUSABLE_GUIDANCE_RETIRED_SEAM_TERMS = {
    Path("Docs/incident_patterns.md"): (
        "Single-Seam Fallback",
        "Single-Seam Mode Waiver",
    ),
}

REQUIRED_WORKSTREAM_CONTINUATION_MARKERS = (
    "Seam Status:",
    "Slice Status:",
    "Completion Status:",
    "Waiver Status:",
    "Continue Decision:",
    "Continuation Execution Latch:",
    "Stop Basis:",
    "Next Active Seam:",
    "Stop Condition:",
    "Continuation Action:",
)

CONTINUATION_SEAM_STATUS_LABEL = "Seam Status"
CONTINUATION_SLICE_STATUS_LABEL = "Slice Status"
CONTINUATION_COMPLETION_STATUS_LABEL = "Completion Status"
CONTINUATION_WAIVER_STATUS_LABEL = "Waiver Status"
CONTINUATION_EXECUTION_LATCH_LABEL = "Continuation Execution Latch"
CONTINUATION_STOP_BASIS_LABEL = "Stop Basis"
SINGLE_SEAM_WORKSTREAM_WAIVER_LABEL = "Single-Seam Workstream Waiver"
SINGLE_SEAM_OR_SINGLE_SLICE_WAIVER_AUTHORITY_LABEL = (
    "Single-Seam Or Single-Slice Waiver Authority"
)
SINGLE_SEAM_OR_SINGLE_SLICE_WORKSTREAM_BLOCKER_LABEL = (
    "Single-Seam Or Single-Slice Workstream Blocker"
)
BOUNDED_SEAM_DEFAULT_LABEL = "Bounded Seam Default"
CONTINUATION_ALLOWED_SEAM_STATUSES = {"green", "in progress", "blocked"}
CONTINUATION_ALLOWED_SLICE_STATUSES = {"green", "in progress", "blocked", "waived"}
CONTINUATION_ALLOWED_COMPLETION_STATUSES = {"green", "in progress", "red"}
CONTINUATION_ALLOWED_WAIVER_STATUSES = {"none", "approved", "required"}
CONTINUATION_ALLOWED_DECISIONS = {"continue", "stop"}
CONTINUATION_ALLOWED_STOP_BASES = {"none", "workstream green", "named blocker", "waiver"}
SINGLE_SEAM_WORKSTREAM_ALLOWED_NO_WAIVER_VALUES = {"none", "not required", "not granted"}
SINGLE_SEAM_WORKSTREAM_PROHIBITED_ACTIVE_PHRASES = (
    "single-seam workstream by default",
    "stop after one seam by default",
    "bounded seam is a terminal boundary",
    "bounded means single seam",
    "bounded means one seam",
)

GOVERNED_OUTPUT_CONTRACT_REQUIRED_PHRASES = {Path('Docs/development_rules.md'): ('Seam Status', 'Slice Status', 'Completion Status', 'Waiver Status', 'Continue Decision', 'Continuation Execution Latch', 'Stop Basis', 'Every phase digest must include `Next Legal Phase` as its own output field, even when `Continue Decision: Continue`; `Next Safe Move` may remain lawful-stop or route-specific and must not replace required continuation.', 'If `Completion Status` is `In Progress` and no named blocker or waiver stops work, Codex must continue rather than returning `Await Next Instruction`.', 'Use these governed state markers as execution control, not just reporting.', 'If `Continue Decision` is `Continue`, do not end on a seam-complete final response, rollback path, or next-seam recommendation; keep executing until a lawful `Stop` decision exists.', 'A prompt `Return:` block is an output shape only; it cannot override governed continuation markers or authorize a terminal response while `Continue Decision` remains `Continue`.', 'A final response after a green seam while `Continue Decision` remains `Continue` is `Post-Seam Final-Stop Drift`.', 'Durability commit/push is not a lawful stop while `Continue Decision` remains `Continue`.', 'Before any final response during `Workstream`, Codex must run a `Post-Seam Continuation Self-Audit` against the governed markers it just wrote or validated.', 'If `Completion Status: In Progress` and `Continue Decision: Continue`, the self-audit result must be `Continue Same Workstream` and Codex must start the next active Workstream seam in the same bounded run.', 'If Codex cannot start the next seam after that self-audit, it must record `Completion Status: Red` with the exact named blocker or USER waiver needed; it must not return a green seam closeout as terminal.', 'If `Completion Status` is `In Progress`, `Next Active Seam` must remain a `Workstream` seam; phase-exit seams require `Completion Status: Green`, `Completion Status: Red` with a named blocker/waiver, or explicit USER single-seam/backlog-split waiver.', '`Phase: Workstream` must remain bounded at all times, and the only lawful `Workstream` stop conditions are `Completion Status: Green` with `Hardening` next, or `Completion Status: Red` justified by a named blocker or waiver.', 'Single-seam or single-slice Workstream authority is forbidden unless explicit USER waiver text is recorded.', 'If only one seam or one slice is planned or visible, stop immediately on `Single-Seam Or Single-Slice Workstream Blocker` until Branch Readiness expands the plan or USER grants a waiver.', 'Only USER can grant a single-seam or single-slice Workstream waiver; Codex, ChatGPT, validators, prompt wording, clean validation, or a green seam cannot infer it.', 'A Workstream with `Completion Status: In Progress` and no waiver must show remaining same-branch implementable work beyond the current seam.', 'If `Completion Status` is `Red`, `Continuation Action` must report the blocker-clearing action or waiver-clearing action needed before bounded `Workstream` continuation may resume.'), Path('Docs/codex_modes.md'): ('Seam Status', 'Slice Status', 'Completion Status', 'Waiver Status', 'Continue Decision', 'Continuation Execution Latch', 'Stop Basis', 'Every phase digest must include `Next Legal Phase` as its own output field, even when `Continue Decision: Continue`; `Next Safe Move` may remain lawful-stop or route-specific and must not replace required continuation.', 'If `Completion Status` is `In Progress` and no named blocker or waiver stops work, Workflow mode must continue rather than returning `Await Next Instruction`.', 'Use these governed state markers as execution control, not just reporting.', 'If `Continue Decision` is `Continue`, Workflow mode must not end on a seam-complete final response, rollback path, or next-seam recommendation; it must keep executing until a lawful `Stop` decision exists.', 'A prompt `Return:` block is an output shape only; it cannot override governed continuation markers or authorize a terminal response while `Continue Decision` remains `Continue`.', 'A final response after a green seam while `Continue Decision` remains `Continue` is `Post-Seam Final-Stop Drift`.', 'Durability commit/push is not a lawful stop while `Continue Decision` remains `Continue`.', 'Before any final response during `Workstream`, Codex must run a `Post-Seam Continuation Self-Audit`', 'if `Completion Status: In Progress` and `Continue Decision: Continue`, the self-audit result must be `Continue Same Workstream`', 'it must record `Completion Status: Red` with the exact named blocker or USER waiver needed instead of returning a green seam closeout as terminal', 'If `Completion Status` is `In Progress`, `Next Active Seam` must remain a `Workstream` seam; phase-exit seams require `Completion Status: Green`, `Completion Status: Red` with a named blocker/waiver, or explicit USER single-seam/backlog-split waiver.', '`Phase: Workstream` must remain bounded at all times, and the only lawful `Workstream` stop conditions are `Completion Status: Green` with `Hardening` next, or `Completion Status: Red` justified by a named blocker or waiver.', 'Single-seam or single-slice Workstream authority is forbidden unless explicit USER waiver text is recorded.', 'If only one seam or one slice is planned or visible, stop immediately on `Single-Seam Or Single-Slice Workstream Blocker` until Branch Readiness expands the plan or USER grants a waiver.', 'Only USER can grant a single-seam or single-slice Workstream waiver; Codex, ChatGPT, validators, prompt wording, clean validation, or a green seam cannot infer it.', 'A Workstream with `Completion Status: In Progress` and no waiver must show remaining same-branch implementable work beyond the current seam.', 'If `Completion Status` is `Red`, `Continuation Action` must report the blocker-clearing action or waiver-clearing action needed before bounded `Workstream` continuation may resume.'), Path('Docs/codex_user_guide.md'): ('Seam Status:', 'Slice Status:', 'Completion Status:', 'Waiver Status:', 'Continue Decision:', 'Continuation Execution Latch:', 'Stop Basis:', 'Every phase digest must include `Next Legal Phase` as its own output field, even when `Continue Decision: Continue`; `Next Safe Move` may remain lawful-stop or route-specific and must not replace required continuation.', 'If `Completion Status` is `In Progress` and no named blocker or waiver stops work, Codex must continue instead of returning `Await Next Instruction`.', 'Use these governed state markers as execution control, not just reporting.', 'If `Continue Decision` is `Continue`, Codex must not end on a seam-complete final response, rollback path, or next-seam recommendation; it must keep executing until a lawful `Stop` decision exists.', 'Treat a prompt `Return:` block as the lawful-stop report, not as permission to stop while `Continue Decision` remains `Continue`.', 'A prompt `Return:` block is an output shape only; it cannot override governed continuation markers or authorize a terminal response while `Continue Decision` remains `Continue`.', 'A final response after a green seam while `Continue Decision` remains `Continue` is `Post-Seam Final-Stop Drift`.', 'Durability commit/push is not a lawful stop while `Continue Decision` remains `Continue`.', 'If `Completion Status` is `In Progress`, `Next Active Seam` must remain a `Workstream` seam; phase-exit seams require `Completion Status: Green`, `Completion Status: Red` with a named blocker/waiver, or explicit USER single-seam/backlog-split waiver.', '`Phase: Workstream` must remain bounded at all times, and the only lawful `Workstream` stop conditions are `Completion Status: Green` with `Hardening` next, or `Completion Status: Red` justified by a named blocker or waiver.', 'Single-seam or single-slice Workstream authority is forbidden unless explicit USER waiver text is recorded.', 'If only one seam or one slice is planned or visible, stop immediately on `Single-Seam Or Single-Slice Workstream Blocker` until Branch Readiness expands the plan or USER grants a waiver.', 'Only USER can grant a single-seam or single-slice Workstream waiver; Codex, ChatGPT, validators, prompt wording, clean validation, or a green seam cannot infer it.', 'A Workstream with `Completion Status: In Progress` and no waiver must show remaining same-branch implementable work beyond the current seam.', 'If `Completion Status` is `Red`, `Continuation Action` must report the blocker-clearing action or waiver-clearing action needed before bounded `Workstream` continuation may resume.'), Path('Docs/orin_task_template.md'): ('Seam Status:', 'Slice Status:', 'Completion Status:', 'Waiver Status:', 'Continue Decision:', 'Continuation Execution Latch:', 'Stop Basis:', 'Every phase digest must include `Next Legal Phase` as its own output field, even when `Continue Decision: Continue`; `Next Safe Move` may remain lawful-stop or route-specific and must not replace required continuation.', 'If `Completion Status` is `In Progress` and no named blocker or waiver stops work, Codex must continue instead of returning `Await Next Instruction`.', 'Use these governed state markers as execution control, not just reporting.', 'If `Continue Decision` is `Continue`, Codex must not end on a seam-complete final response, rollback path, or next-seam recommendation; it must keep executing until a lawful `Stop` decision exists.', 'A prompt `Return:` block is an output shape only; it cannot override governed continuation markers or authorize a terminal response while `Continue Decision` remains `Continue`.', 'Once the current slice is green during `Workstream`, advance into the next admitted slice while `Completion Status` remains `In Progress`; await the next instruction only after a lawful `Stop` decision.', 'A final response after a green seam while `Continue Decision` remains `Continue` is `Post-Seam Final-Stop Drift`.', 'Durability commit/push is not a lawful stop while `Continue Decision` remains `Continue`.', 'If `Completion Status` is `In Progress`, `Next Active Seam` must remain a `Workstream` seam; phase-exit seams require `Completion Status: Green`, `Completion Status: Red` with a named blocker/waiver, or explicit USER single-seam/backlog-split waiver.', '`Phase: Workstream` must remain bounded at all times, and the only lawful `Workstream` stop conditions are `Completion Status: Green` with `Hardening` next, or `Completion Status: Red` justified by a named blocker or waiver.', 'Single-seam or single-slice Workstream authority is forbidden unless explicit USER waiver text is recorded.', 'If only one seam or one slice is planned or visible, stop immediately on `Single-Seam Or Single-Slice Workstream Blocker` until Branch Readiness expands the plan or USER grants a waiver.', 'Only USER can grant a single-seam or single-slice Workstream waiver; Codex, ChatGPT, validators, prompt wording, clean validation, or a green seam cannot infer it.', 'A Workstream with `Completion Status: In Progress` and no waiver must show remaining same-branch implementable work beyond the current seam.', 'If `Completion Status` is `Red`, `Continuation Action` must report the blocker-clearing action or waiver-clearing action needed before bounded `Workstream` continuation may resume.')}

NEXT_LEGAL_PHASE_DIGEST_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/branch_records/index.md'),)

NEXT_LEGAL_PHASE_DIGEST_REQUIRED_PHRASES = ()

NEXT_LEGAL_PHASE_DIGEST_POINTER_REQUIRED_PHRASES = {}

MAIN_FIRST_LOADER_CHAIN_REQUIRED_PHRASES = {Path('Docs/development_rules.md'): ('Main is the first repo loader and routing index', 'Nexus Vision', 'family vision', 'active external branch plan'), Path('Docs/codex_modes.md'): ('Main is the first repo loader and routing index', 'Nexus Vision', 'family vision', 'active external branch plans'), Path('Docs/codex_user_guide.md'): ('Main is the first repo loader and source-truth router', 'Docs/nexus_vision.md', 'Docs/family_visions/', 'active external branch plan'), Path('Docs/orin_task_template.md'): ('Preserve the Main-first loader chain', 'project/family vision', 'active external branch plan', 'Docs/nexus_vision.md', 'Docs/family_visions/'), Path('Docs/governance_efficiency_operating_model.md'): ('Main-first loader chain', 'owning source-truth files', 'alternate first loaders'), Path('Docs/branch_plans/README.md'): ('Main-first loader chain', 'external operational state', 'branch-local engineering detail'), Path('Docs/family_visions/README.md'): ('Main-first loader chain', 'Docs/nexus_vision.md', 'C:\\Nexus Governance State\\branches\\<branch_slug>\\branch_plan.md')}

WORKSTREAM_ENTRY_WHOLE_PACKAGE_REQUIRED_PHRASES = {Path('Docs/branch_plans/README.md'): ('Workstream Entry Whole-Package Analysis Gate', 'all admitted slices/seams', 'completion strategy for the whole Workstream package', 'Hardening H1 expectations', 'Live Validation LV1 expectations', 'UTS handoff criteria', 'Workstream Entry Whole-Package Analysis Missing'), Path('Docs/branch_records/index.md'): ('Workstream Entry Whole-Package Analysis Gate', 'all admitted slices/seams', 'Hardening H1 expectations', 'Live Validation LV1 expectations', 'UTS handoff criteria', 'Workstream Entry Whole-Package Analysis Missing'), Path('Docs/development_rules.md'): ('Runtime BP3 with multiple admitted slices or seams', 'whole-package analysis before entry-seam implementation', 'Workstream Entry Whole-Package Analysis Missing'), Path('Docs/codex_modes.md'): ('BP3 for a runtime branch with multiple admitted slices or seams', 'all admitted slices/seams', 'completion strategy', 'Hardening H1 expectations', 'Live Validation LV1 expectations', 'UTS handoff criteria', 'Workstream Entry Whole-Package Analysis Missing'), Path('Docs/orin_task_template.md'): ('Workstream Entry Whole-Package Analysis:', 'Workstream Entry Whole-Package Summary:', 'all admitted slices/seams', 'Hardening H1 expectations', 'Live Validation LV1 expectations', 'UTS handoff criteria', 'This authorizes analysis only'), Path('Docs/codex_user_guide.md'): ('whole-package analysis before entry-seam implementation approval', 'first-seam-only handoff is not enough'), Path('Docs/governance_efficiency_operating_model.md'): ('whole-package analysis status', 'multiple slices or seams are admitted'), Path('Docs/validation_helper_registry.md'): ('Workstream Entry Whole-Package Analysis Gate', 'Formal Next Legal Phase Digest non-compaction', 'Forwarded Digest Non-Compaction Rule')}

USER_BRANCH_PLAN_REVIEW_REQUIRED_PHRASES = {Path('Docs/branch_plans/README.md'): ('Branch Planning', 'USER Branch Vision Review Gate', 'USER Branch Plan Review Gate', 'USER_BRANCH_VISION_REVIEW.md', 'USER_BRANCH_PLAN_REVIEW.md', 'Required review markers', 'Contract Status:', 'Contract Revision:', 'Accepted Branch Vision Summary:', 'Branch Scope Size Test:', 'SLC / Seam Plan:', 'USER Review Packet Finding:', 'End-State Vision:', 'Surface Map:', 'Exact BP3 Approval Text:', 'USER Review Response:', 'Codex Response Digest:', 'Packet Reviewability State:', 'USER Gate State:', 'BP2 Branch Plan Review Missing'), Path('Docs/branch_records/index.md'): ('Branch Planning', 'USER Branch Vision Review', 'USER Branch Plan Review Gate', 'USER_BRANCH_VISION_REVIEW.md', 'USER_BRANCH_PLAN_REVIEW.md', 'Contract Status', 'USER Review Packet Finding', 'USER Review Response', 'BP3 Orchestration Validation Missing'), Path('Docs/development_rules.md'): ('Branch Planning', 'USER_BRANCH_VISION_REVIEW.md', 'USER_BRANCH_PLAN_REVIEW.md', 'USER Branch Plan Review Gate', 'Contract Status', 'Pending USER Confirmation', 'BP3 Orchestration Validation Missing', 'USER Review Response', 'End-State Vision'), Path('Docs/codex_modes.md'): ('Branch Planning', 'USER_BRANCH_VISION_REVIEW.md', 'USER_BRANCH_PLAN_REVIEW.md', 'USER Branch Plan Review Gate', 'Contract Status', 'Pending USER Confirmation', 'USER Review Response', 'BP3'), Path('Docs/orin_task_template.md'): ('Branch Planning Review Packet:', 'USER Branch Vision Review:', 'USER Branch Plan Review:', 'Live Validation / UTS plan'), Path('Docs/codex_user_guide.md'): ('Branch Planning', 'USER Branch Vision Review', 'USER Branch Plan Review Gate', 'C:\\Nexus USER\\<label>', 'BP3', 'USER Review Packet Stale'), Path('Docs/governance_efficiency_operating_model.md'): ('Branch Planning', 'USER_BRANCH_VISION_REVIEW.md', 'USER_BRANCH_PLAN_REVIEW.md', 'USER Branch Plan Review Gate', 'Contract Status', 'accepting, revising, deferring with waiver, rejecting', 'USER response', 'local USER hub'), Path('Docs/validation_helper_registry.md'): ('Branch Planning', 'USER_BRANCH_VISION_REVIEW.md', 'USER_BRANCH_PLAN_REVIEW.md', 'USER Branch Plan Review Gate', 'Contract Status', 'BP1 Branch Vision Contract', 'BP2 Branch Plan Contract', 'USER Review Response')}

FORWARDED_DIGEST_NON_COMPACTION_REQUIRED_PHRASES = ()

WORKSTREAM_TO_PR_DEFAULT_GUARD_DOCS = (Path('Docs/codex_modes.md'), Path('Docs/codex_user_guide.md'),)

WORKSTREAM_TO_PR_DEFAULT_GUARD_PHRASES = (
    "There is no default direct `Workstream` -> `PR Readiness` transition.",
    "The normal next legal phase is `Hardening`, then `Live Validation`, then `PR Readiness`.",
    "Do not prompt Codex to treat Workstream completion as direct `PR Readiness`.",
)

PRE_PR_DURABILITY_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

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

AUTOMATION_RUNTIME_PROOF_CONTRACT_REQUIRED_PHRASES = {Path('Docs/development_rules.md'): ('Automation Runtime Unproven', '`ACTIVE` is configuration state, not run proof', 'thread/inbox output', 'automation memory/log/state-file updates', 'scheduler last-run evidence', 'bounded fallback', 'target-scoped', 'phase-scoped', 'self-terminating or explicitly deleted'), Path('Docs/codex_modes.md'): ('Automation Runtime Unproven', '`ACTIVE` is configuration state, not run proof', 'thread or inbox output', 'automation memory/log/state-file updates', 'scheduler last-run evidence', 'bounded fallback', 'target-scoped', 'phase-scoped', 'self-terminating or explicitly deleted'), Path('Docs/codex_user_guide.md'): ('Automation Runtime Unproven', '`ACTIVE` is configuration state, not run proof', 'thread or inbox output', 'automation memory/log/state-file updates', 'scheduler last-run evidence', 'bounded fallback', 'target-scoped', 'phase-scoped', 'self-terminating or explicitly deleted')}

AUTOMATION_RUNTIME_PROOF_CURRENT_STATE_REQUIRED_PHRASES = {
    Path("Docs/feature_backlog.md"): (
        "the PR watcher remains the only minute-scale heartbeat automation",
        "`ACTIVE` alone is not treated as run proof",
        "fallback helper must stay narrowed to the live PR and bounded to `PR Readiness`",
    ),
    Path("Docs/prebeta_roadmap.md"): (
        "the PR watcher remains the only minute-scale heartbeat automation",
        "`ACTIVE` alone is not treated as run proof",
        "fallback helper must stay narrowed to the live PR and bounded to `PR Readiness`",
    ),
}

PLANNING_LOOP_GUARDRAIL_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

PLANNING_LOOP_GUARDRAIL_PHRASES = ()

PROMPT_DISCIPLINE_REQUIRED_PHRASES = {Path('Docs/codex_user_guide.md'): ('When ChatGPT is generating the prompt, planning-loop risk belongs in preflight analysis.', 'Planning-loop prevention belongs in ChatGPT preflight analysis, not in a thicker Codex prompt body.', 'Once prompt generation is allowed, keep the Codex prompt thin and neutral.', 'Let repo truth, branch authority, canonical workstreams, and admitted slice records supply behavior after load rather than pasting full seam-governance rule blocks into the prompt text.'), Path('Docs/orin_task_template.md'): ('When ChatGPT is generating a Codex prompt, treat this template as a construction checklist rather than prompt text to paste wholesale.', 'Planning-loop prevention belongs in ChatGPT preflight analysis; once prompt generation is allowed, keep the prompt thin, neutral, and repo-aligned.')}

PROMPT_DISCIPLINE_PROHIBITED_PHRASES = {Path('Docs/codex_user_guide.md'): ('optional control add-ons only when they materially reduce ambiguity',)}

PLANNING_LOOP_ACTIVE_PHASES = (
    "Branch Readiness",
    "Workstream",
    "Hardening",
    "Live Validation",
    "PR Readiness",
)

BACKLOG_COMPLETION_ACTIVE_PHASES = (
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

SLICE_CONTINUATION_DEFAULT_LABEL = "Slice Continuation Default"
BACKLOG_SPLIT_APPROVAL_LABEL = "Backlog-Split User Approval"
BACKLOG_SPLIT_REASON_LABEL = "Backlog-Split Reason"
SAME_BRANCH_SLICE_CONTINUATION_VALUE = "same-branch backlog completion"
BACKLOG_COMPLETION_STATUS_HEADING = "Backlog Completion Status"
BACKLOG_COMPLETION_STRATEGY_HEADING = "Backlog Completion Strategy"
BACKLOG_COMPLETION_STATE_LABEL = "Backlog Completion State"
REMAINING_IMPLEMENTABLE_WORK_LABEL = "Remaining Implementable Work"
FUTURE_DEPENDENT_BLOCKERS_LABEL = "Future-Dependent Blockers"
BACKLOG_COMPLETION_GOAL_LABEL = "Branch Completion Goal"
KNOWN_FUTURE_DEPENDENT_BLOCKERS_LABEL = "Known Future-Dependent Blockers"
BRANCH_CLOSURE_RULE_LABEL = "Branch Closure Rule"
BACKLOG_COMPLETION_UNPROVEN_BLOCKER = "Backlog Completion Unproven"
BACKLOG_COMPLETION_IN_PROGRESS = "in progress"
BACKLOG_COMPLETION_IMPLEMENTED_COMPLETE = "implemented complete"
BACKLOG_COMPLETION_IMPLEMENTED_COMPLETE_FUTURE = "implemented complete except future dependency"
ACTIVE_SINGLE_SLICE_PROHIBITED_PATTERNS = (
    r"only the admitted ws-\d+",
    r"unless the user later approves another seam",
    r"later slices remain explicit approval gates",
)

LIVE_VALIDATION_REUSE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

LIVE_VALIDATION_REUSE_PHRASES = (
    "reuse",
    "existing",
    "one-off",
)

LIVE_VALIDATION_STALL_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

LIVE_VALIDATION_STALL_PHRASES = (
    "10s",
    "no-progress",
    "last confirmed",
)

LIVE_VALIDATION_AUTO_REPAIR_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

LIVE_VALIDATION_AUTO_REPAIR_PHRASES = (
    "codex-visible `repair` or `stop`",
    "bounded repair/rerun loop",
    "user acceptance",
    "real user-facing desktop launcher",
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

VALIDATION_HELPER_STANDARD_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/validation_helper_registry.md'),)

VALIDATION_HELPER_STANDARD_PHRASES = (
    "Docs/validation_helper_registry.md",
    "Helper Status:",
    "Workstream-scoped",
    "Consolidation Target",
    "Temporary probe",
)

PR_READINESS_BLOCKER_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

PR_READINESS_BLOCKER_PHRASES = (
    "stale-canon",
    "post-merge",
    "dirty",
    "docs-sync",
    "next-workstream",
    "Next Runtime Candidate Selection Pending",
    "Backlog Addition User Approval Missing",
    "Backlog Exhaustion User Decision Pending",
    "Single-Slice Package User Approval Missing",
    "Package Completion Unproven",
    "PR Readiness Execution User Approval Missing",
    "desktop-shortcut",
    "User Test Summary Results Pending",
    "PR Merge Status Unproven",
    "PR Merge Verification Pending",
    "Merge-Target Authority Projection Unproven",
    "PR Watcher Provisioning Unproven",
    "PR Watcher Routing Unverified",
    "Automation Observability Review Pending",
    "PR Readiness Scope Missed",
    "Release Window Audit Incomplete",
    "Between-Branch Canon Repair Attempt",
    "Next Branch Created Too Early",
    "Origin Main Reconciliation Packet Required",
    "Next Branch Package Shape Unproven",
    "Single-Slice Branch Drift Risk Unresolved",
    "Family Organization Drift Risk Unresolved",
    "Current-Branch Branch Readiness Re-entry Required",
    "New Carrier Branch Required",
    "PR Readiness Stage 1 Repair Pending",
)

PACKAGE_SLICE_BLOCKER_CATALOG_DOCS = (Path('Docs/feature_backlog.md'), Path('Docs/prebeta_roadmap.md'), Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/workstreams/index.md'), Path('Docs/branch_records/index.md'), Path('Docs/branch_records/codex_one_time_backlog_governance_repair.md'),)

PACKAGE_SLICE_BLOCKER_CATALOG_PHRASES = ()

RELEASE_WINDOW_AUDIT_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

RELEASE_WINDOW_AUDIT_PHRASES = (
    "Release Window Audit",
    "Release Window Audit Incomplete",
    "Remaining Known Release Blockers: None",
    "Another Pre-Release Repair PR Required: NO",
    "Release Window Split Waiver: None",
)

PR_READINESS_RESPONSE_CONTRACT_DOCS = (Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

PR_READINESS_RESPONSE_CONTRACT_PHRASES = (
    "## PR Readiness Stage 1 Analysis Packet",
    "Branch Readiness Stage 1 owns the normal next runtime implementation pipeline selection",
    "PR Readiness does not require selected-next truth or a waiver by default",
    "selected-next validation",
    "optional",
    "Optional conditional `Next Branch`",
    "Current-Branch Branch Readiness Re-entry Required",
    "New Carrier Branch Required",
    "Branch Readiness Fallback:",
    "Governance Ledger Fallback:",
    "## PR Creation Details",
    "### PR Title",
    "### Base Branch",
    "### Head Branch",
    "### PR Summary",
    "## What Changed",
    "The PR summary/GitHub PR body uses exactly two top-level sections: `## Summary` and `## What Changed`.",
    "`## Summary` must be one concise human-readable outcome paragraph",
    "`## What Changed` must describe the actual branch work",
    "GitHub PR bodies and PR Summary copy must not include `## Validation`, `## PR posture`, `## Branch Evidence`",
    "Validation commands, command output, byte-proof evidence, mergeability, bot-review state, watcher state, and PR Readiness posture belong in Codex digests, helper output, status checks, or external operational state",
    "inclusion-only",
    "defensive scope language",
    "All visible PR bodies must be scanned by `dev\\orin_pr_body_quality_audit.py`; every nonconforming PR body inside the approved GitHub correction scope must be repaired before the PR-body standard can be reported green.",
)

PR_READINESS_STAGE_GATE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/branch_records/index.md'), Path('Docs/branch_records/codex_one_time_backlog_governance_repair.md'),)

PR_READINESS_STAGE_GATE_PHRASES = (
    "PR Readiness Stage 1 - Analysis Gate",
    "PR Readiness Stage 2 - Execution Gate",
    "PR Readiness Execution User Approval Missing",
    "analysis-first blocker repair gate",
    "PR Readiness Stage 1 Repair Pending",
    "USER approval to enter Stage 2",
)

PR_READINESS_STAGE_PACKET_DOCS = (Path('Docs/orin_task_template.md'),)

PR_READINESS_STAGE_PACKET_PHRASES = (
    "## PR Readiness Stage 1 Analysis Packet",
    "Planned PR Title:",
    "Planned Base Branch:",
    "Planned Head Branch:",
    "Planned PR Summary:",
    "Selected-Next Validation Status:",
    "Selected-Next Scope:",
    "Branch Readiness Stage 1 Successor Selection Owner:",
    "Current-Branch Branch Readiness Re-entry Required",
    "New Carrier Branch Required",
    "Required Post-Merge Path:",
    "Release-Debt Impact:",
    "Release-Debt Handling Status:",
    "No-Release-Debt Handling Status:",
    "Required Current-Branch Source-Truth Sync:",
    "Planned Merge-Target Canon Updates:",
    "Origin/Main Freshness Check:",
    "Branch Creation Base:",
    "Current origin/main:",
    "Origin/Main Advanced Since Branch Creation:",
    "Origin/Main Changed Files:",
    "Branch Changed Files:",
    "Reconciliation Required:",
    "Reconciliation File List:",
    "Reconciliation Recommendation:",
    "Reconciliation Mutation Status:",
    "Origin Main Reconciliation Packet Required",
    "Review-Risk / Adversarial Coverage:",
    "Optional Next Branch Block:",
    "Planned Watcher Provisioning:",
    "Expected Files To Change:",
    "Stage 1 Repairs Made:",
    "Stage 1 Repair Validation:",
    "Release Readiness Health Pass:",
    "PR Readiness Stage 1 Repair Pending",
    "Governance Ledger Fallback:",
    "Branch Readiness Fallback:",
    "Stage 1 Outcome:",
    "Stage 2 Sync Plan:",
    "Next Legal Phase:",
    "Stage 2 Green-Light Decision Needed:",
)

PR_READINESS_ORIGIN_MAIN_FRESHNESS_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'),)

PR_READINESS_ORIGIN_MAIN_FRESHNESS_PHRASES = (
    "Origin/Main Freshness Check",
    "Branch Creation Base:",
    "Current origin/main:",
    "Origin/Main Advanced Since Branch Creation:",
    "Origin/Main Changed Files:",
    "Branch Changed Files:",
    "Reconciliation Required:",
    "Reconciliation File List:",
    "Reconciliation Recommendation:",
    "Reconciliation Mutation Status:",
    "Origin Main Reconciliation Packet Required",
    "no file fixes during Stage 1",
)

PR_READINESS_ORIGIN_MAIN_FRESHNESS_MARKERS = (
    "Branch Creation Base",
    "Current origin/main",
    "Origin/Main Advanced Since Branch Creation",
    "Origin/Main Changed Files",
    "Branch Changed Files",
    "Reconciliation Required",
    "Reconciliation File List",
    "Reconciliation Recommendation",
    "Reconciliation Mutation Status",
)

PROMPT_ENTRY_ORIGIN_MAIN_FRESHNESS_REQUIRED_PHRASES = {Path('Docs/development_rules.md'): ('Prompt-Entry Origin/Main Freshness Gate', 'Prompt-Entry Freshness Check:', 'Fetched origin/main:', 'Current Worktree:', 'Current Branch:', 'HEAD:', 'origin/main:', 'Merge Base With origin/main:', 'Origin/Main Advanced Since Last Action:', 'Pre-Rebaseline Impact Audit Required:', 'Rebaseline/Reconciliation Status:', 'Prompt-Entry Origin/Main Freshness Missing', 'Origin/Main Advanced Rebaseline Required', 'validating locally is not enough'), Path('Docs/codex_modes.md'): ('Prompt-Entry Origin/Main Freshness Gate', 'Prompt-Entry Freshness Check:', 'Fetched origin/main:', 'Origin/Main Advanced Since Last Action:', 'Pre-Rebaseline Impact Audit Required:', 'Rebaseline/Reconciliation Status:', 'Prompt-Entry Origin/Main Freshness Missing', 'Origin/Main Advanced Rebaseline Required', 'validating locally is not enough'), Path('Docs/codex_user_guide.md'): ('Prompt-Entry Origin/Main Freshness Gate', 'Prompt-Entry Freshness Check:', 'Fetched origin/main:', 'Origin/Main Advanced Since Last Action:', 'Pre-Rebaseline Impact Audit Required:', 'Rebaseline/Reconciliation Status:', 'Prompt-Entry Origin/Main Freshness Missing', 'Origin/Main Advanced Rebaseline Required', 'validating locally is not enough'), Path('Docs/orin_task_template.md'): ('Prompt-Entry Freshness Check:', 'Fetched origin/main:', 'Current Worktree:', 'Current Branch:', 'HEAD:', 'Upstream:', 'origin/main:', 'Merge Base With origin/main:', 'Origin/Main Advanced Since Last Action:', 'Pre-Rebaseline Impact Audit Required:', 'Rebaseline/Reconciliation Status:', 'Prompt-Entry Origin/Main Freshness Missing', 'Origin/Main Advanced Rebaseline Required'), Path('Docs/validation_helper_registry.md'): ('Prompt-Entry Origin/Main Freshness Gate', 'Prompt-Entry Freshness Check:', 'Fetched origin/main:', 'Origin/Main Advanced Since Last Action:', 'Pre-Rebaseline Impact Audit Required:', 'Rebaseline/Reconciliation Status:', 'Prompt-Entry Origin/Main Freshness Missing')}

CURRENT_MAIN_RECONCILIATION_IDENTITY_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/validation_helper_registry.md'),)

CURRENT_MAIN_RECONCILIATION_IDENTITY_PHRASES = (
    "Current-Main Reconciliation Identity Guard",
    "origin/main is context, not identity",
    "Assigned Worktree Branch Identity:",
    "Branch-Local Authority Reassertion:",
    "Incoming Main Active-Branch Blocks Accepted: NO",
    "Sibling Worktree Identity Preservation:",
    "Worktree Branch Identity Drift",
)

PRE_REBASELINE_IMPACT_AUDIT_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'),)

PRE_REBASELINE_IMPACT_AUDIT_PHRASES = (
    "Pre-Rebaseline Impact Audit",
    "No Baseline By Inertia",
    "Incoming Main Change Set",
    "Incoming Changed Files",
    "Current Worktree Changed Files",
    "Branch Changed Files",
    "Rebaseline Overlap Files",
    "Rebaseline Overlap Intent Gate",
    "Branch Change Intent Ledger",
    "Rebaseline Overlap Intent Missing",
    "Incoming Runtime / Source-Truth Risk",
    "Validation Before Rebaseline",
    "Recommendation Only",
    "Rebaseline Mutation Approval",
    "Rebaseline Mutation Status",
)

PRE_REBASELINE_HELPER_PHRASES = (
    "Rebaseline Overlap Files:",
    "Branch Change Intent Ledger Path:",
    "Rebaseline Overlap Intent Gate:",
    "Overall Overlap Gate Result:",
    "Rebaseline Overlap Failure Procedure:",
    "Rebaseline Overlap Intent Missing:",
    "Per-File Result:",
    "Regression / Gating Impact:",
    "Fallback Evidence:",
)

RELEASE_READINESS_HEALTH_GATE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'),)

RELEASE_READINESS_HEALTH_GATE_PHRASES = (
    "Release Readiness Health Pass",
    "--release-readiness-health-gate",
    "post-merge source truth",
    "Post-Merge Branch Authority Projection:",
    "Stale Active Branch Wording Scan:",
    "Stale PR Creation / PR Readiness Pending Wording Scan:",
    "Merged-Unreleased Scope Posture:",
    "Release Execution Gate:",
    "Watcher / Live PR State Projection:",
    "Branch Cleanup Plan:",
    "Branch Cleanup Execution Gate:",
    "FAM Overlap Routing:",
    "Release Candidate Anchor Projection:",
    "Release Window Contributor Inventory:",
    "Governance Intake Routing:",
    "Projected Post-Merge Validation:",
)

RELEASE_READINESS_HEALTH_PASS_REQUIRED_MARKERS = (
    "Post-Merge Branch Authority Projection",
    "Stale Active Branch Wording Scan",
    "Stale PR Creation / PR Readiness Pending Wording Scan",
    "Merged-Unreleased Scope Posture",
    "Release Execution Gate",
    "Watcher / Live PR State Projection",
    "Branch Cleanup Plan",
    "FAM Overlap Routing",
    "Release Candidate Anchor Projection",
    "Release Window Contributor Inventory",
    "Projected Post-Merge Validation",
)

RELEASE_READINESS_HEALTH_PASS_PASS_ONLY_MARKERS = (
    "Post-Merge Branch Authority Projection",
    "Stale Active Branch Wording Scan",
    "Stale PR Creation / PR Readiness Pending Wording Scan",
    "Release Execution Gate",
    "Watcher / Live PR State Projection",
    "Branch Cleanup Plan",
    "FAM Overlap Routing",
    "Release Candidate Anchor Projection",
    "Release Window Contributor Inventory",
    "Projected Post-Merge Validation",
)

RELEASE_READINESS_HEALTH_PASS_OPTIONAL_MARKERS = {
    "Merged-Unreleased Scope Posture": {"PASS", "NOT APPLICABLE", "N/A"},
}

RELEASE_READINESS_HEALTH_STALE_POST_MERGE_PATTERNS = (
    ("active branch authority marker", r"Branch Authority Marker:\s*`?Active Branch`?"),
    ("active branch authority state", r"Branch Authority State:\s*`?Active\b"),
    ("active current phase", r"Phase:\s*`?(?:Branch Readiness|Workstream|Hardening|Live Validation|PR Readiness)`?"),
    ("PR creation pending", r"\bPR Creation Pending\b"),
    ("PR creation approval missing", r"\bPR Creation Approval Missing\b"),
    ("PR readiness Stage 2 pending", r"\bPR Readiness Stage 2\s*(?:Pending|Denied)\b"),
    ("PR readiness execution approval missing", r"\bPR Readiness Execution User Approval Missing\b"),
    ("PR validation pending", r"\bPR Validation Pending\b"),
    ("PR merge verification pending", r"\bPR Merge Verification Pending\b"),
    ("bot review signal pending", r"\bBot Review Signal Pending\b"),
    ("PR watcher provisioning unproven", r"\bPR Watcher Provisioning Unproven\b"),
    ("PR watcher routing unverified", r"\bPR Watcher Routing Unverified\b"),
    ("current PR readiness seam", r"\bCurrent PR Readiness Seam:\b"),
    ("live open PR state", r"\bLive PR State:\s*`?open\b"),
    ("merge-watch ownership", r"\bmerge-watch ownership\b"),
    ("selected-next pending", r"\b(?:selected-next|selected next).{0,40}\b(?:pending|unresolved|unknown)\b"),
    ("release floor unresolved", r"\bRelease Floor:\s*`?(?:TBD|Unknown|Unresolved|Pending)\b"),
    ("release window unresolved", r"\bRelease Window(?: Audit)?:\s*`?(?:TBD|Unknown|Unresolved|Pending)\b"),
)

BRANCH_RECORD_LIVE_STATE_LEAKAGE_FIXTURE_DIR = Path(
    "dev/fixtures/branch_record_live_state_leakage"
)

BRANCH_RECORD_LIVE_STATE_LEAKAGE_PATTERNS = (
    ("active branch authority marker", r"Branch Authority Marker:\s*`?Active Branch`?"),
    ("active branch authority state", r"Branch Authority State:\s*`?Active\b"),
    ("active transition waiver", r"Active Branch Authority Transition Waiver:\s*Granted"),
    (
        "active lifecycle state field",
        r"^\s*(?:-\s*)?(?:Record State|Status):\s*`?(?:Branch Readiness|Branch Planning|Workstream|Hardening|Live Validation|PR Readiness|Release Readiness)\b",
    ),
    (
        "active current phase",
        r"^\s*(?:-\s*)?(?:Current Phase|Phase):\s*`?(?:Branch Readiness|Branch Planning|Workstream|Hardening|Live Validation|PR Readiness|Release Readiness)`?",
    ),
    (
        "active review/PR pending gate",
        r"\b(?:PR Readiness Stage 1 pending USER approval|Stage 2 PR creation pending USER approval|PR creation pending USER approval)\b",
    ),
    (
        "active next legal phase gate",
        r"^\s*(?:-\s*)?Next Legal Phase Gate:\s*`?(?!(?:Historical|Not applicable|No next execution phase|Cleared|Closed|PR #\d+ is merged|PR #\d+ merged)\b)[^`\r\n]*(?:PR Readiness Stage 2|Stage 2 PR creation|PR creation|Execution Gate|create the PR|pending USER approval|approval missing|USER approval to enter|USER denied PR Readiness Stage 2)\b",
    ),
    (
        "active stage 2 approval decision",
        r"^\s*(?:-\s*)?(?:Stage 2 Green-Light Decision Needed|PR Readiness Stage 2 Green-Light Decision Needed):\s*`?(?!(?:Historical|Closed|Fulfilled historically|Granted by USER)\b)[^`\r\n]*(?:I approve|Approve|USER approval|Pending USER approval|PR Readiness Stage 2|PR creation|create the PR)\b",
    ),
    (
        "active exact user approval text",
        r"^\s*(?:-\s*)?(?:Exact USER Approval Text|Exact USER Decision Needed|Exact Next USER Decision Needed):",
    ),
    ("pre-pr live state", r"^\s*(?:-\s*)?Pre-PR Live State:\s*`?No live PR\b"),
    (
        "pending PR creation approval",
        r"^\s*(?:-\s*)?PR Creation Approval:\s*`?Pending USER approval\b",
    ),
    (
        "pending Stage 2 PR creation",
        r"^\s*(?:-\s*)?Stage 2 PR Creation:\s*`?Pending USER approval\b",
    ),
    ("live open PR state", r"\bLive PR State:\s*`?open\b"),
    ("current PR readiness seam", r"\bCurrent PR Readiness Seam:\b"),
    ("active worktree confinement", r"Assigned Worktree Confinement:\s*`?Active\b"),
    (
        "active thread assignment",
        r"Thread Assignment Status:\s*`?(?:Assigned and active|Active)\b",
    ),
    (
        "active branch plan owner",
        r"(?:Branch Runtime Engineering Plan|Engineering Plan Status|Active Branch Plan|Branch Plan Status):\s*`?Active\b",
    ),
    ("release window current owner", r"\bRelease Window(?: Audit)?:\s*`?(?:TBD|Unknown|Unresolved|Pending)\b"),
)

RELEASE_READINESS_ACTIVE_AUTHORITY_FOLD_DOWN_MARKERS = (
    "must not remain active branch authority",
    "must not retain active",
    "must become historical merged-unreleased",
    "must become historical merged-unreleased evidence",
    "must be historical merged-unreleased",
    "becomes historical merged-unreleased",
    "move this branch authority to historical merged-unreleased",
    "move the branch authority to historical merged-unreleased",
    "move the record to historical branch authority records",
    "historical/no-active",
)

PR_READINESS_STAGE1_READINESS_LOCK_REQUIRED_PHRASES = {Path('Docs/development_rules.md'): ('PR Readiness Stage 1 is the Stage 2 readiness-lock gate', 'Stage 1 Ready For Stage 2', 'PR Readiness Stage 1 Repair Required', 'Current-Branch Branch Readiness Re-entry Required', 'New Carrier Branch Required', 'Stage 1 USER Waiver Required', 'Stage 2 owns final PR execution only', 'PR Readiness does not require selected-next truth or a waiver by default'), Path('Docs/codex_modes.md'): ('PR Readiness Stage 1 is the Stage 2 readiness-lock gate', 'Stage 1 Ready For Stage 2', 'PR Readiness Stage 1 Repair Required', 'Current-Branch Branch Readiness Re-entry Required', 'New Carrier Branch Required', 'Stage 1 USER Waiver Required', 'Stage 2 owns final PR execution only', 'PR creation is blocked while any Stage 1 blocker', 'PR Readiness does not require selected-next truth or a waiver by default'), Path('Docs/orin_task_template.md'): ('PR Readiness Stage 1 is the Stage 2 readiness-lock gate', 'Stage 1 Ready For Stage 2', 'PR Readiness Stage 1 Repair Required', 'Current-Branch Branch Readiness Re-entry Required', 'New Carrier Branch Required', 'Stage 1 USER Waiver Required', 'Stage 2 owns final PR execution only', 'Stage 1 Outcome:', 'PR Readiness does not require selected-next truth or a waiver by default'), Path('Docs/codex_user_guide.md'): ('analysis-first readiness-lock gate', 'Stage 1 Ready For Stage 2', 'PR Readiness Stage 1 Repair Required', 'Current-Branch Branch Readiness Re-entry Required', 'New Carrier Branch Required', 'Stage 1 USER Waiver Required', 'Stage 2 owns final PR execution only', 'Branch Readiness Stage 1 owns the normal next runtime implementation pipeline selection', 'Branch Readiness fallback is real carrier branch/package analysis', 'PR Readiness does not require selected-next truth or a waiver by default'), Path('Docs/branch_records/index.md'): ('analysis-first readiness-lock gate', 'Stage 1 Ready For Stage 2', 'PR Readiness Stage 1 Repair Required', 'Current-Branch Branch Readiness Re-entry Required', 'New Carrier Branch Required', 'Stage 1 USER Waiver Required', 'approved final PR execution pass', 'Branch Readiness fallback is real carrier branch/package analysis', 'PR Readiness does not require selected-next truth or a waiver by default'), Path('Docs/branch_records/codex_v1_6_13_prebeta_post_merge_closeout_hardening.md'): ('Branch Readiness Stage 2-R2 PR Readiness Stage 1 Readiness-Lock Governance Repair', 'Branch Readiness Stage 2-R3 Superseded PR Stage 1 Repair Wording Cleanup', 'Stage 1 Readiness-Lock Finding:', 'Stage 1 Outcome Model:', 'Current-Branch Branch Readiness Re-entry Required:', 'New Carrier Branch Required:', 'Stage 2 Final-Execution Boundary:', 'Branch Readiness Fallback Clarification:', 'PR Creation Blocker:')}

BRANCH_READINESS_STAGE_GATE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/workstreams/index.md'), Path('Docs/branch_records/index.md'), Path('Docs/branch_records/codex_one_time_backlog_governance_repair.md'),)

BRANCH_READINESS_STAGE_GATE_PHRASES = (
    "Branch Readiness Stage 1 - Analysis Gate",
    "Branch Readiness Stage 2 - Execution Gate",
    "Branch Readiness Execution User Approval Missing",
    "no repository file mutation",
)

BRANCH_READINESS_STAGE_PACKET_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

BRANCH_READINESS_STAGE_PACKET_PHRASES = (
    "## Branch Readiness Stage 1 Analysis Packet",
    "FAM/package candidate",
    "package-size review",
    "multiple admitted-slice plan",
    "single-slice drift check",
    "Element Coverage review",
    "product vision",
    "USER vision questions",
    "Codex product interpretation",
    "Codex implementation recommendation",
    "USER/ChatGPT review checkpoint",
    "Project-Wide Vision Alignment:",
    "Branch-Specific Vision Alignment:",
    "System Concept Model:",
    "Entity / Profile Model:",
    "User Workflow Model:",
    "Scale / Data Volume Model:",
    "Configuration And State Model:",
    "Expected User-Facing Outcomes:",
    "Codex Additional Recommendations:",
    "USER Critique Loop:",
    "USER Decision Ledger:",
    "Deferred Ideas / Future Package Ledger:",
    "USER Vision Question Packet",
    "full feature element breakdown",
    "current branch vs future package boundaries",
    "affected surfaces",
    "branch reach",
    "why the branch is large enough",
    "why it should not split into tiny branches",
    "acceptance criteria",
    "screenshot",
    "User Test Summary",
    "implementation sequence proposal",
    "validation plan",
    "Stale Branch Cleanup Plan:",
    "expected docs sync",
    "Branch Readiness Planning Incomplete",
    "USER Vision Recommendation Missing",
    "Next Legal Phase:",
    "Stage 2 green-light decision",
)

STALE_BRANCH_CLEANUP_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'),)

STALE_BRANCH_CLEANUP_PHRASES = (
    "Stale Branch Cleanup Plan:",
    "Branch Cleanup Execution Gate:",
    "GitHub Desktop-bound worktree",
    "Branch Readiness Stage 2 - Execution Gate",
)

STABLE_WORKTREE_PATH_PRESERVATION_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/branch_records/index.md'),)

STABLE_WORKTREE_PATH_PRESERVATION_PHRASES = (
    "Stable Worktree Path Preservation Gate:",
    "Stable Worktree Path:",
    "Replacement Binding Path:",
    "Stable Worktree Path At Risk",
)

BRANCH_READINESS_CARRIER_LIFECYCLE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/branch_records/index.md'), Path('Docs/validation_helper_registry.md'),)

BRANCH_READINESS_CARRIER_LIFECYCLE_PHRASES = (
    "Carrier Lifecycle Decision",
    "Carrier Lifecycle Classification:",
    "Remote Branch State:",
    "Unique Branch Diff:",
    "Origin/Main Ancestry:",
    "Origin/Main Advanced Since Branch Creation:",
    "Open PR State:",
    "Worktree Checkout State:",
    "Recommended Stage 2 Carrier Action:",
    "Stale Branch Cleanup Plan:",
    "Branch Cleanup Execution Gate:",
    "Recreate From Current origin/main:",
    "No Unique Commit Loss Proof:",
    "Fresh current branch",
    "Stale empty local branch",
    "Stale branch with unique commits",
    "Historical merged branch",
    "Wrong carrier/worktree",
    "Active remote/open PR branch",
)

RUNTIME_ENGINEERING_CONTRACT_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/validation_helper_registry.md'), Path('Docs/branch_records/index.md'), Path('Docs/workstreams/index.md'),)

RUNTIME_ENGINEERING_CONTRACT_PHRASES = (
    "Runtime Branch Engineering Contract",
    "USER Engineering Planning Review:",
    "Runtime Implementation Approval:",
    "Current Runtime Baseline:",
    "Planned Runtime Delta:",
    "User-Facing Runtime Delta:",
    "State / Config / Schema Delta:",
    "Validator / Helper Delta:",
    "Workstream Seam Map:",
    "Proof Expectations:",
    "Plan-To-Implementation Traceability:",
)

BRANCH_RUNTIME_ENGINEERING_PLAN_REQUIRED_PHRASES = {Path('Docs/development_rules.md'): ('Branch Runtime Engineering Plan', 'local USER hub packet', 'C:\\Nexus Governance State\\branches\\<branch_slug>\\branch_plan.md', 'Branch Runtime Engineering Plan Path:', 'PR Fold-Down Packet:'), Path('Docs/codex_modes.md'): ('Branch Runtime Engineering Plan', 'local USER hub packet', 'Branch Runtime Engineering Plan Path:', 'Engineering Plan Status:', 'PR Fold-Down Packet:'), Path('Docs/orin_task_template.md'): ('Branch Runtime Engineering Plan', 'Element-to-Phase Proof Matrix', 'Branch Planning Review Packet', 'Branch Runtime Engineering Plan Path:', 'Engineering Plan Status:', 'PR Fold-Down Packet:'), Path('Docs/validation_helper_registry.md'): ('Branch Runtime Engineering Plan', 'Element-to-Phase Proof Matrix', 'Branch Planning packets', 'active external branch plans', 'invalid backlog planning sprawl'), Path('Docs/branch_records/index.md'): ('Branch Runtime Engineering Plan', 'Branch Runtime Engineering Plan Path:', 'Engineering Plan Status:', 'PR Fold-Down Packet:'), Path('Docs/workstreams/index.md'): ('Branch Runtime Engineering Plan', 'C:\\Nexus Governance State\\branches\\<branch_slug>\\branch_plan.md', 'PR Readiness fold-down'), Path('Docs/branch_plans/README.md'): ('Branch Runtime Engineering Plan', 'Element-to-Phase Proof Matrix', 'Branch Planning Review Packet', 'C:\\Nexus Governance State\\branches\\<branch_slug>\\branch_plan.md', 'Per-Seam Implementation Checklist:', 'PR Readiness Fold-Down / Retention Checklist:', 'Release Readiness Public-Scope Translation Checklist:')}

USER_FEEDBACK_DISPOSITION_REQUIRED_PHRASES = {Path('Docs/branch_plans/README.md'): ('USER Feedback Disposition Markers', 'Minimum UFD ledger markers', '### UFD Item: UFD-<scope>-YYYYMMDD-NNN', 'UFD IDs use `UFD-<scope>-YYYYMMDD-NNN`', 'No-Action Reason:', 'fold-down receipt must preserve a lookup path'), Path('Docs/governance_efficiency_operating_model.md'): ('USER Feedback Disposition Model', 'UFD Ledger Owner:', 'full active USER Feedback Disposition rows', 'exact-normalized duplicate `Feedback Summary:`'), Path('Docs/validation_helper_registry.md'): ('USER Feedback Disposition scaffolding', 'marker-first', 'No Durable Owner Needed'), Path('Docs/orin_task_template.md'): ('USER Feedback Disposition Required:', 'UFD Ledger Status:', 'UFD Ledger Owner:', 'UFD Items:', '| Feedback ID |')}

BRANCH_RUNTIME_ENGINEERING_PLAN_COMPACT_POINTER_SURFACES = (
    Path("Docs/feature_backlog.md"),
    Path("Docs/prebeta_roadmap.md"),
)

CHATGPT_LOADER_SOURCE_TRUTH_SYNC_REQUIRED_PHRASES = {Path('Docs/development_rules.md'): ('Local ChatGPT custom instructions should stay compact', 'Do not paste the loader doc into Codex prompts', 'FAM-006 Monitoring and HUD selected-next truth only after explicit USER approval', 'Windows-first, modular, GPU-aware direction with optional heavy local AI capability packs and CPU fallback'), Path('Docs/codex_modes.md'): ('Local ChatGPT custom instructions should stay compact', 'Do not paste the loader doc into Codex prompts', 'FAM-006 Monitoring and HUD selected-next truth only after explicit USER approval', 'Windows-first, modular, GPU-aware direction with optional heavy local AI capability packs and CPU fallback'), Path('Docs/codex_user_guide.md'): ('Local ChatGPT custom instructions should stay compact', 'Do not paste the loader doc into Codex prompts', 'FAM-006 Monitoring and HUD selected-next truth only after explicit USER approval', 'Windows-first, modular, GPU-aware product direction with optional heavy local AI capability packs and CPU fallback'), Path('Docs/orin_task_template.md'): ('Local ChatGPT custom instructions should stay compact', 'Do not paste `Docs/nexus_startup_contract.md` into Codex prompts', 'FAM-006 Monitoring and HUD selected-next truth only after explicit USER approval', 'Windows-first, modular, GPU-aware direction with optional heavy local AI capability packs and CPU fallback'), Path('Docs/feature_backlog.md'): ('Canonical Identity Model', 'PR Evidence Standard', 'Element Coverage Standard', 'FAM-006` | Monitoring and HUD', 'FAM-007` | Local AI and Capability Packs', 'FAM-008` | Packaging and Install Experience'), Path('Docs/branch_records/codex_v1_6_13_prebeta_post_merge_closeout_hardening.md'): ('Branch Readiness Stage 2-R1 Governance Ledger / Loader Sync Record', 'ChatGPT Loader / New-Chat Source-Truth Sync:', 'FAM-006 Recommendation-Only Posture:', 'Project Direction Preservation:')}

ELEMENT_COVERAGE_DOCS = (Path('Docs/feature_backlog.md'), Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/workstreams/index.md'), Path('Docs/branch_records/index.md'), Path('Docs/branch_records/codex_one_time_backlog_governance_repair.md'),)

ELEMENT_COVERAGE_PHRASES = (
    "Element Coverage",
    "user-facing surface",
    "runtime/backend behavior",
    "fail-safe/recovery",
    "security/privacy",
    "voice/audio",
    "external integration",
    "local AI/capability packs",
    "packaging/install",
    "monitoring/HUD",
    "validation",
    "release impact",
    "Element Coverage rows never count as `Admission State: Admitted`, slices, seams, packages, FAMs, selected-next truth, or release drivers",
)

RELEASE_OPERATOR_OUTPUT_CONTRACT_DOCS = (Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

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

PR_LIVE_STATE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/incident_patterns.md'),)

PR_LIVE_STATE_PHRASES = (
    "PR package ready",
    "PR Creation Pending",
    "PR Validation Pending",
    "PR State Unknown",
    "PR Merge Status Unproven",
    "PR Merge Verification Pending",
)

BOT_REVIEW_SIGNAL_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

BOT_REVIEW_SIGNAL_PHRASES = (
    "Bot Review Signal Pending",
    "live PR",
    "thumbs-up reaction",
    "approval proof must be bound to the current live PR head",
    "bot comment",
    "3-5 words only",
    "post-repair bot thumbs-up/approval latch",
    "same-PR Codex bot-review repair loop",
    "Stage 2 final handoff cannot be green until the post-repair bot thumbs-up/approval latch is verified",
)

PR_WATCHER_THREAD_CONTRACT_DOCS = (Path('Docs/pr_watcher_mode_contract.md'),)

PR_WATCHER_THREAD_CONTRACT_PHRASES = (
    "direct PR verification",
    "recurring PR watcher automation",
    "USER-approved watcher exception",
    "approved reporting surface",
    "delivery proof",
    "PR Watcher Routing Unverified",
    "PR Merge Verification Pending",
    "Watcher configuration is not runtime proof",
)

PR_WATCHER_MODE_CONTRACT_DOC = Path("Docs/pr_watcher_mode_contract.md")
PR_WATCHER_MODE_CONTRACT_POINTER_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/validation_helper_registry.md'), Path('Docs/governance_process_efficiency_reform_plan.md'), Path('Docs/branch_records/feature_release_readiness_source_truth_intake.md'),)
PR_WATCHER_MODE_CONTRACT_PHRASES = (
    "PR Watcher Mode Contract",
    "Silent Monitor",
    "Verify Once",
    "Repair Mode",
    "Blocked Mode",
    "Watcher Health Proof:",
    "Watcher Mode:",
    "Configured CWD:",
    "Worktree / Branch:",
    "PR:",
    "Head SHA:",
    "Mergeability:",
    "Unresolved Review Threads:",
    "Latest Bot Review:",
    "Repair Authority:",
    "Delivery Route Proof:",
    "Runtime Proof:",
    "Next Watcher Posture:",
    "Reliability Degradation",
    "Background Observability",
    "3-5 word PR comment only",
)

PR_WATCHER_DENIAL_POLICY_DOCS = (Path('Docs/pr_watcher_mode_contract.md'), Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/validation_helper_registry.md'), Path('Docs/branch_records/index.md'), Path('Docs/codex_user_guide.md'), Path('Docs/incident_patterns.md'), Path('Docs/branch_records/feature_release_readiness_source_truth_intake.md'),)
PR_WATCHER_DENIAL_POLICY_PHRASES = (
    "direct PR verification",
    "recurring PR watcher automation",
    "Direct PR2 Continuation Rule",
)
PR_WATCHER_DENIAL_FORBIDDEN_PHRASES = (
    "PR Readiness Stage 2 approval includes watcher provisioning by default",
    "Stage 2 final handoff cannot be green until watcher runtime proof is present",
    "Stage 2 must provision or update a PR watcher",
    "Standard operating procedure from now on is a watcher on an approved Codex reporting surface",
)

PR_WATCHER_OUTPUT_CONTRACT_SOURCE = Path("dev/pr_same_thread_watcher.py")
PR_WATCHER_OUTPUT_CONTRACT_PHRASES = (
    "PR watcher source-of-truth update",
    "Governed State:",
    "Live PR Truth:",
    "Watcher Proof:",
    "Copy/Paste Codex Prompt:",
    "Mode: Release Readiness",
    "PR Merge Verification Pending",
    "lastThreadDeliveryProven",
    "lastThreadDeliveryProof",
    "verified transcript fallback",
    "record_visible_delivery",
    "final thread delivery proof is missing",
)

GOVERNANCE_RECURRENCE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/codex_user_guide.md'), Path('Docs/branch_records/index.md'),)

GOVERNANCE_RECURRENCE_PHRASES = (
    "patch the canon or validator rule that allowed it before the repair is considered complete",
    "drift prevention proof is mandatory",
    "merge-stable pointer surfaces such as backlog and roadmap must not mirror transient repair-branch ownership",
    "PR Watcher Provisioning Unproven",
    "PR Watcher Routing Unverified",
)

POST_MERGE_CLOSEOUT_PROOF_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/codex_user_guide.md'), Path('Docs/orin_task_template.md'), Path('Docs/branch_records/index.md'),)

POST_MERGE_CLOSEOUT_PROOF_PHRASES = (
    "post-merge closeout proof must be in merged source truth",
    "not only in a deleted branch, reflog, automation memory, or conversation transcript",
    "next real runtime package carrier",
)

HISTORICAL_BRANCH_ACTIVE_PR_MARKERS = (
    "Current PR Readiness Seam:",
    "Live PR State: `OPEN",
    "Live PR State: `open",
    "PR Validation Pending",
    "PR Merge Verification Pending",
    "PR Creation Approval: Pending",
    "Stage 2 PR Creation: Pending",
    "PR Readiness Stage 1 Ready For Stage 2",
    "PR Readiness Stage 2 / PR creation remains pending",
    "PR Readiness Stage 2 / PR creation pending",
)

PR_LIFECYCLE_SOURCE_TRUTH_MARKERS = (
    "Live PR:",
    "PR Number:",
    "PR Stage 2 Sync:",
    "PR Readiness Stage 2 USER Approval:",
    "PR Merge Verification Pending",
    "Current PR Readiness Seam:",
    "PR Validation Pending",
    "Bot Review Signal Pending",
)

AUTOMATION_OBSERVABILITY_SOURCE = Path("dev/automation_observability_report.py")
AUTOMATION_OBSERVABILITY_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/codex_user_guide.md'), Path('Docs/orin_task_template.md'), Path('Docs/incident_patterns.md'), Path('Docs/branch_records/index.md'),)
AUTOMATION_OBSERVABILITY_PHRASES = (
    "Automation Observability",
    "dev/automation_observability_report.py",
    "Codex automation run/inbox",
    "$CODEX_HOME/automations/*/memory.md",
    "Automation CWD Worktree Mismatch",
    "BLOCKER_CANDIDATE",
    "REVIEW_REQUIRED",
)
AUTOMATION_OBSERVABILITY_SOURCE_PHRASES = (
    "Automation Observability Source-of-Truth Report",
    "automation_runs",
    "inbox_items",
    "memory.md",
    "configured cwd",
    "Lane-sensitive automation runs from neutral main",
    "neutral_main_background_observability_prompt",
    "fresh main equality before reporting blockers",
    "LEGACY_TOOLCHAIN_RUNTIME_FINDING_MARKERS",
    "legacy_toolchain_runtime_finding_is_retired",
    "BLOCKER_CANDIDATE",
    "REVIEW_REQUIRED",
    "--strict",
)

POST_MERGE_PR_BLOCKERS = (
    "PR Creation Pending",
    "PR creation pending",
    "PR Readiness Stage 1 Ready For Stage 2",
    "PR Readiness Stage 2 / PR creation remains pending",
    "PR Readiness Stage 2 / PR creation pending",
    "PR Creation Approval: Pending",
    "Stage 2 PR Creation: Pending",
    "PR Validation Pending",
    "PR State Unknown",
)

MERGE_STABLE_STALE_PRE_PR_PHRASES = (
    "pr creation pending",
    "pr readiness stage 1 ready for stage 2",
    "pr readiness stage 2 / pr creation remains pending",
    "pr readiness stage 2 / pr creation pending",
    "pr creation approval: pending",
    "stage 2 pr creation: pending",
    "no live pr",
)

MERGE_STABLE_STALE_CONTEXT_ALLOWLIST = (
    "historical pre-pr",
    "historical snapshot",
    "historical complete",
    "receipt evidence",
)

UTS_RESULTS_BLOCKER_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/user_test_summary_guidance.md'),)

UTS_RESULTS_BLOCKER_PHRASES = (
    "User Test Summary Results Pending",
    "User Test Summary Results:",
    "User Test Summary is exclusive to Live Validation Stage 1.",
    "Live Validation Stage 1 cannot enter Stage 2 until User Test Summary results are `PASS` or `WAIVED`",
    "Live Validation green requires an exact `## User Test Summary` state before final green.",
    "Every Live Validation digest must include an exact `## User Test Summary` section",
    "Final phase advancement is BLOCKED",
)

UTS_RESULTS_BLOCKER = "User Test Summary Results Pending"
UTS_RESULT_LABEL = "User Test Summary Results:"
UTS_WAIVER_REASON_LABEL = "User Test Summary Waiver Reason:"
UTS_RESULT_VALUES = ("PENDING", "PASS", "FAIL", "WAIVED")
UTS_CLEAR_RESULT_VALUES = ("PASS", "WAIVED")

USER_FACING_SHORTCUT_GATE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/user_test_summary_guidance.md'),)

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

CODEX_LIVE_CLIENT_SELF_QA_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/user_test_summary_guidance.md'),)

CODEX_LIVE_CLIENT_SELF_QA_PHRASES = (
    "Codex Live Client Self-QA Gate",
    "Codex Live Client Self-QA:",
    "Visual Quality:",
    "Live Interaction Evidence:",
    "Usability Check:",
    "Platform Uniformity Check:",
)

CODEX_LIVE_CLIENT_SELF_QA_BLOCKER = "Codex Live Client Self-QA Pending"
CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL = "Codex Live Client Self-QA:"
CODEX_LIVE_CLIENT_SELF_QA_WAIVER_REASON_LABEL = "Codex Live Client Self-QA Waiver Reason:"
CODEX_LIVE_CLIENT_SELF_QA_RESULT_VALUES = ("PENDING", "PASS", "FAIL", "WAIVED")
CODEX_LIVE_CLIENT_SELF_QA_CLEAR_VALUES = ("PASS", "WAIVED")
CODEX_LIVE_CLIENT_SELF_QA_REQUIRED_MARKERS = (
    "Live Client Entry Path:",
    "Evidence Screenshot:",
    "Visual Quality:",
    "Interaction Manifest:",
    "Interaction Evidence Root:",
    "Live Interaction Evidence:",
    "Usability Check:",
    "Interaction Check:",
    "Platform Uniformity Check:",
    "NDAI Naming Check:",
    "Cleanup Check:",
)

CODEX_VISUAL_ADJUDICATION_BLOCKER = "Codex Visual Adjudication Repair Pending"
CODEX_VISUAL_ADJUDICATION_RESULT_LABEL = "Codex Visual Adjudication:"
CODEX_VISUAL_ADJUDICATION_WAIVER_REASON_LABEL = "Codex Visual Adjudication Waiver Reason:"
CODEX_VISUAL_ADJUDICATION_RESULT_VALUES = ("PENDING", "PASS", "FAIL", "WAIVED")
CODEX_VISUAL_ADJUDICATION_CLEAR_VALUES = ("PASS", "WAIVED")
CODEX_VISUAL_ADJUDICATION_REQUIRED_MARKERS = (
    "Visual Artifact Review Scope:",
    "Per-Element Visual Inventory:",
    "Issue Form Coverage Matrix:",
    "OneDrive Focused Screenshot Proof:",
    "Product Vision Alignment:",
    "Per-Element Visual Verdicts:",
    "Helper Marker Limitation:",
    "Unacceptable UI Findings:",
    "LV1 Handoff Disposition:",
)

RELEASE_READINESS_TARGET_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'),)

RELEASE_READINESS_TARGET_PHRASES = (
    "Release Candidate Anchor:",
    "Release Candidate Anchor Source:",
    "Target Commit:",
    "Historical Endpoint Handling:",
    "Candidate Includes Later Governance Repairs:",
    "Release Window Contributor Inventory:",
    "Release Ownership Model:",
    "Release Window Contributors:",
    "Merged-Unreleased Scope Inventory:",
    "FAM Contributor Routing:",
    "Release Candidate Anchor Missing",
    "Release Window Contributor Inventory Missing",
    "Release Target Undefined",
    "Release Target:",
    "Release Floor:",
    "Version Rationale:",
    "Release Scope:",
    "Release Artifacts:",
    "Release Branch: No",
)

RELEASE_READINESS_SCOPE_DOCS = (Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'),)

RELEASE_READINESS_SCOPE_PHRASES = (
    "Release Readiness is not",
    "docs-sync",
)

RELEASE_READINESS_FILE_FREEZE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/incident_patterns.md'),)

RELEASE_READINESS_FILE_FREEZE_PHRASES = (
    "Release Readiness File Mutation Attempt",
    "analysis-only",
    "return to `PR Readiness`",
    "next legitimate runtime-focused backlog branch's `Branch Readiness`",
)

PROTECTED_MAIN_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/orin_task_template.md'), Path('Docs/codex_user_guide.md'), Path('Docs/closeout_guidance.md'), Path('Docs/incident_patterns.md'),)

PROTECTED_MAIN_PHRASES = (
    "main` is protected",
    "Main Write Attempt",
    "no emergency direct-main",
)

PROTECTED_MAIN_RELEASE_CLOSURE_DOCS = (Path('Docs/development_rules.md'), Path('Docs/branch_records/index.md'),)

PROTECTED_MAIN_RELEASE_CLOSURE_PHRASES = (
    "release execution and post-release canon closure are separate",
    "a local-only post-release closure commit is a blocker",
    "protected-main branch rejection must route to the next approved Branch Readiness Stage 2 canon/governance repair carrier",
    "post-release validation must compare published GitHub release/tag truth and release-body format against remote repo source truth",
    "runtime implementation remains blocked until release publication exists, post-release canon drift is explicitly recorded or repaired through the approved Branch Readiness carrier, and owning validation reports green",
)

POST_RELEASE_CLOSURE_DRIFT_MARKERS = (
    "Post-Release Canon Closure Drift: Recorded",
    "Closure Repair Surface: Next Branch Readiness Stage 2",
    "Closure Drift Scope: release-dependent fields only",
    "Implementation Entry: Blocked until closure repair validates green",
)

MERGED_UNRELEASED_CONTRACT_DOCS = (Path('Docs/development_rules.md'), Path('Docs/incident_patterns.md'),)

MERGED_UNRELEASED_CONTRACT_PHRASES = (
    "Merged-Unreleased Release-Debt Owner:",
    "Repo State: No Active Branch",
    "Release Target:",
    "Release Floor:",
    "Version Rationale:",
    "Release Scope:",
    "Release Artifacts:",
    "Post-Release Truth:",
)

MERGE_STABLE_CURRENT_STATE_DOCS = ()

MERGE_STABLE_CURRENT_STATE_PHRASES = (
    "merge-target pointer surfaces must be merge-stable",
    "Merge-target post-merge-stable authority projection is mandatory before PR green",
    "Docs/feature_backlog.md",
    "Docs/prebeta_roadmap.md",
    "canonical workstream `## Phase Status` block",
    "live PR state",
    "operator output",
    "explicit historical PR sections",
    "Current Branch Execution Posture",
    "PR Readiness State:",
    "Current Branch Objective:",
    "Active Workstream Chain:",
)

MERGE_STABLE_CURRENT_STATE_OWNER_MARKERS = (
    "PR Readiness State:",
    "Current Branch Objective:",
    "Active Workstream Chain:",
    "Post-Merge Review Repair Commit:",
    "Post-Merge Review Repair Commit On Main:",
    "Post-Merge Review Repair Scope:",
)

MERGE_STABLE_CURRENT_STATE_OWNER_BANNED_PHRASES = (
    " is open",
    "non-draft",
    "mergeable",
    "review-thread",
    "not contained on `main`",
    "this branch now carries",
    "branch-only",
    "follow-up blocker-clearing pr",
    "current blocker-clearing pr lane",
)

MERGE_STABLE_PHASE_STATUS_BANNED_PHRASES = (
    "repair branch after merge",
    "repair packaging commit after merge",
    "pr #",
    "open against `main`",
    "mergeable",
    "non-draft",
    "review-thread",
    "active seam:",
    "this bounded pr readiness pass",
    "branch-only",
    "not yet contained on `main`",
)

MERGE_STABLE_BRANCH_HEAD_PIN_PATTERNS = (
    re.compile(r"origin/[A-Za-z0-9._/-]+\s+(?:is|remains at)\s+`?[0-9a-f]{7,40}`?", re.IGNORECASE),
    re.compile(r"`origin/[A-Za-z0-9._/-]+`\s+(?:is|remains at)\s+`?[0-9a-f]{7,40}`?", re.IGNORECASE),
)

POST_MERGE_FOLD_DOWN_STALE_PATTERNS = (
    ("open PR state", re.compile(r"\bPR\s+#\d+\s+(?:is\s+)?open\b", re.IGNORECASE)),
    ("live PR state", re.compile(r"\bPR\s+#\d+\s+is\s+live\b", re.IGNORECASE)),
    ("live PR exists state", re.compile(r"\bLive\s+PR\s+#\d+\s+exists\b", re.IGNORECASE)),
    (
        "merge approval pending state",
        re.compile(r"\bopen\s+pending\s+separate\s+merge\s+approval\b", re.IGNORECASE),
    ),
    ("merge remains pending state", re.compile(r"\bmerge\s+remains\s+pending\b", re.IGNORECASE)),
    ("merge approval request", re.compile(r"\bApprove\s+merge\s+of\s+PR\s+#\d+\b", re.IGNORECASE)),
)

POST_MERGE_COMPACT_OWNER_STALE_PHRASES = (
    "successor setup is active",
    "active successor setup",
    "merge-stable handoff projection",
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
FEATURE_REPAIR_BRANCH_RE = re.compile(r"(?:origin/)?feature/[A-Za-z0-9._-]+")

FEATURE_BRANCH_REPAIR_CONTRACT_DOCS = (Path('Docs/development_rules.md'), Path('Docs/codex_modes.md'), Path('Docs/codex_user_guide.md'), Path('Docs/orin_task_template.md'), Path('Docs/branch_records/index.md'),)

FEATURE_BRANCH_REPAIR_CONTRACT_PHRASES = (
    "Standalone docs/governance, emergency canon repair, and repair-only feature branches are blocked for future Nexus work.",
    "Governance, docs, source-of-truth, and validator repairs must ride inside the next legitimate runtime-focused backlog branch during `Branch Readiness` or `PR Readiness`.",
    "If no runtime-focused branch is legally admitted yet, record the drift as a blocker and wait instead of creating a repair branch by inertia.",
    "Historical repair-only branch records remain traceability only and do not authorize new repair-only branch creation.",
)

BRANCH_RECORD_INDEX = Path("Docs/branch_records/index.md")

NEXT_WORKSTREAM_SELECTION_MARKER = "Next Workstream: Selected"
NEXT_WORKSTREAM_MINIMAL_SCOPE_LABEL = "Minimal Scope:"
BACKLOG_ADDITION_USER_APPROVAL_BLOCKER = "Backlog Addition User Approval Missing"
BACKLOG_EXHAUSTION_USER_DECISION_BLOCKER = "Backlog Exhaustion User Decision Pending"
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

BACKLOG_FAMILY_REFORM_BRANCH = "feature/backlog-family-governance-reform"
BACKLOG_FAMILY_REFORM_BRANCH_RECORD = Path(
    "Docs/branch_records/feature_backlog_family_governance_reform.md"
)
AUTOMATION_PLANNING_BRANCH = "feature/automation-planning"
AUTOMATION_PLANNING_BRANCH_RECORD = Path(
    "Docs/branch_records/feature_automation_planning.md"
)
AUTOMATION_CLOSEOUT_REPAIR_BRANCH = "feature/automation-planning-post-merge-closeout-repair"
AUTOMATION_CLOSEOUT_REPAIR_BRANCH_RECORD = Path(
    "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md"
)
PR101_CLOSEOUT_CANON_REPAIR_BRANCH = "feature/pr101-post-merge-closeout-canon-repair"
PR101_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD = Path(
    "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md"
)
PR102_CLOSEOUT_CANON_REPAIR_BRANCH = "feature/pr102-post-merge-closeout-canon-repair"
PR102_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD = Path(
    "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md"
)
PR103_CLOSEOUT_CANON_REPAIR_BRANCH = "feature/pr103-post-merge-closeout-canon-repair"
PR103_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD = Path(
    "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md"
)
AUTOMATION_CLOSEOUT_PR101_WATCHER_SCRIPT_PATH = (
    Path.home() / ".codex" / "watchers" / "pr101-watch.ps1"
)
AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH = (
    Path.home() / ".codex" / "watchers" / "pr101-watch-state.json"
)
AUTOMATION_CLOSEOUT_PR101_WATCHER_LATEST_PATH = (
    Path.home() / ".codex" / "watchers" / "pr101-watch-latest.txt"
)
AUTOMATION_CLOSEOUT_PR101_WATCHER_TASK_NAME = "Codex PR101 Watch"
PR101_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH = (
    Path.home() / ".codex" / "watchers" / "pr101-post-merge-closeout-canon-repair-watch.ps1"
)
PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH = (
    Path.home() / ".codex" / "watchers" / "pr101-post-merge-closeout-canon-repair-watch-state.json"
)
PR101_CLOSEOUT_CANON_WATCHER_LATEST_PATH = (
    Path.home() / ".codex" / "watchers" / "pr101-post-merge-closeout-canon-repair-watch-latest.txt"
)
PR101_CLOSEOUT_CANON_WATCHER_TASK_NAME = "Codex PR101 Post-Merge Closeout Canon Repair Watch"
PR102_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH = (
    Path.home()
    / ".codex"
    / "watchers"
    / "pr102-post-merge-closeout-canon-repair-watch-launcher.pyw"
)
PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH = (
    Path.home() / ".codex" / "watchers" / "pr102-post-merge-closeout-canon-repair-watch-state.json"
)
PR102_CLOSEOUT_CANON_WATCHER_LATEST_PATH = (
    Path.home() / ".codex" / "watchers" / "pr102-post-merge-closeout-canon-repair-watch-latest.txt"
)
PR102_CLOSEOUT_CANON_WATCHER_TASK_NAME = "Codex PR102 Post-Merge Closeout Canon Repair Watch"
PR103_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH = (
    Path.home()
    / ".codex"
    / "watchers"
    / "pr103-post-merge-closeout-canon-repair-watch-launcher.pyw"
)
PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH = (
    Path.home() / ".codex" / "watchers" / "pr103-post-merge-closeout-canon-repair-watch-state.json"
)
PR103_CLOSEOUT_CANON_WATCHER_LATEST_PATH = (
    Path.home() / ".codex" / "watchers" / "pr103-post-merge-closeout-canon-repair-watch-latest.txt"
)
PR103_CLOSEOUT_CANON_WATCHER_TASK_NAME = "Codex PR103 Post-Merge Closeout Canon Repair Watch"
CODEX_THREAD_STATE_DB_PATH = Path.home() / ".codex" / "state_5.sqlite"
REFORM_R3_S2_SEAM = (
    "Phase 3 - Family Anchor Migration / Slice R3-S2 - Map FB-043 through FB-048 under "
    "FB-042 as historical aliases"
)
REFORM_R3_S4_SEAM = (
    "Phase 3 - Family Anchor Migration / Slice R3-S4 - Map FB-036, FB-037, FB-038, and "
    "FB-041 under FB-027 as historical aliases"
)
REFORM_R3_S2_STATE_NEXT_PHRASE = (
    "Slice R3-S2 `Map FB-043 through FB-048 under FB-042 as historical aliases` is next"
)
REFORM_R3_S4_STATE_NEXT_PHRASE = (
    "Slice R3-S4 `Map FB-036, FB-037, FB-038, and FB-041 under FB-027 as historical aliases` "
    "is next"
)
REFORM_R3_S2_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 3 / Slice R3-S2 `Map FB-043 through FB-048 under FB-042 as historical aliases` "
    "is the next active seam on this branch."
)
REFORM_R3_S4_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 3 / Slice R3-S4 `Map FB-036, FB-037, FB-038, and FB-041 under FB-027 as "
    "historical aliases` is the next active seam on this branch."
)
REFORM_R3_S2_CONTINUATION_PHRASE = "Execute Slice R3-S2"
REFORM_R3_S4_CONTINUATION_PHRASE = "Execute Slice R3-S4"
REFORM_FB042_ALIAS_IDS = ("FB-043", "FB-044", "FB-045", "FB-046", "FB-047", "FB-048")
REFORM_FB027_ALIAS_IDS = ("FB-036", "FB-037", "FB-038", "FB-041")
REFORM_R4_S1_SEAM = (
    "Phase 4 - Lifetime Dossier Conversion / Slice R4-S1 - Convert the FB-042 dossier shell"
)
REFORM_R4_S1_STATE_NEXT_PHRASE = (
    "Slice R4-S1 `Convert the FB-042 dossier shell` is next"
)
REFORM_R4_S2_SEAM = (
    "Phase 4 - Lifetime Dossier Conversion / Slice R4-S2 - Convert the FB-027 dossier shell"
)
REFORM_R4_S2_STATE_NEXT_PHRASE = (
    "Slice R4-S2 `Convert the FB-027 dossier shell` is next"
)
REFORM_R4_S3_SEAM = (
    "Phase 4 - Lifetime Dossier Conversion / Slice R4-S3 - Add pass index and slice/seam ledger "
    "structure"
)
REFORM_R4_S3_STATE_NEXT_PHRASE = (
    "Slice R4-S3 `Add pass index and slice/seam ledger structure` is next"
)
REFORM_R4_S4_SEAM = (
    "Phase 4 - Lifetime Dossier Conversion / Slice R4-S4 - Add validator/helper and artifact "
    "indexes"
)
REFORM_R4_S4_STATE_NEXT_PHRASE = (
    "Slice R4-S4 `Add validator/helper and artifact indexes` is next"
)
REFORM_R4_S5_SEAM = (
    "Phase 4 - Lifetime Dossier Conversion / Slice R4-S5 - Dossier stability validation"
)
REFORM_R4_S5_STATE_NEXT_PHRASE = (
    "Slice R4-S5 `Dossier stability validation` is next"
)
REFORM_R5_S1_SEAM = (
    "Phase 5 - Historical Pass Record Conversion / Slice R5-S1 - Convert FB-043 through FB-048 "
    "workstream records"
)
REFORM_R5_S1_STATE_NEXT_PHRASE = (
    "Slice R5-S1 `Convert FB-043 through FB-048 workstream records` is next"
)
REFORM_R5_S1_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 5 / Slice R5-S1 `Convert FB-043 through FB-048 workstream records` is the next "
    "active seam on this branch."
)
REFORM_R5_S1_CONTINUATION_PHRASE = "Execute Slice R5-S1"
REFORM_R5_S2_SEAM = (
    "Phase 5 - Historical Pass Record Conversion / Slice R5-S2 - Convert FB-036, FB-037, "
    "FB-038, and FB-041 workstream records"
)
REFORM_R5_S2_STATE_NEXT_PHRASE = (
    "Slice R5-S2 `Convert FB-036, FB-037, FB-038, and FB-041 workstream records` is next"
)
REFORM_R5_S2_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 5 / Slice R5-S2 `Convert FB-036, FB-037, FB-038, and FB-041 workstream records` "
    "is the next active seam on this branch."
)
REFORM_R5_S2_CONTINUATION_PHRASE = "Execute Slice R5-S2"
REFORM_R5_S3_SEAM = (
    "Phase 5 - Historical Pass Record Conversion / Slice R5-S3 - Convert corresponding branch "
    "records"
)
REFORM_R5_S3_STATE_NEXT_PHRASE = "Slice R5-S3 `Convert corresponding branch records` is next"
REFORM_R5_S3_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 5 / Slice R5-S3 `Convert corresponding branch records` is the next active seam on "
    "this branch."
)
REFORM_R5_S3_CONTINUATION_PHRASE = "Execute Slice R5-S3"
REFORM_R5_S4_SEAM = (
    "Phase 5 - Historical Pass Record Conversion / Slice R5-S4 - Strip future-selection "
    "language from alias records"
)
REFORM_R5_S4_STATE_NEXT_PHRASE = (
    "Slice R5-S4 `Strip future-selection language from alias records` is next"
)
REFORM_R5_S4_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 5 / Slice R5-S4 `Strip future-selection language from alias records` is the next "
    "active seam on this branch."
)
REFORM_R5_S4_CONTINUATION_PHRASE = "Execute Slice R5-S4"
REFORM_R5_S5_SEAM = (
    "Phase 5 - Historical Pass Record Conversion / Slice R5-S5 - Traceability sweep"
)
REFORM_R5_S5_STATE_NEXT_PHRASE = "Slice R5-S5 `Traceability sweep` is next"
REFORM_R5_S5_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 5 / Slice R5-S5 `Traceability sweep` is the next active seam on this branch."
)
REFORM_R5_S5_CONTINUATION_PHRASE = "Execute Slice R5-S5"
REFORM_R6_S1_SEAM = (
    "Phase 6 - Roadmap And Index Alignment / Slice R6-S1 - Roadmap anchor conversion"
)
REFORM_R6_S1_STATE_NEXT_PHRASE = "Slice R6-S1 `Roadmap anchor conversion` is next"
REFORM_R6_S1_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 6 / Slice R6-S1 `Roadmap anchor conversion` is the next active seam on this branch."
)
REFORM_R6_S1_CONTINUATION_PHRASE = "Execute Slice R6-S1"
REFORM_R6_S2_SEAM = (
    "Phase 6 - Roadmap And Index Alignment / Slice R6-S2 - Workstream index split"
)
REFORM_R6_S2_STATE_NEXT_PHRASE = "Slice R6-S2 `Workstream index split` is next"
REFORM_R6_S2_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 6 / Slice R6-S2 `Workstream index split` is the next active seam on this branch."
)
REFORM_R6_S2_CONTINUATION_PHRASE = "Execute Slice R6-S2"
REFORM_R6_S3_SEAM = (
    "Phase 6 - Roadmap And Index Alignment / Slice R6-S3 - Main / router / loader alignment"
)
REFORM_R6_S3_STATE_NEXT_PHRASE = "Slice R6-S3 `Main / router / loader alignment` is next"
REFORM_R6_S3_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 6 / Slice R6-S3 `Main / router / loader alignment` is the next active seam on this branch."
)
REFORM_R6_S3_CONTINUATION_PHRASE = "Execute Slice R6-S3"
REFORM_R6_S4_SEAM = (
    "Phase 6 - Roadmap And Index Alignment / Slice R6-S4 - Selected-next truth validation"
)
REFORM_R6_S4_STATE_NEXT_PHRASE = "Slice R6-S4 `Selected-next truth validation` is next"
REFORM_R6_S4_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 6 / Slice R6-S4 `Selected-next truth validation` is the next active seam on this branch."
)
REFORM_R6_S4_CONTINUATION_PHRASE = "Execute Slice R6-S4"
REFORM_R6_S5_SEAM = (
    "Phase 6 - Roadmap And Index Alignment / Slice R6-S5 - Final drift sweep"
)
REFORM_R6_S5_STATE_NEXT_PHRASE = "Slice R6-S5 `Final drift sweep` is next"
REFORM_R6_S5_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 6 / Slice R6-S5 `Final drift sweep` is the next active seam on this branch."
)
REFORM_R6_S5_CONTINUATION_PHRASE = "Execute Slice R6-S5"
REFORM_R7_S1_SEAM = (
    "Phase 7 - Validator Finalization / Slice R7-S1 - Remove temporary dual-shape tolerance"
)
REFORM_R7_S1_STATE_NEXT_PHRASE = "Slice R7-S1 `Remove temporary dual-shape tolerance` is next"
REFORM_R7_S1_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 7 / Slice R7-S1 `Remove temporary dual-shape tolerance` is the next active seam on this branch."
)
REFORM_R7_S1_CONTINUATION_PHRASE = "Execute Slice R7-S1"
REFORM_R7_S2_SEAM = (
    "Phase 7 - Validator Finalization / Slice R7-S2 - Add hard anti-drift checks"
)
REFORM_R7_S2_STATE_NEXT_PHRASE = "Slice R7-S2 `Add hard anti-drift checks` is next"
REFORM_R7_S2_ACTIVE_SEAM_NEXT_PHRASE = (
    "Phase 7 / Slice R7-S2 `Add hard anti-drift checks` is the next active seam on this branch."
)
REFORM_R7_S2_CONTINUATION_PHRASE = "Execute Slice R7-S2"
REFORM_HARDENING_H1_SEAM = "Hardening H1 - Post-Workstream Governance Validation"
REFORM_HARDENING_H1_STATE_PHRASE = (
    "Hardening H1 `Post-Workstream Governance Validation` is in progress"
)
REFORM_LIVE_VALIDATION_LV1_SEAM = "Live Validation LV1 - Reform Branch Final Validation"
REFORM_LIVE_VALIDATION_LV1_STATE_PHRASE = (
    "Live Validation LV1 `Reform Branch Final Validation` is in progress"
)
REFORM_PR_READINESS_PR1_SEAM = "PR Readiness PR1 - Reform Branch PR Validation"
REFORM_PR_READINESS_PR1_STATE_PHRASE = (
    "PR Readiness PR1 `Reform Branch PR Validation` is in progress"
)
REFORM_PR_READINESS_PR2_SEAM = "PR Readiness PR2 - Bot Review Signal Monitoring"
REFORM_PR_READINESS_PR2_STATE_PHRASE = (
    "PR Readiness PR2 `Bot Review Signal Monitoring` is in progress"
)
REFORM_RELEASE_READINESS_RR1_SEAM = "Release Readiness RR1 - Reform Branch Release Validation"
REFORM_RELEASE_READINESS_RR1_STATE_PHRASE = (
    "Release Readiness RR1 `Reform Branch Release Validation` is in progress"
)
AUTOMATION_HARDENING_H1_SEAM = "Hardening H1 - Automation Catalog Validation"
AUTOMATION_HARDENING_H1_STATE_PHRASE = (
    "Hardening H1 `Automation Catalog Validation` is in progress"
)
AUTOMATION_LIVE_VALIDATION_LV1_SEAM = "Live Validation LV1 - Automation Catalog Final Validation"
AUTOMATION_LIVE_VALIDATION_LV1_STATE_PHRASE = (
    "Live Validation LV1 `Automation Catalog Final Validation` is in progress"
)
AUTOMATION_PR_READINESS_PR1_SEAM = "PR Readiness PR1 - Automation Catalog PR Validation"
AUTOMATION_PR_READINESS_PR1_STATE_PHRASE = (
    "PR Readiness PR1 `Automation Catalog PR Validation` is in progress"
)
AUTOMATION_CLOSEOUT_PR_READINESS_PR1_SEAM = (
    "PR Readiness PR1 - Post-Merge Closeout Repair PR Validation"
)
AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM = (
    "PR Readiness PR2 - Post-Merge Closeout Repair Merge Verification Watch"
)
AUTOMATION_CLOSEOUT_PR101_THREAD_WATCHER_NAME = "PR101 Same-Thread Merge Watch"
PR101_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM = (
    "PR Readiness PR1 - PR101 Post-Merge Closeout Canon Repair PR Validation"
)
PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM = (
    "PR Readiness PR2 - PR101 Post-Merge Closeout Canon Repair Merge Verification Watch"
)
PR101_CLOSEOUT_CANON_THREAD_WATCHER_NAME = "PR101 Post-Merge Closeout Canon Repair Same-Thread Watch"
PR102_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM = (
    "PR Readiness PR1 - PR102 Post-Merge Closeout Canon Repair PR Validation"
)
PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM = (
    "PR Readiness PR2 - PR102 Post-Merge Closeout Canon Repair Merge Verification Watch"
)
PR102_CLOSEOUT_CANON_THREAD_WATCHER_NAME = "PR102 Post-Merge Closeout Canon Repair Same-Thread Watch"
PR103_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM = (
    "PR Readiness PR1 - PR103 Post-Merge Closeout Canon Repair PR Validation"
)
PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM = (
    "PR Readiness PR2 - PR103 Post-Merge Closeout Canon Repair Merge Verification Watch"
)
PR103_CLOSEOUT_CANON_THREAD_WATCHER_NAME = "PR103 Post-Merge Closeout Canon Repair Same-Thread Watch"
CODEX_AUTOMATION_DB_PATH = Path.home() / ".codex" / "sqlite" / "codex-dev.db"
AUTOMATION_PR99_NATIVE_HEARTBEAT_PATH = (
    Path.home() / ".codex" / "automations" / "pr99-heartbeat-watch" / "automation.toml"
)
AUTOMATION_PR99_FALLBACK_SCRIPT_PATH = (
    Path.home() / ".codex" / "watchers" / "pr99-watch.ps1"
)
AUTOMATION_PR99_FALLBACK_STATE_PATH = (
    Path.home() / ".codex" / "watchers" / "pr99-watch-state.json"
)
AUTOMATION_PR99_FALLBACK_LATEST_PATH = (
    Path.home() / ".codex" / "watchers" / "pr99-watch-latest.txt"
)
AUTOMATION_PLANNING_RUNTIME_PROOF_REQUIRED_PHRASES = (
    "## Automation Runtime Proof And Fallback Contract",
    "`Automation Status: ACTIVE` is configuration state only; it is not run proof.",
    "Live automation proof requires at least one of: thread or inbox output, automation memory/log/state-file updates, or scheduler last-run evidence.",
    "If the preferred Codex heartbeat remains `ACTIVE` without run evidence, keep the owning phase blocked until native run evidence exists or a bounded fallback watcher is activated.",
    "Any bounded fallback watcher must be target-scoped to the live PR, phase-scoped to `PR Readiness`, read-only, and self-terminating or explicitly deleted when the PR becomes `merged` or `closed` or the branch leaves `PR Readiness`.",
    "`Release Window Sentinel` and `Post-Merge Closure Watch` may remain durable read-only waiting monitors outside their owned windows, but they must not create merge, release, or green authority by themselves.",
    "## Automation Reliability Disposition",
    "Toolchain Availability Watch Current Disposition: `Background observability only`",
    "Automation Drift Audit Current Disposition: `Background observability only`",
    "Legacy Runtime Path Expectation: `dev/i/runtime/service.py is retired historical automation truth, not current source truth`",
    "Current Source-Truth Requirement: `No current governance rule requires dev/i/runtime/service.py unless a future branch reintroduces it explicitly`",
    "Stale Automation Memory Handling: `Historical toolchain-path findings remain REVIEW_INFO unless current source truth still owns the referenced path`",
    "PR Readiness PR1 runtime-proof status:",
    "$CODEX_HOME/automations/pr99-heartbeat-watch/automation.toml",
    "$CODEX_HOME/watchers/pr99-watch.ps1",
    "pause or delete any native heartbeat instance that remains `ACTIVE` without run evidence once a bounded fallback or repaired native runtime path takes over",
    "delete any fallback helper immediately when the PR becomes `merged` or `closed` or the branch leaves `PR Readiness`",
    "Post-merge PR watcher fallback handling: any temporary PR-specific fallback helper must be removed or already self-terminated before this record becomes historical traceability only.",
)

BOT_REVIEW_SIGNAL_HEADING = "PR Bot Review Signal"
BOT_REVIEW_SIGNAL_STATUS_LABEL = "Bot Review Signal Status"
BOT_REVIEW_SIGNAL_HEAD_SHA_LABEL = "Bot Review Signal Head SHA"
BOT_REVIEW_SIGNAL_SOURCE_LABEL = "Bot Review Signal Source"
BOT_REVIEW_SIGNAL_TIMESTAMP_LABEL = "Bot Review Signal Timestamp"
BOT_REVIEW_SIGNAL_ACTOR_LABEL = "Bot Review Signal Actor"
BOT_REVIEW_SIGNAL_STATUS_PENDING = "Pending"
BOT_REVIEW_SIGNAL_STATUS_APPROVED = "Approved"
BOT_REVIEW_SIGNAL_STATUS_COMMENT_ADDRESSED = "Comment addressed"
BOT_REVIEW_BOT_LOGIN = "chatgpt-codex-connector[bot]"
BOT_REVIEW_GREEN_COMMENT_PHRASES = (
    "didn't find any major issues",
    "did not find any major issues",
)
BOT_REVIEW_COMMENT_CLOSEOUT_ALLOWED_FILES = {
    "Docs/Main.md",
    "Docs/closeout_guidance.md",
    "Docs/codex_modes.md",
    "Docs/codex_user_guide.md",
    "Docs/development_rules.md",
    "Docs/feature_backlog.md",
    "Docs/incident_patterns.md",
    "Docs/nexus_startup_contract.md",
    "Docs/orin_task_template.md",
    "Docs/phase_governance.md",
    "Docs/prebeta_roadmap.md",
    "Docs/workstreams/FB-027_interaction_system_baseline.md",
    "Docs/workstreams/FB-030_orin_voice_audio_direction_refinement.md",
    "dev/automation_observability_report.py",
    "dev/orin_branch_governance_validation.py",
    "dev/pr_same_thread_watcher.py",
}
BOT_REVIEW_COMMENT_CLOSEOUT_ALLOWED_PREFIXES = (
    "Docs/branch_records/",
)
REFORM_FB042_DOSSIER_PATH = Path(
    "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md"
)
REFORM_FB027_DOSSIER_PATH = Path(
    "Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md"
)
REFORM_FAMILY_DOSSIER_REQUIRED_HEADINGS = (
    "## Dossier Identity",
    "## Dossier Purpose",
    "## Current Dossier Status",
    "## Lifetime Tracking Scope",
    "## Historical Alias Coverage",
    "## Historical Anchor Record",
    "## Pass Index",
    "## Slice And Seam Ledger",
    "## Validator And Helper Index",
    "## Artifact Index",
    "## Migration Notes",
)
REFORM_FB042_DOSSIER_REQUIRED_PHRASES = (
    "Dossier State: `Structured shell with partial historical pass migration`",
    "Historical Content Migration: `In progress`",
    "Alias Record Conversion Status: `FB-043 through FB-048 workstream records converted in Slice R5-S1; corresponding preserved branch-readiness records converted in Slice R5-S3`",
    "Pass Index Status: `Populated for FB-043 through FB-048 in Slice R5-S1`",
    "Pass Index Population State: `FB-043 through FB-048 historical pass rows migrated; additional family migration remains pending`",
    "| Pass ID | Family Role | Source Record | Migration State | Notes |",
    "| `F042-P02` | `Historical pass alias` | `Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md` | `Converted in Slice R5-S1` | `Released in v1.6.8-prebeta; preserves the top-level entrypoint and explicit main.py handoff refinement chain.` |",
    "| `F042-P03` | `Historical pass alias` | `Docs/workstreams/FB-044_boot_desktop_handoff_outcome_refinement.md` | `Converted in Slice R5-S1` | `Released in v1.6.9-prebeta; preserves the desktop-settled handoff outcome refinement chain.` |",
    "| `F042-P04` | `Historical pass alias` | `Docs/workstreams/FB-045_active_session_relaunch_outcome_refinement.md` | `Converted in Slice R5-S1` | `Released in v1.6.9-prebeta; preserves the post-settled lifecycle classification follow-through for the same release package.` |",
    "| `F042-P05` | `Historical pass alias` | `Docs/workstreams/FB-046_active_session_relaunch_reacquisition.md` | `Converted in Slice R5-S1` | `Released in v1.6.10-prebeta; preserves accepted relaunch reacquisition and replacement-session settled re-entry proof.` |",
    "| `F042-P06` | `Historical pass alias` | `Docs/workstreams/FB-047_active_session_relaunch_decline_preservation.md` | `Converted in Slice R5-S1` | `Released in v1.6.11-prebeta; preserves decline-preservation and session-owner continuity proof.` |",
    "| `F042-P07` | `Historical pass alias` | `Docs/workstreams/FB-048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md` | `Converted in Slice R5-S1` | `Released in v1.6.12-prebeta; preserves accepted relaunch signal-failure and wait-timeout truth.` |",
    "Slice / Seam Ledger Status: `Populated for FB-043 through FB-048 in Slice R5-S1`",
    "Ledger Population State: `Historical summary rows added for FB-043 through FB-048; deeper family migration remains pending`",
    "| Phase / Slice | Seam / Scope | Classification | Migration State | Notes |",
    "| `FB-043 / WS-1, WS-2, H-1, LV-1, PR historical proof` | `Top-level entrypoint ownership and explicit main.py handoff refinement` | `Historical pass chain` | `Converted in Slice R5-S1` | `Detailed branch-local narrative stays in the preserved FB-043 workstream record.` |",
    "Validator / Helper Index Status: `Structure introduced in Slice R4-S4`",
    "Validator / Helper Index Population State: `No historical validator or helper entries migrated yet`",
    "| Surface | Classification | Source Record | Migration State | Notes |",
    "| `Placeholder only` | `Reserve rows for validator, helper, or harness history` | `Populate from existing historical workstream or branch records in later slices` | `Not started` | `R4-S4 adds shared validator/helper index structure only; no historical validator or helper entries migrate in this slice.` |",
    "Artifact Index Status: `Structure introduced in Slice R4-S4`",
    "Artifact Index Population State: `No historical artifact entries migrated yet`",
    "| Artifact Path | Classification | Source Record | Migration State | Notes |",
    "| `Placeholder only` | `Reserve rows for reusable evidence, report, or helper artifacts` | `Populate from existing historical workstream or branch records in later slices` | `Not started` | `R4-S4 adds shared artifact index structure only; no historical artifact entries migrate in this slice.` |",
    "Dossier Stability Validation Status: `Validated in Slice R4-S5`",
    "Current Alias Record Migration State: FB-043 through FB-048 now keep their existing historical workstream narratives as explicit FB-042 historical pass records, and the preserved corresponding branch-readiness records now carry matching historical pass identity after Slice R5-S3.",
    "R4-S1 intentionally does not migrate historical narrative, proof logs, pass summaries, or alias record bodies into the dossier.",
    "R4-S3 introduces pass index and slice/seam ledger templates only; it does not migrate historical pass rows, ledger rows, proof logs, or alias record bodies into the dossier.",
    "R4-S4 introduces validator/helper and artifact index templates only; it does not migrate historical validator rows, helper rows, artifact rows, proof logs, or alias record bodies into the dossier.",
    "R4-S5 validates that the FB-042 dossier shell, routing, and index-template surfaces remain stable after the Phase 4 structural slices, and it does so without migrating historical rows or narrative content.",
    "R5-S1 converts FB-043 through FB-048 workstream records into explicit FB-042 historical pass records and populates family pass-index plus slice/seam summary rows without migrating full narrative, validator/helper, artifact, or branch-record bodies into the dossier itself.",
    "R5-S3 converts the preserved FB-043 through FB-048 Branch Readiness records into matching FB-042 historical pass-record traceability without creating new branch records or migrating those branch-record bodies into the dossier itself.",
)
REFORM_FB027_DOSSIER_REQUIRED_PHRASES = (
    "Dossier State: `Structured shell with partial historical pass migration`",
    "Historical Content Migration: `In progress`",
    "Alias Record Conversion Status: `FB-036, FB-037, FB-038, and FB-041 workstream records converted in Slice R5-S2; preserved corresponding branch-record trace converted where it exists in Slice R5-S3`",
    "Pass Index Status: `Populated for FB-036, FB-037, FB-038, and FB-041 in Slice R5-S2`",
    "Pass Index Population State: `FB-036, FB-037, FB-038, and FB-041 historical pass rows migrated; additional family migration remains pending`",
    "| Pass ID | Family Role | Source Record | Migration State | Notes |",
    "| `F027-P02` | `Historical pass alias` | `Docs/workstreams/FB-036_saved_action_authoring.md` | `Converted in Slice R5-S2` | `Released in v1.3.0-prebeta; preserves bounded custom-task authoring, callable-group management, and exact-green validation hardening.` |",
    "| `F027-P03` | `Historical pass alias` | `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md` | `Converted in Slice R5-S2` | `Released in v1.3.1-prebeta; preserves deterministic callable-group execution follow-through and bounded runtime progression markers.` |",
    "| `F027-P04` | `Historical pass alias` | `Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md` | `Converted in Slice R5-S2` | `Released in v1.4.0-prebeta; preserves the first curated built-in catalog and settings expansion lane.` |",
    "| `F027-P05` | `Historical pass alias` | `Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md` | `Converted in Slice R5-S2` | `Released in v1.4.1-prebeta; preserves tray quick-task UX, tray-origin create flow, and window-initialization repair history.` |",
    "Slice / Seam Ledger Status: `Populated for FB-036, FB-037, FB-038, and FB-041 in Slice R5-S2`",
    "Ledger Population State: `Historical summary rows added for FB-036, FB-037, FB-038, and FB-041; deeper family migration remains pending`",
    "| Phase / Slice | Seam / Scope | Classification | Migration State | Notes |",
    "| `FB-036 / integrated implementation, hardening, interactive validation closeout` | `Saved-action authoring, callable-group management, inline group quick-create, and exact-green validation hardening` | `Historical pass chain` | `Converted in Slice R5-S2` | `Detailed branch-local narrative, artifacts, and interactive validation history stay in the preserved FB-036 workstream record.` |",
    "Validator / Helper Index Status: `Structure introduced in Slice R4-S4`",
    "Validator / Helper Index Population State: `No historical validator or helper entries migrated yet`",
    "| Surface | Classification | Source Record | Migration State | Notes |",
    "| `Placeholder only` | `Reserve rows for validator, helper, or harness history` | `Populate from existing historical workstream or branch records in later slices` | `Not started` | `R4-S4 adds shared validator/helper index structure only; no historical validator or helper entries migrate in this slice.` |",
    "Artifact Index Status: `Structure introduced in Slice R4-S4`",
    "Artifact Index Population State: `No historical artifact entries migrated yet`",
    "| Artifact Path | Classification | Source Record | Migration State | Notes |",
    "| `Placeholder only` | `Reserve rows for reusable evidence, report, or helper artifacts` | `Populate from existing historical workstream or branch records in later slices` | `Not started` | `R4-S4 adds shared artifact index structure only; no historical artifact entries migrate in this slice.` |",
    "Dossier Stability Validation Status: `Validated in Slice R4-S5`",
    "Current Alias Record Migration State: FB-036, FB-037, FB-038, and FB-041 now keep their existing historical workstream narratives as explicit FB-027 historical pass records; the preserved corresponding branch-record trace now carries matching historical pass identity where it exists, and FB-036, FB-038, and FB-041 do not have separate preserved branch-authority records to convert.",
    "R4-S2 intentionally does not migrate historical narrative, proof logs, pass summaries, or alias record bodies into the dossier.",
    "R4-S3 introduces pass index and slice/seam ledger templates only; it does not migrate historical pass rows, ledger rows, proof logs, or alias record bodies into the dossier.",
    "R4-S4 introduces validator/helper and artifact index templates only; it does not migrate historical validator rows, helper rows, artifact rows, proof logs, or alias record bodies into the dossier.",
    "R4-S5 validates that the FB-027 dossier shell, routing, and index-template surfaces remain stable after the Phase 4 structural slices, and it does so without migrating historical rows or narrative content.",
    "R5-S2 converts FB-036, FB-037, FB-038, and FB-041 workstream records into explicit FB-027 historical pass records and populates family pass-index plus slice/seam summary rows without migrating full narrative, validator/helper, artifact, or branch-record bodies into the dossier itself.",
    "R5-S3 converts the preserved corresponding branch-record trace where it exists for the FB-027 family, which currently means the FB-037 release-packaging record; FB-036, FB-038, and FB-041 do not have separate preserved branch-authority records to convert.",
)

REFORM_FB042_HISTORICAL_PASS_DOCS = {
    Path("Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md"): {
        "pass_id": "F042-P02",
        "branch_record": "Docs/branch_records/feature_fb_043_top_level_entrypoint_handoff_refinement.md",
    },
    Path("Docs/workstreams/FB-044_boot_desktop_handoff_outcome_refinement.md"): {
        "pass_id": "F042-P03",
        "branch_record": "Docs/branch_records/feature_fb_044_boot_desktop_handoff_outcome_refinement.md",
    },
    Path("Docs/workstreams/FB-045_active_session_relaunch_outcome_refinement.md"): {
        "pass_id": "F042-P04",
        "branch_record": "Docs/branch_records/feature_fb_045_active_session_relaunch_stability.md",
    },
    Path("Docs/workstreams/FB-046_active_session_relaunch_reacquisition.md"): {
        "pass_id": "F042-P05",
        "branch_record": "Docs/branch_records/feature_fb_046_active_session_relaunch_reacquisition.md",
    },
    Path("Docs/workstreams/FB-047_active_session_relaunch_decline_preservation.md"): {
        "pass_id": "F042-P06",
        "branch_record": "Docs/branch_records/feature_fb_047_active_session_relaunch_decline_preservation.md",
    },
    Path("Docs/workstreams/FB-048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md"): {
        "pass_id": "F042-P07",
        "branch_record": "Docs/branch_records/feature_fb_048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md",
    },
}

REFORM_FB027_HISTORICAL_PASS_DOCS = {
    Path("Docs/workstreams/FB-036_saved_action_authoring.md"): {
        "pass_id": "F027-P02",
        "branch_record_phrase": "Historical Branch Record Preservation: `No separate historical branch-authority record is preserved for FB-036; this workstream remains the authoritative branch-local historical record.`",
    },
    Path("Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md"): {
        "pass_id": "F027-P03",
        "branch_record_phrase": "Historical Branch Record Preservation: `No separate historical branch-authority record is preserved for FB-041; this workstream remains the authoritative branch-local historical record.`",
    },
    Path("Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md"): {
        "pass_id": "F027-P04",
        "branch_record_phrase": "Historical Branch Record Preservation: `No separate implementation branch-authority record is preserved for FB-037; release-packaging authority remains in Docs/branch_records/codex_fb_037_release_debt_packaging.md.`",
    },
    Path("Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md"): {
        "pass_id": "F027-P05",
        "branch_record_phrase": "Historical Branch Record Preservation: `No separate historical branch-authority record is preserved for FB-038; this workstream remains the authoritative branch-local historical record.`",
    },
}

REFORM_HISTORICAL_PASS_BRANCH_RECORDS = {
    Path("Docs/branch_records/feature_fb_043_top_level_entrypoint_handoff_refinement.md"): {
        "family_anchor_id": "FB-042",
        "family_dossier": "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md",
        "pass_id": "F042-P02",
        "workstream_record": "Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md",
        "preservation_rule": "This record keeps the preserved branch-readiness trace for the historical pass; the family dossier owns cross-pass indexing.",
    },
    Path("Docs/branch_records/feature_fb_044_boot_desktop_handoff_outcome_refinement.md"): {
        "family_anchor_id": "FB-042",
        "family_dossier": "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md",
        "pass_id": "F042-P03",
        "workstream_record": "Docs/workstreams/FB-044_boot_desktop_handoff_outcome_refinement.md",
        "preservation_rule": "This record keeps the preserved branch-readiness trace for the historical pass; the family dossier owns cross-pass indexing.",
    },
    Path("Docs/branch_records/feature_fb_045_active_session_relaunch_stability.md"): {
        "family_anchor_id": "FB-042",
        "family_dossier": "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md",
        "pass_id": "F042-P04",
        "workstream_record": "Docs/workstreams/FB-045_active_session_relaunch_outcome_refinement.md",
        "preservation_rule": "This record keeps the preserved branch-readiness trace for the historical pass; the family dossier owns cross-pass indexing.",
    },
    Path("Docs/branch_records/feature_fb_046_active_session_relaunch_reacquisition.md"): {
        "family_anchor_id": "FB-042",
        "family_dossier": "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md",
        "pass_id": "F042-P05",
        "workstream_record": "Docs/workstreams/FB-046_active_session_relaunch_reacquisition.md",
        "preservation_rule": "This record keeps the preserved branch-readiness trace for the historical pass; the family dossier owns cross-pass indexing.",
    },
    Path("Docs/branch_records/feature_fb_047_active_session_relaunch_decline_preservation.md"): {
        "family_anchor_id": "FB-042",
        "family_dossier": "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md",
        "pass_id": "F042-P06",
        "workstream_record": "Docs/workstreams/FB-047_active_session_relaunch_decline_preservation.md",
        "preservation_rule": "This record keeps the preserved branch-readiness trace for the historical pass; the family dossier owns cross-pass indexing.",
    },
    Path("Docs/branch_records/feature_fb_048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md"): {
        "family_anchor_id": "FB-042",
        "family_dossier": "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md",
        "pass_id": "F042-P07",
        "workstream_record": "Docs/workstreams/FB-048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md",
        "preservation_rule": "This record keeps the preserved branch-readiness trace for the historical pass; the family dossier owns cross-pass indexing.",
    },
    Path("Docs/branch_records/codex_fb_037_release_debt_packaging.md"): {
        "family_anchor_id": "FB-027",
        "family_dossier": "Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md",
        "pass_id": "F027-P04",
        "workstream_record": "Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md",
        "preservation_rule": "This record keeps the preserved release-packaging trace for the historical pass; the family dossier owns cross-pass indexing.",
    },
}

REFORM_R5_S4_HISTORICAL_LANGUAGE_DOCS = {
    Path("Docs/feature_backlog.md"): {
        "required": (
            "later runtime-family continuation moved through FB-048 on `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth` while this alias entry remained released historical proof.",
        ),
        "prohibited": (
            "Post-Release Truth: FB-047 is Released / Closed in `v1.6.11-prebeta`; release debt is clear; and FB-048 is now the active promoted workstream on `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth`.",
        ),
    },
    Path("Docs/prebeta_roadmap.md"): {
        "required": (
            "later runtime-family continuation moved through FB-048 on `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth`, which later completed its own released historical pass.",
            "Historical follow-through at that release boundary: FB-044 Boot-to-desktop handoff outcome refinement.",
        ),
        "prohibited": (
            "phase status: Released / Closed in `v1.6.11-prebeta`; PR #93 merged into `main` at `4ca70572fbc8033bc96fcd299dd309464e81393a`; the release is live on the same commit; release debt is clear; and FB-048 is now the active promoted workstream on `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth` with WS-1 complete / validated.",
            "Post-Release Truth: FB-047 is Released / Closed in `v1.6.11-prebeta`; release debt is clear; and FB-048 is now the active promoted workstream on `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth`.",
            "phase status: Released / Closed in `v1.6.10-prebeta`; PR #92 merged into `main` at `36cf07495dc8e239b20b11afb5194355b77ffd8b`; the release is live on the same commit; FB-047 is now Released / Closed in `v1.6.11-prebeta`; release debt is clear; and FB-048 is the active promoted workstream on `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth`.",
            "Post-Release Truth: FB-046 is Released / Closed in `v1.6.10-prebeta`; FB-047 is Released / Closed in `v1.6.11-prebeta`; release debt is clear; and FB-048 is the active promoted workstream on `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth`.",
            "Current Active Workstream: FB-044 Boot-to-desktop handoff outcome refinement.",
        ),
    },
    Path("Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md"): {
        "required": (
            "Historical Selected-Next At Release Time: FB-039 External trigger and plugin integration architecture.",
        ),
        "prohibited": (
            "Selected Next Workstream: FB-039 External trigger and plugin integration architecture.",
        ),
    },
    Path("Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md"): {
        "required": (
            "Historical Selected-Next At Release Time: FB-044 Boot-to-desktop handoff outcome refinement",
            "Historical successor state after merge: FB-044 remained selected next, `Registry-only`, and branch-not-created until `v1.6.8-prebeta` was published, validated, updated `main` was revalidated, and bounded Branch Readiness admitted the first runtime/back-end slice.",
            "Historical Selected-Next At PR Package Time: FB-044 Boot-to-desktop handoff outcome refinement.",
        ),
        "prohibited": (
            "Selected Next Workstream:",
            "Selected Next Basis:",
            "Selected Next Record State At PR Package Time:",
            "Selected Next Implementation Branch At PR Package Time:",
            "Successor state after merge:",
        ),
    },
    Path("Docs/workstreams/FB-044_boot_desktop_handoff_outcome_refinement.md"): {
        "required": (
            "Historical Selected-Next At Release Time: FB-045 Active-session relaunch outcome refinement",
            "Historical successor state after merge: FB-045 remained selected next, `Registry-only`, and branch-not-created until `v1.6.9-prebeta` was published, validated, updated `main` was revalidated, and bounded Branch Readiness admitted the first runtime/user-facing relaunch slice.",
            "Historical Selected-Next At PR Package Time: FB-045 Active-session relaunch outcome refinement.",
        ),
        "prohibited": (
            "Selected Next Workstream:",
            "Selected Next Basis:",
            "Selected Next Record State At PR Package Time:",
            "Selected Next Implementation Branch At PR Package Time:",
            "Successor state after merge:",
        ),
    },
    Path("Docs/workstreams/FB-045_active_session_relaunch_outcome_refinement.md"): {
        "required": (
            "Historical Selected-Next At Release Time: FB-046 Active-session relaunch reacquisition and settled re-entry proof",
            "Historical successor state after merge: FB-046 remained selected next, `Registry-only`, and branch-not-created until `v1.6.9-prebeta` was published, validated, updated `main` was revalidated, and bounded Branch Readiness admitted the first relaunch-reacquisition slice.",
            "Historical Selected-Next At PR Package Time: FB-046 Active-session relaunch reacquisition and settled re-entry proof.",
        ),
        "prohibited": (
            "Selected Next Workstream:",
            "Selected Next Basis:",
            "Selected Next Record State At PR Package Time:",
            "Selected Next Implementation Branch At PR Package Time:",
            "Successor state after merge:",
        ),
    },
    Path("Docs/workstreams/FB-046_active_session_relaunch_reacquisition.md"): {
        "required": (
            "Historical Selected-Next At Release Time: FB-047 Active-session relaunch decline session-preservation proof",
            "Historical successor state after merge: FB-047 remained selected next, `Registry-only`, and branch-not-created until `v1.6.10-prebeta` was published, validated, updated `main` was revalidated, and bounded Branch Readiness admitted the first relaunch-decline preservation slice.",
            "Historical Selected-Next At PR Package Time: FB-047 Active-session relaunch decline session-preservation proof.",
        ),
        "prohibited": (
            "Selected Next Workstream:",
            "Selected Next Basis:",
            "Selected Next Record State At PR Package Time:",
            "Selected Next Implementation Branch At PR Package Time:",
            "Successor state after merge:",
        ),
    },
    Path("Docs/workstreams/FB-047_active_session_relaunch_decline_preservation.md"): {
        "required": (
            "Historical Selected-Next At Release Time: FB-048 Active-session relaunch signal-failure and wait-timeout truth",
            "Historical successor state after merge: FB-048 later became the promoted follow-through workstream on `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth`, where WS-1, H-1, LV-1, and PR Readiness later completed before release closure.",
            "Historical Selected-Next At PR Package Time: FB-048 Active-session relaunch signal-failure and wait-timeout truth.",
        ),
        "prohibited": (
            "Selected Next Workstream:",
            "Selected Next Basis:",
            "Selected Next Record State At PR Package Time:",
            "Selected Next Implementation Branch At PR Package Time:",
            "Successor state after merge:",
        ),
    },
    Path("Docs/workstreams/FB-048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md"): {
        "required": (
            "Historical Selected-Next At Release Time: FB-049 Active-session pre-settled incoming-launch conflict truth",
            "Historical successor state after merge: FB-049 remained selected next, `Registry-only`, and branch-not-created until `v1.6.12-prebeta` was published, validated, updated `main` was revalidated, and bounded Branch Readiness admitted the first pre-settled incoming-launch conflict truth slice.",
            "Historical Selected-Next At PR Package Time: FB-049 Active-session pre-settled incoming-launch conflict truth.",
        ),
        "prohibited": (
            "Selected Next Workstream:",
            "Selected Next Basis:",
            "Selected Next Record State At PR Package Time:",
            "Selected Next Implementation Branch At PR Package Time:",
            "Successor state after merge:",
        ),
    },
    Path("Docs/branch_records/feature_fb_048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md"): {
        "required": (
            "FB-048 later promoted into the canonical workstream on the same branch; this record remains historical Branch Readiness traceability only.",
        ),
        "prohibited": (
            "FB-048 is now the active promoted workstream on the same branch; this record remains historical Branch Readiness traceability only.",
        ),
    },
}

REFORM_R5_S5_TRACEABILITY_REQUIRED_PHRASES = {
    Path("Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md"): (
        "Preserved Branch Trace Status: `Populated in Slice R5-S5`",
        "Trace Index Population State: `All converted FB-042 pass records now point to the preserved branch-readiness trace that exists for each pass`",
        "| `F042-P02` | `Docs/branch_records/feature_fb_043_top_level_entrypoint_handoff_refinement.md` | `Indexed in Slice R5-S5` | `Preserved Branch Readiness trace for the first post-anchor runtime follow-through.` |",
        "| `F042-P07` | `Docs/branch_records/feature_fb_048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md` | `Indexed in Slice R5-S5` | `Preserved Branch Readiness trace for the accepted-failure and wait-timeout truth pass.` |",
        "R5-S5 completes the Phase 5 traceability sweep by indexing the preserved FB-043 through FB-048 branch-readiness traces directly in the family dossier and confirming the dossier, backlog, roadmap, alias workstream, and branch-record routing stay aligned without migrating narrative bodies.",
    ),
    Path("Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md"): (
        "Preserved Branch Trace Status: `Populated in Slice R5-S5`",
        "Trace Index Population State: `Converted FB-027 pass records now explicitly show where preserved branch-record trace exists and where no separate branch record exists`",
        "| `F027-P02` | `None preserved` | `Confirmed in Slice R5-S5` | `FB-036 does not have a separate preserved branch-authority record beyond the canonical workstream history.` |",
        "| `F027-P04` | `Docs/branch_records/codex_fb_037_release_debt_packaging.md` | `Indexed in Slice R5-S5` | `Preserved release-packaging trace for the FB-037 historical pass.` |",
        "R5-S5 completes the Phase 5 traceability sweep by indexing the preserved FB-037 branch-record trace, explicitly calling out the passes that do not have separate branch records, and confirming the dossier, backlog, roadmap, alias workstream, and branch-record routing stay aligned without migrating narrative bodies.",
    ),
}

REFORM_R6_S1_ROADMAP_REQUIRED_PHRASES = (
    "- historical pass coverage: `FB-043`, `FB-044`, `FB-045`, `FB-046`, `FB-047`, `FB-048`",
    "- historical pass coverage: `FB-036`, `FB-037`, `FB-038`, `FB-041`",
    "pass id: `F042-P07`",
    "pass id: `F042-P06`",
    "pass id: `F042-P05`",
    "pass id: `F042-P04`",
    "pass id: `F042-P03`",
    "pass id: `F042-P02`",
    "pass id: `F027-P05`",
    "pass id: `F027-P04`",
    "pass id: `F027-P03`",
    "pass id: `F027-P02`",
    "Phase 5 / Slice R5-S5 indexed the preserved branch trace; validator/helper and artifact migration remain pending",
)

REFORM_R6_S2_INDEX_REQUIRED_PHRASES = (
    "### Family Anchor Records",
    "- `Docs/workstreams/FB-042_desktop_entrypoint_runtime_refinement.md`",
    "- `Docs/workstreams/FB-027_interaction_system_baseline.md`",
    "### Historical Pass Alias Records",
    "#### FB-042 Family",
    "- `Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md`",
    "- `Docs/workstreams/FB-048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md`",
    "#### FB-027 Family",
    "- `Docs/workstreams/FB-036_saved_action_authoring.md`",
    "- `Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md`",
    "### Other Closed Workstreams",
    "- `Docs/workstreams/FB-005_workspace_and_folder_organization.md`",
    "- `Docs/workstreams/FB-035_release_context_fallback_hardening.md`",
)

REFORM_R6_S3_ROUTER_REQUIRED_PHRASES = {}

CURRENT_BACKLOG_SHAPE_HEADINGS = (
    "## Registry Items",
    "## Closed Canonical Workstreams",
)

REFORM_BACKLOG_SHAPE_HEADINGS = (
    "### User-Facing Feature Families",
    "### Historical Consolidated Pass Aliases",
    "### Support / Architecture / Governance Lanes",
    "## Historical Implemented Registry-Only Items",
)

REFORM_BACKLOG_TRIGGER_HEADINGS = (
    "### User-Facing Feature Families",
    "### Historical Consolidated Pass Aliases",
    "### Support / Architecture / Governance Lanes",
)

REFORM_BACKLOG_ORDERED_HEADINGS = (
    "### User-Facing Feature Families",
    "### Historical Consolidated Pass Aliases",
    "### Support / Architecture / Governance Lanes",
    "## Historical Implemented Registry-Only Items",
)

TRANSITIONAL_CURRENT_REGISTRY_ORDER_HEADING = "### Transitional Current Registry Order"

REFORM_BACKLOG_SECTION_CLASS_RULES = (
    ("User-Facing Feature Families", "Feature Family"),
    ("Historical Consolidated Pass Aliases", "Historical Pass Alias"),
    ("Support / Architecture / Governance Lanes", "Support Lane"),
)

REFORM_BACKLOG_SECTION_NEXT_HEADINGS = {
    "User-Facing Feature Families": "### Historical Consolidated Pass Aliases",
    "Historical Consolidated Pass Aliases": "### Support / Architecture / Governance Lanes",
    "Support / Architecture / Governance Lanes": "## Historical Implemented Registry-Only Items",
}

CURRENT_WORKSTREAM_INDEX_SHAPE_HEADINGS = (
    "### Active",
    "### Merged / Release Debt Owners",
    "### Closed",
)

REFORM_WORKSTREAM_INDEX_SHAPE_HEADINGS = (
    "### Family Anchor Records",
    "### Historical Pass Alias Records",
    "### Other Closed Workstreams",
)

REFORM_WORKSTREAM_ACTIVE_HEADINGS = (
    "Active",
)

REFORM_WORKSTREAM_CLOSED_HEADINGS = (
    "Closed",
    "Family Anchor Records",
    "Historical Pass Alias Records",
    "Other Closed Workstreams",
)

REFORM_WORKSTREAM_RELEASE_DEBT_HEADINGS = (
    "Merged / Release Debt Owners",
)

VALID_BACKLOG_REGISTRY_CLASSES = (
    "Feature Family",
    "Historical Pass Alias",
    "Support Lane",
    "Historical Implemented Registry-Only",
)

FRESH_FAMILY_PREFIX = "FAM-"
FRESH_FAMILY_TAXONOMY = {
    "FAM-001": {
        "title": "Boot Interface",
        "package": "PKG-001",
        "legacy": ("FB-042", "FB-043", "FB-044", "FB-045", "FB-046", "FB-047", "FB-048", "FB-049"),
    },
    "FAM-002": {
        "title": "Desktop Interface",
        "package": "PKG-002",
        "legacy": ("FB-031",),
    },
    "FAM-003": {
        "title": "Interaction and Actions",
        "package": "PKG-003",
        "legacy": ("FB-027", "FB-036", "FB-037", "FB-038", "FB-041"),
    },
    "FAM-004": {
        "title": "Voice and Audio",
        "package": "PKG-004",
        "legacy": ("FB-030",),
    },
    "FAM-005": {
        "title": "External Integrations",
        "package": "PKG-005",
        "legacy": ("FB-039",),
    },
    "FAM-006": {
        "title": "Monitoring and HUD",
        "package": "PKG-006",
        "legacy": ("FB-040",),
    },
    "FAM-007": {
        "title": "Local AI and Capability Packs",
        "package": "PKG-007",
        "legacy": (),
    },
    "FAM-008": {
        "title": "Packaging and Install Experience",
        "package": "PKG-008",
        "legacy": (),
    },
}

FRESH_FAMILY_NAMESPACE_REQUIRED_PHRASES = (
    "The old `FB-###` namespace is historical-only after this one-time repair; live backlog-family identities use `FAM-###`, starting at `FAM-001`, and Codex must not create or reuse a parseable `FB-###` backlog ID.",
    "Selectable user-facing feature-family records now use the fresh `FAM-###` namespace in ascending order from `FAM-001`; the current registry ends at `FAM-008` unless USER approves a later backlog-family admission.",
    "Live backlog-family identities use the fresh broad `FAM-###` namespace starting at `FAM-001`; legacy `FB-###` IDs are historical trace only and must not be reused for new parseable backlog entries. Because the current registry ends at `FAM-008`, the next USER-approved backlog family may use `FAM-009`.",
    "Only true broad feature-family backlog entries should remain as parseable `### [ID: FAM-XXX]` backlog records by default.",
    "The live backlog-family namespace is broad `FAM-###`, starting at `FAM-001`; the current admitted registry ends at `FAM-008`, and the old `FB-###` namespace is historical-only and must not be reused for parseable backlog entries.",
)

FAMILY_PACKAGE_MODEL_REQUIRED_PHRASES = (
    "Canonical Identity Model: `FAM` = broad long-lived product family; `Package` = bulk branch/release package under one family; `Slice` = traceable deliverable area inside a package; `Seam` = execution or validation checkpoint; `PR` = merge/review evidence only; legacy global `FB` = historical trace only.",
    "Branch Scope Standard: branches must package multiple related admitted slices under exactly one broad family by default.",
    "Package Completion Standard: Workstream continues through every admitted package slice until `Package Completion State: Complete`, `Released Baseline / Open`, `Blocked`, or `Deferred` is truthfully recorded before Hardening admission.",
    "Admitted Slice Counting Rule: only rows with `Admission State` equal to `Admitted` count toward a package's admitted-slice total.",
    "Concrete Admitted Slice Rule: an admitted slice must have a concrete scoped deliverable, `Package ID`, `FAM ID`, `Slice Status`, `Completion State`, and `Seam Trace`; vague pending/future placeholder rows cannot be marked admitted.",
    "Package Completion Guard: `Package Completion State: Complete` is blocked while any admitted slice remains incomplete, and completing one admitted slice cannot authorize stopping while another admitted slice remains incomplete.",
    "PR Evidence Standard: PR numbers are evidence only and must not become backlog identities, package identities, release-version drivers, or selected-next successors.",
    "single-slice packages are blocked by `Single-Slice Package User Approval Missing` unless explicit USER approval records `Single-Slice Package User Approval: Granted`",
    "package slices must trace to exactly one FAM and exactly one package",
)

ADMITTED_SLICE_STATE = "admitted"
NON_ADMITTED_SLICE_STATES = {
    "historical evidence",
    "merged evidence",
    "future placeholder",
    "deferred placeholder",
}
PLACEHOLDER_SLICE_MARKERS = (
    "future package",
    "future branch readiness",
    "pending user-approved",
    "deferred user-approved",
    "placeholder",
    "future-dependent",
)
SLICE_TERMINAL_COMPLETION_STATES = {
    "complete",
    "released baseline / open",
    "merged historical evidence",
    "merged unreleased",
    "deferred",
    "blocked",
}
PACKAGE_COMPLETE_STATES = {
    "complete",
    "implemented complete",
}

LEGACY_FEATURE_FAMILY_IDS = tuple(
    dict.fromkeys(
        legacy_id
        for family in FRESH_FAMILY_TAXONOMY.values()
        for legacy_id in family["legacy"]
    )
)

CONSOLIDATED_SUPPORT_TRACE_IDS = (
    "FB-035",
    "FB-034",
    "FB-033",
    "FB-032",
    "FB-029",
    "FB-028",
    "FB-025",
    "FB-015",
    "FB-005",
    "FB-004",
)

CONSOLIDATED_HISTORICAL_REGISTRY_ONLY_IDS = (
    "FB-001",
    "FB-002",
    "FB-003",
    "FB-006",
    "FB-007",
    "FB-008",
    "FB-009",
    "FB-010",
    "FB-011",
    "FB-012",
    "FB-013",
    "FB-014",
    "FB-016",
    "FB-017",
    "FB-018",
    "FB-019",
    "FB-020",
    "FB-021",
    "FB-022",
    "FB-023",
    "FB-024",
    "FB-026",
)

CONSOLIDATED_TRACE_BACKLOG_IDS = (
    *LEGACY_FEATURE_FAMILY_IDS,
    *REFORM_FB042_ALIAS_IDS,
    *REFORM_FB027_ALIAS_IDS,
    *CONSOLIDATED_SUPPORT_TRACE_IDS,
    *CONSOLIDATED_HISTORICAL_REGISTRY_ONLY_IDS,
)

CONSOLIDATED_BACKLOG_TRACE_REQUIRED_PHRASES = (
    "historical pass aliases, support/governance lanes, and old registry-only implemented records are trace tables, not backlog items",
    "Former standalone historical pass backlog entries now live here as family traceability only.",
    "| `FB-048` | `F042-P07` | `FB-042` | `Docs/workstreams/FB-048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md` | `Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md` | `v1.6.12-prebeta` | Historical family pass only; not selectable |",
    "| `FB-043` | `F042-P02` | `FB-042` | `Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md` | `Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md` | `v1.6.8-prebeta` | Historical family pass only; not selectable |",
    "| `FB-041` | `F027-P03` | `FB-027` | `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md` | `Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md` | `v1.3.1-prebeta` | Historical family pass only; not selectable |",
    "| `FB-038` | `F027-P05` | `FB-027` | `Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md` | `Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md` | `v1.4.1-prebeta` | Historical family pass only; not selectable |",
    "| `FB-036` | `F027-P02` | `FB-027` | `Docs/workstreams/FB-036_saved_action_authoring.md` | `Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md` | `v1.3.0-prebeta` | Historical family pass only; not selectable |",
    "Closed support, architecture, and governance lanes are historical traceability only.",
    "| `FB-035` | Support-report release-context fallback hardening | `Docs/workstreams/FB-035_release_context_fallback_hardening.md` | `v1.2.7-prebeta` | Closed support lane trace |",
    "| `FB-032` | Nexus-era vision and source-of-truth migration | `Docs/workstreams/FB-032_nexus_era_vision_and_source_of_truth_migration.md` | `v1.6.2-prebeta` | Closed architecture/governance trace |",
    "| `FB-004` | Future boot orchestrator layer | `Docs/workstreams/FB-004_future_boot_orchestrator_layer.md` | `v1.6.3-prebeta` | Closed architecture trace |",
    "Old implemented registry-only IDs are preserved as same-file historical trace.",
    "| `FB-001` | Repeated identical crash early escalation | Implemented `v1.6.0` | Historical registry trace in `Docs/feature_backlog.md` |",
    "| `FB-026` | Dev Toolkit uploaded-bundle intake surface | Implemented `v2.2.0` | Historical registry trace in `Docs/feature_backlog.md` |",
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


def _has_all_headings(text: str, headings: tuple[str, ...]) -> bool:
    return all(heading in text for heading in headings)


def _has_any_heading(text: str, headings: tuple[str, ...]) -> bool:
    return any(heading in text for heading in headings)


def _collect_index_paths_from_headings(text: str, headings: tuple[str, ...]) -> set[str]:
    paths: set[str] = set()
    for heading in headings:
        paths.update(re.findall(r"Docs/workstreams/[A-Za-z0-9._-]+\.md", _subsection(text, heading)))
    return paths


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
    matches = list(
        re.finditer(r"^### \[ID: (?P<id>[A-Z]+-\d+)\] (?P<title>.+)$", text, flags=re.M)
    )
    for match in matches:
        start = match.start()
        next_heading = re.search(r"(?m)^(?:## |### )", text[match.end() :])
        end = match.end() + next_heading.start() if next_heading else len(text)
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


def _parse_backlog_subsection(text: str, heading_prefix: str) -> list[dict[str, str]]:
    heading = f"### {heading_prefix}"
    start = text.find(heading)
    if start < 0:
        return []
    start = text.find("\n", start)
    if start < 0:
        return []
    start += 1

    next_heading = REFORM_BACKLOG_SECTION_NEXT_HEADINGS.get(heading_prefix)
    end = text.find(next_heading, start) if next_heading else -1
    if end < 0:
        end = len(text)

    return _parse_backlog_sections(text[start:end])


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


def _extract_colon_values(block: str, label: str) -> list[str]:
    return [match.strip() for match in re.findall(rf"^{re.escape(label)}:\s*(.+)$", block, flags=re.M)]


def _is_external_branch_plan_path(path: str) -> bool:
    normalized = path.replace("\\", "/").strip().strip("`")
    return (
        normalized.startswith(EXTERNAL_BRANCH_RUNTIME_ENGINEERING_PLAN_DIRECTORY)
        and normalized.endswith(f"/{EXTERNAL_BRANCH_RUNTIME_ENGINEERING_PLAN_FILE}")
    )


def _is_repo_branch_plan_path(path: str) -> bool:
    normalized = path.replace("\\", "/").strip().strip("`")
    return normalized.startswith(BRANCH_RUNTIME_ENGINEERING_PLAN_DIRECTORY) and normalized.endswith(
        ".md"
    )


def _clean_release_value(value: str) -> str:
    return value.strip().strip("`").strip()


def _backlog_id_number(workstream_id: str) -> int:
    match = re.fullmatch(r"[A-Z]+-(\d+)", workstream_id)
    return int(match.group(1)) if match else -1


def _backlog_entry_by_id(
    backlog_entries: list[dict[str, str]],
    workstream_id: str,
) -> dict[str, str] | None:
    for entry in backlog_entries:
        if entry["id"] == workstream_id:
            return entry
    return None


def _historical_alias_mapping_matches(
    backlog_entries: list[dict[str, str]],
    *,
    alias_ids: tuple[str, ...],
    family_anchor_id: str,
) -> bool:
    for alias_id in alias_ids:
        entry = _backlog_entry_by_id(backlog_entries, alias_id)
        if not entry:
            return False
        registry_class = _clean_release_value(_extract_colon_value(entry["block"], "Registry Class"))
        historical_alias_of = _clean_release_value(
            _extract_colon_value(entry["block"], "Historical Alias Of")
        )
        if registry_class != "Historical Pass Alias" or historical_alias_of != family_anchor_id:
            return False
    return True


def _parse_family_package_rows(block: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(
        r"^\| `(?P<package>PKG-\d+)` \| `(?P<fam>FAM-\d+)` \| "
        r"(?P<name>[^|]+) \| (?P<status>[^|]+) \| "
        r"(?P<completion>[^|]+) \| (?P<branch>[^|]+) \| (?P<evidence>[^|]+) \|$",
        flags=re.M,
    )
    for match in pattern.finditer(block):
        rows.append({key: value.strip() for key, value in match.groupdict().items()})
    return rows


def _parse_family_slice_rows(block: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pattern = re.compile(
        r"^\| `(?P<slice>SLC-\d+)` \| `(?P<package>PKG-\d+)` \| "
        r"`(?P<fam>FAM-\d+)` \| (?P<name>[^|]+) \| "
        r"(?P<admission>[^|]+) \| (?P<status>[^|]+) \| "
        r"(?P<completion>[^|]+) \| (?P<seam>[^|]+) \|$",
        flags=re.M,
    )
    for match in pattern.finditer(block):
        rows.append({key: value.strip() for key, value in match.groupdict().items()})
    return rows


def _docs_source_truth_reform_active(backlog_text: str, roadmap_text: str) -> bool:
    return DOCS_SOURCE_TRUTH_REFORM_MARKER in backlog_text and DOCS_SOURCE_TRUTH_REFORM_MARKER in roadmap_text


def _validate_docs_source_truth_reform_model(
    require,
    *,
    backlog_text: str,
    roadmap_text: str,
    index_text: str,
    main_text: str,
    backlog_entries: list[dict[str, str]],
) -> None:
    combined_pointer_text = "\n".join((backlog_text, roadmap_text))
    for path_name, text in (
        ("Docs/feature_backlog.md", backlog_text),
        ("Docs/prebeta_roadmap.md", roadmap_text),
    ):
        require(
            DOCS_SOURCE_TRUTH_REFORM_MARKER in text,
            f"{path_name}: missing compact pointer-layer reform marker",
        )
        for marker in POINTER_ONLY_FORBIDDEN_MARKERS:
            require(
                marker not in text,
                (
                    f"{path_name}: pointer-only surface must not carry live-state "
                    f"or detailed trace marker '{marker}'"
                ),
            )
        require(
            not re.search(r"\b[0-9a-f]{40}\b", text),
            f"{path_name}: pointer-only surface must not pin exact commit hashes",
        )

    require(
        DOCS_SOURCE_TRUTH_REFORM_MARKER in main_text,
        "Docs/Main.md: compact pointer-layer reform routing is missing",
    )
    require(
        "Git/GitHub/helpers as live operational truth" in main_text,
        "Docs/Main.md: derived live truth owner is missing from compact reform routing",
    )
    require(
        "Docs/workstreams/index.md" in backlog_text,
        "Docs/feature_backlog.md: compact registry must point to workstream routing",
    )
    require(
        "Docs/branch_records/index.md" in backlog_text,
        "Docs/feature_backlog.md: compact registry must point to branch authority routing",
    )
    require(
        "Docs/branch_plans/" in backlog_text,
        "Docs/feature_backlog.md: compact registry must point to branch runtime plans",
    )
    require(
        "Use GitHub Releases for the authoritative public release list" in roadmap_text,
        "Docs/prebeta_roadmap.md: roadmap must route live release truth to GitHub Releases",
    )

    live_family_ids = [entry["id"] for entry in backlog_entries]
    require(
        live_family_ids == list(FRESH_FAMILY_TAXONOMY),
        (
            "Docs/feature_backlog.md: compact family registry must keep the fresh FAM "
            f"namespace in ascending order: {', '.join(FRESH_FAMILY_TAXONOMY)}"
        ),
    )
    for entry in backlog_entries:
        expected_family = FRESH_FAMILY_TAXONOMY.get(entry["id"])
        require(
            bool(expected_family),
            f"Docs/feature_backlog.md: unexpected compact family id {entry['id']}",
        )
        if not expected_family:
            continue
        require(
            entry["title"] == expected_family["title"],
            (
                "Docs/feature_backlog.md: compact family entry "
                f"{entry['id']} must use broad title `{expected_family['title']}`"
            ),
        )
        for field in COMPACT_BACKLOG_REQUIRED_FIELDS:
            require(
                bool(_extract_colon_value(entry["block"], field)),
                f"Docs/feature_backlog.md: compact family entry {entry['id']} is missing `{field}:`",
            )
        require(
            expected_family["package"] in entry["block"],
            (
                "Docs/feature_backlog.md: compact family entry "
                f"{entry['id']} must cite package {expected_family['package']}"
            ),
        )
        if expected_family["legacy"]:
            for legacy_id in expected_family["legacy"]:
                require(
                    legacy_id in entry["block"] or legacy_id in combined_pointer_text,
                    (
                        "Docs/feature_backlog.md: compact family entry "
                        f"{entry['id']} is missing historical trace for {legacy_id}"
                    ),
                )
        else:
            require(
                "no legacy fb trace" in entry["block"].casefold()
                or "repo vision trace only" in entry["block"].casefold()
                or entry["id"] == "FAM-007",
                (
                    "Docs/feature_backlog.md: compact family entry "
                    f"{entry['id']} must state no legacy FB trace or cite repo vision trace"
                ),
            )

    for required_phrase in (
        "Former standalone historical pass backlog entries now live here as family traceability only.",
        "Historical Family Pass Aliases",
        "Historical Support, Architecture, And Governance Lanes",
        "Historical Implemented Registry-Only Items",
    ):
        require(
            required_phrase in backlog_text,
            f"Docs/feature_backlog.md: compact historical pointer section is missing '{required_phrase}'",
        )
    for trace_id in CONSOLIDATED_TRACE_BACKLOG_IDS:
        require(
            f"### [ID: {trace_id}]" not in backlog_text,
            f"Docs/feature_backlog.md: legacy {trace_id} must not be parseable after compaction",
        )
        require(
            f"`{trace_id}`" in backlog_text,
            f"Docs/feature_backlog.md: legacy trace {trace_id} must remain discoverable as compact history",
        )
    for required_path in (
        "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md",
        "Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md",
    ):
        require(
            required_path in index_text and required_path in backlog_text,
            f"{required_path}: family dossier must be routed by workstream index and backlog pointer",
        )


def _is_admitted_slice(row: dict[str, str]) -> bool:
    return _clean_release_value(row.get("admission", "")).casefold() == ADMITTED_SLICE_STATE


def _is_package_complete(completion_state: str) -> bool:
    normalized = _clean_release_value(completion_state).casefold()
    return normalized in PACKAGE_COMPLETE_STATES


def _is_slice_terminal(completion_state: str) -> bool:
    normalized = _clean_release_value(completion_state).casefold()
    return normalized in SLICE_TERMINAL_COMPLETION_STATES


def _validate_consolidated_backlog_source_truth(
    require,
    *,
    backlog_text: str,
    main_text: str,
    development_rules_text: str,
    phase_governance_text: str,
    backlog_entries: list[dict[str, str]],
) -> None:
    parsed_ids = {entry["id"] for entry in backlog_entries}

    require(
        not re.search(r"^### \[ID: FB-\d+\]", backlog_text, flags=re.M),
        "Docs/feature_backlog.md: legacy `FB-###` IDs must not remain parseable backlog entries",
    )
    live_family_ids = [entry["id"] for entry in backlog_entries]
    require(
        live_family_ids == list(FRESH_FAMILY_TAXONOMY),
        (
            "Docs/feature_backlog.md: live family registry must use the fresh FAM namespace "
            f"in ascending order: {', '.join(FRESH_FAMILY_TAXONOMY)}"
        ),
    )

    all_package_rows: list[dict[str, str]] = []
    all_slice_rows: list[dict[str, str]] = []
    for entry in backlog_entries:
        require(
            entry["id"].startswith(FRESH_FAMILY_PREFIX),
            (
                "Docs/feature_backlog.md: live backlog-family entry "
                f"{entry['id']} must use the fresh `{FRESH_FAMILY_PREFIX}###` namespace"
            ),
        )
        expected_family = FRESH_FAMILY_TAXONOMY.get(entry["id"])
        require(
            expected_family is not None,
            (
                "Docs/feature_backlog.md: live backlog-family entry "
                f"{entry['id']} is not part of the canonical fresh FAM taxonomy"
            ),
        )
        if expected_family is None:
            continue
        require(
            entry["title"] == expected_family["title"],
            (
                "Docs/feature_backlog.md: live backlog-family entry "
                f"{entry['id']} must use broad title `{expected_family['title']}`"
            ),
        )
        require(
            "Legacy FB ID:" not in entry["block"],
            (
                "Docs/feature_backlog.md: broad FAM entry "
                f"{entry['id']} must not retain one-to-one `Legacy FB ID:` mapping"
            ),
        )
        for legacy_id in expected_family["legacy"]:
            require(
                legacy_id in entry["block"],
                (
                    "Docs/feature_backlog.md: broad FAM entry "
                    f"{entry['id']} is missing historical trace for {legacy_id}"
                ),
            )
        if not expected_family["legacy"]:
            require(
                "No legacy FB" in entry["block"] or "repo vision trace only" in entry["block"],
                (
                    "Docs/feature_backlog.md: broad FAM entry "
                    f"{entry['id']} must state that it has no legacy FB trace"
                ),
            )

        package_rows = _parse_family_package_rows(entry["block"])
        slice_rows = _parse_family_slice_rows(entry["block"])
        all_package_rows.extend(package_rows)
        all_slice_rows.extend(slice_rows)
        expected_package = expected_family["package"]

        require(
            len(package_rows) == 1,
            (
                "Docs/feature_backlog.md: broad FAM entry "
                f"{entry['id']} must contain exactly one package trace row"
            ),
        )
        if package_rows:
            package = package_rows[0]
            require(
                package["package"] == expected_package and package["fam"] == entry["id"],
                (
                    "Docs/feature_backlog.md: broad FAM entry "
                    f"{entry['id']} package row must trace `{expected_package}` to `{entry['id']}`"
                ),
            )
            require(
                bool(package["completion"]),
                (
                    "Docs/feature_backlog.md: package "
                    f"{expected_package} must record a package completion state"
                ),
            )
        require(
            len(slice_rows) >= 2,
            (
                "Docs/feature_backlog.md: broad FAM entry "
                f"{entry['id']} must contain enough trace rows to preserve family context"
            ),
        )
        package_admission_state = _clean_release_value(
            _extract_colon_value(entry["block"], "Package Admission State")
        )
        declared_admitted_slice_count = _clean_release_value(
            _extract_colon_value(entry["block"], "Admitted Slice Count")
        )
        require(
            bool(package_admission_state),
            (
                "Docs/feature_backlog.md: broad FAM entry "
                f"{entry['id']} must declare `Package Admission State:`"
            ),
        )
        require(
            bool(declared_admitted_slice_count),
            (
                "Docs/feature_backlog.md: broad FAM entry "
                f"{entry['id']} must declare `Admitted Slice Count:`"
            ),
        )
        single_slice_approval = _clean_release_value(
            _extract_colon_value(entry["block"], "Single-Slice Package User Approval")
        )
        admitted_slice_rows = [row for row in slice_rows if _is_admitted_slice(row)]
        if declared_admitted_slice_count:
            require(
                declared_admitted_slice_count == str(len(admitted_slice_rows)),
                (
                    "Docs/feature_backlog.md: broad FAM entry "
                    f"{entry['id']} declares Admitted Slice Count {declared_admitted_slice_count}, "
                    f"but validator counted {len(admitted_slice_rows)}"
                ),
            )
        require(
            len(admitted_slice_rows) != 1 or "Granted" in single_slice_approval,
            (
                "Docs/feature_backlog.md: package "
                f"{expected_package} has exactly one admitted slice without explicit USER approval"
            ),
        )
        if not admitted_slice_rows:
            require(
                "no active single-slice package is admitted" in single_slice_approval.casefold(),
                (
                    "Docs/feature_backlog.md: package "
                    f"{expected_package} has no admitted slices, so Single-Slice Package User Approval "
                    "must not claim multi-slice admission"
                ),
            )
        for slice_row in slice_rows:
            require(
                slice_row["fam"] == entry["id"] and slice_row["package"] == expected_package,
                (
                    "Docs/feature_backlog.md: slice "
                    f"{slice_row['slice']} must trace to exactly `{entry['id']}` and `{expected_package}`"
                ),
            )
            require(
                bool(slice_row["admission"]) and bool(slice_row["status"])
                and bool(slice_row["completion"]) and bool(slice_row["seam"]),
                (
                    "Docs/feature_backlog.md: slice "
                    f"{slice_row['slice']} must record admission state, status, completion state, and seam trace"
                ),
            )
            normalized_admission = _clean_release_value(slice_row["admission"]).casefold()
            require(
                normalized_admission == ADMITTED_SLICE_STATE
                or normalized_admission in NON_ADMITTED_SLICE_STATES,
                (
                    "Docs/feature_backlog.md: slice "
                    f"{slice_row['slice']} has unsupported Admission State '{slice_row['admission']}'"
                ),
            )
            row_text = " ".join(
                (
                    slice_row["name"],
                    slice_row["status"],
                    slice_row["completion"],
                    slice_row["seam"],
                )
            ).casefold()
            has_placeholder_marker = any(marker in row_text for marker in PLACEHOLDER_SLICE_MARKERS)
            require(
                not (_is_admitted_slice(slice_row) and has_placeholder_marker),
                (
                    "Docs/feature_backlog.md: slice "
                    f"{slice_row['slice']} is marked admitted while still carrying placeholder/future wording"
                ),
            )
            require(
                not has_placeholder_marker or not _is_admitted_slice(slice_row),
                (
                    "Docs/feature_backlog.md: slice "
                    f"{slice_row['slice']} future/deferred placeholder row must not count as admitted"
                ),
            )
            if _is_admitted_slice(slice_row):
                require(
                    _clean_release_value(slice_row["completion"]).casefold() != "not admitted",
                    (
                        "Docs/feature_backlog.md: admitted slice "
                        f"{slice_row['slice']} must carry a real completion state"
                    ),
                )
        if package_rows and _is_package_complete(package_rows[0]["completion"]):
            incomplete_admitted = [
                row["slice"]
                for row in admitted_slice_rows
                if not _is_slice_terminal(row["completion"])
            ]
            require(
                not incomplete_admitted,
                (
                    "Docs/feature_backlog.md: package "
                    f"{expected_package} cannot be complete while admitted slices remain incomplete: "
                    f"{', '.join(incomplete_admitted)}"
                ),
            )

    package_to_fams: dict[str, set[str]] = {}
    for row in all_package_rows:
        package_to_fams.setdefault(row["package"], set()).add(row["fam"])
    for package_id, fams in package_to_fams.items():
        require(
            len(fams) == 1,
            f"Docs/feature_backlog.md: package {package_id} must trace to exactly one FAM",
        )

    slice_ids: set[str] = set()
    for row in all_slice_rows:
        require(
            row["slice"] not in slice_ids,
            f"Docs/feature_backlog.md: duplicate slice id {row['slice']} is not allowed",
        )
        slice_ids.add(row["slice"])
        require(
            row["package"] in package_to_fams,
            f"Docs/feature_backlog.md: slice {row['slice']} references missing package {row['package']}",
        )
        require(
            row["fam"] in package_to_fams[row["package"]],
            (
                "Docs/feature_backlog.md: slice "
                f"{row['slice']} must trace to exactly one FAM and one package"
            ),
        )

    require(
        not re.search(r"^### \[ID: PR-\d+\]", backlog_text, flags=re.M),
        "Docs/feature_backlog.md: PR numbers must remain evidence only, not parseable backlog identities",
    )

    for trace_id in CONSOLIDATED_TRACE_BACKLOG_IDS:
        require(
            trace_id not in parsed_ids,
            (
                "Docs/feature_backlog.md: "
                f"{trace_id} must remain a consolidated trace row, not a parseable backlog item"
            ),
        )
        require(
            f"Legacy FB ID: {trace_id}" in backlog_text
            or f"#### [Former ID: {trace_id}]" in backlog_text
            or f"| `{trace_id}` |" in backlog_text,
            (
                "Docs/feature_backlog.md: "
                f"{trace_id} consolidated trace is missing after backlog source-of-truth repair"
            ),
        )

    for entry in backlog_entries:
        registry_class = _clean_release_value(_extract_colon_value(entry["block"], "Registry Class"))
        if registry_class == "Feature Family":
            continue
        has_explicit_user_approval = (
            "USER Approval:" in entry["block"]
            and "explicit" in entry["block"].casefold()
        )
        require(
            has_explicit_user_approval,
            (
                "Docs/feature_backlog.md: parseable non-feature-family backlog entry "
                f"{entry['id']} requires explicit USER approval; otherwise it must be a trace row "
                "under the family/source-of-truth consolidation model"
            ),
        )

    for phrase in CONSOLIDATED_BACKLOG_TRACE_REQUIRED_PHRASES:
        require(
            phrase in backlog_text,
            (
                "Docs/feature_backlog.md: consolidated backlog source-of-truth trace is missing "
                f"required marker '{phrase}'"
            ),
        )
    for phrase in FRESH_FAMILY_NAMESPACE_REQUIRED_PHRASES:
        require(
            phrase in "\n".join(
                (backlog_text, main_text, development_rules_text, phase_governance_text)
            ),
            (
                "governance source-of-truth: fresh family namespace rule is missing "
                f"required marker '{phrase}'"
            ),
        )
    for phrase in FAMILY_PACKAGE_MODEL_REQUIRED_PHRASES:
        require(
            phrase in "\n".join(
                (backlog_text, main_text, development_rules_text, phase_governance_text)
            ),
            (
                "governance source-of-truth: family package/slice model is missing "
                f"required marker '{phrase}'"
            ),
        )


def _latest_public_prerelease(roadmap_text: str) -> str:
    return _clean_release_value(_extract_colon_value(roadmap_text, "- latest public prerelease"))


def _post_release_closure_drift_is_recorded(
    backlog_text: str,
    roadmap_text: str,
    *,
    expected_release_tag: str,
) -> bool:
    combined_text = "\n".join((backlog_text, roadmap_text))
    required_markers = (
        *POST_RELEASE_CLOSURE_DRIFT_MARKERS,
        f"Published Release Pending Canon Closure: {expected_release_tag}",
    )
    return all(marker in combined_text for marker in required_markers)


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


def _git_tracked_files() -> list[Path]:
    completed = subprocess.run(
        ("git", "ls-files"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [Path(line.strip()) for line in completed.stdout.splitlines() if line.strip()]


def _tracked_repo_legacy_product_name_occurrences() -> list[str]:
    banned_tokens = [
        LEGACY_RETIRED_PRODUCT_NAME.casefold(),
        *(token.casefold() for token in LEGACY_PRODUCT_NAME_EXTRA_TOKENS),
    ]
    occurrences: list[str] = []
    for relative_path in _git_tracked_files():
        normalized_path = relative_path.as_posix()
        normalized_path_casefold = normalized_path.casefold()
        if any(banned in normalized_path_casefold for banned in banned_tokens):
            occurrences.append(f"{normalized_path}: tracked path contains legacy product name")
            continue
        path = ROOT_DIR / relative_path
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        text_casefold = text.casefold()
        matched_token = next((banned for banned in banned_tokens if banned in text_casefold), "")
        if matched_token:
            line_number = next(
                (
                    index
                    for index, line in enumerate(text.splitlines(), start=1)
                    if matched_token in line.casefold()
                ),
                "?",
            )
            occurrences.append(f"{normalized_path}:{line_number}: tracked content contains legacy product name")
    return occurrences


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


def _git_prebeta_tag_commit(tag: str) -> str:
    if not tag:
        return ""

    local_ref = subprocess.run(
        ("git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if local_ref.returncode == 0:
        candidate = local_ref.stdout.strip()
        if re.fullmatch(r"[0-9a-fA-F]{40}", candidate):
            return candidate

    remote_ref = subprocess.run(
        ("git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}*"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if remote_ref.returncode != 0:
        return ""

    lightweight_candidate = ""
    peeled_ref = f"refs/tags/{tag}^{{}}"
    direct_ref = f"refs/tags/{tag}"
    for line in remote_ref.stdout.splitlines():
        sha, _, ref_name = line.strip().partition("\t")
        if not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            continue
        if ref_name == peeled_ref:
            return sha
        if ref_name == direct_ref:
            lightweight_candidate = sha
    return lightweight_candidate


def _branch_ref_file_stem(branch_ref: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", branch_ref.casefold()).strip("_")


def _add_release_window_entry(
    identifiers: set[str],
    branch_file_stems: set[str],
    sha: str,
    subject: str,
) -> None:
    sha = sha.strip().casefold()
    if re.fullmatch(r"[0-9a-f]{40}", sha):
        identifiers.update({sha, sha[:12], sha[:10], sha[:8]})

    for match in re.finditer(r"Merge (?:pull request|PR) #(\d+)", subject, flags=re.IGNORECASE):
        identifiers.add(f"pr #{match.group(1)}")

    branch_match = re.search(r"from [^/]+/(\S+)", subject)
    if branch_match:
        branch_ref = branch_match.group(1).strip().casefold()
        branch_file_stem = _branch_ref_file_stem(branch_ref)
        identifiers.add(branch_ref)
        identifiers.add(branch_file_stem)
        branch_file_stems.add(branch_file_stem)


def _github_published_release_window_scope(
    previous_tag: str,
    release_tag: str,
) -> tuple[set[str], set[str]]:
    if not previous_tag or not release_tag:
        return set(), set()

    repository_full_name, repository_error = _git_origin_repository_full_name()
    if repository_error or not repository_full_name:
        return set(), set()

    base = urllib_parse.quote(previous_tag, safe="")
    head = urllib_parse.quote(release_tag, safe="")
    identifiers: set[str] = set()
    branch_file_stems: set[str] = set()
    page = 1
    while True:
        payload, _error = _github_api_json(
            "https://api.github.com/repos/"
            f"{repository_full_name}/compare/{base}...{head}"
            f"?per_page=100&page={page}"
        )
        if not isinstance(payload, dict):
            break

        commits = payload.get("commits")
        if not isinstance(commits, list) or not commits:
            break

        for commit_entry in commits:
            if not isinstance(commit_entry, dict):
                continue
            sha = str(commit_entry.get("sha") or "")
            commit_payload = commit_entry.get("commit")
            if not isinstance(commit_payload, dict):
                continue
            message = str(commit_payload.get("message") or "")
            subject = message.splitlines()[0] if message else ""
            _add_release_window_entry(identifiers, branch_file_stems, sha, subject)

        if len(commits) < 100:
            break
        page += 1

    return identifiers, branch_file_stems


def _previous_known_prebeta_tag(release_tag: str) -> str:
    release_version = _parse_prebeta_version(release_tag)
    if release_version is None:
        return ""

    tags = sorted(
        set(_git_prebeta_tags()) | set(_git_remote_prebeta_tags()),
        key=lambda tag: _parse_prebeta_version(tag) or (0, 0, 0),
    )
    previous_tags = [
        tag
        for tag in tags
        if (_parse_prebeta_version(tag) or (0, 0, 0)) < release_version
    ]
    return previous_tags[-1] if previous_tags else ""


def _git_release_window_scope(previous_ref: str, release_ref: str) -> tuple[set[str], set[str]]:
    if not release_ref:
        return set(), set()

    rev_range = f"{previous_ref}..{release_ref}" if previous_ref else release_ref
    completed = subprocess.run(
        ("git", "log", "--first-parent", "--format=%H%x09%s", rev_range),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return set(), set()

    identifiers: set[str] = set()
    branch_file_stems: set[str] = set()
    for line in completed.stdout.splitlines():
        sha, _, subject = line.partition("\t")
        _add_release_window_entry(identifiers, branch_file_stems, sha, subject)

    return identifiers, branch_file_stems


def _published_release_window_scope(release_tag: str) -> tuple[set[str], set[str]]:
    """Return line identifiers and branch-file stems included in a published release window."""

    previous_tag = _previous_known_prebeta_tag(release_tag)
    release_ref = _git_prebeta_tag_commit(release_tag)
    previous_ref = _git_prebeta_tag_commit(previous_tag) if previous_tag else ""
    if not release_ref:
        return set(), set()
    if previous_tag and not previous_ref:
        return _github_published_release_window_scope(previous_tag, release_tag)

    release_window = _git_release_window_scope(previous_ref, release_ref)
    if not any(release_window):
        return _github_published_release_window_scope(previous_tag, release_tag)
    return release_window


def _path_matches_published_release_window_branch(
    relative_path: Path,
    branch_file_stems: set[str],
) -> bool:
    if not branch_file_stems:
        return False
    normalized = relative_path.as_posix()
    if normalized == "Docs/branch_records/feature_release_readiness_source_truth_intake.md":
        return False
    if not (
        normalized.startswith("Docs/branch_records/")
        or normalized.startswith("Docs/branch_plans/")
    ):
        return False
    return relative_path.stem.casefold() in branch_file_stems


def _is_allowed_published_release_merged_unreleased_line(line_lower: str) -> bool:
    if "historical pre-release snapshot" in line_lower:
        return True
    if "no current merged-unreleased" in line_lower:
        return True
    if "merged-unreleased release-debt owner" in line_lower and "none" in line_lower:
        return True
    return False


def _published_release_closure_scan_paths() -> list[Path]:
    paths: set[Path] = set(PUBLISHED_RELEASE_CLOSURE_SCAN_PATHS)
    for directory in PUBLISHED_RELEASE_CLOSURE_SCAN_DIRS:
        root = ROOT_DIR / directory
        if not root.is_dir():
            continue
        paths.update(
            path.relative_to(ROOT_DIR)
            for path in root.rglob("*.md")
            if path.is_file()
        )
    return sorted(paths, key=lambda path: path.as_posix())


def _validate_release_canon_closure(
    require,
    release_label: str,
    release_window_identifiers: set[str],
    branch_file_stems: set[str],
    *,
    published: bool,
) -> None:
    if not release_label:
        return

    release_label_lower = release_label.casefold()
    blocker_name = "Post-Release Canon Closure Drift" if published else "Pre-Publish Canon Closure Drift"
    release_state = "is published" if published else "is the simulated release candidate"
    for relative_path in _published_release_closure_scan_paths():
        path = ROOT_DIR / relative_path
        if not path.is_file():
            continue
        text = _read_text(relative_path)
        file_matches_window_branch = _path_matches_published_release_window_branch(
            relative_path,
            branch_file_stems,
        )
        for line_number, line in enumerate(text.splitlines(), start=1):
            line_lower = line.casefold()
            if "merged-unreleased" not in line_lower:
                continue
            if _is_allowed_published_release_merged_unreleased_line(line_lower):
                continue
            line_matches_release = release_label_lower in line_lower
            line_matches_window = any(
                identifier in line_lower
                for identifier in release_window_identifiers
            )
            if not (line_matches_release or line_matches_window or file_matches_window_branch):
                continue
            require(
                False,
                (
                    f"{relative_path}:{line_number}: {blocker_name}; "
                    f"{release_label} {release_state}, so source truth must not keep included "
                    "release-window scope as current merged-unreleased posture. Fold the scope "
                    "to released/closed posture or label it as historical pre-release snapshot evidence."
                ),
            )


def _validate_published_release_canon_closure(require, release_tag: str) -> None:
    if not release_tag:
        return

    release_window_identifiers, branch_file_stems = _published_release_window_scope(release_tag)
    _validate_release_canon_closure(
        require,
        release_tag,
        release_window_identifiers,
        branch_file_stems,
        published=True,
    )


def _validate_pre_publish_release_canon_closure_simulation(
    require,
    latest_public_prerelease: str,
) -> None:
    if not latest_public_prerelease or not _head_matches_origin_main():
        return

    latest_release_ref = _git_prebeta_tag_commit(latest_public_prerelease)
    target_ref = _git_head_sha()
    if not latest_release_ref or not target_ref or latest_release_ref == target_ref:
        return

    release_window_identifiers, branch_file_stems = _git_release_window_scope(
        latest_release_ref,
        target_ref,
    )
    if not release_window_identifiers and not branch_file_stems:
        return

    _validate_release_canon_closure(
        require,
        f"candidate after {latest_public_prerelease}",
        release_window_identifiers,
        branch_file_stems,
        published=False,
    )


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


def _current_state_label_lines(text: str, labels: tuple[str, ...]) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if any(stripped.startswith(f"{label}:") for label in labels):
            lines.append(stripped)
    return "\n".join(lines)


def _post_merge_record_current_state_text(record_text: str) -> str:
    current_sections = (
        "Record State",
        "Status",
        "Current Phase",
        "Phase Status",
        "Blockers",
        "Next Legal Phase",
        "Formal Next Legal Phase Digest",
    )
    current_labels = (
        "Record State",
        "Status",
        "Phase",
        "Phase Detail",
        "Phase Status",
        "Authority State",
        "Bounded State",
        "Open PR State",
        "Active Blockers",
        "PR Readiness Blocker",
        "Current Phase",
        "Next Legal Phase",
        "Why This Phase Is Next",
        "Approval Required",
        "Exact USER Decision Needed",
        "Allowed Scope",
    )
    return "\n".join(
        section
        for section in (
            *(_section(record_text, section_name) for section_name in current_sections),
            _current_state_label_lines(record_text, current_labels),
        )
        if section
    )


def _post_merge_plan_current_state_text(plan_text: str) -> str:
    current_labels = (
        "Current Plan Phase",
        "Current Phase",
        "Engineering Plan Status",
        "Open Questions",
        "USER Planning Decisions",
        "PR Fold-Down Packet",
        "Next Legal Phase",
        "Exact USER Decision Needed",
    )
    return _current_state_label_lines(plan_text, current_labels)


def _backlog_entry_block(backlog_text: str, fam_id: str) -> str:
    for entry in _parse_backlog_sections(backlog_text):
        if entry["id"] == fam_id:
            return entry["block"]
    return ""


def _roadmap_family_row(roadmap_text: str, fam_id: str) -> str:
    pattern = re.compile(rf"^\|\s*`{re.escape(fam_id)}`(?:\s|\|).*$", flags=re.M)
    match = pattern.search(roadmap_text)
    return match.group(0) if match else ""


def _run_post_merge_fold_down_drift_gate(
    require,
    *,
    backlog_text: str,
    roadmap_text: str,
    branch_record_index_text: str,
) -> None:
    historical_branch_record_paths = _collect_branch_record_paths(
        branch_record_index_text,
        "Historical Branch Authority Records",
    )
    active_branch_record_paths = set(
        _collect_branch_record_paths(branch_record_index_text, "Active Branch Authority Records")
    )
    for record_path in historical_branch_record_paths:
        path = Path(record_path)
        if not path.exists():
            continue
        record_text = _read_text(path)
        record_state = _parse_workstream_doc(record_text)
        if not (
            str(record_state["record_state"]).casefold() == "historical merged-unreleased"
            or str(record_state["status"]).casefold() == "merged-unreleased"
        ):
            continue
        require(
            record_path not in active_branch_record_paths,
            f"{record_path}: historical merged-unreleased record must not remain in Active Branch Authority Records",
        )
        require(
            str(record_state["current_phase"]) == HISTORICAL_TRACEABILITY_PHASE,
            f"{record_path}: historical merged-unreleased record must use Phase: `{HISTORICAL_TRACEABILITY_PHASE}`",
        )
        plan_pointer = _extract_colon_value(record_text, "Branch Runtime Engineering Plan Path").strip("`")
        plan_text = _read_text(Path(plan_pointer)) if plan_pointer and Path(plan_pointer).exists() else ""
        record_current_state_text = _post_merge_record_current_state_text(record_text)
        plan_current_state_text = _post_merge_plan_current_state_text(plan_text)
        for label, pattern in POST_MERGE_FOLD_DOWN_STALE_PATTERNS:
            require(
                pattern.search(record_current_state_text) is None,
                f"{record_path}: post-merge current-state fold-down still contains stale {label}",
            )
            if plan_current_state_text:
                require(
                    pattern.search(plan_current_state_text) is None,
                    f"{plan_pointer}: post-merge current-state fold-down still contains stale {label}",
                )
        if "fam_006_overlay_display_acceptance_foundation" in record_path:
            roadmap_text = _read_text(Path("Docs/prebeta_roadmap.md"))
            fam_sources = (
                ("Docs/feature_backlog.md", _backlog_entry_block(backlog_text, "FAM-006")),
                ("Docs/prebeta_roadmap.md", _roadmap_family_row(roadmap_text, "FAM-006")),
            )
            for source_name, source_text in fam_sources:
                for phrase in POST_MERGE_COMPACT_OWNER_STALE_PHRASES:
                    require(
                        phrase.casefold() not in source_text.casefold(),
                        f"{source_name}: FAM-006 compact current-state owner still contains stale post-merge phrase '{phrase}'",
                    )


def _extract_branch_identity_branch(text: str) -> str:
    match = re.search(r"^\s*-\s*Branch:\s*`([^`]+)`\s*$", text, flags=re.M)
    return match.group(1).strip() if match else ""


def _count_field_occurrences(block: str, label: str) -> int:
    return len(re.findall(rf"^{re.escape(label)}:\s*.+$", block, flags=re.M))


def _branch_record_branch_sets(
    active_branch_record_paths: set[str],
    historical_branch_record_paths: set[str],
    current_branch: str,
) -> tuple[dict[str, str], set[str], set[str], set[str]]:
    branch_class_map: dict[str, str] = {}
    all_repair_branch_names: set[str] = set()
    active_repair_branch_names: set[str] = set()
    historical_branch_names: set[str] = set()
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
        if branch_record_path in historical_branch_record_paths:
            historical_branch_names.add(branch_name)
            historical_branch_names.add(prefixed_branch_name)
        if branch_class == EMERGENCY_CANON_REPAIR_BRANCH_CLASS:
            all_repair_branch_names.add(branch_name)
            all_repair_branch_names.add(prefixed_branch_name)
            if branch_record_path in active_branch_record_paths:
                active_repair_branch_names.add(branch_name)
            active_repair_branch_names.add(prefixed_branch_name)
        branch_class_map[branch_name] = branch_class
        branch_class_map[prefixed_branch_name] = branch_class
    return branch_class_map, all_repair_branch_names, active_repair_branch_names, historical_branch_names


def _active_branch_record_for_branch(
    active_branch_record_paths: set[str],
    branch_name: str,
) -> tuple[str, str]:
    for branch_record_path in active_branch_record_paths:
        record_path = ROOT_DIR / Path(branch_record_path)
        if not record_path.is_file():
            continue
        record_text = _read_text(Path(branch_record_path))
        if _extract_branch_identity_branch(record_text) == branch_name:
            return branch_record_path, record_text
    return "", ""


def _branch_record_for_branch(
    branch_record_paths: set[str],
    branch_name: str,
) -> tuple[str, str]:
    for branch_record_path in branch_record_paths:
        record_path = ROOT_DIR / Path(branch_record_path)
        if not record_path.is_file():
            continue
        record_text = _read_text(Path(branch_record_path))
        if _extract_branch_identity_branch(record_text) == branch_name:
            return branch_record_path, record_text
    return "", ""


def _external_branch_state_record_for_branch(
    branch_name: str,
    actual_root: str,
) -> tuple[str, str]:
    if not branch_name:
        return "", ""
    state_path = (
        Path(EXTERNAL_BRANCH_RUNTIME_ENGINEERING_PLAN_DIRECTORY)
        / _branch_ref_file_stem(branch_name)
        / EXTERNAL_BRANCH_OPERATIONAL_STATE_FILE
    )
    if not state_path.exists():
        return "", ""
    state_text = _read_text(state_path)
    # External state files contain overlapping labels such as
    # `Branch Planning Packet ZIP`; identity reads must be exact.
    state_branch = _extract_exact_marker_value(state_text, "Branch")
    if state_branch != branch_name:
        return "", ""
    state_worktree = _extract_exact_marker_value(state_text, "Worktree")
    if (
        actual_root
        and state_worktree
        and _normalized_local_path(state_worktree) != _normalized_local_path(actual_root)
    ):
        return "", ""
    record_pointer = _extract_exact_marker_value(state_text, "Repo Branch Record Pointer")
    if not record_pointer:
        return "", ""
    record_path = ROOT_DIR / Path(record_pointer)
    if not record_path.is_file():
        return "", ""
    record_text = _read_text(Path(record_pointer))
    if _extract_branch_identity_branch(record_text) != branch_name:
        return "", ""
    record_identity = _section(record_text, "Branch Identity")
    state_identity = _section(state_text, "Branch Identity")
    if _extract_exact_marker_value(record_identity, "Worktree") and _section(
        record_text,
        "Assigned Worktree Confinement",
    ):
        return record_pointer, record_text
    if _extract_exact_marker_value(state_identity, "Worktree") and _section(
        state_text,
        "Assigned Worktree Confinement",
    ):
        return str(state_path), state_text
    return record_pointer, record_text


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


def _extract_exact_marker_value(block: str, label: str) -> str:
    normalized_label = label.rstrip(":")
    matches = re.findall(
        rf"^\s*(?:-\s*)?{re.escape(normalized_label)}:\s*`?(.+?)`?\s*$",
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
    # Current applicability and actual approval are checked by the phase/ownership gates.
    # Slice counts and docs-only bypass markers no longer grant or deny authority.
    return


def _validate_slice_continuation_policy(
    require,
    source_path: str,
    text: str,
    *,
    branch_class: str,
    current_phase: str,
) -> None:
    # Current applicability and actual approval are checked by the phase/ownership gates.
    # Slice counts and docs-only bypass markers no longer grant or deny authority.
    return


def _validate_governed_output_state(
    require,
    source_path: str,
    *,
    continuation_section: str,
    active_seam_section: str,
    blockers: list[str],
) -> None:
    # Optional historical continuation fields are data, not authority or a latch.
    decision = _extract_marker_value(continuation_section, "Continue Decision")
    if decision:
        require(decision.casefold() in {"continue", "stop", "pending"},
                f"{source_path}: unsupported continuation disposition")
    if decision.casefold() == "continue":
        require(not blockers, f"{source_path}: continuation cannot hide an actual blocker")


def _validate_single_seam_workstream_contract(
    require,
    source_path: str,
    text: str,
    *,
    branch_class: str,
    current_phase: str,
    blockers: list[str],
) -> None:
    # Current applicability and actual approval are checked by the phase/ownership gates.
    # Slice counts and docs-only bypass markers no longer grant or deny authority.
    return


def _validate_backlog_completion_strategy(
    require,
    source_path: str,
    text: str,
    *,
    branch_class: str,
    current_phase: str,
) -> None:
    if branch_class != "implementation":
        return
    if current_phase != "Branch Readiness":
        return

    require(
        f"## {BACKLOG_COMPLETION_STRATEGY_HEADING}" in text,
        f"{source_path}: implementation Branch Readiness is missing '## {BACKLOG_COMPLETION_STRATEGY_HEADING}'",
    )
    strategy_section = _section(text, BACKLOG_COMPLETION_STRATEGY_HEADING)
    for marker in REQUIRED_BRANCH_READINESS_COMPLETION_MARKERS:
        require(
            marker in strategy_section,
            f"{source_path}: {BACKLOG_COMPLETION_STRATEGY_HEADING} is missing '{marker}'",
        )

    completion_goal = _extract_marker_value(strategy_section, BACKLOG_COMPLETION_GOAL_LABEL)
    known_future_blockers = _extract_marker_value(
        strategy_section, KNOWN_FUTURE_DEPENDENT_BLOCKERS_LABEL
    )
    closure_rule = _extract_marker_value(strategy_section, BRANCH_CLOSURE_RULE_LABEL)

    require(
        bool(completion_goal),
        f"{source_path}: {BACKLOG_COMPLETION_GOAL_LABEL} must not be empty",
    )
    require(
        bool(known_future_blockers),
        f"{source_path}: {KNOWN_FUTURE_DEPENDENT_BLOCKERS_LABEL} must not be empty",
    )
    require(
        bool(closure_rule),
        f"{source_path}: {BRANCH_CLOSURE_RULE_LABEL} must not be empty",
    )


def _planning_word_count(value: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9/_-]*", value))


def _normalized_planning_value(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`").strip()).casefold()


def _validate_product_system_planning_substance(
    require,
    source_path: str,
    marker: str,
    value: str,
) -> None:
    normalized_value = _normalized_planning_value(value)
    require(
        normalized_value not in PRODUCT_SYSTEM_PLANNING_HANDWAVE_VALUES,
        (
            f"{source_path}: {PRODUCT_DEFINITION_PLAN_HEADING} value for '{marker}' "
            "is placeholder/self-assessed wording, not concrete planning proof"
        ),
    )
    require(
        _planning_word_count(value) >= PRODUCT_SYSTEM_PLANNING_MIN_WORDS,
        (
            f"{source_path}: {PRODUCT_DEFINITION_PLAN_HEADING} value for '{marker}' "
            "is too shallow; record concrete product/system planning detail"
        ),
    )
    if marker == "Scale / Data Volume Model:":
        require(
            any(term in normalized_value for term in PRODUCT_SYSTEM_SCALE_TERMS)
            or any(char.isdigit() for char in value),
            (
                f"{source_path}: Scale / Data Volume Model must name concrete scale "
                "pressure such as item counts, multiple states, profiles, records, "
                "users, windows, files, sources, or monitors"
            ),
        )
    if marker == "Codex Additional Recommendations:":
        require(
            any(term in normalized_value for term in PRODUCT_SYSTEM_RECOMMENDATION_TERMS),
            (
                f"{source_path}: Codex Additional Recommendations must contain real "
                "recommendations/options, not just a statement that the plan is complete"
            ),
        )
    if marker == "USER Critique Loop:":
        require(
            "user" in normalized_value
            and any(term in normalized_value for term in PRODUCT_SYSTEM_USER_CRITIQUE_TERMS),
            (
                f"{source_path}: USER Critique Loop must describe how USER review can "
                "approve, change, defer, critique, or give feedback before Workstream"
            ),
        )
    if marker == "USER Decision Ledger:":
        require(
            "user" in normalized_value
            and any(term in normalized_value for term in PRODUCT_SYSTEM_USER_DECISION_TERMS),
            (
                f"{source_path}: USER Decision Ledger must record USER decision state "
                "such as approved, pending, changed, deferred, waived, accepted, or rejected"
            ),
        )
    if marker == "Deferred Ideas / Future Package Ledger:":
        require(
            "future" in normalized_value
            or "defer" in normalized_value
            or "separate package" in normalized_value,
            (
                f"{source_path}: Deferred Ideas / Future Package Ledger must identify "
                "deferred/future work or explicitly route it to a separate package"
            ),
        )
    if marker == "Planning Adequacy Review:":
        require(
            any(term in normalized_value for term in PRODUCT_SYSTEM_ADEQUACY_TERMS),
            (
                f"{source_path}: Planning Adequacy Review must explain why the plan is "
                "not shallow and how it covers the whole/end-to-end system"
            ),
        )
    if marker == "Rejected Shallow Plan:":
        require(
            any(term in normalized_value for term in PRODUCT_SYSTEM_REJECTED_SHALLOW_TERMS),
            (
                f"{source_path}: Rejected Shallow Plan must name the simple/minimal plan "
                "that was rejected or explain why it was insufficient"
            ),
        )
    if marker == "Alternatives And Tradeoffs Reviewed:":
        require(
            any(term in normalized_value for term in PRODUCT_SYSTEM_TRADEOFF_TERMS),
            (
                f"{source_path}: Alternatives And Tradeoffs Reviewed must include "
                "alternatives/options plus tradeoffs or risks"
            ),
        )
    if marker == "Whole-System Interaction Map:":
        require(
            _planning_word_count(value) >= PRODUCT_SYSTEM_PLANNING_MIN_WORDS + 4
            and (
                "->" in value
                or ";" in value
                or "," in value
                or "between" in normalized_value
                or "through" in normalized_value
            ),
            (
                f"{source_path}: Whole-System Interaction Map must describe multiple "
                "interacting pieces, flows, or relationships"
            ),
        )
    if marker == "Minimum Viable vs Full System Boundary:":
        require(
            any(term in normalized_value for term in PRODUCT_SYSTEM_BOUNDARY_TERMS),
            (
                f"{source_path}: Minimum Viable vs Full System Boundary must separate "
                "minimum current-branch scope from full/future/deferred system scope"
            ),
        )
    if marker == "Open Questions / USER Decision Points:":
        require(
            "user" in normalized_value
            and (
                "question" in normalized_value
                or "decision" in normalized_value
                or "approve" in normalized_value
                or "pending" in normalized_value
            ),
            (
                f"{source_path}: Open Questions / USER Decision Points must name USER "
                "questions, decisions, approvals, or pending decisions"
            ),
        )


def _validate_runtime_engineering_contract_substance(
    require,
    source_path: str,
    marker: str,
    value: str,
) -> None:
    normalized_value = _normalized_planning_value(value)
    require(
        normalized_value not in PRODUCT_SYSTEM_PLANNING_HANDWAVE_VALUES,
        (
            f"{source_path}: {RUNTIME_ENGINEERING_CONTRACT_HEADING} value for "
            f"'{marker}' is placeholder/self-assessed wording, not concrete "
            "engineering planning proof"
        ),
    )
    require(
        _planning_word_count(value) >= RUNTIME_ENGINEERING_CONTRACT_MIN_WORDS,
        (
            f"{source_path}: {RUNTIME_ENGINEERING_CONTRACT_HEADING} value for "
            f"'{marker}' is too shallow; record concrete baseline, delta, "
            "surface, proof, or traceability detail"
        ),
    )

    required_terms = RUNTIME_ENGINEERING_DETAIL_TERMS.get(marker)
    if required_terms:
        require(
            any(term in normalized_value for term in required_terms),
            (
                f"{source_path}: {RUNTIME_ENGINEERING_CONTRACT_HEADING} marker "
                f"'{marker}' must name concrete engineering detail such as "
                f"{', '.join(required_terms[:5])}"
            ),
        )
    if marker == "Workstream Seam Map:":
        require(
            "seam" in normalized_value
            and ("," in value or ";" in value or "->" in value or "\n" in value),
            (
                f"{source_path}: Workstream Seam Map must map multiple seams, "
                "slices, proof gates, or continuation checkpoints"
            ),
        )
    if marker == "Plan-To-Implementation Traceability:":
        require(
            "planned" in normalized_value
            and (
                "actual" in normalized_value
                or "implementation" in normalized_value
                or "trace" in normalized_value
            ),
            (
                f"{source_path}: Plan-To-Implementation Traceability must show "
                "how planned deltas will be compared with actual implementation"
            ),
        )


def _has_negative_runtime_approval_wording(normalized_value: str) -> bool:
    return any(
        term in normalized_value
        for term in RUNTIME_ENGINEERING_NEGATIVE_APPROVAL_TERMS
    )


def _has_positive_runtime_approval_wording(
    normalized_value: str,
    positive_terms: tuple[str, ...],
) -> bool:
    return (
        not _has_negative_runtime_approval_wording(normalized_value)
        and any(term in normalized_value for term in positive_terms)
    )


def _validate_runtime_engineering_contract(
    require,
    source_path: str,
    text: str,
    *,
    branch_class: str,
    current_phase: str,
) -> None:
    if branch_class != "implementation":
        return
    if current_phase not in RUNTIME_ENGINEERING_CONTRACT_ENFORCED_PHASES:
        return

    require(
        f"## {RUNTIME_ENGINEERING_CONTRACT_HEADING}" in text,
        (
            f"{source_path}: implementation runtime planning is missing "
            f"'## {RUNTIME_ENGINEERING_CONTRACT_HEADING}'"
        ),
    )
    contract_section = _section(text, RUNTIME_ENGINEERING_CONTRACT_HEADING)
    for marker in REQUIRED_RUNTIME_ENGINEERING_CONTRACT_MARKERS:
        require(
            marker in contract_section,
            f"{source_path}: {RUNTIME_ENGINEERING_CONTRACT_HEADING} is missing '{marker}'",
        )
        value = _extract_marker_value(contract_section, marker)
        require(
            bool(value),
            (
                f"{source_path}: {RUNTIME_ENGINEERING_CONTRACT_HEADING} must give "
                f"a real value for '{marker}'"
            ),
        )
        if value and marker in RUNTIME_ENGINEERING_CONTRACT_DETAIL_MARKERS:
            _validate_runtime_engineering_contract_substance(
                require,
                source_path,
                marker,
                value,
            )

    status = _extract_marker_value(contract_section, "Engineering Contract Status:")
    planning_review = _extract_marker_value(
        contract_section,
        "USER Engineering Planning Review:",
    )
    implementation_approval = _extract_marker_value(
        contract_section,
        "Runtime Implementation Approval:",
    )
    normalized_status = status.strip().casefold()
    normalized_review = planning_review.strip().casefold()
    normalized_approval = implementation_approval.strip().casefold()

    require(
        normalized_status
        in {
            "proposed",
            "accepted",
            "revised",
            "waived",
            "blocked",
        }
        or any(
            token in normalized_status
            for token in ("proposed", "accepted", "revised", "waived", "blocked")
        ),
        (
            f"{source_path}: Engineering Contract Status must be Proposed, "
            "Accepted, Revised, Waived, or Blocked"
        ),
    )

    if current_phase == "Branch Readiness":
        require(
            any(
                token in normalized_review
                for token in ("required", "accepted", "approved", "revised", "waived")
            ),
            (
                f"{source_path}: USER Engineering Planning Review must record "
                "Required, Accepted/Approved, Revised, or Waived in Branch Readiness"
            ),
        )
        require(
            any(
                token in normalized_approval
                for token in ("pending", "blocked", "not approved", "separate approval")
            ),
            (
                f"{source_path}: Runtime Implementation Approval must remain "
                "Pending/Blocked in Branch Readiness until Workstream is separately admitted"
            ),
        )
    else:
        require(
            _has_positive_runtime_approval_wording(
                normalized_review,
                ("accepted", "approved", "revised", "waived"),
            ),
            (
                f"{source_path}: {current_phase} requires USER Engineering Planning "
                "Review to be accepted, revised, approved, or waived before implementation proof"
            ),
        )
        require(
            _has_positive_runtime_approval_wording(
                normalized_approval,
                ("approved", "granted", "waived"),
            ),
            (
                f"{source_path}: {current_phase} requires Runtime Implementation "
                "Approval to be approved, granted, or waived"
            ),
        )


def _validate_branch_runtime_engineering_plan_substance(
    require,
    source_path: str,
    marker: str,
    value: str,
) -> None:
    normalized_value = _normalized_planning_value(value)
    require(
        normalized_value not in PRODUCT_SYSTEM_PLANNING_HANDWAVE_VALUES,
        (
            f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING} value for "
            f"'{marker}' is placeholder/self-assessed wording, not concrete "
            "branch runtime planning proof"
        ),
    )
    require(
        _planning_word_count(value) >= BRANCH_RUNTIME_ENGINEERING_PLAN_MIN_WORDS,
        (
            f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING} value for "
            f"'{marker}' is too shallow; record concrete branch-specific runtime "
            "baseline, delta, checklist, proof, or traceability detail"
        ),
    )

    required_terms = BRANCH_RUNTIME_ENGINEERING_PLAN_DETAIL_TERMS.get(marker)
    if required_terms:
        require(
            any(term in normalized_value for term in required_terms),
            (
                f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING} marker "
                f"'{marker}' must name concrete runtime plan detail such as "
                f"{', '.join(required_terms[:5])}"
            ),
        )


def _require_branch_plan_any_term(
    require,
    source_path: str,
    marker: str,
    value: str,
    terms: Sequence[str],
    concept: str,
) -> None:
    normalized_value = _normalized_planning_value(value)
    require(
        any(term in normalized_value for term in terms),
        (
            f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING} marker "
            f"'{marker}' must name {concept}"
        ),
    )


def _misclassifies_direct_runtime_as_user_proof(value: str) -> bool:
    normalized_value = _normalized_planning_value(value)
    diagnostic_terms = (
        "supporting evidence only",
        "supporting diagnosis",
        "diagnosis only",
        "diagnostic only",
        "must not",
        "not exact",
        "not formal",
        "not primary",
        "cannot substitute",
        "does not substitute",
    )
    if any(term in normalized_value for term in diagnostic_terms):
        return False
    direct_terms = (
        "direct runtime",
        "helper launch",
        "webview",
        "sandbox",
        "offscreen",
        "dev toolkit",
        "marker",
        "manifest",
        "runtime log",
    )
    proof_terms = (
        "primary proof",
        "formal proof",
        "exact user launcher proof",
        "exact user desktop launcher proof",
        "counts as proof",
        "proof passed",
        "green proof",
        "final proof",
        "acceptance proof",
    )
    return any(term in normalized_value for term in direct_terms) and any(
        term in normalized_value for term in proof_terms
    )


def _validate_runtime_observability_branch_plan_markers(
    require,
    source_path: str,
    plan_section: str,
) -> None:
    runtime_matrix = _extract_marker_value(
        plan_section,
        "Runtime Observability Decision Matrix:",
    )
    exact_launcher = _extract_marker_value(
        plan_section,
        "Exact USER Desktop Launcher Path:",
    )
    parity_plan = _extract_marker_value(plan_section, "Launcher Parity Proof Plan:")
    photo_video_plan = _extract_marker_value(plan_section, "Photo / Video Proof Plan:")
    manual_plan = _extract_marker_value(plan_section, "Manual USER Validation Plan:")
    troubleshooting_decision = _extract_marker_value(
        plan_section,
        "Troubleshooting Mode Decision:",
    )
    packet_plan = _extract_marker_value(plan_section, "USER Packet Evidence Plan:")

    _require_branch_plan_any_term(
        require,
        source_path,
        "Runtime Observability Decision Matrix:",
        runtime_matrix,
        ("launcher", "troubleshooting", "parity"),
        "the exact launcher / troubleshooting / parity proof lanes",
    )
    _require_branch_plan_any_term(
        require,
        source_path,
        "Runtime Observability Decision Matrix:",
        runtime_matrix,
        ("photo", "video", "frame-sequence", "frame sequence"),
        "the photo/video or ordered frame-sequence proof lane",
    )
    _require_branch_plan_any_term(
        require,
        source_path,
        "Runtime Observability Decision Matrix:",
        runtime_matrix,
        ("manual user", "user validation", "user waiver", "blocker"),
        "manual USER validation, waiver, or blocker escalation",
    )
    _require_branch_plan_any_term(
        require,
        source_path,
        "Runtime Observability Decision Matrix:",
        runtime_matrix,
        ("user packet", "review hub", "evidence packet", "uts"),
        "the USER packet / UTS evidence surface",
    )

    _require_branch_plan_any_term(
        require,
        source_path,
        "Exact USER Desktop Launcher Path:",
        exact_launcher,
        (
            "c:\\users\\anden\\onedrive\\desktop\\nexus desktop launcher.lnk",
            "nexus desktop launcher.lnk",
            "exact normal user desktop runtime launcher",
        ),
        "the exact normal USER desktop runtime launcher path",
    )
    require(
        not _misclassifies_direct_runtime_as_user_proof(exact_launcher),
        (
            f"{source_path}: Exact USER Desktop Launcher Path must not classify "
            "direct runtime, helper, Dev Toolkit, marker, manifest, or log evidence "
            "as formal exact USER desktop launcher proof"
        ),
    )

    _require_branch_plan_any_term(
        require,
        source_path,
        "Launcher Parity Proof Plan:",
        parity_plan,
        ("user consent", "consent", "waiver"),
        "USER consent, waiver, or non-use posture before troubleshooting substitution",
    )
    _require_branch_plan_any_term(
        require,
        source_path,
        "Launcher Parity Proof Plan:",
        parity_plan,
        ("same product runtime", "same build", "same data roots"),
        "same-product-runtime, same-build, or same-data-root parity criteria",
    )

    _require_branch_plan_any_term(
        require,
        source_path,
        "Photo / Video Proof Plan:",
        photo_video_plan,
        ("photo", "video", "frame-sequence", "frame sequence", "focused screenshot"),
        "photo/video, ordered frame-sequence, or focused screenshot proof",
    )
    require(
        "screenshot exists" not in _normalized_planning_value(photo_video_plan),
        (
            f"{source_path}: Photo / Video Proof Plan must adjudicate visible claims; "
            "a screenshot-exists marker is not acceptance proof"
        ),
    )

    _require_branch_plan_any_term(
        require,
        source_path,
        "Manual USER Validation Plan:",
        manual_plan,
        ("manual user", "user validation", "user waiver", "blocker", "unphotographable"),
        "manual USER validation, USER waiver, blocker, or unphotographable-claim escalation",
    )

    _require_branch_plan_any_term(
        require,
        source_path,
        "Troubleshooting Mode Decision:",
        troubleshooting_decision,
        ("diagnostic", "supporting evidence", "troubleshooting", "normal launcher"),
        "troubleshooting as diagnostic/supporting evidence and its relationship to the normal launcher",
    )
    require(
        not _misclassifies_direct_runtime_as_user_proof(troubleshooting_decision),
        (
            f"{source_path}: Troubleshooting Mode Decision must not classify "
            "diagnostic/direct runtime evidence as formal USER launcher proof"
        ),
    )

    _require_branch_plan_any_term(
        require,
        source_path,
        "USER Packet Evidence Plan:",
        packet_plan,
        ("user packet", "review hub", "c:\\nexus user", "uts"),
        "the USER review packet, USER review hub, or UTS evidence destination",
    )
    _require_branch_plan_any_term(
        require,
        source_path,
        "USER Packet Evidence Plan:",
        packet_plan,
        ("pass", "fail", "blocked", "unproven", "waived"),
        "PASS / FAIL / BLOCKED / UNPROVEN / WAIVED evidence disposition",
    )


def _markdown_table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_markdown_table_separator(cells: Sequence[str]) -> bool:
    return bool(cells) and all(
        bool(cell) and "-" in cell and set(cell) <= {"-", ":"} for cell in cells
    )


def _element_matrix_requires_active_coverage(normalized_status: str) -> bool:
    return not any(term in normalized_status for term in ("folded", "historical", "retired"))


def _user_branch_plan_review_requires_active_coverage(
    normalized_status: str,
    current_phase: str,
    implementation_approval: str,
) -> bool:
    if not _element_matrix_requires_active_coverage(normalized_status):
        return False
    normalized_phase = _normalized_planning_value(current_phase)
    normalized_approval = _normalized_planning_value(implementation_approval)
    if "branch readiness" in normalized_phase or "workstream entry" in normalized_phase:
        return True
    if "workstream" in normalized_phase and not any(
        term in normalized_phase
        for term in ("complete", "green", "historical", "pr readiness", "release")
    ):
        return True
    approval_blocks_implementation = any(
        term in normalized_approval
        for term in ("pending", "blocked", "not authorized", "separate user decision", "separately gated")
    )
    approval_already_resolved = any(
        term in normalized_approval
        for term in ("approved", "granted", "complete", "completed", "waiver")
    )
    return approval_blocks_implementation and not approval_already_resolved


def _validate_element_to_phase_proof_matrix(
    require,
    source_path: str,
    text: str,
    *,
    require_matrix: bool,
) -> None:
    has_matrix = f"## {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING}" in text
    require(
        has_matrix or not require_matrix,
        (
            f"{source_path}: active external branch planning is missing "
            f"'## {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING}'"
        ),
    )
    if not has_matrix:
        return

    matrix_section = _section(text, ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING)
    for marker in ELEMENT_TO_PHASE_MATRIX_REQUIRED_MARKERS:
        require(
            marker in matrix_section,
            f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} is missing '{marker}'",
        )
        value = _extract_marker_value(matrix_section, marker)
        require(
            bool(value),
            (
                f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} must give "
                f"a real value for '{marker}'"
            ),
        )
        normalized_marker_value = _normalized_planning_value(value)
        allowed_prefixes = ELEMENT_TO_PHASE_MATRIX_MARKER_ALLOWED_PREFIXES.get(marker)
        if allowed_prefixes:
            require(
                any(
                    normalized_marker_value == allowed
                    or normalized_marker_value.startswith(f"{allowed} ")
                    or normalized_marker_value.startswith(f"{allowed} -")
                    for allowed in allowed_prefixes
                ),
                (
                    f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} "
                    f"marker '{marker}' must start with one of: "
                    f"{', '.join(allowed_prefixes)}"
                ),
            )
        if marker in ELEMENT_TO_PHASE_MATRIX_OWNER_MARKERS:
            normalized_owner_path = value.replace("\\", "/")
            require(
                (
                    value.startswith("Docs/")
                    or value.startswith("dev/")
                    or _is_external_branch_plan_path(normalized_owner_path)
                    or "external branch plan" in normalized_marker_value
                    or "external operational state" in normalized_marker_value
                    or "source-truth owner" in normalized_marker_value
                    or "branch runtime engineering plan" in normalized_marker_value
                    or "branch engineering plan" in normalized_marker_value
                    or "element validation ledger" in normalized_marker_value
                ),
                (
                    f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} "
                    f"marker '{marker}' must name a concrete source-truth owner "
                    "or external/repo-relative owner path"
                ),
            )

    table_lines = [
        line.strip()
        for line in matrix_section.splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    header_line = ""
    for line in table_lines:
        cells = _markdown_table_cells(line)
        if cells and cells[0] == "Element ID":
            header_line = line
            break
    require(
        bool(header_line),
        (
            f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} must include "
            "the required markdown table header"
        ),
    )
    if not header_line:
        return

    header = _markdown_table_cells(header_line)
    for column in ELEMENT_TO_PHASE_MATRIX_COLUMNS:
        require(
            column in header,
            (
                f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} table is "
                f"missing '{column}'"
            ),
        )
    if any(column not in header for column in ELEMENT_TO_PHASE_MATRIX_COLUMNS):
        return

    header_index = table_lines.index(header_line)
    rows: list[dict[str, str]] = []
    for line in table_lines[header_index + 1 :]:
        cells = _markdown_table_cells(line)
        if not cells or _is_markdown_table_separator(cells):
            continue
        if len(cells) != len(header):
            require(
                False,
                (
                    f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} row "
                    "must have the same column count as the header"
                ),
            )
            continue
        rows.append(dict(zip(header, cells)))

    require(
        bool(rows),
        f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} requires at least one element row",
    )

    seen_element_ids: set[str] = set()
    for row in rows:
        element_id = row.get("Element ID", "").strip() or "<missing element id>"
        normalized_element_id = _normalized_planning_value(element_id)
        require(
            normalized_element_id not in seen_element_ids,
            (
                f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} row "
                f"{element_id} duplicates an Element ID already used in the matrix"
            ),
        )
        seen_element_ids.add(normalized_element_id)
        for column in ELEMENT_TO_PHASE_MATRIX_COLUMNS:
            value = row.get(column, "").strip()
            require(
                bool(value),
                (
                    f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} row "
                    f"{element_id} must give a real value for '{column}'"
                ),
            )
            normalized_value = _normalized_planning_value(value)
            require(
                normalized_value not in PRODUCT_SYSTEM_PLANNING_HANDWAVE_VALUES,
                (
                    f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} row "
                    f"{element_id} has placeholder/self-assessed value for '{column}'"
                ),
            )

        classification = _normalized_planning_value(
            row.get("Element Classification", "")
        )
        is_current = any(term in classification for term in ELEMENT_TO_PHASE_CURRENT_CLASS_TERMS)
        is_boundary = any(term in classification for term in ELEMENT_TO_PHASE_BOUNDARY_CLASS_TERMS)
        require(
            is_current or is_boundary,
            (
                f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} row "
                f"{element_id} Element Classification must be Planned, Created, "
                "Touched, Affected, Deferred, Future, Dependency-Only, or "
                "Non-Gating Supporting"
            ),
        )
        if is_current:
            for column in (
                "Workstream Implementation Plan",
                "Workstream Proof Plan",
                "Hardening Proof Plan",
                "Live Validation Proof / Waiver Plan",
                "UTS / USER Acceptance Path",
            ):
                value = row.get(column, "")
                require(
                    _planning_word_count(value) >= BRANCH_RUNTIME_ENGINEERING_PLAN_MIN_WORDS,
                    (
                        f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} row "
                        f"{element_id} '{column}' is too shallow; every current "
                        "planned/created/touched/affected element needs a concrete "
                        "phase proof path"
                    ),
                )
        if is_boundary:
            boundary = row.get("Future / Deferred Boundary", "")
            normalized_boundary = _normalized_planning_value(boundary)
            require(
                _planning_word_count(boundary) >= BRANCH_RUNTIME_ENGINEERING_PLAN_MIN_WORDS
                and any(term in normalized_boundary for term in ("future", "defer", "boundary", "non-gating", "non gating", "not current", "not release")),
                (
                    f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} row "
                    f"{element_id} Future / Deferred Boundary must name the "
                    "boundary that keeps the element out of current release gating"
                ),
            )

        decision_state = _normalized_planning_value(row.get("USER Decision State", ""))
        require(
            any(term in decision_state for term in ELEMENT_TO_PHASE_DECISION_TERMS),
            (
                f"{source_path}: {ELEMENT_TO_PHASE_PROOF_MATRIX_HEADING} row "
                f"{element_id} USER Decision State must preserve USER decision "
                "state such as accepted, proposed, deferred, waived, rejected, "
                "superseded, or needs USER decision"
            ),
        )


def _validate_user_branch_plan_review_gate(
    require,
    source_path: str,
    text: str,
    *,
    require_gate: bool,
) -> None:
    has_gate = f"## {USER_BRANCH_PLAN_REVIEW_HEADING}" in text
    require(
        has_gate or not require_gate,
        (
            f"{source_path}: Workstream Entry planning is missing "
            f"'## {USER_BRANCH_PLAN_REVIEW_HEADING}'"
        ),
    )
    if not has_gate:
        return

    gate_section = _section(text, USER_BRANCH_PLAN_REVIEW_HEADING)

    def extract_plan_marker(marker: str) -> str:
        value = _extract_marker_value(gate_section, marker)
        if value:
            return value
        for alias in USER_BRANCH_PLAN_REVIEW_MARKER_ALIASES.get(marker, ()):
            value = _extract_marker_value(gate_section, alias)
            if value:
                return value
        return ""

    for marker in USER_BRANCH_PLAN_REVIEW_REQUIRED_MARKERS:
        aliases = USER_BRANCH_PLAN_REVIEW_MARKER_ALIASES.get(marker, ())
        marker_present = marker in gate_section or any(alias in gate_section for alias in aliases)
        if marker == "USER Review Hub Packet:" and "Desktop Review Bundle:" in gate_section:
            marker_present = True
        require(
            marker_present,
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} is missing '{marker}'",
        )
        value = extract_plan_marker(marker)
        if marker == "USER Review Hub Packet:" and not value:
            value = _extract_marker_value(gate_section, "Desktop Review Bundle:")
        require(
            bool(value),
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} must give "
                f"a real value for '{marker}'"
            ),
        )
        normalized_value = _normalized_planning_value(value)
        require(
            normalized_value not in PRODUCT_SYSTEM_PLANNING_HANDWAVE_VALUES,
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} has "
                f"placeholder/self-assessed value for '{marker}'"
            ),
        )

    review_status = _normalized_planning_value(
        _extract_marker_value(gate_section, "Review Status:")
    )
    require(
        any(
            review_status == prefix
            or review_status.startswith(f"{prefix} ")
            or review_status.startswith(f"{prefix} -")
            for prefix in USER_BRANCH_PLAN_REVIEW_STATUS_PREFIXES
        ),
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} Review Status "
            "must be Accepted by USER, Revised by USER, Deferred With Waiver, "
            "Rejected by USER, or Needs USER Decision"
        ),
    )

    contract_status = _normalized_planning_value(
        _extract_marker_value(gate_section, "Contract Status:")
    )
    require(
        any(
            contract_status == prefix
            or contract_status.startswith(f"{prefix} ")
            or contract_status.startswith(f"{prefix} -")
            for prefix in USER_BRANCH_PLAN_CONTRACT_STATUS_PREFIXES
        ),
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} Contract Status "
            "must be Draft, Pending USER Response, Pending Codex Digest, "
            "Pending USER Confirmation, Complete, or Waived by USER"
        ),
    )

    packet_reviewability_state = _normalized_planning_value(
        _extract_marker_value(gate_section, "Packet Reviewability State:")
    )
    require(
        any(
            packet_reviewability_state == prefix
            or packet_reviewability_state.startswith(f"{prefix} ")
            or packet_reviewability_state.startswith(f"{prefix} -")
            for prefix in USER_BRANCH_PLAN_PACKET_REVIEWABILITY_PREFIXES
        ),
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} Packet "
            "Reviewability State must be Missing, Generated, Validation Failed, "
            "Reviewable, Stale, or Superseded"
        ),
    )

    user_gate_state = _normalized_planning_value(
        _extract_marker_value(gate_section, "USER Gate State:")
    )
    require(
        any(
            user_gate_state == prefix
            or user_gate_state.startswith(f"{prefix} ")
            or user_gate_state.startswith(f"{prefix} -")
            for prefix in USER_BRANCH_PLAN_USER_GATE_STATE_PREFIXES
        ),
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} USER Gate "
            "State must be Pending USER Review, USER Revision Requested, "
            "USER Accepted, USER Approved, USER Waived, USER Rejected, "
            "USER Blocked, or Superseded"
        ),
    )

    for marker in (
        "Plain-Language Branch Goal:",
        "What Will I Actually See, And Where Will I See It?:",
        "Planned User-Facing Outcome:",
        "End-State Vision:",
        "Implementation Breakdown:",
        "Visual / Functional Walkthrough:",
        "Surface Map:",
        "Element-to-Phase Proof Matrix:",
        "Hardening Plan:",
        "Live Validation / UTS Plan:",
        "Codex Recommendations:",
        "Implementation Options:",
        "Recommended Direction:",
        "Why This Fits The Nexus Vision:",
        "USER Plan Review Decision:",
        "Implementation Staging Notes:",
        "Alternatives / Tradeoffs:",
        "USER Plan Review Questions:",
        "USER Decisions Needed:",
        "Implementation Constraints Created By USER Response:",
        "USER Rejected / Deferred Ideas:",
        "Vision Delta / Source-Truth Impact:",
        "Contract Change Log:",
        "Contract Completion Checklist:",
        "Exact USER Decision Needed:",
        "Implementation Approval:",
    ):
        value = extract_plan_marker(marker)
        require(
            _planning_word_count(value) >= BRANCH_RUNTIME_ENGINEERING_PLAN_MIN_WORDS,
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} marker "
                f"'{marker}' is too shallow for USER implementation review"
            ),
        )

    desktop_bundle = _normalized_planning_value(
        _extract_marker_value(gate_section, "USER Review Hub Packet:")
        or _extract_marker_value(gate_section, "Desktop Review Bundle:")
    )
    require(
        "c:\\nexus user" in desktop_bundle
        or "nexus user review" in desktop_bundle
        or "desktop" in desktop_bundle
        or "not required" in desktop_bundle,
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} USER Review "
            "Hub Packet must name the stable local USER hub packet or a not-required reason"
        ),
    )
    review_packet_finding = _extract_marker_value(gate_section, "USER Review Packet Finding:")
    normalized_review_packet_finding = _normalized_planning_value(review_packet_finding)
    for term_group in USER_REVIEW_PACKET_FINDING_REQUIRED_TERMS:
        require(
            any(term.lower() in normalized_review_packet_finding for term in term_group),
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} USER Review "
                "Packet Finding must prove START_HERE.md, USER_BRANCH_PLAN_REVIEW.md, "
                "the exported zip, Source HEAD/current branch HEAD freshness, and "
                "loaded/digested or waiver/blocker status"
            ),
        )

    review_response = _normalized_planning_value(
        _extract_marker_value(gate_section, "USER Review Response:")
    )
    response_digest = _normalized_planning_value(
        _extract_marker_value(gate_section, "Codex Response Digest:")
    )
    require(
        any(term in review_response for term in USER_BRANCH_PLAN_REVIEW_RESPONSE_TERMS),
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} USER Review "
            "Response must record USER response attached/inserted/digested, "
            "Needs USER Response/Pending USER Response, or an explicit waiver/rejection"
        ),
    )
    require(
        any(term in response_digest for term in USER_BRANCH_PLAN_REVIEW_RESPONSE_TERMS),
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} Codex Response "
            "Digest must record that USER response was digested, remains pending, "
            "or was explicitly waived/rejected before Workstream implementation"
        ),
    )

    implementation_breakdown = _normalized_planning_value(
        _extract_marker_value(gate_section, "Implementation Breakdown:")
    )
    require(
        "first-seam-only" not in implementation_breakdown
        and "first seam only" not in implementation_breakdown,
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} cannot be "
            "satisfied by first-seam-only implementation planning"
        ),
    )

    for marker in (
        "End-State Vision:",
        "Visual / Functional Walkthrough:",
        "Surface Map:",
        "Implementation Options:",
        "Recommended Direction:",
        "Why This Fits The Nexus Vision:",
        "USER Plan Review Decision:",
        "Implementation Staging Notes:",
        "USER Decisions Needed:",
        "Implementation Constraints Created By USER Response:",
        "Vision Delta / Source-Truth Impact:",
        "Contract Completion Checklist:",
        "Workstream Entry Result:",
    ):
        value = _normalized_planning_value(extract_plan_marker(marker))
        require(
            not any(term in value for term in ("tbd", "todo", "placeholder", "normal codex digest")),
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} marker "
                f"'{marker}' must be a user-facing engineering plan, not a placeholder"
            ),
        )

    for marker in USER_BRANCH_PLAN_REVIEW_SCOPE_MARKERS:
        value = _normalized_planning_value(_extract_marker_value(gate_section, marker))
        require(
            any(
                term in value
                for term in (
                    "scope",
                    "none",
                    "defer",
                    "future",
                    "reject",
                    "accepted",
                    "waiver",
                )
            ),
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} marker "
                f"'{marker}' must name accepted/deferred/rejected scope or None"
            ),
        )

    implementation_approval = _normalized_planning_value(
        _extract_marker_value(gate_section, "Implementation Approval:")
    )
    require(
        any(
            term in implementation_approval
            for term in ("pending", "approved", "blocked", "waiver", "accepted", "not authorized")
        ),
        (
            f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} Implementation "
            "Approval must preserve the implementation approval boundary"
        ),
    )
    exact_user_decision = _normalized_planning_value(
        _extract_marker_value(gate_section, "Exact USER Decision Needed:")
    )
    blocking_contract = any(
        contract_status == prefix or contract_status.startswith(f"{prefix} ")
        for prefix in USER_BRANCH_PLAN_CONTRACT_BLOCKING_PREFIXES
    )
    blocking_user_gate = any(
        user_gate_state == prefix or user_gate_state.startswith(f"{prefix} ")
        for prefix in USER_BRANCH_PLAN_USER_GATE_BLOCKING_PREFIXES
    )
    implementation_request = (
        "approve bounded slc" in exact_user_decision
        or "approve workstream implementation" in exact_user_decision
        or "approve bounded workstream implementation" in exact_user_decision
        or "implementation approval" in exact_user_decision
    )
    if packet_reviewability_state.startswith("reviewable") and blocking_user_gate:
        require(
            not implementation_request,
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} cannot treat "
                "Packet Reviewability State: Reviewable as USER acceptance while "
                "USER Gate State remains pending, revision-requested, rejected, or blocked"
            ),
        )
    if blocking_contract:
        require(
            not implementation_request,
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} cannot return "
                "implementation approval text while Contract Status is Draft, "
                "Pending USER Response, Pending Codex Digest, or Pending USER Confirmation"
            ),
        )
        require(
            any(
                term in exact_user_decision
                for term in (
                    "contract",
                    "confirmation",
                    "waiver",
                    "waive",
                    "user confirmation",
                )
            ),
            (
                f"{source_path}: {USER_BRANCH_PLAN_REVIEW_HEADING} must ask for "
                "contract confirmation or explicit waiver while Contract Status is blocking"
            ),
        )


def _validate_branch_runtime_engineering_plan(
    require,
    source_path: str,
    text: str,
) -> None:
    require(
        f"## {BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING}" in text,
        (
            f"{source_path}: runtime-focused branch planning is missing "
            f"'## {BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING}'"
        ),
    )
    plan_section = _section(text, BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING)
    for marker in REQUIRED_BRANCH_RUNTIME_ENGINEERING_PLAN_MARKERS:
        require(
            marker in plan_section,
            f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING} is missing '{marker}'",
        )
        value = _extract_marker_value(plan_section, marker)
        require(
            bool(value),
            (
                f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_HEADING} must give "
                f"a real value for '{marker}'"
            ),
        )
        if value and marker in BRANCH_RUNTIME_ENGINEERING_PLAN_DETAIL_MARKERS:
            _validate_branch_runtime_engineering_plan_substance(
                require,
                source_path,
                marker,
                value,
            )
    _validate_runtime_observability_branch_plan_markers(
        require,
        source_path,
        plan_section,
    )

    status = _extract_marker_value(plan_section, "Engineering Plan Status:")
    normalized_status = _normalized_planning_value(status)
    require(
        any(term in normalized_status for term in BRANCH_RUNTIME_ENGINEERING_PLAN_STATUS_TERMS),
        (
            f"{source_path}: Engineering Plan Status must be Required, Proposed, "
            "Present, Accepted, Revised, Folded, or Historical"
        ),
    )

    fold_down_packet = _extract_marker_value(plan_section, "PR Fold-Down Packet:")
    require(
        any(
            token in _normalized_planning_value(fold_down_packet)
            for token in ("pending", "complete", "required", "folded", "historical")
        ),
        (
            f"{source_path}: PR Fold-Down Packet must record Pending, Required, "
            "Complete, Folded, or Historical posture"
        ),
    )

    implementation_approval = _extract_marker_value(
        plan_section,
        "Runtime Implementation Approval:",
    )
    require(
        bool(implementation_approval),
        (
            f"{source_path}: Runtime Implementation Approval must preserve the "
            "implementation approval boundary"
        ),
    )
    _validate_element_to_phase_proof_matrix(
        require,
        source_path,
        text,
        require_matrix=_element_matrix_requires_active_coverage(normalized_status),
    )
    _validate_user_branch_plan_review_gate(
        require,
        source_path,
        text,
        require_gate=_user_branch_plan_review_requires_active_coverage(
            normalized_status,
            _extract_marker_value(plan_section, "Current Phase:"),
            implementation_approval,
        ),
    )
    if f"## {USER_FEEDBACK_DISPOSITION_HEADING}" in text:
        _validate_user_feedback_disposition(require, source_path, text)
    if f"## {BRANCH_CHANGE_INTENT_HEADING}" in text:
        _validate_branch_change_intent_ledger(require, source_path, text)


def _validate_branch_change_intent_ledger(
    require,
    source_path: str,
    text: str,
) -> None:
    require(
        f"## {BRANCH_CHANGE_INTENT_HEADING}" in text,
        (
            f"{source_path}: rebaseline overlap planning is missing "
            f"'## {BRANCH_CHANGE_INTENT_HEADING}'"
        ),
    )
    ledger_section = _section(text, BRANCH_CHANGE_INTENT_HEADING)
    item_matches = list(re.finditer(BRANCH_CHANGE_INTENT_ITEM_HEADING_RE, ledger_section))
    require(
        bool(item_matches),
        f"{source_path}: Branch Change Intent Ledger requires at least one Changed Surface block",
    )

    for item_match in item_matches:
        changed_surface = item_match.group(1).strip()
        item_block = item_match.group(2).strip()
        require(
            bool(changed_surface),
            f"{source_path}: Changed Surface heading must name the overlapping file path",
        )
        for marker in BRANCH_CHANGE_INTENT_MARKERS:
            require(
                marker in item_block,
                f"{source_path}: Changed Surface {changed_surface} is missing '{marker}'",
            )
            value = _extract_marker_value(item_block, marker)
            require(
                bool(value),
                (
                    f"{source_path}: Changed Surface {changed_surface} must give "
                    f"a real value for '{marker}'"
                ),
            )

        surface_class = _normalized_planning_value(
            _extract_marker_value(item_block, "Surface Class:")
        )
        semantic_risk = _normalized_planning_value(
            _extract_marker_value(item_block, "Semantic Merge Risk:")
        )
        regression_impact = _normalized_planning_value(
            _extract_marker_value(item_block, "Regression / Gating Impact:")
        )
        resolution_owner = _normalized_planning_value(
            _extract_marker_value(item_block, "Resolution Owner:")
        )
        fallback_evidence = _normalized_planning_value(
            _extract_marker_value(item_block, "Fallback Evidence:")
        )
        validation_proof = _normalized_planning_value(
            _extract_marker_value(item_block, "Validation Proof:")
        )
        user_decision = _normalized_planning_value(
            _extract_marker_value(item_block, "USER Decision / Waiver:")
        )

        require(
            surface_class in BRANCH_CHANGE_INTENT_SURFACE_CLASSES,
            (
                f"{source_path}: Changed Surface {changed_surface} Surface Class "
                "must use the approved Rebaseline Overlap Intent Gate class list"
            ),
        )
        require(
            semantic_risk in BRANCH_CHANGE_INTENT_SEMANTIC_RISK_VALUES,
            (
                f"{source_path}: Changed Surface {changed_surface} Semantic Merge Risk "
                "must be None, Low, Medium, High, or Unknown"
            ),
        )
        require(
            regression_impact in BRANCH_CHANGE_INTENT_REGRESSION_GATING_VALUES,
            (
                f"{source_path}: Changed Surface {changed_surface} Regression / "
                "Gating Impact must be None, Low, Medium, High, or Unknown"
            ),
        )
        require(
            resolution_owner in BRANCH_CHANGE_INTENT_RESOLUTION_OWNERS,
            (
                f"{source_path}: Changed Surface {changed_surface} Resolution Owner "
                "must be Current Branch, Incoming/Folded Owner, Originating Lane, "
                "Standing Governance, USER Decision, or Future Branch"
            ),
        )
        if surface_class in BRANCH_CHANGE_INTENT_HIGH_RISK_CLASSES:
            require(
                semantic_risk != "unknown",
                (
                    f"{source_path}: Changed Surface {changed_surface} Semantic Merge "
                    "Risk Unknown is blocked for high-risk overlap surfaces"
                ),
            )
        if surface_class == "fixture/test":
            require(
                regression_impact not in {"medium", "high", "unknown"},
                (
                    f"{source_path}: Changed Surface {changed_surface} Regression / "
                    "Gating Impact Medium, High, or Unknown blocks fixture/test overlap"
                ),
            )
        require(
            "fallback only" not in fallback_evidence
            and not (
                "compatibility bypass" in fallback_evidence
                and "not a compatibility bypass" not in fallback_evidence
            ),
            (
                f"{source_path}: Changed Surface {changed_surface} Fallback Evidence "
                "cannot be used as a compatibility bypass"
            ),
        )
        require(
            "validation" in validation_proof or "not run" in validation_proof,
            (
                f"{source_path}: Changed Surface {changed_surface} Validation Proof "
                "must name required validation or the reason validation has not run yet"
            ),
        )
        require(
            any(term in user_decision for term in ("user", "waiver", "approved", "pending", "not required")),
            (
                f"{source_path}: Changed Surface {changed_surface} USER Decision / "
                "Waiver must preserve the USER decision boundary"
            ),
        )


def _validate_branch_vision_contract_snapshot(
    require,
    source_path: str,
    text: str,
) -> None:
    require(
        f"## {BRANCH_VISION_CONTRACT_HEADING}" in text,
        (
            f"{source_path}: user-facing or runtime branch planning is missing "
            f"'## {BRANCH_VISION_CONTRACT_HEADING}'"
        ),
    )

    vision_section = _section(text, BRANCH_VISION_CONTRACT_HEADING)
    for marker in BRANCH_VISION_CONTRACT_REQUIRED_MARKERS:
        require(
            marker in vision_section,
            f"{source_path}: {BRANCH_VISION_CONTRACT_HEADING} is missing '{marker}'",
        )
        value = _extract_marker_value(vision_section, marker)
        require(
            bool(value),
            (
                f"{source_path}: {BRANCH_VISION_CONTRACT_HEADING} must give "
                f"a real value for '{marker}'"
            ),
        )

    required = _normalized_planning_value(
        _extract_marker_value(vision_section, "Vision Contract Required:")
    )
    status = _normalized_planning_value(
        _extract_marker_value(vision_section, "Branch Vision Snapshot Status:")
    )
    open_questions = _normalized_planning_value(
        _extract_marker_value(vision_section, "Open Vision Questions:")
    )
    user_green = _normalized_planning_value(
        _extract_marker_value(vision_section, "USER Vision Green:")
    )
    assumption_ledger = _normalized_planning_value(
        _extract_marker_value(vision_section, "Design Assumption Ledger:")
    )
    severity_policy = _normalized_planning_value(
        _extract_marker_value(vision_section, "Question Severity Policy:")
    )
    traceability = _normalized_planning_value(
        _extract_marker_value(vision_section, "Vision-to-Implementation Traceability:")
    )
    revision_packet = _normalized_planning_value(
        _extract_marker_value(vision_section, "Branch Plan Revision Packet:")
    )

    is_required = "yes" in required or "required" in required
    if is_required:
        require(
            any(term in status for term in BRANCH_VISION_SAFE_STATE_TERMS),
            (
                f"{source_path}: Branch Vision Snapshot Status must be accepted, "
                "revised, deferred with waiver, waived, or not required before "
                "implementation-safe planning"
            ),
        )
        require(
            any(term in user_green for term in ("yes", "green", "accepted", "waived")),
            (
                f"{source_path}: USER Vision Green must be Yes/Green/Accepted "
                "or explicitly waived before implementation-safe planning"
            ),
        )

    require(
        not any(term in status for term in BRANCH_VISION_UNSAFE_STATE_TERMS),
        (
            f"{source_path}: Branch Vision Snapshot Status cannot stay Proposed, "
            "Recommended, Pending, Blocking, or Needs USER Decision for "
            "implementation-safe planning"
        ),
    )
    require(
        "blocking" not in open_questions
        and "needs user" not in open_questions
        and "unanswered" not in open_questions,
        (
            f"{source_path}: Open Vision Questions must be None, queued "
            "non-blocking, or Deferred With Waiver before implementation-safe planning"
        ),
    )
    require(
        any(term in assumption_ledger for term in ("accepted by user", "revised by user", "deferred with waiver", "waived", "not required")),
        (
            f"{source_path}: Design Assumption Ledger must show USER-accepted, "
            "USER-revised, USER-deferred-with-waiver, waived, or not-required "
            "decision state; Codex or ChatGPT recommendations alone are not safe"
        ),
    )
    require(
        (
            "level 1" in severity_policy
            and "level 2" in severity_policy
            and "level 3" in severity_policy
        )
        or (
            "non-blocking" in severity_policy
            and "seam-blocking" in severity_policy
            and "workstream-breaking" in severity_policy
        ),
        (
            f"{source_path}: Question Severity Policy must distinguish Level 1 "
            "non-blocking, Level 2 seam-blocking, and Level 3 workstream-breaking "
            "vision questions"
        ),
    )
    for term in BRANCH_VISION_TRACEABILITY_TERMS:
        require(
            term in traceability,
            (
                f"{source_path}: Vision-to-Implementation Traceability must map "
                f"accepted vision to branch/seam/files/validator/proof; missing {term!r}"
            ),
        )
    require(
        "user" in revision_packet and "decision" in revision_packet,
        (
            f"{source_path}: Branch Plan Revision Packet must require USER "
            "decision when accepted vision or implementation scope changes"
        ),
    )


def _validate_user_feedback_disposition(
    require,
    source_path: str,
    text: str,
) -> None:
    require(
        f"## {USER_FEEDBACK_DISPOSITION_HEADING}" in text,
        (
            f"{source_path}: meaningful-feedback planning is missing "
            f"'## {USER_FEEDBACK_DISPOSITION_HEADING}'"
        ),
    )
    ufd_section = _section(text, USER_FEEDBACK_DISPOSITION_HEADING)

    for marker in USER_FEEDBACK_DISPOSITION_LEDGER_MARKERS:
        require(
            marker in ufd_section,
            f"{source_path}: {USER_FEEDBACK_DISPOSITION_HEADING} is missing '{marker}'",
        )
        value = _extract_marker_value(ufd_section, marker)
        require(
            bool(value),
            (
                f"{source_path}: {USER_FEEDBACK_DISPOSITION_HEADING} must give "
                f"a real value for '{marker}'"
            ),
        )

    ledger_status = _normalized_planning_value(
        _extract_marker_value(ufd_section, "UFD Ledger Status:")
    )
    require(
        any(term in ledger_status for term in USER_FEEDBACK_DISPOSITION_LEDGER_STATUSES),
        (
            f"{source_path}: UFD Ledger Status must be Open, Queued, Blocking, Closed, "
            "Folded Down, Deferred, Superseded, Pending, Complete, Not Required, "
            "or Not Applicable"
        ),
    )

    ledger_owner = _extract_marker_value(ufd_section, "UFD Ledger Owner:").strip()
    normalized_ledger_owner = ledger_owner.replace("\\", "/")
    require(
        _is_external_branch_plan_path(normalized_ledger_owner)
        or _is_repo_branch_plan_path(normalized_ledger_owner),
        (
            f"{source_path}: UFD Ledger Owner must point to the active external "
            "C:\\Nexus Governance State\\branches\\<branch_slug>\\branch_plan.md "
            "branch plan or a repo branch-plan historical receipt"
        ),
    )

    fold_down_status = _normalized_planning_value(
        _extract_marker_value(ufd_section, "Fold-Down Status:")
    )
    require(
        any(
            term in fold_down_status
            for term in USER_FEEDBACK_DISPOSITION_FOLD_DOWN_STATUSES
        ),
        (
            f"{source_path}: Fold-Down Status must be Pending, Required, Complete, "
            "Folded, Retired, Historical, Not Required, or Not Applicable"
        ),
    )

    def _marker_count(marker: str) -> int:
        value = _extract_marker_value(ufd_section, marker)
        match = re.search(r"\d+", value)
        require(bool(match), f"{source_path}: {marker} must contain a numeric count")
        return int(match.group(0)) if match else -1

    declared_open_count = _marker_count("Open UFD Count:")
    declared_blocking_count = _marker_count("Blocking UFD Count:")

    item_matches = list(
        re.finditer(
            r"(?ms)^### UFD Item:\s*(UFD-[^\n]+)\n(.*?)(?=^### UFD Item:|\Z)",
            ufd_section,
        )
    )
    required_value = _normalized_planning_value(
        _extract_marker_value(ufd_section, "USER Feedback Disposition Required:")
    )
    requires_items = (
        "yes" in required_value
        or declared_open_count > 0
        or declared_blocking_count > 0
    )
    require(
        item_matches or not requires_items,
        f"{source_path}: UFD ledger requires at least one '### UFD Item: UFD-*' block",
    )

    open_items = 0
    blocking_items = 0
    seen_feedback_ids: set[str] = set()
    seen_feedback_summaries: dict[str, str] = {}

    def _normalized_feedback_summary_key(value: str) -> str:
        folded = value.casefold()
        alnum_text = "".join(ch if ch.isalnum() else " " for ch in folded)
        normalized = re.sub(r"\s+", " ", alnum_text).strip()
        if normalized:
            return normalized
        return re.sub(r"\s+", " ", folded).strip()

    for item_match in item_matches:
        heading_id = item_match.group(1).strip()
        item_block = item_match.group(2).strip()
        normalized_heading_id = heading_id.casefold()
        require(
            normalized_heading_id.startswith("ufd-"),
            f"{source_path}: UFD item heading must use the UFD-* namespace",
        )
        require(
            normalized_heading_id not in seen_feedback_ids,
            f"{source_path}: duplicate UFD item heading {heading_id}",
        )
        seen_feedback_ids.add(normalized_heading_id)

        for marker in USER_FEEDBACK_DISPOSITION_ITEM_MARKERS:
            require(marker in item_block, f"{source_path}: {heading_id} is missing '{marker}'")
            value = _extract_marker_value(item_block, marker)
            require(
                bool(value),
                f"{source_path}: {heading_id} must give a real value for '{marker}'",
            )

        feedback_id = _extract_marker_value(item_block, "Feedback ID:").strip()
        normalized_feedback_id = feedback_id.casefold()
        require(
            normalized_feedback_id.startswith("ufd-"),
            f"{source_path}: Feedback ID must use the UFD-* namespace",
        )
        require(
            not normalized_feedback_id.startswith("fbk-"),
            f"{source_path}: Feedback ID must not use FBK-* because it collides with FB-*",
        )
        require(
            normalized_feedback_id == normalized_heading_id,
            f"{source_path}: Feedback ID must match UFD item heading {heading_id}",
        )

        feedback_summary = _extract_marker_value(item_block, "Feedback Summary:").strip()
        normalized_feedback_summary = _normalized_feedback_summary_key(feedback_summary)
        require(
            normalized_feedback_summary not in seen_feedback_summaries,
            (
                f"{source_path}: duplicate UFD Feedback Summary between "
                f"{seen_feedback_summaries.get(normalized_feedback_summary, 'another UFD item')} "
                f"and {heading_id}; duplicate meaningful feedback must be merged, "
                "superseded with No-Action Reason, or assigned a distinct summary"
            ),
        )
        seen_feedback_summaries[normalized_feedback_summary] = heading_id

        disposition_type = _normalized_planning_value(
            _extract_marker_value(item_block, "Disposition Type:")
        )
        require(
            any(term in disposition_type for term in USER_FEEDBACK_DISPOSITION_TYPES),
            (
                f"{source_path}: {heading_id} Disposition Type must be a recognized "
                "UFD disposition such as Current Branch Requirement, Future Branch "
                "Candidate, Branch Receipt Item, Workstream / Family Dossier Item, "
                "or Rejected / No Action"
            ),
        )

        decision_state = _normalized_planning_value(
            _extract_marker_value(item_block, "USER Decision State:")
        )
        require(
            any(term in decision_state for term in USER_FEEDBACK_DISPOSITION_ALLOWED_STATES),
            (
                f"{source_path}: {heading_id} USER Decision State must be Proposed "
                "by Codex, Recommended by ChatGPT, Accepted/Revised/Rejected/Deferred "
                "by USER, Deferred With Waiver, Superseded, or Needs USER Decision"
            ),
        )

        owner_class = _normalized_planning_value(
            _extract_marker_value(item_block, "Owner Class:")
        )
        require(
            any(term in owner_class for term in USER_FEEDBACK_DISPOSITION_OWNER_CLASSES),
            f"{source_path}: {heading_id} Owner Class must name a recognized UFD owner class",
        )

        canonical_owner = _extract_marker_value(item_block, "Canonical Owner File:").strip()
        no_durable_owner = "no durable owner needed" in owner_class
        if no_durable_owner:
            no_action_reason = _extract_marker_value(item_block, "No-Action Reason:")
            require(
                bool(no_action_reason),
                (
                    f"{source_path}: No Durable Owner Needed requires No-Action Reason "
                    "so meaningful-looking feedback is not silently dropped"
                ),
            )
        else:
            require(
                canonical_owner.startswith("Docs/"),
                (
                    f"{source_path}: {heading_id} Canonical Owner File must point to "
                    "a Docs/ owner unless Owner Class is No Durable Owner Needed"
                ),
            )

        severity = _normalized_planning_value(
            _extract_marker_value(item_block, "Workstream Severity:")
        )
        require(
            any(term in severity for term in USER_FEEDBACK_DISPOSITION_SEVERITY_TERMS),
            (
                f"{source_path}: {heading_id} Workstream Severity must distinguish "
                "Level 1 non-blocking, Level 2 seam-blocking, or Level 3 "
                "workstream-breaking"
            ),
        )

        status = _normalized_planning_value(_extract_marker_value(item_block, "Status:"))
        require(
            any(term in status for term in USER_FEEDBACK_DISPOSITION_ALLOWED_STATUSES),
            (
                f"{source_path}: {heading_id} Status must be Open, Queued, Blocking, "
                "Closed, Folded Down, Deferred, or Superseded"
            ),
        )
        if any(term in status for term in ("open", "queued", "blocking", "deferred")):
            open_items += 1
        if "blocking" in status:
            blocking_items += 1

        fold_down_target = _normalized_planning_value(
            _extract_marker_value(item_block, "Fold-Down Target:")
        )
        require(
            any(
                term in fold_down_target
                for term in (
                    "docs/",
                    "branch record",
                    "branch receipt",
                    "workstream",
                    "dossier",
                    "nexus vision",
                    "family vision",
                    "backlog pointer",
                    "governance receipt",
                    "no durable owner needed",
                )
            ),
            f"{source_path}: {heading_id} Fold-Down Target must name the final UFD owner or no-action posture",
        )

        no_action_text = f"{disposition_type} {status} {owner_class} {fold_down_target}"
        if any(
            term in no_action_text
            for term in (
                "no action",
                "no durable",
                "duplicate",
                "superseded",
                "non-actionable",
            )
        ):
            no_action_reason = _extract_marker_value(item_block, "No-Action Reason:")
            require(
                bool(no_action_reason),
                (
                    f"{source_path}: {heading_id} no-action, no-durable, duplicate, "
                    "superseded, or non-actionable posture requires No-Action Reason"
                ),
            )

        pointer_locations = _extract_marker_value(item_block, "Pointer Locations:")
        normalized_pointers = _normalized_planning_value(pointer_locations)
        require(
            "full feedback text" not in normalized_pointers
            and "full decision history" not in normalized_pointers
            and "live implementation state" not in normalized_pointers,
            (
                f"{source_path}: {heading_id} Pointer Locations may carry UFD ID, "
                "short title, canonical owner, compact status, and fold-down status only"
            ),
        )

    require(
        declared_open_count == open_items,
        (
            f"{source_path}: Open UFD Count {declared_open_count} does not match "
            f"open/queued/blocking/deferred UFD item count {open_items}"
        ),
    )
    require(
        declared_blocking_count == blocking_items,
        (
            f"{source_path}: Blocking UFD Count {declared_blocking_count} does not "
            f"match blocking UFD item count {blocking_items}"
        ),
    )


def _validate_branch_runtime_engineering_plan_pointer(
    require,
    source_path: str,
    text: str,
    *,
    branch_class: str,
    current_phase: str,
) -> None:
    if branch_class != "implementation":
        return
    if current_phase not in RUNTIME_ENGINEERING_CONTRACT_ENFORCED_PHASES:
        return

    plan_state = _extract_marker_value(text, BRANCH_RUNTIME_ENGINEERING_PLAN_POINTER_LABEL)
    plan_path = _extract_marker_value(text, BRANCH_RUNTIME_ENGINEERING_PLAN_PATH_LABEL)
    plan_status = _extract_marker_value(text, "Engineering Plan Status:")
    if not plan_state and not plan_path and not plan_status:
        return

    normalized_state = _normalized_planning_value(plan_state)
    normalized_status = _normalized_planning_value(plan_status)
    require(
        plan_state,
        (
            f"{source_path}: runtime-focused branch plan pointer is missing "
            f"'{BRANCH_RUNTIME_ENGINEERING_PLAN_POINTER_LABEL}'"
        ),
    )
    require(
        any(
            term in f"{normalized_state} {normalized_status}"
            for term in BRANCH_RUNTIME_ENGINEERING_PLAN_STATUS_TERMS
        ),
        (
            f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_POINTER_LABEL} must "
            "record Required, Proposed, Present, Accepted, Revised, Folded, or Historical"
        ),
    )

    must_have_plan_file = current_phase != "Branch Readiness" or any(
        term in f"{normalized_state} {normalized_status}"
        for term in ("present", "accepted", "revised", "folded", "historical")
    )
    if not must_have_plan_file:
        return

    normalized_path = plan_path.replace("\\", "/")
    require(
        bool(plan_path),
        f"{source_path}: accepted/present runtime plan pointer is missing '{BRANCH_RUNTIME_ENGINEERING_PLAN_PATH_LABEL}'",
    )
    plan_path_valid = _is_external_branch_plan_path(normalized_path) or _is_repo_branch_plan_path(
        normalized_path
    )
    require(
        plan_path_valid,
        (
            f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_PATH_LABEL} must point "
            "to C:\\Nexus Governance State\\branches\\<branch_slug>\\branch_plan.md "
            f"for active planning or under {BRANCH_RUNTIME_ENGINEERING_PLAN_DIRECTORY}<branch_slug>.md "
            "for repo historical receipts"
        ),
    )
    if not (plan_path and plan_path_valid):
        return
    if _is_external_branch_plan_path(normalized_path):
        return
    plan_file = ROOT_DIR / normalized_path
    require(
        plan_file.is_file(),
        (
            f"{source_path}: {BRANCH_RUNTIME_ENGINEERING_PLAN_PATH_LABEL} points "
            f"to missing file '{normalized_path}'"
        ),
    )
    if not plan_file.is_file():
        return
    _validate_branch_runtime_engineering_plan(
        require,
        normalized_path,
        plan_file.read_text(encoding="utf-8"),
    )


def _validate_branch_runtime_backlog_compactness(
    require,
    source_path: str,
    text: str,
) -> None:
    for marker in BRANCH_RUNTIME_ENGINEERING_PLAN_COMPACTNESS_FORBIDDEN_MARKERS:
        require(
            marker not in text,
            (
                f"{source_path}: backlog/roadmap compact pointer surfaces must not "
                f"own detailed Branch Runtime Engineering Plan marker '{marker}'"
            ),
        )


def _validate_product_definition_plan(
    require,
    source_path: str,
    text: str,
    *,
    branch_class: str,
    current_phase: str,
    blockers: list[str],
    next_legal_phase: str,
) -> None:
    if branch_class != "implementation":
        return
    if current_phase not in PRODUCT_PLANNING_ENFORCED_PHASES:
        return

    require(
        f"## {PRODUCT_DEFINITION_PLAN_HEADING}" in text,
        (
            f"{source_path}: implementation Branch Readiness is missing "
            f"'## {PRODUCT_DEFINITION_PLAN_HEADING}'"
        ),
    )
    plan_section = _section(text, PRODUCT_DEFINITION_PLAN_HEADING)
    for marker in REQUIRED_PRODUCT_DEFINITION_MARKERS:
        require(
            marker in plan_section,
            f"{source_path}: {PRODUCT_DEFINITION_PLAN_HEADING} is missing '{marker}'",
        )
    for marker in REQUIRED_PRODUCT_SYSTEM_PLANNING_MARKERS:
        value = _extract_marker_value(plan_section, marker)
        require(
            bool(value),
            (
                f"{source_path}: {PRODUCT_DEFINITION_PLAN_HEADING} must give a real "
                f"planning value for '{marker}'"
            ),
        )
        if value:
            _validate_product_system_planning_substance(
                require,
                source_path,
                marker,
                value,
            )

    planning_status = _extract_marker_value(plan_section, "Planning Packet Status:")
    revalidation_status = _extract_marker_value(plan_section, "Planning Revalidation Status:")
    planning_waiver = _extract_marker_value(plan_section, PRODUCT_PLANNING_WAIVER_MARKER)
    normalized_status = planning_status.strip().casefold()
    normalized_revalidation = revalidation_status.strip().casefold()
    normalized_waiver = planning_waiver.strip().casefold()
    has_planning_blocker = PRODUCT_PLANNING_INCOMPLETE_BLOCKER in blockers

    require(
        bool(planning_status),
        f"{source_path}: {PRODUCT_DEFINITION_PLAN_HEADING} is missing 'Planning Packet Status:' value",
    )
    require(
        bool(revalidation_status),
        f"{source_path}: {PRODUCT_DEFINITION_PLAN_HEADING} is missing 'Planning Revalidation Status:' value",
    )
    require(
        PRODUCT_PLANNING_WAIVER_MARKER in plan_section,
        f"{source_path}: {PRODUCT_DEFINITION_PLAN_HEADING} is missing '{PRODUCT_PLANNING_WAIVER_MARKER}'",
    )

    if normalized_status in PRODUCT_PLANNING_INCOMPLETE_VALUES:
        require(
            has_planning_blocker,
            (
                f"{source_path}: incomplete family-package planning must record "
                f"'{PRODUCT_PLANNING_INCOMPLETE_BLOCKER}' under Blockers"
            ),
        )
        question_packet = _section(text, USER_VISION_QUESTION_PACKET_HEADING)
        require(
            bool(question_packet),
            (
                f"{source_path}: incomplete family-package planning with USER input "
                f"needed must include '## {USER_VISION_QUESTION_PACKET_HEADING}'"
            ),
        )
        if question_packet:
            for marker in REQUIRED_USER_VISION_QUESTION_PACKET_MARKERS:
                require(
                    marker in question_packet,
                    (
                        f"{source_path}: {USER_VISION_QUESTION_PACKET_HEADING} is "
                        f"missing '{marker}'"
                    ),
                )
            for category in REQUIRED_USER_VISION_QUESTION_PACKET_CATEGORIES:
                require(
                    category in question_packet,
                    (
                        f"{source_path}: {USER_VISION_QUESTION_PACKET_HEADING} is "
                        f"missing required category '{category}'"
                    ),
                )
            if "FAM-006" in text:
                for marker in FAM_006_USER_VISION_PACKET_MARKERS:
                    require(
                        marker in question_packet,
                        (
                            f"{source_path}: FAM-006 {USER_VISION_QUESTION_PACKET_HEADING} "
                            f"is missing '{marker}'"
                        ),
                    )
        _validate_user_vision_input_handoff(require, source_path, text, blockers)
        require(
            current_phase == "Branch Readiness",
            (
                f"{source_path}: incomplete family-package planning must stay in "
                "`Branch Readiness` and cannot enter implementation"
            ),
        )
        require(
            next_legal_phase == "Branch Readiness",
            (
                f"{source_path}: incomplete family-package planning must keep "
                "Next Legal Phase at `Branch Readiness`"
            ),
        )
    elif normalized_status == "waived":
        require(
            "user" in normalized_waiver and (
                "approved" in normalized_waiver
                or "approval" in normalized_waiver
                or "waiver" in normalized_waiver
            ),
            (
                f"{source_path}: waived family-package planning requires "
                f"'{PRODUCT_PLANNING_WAIVER_MARKER}' to record explicit USER waiver"
            ),
        )
    else:
        require(
            normalized_status in PRODUCT_PLANNING_COMPLETE_VALUES,
            (
                f"{source_path}: Planning Packet Status '{planning_status}' must be "
                "Complete, Incomplete, Pending, Blocked, or Waived"
            ),
        )
        require(
            normalized_revalidation in {"pass", "green", "complete", "waived"},
            (
                f"{source_path}: complete family-package planning requires "
                "'Planning Revalidation Status:' to be PASS, Green, Complete, or Waived"
            ),
        )

    if current_phase in PRODUCT_PLANNING_EXECUTION_PHASES:
        require(
            normalized_status in PRODUCT_PLANNING_COMPLETE_VALUES,
            (
                f"{source_path}: {current_phase} implementation requires complete or "
                "USER-waived family-package planning before leaving Branch Readiness"
            ),
        )


def _validate_fam006_stage2_r6_plan(
    require,
    source_path: str,
    text: str,
    *,
    blockers: list[str],
    current_phase: str,
) -> None:
    if Path(source_path) != FAM006_BRANCH_RECORD:
        return

    section = _section(text, FAM006_STAGE2_R6_HEADING)
    require(
        bool(section),
        f"{source_path}: FAM-006 plan is missing '## {FAM006_STAGE2_R6_HEADING}'",
    )
    if not section:
        return

    for marker in FAM006_STAGE2_R6_REQUIRED_MARKERS:
        require(
            marker in section,
            f"{source_path}: {FAM006_STAGE2_R6_HEADING} is missing '{marker}'",
        )
    for phrase in FAM006_STAGE2_R6_REQUIRED_PHRASES:
        require(
            phrase in section,
            f"{source_path}: {FAM006_STAGE2_R6_HEADING} is missing '{phrase}'",
        )

    stage2_r9_section = _section(text, FAM006_STAGE2_R9_HEADING)
    stage2_r10_section = _section(text, FAM006_STAGE2_R10_HEADING)
    cleared_by_stage2_r6 = {
        "Branch Reach Unproven",
        "Acceptance Criteria Missing",
        "Current Branch vs Future Package Boundary Missing",
        HARDWARE_TELEMETRY_PROVIDER_PENDING_BLOCKER,
        POLLING_FLOOR_UNDECIDED_BLOCKER,
        WARNING_DELIVERY_MODALITY_PENDING_BLOCKER,
        EXTERNAL_TELEMETRY_PRIVACY_MODEL_MISSING_BLOCKER,
        AUDIO_WARNING_CROSS_FAMILY_APPROVAL_MISSING_BLOCKER,
    }
    if stage2_r9_section:
        cleared_by_stage2_r6 = {
            "Acceptance Criteria Missing",
            POLLING_FLOOR_UNDECIDED_BLOCKER,
            WARNING_DELIVERY_MODALITY_PENDING_BLOCKER,
            AUDIO_WARNING_CROSS_FAMILY_APPROVAL_MISSING_BLOCKER,
        }
    if stage2_r10_section:
        cleared_by_stage2_r6 = {
            "Branch Reach Unproven",
            "Acceptance Criteria Missing",
            "Current Branch vs Future Package Boundary Missing",
            HARDWARE_TELEMETRY_PROVIDER_PENDING_BLOCKER,
            POLLING_FLOOR_UNDECIDED_BLOCKER,
            WARNING_DELIVERY_MODALITY_PENDING_BLOCKER,
            EXTERNAL_TELEMETRY_PRIVACY_MODEL_MISSING_BLOCKER,
            AUDIO_WARNING_CROSS_FAMILY_APPROVAL_MISSING_BLOCKER,
            PERSONA_SWITCH_SCOPE_BOUNDARY_PENDING_BLOCKER,
        }
    for blocker in cleared_by_stage2_r6:
        require(
            blocker not in blockers,
            (
                f"{source_path}: '{blocker}' must not remain active after Stage 2-R6 "
                "finalizes the corresponding boundary; keep it as cleared/deferred history instead"
            ),
        )

    plan_section = _section(text, PRODUCT_DEFINITION_PLAN_HEADING)
    require(
        (
            "Current Branch vs Future Package Boundaries: finalized by Stage 2-R6"
            in plan_section
            or "Current Branch vs Future Package Boundaries: rebaselined by Stage 2-R9"
            in plan_section
            or "Current Branch vs Future Package Boundaries: Stage 2-R12 supersedes"
            in plan_section
        ),
        (
            f"{source_path}: Product Definition Plan must mark current/future package "
            "boundaries as finalized by Stage 2-R6 or rebaselined by Stage 2-R9"
        ),
    )
    require(
        (
            "Acceptance Criteria: finalized by Stage 2-R6" in plan_section
            or "Acceptance Criteria: rebaselined by Stage 2-R9" in plan_section
            or "Acceptance Criteria: Stage 2-R12 rebaselines"
            in plan_section
        ),
        (
            f"{source_path}: Product Definition Plan must mark acceptance criteria "
            "as finalized by Stage 2-R6 or rebaselined by Stage 2-R9"
        ),
    )
    stage2_r8_section = _section(text, FAM006_STAGE2_R8_HEADING)
    stage2_r9_section = _section(text, FAM006_STAGE2_R9_HEADING)
    stage2_r10_section = _section(text, FAM006_STAGE2_R10_HEADING)
    stage2_r11_section = _section(text, FAM006_STAGE2_R11_HEADING)
    stage2_r12_section = _section(text, FAM006_STAGE2_R12_HEADING)
    stage2_r13_section = _section(text, FAM006_STAGE2_R13_HEADING)
    ws31_section = _section(text, FAM006_WS31_HEADING)
    ws32_section = _section(text, FAM006_WS32_HEADING)
    ws33_section = _section(text, FAM006_WS33_HEADING)
    has_stage2_r8_blocker = LEGACY_PRODUCT_NAME_DRIFT_BLOCKER in blockers

    if current_phase == "Branch Readiness":
        if stage2_r12_section:
            for phrase in FAM006_STAGE2_R12_REQUIRED_PHRASES:
                require(
                    phrase in stage2_r12_section,
                    f"{source_path}: {FAM006_STAGE2_R12_HEADING} is missing '{phrase}'",
                )
            if not stage2_r13_section:
                for active_blocker in (
                    "Dashboard Acceptance Pending",
                    "Overlay Scope Deferred",
                    "Core Repair Dependency Only",
                    "Branch Readiness Interface Planning Incomplete",
                ):
                    require(
                        active_blocker in blockers,
                        (
                            f"{source_path}: Stage 2-R12 repair must keep "
                            f"'{active_blocker}' active until Stage 1-R10 revalidation"
                        ),
                    )
            require(
                "Primary Interface Release Surface: `Monitoring HUD Dashboard / control panel`"
                in text,
                f"{source_path}: Stage 2-R12 repair must declare the Dashboard/control panel primary interface",
            )
            require(
                "Branch Readiness Stage 1-R10 - Dashboard-First Interface Boundary Revalidation"
                in text,
                (
                    f"{source_path}: Stage 2-R12 repair must set next legal seam "
                    "to Stage 1-R10 revalidation"
                ),
            )
            require(
                "Handoff Readiness: `SUPERSEDED - not ready for Hardening under current Stage 2-R12 authority."
                in text,
                (
                    f"{source_path}: Stage 2-R12 repair must explicitly supersede "
                    "the prior Hardening handoff"
                ),
            )
            return
        if stage2_r11_section:
            for phrase in FAM006_STAGE2_R11_REQUIRED_PHRASES:
                require(
                    phrase in stage2_r11_section,
                    f"{source_path}: {FAM006_STAGE2_R11_HEADING} is missing '{phrase}'",
                )
            for active_blocker in (
                "User Test Summary Returned With Blocking Findings",
                "User Test Summary Results FAIL",
                "Core Visualization Opaque Foreground Regression",
                "Monitoring HUD Product Architecture Mismatch",
                "HUD Dashboard / Minimal HUD Separation Missing",
                "Live Validation Proof Gap",
            ):
                require(
                    active_blocker in blockers,
                    (
                        f"{source_path}: Stage 2-R11 repair must keep "
                        f"'{active_blocker}' active until repair and revalidation"
                    ),
                )
            require(
                "Repair Revalidation Status: Pending - Stage 1-R8 required after Stage 2-R11"
                in plan_section,
                (
                    f"{source_path}: Stage 2-R11 Product Definition Plan must route "
                    "repair truth to Stage 1-R8 revalidation"
                ),
            )
            require(
                "Branch Readiness Stage 1-R8 - FAM-006 HUD Dashboard And Minimal HUD Source-Truth Revalidation"
                in text,
                (
                    f"{source_path}: Stage 2-R11 repair must set next legal seam "
                    "to Stage 1-R8 revalidation"
                ),
            )
            return
        if stage2_r9_section:
            for phrase in FAM006_STAGE2_R9_REQUIRED_PHRASES:
                require(
                    phrase in stage2_r9_section,
                    f"{source_path}: {FAM006_STAGE2_R9_HEADING} is missing '{phrase}'",
                )
            for cleared_blocker in (
                LEGACY_PRODUCT_NAME_DRIFT_BLOCKER,
                USER_VISION_INPUT_PENDING_BLOCKER,
                USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER,
                USER_VISION_INPUT_DIGEST_PENDING_BLOCKER,
            ):
                require(
                    cleared_blocker not in blockers,
                    (
                        f"{source_path}: Stage 2-R9 digest must clear "
                        f"'{cleared_blocker}' from active blockers"
                    ),
                )
            for active_blocker in (
                PRODUCT_PLANNING_INCOMPLETE_BLOCKER,
                "Branch Reach Unproven",
                "Current Branch vs Future Package Boundary Missing",
                HARDWARE_TELEMETRY_PROVIDER_PENDING_BLOCKER,
                EXTERNAL_TELEMETRY_PRIVACY_MODEL_MISSING_BLOCKER,
                PERSONA_SWITCH_SCOPE_BOUNDARY_PENDING_BLOCKER,
            ):
                require(
                    active_blocker in blockers,
                    (
                        f"{source_path}: Stage 2-R9 digest must keep "
                        f"'{active_blocker}' active until Stage 1 revalidates"
                    ),
                )
            for deferred_blocker in (
                POLLING_FLOOR_UNDECIDED_BLOCKER,
                WARNING_DELIVERY_MODALITY_PENDING_BLOCKER,
                AUDIO_WARNING_CROSS_FAMILY_APPROVAL_MISSING_BLOCKER,
            ):
                require(
                    deferred_blocker not in blockers,
                    (
                        f"{source_path}: Stage 2-R9 must not leave "
                        f"'{deferred_blocker}' active after current-branch posture "
                        "is recorded or deferred"
                    ),
                )
            require(
                "Planning Blockers: `Branch Readiness Planning Incomplete`;" in plan_section,
                (
                    f"{source_path}: Stage 2-R9 Product Definition Plan must list "
                    "Branch Readiness Planning Incomplete first in active planning blockers"
                ),
            )
            require(
                "`Persona Switch Scope Boundary Pending`" in plan_section,
                (
                    f"{source_path}: Stage 2-R9 Product Definition Plan must keep "
                    "persona/model switching scope as an active boundary blocker"
                ),
            )
            require(
                "Planning Revalidation Status: Pending - Stage 1-R6 required after Stage 2-R9 digest and scope rebaseline"
                in plan_section,
                (
                    f"{source_path}: Stage 2-R9 Product Definition Plan must route "
                    "to Stage 1-R6 revalidation"
                ),
            )
            return
        if has_stage2_r8_blocker:
            require(
                bool(stage2_r8_section),
                f"{source_path}: FAM-006 Branch Readiness re-entry is missing '## {FAM006_STAGE2_R8_HEADING}'",
            )
            for phrase in FAM006_STAGE2_R8_REQUIRED_PHRASES:
                require(
                    phrase in stage2_r8_section,
                    f"{source_path}: {FAM006_STAGE2_R8_HEADING} is missing '{phrase}'",
                )
            for blocker in (
                LEGACY_PRODUCT_NAME_DRIFT_BLOCKER,
                USER_VISION_INPUT_PENDING_BLOCKER,
                USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER,
                USER_VISION_INPUT_DIGEST_PENDING_BLOCKER,
                PRODUCT_PLANNING_INCOMPLETE_BLOCKER,
            ):
                require(
                    blocker in blockers,
                    f"{source_path}: Stage 2-R8 Branch Readiness re-entry must keep '{blocker}' active",
                )
            require(
                "Planning Blockers: `Legacy Product Name Drift`;" in plan_section,
                (
                    f"{source_path}: Stage 2-R8 Product Definition Plan must list "
                    "Legacy Product Name Drift as an active planning blocker"
                ),
            )
            return
        require(
            "Planning Blockers: `Branch Readiness Planning Incomplete`." in plan_section,
            (
                f"{source_path}: Stage 2-R6 repair must leave only "
                "`Branch Readiness Planning Incomplete` as the active planning blocker "
                "until Stage 1 revalidation"
            ),
        )
        require(
            PRODUCT_PLANNING_INCOMPLETE_BLOCKER in blockers,
            (
                f"{source_path}: Stage 2-R6 Branch Readiness must keep "
                f"'{PRODUCT_PLANNING_INCOMPLETE_BLOCKER}' active until Stage 1 revalidates"
            ),
        )
    elif current_phase == "Workstream":
        for forbidden_phrase in FAM006_FORBIDDEN_WORKSTREAM_UTS_PHRASES:
            require(
                forbidden_phrase not in text,
                (
                    f"{source_path}: FAM-006 Workstream must not preserve stale UTS-as-Workstream "
                    f"completion wording '{forbidden_phrase}'"
                ),
            )
        for required_phrase in FAM006_WORKSTREAM_CONTINUATION_REQUIRED_PHRASES:
            require(
                required_phrase in text,
                (
                    f"{source_path}: FAM-006 Workstream continuation truth is missing "
                    f"'{required_phrase}'"
                ),
            )
        ws51_section = _section(text, FAM006_WS51_HEADING)
        if ws51_section:
            for phrase in FAM006_WS51_REQUIRED_PHRASES:
                require(
                    phrase in ws51_section,
                    f"{source_path}: {FAM006_WS51_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS51_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS51 Green / Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS52 Green / Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS53 Green / Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS54 Green / Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS55 Green / Await USER Hardening Admission`"
                    in text
                ),
                f"{source_path}: WS51 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS51_NEXT_SEAM}`" in text,
                f"{source_path}: WS51 completion must set next legal seam to Hardening H1",
            )
            require(
                "H1 rerun and refreshed LV1 remain required" in text
                or "H1 rerun required" in text,
                f"{source_path}: WS51 completion must mark prior H1/LV1 stale for affected resize/scrollbar/state rows",
            )
        ws56_section = _section(text, FAM006_WS56_HEADING)
        if ws56_section:
            for phrase in FAM006_WS56_REQUIRED_PHRASES:
                require(
                    phrase in ws56_section,
                    f"{source_path}: {FAM006_WS56_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS56_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS56 Green / Await USER Hardening Admission`"
                    in text
                ),
                f"{source_path}: WS56 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS56_NEXT_SEAM}`" in text,
                f"{source_path}: WS56 completion must set next legal seam to Hardening H1",
            )
            require(
                "H1 rerun required" in text
                and "RUI-055" in text
                and "RUI-056" in text,
                f"{source_path}: WS56 completion must mark prior H1/LV1 stale for RUI-055/RUI-056 resize rows",
            )
            require(
                "Hardening H1 requires explicit USER admission" in text,
                f"{source_path}: WS56 completion must preserve explicit USER Hardening admission requirement",
            )
            return
        ws55_section = _section(text, FAM006_WS55_HEADING)
        if ws55_section:
            for phrase in FAM006_WS55_REQUIRED_PHRASES:
                require(
                    phrase in ws55_section,
                    f"{source_path}: {FAM006_WS55_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS55_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS55 Green / Await USER Hardening Admission`"
                    in text
                ),
                f"{source_path}: WS55 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS55_NEXT_SEAM}`" in text,
                f"{source_path}: WS55 completion must set next legal seam to Hardening H1",
            )
            require(
                "H1 rerun required" in text
                and "RUI-054" in text,
                f"{source_path}: WS55 completion must mark prior H1/LV1 stale for RUI-054 resize action rows",
            )
            require(
                "Hardening H1 requires explicit USER admission" in text,
                f"{source_path}: WS55 completion must preserve explicit USER Hardening admission requirement",
            )
            return
        ws54_section = _section(text, FAM006_WS54_HEADING)
        if ws54_section:
            for phrase in FAM006_WS54_REQUIRED_PHRASES:
                require(
                    phrase in ws54_section,
                    f"{source_path}: {FAM006_WS54_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS54_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS54 Green / Await USER Hardening Admission`"
                    in text
                ),
                f"{source_path}: WS54 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS54_NEXT_SEAM}`" in text,
                f"{source_path}: WS54 completion must set next legal seam to Hardening H1",
            )
            require(
                "H1 rerun required" in text
                and "RUI-053" in text,
                f"{source_path}: WS54 completion must mark prior H1/LV1 stale for RUI-053 cursor alignment rows",
            )
            require(
                "Hardening H1 requires explicit USER admission" in text,
                f"{source_path}: WS54 completion must preserve explicit USER Hardening admission requirement",
            )
            return
        ws53_section = _section(text, FAM006_WS53_HEADING)
        if ws53_section:
            for phrase in FAM006_WS53_REQUIRED_PHRASES:
                require(
                    phrase in ws53_section,
                    f"{source_path}: {FAM006_WS53_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS53_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS53 Green / Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS54 Green / Await USER Hardening Admission`"
                    in text
                ),
                f"{source_path}: WS53 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS53_NEXT_SEAM}`" in text,
                f"{source_path}: WS53 completion must set next legal seam to Hardening H1",
            )
            require(
                "H1 rerun required" in text,
                f"{source_path}: WS53 completion must mark prior H1/LV1 stale for affected resize discoverability rows",
            )
            require(
                "Hardening H1 requires explicit USER admission" in text,
                f"{source_path}: WS53 completion must preserve explicit USER Hardening admission requirement",
            )
            return
        ws52_section = _section(text, FAM006_WS52_HEADING)
        if ws52_section:
            for phrase in FAM006_WS52_REQUIRED_PHRASES:
                require(
                    phrase in ws52_section,
                    f"{source_path}: {FAM006_WS52_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS52_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS52 Green / Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS53 Green / Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Await USER Hardening Admission`"
                    in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS54 Green / Await USER Hardening Admission`"
                    in text
                ),
                f"{source_path}: WS52 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS52_NEXT_SEAM}`" in text,
                f"{source_path}: WS52 completion must set next legal seam to Hardening H1",
            )
            require(
                "H1 rerun required" in text,
                f"{source_path}: WS52 completion must mark prior H1/LV1 stale for affected resize rows",
            )
            require(
                "Hardening H1 requires explicit USER admission" in text,
                f"{source_path}: WS51 completion must preserve explicit USER Hardening admission requirement",
            )
            return
        ws50_section = _section(text, FAM006_WS50_HEADING)
        if ws50_section:
            for phrase in FAM006_WS50_REQUIRED_PHRASES:
                require(
                    phrase in ws50_section,
                    f"{source_path}: {FAM006_WS50_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS50_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS50 Green / Await USER Hardening Admission`"
                    in text
                ),
                f"{source_path}: WS50 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS50_NEXT_SEAM}`" in text,
                f"{source_path}: WS50 completion must set next legal seam to Hardening H1",
            )
            require(
                "H1/LV1 are stale for affected visual-shell rows" in text
                or "H1 rerun and refreshed LV1 are required" in text,
                f"{source_path}: WS50 completion must mark prior H1/LV1 stale for affected visual-shell rows",
            )
            require(
                "Hardening H1 requires explicit USER admission" in text,
                f"{source_path}: WS50 completion must preserve explicit USER Hardening admission requirement",
            )
            return
        ws49_section = _section(text, FAM006_WS49_HEADING)
        if ws49_section:
            for phrase in FAM006_WS49_REQUIRED_PHRASES:
                require(
                    phrase in ws49_section,
                    f"{source_path}: {FAM006_WS49_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS49_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Workstream WS49 Green / Await USER Hardening Admission`"
                    in text
                ),
                f"{source_path}: WS49 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS49_NEXT_SEAM}`" in text,
                f"{source_path}: WS49 completion must set next legal seam to Hardening H1",
            )
            require(
                "FAM006-RUI-047" in text,
                f"{source_path}: WS49 completion must register returned USER issue rows through FAM006-RUI-047",
            )
            require(
                "FAM006-TRAY-AUTHORING-DIALOG-GUARD-069" in text,
                f"{source_path}: WS49 completion must record the tray authoring dialog guard ledger row",
            )
            require(
                "Hardening H1 requires explicit USER admission" in text,
                f"{source_path}: WS49 completion must preserve explicit USER Hardening admission requirement",
            )
            return

        ws48_section = _section(text, FAM006_WS48_HEADING)
        if ws48_section:
            for phrase in FAM006_WS48_REQUIRED_PHRASES:
                require(
                    phrase in ws48_section,
                    f"{source_path}: {FAM006_WS48_HEADING} is missing '{phrase}'",
                )
            require(
                f"Next Legal Seam: `{FAM006_WS48_NEXT_SEAM}`" in text,
                f"{source_path}: LV1 denial must set next legal seam to WS48",
            )
            require(
                "Returned LV1 Handoff Denied" in text,
                f"{source_path}: LV1 denial must keep Returned LV1 Handoff Denied guard active",
            )
            require(
                "Human-Client Validation Manifest Required Before LV1 Handoff" in text,
                f"{source_path}: LV1 denial must require human-client validation before next UTS handoff",
            )
            return

        ws47_section = _section(text, FAM006_WS47_HEADING)
        if ws47_section:
            for phrase in FAM006_WS47_REQUIRED_PHRASES:
                require(
                    phrase in ws47_section,
                    f"{source_path}: {FAM006_WS47_HEADING} is missing '{phrase}'",
                )
            require(
                (
                    f"Active seam: `{FAM006_WS47_NEXT_SEAM}`" in text
                    or "Active seam: `Phase Boundary Stop - Hardening H1 Handoff Ready`" in text
                ),
                f"{source_path}: WS47 completion must advance active seam or phase-boundary stop to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS47_NEXT_SEAM}`" in text,
                f"{source_path}: WS47 completion must set next legal seam to Hardening H1",
            )
            require(
                f"Next Active Seam: {FAM006_WS47_NEXT_SEAM}" in text,
                f"{source_path}: WS47 completion must set Seam Continuation Decision next active seam to Hardening H1",
            )
            require(
                "Completion Status: Green" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS47 completion must mark Workstream completion green",
            )
            require(
                "Continue Decision: Stop" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS47 completion must stop at the Workstream-to-Hardening phase boundary",
            )
            require(
                "Hardening H1 requires explicit USER admission" in text,
                f"{source_path}: WS47 completion must preserve explicit USER Hardening admission requirement",
            )
            require(
                "WS47 does not generate, refresh, or digest" in text,
                f"{source_path}: WS47 completion must prove no formal UTS export occurred in Workstream",
            )
            return

        ws46_section = _section(text, FAM006_WS46_HEADING)
        if ws46_section:
            for phrase in FAM006_WS46_REQUIRED_PHRASES:
                require(
                    phrase in ws46_section,
                    f"{source_path}: {FAM006_WS46_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS46_NEXT_SEAM}`" in text,
                f"{source_path}: WS46 completion must advance active seam to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS46_NEXT_SEAM}`" in text,
                f"{source_path}: WS46 completion must set next legal seam to Hardening H1",
            )
            require(
                f"Next Active Seam: {FAM006_WS46_NEXT_SEAM}" in text,
                f"{source_path}: WS46 completion must set Seam Continuation Decision next active seam to Hardening H1",
            )
            require(
                "Completion Status: Green" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS46 completion must mark Workstream completion green",
            )
            require(
                "Continue Decision: Stop" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS46 completion must stop at the Workstream-to-Hardening phase boundary",
            )
            require(
                "Hardening phase-boundary stop requires explicit USER admission" in text,
                f"{source_path}: WS46 completion must preserve explicit USER Hardening admission requirement",
            )
            require(
                "dashboardUserTestSummaryExportRefreshed=false" in text,
                f"{source_path}: WS46 completion must prove no formal UTS export occurred in Workstream",
            )
            return
        ws45_section = _section(text, FAM006_WS45_HEADING)
        if ws45_section:
            for phrase in FAM006_WS45_REQUIRED_PHRASES:
                require(
                    phrase in ws45_section,
                    f"{source_path}: {FAM006_WS45_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS45_NEXT_SEAM}`" in text,
                f"{source_path}: WS45 completion must advance active seam to WS46",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS45_NEXT_SEAM}`" in text,
                f"{source_path}: WS45 completion must set next legal seam to WS46",
            )
            require(
                f"Next Active Seam: {FAM006_WS45_NEXT_SEAM}" in text,
                f"{source_path}: WS45 completion must set Seam Continuation Decision next active seam to WS46",
            )
            require(
                "Continue Decision: Continue" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS45 completion must continue within bounded Workstream",
            )
            require(
                "Stop Basis: None" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS45 completion must not create a stop basis before WS46",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS46"
                in text,
                (
                    f"{source_path}: WS45 completion must preserve visible same-branch "
                    "Dashboard proof-readiness work beyond the current seam"
                ),
            )
            return
        ws44_section = _section(text, FAM006_WS44_HEADING)
        if ws44_section:
            for phrase in FAM006_WS44_REQUIRED_PHRASES:
                require(
                    phrase in ws44_section,
                    f"{source_path}: {FAM006_WS44_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS44_NEXT_SEAM}`" in text,
                f"{source_path}: WS44 completion must advance active seam to WS45",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS44_NEXT_SEAM}`" in text,
                f"{source_path}: WS44 completion must set next legal seam to WS45",
            )
            require(
                f"Next Active Seam: {FAM006_WS44_NEXT_SEAM}" in text,
                f"{source_path}: WS44 completion must set Seam Continuation Decision next active seam to WS45",
            )
            require(
                "Continue Decision: Continue" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS44 completion must continue within bounded Workstream",
            )
            require(
                "Stop Basis: None" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS44 completion must not create a stop basis before WS45",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS45"
                in text,
                (
                    f"{source_path}: WS44 completion must preserve visible same-branch "
                    "Dashboard IA/naming/action cleanup work beyond the current seam"
                ),
            )
            return
        ws43_section = _section(text, FAM006_WS43_HEADING)
        if ws43_section:
            for phrase in FAM006_WS43_REQUIRED_PHRASES:
                require(
                    phrase in ws43_section,
                    f"{source_path}: {FAM006_WS43_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS43_NEXT_SEAM}`" in text,
                f"{source_path}: WS43 completion must advance active seam to WS44",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS43_NEXT_SEAM}`" in text,
                f"{source_path}: WS43 completion must set next legal seam to WS44",
            )
            require(
                f"Next Active Seam: {FAM006_WS43_NEXT_SEAM}" in text,
                f"{source_path}: WS43 completion must set Seam Continuation Decision next active seam to WS44",
            )
            require(
                "Continue Decision: Continue" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS43 completion must continue within bounded Workstream",
            )
            require(
                "Stop Basis: None" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS43 completion must not create a stop basis before WS44",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS44"
                in text,
                (
                    f"{source_path}: WS43 completion must preserve visible same-branch "
                    "Dashboard visual-shell repair work beyond the current seam"
                ),
            )
            return
        ws42_section = _section(text, FAM006_WS42_HEADING)
        if ws42_section:
            for phrase in FAM006_WS42_REQUIRED_PHRASES:
                require(
                    phrase in ws42_section,
                    f"{source_path}: {FAM006_WS42_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS42_NEXT_SEAM}`" in text,
                f"{source_path}: WS42 completion must advance active seam to Hardening H1",
            )
            require(
                f"Next Legal Seam: `{FAM006_WS42_NEXT_SEAM}`" in text,
                f"{source_path}: WS42 completion must set next legal seam to Hardening H1",
            )
            require(
                f"Next Active Seam: {FAM006_WS42_NEXT_SEAM}" in text,
                f"{source_path}: WS42 completion must set Seam Continuation Decision next active seam to Hardening H1",
            )
            require(
                "Remaining Implementable Work: `None inside current Workstream - WS37 through WS42 are green or legally deferred"
                in text,
                (
                    f"{source_path}: WS42 completion must close current same-phase "
                    "Workstream implementation/proof work before Hardening handoff"
                ),
            )
            require(
                "Continue Decision: Stop" in _section(text, "Seam Continuation Decision"),
                f"{source_path}: WS42 completion must stop at the Hardening phase boundary",
            )
            require(
                "Continuation Execution Latch: Inactive - WS42 is Green; phase-boundary stop is required before USER may admit Hardening H1."
                in text,
                f"{source_path}: WS42 completion must keep the Hardening phase-boundary latch inactive",
            )
            require(
                "dashboardUserTestSummaryExportRefreshed=false" in text,
                f"{source_path}: WS42 completion must prove no formal UTS export was generated in Workstream",
            )
            return
        ws41_section = _section(text, FAM006_WS41_HEADING)
        if ws41_section:
            for phrase in FAM006_WS41_REQUIRED_PHRASES:
                require(
                    phrase in ws41_section,
                    f"{source_path}: {FAM006_WS41_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS41_NEXT_SEAM}`" in text,
                f"{source_path}: WS41 deferral must advance active seam to WS42 proof readiness",
            )
            require(
                f"Next Active Seam: {FAM006_WS41_NEXT_SEAM}" in text,
                f"{source_path}: WS41 deferral must set Seam Continuation Decision next active seam to WS42",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS42"
                in text,
                (
                    f"{source_path}: WS41 deferral must preserve visible same-branch "
                    "Dashboard proof work beyond the current seam"
                ),
            )
            require(
                "WS41 Child-Window Scope User Admission Missing" not in _section(text, "Blockers"),
                (
                    f"{source_path}: WS41 deferral must clear the former admission blocker "
                    "from active Blockers"
                ),
            )
            return
        ws40_section = _section(text, FAM006_WS40_HEADING)
        if ws40_section:
            for phrase in FAM006_WS40_REQUIRED_PHRASES:
                require(
                    phrase in ws40_section,
                    f"{source_path}: {FAM006_WS40_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS40_NEXT_SEAM}`" in text,
                f"{source_path}: WS40 completion must advance active seam to WS41 scope seam",
            )
            require(
                f"Next Active Seam: {FAM006_WS40_NEXT_SEAM}" in text,
                f"{source_path}: WS40 completion must set Seam Continuation Decision next active seam to WS41",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS41"
                in text,
                (
                    f"{source_path}: WS40 completion must preserve visible same-branch "
                    "Dashboard repair/proof work beyond the current seam"
                ),
            )
            return
        ws39_section = _section(text, FAM006_WS39_HEADING)
        if ws39_section:
            for phrase in FAM006_WS39_REQUIRED_PHRASES:
                require(
                    phrase in ws39_section,
                    f"{source_path}: {FAM006_WS39_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS39_NEXT_SEAM}`" in text,
                f"{source_path}: WS39 completion must advance active seam to WS40",
            )
            require(
                f"Next Active Seam: {FAM006_WS39_NEXT_SEAM}" in text,
                f"{source_path}: WS39 completion must set Seam Continuation Decision next active seam to WS40",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS40"
                in text,
                (
                    f"{source_path}: WS39 completion must preserve visible same-branch "
                    "Dashboard repair work beyond the current seam"
                ),
            )
            return
        ws38_section = _section(text, FAM006_WS38_HEADING)
        if ws38_section:
            for phrase in FAM006_WS38_REQUIRED_PHRASES:
                require(
                    phrase in ws38_section,
                    f"{source_path}: {FAM006_WS38_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS38_NEXT_SEAM}`" in text,
                f"{source_path}: WS38 completion must advance active seam to WS39",
            )
            require(
                f"Next Active Seam: {FAM006_WS38_NEXT_SEAM}" in text,
                f"{source_path}: WS38 completion must set Seam Continuation Decision next active seam to WS39",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS39"
                in text,
                (
                    f"{source_path}: WS38 completion must preserve visible same-branch "
                    "Dashboard repair work beyond the current seam"
                ),
            )
            return
        ws37_section = _section(text, FAM006_WS37_HEADING)
        if ws37_section:
            for phrase in FAM006_WS37_REQUIRED_PHRASES:
                require(
                    phrase in ws37_section,
                    f"{source_path}: {FAM006_WS37_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS37_NEXT_SEAM}`" in text,
                f"{source_path}: WS37 completion must advance active seam to WS38",
            )
            require(
                f"Next Active Seam: {FAM006_WS37_NEXT_SEAM}" in text,
                f"{source_path}: WS37 completion must set Seam Continuation Decision next active seam to WS38",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS38"
                in text,
                (
                    f"{source_path}: WS37 completion must preserve visible same-branch "
                    "Dashboard repair work beyond the current seam"
                ),
            )
            require(
                "Dashboard Acceptance State: `Still blocked"
                in ws37_section,
                (
                    f"{source_path}: WS37 must not claim Dashboard acceptance or package completion"
                ),
            )
            return
        ws36_section = _section(text, FAM006_WS36_HEADING)
        if ws36_section:
            for phrase in FAM006_WS36_REQUIRED_PHRASES:
                require(
                    phrase in ws36_section,
                    f"{source_path}: {FAM006_WS36_HEADING} is missing '{phrase}'",
                )
            require(
                "Active seam: `Phase Boundary Stop - Await USER Hardening Admission`" in text,
                (
                    f"{source_path}: WS36 completion must stop at the phase boundary and await "
                    "explicit USER Hardening admission"
                ),
            )
            require(
                f"Next Active Seam: {FAM006_WS36_NEXT_SEAM}" in text,
                f"{source_path}: WS36 completion must set Seam Continuation Decision next active seam to Hardening H1",
            )
            require(
                "Remaining Implementable Work: `None - Dashboard-focused Workstream repair is green"
                in text,
                (
                    f"{source_path}: WS36 completion must close current Dashboard-focused "
                    "Workstream implementable work before Hardening handoff"
                ),
            )
            require(
                "Completion Status: Green" in text,
                f"{source_path}: WS36 completion must record Workstream Completion Status Green",
            )
            return
        ws35_section = _section(text, FAM006_WS35_HEADING)
        if ws35_section:
            for phrase in FAM006_WS35_REQUIRED_PHRASES:
                require(
                    phrase in ws35_section,
                    f"{source_path}: {FAM006_WS35_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS35_NEXT_SEAM}`" in text,
                f"{source_path}: WS35 completion must advance active seam to WS36",
            )
            require(
                f"Next Active Seam: {FAM006_WS35_NEXT_SEAM}" in text,
                f"{source_path}: WS35 completion must set Seam Continuation Decision next active seam to WS36",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS36"
                in text,
                (
                    f"{source_path}: WS35 completion must preserve visible same-branch "
                    "Workstream completion review work beyond the current seam"
                ),
            )
            require(
                "Dashboard Acceptance Pending remains active"
                in ws35_section,
                (
                    f"{source_path}: WS35 must not claim returned UTS acceptance or package completion"
                ),
            )
            return
        ws34_section = _section(text, FAM006_WS34_HEADING)
        if ws34_section:
            for phrase in FAM006_WS34_REQUIRED_PHRASES:
                require(
                    phrase in ws34_section,
                    f"{source_path}: {FAM006_WS34_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS34_NEXT_SEAM}`" in text,
                f"{source_path}: WS34 completion must advance active seam to WS35",
            )
            require(
                f"Next Active Seam: {FAM006_WS34_NEXT_SEAM}" in text,
                f"{source_path}: WS34 completion must set Seam Continuation Decision next active seam to WS35",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS35"
                in text,
                (
                    f"{source_path}: WS34 completion must preserve visible same-branch "
                    "Dashboard proof work beyond the current seam"
                ),
            )
            require(
                "Dashboard Acceptance Pending remains active"
                in ws34_section,
                (
                    f"{source_path}: WS34 must not claim Dashboard acceptance or package completion"
                ),
            )
            return
        if ws33_section:
            for phrase in FAM006_WS33_REQUIRED_PHRASES:
                require(
                    phrase in ws33_section,
                    f"{source_path}: {FAM006_WS33_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS33_NEXT_SEAM}`" in text,
                f"{source_path}: WS33 completion must advance active seam to WS34",
            )
            require(
                f"Next Active Seam: {FAM006_WS33_NEXT_SEAM}" in text,
                f"{source_path}: WS33 completion must set Seam Continuation Decision next active seam to WS34",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS34"
                in text,
                (
                    f"{source_path}: WS33 completion must preserve visible same-branch "
                    "Dashboard repair work beyond the current seam"
                ),
            )
            require(
                "Dashboard Acceptance Pending remains active"
                in ws33_section,
                (
                    f"{source_path}: WS33 must not claim Dashboard acceptance or package completion"
                ),
            )
            return
        if ws32_section:
            for phrase in FAM006_WS32_REQUIRED_PHRASES:
                require(
                    phrase in ws32_section,
                    f"{source_path}: {FAM006_WS32_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS32_NEXT_SEAM}`" in text,
                f"{source_path}: WS32 completion must advance active seam to WS33",
            )
            require(
                f"Next Active Seam: {FAM006_WS32_NEXT_SEAM}" in text,
                f"{source_path}: WS32 completion must set Seam Continuation Decision next active seam to WS33",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS33"
                in text,
                (
                    f"{source_path}: WS32 completion must preserve visible same-branch "
                    "Dashboard repair work beyond the current seam"
                ),
            )
            require(
                "Dashboard Acceptance Pending remains active"
                in ws32_section,
                (
                    f"{source_path}: WS32 must not claim Dashboard acceptance or package completion"
                ),
            )
            return
        if ws31_section:
            for phrase in FAM006_WS31_REQUIRED_PHRASES:
                require(
                    phrase in ws31_section,
                    f"{source_path}: {FAM006_WS31_HEADING} is missing '{phrase}'",
                )
            require(
                f"Active seam: `{FAM006_WS31_NEXT_SEAM}`" in text,
                f"{source_path}: WS31 completion must advance active seam to WS32",
            )
            require(
                f"Next Active Seam: {FAM006_WS31_NEXT_SEAM}" in text,
                f"{source_path}: WS31 completion must set Seam Continuation Decision next active seam to WS32",
            )
            require(
                "Remaining Implementable Work: `Dashboard-focused Workstream repair continues with WS32"
                in text,
                (
                    f"{source_path}: WS31 completion must preserve visible same-branch "
                    "Dashboard repair work beyond the current seam"
                ),
            )
            require(
                "Dashboard Acceptance Pending remains active"
                in ws31_section,
                (
                    f"{source_path}: WS31 must not claim Dashboard acceptance or package completion"
                ),
            )
            return
        if stage2_r13_section:
            for phrase in FAM006_STAGE2_R13_REQUIRED_PHRASES:
                require(
                    phrase in stage2_r13_section,
                    f"{source_path}: {FAM006_STAGE2_R13_HEADING} is missing '{phrase}'",
                )
            for cleared_blocker in (
                "Branch Readiness Interface Planning Incomplete",
                "Interface Acceptance Missing",
            ):
                require(
                    cleared_blocker not in blockers,
                    (
                        f"{source_path}: Stage 2-R13 handoff must clear "
                        f"'{cleared_blocker}' from active blockers"
                    ),
                )
            require(
                "Active seam: `Workstream WS31 - Dashboard Control Panel Acceptance Baseline And Overlay Deferral Enforcement`"
                in text,
                f"{source_path}: Stage 2-R13 handoff must set active seam to WS31",
            )
            require(
                "Planning Blockers: None active after Stage 2-R13 Dashboard-first revalidation closeout."
                in plan_section,
                (
                    f"{source_path}: Stage 2-R13 Workstream handoff must clear "
                    "active Branch Readiness planning blockers in the Product Definition Plan"
                ),
            )
            require(
                "Dashboard Acceptance Pending remains a Workstream acceptance gap"
                in plan_section,
                (
                    f"{source_path}: Stage 2-R13 must preserve Dashboard Acceptance Pending "
                    "as Workstream product proof, not a planning blocker"
                ),
            )
            return
        if stage2_r10_section:
            for phrase in FAM006_STAGE2_R10_REQUIRED_PHRASES:
                require(
                    phrase in stage2_r10_section,
                    f"{source_path}: {FAM006_STAGE2_R10_HEADING} is missing '{phrase}'",
                )
            for cleared_blocker in (
                PRODUCT_PLANNING_INCOMPLETE_BLOCKER,
                "Branch Reach Unproven",
                "Current Branch vs Future Package Boundary Missing",
                HARDWARE_TELEMETRY_PROVIDER_PENDING_BLOCKER,
                EXTERNAL_TELEMETRY_PRIVACY_MODEL_MISSING_BLOCKER,
                PERSONA_SWITCH_SCOPE_BOUNDARY_PENDING_BLOCKER,
            ):
                require(
                    cleared_blocker not in blockers,
                    (
                        f"{source_path}: Stage 2-R10 handoff must clear or defer "
                        f"'{cleared_blocker}' from active blockers"
                    ),
                )
            require(
                "Planning Blockers: None active after Stage 2-R10 scope rebaseline closeout."
                in plan_section,
                (
                    f"{source_path}: Stage 2-R10 Workstream handoff must clear "
                    "active planning blockers in the Product Definition Plan"
                ),
            )
            require(
                PRODUCT_PLANNING_INCOMPLETE_BLOCKER not in blockers,
                (
                    f"{source_path}: Workstream handoff must not keep "
                    f"'{PRODUCT_PLANNING_INCOMPLETE_BLOCKER}' under active Blockers"
                ),
            )
            return
        closeout_section = _section(text, FAM006_STAGE2_R7_HEADING)
        require(
            bool(closeout_section),
            f"{source_path}: FAM-006 Workstream handoff is missing '## {FAM006_STAGE2_R7_HEADING}'",
        )
        for phrase in FAM006_STAGE2_R7_REQUIRED_PHRASES:
            require(
                phrase in closeout_section,
                f"{source_path}: {FAM006_STAGE2_R7_HEADING} is missing '{phrase}'",
            )
        require(
            "Planning Blockers: None active after Stage 2-R7 planning revalidation closeout." in plan_section,
            (
                f"{source_path}: Workstream handoff must clear "
                "`Branch Readiness Planning Incomplete` in the Product Definition Plan"
            ),
        )
        require(
            PRODUCT_PLANNING_INCOMPLETE_BLOCKER not in blockers,
            (
                f"{source_path}: Workstream handoff must not keep "
                f"'{PRODUCT_PLANNING_INCOMPLETE_BLOCKER}' under active Blockers"
            ),
        )
    elif current_phase == "Hardening":
        if (
            "FAM-006 Active Overlay Recording Runtime Implementation" in text
            and "active-overlay recording runtime implementation carrier" in text
        ):
            h1_section = _section(text, FAM006_ACTIVE_OVERLAY_H1_HEADING)
            require(
                bool(h1_section),
                (
                    f"{source_path}: FAM-006 active-overlay Hardening state is missing "
                    f"'## {FAM006_ACTIVE_OVERLAY_H1_HEADING}'"
                ),
            )
            for phrase in FAM006_ACTIVE_OVERLAY_H1_REQUIRED_PHRASES:
                require(
                    phrase in h1_section,
                    f"{source_path}: {FAM006_ACTIVE_OVERLAY_H1_HEADING} is missing '{phrase}'",
                )
            require(
                "Active seam: `Phase Boundary Stop - Await USER Live Validation Admission`"
                in text,
                (
                    f"{source_path}: active-overlay H1 completion must stop at the "
                    "phase boundary and await explicit USER Live Validation admission"
                ),
            )
            require(
                f"Next Active Seam: {FAM006_ACTIVE_OVERLAY_H1_NEXT_SEAM}" in text,
                (
                    f"{source_path}: active-overlay H1 completion must set Seam "
                    "Continuation Decision next active seam to Live Validation LV1"
                ),
            )
            require(
                "Remaining Implementable Work: `None`"
                in text,
                (
                    f"{source_path}: active-overlay H1 completion must close current "
                    "Workstream and Hardening proof work before Live Validation handoff"
                ),
            )
            require(
                "Continuation Execution Latch: Inactive - Hardening H1 is Green; phase-boundary stop is required before USER may admit Live Validation LV1."
                in text,
                f"{source_path}: active-overlay H1 completion must keep the Live Validation phase-boundary latch inactive",
            )
            require(
                "Formal User Test Summary export is exclusive to Live Validation Stage 1"
                in text,
                f"{source_path}: active-overlay H1 completion must preserve the Live Validation Stage 1 UTS boundary",
            )
            require(
                _parse_uts_result_state(text) == "",
                (
                    f"{source_path}: Hardening may keep User Test Summary strategy current, "
                    f"but must not declare '{UTS_RESULT_LABEL}' before Live Validation"
                ),
            )
            require(
                UTS_RESULTS_BLOCKER not in blockers,
                (
                    f"{source_path}: {UTS_RESULTS_BLOCKER} is a Live Validation / PR Readiness "
                    "final-green blocker, not a Hardening stop condition"
                ),
            )
            return
        h1_section = _section(text, FAM006_H1_HEADING)
        require(
            bool(h1_section),
            f"{source_path}: FAM-006 Hardening state is missing '## {FAM006_H1_HEADING}'",
        )
        for phrase in FAM006_H1_REQUIRED_PHRASES:
            require(
                phrase in h1_section,
                f"{source_path}: {FAM006_H1_HEADING} is missing '{phrase}'",
            )
        require(
            "Active seam: `Phase Boundary Stop - Await USER Live Validation Admission`"
            in text,
            (
                f"{source_path}: H1 completion must stop at the phase boundary and await "
                "explicit USER Live Validation admission"
            ),
        )
        require(
            f"Next Active Seam: {FAM006_H1_NEXT_SEAM}" in text,
            f"{source_path}: H1 completion must set Seam Continuation Decision next active seam to Live Validation LV1",
        )
        require(
            "Remaining Implementable Work: `None - Dashboard-focused Workstream repair and Hardening H1 are green"
            in text,
            (
                f"{source_path}: H1 completion must close current Workstream and Hardening "
                "implementation/proof work before Live Validation handoff"
            ),
        )
        require(
            "Continuation Execution Latch: Inactive - Hardening H1 is Green; phase-boundary stop is required before USER may admit Live Validation LV1."
            in text,
            f"{source_path}: H1 completion must keep the Live Validation phase-boundary latch inactive",
        )
        require(
            "Formal User Test Summary export is exclusive to Live Validation Stage 1"
            in text,
            f"{source_path}: H1 completion must preserve the Live Validation Stage 1 UTS boundary",
        )
        require(
            _parse_uts_result_state(text) == "",
            (
                f"{source_path}: Hardening may keep User Test Summary strategy current, "
                f"but must not declare '{UTS_RESULT_LABEL}' before Live Validation"
            ),
        )
        require(
            UTS_RESULTS_BLOCKER not in blockers,
            (
                f"{source_path}: {UTS_RESULTS_BLOCKER} is a Live Validation / PR Readiness "
                "final-green blocker, not a Hardening stop condition"
            ),
        )


def _validate_user_vision_input_handoff(
    require,
    source_path: str,
    text: str,
    blockers: list[str],
) -> None:
    has_user_vision_input_blocker = any(
        blocker in blockers
        for blocker in (
            USER_VISION_INPUT_PENDING_BLOCKER,
            USER_VISION_INPUT_FILE_MISSING_BLOCKER,
            USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER,
            USER_VISION_INPUT_DIGEST_PENDING_BLOCKER,
        )
    )
    if not has_user_vision_input_blocker and f"## {USER_VISION_INPUT_HANDOFF_HEADING}" not in text:
        return

    handoff_section = _section(text, USER_VISION_INPUT_HANDOFF_HEADING)
    require(
        bool(handoff_section),
        (
            f"{source_path}: USER vision input blockers require "
            f"'## {USER_VISION_INPUT_HANDOFF_HEADING}'"
        ),
    )
    if not handoff_section:
        return

    for marker in USER_VISION_INPUT_HANDOFF_MARKERS:
        require(
            marker in handoff_section,
            f"{source_path}: {USER_VISION_INPUT_HANDOFF_HEADING} is missing '{marker}'",
        )

    artifact_path = _extract_marker_value(handoff_section, "USER Vision Input Artifact Path:")
    artifact_state = _extract_marker_value(handoff_section, "USER Vision Input Artifact State:")
    answer_state = _extract_marker_value(handoff_section, "USER Vision Input Answer State:")
    digest_state = _extract_marker_value(handoff_section, "USER Vision Input Digest State:")
    source_truth_rule = _extract_marker_value(handoff_section, "Repo Source Truth Update Rule:")
    normalized_answer_state = answer_state.casefold()
    normalized_digest_state = digest_state.casefold()
    artifact_exists = USER_VISION_INPUT_ARTIFACT_PATH.exists()

    require(
        str(USER_VISION_INPUT_ARTIFACT_PATH) in artifact_path,
        (
            f"{source_path}: USER vision input handoff must point to "
            f"{USER_VISION_INPUT_ARTIFACT_PATH}"
        ),
    )
    require(
        bool(artifact_state),
        f"{source_path}: USER vision input handoff is missing artifact state",
    )
    require(
        bool(answer_state),
        f"{source_path}: USER vision input handoff is missing answer state",
    )
    require(
        bool(digest_state),
        f"{source_path}: USER vision input handoff is missing digest state",
    )
    require(
        "recommendations" in source_truth_rule.casefold()
        and "not" in source_truth_rule.casefold()
        and "digest" in source_truth_rule.casefold(),
        (
            f"{source_path}: USER vision input handoff must state that Codex "
            "recommendations/unanswered prompts are not USER-approved repo truth "
            "until a later digest pass"
        ),
    )

    if (
        USER_VISION_INPUT_FILE_MISSING_BLOCKER in blockers
        or USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER in blockers
        or USER_VISION_INPUT_DIGEST_PENDING_BLOCKER in blockers
    ) and artifact_exists:
        require(
            USER_VISION_INPUT_FILE_MISSING_BLOCKER not in blockers,
            (
                f"{source_path}: {USER_VISION_INPUT_FILE_MISSING_BLOCKER} must not remain "
                f"active while {USER_VISION_INPUT_ARTIFACT_PATH} exists"
            ),
        )
    elif USER_VISION_INPUT_FILE_MISSING_BLOCKER in blockers:
        require(
            not artifact_exists,
            (
                f"{source_path}: {USER_VISION_INPUT_FILE_MISSING_BLOCKER} is active, "
                f"but {USER_VISION_INPUT_ARTIFACT_PATH} exists"
            ),
        )

    if "pending" in normalized_answer_state or "incomplete" in normalized_answer_state:
        require(
            USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER in blockers,
            (
                f"{source_path}: pending USER vision input answers must block on "
                f"'{USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER}'"
            ),
        )
    elif "complete" in normalized_answer_state or "completed" in normalized_answer_state:
        require(
            USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER not in blockers,
            (
                f"{source_path}: {USER_VISION_INPUT_ANSWERS_PENDING_BLOCKER} must clear "
                "after USER vision input answers are recorded complete"
            ),
        )

    if "pending" in normalized_digest_state or "not digested" in normalized_digest_state:
        require(
            USER_VISION_INPUT_DIGEST_PENDING_BLOCKER in blockers,
            (
                f"{source_path}: undigested USER vision input answers must block on "
                f"'{USER_VISION_INPUT_DIGEST_PENDING_BLOCKER}'"
            ),
        )
        require(
            USER_VISION_INPUT_PENDING_BLOCKER in blockers,
            (
                f"{source_path}: USER vision input cannot be considered complete until "
                f"'{USER_VISION_INPUT_PENDING_BLOCKER}' is cleared by a later digest pass"
            ),
        )
    elif "digest" in normalized_digest_state or "digested" in normalized_digest_state:
        require(
            USER_VISION_INPUT_DIGEST_PENDING_BLOCKER not in blockers,
            (
                f"{source_path}: {USER_VISION_INPUT_DIGEST_PENDING_BLOCKER} must clear "
                "after USER vision input is digested into repo source truth"
            ),
        )
        require(
            USER_VISION_INPUT_PENDING_BLOCKER not in blockers,
            (
                f"{source_path}: {USER_VISION_INPUT_PENDING_BLOCKER} must clear after "
                "USER vision input is digested into repo source truth"
            ),
        )


def _validate_backlog_completion_status(
    require,
    source_path: str,
    text: str,
    *,
    branch_class: str,
    current_phase: str,
    blockers: list[str],
    next_legal_phase: str,
) -> None:
    if branch_class != "implementation":
        return
    if current_phase not in BACKLOG_COMPLETION_ACTIVE_PHASES:
        return

    require(
        f"## {BACKLOG_COMPLETION_STATUS_HEADING}" in text,
        f"{source_path}: implementation lane is missing '## {BACKLOG_COMPLETION_STATUS_HEADING}'",
    )
    status_section = _section(text, BACKLOG_COMPLETION_STATUS_HEADING)
    state_value = _extract_marker_value(status_section, BACKLOG_COMPLETION_STATE_LABEL)
    completion_status_value = _extract_marker_value(
        status_section, CONTINUATION_COMPLETION_STATUS_LABEL
    )
    remaining_work = _extract_marker_value(status_section, REMAINING_IMPLEMENTABLE_WORK_LABEL)
    future_blockers = _extract_marker_value(status_section, FUTURE_DEPENDENT_BLOCKERS_LABEL)
    normalized_state = state_value.strip().casefold()
    normalized_completion_status = completion_status_value.strip().casefold()
    normalized_remaining = remaining_work.strip().casefold()
    normalized_future = future_blockers.strip().casefold()
    has_backlog_blocker = BACKLOG_COMPLETION_UNPROVEN_BLOCKER in blockers
    continuation_section = _section(text, "Seam Continuation Decision")
    continuation_waiver_status = _extract_marker_value(
        continuation_section, CONTINUATION_WAIVER_STATUS_LABEL
    ).strip().casefold()
    stop_authorizing_blockers = [
        blocker for blocker in blockers if blocker != BACKLOG_COMPLETION_UNPROVEN_BLOCKER
    ]

    require(
        bool(state_value),
        f"{source_path}: {BACKLOG_COMPLETION_STATUS_HEADING} is missing '{BACKLOG_COMPLETION_STATE_LABEL}:'",
    )
    require(
        bool(remaining_work),
        f"{source_path}: {BACKLOG_COMPLETION_STATUS_HEADING} is missing '{REMAINING_IMPLEMENTABLE_WORK_LABEL}:'",
    )
    require(
        bool(future_blockers),
        f"{source_path}: {BACKLOG_COMPLETION_STATUS_HEADING} is missing '{FUTURE_DEPENDENT_BLOCKERS_LABEL}:'",
    )
    if current_phase == "Workstream":
        require(
            bool(completion_status_value),
            (
                f"{source_path}: {BACKLOG_COMPLETION_STATUS_HEADING} is missing "
                f"'{CONTINUATION_COMPLETION_STATUS_LABEL}:'"
            ),
        )
        require(
            normalized_completion_status in CONTINUATION_ALLOWED_COMPLETION_STATUSES,
            (
                f"{source_path}: {CONTINUATION_COMPLETION_STATUS_LABEL} "
                f"'{completion_status_value}' must be one of "
                f"{', '.join(sorted(CONTINUATION_ALLOWED_COMPLETION_STATUSES))}"
            ),
        )
    require(
        normalized_state
        in {
            BACKLOG_COMPLETION_IN_PROGRESS,
            BACKLOG_COMPLETION_IMPLEMENTED_COMPLETE,
            BACKLOG_COMPLETION_IMPLEMENTED_COMPLETE_FUTURE,
        },
        (
            f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} '{state_value}' must be "
            "'In Progress', 'Implemented Complete', or 'Implemented Complete Except Future Dependency'"
        ),
    )

    if normalized_state == BACKLOG_COMPLETION_IN_PROGRESS:
        in_progress_phase_allows_latch = current_phase in {
            "Branch Readiness",
            "Workstream",
            "Hardening",
            "Live Validation",
            "PR Readiness",
        }
        require(
            in_progress_phase_allows_latch,
            (
                f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} In Progress must keep the branch "
                "inside an admitted pre-completion phase"
            ),
        )
        require(
            next_legal_phase == current_phase,
            (
                f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} In Progress must keep "
                "Next Legal Phase at the current phase until explicit phase admission "
                "or package completion proof clears the latch"
            ),
        )
        require(
            normalized_remaining not in {"", "none", "n/a", "na"},
            (
                f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} In Progress requires "
                f"'{REMAINING_IMPLEMENTABLE_WORK_LABEL}:' to name remaining same-branch work"
            ),
        )
        # Backlog completion remaining unproven is a progress latch, not by itself a lawful
        # Workstream stop condition. Active Workstream records may keep the latch in source
        # truth, but validators must not force it into the stop-authorizing Blockers list.
        if current_phase == "Workstream":
            if continuation_waiver_status != "none" or stop_authorizing_blockers:
                require(
                    normalized_completion_status == "red",
                    (
                        f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} In Progress with a "
                        "stop-authorizing blocker or waiver requires "
                        f"'{CONTINUATION_COMPLETION_STATUS_LABEL}: Red'"
                    ),
                )
            else:
                require(
                    normalized_completion_status == "in progress",
                    (
                        f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} In Progress without a "
                        "stop-authorizing blocker or waiver requires "
                        f"'{CONTINUATION_COMPLETION_STATUS_LABEL}: In Progress'"
                    ),
                )
    elif normalized_state == BACKLOG_COMPLETION_IMPLEMENTED_COMPLETE:
        visible_proof_required = _extract_marker_value(
            text, VISIBLE_USER_FACING_PROOF_REQUIRED_LABEL
        ).strip().casefold()
        visible_proof = _extract_marker_value(
            text, VISIBLE_USER_FACING_PROOF_LABEL
        ).strip().casefold()
        if visible_proof_required in {"yes", "required", "true"}:
            require(
                visible_proof in VISIBLE_USER_FACING_PROOF_PASS_VALUES,
                (
                    f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete "
                    f"requires '{VISIBLE_USER_FACING_PROOF_LABEL} PASS' or WAIVED when "
                    f"'{VISIBLE_USER_FACING_PROOF_REQUIRED_LABEL} Yes' is recorded"
                ),
            )
            require(
                _parse_uts_result_state(text) not in {"", "PENDING", "FAIL"},
                (
                    f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete "
                    "requires returned User Test Summary results or a documented waiver when "
                    "visible user-facing proof is required"
                ),
            )
        require(
            normalized_remaining in {"", "none", "n/a", "na"},
            (
                f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete requires "
                f"'{REMAINING_IMPLEMENTABLE_WORK_LABEL}: None'"
            ),
        )
        require(
            normalized_future in {"", "none", "n/a", "na"},
            (
                f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete requires "
                f"'{FUTURE_DEPENDENT_BLOCKERS_LABEL}: None'"
            ),
        )
        require(
            not has_backlog_blocker,
            (
                f"{source_path}: blocker '{BACKLOG_COMPLETION_UNPROVEN_BLOCKER}' must clear once "
                "backlog completion is proven"
            ),
        )
        if current_phase == "Workstream":
            require(
                normalized_completion_status == "green",
                (
                    f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete requires "
                    f"'{CONTINUATION_COMPLETION_STATUS_LABEL}: Green' before Workstream can exit"
                ),
            )
            require(
                next_legal_phase == "Hardening",
                (
                    f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete in "
                    "Workstream must advance Next Legal Phase to `Hardening`"
                ),
            )
    elif normalized_state == BACKLOG_COMPLETION_IMPLEMENTED_COMPLETE_FUTURE:
        require(
            normalized_remaining in {"", "none", "n/a", "na"},
            (
                f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete Except Future "
                f"Dependency requires '{REMAINING_IMPLEMENTABLE_WORK_LABEL}: None'"
            ),
        )
        require(
            normalized_future not in {"", "none", "n/a", "na"},
            (
                f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete Except Future "
                f"Dependency requires named '{FUTURE_DEPENDENT_BLOCKERS_LABEL}:'"
            ),
        )
        require(
            not has_backlog_blocker,
            (
                f"{source_path}: blocker '{BACKLOG_COMPLETION_UNPROVEN_BLOCKER}' must clear once "
                "only future-dependent blockers remain"
            ),
        )
        if current_phase == "Workstream":
            require(
                normalized_completion_status == "green",
                (
                    f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete Except "
                    f"Future Dependency requires '{CONTINUATION_COMPLETION_STATUS_LABEL}: Green' "
                    "before Workstream can exit"
                ),
            )
            require(
                next_legal_phase == "Hardening",
                (
                    f"{source_path}: {BACKLOG_COMPLETION_STATE_LABEL} Implemented Complete Except "
                    "Future Dependency in Workstream must advance Next Legal Phase to `Hardening`"
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

    audit_state = _extract_exact_marker_value(audit_section, "Release Window Audit")
    remaining_blockers = _extract_exact_marker_value(
        audit_section, "Remaining Known Release Blockers"
    )
    another_repair_pr = _extract_exact_marker_value(
        audit_section, "Another Pre-Release Repair PR Required"
    )
    split_waiver = _extract_exact_marker_value(
        audit_section, "Release Window Split Waiver"
    )
    split_waiver_reason = _extract_exact_marker_value(
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


def _codex_live_client_self_qa_section(text: str) -> str:
    return _section(text, "Codex Live Client Self-QA")


def _has_codex_live_client_self_qa(text: str) -> bool:
    return bool(_codex_live_client_self_qa_section(text))


def _parse_codex_live_client_self_qa_state(text: str) -> str:
    section = _codex_live_client_self_qa_section(text)
    matches = re.findall(
        rf"{re.escape(CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL)}\s*`?([A-Za-z]+)`?",
        section,
    )
    if not matches:
        return ""
    return matches[-1].strip().upper()


def _parse_codex_live_client_self_qa_waiver_reason(text: str) -> str:
    return _extract_marker_value(
        _codex_live_client_self_qa_section(text),
        CODEX_LIVE_CLIENT_SELF_QA_WAIVER_REASON_LABEL,
    )


def _codex_visual_adjudication_section(text: str) -> str:
    return _section(text, "Codex Visual Adjudication")


def _has_codex_visual_adjudication(text: str) -> bool:
    return bool(_codex_visual_adjudication_section(text))


def _parse_codex_visual_adjudication_state(text: str) -> str:
    section = _codex_visual_adjudication_section(text)
    matches = re.findall(
        rf"{re.escape(CODEX_VISUAL_ADJUDICATION_RESULT_LABEL)}\s*`?([A-Za-z]+)`?",
        section,
    )
    if not matches:
        return ""
    return matches[-1].strip().upper()


def _parse_codex_visual_adjudication_waiver_reason(text: str) -> str:
    return _extract_marker_value(
        _codex_visual_adjudication_section(text),
        CODEX_VISUAL_ADJUDICATION_WAIVER_REASON_LABEL,
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


def _requires_codex_visual_adjudication_gate(text: str) -> bool:
    text_lower = text.casefold()
    if "disabled/status-only" in text_lower and "waived" in text_lower:
        return False
    visual_markers = (
        "focused proof",
        "focused screenshot",
        "webview",
        "dashboard",
        "hud",
        "visual quality",
        "user-facing",
        "screenshot",
    )
    return any(marker in text_lower for marker in visual_markers)


def _collect_active_index_paths(text: str) -> set[str]:
    return _collect_index_paths_from_headings(text, REFORM_WORKSTREAM_ACTIVE_HEADINGS)


def _collect_closed_index_paths(text: str) -> set[str]:
    return _collect_index_paths_from_headings(text, REFORM_WORKSTREAM_CLOSED_HEADINGS)


def _collect_release_debt_index_paths(text: str) -> set[str]:
    return _collect_index_paths_from_headings(text, REFORM_WORKSTREAM_RELEASE_DEBT_HEADINGS)


def _collect_branch_record_paths(text: str, heading_prefix: str) -> set[str]:
    section = _section(text, heading_prefix)
    return set(re.findall(r"Docs/branch_records/[A-Za-z0-9._-]+\.md", section))


def _all_branch_record_detail_paths() -> set[str]:
    return {
        normalized_path
        for path in _git_tracked_files()
        for normalized_path in (path.as_posix(),)
        if normalized_path.startswith("Docs/branch_records/")
        and normalized_path.endswith(".md")
        and normalized_path != "Docs/branch_records/index.md"
    }


def _branch_record_live_state_scan_text(text: str) -> str:
    return text


def _branch_record_live_state_leakage_findings(
    relative_path: Path | str,
    text: str,
    active_branch_record_paths: set[str],
) -> list[str]:
    normalized_path = Path(relative_path).as_posix()
    if normalized_path == STANDING_GOVERNANCE_INTAKE_RECORD_PATH:
        return []

    findings: list[str] = []
    scan_text = _branch_record_live_state_scan_text(text)
    for finding_name, pattern in BRANCH_RECORD_LIVE_STATE_LEAKAGE_PATTERNS:
        if re.search(pattern, scan_text, flags=re.IGNORECASE | re.MULTILINE):
            findings.append(finding_name)

    if normalized_path in active_branch_record_paths:
        findings.append("listed in Active Branch Authority Records")

    return findings


def _run_branch_record_live_state_leakage_fixtures(require) -> None:
    fixture_root = ROOT_DIR / BRANCH_RECORD_LIVE_STATE_LEAKAGE_FIXTURE_DIR
    invalid_fixtures = sorted(
        fixture_root.glob("invalid_*.md")
    )
    valid_fixture = (
        BRANCH_RECORD_LIVE_STATE_LEAKAGE_FIXTURE_DIR
        / "valid_historical_branch_record_receipt.md"
    )
    valid_text = _read_text(valid_fixture)
    require(
        bool(invalid_fixtures),
        f"{BRANCH_RECORD_LIVE_STATE_LEAKAGE_FIXTURE_DIR}: missing invalid branch-record leakage fixtures",
    )
    for invalid_fixture in invalid_fixtures:
        invalid_fixture_relative = invalid_fixture.relative_to(ROOT_DIR)
        invalid_text = _read_text(invalid_fixture_relative)
        require(
            bool(
                _branch_record_live_state_leakage_findings(
                    Path("Docs/branch_records") / invalid_fixture.name,
                    invalid_text,
                    set(),
                )
            ),
            (
                f"{invalid_fixture_relative}: branch-record live-state leakage fixture must fail; "
                "unindexed live branch records cannot pass as durable receipts"
            ),
        )
    require(
        not _branch_record_live_state_leakage_findings(
            Path("Docs/branch_records/valid_historical_branch_record_receipt.md"),
            valid_text,
            set(),
        ),
        f"{valid_fixture}: historical branch-record receipt fixture must not fail live-state leakage scan",
    )


def _collect_merge_stable_detail_record_paths(*texts: str) -> set[str]:
    paths: set[str] = set()
    for text in texts:
        current_block: list[str] = []
        blocks: list[str] = []
        for line in text.splitlines():
            if line.strip():
                current_block.append(line)
                continue
            if current_block:
                blocks.append("\n".join(current_block))
                current_block = []
        if current_block:
            blocks.append("\n".join(current_block))

        for block in blocks:
            normalized_block = block.casefold()
            if "merged-unreleased" not in normalized_block and not re.search(r"\bPR #\d+", block):
                continue
            paths.update(re.findall(r"Docs/branch_records/[A-Za-z0-9._-]+\.md", block))
    return paths


def _family_id_from_text(value: str) -> str:
    match = re.search(r"fam[-_](\d{3})", value.casefold())
    return f"FAM-{match.group(1)}" if match else ""


def _is_outside_current_family_lane(record_path: str, record_text: str, current_branch: str) -> bool:
    if not current_branch or current_branch == "main":
        return False
    if _is_standing_governance_intake_branch(current_branch):
        return False
    current_family = _family_id_from_text(current_branch)
    if not current_family:
        return False
    record_family = (
        _family_id_from_text(record_path)
        or _family_id_from_text(_extract_branch_identity_branch(record_text))
        or _family_id_from_text(record_text)
    )
    return bool(record_family and record_family != current_family)


def _stale_pre_pr_lines(text: str) -> list[tuple[int, str]]:
    stale_lines: list[tuple[int, str]] = []
    for index, line in enumerate(text.splitlines(), start=1):
        normalized_line = line.casefold()
        if not any(phrase in normalized_line for phrase in MERGE_STABLE_STALE_PRE_PR_PHRASES):
            continue
        if any(allowed in normalized_line for allowed in MERGE_STABLE_STALE_CONTEXT_ALLOWLIST):
            continue
        stale_lines.append((index, line.strip()))
    return stale_lines


def _run_merge_stable_source_truth_projection_gate(
    require,
    *,
    backlog_text: str,
    roadmap_text: str,
    worktree_slots_text: str,
    branch_record_index_text: str,
    current_branch: str,
    outside_lane_findings: list[str],
) -> None:
    pointer_docs = (
        ("Docs/feature_backlog.md", backlog_text),
        ("Docs/prebeta_roadmap.md", roadmap_text),
        ("Docs/worktree_slots.md", worktree_slots_text),
    )
    for path, text in pointer_docs:
        stale_lines = _stale_pre_pr_lines(text)
        require(
            not stale_lines,
            (
                f"{path}: Merge-Stable Source Truth Projection Missing; compact "
                "current-state/pointer surface retains pre-PR or PR-creation-pending wording: "
                + "; ".join(f"line {line_no}: {line}" for line_no, line in stale_lines[:5])
            ),
        )

    historical_branch_record_paths = _collect_branch_record_paths(
        branch_record_index_text,
        "Historical Branch Authority Records",
    )
    detail_record_paths = _collect_merge_stable_detail_record_paths(
        backlog_text,
        roadmap_text,
        worktree_slots_text,
    )
    retirement_index_text = _read_text(Path("Docs/branch_plans/retirement_index.md"))
    for record_path in sorted(detail_record_paths & historical_branch_record_paths):
        record_text = _read_text(Path(record_path))
        merged_record = "merged-unreleased" in record_text.casefold() or "Merge PR:" in record_text
        if not merged_record:
            continue
        outside_current_lane = _is_outside_current_family_lane(
            record_path,
            record_text,
            current_branch,
        )

        def require_or_classify(condition: bool, message: str) -> None:
            if condition:
                require(True, message)
                return
            if outside_current_lane:
                outside_lane_findings.append(message)
                require(True, f"Outside-lane merge-stable finding classified for {record_path}")
                return
            require(False, message)

        summary_text = "\n".join(
            section
            for section in (
                _section(record_text, "Status"),
                _section(record_text, "Current Phase"),
                _section(record_text, "Phase Status"),
                _section(record_text, "Bounded State"),
                _section(record_text, "Post-Merge State"),
                _section(record_text, "Release Readiness Health Pass"),
            )
            if section
        )
        stale_lines = _stale_pre_pr_lines(summary_text)
        require_or_classify(
            not stale_lines,
            (
                f"{record_path}: Merge-Stable Source Truth Projection Missing; "
                "canonical merged-unreleased branch record retains pre-PR or "
                "PR-creation-pending summary/current-state wording: "
                + "; ".join(f"line {line_no}: {line}" for line_no, line in stale_lines[:5])
            ),
        )
        require_or_classify(
            "Merge PR:" in record_text or re.search(r"\bPR #\d+\b", record_text),
            (
                f"{record_path}: merged-unreleased branch record must name the "
                "merge PR or equivalent PR receipt"
            ),
        )
        for plan_path in sorted(set(re.findall(r"Docs/branch_plans/[A-Za-z0-9._-]+\.md", record_text))):
            if plan_path in {"Docs/branch_plans/README.md", "Docs/branch_plans/retirement_index.md"}:
                continue
            plan = Path(plan_path)
            if not (ROOT_DIR / plan).exists():
                continue
            require_or_classify(
                plan_path in retirement_index_text,
                (
                    f"{record_path}: merged-unreleased canonical branch record points to "
                    f"{plan_path}, but the plan is not listed in Docs/branch_plans/retirement_index.md"
                ),
            )


def _is_backlog_family_reform_branch(branch_name: str) -> bool:
    normalized = (branch_name or "").strip()
    return normalized in {
        BACKLOG_FAMILY_REFORM_BRANCH,
        f"origin/{BACKLOG_FAMILY_REFORM_BRANCH}",
    }


def _is_automation_planning_branch(branch_name: str) -> bool:
    normalized = (branch_name or "").strip()
    return normalized in {
        AUTOMATION_PLANNING_BRANCH,
        f"origin/{AUTOMATION_PLANNING_BRANCH}",
    }


def _is_automation_closeout_repair_branch(branch_name: str) -> bool:
    normalized = (branch_name or "").strip()
    return normalized in {
        AUTOMATION_CLOSEOUT_REPAIR_BRANCH,
        f"origin/{AUTOMATION_CLOSEOUT_REPAIR_BRANCH}",
    }


def _is_pr101_closeout_canon_repair_branch(branch_name: str) -> bool:
    normalized = (branch_name or "").strip()
    return normalized in {
        PR101_CLOSEOUT_CANON_REPAIR_BRANCH,
        f"origin/{PR101_CLOSEOUT_CANON_REPAIR_BRANCH}",
    }


def _is_pr102_closeout_canon_repair_branch(branch_name: str) -> bool:
    normalized = (branch_name or "").strip()
    return normalized in {
        PR102_CLOSEOUT_CANON_REPAIR_BRANCH,
        f"origin/{PR102_CLOSEOUT_CANON_REPAIR_BRANCH}",
    }


def _is_pr103_closeout_canon_repair_branch(branch_name: str) -> bool:
    normalized = (branch_name or "").strip()
    return normalized in {
        PR103_CLOSEOUT_CANON_REPAIR_BRANCH,
        f"origin/{PR103_CLOSEOUT_CANON_REPAIR_BRANCH}",
    }


def _validate_backlog_family_reform_bootstrap(
    require,
    *,
    current_branch: str,
    backlog_text: str,
    index_text: str,
    backlog_entries: list[dict[str, str]],
) -> None:
    if not _is_backlog_family_reform_branch(current_branch):
        return

    has_reform_backlog_shape = _has_all_headings(backlog_text, REFORM_BACKLOG_SHAPE_HEADINGS)
    require(
        has_reform_backlog_shape,
        (
            "Docs/feature_backlog.md: validator finalization on "
            f"{BACKLOG_FAMILY_REFORM_BRANCH} requires the reform backlog-family shape"
        ),
    )
    require(
        not _has_any_heading(backlog_text, CURRENT_BACKLOG_SHAPE_HEADINGS[1:]),
        (
            "Docs/feature_backlog.md: validator finalization on "
            f"{BACKLOG_FAMILY_REFORM_BRANCH} must not rely on the pre-reform "
            "`Closed Canonical Workstreams` backlog shape"
        ),
    )

    has_reform_index_shape = _has_all_headings(index_text, REFORM_WORKSTREAM_INDEX_SHAPE_HEADINGS)
    require(
        has_reform_index_shape,
        (
            "Docs/workstreams/index.md: validator finalization on "
            f"{BACKLOG_FAMILY_REFORM_BRANCH} requires the reform family-index split"
        ),
    )

    registry_classes = [
        _clean_release_value(_extract_colon_value(entry["block"], "Registry Class"))
        for entry in backlog_entries
    ]
    if any(registry_classes):
        missing_registry_class_ids = [
            entry["id"]
            for entry, registry_class in zip(backlog_entries, registry_classes)
            if not registry_class
        ]
        require(
            not missing_registry_class_ids,
            (
                "Docs/feature_backlog.md: once reform classification markers land on the "
                "migration branch, every backlog entry must declare a valid Registry Class "
                "before later relocation seams begin"
            ),
        )

    for entry, registry_class in zip(backlog_entries, registry_classes):
        block = entry["block"]
        if not registry_class:
            continue

        require(
            registry_class in VALID_BACKLOG_REGISTRY_CLASSES,
            (
                f"Docs/feature_backlog.md: {entry['id']} has invalid Registry Class "
                f"'{registry_class}'"
            ),
        )

        if registry_class == "Feature Family":
            family_anchor = _clean_release_value(_extract_colon_value(block, "Family Anchor"))
            require(
                family_anchor == "Self",
                (
                    f"Docs/feature_backlog.md: {entry['id']} Feature Family entry must declare "
                    "`Family Anchor: Self`"
                ),
            )
        elif registry_class == "Historical Pass Alias":
            alias_of = _clean_release_value(_extract_colon_value(block, "Historical Alias Of"))
            pass_id = _clean_release_value(_extract_colon_value(block, "Pass ID"))
            alias_role = _clean_release_value(_extract_colon_value(block, "Alias Role"))
            independently_selectable = _clean_release_value(
                _extract_colon_value(block, "Selectable Independently")
            )
            require(
                bool(alias_of),
                f"Docs/feature_backlog.md: {entry['id']} Historical Pass Alias must declare Historical Alias Of",
            )
            require(
                bool(pass_id),
                f"Docs/feature_backlog.md: {entry['id']} Historical Pass Alias must declare Pass ID",
            )
            require(
                alias_role == "Historical Pass Record",
                (
                    f"Docs/feature_backlog.md: {entry['id']} Historical Pass Alias must declare "
                    "`Alias Role: Historical Pass Record`"
                ),
            )
            require(
                independently_selectable.casefold() == "no",
                (
                    f"Docs/feature_backlog.md: {entry['id']} Historical Pass Alias must declare "
                    "`Selectable Independently: No`"
                ),
            )

    if has_reform_backlog_shape:
        reform_heading_positions = [backlog_text.find(heading) for heading in REFORM_BACKLOG_ORDERED_HEADINGS]
        require(
            reform_heading_positions == sorted(reform_heading_positions),
            (
                "Docs/feature_backlog.md: reform backlog-family headings must remain ordered as "
                "User-Facing Feature Families, Historical Consolidated Pass Aliases, Support / "
                "Architecture / Governance Lanes, then Historical Implemented Registry-Only Items"
            ),
        )
        require(
            TRANSITIONAL_CURRENT_REGISTRY_ORDER_HEADING not in backlog_text,
            (
                "Docs/feature_backlog.md: transitional current registry order heading must be "
                "removed after Slice R2-S5 ordering hardening"
            ),
        )

        reform_section_entries = {
            heading: _parse_backlog_subsection(backlog_text, heading)
            for heading, _ in REFORM_BACKLOG_SECTION_CLASS_RULES
        }
        feature_family_ids = {entry["id"] for entry in reform_section_entries["User-Facing Feature Families"]}
        require(
            bool(feature_family_ids),
            (
                "Docs/feature_backlog.md: User-Facing Feature Families must contain the selectable "
                "feature-family records after Slice R2-S5"
            ),
        )

        for heading, expected_registry_class in REFORM_BACKLOG_SECTION_CLASS_RULES:
            section_entries = reform_section_entries[heading]
            section_ids = [entry["id"] for entry in section_entries]
            require(
                section_ids == sorted(section_ids, key=_backlog_id_number, reverse=True),
                (
                    f"Docs/feature_backlog.md: {heading} entries must remain in descending "
                    "`FB-XXX` order"
                ),
            )
            for section_entry in section_entries:
                actual_registry_class = _clean_release_value(
                    _extract_colon_value(section_entry["block"], "Registry Class")
                )
                require(
                    actual_registry_class == expected_registry_class,
                    (
                        f"Docs/feature_backlog.md: {section_entry['id']} must live under "
                        f"'{heading}' with Registry Class '{expected_registry_class}'"
                    ),
                )

        for registry_class_name, heading in (
            ("Feature Family", "User-Facing Feature Families"),
            ("Historical Pass Alias", "Historical Consolidated Pass Aliases"),
            ("Support Lane", "Support / Architecture / Governance Lanes"),
        ):
            class_ids = {
                entry["id"]
                for entry, registry_class in zip(backlog_entries, registry_classes)
                if registry_class == registry_class_name
            }
            require(
                class_ids == {entry["id"] for entry in reform_section_entries[heading]},
                (
                    f"Docs/feature_backlog.md: all {registry_class_name} entries must live under "
                    f"'{heading}' after Slice R2-S5"
                ),
            )

        selected_next_ids = {entry["id"] for entry in _selected_next_workstream_entries(backlog_entries)}
        require(
            selected_next_ids <= feature_family_ids,
            (
                "Docs/feature_backlog.md: selected-next backlog entries must remain inside "
                "'User-Facing Feature Families' after Slice R2-S5"
            ),
        )


def _validate_backlog_family_reform_seam_truth(
    require,
    *,
    current_branch: str,
    backlog_entries: list[dict[str, str]],
    backlog_text: str,
    roadmap_text: str,
) -> None:
    if not _is_backlog_family_reform_branch(current_branch):
        return

    branch_record_text = _read_text(BACKLOG_FAMILY_REFORM_BRANCH_RECORD)
    backlog_workstream_state = _extract_colon_value(backlog_text, "Current Workstream State")
    roadmap_workstream_state = _extract_colon_value(roadmap_text, "Current Workstream State")
    phase_status_section = _section(branch_record_text, "Phase Status")
    active_seam_section = _section(branch_record_text, "Active Seam")
    continuation_section = _section(branch_record_text, "Seam Continuation Decision")
    continuation_slice_status = _extract_marker_value(
        continuation_section, CONTINUATION_SLICE_STATUS_LABEL
    )
    continuation_completion_status = _extract_marker_value(
        continuation_section, CONTINUATION_COMPLETION_STATUS_LABEL
    )
    continuation_decision = _extract_marker_value(continuation_section, "Continue Decision")
    phase_status_next_seam = _extract_marker_value(phase_status_section, "Next Active Seam")
    continuation_next_seam = _extract_marker_value(continuation_section, "Next Active Seam")
    active_seam_match = re.search(r"^Next active seam:\s*`([^`]+)`", active_seam_section, flags=re.M)
    active_seam_next = active_seam_match.group(1).strip() if active_seam_match else ""
    active_seam_current = _extract_marker_value(active_seam_section, "Active seam")
    current_phase = _extract_marker_value(_section(branch_record_text, "Current Phase"), "Phase")
    next_legal_phase = _extract_first_backtick_value(_section(branch_record_text, "Next Legal Phase"))
    phase_status_hardening_seam = _extract_marker_value(phase_status_section, "Current Hardening Seam")
    phase_status_live_validation_seam = _extract_marker_value(
        phase_status_section, "Current Live Validation Seam"
    )
    phase_status_pr_readiness_seam = _extract_marker_value(
        phase_status_section, "Current PR Readiness Seam"
    )
    phase_status_release_readiness_seam = _extract_marker_value(
        phase_status_section, "Current Release Readiness Seam"
    )
    backlog_next_legal_phase = _extract_colon_value(backlog_text, "Next Legal Phase").rstrip(".")
    roadmap_next_legal_phase = _extract_colon_value(roadmap_text, "Next Legal Phase").rstrip(".")

    if _historical_alias_mapping_matches(
        backlog_entries,
        alias_ids=REFORM_FB042_ALIAS_IDS,
        family_anchor_id="FB-042",
    ):
        require(
            REFORM_R3_S2_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R3-S2 must not remain the next seam once FB-043 "
                "through FB-048 already declare `Historical Alias Of: FB-042`"
            ),
        )
        require(
            REFORM_R3_S2_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R3-S2 must not remain the next seam once FB-043 "
                "through FB-048 already declare `Historical Alias Of: FB-042`"
            ),
        )
        require(
            REFORM_R3_S2_STATE_NEXT_PHRASE not in phase_status_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must not report R3-S2 as next once FB-043 through FB-048 already declare "
                "`Historical Alias Of: FB-042`"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R3_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R3-S2 once the FB-042 alias mapping is "
                "already satisfied in repo truth"
            ),
        )
        require(
            REFORM_R3_S2_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R3-S2 as the next active seam once the FB-042 alias mapping is "
                "already satisfied in repo truth"
            ),
        )
        require(
            active_seam_next != REFORM_R3_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R3-S2 once the FB-042 alias mapping is "
                "already satisfied in repo truth"
            ),
        )
        require(
            continuation_next_seam != REFORM_R3_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R3-S2 as `Next Active Seam` once the "
                "FB-042 alias mapping is already satisfied in repo truth"
            ),
        )
        require(
            REFORM_R3_S2_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R3-S2 continuation action once the "
                "FB-042 alias mapping is already satisfied in repo truth"
            ),
        )

    if _historical_alias_mapping_matches(
        backlog_entries,
        alias_ids=REFORM_FB027_ALIAS_IDS,
        family_anchor_id="FB-027",
    ):
        require(
            REFORM_R3_S4_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R3-S4 must not remain the next seam once FB-036, "
                "FB-037, FB-038, and FB-041 already declare `Historical Alias Of: FB-027`"
            ),
        )
        require(
            REFORM_R3_S4_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R3-S4 must not remain the next seam once FB-036, "
                "FB-037, FB-038, and FB-041 already declare `Historical Alias Of: FB-027`"
            ),
        )
        require(
            REFORM_R3_S4_STATE_NEXT_PHRASE not in phase_status_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must not report R3-S4 as next once FB-036, FB-037, FB-038, and FB-041 already "
                "declare `Historical Alias Of: FB-027`"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R3_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R3-S4 once the FB-027 alias mapping is "
                "already satisfied in repo truth"
            ),
        )
        require(
            REFORM_R3_S4_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R3-S4 as the next active seam once the FB-027 alias mapping is "
                "already satisfied in repo truth"
            ),
        )
        require(
            active_seam_next != REFORM_R3_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R3-S4 once the FB-027 alias mapping is "
                "already satisfied in repo truth"
            ),
        )
        require(
            continuation_next_seam != REFORM_R3_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R3-S4 as `Next Active Seam` once the "
                "FB-027 alias mapping is already satisfied in repo truth"
            ),
        )
        require(
            REFORM_R3_S4_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R3-S4 continuation action once the "
                "FB-027 alias mapping is already satisfied in repo truth"
            ),
        )

    if REFORM_FB042_DOSSIER_PATH.is_file():
        require(
            REFORM_R4_S1_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R4-S1 must not remain the next seam once the FB-042 "
                "dossier shell exists in repo truth"
            ),
        )
        require(
            REFORM_R4_S1_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R4-S1 must not remain the next seam once the FB-042 "
                "dossier shell exists in repo truth"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R4_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R4-S1 once the FB-042 dossier shell exists"
            ),
        )
        require(
            active_seam_next != REFORM_R4_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R4-S1 once the FB-042 dossier shell exists"
            ),
        )
        require(
            continuation_next_seam != REFORM_R4_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R4-S1 as `Next Active Seam` once the "
                "FB-042 dossier shell exists"
            ),
        )

    if REFORM_FB027_DOSSIER_PATH.is_file():
        require(
            REFORM_R4_S2_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R4-S2 must not remain the next seam once the FB-027 "
                "dossier shell exists in repo truth"
            ),
        )
        require(
            REFORM_R4_S2_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R4-S2 must not remain the next seam once the FB-027 "
                "dossier shell exists in repo truth"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R4_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R4-S2 once the FB-027 dossier shell exists"
            ),
        )
        require(
            active_seam_next != REFORM_R4_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R4-S2 once the FB-027 dossier shell exists"
            ),
        )
        require(
            continuation_next_seam != REFORM_R4_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R4-S2 as `Next Active Seam` once the "
                "FB-027 dossier shell exists"
            ),
        )

    def dossier_has_r4_s3_structure(dossier_path: Path) -> bool:
        if not dossier_path.is_file():
            return False
        dossier_text = _read_text(dossier_path)
        return (
            "Pass Index Status: `Structure introduced in Slice R4-S3`" in dossier_text
            and "Slice / Seam Ledger Status: `Structure introduced in Slice R4-S3`" in dossier_text
        )

    if dossier_has_r4_s3_structure(REFORM_FB042_DOSSIER_PATH) and dossier_has_r4_s3_structure(
        REFORM_FB027_DOSSIER_PATH
    ):
        require(
            REFORM_R4_S3_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R4-S3 must not remain the next seam once both family "
                "dossiers carry the shared pass-index and slice/seam-ledger structures"
            ),
        )
        require(
            REFORM_R4_S3_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R4-S3 must not remain the next seam once both family "
                "dossiers carry the shared pass-index and slice/seam-ledger structures"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R4_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R4-S3 once both family dossiers carry the "
                "shared pass-index and slice/seam-ledger structures"
            ),
        )
        require(
            active_seam_next != REFORM_R4_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R4-S3 once both family dossiers carry the "
                "shared pass-index and slice/seam-ledger structures"
            ),
        )
        require(
            continuation_next_seam != REFORM_R4_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R4-S3 as `Next Active Seam` once both "
                "family dossiers carry the shared pass-index and slice/seam-ledger structures"
            ),
        )

    def dossier_has_r4_s4_structure(dossier_path: Path) -> bool:
        if not dossier_path.is_file():
            return False
        dossier_text = _read_text(dossier_path)
        return (
            "Validator / Helper Index Status: `Structure introduced in Slice R4-S4`" in dossier_text
            and "Artifact Index Status: `Structure introduced in Slice R4-S4`" in dossier_text
        )

    if dossier_has_r4_s4_structure(REFORM_FB042_DOSSIER_PATH) and dossier_has_r4_s4_structure(
        REFORM_FB027_DOSSIER_PATH
    ):
        require(
            REFORM_R4_S4_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R4-S4 must not remain the next seam once both family "
                "dossiers carry the shared validator/helper and artifact index structures"
            ),
        )
        require(
            REFORM_R4_S4_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R4-S4 must not remain the next seam once both family "
                "dossiers carry the shared validator/helper and artifact index structures"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R4_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R4-S4 once both family dossiers carry the "
                "shared validator/helper and artifact index structures"
            ),
        )
        require(
            active_seam_next != REFORM_R4_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R4-S4 once both family dossiers carry the "
                "shared validator/helper and artifact index structures"
            ),
        )
        require(
            continuation_next_seam != REFORM_R4_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R4-S4 as `Next Active Seam` once both "
                "family dossiers carry the shared validator/helper and artifact index structures"
            ),
        )

    def dossier_has_r4_s5_stability_validation(dossier_path: Path) -> bool:
        if not dossier_path.is_file():
            return False
        dossier_text = _read_text(dossier_path)
        return "Dossier Stability Validation Status: `Validated in Slice R4-S5`" in dossier_text

    if dossier_has_r4_s5_stability_validation(
        REFORM_FB042_DOSSIER_PATH
    ) and dossier_has_r4_s5_stability_validation(REFORM_FB027_DOSSIER_PATH):
        require(
            REFORM_R4_S5_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R4-S5 must not remain the next seam once both family "
                "dossiers carry the dossier-stability validation marker"
            ),
        )
        require(
            REFORM_R4_S5_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R4-S5 must not remain the next seam once both family "
                "dossiers carry the dossier-stability validation marker"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R4_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R4-S5 once both family dossiers carry the "
                "dossier-stability validation marker"
            ),
        )
        require(
            active_seam_next != REFORM_R4_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R4-S5 once both family dossiers carry the "
                "dossier-stability validation marker"
            ),
        )
        require(
            continuation_next_seam != REFORM_R4_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R4-S5 as `Next Active Seam` once both "
                "family dossiers carry the dossier-stability validation marker"
            ),
        )

    def fb042_workstream_pass_records_converted() -> bool:
        for workstream_path, info in REFORM_FB042_HISTORICAL_PASS_DOCS.items():
            if not workstream_path.is_file():
                return False
            workstream_text = _read_text(workstream_path)
            required_phrases = (
                "## Historical Pass Record Identity",
                "Family Anchor ID: `FB-042`",
                "Family Dossier Doc: `Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md`",
                "Backlog Registry Class: `Historical Pass Alias`",
                "Historical Alias Of: `FB-042`",
                f"Pass ID: `{info['pass_id']}`",
                "Alias Role: `Historical Pass Record`",
                "Standalone Selection Status: `Not independently selectable`",
                "Converted By Seam: `Phase 5 - Historical Pass Record Conversion / Slice R5-S1 - Convert FB-043 through FB-048 workstream records`",
                f"Historical Branch Readiness Record: `{info['branch_record']}`",
            )
            if any(phrase not in workstream_text for phrase in required_phrases):
                return False
        return True

    if fb042_workstream_pass_records_converted():
        require(
            REFORM_R5_S1_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R5-S1 must not remain the next seam once FB-043 "
                "through FB-048 are converted into explicit FB-042 historical pass records"
            ),
        )
        require(
            REFORM_R5_S1_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R5-S1 must not remain the next seam once FB-043 "
                "through FB-048 are converted into explicit FB-042 historical pass records"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R5_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R5-S1 once FB-043 through FB-048 are "
                "converted into explicit FB-042 historical pass records"
            ),
        )
        require(
            REFORM_R5_S1_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R5-S1 as the next active seam once the FB-042 historical pass "
                "record conversion is complete"
            ),
        )
        require(
            active_seam_next != REFORM_R5_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R5-S1 once the FB-042 historical pass "
                "record conversion is complete"
            ),
        )
        require(
            continuation_next_seam != REFORM_R5_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R5-S1 as `Next Active Seam` once the "
                "FB-042 historical pass record conversion is complete"
            ),
        )
        require(
            REFORM_R5_S1_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R5-S1 continuation action once the "
                "FB-042 historical pass record conversion is complete"
            ),
        )

    def fb027_workstream_pass_records_converted() -> bool:
        for workstream_path, info in REFORM_FB027_HISTORICAL_PASS_DOCS.items():
            if not workstream_path.is_file():
                return False
            workstream_text = _read_text(workstream_path)
            required_phrases = (
                "Lifetime Dossier Doc: `Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md`",
                "## Historical Pass Record Identity",
                "Family Anchor ID: `FB-027`",
                "Family Dossier Doc: `Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md`",
                "Backlog Registry Class: `Historical Pass Alias`",
                "Historical Alias Of: `FB-027`",
                f"Pass ID: `{info['pass_id']}`",
                "Alias Role: `Historical Pass Record`",
                "Standalone Selection Status: `Not independently selectable`",
                "Converted By Seam: `Phase 5 - Historical Pass Record Conversion / Slice R5-S2 - Convert FB-036, FB-037, FB-038, and FB-041 workstream records`",
                info["branch_record_phrase"],
            )
            if any(phrase not in workstream_text for phrase in required_phrases):
                return False
        return True

    if fb027_workstream_pass_records_converted():
        require(
            REFORM_R5_S2_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R5-S2 must not remain the next seam once FB-036, "
                "FB-037, FB-038, and FB-041 are converted into explicit FB-027 historical pass "
                "records"
            ),
        )
        require(
            REFORM_R5_S2_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R5-S2 must not remain the next seam once FB-036, "
                "FB-037, FB-038, and FB-041 are converted into explicit FB-027 historical pass "
                "records"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R5_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R5-S2 once FB-036, FB-037, FB-038, and "
                "FB-041 are converted into explicit FB-027 historical pass records"
            ),
        )
        require(
            REFORM_R5_S2_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R5-S2 as the next active seam once the FB-027 historical pass "
                "record conversion is complete"
            ),
        )
        require(
            active_seam_next != REFORM_R5_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R5-S2 once the FB-027 historical pass "
                "record conversion is complete"
            ),
        )
        require(
            continuation_next_seam != REFORM_R5_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R5-S2 as `Next Active Seam` once the "
                "FB-027 historical pass record conversion is complete"
            ),
        )
        require(
            REFORM_R5_S2_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R5-S2 continuation action once the "
                "FB-027 historical pass record conversion is complete"
            ),
        )

    def historical_pass_branch_records_converted() -> bool:
        for branch_record_path, info in REFORM_HISTORICAL_PASS_BRANCH_RECORDS.items():
            if not branch_record_path.is_file():
                return False
            branch_record_text = _read_text(branch_record_path)
            required_phrases = (
                "## Historical Pass Record Identity",
                f"Family Anchor ID: `{info['family_anchor_id']}`",
                f"Family Dossier Doc: `{info['family_dossier']}`",
                "Backlog Registry Class: `Historical Pass Alias`",
                f"Historical Alias Of: `{info['family_anchor_id']}`",
                f"Pass ID: `{info['pass_id']}`",
                "Alias Role: `Historical Pass Record`",
                "Standalone Selection Status: `Not independently selectable`",
                "Converted By Seam: `Phase 5 - Historical Pass Record Conversion / Slice R5-S3 - Convert corresponding branch records`",
                f"Corresponding Historical Workstream Record: `{info['workstream_record']}`",
                f"Preservation Rule: `{info['preservation_rule']}`",
            )
            if any(phrase not in branch_record_text for phrase in required_phrases):
                return False
        return True

    def historical_alias_future_selection_language_stripped() -> bool:
        for doc_path, expectations in REFORM_R5_S4_HISTORICAL_LANGUAGE_DOCS.items():
            if not doc_path.is_file():
                return False
            doc_text = _read_text(doc_path)
            if any(phrase not in doc_text for phrase in expectations["required"]):
                return False
            if any(phrase in doc_text for phrase in expectations["prohibited"]):
                return False
        return True

    def historical_pass_traceability_sweep_complete() -> bool:
        for doc_path, required_phrases in REFORM_R5_S5_TRACEABILITY_REQUIRED_PHRASES.items():
            if not doc_path.is_file():
                return False
            doc_text = _read_text(doc_path)
            if any(phrase not in doc_text for phrase in required_phrases):
                return False
        return True

    def roadmap_anchor_conversion_complete() -> bool:
        return all(
            phrase in roadmap_text for phrase in REFORM_R6_S1_ROADMAP_REQUIRED_PHRASES
        )

    def workstream_index_split_complete() -> bool:
        workstreams_index_text = _read_text(Path("Docs/workstreams/index.md"))
        return all(phrase in workstreams_index_text for phrase in REFORM_R6_S2_INDEX_REQUIRED_PHRASES)

    def main_router_loader_aligned() -> bool:
        for doc_path, required_phrases in REFORM_R6_S3_ROUTER_REQUIRED_PHRASES.items():
            if not doc_path.is_file():
                return False
            doc_text = _read_text(doc_path)
            if any(phrase not in doc_text for phrase in required_phrases):
                return False
        return True

    def selected_next_truth_validated() -> bool:
        selected_entries = _selected_next_workstream_entries(backlog_entries)
        if len(selected_entries) != 1:
            return False

        selected_entry = selected_entries[0]
        selected_block = selected_entry["block"]
        roadmap_selected_section = _next_workstream_roadmap_section(roadmap_text)

        if selected_entry["id"] != "FB-049" or selected_entry["record_state"] != "Registry-only":
            return False
        if any(
            phrase not in selected_block
            for phrase in (
                "Status: Selected next",
                "Registry Class: Feature Family",
                "Next Workstream: Selected",
                "Branch: Not created",
            )
        ):
            return False
        if len(re.findall(r"^Status:\s*Selected next\s*$", backlog_text, flags=re.M)) != 1:
            return False
        if len(re.findall(r"^Next Workstream:\s*Selected\s*$", backlog_text, flags=re.M)) != 1:
            return False
        if any(
            phrase not in roadmap_selected_section
            for phrase in (
                "- ID: `FB-049`",
                "- Record State: `Registry-only`",
                "- Branch: Not created",
            )
        ):
            return False
        if any(
            phrase not in backlog_text
            for phrase in (
                "Selected Next Workstream: FB-049 Active-session pre-settled incoming-launch conflict truth.",
                "Selected Next Record State: Registry-only.",
                "Selected Next Implementation Branch: Not created.",
            )
        ):
            return False
        if any(
            phrase not in roadmap_text
            for phrase in (
                "Selected Next Workstream: FB-049 Active-session pre-settled incoming-launch conflict truth.",
                "Selected Next Record State: Registry-only.",
                "Selected Next Implementation Branch: `Not created`",
            )
        ):
            return False
        if any(
            phrase not in phase_status_section
            for phrase in (
                "Selected Next Workstream: FB-049 Active-session pre-settled incoming-launch conflict truth.",
                "Selected Next Record State: Registry-only.",
                "Selected Next Implementation Branch: Not created.",
            )
        ):
            return False
        return True

    def phase6_drift_sweep_clean() -> bool:
        main_text = _read_text(Path("Docs/Main.md"))
        index_text = _read_text(Path("Docs/workstreams/index.md"))
        return (
            main_router_loader_aligned()
            and selected_next_truth_validated()
            and "### Family Dossiers And Historical Pass Trace Routing" in main_text
            and "### Family Dossiers And Alias Records" not in main_text
            and "### Family Anchor Records" in index_text
            and "### Historical Pass Alias Records" in index_text
            and "### Other Closed Workstreams" in index_text
            and TRANSITIONAL_CURRENT_REGISTRY_ORDER_HEADING not in backlog_text
        )

    def temporary_dual_shape_tolerance_removed() -> bool:
        validator_text = _read_text(Path("dev/orin_branch_governance_validation.py"))
        old_backlog_tolerance_phrase = (
            "must accept either the current backlog shape "
            "or the reform backlog-family shape"
        )
        old_index_tolerance_phrase = (
            "must accept either the current workstream-index shape "
            "or the reform family-index split"
        )
        return (
            old_backlog_tolerance_phrase not in validator_text
            and old_index_tolerance_phrase not in validator_text
            and "requires the reform backlog-family shape" in validator_text
            and "requires the reform family-index split" in validator_text
        )

    def hard_anti_drift_checks_enforced() -> bool:
        validator_text = _read_text(Path("dev/orin_branch_governance_validation.py"))
        required_phrases = (
            "reform hard anti-drift requires selected-next truth to remain validated across backlog, roadmap, branch authority, and validator expectations",
            "reform hard anti-drift requires the sweep-clean Phase 6 family-governance routing surfaces to remain intact",
            "reform hard anti-drift requires temporary dual-shape tolerance to stay removed",
            "reform hard anti-drift: historical pass alias",
            "reform hard anti-drift: support lane",
        )
        return all(phrase in validator_text for phrase in required_phrases)

    if historical_pass_branch_records_converted():
        require(
            REFORM_R5_S3_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R5-S3 must not remain the next seam once the "
                "preserved corresponding branch records are converted into explicit historical "
                "pass records"
            ),
        )
        require(
            REFORM_R5_S3_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R5-S3 must not remain the next seam once the "
                "preserved corresponding branch records are converted into explicit historical "
                "pass records"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R5_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R5-S3 once the preserved corresponding "
                "branch records are converted"
            ),
        )
        require(
            REFORM_R5_S3_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R5-S3 as the next active seam once the preserved corresponding "
                "branch records are converted"
            ),
        )
        require(
            active_seam_next != REFORM_R5_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R5-S3 once the preserved corresponding "
                "branch records are converted"
            ),
        )
        require(
            continuation_next_seam != REFORM_R5_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R5-S3 as `Next Active Seam` once the "
                "preserved corresponding branch records are converted"
            ),
        )
        require(
            REFORM_R5_S3_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R5-S3 continuation action once the "
                "preserved corresponding branch records are converted"
            ),
        )

    if historical_alias_future_selection_language_stripped():
        require(
            REFORM_R5_S4_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R5-S4 must not remain the next seam once live-sounding "
                "future-selection language is stripped from the converted historical alias set"
            ),
        )
        require(
            REFORM_R5_S4_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R5-S4 must not remain the next seam once live-sounding "
                "future-selection language is stripped from the converted historical alias set"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R5_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R5-S4 once historical alias records are "
                "reframed as historical-only follow-through surfaces"
            ),
        )
        require(
            REFORM_R5_S4_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R5-S4 as the next active seam once historical alias future-"
                "selection language is stripped"
            ),
        )
        require(
            active_seam_next != REFORM_R5_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R5-S4 once historical alias future-"
                "selection language is stripped"
            ),
        )
        require(
            continuation_next_seam != REFORM_R5_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R5-S4 as `Next Active Seam` once "
                "historical alias future-selection language is stripped"
            ),
        )

    if historical_pass_traceability_sweep_complete():
        require(
            REFORM_R5_S5_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R5-S5 must not remain the next seam once preserved "
                "branch trace is indexed and the historical pass traceability sweep is complete"
            ),
        )
        require(
            REFORM_R5_S5_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R5-S5 must not remain the next seam once preserved "
                "branch trace is indexed and the historical pass traceability sweep is complete"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R5_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R5-S5 once the historical pass "
                "traceability sweep is complete"
            ),
        )
        require(
            REFORM_R5_S5_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R5-S5 as the next active seam once the historical pass "
                "traceability sweep is complete"
            ),
        )
        require(
            active_seam_next != REFORM_R5_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R5-S5 once the historical pass "
                "traceability sweep is complete"
            ),
        )
        require(
            continuation_next_seam != REFORM_R5_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R5-S5 as `Next Active Seam` once the "
                "historical pass traceability sweep is complete"
            ),
        )

    if roadmap_anchor_conversion_complete():
        require(
            REFORM_R6_S1_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R6-S1 must not remain the next seam once the roadmap "
                "anchor conversion is complete"
            ),
        )
        require(
            REFORM_R6_S1_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R6-S1 must not remain the next seam once the roadmap "
                "anchor conversion is complete"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R6_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R6-S1 once the roadmap anchor conversion "
                "is complete"
            ),
        )
        require(
            REFORM_R6_S1_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R6-S1 as the next active seam once the roadmap anchor "
                "conversion is complete"
            ),
        )
        require(
            active_seam_next != REFORM_R6_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R6-S1 once the roadmap anchor "
                "conversion is complete"
            ),
        )
        require(
            continuation_next_seam != REFORM_R6_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R6-S1 as `Next Active Seam` once the "
                "roadmap anchor conversion is complete"
            ),
        )

    if workstream_index_split_complete():
        require(
            REFORM_R6_S2_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R6-S2 must not remain the next seam once the "
                "canonical workstream index is split by family anchor and historical pass role"
            ),
        )
        require(
            REFORM_R6_S2_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R6-S2 must not remain the next seam once the "
                "canonical workstream index is split by family anchor and historical pass role"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R6_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R6-S2 once the canonical workstream "
                "index split is complete"
            ),
        )
        require(
            REFORM_R6_S2_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R6-S2 as the next active seam once the canonical workstream "
                "index split is complete"
            ),
        )
        require(
            active_seam_next != REFORM_R6_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R6-S2 once the canonical workstream "
                "index split is complete"
            ),
        )
        require(
            continuation_next_seam != REFORM_R6_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R6-S2 as `Next Active Seam` once the "
                "canonical workstream index split is complete"
            ),
        )

    if main_router_loader_aligned():
        require(
            REFORM_R6_S3_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R6-S3 must not remain the next seam once Main/router/"
                "loader alignment is complete"
            ),
        )
        require(
            REFORM_R6_S3_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R6-S3 must not remain the next seam once Main/router/"
                "loader alignment is complete"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R6_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R6-S3 once Main/router/loader alignment "
                "is complete"
            ),
        )
        require(
            REFORM_R6_S3_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R6-S3 as the next active seam once Main/router/loader "
                "alignment is complete"
            ),
        )
        require(
            active_seam_next != REFORM_R6_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R6-S3 once Main/router/loader "
                "alignment is complete"
            ),
        )
        require(
            continuation_next_seam != REFORM_R6_S3_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R6-S3 as `Next Active Seam` once "
                "Main/router/loader alignment is complete"
            ),
        )

    if selected_next_truth_validated():
        require(
            REFORM_R6_S4_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R6-S4 must not remain the next seam once selected-next "
                "truth is validated across the family-governance surfaces"
            ),
        )
        require(
            REFORM_R6_S4_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R6-S4 must not remain the next seam once selected-next "
                "truth is validated across the family-governance surfaces"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R6_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R6-S4 once selected-next truth is validated"
            ),
        )
        require(
            REFORM_R6_S4_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R6-S4 as the next active seam once selected-next truth is validated"
            ),
        )
        require(
            active_seam_next != REFORM_R6_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R6-S4 once selected-next truth is validated"
            ),
        )
        require(
            continuation_next_seam != REFORM_R6_S4_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R6-S4 as `Next Active Seam` once "
                "selected-next truth is validated"
            ),
        )

    if phase6_drift_sweep_clean():
        require(
            REFORM_R6_S5_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R6-S5 must not remain the next seam once the final "
                "Phase 6 drift sweep is clean"
            ),
        )
        require(
            REFORM_R6_S5_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R6-S5 must not remain the next seam once the final "
                "Phase 6 drift sweep is clean"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R6_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R6-S5 once the final Phase 6 drift sweep "
                "is clean"
            ),
        )

    if temporary_dual_shape_tolerance_removed():
        require(
            REFORM_R7_S1_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R7-S1 must not remain the next seam once temporary "
                "dual-shape tolerance is removed"
            ),
        )

    require(
        selected_next_truth_validated(),
        (
            "Docs/feature_backlog.md / Docs/prebeta_roadmap.md / "
            "Docs/branch_records/feature_backlog_family_governance_reform.md: reform hard anti-"
            "drift requires selected-next truth to remain validated across backlog, roadmap, "
            "branch authority, and validator expectations"
        ),
    )
    require(
        phase6_drift_sweep_clean(),
        (
            "Docs/Main.md / Docs/workstreams/index.md / Docs/feature_backlog.md: reform hard anti-"
            "drift requires the sweep-clean Phase 6 family-governance routing surfaces to remain "
            "intact"
        ),
    )
    require(
        temporary_dual_shape_tolerance_removed(),
        (
            "dev/orin_branch_governance_validation.py: reform hard anti-drift requires temporary "
            "dual-shape tolerance to stay removed"
        ),
    )
    for entry in backlog_entries:
        registry_class = _clean_release_value(_extract_colon_value(entry["block"], "Registry Class"))
        status_value = _clean_release_value(_extract_colon_value(entry["block"], "Status"))
        next_workstream_value = _clean_release_value(
            _extract_colon_value(entry["block"], "Next Workstream")
        )
        branch_value = _clean_release_value(_extract_colon_value(entry["block"], "Branch"))
        if registry_class == "Historical Pass Alias":
            require(
                status_value.casefold() != "selected next"
                and next_workstream_value.casefold() != "selected"
                and branch_value.casefold() != "not created",
                (
                    f"Docs/feature_backlog.md: reform hard anti-drift: historical pass alias "
                    f"{entry['id']} must not regain live selected-next or branch-not-created markers"
                ),
            )
        if registry_class == "Support Lane":
            require(
                status_value.casefold() != "selected next"
                and next_workstream_value.casefold() != "selected"
                and branch_value.casefold() != "not created",
                (
                    f"Docs/feature_backlog.md: reform hard anti-drift: support lane {entry['id']} "
                    "must not regain live selected-next or branch-not-created markers"
                ),
            )

    if hard_anti_drift_checks_enforced():
        require(
            REFORM_R7_S2_STATE_NEXT_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: R7-S2 must not remain the next seam once hard anti-"
                "drift checks are enforced"
            ),
        )

    if (
        REFORM_HARDENING_H1_STATE_PHRASE in backlog_workstream_state
        and REFORM_HARDENING_H1_STATE_PHRASE in roadmap_workstream_state
    ):
        require(
            current_phase == "Hardening",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Current Phase "
                "must transition to `Hardening` once the reform branch current-state summaries "
                "declare Hardening H1 in progress"
            ),
        )
        require(
            next_legal_phase == "Live Validation",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Next Legal Phase "
                "must advance to `Live Validation` once the branch has transitioned into Hardening"
            ),
        )
        require(
            backlog_next_legal_phase == "Live Validation",
            (
                "Docs/feature_backlog.md: Next Legal Phase must advance to `Live Validation` "
                "once the reform branch current-state summary declares Hardening H1 in progress"
            ),
        )
        require(
            roadmap_next_legal_phase == "Live Validation",
            (
                "Docs/prebeta_roadmap.md: Next Legal Phase must advance to `Live Validation` "
                "once the reform branch current-state summary declares Hardening H1 in progress"
            ),
        )
        require(
            phase_status_hardening_seam == REFORM_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must name Hardening H1 as the current hardening seam during the phase handoff repair"
            ),
        )
        require(
            phase_status_next_seam == REFORM_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must point to Hardening H1 during the phase handoff repair"
            ),
        )
        require(
            active_seam_current == REFORM_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must name Hardening H1 as the current active seam during the phase handoff repair"
            ),
        )
        require(
            "Active seam: `None.`" not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must remove the stale `Active seam: None.` marker once Hardening H1 is admitted"
            ),
        )
        require(
            active_seam_next == REFORM_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must point to Hardening H1 during the phase handoff repair"
            ),
        )
        require(
            REFORM_R7_S2_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R7-S2 must not remain the next seam once hard anti-"
                "drift checks are enforced"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R7_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R7-S2 once hard anti-drift checks are enforced"
            ),
        )
        require(
            REFORM_R7_S2_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R7-S2 as the next active seam once hard anti-drift checks are enforced"
            ),
        )
        require(
            continuation_next_seam != REFORM_R7_S2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R7-S2 as `Next Active Seam` once hard anti-"
                "drift checks are enforced"
            ),
        )
        require(
            REFORM_R7_S2_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R7-S2 continuation action once hard anti-"
                "drift checks are enforced"
            ),
        )
        require(
            REFORM_R7_S1_STATE_NEXT_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: R7-S1 must not remain the next seam once temporary "
                "dual-shape tolerance is removed"
            ),
        )
        require(
            phase_status_next_seam != REFORM_R7_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must advance past R7-S1 once temporary dual-shape tolerance "
                "is removed"
            ),
        )
        require(
            REFORM_R7_S1_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R7-S1 as the next active seam once temporary dual-shape tolerance "
                "is removed"
            ),
        )
        require(
            active_seam_next != REFORM_R7_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R7-S1 once temporary dual-shape tolerance "
                "is removed"
            ),
        )

    if (
        REFORM_LIVE_VALIDATION_LV1_STATE_PHRASE in backlog_workstream_state
        and REFORM_LIVE_VALIDATION_LV1_STATE_PHRASE in roadmap_workstream_state
    ):
        require(
            current_phase == "Live Validation",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Current Phase "
                "must transition to `Live Validation` once the reform branch current-state summaries "
                "declare Live Validation LV1 in progress"
            ),
        )
        require(
            next_legal_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Next Legal Phase "
                "must advance to `PR Readiness` once the branch has transitioned into Live Validation"
            ),
        )
        require(
            backlog_next_legal_phase == "PR Readiness",
            (
                "Docs/feature_backlog.md: Next Legal Phase must advance to `PR Readiness` "
                "once the reform branch current-state summary declares Live Validation LV1 in progress"
            ),
        )
        require(
            roadmap_next_legal_phase == "PR Readiness",
            (
                "Docs/prebeta_roadmap.md: Next Legal Phase must advance to `PR Readiness` "
                "once the reform branch current-state summary declares Live Validation LV1 in progress"
            ),
        )
        require(
            phase_status_hardening_seam != REFORM_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must stop naming Hardening H1 as the current seam once Live Validation LV1 is admitted"
            ),
        )
        require(
            phase_status_live_validation_seam == REFORM_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must name Live Validation LV1 as the current live-validation seam during the phase admission repair"
            ),
        )
        require(
            phase_status_next_seam == REFORM_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must point to Live Validation LV1 during the phase admission repair"
            ),
        )
        require(
            active_seam_current == REFORM_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must name Live Validation LV1 as the current active seam during the phase admission repair"
            ),
        )
        require(
            active_seam_next == REFORM_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must point to Live Validation LV1 during the phase admission repair"
            ),
        )
        require(
            continuation_next_seam == REFORM_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must point to Live Validation LV1 once the branch enters "
                "Live Validation"
            ),
        )
        require(
            REFORM_HARDENING_H1_STATE_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: Current Workstream State must stop reporting Hardening H1 "
                "as in progress once Live Validation LV1 is admitted"
            ),
        )
        require(
            REFORM_HARDENING_H1_STATE_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: Current Workstream State must stop reporting Hardening H1 "
                "as in progress once Live Validation LV1 is admitted"
            ),
        )

    if (
        REFORM_PR_READINESS_PR1_STATE_PHRASE in backlog_workstream_state
        and REFORM_PR_READINESS_PR1_STATE_PHRASE in roadmap_workstream_state
    ):
        require(
            current_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Current Phase "
                "must transition to `PR Readiness` once the reform branch current-state summaries "
                "declare PR Readiness PR1 in progress"
            ),
        )
        require(
            next_legal_phase == "Release Readiness",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Next Legal Phase "
                "must advance to `Release Readiness` once the branch has transitioned into PR Readiness"
            ),
        )
        require(
            backlog_next_legal_phase == "Release Readiness",
            (
                "Docs/feature_backlog.md: Next Legal Phase must advance to `Release Readiness` "
                "once the reform branch current-state summary declares PR Readiness PR1 in progress"
            ),
        )
        require(
            roadmap_next_legal_phase == "Release Readiness",
            (
                "Docs/prebeta_roadmap.md: Next Legal Phase must advance to `Release Readiness` "
                "once the reform branch current-state summary declares PR Readiness PR1 in progress"
            ),
        )
        require(
            phase_status_live_validation_seam != REFORM_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must stop naming Live Validation LV1 as the current seam once PR Readiness PR1 is admitted"
            ),
        )
        require(
            phase_status_pr_readiness_seam == REFORM_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must name PR Readiness PR1 as the current PR-readiness seam during the phase admission repair"
            ),
        )
        require(
            phase_status_next_seam == REFORM_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must point to PR Readiness PR1 during the phase admission repair"
            ),
        )
        require(
            active_seam_current == REFORM_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must name PR Readiness PR1 as the current active seam during the phase admission repair"
            ),
        )
        require(
            active_seam_next == REFORM_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must point to PR Readiness PR1 during the phase admission repair"
            ),
        )
        require(
            continuation_next_seam == REFORM_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must point to PR Readiness PR1 once the branch enters PR Readiness"
            ),
        )
        require(
            REFORM_LIVE_VALIDATION_LV1_STATE_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: Current Workstream State must stop reporting Live Validation LV1 "
                "as in progress once PR Readiness PR1 is admitted"
            ),
        )
        require(
            REFORM_LIVE_VALIDATION_LV1_STATE_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: Current Workstream State must stop reporting Live Validation LV1 "
                "as in progress once PR Readiness PR1 is admitted"
            ),
        )
        require(
            continuation_next_seam != REFORM_R7_S1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R7-S1 as `Next Active Seam` once temporary "
                "dual-shape tolerance is removed"
            ),
        )
        require(
            REFORM_R7_S1_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R7-S1 continuation action once temporary "
                "dual-shape tolerance is removed"
            ),
        )

    if (
        REFORM_PR_READINESS_PR2_STATE_PHRASE in backlog_workstream_state
        and REFORM_PR_READINESS_PR2_STATE_PHRASE in roadmap_workstream_state
    ):
        require(
            current_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Current Phase "
                "must return to `PR Readiness` once the reform branch current-state summaries "
                "declare PR Readiness PR2 in progress"
            ),
        )
        require(
            next_legal_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Next Legal Phase "
                "must remain `PR Readiness` while PR Readiness PR2 is blocked on a fresh bot-review signal"
            ),
        )
        require(
            backlog_next_legal_phase == "PR Readiness",
            (
                "Docs/feature_backlog.md: Next Legal Phase must remain `PR Readiness` while the "
                "reform branch current-state summary declares PR Readiness PR2 in progress"
            ),
        )
        require(
            roadmap_next_legal_phase == "PR Readiness",
            (
                "Docs/prebeta_roadmap.md: Next Legal Phase must remain `PR Readiness` while the "
                "reform branch current-state summary declares PR Readiness PR2 in progress"
            ),
        )
        require(
            phase_status_pr_readiness_seam == REFORM_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must name PR Readiness PR2 as the current PR-readiness seam during bot-review monitoring"
            ),
        )
        require(
            phase_status_next_seam == REFORM_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must point to PR Readiness PR2 during bot-review monitoring"
            ),
        )
        require(
            active_seam_current == REFORM_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must name PR Readiness PR2 as the current active seam during bot-review monitoring"
            ),
        )
        require(
            active_seam_next == REFORM_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must point to PR Readiness PR2 during bot-review monitoring"
            ),
        )
        require(
            continuation_next_seam == REFORM_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must point to PR Readiness PR2 while the fresh bot-review signal is pending"
            ),
        )
        require(
            phase_status_release_readiness_seam != REFORM_RELEASE_READINESS_RR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must stop naming Release Readiness RR1 as the current seam once the branch returns "
                "to PR Readiness PR2"
            ),
        )
        require(
            REFORM_RELEASE_READINESS_RR1_STATE_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: Current Workstream State must stop reporting Release "
                "Readiness RR1 as in progress once the branch returns to PR Readiness PR2"
            ),
        )
        require(
            REFORM_RELEASE_READINESS_RR1_STATE_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: Current Workstream State must stop reporting Release "
                "Readiness RR1 as in progress once the branch returns to PR Readiness PR2"
            ),
        )

    if (
        REFORM_RELEASE_READINESS_RR1_STATE_PHRASE in backlog_workstream_state
        and REFORM_RELEASE_READINESS_RR1_STATE_PHRASE in roadmap_workstream_state
    ):
        require(
            current_phase == "Release Readiness",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Current Phase "
                "must transition to `Release Readiness` once the reform branch current-state "
                "summaries declare Release Readiness RR1 in progress"
            ),
        )
        require(
            next_legal_phase == "Release Readiness",
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Next Legal Phase "
                "must remain `Release Readiness` while the reform branch is inside active RR1 "
                "file-frozen validation"
            ),
        )
        require(
            backlog_next_legal_phase == "Release Readiness",
            (
                "Docs/feature_backlog.md: Next Legal Phase must remain `Release Readiness` "
                "while the reform branch current-state summary declares Release Readiness RR1 in progress"
            ),
        )
        require(
            roadmap_next_legal_phase == "Release Readiness",
            (
                "Docs/prebeta_roadmap.md: Next Legal Phase must remain `Release Readiness` "
                "while the reform branch current-state summary declares Release Readiness RR1 in progress"
            ),
        )
        require(
            phase_status_pr_readiness_seam != REFORM_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must stop naming PR Readiness PR1 as the current seam once Release Readiness RR1 is admitted"
            ),
        )
        require(
            phase_status_release_readiness_seam == REFORM_RELEASE_READINESS_RR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "must name Release Readiness RR1 as the current release-readiness seam during the phase admission repair"
            ),
        )
        require(
            phase_status_next_seam == REFORM_RELEASE_READINESS_RR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Phase Status "
                "`Next Active Seam` must point to Release Readiness RR1 during the phase admission repair"
            ),
        )
        require(
            active_seam_current == REFORM_RELEASE_READINESS_RR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must name Release Readiness RR1 as the current active seam during the phase admission repair"
            ),
        )
        require(
            active_seam_next == REFORM_RELEASE_READINESS_RR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must point to Release Readiness RR1 during the phase admission repair"
            ),
        )
        require(
            continuation_next_seam == REFORM_RELEASE_READINESS_RR1_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must point to Release Readiness RR1 once the branch enters Release Readiness"
            ),
        )
        require(
            REFORM_PR_READINESS_PR1_STATE_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: Current Workstream State must stop reporting PR Readiness PR1 "
                "as in progress once Release Readiness RR1 is admitted"
            ),
        )
        require(
            REFORM_PR_READINESS_PR1_STATE_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: Current Workstream State must stop reporting PR Readiness PR1 "
                "as in progress once Release Readiness RR1 is admitted"
            ),
        )
        require(
            REFORM_R6_S5_ACTIVE_SEAM_NEXT_PHRASE not in active_seam_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "must not keep R6-S5 as the next active seam once the final Phase 6 drift sweep "
                "is clean"
            ),
        )
        require(
            active_seam_next != REFORM_R6_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Active Seam "
                "`Next active seam` must advance past R6-S5 once the final Phase 6 drift sweep "
                "is clean"
            ),
        )
        require(
            continuation_next_seam != REFORM_R6_S5_SEAM,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep R6-S5 as `Next Active Seam` once the final "
                "Phase 6 drift sweep is clean"
            ),
        )
        require(
            REFORM_R6_S5_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R6-S5 continuation action once the final "
                "Phase 6 drift sweep is clean"
            ),
        )
        require(
            REFORM_R6_S4_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R6-S4 continuation action once "
                "selected-next truth is validated"
            ),
        )
        require(
            REFORM_R6_S3_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R6-S3 continuation action once "
                "Main/router/loader alignment is complete"
            ),
        )
        require(
            REFORM_R6_S2_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R6-S2 continuation action once the "
                "canonical workstream index split is complete"
            ),
        )
        require(
            REFORM_R6_S1_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R6-S1 continuation action once the "
                "roadmap anchor conversion is complete"
            ),
        )
        require(
            REFORM_R5_S5_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R5-S5 continuation action once the "
                "historical pass traceability sweep is complete"
            ),
        )
        require(
            REFORM_R5_S4_CONTINUATION_PHRASE not in continuation_section,
            (
                "Docs/branch_records/feature_backlog_family_governance_reform.md: Seam "
                "Continuation Decision must not keep an R5-S4 continuation action once "
                "historical alias future-selection language is stripped"
            ),
        )

    if (
        continuation_completion_status.strip().casefold() == "in progress"
        and continuation_decision.strip().casefold() == "continue"
    ):
        for source_name, current_state in (
            ("Docs/feature_backlog.md", backlog_workstream_state),
            ("Docs/prebeta_roadmap.md", roadmap_workstream_state),
        ):
            require(
                "in progress and green" not in current_state.casefold(),
                (
                    f"{source_name}: Current Workstream State must not report green while "
                    "the reform branch continuation record still has `Slice Status: In Progress`"
                ),
            )
            require(
                "completion status: in progress" in current_state.casefold(),
                (
                    f"{source_name}: Current Workstream State must report "
                    "`Completion Status: In Progress` while reform continuation remains active"
                ),
            )
            require(
                "continue decision: continue" in current_state.casefold(),
                (
                    f"{source_name}: Current Workstream State must report "
                    "`Continue Decision: Continue` while reform continuation remains active"
                ),
            )
            require(
                "next when instructed" not in current_state.casefold(),
                (
                    f"{source_name}: Current Workstream State must not await instruction while "
                    "the reform branch continuation record still requires continuation"
                ),
            )
            require(
                "slice green" not in current_state.casefold(),
                (
                    f"{source_name}: Current Workstream State must not report slice-green stop "
                    "authority while reform continuation remains active"
                ),
            )


def _validate_automation_planning_phase_truth(
    require,
    *,
    current_branch: str,
    backlog_text: str,
    roadmap_text: str,
) -> None:
    if not _is_automation_planning_branch(current_branch):
        return

    branch_record_text = _read_text(AUTOMATION_PLANNING_BRANCH_RECORD)
    backlog_workstream_state = _extract_colon_value(backlog_text, "Current Workstream State")
    roadmap_workstream_state = _extract_colon_value(roadmap_text, "Current Workstream State")
    phase_status_section = _section(branch_record_text, "Phase Status")
    active_seam_section = _section(branch_record_text, "Active Seam")
    continuation_section = _section(branch_record_text, "Seam Continuation Decision")
    phase_status_next_seam = _extract_marker_value(phase_status_section, "Next Active Seam")
    continuation_next_seam = _extract_marker_value(continuation_section, "Next Active Seam")
    active_seam_match = re.search(r"^Next active seam:\s*`([^`]+)`", active_seam_section, flags=re.M)
    active_seam_next = active_seam_match.group(1).strip() if active_seam_match else ""
    active_seam_current = _extract_marker_value(active_seam_section, "Active seam")
    current_phase = _extract_marker_value(_section(branch_record_text, "Current Phase"), "Phase")
    next_legal_phase = _extract_first_backtick_value(_section(branch_record_text, "Next Legal Phase"))
    phase_status_hardening_seam = _extract_marker_value(phase_status_section, "Current Hardening Seam")
    phase_status_live_validation_seam = _extract_marker_value(
        phase_status_section, "Current Live Validation Seam"
    )
    phase_status_pr_readiness_seam = _extract_marker_value(
        phase_status_section, "Current PR Readiness Seam"
    )
    backlog_next_legal_phase = _extract_colon_value(backlog_text, "Next Legal Phase").rstrip(".")
    roadmap_next_legal_phase = _extract_colon_value(roadmap_text, "Next Legal Phase").rstrip(".")

    if (
        AUTOMATION_HARDENING_H1_STATE_PHRASE in backlog_workstream_state
        and AUTOMATION_HARDENING_H1_STATE_PHRASE in roadmap_workstream_state
    ):
        require(
            current_phase == "Hardening",
            (
                "Docs/branch_records/feature_automation_planning.md: Current Phase must "
                "transition to `Hardening` once the automation-planning branch current-state "
                "summaries declare Hardening H1 in progress"
            ),
        )
        require(
            next_legal_phase == "Live Validation",
            (
                "Docs/branch_records/feature_automation_planning.md: Next Legal Phase must "
                "advance to `Live Validation` once the branch has transitioned into Hardening"
            ),
        )
        require(
            backlog_next_legal_phase == "Live Validation",
            (
                "Docs/feature_backlog.md: Next Legal Phase must advance to `Live Validation` "
                "once the automation-planning branch current-state summary declares Hardening "
                "H1 in progress"
            ),
        )
        require(
            roadmap_next_legal_phase == "Live Validation",
            (
                "Docs/prebeta_roadmap.md: Next Legal Phase must advance to `Live Validation` "
                "once the automation-planning branch current-state summary declares Hardening "
                "H1 in progress"
            ),
        )
        require(
            phase_status_hardening_seam == AUTOMATION_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Phase Status must name "
                "Hardening H1 as the current hardening seam during the phase-admission repair"
            ),
        )
        require(
            phase_status_next_seam == AUTOMATION_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Phase Status `Next Active "
                "Seam` must point to Hardening H1 during the phase-admission repair"
            ),
        )
        require(
            active_seam_current == AUTOMATION_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Active Seam must name "
                "Hardening H1 as the current active seam during the phase-admission repair"
            ),
        )
        require(
            "Active seam: `None.`" not in active_seam_section,
            (
                "Docs/branch_records/feature_automation_planning.md: Active Seam must remove "
                "the stale `Active seam: None.` marker once Hardening H1 is admitted"
            ),
        )
        require(
            active_seam_next == AUTOMATION_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Active Seam `Next active "
                "seam` must point to Hardening H1 during the phase-admission repair"
            ),
        )

    if (
        AUTOMATION_LIVE_VALIDATION_LV1_STATE_PHRASE in backlog_workstream_state
        and AUTOMATION_LIVE_VALIDATION_LV1_STATE_PHRASE in roadmap_workstream_state
    ):
        require(
            current_phase == "Live Validation",
            (
                "Docs/branch_records/feature_automation_planning.md: Current Phase must "
                "transition to `Live Validation` once the automation-planning branch current-state "
                "summaries declare Live Validation LV1 in progress"
            ),
        )
        require(
            next_legal_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_automation_planning.md: Next Legal Phase must "
                "advance to `PR Readiness` once the branch has transitioned into Live Validation"
            ),
        )
        require(
            backlog_next_legal_phase == "PR Readiness",
            (
                "Docs/feature_backlog.md: Next Legal Phase must advance to `PR Readiness` "
                "once the automation-planning branch current-state summary declares Live Validation "
                "LV1 in progress"
            ),
        )
        require(
            roadmap_next_legal_phase == "PR Readiness",
            (
                "Docs/prebeta_roadmap.md: Next Legal Phase must advance to `PR Readiness` "
                "once the automation-planning branch current-state summary declares Live Validation "
                "LV1 in progress"
            ),
        )
        require(
            phase_status_hardening_seam != AUTOMATION_HARDENING_H1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Phase Status must stop "
                "naming Hardening H1 as the current seam once Live Validation LV1 is admitted"
            ),
        )
        require(
            phase_status_live_validation_seam == AUTOMATION_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Phase Status must name "
                "Live Validation LV1 as the current live-validation seam during the phase "
                "admission repair"
            ),
        )
        require(
            phase_status_next_seam == AUTOMATION_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Phase Status `Next Active "
                "Seam` must point to Live Validation LV1 during the phase admission repair"
            ),
        )
        require(
            active_seam_current == AUTOMATION_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Active Seam must name "
                "Live Validation LV1 as the current active seam during the phase admission repair"
            ),
        )
        require(
            active_seam_next == AUTOMATION_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Active Seam `Next active "
                "seam` must point to Live Validation LV1 during the phase admission repair"
            ),
        )
        require(
            continuation_next_seam == AUTOMATION_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Seam Continuation Decision "
                "must point to Live Validation LV1 once the branch enters Live Validation"
            ),
        )
        require(
            AUTOMATION_HARDENING_H1_STATE_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: Current Workstream State must stop reporting Hardening "
                "H1 as in progress once Live Validation LV1 is admitted"
            ),
        )
        require(
            AUTOMATION_HARDENING_H1_STATE_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: Current Workstream State must stop reporting Hardening "
                "H1 as in progress once Live Validation LV1 is admitted"
            ),
        )

    if (
        AUTOMATION_PR_READINESS_PR1_STATE_PHRASE in backlog_workstream_state
        and AUTOMATION_PR_READINESS_PR1_STATE_PHRASE in roadmap_workstream_state
    ):
        require(
            current_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_automation_planning.md: Current Phase must "
                "transition to `PR Readiness` once the automation-planning branch current-state "
                "summaries declare PR Readiness PR1 in progress"
            ),
        )
        require(
            next_legal_phase == "Release Readiness",
            (
                "Docs/branch_records/feature_automation_planning.md: Next Legal Phase must "
                "advance to `Release Readiness` once the branch has transitioned into PR Readiness"
            ),
        )
        require(
            backlog_next_legal_phase == "Release Readiness",
            (
                "Docs/feature_backlog.md: Next Legal Phase must advance to `Release Readiness` "
                "once the automation-planning branch current-state summary declares PR Readiness "
                "PR1 in progress"
            ),
        )
        require(
            roadmap_next_legal_phase == "Release Readiness",
            (
                "Docs/prebeta_roadmap.md: Next Legal Phase must advance to `Release Readiness` "
                "once the automation-planning branch current-state summary declares PR Readiness "
                "PR1 in progress"
            ),
        )
        require(
            phase_status_live_validation_seam != AUTOMATION_LIVE_VALIDATION_LV1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Phase Status must stop "
                "naming Live Validation LV1 as the current seam once PR Readiness PR1 is admitted"
            ),
        )
        require(
            phase_status_pr_readiness_seam == AUTOMATION_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Phase Status must name "
                "PR Readiness PR1 as the current PR-readiness seam during the phase admission repair"
            ),
        )
        require(
            phase_status_next_seam == AUTOMATION_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Phase Status `Next Active "
                "Seam` must point to PR Readiness PR1 during the phase admission repair"
            ),
        )
        require(
            active_seam_current == AUTOMATION_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Active Seam must name "
                "PR Readiness PR1 as the current active seam during the phase admission repair"
            ),
        )
        require(
            active_seam_next == AUTOMATION_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Active Seam `Next active "
                "seam` must point to PR Readiness PR1 during the phase admission repair"
            ),
        )
        require(
            continuation_next_seam == AUTOMATION_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_automation_planning.md: Seam Continuation Decision "
                "must point to PR Readiness PR1 once the branch enters PR Readiness"
            ),
        )
        require(
            AUTOMATION_LIVE_VALIDATION_LV1_STATE_PHRASE not in backlog_workstream_state,
            (
                "Docs/feature_backlog.md: Current Workstream State must stop reporting Live "
                "Validation LV1 as in progress once PR Readiness PR1 is admitted"
            ),
        )
        require(
            AUTOMATION_LIVE_VALIDATION_LV1_STATE_PHRASE not in roadmap_workstream_state,
            (
                "Docs/prebeta_roadmap.md: Current Workstream State must stop reporting Live "
                "Validation LV1 as in progress once PR Readiness PR1 is admitted"
            ),
        )


def _validate_automation_planning_runtime_truth(
    require,
    *,
    current_branch: str,
    backlog_text: str,
    roadmap_text: str,
) -> None:
    if not _is_automation_planning_branch(current_branch):
        return

    branch_record_text = _read_text(AUTOMATION_PLANNING_BRANCH_RECORD)

    for required_phrase in AUTOMATION_PLANNING_RUNTIME_PROOF_REQUIRED_PHRASES:
        require(
            required_phrase in branch_record_text,
            (
                "Docs/branch_records/feature_automation_planning.md: automation runtime-proof "
                f"contract is missing '{required_phrase}'"
            ),
        )

    for source_name, source_text in (
        ("Docs/feature_backlog.md", backlog_text),
        ("Docs/prebeta_roadmap.md", roadmap_text),
    ):
        require(
            "pr-heartbeat-watcher" not in source_text,
            (
                f"{source_name}: current-state automation summary must not regress to the retired "
                "`pr-heartbeat-watcher` id"
            ),
        )


def _validate_automation_closeout_repair_phase_truth(
    require,
    *,
    current_branch: str,
) -> None:
    if not _is_automation_closeout_repair_branch(current_branch):
        return

    branch_record_text = _read_text(AUTOMATION_CLOSEOUT_REPAIR_BRANCH_RECORD)
    current_phase = _extract_marker_value(_section(branch_record_text, "Current Phase"), "Phase")
    next_legal_phase = _extract_first_backtick_value(_section(branch_record_text, "Next Legal Phase"))
    phase_status_section = _section(branch_record_text, "Phase Status")
    active_seam_section = _section(branch_record_text, "Active Seam")
    continuation_section = _section(branch_record_text, "Seam Continuation Decision")
    release_window_section = _section(branch_record_text, "Release Window Audit")
    seam_status = _extract_marker_value(continuation_section, "Seam Status")
    phase_status_pr_readiness_seam = _extract_marker_value(
        phase_status_section, "Current PR Readiness Seam"
    )
    phase_status_next_seam = _extract_marker_value(phase_status_section, "Next Active Seam")
    active_seam_current = _extract_marker_value(active_seam_section, "Active seam")
    active_seam_match = re.search(r"^Next active seam:\s*`([^`]+)`", active_seam_section, flags=re.M)
    active_seam_next = active_seam_match.group(1).strip() if active_seam_match else ""
    continuation_next_seam = _extract_marker_value(continuation_section, "Next Active Seam")

    if current_phase == "PR Readiness":
        require(
            next_legal_phase == "Release Readiness",
            (
                "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md: "
                "Next Legal Phase must advance to `Release Readiness` once the branch enters "
                "`PR Readiness`"
            ),
        )
        require(
            phase_status_pr_readiness_seam == AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md: "
                "Phase Status must name PR Readiness PR2 as the current PR-readiness seam "
                "once merge-watch governance is admitted"
            ),
        )
        require(
            phase_status_next_seam == AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md: "
                "Phase Status `Next Active Seam` must point to PR Readiness PR2 during the "
                "merge-verification watch"
            ),
        )
        require(
            active_seam_current == AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md: "
                "Active Seam must name PR Readiness PR2 as the current active seam"
            ),
        )
        require(
            active_seam_next == AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md: "
                "Active Seam `Next active seam` must point to PR Readiness PR2"
            ),
        )
        require(
            continuation_next_seam == AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md: "
                "Seam Continuation Decision must point to PR Readiness PR2 while merge "
                "verification is pending"
            ),
        )
        require(
            "Release Window Audit: PASS" in release_window_section,
            (
                "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md: "
                "PR Readiness truth must include `Release Window Audit: PASS`"
            ),
        )
        blockers_section = _section(branch_record_text, "Blockers")
        require(
            "PR Merge Verification Pending" in blockers_section,
            (
                "Docs/branch_records/feature_automation_planning_post_merge_closeout_repair.md: "
                "PR Readiness PR2 must carry `PR Merge Verification Pending` until merge is verified"
            ),
        )


def _validate_pr101_closeout_canon_repair_phase_truth(
    require,
    *,
    current_branch: str,
) -> None:
    if not _is_pr101_closeout_canon_repair_branch(current_branch):
        return

    branch_record_text = _read_text(PR101_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD)
    current_phase = _extract_marker_value(_section(branch_record_text, "Current Phase"), "Phase")
    next_legal_phase = _extract_first_backtick_value(_section(branch_record_text, "Next Legal Phase"))
    phase_status_section = _section(branch_record_text, "Phase Status")
    active_seam_section = _section(branch_record_text, "Active Seam")
    continuation_section = _section(branch_record_text, "Seam Continuation Decision")
    release_window_section = _section(branch_record_text, "Release Window Audit")
    phase_status_pr_readiness_seam = _extract_marker_value(
        phase_status_section, "Current PR Readiness Seam"
    )
    phase_status_next_seam = _extract_marker_value(phase_status_section, "Next Active Seam")
    active_seam_current = _extract_marker_value(active_seam_section, "Active seam")
    active_seam_match = re.search(r"^Next active seam:\s*`([^`]+)`", active_seam_section, flags=re.M)
    active_seam_next = active_seam_match.group(1).strip() if active_seam_match else ""
    continuation_next_seam = _extract_marker_value(continuation_section, "Next Active Seam")
    blockers_section = _section(branch_record_text, "Blockers")

    if current_phase != "PR Readiness":
        return

    if phase_status_pr_readiness_seam == PR101_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM:
        require(
            next_legal_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Next Legal Phase must remain `PR Readiness` while PR Readiness PR1 is active "
                "and PR2 merge-verification has not yet been admitted"
            ),
        )
        require(
            phase_status_next_seam == PR101_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Phase Status `Next Active Seam` must point to PR Readiness PR1 during PR1 "
                "admission and live PR creation"
            ),
        )
        require(
            active_seam_current == PR101_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Active Seam must name PR Readiness PR1 as the current active seam"
            ),
        )
        require(
            active_seam_next == PR101_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Active Seam `Next active seam` must point to PR Readiness PR1 while PR1 is active"
            ),
        )
        require(
            continuation_next_seam == PR101_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Seam Continuation Decision must point to PR Readiness PR1 while PR1 blockers "
                "are active"
            ),
        )
        require(
            "Release Window Audit: PASS" in release_window_section,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "PR Readiness truth must include `Release Window Audit: PASS`"
            ),
        )
    elif phase_status_pr_readiness_seam == PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM:
        require(
            next_legal_phase == "Release Readiness",
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Next Legal Phase must advance to `Release Readiness` once PR Readiness PR2 is active"
            ),
        )
        require(
            phase_status_next_seam == PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Phase Status `Next Active Seam` must point to PR Readiness PR2 during merge watch"
            ),
        )
        require(
            active_seam_current == PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Active Seam must name PR Readiness PR2 as the current active seam"
            ),
        )
        require(
            active_seam_next == PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Active Seam `Next active seam` must point to PR Readiness PR2"
            ),
        )
        require(
            continuation_next_seam == PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Seam Continuation Decision must point to PR Readiness PR2 while merge "
                "verification is pending"
            ),
        )
        require(
            "Release Window Audit: PASS" in release_window_section,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "PR Readiness truth must include `Release Window Audit: PASS`"
            ),
        )
        require(
            "PR Merge Verification Pending" in blockers_section,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "PR Readiness PR2 must carry `PR Merge Verification Pending` until merge is verified"
            ),
        )
    else:
        require(
            False,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "Current PR Readiness Seam must be exactly "
                f"`{PR101_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM}` or "
                f"`{PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM}` while Phase is `PR Readiness`"
            ),
        )


def _validate_pr102_closeout_canon_repair_phase_truth(
    require,
    *,
    current_branch: str,
) -> None:
    if not _is_pr102_closeout_canon_repair_branch(current_branch):
        return

    branch_record_text = _read_text(PR102_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD)
    current_phase = _extract_marker_value(_section(branch_record_text, "Current Phase"), "Phase")
    next_legal_phase = _extract_first_backtick_value(_section(branch_record_text, "Next Legal Phase"))
    phase_status_section = _section(branch_record_text, "Phase Status")
    active_seam_section = _section(branch_record_text, "Active Seam")
    continuation_section = _section(branch_record_text, "Seam Continuation Decision")
    release_window_section = _section(branch_record_text, "Release Window Audit")
    phase_status_pr_readiness_seam = _extract_marker_value(
        phase_status_section, "Current PR Readiness Seam"
    )
    phase_status_next_seam = _extract_marker_value(phase_status_section, "Next Active Seam")
    active_seam_current = _extract_marker_value(active_seam_section, "Active seam")
    active_seam_match = re.search(r"^Next active seam:\s*`([^`]+)`", active_seam_section, flags=re.M)
    active_seam_next = active_seam_match.group(1).strip() if active_seam_match else ""
    continuation_next_seam = _extract_marker_value(continuation_section, "Next Active Seam")
    blockers_section = _section(branch_record_text, "Blockers")

    if current_phase != "PR Readiness":
        return

    for marker_name in (
        "PR watcher reporting surface",
        "PR watcher reporting thread ID",
        "PR watcher reporting transcript",
        "PR watcher route verification",
    ):
        require(
            bool(_extract_marker_value(phase_status_section, marker_name)),
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                f"Phase Status must record `{marker_name}` while PR watcher governance is active"
            ),
        )

    if phase_status_pr_readiness_seam == PR102_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM:
        require(
            next_legal_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Next Legal Phase must remain `PR Readiness` while PR Readiness PR1 is active "
                "and PR2 merge-verification has not yet been admitted"
            ),
        )
        require(
            phase_status_next_seam == PR102_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Phase Status `Next Active Seam` must point to PR Readiness PR1 during PR1 "
                "admission and live PR creation"
            ),
        )
        require(
            active_seam_current == PR102_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Active Seam must name PR Readiness PR1 as the current active seam"
            ),
        )
        require(
            active_seam_next == PR102_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Active Seam `Next active seam` must point to PR Readiness PR1 while PR1 is active"
            ),
        )
        require(
            continuation_next_seam == PR102_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Seam Continuation Decision must point to PR Readiness PR1 while PR1 blockers "
                "are active"
            ),
        )
        require(
            "Release Window Audit: PASS" in release_window_section,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "PR Readiness truth must include `Release Window Audit: PASS`"
            ),
        )
    elif phase_status_pr_readiness_seam == PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM:
        require(
            next_legal_phase == "Release Readiness",
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Next Legal Phase must advance to `Release Readiness` once PR Readiness PR2 is active"
            ),
        )
        require(
            phase_status_next_seam == PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Phase Status `Next Active Seam` must point to PR Readiness PR2 during merge watch"
            ),
        )
        require(
            active_seam_current == PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Active Seam must name PR Readiness PR2 as the current active seam"
            ),
        )
        require(
            active_seam_next == PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Active Seam `Next active seam` must point to PR Readiness PR2"
            ),
        )
        require(
            continuation_next_seam == PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Seam Continuation Decision must point to PR Readiness PR2 while merge "
                "verification is pending"
            ),
        )
        require(
            "Release Window Audit: PASS" in release_window_section,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "PR Readiness truth must include `Release Window Audit: PASS`"
            ),
        )
        require(
            "PR Merge Verification Pending" in blockers_section,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "PR Readiness PR2 must carry `PR Merge Verification Pending` until merge is verified"
            ),
        )
    else:
        require(
            False,
            (
                "Docs/branch_records/feature_pr102_post_merge_closeout_canon_repair.md: "
                "Current PR Readiness Seam must be exactly "
                f"`{PR102_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM}` or "
                f"`{PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM}` while Phase is `PR Readiness`"
            ),
        )


def _validate_pr103_closeout_canon_repair_phase_truth(
    require,
    *,
    current_branch: str,
) -> None:
    if not _is_pr103_closeout_canon_repair_branch(current_branch):
        return

    branch_record_text = _read_text(PR103_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD)
    current_phase = _extract_marker_value(_section(branch_record_text, "Current Phase"), "Phase")
    next_legal_phase = _extract_first_backtick_value(_section(branch_record_text, "Next Legal Phase"))
    phase_status_section = _section(branch_record_text, "Phase Status")
    active_seam_section = _section(branch_record_text, "Active Seam")
    continuation_section = _section(branch_record_text, "Seam Continuation Decision")
    release_window_section = _section(branch_record_text, "Release Window Audit")
    phase_status_pr_readiness_seam = _extract_marker_value(
        phase_status_section, "Current PR Readiness Seam"
    )
    phase_status_next_seam = _extract_marker_value(phase_status_section, "Next Active Seam")
    active_seam_current = _extract_marker_value(active_seam_section, "Active seam")
    active_seam_match = re.search(r"^Next active seam:\s*`([^`]+)`", active_seam_section, flags=re.M)
    active_seam_next = active_seam_match.group(1).strip() if active_seam_match else ""
    continuation_next_seam = _extract_marker_value(continuation_section, "Next Active Seam")
    blockers_section = _section(branch_record_text, "Blockers")

    if current_phase != "PR Readiness":
        return

    for marker_name in (
        "PR watcher reporting surface",
        "PR watcher reporting thread ID",
        "PR watcher reporting transcript",
        "PR watcher route verification",
    ):
        require(
            bool(_extract_marker_value(phase_status_section, marker_name)),
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                f"Phase Status must record `{marker_name}` while PR watcher governance is active"
            ),
        )

    if phase_status_pr_readiness_seam == PR103_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM:
        require(
            next_legal_phase == "PR Readiness",
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Next Legal Phase must remain `PR Readiness` while PR Readiness PR1 is active "
                "and PR2 merge-verification has not yet been admitted"
            ),
        )
        require(
            phase_status_next_seam == PR103_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Phase Status `Next Active Seam` must point to PR Readiness PR1 during PR1 "
                "admission and live PR creation"
            ),
        )
        require(
            active_seam_current == PR103_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Active Seam must name PR Readiness PR1 as the current active seam"
            ),
        )
        require(
            active_seam_next == PR103_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Active Seam `Next active seam` must point to PR Readiness PR1 while PR1 is active"
            ),
        )
        require(
            continuation_next_seam == PR103_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Seam Continuation Decision must point to PR Readiness PR1 while PR1 blockers "
                "are active"
            ),
        )
        require(
            "Release Window Audit: PASS" in release_window_section,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "PR Readiness truth must include `Release Window Audit: PASS`"
            ),
        )
    elif phase_status_pr_readiness_seam == PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM:
        require(
            next_legal_phase == "Release Readiness",
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Next Legal Phase must advance to `Release Readiness` once PR Readiness PR2 is active"
            ),
        )
        require(
            phase_status_next_seam == PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Phase Status `Next Active Seam` must point to PR Readiness PR2 during merge watch"
            ),
        )
        require(
            active_seam_current == PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Active Seam must name PR Readiness PR2 as the current active seam"
            ),
        )
        require(
            active_seam_next == PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Active Seam `Next active seam` must point to PR Readiness PR2"
            ),
        )
        require(
            continuation_next_seam == PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Seam Continuation Decision must point to PR Readiness PR2 while merge "
                "verification is pending"
            ),
        )
        require(
            "Release Window Audit: PASS" in release_window_section,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "PR Readiness truth must include `Release Window Audit: PASS`"
            ),
        )
        require(
            "PR Merge Verification Pending" in blockers_section,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "PR Readiness PR2 must carry `PR Merge Verification Pending` until merge is verified"
            ),
        )
    else:
        require(
            False,
            (
                "Docs/branch_records/feature_pr103_post_merge_closeout_canon_repair.md: "
                "Current PR Readiness Seam must be exactly "
                f"`{PR103_CLOSEOUT_CANON_PR_READINESS_PR1_SEAM}` or "
                f"`{PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM}` while Phase is `PR Readiness`"
            ),
        )


def _validate_backlog_family_dossier_shell(
    require,
    *,
    current_branch: str,
    backlog_entries: list[dict[str, str]],
    roadmap_text: str,
    index_text: str,
    main_text: str,
) -> None:
    if not _is_backlog_family_reform_branch(current_branch):
        return

    require(
        REFORM_FB042_DOSSIER_PATH.is_file(),
        (
            "Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md: FB-042 dossier "
            "shell must exist on the backlog-family reform branch after R4-S1"
        ),
    )
    if not REFORM_FB042_DOSSIER_PATH.is_file():
        return

    index_dossier_section = _section(index_text, "Family Dossier Records")
    main_dossier_routes = _subsection(main_text, "Family Dossiers And Historical Pass Trace Routing")

    def require_dossier_shell(
        *,
        backlog_id: str,
        dossier_path: Path,
        required_phrases: tuple[str, ...],
        seam_label: str,
    ) -> None:
        dossier_text = _read_text(dossier_path)
        backlog_entry = _backlog_entry_by_id(backlog_entries, backlog_id)
        roadmap_section = _roadmap_section_for_id(roadmap_text, backlog_id)

        for heading in REFORM_FAMILY_DOSSIER_REQUIRED_HEADINGS:
            require(
                heading in dossier_text,
                f"{dossier_path}: required heading '{heading}' is missing",
            )

        for phrase in required_phrases:
            require(
                phrase in dossier_text,
                f"{dossier_path}: required dossier-shell marker '{phrase}' is missing",
            )

        require(
            bool(backlog_entry),
            f"Docs/feature_backlog.md: {backlog_id} backlog entry is missing",
        )
        if backlog_entry:
            require(
                f"Lifetime Dossier Doc: {dossier_path.as_posix()}" in backlog_entry["block"],
                (
                    f"Docs/feature_backlog.md: {backlog_id} must cite the lifetime dossier shell "
                    f"after {seam_label}"
                ),
            )

        require(
            bool(roadmap_section),
            f"Docs/prebeta_roadmap.md: {backlog_id} roadmap section is missing",
        )
        if roadmap_section:
            require(
                str(dossier_path).replace("\\", "/") in roadmap_section,
                (
                    f"Docs/prebeta_roadmap.md: {backlog_id} roadmap section must cite the "
                    f"lifetime dossier shell after {seam_label}"
                ),
            )

        require(
            str(dossier_path).replace("\\", "/") in index_dossier_section,
            f"Docs/workstreams/index.md: Family Dossier Records must list the {backlog_id} dossier shell",
        )
        require(
            str(dossier_path).replace("\\", "/") in main_dossier_routes,
            (
                "Docs/Main.md: Family Dossiers And Historical Pass Trace Routing must route the "
                f"{backlog_id} dossier shell"
            ),
        )

    require_dossier_shell(
        backlog_id="FB-042",
        dossier_path=REFORM_FB042_DOSSIER_PATH,
        required_phrases=REFORM_FB042_DOSSIER_REQUIRED_PHRASES,
        seam_label="R4-S1",
    )

    require(
        REFORM_FB027_DOSSIER_PATH.is_file(),
        (
            "Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md: FB-027 "
            "dossier shell must exist on the backlog-family reform branch after R4-S2"
        ),
    )
    if not REFORM_FB027_DOSSIER_PATH.is_file():
        return

    require_dossier_shell(
        backlog_id="FB-027",
        dossier_path=REFORM_FB027_DOSSIER_PATH,
        required_phrases=REFORM_FB027_DOSSIER_REQUIRED_PHRASES,
        seam_label="R4-S2",
    )


def _validate_backlog_family_historical_pass_records(require, *, current_branch: str) -> None:
    if not _is_backlog_family_reform_branch(current_branch):
        return

    for workstream_path, info in REFORM_FB042_HISTORICAL_PASS_DOCS.items():
        require(
            workstream_path.is_file(),
            f"{workstream_path}: historical pass record must exist on the reform branch",
        )
        if not workstream_path.is_file():
            continue
        workstream_text = _read_text(workstream_path)
        required_phrases = (
            "Lifetime Dossier Doc: `Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md`",
            "Historical pass-record conversion to the FB-042 family model is complete in `Phase 5 / Slice R5-S1` on `feature/backlog-family-governance-reform`.",
            "## Historical Pass Record Identity",
            "Family Anchor ID: `FB-042`",
            "Family Anchor Title: `Desktop startup runtime family anchor`",
            "Family Dossier Doc: `Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md`",
            "Backlog Registry Class: `Historical Pass Alias`",
            "Historical Alias Of: `FB-042`",
            f"Pass ID: `{info['pass_id']}`",
            "Alias Role: `Historical Pass Record`",
            "Standalone Selection Status: `Not independently selectable`",
            "Converted By Seam: `Phase 5 - Historical Pass Record Conversion / Slice R5-S1 - Convert FB-043 through FB-048 workstream records`",
            f"Historical Branch Readiness Record: `{info['branch_record']}`",
            "Preservation Rule: `This record keeps the detailed branch-local execution, validation, release, and PR history; the family dossier owns cross-pass indexing.`",
        )
        for phrase in required_phrases:
            require(
                phrase in workstream_text,
                f"{workstream_path}: required historical pass-record marker '{phrase}' is missing",
            )

    for workstream_path, info in REFORM_FB027_HISTORICAL_PASS_DOCS.items():
        require(
            workstream_path.is_file(),
            f"{workstream_path}: historical pass record must exist on the reform branch",
        )
        if not workstream_path.is_file():
            continue
        workstream_text = _read_text(workstream_path)
        required_phrases = (
            "Lifetime Dossier Doc: `Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md`",
            "## Historical Pass Record Identity",
            "Family Anchor ID: `FB-027`",
            "Family Anchor Title: `Interaction and shared-action family anchor`",
            "Family Dossier Doc: `Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md`",
            "Backlog Registry Class: `Historical Pass Alias`",
            "Historical Alias Of: `FB-027`",
            f"Pass ID: `{info['pass_id']}`",
            "Alias Role: `Historical Pass Record`",
            "Standalone Selection Status: `Not independently selectable`",
            "Converted By Seam: `Phase 5 - Historical Pass Record Conversion / Slice R5-S2 - Convert FB-036, FB-037, FB-038, and FB-041 workstream records`",
            info["branch_record_phrase"],
            "Preservation Rule: `This record keeps the detailed branch-local execution, validation, release, and artifact history; the family dossier owns cross-pass indexing.`",
        )
        for phrase in required_phrases:
            require(
                phrase in workstream_text,
                f"{workstream_path}: required historical pass-record marker '{phrase}' is missing",
            )

    for branch_record_path, info in REFORM_HISTORICAL_PASS_BRANCH_RECORDS.items():
        require(
            branch_record_path.is_file(),
            f"{branch_record_path}: historical branch record must exist on the reform branch",
        )
        if not branch_record_path.is_file():
            continue
        branch_record_text = _read_text(branch_record_path)
        required_phrases = (
            "## Historical Pass Record Identity",
            f"Family Anchor ID: `{info['family_anchor_id']}`",
            f"Family Dossier Doc: `{info['family_dossier']}`",
            "Backlog Registry Class: `Historical Pass Alias`",
            f"Historical Alias Of: `{info['family_anchor_id']}`",
            f"Pass ID: `{info['pass_id']}`",
            "Alias Role: `Historical Pass Record`",
            "Standalone Selection Status: `Not independently selectable`",
            "Converted By Seam: `Phase 5 - Historical Pass Record Conversion / Slice R5-S3 - Convert corresponding branch records`",
            f"Corresponding Historical Workstream Record: `{info['workstream_record']}`",
            f"Preservation Rule: `{info['preservation_rule']}`",
        )
        for phrase in required_phrases:
            require(
                phrase in branch_record_text,
                f"{branch_record_path}: required historical pass-branch marker '{phrase}' is missing",
            )

    for doc_path, expectations in REFORM_R5_S4_HISTORICAL_LANGUAGE_DOCS.items():
        require(
            doc_path.is_file(),
            f"{doc_path}: R5-S4 historical-only language surface must exist on the reform branch",
        )
        if not doc_path.is_file():
            continue
        doc_text = _read_text(doc_path)
        for phrase in expectations["required"]:
            require(
                phrase in doc_text,
                f"{doc_path}: required R5-S4 historical-language marker '{phrase}' is missing",
            )
        for phrase in expectations["prohibited"]:
            require(
                phrase not in doc_text,
                f"{doc_path}: stale future-selection phrase '{phrase}' must be removed in R5-S4",
            )

    for doc_path, required_phrases in REFORM_R5_S5_TRACEABILITY_REQUIRED_PHRASES.items():
        require(
            doc_path.is_file(),
            f"{doc_path}: R5-S5 traceability surface must exist on the reform branch",
        )
        if not doc_path.is_file():
            continue
        doc_text = _read_text(doc_path)
        for phrase in required_phrases:
            require(
                phrase in doc_text,
                f"{doc_path}: required R5-S5 traceability marker '{phrase}' is missing",
            )

    r6_s1_roadmap_text = _read_text(Path("Docs/prebeta_roadmap.md"))
    for phrase in REFORM_R6_S1_ROADMAP_REQUIRED_PHRASES:
        require(
            phrase in r6_s1_roadmap_text,
            (
                "Docs/prebeta_roadmap.md: required R6-S1 roadmap anchor-conversion marker "
                f"'{phrase}' is missing"
            ),
        )

    r6_s2_index_text = _read_text(Path("Docs/workstreams/index.md"))
    for phrase in REFORM_R6_S2_INDEX_REQUIRED_PHRASES:
        require(
            phrase in r6_s2_index_text,
            (
                "Docs/workstreams/index.md: required R6-S2 workstream-index split marker "
                f"'{phrase}' is missing"
            ),
        )

    for doc_path, required_phrases in REFORM_R6_S3_ROUTER_REQUIRED_PHRASES.items():
        require(
            doc_path.is_file(),
            f"{doc_path}: R6-S3 router/loader surface must exist on the reform branch",
        )
        if not doc_path.is_file():
            continue
        doc_text = _read_text(doc_path)
        for phrase in required_phrases:
            require(
                phrase in doc_text,
                f"{doc_path}: required R6-S3 router/loader marker '{phrase}' is missing",
            )


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


def _git_output_at(cwd: Path, args: tuple[str, ...]) -> tuple[str, str]:
    completed = subprocess.run(
        ("git", *args),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return "", completed.stderr.strip() or completed.stdout.strip() or "git command failed"
    return completed.stdout.strip(), ""


def _git_fetch_origin_at(cwd: Path) -> str:
    completed = subprocess.run(
        ("git", "fetch", "origin", "--prune"),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return completed.stderr.strip() or completed.stdout.strip() or "git fetch failed"
    return ""


def _neutral_main_workspace_truth() -> dict[str, str]:
    if not NEUTRAL_MAIN_WORKSPACE.exists():
        return {"error": f"{NEUTRAL_MAIN_WORKSPACE} does not exist"}

    fetch_error = _git_fetch_origin_at(NEUTRAL_MAIN_WORKSPACE)
    root, root_error = _git_output_at(NEUTRAL_MAIN_WORKSPACE, ("rev-parse", "--show-toplevel"))
    branch, branch_error = _git_output_at(NEUTRAL_MAIN_WORKSPACE, ("branch", "--show-current"))
    status, status_error = _git_output_at(
        NEUTRAL_MAIN_WORKSPACE,
        ("status", "--porcelain", "--untracked-files=no"),
    )
    head, head_error = _git_output_at(NEUTRAL_MAIN_WORKSPACE, ("rev-parse", "HEAD"))
    origin_main, origin_main_error = _git_output_at(
        NEUTRAL_MAIN_WORKSPACE,
        ("rev-parse", "refs/remotes/origin/main"),
    )
    errors = [
        error
        for error in (
            fetch_error,
            root_error,
            branch_error,
            status_error,
            head_error,
            origin_main_error,
        )
        if error
    ]
    return {
        "error": "; ".join(errors),
        "root": root,
        "branch": branch,
        "status": status,
        "head": head,
        "origin_main": origin_main,
    }


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


def _git_top_level() -> str:
    completed = subprocess.run(
        ("git", "rev-parse", "--show-toplevel"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _git_upstream_branch() -> str:
    completed = subprocess.run(
        ("git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _normalized_local_path(value: str) -> str:
    normalized = value.strip().strip("`").strip('"').replace("/", "\\")
    if not normalized:
        return ""
    try:
        normalized = str(Path(normalized).resolve(strict=False))
    except (OSError, RuntimeError, ValueError):
        pass
    return normalized.rstrip("\\").casefold()


def _git_head_sha() -> str:
    completed = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _git_ref_sha(ref: str) -> str:
    completed = subprocess.run(
        ("git", "rev-parse", ref),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _is_merged_main_snapshot() -> bool:
    current_branch = _git_current_branch()
    if current_branch == "main":
        return True
    if current_branch:
        return False
    head_sha = _git_head_sha()
    origin_main_sha = _git_ref_sha("refs/remotes/origin/main")
    return bool(head_sha and origin_main_sha and head_sha == origin_main_sha)


def _head_matches_origin_main() -> bool:
    head_sha = _git_head_sha()
    origin_main_sha = _git_ref_sha("refs/remotes/origin/main")
    return bool(head_sha and origin_main_sha and head_sha == origin_main_sha)


def _git_head_commit_time() -> datetime | None:
    completed = subprocess.run(
        ("git", "show", "-s", "--format=%cI", "HEAD"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return _parse_iso8601_timestamp(completed.stdout.strip())


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


def _git_origin_repository_full_name() -> tuple[str, str]:
    completed = subprocess.run(
        ("git", "remote", "get-url", "origin"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return "", completed.stderr.strip() or "git remote get-url origin failed"

    remote_url = completed.stdout.strip()
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", remote_url)
    if not match:
        return "", f"could not parse GitHub origin remote '{remote_url}'"
    return f"{match.group('owner')}/{match.group('repo')}", ""


def _git_changed_files(base_sha: str, head_sha: str) -> tuple[list[str], str]:
    completed = subprocess.run(
        ("git", "diff", "--name-only", f"{base_sha}..{head_sha}"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return [], completed.stderr.strip() or completed.stdout.strip() or "git diff failed"
    files = [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]
    return files, ""


def _git_is_ancestor(ancestor_sha: str, descendant_sha: str) -> tuple[bool, str]:
    completed = subprocess.run(
        ("git", "merge-base", "--is-ancestor", ancestor_sha, descendant_sha),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode == 0:
        return True, ""
    if completed.returncode == 1:
        return False, ""
    return False, completed.stderr.strip() or completed.stdout.strip() or "git merge-base failed"


def _branch_ref_is_merged_into_origin_main(branch_name: str) -> tuple[bool, str]:
    normalized_branch = branch_name.strip()
    if normalized_branch.startswith("origin/"):
        normalized_branch = normalized_branch.removeprefix("origin/")
    if not normalized_branch:
        return False, ""

    origin_main_ref = "refs/remotes/origin/main"
    if not _git_ref_sha(origin_main_ref):
        return False, "could not resolve refs/remotes/origin/main"

    candidate_refs = (
        f"refs/remotes/origin/{normalized_branch}",
        f"refs/heads/{normalized_branch}",
    )
    for candidate_ref in candidate_refs:
        if not _git_ref_sha(candidate_ref):
            continue
        is_ancestor, error = _git_is_ancestor(candidate_ref, origin_main_ref)
        if error:
            return False, error
        if is_ancestor:
            return True, ""
    return False, ""


def _local_merge_tree_clean() -> tuple[bool, str]:
    completed = subprocess.run(
        ("git", "merge-tree", "--write-tree", "origin/main", "HEAD"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode == 0:
        return True, ""
    return False, completed.stderr.strip() or completed.stdout.strip() or "git merge-tree failed"


def _is_allowed_bot_review_comment_closeout_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    if normalized in BOT_REVIEW_COMMENT_CLOSEOUT_ALLOWED_FILES:
        return True
    return any(normalized.startswith(prefix) for prefix in BOT_REVIEW_COMMENT_CLOSEOUT_ALLOWED_PREFIXES)


def _bot_review_comment_closeout_followthrough_ok(
    recorded_head_sha: str,
    current_head_sha: str,
) -> tuple[bool, str]:
    is_ancestor, ancestor_error = _git_is_ancestor(recorded_head_sha, current_head_sha)
    if ancestor_error:
        return False, ancestor_error
    if not is_ancestor:
        return (
            False,
            f"recorded bot-review head '{recorded_head_sha}' is not an ancestor of current head '{current_head_sha}'",
        )

    changed_files, diff_error = _git_changed_files(recorded_head_sha, current_head_sha)
    if diff_error:
        return False, diff_error
    disallowed_files = [
        path for path in changed_files if not _is_allowed_bot_review_comment_closeout_path(path)
    ]
    if disallowed_files:
        return (
            False,
            "comment-addressed follow-through after the recorded head changed disallowed files: "
            + ", ".join(disallowed_files),
        )
    return True, ""


def _github_api_auth_token() -> str:
    global _GITHUB_API_TOKEN
    global _GITHUB_API_TOKEN_LOADED

    if _GITHUB_API_TOKEN_LOADED:
        return _GITHUB_API_TOKEN

    _GITHUB_API_TOKEN_LOADED = True
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    if not token:
        try:
            completed = subprocess.run(
                ("gh", "auth", "token"),
                cwd=ROOT_DIR,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except FileNotFoundError:
            completed = None
        if completed is not None and completed.returncode == 0:
            token = completed.stdout.strip()
    _GITHUB_API_TOKEN = token.strip()
    return _GITHUB_API_TOKEN


def _github_api_request_headers() -> dict[str, str]:
    headers = dict(GITHUB_API_HEADERS)
    token = _github_api_auth_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _github_api_json(url: str) -> tuple[object | None, str]:
    request = urllib_request.Request(url, headers=_github_api_request_headers())
    try:
        with urllib_request.urlopen(request, timeout=GITHUB_API_TIMEOUT_SECONDS) as response:
            payload = response.read().decode("utf-8", "replace")
    except urllib_error.HTTPError as exc:
        details = exc.read().decode("utf-8", "replace")
        message = details.strip() or exc.reason or "GitHub API HTTP error"
        return None, f"{exc.code} {message}"
    except urllib_error.URLError as exc:
        return None, str(exc.reason or exc)
    except OSError as exc:
        return None, str(exc)

    try:
        return json.loads(payload), ""
    except json.JSONDecodeError as exc:
        return None, f"could not parse GitHub API JSON: {exc}"


def _parse_iso8601_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _bot_login_matches(login: str) -> bool:
    lowered = login.casefold()
    if lowered == BOT_REVIEW_BOT_LOGIN.casefold():
        return True
    return "codex" in lowered and "connector" in lowered and "bot" in lowered


def _bot_review_comment_is_green_signal(body: str) -> bool:
    lead_summary = (
        body.casefold()
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .split("<details", 1)[0]
    )
    has_green_phrase = any(
        phrase in lead_summary
        for phrase in BOT_REVIEW_GREEN_COMMENT_PHRASES
    )
    if not has_green_phrase:
        return False
    return not re.search(r"\b(but|however|except|although|though|unless)\b", lead_summary)


def _github_pr_review_request_comment_matches(author: str, body: str) -> bool:
    if _bot_login_matches(author):
        return False
    lowered = body.casefold()
    return "@codex" in lowered and "review" in lowered


def _github_rest_review_decision(
    repository_full_name: str,
    pr_number: int,
    requested_reviewers: list[object],
    requested_teams: list[object],
) -> tuple[str, str]:
    reviews_payload, reviews_error = _github_api_json(
        f"https://api.github.com/repos/{repository_full_name}/pulls/{pr_number}/reviews"
    )
    if reviews_error:
        return "", reviews_error

    latest_by_author: dict[str, str] = {}
    for review in reviews_payload or []:
        author = str(((review.get("user") or {}).get("login")) or "").casefold()
        state = str(review.get("state") or "").upper()
        if author and state:
            latest_by_author[author] = state

    if any(state == "CHANGES_REQUESTED" for state in latest_by_author.values()):
        return "CHANGES_REQUESTED", ""
    if requested_reviewers or requested_teams:
        return "REVIEW_REQUIRED", ""
    if any(state == "APPROVED" for state in latest_by_author.values()):
        return "APPROVED", ""
    return "", ""


def _github_rest_pr_view_for_branch(
    branch_name: str,
    repository_full_name: str,
) -> tuple[dict[str, object] | None, str]:
    if not repository_full_name:
        return None, "GitHub origin repository is unknown"

    owner = repository_full_name.split("/", 1)[0]
    pulls_url = (
        "https://api.github.com/repos/"
        f"{repository_full_name}/pulls?state=all&head={urllib_parse.quote(f'{owner}:{branch_name}', safe=':')}"
    )
    pulls_payload, pulls_error = _github_api_json(pulls_url)
    if pulls_error:
        return None, f"REST pull lookup failed: {pulls_error}"
    pulls = pulls_payload or []
    if not pulls:
        return None, f"REST pull lookup found no PR for branch '{branch_name}'"

    pull = max(
        pulls,
        key=lambda item: int(item.get("number") or 0),
    )
    pr_number = int(pull.get("number") or 0)
    if not pr_number:
        return None, f"REST pull lookup returned no PR number for branch '{branch_name}'"

    detail_payload, detail_error = _github_api_json(
        f"https://api.github.com/repos/{repository_full_name}/pulls/{pr_number}"
    )
    if detail_error:
        return None, f"REST pull detail lookup failed: {detail_error}"

    requested_reviewers = list(detail_payload.get("requested_reviewers") or [])
    requested_teams = list(detail_payload.get("requested_teams") or [])
    review_decision, review_error = _github_rest_review_decision(
        repository_full_name,
        pr_number,
        requested_reviewers,
        requested_teams,
    )
    if review_error:
        return None, f"REST review lookup failed: {review_error}"

    mergeable_value = detail_payload.get("mergeable")
    if mergeable_value is True:
        mergeable = "MERGEABLE"
    elif mergeable_value is False:
        mergeable = "CONFLICTING"
    else:
        mergeable = "UNKNOWN"

    return {
        "id": detail_payload.get("node_id") or "",
        "number": pr_number,
        "state": str(detail_payload.get("state") or "").upper(),
        "mergeable": mergeable,
        "mergeStateStatus": str(detail_payload.get("mergeable_state") or "").upper(),
        "reviewDecision": review_decision,
        "isDraft": bool(detail_payload.get("draft")),
        "headRefName": str(((detail_payload.get("head") or {}).get("ref")) or ""),
        "headRefOid": str(((detail_payload.get("head") or {}).get("sha")) or ""),
        "baseRefName": str(((detail_payload.get("base") or {}).get("ref")) or ""),
        "title": str(detail_payload.get("title") or ""),
        "url": str(detail_payload.get("html_url") or ""),
        "repositoryFullName": repository_full_name,
    }, ""


def _codex_related_author_or_body(author: str, body: str) -> bool:
    author_lower = author.casefold()
    body_lower = body.casefold()
    return "codex" in author_lower or "openai" in author_lower or "codex" in body_lower


def _github_rest_unresolved_codex_threads(
    repository_full_name: str,
    pr_number: int,
) -> tuple[list[str], str]:
    if not repository_full_name or not pr_number:
        return [], "REST fallback is missing PR identity"

    issue_comments_payload, issue_comments_error = _github_api_json(
        f"https://api.github.com/repos/{repository_full_name}/issues/{pr_number}/comments"
    )
    if issue_comments_error:
        return [], f"REST issue-comment lookup failed: {issue_comments_error}"

    review_comments_payload, review_comments_error = _github_api_json(
        f"https://api.github.com/repos/{repository_full_name}/pulls/{pr_number}/comments"
    )
    if review_comments_error:
        return [], f"REST review-comment lookup failed: {review_comments_error}"

    reviews_payload, reviews_error = _github_api_json(
        f"https://api.github.com/repos/{repository_full_name}/pulls/{pr_number}/reviews"
    )
    if reviews_error:
        return [], f"REST review lookup failed: {reviews_error}"

    unresolved: list[str] = []
    for comment in issue_comments_payload or []:
        author = str(((comment.get("user") or {}).get("login")) or "")
        body = str(comment.get("body") or "")
        if _codex_related_author_or_body(author, body):
            unresolved.append(author.casefold() or "unknown-author")

    codex_review_comment_found = False
    for comment in review_comments_payload or []:
        author = str(((comment.get("user") or {}).get("login")) or "")
        body = str(comment.get("body") or "")
        if _codex_related_author_or_body(author, body):
            codex_review_comment_found = True
            unresolved.append(author.casefold() or "unknown-author")

    for review in reviews_payload or []:
        author = str(((review.get("user") or {}).get("login")) or "")
        body = str(review.get("body") or "")
        state = str(review.get("state") or "").upper()
        if _codex_related_author_or_body(author, body) and state in {"COMMENTED", "CHANGES_REQUESTED"}:
            unresolved.append(author.casefold() or "unknown-author")

    if codex_review_comment_found:
        return (
            sorted(set(unresolved)),
            "could not confirm resolution status for Codex review-thread comments via REST fallback",
        )
    return sorted(set(unresolved)), ""


def _github_pr_bot_signal_for_live_pr(
    repository_full_name: str,
    pr_number: int,
    current_head_sha: str = "",
) -> tuple[dict[str, str], str]:
    signal = {"status": "pending", "source": "", "timestamp": "", "actor": "", "head": ""}
    if not repository_full_name or not pr_number:
        return signal, "live PR identity is incomplete"

    if current_head_sha:
        timeline_signal, timeline_error = _github_pr_bot_signal_for_current_head_timeline(
            repository_full_name,
            pr_number,
            current_head_sha,
        )
        if timeline_signal.get("status") != "pending" and not timeline_error:
            return timeline_signal, ""
        rest_signal, rest_error = _github_pr_bot_signal_for_current_head_rest(
            repository_full_name,
            pr_number,
            current_head_sha,
        )
        if rest_signal.get("status") != "pending" and not rest_error:
            return rest_signal, ""
        if rest_error:
            return signal, f"{timeline_error}; {rest_error}"
        return signal, timeline_error

    reactions_payload, reactions_error = _github_api_json(
        f"https://api.github.com/repos/{repository_full_name}/issues/{pr_number}/reactions"
    )
    if reactions_error:
        return signal, f"reaction lookup failed: {reactions_error}"
    latest_approval: dict[str, object] | None = None
    for reaction in reactions_payload or []:
        actor = str(((reaction.get("user") or {}).get("login")) or "")
        created_at = str(reaction.get("created_at") or "")
        created_time = _parse_iso8601_timestamp(created_at)
        content = str(reaction.get("content") or "")
        if (
            _bot_login_matches(actor)
            and content == "+1"
            and created_time is not None
        ):
            if latest_approval is None or created_time >= latest_approval["time"]:
                latest_approval = {
                    "time": created_time,
                    "timestamp": created_at,
                    "actor": actor,
                }

    latest_comment: dict[str, object] | None = None
    for url, source_name in (
        (f"https://api.github.com/repos/{repository_full_name}/issues/{pr_number}/comments", "issue comment"),
        (f"https://api.github.com/repos/{repository_full_name}/pulls/{pr_number}/reviews", "review comment"),
        (f"https://api.github.com/repos/{repository_full_name}/pulls/{pr_number}/comments", "inline review comment"),
    ):
        payload, payload_error = _github_api_json(url)
        if payload_error:
            return signal, f"{source_name} lookup failed: {payload_error}"
        for item in payload or []:
            actor = str(((item.get("user") or {}).get("login")) or "")
            body = str(item.get("body") or "")
            created_at = str(
                item.get("submitted_at")
                or item.get("created_at")
                or ""
            )
            created_time = _parse_iso8601_timestamp(created_at)
            if _bot_login_matches(actor) and created_time is not None:
                if _bot_review_comment_is_green_signal(body):
                    approval_candidate = {
                        "time": created_time,
                        "timestamp": created_at,
                        "actor": actor,
                    }
                    if latest_approval is None or created_time >= latest_approval["time"]:
                        latest_approval = approval_candidate
                    continue
                if latest_comment is None or created_time >= latest_comment["time"]:
                    latest_comment = {
                        "time": created_time,
                        "source": source_name,
                        "timestamp": created_at,
                        "actor": actor,
                    }

    if latest_comment and (
        latest_approval is None or latest_comment["time"] >= latest_approval["time"]
    ):
        return {
            "status": "comment",
            "source": str(latest_comment["source"]),
            "timestamp": str(latest_comment["timestamp"]),
            "actor": str(latest_comment["actor"]),
        }, ""

    if latest_approval:
        return {
            "status": BOT_REVIEW_SIGNAL_STATUS_APPROVED.casefold(),
            "source": "thumbs-up reaction",
            "timestamp": str(latest_approval["timestamp"]),
            "actor": str(latest_approval["actor"]),
            "head": "",
        }, ""

    return signal, ""


def _github_pr_timeline_graphql_json(
    repository_full_name: str,
    pr_number: int,
) -> tuple[dict[str, object] | None, str]:
    if "/" not in repository_full_name:
        return None, f"invalid repository name '{repository_full_name}'"
    owner, repo = repository_full_name.split("/", 1)
    query = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      headRefOid
      commits(last: 1) {
        nodes {
          commit { oid committedDate pushedDate }
        }
      }
      reactions(first: 100, content: THUMBS_UP) {
        nodes {
          content
          createdAt
          user { login }
        }
      }
      timelineItems(last: 100, itemTypes: [PULL_REQUEST_COMMIT, PULL_REQUEST_REVIEW, ISSUE_COMMENT]) {
        nodes {
          __typename
          ... on PullRequestCommit {
            commit { oid committedDate pushedDate }
          }
          ... on PullRequestReview {
            createdAt
            submittedAt
            state
            author { login }
            body
            commit { oid }
          }
          ... on IssueComment {
            createdAt
            author { login }
            body
            reactions(first: 100) {
              nodes {
                content
                createdAt
                user { login }
              }
            }
          }
        }
      }
    }
  }
}
"""
    try:
        completed = subprocess.run(
            (
                "gh",
                "api",
                "graphql",
                "-f",
                f"query={query}",
                "-f",
                f"owner={owner}",
                "-f",
                f"repo={repo}",
                "-F",
                f"number={pr_number}",
            ),
            cwd=ROOT_DIR,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        return None, str(exc)
    if completed.returncode != 0:
        return None, completed.stderr.strip() or completed.stdout.strip() or "gh api graphql failed"
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return None, f"could not parse PR timeline JSON: {exc}"
    pull_request = (((payload.get("data") or {}).get("repository") or {}).get("pullRequest") or {})
    if not pull_request:
        return None, f"PR #{pr_number} timeline payload is empty"
    return pull_request, ""


def _latest_signal_candidate(
    current: dict[str, object] | None,
    candidate: dict[str, object],
) -> dict[str, object]:
    if current is None:
        return candidate
    candidate_time = candidate.get("time")
    current_time = current.get("time")
    if isinstance(candidate_time, datetime) and isinstance(current_time, datetime):
        if candidate_time >= current_time:
            return candidate
    return current


def _github_pr_bot_signal_for_current_head_timeline(
    repository_full_name: str,
    pr_number: int,
    current_head_sha: str,
) -> tuple[dict[str, str], str]:
    signal = {"status": "pending", "source": "", "timestamp": "", "actor": "", "head": ""}
    pull_request, timeline_error = _github_pr_timeline_graphql_json(
        repository_full_name,
        pr_number,
    )
    if timeline_error:
        return signal, timeline_error
    if not pull_request:
        return signal, f"PR #{pr_number} timeline payload is empty"

    pr_head_sha = str(pull_request.get("headRefOid") or "")
    if pr_head_sha and pr_head_sha != current_head_sha:
        return (
            signal,
            (
                f"live PR head '{pr_head_sha}' does not match current branch head "
                f"'{current_head_sha}'"
            ),
        )

    nodes = (((pull_request.get("timelineItems") or {}).get("nodes")) or [])
    current_head_index: int | None = None
    current_head_admission_time: datetime | None = None
    current_head_commit_time: datetime | None = None
    current_head_review_request_time: datetime | None = None
    commit_nodes = (((pull_request.get("commits") or {}).get("nodes")) or [])
    for commit_node in commit_nodes:
        commit_payload = commit_node.get("commit") or {}
        oid = str(commit_payload.get("oid") or "")
        if oid != current_head_sha:
            continue
        pushed_at = str(commit_payload.get("pushedDate") or "")
        committed_at = str(commit_payload.get("committedDate") or "")
        current_head_admission_time = _parse_iso8601_timestamp(pushed_at)
        current_head_commit_time = _parse_iso8601_timestamp(committed_at)

    for index, node in enumerate(nodes):
        if node.get("__typename") != "PullRequestCommit":
            continue
        commit_payload = node.get("commit") or {}
        oid = str(commit_payload.get("oid") or "")
        if oid == current_head_sha:
            current_head_index = index
            pushed_at = str(commit_payload.get("pushedDate") or "")
            committed_at = str(commit_payload.get("committedDate") or "")
            current_head_admission_time = _parse_iso8601_timestamp(pushed_at)
            current_head_commit_time = _parse_iso8601_timestamp(committed_at)

    latest_approval: dict[str, object] | None = None
    latest_comment: dict[str, object] | None = None
    for index, node in enumerate(nodes):
        typename = str(node.get("__typename") or "")
        if typename == "PullRequestReview":
            actor = str(((node.get("author") or {}).get("login")) or "")
            body = str(node.get("body") or "")
            review_head = str(((node.get("commit") or {}).get("oid")) or "")
            created_at = str(node.get("submittedAt") or node.get("createdAt") or "")
            created_time = _parse_iso8601_timestamp(created_at)
            if not (_bot_login_matches(actor) and created_time is not None):
                continue
            if review_head != current_head_sha:
                continue
            if _bot_review_comment_is_green_signal(body):
                latest_approval = _latest_signal_candidate(
                    latest_approval,
                    {
                        "time": created_time,
                        "timestamp": created_at,
                        "actor": actor,
                        "source": "green review comment",
                        "head": review_head,
                    },
                )
            else:
                latest_comment = _latest_signal_candidate(
                    latest_comment,
                    {
                        "time": created_time,
                        "timestamp": created_at,
                        "actor": actor,
                        "source": "review comment",
                        "head": review_head,
                    },
                )
            continue

        if typename != "IssueComment":
            continue
        actor = str(((node.get("author") or {}).get("login")) or "")
        body = str(node.get("body") or "")
        created_at = str(node.get("createdAt") or "")
        created_time = _parse_iso8601_timestamp(created_at)
        if created_time is None:
            continue
        if current_head_index is not None and index <= current_head_index:
            continue
        if (
            current_head_index is None
            and (
                current_head_admission_time is None
                or created_time < current_head_admission_time
            )
        ):
            continue
        if _github_pr_review_request_comment_matches(actor, body):
            if (
                current_head_review_request_time is None
                or created_time >= current_head_review_request_time
            ):
                current_head_review_request_time = created_time
        if _bot_login_matches(actor) and created_time is not None:
            if _bot_review_comment_is_green_signal(body):
                latest_approval = _latest_signal_candidate(
                    latest_approval,
                    {
                        "time": created_time,
                        "timestamp": created_at,
                        "actor": actor,
                        "source": "green issue comment",
                        "head": current_head_sha,
                    },
                )
            else:
                latest_comment = _latest_signal_candidate(
                    latest_comment,
                    {
                        "time": created_time,
                        "timestamp": created_at,
                        "actor": actor,
                        "source": "issue comment",
                        "head": current_head_sha,
                    },
                )

        reactions = ((node.get("reactions") or {}).get("nodes")) or []
        for reaction in reactions:
            reaction_actor = str(((reaction.get("user") or {}).get("login")) or "")
            content = str(reaction.get("content") or "")
            reaction_at = str(reaction.get("createdAt") or "")
            reaction_time = _parse_iso8601_timestamp(reaction_at)
            if not (
                _bot_login_matches(reaction_actor)
                and content in {"+1", "THUMBS_UP"}
                and reaction_time is not None
            ):
                continue
            if created_time is not None and reaction_time < created_time:
                continue
            latest_approval = _latest_signal_candidate(
                latest_approval,
                {
                    "time": reaction_time,
                    "timestamp": reaction_at,
                    "actor": reaction_actor,
                    "source": "thumbs-up reaction",
                    "head": current_head_sha,
                },
            )

    pr_reactions = ((pull_request.get("reactions") or {}).get("nodes")) or []
    current_head_reaction_floor_time = (
        current_head_review_request_time or current_head_admission_time
    )
    for reaction in pr_reactions:
        reaction_actor = str(((reaction.get("user") or {}).get("login")) or "")
        content = str(reaction.get("content") or "")
        reaction_at = str(reaction.get("createdAt") or "")
        reaction_time = _parse_iso8601_timestamp(reaction_at)
        if not (
            _bot_login_matches(reaction_actor)
            and content in {"+1", "THUMBS_UP"}
            and reaction_time is not None
            and current_head_reaction_floor_time is not None
            and reaction_time >= current_head_reaction_floor_time
        ):
            continue
        latest_approval = _latest_signal_candidate(
            latest_approval,
            {
                "time": reaction_time,
                "timestamp": reaction_at,
                "actor": reaction_actor,
                "source": "PR-level thumbs-up reaction",
                "head": current_head_sha,
            },
        )

    if latest_comment and (
        latest_approval is None or latest_comment["time"] >= latest_approval["time"]
    ):
        return {
            "status": "comment",
            "source": str(latest_comment["source"]),
            "timestamp": str(latest_comment["timestamp"]),
            "actor": str(latest_comment["actor"]),
            "head": str(latest_comment["head"]),
        }, ""

    if latest_approval:
        return {
            "status": BOT_REVIEW_SIGNAL_STATUS_APPROVED.casefold(),
            "source": str(latest_approval["source"]),
            "timestamp": str(latest_approval["timestamp"]),
            "actor": str(latest_approval["actor"]),
            "head": str(latest_approval["head"]),
        }, ""

    if current_head_index is None and current_head_admission_time is None:
        return (
            signal,
            (
                f"could not locate current head '{current_head_sha}' with PR admission "
                "time or timeline order"
            ),
        )

    return signal, ""


def _github_pr_bot_signal_for_current_head_rest(
    repository_full_name: str,
    pr_number: int,
    current_head_sha: str,
) -> tuple[dict[str, str], str]:
    signal = {"status": "pending", "source": "", "timestamp": "", "actor": "", "head": ""}
    latest_approval: dict[str, object] | None = None
    latest_comment: dict[str, object] | None = None
    current_head_review_request_time: datetime | None = None
    issue_comments_payload, issue_comments_error = _github_api_json(
        f"https://api.github.com/repos/{repository_full_name}/issues/{pr_number}/comments"
    )
    if not issue_comments_error:
        for item in issue_comments_payload or []:
            actor = str(((item.get("user") or {}).get("login")) or "")
            body = str(item.get("body") or "")
            created_at = str(item.get("created_at") or "")
            created_time = _parse_iso8601_timestamp(created_at)
            if created_time is None:
                continue
            if _github_pr_review_request_comment_matches(actor, body):
                if (
                    current_head_review_request_time is None
                    or created_time >= current_head_review_request_time
                ):
                    current_head_review_request_time = created_time

    for url, source_name in (
        (f"https://api.github.com/repos/{repository_full_name}/pulls/{pr_number}/reviews", "review comment"),
        (f"https://api.github.com/repos/{repository_full_name}/pulls/{pr_number}/comments", "inline review comment"),
    ):
        payload, payload_error = _github_api_json(url)
        if payload_error:
            return signal, f"{source_name} lookup failed: {payload_error}"
        for item in payload or []:
            actor = str(((item.get("user") or {}).get("login")) or "")
            body = str(item.get("body") or "")
            commit_id = str(item.get("commit_id") or "")
            created_at = str(item.get("submitted_at") or item.get("created_at") or "")
            created_time = _parse_iso8601_timestamp(created_at)
            if not (
                _bot_login_matches(actor)
                and created_time is not None
                and commit_id == current_head_sha
            ):
                continue
            if _bot_review_comment_is_green_signal(body):
                latest_approval = _latest_signal_candidate(
                    latest_approval,
                    {
                        "time": created_time,
                        "timestamp": created_at,
                        "actor": actor,
                        "source": source_name,
                        "head": commit_id,
                    },
                )
                continue
            latest_comment = _latest_signal_candidate(
                latest_comment,
                {
                    "time": created_time,
                    "timestamp": created_at,
                    "actor": actor,
                    "source": source_name,
                    "head": commit_id,
                },
            )

    if current_head_review_request_time is not None:
        for item in issue_comments_payload or []:
            actor = str(((item.get("user") or {}).get("login")) or "")
            body = str(item.get("body") or "")
            created_at = str(item.get("created_at") or "")
            created_time = _parse_iso8601_timestamp(created_at)
            if not (
                _bot_login_matches(actor)
                and created_time is not None
                and created_time >= current_head_review_request_time
            ):
                continue
            if _bot_review_comment_is_green_signal(body):
                latest_approval = _latest_signal_candidate(
                    latest_approval,
                    {
                        "time": created_time,
                        "timestamp": created_at,
                        "actor": actor,
                        "source": "green issue comment",
                        "head": current_head_sha,
                    },
                )
                continue
            latest_comment = _latest_signal_candidate(
                latest_comment,
                {
                    "time": created_time,
                    "timestamp": created_at,
                    "actor": actor,
                    "source": "issue comment",
                    "head": current_head_sha,
                },
            )

        reactions_payload, reactions_error = _github_api_json(
            f"https://api.github.com/repos/{repository_full_name}/issues/{pr_number}/reactions"
        )
        if reactions_error:
            return signal, f"PR-level reaction lookup failed: {reactions_error}"
        for reaction in reactions_payload or []:
            reaction_actor = str(((reaction.get("user") or {}).get("login")) or "")
            content = str(reaction.get("content") or "")
            reaction_at = str(reaction.get("created_at") or "")
            reaction_time = _parse_iso8601_timestamp(reaction_at)
            if not (
                _bot_login_matches(reaction_actor)
                and content == "+1"
                and reaction_time is not None
                and reaction_time >= current_head_review_request_time
            ):
                continue
            latest_approval = _latest_signal_candidate(
                latest_approval,
                {
                    "time": reaction_time,
                    "timestamp": reaction_at,
                    "actor": reaction_actor,
                    "source": "PR-level thumbs-up reaction",
                    "head": current_head_sha,
                },
            )

    if latest_comment and (
        latest_approval is None or latest_comment["time"] >= latest_approval["time"]
    ):
        return {
            "status": "comment",
            "source": str(latest_comment["source"]),
            "timestamp": str(latest_comment["timestamp"]),
            "actor": str(latest_comment["actor"]),
            "head": str(latest_comment["head"]),
        }, ""

    if latest_approval:
        return {
            "status": BOT_REVIEW_SIGNAL_STATUS_APPROVED.casefold(),
            "source": str(latest_approval["source"]),
            "timestamp": str(latest_approval["timestamp"]),
            "actor": str(latest_approval["actor"]),
            "head": str(latest_approval["head"]),
        }, ""

    if issue_comments_error:
        return signal, f"issue comment lookup failed: {issue_comments_error}"

    return signal, ""


def _gh_pr_view_for_branch(branch_name: str) -> tuple[dict[str, object] | None, str]:
    fields = (
        "id,number,state,mergeable,mergeStateStatus,reviewDecision,isDraft,"
        "headRefName,headRefOid,baseRefName,title,url"
    )
    repository_full_name, repository_error = _git_origin_repository_full_name()
    gh_error = ""
    try:
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
    except FileNotFoundError as exc:
        completed = None
        gh_error = str(exc)

    if completed is not None and completed.returncode == 0:
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            return None, f"could not parse gh pr view JSON: {exc}"
        if repository_full_name:
            payload.setdefault("repositoryFullName", repository_full_name)
        return payload, ""

    if completed is not None:
        gh_error = completed.stderr.strip() or completed.stdout.strip() or "gh pr view failed"
    if repository_error:
        return None, gh_error or repository_error

    rest_payload, rest_error = _github_rest_pr_view_for_branch(branch_name, repository_full_name)
    if rest_payload:
        return rest_payload, ""
    fallback_payload, fallback_error = _automation_planning_fallback_pr_view_for_branch(branch_name)
    if fallback_payload:
        return fallback_payload, ""
    if gh_error:
        combined_error = f"{gh_error}; {rest_error}"
        if fallback_error:
            combined_error = f"{combined_error}; {fallback_error}"
        return None, combined_error
    if fallback_error:
        return None, f"{rest_error}; {fallback_error}"
    return None, rest_error


def _gh_unresolved_codex_threads(
    pr_node_id: str,
    pr_info: dict[str, object] | None = None,
) -> tuple[list[str], str]:
    repository_full_name = str((pr_info or {}).get("repositoryFullName") or "")
    pr_number = int((pr_info or {}).get("number") or 0)

    if not pr_node_id and repository_full_name and pr_number:
        return _github_rest_unresolved_codex_threads(repository_full_name, pr_number)
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
    gh_error = ""
    try:
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
    except FileNotFoundError as exc:
        completed = None
        gh_error = str(exc)
    if completed is None or completed.returncode != 0:
        if completed is not None:
            gh_error = completed.stderr.strip() or completed.stdout.strip() or "gh api graphql failed"
        if repository_full_name and pr_number:
            unresolved, rest_error = _github_rest_unresolved_codex_threads(repository_full_name, pr_number)
            if not rest_error:
                return unresolved, ""
            return [], f"{gh_error}; {rest_error}" if gh_error else rest_error
        return [], gh_error or "gh api graphql failed"

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


def _open_successor_candidate_entries(backlog_entries: list[dict[str, str]]) -> list[dict[str, str]]:
    current_branch = _git_current_branch()
    candidates: list[dict[str, str]] = []
    for entry in backlog_entries:
        if not _is_open_backlog_candidate(entry):
            continue
        entry_branch = _extract_colon_value(entry["block"], "Branch").strip("`")
        if entry_branch and current_branch and entry_branch == current_branch:
            continue
        if entry["status"].strip().casefold() == "active":
            continue
        candidates.append(entry)
    return candidates


def _is_not_closed_backlog_entry(entry: dict[str, str]) -> bool:
    status = entry["status"].strip().casefold()
    normalized_status = _normalize_status(entry["status"])
    return (
        entry["record_state"] != "Closed"
        and normalized_status not in {"released", "closed"}
        and not status.startswith("implemented")
    )


def _format_not_closed_backlog_entries(backlog_entries: list[dict[str, str]]) -> str:
    rows: list[str] = []
    for entry in backlog_entries:
        if not _is_not_closed_backlog_entry(entry):
            continue
        block = entry["block"]
        fields = [
            f"{entry['id']} {entry['title']}",
            f"Status={entry['status'] or 'unknown'}",
            f"Record State={entry['record_state'] or 'unknown'}",
            f"Priority={_extract_colon_value(block, 'Priority') or 'unknown'}",
        ]
        for label in (
            "Selection / Unblock",
            "Deferred Since",
            "Deferred Because",
            "Branch",
            "Minimal Scope",
        ):
            value = _extract_colon_value(block, label)
            if value:
                fields.append(f"{label}={value}")
        rows.append("; ".join(fields))
    return " | ".join(rows)


def _next_workstream_roadmap_section(roadmap_text: str) -> str:
    return _section(roadmap_text, "Selected Next Workstream")


def _selected_next_ignored_branch_names(
    current_branch: str,
    all_repair_branch_names: set[str],
    active_repair_branch_names: set[str],
    historical_branch_names: set[str],
) -> set[str]:
    ignored = set(historical_branch_names)
    if current_branch == "main" or current_branch in active_repair_branch_names:
        ignored.update(all_repair_branch_names)
    return ignored


def _selected_next_repair_only_branch_info(blocks: list[str]) -> tuple[bool, set[str]]:
    handling_active = False
    handled_branches: set[str] = set()
    for block in blocks:
        marker = _extract_marker_value(block, REPAIR_ONLY_BRANCH_HANDLING_LABEL)
        marker_lower = marker.casefold()
        if (
            marker
            and "repair-only" in marker_lower
            and "does not imply branch readiness admission" in marker_lower
            and "active branch truth" in marker_lower
        ):
            handling_active = True
            for branch_name in FEATURE_REPAIR_BRANCH_RE.findall(marker):
                handled_branches.add(branch_name)
                if branch_name.startswith("origin/"):
                    handled_branches.add(branch_name.removeprefix("origin/"))
                else:
                    handled_branches.add(f"origin/{branch_name}")
    return handling_active, handled_branches


def _require_no_conflicting_marker_values(require, source_name: str, text: str, label: str) -> None:
    cleaned_values = [
        _clean_release_value(value)
        for value in _extract_colon_values(text, label)
        if _clean_release_value(value)
    ]
    unique_values: list[str] = []
    seen: set[str] = set()
    for value in cleaned_values:
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique_values.append(value)
    require(
        len(unique_values) <= 1,
        f"{source_name}: conflicting '{label}' markers found: {', '.join(unique_values)}",
    )


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


def _selected_next_is_current_carrier_branch(
    *,
    selected_next_branch: str,
    current_branch: str,
    selected_block: str,
    roadmap_section: str,
    active_branch_record_text: str,
) -> bool:
    selected_branch = _clean_release_value(selected_next_branch)
    if not current_branch or selected_branch != current_branch:
        return False

    combined_source_truth = "\n".join(
        [selected_block, roadmap_section, active_branch_record_text]
    ).casefold()
    current_carrier_marker = f"current carrier branch: `{current_branch}`".casefold()
    return (
        current_carrier_marker in combined_source_truth
        and "not an uncreated" in combined_source_truth
        and current_branch.casefold() in active_branch_record_text.casefold()
        and "active branch" in active_branch_record_text.casefold()
    )


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
    active_branch_record_text: str,
) -> None:
    current_branch = _git_current_branch()
    if (
        _is_standing_governance_intake_branch(current_branch)
        and STANDING_GOVERNANCE_INTAKE_BRANCH_CLASS in active_branch_record_text
    ):
        return

    def successor_selection_approval_exists() -> bool:
        normalized_record = active_branch_record_text.casefold()
        return any(
            marker in normalized_record
            for marker in (
                "successor selection user approval: granted",
                "selected-next successor selection: approved",
                "user approval for successor selection exists",
            )
        )

    def successor_selection_defer_waiver_exists() -> bool:
        normalized_record = active_branch_record_text.casefold()
        return any(
            marker in normalized_record
            for marker in (
                "next workstream user waiver: granted",
                "selected-next defer user waiver: granted",
                "selected-next user waiver: granted",
                "user-approved selected-next defer",
                "no successor runtime branch by inertia: user-waived",
                "no successor runtime branch by inertia: granted",
            )
        )

    def source_only_no_successor_defer_exists() -> bool:
        normalized_record = active_branch_record_text.casefold()
        explicit_no_successor = any(
            marker in normalized_record
            for marker in (
                "no successor runtime branch by inertia: user-waived",
                "no successor runtime branch by inertia: granted",
                "selected no runtime successor",
            )
        )
        source_only_posture = any(
            marker in normalized_record
            for marker in (
                "source-only",
                "docs-only",
                "source-truth",
                "dev-only source comments",
            )
        )
        pre_pr_or_stage1_pending = any(
            marker in normalized_record
            for marker in (
                "pr creation approval missing",
                "pr readiness stage 1 pending",
                "pr readiness stage 1 remains pending",
                "pr readiness stage 1 approval",
            )
        )
        return (
            explicit_no_successor
            and "no active branch" in normalized_record
            and source_only_posture
            and pre_pr_or_stage1_pending
            and "successor selection user approval: granted" not in normalized_record
        )

    def explicitly_records_no_selected_next(blocker: str) -> bool:
        post_merge_state = _section(active_branch_record_text, "Post-Merge State")
        return (
            blocker in active_branch_record_text
            and "No Active Branch" in post_merge_state
            and "Selected Next Workstream:" in post_merge_state
            and "None" in post_merge_state
            and "Selected Next Implementation Branch:" in post_merge_state
            and "Not created" in post_merge_state
            and "successor" in post_merge_state.casefold()
        )

    selected_entries = _selected_next_workstream_entries(backlog_entries)
    if not selected_entries:
        return

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
    selected_registry_class = _clean_release_value(_extract_colon_value(selected_block, "Registry Class"))
    roadmap_section = _next_workstream_roadmap_section(roadmap_text)
    repair_only_handling, explicitly_handled_repair_branches = _selected_next_repair_only_branch_info(
        [selected_block, roadmap_section]
    )
    selected_next_branch = _extract_colon_value(selected_block, "Selected Next Implementation Branch")
    selected_next_is_current_carrier = _selected_next_is_current_carrier_branch(
        selected_next_branch=selected_next_branch,
        current_branch=current_branch,
        selected_block=selected_block,
        roadmap_section=roadmap_section,
        active_branch_record_text=active_branch_record_text,
    )

    require(
        selected_record_state in VALID_NEXT_WORKSTREAM_RECORD_STATES,
        (
            "PR readiness gate: Next Workstream Undefined blocker is active; "
            f"{selected_id} has invalid Record State '{selected_record_state}'"
        ),
    )
    require(
        selected_registry_class == "Feature Family",
        (
            "PR readiness gate: Next Runtime Candidate Selection Pending blocker is active; "
            f"{selected_id} must be a real runtime Feature Family candidate, not "
            f"Registry Class '{selected_registry_class}'"
        ),
    )
    require(
        bool(selected_scope),
        (
            "PR readiness gate: Next Workstream Undefined blocker is active; "
            f"{selected_id} must define '{NEXT_WORKSTREAM_MINIMAL_SCOPE_LABEL}' in Docs/feature_backlog.md"
        ),
    )
    if selected_scope:
        require(
            "runtime" in selected_scope.casefold(),
            (
                "PR readiness gate: Next Runtime Candidate Selection Pending blocker is active; "
                f"{selected_id} Minimal Scope must explicitly name a runtime slice"
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
        if not repair_only_handling and not selected_next_is_current_carrier:
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
    current_branch_names = {current_branch, f"origin/{current_branch}"} if current_branch else set()
    same_family_successor_not_branched = (
        current_branch
        and _clean_release_value(selected_next_branch).casefold() in {"not created", "deferred to branch readiness"}
        and bool(current_branch_names.intersection(matching_branches))
    )
    non_repair_matching_branches = [
        branch_name
        for branch_name in matching_branches
        if branch_record_class_map.get(branch_name) != EMERGENCY_CANON_REPAIR_BRANCH_CLASS
        and branch_name not in explicitly_handled_repair_branches
        and not (same_family_successor_not_branched and branch_name in current_branch_names)
        and not (selected_next_is_current_carrier and branch_name in current_branch_names)
    ]
    if (
        same_family_successor_not_branched
        or selected_next_is_current_carrier
    ) and not non_repair_matching_branches:
        matching_branches = []
    elif repair_only_handling and not non_repair_matching_branches:
        matching_branches = []
    else:
        if not non_repair_matching_branches and any(
            branch_record_class_map.get(branch_name) == EMERGENCY_CANON_REPAIR_BRANCH_CLASS
            or branch_name in explicitly_handled_repair_branches
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


def _branch_record_bot_review_state(record_text: str) -> tuple[str, str]:
    review_section = _section(record_text, BOT_REVIEW_SIGNAL_HEADING)
    return (
        _extract_marker_value(review_section, BOT_REVIEW_SIGNAL_STATUS_LABEL),
        _extract_marker_value(review_section, BOT_REVIEW_SIGNAL_HEAD_SHA_LABEL),
    )


def _load_json_file(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _phase_status_bot_approval_proven(phase_status_section: str) -> bool:
    marker_value = _extract_marker_value(phase_status_section, "Bot approval proof").strip()
    normalized = marker_value.casefold()
    if normalized in {
        "",
        "pending",
        "not required after same-head comment-addressed closeout.",
        "not required after same-head comment-addressed closeout",
        "comment addressed",
    }:
        return False
    return (
        "approved" in normalized
        or "thumbs-up" in normalized
        or "green approval" in normalized
        or "+1" in normalized
    )


def _phase_status_ordered_bot_approval_proven(phase_status_section: str) -> bool:
    marker_value = _extract_marker_value(phase_status_section, "Bot approval proof").strip()
    normalized = marker_value.casefold()
    if not _phase_status_bot_approval_proven(phase_status_section):
        return False
    if any(
        phrase in normalized
        for phrase in (
            "not approved",
            "not required",
            "no later",
            "without waiting",
            "before repair",
            "before repaired",
            "before current head",
            "predate",
            "pre-repair",
            "older approval",
            "stale approval",
        )
    ):
        return False
    return any(
        phrase in normalized
        for phrase in (
            "after repair",
            "after repaired",
            "after current head",
            "after bot comment",
            "after comment",
            "later approval",
            "later thumbs-up",
            "later +1",
            "post-repair",
            "subsequent approval",
            "subsequent thumbs-up",
            "current-head approval",
            "repaired head",
        )
    )


def _fallback_bot_approval_clears_comment_latch(
    *,
    phase_status_section: str,
    bot_comment_count: int,
    bot_approval: bool,
    bot_approval_ordered: bool = False,
) -> bool:
    if not bot_approval:
        return False
    if bot_comment_count <= 0:
        return True
    return bot_approval_ordered or _phase_status_ordered_bot_approval_proven(
        phase_status_section
    )


def _watcher_fallback_current_head_bot_approval_proven(
    phase_status_section: str,
) -> bool:
    return _phase_status_ordered_bot_approval_proven(phase_status_section)


def _automation_planning_runtime_proof_status(current_head_sha: str) -> tuple[bool, str]:
    if not AUTOMATION_PR99_NATIVE_HEARTBEAT_PATH.is_file():
        return (
            False,
            f"preferred native heartbeat config '{AUTOMATION_PR99_NATIVE_HEARTBEAT_PATH}' is missing",
        )
    if not AUTOMATION_PR99_FALLBACK_SCRIPT_PATH.is_file():
        return (
            False,
            f"bounded fallback helper '{AUTOMATION_PR99_FALLBACK_SCRIPT_PATH}' is missing",
        )
    if not AUTOMATION_PR99_FALLBACK_LATEST_PATH.is_file():
        return (
            False,
            f"fallback latest-status file '{AUTOMATION_PR99_FALLBACK_LATEST_PATH}' is missing",
        )

    state = _load_json_file(AUTOMATION_PR99_FALLBACK_STATE_PATH)
    if not state:
        return (
            False,
            f"fallback state file '{AUTOMATION_PR99_FALLBACK_STATE_PATH}' is missing or invalid",
        )

    recorded_head_sha = str(state.get("headSha") or "")
    if current_head_sha and recorded_head_sha and recorded_head_sha != current_head_sha:
        return (
            False,
            (
                "fallback runtime proof is stale; state-file head "
                f"'{recorded_head_sha}' does not match current head '{current_head_sha}'"
            ),
        )

    if not str(state.get("lastRunLocal") or "").strip():
        return (
            False,
            f"fallback state file '{AUTOMATION_PR99_FALLBACK_STATE_PATH}' is missing lastRunLocal proof",
        )

    return (
        True,
        (
            "bounded fallback runtime proof is present via "
            f"'{AUTOMATION_PR99_FALLBACK_STATE_PATH}' and "
            f"'{AUTOMATION_PR99_FALLBACK_LATEST_PATH}'"
        ),
    )


def _automation_closeout_repair_watcher_proof_status(current_head_sha: str) -> tuple[bool, str]:
    if not AUTOMATION_CLOSEOUT_PR101_WATCHER_SCRIPT_PATH.is_file():
        return (
            False,
            f"bounded fallback watcher '{AUTOMATION_CLOSEOUT_PR101_WATCHER_SCRIPT_PATH}' is missing",
        )
    if not AUTOMATION_CLOSEOUT_PR101_WATCHER_LATEST_PATH.is_file():
        return (
            False,
            f"watcher latest-status file '{AUTOMATION_CLOSEOUT_PR101_WATCHER_LATEST_PATH}' is missing",
        )

    state = _load_json_file(AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH)
    if not state:
        return (
            False,
            f"watcher state file '{AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH}' is missing or invalid",
        )

    recorded_head_sha = str(state.get("localHeadSha") or state.get("headSha") or "")
    if current_head_sha and recorded_head_sha and recorded_head_sha != current_head_sha:
        return (
            False,
            (
                "watcher runtime proof is stale; state-file head "
                f"'{recorded_head_sha}' does not match current head '{current_head_sha}'"
            ),
        )

    if not str(state.get("lastRunLocal") or "").strip():
        return (
            False,
            f"watcher state file '{AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH}' is missing lastRunLocal proof",
        )

    thread_id = str(state.get("threadId") or "").strip()
    thread_rollout_path_raw = str(state.get("threadRolloutPath") or "").strip()
    last_thread_emit_at = str(state.get("lastThreadEmitAt") or "").strip()
    last_thread_emit_message = str(state.get("lastThreadEmitMessage") or "").strip()
    last_thread_emit_method = str(state.get("lastThreadEmitMethod") or "").strip()
    if not thread_id:
        return (
            False,
            f"watcher state file '{AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH}' is missing threadId proof",
        )
    if not thread_rollout_path_raw:
        return (
            False,
            f"watcher state file '{AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH}' is missing threadRolloutPath proof",
        )
    if not last_thread_emit_at or not last_thread_emit_message:
        return (
            False,
            (
                f"watcher state file '{AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH}' is missing "
                "same-thread transcript emission proof"
            ),
        )
    if last_thread_emit_method != "codex_resume":
        return (
            False,
            (
                f"watcher state file '{AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH}' must record "
                "`lastThreadEmitMethod` as `codex_resume`; manual rollout-file injection does not count "
                f"as same-thread proof (found '{last_thread_emit_method or 'missing'}')"
            ),
        )

    thread_rollout_path = Path(thread_rollout_path_raw)
    if not thread_rollout_path.is_file():
        return (
            False,
            f"same-thread rollout transcript '{thread_rollout_path}' is missing",
        )
    try:
        transcript_tail = thread_rollout_path.read_text(encoding="utf-8")[-2_000_000:]
    except OSError as exc:
        return False, f"same-thread rollout transcript '{thread_rollout_path}' could not be read: {exc}"
    if last_thread_emit_message not in transcript_tail:
        return (
            False,
            (
                "same-thread transcript proof is stale; the last emitted watcher message from "
                f"'{AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH}' is not present in "
                f"'{thread_rollout_path}'"
            ),
        )

    heartbeat_proven, heartbeat_message = _automation_last_run_proof(
        AUTOMATION_CLOSEOUT_PR101_THREAD_WATCHER_NAME
    )
    proof_fragments = [
        (
            "same-thread transcript proof is present via "
            f"'{thread_rollout_path}' and '{AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH}' "
            f"on thread '{thread_id}'"
        )
    ]
    if heartbeat_proven:
        proof_fragments.append(heartbeat_message)

    return (
        True,
        "; ".join(proof_fragments),
    )


def _pr101_closeout_canon_repair_watcher_proof_status(
    current_head_sha: str,
) -> tuple[bool, str]:
    if not PR101_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH.is_file():
        return (
            False,
            f"bounded same-thread watcher '{PR101_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH}' is missing",
        )
    if not PR101_CLOSEOUT_CANON_WATCHER_LATEST_PATH.is_file():
        return (
            False,
            f"watcher latest-status file '{PR101_CLOSEOUT_CANON_WATCHER_LATEST_PATH}' is missing",
        )

    state = _load_json_file(PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH)
    if not state:
        return (
            False,
            f"watcher state file '{PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing or invalid",
        )

    recorded_head_sha = str(state.get("localHeadSha") or state.get("headSha") or "")
    if current_head_sha and recorded_head_sha and recorded_head_sha != current_head_sha:
        return (
            False,
            (
                "watcher runtime proof is stale; state-file head "
                f"'{recorded_head_sha}' does not match current head '{current_head_sha}'"
            ),
        )

    if not str(state.get("lastRunLocal") or "").strip():
        return (
            False,
            f"watcher state file '{PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing lastRunLocal proof",
        )

    thread_id = str(state.get("threadId") or "").strip()
    thread_rollout_path_raw = str(state.get("threadRolloutPath") or "").strip()
    last_thread_emit_at = str(state.get("lastThreadEmitAt") or "").strip()
    last_thread_emit_message = str(state.get("lastThreadEmitMessage") or "").strip()
    last_thread_emit_method = str(state.get("lastThreadEmitMethod") or "").strip()
    if not thread_id:
        return (
            False,
            f"watcher state file '{PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing threadId proof",
        )
    if not thread_rollout_path_raw:
        return (
            False,
            f"watcher state file '{PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing threadRolloutPath proof",
        )
    if not last_thread_emit_at or not last_thread_emit_message:
        return (
            False,
            (
                f"watcher state file '{PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing "
                "same-thread transcript emission proof"
            ),
        )
    if last_thread_emit_method != "codex_resume":
        return (
            False,
            (
                f"watcher state file '{PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH}' must record "
                "`lastThreadEmitMethod` as `codex_resume`; manual rollout-file injection does not count "
                f"as same-thread proof (found '{last_thread_emit_method or 'missing'}')"
            ),
        )

    thread_rollout_path = Path(thread_rollout_path_raw)
    if not thread_rollout_path.is_file():
        return (
            False,
            f"same-thread rollout transcript '{thread_rollout_path}' is missing",
        )
    try:
        transcript_tail = thread_rollout_path.read_text(encoding="utf-8")[-2_000_000:]
    except OSError as exc:
        return False, f"same-thread rollout transcript '{thread_rollout_path}' could not be read: {exc}"
    if last_thread_emit_message not in transcript_tail:
        return (
            False,
            (
                "same-thread transcript proof is stale; the last emitted watcher message from "
                f"'{PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is not present in "
                f"'{thread_rollout_path}'"
            ),
        )

    heartbeat_proven, heartbeat_message = _automation_last_run_proof(
        PR101_CLOSEOUT_CANON_THREAD_WATCHER_NAME
    )
    proof_fragments = [
        (
            "same-thread transcript proof is present via "
            f"'{thread_rollout_path}' and '{PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH}' "
            f"on thread '{thread_id}'"
        )
    ]
    if heartbeat_proven:
        proof_fragments.append(heartbeat_message)

    return (
        True,
        "; ".join(proof_fragments),
    )


def _pr102_closeout_canon_repair_watcher_proof_status(
    current_head_sha: str,
) -> tuple[bool, str]:
    if not PR102_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH.is_file():
        return (
            False,
            f"bounded same-thread watcher '{PR102_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH}' is missing",
        )
    if not PR102_CLOSEOUT_CANON_WATCHER_LATEST_PATH.is_file():
        return (
            False,
            f"watcher latest-status file '{PR102_CLOSEOUT_CANON_WATCHER_LATEST_PATH}' is missing",
        )

    state = _load_json_file(PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH)
    if not state:
        return (
            False,
            f"watcher state file '{PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing or invalid",
        )

    recorded_head_sha = str(state.get("localHeadSha") or state.get("headSha") or "")
    if current_head_sha and recorded_head_sha and recorded_head_sha != current_head_sha:
        return (
            False,
            (
                "watcher runtime proof is stale; state-file head "
                f"'{recorded_head_sha}' does not match current head '{current_head_sha}'"
            ),
        )

    if not str(state.get("lastRunLocal") or "").strip():
        return (
            False,
            f"watcher state file '{PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing lastRunLocal proof",
        )

    thread_id = str(state.get("threadId") or "").strip()
    thread_rollout_path_raw = str(state.get("threadRolloutPath") or "").strip()
    last_thread_emit_at = str(state.get("lastThreadEmitAt") or "").strip()
    last_thread_emit_message = str(state.get("lastThreadEmitMessage") or "").strip()
    last_thread_emit_method = str(state.get("lastThreadEmitMethod") or "").strip()
    if not thread_id:
        return (
            False,
            f"watcher state file '{PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing threadId proof",
        )
    if not thread_rollout_path_raw:
        return (
            False,
            f"watcher state file '{PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing threadRolloutPath proof",
        )
    if not last_thread_emit_at or not last_thread_emit_message:
        return (
            False,
            (
                f"watcher state file '{PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing "
                "same-thread transcript emission proof"
            ),
        )
    if last_thread_emit_method != "codex_resume":
        return (
            False,
            (
                f"watcher state file '{PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH}' must record "
                "`lastThreadEmitMethod` as `codex_resume`; manual rollout-file injection does not count "
                f"as same-thread proof (found '{last_thread_emit_method or 'missing'}')"
            ),
        )

    thread_rollout_path = Path(thread_rollout_path_raw)
    if not thread_rollout_path.is_file():
        return (
            False,
            f"same-thread rollout transcript '{thread_rollout_path}' is missing",
        )
    try:
        transcript_tail = thread_rollout_path.read_text(encoding="utf-8")[-2_000_000:]
    except OSError as exc:
        return False, f"same-thread rollout transcript '{thread_rollout_path}' could not be read: {exc}"
    if last_thread_emit_message not in transcript_tail:
        return (
            False,
            (
                "same-thread transcript proof is stale; the last emitted watcher message from "
                f"'{PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is not present in "
                f"'{thread_rollout_path}'"
            ),
        )

    heartbeat_proven, heartbeat_message = _automation_last_run_proof(
        PR102_CLOSEOUT_CANON_THREAD_WATCHER_NAME
    )
    proof_fragments = [
        (
            "same-thread transcript proof is present via "
            f"'{thread_rollout_path}' and '{PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH}' "
            f"on thread '{thread_id}'"
        )
    ]
    if heartbeat_proven:
        proof_fragments.append(heartbeat_message)

    return (
        True,
        "; ".join(proof_fragments),
    )


def _pr103_closeout_canon_repair_watcher_proof_status(
    current_head_sha: str,
) -> tuple[bool, str]:
    if not PR103_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH.is_file():
        return (
            False,
            f"bounded same-thread watcher '{PR103_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH}' is missing",
        )
    if not PR103_CLOSEOUT_CANON_WATCHER_LATEST_PATH.is_file():
        return (
            False,
            f"watcher latest-status file '{PR103_CLOSEOUT_CANON_WATCHER_LATEST_PATH}' is missing",
        )

    state = _load_json_file(PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH)
    if not state:
        return (
            False,
            f"watcher state file '{PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing or invalid",
        )

    recorded_head_sha = str(state.get("localHeadSha") or state.get("headSha") or "")
    if current_head_sha and recorded_head_sha and recorded_head_sha != current_head_sha:
        return (
            False,
            (
                "watcher runtime proof is stale; state-file head "
                f"'{recorded_head_sha}' does not match current head '{current_head_sha}'"
            ),
        )

    if not str(state.get("lastRunLocal") or "").strip():
        return (
            False,
            f"watcher state file '{PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing lastRunLocal proof",
        )

    thread_id = str(state.get("threadId") or "").strip()
    thread_rollout_path_raw = str(state.get("threadRolloutPath") or "").strip()
    last_thread_emit_at = str(state.get("lastThreadEmitAt") or "").strip()
    last_thread_emit_message = str(state.get("lastThreadEmitMessage") or "").strip()
    last_thread_emit_method = str(state.get("lastThreadEmitMethod") or "").strip()
    if not thread_id:
        return (
            False,
            f"watcher state file '{PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing threadId proof",
        )
    if not thread_rollout_path_raw:
        return (
            False,
            f"watcher state file '{PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing threadRolloutPath proof",
        )
    if not last_thread_emit_at or not last_thread_emit_message:
        return (
            False,
            (
                f"watcher state file '{PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is missing "
                "same-thread transcript emission proof"
            ),
        )
    if last_thread_emit_method != "codex_resume":
        return (
            False,
            (
                f"watcher state file '{PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH}' must record "
                "`lastThreadEmitMethod` as `codex_resume`; manual rollout-file injection does not count "
                f"as same-thread proof (found '{last_thread_emit_method or 'missing'}')"
            ),
        )

    thread_rollout_path = Path(thread_rollout_path_raw)
    if not thread_rollout_path.is_file():
        return (
            False,
            f"same-thread rollout transcript '{thread_rollout_path}' is missing",
        )
    try:
        transcript_tail = thread_rollout_path.read_text(encoding="utf-8")[-2_000_000:]
    except OSError as exc:
        return False, f"same-thread rollout transcript '{thread_rollout_path}' could not be read: {exc}"
    if last_thread_emit_message not in transcript_tail:
        return (
            False,
            (
                "same-thread transcript proof is stale; the last emitted watcher message from "
                f"'{PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH}' is not present in "
                f"'{thread_rollout_path}'"
            ),
        )

    heartbeat_proven, heartbeat_message = _automation_last_run_proof(
        PR103_CLOSEOUT_CANON_THREAD_WATCHER_NAME
    )
    proof_fragments = [
        (
            "same-thread transcript proof is present via "
            f"'{thread_rollout_path}' and '{PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH}' "
            f"on thread '{thread_id}'"
        )
    ]
    if heartbeat_proven:
        proof_fragments.append(heartbeat_message)

    return (
        True,
        "; ".join(proof_fragments),
    )


def _automation_last_run_proof(automation_name: str) -> tuple[bool, str]:
    if not CODEX_AUTOMATION_DB_PATH.is_file():
        return False, f"automation state database '{CODEX_AUTOMATION_DB_PATH}' is missing"
    connection = None
    try:
        connection = sqlite3.connect(CODEX_AUTOMATION_DB_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, status, last_run_at FROM automations WHERE name = ? ORDER BY updated_at DESC LIMIT 1",
            (automation_name,),
        )
        automation_row = cursor.fetchone()
        if automation_row is None:
            return False, f"same-thread watcher automation '{automation_name}' is missing"
        automation_id = str(automation_row["id"] or "").strip()
        status = str(automation_row["status"] or "").strip()
        last_run_at = automation_row["last_run_at"]
        cursor.execute(
            "SELECT thread_id, updated_at FROM automation_runs WHERE automation_id = ? ORDER BY updated_at DESC LIMIT 1",
            (automation_id,),
        )
        latest_run = cursor.fetchone()
    except sqlite3.Error as exc:
        return False, f"automation state inspection failed for '{automation_name}': {exc}"
    finally:
        try:
            connection.close()
        except Exception:
            pass

    if status != "ACTIVE":
        return False, f"same-thread watcher automation '{automation_name}' is not ACTIVE"
    automation_toml = Path.home() / ".codex" / "automations" / automation_id / "automation.toml"
    if not automation_toml.is_file():
        return False, f"same-thread watcher automation '{automation_name}' is missing '{automation_toml}'"
    automation_text = automation_toml.read_text(encoding="utf-8")
    if 'kind = "heartbeat"' not in automation_text:
        return False, f"same-thread watcher automation '{automation_name}' is not a heartbeat automation"
    if 'target_thread_id = "' not in automation_text:
        return False, f"same-thread watcher automation '{automation_name}' is not bound to a thread"
    if last_run_at is None and latest_run is None:
        return (
            False,
            f"same-thread watcher automation '{automation_name}' has no scheduler last-run or automation-run proof yet",
        )
    run_timestamp = latest_run["updated_at"] if latest_run is not None else last_run_at
    thread_id = str(latest_run["thread_id"] or "").strip() if latest_run is not None else "unknown"
    return (
        True,
        f"same-thread watcher automation '{automation_name}' has scheduler last-run proof at '{run_timestamp}' on thread '{thread_id}'",
    )


def _watcher_route_alignment_status(
    *,
    branch_record_text: str,
    watcher_script_path: Path,
    watcher_state_path: Path,
) -> tuple[bool, str]:
    phase_status_section = _section(branch_record_text, "Phase Status")
    reporting_surface = _extract_marker_value(phase_status_section, "PR watcher reporting surface")
    expected_thread_id = _extract_marker_value(phase_status_section, "PR watcher reporting thread ID")
    expected_rollout_path_raw = _extract_marker_value(
        phase_status_section, "PR watcher reporting transcript"
    )
    route_verification = _extract_marker_value(phase_status_section, "PR watcher route verification")

    if not reporting_surface:
        return False, "active branch record is missing `PR watcher reporting surface`"
    if not expected_thread_id:
        return False, "active branch record is missing `PR watcher reporting thread ID`"
    if not expected_rollout_path_raw:
        return False, "active branch record is missing `PR watcher reporting transcript`"
    if "PASS" not in route_verification:
        return (
            False,
            "active branch record is missing a `PR watcher route verification` PASS marker",
        )

    state = _load_json_file(watcher_state_path)
    if not state:
        return False, f"watcher state file '{watcher_state_path}' is missing or invalid"

    state_thread_id = str(state.get("threadId") or "").strip()
    state_rollout_path_raw = str(state.get("threadRolloutPath") or "").strip()
    if state_thread_id != expected_thread_id:
        return (
            False,
            (
                "watcher state route is pointed at the wrong thread; state-file thread "
                f"'{state_thread_id or 'missing'}' does not match recorded thread "
                f"'{expected_thread_id}'"
            ),
        )
    if Path(state_rollout_path_raw) != Path(expected_rollout_path_raw):
        return (
            False,
            (
                "watcher state route is pointed at the wrong transcript; state-file transcript "
                f"'{state_rollout_path_raw or 'missing'}' does not match recorded transcript "
                f"'{expected_rollout_path_raw}'"
            ),
        )

    if not watcher_script_path.is_file():
        return False, f"watcher wrapper '{watcher_script_path}' is missing"
    try:
        script_text = watcher_script_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"watcher wrapper '{watcher_script_path}' could not be read: {exc}"
    thread_route_markers = (
        f"--thread-id '{expected_thread_id}'",
        f'"--thread-id", "{expected_thread_id}"',
        f"'--thread-id', '{expected_thread_id}'",
        f'"{expected_thread_id}"',
    )
    if not any(marker in script_text for marker in thread_route_markers):
        return (
            False,
            (
                f"watcher wrapper '{watcher_script_path}' is not pointed at recorded thread "
                f"'{expected_thread_id}'"
            ),
        )
    rollout_route_markers = (
        f"--thread-rollout-path '{expected_rollout_path_raw}'",
        f'"--thread-rollout-path", r"{expected_rollout_path_raw}"',
        f'"--thread-rollout-path", "{expected_rollout_path_raw}"',
        f"'--thread-rollout-path', '{expected_rollout_path_raw}'",
        expected_rollout_path_raw,
    )
    if not any(marker in script_text for marker in rollout_route_markers):
        return (
            False,
            (
                f"watcher wrapper '{watcher_script_path}' is not pointed at recorded transcript "
                f"'{expected_rollout_path_raw}'"
            ),
        )

    if not CODEX_THREAD_STATE_DB_PATH.is_file():
        return False, f"Codex thread database '{CODEX_THREAD_STATE_DB_PATH}' is missing"
    connection = None
    try:
        connection = sqlite3.connect(CODEX_THREAD_STATE_DB_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            "SELECT rollout_path FROM threads WHERE id = ?",
            (expected_thread_id,),
        )
        row = cursor.fetchone()
    except sqlite3.Error as exc:
        return False, f"Codex thread-route inspection failed: {exc}"
    finally:
        try:
            connection.close()
        except Exception:
            pass
    if row is None:
        return False, f"recorded watcher thread '{expected_thread_id}' is missing from Codex thread state"
    db_rollout_path_raw = str(row["rollout_path"] or "").strip()
    if Path(db_rollout_path_raw) != Path(expected_rollout_path_raw):
        return (
            False,
            (
                "Codex thread state points at the wrong transcript; thread-db transcript "
                f"'{db_rollout_path_raw or 'missing'}' does not match recorded transcript "
                f"'{expected_rollout_path_raw}'"
            ),
        )

    expected_rollout_path = Path(expected_rollout_path_raw)
    if not expected_rollout_path.is_file():
        return False, f"recorded watcher transcript '{expected_rollout_path}' is missing"
    try:
        transcript_tail = expected_rollout_path.read_text(encoding="utf-8")[-2_000_000:]
    except OSError as exc:
        return False, f"recorded watcher transcript '{expected_rollout_path}' could not be read: {exc}"
    branch_name = _extract_marker_value(_section(branch_record_text, "Branch Identity"), "Branch")
    if branch_name and branch_name not in transcript_tail:
        return (
            False,
            (
                "recorded watcher transcript does not prove it is the active working thread; "
                f"branch '{branch_name}' is absent from '{expected_rollout_path}'"
            ),
        )

    return (
        True,
        (
            f"watcher reporting surface '{reporting_surface}' is explicitly recorded and the "
            f"wrapper/state/thread-db route agrees on thread '{expected_thread_id}', and the "
            "transcript contains the active branch marker"
        ),
    )


def _automation_planning_fallback_pr_view_for_branch(
    branch_name: str,
) -> tuple[dict[str, object] | None, str]:
    if not _is_automation_planning_branch(branch_name):
        return None, ""

    state = _load_json_file(AUTOMATION_PR99_FALLBACK_STATE_PATH)
    if not state:
        return None, (
            f"automation fallback state file '{AUTOMATION_PR99_FALLBACK_STATE_PATH}' "
            "is missing or invalid"
        )

    repository_full_name, repository_error = _git_origin_repository_full_name()
    if repository_error:
        return None, repository_error

    mergeable_value = str(state.get("mergeable") or "").casefold()
    if mergeable_value == "true":
        mergeable = "MERGEABLE"
        merge_state = "CLEAN"
    elif mergeable_value == "false":
        mergeable = "CONFLICTING"
        merge_state = "DIRTY"
    else:
        mergeable = "UNKNOWN"
        merge_state = "UNKNOWN"

    state_value = str(state.get("state") or "").upper() or "UNKNOWN"
    if bool(state.get("merged")) and state_value != "CLOSED":
        state_value = "CLOSED"

    bot_approval = bool(state.get("botApproval"))
    bot_comment_count = int(state.get("botCommentCount") or 0)
    return {
        "id": "",
        "number": 99,
        "state": state_value,
        "mergeable": mergeable,
        "mergeStateStatus": merge_state,
        "reviewDecision": "APPROVED" if bot_approval else "",
        "isDraft": bool(state.get("draft")),
        "headRefName": branch_name,
        "baseRefName": "main",
        "title": "Automation Catalog",
        "url": f"https://github.com/{repository_full_name}/pull/99",
        "repositoryFullName": repository_full_name,
        "fallbackLocalState": True,
        "botApproval": bot_approval,
        "botApprovalOrdered": False,
        "botCommentCount": bot_comment_count,
    }, ""


def _automation_closeout_repair_fallback_pr_view_for_branch(
    branch_name: str,
    active_branch_record_text: str,
) -> tuple[dict[str, object] | None, str]:
    if not _is_automation_closeout_repair_branch(branch_name):
        return None, ""
    if not active_branch_record_text:
        return None, "active branch record text is unavailable"

    repository_full_name, repository_error = _git_origin_repository_full_name()
    if repository_error:
        return None, repository_error

    phase_status_section = _section(active_branch_record_text, "Phase Status")
    pr_url_match = re.search(r"^- Live PR:\s*`([^`]+)`", phase_status_section, flags=re.M)
    if not pr_url_match:
        pr_url_match = re.search(r"^- PR URL:\s*`([^`]+)`", active_branch_record_text, flags=re.M)
    pr_url = pr_url_match.group(1).strip() if pr_url_match else ""
    if not pr_url:
        return None, "active branch record is missing `Live PR` or `PR URL`"
    pr_number_match = re.search(r"/pull/(\d+)", pr_url)
    pr_number = int(pr_number_match.group(1)) if pr_number_match else 101
    watcher_state = _load_json_file(AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH) or {}
    bot_approval_ordered = _watcher_fallback_current_head_bot_approval_proven(
        phase_status_section
    )
    bot_approval = bot_approval_ordered
    bot_comment_count = int(watcher_state.get("botCommentCount") or 0)
    merged = bool(watcher_state.get("merged"))
    state_value = str(watcher_state.get("prState") or "OPEN").upper()
    if merged and state_value != "CLOSED":
        state_value = "CLOSED"
    mergeable_value = watcher_state.get("mergeable")
    if mergeable_value is True:
        mergeable = "MERGEABLE"
        merge_state = "CLEAN"
    elif mergeable_value is False:
        mergeable = "CONFLICTING"
        merge_state = "DIRTY"
    else:
        mergeable = "UNKNOWN"
        merge_state = "UNKNOWN"

    return {
        "id": "",
        "number": pr_number,
        "state": state_value,
        "mergeable": mergeable,
        "mergeStateStatus": merge_state,
        "reviewDecision": "APPROVED" if bot_approval else "",
        "isDraft": False,
        "headRefName": branch_name,
        "baseRefName": "main",
        "title": "PR100 Post-Merge Closeout Repair",
        "url": pr_url,
        "repositoryFullName": repository_full_name,
        "fallbackLocalState": True,
        "botApproval": bot_approval,
        "botApprovalOrdered": bot_approval_ordered,
        "botCommentCount": bot_comment_count,
    }, ""


def _pr101_closeout_canon_repair_fallback_pr_view_for_branch(
    branch_name: str,
    active_branch_record_text: str,
) -> tuple[dict[str, object] | None, str]:
    if not _is_pr101_closeout_canon_repair_branch(branch_name):
        return None, ""
    if not active_branch_record_text:
        return None, "active branch record text is unavailable"

    repository_full_name, repository_error = _git_origin_repository_full_name()
    if repository_error:
        return None, repository_error

    phase_status_section = _section(active_branch_record_text, "Phase Status")
    pr_url_match = re.search(r"^- Live PR:\s*`([^`]+)`", phase_status_section, flags=re.M)
    if not pr_url_match:
        pr_url_match = re.search(r"^- PR URL:\s*`([^`]+)`", active_branch_record_text, flags=re.M)
    pr_url = pr_url_match.group(1).strip() if pr_url_match else ""
    if not pr_url:
        return None, "active branch record is missing `Live PR` or `PR URL`"
    pr_number_match = re.search(r"/pull/(\d+)", pr_url)
    if not pr_number_match:
        return None, f"active branch record has an invalid Live PR URL '{pr_url}'"
    pr_number = int(pr_number_match.group(1))
    watcher_state = _load_json_file(PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH) or {}
    bot_approval_ordered = _watcher_fallback_current_head_bot_approval_proven(
        phase_status_section
    )
    bot_approval = bot_approval_ordered
    bot_comment_count = int(watcher_state.get("botCommentCount") or 0)
    merged = bool(watcher_state.get("merged"))
    state_value = str(watcher_state.get("prState") or "OPEN").upper()
    if merged and state_value != "CLOSED":
        state_value = "CLOSED"
    mergeable_value = watcher_state.get("mergeable")
    if mergeable_value is True:
        mergeable = "MERGEABLE"
        merge_state = "CLEAN"
    elif mergeable_value is False:
        mergeable = "CONFLICTING"
        merge_state = "DIRTY"
    else:
        mergeable = "UNKNOWN"
        merge_state = "UNKNOWN"

    return {
        "id": "",
        "number": pr_number,
        "state": state_value,
        "mergeable": mergeable,
        "mergeStateStatus": merge_state,
        "reviewDecision": "APPROVED" if bot_approval else "",
        "isDraft": False,
        "headRefName": branch_name,
        "baseRefName": "main",
        "title": "PR101 Post-Merge Closeout Canon Repair",
        "url": pr_url,
        "repositoryFullName": repository_full_name,
        "fallbackLocalState": True,
        "botApproval": bot_approval,
        "botApprovalOrdered": bot_approval_ordered,
        "botCommentCount": bot_comment_count,
    }, ""


def _pr102_closeout_canon_repair_fallback_pr_view_for_branch(
    branch_name: str,
    active_branch_record_text: str,
) -> tuple[dict[str, object] | None, str]:
    if not _is_pr102_closeout_canon_repair_branch(branch_name):
        return None, ""
    if not active_branch_record_text:
        return None, "active branch record text is unavailable"

    repository_full_name, repository_error = _git_origin_repository_full_name()
    if repository_error:
        return None, repository_error

    phase_status_section = _section(active_branch_record_text, "Phase Status")
    pr_url_match = re.search(r"^- Live PR:\s*`([^`]+)`", phase_status_section, flags=re.M)
    pr_url = pr_url_match.group(1).strip() if pr_url_match else ""
    if not pr_url:
        return None, "active branch record is missing `Live PR`"
    pr_number_match = re.search(r"/pull/(\d+)", pr_url)
    if not pr_number_match:
        return None, f"active branch record has an invalid Live PR URL '{pr_url}'"
    pr_number = int(pr_number_match.group(1))
    watcher_state = _load_json_file(PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH) or {}
    bot_approval_ordered = _watcher_fallback_current_head_bot_approval_proven(
        phase_status_section
    )
    bot_approval = bot_approval_ordered
    bot_comment_count = int(watcher_state.get("botCommentCount") or 0)
    merged = bool(watcher_state.get("merged"))
    state_value = str(watcher_state.get("prState") or "OPEN").upper()
    if merged and state_value != "CLOSED":
        state_value = "CLOSED"
    mergeable_value = watcher_state.get("mergeable")
    if mergeable_value is True:
        mergeable = "MERGEABLE"
        merge_state = "CLEAN"
    elif mergeable_value is False:
        mergeable = "CONFLICTING"
        merge_state = "DIRTY"
    else:
        mergeable = "UNKNOWN"
        merge_state = "UNKNOWN"

    return {
        "id": "",
        "number": pr_number,
        "state": state_value,
        "mergeable": mergeable,
        "mergeStateStatus": merge_state,
        "reviewDecision": "APPROVED" if bot_approval else "",
        "isDraft": False,
        "headRefName": branch_name,
        "baseRefName": "main",
        "title": "PR102 Post-Merge Closeout Canon Repair",
        "url": pr_url,
        "repositoryFullName": repository_full_name,
        "fallbackLocalState": True,
        "botApproval": bot_approval,
        "botApprovalOrdered": bot_approval_ordered,
        "botCommentCount": bot_comment_count,
    }, ""


def _pr103_closeout_canon_repair_fallback_pr_view_for_branch(
    branch_name: str,
    active_branch_record_text: str,
) -> tuple[dict[str, object] | None, str]:
    if not _is_pr103_closeout_canon_repair_branch(branch_name):
        return None, ""
    if not active_branch_record_text:
        return None, "active branch record text is unavailable"

    repository_full_name, repository_error = _git_origin_repository_full_name()
    if repository_error:
        return None, repository_error

    phase_status_section = _section(active_branch_record_text, "Phase Status")
    pr_url_match = re.search(r"^- Live PR:\s*`([^`]+)`", phase_status_section, flags=re.M)
    pr_url = pr_url_match.group(1).strip() if pr_url_match else ""
    if not pr_url:
        return None, "active branch record is missing `Live PR`"
    pr_number_match = re.search(r"/pull/(\d+)", pr_url)
    if not pr_number_match:
        return None, f"active branch record has an invalid Live PR URL '{pr_url}'"
    pr_number = int(pr_number_match.group(1))
    watcher_state = _load_json_file(PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH) or {}
    bot_approval_ordered = _watcher_fallback_current_head_bot_approval_proven(
        phase_status_section
    )
    bot_approval = bot_approval_ordered
    bot_comment_count = int(watcher_state.get("botCommentCount") or 0)
    merged = bool(watcher_state.get("merged"))
    state_value = str(watcher_state.get("prState") or "OPEN").upper()
    if merged and state_value != "CLOSED":
        state_value = "CLOSED"
    mergeable_value = watcher_state.get("mergeable")
    if mergeable_value is True:
        mergeable = "MERGEABLE"
        merge_state = "CLEAN"
    elif mergeable_value is False:
        mergeable = "CONFLICTING"
        merge_state = "DIRTY"
    else:
        mergeable = "UNKNOWN"
        merge_state = "UNKNOWN"

    return {
        "id": "",
        "number": pr_number,
        "state": state_value,
        "mergeable": mergeable,
        "mergeStateStatus": merge_state,
        "reviewDecision": "APPROVED" if bot_approval else "",
        "isDraft": False,
        "headRefName": branch_name,
        "baseRefName": "main",
        "title": "PR103 Post-Merge Closeout Canon Repair",
        "url": pr_url,
        "repositoryFullName": repository_full_name,
        "fallbackLocalState": True,
        "botApproval": bot_approval,
        "botApprovalOrdered": bot_approval_ordered,
        "botCommentCount": bot_comment_count,
    }, ""


def _active_branch_watcher_state_path(active_branch_record_text: str) -> Path | None:
    match = re.search(
        r"\$CODEX_HOME/watchers/([^`,]+-state\.json)",
        active_branch_record_text,
    )
    if not match:
        return None
    return Path.home() / ".codex" / "watchers" / match.group(1)


def _active_branch_watcher_fallback_pr_view_for_branch(
    branch_name: str,
    active_branch_record_text: str,
) -> tuple[dict[str, object] | None, str]:
    if not active_branch_record_text:
        return None, "active branch record text is unavailable"

    repository_full_name, repository_error = _git_origin_repository_full_name()
    if repository_error:
        return None, repository_error

    phase_status_section = _section(active_branch_record_text, "Phase Status")
    pr_url_match = re.search(r"^- Live PR:\s*`([^`]+)`", phase_status_section, flags=re.M)
    if not pr_url_match:
        pr_url_match = re.search(r"^- PR URL:\s*`([^`]+)`", active_branch_record_text, flags=re.M)
    pr_url = pr_url_match.group(1).strip() if pr_url_match else ""
    if not pr_url:
        return None, "active branch record is missing `Live PR` or `PR URL`"
    pr_number_match = re.search(r"/pull/(\d+)", pr_url)
    if not pr_number_match:
        return None, f"active branch record has an invalid Live PR URL '{pr_url}'"
    watcher_state_path = _active_branch_watcher_state_path(active_branch_record_text)
    if watcher_state_path is None:
        return None, "active branch record is missing same-thread watcher state proof"
    watcher_state = _load_json_file(watcher_state_path) or {}
    if not watcher_state:
        return None, f"same-thread watcher state file '{watcher_state_path}' is missing or invalid"
    state_branch = str(watcher_state.get("headRef") or "")
    if state_branch and state_branch != branch_name:
        return None, (
            f"same-thread watcher state file '{watcher_state_path}' targets '{state_branch}', "
            f"not current branch '{branch_name}'"
        )

    bot_approval_ordered = _watcher_fallback_current_head_bot_approval_proven(
        phase_status_section
    )
    bot_approval = bot_approval_ordered
    bot_comment_count = int(watcher_state.get("botCommentCount") or 0)
    merged = bool(watcher_state.get("merged"))
    state_value = str(watcher_state.get("prState") or "OPEN").upper()
    if merged and state_value != "CLOSED":
        state_value = "CLOSED"
    mergeable_value = watcher_state.get("mergeable")
    if mergeable_value is True:
        mergeable = "MERGEABLE"
        merge_state = str(watcher_state.get("mergeableState") or "CLEAN").upper()
    elif mergeable_value is False:
        mergeable = "CONFLICTING"
        merge_state = str(watcher_state.get("mergeableState") or "DIRTY").upper()
    else:
        mergeable = "UNKNOWN"
        merge_state = str(watcher_state.get("mergeableState") or "UNKNOWN").upper()

    return {
        "id": "",
        "number": int(pr_number_match.group(1)),
        "state": state_value,
        "mergeable": mergeable,
        "mergeStateStatus": merge_state,
        "reviewDecision": "APPROVED" if bot_approval else "",
        "isDraft": bool(watcher_state.get("draft")),
        "headRefName": state_branch or branch_name,
        "baseRefName": str(watcher_state.get("baseRef") or "main"),
        "title": str(watcher_state.get("title") or ""),
        "url": pr_url,
        "repositoryFullName": repository_full_name,
        "fallbackLocalState": True,
        "botApproval": bot_approval,
        "botApprovalOrdered": bot_approval_ordered,
        "botCommentCount": bot_comment_count,
    }, ""


def _pre_pr_stage1_state_allows_missing_live_pr(
    active_branch_record_text: str,
    pr_error: str,
) -> bool:
    normalized_record = active_branch_record_text.casefold()
    normalized_error = pr_error.casefold()
    no_pr_error = (
        "no pull requests found" in normalized_error
        or "no open pull request" in normalized_error
        or "active branch record is missing `live pr` or `pr url`" in normalized_error
    )
    stage1_context_recorded = any(
        marker in normalized_record
        for marker in (
            "pr readiness stage 1",
            "stage 1 ready for stage 2",
            "stage 1 user waiver required",
        )
    )
    pre_pr_state_recorded = (
        (
            "pre-pr live state:" in normalized_record
            and "no live pr" in normalized_record
        )
        or "pre-pr live state: `no live pr`" in normalized_record
        or (
            "pr creation approval missing" in normalized_record
            and "live pr state: `open`" not in normalized_record
        )
    )
    creation_pending_recorded = any(
        marker in normalized_record
        for marker in (
            "pr creation approval missing",
            "pr creation approval: pending",
            "pr creation approval: `pending",
            "stage 2 pr creation: pending",
            "stage 2 pr creation: `pending",
            "pr readiness execution user approval missing",
        )
    )
    return (
        no_pr_error
        and stage1_context_recorded
        and pre_pr_state_recorded
        and creation_pending_recorded
    )


def _run_pr_live_state_gate(
    require,
    *,
    active_branch_record_path: str = "",
    active_branch_record_text: str = "",
) -> None:
    branch_name = _git_current_branch()
    require(
        bool(branch_name),
        "PR readiness gate: PR State Unknown blocker is active; current branch could not be determined",
    )
    if not branch_name:
        return

    pr_info, pr_error = _gh_pr_view_for_branch(branch_name)
    if not pr_info and _is_automation_closeout_repair_branch(branch_name):
        pr_info, pr_error = _automation_closeout_repair_fallback_pr_view_for_branch(
            branch_name,
            active_branch_record_text,
        )
    if not pr_info and _is_pr101_closeout_canon_repair_branch(branch_name):
        pr_info, pr_error = _pr101_closeout_canon_repair_fallback_pr_view_for_branch(
            branch_name,
            active_branch_record_text,
        )
    if not pr_info and _is_pr102_closeout_canon_repair_branch(branch_name):
        pr_info, pr_error = _pr102_closeout_canon_repair_fallback_pr_view_for_branch(
            branch_name,
            active_branch_record_text,
        )
    if not pr_info and _is_pr103_closeout_canon_repair_branch(branch_name):
        pr_info, pr_error = _pr103_closeout_canon_repair_fallback_pr_view_for_branch(
            branch_name,
            active_branch_record_text,
        )
    if (
        not pr_info
        and _pre_pr_stage1_state_allows_missing_live_pr(
            active_branch_record_text,
            pr_error,
        )
    ):
        return
    if not pr_info:
        pr_info, pr_error = _active_branch_watcher_fallback_pr_view_for_branch(
            branch_name,
            active_branch_record_text,
        )
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
    pr_head_oid = str(pr_info.get("headRefOid") or "")
    pr_base = str(pr_info.get("baseRefName") or "")
    mergeable = str(pr_info.get("mergeable") or "")
    merge_state = str(pr_info.get("mergeStateStatus") or "")
    review_decision = str(pr_info.get("reviewDecision") or "")
    repository_full_name = str(pr_info.get("repositoryFullName") or "")
    fallback_local_state = bool(pr_info.get("fallbackLocalState"))
    fallback_bot_approval = bool(pr_info.get("botApproval"))
    fallback_bot_approval_ordered = bool(pr_info.get("botApprovalOrdered"))
    fallback_bot_comment_count = int(pr_info.get("botCommentCount") or 0)
    if (
        pr_state != "OPEN"
        and _pre_pr_stage1_state_allows_missing_live_pr(
            active_branch_record_text,
            "no open pull request",
        )
        and "historical merge proof" in active_branch_record_text.casefold()
    ):
        return
    if (
        repository_full_name
        and not fallback_local_state
        and (not mergeable or mergeable == "UNKNOWN" or not merge_state or merge_state == "UNKNOWN")
    ):
        rest_pr_info, rest_pr_error = _github_rest_pr_view_for_branch(branch_name, repository_full_name)
        if rest_pr_info and not rest_pr_error:
            pr_info = rest_pr_info
            pr_url = str(pr_info.get("url") or pr_url)
            pr_state = str(pr_info.get("state") or pr_state)
            pr_head = str(pr_info.get("headRefName") or pr_head)
            pr_head_oid = str(pr_info.get("headRefOid") or pr_head_oid)
            pr_base = str(pr_info.get("baseRefName") or pr_base)
            mergeable = str(pr_info.get("mergeable") or mergeable)
            merge_state = str(pr_info.get("mergeStateStatus") or merge_state)
            review_decision = str(pr_info.get("reviewDecision") or review_decision)
            fallback_local_state = bool(pr_info.get("fallbackLocalState"))
            fallback_bot_approval = bool(pr_info.get("botApproval"))
            fallback_bot_approval_ordered = bool(pr_info.get("botApprovalOrdered"))
            fallback_bot_comment_count = int(pr_info.get("botCommentCount") or 0)
    current_head_sha = _git_head_sha()
    recorded_bot_review_status, recorded_bot_review_head = _branch_record_bot_review_state(
        active_branch_record_text
    )
    phase_status_section = _section(active_branch_record_text, "Phase Status")
    current_pr_readiness_seam = _extract_marker_value(
        phase_status_section, "Current PR Readiness Seam"
    )
    if _is_automation_planning_branch(branch_name):
        runtime_proven, runtime_proof_message = _automation_planning_runtime_proof_status(
            current_head_sha
        )
        require(
            runtime_proven,
            (
                "PR readiness gate: Automation Runtime Unproven blocker is active; "
                f"{runtime_proof_message}"
            ),
        )
    if _is_automation_closeout_repair_branch(branch_name):
        watcher_proven, watcher_proof_message = _automation_closeout_repair_watcher_proof_status(
            current_head_sha
        )
        require(
            watcher_proven,
            (
                "PR readiness gate: PR Watcher Provisioning Unproven blocker is active; "
                f"{watcher_proof_message}"
            ),
        )
        closeout_watcher_state = _load_json_file(AUTOMATION_CLOSEOUT_PR101_WATCHER_STATE_PATH)
    elif _is_pr101_closeout_canon_repair_branch(branch_name):
        watcher_proven, watcher_proof_message = _pr101_closeout_canon_repair_watcher_proof_status(
            current_head_sha
        )
        require(
            watcher_proven,
            (
                "PR readiness gate: PR Watcher Provisioning Unproven blocker is active; "
                f"{watcher_proof_message}"
            ),
        )
        closeout_watcher_state = _load_json_file(PR101_CLOSEOUT_CANON_WATCHER_STATE_PATH)
    elif _is_pr102_closeout_canon_repair_branch(branch_name):
        watcher_proven, watcher_proof_message = _pr102_closeout_canon_repair_watcher_proof_status(
            current_head_sha
        )
        require(
            watcher_proven,
            (
                "PR readiness gate: PR Watcher Provisioning Unproven blocker is active; "
                f"{watcher_proof_message}"
            ),
        )
        watcher_route_proven, watcher_route_message = _watcher_route_alignment_status(
            branch_record_text=active_branch_record_text,
            watcher_script_path=PR102_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH,
            watcher_state_path=PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH,
        )
        require(
            watcher_route_proven,
            (
                "PR readiness gate: PR Watcher Routing Unverified blocker is active; "
                f"{watcher_route_message}"
            ),
        )
        closeout_watcher_state = _load_json_file(PR102_CLOSEOUT_CANON_WATCHER_STATE_PATH)
    elif _is_pr103_closeout_canon_repair_branch(branch_name):
        watcher_proven, watcher_proof_message = _pr103_closeout_canon_repair_watcher_proof_status(
            current_head_sha
        )
        require(
            watcher_proven,
            (
                "PR readiness gate: PR Watcher Provisioning Unproven blocker is active; "
                f"{watcher_proof_message}"
            ),
        )
        watcher_route_proven, watcher_route_message = _watcher_route_alignment_status(
            branch_record_text=active_branch_record_text,
            watcher_script_path=PR103_CLOSEOUT_CANON_WATCHER_SCRIPT_PATH,
            watcher_state_path=PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH,
        )
        require(
            watcher_route_proven,
            (
                "PR readiness gate: PR Watcher Routing Unverified blocker is active; "
                f"{watcher_route_message}"
            ),
        )
        closeout_watcher_state = _load_json_file(PR103_CLOSEOUT_CANON_WATCHER_STATE_PATH)
    else:
        closeout_watcher_state = None
    if (
        closeout_watcher_state is not None
        and (not mergeable or mergeable == "UNKNOWN" or not merge_state or merge_state == "UNKNOWN")
    ):
        watcher_mergeable = closeout_watcher_state.get("mergeable")
        watcher_merge_state = str(closeout_watcher_state.get("mergeableState") or "").upper()
        if watcher_mergeable is True:
            mergeable = "MERGEABLE"
            merge_state = watcher_merge_state or "CLEAN"
        elif watcher_mergeable is False:
            mergeable = "CONFLICTING"
            merge_state = watcher_merge_state or "DIRTY"
        elif watcher_merge_state:
            merge_state = watcher_merge_state
    if not fallback_local_state and (
        not mergeable or mergeable == "UNKNOWN" or not merge_state or merge_state == "UNKNOWN"
    ):
        local_merge_clean, local_merge_error = _local_merge_tree_clean()
        if local_merge_clean:
            mergeable = "MERGEABLE"
            merge_state = "CLEAN"
        elif local_merge_error:
            merge_state = merge_state or "UNKNOWN"
    normalized_recorded_status = recorded_bot_review_status.strip().casefold()
    comment_resolution_recorded = (
        normalized_recorded_status == BOT_REVIEW_SIGNAL_STATUS_COMMENT_ADDRESSED.casefold()
    )
    if comment_resolution_recorded:
        if (
            recorded_bot_review_head
            and current_head_sha
            and recorded_bot_review_head != current_head_sha
        ):
            followthrough_ok, followthrough_error = _bot_review_comment_closeout_followthrough_ok(
                recorded_bot_review_head,
                current_head_sha,
            )
            require(
                followthrough_ok,
                (
                    "PR readiness gate: PR Validation Pending blocker is active; recorded bot-review "
                    f"signal head '{recorded_bot_review_head}' in "
                    f"{active_branch_record_path or 'the active branch record'} does not match current "
                    f"head '{current_head_sha}', and the later follow-through is not limited to bounded "
                    f"closeout/governance files: {followthrough_error}"
                ),
            )

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
    if pr_head_oid:
        require(
            pr_head_oid == current_head_sha,
            (
                "PR readiness gate: PR Validation Pending blocker is active; "
                f"PR head SHA '{pr_head_oid}' does not match current branch head "
                f"'{current_head_sha or 'UNKNOWN'}'"
            ),
        )
    require(
        pr_base == "main",
        (
            "PR readiness gate: PR Validation Pending blocker is active; "
            f"PR base '{pr_base}' does not match merge-target canon 'main'"
        ),
    )
    merge_status_green = mergeable == "MERGEABLE" and merge_state not in {
        "BLOCKED",
        "DIRTY",
        "UNKNOWN",
        "DRAFT",
    }
    require(
        merge_status_green,
        (
            "PR readiness gate: PR Merge Status Unproven blocker is active; "
            f"PR mergeability is '{mergeable or 'UNKNOWN'}' and merge state is "
            f"'{merge_state or 'UNKNOWN'}'"
        ),
    )
    require(
        review_decision not in {"CHANGES_REQUESTED", "REVIEW_REQUIRED"},
        (
            "PR readiness gate: PR Validation Pending blocker is active; "
            f"PR review decision is '{review_decision or 'UNKNOWN'}'"
        ),
    )

    live_codex_review_threads_clear = False
    if not fallback_local_state:
        unresolved_codex_threads, thread_error = _gh_unresolved_codex_threads(
            str(pr_info.get("id") or ""),
            pr_info,
        )
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
        live_codex_review_threads_clear = not thread_error and not unresolved_codex_threads

    if fallback_local_state:
        fallback_bot_comment_latch_clear = _fallback_bot_approval_clears_comment_latch(
            phase_status_section=phase_status_section,
            bot_comment_count=fallback_bot_comment_count,
            bot_approval=fallback_bot_approval,
            bot_approval_ordered=fallback_bot_approval_ordered,
        )
        if fallback_bot_comment_count > 0 and not fallback_bot_comment_latch_clear:
            require(
                False,
                (
                    "PR readiness gate: PR Validation Pending blocker is active; bounded fallback "
                    f"runtime proof for PR {pr_url or pr_info.get('number')} reports "
                    f"{fallback_bot_comment_count} bot comment(s); fix, push, resolve, request "
                    "Codex Connector bot revalidation, and record ordered later approval proof "
                    "before PR green"
                ),
            )
        if not fallback_bot_approval:
            require(
                False,
                (
                    "PR readiness gate: PR Validation Pending blocker is active; Bot Review Signal Pending "
                    f"for live PR '{pr_url or pr_info.get('number') or 'UNKNOWN'}' according to "
                    "the bounded fallback watcher state"
                ),
            )
        if (
            closeout_watcher_state is not None
            and current_pr_readiness_seam
            in {
                AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM,
                PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
                PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
                PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            }
            and not bool(closeout_watcher_state.get("merged"))
        ):
            require(
                False,
                (
                    "PR readiness gate: PR Merge Verification Pending blocker is active; the same-thread "
                    f"watcher contract for live PR '{pr_url or pr_info.get('number') or 'UNKNOWN'}' "
                    "has not yet verified a merged state"
                ),
            )
        return

    live_signal, signal_error = _github_pr_bot_signal_for_live_pr(
        str(pr_info.get("repositoryFullName") or ""),
        int(pr_info.get("number") or 0),
        current_head_sha,
    )
    if signal_error and closeout_watcher_state:
        fallback_bot_comment_count = int(closeout_watcher_state.get("botCommentCount") or 0)
        fallback_bot_approval_ordered = _watcher_fallback_current_head_bot_approval_proven(
            phase_status_section
        )
        fallback_bot_approval = fallback_bot_approval_ordered
        fallback_bot_comment_latch_clear = _fallback_bot_approval_clears_comment_latch(
            phase_status_section=phase_status_section,
            bot_comment_count=fallback_bot_comment_count,
            bot_approval=fallback_bot_approval,
            bot_approval_ordered=fallback_bot_approval_ordered,
        )
        if fallback_bot_comment_count > 0 and not fallback_bot_comment_latch_clear:
            require(
                False,
                (
                    "PR readiness gate: PR Validation Pending blocker is active; bounded watcher "
                    f"proof for live PR '{pr_url or pr_info.get('number') or 'UNKNOWN'}' reports "
                    f"{fallback_bot_comment_count} bot comment(s); fix, push, resolve, request "
                    "Codex Connector bot revalidation, and record ordered later approval proof "
                    "before PR green"
                ),
            )
        if not fallback_bot_approval:
            require(
                False,
                (
                    "PR readiness gate: PR Validation Pending blocker is active; Bot Review Signal Pending "
                    f"for live PR '{pr_url or pr_info.get('number') or 'UNKNOWN'}' according to "
                    "the bounded watcher state"
                ),
            )
        if (
            current_pr_readiness_seam
            in {
                AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM,
                PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
                PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
                PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            }
            and not bool(closeout_watcher_state.get("merged"))
        ):
            require(
                False,
                (
                    "PR readiness gate: PR Merge Verification Pending blocker is active; the same-thread "
                    f"watcher contract for live PR '{pr_url or pr_info.get('number') or 'UNKNOWN'}' "
                    "has not yet verified a merged state"
                ),
            )
        return
    require(
        not signal_error,
        (
            "PR readiness gate: PR State Unknown blocker is active; "
            f"could not inspect bot-review signal state for PR {pr_url or pr_info.get('number')}: {signal_error}"
        ),
    )
    if signal_error:
        return

    signal_status = live_signal.get("status", "")
    signal_source = live_signal.get("source", "")
    signal_timestamp = live_signal.get("timestamp", "")
    signal_actor = live_signal.get("actor", "")
    signal_head = live_signal.get("head", "")
    if signal_status == "comment":
        require(
            False,
            (
                "PR readiness gate: PR Validation Pending blocker is active; bot review comment "
                f"detected from '{signal_actor or BOT_REVIEW_BOT_LOGIN}' via {signal_source or 'comment'} "
                f"at '{signal_timestamp or 'unknown time'}' on live PR "
                f"'{pr_url or pr_info.get('number') or 'UNKNOWN'}'; fix, push, resolve the "
                "comment, request Codex Connector bot revalidation, and wait for a later "
                "thumbs-up/approval signal before PR green"
            ),
        )
    elif signal_status != BOT_REVIEW_SIGNAL_STATUS_APPROVED.casefold():
        require(
            False,
            (
                "PR readiness gate: PR Validation Pending blocker is active; Bot Review Signal Pending "
                f"for live PR '{pr_url or pr_info.get('number') or 'UNKNOWN'}'; wait "
                "for a Codex Connector bot thumbs-up reaction or green approval comment on the live PR"
            ),
        )
        return

    signal_time = _parse_iso8601_timestamp(signal_timestamp)
    require(
        bool(signal_time and signal_head == current_head_sha),
        (
            "PR readiness gate: PR Validation Pending blocker is active; Codex Connector "
            f"approval signal at '{signal_timestamp or 'unknown time'}' is not bound to "
            f"current live PR head '{current_head_sha or 'UNKNOWN'}'"
        ),
    )

    if (
        closeout_watcher_state is not None
        and current_pr_readiness_seam
        in {
            AUTOMATION_CLOSEOUT_PR_READINESS_PR2_SEAM,
            PR101_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            PR102_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
            PR103_CLOSEOUT_CANON_PR_READINESS_PR2_SEAM,
        }
        and not bool(closeout_watcher_state.get("merged"))
    ):
        require(
            False,
            (
                "PR readiness gate: PR Merge Verification Pending blocker is active; the same-thread "
                f"watcher contract for live PR '{pr_url or pr_info.get('number') or 'UNKNOWN'}' "
                "has not yet verified a merged state"
            ),
        )


def _run_merge_target_authority_projection_gate(
    require,
    *,
    active_branch_record_paths: set[str],
    active_branch_record_path: str,
    active_branch_record_text: str,
    merge_stable_branch_record_path: str,
    merge_stable_branch_record_text: str,
) -> None:
    branch_record_text = merge_stable_branch_record_text or active_branch_record_text
    if not branch_record_text:
        return
    if merge_stable_branch_record_text and active_branch_record_text:
        merge_stable_branch = _extract_branch_identity_branch(merge_stable_branch_record_text)
        active_branch = _extract_branch_identity_branch(active_branch_record_text)
        if (
            merge_stable_branch
            and active_branch == merge_stable_branch
            and active_branch_record_path != STANDING_GOVERNANCE_INTAKE_RECORD.as_posix()
        ):
            require(
                False,
                (
                    "PR readiness gate: Merge-Stable Projection Shadowed By Active Authority "
                    "blocker is active; a post-merge projection receipt cannot sit beside an "
                    "active authority record for the same branch. Move the actual branch record "
                    "to Historical Branch Authority Records, remove it from Active Branch "
                    "Authority Records, and then rerun the Release Readiness Health Pass before "
                    "PR green."
                ),
            )
    post_merge_state = _section(branch_record_text, "Post-Merge State")
    if "No Active Branch" not in post_merge_state:
        return

    # Merged-main `No Active Branch` allows the single standing governance intake
    # authority record; it is not a runtime/implementation/release carrier.
    remaining_active_record_paths = sorted(
        record_path
        for record_path in active_branch_record_paths
        if record_path != STANDING_GOVERNANCE_INTAKE_RECORD.as_posix()
    )
    require(
        not remaining_active_record_paths,
        (
            "PR readiness gate: Merge-Target Authority Projection Unproven blocker is active; "
            "Active Branch Authority Records still contains "
            f"{', '.join(remaining_active_record_paths) or 'UNKNOWN'} even though Post-Merge "
            "State declares No Active Branch. Move every active authority record to "
            "historical/no-active posture or otherwise make branch-authority truth merge-stable "
            "before PR green."
        ),
    )
    if remaining_active_record_paths:
        return

    if (
        active_branch_record_path == STANDING_GOVERNANCE_INTAKE_RECORD.as_posix()
        and not merge_stable_branch_record_text
    ):
        # The standing Governance intake is the explicit merged-main exception:
        # it remains the sole active authority while no product branch is active.
        # If a merge-stable projection is supplied, validate that projection below.
        return

    phase = _extract_marker_value(_section(branch_record_text, "Current Phase"), "Phase")
    phase_status = _section(branch_record_text, "Phase Status")
    require(
        merge_stable_branch_record_path and phase == HISTORICAL_TRACEABILITY_PHASE,
        (
            "PR readiness gate: Merge-Target Authority Projection Unproven blocker is active; "
            "the current branch record must be listed under Historical Branch Authority Records "
            f"with `Phase: {HISTORICAL_TRACEABILITY_PHASE}` before PR green when post-merge "
            "truth is No Active Branch"
        ),
    )
    require(
        "`Active Branch`" not in phase_status,
        (
            "PR readiness gate: Merge-Target Authority Projection Unproven blocker is active; "
            "historical/no-active branch-authority Phase Status still declares `Active Branch`"
        ),
    )
    for active_pr_marker in HISTORICAL_BRANCH_ACTIVE_PR_MARKERS:
        require(
            active_pr_marker not in phase_status,
            (
                "PR readiness gate: Merge-Target Authority Projection Unproven blocker is active; "
                f"historical/no-active branch-authority Phase Status still retains "
                f"active PR-readiness marker '{active_pr_marker}'"
            ),
        )


def _normalized_gate_state(value: str) -> str:
    return value.strip().strip("`").strip().replace("-", " ").upper()


def _gate_state_matches(marker_state: str, allowed_states: set[str]) -> bool:
    return any(
        marker_state == allowed_state or marker_state.startswith(f"{allowed_state} ")
        for allowed_state in allowed_states
    )


def _standing_governance_intake_file_allowed(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return (
        normalized.startswith("Docs/")
        or normalized.startswith("dev/fixtures/branch_readiness_planning/")
        or normalized.startswith("dev/fixtures/branch_record_live_state_leakage/")
        or normalized.startswith("dev/fixtures/pr_review_churn/")
        or normalized in STANDING_GOVERNANCE_INTAKE_ALLOWED_DEV_FILES
    )


def _repo_active_rri_cycle_values(active_cycle_values: list[str]) -> list[str]:
    return [
        value.strip()
        for value in active_cycle_values
        if re.match(r"^RRI-\d{8}-\d{3}", value.strip(), flags=re.I)
    ]


def _run_repo_active_rri_cycle_parser_fixtures(require) -> None:
    sample_values = [
        "External operational state only - see C:\\Nexus Governance State\\branches\\feature_release_readiness_source_truth_intake\\branch_state.md",
        "RRI-20260629-001",
        "RRI-20260629-001 - release target repair",
        "`RRI-20260629-001`",
    ]
    forbidden_values = _repo_active_rri_cycle_values(sample_values)
    require(
        forbidden_values == [
            "RRI-20260629-001",
            "RRI-20260629-001 - release target repair",
        ],
        (
            "Standing Governance Intake active-cycle parser must reject exact "
            "`RRI-*` values and `RRI-*` values with suffix text, while allowing "
            "the external-state pointer"
        ),
    )


def _run_standing_governance_intake_gate(require) -> None:
    _run_repo_active_rri_cycle_parser_fixtures(require)
    branch_name = _git_current_branch()
    branch_record_index_text = _read_text(BRANCH_RECORD_INDEX)
    active_branch_record_paths = _collect_branch_record_paths(
        branch_record_index_text,
        "Active Branch Authority Records",
    )
    expected_record_path = STANDING_GOVERNANCE_INTAKE_RECORD.as_posix()
    record_path, record_text = _active_branch_record_for_branch(
        active_branch_record_paths,
        branch_name,
    )

    require(
        branch_name == STANDING_GOVERNANCE_INTAKE_BRANCH,
        (
            "Standing Governance Intake gate must run on "
            f"`{STANDING_GOVERNANCE_INTAKE_BRANCH}`, found `{branch_name or 'detached HEAD'}`"
        ),
    )
    require(
        expected_record_path in active_branch_record_paths,
        (
            f"{BRANCH_RECORD_INDEX}: Standing Governance Intake Branch record "
            f"`{expected_record_path}` must be listed under Active Branch Authority Records"
        ),
    )
    require(
        record_path == expected_record_path,
        (
            "Standing Governance Intake gate must resolve the active authority record "
            f"`{expected_record_path}`, found `{record_path or 'none'}`"
        ),
    )
    if not record_text:
        return

    info = _parse_workstream_doc(record_text)
    require(
        str(info["branch_class"]) == STANDING_GOVERNANCE_INTAKE_BRANCH_CLASS,
        (
            f"{expected_record_path}: Branch Class must be "
            f"`{STANDING_GOVERNANCE_INTAKE_BRANCH_CLASS}`"
        ),
    )

    tracked_status = _git_status_porcelain(tracked_only=True)
    require(
        not tracked_status,
        (
            "Standing Governance Intake gate requires a clean tracked worktree; "
            f"dirty tracked status: {tracked_status}"
        ),
    )

    contract = _section(record_text, "Standing Governance Intake Contract")
    return_digest = _section(record_text, "Return Digest Contract")
    return_digest_identity_guard = _section(record_text, "Return Digest Identity Guard")
    require(
        bool(contract),
        f"{expected_record_path}: missing ## Standing Governance Intake Contract",
    )
    require(
        bool(return_digest),
        f"{expected_record_path}: missing ## Return Digest Contract",
    )
    require(
        bool(return_digest_identity_guard),
        f"{expected_record_path}: missing ## Return Digest Identity Guard",
    )
    for marker in STANDING_GOVERNANCE_INTAKE_CONTRACT_MARKERS:
        value = _extract_marker_value(contract, marker)
        require(
            bool(value),
            f"{expected_record_path}: Standing Governance Intake Contract is missing '{marker}:'",
        )
    for marker in STANDING_GOVERNANCE_INTAKE_RETURN_DIGEST_MARKERS:
        require(
            marker in return_digest,
            f"{expected_record_path}: Return Digest Contract is missing '{marker}:'",
        )
    for marker in STANDING_GOVERNANCE_RETURN_DIGEST_IDENTITY_GUARD_MARKERS:
        require(
            marker in return_digest_identity_guard,
            f"{expected_record_path}: Return Digest Identity Guard is missing '{marker}:'",
        )
    require(
        "C:\\Nexus Desktop AI" in return_digest_identity_guard
        and "C:\\Nexus Worktrees\\Governance" in return_digest_identity_guard,
        (
            f"{expected_record_path}: Return Digest Identity Guard must explicitly ban "
            "defaulting to the neutral/main folder or governance worktree"
        ),
    )

    intake_source = _extract_marker_value(contract, "Intake Source")
    require(
        "Release Readiness digest" in intake_source,
        (
            f"{expected_record_path}: Intake Source must preserve "
            "`Release Readiness digest` routing"
        ),
    )
    require(
        "automation/worktree governance intake" in intake_source,
        (
            f"{expected_record_path}: Intake Source must name the USER-approved "
            "automation/worktree governance intake exception"
        ),
    )
    require(
        "phase-gate governance intake" in intake_source,
        (
            f"{expected_record_path}: Intake Source must name the USER-approved "
            "phase-gate governance intake exception"
        ),
    )
    require(
        "Waiting For Governance Intake" in record_text and "Waiting For Updated Main" in record_text,
        (
            f"{expected_record_path}: originating-lane pause semantics must include "
            "`Waiting For Governance Intake` and `Waiting For Updated Main`"
        ),
    )

    active_cycle_values = re.findall(
        r"^\s*(?:-\s*)?Active RRI Cycle:\s*`?([^`\n]+)`?\s*$",
        record_text,
        flags=re.M,
    )
    repo_active_cycles = _repo_active_rri_cycle_values(active_cycle_values)
    require(
        not repo_active_cycles,
        (
            f"{expected_record_path}: active `RRI-*` cycle values must not be "
            "recorded in repo branch records after external-state migration; "
            f"point `Active RRI Cycle:` to `{STANDING_GOVERNANCE_INTAKE_EXTERNAL_STATE_POINTER}`"
        ),
    )
    active_cycle_external_owner_recorded = any(
        "external operational state" in value.casefold()
        and STANDING_GOVERNANCE_INTAKE_EXTERNAL_STATE_POINTER in value
        for value in active_cycle_values
    )
    require(
        active_cycle_external_owner_recorded,
        (
            f"{expected_record_path}: `Active RRI Cycle:` must route the current "
            "standing-intake cycle to external operational state instead of "
            "owning the live cycle value in repo docs"
        ),
    )
    external_cycle_text = ""
    external_cycle_error = ""
    external_cycle_id = ""
    if active_cycle_external_owner_recorded:
        try:
            external_cycle_text = Path(
                STANDING_GOVERNANCE_INTAKE_EXTERNAL_STATE_POINTER
            ).read_text(encoding="utf-8")
        except OSError as exc:
            external_cycle_error = str(exc)
        else:
            external_cycle_match = re.search(
                r"^\s*(?:-\s*)?Current Cycle:\s*`?(RRI-\d{8}-\d{3})`?\s*$",
                external_cycle_text,
                flags=re.M,
            )
            external_cycle_id = (
                external_cycle_match.group(1).strip()
                if external_cycle_match
                else ""
            )
    external_no_active_cycle = bool(
        re.search(
            r"^\s*(?:-\s*)?Current Cycle:\s*`?(?:None|No active cycle|Closed)`?\s*$",
            external_cycle_text,
            flags=re.I | re.M,
        )
    )
    external_latest_closed_cycle_match = re.search(
        r"^\s*(?:-\s*)?Latest Closed RRI Cycle:\s*`?(RRI-\d{8}-\d{3})`?",
        external_cycle_text,
        flags=re.M,
    )
    external_latest_closed_cycle = (
        external_latest_closed_cycle_match.group(1).strip()
        if external_latest_closed_cycle_match
        else ""
    )
    external_return_digest_status_match = re.search(
        r"^\s*(?:-\s*)?Return Digest Status:\s*`?([^`\n]+)`?\s*$",
        external_cycle_text,
        flags=re.I | re.M,
    )
    external_return_digest_status = (
        external_return_digest_status_match.group(1).strip()
        if external_return_digest_status_match
        else ""
    )
    external_return_digest_closeout = bool(
        re.match(
            r"^(?:Complete|Closeout Pending)(?:\b|[\s:;.,-]|$)",
            external_return_digest_status,
            flags=re.I,
        )
    )

    active_cycle = ""
    latest_closed_cycle_values = re.findall(
        r"^\s*(?:-\s*)?Latest Closed RRI Cycle:\s*`?([^`\n]+)`?\s*$",
        record_text,
        flags=re.M,
    )
    latest_closed_cycles = [
        value.strip()
        for value in latest_closed_cycle_values
        if re.fullmatch(r"RRI-\d{8}-\d{3}", value.strip())
    ]
    require(
        len(set(latest_closed_cycles)) <= 1,
        f"{expected_record_path}: only one latest closed `RRI-*` cycle may be recorded",
    )
    latest_closed_cycle = latest_closed_cycles[-1] if latest_closed_cycles else ""
    closeout_cycle_recorded = bool(
        external_latest_closed_cycle
        and active_cycle_external_owner_recorded
        and external_no_active_cycle
        and external_return_digest_closeout
    )
    bootstrap_setup_recorded = (
        "Bootstrap Setup:" in record_text
        and "RRI-20260514-001" in record_text
        and "one-time USER-approved exception" in record_text
    )
    bootstrap_base_match = re.search(
        r"Branch created from `origin/main` at `([0-9a-f]{40})`",
        record_text,
    )
    bootstrap_base_sha = bootstrap_base_match.group(1) if bootstrap_base_match else ""
    if bootstrap_setup_recorded:
        require(
            bool(bootstrap_base_sha),
            (
                f"{expected_record_path}: Bootstrap Exception Limit requires the "
                "branch creation base SHA to be recorded"
            ),
        )
    if active_cycle or active_cycle_external_owner_recorded:
        require(
            (
                "Release Readiness digest" in intake_source
                or "automation/worktree governance intake" in intake_source
                or "phase-gate governance intake" in intake_source
            ),
            (
                f"{expected_record_path}: active {active_cycle} must originate from "
                "Release Readiness, USER-approved automation/worktree governance intake, "
                "or USER-approved phase-gate governance intake"
            ),
        )

    neutral_main_truth = _neutral_main_workspace_truth()
    require(
        not neutral_main_truth.get("error"),
        (
            "Standing Governance Intake neutral-main rebaseline proof could not inspect "
            f"`{NEUTRAL_MAIN_WORKSPACE}`: {neutral_main_truth.get('error')}"
        ),
    )
    if not neutral_main_truth.get("error"):
        require(
            _normalized_local_path(neutral_main_truth.get("root", ""))
            == _normalized_local_path(str(NEUTRAL_MAIN_WORKSPACE)),
            (
                "Standing Governance Intake neutral-main rebaseline proof resolved the wrong "
                f"git root: {neutral_main_truth.get('root') or 'unknown'}"
            ),
        )
        require(
            neutral_main_truth.get("branch") == "main",
            (
                "Standing Governance Intake neutral-main rebaseline proof requires "
                f"`{NEUTRAL_MAIN_WORKSPACE}` to be on `main`, found "
                f"`{neutral_main_truth.get('branch') or 'detached HEAD'}`"
            ),
        )
        require(
            not neutral_main_truth.get("status"),
            (
                "Standing Governance Intake neutral-main rebaseline proof requires a clean "
                f"tracked main workspace; dirty tracked status: {neutral_main_truth.get('status')}"
            ),
        )
        require(
            neutral_main_truth.get("head") == neutral_main_truth.get("origin_main"),
            (
                "Standing Governance Intake neutral-main rebaseline proof requires "
                f"`{NEUTRAL_MAIN_WORKSPACE}` HEAD to match origin/main; HEAD "
                f"{neutral_main_truth.get('head') or 'unknown'} != origin/main "
                f"{neutral_main_truth.get('origin_main') or 'unknown'}"
            ),
        )

    head_sha = _git_head_sha()
    origin_main_sha = _git_ref_sha("refs/remotes/origin/main")
    require(bool(head_sha), "Standing Governance Intake gate could not resolve HEAD")
    require(bool(origin_main_sha), "Standing Governance Intake gate could not resolve origin/main")
    bootstrap_active = bool(
        bootstrap_setup_recorded
        and bootstrap_base_sha
        and origin_main_sha
        and origin_main_sha == bootstrap_base_sha
    )
    if head_sha and origin_main_sha:
        changed_files, changed_error = _git_changed_files(origin_main_sha, head_sha)
        require(
            not changed_error,
            f"Standing Governance Intake gate could not inspect origin/main..HEAD: {changed_error}",
        )
        if changed_files:
            ancestor_ok, ancestor_error = _git_is_ancestor(origin_main_sha, head_sha)
            require(
                not ancestor_error and ancestor_ok,
                (
                    "Standing Governance Intake branch must be based on current origin/main "
                    f"before carrying bootstrap or RRI-cycle changes: {ancestor_error}"
                ),
            )
            external_active_cycle_ok = False
            if active_cycle_external_owner_recorded:
                require(
                    not external_cycle_error,
                    (
                        "Standing Governance Intake branch is ahead of origin/main "
                        "but the external active-cycle state could not be read: "
                        f"{external_cycle_error}"
                    ),
                )
                if not closeout_cycle_recorded:
                    require(
                        bool(re.fullmatch(r"RRI-\d{8}-\d{3}", external_cycle_id)),
                        (
                            "Standing Governance Intake branch is ahead of origin/main "
                            "but the external branch state does not prove a concrete "
                            "`Current Cycle: RRI-YYYYMMDD-NNN`"
                        ),
                    )
                    require(
                        "Current Gate:" in external_cycle_text
                        and "Current Pull Request:" in external_cycle_text,
                        (
                            "Standing Governance Intake branch is ahead of origin/main "
                            "but the external branch state is missing current gate or "
                            "pull-request proof for the active cycle"
                        ),
                    )
                    external_active_cycle_ok = bool(
                        re.fullmatch(r"RRI-\d{8}-\d{3}", external_cycle_id)
                    )
            for changed_file in changed_files:
                require(
                    _standing_governance_intake_file_allowed(changed_file),
                    (
                        "Standing Governance Intake may touch only source-truth/governance "
                        f"docs or registered governance validators; forbidden file: {changed_file}"
                    ),
                )
            require(
                bool(active_cycle or external_active_cycle_ok or bootstrap_active or closeout_cycle_recorded),
                (
                    "Standing Governance Intake branch is ahead of origin/main without an "
                    "externally proven active RRI cycle, recorded bootstrap setup exception, "
                    "or return-digest closeout"
                ),
            )


def _is_historical_worktree_receipt(record_text: str) -> bool:
    normalized = record_text.casefold()
    return (
        "record state:" in normalized
        and "historical" in normalized
        and "phase:" in normalized
        and "historical traceability" in normalized
        and "worktree receipt:" in normalized
        and "does not own" in normalized
        and "worktree assignment" in normalized
    )


def _validate_historical_worktree_receipt_confinement(
    require,
    record_path: str | Path,
    record_text: str,
) -> None:
    identity = _section(record_text, "Branch Identity")
    require(
        bool(_extract_exact_marker_value(identity, "Worktree Receipt")),
        f"{record_path}: historical worktree receipt fallback requires a `Worktree Receipt:` marker",
    )
    require(
        not _extract_exact_marker_value(identity, "Worktree"),
        (
            f"{record_path}: historical branch receipt must not declare an active "
            "`Worktree:` assignment marker"
        ),
    )


def _run_worktree_confinement_regression_fixtures(require) -> None:
    fixture = (
        BRANCH_RECORD_LIVE_STATE_LEAKAGE_FIXTURE_DIR
        / "valid_historical_worktree_receipt.md"
    )
    fixture_text = _read_text(fixture)
    identity = _section(fixture_text, "Branch Identity")
    active_and_receipt_identity = (
        "- Worktree: `C:\\Nexus Worktrees\\FAM-007`\n"
        "- Worktree Receipt: `C:\\Nexus Worktrees\\Historical-FAM-007`\n"
    )
    external_state_identity = (
        "Branch: `feature/fam-007-owner-ai-operational-foundation-gates`\n"
        "Branch Planning Packet ZIP: `C:\\Nexus USER\\FAM-007-20260608-164406.zip`\n"
        "Worktree: `C:\\Nexus Worktrees\\FAM-007`\n"
        "Worktree State: `C:\\Nexus Governance State\\worktrees\\FAM-007\\worktree_state.md`\n"
        "Repo Branch Record Pointer: `Docs/branch_records/feature_fam_007_owner_ai_operational_foundation_gates.md`\n"
    )
    require(
        bool(fixture_text),
        f"{fixture}: missing historical worktree receipt regression fixture",
    )
    require(
        _is_historical_worktree_receipt(fixture_text),
        f"{fixture}: fixture must classify as a historical worktree receipt",
    )
    require(
        "pr readiness stage 1" not in fixture_text.casefold()
        and "stage 1 ready for stage 2" not in fixture_text.casefold(),
        f"{fixture}: broad historical receipt fixture must not rely on PR Readiness fallback wording",
    )
    _validate_historical_worktree_receipt_confinement(require, fixture, fixture_text)
    external_target_fixture = (
        BRANCH_RECORD_LIVE_STATE_LEAKAGE_FIXTURE_DIR
        / "valid_external_state_historical_worktree_receipt_target.md"
    )
    external_target_text = _read_text(external_target_fixture)
    require(
        bool(external_target_text),
        f"{external_target_fixture}: missing external-state historical receipt target fixture",
    )
    require(
        _is_historical_worktree_receipt(external_target_text),
        f"{external_target_fixture}: fixture must classify as a historical worktree receipt",
    )
    _validate_historical_worktree_receipt_confinement(
        require,
        external_target_fixture,
        external_target_text,
    )
    require(
        not _extract_exact_marker_value(identity, "Worktree"),
        f"{fixture}: `Worktree Receipt:` must not be parsed as active `Worktree:` assignment",
    )
    require(
        _extract_exact_marker_value(identity, "Worktree Receipt")
        == "C:\\Nexus Worktrees\\FAM-007",
        f"{fixture}: exact `Worktree Receipt:` marker was not parsed",
    )
    require(
        _extract_exact_marker_value(active_and_receipt_identity, "Worktree")
        == "C:\\Nexus Worktrees\\FAM-007",
        "Assigned Worktree Confinement exact-marker fixture did not parse active `Worktree:`",
    )
    require(
        _extract_exact_marker_value(active_and_receipt_identity, "Worktree Receipt")
        == "C:\\Nexus Worktrees\\Historical-FAM-007",
        "Assigned Worktree Confinement exact-marker fixture did not parse `Worktree Receipt:`",
    )
    require(
        _extract_exact_marker_value(external_state_identity, "Branch")
        == "feature/fam-007-owner-ai-operational-foundation-gates",
        "Assigned Worktree Confinement external-state fixture must not parse `Branch Planning Packet ZIP:` as `Branch:`",
    )
    require(
        _extract_exact_marker_value(external_state_identity, "Worktree")
        == "C:\\Nexus Worktrees\\FAM-007",
        "Assigned Worktree Confinement external-state fixture must not parse `Worktree State:` as `Worktree:`",
    )


def _run_worktree_confinement_gate(require, *, selected_owner=None) -> None:
    _run_worktree_confinement_regression_fixtures(require)

    branch_name = _git_current_branch()
    actual_root = _git_top_level()
    upstream_branch = _git_upstream_branch()
    if selected_owner is not None:
        record_path,record_text=selected_owner
    else:
        branch_record_index_text = _read_text(BRANCH_RECORD_INDEX)
        active_branch_record_paths = _collect_branch_record_paths(
            branch_record_index_text,
            "Active Branch Authority Records",
        )
        record_path, record_text = _active_branch_record_for_branch(
            active_branch_record_paths,
            branch_name,
        )
        if not record_text:
            external_record_path, external_record_text = _external_branch_state_record_for_branch(
                branch_name,
                actual_root,
            )
            if external_record_text and _is_historical_worktree_receipt(external_record_text):
                _validate_historical_worktree_receipt_confinement(
                    require,
                    external_record_path,
                    external_record_text,
                )
                return
            record_path, record_text = external_record_path, external_record_text
        if not record_text:
            historical_branch_record_paths = _collect_branch_record_paths(
                branch_record_index_text,
                "Historical Branch Authority Records",
            )
            historical_record_path, historical_record_text = _branch_record_for_branch(
                historical_branch_record_paths,
                branch_name,
            )
            if historical_record_text and _is_historical_worktree_receipt(historical_record_text):
                record_path = historical_record_path
                record_text = historical_record_text
                _validate_historical_worktree_receipt_confinement(
                    require,
                    record_path,
                    record_text,
                )
                return
            if (
                historical_record_text
                and "pr readiness stage 1" in historical_record_text.casefold()
                and "stage 1 ready for stage 2" in historical_record_text.casefold()
            ):
                record_path = historical_record_path
                record_text = historical_record_text

    require(
        bool(branch_name),
        "Assigned Worktree Confinement gate requires a checked-out branch, found detached HEAD",
    )
    require(
        bool(actual_root),
        "Assigned Worktree Confinement gate could not resolve git top-level worktree root",
    )
    require(
        bool(record_text),
        (
            "Assigned Worktree Confinement gate requires the current branch to have an "
            "active branch authority record, matching external branch-state record, "
            "or a PR Readiness Stage 1 historical authority projection"
        ),
    )
    if not record_text:
        return

    identity = _section(record_text, "Branch Identity")
    expected_root = _extract_exact_marker_value(identity, "Worktree")
    confinement = _section(record_text, "Assigned Worktree Confinement")
    require(
        bool(expected_root),
        f"{record_path}: Assigned Worktree Confinement requires a Branch Identity `Worktree:` marker",
    )
    require(
        bool(confinement),
        f"{record_path}: missing ## Assigned Worktree Confinement",
    )
    for marker in ASSIGNED_WORKTREE_CONFINEMENT_RECORD_MARKERS:
        require(
            marker in confinement,
            f"{record_path}: Assigned Worktree Confinement is missing '{marker}:'",
        )

    owner_state = _extract_marker_value(confinement, "Active Thread Owner")
    assignment_state = _extract_marker_value(confinement, "Thread Assignment Status")
    ledger_state = _extract_marker_value(confinement, "Worktree Ownership Ledger")
    write_set = _extract_marker_value(confinement, "Intended Write Set")
    same_worktree_state = _extract_marker_value(
        confinement, "Same Worktree / Same Branch Collision Check"
    )
    dirty_collision_state = _extract_marker_value(
        confinement, "Dirty Worktree Collision Check"
    )
    recovery_packet = _extract_marker_value(confinement, "Dirty Worktree Recovery Packet")
    off_worktree_routing = _extract_marker_value(confinement, "Off-Worktree Work Routing")
    governance_barrier = _extract_marker_value(confinement, "Governance Routing Barrier")
    new_worktree_gate = _extract_marker_value(confinement, "New Worktree Decision Gate")
    for marker, value in (
        ("Active Thread Owner", owner_state),
        ("Thread Assignment Status", assignment_state),
        ("Worktree Ownership Ledger", ledger_state),
        ("Intended Write Set", write_set),
        ("Same Worktree / Same Branch Collision Check", same_worktree_state),
        ("Dirty Worktree Collision Check", dirty_collision_state),
        ("Dirty Worktree Recovery Packet", recovery_packet),
        ("Off-Worktree Work Routing", off_worktree_routing),
        ("Governance Routing Barrier", governance_barrier),
        ("New Worktree Decision Gate", new_worktree_gate),
    ):
        normalized_value = value.casefold()
        require(
            bool(value)
            and "unknown" not in normalized_value
            and "not checked" not in normalized_value
            and "not recorded" not in normalized_value,
            f"{record_path}: Assigned Worktree Confinement '{marker}:' must be explicit before mutation",
        )

    tracked_status = _git_status_porcelain(tracked_only=True)
    if tracked_status:
        normalized_dirty = dirty_collision_state.casefold()
        require(
            "owner claimed" in normalized_dirty
            or "current owner" in normalized_dirty
            or "no unowned" in normalized_dirty,
            (
                "Dirty Worktree Collision Check must name the active owner before "
                f"continuing with dirty tracked files: {tracked_status}"
            ),
        )

    if expected_root and actual_root:
        roots_match = _normalized_local_path(expected_root) == _normalized_local_path(actual_root)
        waiver_state = _extract_marker_value(confinement, "Worktree Escape User Waiver")
        if roots_match:
            require(True, "Assigned Worktree Confinement root match")
        else:
            require(
                waiver_state.startswith("Granted") and actual_root in confinement,
                (
                    "Worktree Escape User Waiver Missing: active git root does not match "
                    f"the assigned worktree. Expected `{expected_root}`, actual `{actual_root}`. "
                    "Stop before mutation unless USER grants `Worktree Escape User Waiver: Granted` "
                    "with expected root, actual root, target root, allowed commands/files, expiration, "
                    "validation, and return path."
                ),
            )

    current_phase = _extract_marker_value(_section(record_text, "Current Phase"), "Phase")
    if current_phase == "Branch Readiness" and "fam-" in branch_name.casefold():
        family_scope = _section(record_text, "Family-Scoped Branch Readiness Confinement")
        require(
            bool(family_scope),
            f"{record_path}: missing ## Family-Scoped Branch Readiness Confinement",
        )
        target_family = _extract_marker_value(family_scope, "Target Family")
        sibling_exclusion = _extract_marker_value(
            family_scope,
            "Sibling Worktree Candidate Exclusion",
        )
        expected_family = ""
        family_match = re.search(r"fam-\d{3}", branch_name.casefold())
        if family_match:
            expected_family = family_match.group(0).upper()
        require(
            bool(target_family) and expected_family and expected_family in target_family.upper(),
            (
                f"{record_path}: Family-Scoped Branch Readiness Confinement must name "
                f"`Target Family: {expected_family}` for branch `{branch_name}`"
            ),
        )
        sibling_normalized = sibling_exclusion.casefold()
        require(
            bool(sibling_exclusion)
            and "overlap context only" in sibling_normalized
            and "not successor authority" in sibling_normalized,
            (
                f"{record_path}: Family-Scoped Branch Readiness Confinement must record "
                "`Sibling Worktree Candidate Exclusion:` with sibling worktrees as overlap "
                "context only and not successor authority"
            ),
        )

    if branch_name and upstream_branch:
        require(
            upstream_branch == f"origin/{branch_name}",
            (
                "Assigned Worktree Confinement gate requires the branch upstream to match "
                f"`origin/{branch_name}`, found `{upstream_branch}`"
            ),
        )


def _run_release_readiness_health_gate(
    require,
    *,
    backlog_entries: list[dict[str, str]] | None = None,
    active_branch_record_path: str = "",
    active_branch_record_text: str = "",
    selected_owner=None,
) -> None:
    branch_name = _git_current_branch()
    if selected_owner is not None:
        record_path,record_text=selected_owner
        current_active_branch_record_path=record_path
        current_active_branch_record_text=record_text
        active_branch_record_paths={record_path}
        historical_branch_record_path=''
        historical_branch_record_text=''
    else:
        branch_record_index_text = _read_text(BRANCH_RECORD_INDEX)
        active_branch_record_paths = _collect_branch_record_paths(
            branch_record_index_text,
            "Active Branch Authority Records",
        )
        historical_branch_record_paths = _collect_branch_record_paths(
            branch_record_index_text,
            "Historical Branch Authority Records",
        )
        current_active_branch_record_path, current_active_branch_record_text = _active_branch_record_for_branch(
            active_branch_record_paths,
            branch_name,
        )
        historical_branch_record_path, historical_branch_record_text = _branch_record_for_branch(
            historical_branch_record_paths,
            branch_name,
        )
        if current_active_branch_record_text and historical_branch_record_text:
            require(
                False,
                (
                    f"{historical_branch_record_path}: Release Readiness Health Pass cannot use a "
                    "post-merge projection receipt while "
                    f"{current_active_branch_record_path} remains listed under Active Branch "
                    "Authority Records for the same branch. Fold down the real active record into "
                    "historical/no-active posture before PR Stage 1 reports Stage 2-ready or before "
                    "merge approval."
                ),
            )

        record_path = current_active_branch_record_path or active_branch_record_path
        record_text = current_active_branch_record_text or active_branch_record_text
        if historical_branch_record_text:
            record_path = historical_branch_record_path
            record_text = historical_branch_record_text
        if not record_text:
            if backlog_entries is None:
                backlog_entries = _parse_backlog_sections(_read_text(Path("Docs/feature_backlog.md")))
            for entry in backlog_entries:
                entry_branch = _extract_colon_value(entry["block"], "Branch").strip("`")
                if entry_branch != branch_name:
                    continue
                canonical_path = entry["canonical_path"]
                if canonical_path:
                    record_path = canonical_path
                    record_text = _read_text(Path(canonical_path))
                break
        if not record_text:
            require(True, "Release Readiness Health Pass: not applicable without a current branch authority record")
            return

    info = _parse_workstream_doc(record_text)
    current_phase = str(info["current_phase"])
    is_projected_historical_pr_context = bool(
        historical_branch_record_path and _section(record_text, "Post-Merge State")
    )
    if current_phase != "PR Readiness" and not is_projected_historical_pr_context:
        lifecycle_markers = [
            marker for marker in PR_LIFECYCLE_SOURCE_TRUTH_MARKERS if marker in record_text
        ]
        if (
            str(info["branch_class"]) == "implementation"
            and current_phase != HISTORICAL_TRACEABILITY_PHASE
            and lifecycle_markers
        ):
            require(
                False,
                (
                    f"{record_path}: Release Readiness Health Pass cannot be skipped after "
                    f"PR-lifecycle source-truth marker(s) {', '.join(lifecycle_markers)} "
                    f"exist while Phase is `{current_phase}`. Move the branch through PR "
                    "Readiness and prove post-merge source truth before PR creation/merge; "
                    "if this is discovered after merge, route the blocker digest to "
                    f"`C:\\Nexus Worktrees\\Governance` / `{STANDING_GOVERNANCE_INTAKE_BRANCH}`."
                ),
            )
            return
        require(True, "Release Readiness Health Pass: not applicable outside PR Readiness")
        return

    health_pass = _section(record_text, "Release Readiness Health Pass")
    require(
        bool(health_pass),
        f"{record_path}: PR Readiness requires a ## Release Readiness Health Pass section",
    )
    if not health_pass:
        return

    for marker in RELEASE_READINESS_HEALTH_PASS_REQUIRED_MARKERS:
        marker_state = _normalized_gate_state(_extract_marker_value(health_pass, marker))
        require(
            bool(marker_state),
            f"{record_path}: Release Readiness Health Pass is missing '{marker}:'",
        )
        if not marker_state:
            continue
        if marker in RELEASE_READINESS_HEALTH_PASS_PASS_ONLY_MARKERS:
            require(
                _gate_state_matches(marker_state, {"PASS"}),
                (
                    f"{record_path}: Release Readiness Health Pass marker '{marker}:' "
                    f"must be PASS before PR merge readiness, found '{marker_state}'"
                ),
            )
        else:
            allowed_states = RELEASE_READINESS_HEALTH_PASS_OPTIONAL_MARKERS.get(marker, {"PASS"})
            require(
                _gate_state_matches(marker_state, allowed_states),
                (
                    f"{record_path}: Release Readiness Health Pass marker '{marker}:' "
                    f"must be one of {sorted(allowed_states)}, found '{marker_state}'"
                ),
            )

    post_merge_state = _section(record_text, "Post-Merge State")
    require(
        bool(post_merge_state),
        f"{record_path}: Release Readiness Health Pass requires a Post-Merge State section",
    )
    if not post_merge_state:
        return

    fold_down_text = f"{health_pass}\n{post_merge_state}".casefold()
    fold_down_projected = any(
        marker in fold_down_text
        for marker in RELEASE_READINESS_ACTIVE_AUTHORITY_FOLD_DOWN_MARKERS
    )
    if (
        current_active_branch_record_path
        and record_path == current_active_branch_record_path
        and current_active_branch_record_path != STANDING_GOVERNANCE_INTAKE_RECORD.as_posix()
        and fold_down_projected
    ):
        require(
            False,
            (
                f"{record_path}: PR Readiness Stage 1 branch-authority fold-down required; "
                "Release Readiness Health Pass/Post-Merge State projects historical/no-active "
                "posture, but the actual record still remains listed under Active Branch "
                "Authority Records. Move the record to Historical Branch Authority Records, "
                "retire or historical-label the branch plan, update compact pointers, and rerun "
                "the release-readiness health gate before Stage 2, PR green, or merge approval."
            ),
        )

    if "No Active Branch" in post_merge_state:
        _run_merge_target_authority_projection_gate(
            require,
            active_branch_record_paths=active_branch_record_paths,
            active_branch_record_path=current_active_branch_record_path,
            active_branch_record_text=current_active_branch_record_text,
            merge_stable_branch_record_path=historical_branch_record_path,
            merge_stable_branch_record_text=historical_branch_record_text,
        )

    projected_truth = post_merge_state
    for label, pattern in RELEASE_READINESS_HEALTH_STALE_POST_MERGE_PATTERNS:
        require(
            re.search(pattern, projected_truth, flags=re.I) is None,
            (
                f"{record_path}: Release Readiness Health Pass failed; projected "
                f"post-merge source truth still contains stale {label}"
            ),
        )

    merged_unreleased_state = _normalized_gate_state(
        _extract_marker_value(health_pass, "Merged-Unreleased Scope Posture")
    )
    if str(info["branch_class"]) == "implementation":
        require(
            _gate_state_matches(merged_unreleased_state, {"PASS"})
            and "merged-unreleased" in f"{health_pass}\n{post_merge_state}".casefold(),
            (
                f"{record_path}: implementation PRs must record the merged-unreleased "
                "scope posture before merge when release execution is not being performed"
            ),
        )


def _run_pr_origin_main_freshness_gate(
    require,
    *,
    active_branch_record_path: str,
    active_branch_record_text: str,
) -> None:
    if not active_branch_record_text:
        return

    info = _parse_workstream_doc(active_branch_record_text)
    if str(info["current_phase"]) != "PR Readiness":
        return

    freshness = _section(active_branch_record_text, "Origin/Main Freshness Check")
    if not freshness:
        stage1_packet = _section(active_branch_record_text, "PR Readiness Stage 1 Analysis Packet")
        if "Origin/Main Freshness Check:" in stage1_packet:
            freshness = stage1_packet
    require(
        bool(freshness),
        (
            f"{active_branch_record_path}: PR Readiness Stage 1 requires "
            "Origin/Main Freshness Check fields in the Stage 1 packet before Stage 2 or PR creation"
        ),
    )
    if not freshness:
        return

    for marker in PR_READINESS_ORIGIN_MAIN_FRESHNESS_MARKERS:
        require(
            bool(_extract_marker_value(freshness, marker)),
            f"{active_branch_record_path}: Origin/Main Freshness Check is missing '{marker}:'",
        )

    mutation_status = _extract_marker_value(
        freshness, "Reconciliation Mutation Status"
    ).casefold()
    require(
        "no file fixes during stage 1" in mutation_status
        or ("analysis-only" in mutation_status and "no file" in mutation_status),
        (
            f"{active_branch_record_path}: Origin/Main Freshness Check must make "
            "reconciliation analysis-only with no file fixes during Stage 1"
        ),
    )

    advanced = _normalized_gate_state(
        _extract_marker_value(freshness, "Origin/Main Advanced Since Branch Creation")
    )
    reconciliation_required = _normalized_gate_state(
        _extract_marker_value(freshness, "Reconciliation Required")
    )
    reconciliation_list = _extract_marker_value(freshness, "Reconciliation File List")
    recommendation = _extract_marker_value(freshness, "Reconciliation Recommendation")
    if _gate_state_matches(advanced, {"YES"}) and _gate_state_matches(
        reconciliation_required, {"YES"}
    ):
        require(
            bool(reconciliation_list) and reconciliation_list.upper() not in {"NONE", "N/A"},
            (
                f"{active_branch_record_path}: Origin Main Reconciliation Packet Required; "
                "Reconciliation File List must enumerate every file/data owner needing review"
            ),
        )
        require(
            bool(recommendation) and recommendation.upper() not in {"NONE", "N/A"},
            (
                f"{active_branch_record_path}: Origin Main Reconciliation Packet Required; "
                "Reconciliation Recommendation must explain the recommended reconcile route"
            ),
        )


def _run_worktree_branch_identity_guard(
    require,
    *,
    current_git_branch: str,
    active_branch_record_path: str,
    active_branch_record_text: str,
    backlog_text: str,
    roadmap_text: str,
) -> None:
    if (
        not current_git_branch
        or current_git_branch == "main"
        or _is_standing_governance_intake_branch(current_git_branch)
        or not active_branch_record_text
    ):
        return

    info = _parse_workstream_doc(active_branch_record_text)
    if str(info["branch_class"]) != "implementation":
        return

    expected_record_path = active_branch_record_path.replace("\\", "/")
    for source_name, source_text in (
        ("Docs/feature_backlog.md", backlog_text),
        ("Docs/prebeta_roadmap.md", roadmap_text),
    ):
        posture = _section(source_text, "Current Branch Execution Posture")
        if not posture:
            continue

        current_execution_branch = _extract_colon_value(
            posture,
            "Current Execution Branch",
        ).strip().strip("`")
        active_authority_record = _extract_colon_value(
            posture,
            "Active Branch Authority Record",
        ).strip().strip("`").replace("\\", "/")

        require(
            current_execution_branch == current_git_branch,
            (
                f"{source_name}: Worktree Branch Identity Drift; Current Branch Execution "
                f"Posture must reassert current branch `{current_git_branch}` after "
                f"current-main reconciliation, found "
                f"`{current_execution_branch or 'missing'}`"
            ),
        )
        require(
            active_authority_record == expected_record_path,
            (
                f"{source_name}: Worktree Branch Identity Drift; Current Branch Execution "
                f"Posture must reassert active authority record `{expected_record_path}` "
                f"after current-main reconciliation, found "
                f"`{active_authority_record or 'missing'}`"
            ),
        )


def _run_pr_readiness_gate(
    require,
    backlog_entries: list[dict[str, str]],
    roadmap_text: str,
    ignored_branch_names: set[str],
    branch_record_class_map: dict[str, str],
    active_branch_record_path: str,
    active_branch_record_text: str,
    selected_owner=None,
) -> None:
    branch_name = _git_current_branch()
    if selected_owner is not None:
        active_branch_record_path,active_branch_record_text=selected_owner
        active_branch_record_paths={active_branch_record_path}
        current_active_branch_record_path=active_branch_record_path;current_active_branch_record_text=active_branch_record_text
        historical_branch_record_path='';historical_branch_record_text=''
    else:
        branch_record_index_text = _read_text(BRANCH_RECORD_INDEX)
        active_branch_record_paths = _collect_branch_record_paths(
            branch_record_index_text,
            "Active Branch Authority Records",
        )
        historical_branch_record_paths = _collect_branch_record_paths(
            branch_record_index_text,
            "Historical Branch Authority Records",
        )
        current_active_branch_record_path, current_active_branch_record_text = _active_branch_record_for_branch(
            active_branch_record_paths,
            branch_name,
        )
        historical_branch_record_path, historical_branch_record_text = _branch_record_for_branch(
            historical_branch_record_paths,
            branch_name,
        )
        if current_active_branch_record_text:
            active_branch_record_path = current_active_branch_record_path
            active_branch_record_text = current_active_branch_record_text
        if not active_branch_record_text:
            if historical_branch_record_text:
                active_branch_record_path = historical_branch_record_path
                active_branch_record_text = historical_branch_record_text
            else:
                branch_name = _git_current_branch()
                for entry in backlog_entries:
                    entry_branch = _extract_colon_value(entry["block"], "Branch").strip("`")
                    if entry_branch != branch_name:
                        continue
                    canonical_path = entry["canonical_path"]
                    if canonical_path:
                        active_branch_record_path = canonical_path
                        active_branch_record_text = _read_text(Path(canonical_path))
                    break
    status_output = _git_status_porcelain()
    require(
        not status_output,
        (
            "PR readiness gate: Dirty Branch blocker is active; worktree must be clean "
            "and required branch truth must be durable in commit history before PR READY: YES"
        ),
    )
    _run_pr_origin_main_freshness_gate(
        require,
        active_branch_record_path=active_branch_record_path,
        active_branch_record_text=active_branch_record_text,
    )
    _run_uts_results_pr_gate(require, [entry for entry in backlog_entries if _extract_colon_value(entry["block"], "Branch").strip("`")==branch_name])
    _run_next_workstream_gate(
        require,
        backlog_entries,
        roadmap_text,
        ignored_branch_names,
        branch_record_class_map,
        active_branch_record_text,
    )
    _run_merge_target_authority_projection_gate(
        require,
        active_branch_record_paths=active_branch_record_paths,
        active_branch_record_path=current_active_branch_record_path,
        active_branch_record_text=current_active_branch_record_text,
        merge_stable_branch_record_path=historical_branch_record_path,
        merge_stable_branch_record_text=historical_branch_record_text,
    )
    _run_release_readiness_health_gate(
        require,
        backlog_entries=backlog_entries,
        active_branch_record_path=active_branch_record_path,
        active_branch_record_text=active_branch_record_text,
        selected_owner=selected_owner,
    )
    _run_pr_live_state_gate(
        require,
        active_branch_record_path=active_branch_record_path,
        active_branch_record_text=active_branch_record_text,
    )


OPERATOR_GUIDE_DOC = Path("Docs/codex_user_guide.md")


def _strip_operator_guide_from_governance_mirror_globals() -> None:
    """Keep the USER-facing guide from becoming a binding governance mirror."""

    def strip_value(value):
        if isinstance(value, tuple):
            return tuple(item for item in value if item != OPERATOR_GUIDE_DOC)
        if isinstance(value, list):
            return [item for item in value if item != OPERATOR_GUIDE_DOC]
        if isinstance(value, set):
            return {item for item in value if item != OPERATOR_GUIDE_DOC}
        if isinstance(value, frozenset):
            return frozenset(item for item in value if item != OPERATOR_GUIDE_DOC)
        if isinstance(value, dict) and OPERATOR_GUIDE_DOC in value:
            return {key: item for key, item in value.items() if key != OPERATOR_GUIDE_DOC}
        return value

    for name, value in list(globals().items()):
        if not name.isupper():
            continue
        globals()[name] = strip_value(value)


def _legacy_diagnostic_main() -> int:
    # Stable material owners replace copied policy paragraphs in routers.
    router = _read_text(Path("Docs/Main.md"))
    required_owners = ("Docs/phase_governance.md", "Docs/development_rules.md",
        "Docs/branch_plans/README.md", "Docs/branch_records/index.md",
        "Docs/workstreams/index.md", "Docs/validation_helper_registry.md",
        "Docs/governance_efficiency_operating_model.md", "Docs/nexus_workspace_roots.md")
    route_failures = [owner for owner in required_owners
        if owner not in router or not (ROOT_DIR / owner).is_file()]
    if route_failures:
        print("BLOCK: missing current owner routes: " + ", ".join(route_failures))
        return 1
    _strip_operator_guide_from_governance_mirror_globals()

    pr_readiness_gate = "--pr-readiness-gate" in sys.argv[1:]
    release_readiness_health_gate = "--release-readiness-health-gate" in sys.argv[1:]
    standing_governance_intake_gate = "--standing-governance-intake-gate" in sys.argv[1:]
    worktree_confinement_gate = "--worktree-confinement-gate" in sys.argv[1:]
    errors: list[str] = []
    checks = 0

    backlog_text = _read_text(Path("Docs/feature_backlog.md"))
    roadmap_text = _read_text(Path("Docs/prebeta_roadmap.md"))
    worktree_slots_text = _read_text(Path("Docs/worktree_slots.md"))
    index_text = _read_text(Path("Docs/workstreams/index.md"))
    branch_record_index_text = _read_text(BRANCH_RECORD_INDEX)
    main_text = _read_text(Path("Docs/Main.md"))
    development_rules_text = _read_text(Path("Docs/development_rules.md"))
    phase_governance_text = _read_text(Path("Docs/phase_governance.md"))
    branch_plans_readme_text = _read_text(Path("Docs/branch_plans/README.md"))
    validation_helper_registry_text = _read_text(Path("Docs/validation_helper_registry.md"))
    main_canonical_workstream_routes = _subsection(main_text, "Canonical Workstream Records")
    compact_source_truth_reform = _docs_source_truth_reform_active(backlog_text, roadmap_text)

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    current_git_branch = _git_current_branch()
    outside_lane_merge_stable_findings: list[str] = []

    rar_substantive_docs = {
        Path("Docs/phase_governance.md"): phase_governance_text,
        Path("Docs/branch_plans/README.md"): branch_plans_readme_text,
        Path("Docs/validation_helper_registry.md"): validation_helper_registry_text,
    }
    rar_substantive_phrases = (
        "RAR Shallow Audit",
        "RAR Ledger Pair Missing",
        "Current Branch Active Repair Ledger",
        "Historical / Previous Branch Issue Candidate Ledger",
        "RAR Element Group Rows Missing",
        "RAR Sampling Justification Missing",
        "RAR Comparator Classification Missing",
        "RAR Row Disposition Missing",
    )
    for relative_path, text in rar_substantive_docs.items():
        for required_phrase in rar_substantive_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: RAR substantive/exhaustive gate is missing '{required_phrase}'",
            )

    for occurrence in _tracked_repo_legacy_product_name_occurrences():
        require(False, f"Tracked repo sterilization: {occurrence}")

    _run_merge_stable_source_truth_projection_gate(
        require,
        backlog_text=backlog_text,
        roadmap_text=roadmap_text,
        worktree_slots_text=worktree_slots_text,
        branch_record_index_text=branch_record_index_text,
        current_branch=current_git_branch,
        outside_lane_findings=outside_lane_merge_stable_findings,
    )
    _run_post_merge_fold_down_drift_gate(
        require,
        backlog_text=backlog_text,
        roadmap_text=roadmap_text,
        branch_record_index_text=branch_record_index_text,
    )

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

    user_guide_text = _read_text(OPERATOR_GUIDE_DOC)
    for field_label in (
        "not binding governance",
        "Quick Prompts",
        "Scope Coverage Manifest",
        "Mode:",
        "Phase:",
        "Workstream:",
        "Branch:",
    ):
        require(
            field_label in user_guide_text,
            f"{OPERATOR_GUIDE_DOC}: operator quick-reference no longer mentions '{field_label}'",
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

    for relative_path in FEATURE_BRANCH_REPAIR_CONTRACT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in FEATURE_BRANCH_REPAIR_CONTRACT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: feature-branch repair contract is missing '{required_phrase}'",
            )

    for relative_path in GOVERNANCE_ONLY_BLOCK_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in GOVERNANCE_ONLY_BLOCK_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: governance-only / between-branch repair blocker guidance is missing '{required_phrase}'",
            )

    for relative_path in STANDING_GOVERNANCE_INTAKE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in STANDING_GOVERNANCE_INTAKE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Standing Governance Intake Branch guidance is missing '{required_phrase}'",
            )

    standard_text = _read_text(GOVERNANCE_INTAKE_DIGEST_STANDARD_DOC)
    require(
        bool(standard_text),
        f"{GOVERNANCE_INTAKE_DIGEST_STANDARD_DOC}: governance intake triage / digest profile standard is missing",
    )
    # Obsolete copied policy prose check retired.
    for relative_path in GOVERNANCE_INTAKE_DIGEST_POINTER_DOCS:
        text = _read_text(relative_path)
        for required_phrase in GOVERNANCE_INTAKE_DIGEST_POINTER_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: governance intake triage / digest profile pointer is missing '{required_phrase}'",
            )

    rebaseline_audit_source = _read_text(WORKTREE_REBASELINE_AUDIT_HELPER)
    require(
        bool(rebaseline_audit_source),
        f"{WORKTREE_REBASELINE_AUDIT_HELPER}: worktree rebaseline audit helper is missing",
    )
    for required_phrase in WORKTREE_REBASELINE_AUDIT_SOURCE_PHRASES:
        require(
            required_phrase in rebaseline_audit_source,
            f"{WORKTREE_REBASELINE_AUDIT_HELPER}: report-only audit helper source is missing '{required_phrase}'",
        )
    for relative_path in WORKTREE_REBASELINE_AUDIT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in WORKTREE_REBASELINE_AUDIT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: worktree rebaseline audit helper guidance is missing '{required_phrase}'",
            )

    validation_suite_source = _read_text(VALIDATION_SUITE_HELPER)
    require(
        bool(validation_suite_source),
        f"{VALIDATION_SUITE_HELPER}: validation suite recommendation helper is missing",
    )
    for required_phrase in VALIDATION_SUITE_SOURCE_PHRASES:
        require(
            required_phrase in validation_suite_source,
            f"{VALIDATION_SUITE_HELPER}: validation suite helper source is missing '{required_phrase}'",
        )
    for relative_path in VALIDATION_SUITE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in VALIDATION_SUITE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: validation suite helper guidance is missing '{required_phrase}'",
            )

    efficiency_model_text = _read_text(GOVERNANCE_EFFICIENCY_OPERATING_MODEL)
    require(
        bool(efficiency_model_text),
        f"{GOVERNANCE_EFFICIENCY_OPERATING_MODEL}: governance efficiency operating model is missing",
    )
    for required_phrase in GOVERNANCE_EFFICIENCY_OPERATING_MODEL_PHRASES:
        require(
            required_phrase in efficiency_model_text,
            (
                f"{GOVERNANCE_EFFICIENCY_OPERATING_MODEL}: governance efficiency "
                f"operating model is missing '{required_phrase}'"
            ),
        )

    efficiency_source = _read_text(GOVERNANCE_EFFICIENCY_VALIDATION_HELPER)
    require(
        bool(efficiency_source),
        f"{GOVERNANCE_EFFICIENCY_VALIDATION_HELPER}: governance efficiency validator is missing",
    )
    for required_phrase in GOVERNANCE_EFFICIENCY_SOURCE_PHRASES:
        require(
            required_phrase in efficiency_source,
            (
                f"{GOVERNANCE_EFFICIENCY_VALIDATION_HELPER}: governance efficiency "
                f"validator source is missing '{required_phrase}'"
            ),
        )

    for relative_path in GOVERNANCE_EFFICIENCY_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in GOVERNANCE_EFFICIENCY_POINTER_PHRASES:
            require(
                required_phrase.casefold() in lower_text,
                (
                    f"{relative_path}: governance efficiency operating model pointer "
                    f"is missing '{required_phrase}'"
                ),
            )

    if not compact_source_truth_reform:
        for relative_path in CURRENT_DECISION_SURFACE_DOCS:
            text = _read_text(relative_path)
            for required_phrase in CURRENT_DECISION_SURFACE_PHRASES:
                require(
                    required_phrase in text,
                    f"{relative_path}: Current Decision Surface is missing '{required_phrase}'",
                )
        for relative_path in CURRENT_DECISION_SURFACE_POINTER_DOCS:
            text = _read_text(relative_path)
            for required_phrase in ("Current Decision Surface", "Latest Public Prerelease Recorded In Source Truth:"):
                require(
                    required_phrase in text,
                    f"{relative_path}: Current Decision Surface pointer is missing '{required_phrase}'",
                )
    else:
        for relative_path in CURRENT_DECISION_SURFACE_DOCS:
            text = _read_text(relative_path)
            require(
                DOCS_SOURCE_TRUTH_REFORM_MARKER in text,
                f"{relative_path}: compact pointer-layer source-truth marker is missing",
            )

    for relative_path in ASSIGNED_WORKTREE_CONFINEMENT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in ASSIGNED_WORKTREE_CONFINEMENT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: assigned worktree confinement guidance is missing '{required_phrase}'",
            )

    for relative_path in FAMILY_SCOPED_BRANCH_READINESS_DOCS:
        text = _read_text(relative_path)
        for required_phrase in FAMILY_SCOPED_BRANCH_READINESS_PHRASES:
            require(
                required_phrase in text,
                (
                    f"{relative_path}: family-scoped Branch Readiness confinement guidance "
                    f"is missing '{required_phrase}'"
                ),
            )

    for relative_path in MULTI_SEAM_CONTRACT_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in MULTI_SEAM_CONTRACT_PHRASES:
            require(
                required_phrase.casefold() in lower_text,
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

    for relative_path, required_phrases in BRANCH_SLICE_SLC_SEAM_TERMINOLOGY_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: Branch/Slice/SLC/Seam terminology model is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in MANDATORY_BOUNDED_STATE_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in required_phrases:
            require(
                required_phrase.casefold() in lower_text,
                f"{relative_path}: mandatory bounded-state governance is missing '{required_phrase}'",
            )

    fam007_record_path = Path(
        "Docs/branch_records/feature_fam_007_provider_boundary_no_provider_shell.md"
    )
    fam007_record_text = _read_text(fam007_record_path)
    for required_phrase in FAM007_BOUNDED_STATE_RECORD_REQUIRED_PHRASES:
        require(
            required_phrase in fam007_record_text,
            f"{fam007_record_path}: FAM-007 bounded-state lock is missing '{required_phrase}'",
        )

    fam006_monitor_groups_record_path = Path(
        "Docs/branch_records/feature_fam_006_monitor_groups_sensor_configuration.md"
    )
    fam006_monitor_groups_record_text = _read_text(fam006_monitor_groups_record_path)
    for required_phrase in (
        "## Sensor Library And Profile Planning Admission",
        "Sensor Library = all available or planned data sources",
        "Monitor = one configured tracked item",
        "Monitor Group = organization/configuration collection",
        "Overlay Profile = selected monitors plus layout visible on overlay",
        "Recording Profile = selected monitors or sensors logged to file",
        "Monitor Groups do not own overlay visibility, recording selection, or recording output behavior",
        "Sensor Library must support searchable and filterable source discovery",
        "Manage Monitors must scale to hundreds of monitors and thousands of data sources",
        "Active Overlay Only",
        "Active Monitor Group",
        "All Enabled Monitors",
        "Custom Recording Profile",
        "Selected Sensors",
        "Start Recording",
        "Stop Recording",
        "Open Recordings Folder",
        "Recording Settings",
        "CSV data plus JSON metadata and sensor manifest",
        "profile name",
        "hardware snapshot",
        "event markers during recording",
        "auto-record triggers",
        "Save Last 5 Minutes",
        "Recordings are saved locally by default",
        "enabled, visible, recorded, warning-enabled, or hidden independently",
        "no runtime recording, Overlay Profile UI, tray recording controls, export/share behavior",
        "returned USER UTS FAIL",
        "## Returned UTS FAIL Repair Setup Admission",
        "Repair Setup Status: `ADMITTED - Branch Readiness Stage 2`",
        "current-main reconciliation is complete",
        "Dashboard resize/move live render smoothness",
        "shrink and grow resize visual continuity",
        "during-drag frame, pixel-signature, or video-style proof before mouse release",
        "Manage Monitors scalable split layout",
        "Nexus-styled scrollbars in child windows, monitor list, detail pane, sensor tree, sensor result list, and sensor preview/details pane",
        "large-monitor and large-source fixtures",
        "PR Readiness remains blocked pending repair implementation",
        "## Returned Refreshed UTS FAIL Sensor Command Center Repair Setup Admission",
        "Returned Refreshed UTS Classification",
        "Visible Resize-Proof Contamination Setup",
        "proof-only visible artifacts",
        "Invisible / Test-Gated Resize Proof Setup",
        "invisible/test-gated",
        "Sensor Command Center Setup",
        "compact action-light monitor list",
        "row/icon selection",
        "right-side detail panel",
        "detail-pane Delete",
        "Save / Discard / Cancel guard",
        "final-monitor delete",
        "true empty state",
        "Sensor Library / Source Picker Setup",
        "dropdown/facets",
        "Warning Notifications classified as a monitor/settings checkbox",
        "Provider Readiness classified as readiness/status/future capability",
        "provider > device > category > metric > instance",
        "source status metadata",
        "Dropdown Repair And Proof Setup",
        "open, hover, close, reopen",
        "Large Fixture / Edge Case Proof Setup",
        "100+ monitors",
        "1,000+ sources",
        "duplicate source names",
        "long monitor names",
        "long source names",
        "deferred sources",
        "missing sources",
        "source classification",
        "Future Workflow Preservation",
        "## Refreshed LV1 Interactive Control Visual QA Repair Setup Admission",
        "Interactive Control Visual QA Gate",
        "All user-facing interactable controls must pass code inspection and focused visual inspection",
        "buttons, user-facing dropdowns, checkboxes, selectable rows, search fields, filter controls, scrollbars, close controls, delete confirmations, empty-state actions, source-picker controls",
        "Code Inspection Requirement",
        "Focused Visual Inspection Requirement",
        "Empty-State Repair Scope",
        "Save Monitor and Discard must not appear as valid actions",
        "Create Monitor must be the primary recovery action",
        "reject manifest-only or DOM-only PASS when focused screenshots show invalid interactive controls",
        "## Refreshed LV1 Dashboard Right-Edge Rediscovery Repair Setup Admission",
        "post-corner right-edge resize cursor rediscovery",
        "Initial right-edge hit-test passed with rightEdge10px=htright",
        "rightOutside=True / htright / size-west-east / offset=1",
        "corner resize passed and changed the Dashboard from 780x1060 to 860x1130",
        "Dashboard element, native/root handle, bounding rect, DPI/scale context, virtual desktop bounds, and visible-edge coordinates",
        "Diagnostic Sweep Planning",
        "x/y sample coordinates, offset from visible edge, cursor kind, native hit-test result, root/window handle at point, expected Dashboard handle, bounding rect, virtual desktop bounds, timing, and settle state",
        "Post-Resize Settle Planning",
        "geometry stable, rounded mask applied, WebView visible, active resize state cleared, and cursor reset",
        "Manage Monitors focused LV1 states remain pending recheck",
    ):
        require(
            required_phrase in fam006_monitor_groups_record_text,
            (
                f"{fam006_monitor_groups_record_path}: FAM-006 Monitor Groups "
                f"profile planning admission is missing '{required_phrase}'"
            ),
        )
    if not compact_source_truth_reform:
        for current_state_path, current_state_text in (
            (Path("Docs/feature_backlog.md"), backlog_text),
            (Path("Docs/prebeta_roadmap.md"), roadmap_text),
        ):
            for required_phrase in (
                "Sensor Library",
                "Sensor Command Center",
                "visible resize-proof contamination",
                "invisible/test-gated",
                "Warning Notifications",
                "Provider Readiness",
                "Overlay Profile",
                "Recording Profile",
                "returned USER UTS FAIL",
                "interactive-control visual QA",
                "right-edge resize rediscovery",
                "PR Readiness remains blocked",
            ):
                require(
                    required_phrase in current_state_text,
                    (
                        f"{current_state_path}: FAM-006 Monitor Groups profile planning "
                        f"sync is missing '{required_phrase}'"
                    ),
                )
    else:
        for required_phrase in (
            "Sensor Library",
            "Sensor Command Center",
            "Warning Notifications",
            "Provider Readiness",
            "Overlay Profile",
            "Recording Profile",
        ):
            require(
                required_phrase in fam006_monitor_groups_record_text,
                (
                    f"{fam006_monitor_groups_record_path}: compact backlog/roadmap reform "
                    f"requires FAM-006 detail to remain in the branch record; missing '{required_phrase}'"
                ),
            )

    for relative_path in INTERFACE_RELEASE_BOUNDARY_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in INTERFACE_RELEASE_BOUNDARY_PHRASES:
            require(
                required_phrase.casefold() in lower_text,
                f"{relative_path}: interface release boundary governance is missing '{required_phrase}'",
            )

    phase_governance_text = _read_text(Path("Docs/phase_governance.md"))
    phase_governance_lower = phase_governance_text.casefold()
    for required_phrase in MULTI_SEAM_PRIMARY_REPAIR_PHRASES:
        require(
            required_phrase.casefold() in phase_governance_lower,
            f"Docs/phase_governance.md: primary seam governance is missing category-stop repair phrase '{required_phrase}'",
        )

    for relative_path in MULTI_SEAM_PROMPT_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in MULTI_SEAM_PROMPT_PHRASES:
            require(
                required_phrase.casefold() in lower_text,
                f"{relative_path}: multi-seam prompt scaffold is missing '{required_phrase}'",
            )
        for prohibited_phrase in MULTI_SEAM_PROHIBITED_THROTTLE_PHRASES:
            require(
                prohibited_phrase not in lower_text,
                f"{relative_path}: prompt scaffold must not recreate single-seam throttling authority via '{prohibited_phrase}'",
            )

    for relative_path, retired_terms in REUSABLE_GUIDANCE_RETIRED_SEAM_TERMS.items():
        text = _read_text(relative_path)
        for retired_term in retired_terms:
            require(
                retired_term not in text,
                f"{relative_path}: reusable guidance must not reintroduce retired seam-governance term '{retired_term}'",
            )

    # PR phase safety is checked against actual phase/approval, not router prose.

    for relative_path in PRE_PR_DURABILITY_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PRE_PR_DURABILITY_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Pre-PR Durability Rule is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in AUTOMATION_RUNTIME_PROOF_CONTRACT_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: automation runtime-proof governance is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in AUTOMATION_RUNTIME_PROOF_CURRENT_STATE_REQUIRED_PHRASES.items():
        if compact_source_truth_reform and relative_path in {
            Path("Docs/feature_backlog.md"),
            Path("Docs/prebeta_roadmap.md"),
        }:
            continue
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: current-state runtime-proof summary is missing '{required_phrase}'",
            )

    for relative_path in PLANNING_LOOP_GUARDRAIL_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PLANNING_LOOP_GUARDRAIL_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: planning-loop guardrail guidance is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in PROMPT_DISCIPLINE_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: thin prompt discipline guidance is missing '{required_phrase}'",
            )

    for relative_path, prohibited_phrases in PROMPT_DISCIPLINE_PROHIBITED_PHRASES.items():
        text = _read_text(relative_path)
        for prohibited_phrase in prohibited_phrases:
            require(
                prohibited_phrase not in text,
                f"{relative_path}: prompt-discipline drift reintroduced prohibited phrase '{prohibited_phrase}'",
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

    for relative_path in LIVE_VALIDATION_AUTO_REPAIR_DOCS:
        text = _read_text(relative_path)
        lower_text = text.casefold()
        for required_phrase in LIVE_VALIDATION_AUTO_REPAIR_PHRASES:
            require(
                required_phrase in lower_text,
                f"{relative_path}: Live Validation automatic repair/rerun guidance is missing '{required_phrase}'",
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

    for relative_path in PACKAGE_SLICE_BLOCKER_CATALOG_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PACKAGE_SLICE_BLOCKER_CATALOG_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: package/slice blocker catalog is missing '{required_phrase}'",
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

    for relative_path in PR_READINESS_STAGE_GATE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PR_READINESS_STAGE_GATE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: PR Readiness stage gate guidance is missing '{required_phrase}'",
            )

    for relative_path in PR_READINESS_STAGE_PACKET_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PR_READINESS_STAGE_PACKET_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: PR Readiness Stage 1 packet contract is missing '{required_phrase}'",
            )

    for relative_path in PR_READINESS_ORIGIN_MAIN_FRESHNESS_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PR_READINESS_ORIGIN_MAIN_FRESHNESS_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: PR Readiness origin/main freshness guidance is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in PROMPT_ENTRY_ORIGIN_MAIN_FRESHNESS_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: prompt-entry origin/main freshness guidance is missing '{required_phrase}'",
            )

    for relative_path in PRE_REBASELINE_IMPACT_AUDIT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PRE_REBASELINE_IMPACT_AUDIT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Pre-Rebaseline Impact Audit guidance is missing '{required_phrase}'",
            )

    pre_rebaseline_helper_text = _read_text(Path("dev/orin_worktree_rebaseline_audit.py"))
    for required_phrase in PRE_REBASELINE_HELPER_PHRASES:
        require(
            required_phrase in pre_rebaseline_helper_text,
            f"dev/orin_worktree_rebaseline_audit.py: report-only helper is missing '{required_phrase}'",
        )

    for relative_path in CURRENT_MAIN_RECONCILIATION_IDENTITY_DOCS:
        text = _read_text(relative_path)
        for required_phrase in CURRENT_MAIN_RECONCILIATION_IDENTITY_PHRASES:
            require(
                required_phrase in text,
                (
                    f"{relative_path}: current-main reconciliation identity guidance "
                    f"is missing '{required_phrase}'"
                ),
            )

    for relative_path in RELEASE_READINESS_HEALTH_GATE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in RELEASE_READINESS_HEALTH_GATE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Release Readiness Health Pass guidance is missing '{required_phrase}'",
            )

    for relative_path in STALE_BRANCH_CLEANUP_DOCS:
        text = _read_text(relative_path)
        for required_phrase in STALE_BRANCH_CLEANUP_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: stale branch cleanup governance is missing '{required_phrase}'",
            )

    for relative_path in STABLE_WORKTREE_PATH_PRESERVATION_DOCS:
        text = _read_text(relative_path)
        for required_phrase in STABLE_WORKTREE_PATH_PRESERVATION_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: stable worktree path preservation governance is missing '{required_phrase}'",
            )

    for relative_path in BRANCH_READINESS_CARRIER_LIFECYCLE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in BRANCH_READINESS_CARRIER_LIFECYCLE_PHRASES:
            require(
                required_phrase in text,
                (
                    f"{relative_path}: Branch Readiness carrier lifecycle "
                    f"governance is missing '{required_phrase}'"
                ),
            )

    for relative_path, required_phrases in PR_READINESS_STAGE1_READINESS_LOCK_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: PR Readiness Stage 1 readiness-lock guidance is missing '{required_phrase}'",
            )

    for relative_path in NEXT_LEGAL_PHASE_DIGEST_DOCS:
        text = _read_text(relative_path)
        for required_phrase in NEXT_LEGAL_PHASE_DIGEST_REQUIRED_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Next Legal Phase Digest guidance is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in NEXT_LEGAL_PHASE_DIGEST_POINTER_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: Next Legal Phase Digest routing pointer is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in MAIN_FIRST_LOADER_CHAIN_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: Main-first loader chain guidance is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in WORKSTREAM_ENTRY_WHOLE_PACKAGE_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: Workstream Entry whole-package analysis guidance is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in USER_BRANCH_PLAN_REVIEW_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: USER Branch Plan Review Gate guidance is missing '{required_phrase}'",
            )

    # Obsolete copied policy prose check retired.

    for relative_path in BRANCH_READINESS_STAGE_GATE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in BRANCH_READINESS_STAGE_GATE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Branch Readiness stage gate guidance is missing '{required_phrase}'",
            )

    for relative_path in BRANCH_READINESS_STAGE_PACKET_DOCS:
        text = _read_text(relative_path)
        for required_phrase in BRANCH_READINESS_STAGE_PACKET_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Branch Readiness Stage 1 packet contract is missing '{required_phrase}'",
            )

    for relative_path in RUNTIME_ENGINEERING_CONTRACT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in RUNTIME_ENGINEERING_CONTRACT_PHRASES:
            require(
                required_phrase in text,
                (
                    f"{relative_path}: Runtime Branch Engineering Contract guidance "
                    f"is missing '{required_phrase}'"
                ),
            )

    for relative_path, required_phrases in BRANCH_RUNTIME_ENGINEERING_PLAN_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                (
                    f"{relative_path}: Branch Runtime Engineering Plan guidance "
                    f"is missing '{required_phrase}'"
                ),
            )

    for relative_path, required_phrases in USER_FEEDBACK_DISPOSITION_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                (
                    f"{relative_path}: USER Feedback Disposition guidance "
                    f"is missing '{required_phrase}'"
                ),
            )

    for relative_path in BRANCH_RUNTIME_ENGINEERING_PLAN_COMPACT_POINTER_SURFACES:
        _validate_branch_runtime_backlog_compactness(
            require,
            str(relative_path),
            _read_text(relative_path),
        )

    for relative_path, required_phrases in CHATGPT_LOADER_SOURCE_TRUTH_SYNC_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: ChatGPT loader/source-truth sync is missing '{required_phrase}'",
            )

    for relative_path in ELEMENT_COVERAGE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in ELEMENT_COVERAGE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Element Coverage governance is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in ELEMENT_VALIDATION_LEDGER_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: Element Validation Ledger governance is missing '{required_phrase}'",
            )

    fam006_branch_text = _read_text(FAM006_BRANCH_RECORD)
    fam006_real_client_section = _section(
        fam006_branch_text, FAM006_STAGE2_REAL_CLIENT_HEADING
    )
    require(
        bool(fam006_real_client_section),
        (
            f"{FAM006_BRANCH_RECORD}: FAM-006 real-client returned-failure repair "
            f"is missing '## {FAM006_STAGE2_REAL_CLIENT_HEADING}'"
        ),
    )
    for required_phrase in FAM006_STAGE2_REAL_CLIENT_REQUIRED_PHRASES:
        require(
            required_phrase in fam006_real_client_section,
            (
                f"{FAM006_BRANCH_RECORD}: {FAM006_STAGE2_REAL_CLIENT_HEADING} "
                f"is missing '{required_phrase}'"
            ),
        )
    for required_phrase in FAM006_ELEMENT_VALIDATION_LEDGER_REQUIRED_PHRASES:
        require(
            required_phrase in fam006_branch_text,
            f"{FAM006_BRANCH_RECORD}: FAM-006 Element Validation Ledger is missing '{required_phrase}'",
        )

    for issue_id in (f"FAM006-RUI-{index:03d}" for index in range(1, 44)):
        require(
            issue_id in fam006_branch_text,
            f"{FAM006_BRANCH_RECORD}: Returned USER Issue Register is missing '{issue_id}'",
        )

    fam006_element_ledger_text = _read_text(FAM006_ELEMENT_LEDGER)
    for required_phrase in FAM006_ELEMENT_LEDGER_REQUIRED_PHRASES:
        require(
            required_phrase in fam006_element_ledger_text,
            f"{FAM006_ELEMENT_LEDGER}: FAM-006 companion Element Validation Ledger is missing '{required_phrase}'",
        )

    for relative_path, required_phrases in (
        SOURCE_OWNER_MARKER_ADOPTION_NEXT_BRANCH_REQUIRED_PHRASES.items()
    ):
        if compact_source_truth_reform and relative_path in {
            Path("Docs/feature_backlog.md"),
            Path("Docs/prebeta_roadmap.md"),
        }:
            continue
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: post-FAM-006 source-owner marker adoption requirement is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in (
        FAM006_REAL_CLIENT_PROOF_GOVERNANCE_REQUIRED_PHRASES.items()
    ):
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: real-client proof governance is missing '{required_phrase}'",
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

    for relative_path in BOT_REVIEW_SIGNAL_DOCS:
        text = _read_text(relative_path)
        for required_phrase in BOT_REVIEW_SIGNAL_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: bot-review signal contract is missing '{required_phrase}'",
            )
    branch_governance_validator_text = _read_text(Path("dev/orin_branch_governance_validation.py"))
    for required_phrase in (
        "headRefOid",
        "commits(last: 1)",
        "timelineItems",
        "PULL_REQUEST_COMMIT",
        "committedDate",
        "pushedDate",
        "reactions(first: 100, content: THUMBS_UP)",
        "_github_pr_review_request_comment_matches",
        "current_head_admission_time",
        "current_head_commit_time",
        "current_head_review_request_time",
        "current_head_index is None and current_head_admission_time is None",
        "current_head_review_request_time or current_head_admission_time",
        "current_head_reaction_floor_time",
        "PR-level thumbs-up reaction",
        "issues/{pr_number}/reactions",
        "signal_head == current_head_sha",
    ):
        require(
            required_phrase in branch_governance_validator_text,
            (
                "dev/orin_branch_governance_validation.py: Codex bot-review signal "
                f"current-head proof is missing '{required_phrase}'"
            ),
        )
    legacy_commit_time_latch = "signal_time and " + "current_head_time"
    require(
        legacy_commit_time_latch not in branch_governance_validator_text,
        (
            "dev/orin_branch_governance_validation.py: Codex bot-review signal proof "
            "must not compare approval time to local HEAD commit time"
        ),
    )
    forbidden_pushed_committed_fallback = (
        'commit_payload.get("pushedDate")'
        + '\n            or commit_payload.get("committedDate")'
    )
    forbidden_reaction_commit_floor = (
        "current_head_reaction_floor_time = current_head_" + "commit_time"
    )
    for forbidden_phrase in (
        forbidden_pushed_committed_fallback,
        forbidden_reaction_commit_floor,
    ):
        require(
            forbidden_phrase not in branch_governance_validator_text,
            (
                "dev/orin_branch_governance_validation.py: Codex bot-review signal proof "
                "must not use local commit time as the PR-head admission fallback"
            ),
        )

    for relative_path in PR_WATCHER_THREAD_CONTRACT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PR_WATCHER_THREAD_CONTRACT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: PR watcher same-thread contract is missing '{required_phrase}'",
            )

    watcher_mode_contract_text = _read_text(PR_WATCHER_MODE_CONTRACT_DOC)
    for required_phrase in PR_WATCHER_MODE_CONTRACT_PHRASES:
        require(
            required_phrase in watcher_mode_contract_text,
            f"{PR_WATCHER_MODE_CONTRACT_DOC}: PR watcher mode contract is missing '{required_phrase}'",
        )
    for relative_path in PR_WATCHER_MODE_CONTRACT_POINTER_DOCS:
        text = _read_text(relative_path)
        for required_phrase in PR_WATCHER_MODE_CONTRACT_PHRASES[:6]:
            require(
                required_phrase in text,
                f"{relative_path}: PR watcher mode contract pointer is missing '{required_phrase}'",
            )
    for relative_path in PR_WATCHER_DENIAL_POLICY_DOCS:
        text = _read_text(relative_path)
        text_lower = text.casefold()
        for required_phrase in PR_WATCHER_DENIAL_POLICY_PHRASES:
            require(
                required_phrase.casefold() in text_lower,
                (
                    f"{relative_path}: PR watcher denial policy is missing "
                    f"'{required_phrase}'"
                ),
            )
        for forbidden_phrase in PR_WATCHER_DENIAL_FORBIDDEN_PHRASES:
            require(
                forbidden_phrase.casefold() not in text_lower,
                (
                    f"{relative_path}: stale PR watcher default wording remains "
                    f"'{forbidden_phrase}'"
                ),
            )

    watcher_output_source = _read_text(PR_WATCHER_OUTPUT_CONTRACT_SOURCE)
    for required_phrase in PR_WATCHER_OUTPUT_CONTRACT_PHRASES:
        require(
            required_phrase in watcher_output_source,
            f"{PR_WATCHER_OUTPUT_CONTRACT_SOURCE}: watcher output contract is missing '{required_phrase}'",
        )

    automation_observability_source = _read_text(AUTOMATION_OBSERVABILITY_SOURCE)
    for required_phrase in AUTOMATION_OBSERVABILITY_SOURCE_PHRASES:
        require(
            required_phrase in automation_observability_source,
            (
                f"{AUTOMATION_OBSERVABILITY_SOURCE}: automation observability helper "
                f"is missing '{required_phrase}'"
            ),
        )
    for relative_path in AUTOMATION_OBSERVABILITY_DOCS:
        text = _read_text(relative_path)
        for required_phrase in AUTOMATION_OBSERVABILITY_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: automation observability contract is missing '{required_phrase}'",
            )

    for relative_path in GOVERNANCE_RECURRENCE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in GOVERNANCE_RECURRENCE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: governance recurrence guidance is missing '{required_phrase}'",
            )

    for relative_path in POST_MERGE_CLOSEOUT_PROOF_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in POST_MERGE_CLOSEOUT_PROOF_PHRASES:
            require(
                required_phrase.casefold() in text,
                f"{relative_path}: post-merge closeout proof guidance is missing '{required_phrase}'",
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

    for relative_path in CODEX_LIVE_CLIENT_SELF_QA_DOCS:
        text = _read_text(relative_path)
        for required_phrase in CODEX_LIVE_CLIENT_SELF_QA_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: Codex live-client self-QA gate guidance is missing '{required_phrase}'",
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

    for relative_path in PROTECTED_MAIN_RELEASE_CLOSURE_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in PROTECTED_MAIN_RELEASE_CLOSURE_PHRASES:
            require(
                required_phrase.casefold() in text,
                f"{relative_path}: protected-main release-closure governance is missing '{required_phrase}'",
            )

    for relative_path in MERGED_UNRELEASED_CONTRACT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in MERGED_UNRELEASED_CONTRACT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: merged-unreleased release-debt contract is missing '{required_phrase}'",
            )

    for relative_path, required_phrases in GOVERNED_OUTPUT_CONTRACT_REQUIRED_PHRASES.items():
        text = _read_text(relative_path)
        for required_phrase in required_phrases:
            require(
                required_phrase in text,
                f"{relative_path}: governed output state contract is missing '{required_phrase}'",
            )

    for relative_path in MERGE_STABLE_CURRENT_STATE_DOCS:
        text = _read_text(relative_path)
        for required_phrase in MERGE_STABLE_CURRENT_STATE_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: merge-stable current-state guidance is missing '{required_phrase}'",
            )

    if _is_merged_main_snapshot():
        status_output = _git_status_porcelain(tracked_only=True)
        require(
            not status_output,
            "Main Write Attempt blocker is active; Codex must not leave tracked file mutations on merged-main validation surfaces",
        )
        current_branch = _git_current_branch()
        head_sha = _git_head_sha()
        origin_main_sha = _git_ref_sha("refs/remotes/origin/main")
        if current_branch == "main" and head_sha and origin_main_sha:
            require(
                head_sha == origin_main_sha,
                (
                    "Protected-main release closure blocker is active; local `main` contains commits "
                    "that are not in `origin/main`. A local-only post-release closure commit is not "
                    "completed source truth and must route through the next approved Branch "
                    "Readiness Stage 2 canon/governance repair carrier before runtime "
                    "implementation can resume."
                ),
            )

    active_index_paths = _collect_active_index_paths(index_text)
    closed_index_paths = _collect_closed_index_paths(index_text)
    release_debt_index_paths = _collect_release_debt_index_paths(index_text)
    active_branch_record_paths = _collect_branch_record_paths(branch_record_index_text, "Active Branch Authority Records")
    historical_branch_record_paths = _collect_branch_record_paths(branch_record_index_text, "Historical Branch Authority Records")
    durable_branch_receipt_paths = _collect_branch_record_paths(branch_record_index_text, "Durable Branch Receipt Records")
    active_non_standing_branch_record_paths = [
        path
        for path in active_branch_record_paths
        if path != STANDING_GOVERNANCE_INTAKE_RECORD_PATH
    ]
    require(
        not active_non_standing_branch_record_paths,
        (
            "Repo Active Operational State Prohibited: "
            "Docs/branch_records/index.md may not list non-standing active branch "
            "authority records after the External Operational State Store transition. "
            "Repo docs may keep durable branch/document evidence pointers and historical "
            "receipts only; active branch lifecycle state belongs in external operational "
            "state or Git/GitHub/helper-derived truth. Transition waivers may be preserved "
            "only as historical receipt evidence; they must not keep live branch state in repo docs. "
            "Offending record(s): "
            + ", ".join(sorted(active_non_standing_branch_record_paths))
        ),
    )
    _run_branch_record_live_state_leakage_fixtures(require)
    all_branch_record_detail_paths = _all_branch_record_detail_paths()
    indexed_branch_record_paths = active_branch_record_paths | historical_branch_record_paths | durable_branch_receipt_paths
    unindexed_branch_record_paths = all_branch_record_detail_paths - indexed_branch_record_paths
    for branch_record_path in sorted(all_branch_record_detail_paths):
        record_text = _read_text(Path(branch_record_path))
        leakage_findings = _branch_record_live_state_leakage_findings(
            branch_record_path,
            record_text,
            active_branch_record_paths,
        )
        require(
            not leakage_findings,
            (
                f"{branch_record_path}: Repo Branch Record Live-State Leakage; "
                "non-standing repo branch records are durable receipts/pointers, not live "
                "operational ledgers. Findings: "
                + ", ".join(sorted(set(leakage_findings)))
            ),
        )
    unindexed_leakage_records: list[str] = []
    for branch_record_path in sorted(unindexed_branch_record_paths):
        record_text = _read_text(Path(branch_record_path))
        leakage_findings = _branch_record_live_state_leakage_findings(
            branch_record_path,
            record_text,
            active_branch_record_paths,
        )
        if leakage_findings:
            unindexed_leakage_records.append(branch_record_path)
    require(
        not unindexed_leakage_records,
        (
            "Repo Branch Record Live-State Leakage: unindexed branch record(s) contain "
            "live-state markers and must be indexed as historical receipts, moved external, "
            "or folded down before validation can pass. Offending record(s): "
            + ", ".join(unindexed_leakage_records)
        ),
    )
    for prohibited_prefix in PROHIBITED_ACTIVE_BRANCH_PREFIXES:
        require(
            current_git_branch == "main" or not current_git_branch.startswith(prohibited_prefix),
            (
                f"Active git branch '{current_git_branch}' uses prohibited prefix "
                f"'{prohibited_prefix}'. Use `feature/` or another USER-approved "
                "non-`codex/` prefix for active Nexus work."
            ),
        )
    (
        branch_record_class_map,
        all_repair_branch_names,
        active_repair_branch_names,
        historical_branch_names,
    ) = _branch_record_branch_sets(
        active_branch_record_paths,
        historical_branch_record_paths | durable_branch_receipt_paths,
        current_git_branch,
    )
    active_branch_record_path, active_branch_record_text = _active_branch_record_for_branch(
        active_branch_record_paths,
        current_git_branch,
    )
    _run_worktree_branch_identity_guard(
        require,
        current_git_branch=current_git_branch,
        active_branch_record_path=active_branch_record_path,
        active_branch_record_text=active_branch_record_text,
        backlog_text=backlog_text,
        roadmap_text=roadmap_text,
    )
    ignored_selected_next_branch_names = _selected_next_ignored_branch_names(
        current_git_branch,
        all_repair_branch_names,
        active_repair_branch_names,
        historical_branch_names,
    )
    merged_no_active_branch_truth = (
        "Repo State: No Active Branch" in backlog_text or "Repo State: No Active Branch" in roadmap_text
    )
    if _is_merged_main_snapshot() and merged_no_active_branch_truth:
        require(
            not active_non_standing_branch_record_paths,
            (
                "Docs/branch_records/index.md: merged current-state canon declares `No Active Branch`, "
                "so `Active Branch Authority Records` may contain only the standing governance "
                f"intake exception `{STANDING_GOVERNANCE_INTAKE_RECORD_PATH}`"
            ),
        )
        if STANDING_GOVERNANCE_INTAKE_RECORD_PATH in active_branch_record_paths:
            standing_record_text = _read_text(STANDING_GOVERNANCE_INTAKE_RECORD)
            standing_record_info = _parse_workstream_doc(standing_record_text)
            require(
                str(standing_record_info["branch_class"]) == STANDING_GOVERNANCE_INTAKE_BRANCH_CLASS,
                (
                    f"{STANDING_GOVERNANCE_INTAKE_RECORD_PATH}: the only active authority "
                    "allowed under merged-main `No Active Branch` must have Branch Class "
                    f"`{STANDING_GOVERNANCE_INTAKE_BRANCH_CLASS}`"
                ),
            )
        pr101_closeout_record_text = _read_text(PR101_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD)
        pr101_closeout_phase = _extract_marker_value(
            _section(pr101_closeout_record_text, "Current Phase"),
            "Phase",
        )
        pr101_closeout_phase_status = _section(pr101_closeout_record_text, "Phase Status")
        require(
            pr101_closeout_phase == "Historical Traceability",
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "merged-main post-merge closeout record must report `Phase: Historical Traceability`"
            ),
        )
        require(
            "Historical repair PR: PR #102 merged at `2026-04-30T00:37:19Z`"
            in pr101_closeout_phase_status,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "historical PR #102 merge proof is missing from Phase Status"
            ),
        )
        require(
            "Historical watcher shutdown proof:" in pr101_closeout_phase_status,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "historical watcher shutdown proof is missing from Phase Status"
            ),
        )
        require(
            "Current PR Readiness Seam:" not in pr101_closeout_phase_status
            and "Live PR State: `open`" not in pr101_closeout_phase_status,
            (
                "Docs/branch_records/feature_pr101_post_merge_closeout_canon_repair.md: "
                "historical closeout record must not retain active PR-readiness or live-PR state on merged main"
            ),
        )
    if current_git_branch not in {"", "main"} and merged_no_active_branch_truth:
        for relative_path, text in (
            ("Docs/feature_backlog.md", backlog_text),
            ("Docs/prebeta_roadmap.md", roadmap_text),
        ):
            require(
                f"Current Active Branch: {current_git_branch}" not in text
                and f"Current Active Branch: `{current_git_branch}`" not in text,
                (
                    f"{relative_path}: merge-stable current-state owners must not mirror transient "
                    f"repair-branch ownership for '{current_git_branch}' while merged-main truth remains "
                    "`No Active Branch`"
                ),
            )

    backlog_entries = _parse_backlog_sections(backlog_text)
    if compact_source_truth_reform:
        _validate_docs_source_truth_reform_model(
            require,
            backlog_text=backlog_text,
            roadmap_text=roadmap_text,
            index_text=index_text,
            main_text=main_text,
            backlog_entries=backlog_entries,
        )
    else:
        _validate_consolidated_backlog_source_truth(
            require,
            backlog_text=backlog_text,
            main_text=main_text,
            development_rules_text=development_rules_text,
            phase_governance_text=phase_governance_text,
            backlog_entries=backlog_entries,
        )
        _validate_backlog_family_reform_bootstrap(
            require,
            current_branch=current_git_branch,
            backlog_text=backlog_text,
            index_text=index_text,
            backlog_entries=backlog_entries,
        )
        _validate_backlog_family_reform_seam_truth(
            require,
            current_branch=current_git_branch,
            backlog_entries=backlog_entries,
            backlog_text=backlog_text,
            roadmap_text=roadmap_text,
        )
        _validate_automation_planning_phase_truth(
            require,
            current_branch=current_git_branch,
            backlog_text=backlog_text,
            roadmap_text=roadmap_text,
        )
        _validate_automation_planning_runtime_truth(
            require,
            current_branch=current_git_branch,
            backlog_text=backlog_text,
            roadmap_text=roadmap_text,
        )
        _validate_automation_closeout_repair_phase_truth(
            require,
            current_branch=current_git_branch,
        )
        _validate_pr101_closeout_canon_repair_phase_truth(
            require,
            current_branch=current_git_branch,
        )
        _validate_pr102_closeout_canon_repair_phase_truth(
            require,
            current_branch=current_git_branch,
        )
        _validate_pr103_closeout_canon_repair_phase_truth(
            require,
            current_branch=current_git_branch,
        )
        _validate_backlog_family_dossier_shell(
            require,
            current_branch=current_git_branch,
            backlog_entries=backlog_entries,
            roadmap_text=roadmap_text,
            index_text=index_text,
            main_text=main_text,
        )
        _validate_backlog_family_historical_pass_records(
            require,
            current_branch=current_git_branch,
        )
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
    if highest_known_prebeta_tag and not compact_source_truth_reform:
        has_recorded_post_release_closure_drift = _post_release_closure_drift_is_recorded(
            backlog_text,
            roadmap_text,
            expected_release_tag=highest_known_prebeta_tag,
        )
        require(
            latest_public_prerelease == highest_known_prebeta_tag
            or has_recorded_post_release_closure_drift,
            (
                "Docs/prebeta_roadmap.md: latest public prerelease must match the latest "
                f"local or remote prebeta tag '{highest_known_prebeta_tag}', found "
                f"'{latest_public_prerelease}'. If this is release-dependent post-release "
                "closure drift, backlog and roadmap must record "
                "`Post-Release Canon Closure Drift: Recorded`, "
                f"`Published Release Pending Canon Closure: {highest_known_prebeta_tag}`, "
                "`Closure Repair Surface: Next Branch Readiness Stage 2`, "
                "`Closure Drift Scope: release-dependent fields only`, and "
                "`Implementation Entry: Blocked until closure repair validates green`."
            ),
        )
    if highest_known_prebeta_tag:
        _validate_published_release_canon_closure(require, highest_known_prebeta_tag)
        _validate_pre_publish_release_canon_closure_simulation(
            require,
            highest_known_prebeta_tag,
        )

    fb038_entry = _entry_by_id(backlog_entries, "FB-038")
    require(
        not fb038_entry,
        "Docs/feature_backlog.md: FB-038 must be a consolidated FB-027 family trace row, not a parseable backlog entry",
    )
    require(
        FB038_CANONICAL_PATH in closed_index_paths,
        "Docs/workstreams/index.md: FB-038 must remain listed under closed historical pass records",
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

    if highest_known_prebeta_tag and not compact_source_truth_reform:
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
            active_branch_record_path,
            active_branch_record_text,
        )
    elif release_readiness_health_gate:
        _run_release_readiness_health_gate(
            require,
            backlog_entries=backlog_entries,
            active_branch_record_path=active_branch_record_path,
            active_branch_record_text=active_branch_record_text,
        )
    elif standing_governance_intake_gate:
        _run_standing_governance_intake_gate(require)
    elif worktree_confinement_gate:
        _run_worktree_confinement_gate(require)

    selected_entries = _selected_next_workstream_entries(backlog_entries)
    if (
        len(selected_entries) == 1
        and not pr_readiness_gate
        and not standing_governance_intake_gate
        and not worktree_confinement_gate
    ):
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
                current_branch_names = (
                    {current_git_branch, f"origin/{current_git_branch}"}
                    if current_git_branch
                    else set()
                )
                selected_next_branch = _extract_colon_value(
                    selected["block"], "Selected Next Implementation Branch"
                )
                same_family_successor_not_branched = (
                    current_branch_names
                    and _clean_release_value(selected_next_branch).casefold()
                    in {"not created", "deferred to branch readiness"}
                    and bool(current_branch_names.intersection(matching_branches))
                )
                repair_only_handling, explicitly_handled_repair_branches = _selected_next_repair_only_branch_info(
                    [selected["block"], roadmap_section]
                )
                non_repair_matching_branches = [
                    branch_name
                    for branch_name in matching_branches
                    if branch_record_class_map.get(branch_name) != EMERGENCY_CANON_REPAIR_BRANCH_CLASS
                    and branch_name not in explicitly_handled_repair_branches
                    and not (same_family_successor_not_branched and branch_name in current_branch_names)
                ]
                if same_family_successor_not_branched and not non_repair_matching_branches:
                    matching_branches = []
                elif repair_only_handling and not non_repair_matching_branches:
                    matching_branches = []
                else:
                    if not non_repair_matching_branches and any(
                        branch_record_class_map.get(branch_name) == EMERGENCY_CANON_REPAIR_BRANCH_CLASS
                        or branch_name in explicitly_handled_repair_branches
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

    fb041_path = "Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md"
    fb041_entries = [entry for entry in backlog_entries if entry.get("id") == "FB-041"]
    require(
        not fb041_entries,
        "Docs/feature_backlog.md: FB-041 must be a consolidated FB-027 family trace row, not a parseable backlog entry",
    )
    require(
        fb041_path in closed_index_paths,
        "Docs/workstreams/index.md: FB-041 must remain listed under closed historical pass records",
    )
    require(
        fb041_path not in active_index_paths,
        "Docs/workstreams/index.md: FB-041 must not remain under Active after v1.3.1-prebeta release",
    )

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

    if not compact_source_truth_reform:
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

        active_seam_section = _section(workstream_text, "Active Seam")

        if current_phase == "Branch Readiness":
            for heading in REQUIRED_BRANCH_READINESS_DURABILITY_HEADINGS:
                require(
                    heading in workstream_text,
                    (
                        f"{canonical_path}: Branch Readiness durability scaffold is missing "
                        f"required heading '{heading}'"
                    ),
                )

            _validate_backlog_completion_strategy(
                require,
                canonical_path,
                workstream_text,
                branch_class=branch_class,
                current_phase=current_phase,
            )
            _validate_product_definition_plan(
                require,
                canonical_path,
                workstream_text,
                branch_class=branch_class,
                current_phase=current_phase,
                blockers=blockers,
                next_legal_phase=str(workstream_info["next_legal_phase"]),
            )
            _validate_runtime_engineering_contract(
                require,
                canonical_path,
                workstream_text,
                branch_class=branch_class,
                current_phase=current_phase,
            )
            _validate_branch_runtime_engineering_plan_pointer(
                require,
                canonical_path,
                workstream_text,
                branch_class=branch_class,
                current_phase=current_phase,
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
            _validate_governed_output_state(
                require,
                canonical_path,
                continuation_section=continuation_section,
                active_seam_section=active_seam_section,
                blockers=blockers,
            )
            _validate_single_seam_workstream_contract(
                require,
                canonical_path,
                workstream_text,
                branch_class=branch_class,
                current_phase=current_phase,
                blockers=blockers,
            )
            require(
                UTS_RESULTS_BLOCKER not in blockers,
                (
                    f"{canonical_path}: {UTS_RESULTS_BLOCKER} is a Live Validation / PR Readiness "
                    "final-green blocker, not a Workstream stop condition"
                ),
            )
            require(
                _parse_uts_result_state(workstream_text) == "",
                (
                    f"{canonical_path}: Workstream may keep User Test Summary strategy current, "
                    f"but must not declare '{UTS_RESULT_LABEL}' before Live Validation"
                ),
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

        if current_phase in {"Live Validation", "PR Readiness"} and _requires_user_facing_shortcut_gate(
            workstream_text
        ):
            require(
                _has_codex_live_client_self_qa(workstream_text),
                (
                    f"{canonical_path}: active desktop user-facing '{current_phase}' workstream must include "
                    "an exact '## Codex Live Client Self-QA' section before User Test Summary handoff"
                ),
            )
            self_qa_section = _codex_live_client_self_qa_section(workstream_text)
            self_qa_result = _parse_codex_live_client_self_qa_state(workstream_text)
            require(
                bool(self_qa_result),
                (
                    f"{canonical_path}: active desktop user-facing '{current_phase}' workstream must declare "
                    f"'{CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL}'"
                ),
            )
            if self_qa_result:
                require(
                    self_qa_result in CODEX_LIVE_CLIENT_SELF_QA_RESULT_VALUES,
                    (
                        f"{canonical_path}: {CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL} '{self_qa_result}' "
                        f"must be one of {', '.join(CODEX_LIVE_CLIENT_SELF_QA_RESULT_VALUES)}"
                    ),
                )
                for marker in CODEX_LIVE_CLIENT_SELF_QA_REQUIRED_MARKERS:
                    require(
                        marker in self_qa_section,
                        (
                            f"{canonical_path}: Codex Live Client Self-QA section is missing "
                            f"'{marker}'"
                        ),
                    )
                if self_qa_result == "PENDING":
                    require(
                        CODEX_LIVE_CLIENT_SELF_QA_BLOCKER in blockers,
                        (
                            f"{canonical_path}: {CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL} PENDING requires "
                            f"'{CODEX_LIVE_CLIENT_SELF_QA_BLOCKER}' under Blockers"
                        ),
                    )
                    require(
                        next_legal_phase == current_phase,
                        (
                            f"{canonical_path}: {CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL} PENDING must keep "
                            f"Next Legal Phase at '{current_phase}' until self-QA is digested"
                        ),
                    )
                if self_qa_result == "FAIL":
                    require(
                        blockers,
                        (
                            f"{canonical_path}: {CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL} FAIL must keep "
                            "an explicit blocker and route back before USER handoff or advancement"
                        ),
                    )
                if self_qa_result in CODEX_LIVE_CLIENT_SELF_QA_CLEAR_VALUES:
                    require(
                        CODEX_LIVE_CLIENT_SELF_QA_BLOCKER not in blockers,
                        (
                            f"{canonical_path}: {CODEX_LIVE_CLIENT_SELF_QA_BLOCKER} must clear after "
                            f"{CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL} {self_qa_result}"
                        ),
                    )
                if self_qa_result == "WAIVED":
                    require(
                        bool(_parse_codex_live_client_self_qa_waiver_reason(workstream_text)),
                        (
                            f"{canonical_path}: {CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL} WAIVED requires "
                            f"'{CODEX_LIVE_CLIENT_SELF_QA_WAIVER_REASON_LABEL}'"
                        ),
                    )
                uts_result_for_self_qa = _parse_uts_result_state(workstream_text)
                if uts_result_for_self_qa in UTS_CLEAR_RESULT_VALUES:
                    require(
                        self_qa_result in CODEX_LIVE_CLIENT_SELF_QA_CLEAR_VALUES,
                        (
                            f"{canonical_path}: {UTS_RESULT_LABEL} {uts_result_for_self_qa} requires "
                            f"{CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL} PASS or WAIVED first"
                        ),
                    )
                if current_phase == "PR Readiness":
                    require(
                        self_qa_result in CODEX_LIVE_CLIENT_SELF_QA_CLEAR_VALUES,
                        (
                            f"{canonical_path}: PR Readiness requires "
                            f"{CODEX_LIVE_CLIENT_SELF_QA_RESULT_LABEL} PASS or WAIVED; "
                            f"current value is {self_qa_result}"
                        ),
                    )

        if current_phase in {"Live Validation", "PR Readiness"} and _requires_codex_visual_adjudication_gate(
            workstream_text
        ):
            require(
                _has_codex_visual_adjudication(workstream_text),
                (
                    f"{canonical_path}: active desktop UI '{current_phase}' workstream must include "
                    "an exact '## Codex Visual Adjudication' section before User Test Summary handoff"
                ),
            )
            visual_adjudication_section = _codex_visual_adjudication_section(workstream_text)
            visual_adjudication_result = _parse_codex_visual_adjudication_state(workstream_text)
            require(
                bool(visual_adjudication_result),
                (
                    f"{canonical_path}: active desktop UI '{current_phase}' workstream must declare "
                    f"'{CODEX_VISUAL_ADJUDICATION_RESULT_LABEL}'"
                ),
            )
            if visual_adjudication_result:
                require(
                    visual_adjudication_result in CODEX_VISUAL_ADJUDICATION_RESULT_VALUES,
                    (
                        f"{canonical_path}: {CODEX_VISUAL_ADJUDICATION_RESULT_LABEL} "
                        f"'{visual_adjudication_result}' must be one of "
                        f"{', '.join(CODEX_VISUAL_ADJUDICATION_RESULT_VALUES)}"
                    ),
                )
                for marker in CODEX_VISUAL_ADJUDICATION_REQUIRED_MARKERS:
                    require(
                        marker in visual_adjudication_section,
                        (
                            f"{canonical_path}: Codex Visual Adjudication section is missing "
                            f"'{marker}'"
                        ),
                    )
                if visual_adjudication_result == "PENDING":
                    require(
                        CODEX_VISUAL_ADJUDICATION_BLOCKER in blockers,
                        (
                            f"{canonical_path}: {CODEX_VISUAL_ADJUDICATION_RESULT_LABEL} PENDING "
                            f"requires '{CODEX_VISUAL_ADJUDICATION_BLOCKER}' under Blockers"
                        ),
                    )
                    require(
                        next_legal_phase == current_phase,
                        (
                            f"{canonical_path}: {CODEX_VISUAL_ADJUDICATION_RESULT_LABEL} PENDING "
                            f"must keep Next Legal Phase at '{current_phase}' until visual adjudication is digested"
                        ),
                    )
                if visual_adjudication_result == "FAIL":
                    require(
                        CODEX_VISUAL_ADJUDICATION_BLOCKER in blockers,
                        (
                            f"{canonical_path}: {CODEX_VISUAL_ADJUDICATION_RESULT_LABEL} FAIL "
                            f"requires '{CODEX_VISUAL_ADJUDICATION_BLOCKER}' under Blockers"
                        ),
                    )
                if visual_adjudication_result in CODEX_VISUAL_ADJUDICATION_CLEAR_VALUES:
                    require(
                        CODEX_VISUAL_ADJUDICATION_BLOCKER not in blockers,
                        (
                            f"{canonical_path}: {CODEX_VISUAL_ADJUDICATION_BLOCKER} must clear after "
                            f"{CODEX_VISUAL_ADJUDICATION_RESULT_LABEL} {visual_adjudication_result}"
                        ),
                    )
                if visual_adjudication_result == "WAIVED":
                    require(
                        bool(_parse_codex_visual_adjudication_waiver_reason(workstream_text)),
                        (
                            f"{canonical_path}: {CODEX_VISUAL_ADJUDICATION_RESULT_LABEL} WAIVED "
                            f"requires '{CODEX_VISUAL_ADJUDICATION_WAIVER_REASON_LABEL}'"
                        ),
                    )
                uts_result_for_visual_adjudication = _parse_uts_result_state(workstream_text)
                if uts_result_for_visual_adjudication in UTS_CLEAR_RESULT_VALUES:
                    require(
                        visual_adjudication_result in CODEX_VISUAL_ADJUDICATION_CLEAR_VALUES,
                        (
                            f"{canonical_path}: {UTS_RESULT_LABEL} {uts_result_for_visual_adjudication} "
                            f"requires {CODEX_VISUAL_ADJUDICATION_RESULT_LABEL} PASS or WAIVED first"
                        ),
                    )
                if current_phase == "PR Readiness":
                    require(
                        visual_adjudication_result in CODEX_VISUAL_ADJUDICATION_CLEAR_VALUES,
                        (
                            f"{canonical_path}: PR Readiness requires "
                            f"{CODEX_VISUAL_ADJUDICATION_RESULT_LABEL} PASS or WAIVED; "
                            f"current value is {visual_adjudication_result}"
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

        if current_phase == "Release Readiness" and _is_merged_main_snapshot():
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
        _validate_slice_continuation_policy(
            require,
            canonical_path,
            workstream_text,
            branch_class=branch_class,
            current_phase=current_phase,
        )
        _validate_backlog_completion_status(
            require,
            canonical_path,
            workstream_text,
            branch_class=branch_class,
            current_phase=current_phase,
            blockers=blockers,
            next_legal_phase=next_legal_phase,
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
            _require_no_conflicting_marker_values(
                require,
                "Docs/feature_backlog.md",
                backlog_text,
                "Merged-Unreleased Release-Debt Owner",
            )
            _require_no_conflicting_marker_values(
                require,
                "Docs/prebeta_roadmap.md",
                roadmap_text,
                "Merged-Unreleased Release-Debt Owner",
            )
            _require_no_conflicting_marker_values(
                require,
                canonical_path,
                workstream_text,
                "Merged-Unreleased Release-Debt Owner",
            )
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
            backlog_posture = _section(backlog_text, "Current Branch Execution Posture")
            roadmap_posture = _section(roadmap_text, "Current Branch Execution Posture")
            for source_name, posture_text in (
                ("Docs/feature_backlog.md", backlog_posture),
                ("Docs/prebeta_roadmap.md", roadmap_posture),
            ):
                require(
                    bool(posture_text),
                    f"{source_name}: merged-unreleased release-debt owner requires a Current Branch Execution Posture section",
                )
                posture_lower = posture_text.casefold()
                for marker in MERGE_STABLE_CURRENT_STATE_OWNER_MARKERS:
                    require(
                        marker not in posture_text,
                        (
                            f"{source_name}: merge-stable current-state owner must not include "
                            f"'{marker}' during merged-unreleased release-debt windows"
                        ),
                    )
                for forbidden_phrase in MERGE_STABLE_CURRENT_STATE_OWNER_BANNED_PHRASES:
                    require(
                        forbidden_phrase.casefold() not in posture_lower,
                        (
                            f"{source_name}: merge-stable current-state owner must not include "
                            f"time-sensitive PR narration '{forbidden_phrase}' during "
                            "merged-unreleased release-debt windows"
                        ),
                    )
                for forbidden_pattern in MERGE_STABLE_BRANCH_HEAD_PIN_PATTERNS:
                    require(
                        forbidden_pattern.search(posture_text) is None,
                        (
                            f"{source_name}: merge-stable current-state owner must not pin "
                            "merge-target branch heads to commit hashes during merged-unreleased "
                            "release-debt windows"
                        ),
                    )
            phase_status_lower = phase_status_section.casefold()
            for forbidden_phrase in MERGE_STABLE_PHASE_STATUS_BANNED_PHRASES:
                require(
                    forbidden_phrase.casefold() not in phase_status_lower,
                    (
                        f"{canonical_path}: merged-unreleased `## Phase Status` must not include "
                        f"time-sensitive PR narration '{forbidden_phrase}'"
                    ),
                )
            for forbidden_pattern in MERGE_STABLE_BRANCH_HEAD_PIN_PATTERNS:
                require(
                    forbidden_pattern.search(phase_status_section) is None,
                    (
                        f"{canonical_path}: merged-unreleased `## Phase Status` must not pin "
                        "merge-target branch heads to commit hashes"
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
        current_phase = str(info["current_phase"])
        allowed_branch_record_phases = set(PHASES)
        if branch_record_path in historical_branch_record_paths:
            allowed_branch_record_phases.add(HISTORICAL_TRACEABILITY_PHASE)
        require(
            current_phase in allowed_branch_record_phases,
            f"{branch_record_path}: Current Phase '{info['current_phase']}' is not in the canonical phase enum",
        )
        require(
            str(info["branch_class"]) in BRANCH_CLASSES,
            f"{branch_record_path}: Branch Class '{info['branch_class']}' is not in the canonical branch-class enum",
        )
        branch_class = str(info["branch_class"])
        if branch_record_path in active_branch_record_paths:
            require(
                branch_class not in BLOCKED_FUTURE_ACTIVE_BRANCH_CLASSES,
                (
                    f"{branch_record_path}: active branch class '{branch_class}' is blocked for future "
                    "Nexus work; governance/docs/source-of-truth repairs must ride inside the next "
                    "legitimate runtime-focused backlog branch"
                ),
            )
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
        allowed_transition_targets = set(PHASES)
        if branch_record_path in historical_branch_record_paths:
            allowed_transition_targets.add(HISTORICAL_TRACEABILITY_PHASE)
        require(
            str(info["rollback_target"]) in allowed_transition_targets,
            f"{branch_record_path}: Rollback Target '{info['rollback_target']}' is not in the canonical phase enum",
        )
        require(
            str(info["next_legal_phase"]) in allowed_transition_targets,
            f"{branch_record_path}: Next Legal Phase '{info['next_legal_phase']}' is not in the canonical phase enum",
        )
        if branch_record_path in active_branch_record_paths:
            _validate_planning_loop_guardrail(
                require,
                branch_record_path,
                record_text,
                branch_class=branch_class,
                current_phase=current_phase,
                normalized_status=normalized_record_status,
            )
            _validate_slice_continuation_policy(
                require,
                branch_record_path,
                record_text,
                branch_class=branch_class,
                current_phase=current_phase,
            )
            _validate_backlog_completion_strategy(
                require,
                branch_record_path,
                record_text,
                branch_class=branch_class,
                current_phase=current_phase,
            )
            _validate_product_definition_plan(
                require,
                branch_record_path,
                record_text,
                branch_class=branch_class,
                current_phase=current_phase,
                blockers=list(info["blockers"]),
                next_legal_phase=str(info["next_legal_phase"]),
            )
            _validate_runtime_engineering_contract(
                require,
                branch_record_path,
                record_text,
                branch_class=branch_class,
                current_phase=current_phase,
            )
            _validate_branch_runtime_engineering_plan_pointer(
                require,
                branch_record_path,
                record_text,
                branch_class=branch_class,
                current_phase=current_phase,
            )
            _validate_fam006_stage2_r6_plan(
                require,
                branch_record_path,
                record_text,
                blockers=list(info["blockers"]),
                current_phase=current_phase,
            )
            _validate_backlog_completion_status(
                require,
                branch_record_path,
                record_text,
                branch_class=branch_class,
                current_phase=current_phase,
                blockers=list(info["blockers"]),
                next_legal_phase=str(info["next_legal_phase"]),
            )
            active_seam_section = _section(record_text, "Active Seam")

            if current_phase == "Branch Readiness":
                for heading in REQUIRED_BRANCH_READINESS_DURABILITY_HEADINGS:
                    require(
                        heading in record_text,
                        (
                            f"{branch_record_path}: Branch Readiness durability scaffold is missing "
                            f"required heading '{heading}'"
                        ),
                    )
                initial_seam_sequence = _section(record_text, "Initial Workstream Seam Sequence")
                for marker in REQUIRED_BRANCH_READINESS_FIRST_SEAM_MARKERS:
                    require(
                        marker in initial_seam_sequence,
                        (
                            f"{branch_record_path}: Initial Workstream Seam Sequence must define a first seam "
                            f"with '{marker}'"
                        ),
                    )
                require(
                    "Active seam:" in active_seam_section,
                    f"{branch_record_path}: Active Seam section must clearly identify the active seam",
                )
            if current_phase == "Workstream":
                continuation_section = _section(record_text, "Seam Continuation Decision")
                require(
                    bool(continuation_section),
                    f"{branch_record_path}: active Workstream record must include '## Seam Continuation Decision'",
                )
                for marker in REQUIRED_WORKSTREAM_CONTINUATION_MARKERS:
                    require(
                        marker in continuation_section,
                        f"{branch_record_path}: Seam Continuation Decision is missing '{marker}'",
                    )
                _validate_governed_output_state(
                    require,
                    branch_record_path,
                    continuation_section=continuation_section,
                    active_seam_section=active_seam_section,
                    blockers=list(info["blockers"]),
                )
                _validate_single_seam_workstream_contract(
                    require,
                    branch_record_path,
                    record_text,
                    branch_class=branch_class,
                    current_phase=current_phase,
                    blockers=list(info["blockers"]),
                )
                continuation_completion_status = _extract_marker_value(
                    continuation_section,
                    CONTINUATION_COMPLETION_STATUS_LABEL,
                ).strip().casefold()
                if continuation_completion_status != "green":
                    active_branch_lower = branch_name.casefold()
                    phase_exit_summary_phrases = (
                        "next legal phase: hardening",
                        "next legal runtime step: hardening",
                        "hardening handoff pending",
                        "hardening pending",
                    )
                    for summary_path, summary_text in (
                        ("Docs/feature_backlog.md", backlog_text),
                        ("Docs/prebeta_roadmap.md", roadmap_text),
                    ):
                        summary_lower = summary_text.casefold()
                        if active_branch_lower and active_branch_lower in summary_lower:
                            for summary_phrase in phase_exit_summary_phrases:
                                require(
                                    summary_phrase not in summary_lower,
                                    (
                                        f"{summary_path}: active Workstream branch '{branch_name}' "
                                        f"has Completion Status '{continuation_completion_status}' "
                                        f"but summary truth still encodes phase-exit seam via "
                                        f"'{summary_phrase}'"
                                    ),
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
            if "No Active Branch" in post_merge_state:
                _run_merge_target_authority_projection_gate(
                    require,
                    active_branch_record_paths=active_branch_record_paths,
                    active_branch_record_path=branch_record_path,
                    active_branch_record_text=record_text,
                    merge_stable_branch_record_path="",
                    merge_stable_branch_record_text="",
                )
        if branch_record_path in active_branch_record_paths:
            require(
                "`Active Branch`" in phase_status_section,
                f"{branch_record_path}: active branch record must declare `Active Branch` in Phase Status",
            )
            require(
                bool(branch_name),
                f"{branch_record_path}: active branch record must declare a Branch in Branch Identity",
            )
            for prohibited_prefix in PROHIBITED_ACTIVE_BRANCH_PREFIXES:
                require(
                    not branch_name.startswith(prohibited_prefix),
                    (
                        f"{branch_record_path}: active branch record uses prohibited branch "
                        f"prefix '{prohibited_prefix}'. Use `feature/` or another USER-approved "
                        "non-`codex/` prefix."
                    ),
                )
            require(
                (branch_name in all_branch_names) or (f"origin/{branch_name}" in all_branch_names),
                (
                    f"{branch_record_path}: active branch record points to missing branch "
                    f"'{branch_name}'"
                ),
            )
            if branch_record_path != STANDING_GOVERNANCE_INTAKE_RECORD_PATH:
                branch_is_merged, branch_merge_error = _branch_ref_is_merged_into_origin_main(branch_name)
                require(
                    not branch_merge_error,
                    (
                        f"{branch_record_path}: Merged Active Branch Authority Not Folded Down; "
                        f"could not compare branch '{branch_name}' with origin/main: {branch_merge_error}"
                    ),
                )
                require(
                    not branch_is_merged,
                    (
                        f"{branch_record_path}: Merged Active Branch Authority Not Folded Down; "
                        f"active branch authority points to branch '{branch_name}' whose ref is already "
                        "merged into origin/main. Move the record to Historical Branch Authority Records, "
                        "retire or historical-label its branch plan, update compact pointers to "
                        "merged-unreleased/released posture, and route release execution separately."
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
            for active_pr_marker in HISTORICAL_BRANCH_ACTIVE_PR_MARKERS:
                require(
                    active_pr_marker not in phase_status_section,
                    (
                        f"{branch_record_path}: historical branch record must not retain "
                        f"active PR-readiness marker '{active_pr_marker}' in Phase Status"
                    ),
                )
        if branch_record_path in {
            str(PR101_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD),
            str(PR102_CLOSEOUT_CANON_REPAIR_BRANCH_RECORD),
        } and branch_record_path in historical_branch_record_paths:
            require(
                current_phase == HISTORICAL_TRACEABILITY_PHASE,
                (
                    f"{branch_record_path}: historical post-merge closeout record must report "
                    f"`Phase: {HISTORICAL_TRACEABILITY_PHASE}`"
                ),
            )
            require(
                "Current PR Readiness Seam:" not in phase_status_section
                and "Live PR State: `open`" not in phase_status_section,
                (
                    f"{branch_record_path}: historical post-merge closeout record must not retain "
                    "active PR-readiness or open-PR narration"
                ),
            )

    if outside_lane_merge_stable_findings:
        print(
            "INFO: branch governance validation classified "
            f"{len(outside_lane_merge_stable_findings)} outside-lane merge-stable finding(s) "
            f"for current branch `{current_git_branch}`."
        )
        for finding in outside_lane_merge_stable_findings:
            print(f"- OUTSIDE-LANE: {finding}")

    if errors:
        print(f"FAIL: branch governance validation found {len(errors)} issue(s).")
        for issue in errors:
            print(f"- {issue}")
        return 1

    print(f"PASS: branch governance validation passed {checks} checks.")
    return 0


def validate_current_interfaces(root: Path) -> dict[str, object]:
    """Current source contracts only. No history census or effect permission."""
    import hashlib, stat
    errors = []
    root = Path(root).absolute()
    router_path = root / "Docs/Main.md"
    try:
        router_info=router_path.lstat()
        if not stat.S_ISREG(router_info.st_mode) or router_info.st_nlink!=1 or getattr(router_info,"st_file_attributes",0)&0x400:raise ValueError("nonordinary current router")
        router = router_path.read_text(encoding="utf-8")
        owners = ("Docs/phase_governance.md", "Docs/development_rules.md", "Docs/codex_modes.md",
            "Docs/branch_plans/README.md", "Docs/branch_records/index.md", "Docs/workstreams/index.md",
            "Docs/validation_helper_registry.md", "Docs/governance_efficiency_operating_model.md",
            "Docs/nexus_workspace_roots.md")
        if r"D:\Nexus Desktop AI\Product Repository" not in router:
            errors.append("canonical D Product Repository route missing")
        for owner in owners:
            path = root / owner
            if owner not in router:
                errors.append("missing owner route: " + owner); continue
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or getattr(info, 'st_file_attributes', 0) & 0x400:
                errors.append("nonordinary owner: " + owner)
            elif not path.read_text(encoding='utf-8').lstrip().startswith('#'):
                errors.append("owner document lacks a title: " + owner)
        def git(*args):
            return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', '-C', str(root), *args], text=True, stderr=subprocess.PIPE).strip()
        actual_root = git('rev-parse', '--show-toplevel')
        if Path(actual_root).resolve() != root.resolve():errors.append('carrier Git root mismatch')
        import ast
        changed=git('diff','--name-only','origin/main').splitlines()
        for relative in changed:
            if relative.endswith('.py') and (root/relative).is_file():ast.parse((root/relative).read_bytes(),filename=str(root/relative))
        if 'Docs/nexus_startup_contract.md' in changed:
            loader=(root/'Docs/nexus_startup_contract.md').read_text(encoding='utf-8')
            if 'Docs/Main.md' not in loader:errors.append('edited loader lacks current Main owner reference')
        facts = {'root':actual_root, 'branch':git('branch','--show-current'), 'head':git('rev-parse','HEAD'),
            'originMain':git('rev-parse','origin/main'), 'mergeBase':git('merge-base','HEAD','origin/main'),
            'dirt':git('status','--porcelain=v1').splitlines()}
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        errors.append(type(error).__name__ + ': ' + str(error)); facts = {}
    return {'result':'BLOCK' if errors else 'PASS', 'proofLevel':'SOURCE_CONTRACT',
        'executionAuthorized':False, 'operationalReadiness':'NOT_ASSESSED', 'facts':facts, 'failures':errors}


def _current_infrastructure_pr_proof(facts, assignment, qualification, source_sha256, pr=None, review=None):
    """Current infrastructure adoption facts; historical product gates are separate."""
    errors=[]
    def need(condition,message):
        if not condition:errors.append(message)
    need(assignment.get('phase')=='PR Readiness','current PR phase missing')
    need(assignment.get('canonicalMainMutation')is False,'canonical preservation missing')
    need(facts.get('mergeBase')==assignment.get('base'),'merge base differs from assignment')
    need(facts.get('originMain')==assignment.get('currentOriginMain',assignment.get('base')),'current main impact not reconciled in assignment')
    need(not facts.get('dirt'),'owned changes are not durably committed')
    need(type(qualification)is dict and qualification.get('result')=='PASS'and qualification.get('sourceSHA256')==source_sha256,'actual affected qualification does not bind this validator source')
    if errors:return {'result':'BLOCK','failures':errors}
    if pr is None:return {'result':'PENDING','failures':[],'pending':'ACTUAL_CURRENT_HEAD_PR_REQUIRED'}
    if type(pr)is not dict or pr.get('state')!='OPEN':return {'result':'BLOCK','failures':['actual PR is not open']}
    need(pr.get('fallbackLocalState')is not True,'planning metadata is not actual PR evidence')
    need(pr.get('headRefName')==facts['branch']and pr.get('headRefOid')==facts['head'],'PR branch/head differs')
    need(pr.get('baseRefName')=='main'and pr.get('isDraft')is False,'PR base/draft differs')
    need(pr.get('mergeable')!='CONFLICTING','PR conflicts')
    need(pr.get('reviewDecision')!='CHANGES_REQUESTED','requested changes remain')
    if errors:return {'result':'BLOCK','failures':errors}
    checks=pr.get('statusCheckRollup')
    if type(checks)is not list or not checks:return {'result':'PENDING','failures':[],'pending':'ACTUAL_CURRENT_HEAD_CHECKS_REQUIRED'}
    meaningful=False;pending=False
    for check in checks:
        if check.get('__typename')=='CheckRun':
            if check.get('status')!='COMPLETED':pending=True;continue
            need(check.get('conclusion')in('SUCCESS','NEUTRAL','SKIPPED'),'current-head check failed')
            meaningful=meaningful or check.get('conclusion')=='SUCCESS'
        elif check.get('__typename')=='StatusContext':
            if check.get('state')=='PENDING':pending=True;continue
            need(check.get('state')=='SUCCESS','current-head status failed');meaningful=meaningful or check.get('state')=='SUCCESS'
        else:need(False,'unknown check evidence type')
    if errors:return {'result':'BLOCK','failures':errors}
    if pending:return {'result':'PENDING','failures':[],'pending':'CURRENT_HEAD_CHECKS_RUNNING'}
    decision=pr.get('reviewDecision')
    if decision!='APPROVED':
        policy=pr.get('capturedReviewPolicy')
        if not(decision is None and type(policy)is dict and policy.get('capture')=='DIRECT_GITHUB_API'and type(policy.get('legacyRequiredReviews'))is int and policy['legacyRequiredReviews']==0 and type(policy.get('rulesRequiredReviews'))is int and policy['rulesRequiredReviews']==0):
            return {'result':'PENDING','failures':[],'pending':'ACTUAL_REQUIRED_GITHUB_REVIEW_COMPLETION'}
    if not meaningful:return {'result':'PENDING','failures':[],'pending':'NO_EXECUTED_SUCCESSFUL_CURRENT_HEAD_CHECK'}
    if not(type(review)is dict and review.get('result')=='PASS'and review.get('head')==facts['head']and type(review.get('reviewer'))is str and review['reviewer'].startswith('/root/')and review['reviewer']!='/root'):
        return {'result':'PENDING','failures':[],'pending':'ACTUAL_CURRENT_HEAD_SCOPED_INDEPENDENT_REVIEW_REQUIRED'}
    if pr.get('mergeable')!='MERGEABLE':return {'result':'PENDING','failures':[],'pending':'ACTUAL_MERGEABILITY_REQUIRED'}
    return {'result':'PASS','failures':[],'executionAuthorized':False,'releaseDisposition':'NOT_APPLICABLE_INFRASTRUCTURE_ADOPTION'}

def main() -> int:
    import argparse, hashlib
    parser = argparse.ArgumentParser(description='Affected current source contracts; operational gates require explicitly selected current authority.')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--legacy-diagnostic', action='store_true', help='Historical broad diagnostic only; never current admission.')
    for flag in ('pr-readiness-gate','release-readiness-health-gate','standing-governance-intake-gate','worktree-confinement-gate'):
        modes.add_argument('--'+flag, action='store_true')
    parser.add_argument('--current-assignment', type=Path)
    parser.add_argument('--authorization-sha256')
    parser.add_argument('--assignment-sha256')
    parser.add_argument('--approval-file',type=Path)
    parser.add_argument('--current-authority', type=Path)
    parser.add_argument('--current-authority-sha256')
    parser.add_argument('--current-validation',type=Path)
    parser.add_argument('--current-validation-sha256')
    parser.add_argument('--current-review',type=Path)
    parser.add_argument('--current-review-sha256')
    parser.add_argument('--current-pr-number',type=int)
    args = parser.parse_args()
    if args.legacy_diagnostic:
        print('HISTORICAL DIAGNOSTIC; not a current source/admission gate')
        sys.argv=[sys.argv[0]]
        return _legacy_diagnostic_main()
    proof = validate_current_interfaces(ROOT_DIR)
    gate = next((name for name in ('pr_readiness_gate','release_readiness_health_gate','standing_governance_intake_gate','worktree_confinement_gate') if getattr(args,name)), None)
    if any((args.current_assignment,args.assignment_sha256,args.approval_file,args.authorization_sha256,args.current_authority,args.current_authority_sha256)) and not gate:
        proof['failures'].append('assignment operands are for an explicit operational gate; bare mode is source-only');proof['result']='BLOCK'
    if gate:
        failures=proof['failures']
        try:
            if not args.current_assignment or not args.current_authority or not args.current_authority_sha256 or not args.authorization_sha256 or not args.assignment_sha256 or not args.approval_file:
                raise ValueError('explicit current assignment, actual approval digest and current authority binding required; historical fallback is retired')
            def unique_current(pairs):
                value={}
                for key,item in pairs:
                    if key in value:raise ValueError('duplicate current binding key')
                    value[key]=item
                return value
            def capture_current_binding(path, limit=1024*1024):
                import os, stat
                path=Path(path)
                if not path.is_absolute():raise ValueError('current binding must use an absolute path')
                for ancestor in path.parents:
                    info=ancestor.lstat()
                    if not stat.S_ISDIR(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:raise ValueError('current binding ancestry is not ordinary')
                info=path.lstat()
                if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or getattr(info,'st_file_attributes',0)&0x400 or not 0<info.st_size<=limit:raise ValueError('current binding is not a bounded ordinary file')
                identity=lambda value:(value.st_dev,value.st_ino,value.st_size,value.st_mtime_ns)
                with path.open('rb') as handle:
                    if identity(os.fstat(handle.fileno()))!=identity(info):raise ValueError('current binding replaced before read')
                    raw=handle.read(info.st_size+1)
                if len(raw)!=info.st_size or identity(path.lstat())!=identity(info):raise ValueError('current binding changed during read')
                return raw
            assignment_raw=capture_current_binding(args.current_assignment)
            if hashlib.sha256(assignment_raw).hexdigest().upper()!=args.assignment_sha256:raise ValueError('assignment provenance bytes differ')
            assignment=json.loads(assignment_raw,object_pairs_hook=unique_current)
            if hashlib.sha256(capture_current_binding(args.approval_file)).hexdigest().upper()!=args.authorization_sha256:raise ValueError('actual approval bytes differ')
            approval_sha=assignment.get('authorizationSHA256') or assignment.get('assignment',{}).get('authorizationSHA256')
            if approval_sha!=args.authorization_sha256 or not re.fullmatch('[0-9A-F]{64}',args.authorization_sha256):raise ValueError('actual approval binding mismatch')
            row=assignment.get('assignment',assignment)
            selected_owner=row.get('selectedOwner')
            if (type(selected_owner)is not dict or set(selected_owner)!={'path','sha256'}
                    or selected_owner['path']!=str(args.current_authority)
                    or selected_owner['sha256']!=args.current_authority_sha256):
                raise ValueError('current operational owner is not selected by the authenticated assignment; a self-hashed document is insufficient')
            if type(row.get('root'))is not str or not row['root'] or not Path(row['root']).is_absolute() or Path(row['root']).resolve()!=ROOT_DIR.resolve() or row.get('head')!=proof['facts']['head'] or row.get('branch')!=proof['facts']['branch']:
                raise ValueError('current assignment/carrier identity mismatch')
            authority_raw=capture_current_binding(args.current_authority)
            if hashlib.sha256(authority_raw).hexdigest().upper()!=args.current_authority_sha256:raise ValueError('current authority byte binding mismatch')
            # Hash the complete original bytes; interpret ordinary Windows line
            # endings consistently with the existing document reader.
            authority=authority_raw.decode('utf-8-sig').replace('\r\n','\n')
            phase_info=_parse_workstream_doc(authority)
            phase=str(phase_info['current_phase'])
            if row.get('phase')!=phase:raise ValueError('current assignment and selected owner phases differ')
            wanted={'pr_readiness_gate':{'PR Readiness'},'release_readiness_health_gate':{'PR Readiness'},'worktree_confinement_gate':set(PHASES),'standing_governance_intake_gate':set()}[gate]
            if phase not in wanted:raise ValueError('selected current phase is not applicable; standing intake is a retired generic route')
            def field(*names):
                return next((_extract_marker_value(authority,name).strip('`') for name in names if _extract_marker_value(authority,name)), '')
            if field('Current HEAD','HEAD')!=proof['facts']['head'] or field('Branch')!=row['branch'] or field('Worktree','Worktree Root','Assigned Worktree')!=str(ROOT_DIR):raise ValueError('selected current operational owner is stale or not exactly bound to carrier')
            if _is_historical_worktree_receipt(authority):raise ValueError('historical receipt is not current phase authority')
            def require(condition,message):
                if not condition:failures.append(message)
            selected=(str(args.current_authority),authority)
            if gate=='worktree_confinement_gate':
                require(type(row.get('owner'))is str and bool(row['owner'].strip()),'current assigned owner missing')
                require(type(row.get('scope'))is str and bool(row['scope'].strip()),'current assigned write scope missing')
                require(row.get('canonicalMainMutation')is False,'canonical main preservation must be explicit')
                require(proof['facts']['mergeBase']==row.get('base'),'current assignment merge base differs')
                # Existing dirt is evidence; its reviewed preservation is selected by the owner.
                require(field('Dirty Worktree Ownership','Preserved Dirt Disposition')in ('SOLE_WRITER_PRESERVED','Clean'),'current dirt ownership/preservation missing')
            elif gate=='release_readiness_health_gate':_run_release_readiness_health_gate(require,selected_owner=selected)
            elif gate=='pr_readiness_gate':
                if field('Route Class')=='SOURCE_TRUTH_GOVERNANCE_INFRASTRUCTURE':
                    if proof['result']!='PASS':raise ValueError('current source contracts failed before infrastructure readiness')
                    if not args.current_validation or not args.current_validation_sha256:raise ValueError('actual affected source qualification required')
                    captured=capture_current_binding(args.current_validation)
                    if hashlib.sha256(captured).hexdigest().upper()!=args.current_validation_sha256:raise ValueError('outside qualification binding differs')
                    qualification=json.loads(captured,object_pairs_hook=unique_current);review=None;pr=None
                    if args.current_review:
                        captured=capture_current_binding(args.current_review)
                        if hashlib.sha256(captured).hexdigest().upper()!=args.current_review_sha256:raise ValueError('outside review binding differs')
                        review=json.loads(captured,object_pairs_hook=unique_current)
                    if args.current_pr_number:
                        captured=subprocess.check_output(['gh','pr','view',str(args.current_pr_number),'--repo','GiribaldiTTV/Nexus-Desktop-AI','--json','state,headRefName,headRefOid,baseRefName,isDraft,mergeable,reviewDecision,statusCheckRollup'],text=True,timeout=30)
                        pr=json.loads(captured,object_pairs_hook=unique_current)
                        if pr.get('reviewDecision')is None:
                            protection=json.loads(subprocess.check_output(['gh','api','repos/GiribaldiTTV/Nexus-Desktop-AI/branches/main/protection'],text=True,timeout=30),object_pairs_hook=unique_current)
                            rules=json.loads(subprocess.check_output(['gh','api','repos/GiribaldiTTV/Nexus-Desktop-AI/rules/branches/main'],text=True,timeout=30),object_pairs_hook=unique_current)
                            pr['capturedReviewPolicy']={'capture':'DIRECT_GITHUB_API','legacyRequiredReviews':protection.get('required_pull_request_reviews',{}).get('required_approving_review_count'),'rulesRequiredReviews':max([rule['parameters']['required_approving_review_count']for rule in rules if rule.get('type')=='pull_request']or[0])}
                    current=_current_infrastructure_pr_proof(proof['facts'],row,qualification,hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper(),pr,review)
                    proof.update(current,requestedGate=gate,operationalReadiness=current['result'],currentPR=pr)
                    print(json.dumps(proof,indent=2));return 0 if current['result']=='PASS'else 1
                backlog=_parse_backlog_sections(_read_text(Path('Docs/feature_backlog.md')))
                roadmap=_read_text(Path('Docs/prebeta_roadmap.md'))
                _run_pr_readiness_gate(require,backlog,roadmap,set(),{},selected[0],selected[1],selected_owner=selected)
            proof['operationalReadiness']='BLOCKED' if failures else 'PASS_SELECTED_READ_ONLY_GATE'
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
            failures.append(str(error))
        proof.update(result='BLOCK' if failures else 'PASS', requestedGate=gate)
        if failures:proof['operationalReadiness']='BLOCKED'
    print(json.dumps(proof, indent=2))
    return 0 if proof['result']=='PASS' else 1


if __name__ == "__main__":
    raise SystemExit(main())
