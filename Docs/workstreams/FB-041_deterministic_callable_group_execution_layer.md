# FB-041 Deterministic Callable-Group Execution Layer

## ID And Title

- ID: `FB-041`
- Title: `Deterministic callable-group execution layer`

## Record State

- `Closed`

## Status

- `Released (v1.3.1-prebeta)`

## Release Stage

- `pre-Beta`

## Target Version

- `v1.3.1-prebeta`

## Canonical Branch

- `No Active Branch`
- historical implementation branch:
  - `feature/fb-041-deterministic-callable-group-execution`
- release packaging branch:
  - `codex/fb-041-release-debt-packaging`

## Purpose / Why It Matters

Promote the first bounded callable-group follow-through execution layer above the released FB-036 authoring baseline.

This workstream exists so callable groups can move from exact invocation only into deterministic runtime follow-through without reopening FB-036 authoring foundations, widening into automation design, or overlapping the separate future lanes already tracked in FB-037 through FB-040.

## Current Release-Truth Note

- FB-041 is released in `v1.3.1-prebeta`
- the FB-041 release-debt blocker is cleared by the public prerelease
- this closed workstream record is historical lane truth, not active execution authority
- no next implementation branch is selected by this release record
- any future implementation lane must enter through strict `Branch Readiness` from updated `main`

## Current Branch Truth

- the latest public shared baseline is the released FB-027 interaction floor plus the released FB-036 authoring-and-callable-group milestone and the released FB-041 deterministic callable-group execution milestone in `v1.3.1-prebeta`
- exact group invocation still enters through the released chooser and confirm flow, but group follow-through now executes the full stored-order callable group after confirm
- deterministic callable-group execution now emits bounded runtime markers for:
  - group start
  - per-step start
  - per-step success or failure
  - terminal completion or failure
- dispatch now consumes immutable execution intent captured at confirm time rather than ambient overlay group state
- group failures now reuse the existing recoverable launch-failure classification pipeline with structured group-aware payloads
- single-action dispatch, confirm text, result text, and failure behavior remain unchanged except where the documented confirm/result group-only clarification exceptions apply

## Release Definition

The public prerelease for this lane is `v1.3.1-prebeta`.

That release means:

- saved callable groups are officially supported for full stored-order member execution after confirm instead of stopping at exact single-member invocation behavior
- group execution is officially supported as deterministic and stop-on-failure, with bounded runtime progression markers for group start, per-step progression, and terminal completion or failure
- group failures stay aligned to the existing recoverable launch-failure classification path rather than introducing a separate failure system
- group confirm and result copy accurately describe full stored-order group execution while single-action behavior remains unchanged

## Release Artifacts

- tag:
  - `v1.3.1-prebeta`
- high-level release notes:
  - deterministic callable-group execution is now supported after confirm
  - callable-group execution follows persisted stored order and stops on first failure
  - group failures reuse the existing recoverable launch-failure classification path with group-aware context
  - group confirm and result status text now accurately describe full stored-order group execution
  - single-action confirm, dispatch, result, and failure behavior remain unchanged
- supporting release artifacts:
  - `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.3.1-prebeta.md`
  - FB-041 workstream record converted to historical released-lane truth
  - existing FB-041 validator and interactive evidence references retained as release-supporting proof

## Release Closeout

- released in public prerelease `v1.3.1-prebeta`
- release-debt state cleared for FB-041
- backlog, roadmap, workstreams index, closeout index, and Nexus-era rebaseline now treat FB-041 as closed released truth
- no next implementation lane is selected by this closeout
- future work must enter through the strict branch-governance admission flow

## Governance Drift Audit

- Governance Drift Found: `Yes`
- Drift Type:
  - merge-target canon completeness failure
  - stale current-state claim ownership
  - stale prompt scaffolding and operator examples
- Why Current Canon Failed To Prevent It:
  - merged truth advanced without all release-facing canon surfaces being updated together
  - active prompt scaffolds still taught the older phase model
  - current-state claims still lived in guidance and sequencing layers that were not reconciled after merge
- Required Canon Changes:
  - adopt the strict six-phase governance model
  - add the repo-level admission gate and `No Active Branch` state
  - add the governance validator
  - strengthen current-state claim containment
  - update prompt scaffolds to the exact prompt contract
- Whether The Drift Blocks Merge: `No; the governance drift was resolved before release, and the FB-041 release-debt blocker is cleared by v1.3.1-prebeta`
- Whether User Confirmation Is Required: `No; this is historical release evidence for the completed governance pass`

## Scope

- deterministic linear execution only
- stored-order stepping only
- stop on first failure
- terminal success or failure propagation
- runtime markers for group start, per-step progression, and terminal completion or failure

## Explicit Non-Goals

- no UI changes
- no scheduling
- no branching
- no nested groups
- no parallel execution
- no retries
- no plugin or external trigger work
- no built-in catalog expansion

Exception:

