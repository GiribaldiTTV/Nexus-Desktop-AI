# UIREF-003 Nexus Control State And Selector Grammar Reference

Reference ID: `UIREF-003`
Reference Name: `Nexus Control State And Selector Grammar`
Reference Class: `Button / Control State`
Owning Vision Layer: `Project UI Vision -> FAM-002 Desktop Interface -> F2-FF01 Nexus UI Reference System`

Related Product References: `Docs/nexus_vision.md`, `Docs/family_visions/FAM-002_desktop_interface.md`, and `Docs/family_feature_visions/F2-FF01.md`.


Applicable Surface Classes: `Nexus-owned primary, secondary, danger, disabled, hover, focus, selected, dirty, loading, empty, error, selector, dropdown, menu, list, filter, row, scrollbar, and compact command controls.`

Non-Applicable Surface Classes: `OS-native controls used inside platform-native exceptions, provider-owned web controls, and temporary developer-only controls that are not final product UI.`

Required Element Groups: `label/icon, purpose, placement, size, spacing, radius, border, glow/shadow, typography, contrast, disabled/degraded treatment, click/keyboard/focus behavior, and relationship to surrounding controls.`

Required States: `default, hover, focus, pressed, selected, disabled, loading, dirty, empty, error, blocked, unavailable, and accepted platform exception where applicable.`

Geometry / Resize / Accessibility Expectations: `Controls should remain readable, predictable, keyboard/focus navigable where relevant, and consistent enough that changing text does not create a new visual family.`

Proof Artifacts: `FAM-006 tray menu/dashboard controls and FAM-007 Run Local Check/scrollbar evidence provide seed examples. They do not prove every selector, dropdown, menu, list, or filter state.`

Known Limitations: `Open dropdown/menu/list/filter state proof, keyboard/accessibility proof, disabled/loading/error proof, and full selector matrices are incomplete. This reference is accepted as baseline grammar; consuming branches must prove any control state they create or claim.`


Validator / Helper Guidance: `Future helpers should fail generic "button looks good" claims, copied-file-list-only proof, missing state matrix, missing disabled/blocked state, unclassified platform control usage, and USER-facing controls that diverge from UIREF-003 without accepted exception.`


