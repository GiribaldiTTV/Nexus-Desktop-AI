# Incident Patterns

## Purpose

This document captures short reusable debugging and validation patterns extracted from closed workstreams.

It is a generalized knowledge layer, not a case-history diary.

Use:

- canonical workstream docs for the full story of a specific lane
- this document for reusable symptom-to-fix patterns
- the relevant canonical workstream doc first for branch-local reuse notes, artifact guidance, and seam history

Add material here only when the lesson has generalized beyond one lane.
Branch-local "what worked" notes should stay in the canonical workstream doc first and only be distilled here once the pattern is broad enough to help future branches outside that lane.

## Pattern: PR Readiness Green Must Require Durable Process Truth

- symptom:
  PR Readiness can appear green while required canon sync, post-merge state handling, docs changes, PR creation, or PR validation still have not completed
- layer:
  branch governance, merge-target canon, and PR-state validation
- root-cause pattern:
  validation proves branch behavior or produces a copy-ready PR package, but process blockers are not named strongly enough as pre-merge gates
- fix pattern:
  require PR Readiness to clear stale canon, post-merge-state handling, next-workstream selection with minimal scope and no branch created yet, dirty branch / durable commit state, docs-sync / Governance Drift Audit blockers, PR creation, and PR validation before reporting `PR READY: YES` or `PR Readiness GREEN`; `PR package ready` is not green, missing PRs carry `PR Creation Pending`, unknown PR inspection carries `PR State Unknown`, and unresolved live PR issues carry `PR Validation Pending`
- validation pattern:
  run the normal branch governance validator plus the PR-readiness gate mode; the gate must fail while the worktree is dirty, while required post-merge truth is not encoded, while the next workstream is undefined, unscoped, or already branched, while the PR does not exist, or while PR state cannot be inspected
- source references:
  - `Docs/phase_governance.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Release Readiness Green Must Require Explicit Release Target

- symptom:
  Release Readiness can appear green while the branch has not yet named the release version, release floor, version rationale, bounded release scope, or release artifacts it is supposed to package, or while the named target is semantically wrong
- layer:
  branch governance and release-facing canon
- root-cause pattern:
  release-debt truth is present, but release-bearing branch records lack machine-checkable markers that prove the release target is explicit and semantically correct before green status
- fix pattern:
  require release-bearing branches to declare `Release Target:`, `Release Floor:`, `Version Rationale:`, `Release Scope:`, and `Release Artifacts:`; validate target semantics from the latest public prerelease and declared floor; allow `Release Branch: No` only for preserved historical records
- validation pattern:
  run the branch governance validator; it must fail release-packaging branch records that omit release target markers, declare a semantically wrong target, or use the non-release waiver outside preserved historical records

## Pattern: Release Readiness File Mutation Must Backflow

- symptom:
  Release Readiness discovers missing release target, scope, artifact, canon, helper, or release-note truth and patches files while the authority record still says `Release Readiness`
- layer:
  release readiness boundary and phase backflow
- root-cause pattern:
  canon treated release target/scope/artifact definition as something Release Readiness could repair in-place instead of analysis-only output or a blocker that returns to the owning earlier phase
- fix pattern:
  treat Release Readiness as analysis-only for repository files; it may produce release package information in the response, but any required source, docs, canon, validator, helper, release-note, or handoff-file mutation must return to `PR Readiness` before merge or defer to the next active branch's `Branch Readiness` after merge
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; it must enforce `Release Readiness File Mutation Attempt` file-freeze language in governance docs and fail if tracked files are dirty while an active authority record says `Release Readiness`
- source references:
  - `Docs/phase_governance.md`
  - `Docs/development_rules.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Escaped PR Work Blocks Next Branch Readiness

- Trigger:
  PR Readiness misses required canon, branch-authority cleanup, post-merge truth, or next-branch deferral work, and the miss is discovered during Release Readiness, after merge, on updated `main`, or after the next branch was created
- Risk:
  Release Readiness becomes a docs-sync phase, repair work leaks between branches, direct `main` writes become tempting, or a governance-only branch becomes a side door around the active phase machine
- Common Cause:
  PR Readiness checks prove behavior or release artifacts but do not prove that merged-main branch records, roadmap state, post-merge state, and selected-next branch timing are already durable before green
- Required Response:
  classify the issue as `PR Readiness Scope Missed`; if it appears during Release Readiness, also classify `Release Readiness Scope Drift`; if a successor branch already exists, keep that branch in `Branch Readiness` and repair the miss before any implementation begins
