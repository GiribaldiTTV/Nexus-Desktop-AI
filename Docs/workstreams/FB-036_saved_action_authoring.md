# FB-036 Saved-Action Authoring

## ID And Title

- ID: `FB-036`
- Title: `Limited saved-action authoring and type-first custom task UX`

## Record State

- `Promoted`

## Status

- `Active on feature/fb-036-saved-action-authoring`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Purpose / Why It Matters

Deliver a bounded in-product path for creating and editing saved actions without reopening the typed-first interaction contract or expanding into Action Studio behavior.

This workstream exists so users can manage non-standard custom tasks safely through the existing shared action model instead of hand-editing JSON.

## Current Branch Truth

- the branch already includes safe saved-action persistence and explicit catalog reload after writes
- the branch already includes a type-first create flow and a bounded edit flow
- exact-match resolution remains unchanged
- the overlay phase machine remains bounded to `entry` -> `choose` -> `confirm` -> `result`
- current supported saved-action target kinds remain `app`, `folder`, `file`, and `url`
- malformed or colliding saved-action sources still block authoring rather than attempting salvage

## Scope

- bounded saved-action create and edit UX
- safe persistence and validation-before-write
- immediate catalog reload after successful writes
- explicit user-facing type selection mapped to the current persisted target kinds
- small reachability follow-through needed to keep authoring usable from the entry-state inventory

## Non-Goals

- delete or disable flows
- Action Studio behavior
- taskbar or tray authoring surfaces
- resolution-model changes
- overlay phase changes
- new persisted action kinds
- malformed-source repair logic

## Executed Slices So Far

1. added the safe persistence foundation and catalog reload seam
2. added the type-first create flow
3. added the bounded edit flow with identity-preserving updates
4. tightened target validation for `app`, `folder`, and `file`
5. expanded saved-action inventory reachability so edit is no longer capped to the first six items

## User Test Summary

### Test Purpose

Confirm that the full FB-036 branch behavior is stable for real desktop use:

- safe custom-task creation
- bounded in-place editing
- validation-before-write for every supported target kind
- immediate catalog reload after save
- fail-closed handling for unsafe saved-action sources
- edit reachability for inventories larger than six items
- no regression in the typed-first overlay baseline

### Scenario / Entry Point

Open the desktop overlay on `feature/fb-036-saved-action-authoring` with a healthy `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json` source and use the entry-state inventory as the only authoring entry point.

### Setup / Prerequisites

- start from a clean desktop runtime launch on `feature/fb-036-saved-action-authoring`
- keep a safe outside text target open, such as Notepad, so stray typing is easy to spot
- know where `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json` lives
- for the large-inventory checks, prepare at least eight valid saved actions in the source
- for repeated-stability checks, plan to create or edit at least two saved actions in one session
- for the unsafe-source checks, back up `saved_actions.json` before intentionally corrupting it

### Steps To Execute

1. Setup: launch the desktop runtime and open the overlay in its normal typed-first way.
Action: inspect the entry-state panel before typing anything.
Expected Behavior: the overlay opens in the normal entry baseline, the saved-action inventory is visible, and `Create Custom Task` is available without changing the overlay phase model.
Failure Conditions / Edge Cases: the overlay skips entry state, the create trigger is missing, the inventory panel is absent, or outside text receives stray typing.

2. Setup: stay in entry state with a healthy saved-action source.
Action: click `Create Custom Task`, choose `Folder`, enter `Title = Open Reports`, `Aliases = show reports`, `Target = C:\Reports`, then save.
Expected Behavior: the dialog closes, success feedback appears in entry state, and the new saved action appears in inventory immediately without restart.
Failure Conditions / Edge Cases: the dialog closes without feedback, the inventory does not refresh, the overlay leaves entry state unexpectedly, or the source file is not updated.

3. Setup: with `Open Reports` now visible in inventory.
Action: type the exact title or alias into the normal overlay input and execute it through the existing typed-first flow.
Expected Behavior: the overlay still follows the normal `entry -> confirm -> result` path for an exact match, and the new saved action resolves immediately.
Failure Conditions / Edge Cases: no match is found, resolution becomes ambiguous unexpectedly, confirm behavior changes, or the action only works after restart.

