# Nexus Startup Contract

## Purpose

This document is the compact startup and loader contract for Nexus Desktop AI chats.

Use it to start a new Codex or ChatGPT session without pasting the full governance stack into the prompt. It does not replace the owning canon documents. It tells the assistant what to load, how to validate live repo truth, what must stop execution, and what output shape is required before narrowing scope.

Seam workflow logic is intentionally out of scope for this contract. When seam behavior matters, route to `Docs/phase_governance.md`, `Docs/codex_modes.md`, and the active workstream record.

## Owning Canon

This contract routes to these authorities:

- `Docs/Main.md` owns source-of-truth routing and protected-main law.
- `Docs/development_rules.md` owns implementation, validation, cleanup, and durability expectations.
- `Docs/phase_governance.md` owns phase names, blockers, branch classes, phase transitions, proof governance, and seam-governance rules.
- `Docs/codex_modes.md` owns Analysis and Workflow collaboration posture.
- `Docs/feature_backlog.md` owns tracked work identity and `Record State`.
- `Docs/workstreams/index.md` owns canonical workstream-record routing.
- the active workstream doc owns branch-local phase truth, evidence, blockers, and next legal phase for promoted work.
- `Docs/incident_patterns.md` owns generalized recurring drift or validation lessons.
- `Docs/validation_helper_registry.md` owns durable helper naming, status, reuse, and consolidation obligations when helpers are in scope.

If this contract and an owning canon document conflict, live repo truth plus the owning canon document wins. Repair this contract later if it drifted.

## Startup Contract

Before planning, patching, reviewing, generating a prompt, recommending a phase, or acting on a task:

1. Read `Docs/nexus_startup_contract.md`.
2. Read `Docs/Main.md`.
3. Read `Docs/development_rules.md`.
4. Read `Docs/phase_governance.md`.
5. Read `Docs/codex_modes.md`.
6. Load the directly relevant authority docs for the task.
7. If the task maps to a tracked item, load `Docs/feature_backlog.md` and determine its `Record State`.
8. If the tracked item is `Promoted` or `Closed`, load its canonical workstream doc from the backlog and `Docs/workstreams/index.md`.
9. If helpers, validation scripts, live-validation harnesses, or shared support are in scope, load `Docs/validation_helper_registry.md`.
10. If drift, recurrence, release correction, or governance repair is in scope, load `Docs/incident_patterns.md`.
11. Validate current repo truth before acting:
    - current branch
    - branch cleanliness and tracked-file mutations
    - whether the branch is the legal execution base
    - current phase from the authority record
    - phase status
    - branch class
    - blockers
    - next legal phase
12. State the startup assessment before narrowing scope:
    - `Source-of-Truth`
    - `Record State`
    - `Branch Truth`
    - `Canonical Workstream`
    - `Reuse Baseline`
    - `Next Safe Move`

If any required file cannot be read, any authority owner is ambiguous, or live repo truth contradicts the requested phase or branch, stop and report the conflict.

## Authority Model

- Backlog defines identity and `Record State`; it does not own full execution history.
- Roadmap defines sequencing and release posture; it does not override workstream phase truth.
- Workstream docs own promoted-work feature-state, branch-local evidence, phase truth, blockers, active seam references, artifact history, and closure history.
- Phase governance owns phase definitions, blockers, proof hierarchy, branch classes, and phase transitions.
- Development rules own validation depth, cleanup, runtime evidence, helper reuse, and pre-PR durability behavior.
- Codex modes define Analysis versus Workflow posture.
- Incident patterns are reusable lessons, not case-history authority.
- `main` is protected for Codex work and may be read but not mutated.

Do not create parallel governance systems. Add narrow routing pointers here, and put detailed policy in the owning canon document.

## Phase Rules

Use only the canonical normal phases from `Docs/phase_governance.md`:

- `Branch Readiness`
- `Workstream`
- `Hardening`
- `Live Validation`
- `PR Readiness`
- `Release Readiness`

`No Active Branch` is repo state, not a normal phase. `Post-Release Canon Repair` is not a normal phase or standalone branch lane.

Phase-sensitive prompts and outputs must identify:

- `Mode`
- `Phase`
- `Workstream`
- `Branch`
- `Branch Class` when branch-sensitive
- `Active Seam` when seam-sensitive
- `Validation Contract` when validation-sensitive

Do not infer a later phase from user intent. If the requested phase conflicts with the authority record, stop and report `Prompt Phase Mismatch` or the closest canon blocker.

## Validation Contract

Default startup validation:

- `git status --short --branch`
- current branch check
- authority-record phase check
- `python dev\orin_branch_governance_validation.py` when repo governance truth is in scope
- `git diff --check` after edits

