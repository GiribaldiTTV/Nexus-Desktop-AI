# Nexus Source-Of-Truth Index

## Purpose

This document is the routing authority for the merged Nexus Desktop AI canon.

Its job is to:

- define the current source-of-truth layers
- separate ownership between those layers
- point prompts and reviews toward the right authority docs
- prevent local branch overlays from being mistaken for merged truth

`Docs/Main.md` is a routing document.
It does not replace the authority of the docs it points to.

## Authoritative Baseline

Use these rules before trusting any planning or governance claim:

- `origin/main` is the authoritative baseline after merge and release
- the latest public tag or release is authoritative for released-version truth
- local unmerged branches, stashes, and docs overlays are reference material only until revalidated against updated `origin/main`
- if code, logs, and merged docs disagree, validate the live repo truth first and then repair the docs

## Layered Ownership Model

Use this ownership split unless a validated source conflict requires a temporary narrower override:

- backlog = identity and registry
- workstream docs = promoted-work feature-state, branch-local evidence, active seam references, artifact history, branch-local reuse notes, and closure history
- roadmap = sequencing and release posture
- rebaselines and closeouts = epoch or milestone summaries
- incident patterns = generalized reusable lessons
- bug tracking = backlog-first, with promoted bug docs only when warranted
- User Test Summary = validation-contract layer owned by the relevant workstream
- phase governance = repo-wide execution, proof, timeout, seam, stop-loss, validation-helper, and desktop UI audit contract
- branch authority records = repo-owned phase owners for approved non-backlog `docs/governance`, `emergency canon repair`, and `release packaging` branches
- `Docs/Main.md` = routing authority aligned to merged truth

## Analysis-First Prompt Baseline

For system analysis, post-release review, branch-start planning, or source-of-truth audit:

1. read `Docs/Main.md`
2. read `Docs/development_rules.md`
3. read `Docs/phase_governance.md`
4. read `Docs/codex_modes.md`
5. add the directly relevant authority docs for the task
6. add only the live repo evidence needed to validate current truth

Do not narrow the docs set before the system structure, drift, and authority boundaries are understood.

## Canonical Startup Contract

Before planning, patching, reviewing, or recommending the next move, Codex must follow this startup contract:

1. read `Docs/Main.md`
2. read `Docs/development_rules.md`
3. read `Docs/phase_governance.md`
4. read `Docs/codex_modes.md`
5. add the directly relevant authority docs for the task, including `Docs/feature_backlog.md` when the task maps to a tracked item
6. determine the tracked item's `Record State` when one exists
7. validate current branch truth and whether the branch is the correct execution base
8. if the item is `Promoted` or `Closed`, load the canonical workstream doc and treat it as the durable lane-specific execution and traceability record
9. if the task does not map to a promoted backlog workstream but does map to an approved non-backlog branch, load the relevant branch authority record under `Docs/branch_records/`
10. choose the reuse baseline in this order:
   - the relevant canonical workstream doc for branch-local traceability, artifact reuse, seam history, and "what worked" notes
   - the relevant branch authority record for approved non-backlog branch truth
   - `Docs/incident_patterns.md` only for generalized cross-branch lessons
11. state the next safe move before narrowing scope for execution

The startup assessment should make these items explicit:

- `Source-of-Truth`
- `Record State`
- `Branch Truth`
- `Canonical Workstream`
- `Reuse Baseline`
- `Next Safe Move`

If repo truth resolves to blocked `No Active Branch`, `Next Safe Move` must report the blocking repair path instead of inventing a later phase.
If repo truth resolves to steady-state `No Active Branch`, `Next Safe Move` may truthfully say that no branch should open yet or may name an explicitly approved non-implementation branch class whose admission rules pass.

## Routing Layers

### Governance And Prompting

Use these for workflow posture, prompt framing, lifecycle rules, and execution scaffolding:

- `Docs/development_rules.md`
- `Docs/phase_governance.md`
- `Docs/Main.md`
- `Docs/codex_modes.md`
- `Docs/orin_task_template.md`
- `Docs/codex_user_guide.md`

Repo-wide validation-helper rules also live in this governance layer.
Use `Docs/phase_governance.md` for the exact phase enum, blocker rules, branch classes, phase resolver, validation helper contract, proof hierarchy, default-budget closeout rule, and desktop UI audit rule instead of recreating those rules inside a workstream doc.

### Product And Boundary Truth

Use these for current product posture, architecture boundaries, and release-stage meaning:

- `Docs/architecture.md`
- `Docs/orin_vision.md`
- `Docs/orchestration.md`

