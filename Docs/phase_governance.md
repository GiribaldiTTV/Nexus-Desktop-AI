# Nexus Phase Governance

## Purpose

This document defines the governed execution phases used for Nexus Desktop AI work.

It exists so:

- workstream truth
- validation truth
- closeout truth
- prompt routing
- next-phase recommendations

all use the same phase names, blocker rules, and transition rules.

This is the canonical cross-workstream governance layer.
It does not replace:

- `Docs/Main.md` as the routing index
- canonical workstream docs as branch-local feature-state, evidence, and closure records
- release or rebaseline docs as milestone summaries

## Exact Prompt Contract

For phase-sensitive execution, prompts must include:

- `Mode: <mode name>`
- `Phase: <exact canonical phase name>`
- `Workstream: <workstream id or equivalent authority record>`
- `Branch: <branch name or No Active Branch>`

Add these fields when relevant:

- `Branch Class: <implementation / docs/governance / emergency canon repair / release packaging>`
- `Active Seam: <seam name>`
- `Validation Contract: <summary or authority reference>`
- `Timeout Contract: <summary or authority reference>`

If `Phase` is missing or is not one of the exact canonical phase names below, execution is blocked and only truth-validation or analysis may continue.

## Canonical Phase Enum

The only normal branch phases are:

- `Branch Readiness`
- `Workstream`
- `Hardening`
- `Live Validation`
- `PR Readiness`
- `Release Readiness`

These are not normal phases:

- `No Active Branch`
- `Post-Release Canon Repair`

`No Active Branch` is a repo-level state, not a normal phase.
It may be:

- a blocked state when an admission gate or another required repair path is still open
- a steady-state resting posture when no implementation lane is currently selected and no branch should open by inertia

`Post-Release Canon Repair` is an emergency-only exception path after merged or released truth already exists.

## Cross-Phase Rules

- repo canon is the detailed authority
- prompt and instruction layers should mirror the same exact phase names rather than aliases
- active promoted workstream docs are the single authoritative phase owners for their lane
- backlog, roadmap, and prompts may reference phase state but must not override the workstream doc
- a phase must never be inferred from user intent alone
- if the validation contract, timeout contract, harness behavior, active seam, or blocker set changes materially during late-phase work, canon must be updated before continued execution is recommended
- auxiliary guidance docs should be timeless by default and must not quietly become current-state owners

## Canonical Governance Rules

### Source-Of-Truth Enforcement

- `Docs/phase_governance.md` is the repo-wide authority for exact phase names, blocker rules, proof governance, timeout governance, seam governance, stop-loss rules, branch classes, the Governance Drift Audit, and the phase resolver contract
- workstream docs must consume this model rather than redefining repo-wide process rules locally
- workstream docs may record branch-local validation contracts, tighter time budgets, active seams, artifact references, and explicit waivers, but those narrower contracts must be explicit

### Single Phase Authority Rule

For active promoted work, the canonical workstream doc must own:

- `Current Phase`
- `Phase Status`
- `Branch Class`
- `Blockers`
- `Entry Basis`
- `Exit Criteria`
- `Rollback Target`
- `Next Legal Phase`

If any of those are missing for active promoted work, the branch is blocked by `Workstream Phase Authority Missing`.

### Branch Authority Record Rule

When an approved branch does not map to a promoted backlog workstream, it must use a repo-owned branch authority record under `Docs/branch_records/`.

That branch authority record becomes the single authoritative owner of:

- `Current Phase`
- `Phase Status`
- `Branch Class`
- `Blockers`
- `Entry Basis`
- `Exit Criteria`
- `Rollback Target`
- `Next Legal Phase`

This path is for explicitly approved non-backlog branch classes such as:

- `docs/governance`
- `emergency canon repair`
- `release packaging`

It must not be used to avoid carrying supporting canon sync on an already-active implementation branch.

### Repo-Level Admission Gate

Before any next implementation branch may enter `Branch Readiness`, all of the following must be true on updated `main`:

- `main` is aligned with `origin/main`
- merged canon is internally consistent
- no emergency canon repair is outstanding
- no unresolved governance-drift blocker exists
- no unresolved release-debt blocker exists
- no current branch is being treated as executable if it is stale, merged, or identical to `main`

If any of those fail:

- repo state becomes `No Active Branch`
- next implementation branch execution is blocked
- the next safe move is blocker repair, not a later phase

This gate controls next-lane implementation admission.
It does not, by itself, authorize or prohibit a narrower non-implementation branch class.
Those branch classes must still satisfy their own admission rules below.

