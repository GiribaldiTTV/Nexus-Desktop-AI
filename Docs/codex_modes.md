# Nexus Codex Modes

## Top Rule: Pre-PR Durability

Follow `Docs/phase_governance.md#pre-pr-durability-rule`: local commit, push, PR, merge, release, publication, and live activation are separate explicitly authorized actions.

**Release Readiness is file-frozen: block ANY source, docs, canon, validator, helper registry, release-note, or handoff-file changes discovered or needed during `Release Readiness`. Do not edit, stage, commit, or push in `Release Readiness`; route the change back to `PR Readiness` before merge, or to the next active `Branch Readiness` after merge.**
**Release Readiness anchor and aggregation rules are owned by `Docs/phase_governance.md`. This modes file keeps only the compact behavioral mirror: do not mutate files in Release Readiness, and derive candidate/window truth from Git/GitHub/helpers.**
**Post-release external operational state carry-forward is not a Release Readiness blocker by itself after RR2 release publication when release/tag/body/health validation is green. Any bounded RR2 reconciliation is selected by the installed external owner and requires existing USER authorization for its exact effects; otherwise return the missing decision. BR1 reports `Post-Release External State Carry-Forward:` and routes any necessary BR2 reconciliation through that same owner and authorization boundary before dependent setup or implementation.**
**Branch Readiness Stage 1 candidate selection must include the `BR1 Candidate Viability / Grouping Matrix` owned by `Docs/phase_governance.md`: prove a concrete feature outcome, implementation-bearing route class, behavior-change classification, Family Feature Vision / Deferred Feature Carryforward disposition, grouping recommendation, split reason if not grouped, Slice/SLC/seam map, proof path, largest safe coherent package explanation, and tiny-branch sprawl review before recommending candidates.**
**After a release-bearing merge/rebaseline, BR1 must report `Post-Merge Release Readiness Handoff:` and stop on `Post-Merge Release Readiness Decision Missing` or `Release Readiness Handoff Skipped` when Release Readiness Stage 1 has not run and USER has not explicitly deferred it.**

## Purpose

This document defines the collaboration posture Codex should use while handling Nexus Desktop AI tasks.

It works with:

- `Docs/development_rules.md`
- `Docs/phase_governance.md`
- `Docs/Main.md`
- `Docs/nexus_startup_contract.md` for applicable loader and prompt-generation continuity; `Docs/orin_task_template.md` is a retired compatibility pointer only

If those sources conflict, live repo truth and the higher-order governance docs win.

## Why Two Modes Exist

Nexus work benefits from two different postures:

- one for deep truth-mapping, drift analysis, and next-move determination
- one for carrying an approved task through execution and verification

The modes should not be confused.
Analysis mode exists to understand the whole system first.
Workflow mode exists to execute approved work without silent scope drift.

## Required Startup Assessment

Before planning, patching, reviewing, or recommending the next move in either mode, Codex must load the owning source-of-truth documents and validate live repo truth.

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

## Mandatory Bounded State

Workflow mode is legal only inside a proven `Bounded State:` unless USER grants an explicit bounded-state waiver.

Before any file mutation, branch/worktree creation or switch, commit, push, PR action, release action, runtime validation, shortcut mutation, provider/model installation, or GitHub Desktop handoff, Codex must prove the exact phase/stage, workspace, git root, branch, upstream, `HEAD`, `origin/main`, worktree role, write target, owning authority record, active package/slice/seam, allowed scope, affected surfaces, validation contract, non-includes, pending USER decisions, stop/report conditions, and next legal phase.

If that bounded state is absent or ambiguous, Codex must stop on `Bounded State Missing`. If the task needs wider scope than the bounded state allows, Codex must stop on `Bounded State Waiver Missing` unless `Bounded State User Waiver: Granted` names the branch/worktree, phase, slice/seam, relaxed bound, allowed extra seams/slices/files, expiration or stop condition, required validation, and still-pending USER decisions.

Assigned Worktree Confinement is part of bounded state. A thread assigned to a worktree must report `Active Thread Owner:`, `Thread Assignment Status:`, `Worktree Ownership Ledger:`, `Intended Write Set:`, `Same Worktree / Same Branch Collision Check:`, `Dirty Worktree Collision Check:`, `Dirty Worktree Recovery Packet:`, `Off-Worktree Work Routing:`, `Governance Routing Barrier:`, `New Worktree Decision Gate:`, `Expected Worktree Root:`, `Actual Worktree Root:`, `No Cross-Worktree Mutation:`, and `GitHub Desktop-bound worktree` before mutation or handoff. If the active git root is outside the assigned worktree, stop on `Worktree Escape User Waiver Missing`; if another active thread owns the same worktree or branch, stop on `Parallel Worktree Coordination Missing`; if the target worktree is dirty and ownership is unclear, stop for a `Dirty Worktree Recovery Packet`; if work belongs outside the assigned root or active branch scope, stop on `Governance Routing Barrier` and route it to the approved external Governance owner instead of self-activating another worktree. Only USER can grant `Worktree Escape User Waiver: Granted` or pass the `New Worktree Decision Gate`, and the waiver/decision must name the expected root, actual root, target root, allowed commands/files, expiration or stop condition, required validation, and return path.

Prompt-Ingress Lane Lock happens before target-lane execution. If an attached prompt, pasted prompt, referenced file, generated prompt, automation/heartbeat instruction, or ChatGPT review prompt names a different worktree, family, branch, repository path, packet path, or USER hub label than the assigned thread, Codex must stop on `Prompt-Ingress Lane Mismatch` before changing directories, loading that sibling lane's source truth for execution, running helpers, generating packets, mutating external state, or executing commands there. A prompt that says "You are Codex operating in" another lane is evidence of a requested lane, not permission to switch lanes. Only an explicit USER lane-switch/worktree-escape decision can authorize the target lane, and it must name target root, branch, command/file scope, read/write mode, expiration or stop condition, validation, and return path.

Codex App thread/worktree hook guidance is policy-only unless USER separately approves local installation. A local hook may enforce the assigned Git root and prompt-ingress lane lock, but live hook config, thread-lock files, waiver packets, and audit logs are USER-local operational state outside the repo. Read-only cross-worktree analysis is allowed only after the mismatch is reported and routed; write-capable actions outside the assigned root, including packet generation, Git mutation, external-state writes, cleanup, and helper runs that write files, remain blocked without an explicit worktree escape waiver. Operational Governance mutation uses the exact USER-approved external source carrier; no fixed historical worktree overrides that assignment.

