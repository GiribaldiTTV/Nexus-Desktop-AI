# Nexus Vision Contract

## Purpose

This is the project-wide product vision for Nexus Desktop AI and ORIN. It defines intended experience, trust, visual consistency, and release-stage meaning. Family visions and feature documents supply the specific surfaces, behaviors, and dependencies. Intended capabilities must not be mistaken for implemented behavior.

The Public, Dev, and Owner editions share the same normal product experience while separating capability access, private state, installed identity, update channels, and trust boundaries. The edition model is described in `Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md`.

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

FAM-001 owns fatal launcher/runtime diagnostics and recovery surfaces for the current product. Feature-owning FAMs may expose their own degraded, blocked, unavailable, or recoverable states, but they consume the FAM-001 failure/recovery boundary when launcher/runtime recovery, crash diagnostics, support-bundle preparation, manual issue reporting, retry/close/repair choices, startup abort, or recovery exhaustion is involved. The released FB-034 recoverable `launch_failed` path is historical evidence for one bounded non-crashing incident class, not a live backlog owner for new diagnostics scope.

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
- contradictions between launcher, runtime state, renderer, and user-facing reporting

## NDAI Product Experience Contract

Every Nexus feature, window, control, status surface, runtime behavior, assistant interaction, and proof path should preserve a product experience that is deterministic, intuitive, immersive, predictable, reliable, and consistent. This contract applies to both the USER-facing experience and the implementation behavior behind it.

These six qualities are project-wide product standards, not optional style preferences:

- deterministic: the same visible state plus the same user action should produce the same result, with explicit state ownership, known inputs/outputs, no hidden surprise behavior, and a named exception when nondeterminism is intentional or unavoidable
- intuitive: the USER should understand what a surface does, what state it is in, what actions are available or blocked, why they are available or blocked, what will happen next, and where to recover without needing developer knowledge
- immersive: Nexus-owned surfaces should feel like one coherent NDAI product layer, not disconnected Windows utilities, mismatched branch-made widgets, generic native shells, visually unrelated tools, or feature-specific one-off control systems
- predictable: controls, layouts, state labels, assistant responses, recovery paths, disabled paths, confirmation flows, geometry behavior, and handoff behavior should follow recognizable patterns across the product
- reliable: the product should truthfully expose what works, what failed, what is unavailable, what is deferred, what is blocked, what can be retried, what needs setup, and what requires USER decision or waiver
- consistent: same-class Nexus-owned elements should share visual grammar, placement logic, state behavior, proof expectations, and backend truth mapping across families and windows unless a deliberate product exception is justified and verified

The contract applies to both visible product experience and supporting runtime truth. A visually polished surface that hides failed or unavailable backend state is not reliable. A backend path that works only through hidden state, branch-local assumptions, or inconsistent UI labels is not deterministic or intuitive. A control that looks unrelated to the accepted Nexus grammar breaks immersion and consistency even if it technically functions.

Text labels, feature-specific data, feature-owned state payloads, and backend ownership may differ by family. The underlying control family, interaction grammar, state mapping, recovery behavior, and proof expectation should remain recognizable unless a deliberate exception is justified and verified.

### Implementation And Experience Parity Standard

Nexus should behave as one product. Same-class elements and same-purpose behaviors should be as identical as practical across the entire NDAI program, using shared primitives, shared templates, shared state-machine patterns, shared labels, shared failure/recovery grammar, and shared proof expectations when those owners exist.

The expected parity is not blind copy/paste of every feature. It is product and implementation sameness where the USER experiences the same kind of thing:

- a Nexus window frame should feel and behave like the Nexus window frame everywhere it appears
- a close, minimize, back, settings, start, stop, retry, save, open-folder, select, dropdown, filter, toggle, list, status badge, warning, blocked-state, and recovery action should use the same visual grammar and interaction-state grammar unless a verified product exception warrants it
- a button should not silently change size, border language, hover glow, focus behavior, disabled style, typography, or placement logic simply because a different feature created it
- a status line should not claim ready, blocked, unavailable, deferred, failed, or successful unless the backend/runtime truth that owns that state can prove the same meaning
- a recovery or fallback action should follow the same user-understandable pattern across windows even when the feature-specific recovery code differs
- an assistant or AI-facing status should separate implemented, not implemented, provider blocked, local-only, deferred, failed, and user-action-required states with the same plain-language trust posture across all relevant surfaces

