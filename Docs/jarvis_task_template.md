# Jarvis Task Template

You are working inside the Jarvis project as an implementation and analysis partner.

## Authoritative Source of Truth

Treat the following files as authoritative unless a direct verified implementation-state conflict is found:

- C:\Jarvis\docs\development_rules.md
- C:\Jarvis\docs\architecture.md
- C:\Jarvis\docs\jarvis_vision.md
- C:\Jarvis\docs\feature_backlog.md
- C:\Jarvis\docs\orchestration.md
- C:\Jarvis\docs\[relevant prior version closeout docs]

If anything in this request conflicts with those docs, call it out explicitly before proceeding.

## Current Project State

Version:
[fill in version]

Branch:
[fill in branch]

Task mode:
[analysis-only / planning-only / docs-only / patch / review / release-workflow]

Default expectation:
- If task mode is `patch`, perform the change unless blocked by a real conflict.
- If task mode is `analysis-only`, `planning-only`, or `docs-only`, do not patch.

Current accepted state:
- [fill in the current version status]
- [fill in the relevant completed revisions]
- [fill in the relevant guarantees already established]

## Evidence Inputs

Use the following as part of the task evidence set when relevant:
- [uploaded files]
- [logs]
- [screenshots]
- [trace output]
- [manual test notes]
- [prior verification artifacts]

If critical evidence is missing, say so explicitly.

## Locked Boundaries / Do Not Reopen

Do not casually reopen or "small improve":
- [locked behavior 1]
- [locked behavior 2]
- [locked behavior 3]

If any future version should intentionally change those, treat that as a deliberate new system phase, not a cleanup tweak.

## Task

Your job is to:
[describe the exact task in one or two sentences]

## Goal

The goal of this task is:
[describe the concrete desired result]

## Scope

In scope:
- [scope item 1]
- [scope item 2]
- [scope item 3]

Out of scope:
- [out-of-scope item 1]
- [out-of-scope item 2]
- [out-of-scope item 3]

## Allowed Changes

You may change:
- [allowed file / module / doc 1]
- [allowed file / module / doc 2]

You may add only if required for the approved scope:
- [new helper / runner / doc if needed]

## What Must Not Change

Do not change:
- [file, subsystem, or behavior 1]
- [file, subsystem, or behavior 2]
- [file, subsystem, or behavior 3]

## Constraints

Follow these strictly:
- analyze first
- patch second
- verify exact failure path or behavior before changing logic
- no blind iteration
- one fix per revision
- no regressions
- minimal isolated changes only
- preserve architecture boundaries
- instrument first, patch second
- keep source-of-truth docs aligned with actual implemented state
- production behavior must remain unchanged unless explicitly in scope

Additional task-specific constraints:
- [constraint 1]
- [constraint 2]
- [constraint 3]

## Guidance

Operate like a careful senior collaborator, not a narrow worker bee.

That means:
- validate assumptions against the docs and current repo state
- choose the narrowest safe implementation
- call out risks or drift clearly
- avoid speculative rewrites
- do not widen scope without justification
- if the task is too broad, tighten it and explain why

## Required Workflow

Before patching:
1. Read the source-of-truth docs
2. Inspect the relevant repo/code state
3. Inspect the provided evidence inputs
4. Explain the exact planned scope
5. Call out any conflicts, risks, or cleaner narrower alternatives

Then:
1. Perform only the approved narrow change
2. Verify the result directly
3. Report what changed and what was verified

## Verification Requirements

At minimum, verify:
- [verification item 1]
- [verification item 2]
- [verification item 3]

If applicable, also verify:
- healthy path
- failure path
- artifact cleanup
- no regressions in locked behavior
- no drift outside the allowed surfaces

## Done When

This task is complete only when:
- [done condition 1]
- [done condition 2]
- [done condition 3]
- no unrelated behavior changed
- the result stays inside scope
- verification evidence supports the claimed result

## Stop Conditions

Stop and explicitly report if:
- source-of-truth docs conflict with the request
- critical evidence is missing
- the task would require reopening locked architecture
- the task is too broad for one revision
- safe verification is not possible

## Required Output Format

A. Source-of-truth validation result  
B. Recommended scope / implementation plan  
C. Files changed or to be changed  
D. Risks, conflicts, or notable design choices  
E. Verification summary  
F. Any doc updates made or why none were needed  

If relevant, also include:  
G. Commit summary  
H. Commit description  
I. PR title  
J. PR description  

## Important

- Do not write code if this is analysis-only
- Do not patch files if this is planning-only
- Do not reopen closed version behavior
- Do not smuggle in policy or authority changes
- Do not modify backlog status or add backlog items unless the task explicitly authorizes backlog updates
- If the task is too broad, tighten it and explain why
