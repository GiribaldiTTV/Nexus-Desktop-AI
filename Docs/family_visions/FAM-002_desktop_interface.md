# FAM-002 Desktop Interface Vision

## Purpose

This family vision records durable product direction for the Nexus desktop shell, visual language, operator UI, settings presentation, user-facing desktop interaction surfaces, and coherent UI/UX implementation packages.

FAM-002 supplies shared presentation and interaction rules for Nexus-owned desktop surfaces. The feature owning a surface retains its behavior.

## Vision Summary

The Desktop Interface should feel intentional, native to Nexus, and visually coherent across windows, cards, controls, settings, and proof surfaces. It should not collapse into generic utility UI or proof-heavy engineering panels.

## Accepted Direction

- Inspect affected user-facing surfaces in their real rendered and interactive states.
- Define the layout, control states, accessibility, and behavior expected for each affected surface.
- Preserve visual identity, control hierarchy, and reviewability as product requirements, not cosmetic afterthoughts.
- Keep dev/proof scaffolding out of production UI unless explicitly admitted.
- Resident status panels, tray-opened panels, Global Settings, AI Status / Command Center, and quick-access configuration surfaces should follow the Nexus visual hierarchy instead of becoming generic utility popups.
- Tray-accessible surfaces should keep the tray as a doorway: compact entry in the tray, full explanation and configuration in polished Nexus windows.
- Visible diagnostics, failure, degraded-state, recovery, support-bundle, manual-reporting, and repair-option panels consume FAM-002 presentation standards when they are shown to the USER.
- Feature surfaces use FAM-002 presentation rules when shared desktop controls or window behavior apply.
- FAM-003 owns resident tray doorway behavior while consuming FAM-002 presentation standards; FAM-006 owns Recording Studio / Log Viewer behavior and related UI; FAM-007 owns AI Status / Command Center behavior and related UI; FAM-008 owns installer, setup, shortcut, update, patch/restart, and tray-visibility education behavior and related UI.

## NDAI Window Chrome And Immersion Contract

FAM-002 owns the reusable presentation law for Nexus-owned windows and panels. Final product surfaces should not expose default Windows title bars, unstyled native utility chrome, generic button rows, or platform-looking popup shells when the surface is meant to be a Nexus product window.

The expected presentation is Nexus-native: custom product framing or chrome, coherent title/header treatment, matching close/minimize/back/settings affordances where applicable, consistent card/button/list/scrollbar language, readable spacing and density, and deliberate disabled/degraded/recovery states. A consuming FAM may specialize the layout for its feature, but it must inherit this presentation grammar or record a USER-approved exception.

Platform-native file pickers, OS security prompts, provider authentication, and installer trust surfaces may use platform chrome when that treatment protects the user or follows platform requirements. Keep the exception visually and behaviorally clear.

## Top-Level Window Control Grammar Standard

FAM-002 owns the reusable top-level window-control grammar for Nexus-owned product windows. A Nexus-owned top-level, standalone, restorable, independently opened, movable, resizable, or geometry-persisted product window must distinguish window-level controls from content actions. Window-level close, minimize, maximize, restore, drag, and resize behavior must use a compact Nexus-native control cluster or recorded equivalent window-control grammar when those actions are applicable to the window.

A large labeled header `CLOSE` pill is clear and may remain valid for modal dialogs, child windows, footer actions, content-level actions, confirmation flows, temporary proof/dev surfaces, platform-native exceptions, or USER-approved exceptions. It is not the default top-level window-control grammar for standalone Nexus product windows because it can read as a content action, compete with footer buttons, and blur the boundary between closing a window and completing or cancelling work. If a branch keeps a large header `CLOSE` on a top-level product window, it must record why the exception is intentional and prove it does not conflict with footer/content actions.

Top-level control clusters must remain Nexus-native rather than default Windows chrome. Expected behavior includes compact placement, readable icons or symbols, accessible names, hover tooltips, generous hitboxes, keyboard/focus treatment, default/hover/pressed/focus/disabled states, visually secondary minimize/maximize/restore controls, and a close control that is neutral by default unless danger context or hover treatment is intentionally admitted. Consuming FAM branches own their feature-window behavior and proof. FAM-003 owns only user-accessible reset/recovery routes when a global or doorway-level action is admitted; it does not own normal close/minimize/maximize/restore behavior by inference.

## Standalone Window Geometry Recovery Standard

FAM-002 owns the reusable presentation and geometry standard for Nexus-owned product windows. Any Nexus-owned standalone, top-level, restorable, independently opened, movable, resizable, or geometry-persisted product window must define safe default position/size behavior and a USER-accessible reset path so the USER can recover from offscreen placement, missing-monitor movement, corrupted saved geometry, too-small/too-large windows, or layout changes.

The reset route must preserve Nexus presentation grammar: clear language, predictable placement, visible recovery feedback, and no debug-looking utility popup unless a platform/native or troubleshooting exception is recorded. Each feature owns its window behavior and verification. FAM-003 owns the resident access / quick-actions / settings route when the reset action is a global or user-accessible Nexus command. Child panels, anchored panels, OS dialogs, temporary dev/proof tools, or non-restorable surfaces may be Not Applicable only when the reason is technically justified.

## Window Geometry And Resize Contract Standard

