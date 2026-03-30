# Jarvis Boot Access Design

## Purpose

This document is the canonical planning baseline for Jarvis boot-entry, login, trust, recovery, and resident post-login trust-state behavior on a consumer Windows machine.

It consolidates the stable planning decisions previously split across smaller boot-planning slice documents.

This is still a planning artifact.
It does not define implementation details for backend logic, auth storage, biometrics, tray mechanics, shell integration, renderer wiring, diagnostics presentation, or boot runtime control.

## Consolidation Status

This document supersedes and replaces the earlier slice-by-slice boot planning stack as the primary boot-planning source.

The earlier boot slice docs have been retired from the active docs tree.
This document is now the current canonical source for boot access design.

## Relationship To Core Source-Of-Truth Docs

This document is downstream of:

- `architecture.md` for boot/desktop authority boundaries
- `jarvis_vision.md` for long-term product identity
- `feature_backlog.md` for workstream status and scope control
- `orchestration.md` for launcher-owned desktop-phase control limits

This document does not replace those files.
It narrows only the product and planning shape of the future Jarvis boot-access experience.

## Current Startup Reality

The current stabilized startup path is:

`launch_jarvis_desktop.vbs`
-> `jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py`

This is the current controlled desktop-launch path, not the final Jarvis-first experience.

The path-sensitive surfaces that matter most at planning level are:

- `main.py`
- `launch_jarvis_desktop.vbs`
- `desktop/jarvis_desktop_launcher.pyw`
- `jarvis_desktop_main.py`

## Future Boot-Layer Shape

The smallest future boot layer sits above the current launcher stack.

Its conceptual job is to coordinate:

- boot-entry presentation
- pre-desktop trust flow
- delegation into launcher-owned desktop execution
- later observation of downstream launcher outputs after emission

It is not allowed to replace launcher-owned desktop authority.

Desktop-stage ownership begins when boot-stage coordination delegates execution to the launcher.
From that point forward, launcher-owned desktop truth, classification, control, retry, recovery routing, and finalized end-state determination remain launcher-owned and read-only to higher layers.

## Product Intent

Jarvis should feel like the primary visible system presence on a consumer Windows machine.

The intended user impression is:

- the machine feels like it is entering Jarvis, not launching a normal app
- Windows remains the host platform, but not the dominant visible identity during entry
- Jarvis remains coherent before login, during trust confirmation, and after desktop entry
- access feels cinematic, intelligent, and low-friction rather than theatrical or bureaucratic

## Governing Framing

The core framing for this boot-access design is:

- Jarvis owns presentation
- real authentication owns trust
- the user should experience both as one continuous Jarvis-controlled flow

This means:

- the trust action must be explicit and meaningful
- the trust action must remain inside Jarvis presentation
- conversation and presence may frame access, but must not replace real trust
- typed and voice interaction belong to one shared access flow, not two separate products

## Core Design Principles

- cinematic but fast
- immersive but dependable
- voice is presence, typing is certainty
- one shared auth flow, not two systems
- real authentication without breaking the Jarvis atmosphere
- Windows-safe fallback must always exist
- recovery should feel guided and supportive, not punitive
- Jarvis must never trap the user outside Windows
- consumer Windows first, not enterprise

## Consumer Windows Assumptions

This design is for ordinary personal Windows use, not domain-managed or business deployment.

It must remain workable for:

- users who prefer typing
- users who prefer voice
- noisy or private environments
- inconsistent consumer hardware
- users who may forget Jarvis credentials
- users who may need fallback access to Windows
- users who expect speed and clarity during daily use

## Entry And Handoff Model

At planning level, the future boot-access sequence is:

1. Jarvis boot presence appears above the current launcher stack
2. Jarvis frames identity and access inside its own presentation
3. the user completes a real trust step
4. Jarvis delegates into launcher-owned desktop execution
5. Jarvis later continues as a resident post-login presence

The minimal pre-delegation boot layer is for:

- pre-desktop presence
- trust and recovery framing
- Windows handoff coordination
- delegation into desktop-stage launcher execution

It is not for:

- desktop-stage retry or escalation control
- desktop-stage diagnostics authority
- launcher-policy replacement

