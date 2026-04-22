# Nexus Codex Modes

## Top Rule: Pre-PR Durability

**DO THIS ALWAYS before `PR Readiness`: when a bounded phase pass or durability seam changes source, docs, canon, validator, helper registry, workstream authority, or branch-truth files and validation is green, Codex must commit and push those changes on the active branch instead of stopping at a copy-ready, staged-only, or uncommitted state. This includes `Branch Readiness`, `Workstream`, `Hardening`, and `Live Validation`; a prompt-level request not to commit is not enough to stop durability. The only exceptions are a documented `Durability Waiver`, failed validation, a legally file-frozen phase such as `Release Readiness`, or a named Codex self-imposed blocker; when that self-imposed blocker is lifted, Codex must automatically commit and push.**

**Release Readiness is file-frozen: block ANY source, docs, canon, validator, helper registry, release-note, or handoff-file changes discovered or needed during `Release Readiness`. Do not edit, stage, commit, or push in `Release Readiness`; route the change back to `PR Readiness` before merge, or to the next active `Branch Readiness` after merge.**

## Purpose

This document defines the collaboration posture Codex should use while handling Nexus Desktop AI tasks.

It works with:

- `Docs/development_rules.md`
- `Docs/phase_governance.md`
- `Docs/Main.md`
- `Docs/orin_task_template.md`

If those sources conflict, live repo truth and the higher-order governance docs win.

## Why Two Modes Exist

Nexus work benefits from two different postures:

- one for deep truth-mapping, drift analysis, and next-move determination
- one for carrying an approved task through execution and verification

The modes should not be confused.
Analysis mode exists to understand the whole system first.
Workflow mode exists to execute approved work without silent scope drift.

## Required Startup Assessment

Before planning, patching, reviewing, or recommending the next move in either mode, Codex must run the startup contract from `Docs/Main.md`.

That startup assessment should explicitly answer:

- `Source-of-Truth`
- `Record State`
- `Branch Truth`
- `Canonical Workstream`
- `Reuse Baseline`
- `Next Safe Move`

This can stay brief, but it should happen before scope is narrowed for execution.

## Analysis Mode

### Goal

Map the real current state of the system before deciding what should happen next.

### When To Use It

Use Analysis mode when the user asks for:

- drift review
- post-release or post-merge review
- workstream planning
- readiness analysis
- sequencing analysis
- source-of-truth audit
- next-lane determination

### What Codex Should Do

In Analysis mode, Codex should:

- validate current repo truth first
- scan broadly enough to understand the whole affected system
- compare code, docs, branches, tags, and release facts where relevant
- identify factual drift, structural drift, and authority drift
- classify prior suggestions as carry-forward, defer, or discard
- determine the correct next workstream-level move

### Required Analysis Depth

Analysis mode should reason at:

- system level
- lane level
- workstream level
- document-ownership level

Do not narrow to the first apparent slice before full drift and dependency mapping is complete.

### What Codex Must Not Do

In Analysis mode, Codex must not:

- default into implementation
- assume PR, merge, release, or closure is the next move
- compress the task into the smallest possible pass before understanding the system
- treat local unmerged overlays as merged truth

### Expected Outputs

Analysis mode should usually return:

- validated current truth
- key drift findings
- structural assessment
- sequencing options
- one recommended next workstream move

## Workflow Mode

### Goal

Execute an approved task faithfully, verify it, and keep the resulting truth coherent.

### When To Use It

Use Workflow mode when the user has already approved:

- a docs-only pass
- a bounded patch
- a canon sync
- a workstream closure pass
- another clearly bounded execution task

### What Codex Should Do

In Workflow mode, Codex should:

- validate live repo truth before editing
- stay inside the approved execution boundary
- make the required changes
- verify the changed behavior or changed docs
- report any drift or remaining gaps honestly
- when the approved Workstream boundary contains a coherent same-risk seam chain, use bounded multi-seam workflow as the primary model while executing one active seam at a time
- when the approved boundary is continuous validation inside the current workstream, keep iterating until the full gate is green or a hard stop is reached

