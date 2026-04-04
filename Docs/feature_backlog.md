# Jarvis Feature Backlog

This file is the controlled backlog for future revisions and ideas.

Rules:
- Ideas must NOT be implemented immediately
- Ideas must NOT expand current revision scope
- Ideas must be proposed as future revisions
- Each idea should remain small and scoped when possible
- All backlog changes must follow the backlog control rules defined in development_rules.md
- Backlog items must not be added, modified, or completed without approval

---

## Backlog Items

### [ID: FB-001] Repeated identical crash early escalation

Status: Implemented (v1.6.0)  
Priority: Medium  
Suggested Version: v1.6.0  
Suggested Revision: rev12  

Description:
Add early escalation when two consecutive startup attempts fail with the same normalized crash outcome.

Why it matters:
Repeated identical crashes are a stronger signal than generic failures and should not silently consume retries.

Proposed Change:
If two consecutive non-STARTUP_ABORT attempts have the same normalized failure_cause, stop retries and escalate.

Likely Files Affected:
- jarvis_desktop_launcher.pyw

Scope:
- launcher-only
- repeated identical crash handling

Out of Scope:
- mixed-pattern policy
- startup-abort policy changes

Notes:
This should remain a narrow escalation rule for repeated identical crash outcomes only.

---

### [ID: FB-002] Mixed failure-pattern policy

Status: Implemented (v1.6.0)  
Priority: Medium  
Suggested Version: v1.6.0  
Suggested Revision: TBD  

Description:
Define behavior for mixed failure sequences such as crash then abort or abort then crash.

Why it matters:
Mixed failure patterns may indicate unstable startup conditions, but they are weaker signals than repeated identical failures and need careful classification.

Proposed Change:
Classify mixed failure sequences separately from repeated identical crash or repeated STARTUP_ABORT outcomes and define whether they should continue retrying or escalate earlier.

Likely Files Affected:
- jarvis_desktop_launcher.pyw

Scope:
- launcher-only
- mixed failure-sequence classification
- conservative escalation guidance

Out of Scope:
- repeated identical crash policy
- repeated STARTUP_ABORT policy
- renderer changes

Notes:
This conservative mixed-sequence contract is already satisfied by the stabilized `v1.6.0` launcher behavior. Current launcher behavior recognizes `CRASH_TO_STARTUP_ABORT` and `STARTUP_ABORT_TO_CRASH`, keeps first-observed cross-kind sequences non-terminal, allows them to feed instability labeling, diagnostics-priority reporting, and attempt-pattern reporting, and does not treat them as a new early-exhaustion trigger. Conservative retry continuation remains in place unless an existing `FB-003` terminal class is reached.

---

### [ID: FB-003] Retry limit and diagnostics escalation policy

Status: Implemented (v1.9.0 rev1)  
Priority: Medium  
Suggested Version: v1.9.0  
Suggested Revision: rev1  

Description:
Define when repeated failures should escalate to diagnostics instead of continuing to retry.

Why it matters:
The launcher should avoid silent recovery loops and should escalate in a predictable, evidence-based way when retries stop adding value.

Proposed Change:
Refine retry-limit behavior and define clear thresholds for entering the existing diagnostics completion path based on observed repeated failure patterns.

Likely Files Affected:
- jarvis_desktop_launcher.pyw

Scope:
- launcher-only
- retry and diagnostics escalation boundaries

Out of Scope:
- diagnostics UI redesign
- renderer changes
- broad orchestration refactor

Notes:
This is now implemented through `v1.9.0` `rev1a` and `rev1b`. `rev1a` defined the retry-exhaustion and diagnostics-entry policy contract for repeated `STARTUP_ABORT` outcomes and repeated identical crash outcomes only. `rev1b` implemented the first coherent launcher behavior slice so those two evidence classes now terminate as first-class outcomes, propagate actual attempts used into terminal finalization and runtime summary output, use reason-correct terminal wording, and reuse the existing diagnostics completion path unchanged. Mixed failure-sequence policy remains separate `FB-002` work.

---

### [ID: FB-004] Future boot orchestrator layer

Status: Deferred (planning groundwork complete enough to pause)  
Priority: High  
Suggested Version: v2.0  
Suggested Revision: rev1  

Description:
Design and later implement top-level boot orchestration above the desktop launcher.

Why it matters:
The long-term product direction is for Jarvis to feel like the system-facing experience, with a higher-level boot flow coordinating the transition into the stabilized desktop phase.

Proposed Change:
For current repo truth, establish the minimal future boot-orchestrator planning model without authorizing runtime implementation, then defer later implementation-facing work until a separate explicitly approved slice.

Likely Files Affected:
- main.py
- launch_jarvis_desktop.vbs
- desktop launcher entry files
- orchestration documentation

Scope:
- top-level boot orchestration design
- startup-to-desktop phase coordination

