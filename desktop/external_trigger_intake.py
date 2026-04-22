from dataclasses import dataclass, replace
import re
from typing import Iterable


KNOWN_TRIGGER_ORIGIN_CATEGORIES = frozenset(
    {
        "hardware_adjacent",
        "desktop_automation",
        "local_companion_app",
        "future_plugin_hosted",
    }
)
BLOCKED_TRIGGER_ORIGIN_CATEGORIES = frozenset(
    {
        "remote_network",
        "cloud_webhook",
        "untrusted_web_page",
        "arbitrary_script",
        "silent_background",
    }
)

TRIGGER_INTAKE_DECISION_DEFERRED = "deferred"
TRIGGER_INTAKE_DECISION_REJECTED = "rejected"


@dataclass(frozen=True)
class TriggerDecisionEvidence:
    boundary: str
    operation: str
    origin_id: str = ""
    origin_category: str = ""
    decision: str = ""
    reason: str = ""
    origin_category_known: bool = False
    origin_category_blocked: bool = False
    origin_registered: bool = False
    origin_enabled: bool = False
    routed_to_execution: bool = False
    execution_authorized: bool = False
    cleanup_required: bool = False


@dataclass(frozen=True)
class TriggerIntakeRequest:
    origin_id: str
    origin_category: str
    user_visible_label: str = ""
    event_name: str = ""


@dataclass(frozen=True)
class TriggerOriginRegistration:
    origin_id: str
    origin_category: str
    user_visible_label: str = ""
    enabled: bool = False


@dataclass(frozen=True)
class TriggerRegistrationResult:
    registration: TriggerOriginRegistration | None
    registered: bool
    reason: str
    origin_category_known: bool = False
    origin_category_blocked: bool = False
    evidence: TriggerDecisionEvidence | None = None


@dataclass(frozen=True)
class TriggerOriginLifecycleResult:
    registration: TriggerOriginRegistration | None
    changed: bool
    reason: str
    origin_found: bool = False
    evidence: TriggerDecisionEvidence | None = None


@dataclass(frozen=True)
class TriggerIntakeResult:
    request: TriggerIntakeRequest
    decision: str
    reason: str
    origin_category_known: bool = False
    origin_category_blocked: bool = False
    origin_registered: bool = False
    origin_enabled: bool = False
    routed_to_execution: bool = False
    execution_authorized: bool = False
    cleanup_required: bool = False
    evidence: TriggerDecisionEvidence | None = None

    @property
    def accepted(self) -> bool:
        return False


def _trigger_decision_evidence(
    *,
    boundary: str,
    operation: str,
    origin_id: str = "",
    origin_category: str = "",
    decision: str = "",
    reason: str = "",
    origin_category_known: bool = False,
    origin_category_blocked: bool = False,
    origin_registered: bool = False,
    origin_enabled: bool = False,
    routed_to_execution: bool = False,
    execution_authorized: bool = False,
    cleanup_required: bool = False,
) -> TriggerDecisionEvidence:
    return TriggerDecisionEvidence(
        boundary=boundary,
        operation=operation,
        origin_id=normalize_trigger_origin_id(origin_id),
        origin_category=normalize_trigger_origin_category(origin_category),
        decision=decision,
        reason=reason,
        origin_category_known=origin_category_known,
        origin_category_blocked=origin_category_blocked,
        origin_registered=origin_registered,
        origin_enabled=origin_enabled,
        routed_to_execution=routed_to_execution,
        execution_authorized=execution_authorized,
        cleanup_required=cleanup_required,
    )


