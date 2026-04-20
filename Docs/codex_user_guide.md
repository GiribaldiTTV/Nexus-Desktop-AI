# Codex User Guide

## Purpose

This document explains how to prompt Codex effectively inside Nexus Desktop AI work without sacrificing analysis depth, source-of-truth discipline, or validation quality.

It is an operator guide for prompt construction and collaboration posture.

It is downstream of:

- `Docs/development_rules.md`
- `Docs/Main.md`
- `Docs/phase_governance.md`
- `Docs/codex_modes.md`
- `Docs/user_test_summary_guidance.md`

If this guide conflicts with those files, those files win.

## Core Rule

Concise prompts are allowed.

Concise prompts do **not** mean:

- shallow analysis
- reduced source-of-truth reading
- premature scope compression
- automatic readiness, closure, merge, or release framing

Codex should still:

1. validate live repo truth
2. scan broadly enough to understand the affected system
3. map drift, risk, dependencies, and options
4. report clearly
5. narrow execution only after the user and ChatGPT choose scope

## Default Prompt Posture

The default prompt posture is:

- one cue
- one anchor
- optional control add-ons only when they materially reduce ambiguity

Use:

- `[cue]: [anchor]`

Examples:

- `Analyze and Report: best next workstream after current release`
- `Analyze for drift: post-release canon on updated main`
- `Workflow mode: execute the approved canon phase on current branch`
- `docs-only pass: align README to the merged source-of-truth model`
- `digest latest User Test Summary, reevaluate blockers and phase, then continue only if the next legal phase allows it`

The prompt may be concise.
Codex's investigation should still be complete enough for the task.

## Required Phase Anchor

For phase-sensitive work, prompts should explicitly include:

- `Mode: <mode name>`
- `Phase: <exact phase name>`
- `Workstream: <workstream id or authority record>`
- `Branch: <branch name or No Active Branch>`

For governed closeout recovery, also include:

- `Branch Class: <branch class>`
- `Current active seam: <seam name>`
- `Validation Contract: <summary or authority reference>` when validation governance matters
- `Timeout Contract: <summary or authority reference>` when interactive/manual timing governance matters

For bounded multi-seam Workstream execution, also include:

- `Seam Sequence: <ordered seam list>`
- `Per-Seam Gate: validate, record evidence, and report continue-or-stop before the next seam`

## What Codex Should Do Automatically

Brief prompts do not waive source-of-truth reading.

When the user gives a short cue such as:

- `Analyze and Report`
- `Analyze for drift`
- `Analysis mode`
- `Workflow mode`
- `docs-only pass`
- `continue on current branch`

Codex should still:

1. load `Docs/Main.md`
2. load `Docs/development_rules.md`
3. load `Docs/phase_governance.md`
4. load `Docs/codex_modes.md`
5. infer the directly relevant authority docs
6. pull the repo evidence needed to validate live truth
7. keep the same reasoning standard as a longer structured prompt

For meaningful interactive desktop hardening or closeout work, that baseline also includes:

- using `Docs/phase_governance.md` for the repo-wide validation helper contract and proof hierarchy
- using `Docs/development_rules.md` for evidence, cleanup, and hardening expectations
- reusing existing live-validation helpers before creating new scripts, or recording why reuse is unsafe
- treating one-off live-validation probes as temporary ignored artifacts that must be deleted or promoted into documented reusable tooling before closeout-grade proof
- requiring visible helper progress and a no-progress supervisor; if no tighter helper-specific watchdog is active, `10s` without meaningful progress must abort the run, clean up, and report the last confirmed progress point
- planning the post-green live launched-process UI audit when meaningful user-facing desktop UI changed

## Codex Client Screenshot Delivery

When the user wants live screenshot proof to render inside the Codex client, use this as the default delivery path:

1. capture the screenshot from the real launched process and preserve the original file on disk as the durable audit artifact
2. keep the audit manifest and the original capture paths in the evidence trail
3. if in-chat visual confirmation is needed, default to a small inline PNG `data:` image generated from that real file rather than a local-file Markdown image
4. send one image at a time until the user confirms the client is rendering it reliably
5. if the first inline image fails or flashes, reduce the payload further before trying again

Default assumptions:

- local-file Markdown image embeds are not the reliable default for this client
- smaller inline PNG payloads are the proven default for this client state
- WebP should be treated as a fallback path rather than the default unless PNG has stopped working in the current client state
- the in-chat image is a preview convenience layer, not the durable evidence source
- the durable evidence remains the manifest plus the original captured files on disk

When writing a prompt that depends on in-chat screenshot review, say so explicitly:

- `Use live launched-process screenshots.`
- `Preserve original captures on disk and in the audit manifest.`
- `For in-chat image proof, use a small inline PNG data image one at a time until rendering is confirmed.`

If the task remains materially ambiguous after that baseline, Codex should ask one focused clarifying question rather than lowering the quality of analysis.

## Startup Contract For Every Task

Before planning or execution, Codex should follow the startup contract in `Docs/Main.md`.

