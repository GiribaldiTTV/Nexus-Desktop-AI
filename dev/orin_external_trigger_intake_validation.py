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
    normalize_trigger_origin_category,
    normalize_trigger_origin_id,
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


def _assert_summary_no_execution(summary, message: str) -> None:
    _assert(not summary.routed_to_execution, f"{message}: routed_to_execution must stay false")
    _assert(not summary.execution_authorized, f"{message}: execution_authorized must stay false")
    _assert(not summary.cleanup_required, f"{message}: cleanup_required must stay false")
    _assert(not summary.accepted, f"{message}: accepted must stay false")
    _assert_evidence(
        summary.evidence,
        message,
        boundary="internal_trigger_registry_readiness_summary",
        operation="summarize_registry_readiness",
        decision=summary.decision,
        reason=summary.reason,
    )
    _assert_sweep_no_execution(summary.sweep, message)


def _assert_detail_no_execution(detail, message: str) -> None:
    _assert(not detail.routed_to_execution, f"{message}: detail routed_to_execution must stay false")
    _assert(not detail.execution_authorized, f"{message}: detail execution_authorized must stay false")
    _assert(not detail.cleanup_required, f"{message}: detail cleanup_required must stay false")
    _assert(not detail.accepted, f"{message}: detail accepted must stay false")


def _assert_detail_snapshot_no_execution(snapshot, message: str) -> None:
    _assert(not snapshot.routed_to_execution, f"{message}: routed_to_execution must stay false")
    _assert(not snapshot.execution_authorized, f"{message}: execution_authorized must stay false")
    _assert(not snapshot.cleanup_required, f"{message}: cleanup_required must stay false")
    _assert(not snapshot.accepted, f"{message}: accepted must stay false")
    _assert_summary_no_execution(snapshot.summary, message)
    for detail in snapshot.details:
        _assert_detail_no_execution(detail, message)


