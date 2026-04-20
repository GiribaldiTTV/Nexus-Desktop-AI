# Incident Patterns

## Purpose

This document captures short reusable debugging and validation patterns extracted from closed workstreams.

It is a generalized knowledge layer, not a case-history diary.

Use:

- canonical workstream docs for the full story of a specific lane
- this document for reusable symptom-to-fix patterns
- the relevant canonical workstream doc first for branch-local reuse notes, artifact guidance, and seam history

Add material here only when the lesson has generalized beyond one lane.
Branch-local "what worked" notes should stay in the canonical workstream doc first and only be distilled here once the pattern is broad enough to help future branches outside that lane.

## Pattern: PR Readiness Green Must Require Durable Process Truth

- symptom:
  PR Readiness can appear green while required canon sync, post-merge state handling, or docs changes still exist only in the working tree
- layer:
  branch governance and merge-target canon
- root-cause pattern:
  validation proves branch behavior, but process blockers are not named strongly enough as pre-merge gates
- fix pattern:
  require PR Readiness to clear stale canon, post-merge-state handling, next-workstream selection with minimal scope and no branch created yet, dirty branch / durable commit state, and docs-sync / Governance Drift Audit blockers before reporting `PR READY: YES`
- validation pattern:
  run the normal branch governance validator plus the PR-readiness gate mode; the gate must fail while the worktree is dirty, while required post-merge truth is not encoded, or while the next workstream is undefined, unscoped, or already branched
- source references:
  - `Docs/phase_governance.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Released-Canon Fallback Must Not Use The Highest Planned Prerelease

- symptom:
  support bundles or issue drafts can report an unreleased baseline when `.git` metadata is unavailable
- layer:
  support reporting and release-context derivation
- root-cause pattern:
  fallback logic trusts sequencing or planning truth as if it were released-canon truth
- fix pattern:
  derive fallback release context from the latest released prerelease truth, not from the highest planned prerelease target
- validation pattern:
  prove both `git`-present and `git`-unavailable report-artifact paths resolve to the same released public prerelease truth
- source references:
  - `Docs/workstreams/FB-035_release_context_fallback_hardening.md`
  - `Docs/prebeta_roadmap.md`

## Pattern: Repeated-Identical Recoverable launch_failed Must Stay Bounded

- symptom:
  a repeated recoverable `launch_failed` class starts pulling diagnostics policy toward blanket popup or fatal-path behavior
- layer:
  recoverable diagnostics surface and failure-class handling
- root-cause pattern:
  a bounded high-signal recoverable class is treated as permission to widen every recoverable failure into the same diagnostics surface
- fix pattern:
  keep the selected incident class explicit, preserve the manual reporting boundary, and keep fatal launcher and runtime diagnostics behavior separate
- validation pattern:
  prove only the selected repeated-identical `launch_failed` class gets the intended recoverable handling while fatal-path behavior remains unchanged
- source references:
  - `Docs/workstreams/FB-034_recoverable_diagnostics.md`
  - `Docs/architecture.md`