Backend and runtime parity means same-purpose product behavior should use comparable state ownership, inputs, outputs, lifecycle transitions, error/fallback/recovery routes, logging/proof hooks, and UI-visible status mapping. Different features may own different data, but they should not invent incompatible state names, hidden transitions, success semantics, retry behavior, or failure meanings for the same class of product action.

USER-facing parity means same-class visual elements should match or intentionally inherit the accepted Nexus grammar for dimensions, spacing, border weight, glow, typography, color roles, icon/text treatment, hover/focus/pressed/disabled states, keyboard accessibility, tooltip/status wording, placement, and motion/transition behavior. If a template or promoted UI reference exists, the new element should consume it or explain why it cannot. If no template exists, the branch must compare against the best accepted Nexus reference and elevate any judgment-dependent differences for USER review.

Immersion is explicit: the USER should be able to move between the AI Control Center, HUD Dashboard, Recording Studio, Log Viewer Studio, Global Settings, tray-opened surfaces, diagnostics/recovery surfaces, and future Nexus windows without feeling that each was built by a different product. A surface breaks immersion when it uses default Windows title bars for Nexus-owned product UI, mismatched control clusters, inconsistent button/card/list/dropdown grammar, unexplained status wording, hidden backend truth, or branch-specific styling that makes the USER relearn the product.

Permitted differences must be deliberate and bounded. A feature may vary content, domain-specific layout, density, edition-specific copy, or platform-native surfaces when the difference improves clarity, trust, accessibility, or platform safety. The result still needs truthful runtime mapping and a comparable user experience.

Future-proofing means foreseeable same-class additions can extend the same layout, state, and lifecycle model without brittle one-off rewrites. Use content rules, constraints, shared primitives, and explicit state ownership where they exist. This does not authorize implementing speculative future features.

## Project UI Vision

Nexus UI should feel comfortable, reliable, futuristic, and understandable at the same time. It should make the user feel that the system is capable and alive without becoming noisy, cryptic, or fragile.

Durable UI principles:

- comfort: normal operation should feel calm, readable, and safe to leave open for long sessions
- reliability: surfaces should expose state, failures, disabled paths, and recovery options plainly instead of hiding uncertainty
- futuristic feel: the UI should look intentional and Nexus-native, but visual ambition must not reduce clarity, accessibility, or task completion
- understandable interaction: controls, status labels, and assistant messages should explain what they do, what they changed, and what remains blocked
- consistency: similar actions such as Close, Open, Save, Start, Stop, Select Folder, Clear, Retry, and Export should use consistent placement, labels, affordances, and disabled/degraded states unless a deliberate product-wide exception is justified and verified
- window continuity: user-facing Nexus windows should remember USER-moved placement across sessions where technically feasible, restore safely when a saved location is unavailable or off-screen, and make any product-wide exception explicit in the feature behavior
- fail-proof behavior: risky actions should be reversible, confirmed when needed, recoverable, or safely disabled until their prerequisites are proven
- readability: layout density, contrast, typography, spacing, and state hierarchy should keep operator-facing information legible under normal desktop use
- versatility and changeability: future configuration, skins, layouts, modes, and edition-specific behavior are valid product goals, but they must be introduced through coherent product design rather than ad hoc styling
- standard control language: families may specialize controls for their surface, but they should inherit the project-wide control grammar before creating unique widgets, button families, folder pickers, or start/stop flows

Family and feature documents specialize these principles only when they have a real product reason. Product detail should explain user outcomes, surfaces, trust and recovery states, visual behavior, explicit non-goals, and checks that can verify them.

