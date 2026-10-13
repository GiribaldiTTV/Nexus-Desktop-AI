# Runtime Failure Patterns

Concrete engineering lessons from Nexus runtime failures and user-facing defects. These patterns describe affected behavior and checks; they do not create workflow phases or approval gates.

## Backend truth hidden behind a green UI

A screen, marker, or helper can look correct while its runtime state, failure path, or recovery behavior is wrong. For each visible success, blocked, degraded, disabled, or recovered state, verify the owning runtime state transition and the resulting UI label. Logs support diagnosis; they do not by themselves prove the user-visible result. Check schema and configuration compatibility where state persists.

## Screenshot-tuned repair

A magic pixel, fixed row count, default-size-only layout, or one-state assertion can repair the current screenshot and fail on the next same-class item. Derive layout and state rules from the component class; test relevant sizes, states, and extensions. Do not implement speculative future features just to make the current repair reusable.

## No window-geometry recovery path

A movable or persisted Nexus window can become offscreen, too small, or trapped on a missing monitor. Such windows need safe default geometry and a user-accessible reset or recovery route when persistence is supported. FAM-002 defines visual/geometry behavior; FAM-003 settings or resident controls may expose the reset action. Verify missing-monitor and corrupted-position recovery.

## Content-style header close control

A large labeled header `CLOSE` button on a standalone window can be confused with a content action, especially when a footer also has `Close`, `Cancel`, or `Exit`. Use a compact Nexus-native window-control cluster for window management where applicable, keep content actions distinct, and verify hitboxes, keyboard access, hover/focus, and minimize/restore behavior.

## One-size or marker-only geometry proof

Opening a window at its default size or observing a marker does not prove responsive layout. Check minimum, default, wide, and applicable maximize states; DPI and multi-monitor behavior; scroll, wrap, truncation, collapse, and footer attachment. A focused screenshot cannot override contradictory full-window or desktop context.

## Planned prerelease mistaken for released version

When Git metadata is unavailable, support bundles and issue reports must derive fallback version context from the latest actually released prerelease, not the highest planned target. Verify the Git-present and Git-unavailable report paths agree.

## Recoverable launch failure widened into a fatal path

A repeated identical recoverable `launch_failed` class may warrant focused diagnostics, but must not change all recoverable failures into popups or fatal handling. Verify that the selected class alone receives the bounded treatment, while manual reporting and fatal launcher behavior remain distinct.
