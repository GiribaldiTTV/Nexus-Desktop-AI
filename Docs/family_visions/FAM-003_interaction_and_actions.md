# FAM-003 Interaction And Actions Vision

## Purpose

This family vision records durable product direction for shared actions, command/action UX, callable groups, taskbar/tray quick-task interaction, saved action authoring, and user-visible confirmation/interaction contracts.

## Vision Summary

Interaction and Actions should feel predictable, explicit, and easy to trust. Advanced grouping and action behavior should grow from proven exact-match and user-controlled primitives instead of hidden inference.

## Accepted Direction

- Keep pre-Beta callable groups explicit, exact-match, and member-driven.
- Preserve confirmation and boundary clarity for user-triggered actions.
- Treat richer grouping, discovery, recommendation, or query behavior as later post-proof expansion.
- Keep action authoring, built-in action expansion, and tray/quick-task behavior tied to clear validation proof.
- Treat the Nexus resident tray icon as a doorway and status beacon, not the full command center.
- Own the primary tray tooltip and compact status copy. AI/provider/privacy truth comes from the AI state owner; the tooltip is not the only privacy-critical state surface because Windows may hide tray icons.
- Treat the resident tray tooltip/status implementation as existing product dependency evidence for FAM-007 AI status work, not a frozen AI/privacy design. FAM-007 owns AI/provider/privacy status taxonomy, permission-state truth, provider-visible-data truth, Trust Journal or AI Command Center detail routing, and real Privacy Lockdown enforcement. If those product requirements expose a mismatch, update the affected tray scaffold, route, copy, indicator, or infrastructure and validate the visible behavior.
- Keep the resident tray menu compact, with core Nexus actions, safety/status doorways, state-dependent optional feature doorways, and a small USER-configurable Quick Access section rather than a command wall. The Windows taskbar tray icon right-click menu must not carry long status/header text; resident status belongs in the tray-icon hover tooltip, the styled fallback/status surface, or the owning full surface. The compact native tray menu should start with Global Settings, place Quick Access immediately below Global Settings, use categorized submenus such as Quick Access and AI when grouping reduces top-level clutter, keep Exit Nexus easy to find, and defer Developer/Owner menu categories until FAM-007 admits the relevant Dev/Owner model semantics.
- Treat immutable or unremovable resident routes as stable route identity/order/behavior when a route is admitted and enabled, not as forced visibility after USER opt-out.
- Show optional feature doorways only when enabled/admitted, or show them disabled with an owner-bounded reason when the USER wants the feature but it is temporarily blocked, errored, or not ready. Hide optional feature rows from active tray/menu UI when the USER disables them during setup or Global Settings, when the feature is not installed, when it is unsupported, or when the state is unknown enough that the tray/menu would overclaim.
- Adopt the Nexus UI Exposure Contract locally for FAM-003 resident, tray, menu, and minimal Global Settings surfaces: visible product UI may expose only real, enabled/available, or meaningfully shown owner-backed items. Future categories, deferred controls, unowned internals, not-installed surfaces, unsupported surfaces, disabled-by-USER features, and unknown state must stay hidden unless they are useful owner-bounded status, setup/configuration, unavailable-with-reason, or future-gated context.
- Keep Global Settings and Exit Nexus discoverable. The AI status doorway may remain visible, while detailed trust status comes from AI state. Do not show Privacy Lockdown as functioning until it performs the promised action.
- Own the minimal Nexus Tray & Quick Access settings controls used by the resident doorway; do not show unrelated, non-actionable categories as product settings.
- Quick Access settings must make edit state explicit: slot add/remove/reorder/dropdown changes are pending until saved, Revert restores the last saved model, Use Defaults or equivalent reset-default control stages documented defaults instead of silently saving, and closing or chrome-close behavior must not silently lose pending changes.
- Route deep task/group authoring, NCP management, Recording Studio, Log Viewer Studio, AI controls, full app-wide settings, and owner-specific settings internals into their owning full surfaces rather than duplicating every command in the tray menu or resident settings foundation.
- Treat reset-window-position/size actions for standalone Nexus-owned product windows as a resident access / Global Settings / quick-action dependency route when the reset must be user-accessible across families.
- Prefer one primary Nexus tray icon by default; a second AI privacy/status icon is future-gated and requires USER-approved evidence that one icon plus visible status surfaces cannot communicate privacy state safely.
- Verify resident, tray, and runtime-window icon behavior through the real visible product path. Packaging owns installed shortcuts and startup identity.
- AI-native routines and ambient assistance are optional experiences, not automatic background actions. They require clear user controls and truthful availability.
- Routine/action UX must preserve inspectable resolution, explicit confirmation, revocation/back-out paths, and plain-language trust posture before sensitive actions run.

## Implementation Boundaries

- This vision does not admit dynamic natural-language grouping, autonomous scheduling, or broad recommendation behavior.
- This vision does not admit AI routine execution, background monitoring, memory, provider calls, Windows Health repair, or sensitive automation by itself.
- This vision does not admit Windows system-tray pinning control, OS-owned Sound/Network/Mic cluster integration, unhide/unpin prevention, or any claim that Nexus can force third-party tray icon permanence.
- This feature provides the Nexus Tray & Quick Access settings foundation; other settings retain their own feature behavior.
- Offer a window-position/size reset route only for eligible windows with safe visible defaults.
- Validate the affected user flow, safety boundary, failure state, and recovery behavior.

## Canonical Pointers

- Project vision: `Docs/nexus_vision.md`
- Resident access FFV: `Docs/family_feature_visions/F3-FF01.md`
- AI runtime and trust architecture: `Docs/ai_runtime_and_trust_architecture.md`
- Backlog registry: `Docs/feature_backlog.md`
