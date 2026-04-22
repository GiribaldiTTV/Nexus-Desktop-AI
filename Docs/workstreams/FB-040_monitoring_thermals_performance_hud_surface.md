# FB-040 Monitoring, Thermals, And Performance HUD Surface

## ID And Title

- ID: `FB-040`
- Title: `Monitoring, thermals, and performance HUD surface`

## Record State

- `Promoted`

## Status

- `Active (Workstream)`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-040-monitoring-thermals-performance-hud-surface`

## Current Phase

- Phase: `Workstream`

## Phase Status

- `Active Branch`
- Branch Readiness exit is complete and FB-040 Workstream is admitted.
- FB-039 is released and closed in `v1.5.0-prebeta`.
- FB-039 release debt is clear.
- Latest public prerelease truth is `v1.5.0-prebeta`.
- WS-1 monitoring and thermal source map plus ownership vocabulary is complete and durably recorded.
- WS-2 lifecycle and trust/safety boundary framing for monitoring inputs is complete and durably recorded.
- WS-3 validation and admission contract for future runtime monitoring seams is complete and durably recorded.
- Initial architecture-only Workstream seam sequence is complete and ready for Hardening evaluation.
- The prior stop-after-WS-1 posture is classified as seam-continuation governance drift and is superseded by the completed WS-1 through WS-3 chain.
- No FB-040 runtime, HUD, telemetry, thermal, monitoring, plugin, installer, or settings implementation has started.

## Branch Class

- `implementation`

## Blockers

- None after Branch Readiness admission/update validation.

## Entry Basis

- `main` was aligned with `origin/main` before `feature/fb-040-monitoring-thermals-performance-hud-surface` was admitted.
- FB-039 release execution completed as `v1.5.0-prebeta`.
- Release debt is clear after carried-forward canon repair in Branch Readiness.
- The active branch exists because FB-039 release/post-release drift was discovered after merge and must be repaired on the next active Branch Readiness surface before implementation.
- FB-040 was the selected successor in FB-039 merge-target canon.
- Branch Readiness completed with the branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and initial Workstream seam sequence recorded.

## Branch Objective

- Define the branch authority and first execution boundaries for monitoring, thermals, and performance HUD surfaces.
- Keep FB-040 focused on local monitoring/HUD product boundaries rather than external trigger integration, saved-action execution, installer behavior, release packaging, or generic telemetry sprawl.
- Preserve the completed carried-forward FB-039 post-release canon repair while FB-040 begins architecture-first Workstream seams.

## Target End-State

- FB-040 has a coherent Workstream scaffold and an admitted first seam for architecture-first source mapping.
- Monitoring, thermal, and performance HUD source categories are separated from later telemetry plumbing or UI implementation.
- First Workstream seams can begin with architecture/source-map work rather than runtime collection, HUD rendering, persistence, plugin integration, or installer changes.
- FB-039 remains closed/released and release debt remains clear.

## Expected Seam Families And Risk Classes

- Source-map and ownership seam family; risk class: architecture/governance because monitoring data origins, ownership, and display authority must be defined before implementation.
- Privacy/safety and performance-boundary seam family; risk class: product/safety because monitoring can expose local system state and must not create noisy, privileged, or always-on behavior by accident.
- HUD surface framing seam family; risk class: desktop/UI because future overlays or status surfaces can affect visibility, focus, readability, and operator trust.
- Validation/admission seam family; risk class: validator/governance because later implementation must prove cleanup, non-invasive behavior, and no unrelated runtime expansion.

## User Test Summary Strategy

- The initial Workstream seams have no manual `UTS` artifact because no user-facing FB-040 behavior exists yet.
- If later Workstream seams add a user-visible HUD, tray, overlay, shortcut, settings, or monitoring display path, the workstream must add an exact `## User Test Summary` artifact before Live Validation.
- If FB-040 remains architecture-only or internal-only in a later phase, any UTS waiver must include explicit waiver reasons in the canonical `## User Test Summary` section.

## Later-Phase Expectations

- Workstream must begin with source-map and ownership vocabulary before any runtime collection or HUD UI work.
- Hardening must pressure-test cleanup, no-persistence-by-default behavior, performance overhead, and boundary regressions if implementation is admitted.
- Live Validation must classify whether the milestone is user-facing and must include shortcut/HUD/manual validation only if an operator-visible surface exists.
- PR Readiness must prove merge-target canon, release target semantics, next-workstream selection, helper retention, and branch-creation gate truth before PR creation and validation.
- Release Readiness remains analysis-only and file-frozen.