### What Codex Must Not Do

In Workflow mode, Codex must not:

- silently widen scope
- silently start a new workstream
- silently create PR, merge, release, or closure output without current-truth justification
- treat a clean first slice as automatic branch readiness

### Expected Outputs

Workflow mode should usually return:

- changes applied
- validation performed
- a distinct summary of validator results
- a distinct summary of synthetic or headless validation results and the supporting validation artifacts created or used
- a distinct summary of interactive OS-level execution results when that path is feasible
- the existing helper, harness, or shared support reused for interactive validation, or the explicit reason a temporary probe or new helper was necessary
- session cleanup performed and explicitly verified, including what was closed, stopped, restored, or deleted after the pass
- any remaining simulated-only findings or reasoning-only gaps that still matter
- deeper branch-local validation or hardening findings when the slice changes runtime or user-visible behavior
- any timeout or stall conditions encountered during validation, including the last confirmed meaningful progress point and whether the run aborted cleanly
- whether closeout-grade proof came from the helper's documented default budget profile or only from exploratory overrides
- a detailed `## User Test Summary` manual checklist when the slice changes user-visible behavior, runtime interaction, UX flow, prompts, startup behavior, voice behavior, or another operator-facing path
- the updated canonical repo-level `UTS` artifact when the active workstream owns one and the slice makes that artifact relevant
- the exported or refreshed desktop `User Test Summary.txt` copy when the slice is a relevant desktop user-facing path, or an explicit explanation of why that export was skipped
- for relevant desktop user-facing Live Validation, the `User-Facing Shortcut Live Validation Gate` / `desktop-shortcut` result with `User-Facing Shortcut Path:` and `User-Facing Shortcut Validation:` recorded before User Test Summary handoff
- when the user-facing shortcut result is outstanding, the explicit blocker `User-Facing Shortcut Validation Pending`; helper-only, synthetic, harness, or direct-runtime evidence must not be reported as final green while this blocker remains
- when returned User Test Summary results are still outstanding, the explicit blocker output: `Automated validators and live helper evidence: GREEN.`, `User Test Summary Results: PENDING.`, and `Final phase advancement is BLOCKED until the filled User Test Summary is submitted and digested.`
- when meaningful desktop UI changed and closeout posture matters, a distinct summary of the live launched-process UI audit results and evidence
- an explicit statement under `## User Test Summary` when no meaningful manual test exists and why
- if `User Test Summary Results: WAIVED` is used, the response-level `## User Test Summary` section and the canonical workstream `## User Test Summary` artifact must include `User Test Summary Waiver Reason:`
- if `User-Facing Shortcut Validation: WAIVED` is used, the response-level `## User Test Summary` section and the canonical workstream `## User Test Summary` artifact must include `User-Facing Shortcut Waiver Reason:`
- remaining drift or known gaps
- whether the approved phase is complete

Pre-PR Durability Rule:

- before `PR Readiness`, when a bounded phase pass or durability seam changes source, docs, canon, validator, helper registry, workstream authority, or branch-truth files and validation is green, Codex must commit and push those changes on the active branch instead of stopping at a copy-ready, staged-only, or uncommitted state
- this applies through `Branch Readiness`, `Workstream`, `Hardening`, and `Live Validation`
- a prompt-level request to stop before commit/push is not a durability exception; only a documented `Durability Waiver`, failed validation, legally file-frozen `Release Readiness`, or a named Codex self-imposed blocker may stop commit/push
- if Codex names a self-imposed blocker, it must name the lift condition; once lifted, Codex must automatically commit and push without requiring a second durability prompt
- if validation fails, do not commit and push; report the blocker and keep the branch in the current phase until the blocker is lifted
- `PR Readiness` still performs the final dirty-branch and durable-truth gate before PR creation

