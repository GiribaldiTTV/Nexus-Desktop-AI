# Nexus Source-Of-Truth Index

## Top Rule: Pre-PR Durability

**DO THIS ALWAYS before `PR Readiness`: when a bounded phase pass or durability seam changes source, docs, canon, validator, helper registry, workstream authority, or branch-truth files and validation is green, Codex must commit and push those changes on the active branch instead of stopping at a copy-ready, staged-only, or uncommitted state. This includes `Branch Readiness`, `Workstream`, `Hardening`, and `Live Validation`; a prompt-level request not to commit is not enough to stop durability. The only exceptions are a documented `Durability Waiver`, failed validation, a legally file-frozen phase such as `Release Readiness`, or a named Codex self-imposed blocker; when that self-imposed blocker is lifted, Codex must automatically commit and push.**

**Release Readiness is file-frozen: block ANY source, docs, canon, validator, helper registry, release-note, or handoff-file changes discovered or needed during `Release Readiness`. Do not edit, stage, commit, or push in `Release Readiness`; route the change back to `PR Readiness` before merge, or to the next active `Branch Readiness` after merge.**

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

## Protected Main Law

`main` is a protected branch for Codex work.

Codex must not edit, stage, commit, generate, refresh, or directly repair repository files on `main`.
`main` may be read for truth validation, release review, merge verification, and post-release verification only.

There is no emergency direct-main repair path for Codex.
If drift is discovered:

- before merge, return to the owning branch and repair it before PR green
- after merge, repair on the still-available prior branch if that branch remains the legal repair surface
- if the prior branch is unavailable, block the next active branch in `Branch Readiness` and repair there before implementation

Any tracked file mutation while Codex is on `main` is a `Main Write Attempt` blocker.

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
- validation helper registry = repo-wide helper naming, ownership, reuse, workstream-scoped exception, and consolidation contract
- branch authority records = repo-owned phase owners for approved non-backlog `release packaging` branches and preserved historical `docs/governance` or `emergency canon repair` records; new fixes and repairs still use a new `feature/` branch by default
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

## ChatGPT Loader Contract

For prompt generation and new-chat bootstrapping, use `Docs/nexus_startup_contract.md` as the compact loader map.

That file is ChatGPT-facing and interface-only.
It helps generate complete prompts that load the correct source-of-truth without pasting the full governance stack.
Planning-loop blocking belongs in ChatGPT preflight analysis before prompt generation.
Once a prompt is allowed, it should stay thin, neutral, and repo-aligned instead of carrying behavior-management lists or protective governance narration.
It does not own Codex execution behavior, phase transitions, seam continuation, durability, validation, release rules, or branch authority.
Codex execution remains governed by the owning canon documents listed in this index, especially `Docs/development_rules.md`, `Docs/phase_governance.md`, `Docs/codex_modes.md`, and the active workstream or branch authority record.

If repo truth resolves to blocked `No Active Branch`, `Next Safe Move` must report the blocking repair path instead of inventing a later phase.
If repo truth resolves to steady-state `No Active Branch`, `Next Safe Move` may truthfully say that no branch should open yet or may name a release-packaging branch whose admission rules pass.
Governance-only branches are not used for new Nexus work.

## Routing Layers

### Governance And Prompting

Use these for workflow posture, prompt framing, lifecycle rules, and execution scaffolding:

- `Docs/nexus_startup_contract.md`
- `Docs/development_rules.md`
- `Docs/phase_governance.md`
- `Docs/Main.md`
- `Docs/codex_modes.md`
- `Docs/orin_task_template.md`
- `Docs/codex_user_guide.md`

Repo-wide validation-helper rules also live in this governance layer.
Use `Docs/nexus_startup_contract.md` as the compact ChatGPT/new-chat loader map only.
Do not treat it as execution authority.
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
- backlog candidate selection is priority-led; `Priority` and deferred-context fields are the selection inputs for open items
- `Target Version` is not an open-backlog selection input and belongs only to release posture, release debt, or historical closed/implemented evidence
- deferred open backlog entries must explain `Deferred Since:`, `Deferred Because:`, and `Selection / Unblock:` before they can be selected efficiently
- roadmap owns sequencing and release posture
- neither backlog nor roadmap should retain the full execution story once a canonical workstream record exists

### Canonical Workstream Records

Use these for promoted work that needs a stable feature-state, branch-local validation/evidence record, active seam trail, durable artifact/reuse history, and closure history:

- `Docs/workstreams/index.md`
- `Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md`
- `Docs/workstreams/FB-005_workspace_and_folder_organization.md`
- `Docs/workstreams/FB-042_desktop_entrypoint_runtime_refinement.md`
- `Docs/workstreams/FB-030_orin_voice_audio_direction_refinement.md`
- `Docs/workstreams/FB-029_orin_identity_licensing_hardening.md`
- `Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md`
- `Docs/workstreams/FB-004_future_boot_orchestrator_layer.md`
- `Docs/workstreams/FB-032_nexus_era_vision_and_source_of_truth_migration.md`
- `Docs/workstreams/FB-031_nexus_desktop_ai_ui_ux_overhaul_planning.md`
- `Docs/workstreams/FB-040_monitoring_thermals_performance_hud_surface.md`
- `Docs/workstreams/FB-039_external_trigger_plugin_integration_architecture.md`
- `Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md`
- `Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md`
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
- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.4.0-prebeta.md`

Historical closeout leaf docs are intentionally routed through `Docs/closeout_index.md`.

### Incident Patterns

Use this layer for generalized debugging and validation lessons:

- `Docs/incident_patterns.md`

Keep branch-local "what worked" notes in the canonical workstream doc first.
Distill only generalized cross-branch lessons into `Docs/incident_patterns.md`.

### Validation Guidance

Use this when a task depends on manual validation handoff, User Test Summary structure, returned test-evidence digestion, implementation-output requirements for a `## User Test Summary` section, or the canonical repo-level `UTS` artifact for an active workstream:

- `Docs/user_test_summary_guidance.md`
- `Docs/validation_helper_registry.md` when the task creates, extends, names, promotes, consolidates, or relies on a validation helper, live-validation script, audit helper, harness, or shared validation support under `dev/`
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
- during the normal active-branch-first `pre-Beta` flow, governance and canon updates should ride on the active current branch when they are directly required to keep that branch truthful, executable, phase-correct, readiness-correct, validation-correct, closeout-correct, or release-correct
- active-branch governance or canon updates must stay inside the current branch's approved phase, branch class, and scope; they must not weaken validation, stop conditions, phase authority, or become unrelated documentation churn
- do not open a standalone docs-only canon lane, governance-only branch, or between-branch repair window for routine canon completion
- if PR Readiness misses required canon, branch-authority cleanup, or post-merge truth work, the next active branch must treat that miss as a `Branch Readiness` blocker and repair it before implementation begins
- do not write directly to `main`; `main` is protected and any Codex file mutation there is a `Main Write Attempt`
- the normal governed branch lifecycle is:
  1. `Branch Readiness`
  2. `Workstream`
  3. `Hardening`
  4. `Live Validation`
  5. `PR Readiness`
  6. `Release Readiness`
