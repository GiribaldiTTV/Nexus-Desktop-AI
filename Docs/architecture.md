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

## v1.8.0 Direction

`v1.8.0` should be treated as a trust-and-validation phase for cross-run historical intelligence.

Its job is not to make Jarvis more behaviorally aggressive or more authoritative.
Its job is to make the existing historical layer more trustworthy, repeatable, and future-safe before any broader intelligence work is considered.

Official objective:

- validation-first multi-run historical-intelligence infrastructure
- stronger replay and verification across launches
- clearer recurrence and provenance semantics built on existing `v1.7.0` boundaries
- no runtime-control coupling
- no authority expansion

## v1.8.0 Safest First Revision

The safest first revision for `v1.8.0` is:

- `FB-014` multi-run orchestration regression harness

That first revision should remain:

- tooling and verification focused
- cross-run and replay oriented
- isolated from launcher runtime-control behavior
- sufficient to validate recorder, summarizer, diagnostics-context, and diagnostics-advisory behavior across repeated launches

Explicit non-goals for `v1.8.0` rev1:

- confidence scoring
- advisory authority expansion
- historical readback into runtime behavior
- retry, escalation, threshold, or classification changes
- boot-level orchestration work

## v1.8.0 Implemented Rev1 Foundation

`FB-014` rev1 is now implemented as the validation-first harness foundation for `v1.8.0`.

Current implemented rev1 foundation:

- rev1a: dormant contained-execution seams in the launcher for isolated log-root control, target-script override, and optional diagnostics or voice no-op seams
- rev1b: first reusable contained harness runner covering healthy runs, failed runs with no prior history, and failed runs with matching prior failure history
- rev1c: harness scenario expansion covering varied prior failure history, success-only prior history, malformed history input, and hostile or unreadable history storage fallback

Current guarantees remain unchanged:

- harness execution remains external validation tooling rather than runtime-control behavior
- launcher and runtime behavior remain unchanged in production mode when seams are unset
- historical context remains non-authoritative
- advisory output remains non-binding

## v1.8.0 Implemented Rev2a Strict Fingerprint Contract

`FB-012` rev2a is now implemented as the first strict failure-fingerprint contract slice for `v1.8.0`.

Implemented rev2a state:

- fingerprints apply only to finalized failure records
- success records keep empty `failure_fingerprint` values
- failure records require non-empty normalized `failure_fingerprint` values
- initial recurrence grouping uses strict equality on the normalized full fingerprint
- success records and empty fingerprints are excluded from recurrence grouping

Current guarantees remain unchanged:

- no fuzzy matching
- no confidence or provenance semantics
- no reinterpretation of recurrence as runtime policy significance
- no coupling of historical recurrence to runtime-control behavior

## v1.8.0 Implemented Rev2b Deterministic Stability Model

`FB-012` rev2b is now implemented as the deterministic recent-history stability-model slice for `v1.8.0`.

Implemented rev2b state:

- stability is computed only from recurrence-eligible finalized failure records
- the recent-history window is explicitly the most recent `5` eligible finalized failure records
- `stable` means a recent window containing `0` or `1` unique normalized full fingerprints
- `varied` means a recent window containing more than `1` unique normalized full fingerprints
- success records, empty fingerprints, malformed lines, contract-invalid records, and hostile or unreadable history cases are excluded from stability calculations

Current guarantees remain unchanged:

- no fuzzy matching
- no confidence or provenance semantics
- no advisory redesign
- no reinterpretation of stability as runtime policy significance
- no coupling of historical stability to runtime-control behavior

Taken together, `FB-012` rev2a and rev2b complete the failure fingerprint and recurrence model track for `v1.8.0` without changing runtime policy.

## v1.8.0 Implemented Rev3a Provenance-First Advisory Semantics

`FB-013` rev3a is now implemented as the provenance-first advisory semantics slice for `v1.8.0`.

Implemented rev3a state:

- diagnostics-facing output now explicitly distinguishes current-run truth, prior finalized historical context, and advisory inference
- advisory inference remains non-binding and non-authoritative
- confidence remains absent from surfaced operator-facing output in this first slice
- crash-report and incident-summary truth surfaces remain free of historical or advisory provenance language

Current guarantees remain unchanged:

- no surfaced confidence scoring
- no interpretation of confidence as severity, urgency, escalation level, recommendation strength, or runtime-policy permission
- no coupling of advisory semantics to runtime-control behavior
- no authority expansion beyond the existing diagnostics-only advisory boundary

`FB-013` remains open after rev3a pending the next narrow decision on whether a definition-only confidence-semantics slice is still needed for `v1.8.0`.

## v1.8.0 Planned Rev3b Internal Confidence Semantics

`FB-013` rev3b should remain a definition-only and internal confidence-semantics pass.

That narrow confidence slice should:

- define confidence only as evidence-directness or evidence-quality for advisory inference
- keep confidence absent from surfaced operator-facing output

That narrow confidence slice must not:

- interpret confidence as severity, urgency, escalation level, recommendation strength, predictive correctness, runtime-policy permission, or authority over current-run truth
- couple confidence semantics to runtime-control behavior
- expand authority beyond the existing diagnostics-only advisory boundary
- add confidence, historical, or advisory language to crash-report or incident-summary truth surfaces
- redesign advisory output beyond what is needed to preserve the internal-only confidence boundary

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
