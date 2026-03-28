# Jarvis Boot Login, Recovery, and Resident Presence Plan

## Purpose

This document defines the next planning slice for `FB-004`.

`rev1b` is planning-only.
It does not define implementation details, auth storage, shell integration, tray implementation, renderer wiring, or boot runtime control.

Its job is to define:

- the intended consumer-Windows Jarvis-first login experience
- how typed and voice interaction coexist in one shared flow
- how authentication remains real and meaningful without breaking the Jarvis atmosphere
- how fallback and recovery work without trapping the user outside Windows
- what role a resident Jarvis presence should play after desktop entry

## Product Intent

Jarvis should feel like the primary visible system presence on the machine.

The intended user perception is:

- the machine feels like it is entering Jarvis, not launching a normal app
- Jarvis stays visually and interactively present during access
- successful login transitions into authenticated Jarvis desktop presence
- Windows remains the host platform, but not the dominant visible identity during entry

This is a consumer-Windows model.
It is not an enterprise, domain, or business access model.

## Governing Framing

This planning slice follows two core rules:

- Jarvis owns presentation
- real authentication owns trust

The user should experience both as one continuous Jarvis-controlled flow.

That means:

- the user should not feel like Jarvis disappears and a generic login replaces it
- the trust action must still be explicit and real
- the trust action must not be reduced to vague conversational theater

## Core Design Principles

- cinematic but fast
- immersive but dependable
- voice is presence, typing is certainty
- one shared auth flow, not two separate systems
- real authentication without breaking the Jarvis atmosphere
- Windows-safe fallback
- guided recovery that feels supportive, not punitive
- consumer Windows first, not enterprise
- Jarvis must never trap the user outside Windows

## Consumer Windows Assumptions

This design should assume:

- ordinary personal-machine use
- varied hardware quality
- users who may not always want to speak aloud
- users who may forget Jarvis credentials
- users who may need a low-friction fallback path
- users who still need safe access to their Windows machine even if Jarvis access fails

The design should therefore prioritize:

- clarity
- resilience
- recoverability
- local usability
- low-friction daily access

## Experience Layer Versus Trust Layer

Jarvis login must distinguish between:

- experience-layer interaction
- trust-layer authentication

### Experience Layer

The experience layer includes:

- greeting
- visual presence
- conversational framing
- voice presence
- ambient feedback
- animated transitions
- identity acknowledgment at the presentation level

### Trust Layer

The trust layer includes:

- the explicit access check
- the proof required to continue
- the transition from pre-access presence into authenticated desktop entry

The experience layer should frame the trust layer.
It should not replace it.

## Dual-Modality Input Contract

Jarvis login and recovery must support both typed and voice interaction.

This is one shared interaction system, not two separate login products.

### Typed Input

Typed input must always remain available and sufficient.

The following must always be completable by typing alone:

- normal login
- the real trust action
- fallback selection
- recovery initiation
- post-bypass recovery completion
- access to later resident recovery and settings surfaces

Typed input is the certainty path for:

- privacy
- reliability
- noisy environments
- microphone failure
- recovery situations

### Voice Input

Voice may enhance:

- presence
- greeting
- guidance
- confirmation
- pacing
- hands-busy convenience

Voice must never be required for:

- access
- trust completion
- fallback use
- recovery completion

### Shared Flow Rule

Typed and voice input must feed the same conceptual flow:

- same identity state
- same auth state
- same recovery state
- same transition into desktop presence

The user should never feel like there is a separate "voice login" and "typed login."

## Real Authentication Contract

Jarvis must use a real, explicit authentication step.

At the planning level, that means:

- access is granted only after a deliberate trust action
- the trust action is clearly meaningful
- conversation alone is not enough to count as authentication
- the trust action remains inside Jarvis presentation rather than breaking into a disconnected flow

What counts as cinematic interaction:

- greeting
- identity acknowledgment
- voice guidance
- atmosphere
- transition framing

What counts as real authentication:

- the explicit trust action that determines whether access is granted

The trust action should feel like:

- "Jarvis granted access after a real check"

It should not feel like:

- "Jarvis pretended to know me and waved me through"

## Intended Normal Login Shape

The intended normal login path is:

1. Jarvis presence appears
2. Jarvis acknowledges the user in a concise cinematic way
3. the user performs one explicit trust action
4. Jarvis confirms access
5. Jarvis transitions into authenticated desktop presence

The normal path should optimize for:

- speed
- clarity
- confidence
- continuity of atmosphere

## Fast Path Versus Rich Path

The design should support both a fast path and a richer path.

### Fast Path

Routine daily access should favor:

- one primary trust action
- minimal delay
- no unnecessary ritual
- a short transition into desktop presence

### Rich Path

A richer path may be appropriate for:

- first-run introduction
- reauthentication
- recovery
- unusual trust state
- deliberate dramatic presentation moments

The daily default should remain the fast path.

## Fallback And Safety Contract

Jarvis must not become the only rescue path to Windows access.

A Windows-safe fallback path must always exist.

If Jarvis authentication is:

- forgotten
- unavailable
- temporarily unusable
- intentionally bypassed

the user must still be able to reach Windows safely.

Jarvis is the preferred front door.
It must not become the only emergency exit.

## Post-Bypass Recovery Contract

If the user reaches Windows through the fallback path instead of normal Jarvis authentication, Jarvis should detect that state after desktop entry at a conceptual level.

After detection, Jarvis should surface a guided recovery flow inside the resident Jarvis environment.

That recovery flow should:

- explain that normal Jarvis secure access was bypassed or unavailable
- offer a clear path to restore Jarvis access
- allow limited postponement without silently leaving the trust state broken

The tone must be supportive, not punitive.

The experience should feel like:

- "Let's restore your Jarvis access"

not:

- "You failed security"

## Recovery Design Principles

Recovery should be:

- clear
- guided
- low-friction
- recoverable
- accessible by typing alone

Recovery should not be:

- hidden
- accusatory
- voice-dependent
- easy to dismiss forever
- buried in deep settings

## Resident Jarvis Presence After Login

After desktop entry, Jarvis should continue to exist as a visible resident presence inside Windows.

At the planning level, that resident layer should be treated as:

- a visible app/process presence
- a future tray anchor
- the home for recovery prompts
- the home for settings and status
- the persistent trust and control anchor after entry

Long-term intent:

- Jarvis appears as a real app/process
- Jarvis is visible in Task Manager
- Jarvis later has a tray role
- Jarvis feels like a legitimate resident assistant rather than a one-time login effect

## Resident Layer Responsibilities

The future resident Jarvis presence should later act as the home for:

- secure access state
- recovery guidance and reset entry
- user-facing settings
- status surfaces
- quick access to Jarvis controls

The tray role remains implementation-deferred, but conceptually it belongs to this resident control layer rather than the boot flow itself.

## Low-Friction Rule

Jarvis should feel advanced without creating daily friction.

The design standard should be:

- one primary trust action
- no unnecessary ceremony on routine use
- no mandatory voice use
- no long theatrical delays
- no artificial complexity disguised as immersion

The design should favor:

- confidence
- speed
- atmosphere
- clarity

not:

- ritual
- repetition
- security theater

## Explicit Deferrals For Later Revisions

`rev1b` intentionally defers:

- auth backend design
- credential storage design
- biometric design
- shell replacement or shell integration details
- tray implementation details
- startup voice implementation details
- visual animation implementation details
- renderer wiring
- launcher changes
- boot runtime control
- retry or escalation behavior above the launcher
- diagnostics presentation redesign

## Risks And Blockers

### Experience-Layer Risks

- making the login too theatrical for daily use
- making voice feel mandatory even when it is optional
- making the system feel slow or fragile
- letting persona outweigh usability

### Auth/Trust Risks

- fake-feeling authentication
- trust ambiguity between conversation and real access control
- too many trust steps for routine use
- breaking immersion with a disconnected generic-feeling auth interruption

### Fallback/Recovery Risks

- creating lockout risk
- making fallback available but socially or visually discouraged
- making post-bypass recovery too easy to ignore forever
- giving the user no stable later place to restore normal Jarvis access

## What Success Looks Like

A successful design would make the user feel:

- Jarvis stayed present the whole time
- I completed a real trust step
- I never felt dumped out of the Jarvis experience
- I could always type if voice was inconvenient
- I could still reach Windows safely if Jarvis access failed
- Jarvis helped me recover afterward if I had to bypass normal access
- Jarvis remained present after login as a real system layer

## Recommended Next Planning Step After Rev1b

After this planning slice, the next coherent planning revision should narrow one specific area:

- auth-factor and trust-shape planning
- fallback and post-bypass recovery-flow planning
- resident app and tray responsibility planning

It should not try to solve all three at once.
