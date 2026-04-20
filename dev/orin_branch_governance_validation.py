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

MULTI_SEAM_CONTRACT_DOCS = (
    Path("Docs/phase_governance.md"),
    Path("Docs/development_rules.md"),
    Path("Docs/codex_modes.md"),
    Path("Docs/Main.md"),
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

MULTI_SEAM_CONTRACT_PHRASE = "bounded multi-seam workflow"

MULTI_SEAM_PROMPT_DOCS = (
    Path("Docs/orin_task_template.md"),
    Path("Docs/codex_user_guide.md"),
)

MULTI_SEAM_PROMPT_PHRASES = (
    "Seam Sequence",
    "continue-or-stop",
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
)

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


def _extract_colon_value(block: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", block, flags=re.M)
    return match.group(1).strip() if match else ""


def _parse_workstream_doc(text: str) -> dict[str, object]:
    record_state = _extract_first_backtick_value(_section(text, "Record State"))
    status = _extract_first_backtick_value(_section(text, "Status"))
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
        "current_phase": current_phase,
        "branch_class": branch_class,
        "blockers": blockers,
        "rollback_target": rollback_target,
        "next_legal_phase": next_legal_phase,
        "governance_audit": governance_audit,
    }


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
    section = _subsection(text, heading_prefix)
    return set(re.findall(r"Docs/branch_records/[A-Za-z0-9._-]+\.md", section))


def _roadmap_section_for_id(text: str, workstream_id: str) -> str:
    match = re.search(rf"(?ms)^### {re.escape(workstream_id)}.*?(?=^### |\Z)", text)
    return match.group(0).strip() if match else ""


def _phase_index(phase_name: str) -> int:
    return PHASES.index(phase_name)


def _git_status_porcelain() -> str:
    completed = subprocess.run(
        ("git", "status", "--porcelain"),
        cwd=ROOT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return f"__GIT_STATUS_ERROR__ {completed.stderr.strip()}"
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


def _selected_next_workstream_entries(backlog_entries: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        entry
        for entry in backlog_entries
        if re.search(rf"^{re.escape(NEXT_WORKSTREAM_SELECTION_MARKER)}\s*$", entry["block"], flags=re.M)
    ]


def _next_workstream_roadmap_section(roadmap_text: str) -> str:
    return _section(roadmap_text, "Selected Next Workstream")


def _branch_names_for_workstream(branch_names: list[str], workstream_id: str) -> list[str]:
    canonical = workstream_id.casefold()
    compact = canonical.replace("-", "")
    return [
        branch_name
        for branch_name in branch_names
        if canonical in branch_name.casefold() or compact in branch_name.casefold().replace("-", "")
    ]


def _run_next_workstream_gate(require, backlog_entries: list[dict[str, str]], roadmap_text: str) -> None:
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
    matching_branches = _branch_names_for_workstream(branch_names, selected_id)
    require(
        not matching_branches,
        (
            "PR readiness gate: Successor Lock Missing blocker is active; "
            f"{selected_id} already has branch(es): {', '.join(matching_branches)}"
        ),
    )


def _run_pr_readiness_gate(require, backlog_entries: list[dict[str, str]], roadmap_text: str) -> None:
    status_output = _git_status_porcelain()
    require(
        not status_output,
        (
            "PR readiness gate: Dirty Branch blocker is active; worktree must be clean "
            "and required branch truth must be durable in commit history before PR READY: YES"
        ),
    )
    _run_next_workstream_gate(require, backlog_entries, roadmap_text)


def main() -> int:
    pr_readiness_gate = "--pr-readiness-gate" in sys.argv[1:]
    errors: list[str] = []
    checks = 0

    backlog_text = _read_text(Path("Docs/feature_backlog.md"))
    roadmap_text = _read_text(Path("Docs/prebeta_roadmap.md"))
    index_text = _read_text(Path("Docs/workstreams/index.md"))

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
            f"{relative_path}: docs/governance branch-admission guidance is missing",
        )

    for relative_path in MULTI_SEAM_CONTRACT_DOCS:
        text = _read_text(relative_path)
        require(
            MULTI_SEAM_CONTRACT_PHRASE in text,
            f"{relative_path}: canonical bounded multi-seam workflow contract is missing",
        )

    for relative_path in MULTI_SEAM_PROMPT_DOCS:
        text = _read_text(relative_path)
        for required_phrase in MULTI_SEAM_PROMPT_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: multi-seam prompt scaffold is missing '{required_phrase}'",
            )

    for relative_path, guard_phrase in zip(WORKSTREAM_TO_PR_DEFAULT_GUARD_DOCS, WORKSTREAM_TO_PR_DEFAULT_GUARD_PHRASES):
        text = _read_text(relative_path)
        require(
            guard_phrase in text,
            f"{relative_path}: direct Workstream-to-PR default guard is missing",
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

    for relative_path in PR_READINESS_BLOCKER_DOCS:
        text = _read_text(relative_path).casefold()
        for required_phrase in PR_READINESS_BLOCKER_PHRASES:
            require(
                required_phrase in text,
                f"{relative_path}: PR Readiness blocker guidance is missing '{required_phrase}'",
            )

    active_index_paths = _collect_active_index_paths(index_text)
    closed_index_paths = _collect_closed_index_paths(index_text)
    release_debt_index_paths = _collect_release_debt_index_paths(index_text)

    backlog_entries = _parse_backlog_sections(backlog_text)
    if pr_readiness_gate:
        _run_pr_readiness_gate(require, backlog_entries, roadmap_text)

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

        phase_status_section = _section(workstream_text, "Phase Status")
        if (
            _normalize_status(str(workstream_info["status"])) == "merged unreleased"
            and "`No Active Branch`" in phase_status_section
            and "Release Debt" in blockers
        ):
            require(
                current_phase == "Release Readiness",
                (
                    f"{canonical_path}: merged-unreleased `No Active Branch` release-debt owner "
                    "must use `Release Readiness` as Current Phase"
                ),
            )
            require(
                "Merged Canon Drift" not in blockers and "Current-State Claim Drift" not in blockers,
                (
                    f"{canonical_path}: merged-unreleased `No Active Branch` release-debt owner "
                    "must not keep resolved current-state drift blockers active"
                ),
            )

        normalized_workstream_status = _normalize_status(str(workstream_info["status"]))
        if normalized_workstream_status == "merged unreleased":
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

    branch_record_index_text = _read_text(BRANCH_RECORD_INDEX)
    require(
        "Docs/branch_records/" in branch_record_index_text,
        "Docs/branch_records/index.md: expected branch-record paths in the index",
    )

    active_branch_record_paths = _collect_branch_record_paths(branch_record_index_text, "Active Branch Authority Records")
    historical_branch_record_paths = _collect_branch_record_paths(branch_record_index_text, "Historical Branch Authority Records")

    for branch_record_path in active_branch_record_paths | historical_branch_record_paths:
        record_path = ROOT_DIR / Path(branch_record_path)
        require(
            record_path.is_file(),
            f"{branch_record_path}: branch authority record listed in Docs/branch_records/index.md does not exist",
        )
        if not record_path.is_file():
            continue

        record_text = _read_text(Path(branch_record_path))
        phase_status_section = _section(record_text, "Phase Status")
        for heading in REQUIRED_BRANCH_RECORD_HEADINGS:
            require(
                heading in record_text,
                f"{branch_record_path}: required heading '{heading}' is missing",
            )

        info = _parse_workstream_doc(record_text)
        require(
            str(info["current_phase"]) in PHASES,
            f"{branch_record_path}: Current Phase '{info['current_phase']}' is not in the canonical phase enum",
        )
        require(
            str(info["branch_class"]) in BRANCH_CLASSES,
            f"{branch_record_path}: Branch Class '{info['branch_class']}' is not in the canonical branch-class enum",
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
            require(
                "`Active Branch`" in phase_status_section,
                f"{branch_record_path}: active branch record must declare `Active Branch` in Phase Status",
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
