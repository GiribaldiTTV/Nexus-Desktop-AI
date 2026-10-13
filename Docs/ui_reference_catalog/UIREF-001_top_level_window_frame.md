# UIREF-001 Nexus Top-Level Window Frame Reference

Reference ID: `UIREF-001`<br>
Reference Class: `Top-Level Window`<br>
Related product design: `Docs/nexus_vision.md`, `Docs/family_visions/FAM-002_desktop_interface.md`, and `Docs/family_feature_visions/F2-FF01.md`.

Applies to Nexus-owned standalone, restorable, movable, resizable, or geometry-persisted product windows. OS security prompts, file pickers, provider-auth browser windows, and other platform-owned trust surfaces use their native controls.

A Nexus product window uses coherent custom chrome, a clear title/header, content frame, accessible window-control cluster, and a resize affordance when resizable. Persisted geometry needs a safe reset or offscreen-recovery route. Verify focused, unfocused, resized, restored, and relevant blocked/unavailable states at supported display sizes.

AI Control Center provides a compact top-level visual reference; HUD/Dashboard surfaces provide a comparison for larger parent layouts. A consuming feature must still verify its own window class, geometry, accessibility, and justified platform-native exceptions. A screenshot or marker alone does not prove those behaviors.
