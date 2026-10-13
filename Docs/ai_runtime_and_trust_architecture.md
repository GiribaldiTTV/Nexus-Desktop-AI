# AI Runtime And Trust Architecture

## Purpose

This document owns durable cross-family architecture, policy, and experience direction for AI-native behavior in Nexus Desktop AI.

It exists because AI-native planning crosses multiple families and should not turn FAM-007 into a catch-all or turn every important concept into a new backlog family.

Use this document for:

- AI runtime and trust architecture
- permission-state enforcement concepts
- deterministic routing and reliability tiers
- provider orchestration boundaries
- capability registry and capability-pack architecture
- AI Operational Cache Controls
- Trust Journal / AI Activity Journal direction
- routine, continuity, Windows Health, and competitive-integrity architecture boundaries

It does not own:

- backlog family identity
- active branch authority
- provider/model/runtime implementation approval
- memory approval
- installer or shortcut implementation
- private Dev / Owner repo truth
- release execution
- live operational state


## Relationship To Existing Owners

- `Docs/nexus_vision.md` owns project-wide AI-native product direction and ORIN experience intent.
- `Docs/architecture.md` owns current desktop/runtime stack boundaries.
- `Docs/orin_interaction_architecture.md` owns interaction-system architecture and the shared action model.
- `Docs/family_visions/FAM-007_local_ai_and_capability_packs.md` owns local AI, provider, capability-pack, and AI runtime family direction.
- `Docs/family_visions/FAM-008_packaging_and_install_experience.md` owns setup, install, cache-root UX, capability-pack installation, and user education direction.
- Existing FAM visions own family-local workspace/data and safety/privacy implications when their implementation touches those surfaces.
- Former workspace/data and safety/privacy backlog labels are not active backlog families. Their reusable AI-specific constraints are folded into this file and the relevant existing FAM visions.

## Taxonomy Placement

AI-native planning uses this classification by default:

| Concept | Source-Truth Class | Default Owner |
| --- | --- | --- |
| AI-native operating experience | Project-wide vision plus experience layer | `Docs/nexus_vision.md` and this file |
| AI Runtime And Trust Architecture | Architecture layer plus cross-family policy owner | This file |
| Permission-State System | Architecture layer plus cross-family policy owner | This file and relevant implementing FAM vision |
| Deterministic Routing Layer | Architecture layer | This file; implementation through admitted FAM-007 slices |
| Provider Orchestration Layer | Runtime subsystem plus FAM-007 architecture | FAM-007, constrained by this file and relevant safety/privacy family-vision text |
| Trust Journal / AI Activity Journal | Cross-family trust architecture plus policy-facing experience layer | This file and relevant implementing FAM vision |
| AI Operational Cache Controls | Architecture, policy, and runtime concern | This file, with family-specific ownership below |
| Capability-Pack System | Capability-pack domain plus FAM-007 runtime architecture | This file, FAM-007, and FAM-008; other FAMs consume constraints only when implementing their own surfaces |
| Routine Engine | Runtime subsystem or future package/slice candidate | This file and FAM-003 until USER admits a concrete package |
| Daily Continuity / Ambient Assistance | Experience layer | `Docs/nexus_vision.md` and this file |
| Competitive Integrity Layer | Cross-family policy plus lower-level runtime enforcement | This file and relevant implementing FAM vision |
| Windows Health Recommendation Pipeline | Architecture/package candidate | This file and the owning feature |

None of these classifications create a new FAM by themselves.

A future concept needs a defined user-facing behavior, owning feature, privacy boundary, and technical dependencies before implementation.

## AI-Native Operating Principles

Nexus Desktop AI should evolve toward an AI-native operating experience where Windows remains the host platform, Nexus becomes the visible experience layer, and ORIN remains the persistent cooperative assistant identity.

AI-native behavior must prioritize:

- truth over fluency
- visible boundaries over hidden state
- deterministic or tool-backed answers before generative improvisation when objective truth is available
- local-first execution where practical
- explicit provider and network boundaries
- user consent before sensitive capability activation
- calm, plain-language trust UX
- recoverable failure instead of opaque automation
- no silent escalation of permission, provider, memory, cache, routine, monitoring, install, or protected-process behavior

