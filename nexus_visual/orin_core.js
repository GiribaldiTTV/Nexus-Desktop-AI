const body = document.body;
const backCanvas = document.getElementById("fx-back");
const frontCanvas = document.getElementById("fx-front");
const bctx = backCanvas.getContext("2d");
const fctx = frontCanvas.getContext("2d");
const commandOverlay = document.getElementById("command-overlay");
const commandHint = document.getElementById("command-hint");
const commandInputShell = document.getElementById("command-input-shell");
const commandInputText = document.getElementById("command-input-text");
const commandStatus = document.getElementById("command-status");
const commandAmbiguous = document.getElementById("command-ambiguous");
const commandConfirmation = document.getElementById("command-confirmation");
const commandConfirmRequest = document.getElementById("command-confirm-request");
const commandConfirmTitle = document.getElementById("command-confirm-title");
const commandConfirmKind = document.getElementById("command-confirm-kind");
const commandConfirmTarget = document.getElementById("command-confirm-target");
const aiProviderStatus = document.getElementById("ai-provider-status");
const aiProviderStatusState = document.getElementById("ai-provider-status-state");
const aiProviderStatusProvider = document.getElementById("ai-provider-status-provider");
const aiProviderStatusSelection = document.getElementById("ai-provider-status-selection");
const aiProviderStatusConfiguration = document.getElementById("ai-provider-status-configuration");
const aiProviderStatusRegistry = document.getElementById("ai-provider-status-registry");
const aiProviderStatusHardware = document.getElementById("ai-provider-status-hardware");
const aiProviderStatusGpu = document.getElementById("ai-provider-status-gpu");
const aiProviderStatusCpu = document.getElementById("ai-provider-status-cpu");
const aiProviderStatusPower = document.getElementById("ai-provider-status-power");
const aiProviderStatusThermal = document.getElementById("ai-provider-status-thermal");
const aiProviderStatusModelWorkload = document.getElementById("ai-provider-status-model-workload");
const aiProviderStatusHardwareDetection = document.getElementById("ai-provider-status-hardware-detection");
const aiProviderStatusRam = document.getElementById("ai-provider-status-ram");
const aiProviderStatusDisk = document.getElementById("ai-provider-status-disk");
const aiProviderStatusModelMetadata = document.getElementById("ai-provider-status-model-metadata");
const aiProviderStatusCapabilityPack = document.getElementById("ai-provider-status-capability-pack");
const aiProviderStatusCapabilityDownload = document.getElementById("ai-provider-status-capability-download");
const aiProviderStatusCapabilityRecommendation = document.getElementById("ai-provider-status-capability-recommendation");
const aiProviderStatusCapabilityManifest = document.getElementById("ai-provider-status-capability-manifest");
const aiProviderStatusCapabilityIntegrity = document.getElementById("ai-provider-status-capability-integrity");
const aiProviderStatusDataClassification = document.getElementById("ai-provider-status-data-classification");
const aiProviderStatusMemory = document.getElementById("ai-provider-status-memory");
const aiProviderStatusMemoryContract = document.getElementById("ai-provider-status-memory-contract");
const aiProviderStatusEgress = document.getElementById("ai-provider-status-egress");
const aiProviderStatusAuditSecrets = document.getElementById("ai-provider-status-audit-secrets");
const aiProviderStatusWindows = document.getElementById("ai-provider-status-windows");
const aiProviderStatusOffline = document.getElementById("ai-provider-status-offline");
const aiProviderStatusPersona = document.getElementById("ai-provider-status-persona");
const aiProviderStatusVoice = document.getElementById("ai-provider-status-voice");
const aiProviderStatusValidation = document.getElementById("ai-provider-status-validation");
const aiProviderStatusAbuse = document.getElementById("ai-provider-status-abuse");
const aiProviderStatusReleaseProof = document.getElementById("ai-provider-status-release-proof");
const aiProviderStatusCopyContract = document.getElementById("ai-provider-status-copy-contract");
const aiProviderStatusFixtures = document.getElementById("ai-provider-status-fixtures");
const aiProviderStatusConsent = document.getElementById("ai-provider-status-consent");
const aiProviderStatusDisclosure = document.getElementById("ai-provider-status-disclosure");
const aiProviderStatusVisibleDataDetail = document.getElementById("ai-provider-status-visible-data-detail");
const aiProviderStatusConsentBoundary = document.getElementById("ai-provider-status-consent-boundary");
const aiProviderStatusRuntime = document.getElementById("ai-provider-status-runtime");
const aiProviderStatusRuntimeReason = document.getElementById("ai-provider-status-runtime-reason");
const aiProviderStatusRuntimeProvenance = document.getElementById("ai-provider-status-runtime-provenance");
const aiProviderStatusRuntimeSchema = document.getElementById("ai-provider-status-runtime-schema");
const aiProviderStatusReadiness = document.getElementById("ai-provider-status-readiness");
const aiProviderStatusSetupEligibility = document.getElementById("ai-provider-status-setup-eligibility");
const aiProviderStatusSetupBlocker = document.getElementById("ai-provider-status-setup-blocker");
const aiProviderStatusReadinessReason = document.getElementById("ai-provider-status-readiness-reason");
const aiProviderStatusReadinessProvenance = document.getElementById("ai-provider-status-readiness-provenance");
const aiProviderStatusReadinessSchema = document.getElementById("ai-provider-status-readiness-schema");
const aiProviderStatusFutureGate = document.getElementById("ai-provider-status-future-gate");
const aiProviderStatusActivation = document.getElementById("ai-provider-status-activation");
const aiProviderStatusActivationEligibility = document.getElementById("ai-provider-status-activation-eligibility");
const aiProviderStatusActivationBlocker = document.getElementById("ai-provider-status-activation-blocker");
const aiProviderStatusActivationReason = document.getElementById("ai-provider-status-activation-reason");
const aiProviderStatusActivationProvenance = document.getElementById("ai-provider-status-activation-provenance");
const aiProviderStatusActivationSchema = document.getElementById("ai-provider-status-activation-schema");
const aiProviderStatusFutureActivationGate = document.getElementById("ai-provider-status-future-activation-gate");
const aiProviderStatusAdapter = document.getElementById("ai-provider-status-adapter");
const aiProviderStatusExecutionGates = document.getElementById("ai-provider-status-execution-gates");
const aiProviderStatusFunctionalAi = document.getElementById("ai-provider-status-functional-ai");
const aiProviderStatusExecutionReadiness = document.getElementById("ai-provider-status-execution-readiness");
const aiProviderStatusExecutionEligibility = document.getElementById("ai-provider-status-execution-eligibility");
const aiProviderStatusExecutionBlocker = document.getElementById("ai-provider-status-execution-blocker");
const aiProviderStatusExecutionReason = document.getElementById("ai-provider-status-execution-reason");
const aiProviderStatusExecutionProvenance = document.getElementById("ai-provider-status-execution-provenance");
const aiProviderStatusExecutionSchema = document.getElementById("ai-provider-status-execution-schema");
const aiProviderStatusExecutionApproval = document.getElementById("ai-provider-status-execution-approval");
const aiProviderStatusProviderPath = document.getElementById("ai-provider-status-provider-path");
const aiProviderStatusProviderPathReadiness = document.getElementById("ai-provider-status-provider-path-readiness");
const aiProviderStatusProviderPathEligibility = document.getElementById("ai-provider-status-provider-path-eligibility");
const aiProviderStatusProviderPathBlocker = document.getElementById("ai-provider-status-provider-path-blocker");
const aiProviderStatusProviderPathReason = document.getElementById("ai-provider-status-provider-path-reason");
const aiProviderStatusProviderPathSchema = document.getElementById("ai-provider-status-provider-path-schema");
const aiProviderStatusProviderProfile = document.getElementById("ai-provider-status-provider-profile");
const aiProviderStatusProviderConfigEnvelope = document.getElementById("ai-provider-status-provider-config-envelope");
const aiProviderStatusProviderApprovals = document.getElementById("ai-provider-status-provider-approvals");
const aiProviderStatusSetupContract = document.getElementById("ai-provider-status-setup-contract");
const aiProviderStatusSetupContractBlocker = document.getElementById("ai-provider-status-setup-contract-blocker");
const aiProviderStatusSetupContractHandoff = document.getElementById("ai-provider-status-setup-contract-handoff");
const aiProviderStatusSetupFoundation = document.getElementById("ai-provider-status-setup-foundation");
const aiProviderStatusSetupFoundationBlocker = document.getElementById("ai-provider-status-setup-foundation-blocker");
const aiProviderStatusSetupFoundationValidation = document.getElementById("ai-provider-status-setup-foundation-validation");
const aiProviderStatusSetupFoundationPersistence = document.getElementById("ai-provider-status-setup-foundation-persistence");
const aiProviderStatusSetupFoundationHandoff = document.getElementById("ai-provider-status-setup-foundation-handoff");
const aiProviderStatusConsentCollectionFoundation = document.getElementById("ai-provider-status-consent-collection-foundation");
const aiProviderStatusConsentCollectionBlocker = document.getElementById("ai-provider-status-consent-collection-blocker");
const aiProviderStatusConsentCollectionAudit = document.getElementById("ai-provider-status-consent-collection-audit");
const aiProviderStatusConsentCollectionHandoff = document.getElementById("ai-provider-status-consent-collection-handoff");
const aiProviderStatusSetupConsent = document.getElementById("ai-provider-status-setup-consent");
const aiProviderStatusExecutionConsent = document.getElementById("ai-provider-status-execution-consent");
const aiProviderStatusConsentUx = document.getElementById("ai-provider-status-consent-ux");
const aiProviderStatusConsentUxSetup = document.getElementById("ai-provider-status-consent-ux-setup");
const aiProviderStatusConsentUxExecution = document.getElementById("ai-provider-status-consent-ux-execution");
const aiProviderStatusConsentUxRevocationReset = document.getElementById("ai-provider-status-consent-ux-revocation-reset");
const aiProviderStatusConsentUxGates = document.getElementById("ai-provider-status-consent-ux-gates");
const aiProviderStatusConsentSchema = document.getElementById("ai-provider-status-consent-schema");
const aiProviderStatusPathDataVisibility = document.getElementById("ai-provider-status-path-data-visibility");
const aiProviderStatusPathAudit = document.getElementById("ai-provider-status-path-audit");
const aiProviderStatusPathFutureGates = document.getElementById("ai-provider-status-path-future-gates");
const aiProviderStatusAdapterSelection = document.getElementById("ai-provider-status-adapter-selection");
const aiProviderStatusPromptGates = document.getElementById("ai-provider-status-prompt-gates");
const aiProviderStatusModelExecution = document.getElementById("ai-provider-status-model-execution");
const aiProviderStatusExecutionData = document.getElementById("ai-provider-status-execution-data");
const aiProviderStatusFunctionalRelease = document.getElementById("ai-provider-status-functional-release");
const aiProviderStatusCapabilityEligibility = document.getElementById("ai-provider-status-capability-eligibility");
const aiProviderStatusInstallIntent = document.getElementById("ai-provider-status-install-intent");
const aiProviderStatusPublicLane = document.getElementById("ai-provider-status-public-lane");
const aiProviderStatusDeveloperLane = document.getElementById("ai-provider-status-developer-lane");
const aiProviderStatusOwnerLane = document.getElementById("ai-provider-status-owner-lane");
const aiProviderStatusAction = document.getElementById("ai-provider-status-action");
const aiProviderStatusFallback = document.getElementById("ai-provider-status-fallback");
const aiProviderStatusResult = document.getElementById("ai-provider-status-result");
const aiProviderStatusResultDetail = document.getElementById("ai-provider-status-result-detail");
const aiProviderStatusNextAction = document.getElementById("ai-provider-status-next-action");
const aiProviderStatusPrivacy = document.getElementById("ai-provider-status-privacy");
const aiLocalStatusSurface = document.getElementById("ai-local-status-surface");
const aiLocalStatusLabel = document.getElementById("ai-local-status-label");
const aiLocalStatusScope = document.getElementById("ai-local-status-scope");
const aiLocalStatusActivity = document.getElementById("ai-local-status-activity");
const aiProviderTray = document.getElementById("ai-provider-tray");
const aiProviderTrayLabel = document.getElementById("ai-provider-tray-label");
const aiProviderTrayScope = document.getElementById("ai-provider-tray-scope");
const aiProviderTrayWindow = document.getElementById("ai-provider-tray-window");
const aiProviderTrayClose = document.getElementById("ai-provider-tray-close");
const aiProviderTrayLocalStatus = document.getElementById("ai-provider-tray-local-status");
const aiProviderTrayProviderVisibleData = document.getElementById("ai-provider-tray-provider-visible-data");
const aiProviderTrayProviderExecution = document.getElementById("ai-provider-tray-provider-execution");
const aiProviderTrayCapabilityPosture = document.getElementById("ai-provider-tray-capability-posture");
const aiProviderTrayLaneBoundary = document.getElementById("ai-provider-tray-lane-boundary");
const aiProviderTrayStatusBoundary = document.getElementById("ai-provider-tray-status-boundary");
const aiProviderTrayLocalAssistAction = document.getElementById("ai-provider-tray-local-assist-action");
const aiProviderTrayResult = document.getElementById("ai-provider-tray-result");
const aiProviderTrayResultDetail = document.getElementById("ai-provider-tray-result-detail");
const aiProviderTrayReviewNote = document.getElementById("ai-provider-tray-review-note");

let w = 0;
let h = 0;
let cx = 0;
let cy = 0;
let t = 0;

let currentState = "boot";
let ignition = 0.0;
let lastState = "boot";
let bootStartTime = null;

