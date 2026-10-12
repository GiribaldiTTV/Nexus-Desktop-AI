# UI Reference Catalog

These references describe product visual and interaction patterns. Each UIREF names the surface classes to which it applies and any known limitations. A screenshot is a comparison aid, not reusable code or proof that another window already matches it.

A shared primitive is actual reusable code or style. A template is a starting implementation. A reference is an example or behavior contract. New surfaces should reuse available product components and compare rendered states with the applicable references. If a reference conflicts with the feature's accessibility, trust, or platform constraints, choose a deliberate product exception and verify it in the actual window.

The catalog contains seven product references: top-level frames, window controls, control states/selectors, dialogs/status/recovery/doorways, design tokens/shared rules, negative examples for visual claims, and geometry/resize behavior. Each consuming feature remains responsible for its own rendered result, runtime state mapping, accessibility, and recovery.
