(() => {
  const commandPrefix = "NEXUS_AI_CONTROL_CENTER_COMMAND:";
  const stateTaxonomyContract = "ai-dashboard-ai-control-center-state-taxonomy-v1";
  const dashboardViewModelContract = "ai-dashboard-provider-state-view-model-v1";
  const requiredStateTaxonomyStates = [
    "no-provider-fail-closed",
    "provider-unavailable",
    "stale-state-fail-closed",
    "failed-check-fail-closed",
    "retry-local-check-only",
    "recovery-local-only",
    "blocked-action",
    "unavailable-capability",
    "degraded-no-provider",
  ];
  let providerState = {};
  let scrollbarDrag = null;
  let currentReadinessReportText = "";
  const windowControlStates = {
    minimize: "active",
    maximizeRestore: "hidden",
    close: "active",
  };
  const windowControlDefaults = {
    minimize: {
      id: "ai-control-center-minimize-action",
      command: "minimize",
      activeLabel: "Minimize AI Dashboard",
      blockedLabel: "Minimize AI Dashboard blocked",
      hiddenLabel: "Minimize AI Dashboard hidden",
    },
    maximizeRestore: {
      id: "ai-control-center-maximize-action",
      command: "maximize-restore",
      activeLabel: "Maximize AI Dashboard",
      activeMaximizedLabel: "Restore AI Dashboard",
      blockedLabel: "Maximize or restore AI Dashboard blocked",
      hiddenLabel: "Maximize or restore AI Dashboard hidden until future implementation",
    },
    close: {
      id: "ai-control-center-close-action",
      command: "close",
      activeLabel: "Close AI Dashboard",
      blockedLabel: "Close AI Dashboard blocked",
      hiddenLabel: "Close AI Dashboard hidden",
    },
  };
  const validWindowControlStates = new Set(["hidden", "blocked", "active"]);
  const domainDoorwayCommands = {
    "control-center": "open-control-center-child-window",
    "readiness-diagnostics": "open-readiness-diagnostics-child-window",
    "capabilities-maintenance": "open-maintenance-lifecycle-child-window",
  };

  const byId = (id) => document.getElementById(id);
  const setText = (id, value) => {
    const target = byId(id);
    if (target) {
      target.textContent = String(value || "");
    }
  };
  const emitCommand = (name) => {
    console.info(`${commandPrefix}${name}`);
  };
  const formatReportItems = (items, keys = ["label"]) => {
    const list = Array.isArray(items) ? items : [];
    if (!list.length) {
      return "None";
    }
    return list
      .map((item) => {
        if (item && typeof item === "object") {
          return keys
            .map((key) => String(item[key] || "").trim())
            .filter(Boolean)
            .join(" - ");
        }
        return String(item || "").trim();
      })
      .filter(Boolean)
      .join("; ");
  };
  const buildReportText = (report) => {
    const title = String(report.title || "Local AI Readiness Report");
    const lines = [
      title,
      "",
      `Summary: ${String(report.summary || "No local readiness report is available.")}`,
      `Useful outcome: ${String(report.usefulOutcome || "Not available")}`,
      `Provider-visible data: ${String(report.providerVisibleData || "none")}`,
      `Copy/persistence: ${String(report.copyMode || "clipboard-only-user-initiated")} / ${String(report.persistence || "view-only-no-file-persistence")}`,
      "",
      `Ready: ${formatReportItems(report.readyConditions, ["label", "evidence"])}`,
      `Missing: ${formatReportItems(report.missingRequirements, ["label", "reason"])}`,
      `Blocked: ${formatReportItems(report.blockedPaths, ["label", "state", "gate"])}`,
      `Evidence checked: ${formatReportItems(report.localEvidenceChecked)}`,
      `Safe next steps: ${formatReportItems(report.safeNextSteps)}`,
      `Trust boundaries: ${formatReportItems(report.trustBoundaries)}`,
    ];
    return lines.join("\n");
  };
  const setReportCopyEnabled = (enabled) => {
    const button = byId("ai-control-center-copy-report-action");
    if (!button) {
      return;
    }
    button.disabled = !enabled;
    button.setAttribute("aria-disabled", enabled ? "false" : "true");
  };
  const copyTextThroughLocalSurface = (text) => {
    const copySurface = document.createElement("textarea");
    copySurface.value = text;
    copySurface.setAttribute("readonly", "");
    copySurface.style.position = "fixed";
    copySurface.style.left = "-9999px";
    copySurface.style.top = "0";
    document.body.appendChild(copySurface);
    copySurface.focus();
    copySurface.select();
    const copied = document.execCommand("copy");
    copySurface.remove();
    return copied;
  };
  const renderReadinessReport = (report) => {
    const normalized = report && typeof report === "object" ? report : {};
    const guardClosed = (
      normalized.providerVisibleData === "none"
      && normalized.sentToProvider === false
      && normalized.canAcceptPrompts === false
      && normalized.promptSendPosture === "prompt-send-disabled"
      && normalized.networkEgressState === "network-egress-blocked"
      && normalized.memoryIndexingState === "memory-indexing-disabled"
    );
    const body = byId("ai-control-center-report-body");
    if (!guardClosed) {
      currentReadinessReportText = "";
      setText("ai-control-center-report-state", "Blocked by boundary mismatch");
      setText("ai-control-center-report-summary", "Report blocked because local trust-boundary proof is inconsistent.");
      if (body) {
        body.hidden = true;
      }
      setReportCopyEnabled(false);
      requestAnimationFrame(syncDashboardLayout);
      return false;
    }

    currentReadinessReportText = buildReportText(normalized);
    setText("ai-control-center-report-state", "Generated locally");
    setText("ai-control-center-report-persistence", "View-only; copy is USER initiated");
    setText("ai-control-center-report-summary", normalized.summary || "Local readiness report generated.");
    setText("ai-control-center-report-ready", formatReportItems(normalized.readyConditions, ["label", "evidence"]));
    setText("ai-control-center-report-missing", formatReportItems(normalized.missingRequirements, ["label", "reason"]));
    setText("ai-control-center-report-blocked", formatReportItems(normalized.blockedPaths, ["label", "state", "gate"]));
    setText("ai-control-center-report-evidence", formatReportItems(normalized.localEvidenceChecked));
    setText("ai-control-center-report-next", formatReportItems(normalized.safeNextSteps));
    setText("ai-control-center-report-boundary", formatReportItems(normalized.trustBoundaries));
    if (body) {
      body.hidden = false;
    }
    setReportCopyEnabled(true);
    requestAnimationFrame(syncDashboardLayout);
    return true;
  };
  const copyReadinessReport = async () => {
    if (!currentReadinessReportText) {
      setText("ai-control-center-report-state", "Generate report before copying");
      return false;
    }
    try {
      if (copyTextThroughLocalSurface(currentReadinessReportText)) {
        setText("ai-control-center-report-state", "Copied locally");
        return true;
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(currentReadinessReportText);
      } else {
        throw new Error("clipboard unavailable");
      }
      setText("ai-control-center-report-state", "Copied locally");
      return true;
    } catch (error) {
      setText("ai-control-center-report-state", "Copy unavailable; report remains visible");
      return false;
    }
  };
  const attachActivationHandler = (element, handler) => {
    if (!element || typeof handler !== "function") {
      return;
    }
    let lastActivationAt = 0;
    const activate = (event) => {
      const now = Date.now();
      if (now - lastActivationAt < 90) {
        return;
      }
      lastActivationAt = now;
      handler(event);
    };
    element.addEventListener("click", activate);
    element.addEventListener("pointerup", activate);
  };
  const applyDomainDoorwayState = () => {
    document.querySelectorAll("[data-category-doorway]").forEach((button) => {
      const doorway = button.dataset.categoryDoorway || "";
      const command = domainDoorwayCommands[doorway] || "";
      button.removeAttribute("title");
      if (!command) {
        button.disabled = true;
        button.setAttribute("aria-disabled", "true");
        button.dataset.actionState = "blocked";
        button.dataset.launchTarget = "blocked";
        button.dataset.launchWindowKind = "blocked";
        return;
      }
      button.disabled = false;
      button.setAttribute("aria-disabled", "false");
      button.dataset.actionState = "ready";
      button.dataset.launchTarget = doorway;
      button.dataset.launchCommand = command;
      if (!button.dataset.launchWindowKind || button.dataset.launchWindowKind === "deferred-detached-child") {
        button.dataset.launchWindowKind = doorway === "readiness-diagnostics" ? "external-unique" : "exclusive-child";
      }
    });
  };
  const stripNativeTooltips = () => {
    const surface = byId("monitoring-hud");
    if (!surface) {
      return;
    }
    surface.querySelectorAll("[title]").forEach((element) => {
      element.removeAttribute("title");
    });
  };
  const observeNativeTooltipDrift = () => {
    const surface = byId("monitoring-hud");
    if (!surface || !window.MutationObserver) {
      return;
    }
    const observer = new MutationObserver(() => {
      stripNativeTooltips();
    });
    observer.observe(surface, {
      attributes: true,
      attributeFilter: ["title"],
      childList: true,
      subtree: true,
    });
  };

  const normalizeWindowControlState = (value) => (
    validWindowControlStates.has(value) ? value : "blocked"
  );

  const hydrateWindowControlStatesFromMarkup = () => {
    Object.entries(windowControlDefaults).forEach(([key, config]) => {
      const button = byId(config.id);
      if (!button) {
        return;
      }
      windowControlStates[key] = normalizeWindowControlState(
        button.dataset.windowControlState || windowControlStates[key],
      );
      button.dataset.windowControlKey = key;
      button.dataset.windowControlCommand = button.dataset.windowControlCommand || config.command;
      button.removeAttribute("title");
    });
  };

  const syncSingleWindowControlState = (key, windowState) => {
    const config = windowControlDefaults[key];
    const button = config ? byId(config.id) : null;
    if (!button) {
      return;
    }
    const controlState = normalizeWindowControlState(windowControlStates[key]);
    button.dataset.windowControlState = controlState;
    button.removeAttribute("title");

    if (key === "maximizeRestore") {
      button.dataset.windowState = controlState === "active" ? windowState : controlState;
    }

    if (controlState === "hidden") {
      button.hidden = true;
      button.disabled = true;
      button.tabIndex = -1;
      button.setAttribute("aria-hidden", "true");
      button.setAttribute("aria-disabled", "true");
      button.setAttribute("aria-label", config.hiddenLabel);
      button.removeAttribute("aria-pressed");
      return;
    }

    button.hidden = false;
    button.removeAttribute("aria-hidden");
    if (controlState === "blocked") {
      button.disabled = true;
      button.tabIndex = -1;
      button.setAttribute("aria-disabled", "true");
      button.setAttribute("aria-label", config.blockedLabel);
      button.removeAttribute("aria-pressed");
      return;
    }

    button.disabled = false;
    button.tabIndex = 0;
    button.removeAttribute("aria-disabled");
    if (key === "maximizeRestore") {
      button.setAttribute("aria-pressed", windowState === "maximized" ? "true" : "false");
      button.setAttribute(
        "aria-label",
        windowState === "maximized" ? config.activeMaximizedLabel : config.activeLabel,
      );
      return;
    }
    button.setAttribute("aria-label", config.activeLabel);
  };

  const syncWindowControlState = (state, controlStateOverrides = null) => {
    const surface = byId("monitoring-hud");
    const normalized = state === "maximized" ? "maximized" : "normal";
    if (controlStateOverrides && typeof controlStateOverrides === "object") {
      Object.keys(windowControlDefaults).forEach((key) => {
        if (Object.prototype.hasOwnProperty.call(controlStateOverrides, key)) {
          windowControlStates[key] = normalizeWindowControlState(controlStateOverrides[key]);
        }
      });
    }
    if (surface) {
      surface.dataset.windowState = normalized;
    }
    Object.keys(windowControlDefaults).forEach((key) => syncSingleWindowControlState(key, normalized));
  };
  window.nexusAiControlCenterSetWindowState = syncWindowControlState;
  window.nexusAiControlCenterSetWindowControlStates = (states) => {
    syncWindowControlState(byId("monitoring-hud")?.dataset.windowState || "normal", states);
  };

  const syncRowLabelColumnSizing = () => {
    const surface = byId("monitoring-hud");
    const hub = byId("ai-control-center-card-hub");
    if (!surface || !hub) {
      return;
    }
    const labels = [...hub.querySelectorAll(".ai-control-center-card-rows .monitoring-hud__state-row > span")];
    const maxLabelWidth = labels.reduce((maxWidth, label) => {
      const rect = label.getBoundingClientRect();
      return Math.max(maxWidth, Math.ceil(Math.max(rect.width || 0, label.scrollWidth || 0)));
    }, 0);
    hub.style.setProperty(
      "--ai-dashboard-row-label-width",
      `${maxLabelWidth}px`,
    );
    hub.style.setProperty("--ai-dashboard-row-gutter", "8px");
    hub.style.setProperty("--ai-dashboard-row-vertical-gutter", "6px");
    hub.dataset.rowLabelColumnSource = "measured-max-visible-label-content-px";
    hub.dataset.rowLabelColumnWidth = String(maxLabelWidth);
    hub.dataset.rowLabelColumnUnit = "px";
    hub.dataset.rowValueGutter = "8";
    hub.dataset.rowValueColumnContract = "shared-max-label-content-plus-fixed-gutter";
    surface.dataset.rowTitleSizing = "shared-max-label-content-fixed-gutter";
  };
  window.nexusAiControlCenterSyncRowLabelColumnSizing = syncRowLabelColumnSizing;

  const syncTitleDescriptionWrap = () => {
    const surface = byId("monitoring-hud");
    const titleGroup = document.querySelector(".monitoring-hud__title-group");
    const subtitle = document.querySelector(".monitoring-hud__subtitle");
    if (!surface || !titleGroup || !subtitle) {
      return;
    }
    const style = getComputedStyle(titleGroup);
    const rect = titleGroup.getBoundingClientRect();
    const paddingX = Number.parseFloat(style.paddingLeft || "0") + Number.parseFloat(style.paddingRight || "0");
    const maxWidth = Math.max(0, Math.floor(rect.width - paddingX));
    titleGroup.style.setProperty("--ai-dashboard-title-description-max-width", `${maxWidth}px`);
    surface.dataset.titleDescriptionWrap = "measured-title-card-prose-word-wrap";
    subtitle.dataset.titleDescriptionWrap = "measured-title-card-prose-word-wrap";
    subtitle.dataset.titleDescriptionColumnSource = "title-card-inner-content-width-px";
    subtitle.dataset.titleDescriptionMaxWidth = String(maxWidth);
  };
  window.nexusAiControlCenterSyncTitleDescriptionWrap = syncTitleDescriptionWrap;

  const syncDashboardLayout = () => {
    syncTitleDescriptionWrap();
    syncRowLabelColumnSizing();
    syncCustomScrollbar();
  };
  window.nexusAiControlCenterSyncDashboardLayout = syncDashboardLayout;

  const buildDashboardViewModel = () => {
    const providerRuntimeBlocked = (
      providerState.providerExecutionGateState === "provider-execution-disabled"
      && providerState.modelExecutionGateState === "model-execution-disabled"
    );
    const promptDisabled = (
      providerState.promptSendPosture === "prompt-send-disabled"
      && providerState.promptAcceptance === "disabled"
      && providerState.memoryIndexingState === "memory-indexing-disabled"
    );
    const privacyProtected = (
      providerState.providerVisibleData === "none"
      && providerState.sentToProvider === false
      && providerState.networkEgressState === "network-egress-blocked"
    );
  const installBlocked = (
      String(providerState.installIntentState || "").includes("blocked")
      || String(providerState.capabilityPackInstallState || "").includes("blocked")
    );
    const updatesBlocked = String(providerState.capabilityPackUpdateState || "").includes("blocked");
    const privateSetupBlocked = (
      providerState.privateSetupAuthorized === false
      && providerState.privateMaterialVisible === false
    );
    const ownerRuntimeBlocked = (
      providerState.ownerMemoryEnabled === false
      && providerState.ownerAgentsEnabled === false
    );
    const rows = {
      controlCenter: {
        aiPersona: "None; ORIN persona not implemented",
        providerRuntime: providerRuntimeBlocked
          ? "Blocked; no model path active"
          : "Blocked; provider state requires review",
        privacy: privacyProtected
          ? "Protected; no provider or third-party tracking"
          : "Protected; fail-closed boundary mismatch",
      },
      readinessDiagnostics: {
        readinessCheck: "Waiting for USER action",
        readinessReport: "Local decision aid behind diagnostics",
        prompt: promptDisabled
          ? "Not accepted, sent, stored, or indexed"
          : "Not accepted; prompt boundary mismatch",
      },
      capabilitiesMaintenance: {
        capabilityPacks: installBlocked
          ? "Install blocked; downloads disabled"
          : "Install unavailable; capability proof required",
        maintenanceUpdates: updatesBlocked
          ? "Future-gated; no install execution"
          : "Future-gated; update state requires review",
        developerLane: providerState.developerLaneBoundaryLabel || "Developer lane: gated; private setup not configured",
        ownerLane: providerState.ownerLaneBoundaryLabel || "Owner lane: gated; private setup not configured",
        privateSetup: privateSetupBlocked
          ? "Private setup blocked; no private material visible"
          : "Private setup boundary requires review",
      },
    };
    return {
      contract: dashboardViewModelContract,
      source: "AIProviderStateSnapshot.as_renderer_payload",
      sourceFields: {
        providerExecutionGateState: providerState.providerExecutionGateState || "",
        modelExecutionGateState: providerState.modelExecutionGateState || "",
        providerVisibleData: providerState.providerVisibleData || "",
        sentToProvider: providerState.sentToProvider === false ? "false" : String(providerState.sentToProvider || ""),
        networkEgressState: providerState.networkEgressState || "",
        promptSendPosture: providerState.promptSendPosture || "",
        promptAcceptance: providerState.promptAcceptance || "",
        memoryIndexingState: providerState.memoryIndexingState || "",
        installIntentState: providerState.installIntentState || "",
        capabilityPackLifecycleState: providerState.capabilityPackLifecycleState || "",
        capabilityPackDownloadState: providerState.capabilityPackDownloadState || "",
        capabilityPackInstallState: providerState.capabilityPackInstallState || "",
        capabilityPackUpdateState: providerState.capabilityPackUpdateState || "",
        capabilityPackUninstallState: providerState.capabilityPackUninstallState || "",
        developerLaneBoundaryState: providerState.developerLaneBoundaryState || "",
        developerLaneBoundaryLabel: providerState.developerLaneBoundaryLabel || "",
        ownerLaneBoundaryState: providerState.ownerLaneBoundaryState || "",
        ownerLaneBoundaryLabel: providerState.ownerLaneBoundaryLabel || "",
        privateSetupBoundaryState: providerState.privateSetupBoundaryState || "",
        privateSetupAuthorized: providerState.privateSetupAuthorized === false ? "false" : String(providerState.privateSetupAuthorized || ""),
        privateMaterialVisible: providerState.privateMaterialVisible === false ? "false" : String(providerState.privateMaterialVisible || ""),
        ownerMemoryEnabled: providerState.ownerMemoryEnabled === false ? "false" : String(providerState.ownerMemoryEnabled || ""),
        ownerAgentsEnabled: providerState.ownerAgentsEnabled === false ? "false" : String(providerState.ownerAgentsEnabled || ""),
        recoveryLabel: providerState.aiControlCenterRecoveryLabel || "Retry local check only",
      },
      disabledActions: {
        providerModelExecution: providerRuntimeBlocked,
        promptSend: promptDisabled,
        providerVisibleDataEgress: privacyProtected,
        capabilityInstallDownload: installBlocked,
        maintenanceUpdateExecution: updatesBlocked,
        privateSetup: privateSetupBlocked,
        ownerMemoryAgents: ownerRuntimeBlocked,
      },
      recoveryGuidance: {
        label: providerState.aiControlCenterRecoveryLabel || "Retry local check only",
        detail: providerState.aiControlCenterRecoveryDetail || "Recovery remains local-only; provider setup and execution stay future-gated.",
      },
      rows,
    };
  };

  const syncCapabilitiesBoundaryContract = (viewModel) => {
    const card = document.querySelector('[data-dashboard-hub-card="capabilities-maintenance"]');
    if (!card) {
      return;
    }
    Object.assign(card.dataset, {
      capabilitiesBoundaryContract: "capabilities-maintenance-developer-owner-boundary-v1",
      capabilityPackLifecycleState: viewModel.sourceFields.capabilityPackLifecycleState || "capability-pack-lifecycle-planned",
      capabilityPackDownloadState: viewModel.sourceFields.capabilityPackDownloadState || "capability-pack-downloads-blocked",
      installIntentState: viewModel.sourceFields.installIntentState || "install-intent-blocked",
      capabilityPackInstallState: viewModel.sourceFields.capabilityPackInstallState || "install-blocked",
      capabilityPackUpdateState: viewModel.sourceFields.capabilityPackUpdateState || "update-blocked",
      capabilityPackUninstallState: viewModel.sourceFields.capabilityPackUninstallState || "uninstall-blocked",
      developerLaneBoundaryState: viewModel.sourceFields.developerLaneBoundaryState || "developer-lane-private-setup-blocked",
      ownerLaneBoundaryState: viewModel.sourceFields.ownerLaneBoundaryState || "owner-lane-private-setup-blocked",
      privateSetupBoundaryState: viewModel.sourceFields.privateSetupBoundaryState || "private-setup-blocked",
      privateSetupAuthorized: viewModel.sourceFields.privateSetupAuthorized || "false",
      privateMaterialVisible: viewModel.sourceFields.privateMaterialVisible || "false",
      ownerMemoryEnabled: viewModel.sourceFields.ownerMemoryEnabled || "false",
      ownerAgentsEnabled: viewModel.sourceFields.ownerAgentsEnabled || "false",
      downloadExecution: "blocked",
      installExecution: "blocked",
      updateExecution: "blocked",
      fetchExecution: "blocked",
      capabilityExecution: "blocked",
      packagingExecution: "blocked",
      viewModelPrivateSetupBlocked: viewModel.disabledActions.privateSetup ? "true" : "false",
      viewModelOwnerMemoryAgentsBlocked: viewModel.disabledActions.ownerMemoryAgents ? "true" : "false",
    });
  };

  const applyDashboardViewModel = () => {
    const viewModel = buildDashboardViewModel();
    window.nexusAiControlCenterCurrentViewModel = viewModel;
    setText("ai-dashboard-ai-persona-value", viewModel.rows.controlCenter.aiPersona);
    setText("ai-dashboard-provider-runtime-value", viewModel.rows.controlCenter.providerRuntime);
    setText("ai-dashboard-privacy-value", viewModel.rows.controlCenter.privacy);
    setText("ai-dashboard-readiness-check-value", viewModel.rows.readinessDiagnostics.readinessCheck);
    setText("ai-dashboard-readiness-report-value", viewModel.rows.readinessDiagnostics.readinessReport);
    setText("ai-dashboard-prompt-value", viewModel.rows.readinessDiagnostics.prompt);
    setText("ai-dashboard-capability-packs-value", viewModel.rows.capabilitiesMaintenance.capabilityPacks);
    setText("ai-dashboard-maintenance-updates-value", viewModel.rows.capabilitiesMaintenance.maintenanceUpdates);
    const surface = byId("monitoring-hud");
    if (surface) {
      Object.assign(surface.dataset, {
        viewModelContract: viewModel.contract,
        viewModelSource: viewModel.source,
        viewModelState: "provider-payload-applied",
        viewModelProviderRuntimeBlocked: viewModel.disabledActions.providerModelExecution ? "true" : "false",
        viewModelPromptSendDisabled: viewModel.disabledActions.promptSend ? "true" : "false",
        viewModelProviderVisibleDataNone: viewModel.sourceFields.providerVisibleData === "none" ? "true" : "false",
        viewModelRecoveryGuidance: viewModel.recoveryGuidance.label,
        viewModelPrivateSetupBlocked: viewModel.disabledActions.privateSetup ? "true" : "false",
        viewModelOwnerMemoryAgentsBlocked: viewModel.disabledActions.ownerMemoryAgents ? "true" : "false",
      });
    }
    syncCapabilitiesBoundaryContract(viewModel);
    document.querySelectorAll("[data-view-model-key]").forEach((row) => {
      row.dataset.viewModelContract = viewModel.contract;
      row.dataset.viewModelBound = "provider-payload";
    });
    return viewModel;
  };
  window.nexusAiControlCenterBuildDashboardViewModel = buildDashboardViewModel;
  window.nexusAiControlCenterApplyDashboardViewModel = applyDashboardViewModel;

  const syncStateTaxonomyContract = () => {
    const surface = byId("monitoring-hud");
    if (!surface) {
      return;
    }
    const taxonomy = Array.isArray(providerState.aiControlCenterStateTaxonomy)
      ? providerState.aiControlCenterStateTaxonomy
      : [];
    const renderedStates = taxonomy
      .map((item) => (item && typeof item === "object" ? String(item.state || "").trim() : ""))
      .filter(Boolean);
    const complete = requiredStateTaxonomyStates.every((state) => renderedStates.includes(state));
    const providerVisibleData = String(providerState.providerVisibleData || "none");
    const promptSendPosture = String(providerState.promptSendPosture || "prompt-send-disabled");
    const diagnosticState = String(providerState.aiControlCenterDiagnosticState || "no-provider-fail-closed");
    const providerExecution = (
      providerState.providerExecutionGateState === "provider-execution-disabled"
      && providerState.modelExecutionGateState === "model-execution-disabled"
    ) ? "blocked-no-model-path" : "blocked-fail-closed";
    Object.assign(surface.dataset, {
      stateTaxonomyContract,
      stateTaxonomySource: "AIProviderStateSnapshot.aiControlCenterStateTaxonomy",
      stateTaxonomyRenderedStates: renderedStates.join(" "),
      stateTaxonomyComplete: complete ? "true" : "false",
      providerVisibleDataState: providerVisibleData,
      noProviderState: diagnosticState,
      promptExecutionState: promptSendPosture,
      providerModelRuntimeState: providerExecution,
      trustBoundaryState: (
        providerVisibleData === "none"
        && promptSendPosture === "prompt-send-disabled"
        && providerState.networkEgressState === "network-egress-blocked"
        && providerState.memoryIndexingState === "memory-indexing-disabled"
      ) ? "local-only-no-egress-no-memory-no-cache" : "fail-closed-boundary-mismatch",
    });
    document.querySelectorAll("[data-state-taxonomy-contract]").forEach((node) => {
      node.dataset.stateTaxonomyContract = stateTaxonomyContract;
      node.dataset.stateTaxonomyRenderedStates = renderedStates.join(" ");
      node.dataset.stateTaxonomyComplete = complete ? "true" : "false";
    });
    const card = document.querySelector('[data-dashboard-hub-card="control-center"]');
    if (card) {
      Object.assign(card.dataset, {
        aiPersonaState: "none-orin-persona-not-implemented",
        providerModelRuntimeState: providerExecution,
        providerVisibleDataState: providerVisibleData,
        noProviderState: diagnosticState,
      });
    }
  };
  window.nexusAiControlCenterSyncStateTaxonomyContract = syncStateTaxonomyContract;

  const syncCustomScrollbar = () => {
    const surface = byId("monitoring-hud");
    const chrome = surface?.querySelector(".monitoring-hud__chrome");
    const hub = byId("ai-control-center-card-hub");
    const rail = byId("ai-control-center-scrollbar");
    const track = byId("ai-control-center-scrollbar-track");
    const thumb = byId("ai-control-center-scrollbar-thumb");
    if (!surface || !chrome || !hub || !rail || !track || !thumb) {
      return;
    }

    const maxScroll = Math.max(0, hub.scrollHeight - hub.clientHeight);
    surface.dataset.customScrollbarVisible = maxScroll > 1 ? "true" : "false";
    if (maxScroll <= 1) {
      thumb.style.height = "44px";
      thumb.style.transform = "translateY(0px)";
      return;
    }

    const chromeRect = chrome.getBoundingClientRect();
    const hubRect = hub.getBoundingClientRect();
    const trackTop = Math.max(0, hubRect.top - chromeRect.top + 10);
    const trackHeight = Math.max(44, hubRect.height - 26);
    const rightInset = Math.max(10, chromeRect.right - hubRect.right + 4);
    rail.style.top = `${trackTop}px`;
    rail.style.right = `${rightInset}px`;
    rail.style.height = `${trackHeight}px`;

    const thumbHeight = Math.max(44, Math.round(trackHeight * (hub.clientHeight / hub.scrollHeight)));
    const travel = Math.max(0, trackHeight - thumbHeight);
    const y = Math.round((hub.scrollTop / maxScroll) * travel);
    thumb.style.height = `${thumbHeight}px`;
    thumb.style.transform = `translateY(${y}px)`;
  };
  window.nexusAiControlCenterSyncScrollbar = syncCustomScrollbar;

  const scrollHubToTrackPosition = (clientY) => {
    const hub = byId("ai-control-center-card-hub");
    const track = byId("ai-control-center-scrollbar-track");
    const thumb = byId("ai-control-center-scrollbar-thumb");
    if (!hub || !track || !thumb) {
      return;
    }
    const maxScroll = Math.max(0, hub.scrollHeight - hub.clientHeight);
    const trackRect = track.getBoundingClientRect();
    const thumbHeight = thumb.getBoundingClientRect().height || 44;
    const travel = Math.max(1, trackRect.height - thumbHeight);
    const y = Math.min(Math.max(0, clientY - trackRect.top - (thumbHeight / 2)), travel);
    hub.scrollTop = Math.round((y / travel) * maxScroll);
    syncCustomScrollbar();
  };

  window.nexusAiControlCenterApplyProviderState = (payload) => {
    providerState = payload && typeof payload === "object" ? payload : {};
    const dashboardViewModel = applyDashboardViewModel();
    syncStateTaxonomyContract();
    const firstText = (...values) => {
      for (const value of values) {
        const text = String(value || "").trim();
        if (text) {
          return text;
        }
      }
      return "";
    };
    const providerExecution = (
      providerState.providerExecutionGateState === "provider-execution-disabled"
      && providerState.modelExecutionGateState === "model-execution-disabled"
    )
      ? "Disabled and blocked"
      : (providerState.providerExecutionGateLabel || "Disabled and blocked");
    const rawCapabilityPacks = String(providerState.installIntentLabel || "");
    let capabilityPacks = rawCapabilityPacks || "Install blocked; downloads disabled";
    if (
      String(providerState.installIntentState || "").toLowerCase().includes("blocked")
      || rawCapabilityPacks.toLowerCase().includes("blocked")
    ) {
      capabilityPacks = "Install blocked; downloads disabled";
    }
    if (!String(capabilityPacks).toLowerCase().includes("download")) {
      capabilityPacks = `${capabilityPacks}; downloads disabled`;
    }
    const providerVisibleData = providerState.providerVisibleData || "none";
    const providerVisibleDataDisplay = providerVisibleData === "none" ? "None" : providerVisibleData;
    const providerVisibleDataDetail = providerVisibleData === "none"
      ? "No prompt, file, memory, telemetry, or provider config is sent."
      : (
        providerState.providerVisibleDataDetail
        || "Provider-visible data state requires review before any provider path runs."
      );
    const diagnosticLabel = firstText(
      providerState.aiControlCenterDiagnosticLabel,
      "No provider configured; fail-closed",
    );
    const boundaryLabel = firstText(
      providerState.aiControlCenterProviderBoundaryLabel,
      "Provider boundary: blocked",
    );
    const blockedActionLabel = firstText(
      providerState.aiControlCenterBlockedActionLabel,
      "Prompt/provider/model action blocked",
    );
    const unavailableCapabilityLabel = firstText(
      providerState.aiControlCenterUnavailableCapabilityLabel,
      "Capability packs unavailable",
    );
    const recoveryLabel = firstText(
      dashboardViewModel.recoveryGuidance.label,
      providerState.aiControlCenterRecoveryLabel,
      "Retry local check only",
    );
    const degradedPathLabel = firstText(
      providerState.aiControlCenterDegradedPathLabel,
      "Local guidance only",
    );

    setText("ai-control-center-provider-model", providerExecution);
    setText("ai-control-center-prompt-memory", "Not accepted, sent, stored, or indexed");
    setText("ai-control-center-capability-packs", capabilityPacks);
    setText("ai-control-center-maintenance-updates", "Lifecycle placement only; update execution blocked");
    setText("ai-control-center-edition-lanes", "Public only; Developer and Owner gated");
    setText("ai-control-center-provider-boundary", boundaryLabel);
    setText("ai-control-center-diagnostic-state", diagnosticLabel);
    setText("ai-control-center-recovery", recoveryLabel);
    setText("ai-control-center-local-result", "Waiting for local action");
    setText(
      "ai-control-center-local-detail",
      providerVisibleDataDetail,
    );
    setText("ai-control-center-blocked-action", blockedActionLabel);
    setText("ai-control-center-unavailable-capability", unavailableCapabilityLabel);
    setText("ai-control-center-degraded-path", degradedPathLabel);
    currentReadinessReportText = "";
    setText("ai-control-center-report-state", "Not generated");
    setText("ai-control-center-report-persistence", "View-only; copy is USER initiated");
    setText("ai-control-center-report-summary", "Generate the report to inspect local readiness.");
    byId("ai-control-center-report-body")?.setAttribute("hidden", "");
    setReportCopyEnabled(false);
    requestAnimationFrame(syncDashboardLayout);
  };

  window.nexusAiControlCenterRunLocalCheck = () => {
    const guardClosed = providerState.sentToProvider === false
      && providerState.canAcceptPrompts === false
      && providerState.providerVisibleData === "none"
      && providerState.promptSendPosture === "prompt-send-disabled"
      && providerState.networkEgressState === "network-egress-blocked"
      && providerState.memoryIndexingState === "memory-indexing-disabled";
    const rawLocalResult = String(providerState.localActionResultLabel || "No provider configured");
    const localResult = rawLocalResult === "No-provider check: no provider configured"
      ? "No provider configured"
      : rawLocalResult.replace(": no provider configured", ": No provider configured");
    const localDetail = String(
      providerState.localActionResultDetail
      || "No prompt was accepted or sent; provider-visible data remains none. Capability packs, private lanes, downloads, memory, and network remain blocked.",
    );
    setText(
      "ai-control-center-local-result",
      guardClosed ? localResult : "Local check: blocked",
    );
    setText(
      "ai-control-center-local-detail",
      guardClosed
        ? localDetail
        : "Provider boundary mismatch; no local result was produced.",
    );
    setText(
      "ai-control-center-diagnostic-state",
      guardClosed
        ? (providerState.aiControlCenterDiagnosticLabel || "No provider configured; fail-closed")
        : "Boundary mismatch; fail-closed",
    );
    setText(
      "ai-control-center-blocked-action",
      guardClosed
        ? (providerState.aiControlCenterBlockedActionLabel || "Prompt/provider/model action blocked")
        : "Local check blocked by boundary mismatch",
    );
    requestAnimationFrame(syncDashboardLayout);
  };
  window.nexusAiControlCenterGenerateReadinessReport = () => (
    renderReadinessReport(providerState.localAiReadinessReport || {})
  );
  window.nexusAiControlCenterCopyReadinessReport = copyReadinessReport;

  const observeDashboardLayoutDrift = () => {
    const hub = byId("ai-control-center-card-hub");
    if (!hub || !window.ResizeObserver) {
      return;
    }
    const observer = new ResizeObserver(() => {
      requestAnimationFrame(syncDashboardLayout);
    });
    observer.observe(hub);
    const titleGroup = document.querySelector(".monitoring-hud__title-group");
    const subtitle = document.querySelector(".monitoring-hud__subtitle");
    if (titleGroup) {
      observer.observe(titleGroup);
    }
    if (subtitle) {
      observer.observe(subtitle);
    }
    hub.querySelectorAll(".ai-control-center-card-rows .monitoring-hud__state-row > span").forEach((label) => {
      observer.observe(label);
    });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => requestAnimationFrame(syncDashboardLayout)).catch(() => {});
    }
  };

  const attachWindowControlHandlers = () => {
    Object.entries(windowControlDefaults).forEach(([key, config]) => {
      const button = byId(config.id);
      if (!button) {
        return;
      }
      button.addEventListener("click", (event) => {
        if (button.hidden || button.disabled || button.dataset.windowControlState !== "active") {
          event.preventDefault();
          event.stopPropagation();
          return;
        }
        const command = button.dataset.windowControlCommand || config.command;
        if (command) {
          emitCommand(command);
        }
      });
    });
  };
  const attachDomainDoorwayHandlers = () => {
    document.querySelectorAll("[data-category-doorway]").forEach((button) => {
      attachActivationHandler(button, (event) => {
        if (button.disabled || button.getAttribute("aria-disabled") === "true") {
          event.preventDefault();
          event.stopPropagation();
          return;
        }
        const command = button.dataset.launchCommand || domainDoorwayCommands[button.dataset.categoryDoorway || ""];
        if (command) {
          emitCommand(command);
        }
      });
    });
  };

  hydrateWindowControlStatesFromMarkup();
  applyDomainDoorwayState();
  stripNativeTooltips();
  observeNativeTooltipDrift();
  observeDashboardLayoutDrift();
  attachWindowControlHandlers();
  attachDomainDoorwayHandlers();
  attachActivationHandler(byId("ai-control-center-local-check-action"), () => {
    window.nexusAiControlCenterRunLocalCheck();
    emitCommand("run-local-check");
  });
  attachActivationHandler(byId("ai-control-center-generate-report-action"), () => {
    const generated = window.nexusAiControlCenterGenerateReadinessReport();
    emitCommand(generated ? "generate-readiness-report" : "generate-readiness-report-blocked");
  });
  attachActivationHandler(byId("ai-control-center-copy-report-action"), () => {
    window.nexusAiControlCenterCopyReadinessReport().then((copied) => {
      emitCommand(copied ? "copy-readiness-report" : "copy-readiness-report-blocked");
    });
  });
  byId("ai-control-center-card-hub")?.addEventListener("scroll", syncCustomScrollbar, { passive: true });
  byId("ai-control-center-scrollbar-track")?.addEventListener("mousedown", (event) => {
    event.preventDefault();
    scrollHubToTrackPosition(event.clientY);
  });
  byId("ai-control-center-scrollbar-thumb")?.addEventListener("mousedown", (event) => {
    event.preventDefault();
    event.stopPropagation();
    scrollbarDrag = { startY: event.clientY, startScrollTop: byId("ai-control-center-card-hub")?.scrollTop || 0 };
  });
  window.addEventListener("mousemove", (event) => {
    if (!scrollbarDrag) {
      return;
    }
    const hub = byId("ai-control-center-card-hub");
    const track = byId("ai-control-center-scrollbar-track");
    const thumb = byId("ai-control-center-scrollbar-thumb");
    if (!hub || !track || !thumb) {
      return;
    }
    const maxScroll = Math.max(0, hub.scrollHeight - hub.clientHeight);
    const travel = Math.max(1, track.getBoundingClientRect().height - thumb.getBoundingClientRect().height);
    const delta = event.clientY - scrollbarDrag.startY;
    hub.scrollTop = Math.round(scrollbarDrag.startScrollTop + ((delta / travel) * maxScroll));
    syncCustomScrollbar();
  });
  window.addEventListener("mouseup", () => {
    scrollbarDrag = null;
  });
  window.addEventListener("resize", syncDashboardLayout);
  window.addEventListener("load", () => {
    applyDomainDoorwayState();
    requestAnimationFrame(syncDashboardLayout);
  });
  syncWindowControlState("normal");
  syncDashboardLayout();
  requestAnimationFrame(syncDashboardLayout);
})();
