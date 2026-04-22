# FB-031 Nexus Desktop AI UI/UX Overhaul Planning

## Identity

- ID: `FB-031`
- Title: `Nexus Desktop AI UI/UX overhaul planning`

## Record State

- `Promoted`

## Status

- `Workstream`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-031-nexus-desktop-ai-ui-ux-overhaul-planning`

## Current Phase

- Phase: `Workstream`

## Phase Status

- `Active Branch`
- FB-040 is released and closed in `v1.6.0-prebeta`.
- Release debt is clear.
- FB-031 Workstream is admitted for architecture-only UI/UX source mapping and visual-language ownership planning.
- WS-1 Nexus-era UI/UX source map and visual-language ownership vocabulary is the active execution seam for this pass.

## Branch Class

- `implementation`

## Blockers

None.

## Entry Basis

- `main` was clean and aligned with `origin/main` before this branch was created.
- Live release truth confirms `v1.6.0-prebeta` exists and points at the FB-040 release commit.
- Durable canon still lagged FB-040 released truth, so this branch's first Branch Readiness seam repairs that escaped post-release drift before any FB-031 implementation can begin.
- FB-031 was the selected successor lane in FB-040 merge-target canon and is now the legal active Branch Readiness surface.

## Branch Objective

- Define the Nexus-era UI/UX overhaul planning lane without implementing UI behavior.
- Establish a deliberate source map, visual-language ownership vocabulary, validation contract, and non-goal boundary before any UI, launcher, settings, overlay, tray, or runtime implementation work is admitted.

## Target End-State

- FB-031 has a complete architecture-first UI/UX source map.
- Visual-language ownership vocabulary is explicit enough for later UI implementation seams to avoid piecemeal design drift.
- Lifecycle/state framing and validation/admission contracts are planned as later Workstream seams.
- No product/runtime UI implementation is added during this architecture-only Workstream milestone.

## Scope

- Define the Nexus-era UI/UX source map.
- Define visual-language ownership vocabulary for later implementation seams.
- Preserve explicit non-goals so future UI, launcher, settings, tray/taskbar, overlay, HUD, shortcut, voice, plugin, installer, or runtime work is admitted deliberately instead of by design drift.

## Non-Goals

- No UI implementation.
- No launcher implementation.
- No settings implementation.
- No tray, taskbar, overlay, HUD, shortcut, voice, plugin, installer, or runtime behavior changes.
- No release execution.
- No FB-031 PR or Release Readiness work.

## Expected Seam Families And Risk Classes

- Source-map and ownership seam family; risk class: product architecture, because UI/UX planning needs one owner map before design details spread across surfaces.
- Visual-language boundary seam family; risk class: desktop/UI, because visual direction can affect discoverability, trust, focus, and operator confidence.
- Validation/admission seam family; risk class: governance/validator, because future UI implementation seams must prove evidence depth, user-facing test coverage, and non-regression before they begin.

## User Test Summary Strategy

- Branch Readiness has no user-facing behavior and no manual UTS artifact requirement.
- If later Workstream seams add or modify user-visible UI, the workstream must add a concrete `## User Test Summary` checklist before Live Validation.
- If FB-031 remains architecture/planning-only through a later phase, any UTS waiver must be recorded in the exact `## User Test Summary` section with waiver reasons.

## Later-Phase Expectations

- Workstream must begin with a source map and visual-language ownership vocabulary before any UI implementation can be proposed.
- Hardening must pressure-test ambiguity, surface ownership, validation coverage, accessibility/readability risk, and implementation-readiness gaps.
- Live Validation must classify whether the milestone is user-facing; if no UI is implemented, waiver reasoning must be explicit and machine-checkable.
- PR Readiness must prove merge-target canon, next-workstream selection, helper posture, User Test Summary status, and clean branch truth before PR creation and live PR validation.

## Initial Workstream Seam Sequence

Seam 1: Nexus-era UI/UX source map and visual-language ownership vocabulary

- Status: Completed.
- Goal: define the candidate UI/UX surfaces, ownership terms, visual-language boundaries, and planning vocabulary for Nexus-era UI/UX overhaul work.
- Scope: architecture-only source map, surface inventory, ownership vocabulary, and explicit non-goals for future implementation admission.
- Non-Includes: no UI code, runtime behavior, launcher changes, settings changes, tray/taskbar changes, overlay/HUD rendering, installer changes, assets, or release work.

Seam 2: UI/UX surface boundary and design-system admission contract

