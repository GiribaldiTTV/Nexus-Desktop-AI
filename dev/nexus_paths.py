# NEXUS-SOURCE-OWNER: schema=source-owner-v1; owner=GOV-SOURCE-TRUTH; ledger=SRCOWN-FIRSTPASS-VALIDATOR-010; surface=workspace-root-paths; status=shared
"""Canonical current Nexus filesystem roots.

The canonical product repository and task-scoped external roots are on D:.
The C: product copy is a retained rollback predecessor, not current authority.
"""

from __future__ import annotations

from pathlib import Path


NEUTRAL_MAIN_ROOT = Path(r"D:\Nexus Desktop AI\Product Repository")
NEXUS_DATA_ROOT = Path(r"D:\Nexus Desktop AI Data")  # Retained supplemental roots, not one current source root.
WORKTREES_ROOT = Path(r"D:\Nexus Desktop AI\Worktrees")
EXTERNAL_STATE_ROOT = Path(r"D:\Nexus Desktop AI\Governance State")
USER_HUB_ROOT = Path(r"D:\Nexus Desktop AI\USER")
REPOS_ROOT = NEXUS_DATA_ROOT / "Repos"
DEV_ORIN_ROOT = NEXUS_DATA_ROOT / "Dev ORIN"
ARTIFACTS_ROOT = NEXUS_DATA_ROOT / "Artifacts"
CODEX_WORKTREES_ROOT = NEXUS_DATA_ROOT / "Codex Worktrees"
MIGRATION_EVIDENCE_ROOT = NEXUS_DATA_ROOT / "Migration Evidence"
GOVERNANCE_WORKTREE = WORKTREES_ROOT / "Governance"


def windows_text(path: Path) -> str:
    """Return a stable Windows display path for packets and diagnostics."""

    return str(path)
