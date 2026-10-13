# FAM-006 Monitoring And HUD Vision

## Purpose

This family vision records durable product direction for Monitoring HUD, Dashboard, Sensor Command Center, Sensor Library, monitor configuration, Overlay Profile, active-overlay-driven recording, local telemetry presentation, and user-facing performance/health surfaces.

## Vision Summary

Monitoring and HUD should give the user clear, trustworthy, polished visibility into system and sensor state without fake telemetry, proof clutter, broken/deferred controls, or confusing ownership between Dashboard, Overlay, Core, and settings windows.

## Accepted Direction

- Dashboard should act as the polished control hub, not a debug/proof panel.
- New Dashboard, HUD, Overlay Profile, Monitor Group, Recording, Sensor Command Center, or child-window UI must sample from the existing FAM-006 visual system before introducing any new visual grammar.
- Provider, telemetry, no-data, degraded, disabled, and warning states must be truthful.
- Overlay Profile and Monitor Group concepts should remain distinct and reviewable.
- Recording should be active-overlay-driven, not a separately loaded Recording Profile. The active Overlay Profile determines what is recorded.
- User-facing elements should be visually consistent and inspectable in their normal desktop context.
- Visual-system inheritance includes new cards, rows, controls, dividers, empty/deferred states, status fields, and child-window surfaces must match established FAM-006 color tokens, shape/radius, spacing, typography, row/divider treatment, button effects, hover/focus/disabled states, shadows/glows, scrollbar treatment, and layout density with deliberate product design exceptions documented.
- Visual-system inheritance means shared design DNA, not component cloning. Standalone, non-child windows such as Recording Suite and Log Viewer Studio do not need Dashboard card layouts, but they must visibly share the FAM-006/HUD chrome, color, opacity, typography, button, row/divider, glow, state, spacing, and density grammar.
- Deferred actions should be disabled, removed, or clearly labeled; they must not look broken.
- Monitoring, HUD, telemetry, screenshots, recordings, logs, and support evidence must preserve local file hygiene, clear evidence roots, privacy-safe review posture, and no fake or hidden data collection.
- Sensitive telemetry, recording, overlay, process, or performance surfaces must make provider/external telemetry boundaries explicit before any external data path is admitted.
- Resident tray quick access may link to HUD Dashboard, Recording Suite, or Log Viewer Studio after those FAM-006 surfaces exist, but the tray must not own recording state, monitoring state, log-reader internals, or sensor/telemetry truth.
- Recording Suite and Log Viewer Studio are future FAM-006 user-facing surfaces; tray entries should open them as polished owning surfaces rather than turning the tray menu into a recording or log-control workspace.
- Verify user-facing monitoring and recording behavior through the normal desktop launcher; diagnostic launches are supporting evidence only.
- Troubleshooting runtime launcher evidence may support diagnosis and may substitute for normal launcher proof only when USER consent and launcher parity proof show the diagnostic profile does not change the behavior being validated.
- Visible FAM-006 closeout claims require photo/video or ordered frame-sequence proof; claims that cannot be proven visually must be elevated to USER manual validation, explicit waiver, or blocker rather than treated as proven by logs, markers, or helper PASS alone.
- Runtime logs, Dev Toolkit events, and manifests should prove state consistency, bridge delivery, window lifecycle, recording target/log consistency, and failure diagnosis, but they do not replace USER-facing visual proof.

## Family UI Vision Carrydown

FAM-006 carries the Project UI Vision from `Docs/nexus_vision.md` into monitoring, HUD, Dashboard, overlay, recording, and evidence surfaces.

Family-specific UI requirements:

- Monitoring and HUD surfaces should preserve comfort through calm status hierarchy, readable density, and clear no-data/degraded-state copy.
- Futuristic styling must stay standardized: underglow, card chrome, gutter spacing, dashboard/HUD/shell/window spacing, row/divider treatment, button effects, hover/focus/disabled states, shadows/glows, scrollbars, and layout density should remain visually related across FAM-006 surfaces.
- Similar actions such as Start, Stop, Select Folder, Open, Save, Clear, Retry, and Export should inherit the project-wide control grammar unless a deliberate FAM-006 product exception is justified and verified.
- Proof surfaces should help the USER judge product behavior; they must not turn the product UI into a debug wall or expose internal worktree/branch state as product copy.

## Recording Vision

