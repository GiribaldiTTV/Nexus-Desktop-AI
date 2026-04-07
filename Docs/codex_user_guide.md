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

## Quick Start

The best default prompt pattern is:

- one cue
- one anchor
- optional control add-ons only when needed

Use:

- `[cue]: [anchor]`

Examples:

- `Analyze and Report: merge readiness for current branch`
- `Analyze for drift: current branch before merge`
- `Workflow mode: fix zero-match safety on current branch`
- `docs-only pass: improve prompt cookbook guidance`
- `continue on current branch: finish the remaining regression`
- `use latest User Test Summary as authoritative and continue`

## Fastest Reliable Rule

Short prompts are fine.

What still matters is:

- the cue tells Codex how to work
- the anchor tells Codex what the work is about

Good anchors include:

- the active branch
- the bug
- the file
- the workstream
- the outcome you want
- the returned evidence artifact

Weak anchors include:

- `continue`
- `fix it`
- `look at this`

Those can still work if the current thread already makes the target obvious, but they are less reliable than one explicit anchor.

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

## Cue Cheat Sheet

Use `Analyze and Report` or `Analysis mode` when you want:

- audit
- sequencing
- readiness judgment
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

## Best Prompt Building Blocks

The easiest reliable prompt usually contains:

- one cue
- one anchor
- zero to three control add-ons

Useful control add-ons include:

- `on current branch`
- `do not widen scope`
- `analysis only`
- `docs-only pass`
- `no PR/release output`
- `use latest User Test Summary as authoritative`
- `self-validate before handoff`
- `use helper if needed`
- `commit and push if clean`

These add-ons are optional.
Use them only when they materially reduce ambiguity or protect scope.

## Prompt Recipes

### Analyze The Next Move

Use:

- `Analyze and Report: best next lane after current branch`

Useful add-ons:

- `analysis only`
- `use latest User Test Summary as authoritative`

### Check For Drift

Use:

- `Analyze for drift: current branch before merge`

Best for:

- mixed-scope branches
- stale prompt assumptions
- source-of-truth mismatch
- architecture or workflow drift

### Continue The Same Branch

Use:

- `continue on current branch: [exact remaining bug or task]`

Examples:

- `continue on current branch: finish zero-match safety`
- `continue on current branch: do one final smoke-focused hardening pass`

### Run A Narrow Fix Pass

Use:

- `Workflow mode: fix [bug] on current branch`

Useful add-ons:

- `do not widen scope`
- `use helper if needed`
- `self-validate before handoff`

### Run Desktop Runtime Tests Reliably

When the task needs Codex to launch the Nexus desktop runtime for testing, the safe default is:

- use the approved launcher helper in `dev/launchers/`
- or launch `desktop/orin_desktop_launcher.pyw` directly through `pythonw.exe`

Codex should not rely on ad hoc raw `wscript.exe` shell launches for test automation, because path-with-spaces failures can create misleading Windows Script Host errors unrelated to the actual product behavior.

### Review A Returned User Test Summary

Use:

- `review latest User Test Summary to files-of-truth standards`

or:

- `use latest User Test Summary as authoritative and continue`

### Run A Docs-Only Pass

Use:

- `docs-only pass: [exact truth change]`

Examples:

- `docs-only pass: add prompt recipes for same-branch workflow`
- `docs-only pass: clarify helper decision rules`

### Ask For A Ready-To-Use Prompt

Use:

- `give me a prompt for ChatGPT to [task]`

Examples:

- `give me a prompt for ChatGPT to fix zero-match safety on the current branch`
- `give me a prompt for ChatGPT to analyze merge readiness`

### Publish Completed Work

Use:

- `commit and push`

If you want more safety, use:

- `review current branch, then commit and push if clean`

### Ask For A Merge-Readiness Review

Use:

- `Analyze and Report: merge readiness for current branch`

Useful add-ons:

- `analysis only`
- `no PR/release output`

### Ask For A Branch Plan

Use:

- `analysis-to-plan pass: [goal]`

Examples:

- `analysis-to-plan pass: improve Codex operator workflow`
- `analysis-to-plan pass: choose the next FB-027 interaction lane`

## High-Value Special Cases

### Latest User Test Summary

When handing back a filled `User Test Summary.txt`, the strongest short prompt is usually:

- `use latest User Test Summary as authoritative and continue`

If needed, add one anchor:

- `use latest User Test Summary as authoritative and continue on click-away mirroring`

Codex should then:

- digest what passed
- digest what failed
- identify what remains unclear
- separate current-slice work from later ideas
- recommend the next move using repo truth

### Same-Branch Continuation

When you want Codex to stay on the same branch, the strongest short prompts are:

- `continue on current branch: [exact task]`
- `Workflow mode on current branch: [exact task]`

This keeps branch churn low while still preserving scope.

### Review And Readiness

Good short prompts for review:

- `Analyze and Report: is this merge-ready`
- `Analyze for drift: current branch before merge`
- `review latest User Test Summary to files-of-truth standards`

Good short prompts for implementation:

- `Workflow mode: finish Issue 1 on current branch`
- `Workflow mode: do a tiny docs-only pass for shorthand prompt guidance`

## When To Use A Longer Prompt

Use a longer structured prompt when:

- the branch state may be stale or ambiguous
- you need very tight in-scope and out-of-scope boundaries
- the task spans more than one approval-sensitive step
- the work could affect release/readiness, backlog, or source-of-truth canon significantly
- the work involves many exact files, helper paths, or validation expectations

If the task is simple, a short prompt is usually enough.
If the task has hidden risk, a longer prompt is worth it.

## Best Operator Habits

These habits will make the system easier to use:

- prefer one cue plus one anchor over very long prompts by default
- add one control add-on only when scope or validation is easy to misunderstand
- use `Analyze for drift` before merge, release, or major docs carry-forward decisions
- use `use latest User Test Summary as authoritative` whenever returned testing should control the next move
- use `give me a prompt for ChatGPT to ...` whenever you want a reusable handoff prompt instead of rebuilding one manually
- keep using the desktop shortcut to the live guide so updates in repo truth stay visible without duplicating guidance

## What This Guide Does Not Do

This guide does not make two-word prompts universally safe with no anchor at all.

It also does not remove:

- user approval requirements
- backlog control
- scope control
- validation requirements

The goal is lower prompt burden with the same discipline, not lower discipline with shorter prompts.
