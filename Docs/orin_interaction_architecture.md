# Jarvis Interaction Architecture

## Purpose

This document is the canonical planning baseline for Jarvis user interaction as a voice-first, typed-sufficient, user-customizable system layer.

It defines:

- the primary user-facing interaction surfaces
- the shared action model that should sit underneath voice and typed commands
- the customization model for saved actions, routines, aliases, and profiles
- the intended pre-Beta, Beta, and later Full release scope

This is still a planning artifact.
It does not define implementation mechanics for wake-word detection, speech-to-text, auth backend behavior, shell integration, tray mechanics, renderer wiring, plugin loading, or concrete runtime execution logic.

## Relationship To Core Source-Of-Truth Docs

This document is downstream of:

- `architecture.md` for launcher-owned desktop authority and higher-layer read-only limits
- `jarvis_vision.md` for Jarvis as the intended system-facing experience
- `boot_access_design.md` for future pre-desktop access, trust, recovery, and resident trust-state boundaries
- `feature_backlog.md` for workstream status and scope control

This document does not replace those files.
It narrows only the future Jarvis interaction surface and its customization model.

## Product Intent

Jarvis should evolve toward a system-facing interaction layer that feels more like a personal operator than a conventional desktop app launcher.

At the user level, that means:

- Jarvis is voice-first in personality and product direction
- typed interaction remains fully sufficient
- users can speak or type naturally rather than memorize rigid command syntax
- Jarvis can map natural intent to reusable user-defined actions, routines, and environments
- users can inspect, customize, and trust what Jarvis will do

The system should feel closer to:

- "Hey Jarvis, launch sim"
- "Open Windows Explorer"
- "I'd like you to open my sim setup"

than to a brittle command console that only accepts one exact phrase.

## Governing Interaction Principles

- voice-first, not voice-only
- typed-sufficient for all core interaction
- one shared action system underneath all input surfaces
- user-customizable by default rather than hardcoded around one machine
- observable and inspectable rather than opaque
- safe by default when actions could be risky or ambiguous
- local product identity first, not a generic desktop launcher clone

## Core Interaction Surfaces

At planning level, Jarvis interaction should eventually be split across four primary user-facing surfaces:

### 1. Voice Invocation Surface

The long-term voice-first surface is the wake-word path, such as:

- `Jarvis`
- `Hey Jarvis`

This is the future always-ready interaction posture, but it is not required for the first pre-Beta slice.

### 2. Quick Command Overlay

The typed-first companion surface is a dismissible command overlay.

At planning level, this should be:

- fast to open
- fast to dismiss
- usable as the typed equivalent of speaking to Jarvis
- able to accept natural-language typed requests

The current preferred default hotkey is:

- `Ctrl+Alt+Home`

That hotkey should be treated as a planning-level default, not a permanently fixed non-configurable rule.

### Alternate Desktop Hotkey Direction

For current Nexus-era desktop interaction, the default desktop hotkeys remain:

- `Ctrl+Alt+Home` for the quick command overlay
- `Ctrl+Alt+End` for the current desktop shutdown path

Future interaction follow-through should preserve room for:

- one alternate user-usable binding for opening and closing the quick command overlay
- one alternate user-usable binding for the current desktop shutdown path

The purpose of this direction is:

- to reduce dependence on one exact physical-key path
- to support broader usability across keyboards and user preference
- to leave room for later bounded shortcut follow-through without forcing a full shortcut-customization system immediately

This direction does not authorize immediate implementation of configurable shortcut management or a broad keybinding system.

### 3. Action Studio

The customization surface is the place where the user defines and edits saved actions, aliases, routines, and profiles.

This is the closest conceptual analogue to a StreamDeck-style authoring surface, but it should remain Jarvis-shaped rather than becoming a clone of button-grid hardware software.

### 4. Runtime And Status Surface

Jarvis should expose a clear runtime/status surface that explains what it is doing now, what it just ran, and where a routine or command currently stands.

This surface exists to preserve user trust and reduce "black box" behavior.

## Shared Action Model

Voice and typed interaction must not become separate products.

At planning level, both should resolve into one shared interaction model:

- `intent`
  - what the user means
- `action`
  - one executable user-facing thing Jarvis can do
- `routine`
  - an ordered bundle of actions
- `profile`
  - a saved user-defined environment or context, such as a sim setup
- `alias`
  - alternate phrases that resolve to the same action or routine

The key rule is:

- voice input and typed input should resolve into the same action, routine, alias, and profile model

This prevents Jarvis from splitting into:

- one system for "voice commands"
- another system for "typed commands"
- a third system for "saved presets"

## Natural-Language Command Contract

Jarvis should be open to ordinary language variation rather than one exact command syntax.

At planning level, that means a user should be able to express similar intent in multiple ways, such as:

- `open windows explorer`
- `open file explorer`
- `I'd like you to open Windows Explorer`

without the system being planned around one rigid phrase only.

This does not authorize freeform AI action execution without boundaries.
It only defines the product-level expectation that intent matching should be flexible and user-friendly.

## Desktop-Mode Command Confirmation Contract

At planning level, when Jarvis is already inside desktop mode and is about to run a user-requested command, Jarvis should confirm the interpreted action before execution.

That confirmation should make clear:

- what Jarvis believes the user asked for
- which defined action, alias, routine, or target Jarvis resolved
- which user-defined path, app target, or launch context Jarvis is about to use when that matters

The purpose of this confirmation is:

- to ensure Jarvis and the user share the same interpretation before execution
- to keep desktop-mode command execution observable and trustworthy
- to reduce accidental execution caused by ambiguous natural-language interpretation