Provider fluency must not be mistaken for system reliability.

## Permission-State System

Permission must be enforced app state, not a verbal promise.

Allowed permission/capability states:

- `Installed`
- `Available`
- `Enabled`
- `Disabled`
- `Denied`
- `Suspended`
- `Revoked`
- `Requires Setup`
- `Requires Hardware`
- `Requires Consent`
- `Blocked By Privacy Mode`
- `Blocked By Safety Policy`
- `Blocked By Competitive Integrity Mode`
- `Blocked By Provider State`

The UI may describe these states, but UI copy is not the authority by itself. Runtime behavior, provider/network behavior, cache behavior, and tool access must align with the actual permission state.

Sensitive capability classes include camera, microphone, desktop vision, screen understanding, memory, identity recognition, Windows Health logs, file/document access, email review, finance/bills access, external API/provider use, local model execution, knowledge/capability packs, overlays, gaming/process-sensitive features, and protected-process interaction.

## Deterministic Routing Layer

Objective or safety-sensitive requests should route through deterministic, tool-backed, or validation-backed paths before generative responses when such paths exist.

Reliability tiers:

- `Deterministic`
- `High Confidence`
- `Advisory`
- `Creative/Open-ended`

Deterministic routing should account for:

- source availability
- tool capability
- permission state
- provider state
- confidence threshold
- freshness requirements
- citation or provenance needs
- safety and privacy policy
- refusal or uncertainty behavior

When an answer is advisory or uncertain, the product should say so plainly instead of letting confident wording hide weak proof.

## Provider Orchestration Boundary

ORIN remains the stable assistant identity. Providers, models, local runtimes, external APIs, and capability packs are replaceable capability extensions, not the product identity.

Provider/API behavior must preserve:

- user-controlled provider choice
- revocable external API use
- visible local-only, local-network, external-assisted, and no-provider states when those modes exist
- explicit provider-visible data before prompts or context leave the machine
- no hidden provider residue
- fail-closed behavior when provider state is missing, denied, revoked, or privacy-blocked
- clear no-provider Assisted Desktop Mode

Provider recommendation is allowed when local capability is insufficient, but provider execution remains permission-gated.

## AI Transparency Status Surfaces

AI, provider, permission, cache, memory, privacy, and capability-pack status must be visible when those states affect USER trust or behavior.

Durable direction:

- status copy must distinguish local-only, local-network, provider-assisted, no-provider, disabled, blocked, degraded, privacy-lockdown, and USER-consent-required states when those modes exist
- a tray icon may summarize AI state, but it cannot be the only privacy-critical status surface because Windows may hide third-party notification-area icons
- future AI Command Center surfaces should own detailed AI/provider/permission/capability-pack state review, while the tray or HUD may open those surfaces
- privacy-critical status should have at least one non-tray visible route such as Dashboard, HUD/status chip, AI Command Center, Trust Journal, or Settings
- UI labels must reflect enforced permission/runtime behavior, not promises; if provider execution, memory, cache, desktop vision, microphone, or sensitive capability behavior is not approved or enabled, the UI must say so plainly

`Docs/family_feature_visions/F3-FF01.md` owns the resident-access doorway and quick-action model. This file owns the AI trust/status truth that such surfaces must consume.

## Owner AI Operational Foundation Gates

Owner AI Operational Foundation Gates are public-safe control-plane scaffolds for future Developer and Owner AI work. They may define disabled states, explicit consent and install-intent states, artifact exclusion checks, lane-readiness gates, and prerequisite schemas before any private Owner/Developer setup or provider/runtime execution exists.

The gate contract must preserve:

- protected artifact exclusion from public source, shipped packages, support exports, and released artifacts
- provider-visible data of `none`, prompt/provider/model execution disabled, network/download/external calls blocked, and no hidden provider residue
- cache consent and memory consent as separate states; cache remains operational state and does not become durable user memory
- runtime cache behavior, memory writes, indexing, retrieval, learning, personalization, real Owner memory, and real Owner agents disabled until the user explicitly enables the specific behavior with its privacy safeguards
- capability-pack install intent as an explicit blocked or future-gated state before any download, install, update, uninstall, or execution path
- Developer lane and Owner lane readiness as future-gated identity/readiness states, not private repo/root/remote creation

`desktop/ai_provider_state.py` owns the static public-safe gate contract used by validators. `dev/orin_ai_provider_state_validation.py` and `dev/orin_public_leak_prevention_validation.py` must fail if a public-safe gate branch claims readiness while enabling private setup, provider/model execution, runtime cache behavior, real memory, real agents, private paths, secrets, or protected artifacts.

## OpenAI Docs / Developer Tool Boundary


OpenAI Developers tooling, API-key creation, provider setup, model/runtime setup, billing/quota state, account connection state, and provider-visible data routing are sensitive setup or implementation concerns. They must not be recorded in repo docs as current state, must not expose plaintext secrets, and must not imply provider/model execution is enabled.

When a future branch uses OpenAI or other provider tooling, it must separate:

- official documentation evidence from durable rule changes
- API key or credential setup from public documentation alone
- provider-visible data disclosure from a generic feature toggle
- provider/model execution from architecture planning
- private Dev/Owner setup from public repo evidence

When this boundary is unclear, keep provider actions unavailable and do not expose private references or credentials.

## Capability Registry And Capability-Pack System

Capability packs are modular capability domains, not automatic model-weight bundles and not automatic FAMs.

Capability packs may include:

- tools
- retrieval/index layers
- knowledge provenance metadata
- versioned/updateable modules
- source/citation-aware stores
- confidence-aware domain behavior
- storage, VRAM, RAM, power, or hardware requirements
- license metadata
- integrity metadata
- update and removal metadata
- local-only or provider-assisted mode declarations

Capability records should declare:

- what the capability can do
- what it cannot do
- whether it is installed, available, enabled, denied, revoked, blocked, or missing hardware
- which sources it contains
- what data it may read or write
- what cache/index state it owns
- what provider or local-runtime state it requires
- what privacy/safety constraints apply

## AI Operational Cache Controls

Cache is not memory.

Cache is operational, purpose-bound, explainable, clearable, policy-governed state.

Memory is durable user-personal knowledge and requires separate explicit consent.

AI operational cache controls cover provenance, validity, replay, and privacy. They are distinct from personal memory.

### Cache Ownership Split

- This file owns shared cache classes, replay safety, provenance, invalidation, and architecture/policy requirements.
- FAM-007 owns AI runtime/provider cache behavior, capability-pack cache manifests, deterministic/advisory cache behavior, and provider-cache sanitization.
- FAM-008 owns setup/install UX for cache roots, clear-cache flow, and user education.
- FAM-008 owns cache-root setup UX, storage-root selection, clear-cache education, and backup/export root guidance when packaging/setup work touches cache.
- Relevant implementing FAM visions own family-local data-root, evidence-path, privacy, Local-Only, Privacy Lockdown, and Trust Journal implications when their own work touches those surfaces.
- The owning AI feature must define cache invalidation, provenance, expiration, fallback, privacy, and rollback when cache behavior is implemented.

### Cache Scope Classes

| Scope Class | Description |
| --- | --- |
| Session cache | Temporary state needed only for the current interaction/session. |
| Operational cache | Short-lived operational state used to avoid recomputing safe local facts. |
| Deterministic validation cache | Cached objective tool results with strict input, provenance, permission, policy, and tool-version matching. |
| Advisory cache | Non-authoritative assistance state that requires freshness and confidence checks before reuse. |
| Provider-response cache | External-provider-derived material with sanitization, visibility, and retention limits. |
| Capability-pack index cache | Retrieval/index/cache data owned by capability packs. |
| Windows Health analysis cache | Diagnostic analysis state with confidence and freshness windows. |
| Temporary routine-context cache | Temporary routine/session context that expires or revalidates before sensitive reuse. |

