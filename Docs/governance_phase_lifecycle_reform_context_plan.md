# Governance Phase Lifecycle Reform And USER Hub Context Plan

> Historical reform context and accepted evidence. This file grants no current execution authority. Current applicability follows `Docs/Main.md`, `Docs/phase_governance.md` and the selected installed external owner. Preserve dated facts as history.

Plan Label: Governance Phase Lifecycle Reform and USER Hub Context Plan

Status: Active governance context plan for the standing Governance intake branch.

Canonical owner model:

- `Docs/Main.md` remains the source-truth router and sync index.
- `Docs/phase_governance.md` owns phase lifecycle law.
- `Docs/codex_modes.md` mirrors compact execution behavior.
- `Docs/development_rules.md` owns development and execution behavior.
- `Docs/branch_plans/README.md` owns Branch Planning artifact rules.
- `Docs/validation_helper_registry.md` owns helper and validator enforcement.
- `Docs/branch_records/index.md` owns branch authority and routing law.
- This file is a context and consolidation plan, not a live branch-status owner.

## Lifecycle Model

The governed lifecycle is:

1. Branch Readiness
2. Branch Planning
3. Workstream
4. Hardening
5. Live Validation
6. PR Readiness
7. Release Readiness

Branch Readiness:

- BR1 - Candidate / Carrier Readiness Analysis
- BR2 - Branch Setup / Authority Admission

Branch Planning:

- BP1 - USER Branch Vision Review
- BP2 - USER Branch Plan Review
- BP3 - Workstream Entry / Orchestration Validation

Workstream is runtime/code implementation and code-level validation only. Planning belongs to Branch Planning. Pressure testing and accepted-plan comparison belong to Hardening. User-facing proof and UTS handling belong to Live Validation.

## Vision Stack

The vision stack is:

Project Vision -> Family Vision -> Feature Vision -> Branch Vision -> Branch Plan -> Workstream implementation

`Docs/nexus_vision.md` is the preferred project-wide vision owner when present. Branch Planning packets must route Project Vision Context above Family Vision Context before branch-level decisions.

## BP1 Role

BP1 is the USER-facing Branch Vision stage and uses `USER_BRANCH_VISION_REVIEW.md`.

BP1 defines the branch goal, end-state, product shape, user-facing behavior, surfaces, options, Codex recommendations, USER design decisions, acceptance state, and branch-vision contract before engineering planning begins.

BP1 becomes green only when USER accepts the Branch Vision or explicitly waives the BP1 gate.

## BP2 Role

BP2 is the USER-facing engineering Branch Plan stage and uses `USER_BRANCH_PLAN_REVIEW.md`.

BP2 is derived from accepted or waived BP1. It records implementation package summary, branch scope size, SLC/seam plan, affected surfaces, likely files, validators/helpers, proof requirements, Element-to-Phase proof matrix, H1 expectations, LV/UTS expectations, rollback/safety plan, engineering risks, future-gated boundaries, plan acceptance checklist, and exact BP3 approval text.

BP2 becomes green only when USER accepts the Branch Plan or explicitly waives the BP2 gate. BP2 must route back to BP1 if the engineering plan changes the accepted Branch Vision.

## BP3 Role

BP3 is Workstream Entry / Orchestration Validation.

BP3 loads accepted or waived BP1 and BP2 outputs and proves that the Branch Plan correctly implements the accepted Branch Vision, that the branch package is the largest safe feature-focused package, that SLCs are an engineering route inside one branch, and that affected files, validators, helper updates, Hardening, Live Validation, UTS, rollback, proof paths, and future-gated boundaries are ready.

BP3 may return bounded Workstream implementation approval for the admitted same-branch package, naming the entry seam or initial seam sequence, only when BP1 and BP2 are accepted or explicitly waived and BP3 validation is green.

## Branch-Size Law

A branch should be the largest coherent feature-focused implementation package that can be implemented, validated, hardened, live-validated, reviewed, and rolled back safely without mixing unrelated product areas.

Small single-control branches are discouraged when the control naturally belongs to a larger accepted feature branch. Broad unrelated branches are discouraged when they mix distinct families, provider/model work, export/share work, theme work, or unrelated product surfaces.

