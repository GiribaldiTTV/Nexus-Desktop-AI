# FB-027 Interaction System Baseline

## ID And Title

- ID: `FB-027`
- Title: `Interaction system baseline and shared action model`

## Record State

- `Closed`

## Status

- `Released (v1.2.8-prebeta)`

## Release Stage

- `pre-Beta`

## Target Version

- `v1.2.8-prebeta`

## Purpose / Why It Matters

Define the current typed-first interaction system as an explicit baseline contract and use that locked baseline to deliver the first bounded FB-027 capability milestone.

This workstream exists so future interaction work can extend a defended baseline instead of silently rewriting one.

## Current Truth And Boundaries

- the current shipped interaction surface is the typed desktop command overlay
- the current open hotkeys are `Ctrl+Alt+Home` and `Ctrl+Alt+1`
- the current shutdown hotkeys are `Ctrl+Alt+End` and `Ctrl+Alt+2`
- the current overlay flow is bounded to `entry` -> `choose` -> `confirm` -> `result`
- built-in actions and saved actions resolve through one shared action catalog
- the current saved-action seam lives at `%LOCALAPPDATA%/Nexus Desktop AI/saved_actions.json`
- current saved-action target kinds are `app`, `folder`, `file`, and `url`
- current repo truth does not yet include shipped voice invocation, Action Studio authoring UI, routines, profiles, or broader natural-language resolution
- this workstream locked the typed-first baseline and released the first-class URL saved-action target milestone through the existing shared action model

## Milestone Value Statement

If squashed to one milestone, this lane is still worthwhile because it turns the current interaction surface into an explicit contract and then proves that the first bounded capability expansion can land without changing resolution rules, state-machine boundaries, or input-capture behavior.

## Scope

- formalize the current typed-first interaction contract
- define the explicit interaction invariants that future work must defend
- identify which behaviors are baseline guarantees versus implementation details
- define the validator surfaces that must exist before capability expansion proceeds
- implement first-class URL target support for saved actions through the existing shared action model
- extend validator coverage so URL targets are defended as part of the locked baseline
- record directly related deferred follow-through that should remain out of scope for this pass

## Non-Goals

- capability expansion beyond bounded first-class URL target support
- saved-action authoring UX
- voice invocation
- Action Studio
- routines or profiles as shipped features
- fuzzy or semantic intent resolution
- runtime hotkey or shutdown-behavior changes in this pass
- broader diagnostics-policy changes

## Interaction Contract

### Invocation Contract

Guaranteed now:

- the command overlay opens through `Ctrl+Alt+Home` and `Ctrl+Alt+1`
- shutdown remains available through `Ctrl+Alt+End` and `Ctrl+Alt+2`
- opening from the supported overlay hotkeys permits immediate typed interaction without requiring an initial click

Not guaranteed now:

- custom hotkeys
- alternative invocation surfaces
- voice invocation
- shutdown confirmation prompts
- permanent retention of the numeric overlay or shutdown hotkeys through Beta

Must not regress:

- supported overlay hotkeys must continue to open the command surface reliably until an explicitly approved future milestone changes them
- supported shutdown hotkeys must remain predictable until an explicitly approved future milestone changes that path
- initial typing must not leak into the previously focused underlay target

### Overlay State Machine Contract

Guaranteed now:

- the visible interaction flow is bounded to `entry`, `choose`, `confirm`, and `result`
- one exact resolved match moves from `entry` to `confirm`
- ambiguous resolved matches move from `entry` to `choose`
- confirmed execution transitions to `result`
- `Esc` backs out from `choose` or `confirm` to `entry`

Not guaranteed now:

- extra intermediate review phases
- richer multi-step workflows
- alternate execution paths that bypass confirmation

Must not regress:

- the overlay must stay bounded and understandable
- execution must not skip the visible confirmation step
- cancel/back-out behavior must continue to return the user to a clean `entry` state

### Resolution Contract

Guaranteed now:

- command resolution is exact normalized matching against action titles and aliases
- one match yields a confirmable pending action
- multiple matches yield a visible ambiguous-choice state
- zero matches yield a bounded `not_found` state instead of hidden guessing

Not guaranteed now:

- fuzzy matching
- semantic inference
- routines, profiles, or other higher-order command abstractions
- broader natural-language understanding beyond the current normalized title-and-alias model

Must not regress:

- the interaction surface must resolve through one inspectable catalog
- ambiguous outcomes must remain explicit rather than silently choosing a guessed action
- `not_found` must remain bounded and visible

### Saved-Action Contract

Guaranteed now:

- saved actions are sourced from `%LOCALAPPDATA%/Nexus Desktop AI/saved_actions.json`
- built-in actions and saved actions share one effective catalog shape
- supported saved-action target kinds are currently `app`, `folder`, `file`, and `url`
- valid saved-action URL targets open through the existing system-handler launch path
- missing, unreadable, invalid, or colliding saved-action sources fall back to built-ins only

Not guaranteed now:

- a saved-action authoring UI
- partial salvage of malformed saved-action files
- richer target kinds beyond `url`
- routine or profile schemas

Must not regress:

- a bad saved-action source must not break the command overlay
- built-in actions must remain available even when the saved-action source is invalid
- collision handling must stay bounded and predictable
- URL targets must not bypass the shared catalog, confirmation path, or bounded result flow

### Input Capture / Focus Ownership Contract

Guaranteed now:

- fallback global capture owns text, `Enter`, `Esc`, and backspace while the overlay is in no-click entry mode and true local ownership is not yet established
- true manual local focus transfers ownership to the local input field
- outside click suspends no-click fallback capture instead of mirroring typing into the underlay and overlay at the same time
- choose and confirm paths preserve human-delay capture behavior when local focus has not yet been re-established

Not guaranteed now:

- the exact timer values used for launch grace or capture rearm
- any specific renderer timing beyond the behavioral contract above

Must not regress:

- no-click open must remain reliable
- local manual focus takeover must stand fallback capture down
- outside click must keep the overlay from silently mirroring input
- human-delay choose and confirm behavior must remain usable

### Result / Cleanup Contract

Guaranteed now:

- result display clears stale input text, last request text, pending action, and pending ambiguous-match state immediately
- close-and-reopen after success, failure, timeout close, or manual close returns to a clean baseline
- the result state remains bounded and transient rather than becoming a second execution phase

Not guaranteed now:

- exact result copy
- exact result timeout duration
- exact visual layout

Must not regress:

- stale request or confirmation metadata must not survive into the next reopen cycle
- result closure must not leave the command surface in a half-armed state

### Failure / Non-Success Boundary

Guaranteed now:

- `not_found`, `ambiguous`, and launch-failed paths remain bounded inside the current interaction surface
- launch-failed handling preserves the existing manual-reporting boundary
- interaction work does not widen into new diagnostics policy automatically

Not guaranteed now:

- broader recoverable-diagnostics expansion
- automatic reporting
- a richer non-success UX beyond the current bounded result path

Must not regress:

- interaction work must not silently widen reporting, diagnostics, or escalation behavior
- non-success states must remain explicit and bounded

## Invariants

### Behavioral Invariants

- opening the overlay from a supported hotkey must permit immediate typed interaction without an initial click
- `Enter` must never execute a command before the user reaches and accepts the confirm state
- ambiguous requests must require explicit user choice
- `Esc` in `choose` or `confirm` must back out to `entry`
- missing or invalid saved-action sources must degrade to the built-in baseline rather than to a broken overlay

### State Invariants

- `hidden` means no visible overlay state and no pending interaction state
- `entry` means editable request-building state
- `choose` means an ambiguous bounded match set exists
- `confirm` means exactly one pending action is active
- `result` means transient execution state has already been cleared

### Transition Invariants

- `entry` -> `confirm` only on exactly one resolved action
- `entry` -> `choose` only on more than one resolved action
- `choose` -> `confirm` only through explicit user selection
- `choose` -> `entry` and `confirm` -> `entry` must clear stale pending metadata
- `result` -> reopen must restore a clean `entry` baseline

### Fallback Invariants

- fallback capture must not remain active after true local manual focus ownership is established
- fallback capture must not keep mirroring typing after outside-click suspension
- expired capture must stand down instead of intercepting unrelated input
- saved-action fallback must never remove built-ins from the effective catalog
- interaction follow-through must not widen the bounded non-success and reporting contract accidentally

## Validation Coverage And Required Defenses

### Existing Validation Coverage

The current baseline is now defended by:

- `dev/orin_overlay_input_capture_helper.py`
- `dev/orin_shared_action_baseline_validation.py`
- `dev/orin_saved_action_source_validation.py`
- `dev/orin_interaction_baseline_validation.py`

Together, these surfaces now exercise:

