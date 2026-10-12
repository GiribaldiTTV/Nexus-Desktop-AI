# Governance Process Efficiency Reform Plan

> Historical reform context and accepted evidence. This file grants no current execution authority. Current applicability follows `Docs/Main.md`, `Docs/phase_governance.md` and the selected installed external owner. Preserve dated facts as history.

## Purpose

This source-truth planning record captures a repo-wide governance and source-truth audit focused on reducing execution errors, reducing prompt/token load, and improving branch-output quality without weakening the safety gates that protect the multi-worktree workflow.

This plan is not an implementation branch by itself. It is a reform inventory for later focused planning packets and USER-approved governance passes.

## Audit Snapshot

- Audit date: 2026-05-19.
- Audit carrier: `C:\Nexus Worktrees\Governance` on `feature/release-readiness-source-truth-intake`.
- Source-truth baseline: `origin/main` at `81701d4b351ae7bb4c146daf88a8d884f6bc7981`.
- Validation baseline before recording this plan:
  - `python dev\orin_branch_governance_validation.py`: PASS, 5757 checks.
  - `python dev\orin_branch_readiness_planning_fixture_validation.py`: PASS.
  - `python dev\orin_release_body_validation.py`: PASS, 37 published pre-Beta release bodies.

## Reform Principles

- Preserve safety before speed. Any compaction must keep protections for protected `main`, Release Readiness file freeze, multi-worktree identity, pre-rebaseline audit, branch-local authority, and PR/release body firewalls.
- Reduce duplicated prose first. Repetition across `Docs/phase_governance.md`, `Docs/development_rules.md`, `Docs/codex_modes.md`, `Docs/orin_task_template.md`, `Docs/codex_user_guide.md`, and `Docs/Main.md` is the largest token-cost driver.
- Prefer small reform passes. Each category below should become a focused planning packet or branch pass instead of one broad rewrite. Exception: when USER approves a single-carrier / single-PR reform, use internal staged checkpoints on the same branch instead of forcing separate PRs.
- Keep canonical names stable until aliases are proven. User-facing aliases can reduce confusion, but validators should keep the current canonical phase enum until a deliberate rename migration is approved.
- Let validators enforce markers and let docs explain intent. Long policy paragraphs should shrink into canonical rule IDs, packet templates, and validator-backed marker sets.
- Separate derived live truth from governance receipts. Git/GitHub and approved helpers should derive volatile facts such as `HEAD`, PR state, tags, releases, dirty state, and merge base; docs should record intent, USER decisions, receipts, and historical interpretation.

## Category 1: Governance Doc Compaction

Current finding:
- The same top rules and phase contracts are repeated across multiple large docs.
- `Docs/phase_governance.md`, `Docs/development_rules.md`, `Docs/codex_modes.md`, `Docs/orin_task_template.md`, and `Docs/codex_user_guide.md` all carry overlapping versions of Pre-PR Durability, Release Readiness file freeze, Release Candidate Anchor, Pre-Rebaseline Impact Audit, Branch Readiness planning, Runtime Branch Engineering Contract, PR Readiness, and Standing Governance Intake rules.
- This makes prompts expensive and increases drift risk because a future repair can update one owner while missing another mirror.

Recommendation:
- Adopt a `Rule ID + owner + compact mirror` model.
- Keep full normative policy in `Docs/phase_governance.md`.
- Convert other docs to short pointers plus only the minimal operational fields they uniquely need.
- Add a "do not duplicate full policy prose" rule for future governance edits.

Focused planning pass:
- `Governance Doc Compaction Pass`.
- Preserve validator-required phrases until validators are updated to source-check the new IDs.

Priority:
- High.

## Category 2: Phase Naming And User-Facing Aliases

Current finding:
- Current canonical names are precise but user-heavy, especially the Stage 1 / Stage 2 pairs.

Recommendation:
- Preserve canonical phase enum for validator stability.
- Add optional user-facing aliases:
  - `Branch Readiness Stage 1` -> `Plan Review`.
  - `Branch Readiness Stage 2` -> `Setup / Admission`.
  - `Workstream` -> `Build`.
  - `Hardening` -> `Stabilize`.
  - `Live Validation` -> `User Proof`.
  - `PR Readiness Stage 1` -> `Merge Readiness Audit`.
  - `PR Readiness Stage 2` -> `PR Execution / Watch`.
  - `Release Readiness` -> `Release Validation`.
  - `Standing Governance Intake` -> `Policy Repair Lane`.

Focused planning pass:
- `Phase Alias UX Pass`.

Priority:
- Medium.

## Category 3: Packet And Digest Slimming

Current finding:
- Phase digests can become full governance restatements.
- The user usually needs changed values, blockers, validation, and next legal phase rather than a complete policy replay.

Recommendation:
- Define digest profiles:
  - `Decision Packet`: only facts needed for USER approval.
  - `Return Digest`: worktree-specific unblock packet with exact identity and next legal phase.
  - `Validation Digest`: commands, results, failures, and residual risks.
  - `Full Audit Packet`: only for explicit audit/planning requests.
  - `Delta Digest`: changed values since last accepted packet.
- Require default final responses to use the smallest legal profile that satisfies the phase.
- Keep detailed source truth in docs, not in every chat output.

Focused planning pass:
- `Digest Profile Standardization Pass`.

Priority:
- High.

## Category 4: Branch Readiness Planning Quality

Current finding:
- Recent repairs added strong Branch Readiness planning requirements and Runtime Branch Engineering Contract enforcement.
- The quality gate is good, but the required packet is now large enough that USER critique can become harder, not easier.

Recommendation:
- Split Branch Readiness planning into:
  - `Product Intent Summary`.
  - `Engineering Contract`.
  - `Decision Ledger`.
  - `Deferred/Future Ledger`.
  - `Implementation Sequence`.
  - `Proof Plan`.
- Keep validator markers, but let the user-facing packet summarize each section and link to source-truth details.
- Add a planning critique checklist focused on system shape, scope, expected user-facing behavior, and rejected shallow plans.

Focused planning pass:
- `Branch Planning UX And Template Pass`.

Priority:
- High.

## Category 5: Multi-Worktree Identity And Rebaseline Safety

Current finding:
- Identity and Pre-Rebaseline Impact Audit rules are now strong.
- Each thread still has to manually construct the same audit packet before rebaseline.

Recommendation:
- Create or extend a reusable no-mutation `dev/orin_worktree_rebaseline_audit.py` helper.
- It should output current cwd, git root, worktree role, branch, upstream, HEAD, origin/main, merge base, incoming commits, incoming changed files, local changed files, shared surface overlap, active branch record identity, current-main reconciliation identity guard recommendation, and safe operation recommendation.

Focused planning pass:
- `Worktree Rebaseline Audit Helper Pass`.

Priority:
- High.

Implementation record:
- Focused pass admitted `dev/orin_worktree_rebaseline_audit.py` as a reusable report-only helper.
- The helper emits the required `Pre-Rebaseline Impact Audit:` and `Current-Main Reconciliation Identity Guard:` markers without fetching, merging, rebasing, checking out, resetting, or mutating files.
- The helper emits `Rebaseline Mutation Approval:` and `Rebaseline Mutation Status:` so every baseline request remains report-only until USER approves mutation.
- Bot-review hardening requires incoming changed files to compare `merge_base..target_ref`, branch changed files to compare `merge_base..HEAD`, and active authority matching to use the exact `- Branch:` field instead of substring matching.
- Registry owner: `Docs/validation_helper_registry.md`.
- Validator source-check owner: `dev/orin_branch_governance_validation.py`.

### 2026-05-21 Planning Amendment - Rebaseline Overlap Intent Gate

Status:
- Implemented source-truth/helper/fixture scaffold.
- This amendment strengthens Category 5 without creating a new global live-state ledger.
- Effective point: this rule becomes binding for active or re-entering branches after the Governance reform PR merges and each active worktree rebaselines to that updated `origin/main`.
- Fallback evidence supports PASS / WARN / BLOCKED classification and USER decision-making. It does not automatically waive missing Branch Change Intent Ledger evidence.

Rule name:
- `Rebaseline Overlap Intent Gate`.

Trigger:
- Any path appears in both:
  - incoming `origin/main` changed files; and
  - current branch/worktree changed files.
- For this gate, current branch/worktree changed files means the union of:
  - branch changed files from `merge_base..HEAD`;
  - staged, unstaged, and untracked worktree files when applicable; and
  - any current-worktree changed files reported by the Pre-Rebaseline Impact Audit.
- `Rebaseline Overlap Files:` means the intersection of incoming changed files and current branch/worktree changed files. `dev/orin_worktree_rebaseline_audit.py` computes and reports this field rather than requiring Codex to manually compare two lists.

Covered surface classes:
- `governance/source-truth`
- `runtime`
- `desktop/UI`
- `Core visual`
- `validator/helper`
- `fixture/test`
- `configuration/state/schema`
- `release/public-output`
- `prompt/template`
- `automation/watcher`
- `build/packaging`
- `documentation/reference`
- `asset/media`

Required active owner:
- `C:\Nexus Governance State\branches\<branch_slug>\branch_plan.md` owns active full-detail change intent while the branch is active.
- Runtime branches use the Branch Runtime Engineering Plan shape. When a non-runtime branch has `Rebaseline Overlap Files:`, an active external Branch Engineering Plan under `C:\Nexus Governance State\branches\<branch_slug>\branch_plan.md` must be admitted or updated as the active change-intent owner before rebaseline mutation can proceed, using the smallest source-truth-supported branch-plan variant.
- The branch authority record owns compact authority/receipt status and fold-down evidence after PR Readiness decides what should survive.
- Workstreams and family dossiers own reusable or historical implementation lessons after fold-down.
- Backlog, roadmap, worktree slots, and `Docs/Main.md` remain compact pointer/routing surfaces, not overlap ledgers.

