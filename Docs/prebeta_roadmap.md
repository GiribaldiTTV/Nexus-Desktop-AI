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

This roadmap should usually be refreshed on the active implementation branch before PR, or as the first docs-only step on the next implementation branch after release, rather than being deferred into a standalone docs-only refresh branch by default.

## Canon Freshness Timing

For routine Nexus `pre-Beta` work:

- active-lane truth must be synced on the implementation branch before PR packaging
- release-dependent lifecycle closure should normally be carried on the next implementation branch as its first docs-only step
- standalone docs-only roadmap or drift-refresh branches are no longer the default post-release cleanup path
- if no safe next implementation branch can yet be chosen, Codex must call that out explicitly before requesting any exception path

This roadmap should therefore stay fresh in two normal windows only:

- on the active implementation branch before PR
- at the start of the next implementation branch after a release, when release-closure facts now need to be recorded

## Release-Debt Handling

If `main` already contains merged unreleased non-doc implementation work beyond the latest public prerelease, treat that as release debt.

While release debt exists:

- docs-only governance, rebaseline, or release-support lanes may still proceed when they are directly needed
- the current best next non-doc move should usually be release review, release prep, or an explicitly approved continuation of the same version-bearing milestone
- another unrelated non-doc implementation lane should not merge by default

## Current Near-Term Roadmap Horizon

This is the current best provisional sequencing horizon from live repo truth after the live `v1.2.5-prebeta` release.

The just-finished non-doc implementation lane is now:

- `feature/fb-025-boot-desktop-milestone-taxonomy-clarification`

That lane is now released and closed at `v1.2.5-prebeta`.

## Current Active Lane

### `feature/fb-034-recoverable-diagnostics`

- status: `active`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.6-prebeta`
- purpose: do one bounded recoverable-incident follow-through slice that makes the current Class 2/Class 3 boundary explicit for one high-signal incident class without widening diagnostics policy
- milestone target: keep repeated identical `launch_failed` for the same action as the only selected incident class, make the recoverable Class 2-to-Class 3 boundary explicit in renderer evidence, and preserve the existing local/manual reporting boundary without broad diagnostics UI work
- minimum merge-ready threshold: one incident class only; no launcher retry or escalation redesign; no blanket recoverable diagnostics popup behavior; no broad diagnostics UI redesign; no voice-path work required for the first slice; fatal launcher/runtime diagnostics path unchanged; manual reporting boundary unchanged; and narrow validation proves the selected class behaves as intended

This branch begins with the required canon-alignment step on the same implementation branch rather than through a separate standalone docs-only refresh branch.

## Recently Closed Or Superseded Lanes

These entries remain here only long enough to keep the post-`v1.2.5-prebeta` transition explicit.

### `feature/fb-025-boot-desktop-milestone-taxonomy-clarification`

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.5-prebeta`
- release state: `released`
- purpose: do one tiny boot and desktop milestone taxonomy clarification pass that improves cross-lane diagnostic readability while preserving separate ownership between `BOOT_MAIN|...` and `RENDERER_MAIN|...`
- milestone target: clarify the specific boot-to-desktop milestone naming shape so request-versus-visible transitions are easier to compare across boot and renderer evidence without broadening the logging contract
- minimum merge-ready threshold: keep boot and desktop milestone ownership separate; limit the change to naming and taxonomy clarity only; do not change launcher policy, raw verbosity, or shared logging-contract scope; do not change normal user-facing behavior; and prove the affected boot and desktop markers still emit correctly under current flows

### `feature/fb-033-startup-snapshot-harness-follow-through`

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.4-prebeta`
- release state: `released`
- purpose: finish the dev-only startup snapshot harness as intentional, opt-in debugging infrastructure around startup-state capture without changing normal user-facing startup behavior
- milestone target: stabilize the current env-gated startup snapshot path as bounded dev-only debugging infrastructure with a repeatable contained validation path, while keeping the helper harness-gated and out of normal product behavior
- minimum merge-ready threshold: the startup snapshot harness remains explicitly dev-only and opt-in; its owned trigger/env contract and output location are stable on-branch; it does not spill artifacts into live root logs or normal runtime state by default; it works against the current launcher/runtime contract on `main`; and narrow validation proves the intended startup capture path in both healthy and failure-oriented cases

### `feature/fb-028-history-state-relocation`

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.3-prebeta`
- release state: `released`
- purpose: relocate launcher-owned historical state out of the live root `logs` tree without changing historical-memory semantics or widening logs/reporting policy
- milestone target: move launcher-owned historical state out of the live root `logs` tree into a dedicated non-user-facing launcher-owned state root, with migration and clean fallback, without changing historical-memory semantics or widening logs/reporting policy
- minimum merge-ready threshold: launcher history resolves to a dedicated state root outside live root `logs`; successful migration no longer leaves the legacy root-log history file exposed; failure to migrate or write still degrades cleanly to the last non-historical behavior; contained history harness and direct consumers follow the relocated path contract; validation proves history writes no longer spill into live root `logs`; runtime logs, crash logs, and support-bundle locations remain unchanged

### `feature/fb-034-recoverable-diagnostics`

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.2-prebeta`
- release state: `released`
- purpose: first bounded recoverable diagnostics and reporting lane above the current Class 2/Class 4 boundary
- milestone target: the first bounded recoverable-operational-incident milestone while Nexus remains alive, using one explicit incident class and the existing local/manual reporting boundary
- minimum merge-ready threshold: keep first single `launch_failed` inline, preserve fatal launcher/runtime diagnostics ownership, and add one bounded recoverable path where repeated identical `launch_failed` for the same action prepares a local support bundle and issue draft once without widening into blanket diagnostics or reporting redesign

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

- the latest public prerelease is now `v1.2.5-prebeta`
- the `feature/fb-028-history-state-relocation` lane is now released and closed
- the `feature/fb-033-startup-snapshot-harness-follow-through` lane is now released and closed
- the `feature/fb-025-boot-desktop-milestone-taxonomy-clarification` lane is now released and closed
- the prior release debt between `v1.2.4-prebeta` and `main` is cleared
- no new implementation lane became active automatically just because the prior patch milestone released
- fresh next-lane analysis on that released baseline selected `feature/fb-034-recoverable-diagnostics` as the next bounded implementation lane

That does **not** mean every listed lane should automatically happen.
It does mean non-doc implementation lanes should be treated as version-bearing milestones rather than as merge-only background follow-through.
