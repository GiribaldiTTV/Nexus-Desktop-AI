# FB-036 Saved-Action Authoring

## ID And Title

- ID: `FB-036`
- Title: `Limited saved-action authoring and type-first custom task UX`

## Record State

- `Promoted`

## Status

- `Active on feature/fb-036-idea5-integrated-hardening`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Purpose / Why It Matters

Deliver a bounded in-product path for creating and editing saved actions without reopening the typed-first interaction contract or expanding into Action Studio behavior.

This workstream exists so users can manage non-standard custom tasks safely through the existing shared action model instead of hand-editing JSON.

## Current Branch Truth

- the branch already includes safe saved-action persistence, bounded deletion, and explicit catalog reload after writes
- the branch already includes a type-first create flow and a bounded edit flow
- the entry-state NCP opening now stays lightweight and button-led, with peer `Create Custom Task` and `Manage Custom Tasks` actions as the primary authoring entry points
- detailed saved-action inventory viewing and edit reachability now live in the secondary `Manage Custom Tasks` window instead of being expanded inline on the initial opening surface
- the secondary `Manage Custom Tasks` window now supports both edit and delete actions for existing saved tasks
- create/edit dialogs now expose an explicit `Trigger` field with `Launch`, `Open`, `Launch and Open`, and `Custom` options
- new saved actions now use alias-root invocation, with `Title` treated as a label and callable phrases generated at runtime from `aliases`, `trigger_mode`, and optional `custom_triggers`
- legacy saved actions that do not yet carry the new invocation-mode marker still remain title-plus-alias callable so existing tasks do not silently change behavior
- create/edit dialogs now use stronger field headers with label-hover help, darker integrated chrome, and a single callable-surface panel that updates from the current title, aliases, trigger selection, and target kind
- create/edit dialogs now place `Trigger` directly below `Title`, use faster NDAI-styled help tooltips from the field labels themselves, and keep the callable-surface panel to the right of the form for clearer scanning
- exact-match resolution remains unchanged
- new integrated truth now allows multiple saved actions to share the same exact callable phrase while still keeping exact-match normalization and resolution bounded
- saved-vs-saved exact ambiguities now surface through the existing overlay ambiguity chooser, then continue through the normal confirm step before execution
- built-in vs saved callable-phrase overlap still remains blocked rather than becoming ambiguous in this lane
- the overlay phase machine remains bounded to `entry` -> `choose` -> `confirm` -> `result`
- current supported saved-action target kinds remain `app`, `folder`, `file`, and `url`
- malformed or colliding saved-action sources still block authoring rather than attempting salvage
- branch-local validation and hardening work now also includes dedicated FB-036 validators, live-style harnesses, interactive runtime helpers, durable validation reports, and exported manual-test artifacts that future slices should reuse rather than recreate blindly
- the final integrated FB-036 + Idea 5 watchdog-enforced interactive desktop gate passed end-to-end on `2026-04-15` using `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260415_115705.txt`

## Scope

- bounded saved-action create and edit UX
- bounded saved-action deletion from the secondary `Manage Custom Tasks` window
- safe persistence and validation-before-write
- immediate catalog reload after successful writes
- explicit user-facing type selection mapped to the current persisted target kinds
- a lightweight landing path for task authoring and management that does not overload the initial NCP opening surface
- richer secondary create/manage windows that can carry the detailed explanations, guidance, and step-by-step authoring copy users need once they choose an action path
- short inline field guidance inside the secondary create/edit windows so users get quick help without overloading the initial landing surface
- title-driven alias suggestions, explicit trigger configuration, alias-root invocation for new tasks, and a bottom-of-dialog dynamic invocation examples box inside the secondary create/edit windows
- browse-assisted target selection for `Application`, `Folder`, and `File` that fills the existing validated `Target` field while `Website URL` stays direct-entry only

## Non-Goals

- disable flows
- Action Studio behavior
- taskbar or tray authoring surfaces
- overlay phase changes
- new persisted action kinds
- malformed-source repair logic
- built-in vs saved ambiguity
- ambiguity ranking logic changes
- fuzzy matching

## Executed Slices So Far