### NDAI UI Immersion And Window Chrome Standard

Every Nexus-owned product window, panel, dashboard, studio, command center, settings surface, tray-opened surface, diagnostics surface, and proof-visible user interface should feel like part of Nexus Desktop AI rather than a generic Windows utility.

Nexus-owned product windows must use admitted Nexus / NDAI window presentation: custom product framing or chrome, Nexus control grammar, consistent close/minimize/back/settings affordances, coherent title/header treatment, rounded or intentionally shaped frame behavior where applicable, matching card/button/list/scrollbar style, and visual hierarchy that matches the Project UI Vision and FAM-002 presentation standards.

Surface classification:

- `Nexus-Owned Product Surface`: a window, panel, dashboard, studio, command center, settings surface, tray-opened surface, diagnostics/recovery panel, proof-visible user interface, or persistent/transient product control that Nexus owns and the USER experiences as part of NDAI.
- `Platform-Native Exception`: an OS, browser, provider, installer, permission, file/folder picker, authentication, or platform-trust surface where native chrome is required or more trustworthy than custom chrome.
- `Diagnostic / Developer Surface`: a temporary or explicit troubleshooting/proof surface that is not presented as the normal product UI.
- `External Surface`: a provider, browser, OS, GitHub, or third-party UI surface that Nexus can open or route to but does not visually own.

Default Windows title bars, unstyled native utility windows, generic dialog shells, mismatched button families, and platform-looking popups are invalid for final `Nexus-Owned Product Surface` surfaces unless a platform-native exception is justified and verified. Allowed exception candidates include OS file pickers, OS security/permission prompts, installer or update surfaces that must use platform trust affordances, browser/provider-auth surfaces, or temporary troubleshooting-only diagnostics that are explicitly not the product UI. Even then, the product should make the exception deliberate and visually coherent.

FAM-002 is the shared Desktop Interface presentation authority, not the sole owner of every user-facing UI implementation. A consuming FAM branch may implement FAM-002-aligned UI work when that UI is necessary to complete the consuming FAM's feature behavior and technical requirements. Project Vision owns the global UI principles; FAM-002 owns reusable presentation contracts and control hierarchy; each FAM owns the UI/UX of its own feature behavior; each feature document describes the concrete surface, user flow, and checks for its category.

## Runtime Observability And USER Proof

Nexus Desktop AI should be observable enough to prove user-facing behavior without becoming a hidden diagnostic collector.

Durable product direction:

- normal desktop runtime mode is the default USER launch profile
- troubleshooting runtime mode is an explicit USER-consented diagnostic profile
- normal runtime mode should produce only minimal, privacy-safe product logs needed for reliability, recovery, and basic local troubleshooting
- troubleshooting mode should be temporary or scoped, locally stored by default, privacy-safe/redacted where needed, and visibly distinct from normal runtime
- elevated diagnostic logging, Dev Toolkit inspection, provider-visible data, support bundles, or exported evidence must not be enabled silently
- product UI should present client-like product folders and labels; it should not expose worktree, branch, FAM, developer, owner-only, or internal implementation paths unless a source-truth owner explicitly admits that product-facing concept
- developer/proof/evidence paths may use worktree, branch, FAM, or validation-lane labels only when they are clearly developer or validation evidence, not product UI
- branches that create runtime/user-facing behavior must classify fatal, recoverable, degraded, blocked, disabled/deferred, and unavailable-prerequisite behavior before treating the feature as ready

Formal user-facing proof has a stricter bar than internal diagnosis:

- a visible or user-facing behavior claim is closeout-grade only when proved through photo, video, or ordered frame-sequence evidence from the relevant USER-facing runtime path
- runtime logs, markers, manifests, helper output, and Dev Toolkit events are supporting evidence for diagnosis and consistency; they do not replace photo/video proof for visible USER-facing acceptance
- if a required claim cannot be proved in photo/video, the result must remain unverified until a real user observation or suitable direct evidence exists
- user-facing runtime verification for desktop/user-facing behavior must use the exact normal USER desktop runtime launcher path declared for the branch unless verified launcher parity shows the diagnostic path is equivalent for that exact claim

