# User Test Summary Guidance

## Purpose

This document defines how Nexus Desktop AI uses User Test Summary (`UTS`) handoff.

`UTS` is a validation-contract layer.
It is owned by the relevant workstream and this guidance document.

`UTS` is not:

- a backlog field
- a roadmap field
- a separate tracking system

## Ownership Model

Use this ownership split:

- workstream doc = why the validation matters and how it fits the lane
- `Docs/user_test_summary_guidance.md` = the structure and handling rules for the handoff
- returned `UTS` evidence = user validation input that must be digested before recommending the next move

Docs-only passes that do not require user-run validation normally do not need a `UTS`.

When a task changes user-visible behavior or another operator-facing path, the default handoff expectation is that Codex will include a `## User Test Summary` section in its implementation or validation output unless manual testing is not materially relevant.

## When A User Test Summary Is Needed

Create a `UTS` when the active workstream needs user-run validation, especially for:

- launch or relaunch flows
- UI or visual confirmation
- user-visible interaction or UX changes
- startup, first-run, or reopen behavior
- prompts, inline messaging, or operator-facing guidance changes
- voice behavior
- create, edit, recovery, or other manual operator-facing workflows
- Dev Toolkit helpers
- repaired runtime paths
- bounded regression checks after an approved slice

## Output Requirement For Codex Responses

When manual validation is relevant, `## User Test Summary` in a Codex response must be a true manual test checklist, not a recap.

The default checklist must include:

- setup or prerequisites
- exact user actions
- expected visible behavior
- failure signs to watch for
- branch-specific or slice-specific validation focus

If the work changes multiple user-visible paths, the checklist should separate those paths explicitly enough that the user can run them one by one.

If no meaningful manual test exists, Codex must still include `## User Test Summary` and say explicitly:

- that no meaningful manual test is required for this slice
- why manual validation is not materially relevant
- what was validated instead

## Required Structure

When a `UTS` is needed, structure it around:

- `Test Purpose`
- `Scenario / Entry Point`
- `Steps To Execute`
- `Expected Behavior`
- `Failure Conditions / Edge Cases`
- `Validation Evidence Expectations`

Keep the steps concrete and action-oriented.
Make the expected outcome specific enough that the user can tell what passed or failed.

A recap-style behavior summary is not sufficient when the user needs to run or verify anything manually.

## Desktop File Rule

When a durable desktop copy is needed, use the rolling file:

- `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`

Create or refresh that file when:

- the user explicitly asks for it
- the validation flow is long enough that a durable copy helps
- the user is likely to test outside the chat window
- Dev Toolkit launch metadata must be preserved exactly

## Required Desktop File Sections

When the desktop file is created or refreshed, prefer this structure:

- `Workstream`
- `What This Test Is Checking`
- `Expected Outcome`
- `Test Steps`
- `Observed Results`
- `New Ideas / Requests Raised During Testing`
- `Questions / Confusions Raised During Testing`
- `Regression Notes`

If a step expects user feedback, include an explicit response slot directly under that step.

## Dev Toolkit Metadata Rule

For Dev Toolkit runs, copy these fields exactly as shown in the UI:

- `Launch Mode`
- `Purpose`
- `Test / Helper`
- `Delay`

Do not paraphrase or shorten those labels.

## Digest Rule After Submission

When the user returns a filled `UTS`, Codex must digest it before recommending the next move.

That digest should separate:

- what passed
- what failed
- what remained unclear
- what new ideas or requests appeared
- what belongs to the current workstream
- what should be deferred

## Carry-Forward Approval Rule

Ideas surfaced through a returned `UTS` must not be silently added to:

- `Docs/feature_backlog.md`
- roadmap sequencing
- canonical planning docs

until Codex provides:

- a concise evidence digest
- extracted ideas
- any recommended refinement
- a clear recommendation for where the idea belongs

and the user explicitly approves the carry-forward.

## Self-Validation Before Handoff

Before giving the user a manual `UTS` handoff for a runtime or UI path, Codex should run that same path or the closest faithful equivalent when feasible.

If that is not possible, Codex must say:

- what was self-validated
- what was helper-validated only
- what still requires user-only validation
- why the gap could not be closed locally
