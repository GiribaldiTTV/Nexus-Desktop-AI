# Nexus Development Rules

## Top Rule: Pre-PR Durability

Follow `Docs/phase_governance.md#pre-pr-durability-rule`: local commit, push, PR, merge, release, publication, and live activation are separate explicitly authorized actions.

**Release Readiness is file-frozen: block ANY source, docs, canon, validator, helper registry, release-note, or handoff-file changes discovered or needed during `Release Readiness`. Do not edit, stage, commit, or push in `Release Readiness`; route the change back to `PR Readiness` before merge, or to the next active `Branch Readiness` after merge.**
**Release Readiness anchor and aggregation rules are owned by `Docs/phase_governance.md`. This file mirrors only the execution reminder: Release Readiness is file-frozen and must derive release-window truth from Git/GitHub/helpers instead of maintaining duplicate live state.**

## Core Principles

- Analyze first
- Validate live repo truth before making lane, branch, merge, or release recommendations
- One coherent approved change per revision
- Preserve architecture boundaries
- Logs, code, and merged docs are the source of truth for implemented behavior
- No silent scope expansion
- No silent backlog or policy drift
- Bounded State is mandatory before execution, and broad work language cannot widen scope without explicit USER waiver

## Analysis-First Operating Posture

Understand the affected behavior, dependencies, risks and current authority before execution. Carry accepted analysis and planning forward. Expand investigation when material evidence requires it; an ordinary focused defect does not automatically require another full-system audit. Current source reading is proportional to the operation.

## Mandatory Bounded Execution State

Before Codex mutates files, creates or switches branches/worktrees, commits, pushes, creates a PR, handles PR comments, performs release actions, launches runtime validation, mutates shortcuts, installs providers/models, or changes GitHub Desktop handoff state, it must prove a `Bounded State:`.

That bounded state must name the exact phase/stage, workspace, git root, branch, upstream, `HEAD`, `origin/main`, worktree role, write target, owning authority record, active package/slice/seam, allowed scope, affected surfaces, validation contract, non-includes, pending USER decisions, stop/report conditions, and next legal phase.

If Codex cannot prove that bounded state, it must stop on `Bounded State Missing` before mutation and report the exact missing field or USER decision needed.

Broad work requests do not authorize implementation. `Continue`, `complete all`, `all remaining work`, `finish the branch`, or similar wording may be used only when repo source truth resolves it to one exact active bounded seam. If it does not, Codex must stop on `Bounded State Missing` or `Next Bounded Workstream Seam Approval Missing`.

Widening beyond the current bounded state requires `Bounded State User Waiver: Granted` in the owning source truth or current USER approval. The waiver must name the branch/worktree, phase, slice/seam, relaxed bound, allowed extra seams/slices/files, expiration or stop condition, required validation, and still-pending USER decisions. Without that explicit waiver, stop on `Bounded State Waiver Missing`.

Clean validation, clean git state, branch existence, prior broad approval, prompt wording, Codex discretion, or ChatGPT review cannot infer a bounded-state waiver.

## Live-State Validation Gate

Before recommending the next move after a merge, release, or major lane transition, validate:

- current branch
- local `main` versus `origin/main`
- whether referenced PRs are actually merged
- whether referenced branches still exist
- latest public tag or release versus current `main`
- whether docs and canon reflect live repo truth

If prompt framing is stale, report the real state first and plan from that state.
If repo truth resolves to blocked `No Active Branch`, report the blocking repair path instead of inventing a later phase.
If repo truth resolves to steady-state `No Active Branch`, say so explicitly and do not invent a next implementation branch by inertia.

## Prompt-Entry Origin/Main Freshness Gate

Apply `Docs/phase_governance.md#prompt-entry-originmain-freshness-gate`: verify current main and exact carrier, then determine actual impact of advancement. Unrelated advancement does not veto the whole task. Baseline mutation retains separate explicit authority.

## Pre-Rebaseline Impact Audit

`Pre-Rebaseline Impact Audit` is required before any worktree, branch, neutral-main workspace, or standing governance lane baselines itself to a newer `origin/main` through fast-forward, merge, rebase, conflict resolution, branch switch, or current-main reconciliation.

No Baseline By Inertia: Codex must not run the baseline operation merely because the worktree is clean, behind, or expected to fast-forward. First report `Incoming Main Change Set:`, `Incoming Changed Files:`, `Current Worktree Changed Files:`, `Branch Changed Files:`, `Rebaseline Overlap Files:`, `Incoming Runtime / Source-Truth Risk:`, shared-surface/worktree overlap, `Validation Before Rebaseline:`, `Recommendation Only:`, `Rebaseline Mutation Approval:`, and `Rebaseline Mutation Status:`. The audit is report-only until USER approves the exact worktree, branch, target commit, and operation type.

If the incoming change set touches runtime/provider/UI/source-truth/validator files, if the current worktree is dirty, if validation fails, if sibling worktree overlap exists, or if `Rebaseline Overlap Files:` is not `None`, the correct next move is a reconciliation recommendation and USER decision, not automatic mutation. `Rebaseline Overlap Files:` means incoming changed files intersected with current branch/worktree changed files. Any non-empty intersection triggers `Rebaseline Overlap Intent Gate`: freeze mutation, inspect the active external branch plan's `Branch Change Intent Ledger`, classify each overlapping file through the `Rebaseline Overlap Failure Procedure`, and stop on `Rebaseline Overlap Intent Missing` when branch-owned intent evidence is missing, weak, stale, conflicting, or USER-dependent. After an approved baseline, run `Current-Main Reconciliation Identity Guard` before claiming the lane is safe.

## Multi-Worktree Automation Contract

Standing automation is not lane truth by itself. `Automation Observability` must treat Codex automation run/inbox rows and `$CODEX_HOME/automations/*/memory.md` as evidence inputs until the applicable external operational owner classifies a finding against directly verified identity/evidence as `BLOCKER_CANDIDATE` or `REVIEW_REQUIRED`.

Every active automation that can affect branch, PR, Release Readiness, post-merge, release-window, selected-next, toolchain, or branch governance truth must carry a configured cwd that resolves to a known worktree. The report must prove cwd, git root, worktree role, branch, `HEAD`, `origin/main`, and stale-neutral-main posture. `Automation CWD Worktree Mismatch` blocks the finding when the automation is pointed at stale `D:\Nexus Desktop AI\Product Repository`, a missing folder, a parked worktree, the wrong FAM lane, or a Governance worktree that is not the recorded lane. Operational Governance repair uses its explicitly approved external source carrier; product/interface repairs use their approved repository carrier. Historical RRI cycle, standing-intake and closeout exceptions do not select current authority.

## Governance Intake Triage And Digest Profiles

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

## Governance Efficiency Operating Model

Broad governance reform must also use `Docs/governance_efficiency_operating_model.md` before adding another live-state surface, policy mirror, helper family, release ownership rule, alias, or public-output rule. New durable governance rules should name a `Rule ID`, one `Owner File`, compact mirrors, validator/helper owner, and `Do Not Duplicate In:` boundary.

## Source-Of-Truth Ownership Model

Use this layered ownership model:

- backlog = identity and registry
- workstream docs = promoted-work feature-state, branch-local evidence, active seam references, artifact history, branch-local reuse notes, and closure history
- roadmap = stage-breakpoint schedule outline and broad milestone checkpoints, not a release ledger
- rebaselines and closeouts = epoch or milestone summaries
- incident patterns = generalized reusable lessons
- bugs = backlog-first, with promoted bug docs only when warranted
- User Test Summary = validation-contract layer owned by workstreams
- phase governance = repo-wide execution, exact phase enum, blockers, branch classes, proof, timeout, seam, stop-loss, validation-helper, Governance Drift Audit, phase resolver, and desktop UI audit contract
- validation helper registry = repo-wide helper naming, helper ownership, reuse-first inventory, workstream-scoped exception markers, and consolidation contract
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.
- Element Validation Ledger = row-level created/touched/affected/deferred/future element proof tracking owned by the existing workstream doc or branch authority record; use a companion file only when that owning record points to it canonically
- `Docs/nexus_startup_contract.md` = ChatGPT/new-chat loader map and prompt-generation guardrail owner, including the Nexus Prompt Gate final scrub rule when prompt generation, bootstrap continuity, or loader/source-truth drift review is in scope
- `Docs/Main.md` = routing authority aligned to merged truth
- active branch names must not use the `codex/` prefix; use `feature/` or another USER-approved non-`codex/` prefix, and treat historical `codex/` branch names as traceability only

