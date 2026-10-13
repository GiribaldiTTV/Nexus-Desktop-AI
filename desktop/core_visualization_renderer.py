import json
import os

from PySide6.QtCore import Qt, QTimer, QUrl, QRect, Signal
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from .ai_provider_state import (
    build_default_provider_readiness_config,
    build_provider_setup_completion_foundation_state,
    resolve_default_provider_durable_consent_store_dir,
)
from .workerw_utils import (
    attach_window_to_desktop,
    make_window_noninteractive,
    position_desktop_child,
)


class CoreVisualizationWindow(QWidget):
    """Independent ORIN persona Core visualization window.

    FAM-006 HUD surfaces may be launched beside this window, but the Core
    visual must not depend on HUD render files or HUD runtime state.
    """

    core_visualization_ready = Signal()
    core_visualization_visible = Signal()

    def __init__(self, screen, visual_html_path: str, event_logger=None):
        super().__init__()
        self.screen_ref = screen
        self.visual_html_path = os.path.abspath(visual_html_path)
        self.event_logger = event_logger
        self._page_ready = False
        self._is_shutting_down = False
        self._pending_visual_state = "dormant"
        self._pending_voice_level = None
        self._provider_durable_consent_store_dir = (
            resolve_default_provider_durable_consent_store_dir()
        )
        self._ai_provider_state = build_provider_setup_completion_foundation_state(
            build_default_provider_readiness_config(),
            surface_role="core",
            durable_consent_store_dir=self._provider_durable_consent_store_dir,
        )
        self._desktop_layer_attached = False
        self._desktop_layer_logged = False
        self._visible_logged = False
        self._last_parent_geometry = QRect()

        self.setWindowTitle("Nexus Desktop AI - ORIN Core")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("background-color: transparent;")
        initial_geometry = self.compute_core_geometry()
        self.setGeometry(initial_geometry)
        self.setFixedSize(initial_geometry.size())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.webview = QWebEngineView(self)
        self.webview.setAttribute(Qt.WA_TranslucentBackground, True)
        self.webview.setAttribute(Qt.WA_NoSystemBackground, True)
        self.webview.setAutoFillBackground(False)
        self.webview.setStyleSheet("background-color: transparent; border: none;")
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setFocusPolicy(Qt.NoFocus)
        self.webview.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.webview.loadFinished.connect(self._on_load_finished)
        self.webview.load(QUrl.fromLocalFile(self.visual_html_path))
        root.addWidget(self.webview)

    def _log_event(self, event):
        if callable(self.event_logger):
            try:
                self.event_logger(event)
            except Exception:
                pass

    def compute_core_geometry(self):
        g = self.screen_ref.availableGeometry()
        width = min(max(680, int(g.width() * 0.38)), 980)
        height = min(max(620, int(g.height() * 0.72)), 1040)
        x = g.x() + max(0, (g.width() - width) // 2)
        y = g.y() + max(0, (g.height() - height) // 2)
        return QRect(x, y, width, height)

    def _virtual_desktop_geometry(self):
        rect = QRect()
        for screen in QApplication.screens():
            geometry = screen.geometry()
            if geometry.isValid() and not geometry.isNull():
                rect = geometry if rect.isNull() else rect.united(geometry)
        return rect

    def compute_core_parent_geometry(self):
        geometry = self.compute_core_geometry()
        virtual = self._virtual_desktop_geometry()
        if virtual.isValid() and not virtual.isNull():
            return QRect(
                geometry.x() - virtual.x(),
                geometry.y() - virtual.y(),
                geometry.width(),
                geometry.height(),
            )
        return geometry

    def desktop_screen_geometry(self):
        return self.compute_core_geometry()

    def is_core_visualization_ready(self):
        return self._page_ready

    def _apply_desktop_layer_mode(self, source: str = "runtime"):
        if self._is_shutting_down:
            return
        geometry = self.compute_core_geometry()
        self.setGeometry(geometry)
        self.setFixedSize(geometry.size())
        try:
            hwnd = int(self.winId())
            self._desktop_layer_attached = bool(attach_window_to_desktop(hwnd))
            if self._desktop_layer_attached:
                make_window_noninteractive(hwnd)
                parent_geometry = self.compute_core_parent_geometry()
                self.setGeometry(parent_geometry)
                self.setFixedSize(parent_geometry.size())
                self._last_parent_geometry = QRect(parent_geometry)
                position_desktop_child(
                    hwnd,
                    parent_geometry.x(),
                    parent_geometry.y(),
                    parent_geometry.width(),
                    parent_geometry.height(),
                    coordinate_space="parent",
                )
            else:
                self._last_parent_geometry = QRect(geometry)
                self.setAttribute(Qt.WA_ShowWithoutActivating, True)
                self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                self.setFocusPolicy(Qt.NoFocus)
        except Exception as exc:
            self._desktop_layer_attached = False
            self._log_event(
                "RENDERER_MAIN|CORE_VISUALIZATION_DESKTOP_LAYER_FAILED"
                f"|surface=separate_persona_core|source={source}|error={type(exc).__name__}"
            )
            return

        if self._desktop_layer_attached:
            self._log_event(
                "RENDERER_MAIN|CORE_VISUALIZATION_DESKTOP_LAYER_READY"
                "|surface=separate_persona_core"
                "|desktop_layer=workerw"
                "|hud_attachment=none"
                "|dashboard_attachment=none"
                "|overlay_attachment=none"
                "|ncp_attachment=none"
                f"|source={source}"
            )
            self._desktop_layer_logged = True
        else:
            self._log_event(
                "RENDERER_MAIN|CORE_VISUALIZATION_DESKTOP_LAYER_FALLBACK"
                "|surface=separate_persona_core"
                "|desktop_layer=unavailable"
                "|hud_attachment=none"
                "|dashboard_attachment=none"
                "|overlay_attachment=none"
                "|ncp_attachment=none"
                f"|source={source}"
            )

    def _on_load_finished(self, ok):
        if not ok:
            self._log_event("RENDERER_MAIN|CORE_VISUALIZATION_WINDOW_LOAD_FAILED")
            return
        self._page_ready = True
        self._apply_desktop_layer_mode(source="load_finished")
        self._publish_ai_provider_state_to_page()
        self._apply_pending_visual_state()
        self._apply_pending_voice_level()
        self._log_event("RENDERER_MAIN|CORE_VISUALIZATION_READY")
        self._log_event("RENDERER_MAIN|CORE_VISUALIZATION_WINDOW_READY|surface=separate_persona_core")
        geometry = self.compute_core_geometry()
        parent_geometry = self.compute_core_parent_geometry()
        virtual_geometry = self._virtual_desktop_geometry()
        screen_geometry = self.screen_ref.availableGeometry()
        center_dx = abs(geometry.center().x() - screen_geometry.center().x())
        center_dy = abs(geometry.center().y() - screen_geometry.center().y())
        self._log_event(
            "RENDERER_MAIN|CORE_VISUALIZATION_WINDOW_GEOMETRY_READY"
            f"|x={geometry.x()}|y={geometry.y()}"
            f"|w={geometry.width()}|h={geometry.height()}"
            f"|screen_x={screen_geometry.x()}|screen_y={screen_geometry.y()}"
            f"|screen_w={screen_geometry.width()}|screen_h={screen_geometry.height()}"
            f"|center_dx={center_dx}|center_dy={center_dy}"
        )
        self._log_event(
            "RENDERER_MAIN|CORE_VISUALIZATION_WORKERW_COORDINATE_REBASE_READY"
            "|surface=separate_persona_core"
            f"|desktop_layer={'workerw' if self._desktop_layer_attached else 'fallback'}"
            f"|screen_x={geometry.x()}|screen_y={geometry.y()}"
            f"|parent_x={parent_geometry.x()}|parent_y={parent_geometry.y()}"
            f"|virtual_x={virtual_geometry.x()}|virtual_y={virtual_geometry.y()}"
            f"|w={parent_geometry.width()}|h={parent_geometry.height()}"
        )
        self._log_event(
            "RENDERER_MAIN|CORE_VISUALIZATION_FIXED_PRESET_MONITOR_READY"
            "|surface=separate_persona_core"
            "|movable=false"
            "|hud_attachment=none"
            "|dashboard_attachment=none"
            "|overlay_attachment=none"
            f"|desktop_layer={'workerw' if self._desktop_layer_attached else 'fallback'}"
            f"|x={geometry.x()}|y={geometry.y()}"
            f"|parent_x={parent_geometry.x()}|parent_y={parent_geometry.y()}"
            "|coordinate_space=workerw_parent_when_attached"
            f"|w={geometry.width()}|h={geometry.height()}"
        )
        self._log_event(
            "RENDERER_MAIN|CORE_VISUALIZATION_INDEPENDENT_PRESET_MONITOR_READY"
            "|surface=separate_persona_core"
            "|scope=user_selected_install_monitor"
            "|product_attachment=none"
            f"|desktop_layer={'workerw' if self._desktop_layer_attached else 'fallback'}"
            f"|screen_x={screen_geometry.x()}|screen_y={screen_geometry.y()}"
            f"|screen_w={screen_geometry.width()}|screen_h={screen_geometry.height()}"
        )
        self.core_visualization_ready.emit()

    def showEvent(self, event):
        super().showEvent(event)
        if self._page_ready:
            self._apply_desktop_layer_mode(source="show_event")
            if not self._visible_logged:
                self._log_event("RENDERER_MAIN|CORE_VISUALIZATION_WINDOW_VISIBLE|surface=separate_persona_core")
                self._visible_logged = True
            self.core_visualization_visible.emit()

    def _apply_pending_visual_state(self):
        if not self._page_ready:
            return
        state = repr(self._pending_visual_state or "dormant")
        self.webview.page().runJavaScript(
            f"""
            if (window.setVisualState) {{
                window.setVisualState({state});
            }} else {{
                document.body.className = document.body.className
                    .replace(/\\bstate-\\S+/g, "")
                    .trim();
                document.body.classList.add("state-" + {state});
            }}
            """
        )

    def _apply_pending_voice_level(self):
        if not self._page_ready or self._pending_voice_level is None:
            return
        level = max(0.0, min(1.0, float(self._pending_voice_level)))
        self.webview.page().runJavaScript(
            f"window.setCoreVoiceLevel && window.setCoreVoiceLevel({level:.4f});"
        )
        self._pending_voice_level = None

    def _publish_ai_provider_state_to_page(self):
        if not self._page_ready or self._is_shutting_down:
            return

        payload = self._ai_provider_state.as_renderer_payload()
        payload_json = json.dumps(payload, sort_keys=True)
        self.webview.page().runJavaScript(
            f"""
            if (window.setAIProviderState) {{
                window.setAIProviderState({payload_json});
            }}
            """
        )
        self._log_event(
            "RENDERER_MAIN|AI_PROVIDER_STATE_READY"
            "|surface=core_visualization"
            f"|package={payload.get('packageId', '')}"
            f"|slices={','.join(payload.get('sliceIds', []))}"
            f"|state_id={payload.get('stateId', '')}"
            f"|mode={payload.get('mode', '')}"
            f"|availability={payload.get('availability', '')}"
            f"|privacy_scope={payload.get('privacyScope', '')}"
            f"|provider_selection={payload.get('providerSelectionState', '')}"
            f"|provider_configuration={payload.get('providerConfigurationState', '')}"
            f"|provider_registry={payload.get('providerRegistryState', '')}"
            f"|provider_interaction={payload.get('providerInteractionState', '')}"
            f"|runtime_category={payload.get('runtimeStateCategory', '')}"
            f"|runtime_reason={payload.get('runtimeReasonCode', '')}"
            f"|runtime_provenance={payload.get('runtimeProvenance', '')}"
            f"|runtime_schema={payload.get('runtimeStateSchemaVersion', '')}"
            f"|runtime_config={payload.get('runtimeConfigState', '')}"
            f"|runtime_fail_closed={str(payload.get('runtimeFailClosed', True)).lower()}"
            f"|provider_readiness={payload.get('providerReadinessState', '')}"
            f"|setup_eligibility={payload.get('setupEligibilityState', '')}"
            f"|setup_blocker={payload.get('setupBlockerState', '')}"
            f"|readiness_reason={payload.get('readinessReasonCode', '')}"
            f"|readiness_provenance={payload.get('readinessProvenance', '')}"
            f"|readiness_schema={payload.get('readinessStateSchemaVersion', '')}"
            f"|future_provider_gate={payload.get('futureProviderGateStatus', '')}"
            f"|provider_activation={payload.get('providerActivationState', '')}"
            f"|activation_eligibility={payload.get('activationEligibilityState', '')}"
            f"|activation_blocker={payload.get('activationBlockerState', '')}"
            f"|activation_reason={payload.get('activationReasonCode', '')}"
            f"|activation_provenance={payload.get('activationProvenance', '')}"
            f"|activation_schema={payload.get('activationStateSchemaVersion', '')}"
            f"|future_activation_gate={payload.get('futureActivationGateStatus', '')}"
            f"|provider_adapter={payload.get('providerAdapterPosture', '')}"
            f"|prompt_execution_gate={payload.get('promptExecutionGateState', '')}"
            f"|model_execution_gate={payload.get('modelExecutionGateState', '')}"
            f"|provider_execution_gate={payload.get('providerExecutionGateState', '')}"
            f"|functional_ai_criteria={payload.get('functionalAiCriteriaState', '')}"
            f"|v18_prebeta_readiness={payload.get('v18PrebetaReadinessState', '')}"
            f"|execution_readiness={payload.get('providerExecutionReadinessState', '')}"
            f"|execution_eligibility={payload.get('executionEligibilityState', '')}"
            f"|execution_blocker={payload.get('executionBlockerState', '')}"
            f"|execution_reason={payload.get('executionReasonCode', '')}"
            f"|execution_provenance={payload.get('executionProvenance', '')}"
            f"|execution_schema={payload.get('executionStateSchemaVersion', '')}"
            f"|execution_approval={payload.get('executionApprovalStatus', '')}"
            f"|provider_path={payload.get('providerPathStatus', '')}"
            f"|provider_path_readiness={payload.get('providerPathReadinessState', '')}"
            f"|provider_path_eligibility={payload.get('providerPathEligibilityState', '')}"
            f"|provider_path_blocker={payload.get('providerPathBlockerState', '')}"
            f"|provider_path_reason={payload.get('providerPathReasonCode', '')}"
            f"|provider_path_schema={payload.get('providerPathStateSchemaVersion', '')}"
            f"|setup_flow={payload.get('setupFlowReadinessState', '')}"
            f"|setup_flow_blocker={payload.get('setupFlowBlockerState', '')}"
            f"|setup_flow_approval={payload.get('setupFlowApprovalStatus', '')}"
            f"|consent_flow={payload.get('consentFlowReadinessState', '')}"
            f"|consent_flow_blocker={payload.get('consentFlowBlockerState', '')}"
            f"|consent_collection={payload.get('consentCollectionPosture', '')}"
            f"|setup_contract={payload.get('providerSetupContractReadinessState', '')}"
            f"|setup_contract_blocker={payload.get('providerSetupContractBlockerState', '')}"
            f"|setup_contract_approval={payload.get('providerSetupContractApprovalStatus', '')}"
            f"|setup_contract_gate={payload.get('providerSetupContractGateState', '')}"
            f"|setup_foundation={payload.get('providerSetupFoundationState', '')}"
            f"|setup_foundation_blocker={payload.get('providerSetupFoundationBlockerState', '')}"
            f"|setup_foundation_validation={payload.get('providerSetupFoundationValidationStatus', '')}"
            f"|setup_foundation_persistence={payload.get('providerSetupFoundationPersistenceStatus', '')}"
            f"|setup_foundation_gate={payload.get('providerSetupFoundationGateState', '')}"
            f"|consent_collection_foundation={payload.get('consentCollectionFoundationState', '')}"
            f"|consent_collection_blocker={payload.get('consentCollectionBlockerState', '')}"
            f"|consent_collection_validation={payload.get('consentCollectionValidationStatus', '')}"
            f"|consent_collection_persistence={payload.get('consentPersistenceStatus', '')}"
            f"|consent_collection_gate={payload.get('consentCollectionGateState', '')}"
            f"|durable_consent_record={payload.get('durableConsentRecordState', '')}"
            f"|durable_setup_consent={payload.get('durableSetupConsentState', '')}"
            f"|durable_execution_consent={payload.get('durableExecutionConsentState', '')}"
            f"|durable_consent_status_proof={payload.get('durableConsentStatusProofState', '')}"
            f"|durable_consent_desktop_display={payload.get('durableConsentDesktopDisplayState', '')}"
            f"|durable_consent_setup_handoff={payload.get('durableConsentProviderSetupHandoffState', '')}"
            f"|durable_consent_execution_handoff={payload.get('durableConsentProviderExecutionHandoffState', '')}"
            f"|consent_ux_state={payload.get('consentUxState', '')}"
            f"|consent_ux_intent={payload.get('consentUxIntentState', '')}"
            f"|consent_ux_surface={payload.get('consentUxSurfaceState', '')}"
            f"|consent_ux_setup_display={payload.get('consentUxSetupDisplayState', '')}"
            f"|consent_ux_execution_display={payload.get('consentUxExecutionDisplayState', '')}"
            f"|consent_ux_revocation_reset={payload.get('consentUxRevocationResetState', '')}"
            f"|consent_ux_write={payload.get('consentUxWritePosture', '')}"
            f"|consent_ux_status_proof={payload.get('consentUxStatusProofState', '')}"
            f"|consent_ux_desktop_display={payload.get('consentUxDesktopDisplayState', '')}"
            f"|consent_ux_setup_gate={payload.get('consentUxProviderSetupGateState', '')}"
            f"|consent_ux_execution_gate={payload.get('consentUxProviderExecutionGateState', '')}"
            f"|setup_completion={payload.get('providerSetupCompletionState', '')}"
            f"|setup_completion_blocker={payload.get('providerSetupCompletionBlockerState', '')}"
            f"|setup_completion_reason={payload.get('providerSetupCompletionReasonCode', '')}"
            f"|setup_completion_profile={payload.get('providerSetupCompletionProfileStatus', '')}"
            f"|setup_completion_config={payload.get('providerSetupCompletionConfigStatus', '')}"
            f"|setup_completion_no_secrets={payload.get('providerSetupCompletionNoSecretsStatus', '')}"
            f"|setup_completion_validation={payload.get('providerSetupCompletionValidationStatus', '')}"
            f"|setup_completion_persistence={payload.get('providerSetupCompletionPersistenceStatus', '')}"
            f"|setup_completion_reset={payload.get('providerSetupCompletionResetState', '')}"
            f"|setup_completion_status_proof={payload.get('providerSetupCompletionStatusProofState', '')}"
            f"|setup_completion_desktop_display={payload.get('providerSetupCompletionDesktopDisplayState', '')}"
            f"|setup_completion_setup_gate={payload.get('providerSetupCompletionProviderSetupGateState', '')}"
            f"|setup_completion_execution_gate={payload.get('providerSetupCompletionProviderExecutionGateState', '')}"
            f"|setup_completion_sdk_handoff={payload.get('providerSetupCompletionSdkHandoffState', '')}"
            f"|provider_setup_handoff={payload.get('providerSetupHandoffPosture', '')}"
            f"|provider_consent_handoff={payload.get('providerConsentHandoffPosture', '')}"
            f"|desktop_readiness_display={payload.get('desktopAiOwnedReadinessDisplayState', '')}"
            f"|setup_consent={payload.get('setupConsentState', '')}"
            f"|execution_consent={payload.get('executionConsentState', '')}"
            f"|provider_config_status={payload.get('providerConfigStatus', '')}"
            f"|adapter_selection={payload.get('adapterSelectionPosture', '')}"
            f"|prompt_acceptance_gate={payload.get('promptAcceptanceGateState', '')}"
            f"|prompt_routing_gate={payload.get('promptRoutingGateState', '')}"
            f"|prompt_send={payload.get('promptSendPosture', '')}"
            f"|model_execution_status={payload.get('modelExecutionStatus', '')}"
            f"|provider_visible_data_execution={payload.get('providerVisibleDataExecutionPosture', '')}"
            f"|functional_ai_release_gate={payload.get('functionalAiReleaseGateState', '')}"
            f"|v18_release_gate={payload.get('v18ReleaseGateState', '')}"
            f"|configured_provider_count={payload.get('configuredProviderCount', 0)}"
            f"|available_provider_count={payload.get('availableProviderCount', 0)}"
            f"|hardware_capability={payload.get('hardwareCapabilityState', '')}"
            f"|gpu_capability={payload.get('gpuCapabilityState', '')}"
            f"|cpu_fallback={payload.get('cpuFallbackState', '')}"
            f"|hardware_detection_level={payload.get('hardwareDetectionLevel', '')}"
            f"|ram_readiness={payload.get('ramReadinessState', '')}"
            f"|disk_readiness={payload.get('diskReadinessState', '')}"
            f"|model_workload={payload.get('modelWorkloadState', '')}"
            f"|model_workload_metadata={payload.get('modelWorkloadMetadataState', '')}"
            f"|capability_pack_lifecycle={payload.get('capabilityPackLifecycleState', '')}"
            f"|capability_pack_download={payload.get('capabilityPackDownloadState', '')}"
            f"|capability_pack_manifest={payload.get('capabilityPackManifestState', '')}"
            f"|capability_pack_compatibility={payload.get('capabilityPackCompatibilityState', '')}"
            f"|capability_pack_eligibility={payload.get('capabilityPackEligibilityState', '')}"
            f"|install_intent={payload.get('installIntentState', '')}"
            f"|data_classification={payload.get('dataClassificationState', '')}"
            f"|provider_visible_data_guarantee={payload.get('providerVisibleDataGuarantee', '')}"
            f"|memory_context={payload.get('memoryContextState', '')}"
            f"|memory_indexing={payload.get('memoryIndexingState', '')}"
            f"|network_egress={payload.get('networkEgressState', '')}"
            f"|windows_resilience={payload.get('windowsResilienceState', '')}"
            f"|voice_runtime={payload.get('voiceRuntimeState', '')}"
            f"|persona_voice_boundary={payload.get('personaCoreVoiceState', '')}"
            f"|validation_gates={payload.get('validationProofGateState', '')}"
            f"|release_proof={payload.get('releaseProofGateState', '')}"
            f"|copy_contract={payload.get('coreDesktopRuntimeStateContract', '')}"
            f"|contract_ready={payload.get('contractReadyMarker', '')}"
            f"|consent_state={payload.get('consentState', '')}"
            f"|interaction_affordance={payload.get('interactionAffordance', '')}"
            f"|provider_visible_data={payload.get('providerVisibleData', '')}"
            f"|provider_next_action={payload.get('providerNextActionLabel', '')}"
            f"|requires_consent={str(payload.get('requiresConsent', False)).lower()}"
            f"|sent_to_provider={str(payload.get('sentToProvider', False)).lower()}"
        )

    def set_visual_state(self, state_name):
        self._pending_visual_state = state_name
        self._apply_pending_visual_state()

    def set_voice_level(self, level):
        self._pending_voice_level = level
        self._apply_pending_voice_level()

    def request_shutdown(self):
        self._is_shutting_down = True
        try:
            self.close()
        except RuntimeError:
            return
        try:
            QTimer.singleShot(0, self.deleteLater)
        except RuntimeError:
            return