let voiceLevel = 0.0;
let smoothedVoiceLevel = 0.0;
let commandOverlayState = {
  visible: false,
  phase: "hidden",
  input_armed: false,
  input_text: "",
  status_kind: "idle",
  status_text: "",
  typed_request: "",
  pending_action: null,
  ambiguous_titles: []
};
let aiProviderState = {
  mode: "no-provider",
  availability: "disabled",
  providerLabel: "No provider/model execution",
  statusLabel: "No AI executing",
  localStatusSurfaceLabel: "No AI executing",
  localStatusSurfaceScope: "Provider/model off",
  localStatusActivityLabel: "Idle",
  trayStatusLabel: "NDAI",
  trayScopeLabel: "AI",
  trayLocalStatusDetail: "No AI executing; no provider/model active",
  trayProviderExecutionLabel: "disabled and blocked",
  trayStatusBoundaryLabel: "Display-only; controls live here",
  trayReviewNote:
    "FAM-007 owns this AI Control Center; the NDAI resident entry is a doorway only.",
  selectedProviderId: "no-provider",
  providerSelectionState: "fallback-no-provider",
  providerSelectionLabel: "No-provider fallback active",
  providerConfigurationState: "unconfigured",
  providerConfigurationLabel: "Provider configuration: none",
  providerRegistryState: "local-only-registry",
  providerRegistryLabel: "Local provider registry: no configured providers",
  providerInteractionState: "provider-boundary-interaction-plan",
  providerInteractionLabel: "Provider boundary plan: no-provider fallback",
  providerInteractionDetail: "Choose and approve a provider before AI prompts can run",
  configuredProviderCount: 0,
  availableProviderCount: 0,
  hardwareCapabilityState: "local-planning-only",
  hardwareCapabilityLabel: "Hardware capability: local planning only",
  gpuCapabilityState: "gpu-unprobed",
  gpuCapabilityLabel: "GPU acceleration: unprobed; no model workload active",
  cpuFallbackState: "cpu-fallback-preserved",
  cpuFallbackLabel: "CPU fallback: preserved",
  powerState: "power-state-not-evaluated",
  powerStateLabel: "Power state: not evaluated",
  thermalGuardrailState: "thermal-guardrails-required",
  thermalGuardrailLabel: "Thermal guardrails required before model workloads",
  modelWorkloadState: "model-workload-disabled",
  modelWorkloadLabel: "Model workloads: disabled",
  hardwareDetectionLevel: "level-1-safe-local-static-snapshot",
  hardwareDetectionLabel: "Hardware detection: Level 1 safe local static snapshot",
  capabilitySnapshotPolicy: "local-static-no-heavy-probe",
  capabilitySnapshotSource: "default-static-snapshot",
  capabilitySnapshotBudgetLabel: "Capability snapshot budget: static only; no heavy probe",
  ramReadinessState: "ram-unprobed",
  ramReadinessLabel: "RAM readiness: unprobed",
  diskReadinessState: "disk-unprobed",
  diskReadinessLabel: "Disk readiness: unprobed",
  modelWorkloadMetadataState: "model-workload-metadata-planned",
  modelWorkloadMetadataLabel: "Model workload metadata: planned; no execution",
  capabilityRecommendationState: "recommendation-pending",
  capabilityRecommendationLabel: "Capability recommendation pending hardware proof",
  capabilityPackLifecycleState: "capability-pack-lifecycle-planned",
  capabilityPackLifecycleLabel: "Capability packs: lifecycle planned",
  capabilityPackDownloadState: "capability-pack-downloads-blocked",
  capabilityPackDownloadLabel: "Capability pack downloads: blocked",
  capabilityPackManifestSchemaVersion: "capability-pack-manifest.v1",
  capabilityPackManifestState: "manifest-planned",
  capabilityPackSourceType: "local-source-future-gated",
  capabilityPackChecksumState: "checksum-required-before-install",
  capabilityPackSignatureState: "signature-required-before-install",
  capabilityPackCompatibilityState: "compatibility-unproven",
  capabilityPackDiskRequirement: "disk requirement: future manifest required",
  capabilityPackRamRequirement: "ram requirement: future manifest required",
  capabilityPackGpuRequirement: "gpu requirement: future manifest required",
  capabilityPackInstallState: "install-blocked",
  capabilityPackUpdateState: "update-blocked",
  capabilityPackUninstallState: "uninstall-blocked",
  dataClassificationState: "data-classification-local-only",
  dataClassificationLabel: "Data classification: local-only planning",
  dataClassificationSchemaVersion: "data-classification.v1",
  providerVisibleDataGuarantee: "provider-visible-data-none-guaranteed",
  memoryContextState: "memory-context-disabled",
  memoryContextLabel: "Memory/context: disabled; no indexing",
  memoryIndexingState: "memory-indexing-disabled",
  retrievalState: "retrieval-disabled",
  learningState: "learning-disabled",
  persistenceState: "persistence-disabled",
  futureMemoryEligibilityMarker: "future-memory-eligibility-gated",
  consentEnvelopeState: "consent-envelope-required",
  auditEnvelopeState: "audit-envelope-planned",
  secretBoundaryState: "secret-boundary-no-secrets-stored",
  networkEgressState: "network-egress-blocked",
  auditSecretsState: "audit-secrets-planned",
  auditSecretsLabel: "Audit/secrets: planned; no secrets stored",
  windowsResilienceState: "windows-resilience-planned",
  windowsResilienceLabel: "Windows resilience: planning only",
  offlineDegradedState: "offline-degraded-planned",
  offlineDegradedLabel: "Offline/degraded mode: planned",
  personaCoreVoiceState: "persona-core-voice-boundary-planned",
  personaCoreVoiceLabel: "Persona/Core/voice: planning boundary",
  voiceRuntimeState: "voice-runtime-disabled",
  voiceRuntimeLabel: "Voice runtime: disabled",
  validationProofGateState: "validation-proof-gates-planned",
  validationProofGateLabel: "Validation gates: static proof active",
  abuseEvalState: "abuse-eval-pending",
  abuseEvalLabel: "Abuse/eval: pending future approval",
  releaseProofGateState: "release-proof-pending",
  releaseProofGateLabel: "Release proof: pending future approval",
  coreDesktopCopyContractVersion: "core-desktop-provider-state-copy.v1",
  coreDesktopRuntimeStateContract: "core-desktop-runtime-state-contract",
  disabledPromptBehaviorContract: "disabled-prompt-provider-behavior",
  goldenProviderStateFixtures: "golden-provider-state-fixtures",
  validatorExpansionState: "validator-expansion-active",
  contractReadyMarker: "contract-ready",
  uiReadyMarker: "ui-ready",
  validatorReadyMarker: "validator-ready",
  futureImplementationGatedMarker: "future-implementation-gated",
  privacyScope: "local-only",
  privacyLabel: "Local shell only; nothing is sent",
  consentState: "required-before-provider",
  consentLabel: "Consent required before provider setup",
  providerVisibleData: "none",
  providerVisibleDataLabel: "Provider-visible data: none",
  providerVisibleDataDetail: "No prompt, file, screen, memory, or telemetry is sent",
  providerConsentBoundaryLabel: "Consent boundary: provider setup required before prompts",
  providerNextActionLabel:
    "Open NDAI for the AI Control Center; provider/model execution remains blocked",
  localActionResultSchemaVersion: "local-action-result.v1",
  localActionResultState: "deterministic-no-provider-result",
  localActionResultLabel: "No-provider check: no provider configured",
  localActionResultDetail:
    "Deterministic degraded result: no prompt was accepted or sent; provider-visible data remains none.",
  localActionResultProviderVisibleData: "none",
  localActionResultSentToProvider: false,
  localActionResultCanAcceptPrompts: false,
  localActionResultPromptSendPosture: "prompt-send-disabled",
  localActionResultNetworkEgressState: "network-egress-blocked",
  localActionResultMemoryIndexingState: "memory-indexing-disabled",
  runtimeStateSchemaVersion: "provider-runtime-state.v1",
  runtimeStateCategory: "provider_setup_disabled",
  runtimeStateLabel: "Runtime state: provider setup disabled",
  runtimeReasonCode: "provider_setup_disabled_local_only",
  runtimeReasonLabel: "Reason: setup disabled in local-only seam",
  runtimeConfigSchemaVersion: "provider-runtime-config.v1",
  runtimeConfigState: "default_config",
  runtimeConfigLabel: "Config: safe default local-only",
  runtimeConfigMigration: "no-runtime-migration-required",
  runtimeConfigValid: true,
  runtimeFailClosed: true,
  runtimeProvenance: "default_config",
  runtimeProvenanceLabel: "Provenance: default config",
  providerReadinessState: "setup_disabled",
  providerReadinessLabel: "Provider readiness: setup disabled",
  setupEligibilityState: "setup_eligibility_disabled",
  setupEligibilityLabel: "Setup eligibility: disabled",
  setupBlockerState: "setup_disabled",
  setupBlockerLabel: "Setup blocker: setup disabled",
  readinessReasonCode: "readiness_default_local_only",
  readinessReasonLabel: "Readiness reason: local-only default",
  readinessProvenance: "default_config",
  readinessProvenanceLabel: "Readiness provenance: default config",
  readinessStateSchemaVersion: "provider-readiness-state.v1",
  readinessConfigSchemaVersion: "provider-readiness-config.v1",
  readinessConfigState: "default_config",
  readinessConfigLabel: "Readiness config: safe default local-only",
  readinessConfigMigration: "safe-defaults-no-runtime-migration",
  readinessConfigValid: true,
  futureProviderGateStatus: "provider-setup-future-user-approval-required",
  futureProviderGateLabel: "Future provider gate: USER approval required before setup",
  providerActivationState: "activation_unavailable",
  providerActivationLabel: "Provider activation: unavailable",
  activationEligibilityState: "activation_eligibility_unavailable",
  activationEligibilityLabel: "Activation eligibility: unavailable",
  activationBlockerState: "readiness_required",
  activationBlockerLabel: "Activation blocker: readiness required",
  activationReasonCode: "activation_default_unavailable",
  activationReasonLabel: "Activation reason: activation foundation only",
  activationProvenance: "default_config",
  activationProvenanceLabel: "Activation provenance: default config",
  activationStateSchemaVersion: "provider-activation-state.v1",
  activationConfigSchemaVersion: "provider-activation-config.v1",
  activationConfigState: "default_config",
  activationConfigLabel: "Activation config: safe default local-only",
  activationConfigMigration: "safe-defaults-no-runtime-migration",
  activationConfigValid: true,
  futureActivationGateStatus: "activation-future-user-approval-required",
  futureActivationGateLabel: "Future activation gate: USER approval required before activation",
  providerAdapterPosture: "null-local-adapter",
  providerAdapterLabel: "Provider adapter: null local adapter",
  providerAdapterAvailabilityState: "adapter-unavailable",
  providerAdapterAvailabilityLabel: "Adapter availability: unavailable",
  providerAdapterExecutionPosture: "adapter-execution-disabled",
  providerAdapterExecutionLabel: "Adapter execution: disabled",
  providerMetadataContractVersion: "provider-metadata-contract.v1",
  providerConfigEnvelopeVersion: "provider-config-envelope.v1",
  providerActivationHandoffState: "activation-handoff-future-gated",
  promptExecutionGateState: "prompt-execution-disabled",
  promptExecutionGateLabel: "Prompt execution gate: disabled",
  modelExecutionGateState: "model-execution-disabled",
  modelExecutionGateLabel: "Model execution gate: disabled",
  providerExecutionGateState: "provider-execution-disabled",
  providerExecutionGateLabel: "Provider execution gate: disabled",
  functionalAiCriteriaState: "functional-ai-criteria-pending",
  functionalAiCriteriaLabel: "Functional AI: criteria pending for v1.8.0-prebeta",
  v18PrebetaReadinessState: "v1.8.0-prebeta-readiness-pending",
  v18PrebetaReadinessLabel: "v1.8.0-prebeta readiness: pending functional AI proof",
  providerExecutionReadinessState: "execution_unavailable",
  providerExecutionReadinessLabel: "Execution readiness: unavailable",
  promptExecutionReadinessState: "execution_blocked_by_prompt_gate",
  promptExecutionReadinessLabel: "Prompt execution readiness: disabled",
  modelExecutionReadinessState: "execution_blocked_by_model_gate",
  modelExecutionReadinessLabel: "Model execution readiness: disabled",
  executionEligibilityState: "execution_eligibility_unavailable",
  executionEligibilityLabel: "Execution eligibility: unavailable",
  executionBlockerState: "activation_required",
  executionBlockerLabel: "Execution blocker: activation required",
  executionReasonCode: "execution_default_unavailable",
  executionReasonLabel: "Execution reason: execution readiness gates only",
  executionProvenance: "activation_state",
  executionProvenanceLabel: "Execution provenance: activation state",
  executionStateSchemaVersion: "provider-execution-readiness-state.v1",
  executionConfigSchemaVersion: "provider-execution-readiness-config.v1",
  executionConfigState: "default_config",
  executionConfigLabel: "Execution config: safe default local-only",
  executionConfigMigration: "safe-defaults-no-execution-migration",
  executionConfigValid: true,
  executionApprovalStatus: "execution-approval-missing",
  executionApprovalLabel: "Execution approval: USER approval missing",
  providerPathStatus: "provider-path-not-selected",
  providerPathLabel: "Provider path: not selected",
  providerPathReadinessState: "provider_path_unavailable",
  providerPathReadinessLabel: "Provider path readiness: unavailable",
  providerPathEligibilityState: "provider_path_eligibility_unavailable",
  providerPathEligibilityLabel: "Provider path eligibility: unavailable",
  providerPathBlockerState: "execution_readiness_required",
  providerPathBlockerLabel: "Provider path blocker: execution readiness required",
  providerPathReasonCode: "provider_path_default_unavailable",
  providerPathReasonLabel: "Provider path reason: readiness only",
  providerPathProvenance: "default_config",
  providerPathStateSchemaVersion: "provider-path-readiness-state.v1",
  providerPathConfigSchemaVersion: "provider-path-readiness-config.v1",
  providerPathConfigState: "default_config",
  providerPathConfigLabel: "Provider path config: safe default local-only",
  providerPathApprovalStatus: "provider-path-approval-missing",
  providerPathApprovalLabel: "Provider path approval: USER approval missing",
  providerProfileId: "local-null-provider-profile",
  providerProfileKind: "null-local-provider",
  providerProfileDisplayName: "Local/null provider profile",
  providerProfileSource: "local-readiness-scaffold",
  providerProfileMetadataContractVersion: "provider-profile-metadata.v1",
  providerSdkRequirementPosture: "sdk-integration-pending-user-approval",
  providerNetworkRequirementPosture: "network-requirement-blocked",
  providerConfigStatus: "provider-config-missing",
  providerAvailabilityPosture: "provider-availability-unavailable",
  providerSetupApprovalStatus: "provider-setup-approval-missing",
  providerExecutionApprovalStatus: "provider-execution-approval-missing",
  providerVisibleDataScope: "provider-visible-data-requirement-none",
  localNullProviderFallbackStatus: "local-null-provider-fallback-active",
  futureSdkHandoffMarker: "future-sdk-handoff-marker",
  futureProviderSetupHandoffMarker: "future-provider-setup-handoff-marker",
  consentReadinessState: "consent_required_for_provider_setup",
  consentReadinessLabel: "Consent readiness: required before provider setup",
  consentStateSchemaVersion: "provider-consent-readiness-state.v1",
  consentConfigSchemaVersion: "provider-consent-readiness-config.v1",
  consentConfigMigration: "safe-defaults-no-consent-collection-migration",
  setupConsentState: "consent_required_for_provider_setup",
  setupConsentLabel: "Setup consent: required before provider setup",
  setupConsentBlockerState: "setup_consent_required",
  setupConsentBlockerLabel: "Setup consent blocker: consent collection not approved",
  setupConsentReasonCode: "consent_setup_required",
  setupConsentHandoffState: "setup-consent-handoff-future-gated",
  executionConsentState: "consent_required_for_provider_execution",
  executionConsentLabel: "Execution consent: required before prompt/model execution",
  executionConsentBlockerState: "execution_consent_required",
  executionConsentBlockerLabel: "Execution consent blocker: consent collection not approved",
  executionConsentReasonCode: "consent_execution_required",
  executionConsentHandoffState: "execution-consent-handoff-future-gated",
  providerVisibleDataRequirementState: "provider-visible-data-requirement-none",
  providerVisibleDataRequirementLabel: "Provider-visible data requirement: none",
  dataClassificationPostureState: "data-classification-posture-local-only",
  dataClassificationPostureLabel: "Data classification posture: local-only",
  auditEnvelopePostureState: "audit-envelope-posture-planned",
  auditEnvelopePostureLabel: "Audit envelope posture: planned; no collection",
  localOnlyStatusPosture: "local-only-status-posture-active",
  localOnlyStatusLabel: "Local-only status: active",
  setupFlowReadinessState: "setup_flow_unavailable",
  setupFlowReadinessLabel: "Setup flow readiness: unavailable",
  setupFlowEligibilityState: "setup_flow_eligibility_unavailable",
  setupFlowEligibilityLabel: "Setup flow eligibility: unavailable",
  setupFlowBlockerState: "provider_path_required",
  setupFlowBlockerLabel: "Setup flow blocker: provider path required",
  setupFlowReasonCode: "setup_flow_default_unavailable",
  setupFlowReasonLabel: "Setup flow reason: local-only setup flow unavailable",
  setupFlowApprovalStatus: "setup-flow-approval-missing",
  setupFlowApprovalLabel: "Setup flow approval: USER approval missing",
  consentFlowReadinessState: "consent_flow_required_for_setup",
  consentFlowReadinessLabel: "Consent flow readiness: required for setup",
  consentFlowEligibilityState: "consent_flow_eligibility_unavailable",
  consentFlowEligibilityLabel: "Consent flow eligibility: unavailable",
  consentFlowBlockerState: "consent_collection_not_approved",
  consentFlowBlockerLabel: "Consent flow blocker: consent collection pending USER approval",
  consentFlowReasonCode: "consent_flow_setup_required",
  consentFlowReasonLabel: "Consent flow reason: setup consent required",
  consentFlowApprovalStatus: "consent-flow-approval-missing",
  consentFlowApprovalLabel: "Consent flow approval: USER approval missing",
  consentCollectionPosture: "consent-collection-pending-user-approval",
  consentCollectionLabel: "Consent collection: pending USER approval",
  providerSetupContractReadinessState: "setup_contract_unavailable",
  providerSetupContractReadinessLabel: "Setup contract readiness: unavailable",
  providerSetupContractEligibilityState: "setup_contract_eligibility_unavailable",
  providerSetupContractEligibilityLabel: "Setup contract eligibility: unavailable",
  providerSetupContractBlockerState: "setup_contract_provider_path_required",
  providerSetupContractBlockerLabel: "Setup contract blocker: provider path readiness required",
  providerSetupContractReasonCode: "setup_contract_default_unavailable",
  providerSetupContractReasonLabel: "Setup contract reason: setup contract is local-only",
  providerSetupContractApprovalStatus: "setup-contract-approval-missing",
  providerSetupContractApprovalLabel: "Setup contract approval: USER approval missing",
  providerSetupContractGateState: "setup-contract-gate-blocked",
  futureSetupBranchHandoffState: "future-provider-setup-branch-handoff-ready-for-contract",
  providerSetupFoundationState: "setup_foundation_unavailable",
  providerSetupFoundationLabel: "Setup implementation foundation: unavailable",
  providerSetupFoundationEligibilityState: "setup_foundation_eligibility_unavailable",
  providerSetupFoundationEligibilityLabel: "Setup foundation eligibility: unavailable",
  providerSetupFoundationBlockerState: "setup_foundation_setup_contract_required",
  providerSetupFoundationBlockerLabel: "Setup foundation blocker: setup contract readiness required",
  providerSetupFoundationReasonCode: "setup_foundation_default_unavailable",
  providerSetupFoundationReasonLabel: "Setup foundation reason: local-only safe default",
  providerSetupFoundationApprovalStatus: "setup-foundation-approval-missing",
  providerSetupFoundationApprovalLabel: "Setup foundation approval: USER approval missing",
  providerSetupFoundationGateState: "setup-foundation-gate-blocked",
  providerSetupFoundationValidationStatus: "setup-foundation-validation-fail-closed",
  providerSetupFoundationValidationLabel: "Setup foundation validation: fail-closed",
  providerSetupFoundationPersistenceStatus: "setup-foundation-persistence-disabled",
  providerSetupFoundationPersistenceLabel: "Setup foundation persistence: disabled; no provider credentials stored",
  providerSetupImplementationHandoffState: "future-provider-setup-implementation-handoff-ready",
  consentCollectionFoundationState: "consent_collection_unavailable",
  consentCollectionFoundationLabel: "Consent collection foundation: unavailable",
  consentCollectionEligibilityState: "consent_collection_eligibility_unavailable",
  consentCollectionEligibilityLabel: "Consent collection eligibility: unavailable",
  consentCollectionBlockerState: "consent_collection_consent_flow_required",
  consentCollectionBlockerLabel: "Consent collection blocker: consent flow readiness required",
  consentCollectionReasonCode: "consent_collection_default_unavailable",
  consentCollectionReasonLabel: "Consent collection reason: local-only safe default",
  consentCollectionApprovalStatus: "consent-collection-approval-missing",
  consentCollectionApprovalLabel: "Consent collection approval: USER approval missing",
  consentCollectionGateState: "consent-collection-gate-blocked",
  consentCaptureSurfaceState: "consent-capture-surface-disabled",
  consentCaptureSurfaceLabel: "Consent capture surface: disabled until USER-approved consent work",
  consentDataVisibilityReviewStatus: "data-visibility-review-required",
  consentDataVisibilityReviewLabel: "Consent data visibility review: required before capture",
  consentAuditEnvelopeStatus: "consent-audit-envelope-required",
  consentAuditEnvelopeLabel: "Consent audit envelope: required before capture",
  consentProvenanceStatus: "consent-provenance-required",
  consentProvenanceLabel: "Consent provenance: required before capture",
  consentPersistenceStatus: "consent-persistence-disabled",
  consentPersistenceLabel: "Consent persistence: disabled; no consent stored",
  consentCollectionValidationStatus: "consent-collection-validation-fail-closed",
  consentCollectionValidationLabel: "Consent collection validation: fail-closed",
  futureConsentCaptureHandoffState: "future-consent-capture-branch-handoff-ready",
  consentUxState: "consent_ux_blocked_by_durable_consent",
  consentUxLabel: "Consent UX: blocked by durable consent proof",
  consentUxIntentState: "consent_ux_intent_none",
  consentUxIntentLabel: "Consent UX intent: none selected",
  consentUxSurfaceState: "consent-ux-status-only-local",
  consentUxSurfaceLabel: "Consent UX surface: local status only; no provider action",
  consentUxSetupDisplayState: "durable_consent_missing",
  consentUxSetupDisplayLabel: "Consent UX setup consent: missing",
  consentUxExecutionDisplayState: "durable_consent_missing",
  consentUxExecutionDisplayLabel: "Consent UX execution consent: missing",
  consentUxRevocationResetState: "consent_ux_blocked_by_durable_consent",
  consentUxRevocationResetLabel: "Consent UX revoke/reset: blocked",
  consentUxWritePosture: "consent-ux-write-blocked-fail-closed",
  consentUxWriteLabel: "Consent UX write: blocked fail-closed",
  consentUxStatusProofState: "consent-ux-status-proof-derived-from-durable-state",
  consentUxDesktopDisplayState: "consent-ux-desktop-display-suppressed",
  consentUxProviderSetupGateState: "consent-ux-provider-setup-gate-blocked",
  consentUxProviderExecutionGateState: "consent-ux-provider-execution-gate-disabled",
  providerSetupHandoffPosture: "provider-setup-handoff-future-gated",
  providerSetupHandoffLabel: "Provider setup handoff: future-gated",
  providerConsentHandoffPosture: "provider-consent-handoff-future-gated",
  providerConsentHandoffLabel: "Provider consent handoff: future-gated",
  providerPathHandoffPosture: "provider-path-handoff-future-gated",
  providerPathHandoffLabel: "Provider path handoff: future-gated",
  setupFlowGateState: "setup-flow-gate-blocked",
  consentFlowGateState: "consent-flow-gate-required",
  setupApprovalGateState: "setup-approval-gate-missing",
  executionApprovalGateState: "execution-approval-gate-missing",
  dataVisibilityConsentPosture: "data-visibility-consent-none-required",
  dataVisibilityConsentLabel: "Data visibility consent: none required for local status",
  desktopAiOwnedReadinessDisplayState: "desktop-ai-owned-readiness-display-visible",
  desktopAiOwnedReadinessDisplayLabel: "Desktop AI-owned readiness display: no AI execution active",
  providerSetupFutureGatedPosture: "provider-setup-future-gated",
  providerSetupFutureGatedLabel: "Provider setup: future-gated",
  providerExecutionFutureGatedPosture: "provider-execution-future-gated",
  providerExecutionFutureGatedLabel: "Provider execution: disabled; future-gated",
  providerPathGateState: "provider-path-gate-blocked",
  providerConfigGateState: "provider-config-gate-blocked",
  setupConsentGateState: "setup-consent-gate-required",
  executionConsentGateState: "execution-consent-gate-required",
  providerVisibleDataGateState: "provider-visible-data-gate-none",
  auditGateState: "audit-gate-planned",
  providerSelectionPosture: "provider-selection-pending-user-approval",
  providerSelectionPostureLabel: "Provider selection: pending USER approval",
  adapterSelectionPosture: "adapter-selection-null-local",
  adapterSelectionPostureLabel: "Adapter selection: null local fallback",
  promptAcceptanceGateState: "prompt-acceptance-disabled",
  promptAcceptanceGateLabel: "Prompt acceptance gate: disabled",
  promptRoutingGateState: "prompt-routing-disabled",
  promptRoutingGateLabel: "Prompt routing gate: disabled",
  promptSendPosture: "prompt-send-disabled",
  promptSendLabel: "Prompt send: disabled",
  modelExecutionStatus: "model-execution-disabled",
  modelExecutionStatusLabel: "Model execution status: disabled",
  modelWorkloadReadinessPosture: "model-workload-readiness-disabled",
  modelWorkloadReadinessLabel: "Model workload readiness: disabled",
  providerVisibleDataExecutionPosture: "provider-visible-data-execution-none",
  providerVisibleDataExecutionLabel: "Provider-visible execution data: none",
  externalCallReadinessState: "external-calls-blocked",
  externalCallReadinessLabel: "External call readiness: blocked",
  safetyEvalReadinessState: "safety-eval-readiness-pending",
  safetyEvalReadinessLabel: "Safety/eval readiness: pending",
  dataClassificationGateState: "data-classification-gate-local-only",
  dataClassificationGateLabel: "Data classification gate: local-only",
  executionProofMarker: "execution-proof-pending",
  futureExecutionValidationMarker: "future-execution-validation-marker",
  functionalAiReleaseGateState: "functional-ai-release-gate-pending",
  functionalAiReleaseGateLabel: "Functional-AI release gate: pending",
  v18ReleaseGateState: "v1.8.0-prebeta-release-gate-pending-functional-ai",
  v18ReleaseGateLabel: "v1.8.0-prebeta release gate: pending functional AI proof",
  capabilityPackEligibilityState: "capability-pack-eligibility-blocked",
  capabilityPackEligibilityLabel: "Capability-pack eligibility: blocked until local capability proof",
  capabilityPackManifestValidityState: "manifest-missing",
  capabilityPackManifestValidityLabel: "Capability manifest: missing",
  capabilityPackSourceTrustState: "source-trust-unverified",
  capabilityPackSourceTrustLabel: "Capability-pack source trust: unverified",
  capabilityPackCompatibilityPostureState: "compatibility-blocked",
  capabilityPackCompatibilityPostureLabel: "Capability-pack compatibility: blocked",
  capabilityPackCpuRequirementPosture: "requirement-unprobed",
  capabilityPackGpuRequirementPosture: "requirement-unprobed",
  capabilityPackRamRequirementPosture: "requirement-unprobed",
  capabilityPackDiskRequirementPosture: "requirement-unprobed",
  installIntentState: "install-intent-blocked",
  installIntentLabel: "Install intent: blocked; downloads and install execution remain disabled",
  laneBoundarySchemaVersion: "lane-boundary-state.v1",
  publicLaneBoundaryState: "public-lane-local-assist-only",
  publicLaneBoundaryLabel: "Public Edition: deterministic no-provider assist; provider-visible data none",
  developerLaneBoundaryState: "developer-lane-private-setup-blocked",
  developerLaneBoundaryLabel: "Developer lane: gated; private setup not configured",
  ownerLaneBoundaryState: "owner-lane-private-setup-blocked",
  ownerLaneBoundaryLabel: "Owner lane: gated; private setup not configured",
  privateSetupBoundaryState: "private-setup-blocked",
  privateSetupAuthorized: false,
  privateMaterialVisible: false,
  ownerMemoryEnabled: false,
  ownerAgentsEnabled: false,
  capabilityPackDownloadBlockedReason: "download_blocked_user_approval_required",
  capabilityPackInstallBlockedReason: "install_blocked_manifest_or_user_approval_required",
  capabilityPackUpdateBlockedReason: "update_blocked_user_approval_required",
  capabilityPackUninstallBlockedReason: "uninstall_blocked_no_installed_pack",
  interactionAffordance: "local-assisted-action-available",
  interactionLabel: "Run no-provider check",
  interactionDisabledReason:
    "No-provider check runs inside the AI Control Center only; prompts, providers, downloads, memory, and network remain blocked",
  noProviderFallbackLabel: "No-provider guard active",
  sentToProvider: false,
  canAcceptPrompts: false,
  requiresConsent: true,
  providerOptions: []
};

