# ORIN Task Template

You are working inside the Nexus Desktop AI project as an implementation and analysis partner.

## Authoritative Source Of Truth

Treat the following files as authoritative unless a direct verified implementation-state conflict is found:

- `C:\Nexus Desktop AI\Docs\development_rules.md`
- `C:\Nexus Desktop AI\Docs\Main.md`
- `C:\Nexus Desktop AI\Docs\phase_governance.md`
- `C:\Nexus Desktop AI\Docs\architecture.md`
- `C:\Nexus Desktop AI\Docs\orin_vision.md`
- `C:\Nexus Desktop AI\Docs\feature_backlog.md`
- `C:\Nexus Desktop AI\Docs\orchestration.md`
- `C:\Nexus Desktop AI\Docs\[relevant canonical workstream docs]`
- `C:\Nexus Desktop AI\Docs\[relevant rebaseline or closeout docs]`

If anything in the request conflicts with those docs, call it out explicitly before proceeding.

## Prompt Hygiene

- Use `C:\Nexus Desktop AI\Docs\Main.md` as the routing index for selecting the correct authority baseline.
- The default prompt baseline should usually be `development_rules.md`, `Main.md`, `phase_governance.md`, the directly relevant authority docs, and the evidence inputs needed to validate live truth.
- If a canonical workstream, rebaseline, or consolidated design doc exists for the active question, prefer that authority doc over a stack of superseded slice docs.
- Include prior closeout docs and older slice docs only when they are still materially relevant to the specific task.
- Treat canonical workstream docs as branch-local feature-state, evidence, validation-contract, and active-seam references.
- Treat `phase_governance.md` as the repo-wide authority for phase names, stop-loss rules, proof ownership, timeout governance, validation-helper rules, desktop UI audit rules, and truth-drift enforcement.

Concise prompts are acceptable.
They do not reduce the required depth of analysis.

## Current Project State

Version:
[fill in version]

Branch:
[fill in branch]

Mode:
[analysis-only / planning-only / docs-only / patch / review / release-workflow]

Workstream:
[fill in workstream id or authority record]

Phase:
[Branch Readiness / Workstream / Hardening / Live Validation / PR Readiness / Release Readiness]

Branch Class:
[implementation / docs/governance / emergency canon repair / release packaging]

Validation Contract:
[fill in only when validation governance matters]

Timeout Contract:
[fill in only when interactive timing governance matters]

Seam Sequence:
[fill in when a Workstream pass may execute more than one seam]

Repo state:
[Active Branch / No Active Branch]

Current active seam:
[fill in only when the task is in governed closeout recovery]

Note: task mode defines the task type. Codex collaboration posture is defined separately in `C:\Nexus Desktop AI\Docs\codex_modes.md`.
If the task is phase-sensitive and the exact `Phase` field is missing, stop and clarify before execution.
If repo state is blocked `No Active Branch`, implementation is blocked and the task should resolve the blocking repair path instead of starting implementation.
If repo state is steady-state `No Active Branch`, do not start implementation by inertia.
An explicitly approved `docs/governance`, `release packaging`, or `emergency canon repair` branch may still proceed only when the branch-class admission rules from `C:\Nexus Desktop AI\Docs\phase_governance.md` allow it.
If a governance or canon update is directly required to keep the active current branch truthful, executable, phase-correct, readiness-correct, validation-correct, closeout-correct, or release-correct, keep that docs-only update on the active branch inside the current phase and branch class.
Use a separate governance or docs-style branch only for repo-wide uncoupled governance work, emergency canon repair, cross-branch truth repair, or governance work that would contaminate or confuse an active implementation or release branch.
Add `Validation Contract`, `Timeout Contract`, and `Current active seam` when the governed task needs them.
Add `Seam Sequence` when the Workstream prompt may use bounded multi-seam workflow.
If `Seam Sequence` is present, Codex must execute one active seam at a time, validate after each seam, and report a continue-or-stop decision before starting the next seam.

Default expectation:

- if task mode is `analysis-only` or `planning-only`, do not patch
- if task mode is `docs-only`, change docs only inside the approved boundary
- if task mode is `patch`, perform the approved implementation work unless blocked by a real conflict

## Current Accepted State

- [fill in the current version status]
- [fill in the relevant completed revisions]
- [fill in the relevant guarantees already established]

## Carry-Forward Review

Classify prior suggestions, branch conclusions, or closeout output as:

- carry forward
- defer
- discard

Do not treat prior suggestions as automatic scope.

For the first planning prompt after a merge or release, this review should be filled in explicitly.

## Evidence Inputs

Use the following as part of the task evidence set when relevant:

- [uploaded files]
- [logs]
- [screenshots]
- [trace output]
- [manual test notes]
- [prior verification artifacts]
- [branch-local validation artifacts created during the pass]
- [validator or harness outputs]

If critical evidence is missing, say so explicitly.

If the task depends on in-chat screenshot review inside the Codex client, add a prompt note such as:

- `Use live launched-process screenshots.`
- `Preserve the originals on disk and in the audit manifest.`
- `For in-chat image proof, use a small inline PNG data image one at a time until rendering is confirmed.`

## Locked Boundaries / Do Not Reopen

Do not casually reopen:

- [locked behavior 1]
- [locked behavior 2]
- [locked behavior 3]

If any future version should intentionally change those, treat that as a deliberate new workstream or system phase, not a cleanup tweak.

## Task

Your job is to:
[describe the exact task in one or two sentences]

## Workstream Identity

Use this section when the task is a coherent workstream:

- subsystem: [one subsystem only]
- end-state: [one concrete end-state]
- approved subproblem: [one coherent approved subproblem]

## Branch And Milestone Context

Use this section when the branch matters to the task:

- milestone value: [why this branch or docs program is worth completing]
- same-branch follow-through: [dependent work that still belongs on this branch before readiness]
- branch posture: [fresh branch from updated main / continue approved active branch / docs/governance branch from No Active Branch / release packaging branch / emergency canon repair branch / No Active Branch]
- branch-level plan: [objective, target end-state, expected seam families and risk classes, validation contract, User Test Summary strategy, later-phase needs, and first seam or seam sequence]

If a lane was already closed, merged, or released, the next workstream should start from updated `main` on a fresh branch.

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

## Analysis-Phase Rules

Before proposing implementation, Codex should:

- validate live repo truth
- scan broadly enough to understand the affected system
- identify factual, structural, and authority drift where relevant
- report risks, dependencies, and options clearly
- avoid premature scope compression before the user and ChatGPT choose execution boundaries

If the request is analysis-heavy, do not turn it into a bounded executor prompt too early.

## Execution-Phase Rules

After analysis is complete and execution scope is approved, follow these discipline rules:

- verify exact failure path or behavior before changing logic
- no blind iteration
- one coherent approved subproblem per revision
- use bounded multi-seam workflow as the primary Workstream model when the approved seams are same-workstream, same-phase, same-risk, and same-subsystem-family or tightly coupled
- execute exactly one active seam at a time and validate, record, and decide continue-or-stop before the next seam
- use single-seam fallback for bug fixes, hotfixes, unclear or high-risk seams, cross-subsystem work, settings/protocol/launcher/UI-model changes, or any pass where validation cannot support safe continuation
- preserve architecture boundaries
- keep source-of-truth docs aligned with actual implemented state
- production behavior must remain unchanged unless explicitly in scope

Execution-specific discipline such as:

- minimal isolated changes
- smallest coherent execution slice
- bounded implementation
- narrow fix pass

belongs here, after scope has been selected.

Additional task-specific constraints:

- [constraint 1]
- [constraint 2]
- [constraint 3]

## Guidance

Operate like a careful senior collaborator.

That means:

