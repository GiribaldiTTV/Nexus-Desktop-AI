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
- do not force release-dependent canon repair onto a future implementation branch when the truthful next move is a docs-only canon pass

## Post-Release Rule

Release-dependent facts can change only after a public release exists.

Examples:

- latest public prerelease
- release state
- closure state tied to a public release

When those facts change, the repo may legitimately need a docs-only canon repair or rebaseline if no safe next implementation lane should be selected yet.

That does not make standalone docs/governance branches the default.
The normal active-branch-first rule still applies while an implementation or release branch is open.
Use a standalone docs/governance branch only when repo truth is genuinely `No Active Branch`, the branch purpose is really governance or docs maintenance, and `Docs/phase_governance.md` says the branch class may begin.

## Current Policy

- preserve historical closeouts
- route historical lookup and current-baseline lookup through `Docs/closeout_index.md`
- use canonical workstream records for workstream-level detail
- do not let this guidance doc become a live current-state owner
- create new closeouts or rebaselines only when they materially improve future planning clarity
- keep emergency post-release canon repair distinct from a planned standalone docs/governance branch opened from `No Active Branch`
