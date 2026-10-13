# FAM-007 AI Edition Capability / Trust Boundary Release Plan


## Purpose

Define the Public, Dev, and Owner edition capability and trust boundaries for Nexus Desktop AI. These are product design and distribution safeguards. They do not turn on provider/model execution, private data import, memory, packaging, or a new edition merely by describing it.

## Core Model

The project should use an Edition Capability / Trust Boundary model, not three unrelated forks.

The goal is one shared public-safe core with edition-specific capability gates, private overlays, separate data identities, separate update channels, and strict no-leak rules.

| Edition | Product Name | Trust Boundary | Main Purpose | Public Repo Inclusion |
| --- | --- | --- | --- | --- |
| Public | `Nexus Desktop AI` | Least privilege | Normal user-facing product | Public-safe core, docs, validators, and generic gates |
| Dev | `Nexus Desktop AI Dev` | Trusted contributor | Development, validation, repo-aware support | Public-safe hooks only; private Dev intelligence stays outside public repo |
| Owner | `Nexus Desktop AI Owner` | Owner-only highest trust | Private co-developer AI and personal product partner | No private Owner logic, memory, prompts, secrets, evals, or tools |

## Shared Core Experience And Capability Envelopes

Public, Dev, and Owner editions should feel like one coherent Nexus Desktop AI product. The edition split changes capability access, trust boundary, private context, installed identity, and release/update channel. It must not create three unrelated apps with different normal usability, visual grammar, Windows workload behavior, privacy rules, troubleshooting expectations, or product experience semantics.

All editions should preserve the shared core experience:

- same Project Vision and NDAI Product Experience Contract for deterministic, intuitive, immersive, predictable, reliable, and consistent behavior
- same FAM-002 presentation grammar for Nexus-owned windows, controls, cards, status rows, dropdowns, filters, menus, dialogs, tray-opened surfaces, and window-control clusters unless a deliberate product exception is USER-approved, recorded, justified, and verified
- same normal workflows for opening Nexus surfaces, using resident actions, managing standard Windows workloads, reviewing settings, seeing blocked/deferred/unavailable states, and recovering from failures when those capabilities are available
- same privacy and trust posture for local-only, no-provider, provider-assisted, disabled, blocked, degraded, consent-required, troubleshooting, and private-boundary states
- same backend-to-visual truth rule: UI labels, assistant responses, status rows, and proof claims must reflect the actual runtime/provider/memory/cache/private capability state

Edition differences are capability envelopes, not basic usability differences:

- Public Edition includes the shared core and public-safe capabilities. Optional public capability packages may later become subscription-based, purchase-based, entitlement-gated, or otherwise commercialized, but this document does not decide that business model.
- Dev Edition includes the shared core plus developer-focused tools and agents. Future Dev surfaces may expose a Developer category in the tray, resident menu, Global Settings, AI Command Center, or another product doorway when FAM-003, FAM-002, FAM-007, and FAM-008 routing permits it. Dev tools may include troubleshooting helpers, GitHub issue and solution workflows, log import helpers, validation helpers, diagnostics, and other development-support agents. Dev may receive access to public paid packages without the same public purchase/subscription model only if later source truth approves that policy. Dev must not include Owner-only feature creation, innovation, project-control, owner-private agents, Owner memory, Owner prompts, Owner strategy, or Owner secrets.
- Owner Edition includes the shared core plus Public and Dev capability layers plus Owner-exclusive agents and project-control capabilities. Owner may include feature creation, innovation and intuitive planning, private project assistance, advanced repo/project governance support, private automation, and other Owner-only capabilities. Owner is the most powerful edition and requires the strictest privacy, data, memory, provider, leak-prevention, backup, and export boundaries.

Enhanced troubleshooting is not automatically enabled by edition identity. Dev or Owner status may make stronger troubleshooting tools available, but enhanced troubleshooting must still be explicitly launched or enabled through the tray/resident UI, Global Settings, AI Command Center, or another approved user-visible control path. It must remain intentional, reversible, auditable, and visible enough that the USER understands when additional diagnostics, logs, provider-visible data, or development tools are active.

These capabilities remain inactive until their product design, consent, technical safeguards, and verification exist.

## Public Repo Rule

The public repository may define the edition model, generic capability gates, safe manifest schema, public-safe test fixtures, and validators.

The public repository must not contain:

- owner-private prompts
- owner-private memory
- owner-private strategy, planning notes, or repo roadmap material not approved for public release
- owner GitHub tokens, API keys, credentials, cookies, sessions, or secrets
- private Dev ORIN content
- private eval logs
- private model weights or proprietary capability packs
- private assistant instructions that would allow someone to clone the Owner or Dev intelligence layer
- hidden provider/model/memory behavior
- dev-only UI markers in production/public UI

