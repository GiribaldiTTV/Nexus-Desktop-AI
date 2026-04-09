# Pre-Beta Roadmap

## Purpose

This document is the canonical near-term planning interface for current Nexus `pre-Beta` sequencing.

Use it for:

- the current near-term roadmap horizon
- the current best next lane candidates
- provisional sequencing
- provisional version-impact planning
- roadmap refresh triggers
- roadmap entry lifecycle/status handling

This document is intentionally:

- provisional
- near-term
- subject to refresh after milestone merge, release, or meaningful baseline change

This document is **not**:

- a second backlog
- a release log
- a fixed branch promise sheet

## Authority And Boundaries

This roadmap is subordinate to:

- `docs/development_rules.md`
- `docs/codex_modes.md`
- `docs/closeout_guidance.md`
- `docs/orin_vision.md`
- `docs/feature_backlog.md`

That means:

- `development_rules.md` and `codex_modes.md` still own workflow, branch, and governance boundaries
- `closeout_guidance.md` still owns closeout and rebaseline cadence
- `orin_vision.md` still owns release-stage meaning for `pre-Beta`, `Beta`, and `Full`
- `feature_backlog.md` still owns detailed future-work item truth, scope, and backlog control

If this roadmap conflicts with those docs, those docs win.

## Version-Impact Labels

Use only these provisional labels in this roadmap:

- `no release`
- `candidate patch prerelease`
- `candidate minor prerelease`
- `not a release lane / rebaseline only`

These labels are planning guidance only.

They do not:

- assign fixed future version numbers
- guarantee that a listed branch will ship
- turn a candidate into an approved release

Actual release decisions still depend on live repo truth, milestone value, and later readiness review.

## Entry Lifecycle

Use only these statuses in this roadmap:

- `candidate`
- `active`
- `merged`
- `closed`
- `deferred`
- `superseded`

Handling rule:

- keep active near-term entries here while they remain useful for current sequencing
- move closed or superseded items out of the active near-term horizon once they stop helping next-lane planning
- keep detailed implementation truth in `docs/feature_backlog.md`, not here

## Lane Milestone Fields

For each `active` grouped lane, and for the current best next `candidate` when one is named here, include:

- `milestone target`
- `minimum merge-ready threshold`

These fields are still provisional planning guidance.

They do not guarantee that a lane will continue unchanged if live repo truth shifts or a blocker appears.

They do require Codex to judge PR-readiness against the lane milestone rather than against the first clean internal revision.

## Refresh Triggers

Refresh this roadmap when:

- a meaningful milestone merges to `main`
- a public prerelease is cut
- a docs-only rebaseline materially changes the planning baseline
- the current best next lane changes lifecycle state between `candidate`, `active`, `merged`, `closed`, `deferred`, or `superseded`
- `main` materially advances beyond the latest public release and this roadmap no longer matches live repo truth

This roadmap should usually be refreshed by one narrow docs-only governance or rebaseline pass rather than by ad hoc wording drift across multiple unrelated branches.

## Current Near-Term Roadmap Horizon

This is the current best provisional sequencing horizon from live repo truth after the merged post-`v1.2.0-prebeta` follow-through on `main`.

### 1. `feature/prebeta-roadmap-rebaseline`

- status: `merged`
- version impact: `no release`
- purpose: docs-only governance and planning reset so near-term sequencing and provisional version-impact planning have one canonical interface

### 2. `feature/fb-027-saved-action-usability`

- status: `active`
- version impact: `candidate patch prerelease`
- purpose: grouped FB-027 usability follow-through above the current shared-action, saved-action-source, and starter-bootstrap baseline
- milestone target: the first coherent saved-action usability milestone above the current starter-bootstrap baseline
- minimum merge-ready threshold: the current command surface can do more than create the starter file; it must also help the user reach or use that source in a practical bounded way without widening into Action Studio, live reload, or broader interaction redesign

### 3. `feature/prebeta-v1.2.1-rebaseline`

- status: `candidate`
- version impact: `not a release lane / rebaseline only`
- purpose: only if a prior lane becomes release-worthy, do a milestone closure and release-baseline sync pass without treating that branch as a separate public version by itself

### 4. `feature/fb-034-recoverable-diagnostics`

- status: `candidate`
- version impact: `candidate patch prerelease`
- purpose: first bounded recoverable diagnostics and reporting lane if later analysis confirms it is the right next subsystem milestone

## Current Reading

Current repo truth indicates:

- the latest public prerelease is still `v1.2.0-prebeta`
- `main` has moved ahead through several merged follow-through slices
- the next best move is still to prefer milestone-shaped grouped lanes over more micro-branches

That does **not** mean every listed lane should automatically happen, or that each lane implies a new public version.
