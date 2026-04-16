# Nexus Phase Governance

## Purpose

This document defines the governed execution phases used for Nexus Desktop AI work.

It exists so:

- workstream truth
- validation truth
- closeout truth
- prompt routing

all use the same phase names and the same control rules.

This is a cross-workstream governance layer.
It does not replace:

- `Docs/Main.md` as the routing index
- canonical workstream docs as feature and closure truth
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
- if the validation contract, timeout contract, or active seam changes materially during closeout recovery, the workstream doc must be updated before continuation is recommended

## Validation Authority Model

When multiple evidence layers exist, use this authority order unless a workstream explicitly documents a tighter requirement:

1. runtime markers
2. persisted source truth
3. UIAutomation and readback
4. optional UI observations such as help text, examples boxes, and transient labels

UI-only observations may be logged as notes, but they must not override stronger runtime and persisted-source proof unless the UI interaction itself is the thing being validated.

## Interactive Timeout Governance

Interactive closeout and hardening work must use tiered hard stops.

Default contract:

- preflight startup gate: `<= 60s`
- seam or control-acquisition gate: `10-25s`
- no-progress watchdog: `15-20s`
- normal scenario budget: `60-90s`
- exceptional scenario budget: `<= 120s`, only when explicitly declared in the workstream doc
- full interactive run hard cap: `<= 15 minutes`
- outer execution timeout: only slightly above the harness hard cap

Prohibited without explicit workstream-doc reconciliation:

- undocumented `300s+` scenario budgets
- undocumented `15m+` full-run caps
- silent timeout inflation during closeout

## Stop-Loss Rules

For governed closeout recovery:

- fix only one active seam at a time
- rerun the full gate immediately after that seam fix
- if a new seam appears, log it before selecting it as the next active seam
- stop after `2` seam fixes in one governed closeout pass
- stop after `90 minutes` of closeout recovery work and produce findings instead of continuing

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

- determine whether the branch is ready to become a merge candidate

Allowed:

- readiness review
- PR material preparation
- final drift checks

Forbidden:

- assuming readiness because the worktree is clean
- skipping active validation blockers

Required evidence:

- branch-local proof complete
- closeout truth current
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

- repair or align canon after a release when live merged truth requires it

Allowed:

- docs and canon repair tightly coupled to the released truth

Forbidden:

- turning post-release sync into a new implementation lane by accident

Required evidence:

- updated `main`
- latest release truth
- explicit canon drift

Exit:

- canon aligned to released truth
