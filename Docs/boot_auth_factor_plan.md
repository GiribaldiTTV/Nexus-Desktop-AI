# Jarvis Boot Authentication Factor Plan

## Purpose

This document defines the next planning slice for `FB-004`.

`rev1d` is planning-only.
It does not choose backend design, credential storage, biometric stacks, shell integration, or implementation wiring.

Its job is to define:

- the conceptual primary auth-factor shape for routine consumer-Windows Jarvis login
- the stronger auth-factor shape for recovery or elevated-risk access states
- the acceptable user-experience envelope around those factor shapes
- what remains intentionally deferred until later auth and implementation planning

## Relationship To Prior Boot Planning

This document is downstream of:

- `FB-015 rev1a` phase-boundary clarification
- `FB-004 rev1a` boot entry-chain and handoff-topology planning
- `FB-004 rev1b` boot login, fallback, recovery, and resident-presence planning
- `FB-004 rev1c` trust-model planning

Those prior slices established that:

- Jarvis owns presentation
- real authentication owns trust
- typed input must always remain sufficient
- voice may support but never replace the trust action
- the primary trust family is explicit local knowledge-based secret entry

This slice narrows the factor shape inside that trust family.

## Product-Level Factor Objective

The Jarvis auth factor should feel:

- real
- explicit
- quick for routine use
- stronger when needed
- understandable to normal consumer users
- fully inside the Jarvis experience

The user should feel:

- "I completed a real access step."

The user should not feel:

- "I was roleplaying security with Jarvis."
- "I had to go through enterprise-style checkpoints."
- "Jarvis dropped me into a generic security interruption."

## Primary Routine Factor Shape

The safest conceptual primary factor shape for routine daily Jarvis login is:

- a short local access secret entered deliberately by the user

At planning level, that means:

- short enough for frequent daily use
- explicit enough to feel real
- stable enough to remain reliable across normal consumer environments
- simple enough to stay low-friction

This slice does not choose:

- exact secret format
- exact length
- exact character policy
- storage or reset mechanics

It defines only the product-level shape:

- short-form deliberate secret entry for routine access

## Why The Routine Factor Shape Is Acceptable

For consumer Windows daily use, the primary routine factor shape is acceptable because it is:

- easy to repeat
- easy to explain
- easy to complete by typing alone
- compatible with a fast path
- credible as a real trust action
- easy to keep inside Jarvis framing

It avoids:

- voice dependence
- vague conversational proof
- high-friction multi-step rituals
- business or enterprise-style complexity

## Stronger Or Recovery Trust Shape

The stronger trust shape for recovery or elevated-risk states should conceptually be:

- a longer-form deliberate secret entry reserved for stronger trust confirmation

At planning level, that means:

- more deliberate than the routine daily factor
- still knowledge-based
- still completable by typing alone
- still kept inside Jarvis presentation

This stronger shape is not meant for routine daily use.
It is a deliberate step-up trust mode for cases where the normal short-form factor is not enough.

## When The Stronger Path Is Justified

The stronger path should be justified only when the trust state is meaningfully different from normal daily access, such as:

- recovery-oriented access states
- post-bypass or access-restoration flows
- unusual trust conditions that should not be treated like routine daily entry

This slice does not define the exact detection logic for those states.
It defines only that the stronger factor belongs to non-routine trust situations, not the everyday fast path.

## Typed And Voice Relationship Around The Factor

Typed input remains the certainty path.

The following must always be completable by typing alone:

- routine factor entry
- stronger factor entry
- access continuation through the trust step

Voice may support:

- greeting
- pacing
- guidance
- confirmation
- emotional tone

Voice must not:

- replace the factor
- act as sufficient proof on its own
- become a hidden requirement for routine or stronger access

## Fast-Path User-Experience Envelope

The fast path is the routine daily path.

It should feel like:

- a concise Jarvis acknowledgment
- one short explicit access secret
- a smooth transition into authenticated desktop presence