- Prevention:
  block governance-only branches, block between-branch canon repair, block all Codex direct `main` writes, require branch-authority cleanup before PR green, and extend the validator whenever a miss exposes a machine-checkable gap
- source references:
  - `Docs/phase_governance.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Merged-Unreleased Release Debt Must Be Durable Before Release Readiness

- symptom:
  an implementation workstream is merged or squash-merged, but canon still represents it as an active PR Readiness branch and Release Readiness must rediscover the release target, scope, artifacts, or release-debt owner
- layer:
  merge-target canon, roadmap release posture, workstreams index, and branch governance validation
- root-cause pattern:
  PR Readiness recorded future post-merge prose but did not leave machine-checkable merged-unreleased release-debt fields in the exact post-merge shape that `main` needs after merge
- fix pattern:
  require `Merged-Unreleased Release-Debt Owner:`, `Repo State: No Active Branch`, `Release Target:`, `Release Floor:`, `Version Rationale:`, `Release Scope:`, `Release Artifacts:`, `Post-Release Truth:`, `Selected Next Workstream:`, and `Next-Branch Creation Gate:` before PR green when a branch will merge unreleased implementation work
  validate release target semantics from the latest public prerelease and declared release floor before PR green
- validation pattern:
  run `python dev/orin_branch_governance_validation.py` plus the PR-readiness gate mode; the validator must fail if a promoted merged-unreleased workstream remains under Active, lacks release target/floor/rationale/scope/artifacts, carries a semantically wrong release target, or if `main` carries tracked file mutation during Codex work
- source references:
  - `Docs/phase_governance.md`
  - `Docs/prebeta_roadmap.md`
  - `Docs/workstreams/index.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Protected Main Must Stay Read-Only For Codex

- symptom:
  escaped canon drift makes direct `main` repair look faster than a branch-carried fix
- layer:
  branch governance, release readiness boundary, and protected-branch safety
- root-cause pattern:
  older governance left room for emergency direct-main repair, which can bypass PR review and make protected branch truth harder to audit
- fix pattern:
  `main` is protected for Codex work; there is no emergency direct-main repair path, and any required file mutation must ride the still-available prior branch or the next active branch's `Branch Readiness`
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; it must enforce protected-main language and fail with `Main Write Attempt` if tracked file mutation exists while Codex is on `main`
- source references:
  - `Docs/phase_governance.md`
  - `Docs/Main.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Validation Helper Sprawl Must Collapse Into Registered Helper Families

- symptom:
  a feature branch creates seam-specific live validators or helper scripts even though an existing validator family already covers the same desktop, authoring, launcher, or interaction surface
- layer:
  validation helper governance and Workstream evidence
- root-cause pattern:
  the repo requires reuse-first validation, but without a helper registry and naming tiers, a successful seam helper can become accidental permanent tooling
- fix pattern:
  register durable root `dev/` helpers in `Docs/validation_helper_registry.md`, require standardized names and `Helper Status:` values, and force workstream-scoped helpers to declare owner, reason, consolidation target, and promotion decision point
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; it must fail when helper standardization language is missing or a root `dev/` validation/helper script is unregistered
- source references:
  - `Docs/validation_helper_registry.md`
  - `Docs/phase_governance.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: User Test Summary Pending Must Block Final Green

- symptom:
  automated validators and live helpers pass, but final phase output implies the branch can advance before the filled User Test Summary results are submitted and digested
- layer:
  validation evidence digestion and phase governance
- root-cause pattern:
  canon requires returned user evidence digestion, but without a named blocker the result can be summarized as all-green even though the user-facing handoff is still outstanding
- fix pattern:
  require the named blocker `User Test Summary Results Pending`, record `User Test Summary Results: PENDING` in the active authority record, and report that automated/live evidence is green while final phase advancement remains blocked
- validation pattern:
  run `python dev/orin_branch_governance_validation.py` plus the PR-readiness gate mode; the PR gate must fail while `User Test Summary Results Pending` is active or while the result marker is missing for a relevant user-facing Live Validation or PR Readiness workstream
- source references:
  - `Docs/user_test_summary_guidance.md`
  - `Docs/phase_governance.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: UTS Waivers Must Live In The Exact Canonical Artifact

- symptom:
  Live Validation or PR Readiness records `User Test Summary Results: WAIVED` or `User-Facing Shortcut Validation: WAIVED`, but the waiver lives in recap prose, `## User Test Summary Strategy`, or a validation-contract paragraph rather than the exact canonical `## User Test Summary` section
