# Codex User Guide

## Purpose

This is a short USER-facing guide for talking to Codex inside the Nexus Desktop AI repo.

It is not binding governance. Repo source truth lives in `Docs/Main.md` and the owner files routed by `Docs/Main.md`. If this guide and source truth ever disagree, source truth wins.

Use this guide when you want a clear in-chat request without writing a full ChatGPT packet.

## Quick Index

1. Quick Prompts
2. How to ask Codex to check everything
3. Useful context fields
4. Screenshot and visual-review requests
5. If Codex misses something
6. Short glossary
7. What this guide does not do

## Quick Prompts

| Goal | Example prompt |
| --- | --- |
| Analyze only | `Analyze only. Load repo source truth first, inspect the issue, and return options with the safest legal path. Do not mutate.` |
| Rebaseline safely | `Rebaseline and reconcile neutral main and the Governance worktree. Report identity, drift, validation, and next legal phase.` |
| Governance docs-only repair | `Perform the approved bounded docs-only Governance repair. Keep helper, validator, runtime, FAM worktree, PR, merge, release, issue, cleanup, and external-state mutation blocked unless explicitly approved.` |
| Worktree adoption after governance changed | `Run the merged-standard adoption review for this rebaselined branch. Compare current branch output against merged UI/UX, backend/runtime, proof, template, and vision standards. If out-of-scope defects are found, prepare issue candidates only; do not create GitHub issues without USER approval.` |
| PR Readiness analysis only | `Perform PR Readiness Stage 1 analysis only. Do not create a PR. Return blockers, changed-file scope, validation, PR-body risk, and exact Stage 2 approval text if green.` |
| Release Readiness analysis only | `Perform Release Readiness Stage 1 analysis only. Do not mutate files, tag, publish, create a release, or clean branches. Return release-window truth, blockers, and the exact next legal phase.` |
| User Test Summary review | `Digest the returned User Test Summary, map each USER finding to branch scope, evidence, repair status, waiver/deferral, and next legal phase. Do not treat helper green as USER acceptance.` |
| GitHub issue candidates | `If defects are outside the approved current scope, prepare GitHub issue candidates only. Include title, affected FAM/FFV/surface, evidence, expected behavior, owner recommendation, and severity. Do not create or close GitHub issues without USER approval.` |
| Ask for the next prompt | `Give me a bounded prompt for the next legal phase. Include source-truth load order, approval boundaries, stop conditions, validation expectations, and exact return packet.` |

## How To Ask Codex To Check Everything

Weak prompt:

```text
check everything
```

Better prompt:

```text
Run a full Scope Coverage Manifest check for the approved scope. Inventory every changed file, source-truth owner, UI element group, runtime/backend surface, generated artifact, proof claim, validator/helper result, human-judgment item, exclusion, blind spot, and downstream worktree adoption risk. Every target must be labeled PASS, REPAIR, BLOCKED, WAIVED_WITH_REASON, or Not Applicable With Reason before reporting green.
```

Use the stronger version when the work is broad, visual, phase-sensitive, or when prior checks missed drift.

## Useful Context Fields

When the phase, branch, or approval boundary matters, include these fields:

```text
Mode:
Phase:
Workstream:
Branch:
Worktree:
Approved scope:
Not approved:
Validation expected:
Stop conditions:
Return packet:
```

If you paste or attach a prompt for another family, branch, worktree, packet, or USER hub label while a thread is assigned to the current worktree, Codex should stop on `Prompt-Ingress Lane Lock` / `Prompt-Ingress Lane Mismatch` before switching folders or acting on that other lane. Give an explicit lane-switch/worktree-escape approval only when you really want the current thread to leave its assigned lane.

Example:

```text
Mode: Governance repair
Phase: Branch Readiness Stage 1 analysis
Workstream: <actual approved objective>
Branch: <verified assigned branch>
Worktree: D:\Nexus Desktop AI\Worktrees\<assigned-carrier>
Approved scope: analysis only
Not approved: mutation, PR, merge, release, issue mutation, runtime work
Validation expected: read-only identity and source-truth load verification
Stop conditions: wrong worktree, stale origin/main, unclear authority
Return packet: verdict, files loaded, findings, next legal phase
```

## Screenshot And Visual-Review Requests

For UI/UX, visual proof, or screenshot-heavy work, ask for a USER-inspectable visual review:

```text
Evaluate all touched UI against Project Vision, FAM-002 presentation grammar, applicable Family / Feature Vision, Visual Inheritance Matrix, element-group acceptance, and screenshot/video or USER-validation proof. List every repair target.
```

For element-level checks, use:

```text
For each touched UI element group, compare visuals and behavior against accepted NDAI patterns. Check window chrome, close/minimize/maximize controls, spacing, fonts, colors, hover states, disabled states, error states, and whether the result feels deterministic, intuitive, immersive, and predictable.
```

If you want images to render in the Codex app, ask for small previews backed by the original files:

```text
Preserve the original screenshots on disk, then show small in-chat preview images for the key findings so I can inspect them here.
```

## Backend And Runtime Review Requests

For backend/runtime reliability, ask Codex to connect UI state to real runtime truth:

```text
Evaluate all touched runtime/backend behavior against the Backend Predictability / Reliability Contract. Map state owner, deterministic inputs/outputs, lifecycle/state machine, failure/fallback/recovery, logs, rollback, and UI-visible status/error mapping.
```

For UI/backend consistency:

```text
For each touched UI state, identify the backend/runtime truth that drives it. Confirm disabled, loading, unavailable, error, success, fallback, recovery, and degraded states are backed by deterministic state instead of UI-only assumptions.
```

## If Codex Misses Something

Use this shape:

```text
This appears to be drift. Re-open the current phase analysis, explain why the prior check missed it, identify the source-truth/validator/helper gap, repair the gap if in scope, and rerun validation. Do not treat prior green validation as authority.
```

If the miss is visual, add:

```text
Include screenshot or video proof and an element-by-element comparison against the accepted NDAI visual pattern.
```

If the miss is backend/runtime, add:

```text
Include the runtime state owner, deterministic inputs/outputs, failure/fallback/recovery behavior, and UI-visible status mapping.
```

## Short Glossary

- `Source truth`: Repo-owned files routed by `Docs/Main.md`.
- `External operational state`: Local/private operational records outside repo docs when source truth permits.
- `USER packet`: A review aid for USER/ChatGPT; useful evidence, not source truth by itself.
- `Validator/helper output`: Evidence that still needs review against repo truth and the actual work.
- `Scope Coverage Manifest`: A checklist-style review that proves what Codex inspected, what it skipped, what passed, what needs repair, and what remains blocked.
- `Slice` / `SLC`: A bounded implementation unit. `SLC` is the short written form for Slice-level line items.
- `Seam`: The current execution checkpoint inside or between slices.
- `Issue candidate`: A proposed GitHub issue record prepared for USER review before any issue mutation.

## What This Guide Does Not Do

This guide does not define phase law, approval authority, source-truth ownership, release rules, PR rules, helper behavior, validator behavior, external-state schema, or implementation permission.

For those rules, Codex must load `Docs/Main.md` and the current owner files it routes to.
