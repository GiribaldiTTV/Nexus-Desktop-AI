# User Test Summary Guidance

## Purpose

This document is the canonical source-of-truth guidance for when Jarvis work should produce:

- a user-facing `User Test Summary` in the response
- the desktop `User Test Summary.txt` file for the user

It exists so future Codex work follows one consistent manual-test handoff model instead of recreating that behavior ad hoc in chat history.

Returned `User Test Summary` files must be treated as active evidence inputs, not as disposable notes.

## When A User Test Summary Is Needed

Create a `User Test Summary` whenever the active task results in a user-visible validation handoff, especially when the user needs to:

- launch or relaunch a runtime path manually
- verify a UI or visual change
- exercise a Dev Toolkit lane or helper
- confirm that a repaired path reaches the intended file, helper, or state
- check for regression after a bounded patch

Do not add a separate `User Test Summary` for purely internal analysis or for docs-only work that does not require the user to run anything.

## When The Desktop `User Test Summary.txt` File Is Needed

Create or update the desktop `User Test Summary.txt` file when:

- the user explicitly asks for one
- the manual test steps are long enough that a durable desktop copy will help
- the task depends on a multi-step launch or validation flow that the user is likely to follow outside the chat window
- the task uses a Dev Toolkit lane or helper and the exact launch/test metadata must be preserved cleanly

The desktop file should:

- mirror the user-facing manual steps given in the response
- be written to the desktop location the user actually sees
- prefer the visible OneDrive desktop path when the machine uses a OneDrive-backed desktop
- use one uniform filename:
  - `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`
- be treated as the rolling current test handoff file rather than creating a new filename for each slice
- be overwritten or refreshed with the newest test instructions whenever a new user-visible test handoff replaces the old one

## Required Structure For The Desktop File

When the desktop `User Test Summary.txt` file is created or refreshed, it should prefer this structure:

- `Workstream`
- `What This Test Is Checking`
- `Expected Outcome`
- `Test Steps`
- `Observed Results`
- `New Ideas / Requests Raised During Testing`
- `Questions / Confusions Raised During Testing`
- `Regression Notes`

For any step that expects a user reply, the file should include an explicit response slot directly under that step, such as:

- `Response:`
- `Notes:`

Do not force the user to guess where feedback should go.
Do not make the user answer the same validation question again later in a second redundant section.

If a later summary section exists, it should synthesize the step responses rather than repeat the same yes/no prompts.

## User Additions During Testing

User additions raised during testing must not be silently discarded just because they appear inside the `User Test Summary.txt` file.

These additions may include:

- new product ideas
- new constraints
- naming concerns
- hotkey requests
- privacy expectations
- clarification requests
- newly noticed bugs or regressions

Codex should preserve those additions in the file under a clearly separate section such as:

- `New Ideas / Requests Raised During Testing`
- `Questions / Confusions Raised During Testing`
- `Regression Notes`

This separation is important:

- test-result evidence should stay readable as test evidence
- new ideas should still be captured for later digestion

User additions should also be treated as raw inputs rather than final canon wording.

That means Codex should:

- preserve the user's original request or concern faithfully
- refine or clarify the idea when helpful using repo truth, current architecture boundaries, and the product vision
- avoid changing the intended meaning of the user's request while improving precision, scope clarity, or terminology
- explicitly distinguish between the user's raw idea and Codex's refined recommendation when summarizing follow-through

## Digest Rule After Submission

After the user returns a filled `User Test Summary.txt`, Codex must explicitly digest it before recommending the next move.

That digest should separate:

- what passed
- what failed
- what remained unclear or confusing
- what new ideas or requests were introduced during testing
- what belongs to the current slice
- what should be deferred into backlog or future source-of-truth consideration

That digest should also include:

- whether each new idea aligns with the current product vision and architecture boundaries
- whether Codex recommends refining the user's wording before any truth-doc or backlog carry-forward
- whether the idea is best treated as:
  - current-slice follow-through
  - future source-of-truth clarification
  - future backlog candidate
  - not currently recommended