Additional validation is phase- and workstream-specific and must be read from the active workstream doc and `Docs/phase_governance.md`.

For docs/governance-only passes, validation must include:

- governance alignment check against owning canon
- duplication check so the new doc routes rather than re-owning detailed policy
- conflict check against phase governance, protected-main law, and durability rules

## Stop Conditions

Stop immediately if:

- `Docs/nexus_startup_contract.md` or a required owning canon document cannot be read.
- current branch truth is unclear.
- the requested branch is not the checked-out branch and switching/creating it is not authorized by canon.
- the requested phase does not match the authority record.
- the workstream `Record State` is missing or contradictory.
- `main` would need file mutation.
- `Release Readiness` would need file mutation.
- repo truth is `No Active Branch` with unresolved blockers.
- validation fails.
- implementing the task would require runtime/product work outside the approved phase.
- seam workflow policy would need to be defined or redesigned during a pass that explicitly excludes seam workflow logic.

## Output Expectations

Every startup-sensitive pass should return or restate:

- `Source-of-Truth`
- `Record State`
- `Branch Truth`
- `Canonical Workstream`
- `Reuse Baseline`
- `Active Seam` when applicable
- `Validation Results`
- `Ready-To-Commit Decision` when files changed
- `Next Legal Phase`
- `Next Safe Move`

When a pass creates or changes files before `PR Readiness` and validation is green, follow the Pre-PR Durability Rule in `Docs/development_rules.md` and `Docs/phase_governance.md` unless a documented durability exception applies.

## Standard Loader Prompt Pattern

Use this pattern to start a new chat without exceeding prompt limits:

```text
You are continuing the Nexus Desktop AI project.

Mode: <Analysis / Workflow>
Phase: <canonical phase or analysis-only>
Workstream: <FB-XXX or No Active Branch>
Branch: <branch name>
Branch Class: <implementation / docs/governance historical context / release packaging / as canon allows>

First, read and follow:
- Docs/nexus_startup_contract.md

Then execute the startup contract from that file:
- load the owning canon documents it requires
- validate current repo truth
- validate current branch, phase, record state, canonical workstream, blockers, and next legal phase
- stop if the contract cannot be read or if repo truth contradicts this prompt

Task:
<bounded task>

Constraints:
- Do not assume prior chat context is true.
- Do not execute from intent alone.
- Do not skip startup validation.
- Do not implement runtime/product work unless this prompt and canon both authorize it.

Return:
- Source-of-Truth
- Record State
- Branch Truth
- Canonical Workstream
- Reuse Baseline
- Active Seam, if applicable
- Files Changed
- What Was Written or Found
- Validation Results
- Ready-To-Commit Decision
- Next Legal Phase
- Next Safe Move
```

## ChatGPT Prompt Generator Rule

Paste this block into ChatGPT custom instructions when ChatGPT is helping generate Nexus prompts:

```text
When the user asks for a Nexus Desktop AI new-chat prompt, bootstrap prompt, analysis prompt, Branch Readiness prompt, Workstream prompt, PR Readiness prompt, Release Readiness prompt, or similar continuation prompt, generate a full loader prompt.

The prompt must instruct the new chat to read `Docs/nexus_startup_contract.md` first, execute that startup contract, load the required owning canon, validate repo/branch/phase/record-state truth before acting, and stop if any required contract file cannot be read or repo truth contradicts the requested task.

Do not generate minimal prompts that omit governance loading. Do not rely on prior chat memory as truth. Do not let the prompt assume phase, branch, release, PR, or workstream state without requiring repo validation. Do not redesign seam workflow logic unless the user explicitly asks for the later dedicated seam-governance pass.

Every generated prompt must include: Mode, Phase, Workstream, Branch, Branch Class when relevant, task scope, constraints, stop conditions, validation requirements, and an output format containing Source-of-Truth, Record State, Branch Truth, Canonical Workstream, Reuse Baseline, Validation Results, Next Legal Phase, and Next Safe Move.
```

## Standard Prompt Templates

### Analysis

```text
You are continuing the Nexus Desktop AI project.

Mode: Analysis
Phase: analysis-only
Workstream: <FB-XXX / No Active Branch / unknown until validated>
Branch: <current claimed branch>

Read first:
- Docs/nexus_startup_contract.md

Execute the startup contract completely before analysis. Validate current repo truth, branch truth, phase truth, record state, canonical workstream ownership, blockers, and next legal phase. Do not patch files, create branches, create commits, create PRs, tag releases, or execute product/runtime work.

Task:
<analysis task>

Stop if repo truth is unclear, required docs cannot be read, or the requested state conflicts with canon.

Return:
- Source-of-Truth
- Record State
- Branch Truth
- Canonical Workstream
- Reuse Baseline
- Drift Found
- Validation Results
- Next Legal Phase
- Next Safe Move
```