Use `Docs/phase_governance.md` for:

- named execution phases
- blocker rules and branch classes
- phase entry and exit rules
- rollback and next-legal-phase rules
- proof authority rules
- interactive timeout governance
- validation helper rules
- desktop UI audit rules
- truth-drift enforcement
- governed closeout stop-loss rules

Use these lifecycle fields:

- `Status` = delivery or work state
- `Record State` = canonical-record lifecycle

Allowed `Record State` values are:

- `Registry-only`
- `Promoted`
- `Closed`

Rules:

- if `Record State` is not `Registry-only`, `Canonical Workstream Doc` must exist
- closed workstream docs stay at stable paths
- backlog and roadmap must not continue carrying the full execution story once a canonical workstream doc exists
- workstream docs must not silently redefine repo-wide phase or proof-governance rules that belong to `Docs/phase_governance.md`
- before adding a new governance/source-truth file, active artifact, ledger, registry, or durable authority surface, run the `Source-Truth Placement Preflight` from `Docs/phase_governance.md` and extend the existing owner first unless `No Existing Owner Fits` is recorded
- the active Element Validation Ledger belongs inside the canonical workstream doc for `Promoted` work or inside the branch authority record for `Registry-only` active branches; backlog, roadmap, family dossiers, validation helper registry, and Element Coverage must not become active ledger owners by inertia
- USER-facing interface elements, including previous implementations and future implementations, must record a Dev Toolkit Interface Review Mode disposition in the owning Element Validation Ledger: callable in dev-only review mode, deferred to a named repo-wide adoption branch/package, or not-applicable with reason. The review mode should expose element badges, hover highlighting, ledger ID/name tooltips, and screenshot-friendly annotations only in Dev Toolkit/dev mode; production UI must not expose element numbers.

Record-state meaning:

- `Registry-only` = backlog identity exists, but no canonical workstream execution record is required yet
- `Promoted` = a canonical workstream doc is required and becomes the durable branch record that must stay current throughout the active lane
- `Closed` = the canonical workstream doc remains historical lane truth and must not be treated as active execution authority by inertia

## Required Startup Loading

Before planning, patching, reviewing, or recommending the next move, Codex must load the canonical source-of-truth set.

`Docs/nexus_startup_contract.md` may be used as a compact ChatGPT/new-chat loader map, but it is not Codex execution authority.
Execution behavior is governed by this document, `Docs/Main.md`, `Docs/phase_governance.md`, `Docs/codex_modes.md`, the active workstream or branch authority record, and directly relevant owning canon.
Agent-generated prompts and summaries do not create authority. An explicit USER decision may approve an in-scope source reform and change its validation plan; reconcile that decision in the owning candidate source. Withheld push, phase entry, live mutation, deletion, publication, and release actions remain withheld.
Local ChatGPT custom instructions should stay compact while the repo loader/source-truth may preserve longer ChatGPT-facing continuity rules and review memory.
Do not paste the loader doc into Codex prompts; Codex prompts should load `Docs/Main.md` and the owning canon for execution authority.
Main is the first repo loader and routing index. After loading Main, follow its owner chain to phase governance, execution posture docs, Nexus Vision, family vision, applicable Family Feature Vision, active external branch plan, branch record, workstream record, helper registry, and any other directly relevant owner instead of inferring from prompt text or context docs alone.
Loader/source-truth continuity must preserve the broad FAM -> Package -> Slice -> Seam model, PR evidence-only handling, legacy global FB historical-only handling, single-slice/package-completion blockers, Element Coverage as non-identity, Branch/PR Readiness Stage 1 / Stage 2, next-branch hierarchy review, real-carrier repair routing, no direct-main repair, no standalone cleanup branch by default, FAM-006 Monitoring and HUD selected-next truth only after explicit USER approval while branch creation and runtime package admission remain separately blocked, separate release-execution approval, and the Windows-first, modular, GPU-aware direction with optional heavy local AI capability packs and CPU fallback.

PR Readiness Stage 1 is the Stage 2 readiness-lock gate. It must analyze release-debt impact, release-debt handling status, required current-branch source-truth sync, Stage 2 sync needs, PR title/base/head/summary, direct PR verification plan, watcher-exception posture, blockers, and USER decisions before Stage 2 can begin. Branch Readiness Stage 1 owns the normal next runtime implementation pipeline selection, rooted in Nexus Vision, family vision, branch vision, current completed work, and the next implementation need. PR Readiness does not require selected-next truth or a waiver by default; it validates selected-next truth only when USER explicitly approves PR-time selected-next sync or selected-next truth already exists and would merge as durable repo truth. Stage 1 remains active until one outcome is recorded: `Stage 1 Ready For Stage 2`, `PR Readiness Stage 1 Repair Required`, `Current-Branch Branch Readiness Re-entry Required`, `New Carrier Branch Required`, or `Stage 1 USER Waiver Required`. Bounded Stage 1 repair/sync may mutate durable source truth only when the current branch is the legal carrier and the USER-approved current phase/seam authorizes that repair. Stage 2 begins only after `Stage 1 Ready For Stage 2` plus explicit USER approval, and Stage 2 owns final PR execution only: final PR package sync, commit/push if needed, PR creation, direct PR verification, bot-review handling, mergeability validation, and direct merge/close verification. Stage 2 PR creation must create or leave the live PR ready-for-review, never draft; tool defaults to draft are superseded by Nexus governance and `Draft PR Created In PR2` blocks green until converted on the same PR. Recurring PR watcher automation is denied by default unless USER separately approves a named watcher exception for the exact PR. Stage 2 response-level stopping follows the Direct PR2 Continuation Rule: do not end the Codex turn on an eyes-only/no-response current-head bot wait while GitHub is reachable and direct polling can continue; keep polling/repairing until merge-ready/merged/closed state, an actionable repair/blocker, a true direct-verification blocker, tool/context exhaustion, or explicit USER stop/pause.

PR Readiness Stage 1 must also run an `Origin/Main Freshness Check` before Stage 2. It records `Branch Creation Base:`, `Current origin/main:`, `Origin/Main Advanced Since Branch Creation:`, `Origin/Main Changed Files:`, `Branch Changed Files:`, `Reconciliation Required:`, `Reconciliation File List:`, `Reconciliation Recommendation:`, and `Reconciliation Mutation Status:`. If `origin/main` advanced and branch/current-main files or source-truth owners need review, Stage 1 stops on `Origin Main Reconciliation Packet Required`, outputs the complete reconciliation data and recommendation, and performs no file fixes during Stage 1.

Before a merge, rebase, fast-forward, or branch switch performs the reconciliation, Codex must also run `Pre-Rebaseline Impact Audit`. That audit is the mutation-level gate and must record `Incoming Main Change Set:`, `Incoming Changed Files:`, `Current Worktree Changed Files:`, `Branch Changed Files:`, `Rebaseline Overlap Files:`, `Incoming Runtime / Source-Truth Risk:`, `Validation Before Rebaseline:`, `Recommendation Only:`, `Rebaseline Mutation Approval:`, and `Rebaseline Mutation Status:` before any local branch state changes. Non-empty `Rebaseline Overlap Files:` invokes `Rebaseline Overlap Intent Gate`; mutation remains blocked until `Overall Overlap Gate Result:` is not blocked and the USER approves the exact operation.

Current-main reconciliation in a multi-worktree branch must also pass the `Current-Main Reconciliation Identity Guard`. origin/main is context, not identity: after any merge, rebase, fast-forward, or conflict resolution, the assigned worktree must reassert `Assigned Worktree Branch Identity:`, `Branch-Local Authority Reassertion:`, `Incoming Main Active-Branch Blocks Accepted: NO`, and `Sibling Worktree Identity Preservation:` before validation or commit. Do not accept incoming current-workstream, selected-next, or active-branch blocks wholesale when they belong to another worktree; preserve them as merged-main context, then make `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and the active branch record point back to the assigned branch and authority record. If this is not true, stop on `Worktree Branch Identity Drift`.

PR Readiness must prove post-merge source truth before PR creation or merge readiness through the `Release Readiness Health Pass`. Apply `Docs/phase_governance.md#release-readiness-health-pass` during Stage 1, after any Stage 2 or bot-review source-truth repair, and before merge approval when its inputs changed. The pass requires the authority record to carry `Post-Merge Branch Authority Projection:`, `Stale Active Branch Wording Scan:`, `Stale PR Creation / PR Readiness Pending Wording Scan:`, `Merged-Unreleased Scope Posture:`, `Release Execution Gate:`, `Watcher / Live PR State Projection:`, `Branch Cleanup Plan:`, `Branch Cleanup Execution Gate:`, `FAM Overlap Routing:`, `Release Candidate Anchor Projection:`, `Release Window Contributor Inventory:`, `Governance Intake Routing:`, and `Projected Post-Merge Validation:` so Release Readiness validates instead of repairing stale merged-main truth. A separate post-merge projection receipt does not clear the pass while the same branch remains listed under `Active Branch Authority Records`; that shape blocks on `Merge-Stable Projection Shadowed By Active Authority`. PR Readiness Stage 1 must also execute the actual branch-authority fold-down when the health pass or `Post-Merge State` projects `historical/no-active`, `must not remain active branch authority`, or `historical merged-unreleased` posture; projection-only text while the actual record remains active blocks on `PR Readiness Stage 1 branch-authority fold-down required` before Stage 2, PR green, or merge approval. If Release Readiness still discovers stale active branch authority, stale phase wording, stale PR Readiness wording, selected-next ambiguity, release-window contributor ambiguity, or `No Active Branch` conflict after merge, the output digest must say `Governance Intake Routing: use the explicitly approved external operational Governance source carrier` and must include the originating worktree, branch, PR, merge commit, blockers, and next legal phase.