## Initial Workstream Seam Sequence

Seam 1: monitoring and thermal source map plus ownership vocabulary

- Status: Completed.
- Goal: define candidate monitoring data origins, ownership terms, and product boundaries for CPU/GPU thermals, performance status, and HUD-facing signals.
- Scope: architecture-only source categories, Nexus-owned versus external/system-owned responsibility, naming vocabulary, and explicit unknowns for later admission.
- Non-Includes: no telemetry collection, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, tray/taskbar work, plugin integration, installer changes, or release packaging.

Seam 2: lifecycle and trust/safety boundary framing for monitoring inputs

- Status: Completed.
- Goal: define the lifecycle, trust, safety, data-state, and failure-handling boundaries for candidate monitoring inputs before any source collection, adapter, runtime polling, or display surface is admitted.
- Scope: monitoring input lifecycle states, monitoring data states, trust/safety ownership, missing or conflicting telemetry handling, and non-invasive interpretation rules.
- Non-Includes: no telemetry collection, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, tray/taskbar work, plugin integration, installer changes, or release packaging.

Seam 3: validation and admission contract for later implementation seams

- Status: Completed.
- Goal: define the proof required before any monitoring, thermal, or HUD runtime seam can begin.
- Scope: cleanup expectations, non-invasive behavior, performance overhead proof, no-persistence-by-default checks, and UTS classification rules.
- Non-Includes: no validation helper creation unless a later implementation seam makes it necessary, no hardware-dependent test matrix, and no release execution.

## Active Seam

Active seam: None after WS-3 completion.

- WS-1 Status: Completed / executed.
- WS-1 Boundary: architecture-only source categories, ownership vocabulary, Nexus-owned versus external/system-owned responsibilities, and explicit unknowns for later admission.
- WS-1 Non-Includes: no telemetry collection, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, tray/taskbar work, plugin integration, installer changes, or release packaging.
- WS-2 Status: Completed / executed.
- WS-2 Boundary: architecture-only lifecycle states, data states, trust/safety ownership, and missing/conflicting telemetry handling.
- WS-2 Non-Includes: no telemetry collection, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, tray/taskbar work, plugin integration, installer changes, or release packaging.
- WS-3 Status: Completed / executed.
- WS-3 Boundary: architecture-only validation/admission criteria for future runtime monitoring, thermal, and HUD seams.
- WS-3 Non-Includes: no validation helper creation, hardware-dependent test matrix, runtime collector, source adapter, HUD implementation, release packaging, or phase advancement execution.

## WS-1 Execution Record

WS-1 defined the monitoring and thermal source map and the ownership vocabulary for future FB-040 seams. This record is architecture-only and does not admit runtime telemetry collection, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, plugin integration, installer work, or release work.

### Monitoring And Thermal Source Map

Candidate source categories:

- Operating-system performance posture: Windows-owned process, memory, CPU, power, and responsiveness signals that may later describe system or app health without requiring hardware control.
- Hardware thermal posture: system-owned or vendor-owned temperature, throttle, fan-state, and thermal-limit signals for CPU, GPU, and storage-class hardware when exposed through supported local APIs or tools.
- GPU performance posture: vendor-owned utilization, memory pressure, encoder/decoder activity, power, temperature, and throttling status that may later support a local GPU-first status surface.
- Nexus runtime self-observation: Nexus-owned process health, startup responsiveness, renderer responsiveness, validation markers, and cleanup state that can describe Nexus behavior without reading external hardware sensors.
- Desktop session posture: OS-owned foreground/background, power-mode, battery/AC, display/session, and degraded-availability context that may explain whether monitoring data should be visible or suppressed.
- Future plugin-fed monitoring origins: later plugin-owned or companion-app-owned signals that may be considered only after lifecycle, trust/safety, and validation/admission seams define their boundaries.
- Explicitly unsupported origins for this milestone: cloud telemetry, remote device telemetry, UI scraping of third-party monitoring tools, driver installation, kernel-level probing, fan/overclock control, persistent surveillance, and any source that requires Nexus to own hardware-control authority.

Source category status:

- Candidate only: all source categories are planning inputs for future admission.
- No source category is implemented by WS-1.
- No source category is approved for collection until a later seam defines lifecycle, trust/safety, validation, cleanup, and user-facing behavior.

### Ownership Vocabulary