Broad work requests do not authorize implementation. `Continue`, `complete all`, `all remaining work`, `finish the branch`, or similar wording can execute only when source truth resolves it to one exact active bounded seam. Clean validation, branch existence, prompt wording, Codex discretion, or ChatGPT wording cannot infer a waiver.

That startup assessment should explicitly answer:

- `Source-of-Truth`
- `Record State`
- `Branch Truth`
- `Canonical Workstream`
- `Reuse Baseline`
- `Next Safe Move`
- `Source-Truth Placement Preflight` when the task may create a new governance/source-truth file, active artifact, ledger, registry, or durable authority surface
- `Element Validation Ledger Owner` when the task creates, touches, affects, defers, or preserves proof-bearing product elements
- `Dev Toolkit Interface Review Mode disposition` for USER-facing interface elements, including previous and future implementations: callable in dev-only review mode, deferred to a named repo-wide adoption branch/package, or not-applicable with reason

This can stay brief, but it should happen before scope is narrowed for execution.

## Analysis Mode

### Goal

Map the real current state of the system before deciding what should happen next.

### When To Use It

Use Analysis mode when the user asks for:

- drift review
- post-release or post-merge review
- workstream planning
- readiness analysis
- sequencing analysis
- source-of-truth audit
- next-lane determination

### What Codex Should Do

In Analysis mode, Codex should:

- validate current repo truth first
- scan broadly enough to understand the whole affected system
- compare code, docs, branches, tags, and release facts where relevant
- identify factual drift, structural drift, and authority drift
- classify prior suggestions as carry-forward, defer, or discard
- determine the correct next workstream-level move

### Required Analysis Depth

Analysis mode should reason at:

- system level
- lane level
- workstream level
- document-ownership level

Do not narrow to the first apparent slice before full drift and dependency mapping is complete.

### What Codex Must Not Do

In Analysis mode, Codex must not:

- default into implementation
- assume PR, merge, release, or closure is the next move
- compress the task into the smallest possible pass before understanding the system
- treat local unmerged overlays as merged truth

### Expected Outputs

Default Analysis mode return packets include:

- validated current truth
- key drift findings
- structural assessment
- sequencing options
- one recommended next workstream move

## Workflow Mode

### Goal

Execute an approved task faithfully, verify it, and keep the resulting truth coherent.

### When To Use It

Use Workflow mode when the user has already approved:

- a docs-only pass
- a bounded patch
- a canon sync
- a workstream closure pass
- another clearly bounded execution task

### What Codex Should Do

In Workflow mode, Codex should:

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

### What Codex Must Not Do

In Workflow mode, Codex must not:

- silently widen scope
- silently start a new workstream
- silently create PR, merge, release, or closure output without current-truth justification
- treat a clean first slice as automatic branch readiness
- stop after a green seam merely because the prompt task named only the entry seam, the output asks for `Next Safe Move`, durability completed, or one seam was recorded
- treat branch existence, branch rename, backlog promotion, repair-only traceability, or release-bearing posture as Workstream progress by themselves
- treat planning or canon-only output on an implementation branch as valid Workstream progress without explicit USER-approved bypass markers
- open an unapproved product-repository repair carrier or place operational Governance implementation in a product/FAM diff
- create a parallel active source-truth artifact for element tracking when the existing workstream doc or branch authority record already owns the ledger

### Expected Outputs

Default Workflow mode return packets include:

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

Pre-PR Durability Rule:

Follow `Docs/phase_governance.md#pre-pr-durability-rule`: local commit, push, PR, merge, release, publication, and live activation are separate explicitly authorized actions.
PR Readiness still checks the approved product branch's durable truth before PR creation.


When the approved phase is `PR Readiness`, the output must also explicitly include:

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

```markdown
## Next Workstream
- Recommended Next Workstream:
- Recommended Family / Package:
- Candidate Slices:
- Candidate Work To Be Done:
- User-Facing Output:
- Why This Is Next:
- Dependencies / Blockers:
- Validation Needs:
- Release Impact:
- Selection Truth Status:
- Branch Creation Status:
```

- Missing next-workstream recommendation, missing selected-next truth, missing `Next Workstream User Waiver:`, or omitted next-workstream block does not block Stage 2 by default. If USER-approved PR-time selected-next truth exists or selected-next truth already exists, validate it and report the applicable selected-next blocker when it is inconsistent.
- Stage 1 must record one outcome before any Stage 2 approval can be accepted: `Stage 1 Ready For Stage 2`, `PR Readiness Stage 1 Repair Required`, `Current-Branch Branch Readiness Re-entry Required`, `New Carrier Branch Required`, or `Stage 1 USER Waiver Required`
- Stage 2 may begin only after `Stage 1 Ready For Stage 2` is recorded and explicit USER approval exists; PR creation is blocked while any Stage 1 blocker, Stage 1 repair item, applicable selected-next validation item, applicable branch-shape review item, or Stage 2 sync prerequisite remains unresolved
- an optional Stage 1-only `## Next Branch Pre-Plan` section with this field shape when USER asks PR Readiness for next-branch analysis or selected-next truth already exists:

Planning and proof apply to the actual approved objective. One coherent deliverable is valid; actual new scope, ownership, safety, phase and human-result decisions remain governed by `Docs/phase_governance.md`.

- Route a next-branch pre-plan through Branch Readiness only for a real new scope, carrier, ownership or USER decision. One coherent deliverable is valid; slice or seam count does not decide admission.
- if the governance/source-of-truth ledger audit finds identity model drift, FAM taxonomy drift, package/branch rule drift, USER approval blocker drift, real-carrier routing drift, branch-authority lifecycle drift, watcher/automation proof drift, release readiness/execution boundary drift, Element Coverage misuse, ChatGPT loader/source-truth drift, project-direction drift, current workflow drift, after-release workflow drift, or absolute-guardrail drift that cannot be cleared as bounded current-branch PR Stage 1 repair, report `Governance Ledger Fallback:` plus either `Current-Branch Branch Readiness Re-entry Required` or `New Carrier Branch Required` and route to Branch Readiness

Planning and proof apply to the actual approved objective. One coherent deliverable is valid; actual new scope, ownership, safety, phase and human-result decisions remain governed by `Docs/phase_governance.md`.

```markdown
## Next Branch
- Next Legal Branch Type:
- Next Branch Name:
- Branch Class:
- Creation Status:
- Creation Gate:
- Selected Next Workstream:
- Selected Next Implementation Branch:
- May Create Now: YES / NO
- Reason:
```

