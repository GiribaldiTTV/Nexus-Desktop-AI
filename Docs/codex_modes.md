# Jarvis Codex Modes

## Purpose

This document formalizes the two Codex collaboration modes used in the Jarvis project:

- Analysis mode
- Workflow mode

The purpose of these modes is to keep planning, execution, and verification disciplined without weakening user authority, backlog control, or locked architecture boundaries.

This document is operational guidance for how Codex should collaborate inside Jarvis work.
It does not override `development_rules.md`, `orin_task_template.md`, version closeout facts, or explicit user approval requirements.

---

## Why Two Modes Exist

Jarvis work needs two different collaboration postures:

- one for evidence-first analysis, planning, audit, and direction validation
- one for carrying an approved narrow task through analysis, patching, verification, and closeout

Keeping those postures explicit helps prevent:

- premature patching
- scope drift
- silent backlog changes
- reopening closed version guarantees
- mixing planning with implementation before the architecture boundary is clear

---

## Analysis Mode

### Goal

Use Analysis mode when the immediate job is to understand, validate, challenge, audit, or sequence work before any patching begins.

### When To Use It

Use Analysis mode when:

- deciding whether a version, revision, or backlog item is the correct next target
- auditing whether a completed revision is clean enough to close
- identifying risks, missing evidence, or drift traps
- defining the safest scope for a future docs-only or patch task
- validating whether a proposed next move conflicts with source-of-truth docs
- investigating runtime bugs, behavior regressions, or other systems-level failures before patching
- tracing architecture-sensitive behavior where a shallow file-reference answer would be risky
- performing readiness or risk analysis that could directly lead to a patch recommendation
- performing post-version planning such as deciding whether `FB-015` is the correct next architecture-first target

### What Codex Should Do

Codex should:

- read the source-of-truth docs first
- inspect the relevant repo state before making recommendations
- validate assumptions against implemented behavior and documented boundaries
- identify the narrowest safe next step
- separate confirmed facts from inference
- call out risks, blockers, and conflicts directly
- recommend doc-first clarification when implementation boundaries are not yet tight enough

### Required Analysis Depth

Analysis mode is not one fixed depth for every task.

For a tiny docs review, narrow sanity check, or lightweight source-of-truth drift check, Codex should use only the analysis depth needed to answer the question cleanly.

For runtime bugs, behavior regressions, systems investigations, architecture-sensitive work, or readiness/risk analysis that could lead to patching, Analysis mode must become deep investigative analysis rather than shallow reference review.

Deep investigative analysis is also required for branch-level merge-readiness, PR-readiness, release-readiness, version-bump, or release-package review, even when no patch is being proposed.

When that deeper investigation applies, Codex should:

- trace the full execution or behavior chain from entry point to affected output
- identify direct files, indirect files, and regression-risk files
- explain current behavior versus intended behavior
- identify the relevant validators, state transitions, logging surfaces, config usage, and user-visible side effects
- list assumptions, unknowns, and evidence still needed
- define the smallest safe patch scope when a patch may be needed
- define the verification plan, including commands, log review, and user-test needs, before recommending patching or readiness

Analysis mode should follow those same requirements even when the user invokes it with only a short cue such as:

- `Analyze and Report`
- `Analyze for drift`
- `Analysis mode`
- `reference docs for the following`

Those shorthand prompts are mode selectors, not reduced-quality requests.
Codex should still load the default baseline from `docs/Main.md` and the directly relevant canonical docs before reporting.

### First Prompt Rule For New Post-Closeout Version Chats

In the first Codex prompt of each new post-closeout version chat, Analysis mode should explicitly address:

- what must be carried forward into the new version context
- what can be removed from the prompt because the source-of-truth docs already cover it

This keeps new-version chats grounded in the closed baseline without repeating version-closeout facts unnecessarily.

### What Codex Must Not Do

Codex must not:

- patch files
- change backlog state
- imply that unimplemented work already exists
- widen scope to "helpfully" include implementation
- smuggle in authority, policy meaning, or runtime coupling through analysis language
- reopen closed `v1.6.0`, `v1.7.0`, or `v1.8.0` guarantees without explicit user approval

### Expected Outputs

Analysis mode outputs should usually include:

- source-of-truth validation result
- readiness assessment
- recommended scope or next revision
- explicit non-goals
- drift risks
- whether a docs-only clarification should happen before patching
- recommended next move

When deep investigative analysis applies, outputs should also include:

- affected-chain summary
- current behavior versus intended behavior
- explicit assumptions, unknowns, and missing evidence
- smallest safe patch scope when patching is still a live outcome
- verification and user-test plan

Analysis mode should leave the repo unchanged.

---

## Workflow Mode

### Goal

Use Workflow mode only when the user has explicitly approved a narrow task and wants Codex to carry that exact task through end to end inside the approved boundaries.

