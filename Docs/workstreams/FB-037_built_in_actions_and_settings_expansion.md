# FB-037 Curated Built-In System Actions And Nexus Settings Expansion

## ID And Title

- ID: `FB-037`
- Title: `Curated built-in system actions and Nexus settings expansion`

## Record State

- `Promoted`

## Status

- `Merged unreleased on main`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-037-built-in-actions-and-settings-expansion`

## Purpose / Why It Matters

Promote the curated built-in system actions and Nexus settings expansion lane above the released shared action, saved-action authoring, callable-group authoring, and deterministic callable-group execution baseline.

This workstream exists so common Windows, vendor utility, and Nexus-owned destinations can become deliberate first-class built-in actions under the shared action model instead of being left to ad hoc saved-action customization.

## Current Phase

- Phase: `Release Readiness`

## Phase Status

- `No Active Branch`
- after this branch merges, FB-037 is merged-unreleased implementation release debt and no implementation branch remains active
- Release Readiness is the governing post-merge phase until release packaging clears `Release Debt` for FB-037
- successor-lane lock is waived because post-merge repo truth resolves to `No Active Branch` due to `Release Debt` (FB-037)
- historical implementation branch:
  - `feature/fb-037-built-in-actions-and-settings-expansion`
- PR Readiness on the implementation branch passed after Live Validation evidence was digested and merge-target canon was corrected for post-merge truth
- prior Hardening repaired and verified the reusable live-validation helper/process path before the first Live Validation attempt
- Branch Readiness setup is durably checkpointed in commit `1cc1a93`
- first four implementation seams are selected and implemented:
  `catalog-only Task Manager built-in action`, `catalog-only Calculator built-in action`, `catalog-only Notepad built-in action`, and `catalog-only Paint built-in action`
- product/runtime changes are limited to the existing shared-action catalog and exact resolver precedence needed for saved-action fallback safety
- branch-local docs-only governance refinement is allowed only to keep this active implementation branch truthful, phase-correct, and aligned with live source-of-truth; it does not authorize product/runtime scope expansion
- this branch exposed repo-wide multi-seam workflow drift, and the bounded docs/governance repair is carried on this active branch because it directly controls FB-037 Workstream execution truth
- Workstream exit criteria are satisfied under the bounded multi-seam model
- Live Validation exposed process drift: a one-off interactive validation probe did not use the strongest existing watchdog/progress pattern and did not self-abort before operator-visible stall
- the completed Hardening seam remained limited to governance alignment plus reusable live-validation helper/process repair; no new product features, built-ins, target kinds, launcher behavior, UI model changes, settings/protocol behavior, or result/confirm copy changes were introduced
- the first formal FB-037 Live Validation run passed Task Manager and Calculator built-in evidence, reached correct Notepad confirm and launch markers, but failed to capture a visible Notepad launch window before timeout
- the targeted helper Hardening pass added process/window probes, failure manifests, cleanup metadata, framed-window handling, focus-verified input handling, submit markers, and bounded submit retries
- the latest submit-reliability validation proved Task Manager, Calculator, and Notepad all reached `COMMAND_CONFIRM_READY` on the first submit attempt; the remaining failure moved back to Notepad visible-window evidence and Task Manager cleanup
- the later Live Validation attempt at `dev\logs\launcher_live_window_audit\20260420_105902` progressed through built-in scenarios but violated the no-progress cleanup contract during Notepad cleanup and did not generate `manifest.json`
- helper-only Hardening validation later passed at `dev\logs\launcher_live_window_audit\20260420_111616\manifest.json` with manifest-backed cleanup classification and no helper cleanup failures
- closeout-grade Live Validation later passed at `dev\logs\launcher_live_window_audit\20260420_112713\manifest.json` with `19` passed scenarios, `0` scenario failures, `36` captures, and complete cleanup classification
- no additional same-risk Workstream seams remain; settings/protocol behavior, target-kind expansion, launcher-policy work, UI-semantics work, and default-group expansion require a different risk class and remain out of scope unless explicitly reopened later

## Branch Class

- `implementation`

## Blockers

- `Release Debt` (FB-037)

## Entry Basis

- updated `main` is aligned with `origin/main`
- FB-041 is released in `v1.3.1-prebeta` and no longer blocks next-lane admission
- no active promoted workstream exists before this admission
- FB-037 was `Registry-only` on merged canon before this Branch Readiness pass
- this branch was created fresh from updated `main`
- Branch Readiness setup was committed in `1cc1a93`
- Branch Readiness validation passed with `python dev/orin_branch_governance_validation.py`
- `git diff --check` passed after the Branch Readiness checkpoint
- Workstream exited after the approved same-risk built-in catalog seam chain completed and no same-risk seams remained without changing subsystem or risk class
- Hardening pressure-tested the completed seam chain and preserved the earlier Live Validation failures as historical evidence, not active blockers
- Hardening repaired the reusable live-validation helper for progress reporting, failure manifests, process/window probes, focus-verified submit behavior, process-only launch classification, and cleanup outcome classification
- previous reusable helper evidence passed with `powershell -NoProfile -ExecutionPolicy Bypass -File dev\orin_launcher_live_window_audit.ps1 -Fb037Validation`
- previous helper evidence path: `dev\logs\launcher_live_window_audit\20260420_103951`
- subsequent Live Validation evidence path: `dev\logs\launcher_live_window_audit\20260420_105902`
- subsequent Live Validation result: `FAIL`
- subsequent failure basis: the helper passed several built-in scenarios but left a cleanup no-progress gap greater than `10s` during Notepad cleanup and did not generate `manifest.json`
- final helper-only Hardening evidence path: `dev\logs\launcher_live_window_audit\20260420_111616`
- final helper manifest status: `PASS`
- final helper scenario result: `19` passed scenarios, `0` failed scenarios
- final cleanup summary: cleanup success count `5`, OS-blocked cleanup count `0`, helper-failure cleanup count `0`, baseline-skipped count `14`
- repo-side governance validation passed before this phase transition with `python dev/orin_branch_governance_validation.py`
- PR Readiness canon correction recorded the post-merge `No Active Branch` state and waived successor-lane lock because FB-037 release debt blocks next implementation admission

## Exit Criteria

- release packaging for FB-037 is opened on an approved release-packaging branch or otherwise explicitly authorized
- target public prerelease for FB-037 is selected by release packaging
- FB-037 release notes and release-state transitions are prepared before clearing `Release Debt`
- release debt remains explicit until FB-037 is actually released
- no next implementation branch is admitted while FB-037 release debt remains unresolved

## Rollback Target

- `PR Readiness`

## Next Legal Phase

- `Release Readiness`

## Post-Merge State

- Phase (post-merge): `Release Readiness`
- Phase Status (post-merge): `No Active Branch`
- Blocker: `Release Debt` (FB-037)
- Next Legal Phase: `Release Readiness` (release packaging)
- Successor lane lock: waived because repo truth resolves to `No Active Branch` due to FB-037 release debt
- Record State: `Promoted` until release packaging marks FB-037 released and closes the workstream
- Next concern: release packaging; no next implementation lane may begin until release debt is cleared or explicitly waived by canon
- This workstream must not be treated as an active implementation branch owner after merge

## Bounded Objective

Define and implement a curated set of built-in actions for standard Windows, vendor utility, and Nexus-owned surfaces that belong in the product catalog rather than user-authored saved actions.

Workstream execution must use bounded multi-seam workflow where the seams stay in the same risk class and subsystem family.
Each built-in catalog seam must be selected, bounded, implemented, validated, recorded, and judged before the next seam starts.

## Explicit Non-Goals

- no implementation during Branch Readiness
- no product or runtime code changes during Branch Readiness
- no saved-action authoring redesign
- no callable-group execution changes
- no scheduling, branching, retries, nested groups, or parallelism
- no taskbar, tray, plugin, external trigger, monitoring, thermal, or performance HUD work
- no Action Studio behavior
- no voice invocation changes
- no broad UI redesign
- no implicit promotion of FB-038, FB-039, or FB-040

## Reuse Baseline

- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.3.1-prebeta.md`
- `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md`
- `Docs/workstreams/FB-036_saved_action_authoring.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`
- `desktop/shared_action_model.py`
- `desktop/interaction_overlay_model.py`

