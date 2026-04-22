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
- WS-2 and WS-3 remain planned only.
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

Seam 2: HUD surface and visibility boundary framing

- Goal: define when a monitoring or performance signal may become user-visible and what surface classes are candidates.
- Scope: desktop/HUD/tray/overlay framing, visibility ownership, and non-invasive display constraints.
- Non-Includes: no UI implementation, no layout, no live overlays, no notification system, no hotkeys, no timers, and no runtime rendering.

Seam 3: validation and admission contract for later implementation seams

- Goal: define the proof required before any monitoring, thermal, or HUD runtime seam can begin.
- Scope: cleanup expectations, non-invasive behavior, performance overhead proof, no-persistence-by-default checks, and UTS classification rules.
- Non-Includes: no validation helper creation unless a later implementation seam makes it necessary, no hardware-dependent test matrix, and no release execution.

## Active Seam

Active seam: None after WS-1 completion.

- WS-1 Status: Completed / executed.
- WS-1 Boundary: architecture-only source categories, ownership vocabulary, Nexus-owned versus external/system-owned responsibilities, and explicit unknowns for later admission.
- WS-1 Non-Includes: no telemetry collection, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, tray/taskbar work, plugin integration, installer changes, or release packaging.
- WS-2 Status: Planned only; next legal Workstream seam when explicitly activated.
- WS-3 Status: Planned only.

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
- Continue/Stop Decision: Stop after WS-1. WS-2 remains the next planned seam and must be explicitly activated before lifecycle or trust/safety boundary work begins.

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
- Stop if monitoring/HUD scope drifts into external trigger integration, saved-action execution, installer behavior, release packaging, or unrelated governance expansion.
- Stop if validator enforcement would require broad redesign outside current Workstream truth.

## Exit Criteria

- WS-1 monitoring and thermal source map plus ownership vocabulary is complete and durably recorded.
- WS-2 HUD surface and visibility boundary framing is either completed or deliberately deferred with documented rationale.
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
