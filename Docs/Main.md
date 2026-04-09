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

Short prompts may still rely on this baseline.

If the user uses a brief cue rather than a full structured prompt, such as:

- `Analyze and Report`
- `Analyze for drift`
- `Analysis mode`
- `Workflow mode`
- `docs-only pass`
- `reference docs for the following`

Codex should treat that cue as shorthand, not as permission to skip the source-of-truth baseline.

Default shorthand behavior:

1. load `docs/development_rules.md`
2. load `docs/Main.md`
3. infer the directly relevant canonical doc or docs from the active branch, task wording, and current workstream
4. pull only the evidence inputs needed for that task
5. ask a clarifying question only if the task is still materially ambiguous after that baseline is applied

For the deeper Analysis mode workflow contract and when deep investigative analysis is required, use `docs/codex_modes.md`.

## Current Source-Of-Truth Structure

### Core Authoritative Docs

These are the default project-governance and product-boundary docs:

- `docs/development_rules.md`
- `docs/Main.md`
- `docs/architecture.md`
- `docs/orin_vision.md`
- `docs/orin_display_naming_guidance.md`
- `docs/feature_backlog.md`
- `docs/orchestration.md`
- `docs/codex_modes.md`
- `docs/orin_task_template.md`
- `docs/codex_user_guide.md`
- `docs/closeout_guidance.md`
- `docs/user_test_summary_guidance.md`

Within that core set:

- `docs/orin_vision.md` owns the product-wide meaning of `pre-Beta`, `Beta`, and `Full`
- `docs/orin_display_naming_guidance.md` owns the display-level ORIN / O.R.I.N. / full-expansion usage pattern
- `docs/feature_backlog.md` owns per-item or per-slice release-stage assignment

Use these when the task concerns:

- repo-wide rules
- architecture boundaries
- product direction
- backlog control
- orchestration ownership
- prompt or workflow governance, including batched-workstream execution rules
- grouped-workstream branch strategy and multi-developer workflow boundaries

### Canonical Workstream Docs

These are the current canonical planning docs for specific active planning areas:

- `docs/boot_access_design.md`
- `docs/ncp_hardening_assessment.md`
- `docs/orin_interaction_architecture.md`
- `docs/ownership_ip_plan.md`
- `docs/workspace_layout_plan.md`

Current canonical ownership:

- `boot_access_design.md` is the canonical boot-planning source
- `ncp_hardening_assessment.md` is the canonical typed-first NCP hardening reference for the now-closed FB-027 hardening follow-through
- `orin_interaction_architecture.md` is the canonical interaction-planning source
- `ownership_ip_plan.md` is the canonical ownership / licensing / IP-planning source
- `workspace_layout_plan.md` is the canonical workspace-planning source

Use these only when the task is directly about those workstreams.

### Historical / Optional Docs

These docs are still valid, but they are not part of the default prompt baseline for every task:

- `docs/closeouts/v1.6.0_closeout.md`
- `docs/closeouts/v1.7.0_closeout.md`
- `docs/closeouts/v1.8.0_closeout.md`
- `docs/closeouts/v1.9.0_closeout.md`
- `docs/closeouts/v2.0_closeout.md`
- `docs/closeouts/v2.2.0_closeout.md`
- `docs/closeouts/v2.2.1_closeout.md`
- `docs/closeout_index.md`

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

This same minimal baseline should also apply when the user gives only a short cue or shorthand prompt rather than a fully expanded task request.

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

Add `architecture.md`, `orin_vision.md`, `feature_backlog.md`, or `orchestration.md` when the task touches authority, vision, backlog scope, or launcher-owned desktop boundaries.

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

For merge-ready, PR-ready, release-ready, or version-bump review, also include:

- `docs/codex_modes.md`
- the relevant closeout or rebaseline docs when readiness depends on closed guarantees or milestone facts

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
- `docs/orin_task_template.md`
- `docs/codex_user_guide.md`
- `docs/closeout_guidance.md` when closeout policy, cadence, cleanup, or post-release baseline questions are in scope
- `docs/prebeta_roadmap.md` when current near-term sequencing, lane choice, or provisional version-impact questions are in scope
- `docs/user_test_summary_guidance.md`

Add other canonical docs only if the governance wording depends on them.

This governance lane includes:

- user-test-summary handling rules
- backlog-control rules
- batched-workstream execution rules
- grouped-workstream branch strategy for `pre-Beta`
- multi-developer workflow and GitHub/tooling governance boundaries
- shorthand prompt and default-baseline behavior
- human-operator shorthand guidance for reliable short prompts

For reusable human-facing prompt patterns and operator shorthand examples, use `docs/codex_user_guide.md`.

For current near-term roadmap, branch-sequencing, or provisional version-impact questions, use `docs/prebeta_roadmap.md`.
For grouped `pre-Beta` branch-sizing, minimum merge-ready threshold, or "should this lane stop now?" questions, use `docs/prebeta_roadmap.md` together with `docs/codex_modes.md`.
That roadmap remains subordinate to:

- `docs/orin_vision.md` for release-stage meaning
- `docs/closeout_guidance.md` for closeout and rebaseline cadence
- `docs/feature_backlog.md` for detailed backlog-item ownership

## When To Add Closeout Docs

Add closeout docs when the task:

- checks whether a closed version guarantee still holds
- sequences work immediately after a closeout
- audits whether a later change reopens a closed version’s behavior
- needs version-specific implementation facts that are not already captured elsewhere

Do not include all closeout docs by default if only one is relevant.

For closeout policy, cadence, cleanup, or drift questions, use `docs/closeout_guidance.md` alongside the relevant closeout doc or docs.

For historical closeout lookup and browsing, use `docs/closeout_index.md`.

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