const backParticles = [];
const frontParticles = [];
const orbitersBack = [];
const orbitersFront = [];
const orbitTrails = [];
const spokes = [];
const swarms = [];
const filaments = [];
const blips = [];
const shellArcs = [];
const fogBands = [];
const relayBursts = [];

function resize() {
  w = backCanvas.width = frontCanvas.width = window.innerWidth;
  h = backCanvas.height = frontCanvas.height = window.innerHeight;
  cx = w * 0.5;
  cy = h * 0.5;
}
window.addEventListener("resize", resize);
resize();

function rand(min, max) {
  return Math.random() * (max - min) + min;
}

function lerp(a, b, m) {
  return a + (b - a) * m;
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function easeOutCubic(x) {
  x = clamp(x, 0, 1);
  return 1 - Math.pow(1 - x, 3);
}

function easeInOutCubic(x) {
  x = clamp(x, 0, 1);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
}

function stagedProgress(startMs, endMs) {
  if (currentState !== "boot" || bootStartTime === null) return 1.0;
  const elapsed = t - bootStartTime;
  return clamp((elapsed - startMs) / (endMs - startMs), 0, 1);
}

function bootStage(stage) {
  if (currentState !== "boot") return 1.0;

  switch (stage) {
    case "ambient":
      return easeOutCubic(stagedProgress(0, 900));
    case "spark":
      return easeOutCubic(stagedProgress(450, 1450));
    case "rings":
      return easeOutCubic(stagedProgress(1000, 2400));
    case "orbiters":
      return easeOutCubic(stagedProgress(1700, 3200));
    case "network":
      return easeOutCubic(stagedProgress(2400, 3900));
    case "stabilize":
      return easeInOutCubic(stagedProgress(3200, 4700));
    default:
      return 1.0;
  }
}

function effectiveVoiceLevel() {
  if (currentState !== "speaking") return 0.0;
  return smoothedVoiceLevel;
}

function speakingBoost(base = 1.0, multiplier = 1.0) {
  return base + effectiveVoiceLevel() * multiplier;
}

function pickProbeRole(isFront, satType) {
  if (satType !== "major") return null;

  const roles = isFront
    ? ["scanner", "ping", "beam", "blink"]
    : ["ping", "beam", "blink", "scanner"];

  return roles[Math.floor(rand(0, roles.length))];
}

function buildOrbiter(isFront, base, idx) {
  const band = idx % 4;
  const bandMin = [0.11, 0.15, 0.20, 0.24][band];
  const bandMax = [0.15, 0.20, 0.25, 0.31][band];

  const bandSpeedMin = [0.0011, 0.0016, 0.0022, 0.0028][band];
  const bandSpeedMax = [0.0022, 0.0032, 0.0044, 0.0056][band];

  const satType = Math.random() > 0.78 ? "major" : "minor";
  const probeRole = pickProbeRole(isFront, satType);

  return {
    angle: rand(0, Math.PI * 2),
    radius: rand(base * bandMin, base * bandMax),
    speed: rand(bandSpeedMin, bandSpeedMax) * (Math.random() > 0.5 ? 1 : -1),
    size: isFront ? rand(1.0, 3.4) : rand(0.7, 2.7),
    alpha: isFront ? rand(0.24, 0.90) : rand(0.18, 0.72),
    wobble: rand(0.003, 0.012),
    wobblePhase: rand(0, 1000),
    ellipseX: rand(0.88, 1.18),
    ellipseY: rand(0.82, 1.16),
    tilt: rand(-0.35, 0.35),
    satType,
    escortCount: Math.random() > 0.72 ? Math.floor(rand(1, 3.99)) : 0,
    linkChance: rand(0.03, 0.18),
    pulsePhase: rand(0, 3000),

    probeRole,
    probePhase: rand(0, 4000),
    probeRate: rand(0.0007, 0.0022),
    pingRadius: rand(8, 22),
    scanArc: rand(0.18, 0.42),
    beamBias: rand(-0.35, 0.35)
  };
}

function buildSceneData() {
  backParticles.length = 0;
  frontParticles.length = 0;
  orbitersBack.length = 0;
  orbitersFront.length = 0;
  orbitTrails.length = 0;
  spokes.length = 0;
  swarms.length = 0;
  filaments.length = 0;
  blips.length = 0;
  shellArcs.length = 0;
  fogBands.length = 0;
  relayBursts.length = 0;

  const base = Math.min(w, h);

  for (let i = 0; i < 170; i++) {
    backParticles.push({
      angle: rand(0, Math.PI * 2),
      radius: rand(base * 0.10, base * 0.40),
      speed: rand(0.0005, 0.0028),
      size: rand(0.4, 1.7),
      alpha: rand(0.02, 0.24),
      phase: rand(0, 3000),
      drift: rand(-0.12, 0.12)
    });
  }

  for (let i = 0; i < 42; i++) {
    frontParticles.push({
      x: rand(0, w),
      y: rand(0, h),
      vx: rand(-0.02, 0.02),
      vy: rand(-0.02, 0.02),
      size: rand(0.7, 2.4),
      alpha: rand(0.03, 0.14),
      depth: rand(0.6, 1.2),
      phase: rand(0, 3000)
    });
  }

  for (let i = 0; i < 26; i++) {
    orbitersBack.push(buildOrbiter(false, base, i));
  }

  for (let i = 0; i < 20; i++) {
    orbitersFront.push(buildOrbiter(true, base, i));
  }

  for (let i = 0; i < 18; i++) {
    orbitTrails.push({
      angle: rand(0, Math.PI * 2),
      radius: rand(base * 0.13, base * 0.30),
      span: rand(0.08, 0.22),
      width: rand(0.5, 1.7),
      alpha: rand(0.02, 0.08),
      speed: rand(-0.00075, 0.00075),
      ellipseX: rand(0.90, 1.16),
      ellipseY: rand(0.86, 1.12),
      tilt: rand(-0.30, 0.30)
    });
  }

  for (let i = 0; i < 22; i++) {
    spokes.push({
      angle: rand(0, Math.PI * 2),
      length: rand(base * 0.05, base * 0.20),
      alpha: rand(0.025, 0.10),
      width: rand(0.4, 1.1),
      drift: rand(-0.0007, 0.0007)
    });
  }

  for (let i = 0; i < 5; i++) {
    swarms.push({
      baseAngle: rand(0, Math.PI * 2),
      spread: rand(0.22, 0.52),
      radiusMin: rand(base * 0.14, base * 0.18),
      radiusMax: rand(base * 0.22, base * 0.33),
      drift: rand(-0.0009, 0.0009),
      density: Math.floor(rand(14, 26)),
      phase: rand(0, 2000)
    });
  }

  for (let i = 0; i < 11; i++) {
    filaments.push({
      a1: rand(0, Math.PI * 2),
      a2: rand(0, Math.PI * 2),
      r1: rand(base * 0.08, base * 0.18),
      r2: rand(base * 0.14, base * 0.30),
      alpha: rand(0.025, 0.11),
      life: rand(0.2, 1.0),
      decay: rand(0.002, 0.007)
    });
  }

  for (let i = 0; i < 13; i++) {
    shellArcs.push({
      radius: rand(base * 0.16, base * 0.25),
      start: rand(0, Math.PI * 2),
      span: rand(0.18, 0.86),
      width: rand(0.5, 2.2),
      alpha: rand(0.03, 0.13),
      speed: rand(-0.0015, 0.0015),
      jitter: rand(0, 1000)
    });
  }

  for (let i = 0; i < 4; i++) {
    fogBands.push({
      angle: rand(0, Math.PI * 2),
      radius: rand(base * 0.18, base * 0.28),
      width: rand(base * 0.02, base * 0.06),
      alpha: rand(0.015, 0.05),
      speed: rand(-0.0005, 0.0005),
      phase: rand(0, 2000)
    });
  }
}
buildSceneData();
window.addEventListener("resize", buildSceneData);

function stateSpeedMultiplier() {
  let base;
  switch (currentState) {
    case "speaking": base = 1.45; break;
    case "processing": base = 2.0; break;
    case "dormant": base = 0.38; break;
    case "boot": base = 0.68; break;
    default: base = 1.0;
  }
  return base * speakingBoost(1.0, 0.30);
}

function stateParticleSpeedMultiplier() {
  let base;
  switch (currentState) {
    case "speaking": base = 1.45; break;
    case "processing": base = 2.2; break;
    case "dormant": base = 0.45; break;
    case "boot": base = 0.70; break;
    default: base = 1.0;
  }
  return base * speakingBoost(1.0, 0.22);
}

function stateEnergyMultiplier() {
  let base;
  switch (currentState) {
    case "speaking": base = 1.25; break;
    case "processing": base = 1.65; break;
    case "dormant": base = 0.52; break;
    case "boot": base = ignition; break;
    default: base = 1.0;
  }
  return base * speakingBoost(1.0, 0.55);
}

function bootIntensity() {
  if (currentState !== "boot") return 1.0;
  ignition = Math.min(1, ignition + 0.0036);
  return ignition;
}

function clear() {
  bctx.clearRect(0, 0, w, h);
  fctx.clearRect(0, 0, w, h);
}

function drawBackgroundNoise() {
  const baseCount = currentState === "processing" ? 58 : 32;
  const count = Math.floor(baseCount * bootStage("ambient"));
  for (let i = 0; i < count; i++) {
    const x = rand(0, w);
    const y = rand(0, h);
    const a = rand(0.008, 0.045) * bootStage("ambient") * speakingBoost(1.0, 0.30);
    bctx.fillStyle = `rgba(110,220,255,${a})`;
    bctx.fillRect(x, y, 1, 1);
  }
}

function drawBackParticles() {
  const intensity = bootIntensity() * bootStage("ambient") * speakingBoost(1.0, 0.38);

  backParticles.forEach((p, idx) => {
    p.angle += p.speed * stateParticleSpeedMultiplier();
    const radialDrift = Math.sin(t * 0.0008 + p.phase) * (2.0 + p.drift * 5.0 + effectiveVoiceLevel() * 2.2);
    const x = cx + Math.cos(p.angle + p.phase * 0.0006) * (p.radius + radialDrift);
    const y = cy + Math.sin(p.angle + p.phase * 0.0005) * (p.radius - radialDrift * 0.7);

    const flicker = 0.35 + 0.65 * Math.sin(t * 0.0018 + p.phase + idx);

    bctx.beginPath();
    bctx.arc(x, y, p.size, 0, Math.PI * 2);
    bctx.fillStyle = `rgba(110,230,255,${p.alpha * flicker * intensity})`;
    bctx.shadowBlur = 8 + effectiveVoiceLevel() * 5;
    bctx.shadowColor = "rgba(100,220,255,0.16)";
    bctx.fill();
  });

  bctx.shadowBlur = 0;
}

function drawFrontParticles() {
  const energy = stateEnergyMultiplier() * bootStage("orbiters");

  frontParticles.forEach((p, i) => {
    p.x += p.vx * p.depth * energy;
    p.y += p.vy * p.depth * energy;

    if (p.x < -20) p.x = w + 20;
    if (p.x > w + 20) p.x = -20;
    if (p.y < -20) p.y = h + 20;
    if (p.y > h + 20) p.y = -20;

    const flicker = 0.45 + 0.55 * Math.sin(t * 0.001 + p.phase + i);

    fctx.beginPath();
    fctx.arc(p.x, p.y, p.size * speakingBoost(1.0, 0.22), 0, Math.PI * 2);
    fctx.fillStyle = `rgba(160,240,255,${p.alpha * flicker * speakingBoost(1.0, 0.45)})`;
    fctx.shadowBlur = 6 + effectiveVoiceLevel() * 4;
    fctx.shadowColor = "rgba(130,230,255,0.12)";
    fctx.fill();
  });

  fctx.shadowBlur = 0;
}

function drawAtmosphericBands() {
  const intensity = bootIntensity() * bootStage("ambient") * speakingBoost(1.0, 0.28);

  fogBands.forEach((band) => {
    band.angle += band.speed * stateSpeedMultiplier();
    const x = cx + Math.cos(band.angle) * band.radius;
    const y = cy + Math.sin(band.angle) * band.radius;
    const alpha = band.alpha * (0.6 + 0.4 * Math.sin(t * 0.001 + band.phase)) * intensity;

    bctx.beginPath();
    bctx.arc(x, y, band.width * speakingBoost(1.0, 0.18), 0, Math.PI * 2);
    bctx.fillStyle = `rgba(100,220,255,${alpha})`;
    bctx.shadowBlur = 20 + effectiveVoiceLevel() * 7;
    bctx.shadowColor = "rgba(80,190,255,0.10)";
    bctx.fill();
  });

  bctx.shadowBlur = 0;
}

function drawSpokes() {
  const intensity = bootIntensity() * bootStage("rings") * speakingBoost(1.0, 0.25);
  bctx.save();
  bctx.translate(cx, cy);

  spokes.forEach((s, idx) => {
    s.angle += s.drift * stateSpeedMultiplier();
    const a = s.angle + Math.sin(t * 0.00045 + idx * 1.7) * (0.18 + effectiveVoiceLevel() * 0.06);
    const r1 = Math.min(w, h) * 0.045;
    const r2 = r1 + s.length + effectiveVoiceLevel() * 4.0;

    bctx.beginPath();
    bctx.moveTo(Math.cos(a) * r1, Math.sin(a) * r1);
    bctx.lineTo(Math.cos(a) * r2, Math.sin(a) * r2);
    bctx.lineWidth = s.width * speakingBoost(1.0, 0.10);
    bctx.strokeStyle = `rgba(90,220,255,${s.alpha * intensity})`;
    bctx.stroke();
  });

  bctx.restore();
}

function drawArcBand(radius, rotation, count, spanDeg, alpha, width, blur, irregularity = 0.0) {
  bctx.save();
  bctx.translate(cx, cy);
  bctx.rotate(rotation);
  bctx.lineCap = "round";
  bctx.lineWidth = width * speakingBoost(1.0, 0.08);
  bctx.shadowBlur = blur + effectiveVoiceLevel() * 7;
  bctx.shadowColor = "rgba(80,210,255,0.18)";

  for (let i = 0; i < count; i++) {
    const start = (Math.PI * 2 / count) * i + Math.sin(t * 0.0011 + i * 1.3) * (irregularity + effectiveVoiceLevel() * 0.02);
    const end = start + (Math.PI / 180) * (spanDeg + Math.sin(t * 0.0014 + i) * (3.5 + effectiveVoiceLevel() * 4.0));

    bctx.beginPath();
    bctx.strokeStyle = `rgba(100,230,255,${alpha * speakingBoost(1.0, 0.45)})`;
    bctx.arc(0, 0, radius * speakingBoost(1.0, 0.02), start, end);
    bctx.stroke();
  }

  bctx.restore();
  bctx.shadowBlur = 0;
}

function drawBrokenShells() {
  const intensity = bootIntensity() * bootStage("rings") * speakingBoost(1.0, 0.35);

  shellArcs.forEach((arc, idx) => {
    arc.start += arc.speed * stateSpeedMultiplier();
    const pulse = 0.5 + 0.5 * Math.sin(t * 0.0011 + arc.jitter);

    bctx.beginPath();
    bctx.arc(
      cx,
      cy,
      arc.radius + Math.sin(t * 0.0007 + idx) * (2.2 + effectiveVoiceLevel() * 2.8),
      arc.start,
      arc.start + arc.span + pulse * 0.12
    );
    bctx.lineWidth = arc.width * speakingBoost(1.0, 0.10);
    bctx.strokeStyle = `rgba(120,235,255,${arc.alpha * pulse * intensity})`;
    bctx.shadowBlur = 12 + effectiveVoiceLevel() * 6;
    bctx.shadowColor = "rgba(100,220,255,0.14)";
    bctx.stroke();
  });

  bctx.shadowBlur = 0;
}

function drawOrbitTrails() {
  const intensity = bootIntensity() * bootStage("orbiters") * speakingBoost(1.0, 0.42);

  orbitTrails.forEach((trail) => {
    trail.angle += trail.speed * stateSpeedMultiplier();

    bctx.save();
    bctx.translate(cx, cy);
    bctx.rotate(trail.tilt);

    const segments = 8;
    for (let s = 0; s < segments; s++) {
      const localStart = trail.angle + s * 0.08;
      const localEnd = localStart + trail.span * (1 - s / segments);

      bctx.beginPath();
      for (let a = localStart; a <= localEnd; a += 0.04) {
        const x = Math.cos(a) * trail.radius * trail.ellipseX;
        const y = Math.sin(a) * trail.radius * trail.ellipseY;
        if (a === localStart) bctx.moveTo(x, y);
        else bctx.lineTo(x, y);
      }
      bctx.lineWidth = trail.width * (1 - s / (segments + 2)) * speakingBoost(1.0, 0.12);
      bctx.strokeStyle = `rgba(120,235,255,${trail.alpha * (1 - s / segments) * intensity})`;
      bctx.stroke();
    }

    bctx.restore();
  });
}

function orbiterPosition(o) {
  const localRadius = o.radius + Math.sin(t * o.wobble + o.wobblePhase) * (6.5 + effectiveVoiceLevel() * 4.0);
  const rawX = Math.cos(o.angle) * localRadius * o.ellipseX;
  const rawY = Math.sin(o.angle) * localRadius * o.ellipseY;

  const cosT = Math.cos(o.tilt);
  const sinT = Math.sin(o.tilt);

  return {
    x: cx + rawX * cosT - rawY * sinT,
    y: cy + rawX * sinT + rawY * cosT
  };
}

function spawnRelayBurst(x1, y1, x2, y2, alpha) {
  if (relayBursts.length > 14) return;
  relayBursts.push({
    x1, y1, x2, y2,
    life: 1.0,
    alpha,
    speed: rand(0.0015, 0.003)
  });
}

function drawProbeSatellite(ctx, o, pos, r, front, intensity) {
  if (!o.probeRole) return;

  const energy = stateEnergyMultiplier();
  const phase = t * o.probeRate + o.probePhase;
  const probeAlpha = intensity * (0.35 + 0.65 * Math.abs(Math.sin(phase))) * speakingBoost(1.0, 0.55);

  if (o.probeRole === "scanner") {
    const angle = o.angle + o.beamBias + Math.sin(phase * 0.7) * 0.18;
    const coneLen = r * (8.0 + effectiveVoiceLevel() * 3.5);

    ctx.save();
    ctx.translate(pos.x, pos.y);
    ctx.rotate(angle);

    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, coneLen, -o.scanArc, o.scanArc);
    ctx.closePath();
    ctx.fillStyle = `rgba(150,240,255,${0.08 * probeAlpha * energy})`;
    ctx.filter = "blur(2px)";
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(coneLen, 0);
    ctx.lineWidth = 0.7 + effectiveVoiceLevel() * 0.35;
    ctx.strokeStyle = `rgba(180,245,255,${0.12 * probeAlpha})`;
    ctx.stroke();

    ctx.restore();
    ctx.filter = "none";
  }

  if (o.probeRole === "ping") {
    const pingProgress = (Math.sin(phase) + 1) * 0.5;
    const pr = r * (1.8 + pingProgress * (4.5 + effectiveVoiceLevel() * 2.2));

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, pr, 0, Math.PI * 2);
    ctx.lineWidth = 0.9 + effectiveVoiceLevel() * 0.25;
    ctx.strokeStyle = `rgba(160,240,255,${0.12 * (1 - pingProgress) * probeAlpha})`;
    ctx.stroke();
  }

  if (o.probeRole === "beam") {
    const toCoreX = cx - pos.x;
    const toCoreY = cy - pos.y;
    const len = Math.hypot(toCoreX, toCoreY);
    if (len > 0) {
      const nx = toCoreX / len;
      const ny = toCoreY / len;
      const beamLen = Math.min(len * (0.55 + effectiveVoiceLevel() * 0.12), r * 18);

      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      ctx.lineTo(pos.x + nx * beamLen, pos.y + ny * beamLen);
      ctx.lineWidth = (front ? 0.9 : 0.7) + effectiveVoiceLevel() * 0.25;
      ctx.strokeStyle = `rgba(160,240,255,${0.10 * probeAlpha})`;
      ctx.shadowBlur = 10 + effectiveVoiceLevel() * 8;
      ctx.shadowColor = "rgba(120,220,255,0.18)";
      ctx.stroke();
      ctx.shadowBlur = 0;
    }
  }

  if (o.probeRole === "blink") {
    const blink = Math.pow((Math.sin(phase * 2.2) + 1) * 0.5, 3);

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, r * (1.15 + blink * (0.55 + effectiveVoiceLevel() * 0.35)), 0, Math.PI * 2);
    ctx.fillStyle = `rgba(220,250,255,${0.22 * blink * probeAlpha})`;
    ctx.shadowBlur = 14 + effectiveVoiceLevel() * 8;
    ctx.shadowColor = "rgba(180,245,255,0.30)";
    ctx.fill();
    ctx.shadowBlur = 0;
  }
}