When the approved phase is `PR Readiness`, the output must also explicitly include:

- confirmation that the merge-target canon completeness gate passed
- confirmation that the Governance Drift Audit ran
- whether governance drift was found
- confirmation that stale-canon, post-merge-state, next-workstream, dirty-branch, docs-sync/drift-audit, and `User Test Summary Results Pending` blockers are clear
- confirmation that `PR Readiness Scope Missed`, `Between-Branch Canon Repair Attempt`, and `Next Branch Created Too Early` are clear
- confirmation that `PR Creation Pending`, `PR Validation Pending`, and `PR State Unknown` are clear before reporting `PR Readiness GREEN`
- confirmation that `PR package ready` is not being collapsed into `PR Readiness GREEN`
- confirmation that no PR-owned docs or canon work is being deferred to Release Readiness, updated `main`, or a governance-only branch
- confirmation that `main` remains protected and that no Codex file mutation, staging, commit, generation, refresh, or repair work is being performed on `main`
- confirmation that branch truth is committed and durable, not only present in the working tree
- confirmation that the normal governance validator and the PR-readiness gate mode passed
- for the selected next workstream:
  - the selected next workstream identity
  - the next workstream `Record State`
  - the minimal scope recorded in canon
  - confirmation that backlog includes `Next Workstream: Selected` and `Minimal Scope:` and roadmap includes `## Selected Next Workstream`
  - confirmation that no branch exists yet for that next workstream
  - confirmation that successor branch creation is deferred to `Branch Readiness` after merge and updated-`main` revalidation
- when post-merge truth will resolve to `No Active Branch` because `Release Debt` or another repo-level admission blocker remains open:
  - repo state `No Active Branch`
  - the blocking admission item
  - `Merged-Unreleased Release-Debt Owner:`
  - `Release Target:`
  - `Release Floor:`
  - `Version Rationale:`
  - `Release Scope:`
  - `Release Artifacts:`
  - `Post-Release Truth:`
  - confirmation that the release target is semantically correct from the latest public prerelease and declared release floor
  - confirmation that branch creation remains deferred and no next implementation branch may execute by inertia
- a required `## Next Branch` section with this exact field shape:

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

- when PR Readiness is package-ready or `PR package ready`, a copy-ready markdown PR package with this exact section shape:

```markdown
## PR Creation Details
### Title
### Base / Head
### Summary
### Validation
### Governance / Canon
### Post-Merge Truth
### Next Branch
### Not Included
```

The `Next Branch` section must separate the next legal branch type/name from the selected next implementation workstream branch.
If release debt, updated-`main` revalidation, or another admission gate blocks branch creation, `May Create Now: NO` is required with the reason.
The `PR Creation Details` block is preparation material only; it must not imply PR creation, merge execution, release execution, next-branch creation, or PR Readiness GREEN has occurred.
PR Readiness GREEN requires the PR to exist, be open, be non-draft, have no conflicts, match merge-target canon, and have no unresolved Codex comments/issues or requested changes.

When the approved phase is `Release Readiness`, the output must also explicitly include:

- whether the branch is release-bearing
- confirmation that `Release Target Undefined` is clear
- for release-bearing branches:
  - `Release Target:`
  - `Release Floor:`
  - `Version Rationale:`
  - `Release Scope:`
  - `Release Artifacts:`
  - confirmation that marker presence and semantic target correctness both pass
- for explicitly non-release branches:
  - `Release Branch: No`
  - confirmation that this is only a historical context, not a new governance-only branch or a direct-main repair path
- confirmation that the non-release waiver is not being used for an `implementation` or `release packaging` branch
- confirmation that `Release Debt`, post-merge truth, validation, and successor branch deferral remain governed by their normal blockers
- confirmation that Release Readiness is not being used as a docs-sync or branch-authority cleanup phase
- confirmation that Release Readiness is analysis-only for repository files and that no source, docs, canon, validator, helper, release-note, or handoff files were edited, staged, committed, generated, or refreshed
- if any file change is needed, classification as `Release Readiness File Mutation Attempt`, then return to `PR Readiness` before merge or defer to the next active branch's `Branch Readiness` after merge instead of patching inside Release Readiness