def validate_hardened_normalization_and_malformed_input_contract() -> None:
    _assert(
        normalize_trigger_origin_category(" Hardware Adjacent!! ") == "hardware_adjacent",
        "category normalization should produce canonical snake case",
    )
    _assert(
        normalize_trigger_origin_id(" Deck\tButton\n1 ") == "Deck Button 1",
        "origin id normalization should trim and collapse whitespace",
    )

    registry = TriggerOriginRegistry()
    before_snapshot = registry.snapshot()

    invalid_id = registry.register(
        {
            "origin_id": "   ",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert(not invalid_id.registered, "blank origin id registration should reject")
    _assert(invalid_id.reason == "invalid_origin_id", "blank origin id should report invalid id")
    _assert_evidence(
        invalid_id.evidence,
        "blank origin id registration",
        boundary="trigger_origin_registry",
        operation="register",
        decision="rejected",
        reason="invalid_origin_id",
    )
    _assert(registry.snapshot() == before_snapshot, "blank origin id should not mutate registry")

    invalid_category = registry.register(
        {
            "origin_id": "Deck Button 2",
            "origin_category": "   ",
        }
    )
    _assert(not invalid_category.registered, "blank category registration should reject")
    _assert(
        invalid_category.reason == "invalid_origin_category",
        "blank category should report invalid category",
    )
    _assert_evidence(
        invalid_category.evidence,
        "blank category registration",
        boundary="trigger_origin_registry",
        operation="register",
        decision="rejected",
        reason="invalid_origin_category",
    )
    _assert(registry.snapshot() == before_snapshot, "blank category should not mutate registry")

    boundary = InternalTriggerIntakeBoundary(origin_registry=registry)
    missing_id = boundary.receive({"origin_category": "hardware_adjacent"})
    _assert(missing_id.reason == "invalid_origin_id", "missing origin id intake should reject")
    _assert_no_execution(missing_id, "missing origin id intake")
    _assert(registry.snapshot() == before_snapshot, "missing origin id intake should not mutate registry")

    missing_category = boundary.inspect_readiness({"origin_id": "Deck Button 2"})
    _assert(
        missing_category.reason == "invalid_origin_category",
        "missing category readiness should reject",
    )
    _assert_no_execution(missing_category, "missing category readiness", operation="inspect_readiness")
    _assert(registry.snapshot() == before_snapshot, "missing category readiness should not mutate registry")

    try:
        registry.register(object())
    except TypeError:
        pass
    else:
        raise AssertionError("unsupported registration object should raise TypeError")
    _assert(registry.snapshot() == before_snapshot, "unsupported registration object should not mutate registry")

    try:
        boundary.receive(object())
    except TypeError:
        pass
    else:
        raise AssertionError("unsupported intake object should raise TypeError")
    _assert(registry.snapshot() == before_snapshot, "unsupported intake object should not mutate registry")

    print("PASS: hardened normalization and malformed input contract")


def validate_blocked_category_precedence_contract() -> None:
    registry = TriggerOriginRegistry(
        known_origin_categories=("hardware_adjacent", "remote_network"),
        blocked_origin_categories=("remote_network",),
    )
    before_snapshot = registry.snapshot()
    blocked_registration = registry.register(
        {
            "origin_id": "Remote Trigger",
            "origin_category": "remote_network",
            "enabled": True,
        }
    )
    _assert(not blocked_registration.registered, "blocked category should reject even when known")
    _assert(
        blocked_registration.reason == "blocked_origin_category",
        "blocked category should win over known-category admission",
    )
    _assert(blocked_registration.evidence.origin_category_blocked, "blocked evidence should mark blocked")
    _assert_evidence(
        blocked_registration.evidence,
        "known-but-blocked registration",
        boundary="trigger_origin_registry",
        operation="register",
        decision="rejected",
        reason="blocked_origin_category",
    )
    _assert(registry.snapshot() == before_snapshot, "blocked registration should not mutate registry")

    boundary = InternalTriggerIntakeBoundary(
        known_origin_categories=("remote_network",),
        blocked_origin_categories=("remote_network",),
        origin_registry=registry,
    )
    blocked_intake = boundary.receive(
        {
            "origin_id": "Remote Trigger",
            "origin_category": "remote_network",
        }
    )
    _assert(blocked_intake.reason == "blocked_origin_category", "blocked intake should reject")
    _assert(blocked_intake.origin_category_blocked, "blocked intake should mark blocked category")
    _assert_no_execution(blocked_intake, "known-but-blocked intake")
    _assert(registry.snapshot() == before_snapshot, "blocked intake should not mutate registry")

    blocked_readiness = boundary.inspect_readiness(
        {
            "origin_id": "Remote Trigger",
            "origin_category": "remote_network",
        }
    )
    _assert(blocked_readiness.reason == "blocked_origin_category", "blocked readiness should reject")
    _assert(blocked_readiness.origin_category_blocked, "blocked readiness should mark blocked category")
    _assert_no_execution(
        blocked_readiness,
        "known-but-blocked readiness",
        operation="inspect_readiness",
    )
    _assert(registry.snapshot() == before_snapshot, "blocked readiness should not mutate registry")

    print("PASS: blocked category precedence contract")


def validate_duplicate_and_result_immutability_contract() -> None:
    registry = TriggerOriginRegistry()
    registered = registry.register(
        TriggerOriginRegistration(
            origin_id="Deck Button 1",
            origin_category="hardware_adjacent",
            user_visible_label="Deck Button 1",
            enabled=True,
        )
    )
    _assert(registered.registered, "immutability setup should register enabled origin")
    before_snapshot = registry.snapshot()
    duplicate = registry.register(
        {
            "origin_id": " deck   button 1 ",
            "origin_category": "hardware-adjacent",
        }
    )
    _assert(not duplicate.registered, "normalized duplicate should reject")
    _assert(duplicate.reason == "duplicate_origin_id", "normalized duplicate should report duplicate id")
    _assert(duplicate.evidence.origin_registered, "duplicate evidence should mark existing registration")
    _assert_evidence(
        duplicate.evidence,
        "normalized duplicate registration",
        boundary="trigger_origin_registry",
        operation="register",
        decision="rejected",
        reason="duplicate_origin_id",
    )
    _assert(registry.snapshot() == before_snapshot, "duplicate registration should not mutate registry")

    boundary = InternalTriggerIntakeBoundary(origin_registry=registry)
    intake = boundary.receive(
        {
            "origin_id": "Deck Button 1",
            "origin_category": "hardware_adjacent",
        }
    )
    _assert_no_execution(intake, "immutability intake")

    try:
        duplicate.reason = "changed"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("registration result should be immutable")

    try:
        intake.reason = "changed"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("intake result should be immutable")

    try:
        intake.evidence.reason = "changed"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("intake evidence should be immutable")

    print("PASS: duplicate registration and result immutability contract")


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


def validate_registry_readiness_summary_contract() -> None:
    no_registry_summary = InternalTriggerIntakeBoundary().summarize_registry_readiness()
    _assert(
        no_registry_summary.boundary == "internal_trigger_registry_readiness_summary",
        "no-registry summary should identify registry readiness summary boundary",
    )
    _assert(
        no_registry_summary.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "no-registry summary should defer",
    )
    _assert(
        no_registry_summary.reason == "registration_support_not_admitted",
        "no-registry summary should report missing registration support",
    )
    _assert(no_registry_summary.inspected_count == 0, "no-registry summary should report zero inspections")
    _assert(
        not no_registry_summary.sweep.boundary_snapshot.registration_support_admitted,
        "no-registry summary should preserve missing registration support snapshot",
    )
    _assert_summary_no_execution(no_registry_summary, "no-registry readiness summary")

    empty_registry_summary = InternalTriggerIntakeBoundary(
        origin_registry=TriggerOriginRegistry()
    ).summarize_registry_readiness()
    _assert(
        empty_registry_summary.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "empty-registry summary should defer",
    )
    _assert(
        empty_registry_summary.reason == "no_registered_origins",
        "empty-registry summary should report no registered origins",
    )
    _assert(empty_registry_summary.inspected_count == 0, "empty-registry summary should inspect zero origins")
    _assert(
        empty_registry_summary.sweep.boundary_snapshot.registration_support_admitted,
        "empty-registry summary should preserve registration support snapshot",
    )
    _assert_summary_no_execution(empty_registry_summary, "empty-registry readiness summary")

    disabled_registry = TriggerOriginRegistry()
    disabled_result = disabled_registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            user_visible_label="Automation A",
            enabled=False,
        )
    )
    _assert(disabled_result.registered, "disabled summary setup should register disabled origin")
    disabled_snapshot = disabled_registry.snapshot()
    disabled_summary = InternalTriggerIntakeBoundary(
        origin_registry=disabled_registry
    ).summarize_registry_readiness()
    _assert(
        disabled_summary.decision == TRIGGER_INTAKE_DECISION_DEFERRED,
        "disabled-only summary should defer",
    )
    _assert(
        disabled_summary.reason == "no_enabled_origins",
        "disabled-only summary should report no enabled origins",
    )
    _assert(disabled_summary.inspected_count == 1, "disabled-only summary should inspect origin")
    _assert(disabled_summary.deferred_count == 1, "disabled-only summary should count deferred origin")
    _assert(disabled_summary.enabled_count == 0, "disabled-only summary should count zero enabled origins")
    _assert(disabled_summary.disabled_count == 1, "disabled-only summary should count disabled origin")
    _assert(disabled_registry.snapshot() == disabled_snapshot, "disabled-only summary should not mutate registry")
    _assert_summary_no_execution(disabled_summary, "disabled-only readiness summary")

    registry = TriggerOriginRegistry()
    deck_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Deck Button 1",
            origin_category="hardware_adjacent",
            user_visible_label="Deck Button 1",
            enabled=True,
        )
    )
    _assert(deck_result.registered, "summary setup should register enabled origin")
    automation_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            user_visible_label="Automation A",
            enabled=False,
        )
    )
    _assert(automation_result.registered, "summary setup should register disabled origin")
    before_snapshot = registry.snapshot()
    summary = InternalTriggerIntakeBoundary(origin_registry=registry).summarize_registry_readiness()
    _assert(summary.decision == TRIGGER_INTAKE_DECISION_DEFERRED, "populated summary should defer")
    _assert(
        summary.reason == "invocation_follow_through_not_admitted",
        "populated summary should stop at follow-through boundary",
    )
    _assert(summary.inspected_count == 2, "populated summary should mirror inspected count")
    _assert(summary.deferred_count == 2, "populated summary should mirror deferred count")
    _assert(summary.rejected_count == 0, "populated summary should mirror rejected count")
    _assert(summary.enabled_count == 1, "populated summary should mirror enabled count")
    _assert(summary.disabled_count == 1, "populated summary should mirror disabled count")
    _assert(
        tuple(inspection.request.origin_id for inspection in summary.sweep.inspections)
        == ("Automation A", "Deck Button 1"),
        "populated summary should preserve deterministic sweep order",
    )
    _assert(registry.snapshot() == before_snapshot, "populated summary should not mutate registry")
    _assert_summary_no_execution(summary, "populated readiness summary")

    custom_registry = TriggerOriginRegistry(known_origin_categories=("custom_local",))
    custom_result = custom_registry.register(
        TriggerOriginRegistration(
            origin_id="Custom Trigger",
            origin_category="custom_local",
            enabled=True,
        )
    )
    _assert(custom_result.registered, "rejected summary setup should register custom origin")
    rejected_summary = InternalTriggerIntakeBoundary(
        origin_registry=custom_registry
    ).summarize_registry_readiness()
    _assert(
        rejected_summary.decision == TRIGGER_INTAKE_DECISION_REJECTED,
        "rejected summary should reject when sweep contains readiness rejections",
    )
    _assert(
        rejected_summary.reason == "readiness_rejections_present",
        "rejected summary should report sweep rejection presence",
    )
    _assert(rejected_summary.rejected_count == 1, "rejected summary should mirror rejected count")
    _assert_summary_no_execution(rejected_summary, "rejected readiness summary")

    try:
        summary.reason = "changed"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("registry readiness summary should be immutable")

    print("PASS: trigger registry readiness summary contract")