function drawOrbiterSet(ctx, set, front = false) {
  const intensity = bootIntensity() * bootStage("orbiters") * speakingBoost(1.0, 0.48);
  const energy = stateEnergyMultiplier() * bootStage("network") * speakingBoost(1.0, 0.40);
  const positions = [];

  set.forEach((o, idx) => {
    o.angle += o.speed * stateSpeedMultiplier();
    const pos = orbiterPosition(o);
    positions.push(pos);

    const pulse = 0.55 + 0.45 * Math.sin(t * 0.002 + o.pulsePhase);
    const r = o.size * (o.satType === "major" ? 1.35 : 1.0) * speakingBoost(1.0, 0.08);

    drawProbeSatellite(ctx, o, pos, r, front, intensity);

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(175,242,255,${o.alpha * pulse * intensity})`;
    ctx.shadowBlur = (front ? 18 : 14) + effectiveVoiceLevel() * 8;
    ctx.shadowColor = front ? "rgba(120,230,255,0.55)" : "rgba(100,220,255,0.38)";
    ctx.fill();

    if (o.satType === "major") {
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, r * (2.3 + effectiveVoiceLevel() * 0.18), 0, Math.PI * 2);
      ctx.lineWidth = 0.8 + effectiveVoiceLevel() * 0.12;
      ctx.strokeStyle = `rgba(140,235,255,${0.12 * pulse * intensity})`;
      ctx.stroke();
    }

    for (let e = 0; e < o.escortCount; e++) {
      const ea = o.angle + (e + 1) * 0.22 + Math.sin(t * 0.0011 + idx + e) * (0.03 + effectiveVoiceLevel() * 0.02);
      const er = r * (2.2 + e * 0.75 + effectiveVoiceLevel() * 0.4);
      const ex = pos.x + Math.cos(ea) * er;
      const ey = pos.y + Math.sin(ea) * er;

      ctx.beginPath();
      ctx.arc(ex, ey, Math.max(0.65, r * 0.28) * speakingBoost(1.0, 0.10), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(150,235,255,${0.28 * pulse * intensity})`;
      ctx.shadowBlur = 8 + effectiveVoiceLevel() * 6;
      ctx.shadowColor = "rgba(120,230,255,0.20)";
      ctx.fill();

      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      ctx.lineTo(ex, ey);
      ctx.lineWidth = 0.5 + effectiveVoiceLevel() * 0.08;
      ctx.strokeStyle = `rgba(120,230,255,${0.06 * intensity})`;
      ctx.stroke();
    }

    if (Math.random() < o.linkChance * energy) {
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(pos.x, pos.y);
      ctx.lineWidth = (front ? 0.55 : 0.4) + effectiveVoiceLevel() * 0.08;
      ctx.strokeStyle = `rgba(100,220,255,${0.05 * intensity})`;
      ctx.stroke();
    }
  });

  for (let i = 0; i < positions.length; i++) {
    if (Math.random() > 0.035 * energy) continue;
    const j = Math.floor(rand(0, positions.length));
    if (i === j) continue;
    const p1 = positions[i];
    const p2 = positions[j];
    const alpha = front ? 0.14 : 0.09;

    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.lineWidth = 0.55 + effectiveVoiceLevel() * 0.12;
    ctx.strokeStyle = `rgba(130,235,255,${alpha * intensity * bootStage("network") * speakingBoost(1.0, 0.55)})`;
    ctx.shadowBlur = 10 + effectiveVoiceLevel() * 6;
    ctx.shadowColor = "rgba(120,225,255,0.14)";
    ctx.stroke();

    if (Math.random() > 0.6 && bootStage("network") > 0.15) {
      spawnRelayBurst(p1.x, p1.y, p2.x, p2.y, alpha * bootStage("network") * speakingBoost(1.0, 0.65));
    }
  }

  ctx.shadowBlur = 0;
}

function drawRelayBursts() {
  const gate = bootStage("network") * speakingBoost(1.0, 0.70);

  for (let i = relayBursts.length - 1; i >= 0; i--) {
    const r = relayBursts[i];
    r.life -= r.speed * Math.max(0.5, gate);

    if (r.life <= 0) {
      relayBursts.splice(i, 1);
      continue;
    }

    const progress = Math.pow(1 - r.life, 1.6);
    const px = lerp(r.x1, r.x2, progress);
    const py = lerp(r.y1, r.y2, progress);

    fctx.beginPath();
    fctx.arc(px, py, 2.1 + effectiveVoiceLevel() * 0.9, 0, Math.PI * 2);
    fctx.fillStyle = `rgba(200,248,255,${r.alpha * r.life * gate})`;
    fctx.shadowBlur = 12 + effectiveVoiceLevel() * 10;
    fctx.shadowColor = "rgba(150,240,255,0.35)";
    fctx.fill();
  }
  fctx.shadowBlur = 0;
}

function drawSwarms() {
  const energy = stateEnergyMultiplier() * bootStage("rings");
  const intensity = bootIntensity() * bootStage("rings") * speakingBoost(1.0, 0.35);

  swarms.forEach((swarm, si) => {
    swarm.baseAngle += swarm.drift * stateSpeedMultiplier();

    for (let i = 0; i < swarm.density; i++) {
      const local = i / swarm.density;
      const angle =
        swarm.baseAngle +
        (local - 0.5) * swarm.spread +
        Math.sin(t * 0.0013 + swarm.phase + i) * 0.04;

      const r = lerp(swarm.radiusMin, swarm.radiusMax, local) +
        Math.sin(t * 0.001 + i + si * 10) * (4.0 + effectiveVoiceLevel() * 2.0);

      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;

      const alpha = (0.05 + local * 0.13) * intensity * energy;
      const size = (0.5 + local * 1.6) * speakingBoost(1.0, 0.08);

      bctx.beginPath();
      bctx.arc(x, y, size, 0, Math.PI * 2);
      bctx.fillStyle = `rgba(140,238,255,${alpha})`;
      bctx.shadowBlur = 9 + effectiveVoiceLevel() * 6;
      bctx.shadowColor = "rgba(110,225,255,0.18)";
      bctx.fill();
    }
  });

  bctx.shadowBlur = 0;
}

function refreshFilaments() {
  for (let i = 0; i < filaments.length; i++) {
    const f = filaments[i];
    f.life -= f.decay * (currentState === "processing" ? 2.0 : 1.0);

    if (f.life <= 0) {
      const base = Math.min(w, h);
      filaments[i] = {
        a1: rand(0, Math.PI * 2),
        a2: rand(0, Math.PI * 2),
        r1: rand(base * 0.08, base * 0.18),
        r2: rand(base * 0.14, base * 0.30),
        alpha: rand(0.025, 0.11),
        life: rand(0.4, 1.0),
        decay: rand(0.002, 0.007)
      };
    }
  }
}

