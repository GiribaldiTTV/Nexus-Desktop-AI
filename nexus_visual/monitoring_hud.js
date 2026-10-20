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
  statusLabel: "Waiting for Dashboard status",
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
let monitoringHudOverlayProfileEditorGeneration = 0;
let monitoringHudOverlayProfileDraftGeneration = 0;
let monitoringHudOverlayProfilePendingAction = null;
let monitoringHudOverlayProfileResolvingAction = null;

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
  const currentRecordingState = monitoringHudRecordingState();
  if (["recording", "saving"].includes(currentRecordingState)) {
    return false;
  }
  if (currentRecordingState === "paused") {
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
    return false;
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
  const path = String(safeResult.csvPath || "");
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

function monitoringHudOverlayProfileEditorContext(state) {
  const cards = monitoringHudSafeCardsObject(state.cards || {});
  const profiles = monitoringHudSafeOverlayProfilesObject(state.overlayProfiles);
  const profileIds = Object.keys(profiles).filter((profileId) => {
    const profile = profiles[profileId];
    return profile && typeof profile === "object" && !Array.isArray(profile);
  }).sort();
  return JSON.stringify({
    activeProfileId: String(state.activeOverlayProfileId || "").trim(),
    defaultDeleted: Boolean(state.overlayProfileDefaultDeletedByUser),
    monitorIds: monitoringHudStableMonitorIds(cards).sort(),
    profiles: profileIds.map((profileId) => {
      const profile = profiles[profileId];
      return [
        profileId,
        String(profile.id || profileId).trim(),
        String(profile.name || "Overlay Profile").trim() || "Overlay Profile",
        monitoringHudUniqueValidMonitorIds(profile.monitorIds, cards),
        String(profile.displayMode || "monitor-cards").trim() || "monitor-cards"
      ];
    })
  });
}

function monitoringHudInvalidateOverlayProfileEditorAction() {
  monitoringHudOverlayProfileEditorGeneration += 1;
  monitoringHudOverlayProfilePendingAction = null;
  monitoringHudOverlayProfileResolvingAction = null;
  monitoringHudSetOverlayProfileUnsavedGuard(false);
}

function monitoringHudOverlayProfileActionIsCurrent(action) {
  return Boolean(
    action
    && action === monitoringHudOverlayProfilePendingAction
    && action.editorGeneration === monitoringHudOverlayProfileEditorGeneration
    && action.draftGeneration === monitoringHudOverlayProfileDraftGeneration
    && monitoringHudActiveChildWindow === "overlay-profile-settings"
    && monitoringHudOverlayProfileDetailOpen
    && action.draftId === monitoringHudOverlayProfileDraftId
    && action.selectedId === monitoringHudOverlayProfileWindowSelectedId
    && action.pendingCreateId === (monitoringHudOverlayProfilePendingCreate ? monitoringHudOverlayProfilePendingCreate.id : "")
  );
}

function monitoringHudOverlayProfileActionTargetExists(action) {
  if (action.type === "close" || action.type === "create") return true;
  return action.type === "editorSelect"
    && Boolean((monitoringHudControlState.overlayProfiles || {})[action.profileId]);
}

function monitoringHudGuardOverlayProfileAction(type, profileId = "") {
  if (monitoringHudOverlayProfilePendingAction) return true;
  if (monitoringHudActiveChildWindow !== "overlay-profile-settings"
      || !monitoringHudOverlayProfileDetailOpen
      || !monitoringHudOverlayProfileDraftDirty()) return false;
  monitoringHudOverlayProfileEditorGeneration += 1;
  monitoringHudOverlayProfilePendingAction = {
    type,
    profileId,
    editorGeneration: monitoringHudOverlayProfileEditorGeneration,
    draftGeneration: monitoringHudOverlayProfileDraftGeneration,
    draftId: monitoringHudOverlayProfileDraftId,
    selectedId: monitoringHudOverlayProfileWindowSelectedId,
    pendingCreateId: monitoringHudOverlayProfilePendingCreate ? monitoringHudOverlayProfilePendingCreate.id : ""
  };
  monitoringHudSetOverlayProfileWindowDropdownOpen(false);
  monitoringHudSetOverlayProfileUnsavedGuard(true);
  return true;
}

function monitoringHudResolveOverlayProfileUnsavedGuard(saveDraft) {
  const action = monitoringHudOverlayProfilePendingAction;
  if (!action || monitoringHudOverlayProfileResolvingAction) return false;
  if (!monitoringHudOverlayProfileActionIsCurrent(action)
      || !monitoringHudOverlayProfileActionTargetExists(action)) {
    monitoringHudInvalidateOverlayProfileEditorAction();
    return false;
  }
  monitoringHudOverlayProfileResolvingAction = action;
  let resolved = false;
  try {
    resolved = saveDraft ? monitoringHudSaveOverlayProfileDraft() : monitoringHudDiscardOverlayProfileDraft();
  } finally {
    if (monitoringHudOverlayProfileResolvingAction === action) monitoringHudOverlayProfileResolvingAction = null;
  }
  if (!resolved) {
    if (monitoringHudOverlayProfileActionIsCurrent(action)) monitoringHudSetOverlayProfileUnsavedGuard(true);
    return false;
  }
  // Save/Discard may replace this draft once; any other lifecycle change cancels the continuation.
  if (monitoringHudOverlayProfilePendingAction !== action
      || action.editorGeneration !== monitoringHudOverlayProfileEditorGeneration
      || monitoringHudOverlayProfileDraftGeneration !== action.draftGeneration + 1
      || monitoringHudActiveChildWindow !== "overlay-profile-settings"
      || !monitoringHudOverlayProfileActionTargetExists(action)) {
    if (monitoringHudOverlayProfilePendingAction === action) monitoringHudInvalidateOverlayProfileEditorAction();
    return false;
  }
  monitoringHudOverlayProfilePendingAction = null;
  monitoringHudSetOverlayProfileUnsavedGuard(false);
  if (action.type === "editorSelect") return monitoringHudSelectOverlayProfileForWindow(action.profileId);
  if (action.type === "create") return monitoringHudCreateOverlayProfile();
  if (action.type === "close") return monitoringHudCloseChildWindow({ force: true });
  return false;
}

function monitoringHudSetOverlayProfileDraftFromProfile(profile) {
  const action = monitoringHudOverlayProfileResolvingAction;
  const resolvingThisDraft = action
    && action === monitoringHudOverlayProfilePendingAction
    && action.editorGeneration === monitoringHudOverlayProfileEditorGeneration
    && action.draftGeneration === monitoringHudOverlayProfileDraftGeneration;
  monitoringHudOverlayProfileDraftGeneration += 1;
  if (!resolvingThisDraft) {
    monitoringHudOverlayProfilePendingAction = null;
    monitoringHudOverlayProfileResolvingAction = null;
    monitoringHudSetOverlayProfileUnsavedGuard(false);
  }
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
  const normalizedProfileId = String(profileId || "").trim();
  if (normalizedProfileId && normalizedProfileId === monitoringHudOverlayProfileWindowSelectedId) {
    monitoringHudSetOverlayProfileWindowDropdownOpen(false);
    return true;
  }
  if (monitoringHudOverlayProfilePendingAction) return false;
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  if (!monitoringHudControlState.overlayProfiles[normalizedProfileId]) return false;
  if (monitoringHudGuardOverlayProfileAction("editorSelect", normalizedProfileId)) return false;
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
  if (monitoringHudOverlayProfilePendingAction) return false;
  monitoringHudNormalizeOverlayProfileState(monitoringHudControlState);
  if (monitoringHudGuardOverlayProfileAction("create")) return false;
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
  monitoringHudOverlayProfileUnsavedGuard.dataset.pendingOverlayProfileAction = isOpen && monitoringHudOverlayProfilePendingAction
    ? monitoringHudOverlayProfilePendingAction.type
    : "";
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
  const action = monitoringHudOverlayProfilePendingAction;
  if (!action || monitoringHudOverlayProfileResolvingAction) return false;
  if (!monitoringHudOverlayProfileActionIsCurrent(action)) {
    monitoringHudInvalidateOverlayProfileEditorAction();
    return false;
  }
  monitoringHudInvalidateOverlayProfileEditorAction();
  const editorGeneration = monitoringHudOverlayProfileEditorGeneration;
  const draftGeneration = monitoringHudOverlayProfileDraftGeneration;
  const selectedId = monitoringHudOverlayProfileWindowSelectedId;
  const pendingCreateId = monitoringHudOverlayProfilePendingCreate ? monitoringHudOverlayProfilePendingCreate.id : "";
  monitoringHudRenderControls();
  window.requestAnimationFrame(() => {
    if (editorGeneration !== monitoringHudOverlayProfileEditorGeneration
        || draftGeneration !== monitoringHudOverlayProfileDraftGeneration
        || monitoringHudOverlayProfilePendingAction
        || monitoringHudActiveChildWindow !== "overlay-profile-settings"
        || selectedId !== monitoringHudOverlayProfileWindowSelectedId
        || pendingCreateId !== (monitoringHudOverlayProfilePendingCreate ? monitoringHudOverlayProfilePendingCreate.id : "")) return;
    monitoringHudSetOverlayProfileUnsavedGuard(false);
    monitoringHudRenderControls();
  });
  return true;
}

function monitoringHudSaveOverlayProfileAndClose() {
  return monitoringHudResolveOverlayProfileUnsavedGuard(true);
}

function monitoringHudDiscardOverlayProfileAndClose() {
  return monitoringHudResolveOverlayProfileUnsavedGuard(false);
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
const monitoringHudSensorRenderLimit = 120;
let monitoringHudDragInProgress = false;
let monitoringHudPanelPositionFrame = 0;
let monitoringHudQueuedPanelPosition = null;
let monitoringHudActiveChildWindow = "";
let monitoringHudPendingDeleteMonitorId = "";
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
  return sourceDefinitions;
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
  if (monitoringHudActiveChildWindow === "overlay-profile-settings" && kind !== "overlay-profile-settings") {
    monitoringHudInvalidateOverlayProfileEditorAction();
  }
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
  let removedNewMonitor = false;
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
      removedNewMonitor = true;
    }
  }
  monitoringHudPendingDeleteMonitorId = "";
  monitoringHudSetMonitorDraftDirty(false);
  if (removedNewMonitor) monitoringHudMarkChanged();
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
  monitoringHudSensorPreview.textContent = `${selectedCount} selected source${selectedCount === 1 ? "" : "s"}. Showing ${renderedCount} of ${totalCount} filtered sources; ${supportedCount} supported and ${deferredCount} provider-required/deferred. Source rows expose provider, device, category, metric, sensor instance breadcrumbs, and their own Settings buttons.`;
}

