# FAM-006 Recording Family Feature Vision

Family Feature Vision ID: `F6-FF01`
Parent FAM: `FAM-006`
Feature Category: `Recording`
Category-Level Purpose: `Durable Recording feature-category direction for capturing trusted local Monitoring/HUD output through Overlay Profile targets, native NDAI logs, USER-requested exports, and compact user-facing control surfaces.`
USER-Facing Surfaces: `Dashboard Recording Card; Dashboard quick access when admitted; Recording Suite; Log Viewer shell and later viewer; native log folder; exported-log folder; tray/keybind/settings surfaces when later admitted.`
Experience Flow: `USER selects or creates an Overlay Profile, sees Recording target/readiness on the Dashboard, starts/stops through an admitted control surface, receives native NDAI output, and later reviews or exports logs through admitted Log Viewer flows.`
Included Capabilities: `Target/status display; Overlay Profile target mirroring; Start/Stop when admitted; native NDAI output/readback; exported-log access when admitted; Recording Suite planning; Log Viewer planning; tray/keybind/settings planning; Overlay Profile persistence dependency review.`
Explicit Non-Goals: `Provider/model execution, FAM-007 behavior, automatic third-party-readable export, and a complete Native Log Loader are outside this Recording feature.`
Durable Feature Element Inventory: `F6-FF01-E01 - Dashboard Recording Card target/status surface and visual inheritance proof; F6-FF01-E02 - Recording Suite focused control/status surface and window proof; F6-FF01-E03 - Log Viewer native/export shell and future viewer boundary; F6-FF01-E04 - native NDAI log artifact model and readback proof; F6-FF01-E05 - USER-requested export artifact model and readability proof; F6-FF01-E06 - tray/keybind/settings future-control boundaries; F6-FF01-E07 - Overlay Profile persistence dependency for recording target reliability.`
Deferred Feature Carryforward: `deferred item rows preserve title, dependency trigger, grouping recommendation, proof expectation, and durable disposition for Recording Suite, Log Viewer, exported logs, tray controls, keybinds, settings, warning dismissal, Overlay Profile persistence dependency, Dashboard quick access, and Native Log Loader relationship.`
Design Options: `Option F planning solidification before implementation-shape selection; Option C/C-lite Dashboard Recording Card plus Recording Suite plus minimal Log Viewer shell; Start/Stop ownership options; Studio minimize behavior options; direct log-folder button versus Log Viewer access; native-only versus native-plus-explicit-export artifact options.`
Proof Expectations: `Verify target selection, visible state, normal user activation, native output/readback, profile-specific log consistency, failure and recovery behavior, and affected visual/accessibility states.`
Visual Check: `Inspect actual Recording Suite, Log Viewer, and Dashboard card appearance and interactions against their product purpose before calling those surfaces usable.`

## Purpose

Recording captures trustworthy local output from the selected Overlay Profile. This document describes the Dashboard Recording Card, Recording Suite, Log Viewer, native NDAI logs, optional export, and the related user controls.

## Feature Purpose

Recording captures a trusted local record of the selected HUD/Dashboard Overlay Profile. The Recording card, compact Recording Suite, Log Viewer doorway, native NDAI logs, and explicit export path should form one coherent user experience.

Visible Recording surfaces must match the accepted Nexus window and Dashboard visual grammar. Full-window and desktop context matter for size, placement, dead space, chrome, and parent relationships; focused views matter for controls, text, and interaction states. A screenshot, marker, or helper result alone does not prove visual quality. The current compact Recording Suite uses a tight bottom action row with `TARGET - Default Overlay Profile`, `STATE - Ready - 2 active monitors`, and `OPEN LOG VIEWER`; it avoids helper copy and oversized control wells. The Log Viewer is a compact doorway with `VIEWER - Deferred`, `OPEN NATIVE LOGS`, and `OPEN EXPORTED LOGS`, not a fake full log workspace. Window-control styling must remain consistent with Nexus surfaces.

User-facing placement choices should be shown as rendered alternatives when spatial layout is material. The product should not claim a surface is visually or functionally ready when full-context inspection contradicts a focused view.

