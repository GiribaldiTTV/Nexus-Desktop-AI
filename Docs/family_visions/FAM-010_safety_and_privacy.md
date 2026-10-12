# Pending Fold Source: Safety And Privacy

## Purpose

This file is retained only as no-loss source material while safety/privacy direction is folded into existing backlog-family visions and architecture owners.

This is retained product-design source, not a standalone active feature family. Safety and privacy requirements apply within product features that handle the affected data or actions.

Local-first privacy, consent, provider-visible data boundaries, safety gates, secrets handling, data egress controls, and future AI safety posture now fold into the implementing family vision and `Docs/ai_runtime_and_trust_architecture.md` where relevant.

## Vision Summary

Safety and Privacy should be visible product behavior, not hidden policy. Users should understand what data stays local, what could leave the machine, what is disabled, what is degraded, and what choices they control.

## Accepted Direction

- Privacy-first defaults are non-negotiable.
- Local-only, local-network, external API, and no-provider modes should be visible when those modes exist.
- Provider-visible data must be explicit before prompts, provider setup, or model execution occur.
- Public, Dev, and Owner privacy boundaries must remain separate: Owner-private memory/prompts/secrets and Dev-only tooling must not leak into public source, public artifacts, or Public Edition runtime.
- Secrets handling, memory, indexing, learning, and personalization require explicit user consent where they use personal data, visible controls, defined privacy boundaries, and tested failure and recovery behavior before they are enabled.
- AI operational cache privacy belongs here for visibility, provenance, sensitivity classes, profile/user isolation, encryption expectations, Local-Only Mode, Privacy Lockdown behavior, stale-cache refusal, provider-cache sanitization, Trust Journal cache events, and clear-cache safety; cache remains distinct from memory.
- Permission state must be enforced app state, not a verbal promise; sensitive capability classes must be denied, revoked, privacy-blocked, safety-blocked, or provider-blocked in behavior as well as UI.
- Trust Journal / AI Activity Journal direction belongs here for plain-language visibility into provider/network use, permission-blocked attempts, sensitive capability access, cache events, safety refusals, privacy lockdown, and competitive-integrity blocks.
- Privacy Lockdown and Local-Only Mode must block hidden provider egress, provider cache use, sensitive cache writes, and external fallback unless a later USER-approved policy explicitly permits an exception.
- Competitive-integrity enforcement must block hidden automation, anti-cheat bypass, protected-process tampering, game-memory manipulation, exploit tooling, recoil/aim assistance, botting, and packet manipulation independent of prompt wording.
- Identity recognition is consent-based only and does not approve identity memory, camera/microphone/desktop vision, or personalization by itself.
- Deferral is acceptable when local capability is not safe, practical, or approved.

## Implementation Boundaries

- This vision does not admit provider execution, network calls, memory/indexing, secrets handling, external APIs, or capability-pack execution.
- Safety/privacy controls belong to the product feature handling the affected data or action and must offer clear disable and recovery behavior.
- AI-related features must verify permission state, Trust Journal behavior, Local-Only mode, Privacy Lockdown, provider-visible data, cache privacy, and sensitive-capability boundaries before treating those controls as usable.

## Fold Targets

- Project vision: `Docs/nexus_vision.md`
- AI runtime and trust architecture: `Docs/ai_runtime_and_trust_architecture.md`
- Edition capability / trust boundary release plan: `Docs/family_visions/FAM-007_ai_edition_capability_trust_boundary_release_plan.md`
- Backlog registry: `Docs/feature_backlog.md`
- Existing FAM vision records when their implementation touches privacy, safety, consent, provider-visible data, Local-Only, Privacy Lockdown, Trust Journal, or sensitive capability surfaces
- Roadmap posture: `Docs/prebeta_roadmap.md`
