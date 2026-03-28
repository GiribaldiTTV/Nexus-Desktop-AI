# Jarvis Architecture

## Architectural Context

The current startup path is the stabilized desktop orchestration path, not the final product vision.

Current path:

`launch_jarvis_desktop.vbs`
-> `jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py`

Long-term vision:
Windows boot and login should transition into Jarvis as the primary user-facing layer, with Windows remaining the underlying platform.

## Startup Path

`launch_jarvis_desktop.vbs`
-> `jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py` (renderer)

## Future Boot Orchestrator Boundary

A future top-level boot orchestrator may sit above the current desktop launcher stack to coordinate:

- Windows boot and login handoff
- Jarvis startup presentation
- transition into the desktop phase
- future phase-to-phase health decisions

Until that higher-level system is explicitly designed, the desktop launcher remains the owner of:

- desktop-phase readiness observation
- desktop-phase stall handling
- desktop-phase cooperative control
- desktop-phase recovery routing

## System Roles

### Launcher (`jarvis_desktop_launcher.pyw`)

Responsible for:

- process orchestration
- startup observation
- classification (ready / slow / stall / abort / failure)
- control (cooperative abort)
- recovery and retry flow
- runtime and crash logging

### Renderer (`jarvis_desktop_main.py`)

Responsible for:

- UI and desktop rendering
- emitting lifecycle milestones
- responding to cooperative abort signal
- clean shutdown behavior

## Lifecycle Model

1. Startup begins
2. Launcher observes readiness
3. Renderer signals readiness
4. Launcher confirms state
5. System runs
6. Shutdown or failure occurs
7. Launcher handles outcome

## Startup Classification

- `STARTUP_READY_OBSERVED` -> healthy
- `STARTUP_READY_NOT_OBSERVED_WITHIN_WINDOW` -> slow
- `STARTUP_READY_STALL_CONFIRMED` -> stalled
- `RENDERER_MAIN|STARTUP_ABORTED` -> renderer acknowledged the cooperative startup-abort request
- `STARTUP_ABORT_COMPLETE` -> launcher completed abort-specific cleanup and control-flow handoff
- failure path -> crash or exception

## Control System

- Launcher owns control signals
- Renderer responds cooperatively
- No hard kill unless explicitly designed later

## Recovery Model

- Failed startup attempts enter recovery flow
- Recovery is handled by launcher
- Renderer remains simple and reactive

## Design Rule

The launcher is the brain.
The renderer is the body.

## System Layer Model

Jarvis is built as layered control over Windows:

Windows (host platform)
-> Launcher (orchestration and control)
-> Renderer (visual and interaction layer)
-> Future systems (voice, AI, user interaction)

Design rule:
Higher layers depend on lower layers, but lower layers must remain simple and stable.

The launcher controls behavior.
The renderer executes behavior.

## Version Context

`v1.6.0` completed the desktop orchestration stabilization track with:

- startup observation and classification (ready / slow / stall)
- cooperative startup-abort control
- retry and recovery with threshold-based early escalation for repeated `STARTUP_ABORT` and repeated identical crash outcomes
- mixed failure-pattern classification
- attempt-pattern, failure-stability, end-reason, and diagnostics-priority summaries
- diagnostics parity across live status, runtime logs, and crash reports
- triage guidance aligned with stability
- cross-layer consistency across runtime markers, diagnostics output, runtime summaries, and crash summaries

`v1.6.0` is closed and should be treated as a stable orchestration foundation, not an active tuning track.

This staged build order should be preserved in future subsystems when possible:

- observability
- classification
- control
- outcome clarity
- behavior

## v1.7.0 Direction

`v1.7.0` begins a new layer above the finalized `v1.6.0` orchestration truth:

- controlled intelligence
- passive cross-run historical awareness first
- deterministic execution preserved
- advisory-only outputs at the start
- no runtime behavior changes yet