### When To Use It

Use Workflow mode when:

- a docs-only pass has been clearly approved
- a narrow patch revision has been clearly approved
- a closeout sync is needed and its boundaries are already established
- the user has explicitly approved a bounded task rather than a broad implied workflow handoff

### What Codex Should Do

Codex should:

- still analyze first
- complete the required deep Analysis-mode investigation before editing when the task involves runtime bugs, behavior regressions, systems investigations, architecture-sensitive work, or readiness/risk analysis that could lead to patching
- define the exact narrow scope before editing
- make only the approved isolated change
- verify the result directly
- run the same user-facing test path or the closest faithful equivalent before handing that path back to the user when feasible
- report what changed and what was verified
- keep the source-of-truth docs aligned with actual implemented state
- stop and report if the task would require reopening locked architecture or widening beyond one controlled revision

Workflow mode should follow those same requirements even when the user invokes it with only a short cue such as:

- `Workflow mode`
- `docs-only pass`
- `patch this`
- `continue on this branch`

Those shorthand prompts are execution selectors, not permission to skip truth-doc reading, validation, or scope control.
Codex should still load the default baseline from `docs/Main.md`, infer the directly relevant canonical docs, and keep the same validation standard as a longer structured prompt.

Workflow mode means Codex carries the task responsibly, not mechanically.
Codex should behave like a careful senior collaborator who keeps progress moving without bypassing control boundaries.

For desktop-runtime validation inside Workflow mode, Codex should use the approved safe launcher path for testing rather than improvising raw shell launch commands. In practice, that means:

- prefer an approved helper in `dev/launchers/`
- or launch `desktop/orin_desktop_launcher.pyw` directly through `pythonw.exe`

Codex should only use the user-facing VBS or desktop shortcut path when the task specifically requires validating that wrapper layer itself.

### What Codex Must Not Do

Codex must not:

- treat workflow ownership as permission to widen scope
- patch runtime, behavior, or systems-impacting work before the required pre-patch investigation is complete
- silently change backlog status or priorities without explicit approval
- reopen version-closed behavior as a "small improvement"
- merge multiple conceptual fixes into one revision
- convert advisory or historical semantics into runtime policy
- treat Workflow mode as authority over user decisions

### Expected Outputs

Workflow mode outputs should usually include:

- source-of-truth validation result
- exact files changed
- exact minimal changes made
- why the change is sufficient
- verification summary
- whether validation is:
  - self-validated
  - helper-validated
  - or still user-only for the final gap
- any docs intentionally left unchanged
- commit summary
- commit description

Workflow mode should report the result, not paste the full contents of edited files.

Workflow mode may perform edits, but only after the task scope is explicitly approved and bounded.

---

## Batched Workstream Rule

Jarvis may use one tightly related batched workstream per prompt when that is the smallest coherent way to complete one approved subproblem.

A batched workstream is safe only when all of the following are true:

- one subsystem
- one end-state
- one coherent approved subproblem
- later slices are dependent completion steps of the same chain
- validation can still stay narrow and exact

Default batch target:

- 3-4 dependent sub-slices

Hard cap:

- 5 sub-slices only when slices 4-5 are low-risk completion steps such as containment, accepted dev-entry reachability, validator coverage, or tiny directly supportive truth-doc sync

Jarvis batched workstreams must not:

- mix unrelated subsystems
- mix production behavior changes with unrelated dev-tool or docs cleanup
- use filler batching just to make a prompt feel larger
- smuggle in backlog cleanup unrelated to the active workstream

### Validation Inside A Batched Workstream

When a batched workstream is approved, Workflow mode should use:

- baseline validation before edits
- slice-local validation after each code-bearing slice
- one final integrated validation at the end

### Batched-Workstream Stop Conditions

Stop the workstream early and report immediately if:

- a source-of-truth conflict appears
- the next slice would cross into another subsystem
- the next slice would reopen locked production behavior outside the approved scope
- safe verification for the current slice is not possible
- the current slice fails validation
- the remaining slices are no longer obviously required to complete the same end-state

### Docs And Backlog Sync Inside A Batched Workstream

Directly supportive doc sync may travel with the active workstream when it records that exact implemented work and does not widen scope.

Backlog sync remains controlled:

- exact markdown approval is still required before editing `docs/feature_backlog.md`
- only the exact active workstream truth may be synced
- unrelated backlog cleanup must stay separate

### Docs-Only Governance Pass Batching

When the user explicitly approves a docs-only governance or source-of-truth pass, that pass may batch several directly related clarifications when they all serve one coherent workflow or canon end-state.

This is allowed only when:

- the edits stay inside one governance lane
- the file scope stays minimal
- the pass does not widen into unrelated repo cleanup
- the pass does not mix in runtime implementation work
- backlog status or priority changes are not made without separate approval