Required branch-plan section:

```text
## Branch Change Intent Ledger
```

Required repeatable block:

```text
### Changed Surface: <path>
Surface Class:
Change Intent:
Why This File Was Touched:
Owned Behavior / Fact Class:
Canonical Owner / Source Owner:
Resolution Owner:
Shared Surface:
Overlap Risk:
Expected Conflict Risk:
Semantic Merge Risk:
Regression / Gating Impact:
Conflict Resolution Rule:
Rebaseline Handling:
Validation Proof:
Fallback Evidence:
USER Decision / Waiver:
Fold-Down Target:
```

Allowed values:
- `Semantic Merge Risk:` uses `None`, `Low`, `Medium`, `High`, or `Unknown`. For high-risk surface classes, `Unknown` classifies as BLOCKED until evidence or USER decision resolves it.
- `Regression / Gating Impact:` uses `None`, `Low`, `Medium`, `High`, or `Unknown`. For fixture/test overlap, `Medium`, `High`, or `Unknown` blocks until evidence or USER decision resolves validator truth, regression coverage, or release-gating impact.
- `Resolution Owner:` uses `Current Branch`, `Incoming/Folded Owner`, `Originating Lane`, `Standing Governance`, `USER Decision`, or `Future Branch`.

Rebaseline Overlap Failure Procedure:
- Procedure name: `Rebaseline Overlap Failure Procedure`.
- Trigger: an overlapping changed file has missing, weak, stale, or conflicting intent evidence.
- First action: freeze rebaseline mutation and return a packet.
- The packet classifies every overlapping file as PASS, WARN, or BLOCKED.

Severity model:
- PASS: branch-owned intent evidence exists, incoming/current intent aligns with source-truth ownership, and required validation is named.
- WARN: lower-risk surface, partial intent evidence, fallback evidence supports a USER-visible recommendation, and the packet names the risk.
- BLOCKED: high-risk surface lacks intent evidence, incoming/current intent conflicts, accepted behavior changes, source-truth ownership changes, validation rules change, runtime behavior changes, UI behavior changes, config/schema/state changes, public release meaning changes, or approval boundaries change.
- Named blocker: `Rebaseline Overlap Intent Missing`.
- `Rebaseline Overlap Intent Missing` applies when an overlapping changed file lacks required Branch Change Intent evidence, has conflicting intent, or needs USER decision before mutation.
- After the Effective Point, fallback evidence alone cannot produce PASS. PASS requires branch-owned change-intent evidence. Fallback evidence may support WARN or help classify BLOCKED items for USER decision.
- Overall Overlap Gate Result is the highest per-file severity. Any BLOCKED file keeps `Rebaseline Mutation Status:` blocked until the blocker is repaired, waived, deferred by USER decision, or sequencing changes.

High-risk classes default to BLOCKED when intent evidence is missing or contradictory:
- `runtime`
- `desktop/UI`
- `Core visual`
- `governance/source-truth`
- `validator/helper`
- `configuration/state/schema`
- `automation/watcher`
- `release/public-output`
- `build/packaging`

Lower-risk classes may use WARN when fallback evidence is sufficient:
- `documentation/reference`
- `asset/media`
- `fixture/test` only when non-executing and not changing validator truth, regression coverage, or release gating.
- `documentation/reference` is lower-risk only when the file is not a source-truth owner, prompt/template owner, validator/helper owner, branch record, branch plan, backlog/roadmap owner, or governance policy owner.

Required failure packet:

When `Rebaseline Overlap Files:` is `None`, this gate reports `Not Applicable`; the normal Pre-Rebaseline Impact Audit and USER-approved mutation path still apply.

```text
Overall Overlap Gate Result:
Rebaseline Overlap Files:
Overlapping Files:
File:
Surface Class:
Incoming Change Summary:
Current Branch Change Summary:
Branch Change Intent Present:
Incoming Intent Evidence Present:
Fallback Evidence:
Regression / Gating Impact:
Risk:
Per-File Result: PASS / WARN / BLOCKED
Recommended Resolution:
Resolution Owner:
Validation Required:
USER Decision Needed:
Rebaseline Mutation Status:
```

Fallback evidence sources:
- active external branch plan
- branch record
- PR body when available
- commit messages
- git diff
- source-owner markers
- source-truth owner lookup from `Docs/Main.md` or the relevant owner index
- validation helper registry
- workstream or family dossier
- relevant fixtures/tests
- release notes or public-output record when release/public-output files overlap

Resolution paths:
- Add missing Branch Change Intent Ledger entry on the current branch when the current branch is the legal carrier.
- Adding a missing Branch Change Intent Ledger entry is blocker repair before mutation. It does not authorize rebaseline mutation until validation passes and USER approves the rebaseline operation.
- After any overlap-intent repair, rerun the overlap gate and required validation before requesting or executing the rebaseline mutation.
- Request originating-lane evidence when incoming `origin/main` contains a sibling branch change whose intent is not represented.
- Prepare a manual reconciliation patch only after USER approval.
- Return a Branch Plan Revision Packet when the overlap changes accepted branch scope.
- Defer rebaseline until sibling branch/PR sequencing is resolved.
- Route to standing Governance when the current branch cannot legally own the repair.

Implemented and future-extension targets:
- `Docs/governance_process_efficiency_reform_plan.md`
- `Docs/branch_plans/README.md`
- `Docs/phase_governance.md`
- `Docs/governance_efficiency_operating_model.md`
- `Docs/orin_task_template.md`
- `Docs/validation_helper_registry.md`
- `Docs/branch_records/index.md` if future compact fold-down receipt wording is needed
- `dev/orin_branch_governance_validation.py`
- `dev/orin_governance_efficiency_validation.py`
- `dev/orin_branch_readiness_planning_fixture_validation.py`
- `dev/orin_worktree_rebaseline_audit.py`
- branch-readiness planning fixtures cover:
  - valid overlap intent;
  - invalid missing high-risk intent;
  - invalid fallback-only PASS after the Effective Point; and
  - valid low-risk WARN with fallback evidence;
  - fixture/test high regression or gating impact; and
  - fixture/test low regression or gating impact.
- `dev/orin_worktree_rebaseline_audit.py` computes and reports `Rebaseline Overlap Files:` from incoming files intersected with branch/worktree changed files and parses branch-plan ledger evidence through `--branch-plan-path` or branch-plan resolution.

Implementation guard:
- Do not implement this as backlog, roadmap, worktree-slot, or `Docs/Main.md` live-state tracking.
- Do not add backward-compatibility bypass language. After the merged reform baseline is adopted, future active or re-entering branches must carry overlap intent evidence or stop on the failure procedure.
- Historical branches and branch records remain receipts only; this amendment controls active/re-entering branch behavior after the Effective Point.
- Marker-first blocking applies to missing, stale, weak, or conflicting required overlap-intent markers. Natural-language semantic conflict detection beyond the required packet fields remains pending USER approval.

## Category 5A: Source-Truth Ownership And Worktree Slot Model

Current finding:
- The repo has moved from one neutral folder to a multi-worktree workflow, but old language can make current FAM worktrees look like permanent structural lanes.
- Backlog and roadmap carry too many current-state mirrors, while Git/GitHub already own many volatile operational facts.
- Without a stable slot model, branch identity, GitHub Desktop binding, and originating-lane prompts can drift between current family labels and actual worktree roles.

Recommendation:
- Adopt `Docs/worktree_slots.md` as the slot registry and intended assignment layer.
- Use stable slot IDs: `neutral-main`, `governance-standing`, `runtime-active-1`, `runtime-active-2`, `runtime-active-3`, and `archived-historical`.
- Make the slot registry own intended assignment receipts, not raw live Git facts.
- Keep branch authority records as the legal source for active, historical, blocked, waiting, and next-phase posture.
- Keep Branch Runtime Engineering Plans canonical while runtime branches are active, then fold down or promote them during PR Readiness.

Focused planning pass:
- `Source-Truth Ownership And Worktree Slot Model Pass`.

Priority:
- High.

Implementation record:
- Focused pass admitted `Docs/worktree_slots.md` as the stable worktree slot registry.
- `Docs/Main.md` now distinguishes derived live truth from governance receipts and routes worktree slot ownership through `Docs/worktree_slots.md`.
- `Docs/branch_records/index.md` records that slot assignment does not equal active branch authority.
- Marker-first helper/validator enforcement is implemented for worktree slot routing, Pre-Rebaseline Impact Audit, Rebaseline Overlap Files, Branch Change Intent Ledger evidence, backlog/roadmap compact-pointer posture, and duplicate live-state sprawl where source truth is machine-checkable. Broad historical rewrites, destructive file deletion, and natural-language semantic conflict blocking remain separate USER-approved reform passes.

## Category 6: Standing Governance Intake Simplification

Current finding:
- The standing Governance branch now correctly avoids closeout-only PRs.
- Remaining complexity comes from RRI cycle wording, return digest identity, neutral main rebaseline proof, and historical ledger text.

Recommendation:
- Move detailed historical RRI cycle entries into a compact ledger table or appendix.
- Keep the active record focused on active cycle, latest closed cycle, allowed intake source, sync status, return digest status, and next legal phase.
- Preserve validator enforcement for one-active-cycle and return digest identity.

Focused planning pass:
- `Standing Governance Ledger Compaction Pass`.

Priority:
- Medium-high.

## Category 7: PR Watcher And Bot-Review Repair Loop

Current finding:
- Governance requires watchers and same-PR bot-review repair, but the actual user experience still feels unreliable.
- When automation delivery is quiet, the user cannot tell whether the watcher is idle, stuck, or lacking actionable data.

Recommendation:
- Standardize watcher modes:
  - `Silent Monitor`.
  - `Verify Once`.
  - `Repair Mode`.
  - `Blocked Mode`.