## Relationship To FAM-006

Recording belongs to FAM-006 because it depends on Dashboard/HUD visibility,
Overlay Profile state, monitor membership, visual-system inheritance, local file
hygiene, and user-facing validation proof.

Recording does not create a separate Recording Profile system by default. The
Dashboard/HUD Overlay Profile selection remains the recording target source
unless a later USER-accepted feature vision changes that model.

## USER-Facing Surfaces

### HUD Dashboard Recording Access

The Dashboard may provide quick Recording access, but it should not become the
full Recording workspace.

Expected shape:

- a small, obvious Start/Stop affordance when a branch admits quick access
- compact target and status context on a Recording card
- enough information for trust without turning the card into a full studio
- visual-system inheritance from existing Dashboard cards
- truthful disabled, saved, unavailable, and error states

### Dashboard Recording Card

The Recording card is the Dashboard summary and launch surface for Recording.

It should:

- display the selected Overlay Profile target
- show recording readiness and result state
- keep copy concise
- expose admitted Recording actions without crowding the Dashboard
- sample existing Dashboard card chrome, rows, dividers, typography, spacing,
  button treatment, hover/focus/disabled states, glow, and layout density

It should not:

- introduce a separate card visual grammar
- use a unique green-box/table style
- duplicate the HUD Overlay card
- become the long-form recording configuration or log-review surface

### Recording Suite

Recording Suite is the ultra-lightweight detached Recording controller when a
branch admits it. The compact Recording design uses a bounded
standalone-capable controller that owns Start/Stop, recording truth, target
truth, native-log status, and a route to Log Viewer without requiring the
USER to reopen HUD Dashboard.
Dashboard Quick Access may provide a compact Start/Stop shortcut when implemented and verified. Tray integration, keybind behavior,
close-while-recording warnings, and bulky settings remain separate future gates
until implemented and verified.

Expected direction:

- non-child, exclusive, standalone-capable window rather than a Dashboard child
  panel
- compact form factor that behaves like a small detached media-control panel
- standalone window layout that is not a Dashboard card clone and not an AI
  Control Center / command-center clone
- independent lifecycle while Nexus Desktop AI is running: it may launch from HUD
  Dashboard, but it must remain open, truthful, and useful if HUD Dashboard is
  closed when technically safe
- visual-system inheritance from existing Nexus/FAM-006 windows, including chrome,
  color, typography, spacing, buttons, glow/focus/hover/disabled states, and
  compact density rather than generic utility-window styling
- detached child-window title grammar: Recording Suite is independent and
  taskbar/minimize-capable, but its title/header treatment follows the FAM-006
  child-window header pattern of category line plus strong title; it must not
  render a separate rounded title card or main-window hero/title card
- shared rendered primitive inheritance for same-class window chrome, title/header,
  action buttons, row/divider panels, state text, hover/focus/pressed/disabled
  states, and compact body background. When a shared primitive is unavailable, use an existing rendered Nexus CSS/DOM reference and verify the result side by side; do not treat an approximation as visually equivalent.
- Recording Suite and Log Viewer may reuse `nexus_visual/nexus_window_primitives.css` for common chrome, title rows, body, and control states while keeping their distinct product layouts.
- window placement continuity by carrying down the Project UI Vision rule for
  USER-moved windows to restore position safely across sessions where feasible
- Start/Stop control ownership when the branch admits full studio behavior
- selected Overlay Profile target display
- recording state display
- native log status
- Log Viewer doorway/action
- minimal status copy that does not dominate the controller
- close and minimize affordances
- moveable window behavior with safe position memory across launches where
  feasible
- no active resize affordance in the current compact Recording Suite contract;
  Recording Suite should keep its compact controller size while preserving the
  USER-moved position
- deterministic default placement must be proven or optioned before runtime
  implementation closes. Branch-local proposed doctrine is: feature-studio
  child windows open near their parent surface by default unless USER selects a
  different behavior; same-session reopen may restore the last USER-moved
  position; after app or computer restart the window defaults near the parent
  unless USER selects persistent last-position behavior plus a later reset
  route.