Do not report cleanup as complete unless the pass has explicitly checked for leftover apps, windows, dialogs, helper processes, probe files, or other temporary artifacts it created or opened.

Do not report an interactive validation pass as complete or trustworthy if it exceeded its time budgets or sat stalled without a clean abort path.

Do not create a new live-validation script by default.
For Live Validation, Codex should reuse existing helpers first, then parameterize or extend them, then extract shared support if several helpers need the same watchdog or cleanup behavior.
Temporary one-off probes are allowed only as ignored exploratory artifacts and must be deleted or promoted into documented reusable tooling before closeout-grade proof is claimed.
Durable root `dev/` validators, live-validation scripts, audit helpers, harnesses, and shared helper modules must also be checked against `Docs/validation_helper_registry.md`.
If a new helper is kept, Codex must report its standardized name, `Helper Status:`, owner, reuse decision, and `Consolidation Target` when it is `Workstream-scoped`.
Workstream-scoped seam helpers are bridge tooling, not the default release naming model, and must be consolidated, promoted, or explicitly justified before PR Readiness.
Any `Temporary probe` must stay ignored and be deleted or promoted before closeout-grade proof.

## Workstream And Branch Governance

### Grouped Workstreams

During `pre-Beta`, grouped workstreams are allowed when they remain coherent by subsystem and end-state.

That means:

- one branch may host multiple validated slices for one milestone
- grouped workstreams should not become grab-bags of unrelated ideas
- lane evaluation should stay milestone-driven rather than slice-driven

### Bounded Multi-Seam Workflow

For coherent Workstream implementation, bounded multi-seam workflow is the primary execution model.

That means:

- Branch Readiness should plan the branch objective, target end-state, expected seam families, risk classes, validation contract, User Test Summary strategy, later-phase needs, and first seam sequence
- Workstream may execute multiple planned seams in one pass only when they share the same workstream, phase, branch class, risk class, and subsystem family or tightly coupled chain
- each seam is still analyzed, bounded, implemented, validated, recorded, and judged before the next seam starts
- the output must report the per-seam validation result and `continue` or `stop` decision
- a risk-class change, validation failure, scope drift, governance drift, unresolved manual-validation blocker, or branch-truth contradiction stops the workflow

Single-seam fallback is required for bug fixes, hotfixes, unclear or high-risk seams, cross-subsystem work, settings/protocol/launcher/UI-model changes, or any pass where validation cannot support safe continuation.

Completing Workstream seams does not make the branch PR-ready by itself.
The normal next legal phase is `Hardening`, then `Live Validation`, then `PR Readiness`.

### Milestone Gate

Before treating a non-doc implementation branch as ready, Codex should be able to explain:

- the lane milestone target
- the minimum merge-ready threshold
- the milestone value statement
- the same-branch follow-through that still belongs inside the lane

### Worthwhile Milestone Gate

For a non-doc implementation branch, Codex should not recommend readiness until:

- the threshold is reached
- the branch is still worthwhile if squashed today
- the remaining obviously coupled slices are no longer required

### Release-Debt Gate

If `main` already contains merged unreleased non-doc implementation work beyond the latest public prerelease, treat that as release debt.

While release debt exists, the default next move is usually:

- release review
- release prep
- directly needed docs support

not another unrelated implementation lane.

That default blocks the next implementation lane by default.
It does not authorize a governance-only branch.
Release packaging may begin only when `Docs/phase_governance.md` says that branch class may begin from `No Active Branch`.

If release debt or another repo-level admission blocker means no next implementation branch may legally begin execution, report repo state as `No Active Branch` instead of inventing a next implementation phase.
If repo truth is a steady-state `No Active Branch`, say so explicitly instead of pretending a new implementation branch should open automatically.