`Branch Cleanup Plan:` records stale/old branches, retired worktrees, and stale GitHub Desktop entries that may need cleanup after merge. `Branch Cleanup Execution Gate:` must keep cleanup blocked during Release Readiness; stale/old branch cleanup executes only during the next `Branch Readiness Stage 2 - Execution Gate` that creates or validates the replacement branch/worktree. Before deleting any branch or removing any worktree, Codex must prove `git worktree list`, current branch targets, and GitHub Desktop binding so no GitHub Desktop-bound worktree is left without a valid branch target. `Stable Worktree Path Preservation Gate:` is required when the target is a family-stable or GitHub Desktop-bound folder path; Codex must record `Stable Worktree Path:`, `Replacement Binding Path:`, and the preservation method, and must stop on `Stable Worktree Path At Risk` if cleanup would remove the stable path before the successor branch/worktree is moved, switched, or explicitly rebound there.

Assigned Worktree Confinement is mandatory for every thread assigned to a specific worktree. Before mutation, Stage 2 execution, commit, push, PR work, release work, runtime validation, shortcut/provider/model action, branch/worktree cleanup, or GitHub Desktop handoff, report `Active Thread Owner:`, `Thread Assignment Status:`, `Worktree Ownership Ledger:`, `Intended Write Set:`, `Same Worktree / Same Branch Collision Check:`, `Dirty Worktree Collision Check:`, `Dirty Worktree Recovery Packet:`, `Off-Worktree Work Routing:`, `Governance Routing Barrier:`, `New Worktree Decision Gate:`, `Expected Worktree Root:`, `Actual Worktree Root:`, `No Cross-Worktree Mutation:`, and the `GitHub Desktop-bound worktree`. If the active root is not the assigned root, stop on `Worktree Escape User Waiver Missing`; if another active thread owns the same worktree or branch, stop on `Parallel Worktree Coordination Missing`; if the target worktree is dirty and ownership is unclear, stop for a `Dirty Worktree Recovery Packet`. If the requested work belongs outside the assigned worktree, outside the active branch scope, or to another active lane, stop on `Governance Routing Barrier` and route the packet to the approved external Governance owner; that owner decides whether an existing owner, new worktree/thread, or USER waiver is required. The assigned thread must not mutate sibling worktrees, parked clones, or the neutral/main folder by convenience unless the USER grants `Worktree Escape User Waiver: Granted` with expected root, actual root, target root, allowed commands/files, expiration or stop condition, required validation, and return path.

Prompt-Ingress Lane Lock is part of Assigned Worktree Confinement. Before following an attached prompt, pasted prompt, referenced file, generated prompt, automation/heartbeat instruction, or ChatGPT review prompt that names a worktree, family, branch, repository path, packet path, or USER hub label, Codex must classify the requested lane and compare it to the current assigned thread/worktree binding. If the prompt target is a different family/worktree/branch, stop on `Prompt-Ingress Lane Mismatch` before changing directories, loading sibling source truth for execution, running sibling helpers, generating packets, mutating external state, or executing commands in the sibling lane. The only pre-routing actions are identity proof in the currently assigned worktree and a routing packet unless USER grants an explicit lane-switch/worktree-escape decision naming target root, branch, command/file scope, read/write mode, expiration or stop condition, validation, and return path.

That startup pass must make explicit:

- source-of-truth layer selection
- `Record State` when the task maps to a tracked item
- current branch truth and whether the branch is the correct execution base
- the canonical workstream doc when one exists
- the reuse baseline
- the next safe move

## Exact Prompt Contract And Phase Resolver

Every phase-sensitive execution prompt must include:

- `Mode`
- `Phase`
- `Workstream`
- `Branch`

Add these when relevant:

- `Branch Class`
- `Active Seam`
- `Validation Contract`
- `Timeout Contract`

If `Phase` is missing or is not one of the exact canonical phase names from `Docs/phase_governance.md`, execution is blocked and only truth-validation or analysis may continue.

Before answering â€œwhat phase are we in?â€ or â€œwhatâ€™s next?â€, run the phase resolver from `Docs/phase_governance.md` and return:

- `Current Phase`
- `Phase Status`
- `Branch Class`
- `Blockers`
- `Governance Drift Found`
- `Next Legal Phase`
- `Plan To Reach That Phase`

For governed execution output, also return:

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

## Branch And Lane Governance

PR-readiness is not the default checkpoint after a clean slice.

Default checkpoint:

- branch-level lane evaluation