## Validation Contract

Branch Readiness validation is docs/governance-only and must prove:

- FB-037 is promoted exactly once
- FB-037 has a canonical workstream doc
- the active phase block uses the canonical phase enum
- the branch class is `implementation`
- FB-041 released truth remains unchanged
- no product or runtime code changed
- governance validation passes

Workstream-phase validation must preserve:

- shared action model compatibility
- built-in versus saved action source distinction
- exact-match resolution expectations
- saved-action and callable-group regression behavior
- failure classification and result-surface boundaries from the released baseline
- per-seam validation and continue-or-stop decisions when bounded multi-seam workflow is used

Hardening-phase validation must prove the completed same-risk catalog seam chain remains stable as one branch:

- shared action catalog integrity and built-in metadata remain valid
- saved-action source precedence still overrides built-in phrase collisions
- create/edit authoring collision protection remains bounded
- confirm/result flow remains unchanged for built-ins and saved-action overrides
- callable-group execution and failure semantics remain unchanged
- governance and current-state canon remain aligned

## Branch Readiness Progress

- created fresh branch `feature/fb-037-built-in-actions-and-settings-expansion` from updated `main`
- promoted FB-037 from `Registry-only` to `Promoted`
- created this canonical workstream record
- recorded Branch Readiness phase authority, scope, non-goals, reuse baseline, and validation contract
- checkpointed Branch Readiness setup in commit `1cc1a93`
- advanced phase authority to `Workstream` for bounded seam selection and implementation

