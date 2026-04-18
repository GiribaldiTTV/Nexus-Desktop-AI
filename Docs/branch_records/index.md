# Branch Authority Records Index

## Purpose

This index routes repo-owned authority records for approved branches that do not map to a promoted backlog workstream.

Use this layer for:

- `docs/governance` branches
- `emergency canon repair` branches
- `release packaging` branches

when those branches need a durable repo-owned phase authority record.

Do not use this layer to replace:

- `Docs/workstreams/` for promoted backlog-backed workstreams
- merge-target canon sync that belongs on an already-active implementation branch

## Rules

- branch authority records are for explicitly approved non-backlog branches only
- active-branch-first remains the default during `pre-Beta`
- a standalone `docs/governance` branch must not be used for routine canon completion that belongs on an active implementation or release branch
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

- `Docs/branch_records/codex_no_active_branch_docs_governance_refinement.md`

## Historical Branch Authority Records

- none yet
