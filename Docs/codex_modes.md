# Jarvis Codex Modes

## Purpose

This document formalizes the two Codex collaboration modes used in the Jarvis project:

- Analysis mode
- Workflow mode

The purpose of these modes is to keep planning, execution, and verification disciplined without weakening user authority, backlog control, or locked architecture boundaries.

This document is operational guidance for how Codex should collaborate inside Jarvis work.
It does not override `development_rules.md`, `jarvis_task_template.md`, version closeout facts, or explicit user approval requirements.

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
- define the exact narrow scope before editing
- make only the approved isolated change
- verify the result directly
- report what changed and what was verified
- keep the source-of-truth docs aligned with actual implemented state
- stop and report if the task would require reopening locked architecture or widening beyond one controlled revision

Workflow mode means Codex carries the task responsibly, not mechanically.
Codex should behave like a careful senior collaborator who keeps progress moving without bypassing control boundaries.

### What Codex Must Not Do

Codex must not:

- treat workflow ownership as permission to widen scope
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
- any docs intentionally left unchanged
- commit summary
- commit description

Workflow mode should report the result, not paste the full contents of edited files.

Workflow mode may perform edits, but only after the task scope is explicitly approved and bounded.

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

## Relationship To `jarvis_task_template.md`

`docs/jarvis_task_template.md` remains the per-task execution scaffold.

This document does not replace the template.
Instead:

- `jarvis_task_template.md` defines the structure of an individual task request
- `codex_modes.md` defines the collaboration posture Codex should take while handling that task

In practice:

- Analysis mode pairs naturally with `analysis-only`, `planning-only`, and audit tasks in the template
- Workflow mode pairs naturally with approved `docs-only` and `patch` tasks in the template

If the template and a casual user request conflict, Codex should follow the explicit structured task and the source-of-truth docs.

---

## Immediate Next Planning Guidance After `v1.8.0`

After `v1.8.0`, the next safe high-level move is post-`v1.8.0` architecture work rather than launcher-policy tuning.

Based on current source-of-truth docs, `FB-015` is the strongest architecture-first next planning target unless a later source-of-truth conflict proves otherwise.

Why `FB-015` is the cleanest next move:

- `feature_backlog.md` places `FB-015` in `Post-v1.8.0`
- `FB-015` is explicitly a phase-boundary and architecture-modeling item
- `FB-015` stays out of boot-level control, adaptive retries, and launcher behavior changes
- `v1.8.0_closeout.md` already identifies post-`v1.8.0` architecture work such as `FB-015` as the next safe high-level target

### How Analysis Mode Should Be Used First

Use Analysis mode first to:

- confirm that `FB-015` is still the correct next target
- validate whether any source-of-truth conflict appeared after `v1.8.0` closeout
- define the narrowest safe `FB-015` planning scope
- determine whether the first `FB-015` step should be docs-only architecture clarification before any implementation work

### How Workflow Mode Should Be Used Later

Use Workflow mode only after the user explicitly approves a narrow `FB-015` task such as:

- a docs-only architecture planning pass
- a bounded phase-boundary clarification
- a later approved implementation slice if and only if the architecture phase has already been defined and accepted

Workflow mode should not be used to jump directly from `v1.8.0` closeout into boot-control implementation.

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
