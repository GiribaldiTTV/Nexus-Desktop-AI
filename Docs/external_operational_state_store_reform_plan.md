# External Operational State Store / Release Debt Abolition Reform Plan

> Historical reform context and accepted evidence. This file grants no current execution authority. Current applicability follows `Docs/Main.md`, `Docs/phase_governance.md` and the selected installed external owner. Preserve dated facts as history.
## Purpose

This planning reference preserves the agreed External Operational State Store / Release Debt Abolition reform so future Governance branch work can implement it without losing scope, sequencing, safeguards, or USER decisions.

This file is a planning reference, not an active external-state migration, helper implementation, validator implementation, or release-unblocker by itself. Binding source-truth rules live in `Docs/governance_efficiency_operating_model.md`, `Docs/phase_governance.md`, and their routed governance owners.

## Current Approved Sequencing

1. PR #220 / FAM-007 post-merge source-truth repair is historical and released through `v1.7.23-prebeta`.
2. PR #222 / FAM-006 Active Overlay Recording Runtime Foundation planning receipt merged without runtime implementation and is included in `v1.7.25-prebeta`.
3. PR #223 folded PR #222 into historical source truth, and PR #224 hardened PR body drift checks; both are included in `v1.7.25-prebeta`.
4. Docs Split Stage 0 landed through PR #225 and recorded the migration plan, split inventory expectations, and transition drift gate while preserving repo docs as durable source truth.
5. Docs Split Stage 1 landed through PR #226 and added report-only helper/bootstrap scaffolding.
6. Stage 2 initialized `C:\Nexus Governance State` after separate USER approval; that local root initialization did not migrate active state or transition repo validators.
7. Stage 3 recorded a no-mutation migration preview packet in external state after separate USER approval.
8. Stage 4A landed through PR #227 and added the report-only repo live-state leakage scanner / migration-map helper.
9. Stage 4B active-state migration planning packet landed through PR #228 and used the Stage 4A scanner output to name exact repo surfaces, target external records, lock/snapshot/version requirements, durable receipt preservation, and no-loss promotion rules.
10. Stage 4C active-state migration execution planning packet landed through PR #229 and preserved the exact execution preflight, external target record list, durable receipt preservation plan, rollback/recovery plan, and USER review question.
11. Stage 4 active-state migration execution completed externally after PR #229 at source repo HEAD `5abdd9c011c80f5b7b57d473b973654a2427d5a8`; it created only approved central external operational records, released locks, wrote audit logs, and did not move, delete, archive, or rewrite repo Docs.
12. Stage 5 validator transition landed through PR #230. Local external-state validation is explicit for approved local workflows, while repo / CI / clean-clone validators remain independent from `C:\Nexus Governance State`.
13. Stage 6 repo cleanup planning landed through PR #231 and identified compact pointer surfaces as the first cleanup execution lane.
14. Stage 6A compact pointer-surface cleanup landed through PR #232 and cleaned `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/worktree_slots.md`.
15. Stage 6B branch-authority routing cleanup planning landed through PR #233 and defined the `Docs/branch_records/index.md` execution packet.
16. Stage 6C branch-authority routing cleanup landed through PR #234 and made `Docs/branch_records/index.md` durable routing law plus standing Governance authority while non-standing active operational authority routes external.
17. Stage 6D branch-detail-record / branch-plan cleanup planning landed through PR #235 and defined the no-loss cleanup batches.
18. Stage 6E no-loss cleanup closure showed broad branch-record / branch-plan rewrites are not required by default because they risk durable receipt loss.
19. Post-PR #240 release-readiness drift clarified the permanent boundary: repo docs may keep durable branch/document evidence pointers and historical receipts, but must not own live active/complete/pending lifecycle posture. If a later validator finds repo active-state leakage, fix the exact leakage or route it external without broad receipt loss.
20. File movement, deletion, archival, worktree-local staging creation, FAM worktree reconciliation, branch cleanup, release execution, and any future exact branch-record / branch-plan cleanup found by later validators remain separate USER decisions after Stage 6E is reviewed.

## Current Boundaries

Approved now:

- Stage 6E no-loss cleanup closure
- scanner-backed decision that branch records and repo branch-plan files remain durable receipts, schema surfaces, or historical transition evidence unless exact active-state leakage is named
- completion posture for the External Operational State Store transition
- USER review bundle refresh for Stage 6E inspection
- validation and PR Readiness Stage 1 analysis

Permanent intent:

- Repo docs become index/context files for operational work.
- Repo docs may keep durable governance law, product/architecture vision, compact pointers, public-safe explanations, and historical receipts.
- Repo docs must not be the active ledger for branch plans, UFD items, Branch Change Intent rows, Element-to-Phase rows, worktree assignment, PR watcher state, release-window assembly, selected-next posture, review-bundle manifests, rebaseline packets, or temporary Codex handoff state.
- Backlog and roadmap may document that a branch or receipt exists for a family/breakpoint, but live active/complete/pending/no-branch-created status belongs to external operational state or Git/GitHub/helper-derived truth.

Not approved by this planning file:

- helper `--apply` operations
- mandatory GitHub Actions / clean-clone dependency on `C:\Nexus Governance State`
- worktree-local staging folder creation
- file moves, deletion, archive execution, or broad repo cleanup execution
- PR creation
- merge
- release execution
- runtime work
- FAM-006, FAM-007, or Compact-AI mutation outside approved carrier scope
- issue work
- branch cleanup
- backup setup
- private repo creation

## Docs Split Stage 1 - Helper Bootstrap Scaffold Plan

Stage Status: `Active helper/bootstrap scaffolding only`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 1 Base: `origin/main@1acb308fead3c61600604dbfd2fdb36fca338262`

This stage creates safe helper scaffolds and a validation plan without initializing `C:\Nexus Governance State`, migrating active state, moving repo Docs files, or changing clean-clone repo validation. The helpers are report-first and dry-run by default; any operation that creates external state requires a later explicit USER decision and an explicit `--apply` command.

Stage 1 deliverables:

- `dev/orin_external_state_common.py` shared scaffold support
- `dev/orin_external_state_init.py` bootstrap packet and optional future `--apply` initialization path
- `dev/orin_external_state_report.py` external-root posture report
- `dev/orin_external_state_validation.py` clean-clone-safe local validation helper
- `dev/orin_external_state_lock.py` dry-run/applied lock packet scaffold
- `dev/orin_external_state_snapshot.py` dry-run/applied snapshot scaffold
- `dev/orin_state_fold_down_preview.py` fold-down preview scaffold
- `dev/orin_external_state_promote_preview.py` promotion preview scaffold
- `dev/orin_external_state_promote.py` promotion apply scaffold with no-loss audit posture
- helper registry registration and smoke validation for the helper family
- no external folder creation, state migration, file movement, deletion, archival, or worktree-local staging creation

Stage 1 review question:

```text
Do you approve Stage 2 root initialization for C:\Nexus Governance State after reviewing the Stage 1 helper/bootstrap scaffold and smoke-validation proof?
```

Stage 2 candidate after this repair merges:

```text
External Operational State Root Initialization
```

Stage 2 candidate scope:

- run `dev/orin_external_state_init.py --apply` only after explicit USER approval
- initialize `C:\Nexus Governance State` with manifest, generated index placeholder, schema folder, locks, central state folders, snapshot folder, and audit-log folder
- keep repo validators clean-clone safe
- keep active branch/worktree/release-window migration deferred until helper validation and USER review are green

Stage 2 non-includes unless separately approved:

- moving repo `Docs` files
- deleting or archiving branch records/plans
- migrating active branch state
- mutating FAM-006 or FAM-007
- changing runtime behavior
- creating a release or tag

## Docs Split Stage 4A - Repo Live-State Leakage Scanner / Migration Map Helper Plan

Stage Status: `Active report-only migration-map helper support`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 4A Base: `origin/main@7f17b97bac1f0ec7d9e424fdfa8792fe420eb885`

This stage adds a report-only helper that scans repo Docs for live operational state, classifies findings, and prints a migration map. It does not edit repo docs, write central branch/worktree/release-window state, move files, delete files, archive files, transition validators, or treat external state as complete.

Stage 4A deliverables:

- `dev/orin_repo_live_state_leakage_scan.py` report-only scanner for repo live-state leakage and migration candidates
- helper registry entry for the scanner
- source-truth plan updates that distinguish scanner output from active migration
- smoke validation showing the scanner reports `CLEAR / MIGRATION CANDIDATES ONLY` when findings are transition-legal or historical receipts

Stage 4A review question:

```text
Do you approve using the report-only migration map as the basis for a later active-state migration plan, without moving repo Docs files or migrating active state yet?
```

Stage 4A non-includes unless separately approved:

- creating branch/worktree/release-window state records from repo docs
- moving active branch plans or active branch status out of repo
- deleting, archiving, or renaming repo docs
- transitioning repo validators into mandatory external-state checks
- mutating FAM-006 or FAM-007 worktrees
- changing runtime behavior

## Docs Split Stage 4B - Active-State Migration Planning Packet

Stage Status: `Active planning packet only`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 4B Base: `origin/main@6d71e4ee15721174c7fa216afa62e45768a0fe4e`

This stage converts the Stage 4A scanner output into a USER-reviewable migration planning packet. It does not migrate active state, create central branch/worktree/release-window records, move repo docs, delete repo docs, archive repo docs, transition validators, or mutate FAM worktrees.

