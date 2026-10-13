# Nexus Product Family Visions

Each family vision describes the user outcome, visible and non-visible behavior, safety and privacy boundaries, failure and recovery behavior, and relationships to other product features. Feature-category records in `Docs/family_feature_visions/` add detail for individual capabilities. These documents describe the product; they do not track current development status.

A family vision should be specific enough to guide an implementation and an affected-behavior check. User-visible claims require real interaction and rendered-state evidence; automated source checks support but do not replace that observation. Deferred capabilities remain unavailable until their implementation, dependencies, consent, and recovery behavior are actually ready.

## Product Families

| ID | Family | Vision |
| --- | --- | --- |
| FAM-001 | Boot Interface | `FAM-001_boot_interface.md` |
| FAM-002 | Desktop Interface | `FAM-002_desktop_interface.md` |
| FAM-003 | Interaction and Actions | `FAM-003_interaction_and_actions.md` |
| FAM-004 | Voice and Audio | `FAM-004_voice_and_audio.md` |
| FAM-005 | External Integrations | `FAM-005_external_integrations.md` |
| FAM-006 | Monitoring and HUD | `FAM-006_monitoring_and_hud.md` |
| FAM-007 | Local AI and Capability Packs | `FAM-007_local_ai_and_capability_packs.md` |
| FAM-008 | Packaging and Install Experience | `FAM-008_packaging_and_install_experience.md` |

Workspace/data and safety/privacy constraints are described in `FAM-009_workspace_and_data.md` and `FAM-010_safety_and_privacy.md`. They apply to the product features that actually handle those concerns.