These remain authoritative for their layer even where older naming or path references still need later normalization.
When a task depends on future post-Beta AI behavior, privacy posture, local-vs-external execution boundaries, or AI/UI identity, route to `Docs/orin_vision.md` rather than duplicating that intent in roadmap or workstream docs.

### Registry And Sequencing

Use these for tracked identity and near-term sequencing:

- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`

Rules:

- backlog owns identity
- roadmap owns sequencing and release posture
- neither backlog nor roadmap should retain the full execution story once a canonical workstream record exists

### Canonical Workstream Records

Use these for promoted work that needs a stable feature-state, branch-local validation/evidence record, active seam trail, durable artifact/reuse history, and closure history:

- `Docs/workstreams/index.md`
- `Docs/workstreams/FB-036_saved_action_authoring.md`
- `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md`
- `Docs/workstreams/FB-035_release_context_fallback_hardening.md`
- `Docs/workstreams/FB-034_recoverable_diagnostics.md`
- `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md`
- `Docs/workstreams/FB-033_startup_snapshot_harness_follow_through.md`
- `Docs/workstreams/FB-028_history_state_relocation.md`

### Branch Authority Records

Use these for approved branches that do not map to a promoted backlog workstream but still need a durable repo-owned phase authority record:

- `Docs/branch_records/index.md`
- the relevant active branch authority record under `Docs/branch_records/`

### Rebaselines And Closeouts

Use these for closeout policy, historical closeout lookup, and the modern Nexus-era baseline summary:

- `Docs/closeout_guidance.md`
- `Docs/closeout_index.md`
- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.3.1-prebeta.md`

Historical closeout leaf docs are intentionally routed through `Docs/closeout_index.md`.

### Incident Patterns

Use this layer for generalized debugging and validation lessons:

- `Docs/incident_patterns.md`

Keep branch-local "what worked" notes in the canonical workstream doc first.
Distill only generalized cross-branch lessons into `Docs/incident_patterns.md`.

### Validation Guidance

Use this when a task depends on manual validation handoff, User Test Summary structure, returned test-evidence digestion, implementation-output requirements for a `## User Test Summary` section, or the canonical repo-level `UTS` artifact for an active workstream:

- `Docs/user_test_summary_guidance.md`
- the relevant canonical workstream doc under `Docs/workstreams/`, which also owns the active lane's canonical repo-level `UTS` artifact and any durable artifact-history or artifact-reference section for branch-local validation/support assets when that workstream has created them
- `Docs/development_rules.md` when the task also depends on implementation-time validation depth, supporting validation artifacts, required evidence trails, hardening expectations, or the interactive OS-level continuation gate
- `Docs/phase_governance.md` when the task also depends on the repo-wide validation helper contract, marker-first proof hierarchy, gating-vs-non-gating observation rules, default-budget closeout expectations, or the desktop UI audit rule

### Auxiliary Planning References

Use these only when the task directly depends on their planning content:

- `Docs/boot_access_design.md`
- `Docs/orin_interaction_architecture.md`
- `Docs/workspace_layout_plan.md`
- `Docs/orin_display_naming_guidance.md`
- `Docs/ncp_hardening_assessment.md`
- `Docs/ownership_ip_plan.md`

These are reference layers, not active workstream or roadmap owners.

## Routing Rules

- route through the layer that owns the truth you need
- when work is phase-sensitive, route through `Docs/phase_governance.md` before choosing execution posture
- require the exact prompt contract from `Docs/phase_governance.md` before phase-sensitive execution
- prefer index docs for historical or high-cardinality layers
- do not treat a local-only document as canonical just because it exists in the workspace
- keep future post-Beta AI behavior, privacy, and execution intent in `Docs/orin_vision.md` until a later selected workstream turns part of it into execution truth
- do not create duplicate authority by making backlog, roadmap, and workstream docs all carry the same execution story
- do not treat workstream docs as the owner of repo-wide phase, timeout, stop-loss, proof-authority, validation-helper, or desktop UI audit rules; those belong to `Docs/phase_governance.md`
- keep historical Jarvis material preserved, but mark it as historical rather than current reality
- during the normal active-branch-first `pre-Beta` flow, do not default to a standalone docs-only canon lane when a plausible active implementation or release branch should carry the truth updates
- a planned standalone `docs/governance` branch is future-capable from `No Active Branch`, but only when the branch-class admission rules pass and the branch is genuinely governance, policy, docs, or triage work rather than delayed implementation follow-through
- the normal governed branch lifecycle is:
  1. `Branch Readiness`
  2. `Workstream`
  3. `Hardening`
  4. `Live Validation`
  5. `PR Readiness`
  6. `Release Readiness`