- reset-to-default position behavior remains future-gated until the global
  settings/reset-default-window-position surface is admitted

Close behavior should be verified with users. The warning model is: closing the Studio while recording warns that the
recording continues until the USER stops it or Nexus Desktop AI exits. A local
dismissal preference may be allowed if a later branch admits it.

Minimize behavior also needs explicit acceptance. The durable design question is
whether Studio minimizes to the Windows taskbar or folds into a dedicated
Recording tray icon to avoid taskbar clutter.

### Log Viewer

Log Viewer is the Recording log access shell and future expandable log
workspace when implemented. The current Log Viewer design uses a
compact folder-access shell for native and exported log folder access;
previous-log selection, graph/log viewing, in-app log viewing, export
customization, user-selected export file types, and Native Log Loader
integration remain future gates until implemented and verified.

Expected direction:

- non-child, exclusive window
- independent from the Dashboard child-window system
- standalone window layout that is not a Dashboard card clone and not an AI
  Control Center / command-center clone
- compact folder-access shell composition for the current branch
- visual-system inheritance from existing Nexus/FAM-006 windows, including chrome,
  color, typography, spacing, buttons, glow/focus/hover/disabled states, and
  compact density rather than generic utility-window styling
- detached child-window title grammar: Log Viewer is independent and
  resizable, but its title/header treatment follows the FAM-006 child-window
  header pattern of category line plus strong title; it must not render a
  separate rounded title card or main-window hero/title card
- shared rendered primitive inheritance for same-class window chrome, title/header,
  action buttons, row/divider panels, state text, hover/focus/pressed/disabled
  states, and compact body background. When a shared primitive is unavailable, use an existing rendered Nexus CSS/DOM reference and verify the result side by side; do not treat an approximation as visually equivalent.
- Recording Suite and Log Viewer may reuse `nexus_visual/nexus_window_primitives.css` for common chrome, title rows, body, and control states while keeping their distinct product layouts.
- window placement continuity by carrying down the Project UI Vision rule for
  USER-moved windows to restore position safely across sessions where feasible
- access to the native NDAI log folder
- access to the exported-log folder
- previous-log selection when implemented
- in-app log viewing when implemented
- export flow when implemented
- moveable window behavior with safe position memory across launches where
  feasible
- resize affordance for the admitted Log Viewer shell because later log
  review content and path/status readability need screen-space flexibility
- doorway footprint, row/action relationship, and placement behavior must be
  proven with full-desktop/full-context evidence or packeted visual options. A
  focused screenshot that shows readable rows and buttons does not prove that
  the Log Viewer shell is appropriately compact in the USER's desktop
  context.
- doorway layout options must be actual rendered alternatives when USER review
  is choosing between vertical stack, inline row actions, footer actions, or a
  future-leaning shell; prose-only cards are not enough.
- maximize/fullscreen remains deferred until actual log-viewing behavior establishes the required window composition
- reset-to-default position behavior remains future-gated until the global
  settings/reset-default-window-position surface is admitted

Log Viewer should distinguish native NDAI logs from exported files.
Native logs are the product artifact. Exported files are USER-requested
conversions for another reader or tool.

### Tray Recording Visibility And Control

Recording needs visible user-facing transparency when recording behavior is
admitted.

Future tray direction:

- dedicated recording-state visibility when Recording capability is enabled
- left-click Start/Stop only if USER accepts that behavior
- right-click options for Recording Suite, Log Viewer, Start/Stop, and
  related admitted actions
- tray-state clarity that does not hide recording from the USER

Tray behavior is deferred until its controls and recording-state visibility work correctly.

### Keybind Start/Stop

Recording should eventually support a USER-customizable keybind for Start/Stop.

Future settings should decide whether keybind-start opens Recording Suite. The
default may open Studio unless USER accepts a setting that suppresses it.

Keybind behavior is deferred until its controls and conflict handling work correctly.

### Settings

Recording settings should be compact and conventional when admitted.

Potential settings:

- what happens when recording starts
- what happens when recording stops
- whether keybind-start opens Recording Suite
- whether stop opens Log Viewer
- warning dismissal preferences
- export defaults
- native log location
- exported log location

Local one-off acknowledgements, such as "do not show this warning again", should
be separated from global categorized settings.

## Native And Export Artifact Model

Normal product recording should save as a native NDAI recording log owned by
Nexus Desktop AI.

Native NDAI log:

- canonical product artifact
- read by NDAI for future in-app viewing and validation
- not designed as the default third-party-readable file
- should preserve local file hygiene and privacy-safe boundaries
- current default root is the flat product folder `Recordings`; feature-named
  child folders such as `Monitoring HUD` must not be introduced unless a later
  USER-accepted export/storage design admits that taxonomy

Exported log:

- USER-requested conversion
- supports selected readable formats only after an export branch admits them
- should be validated in a user-forward way so the exported file is easy to
  inspect in the target class of software
- belongs in an exported-log folder, separate from native NDAI log storage
- current default root is the flat product folder `Exported Logs`; feature-named
  child folders must not replace the exact exported-log root without later
  USER-approved storage planning

Manual validation exports may exist as test artifacts under governed validation
roots, but they must not become normal product flow.

## Experience Flow

1. USER opens the Dashboard and sees a Recording card that matches the Dashboard
   visual system.
2. Recording target follows the Dashboard/HUD Overlay Profile selection.
3. USER can see whether Recording is ready, unavailable, recording, or saved.
4. Dashboard Quick Access may expose a small Start/Stop shortcut; Recording Suite
   owns the focused control surface when available.
5. Stopping a recording produces native NDAI output.
6. USER can later use Log Viewer to review native logs or export selected
   logs into supported readable formats.
7. Tray and keybind behavior remain future decisions until admitted.

## Included Capabilities

Recording capabilities include or may later add:

- Dashboard Recording card target and status presentation
- Start/Stop behavior when implemented
- snapshot-at-start target policy when implemented
- native NDAI log output
- native output readback proof
- exported-log folder access when admitted
- Recording Suite planning
- Log Viewer planning
- tray recording visibility planning
- keybind planning
- recording settings planning
- Overlay Profile persistence dependency review

## Explicit Non-Goals

This Recording feature does not include provider/model execution, a separate Recording Profile system, automatic third-party-readable export, a full Native Log Loader, full Log Viewer workspace, tray or keybind controls, or a broad theme redesign. Those behaviors need their own product design and technical checks before they appear as working controls.

## Related Feature Boundary

FAM-006 owns recording targets, native logs, control surfaces, and their visible state. Provider/model execution and capability-pack behavior belong to the AI feature and are not required for local recording. Recording must remain usable without those features.

## Product Design Options

The selected compact direction keeps the Dashboard Recording Card as target/status and launch context. Recording Suite is the focused Start/Stop and truthful recording-status surface. Dashboard Quick Access may offer a small Start/Stop shortcut without turning the card into a control workspace. Log Viewer begins as a compact shell for native and exported log folder access; selection, in-app viewing, and customized export remain deferred.

Start/Stop must have one clear owner. The Studio can minimize to the taskbar; a dedicated recording tray state is a later product option that must keep active recording visible. Closing Studio while recording should warn that recording continues until the user stops it or Nexus exits. Native NDAI output is the normal artifact. Readable export occurs only on an explicit user request; automatic readable export is outside this feature. Recording target persistence follows the selected Overlay Profile and must remain reliable after restart.

A direct exported-log folder action may serve as a bounded bridge until the Log Viewer has real viewing capabilities. Folder actions should work even before a recording exists in the current session.

## Observable Product Checks