- Monitoring source: a local origin that may expose performance, thermal, availability, or responsiveness information.
- Thermal source: a monitoring source whose primary value is temperature, throttle, fan-state, or thermal-limit posture.
- Performance signal: a point-in-time or derived description of load, pressure, throughput, responsiveness, or resource availability.
- Telemetry sample: a future bounded read from an admitted source; WS-1 defines the term but does not authorize sampling.
- Sensor origin: the system, vendor, runtime, plugin, or companion-owned surface that produces a signal before Nexus interprets it.
- Source adapter: a future Nexus-owned boundary object that may translate one admitted origin into normalized monitoring language.
- Nexus monitoring intake: the future Nexus-owned conceptual entry point where admitted monitoring signals would be classified before any display or action.
- Derived status: a Nexus-owned interpretation of one or more admitted signals, such as healthy, degraded, unavailable, stale, or unknown.
- HUD candidate signal: a derived status or admitted signal that may later be considered for user-visible display.
- Freshness: the time-validity expectation for a signal or derived status.
- Confidence: the trust level attached to a signal after source ownership, availability, and interpretation limits are known.
- Availability state: whether a source or signal is available, unavailable, partial, stale, invalid, or unknown.
- External-owned surface: a driver, OS, vendor tool, plugin, companion app, or hardware-facing component that Nexus does not control.
- Nexus-owned surface: the in-product boundary for classification, normalization, display admission, validation evidence, cleanup, and user-facing explanation.
- User-visible monitoring surface: a future HUD, overlay, tray, settings, or status path that presents an admitted signal to the operator.

### Ownership Boundaries

External, OS, vendor, plugin, or companion systems own:

- raw sensor production
- driver and hardware access
- source permissions and availability
- source-specific accuracy claims
- vendor-specific terminology and failure behavior
- hardware control, fan control, clock control, and power-policy control

Nexus owns only after a source is admitted by later seams:

- source classification and naming inside Nexus
- validation of whether a source is allowed to enter the product boundary
- normalization into Nexus monitoring vocabulary
- stale, partial, invalid, unavailable, and unknown-state handling
- deciding whether a signal can become a HUD candidate signal
- user-facing explanation, if a display surface is later admitted
- cleanup, no-persistence-by-default behavior, and non-invasive runtime posture

Nexus does not own:

- installing drivers or vendor tools
- scraping third-party monitoring UI
- changing hardware clocks, fan curves, power limits, or thermal policies
- collecting remote/cloud telemetry
- guaranteeing hardware sensor accuracy
- treating plugin-fed monitoring as trusted without future trust/safety admission

### WS-1 Continuation Decision

- WS-1 Result: Complete.
- Validation Layer: documentation and governance validation only.
- Cleanup: no programs, helper processes, windows, temporary files, telemetry collectors, probes, or runtime artifacts were created.
- User Test Summary Applicability: not applicable for WS-1 because it adds architecture-only planning and no user-visible behavior.
- Continue/Stop Decision: the original stop after WS-1 is superseded and classified as seam-continuation governance drift because no canon-valid blocker, phase boundary, stop-loss trigger, or `Single-Seam Fallback` required stopping. WS-2 was the required next Workstream continuation candidate after this governance repair and is now complete.

## Seam Continuation Governance Repair

- Governance Drift Found: Yes.
- Drift Type: green Workstream seam stopped without a canon-valid continuation blocker.
- Root Cause: source-of-truth required a continue-or-stop decision but did not make safe next-seam continuation the default after a green seam.
- Corrected Rule: `Next-Seam Continuation Required` is now the default after a green seam in a valid bounded multi-seam workflow.
- Recurrence Prevention: prompt-named seams are entry seams, not terminal boundaries; stopping after a green seam requires a recorded blocker, phase boundary, stop-loss trigger, or `Single-Seam Fallback`.

## WS-2 Execution Record

WS-2 defines lifecycle and trust/safety boundary framing for monitoring inputs. This record is architecture-only and does not admit runtime telemetry collection, source adapters, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, plugin integration, installer work, or release work.

### Monitoring Input Lifecycle Framing

- Startup: monitoring inputs are not assumed available during startup. Future runtime seams must treat source discovery, delayed availability, permission gaps, and missing vendor surfaces as normal startup conditions rather than failures that block Nexus startup.
- Steady-State: monitoring inputs may be considered steady-state only after a future admitted source can provide current, bounded, provenance-labeled data inside its declared freshness and confidence expectations.
- Degradation: monitoring inputs enter degradation when a source becomes partial, stale, contradictory, slow, permission-limited, or otherwise unable to support confident interpretation. Degradation must favor conservative status language rather than alarmist or overconfident health claims.
- Recovery: monitoring inputs recover only when the future admitted source again produces current data that satisfies its declared provenance, freshness, and confidence requirements. Recovery must be explicit and must not infer health from silence.

