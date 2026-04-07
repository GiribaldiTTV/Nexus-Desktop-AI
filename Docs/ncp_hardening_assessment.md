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

## Mostly Hardened But Under-Validated

`Mostly hardened but under-validated` means the model, runtime, or helper evidence is stronger than the current live user-validation depth.

The clearest current case is:

- `launch_failed` result handling and retry/reset posture

Why it belongs here:

- helper coverage already exercises failure-result clearing and clean reopen/reset behavior
- the current model and renderer state cleanup path is conservative
- but this path has not been closed by the same level of fresh live user validation as the success-path and cancel/retry slices

The helper / regression surface itself is also stronger than the live validation depth for some failure-oriented paths.
That is useful and intentional, but it should not be mistaken for equal-weight user confirmation.

## Still Needs Hardening

No currently reproduced runtime bug forces another NCP patch at the moment.

The only meaningful near-term candidate that still belongs in this lane is:

- `launch_failed` user-visible failure-state predictability

This should be treated as a validation-first candidate, not as an automatically approved new patch.

The current question is not whether a broader failure system should be redesigned.
The current question is only whether the visible `launch_failed` path feels as reset-clean and predictable as the now-validated success path.

## Not In Work Yet

These items are relevant to future NCP follow-through but are not active work right now:

- broader non-success-path polish beyond a reproduced issue
- branch-level readiness and closure review after the `launch_failed` validation-first decision
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
2. do one validation-first step for `launch_failed` user-visible failure-state predictability
3. if that validation passes, move to branch-level readiness / closure review for `feature/fb-027-ncp-hardening`

This is the conservative next step because current repo truth does not show a newly reproduced failure.
It shows one remaining area where helper confidence still leads live validation depth.

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
