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

Status: Deferred  
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
This should follow, not precede, the repeated identical crash policy.

---

### [ID: FB-003] Retry limit and diagnostics escalation policy

Status: Deferred  
Priority: Medium  
Suggested Version: v1.6.0  
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
This should build on the specific repeated-failure classifications already established.

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

Status: Deferred  
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

## Completed Items

Move completed backlog items here for history tracking.