4. Setup: open `Create Custom Task` again.
Action: test invalid creates one at a time:
`Application` with `Target = notepad.exe --help`
`Folder` with `Target = Reports\Daily`
`File` with `Target = C:\Reports\bad?.txt`
`Website URL` with `Target = example.com/docs`
Expected Behavior: each invalid case stays in the dialog, shows a clear validation error, and writes nothing to disk.
Failure Conditions / Edge Cases: any invalid target is accepted, the dialog closes anyway, the inventory changes, or the error text is vague or missing.

5. Setup: with at least one saved action already present.
Action: attempt collision creates:
use a built-in title like `Open Windows Explorer`
use another saved action's existing title or alias
Expected Behavior: the dialog stays open, collision feedback is clear, and no write occurs.
Failure Conditions / Edge Cases: a colliding action is saved, an existing record is overwritten, or inventory count changes.

6. Setup: with `Open Reports` still present in inventory.
Action: click `Edit`, verify the dialog preloads current values, change the title to `Open Weekly Reports`, change the type to `File`, set the target to `C:\Reports\weekly.txt`, and save.
Expected Behavior: the dialog preloads the existing title, aliases, type, and target; save closes it; success feedback appears; the same saved action updates in place; and the inventory refreshes immediately without creating a duplicate.
Failure Conditions / Edge Cases: blank preload, duplicate item creation, wrong action updated, missing feedback, or inventory refresh only after restart.

7. Setup: edit an existing saved action again.
Action: try invalid or colliding edits:
change the target to `Reports\Weekly`
change the title to a built-in title
change the title to another saved action's title
Expected Behavior: the dialog stays open, clear errors appear, the original record remains unchanged, and nothing is written.
Failure Conditions / Edge Cases: invalid edits save, collisions overwrite another action, or the original action mutates despite the error.

8. Setup: prepare at least eight valid saved actions and reopen the overlay.
Action: scroll the inventory, find the seventh or eighth saved action, click `Edit`, change it, and save.
Expected Behavior: later items remain reachable, scrolling stays stable, the correct later item opens for editing, and the updated later item refreshes immediately after save.
Failure Conditions / Edge Cases: only the first six items remain editable, scroll behavior breaks layout, later `Edit` buttons open the wrong item, or later edits do not refresh correctly.

9. Setup: after one or more successful creates or edits.
Action: close the overlay, reopen it, and inspect the inventory again.
Expected Behavior: the newly created or edited saved actions are still present with their latest values, showing that the change persisted and reload behavior was not only in-memory.
Failure Conditions / Edge Cases: changes disappear after reopen, stale values return, or the overlay reopens with stale typed request / confirm / result state.

10. Setup: after a successful create and a successful edit, keep the same session open.
Action: create or edit one more valid saved action, close the overlay, reopen it again, and confirm the full inventory state.
Expected Behavior: repeated authoring operations remain stable, inventory count stays correct, updated values persist, and no stale entry/confirm/result state leaks across reopen cycles.
Failure Conditions / Edge Cases: repeated operations create duplicates, later saves disappear on reopen, stale overlay state returns, or entry-state feedback becomes inconsistent after multiple cycles.

11. Setup: back up `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json`, then intentionally corrupt it with invalid JSON.
Action: reopen the overlay and try both `Create Custom Task` and `Edit`.
Expected Behavior: create/edit are blocked cleanly with repair-oriented messaging, no dialog proceeds into a real save path, and the source is not silently rewritten.
Failure Conditions / Edge Cases: the dialog opens anyway, the source is auto-repaired silently, inventory becomes inconsistent, or outside text/input-capture behavior regresses while blocked.

### Branch / Slice-Specific Validation Focus

- create and edit both route through the shared validation-before-write foundation
- `app`, `folder`, `file`, and `url` validation all fail closed before disk write
- successful saves reload the shared catalog immediately and refresh inventory without restart
- edit preserves saved-action identity instead of creating duplicates
- malformed or colliding source states block authoring rather than attempting salvage
- inventories larger than six saved actions keep every item reachable for editing
- repeated create/edit/reopen cycles do not leave stale overlay state or orphaned saved-action records
- the typed-first baseline and input-capture behavior remain unchanged while authoring is added

## Related References

- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/workstreams/index.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`
