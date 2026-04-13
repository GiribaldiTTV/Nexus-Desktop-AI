# Nexus Pre-Beta Rebaseline Through v1.2.9-prebeta

## Purpose

This document is the modern Nexus-era rebaseline through `v1.2.9-prebeta`.

Its job is to:

- summarize the current shared pre-Beta baseline
- capture what is locked versus deferred
- reduce prompt bloat by replacing repeated lane recaps
- point back to preserved historical closeouts without rewriting them

## Baseline Scope

This rebaseline covers merged shared truth through the released public prerelease:

- `v1.2.9-prebeta`

It stands on top of the preserved historical closeout line indexed in:

- `Docs/closeout_index.md`

## Material Closed Workstreams In This Baseline

The closed workstreams that materially define the current baseline are:

- `Docs/workstreams/FB-028_history_state_relocation.md`
- `Docs/workstreams/FB-033_startup_snapshot_harness_follow_through.md`
- `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md`
- `Docs/workstreams/FB-034_recoverable_diagnostics.md`
- `Docs/workstreams/FB-035_release_context_fallback_hardening.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`

## What Is Locked Now

Through `v1.2.9-prebeta`, current shared truth includes:

- launcher-owned historical state is not a live root-logs surface
- the startup snapshot harness is a bounded dev-only and opt-in debugging surface
- boot and desktop milestone taxonomy remains clarified without collapsing ownership boundaries
- one recoverable-operational-incident class is closed and shipped:
  - repeated identical `launch_failed` for the same action in a still-running session
- support-report fallback now derives release context from released-canon truth instead of the highest planned prerelease target
- the manual-reporting boundary remains local and manual only
- the typed-first desktop interaction baseline is explicit and validator-defended
- built-in actions and saved actions resolve through one shared action catalog
- the first bounded interaction capability milestone is released:
  - first-class URL target support for saved actions without changing exact-match resolution, state-machine boundedness, or input-capture behavior
- the later bounded FB-027 follow-through is also released:
  - saved-action inventory and guided access
  - built-in-vs-saved distinction in choose and confirm
  - saved-source health visibility for missing, invalid, template-only, and colliding states
  - directly coupled validator expansion for inventory, origin, and source-state visibility

## What Remains Deferred

This rebaseline does not authorize automatic continuation into:

- saved-action authoring UX
- broader resolution-quality follow-through
- interaction-clarity follow-through
- shutdown exit-confirmation work
- hotkey cleanup before Beta
- broader reporting-policy or upload-behavior work
- broader boot-layer implementation work
- broader interaction, rebrand, voice, or UI follow-through by inertia

## Forward-Planning Posture After This Baseline

Current merged truth is again between released non-doc implementation lanes.

The next implementation workstream must be chosen from refreshed backlog, workstream, interaction, and product-boundary truth rather than by continuing the released FB-027 lane by inertia.

## Historical Relationship

The preserved historical Jarvis closeout line remains valid historical context.

Use:

- `Docs/closeout_guidance.md` for closeout and rebaseline policy
- `Docs/closeout_index.md` for historical closeout lookup

This document does not rewrite those historical closeouts.

## Carry-Forward Rule

Future prompts should usually treat this rebaseline plus the retained workstream records as the modern carry-forward baseline through `v1.2.9-prebeta` instead of replaying each closed lane narrative in full.
