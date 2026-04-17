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
Repo-wide phase, timeout, proof-authority, and stop-loss rules for this workstream are inherited from `Docs/phase_governance.md`; this record captures the branch-local phase state, evidence, and active seam trail.

## Current Phase

- Phase: `Docs / Canon Sync`
- Substate: `Post-Green Evidence Refresh`

## Phase Entry Basis

- the branch contains the integrated FB-036 + Idea 5 implementation truth, including callable groups and the latest UI/inventory follow-through
- repo-side and live-style validators are already green on the branch
- the exact current branch truth now has fresh fully green watchdog-backed interactive proof under the tightened default timing profile:
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260417_093651.txt`
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260417_105920.txt`
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260417_110929.txt`
- the latest exact-branch proof is:
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260417_110929.txt`
- the latest live launched-process UI audit is:
  - `dev/logs/launcher_live_window_audit/20260417_110602/manifest.json`
- together those artifacts prove:
  - the full interactive gate is green on the exact current branch truth
  - the tightened budget profile is now the default harness profile rather than a manual override
  - the Create Custom Task visual regression introduced during the efficiency pass was corrected without reopening any failing interactive seam
  - real launched-process screenshots of the overlay, task dialogs, group dialogs, and invalid-source dialogs remain aligned with the intended dark/translucent UI direction

## Phase Exit Criteria

- the timeout contract in this workstream doc matches the live harness defaults
- the seam ledger is current and no active seam remains
- the latest green interactive evidence and the live launched-process UI audit are both recorded here
- only after those are true should this workstream move to `PR Readiness`

## Validation Contract

Validation layers for this workstream are intentionally separated:

- repo-side validators
  - persistence safety
  - collision rules
  - invocation generation
  - fail-closed authoring behavior
- live-style validation
  - runtime markers
  - catalog reload
  - saved-actions source updates
  - reopen behavior
- interactive OS-level validation
  - hotkey entry
  - real dialog interaction
  - real group and ambiguity flows
  - cleanup behavior

### Validation Authority Matrix

- primary authority: runtime markers
- secondary authority: persisted source snapshots
- tertiary authority: UIAutomation usability and readback
- optional or non-gating observations by default:
  - help buttons
  - examples-box refresh
  - transient blocked-status labels

UI-only observations may become gating only when the UI interaction itself is the thing under test.
Otherwise they should be recorded as notes and must not override stronger runtime and persisted-source truth.

For the current exact-branch closeout state:

- there is no remaining active seam
- authoritative branch-closeout proof is:
  - the latest full interactive gate is green on the exact current branch truth
  - persisted source snapshots remain correct across create, edit, group, ambiguity, reopen, and invalid-source paths
  - cleanup completed without probe leakage or source corruption
- explicitly non-gating observations for the current green state:
  - delayed `ATTEMPT_STARTED` markers when later success or blocked markers prove the same business transition
  - early help-button readiness
  - examples-box refresh lag
  - first-attempt foreground/focus noise when the target control still becomes interactable within the tightened budget

Current branch-local proven interactive scenarios:

- `valid_create` is currently proven and passing
- `valid_group_create` is currently proven and passing
- `invalid_create_rejection_application` is currently proven and passing
- `collision_rejection` is currently proven and passing
- `group_collision_rejection` is currently proven and passing
- `valid_edit` is currently proven and passing
- `invalid_edit_rejection` is currently proven and passing
- `exact_match_execution` is currently proven and passing
- `saved_alias_ambiguity` is currently proven and passing
- `group_exact_invocation` is currently proven and passing
- `task_inline_group_quick_create` is currently proven and passing
- `reopen_persistence` is currently proven and passing
- `large_inventory_reachability` is currently proven and passing
- `unsafe_source_blocking` is currently proven and passing
- `invalid_group_source_blocking` is currently proven and passing
- `no_input_leakage` is currently proven and passing

### Resolved Invalid-Create Overlay-Recovery Seam

- invalid `Application` create business correctness and cancel recovery are now both proven on the exact current branch state
- the latest green reports move through the blocked marker, no-write proof, dialog close, and overlay recovery path within the tightened default budgets
- blocked-status UI readback remains informational only unless that exact label is the thing under test

