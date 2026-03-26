# Jarvis Architecture

## Architectural Context

The current startup path is the stabilized desktop orchestration path, not the final product vision.

Current path:

`launch_jarvis_desktop.vbs`
-> `jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py`

Long-term vision:
Windows boot and login should transition into Jarvis as the primary user-facing layer, with Windows remaining the underlying platform.

## Startup Path

`launch_jarvis_desktop.vbs`
-> `jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py` (renderer)

## Future Boot Orchestrator Boundary

A future top-level boot orchestrator may sit above the current desktop launcher stack to coordinate:

- Windows boot and login handoff
- Jarvis startup presentation
- transition into the desktop phase
- future phase-to-phase health decisions

Until that higher-level system is explicitly designed, the desktop launcher remains the owner of:

- desktop-phase readiness observation
- desktop-phase stall handling
- desktop-phase cooperative control
- desktop-phase recovery routing

## System Roles

### Launcher (`jarvis_desktop_launcher.pyw`)

Responsible for:

- process orchestration
- startup observation
- classification (ready / slow / stall / abort / failure)
- control (cooperative abort)
- recovery and retry flow
- runtime and crash logging

### Renderer (`jarvis_desktop_main.py`)

Responsible for:

- UI and desktop rendering
- emitting lifecycle milestones
- responding to cooperative abort signal
- clean shutdown behavior

## Lifecycle Model

1. Startup begins
2. Launcher observes readiness
3. Renderer signals readiness
4. Launcher confirms state
5. System runs
6. Shutdown or failure occurs
7. Launcher handles outcome

## Startup Classification

- `STARTUP_READY_OBSERVED` -> healthy
- `NOT_OBSERVED_WITHIN_WINDOW` -> slow
- `STALL_CONFIRMED` -> stalled
- `STARTUP_ABORTED` -> controlled abort
- failure path -> crash or exception

## Control System

- Launcher owns control signals
- Renderer responds cooperatively
- No hard kill unless explicitly designed later

## Recovery Model

- Failed startup attempts enter recovery flow
- Recovery is handled by launcher
- Renderer remains simple and reactive

## Design Rule

The launcher is the brain.
The renderer is the body.

## System Layer Model

Jarvis is built as layered control over Windows:

Windows (host platform)
-> Launcher (orchestration and control)
-> Renderer (visual and interaction layer)
-> Future systems (voice, AI, user interaction)

Design rule:
Higher layers depend on lower layers, but lower layers must remain simple and stable.

The launcher controls behavior.
The renderer executes behavior.

## Version Context

`v1.6` orchestration work established the startup-control foundation in stages:

- production entry separation
- lifecycle instrumentation
- launcher observation
- startup classification
- cooperative control
- outcome classification
- recovery routing
- first automatic stall response

This staged build order should be preserved in future subsystems when possible.