1. added the safe persistence foundation and catalog reload seam
2. added the type-first create flow
3. added the bounded edit flow with identity-preserving updates
4. tightened target validation for `app`, `folder`, and `file`
5. expanded saved-action inventory reachability so edit is no longer capped to the first six items
6. pivoted the initial NCP authoring entry into a lightweight button-led landing surface with a secondary `Created Tasks` window
7. added browse-assisted target selection for `Application`, `Folder`, and `File` while keeping `Website URL` direct-entry only
8. added the explicit Trigger model, runtime-generated callable phrases, stronger field headers/help icons, and a dynamic examples box for create/edit dialogs
9. pivoted new saved actions to alias-root invocation while preserving legacy title-callable behavior for existing tasks
10. added delete reachability for saved tasks through the secondary `Created Tasks` window
11. polished the create/edit dialog layout so `Trigger` follows `Title`, help tooltips appear faster, and the single bottom callable-surface box is easier to scan
12. allowed saved-vs-saved exact-match ambiguity while preserving built-in collision rejection and the existing choose -> confirm -> execute overlay flow
13. integrated the latest FB-036 UI lane, hardening lane, and Idea 5 ambiguity lane into one final proof branch and re-cleared the full watchdog-backed interactive desktop gate

## Idea Impact Analysis And Route Adjustment

- The new idea set refines FB-036 rather than replacing it. The safe create/edit foundation, validation-before-write, reload seam, and bounded inventory editing all remain valid branch truth.
- The strongest route change is at the landing surface. The initial NCP opening should now be treated as a lightweight action launcher rather than a place that carries dense explanatory copy or full task-management detail inline.
- `Create Custom Task` remains in scope for FB-036, but the user-facing route should pivot so the initial surface stays minimal and the detailed help moves into the secondary create/manage windows.
- An explicit `Created Tasks` or task-management entry point remains compatible with FB-036 and now looks like the right follow-through instead of continuing to expand inline entry-state inventory detail.
- Leaving visual room for future buttons such as plugin integration is a forward-compatibility design constraint, not an authorization to add plugin behavior to FB-036.
- Future voice access is a real planning constraint for this lane, but it should be treated as a naming and action-routing requirement rather than as authorization to implement voice in FB-036. The visible actions and windows added here should map cleanly to future voice-addressable intents.
- A user-facing `Active` / `Inactive` toggle for saved tasks should be deferred. It would introduce new persisted enable/disable semantics, new filtering behavior, and a new execution-state policy that goes beyond the current bounded authoring baseline.
- Field-level explanation is now a higher-priority refinement. `Alias`, `Task type`, and `Target` need clearer in-window guidance so users understand what each field does before more advanced target-picking conveniences are layered on top.
- Browse-assisted target selection for the current `Application`, `Folder`, and `File` kinds remains compatible with FB-036 and is a better fit than adding brand-new target kinds right now. It should populate the existing `Target` field rather than introduce a parallel persistence model.
- Additional task kinds beyond `app`, `folder`, `file`, and `url` should remain deferred until runtime behavior actually exists for them.
- A per-task or global browser-selection policy for website tasks crosses into settings and launch-policy territory. That should be deferred to a later settings or built-in-action lane instead of being silently folded into the current authoring branch.
- A visual polish pass for the create/edit window, including the current title-bar look, belongs in planning for this lane but should follow the routing and field-guidance adjustments rather than precede them.

## Planned Resequencing

1. preserve and stabilize the current branch-local validation and support assets so the existing create/edit baseline remains provable and reusable
2. improve field-level help inside the create/edit windows, especially around `Alias`, `Task type`, and `Target`
3. evaluate focused create/edit window visual polish after the routing, explanatory copy, alias suggestions, examples box, and target-picking flow are settled

## Validation And Support Artifact History

- `dev/orin_saved_action_authoring_validation.py`
  Purpose: lane-specific authoring foundation validator for create/update behavior, collision handling, unsafe-source blocking, and write-safe persistence.
  Introduced: when the safe persistence foundation and bounded create/edit baseline were added to FB-036.
  Classification: `baseline`.
  Reuse: extend this first when saved-action draft rules, identity preservation, or persistence semantics change.

- `dev/orin_saved_action_authoring_ui_validation.py`
  Purpose: supporting headless UI validator for create/edit dialog behavior, invalid target rejection, collision messaging, and inventory edit-button mapping.
  Introduced: when the branch moved from persistence-only authoring support into visible create/edit UX.
  Classification: `supporting`.
  Reuse: extend this when dialog controls, labels, type selection, inventory rendering, or button routing change.

- `dev/orin_saved_action_authoring_live_validation.py`
  Purpose: supporting live-style harness that exercises create/edit/reopen behavior with durable reports and saved-actions snapshots without requiring the full interactive desktop gate.
  Introduced: when evidence-backed hardening became required before normal continuation.
  Classification: `supporting`.
  Reuse: keep this as the fast reusable regression layer before a slower interactive OS-level session.

