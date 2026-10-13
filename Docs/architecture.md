# Nexus Architecture

## Purpose

This document defines current architectural boundaries and long-term architectural direction for Nexus Desktop AI.

It does not own:

- backlog identity
- roadmap sequencing

Use this doc for boundary truth and system design.

## Current Runtime Reality

The current controlled desktop runtime path is:

`launch_orin_desktop.vbs`
-> `desktop/orin_desktop_launcher.pyw`
-> `desktop/orin_desktop_main.py`

This is the active stabilized runtime path on merged truth.
It is not yet the final boot-first product experience.

Historical note:

- older Nexus-named releases and docs remain preserved as historical context
- they do not override the current runtime path above

## Architectural Layer Model

Current architecture should be read as:

Windows host platform
-> Windows-facing launch shim
-> desktop launcher
-> desktop renderer
-> support, diagnostics, history, and interaction-support subsystems

Design rule:

- higher layers may consume lower-layer truth
- lower layers must not be reinterpreted by higher layers after the fact

## Current Ownership Boundaries

### Launch Shim

`launch_orin_desktop.vbs` is the Windows-facing entry shim for the current desktop runtime path.

It is a launcher entry surface, not a planning or control owner.

### Desktop Launcher

`desktop/orin_desktop_launcher.pyw` owns:

- startup observation
- readiness, stall, abort, and failure classification
- cooperative control
- recovery routing
- finalized runtime and crash truth generation

The launcher remains the authority for desktop-phase orchestration.

### Desktop Renderer

`desktop/orin_desktop_main.py` owns:

- desktop rendering
- visible desktop lifecycle milestones
- cooperative response to launcher control
- clean shutdown behavior inside the renderer layer

The renderer does not own retry, escalation, or final run classification.

### Reporting And Diagnostics Surfaces

Current merged truth keeps:

- support-report generation under launcher and support-reporting ownership
- recoverable diagnostics bounded to the currently shipped surface
- fatal launcher and runtime diagnostics separate from bounded recoverable handling
- manual reporting and manual issue submission as the current reporting boundary

### Historical State

Normal runtime history resolves under:

- `%LOCALAPPDATA%/Nexus Desktop AI/state/nexus_history_v1.jsonl`

That historical filename is still part of current runtime truth even though the product framing is Nexus Desktop AI and ORIN.

## Root Logs And Evidence Boundaries

Current approved live launcher surfaces resolve under the runtime root's ignored `logs/` directory:

- `<runtime root>/logs`
- `<runtime root>/logs/crash`

Those roots remain the current runtime truth for:

- launcher-generated runtime logs
- matching crash logs
- launcher control or status files when relevant

In source, the desktop launcher resolves this from the repository/runtime root through `DEFAULT_LOG_DIR = os.path.join(ROOT_DIR, "logs")`. Historical `C:/Nexus/...` wording may appear in older records from the Nexus-named runtime era, but it does not override current root-relative launcher code truth.

Launcher-owned historical state is no longer a root-logs surface during normal runtime.

Developer, worker, toolkit, and harness evidence belongs under:

- `<runtime root>/dev/logs/<lane>/...`

That separation is part of the current architecture, not just a docs convention.

## Future Boot-Orchestrator Boundary

A future top-level boot orchestrator may sit above the current desktop launcher stack to coordinate:

- Windows boot and login handoff
- pre-desktop presentation
- access or trust framing before desktop delegation
- post-delegation observation

That future layer must remain above the launcher boundary.

It may:

- observe launcher-emitted downstream truth
- narrate or frame the handoff
- coordinate the transition around the launcher

It must not:

- override launcher-owned desktop truth
- reinterpret launcher-owned final state
- inject cross-layer control back into the launcher

Desktop-stage authority begins when execution is delegated to the desktop launcher.

## Current Design Principles

The architecture should continue to preserve this order when evolving subsystem behavior:

1. observability
2. classification
3. control
4. outcome clarity
5. behavior

And it should continue to preserve this boundary rule:

- launcher is the desktop-phase control authority
- renderer is the desktop-phase presentation authority
