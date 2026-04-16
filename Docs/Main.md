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
- workstream docs = planning, execution, validation, and closure truth for promoted work
- roadmap = sequencing and release posture
- rebaselines and closeouts = epoch or milestone summaries
- incident patterns = generalized reusable lessons
- bug tracking = backlog-first, with promoted bug docs only when warranted
- User Test Summary = validation-contract layer owned by the relevant workstream
- phase governance = cross-workstream execution, closeout, and stop-loss contract
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

## Routing Layers

### Governance And Prompting

Use these for workflow posture, prompt framing, lifecycle rules, and execution scaffolding:

- `Docs/development_rules.md`
- `Docs/phase_governance.md`
- `Docs/Main.md`
- `Docs/codex_modes.md`
- `Docs/orin_task_template.md`
- `Docs/codex_user_guide.md`

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

Use these for promoted work that needs a stable planning, execution, validation, and closure record:

- `Docs/workstreams/index.md`
- `Docs/workstreams/FB-035_release_context_fallback_hardening.md`
- `Docs/workstreams/FB-034_recoverable_diagnostics.md`
- `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md`
- `Docs/workstreams/FB-033_startup_snapshot_harness_follow_through.md`
- `Docs/workstreams/FB-028_history_state_relocation.md`

### Rebaselines And Closeouts

Use these for closeout policy, historical closeout lookup, and the modern Nexus-era baseline summary:

- `Docs/closeout_guidance.md`
- `Docs/closeout_index.md`
- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.2.9-prebeta.md`

Historical closeout leaf docs are intentionally routed through `Docs/closeout_index.md`.

### Incident Patterns

Use this layer for generalized debugging and validation lessons:

- `Docs/incident_patterns.md`

### Validation Guidance

Use this when a task depends on manual validation handoff, User Test Summary structure, returned test-evidence digestion, implementation-output requirements for a `## User Test Summary` section, or the canonical repo-level `UTS` artifact for an active workstream:

- `Docs/user_test_summary_guidance.md`
- the relevant canonical workstream doc under `Docs/workstreams/`, which also owns the active lane's canonical repo-level `UTS` artifact and any durable artifact-history or artifact-reference section for branch-local validation/support assets when that workstream has created them
- `Docs/development_rules.md` when the task also depends on implementation-time validation depth, supporting validation artifacts, required evidence trails, hardening expectations, or the interactive OS-level continuation gate

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
- prefer index docs for historical or high-cardinality layers
- do not treat a local-only document as canonical just because it exists in the workspace
- keep future post-Beta AI behavior, privacy, and execution intent in `Docs/orin_vision.md` until a later selected workstream turns part of it into execution truth
- do not create duplicate authority by making backlog, roadmap, and workstream docs all carry the same execution story
- keep historical Jarvis material preserved, but mark it as historical rather than current reality
- after a release, do not default to a standalone docs-only canon lane when a plausible next workstream can be selected from updated `main`
- the normal post-release sequence is:
  1. validate live repo truth on updated `main`
  2. select the next workstream
  3. create a fresh compliant branch for that workstream
  4. perform required post-release canon sync at the start of that branch
  5. then continue lane work
- a standalone docs-only post-release repair is an explicit exception path only when no plausible next workstream can yet be selected safely
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

## Practical Prompt Rule

If you are unsure what to include in a future Nexus Desktop AI prompt:

1. start with `Docs/Main.md`
2. add `Docs/development_rules.md`
3. add `Docs/codex_modes.md` when collaboration posture matters
4. add the directly relevant authority docs for the active question
5. add live repo evidence only where the truth could have changed or drifted

Only after that full scan should scope be narrowed for execution.