- Status: Planned.
- Goal: define which UI/UX surface classes may be admitted later and what design-system proof is required before implementation.
- Scope: surface categories, user-facing risk classes, accessibility/readability expectations, and implementation-admission evidence.
- Non-Includes: no visual redesign, no component implementation, no CSS/style changes, no interaction runtime, and no release work.

Seam 3: validation and User Test Summary admission contract for future UI implementation seams

- Status: Planned.
- Goal: define the validation, live UI audit, User Test Summary, and cleanup expectations required before future FB-031 implementation seams can begin.
- Scope: evidence requirements, user-facing shortcut/entrypoint classification, manual validation expectations, and validator/harness reuse posture.
- Non-Includes: no helper creation unless a later implementation seam proves one is required, no screenshot capture, no UI implementation, and no release work.

## Active Seam

Active seam: None after WS-1 completion; WS-2 is the next planned Workstream seam.

- BR-1 Status: Completed in this pass; FB-040 post-release canon drift repaired.
- BR-2 Status: Completed in this pass; post-release closure and version-advancement governance/validator hardening added.
- BR-3 Status: Completed in this pass; FB-031 Branch Readiness scaffold established and Workstream admission can be evaluated after validation.
- WS-1 Status: Completed in this pass; Nexus-era UI/UX source map and visual-language ownership vocabulary defined.
- WS-1 Continuation Decision: stop after WS-1 because UI-model / visual-language work is high-risk enough for `Single-Seam Fallback`; continue to WS-2 in a later Workstream pass.

## WS-1 Execution Record

WS-1 is architecture-only. It defines the source map and vocabulary that later UI/UX seams must use before implementation is admitted.

### Nexus-Era UI/UX Source Map

Primary current and candidate UI/UX surface families:

- Runtime shell surface: the first-visible desktop shell, core visualization entry point, window chrome, primary app framing, startup visibility, and any future always-visible Nexus root surface.
- Command and intent surface: command overlay, typed task entry, search/resolution feedback, command interpretation affordances, and future action discovery touchpoints.
- Task creation and authoring surface: Create Custom Task, saved-action authoring, callable-group authoring, task naming, collision feedback, and authoring completion states.
- Confirmation and result surface: confirm/result flows, success/failure readback, retry or blocked-state messaging, and confidence-building status language.
- System access and discoverability surface: tray, taskbar, shortcuts, open/close affordances, return-to-app paths, and visible launch/discoverability cues.
- Settings and configuration surface: Nexus-owned preferences, feature toggles, runtime-safe configuration, and any future operator-controlled customization entry point.
- Status and observability surface: non-invasive status indicators, future monitoring/HUD surfaces, runtime health readback, and system-state presentation boundaries.
- Diagnostics and support surface: recoverable diagnostics, support-report paths, dev toolkit surfaces, validation helpers, and operator-facing error triage language.
- Extension and integration surface: future plugin, external-trigger, companion-tool, and integration management surfaces, limited here to UI/UX planning vocabulary only.
- Historical naming/identity surface: legacy Jarvis terms, Nexus naming, product copy, and migration wording that affects user-facing comprehension.

### Visual-Language Ownership Vocabulary

- UI/UX surface: any visible or operator-facing Nexus surface, including windows, overlays, dialogs, tray/taskbar affordances, settings, status readback, diagnostics, and future extension management.
- Surface family: a group of UI/UX surfaces with shared purpose, risk, and validation needs, such as command entry, authoring, confirmation/result, status, diagnostics, or settings.
- Visual language: the coherent set of layout, hierarchy, spacing, color, typography, iconography, motion, tone, empty states, loading states, error states, and naming conventions that make Nexus feel intentional.
- Interaction contract: the user-facing promise for what an input, action, confirmation, cancellation, failure, or completion state means.
- Shell frame: the top-level app/window context that orients the user before deeper task or configuration surfaces appear.
- Intent entry point: a surface where the user expresses what they want Nexus to do, such as command entry, quick task entry, or future action discovery.
- Authoring surface: a surface where the user creates, edits, names, organizes, or validates reusable tasks, saved actions, or callable groups.
- Confirmation surface: a surface that asks for explicit user approval before execution, mutation, or another meaningful state change.
- Result surface: a surface that reports success, failure, blocked state, partial state, or next recovery action after Nexus handles a request.
- Status surface: a surface that reports state without becoming an execution command path by itself.
- Diagnostic surface: a surface that explains failures, recovery options, support evidence, or dev/operator triage without widening normal product behavior.
- Navigation affordance: a visible or discoverable way to move between Nexus surfaces, return to the main shell, close a surface, or recover orientation.
- Product copy: user-facing words, labels, status text, warnings, and confirmations that shape trust and comprehension.
- Accessibility/readability baseline: minimum expectations for legibility, focus, contrast, hierarchy, keyboard discoverability, and cognitive load before visual implementation is admitted.