### Blocker Catalog

The default named blockers are:

- `Prompt Phase Missing`
- `Prompt Phase Mismatch`
- `Workstream Phase Authority Missing`
- `Branch Base Invalid`
- `Merged Canon Drift`
- `Phase Exit Unmet`
- `Successor Lock Missing`
- `Release Debt`
- `Governance Drift`
- `Current-State Claim Drift`
- `Phase Waiver Missing`

Blockers stop progression immediately and must be reported before any later-phase recommendation.

### Blocker Rule

Phase-sensitive work is blocked until the following are explicit and mutually consistent:

- exact current phase
- active workstream or equivalent authority record
- branch class when branch-sensitive execution is in scope
- validation contract when validation is in scope
- timeout contract when interactive validation is in scope
- current active seam when the branch is in governed recovery
- current blocker set

If live behavior and the documented timeout contract drift, execution is blocked until they are reconciled.

### Branch Class And Phase Waiver Rule

Every active branch must declare a `Branch Class`:

- `implementation`
- `docs/governance`
- `emergency canon repair`
- `release packaging`

The same six normal phases apply to all branch classes.
Phases may be waived only when:

- the waiver is explicit in the active workstream or branch authority record
- the reason is recorded
- the waiver does not weaken merge-target canon completeness, successor lock, or release-debt protections

Silent phase skipping is prohibited.

### Branch-Class Admission Rule

Branch admission is class-sensitive.

`implementation`

- the full repo-level admission gate must pass before the branch may enter `Branch Readiness`
- the active promoted workstream doc is the default authority record

`docs/governance`

- may begin from updated `main` while repo sequencing truth is `No Active Branch` only when:
  - no active implementation branch exists
  - the branch purpose is genuine governance, docs, roadmap, backlog, triage, policy, or prompt-scaffolding maintenance
  - the work is not routine canon completion that belongs on an already-active implementation or release branch
  - the branch is not being used to hide merged canon drift, release debt, or required implementation follow-through
  - the reason it cannot or should not ride on an active implementation branch is explicit in the branch authority record
- during `pre-Beta`, active-branch-first remains the default and standalone `docs/governance` branches are non-default
- in later Beta, public, or project steady-state operation, this branch class may legitimately begin from `No Active Branch` when the same admission rules still hold
- if `Release Debt` remains open, the branch must leave that blocker explicit and must not claim the debt is cleared unless that is the approved scope

`release packaging`

- may begin from updated `main` when merged-unreleased implementation, release notes, tagging, or another release-facing packaging task is explicitly opened
- the branch must not widen into implementation work

`emergency canon repair`

- may begin only when merged or released truth is already stale and the drift escaped the earlier gates
- the branch must stay tightly limited to repairing that escaped canon drift

### Merge-Target Canon Completeness Gate

Rule:

- a branch is not `PR Readiness`-complete if merging it would leave `main` canon-stale

This gate is mandatory when a branch would:

- close a workstream
- become the latest released or merged-unreleased implementation milestone
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
- the new or updated closeout or rebaseline file when current baseline routing changed
- `Docs/Main.md` routing updates when the current baseline pointer changed

If any required merge-target canon update is missing, the branch remains blocked in `PR Readiness`.

### Successor Lane Lock Gate

Rule:

- a branch is not `PR Readiness`-complete unless the next workstream is selected, canon-valid, and a fresh successor branch is created

Exception:

- If post-merge truth will resolve to `No Active Branch` because `Release Debt` or another repo-level admission blocker remains open, successor-lane selection and reserved successor-branch creation are waived for that PR-readiness pass.

This gate requires all of the following before PR creation is allowed:

- the next workstream identity is selected from current canon
- that workstream has canon-valid `Record State`
- a fresh successor branch is created using an approved naming family such as:
  - `feature/<lane>`
  - `fix/<issue>`
  - `docs/<lane>`
- the successor branch is explicitly treated as reserved
- execution on the successor branch must not begin until the current branch merges and the successor branch is revalidated against updated `main`

When the exception applies, the branch must instead:

- make the post-merge `No Active Branch` state explicit in current-state canon
- name the blocking admission item explicitly
- avoid selecting or branching the next implementation lane by inertia

If the next workstream is not selected, its record state is not canon-valid, or the successor branch has not been created, the branch is blocked by `Successor Lock Missing`.

### Governance Drift Audit

Inside `PR Readiness`, the branch must run a formal Governance Drift Audit before it may advance to `Release Readiness`.

The audit must explicitly answer:

- `Governance Drift Found: Yes/No`
- `Drift Type`
- `Why Current Canon Failed To Prevent It`
- `Required Canon Changes`
- `Whether The Drift Blocks Merge`
- `Whether User Confirmation Is Required`

The audit must explicitly check whether the branch exposed:

- a missing blocker
- a weak phase entry or exit rule
- a weak source-of-truth ownership rule
- stale prompt scaffolding or stale operator examples
- a missing validator requirement

If governance drift is found and unresolved, the branch is blocked by `Governance Drift`.

### Governance Drift Escalation Rule

If governance drift is discovered in any earlier phase:

- stop normal progression immediately
- classify it as `Governance Drift`
- either fix it inside the approved governance or docs boundary, or
- produce the exact required canon delta and wait for user confirmation

Do not defer known governance weaknesses silently to a later branch.

### Manual Evidence And Review Digestion Rule

Returned evidence such as:

- `UTS`
- screenshots
- interactive reports
- PR review comments
- release review findings

may satisfy exit criteria, but must never auto-advance phase by implication.

Required sequence:

1. digest the evidence
2. update the authority record
3. reevaluate blockers
4. only then advance phase

### Current-State Claim Containment

Time-sensitive current-state claims must live only in designated current-state owners, or be part of the merge-target canon update set.

Allowed current-state owners:

- backlog
- roadmap
- active workstream doc
- workstreams index
- closeout index
- current rebaseline or closeout file
- `Docs/Main.md` routing

Auxiliary guidance docs should be timeless by default.
If they contain live-current claims, they must either:

- be updated as part of canon sync, or
- stop owning current-state truth

### Governance Validator

Repo-wide governance changes should be checked with the machine-readable governance validator:

- `python dev/orin_branch_governance_validation.py`

That validator should verify at minimum:

- the exact phase enum only
- active prompt scaffolds no longer teach deprecated phase names or stale prompt contracts
- active promoted workstreams carry the required phase-state block
- phase values and branch-class values are valid
- backlog, roadmap, workstreams index, and active workstream docs agree on active or merged-unreleased posture
- stale merge-era wording does not remain in active current-state owners
- Governance Drift Audit output exists before `Release Readiness`
- unresolved blockers prevent phase advancement

A governance or current-state canon branch is not complete until that validator is green.

When branch authority records are active, the validator should also verify:

- `Docs/branch_records/index.md` exists and routes to the active branch authority records
- active branch authority records carry the required phase-state block
- `No Active Branch` blocked-versus-steady-state handling stays consistent across the governance and operator docs
- standalone `docs/governance` branches remain explicit, gated, and non-default during `pre-Beta`

### Phase Resolver Contract

Before any answer about current phase or next move, run this resolver:

1. validate live repo truth
2. determine whether there is an active executable branch, a blocked `No Active Branch`, or a steady-state `No Active Branch`
3. identify the active workstream authority record or branch authority record
4. detect blockers first
5. read the exact `Current Phase`
6. validate entry basis and exit criteria against live truth
7. return only the next legal phase, or no phase if blocked

Required output for any “what phase are we in?” or “what’s next?” answer:

- `Current Phase`
- `Phase Status`
- `Branch Class`
- `Blockers`
- `Governance Drift Found`
- `Next Legal Phase`
- `Plan To Reach That Phase`

If a blocker exists, do not recommend a later phase or next-lane execution.
If repo truth is a steady-state `No Active Branch`, do not invent an implementation branch by inertia; either report that no branch should open yet or name the explicitly approved non-implementation branch class that may legally begin.

## Proof Authority Matrix

When multiple evidence layers exist, use this authority order unless a workstream explicitly documents a tighter requirement:

1. runtime markers
2. persisted source truth
3. UIAutomation and readback
4. optional UI observations such as help text, examples boxes, and transient labels

UI-only observations may be logged as notes, but they must not override stronger runtime and persisted-source proof unless the UI interaction itself is the thing being validated.

## Proof Ownership Rule

- repo-wide phase governance defines the allowed proof model
- the active workstream doc defines the branch-local validation contract, active seam, and any explicit tighter requirements
- runtime markers and persisted source truth own correctness for product behavior unless the scenario is explicitly about UI interaction quality or reachability

## Validation Helper Contract

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

## Seam Classification Rule

Validation seams should be classified before they are fixed:

- `product defect`
- `harness defect`
- `environment issue`
- `canon / contract drift`

Do not treat a seam as a product defect merely because the interactive harness failed first.

## Single-Seam Iteration Rule