### Cache Sensitivity Classes

| Sensitivity Class | Example | Required Posture |
| --- | --- | --- |
| Low | non-sensitive UI/session hints | clearable and bounded |
| Medium | Windows Health analysis cache | freshness, provenance, and journalable recovery |
| High | provider-derived summaries or user document-derived cache | provenance, retention limits, and privacy review |
| Very High | identity-sensitive, finance/email-adjacent, private path, or protected workflow cache | encryption expectation, local-only review, and explicit visibility |
| Critical | secrets, tokens, private owner memory, protected repo material | must not enter operational cache without a later explicit encrypted-vault policy |

### Cache Rules

Cache visibility should make operational cache categories understandable to users.

Cache provenance should record source, timestamp, provider/local mode, capability/tool owner, confidence basis, validity window, and whether the cache is deterministic, advisory, provider-derived, capability-pack-owned, or sensitive.

Cache invalidation should occur when source data, permission state, provider state, model version, tool version, capability-pack version, profile, privacy mode, Local-Only Mode, safety policy, or trust boundary changes.

Stale-cache detection must prevent old cache from silently powering objective answers, Windows Health recommendations, finance/email assistance, identity flows, provider-assisted summaries, safety-sensitive workflows, or recovery guidance.

Corruption recovery should detect, quarantine, rebuild, summarize, and journal cache recovery events rather than silently reusing damaged cache.

Deterministic cache and advisory cache must remain distinct. Deterministic validation cache may replay only when inputs, tool version, source provenance, permission state, and policy state still match. Advisory or provider-assisted cache must not replay as current truth without freshness and provenance checks.

Provider-cache sanitization should prevent private prompts, secrets, private paths, memory, identity data, sensitive logs, protected repo material, finance/email content, and private automation content from entering provider-facing cache unless a future USER-approved policy explicitly permits it.

Local-Only Mode should prohibit provider-cache reads/writes and hidden external cache dependencies.

Privacy Lockdown should suspend sensitive cache writes, block provider/cache egress, and make cache-block behavior visible.

The `clear all AI operational cache` flow should clear operational cache without pretending it deleted memory, Trust Journal entries, support logs, backups, or other separately governed records. The UX should explain what was cleared, what was not cleared, and which cache categories may rebuild later.

Trust Journal cache events should include sensitive cache writes, cache clears, stale-cache refusals, provider-cache use, privacy-lockdown blocks, local-only cache blocks, corruption recovery, replay/freshness decisions, and capability-pack cache rebuild/removal events.

## Trust Journal / AI Activity Journal

The Trust Journal should be plain-language, reviewable, and understandable by a non-technical user.

It should explain meaningful AI, provider, permission, cache, privacy, and safety events without becoming a noisy raw log.

Entry classes should include:

- capability access
- provider/network use
- permission-blocked attempt
- memory/index write or explicit no-write
- file/document access
- email/finance access
- routine action
- Windows Health recommendation
- restore/rollback action
- safety refusal
- competitive-integrity block
- privacy lockdown event
- cache writes, clears, stale-cache refusals, and corruption recovery

Trust Journal direction does not authorize telemetry, hidden monitoring, provider calls, memory, or runtime logging changes by itself.

## Routine And Daily Continuity Boundary

Routine and daily-continuity concepts are experience-layer and runtime-subsystem candidates by default, not new backlog families.

Routine states should include:

- `Suggested`
- `Previewed`
- `Approved`
- `Running`
- `Paused`
- `Completed`
- `Blocked`
- `Canceled`
- `Revised Pending Approval`

ORIN may recognize context and ask whether to begin a routine. It must not silently start sensitive or action-oriented routines without approval.


## Windows Health Recommendation Pipeline

Windows Health support should follow a conservative lifecycle:

1. Diagnose.
2. Recommend.
3. Prepare.
4. Request approval.
5. Execute only when approved and implemented.
6. Verify.
7. Summarize.
8. Log or journal the outcome where policy requires it.

Windows Health recommendations must separate observed evidence, inferred explanation, and uncertain hypothesis.