- `Branch Readiness` must plan the whole branch at phase level before Workstream begins, including objective, target end-state, expected seam families and risk classes, validation contract, User Test Summary strategy, later-phase needs, and first seam or seam sequence
- Branch Readiness owns planning, framing, affected-surface mapping, implementation delta classification, and admitted-slice definition before Workstream begins.
- Branch Readiness must define the first admitted slice and the same-branch continuation posture for the remaining slices needed to complete the backlog item.
- during `Workstream`, `bounded multi-seam workflow` is the primary model for approved seam chains; execute one active seam at a time, validate it, record evidence, report `continue` or `stop`, and continue by default when `Next-Seam Continuation Required` applies
- Workstream must execute admitted implementation slices and keep same-branch backlog completion as the default unless the USER explicitly approves a docs-only bypass or backlog split.
- Docs-only Workstreams require explicit USER approval.
- Planning-loop bypass requires `Planning-Loop Bypass User Approval: APPROVED` and `Planning-Loop Bypass Reason:`.
- Release-bearing implementation work with no runtime/user-facing, backend/runtime, or developer-tooling delta is blocked unless the USER explicitly approves that release window.
- branch existence, branch rename, backlog promotion, repair-only traceability, or release-bearing posture do not count as Workstream progress by themselves
- when a prompt names an active seam inside an approved seam sequence, treat it as the entry seam, not a terminal boundary; a slice is a bounded admitted backlog-completion unit, while a seam is the current execution checkpoint inside or between slices
- there is no repo-wide cap on how many slices a branch or workstream may carry
- Same-branch backlog completion is the default: admit and execute the additional slices needed to finish the backlog item on the current branch whenever scope, phase, risk, and validation authority remain green.
- Perform all admitted seams in the bounded multi-seam workflow and continue through the additional slices needed to complete the backlog item on the same branch unless an explicit `Backlog-Split User Approval` or a named bounded stop condition is recorded.
- stopping after the first slice or splitting the backlog item across branches requires an explicit `Backlog-Split User Approval` or a named bounded stop condition
- reporting `Next Safe Move` is not a substitute for execution when continuation authority passes; A `continue` decision must be acted on immediately by starting the next seam in the approved sequence
- category labels such as bug fix, hotfix, high-risk, cross-subsystem, settings, protocol, launcher, or UI-model work require smaller seams and stronger gates; they are not automatic stop authority when the next seam remains admitted and green
- `Workstream` completion does not imply PR readiness; the normal next legal phase is `Hardening`, followed by `Live Validation` and then `PR Readiness`
- `Post-Release Canon Repair` is not a normal phase or branch; escaped canon repair must ride the prior legal branch or the next active branch's `Branch Readiness`, never direct `main`
- before any next implementation branch may enter `Branch Readiness`, the repo-level admission gate from `Docs/phase_governance.md` must pass on updated `main`
- if repo truth resolves to blocked `No Active Branch`, report the blocking repair path
- if repo truth resolves to steady-state `No Active Branch`, do not invent a next implementation branch by inertia
- governance-only branches are not used for new Nexus work; governance or canon repair rides on the active branch that owns the affected truth, or on the next active branch's `Branch Readiness` if a PR Readiness miss escaped the prior branch
- All fixes and repairs use a new `feature/` branch by default.
- Do not create a `docs/governance` or `emergency canon repair` branch unless explicit `Docs/Governance Branch Waiver: APPROVED` is recorded from the USER.
- Repair-only `feature/` branch existence does not imply Branch Readiness admission or active branch truth.
- Pre-PR Durability Rule: before `PR Readiness`, when a bounded phase pass or durability seam changes source, docs, canon, validator, helper registry, workstream authority, or branch-truth files and validation is green, Codex must commit and push those changes on the active branch instead of stopping at a copy-ready, staged-only, or uncommitted state
- the Pre-PR Durability Rule applies through `Branch Readiness`, `Workstream`, `Hardening`, and `Live Validation`; `PR Readiness` remains the later merge-target gate and must still prove clean durable branch truth
- prompt-level requests to stop before commit/push are not durability exceptions; only a documented `Durability Waiver`, failed validation, legally file-frozen `Release Readiness`, or a named Codex self-imposed blocker may stop commit/push, and self-imposed blockers must automatically commit and push once lifted
- the normal `PR Readiness` sequence for a branch that changes release-facing canon is:
  0. clear the hard PR Readiness blockers: `stale-canon`, `post-merge`, `dirty`, `docs-sync`, `next-workstream`, and `uts-results`
  1. validate current branch truth
  2. complete the merge-target canon updates on that same branch
  3. run the Governance Drift Audit
  4. clear the stale-canon blocker by proving current-state canon and merge-target canon reflect the branch's true state
  5. select the next workstream from current canon
  6. confirm the next workstream is recorded in backlog and roadmap
  7. confirm the next workstream has canon-valid record state and minimal scope
  8. confirm no branch exists yet for that next workstream
  9. defer successor branch creation to `Branch Readiness` after merge and updated-`main` revalidation
  10. encode the machine-checkable selected-next markers: `Next Workstream: Selected` and `Minimal Scope:` in backlog, plus `## Selected Next Workstream` with `Branch: Not created` in roadmap
  11. If post-merge truth will resolve to `No Active Branch` because `Release Debt` or another repo-level admission blocker remains open, successor branch creation remains deferred; next-workstream selection is still required unless the user explicitly approves a no-next-workstream steady-state outcome in canon.
  12. commit all required docs, canon, validator, and branch-truth changes so the worktree is clean and truth is durable in commit history
  13. run the normal branch governance validator and the PR-readiness gate mode
  14. report `PR package ready`, create the PR, and validate the live PR state before reporting `PR READY: YES`
  15. only after the PR exists, has no conflicts, has no unresolved Codex comments/issues, and matches merge-target canon may the branch report `PR Readiness GREEN`