function monitoringHudRenderSensorAssignment(selected) {
  if (!monitoringHudMonitorSensorAssignment) return;
  const layout = selected && selected.layout ? monitoringHudNormalizeSensorAssignments(selected.id, selected.layout) : null;
  const assigned = new Set(Array.isArray(layout && layout.sensors) ? layout.sensors : []);
  monitoringHudMonitorSensorAssignment.innerHTML = "";
  monitoringHudMonitorSensorAssignment.dataset.sensorAssignment = "sensor-library-source-picker";
  monitoringHudMonitorSensorAssignment.dataset.sourcePickerVisual = "nexus-faceted-searchable-rows";
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
    monitoringHudEditMonitor.disabled = false;
    monitoringHudEditMonitor.setAttribute("aria-disabled", "false");
  }
}

function monitoringHudOpenChildWindow(kind) {
  if (kind === "overlay-profile-settings") monitoringHudInvalidateOverlayProfileEditorAction();
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
            : kind === "monitor-group-edit" && Object.keys(monitoringHudControlState.cards || {}).length === 0
              ? monitoringHudMonitorEmptyCreate
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
  if (!options.force && monitoringHudActiveChildWindow === "overlay-profile-settings" && monitoringHudGuardOverlayProfileAction("close")) {
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
  let removedNewMonitor = false;
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
      removedNewMonitor = true;
    }
  }
  monitoringHudSetMonitorDraftDirty(false);
  if (removedNewMonitor) {
    monitoringHudMarkChanged();
    monitoringHudRenderMonitorManagement();
  }
  const preContinuationSelection = monitoringHudControlState.selectedMonitorId;
  monitoringHudRunPendingGuardAction(pendingAction);
  if (
    removedNewMonitor
    && pendingAction.type === "select"
    && monitoringHudControlState.cards
    && Object.prototype.hasOwnProperty.call(monitoringHudControlState.cards, pendingAction.cardId)
    && monitoringHudControlState.cards[pendingAction.cardId]
    && monitoringHudControlState.selectedMonitorId === pendingAction.cardId
    && monitoringHudControlState.selectedMonitorId !== preContinuationSelection
  ) {
    monitoringHudMarkChanged();
  }
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
    monitoringHud.dataset.monitorManagementScrollbars = "nexus-styled-child-list-detail-sensor-panes";
    monitoringHud.dataset.monitorManagementToolbar = "compact-search-summary-list-header-create";
    monitoringHud.dataset.monitorDeletePlacement = "detail-pane-bottom-danger-zone";
    monitoringHud.dataset.manageWindowSizing = "taller-default-bounded-resizable";
    monitoringHud.dataset.firstOpenFlickerGuard = "native-opacity-guard-stable-first-open";
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
    monitoringHudMonitorListSummary.textContent = monitorCount === 0
      ? "No monitors yet. Open Manage Monitors to create one."
      : `${monitorCount} Monitor Groups configured with ${assignedSensorCount} supported source assignment${assignedSensorCount === 1 ? "" : "s"}. Manage opens list, create, edit, delete, and sensor controls.`;
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

