from __future__ import annotations

from dataclasses import asdict, dataclass
import threading
from typing import Callable, Optional


HUD_ACCESS_SUCCESS = "success"
HUD_ACCESS_PARTIAL = "partial"
HUD_ACCESS_FAILED = "failed"
HUD_ACCESS_BLOCKED = "blocked"
HUD_ACCESS_SUPERSEDED = "superseded"


@dataclass(frozen=True)
class MonitoringHudAccessState:
    enabled: bool
    dashboard_open: bool
    available: bool
    runtime_available: bool
    availability_reason: str
    route_state: str
    source: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MonitoringHudAccessResult:
    operation: str
    status: str
    confirmed_enabled: bool
    persistence_succeeded: Optional[bool]
    tray_refresh_succeeded: Optional[bool]
    dashboard_action_succeeded: Optional[bool]
    retryable: bool
    message: str
    generation: int
    source: str
    available: bool
    dashboard_open: bool
    coalesced: bool = False
    superseded_by_generation: Optional[int] = None

    @property
    def succeeded(self) -> bool:
        return self.status == HUD_ACCESS_SUCCESS

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class MonitoringHudAccessAdapter:
    """FAM-003 doorway over the existing owner-backed HUD runtime contract."""

    def __init__(
        self,
        *,
        query_state: Callable[[], dict[str, object]],
        persist_enabled: Callable[[bool, str], bool],
        open_or_restore_dashboard: Callable[[str], bool],
        close_dashboard: Callable[[str], bool],
        refresh_tray: Optional[Callable[[str], bool]] = None,
        is_shutting_down: Optional[Callable[[], bool]] = None,
        event_logger: Optional[Callable[[str], None]] = None,
    ):
        self._query_state_callback = query_state
        self._persist_enabled_callback = persist_enabled
        self._open_dashboard_callback = open_or_restore_dashboard
        self._close_dashboard_callback = close_dashboard
        self._refresh_tray_callback = refresh_tray
        self._is_shutting_down_callback = is_shutting_down or (lambda: False)
        self._event_logger = event_logger or (lambda _event: None)
        self._owner_thread_id = threading.get_ident()
        self._lock = threading.RLock()
        self._generation = 0
        self._in_flight_signature: tuple[str, object] | None = None
        self._last_result: MonitoringHudAccessResult | None = None
        self._last_retry: tuple[str, object] | None = None
        self._shutdown_started = False

    @property
    def generation(self) -> int:
        return self._generation

    def bind_tray_refresh(self, callback: Optional[Callable[[str], bool]]) -> None:
        self._refresh_tray_callback = callback if callable(callback) else None

    def begin_shutdown(self, source: str = "runtime") -> None:
        with self._lock:
            self._shutdown_started = True
            self._generation += 1
            self._emit("SHUTDOWN_GUARD", source, self._generation)

    def query_state(self) -> MonitoringHudAccessState:
        if not self._on_owner_thread():
            return MonitoringHudAccessState(
                enabled=False,
                dashboard_open=False,
                available=False,
                runtime_available=False,
                availability_reason="HUD state is available only on the desktop runtime thread.",
                route_state="unknown",
                source="thread_guard",
            )
        try:
            payload = self._query_state_callback()
        except Exception as exc:
            return MonitoringHudAccessState(
                enabled=False,
                dashboard_open=False,
                available=False,
                runtime_available=False,
                availability_reason=f"HUD state is unavailable ({type(exc).__name__}).",
                route_state="unknown",
                source="query_failed",
            )
        payload = payload if isinstance(payload, dict) else {}
        runtime_available = bool(payload.get("runtime_available", True))
        enabled = bool(payload.get("feature_enabled"))
        available = bool(payload.get("dashboard_available", runtime_available))
        reason = str(
            payload.get("availability_reason")
            or payload.get("resident_route_reason")
            or ("" if available else "HUD Dashboard is unavailable.")
        ).strip()
        route_state = str(
            payload.get("resident_route_state")
            or ("enabled_available" if enabled and available else "enabled_not_ready" if enabled else "disabled_by_user")
        )
        return MonitoringHudAccessState(
            enabled=enabled,
            dashboard_open=bool(payload.get("dashboard_visible")),
            available=available,
            runtime_available=runtime_available,
            availability_reason=reason,
            route_state=route_state,
            source=str(payload.get("source") or "runtime"),
        )

    def set_enabled(self, enabled: bool, source: str) -> MonitoringHudAccessResult:
        desired = bool(enabled)
        operation = "enable" if desired else "disable"
        generation, early = self._begin_operation(operation, desired, source)
        if early is not None:
            return early
        try:
            pre_state = self.query_state()
            persisted = self._call_bool(self._persist_enabled_callback, desired, source)
            stale = self._superseded_result_if_needed(operation, source, generation)
            if stale is not None:
                return stale
            confirmed = self.query_state()
            if not persisted or confirmed.enabled != desired:
                message = (
                    "HUD Dashboard could not be enabled. Try again."
                    if desired
                    else "HUD Dashboard could not be disabled. Try again."
                )
                return self._finish(
                    operation=operation,
                    status=HUD_ACCESS_FAILED,
                    source=source,
                    generation=generation,
                    state=confirmed if persisted else pre_state,
                    persistence_succeeded=False,
                    tray_refresh_succeeded=None,
                    dashboard_action_succeeded=None,
                    retryable=True,
                    message=message,
                    retry=("set_enabled", desired),
                )

            if desired:
                # Enabling changes availability; opening is a separate USER action.
                tray_ok = self._refresh_tray(f"{source}_enabled")
                stale = self._superseded_result_if_needed(operation, source, generation)
                if stale is not None:
                    return stale
                dashboard_ok = None
            else:
                dashboard_ok = self._call_bool(self._close_dashboard_callback, source)
                stale = self._superseded_result_if_needed(operation, source, generation)
                if stale is not None:
                    return stale
                tray_ok = self._refresh_tray(f"{source}_disabled")
                stale = self._superseded_result_if_needed(operation, source, generation)
                if stale is not None:
                    return stale

            final_state = self.query_state()
            stale = self._superseded_result_if_needed(operation, source, generation)
            if stale is not None:
                return stale
            if not desired:
                dashboard_ok = bool(dashboard_ok and not final_state.dashboard_open)
            status = HUD_ACCESS_SUCCESS if tray_ok and dashboard_ok is not False else HUD_ACCESS_PARTIAL
            if status == HUD_ACCESS_SUCCESS:
                message = "HUD Dashboard enabled. Open it when you want to use it." if desired else "HUD Dashboard disabled."
                retry = None
            elif tray_ok and dashboard_ok is False:
                message = "Disabled. Dashboard close needs retry."
                retry = ("close", None)
            elif not tray_ok and dashboard_ok is not False:
                message = (
                    "Enabled. Resident menu update needs retry."
                    if desired
                    else "Disabled. Resident menu update needs retry."
                )
                retry = ("set_enabled", desired)
            else:
                message = "Disabled, but resident menu and Dashboard did not update. Retry."
                retry = ("set_enabled", desired)
            return self._finish(
                operation=operation,
                status=status,
                source=source,
                generation=generation,
                state=final_state,
                persistence_succeeded=True,
                tray_refresh_succeeded=tray_ok,
                dashboard_action_succeeded=dashboard_ok,
                retryable=status != HUD_ACCESS_SUCCESS,
                message=message,
                retry=retry,
            )
        finally:
            self._end_operation(operation, desired)

    def open_or_restore_dashboard(self, source: str) -> MonitoringHudAccessResult:
        return self._run_dashboard_action("open_or_restore", self._open_dashboard_callback, source)

    def close_dashboard(self, source: str) -> MonitoringHudAccessResult:
        return self._run_dashboard_action("close", self._close_dashboard_callback, source)

    def retry_last_operation(self, source: str) -> MonitoringHudAccessResult:
        retry = self._last_retry
        if retry is None:
            state = self.query_state()
            return self._result(
                operation="retry",
                status=HUD_ACCESS_BLOCKED,
                source=source,
                generation=self._generation,
                state=state,
                message="There is no HUD operation to retry.",
                retryable=False,
            )
        operation, value = retry
        if operation == "set_enabled":
            return self.set_enabled(bool(value), source)
        if operation == "open_or_restore":
            return self.open_or_restore_dashboard(source)
        return self.close_dashboard(source)

    def _run_dashboard_action(
        self,
        operation: str,
        callback: Callable[[str], bool],
        source: str,
    ) -> MonitoringHudAccessResult:
        generation, early = self._begin_operation(operation, None, source)
        if early is not None:
            return early
        try:
            state = self.query_state()
            if operation == "open_or_restore" and not state.enabled:
                return self._finish(
                    operation=operation,
                    status=HUD_ACCESS_BLOCKED,
                    source=source,
                    generation=generation,
                    state=state,
                    message="Enable HUD Dashboard in Global Settings first.",
                    retryable=False,
                )
            action_available = (
                state.runtime_available if operation == "close" else state.available
            )
            if not action_available:
                return self._finish(
                    operation=operation,
                    status=HUD_ACCESS_BLOCKED,
                    source=source,
                    generation=generation,
                    state=state,
                    message=state.availability_reason or "HUD Dashboard is unavailable.",
                    retryable=True,
                    retry=(operation, None),
                )
            action_ok = self._call_bool(callback, source)
            stale = self._superseded_result_if_needed(operation, source, generation)
            if stale is not None:
                return stale
            final_state = self.query_state()
            expected_open = operation == "open_or_restore"
            confirmed = final_state.dashboard_open == expected_open
            status = HUD_ACCESS_SUCCESS if action_ok and confirmed else HUD_ACCESS_FAILED
            message = (
                "HUD Dashboard is open."
                if operation == "open_or_restore" and status == HUD_ACCESS_SUCCESS
                else "HUD Dashboard is closed."
                if operation == "close" and status == HUD_ACCESS_SUCCESS
                else "HUD Dashboard did not respond. Try again."
            )
            return self._finish(
                operation=operation,
                status=status,
                source=source,
                generation=generation,
                state=final_state,
                dashboard_action_succeeded=action_ok and confirmed,
                retryable=status != HUD_ACCESS_SUCCESS,
                message=message,
                retry=None if status == HUD_ACCESS_SUCCESS else (operation, None),
            )
        finally:
            self._end_operation(operation, None)

    def _begin_operation(
        self,
        operation: str,
        value: object,
        source: str,
    ) -> tuple[int, MonitoringHudAccessResult | None]:
        state = self.query_state()
        if not self._on_owner_thread():
            return self._generation, self._result(
                operation=operation,
                status=HUD_ACCESS_BLOCKED,
                source=source,
                generation=self._generation,
                state=state,
                message="HUD changes must run on the desktop runtime thread.",
                retryable=True,
            )
        if self._shutdown_started or self._is_shutting_down_callback():
            return self._generation, self._result(
                operation=operation,
                status=HUD_ACCESS_BLOCKED,
                source=source,
                generation=self._generation,
                state=state,
                message="Nexus is shutting down. HUD changes were not applied.",
                retryable=False,
            )
        with self._lock:
            signature = (operation, value)
            if self._in_flight_signature == signature:
                return self._generation, self._result(
                    operation=operation,
                    status=HUD_ACCESS_BLOCKED,
                    source=source,
                    generation=self._generation,
                    state=state,
                    message="That HUD change is already in progress.",
                    retryable=True,
                    coalesced=True,
                )
            self._generation += 1
            generation = self._generation
            self._in_flight_signature = signature
            self._emit("REQUESTED", source, generation, operation=operation)
            return generation, None

    def _end_operation(self, operation: str, value: object) -> None:
        with self._lock:
            if self._in_flight_signature == (operation, value):
                self._in_flight_signature = None

    def _superseded_result_if_needed(
        self,
        operation: str,
        source: str,
        generation: int,
    ) -> MonitoringHudAccessResult | None:
        if generation == self._generation and not self._shutdown_started:
            return None
        state = self.query_state()
        return self._finish(
            operation=operation,
            status=HUD_ACCESS_SUPERSEDED,
            source=source,
            generation=generation,
            state=state,
            message="A newer HUD request replaced this operation.",
            retryable=False,
            superseded_by_generation=self._generation,
        )

    def _refresh_tray(self, source: str) -> bool:
        if not callable(self._refresh_tray_callback):
            return False
        return self._call_bool(self._refresh_tray_callback, source)

    def _finish(
        self,
        *,
        operation: str,
        status: str,
        source: str,
        generation: int,
        state: MonitoringHudAccessState,
        message: str,
        retryable: bool,
        persistence_succeeded: Optional[bool] = None,
        tray_refresh_succeeded: Optional[bool] = None,
        dashboard_action_succeeded: Optional[bool] = None,
        retry: tuple[str, object] | None = None,
        coalesced: bool = False,
        superseded_by_generation: Optional[int] = None,
    ) -> MonitoringHudAccessResult:
        result = self._result(
            operation=operation,
            status=status,
            source=source,
            generation=generation,
            state=state,
            message=message,
            retryable=retryable,
            persistence_succeeded=persistence_succeeded,
            tray_refresh_succeeded=tray_refresh_succeeded,
            dashboard_action_succeeded=dashboard_action_succeeded,
            coalesced=coalesced,
            superseded_by_generation=superseded_by_generation,
        )
        self._last_result = result
        self._last_retry = retry
        self._emit(
            "RESULT",
            source,
            generation,
            operation=operation,
            status=status,
            persistence=persistence_succeeded,
            tray=tray_refresh_succeeded,
            dashboard=dashboard_action_succeeded,
        )
        return result

    def _result(
        self,
        *,
        operation: str,
        status: str,
        source: str,
        generation: int,
        state: MonitoringHudAccessState,
        message: str,
        retryable: bool,
        persistence_succeeded: Optional[bool] = None,
        tray_refresh_succeeded: Optional[bool] = None,
        dashboard_action_succeeded: Optional[bool] = None,
        coalesced: bool = False,
        superseded_by_generation: Optional[int] = None,
    ) -> MonitoringHudAccessResult:
        return MonitoringHudAccessResult(
            operation=operation,
            status=status,
            confirmed_enabled=state.enabled,
            persistence_succeeded=persistence_succeeded,
            tray_refresh_succeeded=tray_refresh_succeeded,
            dashboard_action_succeeded=dashboard_action_succeeded,
            retryable=retryable,
            message=str(message or "HUD state updated.")[:180],
            generation=generation,
            source=str(source or "runtime")[:80],
            available=state.available,
            dashboard_open=state.dashboard_open,
            coalesced=coalesced,
            superseded_by_generation=superseded_by_generation,
        )

    def _on_owner_thread(self) -> bool:
        return threading.get_ident() == self._owner_thread_id

    @staticmethod
    def _call_bool(callback: Callable, *args) -> bool:
        try:
            return bool(callback(*args))
        except Exception:
            return False

    def _emit(self, event: str, source: str, generation: int, **fields) -> None:
        parts = [
            "RENDERER_MAIN",
            f"MONITORING_HUD_ACCESS_{event}",
            f"source={str(source or 'runtime').replace('|', '/')}",
            f"generation={generation}",
        ]
        for key, value in fields.items():
            parts.append(f"{key}={str(value).replace('|', '/')}")
        try:
            self._event_logger("|".join(parts))
        except Exception:
            pass
