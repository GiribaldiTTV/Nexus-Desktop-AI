# F7-FF01 Public-Safe Assisted Desktop AI Interaction And Edition Boundary

Family Feature Vision ID: `F7-FF01`
Parent FAM: `FAM-007`
Feature Category: `Public-Safe Assisted Desktop AI Interaction And Edition Boundary`
Category-Level Purpose: `Define the durable public-safe local AI interaction category for visible ORIN status, no-provider assistance, provider-visible-data transparency, capability-pack eligibility, and edition-boundary explanation before provider/model execution, downloads, memory, private setup, or packaging execution exists.`
USER-Facing Surfaces: `ORIN / AI status surface, local assist action, deterministic no-provider result view, provider-visible data none display, capability-pack eligibility and blocked install-intent display, and Public / Developer / Owner lane boundary explanation.`
Experience Flow: `The USER sees ORIN local AI status, opens or clicks a local assist surface, receives deterministic no-provider guidance, confirms provider-visible data remains none, sees capability-pack install/download intent blocked, and understands Developer and Owner lanes as future-gated boundaries.`
Included Capabilities: `Visible local-only AI status, local assist action, deterministic no-provider result copy, provider-visible-data transparency, capability-pack eligibility display with blocked install intent, public-safe edition boundary copy, and validation proof that provider/model execution, prompt send, downloads, cache, memory, private setup, and hidden network behavior remain blocked.`
Explicit Non-Goals: `Provider/model execution, prompt send, provider account setup, model or capability-pack download, capability-pack install/update/uninstall/execution, runtime cache behavior, memory/learning/personalization/indexing, real Owner agents, private Developer or Owner setup, private assets/logs, and shortcut/installer/packaging execution.`
Durable Feature Element Inventory: `F7-FF01-E01 - Public Edition AI / ORIN status, purpose: make local AI posture visible, proof expectation: UI/status plus provider-state contract proof, future boundary: no provider/model implication; F7-FF01-E02 - local assisted desktop action, purpose: provide a useful no-provider local action, proof expectation: action-click result plus no-egress checks, future boundary: public-safe local state only; F7-FF01-E03 - deterministic no-provider result flow, purpose: produce truthful local guidance, proof expectation: result fixture and provider-visible data none proof, future boundary: no prompt/provider path; F7-FF01-E04 - capability-pack eligibility with blocked install intent, purpose: explain possible capability packs without installation, proof expectation: blocked install/download proof, future boundary: actual pack setup deferred; F7-FF01-E05 - Public / Developer / Owner lane boundary display, purpose: separate public-safe behavior from private lanes, proof expectation: public leak-prevention proof, future boundary: private setup deferred; F7-FF01-E06 - provider/download/memory/cache/network enforcement proof, purpose: prove gated AI behavior remains blocked, proof expectation: provider-state, leak-prevention, no-egress, and no-persistence checks, future boundary: gated execution deferred; F7-FF01-E07 - future provider/model execution; F7-FF01-E08 - future capability-pack install/download execution; F7-FF01-E09 - future memory/learning/personalization; F7-FF01-E10 - future private Developer/Owner setup; F7-FF01-E11 - future shortcut/installer/packaging identity execution.`
Design Options: `Option A keeps status-only AI visibility and is easy but too inert; Option B routes into provider setup and is too broad for the public-safe no-provider category; Option C is the recommended path, using local assisted interaction with deterministic no-provider results while preserving provider, download, memory, private, and packaging gates.`
Proof Expectations: `Verify visible local-only status, a working deterministic no-provider action, provider-visible data none, blocked capability-pack install intent, edition boundaries, and the absence of provider/model execution or private data leakage.`

## FFV Identity

FFV ID: `F7-FF01`

FFV Category: `Public-Safe Assisted Desktop AI Interaction And Edition Boundary`


Parent Family: `FAM-007 Local AI and Capability Packs`

Durable Category Scope: `Public-safe local assisted AI interaction, no-provider result behavior, provider-visible-data explanation, capability-pack eligibility display, blocked install intent, and Public / Developer / Owner lane boundary presentation before provider/model execution or private setup exists.`

