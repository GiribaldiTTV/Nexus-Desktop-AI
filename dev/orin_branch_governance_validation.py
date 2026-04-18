import re
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


def _roadmap_section_for_id(text: str, workstream_id: str) -> str:
    match = re.search(rf"(?ms)^### {re.escape(workstream_id)}.*?(?=^### |\Z)", text)
    return match.group(0).strip() if match else ""


def _phase_index(phase_name: str) -> int:
    return PHASES.index(phase_name)


def main() -> int:
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

    promoted_entries = [
        entry
        for entry in _parse_backlog_sections(backlog_text)
        if entry.get("record_state") == "Promoted"
    ]
    require(bool(promoted_entries), "Docs/feature_backlog.md: expected at least one promoted workstream")

    active_index_paths = _collect_active_index_paths(index_text)
    closed_index_paths = _collect_closed_index_paths(index_text)

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

    if errors:
        print(f"FAIL: branch governance validation found {len(errors)} issue(s).")
        for issue in errors:
            print(f"- {issue}")
        return 1

    print(f"PASS: branch governance validation passed {checks} checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
