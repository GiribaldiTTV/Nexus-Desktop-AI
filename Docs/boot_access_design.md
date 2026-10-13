# Nexus Boot Access Design

## Purpose

This document is the canonical planning reference for future boot-entry, trust, recovery, and post-login presence design in Nexus Desktop AI.

It does not authorize implementation work by itself.
It also does not own:

- backlog identity
- roadmap sequencing

Use it for future boot-access planning boundaries only.

## Current Reality

The current merged runtime path is:

`launch_orin_desktop.vbs`
-> `desktop/orin_desktop_launcher.pyw`
-> `desktop/orin_desktop_main.py`

This is the current controlled desktop-launch path.
It is not yet a boot-first Nexus experience.

## Planning Boundary

The future boot layer, if implemented later, sits above the current desktop launcher stack.

That future layer may eventually own:

- pre-desktop presence
- access or trust framing before desktop delegation
- user-facing boot experience
- post-login resident continuity as part of a coherent product surface

It does not currently authorize:

- boot runtime behavior
- auth backend design
- tray or shell implementation
- credential storage mechanics
- OS integration mechanics

## Experience Goal

The long-term access experience should feel like:

- the machine is entering Nexus Desktop AI rather than launching a normal app
- ORIN is the assistant presence the user is meeting
- trust and recovery are framed inside that experience rather than tacked on around it
- Windows remains reachable as the host platform rather than being replaced as a rescue path

## Delegation Boundary

The future boot layer must stop owning execution once it delegates into the desktop launcher.

After delegation:

- launcher owns desktop startup execution
- launcher owns desktop failure and recovery truth
- higher layers may observe launcher-emitted truth only after emission

This preserves the current architecture instead of creating a second control authority.

## Access Model

The planning model should preserve two distinct conceptual paths:

- routine access
- stronger or recovery-oriented access

Routine access should feel:

- quick
- calm
- intentional
- low-friction

Stronger access should feel:

- more deliberate
- clearly non-routine
- recovery-aware when needed
- still finite and understandable

The stronger path must not silently become the default daily path.

## Typed Sufficiency Rule

Typed secret entry remains the baseline trust-family rule in planning.

That means:

- typed entry must remain sufficient for the routine path
- future convenience or hardening factors must not silently replace typed sufficiency by default

## Windows Hello Role

If Windows Hello is introduced later, it should fit only as an optional routine-path convenience on compatible devices.

It should not:

- become mandatory
- replace typed sufficiency
- redefine trust continuity around device state alone

If Windows Hello is unavailable or fails, the ordinary routine typed path should remain valid.

## TOTP Role

If TOTP or authenticator-app factors are introduced later, they should fit only as optional additive hardening for stronger or recovery-oriented trust states.

They should not:

- become the default daily path
- replace the deliberate stronger-path baseline
- collapse routine and stronger access into one confused flow

## Fallback And Recovery Rule

Nexus Desktop AI must never become the only rescue path to Windows access.

That means:

- fallback to Windows must remain conceptually possible
- if trust continuity is bypassed, the system may later surface a guided recovery path after desktop entry
- fallback must not erase the distinction between routine access and trust restoration

## Resident Post-Login Presence

Later planning may treat Nexus Desktop AI as a resident post-login presence that can:

- reflect trust continuity state
- surface recovery entry when needed
- remain visible as a stable assistant anchor after desktop entry

That future resident surface remains planning-only.

It should stay distinct from:

- setup
- routine settings
- one-off recovery prompts

## Setup And Preference Posture

Consumer setup, later adjustment, and environment preferences remain separate future planning lanes.

This planning layer should preserve:

- future boot enablement as a user-controlled preference
- guided setup if OS changes are needed
- later adjustment as different from recovery
- environment preferences as different from trust or access semantics

## Relationship To Other Canon Layers

- use `Docs/architecture.md` for current system boundaries
- use `Docs/nexus_vision.md` for product intent
- use `Docs/orchestration.md` for current launcher-stack behavior
- use `Docs/orin_interaction_architecture.md` for future interaction-system planning
- use `Docs/feature_backlog.md` for tracked item identity
- use `Docs/prebeta_roadmap.md` for sequencing and release posture