## Product Boundary

This feature provides public-safe assisted desktop interaction without provider execution. It does not turn on provider/model calls, downloads, capability-pack installation, memory or learning, or private Developer/Owner setup. Those capabilities need their own product behavior, consent, safety, and technical prerequisites.

## Vision Basis

Related product contracts:

- `Docs/nexus_vision.md`
- `Docs/feature_backlog.md`
- `Docs/family_visions/FAM-007_local_ai_and_capability_packs.md`
- `Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md`
- `Docs/ai_runtime_and_trust_architecture.md`
- `Docs/family_visions/FAM-008_packaging_and_install_experience.md`

FAM-007 direction requires the base app to remain useful without a local LLM. Assisted Desktop Mode and no-provider behavior should be understandable before any real provider execution. Provider-visible data, provider state, capability-pack eligibility, and edition boundaries must be visible and truthful without activating hidden network, prompt, model, download, memory, or private-edition behavior.

## Feature Purpose

The user-facing purpose is to make ORIN's AI posture visible, useful, and honest in the Public Edition before a provider or local model is connected.

The durable product target is not "make the provider work." The target is a public-safe assisted interaction layer that can say what Nexus can do locally, why provider execution is unavailable, what data would be visible to a provider, and which future capability or edition gates remain blocked.

## Category Boundary

This feature covers public-safe assisted desktop interaction and edition boundaries for FAM-007.

## AI Dashboard / AI Control Center Ontology And Placement Contract

Visible Top-Most AI Hub Surface Name: `AI Dashboard`

Focused Control Domain/Card Name: `AI Control Center`

Internal Product Model: `AI Home / Control Foyer`

Durable Definition: `AI Dashboard is the FAM-007-owned top-level AI orientation and control-entry surface. It tells the USER what AI exists, what state it is in, what is safe or blocked, and where to go for each AI subsystem. AI Control Center is a focused control domain/card inside AI Dashboard for persona, capability, provider/model readiness, Developer / Owner lane, and AI permission/control-plane posture.`

Top-Level Admission Rule: top-level AI Dashboard content must be compact, orienting, trust-critical, immediately useful, or navigational. The top level may show a Global AI Strip, AI truth summaries, category doorway cards, and launcher actions that open the correct external-unique or exclusive child/domain window for the AI Dashboard. Category cards are doors, not workspaces. Permanent stacked top-level report bodies, setup flows, logs, selectors, provider internals, capability-pack detail tables, memory/cache/private setup content, direct local-check execution, direct readiness-report generation/results, and long diagnostics are disallowed unless a deliberate product design adds a focused, safe route.

Child/Domain Window Chrome Rule: for the AI Dashboard, opened AI category windows must render through Nexus-native custom product chrome and must reject generic Windows title bars. Required proof includes a real Dashboard card launcher click path, custom compact minimize/close controls, opened-window classification as exclusive child or external unique, lifecycle proof, full-desktop proof, focused-window proof, and duplicate-screenshot rejection.

Placement Role Vocabulary:

- `Top-level summary`: compact truth about active AI, readiness, trust/provider, capability, lane, or recovery posture.
- `Top-level action`: a bounded launcher action that opens an approved focused surface without executing tests, reports, diagnostics, setup, provider/model behavior, or future-gated behavior by implication.
- `Category doorway`: a card or control that routes to a grouped AI subsystem such as Active AI, AI Readiness, AI Diagnostics, Trust & Provider, Capabilities, Developer / Owner, Activity / Recovery, or AI Settings handoff.
- `Focused surface / child surface / drill-down detail`: a separate approved child/domain window for the current AI Dashboard repair, or a suitable page, panel, or modal. It owns detailed reports, selectors, settings, logs, setup, diagnostics, or recovery flows.
- `Settings route`: a compact utility affordance that routes toward FAM-003 Global Settings / AI when available and remains future-gated when that surface is not implemented.
- `Maintenance lifecycle detail`: compact version/update/capability lifecycle placement that does not execute downloads, installs, updates, capability fetches, provider/model execution, packaging, shortcut mutation, or FAM-008 behavior.
- `Diagnostic / status / trust-boundary`: truthful provider, prompt, model, download, cache, memory, private-lane, or capability state explanation that does not count as a concrete feature by itself.
- `Concrete USER-facing feature`: a useful outcome the USER can intentionally produce beyond blocked-state explanation, status, or proof. The behavior must deliver a useful result beyond unavailable or blocked-path explanation.
- `Future-gated placeholder`: honest disabled or deferred route that does not imply implementation.
- `Cross-FAM dependency support`: narrow dependency context for FAM-002, FAM-003, FAM-006, FAM-008, or another feature without duplicating the other feature.
- `Out-of-scope`: any content requiring unapproved provider/model execution, prompt send, downloads, runtime cache behavior, memory/learning/personalization, private Developer/Owner setup, installer/shortcut/packaging execution, private setup, import, or release actions.