## Grouped Workstream Branch Rule

For `pre-Beta` planning, Codex may recommend or use a grouped workstream branch when:

- the work belongs to one clear category or subsystem
- several related ideas are better handled as one lane than as disconnected micro-branches
- the lane is suitable for multi-developer coordination
- each actual revision inside the branch can still stay narrow and validated

Examples of valid grouped workstream branches:

- interaction
- UI / UX
- workflow / GitHub infrastructure
- diagnostics / tooling

A grouped workstream branch does not authorize one broad patch.

Instead, it means:

- one branch may host a sequence of approved narrow slices
- one focused branch may also carry multiple small related patches when they all serve the same project-focus lane
- one focus-group lane may also carry one larger coherent implementation when that is still the smallest safe milestone inside the same subsystem
- each slice inside that branch still needs clear scope and verification
- each small patch inside that branch must still stay narrow, validated, and within the same subsystem boundary
- unrelated ideas should still be split out even if they are all deferred work

For `pre-Beta`, the default branch strategy should usually prefer focus-group lanes over one branch per micro-fix when:

- the lane stays inside one subsystem or category
- the lane still follows one coherent milestone path
- the resulting branch does not become a grab-bag of unrelated follow-through

For those `pre-Beta` focus-group lanes:

- merge cadence should follow meaningful lane milestones rather than every tiny follow-through
- release cadence should follow meaningful lane milestones when a release is appropriate
- grouped branches must still be split if the work starts crossing subsystem boundaries or accumulating unrelated fixes

## Grouped Lane Milestone Gate

For an active `pre-Beta` grouped workstream branch, Codex should define before implementation:

- the lane milestone target
- the minimum merge-ready threshold
- the tightly coupled groundwork that still belongs inside the same branch

Codex should not treat the first validated revision inside that branch as PR-ready by default.

Instead, Codex should continue through additional narrow slices inside the same branch until:

- the declared minimum merge-ready threshold is reached
- a real blocker appears
- or the user explicitly chooses to stop early

If enabling groundwork and the first usable outcome are tightly coupled inside one subsystem and remain low-risk, they should usually stay in the same grouped branch rather than being split into separate micro-branches or premature PRs.

At `Beta` and later, the default recommendation should usually shift toward:

- issue-specific branches
- bug-fix branches
- single-idea branches

unless a grouped branch remains clearly justified.

## Fresh Branch Start After A Closed Workstream

After a prior workstream branch has been merged, released if applicable, and deleted, the next workstream should start from updated `main` on a fresh branch.

Codex should not create that next branch until:

- the live post-merge or post-release repo state has been verified
- the next workstream plan is clearly established
- the user has approved that next branch path

Once those conditions are met, creating the fresh branch may be the first Workflow-mode step of the new workstream.

---

## Shared Rules Across Both Modes

These rules apply in both modes:

- analyze first
- verify exact behavior or exact doc alignment before changing anything
- no blind iteration
- minimal isolated changes only
- preserve architecture boundaries
- one fix per revision
- production behavior must remain unchanged unless explicitly in scope
- logs, code, and current repo docs are the source of truth for implemented behavior
- when a source-of-truth conflict exists, call it out explicitly before proceeding

## Live-State Readiness Sanity Check

Before Codex generates any readiness or release package such as:

- merge-ready or release-ready judgments
- version bump recommendations
- PR title or PR body output
- release title or release notes output

Codex must verify live repo state first.

Those readiness reviews are Analysis-mode work and must use deep investigative analysis rather than shallow branch-summary reasoning.

That live-state check must include:

- whether the referenced branch is still active
- whether that branch has already been merged
- whether related tag or release state already exists
- whether the prompt framing is stale relative to current repo or GitHub state

For branch-level merge-ready or release-ready review, that deeper analysis should also cover:

- the actual branch scope and what changed on that branch
- whether any active bug, unresolved drift, or dirty worktree state remains
- whether verification evidence is strong enough for the claimed readiness level
- whether closed guarantees, milestone expectations, or release facts could be reopened by the current branch state

If the prompt framing is stale, Codex must not generate a fresh hypothetical readiness package.

Instead, Codex should:

- report the actual current state
- explain which assumptions in the prompt were stale
- recommend the true next move from the live state

## Readiness Output Content Rule

When Codex is asked to provide PR-ready or release-ready output, the default should be to describe what is included in the work under review.

Codex should not add a `Not included` section unless:

- the user explicitly asks for one
- omitting it would create a real scope misunderstanding for the active task

In slice-sizing terms:

- one fix per revision means one coherent approved subproblem per revision
- minimal isolated changes means the minimal coherent approved change set needed to close that subproblem
- use the smallest safe slice for architecture clarification, boundary-setting, and high-risk behavior or policy work
- use the smallest coherent slice for lower-risk post-boundary feature delivery when a smaller fragment would leave an incomplete first deliverable