- `Post-Release Canon Repair` is not a normal phase; it is an emergency-only exception path after merged or released truth already exists
- before any next implementation branch may enter `Branch Readiness`, the repo-level admission gate from `Docs/phase_governance.md` must pass on updated `main`
- if repo truth resolves to blocked `No Active Branch`, report the blocking repair path
- if repo truth resolves to steady-state `No Active Branch`, do not invent a next implementation branch by inertia
- the normal `PR Readiness` sequence for a branch that changes release-facing canon is:
  1. validate current branch truth
  2. complete the merge-target canon updates on that same branch
  3. run the Governance Drift Audit
  4. if post-merge truth will admit a next branch, select the next workstream from current canon
  5. if post-merge truth will admit a next branch, confirm the next workstream has canon-valid record state
  6. if post-merge truth will admit a next branch, create the fresh successor branch
  7. if post-merge truth will admit a next branch, keep that successor branch reserved until it is revalidated after merge
  8. If post-merge truth will resolve to `No Active Branch` because `Release Debt` or another repo-level admission blocker remains open, successor-lane selection and reserved successor-branch creation are waived for that PR-readiness pass.
  9. when that waiver applies, record the blocked repo state explicitly
  10. only then allow the current branch to enter PR creation
- a standalone post-release canon repair is an emergency-only exception path when merged canon is already stale or when external drift made pre-merge prevention impossible
- returned `UTS`, screenshot, interactive, PR-review, or release-review evidence must be digested into the authority record before phase advancement is recommended
- when a slice changes user-visible behavior or another operator-facing path, do not treat `## User Test Summary` as a recap slot; route through `Docs/user_test_summary_guidance.md` and require a real manual checklist unless no meaningful manual test exists
- when an active desktop workstream has a canonical repo-level `UTS` artifact, do not stop at response text; update that workstream-owned artifact as well unless an explicit exception from `Docs/user_test_summary_guidance.md` applies
- for relevant desktop user-facing slices, also export or refresh `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` unless an explicit exception from `Docs/user_test_summary_guidance.md` applies
- do not confuse the canonical workstream-owned repo artifact with the required desktop convenience export or with response-level handoff text
- when a user-visible implementation slice is already validator-green, do not assume that alone is enough to continue; route through `Docs/development_rules.md` and require an explicit hardening or continuation judgment
- when a relevant desktop or runtime path can be launched and exercised through a real desktop session, do not treat validators, simulation, or synthetic/headless harnesses as sufficient for continuation on their own; require the smallest reliable validation infrastructure plus an evidence-backed interactive OS-level result before continuation
- if the real interactive desktop path is not feasible, require an explicit explanation of why, require the strongest available synthetic/headless evidence instead, and treat the continuation judgment as limited by that missing interactive layer
- keep validator results, synthetic/headless validation results, interactive OS-level execution results, simulated reasoning, and manual handoff as separate evidence layers rather than collapsing them into one summary
- when a pass opens programs, windows, dialogs, temporary documents, helper processes, probe files, or other session-scoped artifacts, route through `Docs/development_rules.md` and require cleanup plus explicit cleanup verification before handoff unless there is an explicit reason to preserve them
- when a task depends on interactive desktop validation, route through `Docs/development_rules.md` and require explicit time budgets, clean timeout abort behavior, cleanup, and last-progress reporting rather than relying on open-ended waits
- when closeout depends on interactive desktop validation, also route through `Docs/phase_governance.md` and require the helper's documented default budget profile to prove green before calling the branch truly green
- when a branch materially changes user-facing desktop UI, require the post-green live launched-process UI audit before treating closeout as complete; do not reinterpret that as a screenshot requirement for every seam iteration
- when the user also wants those audit screenshots to render inside the Codex client, use the screenshot-delivery guidance in `Docs/codex_user_guide.md`, which now defaults to small inline PNG preview images backed by preserved original files on disk, rather than assuming local-file image embeds will work

## Practical Prompt Rule

If you are unsure what to include in a future Nexus Desktop AI prompt:

1. start with `Docs/Main.md`
2. add `Docs/development_rules.md`
3. add `Docs/phase_governance.md`
4. add `Docs/codex_modes.md`
5. add the directly relevant authority docs for the active question
6. add live repo evidence only where the truth could have changed or drifted

Only after that full scan should scope be narrowed for execution.