Branch Readiness must establish the branch-level execution plan before Workstream begins.
That plan must name the branch objective, target end-state, expected seam families and risk classes, validation contract, User Test Summary strategy, later-phase needs, and the first Branch Planning target. Branch Readiness does not directly approve Workstream implementation.
Branch Readiness owns planning, framing, affected-surface mapping, implementation delta classification, admitted-slice definition, and whole-backlog closure strategy before Workstream begins.
Branch Readiness is organized inside the same canonical phase as `Branch Readiness Stage 1 - Analysis Gate` followed by `Branch Readiness Stage 2 - Execution Gate`.
Stage 1 is analysis-only and outputs `## Branch Readiness Stage 1 Analysis Packet`; it allows no repository file mutation, branch creation, package admission, docs sync, PR work, release work, selected-next truth, or canon edits.
The Branch Readiness Stage 1 packet must include governed state markers, FAM/package candidate, package-size review, multiple admitted-slice plan, single-slice drift check, Element Coverage review, product vision, project-wide vision alignment, branch-specific vision alignment, USER vision questions, `USER Vision Question Packet`, Codex product interpretation, Codex implementation recommendation, Codex additional recommendations, USER/ChatGPT review checkpoint, USER critique loop, USER decision ledger, full feature element breakdown, system concept model, entity/profile model, user workflow model, scale/data-volume model, configuration/state model, whole-system interaction map, minimum viable vs full-system boundary, current branch vs future package boundaries, affected surfaces, branch reach, why the branch is large enough, why it should not split into tiny branches, expected user-facing outcomes, acceptance criteria, screenshot and User Test Summary proof expectations, implementation sequence proposal, rejected shallow plan, alternatives/tradeoffs, open USER decision points, deferred ideas/future-package ledger, validation plan, `Stale Branch Cleanup Plan:`, expected docs sync, blockers and waivers, rollback path, `Branch Readiness Planning Incomplete` blocker review, `Next Legal Phase:` digest field, and the exact Stage 2 green-light decision needed.
The Branch Readiness Stage 1 packet must also include `BR1 Candidate Viability / Grouping Matrix` before recommending USER-selectable candidates. Each option must prove a concrete feature outcome, implementation-bearing route class, behavior-change classification, support/infrastructure relationship, Family Feature Vision context or not-applicable reason, Deferred Feature Carryforward consumption, grouping recommendation, split reason when not grouped, expected Slice/SLC/seam map, proof path, largest safe coherent package explanation, tiny-branch sprawl review, blockers, and exact USER decision needed. If the options are planning-only, readiness-only, support-only, manifest-only, registry-only, setup-only, proof-only, or split into tiny branches without a split reason, Stage 1 stays blocked on the appropriate BR1 candidate blocker and must revise the options before Stage 2.
Runtime-focused Branch Readiness Stage 1 must also include `## Runtime Branch Engineering Contract` so the branch cannot proceed from broad seam labels into underspecified implementation. Required markers are `USER Engineering Planning Review:`, `Runtime Implementation Approval:`, `Current Runtime Baseline:`, `Planned Runtime Delta:`, `User-Facing Runtime Delta:`, `State / Config / Schema Delta:`, `Validator / Helper Delta:`, `Expected Changed Files / Surfaces:`, `Approval-Boundary Audit:`, `Future-Gated Items:`, `Workstream Seam Map:`, `Proof Expectations:`, `Risk Forecast:`, `Recommendations And Alternatives:`, `Plan Version / Revision Status:`, and `Plan-To-Implementation Traceability:`. Stage 1 may mark the contract `Proposed` and implementation approval `Pending`; Stage 2 must admit or revise the exact branch purpose, Workstream label, first runtime delta, pending USER decisions, setup list, and contract status before Branch Planning can begin. New or re-entering runtime-focused branches must create or admit an active Branch Runtime Engineering Plan at `D:\Nexus Desktop AI\Governance State\branches\<branch_slug>\branch_plan.md`, link it from the branch authority record with `Branch Runtime Engineering Plan Path:`, carry `Engineering Plan Status:`, keep backlog and roadmap compact pointer/status surfaces, and keep `PR Fold-Down Packet:` pending until PR Readiness compares the branch against the active external plan. Before asking USER to green-light implementation, Branch Planning must deliver one primary current-gate decision and the required branch vision, active external branch plan or historical repo receipt, branch authority, relevant Nexus/family vision, matrix, UFD/change-intent and source-truth context through the current external USER lifecycle owner, routed by `Docs/governance_efficiency_operating_model.md#user-review-hub-rule` to the approved workstream collection. BP1 must return the `USER Branch Vision Review Gate` packet. BP2 must return the `USER Branch Plan Review Gate` packet. BP3 must return Workstream Entry / Orchestration Validation proving the accepted Branch Plan implements the accepted Branch Vision and preserving all pending action gates. `USER_BRANCH_VISION_REVIEW.md` and `USER_BRANCH_PLAN_REVIEW.md` are required USER-facing Branch Planning artifacts before bounded Workstream implementation when applicable; USER response must be attached or inserted and then digested by Codex, or an explicit USER waiver must be recorded. Missing proof blocks on `BP1 Branch Vision Review Missing`, `BP2 Branch Plan Review Missing`, or `BP3 Orchestration Validation Missing`; stale packet metadata blocks on `USER Review Packet Stale`; and an omitted digest blocks on `USER Review Packet Not Digested`. Runtime BP3 with multiple admitted slices or seams must also perform whole-package analysis before entry-seam implementation and stop on `Workstream Entry Whole-Package Analysis Missing` if that proof is absent. Workstream entry, each seam start packet, seam closeout, Workstream Green, Hardening, Live Validation, PR Readiness, and Release Readiness must compare actual runtime behavior, changed files, UI copy, state/config/schema changes, validator/helper proof, future-gated items, and public release language against the admitted contract and active external Branch Runtime Engineering Plan. If repo truth proves the contract or plan is too narrow, stale, or wrong, Codex must stop on a plan revision packet instead of improvising runtime behavior.

Runtime/backend-affecting implementation must also consume the Backend Predictability / Reliability Contract from `Docs/phase_governance.md` when it creates, changes, proves, or exposes backend behavior, state, config, schema, persistence, provider/model/cache/private behavior, failure handling, recovery, or UI-visible runtime status. Implementation must preserve deterministic inputs and outputs, named state ownership, lifecycle/state-machine behavior, failure/fallback/recovery routes, config/schema compatibility, rollback/reversibility, and frontend/backend truth mapping. A UI-visible green, disabled, blocked, degraded, recovered, success, or failure state is invalid unless it maps to runtime truth, policy truth, or a USER-approved exception. When rebaseline or re-entry finds violations in already-implemented or previous branch output outside the current branch's legal repair scope, Codex may prepare a GitHub issue candidate for USER review, but must not create or mutate the issue without exact USER approval.
Branch Planning packet proof must also be decision-path consistent before implementation can be approved. The packet is incomplete when the selected primary review, navigation, or applicable supporting artifacts (including `USER_REVIEW_FOLDER_AND_FILE_DIGEST.md`, `WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md`, and `BRANCH_VISION_VALIDATION_CHECKLIST.md` when present) disagree about the exact USER decision or next legal phase. Branch Planning packets must report `Packet Reviewability State:` separately from `USER Gate State:` so helper PASS, validator PASS, zip freshness, file-count proof, or `Reviewable` status cannot become USER acceptance, USER waiver, BP3 approval, or implementation authority. Active branch identity, HEAD, baseline, current PR state, and validation log proof belong in helper output, validator output, Codex chat digest, or external operational state rather than as the content focus of USER-facing files. A packet that still says repair/revalidation or implementation-blocked is a valid blocking review artifact only; it cannot be treated as implementation approval through chat-only explanation.
Current review freshness is checked against the exact pending subject, selected evidence and actual upload through the current external USER lifecycle owner, routed by `Docs/governance_efficiency_operating_model.md#user-review-hub-rule`. The installed owner governs collection selection, paths, ZIP safety/parity and retirement; `dev/orin_user_review_bundle.py` remains legacy operational reference and retained pure public test support, not an executable package-generation owner. Repository review checks still require the applicable `USER_BRANCH_VISION_REVIEW.md` / `USER_BRANCH_PLAN_REVIEW.md`, one primary current-gate decision, a truthful packet finding, readable decision content, and absence of unresolved placeholders or stale-stage claims. Missing required review content, a stale subject or a failed selected-evidence delivery check blocks on `USER Review Packet Stale`. Retained collection evidence is not cleared or made a package prerequisite merely because it exists.

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Stay inside the active grouped lane until one of these is true:

- the milestone threshold is satisfied
- a real blocker appears
- the next work crosses subsystem boundaries
- the user explicitly stops

After a lane is closed or merged:

- the next implementation workstream must execute from updated `main` on a fresh branch
- the next workstream must be selected, canon-defined, minimally scoped, and explicitly not branched during `PR Readiness`
- the successor branch is created only during `Branch Readiness` after the current branch merges and updated `main` is revalidated

If a branch becomes:

- stale
- merged
- identical to `main`

Codex must call that out explicitly and recommend a fresh branch from updated `main`.

Before any next implementation branch may enter `Branch Readiness`, the repo-level admission gate from `Docs/phase_governance.md` must pass.

If the admission gate fails:

- repo state becomes `No Active Branch`
- no next implementation branch may begin
- the next safe move is blocker repair, not next-lane execution

Release-packaging branches may still begin from `No Active Branch` only when their branch-class admission rules from `Docs/phase_governance.md` pass and their branch authority record is explicit.
Protected main remains read-only: do not edit, stage, commit, generate, refresh, or directly repair files there.

Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.

Product PR-owned defects must be repaired on their legal product carrier before claiming its acceptance. An escaped defect blocks only an operation it materially affects; unrelated Governance or historical cleanup debt is not imported into a runtime branch.

Preserve existing USER changes, historical receipts, approved product scope, product tests, and phase protections. Add or update a test for a distinct material failure, not by default after every wording repair.

Merge-stable repository pointers must not mirror transient task ownership. Current phase, write owner, locks, and selected-next state remain external.

Backlog identity is USER-gated:

- Codex must not create, split, promote, or select a new backlog identity without explicit USER approval.
- Backlog items are major user-facing feature-family or major release/support lanes, not small single-seam runtime proofs, governance repairs, validation follow-through, hotfixes, or blocker-clearing repair traces.
- If Codex believes a backlog identity, package admission, branch creation, backlog split, promotion, selected-next successor, or single-slice package waiver is needed but approval is absent, stop on `Backlog Addition User Approval Missing` and output every FAM that is still not closed plus every package or slice that is not complete, including ID, title, Status, Record State, Priority, package state, slice state, and available selection/deferred/minimal-scope fields.
- If that still-not-closed FAM and not-complete package/slice list is empty, stop on `Backlog Exhaustion User Decision Pending` and wait for USER direction.
- Small runtime follow-through inside an existing family is family evidence or aggregation material by default; it must not become a standalone release-version driver without explicit USER approval.

Pre-PR Durability Rule:

Follow `Docs/phase_governance.md#pre-pr-durability-rule`: local commit, push, PR, merge, release, publication, and live activation are separate explicitly authorized actions.
PR Readiness still checks the approved product branch's durable truth before PR creation.