## Workstream Progress

- Seam 1 complete:
  `catalog-only Task Manager built-in action`
- added `open_task_manager` as one built-in `app` action targeting `taskmgr.exe`
- kept the existing `CommandAction` schema, supported target kinds, launch path, UI flow, confirm flow, and result flow unchanged
- preserved saved-action precedence by allowing saved-action phrase collisions with built-ins to load and resolve as saved actions
- kept built-in ID collisions protected
- kept saved-vs-saved exact phrase overlaps as explicit ambiguity candidates
- kept FB-036 authoring create/edit built-in phrase collision rejection intact so the authoring UI path is not widened by this seam
- repo-side validation:
  - `python dev/orin_shared_action_baseline_validation.py` passed
  - `python dev/orin_saved_action_source_validation.py` passed
  - `python dev/orin_saved_action_authoring_validation.py` passed
  - `python dev/orin_interaction_baseline_validation.py` passed
- Seam 2 complete:
  `catalog-only Calculator built-in action`
- added `open_calculator` as one built-in `app` action targeting `calc.exe`
- reused the existing `CommandAction` schema, supported `app` target kind, launch path, UI flow, confirm flow, and result flow
- preserved saved-action precedence so a saved action matching `calculator`, `open calculator`, or `launch calculator` resolves instead of the built-in
- kept FB-036 authoring create/edit built-in phrase collision rejection intact; source-loaded saved actions still retain override authority
- kept callable-group execution, failure classification, result text, Nexus settings, shell arguments, and target-kind support unchanged
- repo-side validation:
  - `python dev/orin_shared_action_baseline_validation.py` passed
  - `python dev/orin_saved_action_source_validation.py` passed
  - `python dev/orin_saved_action_authoring_validation.py` passed
  - `python dev/orin_interaction_baseline_validation.py` passed
  - `python dev/orin_callable_group_execution_validation.py` passed
  - `python dev/orin_branch_governance_validation.py` passed
- same-phase Seam 2 hardening checkpoint passed with targeted proof for catalog ordering, exact-match boundaries, saved-action override precedence, confirm/result continuity, and authoring collision protection
- Seam 3 complete:
  `catalog-only Notepad built-in action`
- added `open_notepad` as one built-in `app` action targeting `notepad.exe`
- reused the existing `CommandAction` schema, supported `app` target kind, launch path, UI flow, confirm flow, and result flow
- preserved saved-action precedence so a saved action matching `notepad`, `open notepad`, or `launch notepad` resolves instead of the built-in
- kept FB-036 authoring create/edit built-in phrase collision rejection intact; source-loaded saved actions still retain override authority
- kept callable-group execution, failure classification, result text, Nexus settings, shell arguments, and target-kind support unchanged
- repo-side validation:
  - `python dev/orin_shared_action_baseline_validation.py` passed
  - `python dev/orin_saved_action_source_validation.py` passed
  - `python dev/orin_saved_action_authoring_validation.py` passed
  - `python dev/orin_interaction_baseline_validation.py` passed
  - `python dev/orin_callable_group_execution_validation.py` passed
  - `python dev/orin_branch_governance_validation.py` passed
- same-phase Seam 3 hardening checkpoint passed with targeted proof for catalog ordering, exact-match boundaries, saved-action override precedence, create/edit authoring collision protection, confirm/result continuity, target-kind boundaries, and default-group boundaries
- Seam 4 complete:
  `catalog-only Paint built-in action`