The safest rule is simple: if losing the public repo would expose it, it cannot be the thing that makes Owner or Dev special.

## Protected Assets Table

Protected assets are the material that gives Dev or Owner editions private value, private authority, private context, or private access. Future branches and validators should use this table as the public-safe reference for what must be excluded, gated, sanitized, or kept private.

| Asset Class | Examples | Public Repo Allowed | Dev Repo Allowed | Owner Repo Allowed | Public Artifact Allowed | Required Gate |
| --- | --- | --- | --- | --- | --- | --- |
| Owner memory | owner-private accepted feedback, owner-specific memories, long-term preferences, private interaction history, and feedback not approved for public source truth | No | No | Yes, only with owner-approved local/private storage | No | Owner memory consent, local vault/encryption plan, no-export default |
| Owner prompts and instructions | private system prompts, owner-specific Codex handoff rules, private assistant behavior prompts | No | No | Yes | No | Owner-only source root or private repo plus private-to-public sanitization before any excerpt leaves Owner |
| Private strategy and planning | private strategy, private planning material, owner roadmap material not approved for public release, competitive/product timing notes | No | No by default | Yes | No | USER approval and sanitized public-safe summary only |
| Secrets and credentials | GitHub tokens, provider keys, API keys, cookies, sessions, signing keys, vault secrets | No | No tracked storage; only scoped local secret store when approved | No tracked storage; only scoped local/owner vault when approved | No | Secret scan, vault/credential-store plan, no tracked plaintext |
| Private Dev ORIN content | private Dev ORIN prompts, evals, workflows, unpublished developer helper instructions | No | Yes, if contributor-scoped and not owner-private | Only if manually selected by Owner | No | Dev private repo gate and no-owner-private scan |
| Private eval logs and support data | raw eval conversations, debug logs, support bundles, screenshots, crash dumps, imported Public user diagnostics | No unless synthetic/sanitized | Yes only when scoped, redacted, and user-approved | Yes only when owner-approved | No by default | Redaction, provenance, user consent, and no-export review |
| Private model or capability assets | model weights, adapters, private capability packs, proprietary data files, entitlement-gated binaries | No | Yes only in private artifact channel or private repo when licensed | Yes only in private artifact channel or private owner root | No unless public license/distribution is approved | License / redistribution review, artifact provenance, SBOM or manifest review, integrity/signature proof, signed artifact gate, public release approval |
| Private automation | owner automation scripts, unrestricted repo/GitHub actions, private repair loops, private watcher/reporting routes | No | Yes only when dev-scoped and audited | Yes only when owner-approved and reversible | No | Tool permission review, audit log, bounded action contract |
| Imported Public user data | Public settings, consent state, personalization, logs, future memory imported into Dev | No as raw data | Yes only after explicit import consent and no-export default | No by default; sanitized fixtures only | No | Public-to-Dev import consent level and provenance stamp |
| Dev-only UI/tooling metadata | source-owner overlays, development-only tools, review markers, debug badges, dev launchers | Public-safe docs/validators only | Yes | Yes if owner chooses | No production public UI | Public build exclusion and no-dev-tooling-in-public-UI validation |
| Hidden provider/model/memory behavior | undisclosed prompt send, model execution, memory indexing, background network egress | No | No unless explicitly developer-visible and approved | No unless explicitly owner-approved and audited | No | Provider-visible data, consent, network, memory, and execution gates |

## Public-Safe Fixture Rule

Public-safe fixtures must be synthetic, non-secret, non-owner-specific, non-memory-derived, non-token-derived, and not copied from private logs unless sanitized and USER-approved.

Fixtures in the public repo may demonstrate schemas, state transitions, validation boundaries, and no-leak rules, but they must not contain real Owner memory, real Dev/private content, real user logs, real provider credentials, private strategy, private planning material, private model data, or owner roadmap material not approved for public release.

## Public Distribution Boundary

Public source, support exports, installers, and released artifacts must exclude Dev/Owner prompts, memory, secrets, private logs, strategy, evals, credentials, and protected model or capability assets. Synthetic fixtures may describe safe schemas but cannot contain copied private content. A product build must not expose developer or owner-only controls in the Public Edition.

Provider, cache, memory, and capability-pack controls should present truthful disabled states until their product behavior, consent, data lifecycle, and technical protections exist. A visible blocked control is not evidence that the capability works.

## Edition Names

Public Edition name: `Nexus Desktop AI`.

Dev Edition working name: `Nexus Desktop AI Dev`. This is accepted for planning and may be renamed by USER before packaging if desired.

Owner Edition accepted name: `Nexus Desktop AI Owner`.

## Public Edition Vision

Public Edition should eventually provide:

- user-facing assistant behavior
- visible provider state
- visible consent state
- safe local-first defaults
- optional capability packs
- clear no-provider and degraded-mode behavior
- safe setup completion and reset behavior
- no hidden data egress
- no hidden provider/model execution
- no dev-only tooling
- no owner-private context

Public Edition must not include:

- GitHub/repo automation intended for owner or contributor workflows
- source-owner review overlays
- development-only tools exposed in production UI
- owner-private memory
- owner-private instructions
- developer tokens
- private eval harnesses
- unrestricted local automation

## Dev Edition Vision

Dev Edition should eventually provide:

- issue and PR intake support
- log and support bundle analysis
- repo navigation
- validation guidance
- source-owner review support
- branch/source-truth awareness
- debug assistance
- contributor-scoped GitHub/repo helpers
- Public-to-Dev profile import with explicit USER approval

Dev Edition must not include:

- owner-private memory
- owner GitHub credentials
- owner-only private planning
- unrestricted automation
- production-user data export by default
- hidden provider/model behavior

Dev Edition is trusted, but it is not owner-private.

Dev Boundary: Dev Edition may contain contributor/dev tooling, but it must not inherit Owner memory, Owner prompts, Owner strategy, Owner credentials, Owner automation, Owner private planning, or owner roadmap material not approved for public release by default. Dev is allowed to be powerful for contributor workflows; it is not allowed to become a backdoor copy of Owner.

## Owner Edition Vision

Owner Edition should eventually provide:

- private AI partner behavior
- product vision support
- creative planning support
- project-development assistance
- Codex handoff support
- validation review
- issue/log intake
- private memory with explicit local consent and safeguards
- owner-specific development workflows
- reversible owner-approved automation

Owner Edition must not ship as the public user product.

Owner Edition must not leak:

- owner memory
- owner prompts
- owner strategy
- private strategy
- private planning material
- owner roadmap material not approved for public release
- owner GitHub credentials
- private logs
- private model or capability-pack assets
- private repo automation

Owner As Private Test Person: Owner Edition may act as a private test/evaluation persona for Public Edition, including launching, testing, and evaluating the public user experience as the owner, but Owner behavior is not shipped Public Edition behavior. Owner behavior cannot define Public runtime behavior unless a later public-safe branch implements, validates, and releases that behavior with public-safe behavior and verification.

Owner Screenshots, Logs, And Evals: Owner screenshots, Owner logs, Owner evaluation transcripts, private model outputs, and private Codex handoff artifacts are Owner-private by default. They may become public evidence only after the user explicitly selects that material and it is sanitized for the intended public use.

## Edition Data And Capability Isolation

Public, Dev, and Owner editions need separate application identities, data roots, logs, update channels, caches, and secret stores when those editions exist. The Public Edition must not load private prompts, Owner memory, contributor logs, private assets, or credentials. Dev tools must not inherit Owner-only context. Enhanced troubleshooting remains intentional, visible, reversible, and scoped even in Dev or Owner.

Capability state should be represented explicitly: unavailable, installed, enabled, disabled, consent-required, blocked, or failed. UI copy and assistant responses must match actual runtime state. Optional capability packs require source, license, integrity, disk-space, install, update, removal, and recovery behavior before they can execute.

## Data Movement And Privacy

Moving selected Public data to a higher-trust edition requires user choice of data classes, provenance, and a no-export default. Moving Dev or Owner material into the Public Edition requires sanitization and explicit selection; public-safe reimplementation is preferable to copying private files. Public restore must not import Dev or Owner state; Dev restore must not import Owner state.

Private memory, logs, screenshots, prompts, model outputs, and backups are protected by default. A durable personalization or memory feature needs user-controlled storage, deletion, export, reset, and an off-boot recovery option before it claims to protect long-lived state. A second physical or encrypted off-device copy may be appropriate for whole-machine loss, but backup behavior remains inactive until implemented and verified.

## Packaging And Release Behavior

If multiple editions ship, their executable identities, shortcuts, taskbar grouping, data locations, update channels, and uninstall behavior must be distinguishable. Installation and updates must not silently turn on provider execution, private import, memory, or enhanced diagnostics. Public packages must exclude private dependencies and content. A version label or edition name does not establish feature readiness.

## Product Verification

- Public builds contain no private assets, credentials, private paths, or hidden Dev/Owner UI.
- No-provider behavior remains useful and accurately reports provider-visible data as `none` when no provider call occurred.
- Provider calls, downloads, memory, cache persistence, and private setup remain disabled until their explicit controls and safeguards exist.
- Capability-pack setup rejects unknown or untrusted sources and supports recovery/removal where installed.
- Data import/export preserves edition boundaries, user selection, and provenance.
- Installation, update, startup, and recovery use the correct edition identity without overwriting another edition's data.
- User-facing status matches actual runtime state in normal, blocked, degraded, failed, and recovery paths.