- a single confirm-surface clarification seam is allowed to accurately reflect deterministic callable-group execution behavior
- this confirm-surface exception does not include result-surface changes or UI restructuring
- a single result status-text clarification seam is allowed to accurately reflect deterministic callable-group execution outcomes
- this result-surface exception is limited to status-text only and does not include result hint changes, timing changes, payload or model changes, or UI restructuring

## Reuse Baseline

- `Docs/workstreams/FB-036_saved_action_authoring.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`
- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.3.1-prebeta.md`
- `desktop/interaction_overlay_model.py`
- `desktop/shared_action_model.py`

## First Execution Boundary

- the active implementation seam starts at the execution dispatch layer after chooser or confirm resolution
- this lane does not start in UI, authoring, or group-definition storage
- the exact dispatch function must be located before any product-code patching begins

## Validation Contract

- prefer repo-side deterministic proof first
- required assertions:
  - member execution order matches persisted stored order exactly
  - step indices are monotonic and gap-free
  - execution halts on first failure
  - later members do not execute after failure
  - aggregate success or failure matches the executed steps
- required runtime markers:
  - group execution start
  - per-step start
  - per-step success or failure
  - group completion or failure
- no timeout inflation
- no validation-rule drift

## Executed Slices

- promoted the backlog identity into an active canonical workstream
- created the stable canonical workstream record
- revalidated the reserved branch against updated `main`
- added deterministic callable-group execution with stored-order stepping, stop-on-failure, and terminal propagation
- routed the post-confirm dispatch handoff through the deterministic group-execution helper when a callable-group confirm context is active
- replaced ambient group-state dispatch decisions with immutable execution intent captured at confirm time and consumed exactly once
- aligned group failure handling with the existing single-action recoverable failure classification and reporting path
- completed structured failure payload normalization so single and group paths are schema-compatible downstream
- added the confirm-surface clarification seam so group confirm copy accurately states that Enter runs the full stored-order group while the selected member remains inspection context
- added the result status-text clarification seam so group success and fallback failure text accurately reflect callable-group outcomes
- added result-name sanity checks proving result text uses execution intent group truth rather than mutable overlay state
- added branch-local interactive launched-process validation and screenshot audit coverage for:
  - real group success
  - real group failure
  - unchanged single-action confirm and result surfaces

## Validation Evidence

- repo-side deterministic validator:
  - `python dev/orin_callable_group_execution_validation.py`
  - latest pass confirms:
    - stored-order execution
    - gap-free step indices
    - stop-on-failure
    - no-later-member execution after failure
    - execution intent single-use behavior
    - confirm/result copy assertions
    - overlay mutation protection for group result naming
- FB-036 regression guard:
  - `python dev/orin_saved_action_authoring_validation.py`
- recoverable-failure regression guard:
  - `python dev/orin_recoverable_launch_failed_validation.py`
  - latest report:
    - `dev/logs/recoverable_launch_failed_validation/reports/RecoverableLaunchFailedValidationReport_20260418_094518.txt`
- exact-branch interactive launched-process closeout proof:
  - `dev/orin_callable_group_execution_interactive_validation.ps1`
  - latest report:
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/FB041CallableGroupInteractiveValidationReport_20260418_094333.txt`
  - latest manifest:
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/manifest.json`
  - latest launched-process UI captures:
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/group_success_confirm.png`
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/group_success_result.png`
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/group_failure_result.png`
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/single_action_confirm.png`
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/single_action_result.png`
- closeout-grade interactive proof now explicitly covers:
  - one real callable-group success pass
  - one real callable-group failure pass
  - live confirm copy audit
  - live result status-text audit
  - unchanged result hint audit
  - unchanged single-action confirm and result audit

## User Test Summary

- setup:
  - start the desktop runtime on the exact FB-041 branch truth
  - ensure the saved-actions source includes:
    - group `Workspace Tools`
    - group `Broken Workspace Tools`
    - single saved action `Open Notes Task`
- exact success invocation:
  - invoke `workspace tools`
  - when the chooser appears, select `Open Notes Task`
  - expected confirm text:
    - hint: `Review the selected member details below. Press Enter to run "Workspace Tools" group in stored order.`
    - footer: `Press Enter to run "Workspace Tools" group in stored order, or Esc to return.`
  - expected success result text:
    - `Group "Workspace Tools" executed in stored order.`
- exact failure invocation:
  - invoke `broken workspace tools`
  - when the chooser appears, select `Open Notes Task`
  - expected failure result text prefix:
    - `Group "Broken Workspace Tools" failed at step 1:`
- unchanged single-action control check:
  - invoke `notes task`
  - expected confirm text:
    - hint: `Review the resolved action origin and destination before execution.`
    - footer: `Press Enter to confirm or Esc to return.`
  - expected success result text:
    - `Launch request sent.`
- what must remain unchanged:
  - result hint text stays `Returning to passive desktop mode.`
  - no new panels, rows, or workflow steps appear
  - single-action behavior stays on the original non-group path
  - the selected group member remains inspection context only; execution still follows the full stored-order group
