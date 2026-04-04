# Jarvis Main

## Purpose

This document is the source-of-truth index and prompt-baseline map for the Jarvis docs set.

Its job is to:

- define the current source-of-truth structure
- separate active canonical docs from historical or optional references
- keep future prompts shorter and more consistent
- point work toward the right canonical doc without bulk-listing the whole docs tree

`Main.md` is an index and routing document.
It does not replace the authority of the docs it points to.

## How To Use This File

For most Jarvis tasks, prompts should include:

- `docs/development_rules.md`
- `docs/Main.md`
- only the directly relevant canonical doc or docs for the active workstream
- only the relevant evidence inputs

Add closeout docs, historical docs, or extra planning docs only when they are materially needed for the specific task.

## Current Source-Of-Truth Structure

### Core Authoritative Docs

These are the default project-governance and product-boundary docs:

- `docs/development_rules.md`
- `docs/Main.md`
- `docs/architecture.md`
- `docs/jarvis_vision.md`
- `docs/feature_backlog.md`
- `docs/orchestration.md`
- `docs/codex_modes.md`
- `docs/jarvis_task_template.md`

Within that core set:

- `docs/jarvis_vision.md` owns the product-wide meaning of `pre-Beta`, `Beta`, and `Full`
- `docs/feature_backlog.md` owns per-item or per-slice release-stage assignment

Use these when the task concerns:

- repo-wide rules
- architecture boundaries
- product direction
- backlog control
- orchestration ownership
- prompt or workflow governance, including batched-workstream execution rules

### Canonical Workstream Docs

These are the current canonical planning docs for specific active planning areas:

- `docs/boot_access_design.md`
- `docs/jarvis_interaction_architecture.md`
- `docs/workspace_layout_plan.md`

Current canonical ownership:

- `boot_access_design.md` is the canonical boot-planning source
- `jarvis_interaction_architecture.md` is the canonical interaction-planning source
- `workspace_layout_plan.md` is the canonical workspace-planning source

Use these only when the task is directly about those workstreams.

### Historical / Optional Docs

These docs are still valid, but they are not part of the default prompt baseline for every task:

- `docs/v1.6.0_closeout.md`
- `docs/v1.7.0_closeout.md`
- `docs/v1.8.0_closeout.md`
- `docs/v1.9.0_closeout.md`
- `docs/v2.0_closeout.md`
- `docs/v2.2.0_closeout.md`

Use them when the task depends on:

- version guarantees
- version closeout facts
- post-closeout sequencing
- auditing whether later work reopens closed version behavior

### Retired / Archive Docs

Retired or archival planning docs are not part of the active docs tree or the default prompt baseline.

If older slice docs or archival planning artifacts are reintroduced for historical tracing, treat them as optional evidence only, not equal-weight current truth.

## Default Prompt Baselines By Task Type

### General Minimal Baseline

For most tasks, start with:

- `docs/development_rules.md`
- `docs/Main.md`
- the directly relevant canonical doc or docs
- relevant evidence inputs

Do not bulk-list unrelated docs by default.

### Code Progression / Patch Work

For active code work, prompts should usually include:

- `docs/development_rules.md`
- `docs/Main.md`
- the directly relevant canonical doc or docs
- the relevant logs, screenshots, traces, or test evidence

Add closeout docs only if the patch could affect a closed version guarantee.

### Boot Work

For boot-planning or future boot-access work, prompts should usually include:

- `docs/development_rules.md`
- `docs/Main.md`
- `docs/boot_access_design.md`

Add `architecture.md`, `jarvis_vision.md`, `feature_backlog.md`, or `orchestration.md` when the task touches authority, vision, backlog scope, or launcher-owned desktop boundaries.

### Workspace / Folder Organization Work

For workspace-organization work, prompts should usually include:

- `docs/development_rules.md`
- `docs/Main.md`
- `docs/workspace_layout_plan.md`

Add `architecture.md` or startup-path docs only if path-sensitive surfaces are directly involved.

### Analysis / Sequencing Work

For "what should we do next," "is this complete," or "is this the right target" tasks, prompts should usually include:

- `docs/development_rules.md`
- `docs/Main.md`
- the canonical doc for the active workstream
- relevant closeout docs only if version guarantees or sequencing are part of the question

### First Post-Closeout Version Planning

For the first planning prompt after a version closes, prompts should usually include:

- `docs/development_rules.md`
- `docs/Main.md`
- `docs/codex_modes.md`
- the latest relevant closeout doc
- the latest relevant interim rebaseline doc if one exists for the active post-closeout branch
- the directly relevant canonical planning doc or docs for the next version lane

That first prompt should explicitly answer:

- what facts must be carried forward into the new version baseline
- what repeated prompt content can now be removed because the source-of-truth docs already capture it

### Governance / Prompt / Workflow Docs Work

For prompt-governance or workflow-governance tasks, prompts should usually include:

- `docs/development_rules.md`
- `docs/Main.md`
- `docs/codex_modes.md`
- `docs/jarvis_task_template.md`

Add other canonical docs only if the governance wording depends on them.

## When To Add Closeout Docs

Add closeout docs when the task:

- checks whether a closed version guarantee still holds
- sequences work immediately after a closeout
- audits whether a later change reopens a closed version’s behavior
- needs version-specific implementation facts that are not already captured elsewhere

Do not include all closeout docs by default if only one is relevant.

## When To Add Historical Or Archival Docs

Add historical or archival docs only when the task is explicitly about:

- tracing why a decision was made
- auditing a consolidation
- comparing current canon to earlier slice decisions
- resolving a real source-of-truth conflict

Historical or archival docs should normally be treated as supporting evidence, not current prompt baseline.

## Code Progression And Doc Sync Rule

Core code progression is prioritized.

That means:

- active code work should not be repeatedly interrupted by separate doc-only micro-passes unless a docs-first clarification is the safest boundary-setting move
- truth-doc updates may be bundled into the same approved code workstream when they directly support, record, or stabilize the active code task
- doc batching should stay minimal and relevant to the active workstream
- broader canonical sync should happen at meaningful milestones rather than after every tiny slice when that would create unnecessary prompt churn

This does not authorize unrelated doc rewrites.
It only allows directly supporting truth-doc maintenance to travel with the active workstream when safe and approved.

## Practical Prompt Rule

If you are writing a future Jarvis prompt and are unsure what to include:

1. include `development_rules.md`
2. include `Main.md`
3. include the directly relevant canonical doc or docs
4. include only the evidence inputs that matter
5. add closeout or historical docs only if the task truly depends on them

Shorter prompts are preferred when they still preserve the real source of truth.

For batched-workstream execution specifics, rely on `docs/codex_modes.md` rather than retyping the full rule set in every prompt unless the task needs a deliberate override.