### Resolved Collision-Rejection Seam

- `collision_rejection` now reaches runtime proof cleanly under the tightened default budgets
- the latest green reports observe the create-attempt path quickly enough that the collision blocker is no longer a timing seam

### Resolved Valid-Edit Popup-Selection Seam

- `valid_edit` now completes under the tightened default budgets on the exact current branch state
- the previous popup-first `Folder` selection stall is no longer able to trip the no-progress watchdog before edit proof completes
- the latest green reports prove the edit dialog updates the action in place and refreshes inventory immediately

## Timeout Contract

- preflight startup gate: `<= 60s`
- seam or control-acquisition gate: `<= 3s` for the interactive driver once the surface is already opened and marker-ready
- no-progress watchdog default: `3s`
- normal scenario budget default: `60s`
- exceptional scenario budget: none currently declared
- transition budget default: `3s`
- full interactive run hard cap default: `1800s`
- outer execution timeout should sit only slightly above the harness hard cap

Undocumented slower profiles are not allowed during normal continuation. If a future slice needs a relaxed profile, it must be explicit, documented, and revalidated rather than silently inherited.

## Current Active Seam

- `none`
- latest proving report:
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260417_110929.txt`
- current branch status note:
  - the full interactive gate is green on the exact current branch truth using the harness defaults `1800s / 3s / 60s / 3s`

## Stop-Loss Threshold

- one active seam at a time
- rerun the full gate immediately after the seam fix
- stop after `2` seam fixes in one governed closeout pass
- stop after `90 minutes` of closeout recovery work and report findings instead of continuing

## Seam Ledger

| Seam | Classification | Current status |
| --- | --- | --- |
| probe startup / notepad acquisition | `harness defect` | fixed earlier in branch-local hardening |
| create-dialog combo acquisition | `harness defect` | fixed earlier in branch-local hardening |
| `valid_create` examples-box dependency | `harness defect` | fixed by marker-first create success criteria |
| runtime marker detection instability | `harness defect` | partially stabilized through created-marker inference |
| group-dialog name input acquisition | `harness defect` | fixed earlier in branch-local hardening |
| group-dialog members region acquisition | `harness defect` | fixed earlier in branch-local hardening |
| overlay reopen / marker reacquisition instability | `harness defect` | fixed earlier in branch-local hardening |
| stale UIAutomation element/property shape crashes | `harness defect` | reduced through null-safe and live-resolution helpers |
| system-wide focus drift / offscreen focus rectangles / global click interference | `environment issue` | still present as late-run noise |
| blank blocked-status readback with correct runtime/source truth | `environment issue` | still present as non-blocking noise |
| `task_inline_group_quick_create :: Assign Group button usability/focus reacquisition` | `harness defect` | resolved during governed hardening; the latest `20260417` green reports prove the task dialog can keep moving through group assignment without focus-churn stalls |
| `task_inline_group_quick_create :: inline group draft handoff used the wrong dialog contract` | `product defect` | resolved by switching the inline group return path onto the callable-group draft builder; the latest `20260417` green reports and persisted-source snapshots prove the new inline group now persists atomically with the task |
| `invalid_create_rejection_application :: stale timeout carryover into overlay recovery after close-after-cancel proof` | `harness defect` | resolved; later `20260417` green reports move through invalid-create recovery under the tightened default budgets |
| `valid_edit :: scenario budget exhausted before or at CUSTOM_TASK_EDIT_ATTEMPT_STARTED after slow combo/type mutation and field verification` | `harness defect` | resolved; the latest green reports move through edit proof under the tightened default budgets |
| `invalid_create_rejection_application :: overlay input recovery after Application cancel` | `harness defect` | resolved; the current green reports reopen and reacquire the overlay cleanly after invalid-create cancel |
| `collision_rejection :: timeout before or at CUSTOM_TASK_CREATE_ATTEMPT_STARTED for Explorer Helper` | `harness defect` | resolved; the latest green reports prove the collision path under the tightened default budgets |
| `valid_edit :: no-progress stall during popup-first Folder type selection` | `harness defect` | resolved; the latest green reports move past the popup-first type-selection path without tripping the `3s` no-progress watchdog |

## Current Branch Truth

- the branch already includes safe saved-action persistence, bounded deletion, and explicit catalog reload after writes
- the branch now also treats callable groups as first-class persisted authoring objects that live alongside saved tasks in the same source document
- the branch already includes a type-first create flow and a bounded edit flow
- the entry-state NCP opening now stays lightweight and button-led, with peer `Create Custom Task`, `Manage Custom Tasks`, `Create Custom Group`, and `Manage Custom Groups` actions as the primary authoring entry points
- detailed saved-action inventory viewing and edit reachability now live in the secondary `Manage Custom Tasks` window instead of being expanded inline on the initial opening surface
- the secondary `Manage Custom Tasks` window now supports both edit and delete actions for existing saved tasks
- standalone callable-group creation and management now live in dedicated `Create Custom Group` and `Manage Custom Groups` windows that mirror the task surfaces without widening into batch automation
- create/edit dialogs now expose an explicit `Trigger` field with `Launch`, `Open`, `Launch and Open`, and `Custom` options
- new saved actions now use alias-root invocation, with `Title` treated as a label and callable phrases generated at runtime from `aliases`, `trigger_mode`, and optional `custom_triggers`
- groups stay alias-only in this lane
  - `Group name` is label-only
  - `Aliases` are the exact callable phrases
  - there is no group `Trigger` field
  - there is no title-callable fallback for groups
- legacy saved actions that do not yet carry the new invocation-mode marker still remain title-plus-alias callable so existing tasks do not silently change behavior
- create/edit dialogs now use stronger field headers with label-hover help, darker integrated chrome, and a single callable-surface panel that updates from the current title, aliases, trigger selection, and target kind
- create/edit dialogs now place `Trigger` directly below `Title`, use faster NDAI-styled help tooltips from the field labels themselves, and keep the callable-surface panel to the right of the form for clearer scanning
- exact-match resolution remains unchanged
- new integrated truth now allows multiple saved actions to share the same exact callable phrase while still keeping exact-match normalization and resolution bounded
- saved-vs-saved exact ambiguities now surface through the existing overlay ambiguity chooser, then continue through the normal confirm step before execution
- exact group invocation now uses that same bounded chooser and confirm flow, but only after an exact group alias expands to the group's explicit members
- built-in vs saved callable-phrase overlap still remains blocked rather than becoming ambiguous in this lane
- group aliases must remain unique against built-ins, saved-task callable phrases, and other group aliases, so there is no mixed task/group ambiguity in v1
- the overlay phase machine remains bounded to `entry` -> `choose` -> `confirm` -> `result`
- current supported saved-action target kinds remain `app`, `folder`, `file`, and `url`
- group membership is explicit and static by action ID
  - groups may include both built-ins and saved tasks
  - groups may not include other groups
  - empty persisted groups are invalid
- malformed group records or dangling member references now produce a group-specific invalid state that blocks group create/manage and group invocation without blocking healthy task authoring or normal task execution
- task create/edit flows now include bounded single-group assignment, including inline quick-create of a new group that is committed atomically with the task save instead of being written early
- deleting a saved task now also removes that task from any groups in the same atomic write
- malformed or colliding saved-action sources still block authoring rather than attempting salvage
- branch-local validation and hardening work now also includes dedicated FB-036 validators, live-style harnesses, interactive runtime helpers, durable validation reports, and exported manual-test artifacts that future slices should reuse rather than recreate blindly
- the `2026-04-15` fully green interactive report remains important historical proof for the earlier integrated truth:
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260415_115705.txt`
- the current exact-branch truth now also includes:
  - a fresh fully green watchdog-backed interactive report using the default harness budgets on `2026-04-17`
  - a live launched-process window audit proving the key overlay, task, group, and invalid-source windows still match the intended UI direction after the efficiency hardening