- only one active seam may be fixed at a time during governed recovery
- rerun the full governed gate immediately after that seam fix
- if a new seam appears, log it before selecting it as the next active seam

Single-seam ownership does not require a new operator prompt after every rerun.
It means one seam is active at a time, even when a longer continuous validation pass is allowed.

## Continuous Validation Loop Rule

When the approved prompt or execution boundary explicitly authorizes a continuous validation pass inside `Hardening`, Codex may continue across seam iterations without waiting for a new user prompt after every rerun.

That is allowed only while all of the following remain true:

- the branch is still in `Hardening`
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

## Stop-Loss Rule

For governed recovery or another approved continuous validation pass:

- stop immediately if a blocker appears
- stop immediately if truth drift appears
- stop immediately if timeout inflation beyond the documented contract is required
- stop immediately if proof ownership, gating rules, or the helper default profile must change before the next rerun
- stop if `2` consecutive seam fixes fail to move the first-failing seam or otherwise fail to produce material end-to-end progress
- stop if roughly `90 minutes` of validation work pass without material end-to-end progress toward green
- when stop-loss is reached, continued execution is blocked until a decision memo or equivalent phase-state update is recorded

## Timeout Governance

Interactive hardening and live-validation work must use tiered hard stops.

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

## Truth-Drift Enforcement Rule

- if validation or harness behavior changes materially, canon must be updated before continued execution is recommended
- if a workstream changes which evidence layer is authoritative for success, that change must be written into the active workstream doc before the next seam-fix iteration
- if a workstream doc, harness defaults, and live execution evidence disagree, the workflow remains in `Hardening` or `Live Validation` until the drift is reconciled

## Preflight Requirement

Before a full interactive gate is used as a closeout proof surface, run or confirm a preflight that proves:

- startup or probe acquisition works
- runtime log creation works
- the overlay or root runtime surface opens
- the cleanup path works
- no stale helper processes, probe windows, or leftover session artifacts are still active from an earlier failed run

If preflight fails, the branch remains in `Hardening`.
Do not burn a full closeout run first.

## Desktop UI Audit Rule

When a branch materially changes user-facing desktop UI and that UI is relevant to the closeout claim:

- a live launched-process UI audit is required before branch closeout is treated as complete
- the audit should happen after the branch is green or effectively green, not during every seam iteration
- the audit evidence should include a manifest or equivalent index plus the captured screenshots or other durable artifacts
- the audit should check layout, readability, visibility, hierarchy, and obvious regressions against the current desktop UI direction

This does not create a repo-wide rule that every validation pass must always take screenshots.
The canonical rule is narrower:

- marker-first proof for behavior
- live launched-process UI audit when meaningful desktop UI changed and closeout depends on user-facing UI quality

## Phase Transition Rule

- `Branch Readiness` -> `Workstream` only after branch base, branch class, authority record, and execution boundary are explicit
- `Workstream` -> `Hardening` when the changed branch truth must be pressure-tested or stabilized before closeout
- `Hardening` -> `Live Validation` only after repo-side hardening proof is sufficient for interactive or manual closeout work
- `Live Validation` -> `PR Readiness` only after branch-local proof is sufficient for closeout and returned evidence has been digested into the authority record
- `PR Readiness` -> `Release Readiness` only after merge-target canon completeness passes, the Governance Drift Audit passes, and either successor lock passes or successor lock is explicitly waived because post-merge truth resolves to `No Active Branch` due to `Release Debt` or another repo-level admission blocker
- `Release Readiness` -> `Post-Release Canon Repair` only as an emergency repair path after merged or released truth already exists and canon drift escaped the earlier gates

Later phases must not paper over missing earlier-phase requirements.
If a later phase discovers an earlier-phase defect, reopen the branch to the failed earlier phase.

## Phase Definitions

### Branch Readiness

Purpose:

- validate branch base
- declare branch class
- set up or confirm the promoted workstream authority record or branch authority record
- align branch-start canon
- lock execution, validation, and timeout boundaries

Allowed:

- source-of-truth audit
- branch-base validation
- branch-start canon sync
- workstream promotion, branch-record setup, or authority setup
- execution-boundary definition

Forbidden:

- implementation
- PR material preparation
- release packaging

Required evidence:

- updated `main` truth
- correct execution base
- explicit branch class
- explicit phase block in the authority record

Exit:

- branch base is valid
- active workstream authority exists
- exact phase state is recorded
- branch-start canon is coherent
- execution boundary is explicit

### Workstream

Purpose:

- execute the approved bounded implementation or bounded governance/docs work
- run normal repo-side regression validation inside that boundary

