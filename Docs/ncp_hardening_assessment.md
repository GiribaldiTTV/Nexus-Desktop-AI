# NCP Hardening Assessment

## Purpose

This document is the canonical hardening assessment for the current FB-027 Nexus Command Prompt (NCP) follow-through lane.

Its purpose is to:

- preserve the current NCP hardening truth outside chat history
- distinguish what is complete enough now from what is only helper-strong
- record the conservative next-step recommendation for the current branch state
- give future FB-027 backlog wording a stable truth reference without changing backlog state in the same pass

This document is an assessment and sequencing reference.
It does not replace `docs/feature_backlog.md`, and it does not authorize automatic scope expansion.

## Scope Boundary For NCP Hardening

For current repo truth, NCP hardening means typed-first reliability follow-through for the current desktop command surface.

That includes:

- keyboard ownership and containment inside the visible overlay
- focus and reopen behavior
- transition stability across `entry`, `choose`, `confirm`, and `result`
- predictable reset and retry posture after success, back-out, or non-success outcomes
- stable user-visible failure-state behavior for the currently implemented command surface
- helper and regression validation for the exact typed-interaction risks already discovered

That does not include:

- voice integration
- Action Studio or later customization surfaces
- shortcut customization beyond the already implemented bounded desktop hotkeys
- command-set expansion
- broad UI polish or redesign
- broad architectural rewrite without a reproduced bug that requires it

## NCP Hardening Subsystems

The current meaningful NCP hardening areas are:

- input ownership and capture stability
- focus and reopen behavior
- `entry` / `choose` / `confirm` transition integrity
- `Enter` / digit / `Esc` containment guarantees
- no-mirroring / no-underlay-leak guarantees
- result-state reset and reopen predictability
- non-success-path predictability
- target clarity and execution clarity
- visual state consistency of the NCP surface
- helper and regression validation coverage

## Complete Enough Now

`Complete enough now` means good enough by current repo truth and live evidence for the current pre-Beta branch state, not theoretical perfection.

The following areas are complete enough now:

- input ownership and capture stability for the regression family already discovered
- no-mirroring / no-underlay-leak guarantees for the currently validated typed paths
- `Enter` / digit / `Esc` containment guarantees for the currently validated typed paths
- focus and reopen behavior for the success-path and cancel/retry flows already exercised
- `entry` / `choose` / `confirm` transition integrity for the current typed command surface
- result-state reset and clean reopen behavior for the validated success path
- `launch_failed` result handling and retry/reset posture for the current typed command surface
- target clarity and execution clarity for the current command set
- visual state consistency of the NCP surface, including compact reset after backing out of expanded states

Current repo truth supports this classification because the merged overlay-usability lane and the current hardening branch already closed:

- mirrored typing and underlay leakage regressions
- first-`Enter` and second-`Enter` containment failures
- delayed ambiguous number-selection failure without manual refocus
- caret / visual state mismatch after focus leaves the NCP
- `Esc` cancel-and-retry reliability issues
- layout reset after `Esc` from `choose` / `confirm`
- success-path clean result close / reopen reset
- stale retry-state carry-over for current non-success back-out flows
- `launch_failed` visible failure-result handling, clean reopen/reset posture, and retry cleanliness for the current command surface

## Mostly Hardened But Under-Validated

`Mostly hardened but under-validated` means the model, runtime, or helper evidence is stronger than the current live user-validation depth.

No currently meaningful NCP subsystem remains in this category for the active branch scope.

The helper / regression surface may still be stronger than the live validation depth for some future failure-oriented or cross-system paths.
That is useful and intentional, but it is no longer the gating question for the current NCP hardening lane.

## Still Needs Hardening

No currently reproduced runtime bug forces another NCP patch at the moment.

No currently meaningful near-term NCP hardening candidate remains inside this lane before branch-level closure review.

Broader failure-class, diagnostics-surface, reporting, or voice-role contract work now belongs to `docs/architecture.md` rather than this NCP hardening doc.
That later cross-system work should not be treated as an automatic continuation of the current typed-first NCP hardening lane.

## Not In Work Yet

These items are relevant to future NCP follow-through but are not active work right now:

- broader non-success-path polish beyond a reproduced issue
- any later slice that is only justified if new live evidence reopens a typed-interaction regression

## Not Ready Yet Due To Future Integration Dependencies

These items are NCP-adjacent, but they should wait because later product layers are not yet ready:

- voice-parity behavior above the same interaction model
- Action Studio and later customization surfaces
- broader shared-action-model expansion beyond the current typed-first hardening lane
- later installable / packaged interaction behavior that depends on future Beta-stage delivery

Future voice should build on the same interaction model as typed interaction.
That does not make voice part of current NCP hardening.

## Current Recommended Next Step

The current recommended next step is:

1. do not patch automatically
2. treat the approved NCP hardening lane as runtime-complete enough for its current scope
3. move to branch-level readiness / closure review for `feature/fb-027-ncp-hardening`

This is the conservative next step because the latest returned live user validation closed the `launch_failed` validation-first question without reopening a new NCP runtime bug.

## What Should Wait Until Later

The following should stay out of the current NCP hardening lane:

- voice integration
- Action Studio
- shortcut customization
- `Shift+Home` or other QoL extras
- broader UI polish
- command expansion
- broad architectural rewrites without a reproduced bug

## How This Document Should Be Used Relative To The Relevant FB-027 Backlog Item

This document should be used as the canonical NCP hardening reference for future FB-027 follow-through wording.

That means:

- `docs/feature_backlog.md` should remain the controlling backlog file
- future approved FB-027 backlog updates may point to this assessment instead of restating the full hardening map
- backlog wording should stay concise and should not duplicate this document unless a later approved slice materially changes the assessment

Backlog changes remain approval-gated.
This document exists so future backlog carry-forward can reference one stable source of truth instead of relying on chat history.
