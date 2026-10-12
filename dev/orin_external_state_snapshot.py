from __future__ import annotations

import argparse

from orin_external_state_common import (
    DEFAULT_EXTERNAL_STATE_ROOT,
    DEFAULT_SCHEMA_VERSION,
    atomic_write_json,
    copy_tree_snapshot,
    new_lock_id,
    resolve_path,
    utc_now,
    validate_canonical_root,
    validate_initialized_root,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create dry-run or applied External Governance State snapshots.")
    parser.add_argument("--root", default=str(DEFAULT_EXTERNAL_STATE_ROOT))
    parser.add_argument("--reason", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--created-by", default="Codex")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA_VERSION)
    parser.add_argument("--apply", action="store_true", help="Write snapshot files. Omit for dry-run.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.apply:
        print("BLOCK: retired legacy mutation route; --apply is not current authority")
        return 1
    root = resolve_path(args.root)
    root_issues = validate_canonical_root(root)
    snapshot_dir = root / "snapshots" / new_lock_id("snapshot")

    print("External State Snapshot Packet")
    print(f"Root: {root}")
    print(f"Snapshot Directory: {snapshot_dir}")
    print(f"Reason: {args.reason}")
    print(f"Mutation Approval: {'Granted by --apply' if args.apply else 'Not granted - dry run'}")

    if root_issues:
        print("Snapshot Result: BLOCKED")
        for issue in root_issues:
            print(issue)
        return 1
    if not root.exists():
        print("Snapshot Result: External State Missing")
        return 1 if args.apply else 0
    initialization_issues = validate_initialized_root(root, args.schema)
    if initialization_issues:
        print("Snapshot Result: BLOCKED")
        for issue in initialization_issues:
            print(issue)
        return 1
    if not args.apply:
        print("Snapshot Result: READY - no snapshot created")
        return 0

    copied = copy_tree_snapshot(root, snapshot_dir)
    manifest = {
        "External State Schema": args.schema,
        "State Version": 1,
        "Last Updated": utc_now(),
        "Last Updated By": args.created_by,
        "Root": str(root.resolve()),
        "Worktree": args.worktree,
        "Branch": args.branch,
        "Source Repo HEAD": "not captured by snapshot scaffold",
        "Snapshot Reason": args.reason,
        "Copied Files": copied,
    }
    atomic_write_json(snapshot_dir / "snapshot_manifest.json", manifest)
    print(f"Snapshot Result: APPLIED - {len(copied)} files copied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
