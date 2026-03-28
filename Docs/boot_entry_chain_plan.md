# Jarvis Boot Entry-Chain Plan

## Purpose

This document defines the first planning pass for `FB-004`.

`rev1a` is planning-only.
It does not introduce boot runtime behavior, change launcher policy, or choose implementation wiring.

Its job is to:

- define the smallest future boot-layer shape above the current launcher stack
- map the current and future entry chain at a practical planning level
- define the pre-delegation phases a future boot layer owns
- define the conceptual handoff into launcher-owned desktop execution
- identify which downstream launcher outputs are safe for later boot observation
- record what remains intentionally deferred for later boot revisions

## Current Entry Chain

Current stabilized desktop-stage startup path:

`launch_jarvis_desktop.vbs`
-> `desktop/jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py`

This current path is the stabilized desktop orchestration chain, not the future boot orchestrator.

Also present at repo root:

- `main.py`

`main.py` is a top-level Jarvis experience surface, but it is not the current desktop launcher chain.
For `FB-004 rev1a`, it should be treated as a path-sensitive top-level surface that future boot work may coordinate with later, not as an already approved boot orchestrator.

## Smallest Future Boot-Layer Shape

The smallest coherent future boot-layer shape is:

`Windows boot/login handoff`
-> `future boot orchestrator`
-> delegation into `desktop/jarvis_desktop_launcher.pyw`
-> `jarvis_desktop_main.py`

At this planning stage, the future boot orchestrator is defined only as:

- a top-level coordinating layer above the desktop launcher
- a pre-desktop phase owner
- a handoff owner into launcher-controlled desktop execution
- a downstream observer of launcher-emitted desktop outcomes after handoff

It is not yet defined as:

- a replacement for the launcher
- a renderer owner inside desktop-phase execution
- a policy authority over launcher retry, escalation, classification, or finalized truth

## Relative Position Of Current Path-Sensitive Surfaces

`main.py`

- remains a root-owned top-level experience surface
- may later become part of the boot-entry story, but `rev1a` does not decide whether it is reused, wrapped, replaced, or kept separate

`launch_jarvis_desktop.vbs`

- remains the current Windows-facing launch shim
- is below any future OS-level handoff, but above the current desktop launcher target
- remains path-sensitive and implementation-deferred

`desktop/jarvis_desktop_launcher.pyw`

- remains the desktop-phase execution owner after delegation
- is the boundary target a future boot layer delegates into
- must not be absorbed into boot-layer control by `rev1a`

`jarvis_desktop_main.py`

- remains the desktop renderer entrypoint launched by the launcher
- stays fully inside launcher-owned desktop-phase execution
- is not a boot-layer planning surface in `rev1a`

## Minimal Pre-Delegation Phase Sequence

The smallest useful future boot-phase sequence before delegation is:

1. host handoff into Jarvis boot entry
2. boot-layer presence becomes active
3. boot layer selects delegation target
4. boot layer delegates desktop startup execution into the launcher
5. launcher-owned desktop-phase authority begins

`rev1a` does not define behavior inside those phases.
It defines only the minimal topology and ownership sequence needed for later revisions.

## Delegation Handoff Model

The delegation handoff is the conceptual point where:

- boot-stage coordination stops owning execution
- the launcher begins owning desktop startup execution
- desktop-phase truth, classification, control, recovery, and finalized outcomes become launcher-owned

After handoff:

- the boot layer may observe
- the boot layer may narrate or coordinate around transition in later revisions
- the boot layer may not rewrite launcher truth
- the boot layer may not inject control back into launcher-owned desktop execution

## Safe Downstream Observation Surface

After delegation, a future boot layer may observe only launcher-emitted downstream outputs such as:

- readiness signals
- failure and recovery signals
- finalized end-state signals
- runtime logs
- crash artifacts
- diagnostics status artifacts
- bounded historical or advisory outputs only as descriptive downstream context

These are safe only under the existing `FB-015` rules:

- after launcher emission
- read-only
- non-authoritative
- non-binding where historical or advisory material is involved

## Explicit Deferrals For Later Boot Revisions

`FB-004 rev1a` intentionally defers:

- deciding whether `main.py` becomes the eventual boot entrypoint
- replacing or rewriting `launch_jarvis_desktop.vbs`
- shell or login integration details
- boot presentation behavior
- startup voice timing
- immersive visual handoff design
- cross-phase health policy behavior
- any launcher-policy change
- any renderer, diagnostics, or voice change
- any implementation scaffolding

## Path-Sensitive Planning Notes

These surfaces require controlled later treatment and should not be changed in `rev1a`:

- `main.py`
- `launch_jarvis_desktop.vbs`
- `desktop/jarvis_desktop_launcher.pyw`
- `jarvis_desktop_main.py`

This planning pass depends on the current workspace-layout rule that path-sensitive entry surfaces must be migrated deliberately rather than rewritten casually.

## Rev1a Non-Goals

`rev1a` does not:

- choose a concrete boot implementation language or file
- assign startup behavior inside the boot phases
- define retry or escalation behavior above the launcher
- define shell ownership or Windows integration details
- define renderer, diagnostics, or voice behavior
- modify the current startup chain

## Risks And Blockers

- treating the future boot layer as a replacement for the launcher would violate the `FB-015` phase boundary
- deciding too early that `main.py` is the boot orchestrator would skip a needed design step
- mixing topology planning with startup presentation, shell integration, or voice behavior would cause scope sprawl
- changing path-sensitive entry surfaces before later approved planning would create avoidable churn

## Recommended Next Planning Step After Rev1a

If `FB-004` continues after this pass, the next coherent planning slice should define:

- the minimum boot-entry ownership model
- which single root-facing entry surface should host or invoke the future boot coordinator
- what remains delegated to the existing Windows-facing shim during an eventual first implementation pass

That next slice should still remain planning-only.