Neither mode permits:

- silent scope expansion
- silent backlog control changes
- policy drift disguised as wording cleanup
- authority expansion disguised as confidence or intelligence work

In Jarvis work, Codex must not return the full contents of created or edited files.

Codex should instead return:

- a summary of what changed
- the changed file path or paths
- the approved scope
- the verification performed

If actual file review is needed, the file should be reviewed outside Codex by uploading it for inspection.

## Pull Request Opening Boundary

Codex may open or submit a pull request directly only for an approved docs-only branch.

For code branches or mixed code/docs branches, Codex may:

- perform PR-readiness analysis
- provide the exact PR title and PR body
- provide merge and release posture guidance

For those non-docs-only branches, Codex should stop short of opening the PR.

---

## Backlog-Control Reminder

`docs/feature_backlog.md` remains a controlled planning layer.

Codex may:

- propose backlog changes
- draft exact backlog markdown for approval

Codex may not:

- silently edit backlog status or priority fields
- mark items complete without approval
- reorder backlog items without approval

If backlog state needs to change, user approval is still required even in Workflow mode.

---

## Relationship To `orin_task_template.md`

`docs/orin_task_template.md` remains the per-task execution scaffold.

This document does not replace the template.
Instead:

- `orin_task_template.md` defines the structure of an individual task request
- `codex_modes.md` defines the collaboration posture Codex should take while handling that task

In practice:

- Analysis mode pairs naturally with `analysis-only`, `planning-only`, and audit tasks in the template
- Workflow mode pairs naturally with approved `docs-only` and `patch` tasks in the template

If the template and a casual user request conflict, Codex should follow the explicit structured task and the source-of-truth docs.

---

## Prompt Hygiene After Consolidation

When a workstream has been consolidated into a canonical planning or design doc, prompts should prefer that canonical doc over the earlier slice-by-slice planning stack.

This keeps prompts shorter, reduces duplicate source lists, and prevents archival reasoning docs from being treated like equal-weight current truth.

### Analysis Mode Guidance

In Analysis mode, Codex should:

- use `docs/Main.md` as the routing index for the active source-of-truth set
- identify whether a canonical consolidated doc already exists for the active workstream
- carry forward that canonical doc instead of the full stack of superseded slice docs
- explicitly say what older slice docs can be removed from the prompt because the canonical doc already covers them
- pull older slice docs back in only if the task is about historical tracing, consolidation audit, or source conflict checking

### Workflow Mode Guidance

In Workflow mode, Codex should:

- use `docs/Main.md` plus the relevant canonical doc or docs as the default prompt baseline for the active workstream
- use the canonical consolidated doc as the primary planning baseline for the active workstream
- avoid re-listing archival slice docs unless the approved task explicitly depends on them
- keep the prompt evidence set narrow and current rather than mechanically repeating every earlier planning file
- prioritize the active code workstream when the task is code-focused
- bundle directly supporting truth-doc updates into the same approved workstream when that keeps docs aligned without widening scope
- prefer milestone-level or canonical doc sync over repeated separate doc-only micro-passes when docs are not the primary deliverable

### Prompt Reduction After Closeout

Once a version has a closeout doc and the directly supportive truth-sync items are complete, future prompts should usually:

- cite the latest relevant closeout doc instead of re-listing the full completed-workstream recap
- carry forward only the baseline facts still needed for the next version lane
- omit validator, harness, and reachability details that are already captured in the closeout and backlog truth unless the new task depends on them directly
- avoid repeating the full batched-workstream rule block when `codex_modes.md` is already part of the prompt baseline

Closeout cadence and whether a new closeout is actually needed should follow `docs/closeout_guidance.md` rather than being assumed mechanically from the existence of a release, branch merge, or docs-only pass.

### Current Boot-Planning Example

For current Jarvis work, `docs/Main.md` should be the default docs index and prompt-baseline map.

For current Jarvis boot-access work, `docs/boot_access_design.md` is the canonical boot planning source.

That means future boot-access prompts should usually prefer:

- `development_rules.md`
- `Main.md`
- `architecture.md`
- `orin_vision.md`
- `feature_backlog.md`
- `orchestration.md`
- `boot_access_design.md`
- relevant closeout docs only when still needed

The earlier `boot_*_plan.md` slice docs have been retired from the active docs tree and should not be listed as prompt inputs unless they are reintroduced separately for historical review outside the normal planning baseline.

---

## Practical Rule Of Thumb

If the user is asking:

- "What should we do next?"
- "Is this the right next version or revision?"
- "Is this complete enough to close?"

Use Analysis mode.

If the user is asking:

- "Carry this approved docs-only pass"
- "Implement this exact narrow revision"
- "Own this closeout sync"

Use Workflow mode.

When in doubt, start in Analysis mode first.
