# Nexus Desktop AI

This repository is the engineering workspace for `Nexus Desktop AI`.

`Nexus Desktop AI` is the product and tooling-shell identity.
`ORIN` is the current shipped assistant persona for the pre-Beta product line.
`ARIA` remains a future optional persona rather than a currently shipped surface.

This README is a repository orientation document.
For merged governance, planning, routing, and lifecycle truth, start with `Docs/Main.md`.

## Current Product And Runtime Truth

Current repo truth includes:

- a manual desktop launch path for the current desktop runtime
- a separate Dev Toolkit surface for controlled testing and diagnostics work
- a dev-only boot harness path used for boot-flow and transition validation
- current pre-Beta delivery under the Nexus Desktop AI / ORIN identity

Latest public prerelease:

- `v1.2.8-prebeta`

## Current Entry Paths

### Manual Desktop Launch

The normal manual desktop entry path is:

`launch_orin_desktop.vbs`
`-> desktop/orin_desktop_launcher.pyw`
`-> desktop/orin_desktop_main.py`

### Dev Toolkit

The Dev Toolkit launcher is:

`dev/launchers/launch_orin_dev_toolkit.vbs`

The Dev Toolkit is an internal engineering surface for validators, diagnostics, launch helpers, and repair-first workflows.

### Boot Harness

`main.py` remains the dev-only boot harness entry.

It is used for controlled boot-path testing and related validation.
It is not the normal user desktop entrypoint.

## Repository Layout

Top-level folders currently include:

- `Audio/` for voice and audio code
- `desktop/` for launcher, renderer, interaction, and diagnostics runtime surfaces
- `dev/` for toolkit surfaces, validators, harnesses, and internal helpers
- `Docs/` for source-of-truth, architecture, planning, and guidance
- `jarvis_visual/` for current visual assets and bridge-side UI resources
- `logs/` for local runtime artifacts

## Source-Of-Truth Routing

Use the merged canon through:

- `Docs/Main.md` for routing authority
- `Docs/development_rules.md` for development governance
- `Docs/codex_modes.md` for collaboration and analysis/execution posture

From there, route into the layer that owns the truth you need:

- `Docs/feature_backlog.md` for tracked identity and registry state
- `Docs/prebeta_roadmap.md` for sequencing and release posture
- `Docs/workstreams/index.md` for canonical workstream records
- `Docs/closeout_index.md` and `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.2.8-prebeta.md` for historical and epoch summaries

## Naming Boundary

Use:

- `Nexus Desktop AI` for the product, repo, and tooling shell
- `ORIN` for the current assistant persona

Older `Jarvis` references remain only where they are:

- preserved historical context
- still-real runtime artifact names
- intentionally retained compatibility references

## Repository Boundary

This repository contains the engineering and canon surfaces for the product.

It is not, by itself:

- a release checklist
- a public marketing page
- a substitute for the source-of-truth stack in `Docs/`

When repo orientation and source-of-truth docs disagree, validate live repo truth first and then route through `Docs/Main.md`.
