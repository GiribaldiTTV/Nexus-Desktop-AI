# Nexus Phase Governance

## Top Rule: Pre-PR Durability

Follow `Docs/phase_governance.md#pre-pr-durability-rule`: local commit, push, PR, merge, release, publication, and live activation are separate explicitly authorized actions.

**Release Readiness is file-frozen: block ANY source, docs, canon, validator, helper registry, release-note, or handoff-file changes discovered or needed during `Release Readiness`. Do not edit, stage, commit, or push in `Release Readiness`; route the change back to `PR Readiness` before merge, or to the next active `Branch Readiness` after merge.**

## Purpose

This document defines the governed execution phases used for Nexus Desktop AI work.

It exists so:

- workstream truth
- validation truth
- closeout truth
- prompt routing
- next-phase recommendations

all use the same phase names, blocker rules, and transition rules.

This is the canonical cross-workstream governance layer.
It does not replace:
- `Docs/Main.md` as the routing index
- canonical workstream docs as branch-local feature-state, evidence, and closure records
- release or rebaseline docs as milestone summaries

## Current Workspace Root Contract

Current root routing is owned by `Docs/nexus_workspace_roots.md`: neutral main
is `D:\Nexus Desktop AI\Product Repository`, active worktrees are under
`D:\Nexus Desktop AI\Worktrees`, external operational state is under
`D:\Nexus Desktop AI\Governance State`, and USER review hubs are under
`D:\Nexus Desktop AI\USER`. Historical
C-drive paths in receipts and fixtures are not current execution targets.

## Exact Prompt Contract

For phase-sensitive execution, prompts must include:

- `Mode: <mode name>`
- `Phase: <exact canonical phase name>`
- `Workstream: <workstream id or equivalent authority record>`
- `Branch: <branch name or No Active Branch>`

Add these fields when relevant:

- `Branch Class: <implementation / release packaging / historical repair context only as canon allows>`
- `Active Seam: <seam name>`
- `Seam Sequence: <ordered seam list>` when the current phase permits a bounded multi-seam pipeline
- `Validation Contract: <summary or authority reference>`
- `Timeout Contract: <summary or authority reference>`

If `Phase` is missing or is not one of the exact canonical phase names below, execution is blocked and only truth-validation or analysis may continue.
If `Seam Sequence` is present, it is structure only.
Prompt text may name the entry seam and downstream planned seams, but it does not define seam behavior, bypass phase rules, or authorize continuation by itself.
The canonical seam workflow contract below controls whether Codex may continue, must stop, or may split a backlog item across branches only with explicit USER approval.

## Mandatory Bounded State Gate

Bounded State is mandatory for every execution pass that can mutate repo files, create or switch branches/worktrees, commit, push, create a PR, handle PR comments, run release actions, launch runtime validation, mutate shortcuts, install providers/models, or hand off GitHub Desktop state.

Before mutation or execution, Codex must prove and report a `Bounded State:` with all of these fields:

- exact phase and stage
- active workspace, git root, branch, upstream, `HEAD`, `origin/main`, worktree role, and write target
- owning workstream or branch authority record
- active package, slice, and seam, or an explicit non-FAM repair carrier allowed by source truth
- exact allowed scope, affected surfaces, and validation contract
- explicit non-includes and pending USER decisions
- stop/report conditions and the next legal phase

If any required bounded-state field is missing, stale, contradictory, or cannot be resolved from source truth, Codex must stop on `Bounded State Missing` before mutation. Analysis may continue only far enough to report the missing field and the exact USER decision needed.

Broad work requests do not authorize implementation. Phrases such as `continue`, `complete all`, `all remaining work`, `finish FAM-007`, `do whatever is next`, or similar broad wording must resolve to the next named bounded same-branch seam already recorded in source truth. If they do not resolve to exactly one active bounded seam, Codex must stop on `Bounded State Missing` or `Next Bounded Workstream Seam Approval Missing`.

Widening beyond the current bounded state requires explicit USER waiver text recorded as `Bounded State User Waiver: Granted`. The waiver must name the branch/worktree, phase, slice/seam, the exact bound being relaxed, allowed extra seams/slices/files, expiration or stop condition, required validation, and still-pending USER decisions. If a task needs wider scope and that waiver is absent, stop on `Bounded State Waiver Missing`.

Clean validation, a clean git tree, branch existence, prior broad approval, Codex discretion, ChatGPT wording, or prompt output shape cannot infer a bounded-state waiver. `Bounded State User Waiver: None` means execute only the named active bounded seam at a time, then continue to the next admitted same-branch seam or slice when the Workstream continuation latch remains active. It does not authorize treating the first seam as a terminal Workstream boundary.

## Prompt-Entry Origin/Main Freshness Gate

Before consequential work, prove current main and the exact carrier identity, refs, merge base, dirt, owner and approval. Read-only remote comparison may establish freshness without changing local refs. If main advanced, determine the incoming change set and its impact on the approved operation. Unrelated advancement does not veto the whole task. A relevant conflict, missing required owner, or unproven baseline blocks only the affected action. Merge, rebase, fast-forward, branch switching and conflict resolution retain separate actual authorization under the Pre-Rebaseline Impact Audit.



## Pre-Rebaseline Impact Audit

`Pre-Rebaseline Impact Audit` is mandatory before any branch, worktree or neutral-main folder merges, rebases, fast-forwards, conflict-resolves, branch-switches, or otherwise baselines itself against a newer `origin/main`.

No Baseline By Inertia: Codex must never treat "behind origin/main", "clean worktree", "already merged", "just housekeeping", or "fast-forward only" as approval to rebaseline without first reporting the audit and receiving USER approval for the recommended mutation path.

The audit packet must include:

- `Pre-Rebaseline Impact Audit:`
- `Incoming Main Change Set:`
- `Incoming Changed Files:`
- `Current Worktree Changed Files:`
- `Branch Changed Files:`
- `Rebaseline Overlap Files:`
- `Incoming Runtime / Source-Truth Risk:`
- `Shared Surface / Worktree Overlap Forecast:`
- `Validation Before Rebaseline:`
- `Recommendation Only:`
- `Rebaseline Mutation Approval:`
- `Rebaseline Mutation Status:`

`Recommendation Only:` must state that the pass reports findings and does not mutate the branch/worktree. `Rebaseline Mutation Approval:` must be `Pending` until the USER approves the exact worktree, branch, target commit, and operation type. `Rebaseline Mutation Status:` must remain `Not started` or `Blocked` until approval exists. If the worktree is dirty, if incoming files touch runtime/provider/UI/source-truth/validator surfaces, if sibling worktrees share files, or if validation fails, the next legal lane is a reported reconciliation decision rather than automatic baseline.

`Rebaseline Overlap Files:` is the intersection of incoming changed files and the current branch/worktree changed files. Current branch/worktree changed files means branch changed files from `merge_base..HEAD` plus staged, unstaged, untracked, or current-worktree changed files when present. When this field is `None`, `Rebaseline Overlap Intent Gate` reports `Not Applicable` and the normal Pre-Rebaseline Impact Audit still controls mutation approval. When this field names any file, Codex must freeze rebaseline mutation, classify every overlapping file, and inspect branch-owned intent before recommending merge, rebase, fast-forward, conflict resolution, or acceptance.

`Rebaseline Overlap Intent Gate` uses the active branch planning owner as the full-detail owner. Runtime branches use the Branch Runtime Engineering Plan shape. Branches with `Rebaseline Overlap Files:` must admit or update the active external Branch Engineering Plan under `D:\Nexus Desktop AI\Governance State\branches\<branch_slug>\branch_plan.md` before rebaseline mutation can proceed. Repo branch-plan files under `Docs/branch_plans/` may provide schema, transition, or historical fallback evidence only; they must not be the active overlap-intent owner after the External Operational State Store transition. The required section is `Branch Change Intent Ledger`; each `Changed Surface: <path>` block records `Surface Class:`, `Change Intent:`, `Why This File Was Touched:`, `Owned Behavior / Fact Class:`, `Canonical Owner / Source Owner:`, `Resolution Owner:`, `Shared Surface:`, `Overlap Risk:`, `Expected Conflict Risk:`, `Semantic Merge Risk:`, `Regression / Gating Impact:`, `Conflict Resolution Rule:`, `Rebaseline Handling:`, `Validation Proof:`, `Fallback Evidence:`, `USER Decision / Waiver:`, and `Fold-Down Target:`. `Regression / Gating Impact:` uses `None`, `Low`, `Medium`, `High`, or `Unknown`; fixture/test overlap with `Medium`, `High`, or `Unknown` impact blocks until evidence or USER decision resolves it.

`Rebaseline Overlap Failure Procedure` triggers when an overlapping file has missing, weak, stale, or conflicting intent evidence. The packet must include `Overall Overlap Gate Result:`, `Rebaseline Overlap Files:`, per-file `File:`, `Surface Class:`, incoming and current branch change summaries, `Branch Change Intent Present:`, `Incoming Intent Evidence Present:`, `Fallback Evidence:`, `Risk:`, `Per-File Result: PASS / WARN / BLOCKED`, `Recommended Resolution:`, `Resolution Owner:`, `Validation Required:`, `USER Decision Needed:`, and `Rebaseline Mutation Status:`. `Overall Overlap Gate Result:` is the highest per-file severity. Any `BLOCKED` file keeps mutation blocked by `Rebaseline Overlap Intent Missing` until repaired, waived, deferred by USER decision, or sequencing changes. Fallback evidence supports classification and USER decision-making only; after the effective point, fallback evidence alone cannot produce `PASS`.

When the USER approves the recommendation, the rebaseline operation must still be constrained to the approved operation type, usually `git merge --ff-only origin/main` for explicitly approved neutral/main synchronization and an explicit merge/rebase/recreate strategy for active implementation branches. After the operation, `Current-Main Reconciliation Identity Guard` must prove origin/main stayed context, not identity, before validation, commit, push, PR Readiness, Release Readiness, or handoff.

### Merged Vision / Proof Standard Adoption Gate

Rule Name: `Merged Vision / Proof Standard Adoption Gate`
Owner: `Docs/phase_governance.md` for phase blocking; the affected Project Vision, Family Vision, Family Feature Vision, branch plan, validation registry, or incident-pattern owner for the standard being adopted.
Applies To: any active, paused, re-entering, or rebased worktree after `origin/main` receives merged source-truth changes that alter product vision, UI/UX standards, FFV sufficiency, deferred carryforward, backend/runtime predictability, frontend/backend truth mapping, reference/template/primitive expectations, proof hierarchy, Live Validation expectations, helper/validator interpretation, or USER review packet requirements.
Required State: The next legal BR1, BR2, BP1, BP2, BP3, Workstream re-entry, Hardening, Live Validation, PR Readiness, or Release Readiness packet for the affected worktree must report whether the merged standard applies to its existing branch work. The packet must name `Merged Standard Source:`, `Rebaseline / Re-entry Event:`, `Current Branch Implementation Inventory:`, `Affected Branch Artifacts:`, `Affected Product Surfaces:`, `Implemented / Touched UI-UX Surfaces:`, `Implemented / Touched Runtime-Backend Surfaces:`, `Affected Proof Claims:`, `Merged Standard Comparison Result:`, `Frontend / Backend Contract Findings:`, `Reference / Template / Primitive Classification:`, `Accepted Reference Set / Comparative Synthesis:`, `UI Reference / Template / Shared Primitive Dependency:`, `Current Violation Findings:`, `Adoption Disposition:`, `Repair / Waiver / Blocker:`, `Issue Candidate Disposition:`, and `No Repo Live-State Tracking:`. For UI/UX standards, the packet must compare the branch's already-implemented or touched surfaces against the current Project Vision, FAM-002 presentation grammar, applicable Family Vision / Family Feature Vision, Visual Inheritance Matrix, Scope Coverage Manifest, Vision-To-Proof Matrix, and Live Validation proof rules. For runtime/backend standards, the packet must compare already-implemented or touched behavior against the Backend Predictability / Reliability Contract, Runtime Branch Engineering Contract, state/config/schema delta, failure/fallback/recovery routes, logging/observability proof, rollback/reversibility path, and frontend/backend truth mapping. It must explicitly classify current output as `No Violation Found`, `Repair Required`, `Route Back To Earlier Gate`, `USER Waiver Required`, `Blocked`, `Issue Candidate Required`, or `Not Applicable With Reason` before advancement. It must either repair branch-local output, route back to the correct earlier gate, future-gate the impact with reason, record an explicit USER waiver, block advancement, or produce a USER-reviewable issue-candidate packet. This adoption check is a phase packet requirement, not a live-state ledger in repo docs.
Allowed Values: `Not Applicable`, `No Affected Surface`, `Adopted`, `Repair Required`, `Route Back To Earlier Gate`, `USER Waiver Required`, `Blocked`, and `Deferred To Next Legal Gate With Reason`.
Invalid Values: `Ignored Because Branch Started Earlier`, `Validator Green Before Standard`, `Will Reconcile Later Without Gate`, `Sibling Worktree Owns It`, `Repo Docs Track Current Adoption State`, `Historical Receipt Failed By New Standard Alone`, `Backend Green Without Runtime Truth`, `UI Green While Backend Unknown`, `Issue Auto-Created From Adoption Scan`, or `FAM Worktree Mutated From Governance Pass`.
Blocking Conditions: `Merged Vision Standard Adoption Missing`, `Merged UI Standard Adoption Missing`, `Merged Backend Predictability Standard Adoption Missing`, `Merged Frontend Backend Contract Adoption Missing`, `Merged Template Dependency Adoption Missing`, `Merged Proof Standard Adoption Missing`, `Merged Standard Implementation Inventory Missing`, `Merged UI-UX Violation Scan Missing`, `Merged Runtime-Backend Violation Scan Missing`, `Reference / Template / Primitive Classification Missing`, `Comparative Synthesis Missing`, `Template Claim Unsupported`, `Shared Primitive Claim Unsupported`, `Accepted Reference Conflict Unrouted`, `Merged UI-UX Standard Violation Unresolved`, `Merged Backend Standard Violation Unresolved`, `Rebaseline Adoption Impact Unclassified`, `Merged Vision Standard Adoption Repair Required`, `Merged Vision Standard Adoption Waiver Missing`, `Merged Vision Standard Adoption Live-State Leakage`, `Issue Candidate Disposition Missing`, `Issue Mutation Approval Missing`, and `Repo File-State Tracking`.
Repair Owner: The affected worktree repairs its own branch-local surfaces under its own legal carrier. The explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable source-truth ambiguity. No worktree may mutate a sibling worktree to perform adoption by convenience.
Repair Path: During the next legal gate after rebaseline, inventory what the current branch already implemented or touched, compare branch output and plans against the new merged standard, name changed files/surfaces/claims and UI/UX/runtime/backend violations if any, decide whether to repair now, route back, future-gate, or create an issue-candidate packet, update only the owning branch-local source truth or external operational state allowed for that gate, and validate before advancing. If the issue applies to already-merged or previous released behavior outside the current branch's legal repair scope, the branch must prepare a USER-reviewable GitHub issue candidate with title, affected FAM/FFV/surface, evidence, expected behavior, owner recommendation, severity, and no auto-close keywords; actual issue creation, labeling, closing, reopening, or commenting remains blocked until USER approves that exact GitHub action.
USER Decision Required: Required for waiver, route-back acceptance, broad scope expansion, sibling-worktree mutation, GitHub issue creation/mutation, or applying the merged standard in a way that changes product/runtime behavior beyond current approval.
Validation Owner: Future helper/validator hardening should extend rebaseline, branch planning, PR Readiness, and Live Validation checks where machine-checkable. Until then, Codex must perform the comparison in the phase digest.
Final Disposition: A branch cannot rely on pre-rebaseline green proof when a newly merged vision/UI/proof standard applies and the adoption impact is unclassified. Historical merged receipts and already-released work do not fail by history alone. FAM-006, FAM-007, and any other active or re-entering product worktrees consume this rule at their own next legal gate after rebaseline; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy may define the rule and return a digest, but it must not mutate those worktrees, active USER packets, or external branch state during a docs-only governance pass.

### Concrete USER-Facing Feature Classification Gate

Rule Name: `Concrete USER-Facing Feature Classification Gate`
Owner: `Docs/phase_governance.md` for phase blockers and PR Readiness admissibility; `Docs/branch_plans/README.md` for Branch Planning fields; `Docs/validation_helper_registry.md` for helper/validator expectations; the affected Project Vision, Family Vision, Family Feature Vision, branch plan, or external operational state owner for branch-specific classification rows.
Applies To: Branch Readiness, BP1, BP2, BP3, Workstream approval, Workstream implementation, Hardening, Live Validation / UTS, PR Readiness, Release Readiness, active external branch plans, USER review packets, and any Codex claim that a branch delivered a feature, is feature-complete, is PR-ready, or can proceed toward release as feature work.
Required State: every planned and delivered work item must be classified as one of `Concrete USER-facing feature`, `Runtime-facing behavior directly supporting a concrete USER-facing feature`, `Foundation / infrastructure`, `Diagnostic / status / trust-boundary`, `Proof / validator / helper`, `Governance / packet / documentation`, or `Cross-FAM dependency support`. The packet must identify any claimed concrete USER-facing feature in plain USER language and answer: what the USER can now do that they could not do before, what useful outcome the system now produces, and whether that outcome is more than explaining unavailable or blocked paths, proving boundaries, or reporting readiness.
Allowed Values: `Concrete USER-facing feature`, `Runtime-facing support`, `Foundation / infrastructure`, `Diagnostic / status / trust-boundary`, `Proof / validator / helper`, `Governance / packet / documentation`, `Cross-FAM dependency support`, `Bounded foundation / infrastructure cycle`, `BP Hold Required`, `PR Readiness Blocked`, `USER-Approved Foundation-Only PR Consideration`, and `Not Applicable With Reason`.
Invalid Values: `Runtime-Visible Therefore Feature`, `Status UI Counts As Feature`, `No-Provider Result Counts As Feature By Itself`, `Blocked-State Explanation Counts As Feature`, `Provider-Visible-Data None Counts As Feature`, `Capability Unavailable Counts As Feature`, `Truthful AI Not Implemented Counts As Feature`, `Validator Green Means Feature Complete`, `Packet Validated Means Feature Complete`, `Proof Helper Green Means PR Ready`, and `Diagnostic Trust Boundary Treated As Concrete Runtime Feature`.
Blocking Conditions: `Concrete Feature Classification Missing`, `Concrete USER-Facing Feature Candidate Missing`, `Feature Delivery Overclaimed`, `Foundation Cycle Not Explicitly Approved`, `Diagnostic / Status Work Masquerading As Feature`, `Proof / Packet Work Masquerading As Feature`, `BP Hold Required`, `PR Readiness Blocked By No Concrete Feature`, and `Foundation-Only PR Consideration Approval Missing`.
Repair Owner: the current branch/worktree repairs its own branch-local classification, active external branch plan, USER packet, and proof language. The explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable source-truth ambiguity. Helper/validator owners repair machine-checkable blind spots only after the source-truth rule is clear. USER owns foundation-only PR consideration approval, waivers, retargeting, or runtime-carrier selection.
Repair Path: inventory planned and delivered work, classify every item, reject diagnostic/status/trust-boundary/proof/governance work as concrete feature delivery by itself, identify any real USER-facing carrier in plain language, and if none exists, hold before PR Readiness, reclassify as a bounded foundation/infrastructure cycle, or return to BP1/BP planning to select the real runtime carrier. PR Readiness can proceed only when a concrete feature was delivered and hardened/validated, or when USER separately approves PR consideration for the explicitly bounded foundation/infrastructure posture.
USER Decision Required: required to approve a foundation-only PR consideration path, waive the concrete-feature requirement, retarget/rename the branch, return to BP1/BP planning after a hold, or select a new runtime carrier.
Validation Owner: future helper/validator coverage should extend existing branch governance, branch readiness planning fixture, and USER review bundle helpers where machine-checkable. Until then, Codex must perform the classification in the phase digest and reject false-green helper output when the deliverable is only diagnostic/status/trust-boundary/proof/governance work.
Final Disposition: a branch cannot be called feature-complete, PR-ready, or release-facing as feature delivery solely because it produces visible status, blocked-state copy, no-provider diagnostics, provider-visible-data transparency, capability unavailable copy, validators, proof helpers, USER packets, or governance artifacts. Those outputs may be preserved as foundation carry-in, but they require either a selected concrete runtime carrier or USER-approved foundation-only PR consideration before PR Readiness.

### Rebaseline Adoption & Reconciliation Phase

Rule Name: `Rebaseline Adoption & Reconciliation Phase` (`RAR`)
Owner: `Docs/phase_governance.md` for phase law and blockers; `Docs/branch_plans/README.md` for packet fields and active branch-plan carrydown; `Docs/governance_efficiency_operating_model.md` for repo/external-state placement; `Docs/validation_helper_registry.md` for future helper/validator expectations; `Docs/user_test_summary_guidance.md` for Live Validation and USER proof interpretation.
Purpose: RAR is the named phase refinement of `Merged Vision / Proof Standard Adoption Gate`. It pauses normal phase progression after a rebaseline, merge/re-entry, or returned-UTS standard drift event so the owning worktree can evaluate its existing branch work against newly merged source-truth, UIREF, vision, proof, packet, helper, or validator standards before continuing.
Supersession Boundary: RAR supersedes normal branch progression only while its trigger is unresolved. It does not supersede protected-main law, USER approval gates, no cross-worktree mutation, issue mutation approval, external-state boundaries, runtime/provider/private/cache/memory gates, PR/merge/release gates, or source-owner placement law.
Trigger Conditions: RAR is required when `origin/main` advanced with governance, Project Vision including the NDAI Product Experience Contract, Family Vision, Family Feature Vision, UIREF, FAM-002 presentation grammar, proof hierarchy, Live Validation, USER packet, helper/validator, issue-intake, backend/runtime predictability, or frontend/backend truth-mapping changes that could affect the active branch's existing output; when rebaseline/re-entry surfaces overlap with current branch files, visible surfaces, proof claims, or active UTS items; or when Codex/USER observes that a branch claims green while owned surfaces or prior branch output have not been compared against the current standard.
Substantive Exhaustiveness Requirement: RAR must be substantive and exhaustive for the approved scope by default. A RAR packet, ledger, helper output, or Codex digest that samples one defect, one screenshot, one window, one control family, or one helper-green path and then claims the whole RAR gate is complete is invalid unless the `Scope Coverage Manifest` explicitly proves why sampling is sufficient and lists every excluded surface, element group, state, file class, proof claim, and issue-candidate class with `Not Applicable With Reason`, `Deferred With Reason`, `USER Waived With Reason`, or `OUT OF CURRENT SCOPE`. RAR must produce both a `Current Branch Active Repair Ledger` and a `Historical / Previous Branch Issue Candidate Ledger`; either ledger may say `None`, but the named ledger must exist. RAR must inventory each material owned/touched visible surface and user-relevant backend/state claim at element-group depth, including controls, text/copy, typography, color, spacing, borders, glow/shadow, rows, cards, dividers, scrollbars, dialogs, failure/blocked/empty states, accessibility/keyboard paths, and state transitions where applicable. Missing rows are `Unproven Owned Surface` or `RAR Shallow Audit` blockers, not acceptable omissions. The reviewer must be able to trace each row from source truth to code path, rendered evidence or explicit proof gap, accepted reference or reference gap, disposition, and next legal action.
Stages:

- `RAR0 Trigger Detection`: identify the merged standard, rebaseline/re-entry event, affected branch/worktree, and whether RAR applies.
- `RAR1 Read-Only Impact Audit`: inventory current branch changes, previous branch carry-ins, owned product surfaces, code paths, proof claims, affected UI/UX/runtime/backend surfaces, and likely issue candidates without mutating repo files.
- `RAR2 Adoption Ledger Generation`: write or update the active external `Rebaseline Adoption & Reconciliation Ledger` and generate a USER packet when USER review is needed.
- `RAR3 USER Review Gate`: USER reviews repair candidates, waiver candidates, route-back recommendations, and GitHub issue candidates. A reviewable packet does not authorize repair or issue mutation by itself.
- `RAR4 Authorized Repair / Issue-Candidate / Carry-Forward`: after exact USER approval, the owning worktree repairs in-scope branch-local defects, records approved waivers, carries future-gated items, or creates approved GitHub issues. Sibling worktree mutation remains blocked.

Required RAR Packet Fields: the USER-facing packet must include `START_HERE`, `Branch / Worktree Identity:`, `Trigger Reason:`, `Source-Truth Files Loaded:`, `Incoming Standard / Change Summary:`, `Affected File Inventory:`, `Affected Surface Inventory:`, `Code-To-Visual Trace Matrix:`, `Reference / Template / Primitive Classification:`, `Reference Candidate Sync Review:`, `Accepted Reference Set / Comparative Synthesis:`, `Accepted Reference / Template / Primitive Comparator Matrix:`, `NDAI Product Experience Contract Comparison:`, `Future-Proof Implementation Review:`, `UI Element Inventory:`, `Backend / State Ownership Trace:`, `Screenshot / Video / Contact-Sheet Evidence:`, `Vision-To-Proof Matrix:`, `Scope Coverage Manifest:`, `Owned-Surface Nonconformance Ledger:`, `Issue-Candidate Table:`, `Repair / Waiver / Defer / Route Decision Table:`, `Validation Summary:`, and `Exact Next USER Decision:`. The active branch ledger or phase digest must also carry `RAR Stage:`, `Merged Standard Source:`, `Rebaseline / Re-entry Event:`, `Current Branch Implementation Inventory:`, `No Repo Live-State Tracking:`, `Repair / Waiver / Blocker:`, and `Next Legal Phase:`.
Code-To-Visual Requirement: RAR must inspect every material in-scope UI/runtime file, element group, and backend-to-visual path affected by the rebaseline/adoption trigger. This means line or code-region review for code that defines or affects owned visible elements, styles, state labels, proof markers, runtime state owners, user-visible text, or behavior claims. RAR must not claim unrelated repo-wide line review by default; unrelated files may be summarized only when the packet names why they are out of scope. Each trace row must map surface name, owning FAM, source file, relevant code symbol/class/selector/component, line range or code region when practical, backend/state owner, rendered proof, accepted comparator, visual match/mismatch, behavior/state match/mismatch, proof strength, defect or exception, and repair route.
Required Code-To-Visual Table: `| Surface | Element Group | Source File / Code Region | Backend / State Owner | Rendered Evidence | Accepted Reference | Visual Match | Behavior Match | Status | Defect / Gap | Next Legal Action |`.
Accepted Reference / Template / Primitive Comparator Requirement: For UI/UX work, RAR must compare each applicable element group against the highest available implementation authority and accepted reference set. The implementation hierarchy is: approved `Shared Primitive` first, approved `Implementation Template` second, and `Reference-Derived Implementation` from the accepted reference set third. Valid accepted references include promoted `Docs/ui_reference_catalog/UIREF-*` records, FAM-002 presentation grammar, AI Control Center where a UIREF record names it as the strongest seed, and any other accepted visual reference routed by current source truth. A branch must not claim it used a template or primitive unless it names the actual approved template or primitive source. If no approved template or primitive exists, the branch must classify the work as `Reference-Derived Implementation` and prove element-by-element parity through comparative synthesis.
Comparative Synthesis Requirement: RAR must identify the element class, list applicable accepted references, identify invariant traits across those references, identify feature-specific traits that may differ, identify conflicts or missing proof, and classify each difference as conforming, repair, exception request, issue candidate, reference gap, template gap, shared primitive gap, source-truth gap, or USER waiver need. Comparative synthesis must not average styles, invent new grammar from intuition, or treat a single screenshot as universal law when multiple accepted references apply.
Target surfaces must either consume the same shared primitive, instantiate the accepted template, reuse the same visual/control grammar, implement an equivalent structure that is visually and behaviorally indistinguishable for the relevant state, or document an exception, issue candidate, source-truth gap, reference gap, template gap, shared primitive gap, future repair, or USER waiver. If the accepted reference, template, primitive, or reference set is insufficient, ambiguous, conflicting, missing, or unusable, RAR must classify that as `SOURCE-TRUTH GAP`, `REFERENCE GAP`, `TEMPLATE GAP`, or `SHARED PRIMITIVE GAP` and route a Governance/UIREF/FAM-002 repair candidate; it must not force the target FAM to silently invent a new canonical standard.
Required Accepted-Reference Table: `| Element Class | Implementation Authority | Accepted Reference Set | Invariant Traits | Feature-Specific Traits | Target Surface | Primitive/Template/Reference-Derived/Exception | Evidence | Gap / Issue |`.
Visual Element / Element-Group Standard: For same-class Nexus-owned controls, including window-control clusters, buttons, dropdowns, filters, menus, lists, cards, rows, scrollbars, status chips, dialogs, tray menus, settings surfaces, and recovery panels, RAR must check anatomy, size family, spacing/density, border, radius, glow/shadow, color roles, typography, state behavior, hover, pressed, focus, disabled, selected, loading, error/blocked/empty states, accessibility labels, hitbox, visual hierarchy, content/action separation, and backend truth mapping where applicable. Text labels and backend ownership may differ by feature; the visual grammar and behavior must remain consistent enough that the USER perceives the same Nexus control family unless source truth grants a variant. RAR must also classify whether the affected surface preserves the NDAI Product Experience Contract: deterministic, intuitive, immersive, predictable, reliable, and consistent. A material mismatch on any applicable quality is a nonconformance, exception request, issue candidate, source-truth gap, reference gap, or blocker until dispositioned by the correct owner.
RAR Row Status Values: `CONFORMING`, `NONCONFORMING`, `UNPROVEN`, `PARTIAL`, `EXCEPTION NEEDED`, `ISSUE CANDIDATE`, `SOURCE-TRUTH GAP`, `REFERENCE GAP`, `TEMPLATE GAP`, `SHARED PRIMITIVE GAP`, and `OUT OF CURRENT SCOPE`. `UNPROVEN`, `PARTIAL`, `NONCONFORMING`, `EXCEPTION NEEDED`, `ISSUE CANDIDATE`, `SOURCE-TRUTH GAP`, `REFERENCE GAP`, `TEMPLATE GAP`, or `SHARED PRIMITIVE GAP` rows block normal progression until repaired, explicitly waived, routed to an approved issue candidate, or dispositioned by the correct owner.
RAR Shallow Audit Rule: `RAR Shallow Audit` is a blocker when RAR reports a review complete while any material owned/touched surface, visible element group, relevant state, accepted comparator, code-to-visual trace, backend/state truth path, proof gap, repair candidate, waiver candidate, or previous/historical issue candidate is omitted or collapsed into an unreviewable summary. A compliant RAR may be concise, but it must remain row-addressable. Broad statements such as `UI reviewed`, `all controls checked`, `screenshots look aligned`, `helper passed`, `current and historical issues reviewed`, `no issue candidates`, or `RAR green` are not valid unless backed by the required ledgers and the `Scope Coverage Manifest`. Any RAR packet that lacks either the current-branch repair ledger or the historical/previous-branch issue-candidate ledger blocks on `RAR Ledger Pair Missing`.
Required Issue-Candidate Table: `| Issue Candidate | Owner FAM | Surface | Element Group | Defect Class | Evidence | Proposed Carrier | GitHub Issue Mutation Approved? |`.
Required RAR Issue-Candidate Durability Surface: When RAR produces, carries, routes, defers, waives, rejects, repairs, or maps an issue candidate, the active external ledger and any USER-facing RAR packet must also include `| Candidate ID | Owning FAM | Surface | Element Group | Defect | Evidence Pointer | Current Disposition | Progression Blocking? | Proposed Carrier | GitHub Issue | Last Verified | Exact USER Decision Needed |`. `Candidate ID` may be a stable ID or durable lineage fingerprint, but it must survive packet regeneration, renaming, regrouping, and newer narrower packets. The row must preserve originating branch/RAR run or packet where available, owning FAM, surface, element group, defect class, evidence pointer, source owner, proposed carrier, current disposition, progression-blocking status, GitHub issue mapping if USER approved issue creation or mapping, last verification source/time, and exact USER decision if one remains.
RAR Issue-Candidate Durability Gate: `Packeted only`, `packet generated`, `packet reviewable`, `issue candidate packet USER-reviewed`, copied-context-only issue tables, secondary review-aid-only issue tables, or chat-only digest language are evidence/transport states, not terminal dispositions. An issue candidate remains active until it reaches a legal durable disposition: `Repaired And Independently Verified`, `USER Rejected With Reason`, `USER Waived With Reason And Scope`, `Deferred With Durable Owner / Reason / Target Carrier / Next Review Trigger`, `Routed To Another Legal Carrier With Acceptance Receipt`, `Approved For GitHub Issue Creation Pending Mutation`, `Mapped To Open GitHub Issue`, or `Mapped To Closed GitHub Issue And Reconciled Against Repair Evidence`. Unresolved active candidates must appear in the actual primary USER decision surface selected and routed through the external USER lifecycle owner; tables that appear only in supporting review aids, copied source-truth context, historical receipts, helper output, or chat digest do not satisfy the current USER decision surface. GitHub live state is read-only evidence for RAR unless USER separately approves issue mutation; deterministic GitHub snapshot evidence must reconcile every mapped issue number before `Mapped To Open GitHub Issue` or `Mapped To Closed GitHub Issue And Reconciled Against Repair Evidence` can clear. Connector/network failure, missing snapshot state, stale state, unknown state, or mismatched open/closed state must be recorded as `UNKNOWN` or `STALE`, not treated as green. Duplicate or renamed candidates must preserve exact-token lineage, predecessor/successor mapping, or reconcile conflicts instead of passing by substring or creating parallel silent rows. Terminal repaired/rejected/waived/closed-reconciled lineage may remain in external/history evidence without being copied into every later USER packet when no current USER decision remains.
Required RAR USER Decision Table: `| RAR USER Decision | Meaning | What It Authorizes | What It Does Not Authorize |`.
USER Packet Requirement: When RAR finds any UI/UX/runtime/backend nonconformance, unproven owned surface, issue candidate, waiver candidate, source-truth/reference gap, or route-back recommendation that needs USER judgment, Codex must prepare the required USER review content and deliver selected current evidence through the external USER lifecycle owner to the approved collection and evidence set. The packet must include the required RAR packet model, visual/code comparator summaries, screenshot/video/contact-sheet evidence or explicit proof gaps, issue-candidate table, repair-versus-issue boundary, and exact USER decision text. A Codex chat digest, helper output, validator output, or branch-plan ledger alone is not enough when USER review is needed.
External State Owner: Active RAR findings belong in `D:\Nexus Desktop AI\Governance State\branches\<branch_slug>\adoption_reconciliation.md` or the active external branch plan for that branch. Repo docs define durable rules, field schemas, blocker names, owner placement, and folded receipts only. RAR must not turn branch records, backlog, roadmap, family visions, FFVs, UIREF files, or repo branch plans into live adoption ledgers.
Blocking Conditions: `Rebaseline Adoption Review Missing`, `Merged Standard Impact Ledger Missing`, `Affected Surface Inventory Missing`, `Owned Surface Nonconformance Ledger Missing`, `Reference / Template / Primitive Classification Missing`, `Reference Candidate Sync Review Missing`, `Reference Candidate Collision Unreviewed`, `Reference Candidate Treated As Canon`, `Promoted Reference Moved External`, `Accepted Reference Comparator Missing`, `Accepted Reference Set Missing`, `Comparative Synthesis Missing`, `NDAI Product Experience Contract Comparison Missing`, `Future-Proof Review Missing`, `Future-Proof Proof Plan Missing`, `Future-Proof Adoption Review Missing`, `Magic Value Unjustified`, `Brittle Implementation Unresolved`, `Default-Only Future-Proof Proof`, `One-State Future-Proof Proof`, `Future Scope Implemented By Inference`, `Reference Effectiveness Warning Unrouted`, `Product Experience Contract Nonconformance Unresolved`, `Template / Shared Primitive Missing`, `Template Claim Unsupported`, `Shared Primitive Claim Unsupported`, `Reference-Derived Parity Unproven`, `Accepted Reference Conflict Unrouted`, `Template Gap Unrouted`, `Shared Primitive Gap Unrouted`, `Code-To-Visual Trace Missing`, `Backend State Ownership Trace Missing`, `Screenshot Contact-Sheet Proof Missing`, `Circular Validation Evidence`, `Visual Comparator Matrix Missing`, `Current Branch Repair Vs Issue Boundary Missing`, `Owned Surface Issue Candidate Missing`, `RAR Issue Candidate Durability Missing`, `RAR Issue Candidate Lineage Missing`, `RAR Issue Candidate Durable Disposition Missing`, `RAR Issue Candidate Disappeared From Active Packet`, `RAR Issue Candidate Packeted Only`, `RAR GitHub Issue State Unknown`, `RAR GitHub Issue Mapping Stale`, `RAR USER Packet Missing`, `Reference Parity Claim Unsupported`, `Source-Truth Gap Unrouted`, `Reference Gap Unrouted`, `Unproven Owned Surface`, `Normal Phase Progression Blocked By RAR`, and `Repo File-State Tracking`.
Additional Blocking Conditions: `RAR Shallow Audit`, `RAR Ledger Pair Missing`, `RAR Scope Coverage Manifest Incomplete`, `RAR Element Group Rows Missing`, `RAR Current Repair Ledger Missing`, `RAR Historical Issue Candidate Ledger Missing`, `RAR Sampling Justification Missing`, `RAR Proof Gap Collapsed`, `RAR Comparator Classification Missing`, and `RAR Row Disposition Missing`.
Circular Validation Rule: RAR evidence must be non-circular. Requirement text cannot be the only proof that the requirement passed. Validator green cannot be the only proof. Helper output cannot be the only proof. Codex summaries cannot be the only proof. Attractive screenshots cannot create visual acceptance by themselves. UIREF records and templates cannot prove themselves; they must be used as comparators against rendered output, code-to-visual trace, backend/state truth, screenshot/video/contact-sheet evidence, and USER review or waiver where human judgment is required.
Final Disposition: RAR exits only through `No Applicable Impact`, `Adoption Green With Evidence`, `Repair Completed And Revalidated`, `USER Waiver Recorded`, `Issue Candidate Durable Disposition Recorded`, `Route Back To Earlier Gate`, or `Blocked`. `Issue Candidate Packet USER-Reviewed` is valid evidence that USER saw the packet, but it is not a final RAR exit by itself unless every active candidate has a durable disposition, owner/route, blocking classification, and USER decision state. Normal BP, Workstream, Hardening, LV, PR Readiness, or Release Readiness progression remains blocked until the active RAR trigger is resolved and no unresolved blocking RAR row status or durability-gate failure remains.

### Backend Predictability / Frontend-Backend Contract Gate

Rule Name: `Backend Predictability / Frontend-Backend Contract Gate`
Owner: `Docs/phase_governance.md` for phase gates and blockers; `Docs/branch_plans/README.md` for BP2/BP3 carrydown fields; `Docs/development_rules.md` for implementation expectations; `Docs/architecture.md` for general runtime/backend boundaries; `Docs/ai_runtime_and_trust_architecture.md` for AI/provider/trust-specific runtime boundaries; `Docs/validation_helper_registry.md` for future helper/validator guidance.
Applies To: Branch Readiness, BP1, BP2, BP3, Workstream, Hardening, Live Validation, PR Readiness, Release Readiness, active external branch plans, USER review packets, and any branch that creates, changes, proves, or presents runtime/backend behavior, state, config, schema, persistence, provider/model/cache/private behavior, failure handling, recovery, or UI-visible runtime status.
Required State: Runtime/backend-affecting branches must define a Backend Predictability / Reliability Contract before implementation and carry it through proof. Required fields are `Runtime / Backend Surface:`, `State Owner:`, `Deterministic Inputs:`, `Deterministic Outputs:`, `Lifecycle / State Machine:`, `Config / Schema Delta:`, `Migration / Compatibility Impact:`, `Idempotency Behavior:`, `Retry Behavior:`, `Concurrency / Reentrancy Assumptions:`, `Failure Behavior:`, `Fallback Behavior:`, `Recovery Route:`, `Logging / Observability Proof:`, `Security / Privacy Boundary:`, `Provider / Model / Cache / Private Boundary:`, `UI / User-Visible Contract Impact:`, `Validation / Proof Path:`, `Rollback / Reversibility Path:`, `Degraded / Disabled / Unavailable State Behavior:`, and `User-Facing Status / Error Mapping:`. Every user-visible state label, green/success claim, disabled action, blocked action, recovery option, degraded state, and failure state must map to runtime truth, policy truth, or a USER-approved exception. Backend logs are diagnostic evidence, not USER-facing proof by themselves.
Allowed Values: `Deterministic Contract Complete`, `Not Applicable With Reason`, `Deferred With USER-Approved Boundary`, `USER Waived With Reason`, `Issue Candidate Required`, and `Blocked`.
Invalid Values: `Backend TBD`, `UI Says Green But Runtime Unknown`, `Runtime State Owner Missing`, `State Machine Missing`, `Logs Equal User Proof`, `Fallback Hidden`, `Recovery UI Without Recovery Path`, `Schema Change Without Compatibility Proof`, `Provider Boundary Assumed`, `Issue Auto-Created`, and `Validator Green Without Backend Contract`.
Blocking Conditions: `Backend Predictability Contract Missing`, `Runtime State Owner Missing`, `Runtime State Machine Missing`, `Nondeterministic Backend Behavior`, `Failure Path Missing`, `Fallback Behavior Hidden`, `Schema Migration Proof Missing`, `Config Compatibility Proof Missing`, `Backend/UI Contract Mismatch`, `User-Facing State Not Backed By Runtime Truth`, `Backend Logs Treated As User Proof`, `Recovery Route Missing`, `Rollback Path Missing`, `Provider Boundary Unclassified`, and `Issue Mutation Approval Missing`.
Repair Owner: The consuming branch repairs its own runtime/backend contract, code, UI mapping, proof, and issue-candidate packet under its legal carrier. The explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable contract ambiguity only. AI/provider/trust-specific contract drift routes through `Docs/ai_runtime_and_trust_architecture.md` and the owning FAM-007 branch when admitted.
Repair Path: Define or repair the contract, map UI-visible states to runtime truth, add or repair failure/fallback/recovery proof, classify config/schema/provider/cache/private boundaries, add rollback or reversibility proof, update branch-local plan/evidence only in the allowed owner, and validate before green. If the violation is discovered in existing or previous branch output that cannot legally be repaired by the current branch, prepare a USER-reviewable issue-candidate packet and stop before GitHub mutation.
USER Decision Required: Required for waiver, issue creation/mutation, broad scope expansion, provider/model/private/cache behavior, schema migration, runtime behavior beyond current approval, or accepting residual backend/UI mismatch risk.
Validation Owner: Future helper/validator coverage should extend existing reusable branch-governance and Branch Readiness fixture validators where machine-checkable. Until then, Codex must report the backend contract and frontend/backend truth mapping in the phase digest.
Final Disposition: A branch cannot call runtime/backend-affecting work complete, predictable, reliable, Live Validation green, or PR-ready while backend state ownership, deterministic behavior, failure/fallback/recovery, UI status mapping, or rollback proof is missing. The rule creates source-truth carrydown and proof expectations only; it does not implement runtime behavior, mutate product worktrees, create issues, or store live operational ledgers in repo docs.

### UI Reference / Template / Shared Primitive Dependency Gate

Rule Name: `UI Reference / Template / Shared Primitive Dependency Gate`
Owner: `Docs/phase_governance.md` for PR-hold and blocker routing; `Docs/ui_reference_catalog/README.md` for reference/template/primitive definitions; `Docs/family_visions/FAM-002_desktop_interface.md` for presentation law; `Docs/validation_helper_registry.md` for future helper/validator guidance.
Applies To: Governance reform, FAM-002 presentation standardization, UIREF reference promotion, future UI implementation-template promotion, future design-token/shared-primitive work, and any branch that claims a reference, template, or shared primitive makes UI proof complete.
Required State: UI reuse authority must be classified as `Accepted Reference`, `Implementation Template`, `Shared Primitive`, `Accepted Reference Set`, or `Comparative Synthesis`. The Package A-E completion pass promoted UIREF-001 through UIREF-004 as accepted visual/control reference grammar with known limitations, UIREF-005 as a design-token/shared-rule source-truth baseline with implementation deferred, and UIREF-006 as a negative-example/enforcement contract with helper/validator/fixture code deferred. That cleared the current reference-system promotion work by source-truth disposition, but it did not create reusable implementation templates, code-level design tokens, shared primitives, helper/validator/fixture enforcement, or consuming-FAM adoption proof. Future template or shared-primitive implementation remains separately USER-gated. Branches may consume promoted UIREF reference grammar and FAM-002 presentation law where the specific UIREF record grants that authority, but they must not claim a template or primitive exists unless the actual approved template or primitive source is named.
Allowed Values: `Accepted Reference Promoted`, `Reference Promoted With Known Limitations`, `Implementation Template Not Promoted`, `Shared Primitive Not Promoted`, `Reference-Derived Implementation`, `USER-Approved Template Promotion`, `USER-Approved Shared Primitive Promotion`, `Future Template/Primitive Work`, `Limited PR Path USER-Approved`, and `Blocked`.
Invalid Values: `Template Exists By Inference`, `Shared Primitive Exists By Inference`, `UIREF Treated As Template`, `ChatGPT/Codex Example Treated As Golden`, `FAM-007 Active Packet Treated As Template`, `Reference Promoted Without USER Review`, `Design Token Implemented In Docs-Only Pass`, `Reference Proof Clears Consuming Branch Adoption`, and `PR Requested While An Admitted Current-Branch Template/Primitive Blocker Remains`.
Blocking Conditions: `Template Dependency Unresolved` when USER-admitted template work is still in current scope, `Shared Primitive Promotion Blocked` when primitive work is attempted without USER approval, `Implementation Template Promotion Blocked` when template promotion lacks USER approval, `Template Claim Unsupported`, `Shared Primitive Claim Unsupported`, `Reference Treated As Existing Template`, `Reference-Derived Parity Unproven`, `Limited PR Path USER Approval Missing`, and `Current Branch Template/Primitive Work Incomplete` when USER explicitly keeps template or primitive implementation in the current PR scope.
Repair Owner: the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy records durable dependency and classification rules. UIREF reference records live in `Docs/ui_reference_catalog/`. Future implementation-template or shared-primitive work belongs to a separately approved owner/carrier after USER admits the plan/promotion path. Consuming FAM worktrees own branch-local adoption proof and repairs at their next legal gate.
Repair Path: Keep current presentation rules enforceable manually through Project Vision, FAM-002, UIREF references, RAR, Vision-To-Proof, and LV/UTS proof. If a branch needs real implementation templates or shared primitives, stop for a USER-approved carrier instead of pretending reference grammar is implementation code. If a branch cites a reference only, classify the work as `Reference-Derived Implementation`, compare against the accepted reference set, prove parity or route gaps, and preserve any issue candidates for USER approval before GitHub mutation.
USER Decision Required: Required for limited PR path, template promotion, shared-primitive promotion, design-token implementation, helper/validator code, fixture mutation, consuming-FAM adoption repair outside current branch scope, issue creation/mutation, or any product worktree adoption.
Validation Owner: Future helper/validator coverage may check reference/template/primitive claims after USER-approved records exist; until then, validators and Codex digests must reject claims that UIREF reference grammar, screenshots, or examples are implementation templates or shared primitives.
Final Disposition: UIREF references may be promoted and PR-ready as source truth with known limitations, while implementation templates and shared primitives remain future-gated. A branch cannot use future template/primitive work as current proof, and a promoted reference cannot clear consuming-branch adoption by itself. This gate must not create templates, shared primitives, design tokens, issue mutations, FAM mutations, or repo live-state ledgers by inference.

### Reference Candidate Synchronization Gate

Rule Name: `Reference Candidate Synchronization Gate`
Owner: `Docs/phase_governance.md` for gate and blocker behavior; `Docs/governance_efficiency_operating_model.md` for external-state placement and schema; `Docs/ui_reference_catalog/README.md` for promoted-reference boundary; `Docs/branch_plans/README.md` for BP/RAR packet carrydown; `Docs/validation_helper_registry.md` for future helper/validator guidance.
Applies To: Branch Readiness, Branch Planning, Workstream, Hardening, Live Validation, UTS, RAR, PR Readiness, and any branch that proposes, consumes, supersedes, varies, or depends on a same-class Reference Standard, Template, Shared Primitive, accepted comparator, token, visual grammar, geometry rule, control-state rule, backend behavior rule, proof standard, naming rule, or applicability rule.
Required State: promoted Reference Standards remain repo source truth. Branch-owned reference candidates live as external/worktree evidence until promotion. A branch must check applicable promoted references and admitted external same-class candidates/collisions before proposing or consuming a new standard. If an applicable promoted reference exists, the branch must consume it, compare against it, instantiate an approved template/primitive, or record `Reference Gap`, `Template Gap`, `Shared Primitive Gap`, `Source-Truth Gap`, or `Exception Needed`. If an external same-class candidate exists, the branch must compare against it or propose merge, split, variant, supersession, defer, reject, or collision disposition. Conflicting candidates require a USER-reviewable collision row before the branch may claim green for work depending on that same-class standard.
Allowed Values: `Promoted Reference Consumed`, `No Applicable Candidate Found`, `External Candidate Compared`, `Candidate Proposed`, `Candidate Merge Proposed`, `Candidate Split Proposed`, `Variant Candidate Proposed`, `Supersession Candidate Proposed`, `Collision Detected`, `Collision Reviewed`, `Candidate Deferred With Owner`, `Candidate Rejected`, `Candidate Promoted Pending PR`, `Promoted To Source Truth`, and `Not Applicable With Reason`.
Invalid Values: `Candidate Treated As Canon`, `External Candidate Overrides Promoted Reference`, `Branch Invented Standard Without Sync`, `Same-Class Candidate Ignored`, `Collision Ignored`, `Reference Promoted From External State Alone`, `Promoted Reference Moved External`, `Candidate Grants Template Authority`, `Candidate Grants Shared Primitive Authority`, `Candidate Clears USER Acceptance`, and `Candidate Clears FAM Adoption Proof`.
Blocking Conditions: `Reference Candidate Sync Missing`, `Reference Candidate Collision Unreviewed`, `Reference Candidate Treated As Canon`, `Promoted Reference Moved External`, `Same-Class Candidate Ignored`, `External Candidate Overrides Promoted Reference`, `Candidate Promotion Packet Missing`, `Candidate Conflict Key Missing`, and `Candidate USER Decision Missing` block when the branch depends on the affected same-class standard or claims reference/template/primitive proof from candidate evidence.
Repair Owner: consuming branch for branch-local candidate comparison and packet rows; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy for durable source-truth ambiguity or promotion; USER for candidate promotion, waiver, exception, split, merge, rejection, or issue/PR decisions.
Repair Path: read promoted repo references, read admitted external candidate/collision evidence when the local workflow has access, produce the required candidate/collision/promotion tables in the current phase packet or digest, keep live candidate rows external, route unresolved conflicts to USER or Governance, and promote only through a USER-approved Governance source-truth update.
USER Decision Required: required for candidate promotion, supersession, variant acceptance, exception, waiver, external-state schema creation/mutation, helper implementation, template/shared-primitive implementation, GitHub issue mutation, or any product/FAM adoption repair.
Validation Owner: future helpers may generate report-only candidate sync/collision digests and future validators may source-check packet fields when machine-checkable. Clean-clone repo validation must not require `D:\Nexus Desktop AI\Governance State`.
Final Disposition: this gate adds a coordination and blocker surface inside existing phases; it is not a new phase and does not authorize runtime work, FAM worktree mutation, external-state mutation, issue mutation, PR creation, merge, release, template/shared-primitive implementation, or source-truth promotion by itself.

### Standalone Window Geometry Recovery Gate

Rule Name: `Standalone Window Geometry Recovery Gate`
Owner: `Docs/phase_governance.md` for phase gates, blockers, and carrydown; `Docs/branch_plans/README.md` for BP1/BP2/BP3 classification and proof-plan fields; `Docs/family_visions/FAM-002_desktop_interface.md` for reusable window presentation and geometry standards; `Docs/family_visions/FAM-003_interaction_and_actions.md` plus `Docs/family_feature_visions/F3-FF01.md` for the resident access / quick-actions / settings dependency route; `Docs/family_visions/FAM-008_packaging_and_install_experience.md` for setup or education only when packaging/setup admits it; `Docs/validation_helper_registry.md` for future helper/validator guidance.
Applies To: Branch Readiness, BP1, BP2, BP3, Workstream, Hardening, Live Validation, PR Readiness, active external branch plans, USER review packets, and any branch that creates, touches, restores, moves, resizes, persists, or proves a Nexus-owned product window.
Required State: Every Nexus-owned standalone, top-level, restorable, independently opened, movable, resizable, or geometry-persisted product window must have a deterministic recovery route to reset its window position and size to safe defaults. The route may be implemented later through FAM-003 resident access, Global Settings, quick actions, or another USER-approved user-accessible surface, but the owning branch must classify the window and carry the dependency before closeout. The consuming FAM owns the feature window behavior and declares whether the reset route applies. FAM-002 owns the window presentation and geometry grammar. FAM-003 owns the user-accessible reset action route when the reset is global/resident/settings/quick-action reachable. FAM-008 may explain or educate the route during setup/installer/startup work, but it does not own the runtime reset action unless a later source-truth owner explicitly grants that authority.
Required Window Classification Fields: `Window Name:`, `Owning FAM:`, `Surface Type:`, `Window Class:`, `Geometry Persistence Behavior:`, `Default Position / Size Behavior:`, `Reset Position / Size Route:`, `FAM-003 Dependency Status:`, `FAM-002 Presentation Standard Consumed:`, `FAM-008 Setup / Education Dependency:`, `Troubleshooting / Fallback Behavior:`, `Proof Method:`, and `Not Applicable Reason:`.
Allowed Window Class Values: `Standalone Nexus-Owned Product Window`, `Top-Level Restorable Nexus-Owned Product Window`, `Anchored Child Panel`, `Child Window Recoverable With Parent`, `Platform-Native Exception`, `Temporary Dev / Proof Surface`, and `Not Applicable With Reason`.
Invalid Values: `Unclassified Window`, `Geometry Persisted But No Reset Route`, `Offscreen Recovery Unspecified`, `Child Window Exception Without Reason`, `Platform-Native Exception Without Reason`, `FAM-003 Owns Feature Window Behavior`, `FAM-008 Owns Runtime Reset By Inference`, `Repo Docs Track Current Window State`, and `Validator Green Without Geometry Proof`.
Blocking Conditions: `Window Position / Size Reset Route Missing`, `FAM-003 Window Recovery Dependency Required`, `Child Window Geometry Reset Not Applicable Unproven`, `Offscreen Window Recovery Path Missing`, `Window Geometry Classification Missing`, and `Repo File-State Tracking`.
Repair Owner: The consuming FAM repairs its own window classification, behavior, fallback, and proof. FAM-002 repairs reusable presentation/geometry standards. FAM-003 repairs the global or user-accessible reset route when admitted. FAM-008 repairs setup/education wording when admitted. The explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable source-truth ambiguity only.
Repair Path: inventory created/touched/affected windows, classify each window, identify geometry persistence and failure modes, declare default safe geometry, declare reset route or Not Applicable reason, record FAM-003 dependency when a user-accessible reset route is required, keep live current window position/size out of repo docs, prove reset behavior or record future-gated dependency/waiver, then carry the result through Hardening, Live Validation, and PR Readiness.
USER Decision Required: required to waive the reset route, approve a platform-native exception, admit FAM-003 runtime implementation, admit FAM-008 setup/education work, accept a child-window Not Applicable reason that is not self-evident, or proceed with residual offscreen/recovery risk.
Validation Owner: future helper/validator coverage should extend existing reusable validators and USER review helpers where machine-checkable. Until then, Codex must report the classification and proof gap review in the relevant phase digest.
Final Disposition: A branch cannot call a Nexus-owned standalone/top-level/restorable geometry-persisted product window closeout-ready while its safe default geometry, reset route, FAM-003 dependency status, exception reason, or proof method is missing, unless USER explicitly waives the risk. This rule creates durable dependency/carrydown governance only; it does not create live window-state tracking in repo docs and does not authorize immediate FAM-003/FAM-006/FAM-007/FAM-008 mutation.

### Window Geometry / Resize Contract Gate

Rule Name: `Window Geometry / Resize Contract Gate`
Owner: `Docs/phase_governance.md` for phase gates, blockers, and carrydown; `Docs/ui_reference_catalog/UIREF-007_window_geometry_resize_contract.md` for the promoted geometry/resize contract; `Docs/family_visions/FAM-002_desktop_interface.md` for reusable presentation law; `Docs/branch_plans/README.md` for BP/RAR packet fields; `Docs/governance_efficiency_operating_model.md` for active-ledger placement boundaries; `Docs/validation_helper_registry.md` for future helper/validator guidance.
Applies To: Branch Readiness, BP1, BP2, BP3, Workstream, Hardening, Live Validation, UTS, PR Readiness, Release Readiness, RAR, active external branch plans, USER review packets, and any branch that creates, touches, repairs, resizes, scrolls, proves, or visually accepts Nexus-owned product-window geometry, size-state composition, responsive layout, fullscreen/maximize behavior, or multi-monitor posture.
Required State: Every applicable surface must classify its window/surface type before proof; define minimum/default/maximum/fullscreen policy; define edge/corner resize, cursor transition, and resize-grip policy; define DPI/display-scale and multi-monitor/portrait behavior; define breakpoint, reflow, scroll, wrap, truncate, collapse, and sparse wide-state behavior; define active-content and footer/action attachment; name accepted references; provide code-to-visual trace; provide screenshot/video/contact-sheet evidence at the required size states or mark the state Not Applicable with reason; and disposition out-of-scope owned defects as repair, waiver, issue candidate, source-truth gap, reference gap, template gap, shared primitive gap, or USER decision.
Required Window Geometry Fields: `Window / Surface Name:`, `Owning FAM / Worktree:`, `Window Classification:`, `Accepted Reference Set:`, `Minimum Supported Size:`, `Default Size:`, `Maximum Useful Size:`, `Fullscreen / Maximize Policy:`, `Resize Mechanics:`, `Cursor Transition / Resize Grip Policy:`, `Breakpoint / Reflow Policy:`, `Scroll / Wrap / Truncate / Collapse Policy:`, `Active Content / Footer Attachment:`, `DPI / Display Scale Proof:`, `Multi-Monitor / Portrait Proof:`, `Geometry Recovery Route:`, `Code-To-Visual Trace:`, `Screenshot / Video / Contact-Sheet Evidence:`, and `Disposition:`.
Allowed Window Geometry Classification Values: `Compact Settings / Tool Window`, `Dashboard / Parent-Class Window`, `Embedded Child Surface`, `Detached Child Window`, `Detached Child Dashboard / Child-Parent Window`, `Modal / Dirty-Guard / Confirmation Surface`, `Platform-Native Exception`, `Temporary Diagnostic / Proof Surface`, and `Not Applicable With Reason`.
Invalid Values: `Child Window` without embedded/detached/parent relationship, `Responsive By Global Zoom`, `Fullscreen Supported Without Composition`, `Resizable` without minimum/default/maximum policy, `Looks Good At Default Size`, `Window Geometry Green By Marker`, `Current Coordinates Stored In Repo Docs`, `Sparse Wide-State Shell Without Purpose`, and `Accepted Reference Ignored`.
Blocking Conditions: `Window Geometry Contract Missing`, `Window Classification Missing`, `Window Min Default Max Policy Missing`, `Window Fullscreen / Maximize Policy Missing`, `Window Resize Mechanics Proof Missing`, `Resize Cursor / Grip Policy Missing`, `DPI Display Scale Proof Missing`, `Multi-Monitor Geometry Proof Missing`, `Responsive Layout Proof Missing`, `Sparse Wide-State Shell`, `Global Zoom Used As Layout Substitute`, `Detached Child Acceptance Missing`, `Embedded Child Inheritance Unproven`, `Geometry Issue Candidate Missing`, `Marker-Only Geometry Conformance`, and `Repo File-State Tracking`.
Per-FAM Carrydown: FAM-003 owns the user-accessible reset/global settings route only when admitted; FAM-006 owns HUD, dashboard, monitoring, recording, and log window behavior/proof; FAM-007 owns AI control/status/trust window behavior/proof and privacy/provider boundaries; FAM-008 owns installer/setup/update/shortcut education and platform-trust surfaces when admitted. Consuming FAM worktrees may overlap files after merge/rebaseline only through normal RAR and branch-local adoption; they must not mutate sibling worktrees or create issues without USER approval.
Repair Owner: The consuming FAM repairs its own product-window geometry, responsive layout, proof, and issue-candidate packet under its legal carrier. FAM-002 repairs reusable presentation/geometry ambiguity. The explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs durable source-truth ambiguity only.
Repair Path: inventory all affected windows/surfaces, classify each surface, compare against UIREF-007 plus the accepted reference set, inspect code-to-visual paths, capture proof at required size states, record issue candidates for previous or out-of-scope owned defects, keep live coordinates/current window state out of repo docs, and stop for USER review when repair, waiver, issue creation, source-truth gap, or reference/template/primitive gap disposition is needed.
USER Decision Required: required to waive missing geometry proof, accept fullscreen/maximize omission for a top-level window, approve platform-native or temporary diagnostic exceptions, accept residual sparse wide-state risk, create or mutate GitHub issues, perform FAM worktree mutation, implement shared primitives/templates/design tokens, or proceed with unresolved geometry nonconformance.
Validation Owner: future helper/validator coverage should extend existing reusable branch-governance, Branch Readiness fixture, USER packet, and surface-specific validators where machine-checkable. Until then, Codex must report the geometry/resize matrix and proof gaps in the relevant phase digest.
Final Disposition: A branch cannot call an applicable Nexus-owned product window visually green, Live Validation green, UTS-ready, PR-ready, or release-ready while UIREF-007 applies and the window geometry/resize matrix is missing, marker-only, unresolved, or based only on default-size proof. This rule creates source-truth carrydown and proof expectations only; it does not implement runtime UI, mutate product worktrees, create issues, promote templates/shared primitives, or store live operational ledgers in repo docs.

### NDAI Top-Level Window Control Grammar Gate

Rule Name: `NDAI Top-Level Window Control Grammar Gate`
Owner: `Docs/phase_governance.md` for phase gates, blockers, and carrydown; `Docs/branch_plans/README.md` for BP1/BP2/BP3 control classification and proof-plan fields; `Docs/family_visions/FAM-002_desktop_interface.md` for reusable top-level window-control presentation grammar; `Docs/family_visions/FAM-003_interaction_and_actions.md` plus `Docs/family_feature_visions/F3-FF01.md` only when a user-accessible reset/recovery route is required; `Docs/validation_helper_registry.md` for future helper/validator guidance.
Applies To: Branch Readiness, BP1, BP2, BP3, Workstream, Hardening, Live Validation, PR Readiness, active external branch plans, USER review packets, and any branch that creates, changes, proves, or visually accepts a Nexus-owned top-level, standalone, restorable, independently opened, movable, resizable, or geometry-persisted product window.
Required State: A Nexus-owned top-level, standalone, restorable product window must classify its window-level controls separately from content actions. When close, minimize, maximize, restore, drag, or resize actions are applicable, the window must use a Nexus-native compact top-level control cluster or recorded equivalent window-control grammar instead of a large content-style header `CLOSE` pill. Large labeled `CLOSE`, `Cancel`, `Exit`, `Back`, or similar buttons remain valid for modal dialogs, child windows, footer actions, content-level actions, confirmation flows, platform-native exceptions, temporary dev/proof surfaces, or USER-approved exceptions when the branch records the reason and proof path. This rule does not authorize default Windows title bars for Nexus-owned product windows.
Required Window Control Fields: `Window Name:`, `Window Role:`, `Window Class:`, `Control Placement:`, `Window-Level Control Set:`, `Close Control Treatment:`, `Minimize Applicability:`, `Maximize / Restore Applicability:`, `Large Labeled Close Button Disposition:`, `Content/Footer Close Actions:`, `Accessibility / Tooltip / Keyboard Treatment:`, `Hitbox / Focus / Hover / Pressed State Coverage:`, `FAM-002 Control Grammar Consumed:`, `FAM-003 Recovery Route Dependency:`, `Exception Reason:`, and `Proof Method:`.
Allowed Control Dispositions: `Compact NDAI Control Cluster`, `Recorded Equivalent Nexus-Native Window Control`, `Content/Footer Action Only`, `Modal / Child Window Explicit Action`, `Platform-Native Exception`, `Temporary Dev / Proof Surface`, `USER-Approved Exception`, and `Not Applicable With Reason`.
Invalid Values: `Large Header CLOSE Pill As Default Top-Level Control`, `Default Windows Title Bar For Nexus Product Window`, `Window-Level Controls Unclassified`, `Minimize / Maximize / Restore Applicability Unclassified`, `Content Close And Window Close Conflated`, `Header And Footer Close Duplicate Without Reason`, `Control Hitbox / Accessibility Unproven`, `FAM-003 Owns Normal Window Controls`, and `Validator Green Without Visual Control Proof`.
Blocking Conditions: `Top-Level Window Control Grammar Missing`, `Large Header CLOSE Pill Requires Exception`, `Default Windows Chrome Regression`, `Window-Control / Content-Action Boundary Missing`, `Minimize / Maximize / Restore Applicability Missing`, `Window Control Accessibility Proof Missing`, `Header/Footer Close Conflict Unresolved`, and `Visual Window Control Proof Missing`.
Repair Owner: The consuming FAM repairs its own window-control behavior, layout, exception, and proof. FAM-002 repairs reusable control grammar. FAM-003 repairs only the user-accessible reset/recovery route when admitted. The explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable source-truth ambiguity only.
Repair Path: inventory top-level and child windows, classify window-level versus content-level controls, choose compact NDAI control cluster or valid exception, classify minimize/maximize/restore applicability, preserve Nexus-native styling, prove default/hover/focus/pressed/disabled states where applicable, prove accessible labels/tooltips/keyboard/focus behavior, preserve any required FAM-003 recovery dependency, and carry the result through Hardening, Live Validation, and PR Readiness.
USER Decision Required: required to approve a large header `CLOSE` exception on a top-level product window, accept platform-native chrome, waive compact control-cluster adoption, proceed with missing minimize/maximize/restore classification, or accept residual accessibility/visual-control risk.
Validation Owner: future helper/validator coverage should extend existing reusable validators and USER review helpers where machine-checkable. Until then, Codex must report the control grammar classification and visual proof review in the relevant phase digest.
Final Disposition: A branch cannot call a Nexus-owned top-level/restorable product window visually or product-ready while its window-level controls are unclassified, large header `CLOSE` usage is unexplained, default Windows chrome appears without exception, minimize/maximize/restore applicability is missing, or accessibility/visual state proof is absent. This rule creates durable presentation/carrydown governance only; it does not implement runtime controls, design tokens, shared primitives, templates, or FAM worktree mutations.

### Hardening / Live Validation Repair Loop Contract

Rule Name: `Hardening / Live Validation Repair Loop Contract`
Owner: `Docs/phase_governance.md` for phase gates, loop ordering, blockers, and PR Readiness admissibility; `Docs/branch_plans/README.md` for BP2/BP3 proof-plan carrydown; `Docs/user_test_summary_guidance.md` for USER validation and UTS interpretation; `Docs/validation_helper_registry.md` for future helper/validator guidance; `Docs/incident_patterns.md` for reusable failure-pattern preservation.
Applies To: Hardening, Live Validation, USER-gated Live Validation, UTS handoff, PR Readiness, active external branch plans, phase packets, and any branch that changes after a Hardening pass because Live Validation or USER validation found defects.
Required State: Hardening is the readiness inspection before Live Validation. Live Validation proves the required runtime or USER path. If Live Validation or USER-gated Live Validation finds a Codex-visible defect before UTS handoff, the branch must repair the Live Validation blockers first instead of rerunning full Hardening by default while the LV path is still known-failing. If the formal USER Test Summary returns `USER Failed`, `FAIL`, `REPAIR`, or equivalent USER rejection, the branch must route back to a bounded Workstream repair posture for the failed accepted scope before renewed Hardening and Live Validation. That returned-UTS Workstream repair may run bounded Hardening checks in conjunction with the Workstream repair loop after each repair slice/seam, but it cannot treat Hardening as a substitute for Workstream repair, cannot skip renewed formal H1/Hardening closeout when the repair is complete, and cannot skip renewed exact-path Live Validation and UTS handoff. After LV blockers are repaired and the affected LV proof path is green, Hardening must rerun because the branch changed after the prior Hardening pass. After rerun Hardening is green, Live Validation must rerun or explicitly reconfirm the proof path affected by the repair. USER review may confirm only the final post-repair Hardening plus LV-green result when USER validation is required. PR Readiness may rely only on the final post-repair Workstream/Hardening/LV/USER-review state, not on a superseded pre-repair Hardening pass, pre-repair LV run, or rejected UTS.
Allowed Loop States: `Hardening Green Before LV`, `LV Blocked / Repair First`, `LV Repair Applied`, `Post-LV-Repair LV Green`, `Post-LV-Repair Hardening Rerun Required`, `Post-LV-Repair Hardening Green`, `LV Reconfirmation Required`, `Returned UTS FAIL / Bounded Workstream Repair Required`, `Returned UTS Workstream Repair In Progress`, `Returned UTS Workstream Repair With Bounded Hardening Checks`, `Returned UTS Renewed H1 Required`, `Returned UTS Renewed LV Required`, `Returned UTS Renewed UTS Handoff Required`, and `Final Workstream/Hardening/LV/USER Review Green`.
Invalid Values: `Pre-Repair Hardening Treated As Final`, `Full Hardening Rerun While LV Known-Failing By Default`, `LV Repair Skips Hardening Rerun`, `Hardening Rerun Skips LV Reconfirmation`, `Returned UTS FAIL Treated As LV Retry Only`, `Returned UTS Repair Skips Workstream`, `Returned UTS Bounded Hardening Treated As Final H1`, `Returned UTS Repair Skips Renewed LV`, `USER Review Based On Pre-Repair Proof`, and `PR Readiness Uses Superseded Hardening`.
Blocking Conditions: `Known-Failing LV Repair First`, `Returned UTS Workstream Repair Missing`, `Returned UTS Renewed H1 Missing`, `Returned UTS Renewed LV Missing`, `Returned UTS Renewed UTS Handoff Missing`, `Post-LV-Repair Hardening Rerun Missing`, `Post-Hardening LV Reconfirmation Missing`, `Pre-Repair Hardening Treated As Final`, and `Final USER Validation Missing`.
Repair Owner: the current branch/worktree repairs its own LV blockers and reruns proof; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable loop-rule ambiguity; USER owns manual validation, waivers, and out-of-scope repair decisions.
Repair Path: classify the LV or UTS defect. For Codex-visible LV defects before UTS return, repair in-scope LV blockers, rerun or reconfirm the affected LV proof path to green, rerun Hardening over changed files, surfaces, proof rows, and coverage rows, rerun or reconfirm LV after Hardening when Hardening changes anything or invalidates proof, digest USER validation when required, then allow PR Readiness to inspect only the final post-repair state. For returned USER UTS `FAIL` / `REPAIR` / equivalent rejection, reopen a bounded Workstream repair for the failed accepted scope, preserve the returned UTS findings as active repair input, permit bounded Hardening checks inside the Workstream loop only as inspection/stabilization support, complete renewed H1/Hardening after the Workstream repair is exhausted or green, rerun exact-path Live Validation, regenerate UTS, and wait for USER UTS `PASS`, `WAIVED_WITH_REASON`, or another returned failure before PR Readiness.
USER Decision Required: required to waive rerun or reconfirmation, accept manual validation, approve an out-of-scope repair, proceed with residual risk, or route defects to a later branch.
Validation Owner: future helper/validator coverage should check this loop when machine-checkable; until then, Codex must inspect and report the loop state in the phase digest.
Final Disposition: PR Readiness is invalid when it relies on a pre-repair Hardening pass, a known-failing LV result, an LV repair without post-repair Hardening, or a post-Hardening state without LV reconfirmation or USER validation disposition when required.

## Branch Naming Prefix Rule

Active Nexus branch names and active branch authority records must not use the `codex/` prefix.
Use `feature/` or another USER-approved non-`codex/` prefix for current branch carriers.
Historical `codex/` branch names remain preserved traceability only and must not be treated as precedent for new or active branch naming.

## Canonical Phase Enum

The only normal branch phases are:

- `Branch Readiness`
- `Branch Planning`
- `Workstream`
- `Hardening`
- `Live Validation`
- `PR Readiness`
- `Release Readiness`

These are not normal phases:

- `No Active Branch`
- `Post-Release Canon Repair`

`No Active Branch` is a repo-level state, not a normal phase.
It may be:

- a blocked state when an admission gate or another required repair path is still open
- a steady-state resting posture when no implementation lane is currently selected and no branch should open by inertia

`Post-Release Canon Repair` is not a normal product phase. Source repair follows the owner-specific carrier route below; it does not authorize direct-main writes.
Codex must not use direct-main repair; `main` is protected and file-frozen for Codex work.

## Phase Alias UX Boundary

`Docs/governance_efficiency_operating_model.md` owns the governance efficiency operating model's human-facing alias map for phase names. The canonical phase names remain unchanged for source truth, validators, branch records, prompt contracts, and phase resolvers.

Aliases such as `Plan Review`, `Build`, `User Proof`, or `Release Validation` may explain a phase to the USER, but they must not replace canonical phase markers in repo files.

`Branch Planning` is the canonical phase between `Branch Readiness` and `Workstream`. It contains BP1, BP2, and BP3:

- BP1 - `USER Branch Vision Review`, using `USER_BRANCH_VISION_REVIEW.md`.
- BP2 - `USER Branch Plan Review`, using `USER_BRANCH_PLAN_REVIEW.md`.
- BP3 - `Workstream Entry / Orchestration Validation`.

`Workstream Entry` is BP3 inside `Branch Planning`; it is not inside `Workstream` and is not a standalone canonical phase. The `Workstream` phase begins only after BP1 and BP2 are accepted or explicitly waived, BP3 is green, and USER approves bounded Workstream implementation for the admitted same-branch package or explicitly named initial seam sequence. The first seam is the entry checkpoint, not stop authority.

### Implementation-Bearing Branch Standard

Rule Name: `Implementation-Bearing Branch Standard`
Owner: `Docs/phase_governance.md`
Applies To: Branch Readiness Stage 1, Branch Readiness Stage 2, BP1 USER Branch Vision Review, BP2 USER Branch Plan Review, BP3 Workstream Entry / Orchestration Validation, active external branch plans, local USER hub Branch Planning packets, helper output, validator output, and fixtures.
Required State: Branch Readiness Stage 2 is the legal stage for identifying infrastructure prerequisites, lane groundwork, missing private/public boundary setup, and route blockers before branch admission completes. Every runtime, product, source-truth, helper, validator, or governance repair branch admitted green from Branch Readiness Stage 2 must name a `Selected Implementation Route:` before BP1 begins. The selected route must be concrete enough for BP1 to define what the branch becomes, BP2 to plan how it will be built, BP3 to verify readiness to execute it, and Workstream to complete bounded implementation without inventing the branch purpose midstream.
Real Feature Implementation Definition: A real implementation route names the actual behavior, control, surface, state transition, workflow, source-truth enforcement, helper behavior, validator behavior, or runtime behavior that Workstream will create, change, or enforce. Proofs, packets, readiness matrices, registries, setup themes, boundary-control labels, decision paths, and validation plans are evidence or infrastructure unless they are tied to a named implemented control or behavior. A `boundary control` counts only when BP1/BP2 name the exact control and Workstream is expected to implement or enforce that control; a proof of a boundary is not the feature.
Deterministic Enforcement Preference: When a route-admission rule can be machine-checked, it should be backed by deterministic validator or fixture coverage. Simulation or fixture coverage must include prompt-like bypass attempts where implementation is deferred to BP2/TBD, proof packets are labeled as feature routes, or boundary-control language appears without a named implemented behavior. Semantic judgments that cannot be machine-checked must be called out as human review requirements instead of reported as validator-proof green.
Required Route Fields: `Selected Implementation Route:`, `Implementation Route Class:`, `Concrete Deliverable:`, `Implementation Output:`, `Infrastructure / Setup Relationship:`, `USER Action Gate:`, `Route Disposition:`, and `Retarget / Rename Recommendation:`.
Infrastructure / Setup Rule: lane setup, repo/root/remote setup, skeleton setup, packet generation, registry creation, manifest creation, or other groundwork is branch-worthy only when it is execution-enabling for the selected implementation route or when USER approves an exact setup action gate that names the allowed setup action and blocked actions. Creating User/Public, Developer, or Owner lanes by itself is groundwork, not a feature implementation carrier.
BR2 Blocker Packet Rule: If BR2 discovers that User/Public, Developer, or Owner lane work cannot proceed until infrastructure or groundwork exists, BR2 must stop with `Route Disposition: HOLD` or `Route Disposition: RETARGET / RENAME` and return a USER decision packet. That packet must name `Infrastructure / Lane Groundwork Blockers:`, `Required Before This Route Can Proceed:`, `Concrete Feature Routes Available Now:`, `Deferrable Groundwork:`, `Non-Deferrable Groundwork:`, `Codex Recommendation:`, and `Exact USER Decision Needed:`. USER may approve the prerequisite groundwork, defer it and select a different concrete worktree-focused feature route that can proceed now, rename/retarget the branch, or hold with No Active Branch. Repeated deferral is legal until the remaining candidate routes all depend on non-deferrable groundwork; at that point BR2 must report the exact non-deferrable blocker instead of inventing a planning-only carrier.
Invalid Route Shapes: planning-only carriers, readiness-only carriers, infrastructure-only carriers, lane-setup-only carriers, branches whose deliverable is to choose later implementation branches, branches whose BP2 can green with orchestration only, and branches that defer every concrete deliverable to a later branch without an exact USER action gate are invalid for BR2 admission.
Terminology Rule: Use `User/Public lane`, `Developer lane`, and `Owner lane` as lanes or environments, not product version numbers. New and current branch-planning text must say `Developer lane`, not `Dev lane`. Historical branch names, previously accepted private repo placeholders, and clearly marked receipts may preserve older wording only as traceability, not current lane law.
Blocking Conditions: `Implementation-Bearing Route Missing`, `Planning-Only Carrier`, `Infrastructure-Only Carrier`, `Exact USER Action Gate Missing`, `Branch Retarget/Rename Decision Required`, and `Developer Lane Terminology Drift`.
Repair Path: BR1 recommends continue, retarget, rename, or hold. BR2 investigates route prerequisites, presents blockers and options, and admits green only after the selected implementation route is named or USER explicitly chooses a legal setup/action-gate path. BP1, BP2, and BP3 serve that route. If the route changes, Codex must return to BR1/BR2 or BP1 as source truth requires instead of continuing Branch Planning by inertia.

### Family Feature Vision Scope And Element Proof Chain

Rule Name: `Family Feature Vision Scope And Element Proof Chain`
Owner: `Docs/phase_governance.md` for phase gates and blockers; `Docs/family_visions/README.md` for Family Feature Vision naming, compact ID, category scope, deferred carryforward, and owner relationship; `Docs/branch_plans/README.md` for branch-plan element traceability.
Applies To: Branch Readiness Stage 1, Branch Readiness Stage 2, BP1 USER Branch Vision Review, BP2 USER Branch Plan Review, BP3 Workstream Entry / Orchestration Validation, Workstream, Hardening, Live Validation, active external branch plans, Family Feature Vision files, USER review packets, helper output, validator output, and future fixtures.
Required State: A Family Feature Vision is a durable feature-category owner inside exactly one FAM. It must use a stable FFV ID or approved transition alias, a human-readable category title, a durable feature element inventory, deferred carryforward facts, proof expectations, and BP1 consumption notes. It must not be named or scoped as a branch route, Slice/SLC, seam, current implementation package, or live operational state record.
Allowed Values: `Category-Level FFV`, `Transition Alias Pending Rename`, `Feature Vision Not Applicable`, `FFV Repair Required`, `USER Decision Required`.
Invalid Values: `Slice-Specific FFV`, `SLC-Specific FFV`, `Seam-Specific FFV`, `Branch-Route FFV`, `Implementation-Package FFV`, `Selected-Next FFV`, `Active-State FFV`, `Live Branch Ledger FFV`.
Required FFV Inventory Rule: Before BP1 begins for a selected feature-bearing route, Codex must inventory all tracked `Docs/family_feature_visions/*.md` files in the owning worktree when the directory exists. The inventory must classify every FFV as `Valid Category-Level FFV`, `Rename / Reframe Required`, `Compact ID Missing`, `Pointer Migration Required`, `Live-State Wording Repair Required`, `Historical Transition Alias`, or `USER Decision Required`. If the current approval covers FFV content mutation, all affected FFVs in that worktree must be repaired or explicitly deferred with a blocker before BP1. If mutation is not approved, Codex must return the blocker and exact approval text.
Required Pointer Rule: Any FFV rename, compact-ID migration, or category reframe must update every in-scope source-truth pointer, branch record pointer, branch plan pointer, active external-state pointer, USER packet context pointer, backlog/roadmap pointer, and generated review reference that names the old FFV path or title. Stale references block on `Family Feature Vision Pointer Migration Missing`.
Required Element Rule: BP1 must classify relevant FFV elements as `Selected`, `Deferred`, or `Blocked` and explain grouping, deferral reason, dependency trigger, owner, proof expectation, and return path. BP2/BP3 must map selected elements to branch-local Slice/SLC/seam work, validation, proof, rollback, and future-gated boundaries. Workstream, Hardening, and Live Validation must carry selected element IDs forward until each implemented element is proven, waived, deferred, or blocked.
Required Proof Chain: `FFV element -> BP1 selected/deferred -> BP2/BP3 mapped to branch-local Slice/SLC/seam -> Workstream implemented -> Hardening inspected -> Live Validation proven -> USER packet evidence`.
External State Guardrail: Family Feature Vision files may own durable visioned elements, deferred facts, and proof expectations. They must not own active branch status, current selected-next state, current BP gate state, live branch lifecycle state, current worktree binding, implementation approval, live PR/release state, or active branch planning ledgers. Those facts belong to `D:\Nexus Desktop AI\Governance State`, Git/GitHub/helper-derived truth, active Branch Planning packets, or USER decision packets as routed by source truth.
Blocking Conditions: `Family Feature Vision Required For Selected Feature`, `Feature Vision Sufficiency Check Failed`, `Family Feature Vision Slice-Scoped`, `Family Feature Vision Compact ID Missing`, `Family Feature Vision Inventory Repair Required`, `Family Feature Vision Pointer Migration Missing`, `FFV Live-State Leakage`, `FFV Element Selection Matrix Missing`, `FFV Element Proof Chain Missing`, `Deferred Carryforward Applicability Missing`, and `Deferred Carryforward Branch Sprawl`.
Repair Owner: owning family/worktree for FFV content repair; active branch-planning owner for selected/deferred element and proof-chain repair; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy for source-truth rule repair; USER for new FFV content-file creation, rename, file movement, deletion, external-state mutation, or waiver decisions.
Repair Path: Reframe the FFV as a category-level feature owner, assign or preserve the compact ID/transition alias, repair the element inventory and deferred carryforward rows, update every pointer in the owning worktree and approved external records, regenerate USER review packets when they named the old FFV, and rerun the relevant validators. If the repair would mutate a sibling worktree, external state, helper code, validator code, or generated packet outside the current approval, stop and return the exact USER decision needed.
USER Decision Required: Required for first FFV folder/index creation, new FFV content files, FFV file renames, file movement, deletion, archival, sibling-worktree mutation, external-state pointer mutation, helper/validator implementation, or any waiver that lets BP1 proceed without a sufficient FFV for a selected feature-bearing route.
Validation Owner: Future helper/validator hardening should extend `dev/orin_branch_governance_validation.py`, `dev/orin_branch_readiness_planning_fixture_validation.py`; USER review preparation and delivery must use the external USER lifecycle owner; green validation remains evidence and Codex must still inspect the actual FFV scope, pointers, and USER packet state.
Final Disposition: The branch may proceed to BP1 only when the relevant FFV is category-level, sufficient, pointer-consistent, no-live-state-clean, and element-selection-ready, or when source truth records a valid `Family Feature Vision Not Applicable` reason or explicit USER waiver.

### BR1 Candidate Viability / Grouping Matrix

Rule Name: `BR1 Candidate Viability / Grouping Matrix`
Owner: `Docs/phase_governance.md`
Applies To: Branch Readiness Stage 1 candidate selection, successor-branch analysis, family-scoped Branch Readiness, Branch Readiness packets that consume Family Feature Vision or Deferred Feature Carryforward, helper output, validator output, and future fixtures.
Required State: Before BR1 recommends USER-selectable branch candidates, it must provide a candidate viability and grouping matrix that proves each candidate is an implementation-bearing package option rather than a planning, readiness, manifest, setup, or support-only branch. The matrix is analysis evidence only; it must not create selected-next truth, active branch state, branch authority, PR state, or release-window state in repo docs.
Required Matrix Fields: `Option name`, `Owning FAM / worktree`, `Main feature/package objective`, `Concrete feature outcome`, `Implementation-bearing route class`, `Behavior change classification`, `Support / infrastructure relationship`, `Family Feature Vision context`, `Deferred Feature Carryforward consumed`, `Cross-FAM Dependency Map`, `Affected FAMs`, `Affected FFV / Element or Not Created`, `Shared Surface Overlap Forecast`, `Dependency Scope Class`, `Carry-In / Deferral / Transfer Decision`, `Platform Contract Adoption Matrix when applicable`, `Repo-Wide Migration Neutralization Proof when applicable`, `Grouping recommendation`, `Split reason if not grouped`, `Expected Slice/SLC/seam map`, `Proof path`, `Largest safe coherent package explanation`, `Tiny-branch sprawl review`, `Blockers`, and `Exact USER decision needed`.
Allowed Implementation-Bearing Route Classes: `User-visible behavior change`, `Runtime behavior change`, `Developer tooling behavior change`, `Source-truth enforcement change`, `Helper behavior change`, `Validator behavior change`, `Control / permission / policy behavior change`, or `Governance rule enforcement change`.
Invalid Candidate Shapes: planning-only branches, readiness-only branches, support-only branches, infrastructure-only branches, manifest-only branches, registry-only branches, proof-only branches, setup/skeleton-only branches without exact USER action gate, candidates whose purpose is to choose later candidates, candidates that defer every concrete deliverable to another branch, and tiny branches that split work when one FAM/package objective, owner/worktree, route, release timing, and validation path can safely carry the grouped scope.
Family Feature Vision Handling: If the candidate is a selected feature-bearing route and no sufficient USER-approved Family Feature Vision exists for the feature category, BR1 must report `Family Feature Vision Required For Selected Feature` and make the next legal phase Family Feature Vision planning/admission on the current legal carrier before BP1. If the candidate is governance-only, release-support, pure helper/validator, source-truth-only, or otherwise non-product, BR1 may report `Family Feature Vision Not Applicable` with a reason.
Deferred Feature Carryforward Handling: BR1 must identify deferred carryforward items from the relevant Family Feature Vision when that owner exists. For each option, BR1 must state which deferred items apply, why the dependency trigger is satisfied, which items remain future-gated, why they remain deferred, and whether the grouped option is the largest safe coherent package. Deferred carryforward is durable planning context; it is not selected-next truth and does not authorize implementation by itself.
Cross-FAM Dependency Handling: BR1 must identify cross-FAM dependency candidates that are relevant to each option, including dependencies discovered by the originating FAM and durable dependency candidates already recorded in the affected FAM or FFV. BR1 must classify each dependency using the `Cross-FAM Dependency And Shared Surface Overlap Model`, state whether the dependency is awareness-only, dependency-bounded, a priority carry-in, a platform contract, a coordinated cross-FAM patch, a repo-wide migration / halt, or transferred FAM work, and explain why the option can proceed, defer, narrow, transfer, or stop. Cross-FAM dependency analysis is durable planning evidence; it must not create selected-next truth, active branch state, current assignment, PR state, release-window state, or a repo-tracked live dependency ledger.
Grouping Rule: BR1 must recommend grouping support, infrastructure, helper, validator, source-truth, and deferred carryforward work into the selected implementation-bearing package when the work shares the same FAM, package objective, route, owner/worktree, release timing, risk class, and validation/proof path. If Codex recommends a split, the packet must name the split reason and the future owner. Missing split reason blocks on `BR1 Candidate Split Reason Missing`.
Blocking Conditions: `BR1 Candidate Implementability Missing`, `BR1 Candidate Grouping Matrix Missing`, `BR1 Planning-Only Candidate Drift`, `BR1 Support-Only Candidate Drift`, `BR1 Readiness-Only Candidate Drift`, `BR1 Manifest-Only Candidate Drift`, `BR1 Tiny-Branch Sprawl`, `BR1 Feature Vision Context Missing`, `BR1 Candidate Split Reason Missing`, `Implementation-Bearing Route Unproven`, `Cross-FAM Dependency Undocumented`, `Cross-FAM Dependency Scope Unclassified`, `Cross-FAM Carry-In Not Evaluated At BR1`, `Transferred FAM Work Requires Owning Branch`, `Affected FAM Receipt Missing`, `Platform Contract Adoption Matrix Missing`, `Repo-Wide Migration Neutralization Missing`, `Worktree-To-Worktree Mutation Approval Missing`, `FFV Dependency Candidate Missing`, and `Cross-FAM Dependency Fold-Down Missing`.
Repair Path: BR1 must revise the candidate matrix, group support work into a coherent implementation-bearing package, route to Family Feature Vision planning/admission, hold with No Active Branch, or return a USER decision packet before Stage 2. BR2 may admit only candidates whose BR1 matrix clears the blockers or records an explicit USER waiver/action gate.
Validation Owner: Future helper/validator enforcement should extend `dev/orin_branch_governance_validation.py` and `dev/orin_branch_readiness_planning_fixture_validation.py`; this docs-only pass does not authorize helper, validator, or fixture mutation.

### Cross-FAM Dependency And Shared Surface Overlap Model

Rule Name: `Cross-FAM Dependency And Shared Surface Overlap Model`
Owner: `Docs/phase_governance.md` for phase gates and blockers; `Docs/family_visions/README.md` for durable Family Vision / Family Feature Vision dependency candidate shape; `Docs/worktree_slots.md` for worktree mutation confinement; `Docs/feature_backlog.md` for compact taxonomy mirrors.
Applies To: Branch Readiness Stage 1, Branch Readiness Stage 2, BP1 USER Branch Vision Review, BP2 USER Branch Plan Review, BP3 Workstream Entry / Orchestration Validation, Workstream, Hardening, Live Validation, PR Readiness, active external branch plans, Family Vision records, Family Feature Vision records, USER review packets, helper output, validator output, rebaseline / reconciliation packets, and future fixtures.
Required State: A branch has one `Owning FAM` and one legal owning worktree. The branch may identify and, when admitted, perform dependency-bounded cross-FAM work only when that work is required for the owning FAM's selected implementation route, is smaller than a separate branch-worthy package for the affected FAM, has an explicit dependency ID, records the affected FAM / FFV / element or `Not Created`, and preserves proof, rollback, fold-down, and affected-FAM receipt expectations. Shared-file overlap between independently owned worktrees is legal when each branch owns its own reason for touching the shared surface and rebaseline / reconciliation handles the merge. Direct worktree-to-worktree mutation remains blocked unless USER grants a bounded waiver.
Allowed Values:

- `Local FAM Only`
- `Cross-FAM Awareness`
- `Dependency-Bounded Cross-FAM Work`
- `Priority Carry-In`
- `Platform Contract`
- `Coordinated Cross-FAM Patch`
- `Repo-Wide Migration / Halt`
- `Transferred FAM Work`

Invalid Values:

- `Unclassified Cross-FAM Dependency`
- `Hidden Dependency`
- `Another FAM As Dependency Queue`
- `Borrowed Branch Scope`
- `FAM-002 Generic UI Polish Carrier`
- `Worktree-To-Worktree Mutation`
- `Shared Surface Overlap Treated As Mutation`
- `Live Dependency Ledger In Repo Docs`
- `Repo File-State Tracking`

Shared Surface Overlap Safe Harbor: Shared-file overlap is not automatically cross-worktree work. Two FAM branches may independently touch the same repo file when each branch has a legal owning-FAM reason, records its intended write set in the active external branch plan, and resolves overlap through Pre-Rebaseline Impact Audit, Branch Change Intent Ledger evidence, PR Readiness, merge sequencing, and post-merge reconciliation. This safe harbor does not authorize one thread to edit another active worktree, assume another branch's scope, or hide cross-FAM dependency work as generic overlap.
FAM-002 Presentation Consumption Safe Harbor: FAM-002 is the shared Desktop Interface / UI presentation authority and may be consumed by other FAM branches without opening a FAM-002 worktree when the consuming branch owns the feature behavior and the UI work is necessary for its accepted Family Vision, Family Feature Vision, branch plan, and proof path. This safe harbor does not authorize generic app-wide UI polish, broad visual redesign, FAM-002 selected-next truth, another FAM's feature behavior, or direct sibling-worktree mutation. A dedicated FAM-002 branch requires USER admission of a concrete Desktop Interface feature category that no consuming FAM owns.
Worktree-To-Worktree Mutation Boundary: Worktree-to-worktree mutation means one thread edits, stages, commits, rebases, merges, cleans, validates-as-owner, or otherwise mutates another active worktree or branch. It is blocked by default on `Worktree-To-Worktree Mutation Approval Missing`, `Parallel Worktree Coordination Missing`, or `Governance Routing Barrier` unless USER explicitly approves a bounded waiver with scope, expiration, validation, and return path.
Dependency-Bounded Work Rule: The owning branch may carry bounded affected-FAM work only when BR1/BR2 prove the work is necessary for the owning route, does not become the affected FAM's whole branch objective, has a clear affected-FAM receipt / carry-in / fold-down target, and does not require direct sibling-worktree mutation. If the work becomes large, user-visible, architecture-defining, package-defining, or independently branch-worthy for the affected FAM, it must be classified as `Transferred FAM Work` and routed to that FAM's Branch Readiness path.
Priority Carry-In, Not Scope Capture: A platform contract or dependency candidate that creates required future work for an affected FAM must be evaluated by that FAM's next BR1. It does not automatically become the only branch objective; the affected FAM should group the carry-in into the relevant FFV or coherent package when practical and split only when the grouping would blur ownership, weaken proof, or create unsafe release timing.
Platform Contract Rule: Platform contract work defines a durable contract, compatibility default, schema, path, update/patch behavior, permission boundary, setup behavior, or adoption expectation other FAMs may consume later. The originating branch must prove existing affected families are not broken, document adoption classes, and avoid forcing every FAM to patch immediately unless the dependency is classified as `Coordinated Cross-FAM Patch` or `Repo-Wide Migration / Halt`.
Repo-Wide Migration / Halt Rule: A branch that changes install, update, patch, launch, repo split, external state, validation, reconciliation, or workflow assumptions broadly enough to affect multiple active FAMs must be admitted as `Repo-Wide Migration / Halt` before Workstream. BP3 must prove affected worktrees are neutral, clean, paused, or explicitly waived; Workstream may then perform only the admitted cross-FAM migration work in one carrier branch; Hardening and Live Validation must prove each affected FAM surface and return-digest / reconciliation path.
Implementation Ownership Split: The branch that introduces a dependency owns the introduced contract, compatibility default, and proof that existing affected families are not broken. The affected FAM owns later feature-specific adoption, FFV creation or repair, polish, expansion, and user-facing follow-through unless the current branch explicitly admits dependency-bounded affected-FAM work.
Repo / External State Boundary: Repo docs may record durable dependency classes, dependency candidates, source-truth owner rules, FFV element IDs, durable dispositions, fold-down receipts, and review requirements. Repo docs must not track live changed-file state, current branch status, current worktree assignment, selected-next truth, active dependency queues, PR state, release-window state, or mutable validation posture. Live operational state belongs to `D:\Nexus Desktop AI\Governance State`, Git/GitHub/helper-derived truth, USER review packets, active external branch plans, or Codex digests as routed by source truth.
Blocking Conditions: `Cross-FAM Dependency Undocumented`, `Cross-FAM Dependency Scope Unclassified`, `Cross-FAM Carry-In Not Evaluated At BR1`, `Transferred FAM Work Requires Owning Branch`, `Affected FAM Receipt Missing`, `Platform Contract Adoption Matrix Missing`, `Repo-Wide Migration Neutralization Missing`, `Worktree-To-Worktree Mutation Approval Missing`, `FFV Dependency Candidate Missing`, `Cross-FAM Dependency Fold-Down Missing`, `Shared Surface Overlap Misclassified`, `FAM-002 Presentation Consumption Ambiguous`, and `Repo File-State Tracking Regression`.
Repair Owner: owning branch/worktree for dependency classification and branch-local proof; affected FAM/worktree for future adoption and FFV content repair; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy for source-truth rule repair; USER for cross-worktree mutation waivers, repo-wide migration / halt admission, new worktree creation, or transferred FAM branch admission.
Repair Path: Classify the dependency, identify the owning and affected FAMs, record the dependency candidate or affected-FAM receipt, update BR1/BR2 matrices, move live operational facts to external state or helper evidence, route branch-worthy affected-FAM work to that FAM, clarify whether FAM-002 is supplying presentation law or attempting to own implementation, or request USER approval for a coordinated cross-FAM patch / repo-wide migration / halt. If direct sibling-worktree mutation would be required, stop and return the exact USER decision needed.
USER Decision Required: Required for worktree-to-worktree mutation, repo-wide migration / halt admission, transferred FAM branch creation, new worktree creation, external-state mutation beyond approved branch planning, helper/validator implementation, or any waiver that lets dependency-bounded work proceed without the required classification, proof, or affected-FAM receipt.
Validation Owner: Future helper/validator hardening should extend `dev/orin_branch_governance_validation.py`, `dev/orin_branch_readiness_planning_fixture_validation.py` for their applicable product/planning contracts. Current operational implementation belongs to the approved external source owner; `dev/orin_worktree_rebaseline_audit.py` remains historical-root forensic support rather than a preferred operational extension point; USER review preparation and delivery must use the external USER lifecycle owner. Green validation is evidence only; Codex must still inspect dependency scope, overlap classification, active-state leakage, and USER decision state.
Final Disposition: A branch may proceed only when cross-FAM dependencies are classified, shared-surface overlap is documented without becoming live repo state, direct worktree mutation is absent or USER-waived, affected-FAM receipts / carry-ins are preserved, and any platform contract or repo-wide migration proof required by the selected dependency class is present.

### Runtime Failure / Recovery Carrydown Gate

Rule Name: `Runtime Failure / Recovery Carrydown Gate`
Owner: `Docs/phase_governance.md` for phase gates and blockers; `Docs/family_visions/FAM-001_boot_interface.md` for fatal launcher/runtime diagnostics and future recovery-surface vision; `Docs/workstreams/FB-034_recoverable_diagnostics.md` for historical bounded `launch_failed` evidence only; `Docs/family_visions/FAM-002_desktop_interface.md` for visible diagnostics/failure panel presentation standards; the consuming FAM / FFV / active external branch plan for feature-specific failure, degraded, blocked, unavailable, and proof behavior.
Applies To: Branch Readiness Stage 1, Branch Readiness Stage 2, BP1 USER Branch Vision Review, BP2 USER Branch Plan Review, BP3 Workstream Entry / Orchestration Validation, Workstream, Hardening, Live Validation, PR Readiness, Family Vision records, Family Feature Vision records, active external branch plans, USER review packets, helper output, validator output, and future fixtures when a branch creates, changes, exposes, routes, diagnoses, degrades, blocks, launches, recovers, retries, repairs, or validates runtime/user-facing behavior.
Required State: Every relevant branch must classify how its feature behaves when it fails, degrades, is blocked, is unavailable, or cannot launch. The packet or active external branch plan must name `Failure Class:`, `USER-Facing Failure State:`, `Recovery Option:`, `Fallback Behavior:`, `Support / Log / Bundle Behavior:`, `Privacy / Safety Boundary:`, `Photo / Video Or USER Manual Proof:`, `Owning FAM:`, and `Consumed Failure / Recovery Rules:`. Fatal launcher/runtime diagnostics and recovery surfaces route to FAM-001. Bounded repeated recoverable `launch_failed` evidence routes to FB-034 only as released historical evidence until USER admits a new owner. Visible diagnostics or failure panels consume FAM-002 presentation standards. Feature-specific disabled, degraded, blocked, no-data, unavailable, provider/privacy, setup, repair, or retry behavior remains owned by the FAM whose feature surface is changing.
Allowed Values:

- `Fatal Launcher / Runtime Failure`
- `Recoverable Action / Launch Failure`
- `Degraded But Running`
- `Blocked By Policy`
- `Disabled / Deferred Feature`
- `Unavailable Prerequisite`
- `No Failure Surface Impact`

Invalid Values:

- `Unclassified Failure Behavior`
- `FB-034 As Active Product Owner`
- `Fatal Path Collapsed Into Recoverable Popup`
- `Recoverable Path Treated As Fatal Crash`
- `Hidden Failure`
- `Helper PASS As Recovery Proof`
- `Logs Only As USER-Facing Proof`
- `Generic Fallback`
- `Support Bundle Without Privacy Boundary`
- `Feature Failure Owned By Another FAM`

Future FAM-001 FFV Route: The actual user-facing diagnostics/recovery/support surface should be admitted through a later USER-approved FAM-001 Family Feature Vision, with candidate titles such as `F1-FF01 Runtime Diagnostics And Recovery Surface` or `F1-FF01 Failure Recovery And Support Reporting`. That future FFV may define fatal launcher failure, repeated recoverable failure, startup abort, recovery exhaustion, support-bundle preparation, manual issue draft, privacy warning, retry/close/repair options, and proof expectations. This gate does not create that FFV file or open a FAM-001 worktree by itself.
Blocking Conditions: `Runtime Failure / Recovery Carrydown Missing`, `Failure Class Unclassified`, `USER-Facing Failure State Missing`, `Recovery Option Missing`, `Fallback Behavior Missing`, `Support / Log / Bundle Boundary Missing`, `Privacy / Safety Boundary Missing`, `Failure Proof Path Missing`, `FAM-001 Diagnostics Ownership Bypassed`, `FB-034 Historical Evidence Misused As Active Owner`, `FAM-002 Failure Panel Presentation Missing`, and `Feature-Specific Failure Ownership Ambiguous`.
Repair Owner: The current branch/worktree repairs feature-local failure behavior and proof classification; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable phase/source-truth rule drift; FAM-001 owns future diagnostics/recovery surface planning when USER admits it; FAM-002 owns reusable visual/presentation standards; the USER owns any waiver that allows a branch to proceed without the required failure/recovery classification.
Repair Path: Classify the failure class, identify FAM-001/FAM-002/consuming-FAM responsibilities, route fatal/recovery-surface product work to future FAM-001 FFV planning when needed, keep FB-034 as historical evidence unless a new branch admits a broader recoverable diagnostics scope, add feature-local degraded/blocked/unavailable behavior and proof expectations to the active branch plan, or stop for USER decision when ownership or proof remains ambiguous.
USER Decision Required: Required for new FAM-001 FFV content-file creation, new diagnostics/recovery implementation, helper/validator enforcement, support-bundle behavior changes, privacy/support reporting behavior changes, broad recoverable diagnostics expansion, fatal launcher/runtime behavior changes, or any waiver of this carrydown gate.
Validation Owner: Future helper/validator hardening should extend `dev/orin_branch_governance_validation.py`, `dev/orin_branch_readiness_planning_fixture_validation.py`, live-validation helpers, and diagnostics/recoverable-failure validators where machine-checkable. Green validation is evidence only; Codex must still inspect failure/recovery ownership, privacy boundary, and visible proof.
Final Disposition: Workstream, Hardening, Live Validation, and PR Readiness may proceed only when relevant failure/recovery behavior is classified, owner-routed, user-facing proof is planned or captured, and no branch is silently relying on logs, helper output, historical FB-034 evidence, or another FAM to own its feature-specific failure state.

### Visual Inheritance Matrix Gate

Rule Name: `Visual Inheritance Matrix Gate`
Owner: `Docs/phase_governance.md` for phase gates and blockers; `Docs/nexus_vision.md` for Project UI Vision; `Docs/family_visions/FAM-002_desktop_interface.md` for reusable presentation standards; the owning Family Vision / Family Feature Vision / active external branch plan for feature-specific UI grammar and proof.
Applies To: Branch Readiness Stage 1, Branch Readiness Stage 2, BP1 USER Branch Vision Review, BP2 USER Branch Plan Review, BP3 Workstream Entry / Orchestration Validation, Workstream, Hardening, Live Validation, PR Readiness, USER review packets, helper output, validator output, and future fixtures when a branch creates or changes user-facing UI, controls, windows, cards, HUDs, overlays, setup flows, status indicators, folder pickers, evidence surfaces, diagnostics panels, or failure/recovery panels.
Required State: The branch must include a `Visual Inheritance Matrix` before Workstream implementation when visible UI changes are admitted. Each row must name `New / Changed Element:`, `Surface Classification:`, `Inherited Existing Element Or Surface:`, `Owning UI Rule:`, `FAM-002 Component Grammar:`, `Window Chrome / Frame Treatment:`, `Platform Exception:`, `Shape / Radius Comparison:`, `Spacing / Density Comparison:`, `Typography Comparison:`, `Card / Row / Divider Treatment:`, `Color / Shadow / Glow Treatment:`, `Hover / Focus / Disabled State:`, `Scrollable / Resize / Transient State Proof:`, `Allowed Exception Or New Grammar:`, `Proof Artifact:`, and `Verdict:`. If no existing element is a valid ancestor, the branch must say why and record the USER-approved new visual grammar before implementation.
Allowed Values: The matrix uses field-specific allowed values. `Surface Classification:` values and `Verdict:` values are not interchangeable.

Allowed `Surface Classification:` Values:

- `Nexus-Owned Product Surface`
- `Platform-Native Exception`
- `Diagnostic / Developer Surface`
- `External Surface`
- `Not Applicable`

Allowed `Verdict:` Values:

- `Inherited`
- `Inherited With Explicit Exception`
- `New Grammar USER Accepted`
- `Needs Repair`
- `USER Decision Required`

Invalid Values:

- `Helper Green`
- `Looks Fine`
- `Generic Nexus Style`
- `No Comparison Needed`
- `Screenshot Exists`
- `Marker PASS`
- `Deferred Visual Review`
- `FAM-002 Owns It`
- `Default OS Chrome By Accident`
- `Native Title Bar Accepted By Inertia`
- `Window Chrome Not Inspected`
- `Surface Class Assumed`
- `Platform Exception By Inertia`

Blocking Conditions: `Visual Inheritance Matrix Missing`, `Existing Element Sample Missing`, `Visual Exception Not USER Accepted`, `Helper Green Treated As Visual Proof`, `Screenshot Without Adjudication`, `Per-Element Visual Verdict Missing`, `FAM-002 Presentation Consumption Missing`, `Feature UI Ownership Ambiguous`, `NDAI Window Chrome Missing`, `Default OS Chrome Used Without Exception`, `Nexus-Owned Surface Classification Missing`, `Platform Exception Unclassified`, `FAM-002 Component Grammar Missing`, and `Obvious UI Failure Passed To USER`.
Repair Owner: The current branch/worktree repairs branch-local UI and proof; FAM-002 supplies reusable presentation law but does not take over the feature implementation; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable rule drift; USER decides deliberate new grammar or waiver.
Repair Path: Identify the inherited element, compare the required visual dimensions, repair mismatches before USER handoff when approval covers repair, route deliberate new grammar through BP1/BP2/BP3 and USER acceptance, or return a blocker instead of asking USER to rediscover obvious UI defects during UTS.
USER Decision Required: Required for a new visual grammar, broad app-wide redesign, waiver of visual inheritance proof, or FAM-002 branch admission.
Validation Owner: Future helper/validator hardening should extend branch-readiness fixture validation, USER review bundle validation, visual proof/live-validation helpers, and source-owner checks where machine-checkable. Green validation is evidence only; Codex must still inspect the actual visual artifacts and compare them to the matrix.
Final Disposition: A user-facing UI branch is not ready for UTS handoff, PR Readiness, or release-facing closeout while unwaived visual matrix rows are missing, unproven, or inconsistent with screenshots/video/frame evidence.

### Evidence Independence / Anti-Circular Validation Gate

Rule Name: `Evidence Independence / Anti-Circular Validation Gate`
Owner: `Docs/phase_governance.md` for phase blocking; `Docs/validation_helper_registry.md` for helper/validator interpretation; `Docs/branch_plans/README.md` for branch proof-plan shape; the applicable vision owner for product claim source truth.
Applies To: BR1, BR2, BP1, BP2, BP3, Workstream, Hardening, Live Validation, PR Readiness, USER packets, helper output, validator output, and Codex closeout claims when a branch claims a product, UI, runtime, vision, proof, or phase-gate result is green.
Required State: Each gate-relevant claim must name `Claim:`, `Claim Class:`, `Source-Truth Owner:`, `Minimum Proof Strength:`, `Independent Evidence Source:`, `Evidence Class:`, `Evidence Provided:`, `Known Limitation:`, `Codex Adjudication Result:`, and `Next Disposition:`. A branch may use its own BP1/BP2/BP3 plan to define expected behavior, but it may not use that same plan, marker presence, helper green, generated manifest, screenshot existence, or Codex assertion as the only proof that the behavior or UI actually satisfies the vision.

Claim Class Model:

- `Governance / Source-Truth Claim`: requires the owning source-truth citation plus changed-file/diff evidence or validator/helper evidence when applicable; helper green supports the claim but does not replace source-owner review.
- `Runtime Behavior Claim`: requires observed runtime proof from the exact normal USER desktop runtime launcher or an accepted launcher-equivalence proof/USER waiver for that exact claim; logs, markers, and direct-runtime helpers are supporting evidence only.
- `Visual / UI Claim`: requires photo, video, ordered frame-sequence, focused screenshot, or equivalent visual artifact evidence plus comparison against Project Vision, FAM-002 grammar, applicable Family/Family Feature Vision, and the accepted Branch Vision/BP2/BP3 proof plan; screenshot path or manifest existence alone is not acceptance.
- `Security / Privacy Claim`: requires source/config proof plus runtime/settings-state or leak-prevention evidence when the claim is observable; claims about private/public boundaries, provider state, cache/memory, or data exposure must identify the boundary owner and limitation.
- `Failure / Recovery Claim`: requires observed failure/recovery path proof, or accepted simulated failure proof with limitation, plus the relevant Runtime Failure / Recovery Carrydown owner.
- `Helper / Validator Claim`: may prove that a helper or validator executed and returned a result; it cannot by itself prove product behavior, visual quality, user acceptance, or durable source-truth correctness.
- `External Live Truth Claim`: requires Git, GitHub, helper-derived live truth, or external operational state evidence as routed by source truth; repo docs may record durable receipts but must not become the live-state ledger.
- `Manual / Subjective USER Claim`: requires USER manual validation, explicit USER waiver, or a named blocker when Codex cannot objectively adjudicate the claim.

Proof Strength Values:

- `Direct Independent Proof`
- `Comparative Visual / Runtime Proof`
- `Source-Truth / Diff Proof`
- `Supporting Diagnostic Evidence`
- `Manual USER Validation`
- `USER Waiver`
- `Unproven`

Minimum Proof Rule: Supporting diagnostic evidence cannot be upgraded into direct proof by confidence wording, helper success, marker presence, schema conformance, manifest creation, screenshot existence, or plan prose. If the minimum proof strength for the claim class is unavailable, the claim must be marked `Manual USER Validation Required`, `USER Waiver Required`, `Repair Required`, or `Blocked` instead of `PASS`.
Allowed Values:

- `Independent Evidence Present`
- `Supporting Evidence Only`
- `Manual USER Validation Required`
- `USER Waiver Required`
- `Not Applicable With Reason`
- `Repair Required`
- `Blocked`

Invalid Values:

- `Claim Proven By Own Plan`
- `Green Because Helper Passed`
- `Screenshot Exists Therefore Accepted`
- `Manifest Exists Therefore Accepted`
- `Vision Cited But Not Compared`
- `Self-Attested`
- `Helper Green Therefore Accepted`
- `Marker Or Schema Exists Therefore Proven`
- `Plan-Only Proof`
- `Screenshot Path Only`
- `Generated Manifest Accepted`
- `No Limitation Recorded`

Blocking Conditions: `Circular Validation Detected`, `Claim Proven By Own Plan`, `Independent Evidence Missing`, `Vision Proof Alignment Missing`, `Helper Green Treated As Product Proof`, `Screenshot Without Adjudication`, `Manifest Treated As Acceptance Proof`, `Manual USER Validation Not Elevated`, `Claim Class Missing`, `Evidence Class Missing`, `Proof Strength Overstated`, `Supporting Evidence Treated As Direct Proof`, `Plan-Only Proof`, `Marker Or Schema Proof Misclassified`, `Screenshot Path Treated As Visual Acceptance`, `Live Validation Comparison Missing`, and `USER Validation Escalation Missing`.
Repair Owner: The current branch/worktree repairs branch-local proof gaps; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable rule drift; helper/validator owners repair confirmed false-green or false-red tooling; USER decides waivers or manual validation.
Repair Path: Identify the claim, cite the source-truth owner, gather independent evidence from runtime behavior, visual artifacts, real user-path interaction, code/diff review, Git/GitHub live truth, helper output, or USER manual validation as appropriate, record limitations, and classify every unresolved claim as `Repair Required`, `Manual USER Validation Required`, `USER Waiver Required`, or `Blocked`.
USER Decision Required: Required to waive independent proof, accept manual validation as the final evidence layer, approve a deliberate UI/vision exception, or expand helper/validator implementation.
Validation Owner: Future helper/validator hardening should extend branch governance validation, branch-readiness fixture validation, USER review bundle validation, visual/live-validation helpers, and source-owner checks where machine-checkable. Green validation is evidence only; Codex must still review the actual claim/evidence relationship.
Final Disposition: Phase advancement, UTS handoff, PR Readiness, and release-facing closeout are invalid when a material claim is circularly proven, unadjudicated, or supported only by the artifact that made the claim.

### Vision-To-Proof Matrix Gate

Rule Name: `Vision-To-Proof Matrix Gate`
Owner: `Docs/phase_governance.md` for Live Validation gates, proof requirements, blockers, and comparative-proof disposition; `Docs/branch_plans/README.md` for BP2/BP3 proof-plan fields; `Docs/user_test_summary_guidance.md` for USER validation and UTS interpretation; `Docs/validation_helper_registry.md` for future helper/validator guidance.
Applies To: BP2, BP3, Workstream, Hardening, Live Validation, UTS handoff, PR Readiness proof review, USER packets, helper output, validator output, and Codex closeout claims when a branch creates or changes runtime behavior, user-facing behavior, UI/UX, workflow, failure/recovery behavior, security/privacy boundaries, helper/validator behavior, source-truth ownership, or any claim that must be proven against accepted vision or branch proof contracts.
Required State: The branch must maintain a `Vision-To-Proof Matrix` for material claims before Live Validation green or UTS handoff. Each row must name `Requirement / Claim ID:`, `Accepted Vision Source:`, `Accepted Requirement:`, `Claim Class:`, `Minimum Proof Strength:`, `Implementation Evidence:`, `Observed Runtime Evidence:`, `Comparison Evidence:`, `Reference Surface / Baseline:`, `Evidence Class:`, `Known Limitation:`, `Codex Adjudication:`, `USER Validation Need:`, and `Final Verdict:`. Hardening must review the matrix for missing, weak, circular, stale, or unobservable proof before Live Validation handoff.
Allowed Values:

- `PASS`
- `REPAIR`
- `BLOCKED`
- `UNPROVEN`
- `WAIVED_WITH_REASON`
- `Manual USER Validation Required`
- `Not Applicable With Reason`

Invalid Values:

- `Helper Green`
- `Marker Green`
- `Screenshot Exists`
- `Video Exists`
- `Manifest Exists`
- `Log Exists`
- `Implemented Therefore Proven`
- `Plan Says It`
- `Looks Fine`
- `No Reference Surface Needed`
- `USER Can Check Later`
- `Hardening Did Not Inspect`

Blocking Conditions: `Vision-To-Proof Matrix Missing`, `Accepted Requirement Missing`, `Observed Runtime Comparison Missing`, `Reference Surface Missing`, `Hardening Proof Gap Not Routed`, `Evidence Input Treated As Comparison`, `Screenshot Or Video Not Adjudicated`, `Runtime Log Treated As Visual Proof`, `Helper Output Treated As Runtime Observation`, `Subjective UX Claim Not USER-Routed`, `Vision-To-Proof Verdict Missing`, and `Live Validation Comparative Proof Missing`.
Repair Owner: The current branch/worktree repairs branch-local implementation or proof gaps; Hardening owns pre-Live-Validation proof-gap discovery for the current branch; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable rule drift; helper/validator owners repair confirmed tool false-green/false-red behavior; USER owns manual validation, waivers, and subjective acceptance.
Repair Path: List every material accepted requirement, map it to the claim/evidence class from the Evidence Independence gate, gather implementation evidence, gather runtime or visual evidence through the legal launcher/path, compare the observed evidence to the accepted vision and reference surfaces, adjudicate each row, route any `REPAIR` or `BLOCKED` row back to Workstream or Hardening, and route any objectively unprovable or subjective row to USER manual validation or explicit waiver before UTS/PR green.
USER Decision Required: Required to waive the matrix, accept subjective/manual validation as the final evidence layer, accept a reference-surface exception, approve a deliberate product/vision mismatch, or allow Live Validation to proceed with a known unproven material claim.
Validation Owner: Future helper/validator hardening should extend branch governance validation, branch-readiness fixture validation, USER review bundle validation, visual/live-validation helpers, source-owner checks, and family-specific runtime validators where machine-checkable. Green validation remains evidence only; Codex must still inspect the actual matrix and evidence relationship.
Final Disposition: Live Validation, UTS handoff, PR Readiness, and release-facing closeout are invalid while a material matrix row is missing, unadjudicated, overclaimed, unsupported by observed runtime/comparison evidence, or left for USER discovery without explicit manual-validation routing.

### Visual Acceptance Target Gate

Rule Name: `Visual Acceptance Target Gate`
Owner: `Docs/phase_governance.md` for phase law, render authority levels, blockers, and implementation-gate disposition; `Docs/branch_plans/README.md` for BP1/BP2/BP3 and active branch-plan field shape; `Docs/nexus_vision.md`, `Docs/family_visions/FAM-002_desktop_interface.md`, applicable Family Vision / Family Feature Vision files, and `Docs/ui_reference_catalog/` for visual contract inputs; `Docs/validation_helper_registry.md` for helper/validator guidance; active external branch plans for branch-local decisions and USER-selected targets.
Applies To: any material visible UI/UX change before runtime implementation, including windows, child windows, existing controls, layouts, copy, buttons, status rows, settings, dialogs, cards, panels, workflows, visual states, density, spacing, footprint, visual-system adoption, or new/changed visual interaction surfaces. Non-visible implementation, text-only docs, non-material typo repair, or invisible backend work may mark the gate `Not Applicable With Reason`.
Required State: Before runtime implementation begins for a material visible UI/UX change, the branch must create or reference a rendered and reviewable `Visual Acceptance Target` path. The target path must be substantial enough for USER, ChatGPT, and Codex review of scale, monitor footprint, spacing, density, hierarchy, visual rhythm, copy, states, controls, hit areas, resize behavior, relation to surrounding UI, relation to accepted reference surfaces, and source-truth conflicts. The branch must not proceed from visual idea to runtime UI code on vague prose, helper green, a single attractive screenshot, or a local-only mockup that USER cannot review.

Visual Acceptance Chain: `Vision Contract -> UIREF / Accepted Reference Set -> Visual Acceptance Target -> Implementation Match Proof -> Pre-Live Visual Purpose Conformance -> Live Validation -> UTS / PR`. Visual Acceptance is the USER-facing proof seam that Codex got the visual/product direction right; Live Validation then proves that the accepted surface works through the required runtime/user path. Packet reviewability, clean ZIP proof, helper output, validator output, source-truth citations, CSS markers, screenshot existence, or Codex narrative are evidence inputs only. They do not become `USER Visual Acceptance`, `Implementation Match Proof PASS`, `Pre-Live Visual Purpose Conformance PASS`, UTS acceptance, or PR Readiness unless the branch records the required comparison rows, evidence class, and USER decision or waiver.

Visual Acceptance applies across BP2/BP3, Workstream, Hardening, Live Validation, RAR, UTS handoff, and PR Readiness when material visible UI is in scope. BP2/BP3 must not approve Workstream when the visual target, accepted reference set, implementation authority classification, state coverage, functionality role contract, and implementation-match proof plan are missing. Workstream must not implement a material visible surface by inference from UIREF, FAM-002, screenshots, or a future template/shared primitive. Hardening and Live Validation must compare actual implementation screenshots/video against the accepted target and accepted reference set before functional proof can clear. PR Readiness must treat unresolved visual-family drift, missing implementation-match proof, or repeated same-class visual repair as a blocker, issue candidate, `Reference Standard Repair Candidate`, `Template Gap`, `Shared Primitive Gap`, `Reference Gap`, or source-truth repair candidate.
Render Authority Levels:

- `Concept Render`: brainstorming or exploration only; not source truth and not an implementation target unless USER explicitly promotes it through the gate.
- `Design Candidate Render`: USER-selection evidence; substantial enough to compare options, critique direction, and decide what should become the target.
- `Visual Acceptance Target`: USER-accepted or USER-revised branch visual contract for the current visible UI/UX change.
- `Implementation Match Proof`: actual implementation screenshot/video or ordered frames proving the runtime UI matches the accepted target after code changes.

Required Visual Target Packet Contents, when USER choice or review is needed:

- multiple design candidates when direction is unresolved
- focused renders
- full desktop/context renders
- actual state renders or state contact sheets for relevant states
- element legends with stable element IDs
- visual selection ledger or template
- draft Visual Acceptance Target
- rejected-pattern ledger
- reusable design recipe/template when useful
- source-truth conflict classification
- UDL / false-green integration where applicable
- validation outputs and packet hygiene proof

Required State Coverage: Visible controls and surfaces must cover relevant states before implementation unless marked `Not Applicable With Reason` with source-truth basis. Relevant states include default, hover, focus, pressed/clicked, disabled/blocked, empty/no-data, loading, error/recovery, active/inactive, open/closed, selected/unselected, resize/default geometry, and any branch-specific state that changes visible behavior.

Required Visual Family Relation Proof Table: `| Surface / Window | Role Classification | Implementation Authority | Accepted Reference | Element Group | Invariant Traits | Feature-Specific Traits | Rendered Evidence | Visual Match | Functional Match | Verdict | Next Legal Action |`.

Required Implementation Authority Table: `| Surface / Window | Approved Template? | Approved Shared Primitive? | Promoted Reference Consumed? | Reference-Derived? | One-Off? | Gap / Exception | Proof Required |`.

Required Functionality Role Contract Table: `| Window / Surface | Product Role | Parent / Launch Source | Primary Actions | Secondary Actions | Non-Goals | Backend / State Owner | UI-Visible Truth Mapping | Recovery / Failure Behavior | Separate Surface Justification |`.

Required Visual Acceptance Chain Table: `| Gate | Required Visual Proof | What Cannot Prove It | Blocking Condition | USER Decision Needed? |`.

Implementation Authority Classification: material visible UI must be classified as exactly one of `Shared Primitive Consumed`, `Implementation Template Instantiated`, `Reference-Derived Implementation`, `One-Off Implementation`, `USER-Approved Exception`, `Reference Gap`, `Template Gap`, `Shared Primitive Gap`, or `Source-Truth Gap`. `One-Off Implementation` is legal only as a disclosed current-branch implementation posture; it is not a standard, template, primitive, or future reuse authority. A branch that claims `Shared Primitive Consumed` or `Implementation Template Instantiated` must name the approved primitive/template source path and consumer contract. If no approved template or primitive exists, the branch must use `Reference-Derived Implementation`, `One-Off Implementation`, or a gap/exception value and prove row-by-row parity against the accepted reference set before green.

Functionality Role Contract: new, detached, child, modal, dashboard, diagnostics, settings, doorway, recovery, or status surfaces must state their product role, parent or launch source, primary and secondary actions, non-goals, backend/state owner, UI-visible truth mapping, recovery/failure behavior, and separate-surface justification before visual acceptance or implementation-match proof can pass. Role-ambiguous surfaces block on `Functionality Role Contract Missing` or `Role-Ambiguous Surface Unrouted`.
Allowed Values:

- `Not Applicable With Reason`
- `Concept Only`
- `Design Candidates Reviewable`
- `USER_ACCEPTED Visual Acceptance Target`
- `USER_REVISED Visual Acceptance Target`
- `USER_WAIVED Visual Acceptance Target`
- `Implementation Match Proof Pending`
- `Implementation Match Proof PASS`
- `Implementation Match Proof REPAIR`
- `Blocked`

Invalid Values:

- `Looks Better`
- `Looks Close`
- `Looks Good Enough`
- `Validator Green Therefore Target Accepted`
- `Concept Render Treated As Target`
- `Screenshot Exists Therefore Target Accepted`
- `Implementation First`
- `USER Can Fix Later`
- `Reference Cited But Not Compared`
- `Template Exists By Inference`
- `No State Coverage Needed`
- `Packet Path Only`

Blocking Conditions: `Visual Acceptance Target Missing`, `Visual Acceptance Target Not Reviewable`, `Concept Render Misclassified As Target`, `Design Candidate Media Missing`, `Visual Target State Coverage Missing`, `Visual Selection Ledger Missing`, `Rejected Pattern Ledger Missing`, `Render Authority Level Missing`, `Implementation Started Before Visual Acceptance`, `Implementation Match Proof Missing`, `Implementation Match Proof Not Compared`, `Source-Truth Visual Conflict Unclassified`, `Vague Visual Acceptance Language`, `Visual Target Packet Hygiene Missing`, and `Visual Target USER Decision Missing`.
Additional blocking conditions: `Visual Family Relation Proof Missing`, `Implementation Authority Classification Missing`, `Accepted Reference Set Missing`, `Accepted Reference Not Compared`, `Reference-Derived Parity Unproven`, `Template Claim Unsupported`, `Shared Primitive Claim Unsupported`, `One-Off Implementation Overclaimed`, `Functionality Role Contract Missing`, `Role-Ambiguous Surface Unrouted`, `Packet Reviewability Treated As Product Acceptance`, `Screenshot Path Treated As Visual Acceptance`, `Helper Green Treated As Visual Acceptance`, `CSS Similarity Treated As Visual Family Proof`, `Implementation-First Visual Target Backfill`, and `Pre-Live Visual Purpose Conformance Missing`.
Repair Owner: The current branch/worktree owns branch-local visual targets and implementation-match proof for its approved visible UI/UX change. The explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy owns reusable rule drift, UIREF/template/shared-primitive promotion, and program-wide helper/validator implementation. USER owns target selection, revision, waiver, and deliberate exception approval.
Repair Path: classify whether the change is material and visible, load the applied Project Vision, Family Vision, Family Feature Vision, Branch Vision, UIREF/reference/template/shared-primitive inputs, create reviewable rendered candidates or a target and deliver selected current evidence through the external USER lifecycle owner when USER review is needed, record conflicts and rejected patterns, obtain USER acceptance/revision/waiver before runtime implementation, then after implementation gather actual screenshot/video proof and compare it against the accepted target before H1/LV/UTS/PR claims.
USER Decision Required: Required to accept, revise, reject, waive, or request more options for a Visual Acceptance Target; required to approve a deliberate mismatch, source-truth conflict disposition, missing-state exception, target bypass, or program-wide template/shared-primitive promotion.
Validation Owner: Future helper/validator coverage should extend branch governance validation, branch-readiness fixture validation, USER review bundle validation, UI/RAR visual proof helpers, and source-owner checks where machine-checkable. Green validation remains evidence only; Codex must still inspect the rendered target, packet media, source-truth conflicts, and USER decision state.
Final Disposition: Runtime UI implementation, renewed H1, Live Validation, UTS handoff, PR Readiness, and release-facing closeout are invalid when a material visible UI/UX change lacks a USER-accepted, USER-revised, or USER-waived Visual Acceptance Target, or when implementation-match proof is missing after code changes.

### Scope Coverage Manifest Gate

Rule Name: `Scope Coverage Manifest Gate`
Owner: `Docs/phase_governance.md` for phase gates, blockers, success-claim proof, and broad/multi-issue decomposition; `Docs/branch_plans/README.md` for BP2/BP3 and active branch-plan field shape; `Docs/family_visions/FAM-002_desktop_interface.md` for reusable UI component anatomy; `Docs/validation_helper_registry.md` for future helper/validator guidance; `Docs/incident_patterns.md` for recurring failure preservation.
Applies To: BR1, BR2, BP1, BP2, BP3, Workstream, Hardening, Live Validation, UTS handoff, PR Readiness, Release Readiness, USER packets, helper output, validator output, Codex closeout claims, and Codex repair claims whenever Codex claims `green`, `complete`, `LV passed`, `PR-ready`, `accepted`, `no drift`, `all fixed`, `everything checked`, or an equivalent full-scope success result.
Required State: A success claim is valid only when the owning phase output includes or references a `Scope Coverage Manifest` for the relevant scope. The manifest must name what was included, what was excluded, what was sampled, what was read directly, what was searched only, what evidence was independently reviewed, which human-judgment areas remain, and the disposition for every relevant file class, surface, claim, defect target, visual element, or element group. A broad or multi-issue USER complaint must be decomposed into atomic repair targets before Codex reports completion.
Required Manifest Fields:

- `Coverage Objective:`
- `Phase / Gate:`
- `Source-Truth Owners Loaded:`
- `Inventory Roots:`
- `File Classes Included:`
- `File Classes Excluded:`
- `Runtime / UI Surfaces Included:`
- `Claims Inventoried:`
- `Visual Elements Or Element Groups Inventoried:`
- `Files Read Directly:`
- `Files Searched Only:`
- `Files Not Read With Reason:`
- `Validators Run:`
- `Helpers Run:`
- `Independent Proof Reviewed:`
- `Photo / Video Evidence Reviewed:`
- `USER Packet Evidence Reviewed:`
- `Human-Judgment Areas:`
- `Known Blind Spots:`
- `Sampling Used:`
- `If Sampling Used, Why:`
- `Coverage Disposition:`

Allowed Coverage Dispositions:

- `Checked`
- `Not Applicable`
- `Deferred With Reason`
- `Repair Required`
- `USER Review Required`
- `Blocked`

Broad / Multi-Issue Decomposition Rule: When USER reports a defect set using broad or quantity-expanding wording such as `all`, `every`, `whole window`, `all text`, `all buttons`, `all dropdowns`, `10 issues`, `multiple issues`, `everything in this window`, or equivalent wording, Codex must classify the complaint as `Single Item`, `Multi Item`, `Broad Class`, `Vague Class`, or `All Surface`. For `Multi Item`, `Broad Class`, `Vague Class`, or `All Surface`, Codex must create an atomic repair ledger that restates the USER complaint, lists every known target, identifies the owning surface/file/code path, expected fix, proof method, and disposition, repairs or blocks each target, reruns the relevant proof for each target, and reports every target as fixed, deferred with reason, blocked, waived, or USER-review-needed. A sample repair cannot be reported as full-class repair unless the manifest records why sampling is sufficient and which remaining items were checked or explicitly deferred.
Quantity-Insensitive Repair Reliability Rule: Codex must treat one defect and many defects with the same closure discipline. If one named text mismatch would require direct proof after repair, ten text mismatches require ten target rows or a justified complete-class scan that proves all ten and the surrounding class. Partial repair followed by a full-scope success claim is invalid.
Element-Group UI Acceptance Rule: For desktop/user-facing UI, the manifest must inventory material user-facing element groups rather than decorative atoms only. Acceptance-critical element groups include any group that affects user action, comprehension, immersion, safety, proof, state, navigation, failure, recovery, or trust. Examples include window chrome, close/minimize/back/settings affordances, primary/secondary/danger buttons, dropdowns and option lists, scrollable rows, cards, dividers/page breaks, status fields, empty/error/degraded/blocked states, confirmation dialogs, dirty guards, tray/menu entries, and proof-visible evidence surfaces. Each applicable element group must have a reference surface or accepted grammar, focused screenshot/video or manual-validation route when visible, and a `PASS`, `REPAIR`, `STOP`, `WAIVED_WITH_REASON`, `USER Review Required`, or `Not Applicable With Reason` verdict.
No-Vague-Final-Acceptance Rule: Vague final verdicts such as `looks good`, `seems fine`, `appears okay`, `validator passed`, `screenshot exists`, `matches style generally`, `NDAI-ish`, `probably fixed`, or `no obvious issue` are not final acceptance. They may appear only as informal observations followed by mapped evidence, coverage disposition, and the exact claim or element group they support. If mapped evidence is missing, the result is `Repair Required`, `USER Review Required`, or `Blocked`.
Active-Ledger Placement Boundary: Durable source truth owns the rule and required fields. Active coverage rows, defect ledgers, per-element visual inventories, photo/video manifests, current branch proof, and current USER packet evidence belong in the active external branch plan, USER review packet, helper output, validator output, Codex digest, evidence root, or approved transition packet until PR Readiness fold-down decides what durable receipt should remain. Repo backlog, roadmap, branch-record index, Main, and Family/Family Feature Vision files must not become live coverage ledgers.
Invalid Values:

- `Complete Without Coverage Manifest`
- `All Fixed Without Target Ledger`
- `Broad Complaint Sampled Without Justification`
- `Validator Green Accepted Without Coverage Review`
- `Generated Artifact Not Checked`
- `Human Judgment Not Elevated`
- `Sampling By Convenience`
- `Looks Good As Final Verdict`
- `Screenshot Exists Therefore Accepted`
- `One Item Fixed Therefore All Fixed`

Blocking Conditions: `Completeness Claim Without Coverage Manifest`, `Relevant File Class Not Inventoried`, `USER-Facing Surface Not Inventoried`, `Visual Element Coverage Missing`, `Element Group Coverage Missing`, `Accepted Vision Claim Not Mapped To Proof`, `Validator Green Accepted Without Coverage Review`, `Generated Artifact Not Checked`, `Human-Judgment Surface Not Elevated`, `Coverage Exclusion Not Justified`, `Sampling Used Without Justification`, `Broad Request Decomposition Missing`, `Multi-Issue Repair Ledger Missing`, `Quantity-Sensitive Repair Drift`, `Partial Repair Reported Complete`, `All-Claim Coverage Missing`, and `Unverified Defect Target`.
Repair Owner: The current branch/worktree repairs branch-local coverage, UI, proof, and defect-target gaps; the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy repairs reusable rule drift; helper/validator owners repair confirmed false-green/false-red tooling; USER owns manual validation, waivers, and subjective acceptance.
Repair Path: Build or repair the manifest, decompose broad claims into atomic targets, inventory every relevant file class/surface/claim/element group, record exclusions and sampling rationale, gather independent proof, rerun proof for every repaired target, adjudicate each target, route any `REPAIR` or `BLOCKED` target back to the owning phase, and route human-judgment areas to USER review or waiver before any full-scope success claim.
USER Decision Required: Required to waive coverage, accept sampling for an all-surface claim, accept manual validation as final evidence, approve a deliberate UI/vision exception, or expand helper/validator/template implementation.
Validation Owner: Future helper/validator hardening should extend existing governance validation, branch-readiness fixture validation, USER review bundle validation, live-validation helpers, source-owner checks, and family-specific validators where machine-checkable. Green validation remains evidence only; Codex must still inspect the manifest and evidence relationship before claiming complete.
Final Disposition: Phase advancement, UTS handoff, PR Readiness, Release Readiness, or any final closeout is invalid when a material coverage scope is missing, sampled without justification, overclaimed, unadjudicated, or reported with vague acceptance language instead of mapped evidence and disposition.

### Branch / Slice / SLC / Seam Terminology Model

Rule Name: `Branch / Slice / SLC / Seam Terminology Model`
Owner: `Docs/phase_governance.md`
Applies To: Branch Readiness, Branch Planning, Workstream, active external branch plans, backlog/workstream package trace, local USER hub planning packets, helper output, validator output, fixtures, and historical receipts that use SLC identifiers.
Branch Definition: A branch is the coherent implementation carrier admitted through Branch Readiness. It must carry one selected implementation route, one owning branch/worktree authority, and one bounded package objective. A branch is not a planning loop, a placeholder for choosing future branches, or a container for unrelated family/package work.
Slice Definition: `Slice` is the canonical package deliverable unit. A slice is a traceable deliverable area inside one admitted package under one FAM; it must name the concrete deliverable, FAM/package relationship, admission posture, completion state, and seam trace when it is active or folded down.
SLC Classification: `SLC` is the current branch-planning alias for a Slice-level implementation line item or historical slice ID. It is not a separate backlog identity, not a seam, and not automatic branch-split authority. Current BP2/BP3 packets may keep labels such as `SLC / Seam Plan:` and historical IDs such as `SLC-051` for traceability, but their meaning must resolve to Slice-level deliverable trace. New source truth should prefer `Slice` when naming canonical package deliverables and may include `SLC` only as an alias or historical trace label.
Seam Definition: `Seam` is the execution or validation checkpoint inside or between slices. A seam is the current bounded checkpoint Codex executes and validates; it cannot replace the slice deliverable, cannot become the branch identity, and cannot authorize stopping while the slice or package remains incomplete.
Relationship Rule: BP1 may mention slices/SLCs/seams only as later implementation staging, because BP1 is the vision gate. BP2 maps the accepted or waived BP1 route into Slice/SLC deliverables, seam sequence, files, validators, proof, rollback, risks, and USER gates. BP3 verifies the BP2 slice/seam map against BP1 and returns Workstream entry approval only for the admitted same-branch package. Workstream executes one active seam at a time and keeps moving through the accepted slice chain until Workstream Green, a real blocker, future dependency, or explicit USER waiver is recorded.
Multi-Slice Branch Rule: Multi-slice branches are legal when the slices share one FAM, one package objective, one selected implementation route, one owner/worktree, aligned release/PR timing, and a validation/proof path that can cover the grouped scope. A branch should split when family ownership, package objective, implementation route, private/runtime/provider action gate, release timing, validation path, risk class, or ownership diverges enough that one bounded Workstream package would blur authority or weaken proof.
Terminology Drift Blockers: `SLC / Slice / Seam Ambiguity`, `SLC Treated As Seam`, `SLC Treated As Separate Branch`, `Slice Treated As Proof Artifact`, `Seam Treated As Branch Deliverable`, and `Multi-Slice Package Shape Unproven`.
Validation Preference: Machine-checkable packets and fixtures must reject ambiguous SLC/Slice/Seam language, fake feature labels, proof/setup/boundary labels posing as implementation, planning-only lane setup, first-seam-only Workstream entry, and multi-slice packages that omit shared FAM/package/route/owner/validation evidence.

### Branch Planning Review Gate State Model

Rule Name: `Branch Planning Review Gate State Model`
Owner: `Docs/phase_governance.md`
Applies To: BP1 USER Branch Vision Review, BP2 USER Branch Plan Review, BP3 Workstream Entry / Orchestration Validation, local USER hub packets, branch planning digests, branch records, branch plans, helper output, and validator output.
Required State: Branch Planning gate evidence must track two independent axes: `Packet Reviewability State` and `USER Gate State`.
Allowed Values:

- `Packet Reviewability State`: `Missing`, `Generated`, `Validation Failed`, `Reviewable`, `Stale`, `Superseded`
- `USER Gate State`: `Pending USER Review`, `USER Revision Requested`, `USER Accepted`, `USER Approved`, `USER Waived`, `USER Rejected`, `USER Blocked`, `Superseded`

Invalid Values: `Implementation-ready`, `validated`, `green`, `generated`, `reviewable`, helper `PASS`, validator `PASS`, Codex agreement, ChatGPT agreement, or packet file-count proof must not be used as USER acceptance, USER waiver, USER approval, or Workstream implementation authority.
Blocking Condition: `Packet Validation Treated As USER Acceptance`, `Review Gate Bypass`, `USER Review Packet Phase-State Conflict`, `USER Review Packet Not Digested`, `Branch Planning Acceptance Receipt Missing`, `Helper False Green On Review Gate State`, or `Codex Digest Conflicts With USER Packet` blocks progression whenever the two axes conflict or when Codex asks for a later gate without accepted/waived prior USER gate proof.
Repair Owner: The current branch/worktree owner repairs branch-local review packets; reusable failures route to the explicitly USER-approved source owner/carrier selected by the Source Truth Authority Hierarchy and update `Docs/phase_governance.md`, `Docs/branch_plans/README.md`, `Docs/validation_helper_registry.md`, and helper/fixture owners when machine-checkable.
Repair Path: regenerate or repair the USER packet until `Packet Reviewability State: Reviewable`, return the packet to USER, digest the USER response, record the receipt, then set `USER Gate State` to the legal USER disposition. Chat-only correction text cannot replace the packet receipt.
USER Decision Required: Required for `USER Accepted`, `USER Approved`, `USER Waived`, `USER Rejected`, and any revision closure that changes branch vision, branch plan, Workstream orchestration, scope, or implementation authority.
Validation Owner: the external USER lifecycle owner governs current review delivery; `dev/orin_branch_governance_validation.py` and `dev/orin_branch_readiness_planning_fixture_validation.py` retain public product-contract and false-green regression coverage. Review completeness and validation output are evidence, not USER acceptance.
Final Disposition: A Branch Planning gate exits only through a recorded USER disposition or a named blocker. A `Reviewable` packet starts USER review; it does not complete USER review.

Transition Rule:

- BP1.1 prepares and repairs `USER_BRANCH_VISION_REVIEW.md` until `Packet Reviewability State: Reviewable`.
- BP1.2 is the USER Branch Vision Review Gate with `USER Gate State: Pending USER Review` until USER responds.
- BP1.3 records `USER Accepted`, `USER Waived`, `USER Rejected`, `USER Revision Requested`, or `USER Blocked` before BP2 preparation.
- BP2.1 prepares and repairs `USER_BRANCH_PLAN_REVIEW.md` only after BP1 is `USER Accepted` or `USER Waived`.
- BP2.2 is the USER Branch Plan Review Gate with `USER Gate State: Pending USER Review` until USER responds.
- BP2.3 records `USER Accepted`, `USER Waived`, `USER Rejected`, `USER Revision Requested`, or `USER Blocked` before BP3 preparation.
- BP3.1 prepares and repairs Workstream Entry / Orchestration Validation only after BP1 and BP2 are `USER Accepted` or `USER Waived`.
- BP3.2 is the USER Workstream Entry / Orchestration Review Gate with `USER Gate State: Pending USER Review` until USER responds.
- BP3.3 records `USER Approved`, `USER Waived`, `USER Revision Requested`, or `USER Blocked` before first Workstream implementation approval may be requested.
- Workstream implementation remains blocked until BP1 is `USER Accepted` or `USER Waived`, BP2 is `USER Accepted` or `USER Waived`, BP3 is `USER Approved` or `USER Waived`, and USER separately approves bounded Workstream implementation for the admitted same-branch package or explicitly named initial seam sequence.

## Cross-Phase Rules

- repo canon is the detailed authority
- prompt and instruction layers should mirror the same exact phase names rather than aliases
- repository workstream and branch owners retain product phase/proof contracts and durable receipts; the matching external operational record exclusively owns current phase/status and execution state
- backlog, roadmap, repository receipts and prompts may point to current phase state but must not provide a competing current value or override the external operational owner or repository product contracts
- a phase must never be inferred from user intent alone
- material changes to product validation/timeout/harness contracts require the approved repository owner update; changes to active seam, blockers or current operational scope update the matching external record. Reconcile both against USER authorization before continued execution is recommended
- auxiliary guidance docs should be timeless by default and must not quietly become current-state owners

## Governed Output State Contract

At a material boundary, report actual effects, affected evidence, approval scope, unresolved blockers and the next admitted action. Continue useful same-phase work under its actual approval. A marker count, single-slice waiver, continuation latch or per-seam diary cannot authorize effects or demand a new approval. Honor explicit USER stops and requested full digests. Required phase/human results remain separate.

One coherent seam or slice can complete an admitted objective. No single-seam or single-slice waiver is required. Remaining useful same-phase work continues under its actual approval; a count or continuation marker cannot enlarge scope or require invented work.


`User Test Summary Results Pending` is not a Workstream stop condition.
Workstream may plan manual user acceptance and may prepare later UTS strategy content, but formal UTS export, returned-result digestion, and the `User Test Summary Results Pending` blocker belong to `Live Validation Stage 1`.
User Test Summary is exclusive to Live Validation Stage 1.
Live Validation Stage 1 cannot enter Stage 2 until User Test Summary results are `PASS` or `WAIVED`, Codex has digested the result into source truth, and blockers have been reevaluated.
PR Readiness may verify the previously digested Live Validation UTS state, but it must not create, refresh, or digest UTS as its own phase artifact.
If user-facing implementation is not product-complete, Workstream must continue implementation, internal sandbox validation, and branch-local proof instead of asking the USER to complete a UTS as the Workstream completion gate.

## Canonical Governance Rules

### Source-Of-Truth Enforcement

- `Docs/phase_governance.md` is the repo-wide authority for exact phase names, blocker rules, proof governance, timeout governance, seam governance, stop-loss rules, branch classes, the Governance Drift Audit, and the phase resolver contract
- workstream docs must consume this model rather than redefining repo-wide process rules locally
- workstream docs may record branch-local validation contracts, tighter time budgets, active seams, artifact references, and explicit waivers, but those narrower contracts must be explicit

### Source-Truth Placement Preflight

Before Codex creates a new governance/source-truth file, active artifact, ledger, registry, or durable authority surface, it must perform a `Source-Truth Placement Preflight`.

The preflight must report:

- existing authority owner for the concept
- whether the change extends an existing owner or needs a new artifact
- why workstream docs, branch records, backlog, roadmap, validation helper registry, family dossiers, Element Coverage, or phase governance are insufficient if a new artifact is recommended
- whether a new artifact would duplicate, conflict with, or bypass an existing owner
- validator updates needed to prevent placement drift

Default rule: extend the existing owner first. A new active source-truth file requires a clear `No Existing Owner Fits` finding or an explicit companion-file pointer from the owning workstream doc or branch authority record.

When the proposed concept touches backlog identity, family vision, architecture, cross-family policy, experience design, runtime subsystem behavior, capability-pack domains, AI-native planning, or AI operational cache behavior, the preflight must also run the `Backlog Taxonomy And Source-Truth Placement Gate` from `Docs/feature_backlog.md`. The packet must classify the concept as exactly one or more of `Backlog family`, `Family vision`, `Architecture layer`, `Cross-family policy owner`, `Experience layer`, `Runtime subsystem`, `Capability-pack domain`, or `Package/slice/seam`; name rejected owner classes; name existing owner files to extend first; and state whether USER approval is required for any new backlog family or new source-truth owner. Missing or ambiguous classification blocks on `Backlog Taxonomy Gate Missing`; creating a new FAM without explicit USER approval remains blocked on `Backlog Addition User Approval Missing`.

AI Operational Cache Governance must not be promoted as a new FAM by inertia. Cache is not memory: cache is operational, purpose-bound, explainable, clearable, and policy-governed, while memory is durable user-personal knowledge and requires separate explicit consent. Cross-family cache architecture, replay safety, provenance, invalidation, Trust Journal cache events, and policy placement route through `Docs/ai_runtime_and_trust_architecture.md`; family-specific cache placement routes through existing FAM-007 AI/runtime/capability-pack owners, FAM-008 setup/install/cache-root UX owners, the relevant implementing family vision for local data/privacy implications, and the active external branch planning owner for implementation-specific cache behavior. Any further new AI architecture or policy owner is legal only after the placement preflight records `No Existing Owner Fits` or USER approves a companion source-truth file.

### Codex Plugin / Connector Use Boundary

`Docs/governance_efficiency_operating_model.md` owns the `Codex Plugin / Connector Evidence Split Compatibility Contract`. Phase governance consumes that contract as a phase-gate boundary.

Codex app plugins and connectors may support any phase only as evidence tools inside the existing phase machine. They do not create a new phase, bypass Branch Readiness / Branch Planning / Workstream / Hardening / Live Validation / PR Readiness / Release Readiness, waive USER gates, authorize implementation, or clear blockers by themselves.

Before Codex relies on a plugin or connector for phase advancement, PR readiness, release readiness, source-truth repair, provider/API setup, private/public boundary work, or governed review evidence, the phase packet must include `Plugin / Connector Use Plan:` with tool, use case, phase/stage, authority class, read/write mode, mutation risk, privacy/secret risk, expected evidence, evidence owner, fallback, USER approval requirement, and repo persistence.

`Plugin / Connector Use Plan Missing`, `Plugin Evidence Treated As Source Truth`, `Plugin Live-State Ledger In Repo`, `Sensitive Connector Setup In Repo`, and `External Plugin Evidence Schema Premature` block phase advancement when applicable.

GitHub connector PR facts remain Git/GitHub/helper-derived live truth. OpenAI Docs lookups are evidence for durable rule review. OpenAI Developers/API key/provider setup is sensitive setup state and remains blocked unless USER approves that exact setup path. Browser, Chrome, Computer Use, Documents, Spreadsheets, and Presentations outputs are review or validation evidence until digested into an owning source-truth file or historical receipt.

### Architecture / Experience / Policy Impact Matrix

Branch Readiness Stage 1 and Branch Planning packets for product, runtime, UI, provider, cache, AI-native, capability-pack, privacy, trust, or source-truth ownership work must include an `Architecture / Experience / Policy Impact Matrix`.

The matrix must classify each touched or plausibly affected owner class as one of:

- `Architecture Layer`
- `Experience Layer`
- `Cross-Family Policy Owner`
- `Runtime Subsystem`
- `Capability-Pack Domain`
- `Family Vision`
- `Package/slice/seam`
- `No Impact`

Allowed impact values are `No Impact`, `Consume Existing`, `Extend Existing`, `Change Existing`, `New Candidate`, and `USER Decision Required`.

The packet must name the existing owner file, current-branch scope, deferred/future scope, rejected owner classes, and proof or validation needed. A `New Candidate` impact is illegal until `Source-Truth Placement Preflight` proves `No Existing Owner Fits` or USER explicitly approves a new owner. Missing or ambiguous matrix rows block on `Architecture Impact Unclassified`, `Experience Layer Impact Unclassified`, `Cross-Family Policy Impact Unclassified`, or `New Owner Candidate Without Placement Preflight`.

`Element Ledger Placement Drift` blocks Stage 2 completion when Codex adds or recommends a new active source-truth artifact without this preflight, when a new artifact duplicates an existing owner, or when the owning record does not point to a large companion ledger file.

### Element Validation Ledger

The `Element Validation Ledger` is the row-level proof ledger for product-significant elements created, touched, affected, deferred, preserved as future, classified as dependency-only, or kept as non-gating supporting evidence.

The ledger is canonical only inside the existing authority owner:

- Promoted workstream: canonical workstream doc.
- Registry-only active branch: matching external branch state; repository receipts are durable or historical, not an active-authority exception.
- Large active ledger: external branch state, optional companion file with canonical pointer from the owning workstream doc, or transition-approved branch authority receipt.
- Family dossier: aggregate or historical trace only.
- Feature backlog: identity and registry only.
- Roadmap: stage-breakpoint schedule outline and broad milestone checkpoints only.
- Validation helper registry: helper inventory only.
- Element Coverage: non-identity checklist only.

Every active ledger row should identify the element ID, element name, category, parent surface, primary interface, classification, user-facing status, visibility, expected behavior, functional requirement, regression risk, affected source surfaces, source-owner marker or source-owner-not-applicable reason, validation required, Workstream proof, Hardening proof, Live Validation proof, UTS question or waiver, phase owner, current status, open issues, and notes.

Element Validation Ledger status values should use this vocabulary unless an owning record explicitly defines a narrower branch-local set: `Planned`, `Implemented Pending Proof`, `Workstream-Proven`, `Hardening-Proven`, `LV1 Handoff`, `USER Accepted`, `Blocked`, `Deferred`, `Future`, `Dependency-Only Supporting`, and `Non-Gating Supporting`.

Each seam must run an `Element Delta Capture` for product/runtime/UI/source-truth changes. New or changed UI, window behavior, focus/click-through, clipping/z-order, movement/drag/resize, copy/content, telemetry truth, provider states, persistence, validation artifacts, screenshots, UTS questions, lifecycle behavior, and source-truth boundaries must either update an existing ledger row or add a new one.

Marker-only proof cannot satisfy user-facing element acceptance. User-facing and hidden-user-facing ledger rows require screenshot/live proof and Live Validation / UTS coverage unless an explicit waiver is recorded. Deferred, future, dependency-only, and non-gating supporting rows must name their boundary so they neither block nor falsely satisfy the current release.

The active external branch planning owner must carry an `Element-to-Phase Proof Matrix` before Workstream implementation begins or resumes when a branch plans, creates, touches, affects, defers, or preserves user-facing, runtime, UI, provider, validation/helper, source-truth, or workflow elements. The matrix is a USER-reviewable pre-implementation bridge from element coverage to Workstream implementation, Workstream proof, Hardening proof, Live Validation proof or waiver, UTS / USER acceptance, future/deferred boundaries, USER decision state, and source owner / ledger owner. It extends the Element Validation Ledger model and does not create a global ledger or live-state owner. Matrix status markers must use the allowed values in `Docs/branch_plans/README.md`, owner markers must name concrete source-truth owners, external operational-state owners, or repo-relative historical receipt paths, and Element IDs must be unique inside the matrix.

Branch Readiness Stage 2 and Branch Planning must produce or admit the matrix before Workstream implementation. Workstream seam closeout updates matrix rows with implemented, skipped, deferred, or future-gated status. Hardening compares actual implementation against the matrix. Live Validation compares observed behavior, user-facing proof, UTS posture, and waiver posture against the matrix. PR Readiness folds durable matrix outcomes into the branch record, workstream doc, family dossier, or Element Validation Ledger owner.

Branch Planning Review Bundle: Before USER can green-light Workstream implementation for a runtime/user-facing/source-truth branch, Codex must complete BP1, BP2, and BP3 and prepare the full current Branch Planning review content for delivery through the external USER lifecycle owner to the approved collection and evidence set. The review must contain exactly one primary USER-facing decision file for the current BP gate, required supporting digests/checklists, and the Project Vision, Family Vision, Branch Vision, Branch Plan, Element-to-Phase Proof Matrix owner, branch authority record, relevant UFD/change-intent surfaces when applicable, and any other source-truth context needed for USER inspection. The digest must identify the current review location, selected context file list, user-readable check/proof summary without live validation-status metadata, exact planning or implementation decision requested, and pending USER decisions. A pending review requires current selected-evidence delivery proof from the external owner, one primary current-gate review file, and no stale-stage text or unresolved placeholders. Completed review gates use retained review evidence and the acceptance/waiver disposition; they do not require a retired ZIP. Active branch status, current HEAD/origin/main, ahead/behind, validation log detail, current PR state, and ZIP hash belong in helper output, validator output, Codex chat digest, or external operational state rather than as the content focus of USER-facing review files. Missing review packet proof blocks on `Branch Planning Review Packet Missing`; stale current-selection or delivery proof blocks on `USER Review Packet Stale`.

BP1 USER Branch Vision Review Gate: BP1 must wrap Project Vision Context, Family Vision Context, Feature Vision Context, selected implementation route, Codex understanding, Branch Goal, End-State Vision, what USER will actually see and where, how it will function, user experience flow, Surface Map, product options/design paths, Codex recommendations with USER response space, Nexus-fit rationale, USER design questions, USER response, Codex digest, Accepted Branch Vision, family-vision versus branch-only impact, must-have behavior, must-not-do/regression-risk rules, deferred and future-gated ideas, Vision Question Queue, Design Assumption Ledger, Contract Status, Contract Revision, and acceptance/revision/rejection/waiver decision area into `USER_BRANCH_VISION_REVIEW.md`. BP1 must define the vision for the BR2-selected implementation route; it must not turn planning, setup, or later branch selection into the branch vision. BP1 becomes green only when USER accepts the Branch Vision or explicitly waives BP1.

BP2 USER Branch Plan Review Gate: BP2 must wrap the accepted or waived BP1 result, selected implementation route, implementation package summary, branch scope size test, SLC/seam plan, affected surfaces, likely files, validators/helpers, proof requirements, Element-to-Phase Proof Matrix, H1 expectations, LV/UTS expectations, rollback/safety plan, open engineering risks, future-gated boundaries, line-item USER plan review list, plan acceptance checklist, Contract Status, and exact BP3 approval text into `USER_BRANCH_PLAN_REVIEW.md`. `Draft`, `Pending USER Response`, `Pending Codex Digest`, and `Pending USER Confirmation` Contract Status values block implementation until USER confirms or waives the final plan. BP2 asks whether the implementation plan correctly builds the accepted BP1 vision. BP2 cannot green an infrastructure-only or orchestration-only route; when setup groundwork is required before implementation, BP2 must name the exact USER action gate, blocked scope, rollback/safety posture, and route disposition. BP2 routes back to BP1 if the engineering plan exposes a vision gap or changes the accepted Branch Vision. BP2 becomes green only when USER accepts the Branch Plan or explicitly waives BP2.

BP3 Workstream Entry / Orchestration Validation Gate: BP3 loads accepted or waived BP1 and BP2 outputs and proves the branch plan matches the accepted branch vision, the package is the largest safe feature-focused implementation package, SLCs are an engineering route inside one branch rather than automatic separate branches, affected files and validators are ready, Hardening and Live Validation proof paths are planned, rollback is understood, the selected implementation route remains concrete, and future-gated boundaries are preserved. BP3 may return bounded Workstream implementation approval for the admitted same-branch package, naming the entry seam or initial seam sequence, only when BP1 and BP2 are accepted or explicitly waived and BP3 validation is green. BP3 cannot convert continued planning, lane setup, or a future branch selection exercise into Workstream approval. Implementation remains blocked on `BP1 Branch Vision Review Missing`, `BP2 Branch Plan Review Missing`, `BP3 Orchestration Validation Missing`, `Implementation-Bearing Route Missing`, `USER Review Packet Stale`, or `USER Review Packet Not Digested` until these gates are green or waived.

USER Branch Planning review reinforcement: BP1 / `USER_BRANCH_VISION_REVIEW.md` owns product/design direction, end-state vision, user-facing behavior, surfaces, options, Codex recommendations, USER response, Codex digest, accepted Branch Vision, deferred/future-gated ideas, and decision state. BP2 / `USER_BRANCH_PLAN_REVIEW.md` owns the engineering plan derived from accepted or waived BP1: accepted Branch Vision summary, implementation package summary, branch scope size test, SLC/seam plan, affected surfaces, likely files, validators/helpers, proof requirements, Element-to-Phase Proof Matrix, H1 expectations, LV/UTS expectations, rollback/safety plan, open engineering risks, future-gated boundaries, line-item USER plan review, plan acceptance checklist, and exact BP3 approval text when ready. BP2 may retain readable context such as surface map, implementation options, and recommended direction, but its primary decision surface is whether the engineering plan correctly builds the accepted BP1 vision. If BP2 changes product direction, user-facing behavior, surfaces, scope, or future-gated boundaries, it must route back to BP1 before implementation approval.

Branch Planning packet acceptance requires more than identity and file count. The active packet must self-validate required BP1/BP2/BP3 file presence, exact USER decision text, and next-legal-phase consistency across the selected primary review, navigation, and applicable supporting BP digests/checklists (including `USER_REVIEW_FOLDER_AND_FILE_DIGEST.md`, `WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md`, and `BRANCH_VISION_VALIDATION_CHECKLIST.md` when present). Active branch status, current source HEAD, current `origin/main`, current PR state, and validation log proof belong in helper output, validator output, external operational state, or Codex chat digest instead of becoming the content focus of USER-facing review files. If packet files disagree about whether the next legal phase is BP1 review, BP2 review, BP3 orchestration validation, Workstream implementation approval, or repair/revalidation, entry blocks on `Branch Planning Packet Decision Path Conflict`. A packet that names Branch Readiness Stage 2 repair/revalidation, or otherwise states that Workstream implementation remains blocked, cannot be used as Workstream implementation approval until the local USER hub packet is reissued or updated and the decision path validates inside the packet itself. Chat-only correction text cannot replace missing packet evidence.

Workstream Entry Whole-Package Analysis Gate: for any runtime-focused branch with multiple admitted slices or seams, Workstream Entry analysis must inspect and report on the entire admitted Workstream package before recommending the entry implementation seam. The packet must include all admitted slices/seams, completion strategy, entry-seam recommendation, seam dependency map, future-gated boundaries, preservation surfaces, validation plan, Hardening H1 expectations, Live Validation LV1 expectations, visual/user-facing proof requirements, UTS handoff criteria, and exact implementation approval text that preserves bounded continuation until Workstream Green, a real blocker, or an explicit USER waiver. A first-seam-only analysis is insufficient and blocks Workstream entry on `Workstream Entry Whole-Package Analysis Missing`. This gate plans Hardening and Live Validation obligations but does not authorize executing those phases; executing Workstream implementation, Hardening, Live Validation, UTS handoff, PR creation, merge, or release work still requires the separately legal phase approval.

Source-code ownership markers are optional backlinks from code to the canonical ledger, not the ledger itself. High-risk elements such as window ownership, drag/move behavior, focus/click-through, clipping/z-order, provider truth, warning behavior, scrollbar/product styling, persistence, proof generation, UTS generation, major UI sections, renderer boundaries, state transitions, and lifecycle/cleanup behavior should carry a source-owner marker or a source-owner-not-applicable reason. Existing source files may adopt this marker format gradually through a later repo-wide marker adoption branch/package.

Dev Toolkit Interface Review Mode is the repo-wide standard dev-only inspection path for USER-facing interface elements once that tooling is admitted. Existing and future USER-facing interface elements, including NCP, Core visualization, Dashboard, Overlay/display when admitted, and other windows/components, should record a Dev Toolkit review disposition in the owning Element Validation Ledger: callable in Dev Toolkit Interface Review Mode, deferred to a named repo-wide adoption branch/package, or not-applicable with reason. The mode is tabled for a planning-heavy Dev Toolkit branch/package and may choose per-interface launchers, a generalized dev-version launch where all eligible surfaces run in review mode, or both. The mode must use dev-only launch surfaces with element badges, hover highlighting, ledger ID/name tooltips, and screenshot-friendly annotations. Production UI must not expose element numbers, and Dev Toolkit review evidence cannot replace Live Validation, screenshot proof, or returned User Test Summary acceptance.

Element ledger blockers include `Element Validation Ledger Missing`, `Element-to-Phase Proof Matrix Missing`, `Element-to-Phase Proof Path Missing`, `Workstream Entry Review Bundle Missing`, `USER Branch Plan Review Missing`, `Workstream Entry Whole-Package Analysis Missing`, `Created Element Untracked`, `Touched Element Proof Missing`, `Affected Element Validation Missing`, `User-Facing Element Acceptance Missing`, `Deferred Element Boundary Missing`, `Element Proof Stale`, `Marker-Only Element Proof`, `Element Ledger Placement Drift`, `Feature Element Source Marker Orphaned`, `High-Risk Element Source Owner Missing`, `Feature Element Marker Proof Insufficient`, `Feature Element Source Marker Stale`, and `Feature Element Source Marker Mismatch`.

### ChatGPT Interface And Codex Execution Authority Rule

ChatGPT, prompt generators, and loader templates are interface layers.
They may package task context, request source-of-truth loading, and describe requested task boundaries for Codex to validate against canon.
They are not execution authority.

ChatGPT-authored prompt additions are analysis and review surfaces. They may add evidence checks, validation reminders, review questions, source-truth checks, and candidate blocker findings for Codex to reconcile against loaded repo governance, but they must not become a second governing authority by removing, replacing, narrowing, reordering, or prohibiting canon-required Codex steps through prompt-layer wording. When ChatGPT finds a flaw, stale assumption, missing step, unsafe scope, governance mismatch, blocker risk, source-truth drift, validation gap, or approval gap, it must frame the concern as an analysis finding, candidate blocker, evidence gap, or USER decision needed; USER approval is required before Codex treats that finding as a source-truth change, approved-plan change, scope widening, waiver, or new FAM/package admission.

Codex execution follows live Git/GitHub truth, repository product contracts routed below, the matching external operational owner for current task/phase state, and the explicit USER authorization for permitted effects:

- `Docs/Main.md`
- `Docs/development_rules.md`
- `Docs/phase_governance.md`
- `Docs/codex_modes.md`
- `Docs/feature_backlog.md` for tracked identity and `Record State`
- `Docs/workstreams/index.md` and the relevant workstream doc for promoted product contracts and durable proof, with the matching external record for current operational authority
- any directly relevant owning canon document for the task

`Docs/nexus_startup_contract.md` owns loader prompt shape only.
It does not own execution behavior, phase transitions, seam continuation, durability, validation, release rules, or branch authority.
Local ChatGPT custom instructions should stay compact, while the repo loader/source-truth may hold longer ChatGPT-facing continuity rules and review memory.
Do not paste the loader doc into Codex prompts. Codex prompts should load `Docs/Main.md` and owning canon for execution authority, and use the loader only when prompt generation, new-chat bootstrapping, or loader/source-truth drift review is in scope.
Loader continuity points to the current owning contracts. It preserves actual phase, ownership, approval and human-result boundaries without copying package-size vetoes or requiring their prose to recur in prompts.

Agent-generated prompts and summaries do not create authority. An explicit USER decision may approve an in-scope source reform and change its validation plan; reconcile that decision in the owning candidate source. Withheld push, phase entry, live mutation, deletion, publication, and release actions remain withheld.
If prompt text conflicts with owning canon, Codex must follow canon, report the conflict, and either continue inside the canon-legal boundary or stop on the canon blocker.

### Single Phase Authority Rule

For promoted, `Registry-only` and approved non-backlog work alike, the matching external operational record is the single owner of live `Current Phase`, `Phase Status`, current blockers, task/write owner, branch/worktree assignment, locks/leases and current next operational action.

Repository phase, workstream and branch owners retain canonical phase names, product phase definitions, branch-class meaning, entry/exit requirements, acceptance/proof contracts, and durable accepted milestone or historical/fold-down receipts. `Entry Basis`, `Exit Criteria` and `Rollback Target` remain required product contracts with applicable current evidence verified against the external owner and live Git truth. Named phase fields in repository records are explicitly historical/accepted snapshots or product contracts; they are not a second live operational value.

`Workstream Phase Authority Missing` blocks execution when the matching external current owner or its required live phase information is missing. Report the exact gap rather than manufacturing a repository current-state record. Product proof and USER acceptance requirements remain in force.

### Branch Authority Record Rule

Repository branch records preserve durable branch identity, product/interface intent, and historical receipts. Current phase, blockers, owner, write scope, locks, and next action belong to the matching external operational record. A historical repository receipt does not need a new live Stage-2 admission merely to serve as input to an explicitly authorized sandbox reform.

Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.

A repository-owned product or interface defect is repaired on a legally assigned repository carrier, preserving protected main and USER changes. An operational Governance defect is repaired on the approved external source carrier and reviewed before activation. A new carrier requires the current USER authorization and identity/collision checks, not a fabricated product implementation route.

A discovered gap requires a test or review only for the material failure it can cause. Do not mandate a new validator, helper, or prompt rule solely because an earlier gate missed a wording or historical-evidence defect.

### Protected Main Law

`main` is protected for Codex work.

Allowed on `main`:

- read-only truth validation
- release review
- merge verification
- post-release verification

Forbidden on `main`:

- editing repository files
- staging files
- committing files
- generating or refreshing source, docs, canon, validator, helper, release-note, or handoff artifacts
- direct canon repair

There is no emergency direct-main repair path for Codex.
Any tracked file mutation while Codex is on `main` is a `Main Write Attempt` blocker.
If drift is discovered before merge, return to the owning branch and repair it before PR green.
Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.

Current phase, blockers, locks, and assigned write scope are owned by the matching external operational record. Repository branch records are durable product/interface receipts or explicitly historical evidence.
Merge-stable pointer surfaces such as backlog and roadmap must not mirror transient task ownership. Retained historical records are not active branch authority merely because they remain present.


### Repo-Level Admission Gate

Before product implementation starts, verify the assigned repository/worktree, current baseline, approved product scope, preservation of USER changes, and the material entry conditions of the product phase. An unresolved defect blocks only the operation whose safety, correctness, authorization, or acceptance it materially affects.

Unrelated historical cleanup debt, old receipt wording, generated-report presence, and retired Governance checks do not block a new product carrier. Operational Governance repair remains external under the ownership contract; it is not added to the runtime branch to satisfy admission.

Protected main remains read-only. Existing USER changes, branch commits, and stash contents remain protected. New branches, live authority, remote actions, and release execution require their own admitted scope.

### Pre-PR Durability Rule

Commit validated changes on the current legal carrier when the USER has approved commits. Preserve each existing commit and USER change unless the current authorization explicitly admits changing it.

Local commit is not push authority. Push, PR creation or mutation, merge, release, USER publication, and live activation each require current explicit authorization. A source rule or generated continuation marker cannot override a USER instruction withholding those actions.

Within an admitted workload, continue useful in-scope repair and validation without asking again for already granted authority. Handoff occurs at the approved review boundary or a genuine material blocker. Product phase protections and standard product tests remain applicable.

### Blocker Catalog

The default named blockers are:

- `Prompt Phase Missing`
- `Prompt Phase Mismatch`
- `Workstream Phase Authority Missing`
- `Branch Base Invalid`
- `Merged Canon Drift`
- `Stale Canon`
- `Phase Exit Unmet`
- `Next Workstream Undefined`
- `Successor Lock Missing`
- `Post-Merge State Unresolved`
- `Dirty Branch`
- `Docs Sync Incomplete`
- `Release Debt`
- `Release Target Undefined`
- `Release Readiness File Mutation Attempt`
- `User-Facing Shortcut Validation Pending`
- `User Test Summary Results Pending`
- `PR Creation Pending`
- `PR Validation Pending`
- `PR State Unknown`
- `PR Readiness Execution User Approval Missing`
- `PR Merge Status Unproven`
- `Merge-Target Authority Projection Unproven`
- `PR Merge Verification Pending`
- `PR Watcher Provisioning Unproven`
- `PR Watcher Routing Unverified`
- `PR Readiness Scope Missed`
- `Release Window Audit Incomplete`
- `Release Readiness Scope Drift`
- `Prior Branch Canon Unresolved`
- `Between-Branch Canon Repair Attempt`
- `Main Write Attempt`
- `Next Branch Created Too Early`
- `Governance Drift`
- `Current-State Claim Drift`
- `Phase Waiver Missing`
- `Planning-Loop Guardrail`
- `Backlog Completion Unproven`
- `Backlog Addition User Approval Missing`
- `Backlog Exhaustion User Decision Pending`
- `Package Completion Unproven`
- `Exact USER Desktop Launcher Proof Missing`
- `Launcher Parity Proof Missing`
- `Photo Or Video Proof Missing`
- `Unphotographable Proof Not Elevated To USER`
- `Direct Runtime Proof Misclassified`
- `Troubleshooting Consent Missing`
- `Live Validation Evidence Packet Incomplete`
- `User-Visible Internal Path Leakage`

Blockers stop progression immediately and must be reported before any later-phase recommendation.

### Planning and execution continuity

An accepted plan and actual USER approval govern their objective until superseded, completed, or blocked by material scope, owner, protected risk or phase change. Carry accepted planning and the affected delta. Documentation, source governance, installation and runtime work are implementation when admitted. No docs-only bypass, planning-loop marker or fresh approval is needed merely because work continues. Plans and helper results never substitute for implementation or actual results.


Runtime Branch Engineering Contract:

- runtime-focused implementation branches must carry `## Runtime Branch Engineering Contract` beside the Product Definition Plan before Workstream begins or any later phase resumes
- the contract must translate USER-reviewed product intent into engineering intent with `USER Engineering Planning Review:`, `Runtime Implementation Approval:`, `Current Runtime Baseline:`, `Planned Runtime Delta:`, `User-Facing Runtime Delta:`, `State / Config / Schema Delta:`, `Validator / Helper Delta:`, `Expected Changed Files / Surfaces:`, `Approval-Boundary Audit:`, `Future-Gated Items:`, `Workstream Seam Map:`, `Proof Expectations:`, `Risk Forecast:`, `Recommendations And Alternatives:`, `Plan Version / Revision Status:`, and `Plan-To-Implementation Traceability:`
- Branch Readiness Stage 1 proposes the contract and stops for USER planning review; Branch Readiness Stage 2 may admit or revise it, but `Runtime Implementation Approval:` remains pending until Workstream is separately approved
- Workstream seam start/closeout, Workstream Green, Hardening, Live Validation, PR Readiness, and Release Readiness must compare actual deltas, visible behavior, validator/helper proof, skipped items, and public release scope against the admitted contract
- if implementation discovers the contract is too narrow, stale, or wrong, Codex must stop with a plan revision packet that names the current approved plan, discovered repo truth, proposed revision, affected seams, approval-boundary impact, and exact USER decision needed

Branch Runtime Engineering Plan:

- new or re-entering runtime-focused branches must create or admit the detailed active-branch execution plan under `D:\Nexus Desktop AI\Governance State\branches\<branch_slug>\branch_plan.md` during Branch Readiness Stage 2 when repo truth supports runtime work
- the branch authority record must remain the control surface and must include `Branch Runtime Engineering Plan:`, `Branch Runtime Engineering Plan Path:`, and `Engineering Plan Status:` when the plan is required, present, accepted, revised, folded, or historical
- backlog and roadmap remain compact pointer/status surfaces; detailed runtime baseline, planned delta, per-seam checklist, validation checklist, user-facing proof checklist, future-gated ledger, approval-boundary audit, and plan-to-implementation traceability belong in the Branch Runtime Engineering Plan or folded historical record
- Branch Readiness Stage 2 and Workstream Entry must admit a USER-reviewable `Element-to-Phase Proof Matrix` in the active external branch planning owner when the branch plans, creates, touches, affects, defers, or preserves product/runtime/UI/source-truth/helper/workflow elements; each current planned/created/touched/affected element must name Workstream implementation, Workstream proof, Hardening proof, Live Validation proof or waiver, UTS / USER acceptance, USER decision state, and source owner / ledger owner before Workstream begins or resumes
- BP1/BP2/BP3 Branch Planning must include a full non-compacted Branch Planning / Workstream Entry Review Digest and exactly one primary current-gate USER decision file, supporting digests/checklists, and the required project vision, family vision, branch vision, branch plan, branch authority, matrix, UFD/change-intent, and source-truth context before USER can green-light implementation. Deliver the selected current review evidence through the external USER lifecycle owner to the approved collection and evidence set.
- BP1 must include the named `USER Branch Vision Review Gate`; BP2 must include the named `USER Branch Plan Review Gate`; BP3 must include `Workstream Entry / Orchestration Validation` for runtime/user-facing/source-truth work. The review packet summarizes the accepted branch vision, planned user-facing outcome, implementation plan, Element-to-Phase Proof Matrix summary, Hardening plan, Live Validation / UTS plan, open USER questions, Codex recommendations, implementation options, alternatives/tradeoffs, accepted/deferred/rejected scope, exact USER decision needed, `USER Review Response:`, `Codex Response Digest:`, and `USER Review Packet Finding:`. The finding must prove the local USER hub packet was loaded and digested or name the exact waiver/blocker. Workstream implementation stays blocked on `BP1 Branch Vision Review Missing`, `BP2 Branch Plan Review Missing`, `BP3 Orchestration Validation Missing`, `USER Review Packet Stale`, or `USER Review Packet Not Digested` until BP1/BP2 are accepted or waived and BP3 is green.
- Workstream Entry reads the plan and returns whole-package analysis before entry-seam implementation, each seam updates traceability, Hardening compares actual implementation against it, Live Validation records proof or waiver posture, PR Readiness produces the `PR Fold-Down Packet:`, and Release Readiness translates the plan into public scope without internal governance jargon
- a missing or shallow Branch Runtime Engineering Plan keeps runtime implementation blocked on Branch Readiness planning until USER accepts, revises, or explicitly waives the plan boundary

USER Feedback Disposition:

- meaningful USER feedback during Branch Readiness, Workstream, Hardening, Live Validation, or PR Readiness must be classified through `USER Feedback Disposition` when it affects branch scope, accepted vision, user-facing behavior, runtime behavior, validation proof, future work, reusable product standards, approval boundaries, or a USER decision
- the active external branch planning owner owns full UFD detail while the branch is active; branch records, repo branch-plan receipts, backlog, roadmap, Nexus Vision, family vision, workstream docs, and family dossiers may carry compact pointers or folded outcomes only when they are the correct owner for the final disposition
- UFD ledger markers include `USER Feedback Disposition Required:`, `UFD Ledger Status:`, `UFD Ledger Owner:`, `Open UFD Count:`, `Blocking UFD Count:`, and `Fold-Down Status:`
- each meaningful feedback item uses a repeatable `### UFD Item: UFD-<scope>-YYYYMMDD-NNN` block with `Feedback ID:`, `Feedback Summary:`, `Feedback Source:`, `Feedback Phase:`, `Disposition Type:`, `USER Decision State:`, `Owner Class:`, `Canonical Owner File:`, `Workstream Severity:`, `Status:`, `Fold-Down Target:`, and `Pointer Locations:`
- Codex may recommend UFD disposition, owner, severity, and no-action posture, but USER decision controls accepted branch scope; Codex and ChatGPT recommendations remain proposed until USER accepts, revises, rejects, defers, waives, or supersedes them
- pointer locations may carry only UFD ID, short title, canonical owner, compact status, and fold-down status; full feedback text, full decision history, and live implementation state stay with the active external branch planning owner until PR Readiness fold-down
- `No Durable Owner Needed` is valid only when the item is closed as minor/no-action, duplicate, superseded, or non-actionable, with `No-Action Reason:` recorded in the active external branch planning owner or return digest
- UFD IDs use `UFD-<scope>-YYYYMMDD-NNN`; do not use `FBK-*` because it collides visually with historical `FB-###` workstream records

Vision Contract / Vision-to-Plan loop:

- runtime/user-facing branches must not silently convert Codex or ChatGPT design recommendations into implementation truth
- Nexus Vision owns project-wide product principles; optional family vision or family dossier sections own broad feature-family direction only when the family is large enough; USER-approved Family Feature Vision records under `Docs/family_feature_visions/` own detailed feature-category direction and Deferred Feature Carryforward inside one FAM; the active external branch planning owner owns the Branch Vision Contract Snapshot for branch-specific accepted vision
- `Vision Contract Required:` is `Yes` for user-facing UI/UX behavior changes, runtime behavior changes, workflow hierarchy changes, visual standard changes, setup/activation behavior changes, provider/model/memory/voice/Core behavior, returned UTS that changes target behavior, broad family planning, ambiguous acceptance criteria, conflicting prior source truth, or any Codex recommendation that would otherwise become product/design truth
- `Vision Contract Required:` may be `No` only for mechanical docs-only repair, validator-only repair with no product/runtime/user-facing impact, release-body formatting repair, source-truth typo/format repair, or branch metadata repair, and the reason must be recorded
- valid design assumption states are `Proposed by Codex`, `Recommended by ChatGPT`, `Accepted by USER`, `Revised by USER`, `Rejected by USER`, `Deferred by USER`, `Deferred With Waiver`, `Superseded`, and `Needs USER Decision`; only `Accepted by USER`, `Revised by USER`, or `Deferred With Waiver` are implementation-safe for product/runtime/user-facing behavior
- before Workstream implementation, a required Branch Vision Contract Snapshot must record `Branch Vision Snapshot Status: Accepted`, `Open Vision Questions: None` or `Deferred With Waiver`, `USER Vision Green: Yes`, accepted implementation scope, accepted seam map, accepted stop conditions, a design assumption ledger, a vision question queue, and vision-to-implementation traceability
- after USER Vision Green, Codex should preserve the accepted plan during implementation; new Level 1 non-blocking questions are queued, Level 2 seam-blocking questions pause only the affected seam and require a Vision Question Digest, and Level 3 workstream-breaking questions require a Branch Plan Revision Packet before affected scope continues
- accepted assumptions expire or require review when branch scope changes, returned UTS changes the accepted target, family vision changes, source truth contradicts prior assumptions, new user-facing behavior appears, or implementation would apply an old decision to a new family/surface
- Hardening compares implementation against accepted vision and accepted branch plan; Live Validation compares observed user-facing behavior against accepted vision and accepted branch plan; PR Readiness folds reusable vision updates into Nexus Vision, family vision/family dossier, workstream docs, structured branch receipts, or validated historical receipts without creating permanent branch-specific vision-file sprawl
- Vision Question Digest must include question, why it matters, affected branch/seam, current accepted vision, Codex recommendation, alternatives, risk of each option, whether work can continue without the answer, recommended USER decision, and exact USER decision needed
- Branch Plan Revision Packet must include current accepted plan, discovered issue, why current plan is insufficient, proposed revision, affected seams, files/surfaces affected, validation impact, current Workstream versus future branch routing, Codex recommendation, and exact USER decision needed

Vision Update Decision Matrix:

| Input or update type | Active owner while unresolved or branch-local | Durable owner when USER accepted | Update trigger |
| --- | --- | --- | --- |
| Branch-specific design, behavior, seam, or implementation detail | Active external branch plan Branch Vision Contract Snapshot, UFD item, question queue, or Branch Plan Revision Packet | Branch receipt, workstream doc, family dossier, or validated historical receipt only if PR Readiness fold-down finds durable value | Record during Branch Readiness or Workstream; fold down during PR Readiness |
| Reusable family-level product direction or design standard | Active external branch plan first, with family vision as alignment reference | `Docs/family_visions/FAM-XXX_*.md` or family dossier section | USER accepts the standard, it applies beyond one branch, and it avoids branch-local implementation detail |
| Detailed feature-category direction inside one FAM | Active external branch plan first, with Family Vision and existing Family Feature Vision as alignment references | `Docs/family_feature_visions/FAM-XXX_<feature_slug>.md` after USER-approved content-file creation | USER accepts the feature-category direction, it applies beyond one branch, and it is more detailed than Family Vision but not branch-local implementation detail |
| Durable deferred feature carryforward inside one FAM | Active external branch plan UFD/future-package queue while unresolved or branch-local | `Docs/family_feature_visions/FAM-XXX_<feature_slug>.md` Deferred Feature Carryforward section after USER-approved disposition | USER accepts or defers the item for future feature grouping, names the dependency trigger, and assigns durable disposition without live branch state |
| Project-wide or cross-family product principle, long-term standard, AI/privacy/execution direction, or foundational behavior | Active external branch plan or governance intake until USER acceptance and scope are clear | `Docs/nexus_vision.md` | USER accepts the standard and it affects multiple families or Nexus-wide principles |
| Proposed, uncertain, conflicting, or ChatGPT/Codex-recommended idea | Active external branch plan question queue, UFD item, assumption ledger, or Vision Question Digest | No durable owner until USER accepts, revises, defers with waiver, rejects, or supersedes it | USER decision or waiver is required before implementation-safe product/runtime/user-facing scope |
| Future feature/package idea outside current branch scope | Active external branch planning owner UFD/future-package queue while active | Backlog compact pointer, family dossier, or future branch plan only after accepted/deferred disposition | USER accepts future-work posture or PR Readiness assigns a named future owner |
| Mechanical docs-only, validator-only, release-body-format, typo/format, or branch-metadata repair with no product/runtime/user-facing impact | Current repair branch plan or return digest with `Vision Contract Required: No` reason | Relevant governance receipt only if the repair creates durable interpretation | Record the not-required reason; do not promote to Nexus or family vision |

Branch plan first. Family Feature Vision only when the update is durable feature-category direction or deferred carryforward inside one FAM and USER accepts or defers it to that owner. Family vision only when reusable and USER accepted at broad family level. Nexus Vision only when project-wide or cross-family. Proposed or unresolved ideas must not be promoted to durable vision owners by Codex inference.

Current execution records identify the approved deliverable, owner/scope, implemented delta, affected proof and real unresolved work. Accepted planning carries with relevant deltas. Old planning-loop bypass catalogs remain historical field formats rather than current admission requirements.


### Blocker Rule

Phase-sensitive work is blocked until the following are explicit and mutually consistent:

- exact current phase
- active workstream or equivalent authority record
- branch class when branch-sensitive execution is in scope
- validation contract when validation is in scope
- timeout contract when interactive validation is in scope
- current active seam when the branch is in governed recovery
- current blocker set

If live behavior and the documented timeout contract drift, execution is blocked until they are reconciled.

### Branch Class And Phase Waiver Rule

Every active branch must declare a `Branch Class`:

- `implementation`
- `docs/governance`
- `emergency canon repair`
- `release packaging`

The same six normal phases apply to all branch classes.
`docs/governance` remains a recognized historical branch class, but it is not an approved new-branch lane in the normal Nexus flow.
Phases may be waived only when:

- the waiver is explicit in the active workstream or branch authority record
- the reason is recorded
- the waiver does not weaken merge-target canon completeness, successor lock, or release-debt protections

Silent phase skipping is prohibited.

### Branch-Class Admission Rule

Branch admission is class-sensitive.

### Family-Scoped Branch Readiness Candidate Rule

When Branch Readiness is scoped to a specific feature family or assigned lane, candidate selection must stay inside that family or lane unless USER explicitly approves cross-family routing. Codex may inspect other families only for same-file overlap, dependency, conflict, pending-decision, or sequencing context. If no legal in-family carrier is selected or admissible, Codex must return `STOP / USER DECISION REQUIRED` with the exact in-family decision needed instead of selecting another family's branch.

`implementation`

- the full repo-level admission gate must pass before the branch may enter `Branch Readiness`
- the active promoted workstream doc is the default authority record
- repository product/interface refinements may ride their active product carrier only when explicitly in its approved scope; operational Governance source does not

`docs/governance`

- the old product-repository branch class is historical vocabulary, not a prohibition on an explicitly USER-approved external source-only Governance carrier
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.
- historical receipts grant no new branch creation, live authority, push, PR, merge, release, or cleanup authority
- no active product branch means no product implementation by inertia; main remains read-only


`release packaging`

- may begin from updated `main` when merged-unreleased implementation, release notes, tagging, or another release-facing packaging task is explicitly opened
- the branch must not widen into implementation work

`emergency canon repair`

- is preserved only as historical vocabulary
- is not a normal branch lane in the current Nexus flow
- does not authorize direct-main repair by Codex
- does not authorize new temporary blocker-clearing branch surfaces for future Nexus work
- it does not promote the associated workstream and does not satisfy or consume selected-next implementation-branch creation
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.

### Merge-Target Canon Completeness Gate

Rule:

- a branch is not `PR Readiness`-complete if merging it would leave `main` canon-stale

This gate is mandatory when a branch would:

- close a workstream
- become the latest released or merged-unreleased implementation milestone
- change the current rebaseline or closeout baseline
- change the current closeout-index pointer
- change backlog status, roadmap stage-breakpoint/checkpoint posture, or workstream-index release posture
- change `Docs/Main.md` routing for the current baseline

When this gate applies, the branch must already contain the required release-facing canon updates before PR creation is allowed:

- canonical workstream record closure or equivalent release-state update
- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/workstreams/index.md`
- `Docs/closeout_index.md`
- the new or updated closeout or rebaseline file when current baseline routing changed
- `Docs/Main.md` routing updates when the current baseline pointer changed
- `Docs/branch_records/index.md` plus any relevant branch authority record when the branch still relies on branch-record authority and would otherwise remain incorrectly active after merge

If any required merge-target canon update is missing, the branch remains blocked in `PR Readiness`.

### Exceptional Merged-Unreleased Release-Debt Owner Contract

Release debt is not a normal acceptable merge state. When an implementation branch would unavoidably merge unreleased product behavior beyond the latest public prerelease, PR Readiness Stage 1 must first record explicit USER approval for that exception, the named owner, the release target/floor semantics, Release Window Audit posture, and the real carrier plan. Selected-next truth is not part of the default release-debt exception; PR Readiness records it only when USER explicitly approves PR-time successor selection or already-encoded selected-next truth would merge as durable source truth. Only then may PR Readiness leave exact post-merge release-debt truth in canon before PR green.

After the External Operational State Store contract is implemented, release debt means durable public release truth is missing or wrong. Wrong tag/body/release notes, invalid or missing artifacts, missing durable public milestone summaries, and released capabilities absent from durable product history remain release debt. Stale repo-file active branch records, repo-file active branch plans, worktree slots, selected-next operational posture, PR watcher state, release-window operational state, and post-release closure status become `Repo Live-State Leakage` or `External Operational State Conflict`, not release debt. This reclassification does not take effect as a migration until the USER approves external-state implementation and validator transition.

Required machine-checkable fields:

- `Merged-Unreleased Release-Debt Owner:`
- `Repo State: No Active Branch`
- `Release Target:`
- `Release Floor:`
- `Version Rationale:`
- `Release Scope:`
- `Release Artifacts:`
- `Post-Release Truth:`

Conditional machine-checkable fields, required only when USER explicitly approved PR-time successor selection or already-encoded selected-next truth would merge as durable source truth:

- `Selected Next Workstream:`
- `Next-Branch Creation Gate:`

Required owner docs:

- `Docs/feature_backlog.md` names the workstream as merged-unreleased release debt, not active execution truth
- `Docs/prebeta_roadmap.md` names the current release-debt owner, release target, release scope, and release artifacts as durable pointers; it names selected-next and branch-creation gate truth only when USER explicitly approved PR-time successor selection or selected-next truth already exists
- `Docs/workstreams/index.md` moves the workstream from `Active` to `Merged / Release Debt Owners`
- the canonical workstream doc records the same merged-unreleased release-debt owner contract

Release Readiness consumes this inherited release truth only after PR Readiness Stage 1 made the exception explicit before PR creation.
Release Readiness may validate target, scope, artifacts, and post-release truth, but it must not create or repair those fields in repository files.

Release target correctness is semantic, not marker-only.
PR Readiness must derive the target from the latest public prerelease and the declared `Release Floor:` before green:

- `patch prerelease` increments only the patch number, for example `v1.4.0-prebeta` -> `v1.4.1-prebeta`
- `minor prerelease` increments the minor number and resets patch to zero, for example `v1.4.0-prebeta` -> `v1.5.0-prebeta`

Release floor ownership:

- `patch prerelease` is the default floor for bug fixes, UX polish, governance fixes, documentation/canon repair, architecture-only planning, admission contracts, validation-only work, and non-user-facing milestones that do not add executable product behavior.
- `minor prerelease` is allowed only when the release delivers a new executable, runtime, operator-facing, user-facing, or materially expanded product capability lane.
- Opening a future planning lane, writing architecture, defining vocabulary, or creating an admission contract is not enough by itself to justify `minor prerelease`.
- If a public tag has already been published with a larger bump than the corrected law would choose, do not rewrite the public tag; record the published tag as latest release truth, classify the mismatch as version-advancement drift, and harden future `Release Floor:` validation.

If the declared target, artifacts, or post-release truth do not match the semantic release floor, keep `Release Target Undefined` active and repair the mismatch in PR Readiness before Release Readiness.

Post-release closure is mandatory after release execution:

- once a public prerelease tag exists for a merged-unreleased release-debt owner, durable canon must move that workstream to Released / Closed
- `Docs/prebeta_roadmap.md` must advance latest public prerelease truth to the published tag
- `Docs/feature_backlog.md` must mark the owner `Record State: Closed` and `Status: Released`
- `Docs/workstreams/index.md` must remove the owner from `Merged / Release Debt Owners` and list it under `Closed`
- the canonical workstream doc must record `Latest Public Prerelease:`, `Release Title:`, released/closed state, and cleared release debt
- release execution and post-release canon closure are separate; post-release canon drift must land in remote source truth through the approved Branch Readiness carrier before implementation begins
- a local-only post-release closure commit is a blocker, not completed source truth
- protected-main branch rejection must route to the next approved Branch Readiness Stage 2 canon/governance repair carrier instead of direct-main mutation, standalone cleanup, or a default release-support branch
- post-release validation must compare published GitHub release/tag truth and release-body format against remote repo source truth
- runtime implementation remains blocked until release publication exists, post-release canon drift is explicitly recorded or repaired through the approved Branch Readiness carrier, and owning validation reports green
- when release-dependent source truth cannot exist until after publication, backlog and roadmap may record bounded transitional drift using `Post-Release Canon Closure Drift: Recorded`, `Published Release Pending Canon Closure: <tag>`, `Closure Repair Surface: Next Branch Readiness Stage 2`, `Closure Drift Scope: release-dependent fields only`, and `Implementation Entry: Blocked until closure repair validates green`
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.

### Successor Lane Lock Gate

Rule:

- Branch Readiness Stage 1 owns the normal next runtime implementation pipeline selection.
- Branch selection is rooted in project vision, family vision, branch vision, current completed work, and the next implementation need. It must not be selected by PR Readiness inertia, release-debt avoidance, old selected-next ledgers, or stale backlog/roadmap posture.
- PR Readiness does not require selected-next truth or a waiver by default. Its default job is to prove the current branch is merge-ready, merge-stable, and free of stale active operational state.
- PR Readiness validates selected-next truth only when USER explicitly approves PR-time successor selection or repo/external state already encodes a USER-approved successor selection.
- When no USER-approved selected-next truth exists, the next implementation carrier is selected later through Branch Readiness Stage 1 after the current PR merges and updated `main` / external operational state are revalidated.

Exception:

- If USER approval for a new or successor backlog identity is absent, Codex must not select, split, promote, or create a successor backlog identity by inertia.
- If selected-next truth already exists, PR Readiness must verify it is USER-approved, vision-aligned, merge-stable, not stale, and not a live operational ledger in repo docs.
- If selected-next truth is absent, that absence is not a PR Readiness blocker. The future branch decision moves to Branch Readiness Stage 1, where Codex must evaluate vision alignment, current work, dependency boundaries, family ownership, implementation need, package/slice shape, and USER questions before admitting any branch.

### Backlog Identity Admission Gate

Backlog IDs are major user-facing feature-family or major release/support lanes.
The live backlog-family namespace is broad `FAM-###`, starting at `FAM-001`; the current admitted registry ends at `FAM-008`, and the old `FB-###` namespace is historical-only and must not be reused for parseable backlog entries.

Canonical identity model:

- `FAM` is a broad long-lived product family.
- `Package` is a bulk branch/release package under exactly one FAM.
- `Slice` is a traceable deliverable area inside exactly one package.
- `Seam` is an execution or validation checkpoint.
- `PR` is merge/review evidence only.
- legacy global `FB` is historical trace only.

Branch scope standard:

- branches should carry one family package with multiple admitted slices by default
- packages must record `Package Completion State:`
- package slices must trace to exactly one FAM and exactly one package
- Workstream must continue through every admitted package slice before Hardening unless package state is truthfully `Complete`, `Released Baseline / Open`, `Blocked`, or `Deferred`
- one coherent admitted slice is valid; historical/future rows are evidence, not admitted work
- every admitted deliverable has concrete scope, identity, actual completion/proof and owner; preserve accepted deferrals

- `Package Completion State: Complete` is blocked while any admitted slice remains incomplete, and completing one admitted slice cannot authorize stopping while another admitted package slice remains incomplete

They are not default identities for:

- small single-seam runtime proofs
- governance repairs
- validation follow-through
- hotfixes
- blocker-clearing repair traces
- branch-readiness or PR-readiness closeout details

Codex must not create a new backlog item, split an existing backlog identity, admit a new package, create a new family branch, promote a new selected-next backlog identity, or encode successor selection without explicit USER approval in the prompt or source-of-truth.

When Codex believes a new backlog item, package admission, branch creation, backlog split, promotion, selected-next successor, or single-slice package waiver is needed but USER approval is absent, Codex must stop on `Backlog Addition User Approval Missing`.
The blocker output must include all FAM entries that are still not closed and all package/slice rows that are not complete, with:

- ID
- title
- Status
- Record State
- Priority
- Package ID
- Package Completion State
- Slice ID
- Slice Status
- Selection / Unblock, deferred-context, branch, and minimal-scope fields when present

If no backlog entries remain open, Codex must stop on `Backlog Exhaustion User Decision Pending` and wait for USER direction.

Small follow-through remains traceable to its existing family/objective. A single coherent deliverable is valid. A new backlog identity or actual branch/scope split still requires its applicable USER authority; do not invent either to satisfy a slice count.


Historical pass aliases, support/governance lanes, and old registry-only implemented IDs are trace rows, not selectable backlog items. Re-promoting one into a parseable backlog identity requires explicit USER approval and a recorded reason that family/workstream/branch traceability is insufficient.
Any approved new backlog identity must use the fresh broad FAM namespace, not `FB-###`.

When USER-approved successor selection already exists and PR Readiness is asked to preserve or validate that existing selected-next truth, this gate requires all of the following before PR creation is allowed:

- the next workstream identity is selected from current canon using open backlog `Priority` plus deferred-context readiness, not `Target Version`
- that workstream exists in `Docs/feature_backlog.md`
- that workstream is recorded in `Docs/prebeta_roadmap.md`
- that workstream has a canon-valid `Record State`
- that workstream is a real runtime `Feature Family` candidate
- that workstream has `Priority` defined
- if that workstream is deferred, the backlog entry records `Deferred Since:`, `Deferred Because:`, and `Selection / Unblock:`
- that workstream has minimal scope defined before PR green
- no branch has been created for that next workstream yet
- successor branch creation is deferred to `Branch Readiness` after the current branch merges and updated `main` is revalidated

`Target Version` is not a next-workstream selection field. Do not use it to rank, select, defer, or skip open backlog candidates. Release targets are assigned by release-floor and release-readiness governance when a release-bearing branch requires them. Closed, released, implemented, or release-debt entries may preserve `Target Version` as historical release evidence.

Machine-checkable canon markers:

- the selected backlog entry must include `Next Workstream: Selected`
- the selected backlog entry must include `Minimal Scope:`
- when USER-approved selected-next truth exists, the roadmap must include `## Selected Next Workstream`
- when USER-approved selected-next truth exists, the roadmap selected-next section must include the same workstream id, its `Record State`, `Minimal Scope:`, and truthful branch status such as `Branch: Not created` before branch creation or the active Branch Readiness branch name after creation

When post-merge `No Active Branch` handling applies, the branch must instead:

- make the post-merge `No Active Branch` state explicit in current-state canon
- name the blocking admission item explicitly
- keep selected-next truth absent by default unless USER explicitly approved PR-time successor selection or selected-next truth already exists
- avoid creating or executing the next implementation branch by inertia

Temporary `emergency canon repair` branches that are explicitly recorded as repair-only must not be treated as the selected-next implementation branch for this gate. Validator and canon checks should distinguish those repair branches from real successor implementation-branch creation.

If selected-next truth is present but not recorded in backlog and roadmap, lacks valid record state, or lacks minimal scope, the branch is blocked by `Next Workstream Undefined`.
If USER approval for new or successor backlog selection is absent, PR Readiness must not create selected-next truth. The next branch decision waits for Branch Readiness Stage 1.
Explicit PR-time successor-selection approval must be machine-recorded as `Successor Selection User Approval: Granted`; otherwise PR Readiness treats successor recommendations as non-binding planning context only.
When post-merge `No Active Branch` truth is merge-stable and no selected-next entry exists, PR Readiness may proceed without `Next Workstream User Waiver:` because the next runtime implementation pipeline belongs to the next Branch Readiness Stage 1 pass.
If a selected deferred workstream lacks deferred-context fields, the branch is blocked by `Deferred Selection Context Missing`.
If a successor branch is created before `Branch Readiness`, the branch is blocked by `Successor Lock Missing`.

### PR Readiness Hard Blocker Gates

PR Readiness must not report green while any pre-merge process blocker remains unresolved.

Hard blockers:

- canonical shorthand: `stale-canon`, `post-merge`, `dirty`, `docs-sync`, `next-workstream-if-selected`, `Backlog Addition User Approval Missing`, `Backlog Exhaustion User Decision Pending`, `Package Completion Unproven`, `PR Readiness Execution User Approval Missing`, `deferred-context`, `desktop-shortcut`, `uts-results`
- `Stale Canon`:
  current-state canon and merge-target canon must already reflect the branch's true state and the state that will be true after merge
- `Post-Merge State Unresolved`:
  post-merge truth must already be merge-stable for the current branch and must not leave stale active branch authority, live PR state, release-window ownership, or repo-ledger operational state. `No Active Branch` is allowed when no USER-approved successor selection exists; the next runtime implementation pipeline is then selected during Branch Readiness Stage 1.
- `Next Workstream Undefined`:
  If selected-next truth is already encoded or USER explicitly approves PR-time successor selection, PR Readiness cannot be green until that selected workstream exists in canon, is recorded in backlog and roadmap, has a valid record state, has minimal scope defined, and has no branch created yet. If selected-next truth is absent, this blocker does not apply.
- `Next Runtime Candidate Selection Pending`:
  Retired as a default PR Readiness blocker after the external-state/index-only reform. Use this only for inconsistent already-encoded selected-next truth or explicit USER-approved PR-time successor selection that cannot be made coherent. Normal next runtime candidate selection belongs to Branch Readiness Stage 1.
- `Backlog Addition User Approval Missing`:
  PR Readiness and Branch Readiness cannot add, split, promote, package-admit, branch-create, or select a backlog identity without explicit USER approval. When this blocker is active, Codex must output the still-not-closed FAM list plus every not-complete package/slice instead of creating selected-next truth.
- `Backlog Exhaustion User Decision Pending`:
  If the still-not-closed FAM plus not-complete package/slice list is empty and new work would require a new backlog identity, Codex must stop for USER direction instead of inventing the next lane.
- `Branch Readiness Execution User Approval Missing`:
  Branch Readiness Stage 1 - Analysis Gate is a no-work review pass. Branch Readiness cannot enter Branch Readiness Stage 2 - Execution Gate, mutate repository files, create a branch, admit a package, sync docs, create selected-next truth, prepare PR work, or perform release work until the Stage 1 packet is returned and explicit USER approval to enter Stage 2 is recorded.
- `Thread / Worktree Identity Mismatch`:
  Any phase, branch creation, worktree creation, commit, push, PR creation, release action, or GitHub Desktop handoff must stop when the active local folder, git root, branch, upstream, `HEAD`, `origin/main`, worktree role, runtime/process ownership, or GitHub Desktop binding does not match the requested thread/workstream. Codex must report the expected workspace, actual workspace, expected branch, actual branch, expected thread/workstream role, actual repo state, and safest next correction before continuing.

- `Package Completion Unproven`:
  Workstream cannot advance to Hardening until every admitted package slice is complete, deferred, blocked, or explicitly preserved as released-baseline/open package truth with `Package Completion State:` recorded. Package completion cannot be green while admitted slices remain incomplete.
- `Deferred Selection Context Missing`:
  PR Readiness cannot be green when the selected next workstream is deferred but lacks `Deferred Since:`, `Deferred Because:`, or `Selection / Unblock:` in the backlog entry
- `Dirty Branch`:
  PR Readiness cannot be green while the worktree is dirty, required docs changes are uncommitted, required canon exists only in the working tree, or branch truth is not durable in commit history
- `Docs Sync Incomplete`:
  docs sync, Governance Drift Audit, validator alignment, and any required post-merge state wording must be complete and mutually consistent
  merge-target pointer surfaces must be merge-stable: during explicitly USER-approved exceptional merged-unreleased release-handling windows, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and the canonical workstream `## Phase Status` block may describe only the durable evidence-pointer truth that will still be correct after merge
  merge-target branch-head hash assertions such as ``origin/main` is `<sha>`` or ``origin/main` remains at `<sha>`` are operator facts only and must not appear in merge-stable current-state owner sections
- `User-Facing Shortcut Validation Pending`:
  Live Validation and PR Readiness cannot be final-green for a relevant desktop user-facing workstream until the final Live Validation closeout has launched through the declared user-facing desktop shortcut or equivalent user entrypoint, recorded `User-Facing Shortcut Validation: PASS` or `User-Facing Shortcut Validation: WAIVED`, and preserved the evidence before User Test Summary handoff
- `User Test Summary Results Pending`:
  Live Validation and PR Readiness cannot be green while a user-facing workstream has a required User Test Summary handoff outstanding and returned results have not been submitted, waived, digested into the active authority record, and reevaluated. Workstream must not list this blocker as the reason to stop implementation; unresolved product work belongs to `Backlog Completion Unproven`, named implementation blockers, or the next bounded Workstream seam.
- `PR Creation Pending`:
  PR Readiness package-ready is not PR Readiness green. PR Readiness Stage 1 may record `Pre-PR Live State: No live PR`, `PR Creation Approval: Pending USER approval`, and `Stage 2 PR Creation: Pending USER approval` while it is still analyzing and repairing pre-PR posture; that state is lawful only before Stage 2 approval and must not be reported as PR-ready green. PR Readiness cannot be green until Stage 2 has USER approval and the GitHub PR exists for the current head branch and base branch.
- `PR Validation Pending`:
  PR Readiness cannot be green until the existing PR has been validated as open, non-draft, conflict-free, aligned to the merge-target canon, and clear of unresolved Codex comments/issues or requested changes.
- `PR State Unknown`:
  PR Readiness cannot be green if Codex cannot inspect the PR state, mergeability/conflict state, base/head alignment, or Codex review-thread state.
- `PR Readiness Execution User Approval Missing`:
  PR Readiness Stage 1 - Analysis Gate is an analysis-first readiness-lock gate. PR Readiness cannot enter PR Readiness Stage 2 - Execution Gate, create the PR, create recurring PR watcher automation, create a next branch, or perform release work until the Stage 1 packet is returned, all USER-approved current-branch Stage 1 repair/re-entry items are validated and durable on the current branch, `Stage 1 Ready For Stage 2` is recorded, and explicit USER approval to enter Stage 2 is recorded.
  This preserves the existing analysis-first blocker repair gate inside the readiness lock.
- `PR Readiness Stage 1 Repair Pending`:
  When PR Readiness Stage 1 finds repo drift, source-truth drift, validator drift, branch-authority drift, or a PR-readiness blocker that can be repaired on the current branch, Stage 1 records `PR Readiness Stage 1 Repair Required` and must remain in Stage 1 until the repair is complete. Stage 1 repair/sync may mutate, stage, commit, and push the active branch only when the current branch is the legal carrier and the USER-approved current phase/seam authorizes that bounded PR-readiness repair work; Stage 1 specifically owns repair or validation of already-encoded selected-next truth, merge-target `No Active Branch` projection, no-release-debt posture, any unavoidable merged-unreleased release-debt owner contract, and active-branch-authority cleanup when those items are found, and they must not be deferred to Stage 2 as planned sync. Stage 1 still cannot create a PR, create recurring PR watcher automation, create a branch, admit a package, waive single-slice rules, create a tag, create release artifacts, draft or publish a GitHub Release, or execute a release. Stage 1 may encode selected-next truth only when USER explicitly approves that selected-next sync, and it still must leave branch creation plus runtime package admission blocked for Branch Readiness.
- `Pre-PR Adversarial Review Firewall Missing` / `Pre-PR Adversarial Review Firewall Failed`:
  For helper, validator, parser, fixture, packet, RAR, UIREF, Product Experience, PR, release, issue-governance, or review-bundle changes, PR Readiness Stage 1 must run the local adversarial firewall before Stage 2 approval, PR creation, or another `@codex` review request. The required command is the current Python interpreter running `dev\orin_pr_review_churn_validation.py --pre-pr-firewall --base origin/main` (for example, `py -3 ...` on the Windows USER lane or `python3 ...` on POSIX agents) unless source truth names a tighter base. Nested manifest Python validation commands must use the portable `{python}` token so the helper resolves them to the current interpreter instead of a platform-specific launcher. Passing posture requires changed helper/validator/parser file family mapping, source-truth / implementation / fixture / generated-mutation / sibling-variant proof for every mapped family, connector-style corpus replay, unknown-comment overmatch guardrails, and local fixture validation. If the firewall is missing, skipped, fails, or reports unmapped changed helper/validator/parser files, Stage 1 remains in repair and Stage 2 / PR review request remains blocked.
- `No Successor Runtime Branch By Inertia`:
  Retired as a default PR Readiness waiver requirement after the external-state/index-only reform. Source-only, docs-only, governance, validator, or repo-wide support branches must not invent the next runtime carrier merely to satisfy selected-next gates. When no USER-approved selected-next truth exists, post-merge `No Active Branch` is allowed and the next runtime implementation pipeline waits for Branch Readiness Stage 1; this does not create, select, or admit a runtime successor.
- `Stage 1 USER Waiver Required`:
  PR Readiness Stage 1 may request an explicit USER waiver for a required Stage 1 review item only when repo truth allows a waiver. A selected-next waiver is not required merely because selected-next truth is absent; normal successor selection belongs to Branch Readiness Stage 1.
- `Next Workstream User Waiver Missing`:
  Retired as a default PR Readiness continuation blocker. PR Readiness does not require selected-next truth or a waiver by default. If USER explicitly asks PR Readiness to encode selected-next truth, the packet must record the USER decision and validate that selected-next truth; otherwise the next runtime implementation pipeline is selected later in Branch Readiness Stage 1.
- `Next Branch Package Shape Unproven`:
  Branch Readiness Stage 1 owns normal next-branch package-shape proof. PR Readiness uses this blocker only when USER explicitly approved PR-time selected-next encoding or when already-encoded selected-next truth is inconsistent.
  Branch Readiness Stage 1 owns normal single-slice drift review for the next branch. PR Readiness uses this blocker only for already-encoded selected-next truth that would be merged as durable source truth.
- `Family Organization Drift Risk Unresolved`:
  Branch Readiness Stage 1 owns normal family-organization review for the next branch. PR Readiness uses this blocker only for already-encoded selected-next truth that drifts away from the FAM -> Package -> Slice -> Seam model.
- `Current-Branch Branch Readiness Re-entry Required`:
  PR Readiness Stage 1 cannot continue to Stage 2 when next-workstream, next-branch, or governance/source-of-truth ledger blockers show that the current branch is still the legal carrier, but the fix is broader than bounded PR-readiness sync and must re-enter Branch Readiness on the same branch. This includes branch-shape drift, package/slice admission drift, or ledger repair that needs the current carrier's Branch Readiness authority before PR execution.
- `New Carrier Branch Required`:
  PR Readiness Stage 1 cannot continue to Stage 2 when the current branch is stale, merged, invalid, or legally cannot own the blocker, so a new real carrier branch is required. This applies to selected-next and next-branch shape blockers only when USER-approved PR-time selected-next truth or already-encoded selected-next truth is in scope, or to ledger items that cannot be cleared without USER approval or a new Branch Readiness carrier. Ledger-triggered fallback covers identity model drift, FAM taxonomy drift, package/branch rule drift, USER approval blocker drift, Branch Readiness or PR Readiness staging drift, selected-next recommendation drift when in scope, real-carrier routing drift, branch-authority lifecycle drift, watcher/automation proof drift, release readiness/execution boundary drift, Element Coverage misuse, ChatGPT loader/source-truth drift, project direction drift, current workflow drift, after-release workflow drift, and absolute-guardrail drift. The Stage 1 packet must output `Governance Ledger Fallback:` and `Branch Readiness Fallback:` and route the next legal work to Branch Readiness rather than create a PR, watcher, branch, package, selected-next truth, or release artifact by inertia. Branch Readiness fallback is real carrier branch/package analysis when PR Stage 1 cannot legally clear the blocker on the current branch; it is not workstream selection by default.
- `PR Merge Status Unproven`:
  PR Readiness cannot be green until the live PR has explicitly reported a green merge status. Treat unknown, unset, conflicting, dirty, blocked, or otherwise non-green mergeability/merge-state results as an active blocker until GitHub reports the PR merge status as green.
- `Bot Review Signal Pending`:
  for Codex-created PRs, PR Readiness cannot be green until the live PR has received a thumbs-up reaction or green approval comment from the Codex Connector bot. A bot comment is not approval; it keeps `PR Validation Pending` active until the branch fixes the comment on the same PR, pushes, replies to and resolves the review thread, requests Codex Connector bot revalidation, and receives a later Codex Connector bot thumbs-up reaction or green approval comment for the repaired live PR head. That approval proof must be bound to the current live PR head by review commit SHA, PR timeline order, or equivalent GitHub live-head evidence, not by local commit time alone. This is the same-PR Codex bot-review repair loop. Stage 2 final handoff cannot be green until the post-repair bot thumbs-up/approval latch is verified.
  When this blocker is active on a live Codex-created PR, Stage 2 must use direct PR verification before handoff; a manual "check later" plan is not enough, and recurring PR watcher automation is denied by default. Direct PR verification must inspect bot reactions, bot comments, review threads, PR comments, inline comments, PR state, status checks, and mergeability, and may perform bounded same-PR repairs for valid Codex bot comments that stay inside the approved PR scope. If no Codex bot comment or thumbs-up/approval signal appears after the current PR head has been live for at least two minutes, Codex may post exactly one PR conversation nudge for that head SHA asking the Codex bot for the review signal, and must not repeat that nudge for the same head. Every Codex Connector review-request or revalidation PR comment must be 3-5 words only, preferably `@codex review please`; head SHAs, validation summaries, repair narratives, and governance proof belong in the Codex thread digest, helper output, validator output, or external operational state, not in the PR comment. The required repair loop is: verify identity, evaluate the bot comment against source truth, repair only approved same-PR scope, rerun required validation, commit and push to the same branch, reply/resolve only when the review-thread contract requires it, request Codex Connector bot revalidation, and continue direct PR verification until the later thumbs-up/approval latch clears. The Direct PR2 Continuation Rule blocks quiet handoff: after any revalidation request or repair push, bounded PR2 must keep checking the live PR in the active Codex turn until a new actionable Codex comment is repaired or blocked, a current-head Codex approval latch plus green mergeability allows merge, the PR merges/closes, or a real blocker prevents further direct verification. `Current-Head Revalidation Pending` is an active PR2 continuation state, not a terminal `BLOCKED` state, while GitHub and the Codex Connector remain reachable and direct polling can continue; an eyes-only or quiet current-head review request must stay in the PR2 loop instead of becoming a blocked handoff. A helper run such as `--require-current-green` may return nonzero when the current-head latch is missing because merge-ready proof is not green, but if that missing latch is the only failure Codex must classify it as `Current-Head Revalidation Pending` and keep direct PR2 verification active rather than stopping as blocked. A final response that only reports an eyes-only/no-response current-head wait is a PR2 continuation failure unless direct verification is no longer possible, a true blocker is named, merge-ready/merged/closed state is proven, or the USER explicitly pauses/stops the loop. Out-of-scope bot requests must be reported as `BLOCKED`, not repaired.
- `PR Watcher Provisioning Unproven`:
  recurring PR watcher automation is denied by default for bounded PR Readiness Stage 2. This blocker applies only when the USER explicitly approves a named watcher exception for the live PR. If an exception is approved, the watcher target, approved reporting surface, routing proof, runtime path, run-proof method, fallback, teardown rule, replacement provisioning for the next live PR, and the live bot-review action contract must be explicit and proven before watcher-based proof can support PR Readiness. Watcher configuration is not runtime proof. Manual rollout-file or transcript-file injection does not count as proof.
  The action contract is part of any approved exception: thumbs-up reaction means report green for PR-entry validation; one or more actionable bot comments means trigger the bounded same-branch PR comment-repair worker, fix the issue, commit, push, reply, resolve the corresponding review thread, request Codex Connector bot revalidation with a 3-5 word PR comment only, and then keep `PR Validation Pending` active until a later thumbs-up reaction or green approval comment clears the repaired head. If the repair worker cannot complete safely, keep `PR Validation Pending` active and surface the exact blocking comment.
  PR watcher mode must be explicit under the PR Watcher Mode Contract in `Docs/pr_watcher_mode_contract.md`: `Silent Monitor`, `Verify Once`, `Repair Mode`, or `Blocked Mode`. Every approved watcher exception Verify Once post must include `Watcher Health Proof:` with `Watcher Mode:`, `Configured CWD:`, `Worktree / Branch:`, `PR:`, `Head SHA:`, `Mergeability:`, `Unresolved Review Threads:`, `Latest Bot Review:`, `Repair Authority:`, `Delivery Route Proof:`, `Runtime Proof:`, and `Next Watcher Posture:`.
- `PR Watcher Routing Unverified`:
  applies only to a USER-approved watcher exception. Even after watcher provisioning exists and run proof is present, watcher-based proof cannot support PR Readiness until the approved reporting surface is explicitly recorded and a validation pass confirms the configured thread/host target, state-file target, transcript target, and delivery proof all point to that recorded surface and that at least one watcher emission has landed there. Direct PR verification is the bounded PR2 default when no watcher exception exists.
- `PR Merge Verification Pending`:
  after PR creation, live PR validation, green merge status, and bot-review approval are complete, PR Readiness stays non-green until direct GitHub/GitHub-connector verification proves that the live PR is actually `merged`. If the USER approved a watcher exception, that watcher may provide additional merge evidence, but recurring watcher automation is not the default merge-verification owner.
  Post-merge closeout proof must be in merged source truth, not only in a deleted branch, reflog, automation memory, or conversation transcript. If missing proof blocks a release and the branch has not merged, return to `PR Readiness`; if the branch has already merged, carry it on the next real runtime package carrier's `Branch Readiness`.
- `Automation Runtime Unproven`:
  phase-critical automation cannot clear a gate merely because its card, config, or automation list says `ACTIVE`; `ACTIVE` is configuration state, not run proof. Accept run evidence only from thread or inbox output, automation memory/log/state-file updates, or scheduler last-run evidence. If the preferred Codex automation remains `ACTIVE` without run evidence, keep the owning phase blocked until run evidence exists or a bounded fallback is activated. Any bounded fallback must be target-scoped, phase-scoped, read-only, and self-terminating or explicitly deleted when its terminal condition or phase exit occurs.
- `Automation Observability Review Pending`:
  standing automations report into Codex automation run/inbox rows and `$CODEX_HOME/automations/*/memory.md`; those reports become source-of-truth work only after the applicable external operational owner classifies directly verified automation evidence as `BLOCKER_CANDIDATE` or `REVIEW_REQUIRED`. Informational green or waiting reports remain `REVIEW_INFO` unless contradicted by repo truth. Any admitted automation finding must enter a bounded repair seam before repo canon changes.
  Multi-worktree automation must also prove its configured cwd, git root, worktree role, branch, `HEAD`, and `origin/main` posture before a report may influence active-lane truth. `Automation CWD Worktree Mismatch` is the blocker when a standing automation runs from a missing, stale, neutral-main, parked, or wrong-lane worktree for the prompt it is carrying. Lane-sensitive prompts that mention active branch, PR Readiness, Release Readiness, post-merge, release-window, selected-next, toolchain, or branch governance cannot run from stale neutral main as if it were an assigned FAM or Governance lane. Automation memory is evidence only; stale `$CODEX_HOME/automations/*/memory.md`, Codex automation run/inbox summaries, or historical prompt assumptions must report `BLOCKER_CANDIDATE` or `REVIEW_REQUIRED`, not mutate canon directly.
  Background-observability-only automations cannot clear phase gates, bot-review gates, PR merge verification, release readiness, or same-PR repair proof. A stale historical toolchain-path report is `REVIEW_INFO` unless a current source-truth owner still declares that exact path active; otherwise the repair is to update the automation contract, not to recreate old files by inertia.
- `PR Readiness Scope Missed`:
  PR Readiness cannot be green while its product acceptance, branch identity, merge-target product contracts, or release obligations remain materially incomplete. Repair those on their legal repository carrier; operational Governance defects follow their external owner and do not become product diff by inertia.
- `Release Window Audit Incomplete`:
  PR Readiness cannot be green inside an unreleased release window until the active branch has audited that window, listed the currently known blocker set, and either clears those blockers on the same branch or records an explicit split waiver with user approval. Do not merge one blocker-clearing PR while already knowing that another blocker-clearing PR is queued behind it in the same unreleased window by default.
- `Release Readiness Health Pass Incomplete`:
  PR Readiness must prove post-merge source truth before PR creation or merge readiness. PR Readiness cannot be green until the active PR branch has run and recorded the `Release Readiness Health Pass`, under `Docs/phase_governance.md#release-readiness-health-pass`, so projected merged `main` would enter Release Readiness without stale source-truth cleanup.
- `Between-Branch Canon Repair Attempt`:
  PR Readiness cannot rely on any canon repair that is planned between branches rather than committed on the active branch before merge
- `Next Branch Created Too Early`:
  PR Readiness cannot be green if the next implementation branch already exists before the current branch has merged and updated `main` has been revalidated

The product-facing checks in `Release Readiness Health Pass` and the external owner's applicable operational checks must pass before reporting `PR READY: YES`.
A normal validator pass cannot clear a dirty worktree, unresolved PR blockers, missing live PR verification, or an unapproved remote effect.

### PR Readiness Stage Gates

`PR Readiness` remains one canonical phase. It is organized into two internal stage gates:

- `PR Readiness Stage 1 - Analysis Gate`: analysis-first readiness-lock gate. Stage 1 must analyze repo truth, identify PR-readiness drift/blockers, output the full `## PR Readiness Stage 1 Analysis Packet` for USER review, including Stage 2 execution plan, and remain active until one outcome is recorded: `Stage 1 Ready For Stage 2`, `PR Readiness Stage 1 Repair Required`, `Current-Branch Branch Readiness Re-entry Required`, `New Carrier Branch Required`, or `Stage 1 USER Waiver Required`. Bounded Stage 1 repair/sync is allowed only when the current branch is the legal carrier and the USER-approved current phase/seam authorizes that repair; repair truth must be validated and locally committed under explicit approval before the repaired Stage 1 packet is ready for USER review. Upstream creation and push require separate remote approval; local readiness never implies remote PR readiness. Branch Readiness Stage 1 owns the normal next runtime implementation pipeline selection, rooted in Nexus Vision, family vision, branch vision, current completed work, and the next implementation need. PR Readiness does not require selected-next truth or a waiver by default; Stage 1 owns repair or validation of selected-next truth only when USER explicitly approves PR-time selected-next sync or selected-next truth already exists and would merge as durable repo truth. Stage 1 also owns merge-target `No Active Branch` projection, no-release-debt posture, release target/floor semantics and Release Window Audit when relevant, any unavoidable merged-unreleased release-debt owner contract, and active-branch-authority cleanup when Stage 1 finds them. Stage 1 still cannot create the PR, create recurring PR watcher automation, create the next branch, execute release work, create tags/artifacts/releases, admit packages, or grant waivers without explicit USER approval. Stage 1 may encode selected-next truth only when USER explicitly approves that selected-next sync, and Stage 2 must verify the synced truth before PR creation.
  When the branch changes helper, validator, parser, fixture, packet, RAR, UIREF, Product Experience, PR, release, issue-governance, or review-bundle code/data, Stage 1 must include `Pre-PR Adversarial Review Firewall:` with the command result from `dev/orin_pr_review_churn_validation.py --pre-pr-firewall`, the mapped changed-file families, local corpus replay result, mutation/sibling coverage summary, and any remaining unknown or untested connector-family risk. A green normal validator suite cannot substitute for this firewall because the firewall exists to keep Codex Connector from becoming the first adversarial parser.
  This preserves the existing analysis-first blocker repair gate inside the readiness lock.
- `PR Readiness Stage 2 - Execution Gate`: begins only after explicit USER approval to enter Stage 2 and only when Stage 1 reports `Stage 1 Ready For Stage 2`. Stage 2 owns final PR execution only: verifying durable Stage 1 projection, commit/push only for bounded operator metadata if legally needed, PR creation, direct PR verification, bot-review handling, mergeability validation, and direct merge/close verification. Stage 2 PR creation must produce a ready-for-review pull request, not a draft; draft PR creation is invalid even when a plugin, connector, CLI helper, or external tool defaults to draft. If Codex accidentally creates or leaves a PR as draft during Stage 2, `Draft PR Created In PR2` blocks green until Codex converts the same PR to ready-for-review and records the correction in operator/external evidence. Recurring PR watcher automation is denied by default and requires a separate USER-approved watcher exception for the exact PR. Direct PR2 does not hand off while waiting for a bot response; it continues by direct PR verification until approval-plus-green-mergeability permits merge, a new comment is repaired or blocked, the PR merges/closes, or a real blocker appears.

The `## PR Readiness Stage 1 Analysis Packet` must include governed state markers, the planned PR title/base/head/summary, required post-merge path, release-debt impact, release-debt handling status, selected-next validation status when selected-next truth exists or PR-time selection is explicitly approved, required current-branch source-truth sync, completed merge-target canon updates when repairable drift is found, planned direct PR verification, planned watcher provisioning posture of `Denied by default` unless a USER-approved exception exists, planned validations, expected Stage 2 execution work, Stage 1 repairs made, Stage 1 repair validation, Governance Ledger fallback status, Branch Readiness fallback status, Stage 2 execution plan, drift findings, blocker and waiver findings, release-window audit posture, rollback path, `Next Legal Phase:` digest field, and the exact Stage 2 green-light decision needed from the USER. Packet field labels include `Selected-Next Validation Status:`, `Selected-Next Scope:`, `Branch Readiness Stage 1 Successor Selection Owner:`, `Review-Risk / Adversarial Coverage:`, `Optional Next Branch Block:`, and `Planned Watcher Provisioning:` so the output proves selected-next is either out of scope by default or explicitly validated, proves review-risk/adversarial coverage is complete for the changed-file scope, and proves recurring watcher automation will not be created by inertia. It may repair Stage 1 PR-readiness blockers on the current branch, but it must not perform Stage 2, create the PR, or create recurring watcher automation. It may encode selected-next truth only when USER explicitly approves selected-next sync, and branch creation plus runtime package admission must stay blocked for Branch Readiness. PR creation is blocked while any Stage 1 blocker, Stage 1 repair item, selected-next validation item when applicable, branch-shape review item when applicable, review-risk/adversarial coverage item, merge-target authority projection item, no-release-debt posture, unavoidable release-debt owner contract, or Stage 2 execution prerequisite remains unresolved.

Review-risk/adversarial coverage is part of normal PR Readiness Stage 1, not a separate phase. The required depth scales with the changed-file classes. Docs/source-truth branches must inspect owner placement, stale wording, duplicate authority, live-state leakage, path/casing drift, and likely Codex Connector comment classes. Helper, validator, fixture, packet, RAR, UIREF, Product Experience, PR, release, or issue-governance branches must additionally include rule-to-code-to-fixture mapping plus adversarial negative and false-positive coverage for parser boundaries, marker-only proof, malformed tables/rows, missing rows, casing, hyphenation, negation, contradictory prose, path roots, traversal, suffixes, duplicate paths, off-root evidence, stale packet state, and sibling failure modes discovered during review. UI/runtime branches must include owned-surface element-group coverage, accepted-reference comparison, backend-to-visual trace, screenshot/video/contact-sheet proof or explicit proof gaps, and issue-candidate disposition. If the Stage 1 packet cannot prove the applicable review-risk coverage, Stage 1 outcome must be `PR Readiness Stage 1 Repair Required`, `Current-Branch Branch Readiness Re-entry Required`, or `Stage 1 USER Waiver Required`; Stage 2/PR creation must not proceed on validator green alone.

`Review Churn Root-Cause Gate` is mandatory when an open PR receives three or more actionable Codex Connector comments in the same helper, validator, fixture, parser, packet, RAR, UIREF, Product Experience, PR, release, or issue-governance family, when total Codex Connector review comments exceed the configured review-churn budget for the branch helper, or when a later same-family comment appears after a same-PR repair push claimed that family was complete. High-volume churn is itself a PR Readiness Stage 1 prediction failure, even when every comment later becomes resolved, because GitHub review became the first effective adversarial fuzzer. The PR repair loop must stop before further review requests or merge readiness claims, cluster all live and historical same-family comments into a Review-Comment Pattern Matrix, identify why PR Readiness missed the family, and repair or route the durable source-truth, helper, validator, fixture, generated mutation/adversarial harness, and Stage 1 proof gap. Stage 2 may resume only after the repaired branch proves `rule -> code -> fixture -> generated mutation/adversarial case -> validation command` coverage for the affected family and reports remaining sibling risks as cleared, waived, routed, or explicitly blocked. For a live PR repair, the proof must inspect all GitHub review-thread pages and all pull-review-comment pages, report total/resolved/unresolved/outdated/unresolved-current counts, classify every Codex Connector review comment into a covered family or block on unknown classification, prove every changed helper/validator/parser file has family coverage, replay sibling variants locally, produce a final local Codex Connector simulation digest before another `@codex` request, and, when the budget is exceeded, carry an exact root-cause receipt with live connector-comment count, family counts, missed PR1 assumption, durable preventive changes, and receipt marker. Until then, `Review Churn Root-Cause Gate Active`, `Comment-Family Matrix Missing`, `Parser Threat Model Missing`, `Review Thread Pagination Proof Missing`, `Review Comment Pagination Proof Missing`, `Codex Connector Simulation Digest Missing`, `Review Churn Budget Exceeded`, `Review Churn Root-Cause Receipt Missing`, or `Rule-To-Code-To-Fixture-To-Mutation Proof Missing` blocks PR continuation.

When the active external branch planning owner contains UFD items, PR Readiness Stage 1 must include a USER Feedback Disposition fold-down review. Every `Feedback ID:` must be implemented, rejected/no-action with reason, deferred with waiver, folded into the structured branch receipt, promoted to Nexus/family vision when reusable, carried as a backlog future-candidate pointer only after USER acceptance, or assigned to a named future owner. The fold-down receipt must preserve a lookup path from each UFD ID to its final owner before the external branch plan can retire from active planning posture.

`PR package ready` is the state where local branch truth, merge-target canon, applicable selected-next validation, and copy-ready PR details are complete. It is not `PR Readiness GREEN`.

Live PR creation and validation facts are required for operator output and PR validation, but they are not merge-target current-state truth. Keep live PR state such as `open`, `non-draft`, `mergeable`, review-thread counts, repair-commit containment timing, blocker-clearing branch narration, and merge-target branch-head hash assertions in operator output and explicit historical PR sections only. Do not place those time-sensitive claims in merge-target current-state owner sections such as backlog or roadmap `## Current Branch Execution Posture`, `PR Readiness State:`, `Current Branch Objective:`, `Active Workstream Chain:`, or the canonical workstream merged-unreleased `## Phase Status` block.

Merge-target post-merge-stable authority projection is mandatory before PR green and is a PR Readiness Stage 1 repair responsibility when Stage 1 finds it. The PR branch must not merge an active branch authority record into `main`; the active authority record must be moved to historical/no-active posture or otherwise made merge-stable during Stage 1 before Stage 2 can execute. Post-merge `No Active Branch` does not require selected-next waiver truth when no USER-approved selected-next truth exists; normal successor selection waits for Branch Readiness Stage 1. Historical branch records must not retain active PR Readiness phase, active seam ownership, live/open PR wording, merge-watch ownership, or `PR Merge Verification Pending`. Operational PR/watcher facts may live in operator output or explicit historical PR sections, but merged current-state owners and historical authority records must already describe the post-merge truth that will remain valid after merge.

A post-merge projection receipt is not enough by itself. If a branch creates a separate projection file, PR Readiness Stage 1 must still fold down the real active authority record or remove it from `Active Branch Authority Records` before it reports `Stage 1 Ready For Stage 2`, before Stage 2 PR creation, and before merge approval. Projection-beside-active-authority blocks on `Merge-Stable Projection Shadowed By Active Authority`.

Projection-only fold-down inside the active record is also not enough. If the active branch record's `Release Readiness Health Pass` or `Post-Merge State` says the branch must become historical/no-active, must not remain active branch authority, or must become historical merged-unreleased evidence, PR Readiness Stage 1 must perform that real fold-down before Stage 2, PR green, or merge approval. Leaving the actual record in `Active Branch Authority Records` blocks on `PR Readiness Stage 1 branch-authority fold-down required`.

`Merge-Target Authority Projection Unproven` blocks PR green whenever that post-merge-stable authority projection is missing or would leave active branch-authority truth in merged `main`.

### Release Readiness Health Pass

The `Release Readiness Health Pass` is the single product-facing PR-check owner. Apply it during PR Readiness Stage 1, after any Stage 2 or bot-review repair that changes source truth, and before merge approval when its inputs changed.

Review the complete branch diff against the verified current `origin/main`, including all earlier commits, and record each changed path's durable owner. Check the prospective tracked result before commit, then the committed result:

```powershell
git -C "<approved-worktree>" diff --check origin/main
git -C "<approved-worktree>" diff --check origin/main...HEAD
```

Replace the placeholder with the exact USER-approved absolute worktree and verify its Git root, branch, HEAD, merge base, upstream and dirty scope before mutation. The first command does not cover untracked files; inspect every intended new file and verify the exact staged set before commit. A whitespace check alone is not the health pass.

Run the existing public product, privacy/security, build or release checks applicable to behavior retained in the final diff. Record command, inputs, result and limits; do not run unrelated suites by inertia. Prove ordinary source inspection and applicable public tests can run from a clean source copy without Governance State, USER, Temp, Validation or installed Control Plane state. Review durable owner routing, approval/worktree protection, post-merge projection and likely bot/human findings.

Local operational identity, authority and confinement checks belong to the current external `policy/POLICY.md`, the exact USER approval and live Git/GitHub facts. The legacy repository `--release-readiness-health-gate` is historical coverage, not a current command or acceptance prerequisite. An installed Control Plane validator pass proves installed source identity, not product PR health. Retained public tests may use pure functions from legacy helpers without activating their local operational entrypoints.

The health pass proves post-merge source truth before PR creation or merge readiness. It must fail if projected merged `main` would force Release Readiness to repair source truth instead of validating release posture.

The current external branch/workstream review record must include the following evidence fields, with a reasoned not-applicable disposition for unrelated release or runtime scope:

- `Post-Merge Branch Authority Projection:`
- `Stale Active Branch Wording Scan:`
- `Stale PR Creation / PR Readiness Pending Wording Scan:`
- `Merged-Unreleased Scope Posture:`
- `Release Execution Gate:`
- `Watcher / Live PR State Projection:`
- `Branch Cleanup Plan:`
- `Branch Cleanup Execution Gate:`
- `FAM Overlap Routing:`
- `Release Candidate Anchor Projection:`
- `Release Window Contributor Inventory:`
- `Governance Intake Routing:`
- `Projected Post-Merge Validation:`

Passing posture means exact post-merge branch-authority projection is recorded, no stale active branch wording lands on `main`, no stale PR creation / PR Readiness Stage 2 pending wording lands on `main`, merged scope is recorded as merged-unreleased when release execution is not being performed, release execution/tag/GitHub Release/artifact work remains gated, watcher/live PR state stays out of merged-main source truth, branch cleanup plan is known, FAM overlap is either non-blocking or routed to the owning lane, release-candidate anchor and release-window contributors are unambiguous, any post-merge source-truth blocker routing says `Governance Intake Routing: use the explicitly approved external operational Governance source carrier`, selected-next or successor truth is not stale, release-window/release-floor posture is resolved, and projected post-merge main would pass validation without a later source-truth repair.

Merge-Stable Source Truth Projection Gate:

- PR Readiness must prove the source truth that will remain valid after the PR merges, not only the pre-PR state that is true before Stage 2.
- Pre-PR markers such as `No live PR`, `PR Creation Approval: Pending`, `Stage 2 PR Creation: Pending`, `PR creation pending`, and `PR Readiness Stage 1 Ready For Stage 2` are lawful only inside clearly labeled historical pre-PR snapshot sections after a PR merges.
- Merged-main current-state owners, compact pointer rows, worktree slot receipts, active external branch planning owners, and canonical branch records must instead project historical merged-unreleased, released/closed, or no-active-branch posture after merge.
- If a merged branch record remains a canonical detail owner, it must name the merge PR/commit when known, clear active PR Readiness / PR creation pending wording from summary fields, retire or historical-label any repo branch-plan receipt, and route release execution as a separate USER decision.
- `Merged Active Branch Authority Not Folded Down` blocks when any branch listed under `Active Branch Authority Records` points to a branch ref already merged into `origin/main`; the validator must compare the branch ref to `origin/main` instead of relying only on compact `No Active Branch` wording.
- `Merge-Stable Projection Shadowed By Active Authority` blocks when a separate historical projection record exists for a branch but the same branch still has an active authority record in `Active Branch Authority Records`.
- `Merge-Stable Source Truth Projection Missing` blocks PR green, merge approval, or Release Readiness Stage 2 when stale pre-PR or Stage 2-pending wording would land in merged-main source truth.

Branch cleanup is planning-only until Branch Readiness owns a new branch/worktree target. `Branch Cleanup Plan:` records stale/old branch refs, retired worktrees, or GitHub Desktop repository entries that may need cleanup after merge. `Branch Cleanup Execution Gate:` must say cleanup is blocked in Release Readiness and may execute only during the next `Branch Readiness Stage 2 - Execution Gate` that creates or validates the next branch/worktree target. Multi-worktree cleanup must not delete a branch checked out by any worktree, remove a worktree before its replacement target is validated, or leave a GitHub Desktop-bound worktree without a valid branch target; stale/old branch cleanup waits until the replacement branch/worktree is created, Desktop is bound to the intended folder, and `git worktree list` proves no checked-out branch will be orphaned. `Stable Worktree Path Preservation Gate:` is mandatory when cleanup touches a family-stable or GitHub Desktop-bound folder path: record `Stable Worktree Path:`, `Replacement Binding Path:`, and the preservation method, and block on `Stable Worktree Path At Risk` unless the stable folder path remains the active repository target before the retired worktree or branch is removed.

`PR Readiness GREEN` requires all `PR package ready` conditions plus:

- the GitHub PR exists
- the PR is open and not draft
- the PR base/head match merge-target canon
- the PR has no conflicts
- PR state is inspectable rather than unknown
- no unresolved Codex comments/issues or requested changes remain
- direct PR verification has inspected the live PR head, mergeability, checks, Codex comments/reviews, approval latch, and merge/close posture in the active Codex turn or helper output
- the Direct PR2 Continuation Rule has not been bypassed; bounded PR2 did not stop on a quiet bot wait when direct verification could continue
- `PR Watcher Provisioning Unproven` and `PR Watcher Routing Unverified` are not active unless the USER explicitly approved a watcher exception for that PR
- `PR Merge Status Unproven` is clear only after the live PR has explicitly reported a green merge status
- `PR Merge Verification Pending` is clear only after direct GitHub/GitHub-connector verification proves that the live PR is `merged`
- the live PR has a thumbs-up reaction or green approval comment from the Codex Connector bot for the current head; when a bot comment appeared after the last approval, a later thumbs-up/approval signal is required after same-PR repair and comment-resolution closeout

### PR Readiness Response Contract

Every `PR Readiness` response must identify whether it is in `PR Readiness Stage 1 - Analysis Gate` or `PR Readiness Stage 2 - Execution Gate`.
When the response is Stage 1, it must include this packet and stop on `PR Readiness Execution User Approval Missing` until USER approval to enter Stage 2 is recorded:

```markdown
## PR Readiness Stage 1 Analysis Packet
- Current PR Readiness Stage:
- Repository Mutation Status:
- Planned PR Title:
- Planned Base Branch:
- Planned Head Branch:
- Planned PR Summary:
- Required Post-Merge Path:
- Selected-Next Validation Status:
- Selected-Next Scope:
- Branch Readiness Stage 1 Successor Selection Owner:
- Package-Size / Single-Slice Drift Review:
- Element Coverage Review:
- Release-Debt Impact:
- Release-Debt Handling Status:
- No-Release-Debt Handling Status:
- Required Current-Branch Source-Truth Sync:
- Planned Merge-Target Canon Updates:
- Origin/Main Freshness Check:
- Branch Creation Base:
- Current origin/main:
- Origin/Main Advanced Since Branch Creation:
- Origin/Main Changed Files:
- Branch Changed Files:
- Reconciliation Required:
- Reconciliation File List:
- Reconciliation Recommendation:
- Reconciliation Mutation Status:
- Review-Risk / Adversarial Coverage:
- Optional Next Branch Block:
- Planned Watcher Provisioning:
- Planned Validation Commands:
- Expected Files To Change:
- Stage 1 Repairs Made:
- Stage 1 Repair Validation:
- Release Readiness Health Pass:
- Release Candidate Anchor Projection:
- Release Window Contributor Inventory:
- Governance Ledger Fallback:
- Branch Readiness Fallback:
- Stage 1 Outcome:
- Stage 2 Sync Plan:
- Drift Findings:
- Blockers And Waivers Needed:
- Release Window Audit Posture:
- Rollback Plan:
- Next Legal Phase:
- Stage 2 Green-Light Decision Needed:
```

For a PR Readiness Stage 1 packet, `USER Review/PR_READINESS_STAGE1_REVIEW.md` is the
primary current-gate USER artifact. `USER_BRANCH_VISION_REVIEW.md` and
`USER_BRANCH_PLAN_REVIEW.md` remain supporting BP1/BP2 context and must not be
selected as the primary Stage 1 decision file. The Stage 1 artifact must state
the current outcome, repair posture, transition-safety proof, adversarial or
false-green coverage, USER Gate State, and exact USER decision supported. A
packet that is structurally valid but promotes a BP2 file as the Stage 1
primary is `PR Readiness Stage 1 Repair Required` and cannot advance on ZIP
parity alone.

Selected-next fields in this packet are validation/status fields, not a request for PR Readiness to create successor truth. `Optional Next Branch Block:` must be `Not in scope` unless USER explicitly requested PR-time successor selection, selected-next truth already exists, or Branch Readiness is the next legal phase.

Allowed Stage 1 outcomes are exactly `Stage 1 Ready For Stage 2`, `PR Readiness Stage 1 Repair Required`, `Current-Branch Branch Readiness Re-entry Required`, `New Carrier Branch Required`, and `Stage 1 USER Waiver Required`. `PR Readiness Stage 1 Repair Required` means bounded current-branch PR-readiness repair/sync remains in Stage 1 before Stage 2. `Current-Branch Branch Readiness Re-entry Required` means the current branch is still the legal carrier, but the fix is broader than PR-readiness sync and must re-enter Branch Readiness on the same branch. `New Carrier Branch Required` means the current branch is stale, merged, invalid, or legally cannot own the blocker, so a new real carrier branch is required. Stage 2 may begin only after `Stage 1 Ready For Stage 2` is recorded and explicit USER approval to enter Stage 2 exists.
Stage 2 begins only after `Stage 1 Ready For Stage 2` and explicit USER approval.
Branch Readiness Stage 1 owns the normal next runtime implementation pipeline selection. That selection must be rooted in project vision, family vision, branch vision, current completed work, and the next implementation need. PR Readiness may recommend next-workstream context, but it does not require selected-next truth or a waiver by default and must not create next-branch live state by inertia. Selected-next truth and active branch authority are different states. PR Readiness validates selected-next truth only when USER explicitly approves PR-time successor selection or already-encoded selected-next truth would merge as durable source truth. If no successor is approved before merge, merged `main` may be steady-state `No Active Branch` while carrying valid merged-unreleased release-window truth, and the next implementation carrier must be selected later through Branch Readiness from current `origin/main` and external operational state. The current product-facing `Release Readiness Health Pass` and external operational identity checks own stale active-authority closeout so Release Readiness does not discover stale active-authority truth after merge.

After a PR merges, active branch authority is invalid for that merged branch even when backlog, roadmap, or worktree slots do not project `No Active Branch`. `Active Branch Authority Records` may not retain any branch whose local or remote ref is already an ancestor of `origin/main`; failing to fold that record down to historical/no-active posture blocks on `Merged Active Branch Authority Not Folded Down`.

`Origin/Main Freshness Check` is required during PR Readiness Stage 1 before Stage 2 can begin. Stage 1 must compare `Branch Creation Base:` to `Current origin/main:` and report whether `Origin/Main Advanced Since Branch Creation:` is `YES` or `NO`. When `origin/main` advanced, Stage 1 must list `Origin/Main Changed Files:` from `git diff --name-only <branch-creation-base>..origin/main`, list `Branch Changed Files:` from `git diff --name-only <branch-creation-base>..HEAD`, decide `Reconciliation Required: YES / NO`, and, when reconciliation is needed, output a complete `Reconciliation File List:` plus `Reconciliation Recommendation:`. The `Reconciliation Mutation Status:` must be analysis-only with no file fixes during Stage 1. If changed upstream files/data need review and the packet is missing or incomplete, `Origin Main Reconciliation Packet Required` blocks Stage 2 and PR creation.

`Pre-Rebaseline Impact Audit` is required before any same-branch current-main reconciliation operation actually mutates local branch state. `Origin/Main Freshness Check` identifies whether upstream advanced before PR Stage 2; `Pre-Rebaseline Impact Audit` is the operation-level proof that reports `Incoming Main Change Set:`, `Incoming Changed Files:`, `Current Worktree Changed Files:`, `Branch Changed Files:`, `Rebaseline Overlap Files:`, `Incoming Runtime / Source-Truth Risk:`, `Validation Before Rebaseline:`, `Recommendation Only:`, `Rebaseline Mutation Approval:`, and `Rebaseline Mutation Status:` before Codex may run a fast-forward, merge, rebase, conflict resolution, or branch switch. Any non-empty `Rebaseline Overlap Files:` value triggers the `Rebaseline Overlap Intent Gate` and must resolve or explicitly block on `Rebaseline Overlap Intent Missing` before mutation.

`Current-Main Reconciliation Identity Guard` is required whenever a multi-worktree branch rebases, fast-forwards, or merges current `origin/main`. origin/main is context, not identity. The assigned worktree must preserve and reassert its own branch-local authority before validation, commit, push, PR readiness, release readiness, or handoff. The reconciliation digest must include `Assigned Worktree Branch Identity:`, `Branch-Local Authority Reassertion:`, `Incoming Main Active-Branch Blocks Accepted: NO`, and `Sibling Worktree Identity Preservation:`. Passing posture means the active worktree's expected branch, actual branch, authority record, current-state owner files, and GitHub Desktop-bound worktree are named explicitly; incoming `origin/main` branch/current-workstream/selected-next blocks are treated as context unless they are the assigned branch's own authority; `Docs/feature_backlog.md` and `Docs/prebeta_roadmap.md` reassert the active worktree's branch-local authority after conflict resolution; sibling worktrees such as FAM-006, FAM-007, Governance, or neutral `main` are not switched, deleted, or mutated; and no reconciliation commit lands with another worktree's active branch/current workstream identity copied into the assigned lane. If this guard fails during Branch Readiness, PR Readiness, or a same-branch rebaseline, stop on `Worktree Branch Identity Drift` and repair source truth inside the assigned worktree before committing. If Release Readiness discovers the failure after merge, the output digest must say `Governance Intake Routing: use the explicitly approved external operational Governance source carrier`.

`Release Candidate Anchor Projection` is required during PR Readiness Stage 1 before Stage 2 can begin for any release-bearing or merged-unreleased branch. Stage 1 must name the default post-merge `Release Candidate Anchor:` as current fetched `origin/main` after merge unless USER explicitly selects a historical release target, must name `Target Commit:` projection or source, must state whether later governance/source-truth PRs are part of the candidate, and must keep historical PR endpoints as audit evidence only unless USER approves `Release Candidate Anchor Source: USER-selected historical commit`.

`Release Window Contributor Inventory` is required during PR Readiness Stage 1 before Stage 2 can begin for any release-bearing or merged-unreleased branch. Stage 1 must identify whether the projected release candidate may include multiple FAM/worktree contributors, must name each known merged-unreleased contributor included or expected to be included in the target commit, must state whether the release is `Release Ownership Model: Aggregated release window`, and must route any contributor-specific blocker to the owning lane instead of letting merge order decide release ownership.

Stage 1 may include this user-facing block as non-binding planning context when USER asks for next-workstream recommendations, or when already-encoded selected-next truth must be validated before merge. This block is not required for PR Readiness Stage 2 by default. It may encode selected-next truth only when USER explicitly approves selected-next sync, and it must not create a branch, admit a package, or waive any blocker without separate approval:

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
- Next Workstream User Waiver:
```

Missing next-workstream recommendation, missing selected-next truth, or missing `Next Workstream User Waiver:` does not block PR Readiness Stage 2 by default. If selected-next truth is already encoded, or USER explicitly approves PR-time successor selection, Stage 1 must validate the selected workstream and stop on the applicable selected-next blocker when that truth is inconsistent. Otherwise the next-workstream decision waits for Branch Readiness Stage 1.

Stage 1 may include this next-branch pre-plan gate only when USER asks PR Readiness for a next-branch recommendation or when selected-next truth already exists and must be validated. Normal next-branch package-shape proof belongs to Branch Readiness Stage 1. This block remains analysis-first and cannot create a branch, admit a package, or waive single-slice rules; it may encode selected-next truth only when USER explicitly approves selected-next sync and still leaves branch creation plus runtime package admission blocked for Branch Readiness:

```markdown
## Next Branch Pre-Plan
- Next Branch Package Shape:
- Proposed FAM:
- Proposed Package:
- Candidate Slices:
- Candidate Work To Be Done:
- Single-Slice Drift Review:
- Family Organization Review:
- Element Coverage Review:
- Dependencies / Blockers:
- Validation / Live-Test Needs:
- Branch Creation Status:
- USER Approvals Required:
```


When `PR Readiness` reports package-ready or `PR package ready`, the response must include markdown-friendly PR operator copy blocks. Include a standardized `Next Branch` block only when USER explicitly requested PR-time successor selection, selected-next truth already exists, or Branch Readiness is the next legal phase.
Those package details are the input to PR creation and validation; they are not themselves proof that PR Readiness is GREEN.
This is a response contract, not permission to create the PR, merge the branch, release the branch, or create the next branch.

When included, the `Next Branch` block must distinguish the next legal branch from the selected next implementation branch.
For example, if USER explicitly approves unavoidable post-merge release handling, the next legal branch may be a release-support carrier while the selected next implementation branch remains deferred until after release handling and updated-`main` revalidation.

Optional conditional `Next Branch` block:

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

Required PR operator copy blocks:

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

Each PR operator field must be its own copy-ready block and must be usable independently.
The PR summary/GitHub PR body uses exactly two top-level sections: `## Summary` and `## What Changed`.
`## Summary` must be one concise human-readable outcome paragraph, not a duplicated changelog.
`## What Changed` must describe the actual branch work in concrete Markdown-friendly detail without repeating the Summary verbatim or keeping nested `### Summary`, `### Purpose`, or `### Overview` sections that only restate the Summary; use concrete subheads such as `### Source Truth`, `### Runtime`, `### Tooling`, or `### Review Support` only when they improve scanability.
GitHub PR bodies and PR Summary copy must not include top-level or nested `## Validation`, `## PR posture`, `## Branch Evidence`, `Testing`, `Checks`, `Does not include`, `Not Included`, `Non-Includes`, `Deferred`, `Future-Gated`, generic defensive scope dumps, or phase-digest/operator handoff fields such as `Next Legal Phase`, `Next Safe Move`, `Continue Decision`, `Stop Basis`, `Exact next USER decision`, `Implemented, validated`, or `::git-*`.
GitHub PR bodies and PR Summary copy must not include `## Validation`, `## PR posture`, `## Branch Evidence`, or defensive scope language.
Validation commands, command output, byte-proof evidence, mergeability, bot-review state, watcher state, and PR Readiness posture belong in Codex digests, helper output, status checks, or external operational state, not the GitHub PR body.
GitHub PR bodies and PR Summary copy must not include auto-close keywords such as `Fixes #`, `Closes #`, or `Resolves #` unless USER explicitly approved issue closeout for that issue set and the PR closeout strategy intentionally relies on GitHub auto-close behavior. Without that approval, issue references must use non-closing language such as `Related issue: #123` or `Issue evidence: #123`. `Issue Auto-Close Keyword Not Approved` blocks PR creation or PR body repair when auto-close language would create an unapproved issue mutation at merge.
Before PR creation, Codex must write the proposed GitHub PR body to a local temporary file and run `python dev\orin_pr_body_quality_audit.py --body-file <path> --body-title "<PR title>"`. If the helper reports `Changed: True` or any warning, PR creation is blocked on `PR Body Drift Check Failed` until Codex reruns the helper with `--apply` or otherwise replaces the proposed body with the normalized body and reruns the check green. After PR creation, Codex must verify the live PR body with `python dev\orin_pr_body_quality_audit.py --limit 1` or a narrower equivalent. All visible PR bodies must be scanned by `dev\orin_pr_body_quality_audit.py`; every nonconforming PR body inside the approved GitHub correction scope must be repaired before the PR-body standard can be reported green. If broad historical PR body mutation is not approved or GitHub access blocks repair, Codex must report the exact blocker instead of calling the all-PR scan green.
When the conditional `Next Branch` block is included and `May Create Now` is `NO`, the subsection must explain the blocking gate rather than implying branch creation is allowed.

### Operator Output Content Rule

Operator-facing PR summaries are evidence-first, and GitHub release notes are inclusion-only.
They must report what exists, what was implemented, what capabilities are available, how the system behaves, and which validation or release facts support the package.
PR summaries must not report generic defensive scope dumps, exclusion lists, deferred work, or PR posture. They should read like human review summaries grounded in the branch's actual changes.
Operator-facing PR summaries must stay evidence-only and must not carry phase-digest handoff fields; a surrounding Codex closeout may include governed phase markers, but the GitHub PR body may not.
Historical PR normalization must preserve useful historical detail inside the same two-section PR body shape and remove redundant Summary/Purpose repetition from `## What Changed`.
Historical PR normalization must not delete Summary paragraphs or bullets merely to make the Summary concise. Any trimmed non-duplicate Summary detail must move into `## What Changed` under a concrete subheading before live GitHub PR bodies are edited.
GitHub release notes must also use the standard Markdown release body shape used by the current pre-Beta releases: the body starts with `## Release Summary` or `## Release Overview`, continues with `## Release Highlights` or release-specific rich sections, then includes GitHub-generated `## What's Changed` and the generated `**Full Changelog**:` compare link to the previous release. The live release body must not start with or repeat the release title as `# <release title>`; the release title belongs in GitHub release metadata and in the separate `Release Title` operator block only.
This rule governs operator output packages; it does not remove normal canon requirements for branch scope, non-goals, stop conditions, or blockers in source-of-truth records.

### User-Facing Shortcut Live Validation Gate

For relevant desktop user-facing workstreams, Live Validation may use validators, direct runtime launches, helper launches, synthetic harnesses, troubleshooting launchers, and targeted manual probes to build scenario coverage.
Those evidence layers are supporting proof, not final green by themselves.

Before User Test Summary handoff, the final Live Validation closeout must launch and exercise the branch through the exact normal USER desktop runtime launcher path declared for the branch.
For desktop UI Live Validation, no sandbox/offscreen/direct-runtime path can be the primary LV1 path when the normal USER desktop launcher is feasible. Direct runtime launches, WebView harnesses, helper launches, generated-equivalent shortcuts, active-client probes, and troubleshooting launcher runs are supporting evidence only unless launcher parity proof and USER approval make the troubleshooting launcher equivalent for the exact claim being validated.
For Nexus Desktop AI, the default normal desktop launcher path is normally `C:\Users\anden\OneDrive\Desktop\Nexus Desktop Launcher.lnk` unless the active authority record declares a different exact USER desktop launcher path. A generated shortcut or non-Desktop equivalent is invalid as final USER-path proof unless it is the declared worktree-local normal runtime launcher created or repaired under the normal worktree launcher rule, or USER explicitly grants a waiver with reason.

Normal worktree launcher creation / repair:

- if the branch's declared worktree-local normal runtime launcher is missing, Live Validation may create or repair that launcher as validation setup before User Test Summary handoff
- the created or repaired launcher must target the active branch's normal product runtime entrypoint and working directory
- the created or repaired launcher must not target a troubleshooting runtime launcher, validation helper, synthetic harness, Dev Toolkit path, or diagnostic-only entrypoint
- the launcher must not enable troubleshooting mode, broad diagnostic capture, provider/model/cache/memory/private setup, startup registration, installer behavior, packaging/update behavior, or persistent OS integration
- the active authority record must declare `Normal Worktree Launcher Creation: CREATED`, `Normal Worktree Launcher Path:`, `Normal Worktree Launcher Target:`, `Normal Worktree Launcher Arguments:`, and `Normal Worktree Launcher Validation: PASS` before the created launcher can satisfy the shortcut gate
- this repair path is not a launcher parity waiver; it is valid only when the resulting launcher is the exact normal runtime path used for LV1 proof

Two-launcher exception:

- `Normal Desktop Runtime Launcher` owns ordinary USER proof.
- `Troubleshooting Runtime Launcher` is an explicit USER-consented diagnostic profile.
- Troubleshooting launcher evidence may count as formal equivalent proof only when `Launcher Parity Proof: PASS` shows both launchers start the same product runtime/build, use the same product data roots and user-visible behavior, and differ only by admitted diagnostic flags, diagnostic evidence roots, log level, and troubleshooting disclosure.
- If launcher parity is missing, fails, or the validated claim could be affected by troubleshooting-mode differences, Live Validation must use the normal USER desktop runtime launcher, request USER manual validation, or stop on a named blocker.

When the declared normal USER desktop runtime launcher is a Windows `.lnk`, shell-executing the `.lnk` path, launching the target script directly, or injecting private test environment variables is not enough for final proof. Codex must use visible user-level desktop control to click, double-click, or keyboard-open the exact USER desktop shortcut from a visible selected Desktop folder item, then exercise tray/menu/window interactions from that launched runtime. The governed human-client helper, old-style real-cursor movement, or another visible mouse/keyboard path may be the primary proof route when it preserves before/during/after photo/video or ordered-frame evidence and exercises the actual USER-facing control. Computer Use is optional supporting tooling only, not a required method, and it may be used only when it is target-safe and stable. Every desktop-control method must be target-safe: Codex may move the mouse, click, right-click, double-click, or type only against a visible accessibility element, a visibly identified app/window control, or a bounded screenshot coordinate that has been visually tied to the intended target in the current screenshot. Codex owns a deterministic visible-target acquisition loop before USER handoff: capture the current visible screen/window, inventory accessible elements and screenshot-visible controls, derive candidate targets from label/icon/proximity/state evidence, exercise only user-equivalent input against the visually tied candidate, and verify the expected visible result before reusing that target model. Hidden app activation calls, direct handler calls, internal signal dispatch, synthetic tray/menu activation, launcher foreground signals, or scripted shortcuts that bypass the visible control surface are not user-simulation proof. Live Validation must exercise the actual USER-facing control surfaces the USER would use; Codex must not create, add, or depend on a new user-visible runtime control surface, dev-only control window, shortcut side channel, or validation-only product window merely to make existing tray/menu/window controls targetable. Live Validation must preserve every window that was already open before the run: no setup, target-acquisition, backdrop, evidence, or cleanup step may use desktop-wide minimize/show-desktop, `Win+D`, per-window minimize, hide, restore, close, move, resize, rearrangement, or equivalent shell/Win32/UIAutomation window-state manipulation against those windows. An explicitly approved test may change the state of the in-scope product window only when that exact window-state behavior is under test; it never authorizes disruption of unrelated USER windows. Capture the initial visible state and verify preservation at closeout. If visible target acquisition or proof setup would require disturbing a pre-existing window, stop on `Live Validation USER Workspace Preservation Blocked`.
Activation-path proof is non-transferable. A visible mouse click proving a button path does not prove the matching keybind path, a keybind proof does not prove the click path, a tray/menu proof does not prove a dashboard/control-window path, and injected/internal activation never proves any USER-facing path. Each admitted activation path must be validated separately with photo/video or ordered frame evidence for the action plus the user-visible state/result it changes. If exhaustive Codex-owned visible attempts cannot safely prove exactly one activation path, USER may grant a named single-path manual validation waiver; that waiver records USER confirmation for that path only, remains supporting evidence for all other Live Validation dimensions, and cannot be generalized to other activation paths or product surfaces.
Visible desktop coordinate control is allowed and may be the primary route for OS-level surfaces such as taskbar tray icons, notification-area menus, window borders, resize handles, or desktop chrome. This route must use a visible desktop-control session or the governed human-client helper, slowly move the real Windows cursor to the screenshot-tied target, send real OS-level mouse down/up or drag input, preserve before/during/after photo/video or ordered-frame evidence, and verify the resulting visible menu/window/state. It is not an injection waiver: direct handler calls, shell commands, synthetic tray/menu activation, hidden app activation, blind coordinate probing, repeated nearby guessing, and desktop-wide minimize/show-desktop shortcut discovery remain invalid. If the actual tray/menu/window path cannot be safely targeted through visible evidence and bounded visible coordinate control is exhausted or unsafe, Codex must stop and elevate the exact manual USER validation need instead of fishing for coordinates.
A blocked activation path requires a `Manual Validation Request Digest` before USER handoff. The digest must name the exact control path, intended USER action, expected visible result/state change, screenshots or ordered frames already captured, why Codex proof is unreliable, the exact USER action to perform, pass/fail criteria, the single waiver scope, and the paths/surfaces that remain unproven. Codex must stop at this digest until USER confirms `GREEN`, `NOT GREEN`, or requests repair; it must not continue as if the path passed.

Named blocker:

- `User-Facing Shortcut Validation Pending`
- `Normal Worktree Launcher Validation Pending`

Machine-checkable authority-record markers:

- `User-Facing Shortcut Path:`
- `User-Facing Shortcut Validation: PENDING`
- `User-Facing Shortcut Validation: PASS`
- `User-Facing Shortcut Validation: FAIL`
- `User-Facing Shortcut Validation: WAIVED`
- `User-Facing Shortcut Waiver Reason:`
- `Exact USER Desktop Launcher Path:`
- `Exact USER Desktop Launcher Validation: PENDING`
- `Exact USER Desktop Launcher Validation: PASS`
- `Exact USER Desktop Launcher Validation: FAIL`
- `Exact USER Desktop Launcher Validation: WAIVED`
- `Exact USER Desktop Launcher Waiver Reason:`
- `Normal Worktree Launcher Creation: CREATED`
- `Normal Worktree Launcher Path:`
- `Normal Worktree Launcher Target:`
- `Normal Worktree Launcher Arguments:`
- `Normal Worktree Launcher Validation: PASS`
- `Troubleshooting Runtime Launcher Path:`
- `Troubleshooting Runtime Launcher Consent: PENDING`
- `Troubleshooting Runtime Launcher Consent: GRANTED`
- `Troubleshooting Runtime Launcher Consent: WAIVED`
- `Launcher Parity Proof: PENDING`
- `Launcher Parity Proof: PASS`
- `Launcher Parity Proof: FAIL`
- `Launcher Parity Proof: WAIVED`

Required proof:

- the declared exact normal USER desktop runtime launcher path launches the active branch runtime
- if a missing worktree-local normal runtime launcher was created or repaired during LV, its path, target, arguments, working directory, and normal-runtime posture are recorded and validation is `PASS`
- the exact USER shortcut is visibly clicked, double-clicked, or keyboard-opened from a visible selected Desktop folder item when a Windows desktop shortcut is the declared normal launcher path
- startup reaches the expected ready state
- the user-visible entry surface introduced or changed by the branch is visible or intentionally documented where the user must look for it
- relevant runtime markers, UI/manual readback, persisted-state checks, and cleanup evidence match the branch validation contract
- helper-only, direct-Python, WebView-only, sandbox/offscreen, active-client direct-runtime, generated-shortcut, troubleshooting-launcher-without-parity, or harness-only evidence is not treated as a substitute for this final launcher gate when the normal USER desktop launcher path is feasible

Lift condition:

- `User-Facing Shortcut Validation: PASS` and `Exact USER Desktop Launcher Validation: PASS` are recorded with evidence from the declared normal USER desktop launcher path, or both are recorded as `WAIVED` with reasons showing the branch is not desktop/user-facing or the exact normal launcher path is explicitly unavailable
- if troubleshooting launcher proof is used as equivalent, `Troubleshooting Runtime Launcher Consent: GRANTED` and `Launcher Parity Proof: PASS` are required before it can satisfy the exact claim being validated
- the blocker state is reevaluated after the result is digested

Routing:

- while `User-Facing Shortcut Validation: PENDING` remains, list `User-Facing Shortcut Validation Pending` under blockers and do not advance
- if `User-Facing Shortcut Validation: FAIL`, keep an explicit blocker and route back to `Workstream` or `Hardening` before PR Readiness
- if the shortcut gate passes or is waived, User Test Summary handoff may proceed only if all other Live Validation gates are green

Compatibility wording: the legacy phrase `real user-facing desktop launcher` means the exact normal USER desktop runtime launcher path declared for the branch; it is not a weaker substitute for the exact-launcher requirement.

### Runtime Observability / Live Validation Proof Contract

Rule Name: `Runtime Observability / Live Validation Proof Contract`
Owner: `Docs/phase_governance.md`
Applies To: BP2 USER Branch Plan Review, BP3 Workstream Entry / Orchestration Validation, Workstream implementation proof, Hardening H1, Live Validation LV1, User Test Summary handoff, active external branch plans, Live Validation helpers, USER review packets, and Codex return digests for runtime or user-facing desktop work.
Required State: every admitted feature, surface, control, window, bridge path, file/folder action, user-visible state transition, and validation-critical hidden state must receive an observability and proof decision before Workstream implementation begins. The decision must state whether normal runtime logs, troubleshooting-mode logs, Dev Toolkit instrumentation, exact normal desktop launcher proof, launcher parity proof, photo/video evidence, screenshot manifests, interaction matrices, manual USER validation, UTS coverage, privacy/redaction, user-visible disclosure, or future-gated observability are required.
Allowed Values: `Normal Runtime Log Required`, `Troubleshooting Log Required`, `Dev Toolkit Instrumentation Required`, `Exact USER Desktop Launcher Proof Required`, `Launcher Parity Proof Required`, `Photo / Video Proof Required`, `Manual USER Validation Required`, `UTS Coverage Required`, `No Log Needed With Reason`, `Privacy / Redaction Constraint`, `User-Visible Disclosure Required`, `Future-Gated Observability`, `Waived By USER With Reason`.
Invalid Values: `Helper PASS Is Proof`, `Marker PASS Is USER Proof`, `Direct Runtime Equals USER Path`, `Generated Shortcut Equals USER Launcher`, `Troubleshooting Equals Normal Without Parity`, `Screenshot Exists Therefore Accepted`, `Video Exists Without Adjudication`, `Unphotographable But Proven By Codex`, `Troubleshooting Enabled Silently`, `Internal Path Exposed As Product Folder`, `Evidence Packet Omitted`.
Blocking Condition: `Exact USER Desktop Launcher Proof Missing`, `Launcher Parity Proof Missing`, `Photo Or Video Proof Missing`, `Unphotographable Proof Not Elevated To USER`, `Direct Runtime Proof Misclassified`, `Troubleshooting Consent Missing`, `Live Validation Evidence Packet Incomplete`, `User-Visible Internal Path Leakage`, `Codex Live Client Self-QA Pending`, or `User Test Summary Results Pending` blocks the phase when applicable.
Repair Owner: current branch owner for product/runtime defects; owning helper/validator for proven tool defects; `Docs/phase_governance.md`, `Docs/branch_plans/README.md`, and `Docs/validation_helper_registry.md` for reusable governance/validation drift; USER for waivers, manual validation, and troubleshooting consent.
Repair Path: add or repair the observability decision matrix, declare the exact normal USER desktop runtime launcher path, rerun formal LV through that launcher, capture photo/video or ordered frame-sequence evidence for visible claims, adjudicate each artifact against Project Vision / Family Vision / FFV / accepted BP1/BP2 contracts, attach or reference raw evidence in the USER packet, elevate unphotographable claims to USER manual validation or explicit waiver, classify direct-runtime/helper evidence as diagnostic-only when it is not the USER path, and route any implementation defect back to Workstream or Hardening. If a troubleshooting launcher is used as equivalent proof, first prove launcher parity and USER consent; otherwise it remains supporting evidence only.
USER Decision Required: required to waive exact normal launcher proof, accept troubleshooting launcher proof as equivalent, waive photo/video proof, accept manual validation for unphotographable claims, enable troubleshooting mode, export/share diagnostic logs, or accept a product UI folder/path that exposes internal implementation concepts.
Validation Owner: active Live Validation helper, `dev/orin_branch_governance_validation.py` when the rule becomes machine-checkable, the product phase owner for required USER decision content and the external USER lifecycle owner for current review delivery, and the relevant family/runtime validators.
Final Disposition: Live Validation may report green only when exact normal launcher proof or approved parity proof, photo/video proof or USER-elevated waiver, runtime/log consistency, Dev Toolkit or helper evidence, visual adjudication, UTS state, and USER packet evidence are all reconciled. Direct runtime evidence remains diagnostic/supporting proof unless exact USER desktop launcher validation is passed or explicitly waived.

If the exact normal worktree-local launcher is missing, Live Validation may create or repair that launcher before rerunning proof only when it remains a normal runtime launcher. This is validation setup, not installer/shortcut/startup/package implementation, and it does not permit troubleshooting mode unless troubleshooting consent and launcher parity are separately recorded.

Formal proof hierarchy for user-facing runtime work:

1. Exact normal USER desktop runtime launcher photo/video proof owns visible USER-path acceptance.
2. Troubleshooting runtime launcher proof may substitute only when USER consent is recorded, launcher parity proof is `PASS`, and the exact claim is not affected by allowed troubleshooting differences.
3. USER manual validation or explicit USER waiver owns required claims that cannot be proven in photo/video.
4. Runtime logs, Dev Toolkit events, manifests, validators, and helper output support diagnosis and consistency; they do not replace item 1, item 2, or item 3 for USER-facing acceptance.
5. Direct runtime, WebView, sandbox/offscreen, generated shortcut, or helper launch proof is diagnostic-only unless USER explicitly waives the exact launcher requirement.

Normal versus troubleshooting runtime mode:

- `Normal Runtime Mode` is the default product launch profile. It uses minimal privacy-safe logs and avoids broad diagnostic capture.
- `Troubleshooting Mode` is an explicit USER-consented diagnostic launch profile. It must be local by default, temporary/scoped, privacy-safe/redacted where needed, and visibly different from normal runtime.
- BP2/BP3 must decide whether troubleshooting mode is required for the branch. Workstream may implement instrumentation only when the approved scope admits it. Live Validation may use troubleshooting evidence only as supporting proof unless launcher parity and USER consent make it equivalent for the exact claim being validated.

### Codex Live Client Self-QA Gate

For relevant desktop user-facing workstreams, Codex must perform a live-client self-QA pass before handing the feature to the USER for a formal User Test Summary.
The pass is not a substitute for USER acceptance, but it is Codex-owned product validation: Codex must inspect the launched UI as if it were a user and judge quality, usability, platform uniformity, naming cleanliness, interaction posture, cleanup, and evidence quality before asking the USER to spend time testing.
For desktop UI branches, this inspection must be human-client faithful when the USER will operate visible tray/menu/window behavior. Codex cannot mark Live Validation Stage 1 green from app-side callbacks, fake/offscreen models, marker-only proof, screenshot-only proof, or direct handler calls. The final LV1 handoff requires a manifest that records visible desktop shortcut launch, visible tray/menu selection, mouse/cursor or UIAutomation-backed interaction evidence, window move/resize/open/close evidence where applicable, screenshot or frame-sequence artifacts, and Codex's own visual review of every issue-grounded UTS item. Missing human-client evidence is a Live Validation failure unless USER explicitly waives it.

Named blocker:

- `Codex Live Client Self-QA Pending`

Machine-checkable authority-record markers:

- `Codex Live Client Self-QA: PENDING`
- `Codex Live Client Self-QA: PASS`
- `Codex Live Client Self-QA: FAIL`
- `Codex Live Client Self-QA: WAIVED`
- `Codex Live Client Self-QA Waiver Reason:`
- `Live Client Entry Path:`
- `Evidence Screenshot:`
- `Visual Quality:`
- `Codex Visual Adjudication:`
- `Visual Artifact Review Scope:`
- `Product Vision Alignment:`
- `Per-Element Visual Verdicts:`
- `Helper Marker Limitation:`
- `Unacceptable UI Findings:`
- `LV1 Handoff Disposition:`
- `Interaction Manifest:`
- `Interaction Evidence Root:`
- `Live Interaction Evidence:`
- `Usability Check:`
- `Interaction Check:`
- `Platform Uniformity Check:`
- `NDAI Naming Check:`
- `Cleanup Check:`

Required proof:

- Exercise the changed acceptance-critical behavior through its actual launched client or declared equivalent. Use visible user-path input for interaction claims; source, marker, direct-handler and synthetic tests remain supporting evidence.
- Define the affected surfaces, issue-specific targets, risks and representative regression cases. Reuse unchanged qualified results. Broaden to full-surface proof for broad redesign, demonstrated spillover or an applicable explicit acceptance requirement, rather than automatically rerunning every historical control/state/combination.
- Cover relevant normal, null/error, stressed, compact/default, modal isolation, persistence/dirty-guard and recovery behavior when the changed behavior or risk makes it material. Explain omissions; a base-state pass does not prove an untested acceptance-critical scenario.
- Inspect actual focused images/video and resulting states, record mismatches and distinguish evidence completeness from visual/runtime success. Helper PASS and screenshot existence do not accept unseen output.
- Full virtual-desktop capture and matched contrast backgrounds apply when placement, multi-monitor geometry, borders or compositing are affected. Preserve pre-existing USER windows and actual safety/input boundaries. Keep inspectable artifacts in the applicable approved USER evidence location.
- Preserve returned USER issues. Repair an escaped defect in its admitted surface and run affected regression proof. Correct governance only when the cause demonstrates a governance defect. No arbitrary one-or-two-defect quota or automatic governance expansion applies.
- Retain real UTS/human-result and phase boundaries. Do not hand off a known unwaived acceptance-critical defect as green. Continue authorized repair and affected verification before that handoff.


Routing:

- while `Codex Live Client Self-QA: PENDING` remains, list `Codex Live Client Self-QA Pending` under blockers and do not hand off the User Test Summary as ready
- if `Codex Live Client Self-QA: FAIL`, keep an explicit blocker and route back to `Workstream` or `Hardening` before USER handoff or PR Readiness
- if `Codex Live Client Self-QA: PASS` is recorded, the USER Test Summary handoff may proceed only if the shortcut/equivalent entrypoint gate and all other Live Validation gates are green
- `Codex Live Client Self-QA: WAIVED` requires explicit waiver reason and is valid only when the branch is not user-facing or the live client path is unavailable

### User Test Summary Results Gate

Live Validation Stage 1 must not enter Live Validation Stage 2 while a relevant user-facing workstream has a required User Test Summary handoff outstanding and returned results have not been submitted and digested.
User Test Summary is exclusive to Live Validation Stage 1.
Live Validation Stage 1 cannot enter Stage 2 until User Test Summary results are `PASS` or `WAIVED`, Codex has digested the result into source truth, and blockers have been reevaluated.
PR Readiness may verify the previously digested Live Validation UTS state, but it must not create, refresh, or digest UTS as its own phase artifact.
Live Validation green requires an exact `## User Test Summary` state before final green.
Every Live Validation digest must include an exact `## User Test Summary` section. If User Test Summary is waived, that digest section must still declare `User Test Summary Results: WAIVED` and `User Test Summary Waiver Reason:`; validation summaries, blocker summaries, and source-truth references do not replace the digest section.
This is a `Live Validation Stage 1` gate, not a Workstream, Hardening, or PR Readiness completion substitute.
Workstream and Hardening may maintain UTS strategy or readiness notes, but they must not create/refresh the formal desktop UTS export, create a UTS results seam, digest UTS results, or stop on `User Test Summary Results Pending`.

Named blocker:

- `User Test Summary Results Pending`

Required status model:

- Automated validators and live helper evidence: GREEN.
- User Test Summary Results: PENDING.
- Final phase advancement is BLOCKED until the filled User Test Summary is submitted and digested.

Machine-checkable authority-record markers:

- the active authority record must include an exact `## User Test Summary` section; `## User Test Summary Strategy` is planning context and is not the canonical `UTS` artifact
- while pending, the active authority record must include `User Test Summary Results: PENDING`
- while pending, the active authority record must list `User Test Summary Results Pending` under `## Blockers`
- while pending, `## Next Legal Phase` must not advance beyond the current phase
- when passing returned results are digested, the active authority record must include `User Test Summary Results: PASS` and a digest of the returned results before the blocker can clear
- when a waiver is used, the active authority record must include `User Test Summary Results: WAIVED` and `User Test Summary Waiver Reason:` before the blocker can clear
- when returned results fail or expose ambiguity, the active authority record must keep or replace the blocker with the appropriate Workstream or Hardening blocker and route backward rather than advancing

Lift condition:

- a filled User Test Summary is submitted or a documented waiver exists
- the results or waiver are digested into the active authority record
- the blocker state is reevaluated after digestion

Routing after digestion:

- if returned results pass, `User Test Summary Results Pending` clears and forward progression may continue if all other gates pass
- if returned results expose mismatch, regression, unclear behavior, cleanup failure, or scope drift, route back to `Workstream` or `Hardening` as appropriate
- if returned results raise new feature ideas, keep them out of current scope until backlog carry-forward is explicitly approved

### Release Readiness Candidate Anchor Rule

Release Readiness must validate the selected release candidate, not re-open historical PR endpoint cleanup by default.

Every Release Readiness packet must declare:

- `Release Candidate Anchor:`
- `Release Candidate Anchor Source:`
- `Target Commit:`
- `Historical Endpoint Handling:`
- `Candidate Includes Later Governance Repairs:`
- `Release Window Contributor Inventory:`

Default anchor rule:

- unless USER explicitly selects another release target, `Release Candidate Anchor:` is current fetched `origin/main`
- `Target Commit:` is the current fetched `origin/main` SHA for the repository being released
- later governance/source-truth repair PRs already merged into the selected candidate are part of candidate truth
- a release candidate may include governance/source-truth-only repair PRs after the last runtime PR; those PRs do not disqualify the candidate or force the release target back to the last runtime merge commit
- `Candidate Includes Later Governance Repairs:` must be `YES` when the selected candidate contains governance/source-truth repair PRs after the runtime PR that carried the user-facing release payload, and the release notes may keep those repairs in internal validation/traceability instead of presenting them as user-facing product features
- historical PR merge commits may be inspected as audit evidence, but they do not become the release-validation base unless USER explicitly selects that historical commit as the release target
- if USER selects a historical PR merge commit as the release target, Release Readiness must label `Release Candidate Anchor Source:` as `USER-selected historical commit` and must verify that commit's source truth without silently mixing later `origin/main` repairs

Pre-merge repair receipts are not the final Release Execution operator package. While an explicitly admitted repair PR is still in flight, a repo durable receipt may keep `Target Commit:` as an explicit external-owner pointer when it also names the release-window external state owner and says the final target commit must be resolved from Git/GitHub/helper live truth during Release Readiness. The active release-window external state must carry the current candidate target posture for local coordination. Once Release Readiness produces the release operator copy block, `Target Commit` must be a concrete commit SHA only.

### Release Window Aggregation Ownership

A release is owned by the selected release candidate window, not by whichever implementation PR or worktree merged last.

Every release-bearing candidate must declare:

- `Release Ownership Model:`
- `Release Window Contributors:`
- `Merged-Unreleased Scope Inventory:`
- `Last Runtime PR:`
- `Post-Runtime Governance Repairs:`
- `FAM Contributor Routing:`

Aggregation rule:

- when multiple FAM/worktree branches merge before the next public prerelease, the selected release candidate must inventory every merged-unreleased contributor included in the target commit
- merge order does not determine release ownership; the release owner is `Release Ownership Model: Aggregated release window` unless USER explicitly opens a release packaging branch or selects a narrower historical/release-branch target
- if current fetched `origin/main` contains both FAM-006 and FAM-007 merged-unreleased scope, both scopes are in the release candidate and both must have release-debt, validation, and issue/posture truth before Release Readiness can be green
- if one merged contributor is not release-ready, Release Readiness must block or USER must explicitly select a release target that excludes it, such as a historical commit or release branch; Release Readiness must not silently pretend the contributor is outside the candidate
- governance/source-truth-only PRs after runtime payload PRs are recorded under `Post-Runtime Governance Repairs:` and may be included without becoming user-facing feature claims
- after release publication, durable post-release closure must clear or move every included `Merged-Unreleased Scope Inventory:` item, not just the last merged branch

The blocker for missing or ambiguous contributor inventory is `Release Window Contributor Inventory Missing`.

### Release Readiness Issue Closeout Candidate Inventory

Release Readiness Stage 1 is read-only and file-frozen, but it must inventory issue closeout candidates when the selected release candidate includes branch records, branch plans, UTS returns, PR review repairs, diagnostics evidence, workstream records, or GitHub issues that claim or imply issue resolution. The inventory must use live GitHub/helper evidence when available and must not turn repo docs into a live issue ledger.

Required RR1 fields for each candidate issue:

- `Issue Number:`
- `Issue Title:`
- `Live GitHub State:`
- `Carried By Branch / Record:`
- `Completed By PR:`
- `Release Target:`
- `Evidence Source:`
- `Recommended Closeout Action:`
- `USER Approval Required:`

Allowed `Recommended Closeout Action:` values are `No Action`, `Comment Candidate`, `Close Candidate`, `Label Candidate`, `Milestone Candidate`, `Already Closed`, `Route To Branch Readiness`, and `USER Decision Required`. RR1 must stop on `Release Issue Closeout Inventory Missing`, `Carried GitHub Issue Not Dispositioned`, or `Issue Closeout Live State Unknown` when issue resolution affects release posture, USER-facing validation, or a release note/public claim.

Release Readiness Stage 2 may comment, close, label, milestone, or otherwise mutate GitHub issues only when USER explicitly approves issue closeout for the affected issue set. Without that approval, RR2 records `Issue Closeout Pending USER Approval` and may proceed only if issue closeout is not required for release truth. If issue closeout is required but approval is absent, `Issue Closeout Approval Missing` and `Issue Mutation Approval Missing` block the action.

Post-release closure rule:

- once a public prerelease tag exists, no current-state owner, compact pointer row, canonical detail branch record, retired branch plan, worktree slot receipt, or family vision pointer may keep that published release window's included scope as current `merged-unreleased` posture
- validation must derive the included release window from Git/GitHub/tag truth and first-parent PR/merge commits, resolving prerelease tags to explicit commit IDs or paginated GitHub compare truth before building the scan range so remote-only tag discovery cannot fall back to a tag-text-only check; when the previous prerelease commit is unavailable, validation must use paginated compare truth rather than widening to a full-history scan, then scan release-window branch records, branch plans, retirement rows, and compact pointers by release tag, PR number, merge commit, and branch identity
- included scope must be folded to released/closed or explicitly labeled as historical pre-release snapshot evidence that is not current posture
- Release Readiness must stop on `Post-Release Canon Closure Drift` when the selected candidate has already been published but source truth still describes an included contributor as merged-unreleased for that published tag
- post-publication source repair follows the owner-specific carrier route; Release Readiness remains file-frozen

Scope routing:

- if the selected release candidate is current `origin/main`, stale wording at an older PR endpoint is historical PR Readiness miss evidence, not a current Release Readiness blocker when later merged governance/source-truth repairs fixed the selected candidate
- if the selected release candidate still lacks release target, release floor, release debt, merged-unreleased, contributor inventory, or issue-posture truth, Release Readiness stops and emits a blocker digest only
- if the branch has not merged, the repair routes back to `PR Readiness`
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.

The blocker for missing or ambiguous anchor data is `Release Candidate Anchor Missing`.

### Release Readiness Target Gate

Release Readiness must not report green while any release target blocker remains unresolved.

Release Readiness is analysis-only and file-frozen. Required release target, scope, artifact, and candidate-anchor truth must be present. Missing or incorrect repository release contracts return to the owning pre-merge phase or a separately approved repository interface carrier; operational Governance defects route externally.

Hard blocker:

- `Release Target Undefined`:
  Release Readiness fails for a release-bearing branch unless the active branch authority record or active workstream authority record explicitly identifies all required release-bearing markers:
  - `Release Target:`
  - `Release Floor:`
  - `Version Rationale:`
  - `Release Scope:`
  - `Release Artifacts:`

  The target must also be semantically correct from the latest public prerelease and declared release floor; marker presence alone is not enough.

A branch is release-bearing when:

- its branch class is `release packaging`
- or it creates, prepares, validates, tags, publishes, or transitions release-facing artifacts or release-state canon

Small single-seam runtime proof that merges inside an existing family may be marked as aggregation evidence instead of a standalone release driver when the USER has not approved it as a release-version driver.
That record must declare the proof as `Standalone Release Driver: No` or equivalent aggregation-hold truth and identify the larger USER-approved family release or future aggregation target when one exists.
Such aggregation-hold evidence does not by itself justify a new release version, selected-next lane, or release packaging branch.

The only non-release waiver is:

- the active authority record explicitly declares `Release Branch: No`
- the record is preserved historical truth
- the branch does not create, prepare, validate, tag, publish, or transition release-facing artifacts or release-state canon

The non-release waiver is not available to `implementation` or `release packaging` branches.
It does not waive `Release Debt`, merge-target canon completeness, post-merge truth, successor lock, validation, or dirty-branch requirements.

If release target markers are missing on a release-bearing branch, the branch is blocked by `Release Target Undefined`.
If `Release Branch: No` appears outside a preserved historical record, the branch is blocked by `Phase Waiver Missing`.
If repository files are changed while their active phase remains `Release Readiness`, report `Release Readiness File Mutation Attempt`. Return to the owning legal repair phase before mutation; external Governance source work is a separately scoped operation, not a mutation inside product Release Readiness.

### Release Readiness Scope Boundary

Release Readiness is not a docs-sync phase. It is also not a file-mutation phase.

Release Readiness is analysis-only for repository files:

- it may inspect repo truth, branches, tags, releases, validator output, and release evidence
- it may produce release package information in the response, including tag, title, release notes, and release-execution instructions
- it may run validation commands that do not mutate tracked source files
- it must not edit, stage, commit, generate, or refresh source, docs, canon, validator, helper, release-note, or desktop handoff files

Release Readiness may read External Governance State only after USER-approved initialization. Repo-file validation in GitHub Actions or clean clones must not require `D:\Nexus Desktop AI\Governance State`; those environments validate durable repo truth only. If external state is missing during active local Release Readiness analysis, Codex reports `External State Missing` and uses the Missing External State Routing in `Docs/governance_efficiency_operating_model.md` to identify the applicable external owner and any missing exact authorization instead of inferring active branch, selected-next, worktree assignment, release-window, or watcher state from stale repo docs.

External state mutation during Release Readiness, including bounded RR2 post-release carry-forward reconciliation, requires the installed external owner to select the operation and existing USER authorization to cover its exact effects. Green release/tag/body/health validation supplies evidence; it does not grant write authority. Return any missing decision before mutation. Even when allowed, that mutation is limited to external operational release-window state, external acknowledgement state, external promotion/recovery packets, or external carry-forward records under `D:\Nexus Desktop AI\Governance State`; it must not edit repo files, create release artifacts, create branches or PRs, merge, release again, clean branches or worktrees, or touch FAM/runtime/private/provider/cache/memory surfaces.

Allowed in `Release Readiness`:

- release-candidate anchor validation
- release-target validation
- release-scope validation
- release-artifact validation
- GitHub release package information such as tag, title, and release notes
- final release-execution authorization or confirmation
- release-state confirmation after the release execution

Forbidden in `Release Readiness`:

- treating a historical PR endpoint as the release base without explicit USER-selected historical commit approval
- broad canon or docs sync that should have been completed in `PR Readiness`
- branch-authority cleanup that should have been merge-safe before PR green
- next-workstream selection, planning, or branch creation
- between-branch canon repair
- any source, docs, canon, validator, helper, release-note, or handoff-file mutation
- any direct write to protected `main`

### Release Readiness Operator Output Contract

When `Release Readiness` is green for release execution, the response must include markdown-friendly release operator copy blocks for direct GitHub release use.

Required release operator copy blocks:

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
<commit sha only for the final Release Execution operator package>
```

### Release Notes
```markdown
<detailed user-facing release notes>
```
````

Each release operator field must be its own copy-ready block and must be usable independently.
Release notes must be detailed, descriptive, and user-facing.
They must clearly explain what was built, what capabilities exist, and how the system behaves.
Release notes must follow the operator output content rule: report included work only, with no exclusion lists, `Not Included` sections, negative scope framing, or defensive wording.
The live GitHub release body must use the standard Markdown release body shape:

- `## Release Summary` or `## Release Overview`
- `## Release Highlights` or release-specific rich sections
- `## What's Changed`
- `**Full Changelog**:`

The live release body must not start with or repeat the release title as `# <release title>`. Keep the public title in GitHub release metadata and the separate `Release Title` operator block; keep milestone names, scope, behavior, capabilities, validation, and next-step context inside the Markdown body.
Public GitHub release bodies must be user-facing and must not include internal automation/tooling brand tokens, generated branch-prefix noise, phase-handoff text, operator transcript text, release-candidate anchor hashes, or internal source-truth/release-readiness governance phrasing. If GitHub-generated notes include `[codex]`, `codex/...`, `Release candidate anchor:`, `source-truth governance`, `governance/source-truth`, `release-readiness governance`, or equivalent internal tooling/phase labels, Release Execution must rewrite those line labels into neutral user-facing PR names before publication or repair the release body immediately after publication.
All published Nexus pre-Beta release bodies remain part of the live public release surface. Historical public prereleases must continue to satisfy the same release-body standard unless a release is explicitly legacy-scoped outside the Nexus pre-Beta line.
The `## What's Changed` section and `**Full Changelog**:` compare link must be populated by GitHub-generated release notes, using the GitHub release notes button or the generated-release-notes API with the previous release selected. Release Readiness may prepare the human-written summary and highlights, but Release Execution must combine them with the GitHub-generated notes before publication or repair the release body immediately after publication.

If Release Readiness discovers missing PR-owned canon or docs work, stop immediately and classify the issue as `PR Readiness Scope Missed` and `Release Readiness Scope Drift`.
If the branch has not merged, return to `PR Readiness` and repair the miss there before any Release Readiness output can be treated as green.
Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.

### Release Window Audit

Inside `PR Readiness`, any branch that is preparing, repairing, or validating truth inside an unreleased release window must run a formal `Release Window Audit` before it may report PR green.

The audit must explicitly answer:

- `Release Window Audit: PASS`
- `Window Scope`
- `Known Window Blockers Reviewed`
- `Remaining Known Release Blockers`
- `Another Pre-Release Repair PR Required`
- `Release Window Split Waiver`

Normal green posture is:

- `Remaining Known Release Blockers: None`
- `Another Pre-Release Repair PR Required: NO`
- `Release Window Split Waiver: None`

If the branch already knows another blocker-clearing PR will be required before release, do not call PR Readiness green by default.
The only allowed exception is an explicit user-approved split:

- `Release Window Split Waiver: APPROVED`
- `Release Window Split Waiver Reason: <why the split is intentional>`
- `Another Pre-Release Repair PR Required: YES`

Without that explicit split waiver, the branch is blocked by `Release Window Audit Incomplete`.
This rule exists to prevent serial blocker-clearing PR chains inside one unreleased window when one repair branch could have cleared the full currently known blocker set.

### Governance Drift Audit

Inside `PR Readiness`, the branch must run a formal Governance Drift Audit before it may advance to `Release Readiness`.

The audit must explicitly answer:

- `Governance Drift Found: Yes/No`
- `Drift Type`
- `Why Current Canon Failed To Prevent It`
- `Required Canon Changes`
- `Whether The Drift Blocks Merge`
- `Whether User Confirmation Is Required`

The audit must explicitly check whether the branch exposed:

- a missing blocker
- a weak phase entry or exit rule
- a weak source-of-truth ownership rule
- stale prompt scaffolding or stale operator examples
- a missing validator requirement
- a serial release-window repair pattern that should be consolidated onto the current branch instead of landing as another pre-release PR
- a repeated or carried blocker class whose repair must include recurrence analysis before green

If governance drift is found and unresolved, the branch is blocked by `Governance Drift`.

### Historical External Operational State Transition Gate

The completed Docs Split Stage 0–6E process, target matrices, prior blocker vocabulary and former standing-intake repair route are historical migration evidence. `External State Transition Gate Missing`, `External State Transition Drift`, `Docs Split Target Matrix Missing` and `External State Migration Premature` describe that retired transition contract; retained history does not activate those blockers for current work.

The chronology and prior stage boundaries remain in `Docs/external_operational_state_store_reform_plan.md` and the historical section of `Docs/governance_efficiency_operating_model.md`. Do not reopen, rewrite or execute completed receipts to satisfy current acceptance.

Current operational changes follow the installed external policy, explicit USER authorization, the legal source carrier, material validation and separately approved activation. GitHub Actions and clean-clone product validation remain independent of machine-local Governance State.

### External-State Currentness And Historical Coverage

The installed external Control Plane selects current operational record validation and writer implementations. A target result proves only its bound operation/input scope, never whole-root currentness or USER acceptance. Current work must prove exact targets, permitted effects, applicable before/after identity, confinement, foreign-change refusal, atomicity and rollback of exact own writes under that owner. Historical receipts remain immutable evidence; unrelated state partitions do not acquire a shared HEAD requirement.

The repository `TARGET_SCOPED_CURRENTNESS` mode and `dev/orin_external_state_*` reconcile/lock/promotion/snapshot entrypoints preserve earlier migration and compatibility coverage. They are not current execution prerequisites or live writer authority. Retained read-only forensic use needs explicitly selected roots and applicable historical schema; omitted defaults do not establish current root routing. The helper registry distinguishes that evidence from isolated product-useful public tests.

No current writer is inferred from a historical helper name, a completed transition stage or a consumed transaction. Select the applicable approved external operation; do not invent a replacement command or replay old admission.

### Governance Drift Escalation Rule

If governance drift is discovered in any earlier phase:

- stop normal progression immediately
- classify it as `Governance Drift`
- fix it on the active branch when the drift is tightly coupled to that branch's truth, phase, readiness, validation, closeout, or release state, or
- produce the exact required canon delta and wait for user confirmation when the repair would exceed the active branch boundary

Do not defer known governance weaknesses silently to a later branch.

Repeated or carried blockers must not be closed by surface cleanup alone.
Before the branch can report green, record what failed, why current governance or validation missed it, what prevents recurrence, and whether canon or validator coverage changed or was explicitly judged sufficient.

### Manual Evidence And Review Digestion Rule

Returned evidence such as:

- `UTS`
- screenshots
- interactive reports
- PR review comments
- release review findings

may satisfy exit criteria, but must never auto-advance phase by implication.

Required sequence:

1. digest the evidence
2. update the authority record
3. reevaluate blockers
4. only then advance phase

### Current-State Claim Containment

Time-sensitive current-state claims must live only in designated operational owners outside repo durable source truth, or be derived from Git/GitHub/helpers at the time of inspection.

After the External Operational State Store contract is implemented, live operational state that exists only to coordinate active branches, PRs, worktrees, release windows, review bundles, watchers, selected-next posture, or temporary handoffs must not be reintroduced into repo docs as current truth. Repo docs may preserve durable branch/document evidence pointers and historical receipts, but they must not own lifecycle posture such as active, complete, pending, no branch created, no live PR, PR creation pending, Stage 2 pending, selected-next current state, release-window ownership, or worktree assignment. If Release Readiness finds that state in repo docs, classify it as `Repo Live-State Leakage` unless it is clearly labeled historical receipt evidence.

Repo docs are index/context files for operational work. They may point to the branch, PR, release, external-state record, workstream, family vision, validator, helper, or receipt that owns detail, but they must not maintain the operational ledger itself. Branch plans, UFD rows, Branch Change Intent rows, Element-to-Phase rows, Workstream Entry review packets, Hardening plans, Live Validation plans, PR watcher state, release-window assembly, and review-bundle manifests belong outside repo docs while active unless USER grants an explicit transition exception.

Allowed operational-state owners after the external-state transition:

- `D:\Nexus Desktop AI\Governance State` for accepted local operational state
- `<worktree>\.nexus_state_staging\` for proposed state only after USER approval
- Git/GitHub/helper-derived live truth for branch, PR, release, issue, review-thread, and dirty-state facts
- repo docs only for durable rules, durable vision, branch/document evidence pointers, and historical receipts

Repo durable docs should be timeless or historical by default.
If they contain live-current claims, they must either:

- be converted to historical receipt evidence,
- be replaced with a durable pointer to the external/derived owner, or
- be removed from repo ownership through a USER-approved cleanup or fold-down repair.

### Governance Validation Routing

Operational Governance validation is owned by the current external `policy/POLICY.md` and the approved external source package. Legacy repository Governance validators are migration/history references, not prerequisites for executing or accepting their external replacement.

Use the smallest adequate checks for the material risks of the selected operation. A check must prevent a distinct plausible failure, and its result is valid only for its declared inputs and claim. Reuse unaffected results, use targeted checks while source changes, and run one proportionate final integration validation when the candidate is stable.

Repository product tests, build checks, release-contract checks, privacy/security checks, and user-facing acceptance remain in their product owners. Their existence does not require importing operational Governance code into the product repository.

### Phase Resolver Contract

Before any answer about current phase or next move, run this resolver:

1. validate live repo truth
2. determine whether there is an active executable branch, a blocked `No Active Branch`, or a steady-state `No Active Branch`
3. identify the exact matching external operational record and separately load the repository product phase/workstream contracts
4. detect blockers first
5. read the exact `Current Phase` exclusively from that external operational record
6. validate that phase, entry/exit proof and USER grant against repository product contracts and live Git/GitHub truth
7. return only the next legal phase, or no phase if blocked

At a real return boundary, report current phase/outcome, material effects/evidence, blockers, next authorized action and any exact missing USER decision. Honor a requested full digest with complete relevant detail and stable evidence links. Applicable decision/handoff reporting remains complete; absence of a fixed field or copied phrase alone is not a blocker.

If a blocker exists, do not recommend a later phase or next-lane execution.
If repo truth is a steady-state `No Active Branch`, do not invent an implementation branch by inertia; either report that no branch should open yet or name the explicitly approved non-implementation branch class that may legally begin.

## Proof Authority Matrix

When multiple evidence layers exist, use this authority order unless a workstream explicitly documents a tighter requirement:

1. runtime markers
2. persisted source truth
3. UIAutomation and readback
4. optional UI observations such as help text, examples boxes, and transient labels

UI-only observations may be logged as notes, but they must not override stronger runtime and persisted-source proof unless the UI interaction itself is the thing being validated.

## Proof Ownership Rule

- repo-wide phase governance defines the allowed proof model
- the active workstream doc defines the branch-local validation contract, active seam, and any explicit tighter requirements
- runtime markers and persisted source truth own correctness for product behavior unless the scenario is explicitly about UI interaction quality or reachability

## Validation Helper Contract

Interactive validation helpers should default to a reusable repo-wide contract unless a workstream explicitly documents a tighter branch-local need.

That contract is:

- runtime markers and runtime logs are the primary proof surface
- persisted source or persisted state snapshots are the secondary proof surface
- UIAutomation, readback, and other live UI inspection are tertiary proof surfaces
- gating observations and non-gating observations must be separated explicitly
- runtime helpers are expected when they materially improve deterministic startup, attach, or runtime-log capture
- a watchdog or equivalent timeout-enforcement path is required for meaningful interactive closeout work
- last-confirmed-progress logging is required for timeout or stall diagnosis
- cleanup guarantees are required for helper processes, launched apps, probe files, and other session artifacts
- saved-state or source snapshots should be preserved when write safety, reopen behavior, or no-write blocking behavior matters
- windows, dialogs, overlays, and controls should be re-resolved live across close/open seams instead of reusing stale references
- validation seams must be classified as `product defect`, `harness defect`, `environment issue`, or `canon / contract drift` before product code is changed

## Validation Helper Registry And Naming Standard

`Docs/validation_helper_registry.md` is the repo-wide registry for durable root `dev/` validators, live-validation scripts, audit helpers, harnesses, and shared helper modules.

The registry must define:

- the canonical helper naming scheme
- the allowed `Helper Status:` values
- which helpers are `Reusable`
- which helpers are `Workstream-scoped`
- which helpers are `Temporary probe`
- the owner, reason, consolidation target, and promotion decision point for every workstream-scoped durable helper

Naming standard:

- repo-side validators use `dev/orin_<domain>_<capability>_validation.py`
- live desktop helpers use `dev/orin_<domain>_<capability>_live_validation.ps1`
- interactive suites use `dev/orin_<domain>_<capability>_interactive_validation.ps1`
- audit helpers use `dev/orin_<domain>_<capability>_audit.ps1`
- reusable harnesses use `dev/orin_<domain>_<capability>_harness.py`
- shared helper modules use `dev/orin_<domain>_<capability>_helper.py`

Workstream-scoped exceptions are allowed only when reuse would contaminate proof ownership, blur workstream truth, or make validation less reliable.
They must use `dev/orin_<workstream_id>_<bounded_capability>_validation.ps1` or `dev/orin_<workstream_id>_<bounded_capability>_live_validation.ps1`, be registered immediately, and carry:

- `Helper Status: Workstream-scoped`
- `Owner Workstream:`
- `Reason Reusable Helper Was Not Extended:`
- `Consolidation Target:`
- `Promotion Decision Point:`

Seam-number helper names are not the default naming model.
They are permitted only as short-lived workstream-scoped bridge names created during active seam proof, and they must be consolidated, promoted, or explicitly justified before PR Readiness.

PR Readiness must fail if a new durable root `dev/` validation helper, live-validation script, audit helper, harness, or shared helper module is unregistered, has no helper status, or is workstream-scoped without a consolidation target.

## Live Validation Reuse-First Rule

Before creating a new live-validation helper, script, or harness, Codex must inventory existing repo helpers and choose the smallest safe reuse path.

Preferred order:

1. inspect `Docs/validation_helper_registry.md`
2. use an existing helper unchanged when it already covers the needed path
3. parameterize or extend an existing helper when the validation belongs to the same desktop/runtime helper family
4. extract shared helper support when multiple helpers need the same watchdog, progress, cleanup, UIAutomation, runtime startup, saved-state snapshot, or artifact-writing behavior
5. create a new workstream-scoped helper only when reuse would contaminate the helper boundary, blur workstream truth, or make validation less reliable

One-off probes are allowed only as temporary exploratory evidence under an ignored evidence root such as `dev/logs/...`.
They must not be used as closeout-grade proof, must not be left behind as de facto reusable tooling, and must either be deleted after the pass or deliberately promoted into a documented reusable helper with workstream artifact-history notes.

If a Live Validation pass needs helper or harness changes before it can produce trustworthy evidence, the branch must reopen to `Hardening` unless the active authority record explicitly allows validation-only support edits in `Live Validation`.

Closeout-grade proof has one extra rule:

- the default budget profile of the validation helper must itself prove green before branch closeout can be claimed

Exploratory command-line overrides may still be used during hardening, but a one-off override profile is not enough to call the branch green unless that same profile becomes the documented default or the documented default also proves green.

## Seam Classification Rule

Validation seams should be classified before they are fixed:

- `product defect`
- `harness defect`
- `environment issue`
- `canon / contract drift`

Do not treat a seam as a product defect merely because the interactive harness failed first.

## Seam Workflow Contract

`Docs/phase_governance.md` is the canonical owner of seam workflow behavior.
Prompts, workstream docs, and mode docs may name a seam chain, active seam, or validation focus, but they do not define continuation authority.
Codex must derive continuation, stopping, fallback, and phase movement from source-of-truth, validation, branch truth, and this contract.

### Phase Scope

Seam workflow applies differently by phase:

- `Branch Readiness` may use planning, admission, or tightly coupled governance-repair seams, but it must not execute product/runtime implementation.
- `Workstream` uses the full bounded multi-seam pipeline as the primary execution model when an approved seam chain remains inside its governed boundary and validation stays green.
- `Hardening` may use a constrained continuous validation loop when the branch is already inside an approved hardening boundary.
- `Live Validation` may use validation, evidence-digestion, waiver, or output-contract seams; it must not become a hidden implementation phase.
- `PR Readiness` uses readiness-gate seams for merge-target canon, drift audit, PR creation, and PR validation; it is not a product implementation seam pipeline.
- `Release Readiness` is analysis-only and file-frozen; it may use review steps in output, but it must not execute file-mutating seams.

### Bounded Multi-Seam Workflow

A bounded multi-seam workflow is an ordered sequence of seams executed inside one approved phase boundary.
It is the default execution model for any governed pass working the current slice through one or more seams.
Every seam in the sequence must stay within:

- the same workstream or equivalent active authority record
- the same normal phase
- the same branch class
- the same approved scope or tightly coupled governance/validation repair scope
- a validation surface strong enough to prove the seam before continuation

Multi-seam does not mean batch execution.
It means Codex continues across a planned seam sequence without requiring a new operator prompt after every seam, while still executing exactly one active seam at a time.
Risky categories such as UI, launcher, settings, protocol, cross-subsystem, or policy work require sharper per-seam boundaries and stronger validation, not an automatic stop.

### Slice And Seam Definitions

A slice is a bounded admitted backlog-completion unit; a seam is the current execution checkpoint inside or between slices.
`bounded` describes scope and blast radius, not partiality by default. A bounded slice may still be the full currently implementable backlog-completion pass for that backlog item or branch lane.
One coherent seam or slice is valid. Continue useful admitted same-phase work to its approved outcome; no next-seam obligation, single-slice waiver or continuation latch creates authority. Preserve affected proof and accepted planning. Stop the affected action for a genuine safety/proof failure, uncovered scope/owner, phase boundary, USER stop or required external result. Continue safe independent admitted work. A scoped USER instruction is honored as stated; it does not need a separate split marker to constrain execution.


### Seam Stages

Each active seam follows this governed stage model:

1. `Stage 0 - Startup and admission`: load the required source-of-truth, confirm branch, phase, branch class, blockers, active authority record, and whether multi-seam continuation is legal.
2. `Stage 1 - Seam analysis and plan`: define the seam name, exact boundary, affected files or evidence surfaces, explicit non-includes, validation gate, cleanup expectations, risk class, and `UTS` applicability.
3. `Stage 2 - Execution`: execute only the active seam within the approved boundary.
4. `Stage 3 - Review and validation`: run the seam validation, inspect results, classify defects or drift, and loop back to Stage 2 only for the same seam when validation, stop-loss, and phase rules allow.
5. `Stage 4 - Record truth and continuation decision`: update branch-local workstream evidence, authority records, `UTS` artifacts, helper registry, or governance docs only when truth changed and the phase permits mutation; then report `continue` or `stop`.
6. `Stage 5 - Finalization`: summarize work, validation, cleanup, durability state, remaining blockers, next legal phase, and next safe move.

Stage 4 is not permission to churn canon after every seam.
Repository files are updated only when branch-local truth, evidence, validation contracts, helper records, or governing rules actually changed and the current phase permits file mutation.
Stage 5 becomes a terminal closeout only when `Continue Decision: Stop`; otherwise it is a status checkpoint and execution must continue into the next admitted seam or slice.

### Required Per-Seam Declaration

Before each seam, Codex must state:

- the seam name
- the active phase and branch class
- the exact boundary
- the affected files or evidence surfaces when known
- the explicit non-includes
- the validation gate required for that seam
- cleanup expectations when the seam opens files, processes, windows, helpers, or temporary artifacts
- `User Test Summary` applicability when user-visible or operator-facing behavior may be affected

After each seam, Codex must:

- run the required validation for that seam
- update active workstream evidence when branch-local truth changed
- update the canonical workstream `User Test Summary` when the seam changes user-visible or operator-facing behavior
- verify cleanup for artifacts the pass created or opened
- decide and report `continue` or `stop`
- continue by default to the next seam needed inside the current slice when `Next-Seam Continuation Required` applies and the continuation authority conditions pass
- act on a `continue` decision by starting the next seam before final closeout

### Continuation and boundaries

Continue under actual current approval while the objective, owner, permitted phase, scope and safety posture remain valid. Correct in-scope failures and run affected checks without replaying unchanged planning or historical audits. An unresolved safety/proof failure blocks its affected effect; it does not automatically block independent safe work.

Stop for material uncovered risk/scope, contradictory authority, unsafe custody, actual phase transition, explicit USER stop, or required external result with no useful admitted work. Category labels and the number of slices are not stop conditions. Pending external review is rechecked on changed evidence/revision, not unchanged polling. Safety timeouts remain enforced by their owners.

## Backlog-Split Rule

Keep related work on its admitted carrier where appropriate. An actual branch split or new backlog identity requires applicable authority and clear ownership. No waiver is required merely because one coherent deliverable completes the approved objective. Preserve accepted deferrals without claiming them implemented.

When a backlog split is used, the output or authority record must name:

- `Backlog-Split User Approval: APPROVED`
- `Backlog-Split Reason:`
- `Backlog-Split Boundary:`
- `Backlog-Split Resume Point:`

Category labels, restrictive task wording, and cautionary phrases such as `execute WS-1`, `stop after WS-1`, `smallest safe slice`, `high-risk`, `launcher`, `settings`, `protocol`, `UI-model`, or `cross-subsystem` do not create split authority by themselves.
Same-branch slice continuation does not authorize phase skipping, readiness claims, or batching multiple seams without per-seam validation.

## Continuous Validation Loop Rule

When the approved prompt or execution boundary explicitly authorizes a continuous validation pass inside `Hardening`, Codex may continue across seam iterations without waiting for a new user prompt after every rerun.

That is allowed only while all of the following remain true:

- the branch is still in `Hardening`
- the same workstream boundary and closeout goal remain valid
- the proof hierarchy, timeout contract, and helper default profile remain unchanged
- no blocker, truth drift, or required canon-sync stop appears
- the pass is still moving through one active seam at a time

Inside that continuous loop, Codex should:

- identify the first real failing seam
- classify it before changing product code
- fix only that seam
- rerun the checks whose material inputs or claims changed; preserve unrelated valid results
- continue until the approved outcome is complete, then run the proportionate final integration check; route unrelated improvements as nonblocking observations

## Stop-Loss Rule

For governed recovery or another approved continuous validation pass:

- stop immediately if a blocker appears
- stop immediately if truth drift appears
- stop immediately if timeout inflation beyond the documented contract is required
- stop immediately if proof ownership, gating rules, or the helper default profile must change before the next rerun
- stop if `2` consecutive seam fixes fail to move the first-failing seam or otherwise fail to produce material end-to-end progress
- stop if roughly `90 minutes` of validation work pass without material end-to-end progress toward green
- when stop-loss is reached, diagnose the dependency or scope defect; a new memo or resumed timer alone is not corrective progress

## Timeout Governance

Interactive hardening and live-validation work must use tiered hard stops.

Repo-wide target contract for hardened desktop interactive helpers:

- preflight startup gate: `<= 60s`
- seam or control-acquisition gate: `<= 3s` once the live desktop surface is already open
- no-progress watchdog: `<= 3s`
- normal scenario budget: `<= 60s`
- exceptional scenario budget: `<= 90s`, only when explicitly declared in the workstream doc
- full interactive rerun hard cap: `<= 15 minutes`
- outer execution timeout: only slightly above the harness hard cap

Prohibited without explicit workstream-doc reconciliation:

- undocumented `90s+` scenario budgets
- undocumented `15m+` full-run caps
- silent timeout inflation during closeout

Additional repo-wide rule:

- when hardening proves that a tighter and faster default helper profile is stable, that profile should replace the older relaxed default before closeout-grade proof is claimed
- if a seam keeps breaching the documented `3s` or `60s` targets, treat that as validation-helper or process debt and redesign the proof path instead of silently letting the run sit longer
- every interactive helper or live-validation run must emit visible progress before and during execution, including scenario start, meaningful step progress, scenario result, and last-confirmed-progress evidence
- if a helper does not already enforce a tighter watchdog, `10s` is the maximum allowed no-progress interval before the run must self-abort, clean up, report the last confirmed progress point, and classify the stall
- long-running interactive commands must not hide behind only the shell/tool outer timeout; they must be supervised by a watchdog, monitor job, child process, or equivalent path that can abort and clean up blocked UIAutomation, app launch, screenshot, focus, source-write, or cleanup operations
- Codex should poll or surface helper progress during live validation instead of leaving the operator with a silent long-running command

## Truth-Drift Enforcement Rule

- if validation or harness behavior changes materially, canon must be updated before continued execution is recommended
- if a workstream changes which evidence layer is authoritative for success, that change must be written into the active workstream doc before the next seam-fix iteration
- if a workstream doc, harness defaults, and live execution evidence disagree, the workflow remains in `Hardening` or `Live Validation` until the drift is reconciled

## Preflight Requirement

Before a full interactive gate is used as a closeout proof surface, run or confirm a preflight that proves:

- startup or probe acquisition works
- runtime log creation works
- the overlay or root runtime surface opens
- the cleanup path works
- no stale helper processes, probe windows, or leftover session artifacts are still active from an earlier failed run

If preflight fails, the branch remains in `Hardening`.
Do not burn a full closeout run first.

## Desktop UI Audit Rule

When a branch materially changes user-facing desktop UI and that UI is relevant to the closeout claim:

- a live launched-process UI audit is required before branch closeout is treated as complete
- the audit should happen after the branch is green or effectively green, not during every seam iteration
- the audit evidence should include a manifest or equivalent index plus the captured screenshots or other durable artifacts
- the audit should check layout, readability, visibility, hierarchy, and obvious regressions against the current desktop UI direction

This does not create a repo-wide rule that every validation pass must always take screenshots.
The canonical rule is narrower:

- marker-first proof for behavior
- live launched-process UI audit when meaningful desktop UI changed and closeout depends on user-facing UI quality

### Visual-Claim Proof Lock

When a branch carries a concrete visual/layout concern, H1 or closeout proof must
prove that exact visible concern with geometry assertions, screenshot audit
evidence, or an equivalent durable visual check. Dataset markers, copy presence,
and successful click/action flow cannot by themselves close a visual/layout
claim.

If USER screenshot or video evidence contradicts a green H1 result, the branch
returns to Hardening for that concern. Codex must record why the earlier proof
was insufficient, patch the smallest reliable validator/helper coverage that
would have caught the defect, rerun validation, and only then recommend PR
Readiness or user handoff again.

### Branch-Local Visual Acceptance Target Overlay

An active implementation branch may record a branch-local Visual Acceptance
Target overlay only when USER approval names the branch, worktree, affected
surface class, and source-truth owners. The overlay is provisional branch-local
source truth for that carrier; it is not a durable repo-wide phase, global UI
standard, implementation template, shared primitive, or reusable validator
mandate until a later Governance/FAM-002 carrier promotes it.

Applies To: material UI/UX direction on the approved branch, including settings
surfaces, tray menus, window chrome, dropdowns, lists, filters, buttons, dirty
guards, state labels, tooltips, and other visible element groups where USER or
Codex must select or compare a visual direction before implementation or before
a green claim can be trusted.

Required classification before implementation or green claims:

- material UI/UX changes must be classified before implementation, renewed
  Live Validation, UTS handoff, PR Readiness, or any visual green claim
- when a packet includes design options, candidate renders, mockups, reference
  comparisons, or hybrid recommendations, the packet must label them as
  `Design Candidate Render`, `Reference`, `Rejected Pattern`,
  `USER_ACCEPTED`, `REPAIR_REQUIRED`, `WAIVED_WITH_REASON`, or
  `Not Applicable With Reason`
- design candidate renders are evidence for USER judgment only; they are not
  source truth until USER selects, combines, revises, rejects, or waives them
- a USER-accepted Visual Acceptance Target is a high-fidelity guide/template
  and comparison target for the affected branch-local surfaces and states; it
  must be close enough to the intended final product to guide expectation and
  implementation, but it is not a guaranteed literal final or end-state
  screenshot
- future Workstream, Hardening, Live Validation, UTS, or PR Readiness visual
  green claims for those surfaces require actual implementation evidence
  compared against the accepted guide/target, with material deviations
  explained, source-truth-grounded, and USER-approved where required

Evidence rules:

- the packet must include actual inspectable evidence when evidence is in
  scope, such as PNG screenshots, contact sheets, videos, ordered frame
  sequences, code-to-visual traces, state matrices, or explicit proof-gap rows
- visual-target packets that include an element legend must make the legend
  traceable to rendered evidence through readable element IDs plus visual
  callouts such as outlines, arrows, labels, highlight boxes, circles, or an
  equivalent annotated element map; color alone is insufficient
- local paths, screenshot existence, marker presence, helper green output,
  validator green output, attractive screenshots, or packet ZIP parity cannot
  by themselves prove visual acceptance or implementation match
- USER/ChatGPT UI findings are seed defects, not the ceiling; Codex must
  independently inspect nearby element groups, adjacent states, and likely
  user journeys within the approved scope before reporting the surface green
- hybrid or additional option recommendations are valid review inputs when the
  source truth and USER approval allow additional rendered candidates; those
  options must carry the same evidence, tradeoff, and state-matrix expectations
  as the original candidates
- if USER/ChatGPT identifies UI defects, proof gaps, false-green risk, or
  missing evidence, the owning branch must use the Unified Defect Ledger or
  equivalent active external branch ledger before broad repair or closure

Required packet fields when a branch-local Visual Acceptance Target packet is
generated: `Current Gate:`, `Design Candidate Render:`, `Visual Acceptance
Target:`, `USER_ACCEPTED:`, `REPAIR_REQUIRED:`, `Implementation Match Proof:`,
`Artifact To Surface Ledger:`, `State Matrix:`, `Rejected Patterns Ledger:`,
`Legend / Callout Traceability:`, `Accepted Target Is Guide / Template, Not
Literal Final Screenshot:`, `Source-Truth Conflict Classification:`,
`Branch-Local vs Durable Governance Disposition:`, `USER / ChatGPT Findings Are
Seed Defects:`, `Codex Independent Evidence Inspection:`, `Current Gate
Preserved:`, and `Not LV Green / Not UTS Complete / Not PR-Ready:` or
equivalent USER-readable wording.

Blocking conditions: `Visual Impact Classification Missing`, `Design Candidate
Evidence Missing`, `Visual Acceptance Target USER Decision Missing`, `Candidate
Render Treated As Source Truth`, `Screenshot Existence Treated As Acceptance`,
`Visual Target Treated As Literal Final Screenshot`, `Legend / Callout
Traceability Missing`, `Implementation Match Proof Missing`, `USER Finding
Ceiling Assumed`, `Codex Independent Evidence Inspection Missing`,
`Branch-Local Visual Overlay Overclaimed As Repo-Wide Governance`, `Visual
Defect Ledger Missing`, and `Visual Target Packet Evidence Missing`.

Routing: a branch-local overlay may repair its own packets, validators,
fixtures, helper registry rows, and active external branch ledgers only inside
the approved carrier. Durable repo-wide enforcement, reusable packet schemas,
shared settings primitives/templates, global helper/fixture gates, and sibling
worktree adoption remain Governance/FAM-002 or owning-FAM follow-up work unless
separately approved.

## Phase Transition Rule

- `Branch Readiness` -> `Branch Planning` only after branch base, branch class, authority record, branch objective, target end-state, complete family-package product planning packet when applicable, project-wide vision alignment, branch-specific vision alignment, product-system concept model, entity/profile model, user workflow model, scale/state planning, expected seam families and risk classes, validation contract, User Test Summary strategy, later-phase expectations, USER critique/decision loop, Codex additional recommendations, and first Branch Planning target are explicit, and no `Branch Readiness Planning Incomplete` blocker remains active unless explicitly USER-waived
- `Branch Planning` -> `Workstream` only after BP1 is accepted or explicitly waived, BP2 is accepted or explicitly waived, BP3 Workstream Entry / Orchestration Validation is green, the admitted Workstream package and entry seam or initial seam sequence are explicit, and no Branch Planning packet, decision-path, vision, plan, or orchestration blocker remains active unless explicitly USER-waived
- `Workstream` -> `Hardening` only after the current Workstream work reports `Completion Status: Green`, every admitted same-branch seam and slice for the current branch is complete, deferred, blocked, or explicitly waived in source truth, no remaining implementable work is still available on that backlog item, `Backlog Completion State` is `Implemented Complete` or `Implemented Complete Except Future Dependency`, direct validation is green, User Test Summary obligations are current for user-facing changes, and no same-slice correctness gap remains
- `Hardening` -> `Live Validation` only after repo-side hardening proof is sufficient for interactive or manual closeout work
- `Live Validation` -> `PR Readiness` only after branch-local proof is sufficient for closeout, returned evidence has been digested into the authority record, and `User Test Summary Results Pending` is absent or cleared by a documented waiver
- `PR Readiness` -> `Release Readiness` only after merge-target canon completeness passes, the Governance Drift Audit passes, the USER-approved next-workstream selection gate passes or a USER-approved next-workstream waiver/defer is explicitly recorded, branch creation remains deferred to `Branch Readiness`, direct GitHub/GitHub-connector verification proves that the live PR is `merged`, and any release candidate anchor/target/scope/artifact truth needed for release review is already available without file mutation
- `Release Readiness` stays restricted to analysis-only release target, scope, artifact, release-execution authorization, and release-state confirmation work; it does not transition into a docs-sync phase or a file-mutation phase

There is no default direct `Branch Readiness` -> `Workstream` transition.
There is no default direct `Workstream` -> `PR Readiness` transition.
If Workstream appears complete, the next normal phase is `Hardening` unless an explicit authority-record waiver says otherwise.

Later phases must not paper over missing earlier-phase requirements.
If a later phase discovers an earlier-phase defect, reopen the branch to the failed earlier phase.

## Phase Definitions

### Branch Readiness

Purpose:

- validate branch base
- declare branch class
- set up or confirm the promoted workstream authority record or branch authority record
- align branch-start canon
- lock execution, validation, and timeout boundaries
- plan the whole branch at phase level before implementation begins

Branch Readiness uses two internal stage gates without changing the canonical phase enum:

- `Branch Readiness Stage 1 - Analysis Gate`: analysis-only; no repository file mutation, branch creation, package admission, docs sync, PR work, release work, selected-next truth, or canon edits are allowed. Stage 1 must output `## Branch Readiness Stage 1 Analysis Packet` for USER review and stop on `Branch Readiness Execution User Approval Missing`.
- `Branch Readiness Stage 2 - Execution Gate`: begins only after explicit USER approval to enter Stage 2. Stage 2 performs approved branch/package admission work, docs sync, branch creation, and authority-record setup only inside the USER-approved FAM/package scope. Stage 2 closeout must clearly distinguish "setup complete" from "implementation approved": it must tell USER that the created/admitted branch is ready for BP1 USER Branch Vision Review, BP2 USER Branch Plan Review, and BP3 Workstream Entry / Orchestration Validation in `Branch Planning`, and that runtime implementation remains blocked until Branch Planning is green or source truth records an explicit USER waiver. When a USER-approved Family Feature Vision exists for the candidate feature category, Stage 2 must load it before final route admission and must not rely on broad Family Vision alone for Feature Vision Context. When the selected feature-bearing route requires Family Feature Vision and none exists or the existing record is shallow, Stage 2 must route to Family Feature Vision planning/admission instead of BP1.

The `## Branch Readiness Stage 1 Analysis Packet` must include governed state markers, FAM/package candidate, package-size review, multiple admitted-slice plan, single-slice drift check, Element Coverage review, `Backlog Taxonomy And Source-Truth Placement Gate:` when the branch proposes or consumes broad AI-native, cache, architecture, policy, experience, runtime-subsystem, capability-pack, new-FAM, new-family-feature-vision, or new-owner concepts, product vision, project-wide vision alignment, family vision alignment, Family Feature Vision alignment or `Family Feature Vision Required For Selected Feature` / `Family Feature Vision Not Applicable` disposition, branch-specific vision alignment, USER vision questions, `USER Vision Question Packet`, Codex product interpretation, Codex implementation recommendation, Codex additional recommendations, USER/ChatGPT review checkpoint, USER critique loop, USER decision ledger, full feature element breakdown, system concept model, entity/profile model, user workflow model, scale/data-volume model, configuration/state model, whole-system interaction map, minimum viable vs full-system boundary, current branch vs future package boundaries, affected surfaces, branch reach, why the branch is large enough, why it should not split into tiny branches, expected user-facing outcomes, acceptance criteria, screenshot and User Test Summary proof expectations, implementation sequence proposal, rejected shallow plan, alternatives/tradeoffs reviewed, open USER decision points, deferred ideas/future-package ledger, validation plan, `Stale Branch Cleanup Plan:`, expected docs sync, blockers and waivers, rollback path, `Branch Readiness Planning Incomplete` blocker review, `Next Legal Phase:` digest field, and the exact Stage 2 green-light decision needed from the USER.

Before the Stage 1 packet recommends USER-selectable candidates, it must include the `BR1 Candidate Viability / Grouping Matrix` from this file. The matrix must prove every recommended option has a concrete feature outcome, implementation-bearing route class, behavior-change classification, support/infrastructure relationship, Family Feature Vision and Deferred Feature Carryforward disposition, grouping recommendation, split reason when not grouped, expected Slice/SLC/seam map, proof path, largest safe coherent package explanation, and tiny-branch sprawl review. Candidate rows that are planning-only, readiness-only, support-only, manifest-only, or too small without a split reason keep the relevant BR1 blocker active.

`Carrier Lifecycle Decision` is required in Branch Readiness Stage 1 for any requested branch/worktree. Stage 1 must classify the carrier with `Carrier Lifecycle Classification:` as exactly one of `Fresh current branch`, `Stale empty local branch`, `Stale branch with unique commits`, `Historical merged branch`, `Wrong carrier/worktree`, or `Active remote/open PR branch`; it must report `Remote Branch State:`, `Unique Branch Diff:`, `Origin/Main Ancestry:`, `Origin/Main Advanced Since Branch Creation:`, `Open PR State:`, `Worktree Checkout State:`, `Recommended Stage 2 Carrier Action:`, `Stale Branch Cleanup Plan:`, `Branch Cleanup Execution Gate:`, `Stable Worktree Path:`, `Replacement Binding Path:`, `Recreate From Current origin/main:`, and `No Unique Commit Loss Proof:`. Stage 1 analyzes only; when it finds a stale empty local branch that is behind `origin/main`, has no unique commits, and has no governing open PR, the recommendation is to create/recreate the fresh carrier from current `origin/main` during Stage 2 rather than silently reusing stale branch identity. Stage 2 must stop on `Stable Worktree Path At Risk` if cleanup would remove a family-stable folder before the replacement branch/worktree is bound there.

`Stale Branch Cleanup Plan:` is required when Release Readiness, PR Readiness, or multi-worktree preflight identified old/stale branches, retired worktrees, or stale GitHub Desktop entries. Stage 1 analyzes only. The cleanup itself belongs to `Branch Readiness Stage 2 - Execution Gate` alongside branch/worktree creation or validation, because every Git repository and GitHub Desktop-bound worktree must keep a valid branch target until the replacement target is ready. If cleanup touches a stable family alias such as a durable FAM worktree folder, `Stable Worktree Path Preservation Gate:` must prove `Stable Worktree Path:` and `Replacement Binding Path:` before cleanup proceeds.

`Post-Release External State Carry-Forward:` is required in Branch Readiness Stage 1 when the previous Release Readiness Stage 2 release has completed and external operational records still point at the just-released branch, PR, release-window, selected-next state, or old source commit. This is a normal BR1 check, not a blocker by itself. Stage 1 must report whether the carry-forward was reconciled during an authorized bounded RR2 closeout or needs an external-owner-selected reconciliation in Branch Readiness Stage 2 before dependent branch/worktree setup or implementation. Any such write requires existing USER authorization for its exact effects; otherwise return the missing decision. It becomes `External Operational State Conflict` only when the external state disagrees with Git/GitHub/repo validation in a way that changes the legal next carrier, requires repo source-truth mutation, requires branch/worktree cleanup, or could authorize stale runtime/FAM/private work.

`Post-Merge Release Readiness Handoff:` is required in Branch Readiness Stage 1 when fetched `origin/main` contains release-bearing merged work after the latest public prerelease, when the current worktree just completed PR2/merge/rebaseline for release-bearing work, or when the requested successor BR1 follows a release-bearing branch merge. BR1 must report whether Release Readiness Stage 1 has run for the current candidate anchor or whether USER explicitly deferred Release Readiness before successor selection. If neither proof exists, BR1 stops on `Post-Merge Release Readiness Decision Missing` or `Release Readiness Handoff Skipped` before recommending successor runtime candidates. This handoff does not execute release, tag, GitHub Release, artifact, issue, cleanup, runtime, provider, private, cache, or memory work; it only prevents successor planning from skipping the file-frozen release-readiness decision point.

`GitHub Issue Relevance Intake Gate:` is required in Branch Readiness Stage 1 for FAM/runtime/product branches, issue-bearing repair branches, re-entering branches after rebaseline/reconciliation, and any branch whose prior USER feedback, UTS return, PR review, GitHub issue, diagnostics flow, or release-window evidence names user-facing defects or requested behavior. BR1 must treat live GitHub issue state as Git/GitHub/helper-derived evidence, not repo source truth, and must classify each inspected issue as exactly one of `Relevant To Current FAM`, `Relevant To Other FAM`, `Cross-FAM`, `Duplicate / Superseded`, `Not Applicable`, `Needs USER Triage`, or `Live State Unknown`. For every issue classified `Relevant To Current FAM` or `Cross-FAM`, the packet must record one disposition: `include in branch scope`, `defer with reason`, `route to another owner`, `block pending USER decision`, or `not applicable with reason`. If the scan cannot run, Codex must say `Live State Unknown` and route the decision instead of inventing issue truth from stale repo docs. `GitHub Issue Relevance Scan Missing`, `Relevant Current-FAM Issue Not Dispositioned`, `Cross-FAM Issue Routing Missing`, `Issue Closeout Live State Unknown`, and `Issue State Treated As Repo Truth` block phase progression when the issue evidence affects branch scope, release scope, USER validation, or public/release closeout.

The issue intake gate is not permission to mutate GitHub. Creating, commenting on, labeling, milestone-changing, closing, reopening, or auto-closing GitHub issues requires explicit USER approval for that exact issue action. Repo docs may preserve durable issue receipts only after the live GitHub state has been checked or the evidence source is named; temporary issue scan evidence belongs in helper output, Codex digest, USER review packets, or `D:\Nexus Desktop AI\Governance State` when source truth permits.

`Issue Candidate Consolidation Gate:` is required before Codex requests GitHub issue creation for RAR, UTS, Live Validation, Branch Readiness, PR Readiness, or user-facing/product defect candidates. Atomic issue candidates remain durable rows with stable IDs, lineage, owner, surface, element group, defect, evidence, disposition, proposed carrier, GitHub mapping state when any, last verified proof, and exact USER decision. Before GitHub issue mutation is requested, Codex must group active atomic candidates by owning FAM, surface, defect class, likely repair carrier, and validation/proof path, then recommend the fewest coherent GitHub issues that preserve traceability. Each group must include `Group ID`, `Group Title`, `Owning FAM`, `Surfaces Included`, `Candidate IDs Included`, `Defect Classes Included`, `Evidence Summary`, `Recommended GitHub Issue Title / Body`, `Proposed Carrier Or Future BR1/BR2 Route`, `Progression Impact`, and USER choices to create issue, map to existing issue, defer to FAM ledger, split, merge, reject, or waive. Grouping is a decision aid, not closure; it must not erase or replace atomic issue-candidate durability. `Issue Candidate Consolidation Missing`, `GitHub Issue Group Without Atomic Traceability`, `Issue Candidate Grouping Too Granular`, and `Issue Candidate Grouping Too Broad` block GitHub issue-creation requests and normal progression when unresolved issue candidates affect the current gate.

The top-level `Merged Vision / Proof Standard Adoption Gate` applies to Branch Readiness and Branch Planning. Branch Readiness must report it when a worktree re-enters after merged Project Vision, Family Vision, Family Feature Vision, UI immersion/window chrome, claim/evidence, proof-strength, Vision-To-Proof, Live Validation, UTS, failure/recovery, or USER-validation standards affect the requested branch. The review is next-legal-gate evaluation only; it must not create repo live-state tracking or authorize cross-worktree mutation.

`Reference Standard Review:` is a carrydown rule inside existing phases, not a new phase. BR1/BR2 must ask whether the selected route needs existing reference standards, whether applicable standards are missing, and whether a missing standard blocks BP1 or can be handled as reference-derived implementation with USER review. BP1 must identify the Reference Standards shaping the branch vision and any missing standard questions. BP2 must explain whether implementation consumes a Shared Primitive, instantiates a Template, derives from an Accepted Reference Set, or needs a USER-approved exception. BP3 must verify the Workstream proof plan against the chosen standards and stop on unresolved reference/template/primitive gaps. Workstream must record Reference Standard gaps instead of silently improvising. Hardening and Live Validation must prove whether the implementation satisfies the applicable reference or route the gap. PR Readiness Stage 1 must review Reference Standard effectiveness, fold down reusable lessons, and create repair/supersession/defer candidates when the reference did not guide an accepted result. When the branch proposes, consumes, supersedes, varies, or depends on a same-class standard, the review must include `Reference Candidate Sync Review:` and report promoted references, same-class external candidates when available, conflict keys, collision status, proposed resolution, USER decision need, and no-candidate-as-canon boundary.

`Future-Proof Implementation Review:` is a carrydown rule inside existing phases, not a new phase. BP2 must define how the accepted feature will support foreseeable same-class additions through derivation rules, state/runtime rules, extension boundaries, and proof expectations. BP3 must verify that Workstream has a proof plan for those rules and future-gated gaps. Workstream must implement from derivation rules rather than screenshot-tuned magic values, or record `Implementation Gap`, `Template Gap`, `Shared Primitive Gap`, `Reference Gap`, `Source-Truth Gap`, `Issue Candidate`, or `Blocked Pending USER Decision`. Hardening must inspect brittle layout/state/proof assumptions, magic pixels, hardcoded one-state behavior, and backend-to-visual truth drift. Live Validation and UTS must prove rendered behavior across relevant states and same-class extension behavior, or elevate unprovable claims to USER validation/waiver. RAR must classify older or re-entering work against this review when merged standards apply. PR Readiness Stage 1 must review whether repeated same-class repairs indicate `Reference Effectiveness Warning` or `Reference Standard Repair Candidate Required`.

Reference Standard lifecycle: `Candidate -> External Candidate Sync -> USER Review -> Promoted Reference -> Consumed By Branch -> Effectiveness Reviewed -> Updated / Superseded / Deferred`. UIREF is the first domain implementation of this lifecycle. New non-UI reference families must not be created without repeated evidence, clear source-truth owner routing, USER promotion approval, and an adoption path. Vision Contracts remain broad product law; Reference Standards are detailed comparators; Templates are USER-approved scaffolds; Shared Primitives are reusable implementation sources. A screenshot, helper output, validator green, external candidate record, aggregate collision report, or branch-local packet is candidate evidence only.

Same-class repair-cycle threshold: `0-1` repair cycles is normal refinement; `2` same-class repair cycles requires a `Reference Effectiveness Note`; `3` same-class repair cycles blocks on `Reference Standard Repair Candidate Required` unless USER explicitly accepts, waives, routes, or defers the risk. Same-class means the repeated repairs involve the same accepted reference, element class, runtime/proof behavior, issue-candidate family, or defect class rather than unrelated implementation details.

Family Feature Vision and Deferred Feature Carryforward BR2 rule:

- `Family Feature Vision` is the durable feature-category layer between Family Vision and Branch Vision Snapshot. When an approved record exists under `Docs/family_feature_visions/`, BR2 must load it before presenting USER-selectable branch options for that feature category.
- `Family Feature Vision Required For Selected Feature` blocks BP1 entry for a selected feature-bearing branch route until the required USER-approved Family Feature Vision exists and passes the `Feature Vision Sufficiency Check`. The next legal phase is Family Feature Vision planning/admission on the current legal carrier, not BP1, when the selected route creates, expands, or depends on a durable feature category that needs more detail than the broad Family Vision can safely preserve.
- `Feature Vision Sufficiency Check` requires branch-consumable durable content: feature purpose, USER-facing surfaces, experience flow, included capabilities, explicit non-goals, dependency/deferred map, design options, proof expectations, Branch Readiness consumption notes, BP1 context notes, fold-down history when applicable, and active-state wording scan. A shallow, generic, copied-list-only, placeholder, or branch-local implementation-only Family Feature Vision does not satisfy BP1 entry and keeps `Family Feature Vision Required For Selected Feature` active.
- `Family Feature Vision Not Applicable` is allowed only for governance-only, release-support, pure helper/validator, source-truth-only, or otherwise non-product branches where no selected product/runtime/user-facing feature category needs a durable middle vision owner. The reason must be stated in BR2 or the branch planning packet.
- If Family Feature Vision planning exposes durable feature ideas, deferrals, surfaces, proof expectations, grouping rules, or routing constraints, Codex must fold those items into the relevant vision owner before BP1 or record a durable deferred disposition. Proposed, unresolved, branch-local, or live operational ideas must not be silently dropped and must not become active branch state in repo vision files.
- BR2 must treat Deferred Feature Carryforward as durable planning preservation, not active branch state. Deferred items are candidates for option evaluation; they do not select a branch, open a PR, set selected-next truth, or authorize implementation by themselves.
- For each USER-selectable BR2 option, BR2 must present an applicability matrix with `Option name`, `Main feature/package objective`, `Applicable deferred carryforward items`, `Reason each deferred item is applicable`, `Dependency trigger that makes the deferred item relevant`, `Recommended grouping`, `Deferred items that remain future-gated`, `Reason future-gated items remain deferred`, and `Validation/proof expectations if the option is selected`.
- If a BR2 option satisfies a deferred item's dependency trigger and shares the same FAM, package objective, owner/worktree, release timing, and validation/proof path, Codex must recommend grouping it into one coherent package rather than splitting it into tiny branches.
- If a deferred item remains future-gated, BR2 must say why: unmet dependency, different Family Feature Vision, different FAM/worktree owner, private/provider/runtime action gate, validation path divergence, release timing divergence, USER decision missing, or unsafe package size.
- BR2 output may use active decision language because BR2 is the dynamic option-evaluation gate. The Family Feature Vision file itself must not store active terms such as `active`, `current branch`, `selected next`, `pending PR`, `in progress`, `next branch`, or release-window status.
- Missing applicable deferred carryforward review blocks on `Deferred Feature Carryforward Review Missing`. Ignoring a relevant deferred item from the selected Family Feature Vision blocks on `Deferred Carryforward Applicability Missing`. Splitting deferred items into tiny branches when dependency and validation proof support one coherent package blocks on `Deferred Carryforward Branch Sprawl`.

Vision Carrydown Contract:

- The governed vision chain is `Project Vision -> Family Vision -> Family Feature Vision -> Branch Vision Contract Snapshot -> BP2/BP3 engineering plan -> Workstream/Hardening/Live Validation proof`.
- Every vision layer must satisfy the product-detail quality bar from its owner: vision contracts describe product outcome, user experience, surfaces, UI/UX expectations, trust/recovery posture, non-goals, and proof expectations, not only file purpose, routing procedure, copied context, or future "define later" placeholders.
- BR1 and BR2 must report which layers apply, which files were loaded, whether a Family Feature Vision exists, whether it is sufficient, and whether any layer is not applicable with a source-truth reason.
- BP1 must digest the applied Project Vision, Family Vision, and Family Feature Vision into a branch-specific vision. BP1 must not invent feature-category direction from branch-local reasoning when the correct Family Feature Vision is missing, shallow, stale, slice-specific, or pointer-stale.
- BP2 must translate the accepted or waived BP1 vision into branch-local Slice/SLC/seam engineering work, proof outputs, rollback, risk controls, deferred-item dispositions, and initial `Vision-To-Proof Matrix` rows. If BP2 changes product direction, user-facing behavior, UI carrydown, surface scope, or deferred/future-gated boundaries, it must route back to BP1 or record an explicit USER waiver before BP3.
- BP3 must verify that the Workstream package implements the accepted or waived BP1/BP2 vision chain, not merely that markers, fixtures, or command outputs are green. BP3 proof planning must classify material claims by `Claim Class:` and `Minimum Proof Strength:`, confirm the expected `Vision-To-Proof Matrix`, and identify what Workstream, Hardening, and Live Validation evidence must fill before implementation is requested.
- Workstream and Hardening must preserve the same selected Family Feature Vision elements, deferred-item decisions, UI/proof expectations, and matrix rows unless source truth routes a revision back to Branch Planning. Hardening must identify missing proof, stale references, weak comparison surfaces, and unobservable claims before Live Validation begins.
- Live Validation must compare observed behavior against the Project Vision, Family Vision, applied Family Feature Vision when present, accepted Branch Vision Contract Snapshot, accepted BP2/BP3 proof plan, and the branch `Vision-To-Proof Matrix`. Helper output, runtime logs, screenshots, videos, markers, manifests, or branch-plan prose cannot clear a product/user-facing claim unless Codex also adjudicates the claim against that vision chain, verifies independent evidence for the claim, records the proof strength actually achieved, records the comparison/reference surface used, or records an explicit waiver/manual-validation requirement.
- USER review packets for BP1, BP2, BP3, Hardening, Live Validation, and UTS handoff must show the applied vision layers, selected/deferred elements, user-facing surfaces, proof gathered, evidence paths, PASS/FAIL/BLOCKED/UNPROVEN disposition, and future-gated scope in a USER-readable way.
- Missing vision-layer proof blocks on `Vision Carrydown Chain Missing`. Branch-local invention while a Family Feature Vision is required blocks on `Branch Vision Invented From Local Reasoning`. Missing Live Validation comparison blocks on `Vision Proof Alignment Missing`. A USER packet that omits the applied vision/evidence mapping blocks on `USER Packet Vision Evidence Missing`. Product-vision files that are mostly procedural, placeholder, slice-route-only, or copied-context-only block on `Vision Contract Product Detail Missing` until repaired or explicitly waived for a non-product branch.

For a genuinely new or materially changed family/package decision, planning must establish the product outcome, current scope and future boundary, affected components, meaningful acceptance proof, ownership, safety and required USER choices. Use the existing plan and evidence owners. Unanswered choices block only the actions that depend on them.

An unchanged admitted Workstream repair carries its accepted plan and proven prerequisites. Review its affected delta; missing historical planning markers, interface packet prose, critique cycles or repeated stage ceremonies alone do not send it back to Branch Readiness. Actual scope, phase, ownership, safety and human-result decisions remain required.

Element Coverage is a non-identity checklist owned by FAM/package analysis only. Coverage categories are user-facing surface, runtime/backend behavior, fail-safe/recovery, security/privacy, voice/audio, external integration, local AI/capability packs, packaging/install, monitoring/HUD, validation, and release impact. Element Coverage rows never count as `Admission State: Admitted`, slices, seams, packages, FAMs, selected-next truth, or release drivers.

Allowed:

- source-of-truth audit
- branch-base validation
- branch-start canon sync
- workstream promotion, branch-record setup, or authority setup
- execution-boundary definition
- branch-level execution planning

Forbidden:

- implementation
- PR material preparation
- release packaging

Required evidence:

- updated `main` truth
- correct execution base
- explicit branch class
- explicit phase block in the authority record
- branch objective and target end-state
- for material new product direction, standard promotion or actual reference collision: applicable vision, impact/collision analysis and actual USER decisions; an unchanged admitted repair carries its accepted direction and relevant delta

- affected-surface mapping and implementation delta classification
- expected seam families and risk classes
- backlog-completion strategy for the whole backlog item, including any known future-dependent blockers
- validation contract and User Test Summary strategy
- expected Hardening, Live Validation, PR Readiness, and Release Readiness needs
- admitted implementation slice or explicit USER-approved docs-only bypass markers
- first Workstream seam or initial seam sequence

Exit:

- branch base is valid
- active workstream authority exists
- exact phase state is recorded
- branch-start canon is coherent
- execution boundary is explicit
- implementation delta class is explicit
- admitted implementation slice is explicit, or an explicit USER-approved docs-only bypass is recorded
- branch-level execution plan is explicit enough to enter Workstream without inventing the lane shape mid-execution
- branch-level closure rule is explicit enough to keep the backlog item on one branch until it is fully implementable and complete or only future-dependent blockers remain
- when later PR Readiness is expected, explicit direct PR verification truth for the future PR gate: target-binding rule, live PR inspection method, Codex Connector approval-latch rule, concise revalidation-comment rule, same-PR repair authority, merge/close verification method, and watcher-exception posture. Watcher-based bot monitoring is not default PR2 behavior; it requires a separate USER-approved watcher exception before `PR Watcher Provisioning Unproven` or `PR Watcher Routing Unverified` can become active blockers.

### Branch Planning

Purpose:

- obtain USER-facing branch vision acceptance before engineering planning
- obtain USER-facing branch plan acceptance before orchestration validation
- prove the accepted plan is ready for Workstream implementation
- preserve branch-size law and Slice/SLC traceability without creating sprawl branches

Branch Planning uses three internal stage gates without changing the canonical phase enum:

- `BP1 - USER Branch Vision Review`: uses `USER_BRANCH_VISION_REVIEW.md` to present Project Vision Context, Family Vision Context, Feature Vision Context, Branch Goal, End-State Vision, user-facing behavior, surface map, design options, Codex recommendations, USER response, Codex digest, accepted Branch Vision, deferred/future-gated ideas, question queue, design assumption ledger, and acceptance/revision/rejection/waiver status. BP1 cannot begin while `Family Feature Vision Required For Selected Feature` is active. When a USER-approved Family Feature Vision exists, `Feature Vision Context` must digest that file and its Deferred Feature Carryforward instead of inventing feature direction from branch-local reasoning. The BP1 artifact must be substantive and branch-specific: it digests source-truth context into an applied branch vision, explains what USER will see/review/decide/rely on, names real design options and tradeoffs, asks decision-driving questions, and cannot pass as a template shell, copied-file list, generic options list, or marker-only packet.
- `BP2 - USER Branch Plan Review`: uses `USER_BRANCH_PLAN_REVIEW.md` to present the engineering plan derived from accepted or waived BP1, including package summary, branch scope size test, Slice/SLC/seam plan, affected surfaces, likely files, validators/helpers, proof requirements, Element-to-Phase Proof Matrix, Runtime Observability Decision Matrix when applicable, claim/evidence matrix, Vision-To-Proof Matrix, exact normal USER desktop runtime launcher proof plan, launcher parity proof plan if troubleshooting may substitute, photo/video proof plan, manual USER validation plan, H1 expectations, LV/UTS expectations, rollback/safety plan, risks, future-gated boundaries, and exact BP3 approval text. The BP2 artifact must translate the accepted BP1 vision into a branch-specific engineering contract with scope, slice-level deliverables, seams, proof outputs, risk controls, rollback/reversibility posture, options, tradeoffs, and Codex recommendation; it must preserve the BR2/BP1 disposition of applicable deferred carryforward items and cannot merely repeat BP1, list markers, or point USER at copied files. The claim/evidence matrix and Vision-To-Proof Matrix must name `Accepted Vision Source:`, `Accepted Requirement:`, `Claim Class:`, `Minimum Proof Strength:`, `Evidence Class:`, `Expected Independent Evidence:`, `Reference Surface / Baseline:`, `Known Limitation:`, and `Manual USER Validation / Waiver Path:` for every material product, runtime, UI, security/privacy, failure/recovery, helper/validator, external-live-truth, or subjective USER claim.
- `BP3 - Workstream Entry / Orchestration Validation`: proves BP2 correctly implements BP1, proves package size and Slice/SLC traceability, verifies affected files, validators, helper updates, H1/LV/UTS/rollback/proof paths, validates runtime observability and exact-launcher/photo-video/manual-validation planning when applicable, preserves future-gated boundaries and deferred-item dispositions, and returns bounded Workstream implementation approval for the admitted same-branch package only when BP1 and BP2 are accepted or explicitly waived and BP3 validation is green. The BP3 artifact must name the entry seam or initial seam sequence and must be a substantive orchestration-readiness contract with scope, implementation order, validation/proof plan, rollback posture, drift controls, unresolved USER decisions, blockers, and a go/repair/blocked recommendation; it cannot rely on helper-green hygiene or first-seam-only readiness.

Allowed:

- USER-facing vision and plan packets
- external operational state updates for active branch planning
- source-truth fold-down needed to represent accepted USER decisions
- helper, validator, fixture, and packet repairs needed to make Branch Planning self-validating
- exact bounded Workstream package implementation approval text, including the entry seam or initial seam sequence, when BP3 is green

Forbidden:

- runtime/code implementation
- treating SLCs/slices as automatic separate branches
- using Workstream for planning, Hardening planning execution, Live Validation execution, PR creation, merge, release execution, private/provider/runtime/cache/memory setup, or branch cleanup
- approving implementation while BP1 or BP2 is pending, stale, missing, rejected, or unwaived
- treating BP1, BP2, or BP3 packet generation, stale-language hygiene, marker validation, copied-file lists, helper PASS output, or ZIP consistency as substantive USER review content or USER gate acceptance

Required evidence:

- accepted or explicitly waived BP1
- accepted or explicitly waived BP2
- BP3 orchestration validation with the admitted Workstream package and entry seam
- Slice/SLC traceability from BP1 accepted branch vision requirements to BP2 branch plan line items
- current USER review content with exactly one primary current-gate decision file when USER review is required, delivered through the external USER lifecycle owner to the approved collection and evidence set with selected-evidence ZIP parity and current delivery proof while review is pending; completed gates use retained review evidence and acceptance/waiver disposition without requiring retired transport
- packet decision-path consistency and unresolved-placeholder absence
- substantive BP1/BP2/BP3 USER review artifacts that contain applied branch-specific vision, plan, or orchestration content rather than template instructions, copied-file manifests, generic recommendations, or broad non-decision-driving USER questions

Exit:

- BP1 accepted or explicitly waived
- BP2 accepted or explicitly waived
- BP3 green
- admitted Workstream package and entry seam or initial seam sequence are explicit
- implementation approval text preserves all pending USER action gates

### Workstream

Workstream executes the approved outcome, including code, source documentation, installation and runtime work as applicable. Carry accepted planning and qualified evidence forward. Record the implemented delta and perform checks affected by it. One coherent deliverable is valid.

Keep scope, ownership, protected state, rollback, required proof and applicable human/UTS results explicit. Do not silently cross to Hardening, Live Validation, PR/release work or another protected action. A fresh BP packet, docs-only bypass, seam diary or continuation latch is not required solely for continuing an unchanged approved objective.

Exit requires the approved deliverable and affected verification, truthful unresolved/deferred work and the applicable phase/human-result prerequisites. It does not accept future work or an unseen result.


### Hardening

Purpose:

- pressure-test the current branch truth
- stabilize defects, seams, validators, or harnesses before closeout

Allowed:

- validators
- harness work
- runtime helper work
- small supporting evidence infrastructure
- bounded corrective fixes

Forbidden:

- unrelated feature work
- new lane selection
- release packaging

Required evidence:

- validator results
- runtime results when relevant
- plan-vs-vision comparison when a Branch Vision Contract Snapshot is required
- `Vision-To-Proof Matrix` proof-gap review for material accepted requirements, including missing observed runtime evidence, missing comparison/reference surfaces, weak proof strength, circular evidence, unobservable claims, and USER validation/waiver routing
- `Pre-Live Visual Purpose Conformance Gate` review for visible user-facing surfaces when UI/UX, window, control, or interaction claims are in scope: before Live Validation begins, Codex must inspect photo/video or ordered-frame evidence against the accepted Project Vision, Family Vision, Family Feature Vision when present, Branch Vision Contract Snapshot, BP2/BP3 proof plan, UIREF/reference/template/shared-primitive rules, and the window or surface purpose. The review must inventory visible element groups, compare shared primitives to the admitted reference set, classify each row as `PASS`, `REPAIR`, `BLOCKED`, `UNPROVEN`, `WAIVED_WITH_REASON`, or `Not Applicable With Reason`, and route any non-green unwaived row to repair, issue candidate, waiver, or blocker before Live Validation functional proof.
- deterministic visual verdict language: `better`, `closer`, `improved`, `looks acceptable`, `seems green`, `good enough`, or equivalent subjective progress language is not a green verdict. A row is green only when it is explicitly `PASS`, `WAIVED_WITH_REASON`, or `Not Applicable With Reason` with cited photo/video evidence or legal USER validation/waiver evidence.
- Future-Proof Implementation Review for brittle layouts, magic pixels, hardcoded assumptions, one-state/default-size-only proof, missing extension boundaries, future scope implemented by inference, and backend-to-visual truth drift
- `Reference Candidate Sync Review` when the branch proposes, consumes, varies, supersedes, or depends on same-class Reference Standards, Templates, Shared Primitives, accepted comparators, token rules, geometry rules, visual grammar, control-state behavior, backend behavior, proof standards, naming rules, or applicability rules. Hardening must report promoted-reference check, admitted external candidate/collision check when available, conflict key, collision status, proposed resolution, USER decision need, and no-candidate-as-canon boundary.
- explicit distinction between product defects, harness defects, environment issues, and canon or contract drift

Exit:

- branch-local hardening gate is green
- no unresolved first-failing seam remains
- no truth-drift contradiction remains
- no unwaived `Vision-To-Proof Matrix` row remains `REPAIR`, `BLOCKED`, `UNPROVEN`, or missing a legal Live Validation / USER validation path
- for visible user-facing work, no unwaived `Pre-Live Visual Purpose Conformance Gate` row remains `REPAIR`, `BLOCKED`, `UNPROVEN`, missing, or supported only by screenshot existence, helper output, runtime marker, DOM marker, code assertion, or unadjudicated photo/video evidence

### Live Validation

Purpose:

- prove the user-facing or operator-facing branch truth through interactive, manual, or launched-process evidence
- digest that evidence into canon

Allowed:

- interactive validation
- manual validation digestion
- UI audit when relevant
- validation-only support changes if the branch reopens to `Hardening` first

Forbidden:

- new implementation
- PR packaging
- behavior widening without reopening earlier phase

Required evidence:

- required interactive or manual evidence
- required UI audit evidence when applicable
- `Pre-Live Visual Purpose Conformance Gate` evidence when visible user-facing UI, window, control, visual state, layout, or interaction-surface claims are in scope. The gate proves that the surface looks like the accepted vision/purpose contract requires before Live Validation proves that it functions.
- exact normal USER desktop runtime launcher proof for desktop/user-facing behavior, or explicit USER waiver with reason
- troubleshooting launcher proof may substitute only with USER consent and `Launcher Parity Proof: PASS`
- photo/video or ordered frame-sequence proof for every visible USER-facing closeout claim, or USER-elevated manual validation/waiver when photo/video cannot prove the claim
- runtime log, Dev Toolkit, manifest, screenshot/video, interaction-matrix, and raw-evidence references in the USER packet when those artifacts support Live Validation
- row-by-row `Vision-To-Proof Matrix` verdicts that compare observed runtime behavior, screenshots/videos, logs, helper output, markers, manifests, and interaction evidence against the accepted Project Vision, Family Vision, Family Feature Vision when present, Branch Vision Contract Snapshot, BP2/BP3 proof plan, and reference surfaces; evidence artifacts are inputs until compared and adjudicated
- Future-Proof Implementation Review evidence for relevant same-class additions, extension boundaries, current/future-gated split, state coverage, and magic-value or brittle-layout disposition when the visible or operator-facing claim depends on those qualities
- vision-vs-observed-behavior comparison across the applied Project Vision, Family Vision, Family Feature Vision when present, accepted Branch Vision Contract Snapshot, and accepted BP2/BP3 proof plan, or an explicit waiver when a Branch Vision Contract Snapshot is required
- ordered proof sequencing: first visual-purpose conformance from recorded evidence, then functional behavior and interaction proof. A successful click, runtime event, log entry, marker, or helper PASS cannot compensate for an unproven or failing visual-purpose row; conversely, a visually conforming surface still requires functional proof for admitted actions, state changes, and recovery paths.
- evidence digestion into the authority record

Exit:

- required interactive or manual evidence is green
- required UI audit exists when applicable
- required `Pre-Live Visual Purpose Conformance Gate` rows are `PASS`, `WAIVED_WITH_REASON`, or `Not Applicable With Reason` before any UTS handoff. Missing visual-purpose rows, non-green unwaived rows, or rows supported only by unadjudicated screenshots/videos block Live Validation exit and must route to bounded repair, USER waiver/manual validation, issue candidate, or source-truth blocker.
- subjective visual-progress language such as `better`, `closer`, `improved`, `looks acceptable`, or `good enough` is not a Live Validation exit state and must be treated as `REPAIR` unless converted to an explicit source-truth-supported `PASS`, `WAIVED_WITH_REASON`, or `Not Applicable With Reason` row.
- exact normal USER desktop runtime launcher validation is passing or explicitly waived for desktop/user-facing behavior
- troubleshooting launcher equivalence, when used, has USER consent and launcher parity proof
- photo/video proof is adjudicated for visible claims, and any unphotographable required claims have returned USER manual validation marked `PASS` or an explicit `WAIVED_WITH_REASON`; a pending `Manual USER Validation Required` route blocks Live Validation exit, UTS handoff, PR Readiness green, and Release Readiness green
- required user-facing desktop shortcut validation is `PASS` or explicitly `WAIVED` before User Test Summary handoff; `User-Facing Shortcut Validation Pending` must not remain active
- returned evidence is digested into canon
- every material `Vision-To-Proof Matrix` row is `PASS`, `WAIVED_WITH_REASON`, or `Not Applicable With Reason`; `Manual USER Validation Required` is a routing/blocker state and cannot satisfy Live Validation exit until converted by returned USER evidence to `PASS` or `WAIVED_WITH_REASON`; no material row remains missing, `REPAIR`, `BLOCKED`, `UNPROVEN`, `Manual USER Validation Required`, or supported only by unadjudicated evidence artifacts
- required User Test Summary results are `PASS` or explicitly `WAIVED`; `User Test Summary Results Pending` must not remain active
- no unresolved validation contradiction remains

### PR Readiness

Purpose:

- first determine whether the branch is package-ready for PR creation without leaving merged canon stale and with the next lane already locked
- then validate the created PR as the actual merge candidate before reporting PR Readiness green

Allowed:

- readiness review
- merge-target canon sync
- final drift checks
- next-workstream confirmation
- successor-branch absence verification
- Branch Readiness branch-creation deferral
- Governance Drift Audit
- PR material preparation
- PR creation
- PR state validation

Repo-wide governance or workflow-policy repairs discovered during Branch Readiness or PR Readiness require an explicit package/carrier decision before Codex edits files unless that repair was already part of the approved package. The decision must classify the repair, identify the cleanest carrier, state what current authorization covers, list pending USER decisions, name any stop/report condition, and either record why the current branch may legally carry the repair or stop with the exact USER decision needed for a separate carrier. Small tightly coupled repairs may ride the current legitimate carrier only when the current phase authorization covers them, source truth records the carrier decision, and the repair does not expand runtime/product scope.

Forbidden:

- implementation
- hardening
- release tagging
- skipping governance drift review
- reporting PR Readiness GREEN before PR creation and PR validation

Required evidence:

- branch-local proof complete
- validation adequacy review complete under `Docs/validation_helper_registry.md`: helper/validator PASS/GREEN output supports the decision but does not replace Codex responsibility, source-truth review, changed-file inspection, review-bundle freshness, phase-scope checks, or USER-approved acceptance criteria
- accepted vision and accepted branch plan satisfied, revised, waived, or folded down with explicit receipt when a Branch Vision Contract Snapshot is required
- required user-facing desktop shortcut validation digested, passing or explicitly waived, and no `User-Facing Shortcut Validation Pending` blocker
- required User Test Summary results digested, passing or explicitly waived, and no `User Test Summary Results Pending` blocker
- merge-target canon completeness gate passed
- when selected-next truth is explicitly in scope, next workstream selected, canon-defined, assigned valid record state, minimally scoped, and explicitly not branched yet
- when selected-next truth is explicitly in scope, successor branch creation deferred to `Branch Readiness`
- post-merge truth fully encoded before merge
- Governance Drift Audit completed
- docs sync complete and validator-aligned
- inclusion-only `## PR Creation Details` operator copy blocks prepared, plus standardized `## Next Branch` response block only when selected-next truth is explicitly in scope or Branch Readiness is the next legal phase
- clean worktree with required branch truth durable in commit history
- GitHub PR created for the current head branch and intended base branch
- PR exists, is open, non-draft, conflict-free, and inspectable
- PR state matches merge-target canon
- unresolved Codex comments/issues and requested changes are absent or resolved
- branches that still rely on branch-authority truth merge with historical or removed branch-authority truth rather than lingering as active branch owners on `main`
- no active seam
- no unresolved blocker that should have been repaired on the current branch before merge
- no validator/helper result was accepted or patched by inertia; any failed, blocked, red, or suspiciously green helper result was diagnosed as source-truth drift, product/runtime defect, environment/configuration issue, USER decision need, or proven helper defect before repair

Exit:

- PR exists and is validated as ready for merge review
- or returned to the failed earlier phase with explicit blockers

### Release Readiness

Purpose:

- determine whether merged or merge-ready truth is ready for release packaging

Allowed:

- release review
- release notes, tag, title, and release package information
- version or tag recommendations
- final release-candidate verification
- release-state confirmation immediately after release execution

Forbidden:

- implementation
- broad canon-sync mutation that should have been completed before PR green
- hidden fix work
- hidden next-lane planning
- branch-authority cleanup that should have been merge-safe in PR Readiness
- stale/old branch deletion, worktree removal, branch switching, or GitHub Desktop-bound worktree cleanup; Release Readiness may record `Branch Cleanup Plan:` and `Branch Cleanup Execution Gate:` only
- between-branch canon repair
- source, docs, canon, validator, helper, release-note, or handoff-file mutation

Required evidence:

- merged or legitimately merge-ready truth
- public release language translates accepted user-facing vision/scope and excludes future-gated vision items when a Branch Vision Contract Snapshot is part of the release window
- `Release Candidate Anchor:`, `Release Candidate Anchor Source:`, `Target Commit:`, `Historical Endpoint Handling:`, and `Candidate Includes Later Governance Repairs:` for the selected release candidate
- `Release Ownership Model:`, `Release Window Contributors:`, `Merged-Unreleased Scope Inventory:`, `Last Runtime PR:`, `Post-Runtime Governance Repairs:`, and `FAM Contributor Routing:` for the selected release candidate
- explicit `Release Target:`, `Release Floor:`, `Version Rationale:`, `Release Scope:`, and `Release Artifacts:` markers for release-bearing branches
- or explicit `Release Branch: No` only for preserved historical records
- release-context verification
- clean tracked-file state; source changes return to the owning pre-merge product phase or a separately approved repository interface carrier; operational Governance changes route externally
- no unresolved blocker

Exit:

- ready for release packaging
- or returned to the failed earlier phase with explicit blockers

### Post-Release External Operational State Carry-Forward

After Release Readiness Stage 2 publishes a GitHub prerelease and post-publish release/tag/body/health validation is green, external operational records that still point to the just-closed branch, PR, release window, selected-next state, or previous source commit are normal carry-forward, not a Release Readiness blocker, when Git/GitHub/repo validators prove the release is published and merged repo source truth is already aligned.

The installed external owner may select a bounded RR2 carry-forward reconciliation only when existing USER authorization covers its exact effects; otherwise return the missing decision. The operation may update only its explicitly approved targets under `D:\Nexus Desktop AI\Governance State` against live Git/GitHub/repo evidence. It must not mutate repo source files, create branches or PRs, merge, release again, clean branches or worktrees, or touch FAM/runtime/private/provider/cache/memory surfaces.

If not reconciled during RR2, Branch Readiness Stage 1 must report `Post-Release External State Carry-Forward:` as a normal check and any necessary Branch Readiness Stage 2 reconciliation must be selected by the installed external owner and covered by existing USER authorization for its exact effects before dependent setup or implementation; otherwise return the missing decision. It becomes `External Operational State Conflict` only when the stale external state conflicts with Git/GitHub/repo validation, changes the legal next carrier, requires repo source-truth mutation, requires branch/worktree cleanup, or could permit runtime/FAM/private work from stale authority.

## Thread Launch / Write-Target Identity Lock

Before meaningful repo work, file mutation, phase entry, branch/worktree creation, commit, push, PR creation, release action, runtime validation, shortcut mutation, provider/model installation, or GitHub Desktop handoff, Codex must verify the active chat lane, local workspace path, git root, branch, upstream, `HEAD`, `origin/main`, `git worktree list`, clean state, worktree role, expected phase/seam, and intended write target.

When relevant, the lock must also verify runtime/process ownership and GitHub Desktop folder binding.

Assigned parallel worktree mode is allowed when USER explicitly assigns different Codex threads to different active branch worktrees. The default limit is two active branch worktrees. Each assigned worktree must have one owning thread, one branch, one write target, one worktree ownership ledger, one intended write set, and one source-truth owner set. A third active branch worktree, unknown active thread owner, unknown write target, missing worktree ownership ledger, same-worktree/same-branch collision, dirty-worktree ownership ambiguity, or overlapping same-file/source-truth-owner mutation is `Parallel Worktree Coordination Missing` until USER routes the work.

An assigned thread may also be in `Waiting For Updated Main` posture. This is valid when that thread is in Release Readiness analysis, Branch Readiness Stage 1 analysis, or another file-freeze analysis state and is waiting for a different branch to merge before creating or continuing its branch. A waiting thread is not an active mutation carrier; it must remain read-only, must not create a branch from stale source truth, and must rerun preflight after `origin/main` updates.

Before mutation in assigned parallel worktree mode, each thread must report:

- assigned thread / worktree owner
- Active Thread Owner:
- Thread Assignment Status:
- Worktree Ownership Ledger:
- Intended Write Set:
- Same Worktree / Same Branch Collision Check:
- Dirty Worktree Collision Check:
- Dirty Worktree Recovery Packet:
- Off-Worktree Work Routing:
- Governance Routing Barrier:
- New Worktree Decision Gate:
- expected path, git root, branch, upstream, `HEAD`, and `origin/main`
- worktree role and phase/seam
- intended write target and source-truth owner
- changed-file set and shared-file overlap forecast against the other active worktree
- clean/dirty state, ahead/behind state, merge forecast, and open PR state
- runtime/process ownership and interactive validation ownership
- Git operation ownership
- GitHub Desktop binding when Desktop is used
- waiting status if the assigned lane has no created branch yet and is blocked on updated `origin/main`

Only one related Git operation should run at a time where practical, and only one interactive desktop validation may run at a time. If a branch needs a shared source-truth file already being edited by the other assigned worktree, or if two Codex threads target the same worktree/branch, stop and surface the coordination decision before patching.

If the active folder, branch, upstream, worktree role, phase/seam, write target, runtime/process owner, or GitHub Desktop binding does not match the requested work, `Thread / Worktree Identity Mismatch` blocks entry and Codex must return a routing packet instead of mutating files.

The routing packet must include expected workspace, actual workspace, expected branch, actual branch, expected write target, actual write target, expected phase/seam, actual repo state, mismatch evidence, and safest next correction.

Prompt-Ingress Lane Lock:

- Before Codex follows an attached prompt, pasted prompt, referenced file, generated prompt, automation instruction, heartbeat instruction, or ChatGPT review prompt that names a worktree, family, branch, repository path, packet path, or USER hub label, Codex must classify the requested target lane from the prompt text and attachment metadata before changing directories, loading that target lane's source truth, running helpers, fetching branch-specific state, generating packets, mutating external state, or executing commands in that target lane.
- The prompt-ingress target classification must compare `Requested Worktree / Family / Branch / USER Label:` against the current assigned thread/worktree binding and report `Prompt-Ingress Lane Lock:` in the identity packet when the prompt names a lane.
- If a FAM-006-bound thread receives a FAM-007 prompt, a FAM-007-bound thread receives a FAM-006 prompt, a Governance-bound thread receives a product-FAM execution prompt, or any assigned thread receives a prompt for a different worktree/family/branch, Codex must stop on `Prompt-Ingress Lane Mismatch` before cross-worktree source loading or commands. The only allowed actions before USER routing are identity proof in the currently assigned worktree and a routing packet.
- A prompt, attachment, packet title, or ChatGPT analysis that says "You are Codex operating in" another worktree is evidence of a requested lane, not authority to switch lanes. Switching, inspecting for execution, or mutating the other lane requires a current explicit USER lane-switch/worktree-escape decision that names the expected root, target root, branch, allowed command/file classes, read/write mode, expiration or stop condition, validation, and return path.
- Read-only cross-worktree analysis remains allowed only after the mismatch is reported and only when the assigned-lane source truth or USER approval requests analysis of the sibling lane as context. It must not become branch-specific source loading, packet generation, helper execution, Git mutation, external-state mutation, or sibling-worktree repair by inertia.

If the requested work belongs outside the assigned worktree, outside the active branch scope, or to another active lane, Codex must stop on `Governance Routing Barrier` and route the packet to the current external Governance owner. That owner decides whether the work belongs to the current owner, an existing worktree/thread, a new worktree/thread, or a USER waiver. New worktree/thread creation, activation, reassignment, and GitHub Desktop repo binding remain blocked on `New Worktree Decision Gate` until USER approves the exact path, branch, owner, and validation route.

### Assigned Worktree Confinement

Assigned Worktree Confinement is mandatory once a thread is assigned to a specific worktree. The thread must treat that worktree root as its boundary for repo mutation, branch operations, runtime launch, shortcut mutation, provider/model install, PR work, release work, and GitHub Desktop handoff.

Codex App Thread Worktree Guard Rule:

- Rule Name: `Codex App Thread Worktree Guard`
- Owner: current external `policy/POLICY.md`; repository mirrors preserve only product-facing confinement interfaces
- Applies To: Codex App threads, local Codex hook policy, assigned worktree preflight, branch/worktree mutation, Git operations, packet generation, helper execution that writes files, external-state mutation, and GitHub Desktop handoff
- Required State: a Codex App thread that is assigned to a worktree must bind mutation authority to the assigned Git root/worktree, not to the exact branch. The thread may switch or create branches inside that assigned worktree only when normal source truth and USER approvals allow it. The thread may inspect sibling worktrees read-only for audit, overlap, rebaseline, or routing analysis. It must not mutate a sibling worktree, parked worktree, neutral main, external operational state, or USER-local Codex state unless the current phase and USER approval explicitly admit that target.
- Allowed Values: `Assigned Root Mutation Allowed`, `Read-Only Cross-Worktree Analysis`, `First Binding Requires USER Confirmation`, `Worktree Escape User Waiver Granted`, `External Hook State Only`, `Reference Hook Template Only`
- Invalid Values: `Mutate Any Worktree From Current Thread`, `Governance Mutation From Non-Governance Worktree`, `Sibling Worktree Packet Generation`, `Sibling Worktree Git Operation`, `External Lock Ledger In Repo Docs`, `Hook Installed By Repo Patch`, `Branch-Specific Lock Only`
- Blocking Condition: `Codex Thread Assigned Worktree Mismatch`, `Worktree Escape User Waiver Missing`, `Governance Worktree Mutation From Non-Governance Root`, `Codex Hook Live State In Repo`, or `Thread First Binding Unconfirmed` blocks mutation when the assigned root is missing, current root differs from assigned root, a non-Governance thread attempts Governance-owned mutation, live hook/lock/audit state is being committed as repo truth, or an existing thread has not reported its first binding before mutation.
- Repair Owner: assigned thread for preflight/reporting; the approved external source carrier for operational policy repair; USER for first-binding confirmation, worktree escape waiver, hook installation, live lock storage, or local Codex configuration mutation.
- Repair Path: verify the exact assigned source root, target root, branch, and current approved write set. Continue useful read-only analysis while resolving a collision. Mutation resumes only on the USER-approved product or external source carrier, or after genuinely new cross-root authority is granted.
- USER Decision Required: required before installing or modifying `C:\Users\anden\.codex\hooks.json`, local hook scripts, thread lock files, waiver files, audit logs, external operational state schemas, sibling worktree files, neutral main files, or any reference hook template/code in the repo.
- Validation Owner: current external operational policy and selected material confinement tests. Legacy marker-first repository checks are historical compatibility evidence, not activation gates for their replacement.
- Final Disposition: the external Control Plane owns operational hook policy and source; installed hook, lock, waiver and audit records remain external operational state. Repository files retain product-facing interfaces only.

Every assigned branch authority record must carry:

- Assigned Worktree Confinement: Required
- Active Thread Owner:
- Thread Assignment Status:
- Worktree Ownership Ledger:
- Intended Write Set:
- Same Worktree / Same Branch Collision Check:
- Dirty Worktree Collision Check:
- Dirty Worktree Recovery Packet:
- Off-Worktree Work Routing:
- Governance Routing Barrier:
- New Worktree Decision Gate:
- Expected Worktree Root:
- Actual Worktree Root:
- No Cross-Worktree Mutation: Required
- GitHub Desktop-bound worktree:
- Worktree Escape User Waiver: Granted only when USER explicitly names the expected root, actual root, target root, allowed commands/files, expiration or stop condition, required validation, and return path
- Worktree Escape User Waiver Missing: Blocks mutation, branch/worktree changes, runtime launch, shortcut/provider/model actions, PR/release actions, and GitHub Desktop handoff outside the assigned worktree

Read-only identity checks may inspect `git worktree list`, remotes, branch names, dirty-file inventory, and GitHub Desktop binding evidence from the assigned root. Any write, branch switch, cleanup, runtime launch, shortcut edit, or helper execution against a sibling worktree or parked clone is `No Cross-Worktree Mutation` scope and must stop on `Worktree Escape User Waiver Missing` unless the USER grants the waiver in clear text.

Dirty worktree collision recovery is mandatory when a target worktree is dirty before a new owner claims it. Freeze mutation, inventory dirty files, identify which thread owns each file, preserve or discard only with USER approval, and resume with exactly one active owner recorded in the worktree ownership ledger.

Off-worktree work routing is mandatory when a branch thread discovers work that does not belong to its assigned worktree or active branch. The discovering thread reports the issue, expected/actual identity, dirty-file risk, likely owning lane, and recommendation, then waits. It must not self-activate a sibling worktree, take over another active thread's branch, or create a new worktree by convenience.

Before Stage 2 execution, phase entry, branch/worktree creation, commit, push, PR work, release work, runtime validation, or GitHub Desktop handoff, the active thread must prove the assigned-worktree contract under the current external operational owner. Bind every command to the exact approved target; verify root, branch, HEAD, upstream, dirty scope, owner and intended effects, and stop on foreign ownership or unapproved cross-worktree mutation. Retained `--worktree-confinement-gate` examples describe historical coverage and do not select the current implementation.

### Family-Scoped Branch Readiness Confinement

Family-scoped Branch Readiness must keep the requested family and worktree as the selector. The active branch record must name `Target Family:` and `Sibling Worktree Candidate Exclusion:` before Stage 2 mutation. Sibling worktrees are overlap context only; they are not successor authority, selected-next authority, or a reason to switch lanes unless USER explicitly broadens the task to repo-wide branch selection.

If a sibling worktree appears to have an active branch, cleaner validation state, or a tempting next phase, the assigned thread must report it as overlap/reconciliation context only. If current source truth truly conflicts with the requested family/worktree, stop on `Family-Scoped Branch Readiness Drift` and return the routing conflict instead of recommending or entering the sibling branch.

Stale parked branches, old worktrees, fallback folders, AI Lab context, deleted/recreated historical refs, and unknown write targets are stop conditions until USER explicitly routes the work to a legal target.

## Repo-Level State: No Active Branch

`No Active Branch` means no runtime, implementation, release-packaging or repair lane is selected for normal product work. External Governance work has separately approved operational authority; it does not require a standing product-repository branch exception. Retained standing-intake records are historical context, not active authority.

Use it when:

- the repo-level admission gate is failing
- merged canon drift remains unresolved
- release handling remains unresolved and USER has explicitly waived/deferred selected-next branch/workstream truth
- the only available implementation branch is stale, merged, or identical to `main`
- no branch should open yet by inertia even though repo truth is otherwise stable

`No Active Branch` may be:

- blocked:
  - a blocker or repair path must be cleared before the next implementation lane may begin
- steady-state:
  - no implementation branch is currently selected, and it is valid for the next safe move to be no branch at all until a new approved need exists. PR Readiness may project steady-state `No Active Branch` when no USER-approved selected-next truth exists; it must not invent selected-next truth or create a successor branch by inertia. The next runtime implementation pipeline is selected later through Branch Readiness Stage 1 from current `origin/main`, external operational state, vision, current completed work, and implementation need.

When `No Active Branch` is blocked:

- do not recommend a later branch phase
- do not start next-lane implementation
- report the blocker and the exact repair path instead

When `No Active Branch` is steady-state:

- do not start the next implementation branch by inertia
- it is valid for `Next Safe Move` to say explicitly that no branch should open yet
- a release packaging branch may still enter `Branch Readiness` if its branch-class admission rules pass
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.
- repository branch records remain durable or historical pointers, not current external authority; no active product selection is implied by a separately approved external sandbox

## Standing Governance Intake Branch

The former product-repository standing intake branch and its `RRI-*` receipts are historical migration and handoff evidence. They are not the default repair carrier or an active operational policy owner.

Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.

An external repair preserves the exact originating task/worktree identity and reports its material outcome without requiring a product PR merely to carry operational Governance changes. Installing an external candidate is a separate USER-approved activation; repository product/interface changes retain their own approved route.

Do not mutate historical intake receipts, retire their worktree, select a runtime successor, or infer push, PR, merge, release, live authority, or retained-storage deletion from this source-routing rule.

## Governance Intake Triage And Digest Profiles

Use the current external policy owner for operational Governance intake and validation. A bounded source repair needs a concrete problem, approved scope, legal carrier, material tests, and an explicit activation boundary; it does not need a new intake framework.

Return the smallest complete decision packet containing outcome, exact scope and identity, material evidence, unresolved blockers, requested USER action when genuinely required, and next legal step. Preserve requested review detail; do not duplicate historical payloads, marker catalogs, or full transcripts as a completeness ritual.


## Exception Path: Post-Release Canon Repair

Purpose:

- classify escaped canon drift after a release without turning Release Readiness into a mutation phase or using `main` as a work surface
- keep external operational state carry-forward separate from durable repo canon drift

Allowed:

- read-only drift analysis on `main`
- blocker annotation when drift is discovered after merge
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.
- repair in the next approved Branch Readiness Stage 2 canon/governance carrier when release publication has completed and protected `main` prevents post-release canon closure from landing directly

Forbidden:

- treating post-release analysis as permission to mutate repository files inside Release Readiness or on main
- treating normal post-release external operational state carry-forward as durable repo canon drift or as a Release Readiness blocker when Git/GitHub/repo validation is green
- using post-release repair instead of the merge-target canon completeness gate
- turning the repair path into a new implementation lane by accident
- opening an unapproved carrier or importing operational Governance source into a product/runtime carrier
- treating a local-only post-release closure commit as completed source truth
- using Release Readiness as a broad docs-sync phase
- mutating `main`

Required evidence:

- updated `main`
- latest release truth
- explicit canon drift
- explicit reason the drift could not be prevented before merge or release
- Route operational Governance source repairs to the approved external carrier under `Docs/governance_efficiency_operating_model.md#source-truth-authority-hierarchy`; keep product changes and repository interface patches on their separately approved repository carrier.
- if protected-main release closure is the blocker, explicit legal repair surface: the next approved Branch Readiness Stage 2 canon/governance carrier that carries the closure into remote source truth

Exit:

- canon aligned to released truth
- remote source truth contains the post-release closure, not only a local commit