Out of Scope:
- current desktop-phase launcher stabilization
- folder reorganization
- voice or UI feature expansion

Notes:
Current planning truth already includes the minimal future boot-orchestrator stage model in `docs/architecture.md` and aligned boot-access planning language in `docs/boot_access_design.md`. That completed groundwork is now complete enough to pause. This item therefore remains deferred only for later implementation-facing planning or runtime work and should not be mixed into current desktop orchestration revisions.

---

### [ID: FB-005] Workspace and folder organization

Status: Deferred (partial implementation through Step 4)  
Priority: Low  
Suggested Version: v2.0  
Suggested Revision: rev1  

Description:
Continue staged project-directory cleanup for clarity and scalability while keeping top-level entrypoint and broader workspace restructuring deferred.

Why it matters:
As the project grows, clearer folder boundaries will make ownership, startup flow, audio systems, diagnostics, and future subsystems easier to maintain.

Proposed Change:
Carry workspace organization only through explicitly approved, path-sensitive slices rather than broad folder cleanup.

Likely Files Affected:
- multiple project directories
- startup scripts
- documentation references

Scope:
- folder and workspace organization
- path cleanup required by the reorganization

Out of Scope:
- orchestration policy changes
- feature additions
- unrelated refactors

Notes:
Current repo truth no longer reflects an untouched deferred item.
Completed slices now include:

- Step 3: `jarvis_desktop_main.py` and `jarvis_desktop_test.py` moved under `desktop/`, and the launcher's target-script assumption now points at the moved desktop entrypoint
- Step 4: `jarvis_voice.py` moved under `Audio/` as `Audio/jarvis_voice.py`
- Step 4: `main.py` now imports `Audio.jarvis_voice`
- Step 4: the launcher-owned diagnostics/error voice path remained valid and unchanged at `Audio/jarvis_error_voice.py`

Step 5 and broader workspace work remain intentionally deferred.
That means:

- `main.py` remains root-owned
- `launch_jarvis_desktop.vbs` remains root-owned
- broader folder cleanup, broader `Audio` casing normalization, and `logs/` reorganization remain out of scope until a later explicitly approved slice

---

### [ID: FB-006] Threshold-based recovery outcome summary refinement

Status: Implemented (v1.6.0)  
Priority: Low  
Suggested Version: v1.6.0  
Suggested Revision: TBD  

Description:
Refine final runtime and crash summaries so threshold-based early escalations are described differently from max-attempt exhaustion.

Why it matters:
Current final artifacts still use a generic recovery-outcome sentence even when recovery stopped early due to a specific launcher threshold.

Proposed Change:
Adjust launcher-generated summary wording so repeated STARTUP_ABORT escalation and repeated identical crash escalation produce threshold-specific recovery outcome text.

Likely Files Affected:
- jarvis_desktop_launcher.pyw

Scope:
- launcher-only
- summary wording refinement

Out of Scope:
- retry policy changes
- diagnostics UI changes
- renderer changes

Notes:
This should remain a reporting refinement only and must not change launcher behavior.

---

### [ID: FB-007] Max-attempt identical-failure attempt-pattern correction

Status: Implemented (v1.6.0)  
Priority: Low  
Suggested Version: v1.6.0  
Suggested Revision: TBD  

Description:
Correct the final failed-run attempt-pattern summary when all max recovery attempts end with the same non-threshold failure.

Why it matters:
The current fallback attempt-pattern wording can describe a stable repeated failure as varied, which weakens final summary accuracy.

Proposed Change:
Refine launcher attempt-pattern selection so max-attempt identical failures produce a stable repeated-failure pattern instead of the generic varied-failure pattern.

Likely Files Affected:
- jarvis_desktop_launcher.pyw

Scope:
- launcher-only
- summary wording correction

Out of Scope:
- retry policy changes
- threshold changes
- diagnostics UI changes
- renderer changes

Notes:
This should remain a reporting refinement only and must not change launcher behavior.

---

### [ID: FB-008] Shutdown voice degradation effect

Status: On Hold  
Priority: Low  
Suggested Version: TBD  
Suggested Revision: TBD  

Description:
Refine the existing staged degradation effect on the final "Shutting down" voice line so Jarvis sounds more convincingly like he is losing power during terminal shutdown.

Why it matters:
Shutdown-line tuning would make Jarvis feel more state-aware and physically present during failure termination without widening the diagnostics/error voice path.

Proposed Change:
Tune the existing shutdown-only voice envelope using staged slowdown, optional pitch drop, and final tail fade or hesitation. Keep the work limited to shutdown-line-only envelope refinement rather than first-time implementation or broader voice-path redesign.

Likely Files Affected:
- C:/Jarvis/Audio/jarvis_error_voice.py

Scope:
- shutdown voice-effect refinement
- final shutdown line only

Out of Scope:
- orchestration policy changes
- diagnostics behavior changes
- renderer changes

