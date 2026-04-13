# Workstream Records Index

## Purpose

This document is the routing index for canonical workstream records under `Docs/workstreams/`.

Use this layer when a backlog item has been promoted and now needs:

- a planning record
- an execution record
- a validation record
- a closure record
- a stable path before and after closure

## Workstream Record Rules

- workstream docs are the canonical planning, execution, validation, and closure truth for promoted work
- `Record State` tracks whether the record is `Promoted` or `Closed`
- `Status` remains the delivery or work field
- backlog remains the identity registry and points here through `Canonical Workstream Doc`
- roadmap consumes this layer for sequencing but does not duplicate its full execution story
- for active desktop workstreams, the default canonical repo-level `UTS` artifact is the `## User Test Summary` section inside the workstream doc unless that doc explicitly declares a different repo path
- for relevant desktop slices, `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` is the required user-facing exported copy unless an explicit documented exception applies
- response-level `## User Test Summary` text does not replace the workstream-owned repo artifact
- when an active desktop slice can be exercised through a real desktop session, the workstream layer should capture or point to the durable evidence from that interactive OS-level validation before continuation is recommended
- synthetic or headless validation evidence may support that continuation decision, but it does not replace the interactive OS-level gate when that gate is feasible
- closed workstream docs may explicitly state that no separate ongoing `UTS` artifact remains

## Current Canonical Workstream Records

### Active

- `Docs/workstreams/FB-036_saved_action_authoring.md` on `feature/fb-036-saved-action-authoring` (branch-local active workstream; not merged on `main`)

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