For tracked work, that means:

1. read `Docs/Main.md`
2. read `Docs/development_rules.md`
3. read `Docs/phase_governance.md`
4. read `Docs/codex_modes.md`
5. check `Docs/feature_backlog.md` for `Record State`
6. load the canonical workstream doc when the item is `Promoted` or `Closed`
7. if the task is an approved non-backlog branch, load the branch authority record under `Docs/branch_records/`
8. validate current branch truth before trusting prompt framing
9. use the canonical workstream doc first for branch-local reuse, artifact history, and "what worked" notes, or use the branch authority record when no promoted workstream owns the branch
10. use `Docs/incident_patterns.md` only for generalized cross-branch patterns
11. state the next safe move before narrowing scope

Promoted workstream docs remain the place to read branch-local feature state, evidence, active seams, artifact history, and branch-local reuse notes.
Repo-wide lifecycle rules such as phases, stop-loss, timeout governance, and proof authority come from `Docs/phase_governance.md`.
Repo-wide validation-helper rules and the desktop UI audit rule also come from `Docs/phase_governance.md`.

## Analysis-Phase Prompting

Use analysis-phase prompts when the user wants:

- current-truth validation
- drift review
- sequencing review
- next-move determination
- post-release or post-merge review
- source-of-truth audit
- lane or branch evaluation

Helpful cues:

- `Analyze and Report`
- `Analyze for drift`
- `Analysis mode`
- `analysis-to-plan pass`

Helpful add-ons:

- `analysis only`
- `digest latest User Test Summary before recommending the next legal phase`
- `use origin/main as authoritative truth`
- `do not patch`

Analysis-phase prompts should encourage:

- full-system reasoning first
- branch and release truth validation
- structural and authority drift mapping
- carry-forward / defer / discard classification of prior suggestions

They should **not** push Codex to behave like a narrowly bounded executor before the analysis is complete.

## Execution-Phase Prompting

Execution-phase prompts are for work the user has already approved.

Helpful cues:

- `Workflow mode`
- `docs-only pass`
- `execute the approved phase`
- `continue on current branch`

Useful execution add-ons:

- `do not widen scope`
- `self-validate before handoff`
- `use helper if needed`
- `no PR/release output`

Execution-phase discipline such as:

- bounded patching
- bounded multi-seam workflow
- minimal isolated change
- smallest coherent execution slice
- narrow fix pass

belongs here, after analysis and scope selection are already complete.

## Prompt Recipes

### Active-Branch Governance Or Canon Update

Use:

- `Workflow mode on current branch: docs-only governance or canon refinement`

Use this when:

- the active branch owns the affected truth
- the change is directly required to keep that branch truthful, executable, phase-correct, readiness-correct, validation-correct, closeout-correct, or release-correct
- the prompt names the exact canonical phase and current branch class
- the update can stay docs-only and inside the active branch's approved scope, validation rules, and stop conditions

Do not use this recipe for unrelated governance cleanup, broad docs churn, product/runtime changes, or work that would contaminate or confuse the active implementation or release branch.

### Deep Analysis Of The Next Move

Use:

- `Analyze and Report: best next workstream after current branch`

Useful add-ons:

- `analysis only`
- `use origin/main as authoritative truth`

### Drift Review

Use:

- `Analyze for drift: current branch before merge`
- `Analyze for drift: post-release canon on updated main`

Best for:

- mixed-scope branches
- stale prompt assumptions
- source-of-truth mismatch
- release-dependent docs drift
- architecture or workflow drift

### Docs-Only Canon Repair

Use:

- `docs-only pass: emergency repair for post-release canon drift on updated main`

This is an emergency-only workflow.
Use it only when merged canon is already stale and that drift could not be prevented before merge or release.
If a plausible next implementation workstream can be selected safely from current truth, do not treat this as the default path.
If that docs pass changes validation or harness behavior assumptions, canon must be updated before further execution is recommended.

This is not the same thing as a planned `docs/governance` branch from `No Active Branch`.
Use the emergency repair recipe only for escaped canon drift.

### Planned Docs/Governance Branch From No Active Branch

Use:

- `Analyze and Report: may a docs/governance branch begin from No Active Branch`

or:

- `Workflow mode: execute the approved docs/governance branch from No Active Branch`

Use this only when:

- no active implementation branch exists
- the branch purpose is genuinely governance, docs, policy, roadmap, backlog, or triage work
- the branch is not being used to avoid canon sync that belongs on an active implementation or release branch
- the branch-class admission rules from `Docs/phase_governance.md` pass
- the work is repo-wide governance not coupled to one active branch, emergency canon repair, cross-branch truth repair, or governance work that would contaminate or confuse an active implementation or release branch

During `pre-Beta`, this path remains non-default and explicitly justified.
In later Beta, public, or steady-state repo operation, it may become a normal maintenance path.

### Continue An Approved Branch

Use:

- `continue on current branch: [approved remaining task]`
- `Workflow mode on current branch: [approved phase]`

Examples:

- `continue on current branch: finish the approved validator follow-through`
- `Workflow mode on current branch: execute Phase 2 of canon reconstruction`

### Bounded Multi-Seam Workstream Execution

Use:

- `Workflow mode on current branch: execute bounded multi-seam Workstream sequence`

Required add-ons:

- `Phase: Workstream`
- `Seam Sequence: [ordered seam list]`
- `validate after each seam`
- `report continue-or-stop after each seam`
- `stop on validation failure, regression, scope drift, risk-class change, governance drift, unresolved manual-validation blocker, or branch-truth inconsistency`

Use this when:

- the seams are in the same workstream, same phase, same branch class, same risk class, and same subsystem family or tightly coupled chain
- the operator wants Codex to keep moving through a coherent seam sequence without a new prompt after every seam
- per-seam validation and evidence recording remain mandatory

Do not use this recipe for bug fixes, hotfixes, unclear or high-risk seams, cross-subsystem changes, settings/protocol/launcher/UI-model changes, or any pass where validation cannot support safe continuation.

When the sequence completes, the normal next phase is `Hardening`.
Do not prompt Codex to treat Workstream completion as direct `PR Readiness`.

### Run A Narrow Fix Pass

Use:

- `Workflow mode: fix [bug] on current branch`

This recipe is for approved execution work.
It is not the default posture for system analysis.

Useful add-ons:

- `do not widen scope`
- `use helper if needed`
- `self-validate before handoff`

### Governed Closeout Recovery

Use:

- `Workflow mode: governed closeout recovery on current branch`

Use this bounded form when the user wants a stop-and-report recovery pass rather than a continuous run to full green.

Required add-ons:

- `Phase: Hardening`
- `Current active seam: [seam name]`
- `do not widen scope`
- `stop after the governed seam budget is exhausted`

### Continuous Validation To Full Green

Use:

- `Workflow mode: continuous governed validation to full green on current branch`

Required add-ons:

- `Phase: Hardening`
- `use the documented validation timeout profile`
- `reuse existing validation helpers first`
- `do not widen scope`
- `do not stop between seam iterations unless blocker, truth drift, stop-loss, or required canon sync appears`
- `continue until the full gate is green or a hard stop is hit`

Helpful add-ons:

- `target no-progress 3s`
- `fallback maximum no-progress 10s when no tighter helper watchdog exists`
- `target transition 3s`
- `target normal seam 60s`

### Review A Returned User Test Summary

Use:

- `review latest User Test Summary to files-of-truth standards`

or:

- `digest latest User Test Summary to files-of-truth standards, reevaluate blockers and phase, and continue only if the next legal phase allows it`

### Ask For A Prompt

Use:

- `give me a prompt for ChatGPT to [task]`

Examples:

- `give me a prompt for ChatGPT to analyze post-release canon drift`
- `give me a prompt for ChatGPT to execute the approved docs-only phase`

## Fresh-Branch Rule

After a workstream is closed, released, merged, or otherwise no longer the right execution base, the next implementation workstream should start from updated `main` on a fresh branch.

Prompting should reflect that reality.

PR Readiness selects and minimally scopes the next workstream in canon, but it must also prove no branch exists yet for that next workstream.
Use machine-checkable markers: `Next Workstream: Selected` and `Minimal Scope:` in the backlog entry, plus `## Selected Next Workstream` and `Branch: Not created` in the roadmap.
Create the fresh branch only during the next `Branch Readiness` pass after the current branch merges and updated `main` is revalidated.

Do not ask Codex to keep planning from an old lane branch when live repo truth shows that branch is stale, merged, or identical to `main`.
If repo truth is a steady-state `No Active Branch`, it is also valid for the truthful next move to be no branch at all until a new approved need exists.

## When To Use A Longer Prompt

Use a longer structured prompt when:

- the branch or release state may be stale
- the task spans multiple authority layers
- the work could affect canon, governance, routing, backlog, or roadmap behavior
- the exact approved execution boundary matters
- validation expectations are unusually specific

Use a shorter prompt when the task is already well anchored and the current thread or canon makes the target obvious.

The key distinction is prompt length, not analysis depth.

## Best Operator Habits

- use one cue plus one anchor by default
- add control language only when it materially protects truth or scope
- use `Analyze for drift` before merge, release, or major canon carry-forward decisions
- use evidence-digestion language when returned validation evidence should control the next move, rather than implying that phase advancement is automatic
- in `PR Readiness`, require five hard blocker checks before accepting `PR READY: YES`: `stale-canon`, `post-merge`, `next-workstream`, `dirty`, and `docs-sync`
- route through `Docs/Main.md` whenever authority is unclear
- treat local unmerged overlays as reference material until revalidated against updated `origin/main`

## What This Guide Does Not Do

This guide does not make vague prompts universally safe.

It also does not remove:

- user approval requirements
- backlog control
- scope control
- validation requirements
- branch and release truth checks

The goal is lower prompt overhead with the same analytical rigor, not lower rigor with shorter prompts.