Notes:
Current repo truth already includes a dedicated shutdown-only effect path for the final "Shutting down." line inside the diagnostics/error voice script. This item now represents any future shutdown-envelope tuning on top of that existing path, not first implementation of a shutdown-specific branch.
This item is intentionally paused behind `FB-020` so the Dev Toolkit utility model and dev-only evidence-root cleanup can land first without mixing voice refinement into the current developer-surface rework.

---

### [ID: FB-009] Align crash-origin mixed markers with stable repeated-failure summaries

Status: Implemented (v1.6.0)  
Priority: Low  
Suggested Version: v1.6.0  
Suggested Revision: TBD  

Description:
Align mixed-pattern classification with final failed-run summaries when the failure cause stays identical across attempts but failure origin changes.

Why it matters:
The launcher can currently emit a mixed crash-pattern marker while the final summary intentionally describes the same run as a repeated identical failure, which weakens summary consistency.

Proposed Change:
Refine mixed crash-pattern classification so identical-cause runs that are intentionally summarized as repeated identical failure do not also emit a conflicting mixed-pattern interpretation unless that distinction is explicitly desired.

Likely Files Affected:
- jarvis_desktop_launcher.pyw

Scope:
- launcher-only
- reporting and classification consistency

Out of Scope:
- retry policy changes
- threshold changes
- diagnostics UI changes
- renderer changes

Notes:
This should remain a summary and classification consistency refinement only and must not change launcher behavior.

---

### [ID: FB-010] v1.6.0 closeout and documentation sync

Status: Implemented (v1.6.0)  
Priority: Medium  
Suggested Version: v1.6.0  
Suggested Revision: closeout  

Description:
Synchronize source-of-truth docs and backlog history with the final rev24 orchestration state before transitioning into v1.7.0.

Why it matters:
The launcher runtime is now internally consistent and stable, but the repo docs and backlog do not yet reflect the final implemented version state. A closeout sync reduces handoff risk and prevents future work from relying on outdated version context.

Proposed Change:
Update architecture and orchestration version context, record final verified scenario coverage, and move implemented v1.6.0 backlog items into completed history.

Likely Files Affected:
- C:/Jarvis/docs/architecture.md
- C:/Jarvis/docs/orchestration.md
- C:/Jarvis/docs/feature_backlog.md
- optional closeout note in C:/Jarvis/docs

Scope:
- documentation only
- backlog history and status sync
- version handoff clarity

Out of Scope:
- launcher policy changes
- renderer changes
- diagnostics UI changes
- new orchestration behavior

Notes:
This is the documentation-only closeout pass for the finalized `v1.6.0` orchestration layer.

---

### [ID: FB-011] Historical memory contract

Status: Implemented (v1.7.0)  
Priority: High  
Suggested Version: v1.7.0  
Suggested Revision: TBD  

Description:
Define the contract for a passive cross-run historical memory layer before any historical intelligence is implemented.

Why it matters:
Without a contract, later history, advisory, and diagnostics work can drift into a second truth source or become nondeterministic.

Proposed Change:
Define a versioned history schema, run identity rules, retention and reset rules, provenance requirements, and corruption fallback behavior for the cross-run memory layer.

Likely Files Affected:
- C:/Jarvis/docs/development_rules.md
- C:/Jarvis/docs/architecture.md
- C:/Jarvis/docs/orchestration.md
- future historical-memory implementation files

Scope:
- planning and architecture contract
- passive historical-memory rules

Out of Scope:
- runtime behavior changes
- retry changes
- escalation changes
- boot-level control

Notes:
This contract was defined in repo docs before implementation began and remains the governing rule for `v1.7.0` historical-memory work.

---

### [ID: FB-012] Failure fingerprint and recurrence model

Status: Implemented (v1.8.0)  
Priority: High  
Suggested Version: v1.8.0  
Suggested Revision: rev2  

Description:
Define how the system recognizes recurring outcomes across launches without changing the closed `v1.6.0` runtime classification model.

Why it matters:
Cross-run recurrence and trend analysis require stable fingerprint rules or historical intelligence will misclassify repeated failures.

Proposed Change:
Define failure fingerprint rules, recurrence grouping rules, and stability trend semantics for cross-run analysis using existing `v1.6.0` truth signals.

Likely Files Affected:
- C:/Jarvis/docs/architecture.md
- C:/Jarvis/docs/orchestration.md
- future historical-memory implementation files

Scope:
- cross-run identity
- recurrence tracking
- stability trend model

Out of Scope:
- runtime classification changes
- retry changes
- escalation changes

Notes:
This is now implemented through `v1.8.0 rev2a` and `v1.8.0 rev2b`, which together formalized the strict failure-fingerprint contract, strict recurrence equality, and deterministic recent-history stability model without reopening `v1.6.0` behavior. The next intended implementation track remains `FB-013`.

---

### [ID: FB-013] Advisory provenance and confidence semantics

