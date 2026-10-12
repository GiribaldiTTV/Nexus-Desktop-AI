# Nexus Orchestration

## Purpose

This document captures the orchestration-specific philosophy and current behavior boundaries of the Nexus desktop launcher stack.

It does not own:

- backlog identity
- roadmap sequencing

Use it for orchestration behavior and boundary truth.

## Current Orchestration Path

The current merged desktop orchestration path is:

`launch_orin_desktop.vbs`
-> `desktop/orin_desktop_launcher.pyw`
-> `desktop/orin_desktop_main.py`

This is the current runtime orchestration path, not a future boot-first shell path.

## Core Orchestration Philosophy

Build orchestration in this order:

1. observability
2. classification
3. control
4. outcome clarity
5. behavior

Do not skip stages.

The system should behave like:

- an observable system
- a controllable system
- a self-correcting system

not a black box.

## Current Control Boundaries

### Launcher-Owned

The launcher owns:

- startup observation
- readiness, stall, abort, and failure classification
- cooperative control
- recovery routing
- final runtime and crash truth generation

### Renderer-Owned

The renderer owns:

- desktop presentation
- renderer lifecycle milestones
- cooperative response to launcher signals
- clean renderer shutdown behavior

### Reporting Boundary

Current merged truth preserves:

- manual support-bundle handling
- manual issue submission
- no silent upload behavior
- no background reporting-policy expansion

### Recoverable Diagnostics Boundary

Current merged truth keeps recoverable diagnostics bounded.

That means:

- the shipped recoverable surface remains intentionally limited
- fatal launcher and runtime diagnostics behavior remains separate
- broader recoverable diagnostics expansion is not implied by the current architecture

## Runtime Outcome Model

Current orchestration still centers on:

- startup observation
- readiness detection
- stall detection
- cooperative startup abort
- failure classification
- launcher-owned recovery handling

The renderer remains reactive inside that model.

## Evidence And Logs

Current runtime evidence boundaries remain:

- live launcher/runtime truth under `<runtime root>/logs`
- live crash truth under `<runtime root>/logs/crash`
- dev, toolkit, and harness evidence under `<runtime root>/dev/logs/<lane>/...`
- normal historical state under `%LOCALAPPDATA%/Nexus Desktop AI/state/nexus_history_v1.jsonl`

The current desktop launcher resolves the live root from the repository/runtime root. Older `C:/Nexus/...` references remain historical wording unless an admitted implementation seam changes current path behavior.

## Future Orchestration Direction

Future orchestration work may later expand upward into:

- pre-desktop boot coordination
- access or trust framing
- post-login resident presence

But current merged orchestration truth remains the desktop launcher stack.

Any future higher layer must consume launcher truth downstream rather than rewriting launcher-owned outcomes.

