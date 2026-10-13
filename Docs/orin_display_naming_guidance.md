# ORIN Display Naming Guidance

## Purpose

This document defines how user-facing surfaces should present the ORIN persona.

Use it to decide when display surfaces should use:

- `ORIN`
- `O.R.I.N.`
- `Operational Response and Intelligence Nexus`

It is a presentation and wording guide only.
It describes visible product naming; implementation details live with the affected feature.

## Relationship To The Source-Of-Truth Stack

This document is a reference layer under:

- `Docs/nexus_vision.md` for product and persona identity
- `Docs/architecture.md` and `Docs/orchestration.md` for boundary truth

It should be used to support wording decisions, not to replace those layers.

## Naming Boundary

Product/tooling shell identity remains:

- `Nexus Desktop AI`

Assistant persona identity remains:

- `ORIN`

This means:

- use `Nexus Desktop AI` for product-level, tooling-shell, or platform identity
- use ORIN naming guidance only where the assistant persona itself is being presented
- keep legacy `Nexus` wording only where the reference is historical or where a still-real runtime artifact continues to use that name

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

Current preferred diagnostics direction:

- the diagnostics voice-trace area header may prefer the full expansion:
  - `Operational Response and Intelligence Nexus`
- diagnostics trace and state text should prefer:
  - `O.R.I.N.`

Use this as the default diagnostics direction unless later merged canon explicitly replaces it.

## Current Boot Reveal Evaluation

Current preferred boot-reveal direction:

- the assistant reveal title may be better as:
  - `O.R.I.N.`
- the reveal subtitle should remain:
  - `Operational Response and Intelligence Nexus`

This is not yet a universal hard rule.
Treat it as a targeted display preference for the boot reveal surface rather than a global naming override.

## Future Persona Rule

If ARIA is later exposed as a user-facing persona, it should follow the same three-form model:

- default short form
- stylized acronym form if needed
- full expansion when explanatory or header clarity is useful

Do not assume the exact ARIA presentation rules are finalized yet.

## Boundary Reminder

This document should not be used to:

- decide when a naming change ships
- rewrite preserved historical records that intentionally keep older naming