For promoted, `Registry-only` and approved non-backlog work alike, the matching external operational record exclusively owns live `Current Phase`, `Phase Status`, current blockers, task/write owner, branch/worktree assignment, locks/leases and next operational action.

Repository phase, workstream and branch owners retain canonical phase names, branch-class meaning, product entry/exit requirements, acceptance/proof contracts, `Entry Basis`, `Exit Criteria`, `Rollback Target` requirements and durable accepted milestone or historical/fold-down receipts. Named phase fields in those records are product contracts or explicitly identified historical/accepted snapshots, not a second live current value.

Resolve current phase through `Docs/phase_governance.md#single-phase-authority-rule` and its phase resolver. Missing current authority blocks execution; do not manufacture a repository live-state record to fill the gap.

## Canon Freshness Rules

Supporting canon must stay aligned with live truth.

That means:

Planning and proof apply to the actual approved objective. One coherent deliverable is valid; actual new scope, ownership, safety, phase and human-result decisions remain governed by `Docs/phase_governance.md`.

Thread / Worktree Identity Preflight:

- before `Branch Readiness Stage 2`, `Workstream`, `Hardening`, `Live Validation`, `PR Readiness`, `Release Readiness`, branch creation, worktree creation, commit, push, PR creation, release action, meaningful repo work, file mutation, or GitHub Desktop handoff, Codex must verify the current working directory, git repository root, branch, upstream, `HEAD`, `origin/main`, `git worktree list`, clean/dirty state, intended local workspace role, expected phase/seam, and intended write target
- local workspace roles are `Main/consolidator`, `active branch worktree`, `parked fallback`, `historical/lab context`, `private/dev workspace`, or `artifact output root`
- `D:\Nexus Desktop AI\Product Repository` is the local main/consolidator workspace by default after workspace reconsolidation; tracked file edits on `main` remain blocked, and it becomes an active branch workspace only when the active branch record and Thread / Worktree Identity Preflight assign it
- `D:\Nexus Desktop AI\Worktrees\` is the governed local root for active branch worktrees after workspace reconsolidation; retired worktrees there are not active carriers unless a current branch record names them
- `D:\Nexus Repos\Nexus Desktop AI Main` and `D:\Nexus Worktrees\` are retained fallback/historical workspace paths unless later USER-approved governance or identity preflight assigns them a current role; `D:\Nexus Dev ORIN\` and `D:\Nexus Artifacts\` remain private/dev or artifact roots whose contents are evidence only until legally imported
- `codex/ai-llm-lab` is historical AI Lab planning traceability only; after USER-approved consolidation into the current feature branch it has no active local/remote branch ref and must not be recreated or reused as a governance carrier, runtime carrier, or FAM-007 implementation carrier without USER-approved repo governance
- assigned parallel worktrees are allowed when USER explicitly assigns separate Codex threads to separate active branch worktrees; each assigned thread must record its expected path, branch, upstream, `HEAD`, `origin/main`, source-truth owner, write target, active thread owner, thread assignment status, worktree ownership ledger, intended write set, same-worktree/same-branch collision check, dirty-worktree collision check, dirty-worktree recovery packet posture, and worktree role before mutation
- the default repo-wide limit is two active assigned branch worktrees; a third active branch worktree or any same-file, same-source-truth-owner, same-worktree, same-branch, dirty-worktree ownership, unknown active-thread owner, or missing worktree ownership ledger overlap between active worktrees requires a USER decision before continued mutation
- Codex App thread assignment may be enforced by a USER-local hook, but the current external Control Plane owns operational hook policy; repository files retain interfaces only. A thread assigned to one Git root may perform read-only sibling-worktree analysis, but it must not edit, stage, commit, push, reset, clean, branch-switch, generate packets, write external state, or run write-capable helpers in another worktree without a `Worktree Escape User Waiver: Granted`. Branch switching or creation inside the assigned root is allowed only when the normal phase, branch authority, and USER decision gates permit it. Live hook configuration, per-thread lock files, waiver files, and hook audit logs belong under USER-local Codex state such as `C:\Users\anden\.codex`, not repo docs.
- an assigned thread may have no created branch yet when it is intentionally waiting in Release Readiness analysis, Branch Readiness Stage 1 analysis, or updated-main wait posture for another branch to merge; this is `Waiting For Updated Main`, not an active branch worktree, and it must remain file-freeze/read-only until updated `origin/main` is fetched, source truth is revalidated, and USER approves any later branch creation or mutation
- multi-worktree branch health markers are: clean/dirty state, ahead/behind state, merge-base freshness, current `origin/main`, upstream reachability, merge forecast, open PR state, branch retirement/cleanup expectation, and whether the branch has source truth projected to merge-stable posture
- multi-worktree file health markers are: changed-file list, intended write set, shared-file overlap with the other active worktree, generated/log artifacts, validator/helper files, source-truth files, line-ending warnings, and unresolved conflict risk
- future FAM-007 worktrees must branch from updated `origin/main`, not from the parked AI lab branch
- before interactive desktop validation, Codex must confirm no Nexus/Python runtime from another worktree is active; only one interactive desktop validation may run at a time
- across related Nexus worktrees, use one Git operation at a time where practical, and run source-truth freshness checks before phase transitions
- before PR creation, run changed-file overlap review and merge/conflict forecasting against `origin/main`
- before USER-driven GitHub Desktop operations, confirm GitHub Desktop is bound to the intended local repository folder
- Historical standing-intake Desktop bindings do not select the current repair carrier. Before USER-driven Desktop operations, verify the explicitly approved assigned worktree so it is not confused with FAM-006, FAM-007, or canonical main.
- if the active folder, branch, upstream, workspace role, expected phase/seam, write target, runtime/process owner, or GitHub Desktop binding does not match the requested work, stop on `Thread / Worktree Identity Mismatch` and report expected workspace, actual workspace, expected branch, actual branch, expected write target, actual write target, expected thread/workstream role, actual repo state, mismatch evidence, and the safest next correction
- `Thread Launch / Write-Target Identity Lock` is the permanent pre-mutation gate for Nexus work: a stale parked branch, AI Lab context, old worktree, fallback folder, wrong GitHub Desktop repository, wrong write target, or unknown lane identity requires a routing packet and blocks source edits, branch/worktree creation, commits, pushes, PR work, release work, shortcut mutation, provider/model installation, and runtime validation until corrected
- dirty worktree collision recovery is freeze-first: when a target worktree has uncommitted tracked changes before a new thread claims it, do not clean, stash, reset, overwrite, commit, or continue by inference. Inventory dirty files, identify the owning thread per file, preserve or discard only with USER approval, then resume with one active owner and a validated `Worktree Ownership Ledger`.

Local docs overlays are reference material only until revalidated against updated `origin/main`.

Time-sensitive current-state claims must live only in designated current-state owners, or be part of the merge-target canon update set.

Allowed current-state owners are:

- backlog
- roadmap
- active workstream doc
- workstreams index
- closeout index
- current rebaseline or closeout file
- `Docs/Main.md` routing

Auxiliary guidance docs should be timeless by default.
If they carry live-current claims, they must either be updated as part of canon sync or stop owning current-state truth.

## Governance Drift Rule

If a branch exposes a governance weakness such as:

- a missing blocker
- a weak phase entry or exit rule
- a weak source-of-truth ownership rule
- stale prompt scaffolding or stale examples
- a missing validator requirement

that weakness must be classified as `Governance Drift`.

If governance drift is discovered:

- stop normal progression immediately
- if the drift is directly coupled to the active branch's truth, phase, readiness, validation, closeout, or release state, fix it on that active branch after the boundary is explicit
- otherwise, produce the exact required canon delta and wait for user confirmation
- if the same drift class could recur, the repair must also harden the canon or validator rule that allowed it instead of only patching the one stale surface
- every repeated or carried blocker must include a recurrence analysis before green: what failed, why current governance/validation missed it, what prevents the same failure next time, and whether canon or validator coverage must change

Do not defer known governance weaknesses silently to a later branch.

When a branch changes:

- repo-wide phase governance
- current-state owners
- prompt scaffolds
- active promoted workstream phase-state records

it must also run:

- `python dev/orin_branch_governance_validation.py`

and keep that validator green before calling the branch ready.

## Change Discipline

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Bounded multi-seam workflow means:

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Stop the workflow immediately if validation fails, regression appears, scope drifts, risk class changes, governance drift appears, manual validation becomes blocking, or branch truth no longer matches the authority record.

Do not use category labels as stop authority.
Bug fixes, hotfixes, unclear seams, high-risk seams, cross-subsystem changes, settings, protocol, launcher-policy, and UI-model work require the smallest safe seam, stronger validation, and an explicit continuation check.
They do not require stopping after a green seam when the current slice still needs another validation-backed seam inside the same bounded workflow.
Legacy `Single-Seam Fallback` and `Single-Seam Mode Waiver` wording is retired and must not be used in active source-of-truth.
Stopping after the first slice or splitting the backlog item across branches requires an explicit `Backlog-Split User Approval` or a named bounded stop condition.
If no explicit approval is raised and no bounded stop condition is recorded, keep later slices on the same branch by default and advance into them automatically while `Completion Status` remains `In Progress`.

Use the smallest safe slice for:

- architecture clarification
- boundary-setting
- high-risk behavior or policy work

Use the smallest coherent slice for:

- lower-risk follow-through inside an already-approved milestone when a smaller fragment would leave the milestone incomplete

These are execution rules, not analysis-stop rules.

## Testing And Validation

Every revision must include:

- healthy-path verification
- failure or edge-case verification when relevant
- runtime log review
- crash log review when present
- artifact cleanup verification when relevant
- session cleanup verification when relevant

Interactive validation must also be time-budgeted.
Codex must not allow stalled validation runs, harnesses, or desktop exercises to sit indefinitely.

When the branch is in governed closeout recovery, `Docs/phase_governance.md` is the controlling timeout and stop-loss authority unless the active workstream doc explicitly documents a tighter contract.

Interactive validation is reuse-first.
Before creating a new live-validation helper, Codex must inspect the existing repo helper surface and use, parameterize, extend, or extract shared support from existing helpers when that is safe.
Temporary one-off probes may be used only under ignored evidence roots, may not become closeout-grade proof by inertia, and must be deleted after the pass unless deliberately promoted into documented reusable tooling.

Validation helper naming and ownership are registry-governed.
Before adding or keeping a durable root `dev/` validation helper, live-validation script, audit helper, harness, or shared helper module, Codex must route through `Docs/validation_helper_registry.md`.
That registry defines the allowed `Helper Status:` values, naming scheme, owner rules, `Workstream-scoped` exception markers, `Temporary probe` handling, and `Consolidation Target` requirements.
New feature work must extend an existing helper family whenever that is safe; creating a new helper is allowed only after registry lookup proves reuse would contaminate proof ownership, blur branch truth, or make validation less reliable.
Workstream-scoped helpers must be registered before closeout-grade proof can depend on them and must carry a promotion or consolidation decision before PR Readiness.

When an interactive validation pass is relevant, it must use:

- a full-run hard timeout
- a no-progress watchdog timeout
- scenario and/or transition budgets where the flow has distinct multi-step seams
- an outer execution timeout that sits only slightly above the interactive harness hard cap rather than extending it by many additional minutes

For meaningful interactive desktop closeout work, helpers should also follow the repo-wide validation helper contract from `Docs/phase_governance.md`.
That means:

- marker-first proof by default
- explicit separation of gating and non-gating observations
- runtime helper support when it materially improves deterministic startup or runtime logging
- watchdog enforcement plus last-progress logging
- cleanup guarantees
- saved-state or source snapshots when write safety or no-write blocking behavior matters
- live re-resolution of windows, dialogs, overlays, and controls across close/open seams
- seam classification before product code is changed during validation hardening

If no tighter helper-specific watchdog is active, `10s` without meaningful progress is the maximum allowed no-progress interval for live validation.
Meaningful progress means a new runtime marker, step-log entry, scenario transition, UI readback, screenshot/proof artifact, process-state observation, cleanup confirmation, or explicit last-progress update.
If that interval is exceeded, Codex must abort the run, clean up session state, report the last confirmed progress point, and classify the stall before patching anything.

When the approved boundary is a continuous `Hardening` pass on the current branch, Codex should keep iterating through seams without waiting for a new user prompt after every rerun unless:

- a blocker appears
- truth drift appears
- stop-loss is reached
- canon sync becomes required before the next rerun

Do not claim closeout-grade green status from a helper profile that only passed under one-off command-line overrides.
The helper's documented default profile must itself prove green before that branch can be treated as truly green.

If a timeout or freeze is detected, Codex must:

- abort cleanly rather than letting the run continue indefinitely
- perform the required session cleanup
- explicitly report the timeout or stall condition
- explicitly report the last confirmed meaningful progress point
- route helper or harness repair back through `Hardening` unless the authority record explicitly allows validation-only support edits in the current phase

For hardened desktop helpers, the working target is not just eventual completion.
The working target is also responsiveness:

- no-progress or transition waits should normally stay within `3s`
- normal seam or scenario completion should normally stay within `60s`
- if a helper keeps needing longer waits, patch the proof path or helper design rather than silently normalizing the delay

If the timeout contract in the active workstream doc and the live harness behavior drift apart, the workflow is blocked until that drift is reconciled in canon before continued execution is recommended.

After any validation run, test pass, runtime exercise, harness execution, or other operational step, Codex must also clean up what it created or opened during that session unless there is a deliberate reason to preserve it.

This is not satisfied by a best-effort attempt alone. Before handoff, Codex must explicitly verify that the cleanup actually happened for the apps, windows, dialogs, helper processes, temporary files, probe documents, and other session-scoped artifacts it opened, started, or created during the pass.

That includes, when relevant:

- closing programs, dialogs, or windows Codex opened
- stopping helper processes, harnesses, validators, or temporary runtimes Codex started
- deleting temporary files, temporary documents, scratch outputs, or probe files Codex created only for the pass
- restoring source files, settings, or local state Codex intentionally modified for the test
- confirming the machine or workspace is not left in a noisier or more invasive state than necessary for the user
- verifying that user-visible apps or windows opened for the pass, such as Notepad or File Explorer windows, are actually closed rather than assumed closed

If something created during the pass must remain on disk or stay open intentionally, Codex must say so explicitly and explain why it was preserved.

Before handing a user-visible runtime, UI, or manual validation path back to the user, Codex must run that same path or the closest faithful equivalent when feasible.

For relevant desktop, runtime, user-facing, or operator-facing slices, if the implemented path can be launched and exercised through a real desktop session in the current environment, true interactive OS-level validation is the default continuation gate.

In that case:

- validator results remain baseline automated proof
- synthetic or headless harnesses remain stronger supporting proof
- a real interactive OS-level session is the required gate before Codex recommends normal continuation
- manual user handoff remains an additional operator layer, not a substitute for Codex's own feasible interactive validation

If Codex cannot self-run the same path reliably, it must say so explicitly and identify the remaining validation gap.

When a slice materially changes user-facing desktop UI, Codex must also plan a post-green live launched-process UI audit before closeout.
That audit is a closeout-quality check, not a screenshot requirement for every seam iteration.

When the approved issue itself is visual or layout-specific, marker proof and
functional click-path proof are not enough. The H1/live validation path must
include a check that would fail the reported visible defect, such as measured
geometry, overlap/gutter assertions, screenshot audit evidence, or another
durable visual proof tied to the exact user concern. If returned USER media
contradicts the active-client result, treat the active-client result as
insufficient proof, reopen the branch to Hardening, and patch validation before
claiming PR readiness.

For runtime, UI, startup, prompt, voice, or other operator-facing implementation slices, green validators are necessary but not sufficient on their own.

Before continuing to the next implementation slice on the same branch, Codex must also perform a deeper branch-local validation and hardening pass that:

- pressure-tests the implemented path and its likely failure modes
- checks integration seams and branch-local regressions beyond the happy path
- adds or creates the smallest reliable validation infrastructure on-branch when the current suite leaves meaningful blind spots
- uses supporting validation artifacts when needed, such as validators, harnesses, fixtures, scripted helpers, trace capture, screenshots, runtime logs, or reproducible sample inputs
- uses synthetic or headless validators and harnesses as supporting evidence rather than the final continuation gate when a real desktop session is feasible
- launches and exercises the real desktop or runtime path through an interactive OS-level session when feasible rather than stopping at simulated reasoning or headless proof
- preserves evidence of what was run, what passed or failed, and where the supporting artifacts live
- explicitly distinguishes:
  - validator results
  - synthetic or headless validation results
  - simulated reasoning or inspection findings
  - interactive OS-level execution results
  - manual user-test handoff that still remains
- explicitly decides whether the correct next move is:
  - continue implementation
  - pause for internal hardening or validation
  - or fix a specific defect first

Validator-green status plus simulated reasoning, recap-style summary, or synthetic/headless harness results is not enough when the implemented desktop or runtime path can be exercised through a real interactive OS-level session.

When Codex recommends continuing implementation after a user-visible slice, it must be able to explain why the current validation and hardening depth is already sufficient for that continuation.

If the current validation surface is too thin to support that explanation, Codex must first add the smallest reliable validation infrastructure on-branch and re-run the validation pass before continuing.

If a real interactive OS-level session is not feasible, Codex must say so explicitly, explain why, cite the strongest available non-interactive evidence, and state that the continuation recommendation is limited by the missing interactive gate.

When a slice changes user-visible behavior, runtime interaction, UX flow, prompts, startup behavior, voice behavior, or any manual operator-facing path, Codex must include a true manual validation checklist under `## User Test Summary` by default.