- `dev/orin_saved_action_authoring_interactive_runtime.py`
  Purpose: branch-local runtime helper that launches the real desktop runtime with a deterministic FB-036 runtime-log target for interactive validation.
  Introduced: during the interactive-validation hardening pass on `2026-04-13`.
  Classification: `interactive-only`.
  Reuse: use this when future FB-036 slices need a reproducible interactive runtime launch path with preserved log evidence.

- `dev/orin_saved_action_authoring_interactive_validation.ps1`
  Purpose: branch-local interactive OS-level validation driver for real hotkey, dialog, create/edit, reopen, unsafe-source, and large-inventory scenarios.
  Introduced: during the same `2026-04-13` interactive-validation hardening pass.
  Classification: `interactive-only`.
  Reuse: continue hardening and reuse this as the default FB-036 interactive continuation gate instead of rebuilding one-off probes.
  Time-budgeted defaults: full run `420s`, no-progress watchdog `45s`, scenario budget `90s`, transition budget `25s`, with clean abort, cleanup, and last-progress reporting required on timeout.

- `dev/logs/fb_036_authoring_live_validation/`
  Purpose: durable report and artifact root for the synthetic/live-style FB-036 validation harness.
  Introduced: when the branch added evidence-backed live validation before continuation.
  Classification: `supporting`.
  Reuse: keep reports and snapshots here so future slices can compare behavior against earlier branch-local authoring evidence.

- `dev/logs/fb_036_authoring_interactive_validation/`
  Purpose: durable report and artifact root for interactive OS-level validation runs, including runtime logs, saved-actions snapshots, and branch-local manual-gate evidence.
  Introduced: during the interactive-validation hardening pass on `2026-04-13`.
  Classification: `interactive-only`.
  Reuse: future slices should append new reports here and cite the exact report used for any continuation recommendation.

- `Docs/workstreams/FB-036_saved_action_authoring.md` `## User Test Summary`
  Purpose: canonical repo-level manual-validation contract for the active workstream.
  Introduced: when FB-036 was promoted into a canonical workstream record.
  Classification: `baseline`.
  Reuse: update this whenever user-visible expectations, fail-closed behavior, or the manual continuation checklist changes.

- `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`
  Purpose: required user-facing exported copy of the active FB-036 manual checklist.
  Introduced: when the lane adopted the stronger desktop-export rule for relevant desktop slices.
  Classification: `supporting`.
  Reuse: keep it aligned with the workstream-owned `## User Test Summary` whenever the manual checklist changes.

- Existing shared baseline validators such as `dev/orin_saved_action_source_validation.py`, `dev/orin_interaction_baseline_validation.py`, `dev/orin_overlay_input_capture_helper.py`, and `dev/orin_recoverable_launch_failed_validation.py` remain part of the required validation stack, but they are reused cross-lane infrastructure rather than FB-036-specific artifact owners.

## Branch Closeout Traceability Record

### Final Implementation Summary

- new-model saved actions now use an alias-root invocation model
  - `Title` is a display label
  - `Aliases` are the invocation-bearing phrases
  - `Trigger` chooses the prefix family that expands callable phrases at runtime
- exact-match discipline still remains the routing contract
  - one exact phrase can now intentionally resolve to more than one saved action
  - when that happens, the existing overlay ambiguity chooser presents the candidates and the user selects one before the normal confirm step executes it
  - built-in vs saved exact overlaps remain blocked in this lane
- built-in trigger families remain bounded to `Launch`, `Open`, `Launch and Open`, and `Custom`
- examples in the create/edit dialogs now reflect only real callable phrases generated from the current alias + trigger draft
- new-model create and edit preserve exact-match discipline and do not widen into fuzzy language handling
- legacy tasks remain backward compatible until explicitly migrated
  - legacy no-trigger tasks stay bare-callable instead of silently widening on update
  - legacy title-callable tasks remain title-callable after normal edits
- the saved-action inventory now supports:
  - create
  - edit in place
  - delete from `Created Tasks`
  - immediate catalog reload after successful writes
- browse-assisted target picking exists only for the currently validated bounded types:
  - `Application`
  - `Folder`
  - `File`
  - `Website URL` remains direct-entry only

### Failure Timeline

1. startup and attach instability
   - early interactive runs could stall before a real overlay-open attempt because the harness performed blocking UIAutomation checks before sending the first hotkey