No Windows repair, system mutation, rollback, backup, installer, or support-bundle behavior is authorized by this architecture text.

## Competitive Integrity Layer

Competitive-integrity enforcement must sit below LLM/tool routing and block protected actions independent of prompt wording.

The system must not assist with hidden automation, anti-cheat bypass, game-memory manipulation, exploit tooling, recoil/aim assistance, botting, packet manipulation, protected-process tampering, or stealthy game advantage behavior.

When competitive-integrity policy blocks an action, the product should explain the block plainly and journal it when the Trust Journal policy requires it.

## Privacy Lockdown And Local-Only Guarantee

Privacy Lockdown should visibly block provider egress, sensitive cache writes, sensitive routine actions, identity-sensitive behavior, and any capability that cannot prove compliant local handling.

Local-Only Mode should be enforceable, not decorative. Provider calls, provider cache, provider-visible data, hidden external dependencies, and external fallback must be blocked while Local-Only Mode is active unless a later USER-approved exception is recorded.

## Identity Recognition Consent

Identity recognition must be consent-based only.

Identity-related capabilities require explicit permission state, clear revocation, visible disabled/degraded posture when denied, and separate handling from generic observation or interaction.

Identity memory is not approved by this document.

## Observation, Inference, And Confidence

Nexus should separate:

- directly observed evidence
- inferred explanation
- uncertain hypothesis

AI-native responses should preserve the feel of intelligent inquiry without over-claiming certainty. Deterministic routing improves accuracy; it must not flatten ORIN into a rigid calculator for diagnostic, planning, exploratory, or creative work.

Reliability classes:

| Reliability Class | Meaning | Default Proof Requirement |
| --- | --- | --- |
| `Deterministic` | Exact fact, state, path, command result, release truth, or permission result is required | Tool-backed, source-derived, or live-check proof; no LLM-only truth |
| `High Confidence` | Evidence-backed conclusion where deterministic proof may not cover every edge | cite evidence, confidence basis, and known uncertainty |
| `Advisory` | Recommendation, planning guidance, or tradeoff analysis | explain basis, alternatives, risks, and safe default |
| `Exploratory / Hypothesis` | Possible explanation, diagnostic reasoning, missing-context discovery, or evidence-gathering plan | label hypotheses, separate observations from inference, ask or propose next evidence |
| `Creative` | Open-ended generation such as naming, copy, layout, or brainstorming | stay inside safety/source-truth boundaries and require user-facing review before release |

Observation / Hypothesis / Validation Loop:

1. Notice the abnormality, user-stated goal, or uncertainty.
2. Separate observed evidence, learned pattern, inferred explanation, hypothesis, and validated truth.
3. Ask who/what/where/when/why/how questions when missing context controls the answer.
4. Form hypotheses only when deterministic proof is unavailable or incomplete.
5. Seek evidence before recommending meaningful action.
6. Communicate uncertainty calmly and without ego-like certainty.
7. Refine, reject, or validate hypotheses as evidence arrives.

Invalid reliability behavior:

- treating learned patterns or experience as unquestionable reality
- presenting hypotheses as facts
- using deterministic class to suppress useful exploratory reasoning
- using creative or advisory phrasing to bypass proof for objective facts
- recommending risky action before seeking available evidence

Confidence labels should include:

- `High confidence`
- `Likely`
- `Possible`
- `Uncertain`
- `Needs validation`

This distinction should inform user-facing explanations, Windows Health recommendations, deterministic routing, provider/tool routing, cache replay, and refusal behavior.

## Explicit Non-Goals

This document does not approve:

- provider SDK integration
- model downloads or model execution
- external API calls
- persistent memory, learning, indexing, or personalization
- camera, microphone, desktop vision, or screen understanding
- voice/Core sync
- installer, shortcut, packaging, backup, restore, or release artifact work
- private Dev ORIN or Owner-private planning import
- runtime cache implementation
- Trust Journal implementation
- Windows Health mutation or repair
- gaming/process-sensitive runtime behavior
- release execution