## Scope

- bounded saved-action create and edit UX
- bounded saved-action deletion from the secondary `Manage Custom Tasks` window
- bounded callable-group create, edit, and delete UX
- safe persistence and validation-before-write
- immediate catalog reload after successful writes
- explicit user-facing type selection mapped to the current persisted target kinds
- a lightweight landing path for task authoring and management that does not overload the initial NCP opening surface
- richer secondary create/manage windows that can carry the detailed explanations, guidance, and step-by-step authoring copy users need once they choose an action path
- explicit callable-group aliases and explicit member selection without weakening the exact-match resolver contract
- bounded single-group assignment, including inline quick-create of a new group from the task dialog
- short inline field guidance inside the secondary create/edit windows so users get quick help without overloading the initial landing surface
- title-driven alias suggestions, explicit trigger configuration, alias-root invocation for new tasks, and a bottom-of-dialog dynamic invocation examples box inside the secondary create/edit windows
- browse-assisted target selection for `Application`, `Folder`, and `File` that fills the existing validated `Target` field while `Website URL` stays direct-entry only

## Non-Goals

- disable flows
- Action Studio behavior
- taskbar or tray authoring surfaces
- overlay phase changes
- new persisted action kinds
- batch group execution
- nested groups
- mixed task/group ambiguity
- malformed-source repair logic
- built-in vs saved ambiguity
- ambiguity ranking logic changes
- fuzzy matching
- dynamic natural-language grouping or query behavior

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
14. extended the same exact-match authoring lane with callable groups, bounded single-group assignment, and exact group invocation through the existing chooser + confirm flow

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
  Current default time budgets after the efficiency hardening pass: full run `1800s`, no-progress watchdog `3s`, normal scenario budget `60s`, transition budget `3s`, with cleanup, last-progress reporting, and watchdog enforcement still required on timeout.