- when PR Readiness is package-ready or `PR package ready`, inclusion-only PR operator copy blocks with this exact shape:

````markdown
## PR Creation Details
### PR Title
```text
<title only>
```

### Base Branch
```text
<base branch only>
```

### Head Branch
```text
<head branch only>
```

### PR Summary
```markdown
## Summary

<concise branch outcome and purpose>

## What Changed

<concrete implemented work, source-truth changes, behavior/capability changes, and useful historical context; do not repeat the Summary>
```
````

The `Next Branch` section must separate the next legal branch type/name from the selected next implementation workstream branch.
If release debt, updated-`main` revalidation, or another admission gate blocks branch creation, `May Create Now: NO` is required with the reason.
The `PR Creation Details` block is preparation material only; it must not imply PR creation, merge execution, release execution, next-branch creation, or PR Readiness GREEN has occurred.
Each PR operator field must be its own copy-ready block and must be usable independently.
The PR summary/GitHub PR body uses exactly two top-level sections: `## Summary` and `## What Changed`.
`## Summary` must be one concise human-readable outcome paragraph, and `## What Changed` must describe the actual branch work in concrete Markdown-friendly detail without repeating the Summary through nested `### Summary`, `### Purpose`, or `### Overview` sections.
Use concrete What Changed subheads such as `### Source Truth`, `### Runtime`, `### Tooling`, or `### Review Support` only when they improve scanability.
The PR summary must include implemented branch truth only. GitHub PR bodies and PR Summary copy must not include `## Validation`, `## PR posture`, `## Branch Evidence`, Testing/Checks sections, generic exclusion dumps, `Not Included` sections, deferred/future-gated sections, defensive scope language, or phase-digest/Codex operator handoff fields such as `Next Legal Phase`, `Next Safe Move`, `Continue Decision`, `Stop Basis`, `Exact next USER decision`, `Implemented, validated`, or `::git-*`.
Validation commands, command output, byte-proof evidence, mergeability, bot-review state, watcher state, and PR Readiness posture belong in Codex digests, helper output, status checks, or external operational state, not the GitHub PR body.
Before PR creation, write the proposed GitHub PR body to a temporary local file and run `python dev\orin_pr_body_quality_audit.py --body-file <path> --body-title "<PR title>"`. If it reports `Changed: True` or warnings, stop on `PR Body Drift Check Failed`, normalize the body with `--apply` or replace the PR body with the normalized output, and rerun the check before calling `gh pr create` or any connector PR-creation action. After PR creation, verify the live PR body with `python dev\orin_pr_body_quality_audit.py --limit 1` or narrower equivalent. All visible PR bodies must be scanned by `dev\orin_pr_body_quality_audit.py`; every nonconforming PR body inside the approved GitHub correction scope must be repaired before the PR-body standard can be reported green. The helper must preserve useful trimmed Summary detail inside `## What Changed`; do not use lossy summary trimming as a shortcut to PR-body green.
PR Readiness GREEN requires the PR to exist, be open, be non-draft, have no conflicts, explicitly report a green merge status, match merge-target canon, clear `Merge-Target Authority Projection Unproven` by ensuring active branch authority will not survive into merged `main` when post-merge truth is `No Active Branch`, have no unresolved Codex comments/issues or requested changes, clear the live PR bot-review signal through a Codex Connector bot thumbs-up reaction or green approval comment on the current head, directly verify the live PR head/checks/comments/reviews/mergeability in the active Codex turn or helper output, clear `PR Watcher Provisioning Unproven` and `PR Watcher Routing Unverified` only when a USER-approved watcher exception exists, clear `PR Merge Verification Pending` only after direct GitHub/GitHub-connector verification proves the PR is `merged`, and avoid `Automation Runtime Unproven`; approval proof must be bound to the current live PR head by review commit SHA, PR timeline order, or equivalent GitHub live-head evidence, not by local commit time alone; when a bot comment appeared after the last approval, a later thumbs-up/approval signal is required after same-PR repair and comment-resolution closeout. This is the same-PR Codex bot-review repair loop: actionable bot comments must be fixed on the same PR, pushed, replied to, resolved, revalidation-requested with a 3-5 word PR comment only, and then approved by a later Codex Connector bot thumbs-up/approval signal before green. Stage 2 final handoff cannot be green until the post-repair bot thumbs-up/approval latch is verified. The Direct PR2 Continuation Rule blocks quiet handoff: bounded PR2 direct verification keeps running in the active Codex turn after revalidation requests and repair pushes until new actionable feedback is repaired or blocked, the current-head approval latch plus green mergeability allows merge, the PR merges/closes, or a real blocker appears. `Current-Head Revalidation Pending` is an active PR2 continuation state, not a terminal `BLOCKED` state, while GitHub and the Codex Connector remain reachable and direct polling can continue; an eyes-only or quiet current-head review request must stay in the PR2 loop instead of becoming a blocked handoff. Recurring PR watcher automation is denied by default for bounded PR2; watcher modes and Watcher Health Proof apply only to a USER-approved watcher exception or historical receipt.

Post-merge closeout proof must be in merged source truth, not only in a deleted branch, reflog, automation memory, or conversation transcript. If missing proof blocks a release, carry it on a real release-support carrier; if product work is next, carry it on the next real runtime package carrier.

Automation Observability Review Pending routes directly verified Codex automation run/inbox and memory evidence to the applicable external operational owner. The repository report helper retains historical root/role assumptions and is not current operational authority. Treat `BLOCKER_CANDIDATE` and `REVIEW_REQUIRED` findings as bounded repair candidates that must be admitted before repo canon changes; treat `REVIEW_INFO` as informational unless it contradicts repo truth. Background-observability-only automations are advisory and must not be used as watcher-exception proof, bot-review repair proof, merge verification proof, or release-readiness proof. `ACTIVE` is configuration state, not run proof; accepted automation runtime proof must come from thread or inbox output, automation memory/log/state-file updates, scheduler last-run evidence, or a bounded fallback that is target-scoped, phase-scoped, and self-terminating or explicitly deleted.

When the approved phase is `Branch Readiness`, the output must also explicitly include:

- the current Branch Readiness stage: `Branch Readiness Stage 1 - Analysis Gate` or `Branch Readiness Stage 2 - Execution Gate`
- for Stage 1, the `## Branch Readiness Stage 1 Analysis Packet`, including product vision, project-wide vision alignment, branch-specific vision alignment, USER vision questions, `USER Vision Question Packet`, Codex product interpretation, Codex implementation recommendation, Codex additional recommendations, USER/ChatGPT review checkpoint, USER critique loop, USER decision ledger, full feature element breakdown, system concept model, entity/profile model, user workflow model, scale/data-volume model, configuration/state model, whole-system interaction map, minimum viable vs full-system boundary, current branch vs future package boundaries, affected surfaces, branch reach, why the branch is large enough, why it should not split into tiny branches, expected user-facing outcomes, acceptance criteria, screenshot and User Test Summary proof expectations, implementation sequence proposal, rejected shallow plan, alternatives/tradeoffs reviewed, open USER decision points, deferred ideas/future-package ledger, `Stale Branch Cleanup Plan:`, `Branch Readiness Planning Incomplete` blocker review, `Next Legal Phase:`, interface release boundary review with `Primary Interface Release Surface:`, fallback point, interface acceptance/proof path, and `Interface Bundle User Approval:` status for user-facing family/package branches, plus the `Carrier Lifecycle Decision` with `Carrier Lifecycle Classification:` exactly one of `Fresh current branch`, `Stale empty local branch`, `Stale branch with unique commits`, `Historical merged branch`, `Wrong carrier/worktree`, or `Active remote/open PR branch`, and with `Remote Branch State:`, `Unique Branch Diff:`, `Origin/Main Ancestry:`, `Origin/Main Advanced Since Branch Creation:`, `Open PR State:`, `Worktree Checkout State:`, `Recommended Stage 2 Carrier Action:`, `Branch Cleanup Execution Gate:`, `Recreate From Current origin/main:`, and `No Unique Commit Loss Proof:`; include confirmation that there was no repository file mutation, no branch creation, no package admission, no docs sync, no PR work, no release work, and no selected-next truth, plus `Branch Readiness Execution User Approval Missing` as the stop blocker until explicit USER approval to enter Stage 2 is recorded; when USER input is needed, the question packet must include Codex recommendation, rationale, options, tradeoffs, current-branch impact, future-package impact, safe default, waiver/defer posture, and exact response format; if USER needs a durable editable handoff, Stage 2 may generate or refresh a USER-facing `User Vision Input.txt` desktop artifact, but the artifact is not repo source truth until a later USER-approved digest pass records completed answers; missing recommendation/rationale/tradeoffs blocks on `USER Vision Recommendation Missing`; missing/incomplete/undigested input artifacts block on `USER Vision Input File Missing`, `USER Vision Input Answers Pending`, `USER Vision Input Digest Pending`, and `USER Vision Input Pending`; missing or shallow product-system planning blocks on `Project-Wide Vision Alignment Missing`, `Branch-Specific Vision Alignment Missing`, `System Concept Model Missing`, `Entity / Profile Model Missing`, `User Workflow Model Missing`, `Scale / Data Volume Model Missing`, `Configuration And State Model Missing`, `Expected User-Facing Outcomes Missing`, `Codex Additional Recommendations Missing`, `USER Critique Loop Missing`, `USER Decision Ledger Missing`, `Deferred Ideas / Future Package Ledger Missing`, `Planning Adequacy Review Missing`, `Rejected Shallow Plan Missing`, `Alternatives And Tradeoffs Missing`, `Whole-System Interaction Map Missing`, `Minimum Viable vs Full System Boundary Missing`, or `Open Questions / USER Decision Points Missing`; missing or ambiguous primary interface release boundaries block on `Interface Release Boundary Missing`, `Primary Interface Undefined`, `Multiple Interface Release Drift`, `Fallback Point Missing`, `Interface Acceptance Missing`, or `Branch Readiness Interface Planning Incomplete`; Branch Readiness does not select the next workstream by default and instead analyzes/adopts USER-approved selected-next truth from prior PR Readiness when present
- active implementation `Product Definition Plan` entries must include non-empty, concrete `Project-Wide Vision Alignment:`, `Branch-Specific Vision Alignment:`, `System Concept Model:`, `Entity / Profile Model:`, `User Workflow Model:`, `Scale / Data Volume Model:`, `Configuration And State Model:`, `Expected User-Facing Outcomes:`, `Codex Additional Recommendations:`, `USER Critique Loop:`, `USER Decision Ledger:`, `Deferred Ideas / Future Package Ledger:`, `Planning Adequacy Review:`, `Rejected Shallow Plan:`, `Alternatives And Tradeoffs Reviewed:`, `Whole-System Interaction Map:`, `Minimum Viable vs Full System Boundary:`, and `Open Questions / USER Decision Points:` markers before Workstream, Hardening, Live Validation, or PR Readiness begins or resumes; placeholder or self-assessed values such as `simple`, `basic`, `minimal`, `see above`, or `not applicable` do not count as proof
- runtime-focused implementation branches must also carry `## Runtime Branch Engineering Contract` before Branch Planning begins, with `USER Engineering Planning Review:`, `Runtime Implementation Approval:`, `Current Runtime Baseline:`, `Planned Runtime Delta:`, `User-Facing Runtime Delta:`, `State / Config / Schema Delta:`, `Validator / Helper Delta:`, `Expected Changed Files / Surfaces:`, `Approval-Boundary Audit:`, `Future-Gated Items:`, `Workstream Seam Map:`, `Proof Expectations:`, `Risk Forecast:`, `Recommendations And Alternatives:`, `Plan Version / Revision Status:`, and `Plan-To-Implementation Traceability:`; new or re-entering runtime branches must also carry an active Branch Runtime Engineering Plan at `D:\Nexus Desktop AI\Governance State\branches\<branch_slug>\branch_plan.md` or a pending Stage 2 requirement, linked by `Branch Runtime Engineering Plan Path:`, with `Engineering Plan Status:` and `PR Fold-Down Packet:` markers; Before asking USER to green-light implementation, Branch Planning must deliver one primary current-gate decision and the required branch vision, active external branch plan or historical repo receipt, branch authority, relevant Nexus/family vision, matrix, UFD/change-intent and source-truth context through the current external USER lifecycle owner, routed by `Docs/governance_efficiency_operating_model.md#user-review-hub-rule` to the approved workstream collection; BP1 must return the `USER Branch Vision Review Gate`, BP2 must return the `USER Branch Plan Review Gate`, and BP3 must return Workstream Entry / Orchestration Validation; stop on `BP1 Branch Vision Review Missing`, `BP2 Branch Plan Review Missing`, `BP3 Orchestration Validation Missing`, `USER Review Packet Stale`, or `USER Review Packet Not Digested` when required planning review, USER response, Codex Response Digest, scope dispositions, exact USER decision, or `USER Review Packet Finding:` is absent or stale; use the accepted Branch Planning contracts and active external plan to compare seam start packets, seam closeouts, Workstream Green, Hardening proof, Live Validation proof, PR Readiness scope integrity, and Release Readiness public scope against admitted engineering intent
- completed USER input digests may add package-specific planning blockers such as legacy product-name drift, telemetry provider selection, polling floor, warning modality, external telemetry privacy model, cross-family audio approval, or persona/model switching scope; these block Workstream entry or continuation until Branch Readiness revalidates or defers them. When USER declares legacy product naming invalid for the current product, `Legacy Product Name Drift` blocks Workstream entry or continuation while that naming remains anywhere in tracked repo source, runtime artifact paths, validators, docs, generated-user surfaces, user-facing copy, or persona-facing copy. The only default preservation location is external GitHub release/tag history; tracked repo preservation requires explicit USER waiver or a USER-approved migration carrier. Product identity and persona identity must remain separate: ORIN may be the shipped/default persona, ARIA may be shown only as locked/coming soon planning copy when source truth allows it, and actual persona switching implementation requires later admission.
- Branch Planning reinforcement: BP1 must treat `USER_BRANCH_VISION_REVIEW.md` as the USER Branch Vision Contract, and BP2 must treat `USER_BRANCH_PLAN_REVIEW.md` as the BP2 Branch Plan Contract. BP1 owns branch goal, end-state, product shape, user-facing behavior, surfaces, options, Codex recommendations, USER response, Codex digest, accepted Branch Vision, deferred/future-gated ideas, and decision state. BP2 owns the accepted Branch Vision summary, package summary, branch scope size test, SLC/seam plan, affected surfaces, likely files, validators/helpers, proof requirements, H1/LV/UTS expectations, rollback/safety plan, risks, future-gated boundaries, plan review checklist, `USER Review Response`, Codex digest, implementation constraints, and exact BP3 approval text. Branch Planning packets must keep `Packet Reviewability State` separate from `USER Gate State`; reviewable/helper-green packet output is not USER acceptance or implementation authority. `Contract Status` must be `Complete` or `Waived by USER` before implementation approval is legal; `Draft`, `Pending USER Response`, `Pending Codex Digest`, and `Pending USER Confirmation` block implementation. If USER feedback changes direction, UI behavior, workflow, scope, boundaries, or seam order, Codex must update source truth and deliver selected evidence for renewed pending review through the external USER lifecycle owner, set Contract Status to Pending USER Confirmation, and wait for confirmation or explicit waiver. SLC/slice/seam details are implementation staging only and must not become the primary USER decision surface.
- Unresolved product decisions block their dependent actions. An unchanged admitted repair continues using the accepted plan and affected evidence without repeating planning stages.
- State the actual approved objective, affected scope, evidence, unresolved decisions and rollback needs. Reuse the accepted plan for unchanged continuation; do not require multiple slices or copied planning packets.
- for Stage 2, confirmation that USER approval to enter Stage 2 exists before branch/package admission work, docs sync, branch creation, or authority-record setup occurs
- for Stage 2, the `Thread Launch / Write-Target Identity Lock` result before mutation, including current workspace, git root, branch, upstream, `HEAD`, `origin/main`, worktree role, clean state, expected phase/seam, write target, active thread owner, thread assignment status, worktree ownership ledger, intended write set, same-worktree/same-branch collision check, dirty-worktree collision check, dirty-worktree recovery packet posture, and any runtime/process or GitHub Desktop binding checks relevant to the work; if assigned parallel worktree mode is active, also include assigned thread owner, intended write set, source-truth owner, shared-file overlap forecast, Git operation ownership, runtime/interactive-validation ownership, and branch/file health markers; if any identity does not match, stop on `Thread / Worktree Identity Mismatch` or `Parallel Worktree Coordination Missing` and return a routing packet instead of continuing