Future two-launcher model:

- `Normal Desktop Runtime Launcher`: starts normal NDAI for ordinary USER operation and owns default user-facing runtime verification proof
- `Troubleshooting Runtime Launcher`: starts NDAI in troubleshooting mode for consented diagnostics, validation, or support
- `Launcher Parity Proof`: proves both launchers start the same product runtime/build, use the same product data roots and user-visible behavior, and differ only by admitted diagnostic flags, diagnostic evidence roots, log level, and troubleshooting disclosure
- if launcher parity is missing, fails, or the claim being validated could be affected by troubleshooting-mode differences, user-facing runtime verification must use the normal USER desktop runtime launcher or leave the claim unverified

## AI-Native Operating Experience

Nexus should become an AI-native operating experience layer without pretending that provider/model fluency is the same thing as system reliability.

The durable direction is:

- Windows remains the host platform
- Nexus becomes the visible experience layer
- ORIN remains the persistent cooperative assistant identity
- providers, models, and capability packs are replaceable extensions, not the product identity
- objective and safety-sensitive answers prefer deterministic, tool-backed, or validation-backed paths before generative improvisation
- AI state, provider state, permission state, cache state, privacy state, and refusal/uncertainty posture should be visible in plain language when they matter
- trust UX should be calm, explainable, reversible, and understandable to non-technical users

Cross-family AI architecture, permission-state, deterministic routing, Trust Journal, AI operational cache controls, routine/continuity boundaries, competitive-integrity boundaries, and capability-pack architecture live in `Docs/ai_runtime_and_trust_architecture.md`.

Family-specific direction remains with the family visions. Runtime AI, provider/model work, memory, cache, camera/microphone/desktop vision, and installer behavior require their specific user consent, privacy boundaries, technical safeguards, and verification before activation.

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
- shipped built-in task grouping/taxonomy should stay deferred until the explicit callable-group model is proven and a stable default group strategy exists
- post-Beta grouping/query ideas should not be used to weaken command predictability in the current release

## Trust And Recovery Posture

Nexus should eventually present trust, recovery, and post-login continuity as one coherent experience layer, but the repo is not there yet.

Current merged truth should still be read as:

- desktop orchestration first
- future boot and access planning deferred
- product trust and resident presence concepts still living at planning level

## Resident Access And Privacy Visibility

Nexus should eventually expose a resident access surface that feels like a doorway into the system-facing assistant experience, not a replacement for the full Dashboard, Settings, NCP, or AI Command Center.

Durable direction:

- the primary resident entry should be one Nexus Desktop AI tray icon by default
- the tray icon should provide compact status and route the USER to the right full surface instead of becoming a deep command wall
- privacy-critical AI/provider/permission/cache state should not depend only on Windows tray visibility, because Windows can hide third-party tray icons
- privacy-critical state should also be visible through a Nexus status panel, HUD/status surface, AI Command Center, or equivalent USER-facing surface when those owners are implemented
- USER-configurable quick-access slots are valid, but immutable privacy and control entries should remain easy to find
- future second-icon AI status behavior remains USER-gated and should be justified only if one icon plus status surfaces cannot communicate privacy state safely

The durable feature-category owner is `Docs/family_feature_visions/F3-FF01.md`. FAM-003 owns resident access and quick-action interaction; FAM-002 owns visual presentation; FAM-006 owns Monitoring/HUD, Recording Studio, and Log Viewer surfaces; FAM-007 plus `Docs/ai_runtime_and_trust_architecture.md` own AI/provider/privacy status truth; FAM-008 owns installer/setup education for tray visibility and startup behavior.

## Local AI And Capability-Pack Vision

This section records public-safe FAM-007 local AI and capability-pack direction.

This is future product intent, not evidence that provider execution, memory, indexing, setup, or heavy local models are available. Those features require their own consent, privacy safeguards, technical implementation, and verification.