Codex should use project truth when refining ideas, including:

- `docs/orin_vision.md`
- `docs/architecture.md`
- the canonical doc for the active workstream
- any directly relevant closeout or planning doc

Codex must not:

- ignore newly introduced user requests
- treat every new idea as automatically in scope for the current patch
- leave the file unanalyzed after the user submits it

## Approval Rule For Carry-Forward

Ideas surfaced through a returned `User Test Summary.txt` must not be silently added to:

- `docs/feature_backlog.md`
- canonical planning docs
- active source-of-truth docs that materially expand planned behavior

until Codex first provides the user with:

- a concise digest of the relevant test evidence
- a summary of the extracted ideas
- any recommended refinement to align the idea with repo truth, product vision, or architecture boundaries
- a clear recommendation for where the idea belongs

and the user explicitly approves that carry-forward.

This approval rule exists even when the idea is good.

The purpose is:

- to preserve user control over backlog and canon growth
- to avoid silent scope expansion from live testing feedback
- to make sure Codex analyzes and refines ideas before proposing them as truth

Directly supportive truth-doc updates for the active approved code task may still be bundled into the same workstream when the user has already approved that truth pass, but new ideas discovered during testing remain approval-gated.

## Historical Summary Review Rule

When the user explicitly asks Codex to revisit earlier `User Test Summary` submissions, Codex should review any recoverable prior summaries or directly preserved returned evidence before recommending new carry-forward.

That review should separate:

- what older summary artifacts are still recoverable
- what ideas were already carried into canon or code
- what ideas appear to have been missed
- which missed ideas should now be proposed for approval-gated carry-forward

If older summaries are no longer recoverable from the local environment, Codex should say so clearly and rely only on the evidence still available rather than pretending a historical review was complete.

## Required Dev Toolkit Metadata

If the user is asked to run a Dev Toolkit instruction, the `User Test Summary` must include the exact:

- `Launch Mode`
- `Purpose`
- `Test / Helper`
- `Delay`

The desktop `User Test Summary.txt` file should carry the same four fields exactly when it is created or refreshed for a Dev Toolkit run.

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

## Desktop File Convention

Use one stable desktop filename for user-facing manual test handoff:

- `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`

Do not create a new slice-specific or workstream-specific desktop filename unless the user explicitly asks for a separate durable record.

Default rule:

- one rolling desktop file
- same visible filename every time
- newest active manual-test instructions replace the previous contents

## Response Rule

## Self-Validation Before Handoff

Before Codex gives the user a manual `User Test Summary` handoff for a runtime or UI path, Codex should first run that same path or the closest faithful equivalent when feasible.

When this is possible, the handoff should reflect what Codex already verified directly.

When this is not possible, Codex must say so clearly and identify:

- what was self-validated
- what was only helper-validated
- what still requires user-only validation
- why the remaining gap could not be closed locally

Codex must not imply that a user-facing path was personally verified if the actual path could not be run reliably from the current environment.

When a `User Test Summary` is needed:

- keep it short and action-oriented
- include expected results, not just steps
- explicitly call out anything that is intentionally not part of the current slice
- keep the step wording concrete enough that the user can tell what visual or runtime outcome they are supposed to confirm
- avoid redundant adjacent steps that sound like the same action unless the second step clearly explains the additional verification target
- when two nearby steps are related but not identical, state the distinction directly so the user knows whether the second step means "launch it" versus "confirm a separate behavior after launch"

When the desktop `User Test Summary.txt` file is also created or refreshed:

- keep the response summary and desktop file aligned
- do not let the desktop file contain extra hidden requirements that were not shown to the user in the response
- reference the same desktop file path in the response rather than inventing a new filename for the current slice
- make sure any prompted user response line has a visible blank line or direct `Response:` slot under it