- validate assumptions against the docs and current repo state
- reason broadly before deciding execution shape
- call out risks or drift clearly
- avoid speculative rewrites
- do not widen scope without justification
- when code work is the primary deliverable, keep directly supporting truth-doc sync inside the same approved workstream when that preserves canon coherence
- when live truth shows a closed lane or released branch is no longer the right base, call that out and move the next workstream to updated `main` on a fresh branch

If an execution task is too broad for one approved pass, explain the cleaner execution shapes after analysis rather than shrinking the investigation itself.

## Required Workflow

### Before Changing Anything

1. Read the source-of-truth docs.
2. Inspect the relevant repo, code, or doc state.
3. Inspect the provided evidence inputs.
4. Validate branch, release, and current-truth posture when relevant.
5. Report the actual state, risks, conflicts, and dependencies.

### Before Execution

1. Explain the approved execution scope.
2. Explain the branch or workstream posture.
3. Explain the exact current phase, branch class, and blockers.
4. Explain the next legal phase or say explicitly that repo state is `No Active Branch`.
5. If in `Branch Readiness`, explain the whole-branch execution plan before Workstream admission.
6. If in `Workstream`, explain whether bounded multi-seam workflow is safe; if it is, list the seam sequence, per-seam gates, and stop conditions.
7. If in `PR Readiness`, explicitly plan the stale-canon check, post-merge-state handling, next-workstream selection/canon/minimal-scope/no-branch-exists check, required `Next Workstream: Selected`, `Minimal Scope:`, `## Selected Next Workstream`, and `Branch: Not created` markers, dirty-branch/durable-commit check, docs-sync/drift-audit check, normal governance validator, and PR-readiness gate mode.
8. Explain the validation plan.

If the task includes interactive validation, the validation plan should also state:

- existing helper or harness that will be reused first, or the exact reason reuse is unsafe
- whether any temporary one-off probe is being used and how it will be deleted or promoted before closeout-grade proof
- full-run hard timeout
- no-progress timeout
- scenario timeout when relevant
- transition timeout when relevant
- visible progress markers or step-log updates that prove the run is not stalled
- how timeout or freeze will be reported and cleaned up

### During Execution

1. Perform only the approved execution work.
2. For bounded multi-seam workflow, perform exactly one seam, verify it, record evidence, and decide `continue` or `stop` before starting the next seam.
3. Stop the workflow immediately on validation failure, regression, scope drift, risk-class change, governance drift, unresolved manual-validation blocker, or branch-truth inconsistency.
4. Clean up session-scoped side effects from the pass unless there is an explicit reason to preserve them.
5. Report what changed, what was verified, the per-seam continue-or-stop decisions, and what was cleaned up or intentionally left in place.

## Verification Requirements

At minimum, verify:

- [verification item 1]
- [verification item 2]
- [verification item 3]

If applicable, also verify:

- healthy path
- failure path
- artifact cleanup
- session cleanup and teardown
- existing-helper reuse or documented justification for any temporary probe
- cleanup verification, including that no test-opened app window, helper process, or temporary probe file was left behind
- no regressions in locked behavior
- no drift outside the allowed surfaces
- interactive validation time budgets and timeout behavior when the pass depends on a real desktop or harness run
- no-progress supervision, using the tighter helper-specific watchdog when present or a `10s` maximum no-progress interval when no tighter watchdog exists

Session cleanup and teardown includes, when relevant:

- closing programs, windows, or dialogs opened during the pass
- stopping helper processes, harnesses, temporary runtimes, or validators started during the pass
- deleting temporary files, scratch documents, probe files, or other temporary outputs created only for the pass
- restoring any local state or source inputs intentionally changed for verification
- explicitly checking that those items are actually closed, stopped, deleted, or restored before handoff rather than assuming they cleaned themselves up

If anything remains intentionally open or preserved after the pass, the output must say so explicitly and explain why.

If an interactive run times out or freezes, the output must also state:

- which time budget tripped
- the last confirmed meaningful progress point
- what cleanup was performed before handoff
- whether the issue is classified as product defect, harness defect, environment issue, or canon / contract drift

