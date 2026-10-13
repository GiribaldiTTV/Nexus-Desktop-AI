# Nexus Pre-Beta Roadmap

## Purpose

This roadmap describes product milestones and feature direction. It does not assert that a planned feature is implemented.

## Product Milestones

| Family | Product Focus | Design Reference |
| --- | --- | --- |
| `FAM-001` Boot Interface | Boot and desktop startup | `Docs/family_visions/FAM-001_boot_interface.md` |
| `FAM-002` Desktop Interface | Desktop interface and visual consistency | `Docs/family_visions/FAM-002_desktop_interface.md` |
| `FAM-003` Interaction and Actions | Shared actions, interaction and tray access | `Docs/family_visions/FAM-003_interaction_and_actions.md` |
| `FAM-004` Voice and Audio | Voice, audio and diagnostics | `Docs/family_visions/FAM-004_voice_and_audio.md` |
| `FAM-005` External Integrations | External trigger and plugin integrations | `Docs/family_visions/FAM-005_external_integrations.md` |
| `FAM-006` Monitoring and HUD | Dashboard, monitoring, HUD, active-overlay recording and log viewing | `Docs/family_visions/FAM-006_monitoring_and_hud.md` |
| `FAM-007` Local AI and Capability Packs | Local AI readiness, capability packs, provider states and private/public trust boundaries | `Docs/family_visions/FAM-007_local_ai_and_capability_packs.md` |
| `FAM-008` Packaging and Install Experience | Packaging and install experience | `Docs/family_visions/FAM-008_packaging_and_install_experience.md` |

## Folded Non-Family Concept Pointers

Workspace/data and safety/privacy are not roadmap milestone families or independent backlog worktrees after the AI-native taxonomy repair. Each feature family includes the applicable workspace, data and privacy constraints.

| Concept Area | Consumed By |
| --- | --- |
| Workspace/data roots, evidence paths, cache storage, support bundles, cleanup, backup/export, and local file hygiene | Existing FAM visions and `Docs/ai_runtime_and_trust_architecture.md` where the implementing family touches those surfaces |
| Safety/privacy, consent, provider-visible data, secrets, Local-Only, Privacy Lockdown, Trust Journal, and sensitive capabilities | Existing FAM visions and `Docs/ai_runtime_and_trust_architecture.md` where the implementing family touches those surfaces |

## Current Schedule Reading

Pre-Beta remains active until the product milestones above are satisfied. Release readiness depends on tested product behavior, packaging, and a reproducible source/build baseline. Version and tag information must reflect the actual published release.

No release, tag, GitHub Release, artifact upload, issue closeout, branch cleanup, worktree cleanup, runtime implementation, provider/model execution, downloads, memory/indexing, voice/Core sync, shortcut/installer work, AI Product Contract import, or Private Dev ORIN import is authorized by this roadmap.