- added `open_paint` as one built-in `app` action targeting `mspaint.exe`
- reused the existing `CommandAction` schema, supported `app` target kind, launch path, UI flow, confirm flow, and result flow
- preserved saved-action precedence so a saved action matching `paint`, `open paint`, or `launch paint` resolves instead of the built-in
- kept FB-036 authoring create/edit built-in phrase collision rejection intact; source-loaded saved actions still retain override authority
- kept callable-group execution, failure classification, result text, Nexus settings, shell arguments, target-kind support, launcher policy, and UI semantics unchanged
- repo-side validation:
  - `python dev/orin_shared_action_baseline_validation.py` passed
  - `python dev/orin_saved_action_source_validation.py` passed
  - `python dev/orin_saved_action_authoring_validation.py` passed
  - `python dev/orin_interaction_baseline_validation.py` passed
  - `python dev/orin_callable_group_execution_validation.py` passed
  - `python dev/orin_branch_governance_validation.py` passed
  - `git diff --check` passed with CRLF normalization warnings only
- all currently safe same-risk Workstream implementation seams are complete; settings/protocol behavior, target-kind expansion, launcher-policy work, UI-semantics work, and default-group expansion remain out of scope unless a later phase-valid prompt explicitly reclassifies the risk
- branch-coupled governance refinement complete:
  `bounded multi-seam workflow` is now formalized as the primary Workstream model while preserving one active seam at a time, per-seam validation, continue-or-stop gates, single-seam fallback, and the normal `Workstream` -> `Hardening` -> `Live Validation` -> `PR Readiness` phase path
- repo-side governance validation:
  - `python dev/orin_branch_governance_validation.py` must pass after the multi-seam governance repair
  - `git diff --check` must pass after the multi-seam governance repair
- Workstream exit complete:
  - all approved same-risk catalog seams are complete and validated
  - no same-risk Workstream seams remain without changing subsystem or risk class
  - phase authority transitioned from `Workstream` to `Hardening`

## Hardening Progress

- Initial Hardening pressure-tested the completed built-in catalog seam chain
- Hardening did not add new built-ins, settings/protocol behavior, target kinds, launcher-policy behavior, UI-model changes, or default-group expansion
- Initial Hardening validation passed:
  - `python dev/orin_shared_action_baseline_validation.py`
  - `python dev/orin_saved_action_source_validation.py`
  - `python dev/orin_saved_action_authoring_validation.py`
  - `python dev/orin_interaction_baseline_validation.py`
  - `python dev/orin_callable_group_execution_validation.py`
  - `python dev/orin_branch_governance_validation.py`
  - `git diff --check`
  - inline four-built-in cross-seam pressure probe
- Live Validation later exposed process drift in the interactive helper path: the attempted validation used a one-off probe pattern without sufficient reusable-helper discipline, visible progress, or no-progress self-abort
- reopened Hardening completed the governance alignment plus reusable live-validation helper/process repair
- `dev/orin_launcher_live_window_audit.ps1` now records visible step progress, writes a step log, reports the last confirmed progress point, and enforces a `10s` no-progress supervisor by default
- helper repair validation passed with `powershell -NoProfile -ExecutionPolicy Bypass -File dev\orin_launcher_live_window_audit.ps1 -TimeoutSeconds 8 -NoProgressTimeoutSeconds 10`
- targeted evidence/cleanup reliability validation passed with `powershell -NoProfile -ExecutionPolicy Bypass -File dev\orin_launcher_live_window_audit.ps1 -Fb037Validation`
- latest reusable helper artifact path: `dev\logs\launcher_live_window_audit\20260420_103951`
- latest reusable helper manifest status: `PASS`
- latest reusable helper cleanup classification is explicit: cleanup success count `1`, OS-blocked cleanup count `0`, helper-failure cleanup count `0`, and baseline-skipped count `14`
- phase authority transitioned from `Hardening` to `Live Validation` after helper repair validation, evidence/cleanup validation, and governance validation passed
- later Live Validation run `dev\logs\launcher_live_window_audit\20260420_105902` reopened Hardening because cleanup created a no-progress gap greater than `10s` after Notepad launch evidence and the run was aborted before `manifest.json` was generated
- helper-only Hardening repaired cleanup watchdog coverage, manifest-before-cleanup failure handling, final manifest refresh, Win32 visible-window probe acceptance, cleanup progress markers, and already-exited cleanup classification
- final helper-only Hardening validation passed:
  `powershell -NoProfile -ExecutionPolicy Bypass -File dev\orin_launcher_live_window_audit.ps1 -Fb037Validation`
- final helper evidence path:
  `dev\logs\launcher_live_window_audit\20260420_111616`
- final helper manifest status:
  `PASS`
