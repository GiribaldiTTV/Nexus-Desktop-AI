# Closeout Guidance

## Purpose

This document defines what closeouts are for, when they are required, when they are optional, and how Nexus Desktop AI should handle closeout drift.

It exists because the repo has a historical closeout line, but the current Nexus pre-Beta release cadence moved forward without a clear replacement rule for every newer release milestone.

This document is downstream of:

- `development_rules.md`
- `Main.md`
- `codex_modes.md`
- `orin_vision.md`

If this document conflicts with those files, those files win.

Use:

- `docs/closeout_guidance.md` for closeout policy
- `docs/closeout_index.md` for closeout lookup
- `docs/closeouts/...` for the actual historical closeout records

## What A Closeout Is

A closeout is a source-of-truth audit for a completed version lane or milestone.

Its job is to:

- record what is complete
- record what remains intentionally deferred
- lock in the accepted guarantees at that layer
- give future planning a clean baseline
- reduce prompt bloat by letting later prompts cite the closeout instead of replaying all prior work

A closeout is not the same thing as:

- a release tag
- GitHub release notes
- a merged branch
- a PR summary

Those are related artifacts, but they do different jobs.

## What Drift Happened

The historical Jarvis line used closeouts regularly through:

- `v1.6.0`
- `v1.7.0`
- `v1.8.0`
- `v1.9.0`
- `v2.0`
- `v2.2.0`
- `v2.2.1`

After that, the Nexus pre-Beta public release line moved to:

- `v1.0.0-prebeta`
- `v1.0.1-prebeta`
- `v1.1.0-prebeta`
- `v1.1.1-prebeta`

but no matching closeout series was created for those newer pre-Beta releases.

That drift happened because:

- the project shifted from the earlier Jarvis version-lane cadence to a newer Nexus pre-Beta release cadence
- releases and branch milestones continued
- but closeout policy was not explicitly redefined for the new cadence

So the repo ended up in a mixed state where:

- historical closeouts still matter
- current canon still references closeouts as real planning surfaces
- but newer Nexus pre-Beta releases have been carried mostly by tags, release notes, branch truth, and source-of-truth doc updates rather than by dedicated closeout docs

## Are Closeouts Still Needed

Yes.

Closeouts are still useful because they:

- create a stable planning baseline
- reduce repeat prompt bulk
- clarify what is intentionally complete versus merely paused
- make post-release sequencing cleaner
- reduce drift between merged work, backlog truth, and future planning

But they are not needed for every tiny release or every docs-only pass.

## Required, Recommended, And Optional Closeouts

### Required

A closeout should be required when:

- a coherent version lane has actually closed
- a milestone materially resets future planning baseline
- the next planning step depends on clearly knowing what is now locked versus deferred
- a release line has accumulated enough change that relying only on branch history and chat memory would create drift risk

### Recommended

A closeout is recommended when:

- a merged workstream created a meaningful user-visible milestone
- several related slices now form one coherent completed milestone
- prompt reduction would materially benefit from having a new stable baseline doc
- a release or milestone changed the practical "what is true now" answer for future planning

### Optional

A closeout is optional, and often unnecessary, when:

- the work is a tiny follow-through patch
- the pass is docs-only governance with no major planning reset
- the milestone does not materially change future sequencing
- the latest truth already lives clearly in canonical docs and a new closeout would mostly duplicate that truth

## Nexus Pre-Beta Rule

For the current Nexus pre-Beta line, closeouts should usually be milestone-based, not release-by-release by default.

That means:

- do not force a new closeout doc for every small pre-Beta patch release
- do create a closeout when a meaningful milestone or lane has actually stabilized and future planning will benefit from a fresh baseline

Examples that usually do not need their own closeout:

- tiny usability follow-through
- narrow docs-only governance sync
- one small regression fix release

Examples that likely do need a closeout:

- a completed multi-slice interaction milestone
- a major pre-Beta baseline shift
- a milestone that materially changes what future prompts should carry forward

## Release, Closeout, And Rebaseline

These should be treated as separate tools:

- `release`
  - a published version/tag/release event
- `closeout`
  - a source-of-truth audit for a completed milestone or version lane
- `rebaseline`
  - a catch-up canonical baseline when many small steps happened without individual closeouts

If Nexus pre-Beta continues through several small releases without closeouts, the clean corrective move is usually:

- one rebaseline or milestone closeout

not:

- one retroactive closeout doc for every missed small patch release

## Cleanup Recommendation For Current Drift

The current recommended cleanup is:

1. keep existing historical closeouts
2. keep them organized under `docs/closeouts/`
3. use an index doc for lookup rather than merging all closeouts into one large historical file
4. do not rewrite them just to modernize wording
5. do not create retroactive closeout docs for every missed Nexus pre-Beta patch release
6. create a new closeout or rebaseline only when the next milestone genuinely justifies it

This keeps the history useful without manufacturing unnecessary documentation churn.

## Current Recommendation

For the current repo state:

- historical closeouts should remain in place
- closeouts should not be treated as abandoned
- closeouts should resume when the next meaningful Nexus milestone closes, not automatically after every small patch

If a future planning pass needs a fresh post-`v1.1.1-prebeta` canonical baseline before broader next-lane work, the best move would be:

- one Nexus-era milestone rebaseline or closeout

rather than trying to backfill every missing pre-Beta patch release individually.
