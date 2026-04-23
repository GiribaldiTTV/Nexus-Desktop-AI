# Nexus Phase Governance

## Top Rule: Pre-PR Durability

**DO THIS ALWAYS before `PR Readiness`: when a bounded phase pass or durability seam changes source, docs, canon, validator, helper registry, workstream authority, or branch-truth files and validation is green, Codex must commit and push those changes on the active branch instead of stopping at a copy-ready, staged-only, or uncommitted state. This includes `Branch Readiness`, `Workstream`, `Hardening`, and `Live Validation`; a prompt-level request not to commit is not enough to stop durability. The only exceptions are a documented `Durability Waiver`, failed validation, a legally file-frozen phase such as `Release Readiness`, or a named Codex self-imposed blocker; when that self-imposed blocker is lifted, Codex must automatically commit and push.**

**Release Readiness is file-frozen: block ANY source, docs, canon, validator, helper registry, release-note, or handoff-file changes discovered or needed during `Release Readiness`. Do not edit, stage, commit, or push in `Release Readiness`; route the change back to `PR Readiness` before merge, or to the next active `Branch Readiness` after merge.**

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
- `Seam Sequence: <ordered seam list>` when the current phase permits a bounded multi-seam pipeline
- `Validation Contract: <summary or authority reference>`
- `Timeout Contract: <summary or authority reference>`

If `Phase` is missing or is not one of the exact canonical phase names below, execution is blocked and only truth-validation or analysis may continue.
If `Seam Sequence` is present, it is structure only.
Prompt text may name the entry seam and downstream planned seams, but it does not define seam behavior, bypass phase rules, or authorize continuation by itself.
The canonical seam workflow contract below controls whether Codex may continue, must stop, or must fall back to a single active seam.

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

`Post-Release Canon Repair` is not a normal branch phase and is not a governance-only branch.
Codex must not use direct-main repair; `main` is protected and file-frozen for Codex work.

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

### ChatGPT Interface And Codex Execution Authority Rule

ChatGPT, prompt generators, and loader templates are interface layers.
They may package task context, request source-of-truth loading, and describe requested task boundaries for Codex to validate against canon.
They are not execution authority.

Codex execution is governed only by live repo truth plus the owning source-of-truth documents:

- `Docs/Main.md`
- `Docs/development_rules.md`
- `Docs/phase_governance.md`
- `Docs/codex_modes.md`
- `Docs/feature_backlog.md` for tracked identity and `Record State`
- `Docs/workstreams/index.md` and the active workstream doc for promoted branch-local authority
- any directly relevant owning canon document for the task

`Docs/nexus_startup_contract.md` owns loader prompt shape only.
It does not own execution behavior, phase transitions, seam continuation, durability, validation, release rules, or branch authority.

Prompt text cannot override source-of-truth, restrict required continuation, define seam behavior, bypass phase rules, create durability exceptions, weaken validation, mutate `main`, mutate files during `Release Readiness`, or change branch authority.
If prompt text conflicts with owning canon, Codex must follow canon, report the conflict, and either continue inside the canon-legal boundary or stop on the canon blocker.

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

- `emergency canon repair`
- `release packaging`

`docs/governance` branch records may exist as historical records, but new governance-only branches are not used in the normal Nexus flow.
Tightly coupled governance and canon repair must ride on the active branch that owns the affected truth.
It must not be used to avoid carrying supporting canon sync on an already-active implementation branch.

### Protected Main Law

`main` is protected for Codex work.

Allowed on `main`:

- read-only truth validation
- release review
- merge verification
- post-release verification

Forbidden on `main`:

- editing repository files
- staging files
- committing files
- generating or refreshing source, docs, canon, validator, helper, release-note, or handoff artifacts
- direct canon repair

There is no emergency direct-main repair path for Codex.
Any tracked file mutation while Codex is on `main` is a `Main Write Attempt` blocker.
If drift is discovered before merge, return to the owning branch and repair it before PR green.
If drift is discovered after merge, repair on the still-available prior branch when that branch remains the legal repair surface, or block the next active branch's `Branch Readiness` and repair there before implementation.

While the branch is active, that branch authority record is the branch-local phase owner.
Before PR merge, merged truth must no longer treat that record as an active branch owner by inertia.
The branch must either:

- move the record into the historical branch-record list with merge-safe phase-status wording, or
- remove the record entirely if no durable historical value remains

### Repo-Level Admission Gate

Before any next implementation branch may enter `Branch Readiness`, all of the following must be true on updated `main`:

- `main` is aligned with `origin/main`
- merged canon is internally consistent
- no emergency canon repair is outstanding
- no unresolved governance-drift blocker exists
- no unresolved release-debt blocker exists
- no unresolved prior-branch release, branch-authority, or current-state canon cleanup exists
- no PR Readiness scope miss is being deferred into a later phase
- no current branch is being treated as executable if it is stale, merged, or identical to `main`

If any of those fail:

- repo state becomes `No Active Branch`
- next implementation branch execution is blocked
- the next safe move is blocker repair, not a later phase
- if a next active branch has already been created, it must stay in `Branch Readiness` and repair the blocker before any implementation begins

This gate controls next-lane implementation admission.
It does not authorize a governance-only branch.
Release packaging branches still satisfy their own admission rules below.

### Pre-PR Durability Rule

Before `PR Readiness`, when a bounded phase pass or durability seam changes source, docs, canon, validator, helper registry, workstream authority, or branch-truth files and validation is green, Codex must commit and push those changes on the active branch instead of stopping at a copy-ready, staged-only, or uncommitted state.

A prompt-level request to stop before commit/push is not a durability exception. Only a documented `Durability Waiver`, failed validation, a legally file-frozen phase such as `Release Readiness`, or a named Codex self-imposed blocker may stop commit/push. If Codex names a self-imposed blocker, the authority record or response must say what lifts it; once lifted, Codex must automatically commit and push without requiring a second durability prompt.

This rule applies through:

- `Branch Readiness`
- `Workstream`
- `Hardening`
- `Live Validation`

If validation fails, Codex must not commit and push; it must report the blocker and keep the branch in the current phase until the blocker is lifted.
`PR Readiness` remains the later merge-target gate and must still prove clean durable branch truth before PR creation.

### Blocker Catalog

The default named blockers are:

- `Prompt Phase Missing`
- `Prompt Phase Mismatch`
- `Workstream Phase Authority Missing`
- `Branch Base Invalid`
- `Merged Canon Drift`
- `Stale Canon`
- `Phase Exit Unmet`
- `Next Workstream Undefined`
- `Successor Lock Missing`
- `Post-Merge State Unresolved`
- `Dirty Branch`
- `Docs Sync Incomplete`
- `Release Debt`
- `Release Target Undefined`
- `Release Readiness File Mutation Attempt`
- `User-Facing Shortcut Validation Pending`
- `User Test Summary Results Pending`
- `PR Creation Pending`
- `PR Validation Pending`
- `PR State Unknown`
- `PR Readiness Scope Missed`
- `Release Readiness Scope Drift`
- `Prior Branch Canon Unresolved`
- `Between-Branch Canon Repair Attempt`
- `Main Write Attempt`
- `Next Branch Created Too Early`
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
`docs/governance` remains a recognized historical branch class, but it is not an approved new-branch lane in the normal Nexus flow.
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
- docs-only governance or canon refinements may ride on the active implementation branch when they are directly required to keep that branch truthful, executable, phase-correct, readiness-correct, validation-correct, closeout-correct, or release-correct
- those refinements do not change the branch class; they must stay inside the current phase, remain explicit in scope, preserve validation and stop conditions, and avoid unrelated governance churn

`docs/governance`

- is preserved only for historical records and explicit legacy interpretation
- must not be opened as a new governance-only branch in the normal Nexus flow
- must not be used for between-branch canon repair
- must not be used to carry PR Readiness work after the branch that owned that work has merged
- if governance or canon work is directly required to keep the current branch truthful, executable, phase-correct, readiness-correct, validation-correct, closeout-correct, or release-correct, that work must ride on the active current branch inside its current phase and branch class
- if a PR Readiness miss is discovered after merge, the next active branch's `Branch Readiness` must carry the repair before implementation begins
- if no active branch exists and no next workstream can be selected, the repo remains `No Active Branch`; Codex must not repair directly on `main`

`release packaging`

- may begin from updated `main` when merged-unreleased implementation, release notes, tagging, or another release-facing packaging task is explicitly opened
- the branch must not widen into implementation work

`emergency canon repair`

- is preserved only as historical vocabulary
- is not a normal branch lane in the current Nexus flow
- does not authorize direct-main repair by Codex
- if escaped canon drift exists, the default repair is the still-available prior branch when legal, or the next active branch's `Branch Readiness`

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
- `Docs/branch_records/index.md` plus any relevant branch authority record when the branch is an approved non-backlog branch that would otherwise remain incorrectly active after merge

If any required merge-target canon update is missing, the branch remains blocked in `PR Readiness`.

### Merged-Unreleased Release-Debt Owner Contract

When an implementation branch will merge unreleased product behavior beyond the latest public prerelease, PR Readiness must leave exact post-merge release-debt truth in canon before PR green.

Required machine-checkable fields:

- `Merged-Unreleased Release-Debt Owner:`
- `Repo State: No Active Branch`
- `Release Target:`
- `Release Floor:`
- `Version Rationale:`
- `Release Scope:`
- `Release Artifacts:`
- `Post-Release Truth:`
- `Selected Next Workstream:`
- `Next-Branch Creation Gate:`

Required owner docs:

- `Docs/feature_backlog.md` names the workstream as merged-unreleased release debt, not active execution truth
- `Docs/prebeta_roadmap.md` names the current release-debt owner, release target, release scope, release artifacts, selected next workstream, and branch-creation gate
- `Docs/workstreams/index.md` moves the workstream from `Active` to `Merged / Release Debt Owners`
- the canonical workstream doc records the same merged-unreleased release-debt owner contract

Release Readiness consumes this inherited release truth.
Release Readiness may validate target, scope, artifacts, and post-release truth, but it must not create or repair those fields in repository files.

Release target correctness is semantic, not marker-only.
PR Readiness must derive the target from the latest public prerelease and the declared `Release Floor:` before green:

- `patch prerelease` increments only the patch number, for example `v1.4.0-prebeta` -> `v1.4.1-prebeta`
- `minor prerelease` increments the minor number and resets patch to zero, for example `v1.4.0-prebeta` -> `v1.5.0-prebeta`

Release floor ownership:

- `patch prerelease` is the default floor for bug fixes, UX polish, governance fixes, documentation/canon repair, architecture-only planning, admission contracts, validation-only work, and non-user-facing milestones that do not add executable product behavior.
- `minor prerelease` is allowed only when the release delivers a new executable, runtime, operator-facing, user-facing, or materially expanded product capability lane.
- Opening a future planning lane, writing architecture, defining vocabulary, or creating an admission contract is not enough by itself to justify `minor prerelease`.
- If a public tag has already been published with a larger bump than the corrected law would choose, do not rewrite the public tag; record the published tag as latest release truth, classify the mismatch as version-advancement drift, and harden future `Release Floor:` validation.

If the declared target, artifacts, or post-release truth do not match the semantic release floor, keep `Release Target Undefined` active and repair the mismatch in PR Readiness before Release Readiness.

Post-release closure is mandatory after release execution:

- once a public prerelease tag exists for a merged-unreleased release-debt owner, durable canon must move that workstream to Released / Closed
- `Docs/prebeta_roadmap.md` must advance latest public prerelease truth to the published tag
- `Docs/feature_backlog.md` must mark the owner `Record State: Closed` and `Status: Released`
- `Docs/workstreams/index.md` must remove the owner from `Merged / Release Debt Owners` and list it under `Closed`
- the canonical workstream doc must record `Latest Public Prerelease:`, `Release Title:`, released/closed state, and cleared release debt
- if this closure is missed after merge or release, the next active branch's `Branch Readiness` is blocked until the closure is repaired and validator coverage is updated so the miss cannot recur

### Successor Lane Lock Gate

Rule:

- a branch is not `PR Readiness`-complete unless the next workstream is selected, canon-defined, assigned a valid record state, minimally scoped, and explicitly not branched yet

Exception:

- If post-merge truth will resolve to `No Active Branch` because `Release Debt` or another repo-level admission blocker remains open, successor branch creation remains deferred; next-workstream selection is still required unless the user explicitly approves a no-next-workstream steady-state outcome in canon.