- first-open immediate typing
- no-click entry behavior
- local-focus takeover
- outside-click suspension
- choose and confirm human-delay capture behavior
- cancel/retry state cleanup
- result cleanup and clean reopen after success, failure, timeout close, and manual close
- one choose-confirm-execute path
- hotkey launch-grace behavior
- shutdown-hotkey continuity
- underlay suppression for fallback text and submit behavior
- exact-match shared-action resolution behavior
- explicit ambiguous-match behavior
- built-in catalog integrity
- valid saved-action catalog extension behavior
- valid URL saved-action catalog extension behavior
- missing, empty, invalid, unsupported, duplicate, and colliding saved-action fallback behavior
- invalid URL saved-action fallback behavior
- URL launch-path behavior without Windows path normalization
- compact end-to-end typed-first `entry` -> `choose` -> `confirm` -> `result` behavior
- compact end-to-end typed-first URL confirm/result behavior

### Missing Explicit Validator Surfaces

No baseline-blocking validator gap is currently known for the locked typed-first interaction contract.

Future capability-expansion milestones may require additional validators when they deliberately change invocation surfaces, resolution behavior, authoring behavior, or non-success handling.

### Required Validator Surfaces Before Capability Expansion

Before capability expansion proceeds, the baseline must continue to be defended by:

- the existing overlay input-capture helper retained as a baseline regression surface
- a dedicated shared-action baseline validator
- a dedicated saved-action-source validator
- a compact integration validator proving the shipped typed-first contract still holds end to end

### What Expansion Must Defend

Future expansion work must preserve or explicitly re-negotiate:

- invocation reliability
- state-machine boundedness
- explicit confirmation before execution
- explicit ambiguity handling
- bounded saved-action fallback behavior
- clean result and reopen behavior
- the existing manual-reporting and non-success boundary

## Expansion Boundaries

### Baseline Guarantees

The guarantees in this document define the current typed-first baseline that future work must treat as protected behavior unless a later approved milestone explicitly changes it.

### Implementation Details

Current implementation details include:

- exact timer values for launch grace and capture rearm
- exact starter built-in action list and alias wording
- exact status or panel copy
- exact presentation layout details

Those details may change later without violating the baseline if the protected contract stays intact.

### Future Capabilities

Future capabilities explicitly deferred beyond this pass include:

- saved-action authoring UX
- routines
- profiles
- richer saved-action target kinds beyond `url`
- broader natural-language resolution
- voice invocation
- Action Studio
- broader shortcut customization

### Deferred Follow-Through Recorded Now

The following directly related FB-027 follow-through is recorded now but not implemented in this pass:

- remove `Ctrl+Alt+1` and `Ctrl+Alt+2` before Beta
- add an `Are you sure you want to exit?` prompt for shutdown hotkeys before Beta
- select the next capability-expansion milestone only through fresh post-release analysis on updated `main`

These are deferred forward items, not current-runtime guarantees.

## Stages / Executed Stages

1. promoted FB-027 into a canonical workstream
2. formalized the current typed-first interaction contract
3. defined enforceable invariants
4. mapped current validation coverage and missing validator surfaces
5. added dedicated shared-action, saved-action-source, and compact end-to-end interaction baseline validators
6. re-validated the retained overlay input-capture helper against the current renderer contract
7. recorded directly related deferred follow-through without widening into capability implementation
8. added first-class URL target support to the saved-action seam and shared action model without changing exact-match resolution
9. extended shared-action, saved-action-source, and integration validators to defend the new URL target capability

## Same-Branch Follow-Through

None for the URL-target capability milestone.

Future runtime or capability work must return as an explicitly selected next FB-027 milestone rather than as silent same-branch continuation.

## Blockers / Holds / Stop Conditions

- do not widen the URL-target milestone into broader saved-action, resolution, or interaction-surface expansion
- do not widen this workstream into runtime behavior changes without explicit approval
- do not treat deferred hotkey cleanup or shutdown confirmation work as current guarantees

## User Test Summary

This milestone changes a user-facing saved-action capability, so a workstream-owned User Test Summary should be expected before closure or release promotion.

Future user-facing interaction changes should assume a workstream-owned User Test Summary will likely be needed before closure.

## Baseline Lock Summary

The typed-first interaction baseline remains explicit and validator-defended, and the first bounded capability milestone now extends that baseline with first-class URL saved-action targets without redefining the state machine, exact-match resolution, or input-capture contract.

## Deferred Forward

- remove `Ctrl+Alt+1` and `Ctrl+Alt+2` before Beta
- add an `Are you sure you want to exit?` prompt for shutdown hotkeys before Beta
- choose the next capability-expansion milestone only through fresh post-release analysis on updated `main`

## Related References

- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/workstreams/index.md`
- `Docs/orin_interaction_architecture.md`
- `Docs/ncp_hardening_assessment.md`