- Add a watcher health proof line to PR Readiness Stage 2 final handoff with configured cwd, PR number, head SHA, unresolved thread count, latest bot review time, repair authority status, and delivery route proof.
- Consider a local watcher helper enhancement before relying only on native heartbeat text.

Focused planning pass:
- `Watcher Reliability And Repair-Mode Pass`.

Priority:
- High.

Implementation record:
- Focused pass admitted `Docs/pr_watcher_mode_contract.md` as the compact PR Watcher Mode Contract.
- The standard defines `Silent Monitor`, `Verify Once`, `Repair Mode`, and `Blocked Mode` so quiet watcher behavior, one-time proof, safe same-PR repair, and no-patch blockers are no longer ambiguous.
- The required `Watcher Health Proof:` line records configured cwd, PR number, head SHA, unresolved review-thread count, latest bot review, repair authority, delivery route proof, runtime proof, and next watcher posture only for a USER-approved watcher exception or historical watcher receipt.
- Follow-up approval-default repair clarifies that USER approval for PR Readiness Stage 2 / PR creation does not include recurring PR watcher automation by default. Codex must use direct PR verification unless USER explicitly approves a named watcher exception for the exact PR.
- Validator source-check owner: `dev/orin_branch_governance_validation.py`.

## Category 8: Validator Modularization

Current finding:
- `dev/orin_branch_governance_validation.py` is the enforcement center and is very large.
- The breadth is useful, but small repairs are harder to review safely.

Recommendation:
- Split the monolith into internal modules without changing the command interface:
  - phase/base parser utilities.
  - branch authority checks.
  - worktree/rebaseline gates.
  - standing governance intake gates.
  - runtime planning contract gates.
  - PR readiness gates.
  - release readiness gates.
  - historical/source-truth migrations.
- Keep `dev/orin_branch_governance_validation.py` as the stable CLI wrapper.

Focused planning pass:
- `Governance Validator Modularization Pass`.

Priority:
- Medium-high.

## Category 9: Source-Truth Volume And Historical Archiving

Current finding:
- Several branch records mix current state, historical evidence, issue ledgers, release details, and long narrative.
- This preserves evidence but increases routine context size.

Recommendation:
- Adopt a current-state / historical-appendix split:
  - top 100-200 lines: current truth and machine markers.
  - appendix or closeout doc: detailed historical narrative and proof.
- For very large branch records, create compact current-summary sections that validators prefer.

Focused planning pass:
- `Source-Truth Archive And Current-State Split Pass`.

Priority:
- High, but risky.

## Category 10: Release Readiness Scope And Release Ownership

Current finding:
- Release Readiness is file-frozen and validates current `origin/main` by default.
- Multi-FAM merged-unreleased windows can still confuse who owns the release when FAM-006 and FAM-007 merge close together.

Recommendation:
- Add a `Release Captain / Release Assembler` concept for release execution:
  - it does not own implementation.
  - it packages the aggregated release window.
  - it lists all contributing PRs/FAMs.
  - it cannot mutate source truth during Release Readiness.
- Keep aggregated release window as default when current `origin/main` contains multiple unreleased contributors.

Focused planning pass:
- `Release Ownership UX Pass`.

Priority:
- Medium.

## Category 11: Helper Registry And Validation Runner

Current finding:
- `Docs/validation_helper_registry.md` is strong but dense.
- Validator command lists vary by branch and phase.

Recommendation:
- Add a lightweight validation runner or registry query helper:
  - input: phase, branch family, changed files.
  - output: recommended validator list and rationale.
  - no mutation.
- Split helper registry into families only if validators can still find canonical helper status.

Focused planning pass:
- `Validation Runner And Registry Query Pass`.

Priority:
- Medium.

Implementation record:
- Focused pass admitted `dev/orin_validation_suite.py` as a reusable report-only validation suite recommendation helper.
- The helper emits `Recommended Validation Suite:` packets from `--phase` and `--changed-file` inputs, recommends commands with rationale, and does not execute commands or mutate files.
- Registry owner: `Docs/validation_helper_registry.md`.
- Validator source-check owner: `dev/orin_branch_governance_validation.py`.

## Category 12: Backlog And Roadmap Current-State Clarity

Revised status:
- Superseded / revised by the Source-Truth Ownership and Derived Live Truth reform. Backlog and roadmap should not own duplicated live-state decision surfaces. They may carry compact status and owner pointers, while Git/GitHub/helpers derive live operational truth and branch/release receipts preserve validated historical interpretation.

Current finding:
- `Docs/feature_backlog.md` and `Docs/prebeta_roadmap.md` carry current state, release history, selected-next posture, and future candidates in dense prose.

Revised recommendation:
- Keep `Docs/feature_backlog.md` as a compact product registry and pointer layer.
- Keep `Docs/prebeta_roadmap.md` as a release-stage breakpoint schedule outline and public milestone posture surface.
- Do not preserve duplicated backlog/roadmap live-state blocks for latest release, merged-unreleased PRs, active branch, worktree state, release blockers, or next legal phase.
- Route volatile facts to Git/GitHub/helpers, route branch authority and selected-next/no-active decisions to branch records, and route validated historical release interpretation to structured receipts.
- Move longer historical explanation below its owning receipt, branch record, workstream doc, or family dossier.

Focused planning pass:
- Historical: `Backlog/Roadmap Current Decision Surface Pass`.

Priority:
- Medium-high.

Implementation record:
- Historical note: an earlier focused pass admitted compact `## Current Decision Surface` blocks in `Docs/feature_backlog.md` and `Docs/prebeta_roadmap.md`.
- Current reform supersedes that future model. Any remaining backlog/roadmap current-summary fields are transitional compact pointers only, not preferred live-state owners.
- Future implementation should replace duplicated live-state fields with owner pointers, helper-derived reports, and branch/release receipts before treating backlog or roadmap as green for source-truth efficiency.
- Validator source-check owner: `dev/orin_branch_governance_validation.py`.

## Category 13: Naming And Product Identity Drift

Current finding:
- Product/persona naming governance is strict, but legacy names can still surface in old docs, runtime artifacts, validator fixtures, or generated outputs.

Recommendation:
- Keep external GitHub release/tag history as historical.
- Add a future repo-wide naming drift scan helper only when USER approves a naming cleanup carrier.
- Do not mix naming migration into runtime branches unless the branch owns the affected user-facing surface.

Focused planning pass:
- `Tracked Naming Drift Scan Pass`.

Priority:
- Medium.

## Category 14: Governance Repair Intake Triage

Current finding:
- The standing Governance branch can accept Release Readiness digests, automation/worktree governance intake, and phase-gate governance intake.
- Broad governance requests risk becoming too large.

Recommendation:
- Add a `Governance Intake Triage Packet` before every non-Release-Readiness governance reform:
  - problem class.
  - source-truth support.
  - smallest safe repair.
  - files likely affected.
  - validator/helper impact.
  - whether a PR is needed.
  - whether the repair should instead ride an active runtime branch.
- This current document can serve as the parent inventory for focused triage packets.

Focused planning pass:
- `Governance Intake Triage Template Pass`.

Priority:
- High.

## Category 15: Public Output Standards

Current finding:
- PR body and release body standards are much better now.
- The next risk is overexplaining public release notes with internal governance repair names.

Recommendation:
- Keep release bodies user-facing and avoid internal process names unless needed for transparency.
- Add public-language mapping from Engineering Contract to release notes:
  - internal scope.
  - user-visible benefit.
  - excluded/future-gated work.
  - validation confidence.
- Add a release-body dry-run preview before release execution when the release window has governance-heavy PRs.

Focused planning pass:
- `Public Language Mapping Pass`.

Priority:
- Medium.

## Recommended Reform Sequence

1. `Governance Intake Triage Template Pass`.
2. `Digest Profile Standardization Pass`.
3. `Worktree Rebaseline Audit Helper Pass`.
4. `Source-Truth Ownership And Worktree Slot Model Pass`.
5. `Watcher Reliability And Repair-Mode Pass`.
6. `Governance Doc Compaction Pass`.
7. `Branch Planning UX And Template Pass`.
8. `Source-Truth Archive And Current-State Split Pass`.
9. `Governance Validator Modularization Pass`.
10. `Backlog/Roadmap Current Decision Surface Pass`.
11. `Release Ownership UX Pass`.
12. `Validation Runner And Registry Query Pass`.
13. `Phase Alias UX Pass`.
14. `Standing Governance Ledger Compaction Pass`.
15. `Public Language Mapping Pass`.
16. `Tracked Naming Drift Scan Pass`.

## Consolidated Governance Reform Pass

USER later approved completing the remaining governance reform categories in one bounded Governance PR instead of separate focused PRs.

This consolidated pass completes the policy and validation scaffolding for:

- `Governance Doc Compaction Pass`
- `Phase Alias UX Pass`
- `Branch Planning UX And Template Pass`
- `Standing Governance Ledger Compaction Pass`
- `Governance Validator Modularization Pass`
- `Source-Truth Archive And Current-State Split Pass`
- `Release Ownership UX Pass`
- `Public Language Mapping Pass`
- `Tracked Naming Drift Scan Pass`

Implementation record:

- `Docs/governance_efficiency_operating_model.md` owns the Rule ID / owner / compact mirror model, source-truth ownership matrix, derived live truth versus governance receipt boundary, duplicate live-state guard, current-summary / historical-appendix split, phase alias UX, branch planning UX, standing-governance ledger compaction, release ownership UX, public language mapping, validator modularization boundary, validation-suite usage, naming drift scan rule, and consolidated pass completion boundary.
- `dev/orin_governance_efficiency_validation.py` validates the operating model, owner-doc pointers, and backlog/roadmap compactness against Branch Runtime Engineering Plan sprawl.
- `Docs/Main.md`, `Docs/phase_governance.md`, `Docs/development_rules.md`, and `Docs/codex_modes.md` carry compact pointers instead of duplicating the full operating model.
- `Docs/validation_helper_registry.md` registers the reusable governance efficiency validator.