- `dev/orin_launcher_live_window_audit.ps1`
  Purpose: branch-local live launched-process window audit driver that captures the real overlay, task, group, and invalid-source windows from the running desktop process for post-green UI review.
  Introduced: during the `2026-04-17` post-green audit pass.
  Classification: `interactive-only`.
  Reuse: use this after meaningful UI or interaction hardening changes when the branch needs real launched-process screenshots rather than synthetic widget captures.

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

- `dev/logs/launcher_live_window_audit/`
  Purpose: durable report and artifact root for live launched-process UI audits, including the manifest and the captured real-window screenshots.
  Introduced: during the `2026-04-17` post-green UI audit pass.
  Classification: `interactive-only`.
  Reuse: append new audit folders here whenever a future branch needs live window screenshots to confirm UI direction after interaction or styling changes.

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
- task authoring now supports bounded single-group assignment and inline quick-create without leaving the task flow
  - the inline group return path now uses the callable-group draft builder, so the newly created group reappears immediately in `Available Groups` and is persisted atomically with the task save
- the interactive harness now defaults to the tightened efficiency profile that actually proved green on the exact current branch state
  - `full run 1800s`
  - `no-progress 3s`
  - `scenario 60s`
  - `transition 3s`
- the live Create Custom Task window retains the intended darker/translucent guidance treatment after the efficiency pass
  - the brief opaque black fill regression in the callable-surface/examples area was corrected before final closeout evidence was recorded
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
  - the `2026-04-17` passing interactive runs are now the exact current-branch proof under the tightened default budget profile
  - the final passing interactive run on `2026-04-15` remains important historical proof for the earlier integrated branch truth, but it is no longer the latest closeout anchor

### Validation Infrastructure And Reuse Guidance

- primary interactive driver
  - `dev/orin_saved_action_authoring_interactive_validation.ps1`
  - reuse this first for any future FB-036 regression or governed closeout rerun
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

- some early dialog help buttons still are not ready before the first required field interactions
  - the current green runs record that noise, but the required inputs remain interactable within the tightened default budgets
- some `ATTEMPT_STARTED` markers still lag behind stronger later markers
  - the current green runs rely on later authoritative runtime truth such as `CUSTOM_TASK_CREATED`, `CUSTOM_TASK_CREATE_BLOCKED`, or `CUSTOM_TASK_EDIT_BLOCKED` when those markers prove the same business transition
- first-attempt foreground/focus acquisition can still log noise for overlay input and inventory buttons
  - the current green runs show those controls still become usable quickly enough that the `3s` no-progress watchdog is not breached