Element Coverage is a non-identity checklist only. Coverage categories are user-facing surface, runtime/backend behavior, fail-safe/recovery, security/privacy, voice/audio, external integration, local AI/capability packs, packaging/install, monitoring/HUD, validation, and release impact. Element Coverage rows never count as `Admission State: Admitted`, slices, seams, packages, FAMs, selected-next truth, or release drivers.

When the approved phase is `Release Readiness`, the output must also explicitly include:

- whether the branch is release-bearing
- confirmation that `Release Target Undefined` is clear
- for release-bearing branches:
  - `Release Target:`
  - `Release Floor:`
  - `Version Rationale:`
  - `Release Scope:`
  - `Release Artifacts:`
  - confirmation that marker presence and semantic target correctness both pass
- for explicitly non-release branches:
  - `Release Branch: No`
  - confirmation that this is only a historical context, not a new governance-only branch or a direct-main repair path
- confirmation that the non-release waiver is not being used for an `implementation` or `release packaging` branch
- confirmation that `Release Debt`, post-merge truth, validation, and successor branch deferral remain governed by their normal blockers
- confirmation that Release Readiness is not being used as a docs-sync or branch-authority cleanup phase
- confirmation that Release Readiness is not deleting stale/old branches, removing worktrees, switching branch targets, or changing a GitHub Desktop-bound worktree; it may record `Branch Cleanup Plan:` plus `Branch Cleanup Execution Gate:` and defer execution to `Branch Readiness Stage 2 - Execution Gate`
- confirmation that cleanup touching a family-stable or GitHub Desktop-bound folder is blocked by `Stable Worktree Path Preservation Gate:` until `Stable Worktree Path:`, `Replacement Binding Path:`, and the preservation method are recorded; stop on `Stable Worktree Path At Risk` if the stable folder would be removed before the successor branch/worktree is moved, switched, or explicitly rebound there
- confirmation that Release Readiness declares `Release Candidate Anchor:`, `Release Candidate Anchor Source:`, `Target Commit:`, `Historical Endpoint Handling:`, and `Candidate Includes Later Governance Repairs:` and stops on `Release Candidate Anchor Missing` when those values are absent or ambiguous
- confirmation that Release Readiness declares `Release Ownership Model:`, `Release Window Contributors:`, `Merged-Unreleased Scope Inventory:`, `Last Runtime PR:`, `Post-Runtime Governance Repairs:`, and `FAM Contributor Routing:` and stops on `Release Window Contributor Inventory Missing` when multi-FAM/worktree contributor inventory is absent or ambiguous
- confirmation that Release Readiness validates current fetched `origin/main` by default and treats historical PR merge commits as audit evidence only unless USER explicitly selects a historical commit as the release target
- confirmation that merge order does not decide release ownership; multiple FAM/worktree contributors in the selected target are released through `Release Ownership Model: Aggregated release window` unless USER selects a narrower release target
- confirmation that governance/source-truth-only PRs merged after the last runtime PR may be included in the release candidate without forcing the target back to the runtime merge commit, with `Candidate Includes Later Governance Repairs: YES` recorded and internal-only repairs kept out of user-facing release-feature claims
- confirmation that Release Readiness is analysis-only for repository files and that no source, docs, canon, validator, helper, release-note, or handoff files were edited, staged, committed, generated, or refreshed
- if repository files require a change, report `Release Readiness File Mutation Attempt` and return to their owning legal repair phase; operational Governance changes use the separately scoped external carrier
- when Release Readiness is green for release execution, inclusion-only release operator copy blocks with this exact shape:

````markdown
## Release Package Details
### Release Title
```text
<release title only>
```

### Release Tag
```text
<tag only>
```

### Target Commit
```text
<commit sha only>
```

### Release Notes
```markdown
<detailed user-facing release notes>
```
````

The Release Notes block must prepare the human-written Markdown release body using the standard release body shape: `## Release Summary` or `## Release Overview`, followed by `## Release Highlights` or release-specific rich sections.
The live GitHub release body must not start with or repeat the release title as `# <release title>`; the release title belongs in GitHub release metadata and the separate `Release Title` operator block only.
During Release Execution, the live GitHub release body must also include GitHub-generated release notes with `## What's Changed` and the generated `**Full Changelog**:` compare link to the previous release, populated through the GitHub release notes button or generated-release-notes API.
Do not hand-write or omit the generated changelog section when publishing or repairing a GitHub release.
Public release bodies must not include internal automation/tooling brand tokens, generated branch-prefix noise, phase-handoff text, or operator transcript text. Rewrite generated `[codex]` / `codex/...` PR labels into neutral user-facing PR names before publication or repair them immediately after publication.
The release-body standard applies to every published Nexus pre-Beta release body, not only the latest release.

- release notes must clearly explain what was built, what capabilities exist, and how the system behaves
- release notes must not include exclusion lists, `Not Included` sections, negative scope framing, or defensive wording

Do not report cleanup as complete unless the pass has explicitly checked for leftover apps, windows, dialogs, helper processes, probe files, or other temporary artifacts it created or opened.

Do not report an interactive validation pass as complete or trustworthy if it exceeded its time budgets or sat stalled without a clean abort path.

Do not create a new live-validation script by default.
For Live Validation, Codex should reuse existing helpers first, then parameterize or extend them, then extract shared support if several helpers need the same watchdog or cleanup behavior.
Temporary one-off probes are allowed only as ignored exploratory artifacts and must be deleted or promoted into documented reusable tooling before closeout-grade proof is claimed.
Durable root `dev/` validators, live-validation scripts, audit helpers, harnesses, and shared helper modules must also be checked against `Docs/validation_helper_registry.md`.
If a new helper is kept, Codex must report its standardized name, `Helper Status:`, owner, reuse decision, and `Consolidation Target` when it is `Workstream-scoped`.
Workstream-scoped seam helpers are bridge tooling, not the default release naming model, and must be consolidated, promoted, or explicitly justified before PR Readiness.
Any `Temporary probe` must stay ignored and be deleted or promoted before closeout-grade proof.

## Workstream And Branch Governance

### Grouped Workstreams

During `pre-Beta`, grouped workstreams are allowed when they remain coherent by subsystem and end-state.

That means:

- one branch may host multiple validated slices for one milestone
- grouped workstreams should not become grab-bags of unrelated ideas
- lane evaluation should stay milestone-driven rather than slice-driven

### Bounded Multi-Seam Workflow

Current planning, continuation and reporting applicability is owned by `Docs/phase_governance.md` and `Docs/governance_intake_triage_and_digest_profiles.md`; carry an accepted plan and relevant delta for an unchanged admitted repair. Actual approval, safety, scope, phase and human-result boundaries remain required.

That means:

- prompts may name a seam chain and active seam, but source-of-truth and validation decide continuation
- Branch Readiness should plan the branch objective, target end-state, expected seam families, risk classes, validation contract, User Test Summary strategy, later-phase needs, and first Branch Planning target
- Branch Planning must provide BP1 USER Branch Vision Review, BP2 USER Branch Plan Review, and BP3 Workstream Entry / Orchestration Validation before implementation so USER can accept, revise, defer with waiver, reject, or request more analysis on the readable branch vision and branch plan
- BP3 for a runtime branch with multiple admitted slices or seams must analyze the whole admitted Workstream package before recommending the entry implementation seam. The packet must report all admitted slices/seams, completion strategy, entry-seam recommendation, seam dependency map, future-gated boundaries, preservation surfaces, validation plan, Hardening H1 expectations, Live Validation LV1 expectations, visual/user-facing proof requirements, UTS handoff criteria, and exact implementation approval text that preserves bounded continuation until Workstream Green, a real blocker, or an explicit USER waiver. A first-seam-only packet blocks on `Workstream Entry Whole-Package Analysis Missing`.
- Workstream may execute multiple planned seams in one pass when they share the same workstream, phase, branch class, approved scope, and subsystem family or tightly coupled implementation, validation, or governance chain
- each seam is still analyzed, bounded, executed, validated, recorded, and judged before the next seam starts
- Hardening and Live Validation may continue through constrained validation or evidence-digestion seams only when their phase rules allow it
- PR Readiness uses readiness-gate seams for PR package, PR creation, and PR validation rather than implementation continuation; during PR2, response-level stop is illegal for a quiet/eyes-only current-head Codex Connector wait while direct GitHub verification can continue
- Release Readiness is review-only and file-frozen; it must not mutate repository files through a seam
- the output must report the per-seam validation result and `continue` or `stop` decision
- reporting `Next Safe Move` is not a substitute for execution when continuation authority passes
- A `continue` decision must be acted on immediately by starting the next seam needed inside the current slice
- a validation failure, regression, scope drift, unplanned risk expansion, governance drift, unresolved manual-validation blocker, branch-truth contradiction, phase boundary, stop-loss trigger, or other bounded stop condition stops the workflow