SLCs divide work inside a branch. SLCs do not automatically become separate branches. Every SLC must trace to a BP1 accepted branch vision requirement and a BP2 branch plan line item.

## USER Review Folder Model

The active local USER hub is:

`C:\Nexus USER`

Readable packets use:

`C:\Nexus USER\<label>\`

Upload artifacts use:

`C:\Nexus USER\<label>-YYYYMMDD-HHMMSS.zip`

Examples:

- `C:\Nexus USER\Governance\`
- `C:\Nexus USER\Governance-YYYYMMDD-HHMMSS.zip`
- `C:\Nexus USER\FAM-006\`
- `C:\Nexus USER\FAM-006-YYYYMMDD-HHMMSS.zip`

USER workflow:

1. Open `C:\Nexus USER`.
2. Read the label folder.
3. Upload the matching timestamped ZIP beside it.

The folder and timestamped ZIP are one matched pair. Before regenerating a matched pair, Codex clears the old readable folder, removes any legacy same-name upload ZIP and previous same-label timestamped upload ZIPs, creates a fresh `YYYYMMDD-HHMMSS` timestamped ZIP, and proves the folder/ZIP contents match. Cloud-backed Desktop or OneDrive locations are backup or convenience mirrors only.

## Technical Metadata Placement

USER-facing review files are temporary review aids. They should focus on context, vision, plan, options, risks, proof expectations, and USER decisions.

Active branch status, current HEAD, current origin/main, ahead/behind, upstream, worktree cleanliness, current validation state, current PR state, ZIP hash, and similar mutable technical proof belong in Codex chat digest, helper output, validator output, or external operational state.

USER-facing review files should not carry ZIP SHA256, ZIP hash, packet hash, upload hash, active branch status, current commit, current baseline, merge base, validation status, PR state, worktree status, or similar byte-proof metadata as active packet content. Those values remain available through Codex chat digest, helper output, validator output, or external governance state.

Repo-tracked files may contain durable source truth, accepted plans, accepted contracts, historical receipts, and fixed snapshots when clearly historical. Repo-tracked files should not carry mutable active branch operational state.

## External Operational State Split

Active branch plans, mutable branch state, phase-progress tracking, current live validation state, and active PR/watch state belong in the External Operational State Store, helper output, or Codex chat digest until accepted durable outcomes are folded into the proper repo owner.

Repo files should not become the live branch-status system. Accepted USER decisions and implementation constraints fold into durable repo owners or approved external-state owners after the relevant phase requires it.

## Artifact Model Decisions

Current active law:

- Use the flat local USER hub: `C:\Nexus USER\<label>\` and `C:\Nexus USER\<label>-YYYYMMDD-HHMMSS.zip`.
- Cloud-backed Desktop / OneDrive copies are optional backup or convenience mirrors only.
- USER-facing review files are temporary USER / ChatGPT review aids, not canon or posterity archives.

Pending USER decisions:

- sidecar artifact model
- separate Review / Upload top-level folder taxonomy
- cloud-backed Desktop / OneDrive as active upload source
- external-state migration beyond the approved repair

## Source-Truth Consolidation Targets

- Fold lifecycle law into `Docs/phase_governance.md`.
- Fold BP1/BP2/BP3 artifact rules into `Docs/branch_plans/README.md`.
- Fold helper enforcement into `Docs/validation_helper_registry.md`.
- Fold branch routing law into `Docs/branch_records/index.md`.
- Keep `Docs/Main.md` as a router/index, not a live ledger.
- Replace duplicate or conflicting active law with references to the proper owner where safe.

## Remaining Pending USER Decisions

- PR Readiness Stage 1
- PR creation
- merge to main
- release execution
- runtime implementation
- FAM-006 mutation
- FAM-007 mutation
- issue mutation
- branch cleanup or deletion beyond this approved governance repair
- private repo actions
- provider/model/runtime/cache/memory/private actions
- AI Product Contract import
- Private Dev ORIN import

## Current Next Legal Route

After this bounded Governance repair is green, validated, committed, and pushed, the next legal route for the Governance branch is PR Readiness Stage 1 analysis for `feature/release-readiness-source-truth-intake`.