def normalize_trigger_origin_category(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip().casefold()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def normalize_trigger_origin_id(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def coerce_trigger_intake_request(request: TriggerIntakeRequest | dict) -> TriggerIntakeRequest:
    if isinstance(request, TriggerIntakeRequest):
        return TriggerIntakeRequest(
            origin_id=normalize_trigger_origin_id(request.origin_id),
            origin_category=normalize_trigger_origin_category(request.origin_category),
            user_visible_label=normalize_trigger_origin_id(request.user_visible_label),
            event_name=normalize_trigger_origin_id(request.event_name),
        )
    if isinstance(request, dict):
        return TriggerIntakeRequest(
            origin_id=normalize_trigger_origin_id(request.get("origin_id")),
            origin_category=normalize_trigger_origin_category(request.get("origin_category")),
            user_visible_label=normalize_trigger_origin_id(request.get("user_visible_label")),
            event_name=normalize_trigger_origin_id(request.get("event_name")),
        )
    raise TypeError("Trigger intake request must be a TriggerIntakeRequest or dict.")


def coerce_trigger_origin_registration(
    registration: TriggerOriginRegistration | dict,
) -> TriggerOriginRegistration:
    if isinstance(registration, TriggerOriginRegistration):
        return TriggerOriginRegistration(
            origin_id=normalize_trigger_origin_id(registration.origin_id),
            origin_category=normalize_trigger_origin_category(registration.origin_category),
            user_visible_label=normalize_trigger_origin_id(registration.user_visible_label),
            enabled=bool(registration.enabled),
        )
    if isinstance(registration, dict):
        return TriggerOriginRegistration(
            origin_id=normalize_trigger_origin_id(registration.get("origin_id")),
            origin_category=normalize_trigger_origin_category(registration.get("origin_category")),
            user_visible_label=normalize_trigger_origin_id(registration.get("user_visible_label")),
            enabled=bool(registration.get("enabled", False)),
        )
    raise TypeError("Trigger origin registration must be a TriggerOriginRegistration or dict.")


class TriggerOriginRegistry:
    def __init__(
        self,
        *,
        known_origin_categories: Iterable[str] = KNOWN_TRIGGER_ORIGIN_CATEGORIES,
        blocked_origin_categories: Iterable[str] = BLOCKED_TRIGGER_ORIGIN_CATEGORIES,
    ):
        self._known_origin_categories = frozenset(
            normalize_trigger_origin_category(category)
            for category in known_origin_categories
            if normalize_trigger_origin_category(category)
        )
        self._blocked_origin_categories = frozenset(
            normalize_trigger_origin_category(category)
            for category in blocked_origin_categories
            if normalize_trigger_origin_category(category)
        )
        self._registrations: dict[str, TriggerOriginRegistration] = {}

    @property
    def registrations(self) -> tuple[TriggerOriginRegistration, ...]:
        return tuple(self._registrations[key] for key in sorted(self._registrations))

    def lookup(self, origin_id: object) -> TriggerOriginRegistration | None:
        key = self._registration_key(origin_id)
        if not key:
            return None
        return self._registrations.get(key)

    def register(
        self,
        registration: TriggerOriginRegistration | dict,
    ) -> TriggerRegistrationResult:
        normalized_registration = coerce_trigger_origin_registration(registration)
        category = normalized_registration.origin_category

        if not normalized_registration.origin_id:
            return self._reject_registration(normalized_registration, "invalid_origin_id")
        if not category:
            return self._reject_registration(normalized_registration, "invalid_origin_category")
        if category in self._blocked_origin_categories:
            return self._reject_registration(
                normalized_registration,
                "blocked_origin_category",
                category_blocked=True,
            )
        if category not in self._known_origin_categories:
            return self._reject_registration(
                normalized_registration,
                "unsupported_origin_category",
            )

        key = normalized_registration.origin_id.casefold()
        if key in self._registrations:
            return self._reject_registration(
                normalized_registration,
                "duplicate_origin_id",
                category_known=True,
            )

        self._registrations[key] = normalized_registration
        return TriggerRegistrationResult(
            registration=normalized_registration,
            registered=True,
            reason="registered",
            origin_category_known=True,
            evidence=self._registration_evidence(
                normalized_registration,
                decision="registered",
                reason="registered",
                category_known=True,
                origin_registered=True,
                origin_enabled=normalized_registration.enabled,
            ),
        )

    def enable(self, origin_id: object) -> TriggerOriginLifecycleResult:
        return self._set_enabled(origin_id, True, operation="enable")

    def disable(self, origin_id: object) -> TriggerOriginLifecycleResult:
        return self._set_enabled(origin_id, False, operation="disable")

    def unregister(self, origin_id: object) -> TriggerOriginLifecycleResult:
        key = self._registration_key(origin_id)
        if not key:
            return self._lifecycle_result(
                None,
                False,
                "invalid_origin_id",
                operation="unregister",
                origin_id=origin_id,
            )
        registration = self._registrations.pop(key, None)
        if registration is None:
            return self._lifecycle_result(
                None,
                False,
                "origin_not_registered",
                operation="unregister",
                origin_id=origin_id,
            )
        return self._lifecycle_result(
            registration,
            True,
            "unregistered",
            operation="unregister",
            origin_found=True,
        )

    def _set_enabled(
        self,
        origin_id: object,
        enabled: bool,
        *,
        operation: str,
    ) -> TriggerOriginLifecycleResult:
        key = self._registration_key(origin_id)
        if not key:
            return self._lifecycle_result(
                None,
                False,
                "invalid_origin_id",
                operation=operation,
                origin_id=origin_id,
            )
        registration = self._registrations.get(key)
        if registration is None:
            return self._lifecycle_result(
                None,
                False,
                "origin_not_registered",
                operation=operation,
                origin_id=origin_id,
            )
        if registration.enabled is enabled:
            reason = "already_enabled" if enabled else "already_disabled"
            return self._lifecycle_result(
                registration,
                False,
                reason,
                operation=operation,
                origin_found=True,
            )

        updated_registration = replace(registration, enabled=enabled)
        self._registrations[key] = updated_registration
        reason = "enabled" if enabled else "disabled"
        return self._lifecycle_result(
            updated_registration,
            True,
            reason,
            operation=operation,
            origin_found=True,
        )

    def _registration_key(self, origin_id: object) -> str:
        normalized_origin_id = normalize_trigger_origin_id(origin_id)
        if not normalized_origin_id:
            return ""
        return normalized_origin_id.casefold()

    def _reject_registration(
        self,
        registration: TriggerOriginRegistration,
        reason: str,
        *,
        category_known: bool = False,
        category_blocked: bool = False,
    ) -> TriggerRegistrationResult:
        return TriggerRegistrationResult(
            registration=registration,
            registered=False,
            reason=reason,
            origin_category_known=category_known,
            origin_category_blocked=category_blocked,
            evidence=self._registration_evidence(
                registration,
                decision="rejected",
                reason=reason,
                category_known=category_known,
                category_blocked=category_blocked,
                origin_registered=reason == "duplicate_origin_id",
                origin_enabled=False,
            ),
        )

    def _lifecycle_result(
        self,
        registration: TriggerOriginRegistration | None,
        changed: bool,
        reason: str,
        *,
        operation: str,
        origin_id: object = "",
        origin_found: bool = False,
    ) -> TriggerOriginLifecycleResult:
        decision = "changed" if changed else "unchanged"
        return TriggerOriginLifecycleResult(
            registration=registration,
            changed=changed,
            reason=reason,
            origin_found=origin_found,
            evidence=_trigger_decision_evidence(
                boundary="trigger_origin_registry",
                operation=operation,
                origin_id=registration.origin_id if registration is not None else origin_id,
                origin_category=registration.origin_category if registration is not None else "",
                decision=decision,
                reason=reason,
                origin_category_known=registration is not None,
                origin_registered=origin_found,
                origin_enabled=registration.enabled if registration is not None else False,
            ),
        )

    def _registration_evidence(
        self,
        registration: TriggerOriginRegistration,
        *,
        decision: str,
        reason: str,
        category_known: bool = False,
        category_blocked: bool = False,
        origin_registered: bool = False,
        origin_enabled: bool = False,
    ) -> TriggerDecisionEvidence:
        return _trigger_decision_evidence(
            boundary="trigger_origin_registry",
            operation="register",
            origin_id=registration.origin_id,
            origin_category=registration.origin_category,
            decision=decision,
            reason=reason,
            origin_category_known=category_known,
            origin_category_blocked=category_blocked,
            origin_registered=origin_registered,
            origin_enabled=origin_enabled,
        )


class InternalTriggerIntakeBoundary:
    def __init__(
        self,
        *,
        known_origin_categories: Iterable[str] = KNOWN_TRIGGER_ORIGIN_CATEGORIES,
        blocked_origin_categories: Iterable[str] = BLOCKED_TRIGGER_ORIGIN_CATEGORIES,
        origin_registry: TriggerOriginRegistry | None = None,
    ):
        self._known_origin_categories = frozenset(
            normalize_trigger_origin_category(category)
            for category in known_origin_categories
            if normalize_trigger_origin_category(category)
        )
        self._blocked_origin_categories = frozenset(
            normalize_trigger_origin_category(category)
            for category in blocked_origin_categories
            if normalize_trigger_origin_category(category)
        )
        self._origin_registry = origin_registry

    @property
    def known_origin_categories(self) -> tuple[str, ...]:
        return tuple(sorted(self._known_origin_categories))

    @property
    def blocked_origin_categories(self) -> tuple[str, ...]:
        return tuple(sorted(self._blocked_origin_categories))

    def receive(self, request: TriggerIntakeRequest | dict) -> TriggerIntakeResult:
        normalized_request = coerce_trigger_intake_request(request)
        category = normalized_request.origin_category

        if not normalized_request.origin_id:
            return self._reject(normalized_request, "invalid_origin_id")
        if not category:
            return self._reject(normalized_request, "invalid_origin_category")
        if category in self._blocked_origin_categories:
            return self._reject(
                normalized_request,
                "blocked_origin_category",
                category_known=False,
                category_blocked=True,
            )
        if category not in self._known_origin_categories:
            return self._reject(normalized_request, "unsupported_origin_category")

        if self._origin_registry is None:
            return self._defer(normalized_request, "registration_support_not_admitted")

        registration = self._origin_registry.lookup(normalized_request.origin_id)
        if registration is None:
            return self._defer(normalized_request, "origin_not_registered")
        if registration.origin_category != category:
            return self._reject(
                normalized_request,
                "origin_registration_mismatch",
                category_known=True,
                origin_registered=True,
                origin_enabled=registration.enabled,
            )
        if not registration.enabled:
            return self._defer(
                normalized_request,
                "origin_not_enabled",
                origin_registered=True,
            )

        return self._defer(
            normalized_request,
            "invocation_follow_through_not_admitted",
            origin_registered=True,
            origin_enabled=True,
        )

    def _defer(
        self,
        request: TriggerIntakeRequest,
        reason: str,
        *,
        origin_registered: bool = False,
        origin_enabled: bool = False,
    ) -> TriggerIntakeResult:
        return TriggerIntakeResult(
            request=request,
            decision=TRIGGER_INTAKE_DECISION_DEFERRED,
            reason=reason,
            origin_category_known=True,
            origin_registered=origin_registered,
            origin_enabled=origin_enabled,
            evidence=self._intake_evidence(
                request,
                decision=TRIGGER_INTAKE_DECISION_DEFERRED,
                reason=reason,
                category_known=True,
                origin_registered=origin_registered,
                origin_enabled=origin_enabled,
            ),
        )

    def _reject(
        self,
        request: TriggerIntakeRequest,
        reason: str,
        *,
        category_known: bool = False,
        category_blocked: bool = False,
        origin_registered: bool = False,
        origin_enabled: bool = False,
    ) -> TriggerIntakeResult:
        return TriggerIntakeResult(
            request=request,
            decision=TRIGGER_INTAKE_DECISION_REJECTED,
            reason=reason,
            origin_category_known=category_known,
            origin_category_blocked=category_blocked,
            origin_registered=origin_registered,
            origin_enabled=origin_enabled,
            evidence=self._intake_evidence(
                request,
                decision=TRIGGER_INTAKE_DECISION_REJECTED,
                reason=reason,
                category_known=category_known,
                category_blocked=category_blocked,
                origin_registered=origin_registered,
                origin_enabled=origin_enabled,
            ),
        )

    def _intake_evidence(
        self,
        request: TriggerIntakeRequest,
        *,
        decision: str,
        reason: str,
        category_known: bool = False,
        category_blocked: bool = False,
        origin_registered: bool = False,
        origin_enabled: bool = False,
    ) -> TriggerDecisionEvidence:
        return _trigger_decision_evidence(
            boundary="internal_trigger_intake",
            operation="receive",
            origin_id=request.origin_id,
            origin_category=request.origin_category,
            decision=decision,
            reason=reason,
            origin_category_known=category_known,
            origin_category_blocked=category_blocked,
            origin_registered=origin_registered,
            origin_enabled=origin_enabled,
        )


__all__ = (
    "BLOCKED_TRIGGER_ORIGIN_CATEGORIES",
    "InternalTriggerIntakeBoundary",
    "KNOWN_TRIGGER_ORIGIN_CATEGORIES",
    "TRIGGER_INTAKE_DECISION_DEFERRED",
    "TRIGGER_INTAKE_DECISION_REJECTED",
    "TriggerDecisionEvidence",
    "TriggerIntakeRequest",
    "TriggerIntakeResult",
    "TriggerOriginLifecycleResult",
    "TriggerOriginRegistration",
    "TriggerOriginRegistry",
    "TriggerRegistrationResult",
    "coerce_trigger_intake_request",
    "coerce_trigger_origin_registration",
    "normalize_trigger_origin_category",
    "normalize_trigger_origin_id",
)