That checklist must include:

- setup or prerequisites
- exact user actions
- expected visible behavior
- failure signs to watch for
- branch-specific or slice-specific validation focus

A recap-style summary is not sufficient when manual validation is relevant.

If no meaningful manual test exists for the change, Codex must say so explicitly under `## User Test Summary` and explain why manual validation is not materially relevant for that slice.
`## User Test Summary Strategy` is planning context only; it does not satisfy the canonical repo-level `## User Test Summary` artifact.

For active desktop workstreams, the default canonical repo-level UTS planning surface is the User Test Summary strategy in the relevant canonical workstream doc unless that doc explicitly declares a different repo path. The formal exact `## User Test Summary` returned-results artifact belongs to Live Validation Stage 1 only.
User Test Summary is exclusive to Live Validation Stage 1.
Live Validation Stage 1 cannot enter Stage 2 until User Test Summary results are `PASS` or `WAIVED`, Codex has digested the result into source truth, and blockers have been reevaluated.
PR Readiness may verify the previously digested Live Validation UTS state, but it must not create, refresh, or digest UTS as its own phase artifact.

When that strategy exists and supporting docs are in scope on the active branch, Codex must update it as part of the same slice by default.

For bounded multi-seam Workstream execution, User Test Summary strategy handling is incremental plus final Live Validation preparation:

- update the canonical workstream User Test Summary strategy as user-visible or operator-facing seams land
- when the Workstream seam chain is complete, preserve the handoff needs for later Live Validation Stage 1; do not create/refresh the formal desktop UTS export and do not use returned UTS results as a Workstream stop condition
- before User Test Summary handoff in Live Validation, run the `User-Facing Shortcut Live Validation Gate` for relevant desktop user-facing workstreams and record `User-Facing Shortcut Path:` plus `User-Facing Shortcut Validation: PENDING`, `PASS`, `FAIL`, or `WAIVED`
- before User Test Summary handoff in Live Validation, run the `Codex Live Client Self-QA Gate` for relevant desktop user-facing workstreams and record `Codex Live Client Self-QA:`, `Visual Quality:`, `Live Interaction Evidence:`, `Usability Check:`, and `Platform Uniformity Check:`
- before User Test Summary handoff in desktop UI Live Validation, run `Codex Visual Adjudication:` and record artifact-by-artifact PASS / REPAIR / STOP / WAIVED_WITH_REASON verdicts against the Product Definition Plan, Runtime Branch Engineering Contract, latest USER vision, and package UI/UX intent
- before User Test Summary handoff in desktop UI Live Validation, prove the per-element visual inventory, issue-form coverage matrix, USER-inspectable OneDrive focused screenshot folder, and every named focused screenshot path; missing inventory rows, missing issue coverage, missing element-labeled filenames, broad desktop-only proof, or `dev\logs`-only images are `REPAIR`
- if the relevant desktop UI is interactive, exercise the same live-client interactions Codex would ask the USER to test and record the evidence before handoff
- when a user-facing control changes another visible state, Live Validation must prove both the action and every expected visible effect through photo/video evidence captured from a visible user-level desktop-control path; visible user-simulated mouse/keyboard input may perform the action, but hidden activation calls, direct function/signal invocation, button existence, code paths, marker output, scripted click output, callback state, or accidental unrelated-app interaction cannot prove the action by themselves
- when target selection is uncertain, Codex must run a deterministic visible-target acquisition loop instead of asking the USER to operate the UI by default: identify candidates from the visible screen, test only user-equivalent input paths with bounded side effects, verify the visible result, and preserve the calibration/evidence path; USER coordinate help is an exception for the current environment, not the normal Live Validation route
- if the relevant desktop UI has hover, dropdown, scroll, resize, flicker, clipping, dirty-guard, confirmation, click-routing, or transient state behavior, LV1 must capture both focused screenshots and short video or ordered frame-sequence proof for those states before exporting the UTS; missing video/frame proof is a `REPAIR` result, not a waiverable Codex shortcut
- before exporting or refreshing a desktop UI UTS handoff, Codex must clear every unwaived Codex-visible `REPAIR` or `STOP` finding from the visual adjudication record, per-element inventory, issue-form matrix, interaction proof, and shortcut/human-client evidence; the UTS handoff is for USER acceptance, not for discovering defects Codex could already see
- when Live Validation discovers a current-branch UI/UX/interaction defect and approval covers bounded continuation, Codex must use the bounded repair/rerun loop: record the defect, repair it, rerun focused proof and required validators, update source truth, and then rerun Live Validation before returning to UTS; when approval does not cover the repair, return `BLOCKED` or `REPAIR` with exact approval needed instead of handing off a known-bad UTS
- digest returned user evidence in `Live Validation Stage 1` before recommending Stage 2 advancement
- route returned evidence back to `Workstream` for in-scope user-facing branch work, to `Hardening` for defects or validation gaps, or to backlog/defer handling for new feature requests

If required user-facing desktop shortcut evidence is outstanding, the active authority record must carry the hard blocker `User-Facing Shortcut Validation Pending`.

The shortcut blocker lifts only after `User-Facing Shortcut Validation: PASS` is recorded with evidence from the declared shortcut path, or `User-Facing Shortcut Validation: WAIVED` is recorded with `User-Facing Shortcut Waiver Reason:` proving the branch is not desktop/user-facing or the shortcut path is explicitly unavailable.
If `User-Facing Shortcut Validation: FAIL`, keep an explicit blocker and route back to `Workstream` or `Hardening` instead of exporting the branch as final-green.

If required Codex live-client self-QA is outstanding, the active authority record must carry the hard blocker `Codex Live Client Self-QA Pending`.
The self-QA blocker lifts only after `Codex Live Client Self-QA: PASS` is recorded with evidence from the launched client path, including `Live Interaction Evidence:` for interactive UI, or `Codex Live Client Self-QA: WAIVED` is recorded with `Codex Live Client Self-QA Waiver Reason:` proving the branch is not user-facing or the live client path is unavailable.
If `Codex Live Client Self-QA: FAIL`, keep an explicit blocker and route back to `Workstream` or `Hardening` before USER handoff.

If a required User Test Summary handoff is outstanding in Live Validation or PR Readiness, the active authority record must carry the hard blocker `User Test Summary Results Pending`.
Live Validation green requires an exact `## User Test Summary` state before final green.
Every Live Validation digest must include an exact `## User Test Summary` section; if User Test Summary is waived, the digest must still include `User Test Summary Results: WAIVED` and `User Test Summary Waiver Reason:`.
Workstream must not list `User Test Summary Results Pending` as the reason to stop implementation; it must continue implementation, internal sandbox validation, or named Workstream repair while current-branch product work remains.

Expected reporting model:

- Automated validators and live helper evidence: GREEN.
- User Test Summary Results: PENDING.
- Final phase advancement is BLOCKED until the filled User Test Summary is submitted and digested.

The blocker lifts only after the filled User Test Summary is submitted or a documented waiver exists, the returned results or waiver are digested into the active authority record, and blockers are reevaluated.
When a waiver is used, the active authority record must include `User Test Summary Results: WAIVED` and `User Test Summary Waiver Reason:` inside the exact `## User Test Summary` section.

Completing a User Test Summary update does not move the branch directly from `Workstream` to `PR Readiness`.
The normal next phase after Workstream completion remains `Hardening`.

Response-only `## User Test Summary` output does not satisfy the workstream-owned validation layer when the canonical repo artifact remains stale.

For desktop user-facing slices, Codex must also export or refresh the convenience copy at:

- `User Test Summary.txt` within the approved collection and evidence set selected by the external USER lifecycle owner

unless it explicitly explains why the desktop export is not relevant or is being intentionally skipped.

The ownership hierarchy is:

- workstream doc exact `## User Test Summary` section = canonical repo source of truth
- local USER hub `User Test Summary.txt` = required user-facing exported copy when relevant
- response-level `## User Test Summary` = current handoff text only

