# Jarvis Task Template

You are working inside the Jarvis project as an implementation and analysis partner.

## Authoritative Source of Truth

Treat the following files as authoritative unless a direct verified implementation-state conflict is found:

- C:\Jarvis\docs\development_rules.md
- C:\Jarvis\docs\Main.md
- C:\Jarvis\docs\architecture.md
- C:\Jarvis\docs\jarvis_vision.md
- C:\Jarvis\docs\feature_backlog.md
- C:\Jarvis\docs\orchestration.md
- C:\Jarvis\docs\[relevant consolidated canonical design docs]
- C:\Jarvis\docs\[relevant prior version closeout docs]

If anything in this request conflicts with those docs, call it out explicitly before proceeding.

Prompt hygiene:
- Use `C:\Jarvis\docs\Main.md` as the index for selecting the smallest correct docs baseline.
- The default prompt baseline should usually be `development_rules.md`, `Main.md`, the directly relevant canonical doc or docs, and only the relevant evidence inputs.
- If a consolidated canonical design or planning doc exists for the active workstream, include that doc and omit superseded slice docs unless the task is explicitly tracing history or auditing the consolidation.
- Do not bulk-list archival planning slice docs as equal-weight prompt inputs once a canonical consolidation exists.
- Include prior closeout docs and older slice docs only when they are still materially relevant to the specific task.

## Current Project State

Version:
[fill in version]

Branch:
[fill in branch]

Task mode:
[analysis-only / planning-only / docs-only / patch / review / release-workflow]

Note: Task mode defines the task type. Codex collaboration posture is defined separately in `C:\Jarvis\docs\codex_modes.md`.

Default expectation:
- If task mode is `patch`, perform the change unless blocked by a real conflict.
- If task mode is `analysis-only`, `planning-only`, or `docs-only`, do not patch.
- If task mode is `patch`, prioritize the core code task and bundle only the directly supporting truth-doc updates needed to keep canonical docs aligned when that is safe and in scope.

Current accepted state:
- [fill in the current version status]
- [fill in the relevant completed revisions]
- [fill in the relevant guarantees already established]

Carry-forward / prompt reduction audit:
- [what must be carried forward from the last closeout or prior canonical baseline]
- [what can now be removed from this prompt because current source-of-truth docs already cover it]

For the first planning prompt after a version closeout, this audit should be filled in explicitly.

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

## Workstream Identity

Use this section when the task is a coherent batched workstream:

- subsystem: [one subsystem only]
- end-state: [one concrete end-state]
- approved subproblem: [one coherent approved subproblem]

## Approved Batch Chain

Use this section only when the task intentionally batches dependent slices:

1. [slice 1]
2. [slice 2]
3. [slice 3]
4. [optional slice 4]
5. [optional low-risk completion slice 5]

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

For collaboration-mode and batched-workstream execution specifics, rely on `C:\Jarvis\docs\codex_modes.md` unless this task needs a deliberate task-specific override.

## Guidance

Operate like a careful senior collaborator, not a narrow worker bee.

That means:
- validate assumptions against the docs and current repo state
- choose the smallest safe or smallest coherent approved implementation that fits the task risk and closes one subproblem
- call out risks or drift clearly
- avoid speculative rewrites
- do not widen scope without justification
- if the task is too broad, tighten it and explain why
- when code work is the primary deliverable, prefer keeping directly supporting truth-doc sync inside that same workstream rather than forcing repeated separate doc-only micro-passes

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