Status: Implemented (v1.8.0)  
Priority: Medium  
Suggested Version: v1.8.0  
Suggested Revision: rev3  

Description:
Define how advisory outputs describe provenance, confidence, and evidence quality without becoming authoritative policy.

Why it matters:
Advisory intelligence can become misleading if the system does not clearly distinguish current-run truth, historical recurrence, and inference.

Proposed Change:
Define provenance labels and confidence semantics so confidence remains explanatory only and advisory outputs remain non-binding.

Likely Files Affected:
- C:/Jarvis/docs/development_rules.md
- C:/Jarvis/docs/orchestration.md
- future advisory-layer implementation files

Scope:
- advisory semantics
- provenance labels
- confidence meaning

Out of Scope:
- behavior changes
- retry changes
- escalation changes

Notes:
This is now implemented through `v1.8.0 rev3a` and `v1.8.0 rev3b`, which together formalized provenance-first advisory semantics and internal-only confidence meaning without introducing surfaced confidence output, runtime coupling, or policy significance. This completes `FB-013` for `v1.8.0`.

---

### [ID: FB-014] Multi-run orchestration regression harness

Status: Implemented (v1.8.0 rev1)  
Priority: Medium  
Suggested Version: v1.8.0  
Suggested Revision: rev1  

Description:
Create a reusable multi-run validation concept for historical-memory, diagnostics-enrichment, and advisory-only orchestration work.

Why it matters:
`v1.7.0` introduces cross-run reasoning, which requires repeatable multi-launch verification instead of only single-run scenario checks.

Proposed Change:
Define and later build a scenario-based regression harness that can validate recurrence, stability trends, fallback behavior, and advisory outputs across multiple launches.

Likely Files Affected:
- orchestration validation tooling
- documentation for scenario expectations

Scope:
- validation tooling
- multi-run scenario replay

Out of Scope:
- launcher policy changes
- renderer behavior changes
- UI redesign

Notes:
This was the safest first implementation target for `v1.8.0` and is now implemented as the validation-first harness foundation through rev1a, rev1b, and rev1c without reopening `v1.6.0` behavior. The next intended implementation track remains `FB-012`.

---

### [ID: FB-015] Boot and desktop phase-boundary model

Status: Deferred (rev1a clarification complete enough to pause)  
Priority: Medium  
Suggested Version: v2.0  
Suggested Revision: rev1a  

Description:
Define the conceptual boundary between future boot-stage orchestration and the already stabilized desktop-stage launcher layer.

Why it matters:
Later boot-level orchestration will need a clean contract for how boot-stage history, diagnostics, and advisory signals relate to desktop-stage truth.

Proposed Change:
For current repo truth, document phase-boundary rules, ownership boundaries, and downstream-input assumptions between a future boot orchestrator and the existing desktop launcher, then defer any later follow-through beyond that clarification.

Likely Files Affected:
- C:/Jarvis/docs/architecture.md
- C:/Jarvis/docs/orchestration.md
- future boot-orchestrator planning docs

Scope:
- architecture modeling
- future phase-boundary preparation

Out of Scope:
- boot-level control
- adaptive retry logic
- launcher behavior changes

Notes:
This remains preparation work only. Current planning truth already includes the architecture-level `FB-015 rev1a` phase-boundary contract in `docs/architecture.md` plus the aligned downstream-input contract in `docs/boot_access_design.md`. That clarification work is now complete enough to pause. Any later boot-planning follow-through remains deferred, this item must not introduce boot-level runtime control, and it still does not authorize `FB-004` implementation work.

---

### [ID: FB-016] Recorder-only historical memory groundwork

Status: Implemented (v1.7.0)  
Priority: High  
Suggested Version: v1.7.0  
Suggested Revision: rev1  

Description:
Implement the first passive historical-memory slice as a recorder-only layer with versioned schema scaffolding and zero readback into runtime behavior.

Why it matters:
This is the narrowest implementation step that proves the historical-memory architecture can record deterministic per-run facts without altering the finalized `v1.6.0` control model.

Proposed Change:
Add a write-only history recorder that stores finalized per-run outcomes using the `v1.7.0` historical memory contract, including schema versioning, run identity, failure fingerprint capture, and corruption-safe fallback behavior.

Likely Files Affected:
- C:/Jarvis/docs/architecture.md
- C:/Jarvis/docs/development_rules.md
- C:/Jarvis/docs/orchestration.md
- future historical-memory implementation files

Scope:
- recorder-only groundwork
- versioned schema scaffolding
- run identity capture
- failure fingerprint capture
- write-only passive recording

Out of Scope:
- diagnostics enrichment
- advisory recommendations
- historical summary output
- runtime behavior changes
- retry changes
- escalation changes

Notes:
Rev1 should record only finalized facts from the closed `v1.6.0` truth layer and must not read history back into control flow.
Implemented in `v1.7.0` rev1.

---

### [ID: FB-017] Support bundle and GitHub issue prefill