## Experience Layer Versus Trust Layer

Jarvis boot access must clearly separate:

- experience-layer interaction
- trust-layer authentication

### Experience Layer

The experience layer includes:

- visual presence
- greeting
- conversational framing
- optional voice timing
- transitions
- identity continuity

### Trust Layer

The trust layer includes:

- the explicit access decision
- the deliberate trust action that grants access
- the distinction between normal access and degraded or recovery-oriented trust states

The experience layer may frame the trust layer.
It must not replace it.

## Dual-Modality Contract

Jarvis access must support typed and voice interaction inside one shared flow.

### Typed Input

Typed input is the certainty path.
It must always remain sufficient for:

- the routine trust step
- the stronger trust step
- fallback selection
- recovery entry
- recovery completion
- resident post-login trust and recovery access

### Voice Input

Voice may support:

- presence
- greeting
- explanatory framing
- optional guidance
- emotional tone

Voice must never be required for:

- trust completion
- fallback use
- recovery completion
- resident trust-state access

### Shared Flow Rule

Typed and voice interaction must feed the same conceptual flow:

- same identity state
- same trust state
- same recovery posture
- same session transition

The user should never feel like there is a separate typed-login product and voice-login product.

## Real Authentication Contract

Jarvis access must include a real, explicit trust action.

That trust action must be:

- deliberate
- understandable
- meaningful
- low-friction for daily use
- visually integrated into Jarvis presentation

The trust step should feel like:

- Jarvis is granting access after a real check

It should not feel like:

- a vague conversational performance
- fake recognition theater
- a generic detached Windows interruption

## Primary Trust Family

At planning level, the safest first trust family is:

- explicit local knowledge-based secret entry

This planning baseline does not choose exact storage or backend mechanics.
It only defines the acceptable trust family shape.

## Auth-Factor Shape

At planning level, the trust family narrows into two conceptual factor shapes:

- a short-form deliberate secret entry for routine daily access
- a longer-form deliberate secret entry for stronger or recovery-oriented trust states

This keeps the normal daily path fast while preserving a distinct elevated path when trust continuity is different from routine access.

## Routine Daily Path

The routine path is the default consumer-Windows access path.

It should conceptually fit into three short beats:

1. concise Jarvis presence
2. explicit routine trust action
3. immediate confirmation and transition

The routine path should feel:

- quick
- calm
- intentional
- low-friction

It should avoid:

- extended conversation before trust
- repeated trust checkpoints
- recovery-style seriousness during normal login
- decorative ceremony that slows routine access

Acceptable routine friction is limited to:

- recognizing the prompt
- entering one routine factor
- receiving immediate confirmation and transition

If normal daily use starts to feel like a ritual, the routine path has become too heavy.

## Stronger Path

The stronger path is not for routine daily use.

Its conceptual purpose is:

- trust restoration
- recovery-oriented confirmation
- elevated confidence when normal trust continuity is meaningfully different from ordinary daily entry

The stronger path is justified when trust continuity is degraded, such as:

- post-bypass return into Jarvis trust restoration
- recovery-oriented access states
- other non-routine trust states where the system should not pretend everything is ordinary

The stronger path should feel:

- more deliberate than routine access
- clearly non-routine
- recovery-aware
- still finite
- still Jarvis-framed

It should not feel:

- punitive
- hostile
- corporate
- like the new default login path

## Fallback And Safety Contract

Jarvis must never become the only rescue path to Windows access.

A Windows-safe fallback path must always exist if:

- Jarvis credentials are forgotten
- Jarvis trust completion is unavailable
- Jarvis access continuity is degraded
- the Jarvis layer is temporarily unable to complete normal access

Jarvis is the preferred front door.
It must not be the only emergency exit.

## Post-Bypass Recovery Contract

If the user reaches Windows through fallback instead of normal Jarvis trust completion, Jarvis should later detect that trust continuity was bypassed at a conceptual level.

After desktop entry, Jarvis should surface a guided recovery path that:

- explains that normal Jarvis trust continuity needs restoration
- provides a clear recovery entry path
- allows bounded postponement without silently leaving the trust state broken forever

The recovery posture must feel:

- supportive
- restorative
- non-accusatory

## Resident Presence After Login

After desktop entry, Jarvis should continue to exist as a visible resident presence inside Windows.

At planning level, that resident layer is:

- the post-login trust and recovery anchor
- the place where trust continuity remains understandable
- the home for recovery entry after login
- the stable presence that carries Jarvis beyond the boot moment

This resident layer is conceptually where future tray and control-center responsibilities belong, but implementation details remain deferred.

## Resident Trust States

At planning level, the resident Jarvis layer should recognize three post-login trust states:

- normal trust state
- degraded trust state
- recovery-needed state

### Normal Trust State

Normal trust state means:

- access continuity is healthy
- no immediate recovery action is needed
- Jarvis can remain calm and available in the background

Normal state should reassure without demanding attention.

### Degraded Trust State

Degraded trust state means:

- trust continuity is no longer fully normal
- desktop use may continue
- recovery entry should be visible and easy to reach

Degraded state should inform without becoming alarmist.

### Recovery-Needed State

Recovery-needed state means:

- trust restoration now needs to be surfaced clearly
- recovery entry must be obvious
- the user should not have to hunt through deep settings

Recovery-needed state should guide without punishing.

## Recovery Entry After Login

Recovery entry must remain reachable after desktop entry through the resident Jarvis presence.

At planning level, this means:

- recovery entry must not be boot-only
- recovery entry must not be voice-only
- recovery entry must remain discoverable later
- the user should be able to revisit recovery without re-entering a boot flow

The resident layer should support both:

- proactive surfacing when trust continuity is degraded
- user-initiated recovery entry later

## Resident Recovery-Entry Trigger And Surfacing Contract

At planning level, resident recovery entry should follow the post-login resident trust states:

- in normal trust state, no proactive recovery surfacing is needed
- in degraded trust state, recovery entry should be visible, easy to reach, and calmly re-discoverable
- in recovery-needed state, recovery entry should surface proactively and clearly enough that the user understands restoration is pending

Resident recovery entry is for restoring Jarvis trust continuity after desktop entry.
It is not a license for:

- launcher-owned runtime classification
- diagnostics escalation or diagnostics authority
- boot-time control after desktop handoff
- backend trust implementation details

## Bounded Deferral And Re-Surface Contract

At planning level, bounded deferral means:

- the user may choose to postpone recovery for now
- postponement must not silently normalize a degraded or recovery-needed state forever
- the system should later re-surface recovery entry until trust continuity is restored
- re-surfacing should remain calmer in degraded state than in recovery-needed state

The user-posture contract is:

- normal desktop use may continue after a bounded deferral
- the user must not feel trapped or locked out of Windows because recovery was postponed
- the user must not be forced through repeated recovery prompts during the same immediate interaction once a clear postpone choice has been made
- later re-surfacing should remind rather than punish

This document intentionally does not define:

- exact timers, cadences, counters, or re-surface schedules
- exact tray, control-center, resident UI, shell, or notification mechanics
- exact post-bypass detection logic
- exact persistence storage or backend state handling

## Resident Trust-State Transition Contract

At planning level, the resident trust-state transitions are:

- normal -> degraded when trust continuity is no longer fully normal but immediate strong recovery surfacing is not yet required
- degraded -> recovery-needed when recovery should be made proactively obvious rather than merely easy to reach
- degraded or recovery-needed -> normal only after trust restoration is completed through the future resident recovery path

These are conceptual planning states for the future resident boot-access layer.
They do not authorize runtime control over launcher-owned desktop behavior or reinterpretation of launcher-owned desktop truth.

## Resident Control-Anchor Responsibility Contract

At planning level, the future resident control-center or settings anchor is the stable post-login place where the user can:

- understand current Jarvis trust posture without re-entering a boot flow
- see whether the current resident trust state is normal, degraded, or recovery-needed
- reach recovery entry later through a user-initiated path
- understand why recovery is being surfaced when trust continuity is no longer fully normal
- revisit Jarvis trust-continuity posture after login through one stable anchor rather than scattered one-off prompts

This resident control anchor is conceptually responsible for:

- calm post-login trust-state visibility
- user-initiated recovery entry after login
- concise explanation of current trust continuity posture
- being the stable post-login home for recovery posture once the boot flow has already handed off to the desktop phase

This resident control anchor should relate to the resident trust states as follows:

- in normal trust state, it may remain quiet and low-demand while still existing as the stable post-login anchor
- in degraded trust state, it should make recovery discoverable, legible, and easy to revisit
- in recovery-needed state, it should make restoration obvious enough that the user does not have to hunt for the next safe step
- after a bounded deferral, it remains the stable place where recovery can later be resumed without forcing the user back through a boot-only flow

This planning contract does not make the resident control anchor responsible for:

- pre-desktop presence or boot-time trust completion
- launcher-owned desktop truth, classification, control, retry, recovery routing, or finalized end-state determination
- diagnostics authority, diagnostics policy, or incident handling
- auth backend, credential storage, biometrics, device-trust, or shell mechanics
- exact tray, control-center, resident UI, or notification implementation mechanics
- broad consumer setup or environment-preference ownership

Consumer setup and environment-preference planning remains a separate future lane.
This resident control-anchor contract is only about post-login trust continuity, trust-state visibility, and user-initiated recovery access.

## Consumer Setup Purpose And Entry Contract

At planning level, consumer setup is the short post-install or first-run onboarding lane that helps Jarvis establish an initial fit for this person and this machine without turning setup into trust, recovery, or system configuration.

Consumer setup is conceptually responsible for:

- introducing Jarvis as the intended system-facing experience rather than a generic Windows app wizard
- establishing a usable first everyday posture after install
- collecting only the smallest set of early user-facing choices needed to avoid an obviously wrong first-run experience
- reassuring the user that typed interaction remains sufficient and that early setup choices are not irreversible commitments
- handing the user into ordinary Jarvis use without keeping them inside a prolonged onboarding ritual

Consumer setup should begin only after install and first run have reached the point where Jarvis can present itself coherently as an experience layer.
It should not be treated as:

- the trust step itself
- a stronger trust or recovery path
- a replacement for resident trust-state visibility
- an excuse to introduce shell, tray, backend, renderer, or diagnostics mechanics

Consumer setup should stay short, legible, and consumer-friendly.
Its purpose is to establish initial fit and comfort, not to front-load every future choice.

## Consumer Setup Completion And Handoff Contract

At planning level, consumer setup should count as complete once:

- Jarvis has established a coherent initial posture for ordinary use
- the user has made only the minimum early choices needed for that posture
- the user understands that later preference adjustment remains possible
- the system can hand off into normal Jarvis use without continuing to behave like an installer or onboarding wizard

Consumer setup completion should not require:

- exhaustive settings selection
- environment-preference finalization across every later context
- auth enrollment, trust restoration, or recovery completion
- decisions about backend, shell, tray, renderer, diagnostics, or runtime behavior

The handoff after setup should feel like:

- Jarvis is now ready for everyday use
- the user is no longer inside a special onboarding state
- future adjustment can happen later without replaying the entire setup lane

## Consumer Setup Relationship To Trust And Recovery Lanes

Consumer setup is separate from the already-defined resident trust and recovery lanes.

That means:

- consumer setup may shape presentation posture, comfort, and early user guidance
- consumer setup must not determine whether trust continuity is normal, degraded, or recovery-needed
- consumer setup must not own recovery-entry surfacing, bounded deferral, or resident trust-state transitions
- consumer setup must not become a hidden access gate or a disguised stronger trust path

The resident control anchor remains the post-login home for:

- trust-state visibility
- recovery-entry access
- explanation of current trust continuity posture

Consumer setup remains responsible only for:

- initial onboarding fit after install or first run
- early consumer-facing calibration
- handing the user into normal use with reversible early choices

Later-adjustment and safe-undo remains a distinct adjacent lane.
This document intentionally does not define the exact setup sequence, exact preference labels, or exact later settings ownership mechanics.

## Environment-Preference Taxonomy Contract

At planning level, environment preferences are the user-facing posture choices that shape how Jarvis feels during setup and ordinary use without changing trust meaning, recovery meaning, or runtime authority.

