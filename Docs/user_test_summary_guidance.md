# User Test Summary Guidance

## Purpose

This document is the canonical source-of-truth guidance for when Jarvis work should produce:

- a user-facing `User Test Summary` in the response
- a desktop `.txt` test-instructions file for the user

It exists so future Codex work follows one consistent manual-test handoff model instead of recreating that behavior ad hoc in chat history.

## When A User Test Summary Is Needed

Create a `User Test Summary` whenever the active task results in a user-visible validation handoff, especially when the user needs to:

- launch or relaunch a runtime path manually
- verify a UI or visual change
- exercise a Dev Toolkit lane or helper
- confirm that a repaired path reaches the intended file, helper, or state
- check for regression after a bounded patch

Do not add a separate `User Test Summary` for purely internal analysis or for docs-only work that does not require the user to run anything.

## When A Desktop `.txt` Test File Is Needed

Create a desktop `.txt` test-instructions file when:

- the user explicitly asks for one
- the manual test steps are long enough that a durable desktop copy will help
- the task depends on a multi-step launch or validation flow that the user is likely to follow outside the chat window
- the task uses a Dev Toolkit lane or helper and the exact launch/test metadata must be preserved cleanly

The desktop `.txt` file should:

- mirror the user-facing manual steps given in the response
- use a clear slice- or workstream-based filename
- be written to the desktop location the user actually sees
- prefer the visible OneDrive desktop path when the machine uses a OneDrive-backed desktop

## Required Dev Toolkit Metadata

If the user is asked to run a Dev Toolkit instruction, the `User Test Summary` must include the exact:

- `Launch Mode`
- `Purpose`
- `Test / Helper`
- `Delay`

The desktop `.txt` file should carry the same four fields exactly when it is created for a Dev Toolkit run.

For Dev Toolkit runs, these fields must be copied from the visible Dev Toolkit dropdown selections exactly as shown in the UI.

- `Launch Mode` must use the exact combo label, for example `Quiet (No Audio / No Voice)` or `With Voice / Audio`
- `Purpose` must use the exact Purpose dropdown group label, not a prose explanation
- `Test / Helper` must use the exact lane label shown in the Test / Helper dropdown
- `Delay` must use the exact Launch Delay dropdown label, for example `Now`, `3s`, `5s`, or `10s`

Do not replace these four fields with paraphrases such as:

- `quiet`
- `none`
- `Validate Slice 3 shell-branding neutralization`
- `Dev Toolkit -> Diagnostics UI Test`

If a Dev Toolkit run is part of the handoff, the user-facing steps should also tell the user which exact dropdown options to choose before launching the lane.

## Filename Guidance

Use a clear slice- or workstream-based desktop filename, for example:

- `Nexus_Desktop_AI_Slice1_User_Test_Summary.txt`
- `ORIN_Boot_Path_Slice2_User_Test_Summary.txt`
- `Dev_Toolkit_Boot_Helper_User_Test_Summary.txt`

Prefer stable, readable filenames over generic names like `test.txt` or `notes.txt`.

## Response Rule

When a `User Test Summary` is needed:

- keep it short and action-oriented
- include expected results, not just steps
- explicitly call out anything that is intentionally not part of the current slice

When a desktop `.txt` file is also created:

- keep the response summary and desktop file aligned
- do not let the desktop file contain extra hidden requirements that were not shown to the user in the response
