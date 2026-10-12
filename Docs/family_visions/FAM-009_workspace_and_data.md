# Pending Fold Source: Workspace And Data

## Purpose

This file is retained only as no-loss source material while workspace/data direction is folded into existing backlog-family visions and architecture owners.

This is retained product-design source, not a standalone active feature family. Workspace and data requirements apply within the product features that own the affected files or user flows.

Workspace layout, data roots, logs/evidence organization, support bundles, dev-toolkit data intake, and local file hygiene now fold into the implementing family vision and `Docs/ai_runtime_and_trust_architecture.md` where relevant.

## Vision Summary

Workspace and Data should keep Nexus understandable on disk. Evidence, logs, support bundles, user data, and dev outputs should have clear owners, retention expectations, and safe cleanup paths.

## Accepted Direction

- Keep live operational truth derived from Git, GitHub, or helpers, not copied into docs.
- Keep evidence roots organized and reviewable.
- Make support bundle and diagnostics paths traceable without exposing private data unnecessarily.
- AI operational cache storage, cache evidence, cache journaling paths, retention windows, corruption quarantine, and clear-cache file hygiene belong here only as workspace/data-root direction; cache contents remain governed by the AI/runtime and privacy owners.
- AI-related roots should distinguish operational cache, Trust Journal entries, support logs, backups, capability-pack indexes, model/capability-pack assets, and user data instead of collapsing them into one hidden data bucket.
- Cache corruption recovery should quarantine or rebuild damaged cache with reviewable evidence rather than silently reusing damaged state.
- Backup/export root guidance must not imply memory, cache, provider data, private Owner material, or capability-pack migration without a later USER-approved package and privacy/safety proof.
- Explain user-data cleanup and retention before deleting product files; preserve recovery where data loss is possible.

## Implementation Boundaries

- This vision does not admit cleanup, deletion, data migration, support-bundle behavior changes, or GitHub Desktop rebinding by itself.
- Workspace/data behavior belongs to the feature that creates, reads, exports, or deletes that data and must include safe cleanup and recovery.

## Related Product Design

- `Docs/nexus_vision.md` for the overall experience.
- `Docs/ai_runtime_and_trust_architecture.md` for AI data, cache, and privacy boundaries.
- The affected feature document for any actual workspace, data-root, support-export, or cleanup behavior.
