# Workstream Records Index

## Purpose

This document is the routing index for canonical workstream records under `Docs/workstreams/`.

Use this layer when a backlog item has been promoted and now needs:

- a stable feature-state record
- a branch-local validation/evidence record
- an active seam or hardening trail when needed
- a closure record
- a stable path before and after closure

This index does not own repo-wide process rules.
Use `Docs/phase_governance.md` for phase names, proof authority, seam governance, timeout governance, preflight rules, stop-loss rules, the validation helper contract, and the desktop UI audit rule.

## Workstream Record Rules

- workstream docs are the canonical feature-state, branch-local validation/evidence, active-seam, artifact-history, branch-local reuse, and closure records for promoted work
- `Record State` tracks whether the record is `Promoted` or `Closed`
- `Status` remains the delivery or work field
- `Registry-only` backlog items do not require a canonical workstream execution record yet
- when a backlog item moves from `Registry-only` to `Promoted`, its canonical workstream doc must be created at a stable `Docs/workstreams/FB-XXX_slug.md` path
- once promoted, the canonical workstream doc becomes the durable execution and traceability record for that lane and must be updated throughout the active branch, not just at closeout
- backlog remains the identity registry and points here through `Canonical Workstream Doc`
- roadmap consumes this layer for sequencing but does not duplicate its full execution story
- repo-wide phase, timeout, proof-authority, seam, stop-loss, validation-helper, and desktop UI audit rules live in `Docs/phase_governance.md`, not in individual workstream docs
- for active desktop workstreams, the default canonical repo-level `UTS` artifact is the `## User Test Summary` section inside the workstream doc unless that doc explicitly declares a different repo path
- for relevant desktop slices, `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` is the required user-facing exported copy unless an explicit documented exception applies
- response-level `## User Test Summary` text does not replace the workstream-owned repo artifact
- when an active desktop slice can be exercised through a real desktop session, the workstream layer should capture or point to the durable evidence from that interactive OS-level validation before continuation is recommended
- synthetic or headless validation evidence may support that continuation decision, but it does not replace the interactive OS-level gate when that gate is feasible
- when meaningful user-facing desktop UI changed on an active workstream branch, the workstream layer should also capture or point to the final live launched-process UI audit evidence as part of closeout history
- that UI audit expectation is a post-green closeout rule for meaningful desktop UI changes, not a rule that every seam iteration must always take screenshots
- when Codex creates or materially extends lane-specific validators, harnesses, runtime helpers, scripts, workers, report roots, exported manual-test artifacts, or other reusable support assets on an active workstream branch, the workstream doc should keep a durable artifact-history or artifact-reference section for them
- that artifact-history section should record the path, purpose, introduced-when or introduced-why note, classification such as `baseline`, `supporting`, `interactive-only`, or `temporary`, and how future work should reuse the artifact
- when an active workstream enters governed closeout recovery or another late hardening phase, it should also record the current phase
- when an active workstream enters governed closeout recovery or another late hardening phase, it should also record the phase exit criteria
- when an active workstream enters governed closeout recovery or another late hardening phase, it should also record the validation contract
- when an active workstream enters governed closeout recovery or another late hardening phase, it should also record the timeout contract
- when an active workstream enters governed closeout recovery or another late hardening phase, it should also record the current active seam
- when an active workstream enters governed closeout recovery or another late hardening phase, it should also record the seam ledger
- when an active workstream enters governed closeout recovery or another late hardening phase, it should also record the stop-loss threshold
- branch-local "what worked", reuse guidance, and future-branch carry-forward notes belong in the canonical workstream doc first
- only generalized cross-branch lessons should be distilled into `Docs/incident_patterns.md`
- closed workstream docs remain historical lane truth and must not be treated as active execution authority by inertia
- closed workstream docs may explicitly state that no separate ongoing `UTS` artifact remains

## Minimum Durable Traceability Content

For an active or recently closed canonical workstream, keep these durable traceability elements current when relevant:

- `ID` / title, `Record State`, and `Status`
- purpose / why it matters
- current branch truth or equivalent promoted-lane truth
- scope and non-goals
- executed slices or equivalent progress log
- current phase and phase-specific validation, seam, timeout, or stop-loss state when phase-sensitive work is active
- durable validation or proof references that materially justify continuation or closeout
- artifact history or artifact references for lane-specific validators, harnesses, helpers, reports, or manual-test exports that future work should reuse
- branch-local reuse notes or "what worked" guidance when a future branch would otherwise need to rediscover the same lesson
- closeout traceability, or an explicit note that the lane is not at closeout yet
- `## User Test Summary` when relevant, or an explicit note in a closed lane that no separate ongoing `UTS` artifact remains

## Current Canonical Workstream Records

### Active

- `Docs/workstreams/FB-036_saved_action_authoring.md` on `feature/fb-036-idea5-integrated-hardening` (branch-local active workstream; not merged on `main`)

### Closed

- `Docs/workstreams/FB-027_interaction_system_baseline.md`
- `Docs/workstreams/FB-035_release_context_fallback_hardening.md`
- `Docs/workstreams/FB-034_recoverable_diagnostics.md`
- `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md`
- `Docs/workstreams/FB-033_startup_snapshot_harness_follow_through.md`
- `Docs/workstreams/FB-028_history_state_relocation.md`

## Naming Pattern

Use:

- `Docs/workstreams/FB-XXX_slug.md`

for backlog-backed canonical workstream records.