Allowed:

- bounded code or docs changes
- direct verification inside the approved scope

Forbidden:

- silent scope expansion
- hidden hardening or closure claims
- PR or release packaging

Required evidence:

- approved execution boundary
- direct verification of the changed behavior or docs

Exit:

- approved scope is implemented
- direct verification is complete
- no unresolved same-slice correctness gaps remain

### Hardening

Purpose:

- pressure-test the current branch truth
- stabilize defects, seams, validators, or harnesses before closeout

Allowed:

- validators
- harness work
- runtime helper work
- small supporting evidence infrastructure
- bounded corrective fixes

Forbidden:

- unrelated feature work
- new lane selection
- release packaging

Required evidence:

- validator results
- runtime results when relevant
- explicit distinction between product defects, harness defects, environment issues, and canon or contract drift

Exit:

- branch-local hardening gate is green
- no unresolved first-failing seam remains
- no truth-drift contradiction remains

### Live Validation

Purpose:

- prove the user-facing or operator-facing branch truth through interactive, manual, or launched-process evidence
- digest that evidence into canon

Allowed:

- interactive validation
- manual validation digestion
- UI audit when relevant
- validation-only support changes if the branch reopens to `Hardening` first

Forbidden:

- new implementation
- PR packaging
- behavior widening without reopening earlier phase

Required evidence:

- required interactive or manual evidence
- required UI audit evidence when applicable
- evidence digestion into the authority record

Exit:

- required interactive or manual evidence is green
- required UI audit exists when applicable
- returned evidence is digested into canon
- no unresolved validation contradiction remains

### PR Readiness

Purpose:

- determine whether the branch is ready to become a merge candidate without leaving merged canon stale and, when post-merge truth will admit a next branch, with the next lane already locked

Allowed:

- readiness review
- merge-target canon sync
- final drift checks
- next-workstream confirmation
- successor-branch creation
- Governance Drift Audit
- PR material preparation

Forbidden:

- implementation
- hardening
- release tagging
- skipping governance drift review

Required evidence:

- branch-local proof complete
- merge-target canon completeness gate passed
- successor lane lock gate passed, or successor lock explicitly waived because post-merge truth resolves to `No Active Branch` due to `Release Debt` or another repo-level admission blocker
- Governance Drift Audit completed
- no active seam
- no unresolved blocker that should have been repaired on the current branch before merge

Exit:

- ready for PR creation
- or returned to the failed earlier phase with explicit blockers

### Release Readiness

Purpose:

- determine whether merged or merge-ready truth is ready for release packaging

Allowed:

- release review
- release notes prep
- version or tag recommendations
- final release-candidate verification

Forbidden:

- implementation
- canon-sync mutation
- hidden fix work
- hidden next-lane planning

Required evidence:

- merged or legitimately merge-ready truth
- release-context verification
- no unresolved blocker

Exit:

- ready for release packaging
- or returned to the failed earlier phase with explicit blockers

## Repo-Level State: No Active Branch

`No Active Branch` is the repo-level state when no implementation lane is currently selected.

Use it when:

- the repo-level admission gate is failing
- merged canon drift remains unresolved
- release debt remains unresolved
- the only available implementation branch is stale, merged, or identical to `main`
- no branch should open yet by inertia even though repo truth is otherwise stable

`No Active Branch` may be:

- blocked:
  - a blocker or repair path must be cleared before the next implementation lane may begin
- steady-state:
  - no implementation branch is currently selected, and it is valid for the next safe move to be no branch at all until a new approved need exists

When `No Active Branch` is blocked:

- do not recommend a later branch phase
- do not start next-lane implementation
- report the blocker and the exact repair path instead

When `No Active Branch` is steady-state:

- do not start the next implementation branch by inertia
- it is valid for `Next Safe Move` to say explicitly that no branch should open yet
- an explicitly approved `docs/governance`, `release packaging`, or `emergency canon repair` branch may still enter `Branch Readiness` if its branch-class admission rules pass

## Exception Path: Post-Release Canon Repair

Purpose:

- perform emergency canon repair after a release only when merged truth is already live and canon drift escaped the earlier gates

Allowed:

- docs and canon repair tightly coupled to the released truth

Forbidden:

- treating post-release canon repair as a normal part of the standard lifecycle
- using post-release repair instead of the merge-target canon completeness gate
- turning the repair path into a new implementation lane by accident

Required evidence:

- updated `main`
- latest release truth
- explicit canon drift
- explicit reason the drift could not be prevented before merge or release

Exit:

- canon aligned to released truth