Explicit non-scope:

- No broad historical branch-record migration.
- No backlog/roadmap shrink migration beyond compactness enforcement.
- No runtime implementation.
- No FAM-006 or FAM-007 mutation.
- No branch deletion, worktree cleanup, issue work, release execution, tag, GitHub Release, or artifact work.

Post-merge operating rule:

- Future governance efficiency changes should first use `Docs/governance_efficiency_operating_model.md` and `dev/orin_governance_efficiency_validation.py` before creating another live-state owner or duplicating policy prose.

## Highest-Value First Pass - Historical / Completed

Status:
- Historical recommendation; the implementation record below supersedes this as an active next-step recommendation.

Recommended first focused pass:

`Governance Intake Triage Template Pass` plus `Digest Profile Standardization Pass`.

Why:
- It is low-risk and documentation-first.
- It immediately narrows future governance requests.
- It reduces token usage before touching the huge docs or validator.
- It gives each later reform category a standard decision packet.

Suggested acceptance criteria:
- A reusable triage packet exists in source truth.
- Digest profiles are named and scoped.
- Future governance reform prompts can cite a category from this plan instead of restating all details.
- No phase enum rename, validator split, source-truth archival, or runtime work is attempted in the first pass.

Implementation record:
- First focused pass admitted: `Docs/governance_intake_triage_and_digest_profiles.md`.
- Governance source-truth pointers added to `Docs/phase_governance.md`, `Docs/development_rules.md`, `Docs/codex_modes.md`, `Docs/orin_task_template.md`, `Docs/Main.md`, `Docs/branch_records/index.md`, and `Docs/validation_helper_registry.md`.
- Validator source-check owner: `dev/orin_branch_governance_validation.py`.

## Remaining External Execution Decisions

The consolidated pass records the governance model. After the deferred-reform completion pass, these work classes remain outside this governance/source-truth cleanup and still require separate USER approval:

- large historical branch-record migration or archival
- direct modular split of `dev/orin_branch_governance_validation.py`
- branch deletion, stale worktree cleanup, or GitHub Desktop cleanup
- runtime/FAM branch mutation
- release execution or public release publication

Resolved by prior or consolidated reform passes:

- phase aliases are explanatory only; canonical phase names remain unchanged
- validation runner recommendation helper exists as `dev/orin_validation_suite.py`
- watcher approval default and watcher mode contract are recorded
- governance efficiency operating model exists as `Docs/governance_efficiency_operating_model.md`
- `Docs/nexus_vision.md` is the project-wide Nexus Vision contract after reference migration from the former `Docs/orin_vision.md` path
- `Docs/family_visions/` exists as the durable family vision owner layer
- `Docs/branch_plans/retirement_index.md` records historical branch-plan retirement posture without deleting useful planning evidence

## USER Review Intake - 2026-05-21

Scope:
- Analysis-only intake for the full Docs source-truth reform review surface.
- Preserve USER review responses from `Docs/governance_docs_reform_user_review_index.md` in this durable planning/model record so the generated review index can be regenerated safely.
- Update the model for this branch's execution without deleting, renaming, archiving, or broadly migrating Docs files in this pass.

USER response integration matrix:

| USER response requirement | Governance interpretation | Model decision | Owner files | Execution effect on this branch | Validator/helper implication |
| --- | --- | --- | --- | --- | --- |
| Complete the remaining reform in staged internal work on this same Governance carrier and one final PR; avoid revolving PRs. | The reform should not become a sequence of small PRs that each leave drift for the next one. | Keep the current carrier as the single reform branch and use internal commits/stages until USER accepts the complete cleanup. | This plan, `Docs/governance_docs_full_inventory_reform_audit.md`, `Docs/governance_docs_reform_user_review_index.md`. | The review packet must show a staged execution plan and must not present PR creation as the next automatic step while USER is still correcting the model. | `dev/orin_governance_efficiency_validation.py` must require the generated dossier/index to expose the user-response integration and single-PR staged execution sections. |
| `Docs/Main.md` should be the least-updated canonical docs index and pointer ledger. | Main is a recovery map and canonical owner index, not a live operations diary. | Main routes to owner docs and explains purpose; context docs preserve evidence and detail. | `Docs/Main.md`, `Docs/governance_efficiency_operating_model.md`. | The cleanup plan must avoid adding live branch/release/current-state ledgers to Main and must flag future Main edits that duplicate owner content. | Governance efficiency validation keeps Main as pointer/routing surface and checks for the operating model pointer. |
| Use a clearer canonical docs versus context docs model. | Some files are law/routing owners; others are evidence/history/reasoning owners. | Add canonical/context taxonomy to the model and dossier so files are not judged only by size. | Operating model, audit dossier, review index. | The file-by-file review must classify each file by owner role and disposition rather than only "keep/delete." | The docs inventory helper must generate owner category, action, consolidation target, ambiguity risk, and structure risk per file. |
| Branch plans should fold down and be retired, not deleted by default. | Planning evidence has value after merge, but it must stop acting like active authority. | Branch plans are canonical only while active; after PR Readiness they fold down, migrate durable content, and get explicit retired posture unless USER later approves deletion. | `Docs/branch_plans/README.md`, operating model, branch record index, audit dossier. | The review packet must list branch plans as fold-down/retirement candidates, not automatic delete candidates. | Planning fixture/governance efficiency validation should preserve fold-down/retirement wording and reject stale active plan authority. |
| Branch receipts may be large for traceability. Compaction for traceability is bad. | The defect is duplicate live state and poor organization, not evidence volume. | Branch records become structured traceability receipts: current summary, indexed historical sections, commit/PR/release evidence, changed-surface map, validation proof, and pointers to promoted durable owners. | `Docs/branch_records/index.md`, operating model, audit dossier. | Large branch records are organized or queued for organization, not blindly compressed. Evidence needed for future bug/rollback analysis is preserved. | Validator wording must distinguish "sprawl/live-state duplication" from legitimate historical receipt evidence. |
| Safe files should be deleted when proven safe or collapsed into current tracked files. | Delete/retire decisions require reference scan, replacement owner, and USER acceptance when ambiguous. | Every Docs file gets a disposition row: keep, organize, migrate, retire, delete candidate, or USER decision needed. | Audit dossier and generated review index. | The branch may identify delete/retire candidates now, but ambiguous deletion stays deferred until USER review. | Inventory helper must keep a full cleanup/disposition table and retirement/delete candidate table. |
| `Docs/nexus_vision.md` should become/reframe as Nexus Vision and drive planning. | Product vision should be a durable product contract, not a branch execution plan. | Product Vision Contract model implemented: vision drives backlog planning and Branch Readiness recommendations; branch plans explain implementation/proof. | `Docs/nexus_vision.md`, operating model, audit dossier. | Reference migration completed from the former `Docs/orin_vision.md` path. | Validation prevents stale path references and keeps vision out of branch-plan implementation detail. |
| Each backlog family may need USER-reviewed vision discussion. | Family vision belongs above branch plans and should shape plan recommendations. | Backlog points to `Docs/family_visions/` owners without absorbing long vision/planning narratives. | Backlog, roadmap, family vision records, operating model. | Family vision owner layer created and linked from backlog/roadmap. | Backlog sprawl checks allow compact vision pointers, not full branch planning. |

Corrected analysis:
- The earlier review surface underweighted the USER responses because it recorded them as a receipt, not as requirements that reshape the model. This section is the durable correction.
- The prior "delete branch plans after fold-down" wording was too aggressive and could lose useful planning evidence. The corrected model is "fold down, migrate durable content, then retire by explicit posture"; deletion requires separate USER approval.
- The prior "compact branch receipt" wording was too easy to misread as "make traceability small." The corrected model is "structured branch receipt": current summary first, indexed historical sections, commit/PR/release evidence, changed-surface map, validation proof, and promoted reusable lessons.
- Main should become more canonical and less operational. It should point to owners and explain the file system, while specific policy, branch, plan, workstream, and vision surfaces carry their own detail.
- The Docs reform should separate information by job: canonical index, policy owner, branch ledger, active plan, workstream/family history, product vision, and generated review/audit surface.
- The generated review index should not be the durable home for raw USER responses because it is regenerated by helper. This plan is the durable intake home, and the generated dossier/index must summarize how the responses changed the model.

Single-PR staged execution plan for this branch:

| Stage | Name | Purpose | Allowed work | Completion proof |
| --- | --- | --- | --- | --- |
| R1 | User-response model correction | Turn USER responses into model decisions instead of passive notes. | Update this plan, operating model, generated dossier/index, and validator-required sections. | Dossier/index contain `USER Response Integration Matrix`, `Single-PR Staged Execution Plan`, and `Disposition Changes From USER Review`. |
| R2 | Canonical/context taxonomy | Make Main the least-updated canonical docs index and classify context docs. | Update ownership model and file-by-file dossier language; no broad file deletion. | Every Docs file has owner category, action, migration target, ambiguity risk, and structure risk. |
| R3 | Backlog/roadmap enforcement model | Keep backlog as product registry/pointers and roadmap as release-stage breakpoint outline. | Harden generated schemas and validators; migrate only safe duplicated planning text already approved. | Backlog/roadmap sprawl checks stay green. |
| R4 | Branch plan lifecycle model | Keep detailed active planning but prevent stale active authority after completion. | Fold-down/retirement rules and candidate queues; no deletion without USER review. | Branch plan candidates appear as retirement candidates, not automatic deletion. |
| R5 | Structured branch receipt model | Preserve traceability without duplicate live-state chaos. | Define receipt schema and queue high-risk records for organization. | High-risk/structure queues identify oversized records and their organization action. |
| R6 | Vision contract implementation | Treat `Docs/nexus_vision.md` as the Nexus Vision contract and `Docs/family_visions/` as the family vision owner layer. | Reference migration, Nexus Vision reframe, and family vision creation completed. | Operating model and dossier carry Product Vision Contract language. |
| R7 | Safe file disposition review | Identify keep/collapse/migrate/retire/delete posture for every Docs file. | Generate full disposition table and USER decision list. | Manifest count matches filesystem enumeration and every file has a review row. |
| R8 | Validator and review-surface hardening | Make the corrected review model regeneration-safe. | Update helper/validator sections and regenerate audit/index. | Validation passes and generator output is stable. |
| R9 | Final USER review hold | Stop before PR Readiness until USER accepts the complete reform surface. | Report results only. | Next legal phase remains USER review, not PR creation by inertia. |