The environment-preference categories that belong in this lane are:

- presence posture:
  how calm, expressive, quiet, or pronounced Jarvis should feel as an experience layer
- guidance posture:
  how concise or guided Jarvis should be while helping the user understand the early experience
- interaction posture:
  how voice participates as optional framing or guidance while typed interaction remains fully sufficient
- pacing and atmosphere posture:
  how brief versus atmospheric the early Jarvis experience should feel without turning setup into ceremony
- everyday resident presence posture:
  how visible or quiet Jarvis should feel after setup when trust continuity is normal and no recovery-oriented surfacing is active

These categories are about comfort, presentation, and usability posture.
They are not:

- trust categories
- recovery-state categories
- backend categories
- shell or tray categories
- diagnostics categories
- runtime-policy categories

## Environment-Preference Timing Model

At planning level, the most plausible up-front setup choices are the broad posture decisions that help Jarvis avoid an obviously wrong first-run experience:

- an initial presence-posture baseline
- an initial guidance-posture baseline
- an initial interaction-posture baseline that keeps typing sufficient and voice optional

At planning level, the most plausible optional setup choices are refinements that may improve comfort but are not required to establish a coherent first everyday posture:

- deeper pacing or atmosphere refinements
- non-essential resident presence refinements for normal trust state
- secondary comfort refinements that are helpful but not required for setup completion

At planning level, the choices that should remain deferred until later are those the user can evaluate better only after living with Jarvis for some time:

- detailed per-surface preference tuning
- exact later everyday adjustments
- anything that would require the user to understand future shell, tray, renderer, or diagnostics behavior
- anything that meaningfully overlaps with trust, recovery, or resident control-anchor ownership

This timing model is meant to keep setup short and consumer-friendly.
It prevents setup from becoming either:

- a full settings migration exercise
- a disguised access-control sequence

## Environment-Preference Boundary Contract

Environment preferences may shape:

- comfort
- presentation tone
- guidance density
- presence intensity
- normal-state everyday visibility posture

Environment preferences must not shape:

- whether trust continuity is normal, degraded, or recovery-needed
- whether recovery-entry surfacing is required
- how bounded deferral works
- how the resident control anchor owns trust-state visibility or recovery access
- launcher-owned desktop truth, diagnostics authority, or any runtime behavior

Later-adjustment and safe-undo remains a separate adjacent lane.
This document does not define how preference changes are revisited later; it defines only which categories belong here and when they are plausibly chosen.

## Later-Adjustment And Safe-Undo Purpose Contract

At planning level, later adjustment and safe-undo is the ordinary post-setup lane where the user can revisit, soften, or reverse prior consumer-facing setup and environment-preference choices without implying that trust is broken or recovery is required.

This lane is conceptually responsible for:

- allowing the user to make Jarvis calmer, simpler, quieter, or less demanding after living with the initial setup choices
- reinforcing that setup and environment-preference choices are revisable rather than one-time commitments
- helping the user recover from overly strong, overly guided, or otherwise poor comfort choices without replaying the meaning of trust failure
- preserving confidence that the Jarvis experience can be adjusted without destabilizing ordinary use

This lane should feel:

- normal
- user-directed
- non-urgent
- non-punitive
- like ordinary preference revision rather than a system repair event

## Ordinary Adjustment Versus Trust Recovery Contract

At planning level, ordinary preference adjustment is different in meaning from trust recovery.

Ordinary preference adjustment is about:

- comfort
- presentation posture
- guidance density
- presence intensity
- how strong or quiet the everyday Jarvis experience should feel

Trust recovery is about:

- degraded or recovery-needed trust continuity
- restoring the intended trust path after bypass or disruption
- the resident trust-state and recovery-entry contracts already defined elsewhere in this document

That means:

- wanting Jarvis to feel calmer or simpler must not be treated as recovery-needed state
- revising a setup choice must not change trust-state meaning by itself
- undoing a consumer-facing preference must not require trust restoration
- trust recovery must remain separate from normal post-setup preference revision

## Later-Adjustment Relationship To The Resident Control Anchor

The resident control anchor remains the post-login home for:

- trust-state visibility
- recovery-entry access
- explanation of current trust continuity posture