This gate requires all of the following before PR creation is allowed:

- the next workstream identity is selected from current canon using open backlog `Priority` plus deferred-context readiness, not `Target Version`
- that workstream exists in `Docs/feature_backlog.md`
- that workstream is recorded in `Docs/prebeta_roadmap.md`
- that workstream has a canon-valid `Record State`
- that workstream has `Priority` defined
- if that workstream is deferred, the backlog entry records `Deferred Since:`, `Deferred Because:`, and `Selection / Unblock:`
- that workstream has minimal scope defined before PR green
- no branch has been created for that next workstream yet
- successor branch creation is deferred to `Branch Readiness` after the current branch merges and updated `main` is revalidated

`Target Version` is not a next-workstream selection field. Do not use it to rank, select, defer, or skip open backlog candidates. Release targets are assigned by release-floor and release-readiness governance when a release-bearing branch requires them. Closed, released, implemented, or release-debt entries may preserve `Target Version` as historical release evidence.

Machine-checkable canon markers:

- the selected backlog entry must include `Next Workstream: Selected`
- the selected backlog entry must include `Minimal Scope:`
- the roadmap must include `## Selected Next Workstream`
- the roadmap selected-next section must include the same workstream id, its `Record State`, `Minimal Scope:`, and branch status such as `Branch: Not created`

When the exception applies, the branch must instead:

- make the post-merge `No Active Branch` state explicit in current-state canon
- name the blocking admission item explicitly
- keep the selected next workstream as canon planning only
- avoid creating or executing the next implementation branch by inertia

If the next workstream is not selected, is not recorded in backlog and roadmap, lacks valid record state, or lacks minimal scope, the branch is blocked by `Next Workstream Undefined`.
If a selected deferred workstream lacks deferred-context fields, the branch is blocked by `Deferred Selection Context Missing`.
If a successor branch is created before `Branch Readiness`, the branch is blocked by `Successor Lock Missing`.

### PR Readiness Hard Blocker Gates

PR Readiness must not report green while any pre-merge process blocker remains unresolved.

Hard blockers:

- canonical shorthand: `stale-canon`, `post-merge`, `dirty`, `docs-sync`, `next-workstream`, `deferred-context`, `desktop-shortcut`, `uts-results`
- `Stale Canon`:
  current-state canon and merge-target canon must already reflect the branch's true state and the state that will be true after merge
- `Post-Merge State Unresolved`:
  post-merge truth must already encode either the `No Active Branch` / `Release Debt` path or the successor-workstream planning, canon sync, and branch-creation deferral required when post-merge truth will admit another branch
- `Next Workstream Undefined`:
  PR Readiness cannot be green until the next workstream exists in canon, is recorded in backlog and roadmap, has a valid record state, has minimal scope defined, and has no branch created yet
- `Deferred Selection Context Missing`:
  PR Readiness cannot be green when the selected next workstream is deferred but lacks `Deferred Since:`, `Deferred Because:`, or `Selection / Unblock:` in the backlog entry
- `Dirty Branch`:
  PR Readiness cannot be green while the worktree is dirty, required docs changes are uncommitted, required canon exists only in the working tree, or branch truth is not durable in commit history
- `Docs Sync Incomplete`:
  docs sync, Governance Drift Audit, validator alignment, and any required post-merge state wording must be complete and mutually consistent
- `User-Facing Shortcut Validation Pending`:
  Live Validation and PR Readiness cannot be final-green for a relevant desktop user-facing workstream until the final Live Validation closeout has launched through the declared user-facing desktop shortcut or equivalent user entrypoint, recorded `User-Facing Shortcut Validation: PASS` or `User-Facing Shortcut Validation: WAIVED`, and preserved the evidence before User Test Summary handoff
- `User Test Summary Results Pending`:
  PR Readiness cannot be green while a user-facing workstream has a required User Test Summary handoff outstanding and returned results have not been submitted, waived, digested into the active authority record, and reevaluated
- `PR Creation Pending`:
  PR Readiness package-ready is not PR Readiness green. PR Readiness cannot be green until the GitHub PR exists for the current head branch and base branch.
- `PR Validation Pending`:
  PR Readiness cannot be green until the existing PR has been validated as open, non-draft, conflict-free, aligned to the merge-target canon, and clear of unresolved Codex comments/issues or requested changes.
- `PR State Unknown`:
  PR Readiness cannot be green if Codex cannot inspect the PR state, mergeability/conflict state, base/head alignment, or Codex review-thread state.
- `PR Readiness Scope Missed`:
  PR Readiness cannot be green if branch-authority cleanup, merge-target canon, post-merge truth, next-workstream selection, next-branch deferral, or release-debt routing is incomplete or being deferred to Release Readiness, updated `main`, or a later governance-only branch
- `Between-Branch Canon Repair Attempt`:
  PR Readiness cannot rely on any canon repair that is planned between branches rather than committed on the active branch before merge
- `Next Branch Created Too Early`:
  PR Readiness cannot be green if the next implementation branch already exists before the current branch has merged and updated `main` has been revalidated

The PR-readiness validator gate must be run in its PR-specific mode before reporting `PR READY: YES`.
If the normal governance validator passes but the PR-specific gate reports dirty worktree or unresolved PR blockers, the result is not PR-ready.

`PR package ready` is the state where local branch truth, merge-target canon, next-workstream selection, and copy-ready PR details are complete. It is not `PR Readiness GREEN`.

`PR Readiness GREEN` requires all `PR package ready` conditions plus:

- the GitHub PR exists
- the PR is open and not draft
- the PR base/head match merge-target canon
- the PR has no conflicts
- PR state is inspectable rather than unknown
- no unresolved Codex comments/issues or requested changes remain

### PR Readiness Response Contract

When `PR Readiness` reports package-ready or `PR package ready`, the response must include a repo-wide standardized `Next Branch` block and markdown-friendly PR operator copy blocks.
Those package details are the input to PR creation and validation; they are not themselves proof that PR Readiness is GREEN.
This is a response contract, not permission to create the PR, merge the branch, release the branch, or create the next branch.

The `Next Branch` block must distinguish the next legal branch from the selected next implementation branch.
For example, if post-merge truth creates `Release Debt`, the next legal branch may be a release packaging branch while the selected next implementation branch remains deferred until after release handling and updated-`main` revalidation.

