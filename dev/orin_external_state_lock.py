from __future__ import annotations

import argparse

from orin_external_state_common import (
    DEFAULT_EXTERNAL_STATE_ROOT,
    DEFAULT_SCHEMA_VERSION,
    atomic_write_json,
    new_lock_id,
    resolve_path,
    utc_now,
    validate_canonical_root,
    validate_initialized_root,
)


LOCK_TYPES = {
    "state-root",
    "migration",
    "release-window",
    "worktree",
    "branch",
    "review-bundle",
    "fold-down",
    "governance-candidate",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create dry-run or applied External Governance State lock packets.")
    parser.add_argument("--root", default=str(DEFAULT_EXTERNAL_STATE_ROOT))
    parser.add_argument("--lock-type", required=True, choices=sorted(LOCK_TYPES))
    parser.add_argument("--owner", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--intended-write-set", required=True)
    parser.add_argument("--expires", required=True, help="Expiration timestamp or policy text")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA_VERSION)
    parser.add_argument("--apply", action="store_true", help="Write lock file. Omit for dry-run packet.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.apply:
        print("BLOCK: retired legacy mutation route; --apply is not current authority")
        return 1
    root = resolve_path(args.root)
    root_issues = validate_canonical_root(root)
    lock_id = new_lock_id(args.lock_type)
    lock_payload = {
        "External State Schema": args.schema,
        "State Version": 1,
        "Last Updated": utc_now(),
        "Last Updated By": args.owner,
        "Worktree": args.worktree,
        "Branch": args.branch,
        "Source Repo HEAD": "not captured by lock scaffold",
        "Lock ID": lock_id,
        "Lock Type": args.lock_type,
        "Lock State": "Locked",
        "Intended Write Set": args.intended_write_set,
        "Expiration": args.expires,
    }

    print("External State Lock Packet")
    print(f"Root: {root}")
    print(f"Lock ID: {lock_id}")
    print(f"Lock Type: {args.lock_type}")
    print("Lock State: Locked")
    print(f"Mutation Approval: {'Granted by --apply' if args.apply else 'Not granted - dry run'}")

    if root_issues:
        print("Lock Result: BLOCKED")
        for issue in root_issues:
            print(issue)
        return 1
    if not root.exists():
        print("Lock Result: External State Missing")
        return 1 if args.apply else 0
    initialization_issues = validate_initialized_root(root, args.schema)
    if initialization_issues:
        print("Lock Result: BLOCKED")
        for issue in initialization_issues:
            print(issue)
        return 1

    if not args.apply:
        print("Lock Result: READY - no lock file created")
        return 0

    lock_path = root / "locks" / f"{lock_id}.json"
    atomic_write_json(lock_path, lock_payload)
    print(f"Lock Result: APPLIED - {lock_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