function drawFilaments() {
  const stage = bootStage("rings");
  refreshFilaments();
  const intensity = bootIntensity() * stage * speakingBoost(1.0, 0.42);

  filaments.forEach((f, idx) => {
    const a1 = f.a1 + Math.sin(t * 0.0008 + idx) * 0.12;
    const a2 = f.a2 + Math.cos(t * 0.0010 + idx * 1.2) * 0.15;

    const x1 = cx + Math.cos(a1) * f.r1;
    const y1 = cy + Math.sin(a1) * f.r1;
    const x2 = cx + Math.cos(a2) * f.r2;
    const y2 = cy + Math.sin(a2) * f.r2;

    const mx = (x1 + x2) * 0.5 + Math.sin(t * 0.0015 + idx) * (8 + effectiveVoiceLevel() * 4);
    const my = (y1 + y2) * 0.5 + Math.cos(t * 0.0012 + idx) * (8 + effectiveVoiceLevel() * 4);

    bctx.beginPath();
    bctx.moveTo(x1, y1);
    bctx.quadraticCurveTo(mx, my, x2, y2);
    bctx.lineWidth = 0.8 + effectiveVoiceLevel() * 0.22;
    bctx.strokeStyle = `rgba(120,235,255,${f.alpha * f.life * intensity})`;
    bctx.shadowBlur = 10 + effectiveVoiceLevel() * 8;
    bctx.shadowColor = "rgba(100,220,255,0.14)";
    bctx.stroke();
  });

  bctx.shadowBlur = 0;
}

function spawnBlip() {
  if (bootStage("network") < 0.25 && currentState === "boot") return;

  const chance =
    currentState === "processing" ? 0.21 :
    currentState === "speaking" ? 0.11 + effectiveVoiceLevel() * 0.08 :
    currentState === "boot" ? 0.05 :
    0.04;

  if (Math.random() > chance) return;

  const r = rand(Math.min(w, h) * 0.11, Math.min(w, h) * 0.31);
  const a = rand(0, Math.PI * 2);

  blips.push({
    x: cx + Math.cos(a) * r,
    y: cy + Math.sin(a) * r,
    life: 1.0,
    size: rand(1.0, 2.8)
  });
}

function drawBlips() {
  const gate = currentState === "boot" ? bootStage("network") : 1.0;
  spawnBlip();

  for (let i = blips.length - 1; i >= 0; i--) {
    const b = blips[i];
    b.life -= currentState === "processing" ? 0.045 : 0.026;

    if (b.life <= 0) {
      blips.splice(i, 1);
      continue;
    }

    fctx.beginPath();
    fctx.arc(b.x, b.y, b.size * speakingBoost(1.0, 0.15), 0, Math.PI * 2);
    fctx.fillStyle = `rgba(185,245,255,${b.life * gate * speakingBoost(1.0, 0.42)})`;
    fctx.shadowBlur = 20 + effectiveVoiceLevel() * 8;
    fctx.shadowColor = "rgba(120,230,255,0.78)";
    fctx.fill();

    fctx.beginPath();
    fctx.moveTo(b.x - 7, b.y);
    fctx.lineTo(b.x + 7, b.y);
    fctx.moveTo(b.x, b.y - 7);
    fctx.lineTo(b.x, b.y + 7);
    fctx.strokeStyle = `rgba(120,230,255,${0.18 * b.life * gate * speakingBoost(1.0, 0.45)})`;
    fctx.lineWidth = 1 + effectiveVoiceLevel() * 0.15;
    fctx.stroke();
  }

  fctx.shadowBlur = 0;
}

function drawOrganicSpeechCore(ctx, x, y, baseRadius, voice, spark, intensity) {
  const points = 72;

  // reduced deformation so the shape stays controlled
  const deform = 0.05 + voice * 0.16;

  // cleaner, lower-frequency motion
  const lobeA = 2.4 + voice * 1.2;
  const lobeB = 3.6 + voice * 1.6;
  const lobeC = 5.2 + voice * 2.0;

  ctx.beginPath();

  for (let i = 0; i <= points; i++) {
    const a = (i / points) * Math.PI * 2;

    const wave1 = Math.sin(a * lobeA + t * 0.006) * deform;
    const wave2 = Math.sin(a * lobeB - t * 0.004 + 1.2) * deform * 0.45;
    const wave3 = Math.sin(a * lobeC + t * 0.008 + 2.1) * deform * 0.25;

    const frontBias =
      Math.max(0, Math.cos(a - Math.sin(t * 0.002) * 0.22)) *
      voice * 0.13;

    const radius = baseRadius * (1 + wave1 + wave2 + wave3 + frontBias);

    const px = x + Math.cos(a) * radius;
    const py = y + Math.sin(a) * radius;

    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }

  ctx.closePath();
  ctx.fillStyle = `rgba(140,235,255,${0.050 * intensity * speakingBoost(1.0, 1.03)})`;
  ctx.shadowBlur = 18 + voice * 20;
  ctx.shadowColor = "rgba(100,220,255,0.38)";
  ctx.fill();

  // calmer inner shell
  ctx.beginPath();
  for (let i = 0; i <= points; i++) {
    const a = (i / points) * Math.PI * 2;

    const wave1 =
      Math.sin(a * (lobeA + 0.8) - t * 0.007 + 0.8) *
      deform * 0.5;

    const wave2 =
      Math.sin(a * (lobeB + 1.5) + t * 0.005 + 2.0) *
      deform * 0.22;

    const radius = baseRadius * 0.72 * (1 + wave1 + wave2);

    const px = x + Math.cos(a) * radius;
    const py = y + Math.sin(a) * radius;

    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }

  ctx.closePath();
  ctx.fillStyle = `rgba(170,242,255,${0.03 + voice * 0.07})`;
  ctx.shadowBlur = 12 + voice * 14;
  ctx.shadowColor = "rgba(130,225,255,0.30)";
  ctx.fill();

  ctx.shadowBlur = 0;
}

function drawCoreSheen() {
  const base = Math.min(w, h);
  const intensity = bootIntensity();
  const energy = stateEnergyMultiplier();

  const spark = bootStage("spark");
  const voice = effectiveVoiceLevel();

  const ox = Math.sin(t * 0.0012) * 4.5 * spark * speakingBoost(1.0, 0.45);
  const oy = Math.cos(t * 0.0009) * 3.8 * spark * speakingBoost(1.0, 0.45);

  const outerRadius =
    base * (0.018 + 0.042 * spark) *
    (1.0 + voice * 0.42);

  if (voice > 0.04 && currentState === "speaking") {
    drawOrganicSpeechCore(
      bctx,
      cx + ox,
      cy + oy,
      outerRadius,
      voice,
      spark,
      intensity * energy * spark
    );
  } else {
    bctx.beginPath();
    bctx.arc(cx + ox, cy + oy, outerRadius, 0, Math.PI * 2);
    bctx.fillStyle = `rgba(140,235,255,${0.05 * intensity * energy * spark * speakingBoost(1.0, 0.95)})`;
    bctx.shadowBlur = 48 * spark + voice * 34;
    bctx.shadowColor = "rgba(100,220,255,0.34)";
    bctx.fill();
    bctx.shadowBlur = 0;
  }

  const innerRadius =
    base * (0.006 + 0.012 * spark) *
    (1.0 + voice * 0.78);

  fctx.beginPath();
  fctx.arc(cx + ox * 0.45, cy + oy * 0.45, innerRadius, 0, Math.PI * 2);
  fctx.fillStyle = `rgba(235,250,255,${0.82 * intensity * spark * speakingBoost(1.0, 1.05)})`;
  fctx.shadowBlur = 26 * spark + voice * 30;
  fctx.shadowColor = "rgba(180,245,255,0.92)";
  fctx.fill();

  if (voice > 0.08) {
    const bloomRadius =
      base * (0.012 + 0.020 * spark) *
      (1.0 + voice * 0.95);

    fctx.beginPath();
    fctx.arc(cx, cy, bloomRadius, 0, Math.PI * 2);
    fctx.fillStyle = `rgba(170,240,255,${0.05 + voice * 0.14})`;
    fctx.shadowBlur = 24 + voice * 30;
    fctx.shadowColor = "rgba(130,225,255,0.40)";
    fctx.fill();
  }

  bctx.shadowBlur = 0;
  fctx.shadowBlur = 0;
}

function drawArrivalPulse() {
  if (currentState !== "boot") return;

  const base = Math.min(w, h);
  const e = bootStage("spark");
  const ringR = lerp(base * 0.02, base * 0.21, e);

  fctx.beginPath();
  fctx.arc(cx, cy, ringR, 0, Math.PI * 2);
  fctx.lineWidth = 2.0;
  fctx.strokeStyle = `rgba(180,245,255,${0.32 * (1 - e)})`;
  fctx.shadowBlur = 20 * e;
  fctx.shadowColor = "rgba(130,235,255,0.28)";
  fctx.stroke();
  fctx.shadowBlur = 0;
}

function drawAnimatedRings() {
  const base = Math.min(w, h);
  const s = stateSpeedMultiplier();
  const intensity = bootIntensity() * bootStage("rings");

  drawArcBand(base * 0.122, t * 0.00028 * s, 7, 15, 0.09 * intensity, 1.9, 12, 0.12);
  drawArcBand(base * 0.152, -t * 0.00019 * s, 9, 11, 0.07 * intensity, 1.4, 10, 0.15);
  drawArcBand(base * 0.186, t * 0.00014 * s, 11, 8, 0.055 * intensity, 1.1, 8, 0.18);
}

function drawForegroundSweep() {
  const energy = stateEnergyMultiplier() * bootStage("network") * speakingBoost(1.0, 0.70);
  const r = Math.min(w, h) * 0.23;
  const a = t * 0.00028 * stateSpeedMultiplier();

  fctx.save();
  fctx.translate(cx, cy);
  fctx.rotate(a);
  fctx.beginPath();
  fctx.moveTo(0, 0);
  fctx.arc(0, 0, r * speakingBoost(1.0, 0.03), -0.10, 0.12 + effectiveVoiceLevel() * 0.06);
  fctx.closePath();
  fctx.fillStyle = `rgba(130,235,255,${0.035 * energy})`;
  fctx.filter = "blur(4px)";
  fctx.fill();
  fctx.restore();
  fctx.filter = "none";
}

function renderCommandOverlay() {
  if (!commandOverlay) return;

  const state = commandOverlayState || {};
  const isVisible = Boolean(state.visible);
  const isInputArmed = Boolean(state.input_armed) && state.phase === "entry";
  const isLocked = state.phase === "confirm" || state.phase === "result";
  commandOverlay.classList.toggle("visible", isVisible);
  commandOverlay.setAttribute("aria-hidden", isVisible ? "false" : "true");

  if (commandInputShell) {
    commandInputShell.classList.toggle("is-armed", isInputArmed);
    commandInputShell.classList.toggle("is-locked", isLocked);
  }

  if (!isVisible) {
    return;
  }

  if (commandInputText) {
    commandInputText.textContent = state.input_text || "";
  }

  if (commandStatus) {
    commandStatus.className = "command-status";
    if (state.status_kind && state.status_kind !== "idle") {
      commandStatus.classList.add(`status-${state.status_kind}`);
    }
    if (state.status_text) {
      commandStatus.textContent = state.status_text;
    } else if (state.phase === "entry" && !isInputArmed) {
      commandStatus.textContent = "Press Enter to activate the command box.";
    } else {
      commandStatus.textContent = "";
    }
  }

  if (commandAmbiguous) {
    const titles = Array.isArray(state.ambiguous_titles) ? state.ambiguous_titles : [];
    commandAmbiguous.textContent =
      titles.length > 0 ? `Matches: ${titles.join(" • ")}` : "";
  }

  if (commandHint) {
    if (state.phase === "confirm") {
      commandHint.textContent = "Review the resolved action before execution.";
    } else if (state.phase === "result") {
      commandHint.textContent = "Returning to passive desktop mode.";
    } else if (!isInputArmed) {
      commandHint.textContent = "Press Enter to activate the command box. Esc closes.";
    } else {
      commandHint.textContent = "Type a saved action or alias, then press Enter.";
    }
  }

  const action = state.pending_action || null;
  const showConfirm = state.phase === "confirm" && action;
  if (commandConfirmation) {
    commandConfirmation.hidden = !showConfirm;
  }

  if (showConfirm) {
    if (commandConfirmRequest) {
      commandConfirmRequest.textContent = state.typed_request || "";
    }
    if (commandConfirmTitle) {
      commandConfirmTitle.textContent = action.title || "";
    }
    if (commandConfirmKind) {
      commandConfirmKind.textContent = action.target_kind || "";
    }
    if (commandConfirmTarget) {
      commandConfirmTarget.textContent = action.target || "";
    }
  }
}

function setTextContent(element, text) {
  if (element) {
    element.textContent = text;
  }
}

function setAIProviderTrayOpen(open) {
  if (!aiProviderTray || !aiProviderTrayWindow) return;

  const shouldOpen = false;
  aiProviderTray.hidden = true;
  aiProviderTrayWindow.hidden = true;
  aiProviderTray.setAttribute("aria-hidden", "true");
  aiProviderTray.setAttribute("tabindex", "-1");
  aiProviderTray.setAttribute("aria-expanded", "false");
  aiProviderTray.dataset.aiTrayState = "closed";
  aiProviderTray.dataset.aiControlCenterState = "native-tray-only";
  aiProviderTray.dataset.desktopTrayDoorway = "native-system-tray";
  aiProviderTray.dataset.interactive = "false";
  aiProviderTrayWindow.dataset.aiTrayState = "closed";
  aiProviderTrayWindow.dataset.aiControlCenterState = shouldOpen ? "open" : "native-tray-only";
}

function renderAIProviderTrayState(state, displayVisible, localActionAvailable) {
  const trayVisible = Boolean(displayVisible || localActionAvailable);
  const providerVisibleData = state.providerVisibleData || "none";
  const promptSend = state.promptSendPosture || "prompt-send-disabled";
  const networkEgress = state.networkEgressState || "network-egress-blocked";
  const memoryIndexing = state.memoryIndexingState || "memory-indexing-disabled";
  const providerExecution =
    state.providerExecutionGateState === "provider-execution-disabled" &&
    state.modelExecutionGateState === "model-execution-disabled"
      ? "disabled and blocked"
      : (state.providerExecutionGateLabel || "disabled and blocked");
  const capabilityPosture =
    state.installIntentLabel ||
    "Install intent: blocked; downloads and install execution remain disabled";
  const laneBoundary =
    `${state.publicLaneBoundaryLabel || "Public Edition: deterministic no-provider assist"}; ` +
    `${state.developerLaneBoundaryLabel || "Developer lane: gated; private setup not configured"}; ` +
    `${state.ownerLaneBoundaryLabel || "Owner lane: gated; private setup not configured"}`;

  if (aiLocalStatusSurface) {
    aiLocalStatusSurface.hidden = !trayVisible;
    aiLocalStatusSurface.dataset.statusOnly = "true";
    aiLocalStatusSurface.dataset.interactive = "false";
    aiLocalStatusSurface.dataset.opensControlCenter = "false";
    aiLocalStatusSurface.dataset.aiLocalStatus = "no-ai-execution";
    aiLocalStatusSurface.dataset.providerVisibleData = providerVisibleData;
    aiLocalStatusSurface.dataset.promptSend = promptSend;
    aiLocalStatusSurface.dataset.providerModelExecution = "blocked";
    aiLocalStatusSurface.dataset.networkEgress = networkEgress;
    aiLocalStatusSurface.dataset.memoryIndexing = memoryIndexing;
    aiLocalStatusSurface.dataset.activityState =
      aiLocalStatusSurface.dataset.activityState || "idle";
  }
  if (aiProviderTray) {
    aiProviderTray.hidden = true;
    aiProviderTray.setAttribute("aria-hidden", "true");
    aiProviderTray.setAttribute("tabindex", "-1");
    aiProviderTray.setAttribute("aria-expanded", "false");
    aiProviderTray.dataset.interactive = "false";
    aiProviderTray.dataset.desktopTrayDoorway = "native-system-tray";
    aiProviderTray.dataset.aiResidentDoorway = "f3-ff01-narrow-ai-command-center";
    aiProviderTray.dataset.aiControlCenterRoute = "fam007-ai-control-center";
    aiProviderTray.dataset.statusSurfaceOwner = "ai-local-status-surface";
    aiProviderTray.dataset.aiLocalStatus = "no-ai-execution";
    aiProviderTray.dataset.providerVisibleData = providerVisibleData;
    aiProviderTray.dataset.promptSend = promptSend;
    aiProviderTray.dataset.providerModelExecution = "blocked";
    aiProviderTray.dataset.networkEgress = networkEgress;
    aiProviderTray.dataset.memoryIndexing = memoryIndexing;
    aiProviderTray.dataset.fam003CarryIn = "narrow-doorway-only";
  }
  if (aiProviderTrayWindow) {
    aiProviderTrayWindow.hidden = true;
    aiProviderTrayWindow.dataset.aiControlCenter = "fam007";
    aiProviderTrayWindow.dataset.aiControlCenterOwner = "FAM-007";
    aiProviderTrayWindow.dataset.aiControlCenterRoute = "fam007-ai-control-center";
    aiProviderTrayWindow.dataset.aiResidentDoorway = "f3-ff01-narrow-ai-command-center";
    aiProviderTrayWindow.dataset.fam003CarryIn = "narrow-doorway-only";
    aiProviderTrayWindow.dataset.fam008PackagingExecution = "blocked-display-only";
    aiProviderTrayWindow.dataset.providerVisibleData = providerVisibleData;
    aiProviderTrayWindow.dataset.promptSend = promptSend;
    aiProviderTrayWindow.dataset.providerModelExecution = "blocked";
    aiProviderTrayWindow.dataset.networkEgress = networkEgress;
    aiProviderTrayWindow.dataset.memoryIndexing = memoryIndexing;
  }

  setTextContent(aiLocalStatusLabel, state.localStatusSurfaceLabel || "No AI executing");
  setTextContent(aiLocalStatusScope, state.localStatusSurfaceScope || "Provider/model off");
  setTextContent(aiLocalStatusActivity, state.localStatusActivityLabel || "Idle");
  setTextContent(aiProviderTrayLabel, state.trayStatusLabel || "NDAI");
  setTextContent(aiProviderTrayScope, state.trayScopeLabel || "AI");
  setTextContent(
    aiProviderTrayLocalStatus,
    state.trayLocalStatusDetail || "No AI executing; no provider/model active"
  );
  setTextContent(aiProviderTrayProviderVisibleData, providerVisibleData);
  setTextContent(aiProviderTrayProviderExecution, providerExecution);
  setTextContent(aiProviderTrayCapabilityPosture, capabilityPosture);
  setTextContent(aiProviderTrayLaneBoundary, laneBoundary);
  setTextContent(
    aiProviderTrayStatusBoundary,
    state.trayStatusBoundaryLabel || "Display-only; controls live here"
  );
  setTextContent(
    aiProviderTrayResultDetail,
    state.providerVisibleDataDetail || "No prompt, file, screen, memory, or telemetry is sent."
  );
  setTextContent(
    aiProviderTrayReviewNote,
    state.trayReviewNote ||
      "FAM-007 owns this AI Control Center; the NDAI resident entry is a doorway only."
  );

  if (aiProviderTrayLocalAssistAction) {
    aiProviderTrayLocalAssistAction.textContent = state.interactionLabel || "Run no-provider check";
    aiProviderTrayLocalAssistAction.title =
      state.interactionDisabledReason ||
      "No-provider check runs inside the AI Control Center only; prompts, providers, downloads, memory, and network remain blocked";
    aiProviderTrayLocalAssistAction.disabled = !localActionAvailable;
    aiProviderTrayLocalAssistAction.setAttribute(
      "aria-disabled",
      localActionAvailable ? "false" : "true"
    );
    aiProviderTrayLocalAssistAction.dataset.localActionGuard = "no-provider";
  }
}