Required `Next Branch` block:

```markdown
## Next Branch
- Next Legal Branch Type:
- Next Branch Name:
- Branch Class:
- Creation Status:
- Creation Gate:
- Selected Next Workstream:
- Selected Next Implementation Branch:
- May Create Now: YES / NO
- Reason:
```

Required PR operator copy blocks:

````markdown
## PR Creation Details
### PR Title
```text
<title only>
```

### Base Branch
```text
<base branch only>
```

### Head Branch
```text
<head branch only>
```

### PR Summary
```markdown
<implemented work only>
```
````

Each PR operator field must be its own copy-ready block and must be usable independently.
The PR summary must describe implemented work, validation evidence, governance/canon state, post-merge truth, and next-branch handling only when those items are part of the implemented branch truth.
The PR summary must not include exclusion lists, `Not Included` sections, or defensive scope language.
If `May Create Now` is `NO`, the `Next Branch` subsection must explain the blocking gate rather than implying branch creation is allowed.

### Operator Output Content Rule

Operator-facing PR summaries and GitHub release notes are inclusion-only.
They must report what exists, what was implemented, what capabilities are available, how the system behaves, and which validation or release facts support the package.
They must not report what was not done, include exclusion lists, use `Not Included` sections, or use defensive scope framing.
GitHub release notes must also use the standard Markdown release body shape: `# <release title>`, `## Release Summary`, `## Release Highlights`, GitHub-generated `## What's Changed`, and the generated `**Full Changelog**:` compare link to the previous release.
This rule governs operator output packages; it does not remove normal canon requirements for branch scope, non-goals, stop conditions, or blockers in source-of-truth records.

### User-Facing Shortcut Live Validation Gate

For relevant desktop user-facing workstreams, Live Validation may use validators, direct runtime launches, helper launches, synthetic harnesses, and targeted manual probes to build scenario coverage.
Those evidence layers are supporting proof, not final green by themselves.

Before User Test Summary handoff, the final Live Validation closeout must launch and exercise the branch through the same user-facing desktop shortcut or equivalent user entrypoint that the user is expected to use.
For Nexus Desktop AI, the default desktop shortcut path is normally `C:\Users\anden\OneDrive\Desktop\Nexus Desktop Launcher.lnk` unless the active authority record declares an explicit equivalent.

Named blocker:

- `User-Facing Shortcut Validation Pending`

Machine-checkable authority-record markers:

- `User-Facing Shortcut Path:`
- `User-Facing Shortcut Validation: PENDING`
- `User-Facing Shortcut Validation: PASS`
- `User-Facing Shortcut Validation: FAIL`
- `User-Facing Shortcut Validation: WAIVED`
- `User-Facing Shortcut Waiver Reason:`

Required proof:

- the declared user-facing shortcut or equivalent entrypoint launches the active branch runtime
- startup reaches the expected ready state
- the user-visible entry surface introduced or changed by the branch is visible or intentionally documented where the user must look for it
- relevant runtime markers, UI/manual readback, persisted-state checks, and cleanup evidence match the branch validation contract
- helper-only, direct-Python, or harness-only evidence is not treated as a substitute for this final shortcut gate when the shortcut path is feasible

Lift condition:

- `User-Facing Shortcut Validation: PASS` is recorded with evidence from the declared shortcut path, or `User-Facing Shortcut Validation: WAIVED` is recorded with `User-Facing Shortcut Waiver Reason:` showing the branch is not desktop/user-facing or the shortcut path is explicitly unavailable
- the blocker state is reevaluated after the result is digested

Routing:

- while `User-Facing Shortcut Validation: PENDING` remains, list `User-Facing Shortcut Validation Pending` under blockers and do not advance
- if `User-Facing Shortcut Validation: FAIL`, keep an explicit blocker and route back to `Workstream` or `Hardening` before PR Readiness
- if the shortcut gate passes or is waived, User Test Summary handoff may proceed only if all other Live Validation gates are green

### User Test Summary Results Gate

Live Validation and PR Readiness must not report final green while a relevant user-facing workstream has a required User Test Summary handoff outstanding and returned results have not been submitted and digested.

Named blocker:

- `User Test Summary Results Pending`

Required status model:

- Automated validators and live helper evidence: GREEN.
- User Test Summary Results: PENDING.
- Final phase advancement is BLOCKED until the filled User Test Summary is submitted and digested.

Machine-checkable authority-record markers:

- the active authority record must include an exact `## User Test Summary` section; `## User Test Summary Strategy` is planning context and is not the canonical `UTS` artifact
- while pending, the active authority record must include `User Test Summary Results: PENDING`
- while pending, the active authority record must list `User Test Summary Results Pending` under `## Blockers`
- while pending, `## Next Legal Phase` must not advance beyond the current phase
- when passing returned results are digested, the active authority record must include `User Test Summary Results: PASS` and a digest of the returned results before the blocker can clear
- when a waiver is used, the active authority record must include `User Test Summary Results: WAIVED` and `User Test Summary Waiver Reason:` before the blocker can clear
- when returned results fail or expose ambiguity, the active authority record must keep or replace the blocker with the appropriate Workstream or Hardening blocker and route backward rather than advancing

Lift condition:

- a filled User Test Summary is submitted or a documented waiver exists
- the results or waiver are digested into the active authority record
- the blocker state is reevaluated after digestion

Routing after digestion:

- if returned results pass, `User Test Summary Results Pending` clears and forward progression may continue if all other gates pass
- if returned results expose mismatch, regression, unclear behavior, cleanup failure, or scope drift, route back to `Workstream` or `Hardening` as appropriate
- if returned results raise new feature ideas, keep them out of current scope until backlog carry-forward is explicitly approved

### Release Readiness Target Gate

Release Readiness must not report green while any release target blocker remains unresolved.

Release Readiness is an analysis-only file-freeze phase. Required release target, scope, and artifact truth must already exist before entering Release Readiness, normally as PR-owned merge-target canon or a PR-ready response package. If Release Readiness analysis discovers that those fields are missing, ambiguous, stale, or require source-file changes, do not patch files inside Release Readiness. Return the active branch to `PR Readiness` if it has not merged; if the branch has already merged, defer the repair to the next active branch's `Branch Readiness`.

