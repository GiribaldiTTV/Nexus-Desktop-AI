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


def _assert_no_execution(result, message: str) -> None:
    _assert(not result.routed_to_execution, f"{message}: routed_to_execution must stay false")
    _assert(not result.execution_authorized, f"{message}: execution_authorized must stay false")
    _assert(not result.cleanup_required, f"{message}: cleanup_required must stay false")
    _assert(not result.accepted, f"{message}: accepted must stay false")
    _assert_evidence(
        result.evidence,
        message,
        boundary="internal_trigger_intake",
        operation="receive",
        decision=result.decision,
        reason=result.reason,
    )


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


def main() -> int:
    validate_registration_contract()
    validate_invocation_follow_through_contract()
    validate_lifecycle_state_transition_contract()
    print("EXTERNAL TRIGGER INTAKE VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
