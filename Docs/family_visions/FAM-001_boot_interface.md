# FAM-001 Boot Interface Vision

## Purpose

This family vision records durable product direction for startup, boot, desktop entrypoint, single-instance ownership, launch handoff, relaunch semantics, lifecycle transition proof, boot-to-runtime trust boundaries, fatal launcher/runtime diagnostics, and recovery surfaces.

## Vision Summary

Boot Interface work should make Nexus feel reliable at startup without pretending the current desktop launcher is already the final boot-first product shell. The user should understand when Nexus starts, recovers, relaunches, or hands off control.

## Accepted Direction

- Preserve the current desktop orchestration path until a later USER-approved boot-facing package changes it.
- Prefer recoverable startup and truthful failure reporting over hidden automation.
- Keep boot-first behavior user-controlled before Beta.
- Make handoff, relaunch, and single-instance behavior explicit and testable.
- Own fatal launcher/runtime diagnostics and recovery surface direction when Nexus reaches startup abort, recovery exhaustion, crash/failure finalization, support-bundle preparation, manual issue reporting, retry/close/repair choices, or user-facing recovery explanation.
- Treat FB-034 recoverable `launch_failed` as released historical evidence for one bounded non-crashing incident class, not as active authority for broad diagnostics/recovery product scope.
- Future diagnostics and recovery UI should have clear behavior, visual consistency, privacy-safe evidence, and tested failure paths before release.

## Implementation Boundaries

This vision does not itself implement bootloader, sign-in, installer, Windows startup mutation, or a broad fatal/recoverable diagnostics redesign. Visible recovery panels use the shared Nexus presentation grammar while each feature owns its own failure, degraded, blocked, and unavailable states.

## Canonical Pointers

- Project vision: `Docs/nexus_vision.md`
- Backlog registry: `Docs/feature_backlog.md`
- Roadmap posture: `Docs/prebeta_roadmap.md`
