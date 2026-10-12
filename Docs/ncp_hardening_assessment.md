# NCP Hardening Assessment

## Purpose

This document describes the typed-first Nexus Command Prompt interaction surface and the failure classes that matter to its reliability. It does not define voice behavior, Action Studio authoring, or unrelated UI changes.

## Current Surface Definition

For current repo truth, the Nexus Command Prompt is the typed-first desktop command surface built around:

- the quick command overlay
- explicit keyboard-owned interaction while the overlay is active
- a bounded `entry` -> `choose` -> `confirm` -> `result` state flow
- explicit confirmation before execution
- shared action-model resolution for built-in and saved actions
- bounded saved-action loading with strict fallback behavior when the saved source is missing or invalid

This document covers hardening expectations for that surface only.

It does not define:

- voice invocation behavior
- Action Studio authoring UI
- broader shortcut customization
- new command families
- unrelated UI redesign

## Hardening Domains

The meaningful hardening domains for the current command surface are:

- keyboard ownership and containment
- focus and reopen stability
- transition integrity across `entry`, `choose`, `confirm`, and `result`
- predictable `Enter`, digit, and `Esc` behavior
- result-state reset and reopen predictability
- non-success-path clarity and recoverability
- target clarity before execution
- visual state consistency
- helper and regression validation coverage

## Current Merged Baseline Assessment

Current product behavior supports the following baseline assessment:

- the typed-first command surface is stable enough for current typed-first use
- the current command-state transitions are bounded and understandable
- confirmation before execution is preserved
- keyboard-first ambiguous-choice resolution is present
- non-success handling now has a clearer bounded result path than earlier overlay iterations
- the shared action model and saved-action seam create a more stable interaction foundation than an overlay-local catalog alone

This assessment means the command surface has a usable hardening baseline.
It does not claim that the surface is feature-complete or final.

## What Future Follow-Through Would Need To Be About

Future NCP hardening work should be justified by one or more of the following:

- a reproduced runtime regression in the current command surface
- a newly discovered failure class that the current interaction contract does not handle cleanly
- a major new interaction capability that changes the command-surface risk profile
- packaging, install, or broader user-testing evidence that exposes a current desktop interaction weakness

Future work should not be justified only by vague polish pressure or by re-opening already settled behavior without fresh evidence.

## Scope Boundary

A reproduced regression, newly discovered failure class, or new command capability can justify targeted hardening. Stable behavior should remain stable unless current evidence shows a defect. Voice invocation, Action Studio authoring, and broader shortcut customization have separate product contracts.