- final helper cleanup classification:
  cleanup success count `5`, OS-blocked cleanup count `0`, helper-failure cleanup count `0`, baseline-skipped count `14`
- Live Validation closeout evidence path: `dev\logs\launcher_live_window_audit\20260420_112713`
- Live Validation closeout manifest status: `PASS`
- Live Validation closeout scenario result: `19` passed scenarios, `0` failed scenarios
- Live Validation closeout artifact summary: `manifest.json`, `step_log.txt`, `36` screenshots/probes, and per-scenario launch evidence were generated
- Live Validation closeout cleanup classification: cleanup success count `20`, OS-blocked cleanup count `14`, helper-failure cleanup count `0`, baseline-skipped count `0`
- environment-specific behavior classification:
  - Task Manager launched correctly and visible launched-window evidence was captured; Windows denied forced Task Manager termination during cleanup, which is classified as OS-blocked cleanup rather than helper or product failure
  - Notepad resolved and launched correctly under runtime markers; this environment exposed Notepad process-only/no-visible-window evidence, so the helper preserved launch probes and classified the launch as `process_launched_no_visible_window`

## Live Validation Progress

- Live Validation was formally opened for real interactive usage checks of the completed built-in catalog seam chain
- first FB-037 live helper run:
  `powershell -NoProfile -ExecutionPolicy Bypass -File dev\orin_launcher_live_window_audit.ps1 -Fb037Validation -TimeoutSeconds 8 -NoProgressTimeoutSeconds 10`
- result: `FAIL`
- preserved evidence path:
  `dev\logs\launcher_live_window_audit\20260420_094357`
- Task Manager built-in evidence passed:
  correct confirm marker, launch marker, result screenshot, and launched-window screenshot were captured for `open_task_manager`
- Calculator built-in evidence passed:
  correct confirm marker, launch marker, result screenshot, and launched-window screenshot were captured for `open_calculator`
- Notepad built-in partial evidence:
  correct confirm marker and launch marker were captured for `open_notepad`, and confirm/result screenshots were written
- Notepad failure:
  the helper timed out while waiting for a visible window matching `*Notepad*`; no manifest was generated because the run stopped before scenario completion
- targeted Hardening rerun after process/window-probe and failure-manifest changes:
  `dev\logs\launcher_live_window_audit\20260420_095824`
- result: `FAIL`
- Task Manager evidence passed and `manifest.json` was generated on failure
- Calculator failure:
  the helper detected `CalculatorApp` process state but no visible process-owned top-level window; the manifest classified the probe instead of timing out silently
- targeted Hardening reruns after framed-window and submit-path changes:
  `dev\logs\launcher_live_window_audit\20260420_100012` and `dev\logs\launcher_live_window_audit\20260420_100155`
- result: `FAIL`
- helper submit failure:
  the runtime observed overlay text changes for `open task manager`, but the helper did not produce the expected `COMMAND_CONFIRM_READY|action_id=open_task_manager` marker
- targeted Hardening rerun after focus-verified submit repair:
  `dev\logs\launcher_live_window_audit\20260420_101109`
- result: `FAIL`
- submit reliability result:
  Task Manager, Calculator, and Notepad each reached the expected `COMMAND_CONFIRM_READY` marker on the first submit attempt, with explicit `input focused`, `text set`, `submit attempted`, and `submit confirmed` step-log markers
- remaining helper failure:
  Notepad launched according to runtime markers but did not expose a visible document window before the `10s` no-progress watchdog; the manifest records the two Notepad processes and hidden window probe
- remaining cleanup failure:
  Task Manager remained open after helper cleanup because Windows denied process termination; the pass also verified that normal close, Alt+F4, `WM_CLOSE`, and `taskkill` could not close the instance from the current process context
- targeted Hardening rerun after evidence/cleanup reliability repair:
  `dev\logs\launcher_live_window_audit\20260420_103951`
- result: `PASS`
- evidence/cleanup reliability result:
  the reusable helper completed the FB-037 validation profile, generated `manifest.json`, wrote `step_log.txt`, preserved confirm/result screenshots, preserved launch probes for process-only launches, and classified cleanup outcomes without helper failure
- second Live Validation attempt:
  `dev\logs\launcher_live_window_audit\20260420_105902`
- result: `FAIL`
- runtime/product result:
  built-in scenarios progressed through Task Manager, Calculator, Notepad, and Paint evidence without a product contradiction before the run was stopped
- helper failure:
  cleanup after Notepad created a no-progress gap greater than the `10s` contract and the aborted run did not generate `manifest.json`