Status: Implemented (v1.9.0 rev1)  
Priority: Medium  
Suggested Version: v1.9.0  
Suggested Revision: rev1  

Description:
Add a user-friendly issue-reporting flow that generates a support bundle and opens a prefilled GitHub issue page.

Why it matters:
End users should be able to report crashes or failures without manually hunting for the right files. A guided support flow would keep reporting simple for users while giving developers a more consistent debug package.

Proposed Change:
Add a `Report Issue` flow that generates a support bundle containing the current runtime log, crash log, version, environment details, and a small manifest, then opens a prefilled GitHub issue form for the user to review and submit manually.

Likely Files Affected:
- issue reporting UI flow
- support bundle generation code
- diagnostics/support documentation
- optional GitHub issue template integration

Scope:
- support bundle generation
- GitHub issue prefill
- user-guided issue reporting flow

Out of Scope:
- silent log uploads
- fully automatic GitHub submission
- forced inclusion of internal historical-memory files
- unrelated diagnostics policy changes

Notes:
The first coherent manual reporting flow is now implemented as a privacy-safe diagnostics-window `Report Issue` action. It generates a local support bundle, writes the manifest, opens a prefilled GitHub issue page for manual completion, keeps attachment and submission manual, and includes a crash log only when the runtime-to-crash match is trustworthily determinable. The support bundle remains simple by default, with advanced/internal artifacts included only if explicitly needed later. The repo now also includes a contained offscreen validator for the production diagnostics `Report Issue` path that verifies support-bundle creation, manifest/manual-submission contract fields, and GitHub issue-prefill URL plus open-attempt handling without changing production behavior. That validator is now reachable through a dedicated VBS launcher and a report-aware lane in the accepted PySide dev toolkit.

---

### [ID: FB-018] Voice-path regression validation harness

Status: Implemented (v1.9.0 rev1)  
Priority: Medium  
Suggested Version: v1.9.0  
Suggested Revision: rev1  

Description:
Add a small contained regression harness for Jarvis voice-path validation across the current launcher and diagnostics/manual test lanes.

Why it matters:
Recent shutdown-line debugging showed that voice regressions can hide inside contained recovery flows even when the launcher still appears to behave correctly. A small voice-focused validation pass would catch missing final lines, broken status sync, bad effect output, or callback drift earlier.

Proposed Change:
Create a narrow validation path that exercises the current contained voice lanes and verifies expected `VOICE_SYNC` / `VOICE_FINAL` status output for the key launcher-owned lines without changing launcher policy or unifying the distinct normal-versus-diagnostics voice roles.

Likely Files Affected:
- developer validation tooling
- voice-path validation helpers
- optional docs for validation usage only if needed

Scope:
- contained voice regression validation
- launcher-owned failure-line verification
- diagnostics voice status verification

Out of Scope:
- voice redesign
- unifying normal and diagnostics voice behavior
- launcher retry or escalation policy changes
- broader devtools framework expansion

Notes:
The first coherent validation-first slice is now implemented as a contained voice regression harness. The repo now includes the harness script, a one-click VBS launcher, toolkit surfacing in the accepted PySide dev toolkit, launcher-owned repeated-crash and startup-abort lane coverage, direct diagnostics/error `VOICE_SYNC` / `VOICE_FINAL` probes, and stronger normal-voice direct-probe evidence beyond exit-code-only smoke validation. The current product direction still intentionally keeps the normal startup/desktop Jarvis voice path distinct from the diagnostics/error Jarvis voice path, so this item remains about guarding those paths, not merging them.

---

### [ID: FB-019] Support bundle to repro triage helper

Status: Implemented (v1.9.0 rev1)  
Priority: Medium  
Suggested Version: v1.9.0  
Suggested Revision: rev1  

Description:
Add a small internal triage helper that reads a user-generated support bundle and maps it to the closest known failure class and internal repro path.

Why it matters:
The implemented `Report Issue` flow now gives developers a consistent support bundle, but engineers still have to manually inspect the manifest, runtime log, and crash log to decide which existing harness or contained validation lane best matches the incident. A small dev-only triage helper would shorten the path from user report to reproducible engineering case without changing the end-user reporting flow.

Proposed Change:
Create a dev-only support-bundle triage helper that parses the support bundle manifest plus available runtime/crash artifacts, identifies the most likely launcher-owned failure class or validation lane, and emits a compact internal summary with suggested next repro steps.

Likely Files Affected:
- dev-only support bundle triage tooling
- support bundle manifest parser/helpers
- optional internal triage documentation if needed

Scope:
- dev-only bundle parsing
- failure-class suggestion
- harness/repro-path suggestion
- compact internal triage summary

Out of Scope:
- exact replay of the user machine state
- end-user UI changes
- silent uploads
- automatic GitHub issue submission
- launcher policy changes
- diagnostics UI redesign