Hard blocker:

- `Release Target Undefined`:
  Release Readiness fails for a release-bearing branch unless the active branch authority record or active workstream authority record explicitly identifies all required release-bearing markers:
  - `Release Target:`
  - `Release Floor:`
  - `Version Rationale:`
  - `Release Scope:`
  - `Release Artifacts:`

  The target must also be semantically correct from the latest public prerelease and declared release floor; marker presence alone is not enough.

A branch is release-bearing when:

- its branch class is `release packaging`
- or it creates, prepares, validates, tags, publishes, or transitions release-facing artifacts or release-state canon

The only non-release waiver is:

- the active authority record explicitly declares `Release Branch: No`
- the record is preserved historical truth
- the branch does not create, prepare, validate, tag, publish, or transition release-facing artifacts or release-state canon

The non-release waiver is not available to `implementation` or `release packaging` branches.
It does not waive `Release Debt`, merge-target canon completeness, post-merge truth, successor lock, validation, or dirty-branch requirements.

If release target markers are missing on a release-bearing branch, the branch is blocked by `Release Target Undefined`.
If `Release Branch: No` appears outside a preserved historical record, the branch is blocked by `Phase Waiver Missing`.
If any source, docs, canon, validator, helper, or release-note file is modified while the active phase remains `Release Readiness`, the branch is blocked by `Release Readiness File Mutation Attempt` and must return to `PR Readiness` or defer to the next active branch's `Branch Readiness` before the change can be made.

### Release Readiness Scope Boundary

Release Readiness is not a docs-sync phase. It is also not a file-mutation phase.

Release Readiness is analysis-only for repository files:

- it may inspect repo truth, branches, tags, releases, validator output, and release evidence
- it may produce release package information in the response, including tag, title, release notes, and release-execution instructions
- it may run validation commands that do not mutate tracked source files
- it must not edit, stage, commit, generate, or refresh source, docs, canon, validator, helper, release-note, or desktop handoff files

Allowed in `Release Readiness`:

- release-target validation
- release-scope validation
- release-artifact validation
- GitHub release package information such as tag, title, and release notes
- final release-execution authorization or confirmation
- release-state confirmation after the release execution

Forbidden in `Release Readiness`:

- broad canon or docs sync that should have been completed in `PR Readiness`
- branch-authority cleanup that should have been merge-safe before PR green
- next-workstream selection, planning, or branch creation
- between-branch canon repair
- any source, docs, canon, validator, helper, release-note, or handoff-file mutation
- any direct write to protected `main`

### Release Readiness Operator Output Contract

When `Release Readiness` is green for release execution, the response must include markdown-friendly release operator copy blocks for direct GitHub release use.

Required release operator copy blocks:

````markdown
## Release Package Details
### Release Title
```text
<release title only>
```

### Release Tag
```text
<tag only>
```

### Target Commit
```text
<commit sha only>
```

### Release Notes
```markdown
<detailed user-facing release notes>
```
````

Each release operator field must be its own copy-ready block and must be usable independently.
Release notes must be detailed, descriptive, and user-facing.
They must clearly explain what was built, what capabilities exist, and how the system behaves.
Release notes must follow the operator output content rule: report included work only, with no exclusion lists, `Not Included` sections, negative scope framing, or defensive wording.
The live GitHub release body must use the standard Markdown release body shape:

- `# <release title>`
- `## Release Summary`
- `## Release Highlights`
- `## What's Changed`
- `**Full Changelog**:`

The `## What's Changed` section and `**Full Changelog**:` compare link must be populated by GitHub-generated release notes, using the GitHub release notes button or the generated-release-notes API with the previous release selected. Release Readiness may prepare the human-written summary and highlights, but Release Execution must combine them with the GitHub-generated notes before publication or repair the release body immediately after publication.

If Release Readiness discovers missing PR-owned canon or docs work, stop immediately and classify the issue as `PR Readiness Scope Missed` and `Release Readiness Scope Drift`.
If the branch has not merged, return to `PR Readiness` and repair the miss there before any Release Readiness output can be treated as green.
If the branch has already merged, the next active branch's `Branch Readiness` must repair the miss before implementation begins and must update governance or validator coverage so the miss cannot recur.

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
- fix it on the active branch when the drift is tightly coupled to that branch's truth, phase, readiness, validation, closeout, or release state, or
- produce the exact required canon delta and wait for user confirmation when the repair would exceed the active branch boundary

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
- release-bearing branches carry `Release Target:`, `Release Floor:`, `Version Rationale:`, `Release Scope:`, and `Release Artifacts:` markers before Release Readiness can report green
- release-target semantics match the latest public prerelease and declared release floor before PR Readiness or Release Readiness can report green
- Release Readiness is analysis-only and cannot mutate files; dirty tracked files while the authority record says `Release Readiness` are a `Release Readiness File Mutation Attempt`
- non-release waiver records use `Release Branch: No` only for preserved historical records
- unresolved blockers prevent phase advancement
- active-branch governance and canon updates remain the primary path when tightly coupled to the active branch's truth, phase, readiness, validation, closeout, or release state
- governance-only branches are not used for new Nexus work, and between-branch canon repair attempts are blocked
- Release Readiness cannot absorb PR Readiness docs sync or canon repair
- prior-branch canon misses block the next active branch in Branch Readiness before implementation can begin
- the canonical `bounded multi-seam workflow` contract is present in governance and operator scaffolds
- prompt scaffolds teach `Seam Sequence`, per-seam validation, and continue-or-stop decisions for multi-seam Workstream execution
- docs do not teach direct `Workstream` -> `PR Readiness` as the default path
- PR Readiness prompt scaffolds require the standardized `## Next Branch` block and inclusion-only `## PR Creation Details` operator copy blocks before reporting PR green
- Release Readiness prompt scaffolds require inclusion-only `## Release Package Details` operator copy blocks when release execution is green

A governance or current-state canon branch is not complete until that validator is green.

When branch authority records are active, the validator should also verify:

- `Docs/branch_records/index.md` exists and routes to the active branch authority records
- active branch authority records carry the required phase-state block
- `No Active Branch` blocked-versus-steady-state handling stays consistent across the governance and operator docs
- new governance-only branches remain blocked during `pre-Beta`; historical `docs/governance` records are allowed only as preserved history

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