If the slice changes user-visible behavior, runtime interaction, UX flow, prompts, startup behavior, voice behavior, or another manual operator-facing path, the final output must include a `## User Test Summary` section as a concrete manual checklist.

That checklist must include:

- setup or prerequisites
- exact user actions
- expected visible behavior
- failure signs to watch for
- branch-specific or slice-specific validation focus

A recap-style summary is not sufficient when manual validation is relevant.

If no meaningful manual test exists, the output must still include `## User Test Summary` and explain why manual validation is not materially relevant for that slice.

If a canonical repo-level `UTS` artifact exists for the active desktop workstream, the execution pass must update that artifact as well rather than stopping at response text.

By default, that artifact is the `## User Test Summary` section in the relevant canonical workstream doc unless that doc explicitly declares a different repo path.

For bounded multi-seam Workstream execution, update the canonical workstream `UTS` incrementally as user-visible seams land.
When the Workstream seam chain is complete, refresh the desktop export if the branch is user-facing.

If the artifact is not updated, the final output must explain why the update was skipped.

For relevant desktop slices, the execution pass must also export or refresh:

- `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`

unless the final output explicitly explains why the desktop export was not relevant or was intentionally skipped.

Response-level `## User Test Summary` text alone is not sufficient when either the canonical repo artifact or the desktop export should exist.

For runtime, UI, startup, prompt, voice, or other operator-facing implementation slices, validator results alone are not sufficient to justify immediate continuation.

The execution pass must also:

- run a deeper branch-local validation or hardening pass against the implemented path
- add or create the smallest reliable validation infrastructure on-branch when meaningful blind spots remain
- preserve evidence of the validators, synthetic/headless harnesses, helper scripts, fixtures, logs, traces, screenshots, or other validation artifacts actually used
- use synthetic or headless validation as supporting proof rather than the final continuation gate when a real desktop session is feasible
- launch and exercise the real desktop or runtime path through an interactive OS-level session when feasible
- explicitly distinguish validator results, synthetic or headless validation results, simulated reasoning, interactive OS-level execution results, and remaining manual user-test handoff
- explicitly decide whether the next move is to continue implementation, pause for hardening, or fix a specific defect first

If the current validation surface is too thin to support a continuation recommendation, the execution pass must strengthen that surface before recommending continuation.

If a real interactive OS-level session is not feasible, the execution pass must explain why, use the strongest available non-interactive evidence, and state that any continuation recommendation is limited by that missing interactive gate.

## Done When

This task is complete only when:

- [done condition 1]
- [done condition 2]
- [done condition 3]
- no unrelated behavior changed
- the result stays inside approved scope
- verification evidence supports the claimed result

## Stop Conditions

Stop and explicitly report if:

- source-of-truth docs conflict with the request
- critical evidence is missing
- the task would require reopening locked architecture
- safe verification is not possible
- the task needs a new branch basis because the current one is stale, merged, or no longer the right execution base

## Required Output Format

A. Source-of-truth validation result
B. Recommended plan or execution summary
C. Files changed or to be changed
D. Risks, conflicts, or notable design choices
E. Verification summary
F. Any doc updates made or why none were needed

If relevant, also include:

G. Commit summary
H. Commit description
I. PR title
J. PR description

K. `## User Test Summary` manual checklist when manual validation is relevant

## Important

- Do not write code if this is analysis-only.
- Do not patch files if this is planning-only.
- Do not reopen closed version behavior without explicit approval.
- Do not smuggle in policy or authority changes outside the approved task.
- Do not modify backlog status or add backlog items unless the task explicitly authorizes backlog updates.
- Do not force tightly coupled governance or canon updates onto a separate docs/governance branch when the active branch owns the affected truth and the update can stay inside its current phase, branch class, validation rules, and stop conditions.
- Do not force a docs-only canon repair onto a hypothetical implementation branch when live truth and `C:\Nexus Desktop AI\Docs\phase_governance.md` justify an explicitly approved standalone docs/governance branch.