Notes:
The first coherent `FB-019` slice is now implemented as a dev-only support-bundle triage helper plus a contained regression harness. The repo now includes support-bundle zip and extracted-folder intake, parsing of the existing manifest plus bundled runtime/crash artifacts, conservative classification for the current launcher-owned terminal failure classes, compact `.txt` / `.json` triage reports, and reusable validation coverage for supported cases plus safe `unknown` fallback. The raw helper is reachable through the accepted PySide dev toolkit, and the repo also includes a contained offscreen validator for that raw-helper toolkit flow that is reachable through a dedicated VBS launcher and a report-aware lane in the accepted PySide dev toolkit. Production support-bundle generation and the end-user `Report Issue` flow remain unchanged; this item is about faster internal mapping from production evidence to the right contained repro path.

---

### [ID: FB-020] Dev Toolkit utility split and dev-only evidence roots

Status: Implemented (v2.0 rev2)  
Priority: High  
Suggested Version: v2.0  
Suggested Revision: rev2  

Description:
Split the Dev Toolkit utility surface into stable global utilities versus lane-aware custom-launch utilities, add a separate previous-launch per-run history and exact-artifact reopen flow, and move toolkit-facing dev writes into dedicated `C:/Jarvis/dev/logs/<lane>/...` roots instead of the active client-facing `logs` / `crash` roots.

Why it matters:
The Dev Toolkit is easier to learn when stable navigation is separated from lane-dependent evidence, current-session utilities only appear when relevant, and historical runs can be reopened precisely without collapsing to the newest lane snapshot. Keeping developer-triggered runtime, report, and crash artifacts under `dev/logs` also prevents dev validation output from polluting the active client-facing `logs` area.

Proposed Change:
Implemented model:
- `Global Utilities` opens stable developer locations such as the Jarvis root, Dev folder, Dev logs root, and Dev launchers folder.
- `Custom Launch Utilities` follows the selected lane, stays hidden until relevant to the current selection, and only enables after that lane produces current-session evidence.
- current launch and previous-launch flows start in explicit chooser-based empty states rather than preselected lane state.
- `Previous Launches` is a true per-run history browser rather than a latest-per-lane snapshot.
- `Previous Launch Utilities` reopens the exact runtime, report, crash, or evidence-root artifacts for the selected saved run.
- toolkit-facing dev and test writes land under `C:/Jarvis/dev/logs/<lane>/...`
- lane-local crash artifacts stay under each lane root as `...\\crash`
- active client-facing `C:/Jarvis/logs` remains read-only investigation context where needed, such as support-bundle picking

Likely Files Affected:
- C:/Jarvis/dev/launchers/jarvis_dev_launcher.pyw
- C:/Jarvis/dev/launchers/launch_jarvis_diagnostics_manual_test.vbs
- C:/Jarvis/dev/launchers/launch_jarvis_launcher_failure_manual_test.vbs
- C:/Jarvis/dev/launchers/launch_jarvis_launcher_failure_manual_test_with_voice.vbs
- C:/Jarvis/dev/launchers/launch_jarvis_launcher_startup_abort_manual_test.vbs
- C:/Jarvis/dev/launchers/launch_jarvis_launcher_startup_abort_manual_test_with_voice.vbs
- directly relevant dev validation and harness scripts that define toolkit-facing evidence roots

Scope:
- Dev Toolkit utility split
- global versus lane-scoped utility boundaries
- previous-launch evidence reopen flow
- previous-launch true per-run history
- exact selected-run artifact reopening
- dev-only evidence-root migration under `dev/logs`
- lane-specific dev runtime/report/crash root normalization
- current empty-state and utility-visibility hardening needed to make the toolkit surface accurate and usable

Out of Scope:
- boot planning
- workspace reorganization
- production launcher log/crash policy changes
- support bundle contract redesign
- shutdown voice refinement

Notes:
Rev1 and rev2 are now implemented in code. The current repo truth uses lane-local crash folders under each lane root rather than a shared `dev/logs/crashes` bucket, and includes later Dev Toolkit UX hardening needed to make the split utility model usable without preselected state or stale artifact reopening. `FB-008` remains intentionally on hold behind this delivered toolkit and dev-evidence cleanup lane.

---

### [ID: FB-021] Dev-only Boot Jarvis test lane

Status: Implemented (v2.1.0 rev1)  
Priority: High  
Suggested Version: v2.1.0  
Suggested Revision: rev1  

Description:
Build out the dev-only Boot Jarvis test lane around `main.py` so boot/login behavior and the boot-to-desktop transition are faster to reproduce without turning `main.py` into the normal product entrypoint.

Why it matters:
Boot and transition testing is currently much slower than desktop-path testing unless the repo keeps a narrow internal harness model for `main.py`.