Legacy `Single-Seam Fallback` and `Single-Seam Mode Waiver` wording is retired in active source-of-truth.
A bounded stop condition blocks continuation; it does not by itself authorize stopping the backlog item after only one slice.
Bug fixes, hotfixes, unclear seams, high-risk seams, cross-subsystem work, settings, protocol, launcher, and UI-model changes require smaller seams and stronger gates; they do not stop a green approved seam chain unless a blocker is recorded or an explicit waiver narrows the pass to one seam.

Completing Workstream seams does not make the branch PR-ready by itself.
The normal next legal phase is `Hardening`, then `Live Validation`, then `PR Readiness`.

### Milestone Gate

Before treating a non-doc implementation branch as ready, Codex should be able to explain:

- the lane milestone target
- the minimum merge-ready threshold
- the milestone value statement
- the same-branch follow-through that still belongs inside the lane

### Worthwhile Milestone Gate

For a non-doc implementation branch, Codex should not recommend readiness until:

- the threshold is reached
- the branch is still worthwhile if squashed today
- the remaining implementable same-branch slices are no longer required, or only future-dependent blockers remain

### No-Release-Debt Gate

If `main` already contains merged unreleased non-doc implementation work beyond the latest public prerelease, treat that as an exceptional release-handling blocker, not normal branch debt.

While that exceptional blocker exists, the default next move is usually:

- release review
- release prep
- directly needed docs support

not another unrelated implementation lane.

That default blocks the next implementation lane by default unless USER explicitly approves a selected-next runtime path and records the release-handling owner/carrier plan.
This release default grants no branch creation authority. An independently USER-approved external Governance source carrier follows its own scope and does not select the next runtime lane.
Release packaging may begin only when `Docs/phase_governance.md` says that branch class may begin from `No Active Branch`.

If release handling, `Backlog Addition User Approval Missing`, `Backlog Exhaustion User Decision Pending`, or another repo-level admission blocker means no next implementation branch may legally begin execution, report repo state as `No Active Branch` only with the explicit blocker or USER waiver/defer instead of inventing a next implementation phase.
If repo truth is a steady-state `No Active Branch`, say so explicitly instead of pretending a new implementation branch should open automatically.

### Fresh Branch Start After A Closed Workstream

After a workstream is merged and closed, the next implementation workstream should execute from updated `main` on a fresh branch.

During `PR Readiness`, selected-next truth is optional and applies only when USER explicitly approves PR-time selected-next sync or selected-next truth already exists. When it applies, the next workstream must be a real runtime candidate, canon-defined, minimally scoped as a runtime slice, and explicitly not branched yet.

That successor branch is created only during `Branch Readiness` after the current branch merges and updated `main` is revalidated.

Post-merge `No Active Branch` is allowed when no USER-approved selected-next truth exists. That state does not select, create, or admit a successor branch; the next runtime implementation pipeline is chosen later in Branch Readiness Stage 1. If USER approval exists for PR-time selected-next selection but no real runtime candidate can be selected, `Next Runtime Candidate Selection Pending` blocks that selected-next path and the branch stops in PR Readiness.

If a branch is stale, merged, or identical to `main`, call it out explicitly and stop using it as the base for next-lane planning.

### Post-Release Canon Repair

Release-dependent truth must be anticipated before PR green.

When release-dependent truth changes:

- carry the canon sync on the active lane when that lane is still open
- require merge-target canon completeness before PR so merged `main` does not become stale in the first place
- after a public prerelease tag exists, require durable closure: latest public prerelease advances, released workstream moves to Released / Closed, release debt clears, and workstreams index moves the record to Closed
- classify any missed durable closure as a Branch Readiness blocker on the next legal active branch before implementation, not as permission to normalize release debt, stale canon, or cleanup-only branches
- treat architecture-only planning, admission contracts, validation-only work, documentation/canon repair, governance repair, and non-user-facing milestones as `patch prerelease` by default unless a new executable, runtime, operator-facing, user-facing, or materially expanded product capability lane is delivered
- do not use Release Readiness as a docs-sync phase
- do not use Release Readiness as a file-mutation phase; release package information may be generated as response text only
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.
- preserve the Release Readiness file freeze and protected-main boundary

## Shared Rules Across Both Modes

- analyze before changing anything
- anchor phase-sensitive work to the current phase in the matching external operational record, using the canonical phase names and product requirements in `Docs/phase_governance.md`
- do not infer a later phase from user intent alone
- verify exact behavior or doc alignment before editing
- preserve architecture boundaries
- call out source-of-truth conflicts explicitly
- backlog owns identity
- roadmap owns the stage-breakpoint schedule outline, not live release state
- workstream docs own promoted-work feature-state, branch-local evidence, external active-seam pointers or executed seam proof references, artifact history, branch-local reuse notes, and closure history
- `Docs/phase_governance.md` owns product phase and acceptance boundaries; operational Governance uses the external ownership contract
- `Docs/validation_helper_registry.md` owns product helper registration and historical Governance-helper disposition
- User Test Summary belongs to workstream-owned validation
- incident patterns are generalized knowledge, not case history
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.
- historical standing-intake receipts do not create current external authority or require a product PR for external Governance source work
- preserve the exact originating task/worktree identity for any handoff; do not infer it from current CWD or a selected desktop repository
- an approved external source-only sandbox is neither product implementation nor live activation
- retain product scope, product tests, private-state protection, and phase boundaries
- `main` is protected for Codex work; Codex may read `main` for truth validation, but any tracked file mutation, staging, commit, generation, refresh, or direct repair on `main` is a `Main Write Attempt`
- There is no emergency direct-main repair path for Codex.

For desktop workstreams, response-level `## User Test Summary` output and the canonical repo-level `UTS` artifact are related but not interchangeable:

- the response section is the current handoff copy
- the workstream-owned repo artifact is the exact `## User Test Summary` section, not `## User Test Summary Strategy`, unless the workstream explicitly declares another repo path
- the local USER hub `User Test Summary.txt` within the approved collection and evidence set selected by the external USER lifecycle owner file is the required user-facing exported copy when relevant, but it is not the default canonical repo record

