# Family Feature Categories

Family feature records describe product behavior within a broader family. They keep the user experience, feature boundaries, dependencies, and testable outcomes together. They do not describe development workflow or live project status.

A feature record should state its purpose, user-visible surfaces, normal flow, included capabilities, exclusions, stable element IDs, deferred capabilities, design tradeoffs, and observable acceptance criteria. A deferred capability should name what is missing and what technical or user-consent condition would make it usable. Describing a future feature does not activate it.

Use IDs such as `F7-FF01` for a feature category and `F7-FF01-E03` for a durable element. The title should name the product feature, not a development task. `Docs/family_feature_visions/index.md` maps IDs to the feature documents.

When one feature opens another, the opening surface owns only its doorway and truthful availability state. The destination owns its internal behavior. For user-visible surfaces, describe the applicable Nexus visual rules, platform-native exceptions, interaction states, resize behavior, accessibility, and failure/recovery behavior. Validate rendered behavior and real interaction for affected states; source markers or screenshots alone do not establish that a control works.

Cross-family dependencies should name the required interface and the owning feature. Sensitive actions such as provider execution, data sharing, downloads, installation, recording, deletion, and persistent personalization remain inactive until their actual product prerequisites and user choices are implemented and verified.