Proposed Change:
Implemented model:
- `main.py` now includes Phase 1 boot-harness seams for boot profile, audio mode, dedicated `dev/logs` runtime roots, structured `BOOT_MAIN|...` milestones, and auto-handoff skip-import support
- dev-only hidden-window boot launchers now exist under `dev/launchers/` for manual versus auto-handoff and quiet versus voice
- Boot Jarvis transition work stayed inside the dev-only harness and did not turn `main.py` into a normal product entrypoint

Likely Files Affected:
- C:/Jarvis/main.py
- C:/Jarvis/dev/launchers/launch_jarvis_main_*.vbs

Scope:
- dev-only boot/login harness support
- faster contained boot-to-desktop repro
- dedicated dev launchers for the existing boot prompt chain
- contained boot transition behavior and evidence inside the dev-only harness

Out of Scope:
- making `main.py` a user-facing launcher
- changing `launch_jarvis_desktop.vbs`
- trust or auth behavior changes
- full boot orchestrator implementation
- Dev Toolkit surfacing in the same slice

Notes:
This item is now implemented as a reusable dev-only boot test lane.
Current repo truth also includes later helper follow-through such as:

- monitor preflight
- boot-to-desktop handoff verification
- transition capture

Those later helper surfaces remain dev-only and still must not blur the line between the boot harness and the normal desktop launch path.

---

### [ID: FB-022] Boot & Transition Checks Dev Toolkit surfacing

Status: Implemented (v2.1.0 rev2)  
Priority: Medium  
Suggested Version: v2.1.0  
Suggested Revision: rev2  

Description:
Add a dedicated `Boot & Transition Checks` purpose group to the Dev Toolkit once the boot helper seams and launchers are stable enough to surface safely.

Why it matters:
The Dev Toolkit should eventually expose repeatable boot and transition checks without requiring direct file launches, but it should only surface stable helpers rather than inventing them inside the toolkit UI.

Proposed Change:
Implemented model:
- the Dev Toolkit now includes a dedicated `Boot & Transition Checks` purpose group
- it reuses the existing quiet/voice launch-mode model rather than inventing a separate boot audio system
- the current surfaced lanes are:
  - `Boot Jarvis Manual Flow`
  - `Boot Jarvis Auto Handoff (Skip Import)`
  - `Boot To Desktop Handoff Verification`
  - `Boot Transition Capture`
  - `Boot Monitor Preflight`
  - `Boot Helper Toolkit Validation`

Likely Files Affected:
- C:/Jarvis/dev/launchers/jarvis_dev_launcher.pyw
- C:/Jarvis/dev/launchers/launch_jarvis_main_manual_test*.vbs
- C:/Jarvis/dev/launchers/launch_jarvis_main_auto_handoff_skip_import*.vbs

Scope:
- Dev Toolkit purpose grouping for boot checks
- boot-specific lane surfacing after helper stability
- reuse of existing quiet versus voice launch-mode patterns

Out of Scope:
- inventing new boot helper seams inside the toolkit
- user-facing boot launchers
- trust or product behavior changes
- desktop launcher policy changes

Notes:
This item is now implemented.
Later Dev Toolkit follow-through in the same branch also added:

- Toolkit session runtime logging
- top-level smoke validation in a separate purpose group
- live background status/progress
- latest-artifact convenience utilities

Those later QoL additions build on this surfacing rather than changing its core ownership model.

---

### [ID: FB-023] Desktop renderer observability gap closure

Status: Implemented (v2.1.0 rev3)  
Priority: High  
Suggested Version: v2.1.0  
Suggested Revision: rev3  

Description:
Add the smallest missing renderer-side runtime markers for the controlled desktop path so renderer failures and shutdown behavior are easier to diagnose from logs.

Why it matters:
Current desktop logs cover startup well but remain thinner on page-load failure, desktop-mode attach results, and renderer-side shutdown milestones.

Proposed Change:
Implemented model:
- `desktop/desktop_renderer.py` now emits the first narrow renderer-side observability markers for:
  - visual page ready versus load failed
  - desktop mode enable begin
  - desktop attach result
  - renderer shutdown begin
- directly supportive WorkerW host-discovery probe evidence then landed to explain a real attach-path blind spot
- a guarded `Progman` fallback followed as machine-specific host-selection follow-through after the new markers surfaced the failed next-WorkerW assumption

Likely Files Affected:
- C:/Jarvis/desktop/desktop_renderer.py
- C:/Jarvis/desktop/jarvis_desktop_main.py

Scope:
- desktop renderer observability only
- missing failure-path and shutdown markers
- improved outcome clarity for the controlled desktop lane

Out of Scope:
- launcher policy changes
- boot-harness changes
- Dev Toolkit work
- raw verbosity increases
- UI redesign

Notes:
This item is now implemented as the first coherent desktop renderer observability slice, with directly supportive attach-path follow-through after the newly surfaced evidence showed the old WorkerW selection assumption was wrong on this machine.

---

### [ID: FB-024] Boot harness edge-path observability refinement
  