If a required User Test Summary handoff is outstanding, `User Test Summary Results Pending` is a hard Live Validation Stage 1 blocker. User Test Summary is exclusive to Live Validation Stage 1. Live Validation Stage 1 cannot enter Stage 2 until User Test Summary results are `PASS` or `WAIVED`, Codex has digested the result into source truth, and blockers have been reevaluated. PR Readiness may verify the previously digested Live Validation UTS state, but it must not create, refresh, or digest UTS as its own phase artifact. Codex must route backward to `Workstream` or `Hardening` if the results expose a mismatch, regression, ambiguity, cleanup issue, or scope drift. For desktop UI Live Validation, Codex must also record `Codex Visual Adjudication:` with `Visual Artifact Review Scope:`, `Product Vision Alignment:`, `Per-Element Visual Verdicts:`, `Helper Marker Limitation:`, `Unacceptable UI Findings:`, and `LV1 Handoff Disposition:`; helper PASS, marker PASS, screenshot existence, and manifest existence cannot replace artifact-by-artifact product-vision judgment. A UTS handoff is invalid while Codex-visible visual or functional `REPAIR` / `STOP` findings remain; those must be repaired and revalidated or explicitly blocked before USER acceptance review.
Live Validation green requires an exact `## User Test Summary` state before final green.

For relevant desktop user-facing workstreams, `User-Facing Shortcut Validation Pending` and `Exact USER Desktop Launcher Proof Missing` are hard blockers before User Test Summary handoff.
Codex may use validators, live helpers, harnesses, troubleshooting launchers, or direct runtime launches for scenario coverage, but Live Validation closeout must also run the exact normal USER desktop runtime launcher path and record `User-Facing Shortcut Path:`, `Exact USER Desktop Launcher Path:`, `User-Facing Shortcut Validation: PASS`, `FAIL`, `PENDING`, or `WAIVED`, and `Exact USER Desktop Launcher Validation: PASS`, `FAIL`, `PENDING`, or `WAIVED`.
Compatibility wording: `real user-facing desktop launcher` means the exact normal USER desktop runtime launcher path declared for the branch.
If troubleshooting launcher proof is used as equivalent proof, the digest must also record `Troubleshooting Runtime Launcher Consent: GRANTED` and `Launcher Parity Proof: PASS`; otherwise troubleshooting launcher evidence remains diagnostic/supporting proof.
If that exact launcher gate or parity gate fails or remains pending, do not report final green; route back to `Workstream` or `Hardening` as appropriate.
Photo/video proof is required for visible USER-facing acceptance claims. Logs, markers, manifests, validators, Dev Toolkit events, direct runtime proof, troubleshooting launcher proof, and helper output are supporting evidence. If a required claim cannot be proven in photo/video, elevate it to USER manual validation, explicit USER waiver, or a named blocker rather than calling it proven.

When manual validation is relevant, `## User Test Summary` must be a real checklist rather than a recap.

It should include:

- setup or prerequisites
- exact user actions
- expected visible behavior
- failure signs to watch for
- branch-specific or slice-specific validation focus

For runtime or user-visible implementation slices, green validators alone do not authorize automatic continuation.

When a relevant desktop or runtime path can be launched and exercised through a real desktop session in the current environment, synthetic or headless validation does not authorize continuation on its own either.

Codex must also:

- run a deeper branch-local hardening pass against the implemented path
- add or create the smallest reliable validation infrastructure when meaningful blind spots remain
- preserve an evidence trail of the validators, harnesses, helper scripts, fixtures, runtime logs, traces, screenshots, or other validation artifacts actually used
- clean up test-session side effects such as temporary files, launched apps, helper processes, probe documents, or altered local state unless there is an intentional reason to preserve them
- enforce visible progress and a no-progress supervisor for live validation; if no tighter helper-specific watchdog is active, `10s` without meaningful progress must stop the run and report the last confirmed progress point
- use synthetic or headless validators and harnesses as supporting proof rather than the final gate when a real desktop session is feasible
- launch and exercise the exact normal USER desktop runtime path through an interactive OS-level session when applicable, or record the explicit waiver/blocker that keeps it from being formal proof
- explicitly distinguish validator results, synthetic or headless validation results, simulated reasoning, interactive OS-level execution results, and manual user-test handoff
- make an explicit next-step call between continue, harden, or corrective fix

When meaningful desktop UI changed, Codex should also:

- treat the live launched-process UI audit as a post-green closeout check rather than a per-seam screenshot requirement
- preserve the audit manifest and key captured windows in the final evidence package when closeout or readiness is being claimed
- when the user wants those screenshots to render inside the Codex client, preserve the original files on disk but default the in-chat preview path to one small inline PNG `data:` image at a time instead of local-path Markdown embeds

If that interactive path is not feasible, Codex must explain why, use the strongest available non-interactive evidence, and state that the continuation judgment is limited by the missing interactive validation.

## Phase Anchoring

Modes define collaboration posture.
Phases define the current governed lifecycle state.

For phase-sensitive work, prompts and execution records should explicitly state:

- `Mode: <mode name>`
- `Phase: <exact phase name>`
- `Workstream: <workstream id or authority record>`
- `Branch: <branch name or No Active Branch>`

When a branch is in governed closeout recovery, prompts should also state:

- `Branch Class: <branch class>`
- `Current active seam: <seam name>`
- `Validation Contract: <summary or authority reference>`
- `Timeout Contract: <summary or authority reference>`

If `Phase` is missing or is not one of the exact canonical phase names from `Docs/phase_governance.md`, execution must stop at truth-validation or analysis.

## Live-State Readiness Sanity Check

Before generating any readiness, PR, merge, or release recommendation, validate:

- current branch truth
- branch merge state
- tag or release state
- dirty worktree risk
- whether the prompt framing is stale

If the framing is stale, report the real state instead of producing a hypothetical package.

## Prompt Hygiene

When a canonical workstream or rebaseline doc exists, prompts should prefer that canonical doc over a stack of superseded slice docs.

This does not mean shrinking analysis depth.
It means reducing duplicated prompt inputs once authority is clear.

## Practical Rule Of Thumb

If the user is asking:

- what is true now
- what drift exists
- what should happen next
- whether the current branch is still the right base

start in Analysis mode.

If the user is asking:

- execute this approved docs-only phase
- implement this approved patch
- carry this approved workstream closure or canon sync

use Workflow mode.
# Current Workspace Root Override

Current root routing is owned by `Docs/nexus_workspace_roots.md`. Neutral main
is `D:\Nexus Desktop AI\Product Repository`; active worktrees are under
`D:\Nexus Desktop AI\Worktrees`, external operational state is under
`D:\Nexus Desktop AI\Governance State`, and USER review hubs are under
`D:\Nexus Desktop AI\USER`. C-drive paths retained in
historical receipts or fixtures are not current execution targets.