function renderAIProviderState() {
  if (!aiProviderStatus) return;

  const state = aiProviderState || {};
  const displayState =
    state.desktopAiOwnedReadinessDisplayState || "desktop-ai-owned-readiness-display-visible";
  const localActionAvailable = state.interactionAffordance === "local-assisted-action-available";
  const displayVisible =
    displayState === "desktop-ai-owned-readiness-display-visible" || localActionAvailable;
  aiProviderStatus.hidden = true;
  aiProviderStatus.setAttribute("aria-hidden", "true");
  aiProviderStatus.dataset.displaySuppression =
    "tray-owned-status";
  aiProviderStatus.dataset.displayVisibility = "tray-owned-hidden";
  aiProviderStatus.dataset.statusOnly = "true";
  aiProviderStatus.dataset.localActionGuard = "no-provider";
  aiProviderStatus.dataset.localActionClickable = "false";
  aiProviderStatus.dataset.localActionResult = aiProviderStatus.dataset.localActionResult || "idle";
  aiProviderStatus.dataset.localActionResultState =
    state.localActionResultState || "local-action-idle";
  aiProviderStatus.dataset.localActionResultSchema =
    state.localActionResultSchemaVersion || "local-action-result.v1";
  aiProviderStatus.dataset.localResultProviderVisibleData =
    state.localActionResultProviderVisibleData || "none";
  aiProviderStatus.dataset.localResultSentToProvider =
    state.localActionResultSentToProvider ? "true" : "false";
  aiProviderStatus.dataset.localResultCanAcceptPrompts =
    state.localActionResultCanAcceptPrompts ? "true" : "false";
  aiProviderStatus.dataset.localResultPromptSend =
    state.localActionResultPromptSendPosture || "prompt-send-disabled";
  aiProviderStatus.dataset.localResultNetworkEgress =
    state.localActionResultNetworkEgressState || "network-egress-blocked";
  aiProviderStatus.dataset.localResultMemoryIndexing =
    state.localActionResultMemoryIndexingState || "memory-indexing-disabled";
  aiProviderStatus.dataset.mode = state.mode || "unknown";
  aiProviderStatus.dataset.availability = state.availability || "disabled";
  aiProviderStatus.dataset.privacyScope = state.privacyScope || "unknown";
  aiProviderStatus.dataset.providerSelection = state.providerSelectionState || "unknown";
  aiProviderStatus.dataset.providerConfiguration = state.providerConfigurationState || "unknown";
  aiProviderStatus.dataset.providerRegistry = state.providerRegistryState || "unknown";
  aiProviderStatus.dataset.providerInteraction = state.providerInteractionState || "unknown";
  aiProviderStatus.dataset.runtimeCategory = state.runtimeStateCategory || "unknown";
  aiProviderStatus.dataset.runtimeReason = state.runtimeReasonCode || "unknown";
  aiProviderStatus.dataset.runtimeProvenance = state.runtimeProvenance || "unknown";
  aiProviderStatus.dataset.runtimeSchema = state.runtimeStateSchemaVersion || "unknown";
  aiProviderStatus.dataset.runtimeConfig = state.runtimeConfigState || "unknown";
  aiProviderStatus.dataset.runtimeFailClosed = state.runtimeFailClosed ? "true" : "false";
  aiProviderStatus.dataset.providerReadiness = state.providerReadinessState || "unknown";
  aiProviderStatus.dataset.setupEligibility = state.setupEligibilityState || "unknown";
  aiProviderStatus.dataset.setupBlocker = state.setupBlockerState || "unknown";
  aiProviderStatus.dataset.readinessReason = state.readinessReasonCode || "unknown";
  aiProviderStatus.dataset.readinessProvenance = state.readinessProvenance || "unknown";
  aiProviderStatus.dataset.readinessSchema = state.readinessStateSchemaVersion || "unknown";
  aiProviderStatus.dataset.futureProviderGate = state.futureProviderGateStatus || "unknown";
  aiProviderStatus.dataset.providerActivation = state.providerActivationState || "unknown";
  aiProviderStatus.dataset.activationEligibility = state.activationEligibilityState || "unknown";
  aiProviderStatus.dataset.activationBlocker = state.activationBlockerState || "unknown";
  aiProviderStatus.dataset.activationReason = state.activationReasonCode || "unknown";
  aiProviderStatus.dataset.activationProvenance = state.activationProvenance || "unknown";
  aiProviderStatus.dataset.activationSchema = state.activationStateSchemaVersion || "unknown";
  aiProviderStatus.dataset.futureActivationGate = state.futureActivationGateStatus || "unknown";
  aiProviderStatus.dataset.providerAdapter = state.providerAdapterPosture || "unknown";
  aiProviderStatus.dataset.promptExecutionGate = state.promptExecutionGateState || "unknown";
  aiProviderStatus.dataset.modelExecutionGate = state.modelExecutionGateState || "unknown";
  aiProviderStatus.dataset.providerExecutionGate = state.providerExecutionGateState || "unknown";
  aiProviderStatus.dataset.functionalAiCriteria = state.functionalAiCriteriaState || "unknown";
  aiProviderStatus.dataset.v18PrebetaReadiness = state.v18PrebetaReadinessState || "unknown";
  aiProviderStatus.dataset.executionReadiness = state.providerExecutionReadinessState || "unknown";
  aiProviderStatus.dataset.executionEligibility = state.executionEligibilityState || "unknown";
  aiProviderStatus.dataset.executionBlocker = state.executionBlockerState || "unknown";
  aiProviderStatus.dataset.executionReason = state.executionReasonCode || "unknown";
  aiProviderStatus.dataset.executionProvenance = state.executionProvenance || "unknown";
  aiProviderStatus.dataset.executionSchema = state.executionStateSchemaVersion || "unknown";
  aiProviderStatus.dataset.executionApproval = state.executionApprovalStatus || "unknown";
  aiProviderStatus.dataset.providerPath = state.providerPathStatus || "unknown";
  aiProviderStatus.dataset.providerPathReadiness = state.providerPathReadinessState || "unknown";
  aiProviderStatus.dataset.providerPathEligibility = state.providerPathEligibilityState || "unknown";
  aiProviderStatus.dataset.providerPathBlocker = state.providerPathBlockerState || "unknown";
  aiProviderStatus.dataset.providerPathReason = state.providerPathReasonCode || "unknown";
  aiProviderStatus.dataset.providerPathSchema = state.providerPathStateSchemaVersion || "unknown";
  aiProviderStatus.dataset.providerPathConfigSchema = state.providerPathConfigSchemaVersion || "unknown";
  aiProviderStatus.dataset.providerProfileId = state.providerProfileId || "unknown";
  aiProviderStatus.dataset.providerKind = state.providerKind || "unknown";
  aiProviderStatus.dataset.providerSource = state.providerProfileSource || "unknown";
  aiProviderStatus.dataset.providerConfigStatus = state.providerConfigStatus || "unknown";
  aiProviderStatus.dataset.providerSetupApproval = state.providerSetupApprovalStatus || "unknown";
  aiProviderStatus.dataset.providerExecutionApproval = state.providerExecutionApprovalStatus || "unknown";
  aiProviderStatus.dataset.setupConsent = state.setupConsentState || "unknown";
  aiProviderStatus.dataset.executionConsent = state.executionConsentState || "unknown";
  aiProviderStatus.dataset.consentSchema = state.consentReadinessStateSchemaVersion || "unknown";
  aiProviderStatus.dataset.providerVisibleDataRequirement =
    state.providerVisibleDataRequirementState || "unknown";
  aiProviderStatus.dataset.dataClassificationPosture = state.dataClassificationPostureState || "unknown";
  aiProviderStatus.dataset.auditEnvelope = state.auditEnvelopePostureState || "unknown";
  aiProviderStatus.dataset.localOnlyStatus = state.localOnlyStatusPosture || "unknown";
  aiProviderStatus.dataset.setupFlowReadiness = state.setupFlowReadinessState || "unknown";
  aiProviderStatus.dataset.setupFlowEligibility = state.setupFlowEligibilityState || "unknown";
  aiProviderStatus.dataset.setupFlowBlocker = state.setupFlowBlockerState || "unknown";
  aiProviderStatus.dataset.setupFlowReason = state.setupFlowReasonCode || "unknown";
  aiProviderStatus.dataset.setupFlowApproval = state.setupFlowApprovalStatus || "unknown";
  aiProviderStatus.dataset.consentFlowReadiness = state.consentFlowReadinessState || "unknown";
  aiProviderStatus.dataset.consentFlowEligibility = state.consentFlowEligibilityState || "unknown";
  aiProviderStatus.dataset.consentFlowBlocker = state.consentFlowBlockerState || "unknown";
  aiProviderStatus.dataset.consentFlowReason = state.consentFlowReasonCode || "unknown";
  aiProviderStatus.dataset.consentFlowApproval = state.consentFlowApprovalStatus || "unknown";
  aiProviderStatus.dataset.consentCollection = state.consentCollectionPosture || "unknown";
  aiProviderStatus.dataset.setupContractReadiness = state.providerSetupContractReadinessState || "unknown";
  aiProviderStatus.dataset.setupContractEligibility = state.providerSetupContractEligibilityState || "unknown";
  aiProviderStatus.dataset.setupContractBlocker = state.providerSetupContractBlockerState || "unknown";
  aiProviderStatus.dataset.setupContractReason = state.providerSetupContractReasonCode || "unknown";
  aiProviderStatus.dataset.setupContractApproval = state.providerSetupContractApprovalStatus || "unknown";
  aiProviderStatus.dataset.setupContractGate = state.providerSetupContractGateState || "unknown";
  aiProviderStatus.dataset.setupFoundationState = state.providerSetupFoundationState || "unknown";
  aiProviderStatus.dataset.setupFoundationEligibility =
    state.providerSetupFoundationEligibilityState || "unknown";
  aiProviderStatus.dataset.setupFoundationBlocker = state.providerSetupFoundationBlockerState || "unknown";
  aiProviderStatus.dataset.setupFoundationReason = state.providerSetupFoundationReasonCode || "unknown";
  aiProviderStatus.dataset.setupFoundationApproval = state.providerSetupFoundationApprovalStatus || "unknown";
  aiProviderStatus.dataset.setupFoundationValidation =
    state.providerSetupFoundationValidationStatus || "unknown";
  aiProviderStatus.dataset.setupFoundationPersistence =
    state.providerSetupFoundationPersistenceStatus || "unknown";
  aiProviderStatus.dataset.setupFoundationGate = state.providerSetupFoundationGateState || "unknown";
  aiProviderStatus.dataset.consentCollectionFoundation =
    state.consentCollectionFoundationState || "unknown";
  aiProviderStatus.dataset.consentCollectionBlocker =
    state.consentCollectionBlockerState || "unknown";
  aiProviderStatus.dataset.consentCollectionApproval =
    state.consentCollectionApprovalStatus || "unknown";
  aiProviderStatus.dataset.consentCollectionValidation =
    state.consentCollectionValidationStatus || "unknown";
  aiProviderStatus.dataset.consentCollectionPersistence =
    state.consentPersistenceStatus || "unknown";
  aiProviderStatus.dataset.consentCollectionGate =
    state.consentCollectionGateState || "unknown";
  aiProviderStatus.dataset.consentUxState = state.consentUxState || "unknown";
  aiProviderStatus.dataset.consentUxIntent = state.consentUxIntentState || "unknown";
  aiProviderStatus.dataset.consentUxSurface = state.consentUxSurfaceState || "unknown";
  aiProviderStatus.dataset.consentUxSetup = state.consentUxSetupDisplayState || "unknown";
  aiProviderStatus.dataset.consentUxExecution =
    state.consentUxExecutionDisplayState || "unknown";
  aiProviderStatus.dataset.consentUxRevocationReset =
    state.consentUxRevocationResetState || "unknown";
  aiProviderStatus.dataset.consentUxWrite = state.consentUxWritePosture || "unknown";
  aiProviderStatus.dataset.consentUxStatusProof =
    state.consentUxStatusProofState || "unknown";
  aiProviderStatus.dataset.consentUxDesktopDisplay =
    state.consentUxDesktopDisplayState || "unknown";
  aiProviderStatus.dataset.consentUxSetupGate =
    state.consentUxProviderSetupGateState || "unknown";
  aiProviderStatus.dataset.consentUxExecutionGate =
    state.consentUxProviderExecutionGateState || "unknown";
  aiProviderStatus.dataset.providerSetupHandoff = state.providerSetupHandoffPosture || "unknown";
  aiProviderStatus.dataset.providerConsentHandoff = state.providerConsentHandoffPosture || "unknown";
  aiProviderStatus.dataset.providerPathHandoff = state.providerPathHandoffPosture || "unknown";
  aiProviderStatus.dataset.setupFlowGate = state.setupFlowGateState || "unknown";
  aiProviderStatus.dataset.consentFlowGate = state.consentFlowGateState || "unknown";
  aiProviderStatus.dataset.setupApprovalGate = state.setupApprovalGateState || "unknown";
  aiProviderStatus.dataset.executionApprovalGate = state.executionApprovalGateState || "unknown";
  aiProviderStatus.dataset.dataVisibilityConsent = state.dataVisibilityConsentPosture || "unknown";
  aiProviderStatus.dataset.adapterSelection = state.adapterSelectionPosture || "unknown";
  aiProviderStatus.dataset.promptAcceptanceGate = state.promptAcceptanceGateState || "unknown";
  aiProviderStatus.dataset.promptRoutingGate = state.promptRoutingGateState || "unknown";
  aiProviderStatus.dataset.promptSend = state.promptSendPosture || "unknown";
  aiProviderStatus.dataset.modelExecutionStatus = state.modelExecutionStatus || "unknown";
  aiProviderStatus.dataset.providerVisibleDataExecution =
    state.providerVisibleDataExecutionPosture || "unknown";
  aiProviderStatus.dataset.functionalAiReleaseGate = state.functionalAiReleaseGateState || "unknown";
  aiProviderStatus.dataset.v18ReleaseGate = state.v18ReleaseGateState || "unknown";
  aiProviderStatus.dataset.configuredProviderCount = String(state.configuredProviderCount || 0);
  aiProviderStatus.dataset.availableProviderCount = String(state.availableProviderCount || 0);
  aiProviderStatus.dataset.hardwareCapability = state.hardwareCapabilityState || "unknown";
  aiProviderStatus.dataset.gpuCapability = state.gpuCapabilityState || "unknown";
  aiProviderStatus.dataset.cpuFallback = state.cpuFallbackState || "unknown";
  aiProviderStatus.dataset.powerState = state.powerState || "unknown";
  aiProviderStatus.dataset.thermalGuardrail = state.thermalGuardrailState || "unknown";
  aiProviderStatus.dataset.modelWorkload = state.modelWorkloadState || "unknown";
  aiProviderStatus.dataset.hardwareDetectionLevel = state.hardwareDetectionLevel || "unknown";
  aiProviderStatus.dataset.ramReadiness = state.ramReadinessState || "unknown";
  aiProviderStatus.dataset.diskReadiness = state.diskReadinessState || "unknown";
  aiProviderStatus.dataset.modelWorkloadMetadata = state.modelWorkloadMetadataState || "unknown";
  aiProviderStatus.dataset.capabilityRecommendation = state.capabilityRecommendationState || "unknown";
  aiProviderStatus.dataset.capabilityPackLifecycle = state.capabilityPackLifecycleState || "unknown";
  aiProviderStatus.dataset.capabilityPackDownload = state.capabilityPackDownloadState || "unknown";
  aiProviderStatus.dataset.capabilityPackInstall = state.capabilityPackInstallState || "unknown";
  aiProviderStatus.dataset.capabilityPackUpdate = state.capabilityPackUpdateState || "unknown";
  aiProviderStatus.dataset.capabilityPackUninstall = state.capabilityPackUninstallState || "unknown";
  aiProviderStatus.dataset.capabilityPackManifest = state.capabilityPackManifestState || "unknown";
  aiProviderStatus.dataset.capabilityPackCompatibility = state.capabilityPackCompatibilityState || "unknown";
  aiProviderStatus.dataset.capabilityPackEligibility = state.capabilityPackEligibilityState || "unknown";
  aiProviderStatus.dataset.installIntent = state.installIntentState || "unknown";
  aiProviderStatus.dataset.laneBoundarySchema = state.laneBoundarySchemaVersion || "unknown";
  aiProviderStatus.dataset.publicLaneBoundary = state.publicLaneBoundaryState || "unknown";
  aiProviderStatus.dataset.developerLaneBoundary = state.developerLaneBoundaryState || "unknown";
  aiProviderStatus.dataset.ownerLaneBoundary = state.ownerLaneBoundaryState || "unknown";
  aiProviderStatus.dataset.privateSetupBoundary = state.privateSetupBoundaryState || "unknown";
  aiProviderStatus.dataset.privateSetupAuthorized = state.privateSetupAuthorized ? "true" : "false";
  aiProviderStatus.dataset.privateMaterialVisible = state.privateMaterialVisible ? "true" : "false";
  aiProviderStatus.dataset.ownerMemoryEnabled = state.ownerMemoryEnabled ? "true" : "false";
  aiProviderStatus.dataset.ownerAgentsEnabled = state.ownerAgentsEnabled ? "true" : "false";
  aiProviderStatus.dataset.dataClassification = state.dataClassificationState || "unknown";
  aiProviderStatus.dataset.memoryContext = state.memoryContextState || "unknown";
  aiProviderStatus.dataset.memoryIndexing = state.memoryIndexingState || "unknown";
  aiProviderStatus.dataset.networkEgress = state.networkEgressState || "unknown";
  aiProviderStatus.dataset.auditSecrets = state.auditSecretsState || "unknown";
  aiProviderStatus.dataset.windowsResilience = state.windowsResilienceState || "unknown";
  aiProviderStatus.dataset.offlineDegraded = state.offlineDegradedState || "unknown";
  aiProviderStatus.dataset.personaVoiceBoundary = state.personaCoreVoiceState || "unknown";
  aiProviderStatus.dataset.voiceRuntime = state.voiceRuntimeState || "unknown";
  aiProviderStatus.dataset.validationGates = state.validationProofGateState || "unknown";
  aiProviderStatus.dataset.abuseEval = state.abuseEvalState || "unknown";
  aiProviderStatus.dataset.releaseProof = state.releaseProofGateState || "unknown";
  aiProviderStatus.dataset.copyContract = state.coreDesktopRuntimeStateContract || "unknown";
  aiProviderStatus.dataset.contractReady = state.contractReadyMarker || "unknown";
  aiProviderStatus.dataset.selectedProvider = state.selectedProviderId || "unknown";
  aiProviderStatus.dataset.consentState = state.consentState || "unknown";
  aiProviderStatus.dataset.interactionAffordance = state.interactionAffordance || "unknown";
  aiProviderStatus.dataset.providerVisibleData = state.providerVisibleData || "unknown";
  aiProviderStatus.dataset.requiresConsent = state.requiresConsent ? "true" : "false";
  aiProviderStatus.dataset.sentToProvider = state.sentToProvider ? "true" : "false";
  aiProviderStatus.dataset.canAcceptPrompts = state.canAcceptPrompts ? "true" : "false";

  if (aiProviderStatusState) {
    aiProviderStatusState.textContent = state.statusLabel || "No AI executing";
  }
  if (aiProviderStatusProvider) {
    aiProviderStatusProvider.textContent =
      state.providerLabel || "No provider/model execution active";
  }
  if (aiProviderStatusSelection) {
    aiProviderStatusSelection.textContent = state.providerSelectionLabel || "No-provider fallback active";
  }
  if (aiProviderStatusConfiguration) {
    aiProviderStatusConfiguration.textContent = state.providerConfigurationLabel || "Provider configuration: none";
  }
  if (aiProviderStatusRegistry) {
    aiProviderStatusRegistry.textContent = state.providerRegistryLabel || "Local provider registry: no configured providers";
  }
  if (aiProviderStatusHardware) {
    aiProviderStatusHardware.textContent = state.hardwareCapabilityLabel || "Hardware capability: local planning only";
  }
  if (aiProviderStatusGpu) {
    aiProviderStatusGpu.textContent = state.gpuCapabilityLabel || "GPU acceleration: unprobed; no model workload active";
  }
  if (aiProviderStatusCpu) {
    aiProviderStatusCpu.textContent = state.cpuFallbackLabel || "CPU fallback: preserved";
  }
  if (aiProviderStatusPower) {
    aiProviderStatusPower.textContent = state.powerStateLabel || "Power state: not evaluated";
  }
  if (aiProviderStatusThermal) {
    aiProviderStatusThermal.textContent = state.thermalGuardrailLabel || "Thermal guardrails required before model workloads";
  }
  if (aiProviderStatusModelWorkload) {
    aiProviderStatusModelWorkload.textContent = state.modelWorkloadLabel || "Model workloads: disabled";
  }
  if (aiProviderStatusHardwareDetection) {
    aiProviderStatusHardwareDetection.textContent =
      state.hardwareDetectionLabel || "Hardware detection: Level 1 safe local static snapshot";
  }
  if (aiProviderStatusRam) {
    aiProviderStatusRam.textContent = state.ramReadinessLabel || "RAM readiness: unprobed";
  }
  if (aiProviderStatusDisk) {
    aiProviderStatusDisk.textContent = state.diskReadinessLabel || "Disk readiness: unprobed";
  }
  if (aiProviderStatusModelMetadata) {
    aiProviderStatusModelMetadata.textContent =
      state.modelWorkloadMetadataLabel || "Model workload metadata: planned; no execution";
  }
  if (aiProviderStatusCapabilityPack) {
    aiProviderStatusCapabilityPack.textContent = state.capabilityPackLifecycleLabel || "Capability packs: lifecycle planned";
  }
  if (aiProviderStatusCapabilityDownload) {
    aiProviderStatusCapabilityDownload.textContent =
      state.capabilityPackDownloadLabel || "Capability pack downloads: blocked";
  }
  if (aiProviderStatusCapabilityRecommendation) {
    aiProviderStatusCapabilityRecommendation.textContent =
      state.capabilityRecommendationLabel || "Capability recommendation pending hardware proof";
  }
  if (aiProviderStatusCapabilityManifest) {
    aiProviderStatusCapabilityManifest.textContent =
      `${state.capabilityPackManifestSchemaVersion || "capability-pack-manifest.v1"}; ${state.capabilityPackManifestState || "manifest-planned"}`;
  }
  if (aiProviderStatusCapabilityIntegrity) {
    aiProviderStatusCapabilityIntegrity.textContent =
      `${state.capabilityPackChecksumState || "checksum-required-before-install"}; ${state.capabilityPackSignatureState || "signature-required-before-install"}; ${state.capabilityPackCompatibilityState || "compatibility-unproven"}`;
  }
  if (aiProviderStatusDataClassification) {
    aiProviderStatusDataClassification.textContent =
      state.dataClassificationLabel || "Data classification: local-only planning";
  }
  if (aiProviderStatusMemory) {
    aiProviderStatusMemory.textContent = state.memoryContextLabel || "Memory/context: disabled; no indexing";
  }
  if (aiProviderStatusMemoryContract) {
    aiProviderStatusMemoryContract.textContent =
      `${state.memoryIndexingState || "memory-indexing-disabled"}; ${state.retrievalState || "retrieval-disabled"}; ${state.learningState || "learning-disabled"}; ${state.persistenceState || "persistence-disabled"}`;
  }
  if (aiProviderStatusEgress) {
    aiProviderStatusEgress.textContent = state.networkEgressState || "network-egress-blocked";
  }
  if (aiProviderStatusAuditSecrets) {
    aiProviderStatusAuditSecrets.textContent = state.auditSecretsLabel || "Audit/secrets: planned; no secrets stored";
  }
  if (aiProviderStatusWindows) {
    aiProviderStatusWindows.textContent = state.windowsResilienceLabel || "Windows resilience: planning only";
  }
  if (aiProviderStatusOffline) {
    aiProviderStatusOffline.textContent = state.offlineDegradedLabel || "Offline/degraded mode: planned";
  }
  if (aiProviderStatusPersona) {
    aiProviderStatusPersona.textContent = state.personaCoreVoiceLabel || "Persona/Core/voice: planning boundary";
  }
  if (aiProviderStatusVoice) {
    aiProviderStatusVoice.textContent = state.voiceRuntimeLabel || "Voice runtime: disabled";
  }
  if (aiProviderStatusValidation) {
    aiProviderStatusValidation.textContent = state.validationProofGateLabel || "Validation gates: static proof active";
  }
  if (aiProviderStatusAbuse) {
    aiProviderStatusAbuse.textContent = state.abuseEvalLabel || "Abuse/eval: pending future approval";
  }
  if (aiProviderStatusReleaseProof) {
    aiProviderStatusReleaseProof.textContent = state.releaseProofGateLabel || "Release proof: pending future approval";
  }
  if (aiProviderStatusCopyContract) {
    aiProviderStatusCopyContract.textContent =
      `${state.coreDesktopCopyContractVersion || "core-desktop-provider-state-copy.v1"}; ${state.coreDesktopRuntimeStateContract || "core-desktop-runtime-state-contract"}`;
  }
  if (aiProviderStatusFixtures) {
    aiProviderStatusFixtures.textContent =
      `${state.goldenProviderStateFixtures || "golden-provider-state-fixtures"}; ${state.validatorExpansionState || "validator-expansion-active"}`;
  }
  if (aiProviderStatusConsent) {
    aiProviderStatusConsent.textContent = state.consentLabel || "Consent required before provider setup";
  }
  if (aiProviderStatusDisclosure) {
    aiProviderStatusDisclosure.textContent = state.providerVisibleDataLabel || "Provider-visible data: none";
  }
  if (aiProviderStatusVisibleDataDetail) {
    aiProviderStatusVisibleDataDetail.textContent =
      state.providerVisibleDataDetail || "No prompt, file, screen, memory, or telemetry is sent";
  }
  if (aiProviderStatusConsentBoundary) {
    aiProviderStatusConsentBoundary.textContent =
      state.providerConsentBoundaryLabel || "Consent boundary: provider setup required before prompts";
  }
  if (aiProviderStatusRuntime) {
    aiProviderStatusRuntime.textContent = state.runtimeStateLabel || "Runtime state: provider setup disabled";
  }
  if (aiProviderStatusRuntimeReason) {
    aiProviderStatusRuntimeReason.textContent =
      state.runtimeReasonLabel || "Reason: setup disabled in local-only seam";
  }
  if (aiProviderStatusRuntimeProvenance) {
    aiProviderStatusRuntimeProvenance.textContent = state.runtimeProvenanceLabel || "Provenance: default config";
  }
  if (aiProviderStatusRuntimeSchema) {
    const schemaVersion = state.runtimeStateSchemaVersion || "provider-runtime-state.v1";
    const configVersion = state.runtimeConfigSchemaVersion || "provider-runtime-config.v1";
    const configLabel = state.runtimeConfigLabel || "Config: safe default local-only";
    aiProviderStatusRuntimeSchema.textContent = `${schemaVersion}; ${configVersion}; ${configLabel}`;
  }
  if (aiProviderStatusReadiness) {
    aiProviderStatusReadiness.textContent = state.providerReadinessLabel || "Provider readiness: setup disabled";
  }
  if (aiProviderStatusSetupEligibility) {
    aiProviderStatusSetupEligibility.textContent = state.setupEligibilityLabel || "Setup eligibility: disabled";
  }
  if (aiProviderStatusSetupBlocker) {
    aiProviderStatusSetupBlocker.textContent = state.setupBlockerLabel || "Setup blocker: setup disabled";
  }
  if (aiProviderStatusReadinessReason) {
    aiProviderStatusReadinessReason.textContent =
      state.readinessReasonLabel || "Readiness reason: local-only default";
  }
  if (aiProviderStatusReadinessProvenance) {
    aiProviderStatusReadinessProvenance.textContent =
      state.readinessProvenanceLabel || "Readiness provenance: default config";
  }
  if (aiProviderStatusReadinessSchema) {
    const readinessSchemaVersion = state.readinessStateSchemaVersion || "provider-readiness-state.v1";
    const readinessConfigVersion = state.readinessConfigSchemaVersion || "provider-readiness-config.v1";
    const readinessConfigLabel = state.readinessConfigLabel || "Readiness config: safe default local-only";
    aiProviderStatusReadinessSchema.textContent =
      `${readinessSchemaVersion}; ${readinessConfigVersion}; ${readinessConfigLabel}`;
  }
  if (aiProviderStatusFutureGate) {
    aiProviderStatusFutureGate.textContent =
      state.futureProviderGateLabel || "Future provider gate: USER approval required before setup";
  }
  if (aiProviderStatusActivation) {
    aiProviderStatusActivation.textContent = state.providerActivationLabel || "Provider activation: unavailable";
  }
  if (aiProviderStatusActivationEligibility) {
    aiProviderStatusActivationEligibility.textContent =
      state.activationEligibilityLabel || "Activation eligibility: unavailable";
  }
  if (aiProviderStatusActivationBlocker) {
    aiProviderStatusActivationBlocker.textContent =
      state.activationBlockerLabel || "Activation blocker: readiness required";
  }
  if (aiProviderStatusActivationReason) {
    aiProviderStatusActivationReason.textContent =
      state.activationReasonLabel || "Activation reason: activation foundation only";
  }
  if (aiProviderStatusActivationProvenance) {
    aiProviderStatusActivationProvenance.textContent =
      state.activationProvenanceLabel || "Activation provenance: default config";
  }
  if (aiProviderStatusActivationSchema) {
    const activationSchemaVersion = state.activationStateSchemaVersion || "provider-activation-state.v1";
    const activationConfigVersion = state.activationConfigSchemaVersion || "provider-activation-config.v1";
    const activationConfigLabel = state.activationConfigLabel || "Activation config: safe default local-only";
    aiProviderStatusActivationSchema.textContent =
      `${activationSchemaVersion}; ${activationConfigVersion}; ${activationConfigLabel}`;
  }
  if (aiProviderStatusFutureActivationGate) {
    aiProviderStatusFutureActivationGate.textContent =
      state.futureActivationGateLabel || "Future activation gate: USER approval required before activation";
  }
  if (aiProviderStatusAdapter) {
    aiProviderStatusAdapter.textContent = state.providerAdapterLabel || "Provider adapter: null local adapter";
  }
  if (aiProviderStatusExecutionGates) {
    aiProviderStatusExecutionGates.textContent =
      `${state.promptExecutionGateLabel || "Prompt execution gate: disabled"}; ${state.modelExecutionGateLabel || "Model execution gate: disabled"}; ${state.providerExecutionGateLabel || "Provider execution gate: disabled"}`;
  }
  if (aiProviderStatusFunctionalAi) {
    aiProviderStatusFunctionalAi.textContent =
      `${state.functionalAiCriteriaLabel || "Functional AI: criteria pending for v1.8.0-prebeta"}; ${state.v18PrebetaReadinessLabel || "v1.8.0-prebeta readiness: pending functional AI proof"}`;
  }
  if (aiProviderStatusExecutionReadiness) {
    aiProviderStatusExecutionReadiness.textContent =
      state.providerExecutionReadinessLabel || "Execution readiness: unavailable";
  }
  if (aiProviderStatusExecutionEligibility) {
    aiProviderStatusExecutionEligibility.textContent =
      state.executionEligibilityLabel || "Execution eligibility: unavailable";
  }
  if (aiProviderStatusExecutionBlocker) {
    aiProviderStatusExecutionBlocker.textContent =
      state.executionBlockerLabel || "Execution blocker: activation required";
  }
  if (aiProviderStatusExecutionReason) {
    aiProviderStatusExecutionReason.textContent =
      state.executionReasonLabel || "Execution reason: execution readiness gates only";
  }
  if (aiProviderStatusExecutionProvenance) {
    aiProviderStatusExecutionProvenance.textContent =
      state.executionProvenanceLabel || "Execution provenance: activation state";
  }
  if (aiProviderStatusExecutionSchema) {
    const executionSchemaVersion = state.executionStateSchemaVersion || "provider-execution-readiness-state.v1";
    const executionConfigVersion =
      state.executionConfigSchemaVersion || "provider-execution-readiness-config.v1";
    const executionConfigLabel = state.executionConfigLabel || "Execution config: safe default local-only";
    aiProviderStatusExecutionSchema.textContent =
      `${executionSchemaVersion}; ${executionConfigVersion}; ${executionConfigLabel}`;
  }
  if (aiProviderStatusExecutionApproval) {
    aiProviderStatusExecutionApproval.textContent =
      state.executionApprovalLabel || "Execution approval: USER approval missing";
  }
  if (aiProviderStatusProviderPath) {
    aiProviderStatusProviderPath.textContent = state.providerPathLabel || "Provider path: not selected";
  }
  if (aiProviderStatusProviderPathReadiness) {
    aiProviderStatusProviderPathReadiness.textContent =
      state.providerPathReadinessLabel || "Provider path readiness: unavailable";
  }
  if (aiProviderStatusProviderPathEligibility) {
    aiProviderStatusProviderPathEligibility.textContent =
      state.providerPathEligibilityLabel || "Provider path eligibility: unavailable";
  }
  if (aiProviderStatusProviderPathBlocker) {
    aiProviderStatusProviderPathBlocker.textContent =
      state.providerPathBlockerLabel || "Provider path blocker: execution readiness required";
  }
  if (aiProviderStatusProviderPathReason) {
    aiProviderStatusProviderPathReason.textContent =
      state.providerPathReasonLabel || "Provider path reason: readiness only";
  }
  if (aiProviderStatusProviderPathSchema) {
    const providerPathSchemaVersion =
      state.providerPathStateSchemaVersion || "provider-path-readiness-state.v1";
    const providerPathConfigVersion =
      state.providerPathConfigSchemaVersion || "provider-path-readiness-config.v1";
    const providerPathConfigLabel =
      state.providerPathConfigLabel || "Provider path config: safe default local-only";
    aiProviderStatusProviderPathSchema.textContent =
      `${providerPathSchemaVersion}; ${providerPathConfigVersion}; ${providerPathConfigLabel}`;
  }
  if (aiProviderStatusProviderProfile) {
    aiProviderStatusProviderProfile.textContent =
      `${state.providerProfileLabel || "Provider profile: local-null-provider-profile"}; ${state.providerKindLabel || "Provider kind: null-local-provider"}; ${state.providerSourceLabel || "Provider source: local status scaffold"}`;
  }
  if (aiProviderStatusProviderConfigEnvelope) {
    aiProviderStatusProviderConfigEnvelope.textContent =
      `${state.providerConfigStatusLabel || "Provider config: missing"}; ${state.sdkRequirementLabel || "SDK integration: pending USER approval"}; ${state.networkRequirementLabel || "Network requirement: blocked"}`;
  }
  if (aiProviderStatusProviderApprovals) {
    aiProviderStatusProviderApprovals.textContent =
      `${state.providerSetupApprovalLabel || "Provider setup approval: missing"}; ${state.providerExecutionApprovalLabel || "Provider execution approval: missing"}`;
  }
  if (aiProviderStatusSetupContract) {
    aiProviderStatusSetupContract.textContent =
      state.providerSetupContractReadinessLabel || "Setup contract readiness: unavailable";
  }
  if (aiProviderStatusSetupContractBlocker) {
    aiProviderStatusSetupContractBlocker.textContent =
      state.providerSetupContractBlockerLabel || "Setup contract blocker: provider path readiness required";
  }
  if (aiProviderStatusSetupContractHandoff) {
    aiProviderStatusSetupContractHandoff.textContent =
      `${state.providerSetupContractApprovalLabel || "Setup contract approval: USER approval missing"}; ${state.futureSetupBranchHandoffState || "future-provider-setup-branch-handoff-ready-for-contract"}`;
  }
  if (aiProviderStatusSetupFoundation) {
    aiProviderStatusSetupFoundation.textContent =
      state.providerSetupFoundationLabel || "Setup implementation foundation: unavailable";
  }
  if (aiProviderStatusSetupFoundationBlocker) {
    aiProviderStatusSetupFoundationBlocker.textContent =
      state.providerSetupFoundationBlockerLabel ||
      "Setup foundation blocker: setup contract readiness required";
  }
  if (aiProviderStatusSetupFoundationValidation) {
    aiProviderStatusSetupFoundationValidation.textContent =
      state.providerSetupFoundationValidationLabel || "Setup foundation validation: fail-closed";
  }
  if (aiProviderStatusSetupFoundationPersistence) {
    aiProviderStatusSetupFoundationPersistence.textContent =
      state.providerSetupFoundationPersistenceLabel ||
      "Setup foundation persistence: disabled; no provider credentials stored";
  }
  if (aiProviderStatusSetupFoundationHandoff) {
    aiProviderStatusSetupFoundationHandoff.textContent =
      `${state.providerSetupFoundationApprovalLabel || "Setup foundation approval: USER approval missing"}; ${state.providerSetupImplementationHandoffState || "future-provider-setup-implementation-handoff-ready"}`;
  }
  if (aiProviderStatusConsentCollectionFoundation) {
    aiProviderStatusConsentCollectionFoundation.textContent =
      state.consentCollectionFoundationLabel || "Consent collection foundation: unavailable";
  }
  if (aiProviderStatusConsentCollectionBlocker) {
    aiProviderStatusConsentCollectionBlocker.textContent =
      state.consentCollectionBlockerLabel ||
      "Consent collection blocker: consent flow readiness required";
  }
  if (aiProviderStatusConsentCollectionAudit) {
    aiProviderStatusConsentCollectionAudit.textContent =
      `${state.consentAuditEnvelopeLabel || "Consent audit envelope: required before capture"}; ${state.consentPersistenceLabel || "Consent persistence: disabled; no consent stored"}`;
  }
  if (aiProviderStatusConsentCollectionHandoff) {
    aiProviderStatusConsentCollectionHandoff.textContent =
      `${state.consentCollectionApprovalLabel || "Consent collection approval: USER approval missing"}; ${state.futureConsentCaptureHandoffState || "future-consent-capture-branch-handoff-ready"}`;
  }
  if (aiProviderStatusSetupConsent) {
    aiProviderStatusSetupConsent.textContent =
      state.setupConsentLabel || "Setup consent: required before provider setup";
  }
  if (aiProviderStatusExecutionConsent) {
    aiProviderStatusExecutionConsent.textContent =
      state.executionConsentLabel || "Execution consent: required before prompt/model execution";
  }
  if (aiProviderStatusConsentUx) {
    aiProviderStatusConsentUx.textContent =
      state.consentUxLabel || "Consent UX: local-only status";
  }
  if (aiProviderStatusConsentUxSetup) {
    aiProviderStatusConsentUxSetup.textContent =
      state.consentUxSetupDisplayLabel || "Consent UX setup: missing";
  }
  if (aiProviderStatusConsentUxExecution) {
    aiProviderStatusConsentUxExecution.textContent =
      state.consentUxExecutionDisplayLabel || "Consent UX execution: missing";
  }
  if (aiProviderStatusConsentUxRevocationReset) {
    aiProviderStatusConsentUxRevocationReset.textContent =
      `${state.consentUxRevocationResetLabel || "Consent UX revoke/reset: local-only"}; ${state.consentUxWriteLabel || "Consent UX write: blocked fail-closed"}`;
  }
  if (aiProviderStatusConsentUxGates) {
    aiProviderStatusConsentUxGates.textContent =
      `Consent UX provider gates: ${state.consentUxProviderSetupGateState || "setup blocked"}; ${state.consentUxProviderExecutionGateState || "execution disabled"}`;
  }
  if (aiProviderStatusConsentSchema) {
    const consentSchemaVersion =
      state.consentReadinessStateSchemaVersion || "provider-consent-readiness-state.v1";
    const consentConfigVersion =
      state.consentReadinessConfigSchemaVersion || "provider-consent-readiness-config.v1";
    const consentConfigLabel =
      state.consentConfigLabel || "Consent config: safe default local-only";
    aiProviderStatusConsentSchema.textContent =
      `${consentSchemaVersion}; ${consentConfigVersion}; ${consentConfigLabel}`;
  }
  if (aiProviderStatusPathDataVisibility) {
    aiProviderStatusPathDataVisibility.textContent =
      `${state.providerVisibleDataRequirementLabel || "Provider-visible data requirement: none"}; ${state.dataClassificationPostureLabel || "Data classification posture: local-only"}`;
  }
  if (aiProviderStatusPathAudit) {
    aiProviderStatusPathAudit.textContent =
      `${state.auditEnvelopePostureLabel || "Audit envelope posture: planned; no collection"}; ${state.localOnlyStatusLabel || "Local-only status: active"}`;
  }
  if (aiProviderStatusPathFutureGates) {
    aiProviderStatusPathFutureGates.textContent =
      `${state.providerSetupFutureGatedLabel || "Provider setup: future-gated"}; ${state.providerExecutionFutureGatedLabel || "Provider execution: disabled; future-gated"}`;
  }
  if (aiProviderStatusAdapterSelection) {
    aiProviderStatusAdapterSelection.textContent =
      state.adapterSelectionPostureLabel || "Adapter selection: null local fallback";
  }
  if (aiProviderStatusPromptGates) {
    aiProviderStatusPromptGates.textContent =
      `${state.promptAcceptanceGateLabel || "Prompt acceptance gate: disabled"}; ${state.promptRoutingGateLabel || "Prompt routing gate: disabled"}; ${state.promptSendLabel || "Prompt send: disabled"}`;
  }
  if (aiProviderStatusModelExecution) {
    aiProviderStatusModelExecution.textContent =
      `${state.modelExecutionStatusLabel || "Model execution status: disabled"}; ${state.modelWorkloadReadinessLabel || "Model workload readiness: disabled"}`;
  }
  if (aiProviderStatusExecutionData) {
    aiProviderStatusExecutionData.textContent =
      `${state.providerVisibleDataExecutionLabel || "Provider-visible execution data: none"}; ${state.externalCallReadinessLabel || "External call readiness: blocked"}`;
  }
  if (aiProviderStatusFunctionalRelease) {
    aiProviderStatusFunctionalRelease.textContent =
      `${state.functionalAiReleaseGateLabel || "Functional-AI release gate: pending"}; ${state.v18ReleaseGateLabel || "v1.8.0-prebeta release gate: pending functional AI proof"}`;
  }
  if (aiProviderStatusCapabilityEligibility) {
    aiProviderStatusCapabilityEligibility.textContent =
      state.capabilityPackEligibilityLabel ||
      "Capability-pack eligibility: blocked until local capability proof";
  }
  if (aiProviderStatusInstallIntent) {
    aiProviderStatusInstallIntent.textContent =
      state.installIntentLabel ||
      "Install intent: blocked; downloads and install execution remain disabled";
  }
  if (aiProviderStatusPublicLane) {
    aiProviderStatusPublicLane.textContent =
      state.publicLaneBoundaryLabel ||
      "Public Edition: deterministic no-provider assist; provider-visible data none";
  }
  if (aiProviderStatusDeveloperLane) {
    aiProviderStatusDeveloperLane.textContent =
      state.developerLaneBoundaryLabel ||
      "Developer lane: gated; private setup not configured";
  }
  if (aiProviderStatusOwnerLane) {
    aiProviderStatusOwnerLane.textContent =
      state.ownerLaneBoundaryLabel ||
      "Owner lane: gated; private setup not configured";
  }
  if (aiProviderStatusAction) {
    aiProviderStatusAction.textContent = "No-provider check lives in AI Control Center";
    aiProviderStatusAction.title =
      "Status is display-only; open NDAI for the FAM-007 AI Control Center.";
    aiProviderStatusAction.disabled = true;
    aiProviderStatusAction.setAttribute("aria-disabled", "true");
    aiProviderStatusAction.dataset.localActionGuard = "no-provider";
    aiProviderStatusAction.dataset.statusOnly = "true";
    aiProviderStatusAction.dataset.aiControlCenterRoute = "fam007-ai-control-center";
  }
  if (aiProviderStatusFallback) {
    aiProviderStatusFallback.textContent = state.noProviderFallbackLabel || "No-provider fallback active";
  }
  if (aiProviderStatusResult) {
    aiProviderStatusResult.textContent =
      "No-provider check: waiting for local action";
  }
  if (aiProviderStatusResultDetail) {
    aiProviderStatusResultDetail.textContent =
      "Run the check to produce a deterministic no-provider result.";
  }
  if (aiProviderStatusNextAction) {
    aiProviderStatusNextAction.textContent =
      state.providerNextActionLabel ||
      "Open NDAI for the AI Control Center; provider/model execution remains blocked";
  }
  if (aiProviderStatusPrivacy) {
    aiProviderStatusPrivacy.textContent = state.privacyLabel || "Local shell only; nothing is sent";
  }
  renderAIProviderTrayState(state, displayVisible, localActionAvailable);
}

