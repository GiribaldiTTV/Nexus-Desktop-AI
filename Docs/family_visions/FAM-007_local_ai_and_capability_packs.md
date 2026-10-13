# FAM-007 Local AI And Capability Packs Vision

## Purpose

This family vision records durable product direction for local AI, provider setup, provider readiness, consent posture, consent collection, capability packs, model lifecycle, local-only privacy boundaries, provider-visible data, execution gates, memory/future learning boundaries, and Core/Desktop AI state.

## Vision Summary

Local AI and capability packs should make Nexus feel smarter while preserving local-first trust, explicit provider boundaries, clear consent, hardware safety, and useful no-provider behavior.

## Accepted Direction

- The base app should remain useful without a local LLM.
- Heavy local AI should remain optional capability-pack work, not default installer bloat.
- Assisted Desktop Mode and no-provider behavior should be defined before real provider execution.
- Owner, Dev, and Public AI deployment must follow the public-safe Edition Capability / Trust Boundary plan before provider/model/runtime work claims release readiness.
- Provider-visible data, privacy mode, hardware eligibility, network/download behavior, and memory/indexing boundaries must be explicit before runtime execution.
- External API use should be opt-in, revocable, cost/privacy-aware, and visible.
- AI Operational Cache Controls belongs here only for AI runtime/provider cache behavior, capability-pack cache manifests, cache provenance, cache validity windows, deterministic versus advisory cache behavior, and provider-cache sanitization; cache is operational state, not memory.
- ORIN remains the stable assistant identity across local models, external providers, no-provider mode, and capability-pack changes.
- Deterministic routing, reliability tiers, capability self-awareness, provider orchestration, and cache replay safety must follow `Docs/ai_runtime_and_trust_architecture.md` before implementation-specific FAM-007 slices can claim readiness.
- Capability packs should declare what they can do, what they cannot do, what sources they contain, what hardware/storage/provider state they require, what cache/index state they own, and whether they are local-only or provider-assisted.
- Provider recommendation is allowed when local capability is insufficient, but execution remains permission-gated and provider-visible data must be explicit before anything leaves the machine.
- AI status shown in tray, HUD, Dashboard, or future AI Command Center surfaces must reflect real permission, provider, local-only, privacy-lockdown, capability-pack, cache, memory, and blocked/degraded posture; UI copy must not overstate runtime capability.
- The visible top-most AI hub surface name is `AI Dashboard`. `AI Control Center` remains a focused FAM-007 control domain/card inside AI Dashboard, not the whole top-most AI window. Internally, the accepted durable product model is `AI Home / Control Foyer`: the top-level AI orientation and control-entry model that tells the USER what AI exists, what state it is in, what is safe or blocked, and where to go for each AI subsystem.
- AI Dashboard should keep top-level content compact, orienting, trust-critical, immediately useful, or navigational. Detailed reports, diagnostics, setup flows, logs, selectors, provider internals, capability details, memory/cache/private setup, and long workflows should route through categories, child/domain windows, Global Settings, or future-gated placeholders instead of becoming permanent stacked top-level cards unless a deliberate product design provides a safe focused route.
- AI Dashboard category cards are doorways, not workspaces. Each top-level category card should contain compact status/summary plus launcher buttons that open the relevant external-unique or exclusive child/domain window for the AI Dashboard. Local AI Check, readiness report generation/results, diagnostics details, provider internals, capability details, setup, settings internals, proof data, and maintenance lifecycle details must run or display inside the opened window rather than inline in the AI Dashboard hub.
- AI Dashboard child/domain windows created by this feature must use Nexus-native product chrome, not generic Windows OS title bars. The child-window model is custom frameless NDAI chrome with compact product window controls, real launcher click paths, non-overlapping default placement near the Dashboard, and full-desktop plus focused proof that the opened windows are not helper-created substitutes.
- AI Dashboard and AI Control Center placement decisions must classify AI-related items by role: top-level summary, top-level action, category doorway, focused surface, child/drill-down detail, settings route, maintenance lifecycle detail, diagnostic/status/trust-boundary, concrete USER-facing feature, future-gated placeholder, cross-FAM dependency support, or out-of-scope. The product usefulness standard is: runtime-visible status, blocked-state explanation, provider-visible-data `none`, and truthful unavailable-capability copy do not count as concrete features by themselves.
- AI Control Center category direction should start from USER jobs, including AI Control Center, AI Readiness / Diagnostics, Capabilities & Maintenance, Developer / Owner, Activity / Recovery, and AI Settings handoff when a working settings surface exists. The top level may show compact summaries and doorway actions; child/domain windows own deeper reports, setup, selectors, settings, logs, and long diagnostic content.
- Visible FAM-007 surfaces should reuse rendered Nexus components where suitable and verify appearance and interaction against real product references. An approximate screenshot or helper marker alone does not prove visual parity.
- Public-safe controls may show disabled provider, cache, memory, capability-install, Developer, and Owner states without activating private setup, execution, persistence, or agents.
- Provider documentation alone does not enable an integration. API keys, account connection, billing, model setup, and provider-visible data routing need user consent, secure handling, and working technical protections before use.

## Implementation Boundaries

This vision does not itself implement provider SDKs, models, downloads, network calls, memory, indexing, voice/Core sync, installer behavior, or private edition setup. The public-safe AI Dashboard can show truthful local status, local actions, and child/domain windows without implying those capabilities are available. Provider execution, data transfer, cache persistence, memory, and installation remain disabled until their actual user controls and safeguards work.

## Canonical Pointers

- Project vision: `Docs/nexus_vision.md`
- AI runtime and trust architecture: `Docs/ai_runtime_and_trust_architecture.md`
- Resident access FFV: `Docs/family_feature_visions/F3-FF01.md`
- Edition capability / trust boundary release plan: `Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md`
- Provider-state validator: `dev/orin_ai_provider_state_validation.py`
