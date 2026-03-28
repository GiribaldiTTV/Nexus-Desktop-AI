# Jarvis Boot Routine Authentication UX Plan

## Purpose

This document defines the next planning slice for `FB-004`.

`rev1e` is planning-only.
It does not choose backend design, credential storage, biometrics, shell integration, or implementation wiring.

Its job is to define:

- the acceptable daily-use UX envelope for the routine Jarvis trust step
- how fast the routine path should feel
- what counts as acceptable versus excessive ceremony
- what visual and conversational framing is appropriate around the routine trust step
- what remains intentionally deferred until later auth and implementation planning

## Relationship To Prior Boot Planning

This document is downstream of:

- `FB-015 rev1a` phase-boundary clarification
- `FB-004 rev1a` boot entry-chain and handoff-topology planning
- `FB-004 rev1b` boot login, fallback, recovery, and resident-presence planning
- `FB-004 rev1c` trust-model planning
- `FB-004 rev1d` auth-factor planning

Those prior slices established that:

- Jarvis owns presentation
- real authentication owns trust
- typed input must always remain sufficient
- voice may support presence but never replace the trust step
- the routine factor is a short-form deliberate local secret
- the stronger path is reserved for non-routine trust states

This slice narrows only the daily-use UX envelope around the routine factor.

## Product-Level Routine UX Objective

The routine Jarvis trust path should feel:

- fast
- calm
- deliberate
- clearly real
- visually continuous
- low-friction for everyday use

The user should feel:

- "Jarvis recognized I was returning, asked for one real access step, and let me in."

The user should not feel:

- "I had to perform a cinematic ritual every time."
- "I got dumped into generic security UI."
- "Jarvis made me wait just to prove it was futuristic."

## Routine Path Envelope

At planning level, the routine path should conceptually fit into three short beats:

1. concise Jarvis presence
2. explicit routine trust action
3. immediate confirmation and transition

This should remain the default daily path.
Anything that materially expands beyond those three beats should be treated as exceptional rather than normal.

## How Fast The Routine Path Should Feel

The routine trust path should feel:

- immediate to begin
- brief to complete
- smooth to exit

At planning level, "fast" means:

- no waiting period whose purpose is only dramatic effect
- no multi-step trust choreography for normal daily use
- no repeated confirmation sequence after the routine factor is accepted
- no conversational detour required before access can proceed

The routine path may feel intentional.
It must not feel slow.

## Acceptable Ceremony

The routine trust path may include a small amount of ceremony if it supports identity, continuity, and atmosphere.

Acceptable ceremony includes:

- a concise greeting or acknowledgment
- visual continuity with the Jarvis boot presence
- short optional voice framing
- a brief confirmation after successful trust completion

Acceptable ceremony must remain:

- short
- skippable through normal pace
- non-blocking
- subordinate to the trust step rather than competing with it

## Excessive Ceremony

The routine trust path becomes excessive when it includes:

- long pre-auth narration
- multiple staged confirmations
- repeated identity theater
- extended ambient delay before the trust step
- forced spoken interaction
- decorative actions that do not add trust or usability

If the user feels they are performing Jarvis instead of accessing Jarvis, the ceremony has gone too far.

## Before, During, And After The Trust Step

### Before

Before the routine trust step, Jarvis should provide:

- immediate presence
- concise acknowledgment
- a clear path into the routine factor

Before the trust step, Jarvis should avoid:

- long monologues
- narrative exposition
- setup-like questioning
- recovery-like behavior during normal access

### During

During the routine trust step, Jarvis should provide:

- a clear prompt for the factor
- stable visual focus
- optional short voice guidance
- minimal surrounding noise or distraction

During the trust step, Jarvis should avoid:

- multiple simultaneous asks
- conversational branching
- theatrical interruptions
- anything that obscures what action actually grants access

### After

After successful routine trust completion, Jarvis should provide:

- short acknowledgment
- immediate transition into authenticated desktop presence

After the trust step, Jarvis should avoid:

- unnecessary victory laps
- repeated confirmations
- extra post-auth checkpoints in the normal path

## Typed Input As The Certainty Path

Typed input remains the certainty path throughout the routine trust step.

The following must remain completable by typing alone:

- entry into the routine factor
- completion of the routine factor
- continuation into authenticated access

Typed input should feel:

- first-class
- dependable
- normal

It should not feel like a fallback for users who "failed" the voice experience.

## Voice As Presence, Not Requirement

Voice may support:

- presence
- acknowledgment
- pacing
- concise guidance
- short confirmation

Voice must not:

- gate the routine path
- delay the trust step
- become necessary for completion
- add extra trust meaning by itself

If voice is unavailable, unwanted, or muted, the routine path should still feel complete and polished.

## Acceptable Daily-Use Friction

Acceptable routine friction is limited to:

- noticing Jarvis presence
- understanding the trust prompt
- entering one routine factor
- receiving brief confirmation

Anything beyond that should be treated carefully as possible friction creep.

Routine friction should not include:

- re-explaining the system every login
- secondary trust steps by default
- speech requirements
- recovery-style warnings during normal use
- repeated dramatic buildup

## What Makes The Routine Path Too Slow

The routine path is too slow when:

- it delays access to create atmosphere
- it makes the user wait before the factor can be entered
- it extends the post-auth transition unnecessarily
- it feels noticeably heavier than normal daily device access should feel

## What Makes The Routine Path Too Theatrical

The routine path is too theatrical when:

- it emphasizes persona over access
- it adds cinematic beats that do not serve trust or usability
- it treats every normal login like a showcase moment
- it blurs the difference between greeting and authentication

## What Makes The Routine Path Too Annoying

The routine path is too annoying when:

- it repeats the same flourishes too often
- it inserts extra steps into daily use
- it asks the user to engage in conversation before access
- it behaves like a ceremony instead of a login

## What Makes The Routine Path Too Enterprise-Like

The routine path becomes too enterprise-like when it assumes:

- repeated challenge checkpoints
- multi-screen step progression by default
- compliance-style posture for ordinary personal access
- admin-style seriousness where consumer simplicity is more appropriate

Consumer-Windows routine access should feel confident, not bureaucratic.

## How Jarvis Stays Present Without Slowing Down Access

Jarvis stays present by owning:

- the visual frame
- the tone
- the transition language
- the immediate before and after feel of the trust step

Jarvis does not need to stay present by:

- adding time
- adding ritual
- adding extra trust gestures
- forcing voice participation

Presence should come from coherence, not delay.

## In-Bounds Routine UX Patterns

The following are in-bounds at planning level:

- concise greeting
- immediate trust prompt
- one routine factor
- brief confirmation
- fast transition into authenticated presence
- optional short voice framing that never blocks progress

## Out-Of-Bounds Routine UX Patterns

The following should be treated as out-of-bounds for the routine daily path:

- extended conversation before trust
- multiple default trust checkpoints
- forced spoken exchange
- theatrical pauses inserted only for atmosphere
- recovery-style seriousness during normal login
- enterprise-style challenge flow

## Explicit Deferrals For Later Revisions

`rev1e` intentionally defers:

- exact prompt wording
- exact animation timing
- exact sound or voice timing
- backend and storage design
- biometric design
- shell integration
- stronger-path implementation detail
- fallback implementation detail
- resident app or tray implementation detail

## Risks And Blockers

### UX Risks

- making the routine path slower than users will tolerate daily
- overusing cinematic framing until it feels repetitive
- treating presence as an excuse for delay

### Trust Risks

- letting the routine path become so light that it feels fake
- obscuring the actual trust action with too much persona
- weakening typed certainty by privileging voice theatrics

### Planning Risks

- drifting into implementation-level timing decisions too early
- mixing routine-path planning with stronger-path or recovery detail
- trying to solve resident presence and login pacing in the same revision

## What Success Looks Like

A successful routine-UX plan would make the user feel:

- the login was fast
- the trust step was real
- Jarvis stayed present
- typing remained natural and sufficient
- voice enhanced the mood without adding friction
- the whole flow felt premium without becoming tedious

## Recommended Next Planning Step After Rev1e

After this routine-UX slice, the next coherent planning revision should narrow one of:

- stronger-path justification and recovery trust-state detail
- resident trust-state surfacing after login
- setup and environment-preference flow for multi-monitor, device-routing, and post-install control

It should not try to solve all three in the same revision.