- Recording should be intuitive and automatically connected to the currently active Overlay Profile.
- Recording should not require a separate Recording Profile, duplicate monitor groups, or a recording-specific sensor chooser. The active Overlay Profile and its active membership define the recording target.
- Recording belongs in its own compact Dashboard Recording card, separate from the HUD Overlay card.
- The Dashboard Recording card shows the selected recording target and status; controls appear only when they work and share truthful recording state.
- The Dashboard Recording card must look and behave like an existing Dashboard hub card. It should reuse the standard Dashboard card chrome, badge treatment, state-row/divider grammar, copy scale, action-button style, disabled/future-gated affordance, hover/focus effects, spacing, and density from the HUD Overlay, Monitor Groups, Data Sources, and Readiness cards unless the Dashboard visual system is deliberately changed and verified.
- Recording-specific styling must not introduce a unique card color family, nested boxed table, custom row shape, custom glow, or separate visual hierarchy that makes the Recording card feel detached from the standardized Dashboard card format.
- The HUD Overlay card should stay focused on overlay identity, Overlay Profile state, Overlay Status, and overlay-specific actions. It should not host recording-specific controls or be the primary recording launcher after this vision revision.
- Keep recording centered in the Dashboard card unless an additional standalone surface has a real user purpose and coherent route.
- Recording output should save first as a native NDAI recording log owned by Nexus Desktop AI. The native log is the canonical product artifact for NDAI readback, future in-app viewing, and validation.
- Excel/CSV, JSON, or other third-party readable files are export artifacts, not the default recording save. Export requires a USER-requested export flow with supported file-type choices and validation that the exported file opens/readably displays in the target class of software.
- The Dashboard Recording card may open the exported-log folder, but normal Start/Stop recording must not auto-create CSV or other third-party export files. Until an export feature exists, manual CSV files may be created only as validation artifacts outside the product-native log folder.
- Native Log Loader is a future separate graph/log viewer that reads completed recording logs over time. It is not the recording control surface and is not admitted for implementation by the active-overlay recording contract alone.

## Future Effective Polling Policy Vision

- Future FAM-006 architecture should support per-overlay effective polling policy so the same Monitor Group can be reused by multiple Overlay Profiles with different effective polling intervals.
- Example future target: a Gaming Overlay can use CPU Group and GPU Group at 1 second polling, while a Lightweight Overlay can use the same groups at 3 second polling.
- The desired long-term model should avoid duplicate Monitor Groups such as CPU Group FAST and CPU Group SLOW merely to change polling cadence.
- Recording should eventually inherit the active overlay's effective runtime policy when recording output is admitted.
- Keep the recording target model compatible with future per-overlay effective polling policy without implementing that policy by inference.

## HUD Overlay Card Vision

- The HUD Overlay card should place Overlay Profile first, then Overlay Status.
- The currently selected Overlay Profile row may show active monitors for overlay clarity, but recording target/status explanation belongs in the Dashboard Recording card after the 2026-06-02 USER design revision.
- Overlay Profile Settings should have a stable location that future additions do not move. Preferred locations are either the HUD Overlay card title row on the right side or the bottom-right action position.
- Future recording controls should not displace the stable Overlay Profile Settings location and should not move back into the HUD Overlay card without a deliberate product redesign.

## Implementation Boundaries

- This vision does not admit recording runtime, tray recording controls, broad theme/skin work, provider expansion, or external telemetry by itself.
- This vision does not admit resident tray implementation by itself; FAM-003 owns resident access interaction and `Docs/family_feature_visions/F3-FF01.md` owns the tray doorway category.
- This vision does not admit hidden monitoring, external telemetry, provider-visible telemetry, support-bundle export, backup/export, or cleanup/deletion behavior by itself.
- The recording target should follow the active Overlay Profile; avoid retaining a competing profile-loaded direction without a clear migration for existing user data.
- Verify target, status, visual states, native log output, and failure/recovery behavior in the affected product surfaces.
- A changed monitoring or recording UI should visibly inherit the accepted FAM-006 colors, shape, spacing, typography, effects, interaction states, and density, or explain a product-specific exception.
- Reuse a shared rendered primitive for same-class controls when it exists; otherwise compare affected controls side by side for consistent appearance and behavior.
- Keep normal recording and monitoring logs minimal and privacy-safe. Diagnostic collection requires clear user control and a return to normal behavior.

## Canonical Pointers

- Project vision: `Docs/nexus_vision.md`
- Resident access FFV: `Docs/family_feature_visions/F3-FF01.md`
- AI runtime and trust architecture: `Docs/ai_runtime_and_trust_architecture.md`
- Backlog registry: `Docs/feature_backlog.md`
- Recording Family Feature Vision: `Docs/family_feature_visions/FAM-006_recording.md`
