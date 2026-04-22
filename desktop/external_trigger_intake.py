from dataclasses import dataclass
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
class TriggerIntakeRequest:
    origin_id: str
    origin_category: str
    user_visible_label: str = ""
    event_name: str = ""


@dataclass(frozen=True)
class TriggerIntakeResult:
    request: TriggerIntakeRequest
    decision: str
    reason: str
    origin_category_known: bool = False
    origin_category_blocked: bool = False
    routed_to_execution: bool = False
    execution_authorized: bool = False
    cleanup_required: bool = False

    @property
    def accepted(self) -> bool:
        return False


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


class InternalTriggerIntakeBoundary:
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

        return TriggerIntakeResult(
            request=normalized_request,
            decision=TRIGGER_INTAKE_DECISION_DEFERRED,
            reason="runtime_support_not_admitted",
            origin_category_known=True,
        )

    def _reject(
        self,
        request: TriggerIntakeRequest,
        reason: str,
        *,
        category_known: bool = False,
        category_blocked: bool = False,
    ) -> TriggerIntakeResult:
        return TriggerIntakeResult(
            request=request,
            decision=TRIGGER_INTAKE_DECISION_REJECTED,
            reason=reason,
            origin_category_known=category_known,
            origin_category_blocked=category_blocked,
        )


__all__ = (
    "BLOCKED_TRIGGER_ORIGIN_CATEGORIES",
    "InternalTriggerIntakeBoundary",
    "KNOWN_TRIGGER_ORIGIN_CATEGORIES",
    "TRIGGER_INTAKE_DECISION_DEFERRED",
    "TRIGGER_INTAKE_DECISION_REJECTED",
    "TriggerIntakeRequest",
    "TriggerIntakeResult",
    "coerce_trigger_intake_request",
    "normalize_trigger_origin_category",
    "normalize_trigger_origin_id",
)