FAM-002 also owns the reusable presentation law for window geometry, resize, responsive layout, and size-state composition. `Docs/ui_reference_catalog/UIREF-007_window_geometry_resize_contract.md` is the product reference for minimum/default/maximum/fullscreen policy, breakpoint/reflow behavior, DPI and display-scale posture, multi-monitor and portrait/narrow-monitor proof, content overflow handling, sparse wide-state prevention, and feature-specific behavior.

Same-class Nexus-owned windows should feel deterministic, intuitive, immersive, predictable, reliable, and consistent across size states. A compact tool window may stay compact or define a purposeful wide-state treatment. A dashboard / parent-class window may grow, but the extra room must be meaningful through composition, reflow, richer density, or bounded scroll. A detached child window or detached child dashboard must say whether it behaves like its parent, owns independent geometry, or needs a justified product exception.

Each feature owns its layout and behavior while using the relevant geometry and resize rules. Verify affected sizes, display scales, and exception states before calling that surface ready.

## Reusable Component Grammar

FAM-002 supplies reusable presentation grammar for:

- product window chrome, frame shape, title/header treatment, close/minimize/back/settings affordances, and resize/drag behavior
- panels, studios, dashboards, command centers, settings windows, status panels, diagnostics panels, and tray-opened product surfaces
- cards, rows, dividers, page breaks, chips, badges, status fields, empty/error/degraded/blocked states, warning banners, confirmation dialogs, and recovery panels
- primary, secondary, danger, disabled, hover, focus, selected, dirty, loading, and future-gated control states
- scrollbars, dropdowns, list rows, input fields, folder/file pickers when Nexus owns the presentation, and compact/expanded layout density
- USER-facing proof readability, so validation or diagnostics surfaces remain understandable product surfaces instead of debug walls

A feature may specialize the shared grammar for a real product need, but should retain recognizable controls, accessible states, and consistent window behavior.

When a missing shared primitive causes a real visual or interaction defect, implement the smallest reusable primitive that fixes the affected surface and verify the rendered result.

## Future-Proof UI Composition Standard

FAM-002 expects Nexus-owned UI to be composed so foreseeable same-class additions can be added without hand-tuning a new one-off visual or layout system. A row, card, control cluster, dropdown, filter, list, dialog, status panel, scrollbar, or window frame should derive its size, spacing, alignment, state treatment, and overflow behavior from the inherited grammar, accepted reference, template, shared primitive, content contract, or named constraint. For example, a value column should derive from label/content rules plus a fixed gutter or documented constraint, not from a magic pixel that only works for the current row count or current screenshot.

Future-proof composition should leave room for foreseeable same-class additions without adding unavailable features or relying on screenshot-tuned layouts.

## Component Anatomy And Element-Group Acceptance

FAM-002 treats reusable UI components as visible element groups with anatomy, state, and proof expectations. A component is not accepted merely because a helper marker exists or a screenshot was captured.

For shared UI components such as close/minimize/back/settings affordances, primary/secondary/danger buttons, dropdowns, cards, rows, scrollbars, confirmation dialogs, dirty guards, status chips, and window chrome, consuming FAM branches should identify the component anatomy that matters to the USER experience:

- visible label/icon and purpose
- placement and relationship to surrounding controls
- size, spacing, radius, border, shadow, glow, and density
- typography, color, contrast, and disabled/degraded treatment
- default, hover, focus, pressed, selected, dirty, loading, disabled, error, empty, and danger states when applicable
- input behavior for mouse, keyboard, focus, scroll, resize, close, save, discard, cancel, and delete paths when applicable
- inherited reference surface, accepted grammar, or USER-approved exception

Judge affected elements against concrete rendered behavior, reference examples, accessibility, and interaction states. Vague visual praise alone cannot establish a usable component.

Same-class shared elements should use the same primitive when practical. Text-only variations should retain height, gutter symmetry, typography, radius, border, glow, interaction states, and accessibility.

## Consumption Model

- FAM-002 rules apply to product surfaces that use shared desktop presentation.
- The feature owning a surface implements its behavior while using the applicable FAM-002 rules.
- Shared desktop components may be implemented centrally when they benefit multiple real product surfaces.
- Ownership Split: FAM-002 supplies shared presentation rules; the consuming feature owns its behavior, feature-specific UI implementation, and validation of visible states.
- Non-Capture Rule: consuming features apply FAM-002 only to relevant shared presentation, preserve other features' behavior, and account for real product dependencies.
- Failure/Recovery UI Rule: FAM-002 supplies visual hierarchy, control grammar, disabled/degraded affordance, and panel presentation law for visible diagnostics or recovery UI; FAM-001 owns fatal launcher/runtime recovery meaning, and the consuming FAM owns feature-specific failure behavior.

## Implementation Boundaries

- This vision does not admit a UI overhaul by itself.
- This vision does not admit tray implementation, shortcut mutation, installer behavior, AI Command Center implementation, or privacy-state runtime behavior by itself.

## Canonical Pointers

- Project vision: `Docs/nexus_vision.md`
- UI reference-system FFV: `Docs/family_feature_visions/F2-FF01.md`
- Promoted UI reference catalog: `Docs/ui_reference_catalog/`
- Resident access FFV: `Docs/family_feature_visions/F3-FF01.md`
- Backlog registry: `Docs/feature_backlog.md`
- Roadmap posture: `Docs/prebeta_roadmap.md`