### Fresh Branch Start After A Closed Workstream

After a workstream is merged and closed, the next implementation workstream should execute from updated `main` on a fresh branch.

During `PR Readiness`, the next workstream must be selected, canon-defined, minimally scoped, and explicitly not branched yet.

That successor branch is created only during `Branch Readiness` after the current branch merges and updated `main` is revalidated.

If post-merge truth will resolve to `No Active Branch` because `Release Debt` or another repo-level admission blocker remains open, successor branch creation remains deferred; next-workstream selection is still required unless the user explicitly approves a no-next-workstream steady-state outcome in canon.

If a branch is stale, merged, or identical to `main`, call it out explicitly and stop using it as the base for next-lane planning.

### Post-Release Canon Repair

Release-dependent truth must be anticipated before PR green.

When release-dependent truth changes:

- carry the canon sync on the active lane when that lane is still open
- require merge-target canon completeness before PR so merged `main` does not become stale in the first place
- do not use Release Readiness as a docs-sync phase
- do not use Release Readiness as a file-mutation phase; release package information may be generated as response text only
- do not open a governance-only branch or between-branch repair window
- if a PR Readiness miss escapes after merge, block the next active branch in `Branch Readiness` and repair the miss before implementation begins
- do not use direct-main emergency repair; `main` is protected for Codex work and repair must ride the still-available prior branch or the next active branch's `Branch Readiness`

## Shared Rules Across Both Modes

- analyze before changing anything
- anchor phase-sensitive work to the current phase named in `Docs/phase_governance.md`
- do not infer a later phase from user intent alone
- verify exact behavior or doc alignment before editing
- preserve architecture boundaries
- call out source-of-truth conflicts explicitly
- backlog owns identity
- roadmap owns sequencing
- workstream docs own promoted-work feature-state, branch-local evidence, active seam references, artifact history, branch-local reuse notes, and closure history
- `Docs/phase_governance.md` owns repo-wide phase, proof, timeout, seam, stop-loss, validation-helper, and desktop UI audit rules
- `Docs/validation_helper_registry.md` owns durable helper naming, helper status, registry, and consolidation expectations
- User Test Summary belongs to workstream-owned validation
- incident patterns are generalized knowledge, not case history
- governance and canon updates should ride on the active current branch when they are directly required to keep that branch truthful, executable, phase-correct, readiness-correct, validation-correct, closeout-correct, or release-correct
- governance-only branches are not used for new Nexus work; tightly coupled governance repair rides on the active branch, and escaped PR misses block the next active branch's `Branch Readiness`
- active-branch governance updates must not weaken validation, stop conditions, phase authority, branch-class authority, or scope control
- `main` is protected for Codex work; Codex may read `main` for truth validation, but any tracked file mutation, staging, commit, generation, refresh, or direct repair on `main` is a `Main Write Attempt`
- There is no emergency direct-main repair path for Codex.

For desktop workstreams, response-level `## User Test Summary` output and the canonical repo-level `UTS` artifact are related but not interchangeable:

- the response section is the current handoff copy
- the workstream-owned repo artifact is the exact `## User Test Summary` section, not `## User Test Summary Strategy`, unless the workstream explicitly declares another repo path
- the desktop `User Test Summary.txt` file is the required user-facing exported copy when relevant, but it is not the default canonical repo record

If a required User Test Summary handoff is outstanding, `User Test Summary Results Pending` is a hard blocker. Codex must not report final phase green or PR-ready while the filled results are missing; it must digest submitted results, update the authority record, reevaluate blockers, and route backward to `Workstream` or `Hardening` if the results expose a mismatch, regression, ambiguity, cleanup issue, or scope drift.