FAM-007 should be staged so the base app remains useful without a local LLM and heavy local AI remains optional capability-pack work rather than default installer bloat.

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
- no-provider behavior should degrade into an Assisted Desktop Mode rather than feeling broken
- provider choice should not replace ORIN/ARIA as the user-facing assistant layer

### Privacy Model

- privacy-first defaults are non-negotiable
- retain as little user data as practical and avoid unnecessary persistence
- avoid third-party monitoring or exposure where a local or first-party path can satisfy the need
- user trust, visibility, and local control are primary design constraints
- Local Only, Local Network, External API, and No AI Provider states should be visible when those modes exist
- external API use should be opt-in, revocable, and cost/privacy-aware

### Execution Model

- the intended direction is hybrid and local-first
- local logic should handle common tasks, routing, and assistant orchestration
- external fallback should remain optional and reserved for queries that exceed reasonable local capability
- even when external help is used, the product should still feel like a local system extension rather than a thin client for a remote dependency
- provider boundaries should be defined before implementation so local, LAN, external API, and test providers can be swapped without changing the ORIN-facing product shell
- hardware safety, power state, thermals, and model/capability-pack requirements should gate what the user can enable on a given machine

### Technology Exploration

- Python is the primary exploration path for orchestration and rapid iteration
- C++ is a candidate path for performance-critical components
- GPU acceleration is preferred where officially supported and validated; NVIDIA CUDA, AMD-supported paths, Windows DirectML / Windows ML / ONNX Runtime, and CPU fallback should be considered by capability and maintenance cost
- Java and C# remain open integration paths where platform or tooling fit warrants them
- this is exploration space, not a locked implementation stack

### Visual Identity Principles

- the UI should read as a direct extension of the assistant rather than as a separate utility wrapped around it
- the visual layer should represent AI state, handoff state, and boundary changes clearly
- AI behavior and UI feedback should stay aligned so the product feels coherent rather than split into "assistant" and "tool"

### Explicit Non-Goals For Current Release

- do not treat this section as current implementation truth
- do not introduce large local models or heavy local inference in the current release
- do not enable provider/model behavior without explicit user consent and technical safeguards
- do not treat vision text as evidence that provider/model behavior already works
- do not put private prompts, plans, or personal data in public product material
- -
### Public-Safe Planning Carry-Forward

The first public-safe AI experience should establish truthful local behavior before provider or model execution.

Public-safe planning principles to carry forward:

- define Assisted Desktop Mode and no-provider behavior first
- preserve the Edition Capability / Trust Boundary model in `Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md` before implementing provider/model/runtime work
- define provider boundaries before tying ORIN to any model, runtime, or vendor
- define visible privacy/provider state before any external call path exists
- define hardware, power, and performance safeguards before enabling local heavy workloads
- define model/capability-pack license, integrity, disk-space, and update migration rules before distribution
- define data classification, memory, context packing, consent, audit, secrets, and trust reset before indexing or learning work
- keep Windows compatibility and safe repair paths first-class
- keep Boot-Facing Mode and secure sign-in work future/high-risk
- keep full internal Dev ORIN/private prompt/eval/beta-feedback tooling outside public repo truth unless later sanitized and approved

## Historical Relationship

Older Nexus releases remain historical records. They do not define the current public Nexus experience or imply that future capabilities are implemented.

## Relationship To Other Canon Layers

- use `Docs/architecture.md` for architectural boundaries
- use `Docs/ai_runtime_and_trust_architecture.md` for cross-family AI runtime/trust architecture, AI operational cache controls, permission-state, deterministic routing, Trust Journal, and capability-pack architecture
- use `Docs/orchestration.md` for orchestration behavior and runtime ownership
- use `Docs/boot_access_design.md` for future boot-access planning
- use `Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md` for Public, Dev, and Owner edition trust boundaries
- use `Docs/family_feature_visions/` for concrete feature-category behavior and deferred product dependencies.
