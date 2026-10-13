# Nexus Product Feature Families

This index names the broad product families. The linked vision files describe their behavior and boundaries. Current development status and repository workflow are outside this product index.

## FAM-001 — Boot Interface

Startup, boot, desktop entrypoint, single-instance ownership, launch handoff, relaunch semantics, lifecycle transition proof, boot-to-runtime trust boundaries, fatal launcher/runtime diagnostics, and recovery surfaces.

Product detail: [Docs/family_visions/FAM-001_boot_interface.md](family_visions/FAM-001_boot_interface.md)

This family covers fatal launcher/runtime diagnostics and recovery surfaces. A recoverable `launch_failed` case does not imply a complete recovery system.

## FAM-002 — Desktop Interface

Nexus desktop shell, visual language, operator UI, settings presentation, user-facing desktop interaction surfaces, and coherent UI/UX implementation packages.

Product detail: [Docs/family_visions/FAM-002_desktop_interface.md](family_visions/FAM-002_desktop_interface.md)

## FAM-003 — Interaction and Actions

Shared actions, command/action UX, callable groups, taskbar/tray quick-task interaction, saved action authoring, and user-visible confirmation/interaction contracts.

Product detail: [Docs/family_visions/FAM-003_interaction_and_actions.md](family_visions/FAM-003_interaction_and_actions.md)

## FAM-004 — Voice and Audio

Voice availability, audio path direction, voice diagnostics, truthful disabled/degraded copy, and future persona/audio capability boundaries.

Product detail: [Docs/family_visions/FAM-004_voice_and_audio.md](family_visions/FAM-004_voice_and_audio.md)

## FAM-005 — External Integrations

External trigger intake, plugin integration, external control surfaces, and safe integration boundaries.

Product detail: [Docs/family_visions/FAM-005_external_integrations.md](family_visions/FAM-005_external_integrations.md)

## FAM-006 — Monitoring and HUD

Monitoring HUD, Dashboard, Sensor Command Center, Sensor Library, monitor configuration, Overlay Profile, Recording Profile, local telemetry presentation, and user-facing performance/health surfaces.

Product detail: [Docs/family_visions/FAM-006_monitoring_and_hud.md](family_visions/FAM-006_monitoring_and_hud.md)

## FAM-007 — Local AI and Capability Packs

Local AI, provider setup, provider readiness, consent posture, consent collection, capability packs, model lifecycle, local-only privacy boundaries, provider-visible data, execution gates, memory/future learning boundaries, and Core/Desktop AI state.

Product detail: [Docs/family_visions/FAM-007_local_ai_and_capability_packs.md](family_visions/FAM-007_local_ai_and_capability_packs.md)

Real provider/model execution, data sharing, capability-pack installation, memory, and private edition behavior require their respective consent, security, and runtime prerequisites; they are not enabled by their presence in this index.

## FAM-008 — Packaging and Install Experience

Installer, shortcuts, packaged app experience, model/capability-pack install boundaries, update flow, and user-facing setup lifecycle.

Product detail: [Docs/family_visions/FAM-008_packaging_and_install_experience.md](family_visions/FAM-008_packaging_and_install_experience.md)