- the bottom guidance/examples box can still lag slightly during early create interaction
  - the live launched-process audit confirms the panel now renders correctly again after the translucency fix, and the current harness treats content-refresh lag as non-blocking when stronger runtime/source truth already exists
- the Notepad probe still sometimes uses the file-backed fallback because the external text control is not always immediately available after launch
- these notes are real but non-blocking
  - they should be treated as future polish or future harness hardening candidates, not as reasons to reopen FB-036 closeout

### Evidence References

- latest exact-branch green interactive report
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260417_110929.txt`
- latest exact-branch green runtime log
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_runtime.log`
- latest exact-branch green step log
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_interactive_steps.log`
- latest exact-branch green snapshots
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_initial_source_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_after_create_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_after_group_create_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_after_edit_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_after_task_inline_group_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_after_large_inventory_edit_saved_actions.json`
  - `dev/logs/fb_036_authoring_interactive_validation/artifacts/20260417_110929_after_invalid_group_source_recovery_saved_actions.json`
- supporting post-fix green interactive report
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260417_105920.txt`
- first tightened-budget green report from the efficiency pass
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260417_093651.txt`
- latest live launched-process UI audit manifest
  - `dev/logs/launcher_live_window_audit/20260417_110602/manifest.json`
- key live launched-process UI audit captures
  - `dev/logs/launcher_live_window_audit/20260417_110602/overlay_entry.png`
  - `dev/logs/launcher_live_window_audit/20260417_110602/create_custom_task_error.png`
  - `dev/logs/launcher_live_window_audit/20260417_110602/edit_custom_task.png`
  - `dev/logs/launcher_live_window_audit/20260417_110602/available_groups.png`
  - `dev/logs/launcher_live_window_audit/20260417_110602/create_custom_group_direct.png`
  - `dev/logs/launcher_live_window_audit/20260417_110602/manage_custom_tasks.png`
  - `dev/logs/launcher_live_window_audit/20260417_110602/manage_custom_groups.png`
  - `dev/logs/launcher_live_window_audit/20260417_110602/manage_custom_tasks_invalid_source.png`
  - `dev/logs/launcher_live_window_audit/20260417_110602/manage_custom_groups_invalid_source.png`
