"""Release one external-state lock through an auditable atomic transition."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from orin_external_state_common import (
    DEFAULT_EXTERNAL_STATE_ROOT,
    atomic_write_json,
    load_json,
    resolve_path,
    utc_now,
    validate_canonical_root,
    validate_initialized_root,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Release one External Governance State lock.")
    parser.add_argument("--root", default=str(DEFAULT_EXTERNAL_STATE_ROOT))
    parser.add_argument("--lock-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--apply", action="store_true")
    return parser


def _before_release_atomic_replacement(_lock_path: Path, _expected_bytes: bytes) -> None:
    """Test seam for adversarial lock mutation before final release validation."""


def release_lock(root: Path, lock_id: str, reason: str, apply: bool) -> tuple[bool, list[str]]:
    if apply:return False, ["BLOCK: retired legacy mutation route; use the selected checked Control Plane owner"]
    root = resolve_path(root)
    failures = validate_canonical_root(root)
    failures.extend(validate_initialized_root(root))
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", lock_id):
        failures.append(f"Lock ID is not a safe filename: {lock_id!r}")
    lock_path = root / "locks" / f"{lock_id}.json"
    if not lock_path.is_file():
        failures.append(f"Lock is missing: {lock_path}")
    if failures:
        return False, failures
    try:
        initial_lock_bytes = lock_path.read_bytes()
    except OSError as exc:
        return False, [f"Lock is unreadable: {lock_path}: {exc}"]
    try:
        payload = load_json(lock_path)
    except Exception as exc:  # noqa: BLE001 - corrupt operational state blocks release
        return False, [f"Lock is unreadable: {lock_path}: {exc}"]
    if payload.get("Lock ID") != lock_id:
        return False, [
            f"Lock payload ID mismatch: expected {lock_id!r}, found {payload.get('Lock ID')!r}"
        ]
    if payload.get("Lock State") not in {"Locked", "Expired"}:
        return False, [f"Lock is already released or invalid: {lock_path}"]
    payload["Lock State"] = "Released"
    payload["Released At"] = utc_now()
    payload["Release Reason"] = reason
    payload["Last Updated"] = utc_now()
    if not apply:
        return True, [f"READY: {lock_path}", "No write performed; omit --apply was honored"]
    _before_release_atomic_replacement(lock_path, initial_lock_bytes)
    try:
        final_lock_bytes = lock_path.read_bytes()
    except OSError as exc:
        return False, [f"Lock changed during release validation; no write performed: {exc}"]
    if final_lock_bytes != initial_lock_bytes:
        return False, ["Lock changed during release validation; no write performed"]
    atomic_write_json(lock_path, payload)
    return True, [f"RELEASED: {lock_path}"]


def main() -> int:
    args = build_parser().parse_args()
    ok, messages = release_lock(Path(args.root), args.lock_id, args.reason, args.apply)
    print("External State Lock Release")
    for message in messages:
        print(message)
    print(f"Release Result: {'PASS' if ok else 'BLOCKED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
