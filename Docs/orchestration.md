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

## Orchestration Evolution (rev1–9)

The orchestration system was built in stages:

1. Separate production from test harness
2. Add renderer lifecycle instrumentation
3. Add launcher observation
4. Add slow-start and stall classification
5. Add cooperative abort control
6. Add abort classification
7. Route abort into recovery
8. Add automatic abort on confirmed stall
9. Add repeated consecutive STARTUP_ABORT escalation

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

## v1.6.0 Evolution (rev10–rev24)

### rev10–12
- Introduced cooperative startup abort
- Added threshold-based early escalation
- Established retry + recovery control boundaries

### rev13–17
- Added mixed-pattern classification
- Implemented attempt-pattern summaries
- Introduced failure stability signal
- Fixed classification correctness (rev17)

### rev18–19
- Surfaced instability into diagnostics_status
- Aligned triage guidance with stability

### rev20–22
- Diagnostics parity across runtime/crash
- Instability end-reason classification
- Diagnostics priority signal

### rev23
- Fixed mixed crash classification inconsistency
- Aligned classifier with summary layer

### rev24
- Normalized incident summaries
- Propagated diagnostics priority across all surfaces
- Removed triage wording duplication

---

## Final State (v1.6.0)

The orchestration system is:

- Behaviorally stable
- Fully observable
- Classification-consistent
- Summary-aligned
- Diagnostics-aligned
- Operator-guided correctly

No contradictions exist between:
- runtime markers
- classification
- summaries
- diagnostics
- triage guidance

## Future Expansion (Not Yet Implemented)

Examples of later orchestration topics:

- retry limits
- diagnostics escalation thresholds
- cooldown timing
- differentiated handling for repeated crash vs repeated stall
- longer-term recovery policy tuning

These should be handled as dedicated revisions, not mixed into unrelated work.