Status: Implemented (v2.1.0 rev4)  
Priority: Medium  
Suggested Version: v2.1.0  
Suggested Revision: rev4  

Description:
Fill in the remaining Boot Jarvis edge-path runtime markers so invalid prompt loops and interrupted handoff paths can be diagnosed without inferring behavior from missing happy-path milestones.

Why it matters:
The current boot harness now records the main happy path well, but unrecognized command loops, invalid import responses, and interrupted shutdown/handoff paths still leave evidence gaps.

Proposed Change:
Implemented model:
- `main.py` now emits the remaining narrow boot edge-path markers for:
  - rejected first-command input
  - rejected import yes/no input
  - typed shutdown accepted at command stage 1 or 2
  - hotkey-triggered shutdown
  - handoff signal emitted versus dropped
- the marker pass stayed inside the existing boot harness and did not redesign prompt flow or alter boot behavior

Likely Files Affected:
- C:/Jarvis/main.py

Scope:
- boot-harness milestone refinement only
- prompt edge-path evidence
- abnormal exit and interrupted handoff evidence

Out of Scope:
- prompt copy rewrite
- monitor preflight helper implementation
- desktop renderer changes
- Dev Toolkit surfacing
- trust or auth behavior changes

Notes:
 Current repo truth for this item includes:
  
- Phase 1 boot-harness seams in `main.py`
- structured `BOOT_MAIN|...` milestones across the happy path
- quiet and auto-handoff skip-import support
- dev-only boot launchers
- a more continuous boot-to-desktop handoff
- helper follow-through such as monitor preflight, handoff verification, transition capture, and boot-helper Toolkit validation
- landed edge-path markers for rejected input, shutdown source, and handoff signal outcome

Later naming cleanup remains deferred under `FB-025`.

---

### [ID: FB-025] Boot and desktop milestone taxonomy clarification

Status: Deferred  
Priority: Low  
Suggested Version: v2.1.0  
Suggested Revision: rev5  

Description:
Clarify the shared naming shape between `BOOT_MAIN|...` and `RENDERER_MAIN|...` milestone families once both lanes have enough core markers to make cross-lane evidence easier to compare.

Why it matters:
Boot and desktop ownership should stay separate, but a small later taxonomy pass could make mixed evidence easier to read without collapsing the two lanes into a single logging system.

Proposed Change:
Do a tiny naming and taxonomy clarification pass only after the core boot and desktop observability gaps are closed, preserving separate lane ownership while aligning milestone shape where that improves diagnostics.

Likely Files Affected:
- C:/Jarvis/main.py
- C:/Jarvis/desktop/jarvis_desktop_main.py
- C:/Jarvis/desktop/desktop_renderer.py

Scope:
- naming and taxonomy clarification only
- cross-lane diagnostic readability

Out of Scope:
- full shared logging contract implementation
- launcher policy changes
- raw verbosity increases
- behavior changes

Notes:
This remains deferred.
Current repo truth now already includes first-class `BOOT_MAIN|...` and `RENDERER_MAIN|...` milestone families, so this item is now only about later naming-shape cleanup and cross-lane readability rather than filling missing core marker coverage.

---

### [ID: FB-026] Dev Toolkit uploaded-bundle intake surface

Status: Deferred  
Priority: Medium  
Suggested Version: v2.1.0  
Suggested Revision: rev6  

Description:
Add a dedicated bottom-of-toolkit intake surface for user-submitted debug bundles so engineers can pick a zip or extracted folder, see what was received, and route it into the right internal helper without leaving the Dev Toolkit.

Why it matters:
The current toolkit already has support-bundle triage coverage, but intake still feels fragmented. A small, explicit uploaded-bundle area would make the toolkit feel like a one-stop internal debugging surface instead of a set of separate helper entrypoints.

Proposed Change:
Add a dedicated `Uploads` or similarly named lower-section panel in the Dev Toolkit that accepts a user-submitted zip or extracted bundle folder, shows the current selected source, and routes that source into the existing support-bundle triage helper or later bundle-specific follow-up helpers.

Likely Files Affected:
- C:/Jarvis/dev/launchers/jarvis_dev_launcher.pyw
- C:/Jarvis/dev/jarvis_support_bundle_triage.py
- directly supportive VBS/helper launcher surfaces only if needed

Scope:
- dev-only uploaded-bundle intake UI
- zip and extracted-folder picking
- clearer one-stop routing into existing bundle-debug helpers

Out of Scope:
- silent uploads
- cloud transfer or remote storage
- product-facing upload UI
- automatic issue submission redesign

Notes:
This remains deferred.
Current repo truth already includes:

- the existing support-bundle triage helper and its Toolkit surfacing
- Toolkit session logging
- live status/progress for background lanes
- latest-artifact convenience utilities

The remaining work is the dedicated lower intake surface itself, not the broader Toolkit foundation around it.

---

## Completed Items

Move completed backlog items here for history tracking.
