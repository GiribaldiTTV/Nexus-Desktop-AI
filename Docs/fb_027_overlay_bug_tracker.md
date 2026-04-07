# FB-027 Overlay Bug Tracker

## Purpose

This document is a branch-focused working tracker for active and very recently closed bugs on:

- `feature/fb-027-overlay-usability`

It exists to support one-bug-at-a-time follow-through on this branch without turning branch-local bug work into:

- backlog management
- repo-wide bug governance
- PR or release readiness output

This file is a working truth surface for the active branch.
It is not a replacement for:

- `docs/feature_backlog.md`
- `docs/user_test_summary_guidance.md`
- version closeouts
- future milestone rebaseline docs

## Status Meanings

- `Confirmed Active`
- `Suspected / Not Yet Confirmed`
- `Fixed Pending User Confirmation`
- `Closed`

Use these states to keep bug work explicit and narrow.

## Evidence Normalization

The latest desktop:

- `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`

is still useful evidence, but it reflects an older mirroring-focused retest and does not fully represent the latest branch truth by itself.

Current normalized branch truth is:

- first-open immediate typing from both overlay hotkeys is working
- the mirrored-text bug is confirmed fixed
- the no-click input leakage bug family is confirmed fixed on the current branch state
- the caret visual bug is confirmed fixed on the current branch state
- the ambiguous-number selection path is confirmed fixed on the current branch state
- `Shift+Home` line-clearing convenience remains a later non-bug enhancement

This tracker should prefer the newest recoverable evidence, including:

- the latest returned desktop `User Test Summary.txt`
- later direct live test results preserved in chat
- branch-local code and helper state

## Current-Slice Active Bugs

- none currently

## Recently Closed On This Branch

### BUG-001A No-Click First Key Leaks To The Previously Focused Target

- Status:
  - `Closed`
- Evidence source:
  - direct live user confirmation on `2026-04-07`
  - helper validation for synchronous Win32 suppression
  - current launcher-path self-run
- Exact reproduction summary:
  1. activate a live caret in an outside text target
  2. open the NCP with no manual click
  3. begin typing a valid command such as `open file explorer`
- Current closure understanding:
  - the first typed letter no longer leaks to the previously focused target on the current branch state
  - synchronous fallback suppression in the Win32 hook contained the printable-key path strongly enough to close this bug

### BUG-001B No-Click First Enter Leaks To The Previously Focused Target

- Status:
  - `Closed`
- Evidence source:
  - direct live user confirmation on `2026-04-07`
  - helper validation
  - current launcher-path self-run
- Exact reproduction summary:
  1. activate a live caret in an outside text target
  2. open the NCP with no manual click
  3. type `open file explorer`
  4. press `Enter` once
- Current closure understanding:
  - the first `Enter` now lands in the NCP and no longer leaks to the previously focused target
  - the direct filter-level fallback `Enter` path closed the first-submit leak

### BUG-001C No-Click Second Enter Misses After Confirm

- Status:
  - `Closed`
- Evidence source:
  - direct live user confirmation on `2026-04-07`
  - helper validation for confirm-delay capture
  - current launcher-path self-run
- Exact reproduction summary:
  1. activate a live caret in an outside text target
  2. open the NCP with no manual click
  3. type `open file explorer`
  4. press `Enter` once to reach confirm
  5. wait a normal human pause
  6. press `Enter` again
- Current closure understanding:
  - the second `Enter` now lands cleanly in the NCP after confirm
  - the longer no-click confirm capture rearm was sufficient to keep the confirm path alive for a human second `Enter`

### BUG-002 Caret Keeps Flashing After Focus Leaves The NCP

- Status:
  - `Closed`
- Evidence source:
  - direct live user confirmation on `2026-04-07`
  - earlier direct user report after mirrored typing was already closed
- Exact reproduction summary:
  1. launch Nexus from the normal desktop shortcut
  2. open the NCP
  3. type or otherwise engage the entry path
  4. click into another app or control
  5. observe whether the caret continues flashing as though the NCP is still ready for typing
- Current closure understanding:
  - the caret-visual mismatch is now treated as fixed on the current branch state by direct user confirmation
  - it is no longer the active next bug for this branch

### BUG-003 Mirrored Typing After Focus Moves Elsewhere

- Status:
  - `Closed`
- Evidence source:
  - direct user confirmation after the no-click reproduction path was corrected
- Exact reproduction summary:
  1. open the NCP
  2. type into it
  3. click into another app
  4. type there
  5. text previously mirrored back into the NCP
- Current closure understanding:
  - no-click outside-click handling now stops the mirrored-text path reliably enough to treat it as closed on this branch
- Why it stays in this file:
  - the active `Enter` leak may share adjacent ownership logic, so keeping the closed bug visible helps avoid reopening it silently

### BUG-004 First-Open Typing Required Manual Click Or Cut Off Mid-Entry

- Status:
  - `Closed`
- Evidence source:
  - later direct user confirmation
- Exact reproduction summary:
  1. open the NCP with `Ctrl+Alt+Home` or `Ctrl+Alt+1`
  2. begin typing immediately without a click
  3. older branch state sometimes dropped characters, stopped mid-entry, or required manual click
- Current closure understanding:
  - first-open immediate typing now works from both overlay hotkeys
  - later random cutoff behavior was also confirmed closed in direct testing
- Why it stays in this file:
  - this branch has already passed through several input-ownership fixes, so keeping the closed path visible helps future drift checks

### BUG-005 Ambiguous Number Selection Fails Until Overlay Is Manually Refocused

- Status:
  - `Closed`
- Evidence source:
  - direct live user confirmation on `2026-04-07`
  - launcher-path self-run on `2026-04-07`
  - helper validation for delayed choose/confirm capture rearm
- Exact reproduction summary:
  1. launch Nexus from the normal desktop shortcut
  2. open the NCP
  3. type `open nexus folder`
  4. wait for the overlay to present numbered choices
  5. press `1` or `2` without manually refocusing the overlay
- Current closure understanding:
  - the choose-phase fallback capture window now stays alive long enough for a normal human delay
  - delayed `1` / `2` selection works without manually refocusing the overlay on the current branch state
  - direct live user confirmation closed the bug

## Suspected / Not Yet Confirmed

- none currently separated from the active bugs above

If a new bug is not yet reproducible enough to count as `Confirmed Active`, add it here first rather than silently upgrading it into active bug work.

## Later Ideas / Non-Bug Follow-Through

- `Shift+Home` line-clearing / line-selection convenience

This is a later usability idea, not a current-slice bug.
Do not fold it into active bug-fix work unless separately approved.

## Merge / Retirement Guidance

This tracker should remain branch-local while:

- the branch is active
- one-bug-at-a-time follow-through is still happening
- branch-local bug state would otherwise be lost between passes

After merge, preferred handling is:

- retire it if all tracked items are closed and no longer needed
- or preserve only if it still provides useful audit context for a closeout, rebaseline, or post-merge follow-through

Default recommendation:

- do not turn this file into a permanent repo-wide bug database
- treat it as a useful branch working artifact first
