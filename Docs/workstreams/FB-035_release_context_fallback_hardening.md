# FB-035 Release-Context Fallback Hardening

## ID And Title

- ID: `FB-035`
- Title: `Release-context fallback hardening`

## Record State

- `Closed`

## Status

- `Released (v1.2.7-prebeta)`

## Release Stage

- `pre-Beta`

## Target Version

- `v1.2.7-prebeta`

## Purpose / Why It Matters

Protect support-report release-context derivation so generated support bundles and issue drafts keep reporting the latest released public prerelease even when `.git` metadata is unavailable.

## Current Truth And Boundaries

- this lane shipped in `v1.2.7-prebeta`
- release-context ownership remains centralized in `desktop/orin_support_reporting.py`
- directly coupled validation remains centered in `dev/orin_recoverable_launch_failed_validation.py`
- roadmap fallback now derives released-canon truth instead of selecting the highest planned prerelease target
- the manual review and manual issue submission boundary remains intact
- this lane did not widen into broader diagnostics policy, upload behavior, launcher policy, or voice work

## Milestone Value Statement

If squashed to one milestone, this lane still reads as a worthwhile support-report hardening release because it prevents unreleased-baseline drift in generated support artifacts.

## Scope

- release-context fallback hardening only
- released-prerelease canon parsing for fallback truth
- directly coupled validation for `git`-present and `git`-unavailable report-artifact paths

## Non-Goals

- new incident classes
- reporting-policy changes
- upload-behavior changes
- diagnostics UI redesign
- launcher retry or escalation redesign
- voice-path work

## Stages / Executed Stages

1. identified that roadmap fallback could select an unreleased higher planned prerelease when `.git` metadata was unavailable
2. hardened the support-report fallback path so only released-canon truth can supply fallback prerelease context
3. validated both metadata-present and metadata-unavailable report-artifact paths
4. released the lane in `v1.2.7-prebeta`

## Same-Branch Follow-Through

Closed. No same-branch follow-through remains for this bounded milestone.

## Blockers / Holds / Stop Conditions

Closed. Reopen only through a new explicitly bounded lane if later evidence requires broader reporting or diagnostics work.

## Validation / Evidence Summary

Closure evidence includes:

- owner confirmation that release-context derivation remains centralized in `desktop/orin_support_reporting.py`
- directly coupled validator evidence proving both `git`-present and forced `git`-unavailable paths resolved to the then-current latest public prerelease truth rather than a higher planned prerelease
- preserved manual review and manual issue submission contract fields
- released branch truth closed at `v1.2.7-prebeta`

## User Test Summary

No separate User Test Summary artifact is required for this closed lane. The relevant validation remained inside the lane and its directly coupled validator evidence.

## Closure Summary

Released in `v1.2.7-prebeta`. The lane now prevents support-report fallback logic from choosing an unreleased planned prerelease when `.git` metadata is unavailable while preserving the existing manual reporting boundary.

## Deferred Forward

- broader reporting UX follow-through
- broader recoverable diagnostics or reporting-policy follow-through
- any new incident-class work

## Related References

- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/incident_patterns.md`
- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.2.8-prebeta.md`