def validate_registry_readiness_detail_snapshot_contract() -> None:
    no_registry_details = InternalTriggerIntakeBoundary().inspect_registry_readiness_details()
    _assert(
        no_registry_details.boundary == "internal_trigger_registry_readiness_details",
        "no-registry details should identify registry readiness details boundary",
    )
    _assert(
        no_registry_details.summary.reason == "registration_support_not_admitted",
        "no-registry details should preserve missing registration support summary",
    )
    _assert(no_registry_details.details == (), "no-registry details should expose empty detail tuple")
    _assert(no_registry_details.detailed_count == 0, "no-registry details should report zero details")
    _assert_detail_snapshot_no_execution(no_registry_details, "no-registry readiness details")

    empty_registry_details = InternalTriggerIntakeBoundary(
        origin_registry=TriggerOriginRegistry()
    ).inspect_registry_readiness_details()
    _assert(
        empty_registry_details.summary.reason == "no_registered_origins",
        "empty-registry details should preserve empty-registry summary",
    )
    _assert(empty_registry_details.details == (), "empty-registry details should expose empty detail tuple")
    _assert(empty_registry_details.detailed_count == 0, "empty-registry details should report zero details")
    _assert_detail_snapshot_no_execution(empty_registry_details, "empty-registry readiness details")

    disabled_registry = TriggerOriginRegistry()
    disabled_result = disabled_registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            user_visible_label="Automation A",
            enabled=False,
        )
    )
    _assert(disabled_result.registered, "disabled details setup should register disabled origin")
    disabled_snapshot = disabled_registry.snapshot()
    disabled_details = InternalTriggerIntakeBoundary(
        origin_registry=disabled_registry
    ).inspect_registry_readiness_details()
    _assert(
        disabled_details.summary.reason == "no_enabled_origins",
        "disabled-only details should preserve no-enabled summary",
    )
    _assert(disabled_details.detailed_count == 1, "disabled-only details should report one detail")
    _assert(disabled_details.details[0].origin_id == "Automation A", "disabled detail should preserve origin id")
    _assert(
        disabled_details.details[0].reason == "origin_not_enabled",
        "disabled detail should preserve readiness reason",
    )
    _assert(disabled_details.details[0].origin_registered, "disabled detail should mark registered")
    _assert(not disabled_details.details[0].origin_enabled, "disabled detail should not mark enabled")
    _assert(disabled_registry.snapshot() == disabled_snapshot, "disabled details should not mutate registry")
    _assert_detail_snapshot_no_execution(disabled_details, "disabled-only readiness details")

    registry = TriggerOriginRegistry()
    deck_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Deck Button 1",
            origin_category="hardware_adjacent",
            user_visible_label="Deck Button 1",
            enabled=True,
        )
    )
    _assert(deck_result.registered, "details setup should register enabled origin")
    automation_result = registry.register(
        TriggerOriginRegistration(
            origin_id="Automation A",
            origin_category="desktop_automation",
            user_visible_label="Automation A",
            enabled=False,
        )
    )
    _assert(automation_result.registered, "details setup should register disabled origin")
    before_snapshot = registry.snapshot()
    details = InternalTriggerIntakeBoundary(origin_registry=registry).inspect_registry_readiness_details()
    _assert(details.summary.reason == "invocation_follow_through_not_admitted", "details should preserve summary")
    _assert(details.detailed_count == 2, "details should report registered origin details")
    _assert(
        tuple(detail.origin_id for detail in details.details)
        == ("Automation A", "Deck Button 1"),
        "details should follow deterministic registry snapshot order",
    )
    _assert(
        tuple(detail.reason for detail in details.details)
        == ("origin_not_enabled", "invocation_follow_through_not_admitted"),
        "details should preserve readiness reasons",
    )
    _assert(
        tuple(detail.origin_enabled for detail in details.details) == (False, True),
        "details should preserve enablement state",
    )
    _assert(details.summary.sweep.inspected_count == details.detailed_count, "details should mirror sweep count")
    _assert(registry.snapshot() == before_snapshot, "details should not mutate registry state")
    _assert_detail_snapshot_no_execution(details, "populated readiness details")

    custom_registry = TriggerOriginRegistry(known_origin_categories=("custom_local",))
    custom_result = custom_registry.register(
        TriggerOriginRegistration(
            origin_id="Custom Trigger",
            origin_category="custom_local",
            user_visible_label="Custom Trigger",
            enabled=True,
        )
    )
    _assert(custom_result.registered, "rejected details setup should register custom origin")
    rejected_details = InternalTriggerIntakeBoundary(
        origin_registry=custom_registry
    ).inspect_registry_readiness_details()
    _assert(
        rejected_details.summary.decision == TRIGGER_INTAKE_DECISION_REJECTED,
        "rejected details should reject when summary rejects",
    )
    _assert(rejected_details.detailed_count == 1, "rejected details should report one detail")
    _assert(
        rejected_details.details[0].reason == "unsupported_origin_category",
        "rejected detail should preserve unsupported readiness reason",
    )
    _assert_detail_snapshot_no_execution(rejected_details, "rejected readiness details")

    try:
        details.detailed_count = 99
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("registry readiness detail snapshot should be immutable")

    try:
        details.details[0].reason = "changed"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("registry readiness detail row should be immutable")

    print("PASS: trigger registry readiness detail snapshot contract")


def main() -> int:
    validate_hardened_normalization_and_malformed_input_contract()
    validate_blocked_category_precedence_contract()
    validate_duplicate_and_result_immutability_contract()
    validate_registration_contract()
    validate_invocation_follow_through_contract()
    validate_lifecycle_state_transition_contract()
    validate_state_snapshot_contract()
    validate_readiness_inspection_contract()
    validate_registry_readiness_sweep_contract()
    validate_registry_readiness_summary_contract()
    validate_registry_readiness_detail_snapshot_contract()
    print("EXTERNAL TRIGGER INTAKE VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