Recommended Category Taxonomy: `AI Control Center`, `AI Readiness / Diagnostics`, `Capabilities & Maintenance`, `Developer / Owner`, `Activity / Recovery`, and `AI Settings` when the settings route exists. `Active AI` and `Trust & Provider` may exist as compact state inside the Global AI Strip or an opened domain window, but this product must not duplicate them as redundant top-level category cards.

Readiness Report Placement: the local AI readiness report remains a valid concrete local decision-aid behavior when it gives the USER ready/missing/blocked conditions, evidence checked, safe next steps, provider-visible-data `none`, and enforced trust boundaries. Its Local AI Check action, report generation action, detailed body, copy action, diagnostics detail, and results belong inside the `AI Readiness / Diagnostics` external-unique child/domain window in this product. The AI Dashboard top level may show a compact readiness summary plus an `Open` launcher, but must not run the local check, generate the report, copy the report, or display the full report body inline.

Visual Proof Carry-In: future visible FAM-007 surfaces must classify whether they use the accepted rendered DOM/CSS path, a future approved template/shared primitive, a reference-derived implementation, or a verified product exception. Reference-derived implementations remain unproven until side-by-side element-group visual adjudication, code-to-visual trace, proof artifacts, and the user-facing result is verified.

## User-Facing Surfaces

- ORIN / AI status surface in the desktop visual layer.
- Local assisted action entrypoint tied to that status surface.
- Deterministic result view for no-provider operation.
- Plain-language provider-visible data display.
- Capability-pack eligibility and blocked install-intent display.
- Public Edition, Developer lane, and Owner lane boundary presentation.

## Durable Experience Flow

1. The user sees an AI / ORIN status surface rather than a hidden or inert provider block.
2. The user activates a local assisted action.
3. Nexus reads only public-safe local app state and provider-boundary state.
4. The result explains that provider execution is unavailable or disabled.
5. The result states provider-visible data as `none` when no prompt/provider path ran.
6. The result names useful local follow-up actions.
7. The result shows capability-pack eligibility without starting download, install, update, uninstall, or execution.
8. Developer lane and Owner lane posture remains visible only as gated boundaries, not as private setup or private asset behavior.

## Durable FFV Element Inventory

These elements describe product behavior and safety boundaries, not current implementation status.