2. overlay-ready signaling gaps
   - `COMMAND_OVERLAY_OPENED` could arrive without a durable `COMMAND_OVERLAY_READY`, leaving the harness waiting on a one-shot readiness signal that was sometimes skipped
3. create-dialog entry stalls
   - the runtime marked the create dialog open/ready, but the harness still blocked on brittle dialog resolution and first-control interaction
4. post-create transition stalls
   - after successful create, the harness could lose the path back to an overlay-ready next step, especially after `Created Tasks` closed
5. invalid-create cancel handoff stalls
   - after rejection and cancel, the dialog-close marker existed, but the harness still relied on stale overlay references instead of a fresh reacquisition path
6. combo-selection instability
   - non-default type changes such as `Application -> Folder` or `Application -> File` could hang because combo handling depended on popup-item scanning and stale UIAutomation elements
7. target-field write/readback drift
   - the correct target text could already be present, but the helper still treated the write as unstable and burned the remaining scenario budget retrying
8. invalid-create submit/marker timing failures
   - the harness used one long invalid-create scenario budget for multiple blocked cases, so the final case timed out while waiting on otherwise-correct runtime markers
9. edit-dialog entry/focus instability
   - edit runs reached `CUSTOM_TASK_EDIT_DIALOG_READY`, but the harness still had weaker entry and focus behavior than the hardened create path
10. watchdog and timeout non-enforcement
    - early timeout work could detect stalls but still relied on the outer shell timeout because the watchdog launch and interruption path were not yet durable
11. exact-match execution misalignment
    - the harness assumed optional saved-action fields such as `custom_triggers` always existed and also reused invocation assumptions that no longer matched alias-root records
12. reopen persistence stalls
    - the runtime closed the overlay successfully, but the harness still tried to prove closure through UIAutomation disappearance instead of trusting the close marker and reopening fresh
13. unsafe-source blocking seam instability
    - after restart and overlay-ready, the final blocked-create path still used weaker direct element walks and could stall before reaching the actual fail-closed runtime markers
14. system-wide focus instability
    - create and edit dialog interactions still failed intermittently because controls were visible and enabled but did not always gain confirmed keyboard focus
15. strict-mode property-access crash
    - `ControlType.ProgrammaticName` was read directly at multiple call sites and could crash the harness when the UIAutomation object shape did not expose that property safely

### Root Causes

- the earliest harness design trusted UIAutomation state too early and too literally
  - it assumed the presence or visibility of an element was enough to proceed
  - it assumed a single event-loop tick or a single UIA lookup represented stable readiness
- the harness initially mixed authoritative runtime markers with non-authoritative UIAutomation heuristics without clearly choosing which source won
- too many transitions reused stale element handles across dialog close/open boundaries
- several helpers assumed ideal object shapes under `Set-StrictMode -Version Latest`
  - optional JSON fields such as `custom_triggers`
  - optional or inconsistent UIAutomation metadata such as `ControlType.ProgrammaticName`
- long multi-case scenarios treated elapsed time as shared state, so later cases inherited the cost of earlier ones and timed out for the wrong reason
- focus checks originally assumed exact control identity instead of recognizing that some controls route keyboard focus through child/editor elements inside the same usable surface
- the original watchdog approach assumed a child enforcement path existed, but it did not verify that the watchdog had actually started and could interrupt the parent if the parent wedged

### Fix Patterns

- marker-first validation
  - runtime markers became the authoritative boundary for open, ready, close, blocked, and submit transitions
  - UIAutomation evidence became a secondary usability check instead of the truth source for lifecycle changes
- deterministic readiness checks
  - overlay and dialog readiness now require real control availability, not just window presence
  - first required controls are verified before interaction begins
- re-resolve instead of reuse
  - overlay roots, dialog roots, buttons, and fields are re-resolved after every close/open seam
  - stale element references are treated as expected failure modes, not surprising exceptions
- hardened interaction helpers
  - combo selection uses deterministic strategies with readback verification
  - field writing uses clear -> write -> immediate normalized readback -> bounded retry
  - focus acquisition uses foreground + focus + click strategies with explicit focus confirmation
- transition gating
  - close markers are treated as authoritative, then the next surface is reacquired from scratch
  - `Created Tasks` close, dialog cancel, overlay reopen, and post-edit continuation all use the same reacquire-and-verify pattern
- watchdog enforcement
  - full-run, no-progress, scenario, and transition budgets are enforced in-harness
  - the external watchdog now proves startup, kills stalled runs when needed, records timeout reason, and performs cleanup instead of waiting on the outer shell timeout
