# Branch Authority Records Index

## Purpose

This index routes repo-owned authority records for approved branches that do not map to a promoted backlog workstream.

Use this layer for:

- `release packaging` branches
- historical `docs/governance` or emergency repair records

when those branches need a durable repo-owned phase authority record.

Do not use this layer to replace:

- `Docs/workstreams/` for promoted backlog-backed workstreams
- merge-target canon sync that belongs on an already-active implementation branch

## Rules

- branch authority records are for explicitly approved non-backlog branches only
- active-branch-first remains the default during `pre-Beta`
- new governance-only branches are not used for Nexus work
- between-branch canon repair is blocked
- missed PR Readiness canon work must be carried by the next active branch's `Branch Readiness` before implementation begins
- the `Active Branch Authority Records` list is only for branches that are still the current execution base
- before PR merge, a non-backlog branch must either move its record into `Historical Branch Authority Records` or remove it entirely so merged truth does not leave a stale active branch owner behind
- historical branch authority records are preserved traceability records, not live execution authority
- each active branch authority record must carry the modern phase-state block:
  - `## Current Phase`
  - `## Phase Status`
  - `## Branch Class`
  - `## Blockers`
  - `## Entry Basis`
  - `## Exit Criteria`
  - `## Rollback Target`
  - `## Next Legal Phase`
- branch authority records should also explain:
  - why the branch exists
  - why it cannot or should not ride on an active implementation branch
  - what it must not change

## Active Branch Authority Records

- `Docs/branch_records/feature_fb_030_successor_branch_truth_repair.md`

## Historical Branch Authority Records

- `Docs/branch_records/codex_fb_037_release_debt_packaging.md`
- `Docs/branch_records/codex_no_active_branch_docs_governance_refinement.md`
- `Docs/branch_records/feature_fb_030_orin_voice_audio_direction_refinement.md`
- `Docs/branch_records/feature_fb_030_release_readiness_canon_repair.md`