Disposition changes from USER review:
- Branch plans: from "delete after PR Readiness" to "fold down, migrate durable content, then retire by explicit posture; delete only with separate USER approval."
- Branch records: from "compact receipts" to "structured traceability receipts that may remain large when they are the correct ledger."
- Main: from "general source-truth doc" to "least-updated canonical docs index and recovery map."
- Backlog: from "current status plus detailed trace" to "compact product registry, status, family scope, package summary, and pointers."
- Roadmap: from "release/current-state record" to "release-stage schedule outline, public milestone posture, and broad feature breakpoints."
- Vision: from "low-risk product reference" to "Nexus Vision contract plus family vision records that drive backlog and branch planning."
- Safe/low-risk docs: from "safe to leave" to "reference-scan before delete/collapse, with replacement owner recorded."

Deferred decisions:
- Whether to create a global governance/source-truth file index beyond the generated dossier and existing `Docs/Main.md`.
- Which historical branch plans should be deleted after retirement proof and reference scans.
- Which oversized branch records should be reorganized first into structured receipt format.
- Which low-risk reference docs should be deleted, collapsed, or retained.

## Vision Contract Implementation Checkpoint - 2026-05-21

Scope:
- Implement the approved Vision Contract / Vision-to-Plan governance model on this Governance carrier.
- Keep implementation limited to source-truth rules, branch-plan lifecycle updates, packet templates, assumption decision-state markers, USER Vision Green markers, fixture examples, and validator/helper scaffolding.
- Nexus Vision rename/reframe and broad family vision file creation are implemented in the deferred-reform completion pass. PR creation, merge, runtime work, FAM-006/FAM-007 mutation, release work, issue work, branch cleanup, and destructive historical deletion remain separate USER decisions.

Implementation model:
- Vision Contract complements the Branch Runtime Engineering Plan rather than replacing it.
- Nexus Vision remains the project-wide product intent layer at `Docs/nexus_vision.md`; family vision lives under `Docs/family_visions/` when feature-family direction is broad enough to justify durable ownership.
- Branch Vision Contract Snapshot belongs inside the active external branch plan so accepted branch-specific vision is close to the seams, files, validators, and proof it governs.
- Codex and ChatGPT recommendations remain proposed until USER accepts, revises, rejects, defers, waives, or supersedes them.
- `USER Vision Green: Yes` is the Workstream continuity lock: after it is recorded, Codex continues on the accepted plan unless a Level 2 seam-blocking or Level 3 workstream-breaking question appears.
- New design questions during Workstream should be classified as Level 1 non-blocking, Level 2 seam-blocking, or Level 3 workstream-breaking so implementation does not churn on harmless questions or silently ignore blocking ones.

Validator/helper posture:
- `dev/orin_branch_governance_validation.py` now carries reusable Branch Vision Contract Snapshot validation scaffolding.
- `dev/orin_branch_readiness_planning_fixture_validation.py` proves valid accepted vision, invalid proposed-only assumptions, and invalid blocking open vision questions through fixtures.
- Heavy enforcement against historical branch records remains deferred so old receipts are not broken by a new model.

## USER Feedback Disposition Implementation Plan - 2026-05-21

Status:
- Planning Status: `Implemented source-truth scaffold and historical planning record`.
- Implementation Status: `Marker-first governance scaffolding implemented on 2026-05-21; multi-item ledger repair implemented on 2026-05-21; exact-normalized duplicate Feedback Summary blocking and branch-plan retirement-index enforcement implemented in deferred-reform completion; broader fuzzy semantic duplicate detection remains human-review territory unless future fixtures prove it safe`.
- This section records the recommended model, implementation targets, and implementation record. It does not by itself authorize Codex to mutate branch plans, create new UFD records outside an approved branch plan, rename files, or treat proposed feedback as accepted branch scope.
- Future Codex packets should treat this section as planning evidence and implementation history; binding UFD guidance lives in the owning governance docs, templates, fixtures, and validators updated by the implementation commit.

Scope:
- Maintain the USER Feedback Disposition model and its implemented marker-first source-truth scaffold.
- Preserve meaningful USER feedback without creating another permanent feedback ledger.
- Keep new UFD items branch-plan-owned unless USER separately approves a specific branch plan or source-truth disposition pass.
- Preserve repo naming / governance taxonomy reform planning so feedback IDs, phase labels, workstream labels, and file names stay easy for USER, ChatGPT, and Codex to call consistently.

Implemented and future-extension target files:
- `Docs/branch_plans/README.md`
- `Docs/phase_governance.md`
- `Docs/governance_efficiency_operating_model.md`
- `Docs/validation_helper_registry.md`
- `Docs/nexus_startup_contract.md` (compact owner pointer only; it owns ChatGPT-generated Codex prompt-gate wording and loader/startup continuity)
- `Docs/codex_user_guide.md` (future USER-facing explanation/examples only)
- `Docs/orin_task_template.md` (future prompt-template field examples only)
- `dev/orin_branch_governance_validation.py`
- `dev/orin_branch_readiness_planning_fixture_validation.py`
- `dev/orin_governance_efficiency_validation.py`
- `dev/fixtures/branch_readiness_planning/<ufd_valid_or_invalid_fixture>.md`

Recommended model:
- Active full-detail feedback belongs in the active external Branch Runtime Engineering Plan at `C:\Nexus Governance State\branches\<branch_slug>\branch_plan.md`.
- The active external branch plan owns one UFD ledger with `UFD Ledger Status:`, `UFD Ledger Owner:`, `Open UFD Count:`, `Blocking UFD Count:`, and `Fold-Down Status:` at section level.
- Each meaningful feedback item lives in a repeatable `### UFD Item: UFD-<scope>-YYYYMMDD-NNN` block.
- Every meaningful USER feedback item should have one stable ID, one full-detail active owner, one disposition state, one USER decision state, one current/future branch impact classification, and one fold-down target.
- Branch records carry compact feedback status and a pointer to the active external branch plan.
- Backlog carries compact future-candidate pointers only after USER accepts the future-work disposition.
- Roadmap carries no feedback detail unless the accepted feedback changes release-stage breakpoint or public milestone sequencing.
- Worktree slots carry no feedback detail.
- Nexus Vision and family vision/family dossier owners receive only accepted reusable standards, not branch-local unresolved feedback.
- Workstream docs and family dossiers receive folded durable outcomes, proof history, branch lessons, package trace, slice trace, and reusable continuity during PR Readiness fold-down.
- Pointer locations may carry UFD ID, short title, canonical owner, compact status, and fold-down status only; they should not carry full feedback text, full decision history, or live implementation state.

Feedback ID recommendation:
- Use `UFD-<scope>-YYYYMMDD-NNN` for USER Feedback Disposition IDs.
- Do not use `FBK-*`; it collides visually with historical `FB-###` records and could be misread as a backlog identity.
- Scope examples: `UFD-FAM006-20260521-001`, `UFD-FAM007-20260521-001`, `UFD-GOV-20260521-001`, `UFD-NEXUS-20260521-001`.
- The ID is the compact pointer used by branch records, backlog, roadmap, workstreams, family dossiers, and PR fold-down receipts. Full feedback text should not be copied into each pointer location.
- UFD IDs remain valid after branch-plan fold-down and retirement. The fold-down receipt becomes the lookup path from the UFD ID to the final owner.

Meaningful feedback threshold:
- Not every USER comment becomes a UFD item.
- UFD disposition is required when USER feedback affects branch scope, accepted vision, user-facing behavior, runtime behavior, validation proof, future work, reusable product standards, approval boundaries, or a USER decision.
- Minor comments, acknowledgements, typo-level notes, duplicate remarks, or non-actionable conversation can close as `Rejected / No Action` or no durable UFD record when Codex states why no source-truth action is needed.
- When Codex closes a meaningful-looking comment without a durable UFD item, the return digest should state the no-action reason so feedback is not silently dropped.

Split-state recommendation:

| Field | Purpose | Allowed planning values |
| --- | --- | --- |
| `UFD Ledger Status:` | State of the whole active feedback ledger. | Open; Queued; Blocking; Closed; Folded Down; Deferred; Superseded; Pending; Complete; Not Required; Not Applicable |
| `Fold-Down Status:` | State of PR Readiness migration for the whole ledger. | Pending; Required; Complete; Folded; Retired; Historical; Not Required; Not Applicable |
| `Disposition Type:` | What kind of feedback item this is. | Current Branch Requirement; Current Seam Blocker; Current Seam Non-Blocking Queue; Branch Plan Revision Required; Future Branch Candidate; Family Vision Update Candidate; Nexus Vision Update Candidate; Backlog Pointer Candidate; Branch Receipt Item; Workstream / Family Dossier Item; Rejected / No Action |
| `USER Decision State:` | Whether USER has accepted the disposition. | Proposed by Codex; Recommended by ChatGPT; Accepted by USER; Revised by USER; Rejected by USER; Deferred by USER; Deferred With Waiver; Superseded; Needs USER Decision |
| `Workstream Severity:` | How much it affects implementation continuity. | Level 1 Non-Blocking; Level 2 Seam-Blocking; Level 3 Workstream-Breaking |
| `Owner Class:` | Which source-truth layer owns the durable fact. | Branch Plan; Branch Record; Backlog Pointer; Roadmap Pointer; Nexus Vision; Family Vision / Dossier; Workstream Doc; Governance Receipt; No Durable Owner Needed |
| `Status:` | Current handling state for one feedback item. | Open; Queued; Blocking; Closed; Folded Down; Deferred; Superseded |

