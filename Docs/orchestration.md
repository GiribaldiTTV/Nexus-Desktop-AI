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

## v1.7.0 Implemented State (rev1-rev6)

### rev1
- recorder-only historical memory groundwork
- versioned per-run history records written only after finalized run completion

### rev2
- recorder validation before write
- storage-path hardening and fail-safe fallback

### rev3
- read-only internal summarizer groundwork
- malformed-line-safe loading
- simple recurrence and stability summarization using recorded failure fingerprints

### rev4
- diagnostics-only historical context on failed runs
- historical context derived only from prior finalized failure history

### rev5
- diagnostics-only historical advisory hints on failed runs
- advisory wording remains explicitly historical, non-authoritative, and non-binding

### rev6
- source-of-truth stabilization and doc/backlog sync
- no launcher behavior change required from the audit

## Current v1.7.0 Guarantees

- no readback into runtime behavior
- no retry, escalation, threshold, or classification changes
- no diagnostics trigger changes
- no changes to `v1.6.0` summary structure or triage guidance
- historical context remains clearly separate from current-run truth
- advisory output remains clearly separate from both current-run truth and runtime control
- historical context and advisory wording remain diagnostics `TRACE` surfaces; crash reports and incident summaries remain current-run truth surfaces
- if history is missing, malformed, unreadable, or hostile, the launcher degrades cleanly to finalized `v1.6.0` behavior plus existing fail-safe history handling

## Final State (v1.7.0)

`v1.7.0` is complete as a conservative historical-memory and diagnostics-only advisory layer.

No contradictions remain between:

- runtime log truth
- crash report truth
- diagnostics `TRACE` historical context
- diagnostics `TRACE` advisory wording
- documented version boundaries

## v1.8.0 Validation-First Boundary

`v1.8.0` should begin as a validation-first phase for the historical-intelligence layer introduced in `v1.7.0`.

The safest first target is:

- `FB-014` multi-run orchestration regression harness

Allowed in early `v1.8.0`:

- repeatable multi-run verification of history recording
- recurrence and fallback validation across repeated launches
- diagnostics historical-context verification
- diagnostics advisory-surface verification

Not allowed in early `v1.8.0`:

- retry or escalation changes
- threshold or classification changes
- diagnostics-trigger changes
- confidence scoring
- broader advisory expansion
- historical content added to crash-report or incident-summary truth surfaces
- readback from history into runtime behavior

Future `v1.8.0` work may formalize recurrence and provenance semantics only after validation infrastructure is in place.

## v1.8.0 Implemented Rev1 State

`FB-014` rev1 now exists as external validation tooling around the historical-intelligence layer.

Implemented rev1 state:

- rev1a added dormant launcher seams for contained execution without touching the live production logs tree
- rev1b added the first reusable contained harness runner
- rev1c expanded that runner to cover baseline prior-history and fallback scenarios

This implemented rev1 state does not alter orchestration behavior.
It validates the existing recorder, summarizer, diagnostics-context, and diagnostics-advisory surfaces from outside the runtime-control path.

## Later Orchestration Topics

Examples of later orchestration topics:

- retry limits
- diagnostics escalation thresholds
- cooldown timing
- differentiated handling for repeated crash vs repeated stall
- longer-term recovery policy tuning

These should be handled as dedicated revisions, not mixed into unrelated work.

## FB-003 Rev1 Baseline and Implemented State

`FB-003` began with a `rev1a` policy-contract pass and now includes an implemented `rev1b` launcher behavior slice.

The `rev1a` baseline defines when retries stop adding value and when the launcher should enter the existing diagnostics completion path, using current launcher-owned failure classes and recovery outcomes rather than new UI or new control surfaces.

Rev1a should stay grounded in the current high-signal desktop-phase evidence classes already recognized by the launcher:

- repeated `STARTUP_ABORT` outcomes
- repeated identical crash outcomes

Rev1a may define:

- when those repeated failure classes should be treated as retry-exhausting evidence
- that retry exhaustion stops further recovery attempts for the current run
- that the launcher then enters the existing diagnostics completion path rather than continuing silent recovery
- that this transition reuses the current diagnostics completion surfaces rather than redesigning diagnostics behavior

Implemented `rev1b` state:

- repeated `STARTUP_ABORT` exhaustion now behaves as a first-class terminal outcome
- repeated identical crash exhaustion now behaves as a first-class terminal outcome
- actual attempts used now propagate into terminal finalization and runtime summary output
- terminal crash-report wording now reflects the real end reason instead of generic max-attempt framing
- the existing diagnostics completion path is reused unchanged

`FB-003` must not define yet:

- mixed failure-sequence policy such as crash-then-abort or abort-then-crash
- threshold retuning
- classification redesign
- diagnostics UI changes
- summary or triage wording changes
- cooldown redesign

Mixed failure-sequence policy remains separate `FB-002` work and must not be pulled into `FB-003` rev1a.

## FB-002 Rev1 Baseline and Current Launcher State

`FB-002` began with a `rev1a` policy-contract pass.

The `rev1a` baseline defines the conservative policy meaning of cross-kind mixed failure sequences without retuning thresholds, redesigning classification broadly, or reopening the terminal classes already handled by `FB-003`.

Rev1a should stay limited to the currently recognized cross-kind crash and abort transitions:

- `CRASH_TO_STARTUP_ABORT`
- `STARTUP_ABORT_TO_CRASH`

Rev1a should treat those mixed sequences as weaker evidence than the `FB-003` terminal classes:

- repeated `STARTUP_ABORT` outcomes
- repeated identical crash outcomes

Rev1a may define:

- that a first observed `CRASH_TO_STARTUP_ABORT` or `STARTUP_ABORT_TO_CRASH` sequence remains non-terminal
- that these mixed sequences may continue contributing to instability labeling
- that these mixed sequences may continue contributing to diagnostics-priority and attempt-pattern reporting
- that these mixed sequences do not become a new early-exhaustion trigger in rev1a
- that the launcher should preserve conservative retry continuation unless stronger existing terminal evidence appears

Current launcher state already satisfies this conservative `rev1a` baseline:

- `CRASH_TO_STARTUP_ABORT` and `STARTUP_ABORT_TO_CRASH` are recognized as mixed cross-kind sequences
- first-observed cross-kind mixed sequences remain non-terminal
- these mixed sequences continue feeding instability labeling
- these mixed sequences continue feeding diagnostics-priority and attempt-pattern reporting
- these mixed sequences do not act as a new early-exhaustion trigger
- conservative retry continuation remains in place unless an existing `FB-003` terminal class is reached

Rev1a must not define yet:

- threshold retuning
- new early-escalation thresholds for mixed sequences
- broader varied-failure policy beyond the two cross-kind crash and abort transitions above
- classification redesign outside this mixed-sequence clarification
- diagnostics UI changes
- summary or triage redesign
- cooldown redesign

`FB-002` remains intentionally separate from `FB-003`.
It may describe how mixed sequences relate to instability reporting and diagnostics entry, but it must not weaken or replace the existing `FB-003` terminal classes.
