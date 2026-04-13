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

- workstream doc = why the validation matters, how it fits the lane, and the canonical repo-level `UTS` artifact for that workstream unless a different repo path is explicitly declared there
- `Docs/user_test_summary_guidance.md` = the structure and handling rules for the handoff
- response-level `## User Test Summary` = the current user-facing handoff copy, not a replacement for the canonical repo artifact
- returned `UTS` evidence = user validation input that must be digested before recommending the next move

Docs-only passes that do not require user-run validation normally do not need a `UTS`.

When a task changes user-visible behavior or another operator-facing path, the default handoff expectation is that Codex will include a `## User Test Summary` section in its implementation or validation output unless manual testing is not materially relevant.

## Canonical Repo Artifact Rule

For active desktop workstreams, the default canonical repo-level `UTS` artifact is:

- the `## User Test Summary` section inside the relevant canonical workstream doc under `Docs/workstreams/`

Use a different repo-level artifact path only when that workstream doc explicitly declares one.

When a slice changes user-visible behavior or another operator-facing desktop path, Codex must normally do both:

- include a detailed `## User Test Summary` section in the response or output when manual validation is relevant
- update the canonical repo-level `UTS` artifact for the active workstream in the same branch
- export or refresh `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` as the user-facing convenience copy when the slice is a relevant desktop path

Response-only `UTS` text is not sufficient when the canonical repo artifact exists and the supporting docs for that workstream are in scope.

If the canonical repo artifact is not updated, Codex must say explicitly why. The normal allowed reasons are:

- no meaningful manual test exists for the slice
- no canonical workstream doc exists yet, so there is no active repo-level `UTS` owner to update
- the user explicitly restricted the pass so the supporting workstream doc or declared repo artifact could not be changed
- the relevant workstream doc already says that no separate ongoing `UTS` artifact remains for that closed lane
- the desktop export is not relevant because the slice is not a desktop or user-facing manual-validation path

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

That desktop file is the required user-facing exported copy for relevant desktop slices.
It is not the canonical repo-level `UTS` artifact unless a workstream doc explicitly says otherwise.

Create or refresh that file by default when:

- the slice changes desktop user-visible behavior or another desktop operator-facing path
- the user is likely to test outside the chat window
- the validation flow is long enough that a durable copy helps
- Dev Toolkit launch metadata must be preserved exactly

If the slice is not a relevant desktop manual-validation path, Codex may skip the desktop export only if it says so explicitly and explains why.

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

For relevant desktop or operator-facing slices, if the implemented path can be launched and exercised through a real desktop session in the current environment, Codex must treat that interactive OS-level session as the default self-validation gate before recommending normal continuation.

If that is not possible, Codex must say:

- what was self-validated
- what was helper-validated only
- what still requires user-only validation
- why the gap could not be closed locally

When the current validation surface is too thin to support that self-validation, Codex must add or create the smallest reliable supporting validation artifacts on-branch first when feasible.

Examples include:

- new or extended validators
- harnesses or scripted helpers
- fixtures or reproducible sample inputs
- runtime logs, traces, or screenshots
- other durable evidence artifacts needed to prove what was actually exercised

Codex must preserve an evidence trail for that self-validation and distinguish clearly between:

- validator results
- synthetic or headless validation results
- simulated reasoning or code-inspection findings
- interactive OS-level executed-path results
- user-only manual handoff that still remains

## Implementation-Time Hardening Rule

For runtime, UI, startup, prompt, voice, or other operator-facing implementation slices, the required validator suite is only one layer of validation.

Codex must also perform a deeper branch-local validation and hardening pass before continuing to the next implementation slice. That pass should:

- inspect the implemented path for likely failure modes and integration regressions
- add or create the smallest reliable validation infrastructure when meaningful blind spots remain
- use supporting validation artifacts when needed, such as harnesses, fixtures, scripted helpers, runtime logs, traces, screenshots, or reproducible sample inputs
- use synthetic or headless validators and harnesses as supporting proof rather than the final continuation gate when a real desktop session is feasible
- launch and exercise the real desktop or runtime path through an interactive OS-level session when feasible, rather than stopping at simulated reasoning or headless proof
- preserve evidence of what was run, what passed or failed, and where the supporting artifacts live
- produce an explicit judgment about whether the next move is:
  - continue implementation
  - pause for hardening or internal validation
  - or make a corrective fix first

Green validators plus simulated reasoning, response-level summary text, and synthetic/headless harness results are not enough when the implemented path can still be exercised through a real interactive desktop session.

If that interactive path is not feasible, Codex must explain why, use the strongest available non-interactive evidence, and state that the continuation judgment is limited by the missing interactive validation.
