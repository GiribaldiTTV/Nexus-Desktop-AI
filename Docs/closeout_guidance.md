# Closeout Guidance

## Purpose

This document defines how Nexus Desktop AI should use:

- closeouts
- rebaselines
- preserved historical closeout records

Use this file for policy.
Use `Docs/closeout_index.md` for lookup.
Use individual closeout or rebaseline docs for the historical or epoch summary itself.

## What Closeouts And Rebaselines Are For

A closeout or rebaseline should:

- summarize what is locked
- state what remains deferred
- reduce prompt bloat by replacing repeated historical recaps
- give later planning a stable shared baseline

They do not replace:

- the backlog registry
- canonical workstream records
- release tags
- GitHub release notes

## Current Nexus Posture

This guide is policy only.
It is not the owner of live current-baseline truth.

For the current Nexus-era baseline, always use:

- `Docs/closeout_index.md`

For the current epoch summary itself, route to the file referenced there.

## When To Use A Closeout

Use a closeout when:

- a milestone or lane materially resets future planning
- future work depends on knowing what is now locked
- a meaningful release or workstream justifies its own durable summary

## When To Use A Rebaseline

Use a rebaseline when:

- several smaller releases or lanes need one shared epoch summary
- the repo needs a fresh planning baseline without backfilling every small patch release
- current planning truth is fragmented across multiple closed lanes

## What Not To Do

- do not create retroactive closeouts for every missed small prerelease
- do not rewrite historical closeouts just to modernize wording
- do not use closeouts or rebaselines as substitutes for workstream records
- do not force release-dependent canon repair into `Release Readiness`; PR-owned canon must be complete before PR green, and escaped misses block the next active branch's `Branch Readiness`

## Post-Release Rule

Release-dependent facts can change only after a public release exists.

Examples:

- latest public prerelease
- release state
- closure state tied to a public release

When those facts change, the owning branch must carry the release-state canon before it reports PR-ready or release-ready.
Release Readiness is not a broad docs-sync phase.
If a required canon update escapes PR Readiness and the owning branch has already merged, the miss becomes a blocker in the next active branch's `Branch Readiness`; repair it there before implementation begins.
Do not open a governance-only branch or between-branch canon repair lane for routine closeout cleanup.
Do not repair directly on `main`; `main` is protected and read-only for Codex work.
There is no emergency direct-main repair path for Codex.
Any tracked file mutation while Codex is on `main` is a `Main Write Attempt`.

The public GitHub prerelease title format for Nexus `pre-Beta` releases is:

- `Pre-Beta v<major>.<minor>.<patch>`

Milestone names, user-facing scope, evidence roots, and implementation details belong in the release notes, not in the GitHub release title.
Post-release confirmation must treat that concise `Pre-Beta v<major>.<minor>.<patch>` title as the expected published title when it matches the tag and release notes carry the scoped summary.

## Current Policy

- preserve historical closeouts
- route historical lookup and current-baseline lookup through `Docs/closeout_index.md`
- use canonical workstream records for workstream-level detail
- use `Docs/validation_helper_registry.md` for helper naming, helper status, and consolidation truth when closeout or release notes mention validation helpers
- do not let this guidance doc become a live current-state owner
- create new closeouts or rebaselines only when they materially improve future planning clarity
- keep escaped post-release canon drift as a protected-main blocker that must be repaired on a legal branch surface, not as a planned governance-only branch or direct-main write
- prevent recurrence during PR Readiness by carrying the exact release-state closure plan for latest public prerelease, released/closed workstream state, release-debt clearing, and release title format before a release-bearing branch reports PR-ready