### Ownership Boundaries

- Nexus-owned: visual language, product copy, surface hierarchy, interaction contract, confirmation/result semantics, accessibility/readability standards, and consistency across Nexus-owned surfaces.
- Workstream-owned for FB-031: source map, vocabulary, admission rules, risk classification, validation expectations, and explicit non-goals for future UI/UX implementation seams.
- Future implementation-owned: actual component code, layout changes, CSS/style tokens, assets, icons, animations, launcher behavior, settings behavior, tray/taskbar behavior, or runtime UI changes after a later seam admits them.
- External/system-owned: Windows shell behavior, OS notifications, taskbar mechanics, file associations, external plugin UI, hardware overlays, and third-party automation tools outside Nexus control.
- Not owned by WS-1: product redesign, visual assets, runtime behavior, settings flow, launcher policy, installer flow, protocol/transport behavior, telemetry/HUD implementation, or release packaging.

### WS-1 Completion Decision

- WS-1 Result: Complete / green.
- Validation Layer: documentation and governance validation only.
- User Test Summary Applicability: not applicable for WS-1 because this seam adds architecture/vocabulary only and creates no user-visible behavior.
- Cleanup: no programs, helper processes, windows, temporary files, probes, assets, or runtime artifacts were created.
- Continue/Stop Decision: stop after WS-1 under `Single-Seam Fallback` because visual-language and UI-model planning should be reviewed one seam at a time before lifecycle/interaction-state framing begins.

## Validation Contract

- `python dev\orin_branch_governance_validation.py`
- `git diff --check`
- `git status --short --branch`
- Validator must compare latest public prerelease canon against the latest local or remote pre-Beta tag.
- Validator must fail if a workstream whose release tag exists remains represented as merged-unreleased release debt.
- Validator must fail future release-floor claims where architecture-only or non-user-facing planning is treated as `minor prerelease` without an executable, runtime, operator-facing, or user-facing capability rationale.

## Stop Conditions

- Stop if FB-040 remains represented as merged-unreleased release debt after repair.
- Stop if latest public prerelease truth trails the live `v1.6.0-prebeta` release.
- Stop if release-version law cannot distinguish architecture-only planning from actual minor capability expansion.
- Stop if FB-031 scope drifts into UI implementation, launcher work, settings work, runtime behavior, assets, or release work.
- Stop if visual-language vocabulary becomes implementation-shaped before lifecycle/state framing and validation/admission contracts are complete.
- Stop if validator hardening requires broad redesign outside post-release closure or release-version advancement.
- Stop if source-of-truth conflicts make FB-031 Branch Readiness admission unclear.

## Exit Criteria

- FB-040 is Released / Closed in `v1.6.0-prebeta`.
- Latest public prerelease truth is `v1.6.0-prebeta`.
- Release debt is clear across backlog, roadmap, workstreams index, and FB-040 workstream canon.
- FB-031 is represented as the active Branch Readiness workstream.
- Branch objective, target end-state, expected seam families, UTS strategy, later-phase expectations, initial Workstream seam sequence, validation contract, and stop conditions are explicit.
- Validator hardening covers post-release closure drift and release-version advancement drift.
- WS-1 Nexus-era UI/UX source map and visual-language ownership vocabulary is complete and durably recorded.

## Rollback Target

- `Workstream`

## Next Legal Phase

- `Workstream`

## Governance Drift Audit

Governance Drift Found: Yes, repaired during FB-031 Branch Readiness.

- Drift Type: escaped post-release canon closure drift and release-version advancement drift.
- Finding: FB-040 was live as `v1.6.0-prebeta`, but durable canon still carried latest public prerelease `v1.5.0-prebeta`, FB-040 merged-unreleased release debt, and FB-031 selected-only / branch-not-created wording after this branch was created.
- Version Finding: FB-040 advanced by a minor prerelease despite delivering an architecture-only, non-user-facing planning/admission milestone; the published tag remains canonical, but future equivalent work must not use minor advancement solely because it opens a planning lane.
- Repair: latest public prerelease truth is advanced to `v1.6.0-prebeta`, FB-040 is closed/released, release debt is cleared, FB-031 is admitted as the active Branch Readiness workstream, and validator/governance coverage is tightened for remote tag closure and release-floor semantics.
- Governance Drift Found After Repair: No unresolved drift remains after validation.
