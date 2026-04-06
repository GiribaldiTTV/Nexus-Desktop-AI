# Jarvis Development Rules

## Core Principles

- One fix per revision
- No regressions
- Latest files are the only source of truth
- Identical source filenames only (do not create versioned code files)
- Generated runtime and crash artifacts may use Run ID-based filenames

## Workflow

1. Analyze first
2. Patch second
3. Verify the exact failure path before changing logic
4. No blind iteration
5. Run a post-revision Analyze pass before recommending the next revision

## Change Discipline

- Changes must be minimal and isolated
- Preserve architecture boundaries
- Do not mix multiple behaviors into one revision

In Jarvis workflow terms:

- one fix per revision means one coherent approved subproblem per revision, not one tiny mechanical fragment
- minimal isolated changes means the minimal coherent approved change set needed to close that subproblem

Use the smallest safe slice for:

- architecture clarification
- boundary-setting
- high-risk behavior or policy work

Use the smallest coherent slice for:

- lower-risk post-boundary feature delivery where a smaller fragment would leave an incomplete first deliverable

## Testing Requirements

Every revision must include:

- Healthy path verification
- Failure or edge-case verification (if applicable)
- Runtime log review
- Crash log review (if present)
- Artifact cleanup verification

## Standard Analyze Pass

After every revision, review:

- the newest runtime log
- the newest crash log, if one exists
- `diagnostics_status.txt`
- `diagnostics_stop.signal` and `renderer_startup_abort.signal` when relevant
- the exact startup, shutdown, failure, or recovery milestones reached
- whether observed behavior matches the intended revision scope
- whether any regression markers appeared

## Logging Philosophy

- Logs are the source of truth
- Do not assume behavior without log evidence
- Prefer structured markers over raw output

## Root Logs Governance

- `C:/Jarvis/logs` and `C:/Jarvis/logs/crash` are reserved for already-approved live launcher/runtime truth surfaces only
- current approved root-owned surfaces are:
  - launcher-generated `Runtime_*.txt`
  - matching live crash logs
  - launcher control/status files when relevant
  - the current launcher-owned historical state file `jarvis_history_v1.jsonl` until a later explicitly approved relocation slice moves it
- dev/test/worker/toolkit evidence must write under `C:/Jarvis/dev/logs/<lane>/...`
- no new dev/test/worker evidence roots, new subfolders, or new artifact families may be introduced under `C:/Jarvis/logs` or `C:/Jarvis/logs/crash` without explicit user approval

## Dev-Only Startup Snapshot Harness

For desktop attach, first-visible frame, or startup-freeze debugging, Codex may use the env-gated startup snapshot harness in the desktop renderer when that is the smallest reliable evidence path.

Rules:

- the harness must remain opt-in through `JARVIS_HARNESS_STARTUP_SNAPSHOT_DIR`
- snapshot output must write to an explicitly chosen dev/test evidence path, not to root `logs`
- the harness is for internal debugging only and must not become normal user-facing behavior
- snapshot timing should stay bounded to the startup window under investigation
- if the harness is not needed for the active task, leave it disabled

## Orchestration Philosophy

Build in this order:

1. Observability (know what is happening)
2. Classification (know what state it is in)
3. Control (safe ability to intervene)
4. Outcome clarity (know what happened)
5. Behavior (decide what to do)

Never skip a stage.

## Scope Control

Do NOT mix into orchestration revisions:

- UI changes
- Voice system changes
- Feature development
- Folder restructuring
- `main.py` redesign

These are separate phases.

## Controlled Improvement Suggestions

If you identify a potential improvement while analyzing or implementing a revision:

- Do NOT include it in the current patch
- Do NOT expand the scope of the current revision
- Do NOT combine it with the active change

Instead:

1. Clearly call out the improvement separately
2. Explain why it is beneficial
3. Propose it as a future revision
4. Keep it within one-fix-per-revision discipline

Example format:

Suggested Future Revision:

- Description of the improvement
- Why it should be done
- Which files would likely be affected
- Why it is not included in the current revision

## Rule