## Validation Helper Registry And Naming Standard

`Docs/validation_helper_registry.md` is the repo-wide registry for durable root `dev/` validators, live-validation scripts, audit helpers, harnesses, and shared helper modules.

The registry must define:

- the canonical helper naming scheme
- the allowed `Helper Status:` values
- which helpers are `Reusable`
- which helpers are `Workstream-scoped`
- which helpers are `Temporary probe`
- the owner, reason, consolidation target, and promotion decision point for every workstream-scoped durable helper

Naming standard:

- repo-side validators use `dev/orin_<domain>_<capability>_validation.py`
- live desktop helpers use `dev/orin_<domain>_<capability>_live_validation.ps1`
- interactive suites use `dev/orin_<domain>_<capability>_interactive_validation.ps1`
- audit helpers use `dev/orin_<domain>_<capability>_audit.ps1`
- reusable harnesses use `dev/orin_<domain>_<capability>_harness.py`
- shared helper modules use `dev/orin_<domain>_<capability>_helper.py`

Workstream-scoped exceptions are allowed only when reuse would contaminate proof ownership, blur workstream truth, or make validation less reliable.
They must use `dev/orin_<workstream_id>_<bounded_capability>_validation.ps1` or `dev/orin_<workstream_id>_<bounded_capability>_live_validation.ps1`, be registered immediately, and carry:

- `Helper Status: Workstream-scoped`
- `Owner Workstream:`
- `Reason Reusable Helper Was Not Extended:`
- `Consolidation Target:`
- `Promotion Decision Point:`

Seam-number helper names are not the default naming model.
They are permitted only as short-lived workstream-scoped bridge names created during active seam proof, and they must be consolidated, promoted, or explicitly justified before PR Readiness.

PR Readiness must fail if a new durable root `dev/` validation helper, live-validation script, audit helper, harness, or shared helper module is unregistered, has no helper status, or is workstream-scoped without a consolidation target.

## Live Validation Reuse-First Rule

Before creating a new live-validation helper, script, or harness, Codex must inventory existing repo helpers and choose the smallest safe reuse path.

Preferred order:

1. inspect `Docs/validation_helper_registry.md`
2. use an existing helper unchanged when it already covers the needed path
3. parameterize or extend an existing helper when the validation belongs to the same desktop/runtime helper family
4. extract shared helper support when multiple helpers need the same watchdog, progress, cleanup, UIAutomation, runtime startup, saved-state snapshot, or artifact-writing behavior
5. create a new workstream-scoped helper only when reuse would contaminate the helper boundary, blur workstream truth, or make validation less reliable

One-off probes are allowed only as temporary exploratory evidence under an ignored evidence root such as `dev/logs/...`.
They must not be used as closeout-grade proof, must not be left behind as de facto reusable tooling, and must either be deleted after the pass or deliberately promoted into a documented reusable helper with workstream artifact-history notes.

If a Live Validation pass needs helper or harness changes before it can produce trustworthy evidence, the branch must reopen to `Hardening` unless the active authority record explicitly allows validation-only support edits in `Live Validation`.

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

## Seam Workflow Contract

`Docs/phase_governance.md` is the canonical owner of seam workflow behavior.
Prompts, workstream docs, and mode docs may name a seam chain, active seam, or validation focus, but they do not define continuation authority.
Codex must derive continuation, stopping, fallback, and phase movement from source-of-truth, validation, branch truth, and this contract.

### Phase Scope

Seam workflow applies differently by phase:

- `Branch Readiness` may use planning, admission, or tightly coupled governance-repair seams, but it must not execute product/runtime implementation.
- `Workstream` uses the full bounded multi-seam pipeline as the primary execution model when an approved seam chain remains inside its governed boundary and validation stays green.
- `Hardening` may use a constrained continuous validation loop when the branch is already inside an approved hardening boundary.
- `Live Validation` may use validation, evidence-digestion, waiver, or output-contract seams; it must not become a hidden implementation phase.
- `PR Readiness` uses readiness-gate seams for merge-target canon, drift audit, PR creation, and PR validation; it is not a product implementation seam pipeline.
- `Release Readiness` is analysis-only and file-frozen; it may use review steps in output, but it must not execute file-mutating seams.

### Bounded Multi-Seam Workflow

A bounded multi-seam workflow is an ordered sequence of seams executed inside one approved phase boundary.
It is the default execution model for any governed pass that names an approved seam sequence.
Every seam in the sequence must stay within:

- the same workstream or equivalent active authority record
- the same normal phase
- the same branch class
- the same approved scope or tightly coupled governance/validation repair scope
- a validation surface strong enough to prove the seam before continuation

Multi-seam does not mean batch execution.
It means Codex continues across a planned seam sequence without requiring a new operator prompt after every seam, while still executing exactly one active seam at a time.
Risky categories such as UI, launcher, settings, protocol, cross-subsystem, or policy work require sharper per-seam boundaries and stronger validation, not an automatic stop.

### Default Continuation Duty

`Next-Seam Continuation Required` is the default result after a green seam in a valid bounded multi-seam workflow.
When a prompt names an `Active Seam` or says to execute a seam that also appears inside an approved seam sequence, that seam is the entry seam, not a terminal boundary.
After the entry seam validates green, Codex must evaluate the next seam in the sequence from source-of-truth and continue by default when the continuation authority conditions pass.

Codex must not stop merely because:

- the prompt task named only the entry seam
- the output format asks for `Next Safe Move`
- durability commit and push completed
- one seam was successfully recorded

reporting `Next Safe Move` is not a substitute for execution when continuation authority passes.
A `continue` decision must be acted on immediately by starting the next seam in the approved sequence.
Durability commit/push after a green seam is a checkpoint, not a stop.
Do not send a final closeout response after a green entry seam while the next seam remains admitted and no bounded stop condition exists.

Stopping after a green seam requires a recorded bounded stop condition from this contract.

A prompt-level `execute only <seam>` request does not override this continuation duty unless the request is paired with a bounded stop condition or another named blocker from this contract.
If Codex stops after a green seam without one of the recorded reasons above, classify that stop as `Governance Drift` and repair the source-of-truth or validator gap before treating the workflow as healthy.

