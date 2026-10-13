# UIREF-007 Window Geometry And Resize Contract

Reference ID: `UIREF-007`<br>
Reference Class: `Window Geometry / Resize`<br>
Related product design: `Docs/nexus_vision.md`, `Docs/family_visions/FAM-002_desktop_interface.md`, and `Docs/family_feature_visions/F2-FF01.md`.

This reference applies to Nexus-owned top-level windows, dashboards, detached or embedded child surfaces, settings/tools, studios, and dialogs that own geometry, resizing, scrolling, or responsive behavior. Platform-owned security prompts, OS pickers, provider-auth windows, and temporary diagnostic surfaces may use platform conventions.

For each applicable surface, define a minimum usable size, default size, maximum useful size, and whether maximize or fullscreen is supported. Verify resize edges and cursors, breakpoints, reflow, scrolling, wrapping, truncation, active-content/footer attachment, DPI, monitor changes, narrow/portrait layouts, and recovery from an unavailable saved monitor. A compact window should not become a tiny island in a large empty shell. Dashboard space should be used meaningfully rather than filled by global zoom.

Window classes include compact settings/tool, dashboard/parent, embedded child, detached child, modal/dirty guard, and platform-native exception. `Child Window` without a parent relationship, `Resizable` without a size policy, and `Looks Good At Default Size` are insufficient descriptions.

Derive layout from content constraints, tokens, breakpoints, or shared primitives where available. Foreseeable same-class rows and controls should fit without screenshot-tuned pixels. This does not enable deferred functionality. FAM-003 may expose a user-accessible reset route; the consuming feature owns its own window behavior. Each surface needs actual rendered and interactive verification against the applicable reference, including full-window context where placement or footprint matters.