- layer:
  workstream-owned validation evidence, response contract, and branch governance validation
- root-cause pattern:
  the branch has a valid no-meaningful-manual-test rationale, but validator parsing trusts loose markers outside the canonical UTS artifact, allowing the response/output contract to drift
- fix pattern:
  require an exact `## User Test Summary` section for active `Live Validation` and `PR Readiness` workstreams; require `User Test Summary Waiver Reason:` for UTS waivers and `User-Facing Shortcut Waiver Reason:` for shortcut waivers
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; it must fail if `## User Test Summary Strategy` is present but the exact canonical `## User Test Summary` section lacks the required result and waiver-reason markers
- source references:
  - `Docs/phase_governance.md`
  - `Docs/development_rules.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Desktop Shortcut Gate Must Precede User Test Summary Handoff

- symptom:
  validators, live helpers, and direct-runtime launches pass, but the user-facing desktop shortcut path later exposes a visibility, startup, or discoverability failure
- layer:
  Live Validation proof hierarchy and User Test Summary handoff
- root-cause pattern:
  helper evidence proves branch behavior through controlled launch paths, but the final user entrypoint is not named as a machine-checkable gate before `UTS` handoff
- fix pattern:
  require the `User-Facing Shortcut Live Validation Gate`, record `User-Facing Shortcut Path:` and `User-Facing Shortcut Validation:`, and keep `User-Facing Shortcut Validation Pending` active until the declared shortcut or equivalent user entrypoint passes or is explicitly waived before User Test Summary handoff
- validation pattern:
  run `python dev/orin_branch_governance_validation.py` plus the PR-readiness gate mode; relevant desktop user-facing Live Validation and PR Readiness records must fail if the shortcut result is missing, pending, or failed
- source references:
  - `Docs/user_test_summary_guidance.md`
  - `Docs/phase_governance.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Released-Canon Fallback Must Not Use The Highest Planned Prerelease

- symptom:
  support bundles or issue drafts can report an unreleased baseline when `.git` metadata is unavailable
- layer:
  support reporting and release-context derivation
- root-cause pattern:
  fallback logic trusts sequencing or planning truth as if it were released-canon truth
- fix pattern:
  derive fallback release context from the latest released prerelease truth, not from the highest planned prerelease target
- validation pattern:
  prove both `git`-present and `git`-unavailable report-artifact paths resolve to the same released public prerelease truth
- source references:
  - `Docs/workstreams/FB-035_release_context_fallback_hardening.md`
  - `Docs/prebeta_roadmap.md`

## Pattern: Post-Release Canon Must Close Released Release Debt

- symptom:
  a public prerelease tag and GitHub prerelease exist, but canon still reports the released workstream as merged-unreleased release debt or leaves latest public prerelease at the prior tag
- layer:
  post-release confirmation and release-state canon
- root-cause pattern:
  PR Readiness defines pre-release target/scope/artifacts but does not include a machine-checkable release-state closure plan that forces latest public prerelease, released/closed workstream state, and release-debt clearing after the tag exists
- fix pattern:
  during PR Readiness for release-bearing work, require a release-state closure plan that covers latest public prerelease, released/closed workstream state, release-debt clearing, workstream-index movement to Closed, and successor branch deferral; after a release tag exists, the governance validator must fail stale release-debt canon
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; it must fail if the latest local pre-Beta tag is newer than roadmap latest public prerelease, or if the released workstream remains promoted/merged-unreleased instead of closed/released
- source references:
  - `Docs/prebeta_roadmap.md`
  - `Docs/feature_backlog.md`
  - `Docs/workstreams/index.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Architecture-Only Milestones Must Not Force Minor Prerelease Bumps

- symptom:
  a planning, architecture, admission-contract, validation-only, or non-user-facing milestone advances the public pre-Beta version by a minor bump even though no executable, runtime, operator-facing, user-facing, or materially expanded product capability lane was delivered
- layer:
  release-floor governance, PR Readiness release-target semantics, and validator enforcement
- root-cause pattern:
  source-of-truth treats "opens a lane" or "defines architecture" as equivalent to delivering a new capability lane, so `Release Floor: minor prerelease` can pass marker checks without proving user-visible or executable product expansion
- fix pattern:
  make `patch prerelease` the default for architecture-only planning, admission contracts, validation-only work, documentation/canon repair, governance repair, and non-user-facing milestones; require `minor prerelease` rationale to name a new executable, runtime, operator-facing, user-facing, or materially expanded product capability lane
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; the validator must fail a merged-unreleased owner that declares `Release Floor: minor prerelease` while its rationale/scope is architecture-only or non-user-facing without an executable or user-facing capability marker
- source references:
  - `Docs/phase_governance.md`
  - `Docs/prebeta_roadmap.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Pre-Beta Release Title Format Is Concise

