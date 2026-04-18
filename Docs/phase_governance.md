# Nexus Phase Governance

## Purpose

This document defines the governed execution phases used for Nexus Desktop AI work.

It exists so:

- workstream truth
- validation truth
- closeout truth
- prompt routing

all use the same phase names and the same control rules.

This is the canonical cross-workstream governance layer.
It does not replace:

- `Docs/Main.md` as the routing index
- canonical workstream docs as branch-local feature-state, evidence, and closure records
- release or rebaseline docs as milestone summaries

## Required Prompt Anchors

For phase-sensitive work, prompts should explicitly include:

- `Current approved phase: <phase name>`

When the branch is in closeout recovery, prompts should also include:

- `Current active seam: <seam name>`

## Cross-Phase Rules

- repo canon is the detailed authority
- prompt and instruction layers should mirror the same phase names in compressed form
- workstream docs must record the current phase when promoted work is active
- a branch must not be treated as PR-ready or release-ready while its active workstream still sits in `Validation / Hardening`
- if the validation contract, timeout contract, harness behavior, or active seam changes materially during closeout recovery, canon must be updated before continued execution is recommended

## Canonical Governance Rules

### Source-Of-Truth Enforcement

- `Docs/phase_governance.md` is the repo-wide authority for phase names, proof governance, timeout governance, seam governance, and stop-loss rules
- workstream docs must consume this model rather than redefining repo-wide process rules locally
- workstream docs may record branch-local validation contracts, tighter time budgets, active seams, and evidence references, but those narrower contracts must be explicit

### Blocker Rule

Phase-sensitive work is blocked until the following are explicit and mutually consistent:

- current approved phase
- active workstream or equivalent authority record
- validation contract when validation is in scope
- timeout contract when interactive validation is in scope
- current active seam when the branch is in governed closeout recovery

If the live harness behavior and documented timeout contract drift, execution is blocked until they are reconciled.

### Merge-Target Canon Completeness Gate

Rule:

- a branch is not `PR Readiness`-complete if merging it would leave `main` canon-stale

This gate is mandatory when a branch would:

- close a workstream
- become the latest released implementation milestone
- change the current rebaseline or closeout baseline
- change the current closeout-index pointer
- change backlog, roadmap, or workstream-index release posture
- change `Docs/Main.md` routing for the current baseline

When this gate applies, the branch must already contain the required release-facing canon updates before PR creation is allowed:

- canonical workstream record closure or equivalent release-state update
- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/workstreams/index.md`
- `Docs/closeout_index.md`
- the new or updated closeout or rebaseline file
- `Docs/Main.md` routing updates when the current baseline pointer changed

If any required merge-target canon update is missing, the branch remains blocked in `Docs / Canon Sync` or `PR Readiness`.

### Successor Lane Lock Gate

Rule:

- a branch is not `PR Readiness`-complete unless the next workstream is selected, canon-valid, and a fresh successor branch is created

This gate requires all of the following before PR creation is allowed:

- the next workstream identity is selected from current canon
- that workstream has canon-valid `Record State`
- a fresh successor branch is created using an approved naming family such as:
  - `feature/<lane>`
  - `fix/<issue>`
  - `docs/<lane>`
- the successor branch is explicitly treated as reserved
- execution on the successor branch must not begin until the current branch merges and the successor branch is revalidated against updated `main`

If the next workstream is not selected, its record state is not canon-valid, or the successor branch has not been created, the current branch is not PR-ready.

### Proof Authority Matrix

When multiple evidence layers exist, use this authority order unless a workstream explicitly documents a tighter requirement:

1. runtime markers
2. persisted source truth
3. UIAutomation and readback
4. optional UI observations such as help text, examples boxes, and transient labels

UI-only observations may be logged as notes, but they must not override stronger runtime and persisted-source proof unless the UI interaction itself is the thing being validated.

### Proof Ownership Rule

- repo-wide phase governance defines the allowed proof model
- the active workstream doc defines the branch-local validation contract, active seam, and any explicit tighter requirements
- runtime markers and persisted source truth own correctness for product behavior unless the scenario is explicitly about UI interaction quality or reachability

### Validation Helper Contract

Interactive validation helpers should default to a reusable repo-wide contract unless a workstream explicitly documents a tighter branch-local need.

That contract is:

- runtime markers and runtime logs are the primary proof surface
- persisted source or persisted state snapshots are the secondary proof surface
- UIAutomation, readback, and other live UI inspection are tertiary proof surfaces
- gating observations and non-gating observations must be separated explicitly
- runtime helpers are expected when they materially improve deterministic startup, attach, or runtime-log capture
- a watchdog or equivalent timeout-enforcement path is required for meaningful interactive closeout work
- last-confirmed-progress logging is required for timeout or stall diagnosis
- cleanup guarantees are required for helper processes, launched apps, probe files, and other session artifacts
- saved-state or source snapshots should be preserved when write safety, reopen behavior, or no-write blocking behavior matters
- windows, dialogs, overlays, and controls should be re-resolved live across close/open seams instead of reusing stale references
- validation seams must be classified as `product defect`, `harness defect`, `environment issue`, or `canon / contract drift` before product code is changed

Closeout-grade proof has one extra rule:

- the default budget profile of the validation helper must itself prove green before branch closeout can be claimed

Exploratory command-line overrides may still be used during hardening, but a one-off override profile is not enough to call the branch green unless that same profile becomes the documented default or the documented default also proves green.

### Seam Classification Rule

Validation seams should be classified before they are fixed:

- `product defect`
- `harness defect`
- `environment issue`
- `canon / contract drift`

Do not treat a seam as a product defect merely because the interactive harness failed first.

### Single-Seam Iteration Rule

- only one active seam may be fixed at a time during governed closeout recovery
- rerun the full governed gate immediately after that seam fix
- if a new seam appears, log it before selecting it as the next active seam

Single-seam ownership does not require a new operator prompt after every rerun.
It means one seam is active at a time, even when a longer continuous validation pass is allowed.

### Continuous Validation Loop Rule

When the approved prompt or execution boundary explicitly authorizes a continuous validation pass inside `Validation / Hardening`, Codex may continue across seam iterations without waiting for a new user prompt after every rerun.

That is allowed only while all of the following remain true:

- the branch is still in `Validation / Hardening`
- the same workstream boundary and closeout goal remain valid
- the proof hierarchy, timeout contract, and helper default profile remain unchanged
- no blocker, truth drift, or required canon-sync stop appears
- the pass is still moving through one active seam at a time

Inside that continuous loop, Codex should:

- identify the first real failing seam
- classify it before changing product code
- fix only that seam
- rerun the full governed gate immediately
- continue until the full gate is green or a hard stop is reached

This rule exists so governed validation can keep moving toward full green without unnecessary stop-and-report churn between every seam.

### Stop-Loss Rule

For governed closeout recovery or another approved continuous validation pass:

- stop immediately if a blocker appears
- stop immediately if truth drift appears
- stop immediately if timeout inflation beyond the documented contract is required
- stop immediately if proof ownership, gating rules, or the helper default profile must change before the next rerun
- stop if `2` consecutive seam fixes fail to move the first-failing seam or otherwise fail to produce material end-to-end progress
- stop if roughly `90 minutes` of validation work pass without material end-to-end progress toward green
- when stop-loss is reached, continued execution is blocked until a decision memo or equivalent phase-state update is recorded

### Timeout Governance

Interactive closeout and hardening work must use tiered hard stops.

Repo-wide target contract for hardened desktop interactive helpers:

- preflight startup gate: `<= 60s`
- seam or control-acquisition gate: `<= 3s` once the live desktop surface is already open
- no-progress watchdog: `<= 3s`
- normal scenario budget: `<= 60s`
- exceptional scenario budget: `<= 90s`, only when explicitly declared in the workstream doc
- full interactive rerun hard cap: `<= 15 minutes`
- outer execution timeout: only slightly above the harness hard cap

Prohibited without explicit workstream-doc reconciliation:

- undocumented `90s+` scenario budgets
- undocumented `15m+` full-run caps
- silent timeout inflation during closeout

Additional repo-wide rule:

- when hardening proves that a tighter and faster default helper profile is stable, that profile should replace the older relaxed default before closeout-grade proof is claimed
- if a seam keeps breaching the documented `3s` or `60s` targets, treat that as validation-helper or process debt and redesign the proof path instead of silently letting the run sit longer

### Truth-Drift Enforcement Rule

- if validation or harness behavior changes materially, canon must be updated before continued execution is recommended
- if a workstream changes which evidence layer is authoritative for success, that change must be written into the active workstream doc before the next seam-fix iteration
- if a workstream doc, harness defaults, and live execution evidence disagree, the workflow remains in `Validation / Hardening` until the drift is reconciled

### Preflight Requirement

Before a full interactive gate is used as a closeout proof surface, run or confirm a preflight that proves:

- startup or probe acquisition works
- runtime log creation works
- the overlay or root runtime surface opens
- the cleanup path works
- no stale helper processes, probe windows, or leftover session artifacts are still active from an earlier failed run

If preflight fails, the branch remains in `Validation / Hardening`; do not burn a full closeout run first.

### Desktop UI Audit Rule

When a branch materially changes user-facing desktop UI and that UI is relevant to the closeout claim:

- a live launched-process UI audit is required before branch closeout is treated as complete
- the audit should happen after the branch is green or effectively green, not during every seam iteration
- the audit evidence should include a manifest or equivalent index plus the captured screenshots or other durable artifacts
- the audit should check layout, readability, visibility, hierarchy, and obvious regressions against the current desktop UI direction

This does not create a repo-wide rule that every validation pass must always take screenshots.
The canonical rule is narrower:

- marker-first proof for behavior
- live launched-process UI audit when meaningful desktop UI changed and closeout depends on user-facing UI quality

### Iteration Discipline

- full interactive reruns are for proof, not exploration
- do not keep fixing seams informally without updating the seam ledger
- after a green rerun, move to `Docs / Canon Sync` before calling PR readiness
- after a non-green rerun inside a continuous validation pass, either select the next single active seam inside stop-loss or stop at the hard-stop boundary
- do not stop a continuous validation pass merely because one seam finished; stop only at green, truth drift, a blocker, or stop-loss

### Phase Transition Rule

- `Workstream Analysis` -> `Approved Execution` only after the execution boundary is explicit
- `Approved Execution` -> `Validation / Hardening` when branch truth must be proven or hardened
- `Validation / Hardening` -> `Docs / Canon Sync` only after branch-local proof is sufficient for closeout
- `Docs / Canon Sync` -> `PR Readiness` only after the docs reflect the proven branch truth, the merge-target canon completeness gate passes, the successor lane lock gate passes, and no active seam remains
- `PR Readiness` -> `Release Readiness` only when the branch is a legitimate merge or release candidate
- `Release Readiness` -> `Post-Release Canon Sync` only as an emergency repair path after merged or released truth already exists and canon drift escaped the earlier gates

## Phase Definitions

### Workstream Analysis

Purpose:

- determine current truth
- identify drift
- choose the correct next move

Allowed:

- broad repo analysis
- source-of-truth audits
- branch and release validation
- non-mutating exploration

Forbidden:

- implementation
- silent scope narrowing before analysis completes

Required evidence:

- current branch truth
- relevant authority docs
- live repo or log evidence where truth could have changed

Exit:

- one recommended next move or approved execution boundary

### Approved Execution

Purpose:

- carry an approved change through implementation and verification

Allowed:

- bounded code or docs changes
- validation inside the approved scope

Forbidden:

- silent scope expansion
- free-form lane redesign

Required evidence:

- approved execution boundary
- direct verification of the changed behavior or docs

Exit:

- implementation slice is complete
- branch either remains in execution, moves to validation/hardening, or returns to analysis

### Validation / Hardening

Purpose:

- prove the current branch truth
- harden validation infrastructure when proof gaps remain
- when explicitly approved, continue a bounded seam-by-seam validation loop until the full gate is green or a hard stop is reached

Allowed:

- validators
- harness work
- runtime helper work
- small supporting evidence infrastructure

Forbidden:

- unrelated feature work
- treating green repo-side validation as automatic closeout

Required evidence:

- validator results
- live/runtime results when relevant
- interactive results when feasible
- explicit distinction between product defects, harness defects, and environment issues

Exit:

- branch-local proof is sufficient for closeout
- or the pass stops with a bounded active seam and findings

### Docs / Canon Sync

Purpose:

- align source-of-truth docs to the proven current branch truth

Allowed:

- workstream evidence refresh
- manual validation artifact refresh
- canon alignment inside the approved scope

Forbidden:

- speculative governance or roadmap churn
- advancing closeout truth without proof

Required evidence:

- passing proof artifacts or explicitly bounded limitation notes

Exit:

- docs reflect current proven truth

### PR Readiness

Purpose:

- determine whether the branch is ready to become a merge candidate without leaving merged canon stale and with the next lane already locked

Allowed:

- readiness review
- PR material preparation
- final drift checks
- next-workstream confirmation
- successor-branch creation

Forbidden:

- assuming readiness because the worktree is clean
- skipping active validation blockers
- allowing a branch to enter PR creation while merge-target canon updates are still missing
- allowing a branch to enter PR creation while the next workstream identity or successor branch is still unresolved

Required evidence:

- branch-local proof complete
- closeout truth current
- merge-target canon completeness gate passed
- next workstream identity selected from canon
- next workstream record state is canon-valid
- successor branch created and marked reserved until post-merge revalidation
- no active seam

Exit:

- ready for PR creation
- or returned to validation/hardening with explicit blockers

### Release Readiness

Purpose:

- determine whether merged truth is ready for release packaging

Allowed:

- release review
- release notes prep
- version/tag recommendations

Forbidden:

- treating branch-local success as released truth

Required evidence:

- merged or merge-ready truth
- release-context verification

Exit:

- ready for release packaging
- or returned to analysis/docs sync for unresolved release debt

### Post-Release Canon Sync

Purpose:

- perform emergency canon repair after a release only when merged truth is already live and canon drift escaped the earlier gates

Allowed:

- docs and canon repair tightly coupled to the released truth

Forbidden:

- treating post-release canon sync as a normal part of the standard merge lifecycle
- using post-release canon sync instead of the merge-target canon completeness gate
- turning post-release sync into a new implementation lane by accident

Required evidence:

- updated `main`
- latest release truth
- explicit canon drift
- explicit reason the drift could not be prevented before merge or release

Exit:

- canon aligned to released truth
