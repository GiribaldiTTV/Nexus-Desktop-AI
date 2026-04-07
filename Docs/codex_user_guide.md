# Codex User Guide

## Purpose

This document is the canonical operator guide for using short, reliable prompts with Codex inside Nexus Desktop AI work.

It exists to reduce prompt overhead without reducing source-of-truth discipline, validation quality, or scope control.

This guide is downstream of:

- `development_rules.md`
- `Main.md`
- `codex_modes.md`
- `user_test_summary_guidance.md`

If this guide conflicts with those files, those files win.

## Core Rule

The best default prompt pattern is:

- one mode or task cue
- plus one concrete anchor

The cue tells Codex how to work.
The anchor tells Codex what the work is actually about.

Good anchors include:

- the active branch
- the bug
- the file
- the workstream
- the outcome you want
- the returned evidence artifact

## What Codex Should Do Automatically

Short prompts do not waive source-of-truth reading.

When the user gives a brief cue such as:

- `Analyze and Report`
- `Analyze for drift`
- `Analysis mode`
- `Workflow mode`
- `docs-only pass`
- `reference docs for the following`
- `continue on current branch`

Codex should still:

1. load `docs/development_rules.md`
2. load `docs/Main.md`
3. infer the directly relevant canonical doc or docs
4. pull only the evidence inputs needed for the task
5. keep the same validation standard as a longer structured prompt

If the task is still materially ambiguous after that baseline, Codex should ask one tight clarifying question rather than lowering quality.

## Best Short Prompt Pattern

Use:

- `[cue]: [anchor]`

Examples:

- `Analyze and Report: merge readiness for current branch`
- `Analyze for drift: FB-027 overlay usability branch`
- `Workflow mode: fix zero-match enter leak on current branch`
- `docs-only pass: add shorthand prompt baseline rules`
- `reference docs for the following: next FB-027 interaction lane`
- `continue on current branch: finish click-away no-mirroring`

## What Good Anchors Look Like

Good anchors are concrete.

Examples:

- `current branch`
- `latest User Test Summary`
- `FB-027 overlay usability`
- `merge readiness`
- `zero-match safety`
- `Docs/Main.md routing cleanup`

Weak anchors are vague.

Examples:

- `look at this`
- `continue`
- `fix it`

Those can still work if the current thread already makes the target obvious, but they are less reliable than one explicit anchor.

## Mode Cheat Sheet

Use `Analyze and Report` or `Analysis mode` when you want:

- audit
- sequencing
- readiness judgment
- drift review
- recommendation without patching

Use `Analyze for drift` when you specifically want:

- a check for scope drift
- source-of-truth drift
- prompt drift
- architecture drift
- branch-readiness risk caused by mixed work

Use `Workflow mode` when you want:

- a bounded patch
- a docs-only pass
- a same-branch fix pass
- a controlled validation pass after approval

Use `docs-only pass` when you want:

- truth-doc updates only
- no runtime implementation work

## User Test Summary Rule Of Thumb

When handing back a filled `User Test Summary.txt`, the shortest strong prompt is usually:

- `use latest User Test Summary as authoritative and continue`

If needed, add one anchor:

- `use latest User Test Summary as authoritative and continue on click-away mirroring`

Codex should then:

- digest what passed
- digest what failed
- identify what remains unclear
- separate current-slice work from later ideas
- recommend the next move using repo truth

## Same-Branch Continuation Rule Of Thumb

When you want Codex to stay on the same branch, the strongest short prompts are:

- `continue on current branch: [exact task]`
- `Workflow mode on current branch: [exact task]`

This keeps branch churn low while still preserving scope.

## Review And Readiness Shortcuts

Good short prompts for review:

- `Analyze and Report: is this merge-ready`
- `Analyze for drift: current branch before merge`
- `review latest User Test Summary to files-of-truth standards`

Good short prompts for implementation:

- `Workflow mode: finish Issue 1 on current branch`
- `Workflow mode: do a tiny docs-only pass for shorthand prompt guidance`

## What This Guide Does Not Do

This guide does not make two-word prompts universally safe with no anchor at all.

It also does not remove:

- user approval requirements
- backlog control
- scope control
- validation requirements

The goal is lower prompt burden with the same discipline, not lower discipline with shorter prompts.