The fast path should avoid:

- long ceremony
- multiple trust gestures
- repeated confirmations
- spoken requirements
- theatrical delays

## Stronger-Path User-Experience Envelope

The stronger path should still feel like Jarvis, but it may be:

- slower than the routine path
- more deliberate
- more clearly marked as a higher-trust or recovery-oriented step

Even then, it should not become:

- enterprise-style challenge flow
- multi-screen bureaucracy
- a generic non-Jarvis interruption
- an excuse to pile on multiple unrelated trust checks

## In-Bounds Planning Shapes

The following are in-bounds for this slice:

- short-form deliberate secret entry for routine access
- longer-form deliberate secret entry for stronger or recovery-oriented access
- one primary factor for daily access
- a stronger factor shape reserved for non-routine trust states
- Jarvis-framed presentation around both factor shapes

## Out-Of-Bounds Planning Shapes

The following should be treated as out-of-bounds or insufficient for this factor slice:

- freeform conversation as the factor
- voice identity as the primary factor
- passive recognition as the primary factor
- invisible or background trust decisions as the primary factor
- multi-step enterprise challenge patterns for routine consumer access
- piling routine access and recovery access into the same default path

The following also remain out of scope for this slice:

- biometric-first factor design
- concrete multi-factor implementation
- storage policy
- backend selection
- reset mechanics
- shell-linked trust behavior

## What Makes A Factor Too Weak

A factor shape is too weak if:

- it can be confused with greeting or conversation
- the user cannot tell what actually granted access
- it depends on mood, wording, or performative interaction
- it feels like Jarvis "decided" access without deliberate proof

## What Makes A Factor Too Annoying

A factor shape is too annoying if:

- it takes too long for normal daily use
- it adds ritual instead of trust
- it requires more than one routine trust act
- it requires speech
- it feels more like admin friction than personal-machine access

## What Makes A Factor Too Enterprise-Like

The factor model becomes too enterprise-like if it assumes:

- repeated challenge escalation during normal login
- complex multi-step confirmation by default
- business-style compliance posture
- high-friction trust choreography for routine personal use

Consumer-Windows daily access should remain simpler and more humane than that.

## How The Factor Stays Inside Jarvis Presentation

The factor stays inside Jarvis presentation when:

- Jarvis remains the visible frame
- the factor appears as part of the Jarvis flow
- the user is not forced through a detached generic-feeling security interruption
- the atmosphere supports the trust step without replacing it

The correct balance remains:

- Jarvis owns framing
- the factor provides proof
- access depends on the factor

## Explicit Deferrals For Later Revisions

`rev1d` intentionally defers:

- exact secret format decisions
- credential storage design
- backend and validation design
- biometric integration details
- multi-factor implementation details
- device-trust implementation
- shell integration
- fallback implementation details
- post-bypass recovery implementation details
- tray or resident app implementation details

## Risks And Blockers

### Trust Risks

- choosing a factor so vague that it feels theatrical
- choosing a factor so loose that users cannot tell what granted access
- blurring the routine factor and the stronger factor into one confused path

### Friction Risks

- making the routine factor too burdensome
- making the stronger factor too common
- letting cinematic framing slow down daily access

### Planning Risks

- solving storage or backend questions too early
- sneaking biometric or device-trust design into the baseline
- overfitting to rare recovery states before the daily factor is stable

## What Success Looks Like

A successful factor-shape plan would make the user feel:

- I know what the routine access step is
- I know what the stronger access step is
- the routine path is fast enough for everyday use
- the stronger path feels justified when it appears
- both still feel like Jarvis
- neither feels fake or enterprise-heavy

## Recommended Next Planning Step After Rev1d

After this factor-shape baseline, the next coherent planning revision should narrow one of:

- exact routine factor envelope and acceptable UX boundaries
- stronger-path justification and recovery trust-state detail
- resident trust-state surfacing after login

It should not try to solve all three in the same revision.
