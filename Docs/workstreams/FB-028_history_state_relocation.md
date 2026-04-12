# FB-028 History State Relocation

## ID And Title

- ID: `FB-028`
- Title: `Relocate launcher history state out of root logs`

## Record State

- `Closed`

## Status

- `Released (v1.2.3-prebeta)`

## Release Stage

- `pre-Beta`

## Target Version

- `v1.2.3-prebeta`

## Purpose / Why It Matters

Preserve the closed lane that relocated launcher-owned historical state out of the user-visible root logs tree without changing historical-memory semantics or widening logs or reporting policy.

## Current Truth And Boundaries

- normal runtime history resolves under `%LOCALAPPDATA%/Nexus Desktop AI/state/jarvis_history_v1.jsonl`
- successful migration no longer leaves the legacy root-log history file exposed
- fail-safe degradation remains in place if migration or new-state writes fail
- runtime logs, crash logs, and support-bundle locations remain unchanged

## Milestone Value Statement

The lane closed as a worthwhile root-logs-governance milestone because it removed launcher-owned history from live root logs without changing historical-memory behavior.

## Scope

- launcher-owned historical-state relocation only
- one-time migration and fallback behavior
- preserving live runtime and crash roots plus dev evidence roots

## Non-Goals

- moving runtime logs
- moving crash logs
- changing support-bundle locations
- redesigning historical-memory semantics

## Stages / Executed Stages

1. relocated launcher-owned historical state to a dedicated non-user-facing state root
2. preserved migration and fail-safe degradation behavior
3. kept contained history harness runs isolated under contained roots
4. released the lane in `v1.2.3-prebeta`

## Same-Branch Follow-Through

Closed. Only future evidence-driven refinement should reopen this area.

## Blockers / Holds / Stop Conditions

Closed. Wider logs-root cleanup remains out of scope for this preserved record.

## Validation / Evidence Summary

Closure depended on validation proving that history writes no longer spilled into live root logs while runtime logs, crash logs, and support-bundle locations remained unchanged.

## User Test Summary

No separate ongoing User Test Summary artifact remains for this closed lane.

## Closure Summary

Released in `v1.2.3-prebeta` as a bounded runtime-state relocation milestone.

## Deferred Forward

- later evidence-driven refinement only if the released relocation behavior needs it

## Related References

- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/development_rules.md`
- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.2.8-prebeta.md`
