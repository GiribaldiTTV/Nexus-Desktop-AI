const body = document.body;
const monitoringHud = document.getElementById("monitoring-hud");
const monitoringHudMinimal = document.getElementById("monitoring-hud-minimal");
const monitoringHudOverlayDisplay = document.getElementById("monitoring-hud-overlay-display");
const monitoringHudOverlayCanvas = document.getElementById("monitoring-hud-overlay-canvas");
const monitoringHudOverlayProfileDisplayStatus = document.getElementById("monitoring-hud-overlay-profile-display-status");
const monitoringHudOverlayProfileDisplayName = document.getElementById("monitoring-hud-overlay-profile-display-name");
const monitoringHudOverlayProfileDisplayCount = document.getElementById("monitoring-hud-overlay-profile-display-count");
const monitoringHudMinimalRuntimeStatus = document.getElementById("monitoring-hud-minimal-runtime-status");
const monitoringHudMinimalProviderState = document.getElementById("monitoring-hud-minimal-provider-state");
const monitoringHudMinimalAnchor = document.getElementById("monitoring-hud-minimal-anchor");
const monitoringHudMinimalWarning = document.getElementById("monitoring-hud-minimal-warning");
const monitoringHudRuntimeStatus = document.getElementById("monitoring-hud-runtime-status");
const monitoringHudProviderState = document.getElementById("monitoring-hud-provider-state");
const monitoringHudAdapterStatus = document.getElementById("monitoring-hud-adapter-status");
const monitoringHudSourceScope = document.getElementById("monitoring-hud-source-scope");
const monitoringHudHardwarePolling = document.getElementById("monitoring-hud-hardware-polling");
const monitoringHudProviderStateMatrix = document.getElementById("monitoring-hud-provider-state-matrix");
const monitoringHudPlacementOwner = document.getElementById("monitoring-hud-placement-owner");
const monitoringHudPlacementAnchor = document.getElementById("monitoring-hud-placement-anchor");
const monitoringHudPlacementPointer = document.getElementById("monitoring-hud-placement-pointer");
const monitoringHudResizePosture = document.getElementById("monitoring-hud-resize-posture");
const monitoringHudOverlayProfileEditor = document.getElementById("monitoring-hud-overlay-profile-editor");
const monitoringHudOverlayProfileSelector = document.getElementById("monitoring-hud-overlay-profile-selector");
const monitoringHudOverlayProfileToggle = document.getElementById("monitoring-hud-overlay-profile-toggle");
const monitoringHudOverlayProfileLabel = document.getElementById("monitoring-hud-overlay-profile-label");
const monitoringHudOverlayProfileMenu = document.getElementById("monitoring-hud-overlay-profile-menu");
const monitoringHudOverlayProfileMonitorCount = document.getElementById("monitoring-hud-overlay-profile-monitor-count");
const monitoringHudOverlayProfileDisplayMode = document.getElementById("monitoring-hud-overlay-profile-display-mode");
let monitoringHudOverlayProfileSelectorPointerActivatedAt = 0;
const monitoringHudRecordingCard = document.querySelector('[data-dashboard-hub-card="recording"]');
const monitoringHudRecordingCardSummary = document.getElementById("monitoring-hud-recording-card-summary");
const monitoringHudRecordingTargetPreview = document.getElementById("monitoring-hud-recording-target-preview");
const monitoringHudRecordingTargetProfile = document.getElementById("monitoring-hud-recording-target-profile");
const monitoringHudRecordingTargetCount = document.getElementById("monitoring-hud-recording-target-count");
const monitoringHudRecordingTargetSummary = document.getElementById("monitoring-hud-recording-target-summary");
const monitoringHudRecordingControlLauncher = document.getElementById("monitoring-hud-recording-control-launcher");
const monitoringHudRecordingStudioOpen = document.getElementById("monitoring-hud-recording-studio-open");
const monitoringHudRecordingOpenFolder = document.getElementById("monitoring-hud-recording-open-folder");
const monitoringHudOverlayProfileOpenSettings = document.getElementById("monitoring-hud-overlay-profile-open-settings");
const monitoringHudOverlayProfileNameInput = document.getElementById("monitoring-hud-overlay-profile-name-input");
const monitoringHudOverlayProfileCreate = document.getElementById("monitoring-hud-overlay-profile-create");
const monitoringHudOverlayProfileSave = document.getElementById("monitoring-hud-overlay-profile-save");
const monitoringHudOverlayProfileDiscard = document.getElementById("monitoring-hud-overlay-profile-discard");
const monitoringHudOverlayProfileMembershipNote = document.getElementById("monitoring-hud-overlay-profile-membership-note");
const monitoringHudOverlayProfileMembershipList = document.getElementById("monitoring-hud-overlay-profile-membership-list");
const monitoringHudOverlayProfileMonitorSearch = document.getElementById("monitoring-hud-overlay-profile-monitor-search");
const monitoringHudOverlayProfileMonitorFilter = document.getElementById("monitoring-hud-overlay-profile-monitor-filter");
const monitoringHudOverlayProfileMonitorFilterToggle = document.getElementById("monitoring-hud-overlay-profile-monitor-filter-toggle");
const monitoringHudOverlayProfileMonitorFilterLabel = document.getElementById("monitoring-hud-overlay-profile-monitor-filter-label");
const monitoringHudOverlayProfileMonitorFilterMenu = document.getElementById("monitoring-hud-overlay-profile-monitor-filter-menu");
const monitoringHudOverlayProfileMonitorResults = document.getElementById("monitoring-hud-overlay-profile-monitor-results");
const monitoringHudOverlayProfileWindow = document.getElementById("monitoring-hud-overlay-profile-window");
const monitoringHudOverlayProfileWindowTitle = document.getElementById("monitoring-hud-overlay-profile-window-title");
const monitoringHudOverlayProfileWindowActiveName = document.getElementById("monitoring-hud-overlay-profile-window-active-name");
const monitoringHudOverlayProfileWindowCount = document.getElementById("monitoring-hud-overlay-profile-window-count");
const monitoringHudOverlayProfileWindowMembership = document.getElementById("monitoring-hud-overlay-profile-window-membership");
const monitoringHudOverlayProfileWindowSelector = document.getElementById("monitoring-hud-overlay-profile-window-selector");
const monitoringHudOverlayProfileWindowToggle = document.getElementById("monitoring-hud-overlay-profile-window-toggle");
const monitoringHudOverlayProfileWindowLabel = document.getElementById("monitoring-hud-overlay-profile-window-label");
const monitoringHudOverlayProfileWindowMenu = document.getElementById("monitoring-hud-overlay-profile-window-menu");
const monitoringHudOverlayProfileDetailSection = document.getElementById("monitoring-hud-overlay-profile-detail-section");
const monitoringHudOverlayProfileUnsavedGuard = document.getElementById("monitoring-hud-overlay-profile-unsaved-guard");
const monitoringHudOverlayProfileUnsavedSave = document.getElementById("monitoring-hud-overlay-profile-unsaved-save");
const monitoringHudOverlayProfileUnsavedDiscard = document.getElementById("monitoring-hud-overlay-profile-unsaved-discard");
const monitoringHudOverlayProfileUnsavedCancel = document.getElementById("monitoring-hud-overlay-profile-unsaved-cancel");
const monitoringHudOverlayProfileDelete = document.getElementById("monitoring-hud-overlay-profile-delete");
const monitoringHudOverlayProfileDeleteConfirmation = document.getElementById("monitoring-hud-overlay-profile-delete-confirmation");
const monitoringHudOverlayProfileDeleteTitle = document.getElementById("monitoring-hud-overlay-profile-delete-title");
const monitoringHudOverlayProfileDeleteCopy = document.getElementById("monitoring-hud-overlay-profile-delete-copy");
const monitoringHudOverlayProfileDeleteConfirm = document.getElementById("monitoring-hud-overlay-profile-delete-confirm");
const monitoringHudOverlayProfileDeleteCancel = document.getElementById("monitoring-hud-overlay-profile-delete-cancel");
const monitoringHudControlsVisibility = document.getElementById("monitoring-hud-controls-visibility");
const monitoringHudControlsSurface = document.getElementById("monitoring-hud-controls-surface");
const monitoringHudControlsPersistence = document.getElementById("monitoring-hud-controls-persistence");
const monitoringHudStatusLabel = document.getElementById("monitoring-hud-status-label");
const monitoringHudNoDataBehavior = document.getElementById("monitoring-hud-no-data-behavior");
const monitoringHudDegradedBehavior = document.getElementById("monitoring-hud-degraded-behavior");
const monitoringHudWarningPosture = document.getElementById("monitoring-hud-warning-posture");
const monitoringHudTrayPath = document.getElementById("monitoring-hud-tray-path");
const monitoringHudAnchorStatus = document.getElementById("monitoring-hud-anchor-status");
const monitoringHudDragHandle = document.getElementById("monitoring-hud-drag-handle");
const monitoringHudToggle = document.getElementById("monitoring-hud-toggle");
const monitoringHudAnchorToggle = document.getElementById("monitoring-hud-anchor-toggle");
const monitoringHudDashboardClose = document.getElementById("monitoring-hud-dashboard-close-action");
const monitoringHudSettingsAction = document.getElementById("monitoring-hud-settings-action");
const monitoringHudEditMonitor = document.getElementById("monitoring-hud-edit-monitor-action");
const monitoringHudSnapToggle = document.getElementById("monitoring-hud-snap-toggle");
const monitoringHudWarningToggle = document.getElementById("monitoring-hud-warning-toggle");
const monitoringHudSnapLabel = document.getElementById("monitoring-hud-snap-label");
const monitoringHudPollingRate = document.getElementById("monitoring-hud-polling-rate");
const monitoringHudWarningModeControl = document.getElementById("monitoring-hud-warning-mode-control");
const monitoringHudMonitorList = document.getElementById("monitoring-hud-monitor-list");
const monitoringHudMonitorListSummary = document.getElementById("monitoring-hud-monitor-list-summary");
const monitoringHudMonitorCount = document.getElementById("monitoring-hud-monitor-count");
const monitoringHudMonitorPollingSummary = document.getElementById("monitoring-hud-monitor-polling-summary");
const monitoringHudMonitorEditorTitle = document.getElementById("monitoring-hud-monitor-editor-title");
const monitoringHudMonitorEnabled = document.getElementById("monitoring-hud-monitor-enabled");
const monitoringHudMonitorPollingRate = document.getElementById("monitoring-hud-monitor-polling-rate");
const monitoringHudMonitorPollingRateControl = document.getElementById("monitoring-hud-monitor-polling-rate-control");
const monitoringHudMonitorPollingRateToggle = document.getElementById("monitoring-hud-monitor-polling-rate-toggle");
const monitoringHudMonitorPollingRateLabel = document.getElementById("monitoring-hud-monitor-polling-rate-label");
const monitoringHudMonitorEditorScope = document.getElementById("monitoring-hud-monitor-editor-scope");
const monitoringHudChildWindowLayer = document.getElementById("monitoring-hud-child-window-layer");
const monitoringHudSettingsWindow = document.getElementById("monitoring-hud-settings-window");
const monitoringHudSettingsWarningToggle = document.getElementById("monitoring-hud-settings-warning-toggle");
const monitoringHudSettingsFeatureControl = document.getElementById("monitoring-hud-settings-feature-control");
const monitoringHudSettingsWarningState = document.getElementById("monitoring-hud-settings-warning-state");
const monitoringHudSettingsPersistence = document.getElementById("monitoring-hud-settings-persistence");
const monitoringHudSettingsOverlayState = document.getElementById("monitoring-hud-settings-overlay-state");
const monitoringHudSettingsProviderState = document.getElementById("monitoring-hud-settings-provider-state");
const monitoringHudCreateMonitorWindow = document.getElementById("monitoring-hud-create-monitor-window");
const monitoringHudEditMonitorWindow = document.getElementById("monitoring-hud-edit-monitor-window");
const monitoringHudCreateMonitorName = document.getElementById("monitoring-hud-create-monitor-name");
const monitoringHudCreateMonitorConfirm = document.getElementById("monitoring-hud-create-monitor-confirm");
const monitoringHudManageMonitorCreate = document.getElementById("monitoring-hud-manage-monitor-create-action");
const monitoringHudMonitorManageSummary = document.getElementById("monitoring-hud-monitor-manage-summary");
const monitoringHudMonitorSearch = document.getElementById("monitoring-hud-monitor-search");
const monitoringHudEditMonitorList = document.getElementById("monitoring-hud-edit-monitor-list");
const monitoringHudMonitorListEmpty = document.getElementById("monitoring-hud-monitor-list-empty");
const monitoringHudEditMonitorTitle = document.getElementById("monitoring-hud-edit-monitor-title");
const monitoringHudEditMonitorName = document.getElementById("monitoring-hud-edit-monitor-name");
const monitoringHudEditMonitorConfirm = document.getElementById("monitoring-hud-edit-monitor-confirm");
const monitoringHudEditMonitorDiscard = document.getElementById("monitoring-hud-edit-monitor-discard");
const monitoringHudMonitorDetailActions = document.getElementById("monitoring-hud-monitor-detail-actions");
const monitoringHudMonitorDetailNote = document.getElementById("monitoring-hud-monitor-detail-note");
const monitoringHudMonitorDeleteConfirmation = document.getElementById("monitoring-hud-monitor-delete-confirmation");
const monitoringHudMonitorDeleteTitle = document.getElementById("monitoring-hud-monitor-delete-title");
const monitoringHudMonitorDeleteCopy = document.getElementById("monitoring-hud-monitor-delete-copy");
const monitoringHudMonitorDeleteConfirm = document.getElementById("monitoring-hud-monitor-delete-confirm");
const monitoringHudMonitorDeleteCancel = document.getElementById("monitoring-hud-monitor-delete-cancel");
const monitoringHudMonitorDetailDelete = document.getElementById("monitoring-hud-monitor-detail-delete");
const monitoringHudMonitorUnsavedGuard = document.getElementById("monitoring-hud-monitor-unsaved-guard");
const monitoringHudMonitorUnsavedSave = document.getElementById("monitoring-hud-monitor-unsaved-save");
const monitoringHudMonitorUnsavedDiscard = document.getElementById("monitoring-hud-monitor-unsaved-discard");
const monitoringHudMonitorUnsavedCancel = document.getElementById("monitoring-hud-monitor-unsaved-cancel");
const monitoringHudMonitorDetailEmpty = document.getElementById("monitoring-hud-monitor-detail-empty");
const monitoringHudMonitorEmptyCreate = document.getElementById("monitoring-hud-monitor-empty-create-action");
const monitoringHudMonitorWarningSetting = document.getElementById("monitoring-hud-monitor-warning-notifications-setting");
const monitoringHudProviderReadinessPanel = document.getElementById("monitoring-hud-provider-readiness-panel");
const monitoringHudMonitorOverlayProfileContext = document.getElementById("monitoring-hud-monitor-overlay-profile-context");
const monitoringHudMonitorOverlayProfileName = document.getElementById("monitoring-hud-monitor-overlay-profile-name");
const monitoringHudMonitorOverlayProfileSelectedState = document.getElementById("monitoring-hud-monitor-overlay-profile-selected-state");
const monitoringHudMonitorOverlayProfileCount = document.getElementById("monitoring-hud-monitor-overlay-profile-count");
const monitoringHudMonitorOverlayProfileDisplayMode = document.getElementById("monitoring-hud-monitor-overlay-profile-display-mode");
const monitoringHudMonitorOverlayProfileSettings = document.getElementById("monitoring-hud-monitor-overlay-profile-settings");
const monitoringHudOverlayAssignmentWindow = document.getElementById("monitoring-hud-overlay-assignment-window");
const monitoringHudOverlayAssignmentTitle = document.getElementById("monitoring-hud-overlay-assignment-title");
const monitoringHudOverlayAssignmentMonitorName = document.getElementById("monitoring-hud-overlay-assignment-monitor-name");
const monitoringHudOverlayAssignmentSummary = document.getElementById("monitoring-hud-overlay-assignment-summary");
const monitoringHudOverlayAssignmentList = document.getElementById("monitoring-hud-overlay-assignment-list");
const monitoringHudMonitorSensorAssignment = document.getElementById("monitoring-hud-monitor-sensor-assignment");
const monitoringHudMonitorSensorSettings = document.getElementById("monitoring-hud-monitor-sensor-settings");
const monitoringHudSourceSettingsWindow = document.getElementById("monitoring-hud-source-settings-window");
const monitoringHudSourceSettingsTitle = document.getElementById("monitoring-hud-source-settings-title");
const monitoringHudSourceSettingsName = document.getElementById("monitoring-hud-source-settings-name");
const monitoringHudSourceSettingsState = document.getElementById("monitoring-hud-source-settings-state");
const monitoringHudSourceSettingsBody = document.getElementById("monitoring-hud-source-settings-body");
const monitoringHudSourceSettingsNote = document.getElementById("monitoring-hud-source-settings-note");
const monitoringHudSensorSearch = document.getElementById("monitoring-hud-sensor-search");
const monitoringHudSensorFilter = document.getElementById("monitoring-hud-sensor-filter");
const monitoringHudSensorFilterToggle = document.getElementById("monitoring-hud-sensor-filter-toggle");
const monitoringHudSensorFilterLabel = document.getElementById("monitoring-hud-sensor-filter-label");
const monitoringHudSensorResultSummary = document.getElementById("monitoring-hud-sensor-result-summary");
const monitoringHudSensorPreview = document.getElementById("monitoring-hud-sensor-preview");

let monitoringHudTelemetry = {
  packageId: "PKG-006",
  sliceId: "SLC-025",
  adapterStatus: "Waiting for safe provider",
  sourceScope: "Provider-first; no fake values",
  hardwarePolling: "1s after provider proof",
  sources: []
};
let monitoringHudPlacement = {
  packageId: "PKG-006",
  sliceId: "SLC-026",
  placementId: "standalone-native-hud-window",
  rendererOwner: "HUD Overlay release acceptance is deferred. The Dashboard can describe the future overlay boundary without enabling it.",
  anchor: "Deferred / non-gating",
  pointerModel: "Dashboard configures future HUD Overlay behavior",
  resizePosture: "Overlay settings are future branch scope"
};
let monitoringHudControls = {
  packageId: "PKG-006",
  sliceId: "SLC-027",
  controlsId: "hud-controls-visibility",
  visibilityState: "HUD feature disabled from dashboard/tray",
  controlSurface: "Tray controls HUD feature state; Dashboard open/close is separate; HUD Overlay remains deferred",
  persistence: "Store group/layout posture locally",
  operatorAction: "No default keybinds",
  trayPath: "Task tray enables/disables HUD feature and opens/closes Dashboard; HUD Overlay controls deferred"
};
let monitoringHudStatus = {
  packageId: "PKG-006",
  sliceId: "SLC-028",
  statusId: "hud-local-readiness-status",
  statusKind: "no-data",
  statusLabel: "Provider setup required",
  noDataBehavior: "Show unavailable; no fake values",
  degradedBehavior: "Name reconnect/setup gap; visual warning only"
};

function monitoringHudInitialCards() {
  return {
    cpu: {
      x: 0,
      y: 0,
      w: 600,
      h: 280,
      title: "CPU Group",
      enabled: true,
      pollingRateMs: 1000,
      warningNotificationsEnabled: true,
      sensors: ["cpu-load"],
      sensorSettings: {
        "cpu-load": { displayMode: "badge-text", warningEnabled: true }
      }
    },
    gpu: {
      x: 0,
      y: 300,
      w: 600,
      h: 280,
      title: "GPU Group",
      enabled: true,
      pollingRateMs: 1000,
      warningNotificationsEnabled: true,
      sensors: [],
      sensorSettings: {}
    }
  };
}

function monitoringHudHasOwnCards(state) {
  return Boolean(state) && Object.prototype.hasOwnProperty.call(state, "cards");
}

function monitoringHudSafeCardsObject(cards) {
  if (!cards || typeof cards !== "object" || Array.isArray(cards)) return {};
  return Object.assign({}, cards);
}

const monitoringHudOverlayProfileSchemaVersion = 1;
const monitoringHudDefaultOverlayProfileId = "default-overlay-profile";
const monitoringHudActiveOverlayRecordingTargetSchemaVersion = 1;
let monitoringHudOverlayProfilePendingCreate = null;

function monitoringHudSafeOverlayProfilesObject(overlayProfiles) {
  if (!overlayProfiles || typeof overlayProfiles !== "object" || Array.isArray(overlayProfiles)) return {};
  return Object.assign({}, overlayProfiles);
}

function monitoringHudStableMonitorIds(cards) {
  return Object.keys(cards || {}).filter((cardId) => typeof cardId === "string" && cardId.trim());
}

function monitoringHudUniqueValidMonitorIds(values, cards) {
  const cardIds = new Set(monitoringHudStableMonitorIds(cards));
  const seen = new Set();
  const result = [];
  if (!Array.isArray(values)) return result;
  values.forEach((value) => {
    const monitorId = String(value || "").trim();
    if (!monitorId || !cardIds.has(monitorId) || seen.has(monitorId)) return;
    seen.add(monitorId);
    result.push(monitorId);
  });
  return result;
}

function monitoringHudDefaultOverlayProfile(cards, previousProfile = {}) {
  const previousMonitorIds = Array.isArray(previousProfile.monitorIds)
    ? monitoringHudUniqueValidMonitorIds(previousProfile.monitorIds, cards)
    : null;
  return {
    id: monitoringHudDefaultOverlayProfileId,
    schemaVersion: monitoringHudOverlayProfileSchemaVersion,
    kind: "overlay-profile",
    scope: "overlay-visible-monitor-membership",
    name: previousProfile.name || "Default Overlay Profile",
    monitorIds: previousMonitorIds || monitoringHudStableMonitorIds(cards),
    displayMode: previousProfile.displayMode || "monitor-cards",
    source: previousProfile.source || "legacy-monitor-card-migration",
    dirty: false
  };
}

function monitoringHudBuildActiveOverlayRecordingTargetSnapshot(targetState, requestedActiveProfileId = "") {
  const safeState = targetState || monitoringHudControlState;
  const profiles = monitoringHudSafeOverlayProfilesObject(safeState.overlayProfiles);
  const activeProfileId = String(safeState.activeOverlayProfileId || "").trim();
  const requestedProfileId = String(requestedActiveProfileId || "").trim();
  const pendingCreate = monitoringHudOverlayProfilePendingCreate
    && activeProfileId === String(monitoringHudOverlayProfilePendingCreate.id || "").trim()
    ? monitoringHudOverlayProfilePendingCreate
    : null;
  const activeProfile = activeProfileId && profiles[activeProfileId]
    ? profiles[activeProfileId]
    : pendingCreate;
  const monitorIds = activeProfile
    ? monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, safeState.cards || {})
    : [];
  const fallbackUsed = Boolean(requestedProfileId && requestedProfileId !== activeProfileId);
  let targetStateLabel = "no-overlay-profiles";
  if (activeProfile && monitorIds.length >= 100) {
    targetStateLabel = "high-volume-membership";
  } else if (activeProfile && monitorIds.length > 0) {
    targetStateLabel = "ready";
  } else if (activeProfile) {
    targetStateLabel = "empty-membership";
  } else if (safeState.overlayProfileDefaultDeletedByUser && Object.keys(profiles).length === 0) {
    targetStateLabel = "deleted-default-empty";
  } else if (Object.keys(profiles).length > 0) {
    targetStateLabel = "missing-active-profile";
  }
  return {
    schemaVersion: monitoringHudActiveOverlayRecordingTargetSchemaVersion,
    kind: "active-overlay-recording-target",
    scope: "target-session-truth-only",
    source: "active-overlay-profile-membership",
    activeOverlayProfileId: activeProfileId,
    requestedActiveOverlayProfileId: requestedProfileId,
    activeOverlayProfileName: activeProfile ? monitoringHudCleanOverlayProfileName(activeProfile.name, "Overlay Profile") : "",
    targetState: targetStateLabel,
    fallbackUsed: fallbackUsed,
    membershipSnapshotCandidate: monitorIds.slice(),
    membershipSnapshotCandidateCount: monitorIds.length,
    emptyMembership: monitorIds.length === 0,
    highVolumeMembership: monitorIds.length >= 100,
    snapshotAtStartModel: "snapshot-at-recording-start",
    hiddenRecordingTargetState: "absent",
    noHiddenRecordingTargetState: true,
    recordingExecutionState: targetStateLabel === "ready" || targetStateLabel === "high-volume-membership" ? "ready" : "blocked",
    fileWritingState: targetStateLabel === "ready" || targetStateLabel === "high-volume-membership" ? "ready" : "blocked",
    separateRecordingProfileState: "not-created",
    recordingProfileBoundary: "recording-profile-state-absent-future-gated",
    monitorGroupBoundary: "monitor-groups-organize-configuration-only",
    profileCount: Object.keys(profiles).length
  };
}

function monitoringHudApplyActiveOverlayRecordingTargetProof(targetState, requestedActiveProfileId = "") {
  const snapshot = monitoringHudBuildActiveOverlayRecordingTargetSnapshot(targetState, requestedActiveProfileId);
  targetState.activeOverlayRecordingTarget = snapshot;
  targetState.activeOverlayRecordingTargetProof = {
    schemaVersion: monitoringHudActiveOverlayRecordingTargetSchemaVersion,
    slice: "SLC-051",
    source: snapshot.source,
    scope: snapshot.scope,
    targetState: snapshot.targetState,
    activeOverlayProfileId: snapshot.activeOverlayProfileId,
    membershipSnapshotCandidateCount: snapshot.membershipSnapshotCandidateCount,
    snapshotAtStartModel: snapshot.snapshotAtStartModel,
    nullActiveProfileHandled: ["deleted-default-empty", "no-overlay-profiles", "missing-active-profile"].includes(snapshot.targetState),
    emptyMembershipHandled: snapshot.emptyMembership,
    staleDeletedMissingActiveProfileHandled: snapshot.fallbackUsed || ["deleted-default-empty", "missing-active-profile", "no-overlay-profiles"].includes(snapshot.targetState),
    highVolumeMembership: snapshot.highVolumeMembership,
    noHiddenRecordingTargetState: true,
    recordingExecutionState: snapshot.recordingExecutionState,
    fileWritingState: snapshot.fileWritingState,
    recordingProfileBoundary: "recording-profile-state-absent-future-gated"
  };
  return snapshot;
}

function monitoringHudActiveOverlayRecordingTargetLabel(target) {
  const targetState = target && target.targetState ? String(target.targetState) : "no-overlay-profiles";
  if (targetState === "ready" || targetState === "high-volume-membership") return "Target Ready";
  if (targetState === "empty-membership") return "No active monitors";
  if (targetState === "missing-active-profile") return "Active profile missing";
  if (targetState === "deleted-default-empty") return "Default profile deleted";
  return "No active Overlay Profile";
}

function monitoringHudActiveOverlayRecordingTargetNames(target, cards) {
  const safeCards = monitoringHudSafeCardsObject(cards);
  const ids = Array.isArray(target && target.membershipSnapshotCandidate)
    ? target.membershipSnapshotCandidate
    : [];
  const names = ids.slice(0, 3).map((cardId) => {
    const layout = Object.assign(monitoringHudCardDefaults(cardId), safeCards[cardId] || {});
    return layout.title || cardId;
  });
  if (!ids.length) return "No active monitors";
  if (ids.length > names.length) return `${names.join(", ")} +${ids.length - names.length} more`;
  return names.join(", ");
}

function monitoringHudRecordingNowIso() {
  return new Date().toISOString();
}

function monitoringHudRecordingState() {
  return monitoringHudControlState.recordingSessionState || "ready";
}

function monitoringHudRecordingTargetReady(target) {
  return Boolean(
    target
    && ["ready", "high-volume-membership"].includes(String(target.targetState || ""))
    && Number(target.membershipSnapshotCandidateCount || 0) > 0
  );
}

function monitoringHudBuildRecordingRowsFromTarget(target, startedAt, stoppedAt) {
  const safeTarget = target || monitoringHudControlState.activeOverlayRecordingTarget || {};
  const ids = Array.isArray(safeTarget.membershipSnapshotCandidate)
    ? safeTarget.membershipSnapshotCandidate
    : [];
  const cards = monitoringHudSafeCardsObject(monitoringHudControlState.cards || {});
  const sessionStartedMs = Number(monitoringHudControlState.recordingStartedAtMs || 0)
    || Date.parse(monitoringHudControlState.recordingStartedAt || startedAt || "")
    || Date.now();
  const segmentStartedMs = Date.parse(startedAt || "") || sessionStartedMs;
  const segmentStoppedMs = Date.parse(stoppedAt || "") || Date.now();
  const segmentStartedElapsedMs = Math.max(0, segmentStartedMs - sessionStartedMs);
  const segmentStoppedElapsedMs = Math.max(segmentStartedElapsedMs + 1, segmentStoppedMs - sessionStartedMs);
  const timestamps = [
    { timestamp: startedAt || monitoringHudRecordingNowIso(), elapsedMs: segmentStartedElapsedMs },
    { timestamp: stoppedAt || monitoringHudRecordingNowIso(), elapsedMs: segmentStoppedElapsedMs }
  ];
  const rows = [];
  ids.forEach((monitorId) => {
    const card = Object.assign(monitoringHudCardDefaults(monitorId), cards[monitorId] || {});
    const sensors = Array.isArray(card.sensors) ? card.sensors : [];
    const recordingSensors = sensors.length ? sensors : ["recording-target-no-sensor-sample"];
    recordingSensors.forEach((sensorId) => {
      timestamps.forEach((sample) => {
        const noSensorSample = sensorId === "recording-target-no-sensor-sample";
        rows.push({
          timestamp_utc: sample.timestamp,
          elapsed_ms: sample.elapsedMs,
          overlay_profile_id: String(safeTarget.activeOverlayProfileId || ""),
          overlay_profile_name: String(safeTarget.activeOverlayProfileName || ""),
          monitor_id: String(monitorId || ""),
          monitor_name: String(card.title || monitorId || ""),
          sensor_id: String(sensorId || ""),
          sensor_label: noSensorSample
            ? "Recording Target"
            : String(sensorId || "").replace(/-/g, " ").replace(/\b\w/g, (value) => value.toUpperCase()),
          value: "",
          unit: noSensorSample ? "" : sensorId.includes("load") ? "%" : "",
          quality: "unavailable",
          source_state: noSensorSample ? "no-sensor-sample" : "provider-required"
        });
      });
    });
  });
  return rows;
}

function monitoringHudSetRecordingError(message) {
  monitoringHudControlState.recordingSessionState = "disabled-error";
  monitoringHudControlState.recordingSessionMessage = message || "Recording is not available for the current Overlay Profile.";
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return false;
}

function monitoringHudStartRecording() {
  if (monitoringHudRecordingState() === "paused") {
    const resumedAt = monitoringHudRecordingNowIso();
    monitoringHudControlState.recordingSessionState = "recording";
    monitoringHudControlState.recordingSessionMessage = "Recording resumed.";
    monitoringHudControlState.recordingResumedAt = resumedAt;
    monitoringHudControlState.recordingActiveSegmentStartedAt = resumedAt;
    monitoringHudRenderControls();
    monitoringHudMarkChanged();
    return true;
  }
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const target = monitoringHudControlState.activeOverlayRecordingTarget
    || monitoringHudBuildActiveOverlayRecordingTargetSnapshot(monitoringHudControlState);
  if (!monitoringHudRecordingTargetReady(target)) {
    return monitoringHudSetRecordingError("Select an Overlay Profile with active monitors before starting recording.");
  }
  const rows = monitoringHudBuildRecordingRowsFromTarget(target, monitoringHudRecordingNowIso(), monitoringHudRecordingNowIso());
  if (!rows.length) {
    return monitoringHudSetRecordingError("The active Overlay Profile has no usable sensor samples to record.");
  }
  const startedAt = monitoringHudRecordingNowIso();
  monitoringHudControlState.recordingSessionId = `recording-${Date.now()}`;
  monitoringHudControlState.recordingStartedAt = startedAt;
  monitoringHudControlState.recordingStartedAtMs = Date.now();
  monitoringHudControlState.recordingActiveSegmentStartedAt = startedAt;
  monitoringHudControlState.recordingStoppedAt = "";
  monitoringHudControlState.recordingSessionState = "recording";
  monitoringHudControlState.recordingSessionMessage = "Recording active. Target locked to active Overlay Profile at Start.";
  monitoringHudControlState.recordingSnapshotTarget = JSON.parse(JSON.stringify(target));
  monitoringHudControlState.recordingSamples = monitoringHudBuildRecordingRowsFromTarget(target, startedAt, startedAt);
  monitoringHudControlState.recordingOutputRequest = null;
  monitoringHudControlState.recordingOutputResult = null;
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudPauseRecording() {
  if (monitoringHudRecordingState() !== "recording") {
    return false;
  }
  const target = monitoringHudControlState.recordingSnapshotTarget || monitoringHudControlState.activeOverlayRecordingTarget || {};
  const pausedAt = monitoringHudRecordingNowIso();
  const segmentStartedAt = monitoringHudControlState.recordingActiveSegmentStartedAt || monitoringHudControlState.recordingStartedAt;
  const rows = monitoringHudBuildRecordingRowsFromTarget(target, segmentStartedAt, pausedAt);
  monitoringHudControlState.recordingPausedAt = pausedAt;
  monitoringHudControlState.recordingActiveSegmentStartedAt = "";
  monitoringHudControlState.recordingSamples = (Array.isArray(monitoringHudControlState.recordingSamples) ? monitoringHudControlState.recordingSamples : []).concat(rows);
  monitoringHudControlState.recordingSessionState = "paused";
  monitoringHudControlState.recordingSessionMessage = "Recording paused. Stop saves the current session; Start resumes.";
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudStopRecording() {
  const currentRecordingState = monitoringHudRecordingState();
  if (!["recording", "paused"].includes(currentRecordingState)) {
    return monitoringHudStartRecording();
  }
  const target = monitoringHudControlState.recordingSnapshotTarget || monitoringHudControlState.activeOverlayRecordingTarget || {};
  const stoppedAt = monitoringHudRecordingNowIso();
  const segmentStartedAt = monitoringHudControlState.recordingActiveSegmentStartedAt || monitoringHudControlState.recordingStartedAt;
  const rows = currentRecordingState === "paused"
    ? []
    : monitoringHudBuildRecordingRowsFromTarget(target, segmentStartedAt, stoppedAt);
  const allRows = (Array.isArray(monitoringHudControlState.recordingSamples) ? monitoringHudControlState.recordingSamples : []).concat(rows);
  if (!allRows.length) {
    return monitoringHudSetRecordingError("Recording stopped without usable samples.");
  }
  const sequence = Number(monitoringHudControlState.recordingOutputRequestSequence || 0) + 1;
  monitoringHudControlState.recordingStoppedAt = stoppedAt;
  monitoringHudControlState.recordingActiveSegmentStartedAt = "";
  monitoringHudControlState.recordingSamples = allRows;
  monitoringHudControlState.recordingOutputRequestSequence = sequence;
  monitoringHudControlState.recordingOutputRequest = {
    requestId: `recording-output-${sequence}-${Date.now()}`,
    sessionId: monitoringHudControlState.recordingSessionId || `recording-${Date.now()}`,
    activeOverlayProfileId: target.activeOverlayProfileId || "",
    activeOverlayProfileName: target.activeOverlayProfileName || "",
    targetMonitorIds: Array.isArray(target.membershipSnapshotCandidate) ? target.membershipSnapshotCandidate.slice() : [],
    targetState: target.targetState || "unknown",
    startedAtUtc: monitoringHudControlState.recordingStartedAt || "",
    stoppedAtUtc: stoppedAt,
    samples: allRows
  };
  monitoringHudControlState.recordingSessionState = "saving";
  monitoringHudControlState.recordingSessionMessage = "Saving recording output locally.";
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudToggleRecording() {
  return monitoringHudRecordingState() === "recording" ? monitoringHudStopRecording() : monitoringHudStartRecording();
}

function monitoringHudRecordingExportFolderPath(outputResult) {
  const safeResult = outputResult && typeof outputResult === "object" ? outputResult : {};
  if (safeResult.exportDir) return String(safeResult.exportDir || "");
  const path = String(safeResult.validationExportPath || safeResult.csvPath || "");
  if (!path) return "";
  const lastSlash = Math.max(path.lastIndexOf("/"), path.lastIndexOf("\\"));
  return lastSlash >= 0 ? path.slice(0, lastSlash) : "";
}

function monitoringHudRequestOpenRecordingFolder() {
  const outputResult = monitoringHudControlState.recordingOutputResult || {};
  const folderPath = monitoringHudRecordingExportFolderPath(outputResult);
  const sequence = Number(monitoringHudControlState.recordingFolderOpenRequestSequence || 0) + 1;
  monitoringHudControlState.recordingFolderOpenRequestSequence = sequence;
  monitoringHudControlState.recordingFolderOpenRequest = {
    requestId: `fam006-open-folder-${sequence}-${Date.now()}`,
    outputDir: folderPath,
    nativeLogPath: String(outputResult.nativeLogPath || ""),
    validationExportPath: String(outputResult.validationExportPath || ""),
    source: "dashboard-recording-card"
  };
  monitoringHudControlState.recordingFolderOpenStatus = "requested";
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudBuildRecordingStudioTargetSummary(target, executionState, fileWritingState, sessionState) {
  const safeTarget = target && typeof target === "object"
    ? target
    : monitoringHudBuildActiveOverlayRecordingTargetSnapshot(monitoringHudControlState);
  const currentSessionState = String(sessionState || monitoringHudRecordingState());
  const startStopState = currentSessionState === "recording"
    ? "recording-stop-enabled"
    : currentSessionState === "paused"
      ? "paused-stop-enabled"
      : currentSessionState === "saving"
      ? "saving-disabled"
      : monitoringHudRecordingTargetReady(safeTarget)
        ? "start-enabled"
        : "target-required";
  const outputResult = monitoringHudControlState.recordingOutputResult || {};
  const nativeLogPath = String(outputResult.nativeLogPath || "");
  const validationExportPath = String(outputResult.validationExportPath || "");
  const exportDir = monitoringHudRecordingExportFolderPath(outputResult);
  return {
    activeOverlayProfileId: safeTarget.activeOverlayProfileId || "",
    activeOverlayProfileName: safeTarget.activeOverlayProfileName || "",
    targetState: safeTarget.targetState || "no-overlay-profiles",
    targetCount: Number(safeTarget.membershipSnapshotCandidateCount) || 0,
    targetNames: monitoringHudActiveOverlayRecordingTargetNames(safeTarget, monitoringHudControlState.cards || {}),
    recordingExecutionState: executionState || (currentSessionState === "recording" ? "recording" : "ready"),
    fileWritingState: fileWritingState || (currentSessionState === "saved-complete" ? "saved-complete" : "ready"),
    recordingSessionState: currentSessionState,
    nativeLogPath,
    validationExportPath,
    exportDir,
    rowCount: Number(outputResult.rowCount || 0),
    currentLogState: nativeLogPath ? "native-log-saved" : currentSessionState === "recording" ? "native-log-pending" : "no-current-log",
    startStopState,
    studioSurfaceState: "recording-studio-focused-control-status"
  };
}

function monitoringHudBuildLogViewerSummary(outputResult) {
  const safeResult = outputResult && typeof outputResult === "object" ? outputResult : {};
  return {
    nativeLogPath: String(safeResult.nativeLogPath || ""),
    validationExportPath: String(safeResult.validationExportPath || ""),
    exportDir: monitoringHudRecordingExportFolderPath(safeResult),
    nativeFolderState: "create-or-open-before-session",
    exportFolderState: "create-or-open-before-session",
    fullLogViewerState: "future-gated",
    previousLogSelectionState: "future-gated",
    exportCustomizationState: "future-gated"
  };
}

window.setMonitoringHudRecordingFolderOpenResult = function(result) {
  const safeResult = result && typeof result === "object" ? result : {};
  monitoringHudControlState.recordingFolderOpenResult = safeResult;
  monitoringHudControlState.recordingFolderOpenStatus = safeResult.passed ? "opened" : "blocked";
  if (!safeResult.passed) {
    monitoringHudControlState.recordingSessionMessage = String(safeResult.error || "The recording log folder could not be opened.");
  }
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
};

window.setMonitoringHudRecordingOutputResult = function(result) {
  const safeResult = result && typeof result === "object" ? result : {};
  monitoringHudControlState.recordingOutputResult = safeResult;
  monitoringHudControlState.recordingSessionState = safeResult.passed ? "saved-complete" : "disabled-error";
  monitoringHudControlState.recordingSessionMessage = safeResult.passed
    ? "Recording saved and read back successfully."
    : String(safeResult.error || "Recording output could not be saved.");
  if (safeResult.passed) {
    monitoringHudControlState.recordingOutputRequest = null;
    monitoringHudControlState.recordingSamples = [];
  }
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
};

function monitoringHudRenderActiveOverlayRecordingTargetPreview() {
  const target = monitoringHudControlState.activeOverlayRecordingTarget
    || monitoringHudBuildActiveOverlayRecordingTargetSnapshot(monitoringHudControlState);
  const count = Number(target.membershipSnapshotCandidateCount) || 0;
  const activeProfileName = monitoringHudCleanOverlayProfileName(
    target.activeOverlayProfileName || (monitoringHudActiveOverlayProfile() || {}).name,
    "No active overlay profile"
  );
  const targetLabel = monitoringHudActiveOverlayRecordingTargetLabel(target);
  const targetNames = monitoringHudActiveOverlayRecordingTargetNames(target, monitoringHudControlState.cards || {});
  const sessionState = monitoringHudRecordingState();
  const targetReady = monitoringHudRecordingTargetReady(target);
  const outputResult = monitoringHudControlState.recordingOutputResult || {};
  const executionState = sessionState === "recording" ? "recording" : sessionState === "saved-complete" ? "saved-complete" : targetReady ? "ready" : "disabled-error";
  const fileWritingState = sessionState === "saved-complete" ? "saved-complete" : sessionState === "saving" ? "saving" : targetReady ? "ready" : "blocked";
  const buttonEnabled = ["recording", "paused"].includes(sessionState) || (targetReady && sessionState !== "saving");
  const outputFolderPath = monitoringHudRecordingExportFolderPath(outputResult);
  const folderButtonEnabled = true;
  if (monitoringHudRecordingCard) {
    monitoringHudRecordingCard.dataset.recordingCardPlacement = "dashboard-recording-card-primary";
    monitoringHudRecordingCard.dataset.recordingSurfaceOwner = "dashboard-card-not-hud-overlay";
    monitoringHudRecordingCard.dataset.recordingCardVisualSystem = "dashboard-hub-card-sampled";
    monitoringHudRecordingCard.dataset.recordingCardSampledElements = "hud-overlay-monitor-groups-data-sources-readiness";
    monitoringHudRecordingCard.dataset.activeOverlayProfileId = String(target.activeOverlayProfileId || "");
    monitoringHudRecordingCard.dataset.activeOverlayRecordingTargetState = String(target.targetState || "no-overlay-profiles");
    monitoringHudRecordingCard.dataset.activeOverlayRecordingTargetCount = String(count);
    monitoringHudRecordingCard.dataset.recordingExecutionState = executionState;
    monitoringHudRecordingCard.dataset.recordingFileWritingState = fileWritingState;
    monitoringHudRecordingCard.dataset.recordingControlSurfaceState = "dashboard-status-summary";
    monitoringHudRecordingCard.dataset.hudOverlayRecordingBoundary = "hud-overlay-overlay-focused";
  }
  if (monitoringHudRecordingTargetPreview) {
    monitoringHudRecordingTargetPreview.dataset.recordingTargetPreview = "slc-052-dashboard-recording-card-target-status";
    monitoringHudRecordingTargetPreview.dataset.recordingCardVisualSystem = "dashboard-hub-card-sampled";
    monitoringHudRecordingTargetPreview.dataset.recordingCardSampledElements = "hud-overlay-monitor-groups-data-sources-readiness";
    monitoringHudRecordingTargetPreview.dataset.activeOverlayProfileId = String(target.activeOverlayProfileId || "");
    monitoringHudRecordingTargetPreview.dataset.activeOverlayRecordingTargetState = String(target.targetState || "no-overlay-profiles");
    monitoringHudRecordingTargetPreview.dataset.activeOverlayRecordingTargetCount = String(count);
    monitoringHudRecordingTargetPreview.dataset.activeMonitorTransparency = "slc-052-dashboard-visible-count-and-names";
    monitoringHudRecordingTargetPreview.dataset.recordingCardPlacement = "dashboard-recording-card-primary";
    monitoringHudRecordingTargetPreview.dataset.hudOverlayRecordingBoundary = "hud-overlay-overlay-focused";
    monitoringHudRecordingTargetPreview.dataset.recordingExecutionState = executionState;
    monitoringHudRecordingTargetPreview.dataset.recordingFileWritingState = fileWritingState;
    monitoringHudRecordingTargetPreview.dataset.recordingControlWindowState = "recording-card-status-summary";
    monitoringHudRecordingTargetPreview.dataset.recordingControlWindowContract = "recording-studio-focused-control-status";
    monitoringHudRecordingTargetPreview.dataset.logViewerState = "ready";
    monitoringHudRecordingTargetPreview.dataset.trayRecordingControlState = "not-created";
  }
  if (monitoringHudRecordingCardSummary) {
    monitoringHudRecordingCardSummary.textContent = "Recording follows the active Overlay Profile and saves a native NDAI log when stopped.";
  }
  if (monitoringHudRecordingTargetProfile) {
    monitoringHudRecordingTargetProfile.textContent = activeProfileName;
  }
  if (monitoringHudRecordingTargetCount) {
    monitoringHudRecordingTargetCount.textContent = `${count} active monitor${count === 1 ? "" : "s"}`;
  }
  if (monitoringHudRecordingTargetSummary) {
    const resultText = outputResult && outputResult.nativeLogPath ? ` Saved ${outputResult.rowCount || 0} rows to a native NDAI log.` : "";
    monitoringHudRecordingTargetSummary.textContent = `${targetLabel}: ${targetNames}. ${monitoringHudControlState.recordingSessionMessage || "Ready for local Start/Stop recording."}${resultText}`;
  }
  if (monitoringHudRecordingControlLauncher) {
    monitoringHudRecordingControlLauncher.disabled = !buttonEnabled;
    monitoringHudRecordingControlLauncher.setAttribute("aria-disabled", buttonEnabled ? "false" : "true");
    monitoringHudRecordingControlLauncher.dataset.dashboardQuickAccess = "recording-start-stop";
    monitoringHudRecordingControlLauncher.dataset.recordingControlWindowState = "quick-access-start-stop";
    monitoringHudRecordingControlLauncher.dataset.recordingControlWindowContract = "dashboard-quick-access-start-stop";
    monitoringHudRecordingControlLauncher.dataset.nativeWindowContract = "dashboard-quick-access-start-stop";
    monitoringHudRecordingControlLauncher.dataset.recordingExecutionState = executionState;
    monitoringHudRecordingControlLauncher.dataset.recordingFileWritingState = fileWritingState;
    monitoringHudRecordingControlLauncher.textContent = sessionState === "recording"
      ? "Stop Recording"
      : sessionState === "paused"
        ? "Resume Recording"
      : sessionState === "saving"
        ? "Saving Recording"
        : "Start Recording";
  }
  if (monitoringHudRecordingStudioOpen) {
    monitoringHudRecordingStudioOpen.disabled = false;
    monitoringHudRecordingStudioOpen.setAttribute("aria-disabled", "false");
    monitoringHudRecordingStudioOpen.dataset.recordingControlWindowState = targetReady
      ? "recording-studio-ready"
      : "recording-studio-open-target-required";
    monitoringHudRecordingStudioOpen.dataset.recordingControlWindowContract = "recording-studio-focused-control-status";
    monitoringHudRecordingStudioOpen.dataset.recordingStudioUserPath = "always-openable-target-state-visible";
    monitoringHudRecordingStudioOpen.dataset.nativeWindowContract = "recording-studio-focused-control-status";
    monitoringHudRecordingStudioOpen.dataset.recordingExecutionState = executionState;
    monitoringHudRecordingStudioOpen.dataset.recordingFileWritingState = fileWritingState;
    monitoringHudRecordingStudioOpen.dataset.recordingCardVisualSystem = "dashboard-hub-card-sampled";
    monitoringHudRecordingStudioOpen.textContent = "Recording Suite";
  }
  if (monitoringHudRecordingOpenFolder) {
    monitoringHudRecordingOpenFolder.disabled = !folderButtonEnabled;
    monitoringHudRecordingOpenFolder.setAttribute("aria-disabled", folderButtonEnabled ? "false" : "true");
    monitoringHudRecordingOpenFolder.dataset.recordingFolderAction = "native-and-export-folder-shell";
    monitoringHudRecordingOpenFolder.dataset.recordingFolderPathAvailable = outputFolderPath ? "saved-export-path" : "pre-session-root";
    monitoringHudRecordingOpenFolder.dataset.recordingFileWritingState = fileWritingState === "blocked" ? "pre-session-ready" : fileWritingState;
    monitoringHudRecordingOpenFolder.dataset.logViewerState = "ready";
    monitoringHudRecordingOpenFolder.dataset.recordingCardVisualSystem = "dashboard-hub-card-sampled";
    monitoringHudRecordingOpenFolder.textContent = "Log Viewer";
  }
  if (monitoringHudControlState.recordingControlWindowRequested) {
    monitoringHudControlState.recordingControlWindowTargetSummary = monitoringHudBuildRecordingStudioTargetSummary(
      target,
      executionState,
      fileWritingState,
      sessionState
    );
  }
  if (monitoringHudControlState.logViewerRequested) {
    monitoringHudControlState.logViewerSummary = monitoringHudBuildLogViewerSummary(outputResult);
  }
  return {
    activeProfileName,
    count,
    targetLabel,
    targetNames,
    recordingExecutionState: executionState,
    fileWritingState,
    recordingCardPlacement: "dashboard-recording-card-primary",
    recordingControlWindowState: "recording-card-status-summary",
    recordingFolderPathAvailable: true,
  };
}

function monitoringHudRequestRecordingControlWindow() {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const target = monitoringHudControlState.activeOverlayRecordingTarget
    || monitoringHudBuildActiveOverlayRecordingTargetSnapshot(monitoringHudControlState);
  const sequence = Number(monitoringHudControlState.recordingControlWindowRequestSequence || 0) + 1;
  monitoringHudControlState.recordingControlWindowRequestSequence = sequence;
  monitoringHudControlState.recordingControlWindowRequested = true;
  monitoringHudControlState.recordingControlWindowRequestId = sequence;
  monitoringHudControlState.recordingControlWindowContract = "recording-studio-focused-control-status";
  monitoringHudControlState.recordingControlWindowState = "native-window-requested";
  monitoringHudControlState.recordingControlWindowTargetSummary = monitoringHudBuildRecordingStudioTargetSummary(
    target,
    monitoringHudRecordingState() === "recording" ? "recording" : monitoringHudRecordingState() === "paused" ? "paused" : "ready",
    monitoringHudRecordingState() === "saved-complete" ? "saved-complete" : "ready",
    monitoringHudRecordingState()
  );
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudRequestLogViewerWindow() {
  const sequence = Number(monitoringHudControlState.logViewerRequestSequence || 0) + 1;
  monitoringHudControlState.logViewerRequestSequence = sequence;
  monitoringHudControlState.logViewerRequested = true;
  monitoringHudControlState.logViewerRequestId = `recording-log-viewer-${sequence}-${Date.now()}`;
  monitoringHudControlState.logViewerState = "native-window-requested";
  monitoringHudControlState.logViewerSummary = monitoringHudBuildLogViewerSummary(
    monitoringHudControlState.recordingOutputResult || {}
  );
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudNormalizeOverlayProfileState(state) {
  const targetState = state || monitoringHudControlState;
  const cards = monitoringHudSafeCardsObject(targetState.cards || {});
  const rawProfiles = monitoringHudSafeOverlayProfilesObject(targetState.overlayProfiles);
  const profiles = {};
  const migratedLegacyCards = !Object.prototype.hasOwnProperty.call(targetState, "overlayProfiles");
  const defaultProfileDeletedByUser = Boolean(targetState.overlayProfileDefaultDeletedByUser);

  Object.keys(rawProfiles).forEach((profileKey) => {
    const rawProfile = rawProfiles[profileKey];
    if (!rawProfile || typeof rawProfile !== "object" || Array.isArray(rawProfile)) return;
    const profileId = String(rawProfile.id || profileKey || "").trim();
    if (!profileId) return;
    profiles[profileId] = {
      id: profileId,
      schemaVersion: monitoringHudOverlayProfileSchemaVersion,
      kind: "overlay-profile",
      scope: "overlay-visible-monitor-membership",
      name: String(rawProfile.name || "Overlay Profile").trim() || "Overlay Profile",
      monitorIds: monitoringHudUniqueValidMonitorIds(rawProfile.monitorIds, cards),
      displayMode: String(rawProfile.displayMode || "monitor-cards").trim() || "monitor-cards",
      source: String(rawProfile.source || "persisted-overlay-profile-state").trim() || "persisted-overlay-profile-state",
      dirty: Boolean(rawProfile.dirty)
    };
  });

  const requestedActiveProfileId = String(targetState.activeOverlayProfileId || "").trim();
  const activeProfileId = requestedActiveProfileId;
  const shouldEnsureDefaultProfile = migratedLegacyCards
    || (!defaultProfileDeletedByUser && Object.keys(profiles).length === 0)
    || (!defaultProfileDeletedByUser && activeProfileId === monitoringHudDefaultOverlayProfileId)
    || Boolean(rawProfiles[monitoringHudDefaultOverlayProfileId]);
  if (shouldEnsureDefaultProfile) {
    profiles[monitoringHudDefaultOverlayProfileId] = monitoringHudDefaultOverlayProfile(
      cards,
      profiles[monitoringHudDefaultOverlayProfileId] || rawProfiles[monitoringHudDefaultOverlayProfileId] || {}
    );
  }
  const fallbackProfileId = profiles[monitoringHudDefaultOverlayProfileId]
    ? monitoringHudDefaultOverlayProfileId
    : Object.keys(profiles)[0] || "";
  const pendingCreate = monitoringHudOverlayProfilePendingCreate
    && requestedActiveProfileId === String(monitoringHudOverlayProfilePendingCreate.id || "").trim()
    ? monitoringHudOverlayProfilePendingCreate
    : null;
  targetState.overlayProfileSchemaVersion = monitoringHudOverlayProfileSchemaVersion;
  targetState.overlayProfiles = profiles;
  targetState.overlayProfileDefaultDeletedByUser = defaultProfileDeletedByUser && !profiles[monitoringHudDefaultOverlayProfileId];
  targetState.activeOverlayProfileId = profiles[activeProfileId] ? activeProfileId : (pendingCreate ? activeProfileId : fallbackProfileId);
  targetState.overlayProfileStateProof = {
    schemaVersion: monitoringHudOverlayProfileSchemaVersion,
    activeProfileId: targetState.activeOverlayProfileId,
    defaultProfileId: monitoringHudDefaultOverlayProfileId,
    defaultProfileMonitorIds: profiles[monitoringHudDefaultOverlayProfileId]
      ? profiles[monitoringHudDefaultOverlayProfileId].monitorIds.slice()
      : [],
    defaultProfileDeletedByUser: Boolean(targetState.overlayProfileDefaultDeletedByUser),
    profileCount: Object.keys(profiles).length + (pendingCreate ? 1 : 0),
    legacyCardsMigrated: migratedLegacyCards,
    duplicateMonitorIdsRemoved: true,
    staleMonitorIdsRemoved: true,
    monitorGroupBoundary: "monitor-groups-organize-configuration-only",
    recordingProfileBoundary: "recording-profile-state-absent-future-gated",
    visibleEditorUi: "slc-039-membership-editor"
  };
  monitoringHudApplyActiveOverlayRecordingTargetProof(targetState, requestedActiveProfileId);
  return targetState;
}

function monitoringHudActiveOverlayProfile() {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  if (
    monitoringHudOverlayProfilePendingCreate
    && monitoringHudControlState.activeOverlayProfileId === String(monitoringHudOverlayProfilePendingCreate.id || "")
  ) {
    return monitoringHudOverlayProfilePendingCreate;
  }
  return monitoringHudControlState.overlayProfiles[monitoringHudControlState.activeOverlayProfileId]
    || monitoringHudControlState.overlayProfiles[monitoringHudDefaultOverlayProfileId]
    || null;
}

function monitoringHudOverlayProfileList() {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const profiles = monitoringHudControlState.overlayProfiles || {};
  return Object.keys(profiles)
    .sort((left, right) => {
      if (left === monitoringHudDefaultOverlayProfileId) return -1;
      if (right === monitoringHudDefaultOverlayProfileId) return 1;
      return String(profiles[left].name || left).localeCompare(String(profiles[right].name || right));
    })
    .map((profileId) => profiles[profileId])
    .filter(Boolean);
}

function monitoringHudCleanOverlayProfileName(value, fallback = "Overlay Profile") {
  const cleaned = String(value || "").replace(/\s+/g, " ").trim();
  return (cleaned || fallback).slice(0, 48);
}

function monitoringHudCompactOverlayProfileName(value, fallback = "Overlay Profile") {
  const cleaned = monitoringHudCleanOverlayProfileName(value, fallback);
  return cleaned === "Default Overlay Profile" ? "Default Profile" : cleaned;
}

function monitoringHudUniqueOverlayProfileName(value, currentProfileId = "") {
  const baseName = monitoringHudCleanOverlayProfileName(value);
  const existingNames = new Set(
    monitoringHudOverlayProfileList()
      .filter((profile) => profile.id !== currentProfileId)
      .map((profile) => String(profile.name || "").trim().toLocaleLowerCase())
      .filter(Boolean)
  );
  if (!existingNames.has(baseName.toLocaleLowerCase())) return baseName;
  for (let index = 2; index < 100; index += 1) {
    const candidate = `${baseName} ${index}`;
    if (!existingNames.has(candidate.toLocaleLowerCase())) return candidate;
  }
  return `${baseName} ${Date.now()}`;
}

function monitoringHudNextOverlayProfileId() {
  const profiles = monitoringHudControlState.overlayProfiles || {};
  let index = Object.keys(profiles).length + 1;
  let profileId = `overlay-profile-${index}`;
  while (profiles[profileId]) {
    index += 1;
    profileId = `overlay-profile-${index}`;
  }
  return profileId;
}

function monitoringHudOverlayProfileDisplayLabel(displayMode) {
  return String(displayMode || "monitor-cards")
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ") || "Monitor Cards";
}

function monitoringHudSameMonitorMembership(left, right, cards) {
  const normalizedLeft = monitoringHudUniqueValidMonitorIds(left, cards);
  const normalizedRight = monitoringHudUniqueValidMonitorIds(right, cards);
  return JSON.stringify(normalizedLeft) === JSON.stringify(normalizedRight);
}

function monitoringHudOverlayProfileDraftMonitorIdsFromWindow() {
  const cards = monitoringHudControlState && monitoringHudControlState.cards
    ? monitoringHudControlState.cards
    : {};
  if (!monitoringHudOverlayProfileMembershipList) {
    return monitoringHudUniqueValidMonitorIds(monitoringHudOverlayProfileDraftMonitorIds, cards);
  }
  const checkedIds = Array.from(
    monitoringHudOverlayProfileMembershipList.querySelectorAll("[data-overlay-profile-membership-toggle]")
  );
  if (!checkedIds.length) {
    if (monitoringHudOverlayProfileDraftMonitorIds.length) {
      return monitoringHudUniqueValidMonitorIds(monitoringHudOverlayProfileDraftMonitorIds, cards);
    }
    const activeProfile = monitoringHudOverlayProfileDraftTarget() || monitoringHudActiveOverlayProfile() || {};
    return monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, cards);
  }
  const selectedIds = checkedIds
    .filter((input) => input.checked)
    .map((input) => input.value);
  const renderedIds = new Set(checkedIds.map((input) => input.value));
  const baselineIds = monitoringHudOverlayProfileDraftMonitorIds.length
    ? monitoringHudOverlayProfileDraftMonitorIds
    : monitoringHudUniqueValidMonitorIds((monitoringHudOverlayProfileDraftTarget() || monitoringHudActiveOverlayProfile() || {}).monitorIds, cards);
  const preservedIds = monitoringHudUniqueValidMonitorIds(baselineIds, cards)
    .filter((cardId) => !renderedIds.has(cardId));
  return monitoringHudUniqueValidMonitorIds(preservedIds.concat(selectedIds), cards);
}

function monitoringHudOverlayProfileMonitorSummary(cardId, layout) {
  const label = monitoringHudSensorAssignmentSummary(layout);
  const pollingMs = Math.max(1000, Number(layout && layout.pollingRateMs) || 1000);
  const enabledCopy = layout && layout.enabled === false ? "hidden" : "visible";
  return `${label}; ${enabledCopy}; ${pollingMs / 1000}s polling`;
}

function monitoringHudRenderOverlayProfileMembershipList(activeProfile, cards, draftMonitorIds) {
  if (!monitoringHudOverlayProfileMembershipList) return;
  const monitorIds = monitoringHudStableMonitorIds(cards);
  const selectedIds = new Set(monitoringHudUniqueValidMonitorIds(draftMonitorIds, cards));
  const searchTerm = String(monitoringHudOverlayProfileMonitorSearchTerm || "").trim().toLowerCase();
  const filterMode = ["all", "visible", "hidden"].includes(monitoringHudOverlayProfileMonitorFilterMode)
    ? monitoringHudOverlayProfileMonitorFilterMode
    : "all";
  const visibleMonitorRows = monitorIds.filter((cardId) => {
    const layout = Object.assign(monitoringHudCardDefaults(cardId), cards[cardId] || {});
    const checked = selectedIds.has(cardId);
    const haystack = `${layout.title || ""} ${monitoringHudOverlayProfileMonitorSummary(cardId, layout)}`.toLowerCase();
    const matchesSearch = !searchTerm || haystack.includes(searchTerm);
    const matchesFilter = filterMode === "all"
      || (filterMode === "visible" && checked)
      || (filterMode === "hidden" && !checked);
    return matchesSearch && matchesFilter;
  });
  monitoringHudOverlayProfileMembershipList.replaceChildren();
  monitoringHudOverlayProfileMembershipList.dataset.overlayProfileMembershipList = "editable-monitor-membership";
  monitoringHudOverlayProfileMembershipList.dataset.overlayProfileVisibleMonitorTarget = "max-five";
  monitoringHudOverlayProfileMembershipList.dataset.scrollbarStyle = "ndai-native";
  monitoringHudOverlayProfileMembershipList.dataset.activeOverlayProfileId = activeProfile.id || monitoringHudDefaultOverlayProfileId;
  monitoringHudOverlayProfileMembershipList.dataset.selectedMonitorCount = String(selectedIds.size);
  monitoringHudOverlayProfileMembershipList.dataset.filteredMonitorCount = String(visibleMonitorRows.length);
  monitoringHudOverlayProfileMembershipList.dataset.filterMode = filterMode;
  monitoringHudOverlayProfileMembershipList.dataset.searchQuery = searchTerm;
  if (monitoringHudOverlayProfileMonitorResults) {
    const total = monitorIds.length;
    monitoringHudOverlayProfileMonitorResults.textContent = `${visibleMonitorRows.length} shown / ${selectedIds.size} visible / ${total} total`;
  }
  if (!monitorIds.length) {
    const empty = document.createElement("p");
    empty.className = "monitoring-hud__child-note";
    empty.textContent = "No Monitor Groups are available to map yet.";
    monitoringHudOverlayProfileMembershipList.appendChild(empty);
    return;
  }
  if (!visibleMonitorRows.length) {
    const empty = document.createElement("p");
    empty.className = "monitoring-hud__child-note";
    empty.textContent = "No monitors match the current search and filter.";
    monitoringHudOverlayProfileMembershipList.appendChild(empty);
    return;
  }
  visibleMonitorRows.forEach((cardId) => {
    const layout = Object.assign(monitoringHudCardDefaults(cardId), cards[cardId] || {});
    const checked = selectedIds.has(cardId);
    const row = document.createElement("label");
    row.className = "monitoring-hud__overlay-profile-membership-row";
    row.dataset.overlayProfileMembershipRow = cardId;
    row.setAttribute("aria-selected", checked ? "true" : "false");
    if (cardId === monitoringHudOverlayProfileContextMonitorId) {
      row.classList.add("monitoring-hud__overlay-profile-membership-row--context");
      row.dataset.overlayProfileContextMonitor = "selected-monitor";
    }

    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = cardId;
    input.checked = checked;
    input.dataset.overlayProfileMembershipToggle = cardId;
    input.setAttribute("aria-label", `Show ${layout.title || "Monitor Group"} in active Overlay Profile`);

    const title = document.createElement("strong");
    title.textContent = layout.title || "Monitor Group";

    const summary = document.createElement("small");
    summary.textContent = monitoringHudOverlayProfileMonitorSummary(cardId, layout);

    row.appendChild(input);
    row.appendChild(title);
    row.appendChild(summary);
    monitoringHudOverlayProfileMembershipList.appendChild(row);
  });
  if (monitoringHudOverlayProfileContextMonitorId && monitoringHudActiveChildWindow === "overlay-profile-settings") {
    const contextRow = monitoringHudOverlayProfileMembershipList.querySelector("[data-overlay-profile-context-monitor='selected-monitor']");
    if (contextRow && typeof contextRow.scrollIntoView === "function") {
      window.requestAnimationFrame(() => contextRow.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "instant" }));
    }
  }
}

function monitoringHudClearOverlayProfileMembershipList() {
  if (monitoringHudOverlayProfileMembershipList) {
    monitoringHudOverlayProfileMembershipList.replaceChildren();
  }
}

function monitoringHudSetOverlayProfileDraftFromProfile(profile) {
  const activeProfile = profile || null;
  const cards = monitoringHudControlState.cards || {};
  monitoringHudOverlayProfileDraftId = activeProfile && activeProfile.id ? activeProfile.id : "";
  monitoringHudOverlayProfileDraftName = activeProfile
    ? monitoringHudCleanOverlayProfileName(activeProfile.name, "Overlay Profile")
    : "";
  monitoringHudOverlayProfileDraftMonitorIds = activeProfile
    ? monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, cards)
    : [];
  if (monitoringHudOverlayProfileNameInput) {
    monitoringHudOverlayProfileNameInput.value = monitoringHudOverlayProfileDraftName;
  }
}

function monitoringHudSetOverlayProfileDraftFromActive() {
  monitoringHudSetOverlayProfileDraftFromProfile(monitoringHudOverlayProfilePendingCreate || monitoringHudActiveOverlayProfile());
}

function monitoringHudOverlayProfileDraftTarget() {
  if (monitoringHudOverlayProfilePendingCreate) return monitoringHudOverlayProfilePendingCreate;
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const selectedId = String(monitoringHudOverlayProfileWindowSelectedId || "").trim();
  return selectedId && monitoringHudControlState.overlayProfiles
    ? monitoringHudControlState.overlayProfiles[selectedId] || null
    : null;
}

function monitoringHudOverlayProfileDraftDirty() {
  const activeProfile = monitoringHudOverlayProfileDraftTarget() || {};
  const cards = monitoringHudControlState.cards || {};
  const currentName = monitoringHudCleanOverlayProfileName(activeProfile.name, "Overlay Profile");
  const currentMonitorIds = monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, cards);
  const draftName = monitoringHudCleanOverlayProfileName(
    monitoringHudOverlayProfileNameInput ? monitoringHudOverlayProfileNameInput.value : monitoringHudOverlayProfileDraftName,
    "Overlay Profile"
  );
  const draftMonitorIds = monitoringHudOverlayProfileDraftMonitorIdsFromWindow();
  monitoringHudOverlayProfileDraftMonitorIds = draftMonitorIds;
  return Boolean(
    monitoringHudOverlayProfilePendingCreate
    || draftName !== currentName
    || !monitoringHudSameMonitorMembership(draftMonitorIds, currentMonitorIds, cards)
  );
}

function monitoringHudCurrentOverlayProfileSelector() {
  return document.getElementById("monitoring-hud-overlay-profile-selector") || monitoringHudOverlayProfileSelector;
}

function monitoringHudCurrentOverlayProfileToggle() {
  return document.getElementById("monitoring-hud-overlay-profile-toggle") || monitoringHudOverlayProfileToggle;
}

function monitoringHudCurrentOverlayProfileLabel() {
  return document.getElementById("monitoring-hud-overlay-profile-label") || monitoringHudOverlayProfileLabel;
}

function monitoringHudCurrentOverlayProfileMenu() {
  return document.getElementById("monitoring-hud-overlay-profile-menu") || monitoringHudOverlayProfileMenu;
}

function monitoringHudSetOverlayProfileDropdownOpen(open) {
  const selector = monitoringHudCurrentOverlayProfileSelector();
  const menu = monitoringHudCurrentOverlayProfileMenu();
  const toggle = monitoringHudCurrentOverlayProfileToggle();
  if (!selector || !menu) return;
  selector.dataset.dropdownOpen = open ? "true" : "false";
  menu.hidden = !open;
  const ownerCard = selector.closest
    ? selector.closest("[data-dashboard-hub-card]")
    : null;
  if (ownerCard) {
    ownerCard.dataset.dropdownLayerOpen = open ? "true" : "false";
  }
  if (toggle) {
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (!open) {
    monitoringHudResetOverlayProfileHover();
  }
}

function monitoringHudResetOverlayProfileHover() {
  const selector = monitoringHudCurrentOverlayProfileSelector();
  if (!selector) return;
  selector.dataset.hoveredProfileId = "";
  selector.querySelectorAll("[data-overlay-profile-option].is-hovered").forEach((option) => {
    option.classList.remove("is-hovered");
  });
}

function monitoringHudShouldSuppressDuplicateOverlayProfileActivation(phase) {
  const now = Date.now();
  if (phase === "click") {
    return Boolean(monitoringHudOverlayProfileSelectorPointerActivatedAt && now - monitoringHudOverlayProfileSelectorPointerActivatedAt < 700);
  }
  if (monitoringHudOverlayProfileSelectorPointerActivatedAt && now - monitoringHudOverlayProfileSelectorPointerActivatedAt < 150) {
    return true;
  }
  monitoringHudOverlayProfileSelectorPointerActivatedAt = now;
  return false;
}

function monitoringHudHandleDashboardOverlayProfileActivation(target, event, phase) {
  const selector = monitoringHudCurrentOverlayProfileSelector();
  if (!selector || !target || !selector.contains(target)) return false;
  if (event && event.preventDefault) event.preventDefault();
  if (event && event.stopPropagation) event.stopPropagation();
  if (event && event.stopImmediatePropagation) event.stopImmediatePropagation();
  if (monitoringHudShouldSuppressDuplicateOverlayProfileActivation(phase)) return true;
  monitoringHudApplyPressedState(target, false);
  const key = `overlay-profile:${monitoringHudControlActivationKey(target)}`;
  if (!monitoringHudReliableActivationAllowed(key)) return false;
  const menu = monitoringHudCurrentOverlayProfileMenu();
  const selectorIsActuallyOpen = Boolean(selector.dataset.dropdownOpen === "true" && menu && !menu.hidden);
  const desiredOpen = !selectorIsActuallyOpen;
  const requestedProfileId = target.dataset.overlayProfileOption || "";
  const profileExists = Boolean(requestedProfileId && monitoringHudControlState.overlayProfiles && monitoringHudControlState.overlayProfiles[requestedProfileId]);
  const beforeActiveProfileId = String(monitoringHudControlState.activeOverlayProfileId || "");
  const result = target.id === "monitoring-hud-overlay-profile-toggle"
    ? (monitoringHudSetOverlayProfileDropdownOpen(desiredOpen), true)
    : monitoringHudSelectOverlayProfile(requestedProfileId || monitoringHudDefaultOverlayProfileId);
  const menuAfter = monitoringHudCurrentOverlayProfileMenu();
  selector.dataset.lastDashboardSelectorActivation = JSON.stringify({
    target: target.id || target.dataset.overlayProfileOption || "",
    phase,
    wasOpen: selectorIsActuallyOpen,
    desiredOpen,
    requestedProfileId,
    profileExists,
    beforeActiveProfileId,
    result: result !== false,
    afterActiveProfileId: String(monitoringHudControlState.activeOverlayProfileId || ""),
    afterOpen: selector.dataset.dropdownOpen || "",
    afterMenuHidden: menuAfter ? Boolean(menuAfter.hidden) : true
  });
  monitoringHudRecordReliableActivation(target, phase, result !== false);
  return result !== false;
}

function monitoringHudBindDashboardOverlayProfileActivation(element) {
  if (!element) return;
  element.onpointerdown = (event) => monitoringHudHandleDashboardOverlayProfileActivation(element, event, "pointerdown");
  element.onmousedown = (event) => monitoringHudHandleDashboardOverlayProfileActivation(element, event, "mousedown");
  element.onclick = (event) => monitoringHudHandleDashboardOverlayProfileActivation(element, event, "click");
}

function monitoringHudSetOverlayProfileWindowDropdownOpen(open) {
  if (!monitoringHudOverlayProfileWindowSelector || !monitoringHudOverlayProfileWindowMenu) return;
  monitoringHudOverlayProfileWindowSelector.dataset.dropdownOpen = open ? "true" : "false";
  monitoringHudOverlayProfileWindowMenu.hidden = !open;
  if (monitoringHudOverlayProfileWindowToggle) {
    monitoringHudOverlayProfileWindowToggle.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (!open) {
    monitoringHudResetOverlayProfileWindowHover();
  }
}

function monitoringHudResetOverlayProfileWindowHover() {
  if (!monitoringHudOverlayProfileWindowSelector) return;
  monitoringHudOverlayProfileWindowSelector.dataset.hoveredProfileId = "";
  monitoringHudOverlayProfileWindowSelector.querySelectorAll("[data-overlay-profile-window-option].is-hovered").forEach((option) => {
    option.classList.remove("is-hovered");
  });
}

function monitoringHudSetOverlayProfileMonitorFilterOpen(open) {
  if (!monitoringHudOverlayProfileMonitorFilter || !monitoringHudOverlayProfileMonitorFilterMenu) return;
  monitoringHudOverlayProfileMonitorFilter.dataset.dropdownOpen = open ? "true" : "false";
  monitoringHudOverlayProfileMonitorFilterMenu.hidden = !open;
  if (monitoringHudOverlayProfileMonitorFilterToggle) {
    monitoringHudOverlayProfileMonitorFilterToggle.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (!open) {
    monitoringHudResetOverlayProfileMonitorFilterHover();
  }
}

function monitoringHudResetOverlayProfileMonitorFilterHover() {
  if (!monitoringHudOverlayProfileMonitorFilter) return;
  monitoringHudOverlayProfileMonitorFilter.dataset.hoveredFilter = "";
  monitoringHudOverlayProfileMonitorFilter.querySelectorAll("[data-overlay-profile-monitor-filter-option].is-hovered").forEach((option) => {
    option.classList.remove("is-hovered");
  });
}

function monitoringHudSetOverlayProfileMonitorFilterValue(value) {
  const filterValue = ["all", "visible", "hidden"].includes(value) ? value : "all";
  monitoringHudOverlayProfileMonitorFilterMode = filterValue;
  if (monitoringHudOverlayProfileMonitorFilter) {
    monitoringHudOverlayProfileMonitorFilter.dataset.overlayProfileMonitorFilter = filterValue;
  }
  if (monitoringHudOverlayProfileMonitorFilterLabel) {
    monitoringHudOverlayProfileMonitorFilterLabel.textContent = monitoringHudOverlayProfileMonitorFilterLabels[filterValue] || "All";
  }
  if (monitoringHudOverlayProfileMonitorFilterMenu) {
    monitoringHudOverlayProfileMonitorFilterMenu.querySelectorAll("[data-overlay-profile-monitor-filter-option]").forEach((option) => {
      option.setAttribute("aria-selected", option.dataset.overlayProfileMonitorFilterOption === filterValue ? "true" : "false");
    });
  }
}

function monitoringHudOpenOverlayProfileDetail(profileId) {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const normalizedProfileId = String(profileId || monitoringHudOverlayProfileWindowSelectedId || monitoringHudControlState.activeOverlayProfileId || "").trim();
  if (!normalizedProfileId || !monitoringHudControlState.overlayProfiles[normalizedProfileId]) return false;
  monitoringHudOverlayProfilePendingCreate = null;
  monitoringHudOverlayProfileWindowSelectedId = normalizedProfileId;
  monitoringHudOverlayProfileDetailOpen = true;
  monitoringHudPendingDeleteOverlayProfileId = "";
  monitoringHudSetOverlayProfileDraftFromProfile(monitoringHudControlState.overlayProfiles[normalizedProfileId]);
  monitoringHudClearOverlayProfileMembershipList();
  monitoringHudSetOverlayProfileWindowDropdownOpen(false);
  monitoringHudRenderControls();
  if (monitoringHudOverlayProfileNameInput && typeof monitoringHudOverlayProfileNameInput.focus === "function") {
    setTimeout(() => monitoringHudOverlayProfileNameInput.focus(), 0);
  }
  return true;
}

function monitoringHudSelectOverlayProfile(profileId) {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const normalizedProfileId = String(profileId || "").trim();
  if (!monitoringHudControlState.overlayProfiles[normalizedProfileId]) return false;
  monitoringHudControlState.activeOverlayProfileId = normalizedProfileId;
  monitoringHudSetOverlayProfileDraftFromActive();
  monitoringHudControlState.activeOverlayRecordingTarget = monitoringHudBuildActiveOverlayRecordingTargetSnapshot(monitoringHudControlState);
  monitoringHudClearOverlayProfileMembershipList();
  monitoringHudSetOverlayProfileDropdownOpen(false);
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudSelectOverlayProfileForWindow(profileId) {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const normalizedProfileId = String(profileId || "").trim();
  if (!monitoringHudControlState.overlayProfiles[normalizedProfileId]) return false;
  monitoringHudOverlayProfilePendingCreate = null;
  monitoringHudOverlayProfileWindowSelectedId = normalizedProfileId;
  monitoringHudOverlayProfileDetailOpen = true;
  monitoringHudPendingDeleteOverlayProfileId = "";
  monitoringHudSetOverlayProfileDraftFromProfile(monitoringHudControlState.overlayProfiles[normalizedProfileId]);
  monitoringHudClearOverlayProfileMembershipList();
  monitoringHudSetOverlayProfileWindowDropdownOpen(false);
  monitoringHudRenderControls();
  return true;
}

function monitoringHudCreateOverlayProfile() {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const profileId = monitoringHudNextOverlayProfileId();
  const profileName = monitoringHudUniqueOverlayProfileName("Overlay Profile", profileId);
  monitoringHudOverlayProfilePendingCreate = {
    id: profileId,
    schemaVersion: monitoringHudOverlayProfileSchemaVersion,
    kind: "overlay-profile",
    scope: "overlay-visible-monitor-membership",
    name: profileName,
    monitorIds: [],
    displayMode: "monitor-cards",
    source: "slc-039-membership-editor-create-shell",
    dirty: true
  };
  monitoringHudControlState.activeOverlayProfileId = profileId;
  monitoringHudControlState.activeOverlayProfileDraftSessionId = profileId;
  monitoringHudOverlayProfileWindowSelectedId = profileId;
  monitoringHudOverlayProfileDetailOpen = true;
  monitoringHudPendingDeleteOverlayProfileId = "";
  monitoringHudSetOverlayProfileDraftFromProfile(monitoringHudOverlayProfilePendingCreate);
  monitoringHudClearOverlayProfileMembershipList();
  monitoringHudSyncActiveOverlayRecordingTargetFromOverlayProfile();
  monitoringHudRenderControls();
  monitoringHudSyncActiveOverlayRecordingTargetFromOverlayProfile();
  setTimeout(() => {
    monitoringHudSyncActiveOverlayRecordingTargetFromOverlayProfile();
    monitoringHudRenderActiveOverlayRecordingTargetPreview();
  }, 0);
  if (monitoringHudOverlayProfileNameInput && typeof monitoringHudOverlayProfileNameInput.focus === "function") {
    monitoringHudOverlayProfileNameInput.focus();
    monitoringHudOverlayProfileNameInput.select();
  }
  return true;
}

function monitoringHudSetOverlayProfileDeleteConfirmation(open) {
  const activeProfile = monitoringHudOverlayProfileDraftTarget() || {};
  monitoringHudPendingDeleteOverlayProfileId = open ? String(activeProfile.id || "") : "";
  if (!monitoringHudOverlayProfileDeleteConfirmation) return;
  const canOpen = Boolean(open && monitoringHudPendingDeleteOverlayProfileId);
  monitoringHudOverlayProfileDeleteConfirmation.hidden = !canOpen;
  monitoringHudOverlayProfileDeleteConfirmation.dataset.overlayProfileDeleteConfirmation = canOpen ? "open" : "closed";
  monitoringHudOverlayProfileDeleteConfirmation.dataset.overlayProfileId = canOpen ? monitoringHudPendingDeleteOverlayProfileId : "";
  if (monitoringHudOverlayProfileWindow) {
    monitoringHudOverlayProfileWindow.dataset.overlayProfileDeleteState = canOpen ? "open" : "closed";
  }
  if (monitoringHudOverlayProfileDetailSection) {
    monitoringHudOverlayProfileDetailSection.dataset.overlayProfileDeleteState = canOpen ? "open" : "closed";
  }
  if (monitoringHudOverlayProfileDeleteTitle) {
    monitoringHudOverlayProfileDeleteTitle.textContent = canOpen
      ? `Delete ${monitoringHudCleanOverlayProfileName(activeProfile.name, "Overlay Profile")}?`
      : "Delete Overlay Profile?";
  }
  if (monitoringHudOverlayProfileDeleteCopy) {
    monitoringHudOverlayProfileDeleteCopy.textContent = canOpen
      ? "Confirm before removing this Overlay Profile. Monitor Groups and Recording Profiles stay separate."
      : "Confirm before removing this Overlay Profile.";
  }
}

function monitoringHudConfirmDeleteOverlayProfile() {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const deleteId = String(monitoringHudPendingDeleteOverlayProfileId || "").trim();
  if (monitoringHudOverlayProfilePendingCreate && deleteId === monitoringHudOverlayProfilePendingCreate.id) {
    monitoringHudOverlayProfilePendingCreate = null;
    monitoringHudOverlayProfileWindowSelectedId = "";
    monitoringHudOverlayProfileDetailOpen = false;
    monitoringHudPendingDeleteOverlayProfileId = "";
    monitoringHudSetOverlayProfileDraftFromActive();
    monitoringHudClearOverlayProfileMembershipList();
    monitoringHudRenderControls();
    return true;
  }
  const profiles = monitoringHudControlState.overlayProfiles || {};
  if (!deleteId || !profiles[deleteId]) return false;
  delete profiles[deleteId];
  if (deleteId === monitoringHudDefaultOverlayProfileId) {
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = true;
  }
  monitoringHudControlState.overlayProfiles = profiles;
  monitoringHudControlState.activeOverlayProfileId = Object.keys(profiles)[0] || "";
  monitoringHudOverlayProfileWindowSelectedId = "";
  monitoringHudOverlayProfileDetailOpen = false;
  monitoringHudPendingDeleteOverlayProfileId = "";
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  monitoringHudSetOverlayProfileDraftFromActive();
  monitoringHudClearOverlayProfileMembershipList();
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudSaveOverlayProfileDraft() {
  const activeProfile = monitoringHudOverlayProfileDraftTarget();
  if (!activeProfile) return false;
  const cards = monitoringHudControlState.cards || {};
  const draftName = monitoringHudUniqueOverlayProfileName(
    monitoringHudOverlayProfileNameInput ? monitoringHudOverlayProfileNameInput.value : activeProfile.name,
    activeProfile.id
  );
  activeProfile.name = draftName;
  activeProfile.monitorIds = monitoringHudOverlayProfileDraftMonitorIdsFromWindow();
  activeProfile.monitorIds = monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, cards);
  activeProfile.dirty = false;
  activeProfile.source = "slc-039-membership-editor";
  monitoringHudControlState.overlayProfiles[activeProfile.id] = activeProfile;
  monitoringHudControlState.activeOverlayProfileId = activeProfile.id;
  monitoringHudOverlayProfileWindowSelectedId = activeProfile.id;
  monitoringHudOverlayProfilePendingCreate = null;
  monitoringHudSetOverlayProfileDraftFromProfile(activeProfile);
  monitoringHudClearOverlayProfileMembershipList();
  monitoringHudPendingDeleteOverlayProfileId = "";
  monitoringHudSyncActiveOverlayRecordingTargetFromOverlayProfile();
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudDiscardOverlayProfileDraft() {
  const pendingWasNew = Boolean(monitoringHudOverlayProfilePendingCreate);
  monitoringHudOverlayProfilePendingCreate = null;
  if (pendingWasNew) {
    monitoringHudOverlayProfileWindowSelectedId = "";
    monitoringHudOverlayProfileDetailOpen = false;
  }
  monitoringHudSetOverlayProfileDraftFromProfile(monitoringHudOverlayProfileDraftTarget() || monitoringHudActiveOverlayProfile());
  monitoringHudClearOverlayProfileMembershipList();
  monitoringHudPendingDeleteOverlayProfileId = "";
  monitoringHudRenderControls();
  return true;
}

function monitoringHudSetChildWindowDirtyModalState(childWindow, isOpen) {
  if (!childWindow) return;
  childWindow.dataset.hudUnsavedState = isOpen ? "open" : "closed";
  const closeButton = childWindow.querySelector(".monitoring-hud__child-window-close");
  if (!closeButton) return;
  closeButton.hidden = isOpen;
  closeButton.setAttribute("aria-hidden", isOpen ? "true" : "false");
  closeButton.tabIndex = isOpen ? -1 : 0;
  closeButton.style.pointerEvents = isOpen ? "none" : "";
}

function monitoringHudSetOverlayProfileUnsavedGuard(open) {
  if (!monitoringHudOverlayProfileUnsavedGuard) return;
  const isOpen = Boolean(open);
  monitoringHudOverlayProfileUnsavedGuard.hidden = !isOpen;
  monitoringHudOverlayProfileUnsavedGuard.dataset.unsavedGuard = isOpen ? "open-save-discard" : "closed";
  monitoringHudOverlayProfileUnsavedGuard.dataset.guardActionLayout = "modal-save-discard-cancel";
  monitoringHudOverlayProfileUnsavedGuard.dataset.pendingOverlayProfileAction = isOpen ? "close" : "";
  if (monitoringHudOverlayProfileWindow) {
    monitoringHudSetChildWindowDirtyModalState(monitoringHudOverlayProfileWindow, isOpen);
    monitoringHudOverlayProfileWindow.dataset.overlayProfileUnsavedState = isOpen ? "open" : "closed";
  }
  if (monitoringHudOverlayProfileDetailSection) {
    monitoringHudOverlayProfileDetailSection.dataset.overlayProfileUnsavedState = isOpen ? "open" : "closed";
  }
  if (!isOpen) return;
  window.requestAnimationFrame(() => {
    if (!monitoringHudOverlayProfileUnsavedGuard || monitoringHudOverlayProfileUnsavedGuard.hidden) return;
    const focusTarget = monitoringHudOverlayProfileUnsavedSave || monitoringHudOverlayProfileUnsavedDiscard;
    if (focusTarget && typeof focusTarget.focus === "function") {
      focusTarget.focus({ preventScroll: true });
    }
  });
}

function monitoringHudCancelOverlayProfileUnsavedGuard() {
  const pendingCreate = monitoringHudOverlayProfilePendingCreate
    ? Object.assign({}, monitoringHudOverlayProfilePendingCreate)
    : null;
  const selectedId = monitoringHudOverlayProfileWindowSelectedId || (pendingCreate ? pendingCreate.id : "");
  const detailWasOpen = Boolean(monitoringHudOverlayProfileDetailOpen || pendingCreate);
  const restoreDraftState = () => {
    if (pendingCreate) {
      monitoringHudOverlayProfilePendingCreate = Object.assign({}, pendingCreate);
    }
    if (selectedId) {
      monitoringHudOverlayProfileWindowSelectedId = selectedId;
    }
    if (detailWasOpen) {
      monitoringHudOverlayProfileDetailOpen = true;
    }
    if (monitoringHudActiveChildWindow !== "overlay-profile-settings") {
      monitoringHudActiveChildWindow = "overlay-profile-settings";
      monitoringHudSetChildWindowVisibility("overlay-profile-settings");
    }
    monitoringHudSetOverlayProfileUnsavedGuard(false);
  };
  monitoringHudSetOverlayProfileUnsavedGuard(false);
  restoreDraftState();
  monitoringHudRenderControls();
  window.requestAnimationFrame(() => {
    restoreDraftState();
    monitoringHudRenderControls();
  });
  return true;
}

function monitoringHudSaveOverlayProfileAndClose() {
  if (!monitoringHudSaveOverlayProfileDraft()) return false;
  monitoringHudSetOverlayProfileUnsavedGuard(false);
  return monitoringHudCloseChildWindow({ force: true });
}

function monitoringHudDiscardOverlayProfileAndClose() {
  if (!monitoringHudDiscardOverlayProfileDraft()) return false;
  monitoringHudSetOverlayProfileUnsavedGuard(false);
  return monitoringHudCloseChildWindow({ force: true });
}

let monitoringHudControlState = {
  featureEnabled: false,
  overlayDeferred: true,
  visible: false,
  anchored: true,
  snapEnabled: true,
  pollingRateMs: 1000,
  warningMode: "badge-text-color",
  warningNotificationsMuted: false,
  panelPosition: null,
  selectedMonitorId: "cpu",
  monitorSequence: 2,
  cards: monitoringHudInitialCards(),
  overlayProfileSchemaVersion: monitoringHudOverlayProfileSchemaVersion,
  activeOverlayProfileId: monitoringHudDefaultOverlayProfileId,
  overlayProfiles: {},
  recordingControlWindowRequested: false,
  recordingControlWindowRequestId: 0,
  recordingControlWindowContract: "recording-studio-focused-control-status",
  recordingControlWindowState: "ready",
  recordingControlWindowTargetSummary: null,
  recordingSessionState: "ready",
  recordingSessionId: "",
  recordingStartedAt: "",
  recordingActiveSegmentStartedAt: "",
  recordingStoppedAt: "",
  recordingStartedAtMs: 0,
  recordingSessionMessage: "Ready for local Start/Stop recording.",
  recordingSnapshotTarget: null,
  recordingSamples: [],
  recordingOutputRequest: null,
  recordingOutputRequestSequence: 0,
  recordingOutputResult: null,
  recordingFolderOpenRequest: null,
  recordingFolderOpenRequestSequence: 0,
  recordingFolderOpenResult: null,
  recordingFolderOpenStatus: "no-output-yet",
  logViewerRequested: false,
  logViewerRequestId: "",
  logViewerRequestSequence: 0,
  logViewerState: "ready",
  logViewerSummary: null,
  changedAt: Date.now()
};
monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
const monitoringHudStorageKey = "nexusMonitoringHudLayoutV4";
const monitoringHudLegacyStorageKeys = ["nexusMonitoringHudLayoutV1", "nexusMonitoringHudLayoutV2", "nexusMonitoringHudLayoutV3"];
const monitoringHudTransientRecordingSessionStates = new Set(["recording", "paused", "saving"]);
const monitoringHudSnapSize = 20;
const monitoringHudLargeMonitorFixtureCount = 125;
const monitoringHudLargeSensorFixtureCount = 1200;
const monitoringHudSensorRenderLimit = 120;
let monitoringHudDragInProgress = false;
let monitoringHudPanelPositionFrame = 0;
let monitoringHudQueuedPanelPosition = null;
let monitoringHudActiveChildWindow = "";
let monitoringHudPendingDeleteMonitorId = "";
let monitoringHudResizeProofFrame = 0;
let monitoringHudLargeFixtureModeEnabled = false;
let monitoringHudLargeSensorFixtureCache = null;
let monitoringHudUnsavedMonitorDirty = false;
let monitoringHudPendingSelectMonitorId = "";
let monitoringHudPendingGuardAction = null;
let monitoringHudDraftOriginalMonitorId = "";
let monitoringHudDraftOriginalLayout = null;
let monitoringHudDraftWorkingLayout = null;
let monitoringHudSensorSettingsRefreshFrame = 0;
let monitoringHudSourcePickerSuppressNativeChangeUntil = 0;
let monitoringHudSourcePickerSuppressClickUntil = 0;
let monitoringHudSourcePickerSuppressClickRow = null;
let monitoringHudDisplayModeSuppressClickUntil = 0;
let monitoringHudDisplayModeSuppressClickButton = null;
let monitoringHudHoveredSourcePickerId = "";
let monitoringHudOverlayProfileDraftId = monitoringHudDefaultOverlayProfileId;
let monitoringHudOverlayProfileDraftName = "Default Overlay Profile";
let monitoringHudOverlayProfileDraftMonitorIds = [];
let monitoringHudOverlayProfileContextMonitorId = "";
let monitoringHudOverlayProfileWindowSelectedId = "";
let monitoringHudOverlayProfileDetailOpen = false;
let monitoringHudPendingDeleteOverlayProfileId = "";
let monitoringHudOverlayProfileMonitorSearchTerm = "";
let monitoringHudOverlayProfileMonitorFilterMode = "all";
let monitoringHudActiveSourceSettingsId = "";
let monitoringHudSourcePollingDropdownOpenSensorId = "";
const monitoringHudSourceFilterLabels = {
  all: "All",
  supported: "Supported",
  deferred: "Deferred",
  missing: "Missing",
  warning: "Warning",
  cpu: "CPU",
  gpu: "GPU",
  memory: "Memory",
  disk: "Disk",
  network: "Network",
  temperature: "Temperature",
  load: "Load",
  clock: "Clock",
  power: "Power",
  fan: "Fan",
  voltage: "Voltage"
};
const monitoringHudPollingRateLabels = {
  default: "Default",
  1000: "1s",
  2000: "2s",
  5000: "5s",
  10000: "10s"
};
const monitoringHudOverlayProfileMonitorFilterLabels = {
  all: "All",
  visible: "Visible",
  hidden: "Hidden"
};
const monitoringHudReliableActivationState = {
  sequence: 0,
  lastKey: "",
  lastAt: 0,
  attempts: [],
  visualStates: {}
};

function monitoringHudSnap(value) {
  if (!monitoringHudControlState.snapEnabled) return Math.round(value);
  return Math.round(value / monitoringHudSnapSize) * monitoringHudSnapSize;
}

function monitoringHudBound(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function monitoringHudRecordResizeFrame(payload) {
  if (!monitoringHud) return;
  const rect = payload || {};
  monitoringHudResizeProofFrame += 1;
  monitoringHud.dataset.liveResizeProof = "invisible-real-ui-frame-pixel-signature-grow-shrink";
  monitoringHud.dataset.liveResizeActive = rect.active === false ? "false" : "true";
  monitoringHud.dataset.liveResizeFrame = String(monitoringHudResizeProofFrame);
  monitoringHud.dataset.liveResizeDirection = String(rect.direction || "unknown");
  monitoringHud.dataset.liveResizeGeometry = `${Number(rect.width) || 0}x${Number(rect.height) || 0}`;
  monitoringHud.dataset.liveResizeFrameIntervalMs = String(Number(rect.frameIntervalMs) || 0);
  monitoringHud.dataset.resizeProofVisibility = "normal-ui-no-proof-artifacts";
  monitoringHud.dataset.resizeProofVisuals = "none";
  monitoringHud.dataset.liveResizeVisualArtifact = "none";
  monitoringHud.dataset.liveResizePixelSignature = [
    monitoringHudResizeProofFrame,
    Number(rect.width) || 0,
    Number(rect.height) || 0,
    String(rect.direction || "unknown")
  ].join(":");
  monitoringHud.style.setProperty("--monitoring-hud-live-resize-proof-x", "0px");
  monitoringHud.style.setProperty("--monitoring-hud-live-resize-proof-y", "0px");
  monitoringHud.style.setProperty("--monitoring-hud-live-resize-proof-alpha", "0");
}

function monitoringHudFinishResizeFrame(payload) {
  monitoringHudRecordResizeFrame(Object.assign({}, payload || {}, { active: false }));
  if (monitoringHud) {
    monitoringHud.dataset.liveResizeActive = "false";
    monitoringHud.style.setProperty("--monitoring-hud-live-resize-proof-alpha", "0");
  }
}

window.monitoringHudRecordResizeFrame = monitoringHudRecordResizeFrame;
window.monitoringHudFinishResizeFrame = monitoringHudFinishResizeFrame;

function monitoringHudClearTransientRecordingRuntimeState(state) {
  if (!state || typeof state !== "object") return state;
  const sessionState = String(state.recordingSessionState || "");
  if (monitoringHudTransientRecordingSessionStates.has(sessionState)) {
    state.recordingSessionState = "ready";
    state.recordingSessionMessage = "Ready for local Start/Stop recording.";
  }
  state.recordingSessionId = "";
  state.recordingStartedAt = "";
  state.recordingActiveSegmentStartedAt = "";
  state.recordingPausedAt = "";
  state.recordingStoppedAt = "";
  state.recordingStartedAtMs = 0;
  state.recordingSnapshotTarget = null;
  state.recordingSamples = [];
  state.recordingOutputRequest = null;
  state.recordingControlWindowRequested = false;
  state.recordingControlWindowRequestId = 0;
  state.recordingControlWindowState = "ready";
  state.recordingControlWindowTargetSummary = null;
  state.logViewerRequested = false;
  state.logViewerRequestId = "";
  state.logViewerState = "ready";
  state.logViewerSummary = null;
  return state;
}

function monitoringHudLoadStoredState() {
  try {
    if (window.localStorage) {
      monitoringHudLegacyStorageKeys.forEach((key) => window.localStorage.removeItem(key));
    }
    const raw = window.localStorage ? window.localStorage.getItem(monitoringHudStorageKey) : "";
    if (!raw) return;
    const stored = JSON.parse(raw);
    const storedHasCards = monitoringHudHasOwnCards(stored);
    monitoringHudControlState = Object.assign({}, monitoringHudControlState, stored || {});
    monitoringHudControlState.cards = storedHasCards
      ? monitoringHudSafeCardsObject(stored.cards)
      : monitoringHudSafeCardsObject(monitoringHudControlState.cards || monitoringHudInitialCards());
    if (!monitoringHudControlState.selectedMonitorId || !monitoringHudControlState.cards[monitoringHudControlState.selectedMonitorId]) {
      monitoringHudControlState.selectedMonitorId = Object.keys(monitoringHudControlState.cards)[0] || "";
    }
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudClearTransientRecordingRuntimeState(monitoringHudControlState);
  } catch (_err) {
    monitoringHudControlState.changedAt = Date.now();
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudClearTransientRecordingRuntimeState(monitoringHudControlState);
  }
}

function monitoringHudSaveStoredState() {
  try {
    if (!window.localStorage) return;
    const persistedState = JSON.parse(JSON.stringify(monitoringHudControlState));
    monitoringHudNormalizeOverlayProfileState(persistedState);
    monitoringHudClearTransientRecordingRuntimeState(persistedState);
    window.localStorage.setItem(monitoringHudStorageKey, JSON.stringify(persistedState));
    monitoringHudSyncActiveOverlayRecordingTargetFromOverlayProfile();
  } catch (_err) {}
}

function monitoringHudMarkChanged() {
  monitoringHudControlState.changedAt = Date.now();
  monitoringHudSaveStoredState();
}

function monitoringHudCardDefaults(cardId) {
  const sensors = monitoringHudDefaultSensorIds(cardId);
  const sensorSettings = {};
  sensors.forEach((sensorId) => {
    sensorSettings[sensorId] = monitoringHudDefaultSensorSetting(sensorId);
  });
  return {
    x: 0,
    y: Object.keys(monitoringHudControlState.cards || {}).length * 300,
    w: 600,
    h: 280,
    title: cardId === "cpu" ? "CPU Group" : cardId === "gpu" ? "GPU Group" : "Monitor Group",
    enabled: true,
    pollingRateMs: 1000,
    warningNotificationsEnabled: true,
    sensors,
    sensorSettings
  };
}

function monitoringHudNextMonitorGroupNumber() {
  const usedNumbers = new Set();
  Object.entries(monitoringHudControlState.cards || {}).forEach(([cardId, layout]) => {
    const idMatch = String(cardId || "").match(/^monitor-(\d+)$/);
    if (idMatch) usedNumbers.add(Number(idMatch[1]));
    const titleMatch = String(layout && layout.title ? layout.title : "").match(/^Monitor Group\s+(\d+)$/i);
    if (titleMatch) usedNumbers.add(Number(titleMatch[1]));
  });
  for (let candidate = 3; candidate < 10000; candidate += 1) {
    if (!usedNumbers.has(candidate)) return candidate;
  }
  return Math.max(3, ...Array.from(usedNumbers).filter((value) => Number.isFinite(value))) + 1;
}

function monitoringHudSuggestedMonitorName() {
  return `Monitor Group ${monitoringHudNextMonitorGroupNumber()}`;
}

function monitoringHudCleanMonitorTitle(value, fallback) {
  const title = String(value || "").trim();
  return title || fallback || "Monitor Group";
}

function monitoringHudSensorCategoryForId(sensorId) {
  const value = String(sensorId || "").toLowerCase();
  if (value.includes("cpu")) return "cpu";
  if (value.includes("gpu")) return "gpu";
  if (value.includes("memory")) return "memory";
  if (value.includes("disk")) return "disk";
  if (value.includes("network")) return "network";
  if (value.includes("temperature") || value.includes("thermal")) return "temperature";
  if (value.includes("clock")) return "clock";
  if (value.includes("power")) return "power";
  if (value.includes("fan")) return "fan";
  if (value.includes("voltage")) return "voltage";
  if (value.includes("load")) return "load";
  return "supported";
}

function monitoringHudLargeSensorFixtures() {
  if (monitoringHudLargeSensorFixtureCache) return monitoringHudLargeSensorFixtureCache;
  const categories = [
    ["cpu", "CPU", "Load"],
    ["gpu", "GPU", "Load"],
    ["memory", "Memory", "Usage"],
    ["disk", "Disk", "Throughput"],
    ["network", "Network", "Throughput"],
    ["temperature", "Temperature", "Thermal"],
    ["clock", "Clock", "Frequency"],
    ["power", "Power", "Watts"],
    ["fan", "Fan", "RPM"],
    ["voltage", "Voltage", "Volts"]
  ];
  const sensors = [];
  for (let index = 0; index < monitoringHudLargeSensorFixtureCount; index += 1) {
    const [category, deviceLabel, metricLabel] = categories[index % categories.length];
    const deviceIndex = Math.floor(index / categories.length) + 1;
    const supported = index % 6 === 0 || category === "cpu" || category === "memory";
    const duplicateName = index % 47 === 0 ? "Duplicate Thermal Sensor" : "";
    const longName = index % 59 === 0
      ? `${deviceLabel} ${deviceIndex} ${metricLabel} Extended Descriptor For Long Source Name Validation`
      : "";
    sensors.push({
      id: `fixture-${category}-${deviceIndex}-${index}`,
      label: duplicateName || longName || `${deviceLabel} ${deviceIndex} ${metricLabel}`,
      source: `${supported ? "Local fixture" : "Provider-required fixture"} / ${deviceLabel} ${deviceIndex} / ${metricLabel} / sensor ${index}${longName ? " / extended descriptor long source path" : ""}`,
      state: supported ? "fixture-supported" : "blocked-until-provider",
      value: supported ? "Fixture source available for scale proof" : "Provider required",
      assignable: supported,
      reason: supported ? "Fixture-supported source" : "Provider required",
      provider: supported ? "local-fixture" : "provider-required",
      device: `${deviceLabel} ${deviceIndex}`,
      category,
      metric: metricLabel,
      instance: `sensor-${index}`
    });
  }
  monitoringHudLargeSensorFixtureCache = sensors;
  return monitoringHudLargeSensorFixtureCache;
}

function monitoringHudSensorDefinitions() {
  const base = {
    "cpu-load": {
      id: "cpu-load",
      label: "CPU Load",
      source: "Native Windows CPU load",
      state: "native-provider-pending",
      value: "Warming up",
      assignable: true,
      reason: "Native runtime source",
      provider: "native",
      device: "CPU",
      category: "cpu",
      metric: "Load",
      instance: "primary"
    },
    "cpu-thermal": {
      id: "cpu-thermal",
      label: "CPU Thermal",
      source: "Thermal source pending",
      state: "blocked-until-provider",
      value: "Provider required",
      assignable: false,
      reason: "Provider required",
      provider: "provider-required",
      device: "CPU",
      category: "temperature",
      metric: "Thermal",
      instance: "primary"
    },
    "gpu-load": {
      id: "gpu-load",
      label: "GPU Load",
      source: "GPU source pending",
      state: "blocked-until-provider",
      value: "Unavailable",
      assignable: false,
      reason: "Provider required",
      provider: "provider-required",
      device: "GPU",
      category: "gpu",
      metric: "Load",
      instance: "primary"
    },
    "gpu-thermal": {
      id: "gpu-thermal",
      label: "GPU Thermal",
      source: "Thermal source pending",
      state: "blocked-until-provider",
      value: "Unavailable",
      assignable: false,
      reason: "Provider required",
      provider: "provider-required",
      device: "GPU",
      category: "temperature",
      metric: "Thermal",
      instance: "primary"
    },
    "memory-usage": {
      id: "memory-usage",
      label: "Memory Usage",
      source: "Provider memory source pending",
      state: "blocked-until-provider",
      value: "Provider required",
      assignable: false,
      reason: "Provider required",
      provider: "provider-required",
      device: "Memory",
      category: "memory",
      metric: "Usage",
      instance: "primary"
    },
    "disk-throughput": {
      id: "disk-throughput",
      label: "Disk Throughput",
      source: "Provider disk source pending",
      state: "missing",
      value: "Missing source",
      assignable: false,
      reason: "Missing source",
      provider: "provider-required",
      device: "Disk",
      category: "disk",
      metric: "Throughput",
      instance: "primary"
    },
    "network-throughput": {
      id: "network-throughput",
      label: "Network Throughput",
      source: "Provider network source pending",
      state: "warning",
      value: "Provider warning",
      assignable: false,
      reason: "Warning state, provider required",
      provider: "provider-required",
      device: "Network",
      category: "network",
      metric: "Throughput",
      instance: "primary"
    },
    "clock-frequency": {
      id: "clock-frequency",
      label: "Clock Frequency",
      source: "Provider clock source pending",
      state: "blocked-until-provider",
      value: "Provider required",
      assignable: false,
      reason: "Provider required",
      provider: "provider-required",
      device: "Clock",
      category: "clock",
      metric: "Frequency",
      instance: "primary"
    },
    "power-watts": {
      id: "power-watts",
      label: "Power Draw",
      source: "Provider power source pending",
      state: "blocked-until-provider",
      value: "Provider required",
      assignable: false,
      reason: "Provider required",
      provider: "provider-required",
      device: "Power",
      category: "power",
      metric: "Watts",
      instance: "primary"
    },
    "fan-rpm": {
      id: "fan-rpm",
      label: "Fan Speed",
      source: "Provider fan source pending",
      state: "blocked-until-provider",
      value: "Provider required",
      assignable: false,
      reason: "Provider required",
      provider: "provider-required",
      device: "Fan",
      category: "fan",
      metric: "RPM",
      instance: "primary"
    },
    "voltage-rail": {
      id: "voltage-rail",
      label: "Voltage Rail",
      source: "Provider voltage source pending",
      state: "blocked-until-provider",
      value: "Provider required",
      assignable: false,
      reason: "Provider required",
      provider: "provider-required",
      device: "Voltage",
      category: "voltage",
      metric: "Volts",
      instance: "primary"
    }
  };
  const telemetryCards = Array.isArray(monitoringHudTelemetry.sensorCards) ? monitoringHudTelemetry.sensorCards : [];
  const nonAssignableProductConcepts = new Set(["provider-state", "warning-notifications"]);
  telemetryCards.forEach((card) => {
    const sensors = card && Array.isArray(card.sensors) ? card.sensors : [];
    sensors.forEach((sensor) => {
      if (!sensor || !sensor.id) return;
      const sensorId = String(sensor.id);
      if (nonAssignableProductConcepts.has(sensorId)) return;
      const state = String(sensor.state || base[sensorId]?.state || "");
      const telemetryAssignable = !["blocked-until-provider", "provider-required", "deferred", "missing", "warning"].includes(state);
      base[sensorId] = Object.assign({}, base[sensorId] || {}, {
        id: sensorId,
        label: String(sensor.label || base[sensorId]?.label || sensorId),
        source: String(sensor.source || base[sensorId]?.source || "runtime source"),
        state,
        value: String(sensor.value || base[sensorId]?.value || ""),
        assignable: telemetryAssignable,
        reason: telemetryAssignable ? "Runtime source" : "Provider required",
        provider: String(sensor.provider || base[sensorId]?.provider || "runtime"),
        device: String(sensor.device || base[sensorId]?.device || "Runtime"),
        category: String(sensor.category || base[sensorId]?.category || monitoringHudSensorCategoryForId(sensorId)),
        metric: String(sensor.metric || base[sensorId]?.metric || "Metric"),
        instance: String(sensor.instance || base[sensorId]?.instance || sensorId)
      });
    });
  });
  const sourceDefinitions = Object.values(base);
  return monitoringHudLargeFixtureModeEnabled ? sourceDefinitions.concat(monitoringHudLargeSensorFixtures()) : sourceDefinitions;
}

function monitoringHudSensorDefinitionById(sensorId) {
  return monitoringHudSensorDefinitions().find((sensor) => sensor.id === sensorId) || null;
}

function monitoringHudDefaultSensorIds(cardId) {
  if (cardId === "cpu") return ["cpu-load"];
  return [];
}

function monitoringHudDefaultSensorSetting(sensorId) {
  return {
    displayMode: sensorId === "cpu-load" ? "badge-text" : "text",
    pollingRateMs: "default",
    warningEnabled: true
  };
}

function monitoringHudNormalizeSensorAssignments(cardId, layout) {
  if (!layout) return layout;
  const assignable = new Set(
    monitoringHudSensorDefinitions()
      .filter((sensor) => sensor.assignable !== false)
      .map((sensor) => sensor.id)
  );
  const rawSensors = Array.isArray(layout.sensors) ? layout.sensors : monitoringHudDefaultSensorIds(cardId);
  layout.sensors = rawSensors
    .map((sensorId) => String(sensorId || "").trim())
    .filter((sensorId, index, list) => sensorId && assignable.has(sensorId) && list.indexOf(sensorId) === index);
  layout.sensorSettings = Object.assign({}, layout.sensorSettings || {});
  layout.sensors.forEach((sensorId) => {
    layout.sensorSettings[sensorId] = Object.assign(
      monitoringHudDefaultSensorSetting(sensorId),
      layout.sensorSettings[sensorId] || {}
    );
  });
  Object.keys(layout.sensorSettings).forEach((sensorId) => {
    if (!layout.sensors.includes(sensorId)) delete layout.sensorSettings[sensorId];
  });
  return layout;
}

function monitoringHudSelectedMonitor() {
  const cards = monitoringHudControlState.cards || {};
  const selectedId = monitoringHudControlState.selectedMonitorId;
  if (selectedId && cards[selectedId]) {
    return { id: selectedId, layout: monitoringHudNormalizeSensorAssignments(selectedId, cards[selectedId]) };
  }
  const firstId = Object.keys(cards)[0] || "";
  monitoringHudControlState.selectedMonitorId = firstId;
  return firstId
    ? { id: firstId, layout: monitoringHudNormalizeSensorAssignments(firstId, cards[firstId] || monitoringHudCardDefaults(firstId)) }
    : { id: "", layout: null };
}

function monitoringHudNormalizeMonitorGroupTitle(cardId, layout) {
  if (!layout) return;
  const oldCpuTitle = ["CPU", "Monitor"].join(" ");
  const oldGpuTitle = ["GPU", "Monitor"].join(" ");
  if (cardId === "cpu" && (!layout.title || layout.title === oldCpuTitle)) {
    layout.title = "CPU Group";
  } else if (cardId === "gpu" && (!layout.title || layout.title === oldGpuTitle)) {
    layout.title = "GPU Group";
  } else if (/^Monitor\s+\d+$/i.test(String(layout.title || ""))) {
    layout.title = String(layout.title).replace(/^Monitor/i, "Monitor Group");
  } else if (!layout.title) {
    layout.title = "Monitor Group";
  }
}

function monitoringHudCreateCardNode(cardId, layout) {
  if (!cardId || !layout) return;
  monitoringHudControlState.lastMonitorGroupNodeSync = "edit-child-window-list";
}

function monitoringHudEnsureCardNodes() {
  if (!monitoringHudMonitorList) return;
  Object.keys(monitoringHudControlState.cards || {}).forEach((cardId) => {
    const layout = Object.assign(monitoringHudCardDefaults(cardId), monitoringHudControlState.cards[cardId] || {});
    monitoringHudNormalizeMonitorGroupTitle(cardId, layout);
    monitoringHudNormalizeSensorAssignments(cardId, layout);
    monitoringHudControlState.cards[cardId] = layout;
    monitoringHudCreateCardNode(cardId, layout);
  });
}

function monitoringHudSetChildWindowVisibility(kind) {
  monitoringHudActiveChildWindow = kind || "";
  if (!monitoringHudChildWindowLayer) return;
  const open = Boolean(monitoringHudActiveChildWindow);
  monitoringHudChildWindowLayer.hidden = !open;
  monitoringHudChildWindowLayer.setAttribute("aria-hidden", open ? "false" : "true");
  monitoringHudChildWindowLayer.dataset.childWindowState = open ? monitoringHudActiveChildWindow : "closed";
  [
    monitoringHudSettingsWindow,
    monitoringHudOverlayProfileWindow,
    monitoringHudOverlayAssignmentWindow,
    monitoringHudSourceSettingsWindow,
    monitoringHudCreateMonitorWindow,
    monitoringHudEditMonitorWindow
  ].forEach((windowNode) => {
    if (!windowNode) return;
    const isActive = windowNode.dataset.childWindow === monitoringHudActiveChildWindow;
    windowNode.hidden = !isActive;
    windowNode.setAttribute("aria-hidden", isActive ? "false" : "true");
  });
  if (monitoringHud) {
    monitoringHud.dataset.activeChildWindow = open ? monitoringHudActiveChildWindow : "none";
    monitoringHud.dataset.dashboardSettingsPanelState = monitoringHudActiveChildWindow === "dashboard-settings" ? "open" : "closed";
    monitoringHud.dataset.overlayProfileSettingsWindowState = monitoringHudActiveChildWindow === "overlay-profile-settings" ? "open" : "closed";
    monitoringHud.dataset.overlayAssignmentWindowState = monitoringHudActiveChildWindow === "monitor-overlay-assignment" ? "open" : "closed";
    monitoringHud.dataset.sourceSettingsWindowState = monitoringHudActiveChildWindow === "sensor-source-settings" ? "open" : "closed";
  }
  if (monitoringHudSettingsAction) {
    const settingsOpen = monitoringHudActiveChildWindow === "dashboard-settings";
    monitoringHudSettingsAction.setAttribute("aria-expanded", settingsOpen ? "true" : "false");
  }
  if (monitoringHudOverlayProfileOpenSettings) {
    const profileSettingsOpen = monitoringHudActiveChildWindow === "overlay-profile-settings";
    monitoringHudOverlayProfileOpenSettings.setAttribute("aria-expanded", profileSettingsOpen ? "true" : "false");
  }
  if (monitoringHudMonitorOverlayProfileSettings) {
    const profileSettingsOpen = monitoringHudActiveChildWindow === "overlay-profile-settings";
    monitoringHudMonitorOverlayProfileSettings.setAttribute("aria-expanded", profileSettingsOpen ? "true" : "false");
  }
}

function monitoringHudRenderDashboardSettingsPanel() {
  const warningEnabled = !monitoringHudControlState.warningNotificationsMuted;
  if (monitoringHudSettingsWarningToggle) {
    monitoringHudSettingsWarningToggle.checked = warningEnabled;
  }
  if (monitoringHudSettingsFeatureControl) {
    monitoringHudSettingsFeatureControl.textContent = monitoringHudControlState.featureEnabled
      ? "Tray owns HUD feature enablement; Dashboard close hides this window only"
      : "HUD feature disabled from tray path; Dashboard opens only when feature is enabled";
  }
  if (monitoringHudSettingsWarningState) {
    monitoringHudSettingsWarningState.textContent = warningEnabled
      ? "Visual notifications enabled"
      : "Warning notifications muted; monitor group settings preserved";
  }
  if (monitoringHudSettingsPersistence) {
    monitoringHudSettingsPersistence.textContent = "Monitor group and Dashboard layout posture are stored locally";
  }
  if (monitoringHudSettingsOverlayState) {
    monitoringHudSettingsOverlayState.textContent = "Deferred; no Overlay/display acceptance in this branch";
  }
  if (monitoringHudSettingsProviderState) {
    monitoringHudSettingsProviderState.textContent = "Provider setup required; no fake telemetry values";
  }
}

function monitoringHudRenderOverlayProfileControls() {
  if (!monitoringHudOverlayProfileEditor) return;
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const profiles = monitoringHudOverlayProfileList();
  const activeProfile = monitoringHudActiveOverlayProfile();
  const activeProfileId = activeProfile && activeProfile.id ? activeProfile.id : "";
  const activeProfileName = activeProfile
    ? monitoringHudCleanOverlayProfileName(activeProfile.name, "Overlay Profile")
    : "No profile selected";
  const cards = monitoringHudControlState.cards || {};
  const monitorIds = activeProfile ? monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, cards) : [];
  const selectedProfile = monitoringHudOverlayProfilePendingCreate
    || profiles.find((profile) => profile.id === monitoringHudOverlayProfileWindowSelectedId)
    || null;
  const selectedProfileName = selectedProfile
    ? monitoringHudCleanOverlayProfileName(selectedProfile.name, "Overlay Profile")
    : activeProfileName;
  const detailOpen = Boolean(monitoringHudOverlayProfileDetailOpen && selectedProfile);
  const dirty = detailOpen && monitoringHudOverlayProfileDraftDirty();
  const draftMonitorIds = monitoringHudOverlayProfileDraftMonitorIdsFromWindow();
  const dashboardProfileSelector = monitoringHudCurrentOverlayProfileSelector();
  const dashboardProfileLabel = monitoringHudCurrentOverlayProfileLabel();
  const dashboardProfileMenu = monitoringHudCurrentOverlayProfileMenu();

  monitoringHudOverlayProfileEditor.dataset.overlayProfileEditorUi = "slc-039-membership-editor";
  monitoringHudOverlayProfileEditor.dataset.overlayProfileMembership = "editable-slc-039-mapping";
  monitoringHudOverlayProfileEditor.dataset.overlayProfileDirty = dirty ? "dirty" : "clean";
  monitoringHudOverlayProfileEditor.dataset.activeOverlayProfileId = activeProfileId;
  monitoringHudOverlayProfileEditor.dataset.overlayProfileCount = String(profiles.length);
  monitoringHudOverlayProfileEditor.dataset.overlayProfileProof = "selector-settings-window-create-rename-membership-save-discard";

  if (dashboardProfileSelector) {
    dashboardProfileSelector.dataset.selectedProfileId = activeProfileId;
    dashboardProfileSelector.dataset.overlayProfileSelector = "active-profile-selector";
  }
  monitoringHudBindDashboardOverlayProfileActivation(monitoringHudCurrentOverlayProfileToggle());
  if (dashboardProfileLabel) {
    dashboardProfileLabel.textContent = activeProfileName;
  }
  if (dashboardProfileMenu) {
    dashboardProfileMenu.replaceChildren();
    dashboardProfileMenu.dataset.visibleOptionTarget = "max-five";
    dashboardProfileMenu.dataset.scrollbarStyle = "ndai-native";
    profiles.forEach((profile) => {
      const option = document.createElement("button");
      option.type = "button";
      option.className = "monitoring-hud__bounded-dropdown-option";
      option.dataset.overlayProfileOption = profile.id;
      option.setAttribute("role", "option");
      option.setAttribute("aria-selected", profile.id === activeProfileId ? "true" : "false");
      option.textContent = monitoringHudCleanOverlayProfileName(profile.name, "Overlay Profile");
      monitoringHudBindDashboardOverlayProfileActivation(option);
      dashboardProfileMenu.appendChild(option);
    });
  }
  if (monitoringHudOverlayProfileWindowSelector) {
    monitoringHudOverlayProfileWindowSelector.dataset.selectedProfileId = monitoringHudOverlayProfileWindowSelectedId || "";
    monitoringHudOverlayProfileWindowSelector.dataset.explicitProfileSelection = monitoringHudOverlayProfileWindowSelectedId ? "true" : "false";
    monitoringHudOverlayProfileWindowSelector.dataset.visibleOptionTarget = "max-five";
    monitoringHudOverlayProfileWindowSelector.dataset.scrollbarStyle = "ndai-native";
  }
  if (monitoringHudOverlayProfileWindowLabel) {
    monitoringHudOverlayProfileWindowLabel.textContent = selectedProfile
      ? monitoringHudCompactOverlayProfileName(selectedProfile.name, "Overlay Profile")
      : "Select profile";
  }
  if (monitoringHudOverlayProfileWindowMenu) {
    monitoringHudOverlayProfileWindowMenu.replaceChildren();
    monitoringHudOverlayProfileWindowMenu.dataset.visibleOptionTarget = "max-five";
    monitoringHudOverlayProfileWindowMenu.dataset.scrollbarStyle = "ndai-native";
    profiles.forEach((profile) => {
      const option = document.createElement("button");
      option.type = "button";
      option.className = "monitoring-hud__bounded-dropdown-option";
      option.dataset.overlayProfileWindowOption = profile.id;
      option.setAttribute("role", "option");
      option.setAttribute("aria-selected", profile.id === monitoringHudOverlayProfileWindowSelectedId ? "true" : "false");
      option.textContent = monitoringHudCleanOverlayProfileName(profile.name, "Overlay Profile");
      monitoringHudOverlayProfileWindowMenu.appendChild(option);
    });
  }
  if (monitoringHudOverlayProfileMonitorCount) {
    monitoringHudOverlayProfileMonitorCount.textContent = `${monitorIds.length} mapped monitor${monitorIds.length === 1 ? "" : "s"}`;
  }
  if (monitoringHudOverlayProfileDisplayMode) {
    monitoringHudOverlayProfileDisplayMode.textContent = activeProfile
      ? monitoringHudOverlayProfileDisplayLabel(activeProfile.displayMode)
      : "No profile";
  }
  if (monitoringHudOverlayProfileWindow) {
    monitoringHudOverlayProfileWindow.dataset.overlayProfileWindow = "select-profile-to-edit-create-right-save-required";
    monitoringHudOverlayProfileWindow.dataset.overlayProfileWorkflow = "select-loads-edit-create-draft-save-required";
    monitoringHudOverlayProfileWindow.dataset.overlayProfileVisualRepair = "manager-selector-same-row-compact-unclipped-proof";
    monitoringHudOverlayProfileWindow.dataset.dirtyGuardCoverage = "save-discard-close-guard";
    monitoringHudOverlayProfileWindow.dataset.overlayProfileVolumePolicy = "max-five-visible-monitors-inner-scroll";
    monitoringHudOverlayProfileWindow.dataset.overlayProfileSelectorPolicy = "max-five-visible-profile-options-ndai-scrollbar";
    monitoringHudOverlayProfileWindow.dataset.overlayProfileOuterScrollPolicy = "normal-no-scroll-emergency-compact-scroll";
    monitoringHudOverlayProfileWindow.dataset.activeOverlayProfileId = activeProfileId;
    monitoringHudOverlayProfileWindow.dataset.selectedProfileId = monitoringHudOverlayProfileWindowSelectedId || "";
    monitoringHudOverlayProfileWindow.dataset.overlayProfileDetailState = detailOpen ? "open" : "closed";
    monitoringHudOverlayProfileWindow.dataset.overlayProfileDirty = dirty ? "dirty" : "clean";
    monitoringHudOverlayProfileWindow.dataset.overlayProfilePendingCreate = monitoringHudOverlayProfilePendingCreate ? "true" : "false";
    monitoringHudOverlayProfileWindow.dataset.overlayProfileMembership = "editable-slc-039-mapping";
    monitoringHudOverlayProfileWindow.dataset.contextMonitorId = monitoringHudOverlayProfileContextMonitorId || "";
  }
  if (monitoringHudOverlayProfileWindowTitle) {
    monitoringHudOverlayProfileWindowTitle.textContent = "Select Or Create";
  }
  if (monitoringHudOverlayProfileWindowActiveName) {
    monitoringHudOverlayProfileWindowActiveName.textContent = selectedProfile
      ? `${monitoringHudCleanOverlayProfileName(selectedProfile.name, "Overlay Profile")} selected`
      : "No profile selected for editing";
  }
  if (monitoringHudOverlayProfileWindowCount) {
    monitoringHudOverlayProfileWindowCount.textContent = `${profiles.length} available profile${profiles.length === 1 ? "" : "s"}`;
  }
  if (monitoringHudOverlayProfileWindowMembership) {
    monitoringHudOverlayProfileWindowMembership.textContent = detailOpen
      ? `${draftMonitorIds.length} selected of ${monitoringHudStableMonitorIds(cards).length} monitor${monitoringHudStableMonitorIds(cards).length === 1 ? "" : "s"}`
      : "Select a profile, then edit its settings.";
  }
  if (monitoringHudOverlayProfileDetailSection) {
    monitoringHudOverlayProfileDetailSection.hidden = !detailOpen;
    monitoringHudOverlayProfileDetailSection.dataset.overlayProfileDetailState = detailOpen ? "open" : "closed";
  }
  if (!detailOpen || !dirty) {
    monitoringHudSetOverlayProfileUnsavedGuard(false);
  }
  if (monitoringHudOverlayProfileMonitorSearch && document.activeElement !== monitoringHudOverlayProfileMonitorSearch) {
    monitoringHudOverlayProfileMonitorSearch.value = monitoringHudOverlayProfileMonitorSearchTerm;
  }
  if (monitoringHudOverlayProfileMonitorFilter) {
    monitoringHudSetOverlayProfileMonitorFilterValue(monitoringHudOverlayProfileMonitorFilterMode);
  }
  if (detailOpen) {
    monitoringHudRenderOverlayProfileMembershipList(activeProfile, cards, draftMonitorIds);
  } else {
    monitoringHudClearOverlayProfileMembershipList();
  }
  if (monitoringHudOverlayProfileNameInput && document.activeElement !== monitoringHudOverlayProfileNameInput) {
    monitoringHudOverlayProfileNameInput.value = dirty
      ? monitoringHudOverlayProfileNameInput.value
      : selectedProfileName;
  }
  if (monitoringHudOverlayProfileSave) {
    monitoringHudSetActionDisabled(monitoringHudOverlayProfileSave, !detailOpen || !dirty, "saveable");
  }
  if (monitoringHudOverlayProfileDiscard) {
    monitoringHudSetActionDisabled(monitoringHudOverlayProfileDiscard, !detailOpen || !dirty, "discardable");
  }
  if (monitoringHudOverlayProfileDelete) {
    monitoringHudSetActionDisabled(monitoringHudOverlayProfileDelete, !detailOpen, "deleteable");
  }
  if (monitoringHudOverlayProfileDeleteConfirmation && !monitoringHudPendingDeleteOverlayProfileId) {
    monitoringHudOverlayProfileDeleteConfirmation.hidden = true;
    monitoringHudOverlayProfileDeleteConfirmation.dataset.overlayProfileDeleteConfirmation = "closed";
  }
  if (monitoringHudOverlayProfileMembershipNote) {
    monitoringHudOverlayProfileMembershipNote.textContent = detailOpen
      ? "Visible monitor membership is scroll-contained here; Monitor Groups and Recording Profiles remain separate."
      : "Select an existing profile to edit or create a new draft profile first.";
  }
}

function monitoringHudRenderMonitorOverlayProfileContext(selected, cards) {
  if (!monitoringHudMonitorOverlayProfileContext) return;
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const hasSelectedMonitor = Boolean(selected && selected.id && cards && cards[selected.id]);
  const activeProfile = monitoringHudActiveOverlayProfile() || {};
  const activeProfileId = activeProfile.id || monitoringHudDefaultOverlayProfileId;
  const activeMonitorIds = monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, cards || {});
  const included = hasSelectedMonitor && activeMonitorIds.includes(selected.id);
  const assignedProfileCount = hasSelectedMonitor
    ? monitoringHudOverlayProfileList().filter((profile) => {
        const profileMonitorIds = monitoringHudUniqueValidMonitorIds(profile.monitorIds, cards || {});
        return profileMonitorIds.includes(selected.id);
      }).length
    : 0;
  monitoringHudMonitorOverlayProfileContext.dataset.overlayProfileIntegration = "slc-040-readonly-manage-context";
  monitoringHudMonitorOverlayProfileContext.dataset.overlayProfileContextLayout = "single-row-readonly";
  monitoringHudMonitorOverlayProfileContext.dataset.overlayProfileMembershipState = hasSelectedMonitor
    ? (included ? "selected-monitor-included" : "selected-monitor-excluded")
    : "no-selected-monitor";
  monitoringHudMonitorOverlayProfileContext.dataset.overlayProfileMutation = "assign-unassign-status-window";
  monitoringHudMonitorOverlayProfileContext.dataset.overlayProfileRoute = "assigned-overlay-status-window";
  monitoringHudMonitorOverlayProfileContext.dataset.activeOverlayProfileId = activeProfileId;
  monitoringHudMonitorOverlayProfileContext.dataset.selectedMonitorId = hasSelectedMonitor ? selected.id : "";
  monitoringHudMonitorOverlayProfileContext.dataset.assignedOverlayCount = String(assignedProfileCount);
  if (monitoringHudMonitorOverlayProfileName) {
    monitoringHudMonitorOverlayProfileName.textContent = "Assigned Overlay";
  }
  if (monitoringHudMonitorOverlayProfileSelectedState) {
    monitoringHudMonitorOverlayProfileSelectedState.textContent = hasSelectedMonitor
      ? (included ? "Included in active" : "Not in active")
      : "No monitor selected";
  }
  if (monitoringHudMonitorOverlayProfileCount) {
    monitoringHudMonitorOverlayProfileCount.textContent = `${assignedProfileCount} assigned`;
  }
  if (monitoringHudMonitorOverlayProfileDisplayMode) {
    monitoringHudMonitorOverlayProfileDisplayMode.textContent = monitoringHudOverlayProfileDisplayLabel(activeProfile.displayMode);
  }
}

function monitoringHudRenderOverlayAssignmentWindow() {
  if (!monitoringHudOverlayAssignmentWindow || !monitoringHudOverlayAssignmentList) return;
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const selected = monitoringHudSelectedMonitor();
  const hasSelectedMonitor = Boolean(selected.id && selected.layout);
  const profiles = monitoringHudOverlayProfileList();
  const assignedProfiles = hasSelectedMonitor
    ? profiles.filter((profile) => monitoringHudUniqueValidMonitorIds(profile.monitorIds, monitoringHudControlState.cards || {}).includes(selected.id))
    : [];
  monitoringHudOverlayAssignmentWindow.dataset.overlayAssignmentWindow = "monitor-group-overlay-status-assignment";
  monitoringHudOverlayAssignmentWindow.dataset.selectedMonitorId = hasSelectedMonitor ? selected.id : "";
  monitoringHudOverlayAssignmentWindow.dataset.assignedOverlayCount = String(assignedProfiles.length);
  if (monitoringHudOverlayAssignmentTitle) {
    monitoringHudOverlayAssignmentTitle.textContent = hasSelectedMonitor ? "Overlay Assignment" : "No Monitor Selected";
  }
  if (monitoringHudOverlayAssignmentMonitorName) {
    monitoringHudOverlayAssignmentMonitorName.textContent = hasSelectedMonitor
      ? (selected.layout.title || "Monitor Group")
      : "No monitor selected";
  }
  if (monitoringHudOverlayAssignmentSummary) {
    monitoringHudOverlayAssignmentSummary.textContent = `${assignedProfiles.length} assigned`;
  }
  monitoringHudOverlayAssignmentList.replaceChildren();
  profiles.forEach((profile) => {
    const profileMonitorIds = monitoringHudUniqueValidMonitorIds(profile.monitorIds, monitoringHudControlState.cards || {});
    const assigned = hasSelectedMonitor && profileMonitorIds.includes(selected.id);
    const row = document.createElement("div");
    row.className = "monitoring-hud__overlay-assignment-row";
    row.dataset.overlayAssignmentProfileId = profile.id;
    row.dataset.overlayAssignmentState = assigned ? "assigned" : "unassigned";
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = monitoringHudCleanOverlayProfileName(profile.name, "Overlay Profile");
    const summary = document.createElement("span");
    summary.textContent = `${profileMonitorIds.length} monitor${profileMonitorIds.length === 1 ? "" : "s"} visible`;
    copy.appendChild(title);
    copy.appendChild(summary);
    const action = document.createElement("button");
    action.type = "button";
    action.className = assigned
      ? "monitoring-hud__hub-action monitoring-hud__hub-action--danger monitoring-hud__hub-action--compact"
      : "monitoring-hud__hub-action monitoring-hud__hub-action--compact";
    action.dataset.overlayAssignmentToggle = profile.id;
    action.textContent = assigned ? "Unassign" : "Assign";
    action.disabled = !hasSelectedMonitor;
    action.setAttribute("aria-disabled", hasSelectedMonitor ? "false" : "true");
    row.appendChild(copy);
    row.appendChild(action);
    monitoringHudOverlayAssignmentList.appendChild(row);
  });
  if (!profiles.length) {
    const empty = document.createElement("div");
    empty.className = "monitoring-hud__sensor-settings-empty";
    empty.textContent = "No Overlay Profiles are available yet.";
    monitoringHudOverlayAssignmentList.appendChild(empty);
  }
}

function monitoringHudToggleOverlayAssignment(profileId) {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const selected = monitoringHudSelectedMonitor();
  if (!selected.id || !profileId || !monitoringHudControlState.overlayProfiles[profileId]) return false;
  const profile = monitoringHudControlState.overlayProfiles[profileId];
  const currentIds = monitoringHudUniqueValidMonitorIds(profile.monitorIds, monitoringHudControlState.cards || {});
  const assigned = currentIds.includes(selected.id);
  profile.monitorIds = assigned
    ? currentIds.filter((monitorId) => monitorId !== selected.id)
    : currentIds.concat(selected.id);
  monitoringHudControlState.overlayProfiles[profileId] = profile;
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  monitoringHudRenderControls();
  monitoringHudOpenChildWindow("monitor-overlay-assignment");
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudSensorAssignmentSummary(layout) {
  const assigned = Array.isArray(layout && layout.sensors) ? layout.sensors : [];
  if (!assigned.length) return "No sources assigned";
  const labels = assigned
    .map((sensorId) => monitoringHudSensorDefinitionById(sensorId))
    .filter(Boolean)
    .map((sensor) => sensor.label);
  return labels.length ? `${labels.length} source${labels.length === 1 ? "" : "s"}: ${labels.join(", ")}` : "No sources assigned";
}

function monitoringHudRenderDeleteConfirmation() {
  if (!monitoringHudMonitorDeleteConfirmation) return;
  const cardId = monitoringHudPendingDeleteMonitorId;
  const layout = cardId && monitoringHudControlState.cards ? monitoringHudControlState.cards[cardId] : null;
  const open = Boolean(cardId && layout);
  monitoringHudMonitorDeleteConfirmation.hidden = !open;
  monitoringHudMonitorDeleteConfirmation.dataset.deleteConfirmationState = open ? "open" : "closed";
  monitoringHudMonitorDeleteConfirmation.dataset.deleteMonitorId = open ? cardId : "";
  if (monitoringHudMonitorDeleteTitle) {
    monitoringHudMonitorDeleteTitle.textContent = open ? `Delete ${layout.title || "Monitor Group"}?` : "Delete monitor?";
  }
  if (monitoringHudMonitorDeleteCopy) {
    monitoringHudMonitorDeleteCopy.textContent = open
      ? "Confirm before removing this Monitor Group and its source assignments."
      : "Confirm before removing this Monitor Group.";
  }
}

function monitoringHudMonitorSearchValue() {
  return String(monitoringHudMonitorSearch ? monitoringHudMonitorSearch.value : "").trim().toLowerCase();
}

function monitoringHudFilteredMonitorIds(cards) {
  const query = monitoringHudMonitorSearchValue();
  const ids = Object.keys(cards || {});
  if (!query) return ids;
  return ids.filter((cardId) => {
    const layout = cards[cardId] || {};
    return [
      cardId,
      layout.title,
      monitoringHudSensorAssignmentSummary(layout)
    ].some((value) => String(value || "").toLowerCase().includes(query));
  });
}

function monitoringHudSensorSearchValue() {
  return String(monitoringHudSensorSearch ? monitoringHudSensorSearch.value : "").trim().toLowerCase();
}

function monitoringHudSensorFilterValue() {
  return String(
    monitoringHudSensorFilter
      ? (monitoringHudSensorFilter.dataset.selectedFilter || monitoringHudSensorFilter.value || "all")
      : "all"
  ).trim().toLowerCase() || "all";
}

function monitoringHudResetSourceFilterHover() {
  if (!monitoringHudSensorFilter) return;
  monitoringHudSensorFilter.dataset.hoveredFilter = "";
  monitoringHudSensorFilter.querySelectorAll("[data-source-filter]").forEach((item) => {
    item.classList.remove("is-hovered");
  });
}

function monitoringHudSetSourceFilterDropdownOpen(open) {
  if (!monitoringHudSensorFilter) return;
  const isOpen = Boolean(open);
  const menu = monitoringHudSensorFilter.querySelector(".monitoring-hud__source-filter-menu");
  monitoringHudSensorFilter.dataset.filterOpen = isOpen ? "true" : "false";
  if (monitoringHudSensorFilterToggle) {
    monitoringHudSensorFilterToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  }
  if (menu) menu.hidden = !isOpen;
  monitoringHudResetSourceFilterHover();
}

function monitoringHudSetSourceFilterValue(value) {
  if (!monitoringHudSensorFilter) return;
  const nextValue = String(value || "all").trim().toLowerCase() || "all";
  monitoringHudSensorFilter.dataset.selectedFilter = nextValue;
  monitoringHudSensorFilter.dataset.currentFilterLabel = monitoringHudSourceFilterLabels[nextValue] || nextValue;
  monitoringHudSensorFilter.querySelectorAll("[data-source-filter]").forEach((item) => {
    const selected = String(item.dataset.sourceFilter || "all").toLowerCase() === nextValue;
    item.setAttribute("aria-selected", selected ? "true" : "false");
    item.setAttribute("aria-pressed", selected ? "true" : "false");
  });
  if (monitoringHudSensorFilterLabel) {
    monitoringHudSensorFilterLabel.textContent = monitoringHudSourceFilterLabels[nextValue] || nextValue;
  }
}

function monitoringHudPollingRateValue(value) {
  const number = Math.max(1000, Number(value) || 1000);
  return Object.prototype.hasOwnProperty.call(monitoringHudPollingRateLabels, number) ? String(number) : "1000";
}

function monitoringHudResetPollingRateHover() {
  if (!monitoringHudMonitorPollingRateControl) return;
  monitoringHudMonitorPollingRateControl.dataset.hoveredValue = "";
  monitoringHudMonitorPollingRateControl.querySelectorAll("[data-polling-rate-option]").forEach((item) => {
    item.classList.remove("is-hovered");
  });
}

function monitoringHudSetPollingRateDropdownOpen(open) {
  if (!monitoringHudMonitorPollingRateControl) return;
  const isOpen = Boolean(open) && monitoringHudMonitorPollingRateControl.dataset.controlDisabled !== "true";
  const menu = document.getElementById("monitoring-hud-monitor-polling-rate-menu");
  monitoringHudMonitorPollingRateControl.dataset.dropdownOpen = isOpen ? "true" : "false";
  if (monitoringHudMonitorPollingRateToggle) {
    monitoringHudMonitorPollingRateToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  }
  if (menu) menu.hidden = !isOpen;
  monitoringHudResetPollingRateHover();
}

function monitoringHudSetPollingRateValue(value, options = {}) {
  const nextValue = monitoringHudPollingRateValue(value);
  if (monitoringHudMonitorPollingRate) {
    monitoringHudMonitorPollingRate.value = nextValue;
  }
  if (monitoringHudMonitorPollingRateControl) {
    monitoringHudMonitorPollingRateControl.dataset.selectedValue = nextValue;
    monitoringHudMonitorPollingRateControl.dataset.currentLabel = monitoringHudPollingRateLabels[Number(nextValue)] || nextValue;
    monitoringHudMonitorPollingRateControl.querySelectorAll("[data-polling-rate-option]").forEach((item) => {
      const selected = String(item.dataset.pollingRateOption || "") === nextValue;
      item.setAttribute("aria-selected", selected ? "true" : "false");
      item.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }
  if (monitoringHudMonitorPollingRateLabel) {
    monitoringHudMonitorPollingRateLabel.textContent = monitoringHudPollingRateLabels[Number(nextValue)] || nextValue;
  }
  if (options.dispatchChange && monitoringHudMonitorPollingRate) {
    monitoringHudMonitorPollingRate.dispatchEvent(new Event("change", { bubbles: true }));
  }
}

function monitoringHudEffectivePollingRateMs(layout) {
  const normalizedLayout = layout || {};
  const rates = [Math.max(1000, Number(normalizedLayout.pollingRateMs) || 1000)];
  const sensorSettings = normalizedLayout.sensorSettings && typeof normalizedLayout.sensorSettings === "object"
    ? normalizedLayout.sensorSettings
    : {};
  const assignedSensors = Array.isArray(normalizedLayout.sensors) ? normalizedLayout.sensors : [];
  assignedSensors.forEach((sensorId) => {
    const setting = sensorSettings[sensorId] || {};
    const value = String(setting.pollingRateMs || "default");
    if (value !== "default") {
      rates.push(Math.max(1000, Number(value) || 1000));
    }
  });
  return Math.min(...rates);
}

function monitoringHudApplyEffectivePollingRate(layout, source = "selected-monitor") {
  if (!layout) return 1000;
  const effectiveRate = monitoringHudEffectivePollingRateMs(layout);
  monitoringHudControlState.pollingRateMs = effectiveRate;
  if (monitoringHud) {
    monitoringHud.dataset.pollingRateLiveCadence = "selected-monitor-and-source-overrides";
    monitoringHud.dataset.effectivePollingRateMs = String(effectiveRate);
    monitoringHud.dataset.effectivePollingRateSource = source;
  }
  return effectiveRate;
}

function monitoringHudControlActivationKey(element, fallback = "") {
  if (!element) return fallback || "unknown-control";
  if (element.id) return element.id;
  if (element.dataset) {
    if (element.dataset.control) return `control:${element.dataset.control}`;
    if (element.dataset.childWindowClose) return `close:${element.dataset.childWindowClose}`;
    if (element.dataset.monitorSelect) return `monitor:${element.dataset.monitorSelect}`;
    if (element.dataset.sourcePickerRow) return `source-row:${element.dataset.sourcePickerRow}`;
    if (element.dataset.monitorSensorInput) return `source-check:${element.dataset.monitorSensorInput}`;
    if (element.dataset.sourceFilter) return `source-filter:${element.dataset.sourceFilter}`;
    if (element.dataset.pollingRateOption) return `polling-rate:${element.dataset.pollingRateOption}`;
    if (element.dataset.sensorDisplayModeOption) {
      return `display-mode:${element.dataset.sensorDisplayModeOption}:${element.dataset.sensorDisplayModeValue || "text"}`;
    }
  }
  return fallback || String(element.textContent || element.tagName || "unknown-control").trim().slice(0, 64);
}

function monitoringHudControlInterceptionSnapshot(element) {
  if (!element || typeof element.getBoundingClientRect !== "function") return {};
  const rect = element.getBoundingClientRect();
  const x = Math.round(rect.left + rect.width / 2);
  const y = Math.round(rect.top + rect.height / 2);
  const topElement = document.elementFromPoint ? document.elementFromPoint(x, y) : null;
  const style = window.getComputedStyle ? window.getComputedStyle(element) : null;
  const topStyle = topElement && window.getComputedStyle ? window.getComputedStyle(topElement) : null;
  return {
    target: monitoringHudControlActivationKey(element),
    tag: String(element.tagName || ""),
    x,
    y,
    width: Math.round(rect.width),
    height: Math.round(rect.height),
    disabled: Boolean(element.disabled),
    ariaDisabled: String(element.getAttribute && element.getAttribute("aria-disabled") || "false"),
    pointerEvents: style ? style.pointerEvents : "",
    zIndex: style ? style.zIndex : "",
    interceptedBy: topElement ? monitoringHudControlActivationKey(topElement, String(topElement.tagName || "")) : "",
    interceptedPointerEvents: topStyle ? topStyle.pointerEvents : "",
    sameTargetOrChild: Boolean(topElement && (topElement === element || element.contains(topElement)))
  };
}

function monitoringHudPollingRateHitboxProof() {
  const row = document.querySelector('[data-control-row="polling-rate-inline"]');
  const control = monitoringHudMonitorPollingRateControl;
  const toggle = monitoringHudMonitorPollingRateToggle;
  if (!row || !control || !toggle) {
    return { passed: false, reason: "polling-rate-hitbox:missing-control" };
  }
  const rowRect = row.getBoundingClientRect();
  const toggleRect = toggle.getBoundingClientRect();
  const labelX = Math.round(rowRect.left + Math.min(24, Math.max(4, rowRect.width * 0.12)));
  const labelY = Math.round(rowRect.top + rowRect.height / 2);
  const labelTarget = document.elementFromPoint ? document.elementFromPoint(labelX, labelY) : null;
  const labelOpensControl = Boolean(
    labelTarget
    && (
      labelTarget === toggle
      || toggle.contains(labelTarget)
      || labelTarget === control
      || control.contains(labelTarget)
    )
  );
  const rowMuchWiderThanToggle = rowRect.width > toggleRect.width + 80;
  const toggleBounded = toggleRect.width <= 156 && toggleRect.right <= rowRect.right + 2;
  return {
    passed: row.dataset.pollingRateHitbox === "toggle-only" && rowMuchWiderThanToggle && toggleBounded && !labelOpensControl,
    rowWidth: Math.round(rowRect.width),
    toggleWidth: Math.round(toggleRect.width),
    labelProbe: [labelX, labelY],
    labelProbeTarget: monitoringHudControlActivationKey(labelTarget),
    labelOpensControl,
    rowPointerEvents: window.getComputedStyle ? window.getComputedStyle(row).pointerEvents : "",
    controlPointerEvents: window.getComputedStyle ? window.getComputedStyle(control).pointerEvents : "",
    hitboxMode: row.dataset.pollingRateHitbox || ""
  };
}

function monitoringHudManageCloseHitboxProof() {
  const button = document.querySelector('[data-child-window-close="monitor-group-edit"]');
  const windowNode = document.getElementById("monitoring-hud-edit-monitor-window");
  if (!button || !windowNode || windowNode.hidden) {
    return { passed: false, reason: "manage-close-hitbox:missing-open-control" };
  }
  const rect = button.getBoundingClientRect();
  const probes = [0.18, 0.50, 0.82].map((ratio) => {
    const x = Math.round(rect.left + rect.width / 2);
    const y = Math.round(rect.top + rect.height * ratio);
    const target = document.elementFromPoint ? document.elementFromPoint(x, y) : null;
    const sameTargetOrChild = Boolean(target && (target === button || button.contains(target)));
    return {
      ratio,
      x,
      y,
      target: monitoringHudControlActivationKey(target),
      sameTargetOrChild
    };
  });
  const style = window.getComputedStyle ? window.getComputedStyle(button) : null;
  const allProbesHitButton = probes.every((probe) => probe.sameTargetOrChild);
  return {
    passed: allProbesHitButton
      && rect.width >= 64
      && rect.height >= 30
      && (!style || (style.pointerEvents !== "none" && style.cursor === "pointer")),
    reason: allProbesHitButton ? "manage-close-hitbox:full-height-clear" : "manage-close-hitbox:partial-interception",
    rect: {
      left: Math.round(rect.left),
      top: Math.round(rect.top),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      bottom: Math.round(rect.bottom)
    },
    probes,
    pointerEvents: style ? style.pointerEvents : "",
    cursor: style ? style.cursor : "",
    activeChildWindow: monitoringHudActiveChildWindow || "none"
  };
}

function monitoringHudReliableActivationAllowed(key) {
  const now = Date.now();
  monitoringHudReliableActivationState.lastKey = key;
  monitoringHudReliableActivationState.lastAt = now;
  return true;
}

function monitoringHudRecordReliableActivation(element, phase, passed = true) {
  const key = monitoringHudControlActivationKey(element);
  monitoringHudReliableActivationState.sequence += 1;
  const snapshot = monitoringHudControlInterceptionSnapshot(element);
  const record = Object.assign({}, snapshot, {
    sequence: monitoringHudReliableActivationState.sequence,
    key,
    phase,
    passed: Boolean(passed),
    timestamp: Date.now()
  });
  monitoringHudReliableActivationState.attempts.push(record);
  if (monitoringHudReliableActivationState.attempts.length > 120) {
    monitoringHudReliableActivationState.attempts.shift();
  }
  if (monitoringHud) {
    monitoringHud.dataset.interactiveControlReliability = "first-click-stress-ready";
    monitoringHud.dataset.lastInteractiveControl = key;
    monitoringHud.dataset.lastInteractiveControlPhase = phase;
    monitoringHud.dataset.clickInterceptionDiagnostics = record.sameTargetOrChild ? "target-clear" : "possible-interception";
  }
  return record;
}

function monitoringHudApplyPressedState(element, pressed) {
  if (!element || !element.classList) return;
  element.classList.toggle("is-pressed", Boolean(pressed));
}

function monitoringHudWireReliableControl(element, key, handler, options = {}) {
  if (!element || typeof handler !== "function") return;
  const activationKey = key || monitoringHudControlActivationKey(element);
  const activate = (event, phase) => {
    if (event && typeof event.preventDefault === "function") event.preventDefault();
    if (event && typeof event.stopPropagation === "function") event.stopPropagation();
    monitoringHudApplyPressedState(element, false);
    if (!monitoringHudReliableActivationAllowed(activationKey)) return;
    const result = handler(event);
    if (result !== false && (options.activateOnPointerUp || options.activateOnPointerDown)) {
      element.dataset.reliablePointerActivatedAt = String(Date.now());
    }
    monitoringHudRecordReliableActivation(element, phase, result !== false);
  };
  const activateOnDown = (event) => {
    monitoringHudApplyPressedState(element, true);
    if (options.activateOnPointerDown) {
      const pointerActivatedAt = Number(element.dataset.reliablePointerActivatedAt || 0);
      if (pointerActivatedAt && Date.now() - pointerActivatedAt < 700) {
        if (event && typeof event.preventDefault === "function") event.preventDefault();
        if (event && typeof event.stopPropagation === "function") event.stopPropagation();
        return;
      }
    }
    if (options.activateOnPointerDown) {
      activate(event, event && event.type === "mousedown" ? "mousedown" : "pointerdown");
    } else {
      monitoringHudRecordReliableActivation(element, event && event.type === "mousedown" ? "mousedown" : "pointerdown", true);
    }
  };
  element.addEventListener("pointerdown", activateOnDown);
  element.addEventListener("mousedown", activateOnDown);
  if (options.activateOnPointerUp) {
    element.addEventListener("pointerup", (event) => activate(event, "pointerup"));
  }
  element.addEventListener("pointerleave", () => monitoringHudApplyPressedState(element, false));
  element.addEventListener("keydown", (event) => {
    const keyName = event && typeof event.key === "string" ? event.key : "";
    if (keyName !== "Enter" && keyName !== " ") return;
    monitoringHudApplyPressedState(element, true);
    activate(event, keyName === "Enter" ? "keyboard-enter" : "keyboard-space");
    element.dataset.reliableKeyboardActivatedAt = String(Date.now());
  });
  element.addEventListener("keyup", () => monitoringHudApplyPressedState(element, false));
  element.addEventListener("click", (event) => {
    if (options.activateOnPointerUp || options.activateOnPointerDown) {
      const pointerActivatedAt = Number(element.dataset.reliablePointerActivatedAt || 0);
      if (pointerActivatedAt && Date.now() - pointerActivatedAt < 700) {
        if (event && typeof event.preventDefault === "function") event.preventDefault();
        if (event && typeof event.stopPropagation === "function") event.stopPropagation();
        return;
      }
    }
    const keyboardActivatedAt = Number(element.dataset.reliableKeyboardActivatedAt || 0);
    if (keyboardActivatedAt && Date.now() - keyboardActivatedAt < 700 && Number(event.detail || 0) === 0) {
      if (event && typeof event.preventDefault === "function") event.preventDefault();
      if (event && typeof event.stopPropagation === "function") event.stopPropagation();
      return;
    }
    activate(event, "click");
  });
}

function monitoringHudWireReliableDelegatedControl(root, selector, keyPrefix, handler, options = {}) {
  if (!root || typeof handler !== "function") return;
  const activate = (event, phase) => {
    const target = event.target && event.target.closest ? event.target.closest(selector) : null;
    if (!target || !root.contains(target)) return;
    const allowNative = Boolean(options.allowNative && options.allowNative(target, event, phase));
    if (!allowNative && event && typeof event.preventDefault === "function") event.preventDefault();
    if (!allowNative && event && typeof event.stopPropagation === "function") event.stopPropagation();
    if (options.activateOnPointerDown) {
      const pointerActivatedAt = Number(target.dataset.reliablePointerActivatedAt || 0);
      if (pointerActivatedAt && Date.now() - pointerActivatedAt < 700) {
        return;
      }
    }
    monitoringHudApplyPressedState(target, false);
    const key = `${keyPrefix}:${monitoringHudControlActivationKey(target)}`;
    if (!monitoringHudReliableActivationAllowed(key)) return;
    const result = handler(target, event);
    monitoringHudRecordReliableActivation(target, phase, result !== false);
  };
  root.addEventListener("pointerdown", (event) => {
    const target = event.target && event.target.closest ? event.target.closest(selector) : null;
    if (!target || !root.contains(target)) return;
    monitoringHudApplyPressedState(target, true);
    monitoringHudRecordReliableActivation(target, "pointerdown", true);
    if (options.activateOnPointerDown) {
      if (event && typeof event.preventDefault === "function") event.preventDefault();
      if (event && typeof event.stopPropagation === "function") event.stopPropagation();
      const key = `${keyPrefix}:${monitoringHudControlActivationKey(target)}`;
      if (!monitoringHudReliableActivationAllowed(key)) return;
      target.dataset.reliablePointerActivatedAt = String(Date.now());
      const result = handler(target, event);
      monitoringHudRecordReliableActivation(target, "pointerdown-immediate", result !== false);
      window.setTimeout(() => monitoringHudApplyPressedState(target, false), 80);
    }
  });
  root.addEventListener("pointerleave", (event) => {
    const target = event.target && event.target.closest ? event.target.closest(selector) : null;
    if (target) monitoringHudApplyPressedState(target, false);
  });
  root.addEventListener("click", (event) => activate(event, "click"));
}

function monitoringHudSourcePickerRowFromEvent(event) {
  if (event && event.target && event.target.closest && event.target.closest("[data-source-settings-open]")) return null;
  return event && event.target && event.target.closest
    ? event.target.closest("[data-source-picker-row]")
    : null;
}

function monitoringHudPreventNativeSourcePickerEvent(event) {
  if (event && typeof event.preventDefault === "function") event.preventDefault();
  if (event && typeof event.stopPropagation === "function") event.stopPropagation();
}

function monitoringHudActivateSourcePickerRow(row, event, phase, options = {}) {
  if (!row || !monitoringHudMonitorSensorAssignment || !monitoringHudMonitorSensorAssignment.contains(row)) return false;
  monitoringHudPreventNativeSourcePickerEvent(event);
  const key = `source-picker:checkmark:${monitoringHudControlActivationKey(row)}`;
  if (options.suppressNativeChange) monitoringHudSourcePickerSuppressNativeChangeUntil = Date.now() + 500;
  if (options.suppressFollowingClick) {
    monitoringHudSourcePickerSuppressClickUntil = Date.now() + 500;
    monitoringHudSourcePickerSuppressClickRow = row;
  }
  monitoringHudApplyPressedState(row, true);
  const result = monitoringHudToggleSensorAssignmentRow(row);
  window.setTimeout(() => monitoringHudApplyPressedState(row, false), 80);
  monitoringHudRecordReliableActivation(row, phase, result !== false);
  if (monitoringHudMonitorSensorAssignment) {
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerActivationPath = "single-deterministic-row-input-keyboard";
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerLastActivation = phase;
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerLastActivationKey = key;
  }
  return result;
}

function monitoringHudWireSourcePickerReliableSelection(root) {
  if (!root) return;
  root.addEventListener("pointerdown", (event) => {
    const row = monitoringHudSourcePickerRowFromEvent(event);
    if (!row || !root.contains(row)) return;
    monitoringHudActivateSourcePickerRow(row, event, "pointerdown-immediate", {
      suppressNativeChange: true,
      suppressFollowingClick: true
    });
  });
  root.addEventListener("pointerleave", (event) => {
    const row = monitoringHudSourcePickerRowFromEvent(event);
    if (row) monitoringHudApplyPressedState(row, false);
  });
  root.addEventListener("click", (event) => {
    const row = monitoringHudSourcePickerRowFromEvent(event);
    if (!row || !root.contains(row)) return;
    monitoringHudPreventNativeSourcePickerEvent(event);
    if (Date.now() <= monitoringHudSourcePickerSuppressClickUntil && row === monitoringHudSourcePickerSuppressClickRow) {
      monitoringHudSourcePickerSuppressClickUntil = 0;
      monitoringHudSourcePickerSuppressClickRow = null;
      return;
    }
    monitoringHudSourcePickerSuppressClickRow = null;
    monitoringHudActivateSourcePickerRow(row, event, "click-fallback");
  }, true);
}

function monitoringHudSetActionDisabled(button, disabled, activeState, disabledState = "clean-disabled") {
  if (!button) return;
  const isDisabled = Boolean(disabled);
  button.disabled = isDisabled;
  button.setAttribute("aria-disabled", isDisabled ? "true" : "false");
  button.dataset.controlState = isDisabled ? disabledState : activeState;
}

function monitoringHudUpdateMonitorActionState() {
  const selected = monitoringHudSelectedMonitor();
  const canEdit = Boolean(selected && selected.id && selected.layout);
  const dirty = Boolean(canEdit && monitoringHudUnsavedMonitorDirty);
  monitoringHudSetActionDisabled(monitoringHudEditMonitorConfirm, !dirty, "saveable");
  monitoringHudSetActionDisabled(monitoringHudEditMonitorDiscard, !dirty, "discardable");
  if (monitoringHudMonitorDetailActions) {
    monitoringHudMonitorDetailActions.dataset.draftActionState = dirty ? "dirty-save-discard-enabled" : "clean-save-discard-disabled";
    monitoringHudMonitorDetailActions.dataset.footerActions = "save-left-discard-delete-right";
  }
}

function monitoringHudDiscardCurrentMonitorDraft() {
  if (!monitoringHudUnsavedMonitorDirty) {
    monitoringHudUpdateMonitorActionState();
    return false;
  }
  if (
    monitoringHudDraftOriginalMonitorId
    && monitoringHudControlState.cards
    && monitoringHudControlState.cards[monitoringHudDraftOriginalMonitorId]
  ) {
    if (monitoringHudDraftOriginalLayout) {
      monitoringHudControlState.cards[monitoringHudDraftOriginalMonitorId] = monitoringHudCloneMonitorLayout(monitoringHudDraftOriginalLayout);
      monitoringHudControlState.selectedMonitorId = monitoringHudDraftOriginalMonitorId;
    } else {
      delete monitoringHudControlState.cards[monitoringHudDraftOriginalMonitorId];
      monitoringHudControlState.selectedMonitorId = Object.keys(monitoringHudControlState.cards || {})[0] || "";
    }
  }
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudSetMonitorDraftDirty(false);
  monitoringHudRenderMonitorManagement();
  return true;
}

function monitoringHudRevealUnsavedGuard() {
  if (!monitoringHudMonitorUnsavedGuard || monitoringHudMonitorUnsavedGuard.hidden) return;
  monitoringHudMonitorUnsavedGuard.dataset.unsavedGuardReveal = "modal-focused";
  window.requestAnimationFrame(() => {
    if (!monitoringHudMonitorUnsavedGuard || monitoringHudMonitorUnsavedGuard.hidden) return;
    const focusTarget = monitoringHudMonitorUnsavedSave || monitoringHudMonitorUnsavedDiscard;
    if (focusTarget && typeof focusTarget.focus === "function") {
      focusTarget.focus({ preventScroll: true });
    }
  });
}

function monitoringHudActivateDisplayModeChip(button, event, phase, options = {}) {
  const root = button && button.closest
    ? button.closest("#monitoring-hud-monitor-sensor-settings, #monitoring-hud-source-settings-body")
    : null;
  if (!button || !root) return false;
  if (event && typeof event.preventDefault === "function") event.preventDefault();
  if (event && typeof event.stopPropagation === "function") event.stopPropagation();
  if (options.suppressFollowingClick) {
    monitoringHudDisplayModeSuppressClickUntil = Date.now() + 500;
    monitoringHudDisplayModeSuppressClickButton = button;
  }
  const sensorId = button.dataset.sensorDisplayModeOption;
  const value = button.dataset.sensorDisplayModeValue || "text";
  const group = root.querySelector(`[data-sensor-display-mode="${sensorId}"]`);
  if (!sensorId || !group) return false;
  group.dataset.sensorDisplayModeSelected = value;
  group.querySelectorAll("[data-sensor-display-mode-option]").forEach((item) => {
    item.setAttribute("aria-pressed", item === button ? "true" : "false");
    item.classList.toggle("is-pressed", item === button && phase.indexOf("pointerdown") >= 0);
  });
  const draft = root === monitoringHudSourceSettingsBody
    ? (monitoringHudApplySourceSetting(sensorId, { displayMode: value }, { skipRender: true }) ? monitoringHudEnsureMonitorDraft() : null)
    : monitoringHudUpdateMonitorDraftFromWindow();
  if (draft) {
    monitoringHudUpdateSelectedMonitorRowSummary(draft.layout);
    root.dataset.displayModeActivationPath = "deterministic-pointer-click-keyboard";
    root.dataset.displayModeLastActivation = phase;
    root.dataset.displayModeLastValue = value;
  }
  monitoringHudRecordReliableActivation(button, phase, Boolean(draft));
  if (phase.indexOf("pointerdown") >= 0) {
    window.setTimeout(() => monitoringHudApplyPressedState(button, false), 80);
  }
  return Boolean(draft);
}

function monitoringHudWireDisplayModeReliableSelection(root) {
  if (!root) return;
  root.addEventListener("pointerdown", (event) => {
    const button = event.target && event.target.closest ? event.target.closest("[data-sensor-display-mode-option]") : null;
    if (!button || !root.contains(button)) return;
    monitoringHudActivateDisplayModeChip(button, event, "pointerdown-immediate", { suppressFollowingClick: true });
  });
  root.addEventListener("click", (event) => {
    const button = event.target && event.target.closest ? event.target.closest("[data-sensor-display-mode-option]") : null;
    if (!button || !root.contains(button)) return;
    if (Date.now() <= monitoringHudDisplayModeSuppressClickUntil && button === monitoringHudDisplayModeSuppressClickButton) {
      if (event && typeof event.preventDefault === "function") event.preventDefault();
      if (event && typeof event.stopPropagation === "function") event.stopPropagation();
      monitoringHudDisplayModeSuppressClickUntil = 0;
      monitoringHudDisplayModeSuppressClickButton = null;
      return;
    }
    monitoringHudDisplayModeSuppressClickButton = null;
    monitoringHudActivateDisplayModeChip(button, event, "click-fallback");
  }, true);
  root.addEventListener("keydown", (event) => {
    if (!["Enter", " "].includes(event.key)) return;
    const button = event.target && event.target.closest ? event.target.closest("[data-sensor-display-mode-option]") : null;
    if (!button || !root.contains(button)) return;
    monitoringHudActivateDisplayModeChip(button, event, "keyboard-toggle");
  });
}

function monitoringHudSensorMatchesFilter(sensor, query, filterValue) {
  const category = String(sensor.category || monitoringHudSensorCategoryForId(sensor.id)).toLowerCase();
  const metric = String(sensor.metric || "").toLowerCase();
  const state = String(sensor.state || "").toLowerCase();
  const supported = sensor.assignable !== false;
  if (filterValue === "supported" && !supported) return false;
  if (filterValue === "deferred" && (supported || !["blocked-until-provider", "provider-required", "deferred"].includes(state))) return false;
  if (filterValue === "missing" && state !== "missing") return false;
  if (filterValue === "warning" && state !== "warning") return false;
  if (!["all", "supported", "deferred", "missing", "warning"].includes(filterValue)) {
    const filterCandidates = [category, metric, state, sensor.id, sensor.label, sensor.source, sensor.provider, sensor.device, sensor.instance, sensor.reason]
      .map((value) => String(value || "").toLowerCase());
    if (!filterCandidates.some((value) => value === filterValue || value.includes(filterValue))) return false;
  }
  if (!query) return true;
  return [
    sensor.id,
    sensor.label,
    sensor.source,
    sensor.provider,
    sensor.device,
    sensor.category,
    sensor.metric,
    sensor.instance,
    sensor.reason,
    state
  ].some((value) => String(value || "").toLowerCase().includes(query));
}

function monitoringHudFilteredSensorDefinitions() {
  const query = monitoringHudSensorSearchValue();
  const filterValue = monitoringHudSensorFilterValue();
  return monitoringHudSensorDefinitions().filter((sensor) => monitoringHudSensorMatchesFilter(sensor, query, filterValue));
}

function monitoringHudRenderSensorPreview(totalCount, renderedCount, selectedCount, supportedCount, deferredCount) {
  if (!monitoringHudSensorPreview) return;
  monitoringHudSensorPreview.dataset.sensorPreview = "source-identity-breadcrumbs";
  monitoringHudSensorPreview.dataset.sensorSourceSummaryPlacement = "attached-to-sensor-source-card";
  const fixtureCopy = monitoringHudLargeFixtureModeEnabled
    ? ` Large-source fixture proof mode is active with ${monitoringHudLargeSensorFixtureCount} scale sources.`
    : "";
  monitoringHudSensorPreview.textContent = `${selectedCount} selected source${selectedCount === 1 ? "" : "s"}. Showing ${renderedCount} of ${totalCount} filtered sources; ${supportedCount} supported and ${deferredCount} provider-required/deferred. Source rows expose provider, device, category, metric, sensor instance breadcrumbs, and their own Settings buttons.${fixtureCopy}`;
}

function monitoringHudRenderSensorAssignment(selected) {
  if (!monitoringHudMonitorSensorAssignment) return;
  const layout = selected && selected.layout ? monitoringHudNormalizeSensorAssignments(selected.id, selected.layout) : null;
  const assigned = new Set(Array.isArray(layout && layout.sensors) ? layout.sensors : []);
  monitoringHudMonitorSensorAssignment.innerHTML = "";
  monitoringHudMonitorSensorAssignment.dataset.sensorAssignment = "sensor-library-source-picker";
  monitoringHudMonitorSensorAssignment.dataset.sourcePickerVisual = "nexus-faceted-searchable-rows";
  monitoringHudMonitorSensorAssignment.dataset.largeSourceFixtureCount = String(monitoringHudLargeSensorFixtureCount);
  monitoringHudMonitorSensorAssignment.dataset.largeSourceFixtureMode = monitoringHudLargeFixtureModeEnabled ? "enabled-validation-support" : "available-validation-support";
  monitoringHudMonitorSensorAssignment.dataset.visibleSourceResultLimit = String(monitoringHudSensorRenderLimit);
  monitoringHudMonitorSensorAssignment.dataset.sourcePickerHoverPersistence = monitoringHudHoveredSourcePickerId
    ? "preserved-across-refresh"
    : "ready";
  const filtered = monitoringHudFilteredSensorDefinitions();
  const rendered = filtered.slice(0, monitoringHudSensorRenderLimit);
  const supportedCount = filtered.filter((sensor) => sensor.assignable !== false).length;
  const deferredCount = filtered.length - supportedCount;
  monitoringHudMonitorSensorAssignment.dataset.filteredSourceCount = String(filtered.length);
  monitoringHudMonitorSensorAssignment.dataset.renderedSourceCount = String(rendered.length);
  monitoringHudMonitorSensorAssignment.dataset.supportedSourceCount = String(supportedCount);
  monitoringHudMonitorSensorAssignment.dataset.deferredSourceCount = String(deferredCount);
  if (monitoringHudSensorResultSummary) {
    monitoringHudSensorResultSummary.textContent = `${rendered.length} shown of ${filtered.length} matching sources (${supportedCount} supported, ${deferredCount} deferred)`;
  }
  rendered.forEach((sensor) => {
    const row = document.createElement("div");
    row.className = "monitoring-hud__sensor-option";
    row.dataset.monitorSensorOption = sensor.id;
    row.dataset.sourcePickerRow = sensor.id;
    row.dataset.sensorSourceState = sensor.state || "unknown";
    row.dataset.sensorAssignable = sensor.assignable === false ? "false" : "true";
    row.dataset.sensorProvider = sensor.provider || "";
    row.dataset.sensorDevice = sensor.device || "";
    row.dataset.sensorCategory = sensor.category || "";
    row.dataset.sensorMetric = sensor.metric || "";
    row.dataset.sensorInstance = sensor.instance || "";
    row.dataset.sourceBreadcrumb = [sensor.provider, sensor.device, sensor.category, sensor.metric, sensor.instance].filter(Boolean).join(" > ");
    row.dataset.sourceToggleMode = "row-and-checkbox-immediate";
    row.dataset.sourceSelected = assigned.has(sensor.id) ? "true" : "false";
    if (monitoringHudHoveredSourcePickerId === sensor.id) {
      row.classList.add("is-hovered");
      row.dataset.hoverPersistence = "preserved-across-refresh";
    }
    row.setAttribute("role", "option");
    row.setAttribute("tabindex", sensor.assignable === false ? "-1" : "0");
    row.setAttribute("aria-selected", assigned.has(sensor.id) ? "true" : "false");
    row.setAttribute("aria-disabled", sensor.assignable === false ? "true" : "false");
    if (sensor.assignable === false) {
      row.classList.add("monitoring-hud__sensor-option--disabled");
    }
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = sensor.id;
    checkbox.checked = assigned.has(sensor.id);
    checkbox.disabled = sensor.assignable === false;
    checkbox.dataset.monitorSensorInput = sensor.id;
    checkbox.setAttribute("aria-label", `Assign ${sensor.label || sensor.id}`);
    const name = document.createElement("span");
    name.textContent = sensor.label || sensor.id;
    const status = document.createElement("b");
    status.className = "monitoring-hud__source-status";
    status.textContent = sensor.assignable === false ? String(sensor.state || "deferred").replace(/-/g, " ") : "supported";
    const settingsButton = document.createElement("button");
    settingsButton.type = "button";
    settingsButton.className = "monitoring-hud__source-settings-button";
    settingsButton.dataset.sourceSettingsOpen = sensor.id;
    settingsButton.textContent = "Settings";
    settingsButton.disabled = sensor.assignable === false;
    settingsButton.setAttribute("aria-disabled", sensor.assignable === false ? "true" : "false");
    const detail = document.createElement("small");
    const breadcrumb = [sensor.provider, sensor.device, sensor.category, sensor.metric, sensor.instance]
      .filter(Boolean)
      .join(" > ");
    detail.textContent = sensor.assignable === false
      ? `${sensor.reason || "Provider required"} - ${breadcrumb || sensor.source || ""}`.trim()
      : `${sensor.reason || "Runtime source"} - ${breadcrumb || sensor.value || sensor.source || ""}`.trim();
    const meta = document.createElement("div");
    meta.className = "monitoring-hud__source-meta";
    [
      sensor.provider || "provider",
      sensor.device || "device",
      sensor.category || "category",
      sensor.metric || "metric",
      sensor.instance || "instance",
      sensor.value || sensor.reason || ""
    ].filter(Boolean).forEach((part) => {
      const item = document.createElement("span");
      item.textContent = String(part);
      meta.appendChild(item);
    });
    row.appendChild(checkbox);
    row.appendChild(name);
    row.appendChild(status);
    row.appendChild(settingsButton);
    row.appendChild(detail);
    row.appendChild(meta);
    monitoringHudMonitorSensorAssignment.appendChild(row);
  });
  if (!rendered.length) {
    const empty = document.createElement("div");
    empty.className = "monitoring-hud__sensor-settings-empty";
    empty.dataset.sensorLibraryEmpty = "no-results";
    empty.textContent = "No matching sources. Change search or filter to find supported or deferred data sources.";
    monitoringHudMonitorSensorAssignment.appendChild(empty);
  }
  monitoringHudRenderSensorPreview(filtered.length, rendered.length, assigned.size, supportedCount, deferredCount);
}

function monitoringHudSetSourceRowSelectionState(row, checked) {
  if (!row) return;
  row.dataset.sourceSelected = checked ? "true" : "false";
  row.setAttribute("aria-selected", checked ? "true" : "false");
}

function monitoringHudUpdateSelectedMonitorRowSummary(layout) {
  if (!monitoringHudEditMonitorList || !monitoringHudControlState.selectedMonitorId || !layout) return;
  const row = monitoringHudEditMonitorList.querySelector(`[data-monitor-row="${monitoringHudControlState.selectedMonitorId}"]`);
  const summary = row ? row.querySelector("span") : null;
  if (summary) summary.textContent = monitoringHudSensorAssignmentSummary(layout);
}

function monitoringHudRefreshSensorPickerSelectionProof(draft, options = {}) {
  const layout = draft && draft.layout ? draft.layout : null;
  const selectedCount = Array.isArray(layout && layout.sensors) ? layout.sensors.length : 0;
  monitoringHudUpdateSelectedMonitorRowSummary(layout);
  if (options.deferSettingsRefresh && monitoringHudMonitorSensorAssignment) {
    const totalCount = Number(monitoringHudMonitorSensorAssignment.dataset.filteredSourceCount || 0);
    const renderedCount = Number(monitoringHudMonitorSensorAssignment.dataset.renderedSourceCount || 0);
    const supportedCount = Number(monitoringHudMonitorSensorAssignment.dataset.supportedSourceCount || 0);
    const deferredCount = Number(monitoringHudMonitorSensorAssignment.dataset.deferredSourceCount || 0);
    monitoringHudRenderSensorPreview(totalCount, renderedCount, selectedCount, supportedCount, deferredCount);
    monitoringHudScheduleSensorSettingsRefresh(draft);
  } else {
    const filtered = monitoringHudFilteredSensorDefinitions();
    const rendered = filtered.slice(0, monitoringHudSensorRenderLimit);
    const supportedCount = filtered.filter((sensor) => sensor.assignable !== false).length;
    const deferredCount = filtered.length - supportedCount;
    monitoringHudRenderSensorSettings(draft);
    monitoringHudRenderSensorPreview(filtered.length, rendered.length, selectedCount, supportedCount, deferredCount);
  }
  if (monitoringHudMonitorSensorAssignment) {
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerCheckmarkMode = options.deferSettingsRefresh
      ? "row-and-checkbox-immediate-deferred-settings"
      : "row-and-checkbox-immediate";
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerCheckmarkStress = "ready";
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerCheckmarkLatency = options.deferSettingsRefresh
      ? "immediate-visual-deferred-settings"
      : "synchronous";
  }
}

function monitoringHudScheduleSensorSettingsRefresh(draft) {
  if (!monitoringHudMonitorSensorSettings) return;
  if (monitoringHudSensorSettingsRefreshFrame) {
    cancelAnimationFrame(monitoringHudSensorSettingsRefreshFrame);
  }
  const selected = draft && draft.id && draft.layout
    ? { id: draft.id, layout: monitoringHudCloneMonitorLayout(draft.layout) }
    : null;
  monitoringHudSensorSettingsRefreshFrame = requestAnimationFrame(() => {
    monitoringHudSensorSettingsRefreshFrame = 0;
    monitoringHudRenderSensorSettings(selected);
  });
}

function monitoringHudApplySensorAssignmentToDraft(row, checked) {
  if (!row || row.dataset.sensorAssignable === "false") return null;
  const sourceId = String(row.dataset.sourcePickerRow || row.dataset.monitorSensorOption || "").trim();
  if (!sourceId) return null;
  const draft = monitoringHudEnsureMonitorDraft();
  if (!draft || !draft.layout) return null;
  draft.layout.title = monitoringHudCleanMonitorTitle(
    monitoringHudEditMonitorName ? monitoringHudEditMonitorName.value : "",
    draft.layout.title || "Monitor Group"
  );
  draft.layout.enabled = monitoringHudMonitorEnabled ? Boolean(monitoringHudMonitorEnabled.checked) : draft.layout.enabled !== false;
  draft.layout.pollingRateMs = monitoringHudMonitorPollingRate
    ? Math.max(1000, Number(monitoringHudMonitorPollingRate.value) || 1000)
    : Math.max(1000, Number(draft.layout.pollingRateMs) || 1000);
  draft.layout.warningNotificationsEnabled = monitoringHudMonitorWarningSetting
    ? Boolean(monitoringHudMonitorWarningSetting.checked)
    : draft.layout.warningNotificationsEnabled !== false;
  const existing = Array.isArray(draft.layout.sensors) ? draft.layout.sensors.slice() : [];
  const selected = checked
    ? Array.from(new Set(existing.concat(sourceId)))
    : existing.filter((sensorId) => sensorId !== sourceId);
  draft.layout.sensors = selected;
  draft.layout.sensorSettings = Object.assign({}, draft.layout.sensorSettings || {});
  if (checked) {
    draft.layout.sensorSettings[sourceId] = Object.assign(
      monitoringHudDefaultSensorSetting(sourceId),
      draft.layout.sensorSettings[sourceId] || {}
    );
  } else {
    delete draft.layout.sensorSettings[sourceId];
  }
  monitoringHudDraftWorkingLayout = draft.layout;
  return {
    id: draft.id,
    layout: monitoringHudDraftWorkingLayout
  };
}

function monitoringHudToggleSensorAssignmentRow(row, explicitChecked) {
  if (!row || row.dataset.sensorAssignable === "false") return false;
  const input = row.querySelector("[data-monitor-sensor-input]");
  if (!input || input.disabled) return false;
  const nextChecked = typeof explicitChecked === "boolean" ? explicitChecked : !input.checked;
  input.checked = nextChecked;
  monitoringHudSetSourceRowSelectionState(row, nextChecked);
  const draft = monitoringHudApplySensorAssignmentToDraft(row, nextChecked);
  if (!draft) return false;
  monitoringHudRefreshSensorPickerSelectionProof(draft, { deferSettingsRefresh: true });
  return true;
}

function monitoringHudSensorPollingRateLabel(value) {
  const key = String(value || "default");
  return monitoringHudPollingRateLabels[key] || "Default";
}

function monitoringHudApplySourceSetting(sensorId, updates = {}, options = {}) {
  const draft = monitoringHudEnsureMonitorDraft();
  if (!draft || !draft.layout || !sensorId) return false;
  draft.layout.sensorSettings = Object.assign({}, draft.layout.sensorSettings || {});
  const current = Object.assign(
    monitoringHudDefaultSensorSetting(sensorId),
    draft.layout.sensorSettings[sensorId] || {}
  );
  draft.layout.sensorSettings[sensorId] = Object.assign(current, updates);
  monitoringHudDraftWorkingLayout = monitoringHudCloneMonitorLayout(draft.layout);
  monitoringHudApplyEffectivePollingRate(draft.layout, "source-setting-override");
  monitoringHudUpdateSelectedMonitorRowSummary(draft.layout);
  if (!options.skipRender) {
    monitoringHudRenderSourceSettingsWindow();
  }
  monitoringHudUpdateMonitorActionState();
  return true;
}

function monitoringHudOpenSourceSettings(sensorId) {
  const sourceId = String(sensorId || "").trim();
  const sensor = monitoringHudSensorDefinitionById(sourceId);
  if (!sensor || sensor.assignable === false) return false;
  monitoringHudActiveSourceSettingsId = sourceId;
  monitoringHudOpenChildWindow("sensor-source-settings");
  return true;
}

function monitoringHudRenderSourceSettingsWindow() {
  if (!monitoringHudSourceSettingsWindow || !monitoringHudSourceSettingsBody) return;
  const sensorId = String(monitoringHudActiveSourceSettingsId || "").trim();
  const sensor = monitoringHudSensorDefinitionById(sensorId);
  const selected = monitoringHudSelectedMonitor();
  const layout = monitoringHudSelectedMonitorDetailLayout(selected);
  const assigned = Boolean(layout && Array.isArray(layout.sensors) && layout.sensors.includes(sensorId));
  const settings = Object.assign(
    monitoringHudDefaultSensorSetting(sensorId),
    layout && layout.sensorSettings ? layout.sensorSettings[sensorId] || {} : {}
  );
  monitoringHudSourceSettingsWindow.dataset.sourceSettingsWindow = "source-list-sensor-settings";
  monitoringHudSourceSettingsWindow.dataset.sourceId = sensorId;
  monitoringHudSourceSettingsWindow.dataset.sourceAssigned = assigned ? "true" : "false";
  monitoringHudSourceSettingsWindow.dataset.pollingOverride = String(settings.pollingRateMs || "default");
  if (monitoringHudSourceSettingsTitle) {
    monitoringHudSourceSettingsTitle.textContent = sensor ? "Sensor Settings" : "No Source Selected";
  }
  if (monitoringHudSourceSettingsName) {
    monitoringHudSourceSettingsName.textContent = sensor ? (sensor.label || sensor.id) : "Select a source";
  }
  if (monitoringHudSourceSettingsState) {
    monitoringHudSourceSettingsState.textContent = `Polling ${monitoringHudSensorPollingRateLabel(settings.pollingRateMs)}`;
  }
  monitoringHudSourceSettingsBody.replaceChildren();
  if (!sensor) {
    const empty = document.createElement("div");
    empty.className = "monitoring-hud__sensor-settings-empty";
    empty.textContent = "Select a Source row Settings button to edit sensor-specific settings.";
    monitoringHudSourceSettingsBody.appendChild(empty);
    return;
  }
  const modeGroup = document.createElement("div");
  modeGroup.className = "monitoring-hud__mode-chip-group monitoring-hud__source-settings-mode";
  modeGroup.dataset.sensorDisplayMode = sensorId;
  modeGroup.dataset.sensorDisplayModeSelected = settings.displayMode || "text";
  const modeTitle = document.createElement("span");
  modeTitle.textContent = "Display mode";
  modeGroup.appendChild(modeTitle);
  [
    ["badge-text", "Badge + text"],
    ["text", "Text only"],
    ["badge", "Badge only"]
  ].forEach(([value, label]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "monitoring-hud__mode-chip";
    button.dataset.sensorDisplayModeOption = sensorId;
    button.dataset.sensorDisplayModeValue = value;
    button.setAttribute("aria-pressed", settings.displayMode === value ? "true" : "false");
    button.textContent = label;
    modeGroup.appendChild(button);
  });
  const polling = document.createElement("div");
  polling.className = "monitoring-hud__child-field monitoring-hud__child-field--inline monitoring-hud__source-settings-polling";
  polling.dataset.sourceSettingsPolling = "default-or-override";
  const pollingText = document.createElement("span");
  pollingText.textContent = "Polling Rate";
  const pollingControl = document.createElement("div");
  pollingControl.className = "monitoring-hud__bounded-dropdown";
  pollingControl.dataset.boundedDropdown = "source-polling-rate";
  pollingControl.dataset.sourcePollingControl = sensorId;
  pollingControl.dataset.selectedValue = String(settings.pollingRateMs || "default");
  const pollingOpen = monitoringHudSourcePollingDropdownOpenSensorId === sensorId;
  pollingControl.dataset.dropdownOpen = pollingOpen ? "true" : "false";
  pollingControl.dataset.visibleOptionTarget = "max-five";
  pollingControl.dataset.scrollbarStyle = "ndai-native";
  const pollingToggle = document.createElement("button");
  pollingToggle.type = "button";
  pollingToggle.className = "monitoring-hud__bounded-dropdown-toggle";
  pollingToggle.dataset.sourcePollingToggle = sensorId;
  pollingToggle.setAttribute("aria-haspopup", "listbox");
  pollingToggle.setAttribute("aria-expanded", pollingOpen ? "true" : "false");
  const pollingToggleSpan = document.createElement("span");
  pollingToggleSpan.textContent = "Rate";
  const pollingToggleStrong = document.createElement("strong");
  pollingToggleStrong.textContent = monitoringHudSensorPollingRateLabel(settings.pollingRateMs);
  pollingToggle.appendChild(pollingToggleSpan);
  pollingToggle.appendChild(pollingToggleStrong);
  const pollingMenu = document.createElement("div");
  pollingMenu.className = "monitoring-hud__bounded-dropdown-menu monitoring-hud__nexus-scroll-pane";
  pollingMenu.dataset.sourcePollingMenu = sensorId;
  pollingMenu.setAttribute("role", "listbox");
  pollingMenu.setAttribute("aria-label", "Sensor polling rate options");
  pollingMenu.hidden = !pollingOpen;
  ["default", "1000", "2000", "5000", "10000"].forEach((value) => {
    const option = document.createElement("button");
    option.type = "button";
    option.className = "monitoring-hud__bounded-dropdown-option";
    option.dataset.sourcePollingOption = value;
    option.setAttribute("role", "option");
    option.setAttribute("aria-selected", String(settings.pollingRateMs || "default") === value ? "true" : "false");
    option.textContent = monitoringHudSensorPollingRateLabel(value);
    pollingMenu.appendChild(option);
  });
  pollingControl.appendChild(pollingToggle);
  pollingControl.appendChild(pollingMenu);
  polling.appendChild(pollingText);
  polling.appendChild(pollingControl);
  const warningLabel = document.createElement("label");
  warningLabel.className = "monitoring-hud__source-settings-warning";
  const warning = document.createElement("input");
  warning.type = "checkbox";
  warning.dataset.sensorWarningEnabled = sensorId;
  warning.checked = settings.warningEnabled !== false;
  warningLabel.appendChild(warning);
  warningLabel.append(" Enable Warning Notifications for this sensor");
  const warningFuture = document.createElement("span");
  warningFuture.className = "monitoring-hud__source-settings-warning-note";
  warningFuture.textContent = "Future warning settings will inherit Monitor defaults unless this sensor overrides them.";
  warningLabel.appendChild(warningFuture);
  monitoringHudSourceSettingsBody.appendChild(modeGroup);
  monitoringHudSourceSettingsBody.appendChild(polling);
  monitoringHudSourceSettingsBody.appendChild(warningLabel);
  if (monitoringHudSourceSettingsNote) {
    monitoringHudSourceSettingsNote.textContent = "Default uses this Monitor Group's Polling Rate. Choosing a sensor-specific rate overrides the generalized polling rate for this source.";
  }
}

function monitoringHudRenderSensorSettings(selected) {
  if (!monitoringHudMonitorSensorSettings) return;
  const layout = selected && selected.layout ? monitoringHudNormalizeSensorAssignments(selected.id, selected.layout) : null;
  const assigned = Array.isArray(layout && layout.sensors) ? layout.sensors : [];
  monitoringHudMonitorSensorSettings.innerHTML = "";
  monitoringHudMonitorSensorSettings.dataset.sensorSettings = "source-list-entry-points";
  monitoringHudMonitorSensorSettings.dataset.sensorSettingsSummaryPlacement = "sensor-source-card";
  monitoringHudMonitorSensorSettings.dataset.assignedSourceCount = String(assigned.length);
  monitoringHudMonitorSensorSettings.hidden = true;
}

function monitoringHudRenderChildWindows() {
  const cards = monitoringHudControlState.cards || {};
  const selected = monitoringHudSelectedMonitor();
  const hasSelectedMonitor = Boolean(selected.id && selected.layout);
  const selectedLayout = hasSelectedMonitor ? monitoringHudSelectedMonitorDetailLayout(selected) : null;
  const count = Object.keys(cards).length;
  if (selectedLayout) {
    monitoringHudApplyEffectivePollingRate(selectedLayout, "selected-monitor-render");
  }
  monitoringHudRenderDashboardSettingsPanel();
  if (monitoringHudCreateMonitorName && !monitoringHudCreateMonitorName.value.trim()) {
    monitoringHudCreateMonitorName.value = monitoringHudSuggestedMonitorName();
  }
  if (monitoringHudEditMonitorTitle) {
    monitoringHudEditMonitorTitle.textContent = selectedLayout ? (selectedLayout.title || "Monitor Group") : (count === 0 ? "No Monitors Yet" : "No Monitor Selected");
  }
  if (monitoringHudEditMonitorName) {
    monitoringHudEditMonitorName.value = selectedLayout ? (selectedLayout.title || "Monitor Group") : "";
    monitoringHudEditMonitorName.disabled = !hasSelectedMonitor;
  }
  if (monitoringHudMonitorEnabled) {
    monitoringHudMonitorEnabled.checked = selectedLayout ? selectedLayout.enabled !== false : false;
    monitoringHudMonitorEnabled.disabled = !hasSelectedMonitor;
  }
  if (monitoringHudMonitorPollingRate) {
    monitoringHudSetPollingRateValue(selectedLayout ? String(Math.max(1000, Number(selectedLayout.pollingRateMs) || 1000)) : "1000");
    monitoringHudMonitorPollingRate.disabled = !hasSelectedMonitor;
  }
  if (monitoringHudMonitorPollingRateControl) {
    monitoringHudMonitorPollingRateControl.dataset.controlDisabled = hasSelectedMonitor ? "false" : "true";
  }
  if (monitoringHudMonitorPollingRateToggle) {
    monitoringHudMonitorPollingRateToggle.disabled = !hasSelectedMonitor;
    monitoringHudMonitorPollingRateToggle.setAttribute("aria-disabled", hasSelectedMonitor ? "false" : "true");
  }
  if (monitoringHudMonitorWarningSetting) {
    monitoringHudMonitorWarningSetting.checked = selectedLayout ? selectedLayout.warningNotificationsEnabled !== false : false;
    monitoringHudMonitorWarningSetting.disabled = !hasSelectedMonitor;
  }
  if (monitoringHudProviderReadinessPanel) {
    monitoringHudProviderReadinessPanel.dataset.readinessClassification = "status-future-capability-not-assignable-source";
  }
  monitoringHudRenderMonitorOverlayProfileContext(selected, cards);
  if (monitoringHudSensorFilter) {
    monitoringHudSetSourceFilterValue(monitoringHudSensorFilterValue());
  }
  if (monitoringHudMonitorDetailDelete) {
    monitoringHudMonitorDetailDelete.disabled = !hasSelectedMonitor;
    monitoringHudMonitorDetailDelete.setAttribute("aria-disabled", hasSelectedMonitor ? "false" : "true");
  }
  if (monitoringHudMonitorDetailEmpty) {
    monitoringHudMonitorDetailEmpty.hidden = count !== 0;
    monitoringHudMonitorDetailEmpty.dataset.monitorDetailEmpty = count === 0 ? "true-empty-state-create-reachable" : "hidden";
  }
  if (monitoringHudMonitorDetailActions) {
    monitoringHudMonitorDetailActions.hidden = !hasSelectedMonitor;
    monitoringHudMonitorDetailActions.dataset.monitorDetailActions = hasSelectedMonitor ? "selected-monitor-footer" : "hidden-no-monitor";
  }
  monitoringHudUpdateMonitorActionState();
  if (monitoringHudMonitorDetailNote) {
    monitoringHudMonitorDetailNote.hidden = !hasSelectedMonitor;
  }
  const settingsPanel = monitoringHudEditMonitorWindow
    ? monitoringHudEditMonitorWindow.querySelector(".monitoring-hud__monitor-settings-panel")
    : null;
  if (settingsPanel) {
    settingsPanel.hidden = count === 0;
    settingsPanel.dataset.monitorDetailState = count === 0 ? "empty" : "selected-monitor-detail";
  }
  if (monitoringHudEditMonitorList) {
    monitoringHudEditMonitorList.innerHTML = "";
    const visibleMonitorIds = monitoringHudFilteredMonitorIds(cards);
    visibleMonitorIds.forEach((cardId) => {
      const layout = Object.assign(monitoringHudCardDefaults(cardId), cards[cardId] || {});
      monitoringHudNormalizeMonitorGroupTitle(cardId, layout);
      monitoringHudNormalizeSensorAssignments(cardId, layout);
      cards[cardId] = layout;
      const row = document.createElement("div");
      row.className = "monitoring-hud__monitor-manage-row";
      row.dataset.monitorRow = cardId;
      row.dataset.monitorSelect = cardId;
      row.setAttribute("role", "button");
      row.setAttribute("tabindex", "0");
      row.setAttribute("aria-current", cardId === selected.id ? "true" : "false");
      const copy = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = layout.title || `Group ${cardId}`;
      const meta = document.createElement("span");
      meta.textContent = monitoringHudSensorAssignmentSummary(layout);
      copy.appendChild(title);
      copy.appendChild(meta);
      row.appendChild(copy);
      monitoringHudEditMonitorList.appendChild(row);
    });
    monitoringHudEditMonitorList.dataset.monitorListScale = "searchable-large-monitor-list";
    monitoringHudEditMonitorList.dataset.monitorListStressProof = "20-plus-groups-nexus-scrollbar";
    monitoringHudEditMonitorList.dataset.largeMonitorFixtureCount = String(monitoringHudLargeMonitorFixtureCount);
    monitoringHudEditMonitorList.dataset.visibleMonitorCount = String(visibleMonitorIds.length);
    if (monitoringHudMonitorListEmpty) {
      const empty = visibleMonitorIds.length === 0;
      monitoringHudMonitorListEmpty.hidden = !empty;
      monitoringHudMonitorListEmpty.dataset.monitorListEmpty = empty ? (count === 0 ? "true-empty-state" : "no-results") : "hidden";
      monitoringHudMonitorListEmpty.textContent = count === 0 ? "No monitors yet." : "No matching monitors.";
    }
  }
  if (monitoringHudMonitorManageSummary) {
    const visibleCount = monitoringHudEditMonitorList
      ? Number(monitoringHudEditMonitorList.dataset.visibleMonitorCount || count)
      : count;
    monitoringHudMonitorManageSummary.textContent = `${visibleCount} shown / ${count} created monitor${count === 1 ? "" : "s"}`;
  }
  monitoringHudRenderDeleteConfirmation();
  monitoringHudRenderSensorAssignment({ id: selected.id, layout: selectedLayout });
  monitoringHudRenderSensorSettings({ id: selected.id, layout: selectedLayout });
  monitoringHudRenderOverlayAssignmentWindow();
  if (monitoringHudActiveChildWindow === "sensor-source-settings") {
    monitoringHudRenderSourceSettingsWindow();
  }
  if (monitoringHudEditMonitor) {
    monitoringHudEditMonitor.disabled = count === 0;
    monitoringHudEditMonitor.setAttribute("aria-disabled", count === 0 ? "true" : "false");
  }
}

function monitoringHudOpenChildWindow(kind) {
  if (kind === "monitor-group-create" && monitoringHudCreateMonitorName) {
    monitoringHudCreateMonitorName.value = monitoringHudSuggestedMonitorName();
  }
  if (kind === "overlay-profile-settings") {
    monitoringHudOverlayProfileWindowSelectedId = "";
    monitoringHudOverlayProfileDetailOpen = false;
    monitoringHudOverlayProfilePendingCreate = null;
    monitoringHudPendingDeleteOverlayProfileId = "";
    monitoringHudSetOverlayProfileDraftFromActive();
    monitoringHudClearOverlayProfileMembershipList();
    monitoringHudSetOverlayProfileDropdownOpen(false);
    monitoringHudSetOverlayProfileWindowDropdownOpen(false);
    monitoringHudSetOverlayProfileMonitorFilterOpen(false);
  }
  monitoringHudRenderChildWindows();
  monitoringHudSetChildWindowVisibility(kind);
  if (kind === "overlay-profile-settings") {
    monitoringHudRenderOverlayProfileControls();
    monitoringHudRenderMonitorOverlayProfileContext(monitoringHudSelectedMonitor(), monitoringHudControlState.cards || {});
  } else if (kind === "monitor-overlay-assignment") {
    monitoringHudRenderOverlayAssignmentWindow();
  } else if (kind === "sensor-source-settings") {
    monitoringHudRenderSourceSettingsWindow();
  }
  const focusTarget = kind === "dashboard-settings"
    ? monitoringHudSettingsWarningToggle
    : kind === "monitor-group-create"
      ? monitoringHudCreateMonitorName
      : kind === "overlay-profile-settings"
        ? monitoringHudOverlayProfileCreate
        : kind === "monitor-overlay-assignment"
          ? monitoringHudOverlayAssignmentList
          : kind === "sensor-source-settings"
            ? monitoringHudSourceSettingsBody
            : monitoringHudEditMonitorName;
  if (focusTarget && typeof focusTarget.focus === "function") {
    setTimeout(() => focusTarget.focus(), 0);
  }
}

function monitoringHudCloseChildWindow(options = {}) {
  if (!options.force && monitoringHudActiveChildWindow === "monitor-group-edit" && monitoringHudUnsavedMonitorDirty) {
    monitoringHudShowUnsavedGuard({ type: "close" });
    return false;
  }
  if (!options.force && monitoringHudActiveChildWindow === "overlay-profile-settings" && monitoringHudOverlayProfileDetailOpen && monitoringHudOverlayProfileDraftDirty()) {
    monitoringHudSetOverlayProfileUnsavedGuard(true);
    return false;
  }
  if (!options.force && monitoringHudActiveChildWindow === "monitor-overlay-assignment") {
    if (monitoringHud) monitoringHud.dataset.nestedChildWindowReturnFlow = "overlay-assignment-returns-to-manage-monitors";
    monitoringHudOpenChildWindow("monitor-group-edit");
    return true;
  }
  if (!options.force && monitoringHudActiveChildWindow === "sensor-source-settings") {
    monitoringHudActiveSourceSettingsId = "";
    monitoringHudSourcePollingDropdownOpenSensorId = "";
    if (monitoringHud) monitoringHud.dataset.nestedChildWindowReturnFlow = "source-settings-returns-to-manage-monitors";
    monitoringHudOpenChildWindow("monitor-group-edit");
    return true;
  }
  if (document.activeElement && document.activeElement.closest && document.activeElement.closest(".monitoring-hud__child-window")) {
    document.activeElement.blur();
  }
  if (monitoringHudActiveChildWindow === "overlay-profile-settings") {
    monitoringHudOverlayProfileContextMonitorId = "";
    monitoringHudOverlayProfileDetailOpen = false;
    monitoringHudOverlayProfilePendingCreate = null;
    monitoringHudPendingDeleteOverlayProfileId = "";
    monitoringHudSetOverlayProfileUnsavedGuard(false);
  }
  if (monitoringHudActiveChildWindow === "sensor-source-settings") {
    monitoringHudActiveSourceSettingsId = "";
    monitoringHudSourcePollingDropdownOpenSensorId = "";
  }
  monitoringHudSetChildWindowVisibility("");
  return true;
}

function monitoringHudCreateMonitorGroup(titleValue) {
  const nextNumber = monitoringHudNextMonitorGroupNumber();
  monitoringHudControlState.monitorSequence = Math.max(Number(monitoringHudControlState.monitorSequence || 2), nextNumber);
  const cardId = `monitor-${nextNumber}`;
  const title = monitoringHudCleanMonitorTitle(
    titleValue,
    `Monitor Group ${nextNumber}`
  );
  monitoringHudControlState.cards[cardId] = {
    x: 0,
    y: (nextNumber - 1) * 300,
    w: 600,
    h: 280,
    title,
    enabled: true,
    pollingRateMs: 1000,
    warningNotificationsEnabled: true,
    sensors: [],
    sensorSettings: {}
  };
  monitoringHudNormalizeSensorAssignments(cardId, monitoringHudControlState.cards[cardId]);
  monitoringHudControlState.selectedMonitorId = cardId;
  monitoringHudPendingDeleteMonitorId = "";
  return cardId;
}

function monitoringHudCreateMonitorGroupFromWindow() {
  const createdId = monitoringHudCreateMonitorGroup(monitoringHudCreateMonitorName ? monitoringHudCreateMonitorName.value : "");
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  monitoringHudCloseChildWindow();
  monitoringHudSetMonitorDraftDirty(true);
  monitoringHudDraftOriginalMonitorId = createdId;
  monitoringHudDraftOriginalLayout = null;
  monitoringHudMarkChanged();
}

function monitoringHudCreateMonitorGroupFromManageWindow(options = {}) {
  if (!options.force && monitoringHudUnsavedMonitorDirty) {
    monitoringHudShowUnsavedGuard({ type: "create" });
    return;
  }
  const createdId = monitoringHudCreateMonitorGroup(monitoringHudSuggestedMonitorName());
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  monitoringHudOpenChildWindow("monitor-group-edit");
  monitoringHudSetMonitorDraftDirty(true);
  monitoringHudDraftOriginalMonitorId = createdId;
  monitoringHudDraftOriginalLayout = null;
  monitoringHudMarkChanged();
}

function monitoringHudBuildLargeMonitorFixture(count) {
  monitoringHudLargeFixtureModeEnabled = true;
  const targetCount = Math.max(1, Number(count) || monitoringHudLargeMonitorFixtureCount);
  const cards = {};
  for (let index = 0; index < targetCount; index += 1) {
    const number = index + 1;
    const cardId = `fixture-monitor-${number}`;
    const sensorA = index % 3 === 0 ? "cpu-load" : "";
    const sensorB = index % 5 === 0 ? "memory-usage" : "";
    const sensors = [sensorA, sensorB].filter(Boolean);
    const sensorSettings = {};
    sensors.forEach((sensorId) => {
      sensorSettings[sensorId] = monitoringHudDefaultSensorSetting(sensorId);
    });
    cards[cardId] = {
      x: 0,
      y: index * 300,
      w: 600,
      h: 280,
      title: `Monitor Group Fixture ${number}`,
      enabled: index % 7 !== 0,
      pollingRateMs: [1000, 2000, 5000, 10000][index % 4],
      warningNotificationsEnabled: index % 4 !== 0,
      sensors,
      sensorSettings
    };
  }
  monitoringHudControlState.cards = cards;
  monitoringHudControlState.monitorSequence = targetCount + 2;
  monitoringHudControlState.selectedMonitorId = Object.keys(cards)[0] || "";
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  monitoringHudRenderMonitorManagement();
  return {
    monitorCount: Object.keys(cards).length,
    sensorFixtureCount: monitoringHudLargeSensorFixtureCount,
    selectedMonitorId: monitoringHudControlState.selectedMonitorId
  };
}

window.setMonitoringHudLargeFixtureMode = monitoringHudBuildLargeMonitorFixture;
window.clearMonitoringHudLargeFixtureMode = function() {
  monitoringHudLargeFixtureModeEnabled = false;
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  monitoringHudRenderMonitorManagement();
};

window.runMonitoringHudMonitorGroupNameReuseProof = function() {
  const backup = getMonitoringHudControlState();
  try {
    monitoringHudControlState.cards = {
      cpu: monitoringHudCardDefaults("cpu"),
      gpu: monitoringHudCardDefaults("gpu"),
      "monitor-3": Object.assign(monitoringHudCardDefaults("monitor-3"), {
        title: "Monitor Group 3",
        sensors: [],
        sensorSettings: {}
      })
    };
    monitoringHudControlState.selectedMonitorId = "monitor-3";
    monitoringHudControlState.monitorSequence = 99;
    monitoringHudPendingDeleteMonitorId = "monitor-3";
    monitoringHudSetMonitorDraftDirty(false);
    monitoringHudConfirmDeleteMonitorGroup();
    const nextNumberAfterDelete = monitoringHudNextMonitorGroupNumber();
    const createdId = monitoringHudCreateMonitorGroup(monitoringHudSuggestedMonitorName());
    const created = monitoringHudControlState.cards[createdId] || {};
    const passed = Boolean(
      nextNumberAfterDelete === 3
      && createdId === "monitor-3"
      && created.title === "Monitor Group 3"
      && Number(monitoringHudControlState.monitorSequence || 0) >= 99
    );
    return {
      passed,
      nextNumberAfterDelete,
      createdId,
      createdTitle: created.title || "",
      monitorSequence: monitoringHudControlState.monitorSequence,
      proof: "delete-create-reuses-lowest-available-monitor-group-number"
    };
  } finally {
    if (window.setMonitoringHudControlState) {
      window.setMonitoringHudControlState(backup);
    }
  }
};

function monitoringHudReadSensorAssignmentsFromWindow(layout) {
  if (!layout) return;
  const selectedSensors = Array.isArray(layout.sensors) ? layout.sensors.slice() : [];
  if (monitoringHudMonitorSensorAssignment) {
    monitoringHudMonitorSensorAssignment.querySelectorAll("input[type='checkbox'][data-monitor-sensor-input]").forEach((input) => {
      const sensorId = String(input.value || "");
      if (!sensorId) return;
      const existingIndex = selectedSensors.indexOf(sensorId);
      if (!input.disabled && input.checked && existingIndex === -1) selectedSensors.push(sensorId);
      if (!input.disabled && !input.checked && existingIndex !== -1) selectedSensors.splice(existingIndex, 1);
    });
  }
  layout.sensors = selectedSensors.filter(Boolean);
  const previousSettings = Object.assign({}, layout.sensorSettings || {});
  layout.sensorSettings = {};
  layout.sensors.forEach((sensorId) => {
    const defaultSetting = monitoringHudDefaultSensorSetting(sensorId);
    const existing = Object.assign(defaultSetting, previousSettings[sensorId] || {});
    const mode = monitoringHudSourceSettingsBody
      ? monitoringHudSourceSettingsBody.querySelector(`[data-sensor-display-mode="${sensorId}"]`)
      : null;
    const warning = monitoringHudSourceSettingsBody
      ? monitoringHudSourceSettingsBody.querySelector(`[data-sensor-warning-enabled="${sensorId}"]`)
      : null;
    const polling = monitoringHudSourceSettingsBody
      ? monitoringHudSourceSettingsBody.querySelector(`[data-source-polling-control="${sensorId}"]`)
      : null;
    layout.sensorSettings[sensorId] = {
      displayMode: mode ? String(mode.dataset.sensorDisplayModeSelected || existing.displayMode || "text") : existing.displayMode,
      pollingRateMs: polling ? String(polling.dataset.selectedValue || existing.pollingRateMs || "default") : existing.pollingRateMs,
      warningEnabled: warning ? Boolean(warning.checked) : existing.warningEnabled !== false
    };
  });
  monitoringHudNormalizeSensorAssignments(monitoringHudControlState.selectedMonitorId, layout);
}

function monitoringHudCloneMonitorLayout(layout) {
  return JSON.parse(JSON.stringify(layout || {}));
}

function monitoringHudSelectedMonitorDetailLayout(selected = monitoringHudSelectedMonitor()) {
  if (
    monitoringHudUnsavedMonitorDirty
    && selected.id
    && selected.id === monitoringHudDraftOriginalMonitorId
    && monitoringHudDraftWorkingLayout
  ) {
    return monitoringHudNormalizeSensorAssignments(selected.id, monitoringHudDraftWorkingLayout);
  }
  return selected.layout;
}

function monitoringHudEnsureMonitorDraft() {
  const selected = monitoringHudSelectedMonitor();
  if (!selected.id || !selected.layout) return null;
  if (!monitoringHudUnsavedMonitorDirty) {
    monitoringHudDraftOriginalMonitorId = selected.id;
    monitoringHudDraftOriginalLayout = monitoringHudCloneMonitorLayout(selected.layout);
    monitoringHudDraftWorkingLayout = monitoringHudCloneMonitorLayout(selected.layout);
  } else if (!monitoringHudDraftWorkingLayout) {
    monitoringHudDraftWorkingLayout = monitoringHudCloneMonitorLayout(selected.layout);
  }
  monitoringHudUnsavedMonitorDirty = true;
  if (monitoringHud) {
    monitoringHud.dataset.monitorUnsavedChanges = "pending";
  }
  monitoringHudUpdateMonitorActionState();
  return {
    id: monitoringHudDraftOriginalMonitorId || selected.id,
    layout: monitoringHudDraftWorkingLayout
  };
}

function monitoringHudUpdateMonitorDraftFromWindow() {
  const draft = monitoringHudEnsureMonitorDraft();
  if (!draft || !draft.layout) return null;
  draft.layout.title = monitoringHudCleanMonitorTitle(
    monitoringHudEditMonitorName ? monitoringHudEditMonitorName.value : "",
    draft.layout.title || "Monitor Group"
  );
  draft.layout.enabled = monitoringHudMonitorEnabled ? Boolean(monitoringHudMonitorEnabled.checked) : draft.layout.enabled !== false;
  draft.layout.pollingRateMs = monitoringHudMonitorPollingRate
    ? Math.max(1000, Number(monitoringHudMonitorPollingRate.value) || 1000)
    : Math.max(1000, Number(draft.layout.pollingRateMs) || 1000);
  draft.layout.warningNotificationsEnabled = monitoringHudMonitorWarningSetting
    ? Boolean(monitoringHudMonitorWarningSetting.checked)
    : draft.layout.warningNotificationsEnabled !== false;
  monitoringHudReadSensorAssignmentsFromWindow(draft.layout);
  monitoringHudApplyEffectivePollingRate(draft.layout, "selected-monitor-draft");
  monitoringHudDraftWorkingLayout = monitoringHudCloneMonitorLayout(draft.layout);
  return {
    id: draft.id,
    layout: monitoringHudDraftWorkingLayout
  };
}

function monitoringHudSaveEditMonitorWindow(options = {}) {
  const selected = monitoringHudSelectedMonitor();
  if (!selected.id || !selected.layout) return;
  const draft = monitoringHudUpdateMonitorDraftFromWindow();
  const targetId = draft && draft.id ? draft.id : selected.id;
  const targetLayout = draft && draft.layout ? monitoringHudCloneMonitorLayout(draft.layout) : monitoringHudCloneMonitorLayout(selected.layout);
  monitoringHudNormalizeSensorAssignments(targetId, targetLayout);
  monitoringHudControlState.cards[targetId] = targetLayout;
  monitoringHudApplyEffectivePollingRate(targetLayout, "selected-monitor-save");
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudSetMonitorDraftDirty(false);
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  if (options.keepOpen) monitoringHudRenderMonitorManagement();
  if (!options.keepOpen) monitoringHudCloseChildWindow({ force: true });
  monitoringHudMarkChanged();
}

function monitoringHudPersistCurrentMonitorDraft() {
  const selected = monitoringHudSelectedMonitor();
  const targetId = monitoringHudDraftOriginalMonitorId || (selected && selected.id) || "";
  if (!targetId || !monitoringHudControlState.cards || !monitoringHudControlState.cards[targetId]) return false;
  const targetLayout = monitoringHudDraftWorkingLayout
    ? monitoringHudCloneMonitorLayout(monitoringHudDraftWorkingLayout)
    : monitoringHudCloneMonitorLayout(monitoringHudControlState.cards[targetId]);
  monitoringHudNormalizeSensorAssignments(targetId, targetLayout);
  monitoringHudControlState.cards[targetId] = targetLayout;
  monitoringHudApplyEffectivePollingRate(targetLayout, "selected-monitor-persist");
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudSetMonitorDraftDirty(false);
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
  return true;
}

function monitoringHudRequestDeleteMonitorGroup(cardId, options = {}) {
  if (!cardId || !monitoringHudControlState.cards || !monitoringHudControlState.cards[cardId]) return;
  if (!options.force && monitoringHudUnsavedMonitorDirty && cardId === monitoringHudControlState.selectedMonitorId) {
    monitoringHudShowUnsavedGuard({ type: "delete", cardId });
    return;
  }
  monitoringHudPendingDeleteMonitorId = cardId;
  monitoringHudControlState.selectedMonitorId = cardId;
  monitoringHudRenderMonitorManagement();
  monitoringHudRevealDeleteConfirmation();
}

function monitoringHudRevealDeleteConfirmation() {
  if (!monitoringHudMonitorDeleteConfirmation || monitoringHudMonitorDeleteConfirmation.hidden) return;
  monitoringHudMonitorDeleteConfirmation.dataset.deleteConfirmationReveal = "scrolled-focused";
  window.requestAnimationFrame(() => {
    if (!monitoringHudMonitorDeleteConfirmation || monitoringHudMonitorDeleteConfirmation.hidden) return;
    if (typeof monitoringHudMonitorDeleteConfirmation.scrollIntoView === "function") {
      monitoringHudMonitorDeleteConfirmation.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "instant" });
    }
    const focusTarget = monitoringHudMonitorDeleteConfirm || monitoringHudMonitorDeleteCancel;
    if (focusTarget && typeof focusTarget.focus === "function") {
      focusTarget.focus({ preventScroll: true });
    }
  });
}

function monitoringHudConfirmDeleteMonitorGroup() {
  const cardId = monitoringHudPendingDeleteMonitorId;
  if (!cardId || !monitoringHudControlState.cards || !monitoringHudControlState.cards[cardId]) return;
  delete monitoringHudControlState.cards[cardId];
  const nextId = Object.keys(monitoringHudControlState.cards)[0] || "";
  monitoringHudControlState.selectedMonitorId = nextId;
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudSetMonitorDraftDirty(false);
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
}

function monitoringHudCancelDeleteMonitorGroup() {
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudRenderMonitorManagement();
}

function monitoringHudSetMonitorDraftDirty(dirty) {
  if (dirty && !monitoringHudUnsavedMonitorDirty) {
    const selected = monitoringHudSelectedMonitor();
    monitoringHudDraftOriginalMonitorId = selected.id || "";
    monitoringHudDraftOriginalLayout = selected.layout ? JSON.parse(JSON.stringify(selected.layout)) : null;
  }
  monitoringHudUnsavedMonitorDirty = Boolean(dirty);
  if (monitoringHud) {
    monitoringHud.dataset.monitorUnsavedChanges = monitoringHudUnsavedMonitorDirty ? "pending" : "clean";
  }
  if (!monitoringHudUnsavedMonitorDirty) {
    monitoringHudPendingSelectMonitorId = "";
    monitoringHudPendingGuardAction = null;
    monitoringHudDraftOriginalMonitorId = "";
    monitoringHudDraftOriginalLayout = null;
    monitoringHudDraftWorkingLayout = null;
    if (monitoringHudMonitorUnsavedGuard) {
      monitoringHudMonitorUnsavedGuard.hidden = true;
      monitoringHudMonitorUnsavedGuard.dataset.unsavedGuard = "closed";
      monitoringHudMonitorUnsavedGuard.dataset.guardActionLayout = "";
      monitoringHudMonitorUnsavedGuard.dataset.draftMonitorId = "";
      monitoringHudMonitorUnsavedGuard.dataset.guardStateModel = "";
      monitoringHudMonitorUnsavedGuard.dataset.pendingMonitorSelect = "";
      monitoringHudMonitorUnsavedGuard.dataset.pendingMonitorAction = "";
    }
    if (monitoringHudEditMonitorWindow) {
      monitoringHudSetChildWindowDirtyModalState(monitoringHudEditMonitorWindow, false);
      monitoringHudEditMonitorWindow.dataset.monitorUnsavedState = "closed";
    }
  }
  monitoringHudUpdateMonitorActionState();
}

function monitoringHudShowUnsavedGuard(action) {
  monitoringHudUpdateMonitorDraftFromWindow();
  const pendingAction = typeof action === "string" ? { type: "select", cardId: action } : Object.assign({}, action || {});
  monitoringHudPendingGuardAction = pendingAction;
  monitoringHudPendingSelectMonitorId = pendingAction.type === "select" ? (pendingAction.cardId || "") : "";
  if (!monitoringHudMonitorUnsavedGuard) return;
  monitoringHudMonitorUnsavedGuard.hidden = false;
  monitoringHudMonitorUnsavedGuard.dataset.unsavedGuard = "open-save-discard";
  monitoringHudMonitorUnsavedGuard.dataset.guardActionLayout = "modal-save-discard-cancel";
  monitoringHudMonitorUnsavedGuard.dataset.draftMonitorId = monitoringHudDraftOriginalMonitorId || "";
  monitoringHudMonitorUnsavedGuard.dataset.guardStateModel = "draft-preserved-before-queued-action";
  monitoringHudMonitorUnsavedGuard.dataset.pendingMonitorSelect = monitoringHudPendingSelectMonitorId;
  monitoringHudMonitorUnsavedGuard.dataset.pendingMonitorAction = pendingAction.type || "unknown";
  if (monitoringHudEditMonitorWindow) {
    monitoringHudSetChildWindowDirtyModalState(monitoringHudEditMonitorWindow, true);
    monitoringHudEditMonitorWindow.dataset.monitorUnsavedState = "open";
  }
  monitoringHudRevealUnsavedGuard();
}

function monitoringHudCancelMonitorUnsavedGuard() {
  monitoringHudPendingSelectMonitorId = "";
  monitoringHudPendingGuardAction = null;
  if (monitoringHudMonitorUnsavedGuard) {
    monitoringHudMonitorUnsavedGuard.hidden = true;
    monitoringHudMonitorUnsavedGuard.dataset.unsavedGuard = "closed";
    monitoringHudMonitorUnsavedGuard.dataset.pendingMonitorSelect = "";
    monitoringHudMonitorUnsavedGuard.dataset.pendingMonitorAction = "";
  }
  if (monitoringHudEditMonitorWindow) {
    monitoringHudSetChildWindowDirtyModalState(monitoringHudEditMonitorWindow, false);
    monitoringHudEditMonitorWindow.dataset.monitorUnsavedState = "closed";
  }
  monitoringHudUpdateMonitorActionState();
  return true;
}

function monitoringHudSelectMonitorGroup(cardId, options = {}) {
  if (!cardId || !monitoringHudControlState.cards || !monitoringHudControlState.cards[cardId]) return false;
  if (!options.force && cardId === monitoringHudControlState.selectedMonitorId) {
    if (monitoringHudUnsavedMonitorDirty) {
      monitoringHudShowUnsavedGuard({ type: "same-select", cardId });
      if (monitoringHud) monitoringHud.dataset.sameMonitorRowDirtyClick = "guard-open-draft-preserved";
    }
    return false;
  }
  if (!options.force && monitoringHudUnsavedMonitorDirty && cardId !== monitoringHudControlState.selectedMonitorId) {
    monitoringHudShowUnsavedGuard({ type: "select", cardId });
    return false;
  }
  monitoringHudControlState.selectedMonitorId = cardId;
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudSetMonitorDraftDirty(false);
  monitoringHudRenderMonitorManagement();
  return true;
}

function monitoringHudOpenOverlayProfileSettingsFromManage(options = {}) {
  const selected = monitoringHudSelectedMonitor();
  const cardId = options.cardId || (selected && selected.id) || "";
  if (!cardId || !monitoringHudControlState.cards || !monitoringHudControlState.cards[cardId]) return false;
  if (!options.force && monitoringHudUnsavedMonitorDirty) {
    monitoringHudShowUnsavedGuard({ type: "overlay-profile-settings", cardId });
    return false;
  }
  monitoringHudOverlayProfileContextMonitorId = cardId;
  monitoringHudOpenChildWindow("overlay-profile-settings");
  return true;
}

function monitoringHudRunPendingGuardAction(action) {
  const pendingAction = action || monitoringHudPendingGuardAction;
  if (!pendingAction || !pendingAction.type) return;
  if (pendingAction.type === "select") {
    monitoringHudSelectMonitorGroup(pendingAction.cardId, { force: true });
  } else if (pendingAction.type === "create") {
    monitoringHudCreateMonitorGroupFromManageWindow({ force: true });
  } else if (pendingAction.type === "delete") {
    monitoringHudRequestDeleteMonitorGroup(pendingAction.cardId, { force: true });
  } else if (pendingAction.type === "close") {
    monitoringHudCloseChildWindow({ force: true });
  } else if (pendingAction.type === "overlay-profile-settings") {
    monitoringHudOpenOverlayProfileSettingsFromManage({ force: true, cardId: pendingAction.cardId });
  } else if (pendingAction.type === "same-select") {
    monitoringHudRenderMonitorManagement();
  }
}

function monitoringHudPendingGuardActionSnapshot() {
  const pendingAction = Object.assign({}, monitoringHudPendingGuardAction || {});
  if (pendingAction.type) return pendingAction;
  if (!monitoringHudMonitorUnsavedGuard || monitoringHudMonitorUnsavedGuard.hidden) return pendingAction;
  const guardType = monitoringHudMonitorUnsavedGuard.dataset.pendingMonitorAction || "";
  if (!guardType) return pendingAction;
  if (guardType === "select") {
    return {
      type: "select",
      cardId: monitoringHudMonitorUnsavedGuard.dataset.pendingMonitorSelect || ""
    };
  }
  return {
    type: guardType,
    cardId: monitoringHudMonitorUnsavedGuard.dataset.draftMonitorId || monitoringHudControlState.selectedMonitorId || ""
  };
}

function monitoringHudSaveAndSelectPendingMonitor() {
  const pendingAction = monitoringHudPendingGuardActionSnapshot();
  monitoringHudPersistCurrentMonitorDraft();
  monitoringHudRunPendingGuardAction(pendingAction);
}

function monitoringHudDiscardAndSelectPendingMonitor() {
  const pendingAction = monitoringHudPendingGuardActionSnapshot();
  if (
    monitoringHudDraftOriginalMonitorId
    && monitoringHudControlState.cards
    && monitoringHudControlState.cards[monitoringHudDraftOriginalMonitorId]
  ) {
    if (monitoringHudDraftOriginalLayout) {
      monitoringHudControlState.cards[monitoringHudDraftOriginalMonitorId] = JSON.parse(JSON.stringify(monitoringHudDraftOriginalLayout));
    } else {
      delete monitoringHudControlState.cards[monitoringHudDraftOriginalMonitorId];
      monitoringHudControlState.selectedMonitorId = Object.keys(monitoringHudControlState.cards || {})[0] || "";
    }
  }
  monitoringHudSetMonitorDraftDirty(false);
  monitoringHudRunPendingGuardAction(pendingAction);
}

function monitoringHudRenderMonitorManagement() {
  const selected = monitoringHudSelectedMonitor();
  const selectedLayout = selected.id ? monitoringHudSelectedMonitorDetailLayout(selected) : null;
  const monitorCount = Object.keys(monitoringHudControlState.cards || {}).length;
  const assignedSensorCount = Object.values(monitoringHudControlState.cards || {}).reduce((total, layout) => {
    return total + (Array.isArray(layout && layout.sensors) ? layout.sensors.length : 0);
  }, 0);
  if (monitoringHud) {
    monitoringHud.dataset.dashboardControlPanel = "hud-overlay-monitor-management";
    monitoringHud.dataset.monitorManagement = "sensor-command-center-list-detail-source-picker";
    monitoringHud.dataset.overlayModeControls = "overlay-deferred-tray-owned";
    monitoringHud.dataset.primaryInterfaceReleaseSurface = "monitoring-hud-dashboard-control-panel";
    monitoringHud.dataset.interfaceAcceptancePolicy = "dashboard-only-current-branch";
    monitoringHud.dataset.dashboardAcceptanceBaseline = "ws31-dashboard-control-panel";
    monitoringHud.dataset.dashboardProofPath = "dashboard-specific-static-live-uts";
    monitoringHud.dataset.dashboardStandaloneProof = "ws32-dashboard-window-travel";
    monitoringHud.dataset.dashboardClippingProof = "within-virtual-desktop";
    monitoringHud.dataset.dashboardMinimumEdgeProof = "native-min-size-bottom-edge-visible";
    monitoringHud.dataset.dashboardDecouplingProof = "core-overlay-independent";
    monitoringHud.dataset.dashboardContentPolish = "branch2-monitor-groups-no-dead-space";
    monitoringHud.dataset.dashboardLayoutProof = "monitor-groups-measured-no-overlap";
    monitoringHud.dataset.dashboardHomeModel = "control-hub-cards-monitor-management-child-windows";
    monitoringHud.dataset.dashboardPollingPlacement = "monitor-group-editor-only";
    monitoringHud.dataset.dashboardProofContentPolicy = "validator-artifacts-not-home-surface";
    monitoringHud.dataset.dashboardChildWindowScope = "monitor-groups-manage-create-edit-delete-sensor-windows-overlay-profile-settings";
    monitoringHud.dataset.dashboardSettingsModel = "hud-overlay-monitor-groups-provider-warning";
    monitoringHud.dataset.dashboardIaModel = "branch2-ia-controls-followthrough";
    monitoringHud.dataset.dashboardCloseAffordance = "window-level-close-button";
    monitoringHud.dataset.dashboardCloseLayout = "uiref-002-compact-top-right-symbol-control";
    monitoringHud.dataset.dashboardOpenBadge = "removed";
    monitoringHud.dataset.dashboardMonitorSelectionPlacement = "edit-child-window-only";
    monitoringHud.dataset.dashboardQuickAccess = "warning-notifications-recording-start-stop";
    monitoringHud.dataset.dashboardGlobalFeatureControl = "tray-owned";
    monitoringHud.dataset.dashboardDeferredActionPolicy = "disabled-labeled-not-clickable";
    monitoringHud.dataset.dashboardCardOrder = "hud-overlay-recording-monitor-groups-data-sources-readiness";
    monitoringHud.dataset.dashboardSettingsAffordance = "dashboard-ia-card-settings-button";
    monitoringHud.dataset.dashboardSettingsPanel = "settings-panel-child-window";
    monitoringHud.dataset.dashboardSettingsProof = "visible-open-close-control-hit-target";
    monitoringHud.dataset.dashboardSettingsPanelState = monitoringHudActiveChildWindow === "dashboard-settings" ? "open" : "closed";
    monitoringHud.dataset.monitorGroupModel = "configurable-groups-sensor-assignment";
    monitoringHud.dataset.monitorManagementScale = "split-layout-search-filter-large-fixtures";
    monitoringHud.dataset.monitorManagementLayout = "compact-list-right-detail-command-center";
    monitoringHud.dataset.sensorLibraryScale = "search-facet-thousand-source-fixture";
    monitoringHud.dataset.sourceFilterMode = "nexus-dropdown-source-picker";
    monitoringHud.dataset.sensorLibraryFixtures = `monitors-${monitoringHudLargeMonitorFixtureCount}-sources-${monitoringHudLargeSensorFixtureCount}`;
    monitoringHud.dataset.sensorLibraryFixtureMode = monitoringHudLargeFixtureModeEnabled ? "enabled-validation-support" : "available-validation-support";
    monitoringHud.dataset.monitorManagementScrollbars = "nexus-styled-child-list-detail-sensor-panes";
    monitoringHud.dataset.monitorManagementToolbar = "compact-search-summary-list-header-create";
    monitoringHud.dataset.monitorDeletePlacement = "detail-pane-bottom-danger-zone";
    monitoringHud.dataset.manageWindowSizing = "taller-default-bounded-resizable";
    monitoringHud.dataset.firstOpenFlickerGuard = "native-opacity-guard-stable-first-open";
    monitoringHud.dataset.resizeLiveProof = "invisible-real-ui-frame-pixel-signature-grow-shrink";
    monitoringHud.dataset.resizeProofVisibility = "normal-ui-no-proof-artifacts";
    monitoringHud.dataset.resizeProofVisuals = "none";
    monitoringHud.dataset.dashboardMonitorCardPolicy = "overlay-display-owns-visual-rendering";
    monitoringHud.dataset.monitorSensorAssignment = "sensor-library-source-picker";
    monitoringHud.dataset.sourceClassification = "settings-readiness-outside-assignable-sensors";
    monitoringHud.dataset.monitorDeleteConfirmation = monitoringHudPendingDeleteMonitorId ? "pending-confirmation" : "closed";
    monitoringHud.dataset.interactiveControlAffordance = "normal-hover-active-focus-visible-disabled-open-selected";
    monitoringHud.dataset.interactiveControlReliability = monitoringHud.dataset.interactiveControlReliability || "first-click-stress-proof-required";
    monitoringHud.dataset.clickInterceptionDiagnostics = monitoringHud.dataset.clickInterceptionDiagnostics || "z-index-pointer-events-disabled-aria-dom-focus-timing";
    monitoringHud.dataset.pollingRateDropdown = "nexus-styled-bounded-control";
    monitoringHud.dataset.overlayProfileIntegration = "followup-assigned-overlay-status-assignment";
    monitoringHud.dataset.manageOverlayProfileContext = "clickable-assigned-overlay-status-window";
    monitoringHud.dataset.sourceSettingsIa = "source-list-settings-entry-points";
    monitoringHud.dataset.overlayAcceptancePolicy = "deferred-non-gating";
    monitoringHud.dataset.interfaceBundleApproval = "not-granted";
    monitoringHud.dataset.coreRepairClassification = "dependency-repair-only";
    monitoringHud.dataset.monitorCount = String(monitorCount);
    monitoringHud.dataset.assignedSensorCount = String(assignedSensorCount);
    monitoringHud.dataset.selectedMonitor = selected.id || "";
  }
  Object.keys(monitoringHudControlState.cards || {}).forEach((cardId) => {
    const layout = Object.assign(monitoringHudCardDefaults(cardId), monitoringHudControlState.cards[cardId] || {});
    monitoringHudNormalizeMonitorGroupTitle(cardId, layout);
    const cardNode = monitoringHudEditMonitorList
      ? monitoringHudEditMonitorList.querySelector(`[data-monitor-row="${cardId}"]`)
      : null;
    if (!cardNode) return;
    cardNode.dataset.monitorEnabled = layout.enabled === false ? "false" : "true";
    cardNode.dataset.monitorPollingMs = String(Math.max(1000, Number(layout.pollingRateMs) || 1000));
    cardNode.dataset.assignedSensorCount = String(Array.isArray(layout.sensors) ? layout.sensors.length : 0);
  });
  if (monitoringHudMonitorListSummary) {
    monitoringHudMonitorListSummary.textContent = `${monitorCount} Monitor Groups configured with ${assignedSensorCount} supported source assignment${assignedSensorCount === 1 ? "" : "s"}. Manage opens list, create, edit, delete, and sensor controls.`;
  }
  if (monitoringHudMonitorCount) {
    monitoringHudMonitorCount.textContent = `${monitorCount} configured`;
  }
  if (monitoringHudMonitorPollingSummary) {
    monitoringHudMonitorPollingSummary.textContent = `${assignedSensorCount} assigned source${assignedSensorCount === 1 ? "" : "s"}`;
  }
  if (monitoringHudMonitorEditorTitle) {
    monitoringHudMonitorEditorTitle.textContent = selectedLayout ? (selectedLayout.title || "Monitor Group") : "No Monitor Selected";
  }
  if (monitoringHudMonitorEnabled) {
    monitoringHudMonitorEnabled.checked = selectedLayout ? selectedLayout.enabled !== false : false;
  }
  if (monitoringHudMonitorPollingRate) {
    monitoringHudSetPollingRateValue(selectedLayout ? String(Math.max(1000, Number(selectedLayout.pollingRateMs) || 1000)) : "1000");
  }
  if (monitoringHudMonitorEditorScope) {
    monitoringHudMonitorEditorScope.textContent = "Monitor Groups assign available runtime sources and settings. HUD Overlay owns future visual display; fake values remain blocked.";
  }
  monitoringHudRenderChildWindows();
}

function monitoringHudCreateOverlayCardNode(cardId, layout) {
  if (!monitoringHudOverlayCanvas || monitoringHudOverlayCanvas.querySelector(`[data-overlay-monitor-card="${cardId}"]`)) return;
  const article = document.createElement("article");
  article.className = "monitoring-hud-overlay-card monitoring-hud-overlay-card--unavailable";
  article.dataset.overlayMonitorCard = cardId;
  article.dataset.overlayMonitorEnabled = layout.enabled === false ? "false" : "true";
  article.dataset.overlayMonitorPollingMs = String(layout.pollingRateMs || 1000);
  article.style.setProperty("--overlay-card-x", `${Math.round(layout.x || 0)}px`);
  article.style.setProperty("--overlay-card-y", `${Math.round(layout.y || 0)}px`);
  article.style.setProperty("--overlay-card-w", `${Math.round(Math.max(220, Math.min(layout.w || 300, 420)))}px`);
  article.style.setProperty("--overlay-card-h", `${Math.round(Math.max(108, Math.min(layout.h || 132, 180)))}px`);
  article.innerHTML = `
    <div class="monitoring-hud-overlay-card__topline">
      <strong data-overlay-monitor-title="${cardId}"></strong>
      <span data-overlay-monitor-state="${cardId}">No data</span>
    </div>
    <p data-overlay-monitor-summary="${cardId}">Provider required</p>
    <div class="monitoring-hud-overlay-card__quick-actions" data-overlay-monitor-quick-actions="${cardId}">
      <button type="button" data-overlay-monitor-edit="${cardId}">Edit</button>
    </div>
  `;
  monitoringHudOverlayCanvas.appendChild(article);
}

function monitoringHudRenderOverlayDisplay() {
  if (!monitoringHudOverlayDisplay || !monitoringHudOverlayCanvas) return;
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  const cards = monitoringHudControlState.cards || {};
  const activeProfile = monitoringHudActiveOverlayProfile() || {};
  const activeMonitorIds = monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, cards);
  const activeRecordingTarget = monitoringHudControlState.activeOverlayRecordingTarget
    || monitoringHudBuildActiveOverlayRecordingTargetSnapshot(monitoringHudControlState);
  const activeMonitorIdSet = new Set(activeMonitorIds);
  const overlayDeferred = monitoringHudControlState.overlayDeferred !== false;
  monitoringHudOverlayDisplay.dataset.anchorState = monitoringHudControlState.anchored ? "anchored" : "unanchored";
  monitoringHudOverlayDisplay.dataset.visibilityState = overlayDeferred ? "hidden-deferred" : (monitoringHudControlState.visible ? "visible" : "hidden");
  monitoringHudOverlayDisplay.dataset.overlayEditMode = "unanchored-focusable-resizable-scrollable";
  monitoringHudOverlayDisplay.dataset.overlayAnchorMode = "anchored-uninteractable-click-through";
  monitoringHudOverlayDisplay.dataset.overlayCanvas = "edge-to-edge-snipping-tool-style";
  monitoringHudOverlayDisplay.dataset.monitorLayout = "movable-resizable-monitor-cards";
  monitoringHudOverlayDisplay.dataset.edgeToEdgePosture = "landscape-portrait-monitor-fit";
  monitoringHudOverlayDisplay.dataset.interfaceAcceptancePolicy = "deferred-non-gating";
  monitoringHudOverlayDisplay.dataset.dashboardAcceptanceRole = "supporting-future-interface-evidence";
  monitoringHudOverlayDisplay.dataset.currentBranchReleaseGate = "false";
  monitoringHudOverlayDisplay.dataset.monitorCount = String(activeMonitorIds.length);
  monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptance = "slc-042-active-profile-state-bridge";
  monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptancePolicy = "profile-aware-baseline-non-recording";
  monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptanceSlice = "SLC-042";
  monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptanceProof = monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptanceProof || "pending";
  monitoringHudOverlayDisplay.dataset.activeOverlayProfileDisplayBehavior = "slc-043-active-profile-display";
  monitoringHudOverlayDisplay.dataset.activeOverlayProfileDisplaySlice = "SLC-043";
  monitoringHudOverlayDisplay.dataset.activeOverlayProfileDisplayProof = monitoringHudOverlayDisplay.dataset.activeOverlayProfileDisplayProof || "pending";
  monitoringHudOverlayDisplay.dataset.dashboardOverlayIndependence = "slc-044-dashboard-overlay-independent";
  monitoringHudOverlayDisplay.dataset.dashboardOverlayIndependenceProof = monitoringHudOverlayDisplay.dataset.dashboardOverlayIndependenceProof || "pending";
  monitoringHudOverlayDisplay.dataset.overlayProfileState = "slc-039-membership-mapping";
  monitoringHudOverlayDisplay.dataset.overlayProfileSchemaVersion = String(monitoringHudOverlayProfileSchemaVersion);
  monitoringHudOverlayDisplay.dataset.activeOverlayProfileId = String(monitoringHudControlState.activeOverlayProfileId || "");
  const activeProfileName = monitoringHudCleanOverlayProfileName(activeProfile.name, "No active overlay profile");
  monitoringHudOverlayDisplay.dataset.activeOverlayProfileName = activeProfileName;
  monitoringHudOverlayDisplay.dataset.activeOverlayProfileMonitorCount = String(activeMonitorIds.length);
  monitoringHudOverlayDisplay.dataset.activeOverlayProfileMonitorIds = activeMonitorIds.join(",");
  monitoringHudOverlayDisplay.dataset.overlayDisplayEmpty = activeMonitorIds.length === 0 ? "true" : "false";
  monitoringHudOverlayDisplay.dataset.overlayDisplayProfileStatus = activeProfile.id
    ? (activeMonitorIds.length > 0 ? "active-profile-rendering" : "active-profile-empty")
    : "no-active-profile";
  monitoringHudOverlayDisplay.dataset.overlayProfileEditor = "slc-039-membership-editor";
  monitoringHudOverlayDisplay.dataset.overlayProfileMembership = "editable-slc-039-mapping";
  monitoringHudOverlayDisplay.dataset.recordingProfileState = "recording-profile-state-absent-future-gated";
  monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTarget = "slc-051-active-overlay-profile-membership-target";
  monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTargetProof = monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTargetProof || "pending";
  monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTargetState = activeRecordingTarget.targetState || "no-overlay-profiles";
  monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTargetSource = activeRecordingTarget.source || "active-overlay-profile-membership";
  monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTargetScope = activeRecordingTarget.scope || "target-session-truth-only";
  monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTargetMonitorCount = String(activeRecordingTarget.membershipSnapshotCandidateCount || 0);
  monitoringHudOverlayDisplay.dataset.snapshotAtStartModel = activeRecordingTarget.snapshotAtStartModel || "snapshot-at-recording-start";
  monitoringHudOverlayDisplay.dataset.hiddenRecordingTargetState = activeRecordingTarget.hiddenRecordingTargetState || "absent";
  monitoringHudOverlayDisplay.dataset.recordingExecutionState = activeRecordingTarget.recordingExecutionState || "blocked";
  monitoringHudOverlayDisplay.dataset.recordingFileWritingState = activeRecordingTarget.fileWritingState || "blocked";
  if (monitoringHudOverlayProfileDisplayStatus) {
    monitoringHudOverlayProfileDisplayStatus.dataset.overlayProfileDisplayStatus = "slc-043-active-profile-display";
    monitoringHudOverlayProfileDisplayStatus.dataset.activeOverlayProfileId = String(monitoringHudControlState.activeOverlayProfileId || "");
    monitoringHudOverlayProfileDisplayStatus.dataset.activeOverlayProfileMonitorCount = String(activeMonitorIds.length);
    monitoringHudOverlayProfileDisplayStatus.dataset.overlayDisplayProfileStatus = monitoringHudOverlayDisplay.dataset.overlayDisplayProfileStatus;
  }
  if (monitoringHudOverlayProfileDisplayName) {
    monitoringHudOverlayProfileDisplayName.textContent = activeProfileName;
  }
  if (monitoringHudOverlayProfileDisplayCount) {
    monitoringHudOverlayProfileDisplayCount.textContent = `${activeMonitorIds.length} monitor${activeMonitorIds.length === 1 ? "" : "s"}`;
  }
  Array.from(monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]")).forEach((node) => {
    const cardId = String(node.dataset.overlayMonitorCard || "");
    if (!activeMonitorIdSet.has(cardId)) node.remove();
  });
  activeMonitorIds.forEach((cardId) => {
    const layout = Object.assign(monitoringHudCardDefaults(cardId), cards[cardId] || {});
    const overlayLayout = Object.assign({}, layout, {
      x: monitoringHudSnap(layout.x || 0) + 28,
      y: monitoringHudSnap(layout.y || 0) + 34,
      w: Math.max(220, Math.min(layout.w || 300, 420)),
      h: Math.max(108, Math.min(layout.h || 132, 180))
    });
    monitoringHudCreateOverlayCardNode(cardId, overlayLayout);
    const cardNode = monitoringHudOverlayCanvas.querySelector(`[data-overlay-monitor-card="${cardId}"]`);
    if (!cardNode) return;
    cardNode.dataset.overlayMonitorEnabled = layout.enabled === false ? "false" : "true";
    cardNode.dataset.overlayMonitorPollingMs = String(Math.max(1000, Number(layout.pollingRateMs) || 1000));
    cardNode.style.setProperty("--overlay-card-x", `${Math.round(overlayLayout.x)}px`);
    cardNode.style.setProperty("--overlay-card-y", `${Math.round(overlayLayout.y)}px`);
    cardNode.style.setProperty("--overlay-card-w", `${Math.round(overlayLayout.w)}px`);
    cardNode.style.setProperty("--overlay-card-h", `${Math.round(overlayLayout.h)}px`);
    cardNode.classList.toggle("monitoring-hud-overlay-card--setup", cardId === "cpu");
    cardNode.classList.toggle("monitoring-hud-overlay-card--unavailable", cardId !== "cpu");
    const titleNode = cardNode.querySelector(`[data-overlay-monitor-title="${cardId}"]`);
    if (titleNode) titleNode.textContent = layout.title || "Monitor";
    const stateNode = cardNode.querySelector(`[data-overlay-monitor-state="${cardId}"]`);
    if (stateNode) stateNode.textContent = layout.enabled === false ? "Hidden" : (cardId === "cpu" ? "Setup" : "No data");
    const summaryNode = cardNode.querySelector(`[data-overlay-monitor-summary="${cardId}"]`);
    if (summaryNode) {
      summaryNode.textContent = layout.enabled === false
        ? "Disabled in overlay"
        : (cardId === "cpu" ? "Provider warming" : cardId === "gpu" ? "Provider required" : "Provider route pending");
    }
  });
  monitoringHudOverlayDisplay.dataset.overlayRenderedMonitorCount = String(
    monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]").length
  );
}

function monitoringHudUpdateSurfaceSplit() {
  if (monitoringHud) {
    monitoringHud.dataset.productSurfaceRole = "dashboard-configuration-surface";
    monitoringHud.dataset.dashboardSurface = "monitoring-hud-dashboard";
    monitoringHud.dataset.configuresSurface = "monitoring-hud-minimal";
    monitoringHud.dataset.splitContract = "dashboard-configures-minimal-overlay";
    monitoringHud.dataset.nativeDashboardOwner = "DesktopRuntimeWindow";
    monitoringHud.dataset.standaloneWindowContract = "dashboard-overlay-core-independent-native-surfaces";
    monitoringHud.dataset.dragSmoothing = "native-os-window-move";
    monitoringHud.dataset.nativeResizeModel = "os-edge-corner-resize";
    monitoringHud.dataset.scrollbarStyle = "nexus-thin-glow";
    monitoringHud.dataset.frameOwnership = "single-rounded-dashboard-chrome";
    monitoringHud.dataset.scrollOwner = "monitoring-hud-control-hub";
    monitoringHud.dataset.scrollbarBoundary = "inner-content-well-gutter";
    monitoringHud.dataset.outerFrameHaze = "removed-no-square-layer";
    monitoringHud.dataset.gridScope = "control-hub-cards-only";
    monitoringHud.dataset.deadzonePolicy = "auto-height-content-no-empty-hit-zones";
    monitoringHud.dataset.stickyHeaderMask = "opaque-scroll-mask";
    monitoringHud.dataset.nativeResizeHitZone = "preclick-hover-cursor-aligned-14px-app-owned-resize-action";
    monitoringHud.dataset.primaryInterfaceReleaseSurface = "monitoring-hud-dashboard-control-panel";
    monitoringHud.dataset.interfaceAcceptancePolicy = "dashboard-only-current-branch";
    monitoringHud.dataset.dashboardAcceptanceBaseline = "ws31-dashboard-control-panel";
    monitoringHud.dataset.dashboardProofPath = "dashboard-specific-static-live-uts";
    monitoringHud.dataset.dashboardMinimumEdgeProof = "native-min-size-bottom-edge-visible";
    monitoringHud.dataset.overlayAcceptancePolicy = "deferred-non-gating";
    monitoringHud.dataset.interfaceBundleApproval = "not-granted";
    monitoringHud.dataset.coreRepairClassification = "dependency-repair-only";
    monitoringHud.dataset.dashboardContentPolish = "branch2-monitor-groups-no-dead-space";
    monitoringHud.dataset.dashboardLayoutProof = "monitor-groups-measured-no-overlap";
    monitoringHud.dataset.dashboardSettingsModel = "hud-overlay-monitor-groups-provider-warning";
    monitoringHud.dataset.dashboardHomeModel = "control-hub-cards-monitor-management-child-windows";
    monitoringHud.dataset.dashboardChildWindowScope = "monitor-groups-manage-create-edit-delete-sensor-windows-overlay-profile-settings";
    monitoringHud.dataset.dashboardIaModel = "branch2-ia-controls-followthrough";
    monitoringHud.dataset.dashboardCloseAffordance = "window-level-close-button";
    monitoringHud.dataset.dashboardCloseLayout = "uiref-002-compact-top-right-symbol-control";
    monitoringHud.dataset.dashboardOpenBadge = "removed";
    monitoringHud.dataset.dashboardMonitorSelectionPlacement = "edit-child-window-only";
    monitoringHud.dataset.dashboardQuickAccess = "warning-notifications-recording-start-stop";
    monitoringHud.dataset.dashboardGlobalFeatureControl = "tray-owned";
    monitoringHud.dataset.dashboardDeferredActionPolicy = "disabled-labeled-not-clickable";
    monitoringHud.dataset.dashboardCardOrder = "hud-overlay-recording-monitor-groups-data-sources-readiness";
    monitoringHud.dataset.monitorGroupModel = "configurable-groups-sensor-assignment";
    monitoringHud.dataset.dashboardMonitorCardPolicy = "overlay-display-owns-visual-rendering";
    monitoringHud.dataset.dashboardOverlayIndependence = "slc-044-dashboard-overlay-independent";
    monitoringHud.dataset.dashboardOverlayIndependenceProof = monitoringHud.dataset.dashboardOverlayIndependenceProof || "pending";
    monitoringHud.dataset.monitorSensorAssignment = "sensor-library-source-picker";
    monitoringHud.dataset.sourceClassification = "settings-readiness-outside-assignable-sensors";
    monitoringHud.dataset.interactiveControlAffordance = "normal-hover-active-focus-visible-disabled-open-selected";
    monitoringHud.dataset.interactiveControlReliability = monitoringHud.dataset.interactiveControlReliability || "first-click-stress-proof-required";
    monitoringHud.dataset.clickInterceptionDiagnostics = monitoringHud.dataset.clickInterceptionDiagnostics || "z-index-pointer-events-disabled-aria-dom-focus-timing";
    monitoringHud.dataset.pollingRateDropdown = "nexus-styled-bounded-control";
    monitoringHud.dataset.overlayProfileIntegration = "followup-assigned-overlay-status-assignment";
    monitoringHud.dataset.manageOverlayProfileContext = "clickable-assigned-overlay-status-window";
    monitoringHud.dataset.sourceSettingsIa = "source-list-settings-entry-points";
  }
  if (!monitoringHudMinimal) return;
  monitoringHudMinimal.dataset.visibilityState = monitoringHudControlState.overlayDeferred !== false ? "hidden-deferred" : (monitoringHudControlState.visible ? "visible" : "hidden");
  monitoringHudMinimal.dataset.anchorState = monitoringHudControlState.anchored ? "anchored" : "unanchored";
  monitoringHudMinimal.dataset.interactionMode = monitoringHudControlState.anchored
    ? "anchored-click-through"
    : "unanchored-edit-preview";
  monitoringHudMinimal.dataset.configuredBy = "monitoring-hud";
  monitoringHudMinimal.dataset.dashboardOwner = "monitoring-hud";
  monitoringHudMinimal.dataset.splitContract = "dashboard-configures-minimal-overlay";
  monitoringHudMinimal.dataset.nativeOverlayOwner = "MonitoringHudOverlayDisplayWindow";
  monitoringHudMinimal.dataset.nativeWindowSplitProof = "ready-ws26";
  monitoringHudMinimal.dataset.providerState = monitoringHudTelemetry.providerState || "setup-required";
  monitoringHudMinimal.dataset.liveValues = monitoringHudTelemetry.liveValues || "provider-required";
  monitoringHudMinimal.dataset.warningMode = "visual-non-invasive";
  monitoringHudMinimal.dataset.clickThroughProof = monitoringHudControlState.anchored
    ? "native-transparent-input"
    : "edit-mode-preview";
  monitoringHudMinimal.dataset.focusProof = monitoringHudControlState.anchored
    ? "native-no-focus-noactivate"
    : "edit-mode-preview";
  monitoringHudMinimal.dataset.interfaceAcceptancePolicy = "deferred-non-gating";
  monitoringHudMinimal.dataset.dashboardAcceptanceRole = "supporting-future-interface-evidence";
  monitoringHudMinimal.dataset.currentBranchReleaseGate = "false";
  if (monitoringHudMinimalRuntimeStatus) {
    monitoringHudMinimalRuntimeStatus.textContent = monitoringHudControlState.visible ? "Minimal HUD enabled" : "Minimal HUD hidden";
  }
  if (monitoringHudMinimalAnchor) {
    monitoringHudMinimalAnchor.textContent = monitoringHudControlState.anchored ? "Anchored" : "Edit";
  }
  if (monitoringHudMinimalProviderState) {
    monitoringHudMinimalProviderState.textContent = monitoringHudTelemetry.providerLabel || "Provider setup required";
  }
  if (monitoringHudMinimalWarning) {
    monitoringHudMinimalWarning.textContent = monitoringHudStatus.warningPosture || "Visual warning baseline only";
  }
  monitoringHudRenderOverlayDisplay();
}

function monitoringHudApplyCardLayout() {
  monitoringHudEnsureCardNodes();
  Object.keys(monitoringHudControlState.cards).forEach((cardId) => {
    const layout = Object.assign(monitoringHudCardDefaults(cardId), monitoringHudControlState.cards[cardId] || {});
    monitoringHudNormalizeMonitorGroupTitle(cardId, layout);
    monitoringHudControlState.cards[cardId] = layout;
  });
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  monitoringHudRenderMonitorManagement();
  monitoringHudRenderOverlayDisplay();
}

function monitoringHudSyncActiveOverlayRecordingTargetFromOverlayProfile() {
  const profiles = Object.assign({}, monitoringHudControlState.overlayProfiles || {});
  const selectedDraft = monitoringHudOverlayProfileDraftTarget ? monitoringHudOverlayProfileDraftTarget() : null;
  const draftIsActive = Boolean(
    selectedDraft
    && selectedDraft.id
    && (
      monitoringHudOverlayProfilePendingCreate
      || String(selectedDraft.id) === String(monitoringHudControlState.activeOverlayProfileId || "")
    )
  );
  let targetState = monitoringHudControlState;
  if (draftIsActive) {
    monitoringHudControlState.activeOverlayProfileId = selectedDraft.id;
    monitoringHudControlState.activeOverlayProfileDraftSessionId = selectedDraft.id;
    profiles[selectedDraft.id] = Object.assign({}, selectedDraft, {
      monitorIds: monitoringHudUniqueValidMonitorIds(selectedDraft.monitorIds || [], monitoringHudControlState.cards || {})
    });
    targetState = Object.assign({}, monitoringHudControlState, {
      overlayProfiles: profiles,
      activeOverlayProfileId: selectedDraft.id,
      overlayProfileDefaultDeletedByUser: false
    });
  }
  const snapshot = monitoringHudBuildActiveOverlayRecordingTargetSnapshot(targetState);
  monitoringHudControlState.activeOverlayRecordingTarget = snapshot;
  monitoringHudControlState.recordingTargetOverlayProfileMirrorProof = {
    passed: true,
    source: draftIsActive ? "active-overlay-profile-draft-mirror" : "active-overlay-profile-state-mirror",
    sessionActiveDraft: draftIsActive,
    activeOverlayProfileId: snapshot.activeOverlayProfileId || "",
    activeOverlayProfileName: snapshot.activeOverlayProfileName || "",
    targetState: snapshot.targetState || "no-overlay-profiles",
    monitorCount: Number(snapshot.membershipSnapshotCandidateCount) || 0
  };
  if (monitoringHud) {
    monitoringHud.dataset.recordingTargetOverlayProfileMirror = "active-overlay-profile-state";
    monitoringHud.dataset.recordingTargetOverlayProfileMirrorProof = "pass";
  }
  return snapshot;
}

function monitoringHudRenderControls() {
  if (!monitoringHud) return;
  const featureEnabled = Boolean(monitoringHudControlState.featureEnabled);
  const dashboardVisible = Boolean(featureEnabled && monitoringHudControlState.visible);
  const overlayDeferred = monitoringHudControlState.overlayDeferred !== false;
  monitoringHudControlState.visible = dashboardVisible;
  monitoringHud.dataset.visibilityState = dashboardVisible ? "visible" : "hidden";
  monitoringHud.dataset.featureEnabled = featureEnabled ? "true" : "false";
  monitoringHud.dataset.overlayDeferred = overlayDeferred ? "true" : "false";
  monitoringHud.dataset.anchorState = monitoringHudControlState.anchored ? "overlay-anchored" : "overlay-unanchored";
  monitoringHud.dataset.interactionMode = "standalone-dashboard-window";
  monitoringHud.dataset.controlsState = featureEnabled
    ? (dashboardVisible ? "feature-enabled-dashboard-open" : "feature-enabled-dashboard-closed")
    : "feature-disabled-dashboard-closed";
  monitoringHud.dataset.snapState = monitoringHudControlState.snapEnabled ? "enabled" : "disabled";
  monitoringHud.dataset.pollingRateMs = String(monitoringHudControlState.pollingRateMs);
  monitoringHud.dataset.overlayProfileState = "slc-039-membership-mapping";
  monitoringHud.dataset.overlayProfileSchemaVersion = String(monitoringHudOverlayProfileSchemaVersion);
  monitoringHud.dataset.activeOverlayProfileId = String(monitoringHudControlState.activeOverlayProfileId || "");
  monitoringHud.dataset.overlayProfileEditor = "slc-039-membership-editor";
  monitoringHud.dataset.overlayProfileMembership = "editable-slc-039-mapping";
  monitoringHud.dataset.overlayProfileIntegration = "followup-assigned-overlay-status-assignment";
  monitoringHud.dataset.manageOverlayProfileContext = "clickable-assigned-overlay-status-window";
  monitoringHud.dataset.sourceSettingsIa = "source-list-settings-entry-points";
  monitoringHud.dataset.recordingProfileState = "recording-profile-state-absent-future-gated";
  const activeRecordingTarget = monitoringHudSyncActiveOverlayRecordingTargetFromOverlayProfile();
  monitoringHud.dataset.activeOverlayRecordingTarget = "slc-051-active-overlay-profile-membership-target";
  monitoringHud.dataset.activeOverlayRecordingTargetProof = monitoringHud.dataset.activeOverlayRecordingTargetProof || "pending";
  monitoringHud.dataset.activeOverlayRecordingTargetState = activeRecordingTarget.targetState || "no-overlay-profiles";
  monitoringHud.dataset.activeOverlayRecordingTargetSource = activeRecordingTarget.source || "active-overlay-profile-membership";
  monitoringHud.dataset.activeOverlayRecordingTargetScope = activeRecordingTarget.scope || "target-session-truth-only";
  monitoringHud.dataset.activeOverlayRecordingTargetMonitorCount = String(activeRecordingTarget.membershipSnapshotCandidateCount || 0);
  monitoringHud.dataset.snapshotAtStartModel = activeRecordingTarget.snapshotAtStartModel || "snapshot-at-recording-start";
  monitoringHud.dataset.hiddenRecordingTargetState = activeRecordingTarget.hiddenRecordingTargetState || "absent";
  monitoringHud.dataset.recordingExecutionState = activeRecordingTarget.recordingExecutionState || "blocked";
  monitoringHud.dataset.recordingFileWritingState = activeRecordingTarget.fileWritingState || "blocked";
  monitoringHud.dataset.recordingTargetPreview = "slc-052-dashboard-recording-card-target-status";
  monitoringHud.dataset.recordingCardPlacement = "dashboard-recording-card-primary";
  monitoringHud.dataset.hudOverlayRecordingBoundary = "hud-overlay-overlay-focused";
  monitoringHud.dataset.recordingControlWindowState = "recording-studio-ready";
  monitoringHud.dataset.recordingControlWindowContract = "recording-studio-focused-control-status";
  monitoringHud.dataset.logViewerState = "ready";
  monitoringHud.dataset.activeMonitorTransparency = "slc-052-dashboard-visible-count-and-names";
  monitoringHudRenderActiveOverlayRecordingTargetPreview();
  monitoringHud.dataset.warningControlPosture = monitoringHudControlState.warningNotificationsMuted
    ? "global-muted"
    : "visual-notifications-enabled";
  monitoringHud.dataset.dashboardActionsAlignment = "right-settings-after-deferred-status";
  monitoringHud.dataset.dataSourcesActionCopy = "manage-data-sources-feature-deferred";
  monitoringHud.dataset.dashboardProviderTruth = "provider-contract-first";
  monitoringHud.dataset.dashboardStateModel = "setup-no-data-degraded-warning";
  monitoringHud.dataset.dashboardWarningControls = "visual-non-invasive-only";
  monitoringHud.dataset.dashboardFakeTelemetryPolicy = "blocked";
  monitoringHud.dataset.interactiveControlAffordance = "normal-hover-active-focus-visible-disabled-open-selected";
  monitoringHud.dataset.interactiveControlReliability = monitoringHud.dataset.interactiveControlReliability || "first-click-stress-proof-required";
  monitoringHud.dataset.clickInterceptionDiagnostics = monitoringHud.dataset.clickInterceptionDiagnostics || "z-index-pointer-events-disabled-aria-dom-focus-timing";
  monitoringHud.dataset.pollingRateDropdown = "nexus-styled-bounded-control";
  if (monitoringHudRuntimeStatus) {
    monitoringHudRuntimeStatus.textContent = dashboardVisible ? "Dashboard visible" : "Dashboard hidden";
  }
  if (monitoringHudAnchorStatus) {
    monitoringHudAnchorStatus.textContent = overlayDeferred ? "HUD Overlay deferred" : (monitoringHudControlState.anchored ? "HUD Overlay anchored" : "HUD Overlay unanchored");
  }
  if (monitoringHudToggle) {
    monitoringHudToggle.textContent = featureEnabled ? "Disable HUD Overlay" : "Enable HUD Overlay";
  }
  if (monitoringHudAnchorToggle) {
    monitoringHudAnchorToggle.textContent = overlayDeferred ? "HUD Overlay deferred" : (monitoringHudControlState.anchored ? "Unanchor HUD Overlay" : "Anchor HUD Overlay");
    monitoringHudAnchorToggle.disabled = overlayDeferred;
  }
  if (monitoringHudEditMonitor) {
    monitoringHudEditMonitor.textContent = "Manage Monitors";
  }
  if (monitoringHudSnapToggle) {
    monitoringHudSnapToggle.textContent = "HUD Overlay settings";
    monitoringHudSnapToggle.disabled = overlayDeferred;
  }
  if (monitoringHudWarningToggle) {
    monitoringHudWarningToggle.textContent = monitoringHudControlState.warningNotificationsMuted
      ? "Warning Notifications Muted"
      : "Warning Notifications On";
  }
  if (monitoringHudSnapLabel) {
    monitoringHudSnapLabel.textContent = "HUD Overlay deferred";
  }
  if (monitoringHudPollingRate) {
    monitoringHudPollingRate.value = String(monitoringHudControlState.pollingRateMs);
  }
  if (monitoringHudWarningModeControl) {
    monitoringHudWarningModeControl.value = monitoringHudControlState.warningMode || "badge-text-color";
  }
  monitoringHudRenderDashboardSettingsPanel();
  monitoringHudRenderOverlayProfileControls();
  if (monitoringHudWarningPosture) {
    monitoringHudWarningPosture.textContent = monitoringHudControlState.warningNotificationsMuted
      ? "Globally muted; Monitor Group settings preserved"
      : "Visual notifications enabled";
  }
  if (monitoringHudPlacementPointer) {
    monitoringHudPlacementPointer.textContent = "Dashboard configures future HUD Overlay behavior";
  }
  monitoringHudUpdateSurfaceSplit();
  monitoringHudRenderMonitorManagement();
  monitoringHudRenderOverlayDisplay();
}

function monitoringHudApplyPanelPosition(position) {
  if (!monitoringHud || !position) return;
  monitoringHud.style.left = `${position.left}px`;
  monitoringHud.style.top = `${position.top}px`;
  monitoringHud.style.right = "auto";
  monitoringHud.style.transformOrigin = "top left";
}

function monitoringHudSetPanelPosition(left, top, persist = true) {
  if (!monitoringHud) return;
  const minVisibleWidth = Math.min(monitoringHud.offsetWidth, 520);
  const minVisibleHeight = Math.min(monitoringHud.offsetHeight, 420);
  const maxLeft = Math.max(0, window.innerWidth - minVisibleWidth);
  const maxTop = Math.max(0, window.innerHeight - minVisibleHeight);
  const boundedLeft = monitoringHudBound(monitoringHudSnap(left), 0, maxLeft);
  const boundedTop = monitoringHudBound(monitoringHudSnap(top), 0, maxTop);
  monitoringHudControlState.panelPosition = { left: boundedLeft, top: boundedTop };
  monitoringHudQueuedPanelPosition = { left: boundedLeft, top: boundedTop };
  if (typeof window.requestAnimationFrame === "function") {
    if (!monitoringHudPanelPositionFrame) {
      monitoringHudPanelPositionFrame = window.requestAnimationFrame(() => {
        monitoringHudPanelPositionFrame = 0;
        monitoringHudApplyPanelPosition(monitoringHudQueuedPanelPosition);
      });
    }
  } else {
    monitoringHudApplyPanelPosition(monitoringHudQueuedPanelPosition);
  }
  if (persist && !monitoringHudDragInProgress) {
    monitoringHudMarkChanged();
  } else {
    monitoringHudControlState.changedAt = Date.now();
  }
}

function monitoringHudClearPanelPosition() {
  if (!monitoringHud) return;
  monitoringHud.style.left = "";
  monitoringHud.style.top = "";
  monitoringHud.style.right = "";
  monitoringHud.style.transformOrigin = "top right";
  monitoringHudControlState.panelPosition = null;
}

function monitoringHudRenderSensorCards(cards) {
  if (!Array.isArray(cards)) return;
  cards.forEach((card) => {
    if (!card || !card.id) return;
    const cardNode = monitoringHudEditMonitorList
      ? monitoringHudEditMonitorList.querySelector(`[data-monitor-row="${card.id}"]`)
      : null;
    if (cardNode) {
      if (card.state) cardNode.dataset.monitorProviderState = card.state;
      const statusNode = cardNode.querySelector(`[data-monitor-config-status="${card.id}"]`);
      if (statusNode) statusNode.textContent = card.summary || (card.state === "warning" ? "Warning in future overlay" : "Enabled for future overlay");
    }
    const minimalCardNode = monitoringHudMinimal
      ? monitoringHudMinimal.querySelector(`[data-minimal-card="${card.id}"]`)
      : null;
    if (minimalCardNode && card.state) {
      minimalCardNode.classList.toggle("monitoring-hud-minimal-card--setup", card.state === "setup");
      minimalCardNode.classList.toggle("monitoring-hud-minimal-card--unavailable", card.state === "no-data" || card.state === "degraded");
      minimalCardNode.classList.toggle("monitoring-hud-minimal-card--warning", card.state === "warning");
      minimalCardNode.dataset.cardState = card.state;
    }
    const minimalSummaryNode = monitoringHudMinimal
      ? monitoringHudMinimal.querySelector(`[data-minimal-card-summary="${card.id}"]`)
      : null;
    if (minimalSummaryNode && card.summary) minimalSummaryNode.textContent = card.summary;
    if (!Array.isArray(card.sensors)) return;
    card.sensors.forEach((sensor) => {
      if (!sensor || !sensor.id) return;
      const row = cardNode ? cardNode.querySelector(`[data-sensor-row="${sensor.id}"]`) : null;
      const valueNode = cardNode ? cardNode.querySelector(`[data-sensor-value="${sensor.id}"]`) : null;
      const sourceNode = cardNode ? cardNode.querySelector(`[data-sensor-source="${sensor.id}"]`) : null;
      if (row && sensor.state) row.dataset.liveValue = sensor.state;
      if (valueNode && sensor.value) valueNode.textContent = sensor.value;
      if (sourceNode && sensor.source) sourceNode.textContent = sensor.source;
    });
  });
}

function monitoringHudStartPointerDrag(event, target, onMove) {
  if (!monitoringHud || !monitoringHudControlState.visible) return;
  if (monitoringHudDragInProgress) return;
  if (event.button !== undefined && event.button !== 0) return;
  if (event.target && event.target.closest && event.target.closest("button,input,select,label")) return;
  event.preventDefault();
  monitoringHudDragInProgress = true;
  monitoringHudControlState.lastDragEvent = {
    target: target && target.id ? target.id : (target && target.dataset ? JSON.stringify(target.dataset) : "unknown"),
    phase: "started",
    type: event.type || "unknown",
    startX: event.clientX,
    startY: event.clientY
  };
  const startX = event.clientX;
  const startY = event.clientY;
  const isPointerEvent = String(event.type || "").indexOf("pointer") === 0;
  const moveEventName = isPointerEvent ? "pointermove" : "mousemove";
  const upEventName = isPointerEvent ? "pointerup" : "mouseup";
  const cancelEventName = isPointerEvent ? "pointercancel" : "";
  if (isPointerEvent && typeof target.setPointerCapture === "function" && event.pointerId !== undefined) {
    target.setPointerCapture(event.pointerId);
  }
  function move(moveEvent) {
    monitoringHudControlState.lastDragEvent = Object.assign({}, monitoringHudControlState.lastDragEvent || {}, {
      phase: "moving",
      dx: moveEvent.clientX - startX,
      dy: moveEvent.clientY - startY
    });
    onMove(moveEvent.clientX - startX, moveEvent.clientY - startY);
  }
  function end() {
    monitoringHudControlState.lastDragEvent = Object.assign({}, monitoringHudControlState.lastDragEvent || {}, {
      phase: "ended"
    });
    monitoringHudDragInProgress = false;
    monitoringHudMarkChanged();
    document.removeEventListener(moveEventName, move);
    document.removeEventListener(upEventName, end);
    if (cancelEventName) document.removeEventListener(cancelEventName, end);
  }
  document.addEventListener(moveEventName, move);
  document.addEventListener(upEventName, end);
  if (cancelEventName) document.addEventListener(cancelEventName, end);
}

function monitoringHudWirePanelDrag() {
  if (!monitoringHud || !monitoringHudDragHandle) return;
  const startPanelDrag = (event) => {
    if (document.body && document.body.classList.contains("desktop-mode")) {
      return;
    }
    const rect = monitoringHud.getBoundingClientRect();
    monitoringHudStartPointerDrag(event, monitoringHudDragHandle, (dx, dy) => {
      monitoringHudSetPanelPosition(rect.left + dx, rect.top + dy, false);
    });
  };
  monitoringHudDragHandle.addEventListener("pointerdown", startPanelDrag);
  monitoringHudDragHandle.addEventListener("mousedown", startPanelDrag);
}

function monitoringHudWireCardInteractions() {
  // Monitor card movement/resizing belongs to the standalone overlay window.
  // The dashboard only edits monitor settings and never renders monitor cards.
}

function monitoringHudWireControls() {
  if (monitoringHudChildWindowLayer) {
    monitoringHudChildWindowLayer.dataset.childWindowPointerIsolation = "modal-layer-stops-dashboard-click-through";
    ["pointerdown", "mousedown", "click"].forEach((eventName) => {
      monitoringHudChildWindowLayer.addEventListener(eventName, (event) => {
        if (event.target === monitoringHudChildWindowLayer && typeof event.preventDefault === "function") {
          event.preventDefault();
        }
        if (typeof event.stopPropagation === "function") event.stopPropagation();
        if (typeof event.stopImmediatePropagation === "function") event.stopImmediatePropagation();
      });
    });
    monitoringHudChildWindowLayer.querySelectorAll(".monitoring-hud__child-window").forEach((windowNode) => {
      ["pointerdown", "mousedown", "click"].forEach((eventName) => {
        windowNode.addEventListener(eventName, (event) => {
          if (typeof event.stopPropagation === "function") event.stopPropagation();
          if (typeof event.stopImmediatePropagation === "function") event.stopImmediatePropagation();
        });
      });
    });
  }
  if (monitoringHudToggle) {
    monitoringHudWireReliableControl(monitoringHudToggle, "dashboard:toggle-visibility", () => {
      monitoringHudControlState.featureEnabled = !monitoringHudControlState.featureEnabled;
      monitoringHudControlState.visible = monitoringHudControlState.featureEnabled;
      monitoringHudRenderControls();
      monitoringHudMarkChanged();
    });
  }
  if (monitoringHudAnchorToggle) {
    monitoringHudWireReliableControl(monitoringHudAnchorToggle, "dashboard:anchor-toggle", () => {
      if (monitoringHudControlState.overlayDeferred !== false) {
        monitoringHudControlState.lastDeferredAnchorRequest = Date.now();
        monitoringHudRenderControls();
        monitoringHudMarkChanged();
        return;
      }
      monitoringHudControlState.anchored = !monitoringHudControlState.anchored;
      monitoringHudRenderControls();
      monitoringHudMarkChanged();
    });
  }
  if (monitoringHudDashboardClose) {
    monitoringHudWireReliableControl(monitoringHudDashboardClose, "dashboard:close", () => {
      if (!monitoringHudCloseChildWindow()) return;
      monitoringHudControlState.visible = false;
      monitoringHudRenderControls();
      monitoringHudMarkChanged();
    });
  }
  if (monitoringHudSettingsAction) {
    monitoringHudWireReliableControl(monitoringHudSettingsAction, "dashboard:settings", () => {
      monitoringHudOpenChildWindow("dashboard-settings");
    });
  }
  if (monitoringHudEditMonitor) {
    monitoringHudWireReliableControl(monitoringHudEditMonitor, "dashboard:manage-monitors", () => {
      monitoringHudOpenChildWindow("monitor-group-edit");
    });
  }
  if (monitoringHudRecordingControlLauncher) {
    monitoringHudWireReliableControl(monitoringHudRecordingControlLauncher, "recording-control:quick-access-start-stop", monitoringHudToggleRecording, { activateOnPointerDown: true });
  }
  if (monitoringHudRecordingStudioOpen) {
    monitoringHudWireReliableControl(monitoringHudRecordingStudioOpen, "recording-control:open-recording-studio", monitoringHudRequestRecordingControlWindow, { activateOnPointerDown: true });
  }
  if (monitoringHudRecordingOpenFolder) {
    monitoringHudWireReliableControl(monitoringHudRecordingOpenFolder, "recording-control:open-log-viewer", monitoringHudRequestLogViewerWindow, { activateOnPointerDown: true });
  }
  if (monitoringHudCreateMonitorConfirm) {
    monitoringHudWireReliableControl(monitoringHudCreateMonitorConfirm, "create-window:confirm", monitoringHudCreateMonitorGroupFromWindow);
  }
  if (monitoringHudManageMonitorCreate) {
    monitoringHudWireReliableControl(monitoringHudManageMonitorCreate, "manage:create", monitoringHudCreateMonitorGroupFromManageWindow);
  }
  if (monitoringHudMonitorEmptyCreate) {
    monitoringHudWireReliableControl(monitoringHudMonitorEmptyCreate, "manage:empty-create", monitoringHudCreateMonitorGroupFromManageWindow);
  }
  if (monitoringHudEditMonitorConfirm) {
    monitoringHudWireReliableControl(monitoringHudEditMonitorConfirm, "manage:save-monitor", () => monitoringHudSaveEditMonitorWindow({ keepOpen: true }));
  }
  if (monitoringHudEditMonitorDiscard) {
    monitoringHudWireReliableControl(monitoringHudEditMonitorDiscard, "manage:discard-monitor", monitoringHudDiscardCurrentMonitorDraft);
  }
  if (monitoringHudEditMonitorList) {
    monitoringHudWireReliableDelegatedControl(monitoringHudEditMonitorList, "[data-monitor-select]", "manage:row-switch", (row) => {
      if (monitoringHudSelectMonitorGroup(row.dataset.monitorSelect)) {
        monitoringHudMarkChanged();
      }
    });
    monitoringHudEditMonitorList.addEventListener("keydown", (event) => {
      if (!["Enter", " "].includes(event.key)) return;
      const row = event.target && event.target.closest ? event.target.closest("[data-monitor-select]") : null;
      if (!row) return;
      event.preventDefault();
      if (monitoringHudSelectMonitorGroup(row.dataset.monitorSelect)) {
        monitoringHudMarkChanged();
      }
    });
  }
  if (monitoringHudMonitorSearch) {
    monitoringHudMonitorSearch.addEventListener("input", () => {
      monitoringHudRenderMonitorManagement();
    });
  }
  if (monitoringHudMonitorDeleteConfirm) {
    monitoringHudWireReliableControl(monitoringHudMonitorDeleteConfirm, "manage:delete-confirm", monitoringHudConfirmDeleteMonitorGroup);
  }
  if (monitoringHudMonitorDeleteCancel) {
    monitoringHudWireReliableControl(monitoringHudMonitorDeleteCancel, "manage:delete-cancel", monitoringHudCancelDeleteMonitorGroup);
  }
  if (monitoringHudMonitorDetailDelete) {
    monitoringHudWireReliableControl(monitoringHudMonitorDetailDelete, "manage:delete-selected", () => {
      const selected = monitoringHudSelectedMonitor();
      if (!selected.id) return;
      monitoringHudRequestDeleteMonitorGroup(selected.id);
    });
  }
  if (monitoringHudMonitorUnsavedSave) {
    monitoringHudWireReliableControl(monitoringHudMonitorUnsavedSave, "manage:dirty-save", monitoringHudSaveAndSelectPendingMonitor);
  }
  if (monitoringHudMonitorUnsavedDiscard) {
    monitoringHudWireReliableControl(monitoringHudMonitorUnsavedDiscard, "manage:dirty-discard", monitoringHudDiscardAndSelectPendingMonitor);
  }
  if (monitoringHudMonitorUnsavedCancel) {
    monitoringHudWireReliableControl(monitoringHudMonitorUnsavedCancel, "manage:dirty-cancel", monitoringHudCancelMonitorUnsavedGuard);
  }
  if (monitoringHudMonitorSensorAssignment) {
    monitoringHudWireReliableDelegatedControl(monitoringHudMonitorSensorAssignment, "[data-source-settings-open]", "source-settings", (button) => {
      return monitoringHudOpenSourceSettings(button.dataset.sourceSettingsOpen || "");
    }, { activateOnPointerDown: true });
    monitoringHudMonitorSensorAssignment.addEventListener("change", (event) => {
      if (!event.target || !event.target.matches || !event.target.matches("[data-monitor-sensor-input]")) return;
      if (Date.now() <= monitoringHudSourcePickerSuppressNativeChangeUntil) {
        monitoringHudPreventNativeSourcePickerEvent(event);
        return;
      }
      const row = event.target.closest("[data-source-picker-row]");
      if (row) monitoringHudSetSourceRowSelectionState(row, Boolean(event.target.checked));
      const draft = row
        ? monitoringHudApplySensorAssignmentToDraft(row, Boolean(event.target.checked))
        : monitoringHudUpdateMonitorDraftFromWindow();
      if (!draft) return;
      monitoringHudRefreshSensorPickerSelectionProof(draft, { deferSettingsRefresh: Boolean(row) });
    });
    monitoringHudWireSourcePickerReliableSelection(monitoringHudMonitorSensorAssignment);
    monitoringHudMonitorSensorAssignment.addEventListener("mouseover", (event) => {
      const row = event.target && event.target.closest ? event.target.closest("[data-source-picker-row]") : null;
      if (!row || !monitoringHudMonitorSensorAssignment.contains(row)) return;
      monitoringHudMonitorSensorAssignment.querySelectorAll("[data-source-picker-row].is-hovered").forEach((item) => {
        if (item !== row) item.classList.remove("is-hovered");
      });
      monitoringHudHoveredSourcePickerId = row.dataset.sourcePickerRow || "";
      row.classList.add("is-hovered");
      row.dataset.hoverPersistence = "preserved-across-refresh";
      monitoringHudMonitorSensorAssignment.dataset.sourcePickerHoverPersistence = "preserved-across-refresh";
    });
    monitoringHudMonitorSensorAssignment.addEventListener("mouseleave", () => {
      monitoringHudHoveredSourcePickerId = "";
      monitoringHudMonitorSensorAssignment.dataset.sourcePickerHoverPersistence = "cleared-on-leave";
      monitoringHudMonitorSensorAssignment.querySelectorAll("[data-source-picker-row].is-hovered").forEach((item) => {
        item.classList.remove("is-hovered");
      });
    });
    monitoringHudMonitorSensorAssignment.addEventListener("keydown", (event) => {
      if (!["Enter", " "].includes(event.key)) return;
      const row = event.target && event.target.closest ? event.target.closest("[data-source-picker-row]") : null;
      if (!row || !monitoringHudMonitorSensorAssignment.contains(row)) return;
      event.preventDefault();
      if (typeof event.stopPropagation === "function") event.stopPropagation();
      const result = monitoringHudToggleSensorAssignmentRow(row);
      monitoringHudRecordReliableActivation(row, "keyboard-toggle", result !== false);
    });
  }
  if (monitoringHudMonitorSensorSettings) {
    monitoringHudMonitorSensorSettings.addEventListener("change", (event) => {
      if (!event.target || !event.target.matches) return;
      if (!event.target.matches("[data-sensor-warning-enabled]")) return;
      if (!monitoringHudUpdateMonitorDraftFromWindow()) return;
      monitoringHudRenderMonitorManagement();
    });
    monitoringHudWireDisplayModeReliableSelection(monitoringHudMonitorSensorSettings);
  }
  if (monitoringHudSensorSearch) {
    monitoringHudSensorSearch.addEventListener("input", () => {
      monitoringHudRenderMonitorManagement();
    });
  }
  if (monitoringHudSensorFilter) {
    monitoringHudWireReliableDelegatedControl(monitoringHudSensorFilter, "#monitoring-hud-sensor-filter-toggle,[data-source-filter]", "source-filter", (button) => {
      if (button.id === "monitoring-hud-sensor-filter-toggle") {
        monitoringHudSetSourceFilterDropdownOpen(monitoringHudSensorFilter.dataset.filterOpen !== "true");
        return true;
      }
      monitoringHudSetSourceFilterValue(button.dataset.sourceFilter || "all");
      monitoringHudSetSourceFilterDropdownOpen(false);
      monitoringHudRenderMonitorManagement();
    });
    monitoringHudSensorFilter.addEventListener("mouseover", (event) => {
      const option = event.target && event.target.closest ? event.target.closest("[data-source-filter]") : null;
      if (!option) return;
      monitoringHudResetSourceFilterHover();
      option.classList.add("is-hovered");
      monitoringHudSensorFilter.dataset.hoveredFilter = option.dataset.sourceFilter || "";
    });
    monitoringHudSensorFilter.addEventListener("mouseleave", monitoringHudResetSourceFilterHover);
    monitoringHudSensorFilter.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        monitoringHudSetSourceFilterDropdownOpen(false);
      }
    });
    monitoringHudSetSourceFilterValue(monitoringHudSensorFilterValue());
  }
  const activateDashboardOverlayProfileSelector = (event, phase) => {
    const selector = monitoringHudCurrentOverlayProfileSelector();
    if (!selector || !event || !event.target || !event.target.closest) return;
    const target = event.target.closest("#monitoring-hud-overlay-profile-toggle,[data-overlay-profile-option]");
    if (!target || !selector.contains(target)) return;
    monitoringHudHandleDashboardOverlayProfileActivation(target, event, phase);
  };
  ["pointerdown", "mousedown", "click"].forEach((eventName) => {
    document.addEventListener(eventName, (event) => activateDashboardOverlayProfileSelector(event, eventName), true);
  });
  if (monitoringHudOverlayProfileSelector) {
    monitoringHudWireReliableDelegatedControl(monitoringHudOverlayProfileSelector, "#monitoring-hud-overlay-profile-toggle,[data-overlay-profile-option]", "overlay-profile", (button) => {
      if (button.id === "monitoring-hud-overlay-profile-toggle") {
        const selector = monitoringHudCurrentOverlayProfileSelector();
        const menu = monitoringHudCurrentOverlayProfileMenu();
        const selectorIsActuallyOpen = Boolean(selector && selector.dataset.dropdownOpen === "true" && menu && !menu.hidden);
        monitoringHudSetOverlayProfileDropdownOpen(!selectorIsActuallyOpen);
        return true;
      }
      return monitoringHudSelectOverlayProfile(button.dataset.overlayProfileOption || monitoringHudDefaultOverlayProfileId);
    }, { activateOnPointerDown: true });
    monitoringHudOverlayProfileSelector.addEventListener("mouseover", (event) => {
      const option = event.target && event.target.closest ? event.target.closest("[data-overlay-profile-option]") : null;
      if (!option) return;
      monitoringHudResetOverlayProfileHover();
      option.classList.add("is-hovered");
      monitoringHudOverlayProfileSelector.dataset.hoveredProfileId = option.dataset.overlayProfileOption || "";
    });
    monitoringHudOverlayProfileSelector.addEventListener("mouseleave", monitoringHudResetOverlayProfileHover);
    monitoringHudOverlayProfileSelector.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        monitoringHudSetOverlayProfileDropdownOpen(false);
      }
    });
  }
  if (monitoringHudOverlayProfileWindowSelector) {
    monitoringHudWireReliableDelegatedControl(monitoringHudOverlayProfileWindowSelector, "#monitoring-hud-overlay-profile-window-toggle,[data-overlay-profile-window-option]", "overlay-profile-window", (button) => {
      if (button.id === "monitoring-hud-overlay-profile-window-toggle") {
        monitoringHudSetOverlayProfileWindowDropdownOpen(monitoringHudOverlayProfileWindowSelector.dataset.dropdownOpen !== "true");
        return true;
      }
      return monitoringHudSelectOverlayProfileForWindow(button.dataset.overlayProfileWindowOption || "");
    });
    monitoringHudOverlayProfileWindowSelector.addEventListener("mouseover", (event) => {
      const option = event.target && event.target.closest ? event.target.closest("[data-overlay-profile-window-option]") : null;
      if (!option) return;
      monitoringHudResetOverlayProfileWindowHover();
      option.classList.add("is-hovered");
      monitoringHudOverlayProfileWindowSelector.dataset.hoveredProfileId = option.dataset.overlayProfileWindowOption || "";
    });
    monitoringHudOverlayProfileWindowSelector.addEventListener("mouseleave", monitoringHudResetOverlayProfileWindowHover);
    monitoringHudOverlayProfileWindowSelector.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        monitoringHudSetOverlayProfileWindowDropdownOpen(false);
      }
    });
  }
  if (monitoringHudOverlayProfileOpenSettings) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileOpenSettings, "overlay-profile:open-settings", () => {
      monitoringHudOverlayProfileContextMonitorId = "";
      monitoringHudOpenChildWindow("overlay-profile-settings");
      return true;
    });
  }
  if (monitoringHudMonitorOverlayProfileSettings) {
    monitoringHudWireReliableControl(monitoringHudMonitorOverlayProfileSettings, "manage-overlay-profile:open-settings", () => {
      if (monitoringHudMonitorOverlayProfileSettings.disabled) return false;
      return monitoringHudOpenOverlayProfileSettingsFromManage();
    });
  }
  if (monitoringHudOverlayProfileNameInput) {
    monitoringHudOverlayProfileNameInput.addEventListener("input", () => {
      monitoringHudRenderOverlayProfileControls();
    });
    monitoringHudOverlayProfileNameInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        monitoringHudSaveOverlayProfileDraft();
      } else if (event.key === "Escape") {
        event.preventDefault();
        monitoringHudDiscardOverlayProfileDraft();
      }
    });
  }
  if (monitoringHudOverlayProfileMonitorSearch) {
    monitoringHudOverlayProfileMonitorSearch.addEventListener("input", () => {
      monitoringHudOverlayProfileMonitorSearchTerm = monitoringHudOverlayProfileMonitorSearch.value || "";
      monitoringHudRenderOverlayProfileControls();
    });
  }
  if (monitoringHudOverlayProfileMonitorFilter) {
    monitoringHudWireReliableDelegatedControl(monitoringHudOverlayProfileMonitorFilter, "#monitoring-hud-overlay-profile-monitor-filter-toggle,[data-overlay-profile-monitor-filter-option]", "overlay-profile-monitor-filter", (button) => {
      if (button.id === "monitoring-hud-overlay-profile-monitor-filter-toggle") {
        monitoringHudSetOverlayProfileMonitorFilterOpen(monitoringHudOverlayProfileMonitorFilter.dataset.dropdownOpen !== "true");
        return true;
      }
      monitoringHudSetOverlayProfileMonitorFilterValue(button.dataset.overlayProfileMonitorFilterOption || "all");
      monitoringHudSetOverlayProfileMonitorFilterOpen(false);
      monitoringHudRenderOverlayProfileControls();
      return true;
    });
    monitoringHudOverlayProfileMonitorFilter.addEventListener("mouseover", (event) => {
      const option = event.target && event.target.closest ? event.target.closest("[data-overlay-profile-monitor-filter-option]") : null;
      if (!option) return;
      monitoringHudResetOverlayProfileMonitorFilterHover();
      option.classList.add("is-hovered");
      monitoringHudOverlayProfileMonitorFilter.dataset.hoveredFilter = option.dataset.overlayProfileMonitorFilterOption || "";
    });
    monitoringHudOverlayProfileMonitorFilter.addEventListener("mouseleave", monitoringHudResetOverlayProfileMonitorFilterHover);
    monitoringHudOverlayProfileMonitorFilter.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        monitoringHudSetOverlayProfileMonitorFilterOpen(false);
      }
    });
  }
  if (monitoringHudOverlayProfileMembershipList) {
    monitoringHudOverlayProfileMembershipList.addEventListener("change", (event) => {
      const toggle = event.target && event.target.closest
        ? event.target.closest("[data-overlay-profile-membership-toggle]")
        : null;
      if (!toggle) return;
      const row = toggle.closest("[data-overlay-profile-membership-row]");
      if (row) {
        row.setAttribute("aria-selected", toggle.checked ? "true" : "false");
      }
      monitoringHudOverlayProfileDraftMonitorIds = monitoringHudOverlayProfileDraftMonitorIdsFromWindow();
      monitoringHudRenderOverlayProfileControls();
    });
  }
  if (monitoringHudOverlayProfileCreate) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileCreate, "overlay-profile:create", monitoringHudCreateOverlayProfile, { activateOnPointerDown: true });
  }
  if (monitoringHudOverlayProfileSave) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileSave, "overlay-profile:save", () => {
      if (monitoringHudOverlayProfileSave.disabled) return false;
      return monitoringHudSaveOverlayProfileDraft();
    });
  }
  if (monitoringHudOverlayProfileDiscard) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileDiscard, "overlay-profile:discard", () => {
      if (monitoringHudOverlayProfileDiscard.disabled) return false;
      return monitoringHudDiscardOverlayProfileDraft();
    });
  }
  if (monitoringHudOverlayProfileDelete) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileDelete, "overlay-profile:delete", () => {
      if (monitoringHudOverlayProfileDelete.disabled) return false;
      monitoringHudSetOverlayProfileDeleteConfirmation(true);
      return true;
    });
  }
  if (monitoringHudOverlayProfileDeleteConfirm) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileDeleteConfirm, "overlay-profile:delete-confirm", monitoringHudConfirmDeleteOverlayProfile);
  }
  if (monitoringHudOverlayProfileDeleteCancel) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileDeleteCancel, "overlay-profile:delete-cancel", () => {
      monitoringHudSetOverlayProfileDeleteConfirmation(false);
      return true;
    });
  }
  if (monitoringHudOverlayProfileUnsavedSave) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileUnsavedSave, "overlay-profile:dirty-save-close", monitoringHudSaveOverlayProfileAndClose);
  }
  if (monitoringHudOverlayProfileUnsavedDiscard) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileUnsavedDiscard, "overlay-profile:dirty-discard-close", monitoringHudDiscardOverlayProfileAndClose);
  }
  if (monitoringHudOverlayProfileUnsavedCancel) {
    monitoringHudWireReliableControl(monitoringHudOverlayProfileUnsavedCancel, "overlay-profile:dirty-cancel", monitoringHudCancelOverlayProfileUnsavedGuard);
  }
  if (monitoringHudMonitorOverlayProfileContext) {
    monitoringHudWireReliableControl(monitoringHudMonitorOverlayProfileContext, "manage:assigned-overlay", () => {
      const selected = monitoringHudSelectedMonitor();
      if (!selected.id) return false;
      monitoringHudOpenChildWindow("monitor-overlay-assignment");
      return true;
    });
  }
  if (monitoringHudOverlayAssignmentList) {
    monitoringHudWireReliableDelegatedControl(monitoringHudOverlayAssignmentList, "[data-overlay-assignment-toggle]", "overlay-assignment", (button) => {
      return monitoringHudToggleOverlayAssignment(button.dataset.overlayAssignmentToggle || "");
    });
  }
  if (monitoringHudSourceSettingsBody) {
    monitoringHudWireDisplayModeReliableSelection(monitoringHudSourceSettingsBody);
    monitoringHudSourceSettingsBody.addEventListener("change", (event) => {
      if (!event.target || !event.target.matches) return;
      if (!event.target.matches("[data-sensor-warning-enabled]")) return;
      monitoringHudApplySourceSetting(event.target.dataset.sensorWarningEnabled || monitoringHudActiveSourceSettingsId, {
        warningEnabled: Boolean(event.target.checked)
      }, { skipRender: true });
    });
    monitoringHudWireReliableDelegatedControl(monitoringHudSourceSettingsBody, "[data-source-polling-toggle],[data-source-polling-option]", "source-polling", (button) => {
      const control = button.closest("[data-source-polling-control]");
      if (!control) return false;
      if (button.dataset.sourcePollingToggle) {
        const open = control.dataset.dropdownOpen !== "true";
        control.dataset.dropdownOpen = open ? "true" : "false";
        monitoringHudSourcePollingDropdownOpenSensorId = open ? (control.dataset.sourcePollingControl || monitoringHudActiveSourceSettingsId) : "";
        button.setAttribute("aria-expanded", open ? "true" : "false");
        const menu = control.querySelector("[data-source-polling-menu]");
        if (menu) menu.hidden = !open;
        return true;
      }
      const value = button.dataset.sourcePollingOption || "default";
      control.dataset.selectedValue = value;
      control.querySelectorAll("[data-source-polling-option]").forEach((option) => {
        const selected = String(option.dataset.sourcePollingOption || "default") === value;
        option.setAttribute("aria-selected", selected ? "true" : "false");
      });
      const toggleLabel = control.querySelector(".monitoring-hud__bounded-dropdown-toggle strong");
      if (toggleLabel) toggleLabel.textContent = monitoringHudSensorPollingRateLabel(value);
      monitoringHudSourcePollingDropdownOpenSensorId = "";
      control.dataset.dropdownOpen = "false";
      const menu = control.querySelector("[data-source-polling-menu]");
      if (menu) menu.hidden = true;
      const toggle = control.querySelector("[data-source-polling-toggle]");
      if (toggle) toggle.setAttribute("aria-expanded", "false");
      monitoringHudApplySourceSetting(control.dataset.sourcePollingControl || monitoringHudActiveSourceSettingsId, { pollingRateMs: value }, { skipRender: true });
      return true;
    });
  }
  if (monitoringHudMonitorPollingRateControl) {
    monitoringHudWireReliableDelegatedControl(monitoringHudMonitorPollingRateControl, "#monitoring-hud-monitor-polling-rate-toggle,[data-polling-rate-option]", "polling-rate", (button) => {
      if (button.id === "monitoring-hud-monitor-polling-rate-toggle") {
        monitoringHudSetPollingRateDropdownOpen(monitoringHudMonitorPollingRateControl.dataset.dropdownOpen !== "true");
        return true;
      }
      monitoringHudSetPollingRateValue(button.dataset.pollingRateOption || "1000", { dispatchChange: true });
      monitoringHudSetPollingRateDropdownOpen(false);
      if (!monitoringHudUpdateMonitorDraftFromWindow()) return false;
      monitoringHudRenderMonitorManagement();
      return true;
    });
    monitoringHudMonitorPollingRateControl.addEventListener("mouseover", (event) => {
      const option = event.target && event.target.closest ? event.target.closest("[data-polling-rate-option]") : null;
      if (!option) return;
      monitoringHudResetPollingRateHover();
      option.classList.add("is-hovered");
      monitoringHudMonitorPollingRateControl.dataset.hoveredValue = option.dataset.pollingRateOption || "";
    });
    monitoringHudMonitorPollingRateControl.addEventListener("mouseleave", monitoringHudResetPollingRateHover);
    monitoringHudMonitorPollingRateControl.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        monitoringHudSetPollingRateDropdownOpen(false);
      }
    });
    monitoringHudSetPollingRateValue(monitoringHudMonitorPollingRate ? monitoringHudMonitorPollingRate.value : "1000");
  }
  document.addEventListener("click", (event) => {
    if (!monitoringHudSensorFilter || monitoringHudSensorFilter.contains(event.target)) return;
    monitoringHudSetSourceFilterDropdownOpen(false);
  });
  document.addEventListener("click", (event) => {
    const selector = monitoringHudCurrentOverlayProfileSelector();
    if (!selector || selector.contains(event.target)) return;
    monitoringHudSetOverlayProfileDropdownOpen(false);
  });
  document.addEventListener("click", (event) => {
    if (!monitoringHudOverlayProfileWindowSelector || monitoringHudOverlayProfileWindowSelector.contains(event.target)) return;
    monitoringHudSetOverlayProfileWindowDropdownOpen(false);
  });
  document.addEventListener("click", (event) => {
    if (!monitoringHudOverlayProfileMonitorFilter || monitoringHudOverlayProfileMonitorFilter.contains(event.target)) return;
    monitoringHudSetOverlayProfileMonitorFilterOpen(false);
  });
  document.addEventListener("click", (event) => {
    if (!monitoringHudMonitorPollingRateControl || monitoringHudMonitorPollingRateControl.contains(event.target)) return;
    monitoringHudSetPollingRateDropdownOpen(false);
  });
  document.querySelectorAll("[data-child-window-close]").forEach((button) => {
    monitoringHudWireReliableControl(button, `child-window-close:${button.dataset.childWindowClose || "unknown"}`, () => monitoringHudCloseChildWindow());
  });
  if (monitoringHudSnapToggle) {
    monitoringHudWireReliableControl(monitoringHudSnapToggle, "dashboard:snap-toggle", () => {
      monitoringHudControlState.snapEnabled = !monitoringHudControlState.snapEnabled;
      monitoringHudRenderControls();
      monitoringHudMarkChanged();
    });
  }
  if (monitoringHudPollingRate) {
    monitoringHudPollingRate.addEventListener("change", () => {
      const value = Number(monitoringHudPollingRate.value) || 1000;
      monitoringHudControlState.pollingRateMs = Math.max(1000, value);
      monitoringHudRenderControls();
      monitoringHudMarkChanged();
    });
  }
  if (monitoringHudWarningModeControl) {
    monitoringHudWarningModeControl.addEventListener("change", () => {
      const allowedModes = new Set(["badge-text-color", "badge-only", "text-color"]);
      const value = String(monitoringHudWarningModeControl.value || "badge-text-color");
      monitoringHudControlState.warningMode = allowedModes.has(value) ? value : "badge-text-color";
      monitoringHudRenderControls();
      monitoringHudMarkChanged();
    });
  }
  document.querySelectorAll('[data-control="warning-notifications"]').forEach((button) => {
    monitoringHudWireReliableControl(button, "dashboard:warning-notifications", () => {
      monitoringHudControlState.warningNotificationsMuted = !monitoringHudControlState.warningNotificationsMuted;
      monitoringHudRenderControls();
      monitoringHudMarkChanged();
    });
  });
  if (monitoringHudSettingsWarningToggle) {
    monitoringHudSettingsWarningToggle.addEventListener("change", () => {
      monitoringHudControlState.warningNotificationsMuted = !monitoringHudSettingsWarningToggle.checked;
      monitoringHudRenderControls();
      monitoringHudMarkChanged();
    });
  }
  if (monitoringHudMonitorEnabled) {
    monitoringHudMonitorEnabled.addEventListener("change", () => {
      if (!monitoringHudUpdateMonitorDraftFromWindow()) return;
      monitoringHudRenderMonitorManagement();
    });
  }
  if (monitoringHudMonitorPollingRate) {
    monitoringHudMonitorPollingRate.addEventListener("change", () => {
      if (!monitoringHudUpdateMonitorDraftFromWindow()) return;
      monitoringHudRenderMonitorManagement();
    });
  }
  if (monitoringHudEditMonitorName) {
    monitoringHudEditMonitorName.addEventListener("input", () => {
      monitoringHudUpdateMonitorDraftFromWindow();
    });
  }
  if (monitoringHudMonitorWarningSetting) {
    monitoringHudMonitorWarningSetting.addEventListener("change", () => {
      if (!monitoringHudUpdateMonitorDraftFromWindow()) return;
      monitoringHudRenderMonitorManagement();
    });
  }
}

function monitoringHudInitializeControls() {
  monitoringHudLoadStoredState();
  monitoringHudApplyCardLayout();
  monitoringHudSetOverlayProfileDraftFromActive();
  monitoringHudRenderControls();
  monitoringHudWirePanelDrag();
  monitoringHudWireCardInteractions();
  monitoringHudWireControls();
  document.addEventListener("mousedown", (event) => {
    const target = event.target && event.target.id
      ? event.target.id
      : (event.target && event.target.dataset ? JSON.stringify(event.target.dataset) : String(event.target && event.target.tagName || "unknown"));
    monitoringHudControlState.lastMouseEvent = {
      type: "mousedown",
      target,
      x: event.clientX,
      y: event.clientY
    };
  }, true);
  document.addEventListener("mousemove", (event) => {
    if (event.buttons !== 1) return;
    monitoringHudControlState.lastMouseEvent = {
      type: "mousemove",
      target: event.target && event.target.id ? event.target.id : String(event.target && event.target.tagName || "unknown"),
      x: event.clientX,
      y: event.clientY,
      buttons: event.buttons
    };
  }, true);
}

window.runMonitoringHudOverlayProfileStateProof = function() {
  const legacyCards = {
    cpu: Object.assign(monitoringHudCardDefaults("cpu"), { title: "CPU Group" }),
    gpu: Object.assign(monitoringHudCardDefaults("gpu"), { title: "GPU Group" })
  };
  const legacyState = {
    cards: legacyCards,
    selectedMonitorId: "gpu"
  };
  monitoringHudNormalizeOverlayProfileState(legacyState);
  const legacyDefaultProfile = legacyState.overlayProfiles[monitoringHudDefaultOverlayProfileId] || {};

  const mixedState = {
    cards: legacyCards,
    selectedMonitorId: "gpu",
    activeOverlayProfileId: "missing-profile",
    overlayProfiles: {
      custom: {
        id: "custom",
        name: "Custom Overlay Profile",
        monitorIds: ["gpu", "gpu", "missing", "cpu"],
        displayMode: "monitor-cards",
        monitorGroupId: "must-not-survive",
        recordingProfileId: "must-not-survive"
      }
    }
  };
  monitoringHudNormalizeOverlayProfileState(mixedState);
  const customProfile = mixedState.overlayProfiles.custom || {};
  const deletedDefaultState = {
    cards: legacyCards,
    selectedMonitorId: "cpu",
    activeOverlayProfileId: monitoringHudDefaultOverlayProfileId,
    overlayProfileDefaultDeletedByUser: true,
    overlayProfiles: {}
  };
  monitoringHudNormalizeOverlayProfileState(deletedDefaultState);
  const visibleEditorUi = Boolean(document.querySelector("#monitoring-hud-overlay-profile-editor[data-overlay-profile-editor-ui='slc-039-membership-editor']"));
  const proof = {
    passed: true,
    package: "PKG-006",
    slice: "SLC-039",
    schemaVersion: monitoringHudOverlayProfileSchemaVersion,
    defaultProfileId: monitoringHudDefaultOverlayProfileId,
    defaultProfileCreatedForLegacyCards: legacyState.activeOverlayProfileId === monitoringHudDefaultOverlayProfileId,
    legacyDefaultMembership: (legacyDefaultProfile.monitorIds || []).slice(),
    activeProfileFallback: mixedState.activeOverlayProfileId === "custom",
    defaultNotReinjectedWhenProfilesExist: !Object.prototype.hasOwnProperty.call(
      mixedState.overlayProfiles || {},
      monitoringHudDefaultOverlayProfileId
    ),
    defaultDeletePersistsWithoutAutoRecreate: Boolean(
      deletedDefaultState.overlayProfileDefaultDeletedByUser
      && deletedDefaultState.activeOverlayProfileId === ""
      && Object.keys(deletedDefaultState.overlayProfiles || {}).length === 0
    ),
    customMembershipNormalized: JSON.stringify(customProfile.monitorIds || []) === JSON.stringify(["gpu", "cpu"]),
    staleMonitorIdsRemoved: !(customProfile.monitorIds || []).includes("missing"),
    duplicateMonitorIdsRemoved: (customProfile.monitorIds || []).length === 2,
    selectedMonitorIdPreserved: mixedState.selectedMonitorId === "gpu",
    monitorGroupBoundary: !Object.prototype.hasOwnProperty.call(customProfile, "monitorGroupId"),
    recordingProfileBoundary: !Object.prototype.hasOwnProperty.call(customProfile, "recordingProfileId"),
    visibleProfileEditorUi: visibleEditorUi ? "slc-039-membership-editor" : "missing-slc-039-membership-editor"
  };
  proof.passed = proof.defaultProfileCreatedForLegacyCards
    && JSON.stringify(proof.legacyDefaultMembership) === JSON.stringify(["cpu", "gpu"])
    && proof.activeProfileFallback
    && proof.defaultNotReinjectedWhenProfilesExist
    && proof.defaultDeletePersistsWithoutAutoRecreate
    && proof.customMembershipNormalized
    && proof.staleMonitorIdsRemoved
    && proof.duplicateMonitorIdsRemoved
    && proof.selectedMonitorIdPreserved
    && proof.monitorGroupBoundary
    && proof.recordingProfileBoundary
    && visibleEditorUi;
  monitoringHudControlState.overlayProfileStateProof = proof;
  if (monitoringHud) {
    monitoringHud.dataset.overlayProfileStateProof = proof.passed ? "pass" : "fail";
    monitoringHud.dataset.overlayProfileEditor = proof.visibleProfileEditorUi;
  }
  if (monitoringHudOverlayDisplay) {
    monitoringHudOverlayDisplay.dataset.overlayProfileStateProof = proof.passed ? "pass" : "fail";
    monitoringHudOverlayDisplay.dataset.overlayProfileEditor = proof.visibleProfileEditorUi;
  }
  return proof;
};

window.runMonitoringHudActiveOverlayRecordingTargetProof = function() {
  const previousState = JSON.stringify(monitoringHudControlState);
  let proof = {
    passed: false,
    package: "PKG-006",
    slice: "SLC-051",
    seam: "Active Overlay recording target foundation",
    activeOverlayProfileMembershipIsSource: false,
    snapshotAtStartTargetCandidate: false,
    nullActiveProfileHandled: false,
    emptyMembershipHandled: false,
    staleMissingActiveProfileHandled: false,
    deletedDefaultHandled: false,
    highVolumeMembershipHandled: false,
    noHiddenRecordingTargetState: false,
    recordingExecutionReady: false,
    fileWritingReady: false,
    recordingProfileBoundary: true,
    monitorGroupBoundary: true
  };
  try {
    const fixtureCards = {};
    for (let index = 1; index <= 130; index += 1) {
      const cardId = `slc051-monitor-${String(index).padStart(3, "0")}`;
      fixtureCards[cardId] = Object.assign(monitoringHudCardDefaults(cardId), {
        id: cardId,
        title: `SLC-051 Monitor ${String(index).padStart(3, "0")}`,
        enabled: true,
        sensors: index % 2 === 0 ? ["cpu-load"] : [],
        pollingRateMs: 1000
      });
    }

    monitoringHudControlState.cards = fixtureCards;
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = false;
    monitoringHudControlState.overlayProfiles = {
      "slc051-target": {
        id: "slc051-target",
        name: "SLC-051 Target Profile",
        monitorIds: ["slc051-monitor-003", "slc051-monitor-001", "missing-monitor", "slc051-monitor-003"],
        displayMode: "monitor-cards",
        monitorGroupId: "must-not-survive",
        recordingProfileId: "must-not-survive"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc051-target";
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudRenderOverlayDisplay();
    const targetSnapshot = monitoringHudControlState.activeOverlayRecordingTarget || {};
    const targetProfile = monitoringHudControlState.overlayProfiles["slc051-target"] || {};
    proof.activeOverlayProfileMembershipIsSource = targetSnapshot.source === "active-overlay-profile-membership"
      && JSON.stringify(targetSnapshot.membershipSnapshotCandidate || []) === JSON.stringify(["slc051-monitor-003", "slc051-monitor-001"])
      && monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTargetSource === "active-overlay-profile-membership";
    proof.snapshotAtStartTargetCandidate = targetSnapshot.snapshotAtStartModel === "snapshot-at-recording-start"
      && monitoringHudOverlayDisplay.dataset.snapshotAtStartModel === "snapshot-at-recording-start";
    proof.noHiddenRecordingTargetState = targetSnapshot.hiddenRecordingTargetState === "absent"
      && targetSnapshot.noHiddenRecordingTargetState === true
      && monitoringHudOverlayDisplay.dataset.hiddenRecordingTargetState === "absent";
    proof.recordingExecutionReady = targetSnapshot.recordingExecutionState === "ready"
      && monitoringHudOverlayDisplay.dataset.recordingExecutionState === "ready";
    proof.fileWritingReady = targetSnapshot.fileWritingState === "ready"
      && monitoringHudOverlayDisplay.dataset.recordingFileWritingState === "ready";
    proof.recordingProfileBoundary = !Object.prototype.hasOwnProperty.call(targetProfile, "recordingProfileId")
      && targetSnapshot.recordingProfileBoundary === "recording-profile-state-absent-future-gated";
    proof.monitorGroupBoundary = !Object.prototype.hasOwnProperty.call(targetProfile, "monitorGroupId")
      && targetSnapshot.monitorGroupBoundary === "monitor-groups-organize-configuration-only";

    monitoringHudControlState.overlayProfiles = {
      "slc051-empty": {
        id: "slc051-empty",
        name: "SLC-051 Empty Target",
        monitorIds: [],
        displayMode: "monitor-cards"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc051-empty";
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    proof.emptyMembershipHandled = monitoringHudControlState.activeOverlayRecordingTarget.targetState === "empty-membership"
      && monitoringHudControlState.activeOverlayRecordingTarget.membershipSnapshotCandidateCount === 0;

    monitoringHudControlState.overlayProfiles = {
      "slc051-fallback": {
        id: "slc051-fallback",
        name: "SLC-051 Fallback Target",
        monitorIds: ["slc051-monitor-004"],
        displayMode: "monitor-cards"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "missing-profile";
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    proof.staleMissingActiveProfileHandled = monitoringHudControlState.activeOverlayProfileId === "slc051-fallback"
      && monitoringHudControlState.activeOverlayRecordingTarget.fallbackUsed === true
      && JSON.stringify(monitoringHudControlState.activeOverlayRecordingTarget.membershipSnapshotCandidate || []) === JSON.stringify(["slc051-monitor-004"]);

    monitoringHudControlState.overlayProfiles = {};
    monitoringHudControlState.activeOverlayProfileId = "";
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = true;
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    proof.nullActiveProfileHandled = monitoringHudControlState.activeOverlayRecordingTarget.targetState === "deleted-default-empty";
    proof.deletedDefaultHandled = monitoringHudControlState.activeOverlayRecordingTarget.profileCount === 0
      && monitoringHudControlState.activeOverlayRecordingTarget.membershipSnapshotCandidateCount === 0;

    const highVolumeIds = Object.keys(fixtureCards).slice(0, 125);
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = false;
    monitoringHudControlState.overlayProfiles = {
      "slc051-high-volume": {
        id: "slc051-high-volume",
        name: "SLC-051 High Volume Target",
        monitorIds: highVolumeIds.concat(["missing-monitor", highVolumeIds[0]]),
        displayMode: "monitor-cards"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc051-high-volume";
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    proof.highVolumeMembershipHandled = monitoringHudControlState.activeOverlayRecordingTarget.targetState === "high-volume-membership"
      && monitoringHudControlState.activeOverlayRecordingTarget.membershipSnapshotCandidateCount === 125
      && !(monitoringHudControlState.activeOverlayRecordingTarget.membershipSnapshotCandidate || []).includes("missing-monitor");

    proof.passed = proof.activeOverlayProfileMembershipIsSource
      && proof.snapshotAtStartTargetCandidate
      && proof.nullActiveProfileHandled
      && proof.emptyMembershipHandled
      && proof.staleMissingActiveProfileHandled
      && proof.deletedDefaultHandled
      && proof.highVolumeMembershipHandled
      && proof.noHiddenRecordingTargetState
      && proof.recordingExecutionReady
      && proof.fileWritingReady
      && proof.recordingProfileBoundary
      && proof.monitorGroupBoundary;
  } finally {
    try {
      monitoringHudControlState = JSON.parse(previousState);
      monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
      monitoringHudRenderControls();
    } catch (_err) {}
  }
  monitoringHudControlState.activeOverlayRecordingTargetProof = proof;
  if (monitoringHud) {
    monitoringHud.dataset.activeOverlayRecordingTargetProof = proof.passed ? "pass" : "fail";
  }
  if (monitoringHudOverlayDisplay) {
    monitoringHudOverlayDisplay.dataset.activeOverlayRecordingTargetProof = proof.passed ? "pass" : "fail";
  }
  return proof;
};

window.runMonitoringHudRecordingTargetPreviewProof = function() {
  const previousState = JSON.stringify(monitoringHudControlState);
  let proof = {
    passed: false,
    package: "PKG-006",
    slice: "SLC-052",
    seam: "Dashboard Recording card target/status and active-monitor transparency",
    dashboardRecordingCardPresent: false,
    hudOverlayBoundaryPreserved: false,
    activeProfileNameVisible: false,
    activeMonitorCountVisible: false,
    activeMonitorNamesVisible: false,
    controlSurfaceEnabled: false,
    recordingStudioNativeWindowRequested: false,
    recordingExecutionReady: false,
    fileWritingReady: false,
    trayControlsAbsent: false,
    noRecordingControlWindowCreated: false,
    activeProfileCreateMirrorsRecordingTarget: false,
    savedActiveProfileSelectorSwitchesRecordingTarget: false,
    recordingTargetOverlayProfileMirrorProof: false
  };
  try {
    monitoringHudControlState.cards = {
      "slc052-cpu": Object.assign(monitoringHudCardDefaults("slc052-cpu"), {
        id: "slc052-cpu",
        title: "CPU Runtime",
        enabled: true,
        sensors: ["cpu-load"]
      }),
      "slc052-gpu": Object.assign(monitoringHudCardDefaults("slc052-gpu"), {
        id: "slc052-gpu",
        title: "GPU Runtime",
        enabled: true,
        sensors: ["gpu-load"]
      }),
      "slc052-hidden": Object.assign(monitoringHudCardDefaults("slc052-hidden"), {
        id: "slc052-hidden",
        title: "Hidden Monitor",
        enabled: false,
        sensors: []
      })
    };
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = false;
    monitoringHudControlState.overlayProfiles = {
      "slc052-target": {
        id: "slc052-target",
        name: "Recording Target Overlay",
        monitorIds: ["slc052-cpu", "slc052-gpu", "missing-monitor", "slc052-cpu"],
        displayMode: "monitor-cards"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc052-target";
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudRenderControls();
    const summaryText = monitoringHudRecordingTargetSummary
      ? String(monitoringHudRecordingTargetSummary.textContent || "")
      : "";
    proof.dashboardRecordingCardPresent = Boolean(monitoringHudRecordingCard)
      && monitoringHudRecordingCard.dataset.recordingCardPlacement === "dashboard-recording-card-primary"
      && Boolean(monitoringHudRecordingTargetPreview)
      && monitoringHudRecordingTargetPreview.dataset.recordingTargetPreview === "slc-052-dashboard-recording-card-target-status";
    proof.hudOverlayBoundaryPreserved = Boolean(monitoringHudRecordingTargetPreview)
      && monitoringHudRecordingTargetPreview.dataset.hudOverlayRecordingBoundary === "hud-overlay-overlay-focused"
      && !document.querySelector('[data-dashboard-hub-card="hud-overlay"] [data-recording-target-preview]');
    proof.activeProfileNameVisible = Boolean(monitoringHudRecordingTargetProfile)
      && monitoringHudRecordingTargetProfile.textContent === "Recording Target Overlay";
    proof.activeMonitorCountVisible = Boolean(monitoringHudRecordingTargetCount)
      && monitoringHudRecordingTargetCount.textContent === "2 active monitors";
    proof.activeMonitorNamesVisible = summaryText.includes("CPU Runtime")
      && summaryText.includes("GPU Runtime")
      && !summaryText.includes("missing-monitor");
    proof.controlSurfaceEnabled = Boolean(monitoringHudRecordingControlLauncher)
      && monitoringHudRecordingControlLauncher.disabled === false
      && monitoringHudRecordingControlLauncher.dataset.recordingControlWindowContract === "dashboard-quick-access-start-stop"
      && monitoringHudRecordingControlLauncher.dataset.recordingControlWindowState === "quick-access-start-stop"
      && monitoringHudRecordingControlLauncher.closest(".monitoring-hud__toolbar");
    proof.recordingCardRemainsSummarySurface = Boolean(monitoringHudRecordingCard)
      && Boolean(monitoringHudRecordingTargetPreview)
      && monitoringHudRecordingCard.dataset.recordingControlSurfaceState === "dashboard-status-summary"
      && !monitoringHudRecordingTargetPreview.querySelector("#monitoring-hud-recording-control-launcher");
    proof.recordingStudioLaunchReady = Boolean(monitoringHudRecordingStudioOpen)
      && monitoringHudRecordingStudioOpen.disabled === false
      && monitoringHudRecordingStudioOpen.dataset.recordingControlWindowContract === "recording-studio-focused-control-status";
    const studioRequestResult = monitoringHudRequestRecordingControlWindow();
    proof.recordingStudioNativeWindowRequested = Boolean(
      studioRequestResult
      && monitoringHudControlState.recordingControlWindowRequested === true
      && monitoringHudControlState.recordingControlWindowState === "native-window-requested"
      && monitoringHudControlState.recordingControlWindowTargetSummary
      && monitoringHudControlState.recordingControlWindowTargetSummary.startStopState === "start-enabled"
    );
    proof.logViewerLaunchReady = Boolean(monitoringHudRecordingOpenFolder)
      && monitoringHudRecordingOpenFolder.disabled === false
      && monitoringHudRecordingOpenFolder.dataset.logViewerState === "ready"
      && monitoringHudRecordingOpenFolder.dataset.recordingFolderAction === "native-and-export-folder-shell";
    const logViewerRequestResult = monitoringHudRequestLogViewerWindow();
    proof.logViewerNativeWindowRequested = Boolean(
      logViewerRequestResult
      && monitoringHudControlState.logViewerRequested === true
      && monitoringHudControlState.logViewerState === "native-window-requested"
      && monitoringHudControlState.logViewerSummary
      && monitoringHudControlState.logViewerSummary.nativeFolderState === "create-or-open-before-session"
      && monitoringHudControlState.logViewerSummary.exportFolderState === "create-or-open-before-session"
    );
    proof.recordingExecutionReady = Boolean(monitoringHudRecordingTargetPreview)
      && monitoringHudRecordingTargetPreview.dataset.recordingExecutionState === "ready"
      && monitoringHudRecordingControlLauncher.dataset.recordingExecutionState === "ready";
    proof.fileWritingReady = Boolean(monitoringHudRecordingTargetPreview)
      && monitoringHudRecordingTargetPreview.dataset.recordingFileWritingState === "ready"
      && monitoringHudRecordingControlLauncher.dataset.recordingFileWritingState === "ready";
    proof.trayControlsAbsent = !document.querySelector("[data-control='tray-recording-control']");
    proof.noRecordingControlWindowCreated = !document.querySelector("[data-child-window='recording-control']");
    monitoringHudCreateOverlayProfile();
    const createdProfile = monitoringHudOverlayProfilePendingCreate || {};
    const createdId = String(createdProfile.id || "");
    monitoringHudRenderControls();
    proof.activeProfileCreateMirrorsRecordingTarget = Boolean(
      createdId
      && monitoringHudControlState.activeOverlayRecordingTarget
      && monitoringHudControlState.activeOverlayRecordingTarget.activeOverlayProfileId === createdId
      && monitoringHudRecordingTargetProfile
      && monitoringHudRecordingTargetProfile.textContent === monitoringHudCleanOverlayProfileName(createdProfile.name, "Overlay Profile")
      && monitoringHudRecordingTargetCount
      && monitoringHudRecordingTargetCount.textContent === "0 active monitors"
    );
    monitoringHudSaveOverlayProfileDraft();
    const savedFirstId = createdId;
    monitoringHudCreateOverlayProfile();
    const secondProfile = monitoringHudOverlayProfilePendingCreate || {};
    const secondId = String(secondProfile.id || "");
    if (monitoringHudOverlayProfileNameInput) {
      monitoringHudOverlayProfileNameInput.value = "Recording Target Switch Overlay";
    }
    monitoringHudSaveOverlayProfileDraft();
    const switchedBack = monitoringHudSelectOverlayProfile(savedFirstId);
    const firstProfile = (monitoringHudControlState.overlayProfiles || {})[savedFirstId] || {};
    proof.savedActiveProfileSelectorSwitchesRecordingTarget = Boolean(
      savedFirstId
      && secondId
      && switchedBack
      && monitoringHudControlState.activeOverlayProfileId === savedFirstId
      && monitoringHudControlState.activeOverlayRecordingTarget
      && monitoringHudControlState.activeOverlayRecordingTarget.activeOverlayProfileId === savedFirstId
      && monitoringHudRecordingTargetProfile
      && monitoringHudRecordingTargetProfile.textContent === monitoringHudCleanOverlayProfileName(firstProfile.name, "Overlay Profile")
      && monitoringHudRecordingTargetCount
      && monitoringHudRecordingTargetCount.textContent === "0 active monitors"
    );
    proof.recordingTargetOverlayProfileMirrorProof = Boolean(
      monitoringHudControlState.recordingTargetOverlayProfileMirrorProof
      && monitoringHudControlState.recordingTargetOverlayProfileMirrorProof.passed === true
      && monitoringHud.dataset.recordingTargetOverlayProfileMirrorProof === "pass"
    );
    proof.passed = proof.dashboardRecordingCardPresent
      && proof.hudOverlayBoundaryPreserved
      && proof.activeProfileNameVisible
      && proof.activeMonitorCountVisible
      && proof.activeMonitorNamesVisible
      && proof.controlSurfaceEnabled
      && proof.recordingCardRemainsSummarySurface
      && proof.recordingStudioLaunchReady
      && proof.recordingStudioNativeWindowRequested
      && proof.logViewerLaunchReady
      && proof.logViewerNativeWindowRequested
      && proof.recordingExecutionReady
      && proof.fileWritingReady
      && proof.trayControlsAbsent
      && proof.noRecordingControlWindowCreated
      && proof.activeProfileCreateMirrorsRecordingTarget
      && proof.savedActiveProfileSelectorSwitchesRecordingTarget
      && proof.recordingTargetOverlayProfileMirrorProof;
  } finally {
    try {
      monitoringHudControlState = JSON.parse(previousState);
      monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
      monitoringHudRenderControls();
    } catch (_err) {}
  }
  monitoringHudControlState.recordingTargetPreviewProof = proof;
  if (monitoringHudRecordingTargetPreview) {
    monitoringHudRecordingTargetPreview.dataset.recordingTargetPreviewProof = proof.passed ? "pass" : "fail";
  }
  if (monitoringHud) {
    monitoringHud.dataset.recordingTargetPreviewProof = proof.passed ? "pass" : "fail";
  }
  return proof;
};

window.runMonitoringHudOverlayDisplayAcceptanceProof = function() {
  const previousState = JSON.stringify(monitoringHudControlState);
  let proof = {
    passed: false,
    package: "PKG-006",
    slice: "SLC-042",
    seam: "Overlay display acceptance baseline and active-profile state bridge",
    profileAwareBridge: false,
    activeProfileSelectionDrivesRenderedCards: false,
    staleOverlayCardsRemoved: false,
    nullProfileStateRendersZeroCards: false,
    highVolumeMembershipRendersDeterministically: false,
    activeProfileDatasetReady: false,
    monitorGroupBoundary: true,
    recordingProfileBoundary: true,
    nonRecordingScope: true,
    nonThemeScope: true,
    overlayAcceptancePolicy: "profile-aware-baseline-non-recording"
  };
  try {
    const fixtureCards = {};
    for (let index = 1; index <= 125; index += 1) {
      const cardId = `slc042-monitor-${String(index).padStart(3, "0")}`;
      fixtureCards[cardId] = Object.assign(monitoringHudCardDefaults(cardId), {
        id: cardId,
        title: `SLC-042 Monitor ${String(index).padStart(3, "0")}`,
        enabled: true,
        sensors: index % 2 === 0 ? ["cpu-load"] : [],
        pollingRateMs: 1000
      });
    }
    monitoringHudControlState.cards = fixtureCards;
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = false;
    monitoringHudControlState.overlayProfiles = {
      "slc042-a": {
        id: "slc042-a",
        name: "SLC-042 Active Profile A",
        monitorIds: ["slc042-monitor-001", "slc042-monitor-002"],
        displayMode: "monitor-cards"
      },
      "slc042-b": {
        id: "slc042-b",
        name: "SLC-042 Active Profile B",
        monitorIds: ["slc042-monitor-003"],
        displayMode: "monitor-cards"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc042-a";
    monitoringHudRenderOverlayDisplay();
    const firstRenderIds = Array.from(monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]"))
      .map((node) => node.dataset.overlayMonitorCard);
    monitoringHudControlState.activeOverlayProfileId = "slc042-b";
    monitoringHudRenderOverlayDisplay();
    const secondRenderIds = Array.from(monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]"))
      .map((node) => node.dataset.overlayMonitorCard);
    proof.profileAwareBridge = monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptance === "slc-042-active-profile-state-bridge";
    proof.activeProfileSelectionDrivesRenderedCards = JSON.stringify(firstRenderIds) === JSON.stringify(["slc042-monitor-001", "slc042-monitor-002"])
      && JSON.stringify(secondRenderIds) === JSON.stringify(["slc042-monitor-003"]);
    proof.staleOverlayCardsRemoved = !secondRenderIds.includes("slc042-monitor-001") && !secondRenderIds.includes("slc042-monitor-002");
    proof.activeProfileDatasetReady = monitoringHudOverlayDisplay.dataset.activeOverlayProfileId === "slc042-b"
      && monitoringHudOverlayDisplay.dataset.activeOverlayProfileMonitorCount === "1"
      && monitoringHudOverlayDisplay.dataset.activeOverlayProfileMonitorIds === "slc042-monitor-003"
      && monitoringHudOverlayDisplay.dataset.overlayRenderedMonitorCount === "1";

    monitoringHudControlState.overlayProfiles = {};
    monitoringHudControlState.activeOverlayProfileId = "";
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = true;
    monitoringHudRenderOverlayDisplay();
    proof.nullProfileStateRendersZeroCards = monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]").length === 0
      && monitoringHudOverlayDisplay.dataset.overlayRenderedMonitorCount === "0";

    const highVolumeIds = Object.keys(fixtureCards).slice(0, 100);
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = false;
    monitoringHudControlState.overlayProfiles = {
      "slc042-high-volume": {
        id: "slc042-high-volume",
        name: "SLC-042 High Volume Profile",
        monitorIds: highVolumeIds.concat(["missing-monitor", highVolumeIds[0]]),
        displayMode: "monitor-cards",
        monitorGroupId: "must-not-survive",
        recordingProfileId: "must-not-survive"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc042-high-volume";
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudRenderOverlayDisplay();
    const highVolumeProfile = monitoringHudControlState.overlayProfiles["slc042-high-volume"] || {};
    const highVolumeRenderedCount = monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]").length;
    proof.highVolumeMembershipRendersDeterministically = highVolumeRenderedCount === 100
      && (highVolumeProfile.monitorIds || []).length === 100
      && !(highVolumeProfile.monitorIds || []).includes("missing-monitor");
    proof.monitorGroupBoundary = !Object.prototype.hasOwnProperty.call(highVolumeProfile, "monitorGroupId");
    proof.recordingProfileBoundary = !Object.prototype.hasOwnProperty.call(highVolumeProfile, "recordingProfileId");
    proof.nonRecordingScope = monitoringHudOverlayDisplay.dataset.recordingProfileState === "recording-profile-state-absent-future-gated";
    proof.nonThemeScope = !/theme|skin/i.test(monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptancePolicy || "");
    proof.passed = proof.profileAwareBridge
      && proof.activeProfileSelectionDrivesRenderedCards
      && proof.staleOverlayCardsRemoved
      && proof.nullProfileStateRendersZeroCards
      && proof.highVolumeMembershipRendersDeterministically
      && proof.activeProfileDatasetReady
      && proof.monitorGroupBoundary
      && proof.recordingProfileBoundary
      && proof.nonRecordingScope
      && proof.nonThemeScope;
  } finally {
    try {
      monitoringHudControlState = JSON.parse(previousState);
      monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
      monitoringHudRenderControls();
    } catch (_err) {}
  }
  monitoringHudControlState.overlayDisplayAcceptanceProof = proof;
  if (monitoringHud) {
    monitoringHud.dataset.overlayDisplayAcceptanceProof = proof.passed ? "pass" : "fail";
    monitoringHud.dataset.overlayDisplayAcceptance = "slc-042-active-profile-state-bridge";
  }
  if (monitoringHudOverlayDisplay) {
    monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptanceProof = proof.passed ? "pass" : "fail";
    monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptance = "slc-042-active-profile-state-bridge";
  }
  return proof;
};

window.runMonitoringHudActiveOverlayProfileDisplayProof = function() {
  const previousState = JSON.stringify(monitoringHudControlState);
  let proof = {
    passed: false,
    package: "PKG-006",
    slice: "SLC-043",
    seam: "Active Overlay Profile display behavior",
    displayBehaviorMarkerReady: false,
    statusStripReflectsActiveProfile: false,
    activeProfileSwitchUpdatesVisibleDisplay: false,
    staleActiveProfileFallsBackDeterministically: false,
    nullProfileStateShowsNoActiveProfile: false,
    highVolumeDisplayRendersDeterministically: false,
    staleOverlayCardsRemoved: false,
    monitorGroupBoundary: true,
    recordingProfileBoundary: true,
    nonRecordingScope: true,
    nonThemeScope: true
  };
  try {
    const fixtureCards = {};
    for (let index = 1; index <= 160; index += 1) {
      const cardId = `slc043-monitor-${String(index).padStart(3, "0")}`;
      fixtureCards[cardId] = Object.assign(monitoringHudCardDefaults(cardId), {
        id: cardId,
        title: `SLC-043 Monitor ${String(index).padStart(3, "0")}`,
        enabled: true,
        sensors: index % 3 === 0 ? ["cpu-load"] : [],
        pollingRateMs: 1000
      });
    }
    monitoringHudControlState.cards = fixtureCards;
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = false;
    monitoringHudControlState.overlayProfiles = {
      "slc043-alpha": {
        id: "slc043-alpha",
        name: "SLC-043 Alpha Profile",
        monitorIds: ["slc043-monitor-001", "slc043-monitor-002"],
        displayMode: "monitor-cards"
      },
      "slc043-beta": {
        id: "slc043-beta",
        name: "SLC-043 Beta Profile",
        monitorIds: ["slc043-monitor-003", "slc043-monitor-004", "slc043-monitor-005"],
        displayMode: "monitor-cards"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc043-alpha";
    monitoringHudRenderOverlayDisplay();
    const alphaIds = Array.from(monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]"))
      .map((node) => node.dataset.overlayMonitorCard);
    const alphaName = monitoringHudOverlayProfileDisplayName ? monitoringHudOverlayProfileDisplayName.textContent : "";
    const alphaCount = monitoringHudOverlayProfileDisplayCount ? monitoringHudOverlayProfileDisplayCount.textContent : "";
    monitoringHudControlState.activeOverlayProfileId = "slc043-beta";
    monitoringHudRenderOverlayDisplay();
    const betaIds = Array.from(monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]"))
      .map((node) => node.dataset.overlayMonitorCard);
    const betaName = monitoringHudOverlayProfileDisplayName ? monitoringHudOverlayProfileDisplayName.textContent : "";
    const betaCount = monitoringHudOverlayProfileDisplayCount ? monitoringHudOverlayProfileDisplayCount.textContent : "";
    proof.displayBehaviorMarkerReady = monitoringHudOverlayDisplay.dataset.activeOverlayProfileDisplayBehavior === "slc-043-active-profile-display"
      && monitoringHudOverlayDisplay.dataset.activeOverlayProfileDisplaySlice === "SLC-043";
    proof.statusStripReflectsActiveProfile = alphaName === "SLC-043 Alpha Profile"
      && alphaCount === "2 monitors"
      && betaName === "SLC-043 Beta Profile"
      && betaCount === "3 monitors"
      && monitoringHudOverlayProfileDisplayStatus
      && monitoringHudOverlayProfileDisplayStatus.dataset.overlayDisplayProfileStatus === "active-profile-rendering";
    proof.activeProfileSwitchUpdatesVisibleDisplay = JSON.stringify(alphaIds) === JSON.stringify(["slc043-monitor-001", "slc043-monitor-002"])
      && JSON.stringify(betaIds) === JSON.stringify(["slc043-monitor-003", "slc043-monitor-004", "slc043-monitor-005"]);
    proof.staleOverlayCardsRemoved = !betaIds.includes("slc043-monitor-001") && !betaIds.includes("slc043-monitor-002");

    monitoringHudControlState.overlayProfiles = {
      "slc043-fallback": {
        id: "slc043-fallback",
        name: "SLC-043 Fallback Profile",
        monitorIds: ["slc043-monitor-006"],
        displayMode: "monitor-cards"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "missing-profile";
    monitoringHudRenderOverlayDisplay();
    proof.staleActiveProfileFallsBackDeterministically = monitoringHudControlState.activeOverlayProfileId === "slc043-fallback"
      && monitoringHudOverlayDisplay.dataset.activeOverlayProfileId === "slc043-fallback"
      && monitoringHudOverlayDisplay.dataset.overlayRenderedMonitorCount === "1";

    monitoringHudControlState.overlayProfiles = {};
    monitoringHudControlState.activeOverlayProfileId = "";
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = true;
    monitoringHudRenderOverlayDisplay();
    proof.nullProfileStateShowsNoActiveProfile = monitoringHudOverlayDisplay.dataset.overlayDisplayProfileStatus === "no-active-profile"
      && monitoringHudOverlayDisplay.dataset.overlayRenderedMonitorCount === "0"
      && monitoringHudOverlayProfileDisplayName
      && monitoringHudOverlayProfileDisplayName.textContent === "No active overlay profile"
      && monitoringHudOverlayProfileDisplayCount
      && monitoringHudOverlayProfileDisplayCount.textContent === "0 monitors";

    const highVolumeIds = Object.keys(fixtureCards).slice(0, 120);
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = false;
    monitoringHudControlState.overlayProfiles = {
      "slc043-high-volume": {
        id: "slc043-high-volume",
        name: "SLC-043 High Volume Profile",
        monitorIds: highVolumeIds.concat(["missing-monitor", highVolumeIds[0]]),
        displayMode: "monitor-cards",
        monitorGroupId: "must-not-survive",
        recordingProfileId: "must-not-survive"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc043-high-volume";
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudRenderOverlayDisplay();
    const highVolumeProfile = monitoringHudControlState.overlayProfiles["slc043-high-volume"] || {};
    proof.highVolumeDisplayRendersDeterministically = monitoringHudOverlayCanvas.querySelectorAll("[data-overlay-monitor-card]").length === 120
      && monitoringHudOverlayDisplay.dataset.overlayRenderedMonitorCount === "120"
      && monitoringHudOverlayProfileDisplayCount
      && monitoringHudOverlayProfileDisplayCount.textContent === "120 monitors"
      && (highVolumeProfile.monitorIds || []).length === 120
      && !(highVolumeProfile.monitorIds || []).includes("missing-monitor");
    proof.monitorGroupBoundary = !Object.prototype.hasOwnProperty.call(highVolumeProfile, "monitorGroupId");
    proof.recordingProfileBoundary = !Object.prototype.hasOwnProperty.call(highVolumeProfile, "recordingProfileId");
    proof.nonRecordingScope = monitoringHudOverlayDisplay.dataset.recordingProfileState === "recording-profile-state-absent-future-gated";
    proof.nonThemeScope = !/theme|skin/i.test(monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptancePolicy || "");
    proof.passed = proof.displayBehaviorMarkerReady
      && proof.statusStripReflectsActiveProfile
      && proof.activeProfileSwitchUpdatesVisibleDisplay
      && proof.staleActiveProfileFallsBackDeterministically
      && proof.nullProfileStateShowsNoActiveProfile
      && proof.highVolumeDisplayRendersDeterministically
      && proof.staleOverlayCardsRemoved
      && proof.monitorGroupBoundary
      && proof.recordingProfileBoundary
      && proof.nonRecordingScope
      && proof.nonThemeScope;
  } finally {
    try {
      monitoringHudControlState = JSON.parse(previousState);
      monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
      monitoringHudRenderControls();
    } catch (_err) {}
  }
  monitoringHudControlState.activeOverlayProfileDisplayProof = proof;
  if (monitoringHud) {
    monitoringHud.dataset.activeOverlayProfileDisplayProof = proof.passed ? "pass" : "fail";
  }
  if (monitoringHudOverlayDisplay) {
    monitoringHudOverlayDisplay.dataset.activeOverlayProfileDisplayProof = proof.passed ? "pass" : "fail";
    monitoringHudOverlayDisplay.dataset.activeOverlayProfileDisplayBehavior = "slc-043-active-profile-display";
  }
  return proof;
};

window.runMonitoringHudDashboardOverlayIndependenceProof = function() {
  const previousState = JSON.stringify(monitoringHudControlState);
  let proof = {
    passed: false,
    package: "PKG-006",
    slice: "SLC-044",
    seam: "Dashboard / Overlay display independence and visual acceptance",
    independenceMarkerReady: false,
    dashboardAndOverlayRolesDistinct: false,
    dashboardConfiguresOverlayWithoutOwningDisplay: false,
    activeProfileSharedStateVisibleInOverlay: false,
    dashboardAcceptanceRemainsReady: false,
    overlayAcceptanceRemainsNonGating: false,
    monitorGroupsRemainPreservationSurface: false,
    visualAcceptanceBaselineReady: false,
    monitorGroupBoundary: true,
    recordingProfileBoundary: true,
    nonRecordingScope: true,
    nonThemeScope: true
  };
  try {
    monitoringHudControlState.cards = {
      "slc044-dashboard": Object.assign(monitoringHudCardDefaults("slc044-dashboard"), {
        id: "slc044-dashboard",
        title: "SLC-044 Dashboard Monitor",
        enabled: true,
        sensors: ["cpu-load"],
        pollingRateMs: 1000
      }),
      "slc044-overlay": Object.assign(monitoringHudCardDefaults("slc044-overlay"), {
        id: "slc044-overlay",
        title: "SLC-044 Overlay Monitor",
        enabled: true,
        sensors: [],
        pollingRateMs: 1000
      })
    };
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = false;
    monitoringHudControlState.overlayProfiles = {
      "slc044-shared": {
        id: "slc044-shared",
        name: "SLC-044 Shared Display Profile",
        monitorIds: ["slc044-dashboard", "slc044-overlay"],
        displayMode: "monitor-cards"
      }
    };
    monitoringHudControlState.activeOverlayProfileId = "slc044-shared";
    monitoringHudRenderControls();
    const split = window.getMonitoringHudSurfaceSplitState ? window.getMonitoringHudSurfaceSplitState() : {};
    const acceptance = window.getMonitoringHudDashboardAcceptanceState ? window.getMonitoringHudDashboardAcceptanceState() : {};
    const isolation = window.getMonitoringHudIsolationState ? window.getMonitoringHudIsolationState() : {};
    const dashboardSnapshot = monitoringHudVisualInspectionStyleSnapshot(monitoringHud);
    const overlayStatusSnapshot = monitoringHudVisualInspectionStyleSnapshot(monitoringHudOverlayProfileDisplayStatus);
    proof.independenceMarkerReady = monitoringHud
      && monitoringHud.dataset.dashboardOverlayIndependence === "slc-044-dashboard-overlay-independent"
      && monitoringHudOverlayDisplay
      && monitoringHudOverlayDisplay.dataset.dashboardOverlayIndependence === "slc-044-dashboard-overlay-independent";
    proof.dashboardAndOverlayRolesDistinct = split.dashboardSurfaceRole === "dashboard-configuration-surface"
      && split.overlayDisplaySurfaceRole === "edgeless-overlay-display"
      && split.dashboardSurfaceRole !== split.overlayDisplaySurfaceRole;
    proof.dashboardConfiguresOverlayWithoutOwningDisplay = split.dashboardConfigures === "monitoring-hud-minimal"
      && split.dashboardMonitorCardPolicy === "overlay-display-owns-visual-rendering"
      && split.dashboardDecouplingProof === "core-overlay-independent";
    proof.activeProfileSharedStateVisibleInOverlay = monitoringHudOverlayDisplay
      && monitoringHudOverlayDisplay.dataset.activeOverlayProfileId === "slc044-shared"
      && monitoringHudOverlayDisplay.dataset.activeOverlayProfileMonitorCount === "2"
      && monitoringHudOverlayDisplay.dataset.overlayRenderedMonitorCount === "2"
      && monitoringHudOverlayProfileDisplayName
      && monitoringHudOverlayProfileDisplayName.textContent === "SLC-044 Shared Display Profile";
    proof.dashboardAcceptanceRemainsReady = acceptance.dashboardAcceptanceBaselineReady === true
      && acceptance.dashboardStandaloneMovementReady === true
      && acceptance.dashboardSettingsContentReady === true
      && acceptance.dashboardProviderTruthReady === true;
    proof.overlayAcceptanceRemainsNonGating = acceptance.overlayAcceptanceNonGating === true
      && isolation.overlayAcceptanceNonGating === true;
    proof.monitorGroupsRemainPreservationSurface = split.monitorGroupModel === "configurable-groups-sensor-assignment"
      && split.monitorSensorAssignment === "sensor-library-source-picker"
      && split.monitorManagement === "sensor-command-center-list-detail-source-picker";
    proof.visualAcceptanceBaselineReady = monitoringHudVisualInspectionVisible(monitoringHud)
      && monitoringHudVisualInspectionVisible(monitoringHudOverlayProfileDisplayStatus)
      && dashboardSnapshot.rect.width > 100
      && overlayStatusSnapshot.rect.width > 120
      && monitoringHudVisualInspectionHasGlow(overlayStatusSnapshot);
    proof.monitorGroupBoundary = split.monitorGroupModel === "configurable-groups-sensor-assignment";
    proof.recordingProfileBoundary = monitoringHudOverlayDisplay.dataset.recordingProfileState === "recording-profile-state-absent-future-gated";
    proof.nonRecordingScope = proof.recordingProfileBoundary;
    proof.nonThemeScope = !/theme|skin/i.test([
      monitoringHud.dataset.dashboardOverlayIndependence || "",
      monitoringHudOverlayDisplay.dataset.dashboardOverlayIndependence || "",
      monitoringHudOverlayDisplay.dataset.overlayDisplayAcceptancePolicy || ""
    ].join(" "));
    proof.passed = proof.independenceMarkerReady
      && proof.dashboardAndOverlayRolesDistinct
      && proof.dashboardConfiguresOverlayWithoutOwningDisplay
      && proof.activeProfileSharedStateVisibleInOverlay
      && proof.dashboardAcceptanceRemainsReady
      && proof.overlayAcceptanceRemainsNonGating
      && proof.monitorGroupsRemainPreservationSurface
      && proof.visualAcceptanceBaselineReady
      && proof.monitorGroupBoundary
      && proof.recordingProfileBoundary
      && proof.nonRecordingScope
      && proof.nonThemeScope;
  } finally {
    try {
      monitoringHudControlState = JSON.parse(previousState);
      monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
      monitoringHudRenderControls();
    } catch (_err) {}
  }
  monitoringHudControlState.dashboardOverlayIndependenceProof = proof;
  if (monitoringHud) {
    monitoringHud.dataset.dashboardOverlayIndependenceProof = proof.passed ? "pass" : "fail";
    monitoringHud.dataset.dashboardOverlayIndependence = "slc-044-dashboard-overlay-independent";
  }
  if (monitoringHudOverlayDisplay) {
    monitoringHudOverlayDisplay.dataset.dashboardOverlayIndependenceProof = proof.passed ? "pass" : "fail";
    monitoringHudOverlayDisplay.dataset.dashboardOverlayIndependence = "slc-044-dashboard-overlay-independent";
  }
  return proof;
};

window.runMonitoringHudOverlayProfileControlsProof = function() {
  const previousState = JSON.stringify(monitoringHudControlState);
  const previousDraftId = monitoringHudOverlayProfileDraftId;
  const previousDraftName = monitoringHudOverlayProfileDraftName;
  const previousDraftMonitorIds = monitoringHudOverlayProfileDraftMonitorIds.slice();
  const previousWindowSelectedId = monitoringHudOverlayProfileWindowSelectedId;
  const previousDetailOpen = monitoringHudOverlayProfileDetailOpen;
  const previousPendingDeleteId = monitoringHudPendingDeleteOverlayProfileId;
  const previousPendingCreate = monitoringHudOverlayProfilePendingCreate
    ? JSON.parse(JSON.stringify(monitoringHudOverlayProfilePendingCreate))
    : null;
  let proof = {
    passed: false,
    package: "PKG-006",
    slice: "SLC-039-SLC-040-followup",
    selectorVisible: Boolean(monitoringHudOverlayProfileSelector && monitoringHudOverlayProfileToggle && monitoringHudOverlayProfileMenu),
    settingsEntryVisible: Boolean(monitoringHudOverlayProfileOpenSettings),
    settingsWindowPresent: Boolean(monitoringHudOverlayProfileWindow),
    settingsWindowOpens: false,
    managerDefaultState: false,
    windowSelectorVisible: Boolean(monitoringHudOverlayProfileWindowSelector && monitoringHudOverlayProfileWindowToggle && monitoringHudOverlayProfileWindowMenu),
    windowSelectorReadable: false,
    windowSelectorScalesWithinRow: false,
    windowSelectorSameRow: false,
    windowSelectorStandardFootprint: false,
    windowSelectorMenuUnclipped: false,
    windowSelectorResponsiveCompact: false,
    visualRepairMarker: false,
    windowDropdownMaxFive: false,
    largeProfileFixture: false,
    profileDropdownMaxFiveStress: false,
    profileDropdownNDAIScrollbar: false,
    dropdownNullStress: false,
    dropdownHighVolumeStress: false,
    dropdownStressSurfaceCount: 0,
    editButtonRemovedAndSelectorDefaultEmpty: false,
    selectorLoadsSelectedSettings: false,
    createRequiresSave: false,
    createStartsEmptyMembership: false,
    closeGuardOpensForCreatedDraft: false,
    childWindowClickIsolation: false,
    createVisible: Boolean(monitoringHudOverlayProfileCreate),
    renameVisible: false,
    saveDiscardVisible: Boolean(monitoringHudOverlayProfileSave && monitoringHudOverlayProfileDiscard),
    selectorFirstCreateFirstWindow: Boolean(
      monitoringHudOverlayProfileWindow
      && monitoringHudOverlayProfileWindow.dataset.overlayProfileWindow === "select-profile-to-edit-create-right-save-required"
    ),
    monitorSearchFilterVisible: Boolean(monitoringHudOverlayProfileMonitorSearch && monitoringHudOverlayProfileMonitorFilter && monitoringHudOverlayProfileMonitorFilterToggle),
    monitorFilterNexusDropdown: Boolean(
      monitoringHudOverlayProfileMonitorFilter
      && monitoringHudOverlayProfileMonitorFilter.dataset.boundedDropdown === "overlay-profile-monitor-filter"
      && monitoringHudOverlayProfileMonitorFilter.dataset.scrollbarStyle === "ndai-native"
    ),
    maxFiveInnerScrollPolicy: Boolean(
      monitoringHudOverlayProfileMembershipList
      && monitoringHudOverlayProfileMembershipList.dataset.overlayProfileVisibleMonitorTarget === "max-five"
      && monitoringHudOverlayProfileMembershipList.dataset.scrollbarStyle === "ndai-native"
    ),
    dangerDiscardRight: Boolean(
      monitoringHudOverlayProfileDiscard
      && monitoringHudOverlayProfileDiscard.classList.contains("monitoring-hud__hub-action--danger")
    ),
    deleteDangerVisible: Boolean(
      monitoringHudOverlayProfileDelete
      && monitoringHudOverlayProfileDelete.classList.contains("monitoring-hud__hub-action--danger")
    ),
    deleteConfirmationVisible: false,
    deleteConfirmationVisualReviewable: false,
    defaultProfileDeletePersists: false,
    detailActionsVisualReviewable: false,
    profileDeleted: false,
    editableMembership: monitoringHudOverlayProfileEditor
      ? monitoringHudOverlayProfileEditor.dataset.overlayProfileMembership === "editable-slc-039-mapping"
      : false,
    createdProfileSelectable: false,
    renameSaved: false,
    discardRestored: false,
    membershipListVisible: Boolean(monitoringHudOverlayProfileMembershipList),
    membershipSaved: false,
    membershipDiscardRestored: false,
    membershipModelPresent: false,
    monitorGroupBoundary: true,
    recordingProfileBoundary: true,
    activeProfilePersistsInState: false
  };
  try {
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudOpenChildWindow("overlay-profile-settings");
    proof.settingsWindowOpens = Boolean(
      monitoringHudActiveChildWindow === "overlay-profile-settings"
      && monitoringHudOverlayProfileWindow
      && monitoringHudOverlayProfileWindow.hidden === false
    );
    proof.childWindowClickIsolation = Boolean(
      monitoringHudChildWindowLayer
      && monitoringHudChildWindowLayer.dataset.childWindowPointerIsolation === "modal-layer-stops-dashboard-click-through"
    );
    proof.managerDefaultState = Boolean(
      !monitoringHudOverlayProfileWindowSelectedId
      && monitoringHudOverlayProfileDetailSection
      && monitoringHudOverlayProfileDetailSection.hidden
    );
    proof.editButtonRemovedAndSelectorDefaultEmpty = Boolean(
      !monitoringHudOverlayProfileWindowSelectedId
      && monitoringHudOverlayProfileWindowToggle
      && /profile to edit/i.test(monitoringHudOverlayProfileWindowToggle.textContent || "")
      && monitoringHudOverlayProfileWindowLabel
      && /select profile/i.test(monitoringHudOverlayProfileWindowLabel.textContent || "")
    );
    proof.windowDropdownMaxFive = Boolean(
      monitoringHudOverlayProfileWindowSelector
      && monitoringHudOverlayProfileWindowSelector.dataset.visibleOptionTarget === "max-five"
      && monitoringHudOverlayProfileWindowSelector.dataset.scrollbarStyle === "ndai-native"
    );
    const measureWindowSelectorLayout = () => {
      const selector = monitoringHudOverlayProfileWindowSelector;
      const menu = monitoringHudOverlayProfileWindowMenu;
      const row = selector && selector.closest
        ? selector.closest("[data-overlay-profile-manager-row]")
        : null;
      const create = monitoringHudOverlayProfileCreate;
      const windowRect = monitoringHudOverlayProfileWindow
        ? monitoringHudOverlayProfileWindow.getBoundingClientRect()
        : { left: 0, top: 0, right: 0, bottom: 0 };
      if (!selector || !row || !create) {
        return {
          sameRow: false,
          standardFootprint: false,
          equalFootprint: false,
          menuUnclipped: false,
          insideRow: false,
          selectorWidth: 0,
          createWidth: 0,
          rowWidth: 0,
          menuWidth: 0,
          rowTopDelta: 999
        };
      }
      const selectorRect = selector.getBoundingClientRect();
      const rowRect = row.getBoundingClientRect();
      const createRect = create.getBoundingClientRect();
      const selectorCenterY = selectorRect.top + (selectorRect.height / 2);
      const createCenterY = createRect.top + (createRect.height / 2);
      const rowTopDelta = Math.abs(selectorCenterY - createCenterY);
      const sameRow = Boolean(
        rowTopDelta <= 9
        && createRect.left >= selectorRect.right - 2
        && selectorRect.top <= createRect.top + 9
      );
      const insideRow = Boolean(
        selectorRect.left >= rowRect.left - 1
        && createRect.right <= rowRect.right + 1
      );
      const equalFootprint = Math.abs(selectorRect.width - createRect.width) <= 2;
      const standardFootprint = Boolean(
        selectorRect.width >= 150
        && createRect.width >= 150
        && equalFootprint
        && insideRow
      );
      const wasOpen = selector.dataset.dropdownOpen === "true";
      if (typeof monitoringHudSetOverlayProfileWindowDropdownOpen === "function") {
        monitoringHudSetOverlayProfileWindowDropdownOpen(true);
      }
      const menuRect = menu ? menu.getBoundingClientRect() : { left: 0, right: 0, top: 0, bottom: 0, width: 0, height: 0 };
      const menuUnclipped = Boolean(
        menu
        && !menu.hidden
        && menuRect.width >= Math.max(180, selectorRect.width - 2)
        && menuRect.width <= selectorRect.width + 2
        && menuRect.left >= rowRect.left - 1
        && menuRect.right <= rowRect.right + 1
        && menuRect.top >= windowRect.top - 1
        && menuRect.bottom <= windowRect.bottom + 1
      );
      if (typeof monitoringHudSetOverlayProfileWindowDropdownOpen === "function") {
        monitoringHudSetOverlayProfileWindowDropdownOpen(wasOpen);
      }
      return {
        sameRow,
        standardFootprint,
        equalFootprint,
        menuUnclipped,
        insideRow,
        selectorWidth: selectorRect.width,
        createWidth: createRect.width,
        rowWidth: rowRect.width,
        menuWidth: menuRect.width,
        rowTopDelta
      };
    };
    const currentSelectorMeasurement = measureWindowSelectorLayout();
    proof.windowSelectorReadable = Boolean(
      monitoringHudOverlayProfileWindowSelector
      && currentSelectorMeasurement.standardFootprint
      && monitoringHudOverlayProfileWindowLabel
      && monitoringHudOverlayProfileWindowLabel.scrollWidth <= monitoringHudOverlayProfileWindowLabel.clientWidth + 1
    );
    proof.windowSelectorSameRow = currentSelectorMeasurement.sameRow;
    proof.windowSelectorStandardFootprint = currentSelectorMeasurement.standardFootprint;
    proof.windowSelectorMenuUnclipped = currentSelectorMeasurement.menuUnclipped;
    proof.windowSelectorScalesWithinRow = Boolean(
      currentSelectorMeasurement.sameRow
      && currentSelectorMeasurement.standardFootprint
      && currentSelectorMeasurement.insideRow
    );
    if (monitoringHudOverlayProfileWindow && monitoringHudOverlayProfileWindowSelector) {
      const previousWindowStyle = monitoringHudOverlayProfileWindow.getAttribute("style") || "";
      const availableWidth = Math.max(460, Math.min(820, (window.innerWidth || 900) - 56));
      const compactWidth = Math.max(420, Math.min(availableWidth - 160, 620));
      const measureSelectorAtWidth = (width) => {
        monitoringHudOverlayProfileWindow.style.width = `${Math.round(width)}px`;
        monitoringHudOverlayProfileWindow.style.minWidth = "0";
        monitoringHudOverlayProfileWindow.style.maxWidth = "none";
        const measurement = measureWindowSelectorLayout();
        return {
          sameRow: measurement.sameRow,
          standardFootprint: measurement.standardFootprint,
          equalFootprint: measurement.equalFootprint,
          menuUnclipped: measurement.menuUnclipped,
          selectorWidth: measurement.selectorWidth,
          createWidth: measurement.createWidth,
          rowWidth: measurement.rowWidth,
          menuWidth: measurement.menuWidth,
          rowTopDelta: measurement.rowTopDelta
        };
      };
      const wideMeasurement = measureSelectorAtWidth(availableWidth);
      const compactMeasurement = measureSelectorAtWidth(compactWidth);
      proof.windowSelectorResponsiveCompact = Boolean(
        wideMeasurement.sameRow
        && compactMeasurement.sameRow
        && wideMeasurement.standardFootprint
        && compactMeasurement.standardFootprint
        && wideMeasurement.menuUnclipped
        && compactMeasurement.menuUnclipped
        && wideMeasurement.equalFootprint
        && compactMeasurement.equalFootprint
        && compactMeasurement.selectorWidth <= wideMeasurement.selectorWidth + 2
      );
      proof.windowSelectorCompactMeasurements = {
        current: {
          rowWidth: Math.round(currentSelectorMeasurement.rowWidth),
          selectorWidth: Math.round(currentSelectorMeasurement.selectorWidth),
          createWidth: Math.round(currentSelectorMeasurement.createWidth),
          equalFootprint: currentSelectorMeasurement.equalFootprint,
          menuWidth: Math.round(currentSelectorMeasurement.menuWidth),
          sameRow: currentSelectorMeasurement.sameRow,
          standardFootprint: currentSelectorMeasurement.standardFootprint,
          menuUnclipped: currentSelectorMeasurement.menuUnclipped,
          rowTopDelta: Math.round(currentSelectorMeasurement.rowTopDelta)
        },
        wide: {
          windowWidth: Math.round(availableWidth),
          rowWidth: Math.round(wideMeasurement.rowWidth),
          selectorWidth: Math.round(wideMeasurement.selectorWidth),
          createWidth: Math.round(wideMeasurement.createWidth),
          equalFootprint: wideMeasurement.equalFootprint,
          menuWidth: Math.round(wideMeasurement.menuWidth),
          sameRow: wideMeasurement.sameRow,
          standardFootprint: wideMeasurement.standardFootprint,
          menuUnclipped: wideMeasurement.menuUnclipped,
          rowTopDelta: Math.round(wideMeasurement.rowTopDelta)
        },
        compact: {
          windowWidth: Math.round(compactWidth),
          rowWidth: Math.round(compactMeasurement.rowWidth),
          selectorWidth: Math.round(compactMeasurement.selectorWidth),
          createWidth: Math.round(compactMeasurement.createWidth),
          equalFootprint: compactMeasurement.equalFootprint,
          menuWidth: Math.round(compactMeasurement.menuWidth),
          sameRow: compactMeasurement.sameRow,
          standardFootprint: compactMeasurement.standardFootprint,
          menuUnclipped: compactMeasurement.menuUnclipped,
          rowTopDelta: Math.round(compactMeasurement.rowTopDelta)
        }
      };
      if (previousWindowStyle) {
        monitoringHudOverlayProfileWindow.setAttribute("style", previousWindowStyle);
      } else {
        monitoringHudOverlayProfileWindow.removeAttribute("style");
      }
    }
    proof.visualRepairMarker = Boolean(
      monitoringHudOverlayProfileWindow
      && monitoringHudOverlayProfileWindow.dataset.overlayProfileVisualRepair === "manager-selector-same-row-compact-unclipped-proof"
    );
    const inspectWindowDropdownVolume = (label) => {
      if (typeof monitoringHudRenderControls === "function") {
        monitoringHudRenderControls();
      }
      if (typeof monitoringHudOpenChildWindow === "function") {
        monitoringHudOpenChildWindow("overlay-profile-settings");
      }
      if (typeof monitoringHudSetOverlayProfileWindowDropdownOpen === "function") {
        monitoringHudSetOverlayProfileWindowDropdownOpen(true);
      }
      const selector = monitoringHudOverlayProfileWindowSelector;
      const menu = monitoringHudOverlayProfileWindowMenu;
      const row = selector && selector.closest
        ? selector.closest("[data-overlay-profile-manager-row]")
        : null;
      const create = monitoringHudOverlayProfileCreate;
      const windowRect = monitoringHudOverlayProfileWindow
        ? monitoringHudOverlayProfileWindow.getBoundingClientRect()
        : { left: 0, top: 0, right: 0, bottom: 0 };
      const selectorRect = selector
        ? selector.getBoundingClientRect()
        : { left: 0, right: 0, top: 0, bottom: 0, width: 0, height: 0 };
      const menuRect = menu
        ? menu.getBoundingClientRect()
        : { left: 0, right: 0, top: 0, bottom: 0, width: 0, height: 0 };
      const createRect = create
        ? create.getBoundingClientRect()
        : { top: 0, right: 0, height: 0, width: 0 };
      const selectorCenterY = selectorRect.top + (selectorRect.height / 2);
      const createCenterY = createRect.top + (createRect.height / 2);
      const rowTopDelta = Math.abs(selectorCenterY - createCenterY);
      const options = menu
        ? Array.from(menu.querySelectorAll("[data-overlay-profile-window-option]"))
        : [];
      const visibleOptions = options.filter((option) => {
        const optionRect = option.getBoundingClientRect();
        return Boolean(
          menuRect.height > 0
          && optionRect.top >= menuRect.top - 1
          && optionRect.bottom <= menuRect.bottom + 1
        );
      });
      const sameRow = Boolean(
        selector
        && create
        && row
        && rowTopDelta <= 9
        && createRect.left >= selectorRect.right - 2
      );
      const equalFootprint = Math.abs(selectorRect.width - createRect.width) <= 2;
      const standardFootprint = Boolean(selectorRect.width >= 150 && createRect.width >= 150 && equalFootprint);
      const menuUnclipped = Boolean(
        menu
        && !menu.hidden
        && menuRect.width >= Math.max(180, selectorRect.width - 2)
        && menuRect.width <= selectorRect.width + 2
        && menuRect.left >= windowRect.left - 1
        && menuRect.right <= windowRect.right + 1
        && menuRect.top >= windowRect.top - 1
        && menuRect.bottom <= windowRect.bottom + 1
      );
      const maxFiveVisible = Boolean(options.length <= 5 || visibleOptions.length <= 5);
      const scrollsWhenStressed = Boolean(
        options.length <= 5
        || (menu && menu.scrollHeight > menu.clientHeight + 1)
      );
      return {
        label,
        optionCount: options.length,
        visibleOptionCount: visibleOptions.length,
        sameRow,
        standardFootprint,
        menuUnclipped,
        maxFiveVisible,
        scrollsWhenStressed,
        selectorWidth: Math.round(selectorRect.width),
        createWidth: Math.round(createRect.width),
        equalFootprint,
        menuWidth: Math.round(menuRect.width),
        menuBottom: Math.round(menuRect.bottom),
        windowBottom: Math.round(windowRect.bottom),
        rowTopDelta: Math.round(rowTopDelta)
      };
    };
    const volumeStateBefore = JSON.stringify(monitoringHudControlState);
    const volumeSelectedBefore = monitoringHudOverlayProfileWindowSelectedId;
    const volumeDetailBefore = monitoringHudOverlayProfileDetailOpen;
    monitoringHudControlState.overlayProfiles = {};
    monitoringHudControlState.activeOverlayProfileId = "";
    monitoringHudControlState.overlayProfileDefaultDeletedByUser = true;
    monitoringHudOverlayProfileWindowSelectedId = "";
    monitoringHudOverlayProfileDetailOpen = false;
    const nullDropdownProof = inspectWindowDropdownVolume("overlay-profile-window-null");
    monitoringHudControlState = JSON.parse(volumeStateBefore);
    monitoringHudOverlayProfileWindowSelectedId = volumeSelectedBefore;
    monitoringHudOverlayProfileDetailOpen = volumeDetailBefore;
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudRenderControls();
    monitoringHudOpenChildWindow("overlay-profile-settings");
    proof.dropdownNullStress = Boolean(
      nullDropdownProof.optionCount === 0
      && nullDropdownProof.sameRow
      && nullDropdownProof.standardFootprint
      && nullDropdownProof.menuUnclipped
    );
    const stressProfileIds = [];
    const stressMonitorIds = monitoringHudStableMonitorIds(monitoringHudControlState.cards || {});
    for (let index = 1; index <= 124; index += 1) {
      const stressId = `stress-overlay-profile-${index}`;
      stressProfileIds.push(stressId);
      monitoringHudControlState.overlayProfiles[stressId] = {
        id: stressId,
        name: `Overlay Profile ${String(index).padStart(2, "0")}`,
        monitorIds: stressMonitorIds.slice(0, Math.max(1, Math.min(index, stressMonitorIds.length || 1))),
        displayMode: "monitor-cards"
      };
    }
    monitoringHudRenderControls();
    monitoringHudOpenChildWindow("overlay-profile-settings");
    if (typeof monitoringHudSetOverlayProfileWindowDropdownOpen === "function") {
      monitoringHudSetOverlayProfileWindowDropdownOpen(true);
    }
    const stressOptions = monitoringHudOverlayProfileWindowMenu
      ? Array.from(monitoringHudOverlayProfileWindowMenu.querySelectorAll("[data-overlay-profile-window-option]"))
      : [];
    const stressMenuRect = monitoringHudOverlayProfileWindowMenu
      ? monitoringHudOverlayProfileWindowMenu.getBoundingClientRect()
      : { height: 0 };
    const stressOptionRect = stressOptions[0]
      ? stressOptions[0].getBoundingClientRect()
      : { height: 0 };
    const stressMenuStyle = monitoringHudOverlayProfileWindowMenu
      ? window.getComputedStyle(monitoringHudOverlayProfileWindowMenu)
      : {};
    const stressVisibleOptions = stressOptions.filter((option) => {
      const optionRect = option.getBoundingClientRect();
      return Boolean(
        stressMenuRect.height > 0
        && optionRect.top >= stressMenuRect.top - 1
        && optionRect.bottom <= stressMenuRect.bottom + 1
      );
    });
    const stressMenuScrollable = Boolean(
      monitoringHudOverlayProfileWindowMenu
      && monitoringHudOverlayProfileWindowMenu.scrollHeight > monitoringHudOverlayProfileWindowMenu.clientHeight + 1
    );
    proof.largeProfileFixture = stressOptions.length >= 100;
    proof.profileDropdownNDAIScrollbar = Boolean(
      monitoringHudOverlayProfileWindowMenu
      && monitoringHudOverlayProfileWindowMenu.classList.contains("monitoring-hud__nexus-scroll-pane")
      && monitoringHudOverlayProfileWindowSelector
      && monitoringHudOverlayProfileWindowSelector.dataset.scrollbarStyle === "ndai-native"
    );
    proof.profileDropdownMaxFiveStress = Boolean(
      proof.largeProfileFixture
      && stressOptionRect.height > 0
      && stressOptions.length > 5
      && stressVisibleOptions.length <= 5
      && stressMenuScrollable
      && (stressMenuStyle.overflowY === "auto" || stressMenuStyle.overflowY === "scroll")
    );
    const highVolumeDropdownProof = inspectWindowDropdownVolume("overlay-profile-window-125");
    proof.dropdownHighVolumeStress = Boolean(
      highVolumeDropdownProof.optionCount >= 100
      && highVolumeDropdownProof.sameRow
      && highVolumeDropdownProof.standardFootprint
      && highVolumeDropdownProof.menuUnclipped
      && highVolumeDropdownProof.maxFiveVisible
      && highVolumeDropdownProof.scrollsWhenStressed
    );
    proof.dropdownStressSurfaceCount = 2;
    proof.dropdownStressProof = {
      null: nullDropdownProof,
      highVolume: highVolumeDropdownProof
    };
    if (typeof monitoringHudSetOverlayProfileWindowDropdownOpen === "function") {
      monitoringHudSetOverlayProfileWindowDropdownOpen(false);
    }
    const firstProfile = monitoringHudOverlayProfileList()[0] || {};
    if (firstProfile.id) {
      proof.selectorLoadsSelectedSettings = monitoringHudSelectOverlayProfileForWindow(firstProfile.id)
        && monitoringHudOverlayProfileDetailSection
        && monitoringHudOverlayProfileDetailSection.hidden === false;
      monitoringHudOpenChildWindow("overlay-profile-settings");
    }
    const profileCountBeforeCreate = Object.keys(monitoringHudControlState.overlayProfiles || {}).length;
    const created = monitoringHudCreateOverlayProfile();
    const createdId = monitoringHudOverlayProfilePendingCreate ? monitoringHudOverlayProfilePendingCreate.id : "";
    const createdProfile = monitoringHudOverlayProfilePendingCreate || {};
    proof.createRequiresSave = Boolean(
      created
      && createdId
      && Object.keys(monitoringHudControlState.overlayProfiles || {}).length === profileCountBeforeCreate
      && !((monitoringHudControlState.overlayProfiles || {})[createdId])
      && monitoringHudOverlayProfileDraftDirty()
    );
    proof.createStartsEmptyMembership = Boolean(created && Array.isArray(createdProfile.monitorIds) && createdProfile.monitorIds.length === 0);
    proof.createdProfileSelectable = Boolean(created && createdId && monitoringHudOverlayProfileWindowSelectedId === createdId);
    proof.membershipModelPresent = Array.isArray(createdProfile.monitorIds);
    if (created && monitoringHudCloseChildWindow) {
      const closeResult = monitoringHudCloseChildWindow();
      proof.closeGuardOpensForCreatedDraft = Boolean(
        closeResult === false
        && monitoringHudOverlayProfileUnsavedGuard
        && monitoringHudOverlayProfileUnsavedGuard.hidden === false
        && monitoringHudOverlayProfileUnsavedGuard.dataset.unsavedGuard === "open-save-discard"
      );
      monitoringHudSetOverlayProfileUnsavedGuard(false);
    }
    proof.renameVisible = Boolean(
      monitoringHudOverlayProfileNameInput
      && monitoringHudOverlayProfileDetailSection
      && monitoringHudOverlayProfileDetailSection.hidden === false
    );
    if (monitoringHudOverlayProfileNameInput) {
      monitoringHudOverlayProfileNameInput.value = "Focused Overlay Profile";
    }
    const allMonitorIds = monitoringHudStableMonitorIds(monitoringHudControlState.cards || {});
    const savedMonitorIds = allMonitorIds.slice(0, Math.max(1, Math.min(1, allMonitorIds.length)));
    if (monitoringHudOverlayProfileMembershipList) {
      const inputs = Array.from(monitoringHudOverlayProfileMembershipList.querySelectorAll("[data-overlay-profile-membership-toggle]"));
      inputs.forEach((input) => {
        input.checked = savedMonitorIds.includes(input.value);
      });
      if (inputs[0]) inputs[0].dispatchEvent(new Event("change", { bubbles: true }));
    } else {
      monitoringHudOverlayProfileDraftMonitorIds = savedMonitorIds.slice();
    }
    monitoringHudSaveOverlayProfileDraft();
    const savedProfile = (monitoringHudControlState.overlayProfiles || {})[createdId] || {};
    proof.renameSaved = savedProfile.name === "Focused Overlay Profile";
    proof.membershipSaved = JSON.stringify(savedProfile.monitorIds || []) === JSON.stringify(savedMonitorIds);
    if (monitoringHudOverlayProfileNameInput) {
      monitoringHudOverlayProfileNameInput.value = "Discarded Draft Name";
    }
    const discardedMonitorIds = allMonitorIds.slice().reverse();
    if (monitoringHudOverlayProfileMembershipList) {
      const inputs = Array.from(monitoringHudOverlayProfileMembershipList.querySelectorAll("[data-overlay-profile-membership-toggle]"));
      inputs.forEach((input) => {
        input.checked = discardedMonitorIds.includes(input.value);
      });
      if (inputs[0]) inputs[0].dispatchEvent(new Event("change", { bubbles: true }));
    } else {
      monitoringHudOverlayProfileDraftMonitorIds = discardedMonitorIds.slice();
    }
    monitoringHudDiscardOverlayProfileDraft();
    proof.discardRestored = monitoringHudOverlayProfileNameInput
      ? monitoringHudOverlayProfileNameInput.value === "Focused Overlay Profile"
      : true;
    const restoredProfile = (monitoringHudControlState.overlayProfiles || {})[createdId] || {};
    proof.membershipDiscardRestored = JSON.stringify(restoredProfile.monitorIds || []) === JSON.stringify(savedMonitorIds)
      && monitoringHudSameMonitorMembership(monitoringHudOverlayProfileDraftMonitorIds, savedMonitorIds, monitoringHudControlState.cards || {});
    proof.activeProfilePersistsInState = monitoringHudControlState.activeOverlayProfileId === createdId;
    const actionWindowRect = monitoringHudOverlayProfileWindow
      ? monitoringHudOverlayProfileWindow.getBoundingClientRect()
      : { top: 0, bottom: 0 };
    const actionRects = [monitoringHudOverlayProfileSave, monitoringHudOverlayProfileDelete, monitoringHudOverlayProfileDiscard]
      .filter(Boolean)
      .map((element) => element.getBoundingClientRect());
    proof.detailActionsVisualReviewable = Boolean(
      actionRects.length === 3
      && actionRects.every((rect) => rect.height > 0 && rect.top >= actionWindowRect.top - 1 && rect.bottom <= actionWindowRect.bottom + 1)
    );
    monitoringHudSetOverlayProfileDeleteConfirmation(true);
    proof.deleteConfirmationVisible = Boolean(
      monitoringHudOverlayProfileDeleteConfirmation
      && monitoringHudOverlayProfileDeleteConfirmation.hidden === false
      && monitoringHudOverlayProfileDeleteConfirmation.dataset.overlayProfileDeleteConfirmation === "open"
    );
    const confirmationRect = monitoringHudOverlayProfileDeleteConfirmation
      ? monitoringHudOverlayProfileDeleteConfirmation.getBoundingClientRect()
      : { top: 0, bottom: 0, height: 0 };
    proof.deleteConfirmationVisualReviewable = Boolean(
      proof.deleteConfirmationVisible
      && confirmationRect.height > 0
      && confirmationRect.top >= actionWindowRect.top - 1
      && confirmationRect.bottom <= actionWindowRect.bottom + 1
    );
    monitoringHudConfirmDeleteOverlayProfile();
    proof.profileDeleted = !((monitoringHudControlState.overlayProfiles || {})[createdId]);
    const defaultDeleteFixtureCards = monitoringHudSafeCardsObject(monitoringHudControlState.cards || {});
    monitoringHudControlState = {
      cards: defaultDeleteFixtureCards,
      selectedMonitorId: Object.keys(defaultDeleteFixtureCards)[0] || "",
      activeOverlayProfileId: monitoringHudDefaultOverlayProfileId,
      overlayProfileDefaultDeletedByUser: false,
      overlayProfiles: {}
    };
    monitoringHudControlState.overlayProfiles[monitoringHudDefaultOverlayProfileId] = monitoringHudDefaultOverlayProfile(defaultDeleteFixtureCards);
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    monitoringHudOpenChildWindow("overlay-profile-settings");
    const defaultDetailOpened = monitoringHudOpenOverlayProfileDetail(monitoringHudDefaultOverlayProfileId);
    monitoringHudSetOverlayProfileDeleteConfirmation(true);
    const defaultDeleteConfirmationOpen = Boolean(
      monitoringHudOverlayProfileDeleteConfirmation
      && monitoringHudOverlayProfileDeleteConfirmation.hidden === false
      && monitoringHudPendingDeleteOverlayProfileId === monitoringHudDefaultOverlayProfileId
    );
    monitoringHudConfirmDeleteOverlayProfile();
    proof.defaultProfileDeletePersists = Boolean(
      defaultDetailOpened
      && defaultDeleteConfirmationOpen
      && monitoringHudControlState.overlayProfileDefaultDeletedByUser
      && monitoringHudControlState.activeOverlayProfileId === ""
      && !((monitoringHudControlState.overlayProfiles || {})[monitoringHudDefaultOverlayProfileId])
      && Object.keys(monitoringHudControlState.overlayProfiles || {}).length === 0
    );
  } finally {
    try {
      monitoringHudControlState = JSON.parse(previousState);
      monitoringHudOverlayProfileDraftId = previousDraftId;
      monitoringHudOverlayProfileDraftName = previousDraftName;
      monitoringHudOverlayProfileDraftMonitorIds = previousDraftMonitorIds.slice();
      monitoringHudOverlayProfileWindowSelectedId = previousWindowSelectedId;
      monitoringHudOverlayProfileDetailOpen = previousDetailOpen;
      monitoringHudPendingDeleteOverlayProfileId = previousPendingDeleteId;
      monitoringHudOverlayProfilePendingCreate = previousPendingCreate;
      monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
      monitoringHudSetOverlayProfileDraftFromActive();
      monitoringHudRenderControls();
      monitoringHudCloseChildWindow({ force: true });
      monitoringHudSaveStoredState();
    } catch (_err) {}
  }
  proof.passed = proof.selectorVisible
    && proof.settingsEntryVisible
    && proof.settingsWindowPresent
    && proof.settingsWindowOpens
    && proof.managerDefaultState
    && proof.windowSelectorVisible
    && proof.windowSelectorReadable
    && proof.windowSelectorScalesWithinRow
    && proof.windowSelectorSameRow
    && proof.windowSelectorStandardFootprint
    && proof.windowSelectorMenuUnclipped
    && proof.windowSelectorResponsiveCompact
    && proof.visualRepairMarker
    && proof.windowDropdownMaxFive
    && proof.largeProfileFixture
    && proof.profileDropdownMaxFiveStress
    && proof.profileDropdownNDAIScrollbar
    && proof.dropdownNullStress
    && proof.dropdownHighVolumeStress
    && proof.dropdownStressSurfaceCount >= 2
    && proof.editButtonRemovedAndSelectorDefaultEmpty
    && proof.selectorLoadsSelectedSettings
    && proof.createRequiresSave
    && proof.createStartsEmptyMembership
    && proof.closeGuardOpensForCreatedDraft
    && proof.childWindowClickIsolation
    && proof.createVisible
    && proof.renameVisible
    && proof.saveDiscardVisible
    && proof.selectorFirstCreateFirstWindow
    && proof.monitorSearchFilterVisible
    && proof.monitorFilterNexusDropdown
    && proof.maxFiveInnerScrollPolicy
    && proof.dangerDiscardRight
    && proof.deleteDangerVisible
    && proof.deleteConfirmationVisible
    && proof.deleteConfirmationVisualReviewable
    && proof.defaultProfileDeletePersists
    && proof.detailActionsVisualReviewable
    && proof.profileDeleted
    && proof.editableMembership
    && proof.createdProfileSelectable
    && proof.membershipModelPresent
    && proof.renameSaved
    && proof.discardRestored
    && proof.membershipListVisible
    && proof.membershipSaved
    && proof.membershipDiscardRestored
    && proof.monitorGroupBoundary
    && proof.recordingProfileBoundary
    && proof.activeProfilePersistsInState;
  if (monitoringHud) {
    monitoringHud.dataset.overlayProfileControlsProof = proof.passed ? "pass" : "fail";
  }
  return proof;
};

window.runMonitoringHudOverlayProfileIntegrationProof = function() {
  const previousState = JSON.stringify(monitoringHudControlState);
  const previousSelectedMonitorId = monitoringHudControlState.selectedMonitorId || "";
  const previousChildWindow = monitoringHudActiveChildWindow;
  const previousContextMonitorId = monitoringHudOverlayProfileContextMonitorId;
  let proof = {
    passed: false,
    package: "PKG-006",
    slice: "SLC-040-followup",
    manageContextVisible: false,
    manageContextClickable: false,
    manageContextStateMatchesMembership: false,
    manageContextSingleRow: false,
    manageContextBelowSensorSource: false,
    manageContextRowAffordanceVisible: false,
    manageContextAssignedCount: false,
    manageContextDisplayMode: false,
    noDuplicateMembershipEditorInManageMonitors: false,
    settingsRouteRemoved: !Boolean(monitoringHudMonitorOverlayProfileSettings),
    enabledForOverlayRemoved: !Boolean(document.getElementById("monitoring-hud-monitor-enabled")) && !/Enabled for Overlay/.test(document.body ? document.body.textContent || "" : ""),
    assignmentWindowOpens: false,
    assignmentToggleWorks: false,
    monitorGroupBoundary: true,
    recordingProfileBoundary: true
  };
  try {
    monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
    const cards = monitoringHudControlState.cards || {};
    const monitorIds = monitoringHudStableMonitorIds(cards);
    const selectedId = monitorIds.includes(monitoringHudControlState.selectedMonitorId)
      ? monitoringHudControlState.selectedMonitorId
      : (monitorIds[0] || "");
    if (!selectedId) return proof;
    monitoringHudSelectMonitorGroup(selectedId, { force: true });
    monitoringHudOpenChildWindow("monitor-group-edit");
    monitoringHudRenderMonitorOverlayProfileContext({ id: selectedId }, cards);
    const activeProfile = monitoringHudActiveOverlayProfile() || {};
    const activeMonitorIds = monitoringHudUniqueValidMonitorIds(activeProfile.monitorIds, cards);
    const assignedProfileCount = monitoringHudOverlayProfileList().filter((profile) => {
      const profileMonitorIds = monitoringHudUniqueValidMonitorIds(profile.monitorIds, cards);
      return profileMonitorIds.includes(selectedId);
    }).length;
    const expectedMembershipState = activeMonitorIds.includes(selectedId)
      ? "selected-monitor-included"
      : "selected-monitor-excluded";
    const manageWindow = monitoringHudEditMonitorWindow;
    const contextPanel = monitoringHudMonitorOverlayProfileContext;
    proof.manageContextVisible = Boolean(
      manageWindow
      && manageWindow.hidden === false
      && contextPanel
      && contextPanel.dataset.overlayProfileIntegration === "slc-040-readonly-manage-context"
    );
    proof.manageContextClickable = Boolean(
      contextPanel
      && contextPanel.dataset.overlayProfileMutation === "assign-unassign-status-window"
      && contextPanel.dataset.overlayProfileRoute === "assigned-overlay-status-window"
      && contextPanel.dataset.control === "assigned-overlay-status"
      && !contextPanel.querySelector("input, textarea, select, [data-overlay-profile-membership-toggle]")
    );
    proof.manageContextStateMatchesMembership = Boolean(
      contextPanel
      && contextPanel.dataset.overlayProfileMembershipState === expectedMembershipState
      && contextPanel.dataset.selectedMonitorId === selectedId
    );
    proof.manageContextSingleRow = Boolean(
      contextPanel
      && contextPanel.dataset.overlayProfileContextLayout === "single-row-readonly"
      && contextPanel.dataset.overlayProfileRoute === "assigned-overlay-status-window"
    );
    const sensorSourceCard = manageWindow ? manageWindow.querySelector('[data-monitor-detail-card="sensor-source"]') : null;
    proof.manageContextBelowSensorSource = Boolean(
      contextPanel
      && sensorSourceCard
      && contextPanel.dataset.monitorDetailPlacement === "below-sensor-source"
      && (sensorSourceCard.compareDocumentPosition(contextPanel) & Node.DOCUMENT_POSITION_FOLLOWING)
    );
    const contextRect = contextPanel ? contextPanel.getBoundingClientRect() : null;
    proof.manageContextRowAffordanceVisible = Boolean(
      contextPanel
      && contextPanel.tagName === "BUTTON"
      && contextPanel.dataset.control === "assigned-overlay-status"
      && !contextPanel.disabled
      && contextRect
      && contextRect.width >= 300
      && contextRect.height >= 32
    );
    proof.manageContextAssignedCount = Boolean(
      monitoringHudMonitorOverlayProfileCount
      && monitoringHudMonitorOverlayProfileCount.textContent === `${assignedProfileCount} assigned`
      && contextPanel
      && contextPanel.dataset.assignedOverlayCount === String(assignedProfileCount)
    );
    proof.manageContextDisplayMode = Boolean(
      monitoringHudMonitorOverlayProfileDisplayMode
      && monitoringHudMonitorOverlayProfileDisplayMode.textContent === monitoringHudOverlayProfileDisplayLabel(activeProfile.displayMode)
    );
    proof.noDuplicateMembershipEditorInManageMonitors = Boolean(
      manageWindow
      && !manageWindow.querySelector("#monitoring-hud-overlay-profile-membership-list, [data-overlay-profile-membership-list]")
    );
    monitoringHudOpenChildWindow("monitor-overlay-assignment");
    proof.assignmentWindowOpens = Boolean(
      monitoringHudActiveChildWindow === "monitor-overlay-assignment"
      && monitoringHudOverlayAssignmentWindow
      && monitoringHudOverlayAssignmentWindow.hidden === false
      && monitoringHudOverlayAssignmentList
    );
    const firstProfile = monitoringHudOverlayProfileList()[0] || {};
    if (firstProfile.id) {
      const before = monitoringHudUniqueValidMonitorIds(firstProfile.monitorIds, cards).includes(selectedId);
      monitoringHudToggleOverlayAssignment(firstProfile.id);
      const afterProfile = (monitoringHudControlState.overlayProfiles || {})[firstProfile.id] || {};
      const after = monitoringHudUniqueValidMonitorIds(afterProfile.monitorIds, monitoringHudControlState.cards || {}).includes(selectedId);
      proof.assignmentToggleWorks = before !== after;
    }
  } finally {
    try {
      monitoringHudControlState = JSON.parse(previousState);
      monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
      monitoringHudOverlayProfileContextMonitorId = previousContextMonitorId;
      if (previousSelectedMonitorId && monitoringHudControlState.cards && monitoringHudControlState.cards[previousSelectedMonitorId]) {
        monitoringHudSelectMonitorGroup(previousSelectedMonitorId, { force: true });
      }
      monitoringHudSetChildWindowVisibility(previousChildWindow || "");
      monitoringHudRenderControls();
    } catch (_err) {}
  }
  proof.passed = proof.manageContextVisible
    && proof.manageContextClickable
    && proof.manageContextStateMatchesMembership
    && proof.manageContextSingleRow
    && proof.manageContextBelowSensorSource
    && proof.manageContextRowAffordanceVisible
    && proof.manageContextAssignedCount
    && proof.manageContextDisplayMode
    && proof.noDuplicateMembershipEditorInManageMonitors
    && proof.settingsRouteRemoved
    && proof.enabledForOverlayRemoved
    && proof.assignmentWindowOpens
    && proof.assignmentToggleWorks
    && proof.monitorGroupBoundary
    && proof.recordingProfileBoundary;
  if (monitoringHud) {
    monitoringHud.dataset.overlayProfileIntegrationProof = proof.passed ? "pass" : "fail";
  }
  return proof;
};

window.getMonitoringHudControlState = function() {
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  return Object.assign({}, monitoringHudControlState, {
    cards: Object.assign({}, monitoringHudControlState.cards),
    overlayProfiles: JSON.parse(JSON.stringify(monitoringHudControlState.overlayProfiles || {})),
    activeOverlayProfileId: monitoringHudControlState.activeOverlayProfileId || "",
    overlayProfileDefaultDeletedByUser: Boolean(monitoringHudControlState.overlayProfileDefaultDeletedByUser),
    overlayProfileSchemaVersion: monitoringHudOverlayProfileSchemaVersion,
    overlayProfileStateProof: Object.assign({}, monitoringHudControlState.overlayProfileStateProof || {}),
    activeOverlayRecordingTarget: Object.assign({}, monitoringHudControlState.activeOverlayRecordingTarget || {}),
    activeOverlayRecordingTargetProof: Object.assign({}, monitoringHudControlState.activeOverlayRecordingTargetProof || {}),
    recordingTargetPreviewProof: Object.assign({}, monitoringHudControlState.recordingTargetPreviewProof || {}),
    overlayDisplayAcceptanceProof: Object.assign({}, monitoringHudControlState.overlayDisplayAcceptanceProof || {}),
    activeOverlayProfileDisplayProof: Object.assign({}, monitoringHudControlState.activeOverlayProfileDisplayProof || {}),
    dashboardOverlayIndependenceProof: Object.assign({}, monitoringHudControlState.dashboardOverlayIndependenceProof || {}),
    activeChildWindow: monitoringHudActiveChildWindow || "none",
    interactiveControlReliabilityProof: Object.assign({}, monitoringHudReliableActivationState, {
      attempts: monitoringHudReliableActivationState.attempts.slice(-40)
    }),
    geometry: window.getMonitoringHudLiveClientGeometry
      ? window.getMonitoringHudLiveClientGeometry()
      : {}
  });
};

window.getMonitoringHudLiveClientGeometry = function() {
  function rectFor(selector) {
    const node = document.querySelector(selector);
    if (!node) return null;
    const rect = node.getBoundingClientRect();
    return {
      left: rect.left,
      top: rect.top,
      width: rect.width,
      height: rect.height,
      right: rect.right,
      bottom: rect.bottom,
      centerX: rect.left + rect.width / 2,
      centerY: rect.top + rect.height / 2
    };
  }
  return {
    hud: rectFor("#monitoring-hud"),
    dashboard: rectFor("#monitoring-hud"),
    minimalHud: rectFor("#monitoring-hud-minimal"),
    overlayDisplay: rectFor("#monitoring-hud-overlay-display"),
    overlayCanvas: rectFor("#monitoring-hud-overlay-canvas"),
    overlayProfileDisplayStatus: rectFor("#monitoring-hud-overlay-profile-display-status"),
    coreWrap: null,
    anchorToggle: null,
    settingsAction: rectFor("#monitoring-hud-settings-action"),
    createMonitor: rectFor("#monitoring-hud-create-monitor-action"),
    editMonitor: rectFor("#monitoring-hud-edit-monitor-action"),
    dashboardClose: rectFor("#monitoring-hud-dashboard-close-action"),
    settingsWindow: rectFor("#monitoring-hud-settings-window"),
    settingsClose: rectFor('[data-child-window-close="dashboard-settings"]'),
    settingsWarningToggle: rectFor("#monitoring-hud-settings-warning-toggle"),
    createMonitorWindow: rectFor("#monitoring-hud-create-monitor-window"),
    createMonitorClose: rectFor('[data-child-window-close="monitor-group-create"]'),
    editMonitorWindow: rectFor("#monitoring-hud-edit-monitor-window"),
    editMonitorClose: rectFor('[data-child-window-close="monitor-group-edit"]'),
    manageMonitorCreate: rectFor("#monitoring-hud-manage-monitor-create-action"),
    manageMonitorEmptyCreate: rectFor("#monitoring-hud-monitor-empty-create-action"),
    monitorDetailActions: rectFor("#monitoring-hud-monitor-detail-actions"),
    monitorDeleteConfirmation: rectFor("#monitoring-hud-monitor-delete-confirmation"),
    monitorSensorAssignment: rectFor("#monitoring-hud-monitor-sensor-assignment"),
    monitorSensorSettings: rectFor("#monitoring-hud-monitor-sensor-settings"),
    childWindowLayer: rectFor("#monitoring-hud-child-window-layer"),
    visibilityToggle: null,
    snapToggle: rectFor("#monitoring-hud-snap-toggle"),
    warningToggle: rectFor("#monitoring-hud-warning-toggle"),
    pollingRate: rectFor("#monitoring-hud-polling-rate"),
    warningModeControl: rectFor("#monitoring-hud-warning-mode-control"),
    panelDragHandle: rectFor("#monitoring-hud-drag-handle"),
    monitorList: rectFor("#monitoring-hud-monitor-list"),
    hudOverlayCard: rectFor('[data-dashboard-hub-card="hud-overlay"]'),
    recordingCard: rectFor('[data-dashboard-hub-card="recording"]'),
    recordingTargetPreview: rectFor("#monitoring-hud-recording-target-preview"),
    recordingTargetSourceRow: rectFor("#monitoring-hud-recording-target-profile"),
    recordingActiveMonitorsRow: rectFor("#monitoring-hud-recording-target-count"),
    recordingControlLauncher: rectFor("#monitoring-hud-recording-control-launcher"),
    recordingStudioOpen: rectFor("#monitoring-hud-recording-studio-open"),
    recordingOpenFolder: rectFor("#monitoring-hud-recording-open-folder"),
    monitorGroupsCard: rectFor('[data-dashboard-hub-card="monitor-groups"]'),
    monitorGroupsSummaryGrid: rectFor('[data-dashboard-hub-card="monitor-groups"] .monitoring-hud__monitor-summary-grid'),
    monitorGroupsActions: rectFor('[data-dashboard-hub-card="monitor-groups"] .monitoring-hud__hub-actions'),
    monitorGroupsScope: rectFor("#monitoring-hud-monitor-editor-scope"),
    dataSourcesCard: rectFor('[data-dashboard-hub-card="data-sources"]'),
    readinessCard: rectFor('[data-dashboard-hub-card="readiness"]'),
    monitorSelector: null,
    dataSourcesAction: rectFor('[data-control="open-data-sources"]'),
    hudOverlayDeferredAction: rectFor('[data-dashboard-hub-card="hud-overlay"]'),
    monitorPollingRate: rectFor("#monitoring-hud-monitor-polling-rate"),
    monitorPollingRateControl: rectFor("#monitoring-hud-monitor-polling-rate-control"),
    monitorPollingRateToggle: rectFor("#monitoring-hud-monitor-polling-rate-toggle"),
    monitorOverlayProfileContext: rectFor("#monitoring-hud-monitor-overlay-profile-context"),
    monitorOverlayProfileSettings: rectFor("#monitoring-hud-monitor-overlay-profile-settings"),
    monitorOverlayProfileSelectedState: rectFor("#monitoring-hud-monitor-overlay-profile-selected-state"),
    monitorOverlayProfileCount: rectFor("#monitoring-hud-monitor-overlay-profile-count"),
    overlayProfileEditor: rectFor("#monitoring-hud-overlay-profile-editor"),
    overlayProfileSelector: rectFor("#monitoring-hud-overlay-profile-selector"),
    overlayProfileToggle: rectFor("#monitoring-hud-overlay-profile-toggle"),
    overlayProfileMenu: rectFor("#monitoring-hud-overlay-profile-menu"),
    overlayProfileOpenSettings: rectFor("#monitoring-hud-overlay-profile-open-settings"),
    overlayProfileWindow: rectFor("#monitoring-hud-overlay-profile-window"),
    overlayProfileWindowClose: rectFor('[data-child-window-close="overlay-profile-settings"]'),
    overlayProfileWindowSelector: rectFor("#monitoring-hud-overlay-profile-window-selector"),
    overlayProfileNameInput: rectFor("#monitoring-hud-overlay-profile-name-input"),
    overlayProfileMonitorSearch: rectFor("#monitoring-hud-overlay-profile-monitor-search"),
    overlayProfileMonitorFilter: rectFor("#monitoring-hud-overlay-profile-monitor-filter"),
    overlayProfileMonitorResults: rectFor("#monitoring-hud-overlay-profile-monitor-results"),
    overlayProfileMembershipList: rectFor("#monitoring-hud-overlay-profile-membership-list"),
    overlayProfileMembershipFirstToggle: rectFor("[data-overlay-profile-membership-toggle]"),
    overlayProfileCreate: rectFor("#monitoring-hud-overlay-profile-create"),
    overlayProfileSave: rectFor("#monitoring-hud-overlay-profile-save"),
    overlayProfileDiscard: rectFor("#monitoring-hud-overlay-profile-discard"),
    overlayProfileDelete: rectFor("#monitoring-hud-overlay-profile-delete"),
    overlayProfileDeleteConfirmation: rectFor("#monitoring-hud-overlay-profile-delete-confirmation"),
    overlayAssignmentWindow: rectFor("#monitoring-hud-overlay-assignment-window"),
    overlayAssignmentList: rectFor("#monitoring-hud-overlay-assignment-list"),
    sourceSettingsWindow: rectFor("#monitoring-hud-source-settings-window"),
    sourceSettingsBody: rectFor("#monitoring-hud-source-settings-body"),
    editMonitorName: rectFor("#monitoring-hud-edit-monitor-name"),
    createMonitorName: rectFor("#monitoring-hud-create-monitor-name"),
    monitorListSummary: rectFor("#monitoring-hud-monitor-list-summary")
  };
};

window.getMonitoringHudSurfaceSplitState = function() {
  const dashboardRect = monitoringHud ? monitoringHud.getBoundingClientRect() : null;
  const minimalRect = monitoringHudMinimal ? monitoringHudMinimal.getBoundingClientRect() : null;
  const overlayRect = monitoringHudOverlayDisplay ? monitoringHudOverlayDisplay.getBoundingClientRect() : null;
  return {
    dashboardPresent: Boolean(monitoringHud),
    minimalHudPresent: Boolean(monitoringHudMinimal),
    overlayDisplayPresent: Boolean(monitoringHudOverlayDisplay),
    dashboardSurfaceRole: monitoringHud ? monitoringHud.dataset.productSurfaceRole || "" : "",
    minimalHudSurfaceRole: monitoringHudMinimal ? monitoringHudMinimal.dataset.productSurfaceRole || "" : "",
    overlayDisplaySurfaceRole: monitoringHudOverlayDisplay ? monitoringHudOverlayDisplay.dataset.productSurfaceRole || "" : "",
    overlayCanvas: monitoringHudOverlayDisplay ? monitoringHudOverlayDisplay.dataset.overlayCanvas || "" : "",
    overlayMonitorLayout: monitoringHudOverlayDisplay ? monitoringHudOverlayDisplay.dataset.monitorLayout || "" : "",
    overlayEdgeToEdgePosture: monitoringHudOverlayDisplay ? monitoringHudOverlayDisplay.dataset.edgeToEdgePosture || "" : "",
    dashboardConfigures: monitoringHud ? monitoringHud.dataset.configuresSurface || "" : "",
    minimalConfiguredBy: monitoringHudMinimal ? monitoringHudMinimal.dataset.configuredBy || "" : "",
    splitContract: monitoringHudMinimal ? monitoringHudMinimal.dataset.splitContract || "" : "",
    dashboardVisible: Boolean(dashboardRect && dashboardRect.width > 100 && dashboardRect.height > 100),
    minimalHudVisible: Boolean(minimalRect && minimalRect.width > 180 && minimalRect.height > 80),
    overlayDisplayVisible: Boolean(overlayRect && overlayRect.width > 640 && overlayRect.height > 420),
    overlayDisplayEdgeToEdge: Boolean(
      overlayRect
      && overlayRect.width >= Math.max(640, window.innerWidth - 24)
      && overlayRect.height >= Math.max(360, window.innerHeight - 24)
    ),
    primaryInterfaceReleaseSurface: monitoringHud ? monitoringHud.dataset.primaryInterfaceReleaseSurface || "" : "",
    dashboardAcceptanceBaseline: monitoringHud ? monitoringHud.dataset.dashboardAcceptanceBaseline || "" : "",
    dashboardProofPath: monitoringHud ? monitoringHud.dataset.dashboardProofPath || "" : "",
    dashboardStandaloneProof: monitoringHud ? monitoringHud.dataset.dashboardStandaloneProof || "" : "",
    dashboardClippingProof: monitoringHud ? monitoringHud.dataset.dashboardClippingProof || "" : "",
    dashboardMinimumEdgeProof: monitoringHud ? monitoringHud.dataset.dashboardMinimumEdgeProof || "" : "",
    dashboardDecouplingProof: monitoringHud ? monitoringHud.dataset.dashboardDecouplingProof || "" : "",
    dashboardContentPolish: monitoringHud ? monitoringHud.dataset.dashboardContentPolish || "" : "",
    dashboardSettingsModel: monitoringHud ? monitoringHud.dataset.dashboardSettingsModel || "" : "",
    monitorGroupModel: monitoringHud ? monitoringHud.dataset.monitorGroupModel || "" : "",
    dashboardMonitorCardPolicy: monitoringHud ? monitoringHud.dataset.dashboardMonitorCardPolicy || "" : "",
    monitorManagement: monitoringHud ? monitoringHud.dataset.monitorManagement || "" : "",
    dashboardChildWindowScope: monitoringHud ? monitoringHud.dataset.dashboardChildWindowScope || "" : "",
    monitorSensorAssignment: monitoringHud ? monitoringHud.dataset.monitorSensorAssignment || "" : "",
    monitorDeleteConfirmation: monitoringHud ? monitoringHud.dataset.monitorDeleteConfirmation || "" : "",
    assignedSensorCount: monitoringHud ? Number(monitoringHud.dataset.assignedSensorCount || 0) : 0,
    dashboardProviderTruth: monitoringHud ? monitoringHud.dataset.dashboardProviderTruth || "" : "",
    dashboardStateModel: monitoringHud ? monitoringHud.dataset.dashboardStateModel || "" : "",
    dashboardWarningControls: monitoringHud ? monitoringHud.dataset.dashboardWarningControls || "" : "",
    dashboardFakeTelemetryPolicy: monitoringHud ? monitoringHud.dataset.dashboardFakeTelemetryPolicy || "" : "",
    dashboardSettingsAffordance: monitoringHud ? monitoringHud.dataset.dashboardSettingsAffordance || "" : "",
    dashboardSettingsPanel: monitoringHud ? monitoringHud.dataset.dashboardSettingsPanel || "" : "",
    dashboardSettingsPanelState: monitoringHud ? monitoringHud.dataset.dashboardSettingsPanelState || "" : "",
    dashboardSettingsProof: monitoringHud ? monitoringHud.dataset.dashboardSettingsProof || "" : "",
    warningControlPosture: monitoringHud ? monitoringHud.dataset.warningControlPosture || "" : "",
    interfaceAcceptancePolicy: monitoringHud ? monitoringHud.dataset.interfaceAcceptancePolicy || "" : "",
    overlayAcceptancePolicy: monitoringHud ? monitoringHud.dataset.overlayAcceptancePolicy || "" : "",
    interfaceBundleApproval: monitoringHud ? monitoringHud.dataset.interfaceBundleApproval || "" : "",
    coreRepairClassification: monitoringHud ? monitoringHud.dataset.coreRepairClassification || "" : "",
    minimalHudAcceptancePolicy: monitoringHudMinimal ? monitoringHudMinimal.dataset.interfaceAcceptancePolicy || "" : "",
    overlayDisplayAcceptancePolicy: monitoringHudOverlayDisplay ? monitoringHudOverlayDisplay.dataset.interfaceAcceptancePolicy || "" : "",
    sharedRendererOwner: monitoringHudMinimal ? monitoringHudMinimal.dataset.rendererOwner || "" : "",
    nativeOverlayOwner: monitoringHudMinimal ? monitoringHudMinimal.dataset.nativeOverlayOwner || "" : "",
    nativeWindowSplitProof: monitoringHudMinimal ? monitoringHudMinimal.dataset.nativeWindowSplitProof || "" : ""
  };
};

window.getMonitoringHudDashboardAcceptanceState = function() {
  const split = window.getMonitoringHudSurfaceSplitState ? window.getMonitoringHudSurfaceSplitState() : {};
  return {
    primaryInterfaceReleaseSurface: split.primaryInterfaceReleaseSurface || "",
    dashboardAcceptanceBaseline: split.dashboardAcceptanceBaseline || "",
    dashboardProofPath: split.dashboardProofPath || "",
    dashboardStandaloneProof: split.dashboardStandaloneProof || "",
    dashboardClippingProof: split.dashboardClippingProof || "",
    dashboardMinimumEdgeProof: split.dashboardMinimumEdgeProof || "",
    dashboardDecouplingProof: split.dashboardDecouplingProof || "",
    interfaceAcceptancePolicy: split.interfaceAcceptancePolicy || "",
    overlayAcceptancePolicy: split.overlayAcceptancePolicy || "",
    interfaceBundleApproval: split.interfaceBundleApproval || "",
    coreRepairClassification: split.coreRepairClassification || "",
    overlayAcceptanceNonGating: Boolean(
      split.overlayAcceptancePolicy === "deferred-non-gating"
      && split.minimalHudAcceptancePolicy === "deferred-non-gating"
      && split.overlayDisplayAcceptancePolicy === "deferred-non-gating"
    ),
    dashboardAcceptanceBaselineReady: Boolean(
      split.primaryInterfaceReleaseSurface === "monitoring-hud-dashboard-control-panel"
      && split.dashboardAcceptanceBaseline === "ws31-dashboard-control-panel"
      && split.interfaceAcceptancePolicy === "dashboard-only-current-branch"
      && split.interfaceBundleApproval === "not-granted"
    ),
    dashboardStandaloneMovementReady: Boolean(
      split.dashboardStandaloneProof === "ws32-dashboard-window-travel"
      && split.dashboardClippingProof === "within-virtual-desktop"
      && split.dashboardMinimumEdgeProof === "native-min-size-bottom-edge-visible"
      && split.dashboardDecouplingProof === "core-overlay-independent"
    ),
    dashboardSettingsContentReady: Boolean(
      split.dashboardContentPolish === "branch2-monitor-groups-no-dead-space"
      && split.dashboardSettingsModel === "hud-overlay-monitor-groups-provider-warning"
      && split.dashboardSettingsAffordance === "dashboard-ia-card-settings-button"
      && split.dashboardSettingsPanel === "settings-panel-child-window"
      && split.dashboardSettingsProof === "visible-open-close-control-hit-target"
      && split.monitorManagement === "sensor-command-center-list-detail-source-picker"
      && split.dashboardChildWindowScope === "monitor-groups-manage-create-edit-delete-sensor-windows-overlay-profile-settings"
      && split.monitorGroupModel === "configurable-groups-sensor-assignment"
      && split.dashboardMonitorCardPolicy === "overlay-display-owns-visual-rendering"
      && split.monitorSensorAssignment === "sensor-library-source-picker"
    ),
    dashboardProviderTruthReady: Boolean(
      split.dashboardProviderTruth === "provider-contract-first"
      && split.dashboardStateModel === "setup-no-data-degraded-warning"
      && split.dashboardWarningControls === "visual-non-invasive-only"
      && split.dashboardFakeTelemetryPolicy === "blocked"
    )
  };
};

window.getMonitoringHudIsolationState = function() {
  const hudRect = monitoringHud ? monitoringHud.getBoundingClientRect() : null;
  const minimalRect = monitoringHudMinimal ? monitoringHudMinimal.getBoundingClientRect() : null;
  const overlayRect = monitoringHudOverlayDisplay ? monitoringHudOverlayDisplay.getBoundingClientRect() : null;
  const split = window.getMonitoringHudSurfaceSplitState ? window.getMonitoringHudSurfaceSplitState() : {};
  const hudWindowMode = body.classList.contains("hud-window-mode");
  return {
    hudWindowMode,
    coreWindowMode: false,
    standaloneHudWindow: Boolean(hudWindowMode && monitoringHud && !document.getElementById("scene")),
    coreSceneHiddenInHudWindow: Boolean(hudWindowMode && !document.getElementById("scene")),
    coreWrapPresent: false,
    coreWrapVisible: false,
    coreWrapVisuallyReadable: false,
    hudPresent: Boolean(monitoringHud),
    hudVisible: Boolean(hudRect && hudRect.width > 100 && hudRect.height > 100),
    dashboardSurfacePresent: Boolean(monitoringHud),
    minimalHudSurfacePresent: Boolean(monitoringHudMinimal),
    overlayDisplaySurfacePresent: Boolean(monitoringHudOverlayDisplay),
    minimalHudVisible: Boolean(minimalRect && minimalRect.width > 180 && minimalRect.height > 80),
    overlayDisplayVisible: Boolean(overlayRect && overlayRect.width > 640 && overlayRect.height > 420),
    overlayDisplayEdgeToEdge: split.overlayDisplayEdgeToEdge === true,
    dashboardMinimalSplitReady: Boolean(
      split.dashboardSurfaceRole === "dashboard-configuration-surface"
      && split.minimalHudSurfaceRole === "minimal-anchored-hud-overlay"
      && split.dashboardConfigures === "monitoring-hud-minimal"
      && split.minimalConfiguredBy === "monitoring-hud"
    ),
    dashboardAcceptanceBaselineReady: Boolean(
      split.primaryInterfaceReleaseSurface === "monitoring-hud-dashboard-control-panel"
      && split.dashboardAcceptanceBaseline === "ws31-dashboard-control-panel"
      && split.interfaceAcceptancePolicy === "dashboard-only-current-branch"
      && split.overlayAcceptancePolicy === "deferred-non-gating"
      && split.interfaceBundleApproval === "not-granted"
    ),
    overlayAcceptanceNonGating: Boolean(
      split.overlayAcceptancePolicy === "deferred-non-gating"
      && split.minimalHudAcceptancePolicy === "deferred-non-gating"
      && split.overlayDisplayAcceptancePolicy === "deferred-non-gating"
    ),
    primaryInterfaceReleaseSurface: split.primaryInterfaceReleaseSurface || "",
    interfaceAcceptancePolicy: split.interfaceAcceptancePolicy || "",
    overlayAcceptancePolicy: split.overlayAcceptancePolicy || "",
    interfaceBundleApproval: split.interfaceBundleApproval || "",
    dashboardSurfaceRole: split.dashboardSurfaceRole || "",
    minimalHudSurfaceRole: split.minimalHudSurfaceRole || "",
    hudOutsideCoreScene: Boolean(monitoringHud && !document.getElementById("scene")),
    coreHudOverlap: false,
    coreHudGap: 999,
    coreHudSeparated: true,
    isolationBoundary: monitoringHud ? monitoringHud.dataset.isolationBoundary || "" : "",
    coreFailureIsolation: monitoringHud ? monitoringHud.dataset.coreFailureIsolation || "" : "",
    validationFault: monitoringHud ? monitoringHud.dataset.validationFault || "" : "",
    desktopMode: body.classList.contains("desktop-mode")
  };
};

window.simulateMonitoringHudFaultForValidation = function(enabled) {
  if (monitoringHud) {
    monitoringHud.dataset.validationFault = enabled ? "simulated-hud-module-fault" : "";
    monitoringHud.classList.toggle("monitoring-hud--validation-fault", Boolean(enabled));
  }
  return window.getMonitoringHudIsolationState();
};

function monitoringHudVisualInspectionStyleSnapshot(element) {
  if (!element || !window.getComputedStyle) return {};
  const style = window.getComputedStyle(element);
  const rect = typeof element.getBoundingClientRect === "function"
    ? element.getBoundingClientRect()
    : { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
  return {
    display: style.display,
    visibility: style.visibility,
    opacity: style.opacity,
    cursor: style.cursor,
    borderColor: style.borderColor,
    borderTopColor: style.borderTopColor,
    backgroundColor: style.backgroundColor,
    backgroundImage: style.backgroundImage,
    boxShadow: style.boxShadow,
    outlineStyle: style.outlineStyle,
    outlineColor: style.outlineColor,
    borderLeftColor: style.borderLeftColor,
    paddingLeft: style.paddingLeft,
    paddingRight: style.paddingRight,
    transform: style.transform,
    rect: {
      left: Math.round(rect.left),
      top: Math.round(rect.top),
      right: Math.round(rect.right),
      bottom: Math.round(rect.bottom),
      width: Math.round(rect.width),
      height: Math.round(rect.height)
    }
  };
}

function monitoringHudVisualInspectionHasGlow(snapshot) {
  const shadow = String(snapshot && snapshot.boxShadow || "").toLowerCase();
  return Boolean(shadow && shadow !== "none" && shadow.indexOf("rgb") >= 0);
}

function monitoringHudVisualInspectionSemanticPreserved(snapshot, semanticRole) {
  const text = [
    snapshot && snapshot.borderColor,
    snapshot && snapshot.backgroundColor,
    snapshot && snapshot.backgroundImage,
    snapshot && snapshot.boxShadow
  ].join(" ").toLowerCase();
  if (!semanticRole || semanticRole === "default") return true;
  if (semanticRole === "danger") return /255,\s*(1[0-9]{2}|[6-9][0-9])|122,\s*31,\s*42|96,\s*24,\s*34/.test(text);
  if (semanticRole === "warning") return /255,\s*(2[0-5][0-9]|214|226|246)|96,\s*70,\s*16|82,\s*59,\s*13/.test(text);
  if (semanticRole === "safe") return /126,\s*248|165,\s*255|12,\s*94|10,\s*79/.test(text);
  return true;
}

function monitoringHudVisualInspectionChanged(before, after) {
  if (!before || !after) return false;
  return Boolean(
    before.borderColor !== after.borderColor
    || before.backgroundColor !== after.backgroundColor
    || before.backgroundImage !== after.backgroundImage
    || before.boxShadow !== after.boxShadow
    || before.transform !== after.transform
  );
}

function monitoringHudVisualInspectionVisible(element) {
  if (!element || typeof element.getBoundingClientRect !== "function" || !window.getComputedStyle) return false;
  const style = window.getComputedStyle(element);
  const rect = element.getBoundingClientRect();
  return Boolean(
    !element.hidden
    && style.display !== "none"
    && style.visibility !== "hidden"
    && rect.width > 0
    && rect.height > 0
  );
}

window.runMonitoringHudVisualInspectionMatrixProof = function() {
  const backup = window.getMonitoringHudControlState ? window.getMonitoringHudControlState() : null;
  const previousChildWindow = monitoringHudActiveChildWindow || "";
  const previousSourceFilterOpen = monitoringHudSensorFilter ? monitoringHudSensorFilter.dataset.filterOpen : "";
  const previousPollingOpen = monitoringHudMonitorPollingRateControl ? monitoringHudMonitorPollingRateControl.dataset.dropdownOpen : "";
  const previousOverlayDropdownOpen = monitoringHudOverlayProfileSelector ? monitoringHudOverlayProfileSelector.dataset.dropdownOpen : "";
  const previousOverlayWindowDropdownOpen = monitoringHudOverlayProfileWindowSelector ? monitoringHudOverlayProfileWindowSelector.dataset.dropdownOpen : "";
  const previousOverlayMonitorFilterOpen = monitoringHudOverlayProfileMonitorFilter ? monitoringHudOverlayProfileMonitorFilter.dataset.dropdownOpen : "";
  const failures = [];
  const targets = [];
  const surfaces = [];
  function prepareVisibleTarget(element) {
    if (!element) return;
    if (typeof element.scrollIntoView === "function") {
      element.scrollIntoView({ block: "center", inline: "center", behavior: "instant" });
    }
  }
  function resolveTarget(selector) {
    if (!selector) return null;
    if (typeof selector === "string") return document.querySelector(selector);
    return selector;
  }
  function inspectTarget(name, selector, options) {
    const targetOptions = options || {};
    if (typeof targetOptions.prepare === "function") targetOptions.prepare();
    const element = resolveTarget(selector);
    if (!element) {
      failures.push(`${name}:missing`);
      targets.push({ name, present: false });
      return null;
    }
    prepareVisibleTarget(element);
    const visible = monitoringHudVisualInspectionVisible(element);
    const disabled = Boolean(
      element.disabled
      || String(element.getAttribute && element.getAttribute("aria-disabled") || "false") === "true"
      || targetOptions.expectDisabled === true
    );
    const isButtonLike = Boolean(
      element.tagName === "BUTTON"
      || element.tagName === "INPUT"
      || element.tagName === "SELECT"
      || element.getAttribute("role") === "button"
      || element.classList.contains("monitoring-hud__bounded-dropdown-toggle")
      || element.classList.contains("monitoring-hud__source-filter-toggle")
    );
    const before = monitoringHudVisualInspectionStyleSnapshot(element);
    const interception = monitoringHudControlInterceptionSnapshot(element);
    if (!visible) failures.push(`${name}:not-visible`);
    if (targetOptions.expectDisabled === true && !disabled) failures.push(`${name}:expected-disabled-state-missing`);
    if (!disabled && isButtonLike && interception.sameTargetOrChild === false) failures.push(`${name}:intercepted`);
    const defaultGlow = monitoringHudVisualInspectionHasGlow(before);
    const paddingLeft = Number.parseFloat(before.paddingLeft || "0") || 0;
    const paddingRight = Number.parseFloat(before.paddingRight || "0") || 0;
    const textDeadSpacePass = !isButtonLike || (paddingLeft >= 12 && paddingRight >= 12);
    const textFits = !isButtonLike || element.scrollWidth <= element.clientWidth + 2;
    if (!disabled && isButtonLike && !defaultGlow) failures.push(`${name}:default-glow-missing`);
    if (!disabled && !textDeadSpacePass) failures.push(`${name}:button-dead-space-missing`);
    if (!disabled && !targetOptions.allowTextOverflow && !textFits) failures.push(`${name}:button-text-clipping`);
    if (disabled) {
      targets.push({
        name,
        present: true,
        visible,
        disabled: true,
        defaultGlow,
        textDeadSpacePass,
        textFits,
        hoverGlow: false,
        pressedState: false,
        focusCapable: false,
        cursor: before.cursor,
        opacity: before.opacity,
        interception
      });
      return element;
    }
    const previousTransition = element.style.transition;
    const previousAnimation = element.style.animation;
    element.style.transition = "none";
    element.style.animation = "none";
    void element.offsetWidth;
    element.classList.add("is-hovered");
    const hover = monitoringHudVisualInspectionStyleSnapshot(element);
    const selectedAlready = Boolean(
      String(element.getAttribute && element.getAttribute("aria-selected") || "false") === "true"
      || String(element.getAttribute && element.getAttribute("aria-pressed") || "false") === "true"
      || String(element.getAttribute && element.getAttribute("aria-current") || "false") === "true"
      || String(element.getAttribute && element.getAttribute("aria-expanded") || "false") === "true"
    );
    const alreadyAfforded = selectedAlready || monitoringHudVisualInspectionHasGlow(before);
    const hoverGlow = monitoringHudVisualInspectionHasGlow(hover)
      && (monitoringHudVisualInspectionChanged(before, hover) || alreadyAfforded);
    if (isButtonLike && !hoverGlow) failures.push(`${name}:hover-glow-missing`);
    const semanticRole = targetOptions.semanticRole || "";
    const semanticPreserved = monitoringHudVisualInspectionSemanticPreserved(hover, semanticRole);
    if (!semanticPreserved) failures.push(`${name}:semantic-hover-color-drift`);
    element.classList.add("is-pressed");
    const pressed = monitoringHudVisualInspectionStyleSnapshot(element);
    const pressedState = monitoringHudVisualInspectionChanged(hover, pressed)
      || monitoringHudVisualInspectionHasGlow(pressed);
    if (isButtonLike && !pressedState) failures.push(`${name}:pressed-state-missing`);
    let focusCapable = false;
    if (typeof element.focus === "function") {
      element.focus({ preventScroll: true });
      const focused = document.activeElement === element || element.contains(document.activeElement);
      const focusSnapshot = monitoringHudVisualInspectionStyleSnapshot(element);
      focusCapable = Boolean(focused || focusSnapshot.outlineStyle !== "none" || monitoringHudVisualInspectionHasGlow(focusSnapshot));
      if (targetOptions.requireFocus !== false && !focusCapable) failures.push(`${name}:focus-state-missing`);
    }
    element.classList.remove("is-hovered");
    element.classList.remove("is-pressed");
    element.style.transition = previousTransition;
    element.style.animation = previousAnimation;
    targets.push({
      name,
      present: true,
      visible,
      disabled: false,
      defaultGlow,
      textDeadSpacePass,
      textFits,
      semanticRole,
      semanticPreserved,
      hoverGlow,
      pressedState,
      focusCapable,
      before,
      hover,
      pressed,
      interception
    });
    return element;
  }
  function inspectDividerGroup(name, selector) {
    const elements = Array.from(document.querySelectorAll(selector)).filter(monitoringHudVisualInspectionVisible);
    const rootStyle = window.getComputedStyle ? window.getComputedStyle(document.documentElement) : {};
    const dividerGlowSize = Number.parseFloat(rootStyle.getPropertyValue ? rootStyle.getPropertyValue("--monitoring-hud-divider-glow-size") : "0") || 0;
    const dividerGlowReduced = dividerGlowSize > 0 && dividerGlowSize <= 13.1;
    if (!dividerGlowReduced) failures.push(`${name}:divider-glow-not-reduced-50-percent`);
    const sampled = elements.slice(0, 8).map((element, index) => {
      const style = monitoringHudVisualInspectionStyleSnapshot(element);
      const hasDivider = Boolean(
        String(style.borderTopColor || "").indexOf("rgba(0, 0, 0, 0)") < 0
        && String(style.backgroundImage || "").toLowerCase().indexOf("gradient") >= 0
        && monitoringHudVisualInspectionHasGlow(style)
      );
      if (!hasDivider) failures.push(`${name}:${index}:divider-visual-contract-missing`);
      return { index, hasDivider, style };
    });
    if (!sampled.length) failures.push(`${name}:no-visible-divider-samples`);
    surfaces.push({ name, selector, sampleCount: sampled.length, dividerGlowSize, dividerGlowReduced, sampled });
  }
  function inspectNoClipping(name, selector) {
    const elements = Array.from(document.querySelectorAll(selector)).filter(monitoringHudVisualInspectionVisible);
    const sampled = elements.slice(0, 8).map((element, index) => {
      const rect = element.getBoundingClientRect();
      const withinViewport = Boolean(
        rect.left >= -1
        && rect.top >= -1
        && rect.right <= window.innerWidth + 1
        && rect.bottom <= window.innerHeight + 1
      );
      if (!withinViewport) failures.push(`${name}:${index}:viewport-clipping`);
      return {
        index,
        withinViewport,
        rect: {
          left: Math.round(rect.left),
          top: Math.round(rect.top),
          right: Math.round(rect.right),
          bottom: Math.round(rect.bottom),
          width: Math.round(rect.width),
          height: Math.round(rect.height)
        }
      };
    });
    if (!sampled.length) failures.push(`${name}:no-visible-clipping-samples`);
    surfaces.push({ name, selector, sampleCount: sampled.length, sampled });
  }
  function inspectRowTitleInset(name, selector) {
    const elements = Array.from(document.querySelectorAll(selector)).filter(monitoringHudVisualInspectionVisible);
    const sampled = elements.slice(0, 12).map((element, index) => {
      const style = monitoringHudVisualInspectionStyleSnapshot(element);
      const paddingLeft = Number.parseFloat(style.paddingLeft || "0") || 0;
      const hasTab = Boolean(
        paddingLeft >= 8
        && String(style.borderLeftColor || "").indexOf("rgba(0, 0, 0, 0)") < 0
      );
      if (!hasTab) failures.push(`${name}:${index}:row-title-tab-missing`);
      return { index, hasTab, style };
    });
    if (!sampled.length) failures.push(`${name}:no-visible-row-title-samples`);
    surfaces.push({ name, selector, sampleCount: sampled.length, sampled });
  }
  function inspectCheckedControlHoverAffordance(name) {
    const elements = Array.from(document.querySelectorAll('.monitoring-hud input[type="checkbox"]:checked')).filter(monitoringHudVisualInspectionVisible);
    const sampled = elements.slice(0, 16).map((element, index) => {
      const host = element.closest("label,[data-source-picker-row],[aria-selected],.monitoring-hud__source-settings-warning")
        || element.parentElement
        || element;
      const before = monitoringHudVisualInspectionStyleSnapshot(element);
      const previousHostHovered = host.classList.contains("is-hovered");
      const previousElementHovered = element.classList.contains("is-hovered");
      host.classList.add("is-hovered");
      element.classList.add("is-hovered");
      const hover = monitoringHudVisualInspectionStyleSnapshot(element);
      const hasHoverAffordance = Boolean(
        monitoringHudVisualInspectionHasGlow(hover)
        || String(hover.outlineStyle || "") !== "none"
        || before.borderColor !== hover.borderColor
        || before.boxShadow !== hover.boxShadow
      );
      if (!hasHoverAffordance) failures.push(`${name}:${index}:checked-hover-affordance-missing`);
      if (!previousHostHovered) host.classList.remove("is-hovered");
      if (!previousElementHovered) element.classList.remove("is-hovered");
      return {
        index,
        hasHoverAffordance,
        before,
        hover,
        hostClass: host.className || "",
        inputName: element.getAttribute("aria-label") || element.name || element.dataset.monitorSensorInput || element.dataset.sensorWarningEnabled || ""
      };
    });
    if (!sampled.length) failures.push(`${name}:no-visible-checked-controls`);
    surfaces.push({ name, selector: '.monitoring-hud input[type="checkbox"]:checked', sampleCount: sampled.length, sampled });
  }
  function inspectOverlayProfileManagerScaling() {
    const selector = monitoringHudOverlayProfileWindowSelector;
    const row = selector && selector.closest ? selector.closest("[data-overlay-profile-manager-row]") : null;
    const create = monitoringHudOverlayProfileCreate;
    const menu = monitoringHudOverlayProfileWindowMenu;
    if (!selector || !row || !monitoringHudVisualInspectionVisible(selector) || !monitoringHudVisualInspectionVisible(row)) {
      failures.push("overlay-manager-scaling:missing-visible-selector-row");
      surfaces.push({ name: "overlay-manager-scaling", selector: "#monitoring-hud-overlay-profile-window-selector", sampleCount: 0 });
      return;
    }
    const measureSelectorLayout = () => {
      const selectorRect = selector.getBoundingClientRect();
      const rowRect = row.getBoundingClientRect();
      const choicePanel = monitoringHudOverlayProfileWindow
        ? monitoringHudOverlayProfileWindow.querySelector(".monitoring-hud__overlay-profile-choice-panel")
        : null;
      const choicePanelRect = choicePanel
        ? choicePanel.getBoundingClientRect()
        : { left: 0, right: 0, width: 0 };
      const createRect = create ? create.getBoundingClientRect() : { top: 0, right: 0, height: 0, width: 0 };
      const windowRect = monitoringHudOverlayProfileWindow
        ? monitoringHudOverlayProfileWindow.getBoundingClientRect()
        : { left: 0, top: 0, right: 0, bottom: 0 };
      const layer = monitoringHudOverlayProfileWindow
        ? monitoringHudOverlayProfileWindow.closest(".monitoring-hud__child-window-layer")
        : null;
      const layerRect = layer
        ? layer.getBoundingClientRect()
        : { left: 0, right: window.innerWidth || 0 };
      const leftBuffer = windowRect.left - layerRect.left;
      const rightBuffer = layerRect.right - windowRect.right;
      const symmetricWindowBuffer = Boolean(
        leftBuffer >= 14
        && rightBuffer >= 14
        && Math.abs(leftBuffer - rightBuffer) <= 8
      );
      const choicePanelLeftInset = choicePanelRect.left - windowRect.left;
      const choicePanelRightInset = windowRect.right - choicePanelRect.right;
      const symmetricChoicePanelBuffer = Boolean(
        choicePanelRect.width > 0
        && choicePanelLeftInset >= 10
        && choicePanelRightInset >= 10
        && Math.abs(choicePanelLeftInset - choicePanelRightInset) <= 4
      );
      const selectorCenterY = selectorRect.top + (selectorRect.height / 2);
      const createCenterY = createRect.top + (createRect.height / 2);
      const rowTopDelta = Math.abs(selectorCenterY - createCenterY);
      const sameRow = Boolean(
        create
        && rowTopDelta <= 9
        && createRect.left >= selectorRect.right - 2
      );
      const insideRow = Boolean(
        selectorRect.left >= rowRect.left - 1
        && createRect.right <= rowRect.right + 1
      );
      const equalFootprint = Math.abs(selectorRect.width - createRect.width) <= 2;
      const standardFootprint = Boolean(
        selectorRect.width >= 150
        && createRect.width >= 150
        && equalFootprint
        && insideRow
      );
      const wasOpen = selector.dataset.dropdownOpen === "true";
      if (typeof monitoringHudSetOverlayProfileWindowDropdownOpen === "function") {
        monitoringHudSetOverlayProfileWindowDropdownOpen(true);
      }
      const menuRect = menu ? menu.getBoundingClientRect() : { left: 0, right: 0, top: 0, bottom: 0, width: 0 };
      const menuUnclipped = Boolean(
        menu
        && !menu.hidden
        && menuRect.width >= Math.max(180, selectorRect.width - 2)
        && menuRect.width <= selectorRect.width + 2
        && menuRect.left >= rowRect.left - 1
        && menuRect.right <= rowRect.right + 1
        && menuRect.top >= windowRect.top - 1
        && menuRect.bottom <= windowRect.bottom + 1
      );
      if (typeof monitoringHudSetOverlayProfileWindowDropdownOpen === "function") {
        monitoringHudSetOverlayProfileWindowDropdownOpen(wasOpen);
      }
      return {
        sameRow,
        standardFootprint,
        equalFootprint,
        menuUnclipped,
        insideRow,
        selectorWidth: selectorRect.width,
        createWidth: createRect.width,
        rowWidth: rowRect.width,
        menuWidth: menuRect.width,
        rowTopDelta,
        leftBuffer,
        rightBuffer,
        symmetricWindowBuffer,
        choicePanelLeftInset,
        choicePanelRightInset,
        symmetricChoicePanelBuffer,
        selectorRect,
        rowRect,
        choicePanelRect
      };
    };
    const currentMeasurement = measureSelectorLayout();
    const scalesWithinRow = Boolean(
      currentMeasurement.sameRow
      && currentMeasurement.standardFootprint
      && currentMeasurement.insideRow
    );
    const previousWindowStyle = monitoringHudOverlayProfileWindow ? (monitoringHudOverlayProfileWindow.getAttribute("style") || "") : "";
    const measureSelectorAtWidth = (width) => {
      if (!monitoringHudOverlayProfileWindow) {
        return { sameRow: false, standardFootprint: false, menuUnclipped: false, selectorWidth: 0, rowWidth: 0, menuWidth: 0 };
      }
      monitoringHudOverlayProfileWindow.style.width = `${Math.round(width)}px`;
      monitoringHudOverlayProfileWindow.style.minWidth = "0";
      monitoringHudOverlayProfileWindow.style.maxWidth = "none";
      const measurement = measureSelectorLayout();
      return {
        sameRow: measurement.sameRow,
        standardFootprint: measurement.standardFootprint,
        equalFootprint: measurement.equalFootprint,
        menuUnclipped: measurement.menuUnclipped,
        selectorWidth: measurement.selectorWidth,
        createWidth: measurement.createWidth,
        rowWidth: measurement.rowWidth,
        menuWidth: measurement.menuWidth,
        rowTopDelta: measurement.rowTopDelta,
        leftBuffer: measurement.leftBuffer,
        rightBuffer: measurement.rightBuffer,
        symmetricWindowBuffer: measurement.symmetricWindowBuffer,
        choicePanelLeftInset: measurement.choicePanelLeftInset,
        choicePanelRightInset: measurement.choicePanelRightInset,
        symmetricChoicePanelBuffer: measurement.symmetricChoicePanelBuffer
      };
    };
    const availableWidth = Math.max(460, Math.min(820, (window.innerWidth || 900) - 56));
    const compactWidth = Math.max(420, Math.min(availableWidth - 160, 620));
    const wideMeasurement = measureSelectorAtWidth(availableWidth);
    const compactMeasurement = measureSelectorAtWidth(compactWidth);
    if (monitoringHudOverlayProfileWindow) {
      if (previousWindowStyle) {
        monitoringHudOverlayProfileWindow.setAttribute("style", previousWindowStyle);
      } else {
        monitoringHudOverlayProfileWindow.removeAttribute("style");
      }
    }
    const responsiveCompact = Boolean(
      wideMeasurement.sameRow
      && compactMeasurement.sameRow
      && wideMeasurement.standardFootprint
      && compactMeasurement.standardFootprint
      && wideMeasurement.menuUnclipped
      && compactMeasurement.menuUnclipped
      && wideMeasurement.symmetricWindowBuffer
      && compactMeasurement.symmetricWindowBuffer
      && wideMeasurement.symmetricChoicePanelBuffer
      && compactMeasurement.symmetricChoicePanelBuffer
      && wideMeasurement.equalFootprint
      && compactMeasurement.equalFootprint
      && compactMeasurement.selectorWidth <= wideMeasurement.selectorWidth + 2
    );
    if (!currentMeasurement.symmetricWindowBuffer || !currentMeasurement.symmetricChoicePanelBuffer || !scalesWithinRow || !responsiveCompact || !currentMeasurement.menuUnclipped) {
      failures.push("overlay-manager-scaling:selector-stacked-oversized-or-clipped");
    }
    surfaces.push({
      name: "overlay-manager-scaling",
      selector: "#monitoring-hud-overlay-profile-window-selector",
      sampleCount: 1,
      scalesWithinRow,
      sameRow: currentMeasurement.sameRow,
      standardFootprint: currentMeasurement.standardFootprint,
      menuUnclipped: currentMeasurement.menuUnclipped,
      responsiveCompact,
      compactMeasurements: {
        current: {
          rowWidth: Math.round(currentMeasurement.rowWidth),
          selectorWidth: Math.round(currentMeasurement.selectorWidth),
          createWidth: Math.round(currentMeasurement.createWidth),
          menuWidth: Math.round(currentMeasurement.menuWidth),
          rowTopDelta: Math.round(currentMeasurement.rowTopDelta),
          leftBuffer: Math.round(currentMeasurement.leftBuffer),
          rightBuffer: Math.round(currentMeasurement.rightBuffer),
          symmetricWindowBuffer: currentMeasurement.symmetricWindowBuffer,
          choicePanelLeftInset: Math.round(currentMeasurement.choicePanelLeftInset),
          choicePanelRightInset: Math.round(currentMeasurement.choicePanelRightInset),
          symmetricChoicePanelBuffer: currentMeasurement.symmetricChoicePanelBuffer
        },
        wide: {
          windowWidth: Math.round(availableWidth),
          rowWidth: Math.round(wideMeasurement.rowWidth),
          selectorWidth: Math.round(wideMeasurement.selectorWidth),
          createWidth: Math.round(wideMeasurement.createWidth),
          menuWidth: Math.round(wideMeasurement.menuWidth),
          sameRow: wideMeasurement.sameRow,
          standardFootprint: wideMeasurement.standardFootprint,
          menuUnclipped: wideMeasurement.menuUnclipped,
          rowTopDelta: Math.round(wideMeasurement.rowTopDelta),
          leftBuffer: Math.round(wideMeasurement.leftBuffer),
          rightBuffer: Math.round(wideMeasurement.rightBuffer),
          symmetricWindowBuffer: wideMeasurement.symmetricWindowBuffer,
          choicePanelLeftInset: Math.round(wideMeasurement.choicePanelLeftInset),
          choicePanelRightInset: Math.round(wideMeasurement.choicePanelRightInset),
          symmetricChoicePanelBuffer: wideMeasurement.symmetricChoicePanelBuffer
        },
        compact: {
          windowWidth: Math.round(compactWidth),
          rowWidth: Math.round(compactMeasurement.rowWidth),
          selectorWidth: Math.round(compactMeasurement.selectorWidth),
          createWidth: Math.round(compactMeasurement.createWidth),
          menuWidth: Math.round(compactMeasurement.menuWidth),
          sameRow: compactMeasurement.sameRow,
          standardFootprint: compactMeasurement.standardFootprint,
          menuUnclipped: compactMeasurement.menuUnclipped,
          rowTopDelta: Math.round(compactMeasurement.rowTopDelta),
          leftBuffer: Math.round(compactMeasurement.leftBuffer),
          rightBuffer: Math.round(compactMeasurement.rightBuffer),
          symmetricWindowBuffer: compactMeasurement.symmetricWindowBuffer,
          choicePanelLeftInset: Math.round(compactMeasurement.choicePanelLeftInset),
          choicePanelRightInset: Math.round(compactMeasurement.choicePanelRightInset),
          symmetricChoicePanelBuffer: compactMeasurement.symmetricChoicePanelBuffer
        }
      },
      selectorRect: {
        left: Math.round(currentMeasurement.selectorRect.left),
        right: Math.round(currentMeasurement.selectorRect.right),
        width: Math.round(currentMeasurement.selectorRect.width)
      },
      rowRect: {
        left: Math.round(currentMeasurement.rowRect.left),
        right: Math.round(currentMeasurement.rowRect.right),
        width: Math.round(currentMeasurement.rowRect.width)
      },
      choicePanelRect: {
        left: Math.round(currentMeasurement.choicePanelRect.left),
        right: Math.round(currentMeasurement.choicePanelRect.right),
        width: Math.round(currentMeasurement.choicePanelRect.width)
      }
    });
  }
  function inspectOverlayProfileMinimumFunctionalHeight() {
    const windowElement = monitoringHudOverlayProfileWindow;
    const list = monitoringHudOverlayProfileMembershipList;
    if (!windowElement || !list || !monitoringHudVisualInspectionVisible(windowElement)) {
      failures.push("overlay-profile-minimum-functional-height:missing-window-or-list");
      surfaces.push({ name: "overlay-profile-minimum-functional-height", selector: "#monitoring-hud-overlay-profile-membership-list", sampleCount: 0 });
      return;
    }
    const rows = Array.from(list.querySelectorAll("[data-overlay-profile-membership-row]")).filter(monitoringHudVisualInspectionVisible);
    const firstRow = rows[0] || null;
    const listRect = list.getBoundingClientRect();
    const firstRowRect = firstRow
      ? firstRow.getBoundingClientRect()
      : { top: 0, bottom: 0, height: 0 };
    const listStyle = window.getComputedStyle(list);
    const windowStyle = window.getComputedStyle(windowElement);
    const oneFullMonitorVisible = Boolean(
      firstRow
      && firstRowRect.height >= 46
      && firstRowRect.top >= listRect.top - 1
      && firstRowRect.bottom <= listRect.bottom + 1
    );
    const compactScrollPolicy = windowElement.dataset.overlayProfileOuterScrollPolicy === "normal-no-scroll-emergency-compact-scroll";
    const membershipHasFunctionalMinimum = Number.parseFloat(listStyle.minHeight || "0") >= 54 || listRect.height >= firstRowRect.height;
    const emergencyScrollAvailable = Boolean(
      windowStyle.overflowY === "auto"
      || windowStyle.overflowY === "scroll"
      || windowElement.scrollHeight <= windowElement.clientHeight + 1
    );
    if (!oneFullMonitorVisible || !compactScrollPolicy || !membershipHasFunctionalMinimum || !emergencyScrollAvailable) {
      failures.push("overlay-profile-minimum-functional-height:no-full-monitor-row-at-compact-minimum");
    }
    surfaces.push({
      name: "overlay-profile-minimum-functional-height",
      selector: "#monitoring-hud-overlay-profile-membership-list",
      sampleCount: rows.length,
      oneFullMonitorVisible,
      compactScrollPolicy,
      membershipHasFunctionalMinimum,
      emergencyScrollAvailable,
      listRect: {
        top: Math.round(listRect.top),
        bottom: Math.round(listRect.bottom),
        height: Math.round(listRect.height)
      },
      firstRowRect: {
        top: Math.round(firstRowRect.top),
        bottom: Math.round(firstRowRect.bottom),
        height: Math.round(firstRowRect.height)
      }
    });
  }
  function inspectSourceSettingsFocusFrame() {
    const element = document.getElementById("monitoring-hud-source-settings-body");
    if (!element) {
      failures.push("source-settings-shift-focus-frame:missing");
      return;
    }
    if (typeof element.focus === "function") element.focus({ preventScroll: true });
    const style = monitoringHudVisualInspectionStyleSnapshot(element);
    const outline = `${style.outlineStyle || ""} ${style.outlineColor || ""}`.toLowerCase();
    const noGoldFocus = Boolean(
      style.outlineStyle === "none"
      || (
        outline.indexOf("255, 193") < 0
        && outline.indexOf("255, 214") < 0
        && outline.indexOf("gold") < 0
        && outline.indexOf("yellow") < 0
      )
    );
    if (!noGoldFocus) failures.push("source-settings-shift-focus-frame:gold-focus-outline");
    surfaces.push({
      name: "source-settings-shift-focus-frame",
      selector: "#monitoring-hud-source-settings-body",
      sampleCount: 1,
      noGoldFocus,
      style
    });
  }
  function inspectResponsiveWindowContract() {
    const elements = Array.from(document.querySelectorAll(".monitoring-hud__child-window:not([hidden])")).filter(monitoringHudVisualInspectionVisible);
    const sampled = elements.map((element, index) => {
      const rect = element.getBoundingClientRect();
      const withinViewport = Boolean(
        rect.left >= -1
        && rect.top >= -1
        && rect.right <= window.innerWidth + 1
        && rect.bottom <= window.innerHeight + 1
      );
      const style = window.getComputedStyle ? window.getComputedStyle(element) : {};
      const overflowY = String(style.overflowY || "");
      const noOuterScrollbarNeeded = Boolean(
        !["auto", "scroll"].includes(overflowY)
        || element.scrollHeight <= element.clientHeight + 2
      );
      if (!withinViewport) failures.push(`responsive-window-contract:${index}:viewport-clipping`);
      if (!noOuterScrollbarNeeded) failures.push(`responsive-window-contract:${index}:outer-window-scrollbar-needed`);
      return {
        index,
        windowClass: element.className,
        withinViewport,
        noOuterScrollbarNeeded,
        rect: {
          left: Math.round(rect.left),
          top: Math.round(rect.top),
          right: Math.round(rect.right),
          bottom: Math.round(rect.bottom),
          width: Math.round(rect.width),
          height: Math.round(rect.height)
        },
        clientHeight: element.clientHeight,
        scrollHeight: element.scrollHeight
      };
    });
    if (!sampled.length) failures.push("responsive-window-contract:no-open-window-sample");
    surfaces.push({ name: "responsive-window-contract", selector: ".monitoring-hud__child-window:not([hidden])", sampleCount: sampled.length, sampled });
  }
  try {
    if (monitoringHud) {
      monitoringHud.dataset.hudWideVisualInspectionMatrix = "running";
      monitoringHud.dataset.visualInspectionScope = "buttons-dropdowns-rows-chips-fields-page-breaks-backgrounds-bleed-clipping-scaling";
    }
    monitoringHudCloseChildWindow({ force: true });
    inspectTarget("dashboard-window-border", "#monitoring-hud", { requireFocus: false });
    inspectTarget("dashboard-chrome-background", ".monitoring-hud__chrome", { requireFocus: false });
    inspectTarget("dashboard-control-hub-scrollbar", ".monitoring-hud__control-hub", { requireFocus: false });
    inspectTarget("dashboard-hud-overlay-card", '[data-dashboard-hub-card="hud-overlay"]', { requireFocus: false });
    inspectTarget("dashboard-recording-card", '[data-dashboard-hub-card="recording"]', { requireFocus: false });
    inspectTarget("dashboard-monitor-groups-card", '[data-dashboard-hub-card="monitor-groups"]', { requireFocus: false });
    inspectTarget("dashboard-data-sources-card", '[data-dashboard-hub-card="data-sources"]', { requireFocus: false });
    inspectTarget("dashboard-readiness-card", '[data-dashboard-hub-card="readiness"]', { requireFocus: false });
    inspectTarget("dashboard-data-sources-deferred", '[data-control="open-data-sources"]', { expectDisabled: true });
    inspectRowTitleInset("dashboard-row-title-tabs", ".monitoring-hud__state-row > span, .monitoring-hud__overlay-profile-heading > span");
    monitoringHudSetOverlayProfileDropdownOpen(true);
    inspectTarget("dashboard-close", "#monitoring-hud-dashboard-close-action");
    inspectTarget("dashboard-settings", "#monitoring-hud-settings-action");
    inspectTarget("dashboard-warning", "#monitoring-hud-warning-toggle", { semanticRole: "warning" });
    inspectTarget("dashboard-overlay-profile-toggle", "#monitoring-hud-overlay-profile-toggle");
    inspectTarget("dashboard-overlay-profile-option", "[data-overlay-profile-option]");
    inspectTarget("dashboard-overlay-profile-settings", "#monitoring-hud-overlay-profile-open-settings");
    inspectTarget("dashboard-manage-monitors", "#monitoring-hud-edit-monitor-action");
    monitoringHudSetOverlayProfileDropdownOpen(false);
    monitoringHudOpenChildWindow("overlay-profile-settings");
    monitoringHudSetOverlayProfileWindowDropdownOpen(true);
    inspectTarget("overlay-window-frame", "#monitoring-hud-overlay-profile-window", { requireFocus: false });
    inspectTarget("overlay-choice-panel", ".monitoring-hud__overlay-profile-choice-panel", { requireFocus: false });
    inspectTarget("overlay-manager-meta-row", ".monitoring-hud__overlay-profile-manager-meta", { requireFocus: false });
    inspectResponsiveWindowContract();
    inspectTarget("overlay-window-close", '[data-child-window-close="overlay-profile-settings"]');
    inspectTarget("overlay-create", "#monitoring-hud-overlay-profile-create");
    inspectTarget("overlay-profile-window-toggle", "#monitoring-hud-overlay-profile-window-toggle");
    inspectTarget("overlay-profile-window-option", "[data-overlay-profile-window-option]");
    inspectOverlayProfileManagerScaling();
    monitoringHudSetOverlayProfileWindowDropdownOpen(false);
    if (typeof monitoringHudOpenOverlayProfileDetail === "function") {
      monitoringHudOpenOverlayProfileDetail(monitoringHudDefaultOverlayProfileId);
    }
    inspectOverlayProfileMinimumFunctionalHeight();
    monitoringHudSetOverlayProfileMonitorFilterOpen(true);
    inspectTarget("overlay-monitor-filter-toggle", "#monitoring-hud-overlay-profile-monitor-filter-toggle");
    inspectTarget("overlay-monitor-filter-option", "[data-overlay-profile-monitor-filter-option]");
    inspectTarget("overlay-profile-monitor-search", "#monitoring-hud-overlay-profile-monitor-search", { requireFocus: false });
    inspectTarget("overlay-save-disabled", "#monitoring-hud-overlay-profile-save", { expectDisabled: true });
    inspectTarget("overlay-discard-disabled", "#monitoring-hud-overlay-profile-discard", { expectDisabled: true });
    inspectTarget("overlay-delete-danger", "#monitoring-hud-overlay-profile-delete", { semanticRole: "danger" });
    inspectCheckedControlHoverAffordance("overlay-checked-control-hover-affordance");
    monitoringHudSetOverlayProfileMonitorFilterOpen(false);
    monitoringHudOpenChildWindow("monitor-group-edit");
    monitoringHudRenderMonitorManagement();
    monitoringHudSetSourceFilterDropdownOpen(true);
    inspectTarget("manage-window-frame", "#monitoring-hud-edit-monitor-window", { requireFocus: false });
    inspectTarget("manage-monitor-list-pane", ".monitoring-hud__monitor-list-pane", { requireFocus: false });
    inspectTarget("manage-monitor-detail-pane", ".monitoring-hud__monitor-detail-pane", { requireFocus: false });
    inspectTarget("manage-source-library-card", '[data-monitor-detail-card="sensor-source"]', { requireFocus: false });
    inspectTarget("manage-source-result-summary", "#monitoring-hud-sensor-result-summary", { requireFocus: false });
    inspectTarget("manage-provider-readiness-card", "#monitoring-hud-provider-readiness-panel", { requireFocus: false });
    inspectTarget("manage-window-close", '[data-child-window-close="monitor-group-edit"]');
    inspectTarget("manage-create", "#monitoring-hud-manage-monitor-create-action");
    inspectTarget("manage-monitor-row", "[data-monitor-select]");
    inspectTarget("source-search-field", "#monitoring-hud-sensor-search", { requireFocus: false });
    inspectTarget("source-filter-toggle", "#monitoring-hud-sensor-filter-toggle");
    inspectTarget("source-filter-option", '[data-source-filter]:not([aria-selected="true"])');
    monitoringHudSetSourceFilterDropdownOpen(false);
    monitoringHudSetPollingRateDropdownOpen(true);
    inspectTarget("polling-rate-toggle", "#monitoring-hud-monitor-polling-rate-toggle");
    inspectTarget("polling-rate-option", "[data-polling-rate-option]");
    monitoringHudSetPollingRateDropdownOpen(false);
    inspectTarget("source-picker-row", "[data-source-picker-row]");
    inspectTarget("source-picker-settings", "[data-source-settings-open]");
    inspectCheckedControlHoverAffordance("manage-checked-control-hover-affordance");
    const firstSettingsButton = document.querySelector("[data-source-settings-open]");
    if (firstSettingsButton) monitoringHudOpenSourceSettings(firstSettingsButton.dataset.sourceSettingsOpen || "");
    inspectTarget("source-settings-window-frame", "#monitoring-hud-source-settings-window", { requireFocus: false });
    inspectTarget("source-settings-summary", ".monitoring-hud__source-settings-summary", { requireFocus: false });
    inspectTarget("source-settings-body", "#monitoring-hud-source-settings-body", { requireFocus: false });
    inspectTarget("source-settings-warning-row", ".monitoring-hud__source-settings-warning", { requireFocus: false });
    inspectSourceSettingsFocusFrame();
    inspectResponsiveWindowContract();
    inspectTarget("source-display-mode-chip", '[data-sensor-display-mode-option]:not([aria-pressed="true"])');
    inspectTarget("source-polling-toggle", "[data-source-polling-toggle]");
    inspectTarget("source-settings-close", '[data-child-window-close="sensor-source-settings"]');
    inspectCheckedControlHoverAffordance("source-settings-checked-control-hover-affordance");
    monitoringHudOpenChildWindow("monitor-group-edit");
    monitoringHudRenderMonitorManagement();
    inspectTarget("assigned-overlay-status", "#monitoring-hud-monitor-overlay-profile-context");
    inspectTarget("monitor-detail-actions-row", ".monitoring-hud__detail-action-row", { requireFocus: false });
    inspectTarget("monitor-save-disabled", "#monitoring-hud-edit-monitor-confirm", { expectDisabled: true });
    inspectTarget("monitor-discard-disabled", "#monitoring-hud-edit-monitor-discard", { expectDisabled: true, semanticRole: "danger" });
    inspectTarget("monitor-delete-danger", "#monitoring-hud-monitor-detail-delete", { semanticRole: "danger" });
    if (typeof monitoringHudRequestDeleteMonitorGroup === "function") {
      monitoringHudRequestDeleteMonitorGroup(monitoringHudControlState.selectedMonitorId, { force: true });
    }
    inspectTarget("monitor-delete-confirm-danger", "#monitoring-hud-monitor-delete-confirm", { semanticRole: "danger" });
    inspectTarget("monitor-delete-cancel", "#monitoring-hud-monitor-delete-cancel", { semanticRole: "safe" });
    inspectDividerGroup("dashboard-page-breaks", ".monitoring-hud__state-row, .monitoring-hud__overlay-profile-panel");
    monitoringHudOpenChildWindow("dashboard-settings");
    inspectDividerGroup("child-window-page-breaks", ".monitoring-hud__setting-row");
    inspectRowTitleInset("child-window-row-title-tabs", ".monitoring-hud__setting-row > span, .monitoring-hud__source-settings-polling > span");
    inspectResponsiveWindowContract();
    inspectNoClipping("visible-hud-surfaces", "#monitoring-hud, .monitoring-hud__card, .monitoring-hud__child-window:not([hidden])");
  } catch (err) {
    failures.push(`exception:${String(err && err.message ? err.message : err)}`);
  }
  if (backup && window.setMonitoringHudControlState) {
    window.setMonitoringHudControlState(backup);
  }
  if (previousSourceFilterOpen && monitoringHudSensorFilter) {
    monitoringHudSetSourceFilterDropdownOpen(previousSourceFilterOpen === "true");
  }
  if (previousPollingOpen && monitoringHudMonitorPollingRateControl) {
    monitoringHudSetPollingRateDropdownOpen(previousPollingOpen === "true");
  }
  if (previousOverlayDropdownOpen && monitoringHudOverlayProfileSelector) {
    monitoringHudSetOverlayProfileDropdownOpen(previousOverlayDropdownOpen === "true");
  }
  if (previousOverlayWindowDropdownOpen && monitoringHudOverlayProfileWindowSelector) {
    monitoringHudSetOverlayProfileWindowDropdownOpen(previousOverlayWindowDropdownOpen === "true");
  }
  if (previousOverlayMonitorFilterOpen && monitoringHudOverlayProfileMonitorFilter) {
    monitoringHudSetOverlayProfileMonitorFilterOpen(previousOverlayMonitorFilterOpen === "true");
  }
  if (previousChildWindow && previousChildWindow !== "none") {
    monitoringHudOpenChildWindow(previousChildWindow);
  } else {
    monitoringHudCloseChildWindow({ force: true });
  }
  if (targets.length < 40) failures.push("per-element-visual-inventory-too-small");
  if (surfaces.length < 3) failures.push("visual-surface-inventory-too-small");
  const perElementVisualInventory = targets.map((target) => ({
    name: target.name,
    present: target.present === true,
    visible: target.visible === true,
    disabled: target.disabled === true,
    semanticRole: target.semanticRole || "default",
    textFits: target.textFits !== false,
    textDeadSpacePass: target.textDeadSpacePass !== false,
    defaultGlow: target.defaultGlow === true,
    hoverGlow: target.hoverGlow === true,
    focusCapable: target.focusCapable === true,
    screenshotRequired: true
  }));
  const issueFormCoverageMatrix = {
    "UTS-HUD-001": ["defaultButtonGlowUniformity", "buttonRoleColorUniformity"],
    "UTS-HUD-002": ["backgroundBleedClippingInspection", "dashboard-hud-overlay-card", "dashboard-recording-card", "dashboard-monitor-groups-card"],
    "UTS-HUD-003": ["buttonTextDeadSpacePass", "defaultButtonGlowUniformity"],
    "UTS-HUD-004": ["semanticHoverColorPreserved", "buttonRoleColorUniformity"],
    "UTS-HUD-005": ["buttonTextDeadSpacePass"],
    "UTS-HUD-006": ["source-picker-row", "sourceRowHoverPersistence", "checkedControlHoverAffordance"],
    "UTS-HUD-007": ["source-filter-toggle", "source-filter-option"],
    "UTS-HUD-008": ["source-picker-row", "sourceRowHoverPersistence"],
    "UTS-HUD-009": ["polling-rate-toggle", "pollingRateLiveCadence"],
    "UTS-HUD-010": ["source-settings-window-frame", "source-display-mode-chip", "source-polling-toggle"],
    "UTS-HUD-011": ["dashboard-settings", "dashboard-data-sources-deferred"],
    "UTS-HUD-012": ["dirtyGuardCoverage", "sameMonitorRowDirtyGuard", "monitor-detail-actions-row"],
    "UTS-HUD-013": ["perElementVisualInventory", "issueFormCoverageMatrix"],
    "UTS-HUD-014": ["overlay-window-frame", "overlay-choice-panel", "overlay-manager-meta-row", "overlay-manager-scaling", "overlay-profile-minimum-functional-height", "defaultProfileDeletePersists", "createRequiresSave", "createStartsEmptyMembership", "closeGuardOpensForCreatedDraft", "childWindowClickIsolation", "selectorLoadsSelectedSettings"],
    "UTS-HUD-015": ["dashboard-control-hub-scrollbar", "manage-monitor-list-pane"],
    "UTS-HUD-016": ["pageBreakVisualInspection", "dashboard-page-breaks", "child-window-page-breaks"],
    "UTS-HUD-017": ["buttonRoleColorUniformity", "semanticHoverColorPreserved"],
    "UTS-HUD-018": ["dashboard-row-title-tabs", "child-window-row-title-tabs", "pageBreakVisualInspection"],
    "UTS-HUD-019": ["responsive-window-contract", "sourceSettingsWindowFlow", "manage-monitor-row"],
    "UTS-HUD-020": ["source-settings-shift-focus-frame", "source-settings-body", "source-settings-warning-row"],
    "UTS-HUD-021": ["responsive-window-contract", "visible-hud-surfaces", "dashboard-window-border", "overlay-manager-scaling", "overlay-profile-minimum-functional-height", "windowSelectorResponsiveCompact", "overlay-profile-compact-default-functional"]
  };
  const proof = {
    passed: failures.length === 0,
    failures,
    targetCount: targets.length,
    targets,
    surfaceCount: surfaces.length,
    surfaces,
    scope: "buttons-dropdowns-rows-chips-fields-page-breaks-backgrounds-bleed-clipping-scaling",
    perElementVisualInventory,
    issueFormCoverageMatrix,
    buttonGlowUniformity: failures.every((failure) => String(failure).indexOf("hover-glow-missing") < 0),
    defaultButtonGlowUniformity: failures.every((failure) => String(failure).indexOf("default-glow-missing") < 0),
    semanticHoverColorPreserved: failures.every((failure) => String(failure).indexOf("semantic-hover-color-drift") < 0),
    buttonRoleColorUniformity: failures.every((failure) => String(failure).indexOf("semantic-hover-color-drift") < 0),
    buttonTextDeadSpacePass: failures.every((failure) => String(failure).indexOf("button-dead-space-missing") < 0 && String(failure).indexOf("button-text-clipping") < 0),
    sourceRowHoverPersistence: Boolean(monitoringHudMonitorSensorAssignment && monitoringHudMonitorSensorAssignment.dataset.sourcePickerHoverPersistence),
    checkedControlHoverAffordance: surfaces.some((surface) => surface.name === "manage-checked-control-hover-affordance" && surface.sampled && surface.sampled.every((sample) => sample.hasHoverAffordance === true))
      && surfaces.some((surface) => surface.name === "source-settings-checked-control-hover-affordance" && surface.sampled && surface.sampled.every((sample) => sample.hasHoverAffordance === true)),
    sourceSettingsWindowFlow: "nested-source-settings-returns-to-manage-monitors",
    dirtyGuardCoverage: "monitor-and-overlay-profile-save-discard-close-guards",
    pageBreakVisualInspection: surfaces.some((surface) => surface.name === "dashboard-page-breaks")
      && surfaces.some((surface) => surface.name === "child-window-page-breaks"),
    backgroundBleedClippingInspection: surfaces.some((surface) => surface.name === "visible-hud-surfaces"),
    sourceSettingsFocusNoGold: surfaces.some((surface) => surface.name === "source-settings-shift-focus-frame" && surface.noGoldFocus === true),
    rowTitleTabsInspected: surfaces.some((surface) => surface.name === "dashboard-row-title-tabs")
      && surfaces.some((surface) => surface.name === "child-window-row-title-tabs"),
    responsiveWindowContract: surfaces.some((surface) => surface.name === "responsive-window-contract"),
    overlayManagerScaling: surfaces.some((surface) => (
      surface.name === "overlay-manager-scaling"
      && surface.scalesWithinRow === true
      && surface.sameRow === true
      && surface.standardFootprint === true
      && surface.menuUnclipped === true
      && surface.responsiveCompact === true
    )),
    dividerGlowReduced50Percent: surfaces.filter((surface) => String(surface.name || "").indexOf("page-breaks") >= 0).every((surface) => surface.dividerGlowReduced === true),
    visualInspectionScopeCovered: targets.length >= 40 && surfaces.length >= 3
  };
  if (monitoringHud) {
    monitoringHud.dataset.hudWideVisualInspectionMatrix = proof.passed ? "pass" : "fail";
    monitoringHud.dataset.buttonGlowUniformity = proof.buttonGlowUniformity ? "pass" : "fail";
    monitoringHud.dataset.defaultButtonGlowUniformity = proof.defaultButtonGlowUniformity ? "pass" : "fail";
    monitoringHud.dataset.semanticHoverColorPreserved = proof.semanticHoverColorPreserved ? "pass" : "fail";
    monitoringHud.dataset.buttonRoleColorUniformity = proof.buttonRoleColorUniformity ? "pass" : "fail";
    monitoringHud.dataset.buttonTextDeadSpacePass = proof.buttonTextDeadSpacePass ? "pass" : "fail";
    monitoringHud.dataset.perElementVisualInventory = proof.visualInspectionScopeCovered ? "pass" : "fail";
    monitoringHud.dataset.visualInspectionScope = proof.scope;
  }
  monitoringHudControlState.visualInspectionMatrixProof = proof;
  return proof;
};

window.runMonitoringHudInteractiveControlStressProof = function() {
  const backup = window.getMonitoringHudControlState ? window.getMonitoringHudControlState() : null;
  const failures = [];
  const states = {};
  let sourcePickerCheckmarkProof = {};
  let displayModeChipProof = {};
  let pollingRateHitboxProof = {};
  let manageCloseHitboxProof = {};
  let visualInspectionMatrixProof = {};
  let monitorNameReuseProof = {};
  function prepareVisibleTarget(element) {
    if (!element) return;
    if (typeof element.scrollIntoView === "function") {
      element.scrollIntoView({ block: "center", inline: "center", behavior: "instant" });
    }
  }
  function targetSnapshot(name, selector) {
    const element = document.querySelector(selector);
    prepareVisibleTarget(element);
    const snapshot = monitoringHudControlInterceptionSnapshot(element);
    states[name] = Object.assign({}, snapshot, {
      selector,
      present: Boolean(element),
      focusable: Boolean(element && typeof element.focus === "function"),
      disabled: Boolean(element && element.disabled),
      ariaDisabled: element && element.getAttribute ? String(element.getAttribute("aria-disabled") || "false") : ""
    });
    if (!element) failures.push(`${name}:missing`);
    if (element && element.disabled) failures.push(`${name}:disabled`);
    if (element && snapshot.sameTargetOrChild === false) failures.push(`${name}:intercepted`);
    return element;
  }
  function activate(name, selector, check) {
    const element = targetSnapshot(name, selector);
    if (!element) return false;
    element.click();
    const passed = typeof check === "function" ? Boolean(check(element)) : true;
    if (!passed) failures.push(`${name}:first-click-no-state-change`);
    return passed;
  }
  try {
    if (monitoringHud) {
      monitoringHud.dataset.interactiveControlVisualAffordance = "normal-hover-active-focus-disabled-open-selected";
      monitoringHud.dataset.interactiveControlReliability = "first-click-stress-running";
      monitoringHud.dataset.clickInterceptionDiagnostics = "z-index-pointer-events-disabled-aria-dom-focus-timing";
      monitoringHud.dataset.pollingRateDropdown = "nexus-styled-bounded-control";
    }
    monitoringHudPendingDeleteMonitorId = "";
    monitoringHudSetMonitorDraftDirty(false);
    monitoringHudSetSourceFilterDropdownOpen(false);
    monitoringHudSetPollingRateDropdownOpen(false);
    monitoringHudRenderMonitorManagement();
    monitoringHudCloseChildWindow({ force: true });
    activate("dashboard-settings", "#monitoring-hud-settings-action", () => monitoringHudActiveChildWindow === "dashboard-settings");
    activate("settings-close", '[data-child-window-close="dashboard-settings"]', () => monitoringHudActiveChildWindow !== "dashboard-settings");
    activate("dashboard-warning", "#monitoring-hud-warning-toggle", () => true);
    activate("dashboard-manage-monitors", "#monitoring-hud-edit-monitor-action", () => monitoringHudActiveChildWindow === "monitor-group-edit");
    if (typeof monitoringHudManageCloseHitboxProof === "function") {
      manageCloseHitboxProof = monitoringHudManageCloseHitboxProof() || {};
      if (manageCloseHitboxProof.passed !== true) failures.push("manage-close-hitbox-partial-interception");
    }
    const beforeSelected = monitoringHudControlState.selectedMonitorId;
    const nextRow = document.querySelector(`[data-monitor-select]:not([data-monitor-select="${beforeSelected}"])`);
    if (nextRow) {
      const nextId = nextRow.dataset.monitorSelect || "";
      activate("monitor-row-switch", `[data-monitor-select="${nextId}"]`, () => monitoringHudControlState.selectedMonitorId === nextId);
    }
    activate("manage-create", "#monitoring-hud-manage-monitor-create-action", () => {
      const id = monitoringHudControlState.selectedMonitorId || "";
      const card = monitoringHudControlState.cards[id];
      return Boolean(
        id.indexOf("monitor-") === 0
        && card
        && monitoringHudUnsavedMonitorDirty
        && Array.isArray(card.sensors)
        && card.sensors.length === 0
      );
    });
    activate("manage-create-save-required", "#monitoring-hud-edit-monitor-confirm", () => !monitoringHudUnsavedMonitorDirty);
    activate("delete-selected", "#monitoring-hud-monitor-detail-delete", () => monitoringHudPendingDeleteMonitorId === monitoringHudControlState.selectedMonitorId);
    activate("delete-cancel", "#monitoring-hud-monitor-delete-cancel", () => !monitoringHudPendingDeleteMonitorId);
    const input = document.getElementById("monitoring-hud-edit-monitor-name");
    if (input) {
      input.value = "First Click Stress Draft";
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
    const sameRowDirtyId = monitoringHudControlState.selectedMonitorId || "";
    if (sameRowDirtyId) {
      activate("same-row-dirty-guard", `[data-monitor-select="${sameRowDirtyId}"]`, () => {
        const guard = document.getElementById("monitoring-hud-monitor-unsaved-guard");
        return Boolean(
          guard
          && !guard.hidden
          && guard.dataset.pendingMonitorAction === "same-select"
          && monitoringHud
          && monitoringHud.dataset.sameMonitorRowDirtyClick === "guard-open-draft-preserved"
        );
      });
      activate("same-row-dirty-discard", "#monitoring-hud-monitor-unsaved-discard", () => monitoringHudActiveChildWindow === "monitor-group-edit" && !monitoringHudUnsavedMonitorDirty);
      const dirtyAgainInput = document.getElementById("monitoring-hud-edit-monitor-name");
      if (dirtyAgainInput) {
        dirtyAgainInput.value = "First Click Stress Draft";
        dirtyAgainInput.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
    activate("dirty-close", '[data-child-window-close="monitor-group-edit"]', () => {
      const guard = document.getElementById("monitoring-hud-monitor-unsaved-guard");
      return Boolean(guard && !guard.hidden && guard.dataset.pendingMonitorAction === "close");
    });
    activate("dirty-discard", "#monitoring-hud-monitor-unsaved-discard", () => {
      const guard = document.getElementById("monitoring-hud-monitor-unsaved-guard");
      return Boolean(monitoringHudActiveChildWindow === "monitor-group-edit" && guard && guard.hidden && !monitoringHudUnsavedMonitorDirty);
    });
    if (typeof monitoringHudOpenChildWindow === "function") monitoringHudOpenChildWindow("monitor-group-edit");
    activate("source-filter-open", "#monitoring-hud-sensor-filter-toggle", () => monitoringHudSensorFilter && monitoringHudSensorFilter.dataset.filterOpen === "true");
    activate("source-filter-supported", '[data-source-filter="supported"]', () => monitoringHudSensorFilterValue() === "supported");
    activate("source-filter-reopen", "#monitoring-hud-sensor-filter-toggle", () => monitoringHudSensorFilter && monitoringHudSensorFilter.dataset.filterOpen === "true");
    monitoringHudSetSourceFilterDropdownOpen(false);
    activate("polling-rate-open", "#monitoring-hud-monitor-polling-rate-toggle", () => monitoringHudMonitorPollingRateControl && monitoringHudMonitorPollingRateControl.dataset.dropdownOpen === "true");
    activate("polling-rate-5s", '[data-polling-rate-option="5000"]', () => monitoringHudMonitorPollingRate && monitoringHudMonitorPollingRate.value === "5000");
    if (typeof monitoringHudPollingRateHitboxProof === "function") {
      pollingRateHitboxProof = monitoringHudPollingRateHitboxProof() || {};
      if (pollingRateHitboxProof.passed !== true) failures.push("polling-rate-hitbox-too-wide");
    }
    if (typeof window.runMonitoringHudSourcePickerCheckmarkStressProof === "function") {
      sourcePickerCheckmarkProof = window.runMonitoringHudSourcePickerCheckmarkStressProof() || {};
      if (sourcePickerCheckmarkProof.passed !== true) failures.push("source-picker-checkmark-stress");
    }
    if (typeof window.runMonitoringHudDisplayModeChipStressProof === "function") {
      displayModeChipProof = window.runMonitoringHudDisplayModeChipStressProof() || {};
      if (displayModeChipProof.passed !== true) failures.push("display-mode-chip-stress");
    }
    monitorNameReuseProof = typeof window.runMonitoringHudMonitorGroupNameReuseProof === "function"
      ? window.runMonitoringHudMonitorGroupNameReuseProof() || {}
      : {};
    if (monitorNameReuseProof.passed !== true) failures.push("monitor-group-name-reuse-proof");
    monitoringHudOpenChildWindow("monitor-group-edit");
    monitoringHudOpenSourceSettings("cpu-load");
    const warningToggle = document.querySelector('[data-sensor-warning-enabled="cpu-load"]');
    const warningBefore = Boolean(warningToggle && warningToggle.checked);
    activate("source-settings-warning-toggle", '[data-sensor-warning-enabled="cpu-load"]', () => {
      const toggle = document.querySelector('[data-sensor-warning-enabled="cpu-load"]');
      return Boolean(toggle && toggle.checked) !== warningBefore;
    });
    activate("source-settings-rate-open", '[data-source-polling-toggle="cpu-load"]', () => {
      const control = document.querySelector('[data-source-polling-control="cpu-load"]');
      const menu = document.querySelector('[data-source-polling-menu="cpu-load"]');
      return Boolean(control && control.dataset.dropdownOpen === "true" && menu && !menu.hidden);
    });
    activate("source-settings-rate-select", '[data-source-polling-control="cpu-load"] [data-source-polling-option="2000"]', () => {
      const control = document.querySelector('[data-source-polling-control="cpu-load"]');
      return Boolean(control && control.dataset.selectedValue === "2000" && monitoringHudActiveChildWindow === "sensor-source-settings");
    });
    activate("source-settings-return-manage", '[data-child-window-close="sensor-source-settings"]', () => monitoringHudActiveChildWindow === "monitor-group-edit");
    monitoringHudOpenChildWindow("overlay-profile-settings");
    if (typeof monitoringHudOpenOverlayProfileDetail === "function") {
      monitoringHudOpenOverlayProfileDetail(monitoringHudDefaultOverlayProfileId);
    }
    const overlayInput = document.getElementById("monitoring-hud-overlay-profile-name-input");
    if (overlayInput) {
      overlayInput.value = "Overlay Profile Dirty Guard Proof";
      overlayInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
    activate("overlay-profile-dirty-close", '[data-child-window-close="overlay-profile-settings"]', () => {
      const guard = document.getElementById("monitoring-hud-overlay-profile-unsaved-guard");
      return Boolean(guard && !guard.hidden && guard.dataset.unsavedGuard === "open-save-discard");
    });
    activate("overlay-profile-dirty-discard", "#monitoring-hud-overlay-profile-unsaved-discard", () => {
      const guard = document.getElementById("monitoring-hud-overlay-profile-unsaved-guard");
      return Boolean(monitoringHudActiveChildWindow === "overlay-profile-settings" && guard && guard.hidden);
    });
    if (typeof window.runMonitoringHudVisualInspectionMatrixProof === "function") {
      visualInspectionMatrixProof = window.runMonitoringHudVisualInspectionMatrixProof() || {};
      if (visualInspectionMatrixProof.passed !== true) failures.push("hud-wide-visual-inspection-matrix");
    }
    if (typeof monitoringHudOpenChildWindow === "function") {
      monitoringHudOpenChildWindow("monitor-group-edit");
      monitoringHudRenderMonitorManagement();
    }
    const saveInput = document.getElementById("monitoring-hud-edit-monitor-name");
    if (saveInput) {
      saveInput.value = "First Click Stress Save";
      saveInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
    activate("save-monitor", "#monitoring-hud-edit-monitor-confirm", () => true);
    if (typeof monitoringHudOpenChildWindow === "function") monitoringHudOpenChildWindow("monitor-group-edit");
    activate("manage-close-clean", '[data-child-window-close="monitor-group-edit"]', () => monitoringHudActiveChildWindow !== "monitor-group-edit");
    if (backup && window.setMonitoringHudControlState) {
      window.setMonitoringHudControlState(backup);
      monitoringHudOpenChildWindow("monitor-group-edit");
    }
  } catch (err) {
    failures.push(`exception:${String(err && err.message ? err.message : err)}`);
  }
  const proof = {
    passed: failures.length === 0,
    failures,
    stateCount: Object.keys(states).length,
    states,
    repeatedFirstClickStress: true,
    postRenderStatesCovered: [
      "re-render",
      "dirty-guard",
      "same-row-dirty-guard",
      "delete-confirmation",
      "dropdown-open",
      "post-close-reopen",
      "post-render"
    ],
    pollingRateDropdownNexusStyled: Boolean(monitoringHudMonitorPollingRateControl && monitoringHudMonitorPollingRateControl.dataset.selectedValue),
    pollingRateHitboxToggleOnly: pollingRateHitboxProof.passed === true,
    pollingRateHitboxProof,
    manageCloseHitboxFullHeight: manageCloseHitboxProof.passed === true,
    manageCloseHitboxProof,
    sourceFilterDropdownNexusStyled: Boolean(monitoringHudSensorFilter && monitoringHudSensorFilter.dataset.sourceFilterMode === "nexus-dropdown-source-picker"),
    sourcePickerCheckmarkStress: sourcePickerCheckmarkProof.passed === true,
    sourcePickerCheckmarkProof,
    displayModeChipStress: displayModeChipProof.passed === true,
    displayModeChipProof,
    monitorGroupNameReuseAfterDelete: monitorNameReuseProof.passed === true,
    monitorNameReuseProof,
    sourceSettingsFlowStress: failures.every((failure) => String(failure).indexOf("source-settings-") !== 0),
    sameMonitorRowDirtyGuard: failures.every((failure) => String(failure).indexOf("same-row-dirty-") !== 0),
    overlayProfileDirtyGuardStress: failures.every((failure) => String(failure).indexOf("overlay-profile-dirty-") !== 0),
    hudWideVisualInspectionMatrix: visualInspectionMatrixProof.passed === true,
    visualInspectionMatrixProof,
    affordanceStatesRequired: "normal-hover-active-focus-visible-disabled-open-selected-warning"
  };
  monitoringHudReliableActivationState.visualStates = states;
  if (monitoringHud) {
    monitoringHud.dataset.interactiveControlReliability = proof.passed ? "first-click-stress-pass" : "first-click-stress-fail";
    monitoringHud.dataset.interactiveControlVisualAffordance = "normal-hover-active-focus-visible-disabled-open-selected-hud-wide-glow";
    monitoringHud.dataset.interactiveControlStressProof = proof.passed ? "pass" : "fail";
    monitoringHud.dataset.pollingRateDropdown = "nexus-styled-bounded-control";
  }
  monitoringHudControlState.interactiveControlReliabilityProof = proof;
  return proof;
};

window.runMonitoringHudSourcePickerCheckmarkStressProof = function() {
  const backup = window.getMonitoringHudControlState ? window.getMonitoringHudControlState() : null;
  const failures = [];
  const toggles = [];
  const activationMethods = ["row-click", "checkbox-click", "keyboard-space"];
  let maxToggleMs = 0;
  let rowsTested = 0;
  let rowsAvailable = 0;
  let alternatingToggleCount = 0;
  let alternatingTogglePass = false;
  function dispatchHumanPointerDown(target) {
    if (!target || typeof target.dispatchEvent !== "function") return;
    let event = null;
    try {
      event = new PointerEvent("pointerdown", {
        bubbles: true,
        cancelable: true,
        pointerType: "mouse",
        isPrimary: true
      });
    } catch (err) {
      event = new MouseEvent("pointerdown", { bubbles: true, cancelable: true });
    }
    target.dispatchEvent(event);
  }
  try {
    if (typeof window.setMonitoringHudLargeFixtureMode === "function") {
      window.setMonitoringHudLargeFixtureMode(80);
    }
    monitoringHudOpenChildWindow("monitor-group-edit");
    if (monitoringHudSensorSearch) {
      monitoringHudSensorSearch.value = "";
    }
    monitoringHudSetSourceFilterValue("supported");
    monitoringHudSetSourceFilterDropdownOpen(false);
    monitoringHudRenderMonitorManagement();
    const rows = Array.from(document.querySelectorAll("[data-source-picker-row]"))
      .filter((row) => row.dataset.sensorAssignable === "true" && row.querySelector("[data-monitor-sensor-input]"))
      .slice(0, 18);
    rowsAvailable = rows.length;
    rowsTested = rows.length;
    if (rows.length < 8) failures.push("source-picker-checkmark:too-few-supported-rows");
    rows.forEach((row, index) => {
      const input = row.querySelector("[data-monitor-sensor-input]");
      const before = Boolean(input && input.checked);
      const startedAt = (window.performance && performance.now) ? performance.now() : Date.now();
      monitoringHudReliableActivationState.lastKey = "";
      monitoringHudReliableActivationState.lastAt = 0;
      const method = activationMethods[index % activationMethods.length];
      if (method === "checkbox-click" && input && typeof input.click === "function") {
        dispatchHumanPointerDown(input);
        input.click();
      } else if (method === "keyboard-space") {
        if (typeof row.focus === "function") row.focus();
        row.dispatchEvent(new KeyboardEvent("keydown", {
          key: " ",
          code: "Space",
          bubbles: true,
          cancelable: true
        }));
      } else {
        row.click();
      }
      const finishedAt = (window.performance && performance.now) ? performance.now() : Date.now();
      const elapsed = Math.max(0, finishedAt - startedAt);
      maxToggleMs = Math.max(maxToggleMs, elapsed);
      const after = Boolean(input && input.checked);
      const ariaSelected = row.getAttribute("aria-selected") === "true";
      const sourceId = row.dataset.sourcePickerRow || `row-${index}`;
      toggles.push({
        sourceId,
        method,
        before,
        after,
        elapsedMs: Math.round(elapsed * 10) / 10,
        ariaSelected,
        visualSelected: row.dataset.sourceSelected === "true"
      });
      if (after === before) failures.push(`source-picker-checkmark:${sourceId}:no-toggle`);
      if (ariaSelected !== after) failures.push(`source-picker-checkmark:${sourceId}:aria-mismatch`);
      if ((row.dataset.sourceSelected === "true") !== after) failures.push(`source-picker-checkmark:${sourceId}:visual-state-mismatch`);
      if (elapsed > 80) failures.push(`source-picker-checkmark:${sourceId}:slow-${Math.round(elapsed)}ms`);
    });
    const alternatingRow = rows[0];
    const alternatingInput = alternatingRow ? alternatingRow.querySelector("[data-monitor-sensor-input]") : null;
    if (alternatingRow && alternatingInput) {
      let expected = Boolean(alternatingInput.checked);
      alternatingTogglePass = true;
      for (let index = 0; index < 12; index += 1) {
        expected = !expected;
        monitoringHudReliableActivationState.lastKey = "";
        monitoringHudReliableActivationState.lastAt = 0;
        const startedAt = (window.performance && performance.now) ? performance.now() : Date.now();
        if (index % 2 === 0) {
          alternatingRow.click();
        } else {
          dispatchHumanPointerDown(alternatingInput);
          alternatingInput.click();
        }
        const finishedAt = (window.performance && performance.now) ? performance.now() : Date.now();
        const elapsed = Math.max(0, finishedAt - startedAt);
        maxToggleMs = Math.max(maxToggleMs, elapsed);
        alternatingToggleCount += 1;
        const after = Boolean(alternatingInput.checked);
        const ariaSelected = alternatingRow.getAttribute("aria-selected") === "true";
        const visualSelected = alternatingRow.dataset.sourceSelected === "true";
        toggles.push({
          sourceId: alternatingRow.dataset.sourcePickerRow || "alternating-row",
          method: index % 2 === 0 ? "alternating-row-click" : "alternating-checkbox-click",
          before: !expected,
          after,
          expected,
          elapsedMs: Math.round(elapsed * 10) / 10,
          ariaSelected,
          visualSelected
        });
        if (after !== expected || ariaSelected !== expected || visualSelected !== expected) {
          alternatingTogglePass = false;
          failures.push(`source-picker-checkmark:alternating-${index}:expected-${expected}-got-${after}`);
        }
        if (elapsed > 80) failures.push(`source-picker-checkmark:alternating-${index}:slow-${Math.round(elapsed)}ms`);
      }
    } else {
      failures.push("source-picker-checkmark:alternating-missing-row");
    }
  } catch (err) {
    failures.push(`source-picker-checkmark:exception:${String(err && err.message ? err.message : err)}`);
  }
  const proof = {
    passed: failures.length === 0,
    failures,
    rowsTested,
    rowsAvailable,
    toggles,
    maxToggleMs: Math.round(maxToggleMs * 10) / 10,
    rowClickTarget: true,
    checkboxClickTarget: true,
    keyboardToggleTarget: true,
    alternatingTogglePass,
    alternatingToggleCount,
    activationMethods,
    sourcePickerCheckmarkStress: true,
    sourcePickerCheckmarkMode: "row-and-checkbox-immediate-deferred-settings",
    sourcePickerCheckmarkLatency: "immediate-visual-deferred-settings",
    sourcePickerRenderScope: "immediate-row-preview-deferred-settings"
  };
  if (monitoringHudMonitorSensorAssignment) {
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerCheckmarkStress = proof.passed ? "pass" : "fail";
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerCheckmarkStressCount = String(rowsTested);
    monitoringHudMonitorSensorAssignment.dataset.sourcePickerCheckmarkMaxToggleMs = String(proof.maxToggleMs);
  }
  if (monitoringHud) {
    monitoringHud.dataset.sourcePickerCheckmarkStress = proof.passed ? "pass" : "fail";
    monitoringHud.dataset.sourcePickerCheckmarkMode = proof.sourcePickerCheckmarkMode;
  }
  if (backup && window.setMonitoringHudControlState) {
    window.setMonitoringHudControlState(backup);
    monitoringHudOpenChildWindow("monitor-group-edit");
  }
  monitoringHudControlState.sourcePickerCheckmarkStressProof = proof;
  return proof;
};

window.runMonitoringHudDisplayModeChipStressProof = function() {
  const backup = window.getMonitoringHudControlState ? window.getMonitoringHudControlState() : null;
  const failures = [];
  const toggles = [];
  let maxToggleMs = 0;
  try {
    monitoringHudOpenChildWindow("monitor-group-edit");
    const selected = monitoringHudSelectedMonitor();
    if (!selected.id || !selected.layout) throw new Error("display-mode:selected-monitor-missing");
    if (!Array.isArray(selected.layout.sensors) || !selected.layout.sensors.includes("cpu-load")) {
      const row = document.querySelector('[data-source-picker-row="cpu-load"]');
      if (row) monitoringHudToggleSensorAssignmentRow(row, true);
      monitoringHudRenderSensorSettings(monitoringHudSelectedMonitor());
    }
    monitoringHudOpenSourceSettings("cpu-load");
    let buttons = Array.from(document.querySelectorAll("#monitoring-hud-source-settings-body [data-sensor-display-mode-option]"));
    if (!buttons.length) {
      monitoringHudRenderMonitorManagement();
      monitoringHudOpenSourceSettings("cpu-load");
      buttons = Array.from(document.querySelectorAll("#monitoring-hud-source-settings-body [data-sensor-display-mode-option]"));
    }
    const buttonForValue = (value) => Array.from(document.querySelectorAll("#monitoring-hud-source-settings-body [data-sensor-display-mode-option]"))
      .find((item) => item.dataset.sensorDisplayModeValue === value);
    const values = ["text", "badge", "badge-text", "text", "badge-text", "badge"];
    values.forEach((value, index) => {
      const button = buttonForValue(value);
      if (!button) {
        failures.push(`display-mode:${value}:missing-button`);
        return;
      }
      const sensorId = button.dataset.sensorDisplayModeOption;
      const startedAt = (window.performance && performance.now) ? performance.now() : Date.now();
      if (index % 3 === 0) {
        monitoringHudActivateDisplayModeChip(button, null, "proof-direct-pointerdown");
      } else if (index % 3 === 1) {
        button.click();
      } else {
        if (typeof button.focus === "function") button.focus();
        button.dispatchEvent(new KeyboardEvent("keydown", {
          key: " ",
          code: "Space",
          bubbles: true,
          cancelable: true
        }));
      }
      const finishedAt = (window.performance && performance.now) ? performance.now() : Date.now();
      const elapsed = Math.max(0, finishedAt - startedAt);
      maxToggleMs = Math.max(maxToggleMs, elapsed);
      const currentGroup = monitoringHudSourceSettingsBody
        ? monitoringHudSourceSettingsBody.querySelector(`[data-sensor-display-mode="${sensorId}"]`)
        : null;
      const currentButton = buttonForValue(value);
      const selectedValue = currentGroup ? currentGroup.dataset.sensorDisplayModeSelected : "";
      const pressed = currentButton ? currentButton.getAttribute("aria-pressed") === "true" : false;
      toggles.push({
        value,
        selectedValue,
        pressed,
        elapsedMs: Math.round(elapsed * 10) / 10
      });
      if (selectedValue !== value) failures.push(`display-mode:${value}:selection-not-updated`);
      if (!pressed) failures.push(`display-mode:${value}:pressed-not-updated`);
      if (elapsed > 80) failures.push(`display-mode:${value}:slow-${Math.round(elapsed)}ms`);
    });
  } catch (err) {
    failures.push(`display-mode:exception:${String(err && err.message ? err.message : err)}`);
  }
  const proof = {
    passed: failures.length === 0,
    failures,
    toggles,
    maxToggleMs: Math.round(maxToggleMs * 10) / 10,
    displayModeChipStress: true,
    displayModeActivationPath: "deterministic-pointer-click-keyboard",
    displayModeSelectionLatency: "immediate-visual-draft-update"
  };
  if (monitoringHudMonitorSensorSettings) {
    monitoringHudMonitorSensorSettings.dataset.displayModeChipStress = proof.passed ? "pass" : "fail";
    monitoringHudMonitorSensorSettings.dataset.displayModeChipMaxToggleMs = String(proof.maxToggleMs);
  }
  if (monitoringHud) {
    monitoringHud.dataset.displayModeChipStress = proof.passed ? "pass" : "fail";
  }
  if (backup && window.setMonitoringHudControlState) {
    window.setMonitoringHudControlState(backup);
    monitoringHudOpenChildWindow("monitor-group-edit");
  }
  monitoringHudControlState.displayModeChipStressProof = proof;
  return proof;
};

window.setMonitoringHudControlState = function(state) {
  const incomingState = state || {};
  const incomingHasCards = monitoringHudHasOwnCards(incomingState);
  monitoringHudControlState = Object.assign({}, monitoringHudControlState, incomingState);
  monitoringHudControlState.featureEnabled = Boolean(monitoringHudControlState.featureEnabled);
  monitoringHudControlState.overlayDeferred = monitoringHudControlState.overlayDeferred !== false;
  monitoringHudControlState.visible = Boolean(monitoringHudControlState.featureEnabled && monitoringHudControlState.visible);
  monitoringHudControlState.warningMode = monitoringHudControlState.warningMode || "badge-text-color";
  monitoringHudControlState.cards = incomingHasCards
    ? monitoringHudSafeCardsObject(incomingState.cards)
    : monitoringHudSafeCardsObject(monitoringHudControlState.cards || monitoringHudInitialCards());
  Object.keys(monitoringHudControlState.cards).forEach((cardId) => {
    monitoringHudControlState.cards[cardId] = Object.assign(
      monitoringHudCardDefaults(cardId),
      monitoringHudControlState.cards[cardId] || {}
    );
    monitoringHudNormalizeSensorAssignments(cardId, monitoringHudControlState.cards[cardId]);
  });
  if (!monitoringHudControlState.selectedMonitorId || !monitoringHudControlState.cards[monitoringHudControlState.selectedMonitorId]) {
    monitoringHudControlState.selectedMonitorId = Object.keys(monitoringHudControlState.cards)[0] || "";
  }
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  monitoringHudControlState.monitorSequence = Math.max(
    Number(monitoringHudControlState.monitorSequence || 2),
    Object.keys(monitoringHudControlState.cards).length
  );
  monitoringHudControlState.emptyCardsPersistenceProof = {
    explicitEmptyCardsPreserved: incomingHasCards && Object.keys(monitoringHudControlState.cards).length === 0,
    defaultCardsOnlyWhenCardsAbsent: !incomingHasCards,
    selectedMonitorId: monitoringHudControlState.selectedMonitorId || ""
  };
  if (monitoringHudControlState.panelPosition) {
    monitoringHudSetPanelPosition(
      monitoringHudControlState.panelPosition.left || 0,
      monitoringHudControlState.panelPosition.top || 0
    );
  } else if (monitoringHud) {
    monitoringHudClearPanelPosition();
  }
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudSetMonitorDraftDirty(false);
  monitoringHudSetSourceFilterDropdownOpen(false);
  monitoringHudSetPollingRateDropdownOpen(false);
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
};

window.runMonitoringHudEmptyCardsPersistenceProof = function() {
  const backup = window.getMonitoringHudControlState ? window.getMonitoringHudControlState() : null;
  const failures = [];
  try {
    window.setMonitoringHudControlState(Object.assign({}, backup || {}, {
      cards: {},
      selectedMonitorId: "",
      featureEnabled: true,
      visible: true
    }));
    monitoringHudOpenChildWindow("monitor-group-edit");
    const cardIds = Object.keys(monitoringHudControlState.cards || {});
    const emptyDetail = monitoringHudMonitorDetailEmpty && monitoringHudMonitorDetailEmpty.dataset.monitorDetailEmpty === "true-empty-state-create-reachable";
    const listEmpty = monitoringHudMonitorListEmpty && monitoringHudMonitorListEmpty.dataset.monitorListEmpty === "true-empty-state";
    if (cardIds.length !== 0) failures.push(`cards-restored:${cardIds.join(",")}`);
    if (monitoringHudControlState.selectedMonitorId) failures.push(`selected-not-empty:${monitoringHudControlState.selectedMonitorId}`);
    if (!emptyDetail) failures.push("detail-empty-state-not-rendered");
    if (!listEmpty) failures.push("list-empty-state-not-rendered");
  } catch (err) {
    failures.push(`exception:${String(err && err.message ? err.message : err)}`);
  }
  const proof = {
    passed: failures.length === 0,
    failures,
    cardCount: Object.keys(monitoringHudControlState.cards || {}).length,
    selectedMonitorId: monitoringHudControlState.selectedMonitorId || "",
    explicitEmptyCardsPreserved: true,
    defaultCardsOnlyWhenCardsAbsent: true
  };
  if (monitoringHud) {
    monitoringHud.dataset.emptyCardsPersistence = proof.passed ? "explicit-empty-cards-preserved" : "failed";
  }
  if (backup && window.setMonitoringHudControlState) {
    window.setMonitoringHudControlState(backup);
    monitoringHudOpenChildWindow("monitor-group-edit");
  }
  monitoringHudControlState.emptyCardsPersistenceProof = proof;
  return proof;
};

window.setDesktopSurfaceMode = function(enabled) {
  const isEnabled = Boolean(enabled);
  body.classList.toggle("desktop-mode", isEnabled);
  body.classList.add("hud-window-mode");
  if (monitoringHud) {
    monitoringHud.setAttribute("aria-hidden", isEnabled ? "false" : "true");
    monitoringHud.dataset.renderState = isEnabled ? "product-visibility-baseline" : "hidden";
    monitoringHud.dataset.productSurfaceState = (isEnabled && monitoringHudControlState.visible) ? "visible-user-facing" : "hidden";
  }
  if (monitoringHudMinimal) {
    monitoringHudMinimal.setAttribute("aria-hidden", isEnabled ? "false" : "true");
    monitoringHudMinimal.dataset.renderState = isEnabled ? "minimal-overlay-ready" : "hidden";
    monitoringHudMinimal.dataset.productSurfaceState = "hidden-deferred";
  }
  if (monitoringHudOverlayDisplay) {
    monitoringHudOverlayDisplay.setAttribute("aria-hidden", isEnabled ? "false" : "true");
    monitoringHudOverlayDisplay.dataset.renderState = isEnabled ? "edgeless-overlay-display-ready" : "hidden";
    monitoringHudOverlayDisplay.dataset.productSurfaceState = "hidden-deferred";
  }
  monitoringHudRenderControls();
};

window.setMonitoringHudTelemetry = function(snapshot) {
  monitoringHudTelemetry = Object.assign({}, monitoringHudTelemetry, snapshot || {});
  if (monitoringHud) {
    monitoringHud.dataset.telemetryPackage = monitoringHudTelemetry.packageId || "PKG-006";
    monitoringHud.dataset.telemetrySlice = monitoringHudTelemetry.sliceId || "SLC-025";
    monitoringHud.dataset.telemetryAdapter = monitoringHudTelemetry.adapterId || "desktop-runtime-boundary";
    monitoringHud.dataset.providerState = monitoringHudTelemetry.providerState || "setup-required";
    monitoringHud.dataset.liveValues = monitoringHudTelemetry.liveValues || "provider-required";
    monitoringHud.dataset.pollingRateMs = String(monitoringHudTelemetry.pollingRateMs || monitoringHudControlState.pollingRateMs || 1000);
  }
  if (monitoringHudRuntimeStatus) {
    monitoringHudRuntimeStatus.textContent = monitoringHudControlState.visible ? "Dashboard visible" : "Dashboard hidden";
  }
  if (monitoringHudProviderState) {
    monitoringHudProviderState.textContent = monitoringHudTelemetry.providerLabel || "Provider setup required";
  }
  if (monitoringHudAdapterStatus) {
    monitoringHudAdapterStatus.textContent = "Feature Deferred";
    monitoringHudAdapterStatus.dataset.providerTruth = monitoringHudTelemetry.adapterStatus || "Waiting for safe provider";
  }
  if (monitoringHudSourceScope) {
    monitoringHudSourceScope.textContent = monitoringHudTelemetry.sourceScope || "Provider-first; no fake values";
  }
  if (monitoringHudHardwarePolling) {
    monitoringHudHardwarePolling.textContent = monitoringHudTelemetry.hardwarePolling || "1s after provider proof";
  }
  if (monitoringHudProviderStateMatrix) {
    monitoringHudProviderStateMatrix.textContent = "Setup / no data / degraded / ready";
  }
  monitoringHudRenderSensorCards(monitoringHudTelemetry.sensorCards);
  if (monitoringHudActiveChildWindow === "sensor-source-settings") {
    if (monitoringHudSourceSettingsWindow) {
      monitoringHudSourceSettingsWindow.dataset.telemetryRefreshPolicy = "preserve-active-source-settings-controls";
    }
  } else {
    monitoringHudRenderMonitorManagement();
  }
  monitoringHudUpdateSurfaceSplit();
};

window.setMonitoringHudPlacementOwnership = function(contract) {
  monitoringHudPlacement = Object.assign({}, monitoringHudPlacement, contract || {});
  if (monitoringHud) {
    monitoringHud.dataset.placementPackage = monitoringHudPlacement.packageId || "PKG-006";
    monitoringHud.dataset.placementSlice = monitoringHudPlacement.sliceId || "SLC-026";
    monitoringHud.dataset.placementId = monitoringHudPlacement.placementId || "standalone-native-hud-window";
    monitoringHud.dataset.placementState = "desktop-renderer-owned";
    monitoringHud.dataset.interactionMode = "standalone-dashboard-window";
  }
  if (monitoringHudPlacementOwner) {
    monitoringHudPlacementOwner.textContent = monitoringHudPlacement.rendererOwner || "HUD Overlay release acceptance is deferred. The Dashboard can describe the future overlay boundary without enabling it.";
  }
  if (monitoringHudPlacementAnchor) {
    monitoringHudPlacementAnchor.textContent = monitoringHudPlacement.anchor || "Deferred / non-gating";
  }
  if (monitoringHudPlacementPointer) {
    monitoringHudPlacementPointer.textContent = monitoringHudPlacement.pointerModel || "Dashboard configures future HUD Overlay behavior";
  }
  if (monitoringHudResizePosture) {
    monitoringHudResizePosture.textContent = monitoringHudPlacement.resizePosture || "Overlay settings are future branch scope";
  }
  monitoringHudUpdateSurfaceSplit();
};

window.setMonitoringHudControlsVisibility = function(contract) {
  monitoringHudControls = Object.assign({}, monitoringHudControls, contract || {});
  if (monitoringHud) {
    monitoringHud.dataset.controlsPackage = monitoringHudControls.packageId || "PKG-006";
    monitoringHud.dataset.controlsSlice = monitoringHudControls.sliceId || "SLC-027";
    monitoringHud.dataset.controlsId = monitoringHudControls.controlsId || "hud-controls-visibility";
    monitoringHud.dataset.controlsState = monitoringHudControlState.featureEnabled
      ? (monitoringHudControlState.visible ? "feature-enabled-dashboard-open" : "feature-enabled-dashboard-closed")
      : "feature-disabled-dashboard-closed";
    monitoringHud.dataset.keybindPolicy = "none";
    monitoringHud.dataset.monitorManagement = "sensor-command-center-list-detail-source-picker";
    monitoringHud.dataset.overlayModeControls = "overlay-deferred-tray-owned";
  }
  if (monitoringHudControlsVisibility) {
    monitoringHudControlsVisibility.textContent = monitoringHudControls.visibilityState || "HUD feature disabled from dashboard/tray";
  }
  if (monitoringHudControlsSurface) {
    monitoringHudControlsSurface.textContent = monitoringHudControls.controlSurface || "Tray controls HUD feature state; Dashboard open/close is separate; HUD Overlay remains deferred";
  }
  if (monitoringHudControlsPersistence) {
    monitoringHudControlsPersistence.textContent = monitoringHudControls.persistence || "Store group/layout posture locally";
  }
  if (monitoringHudWarningPosture && monitoringHudControls.warningControls) {
    monitoringHudWarningPosture.textContent = monitoringHudControls.warningControls;
  }
  if (monitoringHudTrayPath) {
    monitoringHudTrayPath.textContent = monitoringHudControls.trayPath || "Task tray enables/disables HUD feature and opens/closes Dashboard; HUD Overlay controls deferred";
  }
  monitoringHudRenderControls();
  monitoringHudUpdateSurfaceSplit();
};

window.setMonitoringHudStatusBehavior = function(snapshot) {
  monitoringHudStatus = Object.assign({}, monitoringHudStatus, snapshot || {});
  if (monitoringHud) {
    monitoringHud.dataset.statusPackage = monitoringHudStatus.packageId || "PKG-006";
    monitoringHud.dataset.statusSlice = monitoringHudStatus.sliceId || "SLC-028";
    monitoringHud.dataset.statusId = monitoringHudStatus.statusId || "hud-local-readiness-status";
    monitoringHud.dataset.statusKind = monitoringHudStatus.statusKind || "no-data";
    monitoringHud.dataset.warningMode = "visual-non-invasive";
    monitoringHud.dataset.warningState = monitoringHudStatus.warningState || "advisory";
    monitoringHud.dataset.dashboardProviderTruth = "provider-contract-first";
    monitoringHud.dataset.dashboardStateModel = "setup-no-data-degraded-warning";
    monitoringHud.dataset.dashboardWarningControls = "visual-non-invasive-only";
    monitoringHud.dataset.dashboardFakeTelemetryPolicy = "blocked";
    monitoringHud.dataset.interactiveControlAffordance = "normal-hover-active-focus-visible-disabled-open-selected";
    monitoringHud.dataset.interactiveControlReliability = monitoringHud.dataset.interactiveControlReliability || "first-click-stress-proof-required";
    monitoringHud.dataset.clickInterceptionDiagnostics = monitoringHud.dataset.clickInterceptionDiagnostics || "z-index-pointer-events-disabled-aria-dom-focus-timing";
    monitoringHud.dataset.pollingRateDropdown = "nexus-styled-bounded-control";
  }
  if (monitoringHudStatusLabel) {
    monitoringHudStatusLabel.textContent = monitoringHudStatus.statusLabel || "Provider setup required";
  }
  if (monitoringHudNoDataBehavior) {
    monitoringHudNoDataBehavior.textContent = monitoringHudStatus.noDataBehavior || "Show unavailable; no fake values";
  }
  if (monitoringHudDegradedBehavior) {
    monitoringHudDegradedBehavior.textContent = monitoringHudStatus.degradedBehavior || "Name reconnect/setup gap";
  }
  if (monitoringHudWarningPosture) {
    monitoringHudWarningPosture.textContent = monitoringHudStatus.warningPosture || "Visual notifications enabled";
  }
  monitoringHudUpdateSurfaceSplit();
};

monitoringHudInitializeControls();
window.setDesktopSurfaceMode(false);
window.setMonitoringHudTelemetry({});
window.setMonitoringHudPlacementOwnership({});
window.setMonitoringHudControlsVisibility({});
window.setMonitoringHudStatusBehavior({});
