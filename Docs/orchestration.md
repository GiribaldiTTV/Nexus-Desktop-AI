# Jarvis Orchestration

## Purpose

This document captures the orchestration-specific philosophy and behavior of the Jarvis launcher stack.

It exists so future revisions can reference:

- how startup is classified
- how control is applied
- how recovery is routed
- what order orchestration capabilities should be built in

## Current Startup Path

`launch_jarvis_desktop.vbs`
-> `jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py`

## Orchestration Evolution (rev1-rev9)

The orchestration system was built in stages:

1. Separate production from test harness
2. Add renderer lifecycle instrumentation
3. Add launcher observation
4. Add slow-start and stall classification
5. Add cooperative abort control
6. Add abort classification
7. Route abort into recovery
8. Add automatic abort on confirmed stall
9. Add repeated consecutive `STARTUP_ABORT` escalation

This sequence must not be skipped in future systems.

New systems should follow:

Observability -> Classification -> Control -> Outcome -> Behavior

## Marker Glossary

- `STARTUP_OBSERVE_BEGIN` -> launcher began watching the current attempt for startup readiness
- `STARTUP_READY_OBSERVED` -> launcher confirmed the renderer reached readiness
- `STARTUP_READY_NOT_OBSERVED_WITHIN_WINDOW` -> startup is slower than expected
- `STARTUP_READY_STALL_CONFIRMED` -> startup still has not reached readiness at the later stall deadline
- `STARTUP_ABORT_REQUESTED_ON_CONFIRMED_STALL` -> launcher requested the cooperative startup abort signal
- `STARTUP_ABORT_OBSERVED` -> launcher observed the renderer's startup-abort milestone
- `STARTUP_ABORT_COMPLETE` -> launcher completed the abort-specific cleanup and control-flow handoff
- `NORMAL_EXIT_COMPLETE` -> launcher completed a healthy normal-exit path

## Startup Observation

Launcher monitors:

- renderer process spawn
- readiness milestones
- time to readiness
- renderer process state

## Stall Detection

Two-stage system:

1. Slow warning (early threshold)
2. Confirmed stall (later threshold)

## Threshold Guidance

Current launcher thresholds are conservative stabilization values for the desktop startup phase.

- The early warning threshold is meant to detect "slower than expected"
- The later stall threshold is meant to detect "slow enough to justify cooperative action"

These values should be tuned from observed evidence, not guesswork.
Future boot or startup phases must not automatically inherit the desktop-phase thresholds.

## Stall Response (Current)

On confirmed stall:

- Request cooperative abort once
- Do not hard kill
- Continue observing
- Let existing abort classification and recovery routing handle the outcome

## Abort Handling

When renderer aborts during startup:

- Renderer emits `RENDERER_MAIN|STARTUP_ABORTED`
- Launcher classifies the abort distinctly
- Launcher treats the attempt as a startup failure outcome
- Launcher routes that outcome into recovery flow

## Recovery Flow

- Attempt restart
- Track attempt index
- Maintain logs and state markers
- Preserve cleanup of transient control and status artifacts

## Behavior Philosophy

- Prefer cooperative control over forced control
- Prefer classification before action
- Prefer minimal intervention first
- Avoid aggressive recovery unless proven necessary
- Recovery policy should be staged and justified by observed behavior

## Current Boundaries

The launcher is responsible for:

- observation
- classification
- control decisions
- recovery routing

The renderer is responsible for:

- lifecycle milestones
- UI ownership
- cooperative response to launcher control signals
- clean shutdown behavior

## v1.6.0 Evolution (rev10-rev24)

### rev10-rev12
- Introduced cooperative startup abort
- Added threshold-based early escalation
- Established retry and recovery control boundaries

### rev13-rev17
- Added mixed-pattern classification
- Implemented attempt-pattern summaries
- Introduced failure stability signal
- Fixed classification correctness

### rev18-rev19
- Surfaced instability into `diagnostics_status`
- Aligned triage guidance with stability

### rev20-rev22
- Established diagnostics parity across runtime and crash surfaces
- Added instability end-reason classification
- Added diagnostics priority signal

### rev23
- Fixed mixed crash classification inconsistency
- Aligned classifier with the summary layer

### rev24
- Normalized incident summaries
- Propagated diagnostics priority across all surfaces
- Removed triage wording duplication

## Final State (v1.6.0)

The orchestration system is:

- behaviorally stable
- fully observable
- classification-consistent
- summary-aligned
- diagnostics-aligned
- operator-guided correctly

No contradictions exist between:

- runtime markers
- classification
- summaries
- diagnostics
- triage guidance

## v1.7.0 Boundary Note

`v1.7.0` may introduce historical memory and advisory intelligence, but it may not alter the closed `v1.6.0` runtime control model.

Allowed in `v1.7.0`:

- cross-run outcome recording
- recurrence and stability trend summaries
- diagnostics enrichment using historical context
- advisory recommendations with clear provenance

Not allowed in `v1.7.0`:

- retry changes
- escalation changes
- threshold changes
- classification changes
- diagnostics trigger changes
- instability-driven behavior
- adaptive retry behavior
- boot-level runtime control

Historical memory in `v1.7.0` must remain advisory-only.
If history is missing, unreadable, or corrupt, runtime behavior must degrade cleanly to the finalized `v1.6.0` orchestration behavior.

## Future Expansion (Not Yet Implemented)

Examples of later orchestration topics:

- retry limits
- diagnostics escalation thresholds
- cooldown timing
- differentiated handling for repeated crash vs repeated stall
- longer-term recovery policy tuning

These should be handled as dedicated revisions, not mixed into unrelated work.