Stage 4B evidence:

- Scanner command: `python dev\orin_repo_live_state_leakage_scan.py --repo "C:\Nexus Worktrees\Governance" --max-findings 50 --strict`
- Scanned Files: `136`
- Findings: `5881`
- Blocking Leakage Findings: `0`
- Scan Result: `CLEAR / MIGRATION CANDIDATES ONLY`
- Classification Summary: `Durable Historical Receipt: 5006`; `Durable Rule Reference: 368`; `Migration Candidate: 408`; `Review Candidate: 18`; `Transition-Legal Current Owner: 81`
- External root report: `C:\Nexus Governance State` exists and passes canonical root check with schema `external-state-v1`; its recorded Source Repo HEAD is `7f17b97bac1f0ec7d9e424fdfa8792fe420eb885`, so any future migration execution must first snapshot and reconcile the external root against the then-current `origin/main`.

Stage 4B deliverables:

- a concrete migration planning matrix naming repo surface classes, target external records, preservation rules, and execution blockers
- a migration wave plan that keeps branch records and repo branch-plan files legal receipt owners while active branch status and active branch planning move external after USER-approved migration execution
- lock, snapshot, schema, version, generated-index, acknowledgement, and no-loss promotion requirements for the future execution stage
- exact USER decision text for the next stage

Stage 4B migration planning matrix:

| Source Surface / State Class | Current Legal Owner During Transition | Target Owner After Migration Approval | Durable Repo Preservation Rule | Execution Blocker Before Migration |
| --- | --- | --- | --- | --- |
| Active branch authority index entries | `Docs/branch_records/index.md` | `C:\Nexus Governance State\central\active_branch_authority_state.md` plus generated `state_index.md` | Keep repo index as durable routing law and historical receipt index only | `External State Migration Premature` / `USER Decision Required` |
| Active branch record operational fields | `Docs/branch_records/<branch>.md` | `C:\Nexus Governance State\branches\<branch_slug>\branch_state.md` | Keep durable approvals, decisions, PR/release receipts, and final fold-down history in repo | `External State Promotion Missing` |
| Active branch plans | Repo files must not own active branch-plan rows after transition | `C:\Nexus Governance State\branches\<branch_slug>\branch_plan.md` | Keep templates/rules in repo and preserve retired repo branch-plan receipts only when USER approves durable receipt retention | `External State Promotion Missing` |
| Active UFD, Branch Change Intent, and Element-to-Phase proof ledgers | active branch plan | `C:\Nexus Governance State\branches\<branch_slug>\ufd_ledger.md`, `change_intent_ledger.md`, and `element_to_phase_matrix.md` | Keep compact folded outcomes in repo only after PR Readiness fold-down | `External State Promotion Missing` |
| Worktree slot live assignment | `Docs/worktree_slots.md` while transition remains legal | `C:\Nexus Governance State\worktrees\<worktree_label>\worktree_state.md` | Keep stable slot definitions and durable assignment receipt schema in repo | `External State Promotion Missing` |
| Selected-next operational posture | backlog/roadmap transition fields when still legal | `C:\Nexus Governance State\central\selected_next_state.md` or branch/family planning state | Keep durable product priority, family direction, and USER-approved future package references in repo | `External State Promotion Missing` |
| Release-window assembly | Release Readiness packet plus repo historical receipts | `C:\Nexus Governance State\release_windows\<release_slug>\release_window_state.md` | Keep public release truth, released tags, and durable release interpretation in repo | `External State Lock Missing` |
| Live PR / review / watcher state | Git/GitHub/helpers; repo records only as historical receipts | Git/GitHub/helpers plus optional `branches\<branch_slug>\pr_readiness_state.md` snapshots | Keep final PR receipts and bot-review closeout evidence only when durable | `External State Transition Drift` |
| USER review bundle manifests | Desktop bundle helper output | `C:\Nexus Governance State\review_bundles\<worktree_label>\` after approval | Keep review-bundle rule in repo; do not commit local bundle outputs | `External State Promotion Missing` |
| Rebaseline audit packets and temporary handoff digests | Codex packet / branch authority while active | `C:\Nexus Governance State\branches\<branch_slug>\` or `worktrees\<label>\` as operational evidence | Keep only durable decisions and final fold-down receipts in repo | `External State Promotion Missing` |
| Cross-worktree lessons and governance candidates | Repo source truth only after USER-approved merge | `C:\Nexus Governance State\cross_worktree_lessons\` and `governance_candidates\` | Accepted governance returns to repo source truth by PR and merge | `Governance Candidate Not Promoted` |
| Reference Standard candidate proposals and collision reports | Branch packets, Codex digest, helper output, or external evidence after workflow admission | `C:\Nexus Governance State\branches\<branch_slug>\reference_candidates\` plus generated `C:\Nexus Governance State\reference_standards\` reports | Promoted Reference Standards stay in repo source-truth catalogs; external candidates remain evidence until USER-approved promotion merges | `Reference Candidate Sync Missing` / `Reference Candidate Treated As Canon` |

Stage 4B future execution wave plan:

1. Wave 1 - Migration preflight: verify external root schema, current repo HEAD, root lock, migration lock, snapshot, audit-log path, and generated-index rule.
2. Wave 2 - Branch/worktree/release state creation: create central external records from current legal repo owners without deleting or moving repo docs.
3. Wave 3 - No-loss reconciliation: compare external records back to repo source truth, classify every copied fact as external-only, durable receipt, generated index, or USER decision required.
4. Wave 4 - Repo cleanup proposal: produce a separate USER-reviewable cleanup packet for repo docs that should become pointers, durable receipts, templates, or historical archives.
5. Wave 5 - Validator transition proposal: update repo validators only after external records exist, snapshots pass, and clean-clone behavior is preserved.
6. Wave 6 - Active worktree acknowledgement: require Governance, FAM-006, FAM-007, and any active future worktree to acknowledge merged governance/source-truth changes before relying on the new operational-state model.

Stage 4B review question:

```text
Do you accept this active-state migration planning packet as the basis for a later USER-approved migration execution stage, with no repo doc movement, deletion, archival, validator transition, or FAM worktree mutation in this stage?
```

Stage 4B non-includes unless separately approved:

- creating or updating central branch/worktree/release-window operational records
- using worktree-local `.nexus_state_staging`
- changing external state schema
- moving, deleting, archiving, or renaming repo docs
- transitioning repo validators into mandatory external-state checks
- mutating FAM-006 or FAM-007 worktrees
- release execution, runtime implementation, issue work, branch cleanup, or private-state backup

## Docs Split Stage 4C - Active-State Migration Execution Planning Packet

Stage Status: `Historical - execution planning packet landed through PR #229`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 4C Base: `origin/main@edd65eb363ffd23428f492b4a1de8613599fd85e`

This stage converted the Stage 4B migration planning matrix into an exact USER-reviewable execution packet. It planned the active-state migration run and did not write central external records, update active external state, run helper `--apply` operations, create worktree-local staging, move repo docs, delete repo docs, archive repo docs, transition validators, or mutate FAM worktrees.

Stage 4C evidence:

- Scanner command: `python dev\orin_repo_live_state_leakage_scan.py --repo "C:\Nexus Worktrees\Governance" --max-findings 50 --strict`
- Scanned Files: `136`
- Findings: `5909`
- Blocking Leakage Findings: `0`
- Scan Result: `CLEAR / MIGRATION CANDIDATES ONLY`
- Classification Summary: `Durable Historical Receipt: 5006`; `Durable Rule Reference: 396`; `Migration Candidate: 408`; `Review Candidate: 18`; `Transition-Legal Current Owner: 81`
- External root report: `C:\Nexus Governance State` exists and passes canonical root check with schema `external-state-v1`; its recorded Source Repo HEAD is `7f17b97bac1f0ec7d9e424fdfa8792fe420eb885`, so any future migration execution must snapshot and reconcile the external root against the then-current `origin/main` before writing.

Stage 4C execution preflight:

1. Verify the Governance worktree is clean, on `feature/release-readiness-source-truth-intake`, and equal to fetched `origin/main`.
2. Verify `C:\Nexus Governance State` exists, is outside every Git worktree, declares `External State Schema: external-state-v1`, and reports a clear canonical-root check.
3. Verify external root Source Repo HEAD is reconciled to the current migration source commit or explicitly recorded as stale with a USER-approved migration preflight decision.
4. Acquire the state-root lock before migration-wide inspection and the migration lock before any future execution write.
5. Acquire narrower worktree, branch, release-window, review-bundle, fold-down, or governance-candidate locks before writing those partitions.
6. Create a snapshot before any active-state migration write and record the snapshot manifest, schema version, timestamp, source root, checksum posture, and changed state files.
7. Validate planned records before writing them, then write temp files, validate temp files, replace atomically, append audit log entries, and release locks.
8. Treat mixed or unsupported schema values as `External State Schema Conflict`.
9. Treat central target version changes between read and write as `External State Version Conflict`.
10. Do not delete, move, archive, or rewrite repo docs during the execution run; repo cleanup remains a separate USER-reviewed stage after external records exist.

Stage 4C target external record list:

| Target Record | Planned Source Evidence | Planned Purpose | Write Approval Status |
| --- | --- | --- | --- |
| `central\active_branch_authority_state.md` | `Docs\branch_records\index.md` and active branch authority records | Accepted operational active-branch authority state after migration | Future USER-approved execution only |
| `central\selected_next_state.md` | compact roadmap/backlog selected-next posture and USER decisions | Selected-next operational posture after migration | Future USER-approved execution only |
| `worktrees\<worktree_label>\worktree_state.md` | `Docs\worktree_slots.md`, branch records, and Git/worktree helper truth | Current worktree assignment and acknowledgement posture | Future USER-approved execution only |
| `branches\<branch_slug>\branch_state.md` | active branch record operational fields | Active branch phase, blockers, next legal phase, and USER decisions | Future USER-approved execution only |
| `branches\<branch_slug>\branch_plan.md` | active branch plan | Active planning packet and Workstream/Hardening/Live Validation intent | Future USER-approved execution only |
| `branches\<branch_slug>\ufd_ledger.md` | active branch plan UFD section | Active USER feedback disposition while branch is open | Future USER-approved execution only |
| `branches\<branch_slug>\change_intent_ledger.md` | active branch plan Branch Change Intent Ledger | Active changed-surface intent evidence | Future USER-approved execution only |
| `branches\<branch_slug>\element_to_phase_matrix.md` | active branch plan Element-to-Phase Proof Matrix | Active implementation/proof path matrix | Future USER-approved execution only |
| `branches\<branch_slug>\pr_readiness_state.md` | Git/GitHub/helper PR evidence plus durable branch receipts | Optional PR readiness snapshot, not live GitHub truth | Future USER-approved execution only |
| `release_windows\<release_slug>\release_window_state.md` | Release Readiness packet, Git/GitHub release/tag truth, and durable receipts | Current release-window assembly after migration | Future USER-approved execution only |
| `review_bundles\<worktree_label>\manifest.md` | local USER hub helper output and START_HERE metadata | Local-private USER review bundle manifest | Future USER-approved execution only |
| `cross_worktree_lessons\<lesson_id>.md` | governance intake digests and worktree acknowledgement conflicts | No-loss cross-worktree lessons queue | Future USER-approved execution only |
| `governance_candidates\<candidate_id>.md` | proposed rules from lessons, digests, or branch packets | Non-binding governance candidate queue | Future USER-approved execution only |
| `promotion_packets\<packet_id>.md` | staged state proposal and conflict scan | State promotion packet from staging to central | Future USER-approved execution only |
| `acknowledgements\<worktree_label>\<ack_id>.md` | post-merge rebaseline/acknowledgement packets | Worktree acknowledgement after merged governance changes | Future USER-approved execution only |

Stage 4C repo durable receipt preservation plan:

- `Docs\Main.md` remains the repo loader and source-truth router; it should point to durable governance and context owners, not live operational state.
- `Docs\branch_records\index.md` remains durable routing law and historical receipt index until a later approved cleanup makes it pointer-only.
- `Docs\branch_records\<branch>.md` files preserve durable approvals, USER decisions, PR/merge/release receipts, and final fold-down history; active operational fields migrate only after USER-approved execution.
- `Docs\branch_plans\<branch>.md` files remain active owners until migration execution is approved; after migration and fold-down, repo retention/deletion/archive requires a separate USER decision.
- `Docs\feature_backlog.md` and `Docs\prebeta_roadmap.md` remain durable compact product/family/stage pointers; selected-next or release-window operational posture migrates only after USER-approved execution.
- `Docs\worktree_slots.md` remains a stable slot-definition and routing surface; live assignment and acknowledgement posture migrate only after USER-approved execution.
- Workstream and family vision docs keep durable product direction and folded receipts; they must not become external operational state shadows.

Stage 4C rollback and recovery plan:

- If lock acquisition, schema validation, external root validation, version checks, or source commit reconciliation fails, stop before writes and return the exact blocker.
- If a future execution write fails before atomic replacement, discard temp files, preserve the pre-write snapshot, and return a recovery packet.
- If a future execution write fails after atomic replacement but before audit logging, stop on `External State Corrupt` or `Stale Lock Recovery Required` and require USER-reviewed recovery.
- If central state conflicts with worktree-local staging or a concurrent branch update, stop on `External State Version Conflict` or `External State Owner Conflict`; do not merge by inference.
- Promotion never deletes staging source by default. Staging source may expire or archive only after promotion result and audit log exist.

Stage 4C USER review question:

```text
Do you approve a future External Operational State Store active-state migration execution run using this exact preflight, target external record list, repo durable receipt preservation plan, and rollback/recovery plan, with no repo file movement, deletion, archival, validator transition, release execution, runtime work, or FAM worktree mutation unless separately approved?
```

Stage 4C non-includes unless separately approved:

- helper `--apply` operations
- central external record creation or update
- worktree-local `.nexus_state_staging` creation or promotion
- active-state migration execution
- external state schema changes
- moving, deleting, archiving, or renaming repo docs
- transitioning repo validators into mandatory external-state checks
- mutating FAM-006 or FAM-007 worktrees
- release execution, runtime implementation, issue work, branch cleanup, or private-state backup

## Docs Split Stage 4 - Active-State Migration Execution Receipt

Stage Status: `Complete - external operational records seeded`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 4 Source Repo HEAD: `5abdd9c011c80f5b7b57d473b973654a2427d5a8`
External Root: `C:\Nexus Governance State`

Stage 4 active-state migration execution ran after PR #229 merged and after separate USER approval. It updated only `C:\Nexus Governance State`; it did not move, delete, archive, or rewrite repo Docs, did not create worktree-local staging, did not mutate FAM-006 or FAM-007 worktrees, and did not execute release/runtime work.

Stage 4 execution proof:

- Snapshot: `C:\Nexus Governance State\snapshots\snapshot-20260526T183300Z-37259320`
- Manifest Source Repo HEAD: `5abdd9c011c80f5b7b57d473b973654a2427d5a8`
- Target Records Promoted: `15`
- Locks Acquired And Released: `8`
- Audit Entries After Execution: `17`
- Completion Audit: `C:\Nexus Governance State\audit_log\stage4_active_state_migration_completion_20260526T1838Z.json`
- Validation: `python dev\orin_external_state_validation.py --root "C:\Nexus Governance State" --repo "C:\Nexus Worktrees\Governance" --require-root` returned PASS before Stage 5 work began.

Stage 4 target records now exist at:

- `central\active_branch_authority_state.md`
- `central\selected_next_state.md`
- `worktrees\Governance\worktree_state.md`
- `branches\feature_release_readiness_source_truth_intake\branch_state.md`
- `branches\feature_release_readiness_source_truth_intake\branch_plan.md`
- `branches\feature_release_readiness_source_truth_intake\ufd_ledger.md`
- `branches\feature_release_readiness_source_truth_intake\change_intent_ledger.md`
- `branches\feature_release_readiness_source_truth_intake\element_to_phase_matrix.md`
- `branches\feature_release_readiness_source_truth_intake\pr_readiness_state.md`
- `release_windows\current_release_window_state.md`
- `review_bundles\Governance\manifest.md`
- `cross_worktree_lessons\queue_state.md`
- `governance_candidates\queue_state.md`
- `promotion_packets\stage4_active_state_migration_execution_20260526.md`
- `acknowledgements\Governance\stage4_active_state_migration_execution_ack.md`

## Docs Split Stage 5 - Validator Transition

Stage Status: `Historical - validator transition landed through PR #230`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 5 Base: `origin/main@5abdd9c011c80f5b7b57d473b973654a2427d5a8`

Stage 5 transitions validation posture after the approved Stage 4 external records exist. Repo validators remain clean-clone safe and must not require `C:\Nexus Governance State` in GitHub Actions or clean-clone validation. Local Governance workflows may require external operational validation only when the workflow explicitly depends on active local state, release-readiness analysis, worktree coordination, external-state migration, lock/snapshot/recovery, or user-review external-state evidence.

Stage 5 deliverables:

- `dev/orin_external_state_validation.py` gains an opt-in migrated-record check through `--require-stage4-records`.
- `--expected-source-head <sha>` may be used to prove the manifest and required migrated markdown records match the current approved source repo HEAD.
- The helper still treats a missing external root as clean-clone-safe unless `--require-root` is supplied.
- Lock validation blocks local operational workflow on unreleased locks with `Stale Lock Recovery Required`.
- Source truth is updated so future Codex does not treat local external-state validation as mandatory repo CI.

Stage 5 validation command:

```text
python dev\orin_external_state_validation.py --root "C:\Nexus Governance State" --repo "C:\Nexus Worktrees\Governance" --require-root --require-stage4-records --expected-source-head 5abdd9c011c80f5b7b57d473b973654a2427d5a8
```

Stage 5 non-includes unless separately approved:

- repo Docs file movement, deletion, archival, or broad cleanup
- worktree-local `.nexus_state_staging` creation
- FAM-006 or FAM-007 worktree mutation
- release execution, runtime implementation, issue work, branch cleanup, private-state backup, or new external schema migration

## Docs Split Stage 6 - Repo Cleanup Planning

Stage Status: `Historical - repo cleanup planning landed through PR #231`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 6 Base: `origin/main@752d61c60a2b362a17d7c8c700c98bfe65835f08`

Stage 6 is a USER-reviewable cleanup plan after Stage 4 external records exist and Stage 5 local validation is in place. It decides which repo Docs live-state fields should later become pointer-only, external-only, or durable historical receipts. It does not move, delete, archive, rename, collapse, or rewrite repo Docs.

Stage 6 evidence:

- Scanner command: `python dev\orin_repo_live_state_leakage_scan.py --repo "C:\Nexus Worktrees\Governance" --max-findings 12 --strict`
- Scanned Files: `136`
- Findings: `5926`
- Blocking Leakage Findings: `0`
- Scan Result: `CLEAR / MIGRATION CANDIDATES ONLY`
- Classification Summary: `Durable Historical Receipt: 5006`; `Durable Rule Reference: 410`; `Migration Candidate: 408`; `Review Candidate: 18`; `Transition-Legal Current Owner: 84`
- External root report: `C:\Nexus Governance State` exists and passes canonical root check with schema `external-state-v1`; its manifest remains anchored to the Stage 4 migration source repo HEAD `5abdd9c011c80f5b7b57d473b973654a2427d5a8`.

Stage 6 cleanup planning rule:

Repo cleanup execution is not legal until a later USER-approved cleanup execution packet names the exact files, exact fields/sections, replacement owner, receipt preservation plan, validation commands, and review bundle. Stage 6 may recommend cleanup lanes, but it must not modify the candidate repo surfaces merely to make the scanner output smaller.

Stage 6 cleanup execution preflight for a future stage:

1. Rebaseline Governance and neutral main to current `origin/main`.
2. Run the repo live-state leakage scanner and compare current findings against this Stage 6 plan.
3. Validate the external root; if cleanup depends on Stage 4 records, run the Stage 5 local external-state validation command.
4. Reconcile or explicitly waive the external root Source Repo HEAD mismatch if the cleanup execution depends on post-Stage-4 repo state.
5. For each proposed cleanup edit, name the replacement owner as repo durable truth, central external state, Git/GitHub/helper-derived live truth, or historical receipt.
6. Preserve durable USER decisions, accepted branch vision, PR/merge/release evidence, validation proof, and public/product release interpretation.
7. Create a local USER hub review packet with the exact files and before/after cleanup intent.
8. Stop on `Fold-Down Decision Missing`, `Repo Live-State Leakage`, `External State Missing`, `External State Version Conflict`, or `USER Decision Required` when ownership is unclear.

Stage 6 cleanup lane matrix:

| Cleanup Lane | Candidate Surfaces | Target Posture | Cleanup Planning Decision | Future Execution Approval Needed |
| --- | --- | --- | --- | --- |
| Compact pointer surfaces | `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, `Docs/worktree_slots.md` | Repo keeps durable family/stage/slot definitions and pointers; live selected-next, release-window, active branch, and worktree assignment state belongs to Git/GitHub/helpers or `C:\Nexus Governance State` | First recommended cleanup execution lane because it should reduce release-loop drift without deleting receipts | Required before any wording rewrite |
| Branch authority routing | `Docs/branch_records/index.md` | Repo keeps durable routing law, active standing Governance exception, historical receipt index, and pointer to external active operational state | Candidate for second cleanup lane after pointer surfaces | Required before active authority lists become pointer-only |
| Historical branch records | `Docs/branch_records/*.md` | Repo keeps USER approvals, phase decisions, PR/merge/release receipts, validation proof, accepted vision, and final fold-down history; active operational state moves external | Planning says preserve first; do not bulk shrink or delete | Required per family/branch group before edits |
| Branch plans | `Docs/branch_plans/*.md`, `Docs/branch_plans/retirement_index.md` | Active plans live external after transition; repo plans remain schema, transition evidence, durable receipts, or indexed historical references | Candidate for focused review after branch authority routing | Required before any retirement rewrite, archive, or deletion |
| Workstream and family dossiers | `Docs/workstreams/*.md`, `Docs/family_visions/*.md` | Repo keeps durable package/slice/proof history and reusable family direction; live watcher, PR, selected-next, or release-window state should not appear as current truth | Review-only unless scanner identifies active live-state leakage | Required before edits |
| Governance law and loader chain | `Docs/Main.md`, `Docs/phase_governance.md`, `Docs/governance_efficiency_operating_model.md`, `Docs/validation_helper_registry.md`, this plan | Repo keeps durable law, stage boundaries, helper registry, and source-truth routing | Keep as durable source truth; update only for stage transitions | Required for future stage changes |
| Generated review/audit surfaces | `Docs/governance_docs_full_inventory_reform_audit.md`, `Docs/governance_docs_reform_user_review_index.md` | Generated review surfaces should be refreshed only by their generator when the cleanup execution changes source files | Regenerate only after approved cleanup execution | Required if generated outputs would change |

Stage 6 recommended next cleanup execution lane:

Start with compact pointer surfaces only: `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/worktree_slots.md`. These surfaces already declare that they should not own live state, and the scanner reports migration candidates there. The future execution packet should make them more pointer-only without moving files or deleting historical receipts.

Stage 6 USER review question:

```text
Do you approve a future External Operational State Store repo cleanup execution lane for compact pointer surfaces only (`Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/worktree_slots.md`), with exact before/after review bundle and no branch-record/branch-plan deletion, archive, file movement, FAM worktree mutation, release execution, or runtime work unless separately approved?
```

Stage 6 non-includes unless separately approved:

- editing `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, or `Docs/worktree_slots.md`
- moving, deleting, archiving, renaming, or broad-migrating repo Docs
- rewriting historical branch records or branch plans
- creating worktree-local `.nexus_state_staging`
- mutating FAM-006 or FAM-007 worktrees
- release execution, runtime implementation, issue work, branch cleanup, private-state backup, or new external schema migration

## Docs Split Stage 6A - Compact Pointer-Surface Cleanup Execution

Stage Status: `Historical - compact pointer cleanup landed through PR #232`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 6A Base: `origin/main@1cc2b6aa9b821471bf05323226de3e55253b8149`

Stage 6A executes the first cleanup lane from Stage 6. It edits only the compact pointer surfaces that were named in the Stage 6 review packet:

- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/worktree_slots.md`

Stage 6A cleanup intent:

- Keep feature-family identity, broad package posture, family vision pointers, branch/detail owner pointers, stage-breakpoint meaning, and stable slot definitions.
- Remove or compress selected-next, live branch, live PR, release-window, worktree assignment, and long branch-history narration from compact pointer surfaces.
- Route current operational selection, worktree assignment, branch creation posture, and live release-window truth to Git/GitHub/helpers and `C:\Nexus Governance State`.
- Preserve durable receipts by pointer instead of copying PR-by-PR and branch-by-branch history into compact surfaces.

Stage 6A replacement owners:

| Removed / Compressed Fact Class | Replacement Owner |
| --- | --- |
| Selected-next operational posture | `C:\Nexus Governance State\central\selected_next_state.md`, future Branch Readiness packet, and Git/GitHub/helper evidence |
| Live branch / PR / release-window truth | Git/GitHub/helpers; release-window external state when needed |
| Current runtime worktree assignment | `C:\Nexus Governance State\worktrees\<worktree_label>\worktree_state.md` plus live worktree preflight |
| Detailed branch history, fold-down proof, and release interpretation | canonical branch records, branch plans, family visions, workstream dossiers, and public release receipts |

Stage 6A non-includes unless separately approved:

- editing `Docs/branch_records/index.md`
- rewriting historical branch records or branch plans
- moving, deleting, archiving, renaming, or broad-migrating repo Docs
- creating worktree-local `.nexus_state_staging`
- mutating FAM-006 or FAM-007 worktrees
- release execution, runtime implementation, issue work, branch cleanup, private-state backup, or new external schema migration

## Docs Split Stage 6B - Branch-Authority Routing Cleanup Planning

Stage Status: `Active branch-authority routing cleanup planning`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 6B Base: `origin/main@0551e7e16832cbae426ac387d3260b0c7c302344`

Stage 6B plans the second cleanup lane from Stage 6. It does not edit `Docs/branch_records/index.md` yet. It defines how that file can stop acting as a live active-branch operations list while preserving the standing Governance intake exception and durable historical routing.

Stage 6B cleanup intent:

- Keep `Docs/branch_records/index.md` as repo durable branch-record routing law, branch-record schema, historical receipt index, and standing Governance intake authority owner.
- Move non-standing active runtime/workstream branch authority posture to `C:\Nexus Governance State\central\active_branch_authority_state.md` and branch-specific external records after execution.
- Keep historical branch records in repo as durable receipts unless a later branch-record cleanup lane names an exact preservation, archive, or deletion decision.
- Preserve the standing Governance branch as the only repo-tracked active authority exception until USER approves a different operating model.

Stage 6B proposed `Docs/branch_records/index.md` future execution:

| Future Edit Area | Target Posture | Replacement Owner |
| --- | --- | --- |
| Active runtime/workstream branch list | Replace with a pointer to external active operational state and a rule that live active branch truth is derived | `C:\Nexus Governance State\central\active_branch_authority_state.md`, branch external records, Git/GitHub/helpers |
| Standing Governance authority | Keep as explicit repo-tracked active exception | `Docs/branch_records/feature_release_readiness_source_truth_intake.md` |
| Historical branch record index | Keep durable historical receipt routing | `Docs/branch_records/*.md` and future generated index support if approved |
| Branch authority rules and blockers | Keep durable governance law | `Docs/phase_governance.md`, `Docs/branch_records/index.md`, validators |

Stage 6B future execution preflight:

1. Rebaseline Governance and neutral main to current `origin/main`.
2. Validate `C:\Nexus Governance State` and confirm the external active-branch authority record exists or is explicitly not required for planning-only posture.
3. Run `python dev\orin_branch_governance_validation.py` and `python dev\orin_branch_governance_validation.py --standing-governance-intake-gate`.
4. Run the repo live-state leakage scanner and capture current `Docs/branch_records/index.md` findings.
5. Produce an exact before/after review bundle for `Docs/branch_records/index.md`.
6. Preserve the standing Governance authority record as the only active repo authority exception.
7. Stop on `External State Missing`, `External State Version Conflict`, `Standing Governance Intake Not Rebased`, `Branch Authority Routing Owner Missing`, or `USER Decision Required`.

Stage 6B non-includes unless separately approved:

- editing `Docs/branch_records/index.md`
- editing any `Docs/branch_records/*.md` detail record
- editing branch plans, workstreams, family visions, or generated audits
- moving, deleting, archiving, renaming, or broad-migrating repo Docs
- creating worktree-local `.nexus_state_staging`
- mutating FAM-006 or FAM-007 worktrees
- release execution, runtime implementation, issue work, branch cleanup, private-state backup, or new external schema migration

## Docs Split Stage 6C - Branch-Authority Routing Cleanup Execution

Stage Status: `Active branch-authority routing cleanup execution`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 6C Base: `origin/main@8d0301cd547380e35431ce7f211f2589ce1c8fb1`

Stage 6C executes the `Docs/branch_records/index.md` cleanup planned in Stage 6B. It edits the index and stage-boundary source truth only; it does not edit branch detail records, branch plans, generated audits, or external state contents.

Stage 6C cleanup intent:

- Keep `Docs/branch_records/index.md` as durable branch-record law, required branch-record schema, historical receipt routing, and the single standing Governance active-authority exception.
- Stop treating the repo-tracked `Active Branch Authority Records` section as a general live operations ledger for non-standing active branches.
- Route non-standing active runtime, implementation, release-packaging, repair, selected-next, PR, watcher, release-window, and worktree operational authority to `C:\Nexus Governance State\central\active_branch_authority_state.md`, branch-specific external records, and Git/GitHub/helper live checks.
- Preserve historical branch records in repo as durable receipt evidence until a later exact branch-record / branch-plan cleanup lane names the preservation, compaction, archive, or deletion decision.

Stage 6C replacement owners:

| Removed / Compressed Fact Class | Replacement Owner |
| --- | --- |
| Non-standing active branch authority list | `C:\Nexus Governance State\central\active_branch_authority_state.md`, branch-specific external records, and Git/GitHub/helper live checks |
| Standing Governance active exception | `Docs/branch_records/index.md` and `Docs/branch_records/feature_release_readiness_source_truth_intake.md` |
| Historical branch record routing | `Docs/branch_records/index.md` historical index until generated index support is separately approved |
| Branch-record law, blocker names, and schema fields | `Docs/branch_records/index.md`, `Docs/phase_governance.md`, and durable repo validators |

Stage 6C non-includes unless separately approved:

- editing any `Docs/branch_records/*.md` detail record except the standing Governance intake record that owns this RRI cycle
- editing branch plans, workstreams, family visions, or generated audits
- moving, deleting, archiving, renaming, or broad-migrating repo Docs
- creating worktree-local `.nexus_state_staging`
- mutating FAM-006 or FAM-007 worktrees
- release execution, runtime implementation, issue work, branch cleanup, private-state backup, or new external schema migration

## Docs Split Stage 6D - Branch Detail Record / Branch Plan Cleanup Planning

Stage Status: `Active branch-detail-record / branch-plan cleanup planning`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 6D Base: `origin/main@d74d07d2846044cdc8859e769ebe3410d3cf5b62`

Stage 6D plans the next cleanup family. It does not edit branch detail records, branch plans, generated audits, or external state. It exists to prevent a broad lossy rewrite by defining exact batches, preservation rules, replacement owners, and validation preflight before any active operational fields are removed from branch records or branch plans.

Stage 6D cleanup objectives:

- Preserve branch records as durable authority receipts, phase history, USER approvals, release interpretation, PR/merge/release evidence, validation proof, accepted vision summaries, and final fold-down history.
- Preserve active branch planning in external operational state after transition; repo branch plans remain schema, transition evidence, or historical planning receipts, and after fold-down they retire behind `Docs/branch_plans/retirement_index.md`.
- Remove or compress live operational fields only after a later execution lane proves external replacement owners, durable receipt retention, and no-loss auditability.
- Keep detailed USER Feedback Disposition, Branch Change Intent Ledger, Element-to-Phase matrix, Workstream Entry review, Hardening plan, Live Validation plan, and PR readiness state external while active.
- Keep repo branch records and branch plans readable from a clean clone as durable historical receipts even when active operational state lives outside the repo.

Stage 6D future cleanup batches:

| Batch | Candidate Surfaces | Future Execution Goal | Non-Loss Requirement |
| --- | --- | --- | --- |
| Batch A - historical branch-record posture cleanup | `Docs/branch_records/*.md` historical records except the standing Governance record | remove active/open/current-state wording that is no longer durable receipt truth; preserve PR/merge/release evidence and USER decisions | before/after review bundle plus release/tag/PR evidence references |
| Batch B - active-to-external branch-plan cleanup | `Docs/branch_plans/*.md` active or retired plans | convert active operational planning posture into historical receipt or external-state pointer posture after external replacement is proven | retirement index update, external replacement-owner pointer, and no-loss proof |
| Batch C - standing Governance exception preservation | `Docs/branch_records/feature_release_readiness_source_truth_intake.md` | keep the single standing authority record active while reducing cycle-local operational narration by future exact lanes only | preserve One Active Cycle, Sync Rule, Return Digest, and worktree confinement markers |
| Batch D - generated audit and index follow-up | generated reform audits or inventories only if source truth requires refresh | update generated views after cleanup execution, not before | generator source and output must match current HEAD and review bundle count proof |

Stage 6D replacement-owner map:

| Active Operational Fact Class | External / Derived Owner |
| --- | --- |
| active branch state and phase posture while current | `C:\Nexus Governance State\branches\<branch_slug>\branch_state.md` plus Git/GitHub/helper live checks |
| active branch plan while current | `C:\Nexus Governance State\branches\<branch_slug>\branch_plan.md` |
| USER Feedback Disposition while active | `C:\Nexus Governance State\branches\<branch_slug>\ufd_ledger.md` |
| Branch Change Intent Ledger while active | `C:\Nexus Governance State\branches\<branch_slug>\change_intent_ledger.md` |
| Element-to-Phase matrix while active | `C:\Nexus Governance State\branches\<branch_slug>\element_to_phase_matrix.md` |
| Workstream Entry / Hardening / Live Validation planning while active | `C:\Nexus Governance State\branches\<branch_slug>\workstream_entry_review.md`, `hardening_plan.md`, and `live_validation_plan.md` |
| PR readiness, watcher, and live PR operational state | Git/GitHub/helpers plus optional external PR-readiness snapshot |
| durable folded receipt after USER approval | repo branch record, family vision, workstream dossier, release receipt, or branch-plan retirement index |

Stage 6D future execution preflight:

1. Rebaseline Governance and neutral main to current `origin/main`.
2. Run the repo live-state leakage scanner with paths `Docs/branch_records` and `Docs/branch_plans`.
3. Confirm approved external records exist for every active operational fact class being removed or compressed.
4. Produce a no-loss review bundle showing before/after posture for every edited branch record or branch plan.
5. Preserve USER decisions, accepted vision, release interpretation, PR/merge/release evidence, and validation proof.
6. Update `Docs/branch_plans/retirement_index.md` when branch-plan active posture changes to retired/historical pointer posture.
7. Stop on `External State Missing`, `External State Version Conflict`, `Branch Detail Receipt Loss Risk`, `Branch Plan Retirement Owner Missing`, `Generated Audit Drift`, or `USER Decision Required`.

Stage 6D non-includes unless separately approved:

- editing branch detail records or branch plans
- editing generated audits or generated indexes
- moving, deleting, archiving, renaming, or broad-migrating repo Docs
- creating worktree-local `.nexus_state_staging`
- mutating FAM-006 or FAM-007 worktrees
- release execution, runtime implementation, issue work, branch cleanup, private-state backup, or new external schema migration

## Docs Split Stage 6E - No-Loss Cleanup Closure

Stage Status: `Active no-loss cleanup closure`
Source Branch: `feature/release-readiness-source-truth-intake`
Source Worktree: `C:\Nexus Worktrees\Governance`
Stage 6E Base: `origin/main@9fa9f4300e3be9cd51319cc62ec384a61cf0b456`

Stage 6E closes the branch-detail-record / branch-plan cleanup family without broad rewriting. Stage 6D planned cleanup batches, then validation evidence showed that branch records and branch plans are not producing blocking repo live-state leakage. The safe execution is therefore a no-loss closure: keep these files as durable receipts, schema surfaces, or historical transition evidence, and do not rewrite them just to reduce scanner counts.

Stage 6E execution finding:

- `Docs/branch_records` scan: `Repo Live-State Leakage Scan Result: CLEAR / MIGRATION CANDIDATES ONLY`; `Blocking Leakage Findings: 0`.
- `Docs/branch_plans` scan: `Repo Live-State Leakage Scan Result: CLEAR / MIGRATION CANDIDATES ONLY`; `Blocking Leakage Findings: 0`.
- Branch detail records are predominantly durable historical receipts, transition-legal current owners, or durable rule references.
- Branch plans are classified as durable historical receipts or durable rule references by the current scanner.
- Stage 6C already removed the repo index as a general live active-authority operations list.
- Broad branch-record or branch-plan rewrites would risk losing USER decisions, accepted vision, PR/merge/release evidence, validation proof, and durable receipt context.

Stage 6E closure rule:

Branch records and repo branch-plan files remain in repo as durable receipts, schema surfaces, transition evidence, templates, or historical planning records unless a later validator reports blocking `Repo Live-State Leakage` or USER approves an exact no-loss cleanup lane for named files. Active operational ownership and active branch planning are external or derived by contract; durable receipt preservation wins over cosmetic shrinkage.

Stage 6E completed owner split:

| Fact Class | Final Owner After Stage 6E |
| --- | --- |
| active operational branch authority | `C:\Nexus Governance State\central\active_branch_authority_state.md`, branch-specific external records, and Git/GitHub/helper live checks |
| compact backlog / roadmap / worktree-slot posture | repo pointer surfaces cleaned in Stage 6A; live state external or derived |
| branch-record index active list | standing Governance exception only after Stage 6C |
| branch detail records | durable receipts, transition owners, historical evidence, and future exact cleanup candidates only when blocking leakage appears |
| branch plans | external active planning owners after transition; repo copies are schema, transition evidence, historical planning receipts, or retirement-index entries |
| release debt | durable public release truth defects only; stale operational trackers classify as `Repo Live-State Leakage` or external operational state conflict |
| local operational state | `C:\Nexus Governance State` with locks, schema, audit, snapshots, reports, and no-loss promotion posture |

Stage 6E remaining future work:

- Worktree-local `.nexus_state_staging` remains optional and uncreated until USER approves it.
- Repo Docs file movement, deletion, archive, or folder restructuring remains blocked until USER approves a separate exact plan.
- FAM-006 and FAM-007 worktree reconciliation remains paused until USER chooses to rebaseline those worktrees after this Governance transition lands.
- Generated audit refresh is optional unless a validator or USER review reports generated-source drift.
- Future exact branch-record or branch-plan cleanup remains legal only when named files, no-loss preservation, external replacement owners, validation, and review bundle proof are present.

## Problem Statement

Release Readiness keeps blocking on stale live operational state in repo-tracked Docs after branches merge. Recent examples include:

- branch records remaining listed as active after PR merge
- repo branch-plan files retaining active/current posture after their owning branch merges
- roadmap or backlog text carrying selected-next or "no branch exists" posture after live Git truth changes
- worktree slots describing a branch as active after it merges
- release-window and post-release closure state dirtying repo Docs and forcing Governance repair PRs before releases

These are operational coordination problems, not durable public release truth problems. They should not repeatedly require repo PRs when the underlying product, release tag, GitHub Release, and runtime source are already correct.

## Core Split

Repo durable source truth:

- governance laws and phase rules
- development and Codex mode rules
- source-truth ownership and loader routes
- Nexus vision and family visions
- validator/helper registry
- release body and public output standards
- public-safe architecture and durable product direction
- durable folded receipts after USER approval

External operational state:

- active branch state
- active external branch plans
- Workstream Entry review packets
- USER Feedback Disposition while active
- Branch Change Intent Ledger while active
- Element-to-Phase Proof Matrix while active
- current worktree assignment
- release-window assembly
- PR watcher and live PR state snapshots
- USER review bundle manifests
- rebaseline audit packets
- temporary Codex handoff digests
- fold-down previews
- cross-worktree lessons
- governance candidates
- state promotion packets
- worktree acknowledgement records

Derived live truth from Git, GitHub, and helpers:

- `HEAD`
- `origin/main`
- merge base
- dirty state
- ahead/behind
- remote branch existence
- open, merged, or closed PR state
- review-thread state
- issue state
- latest tag
- latest GitHub Release
- release body truth

## Docs Split Target Matrix

Matrix Status: `Current for Docs Split Stage 5`
Matrix Owner: `Docs/external_operational_state_store_reform_plan.md`
Binding Rule Owner: `Docs/governance_efficiency_operating_model.md`
Phase Gate Owner: `Docs/phase_governance.md`

This matrix originated as the Stage 4B/Stage 4C review surface for preventing drift while repo docs still carried transition-legal active operational owners. In Stage 5, it remains the review surface for validator transition and later repo cleanup planning. It does not move files, delete/archive repo docs, create worktree-local staging, or mutate FAM worktrees by itself.

| Surface | Current Repo Role | Target Owner After Migration | Stage 0 Disposition | Drift Risk | Recommendation |
| --- | --- | --- | --- | --- | --- |
| `Docs/Main.md` | first loader and source-truth router | stays repo durable source truth | keep compact pointer to this plan and transition gate | high if Main implies migration is complete | update rarely; route only |
| `Docs/phase_governance.md` | phase rules, blockers, PR/Release gates | stays repo durable source truth | add transition gate and blockers | high if Stage 0, helper bootstrap, and migration blur | keep gate fields deterministic |
| `Docs/governance_efficiency_operating_model.md` | external-state contract and ownership model | stays repo durable source truth | owns binding transition drift gate | high if external candidates become shadow law | keep deterministic rule table |
| `Docs/external_operational_state_store_reform_plan.md` | implementation plan and future-work ledger | stays repo planning/reference surface until migration completes | own matrix, annotations, sequencing | high if treated as active migration authority | label as plan, not root/state |
| `Docs/validation_helper_registry.md` | helper inventory and future validation ownership | stays repo durable source truth | register future external-state helper family and drift-check hook | medium if validators are expected before approved | mark implementation as future |
| `Docs/branch_records/index.md` | active/historical branch authority routing | mixed/split: durable routing stays repo; live active posture migrates external later | keep current until migration stage | high release-loop source | migrate active operational posture later |
| `Docs/branch_records/*.md` | durable branch identity, approvals, phase history, receipts | durable receipts stay repo; active branch state is external after transition | repo current active owners are drift after transition except the standing Governance intake exception | high release-loop source | fold historical receipts, route active records to external state |
| `Docs/branch_plans/README.md` | branch-plan rules and templates | stays repo durable source truth | keep rules; external active plans later use same contract | medium | update only when plan ownership changes |
| `Docs/branch_plans/*.md` | active engineering plans while branch is active | mixed/split: active plans migrate external; durable retired receipts stay repo if approved | current active plans remain legal until migration | high release-loop source | migrate after helper/bootstrap validation |
| `Docs/worktree_slots.md` | stable slot registry and assignment receipts | mixed/split: durable slot definitions stay repo; live assignment migrates external | keep stable slots only | high if live assignment is copied | strip active assignment later |
| `Docs/feature_backlog.md` | compact feature-family registry | stays repo durable source truth | keep identity/pointers only | medium if selected-next returns | avoid live branch/PR posture |
| `Docs/prebeta_roadmap.md` | stage-breakpoint schedule outline | stays repo durable source truth | keep milestones/checkpoints only | high if release-window live state returns | avoid live release-window assembly |
| `Docs/workstreams/` | durable package/slice/proof history | stays repo durable receipt/history | keep promoted historical truth | medium | no live PR/watcher state |
| `Docs/family_visions/` | reusable family product direction | stays repo durable source truth | keep USER-accepted durable direction | low | do not absorb active plans |
| USER review hub packet | local review/export packet | external/local review-bundle state after helper stage | timestamped upload bundle remains helper output | medium if stale zip recurs | keep stale-guard proof |
| Git/GitHub/helper live facts | derived live truth | Git/GitHub/helpers | unchanged | high if copied into docs | derive on demand |

## Canonical Location Model

Canonical external operational state root:

```text
C:\Nexus Governance State
```

Optional worktree-local proposed staging:

```text
<worktree>\.nexus_state_staging\
```

Invalid as canonical operational state unless USER grants a one-off migration waiver:

- repo-root `.nexus_state`
- repo-root `.nexus_local_state`
- repo-root `.nexus_state_staging`
- any folder inside a Git worktree

Repo-root ignored folders may be staging, scratch, or defensive guard paths only. They must not become canonical shared operational truth.

## Proposed External State Layout

```text
C:\Nexus Governance State\README.md
C:\Nexus Governance State\state_index.md
C:\Nexus Governance State\state_manifest.json
C:\Nexus Governance State\schemas\
C:\Nexus Governance State\locks\
C:\Nexus Governance State\central\
C:\Nexus Governance State\worktrees\Governance\
C:\Nexus Governance State\worktrees\FAM-006\
C:\Nexus Governance State\worktrees\FAM-007\
C:\Nexus Governance State\branches\<branch_slug>\
C:\Nexus Governance State\release_windows\<release_slug>\
C:\Nexus Governance State\review_bundles\<worktree_label>\
C:\Nexus Governance State\cross_worktree_lessons\
C:\Nexus Governance State\governance_candidates\
C:\Nexus Governance State\reference_standards\
C:\Nexus Governance State\promotion_packets\
C:\Nexus Governance State\acknowledgements\
C:\Nexus Governance State\snapshots\
C:\Nexus Governance State\audit_log\
```

Generated global indexes such as `state_index.md` are reports, not primary state. Primary state lives in branch, worktree, release-window, candidate, promotion, acknowledgement, and fold-down records.

## Proposed Branch State Layout

```text
branch_state.md
branch_plan.md
branch_plan_review.md
ufd_ledger.md
change_intent_ledger.md
element_to_phase_matrix.md
reference_candidates\
workstream_entry_review.md
hardening_plan.md
live_validation_plan.md
pr_readiness_state.md
fold_down_preview.md
```

## Deterministic Governance Language Contract

Binding external-state rules must use deterministic rule language. Recommendation or planning prose may use softer wording only when explicitly labeled `Non-Binding Planning`.

Every binding rule that controls ownership, mutation, locks, promotion, fold-down, Release Readiness, cross-worktree reconciliation, source-truth ownership, or validator blocking must include:

- Rule Name
- Owner
- Applies To
- Required State
- Allowed Values
- Invalid Values
- Blocking Condition
- Repair Owner
- Repair Path
- USER Decision Required
- Validation Owner
- Final Disposition

Required state models:

- External State Item Status: `Active`, `Queued`, `Promotion Pending`, `Promoted`, `Fold-Down Pending`, `Folded`, `Archived`, `Expired`, `Rejected`, `USER Decision Required`
- Worktree Acknowledgement State: `Pending`, `Accepted`, `Conflict`, `Not Applicable`
- Lock State: `Unlocked`, `Locked`, `Expired`, `Stale`, `Conflict`, `Released`, `Recovery Required`
- Promotion Result: `Approved`, `Rejected`, `Blocked`, `Superseded`, `Folded Into Repo`, `External Only`, `USER Decision Required`
- Release Readiness Live-State Result: `Clear`, `Post-Release External State Carry-Forward`, `External Operational State Conflict`, `Repo Live-State Leakage`, `Durable Release Truth Defect`, `USER Decision Required`
- Reference Candidate Status: `Proposed`, `Under Review`, `Collision Detected`, `Candidate Merged Into Another Candidate`, `Candidate Split`, `Candidate Rejected`, `Candidate Deferred With Owner`, `Candidate Promoted Pending PR`, `Promoted To Source Truth`, `Superseded`, `Not Applicable`, `Withdrawn`
- Reference Collision Class: `Token Conflict`, `Visual Grammar Conflict`, `Geometry Conflict`, `Control-State Conflict`, `Backend Behavior Conflict`, `Proof Standard Conflict`, `Template Conflict`, `Shared Primitive Conflict`, `Naming Conflict`, `Applicability Conflict`, `Variant Conflict`, `Supersession Conflict`

Required named blockers:

- `External State Lock Missing`
- `External State Version Conflict`
- `External State Owner Conflict`
- `External State Promotion Missing`
- `Governance Candidate Not Promoted`
- `Cross-Worktree Acknowledgement Missing`
- `Repo Live-State Leakage`
- `Fold-Down Decision Missing`
- `Release Debt Misclassified`
- `External State Missing`
- `External State Corrupt`
- `External State Schema Conflict`
- `Stale Lock Recovery Required`
- `External State Transition Gate Missing`
- `External State Transition Drift`
- `Docs Split Target Matrix Missing`
- `External State Migration Premature`
- `Reference Candidate Sync Missing`
- `Reference Candidate Collision Unreviewed`
- `Reference Candidate Treated As Canon`
- `Promoted Reference Moved External`

## External State Transition Drift Gate

Gate Status: `Required for external-state reform PR Readiness`
Current Stage: `Stage 6E - No-Loss Cleanup Closure`
External Root Approval: `Bootstrap Approved`
External Root Status: `Initialized`
Migration Status: `Stage 4 active-state migration execution completed externally at source repo HEAD 5abdd9c011c80f5b7b57d473b973654a2427d5a8; Stage 6E closes repo cleanup with no-loss durable receipt preservation`
Validator / Helper Transition Status: `Stage 5 landed - local external-state validation is opt-in and explicit; clean-clone repo validation remains external-root independent`

Required packet fields:

- `External State Transition Gate:`
- `Transition Stage:`
- `Docs Split Target Matrix Status:`
- `Active-State Owner Boundary:`
- `External Root Approval:`
- `External Root Status:`
- `Premature Migration Scan:`
- `Repo Live-State Leakage Scan:`
- `Validator / Helper Transition Status:`
- `Source-Truth Agreement:`
- `Next Approved Step:`
- `Remaining USER Decisions:`

This gate exists so future Codex cannot treat the planning reference, helper scaffolds, root initialization, report-only scanner, active-state migration planning packet, active-state migration execution planning packet, active-state migration execution, validator transition, repo cleanup planning, compact pointer cleanup, branch-authority routing planning, branch-authority routing cleanup, branch-detail-record / branch-plan cleanup planning, no-loss cleanup closure, or broader repo cleanup execution as interchangeable. Stage 6E means closure only: record the scanner-backed no-loss decision and completion posture. It must not edit branch detail records, branch plans, generated audits, move/delete/archive repo files, create worktree-local staging, rely on external state without no-loss preservation proof, mutate FAM worktrees, or let repo files resume active branch status / active branch-plan ownership. Clean-clone repo validators must remain external-root independent.

Drift blockers:

- `External State Transition Gate Missing`: PR Readiness packet omits the gate.
- `External State Transition Drift`: Main, phase governance, governance efficiency, this plan, branch authority, or helper registry disagree on stage, owner, or next step.
- `Docs Split Target Matrix Missing`: the matrix is absent or stale.
- `External State Migration Premature`: helper/bootstrap/root/migration/file-movement work is treated as approved before USER approves that stage.
- `External State Missing`: a local active operational workflow needs external state but the root or required migrated records are absent.
- `Stale Lock Recovery Required`: local external-state validation finds an unreleased or conflicting lock.

Recommended near-term implementation posture:

- keep this branch at Stage 6E until PR/merge and active worktree acknowledgement, then treat the External Operational State Store transition as complete unless a later validator reports blocking leakage
- validate the approved Stage 4 migrated records through explicit local external-state validation when cleanup planning depends on migrated external records
- do not run helper `--apply` operations in this PR
- do not migrate branch records or branch plans in this PR
- require the transition gate in the next external-state implementation PR before Stage 2 / PR creation

## CI And Clean Clone Boundary

Repo validators running in GitHub Actions or clean clones validate durable repo truth only. They must not require access to `C:\Nexus Governance State`.

Local governance validators may require external state only for:

- active local workflow
- Release Readiness analysis
- worktree coordination
- external-state migration
- external-state validation
- lock, snapshot, or recovery workflows

If external state is unavailable in CI, the result is not a repo failure unless repo docs contain live-state leakage.

## Bootstrap Rule

If external state is missing during active local workflow, Codex returns `External State Missing`.

The bootstrap packet must include:

- desired root: `C:\Nexus Governance State`
- worktree label
- source repo path
- branch
- source repo HEAD
- schema version
- initialization scope
- exact USER decision needed

Expected future helper command:

```powershell
python dev\orin_external_state_init.py --root "C:\Nexus Governance State" --worktree "<label>" --repo "<repo_path>" --schema <schema_version>
```

Until USER approves initialization, active operational workflow waits. Analysis-only work may continue only with an explicit analysis-only waiver.

## Schema Migration Rule

Every external state file must name:

- External State Schema
- State Version
- Last Updated
- Last Updated By
- Worktree
- Branch
- Source Repo HEAD

Schema changes require:

- migration packet
- snapshot
- validation
- USER decision
- audit log entry

Mixed or unsupported schema versions return `External State Schema Conflict`.

## Multi-Worktree Concurrency Contract

State ownership partitions:

- branch state
- worktree state
- release-window state
- review-bundle state
- fold-down state
- generated global index state
- cross-worktree lessons
- governance candidates
- promotion packets

Lock scopes:

- state root lock
- migration lock
- release-window lock
- worktree lock
- branch lock
- review-bundle lock
- fold-down lock
- governance-candidate lock

Lock acquisition order:

1. migration
2. release window
3. worktree
4. branch
5. review bundle
6. fold-down
7. governance candidate

Read/write modes:

- read-only
- write
- migration
- fold-down
- recovery

Required state-file version fields:

- State Version
- Last Updated
- Last Updated By
- Worktree
- Branch
- Source Repo HEAD
- External State Schema

Helper behavior expected in implementation:

- detect state version changes between read and write
- return `External State Version Conflict` on changed versions
- write temp file
- validate temp file
- replace atomically
- append audit log
- release lock

Release-window single-writer rule:

- only the active Release Readiness carrier may hold the release-window write lock
- other workstreams may read release-window state

## Stale-Lock Recovery

Stale-lock recovery requires a recovery packet with:

- stale lock ID
- lock owner
- intended write set
- last state version
- current state version
- recovery risk
- exact USER decision needed

Stale lock recovery must not discard or overwrite state when ownership or version risk is unclear.

## Cross-Worktree Lessons

Proposed path:

```text
C:\Nexus Governance State\cross_worktree_lessons\
```

Each lesson record includes:

- Lesson ID
- Origin Worktree
- Origin Branch
- Issue / Failure
- Affected Surfaces
- Affected Worktrees
- Recommended Rule Change
- Recommended Owner
- Severity
- Current Disposition
- Promotion Target
- USER Decision Needed

Allowed dispositions:

- `Local Only`
- `Share As Warning`
- `Governance Candidate`
- `Validator Candidate`
- `Family Vision Candidate`
- `Branch-Plan Template Candidate`
- `Folded Into Repo Source Truth`
- `Rejected / No Action`
- `USER Decision Required`

## Governance Candidates

Proposed path:

```text
C:\Nexus Governance State\governance_candidates\
```

Each governance candidate includes:

- Candidate ID
- Origin Worktree
- Origin Branch
- Proposed Rule
- Reason
- Affected Worktrees
- Affected Source-Truth Owners
- Proposed Repo Owner File
- Validator Impact
- Risk
- USER Decision Needed
- Current Disposition

External governance candidates are not binding governance. They become governing only after USER-approved repo source-truth update and merge.

## State Promotion Packet

Each packet includes:

- Source State
- Target State
- Proposed Change
- Reason
- Affected Worktrees
- Conflict Scan
- Validation Required
- USER Decision Needed
- Final Disposition

Promotion from worktree staging to central state requires:

- lock acquisition
- central state version check
- conflict scan
- validation
- snapshot when risk warrants it
- audit log
- USER decision when shared state, release-window state, selected-next posture, branch authority, fold-down, or cross-worktree lesson state is affected

Promotion does not delete staging source by default. Promotion updates central state, records final disposition, writes the audit log, and preserves staging source until the promotion result exists. Staging may expire or archive only after promotion result and audit log exist.

## Worktree Acknowledgement After Governance Merge

Active worktrees need acknowledgement records after merged governance/source-truth changes that affect:

- phase rules
- branch plan rules
- validator behavior
- source-truth ownership
- Release Readiness
- review bundles
- external state schema
- worktree slots
- any active branch implementation or proof path

Allowed acknowledgement states:

- `Pending`
- `Accepted`
- `Conflict`
- `Not Applicable`

Acknowledgement conflicts return one of:

- rebaseline packet
- branch-plan revision packet
- external state promotion packet
- USER decision packet

## Release Debt Redefinition

Release debt means durable public release truth is missing or wrong.

Examples of true release debt:

- published release tag/body/release notes wrong
- invalid or missing release artifact
- missing durable public milestone summary
- released capability absent from durable product history

These become external operational state updates or repo live-state leakage findings:

- branch record still active
- branch plan still active
- worktree slot stale
- selected-next stale
- PR watcher stale
- release-window operational state stale
- post-release closure state pending

## Release Readiness Post-Reform

Release Readiness reads:

1. Git/GitHub/helper truth: latest tag, latest release, release body, candidate commit, PR merge state.
2. External Governance State: active branch posture, branch fold-down state, release-window assembly, worktree assignment, review bundle state, carry-forward blockers, unresolved cross-worktree lessons, unresolved governance candidates.
3. Repo durable docs: product vision, governance contracts, family direction, durable release milestone posture, folded historical receipts.
4. Repo live-state leakage scan: active branch fields in repo, active worktree assignment in repo, PR/watcher state in repo, release-window assembly in repo, selected-next operational posture in repo.

Release Readiness blocks on:

- `Durable Release Truth Defect`
- `External Operational State Conflict`
- `Repo Live-State Leakage`
- `Post-Release Canon Closure Drift` when repo durable receipts for an included published release window still keep current `merged-unreleased` posture instead of released/closed or explicitly historical pre-release snapshot evidence
- `Governance Candidate Not Promoted` when it affects durable release truth, public safety, validator correctness, or source-truth ownership
- `USER Decision Required`

`Post-Release External State Carry-Forward` is the expected state after RR2 release publication when external operational records still point to the just-released branch, PR, release window, selected-next state, or previous source commit but Git/GitHub/repo release validation is green. It is not release debt, not durable repo canon drift, and not a blocker by itself. Bounded RR2 closeout may reconcile only external operational files to live truth without a new USER decision; if not reconciled there, Branch Readiness Stage 1 reports the carry-forward and Branch Readiness Stage 2 reconciles it before branch/worktree setup or implementation.

Release Readiness remains repo-file-frozen. External Governance State may be read during Release Readiness after USER-approved initialization. External state mutation during Release Readiness requires explicit USER approval except for bounded RR2 post-release external state carry-forward reconciliation, and is limited to operational release-window state or approved external operational state reconciliation.

## Review Bundle Integration

USER review bundles should be able to include external state files when USER review needs them.

External state is local-private by default. Private, Owner, or DEV-sensitive state requires sanitization and USER approval before upload, zip export, public PR attachment, or cloud backup.

## Backup And Snapshot Model

Snapshots are expected before:

- external-state migration
- Release Readiness pass
- branch-plan fold-down
- lock recovery
- high-risk schema migration

Optional daily snapshots may be used during heavy work after USER approval.

Snapshot manifests include:

- schema version
- timestamp
- source root
- checksum
- changed state files

External state must not contain plaintext secrets, tokens, cookies, provider keys, private model files, or owner-private memory unless a later encrypted Owner vault is approved.

## Migration Stages

1. Clear current post-merge source-truth blockers under existing repo rules.
2. Land docs-only source-truth contract for repo durable truth, external operational state, deterministic language, and concurrency model.
3. Implement helper scaffolds: init, report, lock, validate, snapshot, fold-down preview, promotion preview, and promote.
4. Initialize the canonical external root only after explicit USER approval.
5. Record report-only migration preview packets without active-state migration.
6. Implement the report-only repo live-state leakage scanner and migration-map helper.
7. Adopt external state for new or re-entering branches after USER approval.
8. Adopt ignored worktree staging for proposed state only after USER approval.
9. Migrate active branch, worktree, and release-window state out of repo docs after USER approval.
10. Transition validators: repo validators stop requiring live state in repo docs; external validators check operational state.
11. Clean repo docs: remove stale live-state fields and keep durable receipts only.
12. Transition Release Readiness to Git/GitHub truth plus external state plus repo durable truth.
13. Require active worktree acknowledgements after merged governance/source-truth changes.

## Risks And Mitigations

Shadow governance:

- External candidates are non-binding until folded into repo source truth by USER-approved update and merge.

Clean clone breakage:

- CI validates durable repo truth only and must not require `C:\Nexus Governance State`.

External state loss:

- Use snapshots, audit logs, schema validation, and no-loss promotion.

Multi-worktree corruption:

- Use lock scopes, version checks, acknowledgement records, and atomic writes.

Stale generated indexes:

- Treat indexes as generated reports only; primary state lives in records.

Release delay:

- PR #220 was handled under existing rules and released through `v1.7.23-prebeta`; PR #222, PR #223, and PR #224 are handled through `v1.7.25-prebeta` post-release canon closure before external-state implementation begins.

## Annotated Recommendations For Next Governance Pass

Recommendation A - keep Main as a router:

- Status: `Applied in Stage 0`
- Reason: Main must point to the external-state contract and plan without becoming the detailed migration ledger.
- Future risk: if Main starts carrying detailed live-state migration fields, it becomes another live-state owner.

Recommendation B - require the transition gate before external-state PR creation:

- Status: `Applied in Stage 0`
- Reason: this prevents planning from being mistaken for migration complete and catches disagreement between Main, phase governance, governance efficiency, the plan, branch authority, and helper registry.
- Future risk: without this gate, Codex could initialize helpers or demand external state before USER approves bootstrap.

Recommendation C - keep helper work bounded to each approved stage:

- Status: `Applied through Stage 5; report-only helpers stayed report-only until Stage 4 execution approval, and Stage 5 validation remains local/opt-in instead of a clean-clone repo requirement`
- Reason: scanner output should expose migration candidates without rewriting repo docs or creating central active branch/worktree/release-window records.
- Future risk: if scanner output is treated as migration itself, the repo could lose durable receipts or create shadow external truth.

Recommendation D - keep repo cleanup separate from external active-record migration:

- Status: `Stage 4 active external records exist; repo cleanup remains future-gated`
- Reason: moving branch records and plans out of repo without a separate cleanup plan risks losing the exact planning receipts the reform is meant to preserve.
- Future risk: premature file movement could trade release debt for durable receipt loss or external-state corruption.

Recommendation E - keep release debt narrow:

- Status: `Applied in Stage 0`
- Reason: stale operational trackers should become `Repo Live-State Leakage` or external-state updates, not durable release debt.
- Future risk: if Release Readiness keeps treating stale branch/worktree posture as release debt, the repair loop continues.

## Current External-State Sequencing Recommendation

Default path:

1. Complete Stage 6E no-loss cleanup closure after Stage 6D planning has landed and the branch has rebaselined to current `origin/main`.
2. Merge the Stage 6E closure packet only after validation, USER review bundle refresh, and USER approval.
3. Rebaseline or acknowledge active worktrees after merge when USER chooses that sequencing.
4. Resume normal branch work from current `origin/main`; route any future exact branch-record / branch-plan cleanup only when a validator or USER review reports blocking leakage or receipt-safe cleanup need.

External-state implementation does not replace post-release canon closure or become a release unblocker unless USER explicitly pauses release flow and approves that route.

## Future Exact USER Decision Shape

After this Stage 6E no-loss cleanup closure PR merges and active worktrees rebaseline or acknowledge the changed governance when USER chooses that sequencing, the External Operational State Store transition is complete for current repo governance. Future optional cleanup requires a new exact USER decision:

```text
Approve a future exact cleanup only if a validator or USER review names blocking repo live-state leakage or receipt-safe cleanup need. Scope must name exact files, no-loss preservation proof, external replacement owners, validation, and USER review bundle. Do not move/delete/archive repo files, mutate runtime, create releases, clean branches/worktrees, create worktree-local staging, or change FAM-006/FAM-007 without separate USER approval.
```
