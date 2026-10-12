# UIREF-005 Nexus Design Token And Shared Rule Baseline

Reference ID: `UIREF-005`
Reference Name: `Nexus Design Token And Shared Rule Baseline`
Reference Class: `Proof / Review Surface`
Owning Vision Layer: `Project UI Vision -> FAM-002 Desktop Interface -> F2-FF01 Nexus UI Reference System`

Source Evidence: `Docs/nexus_vision.md`, `Docs/family_visions/FAM-002_desktop_interface.md`, `Docs/family_feature_visions/F2-FF01.md`, selected FAM-006/FAM-007 comparison evidence, and the consolidated Package A-E runtime proof packet.


Applicable Surface Classes: `Nexus-owned product windows, cards, rows, controls, status surfaces, proof surfaces, dialogs, command centers, studios, dashboards, settings surfaces, and resident doorway surfaces.`

Non-Applicable Surface Classes: `External/provider/OS surfaces, platform-native exceptions, and temporary developer-only diagnostics not presented as final Nexus UI.`

Required Element Groups: `color roles, typography roles, spacing and density, radius, border, glow/shadow, disabled/degraded states, scrollbar treatment, window-frame treatment, action hierarchy, and proof-surface readability.`

Required States: `default, hover, focus, pressed, selected, disabled, loading, degraded, blocked, error, empty, and platform-native exception where applicable.`

Geometry / Resize / Accessibility Expectations: `Design rules must preserve readability, predictable interaction, stable hierarchy, and enough contrast for long-session use. Future code-level tokens must prove source-to-visual trace instead of relying on prose alone.`

Proof Artifacts: `Project UI Vision and FAM-002 grammar provide durable product law; FAM-006/FAM-007 evidence provides comparison input. No code-level shared primitive is promoted by this record.`

Known Limitations: `Accepted token values, shared CSS/component implementations, code-to-visual trace, contrast audits, migration/rollback plans, and product-worktree adoption are not implemented by this product reference. Those remain future implementation work, not current PR blockers after this disposition.`


Shared Primitive Example: `nexus_visual/nexus_window_primitives.css` can supply common Recording Studio and Log Viewer chrome and controls. Each consuming window still needs rendered, interactive, and accessibility checks before reuse is claimed.

Validator / Helper Guidance: `Future helpers should flag branches that claim design-token implementation without a code carrier, claim shared primitives exist by inference, or skip visual proof because a design-rule baseline exists.`


