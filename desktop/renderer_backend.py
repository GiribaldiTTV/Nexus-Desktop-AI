"""Shared Qt WebEngine environment policy for the desktop renderer child."""

from __future__ import annotations

from collections.abc import Mapping


WEBENGINE_SOFTWARE_COMPOSITOR_FLAG = "--disable-gpu"
RENDERER_BACKEND_POLICY = "temporary-shared-runtime-safety-policy"
RENDERER_BACKEND_CLASSIFICATION = "shared-desktop-runtime-not-fam003-only"


def build_renderer_environment(parent_environment: Mapping[str, str]) -> dict[str, str]:
    """Return the renderer-child environment with one software-compositor flag."""

    env = dict(parent_environment)
    parent_flags = str(env.get("QTWEBENGINE_CHROMIUM_FLAGS") or "").strip()
    normalized_tokens: list[str] = []
    for token in parent_flags.split():
        if token not in normalized_tokens:
            normalized_tokens.append(token)
    if WEBENGINE_SOFTWARE_COMPOSITOR_FLAG not in normalized_tokens:
        normalized_tokens.append(WEBENGINE_SOFTWARE_COMPOSITOR_FLAG)

    effective_flags = " ".join(normalized_tokens)
    env["QTWEBENGINE_CHROMIUM_FLAGS"] = effective_flags
    env["NEXUS_RENDERER_PARENT_QTWEBENGINE_CHROMIUM_FLAGS"] = parent_flags
    env["NEXUS_RENDERER_EFFECTIVE_QTWEBENGINE_CHROMIUM_FLAGS"] = effective_flags
    env["NEXUS_RENDERER_BACKEND_POLICY"] = RENDERER_BACKEND_POLICY
    env["NEXUS_RENDERER_BACKEND_CLASSIFICATION"] = RENDERER_BACKEND_CLASSIFICATION
    return env