- historical governed seam-history reports remain relevant for the recovery trail
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260416_161300.txt`
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260416_153450.txt`
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260416_151450.txt`
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260416_145604.txt`
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260416_143010.txt`
  - `dev/logs/fb_036_authoring_interactive_validation/reports/FB036SavedActionAuthoringInteractiveValidationReport_20260416_135000.txt`

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
  - historical hardening proof baseline: full interactive pass on `feature/fb-036-validation-hardening`

### Current Branch Baseline

- historically validated behavior that future work may still rely on
  - bounded create/edit/delete flows
  - alias-root invocation for new tasks
  - legacy compatibility preservation
  - explicit trigger-family behavior
  - exact-match execution after create/edit
  - reopen persistence
  - large-inventory edit reachability
  - fail-closed unsafe-source blocking
  - no-input-leakage proof during interactive authoring
- branch-local validation infrastructure that future work should reuse
  - the dedicated FB-036 validators
  - the live-style harness
  - the interactive runtime helper
  - the watchdog-enforced interactive harness
  - the live launched-process window audit helper
  - the evidence roots and saved-action snapshot pattern
- current closeout status means
  - the exact current branch state is now fully green under the default interactive harness budgets `1800s / 3s / 60s / 3s`
  - the live launched-process window audit confirms the user-facing windows remain visually aligned after the interaction-efficiency hardening and the create-dialog translucency fix
  - future Codex or developer work should treat this workstream record, the latest `2026-04-17` green proof package, and the live audit captures as the baseline to extend

## User Test Summary

### Test Purpose

Confirm that the full FB-036 branch behavior is stable for real desktop use, including:

- safe custom-task creation
- bounded in-place editing
- bounded deletion from `Manage Custom Tasks`
- safe custom-group creation
- bounded custom-group editing and deletion
- explicit Trigger configuration with runtime-generated callable phrases
- alias-root invocation for newly created tasks without silently changing legacy tasks
- exact callable-group aliases with explicit static membership
- bounded single-group assignment, including inline quick-create
- validation-before-write for every supported target kind
- immediate catalog reload after save
- fail-closed handling for unsafe saved-action sources
- edit reachability for inventories larger than six items
- saved-vs-saved exact-match ambiguity surfaced through candidate selection
- exact group invocation surfaced through the same chooser + confirm flow
- built-in-vs-saved overlap still blocked before write
- no regression in the typed-first overlay baseline

### Scenario / Entry Point

Open the desktop overlay on `feature/fb-036-idea5-integrated-hardening` with a healthy `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json` source and use the lightweight button-led entry surface as the authoring landing path:

- `Create Custom Task`
- `Manage Custom Tasks`
- `Create Custom Group`
- `Manage Custom Groups`

### Setup / Prerequisites

- start from a clean desktop runtime launch on `feature/fb-036-idea5-integrated-hardening`
- keep a safe outside text target open, such as Notepad, so stray typing is easy to spot
- know where `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json` lives
- for the large-inventory checks, prepare at least eight valid saved actions in the source
- for the unsafe-source checks, back up `saved_actions.json` before intentionally corrupting it

### Steps To Execute

1. Setup: launch the desktop runtime and open the overlay in its normal typed-first way.
Action: inspect the entry-state panel before typing anything.
Expected Behavior: the overlay opens in the normal entry baseline, the initial landing surface stays lightweight, `Create Custom Task`, `Manage Custom Tasks`, `Create Custom Group`, and `Manage Custom Groups` are all visible as peer actions, and no inline saved-action detail or `Edit` buttons overload the first surface.
Failure Conditions / Edge Cases: the overlay skips entry state, any top-level authoring button is missing, inline inventory/edit detail still clutters the landing surface, or outside text receives stray typing.

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

9. Setup: with at least one built-in action and one saved task visible to the current source.
Action: click `Create Custom Group`, enter `Group name = Workspace Tools`, add aliases such as `Workspace Tools, Tools Group`, select both a built-in member and a saved-task member, and save.
Expected Behavior: the group saves successfully only when it has at least one valid member and unique aliases; the callable-surface panel shows exact group aliases only; and the new group appears immediately in `Manage Custom Groups` without restart.
Failure Conditions / Edge Cases: the group saves with no members, aliases collide with built-ins or saved-task phrases, generated trigger phrases appear even though groups are alias-only, or the group only appears after restart.

10. Setup: with the new group present.
Action: type one of the exact group aliases into the normal overlay input, choose the built-in member first, confirm, then repeat and choose the saved-task member.
Expected Behavior: the exact group alias opens the existing chooser with that group's members only; member selection advances to the normal confirm step; and only the selected built-in or saved task executes.
Failure Conditions / Edge Cases: the group alias executes immediately without showing members, non-member actions appear in the chooser, the chooser skips confirm, or the wrong member executes.

11. Setup: with an existing saved task that is not yet assigned to a callable group.
Action: open `Create Custom Task` or edit an existing task, confirm the dialog starts with `Assign Group...`, assign one existing group, then unassign it and use the inline quick-create path to create a new group for the current task and save.
Expected Behavior: tasks stay limited to one assigned group at a time; the main task dialog swaps `Assign Group...` for `Unassign Group` once one group is attached; inline quick-create reuses the same `Create Custom Group` window with only `Group name` and `Aliases`; the new group is not persisted early; and the saved task plus the new membership land together in one atomic write.
Failure Conditions / Edge Cases: multiple groups can be assigned at once, the inline group persists before the task save succeeds, the current task does not become the first member, group assignment is lost after save, or the task flow leaves the dialog unexpectedly.

12. Setup: with the created task already present.
Action: click `Manage Custom Tasks`, then `Edit`, verify current values preload, change `Trigger` to `Open`, change type to `File`, use `Browse...` to choose `C:\Reports\weekly.txt`, and save.
Expected Behavior: the edit dialog preloads the existing title, aliases, trigger choice, and target; type changes still update the default trigger until you deliberately choose a trigger yourself; the same saved action updates in place; and the examples box refreshes to match the edited trigger and target kind.
Failure Conditions / Edge Cases: preload is blank or incomplete, the trigger resets unexpectedly after a manual choice, browse support disappears for `File`, the examples box stays stale, the save creates a duplicate, or refresh only happens after restart.

13. Setup: after the valid edit succeeds.
Action: run the callable phrases that should still work for the edited task, then verify phrases that should no longer work after the trigger change.
Expected Behavior: the alias-root phrases still work; the current trigger family works; and phrases from trigger families you removed no longer resolve for that task.
Failure Conditions / Edge Cases: old trigger phrases still resolve after the trigger mode changed, current alias-root phrases do not resolve, or the title label behaves like an invocation source for the new task even when it is not in aliases.

14. Setup: with at least two saved actions present after a successful create or edit pass and with one of those tasks belonging to a group.
Action: click `Manage Custom Tasks`, choose `Delete` for one task, then return to the overlay and verify the remaining inventory and the affected group.
Expected Behavior: the selected task is removed immediately without restart, the remaining tasks stay intact, the deleted task disappears from `Manage Custom Tasks`, the deleted task also disappears from any group membership in the same write, and the overlay returns to entry-ready state with clear deletion feedback.
Failure Conditions / Edge Cases: deleting one task removes the wrong row, inventory does not refresh until restart, the deleted task still resolves as callable, the deleted task remains in a group member list, or the overlay does not recover cleanly afterward.

15. Setup: use or create one saved action record that predates the alias-root invocation marker, then open `Manage Custom Tasks` and edit it without changing its compatibility mode.
Action: save a valid edit and then run the legacy task again by bare title.
Expected Behavior: the legacy task keeps its title-callable behavior after the edit because existing tasks must not silently convert.
Failure Conditions / Edge Cases: a legacy task loses bare-title callability after a normal edit, or it silently flips into the new alias-root model without an explicit migration step.

16. Setup: prepare at least eight valid saved actions and multiple valid groups, then reopen the overlay.
Action: click `Manage Custom Tasks`, scroll the inventory there, find the seventh or eighth saved action, click `Edit`, change it, and save; then open `Manage Custom Groups`, scroll to a later group, and verify edit/delete reachability there too.
Expected Behavior: later items remain reachable through both secondary windows, scrolling stays stable, the correct later item opens for editing, and later task/group edits refresh immediately after save.
Failure Conditions / Edge Cases: only the first six items remain reachable, either management window breaks layout while scrolling, later `Edit` buttons open the wrong record, or later edits do not refresh correctly.

17. Setup: back up `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json`, then intentionally corrupt only the `groups` section or insert a dangling group member ID while keeping the task records themselves valid.
Action: reopen the overlay, try `Create Custom Task`, `Manage Custom Tasks`, `Create Custom Group`, and `Manage Custom Groups`, then try invoking a normal task and a group alias.
Expected Behavior: normal task authoring and normal task invocation remain available; group create/manage and group invocation are blocked cleanly with repair-oriented messaging; and the source is not silently rewritten.
Failure Conditions / Edge Cases: task authoring is blocked even though only groups are invalid, a broken group can still be invoked, the source is auto-repaired silently, or outside text/input-capture behavior regresses while blocked.

### Branch / Slice-Specific Validation Focus

- the entry-state surface remains lightweight and button-led rather than becoming a dense inline management surface
- `Create Custom Task`, `Manage Custom Tasks`, `Create Custom Group`, and `Manage Custom Groups` remain the top-level authoring entry points on the initial NCP opening
- create and edit dialogs now expose an explicit `Trigger` field instead of relying on alias hacks
- `Launch`, `Open`, `Launch and Open`, and `Custom` stay bounded and exact rather than widening into fuzzy language
- new saved actions treat `Title` as a label and `Aliases` as the invocation roots
- callable groups treat `Group name` as a label and `Aliases` as the exact callable phrases
- groups stay alias-only with no trigger expansion, no title-callable fallback, and no mixed task/group ambiguity
- group aliases remain unique against built-ins, saved-task phrases, and other groups
- exact group invocation reuses the chooser + confirm flow instead of inventing a second execution surface
- task create/edit dialogs support bounded single-group assignment and inline group quick-create without early persistence
- deleting a task removes its group membership in the same write
- invalid groups fail closed for group flows only and do not block healthy task flows
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
