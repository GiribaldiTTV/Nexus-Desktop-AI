# ORIN Interaction Architecture

## Purpose

This document defines the interaction-system architecture for Nexus Desktop AI and the ORIN persona.

It is a planning and boundary reference.
It does not own workstream status, backlog state, roadmap sequencing, or release closure.

Use this document to define:

- the interaction surfaces the product should support
- the shared concepts those surfaces should resolve through
- the current merged interaction baseline
- the long-term interaction architecture that future work should preserve

## Relationship To The Source-Of-Truth Stack

This document is downstream of:

- `Docs/architecture.md` for desktop/runtime ownership boundaries
- `Docs/orin_vision.md` for product identity and release-stage framing
- `Docs/orchestration.md` for runtime behavior and orchestration boundaries
- `Docs/boot_access_design.md` for future pre-desktop trust and access boundaries
- `Docs/feature_backlog.md` for tracked identity
- `Docs/prebeta_roadmap.md` for sequencing and release posture
- `Docs/workstreams/` for promoted execution and closure truth

This document does not replace those layers.
It defines the stable interaction model that future work should align to.

## Current Merged Baseline

Current repo truth is a typed-first desktop interaction system with the following merged baseline:

- a quick command overlay is the current primary user-facing interaction surface
- the current default desktop hotkeys are `Ctrl+Alt+Home` and `Ctrl+Alt+1` for opening the overlay
- the current desktop shutdown paths are `Ctrl+Alt+End` and `Ctrl+Alt+2`
- the overlay uses a bounded `entry` -> `choose` -> `confirm` -> `result` interaction flow
- the overlay preserves explicit confirmation before executing the resolved action
- a shared action model now sits underneath the command surface
- a saved-action source seam exists at `%LOCALAPPDATA%/Nexus Desktop AI/saved_actions.json`
- built-in actions and saved actions resolve through the same shared catalog shape

Current repo truth does not yet include a shipped voice-invocation surface, Action Studio UI, or broader shortcut-customization system.

## Product Intent

Nexus Desktop AI should evolve toward an interaction system where ORIN feels like an understandable, inspectable operator surface rather than a brittle launcher or opaque automation engine.

At product level, that means:

- voice-forward product direction without making voice the only valid interface
- typed interaction remaining fully sufficient
- natural-language requests resolving into one coherent action model
- users being able to inspect what ORIN believes they asked for before execution
- users being able to define, reuse, and later expand their own actions and routines

## Governing Interaction Principles

- voice-forward, not voice-exclusive
- typed interaction is a first-class certainty path
- one shared action model underneath all interaction surfaces
- inspectable resolution before execution
- safe handling when interpretation is ambiguous or execution could surprise the user
- user-defined actions and aliases should be part of the architecture, not bolted on later
- ORIN is the current assistant persona for interaction surfaces

## Interaction Surfaces

### Desktop Command Overlay

The current merged interaction surface is the desktop command overlay.

Architecturally, it should remain:

- fast to invoke
- fast to dismiss
- keyboard-first for current pre-Beta use
- capable of accepting natural-language typed requests
- explicit about the resolved action before execution

### Voice Invocation Surface

A future voice surface may later sit above the same shared action model.

That future surface should be treated as another entry path into the same interaction system, not as a separate product with separate logic.

This document does not define wake-word implementation, speech-to-text mechanics, or audio-pipeline execution details.

### Action Authoring Surface

A future authoring surface should let users define and inspect:

- saved actions
- aliases
- routines
- profiles
- later bounded preferences that affect how supported actions resolve

This authoring surface should stay downstream of the same shared action model already used by typed interaction.

The first bounded authoring follow-through should prefer:

- explicit user-facing action-type selection
- bounded target choices such as Windows app, Application (`.exe`), folder, file, and website URL
- safe persistence and validation before write

It should not assume full Action Studio scope just to make custom tasks usable.

### Built-In Versus User-Defined Actions

The architecture should distinguish between:

- curated built-in actions for standard Windows, system, vendor-utility, and Nexus-owned surfaces
- user-defined saved actions for personal, host-specific, or non-standard tasks such as custom URLs, folders, files, or app targets

That distinction keeps common product capability feeling native while preserving saved actions as the bounded customization seam.

### Taskbar Or Tray Quick-Access Surface

A future shell-facing surface may later expose quick-task entry from the taskbar or tray, including a Create Custom Task affordance.