Later adjustment and safe-undo may still be reachable after login, but it is not conceptually the same lane as the resident control anchor.

At planning level, that means:

- later adjustment may coexist with post-login Jarvis presence without being reclassified as trust-state ownership
- later adjustment must not take over recovery-entry surfacing or bounded-deferral meaning
- the resident control anchor must not become the owner of broad consumer setup or environment-preference revision just because both are post-login reachable

This document intentionally does not define:

- exact settings-surface ownership
- exact cross-links between trust-state access and later adjustment
- exact tray, shell, resident UI, or notification mechanics for how later adjustment is reached
- exact later-adjustment screen flow or safe-undo sequence

## How Jarvis Stays Present Without Becoming Heavy

Jarvis should remain present through:

- the visual frame around the trust step
- the immediate before and after of access confirmation
- the continuity of post-login resident presence
- supportive recovery framing when needed

Jarvis should not stay present by:

- adding extra trust gestures
- delaying routine access
- turning voice into a hidden requirement
- extending the emotional posture of boot-time login through the entire desktop session

## In-Bounds Patterns

The following are in-bounds for the canonical boot-access design:

- a Jarvis-framed pre-desktop layer above the current launcher stack
- one shared typed-and-voice access flow
- typed completion for all critical trust and recovery actions
- voice as optional presence and guidance only
- a short routine trust path for normal daily use
- a distinct stronger path for degraded or recovery-oriented trust states
- Windows-safe fallback
- guided post-bypass recovery
- resident post-login trust-state surfacing
- a future resident control anchor distinct from the boot flow

## Out-Of-Bounds Patterns

The following are out-of-bounds for the current canonical design:

- conversation or voice alone as primary trust
- mandatory voice for access or recovery
- hidden or passive primary trust decisions
- enterprise-style challenge choreography for routine consumer access
- punitive recovery posture
- turning the stronger path into the default path
- turning resident trust-state surfacing into constant warning posture
- using the boot layer to override launcher-owned desktop truth or control
- implementation drift into backend, shell, tray, or diagnostics mechanics inside this design baseline

## Explicit Deferrals

This canonical document intentionally defers:

- auth backend design
- credential storage design
- biometric design
- device-trust design
- tray implementation details
- resident UI mechanics
- shell integration
- renderer wiring
- diagnostics presentation behavior
- notification-system implementation
- exact post-bypass detection logic
- exact resident recovery-entry persistence mechanics
- exact resident control-anchor information architecture or settings taxonomy
- exact consumer setup sequence, prompt set, or screen flow
- exact environment-preference labels, defaults, or per-surface mappings
- exact later-adjustment or safe-undo mechanics for setup choices
- boot runtime control
- launcher-policy changes

## Main Risks

### Experience Risks

- making routine access slower than users tolerate
- confusing atmosphere with delay
- letting the boot flow feel theatrical instead of usable

### Trust Risks

- making the trust step visually explicit but conceptually weak
- allowing conversation to substitute for real trust
- blurring routine and stronger trust states together

### Recovery Risks

- making fallback available but socially discouraged
- making recovery too easy to ignore forever
- making recovery feel like punishment

### Planning Risks

- mixing canonical design work with implementation details
- re-opening launcher-owned desktop behavior inside boot planning
- keeping too many slice docs active after consolidation

## What Success Looks Like

A successful consolidated boot-access design would make the user feel:

- the machine entered Jarvis, not a generic app
- the trust step was real
- typing was always enough
- voice made Jarvis feel alive without becoming required
- normal daily access stayed fast
- stronger trust only appeared when it felt justified
- fallback existed if something went wrong
- recovery after login felt guided and supportive
- Jarvis remained present after entry as a trustworthy anchor

## Recommended Next Planning Splits

If boot planning continues after this clarification, any later revisions should stay narrower than the already-defined planning contracts and focus only on:

- exact settings ownership or information-architecture clarification if a later planning boundary still needs it
- exact preference labels, defaults, or per-surface mappings if a later planning boundary intentionally allows that depth

Those should remain separate from backend, shell, diagnostics, or implementation design until the planning boundary is intentionally changed.