- Inspect affected window and control groups in their normal, hover, focus, disabled, empty, error, and recording states; a source marker or screenshot by itself does not prove usability.
- Keep shared action buttons consistent in height, typography, radius, border, gutters, and interaction states.
- The compact Recording Suite is moveable and remembers position but is not resizable; Log Viewer follows its defined doorway-shell resize behavior. Do not use an attached-child corner grip for these standalone-capable studios.
- When the selected controls are present, START, PAUSE, STOP, and OPEN LOG VIEWER must have distinct behaviors and truthful availability.
- Show the selected Overlay Profile target and readiness accurately. For different profile monitor memberships, verify selected identity, monitor set, target snapshot, native log content, and their consistency.
- Save and read back NDAI-native output. Do not automatically create CSV or Excel files. Create readable exports only after the user requests an available export action.
- Verify recording, saved, disabled, warning, failure, and recovery states; do not infer telemetry or recording state from visual copy alone.
- Open Recording Suite and Log Viewer through their normal visible product routes. Diagnostic launches may aid troubleshooting but cannot establish that the ordinary user route works.
- Compare shared rendered primitives across Recording Suite and Log Viewer, including spacing, controls, typography, status, and resize treatment. Generic window-shell markers do not establish visual consistency.
- Avoid displaying worktree, branch, internal family, or developer-only identifiers in product folder labels or messages.
- Verify the user-facing Dashboard card, tray route if available, keybind if available, log review, export, settings, and profile persistence only when those affected capabilities are implemented.

## Deferred And Optional Capabilities

Describing an option does not enable it. Each available control must reflect real recording state and a safe recovery path.

| Capability | Surface | Behavior | Prerequisite | Verification |
| --- | --- | --- | --- | --- |
| Recording Suite full control surface | Recording Suite | Compact non-child Studio for Start/Stop, target, status, close/minimize warning, and screen-space-efficient control. | Branch admits full recording control surface beyond Dashboard card summary. | Focused Studio screenshots, Start/Stop proof, close/minimize behavior proof. |
| Log Viewer | Log Viewer | Non-child surface for native log access, exported-log access, previous-log selection, in-app viewing, and export entry. | Branch admits log review or export workflow. | Focused Log Viewer screenshots, native/export folder proof, export/readability proof when export is admitted. |
| Native NDAI log model | Native logs | Recording saves first as NDAI-native product artifact for readback and future in-app review. | Branch writes or reads recording output. | Native save/readback helper proof, no automatic readable export. |
| Exported log model | Exports | Readable CSV/Excel/JSON or other files are USER-requested exports, not default product saves. | Branch admits export/share or third-party-readable output. | Export file readability proof in target software class, output-folder proof. |
| Tray recording visibility and control | Tray | Dedicated recording visibility and optional Start/Stop / Studio / Log Viewer controls through tray. | Branch admits recording transparency or minimized Studio behavior. | Real tray interaction proof, visible state proof, screenshot/video proof. |
| Keybind Start/Stop | Keybind | USER-customizable Start/Stop keybind and setting for whether keybind-start opens Studio. | Branch admits keyboard recording control. | Keybind registration proof, conflict handling, setting proof. |
| Recording settings | Settings | Compact categorized settings for start/stop behavior, Studio opening, Log Viewer opening, warnings, export defaults, and log locations. | Branch admits configurable recording behavior. | Settings UI proof, persistence proof, reset/rollback proof. |
| Warning dismissal behavior | Recording Suite warning | Local dismissal for close-while-recording warning, separate from global settings. | Branch admits close-while-recording warning. | Warning modal proof, dismissal persistence proof, recording continues/stops behavior proof. |
| Overlay Profile persistence dependency | Overlay Profiles | Recording target reliability depends on saved Overlay Profiles remaining present after restart. | Branch depends on saved Overlay Profile targets across sessions. | Create/save/restart/reselect proof, recording target mirror proof. |
| Dashboard quick-access recording affordance | Dashboard | Small obvious Dashboard Start/Stop affordance, possibly icon-led. | Branch admits Dashboard-level quick control. | Focused Dashboard Quick Access screenshots, click/state proof, visual-system proof. |
| Native Log Loader relationship | Log viewing | Native Log Loader remains separate graph/log viewer unless later planning folds it into Log Viewer. | Branch admits graph/log viewer capability. | Viewer/readback proof if admitted; otherwise explicit future-gated proof. |