Owner-class guardrail:
- `No Durable Owner Needed` may be used only when the item is closed as minor/no-action, duplicate, superseded, or non-actionable, with reason recorded in the active external branch plan or return digest.

Minimum UFD ledger record:
- `USER Feedback Disposition Required:`
- `UFD Ledger Status:`
- `UFD Ledger Owner:`
- `Open UFD Count:`
- `Blocking UFD Count:`
- `Fold-Down Status:`

Minimum UFD record:
- `### UFD Item: UFD-<scope>-YYYYMMDD-NNN`
- `Feedback ID:`
- `Feedback Summary:`
- `Feedback Source:`
- `Feedback Phase:`
- `Disposition Type:`
- `USER Decision State:`
- `Owner Class:`
- `Canonical Owner File:`
- `Workstream Severity:`
- `Status:`
- `Fold-Down Target:`

Full UFD record:
- `### UFD Item: UFD-<scope>-YYYYMMDD-NNN`
- `Feedback ID:`
- `Feedback Summary:`
- `Feedback Source:` chat, USER file, User Test Summary, ChatGPT review, GitHub review, validation result, or live proof.
- `Feedback Phase:`
- `Affected Branch / Seam:`
- `Original Feedback Location:`
- `Disposition Type:`
- `Proposed Disposition:`
- `Accepted Disposition:`
- `USER Decision State:`
- `Workstream Severity:`
- `Status:`
- `Canonical Owner File:`
- `Pointer Locations:`
- `Current Branch Impact:`
- `Future Branch Impact:`
- `Codex Recommendation:`
- `ChatGPT Critique / Review:`
- `Follow-Up Required:`
- `Fold-Down Target:`
- `Final Owner After PR Readiness:`

Fold-down receipt rule:
- PR Readiness Stage 1 must compare all open feedback items against the accepted branch plan and accepted Branch Vision Contract Snapshot.
- PR Readiness Stage 2 may proceed only when every meaningful feedback item is migrated, deferred with waiver, rejected/no-action with reason, closed, or explicitly carried to a future owner.
- The fold-down receipt should include `Feedback ID`, original owner, final disposition, final owner, USER decision, proof or migration reference, branch-plan retirement/deletion eligibility, and remaining open items.
- Fold-down must preserve a lookup path from every UFD ID to its final owner after branch-plan fold-down and retirement.
- Branch plan deletion remains a separate USER decision. The default post-PR outcome is folded/retired posture, not deletion.
- Default branch-plan lifecycle outcome: folded / retired posture. Deletion requires separate USER approval or a future repo-established deletion rule that includes reference scans and durable-content preservation proof.

Validator/helper implementation posture:
- Initial implementation should add source-truth rule text, branch-plan template markers, fixture examples, and marker-based validator scaffolding.
- Heavy enforcement against historical branch records is deferred because old receipts contain many historical feedback/disposition phrases that were not created under this model.
- False-positive-prone duplicate full-text detection should be report-only until fixtures prove the pattern.
- Initial validators should enforce required markers, owner fields, safe decision-state values, and fold-down status only.
- Natural-language duplicate feedback detection starts as report-only. Blocking duplicate-feedback detection requires approved fixtures, false-positive review, and separate USER approval.

Codex implementation guard:
- Codex may recommend UFD disposition, owner, Workstream severity, and fold-down target.
- Codex may not convert proposed feedback, Codex recommendations, ChatGPT recommendations, or inferred design preference into accepted branch scope without USER decision.
- USER decision controls accepted branch scope, accepted vision, accepted future-work posture, accepted reusable standard, and accepted no-action closure.

### Repo Naming / Governance Taxonomy Reform Addendum

Purpose:
- Make governance names easy for USER to call, easy for Codex to follow, easy for validators to report, and hard to confuse with backlog IDs, branch IDs, feedback IDs, or historical records.
- Reduce ambiguity that causes drift, especially around phase/stage/seam/slice/package/workstream/family and live-state/current-state language.
- Produce naming recommendations and record the completed safe vision rename/family-vision owner migration. Further bulk file moves, directory moves outside `Docs/family_visions/`, historical rewrites, and destructive rename/delete execution remain separate USER decisions unless this plan names a validated no-loss path.

Canonical names versus friendly aliases:
- Canonical names are used by validators, source truth, Codex packets, branch records, branch plans, helper output, and commit/PR metadata.
- Friendly aliases are USER-facing helper labels only.
- Friendly aliases never replace canonical phase, stage, marker, or file-owner names unless a future USER-approved rename migration updates source truth, validators, fixtures, templates, and historical compatibility notes.
- When both are useful, write the canonical name first and the alias second, such as `Branch Readiness Stage 1 (Plan Review)`.

Naming inventory:

| Term / Label | Current meaning / context | Correct intended meaning | Ambiguity risk | Recommended future name / usage | Owner documentation | Migration priority | USER decision needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Phase | Lifecycle state in phase governance. | Top-level lifecycle state. | Medium: sometimes used for substeps. | Keep `Phase`; define once. | `Docs/phase_governance.md`, `Docs/Main.md` | Low | No |
| Stage | Ordered sub-step inside a phase. | Stage 1 analysis vs Stage 2 execution/setup. | Medium: sometimes confused with release stage. | Keep `Stage`; always pair with phase name. | `Docs/phase_governance.md` | Low | No |
| Seam | Bounded execution checkpoint inside Workstream. | Workstream execution lane/checkpoint. | High: sometimes treated as final branch scope. | Keep `Seam`; define as bounded checkpoint, not automatic stop. | `Docs/Main.md`, `Docs/phase_governance.md` | Medium | No |
| Slice | Traceable deliverable unit inside a package. | Smaller admitted implementation unit. | High: overlaps seam in conversation. | Keep `Slice`; require `Slice = deliverable`, `Seam = execution checkpoint`. | `Docs/workstreams/index.md` | Medium | No |
| Workstream | Phase name and durable doc family. | Build/implementation phase; also promoted work record. | High: process and file owner share name. | Keep canonical `Workstream`; use `Workstream Doc` for files. | `Docs/workstreams/index.md` | Medium | No |
| Package | Grouped delivery scope under one family. | Branch/release package of related slices. | Medium: can sound like installer package. | Keep `Package`; expand as `Feature Package` at first use. | `Docs/feature_backlog.md` | Medium | No |
| Family | Long-lived product area. | Broad feature family. | Medium: FAM IDs can look temporary. | Keep `Family`; expand `FAM` at first use. | `Docs/feature_backlog.md` | Low | No |
| Backlog Item | Product registry entry. | Broad selectable family/package identity. | Medium: legacy FB rows are historical only. | Use `Backlog Family` for FAM records; `historical trace` for old FB rows. | `Docs/feature_backlog.md` | Medium | No |
| Branch Authority Record | Branch legal control surface. | Branch authority, approvals, phase history, compact receipt. | Low/Medium: often shortened to branch record. | Keep; allow `Branch Record` as alias after first use. | `Docs/branch_records/index.md` | Low | No |
| Branch Runtime Engineering Plan | Active detailed branch plan. | Runtime-focused active execution blueprint. | Medium: long name. | Keep formal name; alias `Branch Plan` after first use. | `Docs/branch_plans/README.md` | Low | No |
| Branch Engineering Plan | Conversational form for branch-level implementation planning. | Generic alias for Branch Runtime Engineering Plan or a future non-runtime branch plan when source truth supports it. | Medium: can blur runtime and governance branches. | Use the formal owner name first, then the alias. | `Docs/branch_plans/README.md` | Medium | No |
| Branch Plan | Short alias. | Alias for Branch Runtime Engineering Plan when context is clear. | Medium: could mean any plan. | Use only after formal name is introduced. | `Docs/branch_plans/README.md` | Medium | No |
| Branch Receipt | Folded historical branch evidence. | Compact/structured historical branch trace. | Medium: not consistently defined. | Define as `Structured Branch Receipt`. | `Docs/branch_records/index.md` | Medium | No |
| Worktree Slot | Stable workspace role assignment. | Intended lane assignment, not live state. | Low/Medium. | Keep; always say slot does not equal active authority. | `Docs/worktree_slots.md` | Low | No |
| Governance Receipt | Historical interpretation after validation. | Recorded decision/evidence, not live truth. | Medium. | Keep; define beside derived live truth. | `Docs/governance_efficiency_operating_model.md` | Low | No |
| Runtime Branch Engineering Contract | Engineering intent contract. | Branch-wide runtime baseline/delta/proof contract. | Medium: overlaps branch plan. | Keep; state contract = intent, plan = execution blueprint. | `Docs/phase_governance.md` | Low | No |
| Vision Contract | Product/design intent layer. | USER-accepted product/design standard. | Medium: can sound like new file. | Keep; use `Nexus Vision`, `Family Vision`, or `Branch Vision Snapshot` by scope. | `Docs/branch_plans/README.md` | Medium | Future file decision |
| Branch Vision Snapshot | Branch-specific accepted vision. | Snapshot inside active external branch plan. | Low. | Use `Branch Vision Contract Snapshot` formally. | `Docs/branch_plans/README.md` | Low | No |
| USER Feedback Disposition | Feedback routing model. | Item-level classification and final owner proof. | Implemented governance term. | Use `USER Feedback Disposition (UFD)` with ID glossary. | `Docs/branch_plans/README.md`; this plan | High | No |
| USER Decision Ledger | Planning decision record. | USER decisions, waivers, rejects, accepts. | Medium: could duplicate UFD. | Keep; UFD items link to it rather than copy. | `Docs/phase_governance.md` | Medium | No |
| Assumption Ledger | Design assumption states. | Codex/ChatGPT/USER assumption decision states. | Medium. | Use `Design Assumption Ledger`. | `Docs/branch_plans/README.md` | Low | No |
| Vision Question Digest | Packet for design uncertainty. | Question packet when vision/design uncertainty blocks or affects work. | Low. | Keep. | `Docs/branch_plans/README.md` | Low | No |
| Branch Plan Revision Packet | Controlled plan change packet. | Required when accepted scope/vision changes. | Low. | Keep. | `Docs/branch_plans/README.md` | Low | No |
| Hardening | Stabilization/proof phase. | Repo-side stabilization and plan comparison. | Medium for USER. | Keep canonical; optional alias `Stabilize`. | `Docs/phase_governance.md` | Low | No |
| Live Validation | User-observable validation phase. | Live/static proof, UTS, waiver posture. | Medium. | Keep canonical; optional alias `User Proof`. | `Docs/phase_governance.md` | Low | No |
| PR Readiness | Merge-readiness phase. | Stage 1 analysis and Stage 2 PR execution/watch. | Medium. | Keep canonical; aliases `Merge Readiness Audit` and `PR Execution / Watch`. | `Docs/phase_governance.md` | Low | No |
| Release Readiness | Release validation phase. | File-frozen release candidate validation. | Medium: confused with release execution. | Keep; always separate from `Release Execution`. | `Docs/phase_governance.md` | Low | No |
| Branch Readiness | Branch planning/setup phase. | Stage 1 analysis, Stage 2 setup/admission. | Medium. | Keep; aliases `Plan Review` and `Setup / Admission`. | `Docs/phase_governance.md` | Low | No |
| RRI | Standing governance intake cycle ID. | Release Readiness / governance intake cycle. | High: acronym is opaque. | Keep `RRI-*`; expand as `Release Readiness Intake` or `Governance Intake Cycle` at first use. | `Docs/branch_records/index.md` | Medium | Maybe rename later |
| UTS | User Test Summary. | USER validation questionnaire / returned proof. | Medium. | Keep; expand at first use in prompts. | `Docs/user_test_summary_guidance.md` | Low | No |
| SLC | Slice shorthand. | Slice ID or source-owner ledger row depending context. | High collision risk. | Avoid in new USER-facing prose; use `Slice` unless source-owner marker ID requires `SLC`. | `Docs/workstreams/index.md`, source-owner inventory | High | No for prose, yes for ID migration |
| PKG | Package shorthand. | Package ID. | Medium. | Keep in tables; expand `Package` at first use. | `Docs/feature_backlog.md` | Low | No |
| FAM | Feature Family shorthand. | Long-lived feature family ID. | Low/Medium. | Keep; expand `Feature Family (FAM)` at first use. | `Docs/feature_backlog.md` | Low | No |
| FB | Legacy backlog/workstream shorthand. | Historical trace only. | High: conflicts with future feedback IDs. | Preserve historical `FB-###`; never use for new feedback IDs or live backlog identities. | `Docs/feature_backlog.md`, `Docs/workstreams/index.md` | High | No |
| LV | Live Validation shorthand. | Live Validation stage shorthand, often LV1/LV2. | Medium. | Use `Live Validation LV1` at first use. | `Docs/phase_governance.md` | Low | No |
| H1 | Hardening pass shorthand. | Hardening stage/pass evidence. | Medium. | Use `Hardening H1` at first use. | `Docs/phase_governance.md` | Low | No |
| PR | Pull Request. | GitHub pull request evidence only. | Low/Medium. | Keep; never use PR number as backlog/workstream identity. | `Docs/Main.md` | Low | No |
| Release Window | Set of merged PRs since last release. | Derived release inventory for Release Readiness. | Medium: can become live ledger. | Keep; derive from GitHub/helper, record only historical receipt. | `Docs/prebeta_roadmap.md` | Medium | No |
| Current State | Often means live state or compact decision surface. | Avoid as owner unless clearly historical/current-summary. | High. | Prefer `Current Summary`, `Decision Surface`, or derived live truth. | `Docs/governance_efficiency_operating_model.md` | High | No |
| Active Branch | Legal current branch authority. | Active branch authorized by branch record, not slot or git alone. | High. | Use `Active Branch Authority` when legal meaning matters. | `Docs/branch_records/index.md` | High | No |
| Selected Next | USER-approved next branch/workstream posture. | Future selected work, not active branch by inertia. | High. | Use `Selected Next Workstream` or `Selected Next: Deferred/Waived`. | `Docs/phase_governance.md` | High | No |
| No Active Branch | Merged-main runtime/implementation idle posture. | No runtime/implementation/release/repair carrier active; standing governance may still exist. | High. | Keep with explicit standing-governance exception. | `Docs/branch_records/index.md` | High | No |
| Compact-AI | Protected sibling lane/worktree name found in mutation-boundary and source-owner-marker records. | Separate protected mutation boundary until USER/source truth defines whether it becomes a feature family, workstream, external project, or retired lane. | Medium: unclear whether it is a feature family, workstream, or external project. | Do not treat as active branch/workstream identity without owner definition; keep as pending/protected boundary in packets. | `Docs/branch_records/feature_repo_wide_source_owner_marker_adoption.md`, `Docs/validation_helper_registry.md` | Medium | Needs USER/source-truth decision |

ID namespace policy:

| Namespace | Meaning | Status | Collision guard |
| --- | --- | --- | --- |
| `FAM-*` | Feature Family. | Live backlog family namespace. | Do not use for branch IDs, feedback IDs, PR IDs, or worktree slot IDs. |
| `PKG-*` | Feature Package under one family. | Live package namespace. | Expand as `Package` at first use. |
| `SLC-*` | Slice or source-owner marker slice row where historically required. | Avoid in new prose; preserve where existing source-owner records require it. | Prefer `Slice` in USER-facing text. |
| `FB-*` | Legacy backlog/workstream trace. | Historical-only. | Never use for new live backlog items or feedback IDs. |
| `UFD-*` | USER Feedback Disposition item. | Implemented feedback namespace. | Never use `FBK-*`; UFD is not a backlog item. |
| `RRI-*` | Standing governance / Release Readiness Intake cycle. | Existing governance intake namespace. | Expand at first use; do not use for release IDs. |
| `PR #*` | GitHub pull request number. | GitHub evidence only. | PR number is never a backlog, workstream, package, or feedback identity. |
| `feature/*`, `repair/*`, `codex/*` | Git branch/ref namespace. | Branch/ref identity only. | Never use as feature, package, feedback, workstream, release, or vision identity. |
| `v*-prebeta` | Git tag / GitHub Release namespace. | Release identity only. | Never use as branch, workstream, backlog, feedback, or package identity. |

File naming analysis:

| Category | Preferred naming pattern | Preserve | Phase out later | Migration risk | USER decision needed |
| --- | --- | --- | --- | --- | --- |
| Top-level Docs files | `Docs/<clear_topic>.md`; noun phrase matching owner role. | `Docs/Main.md`, `Docs/phase_governance.md`, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`. | Ambiguous old one-off topic files only after reference scan. | Medium because many prompts reference exact paths. | Yes for deletion/rename. |
| Branch records | `Docs/branch_records/<branch_slug>.md`. | Historical `codex_*` and `feature_*` records as receipts. | New active `codex/` naming; active repair-only naming by inertia. | High for historical links. | Yes for historical rewrites. |
| Branch plans | `C:\Nexus Governance State\branches\<branch_slug>\branch_plan.md` for active plans; `Docs/branch_plans/<branch_slug>.md` for repo historical receipts. | External active plans plus historical repo receipts until fold-down review. | Permanent branch-specific plan sprawl after fold-down. | Medium. | Yes before deletion. |
| Workstream docs | `Docs/workstreams/FB-XXX_slug.md` for historical/promoted records. | Existing FB historical trace names. | New live FB IDs. | High; legacy evidence paths. | Yes for rename. |
| Family dossiers | `Docs/workstreams/FB-XXX_slug_family_dossier.md` until a future family-dossier directory is approved. | Existing family dossiers. | Mixing dossier and workstream meaning in text. | Medium. | Yes for directory split. |
| Validators/helpers | `dev/orin_<domain>_<capability>_validation.py`, `_audit.py`, `_harness.py`, `_helper.py`. | Existing reusable helper names. | Seam-number helper names unless temporary with consolidation target. | Low/Medium. | No for new names, yes for bulk rename. |
| Fixtures | `dev/fixtures/<domain>/<valid_or_invalid>_<scenario>.md`. | Existing branch readiness fixture names. | Opaque fixture names without expected result. | Low. | No for new fixtures. |
| README/index files | `README.md` for local standard; `index.md` for routing table. | `Docs/branch_plans/README.md`, `Docs/workstreams/index.md`, `Docs/branch_records/index.md`. | README carrying live branch state. | Low. | No. |

Governance label hierarchy recommendation:
- `Phase`: top-level lifecycle state: Branch Readiness, Workstream, Hardening, Live Validation, PR Readiness, Release Readiness, Release Execution, Post-Release Carry-Forward.
- `Stage`: ordered sub-step inside a phase: Stage 1 analysis; Stage 2 setup/execution.
- Use `Release Milestone` or `Release Sequencing` when discussing public release progress; reserve `Stage` for ordered substeps inside a phase.
- `Workstream`: implementation/build phase and promoted durable work record. When referencing files, say `Workstream Doc`.
- `Package`: delivery scope under one feature family.
- `Slice`: deliverable unit inside a package.
- `Seam`: bounded execution/proof checkpoint inside Workstream; not automatically the whole branch scope.
- A branch may contain multiple seams and slices; neither a seam nor a slice automatically defines the full branch scope.
- `Branch Record`: legal authority and structured branch receipt.
- `Branch Plan`: active Branch Runtime Engineering Plan after first formal use.
- `Dossier`: durable family-level continuity surface, not active branch authority.
- `Receipt`: historical/validated interpretation, not live operational truth.

Acronym policy:
- Keep with first-use expansion: `FAM`, `PKG`, `UTS`, `LV`, `H1`, `PR`.
- Keep but mark historical-only: `FB`.
- Keep but expand aggressively: `RRI`.
- Avoid in new USER-facing prose unless table/ID context requires it: `SLC`.
- Add new: `UFD` for USER Feedback Disposition IDs only.
- Acronym glossary should live in `Docs/Main.md` as the recovery pointer and in the detailed owner docs (`Docs/feature_backlog.md`, `Docs/phase_governance.md`, `Docs/branch_plans/README.md`, `Docs/workstreams/index.md`) for context-specific definitions.

User-facing process names:
- Keep canonical names and add friendly aliases only as presentation aids:
  - `Branch Readiness Stage 1` = `Plan Review`
  - `Branch Readiness Stage 2` = `Setup / Admission`
  - `Workstream Entry` = `Build Entry`
  - `Seam Execution` = `Bounded Build Seam`
  - `Hardening H1` = `Stabilize H1`
  - `Live Validation LV1` = `User Proof LV1`
  - `PR Readiness Stage 1` = `Merge Readiness Audit`
  - `PR Readiness Stage 2` = `PR Execution / Watch`
  - `Release Readiness Stage 1` = `Release Validation`
  - `Release Readiness Stage 2` = `Release Preparation`
  - `Release Execution` = `Publish Release`
  - `Post-Release Carry-Forward` = `Next-Branch Carry-Forward`
- Validators should continue to use canonical names until USER approves any canonical enum rename.
- Validator output may include friendly aliases only after the canonical term appears, such as `Branch Readiness Stage 1 (Plan Review)`.

Codex prompt naming standard:
- Every prompt should name exact worktree, exact branch, exact phase, exact stage if applicable, exact source-truth owner, allowed mutation surfaces, pending USER decisions, validation commands, stop/report conditions, and exact return packet fields.
- ChatGPT-generated Codex prompt gates are owned by `Docs/nexus_startup_contract.md`. This plan and Codex prompt naming standards may point to that owner, but must not re-own or restate the Nexus Prompt Gate final scrub rule.
- Governance docs may define direct repo policy for Codex execution. The startup/loader contract owns generated-prompt wording and ChatGPT/new-chat bootstrap continuity.
- If a friendly alias is used, include the canonical name next to it on first use.
- Do not say `current state` without naming whether it means derived live truth, current summary, decision surface, or historical receipt.
- Do not say `branch plan` without naming the file path when mutation or validation is in scope.
- Do not say `feedback` without classifying whether it is UFD current-branch, future-candidate, reusable-vision, no-action, or needs USER decision.

Validator output naming standard:
- Validator messages should include severity, source-truth owner, fact class, phase/stage affected, exact blocking marker, exact repair owner, and exact USER decision needed when human approval is required.
- Recommended shape: `BLOCKED: <owner file>: <fact class>: <phase/stage>: <condition>; repair owner=<owner>; USER decision=<needed or none>`.
- Avoid ambiguous messages such as `current state missing`; prefer `Active Branch Authority marker missing from branch record` or `Derived live truth attempted in backlog`.

Index / README documentation standard:
- `Docs/Main.md`: glossary pointer, acronym first-use map, source-truth owner map, canonical/friendly phase alias table.
- `Docs/nexus_startup_contract.md`: ChatGPT/new-chat loader map and Nexus Prompt Gate owner for generated Codex prompts; other docs should use compact pointers instead of copying its prompt-gate wording.
- `Docs/codex_user_guide.md`: USER-facing explanation and examples.
- `Docs/orin_task_template.md`: reusable prompt packet skeleton and prompt-field examples; it points to the startup contract for prompt-gate wording rather than owning it.
- `Docs/phase_governance.md`: canonical lifecycle names and validator-backed markers.
- `Docs/branch_plans/README.md`: Branch Runtime Engineering Plan, UFD ledger, Branch Vision Snapshot, fold-down fields.
- `Docs/workstreams/index.md`: package/slice/seam/workstream/dossier naming.
- `Docs/branch_records/index.md`: branch authority, branch receipt, active/no-active/selected-next naming.
- `Docs/validation_helper_registry.md`: helper and validator naming standard.
- `Docs/worktree_slots.md`: slot naming and assignment-vs-authority distinction.

Missed source-truth owner coverage audit:

This table is a compact addendum to the complete Docs manifest in `Docs/governance_docs_full_inventory_reform_audit.md`. It records the owner files most likely to be missed by the UFD/naming implementation path and keeps prompt-gate ownership visible without duplicating prompt-gate policy.

| File path | Expected owner role | Manifest represented | Ownership map represented | Reform package represented | Missing / weak area | Repair posture |
| --- | --- | --- | --- | --- | --- | --- |
| `Docs/nexus_startup_contract.md` | ChatGPT/new-chat loader map and Nexus Prompt Gate owner for generated Codex prompts. | Yes | Yes | Weak before this addendum | UFD/naming implementation targets and Codex prompt naming standard did not visibly point to the loader/startup owner. | Repaired with compact target-file, prompt-naming, and documentation-standard pointers; no policy duplication. |
| `Docs/orin_task_template.md` | Reusable Codex task/prompt packet skeleton and prompt-field examples. | Yes | Yes | Present but paired weakly with startup owner | Template can look like prompt-gate owner if the startup contract pointer is missing. | Repaired with compact pointer that template examples route prompt-gate wording to `Docs/nexus_startup_contract.md`. |
| `Docs/codex_user_guide.md` | USER-facing Codex workflow guide and examples. | Yes | Yes | Yes | No source-truth miss found. | No repair beyond keeping it in future implementation targets for examples. |
| `Docs/codex_modes.md` | Codex execution posture and mode behavior. | Yes | Yes | Yes | No source-truth miss found. | No repair; it already points to the startup contract for prompt generation scope. |
| `Docs/pr_watcher_mode_contract.md` | PR watcher mode contract and watcher approval/default behavior. | Yes | Yes | Yes | No source-truth miss found. | No repair. |
| `Docs/user_test_summary_guidance.md` | User Test Summary guidance and UTS artifact expectations. | Yes | Yes | Yes | No source-truth miss found. | No repair. |
| `Docs/governance_intake_triage_and_digest_profiles.md` | Governance intake triage and digest profile standard. | Yes | Yes | Yes | No source-truth miss found. | No repair. |
| `Docs/nexus_vision.md` | Project-wide Nexus Vision contract. | Yes | Yes | Yes | Rename/reframe completed from the former `Docs/orin_vision.md` path. | Keep; family-specific vision now routes through `Docs/family_visions/`. |
| `Docs/validation_helper_registry.md` | Helper/validator responsibility registry. | Yes | Yes | Yes | No source-truth miss found. | No repair. |

Staged naming migration plan:

| Stage | Work | Risk | Approval |
| --- | --- | --- | --- |
| N1 | Add glossary and taxonomy sections to owner docs. | Low. | Future source-edit approval. |
| N2 | Update Codex User Guide and templates with canonical name plus friendly alias rules. | Low/Medium. | Partially implemented through current owner docs; further guide examples remain future-safe. |
| N3 | Add validator wording standard and report-only taxonomy checks. | Medium. | Implemented for stale vision path, family vision pointers, and branch-plan retirement index; broader global severity prefixes remain future. |
| N4 | Add fixture coverage for UFD IDs and ambiguous-name failures. | Low. | UFD ID fixtures implemented; broader taxonomy failure fixtures remain future-safe. |
| N5 | Rename or collapse ambiguous top-level Docs files after reference scan. | High. | Separate USER decision per file group. |
| N6 | Consider directory split for family dossiers only if workstreams folder remains confusing after glossary update. | High. | Separate USER decision. |
| N7 | Historical compatibility pass for old FB/codex records; preserve old names as receipts. | High. | Separate USER decision. |

Naming reform acceptance checklist:
- Each term has one intended meaning.
- Each term has one owner doc.
- Each acronym is expanded at first use.
- Each process label fits phase/stage/seam/slice/package/family hierarchy.
- Each file name matches its ownership role.
- Codex prompts can call the term consistently.
- Validator output can report the term clearly.
- USER can understand and invoke the term without knowing internal history.
- Migration risk and rollback risk are documented.
- Historical compatibility is preserved for old branch, PR, release, and FB evidence.

Naming decisions still needing USER approval:
- Whether `RRI` should be re-expanded or renamed in public governance packets.
- Whether to create a dedicated acronym glossary section in `Docs/Main.md` or keep glossary entries distributed across owner docs.
- Whether to split family dossiers out of `Docs/workstreams/` later.
- Whether any top-level context docs should be renamed, collapsed, or deleted.
- Whether validator output should adopt severity prefixes globally.
- Whether friendly aliases should appear in final response packets by default or only in USER-facing guides.

## Next Legal Phase

- Recommended next phase: USER review of the updated Docs reform dossier and review index.
- PR creation: held until USER accepts the updated review surface and explicitly approves PR Readiness Stage 2.
- Merge: pending USER approval.
- Runtime implementation: blocked.
- FAM-006 mutation: blocked.
- FAM-007 mutation: blocked.
- Release/tag/artifact work: blocked.