### Monitoring Data States

- Valid: data is current enough for its declared freshness window, comes from an admitted source, and can be interpreted inside the source's documented confidence limits.
- Invalid: data is malformed, outside the source's expected shape, internally impossible, or known to violate the admitted source contract.
- Stale: data was once valid but is older than the declared freshness expectation for the future admitted source.
- Partial: data covers only part of the expected source surface, such as CPU without GPU, temperature without throttle state, or Nexus runtime responsiveness without OS performance context.
- Unavailable: the source, permission, vendor surface, operating-system path, or plugin-fed origin is not available to Nexus at the time of interpretation.
- Unknown: Nexus lacks enough admitted evidence to classify the state as valid, invalid, stale, partial, or unavailable.

### Trust And Safety Boundary Rules

- Raw monitoring inputs are not execution authority. A source can inform a future derived status only after a later seam admits the source, declares provenance, and proves validation behavior.
- External-owned surfaces retain authority over raw sensor production, source availability, source-specific accuracy claims, driver behavior, and hardware access.
- Nexus-owned surfaces may classify, normalize, explain, suppress, or display admitted inputs, but must not claim hardware-control authority.
- Future plugin-fed monitoring input is conditionally admissible only after lifecycle, trust/safety, validation, and cleanup contracts define the plugin's provenance and failure behavior.
- User-visible warnings, HUD status, tray status, or overlay presentation must not be produced directly from raw source data without a later display-admission seam.
- Monitoring must remain non-invasive by default: no driver installation, no hardware control, no fan or clock changes, no kernel probing, no remote/cloud telemetry, and no persistent surveillance behavior.
- Missing, stale, partial, or conflicting telemetry must degrade the confidence of Nexus interpretation rather than trigger hidden execution, automatic remediation, or hardware policy changes.

### Conflicting Or Missing Telemetry Handling

- If two admitted sources conflict, Nexus must preserve provenance and report conservative confidence rather than silently choosing the more dramatic or more convenient value.
- If one source is missing and another is present, Nexus may later derive a partial status only if the future source contract says that partial interpretation is meaningful.
- If all relevant sources are unavailable or unknown, Nexus must represent monitoring status as unavailable or unknown rather than healthy.
- If a source becomes stale, Nexus must prefer stale/degraded language over continuing to display the last value as current.
- If a source reports values outside plausible or contract-defined bounds, Nexus must classify the input as invalid and prevent it from becoming display-ready without later validation rules.

### WS-2 Continuation Decision

- WS-2 Result: Complete.
- Validation Layer: documentation and governance validation only.
- Cleanup: no programs, helper processes, windows, temporary files, telemetry collectors, probes, or runtime artifacts were created.
- User Test Summary Applicability: not applicable for WS-2 because it adds architecture-only planning and no user-visible behavior.
- Continue/Stop Decision: continue to WS-3 under `Next-Seam Continuation Required` if documentation and governance validation pass, because WS-3 remains in the same workstream, phase, branch class, risk envelope, and architecture-only subsystem family.

## WS-3 Execution Record

WS-3 defines the validation and admission contract future runtime monitoring seams must satisfy before FB-040 can move from architecture into implementation. This record is architecture/governance-only and does not create validators, helpers, runtime collectors, source adapters, HUD surfaces, or hardware-dependent test matrices.

### Future Runtime Admission Gate

Before any future runtime monitoring seam may begin, the seam must explicitly define:

- the admitted monitoring source or source family
- the owning external, OS, vendor, plugin, companion, or Nexus surface
- the source's provenance, freshness, confidence, and availability expectations
- the exact data states it can produce: valid, invalid, stale, partial, unavailable, or unknown
- the lifecycle state it participates in: startup, steady-state, degradation, or recovery
- the Nexus-owned interpretation boundary and the external-owned raw-source boundary
- the affected files and modules
- the validation surface
- cleanup expectations
- User Test Summary applicability

### Validation Contract For Future Runtime Seams

- Baseline governance validation remains `python dev\orin_branch_governance_validation.py` plus `git diff --check` for docs/canon changes.
- Future source-adapter or intake code must add the smallest reliable repo-side validation needed to prove healthy-path, failure-path, stale-data, unavailable-source, partial-data, and cleanup behavior.
- Durable root `dev/` validators or helpers must route through `Docs/validation_helper_registry.md` before closeout-grade proof depends on them.
- Hardware-specific or vendor-specific proof must stay optional and bounded unless a future seam explicitly admits that dependency.
- User-facing HUD, tray, overlay, settings, or shortcut behavior must add the exact `## User Test Summary` artifact and later Live Validation shortcut gate required by repo governance.