- null-safe property access
  - optional saved-action fields and optional UIAutomation metadata now flow through helper-based safe access rather than strict-mode direct property reads

### Validation Evolution

- baseline validators
  - `dev/orin_saved_action_authoring_validation.py` proved persistence safety, collision behavior, legacy compatibility, invocation generation, and fail-closed authoring semantics
- UI validator
  - `dev/orin_saved_action_authoring_ui_validation.py` proved dialog structure, control routing, bottom guidance presentation, delete reachability, and visible create/edit expectations
- live-style validator
  - `dev/orin_saved_action_authoring_live_validation.py` proved create/edit/delete, alias-root behavior, exact phrase generation, and reopen/catalog behavior without requiring a full OS-level run
- interactive harness
  - `dev/orin_saved_action_authoring_interactive_validation.ps1` became the authoritative full-gate proof for:
    - hotkey entry
    - real desktop dialogs
    - real input flow
    - real blocked cases
    - reopen persistence
    - unsafe-source behavior
    - no-input-leakage proof
- watchdog-enforced interactive proof
  - time budgets and watchdog enforcement turned interactive validation from a best-effort probe into a bounded, repeatable continuation gate
  - the final passing interactive run on `2026-04-15` is the branch-closeout proof point for this lane

### Validation Infrastructure And Reuse Guidance

- primary interactive driver
  - `dev/orin_saved_action_authoring_interactive_validation.ps1`
  - reuse this first for any future FB-036 regression or branch-closeout rerun
- runtime helper
  - `dev/orin_saved_action_authoring_interactive_runtime.py`
  - use this when a future slice needs deterministic runtime startup and log capture
- log and artifact roots
  - `dev/logs/fb_036_authoring_live_validation/`
  - `dev/logs/fb_036_authoring_interactive_validation/`
  - future work should append evidence here rather than inventing new parallel log roots
- saved-action snapshots
  - `initial_source`
  - `after_create`
  - `after_edit`
  - `after_large_inventory_edit`
  - `final_source_before_restore`
  - these snapshots are now part of the expected evidence package for meaningful interactive reruns
- exported manual checklist
  - `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`
  - keep it aligned with this workstream record whenever the human-run checklist changes

### Key Engineering Rules For Future Work

- never trust UI state alone when a runtime marker exists
- never reuse a dialog or overlay reference across a close/open seam
- always re-resolve the control you are about to interact with
- treat visible + enabled as necessary but not sufficient; keyboard focus or equivalent interaction readiness must still be confirmed
- keep validation time-budgeted
  - full-run hard timeout
  - no-progress timeout
  - scenario budget
  - transition budget
- separate product bugs from harness bugs before changing runtime behavior
- prefer marker-first fixes and null-safe helper patterns over ad hoc one-line patches
- when a blocked state is the expected result, prove:
  - no write
  - correct blocked marker
  - correct user-facing status
  - correct recovery path

### Remaining Non-Blocking Notes

- help-button readiness is still noisy during early dialog interaction
  - the final passing run recorded repeated notes that help buttons were not always ready before the first required field interactions
  - this did not block the validated flow because the required inputs were still interactable
- the bottom guidance/examples box can lag by one interaction attempt
  - the harness occasionally needed one retry before the expected wording fully refreshed
  - this did not invalidate the final run because the later dialog validation path still confirmed the correct model
- status-label readback for blocked cases can be blank in UIAutomation even when the runtime and dialog state are correct
  - the harness now treats this as a note rather than a blocker when the stronger runtime and no-write conditions are already proven
- these notes are real but non-blocking
  - they should be treated as polish or future hardening candidates, not as reasons to reopen the FB-036 core or closeout claim

### Evidence References

- final passing interactive report
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260415_061125.txt`
- final passing interactive runtime log
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260415_061125_runtime.log`
- final passing interactive step log
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260415_061125_interactive_steps.log`
- final passing snapshots
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260415_061125_initial_source_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260415_061125_after_create_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260415_061125_after_edit_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260415_061125_after_large_inventory_edit_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260415_061125_final_source_before_restore_saved_actions.json`
- final supporting live report
  - `dev/logs/fb_036_authoring_live_validation/reports/FB036SavedActionAuthoringLiveValidationReport_20260415_061122.txt`