- PR creation details must use the operator copy-block contract from `Docs/phase_governance.md`: separate copy-ready blocks for `PR Title`, `Base Branch`, `Head Branch`, and `PR Summary`; the summary reports included implementation and validation truth only
- PR Readiness also owns `PR Readiness Scope Missed`, `Between-Branch Canon Repair Attempt`, and `Next Branch Created Too Early`; none may be deferred into Release Readiness or a later side branch
- PR Readiness also owns `Release Window Audit Incomplete`; if the branch is inside an unreleased release window, it must audit the current blocker set and clear it on the same branch by default instead of knowingly teeing up another blocker-clearing PR before release
- the normal green posture for that audit is `Remaining Known Release Blockers: None`, `Another Pre-Release Repair PR Required: NO`, and `Release Window Split Waiver: None`; only an explicit user-approved `Release Window Split Waiver` may allow a deliberate split
- PR Readiness also owns `PR Creation Pending`, `PR Validation Pending`, and `PR State Unknown`; `PR package ready` is not `PR Readiness GREEN`
- PR Readiness also owns the merged-unreleased release-debt owner contract when a branch will merge unreleased implementation work; the merge-target canon must already contain `Merged-Unreleased Release-Debt Owner:`, `Repo State: No Active Branch`, `Release Target:`, `Release Floor:`, `Version Rationale:`, `Release Scope:`, `Release Artifacts:`, `Post-Release Truth:`, `Selected Next Workstream:`, and `Next-Branch Creation Gate:` before PR green
- PR Readiness must validate release target semantics from the latest public prerelease and declared `Release Floor:` before green; marker presence is insufficient if the version is wrong
- the normal `Release Readiness` sequence for a release-bearing branch must clear `Release Target Undefined` before reporting green:
  1. confirm whether the branch is release-bearing or explicitly non-release
  2. for release-bearing branches, require machine-checkable `Release Target:`, `Release Floor:`, `Version Rationale:`, `Release Scope:`, and `Release Artifacts:` markers before Release Readiness can report green
  3. for non-release branches, require `Release Branch: No`
  4. allow `Release Branch: No` only for preserved historical records
  5. never use the non-release waiver for `implementation` or `release packaging` branches
  6. never let the waiver clear `Release Debt`, weaken post-merge truth, weaken validation, or permit premature next-workstream branch creation