function handleAIProviderStatusActionClick(event) {
  event.preventDefault();
  if (!aiProviderStatus) return;

  const state = aiProviderState || {};
  const guardClosed =
    state.sentToProvider === false &&
    state.canAcceptPrompts === false &&
    state.providerVisibleData === "none" &&
    state.promptSendPosture === "prompt-send-disabled" &&
    state.networkEgressState === "network-egress-blocked" &&
    state.memoryIndexingState === "memory-indexing-disabled";

  const resultState = guardClosed
    ? (state.localActionResultState || "deterministic-no-provider-result")
    : "blocked-boundary-mismatch";
  const resultLabel = guardClosed
    ? (state.localActionResultLabel || "No-provider check: no provider configured")
    : "No-provider check: blocked";
  const resultDetail = guardClosed
    ? (state.localActionResultDetail ||
      "Deterministic degraded result: no prompt was accepted or sent; provider-visible data remains none.")
    : "Provider boundary mismatch; no local result was produced.";

  aiProviderStatus.dataset.localActionResult = resultState;
  aiProviderStatus.dataset.localActionResultState = resultState;
  aiProviderStatus.dataset.localActionGuardResult =
    guardClosed ? "guarded-no-provider" : "blocked-boundary-mismatch";
  aiProviderStatus.dataset.sentToProvider = "false";
  aiProviderStatus.dataset.canAcceptPrompts = "false";
  aiProviderStatus.dataset.providerVisibleData = "none";
  aiProviderStatus.dataset.localResultProviderVisibleData = "none";
  aiProviderStatus.dataset.localResultSentToProvider = "false";
  aiProviderStatus.dataset.localResultCanAcceptPrompts = "false";
  aiProviderStatus.dataset.localResultPromptSend = "prompt-send-disabled";
  aiProviderStatus.dataset.localResultNetworkEgress = "network-egress-blocked";
  aiProviderStatus.dataset.localResultMemoryIndexing = "memory-indexing-disabled";

  if (aiProviderStatusFallback) {
    aiProviderStatusFallback.textContent = guardClosed
      ? "No-provider check complete; provider-visible data remains none"
      : "No-provider check blocked; provider boundary mismatch";
  }
  if (aiProviderStatusResult) {
    aiProviderStatusResult.textContent = resultLabel;
  }
  if (aiProviderStatusResultDetail) {
    aiProviderStatusResultDetail.textContent = resultDetail;
  }
  if (aiProviderStatusNextAction) {
    aiProviderStatusNextAction.textContent = guardClosed
      ? resultDetail
      : "Provider boundary mismatch; no local action ran.";
  }
  if (aiProviderTrayResult) {
    aiProviderTrayResult.textContent = resultLabel;
  }
  if (aiProviderTrayResultDetail) {
    aiProviderTrayResultDetail.textContent = resultDetail;
  }
  if (aiProviderTrayProviderVisibleData) {
    aiProviderTrayProviderVisibleData.textContent = "none";
  }
  if (aiProviderTray) {
    aiProviderTray.dataset.providerVisibleData = "none";
    aiProviderTray.dataset.promptSend = "prompt-send-disabled";
    aiProviderTray.dataset.networkEgress = "network-egress-blocked";
    aiProviderTray.dataset.memoryIndexing = "memory-indexing-disabled";
  }
  if (aiProviderTrayWindow) {
    aiProviderTrayWindow.dataset.providerVisibleData = "none";
    aiProviderTrayWindow.dataset.promptSend = "prompt-send-disabled";
    aiProviderTrayWindow.dataset.networkEgress = "network-egress-blocked";
    aiProviderTrayWindow.dataset.memoryIndexing = "memory-indexing-disabled";
  }
  if (aiLocalStatusSurface) {
    aiLocalStatusSurface.dataset.statusOnly = "true";
    aiLocalStatusSurface.dataset.interactive = "false";
    aiLocalStatusSurface.dataset.opensControlCenter = "false";
    aiLocalStatusSurface.dataset.activityState = guardClosed ? "active" : "blocked";
    aiLocalStatusSurface.dataset.providerVisibleData = "none";
    aiLocalStatusSurface.dataset.promptSend = "prompt-send-disabled";
    aiLocalStatusSurface.dataset.networkEgress = "network-egress-blocked";
    aiLocalStatusSurface.dataset.memoryIndexing = "memory-indexing-disabled";
  }
  setTextContent(
    aiLocalStatusActivity,
    guardClosed ? "Checked locally" : "Blocked"
  );
}