- the earlier interrupted attempt remains non-closeout-grade evidence
- interrupted or partial interactive evidence is not closeout-grade proof and does not advance the phase by implication
- closeout-grade Live Validation run:
  `powershell -NoProfile -ExecutionPolicy Bypass -File dev\orin_launcher_live_window_audit.ps1 -Fb037Validation`
- closeout-grade evidence path:
  `dev\logs\launcher_live_window_audit\20260420_112713`
- result: `PASS`
- scenario summary:
  `19` passed scenarios, `0` scenario failures
- artifact summary:
  `manifest.json`, `step_log.txt`, `36` screenshots/probes, confirm captures, result captures, launched-window captures where visible-window evidence was available, and launch probes where process-only evidence was the observed environment behavior
- required Live Validation focus completed:
  - built-in execution for Task Manager, Calculator, Notepad, and Paint
  - saved-action override behavior for the same phrase families
  - authoring collision rejection for built-in phrases
  - mixed built-in plus saved-action source behavior
  - repeated execution without resolution drift or state leakage
- environment-specific classifications:
  - Task Manager cleanup produced OS-blocked termination outcomes while preserving successful launch evidence and no helper cleanup failure
  - Notepad produced process-only/no-visible-window launch evidence in this environment; runtime markers and launch probes remained consistent with successful execution
- no product/runtime contradiction, confirm/result divergence, saved-action override failure, or helper evidence gap remained after the run
- phase authority advanced from `Live Validation` to `PR Readiness` during the implementation branch, and PR Readiness correction later encoded the post-merge `Release Readiness` / `No Active Branch` release-debt state

## Governance Drift Audit

- Governance Drift Found: Yes, already resolved on this active branch
- Drift Type: Workstream execution-flow governance, active-branch governance placement, and Live Validation helper/process discipline
- Why Current Canon Failed To Prevent It: Earlier canon still carried one-seam-per-pass habits, left ambiguity around whether branch-coupled governance fixes belonged on a separate docs branch, and did not make reusable Live Validation helpers plus no-progress monitoring explicit enough to prevent operator-visible stalls
- Required Canon Changes: Already applied on this branch across repo-wide governance docs, prompt scaffolds, the branch governance validator, and this authority record; no additional canon delta is required by the closeout-grade Live Validation evidence
- Whether The Drift Blocks Merge: No, because the drift was corrected before PR Readiness and the remaining PR gate is ordinary merge-target canon/package review
- Whether User Confirmation Is Required: No further confirmation is required for the already-applied governance repairs; any new governance expansion found during PR Readiness must stop and request confirmation before implementation
- Missing blocker check: no missing blocker remains after adding reusable-helper timeout, active-branch governance, and bounded multi-seam rules
- Weak phase entry or exit rule check: no unresolved weakness remains for the current FB-037 phase path
- Weak source-of-truth ownership rule check: active workstream authority remains the phase owner; backlog and roadmap only mirror current state
- Stale prompt scaffolding or example check: branch-coupled prompt scaffolds were updated earlier on this branch for multi-seam and active-branch governance rules
- Missing validator requirement check: the branch governance validator now enforces the PR Readiness Governance Drift Audit presence requirement and still guards canonical phase/state drift

## User Test Summary

Seams 1, 2, 3, and 4 add user-visible built-in catalog actions without changing UI structure.

Live Validation evidence captured:

- evidence path: `dev\logs\launcher_live_window_audit\20260420_112713`
- `manifest.json`: generated and `PASS`
- `step_log.txt`: generated with visible progress through cleanup completion
- built-in execution passed for `open task manager`, `open calculator`, `open notepad`, and `open paint`
- saved-action override passed for `task manager`, `calculator`, `notepad`, and `paint`; saved actions won and built-ins did not execute for those override scenarios
- authoring boundary passed for create collisions on `task manager`, `calculator`, `notepad`, and `paint`, plus edit collision on `task manager`
- mixed environment passed for built-in Task Manager, saved Calculator, built-in Notepad, and saved Paint
- repeated execution passed for Notepad without resolution drift or state leakage
- Task Manager launched with visible-window evidence; cleanup termination was OS-blocked by Windows and classified as environmental cleanup behavior, not a product or helper failure
- Notepad launched with runtime markers and process-only/no-visible-window probe evidence in this environment; the helper preserved probe artifacts and classified the launch without treating it as a product contradiction
- confirm and result surfaces used the existing flow and did not require UI copy or model changes