- Release Readiness is not a docs-sync phase and not a file-mutation phase; it is analysis-only for repository files and is restricted to release-target validation, release-scope validation, release-artifact validation, GitHub release package information, final release-execution authorization or confirmation, and release-state confirmation after release execution
- Release package details must use the operator copy-block contract from `Docs/phase_governance.md`: separate copy-ready blocks for `Release Title`, `Release Tag`, `Target Commit`, and `Release Notes`; release notes are detailed, user-facing, inclusion-only, Markdown-friendly, must not start with or repeat the release title as `# <release title>`, and must be combined with GitHub-generated `## What's Changed` plus the generated `**Full Changelog**:` compare link to the previous release during Release Execution
- Release Readiness must not edit, stage, commit, generate, or refresh source, docs, canon, validator, helper, release-note, or handoff files; if such work is discovered before merge, return to `PR Readiness`, and if discovered after merge, defer it to the next active branch's `Branch Readiness`
- tracked file changes while the authority record says `Release Readiness` are blocked as `Release Readiness File Mutation Attempt`
- a post-release canon repair must not mutate `main`; if merged canon is stale, carry the repair on the still-available prior branch or block the next active branch's `Branch Readiness`
- returned `UTS`, screenshot, interactive, PR-review, or release-review evidence must be digested into the authority record before phase advancement is recommended
- while a required User Test Summary handoff is outstanding, the active branch must report `User Test Summary Results Pending`; automated validators and live helper evidence may be green, but final phase advancement is blocked until the filled User Test Summary is submitted or waived, digested into the authority record, and blockers are reevaluated
- Live Validation green requires an exact `## User Test Summary` state before final green.
- required pending-UTS wording is: `Automated validators and live helper evidence: GREEN.`, `User Test Summary Results: PENDING.`, and `Final phase advancement is BLOCKED until the filled User Test Summary is submitted and digested.`
- when a slice changes user-visible behavior or another operator-facing path, do not treat `## User Test Summary` as a recap slot; route through `Docs/user_test_summary_guidance.md` and require a real manual checklist unless no meaningful manual test exists
- `## User Test Summary Strategy` is planning context only; the canonical repo-level `UTS` artifact must be the exact `## User Test Summary` section when one is required or waived
- when `User Test Summary Results: WAIVED` is used, the exact `## User Test Summary` section must also include `User Test Summary Waiver Reason:`
- when an active desktop workstream has a canonical repo-level `UTS` artifact, do not stop at response text; update that workstream-owned artifact as well unless an explicit exception from `Docs/user_test_summary_guidance.md` applies
- during bounded multi-seam Workstream execution, update the canonical workstream `UTS` incrementally as user-visible seams land, then refresh the desktop export when the Workstream seam chain is complete and the branch is user-facing
- for relevant desktop user-facing slices, also export or refresh `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` unless an explicit exception from `Docs/user_test_summary_guidance.md` applies
- do not confuse the canonical workstream-owned repo artifact with the required desktop convenience export or with response-level handoff text
- when a user-visible implementation slice is already validator-green, do not assume that alone is enough to continue; route through `Docs/development_rules.md` and require an explicit hardening or continuation judgment
- when a relevant desktop or runtime path can be launched and exercised through a real desktop session, do not treat validators, simulation, or synthetic/headless harnesses as sufficient for continuation on their own; require the smallest reliable validation infrastructure plus an evidence-backed interactive OS-level result before continuation
- when Live Validation concerns a relevant desktop user-facing workstream, route through `Docs/phase_governance.md` and require the `User-Facing Shortcut Live Validation Gate`; this is the canonical `desktop-shortcut` blocker path: the active authority record must declare `User-Facing Shortcut Path:` and `User-Facing Shortcut Validation:` before User Test Summary handoff, and final green is blocked by `User-Facing Shortcut Validation Pending` until the declared user-facing desktop shortcut or equivalent entrypoint is passable or explicitly waived with `User-Facing Shortcut Waiver Reason:`
- if the real interactive desktop path is not feasible, require an explicit explanation of why, require the strongest available synthetic/headless evidence instead, and treat the continuation judgment as limited by that missing interactive layer
- keep validator results, synthetic/headless validation results, interactive OS-level execution results, simulated reasoning, and manual handoff as separate evidence layers rather than collapsing them into one summary
- when a pass opens programs, windows, dialogs, temporary documents, helper processes, probe files, or other session-scoped artifacts, route through `Docs/development_rules.md` and require cleanup plus explicit cleanup verification before handoff unless there is an explicit reason to preserve them
- when a task depends on interactive desktop validation, route through `Docs/development_rules.md` and require explicit time budgets, clean timeout abort behavior, cleanup, and last-progress reporting rather than relying on open-ended waits
- when a task depends on Live Validation or another interactive desktop helper, route through `Docs/phase_governance.md` and require reuse-first selection from existing helpers before creating new scripts; temporary one-off probes must stay ignored, temporary, and non-closeout-grade unless promoted into documented reusable tooling
- when a task creates or keeps a durable root `dev/` validation helper, live-validation script, audit helper, harness, or shared helper, route through `Docs/validation_helper_registry.md` and require the standardized helper name, `Helper Status:`, owner, reuse decision, `Workstream-scoped` classification when applicable, `Consolidation Target`, and `Temporary probe` deletion or promotion handling
- when a live validation helper has no tighter watchdog, require a `10s` maximum no-progress supervisor with visible progress, clean abort, cleanup, and last confirmed progress reporting
- when closeout depends on interactive desktop validation, also route through `Docs/phase_governance.md` and require the helper's documented default budget profile to prove green before calling the branch truly green
- when a branch materially changes user-facing desktop UI, require the post-green live launched-process UI audit before treating closeout as complete; do not reinterpret that as a screenshot requirement for every seam iteration
- when the user also wants those audit screenshots to render inside the Codex client, use the screenshot-delivery guidance in `Docs/codex_user_guide.md`, which now defaults to small inline PNG preview images backed by preserved original files on disk, rather than assuming local-file image embeds will work

## Practical Prompt Rule

If you are unsure what to include in a future Nexus Desktop AI prompt:

1. start with `Docs/nexus_startup_contract.md`
2. treat it as a loader map, not execution authority
3. add `Docs/Main.md`
4. add `Docs/development_rules.md`
5. add `Docs/phase_governance.md`
6. add `Docs/codex_modes.md`
7. add the directly relevant authority docs for the active question
8. add live repo evidence only where the truth could have changed or drifted

Only after that full scan should scope be narrowed for execution.
