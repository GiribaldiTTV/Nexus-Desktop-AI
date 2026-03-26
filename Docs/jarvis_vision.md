# Jarvis Vision

## Core Product Goal

Jarvis is not intended to feel like a normal desktop app that opens after Windows.

The long-term goal is:

Windows boots
-> Jarvis startup and orchestration begins
-> Jarvis becomes the primary visible experience
-> the desktop exists underneath as the underlying operating system layer

Jarvis should feel like the system-facing layer, not just a program running on top of Windows.

## Experience Goal

The user experience should feel like:

- the machine is booting into Jarvis
- Jarvis is coming online as the interface layer
- Windows is present underneath, but not the star of the experience
- Jarvis transitions from boot presence into desktop presence cleanly

## Current Reality

Current architecture is still a staged desktop and orchestration subsystem:

`launch_jarvis_desktop.vbs`
-> `jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py`

This is not yet the final boot experience.
It is the current controlled orchestration path used to stabilize startup, recovery, and lifecycle behavior.

## Long-Term Direction

Jarvis should eventually own or coordinate:

- system startup presentation
- boot-to-desktop transition
- immersive visual handoff into the desktop state
- startup voice timing
- persistent desktop presence
- controlled recovery and diagnostics behavior

## Important Design Principle

Do not confuse the current launcher path with the final product vision.

Current launcher and orchestration work is foundation work.
It exists to make the future boot-to-Jarvis experience stable, observable, and controllable.

## Architectural Intent

Windows is the host platform.
Jarvis is the intended user-facing system layer.

That means future design should trend toward:

- Windows as infrastructure
- Jarvis as experience

not:

- Windows as experience
- Jarvis as just another application

## Scope Reminder

This vision does not mean all boot ownership should be implemented immediately.

Boot ownership, startup immersion, login and launch timing, shell behavior, and Windows integration should be handled as later dedicated revision tracks after orchestration is stable.

## Behavior Philosophy (Early Definition)

Jarvis should behave conservatively first:

- prefer cooperative control over forced control
- prefer staged escalation over immediate action
- prefer recovery over termination
- avoid aggressive retry loops without classification

Jarvis should not behave like a script.
Jarvis should behave like a system that understands its own state.

## Product Direction Reminder

The current desktop launcher path is a foundation layer, not the final identity of the product.

Future decisions should be checked against this question:

Does this make Jarvis feel more like the system-facing experience, or more like a normal Windows app?

If it only improves the app layer while drifting away from the system-layer vision, that tradeoff should be called out explicitly before implementation.