If Codex does not update the canonical repo-level `UTS` artifact, it must say explicitly why. Valid reasons are limited to:

- no meaningful manual test exists for the slice
- no canonical workstream doc exists yet for the active lane
- the user explicitly restricted the pass so the relevant artifact could not be updated
- the relevant closed workstream doc already says that no separate ongoing `UTS` artifact remains

If Codex does not export or refresh the local USER hub `User Test Summary.txt` copy for a relevant desktop slice, it must also say explicitly why.

Returned evidence such as `UTS`, screenshots, interactive reports, PR review comments, or release-review findings may satisfy exit criteria, but they must never auto-advance phase by implication.

Required sequence:

1. digest the evidence
2. update the authority record
3. reevaluate blockers
4. only then advance phase

## Runtime Evidence And Logging

- logs are source-truth evidence for internal runtime behavior, diagnosis, state transitions, and consistency checks; they are not by themselves visible USER acceptance proof
- do not assume behavior without log or code evidence
- prefer structured markers over raw output
- visible USER-facing proof is not complete from logs or markers alone; formal Live Validation must include photo/video or ordered frame-sequence evidence for visible claims
- if a required acceptance claim cannot be proven in photo/video, elevate it to USER manual validation, explicit USER waiver, or a named blocker instead of treating helper output as proof
- formal desktop Live Validation must use the exact normal USER desktop runtime launcher path declared for the branch; direct runtime, helper, WebView, sandbox/offscreen, generated-shortcut, troubleshooting-launcher-without-parity, or diagnostic launches are supporting evidence unless USER explicitly waives the launcher requirement
- troubleshooting-mode logging is opt-in, USER-consented, local by default, privacy-safe/redacted where needed, and distinct from normal runtime logging
- troubleshooting runtime launcher evidence can substitute for normal launcher proof only when USER consent and launcher parity proof show that troubleshooting differences are diagnostic-only and irrelevant to the validated claim
- preserve or cite the exact validator outputs, helper scripts or harnesses used, runtime logs reviewed, and any created fixtures, traces, or screenshots that materially support a continuation recommendation
- when interactive OS-level validation is required and feasible, preserve or cite the exact session evidence that shows the real path was exercised, such as runtime logs, screenshots, structured markers, traces, or durable validation reports
- when meaningful desktop UI changed and a live launched-process UI audit was required, preserve or cite the audit manifest and the key captured windows as part of the final closeout evidence
- when desktop Live Validation depends on visual proof, capture the full virtual desktop by default for window-position frame of reference, copy the raw PNG into `C:\Users\anden\OneDrive\Pictures\Screenshots\<project-or-validation-lane>\<timestamp>\` or the active USER-declared screenshots folder, and surface that raw path in the Codex handoff/chat for USER inspection
- when the user wants to visually validate those screenshots inside the Codex client, do not rely on local-file image embeds as the default delivery path; keep the original audit captures on disk and use the client-compatible preview path documented in `Docs/codex_user_guide.md`
- the default client-compatible preview path is: preserve the original live capture on disk, generate a smaller derivative from that real file, and send one small inline PNG `data:` image at a time until render reliability is confirmed
- do not claim live-style validation without evidence or a specific explanation of what path was actually exercised

### Root Logs Governance

- the runtime root's ignored `logs/` directory and `logs/crash` child remain reserved for approved live launcher and runtime truth surfaces only
- launcher-owned historical state is not a root-owned live logs surface
- normal runtime historical state resolves under `%LOCALAPPDATA%/Nexus Desktop AI/state/nexus_history_v1.jsonl`
- dev, test, worker, and toolkit evidence must write under the runtime root's ignored `dev/logs/<lane>/...` evidence lanes
- no new dev or worker evidence roots may be introduced under the runtime root's live `logs/` directory without explicit approval
- historical `C:/Nexus/...` wording in older records does not override current root-relative launcher code truth

### Dev-Only Startup Snapshot Harness

For startup-state debugging, Codex may use the env-gated startup snapshot harness when it is the smallest reliable evidence path.

Rules:

- the harness must remain opt-in through `NEXUS_HARNESS_STARTUP_SNAPSHOT_DIR`
- snapshot output must write to an explicitly chosen dev evidence path, not root logs
- the harness is internal debugging infrastructure only
- if the harness is not needed for the active task, leave it disabled

## Historical Intelligence Rules

Cross-run intelligence must stay contract-defined in repo docs before implementation changes begin.

That contract must define:

- schema and versioning
- run identity
- failure fingerprint rules
- provenance labeling
- retention and reset behavior
- corruption and fallback behavior

Historical intelligence must remain explainable and deterministic rather than becoming a second hidden truth source.

## Documentation And Carry-Forward Review

Important architecture, orchestration, planning, and validation decisions should live in repo docs rather than only in chat history.

For every post-merge, post-release, or next-lane review, classify prior recommendations as:

- carry forward
- defer
- discard

Never treat prior suggestions as automatic scope.

For every `PR Readiness` pass, also run the formal Governance Drift Audit from `Docs/phase_governance.md`.
If that audit finds required canon strengthening, do not silently merge past it.

Use `Docs/Main.md` as the routing index for the merged canon.

## Backlog Governance

`Docs/feature_backlog.md` is a controlled registry layer.

Only true broad feature-family backlog entries should remain as parseable `### [ID: FAM-XXX]` backlog records by default. The legacy `FB-###` namespace is historical-only; historical pass aliases, support/governance lanes, and old registry-only implemented IDs are traceability rows that route to family dossiers, canonical workstream records, or same-file historical trace; they must not be selected as backlog items by inertia.

Canonical identity model:

- `FAM` is a broad long-lived product family.
- `Package` is a bulk branch/release package under exactly one FAM.
- `Slice` is a traceable deliverable area inside exactly one package.
- `Seam` is an execution or validation checkpoint.
- `PR` is merge/review evidence only.
- legacy global `FB` is historical trace only.

Branch scope standard:

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Element Coverage standard:

- Element Coverage is a non-identity checklist owned by FAM/package analysis, Branch Readiness Stage 1, and PR Readiness Stage 1 review
- coverage categories are user-facing surface, runtime/backend behavior, fail-safe/recovery, security/privacy, voice/audio, external integration, local AI/capability packs, packaging/install, monitoring/HUD, validation, and release impact
- Element Coverage rows never count as `Admission State: Admitted`, slices, seams, packages, FAMs, selected-next truth, or release drivers

Open backlog selection is priority-led:

- `Priority` is the primary selection signal for open candidate work
- `Target Version` must not be used to rank, select, defer, or skip open backlog candidates
- open `Registry-only` and active `Promoted` entries should not carry `Target Version`
- closed, released, implemented, or release-debt entries may keep `Target Version` as historical release evidence
- deferred open entries must state `Deferred Since:`, `Deferred Because:`, and `Selection / Unblock:` before they are eligible for next-workstream selection

Codex may:

- propose backlog changes
- draft exact backlog markdown for approval
- carry approved state changes during an explicitly authorized docs pass

Codex may not:

- silently add backlog items
- add, split, promote, package-admit, branch-create, select successor backlog identities, or waive the single-slice package blocker without explicit USER approval
- create or reuse parseable `FB-###` backlog IDs
- turn historical trace rows back into parseable backlog entries without explicit USER approval
- silently change priority or status outside approved work
- silently mark work complete because a branch merely looks clean

If Codex reaches the approval blocker, it must report `Backlog Addition User Approval Missing` and list every FAM that is still not closed plus every package or slice that is not complete.
If no still-not-closed entries exist, report `Backlog Exhaustion User Decision Pending` and stop for USER direction.

## Retired Task-Template Compatibility

`Docs/orin_task_template.md` is a retained forwarding stub for old links, not a per-task execution scaffold or an independent owner of prompt or phase law. Current prompt-generation and loader continuity belong to `Docs/nexus_startup_contract.md` after Main-first loading. The product and phase requirements in this document and `Docs/phase_governance.md` remain authoritative for their layers; current task identity and operational effects resolve through the matching external owner and explicit USER authorization.

# Current Workspace Root Override

Current root routing is owned by `Docs/nexus_workspace_roots.md`. Neutral main
is `D:\Nexus Desktop AI\Product Repository`; active worktrees are under
`D:\Nexus Desktop AI\Worktrees`, external operational state is under
`D:\Nexus Desktop AI\Governance State`, and USER review hubs are under
`D:\Nexus Desktop AI\USER`. C-drive paths retained in
historical receipts or fixtures are not current execution targets.