if (aiProviderStatusAction) {
  aiProviderStatusAction.disabled = true;
  aiProviderStatusAction.setAttribute("aria-disabled", "true");
  aiProviderStatusAction.dataset.statusOnly = "true";
  aiProviderStatusAction.dataset.aiControlCenterRoute = "fam007-ai-control-center";
}
if (aiProviderTray) {
  aiProviderTray.hidden = true;
  aiProviderTray.setAttribute("aria-hidden", "true");
  aiProviderTray.setAttribute("tabindex", "-1");
  aiProviderTray.dataset.interactive = "false";
  aiProviderTray.dataset.desktopTrayDoorway = "native-system-tray";
}
if (aiProviderTrayClose) {
  aiProviderTrayClose.disabled = true;
  aiProviderTrayClose.setAttribute("aria-disabled", "true");
}
if (aiProviderTrayLocalAssistAction) {
  aiProviderTrayLocalAssistAction.disabled = true;
  aiProviderTrayLocalAssistAction.setAttribute("aria-disabled", "true");
}
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    setAIProviderTrayOpen(false);
  }
});

function frame(ts) {
  t = ts;
  if (currentState === "boot" && bootStartTime === null) bootStartTime = t;

if (voiceLevel > smoothedVoiceLevel) {
  smoothedVoiceLevel = lerp(smoothedVoiceLevel, voiceLevel, 0.42);
} else {
  smoothedVoiceLevel = lerp(smoothedVoiceLevel, voiceLevel, 0.16);
}

  clear();
  drawBackgroundNoise();
  drawAtmosphericBands();
  drawBackParticles();
  drawSpokes();
  drawBrokenShells();
  drawOrbitTrails();
  drawAnimatedRings();
  drawSwarms();
  drawFilaments();
  drawOrbiterSet(bctx, orbitersBack, false);
  drawCoreSheen();
  drawArrivalPulse();
  drawFrontParticles();
  drawOrbiterSet(fctx, orbitersFront, true);
  drawRelayBursts();
  drawBlips();
  drawForegroundSweep();
  requestAnimationFrame(frame);
}

window.setCoreVisualState = function (stateName) {
  lastState = currentState;
  currentState = stateName || "idle";

  if (currentState === "boot") {
    ignition = 0.0;
    bootStartTime = null;
  } else if (lastState === "boot") {
    ignition = 1.0;
  } else if (currentState !== "boot") {
    ignition = 1.0;
  }

  body.classList.remove(
    "state-boot",
    "state-idle",
    "state-speaking",
    "state-processing",
    "state-dormant"
  );
  body.classList.add(`state-${currentState}`);
};

window.setCoreVoiceLevel = function(level) {
  voiceLevel = clamp(Number(level) || 0, 0, 1);
};

window.setCommandOverlayState = function(state) {
  commandOverlayState = Object.assign({}, commandOverlayState, state || {});
  renderCommandOverlay();
};

window.setAIProviderState = function(state) {
  aiProviderState = Object.assign({}, aiProviderState, state || {});
  renderAIProviderState();
};

window.setCoreVisualState("boot");
window.setCoreVoiceLevel(0);
window.setCommandOverlayState({ visible: false });
window.setAIProviderState(aiProviderState);
requestAnimationFrame(frame);
