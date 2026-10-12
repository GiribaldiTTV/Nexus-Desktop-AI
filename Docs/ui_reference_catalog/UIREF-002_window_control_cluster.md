# UIREF-002 Nexus Window Control Cluster Reference

Reference ID: `UIREF-002`
Reference Name: `Nexus Compact Window Control Cluster`
Reference Class: `Window Control Cluster`
Owning Vision Layer: `Project UI Vision -> FAM-002 Desktop Interface -> F2-FF01 Nexus UI Reference System`

Related Product References: `Docs/nexus_vision.md`, `Docs/family_visions/FAM-002_desktop_interface.md`, and `Docs/family_feature_visions/F2-FF01.md`.


Applicable Surface Classes: `Nexus-owned top-level, standalone, restorable, independently opened, movable, resizable, or geometry-persisted product windows where close, minimize, maximize, restore, drag, or resize controls are meaningful.`

Non-Applicable Surface Classes: `modal confirmations, child panels, footer/content actions, one-shot proof/dev windows, OS/platform-native surfaces, and product surfaces with a recorded USER-approved control exception.`

Required Element Groups: `close control, minimize control when applicable, maximize/restore control when applicable, disabled/hidden controls when not applicable, hitbox, accessible name, tooltip or equivalent discoverability where needed, hover/focus/pressed states, and content-action separation.`

Required States: `default, hover, focus, pressed/clicked, disabled or hidden when a control is not applicable, blocked/unavailable with explanation when applicable, and platform-native exception when applicable.`

Geometry / Resize / Accessibility Expectations: `Controls must remain compact, clearly window-level rather than content-level, visually secondary except for close when intentional, keyboard/focus reachable where applicable, and large enough for reliable pointer interaction.`

Proof Artifacts: `FAM-007 close-hover and default control screenshots provide accepted proof seed. The recorded duplicate minimize-hover screenshot remains a known limitation rather than independent minimize-hover proof.`

Known Limitations: `Independent visual evidence for minimize-hover, maximize/restore, disabled, focus, pressed, and hitbox states is incomplete. Consuming features must substantiate only the states they actually verify and identify unproven states as incomplete.`


Validator / Helper Guidance: `Future helpers should flag default OS chrome, large header CLOSE on a top-level window without exception, missing minimize/maximize applicability, missing accessibility label proof, and screenshots that claim hover state while hashing identically to default state.`


