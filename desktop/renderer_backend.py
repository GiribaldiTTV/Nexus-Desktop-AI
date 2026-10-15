"""Preserve the inherited Qt WebEngine environment for the renderer child."""

from __future__ import annotations

from collections.abc import Mapping


WEBENGINE_SOFTWARE_COMPOSITOR_FLAG = "--disable-gpu"
RENDERER_BACKEND_POLICY = "inherited-platform-default-and-parent-flags"
RENDERER_BACKEND_CLASSIFICATION = "shared-desktop-runtime-not-fam003-only"


def build_renderer_environment(parent_environment: Mapping[str, str]) -> dict[str, str]:
    """Copy parent settings without forcing a software compositor on all views."""

    env = dict(parent_environment)
    parent_flags = str(env.get("QTWEBENGINE_CHROMIUM_FLAGS") or "")
    env["NEXUS_RENDERER_PARENT_QTWEBENGINE_CHROMIUM_FLAGS"] = parent_flags
    env["NEXUS_RENDERER_EFFECTIVE_QTWEBENGINE_CHROMIUM_FLAGS"] = parent_flags
    env["NEXUS_RENDERER_BACKEND_POLICY"] = RENDERER_BACKEND_POLICY
    env["NEXUS_RENDERER_BACKEND_CLASSIFICATION"] = RENDERER_BACKEND_CLASSIFICATION
    return env