### Seam Stages

Each active seam follows this governed stage model:

1. `Stage 0 - Startup and admission`: load the required source-of-truth, confirm branch, phase, branch class, blockers, active authority record, and whether multi-seam continuation is legal.
2. `Stage 1 - Seam analysis and plan`: define the seam name, exact boundary, affected files or evidence surfaces, explicit non-includes, validation gate, cleanup expectations, risk class, and `UTS` applicability.
3. `Stage 2 - Execution`: execute only the active seam within the approved boundary.
4. `Stage 3 - Review and validation`: run the seam validation, inspect results, classify defects or drift, and loop back to Stage 2 only for the same seam when validation, stop-loss, and phase rules allow.
5. `Stage 4 - Record truth and continuation decision`: update branch-local workstream evidence, authority records, `UTS` artifacts, helper registry, or governance docs only when truth changed and the phase permits mutation; then report `continue` or `stop`.
6. `Stage 5 - Finalization`: summarize work, validation, cleanup, durability state, remaining blockers, next legal phase, and next safe move.

Stage 4 is not permission to churn canon after every seam.
Repository files are updated only when branch-local truth, evidence, validation contracts, helper records, or governing rules actually changed and the current phase permits file mutation.

### Required Per-Seam Declaration

Before each seam, Codex must state:

- the seam name
- the active phase and branch class
- the exact boundary
- the affected files or evidence surfaces when known
- the explicit non-includes
- the validation gate required for that seam
- cleanup expectations when the seam opens files, processes, windows, helpers, or temporary artifacts
- `User Test Summary` applicability when user-visible or operator-facing behavior may be affected

After each seam, Codex must:

- run the required validation for that seam
- update active workstream evidence when branch-local truth changed
- update the canonical workstream `User Test Summary` when the seam changes user-visible or operator-facing behavior
- verify cleanup for artifacts the pass created or opened
- decide and report `continue` or `stop`
- continue by default to the next planned seam when `Next-Seam Continuation Required` applies and the continuation authority conditions pass
- act on a `continue` decision by starting the next seam before final closeout

### Continuation Authority

Continuation is allowed only when:

- validation passes
- no regression is detected
- no scope drift is detected
- no unplanned risk-class expansion is detected
- no governance drift is detected
- no unresolved manual-validation blocker is present
- branch truth remains consistent with the authority record
- stop-loss has not been reached
- the next seam remains inside the same permitted phase scope

If any continuation condition fails, the whole workflow stops immediately and the next safe move must be reported from the blocking truth.
If continuation would require broader authority, a different phase, unplanned risk expansion, or weaker validation, Codex must stop and report the blocker rather than treating the downstream seam as activated.
If all continuation conditions pass and the next planned seam remains inside the approved sequence, continuation is required under `Next-Seam Continuation Required`; do not downgrade a safe continuation into an optional stop.

### Bounded Stop Conditions

A bounded multi-seam workflow may end before phase completion only when one of these serious stop conditions is recorded:

- validation failure
- regression or failed evidence review
- scope drift or attempted work outside the approved seam chain
- unplanned risk-class expansion that requires a new admission decision
- governance drift that must be repaired before continuation
- branch-truth contradiction or dirty-state contradiction that changes phase authority
- unresolved manual-validation, User Test Summary, or live-evidence blocker
- missing source-of-truth, unreadable authority, or conflicting authority ownership
- stop-loss trigger, timeout/freeze risk, or unsafe tool/process state
- phase boundary reached, phase completion reached, or next seam belongs to a different phase
- the next seam would require weaker validation than the current seam
- explicit operator stop, pause, or waiver that does not conflict with protected-main, Release Readiness, or durability law

Category labels are not stop conditions by themselves.
Bug fix, hotfix, UI-model, launcher, settings, protocol, policy, cross-subsystem, or high-risk labels may require smaller seams and stronger gates, but they do not cancel bounded multi-seam continuation when the next seam remains admitted and green.

## Single-Seam Fallback Rule

`Single-Seam Fallback` is not a category shortcut.
It is a bounded stop decision after one seam, allowed only when the pass records one of the bounded stop conditions above or when source-of-truth admits exactly one seam and no next seam exists.

When `Single-Seam Fallback` is used, the output or authority record must name:

- the bounded stop condition
- why continuation would be unsafe, invalid, or outside phase authority
- the lift condition or next legal phase

It does not authorize phase skipping, readiness claims, or stopping a green approved seam chain merely because the work is high-risk.

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
- every interactive helper or live-validation run must emit visible progress before and during execution, including scenario start, meaningful step progress, scenario result, and last-confirmed-progress evidence
- if a helper does not already enforce a tighter watchdog, `10s` is the maximum allowed no-progress interval before the run must self-abort, clean up, report the last confirmed progress point, and classify the stall
- long-running interactive commands must not hide behind only the shell/tool outer timeout; they must be supervised by a watchdog, monitor job, child process, or equivalent path that can abort and clean up blocked UIAutomation, app launch, screenshot, focus, source-write, or cleanup operations
- Codex should poll or surface helper progress during live validation instead of leaving the operator with a silent long-running command

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

- `Branch Readiness` -> `Workstream` only after branch base, branch class, authority record, branch objective, target end-state, expected seam families and risk classes, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam or initial seam sequence are explicit
- `Workstream` -> `Hardening` only after the approved Workstream seam sequence is complete, direct validation is green, User Test Summary obligations are current for user-facing changes, and no same-slice correctness gap remains
- `Hardening` -> `Live Validation` only after repo-side hardening proof is sufficient for interactive or manual closeout work
- `Live Validation` -> `PR Readiness` only after branch-local proof is sufficient for closeout, returned evidence has been digested into the authority record, and `User Test Summary Results Pending` is absent or cleared by a documented waiver
- `PR Readiness` -> `Release Readiness` only after merge-target canon completeness passes, the Governance Drift Audit passes, the next-workstream selection gate passes, branch creation remains deferred to `Branch Readiness`, and any release target/scope/artifact truth needed for release review is already available without file mutation
- `Release Readiness` stays restricted to analysis-only release target, scope, artifact, release-execution authorization, and release-state confirmation work; it does not transition into a docs-sync phase or a file-mutation phase