That future surface should feed into the same shared action model and authoring boundaries rather than becoming a disconnected launcher path.

### Runtime And Status Surface

The interaction system should expose what ORIN is doing, what it just resolved, and what the current command state is.

This supports:

- user trust
- confirmation clarity
- recoverability after non-success outcomes
- better debugging and validation evidence

A later runtime-and-status follow-through may also expose monitoring or HUD surfaces for GPU / CPU thermals and performance, but that should remain a separate bounded lane rather than being treated as automatic saved-action follow-through.

## Shared Action Model

Typed and future voice interaction should resolve through the same conceptual model:

- `intent`
- `action`
- `routine`
- `profile`
- `alias`

The architecture should not split into:

- one system for typed commands
- one system for voice commands
- one separate system for saved presets
- one hidden side system for shell quick tasks, plugins, or monitoring overlays

The shared action model is the architectural seam that keeps those surfaces coherent.

## Command Resolution Contract

The interaction layer should accept ordinary language variation rather than depending on one exact phrase.

Examples of equivalent user intent may include:

- `open windows explorer`
- `open file explorer`
- `open my Nexus docs`

The architectural rule is flexible intent resolution with bounded, inspectable outcomes.
It is not authorization for unconstrained AI action execution.

## Confirmation Contract

Before execution, the interaction surface should make clear:

- what ORIN believes the user requested
- which action, alias, routine, or target was resolved
- what destination, app target, file, folder, or URL will be used when that matters

For path-sensitive targets, the confirmation surface should show enough detail to distinguish similar options without becoming visually noisy.

This contract preserves trust and reduces accidental execution when natural-language resolution is flexible.

## Current Desktop Interaction Guarantees

Current merged desktop interaction guarantees include:

- immediate typed-entry readiness when the overlay opens from the supported hotkey paths
- bounded ambiguous-choice resolution through visible number-key selection
- preserved explicit confirmation before execution after keyboard selection
- clean `Esc` back-out behavior inside the visible overlay
- local keyboard ownership while the overlay is active
- reuse of the shared action model rather than an overlay-only command catalog
- bounded saved-action sourcing with strict built-in fallback when the saved source is missing or invalid

These are current baseline guarantees, not the full future interaction surface.

## User-Facing Naming Boundary

For current product truth:

- `Nexus Desktop AI` is the product and tooling-shell identity
- `ORIN` is the shipped assistant persona

User-facing interaction surfaces should prefer current Nexus / ORIN naming.

Legacy `Jarvis` wording should appear only when:

- preserved historical context is being discussed
- backward-compatible runtime artifacts still use that name
- the user is explicitly interacting with older historical material

## Customization Boundary

The interaction architecture should support user-defined:

- action names
- aliases
- targets
- ordered routines
- profiles and recurring contexts

It may later support bounded user preferences for supported web-facing or external actions, but those capabilities should remain explicit and inspectable.

This document does not define the exact storage schema, editor UI, or execution engine for those features.

Future customization should also preserve:

- explicit user-facing type choice for custom tasks
- safe distinction between standard built-in actions and user-defined saved actions
- bounded plugin and external-trigger ownership instead of silent connector sprawl

## Release-Stage View

At architecture level:

- `pre-Beta` proves the interaction model and current desktop command surface
- `Beta` expands that model into a more installable and broadly testable product surface
- `Full` may later widen into richer voice, authoring, and profile capabilities

The release-stage view belongs here only as interaction-system framing.
Specific sequencing belongs in the roadmap and specific execution belongs in workstream records.

## Explicit Deferrals

This architecture document does not define:

- wake-word implementation mechanics
- speech-to-text or local-audio pipeline mechanics
- tray, shell, renderer, or notification implementation details
- auth or trust backend mechanics
- plugin lifecycle design
- Stream Deck or similar external-trigger lifecycle specifics
- monitoring or HUD implementation specifics
- exact Action Studio screen layout
- detailed routine-graph editing UX

## Failure Modes To Avoid

The interaction architecture is drifting if future work turns it into:

- a generic launcher with no coherent interaction identity
- disconnected typed, voice, and saved-action systems
- an opaque execution surface with weak confirmation
- a system where typed input is treated as a temporary fallback instead of a first-class path

The architecture is holding together if future work keeps all interaction surfaces aligned to one inspectable shared action model.