- branch checkpoints that future slices can anchor to
  - core checkpoint: `d20c1aa` on `feature/fb-036-saved-action-authoring`
  - UI checkpoint: `11c1292` on `feature/fb-036-ui-clarity-polish`
  - hardening closeout proof: full interactive pass on `feature/fb-036-validation-hardening`

### Final Branch State

- validated behavior that future work may rely on
  - bounded create/edit/delete flows
  - alias-root invocation for new tasks
  - legacy compatibility preservation
  - explicit trigger-family behavior
  - exact-match execution after create/edit
  - reopen persistence
  - large-inventory edit reachability
  - fail-closed unsafe-source blocking
  - no-input-leakage proof during interactive authoring
- validated infrastructure that future work should reuse
  - the dedicated FB-036 validators
  - the live-style harness
  - the interactive runtime helper
  - the watchdog-enforced interactive harness
  - the evidence roots and saved-action snapshot pattern
- what this closeout means
  - FB-036 is no longer just “feature-complete”; it is now branch-closeout provable on real desktop interaction evidence
  - future Codex or developer work should treat this workstream record and the final `2026-04-15` interactive report as the baseline truth to extend, not as a lane that still needs first-principles rediscovery

## User Test Summary

### Test Purpose

Confirm that the full FB-036 branch behavior is stable for real desktop use, including:

- safe custom-task creation
- bounded in-place editing
- bounded deletion from `Created Tasks`
- explicit Trigger configuration with runtime-generated callable phrases
- alias-root invocation for newly created tasks without silently changing legacy tasks
- validation-before-write for every supported target kind
- immediate catalog reload after save
- fail-closed handling for unsafe saved-action sources
- edit reachability for inventories larger than six items
- saved-vs-saved exact-match ambiguity surfaced through candidate selection
- built-in-vs-saved overlap still blocked before write
- no regression in the typed-first overlay baseline

### Scenario / Entry Point

Open the desktop overlay on `feature/fb-036-idea5-integrated-hardening` with a healthy `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json` source and use the lightweight button-led entry surface as the authoring landing path:

- `Create Custom Task`
- `Manage Custom Tasks`

### Setup / Prerequisites

- start from a clean desktop runtime launch on `feature/fb-036-idea5-integrated-hardening`
- keep a safe outside text target open, such as Notepad, so stray typing is easy to spot
- know where `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json` lives
- for the large-inventory checks, prepare at least eight valid saved actions in the source
- for the unsafe-source checks, back up `saved_actions.json` before intentionally corrupting it

### Steps To Execute

1. Setup: launch the desktop runtime and open the overlay in its normal typed-first way.
Action: inspect the entry-state panel before typing anything.
Expected Behavior: the overlay opens in the normal entry baseline, the initial landing surface stays lightweight, `Create Custom Task` and `Manage Custom Tasks` are both visible as peer actions, and no inline saved-action detail or `Edit` buttons overload the first surface.
Failure Conditions / Edge Cases: the overlay skips entry state, either top-level button is missing, inline inventory/edit detail still clutters the landing surface, or outside text receives stray typing.

2. Setup: stay in entry state with a healthy saved-action source.
Action: click `Create Custom Task`, choose `Application`, then inspect the dialog before saving anything.
Expected Behavior: the dialog shows stronger headers for `Title`, `Trigger`, `Aliases`, and `Target`; `Trigger` sits directly below `Title`; the field labels themselves surface hover help; field-specific helper text is carried by the tooltips instead of stacked under the fields; the help tooltip appears quickly in a compact NDAI-styled card; `Trigger` offers `Launch`, `Open`, `Launch and Open`, and `Custom`; `Custom` keeps its comma-separated trigger field hidden until selected; and a single callable-surface panel stays visible to the right of the form.
Failure Conditions / Edge Cases: headers are not visually distinct, `Trigger` is still buried below `Aliases`, hover-help affordances feel undiscoverable, field helper text still stacks under the inputs, tooltips feel delayed or unusable, the trigger dropdown is missing, the custom trigger field is always visible, or the callable-surface panel is missing.

3. Setup: stay in the same create dialog.
Action: enter `Title = Open Nexus`, `Aliases = Nexus, NDAI`, confirm the default trigger for `Application`, then switch `Trigger` to `Launch and Open`.
Expected Behavior: alias suggestions update from the title without overwriting the aliases field; `Application` defaults to `Launch`; the bottom callable-surface box updates live to the current draft and clearly separates suggested aliases, real callable phrases, and the target-format reminder; it shows only relevant callable phrases like `Nexus`, `NDAI`, `Launch Nexus`, `Open Nexus`, `Launch NDAI`, and `Open NDAI`; the title itself is treated as a label rather than a callable phrase source unless it also appears in aliases; and the target-format reminder stays specific to `Application`.
Failure Conditions / Edge Cases: alias suggestions overwrite typed aliases, the default trigger does not match the selected type, the bottom box does not update live, the sectioned presentation becomes harder to read, the title appears as a generated callable phrase even when it is not in aliases, irrelevant examples remain visible, or generated trigger phrases are missing.