There is no default direct `Workstream` -> `PR Readiness` transition.
If Workstream appears complete, the next normal phase is `Hardening` unless an explicit authority-record waiver says otherwise.

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
- plan the whole branch at phase level before implementation begins

Allowed:

- source-of-truth audit
- branch-base validation
- branch-start canon sync
- workstream promotion, branch-record setup, or authority setup
- execution-boundary definition
- branch-level execution planning

Forbidden:

- implementation
- PR material preparation
- release packaging

Required evidence:

- updated `main` truth
- correct execution base
- explicit branch class
- explicit phase block in the authority record
- branch objective and target end-state
- expected seam families and risk classes
- validation contract and User Test Summary strategy
- expected Hardening, Live Validation, PR Readiness, and Release Readiness needs
- first Workstream seam or initial seam sequence

Exit:

- branch base is valid
- active workstream authority exists
- exact phase state is recorded
- branch-start canon is coherent
- execution boundary is explicit
- branch-level execution plan is explicit enough to enter Workstream without inventing the lane shape mid-execution

### Workstream

Purpose:

- execute the approved bounded implementation or bounded governance/docs work
- run normal repo-side regression validation inside that boundary
- use bounded multi-seam workflow as the primary model when an approved seam chain remains inside its governed boundary and validation stays green

Allowed:

- bounded code or docs changes
- direct verification inside the approved scope
- one active seam at a time within an approved multi-seam sequence
- incremental workstream evidence and User Test Summary updates when branch-local truth changes

Forbidden:

- silent scope expansion
- hidden hardening or closure claims
- PR or release packaging
- batching multiple seams without per-seam validation and continue-or-stop gates
- crossing risk class, subsystem family, or phase boundaries under a multi-seam prompt

Required evidence:

- approved execution boundary
- direct verification of the changed behavior or docs
- seam sequence when multiple seams may execute in one pass
- per-seam validation results and continue-or-stop decisions

Exit:

- approved scope is implemented
- direct verification is complete
- no unresolved same-slice correctness gaps remain
- Workstream evidence and User Test Summary obligations are current for user-facing changes

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
- required user-facing desktop shortcut validation is `PASS` or explicitly `WAIVED` before User Test Summary handoff; `User-Facing Shortcut Validation Pending` must not remain active
- returned evidence is digested into canon
- required User Test Summary results are `PASS` or explicitly `WAIVED`; `User Test Summary Results Pending` must not remain active
- no unresolved validation contradiction remains

### PR Readiness

Purpose:

- first determine whether the branch is package-ready for PR creation without leaving merged canon stale and with the next lane already locked
- then validate the created PR as the actual merge candidate before reporting PR Readiness green

Allowed:

- readiness review
- merge-target canon sync
- final drift checks
- next-workstream confirmation
- successor-branch absence verification
- Branch Readiness branch-creation deferral
- Governance Drift Audit
- PR material preparation
- PR creation
- PR state validation

Forbidden:

- implementation
- hardening
- release tagging
- skipping governance drift review
- reporting PR Readiness GREEN before PR creation and PR validation

Required evidence:

- branch-local proof complete
- required user-facing desktop shortcut validation digested, passing or explicitly waived, and no `User-Facing Shortcut Validation Pending` blocker
- required User Test Summary results digested, passing or explicitly waived, and no `User Test Summary Results Pending` blocker
- merge-target canon completeness gate passed
- next workstream selected, canon-defined, assigned valid record state, minimally scoped, and explicitly not branched yet
- successor branch creation deferred to `Branch Readiness`
- post-merge truth fully encoded before merge
- Governance Drift Audit completed
- docs sync complete and validator-aligned
- standardized `## Next Branch` response block and inclusion-only `## PR Creation Details` operator copy blocks prepared
- clean worktree with required branch truth durable in commit history
- GitHub PR created for the current head branch and intended base branch
- PR exists, is open, non-draft, conflict-free, and inspectable
- PR state matches merge-target canon
- unresolved Codex comments/issues and requested changes are absent or resolved
- approved non-backlog branches merge with historical or removed branch-authority truth rather than lingering as active branch owners on `main`
- no active seam
- no unresolved blocker that should have been repaired on the current branch before merge

Exit:

- PR exists and is validated as ready for merge review
- or returned to the failed earlier phase with explicit blockers

### Release Readiness

Purpose:

- determine whether merged or merge-ready truth is ready for release packaging

Allowed:

- release review
- release notes, tag, title, and release package information
- version or tag recommendations
- final release-candidate verification
- release-state confirmation immediately after release execution

Forbidden:

- implementation
- broad canon-sync mutation that should have been completed before PR green
- hidden fix work
- hidden next-lane planning
- branch-authority cleanup that should have been merge-safe in PR Readiness
- between-branch canon repair
- source, docs, canon, validator, helper, release-note, or handoff-file mutation

Required evidence:

- merged or legitimately merge-ready truth
- explicit `Release Target:`, `Release Floor:`, `Version Rationale:`, `Release Scope:`, and `Release Artifacts:` markers for release-bearing branches
- or explicit `Release Branch: No` only for preserved historical records
- release-context verification
- clean tracked-file state; any required file update must be routed back to `PR Readiness` before merge or to the next active branch's `Branch Readiness` after merge
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
- a release packaging branch may still enter `Branch Readiness` if its branch-class admission rules pass
- governance-only branches are not used; governance or canon repair must ride on the still-available prior branch or the next active branch's `Branch Readiness`

## Exception Path: Post-Release Canon Repair

Purpose:

- classify escaped canon drift after a release without turning Release Readiness into a mutation phase or using `main` as a work surface

Allowed:

- read-only drift analysis on `main`
- repair on the still-available prior branch when that branch remains the legal repair surface
- repair in the next active branch's `Branch Readiness` before implementation when the prior branch is unavailable

Forbidden:

- treating post-release canon repair as a normal part of the standard lifecycle
- using post-release repair instead of the merge-target canon completeness gate
- turning the repair path into a new implementation lane by accident
- opening a governance-only branch
- using Release Readiness as a broad docs-sync phase
- mutating `main`

Required evidence:

- updated `main`
- latest release truth
- explicit canon drift
- explicit reason the drift could not be prevented before merge or release
- explicit legal repair surface: prior branch or next active branch's `Branch Readiness`

Exit:

- canon aligned to released truth
