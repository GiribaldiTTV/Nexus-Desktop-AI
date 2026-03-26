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