4. Setup: still in the create dialog.
Action: change `Trigger` to `Custom`, enter `Force Open, Duck Duck Goose`, then use `Browse...` or manual entry to set `Target = notepad.exe` and save.
Expected Behavior: the custom trigger field appears only for `Custom`; the examples box updates to phrases like `Force Open Nexus`, `Duck Duck Goose Nexus`, `Force Open NDAI`, and `Duck Duck Goose NDAI`; standard `Launch` / `Open` phrases disappear from the examples box in this mode; the title label does not generate its own custom-trigger phrases unless it is also present in aliases; save succeeds; and the new task appears immediately without restart.
Failure Conditions / Edge Cases: the custom trigger field stays hidden, the examples box still shows standard trigger phrases, custom trigger phrases are ignored, the title generates callable phrases on its own, or the task only appears after restart.

5. Setup: with the newly created task present.
Action: type callable phrases through the normal overlay input:
`Nexus`
`NDAI`
`Force Open Nexus`
`Duck Duck Goose NDAI`
Expected Behavior: each exact phrase resolves through the existing typed-first path with no fuzzy expansion because the aliases are the invocation roots for the new task.
Failure Conditions / Edge Cases: alias-root phrases do not resolve, custom-trigger phrases do not resolve, the title label resolves even though it is not present in aliases, resolution becomes fuzzy or ambiguous unexpectedly, or restart is required before the new phrases work.

6. Setup: with two valid saved actions intentionally sharing the same alias, for example `weekly reports`.
Action: type the shared phrase into the normal overlay input, confirm that the ambiguity chooser appears, choose the second candidate, then confirm execution.
Expected Behavior: the overlay stays within the existing typed-first phase model, shows multiple exact candidates for the shared phrase, accepts numbered or direct chooser selection, advances to the normal confirm step for the selected action only, and executes only that chosen saved action.
Failure Conditions / Edge Cases: the shared exact phrase is rejected as an authoring error, the overlay silently picks one action without showing candidates, the candidate ordering is unstable across repeats, confirmation is skipped, or the wrong saved action executes after selection.

7. Setup: open `Create Custom Task` again.
Action: test invalid creates one at a time:
`Application` with `Target = notepad.exe --help`
`Folder` with `Target = Reports\Daily`
`File` with `Target = C:\Reports\bad?.txt`
`Website URL` with `Target = example.com/docs`
then set `Trigger = Custom` and enter duplicate custom trigger phrases like `Force Open, force open`.
Expected Behavior: each invalid case stays in the dialog, shows a clear explanation for what failed, and writes nothing to disk.
Failure Conditions / Edge Cases: any invalid target or invalid custom trigger set is accepted, the dialog closes anyway, inventory changes, or the error text is vague or missing.

8. Setup: with at least one saved action already present.
Action: attempt collision creates:
use an alias like `Open Windows Explorer`
use another saved action's existing title or alias
use wording that collides only through generated trigger phrases, such as creating `Workspace` with `Trigger = Open` after another task already makes `Open Workspace` callable
Expected Behavior: the dialog stays open, collision feedback is clear, and no write occurs.
Failure Conditions / Edge Cases: a colliding action is saved, an existing record is overwritten, or inventory count changes.

9. Setup: with the created task already present.
Action: click `Manage Custom Tasks`, then `Edit`, verify current values preload, change `Trigger` to `Open`, change type to `File`, use `Browse...` to choose `C:\Reports\weekly.txt`, and save.
Expected Behavior: the edit dialog preloads the existing title, aliases, trigger choice, and target; type changes still update the default trigger until you deliberately choose a trigger yourself; the same saved action updates in place; and the examples box refreshes to match the edited trigger and target kind.
Failure Conditions / Edge Cases: preload is blank or incomplete, the trigger resets unexpectedly after a manual choice, browse support disappears for `File`, the examples box stays stale, the save creates a duplicate, or refresh only happens after restart.