For relevant desktop user-facing workstreams, `User-Facing Shortcut Validation Pending` is a hard blocker before User Test Summary handoff.
Codex may use validators, live helpers, harnesses, or direct runtime launches for scenario coverage, but Live Validation closeout must also run the declared user-facing desktop shortcut or equivalent entrypoint and record `User-Facing Shortcut Path:` plus `User-Facing Shortcut Validation: PASS`, `FAIL`, `PENDING`, or `WAIVED`.
If that shortcut gate fails or remains pending, do not report final green; route back to `Workstream` or `Hardening` as appropriate.

When manual validation is relevant, `## User Test Summary` must be a real checklist rather than a recap.

It should include:

- setup or prerequisites
- exact user actions
- expected visible behavior
- failure signs to watch for
- branch-specific or slice-specific validation focus

For runtime or user-visible implementation slices, green validators alone do not authorize automatic continuation.

When a relevant desktop or runtime path can be launched and exercised through a real desktop session in the current environment, synthetic or headless validation does not authorize continuation on its own either.

Codex must also:

- run a deeper branch-local hardening pass against the implemented path
- add or create the smallest reliable validation infrastructure when meaningful blind spots remain
- preserve an evidence trail of the validators, harnesses, helper scripts, fixtures, runtime logs, traces, screenshots, or other validation artifacts actually used
- clean up test-session side effects such as temporary files, launched apps, helper processes, probe documents, or altered local state unless there is an intentional reason to preserve them
- enforce visible progress and a no-progress supervisor for live validation; if no tighter helper-specific watchdog is active, `10s` without meaningful progress must stop the run and report the last confirmed progress point
- use synthetic or headless validators and harnesses as supporting proof rather than the final gate when a real desktop session is feasible
- launch and exercise the real desktop or runtime path through an interactive OS-level session when feasible
- explicitly distinguish validator results, synthetic or headless validation results, simulated reasoning, interactive OS-level execution results, and manual user-test handoff
- make an explicit next-step call between continue, harden, or corrective fix

When meaningful desktop UI changed, Codex should also:

- treat the live launched-process UI audit as a post-green closeout check rather than a per-seam screenshot requirement
- preserve the audit manifest and key captured windows in the final evidence package when closeout or readiness is being claimed
- when the user wants those screenshots to render inside the Codex client, preserve the original files on disk but default the in-chat preview path to one small inline PNG `data:` image at a time instead of local-path Markdown embeds

If that interactive path is not feasible, Codex must explain why, use the strongest available non-interactive evidence, and state that the continuation judgment is limited by the missing interactive validation.

## Phase Anchoring

Modes define collaboration posture.
Phases define the current governed lifecycle state.

For phase-sensitive work, prompts and execution records should explicitly state:

- `Mode: <mode name>`
- `Phase: <exact phase name>`
- `Workstream: <workstream id or authority record>`
- `Branch: <branch name or No Active Branch>`

When a branch is in governed closeout recovery, prompts should also state:

- `Branch Class: <branch class>`
- `Current active seam: <seam name>`
- `Validation Contract: <summary or authority reference>`
- `Timeout Contract: <summary or authority reference>`

If `Phase` is missing or is not one of the exact canonical phase names from `Docs/phase_governance.md`, execution must stop at truth-validation or analysis.

## Live-State Readiness Sanity Check

Before generating any readiness, PR, merge, or release recommendation, validate:

- current branch truth
- branch merge state
- tag or release state
- dirty worktree risk
- whether the prompt framing is stale

If the framing is stale, report the real state instead of producing a hypothetical package.

## Prompt Hygiene

When a canonical workstream or rebaseline doc exists, prompts should prefer that canonical doc over a stack of superseded slice docs.

This does not mean shrinking analysis depth.
It means reducing duplicated prompt inputs once authority is clear.

## Practical Rule Of Thumb

If the user is asking:

- what is true now
- what drift exists
- what should happen next
- whether the current branch is still the right base

start in Analysis mode.

If the user is asking:

- execute this approved docs-only phase
- implement this approved patch
- carry this approved workstream closure or canon sync

use Workflow mode.
