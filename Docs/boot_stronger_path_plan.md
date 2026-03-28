# Jarvis Boot Stronger Trust Path Plan

## Purpose

This document defines the next planning slice for `FB-004`.

`rev1f` is planning-only.
It does not choose backend design, credential storage, biometric stacks, shell integration, or recovery implementation wiring.

Its job is to define:

- what the stronger Jarvis trust path is conceptually for
- when the stronger path is justified instead of the routine path
- what recovery-oriented trust states conceptually relate to the stronger path
- how the stronger path should remain distinct from the routine daily path
- what remains intentionally deferred until later auth and implementation planning

## Relationship To Prior Boot Planning

This document is downstream of:

- `FB-015 rev1a` phase-boundary clarification
- `FB-004 rev1a` boot entry-chain and handoff-topology planning
- `FB-004 rev1b` boot login, fallback, recovery, and resident-presence planning
- `FB-004 rev1c` trust-model planning
- `FB-004 rev1d` auth-factor planning
- `FB-004 rev1e` routine auth UX planning

Those prior slices established that:

- Jarvis owns presentation
- real authentication owns trust
- the routine path is the default daily path
- the stronger path is not for routine use
- typed input must remain sufficient
- voice may support presence but never replace trust

This slice narrows only the stronger-path concept and its justification boundary.

## Product-Level Stronger Path Objective

The stronger path exists to handle trust states that are meaningfully different from normal daily access.

It should feel:

- real
- deliberate
- justified
- more serious than routine login
- still recognizably Jarvis
- not hostile or bureaucratic

The user should feel:

- "Jarvis is asking for a stronger confirmation because the trust state is different."

The user should not feel:

- "Jarvis suddenly turned into enterprise security."
- "I am being punished."
- "The system invented extra friction for no reason."

## Conceptual Purpose Of The Stronger Path

The stronger path is conceptually for:

- access states that are not normal daily access
- trust restoration
- recovery-oriented confirmation
- elevated confidence before re-establishing normal Jarvis trust

It is not conceptually for:

- every login
- cosmetic drama
- replacing the routine path
- making Jarvis feel more serious for its own sake

## When The Stronger Path Is Justified

At planning level, the stronger path is justified when the trust state is meaningfully different from routine daily entry.

Conceptually justified states include:

- post-bypass return into Jarvis trust restoration
- recovery-oriented access states
- access after a clearly degraded Jarvis trust state
- access states that should not be treated as routine because normal trust continuity was interrupted

These states are unified by one idea:

- the system no longer treats the current access attempt as ordinary routine continuity

## What Should Not Justify The Stronger Path

The stronger path should not be justified by:

- normal daily login
- a desire for more dramatic presentation
- ordinary user familiarity checks
- optional voice non-use
- the system wanting to look more secure than it is

If the trust state still feels like normal daily continuity, the routine path should remain in control.

## Recovery-Oriented Trust States

At planning level, recovery-oriented trust states include situations where:

- the user is restoring normal Jarvis access
- prior normal trust continuity was bypassed, interrupted, or degraded
- the system should re-establish trust before returning the user to the normal routine path

This slice does not define exact detection logic.
It defines only that recovery states are one of the main conceptual homes for the stronger path.

## Relationship To Post-Bypass Recovery

Post-bypass recovery is one of the clearest conceptual justifications for the stronger path.

If the user entered Windows through a fallback route, later Jarvis recovery should not pretend that nothing happened.
It should also not become punitive.

The stronger path should serve as:

- a deliberate trust-restoration step

not:

- a punishment flow
- a shame flow
- a generic admin procedure

## How The Stronger Path Should Differ From The Routine Path

The stronger path should differ from the routine path in these ways:

- more deliberate
- more clearly marked as non-routine
- more explicitly tied to trust restoration or elevated confidence
- allowed slightly more friction than the daily path

It should not differ in these ways:

- it should not abandon Jarvis presentation
- it should not become enterprise-style challenge flow
- it should not require voice
- it should not add unrelated security theater

## Acceptable Extra Friction

Some extra friction is acceptable in the stronger path because it is not the normal daily path.

Acceptable extra friction means:

- a more deliberate pace
- a more serious framing tone
- a stronger confirmation feel than the routine path
- a more obviously elevated trust posture

That extra friction must still remain:

- understandable
- finite
- justified by trust state
- appropriate for consumer Windows use

## Too Much Friction

The stronger path becomes too harsh when it:

- feels punitive
- becomes bureaucratic
- multiplies trust steps unnecessarily
- turns recovery into a burden
- uses friction to perform seriousness rather than restore trust

The user should understand:

- why this path is different
- why it is appearing now
- that it is still meant to help them restore normal access

## Typed And Voice Relationship During The Stronger Path

Typed input remains the certainty path during the stronger path.

The following must always remain completable by typing alone:

- stronger trust entry
- stronger-path continuation
- recovery-oriented trust restoration actions that depend on the stronger path

Voice may support:

- framing
- explanation
- reassurance
- concise guidance

Voice must not:

- replace the stronger trust step
- become required for completion
- add hidden trust meaning of its own

## How The Stronger Path Stays Inside Jarvis Presentation

The stronger path should remain inside Jarvis presentation just like the routine path, but with a more deliberate tone.

That means:

- Jarvis remains the visible frame
- the stronger step still feels like part of the Jarvis flow
- the user is not dumped into a detached generic security interruption
- the presentation communicates that this is non-routine without becoming theatrical security theater

The correct balance is:

- elevated trust posture
- same Jarvis-owned presentation continuity

## What Makes The Stronger Path Too Vague

The stronger path is too vague when:

- the user cannot tell why it appeared
- the path feels only cosmetically different from routine login
- it implies elevated trust without clearly being an elevated trust state

## What Makes The Stronger Path Too Harsh

The stronger path is too harsh when:

- it feels accusatory
- it treats recovery as wrongdoing
- it makes the user feel punished for using fallback
- it creates enterprise-style burden on a personal machine

## What Makes The Stronger Path Too Enterprise-Like

The stronger path becomes too enterprise-like when it assumes:

- default challenge escalation patterns
- multi-screen policy choreography
- compliance-style seriousness as a default interaction tone
- admin-oriented recovery expectations

Consumer-Windows recovery should feel protective and clear, not corporate.

## In-Bounds Stronger-Path Patterns

The following are in-bounds at planning level:

- stronger trust used only for non-routine trust states
- recovery-oriented trust restoration
- a more deliberate but still finite trust step
- clear distinction from the routine daily path
- Jarvis-framed elevated confirmation without punitive tone

## Out-Of-Bounds Stronger-Path Patterns

The following should be treated as out-of-bounds for this slice:

- using the stronger path as the new default login path
- using the stronger path for cosmetic drama
- making fallback automatically feel like guilt
- forcing voice participation
- adding unrelated challenge steps only to look more secure
- enterprise-style escalation by default

## Explicit Deferrals For Later Revisions

`rev1f` intentionally defers:

- exact trigger logic
- exact recovery-branch sequencing
- exact prompt wording
- backend and storage design
- biometric or device-trust design
- shell integration
- concrete recovery mechanics
- resident app or tray implementation details

## Risks And Blockers

### Trust Risks

- making the stronger path so soft that it feels no different from routine access
- making it so vague that users cannot understand why it exists
- letting it become symbolic rather than meaningful

### Friction Risks

- making the stronger path feel punitive
- carrying too much extra friction into consumer recovery states
- letting elevated tone turn into enterprise-style burden

### Planning Risks

- solving triggers and implementation details too early
- mixing stronger-path planning with resident-app surfacing in the same slice
- collapsing recovery-state logic and factor implementation into one pass

## What Success Looks Like

A successful stronger-path plan would make the user feel:

- this path only appears when the trust state is genuinely different
- it feels more serious than daily login without becoming hostile
- I understand why it is happening
- I can still complete it reliably by typing
- Jarvis stayed present
- the system is restoring trust, not punishing me

## Recommended Next Planning Step After Rev1f

After this stronger-path slice, the next coherent planning revision should narrow one of:

- resident trust-state surfacing after login
- setup and environment-preference flow for installation, monitor/layout, and device-routing control
- diagnostics presentation refinement if you explicitly decide to branch into non-boot UX polish

It should not try to solve all three in the same revision.
