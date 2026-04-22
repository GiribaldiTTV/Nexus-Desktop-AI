# FB-039 External Trigger And Plugin Integration Architecture

## ID And Title

- ID: `FB-039`
- Title: `External trigger and plugin integration architecture`

## Record State

- `Promoted`

## Status

- `Workstream`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-039-external-trigger-plugin-integration-architecture`

## Current Phase

- Phase: `Workstream`

## Phase Status

- `Active Branch`
- branch: `feature/fb-039-external-trigger-plugin-integration-architecture`
- branch created from updated `main` after FB-038 release/post-release confirmation green
- FB-038 remains `Released (v1.4.1-prebeta)` / `Closed`
- release debt is clear
- no runtime/product implementation has started

## Branch Class

- `implementation`

## Blockers

- None.

## Entry Basis

- `main` was aligned with `origin/main` before branch creation.
- FB-038 is released and closed in `v1.4.1-prebeta`.
- Latest public prerelease truth is `v1.4.1-prebeta`.
- Repo-level admission gate passed: no release debt, no stale FB-038 canon, no active implementation branch, and no existing FB-039 branch.
- FB-039 was selected in backlog and roadmap as the next implementation workstream before this branch was created.
- Branch Readiness is admitted to define the FB-039 source map, lifecycle ownership, trust/safety boundaries, validation contract, non-goals, and first Workstream seam before implementation.
- Branch Readiness durability is committed and pushed; Workstream admitted WS-1 first, and WS-1 durability is complete.

## Branch Objective

- Establish the architecture-first authority for FB-039 external trigger and plugin integration before any runtime implementation begins.
- Define how external trigger origins are named, owned, trusted, admitted, validated, and later routed into existing Nexus action authority.
- Keep this branch bounded to external trigger and plugin integration architecture; do not use it to implement Stream Deck, protocol transport, installer, settings, or runtime plugin behavior during architecture seams.

## Target End-State

- FB-039 has a durable source map for candidate external trigger origins and the vocabulary needed to discuss ownership without implementation ambiguity.
- Lifecycle ownership is explicit for trigger discovery, registration, enablement, invocation, teardown, failure handling, and user-visible safety boundaries.
- Trust/safety and validation/admission contracts are explicit enough to admit later Workstream implementation seams without inventing validation scope midstream.
- The first Workstream seam is architecture-first, non-implementing, and bounded to source-map plus ownership vocabulary.

## Expected Seam Families And Risk Classes

- Source-map and vocabulary seam family; risk class: architecture/governance because it defines nouns, owners, and system boundaries before runtime code exists.
- Lifecycle and trust/safety seam family; risk class: integration/safety because external inputs can cross user intent, saved-action authority, and local execution boundaries.
- Validation/admission seam family; risk class: validator/governance because later implementation must prove negative paths, trust boundaries, and no unauthorized execution.
- User-facing integration seam family is later-phase only; risk class: desktop/manual validation if future implementation introduces operator-visible trigger setup or invocation behavior.

## User Test Summary Strategy

- Branch Readiness had no meaningful manual User Test Summary because it did not change runtime or user-visible product behavior; WS-1 and WS-2 are documentation-only and have no meaningful manual User Test Summary.
- If a later Workstream seam introduces user-visible setup, trigger invocation, tray/overlay interaction, settings, prompt, or desktop shortcut behavior, the workstream must add a User Test Summary section and follow the returned-results blocker model before Live Validation or PR Readiness can advance.
- If later implementation remains headless or architecture-only, the workstream must explicitly record why no meaningful manual User Test Summary applies.

## Later-Phase Expectations

- Workstream began only after this Branch Readiness scaffold became durable and Seam 1 was explicitly admitted.
- Hardening must pressure-test trust boundaries, lifecycle cleanup, negative-path handling, and regression risk against saved-action, callable-group, overlay, tray, and built-in catalog baselines if implementation touches those paths.
- Live Validation is required only if FB-039 introduces user-visible desktop behavior or operator-facing integration setup; otherwise validation may remain repo-side with a documented no-meaningful-manual-test rationale.
- PR Readiness must confirm no helper sprawl, no scope drift into FB-040 monitoring/HUD, no unapproved runtime/plugin surface, and no stale release or branch-authority canon.

## Initial Workstream Seam Sequence

### Seam 1: External Trigger Source Map And Ownership Vocabulary

- Goal: define candidate trigger-origin classes, ownership nouns, authority boundaries, and non-runtime vocabulary for later implementation planning.
- Scope: document source categories, owner roles, allowed/disallowed trigger authority, and how the existing saved-action/callable-group/confirmation model constrains future trigger behavior.
- Non-Includes: no plugin runtime, no Stream Deck integration, no protocol transport, no installer work, no settings UI, no trigger execution, and no helper creation.

### Seam 2: Trigger Lifecycle And Trust/Safety Contract

- Goal: define the lifecycle and safety contract for discovery, registration, enablement, invocation request handling, teardown, failure visibility, and blocked input paths.
- Scope: map lifecycle states and trust decisions needed before any executable integration code is admitted.
- Non-Includes: no lifecycle implementation, no persisted schema changes, no external device/API integration, and no user-facing setup surface.

### Seam 3: Validation And Admission Contract For Later Implementation Seams

- Goal: define the validation families, runtime markers, negative-path proof, cleanup proof, and user-facing/manual gates required before implementation seams can be admitted.
- Scope: specify what later validators or helper reuse must prove and when helper creation would be justified under the registry.
- Non-Includes: no new validator/helper creation during WS-1 or WS-3 planning unless a concrete validation gap blocks later implementation admission.

### Seam 4: Implementation Boundary And First Runtime Seam Admission Framing

- Goal: define the first runtime implementation seam boundary that may be admitted later without implementing it in the architecture pass.
- Scope: frame the first Nexus-owned runtime seam, its required proof, and its non-includes so later implementation cannot invent transport, plugin, or execution scope midstream.
- Non-Includes: no runtime code, no external listener, no plugin host, no transport binding, no payload schema, no settings UI, no installer work, and no action execution path.

### Seam 5: Follow-On Architecture Tightening

- Goal: reconcile WS-1 through WS-4 into one durable architecture authority and identify unresolved architecture decisions that must remain blocked from runtime implementation.
- Scope: tighten terminology, stop conditions, future-seam gates, and non-goals without adding product/runtime behavior.
- Non-Includes: no implementation, no helper creation, no validator creation, no release work, and no phase advancement claim.

### Seam 6: Internal Trigger Intake Boundary Skeleton

- Goal: implement the first Nexus-owned internal trigger intake boundary as a default reject/defer skeleton.
- Scope: add an internal-only runtime module that can normalize a trigger request concept, classify known / blocked / unsupported origin categories, and refuse execution routing by default.
- Non-Includes: no external listener, protocol endpoint, transport binding, payload schema, plugin host, Stream Deck integration, settings UI, installer work, saved-action execution, callable-group execution, helper creation, or user-facing behavior.

### Seam 7: Trigger Registration And Bounded Invocation Follow-Through

- Goal: later define a bounded registration and invocation handoff path only after WS-6 proves the intake boundary remains safe by default.
- Scope: planned only until a future pass admits exact affected files, validation gates, and non-includes.
- Non-Includes: not executed during WS-6; no action execution, plugin host, transport, protocol, settings, or UI work by inheritance.

### Seam 8: Validation Tightening And User-Test Classification Alignment

- Goal: later decide whether reusable validation helper coverage or User Test Summary classification must be added for the first runtime implementation chain.
- Scope: planned only until WS-7 truth exists or validation gaps become concrete.
- Non-Includes: not executed during WS-6; no durable helper creation, user-test handoff, or phase advancement by inertia.

## Active Seam

- Active seam: `None after WS-6 completion`.
- Last executed seam: `WS-6 Internal Trigger Intake Boundary Skeleton`.
- WS-1 status: complete and durable as architecture-only documentation.
- WS-2 status: complete and durable as architecture-only documentation.
- WS-3 status: complete and durable as architecture-only documentation.
- WS-4 status: complete and durable as architecture-only documentation.
- WS-5 status: complete and durable as architecture-only documentation.
- WS-6 status: complete and durable as internal-only runtime skeleton.
- WS-7 status: planned only; not activated because WS-6 is the first runtime seam and downstream registration/invocation follow-through needs a separate admission decision.
- WS-8 status: planned only; not activated because validation-helper/User Test Summary tightening must follow concrete WS-7 truth or a proven validation gap.
- Next runtime implementation seam: not active; requires a later bounded Workstream pass with exact affected files, non-includes, validation gates, and User Test Summary classification.

## WS-1 External Trigger Source Map

An external trigger source is a local or locally-adjacent origin outside the core Nexus command overlay that asks Nexus to consider starting an action, workflow, or future plugin-owned entry path.

External trigger sources are not themselves Nexus action authority. They may request attention or route a trigger request into a Nexus-owned entry point, but they do not bypass Nexus confirmation, saved-action authority, callable-group behavior, trust boundaries, or user-visible failure handling.

Candidate trigger-origin categories for FB-039 planning:

- Hardware-adjacent trigger tools: local devices or device-control applications that expose user-initiated buttons, macro keys, decks, or equivalent physical/near-physical trigger surfaces.
- Desktop automation tools: local automation utilities that can initiate user-configured actions or shortcuts from the desktop environment.
- Local companion apps: installed local applications that could request Nexus action handling through a future approved integration path.
- Future plugin-hosted sources: Nexus-adjacent plugin surfaces that may later host trigger affordances once lifecycle, trust/safety, and validation contracts exist.
- Explicitly unsupported origins for WS-1: remote network callers, untrusted web pages, cloud webhook ingress, background services without user-visible ownership, arbitrary script injection, and any source that would require transport or security enforcement design in this seam.

## WS-1 Ownership Vocabulary

- External trigger: a user-initiated or tool-originated signal outside the core Nexus overlay asking Nexus to consider action handling.
- Trigger origin: the named source category or concrete surface that produced an external trigger.
- Trigger event: the occurrence at the origin, before Nexus accepts or interprets it.
- Trigger request: the Nexus-facing request concept created after a trigger event is intentionally handed toward Nexus ownership.
- Nexus entry point: the architecture-level receiving boundary where Nexus may later validate, route, reject, or surface a trigger request.
- Supported origin: an origin category admitted by workstream truth and later validation as eligible for a Nexus entry point.
- Unsupported origin: an origin category excluded by scope, trust posture, missing validation, or lack of user-visible ownership.
- External-owned surface: the UI, hardware, automation tool, companion app, or plugin-hosted surface outside Nexus that emits the trigger event.
- Nexus-owned surface: any Nexus-controlled confirmation, overlay, execution, saved-action, callable-group, failure visibility, or audit surface reached after a trigger request is accepted.

## WS-1 Ownership Boundaries

External systems own:

- the physical, desktop, app, or future plugin-hosted surface where the trigger event begins
- local user configuration inside that external surface
- whether their surface presents a button, shortcut, macro, or equivalent origin affordance
- non-Nexus device/app availability, naming, and native UI state

Nexus owns:

- whether an origin category is supported or unsupported
- the Nexus entry point boundary for accepting, rejecting, or deferring a trigger request
- any later mapping from a trigger request into existing saved-action, callable-group, overlay, confirmation, or result behavior
- user-visible Nexus failure messaging and audit markers once a trigger request crosses into Nexus ownership
- preservation of existing action authority, confirmation, and execution semantics

Not-owned / non-goal surfaces for WS-1:

- external device SDK behavior
- Stream Deck runtime integration
- protocol listeners or transport bindings
- command payload schemas
- installer or settings flows
- trust/safety enforcement logic
- validation matrix design
- new helper or runtime implementation

## WS-1 Entry-Point Architecture Framing

The Nexus entry point is an architecture boundary, not an implementation component in WS-1.

For WS-1, the entry point means: the future Nexus-owned place where a trigger request may be received, classified by origin support, and routed or rejected according to later lifecycle, trust/safety, and validation contracts.

The entry point does not define a listener, transport, payload schema, protocol, plugin API, background service, or UI surface in this seam. Those decisions are intentionally deferred to later seams after WS-2 defines lifecycle/trust-safety boundaries and WS-3 defines validation/admission requirements.

## WS-1 Execution Record

- WS-1 executed as architecture-only documentation on the active FB-039 branch.
- Source map: complete for bounded candidate categories and unsupported origins.
- Ownership vocabulary: complete for later-seam terminology.
- Ownership boundaries: complete at architecture level.
- Entry-point framing: complete as a concept only, with no implementation contract.
- Runtime/product implementation: none.
- Helper creation: none.
- WS-2 was admitted only in a later bounded Workstream pass.
- WS-3 remained planned only at WS-1 completion.

## WS-2 Lifecycle Ownership Boundaries

WS-2 defines lifecycle ownership at the architecture boundary only. It does not define a listener, protocol, payload schema, persistence schema, plugin API, transport binding, settings UI, or runtime implementation.

Lifecycle ownership for FB-039 planning:

- Discovery: external systems own whether their device, automation tool, companion app, or future plugin-hosted surface exists and is available; Nexus owns whether an origin category is recognized as eligible for later support.
- Registration: Nexus owns the future admission record concept for a supported origin; the external system may present origin identity, but it cannot self-register into Nexus authority.
- Enablement: the user and Nexus-owned approval surfaces own enablement; an external origin may request eligibility but cannot silently enable itself.
- Invocation: the external origin owns the trigger event before handoff; Nexus-owned trigger intake owns classification, acceptance, rejection, and routing once a trigger request crosses the entry boundary.
- Disablement: Nexus and the user own revocation, disablement, and blocked-origin state; an external origin must not bypass a disabled or rejected state.
- Teardown: Nexus owns cleanup of Nexus-accepted intake state, pending request state, and user-visible Nexus failure state; the external system owns its own device/app shutdown and local cleanup.
- Failure visibility: external systems own failures before handoff; Nexus owns user-visible failure visibility once a trigger request reaches Nexus-owned intake or execution authority.

## WS-2 Trust/Safety Boundary Vocabulary

- Nexus-owned trigger intake: the future Nexus boundary that may classify a trigger request, determine whether the origin is supported, and reject unsafe or unsupported requests before action authority is reached.
- Nexus-owned execution authority: the existing Nexus-controlled authority that governs saved actions, callable groups, confirmation, result reporting, and any future trigger-routed execution.
- User-controlled approval surface: any Nexus-owned surface or recorded user decision that enables, confirms, disables, or rejects trigger-origin access.
- Externally initiable request: a request an external origin may start, limited to asking Nexus to consider handling; it is not execution authority.
- User-controlled execution decision: a Nexus-owned decision point that remains under user or Nexus policy control before action execution may happen.
- Blocked origin: an origin class or concrete origin that must not be admitted because it lacks user-visible ownership, local trust posture, validation basis, or safe routing.
- Conditional origin: an origin class that may be considered later only after lifecycle, trust/safety, and validation/admission contracts prove enough boundary control.

## WS-2 Trigger Class Admission Posture

Admissible at architecture level for later consideration:

- local hardware-adjacent trigger tools with user-visible device/app ownership
- local desktop automation tools with user-owned configuration
- local companion apps installed and controlled by the user
- future plugin-hosted sources after Nexus-owned lifecycle and validation contracts exist

Conditionally admissible in later seams only:

- background local services with explicit user-visible owner, revocation path, and failure visibility
- local app-to-app request paths whose transport and trust posture are admitted by later seams
- multi-action plugin surfaces after WS-3 defines validation/admission proof and later implementation seams remain bounded

Explicitly blocked for FB-039 unless future governance reopens scope:

- remote/cloud webhook ingress
- untrusted web pages or browser-originated arbitrary trigger requests
- arbitrary scripts with no named user-visible owner
- origins that request direct execution while bypassing Nexus-owned intake, confirmation, or execution authority
- origins that require credential, privilege, session, or persistence escalation outside existing Nexus authority
- silent background origins that cannot be disabled, audited, or made visible to the user

## WS-2 User Control And External Initiation Rules

Must remain user-controlled or Nexus-controlled:

- whether an origin category is supported
- whether a concrete origin is enabled or disabled
- any binding from a trigger request into saved-action, callable-group, overlay, confirmation, or result behavior
- any approval, confirmation, or rejection surface needed before execution authority is reached
- user-visible failure handling once a request crosses into Nexus-owned intake

May be externally initiable:

- the original trigger event on an external-owned surface
- a trigger request asking Nexus-owned intake to consider routing
- a later eligible handoff into Nexus only after the origin is supported and enabled

Must not be externally controlled:

- direct execution of saved actions or callable groups
- bypass of confirmation or approval surfaces
- automatic enablement, registration, disablement override, or teardown override
- suppression of Nexus-owned failure visibility or audit markers

## WS-2 Execution Record

- WS-2 executed as architecture-only documentation on the active FB-039 branch.
- Lifecycle ownership boundaries: complete for discovery, registration, enablement, invocation, disablement, teardown, and failure visibility.
- Trust/safety boundary vocabulary: complete for external origin, Nexus intake, Nexus execution authority, and user-controlled surfaces.
- Trigger class admission posture: complete for admissible, conditionally admissible, and blocked trigger classes.
- User-control rules: complete for what remains user/Nexus controlled versus externally initiable.
- Runtime/product implementation: none.
- Protocol, payload schema, transport binding, installer, settings UI, monitoring/HUD, taskbar/tray expansion, and helper creation: none.
- WS-3 remains planned only.
- Continuation decision: WS-3 may be admitted only in a later bounded Workstream pass.

## WS-3 Validation And Implementation-Admission Contract

WS-3 defines what later implementation seams must prove before runtime code is admitted. It does not create validators, helpers, runtime code, protocols, transports, payload schemas, UI, installer behavior, or release artifacts.

Validation families required before a later runtime seam may be admitted:

- Governance and branch-truth validation: `python dev\orin_branch_governance_validation.py`, `git diff --check`, and clean branch-status proof remain required for every runtime-admission pass.
- Regression validation: later runtime implementation must preserve FB-027 interaction baselines, FB-036 saved-action authoring authority, FB-041 callable-group execution semantics, FB-037 built-in catalog authority, and FB-038 tray/task UX behavior when touched.
- Boundary validation: the seam must prove external origins can only create a Nexus-facing trigger request and cannot bypass Nexus-owned intake, approval, confirmation, saved-action, callable-group, or result authority.
- Negative-path validation: unsupported, disabled, blocked, malformed, unauthenticated, non-user-visible, and remote/cloud-origin trigger attempts must reject safely without execution.
- Cleanup validation: accepted, rejected, disabled, failed, and canceled trigger requests must leave no stale pending state, duplicate execution, orphaned runtime process, or persistent binding outside admitted scope.
- User-facing validation: if a later seam adds operator-visible setup, settings, prompt, tray, overlay, notification, or shortcut behavior, the workstream must add a meaningful User Test Summary path and follow the returned-results blocker model before Live Validation or PR Readiness.
- Helper governance validation: reuse existing validators and registered helper families first; new durable root `dev/` helpers require registry lookup, `Helper Status`, owner, reuse decision, and consolidation target before closeout-grade proof can depend on them.

Implementation-admission gates:

- A later runtime seam must name exactly one runtime boundary and one active owner before edits begin.
- The seam must list exact non-includes, including any blocked protocol, transport, payload, UI, installer, plugin-host, settings, or action-execution expansion.
- The seam must state whether it is internal-only, user-visible, or external-facing; external-facing or user-visible seams require stronger validation and User Test Summary handling.
- The seam must identify affected modules before patching and must stop if the affected surface crosses risk class or subsystem family.
- The seam must define a rollback target and cleanup expectation before implementation begins.
- The seam must prove branch-local authority remains current after implementation and before durability commit/push.

Runtime marker expectations for later implementation:

- later runtime seams should emit or expose clear evidence for intake received, origin classified, request accepted or rejected, execution blocked or routed, cleanup complete, and failure surfaced when those states exist
- runtime markers are admission expectations only in WS-3; marker names, log shape, payload fields, and persistence format remain deferred to the implementation seam that owns them

WS-3 continue-or-stop decision:

- WS-3 validation/admission contract is architecture-only and stays in the same workstream, phase, branch class, risk class, and subsystem family as WS-1 and WS-2.
- WS-4 may continue in this pass only as implementation-boundary framing, not runtime implementation.
- Stop before runtime code, protocol mechanics, payload schema, transport binding, plugin host, settings UI, installer flow, or helper creation.

## WS-3 Execution Record

- WS-3 executed as architecture-only documentation on the active FB-039 branch.
- Validation families: complete for governance, regression, boundary, negative-path, cleanup, user-facing, and helper-governance proof.
- Implementation-admission gates: complete for future seam ownership, boundary, non-includes, affected surface, rollback, cleanup, and branch-truth requirements.
- Runtime marker expectations: recorded only as future proof categories; concrete marker names and formats remain deferred.
- Runtime/product implementation: none.
- Validator/helper creation: none.
- Continue decision after WS-3: continue to WS-4 only as docs-only implementation-boundary framing.

## WS-4 Implementation Boundary And First Runtime Seam Admission Framing

WS-4 frames the first runtime implementation seam that may be admitted later. It does not implement that seam.

First runtime seam candidate:

- Name: `Internal Trigger Intake Boundary Skeleton`.
- Goal: introduce a Nexus-owned internal trigger intake boundary that can receive an internal trigger request concept and reject or defer it by default until later seams admit origin support and routing.
- Owner: Nexus-owned trigger intake.
- Risk class: implementation/integration safety, because the seam touches the boundary where external-origin intent may later cross into Nexus action authority.
- Admission posture: not active in WS-4; eligible only for a later bounded Workstream implementation pass with exact affected files and validation commands named before patching.

Allowed future runtime seam boundary:

- internal-only Nexus-owned intake boundary
- default reject/defer behavior for every origin until explicit support is admitted
- branch-local evidence proving no saved action, callable group, overlay, tray, settings, installer, plugin host, or external transport is reached by default
- governance validation and direct negative-path proof before durability

Not admitted by WS-4:

- external listener, protocol endpoint, URI handler, socket, webhook, cloud ingress, browser-origin bridge, or transport binding
- payload schema, serialization format, plugin API, Stream Deck API, installer path, settings UI, tray/taskbar expansion, or monitoring/HUD behavior
- direct saved-action execution, callable-group execution, silent background execution, or bypass of Nexus-owned confirmation/approval surfaces
- durable helper creation unless the future implementation seam proves existing validators cannot cover its negative-path and cleanup proof

Required preflight for the future first runtime seam:

- name the affected source files before editing
- state the exact trigger-intake boundary and its non-includes
- prove whether the seam is internal-only, user-visible, or external-facing
- identify required regression baselines and negative-path checks
- record whether any User Test Summary applies before claiming Workstream completion
- stop if implementation needs protocol, payload, transport, settings, installer, plugin-host, or execution routing decisions

## WS-4 Execution Record

- WS-4 executed as architecture-only documentation on the active FB-039 branch.
- First runtime seam admission framing: complete for the `Internal Trigger Intake Boundary Skeleton` candidate.
- Implementation boundary: complete for internal-only intake, default reject/defer behavior, and blocked external transport/execution scope.
- Preflight requirements: complete for future affected-file naming, non-includes, regression baselines, negative-path proof, User Test Summary classification, and stop conditions.
- Runtime/product implementation: none.
- Protocol, payload schema, transport binding, plugin host, installer, settings UI, monitoring/HUD, taskbar/tray expansion, and helper creation: none.
- Continue decision after WS-4: continue to WS-5 only as docs-only follow-on architecture tightening.

## WS-5 Follow-On Architecture Tightening

WS-5 reconciles the architecture chain into one durable authority. It does not authorize implementation.

Architecture authority after WS-5:

- WS-1 owns the external trigger source map, origin categories, ownership vocabulary, and Nexus entry-point framing.
- WS-2 owns lifecycle ownership, trust/safety boundary vocabulary, trigger class admission posture, and user-control versus external-initiation rules.
- WS-3 owns the validation families, implementation-admission gates, runtime marker expectation categories, and helper/User Test Summary admission rules for future implementation seams.
- WS-4 owns the first runtime seam admission framing for the future `Internal Trigger Intake Boundary Skeleton` candidate.

Unresolved architecture decisions that remain blocked from implementation:

- exact source files for the first runtime seam
- concrete runtime marker names, log shape, payload fields, or persistence format
- any external transport, protocol, URI handler, socket, webhook, browser bridge, or cloud ingress
- Stream Deck integration, plugin host API, installer flow, settings UI, tray/taskbar expansion, monitoring/HUD, or action execution routing
- durable helper creation or validator expansion before a concrete implementation seam proves the validation gap and registry obligations

Future Workstream admission rule:

- The next implementation pass may admit only one runtime seam at a time.
- The candidate first runtime seam is `Internal Trigger Intake Boundary Skeleton`.
- Admission must restate source-of-truth, affected files, exact boundary, explicit non-includes, validation commands, cleanup expectations, User Test Summary classification, and stop conditions before any code edits.
- If the future seam needs protocol, payload, transport, settings, installer, plugin-host, or direct execution design, it must stop and split that concern into a later seam rather than absorbing it.

## WS-5 Execution Record

- WS-5 executed as architecture-only documentation on the active FB-039 branch.
- Architecture authority reconciliation: complete for WS-1 through WS-4.
- Blocked implementation decisions: complete and explicitly deferred.
- Future runtime seam admission rule: complete for the first candidate implementation seam.
- Runtime/product implementation: none.
- Protocol, payload schema, transport binding, plugin host, installer, settings UI, monitoring/HUD, taskbar/tray expansion, action execution routing, validator/helper creation, and release work: none.
- Continue decision after WS-5: stop the current bounded architecture chain; next movement requires a later bounded Workstream pass admitting exactly one runtime implementation seam or a governance-backed decision that architecture-only Workstream scope is complete.

## WS-6 Internal Trigger Intake Boundary Skeleton

WS-6 implements the first internal Nexus-owned trigger intake boundary. The boundary is importable and testable, but it is not wired to any external listener, UI, action catalog, saved-action path, callable-group path, plugin host, protocol, transport, or launcher path.

Runtime boundary introduced:

- Module: `desktop/external_trigger_intake.py`
- Boundary owner: Nexus-owned trigger intake.
- Request concept: internal `TriggerIntakeRequest` with origin id, origin category, optional user-visible label, and optional event name.
- Result concept: internal `TriggerIntakeResult` with decision, reason, category classification flags, and hard false execution/routing fields.
- Default behavior: known local candidate origin categories are deferred with `runtime_support_not_admitted`; blocked, unsupported, or malformed categories are rejected.
- Execution authority: always false in WS-6; no saved-action, callable-group, confirmation, overlay, or result authority is reached.

WS-6 direct validation expectations:

- known local candidate origin category defers rather than routes
- blocked origin category rejects
- unsupported origin category rejects
- malformed origin id or category rejects
- all results keep `routed_to_execution=false`, `execution_authorized=false`, and `cleanup_required=false`
- import/compile succeeds without PySide, desktop runtime, external device, plugin, or transport dependencies

## WS-6 Execution Record

- WS-6 executed as an internal-only runtime skeleton on the active FB-039 branch.
- Added `desktop/external_trigger_intake.py`.
- Internal intake boundary: complete for request normalization, origin-category classification, blocked-category rejection, unsupported-category rejection, malformed-request rejection, and known-category defer.
- External listener/protocol/transport/payload schema/plugin host/settings UI/installer/taskbar/tray/action execution/callable-group execution: none.
- User-visible behavior: none; User Test Summary remains not meaningful for WS-6.
- Durable dev helper creation: none; direct proof uses inline Python for this seam, and WS-8 remains the planned seam for any reusable validation tightening if a concrete gap appears.
- Continue decision after WS-6: stop before WS-7 because trigger registration and invocation follow-through would expand beyond the first runtime skeleton and requires a fresh affected-file/validation admission decision.

## Scope

- Record WS-6 as the first bounded runtime seam when validation remains green.
- Preserve WS-1 as complete and durable architecture-only source map and ownership vocabulary.
- Preserve WS-2 as complete and durable architecture-only lifecycle ownership and trust/safety boundary contract.
- Preserve WS-3 through WS-5 as complete and durable architecture/admission framing.
- Keep WS-7 and WS-8 planned only; do not implement registration, invocation follow-through, validation-helper creation, or user-test handoff in this pass.
- Preserve architecture-level entry-point framing without implementation design, listener design, transport binding, protocol mechanics, payload schema details, settings UI, installer flow, or helper creation.
- Carry the deferred PR #67 connector follow-up as later Workstream governance review only if it remains relevant to validator trust.

## Non-Goals

- No plugin runtime implementation during WS-6.
- No Stream Deck integration implementation during WS-6.
- No protocol handling, installer work, settings surface, taskbar/tray expansion, monitoring HUD work, or release packaging.
- No runtime/product code beyond the internal-only trigger intake boundary skeleton.
- No new validation helper creation unless a later Workstream seam proves an actual validation gap and registry rules are satisfied.
- No FB-040 monitoring, thermals, or HUD scope.
- No trust/safety enforcement logic, transport payload schema detail, user-facing settings/UI, or runtime plugin lifecycle implementation in WS-6.

## Validation Contract

- Workstream WS-6 validation:
  - `python dev\orin_branch_governance_validation.py`
  - inline Python proof for `desktop.external_trigger_intake`
  - `python -m compileall desktop\external_trigger_intake.py`
  - `git diff --check`
  - `git status --short --branch`
- WS-6 is internal-only and introduces no user-visible desktop behavior; no runtime helper or User Test Summary export is required.
- WS-7 must rerun and expand validation only after it is admitted in a later bounded pass.
- Reuse existing validator families and `Docs/validation_helper_registry.md` guidance first.
- New helpers are blocked until a concrete validation gap exists, the helper purpose is branch-scoped or reusable by design, and registry status/consolidation rules are satisfied.
- Any user-facing behavior introduced later must route through the User Test Summary and user-facing shortcut validation rules if applicable.

## Stop Conditions

- Stop if FB-039 scope expands beyond the internal-only trigger intake boundary skeleton during WS-6.
- Stop if WS-6 starts defining trust/safety enforcement logic, protocol mechanics, payload schemas, settings UI, installer flow, plugin host, helper implementation, or action/callable-group execution.
- Stop if a downstream seam cannot be stated as the same workstream, same phase, same branch class, same risk class, and same subsystem family or tightly coupled architecture chain.
- Stop if direct negative-path proof cannot demonstrate default reject/defer behavior without execution routing.
- Stop if any FB-038 release debt or stale release canon reappears.
- Stop if a governance-only branch, direct-main mutation, or between-branch repair path is attempted.
- Stop if new helper creation is proposed before reuse and registry obligations are satisfied.
- Stop if Workstream execution expands into WS-7 or WS-8 before WS-6 is recorded and validated and a fresh downstream admission decision is justified.

## Exit Criteria

- FB-039 is represented as the active Workstream in backlog, roadmap, and workstreams index.
- This workstream record contains the required phase authority fields.
- WS-1 external trigger source map, ownership vocabulary, ownership boundaries, and architecture-only entry-point framing are recorded.
- WS-2 lifecycle ownership boundaries, trust/safety boundary vocabulary, trigger class admission posture, and user-control rules are recorded.
- WS-3 validation and implementation-admission contract is recorded.
- WS-4 implementation boundary and first runtime seam admission framing is recorded.
- WS-5 follow-on architecture tightening is recorded.
- WS-6 internal trigger intake boundary skeleton is implemented and validated.
- WS-7 and WS-8 remain planned only until a later bounded Workstream pass admits them.
- FB-038 remains released/closed and release debt remains clear.
- Repo state is no longer `No Active Branch`; active branch truth is `feature/fb-039-external-trigger-plugin-integration-architecture`.
- No runtime/product implementation has started.

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Branch Readiness Notes

Branch Readiness durability is complete, WS-1 through WS-5 are durable, and WS-6 is now recorded as the first internal-only runtime skeleton. WS-7 and WS-8 remain planned only.