### Cleanup And Non-Invasive Requirements

- Future runtime seams must default to no persistence, no autorun collection, no hidden background polling, and no hardware-control behavior unless a later authority record explicitly admits a narrower exception.
- Runtime validation must prove created collectors, timers, subscriptions, processes, windows, temporary files, or probe artifacts are stopped or removed after the pass.
- Source failures must degrade to documented state handling rather than forcing Nexus startup failure, hidden remediation, or unrelated runtime changes.
- Missing or conflicting telemetry must not produce display-ready health claims without an admitted confidence model.

### WS-3 Completion Decision

- WS-3 Result: Complete.
- Validation Layer: documentation and governance validation only.
- Cleanup: no programs, helper processes, windows, temporary files, telemetry collectors, probes, or runtime artifacts were created.
- User Test Summary Applicability: not applicable for WS-3 because it adds architecture-only admission rules and no user-visible behavior.
- Continue/Stop Decision: stop at the Workstream phase boundary because the approved initial WS-1 through WS-3 architecture sequence is complete. The next legal phase is `Hardening`.

Completed Branch Readiness seam history:

- BR-1: repaired carried-forward post-release canon drift from FB-039.
- BR-2: repaired carried-forward version-governance drift and validator expectations.
- BR-3: reevaluated repo truth and admitted FB-040 to Branch Readiness.
- GOV-1 through GOV-3: implemented and aligned the canonical seam workflow contract.
- GOV-I1 through GOV-I3: separated ChatGPT loader/prompt responsibilities from Codex execution authority.
- GOV-O1 through GOV-O3: standardized operator-facing PR Readiness and Release Readiness copy-block output.

## Validation Contract

- `python dev\orin_branch_governance_validation.py`
- `git diff --check`
- `git status --short --branch`
- The validator must fail if latest public prerelease canon trails the latest local pre-Beta tag.
- The validator must fail if a workstream whose release tag exists remains represented as merged-unreleased release debt instead of closed/released.
- Workstream admission is not clean unless FB-039 is closed/released, release debt is clear, FB-040 is active/promoted, and this authority record contains the required Workstream phase state and active WS-1 seam.
- Workstream validation remains architecture/documentation-only until a later seam explicitly admits runtime or HUD implementation.

## Stop Conditions

- Stop if FB-039 release debt, stale latest public prerelease truth, or merged-unreleased state returns.
- Stop if FB-040 implementation work begins outside an admitted Workstream seam.
- Stop if WS-1 drifts into telemetry collection, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, tray/taskbar work, plugin integration, installer changes, or release packaging.
- Stop if WS-2 or WS-3 drift from architecture/admission framing into runtime telemetry collection, source-adapter implementation, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, tray/taskbar work, plugin integration, installer changes, or release packaging.
- Stop if monitoring/HUD scope drifts into external trigger integration, saved-action execution, installer behavior, release packaging, or unrelated governance expansion.
- Stop if validator enforcement would require broad redesign outside current Workstream truth.

## Exit Criteria

- WS-1 monitoring and thermal source map plus ownership vocabulary is complete and durably recorded.
- WS-2 lifecycle and trust/safety boundary framing for monitoring inputs is complete and durably recorded.
- WS-3 validation and admission contract for later implementation seams is complete before any runtime monitoring or HUD implementation seam begins.
- Workstream evidence and User Test Summary obligations are current for the completed scope.
- Direct validation is green.
- No unresolved same-slice correctness gap remains.

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Hardening` after Workstream exit criteria are met.

## Governance Drift Audit

Governance Drift Found: Yes, repaired during FB-040 Branch Readiness.

- Drift Type: carried-forward post-release canon drift and version-governance validator gap.
- Finding: FB-039 had been released as `v1.5.0-prebeta`, but durable canon still recorded latest public prerelease `v1.4.1-prebeta`, kept FB-039 as merged-unreleased release debt, and treated FB-040 as selected-only / not-created after the FB-040 branch existed.
- Repair: latest public prerelease truth is advanced to `v1.5.0-prebeta`, FB-039 is closed/released, release debt is cleared, FB-040 was admitted as the active Branch Readiness workstream, and validator coverage is extended so the latest released tag cannot leave its owner in merged-unreleased state.
- Governance Drift Found After Repair: No unresolved drift remains after validation.