| FFV Element ID | Element | Durable User Value | Expected Surface / Flow | Boundary / Gate | Proof Expectation |
| --- | --- | --- | --- | --- | --- |
| `F7-FF01-E01` | Public Edition AI / ORIN status | The user can see whether AI assistance is locally available, degraded, disabled, or provider-blocked. | Visible ORIN / AI status in the Public Edition desktop surface. | Must not imply provider/model execution, prompt acceptance, network use, memory, or private setup. | UI/status proof plus provider-state contract proof. |
| `F7-FF01-E02` | Local assisted desktop action | The user can click a local action that is useful even without a provider. | Action control tied to the AI / ORIN status surface. | Reads public-safe local app state only; no prompt send, provider call, download, memory write, or external dependency. | Action-click result proof plus no-provider/no-egress checks. |
| `F7-FF01-E03` | Deterministic no-provider result flow | The user gets truthful local guidance instead of a broken or vague AI-disabled message. | Result panel or equivalent local response state. | Result must say provider execution is unavailable or disabled and provider-visible data is `none` when no provider path ran. | Deterministic result fixture, provider-visible-data proof, no hidden network proof. |
| `F7-FF01-E04` | Capability-pack eligibility with blocked install intent | The user can understand what capability packs could add without accidentally installing anything. | Eligibility summary and disabled or blocked install intent state. | Actual download, install, update, uninstall, model asset fetch, or capability execution remains future-gated. | Static/fixture proof that install intent is blocked and FAM-008 install authority is preserved. |
| `F7-FF01-E05` | Public / Developer / Owner lane boundary display | The user can distinguish public-safe behavior from future Developer and Owner capabilities. | Boundary labels or explanatory copy in the Public Edition surface. | No private repository, private root, private remote, private prompt, private memory, private log, or private asset exposure. | Public leak-prevention proof and product copy review. |
| `F7-FF01-E06` | Provider, download, memory, cache, and network enforcement proof | The product proves the public-safe path is not secretly executing gated AI behavior. | Validator, fixture, and technical proof surface; visible copy where useful. | Provider/model execution, prompt send, downloads, network/external calls, runtime cache behavior, memory, learning, indexing, personalization, and real Owner agents remain blocked. | Provider-state validation, public leak-prevention validation, and no-egress/no-persistence checks. |

## Deferred Capabilities And Dependencies

- `F7-FF01-E07` real provider/model execution: requires explicit user consent, a truthful provider-visible-data boundary, secure credentials, cost awareness, and rollback behavior.
- `F7-FF01-E08` capability-pack download, installation, update, removal, or execution: requires trustworthy sources, integrity and license checks, storage handling, setup and recovery behavior.
- `F7-FF01-E09` persistent memory, indexing, learning, personalization, or Owner memory: requires a separate user-controlled data lifecycle and privacy model.
- `F7-FF01-E10` private Developer or Owner setup: must not place private roots, prompts, logs, assets, or credentials in public product material.
- `F7-FF01-E11` shortcuts, installers, package identity, and update behavior: depend on the packaging feature's setup and recovery contracts.

The public-safe interaction consists of elements `F7-FF01-E01` through `F7-FF01-E06`. Deferred elements must remain visibly unavailable rather than appear as functioning controls.

## Design Options

Option A - Status-only AI surface:
This improves visibility, but it can still feel inert because the user cannot do anything useful inside the no-provider boundary.

Option B - Provider setup path:
This is outside the current public-safe feature because provider/model execution, prompt send, data egress, credentials, downloads, and cost/privacy behavior require separate user choices and technical safeguards.

Option C - Public-safe local assisted interaction:
This is the preferred public-safe behavior. It creates useful, clickable, deterministic no-provider behavior while preserving provider, private edition, memory, download, and packaging gates.

## Explicit Non-Goals

- Provider SDK integration.
- Provider account setup or API key creation.
- Model execution.
- Prompt acceptance or prompt send.
- Model or capability-pack download.
- Capability-pack install, update, uninstall, or execution.
- External API calls or hidden network behavior.
- Runtime cache behavior.
- Persistent memory, indexing, learning, personalization, or real Owner memory.
- Real Owner agents.
- Private Developer or Owner repositories, roots, remotes, prompts, logs, memory, evals, or assets.
- Backup or recovery execution.
- Voice/Core runtime sync.
- Shortcut, installer, packaging identity, or release artifact work.
- AI Product Contract import.
- Private Dev ORIN import.

## Proof Expectations

- The Public Edition AI / ORIN status surface is visible when implementation later begins.
- The local assisted action is clickable and produces a deterministic result.
- The result includes local capability, provider unavailable or disabled posture, provider-visible data `none`, and safe next actions.
- Capability-pack eligibility and blocked install intent appear without executing installation.
- Developer lane and Owner lane labels do not expose private content or private setup behavior.
- Provider/model execution remains disabled.
- Prompt acceptance and prompt send remain disabled.
- Downloads, installs, external calls, runtime cache behavior, memory writes, real Owner memory, and real agents remain blocked.
- Validation includes static contract proof plus UI/result-flow proof once implementation begins.
