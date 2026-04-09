# Pre-Beta Roadmap

## Purpose

This document is the canonical near-term planning interface for current Nexus `pre-Beta` sequencing.

Use it for:

- the current near-term roadmap horizon
- the current best next lane candidates
- provisional sequencing
- provisional release-floor and target-version planning
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

## Lane Types, Release Floors, And Release States

Use these lane types in this roadmap:

- `docs-only`
- `implementation`
- `rebaseline`

Use these release floors in this roadmap:

- `no release`
- `patch prerelease`
- `minor prerelease`

Use these release states when relevant:

- `active delta`
- `merged unreleased`
- `released`
- `closed`

These fields are planning guidance only.

They do not:

- assign fixed future version numbers
- guarantee that a listed branch will ship
- turn a release floor into an approved release by itself

Actual release decisions still depend on live repo truth, milestone value, and later readiness review.

Rules:

- `no release` should normally be limited to `docs-only` or docs-only `rebaseline` lanes
- non-doc `implementation` lanes should usually declare at least `patch prerelease`
- larger subsystem or capability shifts may justify `minor prerelease`
- if merged unreleased implementation work already exists on `main`, that should be treated as release debt rather than as normal background drift

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

- `lane type`
- `milestone target`
- `minimum merge-ready threshold`
- `release floor`
- `target version` for non-doc implementation lanes
- `release state` when merged implementation work already exists for that lane

These fields are still provisional planning guidance.

They do not guarantee that a lane will continue unchanged if live repo truth shifts or a blocker appears.

They do require Codex to judge PR-readiness against the lane milestone rather than against the first clean internal revision.

## Refresh Triggers

Refresh this roadmap when:

- a meaningful milestone merges to `main`
- a public prerelease is cut
- a docs-only rebaseline materially changes the planning baseline
- the current best next lane changes lifecycle state between `candidate`, `active`, `merged`, `closed`, `deferred`, or `superseded`
- the current release-debt posture changes
- `main` materially advances beyond the latest public release and this roadmap no longer matches live repo truth

This roadmap should usually be refreshed by one narrow docs-only governance or rebaseline pass rather than by ad hoc wording drift across multiple unrelated branches.

## Release-Debt Handling

If `main` already contains merged unreleased non-doc implementation work beyond the latest public prerelease, treat that as release debt.

While release debt exists:

- docs-only governance, rebaseline, or release-support lanes may still proceed when they are directly needed
- the current best next non-doc move should usually be release review, release prep, or an explicitly approved continuation of the same version-bearing milestone
- another unrelated non-doc implementation lane should not merge by default

## Current Near-Term Roadmap Horizon

This is the current best provisional sequencing horizon from live repo truth after the live `v1.2.1-prebeta` release.

### 1. `feature/fb-034-recoverable-diagnostics`

- status: `candidate`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.2-prebeta`
- purpose: first bounded recoverable diagnostics and reporting lane if later analysis confirms it is the right next subsystem milestone

## Recently Closed Or Superseded Lanes

These entries remain here only long enough to keep the post-`v1.2.1-prebeta` transition explicit.

### `feature/prebeta-roadmap-rebaseline`

- status: `merged`
- lane type: `docs-only`
- release floor: `no release`
- release state: `closed`
- purpose: docs-only governance and planning reset so near-term sequencing and provisional version-impact planning have one canonical interface

### `feature/fb-027-saved-action-usability`

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.1-prebeta`
- release state: `released`
- purpose: released FB-027 usability milestone above the current shared-action, saved-action-source, and starter-bootstrap baseline
- milestone target: the first coherent saved-action usability milestone above the current starter-bootstrap baseline
- minimum merge-ready threshold: the current command surface can do more than create the starter file; it must also help the user reach or use that source in a practical bounded way, and the resulting lane should be strong enough to justify the declared patch prerelease rather than another merge-only code delta

### `feature/prebeta-v1.2.1-rebaseline`

- status: `superseded`
- lane type: `rebaseline`
- release floor: `no release`
- purpose: direct release execution plus this roadmap refresh closed the `v1.2.1-prebeta` baseline drift without needing a separate rebaseline branch

## Current Reading

Current repo truth indicates:

- the latest public prerelease is now `v1.2.1-prebeta`
- `main` is aligned with that released commit
- the `feature/fb-027-saved-action-usability` lane is now released and closed
- the prior release debt between `v1.2.0-prebeta` and `main` is cleared
- broader sequencing may resume from clean post-release truth
- the current best next implementation candidate from canon is `feature/fb-034-recoverable-diagnostics`, but it remains provisional until the next lane is explicitly selected

That does **not** mean every listed lane should automatically happen.
It does mean non-doc implementation lanes should be treated as version-bearing milestones rather than as merge-only background follow-through.
