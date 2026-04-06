# Nexus Desktop AI

This repository is the current engineering workspace for **Nexus Desktop AI**.

`Nexus Desktop AI` is the product/platform identity. `ORIN` is the shipped assistant persona for `pre-Beta` and `Beta`. `ARIA` is reserved as a future optional persona for `Full` and is not currently shipped.

Older legacy/internal releases and tags remain preserved as historical internal context. The future public product line begins later under `Nexus Desktop AI`; this README does not imply that public release work is already complete.

## Current Status

This repo is in active internal development.

What is currently true on this branch:
- the manual desktop launch path is working well enough for continued validation
- the dev/boot harness path remains separate from the normal desktop entrypoint
- diagnostics and Dev Toolkit flows exist to support internal testing and repair-first iteration

This is an engineering README, not a public product-launch page.

## Current Entry Paths

### Manual desktop launch path

The current manual desktop entry path is:

`launch_orin_desktop.vbs`  
`-> desktop/orin_desktop_launcher.pyw`  
`-> desktop/orin_desktop_main.py`

This is the current normal desktop entrypoint for manual runs.

### Dev Toolkit entry

The current Dev Toolkit entry is:

`dev\launchers\launch_orin_dev_toolkit.vbs`

The Dev Toolkit is an internal testing surface used for launch lanes, diagnostics, validation helpers, and related repair-first workflows.

### Boot/dev harness path

`main.py` is the current dev-only boot harness path.

It is not the normal user desktop entrypoint. It exists to support controlled boot-path testing, transition checks, and related internal validation work.

## Naming And Release Posture

- product/platform identity: `Nexus Desktop AI`
- shipped persona in `pre-Beta` and `Beta`: `ORIN`
- future persona option in `Full`: `ARIA`
- older legacy/internal releases and tags remain preserved as historical internal context
- the new public product line begins later under `Nexus Desktop AI`

## Repository Layout

Top-level folders currently include:
- `Audio/` for voice/audio code
- `desktop/` for launcher, renderer, runtime, and diagnostics surfaces
- `dev/` for toolkit, validators, harnesses, and related internal helpers
- `docs/` for project truth, architecture, backlog, and guidance
- the current visual assets and bridge-side UI resources
- `logs/` for local runtime artifacts

Top-level launch/runtime surfaces currently include:
- `launch_orin_desktop.vbs`
- `main.py`

## Current Working Boundary

This branch is being advanced through narrow, evidence-driven slices:
- preserve working launch paths first
- fix visible rebrand gaps before deeper cleanup
- keep runtime behavior stable while reducing outdated pre-rebrand user-facing surfaces
- defer larger UX, release, repo-rename, and public-launch work until separately approved

## Current Source Of Truth

For the current project truth and routing, use:
- `docs/Main.md`
- `docs/feature_backlog.md`
- `docs/orin_display_naming_guidance.md`
- `docs/orin_vision.md`
- `docs/user_test_summary_guidance.md`