The purpose of `v1.7.0` is not to revisit launcher control policy.
It is to introduce a derived memory layer that can describe history safely without altering the closed `v1.6.0` runtime behavior.

## Historical Memory Layer

The `v1.7.0` historical-memory layer is a passive, derived layer above finalized `v1.6.0` truth.

Its foundation is intended to support:

- cross-run outcome recording
- recurrence tracking
- stability trend tracking
- a multi-run regression concept

Confidence may exist inside this layer, but only as explanatory metadata.
It must never be treated as authoritative runtime policy.

## Historical Memory Contract (v1.7.0 Phase 1)

The historical memory layer was contract-defined before implementation began and remains governed by that contract.

That contract must define:

- versioned history schema
- run identity rules
- failure fingerprint rules
- provenance labeling
- retention and reset behavior
- corruption and fallback behavior

## v1.7.0 Implemented Foundation (rev1-rev6)

Current implemented foundation:

- rev1: recorder-only historical memory groundwork with versioned schema scaffolding and one finalized record per completed run
- rev2: recorder validation and storage-path hardening with fail-safe fallback
- rev3: read-only internal summarizer groundwork using recorded failure fingerprints and simple stability characterization
- rev4: diagnostics-only historical context on failed runs using prior finalized failure history
- rev5: diagnostics-only historical advisory hints on failed runs, clearly labeled historical and non-authoritative
- rev6: source-of-truth stabilization and doc/backlog sync for the implemented memory and advisory layer

Current guarantees:

- historical memory remains derived from finalized `v1.6.0` truth surfaces
- the launcher remains the source of truth for current-run state
- history remains non-authoritative and does not read back into runtime behavior
- diagnostics-facing historical context and advisory output remain failed-run-only
- advisory output remains non-binding
- historical context and advisory output remain diagnostics-facing surfaces and do not replace current-run incident-summary or crash-report truth
- if history is missing, unreadable, corrupt, or hostile, behavior degrades cleanly to finalized `v1.6.0` orchestration behavior

## Recorder / Summarizer / Advisor Separation

`v1.7.0` separates historical intelligence into three roles:

### Recorder

Responsible for:

- writing versioned per-run history
- storing only derived facts from finalized `v1.6.0` truth surfaces
- preserving deterministic, auditable history inputs

### Summarizer

Responsible for:

- recurrence interpretation
- stability trend summaries
- historical comparisons across runs
- provenance labeling for derived statements

### Advisor

Responsible for:

- presenting non-binding advisory output
- surfacing historical context to diagnostics or operators
- remaining advisory-only until a later explicitly approved control phase

Current implemented scope through rev5:

- diagnostics-only historical advisory hints
- failed runs only
- no runtime-control influence

## v1.7.0 Closeout State

`v1.7.0` is the completed historical-memory and diagnostics-advisory foundation above the closed `v1.6.0` orchestration layer.

It should be treated as:

- a completed passive recorder, summarizer, diagnostics-context, and diagnostics-advisory track
- a non-authoritative and non-binding intelligence layer
- a stopping point before any future confidence scoring, broader advisory expansion, or behavior-coupled intelligence work

## Read-Only Memory Rule

Historical memory in `v1.7.0` must remain a derived, read-only layer over `v1.6.0` truth.

That means:

- current-run runtime markers remain the primary truth
- current-run classification remains owned by the launcher
- historical memory may summarize, compare, and advise
- historical memory may not rewrite, override, or reinterpret current-run control state
- if historical data is missing, unreadable, or corrupt, the system must fall back cleanly to `v1.6.0` behavior

## Boot-Orchestration Preparation Boundary

`v1.7.0` may prepare for later boot-level orchestration only at the modeling layer.

Allowed:

- define desktop-stage history shapes that a future boot orchestrator could consume
- define boot and desktop phase-boundary concepts
- document how future higher layers may depend on launcher truth

Not allowed yet:

- boot-level runtime control
- adaptive retry or escalation
- instability-driven behavior
- hard-kill behavior