### Branch Readiness

```text
You are continuing the Nexus Desktop AI project.

Mode: Workflow
Phase: Branch Readiness
Workstream: <FB-XXX>
Branch: <branch name>
Branch Class: implementation

Read first:
- Docs/nexus_startup_contract.md

Execute the startup contract completely. Validate that the branch is the legal Branch Readiness surface, the workstream Record State is correct, the canonical workstream doc exists, current blockers are explicit, and implementation has not started unless canon already admitted Workstream.

Task:
<Branch Readiness task>

Constraints:
- No runtime/product implementation.
- No PR, merge, tag, release, or next-branch work.
- Repair only canon/governance truth directly required for Branch Readiness.

Stop if branch truth, phase truth, or admission legality is unclear.

Return:
- Source-of-Truth
- Record State
- Branch Truth
- Canonical Workstream
- Reuse Baseline
- Active Seam, if applicable
- Files Changed
- What Was Written
- Validation Results
- Ready-To-Commit Decision
- Next Legal Phase
- Next Safe Move
```

### Workstream

```text
You are continuing the Nexus Desktop AI project.

Mode: Workflow
Phase: Workstream
Workstream: <FB-XXX>
Branch: <branch name>
Branch Class: implementation

Read first:
- Docs/nexus_startup_contract.md

Execute the startup contract completely. Validate that Workstream is the current phase in the authority record, that branch truth is correct, that blockers are clear, and that the workstream scope and validation contract are explicit.

Task:
<bounded Workstream task>

Constraints:
- Stay inside the approved Workstream scope.
- Do not enter Hardening, Live Validation, PR Readiness, Release Readiness, release execution, or next-branch work.
- Do not redesign seam workflow logic; use existing canon if seam behavior is relevant.

Stop if scope, phase, branch truth, or validation requirements are unclear.

Return:
- Source-of-Truth
- Record State
- Branch Truth
- Canonical Workstream
- Reuse Baseline
- Active Seam, if applicable
- Files Changed
- What Was Written
- Validation Results
- Ready-To-Commit Decision
- Next Legal Phase
- Next Safe Move
```

### PR Readiness

```text
You are continuing the Nexus Desktop AI project.

Mode: Workflow
Phase: PR Readiness
Workstream: <FB-XXX>
Branch: <branch name>
Branch Class: implementation

Read first:
- Docs/nexus_startup_contract.md

Execute the startup contract completely. Validate branch truth, authority-record phase truth, clean durable branch state, merge-target canon, next-workstream selection, helper retention, PR creation requirements, and PR validation requirements from owning canon.

Task:
<PR Readiness task>

Constraints:
- No runtime/product implementation.
- Do not merge.
- Do not execute release work.
- Do not create the next branch.
- Do not report PR Readiness GREEN until PR creation and PR validation requirements are satisfied by canon and live PR truth.

Stop if PR state, branch truth, post-merge canon, next-workstream truth, or required validation is unknown.

Return:
- Source-of-Truth
- Record State
- Branch Truth
- Canonical Workstream
- Reuse Baseline
- Files Changed
- Governance Drift Found
- Validation Results
- Ready-To-Commit Decision
- Whether PR Readiness is GREEN
- PR Creation Details, if package-ready
- Next Legal Phase
- Next Safe Move
```

### Release Readiness

```text
You are continuing the Nexus Desktop AI project.

Mode: Workflow
Phase: Release Readiness
Workstream: <FB-XXX>
Branch: main or release-review branch as canon permits
Branch Class: <release packaging / implementation release-review context / No Active Branch release review, as canon permits>

Read first:
- Docs/nexus_startup_contract.md

Execute the startup contract completely. Validate merged repo truth, release-debt owner truth, release target, release floor, version rationale, release scope, release artifacts, and post-release truth from canon.

Task:
<Release Readiness task>

Constraints:
- Release Readiness is analysis-only and file-frozen.
- Do not edit, stage, commit, generate, or refresh repository files.
- Do not create tags or GitHub releases.
- Do not create branches.
- If any file change is needed, classify the drift and route it to PR Readiness before merge or the next active Branch Readiness after merge.

Stop if release target, scope, artifacts, post-release truth, or file-frozen state is unclear.

Return:
- Source-of-Truth
- Record State
- Branch Truth
- Canonical Workstream
- Reuse Baseline
- Release Target
- Release Scope
- Release Artifacts
- Post-Release Truth
- Validation Results
- Whether Release Readiness is GREEN
- Remaining Blockers
- Next Legal Phase
- Next Safe Move
```