window.setMonitoringHudControlState = function(state) {
  const previousProfileContext = monitoringHudOverlayProfileEditorContext(monitoringHudControlState);
  const incomingState = state || {};
  const incomingHasCards = monitoringHudHasOwnCards(incomingState);
  const monitorDraftOwnerId = monitoringHudDraftOriginalMonitorId;
  const preserveMonitorDraft = monitoringHudUnsavedMonitorDirty
    && !incomingHasCards
    && monitorDraftOwnerId
    && monitoringHudControlState.selectedMonitorId === monitorDraftOwnerId
    && Object.prototype.hasOwnProperty.call(monitoringHudControlState.cards || {}, monitorDraftOwnerId)
    && (!Object.prototype.hasOwnProperty.call(incomingState, "selectedMonitorId")
      || incomingState.selectedMonitorId === monitorDraftOwnerId);
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
  if (previousProfileContext !== monitoringHudOverlayProfileEditorContext(monitoringHudControlState)) {
    monitoringHudInvalidateOverlayProfileEditorAction();
  }
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
  if (
    !preserveMonitorDraft
    || monitoringHudControlState.selectedMonitorId !== monitorDraftOwnerId
    || !Object.prototype.hasOwnProperty.call(monitoringHudControlState.cards, monitorDraftOwnerId)
  ) {
    monitoringHudSetMonitorDraftDirty(false);
  }
  monitoringHudSetSourceFilterDropdownOpen(false);
  monitoringHudSetPollingRateDropdownOpen(false);
  monitoringHudApplyCardLayout();
  monitoringHudRenderControls();
  monitoringHudMarkChanged();
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
    monitoringHudStatusLabel.textContent = monitoringHudStatus.statusLabel || "Dashboard status unavailable";
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