Improvements must be proposed, not silently implemented.

Scope expansion without explicit approval is not allowed.

## Goal

Jarvis must behave as a:

- Observable system
- Controllable system
- Self-correcting system

Not a black box.

## Versioning Philosophy

Each version should focus on a single system layer.

Examples:

- Logging work should focus on observability and traceability
- Orchestration work should focus on startup control, recovery, and lifecycle behavior
- Behavior work should focus on decision-making and policy

Do not mix major system layers across versions unless explicitly planned as a dedicated transition.

Each revision (`revX`) must introduce only one controlled change within that version's scope.

## Documentation Rule

Important architecture, orchestration, and behavior decisions should be written into repo docs rather than left only in chat history.

Project docs are part of the source of truth and should be read before planning future revisions.

Use `docs/Main.md` as the source-of-truth index and prompt-baseline map for future Jarvis tasks.

When a workstream has a consolidated canonical planning or design doc, future prompts and task baselines should prefer that canonical doc over the full stack of superseded slice docs.

Superseded slice docs may still be used for historical traceability, earlier revision review, or conflict checking, but they should not continue to be listed as equal-weight prompt inputs once a canonical consolidation exists.

Future prompts should usually prefer:

- `docs/development_rules.md`
- `docs/Main.md`
- only the directly relevant canonical doc or docs
- only the relevant evidence inputs

Closeout docs, historical docs, and optional planning references should be added only when the task materially depends on them.

Core code progression is prioritized over repeated separate doc-only micro-passes.

When a code workstream directly establishes or changes truth that should be recorded, the required truth-doc updates may be bundled into that same approved workstream if:

- the doc updates directly support or record the active code task
- the edits do not widen architecture or backlog scope
- batching the doc sync keeps the repo more accurate than delaying it

Prefer milestone-level or canonical doc sync when meaningful, rather than forcing repeated separate micro-passes for every small code slice, unless a docs-only clarification is the safest boundary-setting move.

When using Codex or ChatGPT for project tasks, prefer the structured prompt format in `docs/jarvis_task_template.md` so requests include clear goal, context, evidence, constraints, allowed surfaces, and done-when criteria.

## Historical Intelligence Rules

Cross-run intelligence must be contract-defined in repo docs before implementation begins.

That contract must define:

- versioned history schema
- run identity rules
- failure fingerprint rules
- provenance labeling
- retention and reset behavior
- corruption and fallback behavior

Historical intelligence must remain a derived layer over current-run truth.
It must not become a second source of runtime truth.

Confidence may be used only as explanatory metadata.
It must never be treated as authoritative runtime policy.

If historical state is missing, unreadable, or corrupt, the system must degrade cleanly to the last finalized non-historical behavior.

## Backlog Integration

If a new idea or improvement is identified:

- It must be added to docs/feature_backlog.md
- It must NOT be implemented immediately
- It must be assigned a suggested version and revision
- It must follow one-fix-per-revision discipline

Ideas are only implemented after being explicitly selected from the backlog.

## Backlog Control

The backlog file (docs/feature_backlog.md) is the controlled planning layer for future work.

### Codex Permissions

Codex may:
- propose new backlog items
- format backlog entries
- suggest updates to backlog items

Codex may NOT:
- silently edit the backlog
- mark items complete without approval
- change status of existing items without approval
- reorder or reprioritize items
- delete backlog items

Backlog state changes must be explicitly approved and performed by the user.

### Required Backlog Workflow

If a new idea, improvement, or follow-up work is identified:

1. Codex must propose a backlog update first
2. The proposal must include:
   - Type (new item / status update / notes / completion)
   - Title
   - Reason
   - Exact markdown change
3. Codex must wait for explicit user approval
4. Only after approval may Codex edit docs/feature_backlog.md

### Execution Rules

- Backlog updates must remain minimal and scoped
- Backlog changes may be made alongside other files ONLY after approval
- If no backlog update is required, do not modify the backlog

### Control Principle

The backlog is a planning and control layer.

Codex assists in managing it, but the user retains final authority over:
- prioritization
- status changes
- completion