This planning contract does not define the exact UI phrasing, visual layout, or confirmation-control mechanics.
It only defines the product rule that desktop-mode command execution should be explicitly confirmed before Jarvis runs the resolved action.

### Confirmation Clarity For Paths And Targets

When the resolved action points to a file, folder, URL, app target, or other path-sensitive destination, the confirmation surface should make the destination understandable before execution.

At planning level, that means:

- show enough target detail that the user can tell what will open or run
- use a compact or truncated path display when the full raw path would be visually noisy
- avoid hiding the important distinguishing part of the target when multiple similar choices exist

The purpose of this rule is:

- to keep confirmation useful instead of decorative
- to help the user understand why one match differs from another
- to reduce accidental launches when multiple choices are similar

## Nexus-Era User-Facing Naming Rule

For Nexus Desktop AI / ORIN-era interaction surfaces, user-facing command labels and choices should prefer current Nexus-era naming rather than legacy Jarvis branding unless the user is explicitly interacting with preserved historical context.

This means future command-surface work should trend toward:

- Nexus-facing names for Nexus-facing actions
- ORIN-facing assistant presentation where assistant identity matters
- avoiding legacy Jarvis naming in normal Nexus-facing command choices

This is a user-facing interaction rule only.
It does not authorize historical rewrite of preserved Jarvis release history.

## Customization Contract

Jarvis customization should allow users to define:

- action names
- aliases and alternate phrases
- app, file, folder, URL, or command targets
- ordered launch steps
- saved routines or environment profiles
- preferred starting posture for recurring contexts, such as sim-racing setups

At planning level, this contract should support user-defined targets like:

- `Launch Sim`
- `Start Racing`
- `Open Work Setup`

without forcing every user into the same built-in command map.

As the interaction model grows, customization should also allow bounded preference control over supported web-facing actions, such as:

- which browser Nexus uses for supported search or web actions
- which user-approved external web destination should be used when more than one valid route exists

Those later capabilities should remain:

- user-controlled
- explicit
- privacy-aware
- downstream of the same shared action model rather than separate hardcoded pathways

## Release-Stage Model

At planning level, the release stages for this interaction lane should follow the product-wide release-stage framing in `jarvis_vision.md`:

- `pre-Beta`
  - internal or tightly controlled delivery of the first usable interaction slices
  - architecture, interaction model, and command-surface proof rather than packaged user distribution
- `Beta`
  - a packaged, installable, user-facing release with a real `.exe` or installer path, stable setup expectations, and practical customization
- `Full`
  - the broader mature interaction system beyond the first installable/testing release

## Pre-Beta Release Direction

The pre-Beta phase should prioritize the smallest coherent user-visible interaction foundation.

At planning level, pre-Beta should center on:

- the quick command overlay
- typed natural-language command entry
- the shared action model underneath typed commands and future voice commands
- saved actions, aliases, routines, and profiles
- a clear runtime/status surface for launched actions

Pre-Beta should aim to prove:

- Jarvis can feel like a coherent command surface rather than a generic app menu
- users can define reusable launch actions and routines for their own machine
- typed interaction already uses the same model that future voice interaction will depend on

## Pre-Beta First Deliverable Direction

The first pre-Beta deliverable should be the smallest typed-first slice of this interaction model:

- a dismissible quick command overlay
- natural-language typed command entry
- a minimal shared action model for direct actions and saved aliases
- desktop-mode confirmation before executing the resolved action

This first deliverable should not require the full Action Studio, wake-word support, or advanced routine graphing.

## Beta Release Direction

At planning level, the Beta release should expand the proven pre-Beta interaction foundation into a packaged and installable user-facing release.

Beta may later include:

- a real `.exe` or installer path
- stable install-time setup expectations
- practical user-facing customization beyond the first internal slice
- stronger reliability and usability for broader testing

## Full Release Direction

At planning level, the Full release may later expand into:

- wake-word voice invocation
- stronger voice parity with typed commands
- optional spoken response or confirmation support for more hands-free interaction
- richer saved routines and environment profiles
- more advanced customization surfaces
- import/export or sharing of user-defined actions
- bounded user-approved external-assistant or web handoff actions if they remain privacy-aware and clearly inspectable
- future plugin capability if the shared action model proves stable enough

These later additions should remain downstream of the same shared action system rather than becoming parallel products.

## Explicit Deferrals

This planning baseline intentionally defers:

- wake-word implementation mechanics
- speech-to-text or local-audio pipeline mechanics
- shell, tray, renderer, or notification mechanics
- exact runtime execution engine mechanics
- auth backend or trust mechanics
- Windows Hello or TOTP implementation mechanics
- plugin architecture and plugin lifecycle design
- exact screen layout or UI flow details for the Action Studio
- advanced node-graph or visual process-tree editing

## Out-Of-Bounds Patterns

The following are out of bounds for this planning baseline:

- building separate logic stacks for voice commands and typed commands
- treating voice-only interaction as sufficient
- treating typed interaction as a temporary debug path rather than a first-class certainty path
- collapsing Jarvis into a generic launcher with no user-defined action model
- turning the first pre-Beta slice into plugin work
- coupling the interaction layer to launcher-owned desktop authority or control decisions

## Success Criteria

This planning baseline is heading in the right direction if future implementation makes it feel like:

- Jarvis is the command surface
- Jarvis is understandable and customizable
- Jarvis can be shaped around the user's machine and habits
- voice and typed interaction feel like two entry paths into one coherent system

This planning baseline is drifting if future implementation makes it feel like:

- a generic desktop app launcher
- a brittle command parser with exact syntax only
- an opaque automation engine the user cannot inspect
- disconnected voice, typed, and preset systems pretending to be one product