10. Setup: after the valid edit succeeds.
Action: run the callable phrases that should still work for the edited task, then verify phrases that should no longer work after the trigger change.
Expected Behavior: the alias-root phrases still work; the current trigger family works; and phrases from trigger families you removed no longer resolve for that task.
Failure Conditions / Edge Cases: old trigger phrases still resolve after the trigger mode changed, current alias-root phrases do not resolve, or the title label behaves like an invocation source for the new task even when it is not in aliases.

11. Setup: with at least two saved actions present after a successful create or edit pass.
Action: click `Manage Custom Tasks`, choose `Delete` for one task, then return to the overlay and verify the remaining inventory.
Expected Behavior: the selected task is removed immediately without restart, the remaining tasks stay intact, the deleted task disappears from `Manage Custom Tasks`, and the overlay returns to entry-ready state with clear deletion feedback.
Failure Conditions / Edge Cases: deleting one task removes the wrong row, inventory does not refresh until restart, the deleted task still resolves as callable, or the overlay does not recover cleanly afterward.

12. Setup: use or create one saved action record that predates the alias-root invocation marker, then open `Created Tasks` and edit it without changing its compatibility mode.
Action: save a valid edit and then run the legacy task again by bare title.
Expected Behavior: the legacy task keeps its title-callable behavior after the edit because existing tasks must not silently convert.
Failure Conditions / Edge Cases: a legacy task loses bare-title callability after a normal edit, or it silently flips into the new alias-root model without an explicit migration step.

12. Setup: prepare at least eight valid saved actions and reopen the overlay.
Action: click `Created Tasks`, scroll the inventory there, find the seventh or eighth saved action, click `Edit`, change it, and save.
Expected Behavior: later items remain reachable through the secondary window, scrolling stays stable, the correct later item opens for editing, and the updated later item refreshes immediately after save.
Failure Conditions / Edge Cases: only the first six items remain editable, `Created Tasks` does not expose later rows cleanly, scroll behavior breaks layout, later `Edit` buttons open the wrong item, or later edits do not refresh correctly.

13. Setup: back up `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json`, then intentionally corrupt it with invalid JSON.
Action: reopen the overlay, try `Create Custom Task`, then open `Manage Custom Tasks`; if any saved-action rows still show `Edit`, try that too.
Expected Behavior: authoring is blocked cleanly with repair-oriented messaging, no dialog proceeds into a real save path, and the source is not silently rewritten. In a fail-closed invalid-source state, `Manage Custom Tasks` may still open for status visibility while edit affordances disappear entirely; that absence is acceptable as long as the UI does not expose a live edit path.
Failure Conditions / Edge Cases: the dialog opens anyway, the source is auto-repaired silently, inventory becomes inconsistent, a live edit path is still reachable against the broken source, or outside text/input-capture behavior regresses while blocked.

### Branch / Slice-Specific Validation Focus

- the entry-state surface remains lightweight and button-led rather than becoming a dense inline management surface
- `Create Custom Task` and `Created Tasks` remain the top-level authoring entry points on the initial NCP opening
- create and edit dialogs now expose an explicit `Trigger` field instead of relying on alias hacks
- `Launch`, `Open`, `Launch and Open`, and `Custom` stay bounded and exact rather than widening into fuzzy language
- new saved actions treat `Title` as a label and `Aliases` as the invocation roots
- custom trigger phrases are comma-separated, user-authored, and persisted separately from aliases
- runtime-generated callable phrases for new tasks include bare aliases and trigger + aliases
- legacy saved actions without the new invocation-mode marker keep title-plus-alias callability until an explicit migration path exists
- stronger headers and concise help icons improve readability without creating a text wall
- `Trigger` now sits directly below `Title` in the create/edit dialog flow
- help tooltips appear quickly and use a compact NDAI-styled presentation instead of slow generic hover bubbles
- field-specific helper text now lives in the tooltips instead of separate labels under each field
- the single bottom guidance/examples box shows sectioned suggested aliases, real callable phrases, and the relevant current target-format reminder
- `Application`, `Folder`, and `File` expose `Browse...` support while still allowing manual target entry
- `Website URL` stays direct-entry only
- generated trigger phrases participate in collision detection before write
- create and edit both route through the shared validation-before-write foundation
- successful saves reload the shared catalog immediately and refresh inventory without restart
- edit preserves saved-action identity instead of creating duplicates
- inventories larger than six saved actions keep every item reachable for editing
- the typed-first baseline and input-capture behavior remain unchanged while authoring is extended

## Related References

- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/workstreams/index.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`
