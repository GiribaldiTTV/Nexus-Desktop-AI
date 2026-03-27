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

Status: Deferred  
Priority: Medium  
Suggested Version: Post-v1.7.0  
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
This remains intentionally deferred and should not be mixed into the advisory-only `v1.7.0` track.

---

### [ID: FB-003] Retry limit and diagnostics escalation policy

Status: Deferred  
Priority: Medium  
Suggested Version: Post-v1.7.0  
Suggested Revision: TBD  

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
This remains intentionally deferred and should not be mixed into the advisory-only `v1.7.0` track.

---

### [ID: FB-004] Future boot orchestrator layer

Status: Deferred  
Priority: High  
Suggested Version: TBD  
Suggested Revision: TBD  

Description:
Design and implement top-level boot orchestration above the desktop launcher.

Why it matters:
The long-term product direction is for Jarvis to feel like the system-facing experience, with a higher-level boot flow coordinating the transition into the stabilized desktop phase.

Proposed Change:
Introduce a future boot orchestrator layer that sits above the desktop launcher and coordinates boot presentation, phase transitions, and higher-level startup policy.

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
This is a later architecture track and should not be mixed into the current desktop orchestration revisions.

---

### [ID: FB-005] Workspace and folder organization

Status: Deferred  
Priority: Low  
Suggested Version: TBD  
Suggested Revision: TBD  

Description:
Restructure project directories for clarity and scalability.

Why it matters:
As the project grows, clearer folder boundaries will make ownership, startup flow, audio systems, diagnostics, and future subsystems easier to maintain.

Proposed Change:
Reorganize project directories and documentation locations with a dedicated, approved workspace-organization pass.

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
This remains intentionally deferred until after active orchestration stabilization work.

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

Status: Deferred  
Priority: Low  
Suggested Version: TBD  
Suggested Revision: TBD  

Description:
Add a staged degradation effect to the final "Shutting down" voice line so Jarvis sounds like he is losing power during terminal shutdown.

Why it matters:
A shutdown degradation effect would make Jarvis feel more state-aware and physically present during failure termination.

Proposed Change:
Implement a controlled shutdown voice envelope using staged slowdown, optional pitch drop, and final tail fade or hesitation. Prefer segmented delivery over a single linear slowdown so the effect is more reliable and easier to tune.

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
This should be handled as a dedicated voice and experience revision after orchestration stabilization, not mixed into launcher-control work.

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

Status: Deferred  
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
This should be the first `v1.7.0` implementation track.

---

### [ID: FB-012] Failure fingerprint and recurrence model

Status: Deferred  
Priority: High  
Suggested Version: v1.7.0  
Suggested Revision: TBD  

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
This should build directly on the historical memory contract.

---

### [ID: FB-013] Advisory provenance and confidence semantics

Status: Deferred  
Priority: Medium  
Suggested Version: v1.7.0  
Suggested Revision: TBD  

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
This should remain advisory-only throughout `v1.7.0`.

---

### [ID: FB-014] Multi-run orchestration regression harness

Status: Deferred  
Priority: Medium  
Suggested Version: v1.7.0  
Suggested Revision: TBD  

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
This future-proofs `v1.7.0` without reopening `v1.6.0` behavior.

---

### [ID: FB-015] Boot and desktop phase-boundary model

Status: Deferred  
Priority: Medium  
Suggested Version: v1.7.0  
Suggested Revision: TBD  

Description:
Define the conceptual boundary between future boot-stage orchestration and the already stabilized desktop-stage launcher layer.

Why it matters:
Later boot-level orchestration will need a clean contract for how boot-stage history, diagnostics, and advisory signals relate to desktop-stage truth.

Proposed Change:
Document phase-boundary rules, ownership boundaries, and data-sharing assumptions between a future boot orchestrator and the existing desktop launcher.

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
This is preparation work only and must not introduce boot-level runtime control in `v1.7.0`.

---

## Completed Items

Move completed backlog items here for history tracking.
