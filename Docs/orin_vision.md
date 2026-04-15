# Nexus / ORIN Vision

## Purpose

This document defines product intent for Nexus Desktop AI and the ORIN assistant layer.

It does not own:

- workstream closure
- backlog identity
- roadmap sequencing

Use it for product direction, experience intent, and release-stage meaning.

## Core Product Goal

Nexus Desktop AI should eventually feel like the system-facing experience layer, not just a normal desktop app launched after Windows.

The long-term direction is:

Windows boots
-> Nexus startup and orchestration begins
-> ORIN becomes the primary visible assistant experience
-> Windows remains the underlying host platform

## Current Reality

The current merged runtime is still a controlled desktop orchestration path:

`launch_orin_desktop.vbs`
-> `desktop/orin_desktop_launcher.pyw`
-> `desktop/orin_desktop_main.py`

That path is foundation work.
It stabilizes startup, recovery, diagnostics, and lifecycle behavior.
It is not yet the final boot-first product experience.

## Experience Intent

The experience should trend toward:

- Windows as infrastructure
- Nexus Desktop AI as the visible experience layer
- ORIN as the assistant presence that gives the product identity

The product should not feel like:

- Windows as the experience and Nexus as a small overlay
- a generic utility app running on top of the desktop

## Product Principles

Nexus Desktop AI should feel:

- system-facing
- intentional
- calm under normal use
- explicit when trust or recovery posture changes
- recoverable rather than opaque

The system should not rely on:

- hidden state
- unexplained automation
- accidental authority drift between launcher, renderer, planning docs, and user-facing reporting

## Release-Stage Meaning

Across the product:

- `pre-Beta` means architecture, runtime boundaries, validation, and internal product shape are still stabilizing
- `Beta` means the product is coherent enough for broader user-facing evaluation and setup expectations
- `Full` means the product has crossed from staged system foundation into mature product delivery

This means the repo may contain meaningful `pre-Beta` implementation progress without claiming Beta readiness.

## Future Boot Preference Model

Before `Beta`, the Boot portion of Nexus Desktop AI should become a user-controlled preference rather than an assumed always-on behavior.

That future model should mean:

- the user can intentionally enable or disable the Boot experience
- if setup requires Windows login, startup, or boot-configuration changes, the product should guide the user through that setup
- the current desktop runtime path remains valid even when future boot-facing work is deferred

## Future Grouping Direction

Callable groups can be a valid part of the bounded pre-Beta command surface when they stay explicit, exact-match, and member-driven.

Post-Beta expansion may explore richer grouping behavior such as:

- dynamic natural-language grouping requests
- group discovery or query flows like "show me all tasks associated with..."
- broader organizational or recommendation layers above exact callable aliases

That expansion should remain deferred until after the current exact-match callable-group model is proven.

Current vision boundary:

- pre-Beta callable groups should stay explicit and exact-match
- post-Beta grouping/query ideas should not be used to weaken command predictability in the current release

## Trust And Recovery Posture

Nexus should eventually present trust, recovery, and post-login continuity as one coherent experience layer, but the repo is not there yet.

Current merged truth should still be read as:

- desktop orchestration first
- future boot and access planning deferred
- product trust and resident presence concepts still living at planning level

## Post-Beta AI Vision

This section records intended post-Beta AI direction.

It is future-facing product intent only.
It does not change current pre-Beta runtime truth, roadmap sequencing, or the active `FB-036` + Idea 5 branch boundaries.

### AI Behavior Goals

- responses should feel organic and dynamic without becoming vague or improvisational
- reasoning should feel smart and practical while staying inside explicit system constraints
- the assistant should stay lightweight enough to feel responsive on normal hardware
- the interaction model should be approachable for everyday use while still supporting deeper reasoning when needed
- conversational behavior should remain grounded, predictable, and easy to trust

### Capability Boundaries

- common everyday queries should be handled locally where practical
- the local system should avoid heavy or expensive workloads that do not fit the machine or the release stage
- external deferral is acceptable when computation is too large, storage or model footprint is impractical, or an outside system is the better execution surface
- when deferral happens, the system should say so clearly rather than hiding the boundary

### Privacy Model

- privacy-first defaults are non-negotiable
- retain as little user data as practical and avoid unnecessary persistence
- avoid third-party monitoring or exposure where a local or first-party path can satisfy the need
- user trust, visibility, and local control are primary design constraints

### Execution Model

- the intended direction is hybrid and local-first
- local logic should handle common tasks, routing, and assistant orchestration
- external fallback should remain optional and reserved for queries that exceed reasonable local capability
- even when external help is used, the product should still feel like a local system extension rather than a thin client for a remote dependency

### Technology Exploration

- Python is the primary exploration path for orchestration and rapid iteration
- C++ is a candidate path for performance-critical components
- CUDA is an optional acceleration path where a later workload actually justifies it
- Java and C# remain open integration paths where platform or tooling fit warrants them
- this is exploration space, not a locked implementation stack

### Visual Identity Principles

- the UI should read as a direct extension of the assistant rather than as a separate utility wrapped around it
- the visual layer should represent AI state, handoff state, and boundary changes clearly
- AI behavior and UI feedback should stay aligned so the product feels coherent rather than split into "assistant" and "tool"

### Explicit Non-Goals For Current Release

- do not treat this section as current implementation truth
- do not introduce large local models or heavy local inference in the current release
- do not widen the current branch beyond `FB-036` + Idea 5
- do not reinterpret current workstream, validation, or release-posture docs through this future section

## Historical Relationship

The public Nexus release line begins after the preserved Jarvis historical release line.

That means:

- older Jarvis releases remain preserved as historical records
- they do not define the active public Nexus release line
- current vision and current release posture should be expressed in Nexus / ORIN terms unless a section is explicitly historical

## Relationship To Other Canon Layers

- use `Docs/architecture.md` for architectural boundaries
- use `Docs/orchestration.md` for orchestration behavior and runtime ownership
- use `Docs/boot_access_design.md` for future boot-access planning
- use `Docs/prebeta_roadmap.md` for sequencing and release posture
- use `Docs/workstreams/...` for promoted workstream history
