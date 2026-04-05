# ORIN Display Naming Guidance

## Purpose

This document is the canonical source-of-truth guidance for when display surfaces should use:

- `ORIN`
- `O.R.I.N.`
- `Operational Response and Intelligence Nexus`

It is a presentation and wording guide only.
It does not authorize broad source renames, internal identifier rewrites, or repo-wide wording sweeps by itself.

## Naming Boundary

Product/tooling shell identity remains:

- `Nexus Desktop AI`

Assistant persona identity remains:

- `ORIN`

This means:

- use `Nexus Desktop AI` for product-level, tooling-shell, or platform identity
- use ORIN naming guidance only where the assistant persona itself is being presented

## Default Short Form

Use `ORIN` as the default short-form display name when:

- the assistant persona is being named in normal UI copy
- a readable, natural display name is preferred
- the wording is title-like, label-like, or user-facing rather than trace-like
- future lane labels, helper names, or persona headers need the short persona form

`ORIN` should be treated as the default short-form persona label unless a more specific rule below applies.

## Stylized Acronym Form

Use `O.R.I.N.` when:

- the surface should feel more technical, machine-like, or system-coded
- acronym styling improves the presentation
- the wording is trace-like, command-like, or intentionally high-signal
- the user should feel the assistant identity in a more synthetic/system-facing tone

Preferred examples:

- command-surface naming
- diagnostics trace or state wording
- other deliberate acronym-emphasis surfaces

## Full Expansion

Use `Operational Response and Intelligence Nexus` when:

- the full meaning adds clarity
- the surface is header-like, explanatory, or identity-revealing
- the user is being reminded what ORIN stands for
- a more formal persona identity treatment is desired

Preferred examples:

- persona detail headers
- explanatory diagnostics sections
- future vision or presentation docs on first mention when helpful

## Current Diagnostics Direction

Current preferred direction from diagnostics validation:

- the diagnostics voice-trace area header may prefer the full expansion:
  - `Operational Response and Intelligence Nexus`
- diagnostics trace and state text should prefer:
  - `O.R.I.N.`

Future diagnostics wording changes should use this direction unless a later explicit planning decision replaces it.

## Future Persona Rule

If ARIA is later exposed as a user-facing persona, it should follow the same three-form model:

- default short form
- stylized acronym form if needed
- full expansion when explanatory or header clarity is useful

Do not assume the exact ARIA presentation rules are finalized yet.

