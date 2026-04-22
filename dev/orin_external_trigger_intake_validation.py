from dataclasses import FrozenInstanceError
import os
import sys


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from desktop.external_trigger_intake import (
    InternalTriggerIntakeBoundary,
    TRIGGER_INTAKE_DECISION_DEFERRED,
    TRIGGER_INTAKE_DECISION_REJECTED,
    TriggerOriginRegistration,
    TriggerOriginRegistry,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_evidence(
    evidence,
    message: str,
    *,
    boundary: str,
    operation: str,
    decision: str,
    reason: str,
) -> None:
    _assert(evidence is not None, f"{message}: evidence must be present")
    _assert(evidence.boundary == boundary, f"{message}: evidence boundary mismatch")
    _assert(evidence.operation == operation, f"{message}: evidence operation mismatch")
    _assert(evidence.decision == decision, f"{message}: evidence decision mismatch")
    _assert(evidence.reason == reason, f"{message}: evidence reason mismatch")
    _assert(not evidence.routed_to_execution, f"{message}: evidence routed_to_execution must stay false")
    _assert(not evidence.execution_authorized, f"{message}: evidence execution_authorized must stay false")
    _assert(not evidence.cleanup_required, f"{message}: evidence cleanup_required must stay false")


def _assert_no_execution(result, message: str, *, operation: str = "receive") -> None:
    _assert(not result.routed_to_execution, f"{message}: routed_to_execution must stay false")
    _assert(not result.execution_authorized, f"{message}: execution_authorized must stay false")
    _assert(not result.cleanup_required, f"{message}: cleanup_required must stay false")
    _assert(not result.accepted, f"{message}: accepted must stay false")
    _assert_evidence(
        result.evidence,
        message,
        boundary="internal_trigger_intake",
        operation=operation,
        decision=result.decision,
        reason=result.reason,
    )


def _assert_sweep_no_execution(sweep, message: str) -> None:
    _assert(not sweep.routed_to_execution, f"{message}: routed_to_execution must stay false")
    _assert(not sweep.execution_authorized, f"{message}: execution_authorized must stay false")
    _assert(not sweep.cleanup_required, f"{message}: cleanup_required must stay false")
    _assert(not sweep.accepted, f"{message}: accepted must stay false")
    for inspection in sweep.inspections:
        _assert_no_execution(inspection, message, operation="inspect_readiness")


def validate_registration_contract() -> None:
    registry = TriggerOriginRegistry()

    registered = registry.register(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "hardware-adjacent",
            "user_visible_label": "Deck Button 1",
            "enabled": True,
        }
    )
    _assert(registered.registered, "supported trigger origin should register")
    _assert(registered.reason == "registered", "supported registration should report registered")
    _assert_evidence(
        registered.evidence,
        "supported trigger registration",
        boundary="trigger_origin_registry",
        operation="register",
        decision="registered",
        reason="registered",
    )
    _assert(registered.evidence.origin_registered, "supported registration evidence should mark registered")
    _assert(registered.evidence.origin_enabled, "supported registration evidence should mark enabled")

    duplicate = registry.register(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert(not duplicate.registered, "duplicate trigger origin should reject")
    _assert(duplicate.reason == "duplicate_origin_id", "duplicate should report duplicate_origin_id")
    _assert_evidence(
        duplicate.evidence,
        "duplicate trigger registration",
        boundary="trigger_origin_registry",
        operation="register",
        decision="rejected",
        reason="duplicate_origin_id",
    )
    _assert(duplicate.evidence.origin_registered, "duplicate evidence should mark existing registration")

    blocked = registry.register(
        {
            "origin_id": "Remote Network",
            "origin_category": "remote_network",
        }
    )
    _assert(not blocked.registered, "blocked trigger origin should reject")
    _assert(blocked.reason == "blocked_origin_category", "blocked should report blocked category")
    _assert_evidence(
        blocked.evidence,
        "blocked trigger registration",
        boundary="trigger_origin_registry",
        operation="register",
        decision="rejected",
        reason="blocked_origin_category",
    )
    _assert(blocked.evidence.origin_category_blocked, "blocked evidence should mark blocked category")

    unsupported = registry.register(
        {
            "origin_id": "Unknown Trigger",
            "origin_category": "unknown_tool",
        }
    )
    _assert(not unsupported.registered, "unsupported trigger origin should reject")
    _assert(
        unsupported.reason == "unsupported_origin_category",
        "unsupported should report unsupported category",
    )
    _assert_evidence(
        unsupported.evidence,
        "unsupported trigger registration",
        boundary="trigger_origin_registry",
        operation="register",
        decision="rejected",
        reason="unsupported_origin_category",
    )

    print("PASS: trigger origin registration contract")


def validate_invocation_follow_through_contract() -> None:
    registry = TriggerOriginRegistry()
    result = registry.register(
        TriggerOriginRegistration(
            origin_id="Deck Button 1",
            origin_category="hardware_adjacent",
            user_visible_label="Deck Button 1",
            enabled=True,
        )
    )
    _assert(result.registered, "enabled origin setup should register")

    disabled_registry = TriggerOriginRegistry()
    disabled_result = disabled_registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            enabled=False,
        )
    )
    _assert(disabled_result.registered, "disabled origin setup should register")

    no_registry = InternalTriggerIntakeBoundary().receive(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert(
        no_registry.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "request without registry should defer",
    )
    _assert(
        no_registry.reason == "registration_support_not_admitted",
        "request without registry should report missing registration support",
    )
    _assert_no_execution(no_registry, "request without registry")

    boundary = InternalTriggerIntakeBoundary(origin_registry=registry)
    unregistered = boundary.receive(
        {
            "origin_id": "Unregistered Button",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert(
        unregistered.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "unregistered origin should defer",
    )
    _assert(
        unregistered.reason == "origin_not_registered",
        "unregistered origin should report origin_not_registered",
    )
    _assert_no_execution(unregistered, "unregistered origin")

    disabled = InternalTriggerIntakeBoundary(origin_registry=disabled_registry).receive(
        {
            "origin_id": "Automation A",
            "origin_category": "desktop_automation",
        }
    )
    _assert(
        disabled.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "disabled registered origin should defer",
    )
    _assert(disabled.reason == "origin_not_enabled", "disabled origin should report disabled")
    _assert(disabled.origin_registered, "disabled origin should be marked registered")
    _assert(not disabled.origin_enabled, "disabled origin should not be marked enabled")
    _assert_no_execution(disabled, "disabled origin")

    enabled = boundary.receive(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert(
        enabled.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "enabled registered origin should still defer",
    )
    _assert(
        enabled.reason == "invocation_follow_through_not_admitted",
        "enabled origin should stop at follow-through boundary",
    )
    _assert(enabled.origin_registered, "enabled origin should be marked registered")
    _assert(enabled.origin_enabled, "enabled origin should be marked enabled")
    _assert_no_execution(enabled, "enabled registered origin")

    mismatch = boundary.receive(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "desktop_automation",
        }
    )
    _assert(
        mismatch.decision == TRIGGER_INTAKE_DECISION_REJECTED,
        "registration mismatch should reject",
    )
    _assert(
        mismatch.reason == "origin_registration_mismatch",
        "registration mismatch should report mismatch",
    )
    _assert(mismatch.origin_registered, "mismatch should identify known registration")
    _assert(mismatch.origin_enabled, "mismatch should preserve registration enabled state")
    _assert_no_execution(mismatch, "registration mismatch")

    print("PASS: trigger invocation follow-through contract")


def validate_lifecycle_state_transition_contract() -> None:
    registry = TriggerOriginRegistry()
    registration_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            user_visible_label="Automation A",
            enabled=False,
        )
    )
    _assert(registration_result.registered, "lifecycle setup should register disabled origin")

    boundary = InternalTriggerIntakeBoundary(origin_registry=registry)
    disabled = boundary.receive(
        {
            "origin_id": "Automation A",
            "origin_category": "desktop_automation",
        }
    )
    _assert(
        disabled.reason == "origin_not_enabled",
        "disabled registered origin should defer before enable",
    )
    _assert(disabled.origin_registered, "disabled origin should be marked registered")
    _assert(not disabled.origin_enabled, "disabled origin should not be marked enabled")
    _assert_no_execution(disabled, "disabled lifecycle origin")

    enabled_result = registry.enable(" Automation A ")
    _assert(enabled_result.changed, "enable should change disabled origin state")
    _assert(enabled_result.origin_found, "enable should find origin")
    _assert(enabled_result.reason == "enabled", "enable should report enabled")
    _assert_evidence(
        enabled_result.evidence,
        "enable lifecycle transition",
        boundary="trigger_origin_registry",
        operation="enable",
        decision="changed",
        reason="enabled",
    )
    _assert(enabled_result.evidence.origin_enabled, "enable evidence should mark enabled")

    enabled = boundary.receive(
        {
            "origin_id": "Automation A",
            "origin_category": "desktop_automation",
        }
    )
    _assert(
        enabled.reason == "invocation_follow_through_not_admitted",
        "enabled origin should stop at follow-through boundary",
    )
    _assert(enabled.origin_registered, "enabled origin should be marked registered")
    _assert(enabled.origin_enabled, "enabled origin should be marked enabled")
    _assert_no_execution(enabled, "enabled lifecycle origin")

    already_enabled = registry.enable("Automation A")
    _assert(not already_enabled.changed, "repeated enable should be a no-op")
    _assert(already_enabled.reason == "already_enabled", "repeated enable should report no-op")
    _assert_evidence(
        already_enabled.evidence,
        "repeated enable lifecycle transition",
        boundary="trigger_origin_registry",
        operation="enable",
        decision="unchanged",
        reason="already_enabled",
    )

    disabled_result = registry.disable("Automation A")
    _assert(disabled_result.changed, "disable should change enabled origin state")
    _assert(disabled_result.reason == "disabled", "disable should report disabled")
    _assert_evidence(
        disabled_result.evidence,
        "disable lifecycle transition",
        boundary="trigger_origin_registry",
        operation="disable",
        decision="changed",
        reason="disabled",
    )
    _assert(not disabled_result.evidence.origin_enabled, "disable evidence should mark disabled")

    redisabled = boundary.receive(
        {
            "origin_id": "Automation A",
            "origin_category": "desktop_automation",
        }
    )
    _assert(
        redisabled.reason == "origin_not_enabled",
        "disabled origin should return to origin_not_enabled",
    )
    _assert(redisabled.origin_registered, "re-disabled origin should be marked registered")
    _assert(not redisabled.origin_enabled, "re-disabled origin should not be marked enabled")
    _assert_no_execution(redisabled, "re-disabled lifecycle origin")

    already_disabled = registry.disable("Automation A")
    _assert(not already_disabled.changed, "repeated disable should be a no-op")
    _assert(already_disabled.reason == "already_disabled", "repeated disable should report no-op")
    _assert_evidence(
        already_disabled.evidence,
        "repeated disable lifecycle transition",
        boundary="trigger_origin_registry",
        operation="disable",
        decision="unchanged",
        reason="already_disabled",
    )

    unregistered = registry.unregister("Automation A")
    _assert(unregistered.changed, "unregister should remove registered origin")
    _assert(unregistered.origin_found, "unregister should find registered origin")
    _assert(unregistered.reason == "unregistered", "unregister should report unregistered")
    _assert_evidence(
        unregistered.evidence,
        "unregister lifecycle transition",
        boundary="trigger_origin_registry",
        operation="unregister",
        decision="changed",
        reason="unregistered",
    )

    after_teardown = boundary.receive(
        {
            "origin_id": "Automation A",
            "origin_category": "desktop_automation",
        }
    )
    _assert(
        after_teardown.reason == "origin_not_registered",
        "unregistered origin should defer as not registered",
    )
    _assert(not after_teardown.origin_registered, "unregistered origin should not be marked registered")
    _assert_no_execution(after_teardown, "unregistered lifecycle origin")

    missing = registry.unregister("Automation A")
    _assert(not missing.changed, "missing unregister should be a no-op")
    _assert(missing.reason == "origin_not_registered", "missing unregister should report not registered")
    _assert_evidence(
        missing.evidence,
        "missing unregister lifecycle transition",
        boundary="trigger_origin_registry",
        operation="unregister",
        decision="unchanged",
        reason="origin_not_registered",
    )

    invalid = registry.enable("   ")
    _assert(not invalid.changed, "blank origin enable should be a no-op")
    _assert(invalid.reason == "invalid_origin_id", "blank origin enable should report invalid id")
    _assert_evidence(
        invalid.evidence,
        "invalid enable lifecycle transition",
        boundary="trigger_origin_registry",
        operation="enable",
        decision="unchanged",
        reason="invalid_origin_id",
    )

    print("PASS: trigger origin lifecycle state transition contract")


def validate_state_snapshot_contract() -> None:
    registry = TriggerOriginRegistry()
    empty_snapshot = registry.snapshot()
    _assert(empty_snapshot.boundary == "trigger_origin_registry", "empty snapshot should identify registry boundary")
    _assert(empty_snapshot.registrations == (), "empty snapshot should expose empty registration tuple")
    _assert(empty_snapshot.registered_count == 0, "empty snapshot should report zero registrations")
    _assert(empty_snapshot.enabled_count == 0, "empty snapshot should report zero enabled origins")

    deck_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Deck Button 1",
            origin_category="hardware_adjacent",
            user_visible_label="Deck Button 1",
            enabled=True,
        )
    )
    _assert(deck_result.registered, "snapshot setup should register enabled origin")
    automation_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            user_visible_label="Automation A",
            enabled=False,
        )
    )
    _assert(automation_result.registered, "snapshot setup should register disabled origin")

    populated_snapshot = registry.snapshot()
    _assert(populated_snapshot.registered_count == 2, "populated snapshot should report registrations")
    _assert(populated_snapshot.enabled_count == 1, "populated snapshot should count enabled origins")
    _assert(
        tuple(registration.origin_id for registration in populated_snapshot.registrations)
        == ("Automation A", "Deck Button 1"),
        "snapshot registrations should be deterministic by origin id",
    )

    boundary_snapshot = InternalTriggerIntakeBoundary(origin_registry=registry).snapshot()
    _assert(
        boundary_snapshot.boundary == "internal_trigger_intake",
        "boundary snapshot should identify intake boundary",
    )
    _assert(
        boundary_snapshot.registration_support_admitted,
        "boundary snapshot should report registry support",
    )
    _assert(
        boundary_snapshot.registry_snapshot == populated_snapshot,
        "boundary snapshot should include current registry snapshot",
    )
    _assert(
        "hardware_adjacent" in boundary_snapshot.known_origin_categories,
        "boundary snapshot should expose known origin categories",
    )
    _assert(
        "remote_network" in boundary_snapshot.blocked_origin_categories,
        "boundary snapshot should expose blocked origin categories",
    )

    no_registry_snapshot = InternalTriggerIntakeBoundary().snapshot()
    _assert(
        not no_registry_snapshot.registration_support_admitted,
        "boundary snapshot without registry should report no registration support",
    )
    _assert(
        no_registry_snapshot.registry_snapshot is None,
        "boundary snapshot without registry should not synthesize registry state",
    )

    unregistered = registry.unregister("Automation A")
    _assert(unregistered.changed, "snapshot cleanup setup should unregister origin")
    after_cleanup = registry.snapshot()
    _assert(after_cleanup.registered_count == 1, "cleanup snapshot should report removed origin")
    _assert(populated_snapshot.registered_count == 2, "prior snapshot should remain immutable history")

    try:
        populated_snapshot.registered_count = 99
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("registry snapshot should be immutable")

    boundary = InternalTriggerIntakeBoundary(origin_registry=registry)
    enabled = boundary.receive(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert_no_execution(enabled, "snapshot boundary enabled origin")

    print("PASS: trigger boundary state snapshot contract")


def validate_readiness_inspection_contract() -> None:
    registry = TriggerOriginRegistry()
    enabled_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Deck Button 1",
            origin_category="hardware_adjacent",
            user_visible_label="Deck Button 1",
            enabled=True,
        )
    )
    _assert(enabled_result.registered, "readiness setup should register enabled origin")
    disabled_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            user_visible_label="Automation A",
            enabled=False,
        )
    )
    _assert(disabled_result.registered, "readiness setup should register disabled origin")

    no_registry = InternalTriggerIntakeBoundary().inspect_readiness(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert(
        no_registry.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "readiness without registry should defer",
    )
    _assert(
        no_registry.reason == "registration_support_not_admitted",
        "readiness without registry should report missing registration support",
    )
    _assert(
        not no_registry.registration_support_admitted,
        "readiness without registry should not mark support admitted",
    )
    _assert(
        no_registry.boundary_snapshot is not None,
        "readiness without registry should include boundary snapshot",
    )
    _assert(
        not no_registry.boundary_snapshot.registration_support_admitted,
        "readiness snapshot without registry should show no registration support",
    )
    _assert_no_execution(no_registry, "readiness without registry", operation="inspect_readiness")

    boundary = InternalTriggerIntakeBoundary(origin_registry=registry)
    before_snapshot = registry.snapshot()
    unregistered = boundary.inspect_readiness(
        {
            "origin_id": "Unregistered Button",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert(
        unregistered.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "unregistered readiness should defer",
    )
    _assert(
        unregistered.reason == "origin_not_registered",
        "unregistered readiness should report origin_not_registered",
    )
    _assert(unregistered.origin_category_known, "unregistered readiness should mark known category")
    _assert(
        unregistered.registration_support_admitted,
        "unregistered readiness should mark support admitted",
    )
    _assert_no_execution(unregistered, "unregistered readiness", operation="inspect_readiness")

    disabled = boundary.inspect_readiness(
        {
            "origin_id": "Automation A",
            "origin_category": "desktop_automation",
        }
    )
    _assert(
        disabled.reason == "origin_not_enabled",
        "disabled readiness should report origin_not_enabled",
    )
    _assert(disabled.origin_registered, "disabled readiness should mark registered")
    _assert(not disabled.origin_enabled, "disabled readiness should not mark enabled")
    _assert_no_execution(disabled, "disabled readiness", operation="inspect_readiness")

    enabled = boundary.inspect_readiness(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert(
        enabled.reason == "invocation_follow_through_not_admitted",
        "enabled readiness should stop at follow-through boundary",
    )
    _assert(enabled.origin_registered, "enabled readiness should mark registered")
    _assert(enabled.origin_enabled, "enabled readiness should mark enabled")
    _assert(
        enabled.boundary_snapshot.registry_snapshot == before_snapshot,
        "enabled readiness should include current immutable registry snapshot",
    )
    _assert_no_execution(enabled, "enabled readiness", operation="inspect_readiness")

    mismatch = boundary.inspect_readiness(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "desktop_automation",
        }
    )
    _assert(
        mismatch.decision == TRIGGER_INTAKE_DECISION_REJECTED,
        "readiness category mismatch should reject",
    )
    _assert(
        mismatch.reason == "origin_registration_mismatch",
        "readiness category mismatch should report mismatch",
    )
    _assert(mismatch.origin_registered, "mismatch readiness should mark registered")
    _assert(mismatch.origin_enabled, "mismatch readiness should preserve enabled state")
    _assert_no_execution(mismatch, "mismatch readiness", operation="inspect_readiness")

    blocked = boundary.inspect_readiness(
        {
            "origin_id": "Remote Network",
            "origin_category": "remote_network",
        }
    )
    _assert(
        blocked.decision == TRIGGER_INTAKE_DECISION_REJECTED,
        "blocked readiness should reject",
    )
    _assert(
        blocked.reason == "blocked_origin_category",
        "blocked readiness should report blocked category",
    )
    _assert(blocked.origin_category_blocked, "blocked readiness should mark blocked category")
    _assert_no_execution(blocked, "blocked readiness", operation="inspect_readiness")

    unsupported = boundary.inspect_readiness(
        {
            "origin_id": "Unsupported",
            "origin_category": "unknown_tool",
        }
    )
    _assert(
        unsupported.reason == "unsupported_origin_category",
        "unsupported readiness should report unsupported category",
    )
    _assert_no_execution(unsupported, "unsupported readiness", operation="inspect_readiness")

    after_snapshot = registry.snapshot()
    _assert(after_snapshot == before_snapshot, "readiness inspection should not mutate registry state")

    try:
        enabled.boundary_snapshot.boundary = "changed"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("readiness boundary snapshot should be immutable")

    print("PASS: trigger readiness inspection contract")


def validate_registry_readiness_sweep_contract() -> None:
    empty_sweep = InternalTriggerIntakeBoundary().inspect_registry_readiness()
    _assert(
        empty_sweep.boundary == "internal_trigger_registry_readiness_sweep",
        "empty sweep should identify registry readiness boundary",
    )
    _assert(empty_sweep.inspections == (), "empty sweep should expose empty inspection tuple")
    _assert(empty_sweep.inspected_count == 0, "empty sweep should report zero inspections")
    _assert(empty_sweep.deferred_count == 0, "empty sweep should report zero deferred")
    _assert(empty_sweep.rejected_count == 0, "empty sweep should report zero rejected")
    _assert(
        empty_sweep.boundary_snapshot is not None,
        "empty sweep should include boundary snapshot",
    )
    _assert(
        not empty_sweep.boundary_snapshot.registration_support_admitted,
        "empty sweep without registry should report no registration support",
    )
    _assert_sweep_no_execution(empty_sweep, "empty registry readiness sweep")

    registry = TriggerOriginRegistry()
    deck_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Deck Button 1",
            origin_category="hardware_adjacent",
            user_visible_label="Deck Button 1",
            enabled=True,
        )
    )
    _assert(deck_result.registered, "sweep setup should register enabled origin")
    automation_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            user_visible_label="Automation A",
            enabled=False,
        )
    )
    _assert(automation_result.registered, "sweep setup should register disabled origin")

    boundary = InternalTriggerIntakeBoundary(origin_registry=registry)
    before_snapshot = registry.snapshot()
    sweep = boundary.inspect_registry_readiness()
    _assert(sweep.inspected_count == 2, "sweep should inspect registered origins")
    _assert(sweep.deferred_count == 2, "sweep should defer all current registered origins")
    _assert(sweep.rejected_count == 0, "sweep should not reject matching current registrations")
    _assert(sweep.enabled_count == 1, "sweep should count enabled origin readiness")
    _assert(sweep.disabled_count == 1, "sweep should count disabled origin readiness")
    _assert(
        tuple(inspection.request.origin_id for inspection in sweep.inspections)
        == ("Automation A", "Deck Button 1"),
        "sweep should follow deterministic registry snapshot order",
    )
    _assert(
        tuple(inspection.reason for inspection in sweep.inspections)
        == ("origin_not_enabled", "invocation_follow_through_not_admitted"),
        "sweep should preserve readiness reasons",
    )
    _assert(
        sweep.boundary_snapshot.registry_snapshot == before_snapshot,
        "sweep should include current registry snapshot",
    )
    _assert_sweep_no_execution(sweep, "populated registry readiness sweep")
    _assert(registry.snapshot() == before_snapshot, "sweep should not mutate registry state")

    custom_registry = TriggerOriginRegistry(known_origin_categories=("custom_local",))
    custom_result = custom_registry.register(
        TriggerOriginRegistration(
            origin_id="Custom Trigger",
            origin_category="custom_local",
            enabled=True,
        )
    )
    _assert(custom_result.registered, "custom sweep setup should register custom origin")
    rejected_sweep = InternalTriggerIntakeBoundary(origin_registry=custom_registry).inspect_registry_readiness()
    _assert(rejected_sweep.inspected_count == 1, "custom sweep should inspect custom origin")
    _assert(rejected_sweep.rejected_count == 1, "custom sweep should count unsupported boundary rejection")
    _assert(
        rejected_sweep.inspections[0].reason == "unsupported_origin_category",
        "custom sweep should preserve unsupported readiness reason",
    )
    _assert_sweep_no_execution(rejected_sweep, "rejected registry readiness sweep")

    try:
        sweep.inspected_count = 99
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("registry readiness sweep should be immutable")

    print("PASS: trigger registry readiness sweep contract")


def main() -> int:
    validate_registration_contract()
    validate_invocation_follow_through_contract()
    validate_lifecycle_state_transition_contract()
    validate_state_snapshot_contract()
    validate_readiness_inspection_contract()
    validate_registry_readiness_sweep_contract()
    print("EXTERNAL TRIGGER INTAKE VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