- symptom:
  post-release confirmation compares the GitHub release title against a long PR-generated milestone title and treats the published concise title as drift
- layer:
  release artifacts and post-release confirmation
- root-cause pattern:
  source-of-truth does not record the public GitHub prerelease title format separately from release-note summary content
- fix pattern:
  use `Pre-Beta v<major>.<minor>.<patch>` as the public GitHub release title format for Nexus pre-Beta releases; put milestone name, user-facing scope, capabilities, behavior, and evidence in inclusion-only release notes
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; release artifacts and released-state canon should use the concise title format while release notes carry the scoped milestone summary
- source references:
  - `Docs/closeout_guidance.md`
  - `Docs/prebeta_roadmap.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Repeated-Identical Recoverable launch_failed Must Stay Bounded

- symptom:
  a repeated recoverable `launch_failed` class starts pulling diagnostics policy toward blanket popup or fatal-path behavior
- layer:
  recoverable diagnostics surface and failure-class handling
- root-cause pattern:
  a bounded high-signal recoverable class is treated as permission to widen every recoverable failure into the same diagnostics surface
- fix pattern:
  keep the selected incident class explicit, preserve the manual reporting boundary, and keep fatal launcher and runtime diagnostics behavior separate
- validation pattern:
  prove only the selected repeated-identical `launch_failed` class gets the intended recoverable handling while fatal-path behavior remains unchanged
- source references:
  - `Docs/workstreams/FB-034_recoverable_diagnostics.md`
  - `Docs/architecture.md`

## Pattern: Green Multi-Seam Workflows Must Continue Until Blocked

- symptom:
  Codex completes and validates one seam inside a valid bounded multi-seam Workstream sequence, then stops because the prompt named only the entry seam or the output format asks for a next safe move
- layer:
  seam workflow governance, prompt interpretation, and active workstream phase truth
- root-cause pattern:
  source-of-truth required a continue-or-stop decision, but did not make next-seam continuation the default after a green seam; validator enforcement only checked for broad multi-seam markers and missed prompt-as-terminal ambiguity
- fix pattern:
  define `Next-Seam Continuation Required` as the default after a green seam, treat prompt-named seams inside approved sequences as entry seams rather than terminal boundaries, and require a recorded bounded stop condition, phase boundary, stop-loss trigger, or canon-valid `Single-Seam Fallback` before stopping
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; governing docs and prompt scaffolds must include `Next-Seam Continuation Required`, entry-seam language, default-continuation language, bounded stop conditions, and `Single-Seam Fallback` as a bounded stop decision rather than category stop authority
- source references:
  - `Docs/phase_governance.md`
  - `Docs/development_rules.md`
  - `Docs/codex_modes.md`
  - `Docs/orin_task_template.md`
  - `Docs/codex_user_guide.md`
  - `dev/orin_branch_governance_validation.py`

## Pattern: Category-Based Single-Seam Fallback Stops Healthy Chains

- symptom:
  Codex completes and validates an admitted architecture or planning seam, then stops solely because the seam is labeled UI-model, launcher, protocol, settings, high-risk, or cross-subsystem
- layer:
  seam workflow governance and validator enforcement
- root-cause pattern:
  source-of-truth treated risk categories as automatic `Single-Seam Fallback` authority instead of requiring a concrete bounded stop condition
- fix pattern:
  keep bounded multi-seam continuation as the default after green seams; use category labels to require smaller seams and stronger gates, not to stop an otherwise valid chain
- validation pattern:
  run `python dev/orin_branch_governance_validation.py`; the validator must reject governance docs that recreate category-based fallback stop authority
- source references:
  - `Docs/phase_governance.md`
  - `Docs/development_rules.md`
  - `Docs/codex_modes.md`
  - `Docs/orin_task_template.md`
  - `Docs/codex_user_guide.md`
  - `dev/orin_branch_governance_validation.py`
