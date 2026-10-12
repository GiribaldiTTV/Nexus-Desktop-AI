"""Provider/no-provider and foundation-readiness state contract for FAM-007.

This module owns local-only FAM-007 scaffolds. It does not load models, call
provider SDKs, persist memory, probe hardware, or infer a configured provider.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ID = "PKG-007"
SLC_017_ID = "SLC-017"
SLC_018_ID = "SLC-018"
SLC_031_ID = "SLC-031"
SLC_032_ID = "SLC-032"
SLC_033_ID = "SLC-033"
SLC_034_ID = "SLC-034"
SLC_035_ID = "SLC-035"
SLC_036_ID = "SLC-036"
STATE_ID = "provider-boundary-no-provider-shell"
PROVIDER_SELECTION_STATE_ID = "provider-selection-consent-boundary"
LOCAL_PROVIDER_REGISTRY_STATE_ID = "local-provider-registry-configuration-state"
LOCAL_HARDWARE_CAPABILITY_STATE_ID = "hardware-gpu-cpu-capability-planning"
FAM007_FOUNDATION_READINESS_STATE_ID = "fam007-foundation-readiness-scaffold"
LOCAL_AI_RUNTIME_FOUNDATION_STATE_ID = "local-ai-runtime-foundation-provider-boundary"
FAM007_EXECUTION_READINESS_STATE_ID = "fam007-execution-readiness-gates"
FAM007_PROVIDER_PATH_CONSENT_READINESS_STATE_ID = "fam007-provider-path-consent-readiness"
FAM007_PROVIDER_SETUP_CONSENT_FLOW_READINESS_STATE_ID = "fam007-provider-setup-consent-flow-readiness"
FAM007_PROVIDER_SETUP_CONTRACT_READINESS_STATE_ID = "fam007-provider-setup-contract-readiness"
FAM007_PROVIDER_SETUP_IMPLEMENTATION_FOUNDATION_STATE_ID = (
    "fam007-provider-setup-implementation-foundation"
)
FAM007_PROVIDER_CONSENT_COLLECTION_FOUNDATION_STATE_ID = (
    "fam007-provider-consent-collection-foundation"
)
FAM007_PROVIDER_CONSENT_COLLECTION_IMPLEMENTATION_FOUNDATION_STATE_ID = (
    "fam007-provider-consent-collection-implementation-foundation"
)
FAM007_PROVIDER_DURABLE_CONSENT_PERSISTENCE_FOUNDATION_STATE_ID = (
    "fam007-provider-durable-consent-persistence-foundation"
)
FAM007_PROVIDER_USER_OPERATED_CONSENT_UX_FOUNDATION_STATE_ID = (
    "fam007-provider-user-operated-consent-ux-foundation"
)
FAM007_PROVIDER_SETUP_COMPLETION_FOUNDATION_STATE_ID = (
    "fam007-provider-setup-completion-foundation"
)
OWNER_AI_OPERATIONAL_FOUNDATION_GATES_SCHEMA_VERSION = (
    "owner-ai-operational-foundation-gates.v1"
)

NO_PROVIDER_MODE = "no-provider"
NO_PROVIDER_AVAILABILITY = "disabled"
NO_PROVIDER_PRIVACY_SCOPE = "local-only"
PROVIDER_SELECTION_MODE = "provider-selection"
PROVIDER_SELECTION_AVAILABILITY = "unavailable"
LOCAL_PROVIDER_REGISTRY_MODE = "provider-registry"
LOCAL_PROVIDER_REGISTRY_AVAILABILITY = "unavailable"
LOCAL_HARDWARE_CAPABILITY_MODE = "hardware-capability-planning"
LOCAL_HARDWARE_CAPABILITY_AVAILABILITY = "planning-only"
FAM007_FOUNDATION_READINESS_MODE = "foundation-readiness"
FAM007_FOUNDATION_READINESS_AVAILABILITY = "planning-only"
LOCAL_AI_RUNTIME_FOUNDATION_MODE = "runtime-foundation-provider-boundary"
LOCAL_AI_RUNTIME_FOUNDATION_AVAILABILITY = "disabled"
FAM007_EXECUTION_READINESS_MODE = "execution-readiness-gates"
FAM007_EXECUTION_READINESS_AVAILABILITY = "disabled"
FAM007_PROVIDER_PATH_CONSENT_READINESS_MODE = "provider-path-consent-readiness"
FAM007_PROVIDER_PATH_CONSENT_READINESS_AVAILABILITY = "disabled"
FAM007_PROVIDER_SETUP_CONSENT_FLOW_READINESS_MODE = "provider-setup-consent-flow-readiness"
FAM007_PROVIDER_SETUP_CONSENT_FLOW_READINESS_AVAILABILITY = "disabled"
FAM007_PROVIDER_SETUP_CONTRACT_READINESS_MODE = "provider-setup-contract-readiness"
FAM007_PROVIDER_SETUP_CONTRACT_READINESS_AVAILABILITY = "disabled"
FAM007_PROVIDER_SETUP_IMPLEMENTATION_FOUNDATION_MODE = "provider-setup-implementation-foundation"
FAM007_PROVIDER_SETUP_IMPLEMENTATION_FOUNDATION_AVAILABILITY = "disabled"
FAM007_PROVIDER_CONSENT_COLLECTION_FOUNDATION_MODE = "provider-consent-collection-foundation"
FAM007_PROVIDER_CONSENT_COLLECTION_IMPLEMENTATION_FOUNDATION_MODE = (
    "provider-consent-collection-implementation-foundation"
)
FAM007_PROVIDER_DURABLE_CONSENT_PERSISTENCE_FOUNDATION_MODE = (
    "provider-durable-consent-persistence-foundation"
)
FAM007_PROVIDER_USER_OPERATED_CONSENT_UX_FOUNDATION_MODE = (
    "provider-user-operated-consent-ux-foundation"
)
FAM007_PROVIDER_SETUP_COMPLETION_FOUNDATION_MODE = (
    "provider-setup-completion-foundation"
)
FAM007_PROVIDER_CONSENT_COLLECTION_FOUNDATION_AVAILABILITY = "disabled"
FAM007_PROVIDER_CONSENT_COLLECTION_IMPLEMENTATION_FOUNDATION_AVAILABILITY = "disabled"
FAM007_PROVIDER_DURABLE_CONSENT_PERSISTENCE_FOUNDATION_AVAILABILITY = "disabled"
FAM007_PROVIDER_USER_OPERATED_CONSENT_UX_FOUNDATION_AVAILABILITY = "disabled"
FAM007_PROVIDER_SETUP_COMPLETION_FOUNDATION_AVAILABILITY = "disabled"
NO_PROVIDER_ID = "no-provider"
NO_PROVIDER_FALLBACK_SELECTION = "fallback-no-provider"
PROVIDER_CONSENT_REQUIRED = "required-before-provider"
NO_PROVIDER_INTERACTION_AFFORDANCE = "disabled-no-provider-interaction"
LOCAL_ASSISTED_INTERACTION_AFFORDANCE = "local-assisted-action-available"
PROVIDER_CONFIGURATION_UNCONFIGURED = "unconfigured"
PROVIDER_CONFIGURATION_FALLBACK_ACTIVE = "fallback-active"
LOCAL_PROVIDER_REGISTRY_STATE = "local-only-registry"
PROVIDER_BOUNDARY_INTERACTION_PLAN_STATE = "provider-boundary-interaction-plan"
PROVIDER_NEXT_ACTION_DISABLED = "provider-setup-disabled-until-consent"
LOCAL_HARDWARE_CAPABILITY_STATE = "local-planning-only"
GPU_CAPABILITY_UNPROBED = "gpu-unprobed"
CPU_FALLBACK_PRESERVED = "cpu-fallback-preserved"
POWER_STATE_NOT_EVALUATED = "power-state-not-evaluated"
THERMAL_GUARDRAILS_REQUIRED = "thermal-guardrails-required"
MODEL_WORKLOAD_DISABLED = "model-workload-disabled"
CAPABILITY_RECOMMENDATION_PENDING = "recommendation-pending"
CAPABILITY_PACK_LIFECYCLE_PLANNED = "capability-pack-lifecycle-planned"
CAPABILITY_PACK_DOWNLOADS_BLOCKED = "capability-pack-downloads-blocked"
HARDWARE_DETECTION_LEVEL_0 = "level-0-unknown-unprobed"
HARDWARE_DETECTION_LEVEL_1 = "level-1-safe-local-static-snapshot"
HARDWARE_DETECTION_LEVEL_2 = "level-2-lightweight-capability-check-future-gated"
HARDWARE_DETECTION_LEVEL_3 = "level-3-heavy-runtime-validation-blocked"
CAPABILITY_SNAPSHOT_POLICY_LOCAL_STATIC = "local-static-no-heavy-probe"
CAPABILITY_SNAPSHOT_SOURCE_DEFAULT = "default-static-snapshot"
RAM_READINESS_UNPROBED = "ram-unprobed"
DISK_READINESS_UNPROBED = "disk-unprobed"
CAPABILITY_PACK_MANIFEST_SCHEMA_VERSION = "capability-pack-manifest.v1"
CAPABILITY_PACK_MANIFEST_PLANNED = "manifest-planned"
CAPABILITY_PACK_SOURCE_LOCAL_ONLY = "local-source-future-gated"
CAPABILITY_PACK_CHECKSUM_REQUIRED = "checksum-required-before-install"
CAPABILITY_PACK_SIGNATURE_REQUIRED = "signature-required-before-install"
CAPABILITY_PACK_COMPATIBILITY_UNPROVEN = "compatibility-unproven"
CAPABILITY_PACK_INSTALL_BLOCKED = "install-blocked"
CAPABILITY_PACK_UPDATE_BLOCKED = "update-blocked"
CAPABILITY_PACK_UNINSTALL_BLOCKED = "uninstall-blocked"
LANE_BOUNDARY_SCHEMA_VERSION = "lane-boundary-state.v1"
PUBLIC_LANE_BOUNDARY_LOCAL_ASSIST_ONLY = "public-lane-local-assist-only"
DEVELOPER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED = "developer-lane-private-setup-blocked"
OWNER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED = "owner-lane-private-setup-blocked"
PRIVATE_SETUP_BOUNDARY_BLOCKED = "private-setup-blocked"
SLC005_ENFORCEMENT_PROOF_SCHEMA_VERSION = "slc005-enforcement-proof.v1"
MODEL_WORKLOAD_METADATA_PLANNED = "model-workload-metadata-planned"
DATA_CLASSIFICATION_LOCAL_ONLY = "data-classification-local-only"
DATA_CLASSIFICATION_SCHEMA_VERSION = "data-classification.v1"
PROVIDER_VISIBLE_DATA_GUARANTEE_NONE = "provider-visible-data-none-guaranteed"
MEMORY_CONTEXT_DISABLED = "memory-context-disabled"
MEMORY_INDEXING_DISABLED = "memory-indexing-disabled"
RETRIEVAL_DISABLED = "retrieval-disabled"
LEARNING_DISABLED = "learning-disabled"
PERSISTENCE_DISABLED = "persistence-disabled"
CONSENT_ENVELOPE_REQUIRED = "consent-envelope-required"
AUDIT_ENVELOPE_PLANNED = "audit-envelope-planned"
AUDIT_SECRETS_PLANNED = "audit-secrets-planned"
SECRET_BOUNDARY_NO_SECRETS = "secret-boundary-no-secrets-stored"
NETWORK_EGRESS_BLOCKED = "network-egress-blocked"
LOCAL_AI_READINESS_REPORT_SCHEMA_VERSION = "local-ai-readiness-report.v1"
LOCAL_AI_READINESS_REPORT_STATE_READY = "report-ready"
LOCAL_AI_READINESS_REPORT_COPY_MODE = "clipboard-only-user-initiated"
LOCAL_AI_READINESS_REPORT_PERSISTENCE = "view-only-no-file-persistence"
FUTURE_MEMORY_ELIGIBILITY_GATED = "future-memory-eligibility-gated"
WINDOWS_RESILIENCE_PLANNED = "windows-resilience-planned"
OFFLINE_DEGRADED_PLANNED = "offline-degraded-planned"
PERSONA_CORE_VOICE_BOUNDARY_PLANNED = "persona-core-voice-boundary-planned"
VOICE_RUNTIME_DISABLED = "voice-runtime-disabled"
VALIDATION_PROOF_GATES_PLANNED = "validation-proof-gates-planned"
ABUSE_EVAL_PENDING = "abuse-eval-pending"
RELEASE_PROOF_PENDING = "release-proof-pending"
CORE_DESKTOP_COPY_CONTRACT_VERSION = "core-desktop-provider-state-copy.v1"
CORE_DESKTOP_RUNTIME_STATE_CONTRACT = "core-desktop-runtime-state-contract"
DISABLED_PROMPT_BEHAVIOR_CONTRACT = "disabled-prompt-provider-behavior"
GOLDEN_PROVIDER_STATE_FIXTURES = "golden-provider-state-fixtures"
VALIDATOR_EXPANSION_ACTIVE = "validator-expansion-active"
CONTRACT_READY_MARKER = "contract-ready"
UI_READY_MARKER = "ui-ready"
VALIDATOR_READY_MARKER = "validator-ready"
FUTURE_IMPLEMENTATION_GATED_MARKER = "future-implementation-gated"
OWNER_AI_PROTECTED_ARTIFACT_CLASSES = (
    "owner-private-prompts",
    "owner-private-memory",
    "private-dev-orin-content",
    "secrets-and-credentials",
    "private-model-or-capability-assets",
    "private-eval-logs",
    "private-automation",
    "imported-public-user-data",
)
OWNER_AI_PUBLIC_EXCLUSION_TARGETS = (
    "public-repo",
    "local-user-review-packet",
    "timestamped-user-upload-zip",
    "public-review-bundle",
    "public-release-artifact",
)
PROVIDER_RUNTIME_STATE_SCHEMA_VERSION = "provider-runtime-state.v1"
PROVIDER_RUNTIME_CONFIG_SCHEMA_VERSION = "provider-runtime-config.v1"
PROVIDER_RUNTIME_CONFIG_MIGRATION_POSTURE = "no-runtime-migration-required"
PROVIDER_RUNTIME_CATEGORY_NO_PROVIDER = "no_provider"
PROVIDER_RUNTIME_CATEGORY_SETUP_DISABLED = "provider_setup_disabled"
PROVIDER_RUNTIME_CATEGORY_UNCONFIGURED = "provider_unconfigured"
PROVIDER_RUNTIME_CATEGORY_UNAVAILABLE = "provider_unavailable"
PROVIDER_RUNTIME_CATEGORY_CONSENT_MISSING = "provider_consent_missing"
PROVIDER_RUNTIME_CATEGORY_CAPABILITY_MISSING = "provider_capability_missing"
PROVIDER_RUNTIME_CATEGORY_READY_FUTURE_GATED = "provider_ready_future_gated"
PROVIDER_RUNTIME_CATEGORY_ERROR_DEGRADED = "provider_error_degraded"
PROVIDER_RUNTIME_REASON_NO_PROVIDER_CONFIGURED = "no_provider_configured"
PROVIDER_RUNTIME_REASON_SETUP_DISABLED_LOCAL_ONLY = "provider_setup_disabled_local_only"
PROVIDER_RUNTIME_REASON_PROVIDER_UNCONFIGURED = "provider_unconfigured"
PROVIDER_RUNTIME_REASON_PROVIDER_UNAVAILABLE = "provider_unavailable"
PROVIDER_RUNTIME_REASON_CONSENT_REQUIRED = "provider_consent_required"
PROVIDER_RUNTIME_REASON_CAPABILITY_MISSING = "provider_capability_missing"
PROVIDER_RUNTIME_REASON_READY_FUTURE_GATED = "provider_ready_future_gated"
PROVIDER_RUNTIME_REASON_INVALID_CONFIG_FAIL_CLOSED = "invalid_config_fail_closed"
PROVIDER_RUNTIME_REASON_MISSING_CONFIG_FAIL_CLOSED = "missing_config_fail_closed"
PROVIDER_RUNTIME_PROVENANCE_DEFAULT_CONFIG = "default_config"
PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG = "local_config"
PROVIDER_RUNTIME_PROVENANCE_HARDWARE_SNAPSHOT = "hardware_snapshot"
PROVIDER_RUNTIME_PROVENANCE_MANIFEST_STATE = "manifest_state"
PROVIDER_RUNTIME_PROVENANCE_VALIDATOR_FIXTURE = "validator_fixture"
PROVIDER_RUNTIME_PROVENANCE_FUTURE_RUNTIME_CHECK = "future_runtime_check"
PROVIDER_RUNTIME_CONFIG_STATE_DEFAULT = "default_config"
PROVIDER_RUNTIME_CONFIG_STATE_MISSING = "missing_config"
PROVIDER_RUNTIME_CONFIG_STATE_INVALID = "invalid_config"
PROVIDER_RUNTIME_CONFIG_STATE_LOCAL = "local_config"
PROVIDER_READINESS_STATE_SCHEMA_VERSION = "provider-readiness-state.v1"
PROVIDER_READINESS_CONFIG_SCHEMA_VERSION = "provider-readiness-config.v1"
PROVIDER_READINESS_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-runtime-migration"
PROVIDER_READINESS_STATE_UNKNOWN = "readiness_unknown"
PROVIDER_READINESS_STATE_SETUP_DISABLED = "setup_disabled"
PROVIDER_READINESS_STATE_SETUP_AVAILABLE_FUTURE_GATED = "setup_available_future_gated"
PROVIDER_READINESS_STATE_SETUP_INELIGIBLE = "setup_ineligible"
PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CONSENT = "setup_blocked_by_consent"
PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CAPABILITY = "setup_blocked_by_capability"
PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_MANIFEST = "setup_blocked_by_manifest"
PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_POLICY = "setup_blocked_by_policy"
PROVIDER_READINESS_STATE_SETUP_CONFIG_REQUIRED = "setup_config_required"
PROVIDER_READINESS_STATE_PROVIDER_READY_EXECUTION_GATED = "provider_ready_but_execution_gated"
PROVIDER_READINESS_STATE_DEGRADED = "degraded_readiness"
PROVIDER_SETUP_ELIGIBILITY_DISABLED = "setup_eligibility_disabled"
PROVIDER_SETUP_ELIGIBILITY_FUTURE_GATED = "setup_eligibility_future_gated"
PROVIDER_SETUP_ELIGIBILITY_INELIGIBLE = "setup_eligibility_ineligible"
PROVIDER_SETUP_ELIGIBILITY_BLOCKED = "setup_eligibility_blocked"
PROVIDER_SETUP_ELIGIBILITY_CONFIG_REQUIRED = "setup_eligibility_config_required"
PROVIDER_SETUP_ELIGIBILITY_EXECUTION_GATED = "setup_eligibility_execution_gated"
PROVIDER_SETUP_BLOCKER_NONE = "none"
PROVIDER_SETUP_BLOCKER_SETUP_DISABLED = "setup_disabled"
PROVIDER_SETUP_BLOCKER_CONSENT_REQUIRED = "consent_required"
PROVIDER_SETUP_BLOCKER_CAPABILITY_REQUIRED = "capability_required"
PROVIDER_SETUP_BLOCKER_MANIFEST_REQUIRED = "manifest_required"
PROVIDER_SETUP_BLOCKER_POLICY_BLOCKED = "policy_blocked"
PROVIDER_SETUP_BLOCKER_CONFIG_REQUIRED = "config_required"
PROVIDER_SETUP_BLOCKER_CONFIG_INVALID = "config_invalid"
PROVIDER_SETUP_BLOCKER_FUTURE_GATE = "future_gate"
PROVIDER_SETUP_BLOCKER_PROVIDER_NOT_READY = "provider_not_ready"
PROVIDER_READINESS_REASON_DEFAULT_LOCAL_ONLY = "readiness_default_local_only"
PROVIDER_READINESS_REASON_CONFIG_MISSING_FAIL_CLOSED = "readiness_config_missing_fail_closed"
PROVIDER_READINESS_REASON_CONFIG_INVALID_FAIL_CLOSED = "readiness_config_invalid_fail_closed"
PROVIDER_READINESS_REASON_PROVIDER_UNCONFIGURED = "readiness_provider_unconfigured"
PROVIDER_READINESS_REASON_CONSENT_MISSING = "readiness_consent_missing"
PROVIDER_READINESS_REASON_CAPABILITY_MISSING = "readiness_capability_missing"
PROVIDER_READINESS_REASON_MANIFEST_MISSING = "readiness_manifest_missing"
PROVIDER_READINESS_REASON_MANIFEST_INVALID_INSTALL_BLOCKED = "readiness_manifest_invalid_install_blocked"
PROVIDER_READINESS_REASON_POLICY_BLOCKED = "readiness_policy_blocked"
PROVIDER_READINESS_REASON_FUTURE_PROVIDER_GATED = "readiness_future_provider_gated"
PROVIDER_READINESS_REASON_PROVIDER_NOT_READY = "readiness_provider_not_ready"
PROVIDER_READINESS_REASON_PROVIDER_READY_EXECUTION_GATED = "readiness_provider_ready_execution_gated"
PROVIDER_READINESS_PROVENANCE_DEFAULT_CONFIG = "default_config"
PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG = "local_config"
PROVIDER_READINESS_PROVENANCE_RELEASE_SOURCE_TRUTH = "release_source_truth"
PROVIDER_READINESS_PROVENANCE_HARDWARE_SNAPSHOT = "hardware_snapshot"
PROVIDER_READINESS_PROVENANCE_CAPABILITY_MANIFEST = "capability_manifest"
PROVIDER_READINESS_PROVENANCE_CONSENT_STATE = "consent_state"
PROVIDER_READINESS_PROVENANCE_VALIDATOR_FIXTURE = "validator_fixture"
PROVIDER_READINESS_PROVENANCE_FUTURE_RUNTIME_CHECK = "future_runtime_check"
PROVIDER_READINESS_CONFIG_STATE_DEFAULT = "default_config"
PROVIDER_READINESS_CONFIG_STATE_MISSING = "missing_config"
PROVIDER_READINESS_CONFIG_STATE_INVALID = "invalid_config"
PROVIDER_READINESS_CONFIG_STATE_LOCAL = "local_config"
PROVIDER_FUTURE_GATE_STATUS_SETUP_REQUIRED = "provider-setup-future-user-approval-required"
PROVIDER_FUTURE_GATE_STATUS_EXECUTION_REQUIRED = "provider-execution-future-user-approval-required"
PROVIDER_ACTIVATION_STATE_SCHEMA_VERSION = "provider-activation-state.v1"
PROVIDER_ACTIVATION_CONFIG_SCHEMA_VERSION = "provider-activation-config.v1"
PROVIDER_ACTIVATION_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-runtime-migration"
PROVIDER_ACTIVATION_STATE_UNKNOWN = "activation_unknown"
PROVIDER_ACTIVATION_STATE_UNAVAILABLE = "activation_unavailable"
PROVIDER_ACTIVATION_STATE_DISABLED = "activation_disabled"
PROVIDER_ACTIVATION_STATE_BLOCKED_BY_READINESS = "activation_blocked_by_readiness"
PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CONSENT = "activation_blocked_by_consent"
PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CAPABILITY = "activation_blocked_by_capability"
PROVIDER_ACTIVATION_STATE_BLOCKED_BY_POLICY = "activation_blocked_by_policy"
PROVIDER_ACTIVATION_STATE_BLOCKED_BY_MANIFEST = "activation_blocked_by_manifest"
PROVIDER_ACTIVATION_STATE_BLOCKED_BY_ADAPTER = "activation_blocked_by_adapter"
PROVIDER_ACTIVATION_STATE_ELIGIBLE_FUTURE_GATED = "activation_eligible_future_gated"
PROVIDER_ACTIVATION_STATE_READY_EXECUTION_GATED = "activation_ready_but_execution_gated"
PROVIDER_ACTIVATION_STATE_DEGRADED = "activation_degraded"
PROVIDER_ACTIVATION_STATE_FUNCTIONAL_AI_READY_FUTURE_VERSION = "functional_ai_ready_future_version"
PROVIDER_ACTIVATION_ELIGIBILITY_UNAVAILABLE = "activation_eligibility_unavailable"
PROVIDER_ACTIVATION_ELIGIBILITY_DISABLED = "activation_eligibility_disabled"
PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED = "activation_eligibility_blocked"
PROVIDER_ACTIVATION_ELIGIBILITY_FUTURE_GATED = "activation_eligibility_future_gated"
PROVIDER_ACTIVATION_ELIGIBILITY_EXECUTION_GATED = "activation_eligibility_execution_gated"
PROVIDER_ACTIVATION_ELIGIBILITY_FUTURE_VERSION = "activation_eligibility_future_version"
PROVIDER_ACTIVATION_BLOCKER_NONE = "none"
PROVIDER_ACTIVATION_BLOCKER_READINESS_REQUIRED = "readiness_required"
PROVIDER_ACTIVATION_BLOCKER_CONSENT_REQUIRED = "consent_required"
PROVIDER_ACTIVATION_BLOCKER_CAPABILITY_REQUIRED = "capability_required"
PROVIDER_ACTIVATION_BLOCKER_POLICY_BLOCKED = "policy_blocked"
PROVIDER_ACTIVATION_BLOCKER_MANIFEST_REQUIRED = "manifest_required"
PROVIDER_ACTIVATION_BLOCKER_ADAPTER_UNAVAILABLE = "adapter_unavailable"
PROVIDER_ACTIVATION_BLOCKER_EXECUTION_GATE = "execution_gate"
PROVIDER_ACTIVATION_BLOCKER_FUTURE_ACTIVATION_GATE = "future_activation_gate"
PROVIDER_ACTIVATION_BLOCKER_CONFIG_INVALID = "activation_config_invalid"
PROVIDER_ACTIVATION_BLOCKER_VERSION_JUMP_REQUIRED = "version_jump_required"
PROVIDER_ACTIVATION_REASON_DEFAULT_UNAVAILABLE = "activation_default_unavailable"
PROVIDER_ACTIVATION_REASON_CONFIG_MISSING_FAIL_CLOSED = "activation_config_missing_fail_closed"
PROVIDER_ACTIVATION_REASON_CONFIG_INVALID_FAIL_CLOSED = "activation_config_invalid_fail_closed"
PROVIDER_ACTIVATION_REASON_READINESS_BLOCKED = "activation_readiness_blocked"
PROVIDER_ACTIVATION_REASON_CONSENT_REQUIRED = "activation_consent_required"
PROVIDER_ACTIVATION_REASON_CAPABILITY_REQUIRED = "activation_capability_required"
PROVIDER_ACTIVATION_REASON_POLICY_BLOCKED = "activation_policy_blocked"
PROVIDER_ACTIVATION_REASON_MANIFEST_REQUIRED = "activation_manifest_required"
PROVIDER_ACTIVATION_REASON_ADAPTER_UNAVAILABLE = "activation_adapter_unavailable"
PROVIDER_ACTIVATION_REASON_FUTURE_GATED = "activation_future_gated"
PROVIDER_ACTIVATION_REASON_EXECUTION_GATED = "activation_execution_gated"
PROVIDER_ACTIVATION_REASON_FUNCTIONAL_AI_FUTURE_VERSION = "activation_functional_ai_future_version"
PROVIDER_ACTIVATION_PROVENANCE_DEFAULT_CONFIG = "default_config"
PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG = "local_config"
PROVIDER_ACTIVATION_PROVENANCE_READINESS_STATE = "readiness_state"
PROVIDER_ACTIVATION_PROVENANCE_CAPABILITY_MANIFEST = "capability_manifest"
PROVIDER_ACTIVATION_PROVENANCE_CONSENT_STATE = "consent_state"
PROVIDER_ACTIVATION_PROVENANCE_ADAPTER_CONTRACT = "adapter_contract"
PROVIDER_ACTIVATION_PROVENANCE_VALIDATOR_FIXTURE = "validator_fixture"
PROVIDER_ACTIVATION_PROVENANCE_FUTURE_RUNTIME_CHECK = "future_runtime_check"
PROVIDER_ACTIVATION_PROVENANCE_RELEASE_SOURCE_TRUTH = "release_source_truth"
PROVIDER_ACTIVATION_CONFIG_STATE_DEFAULT = "default_config"
PROVIDER_ACTIVATION_CONFIG_STATE_MISSING = "missing_config"
PROVIDER_ACTIVATION_CONFIG_STATE_INVALID = "invalid_config"
PROVIDER_ACTIVATION_CONFIG_STATE_LOCAL = "local_config"
PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_REQUIRED = "activation-future-user-approval-required"
PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_EXECUTION_REQUIRED = "activation-execution-future-user-approval-required"
PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_VERSION_JUMP_REQUIRED = "functional-ai-version-jump-required"
PROVIDER_ADAPTER_POSTURE_NULL_LOCAL = "null-local-adapter"
PROVIDER_ADAPTER_KIND_NULL = "null"
PROVIDER_ADAPTER_AVAILABILITY_UNAVAILABLE = "adapter-unavailable"
PROVIDER_ADAPTER_AVAILABILITY_READY_FUTURE_GATED = "adapter-ready-future-gated"
PROVIDER_ADAPTER_EXECUTION_POSTURE_DISABLED = "adapter-execution-disabled"
PROVIDER_METADATA_CONTRACT_VERSION = "provider-metadata-contract.v1"
PROVIDER_CONFIG_ENVELOPE_VERSION = "provider-config-envelope.v1"
PROVIDER_ACTIVATION_HANDOFF_STATE_FUTURE_GATED = "activation-handoff-future-gated"
PROVIDER_SDK_INTEGRATION_BOUNDARY_FUTURE_APPROVAL = "future-sdk-integration-user-approval-required"
PROMPT_EXECUTION_GATE_DISABLED = "prompt-execution-disabled"
MODEL_EXECUTION_GATE_DISABLED = "model-execution-disabled"
PROVIDER_EXECUTION_GATE_DISABLED = "provider-execution-disabled"
FUNCTIONAL_AI_CRITERIA_PENDING = "functional-ai-criteria-pending"
FUNCTIONAL_AI_CRITERIA_READY_FUTURE_VERSION = "functional-ai-criteria-ready-for-v1.8.0-prebeta"
V18_PREBETA_READINESS_PENDING = "v1.8.0-prebeta-readiness-pending"
V18_PREBETA_READINESS_READY = "v1.8.0-prebeta-readiness-functional-ai-ready"
READINESS_GATE_BLOCKED = "readiness-gate-blocked"
READINESS_GATE_READY = "readiness-gate-ready"
CONSENT_GATE_REQUIRED = "consent-gate-required"
CONSENT_GATE_READY = "consent-gate-ready"
CAPABILITY_GATE_BLOCKED = "capability-gate-blocked"
CAPABILITY_GATE_READY = "capability-gate-ready"
MANIFEST_GATE_BLOCKED = "manifest-gate-blocked"
MANIFEST_GATE_READY = "manifest-gate-ready"
ADAPTER_GATE_NULL_LOCAL = "adapter-gate-null-local"
ADAPTER_GATE_READY_FUTURE_GATED = "adapter-gate-ready-future-gated"
SAFETY_EVAL_GATE_PENDING = "safety-eval-gate-pending"
SAFETY_EVAL_GATE_READY = "safety-eval-gate-ready"
VOICE_CORE_SYNC_GATE_PENDING_APPROVAL = "voice-core-sync-gate-pending-user-approval"
VERSION_JUMP_GATE_PENDING_FUNCTIONAL_AI = "v1.8.0-prebeta-gate-pending-functional-ai"
PROVIDER_EXECUTION_READINESS_STATE_SCHEMA_VERSION = "provider-execution-readiness-state.v1"
PROVIDER_EXECUTION_READINESS_CONFIG_SCHEMA_VERSION = "provider-execution-readiness-config.v1"
PROVIDER_EXECUTION_READINESS_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-execution-migration"
PROVIDER_EXECUTION_READINESS_STATE_UNKNOWN = "execution_readiness_unknown"
PROVIDER_EXECUTION_READINESS_STATE_UNAVAILABLE = "execution_unavailable"
PROVIDER_EXECUTION_READINESS_STATE_DISABLED = "execution_disabled"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ACTIVATION = "execution_blocked_by_activation"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROVIDER_PATH = "execution_blocked_by_provider_path"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ADAPTER = "execution_blocked_by_adapter"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROMPT_GATE = "execution_blocked_by_prompt_gate"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_MODEL_GATE = "execution_blocked_by_model_gate"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_CONSENT = "execution_blocked_by_consent"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_SAFETY = "execution_blocked_by_safety"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_NETWORK = "execution_blocked_by_network"
PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_POLICY = "execution_blocked_by_policy"
PROVIDER_EXECUTION_READINESS_STATE_READY_FUTURE_GATED = "execution_ready_future_gated"
PROVIDER_EXECUTION_READINESS_STATE_READY_BUT_NOT_APPROVED = "execution_ready_but_not_approved"
PROVIDER_EXECUTION_READINESS_STATE_DEGRADED = "execution_degraded"
PROVIDER_EXECUTION_READINESS_STATE_FUNCTIONAL_AI_READY_FUTURE_VERSION = (
    "functional_ai_execution_ready_future_version"
)
PROVIDER_EXECUTION_ELIGIBILITY_UNAVAILABLE = "execution_eligibility_unavailable"
PROVIDER_EXECUTION_ELIGIBILITY_DISABLED = "execution_eligibility_disabled"
PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED = "execution_eligibility_blocked"
PROVIDER_EXECUTION_ELIGIBILITY_FUTURE_GATED = "execution_eligibility_future_gated"
PROVIDER_EXECUTION_ELIGIBILITY_READY_NOT_APPROVED = "execution_eligibility_ready_not_approved"
PROVIDER_EXECUTION_ELIGIBILITY_FUTURE_VERSION = "execution_eligibility_future_version"
PROVIDER_EXECUTION_BLOCKER_NONE = "none"
PROVIDER_EXECUTION_BLOCKER_ACTIVATION_REQUIRED = "activation_required"
PROVIDER_EXECUTION_BLOCKER_PROVIDER_PATH_REQUIRED = "provider_path_required"
PROVIDER_EXECUTION_BLOCKER_ADAPTER_REQUIRED = "adapter_required"
PROVIDER_EXECUTION_BLOCKER_PROMPT_GATE = "prompt_gate"
PROVIDER_EXECUTION_BLOCKER_MODEL_GATE = "model_gate"
PROVIDER_EXECUTION_BLOCKER_CONSENT_REQUIRED = "consent_required"
PROVIDER_EXECUTION_BLOCKER_SAFETY_EVAL_REQUIRED = "safety_eval_required"
PROVIDER_EXECUTION_BLOCKER_NETWORK_APPROVAL_REQUIRED = "network_approval_required"
PROVIDER_EXECUTION_BLOCKER_POLICY_BLOCKED = "policy_blocked"
PROVIDER_EXECUTION_BLOCKER_CONFIG_INVALID = "execution_config_invalid"
PROVIDER_EXECUTION_BLOCKER_FUTURE_EXECUTION_GATE = "future_execution_gate"
PROVIDER_EXECUTION_BLOCKER_APPROVAL_REQUIRED = "execution_approval_required"
PROVIDER_EXECUTION_BLOCKER_VERSION_JUMP_REQUIRED = "version_jump_required"
PROVIDER_EXECUTION_REASON_DEFAULT_UNAVAILABLE = "execution_default_unavailable"
PROVIDER_EXECUTION_REASON_CONFIG_MISSING_FAIL_CLOSED = "execution_config_missing_fail_closed"
PROVIDER_EXECUTION_REASON_CONFIG_INVALID_FAIL_CLOSED = "execution_config_invalid_fail_closed"
PROVIDER_EXECUTION_REASON_ACTIVATION_BLOCKED = "execution_activation_blocked"
PROVIDER_EXECUTION_REASON_PROVIDER_PATH_MISSING = "execution_provider_path_missing"
PROVIDER_EXECUTION_REASON_ADAPTER_UNAVAILABLE = "execution_adapter_unavailable"
PROVIDER_EXECUTION_REASON_PROMPT_GATE_BLOCKED = "execution_prompt_gate_blocked"
PROVIDER_EXECUTION_REASON_MODEL_GATE_BLOCKED = "execution_model_gate_blocked"
PROVIDER_EXECUTION_REASON_CONSENT_REQUIRED = "execution_consent_required"
PROVIDER_EXECUTION_REASON_SAFETY_EVAL_REQUIRED = "execution_safety_eval_required"
PROVIDER_EXECUTION_REASON_NETWORK_BLOCKED = "execution_network_blocked"
PROVIDER_EXECUTION_REASON_POLICY_BLOCKED = "execution_policy_blocked"
PROVIDER_EXECUTION_REASON_FUTURE_GATED = "execution_future_gated"
PROVIDER_EXECUTION_REASON_APPROVAL_MISSING = "execution_approval_missing"
PROVIDER_EXECUTION_REASON_FUNCTIONAL_AI_FUTURE_VERSION = "execution_functional_ai_future_version"
PROVIDER_EXECUTION_PROVENANCE_DEFAULT_CONFIG = "default_config"
PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG = "local_config"
PROVIDER_EXECUTION_PROVENANCE_ACTIVATION_STATE = "activation_state"
PROVIDER_EXECUTION_PROVENANCE_PROVIDER_PATH_CONTRACT = "provider_path_contract"
PROVIDER_EXECUTION_PROVENANCE_ADAPTER_CONTRACT = "adapter_contract"
PROVIDER_EXECUTION_PROVENANCE_PROMPT_GATE = "prompt_gate"
PROVIDER_EXECUTION_PROVENANCE_MODEL_GATE = "model_gate"
PROVIDER_EXECUTION_PROVENANCE_CONSENT_STATE = "consent_state"
PROVIDER_EXECUTION_PROVENANCE_SAFETY_EVAL = "safety_eval"
PROVIDER_EXECUTION_PROVENANCE_NETWORK_POLICY = "network_policy"
PROVIDER_EXECUTION_PROVENANCE_VALIDATOR_FIXTURE = "validator_fixture"
PROVIDER_EXECUTION_PROVENANCE_FUTURE_RUNTIME_CHECK = "future_runtime_check"
PROVIDER_EXECUTION_PROVENANCE_RELEASE_SOURCE_TRUTH = "release_source_truth"
PROVIDER_EXECUTION_CONFIG_STATE_DEFAULT = "default_config"
PROVIDER_EXECUTION_CONFIG_STATE_MISSING = "missing_config"
PROVIDER_EXECUTION_CONFIG_STATE_INVALID = "invalid_config"
PROVIDER_EXECUTION_CONFIG_STATE_LOCAL = "local_config"
PROVIDER_EXECUTION_APPROVAL_STATUS_MISSING = "execution-approval-missing"
PROVIDER_EXECUTION_APPROVAL_STATUS_FUTURE_GATED = "execution-approval-future-gated"
PROVIDER_EXECUTION_APPROVAL_STATUS_GRANTED_FOR_PROOF = "execution-approval-granted-for-proof"
PROVIDER_PATH_STATUS_NOT_SELECTED = "provider-path-not-selected"
PROVIDER_PATH_STATUS_SELECTED_FUTURE_GATED = "provider-path-selected-future-gated"
PROVIDER_SELECTION_POSTURE_PENDING_APPROVAL = "provider-selection-pending-user-approval"
PROVIDER_SELECTION_POSTURE_SELECTED_FUTURE_GATED = "provider-selection-selected-future-gated"
ADAPTER_SELECTION_POSTURE_NULL_LOCAL = "adapter-selection-null-local"
ADAPTER_SELECTION_POSTURE_READY_FUTURE_GATED = "adapter-selection-ready-future-gated"
PROMPT_ACCEPTANCE_GATE_DISABLED = "prompt-acceptance-disabled"
PROMPT_ACCEPTANCE_GATE_FUTURE_GATED = "prompt-acceptance-future-gated"
PROMPT_ROUTING_GATE_DISABLED = "prompt-routing-disabled"
PROMPT_ROUTING_GATE_FUTURE_GATED = "prompt-routing-future-gated"
PROMPT_SEND_POSTURE_DISABLED = "prompt-send-disabled"
LOCAL_ACTION_RESULT_SCHEMA_VERSION = "local-action-result.v1"
LOCAL_ACTION_RESULT_IDLE = "local-action-idle"
LOCAL_ACTION_RESULT_DETERMINISTIC_NO_PROVIDER = "deterministic-no-provider-result"
LOCAL_ACTION_RESULT_BLOCKED_BOUNDARY_MISMATCH = "blocked-boundary-mismatch"
AI_CONTROL_CENTER_DIAGNOSTICS_SCHEMA_VERSION = "ai-control-center-diagnostics.v1"
AI_CONTROL_CENTER_DIAGNOSTIC_NO_PROVIDER_FAIL_CLOSED = "no-provider-fail-closed"
AI_CONTROL_CENTER_DIAGNOSTIC_PROVIDER_UNAVAILABLE = "provider-unavailable"
AI_CONTROL_CENTER_DIAGNOSTIC_STALE_STATE = "stale-state-fail-closed"
AI_CONTROL_CENTER_DIAGNOSTIC_FAILED_CHECK = "failed-check-fail-closed"
AI_CONTROL_CENTER_DIAGNOSTIC_RETRY_LOCAL_ONLY = "retry-local-check-only"
AI_CONTROL_CENTER_DIAGNOSTIC_RECOVERY_LOCAL_ONLY = "recovery-local-only"
AI_CONTROL_CENTER_DIAGNOSTIC_BLOCKED_ACTION = "blocked-action"
AI_CONTROL_CENTER_DIAGNOSTIC_UNAVAILABLE_CAPABILITY = "unavailable-capability"
AI_CONTROL_CENTER_DIAGNOSTIC_DEGRADED_NO_PROVIDER = "degraded-no-provider"
MODEL_EXECUTION_STATUS_DISABLED = "model-execution-disabled"
MODEL_EXECUTION_STATUS_FUTURE_GATED = "model-execution-future-gated"
MODEL_WORKLOAD_READINESS_DISABLED = "model-workload-readiness-disabled"
MODEL_WORKLOAD_READINESS_FUTURE_GATED = "model-workload-readiness-future-gated"
PROVIDER_VISIBLE_DATA_EXECUTION_NONE = "provider-visible-data-execution-none"
PROVIDER_VISIBLE_DATA_EXECUTION_FUTURE_GATED = "provider-visible-data-execution-future-gated"
EXTERNAL_CALL_READINESS_BLOCKED = "external-calls-blocked"
EXTERNAL_CALL_READINESS_FUTURE_GATED = "external-calls-future-gated"
SAFETY_EVAL_READINESS_PENDING = "safety-eval-readiness-pending"
SAFETY_EVAL_READINESS_READY = "safety-eval-readiness-ready"
DATA_CLASSIFICATION_GATE_LOCAL_ONLY = "data-classification-gate-local-only"
EXECUTION_PROOF_MARKER_PENDING = "execution-proof-pending"
EXECUTION_PROOF_MARKER_READY_FUTURE_GATED = "execution-proof-ready-future-gated"
FUTURE_EXECUTION_VALIDATION_MARKER = "future-execution-validation-marker"
FUNCTIONAL_AI_RELEASE_GATE_PENDING = "functional-ai-release-gate-pending"
FUNCTIONAL_AI_RELEASE_GATE_READY_FUTURE_VERSION = "functional-ai-release-gate-ready-future-version"
V18_RELEASE_GATE_PENDING_FUNCTIONAL_AI = "v1.8.0-prebeta-release-gate-pending-functional-ai"
V18_RELEASE_GATE_READY_FUTURE_VERSION = "v1.8.0-prebeta-release-gate-ready-future-version"
PROVIDER_PATH_READINESS_STATE_SCHEMA_VERSION = "provider-path-readiness-state.v1"
PROVIDER_PATH_READINESS_CONFIG_SCHEMA_VERSION = "provider-path-readiness-config.v1"
PROVIDER_PATH_READINESS_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-provider-path-migration"
PROVIDER_PATH_READINESS_STATE_UNKNOWN = "provider_path_unknown"
PROVIDER_PATH_READINESS_STATE_UNAVAILABLE = "provider_path_unavailable"
PROVIDER_PATH_READINESS_STATE_DISABLED = "provider_path_disabled"
PROVIDER_PATH_READINESS_STATE_UNSELECTED = "provider_path_unselected"
PROVIDER_PATH_READINESS_STATE_SELECTION_REQUIRED = "provider_path_selection_required"
PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_POLICY = "provider_path_blocked_by_policy"
PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CONSENT = "provider_path_blocked_by_consent"
PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CAPABILITY = "provider_path_blocked_by_capability"
PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_MANIFEST = "provider_path_blocked_by_manifest"
PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_SAFETY = "provider_path_blocked_by_safety"
PROVIDER_PATH_READINESS_STATE_READY_FUTURE_GATED = "provider_path_ready_future_gated"
PROVIDER_PATH_READINESS_STATE_READY_BUT_NOT_APPROVED = "provider_path_ready_but_not_approved"
PROVIDER_PATH_READINESS_STATE_DEGRADED = "provider_path_degraded"
PROVIDER_PATH_READINESS_STATE_READY_FOR_FUTURE_EXECUTION_BRANCH = (
    "provider_path_ready_for_future_execution_branch"
)
PROVIDER_PATH_ELIGIBILITY_UNAVAILABLE = "provider_path_eligibility_unavailable"
PROVIDER_PATH_ELIGIBILITY_DISABLED = "provider_path_eligibility_disabled"
PROVIDER_PATH_ELIGIBILITY_BLOCKED = "provider_path_eligibility_blocked"
PROVIDER_PATH_ELIGIBILITY_SELECTION_REQUIRED = "provider_path_eligibility_selection_required"
PROVIDER_PATH_ELIGIBILITY_FUTURE_GATED = "provider_path_eligibility_future_gated"
PROVIDER_PATH_ELIGIBILITY_READY_NOT_APPROVED = "provider_path_eligibility_ready_not_approved"
PROVIDER_PATH_ELIGIBILITY_FUTURE_EXECUTION_BRANCH = "provider_path_eligibility_future_execution_branch"
PROVIDER_PATH_BLOCKER_NONE = "none"
PROVIDER_PATH_BLOCKER_EXECUTION_READINESS_REQUIRED = "execution_readiness_required"
PROVIDER_PATH_BLOCKER_SELECTION_REQUIRED = "provider_selection_required"
PROVIDER_PATH_BLOCKER_CONFIG_REQUIRED = "provider_config_required"
PROVIDER_PATH_BLOCKER_CONFIG_INVALID = "provider_config_invalid"
PROVIDER_PATH_BLOCKER_SETUP_CONSENT_REQUIRED = "setup_consent_required"
PROVIDER_PATH_BLOCKER_EXECUTION_CONSENT_REQUIRED = "execution_consent_required"
PROVIDER_PATH_BLOCKER_DATA_VISIBILITY_REQUIRED = "provider_visible_data_required"
PROVIDER_PATH_BLOCKER_CAPABILITY_REQUIRED = "capability_required"
PROVIDER_PATH_BLOCKER_MANIFEST_REQUIRED = "manifest_required"
PROVIDER_PATH_BLOCKER_SAFETY_EVAL_REQUIRED = "safety_eval_required"
PROVIDER_PATH_BLOCKER_POLICY_BLOCKED = "policy_blocked"
PROVIDER_PATH_BLOCKER_SETUP_APPROVAL_REQUIRED = "setup_approval_required"
PROVIDER_PATH_BLOCKER_EXECUTION_APPROVAL_REQUIRED = "execution_approval_required"
PROVIDER_PATH_BLOCKER_VERSION_JUMP_REQUIRED = "version_jump_required"
PROVIDER_PATH_REASON_DEFAULT_UNAVAILABLE = "provider_path_default_unavailable"
PROVIDER_PATH_REASON_CONFIG_MISSING_FAIL_CLOSED = "provider_path_config_missing_fail_closed"
PROVIDER_PATH_REASON_CONFIG_INVALID_FAIL_CLOSED = "provider_path_config_invalid_fail_closed"
PROVIDER_PATH_REASON_EXECUTION_READINESS_UNAVAILABLE = "provider_path_execution_readiness_unavailable"
PROVIDER_PATH_REASON_UNSELECTED = "provider_path_unselected"
PROVIDER_PATH_REASON_CONFIG_MISSING = "provider_path_config_missing"
PROVIDER_PATH_REASON_CONFIG_INVALID = "provider_path_config_invalid"
PROVIDER_PATH_REASON_SETUP_CONSENT_REQUIRED = "provider_path_setup_consent_required"
PROVIDER_PATH_REASON_EXECUTION_CONSENT_REQUIRED = "provider_path_execution_consent_required"
PROVIDER_PATH_REASON_DATA_VISIBILITY_BLOCKED = "provider_path_data_visibility_blocked"
PROVIDER_PATH_REASON_CAPABILITY_MISSING = "provider_path_capability_missing"
PROVIDER_PATH_REASON_MANIFEST_MISSING = "provider_path_manifest_missing"
PROVIDER_PATH_REASON_SAFETY_BLOCKED = "provider_path_safety_blocked"
PROVIDER_PATH_REASON_POLICY_BLOCKED = "provider_path_policy_blocked"
PROVIDER_PATH_REASON_SETUP_APPROVAL_MISSING = "provider_path_setup_approval_missing"
PROVIDER_PATH_REASON_EXECUTION_APPROVAL_MISSING = "provider_path_execution_approval_missing"
PROVIDER_PATH_REASON_READY_FOR_FUTURE_EXECUTION_BRANCH = "provider_path_ready_for_future_execution_branch"
PROVIDER_PATH_REASON_FUNCTIONAL_AI_FUTURE_VERSION = "provider_path_functional_ai_future_version"
PROVIDER_PATH_PROVENANCE_DEFAULT_CONFIG = "default_config"
PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG = "local_config"
PROVIDER_PATH_PROVENANCE_EXECUTION_READINESS_STATE = "execution_readiness_state"
PROVIDER_PATH_PROVENANCE_PROVIDER_SELECTION_CONTRACT = "provider_selection_contract"
PROVIDER_PATH_PROVENANCE_PROVIDER_CONFIG_CONTRACT = "provider_config_contract"
PROVIDER_PATH_PROVENANCE_CONSENT_STATE = "consent_state"
PROVIDER_PATH_PROVENANCE_DATA_VISIBILITY_CONTRACT = "data_visibility_contract"
PROVIDER_PATH_PROVENANCE_CAPABILITY_CONTRACT = "capability_contract"
PROVIDER_PATH_PROVENANCE_MANIFEST_STATE = "manifest_state"
PROVIDER_PATH_PROVENANCE_SAFETY_EVAL = "safety_eval"
PROVIDER_PATH_PROVENANCE_AUDIT_POLICY = "audit_policy"
PROVIDER_PATH_PROVENANCE_FUTURE_RUNTIME_CHECK = "future_runtime_check"
PROVIDER_PATH_PROVENANCE_VALIDATOR_FIXTURE = "validator_fixture"
PROVIDER_PATH_CONFIG_STATE_DEFAULT = "default_config"
PROVIDER_PATH_CONFIG_STATE_MISSING = "missing_config"
PROVIDER_PATH_CONFIG_STATE_INVALID = "invalid_config"
PROVIDER_PATH_CONFIG_STATE_LOCAL = "local_config"
PROVIDER_PATH_APPROVAL_STATUS_MISSING = "provider-path-approval-missing"
PROVIDER_PATH_APPROVAL_STATUS_FUTURE_GATED = "provider-path-approval-future-gated"
PROVIDER_PATH_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF = "provider-path-approval-ready-for-future-proof"
PROVIDER_CONFIG_ENVELOPE_STATUS_MISSING = "provider-config-missing"
PROVIDER_CONFIG_ENVELOPE_STATUS_INVALID = "provider-config-invalid"
PROVIDER_CONFIG_ENVELOPE_STATUS_LOCAL_ONLY_READY = "provider-config-local-only-ready"
PROVIDER_PROFILE_METADATA_CONTRACT_VERSION = "provider-profile-metadata.v1"
PROVIDER_PROFILE_ID_LOCAL_NULL = "local-null-provider-profile"
PROVIDER_PROFILE_KIND_NULL_LOCAL = "null-local-provider"
PROVIDER_PROFILE_SOURCE_LOCAL_SCAFFOLD = "local-readiness-scaffold"
PROVIDER_SDK_REQUIREMENT_PENDING_APPROVAL = "sdk-integration-pending-user-approval"
PROVIDER_NETWORK_REQUIREMENT_BLOCKED = "network-requirement-blocked"
PROVIDER_AVAILABILITY_UNAVAILABLE = "provider-availability-unavailable"
PROVIDER_AVAILABILITY_READY_FUTURE_GATED = "provider-availability-ready-future-gated"
PROVIDER_SETUP_APPROVAL_STATUS_MISSING = "provider-setup-approval-missing"
PROVIDER_SETUP_APPROVAL_STATUS_FUTURE_GATED = "provider-setup-approval-future-gated"
PROVIDER_EXECUTION_APPROVAL_STATUS_PROVIDER_PATH_MISSING = "provider-execution-approval-missing"
LOCAL_NULL_PROVIDER_FALLBACK_ACTIVE = "local-null-provider-fallback-active"
FUTURE_SDK_HANDOFF_MARKER = "future-sdk-handoff-marker"
FUTURE_PROVIDER_SETUP_HANDOFF_MARKER = "future-provider-setup-handoff-marker"
CONSENT_READINESS_STATE_SCHEMA_VERSION = "provider-consent-readiness-state.v1"
CONSENT_READINESS_CONFIG_SCHEMA_VERSION = "provider-consent-readiness-config.v1"
CONSENT_READINESS_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-consent-collection-migration"
CONSENT_READINESS_STATE_UNKNOWN = "consent_unknown"
CONSENT_READINESS_STATE_UNAVAILABLE = "consent_unavailable"
CONSENT_READINESS_STATE_DISABLED = "consent_disabled"
CONSENT_READINESS_STATE_NOT_REQUIRED_FOR_LOCAL_STATUS = "consent_not_required_for_local_status"
CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_SETUP = "consent_required_for_provider_setup"
CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_EXECUTION = "consent_required_for_provider_execution"
CONSENT_READINESS_STATE_BLOCKED_BY_POLICY = "consent_blocked_by_policy"
CONSENT_READINESS_STATE_BLOCKED_BY_DATA_VISIBILITY = "consent_blocked_by_data_visibility"
CONSENT_READINESS_STATE_BLOCKED_BY_AUDIT_REQUIREMENTS = "consent_blocked_by_audit_requirements"
CONSENT_READINESS_STATE_READY_FUTURE_GATED = "consent_ready_future_gated"
CONSENT_READINESS_STATE_READY_BUT_NOT_COLLECTED = "consent_ready_but_not_collected"
CONSENT_READINESS_STATE_DEGRADED = "consent_degraded"
CONSENT_BLOCKER_NONE = "none"
CONSENT_BLOCKER_SETUP_REQUIRED = "setup_consent_required"
CONSENT_BLOCKER_EXECUTION_REQUIRED = "execution_consent_required"
CONSENT_BLOCKER_POLICY = "consent_policy_blocked"
CONSENT_BLOCKER_DATA_VISIBILITY = "data_visibility_blocked"
CONSENT_BLOCKER_AUDIT_REQUIREMENTS = "audit_requirements_blocked"
CONSENT_BLOCKER_COLLECTION_NOT_APPROVED = "consent_collection_not_approved"
CONSENT_REASON_SETUP_REQUIRED = "consent_setup_required"
CONSENT_REASON_EXECUTION_REQUIRED = "consent_execution_required"
CONSENT_REASON_POLICY_BLOCKED = "consent_policy_blocked"
CONSENT_REASON_DATA_VISIBILITY_BLOCKED = "consent_data_visibility_blocked"
CONSENT_REASON_AUDIT_REQUIREMENTS_BLOCKED = "consent_audit_requirements_blocked"
CONSENT_REASON_READY_BUT_NOT_COLLECTED = "consent_ready_but_not_collected"
CONSENT_PROVENANCE_DEFAULT_CONFIG = "default_config"
CONSENT_PROVENANCE_PROVIDER_PATH_CONTRACT = "provider_path_contract"
CONSENT_PROVENANCE_DATA_VISIBILITY_CONTRACT = "data_visibility_contract"
CONSENT_PROVENANCE_AUDIT_POLICY = "audit_policy"
CONSENT_PROVENANCE_FUTURE_COLLECTION = "future_consent_collection"
SETUP_CONSENT_HANDOFF_FUTURE_GATED = "setup-consent-handoff-future-gated"
EXECUTION_CONSENT_HANDOFF_FUTURE_GATED = "execution-consent-handoff-future-gated"
PROVIDER_VISIBLE_DATA_REQUIREMENT_NONE = "provider-visible-data-requirement-none"
PROVIDER_VISIBLE_DATA_REQUIREMENT_BLOCKED = "provider-visible-data-requirement-blocked"
DATA_CLASSIFICATION_POSTURE_LOCAL_ONLY = "data-classification-posture-local-only"
AUDIT_ENVELOPE_POSTURE_PLANNED = "audit-envelope-posture-planned"
LOCAL_ONLY_STATUS_POSTURE_ACTIVE = "local-only-status-posture-active"
PROVIDER_SETUP_FUTURE_GATED_POSTURE = "provider-setup-future-gated"
PROVIDER_EXECUTION_FUTURE_GATED_POSTURE = "provider-execution-future-gated"
PROVIDER_PATH_GATE_BLOCKED = "provider-path-gate-blocked"
PROVIDER_PATH_GATE_FUTURE_GATED = "provider-path-gate-future-gated"
PROVIDER_CONFIG_GATE_BLOCKED = "provider-config-gate-blocked"
PROVIDER_CONFIG_GATE_READY_FUTURE_GATED = "provider-config-gate-ready-future-gated"
SETUP_CONSENT_GATE_REQUIRED = "setup-consent-gate-required"
SETUP_CONSENT_GATE_READY_FUTURE_GATED = "setup-consent-gate-ready-future-gated"
EXECUTION_CONSENT_GATE_REQUIRED = "execution-consent-gate-required"
EXECUTION_CONSENT_GATE_READY_FUTURE_GATED = "execution-consent-gate-ready-future-gated"
PROVIDER_VISIBLE_DATA_GATE_NONE = "provider-visible-data-gate-none"
PROVIDER_VISIBLE_DATA_GATE_BLOCKED = "provider-visible-data-gate-blocked"
AUDIT_GATE_PLANNED = "audit-gate-planned"
AUDIT_GATE_READY_FUTURE_GATED = "audit-gate-ready-future-gated"

SETUP_FLOW_READINESS_STATE_SCHEMA_VERSION = "provider-setup-flow-readiness-state.v1"
SETUP_FLOW_READINESS_CONFIG_SCHEMA_VERSION = "provider-setup-flow-readiness-config.v1"
SETUP_FLOW_READINESS_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-setup-flow-migration"
SETUP_FLOW_STATE_UNKNOWN = "setup_flow_unknown"
SETUP_FLOW_STATE_UNAVAILABLE = "setup_flow_unavailable"
SETUP_FLOW_STATE_DISABLED = "setup_flow_disabled"
SETUP_FLOW_STATE_BLOCKED_BY_PROVIDER_PATH = "setup_flow_blocked_by_provider_path"
SETUP_FLOW_STATE_BLOCKED_BY_SETUP_CONSENT = "setup_flow_blocked_by_setup_consent"
SETUP_FLOW_STATE_BLOCKED_BY_EXECUTION_CONSENT = "setup_flow_blocked_by_execution_consent"
SETUP_FLOW_STATE_BLOCKED_BY_POLICY = "setup_flow_blocked_by_policy"
SETUP_FLOW_STATE_BLOCKED_BY_CAPABILITY = "setup_flow_blocked_by_capability"
SETUP_FLOW_STATE_BLOCKED_BY_MANIFEST = "setup_flow_blocked_by_manifest"
SETUP_FLOW_STATE_BLOCKED_BY_SAFETY = "setup_flow_blocked_by_safety"
SETUP_FLOW_STATE_READY_FUTURE_GATED = "setup_flow_ready_future_gated"
SETUP_FLOW_STATE_READY_BUT_NOT_APPROVED = "setup_flow_ready_but_not_approved"
SETUP_FLOW_STATE_DEGRADED = "setup_flow_degraded"
SETUP_FLOW_STATE_READY_FOR_FUTURE_SETUP_BRANCH = "setup_flow_ready_for_future_setup_branch"
SETUP_FLOW_ELIGIBILITY_UNAVAILABLE = "setup_flow_eligibility_unavailable"
SETUP_FLOW_ELIGIBILITY_DISABLED = "setup_flow_eligibility_disabled"
SETUP_FLOW_ELIGIBILITY_BLOCKED = "setup_flow_eligibility_blocked"
SETUP_FLOW_ELIGIBILITY_FUTURE_GATED = "setup_flow_eligibility_future_gated"
SETUP_FLOW_ELIGIBILITY_READY_NOT_APPROVED = "setup_flow_eligibility_ready_not_approved"
SETUP_FLOW_ELIGIBILITY_FUTURE_SETUP_BRANCH = "setup_flow_eligibility_future_setup_branch"
SETUP_FLOW_BLOCKER_PROVIDER_PATH_REQUIRED = "provider_path_required"
SETUP_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED = "setup_consent_required"
SETUP_FLOW_BLOCKER_EXECUTION_CONSENT_REQUIRED = "execution_consent_required"
SETUP_FLOW_BLOCKER_POLICY_BLOCKED = "policy_blocked"
SETUP_FLOW_BLOCKER_CAPABILITY_REQUIRED = "capability_required"
SETUP_FLOW_BLOCKER_MANIFEST_REQUIRED = "manifest_required"
SETUP_FLOW_BLOCKER_SAFETY_EVAL_REQUIRED = "safety_eval_required"
SETUP_FLOW_BLOCKER_SETUP_APPROVAL_REQUIRED = "setup_approval_required"
SETUP_FLOW_BLOCKER_FUTURE_SETUP_BRANCH = "future_setup_branch_required"
SETUP_FLOW_REASON_DEFAULT_UNAVAILABLE = "setup_flow_default_unavailable"
SETUP_FLOW_REASON_PROVIDER_PATH_REQUIRED = "setup_flow_provider_path_required"
SETUP_FLOW_REASON_SETUP_CONSENT_REQUIRED = "setup_flow_setup_consent_required"
SETUP_FLOW_REASON_EXECUTION_CONSENT_REQUIRED = "setup_flow_execution_consent_required"
SETUP_FLOW_REASON_POLICY_BLOCKED = "setup_flow_policy_blocked"
SETUP_FLOW_REASON_CAPABILITY_MISSING = "setup_flow_capability_missing"
SETUP_FLOW_REASON_MANIFEST_MISSING = "setup_flow_manifest_missing"
SETUP_FLOW_REASON_SAFETY_BLOCKED = "setup_flow_safety_blocked"
SETUP_FLOW_REASON_SETUP_APPROVAL_MISSING = "setup_flow_setup_approval_missing"
SETUP_FLOW_REASON_READY_FOR_FUTURE_SETUP_BRANCH = "setup_flow_ready_for_future_setup_branch"
SETUP_FLOW_PROVENANCE_PROVIDER_PATH = "provider_path_readiness_state"
SETUP_FLOW_PROVENANCE_CONSENT = "consent_flow_state"
SETUP_FLOW_PROVENANCE_CAPABILITY = "capability_contract"
SETUP_FLOW_PROVENANCE_MANIFEST = "manifest_state"
SETUP_FLOW_PROVENANCE_SAFETY = "safety_eval"
SETUP_FLOW_PROVENANCE_POLICY = "audit_policy"
SETUP_FLOW_PROVENANCE_FUTURE_RUNTIME = "future_runtime_check"
SETUP_FLOW_APPROVAL_STATUS_MISSING = "setup-flow-approval-missing"
SETUP_FLOW_APPROVAL_STATUS_FUTURE_GATED = "setup-flow-approval-future-gated"
SETUP_FLOW_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF = "setup-flow-approval-ready-for-future-proof"

CONSENT_FLOW_READINESS_STATE_SCHEMA_VERSION = "provider-consent-flow-readiness-state.v1"
CONSENT_FLOW_READINESS_CONFIG_SCHEMA_VERSION = "provider-consent-flow-readiness-config.v1"
CONSENT_FLOW_READINESS_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-consent-flow-migration"
CONSENT_FLOW_STATE_UNKNOWN = "consent_flow_unknown"
CONSENT_FLOW_STATE_UNAVAILABLE = "consent_flow_unavailable"
CONSENT_FLOW_STATE_DISABLED = "consent_flow_disabled"
CONSENT_FLOW_STATE_BLOCKED_BY_POLICY = "consent_flow_blocked_by_policy"
CONSENT_FLOW_STATE_BLOCKED_BY_DATA_VISIBILITY = "consent_flow_blocked_by_data_visibility"
CONSENT_FLOW_STATE_BLOCKED_BY_AUDIT_REQUIREMENTS = "consent_flow_blocked_by_audit_requirements"
CONSENT_FLOW_STATE_REQUIRED_FOR_SETUP = "consent_flow_required_for_setup"
CONSENT_FLOW_STATE_REQUIRED_FOR_EXECUTION = "consent_flow_required_for_execution"
CONSENT_FLOW_STATE_READY_FUTURE_GATED = "consent_flow_ready_future_gated"
CONSENT_FLOW_STATE_READY_BUT_NOT_COLLECTED = "consent_flow_ready_but_not_collected"
CONSENT_FLOW_STATE_DEGRADED = "consent_flow_degraded"
CONSENT_FLOW_STATE_READY_FOR_FUTURE_CONSENT_BRANCH = "consent_flow_ready_for_future_consent_branch"
CONSENT_FLOW_ELIGIBILITY_UNAVAILABLE = "consent_flow_eligibility_unavailable"
CONSENT_FLOW_ELIGIBILITY_REQUIRED = "consent_flow_eligibility_required"
CONSENT_FLOW_ELIGIBILITY_BLOCKED = "consent_flow_eligibility_blocked"
CONSENT_FLOW_ELIGIBILITY_FUTURE_GATED = "consent_flow_eligibility_future_gated"
CONSENT_FLOW_ELIGIBILITY_READY_NOT_COLLECTED = "consent_flow_eligibility_ready_not_collected"
CONSENT_FLOW_ELIGIBILITY_FUTURE_CONSENT_BRANCH = "consent_flow_eligibility_future_consent_branch"
CONSENT_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED = "setup_consent_required"
CONSENT_FLOW_BLOCKER_EXECUTION_CONSENT_REQUIRED = "execution_consent_required"
CONSENT_FLOW_BLOCKER_POLICY_BLOCKED = "policy_blocked"
CONSENT_FLOW_BLOCKER_DATA_VISIBILITY_REQUIRED = "data_visibility_required"
CONSENT_FLOW_BLOCKER_AUDIT_REQUIRED = "audit_required"
CONSENT_FLOW_BLOCKER_COLLECTION_NOT_APPROVED = "consent_collection_not_approved"
CONSENT_FLOW_BLOCKER_FUTURE_CONSENT_BRANCH = "future_consent_branch_required"
CONSENT_FLOW_REASON_DEFAULT_UNAVAILABLE = "consent_flow_default_unavailable"
CONSENT_FLOW_REASON_SETUP_REQUIRED = "consent_flow_setup_required"
CONSENT_FLOW_REASON_EXECUTION_REQUIRED = "consent_flow_execution_required"
CONSENT_FLOW_REASON_POLICY_BLOCKED = "consent_flow_policy_blocked"
CONSENT_FLOW_REASON_DATA_VISIBILITY_BLOCKED = "consent_flow_data_visibility_blocked"
CONSENT_FLOW_REASON_AUDIT_REQUIREMENTS_BLOCKED = "consent_flow_audit_requirements_blocked"
CONSENT_FLOW_REASON_READY_BUT_NOT_COLLECTED = "consent_flow_ready_but_not_collected"
CONSENT_FLOW_REASON_READY_FOR_FUTURE_CONSENT_BRANCH = "consent_flow_ready_for_future_consent_branch"
CONSENT_FLOW_PROVENANCE_SETUP_CONSENT = "setup_consent_state"
CONSENT_FLOW_PROVENANCE_EXECUTION_CONSENT = "execution_consent_state"
CONSENT_FLOW_PROVENANCE_DATA_VISIBILITY = "data_visibility_contract"
CONSENT_FLOW_PROVENANCE_AUDIT = "audit_policy"
CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION = "future_consent_collection"
CONSENT_FLOW_APPROVAL_STATUS_MISSING = "consent-flow-approval-missing"
CONSENT_FLOW_APPROVAL_STATUS_FUTURE_GATED = "consent-flow-approval-future-gated"
CONSENT_FLOW_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF = "consent-flow-approval-ready-for-future-proof"
PROVIDER_SETUP_HANDOFF_FUTURE_GATED = "provider-setup-handoff-future-gated"
PROVIDER_CONSENT_HANDOFF_FUTURE_GATED = "provider-consent-handoff-future-gated"
PROVIDER_PATH_HANDOFF_FUTURE_GATED = "provider-path-handoff-future-gated"
CONSENT_COLLECTION_POSTURE_PENDING_APPROVAL = "consent-collection-pending-user-approval"
DATA_VISIBILITY_CONSENT_POSTURE_NONE_REQUIRED = "data-visibility-consent-none-required"
SETUP_FLOW_GATE_BLOCKED = "setup-flow-gate-blocked"
SETUP_FLOW_GATE_FUTURE_GATED = "setup-flow-gate-future-gated"
CONSENT_FLOW_GATE_REQUIRED = "consent-flow-gate-required"
CONSENT_FLOW_GATE_FUTURE_GATED = "consent-flow-gate-future-gated"
SETUP_APPROVAL_GATE_MISSING = "setup-approval-gate-missing"
SETUP_APPROVAL_GATE_FUTURE_GATED = "setup-approval-gate-future-gated"
EXECUTION_APPROVAL_GATE_MISSING = "execution-approval-gate-missing"
EXECUTION_APPROVAL_GATE_FUTURE_GATED = "execution-approval-gate-future-gated"
AI_PROVIDER_STATUS_DISPLAY_SUPPRESSED = "desktop-ai-owned-readiness-display-suppressed"
AI_PROVIDER_STATUS_DISPLAY_ABSENT_FROM_DEFAULT_DESKTOP = "desktop-ai-owned-readiness-display-absent-from-default-surface"
AI_PROVIDER_STATUS_DISPLAY_VISIBLE = "desktop-ai-owned-readiness-display-visible"

SETUP_CONTRACT_READINESS_STATE_SCHEMA_VERSION = "provider-setup-contract-readiness-state.v1"
SETUP_CONTRACT_READINESS_CONFIG_SCHEMA_VERSION = "provider-setup-contract-readiness-config.v1"
SETUP_CONTRACT_READINESS_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-provider-setup-contract-migration"
SETUP_CONTRACT_STATE_UNKNOWN = "setup_contract_unknown"
SETUP_CONTRACT_STATE_UNAVAILABLE = "setup_contract_unavailable"
SETUP_CONTRACT_STATE_DISABLED = "setup_contract_disabled"
SETUP_CONTRACT_STATE_BLOCKED_BY_PROVIDER_PATH = "setup_contract_blocked_by_provider_path"
SETUP_CONTRACT_STATE_BLOCKED_BY_CONFIG = "setup_contract_blocked_by_config"
SETUP_CONTRACT_STATE_BLOCKED_BY_SETUP_CONSENT = "setup_contract_blocked_by_setup_consent"
SETUP_CONTRACT_STATE_BLOCKED_BY_EXECUTION_CONSENT = "setup_contract_blocked_by_execution_consent"
SETUP_CONTRACT_STATE_BLOCKED_BY_POLICY = "setup_contract_blocked_by_policy"
SETUP_CONTRACT_STATE_BLOCKED_BY_CAPABILITY = "setup_contract_blocked_by_capability"
SETUP_CONTRACT_STATE_BLOCKED_BY_MANIFEST = "setup_contract_blocked_by_manifest"
SETUP_CONTRACT_STATE_BLOCKED_BY_SAFETY = "setup_contract_blocked_by_safety"
SETUP_CONTRACT_STATE_READY_FUTURE_GATED = "setup_contract_ready_future_gated"
SETUP_CONTRACT_STATE_READY_BUT_NOT_APPROVED = "setup_contract_ready_but_not_approved"
SETUP_CONTRACT_STATE_DEGRADED = "setup_contract_degraded"
SETUP_CONTRACT_STATE_READY_FOR_FUTURE_SETUP_BRANCH = "setup_contract_ready_for_future_setup_branch"
SETUP_CONTRACT_ELIGIBILITY_UNAVAILABLE = "setup_contract_eligibility_unavailable"
SETUP_CONTRACT_ELIGIBILITY_DISABLED = "setup_contract_eligibility_disabled"
SETUP_CONTRACT_ELIGIBILITY_BLOCKED = "setup_contract_eligibility_blocked"
SETUP_CONTRACT_ELIGIBILITY_FUTURE_GATED = "setup_contract_eligibility_future_gated"
SETUP_CONTRACT_ELIGIBILITY_READY_NOT_APPROVED = "setup_contract_eligibility_ready_not_approved"
SETUP_CONTRACT_ELIGIBILITY_FUTURE_SETUP_BRANCH = "setup_contract_eligibility_future_setup_branch"
SETUP_CONTRACT_BLOCKER_PROVIDER_PATH_REQUIRED = "setup_contract_provider_path_required"
SETUP_CONTRACT_BLOCKER_CONFIG_REQUIRED = "setup_contract_config_required"
SETUP_CONTRACT_BLOCKER_SETUP_CONSENT_REQUIRED = "setup_contract_setup_consent_required"
SETUP_CONTRACT_BLOCKER_EXECUTION_CONSENT_REQUIRED = "setup_contract_execution_consent_required"
SETUP_CONTRACT_BLOCKER_POLICY_BLOCKED = "setup_contract_policy_blocked"
SETUP_CONTRACT_BLOCKER_CAPABILITY_REQUIRED = "setup_contract_capability_required"
SETUP_CONTRACT_BLOCKER_MANIFEST_REQUIRED = "setup_contract_manifest_required"
SETUP_CONTRACT_BLOCKER_SAFETY_EVAL_REQUIRED = "setup_contract_safety_eval_required"
SETUP_CONTRACT_BLOCKER_SETUP_APPROVAL_REQUIRED = "setup_contract_setup_approval_required"
SETUP_CONTRACT_BLOCKER_FUTURE_SETUP_BRANCH = "setup_contract_future_setup_branch_required"
SETUP_CONTRACT_REASON_DEFAULT_UNAVAILABLE = "setup_contract_default_unavailable"
SETUP_CONTRACT_REASON_PROVIDER_PATH_REQUIRED = "setup_contract_provider_path_required"
SETUP_CONTRACT_REASON_CONFIG_MISSING = "setup_contract_config_missing"
SETUP_CONTRACT_REASON_CONFIG_INVALID = "setup_contract_config_invalid"
SETUP_CONTRACT_REASON_PROFILE_MISSING = "setup_contract_profile_missing"
SETUP_CONTRACT_REASON_SETUP_CONSENT_REQUIRED = "setup_contract_setup_consent_required"
SETUP_CONTRACT_REASON_EXECUTION_CONSENT_REQUIRED = "setup_contract_execution_consent_required"
SETUP_CONTRACT_REASON_POLICY_BLOCKED = "setup_contract_policy_blocked"
SETUP_CONTRACT_REASON_CAPABILITY_MISSING = "setup_contract_capability_missing"
SETUP_CONTRACT_REASON_MANIFEST_MISSING = "setup_contract_manifest_missing"
SETUP_CONTRACT_REASON_SAFETY_BLOCKED = "setup_contract_safety_blocked"
SETUP_CONTRACT_REASON_SETUP_APPROVAL_MISSING = "setup_contract_setup_approval_missing"
SETUP_CONTRACT_REASON_READY_FOR_FUTURE_SETUP_BRANCH = "setup_contract_ready_for_future_setup_branch"
SETUP_CONTRACT_PROVENANCE_SETUP_FLOW = "setup_flow_readiness_state"
SETUP_CONTRACT_PROVENANCE_PROVIDER_PATH = "provider_path_readiness_state"
SETUP_CONTRACT_PROVENANCE_CONFIG = "provider_config_envelope"
SETUP_CONTRACT_PROVENANCE_PROFILE = "provider_profile_metadata"
SETUP_CONTRACT_PROVENANCE_CONSENT = "provider_consent_prerequisites"
SETUP_CONTRACT_PROVENANCE_CAPABILITY = "capability_contract"
SETUP_CONTRACT_PROVENANCE_MANIFEST = "manifest_state"
SETUP_CONTRACT_PROVENANCE_SAFETY = "safety_eval"
SETUP_CONTRACT_PROVENANCE_POLICY = "audit_policy"
SETUP_CONTRACT_PROVENANCE_FUTURE_RUNTIME = "future_setup_contract_check"
SETUP_CONTRACT_APPROVAL_STATUS_MISSING = "setup-contract-approval-missing"
SETUP_CONTRACT_APPROVAL_STATUS_FUTURE_GATED = "setup-contract-approval-future-gated"
SETUP_CONTRACT_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF = "setup-contract-approval-ready-for-future-proof"
SETUP_CONTRACT_GATE_BLOCKED = "setup-contract-gate-blocked"
SETUP_CONTRACT_GATE_FUTURE_GATED = "setup-contract-gate-future-gated"
PROVIDER_PROFILE_GATE_BLOCKED = "provider-profile-gate-blocked"
PROVIDER_PROFILE_GATE_READY_FUTURE_GATED = "provider-profile-gate-ready-future-gated"
DATA_CLASSIFICATION_GATE_LOCAL_ONLY = "data-classification-gate-local-only"
CAPABILITY_GATE_BLOCKED = "capability-gate-blocked"
CAPABILITY_GATE_READY_FUTURE_GATED = "capability-gate-ready-future-gated"
MANIFEST_GATE_BLOCKED = "manifest-gate-blocked"
MANIFEST_GATE_READY_FUTURE_GATED = "manifest-gate-ready-future-gated"
SAFETY_EVAL_GATE_BLOCKED = "safety-eval-gate-blocked"
SAFETY_EVAL_GATE_READY_FUTURE_GATED = "safety-eval-gate-ready-future-gated"
NETWORK_GATE_BLOCKED = "network-gate-blocked"
MEMORY_INDEXING_GATE_BLOCKED = "memory-indexing-gate-blocked"
VOICE_CORE_SYNC_GATE_BLOCKED = "voice-core-sync-gate-blocked"
VERSION_JUMP_GATE_PENDING = "version-jump-gate-pending-functional-ai"
FUTURE_SETUP_BRANCH_HANDOFF_READY = "future-provider-setup-branch-handoff-ready-for-contract"
PROVIDER_SETUP_CONTRACT_FOLD_DOWN_READY = "setup-contract-fold-down-ready-for-pr-release"
PROVIDER_SETUP_PREREQUISITE_POSTURE_LOCAL_ONLY = "provider-setup-prerequisites-local-only"
PROVIDER_SETUP_VALIDATION_POSTURE_STATIC = "provider-setup-contract-static-validator-fixtures"
PROVIDER_SETUP_UI_PROOF_POSTURE_STATUS_ONLY = "provider-setup-contract-status-only-ui-proof"

SETUP_FOUNDATION_STATE_SCHEMA_VERSION = "provider-setup-implementation-foundation-state.v1"
SETUP_FOUNDATION_CONFIG_SCHEMA_VERSION = "provider-setup-implementation-foundation-config.v1"
SETUP_FOUNDATION_CONFIG_MIGRATION_POSTURE = "safe-defaults-no-provider-setup-foundation-migration"
SETUP_FOUNDATION_STATE_UNKNOWN = "setup_foundation_unknown"
SETUP_FOUNDATION_STATE_UNAVAILABLE = "setup_foundation_unavailable"
SETUP_FOUNDATION_STATE_DISABLED = "setup_foundation_disabled"
SETUP_FOUNDATION_STATE_BLOCKED_BY_SETUP_CONTRACT = "setup_foundation_blocked_by_setup_contract"
SETUP_FOUNDATION_STATE_BLOCKED_BY_PROFILE = "setup_foundation_blocked_by_profile"
SETUP_FOUNDATION_STATE_BLOCKED_BY_CONFIG = "setup_foundation_blocked_by_config"
SETUP_FOUNDATION_STATE_BLOCKED_BY_VALIDATION = "setup_foundation_blocked_by_validation"
SETUP_FOUNDATION_STATE_BLOCKED_BY_SETUP_CONSENT = "setup_foundation_blocked_by_setup_consent"
SETUP_FOUNDATION_STATE_BLOCKED_BY_EXECUTION_CONSENT = (
    "setup_foundation_blocked_by_execution_consent"
)
SETUP_FOUNDATION_STATE_READY_LOCAL_DRAFT = "setup_foundation_ready_local_draft"
SETUP_FOUNDATION_STATE_READY_FUTURE_GATED = "setup_foundation_ready_future_gated"
SETUP_FOUNDATION_STATE_READY_BUT_NOT_APPROVED = "setup_foundation_ready_but_not_approved"
SETUP_FOUNDATION_STATE_DEGRADED = "setup_foundation_degraded"
SETUP_FOUNDATION_STATE_READY_FOR_FUTURE_SETUP_BRANCH = (
    "setup_foundation_ready_for_future_setup_branch"
)
SETUP_FOUNDATION_ELIGIBILITY_UNAVAILABLE = "setup_foundation_eligibility_unavailable"
SETUP_FOUNDATION_ELIGIBILITY_DISABLED = "setup_foundation_eligibility_disabled"
SETUP_FOUNDATION_ELIGIBILITY_BLOCKED = "setup_foundation_eligibility_blocked"
SETUP_FOUNDATION_ELIGIBILITY_LOCAL_DRAFT = "setup_foundation_eligibility_local_draft"
SETUP_FOUNDATION_ELIGIBILITY_FUTURE_GATED = "setup_foundation_eligibility_future_gated"
SETUP_FOUNDATION_ELIGIBILITY_READY_NOT_APPROVED = (
    "setup_foundation_eligibility_ready_not_approved"
)
SETUP_FOUNDATION_ELIGIBILITY_FUTURE_SETUP_BRANCH = (
    "setup_foundation_eligibility_future_setup_branch"
)
SETUP_FOUNDATION_BLOCKER_SETUP_CONTRACT_REQUIRED = "setup_foundation_setup_contract_required"
SETUP_FOUNDATION_BLOCKER_PROFILE_DRAFT_REQUIRED = "setup_foundation_profile_draft_required"
SETUP_FOUNDATION_BLOCKER_CONFIG_DRAFT_REQUIRED = "setup_foundation_config_draft_required"
SETUP_FOUNDATION_BLOCKER_VALIDATION_REQUIRED = "setup_foundation_validation_required"
SETUP_FOUNDATION_BLOCKER_SETUP_CONSENT_REQUIRED = "setup_foundation_setup_consent_required"
SETUP_FOUNDATION_BLOCKER_EXECUTION_CONSENT_REQUIRED = (
    "setup_foundation_execution_consent_required"
)
SETUP_FOUNDATION_BLOCKER_APPROVAL_REQUIRED = "setup_foundation_approval_required"
SETUP_FOUNDATION_BLOCKER_FUTURE_SETUP_BRANCH = "setup_foundation_future_setup_branch_required"
SETUP_FOUNDATION_REASON_DEFAULT_UNAVAILABLE = "setup_foundation_default_unavailable"
SETUP_FOUNDATION_REASON_SETUP_ENTRY_DISABLED = "setup_foundation_setup_entry_disabled"
SETUP_FOUNDATION_REASON_SETUP_CONTRACT_REQUIRED = "setup_foundation_setup_contract_required"
SETUP_FOUNDATION_REASON_CONFIG_MISSING = "setup_foundation_config_missing"
SETUP_FOUNDATION_REASON_CONFIG_INVALID = "setup_foundation_config_invalid"
SETUP_FOUNDATION_REASON_PROFILE_DRAFT_MISSING = "setup_foundation_profile_draft_missing"
SETUP_FOUNDATION_REASON_PROFILE_DRAFT_INVALID = "setup_foundation_profile_draft_invalid"
SETUP_FOUNDATION_REASON_CONFIG_DRAFT_MISSING = "setup_foundation_config_draft_missing"
SETUP_FOUNDATION_REASON_CONFIG_DRAFT_INVALID = "setup_foundation_config_draft_invalid"
SETUP_FOUNDATION_REASON_VALIDATION_FAILED = "setup_foundation_validation_failed"
SETUP_FOUNDATION_REASON_SETUP_CONSENT_REQUIRED = "setup_foundation_setup_consent_required"
SETUP_FOUNDATION_REASON_EXECUTION_CONSENT_REQUIRED = (
    "setup_foundation_execution_consent_required"
)
SETUP_FOUNDATION_REASON_APPROVAL_MISSING = "setup_foundation_approval_missing"
SETUP_FOUNDATION_REASON_READY_LOCAL_DRAFT = "setup_foundation_ready_local_draft"
SETUP_FOUNDATION_REASON_READY_FOR_FUTURE_SETUP_BRANCH = (
    "setup_foundation_ready_for_future_setup_branch"
)
SETUP_FOUNDATION_PROVENANCE_SETUP_CONTRACT = "provider_setup_contract_state"
SETUP_FOUNDATION_PROVENANCE_PROFILE_DRAFT = "provider_profile_draft"
SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT = "provider_config_draft"
SETUP_FOUNDATION_PROVENANCE_VALIDATION = "setup_foundation_validation"
SETUP_FOUNDATION_PROVENANCE_CONSENT = "provider_consent_prerequisites"
SETUP_FOUNDATION_PROVENANCE_APPROVAL = "future_setup_approval"
SETUP_FOUNDATION_PROVENANCE_FUTURE_RUNTIME = "future_provider_setup_check"
SETUP_FOUNDATION_APPROVAL_STATUS_MISSING = "setup-foundation-approval-missing"
SETUP_FOUNDATION_APPROVAL_STATUS_FUTURE_GATED = "setup-foundation-approval-future-gated"
SETUP_FOUNDATION_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF = (
    "setup-foundation-approval-ready-for-future-proof"
)
SETUP_FOUNDATION_GATE_BLOCKED = "setup-foundation-gate-blocked"
SETUP_FOUNDATION_GATE_LOCAL_DRAFT = "setup-foundation-gate-local-draft"
SETUP_FOUNDATION_GATE_FUTURE_GATED = "setup-foundation-gate-future-gated"
SETUP_FOUNDATION_SETUP_ENTRY_DISABLED = "setup-entry-disabled"
SETUP_FOUNDATION_SETUP_ENTRY_READY_LOCAL_DRAFT = "setup-entry-ready-local-draft"
SETUP_FOUNDATION_PROFILE_DRAFT_MISSING = "profile-draft-missing"
SETUP_FOUNDATION_PROFILE_DRAFT_INVALID = "profile-draft-invalid"
SETUP_FOUNDATION_PROFILE_DRAFT_READY = "profile-draft-ready-local-only"
SETUP_FOUNDATION_CONFIG_DRAFT_MISSING = "config-draft-missing"
SETUP_FOUNDATION_CONFIG_DRAFT_INVALID = "config-draft-invalid"
SETUP_FOUNDATION_CONFIG_DRAFT_READY = "config-draft-ready-local-only"
SETUP_FOUNDATION_VALIDATION_FAIL_CLOSED = "setup-foundation-validation-fail-closed"
SETUP_FOUNDATION_VALIDATION_STATIC_READY = "setup-foundation-validation-static-ready"
SETUP_FOUNDATION_PERSISTENCE_DISABLED = "setup-foundation-persistence-disabled"
SETUP_FOUNDATION_PERSISTENCE_LOCAL_DRAFT_ONLY = "setup-foundation-persistence-local-draft-only"
LOCAL_NULL_PROVIDER_FALLBACK_PROOF = "local-null-provider-fallback-no-provider-calls"
FUTURE_PROVIDER_SETUP_IMPLEMENTATION_HANDOFF_READY = (
    "future-provider-setup-implementation-handoff-ready"
)
PROVIDER_SETUP_IMPLEMENTATION_FOLD_DOWN_READY = (
    "setup-implementation-foundation-fold-down-ready-for-pr-release"
)
CONSENT_COLLECTION_FOUNDATION_STATE_SCHEMA_VERSION = (
    "provider-consent-collection-foundation-state.v1"
)
CONSENT_COLLECTION_FOUNDATION_CONFIG_SCHEMA_VERSION = (
    "provider-consent-collection-foundation-config.v1"
)
CONSENT_COLLECTION_FOUNDATION_CONFIG_MIGRATION_POSTURE = (
    "safe-defaults-no-consent-collection-foundation-migration"
)
CONSENT_COLLECTION_STATE_UNKNOWN = "consent_collection_unknown"
CONSENT_COLLECTION_STATE_UNAVAILABLE = "consent_collection_unavailable"
CONSENT_COLLECTION_STATE_DISABLED = "consent_collection_disabled"
CONSENT_COLLECTION_STATE_BLOCKED_BY_CONSENT_FLOW = (
    "consent_collection_blocked_by_consent_flow"
)
CONSENT_COLLECTION_STATE_BLOCKED_BY_SETUP_FOUNDATION = (
    "consent_collection_blocked_by_setup_foundation"
)
CONSENT_COLLECTION_STATE_BLOCKED_BY_POLICY = "consent_collection_blocked_by_policy"
CONSENT_COLLECTION_STATE_BLOCKED_BY_DATA_VISIBILITY = (
    "consent_collection_blocked_by_data_visibility"
)
CONSENT_COLLECTION_STATE_BLOCKED_BY_AUDIT = "consent_collection_blocked_by_audit"
CONSENT_COLLECTION_STATE_READY_FUTURE_GATED = "consent_collection_ready_future_gated"
CONSENT_COLLECTION_STATE_READY_BUT_NOT_APPROVED = (
    "consent_collection_ready_but_not_approved"
)
CONSENT_COLLECTION_STATE_READY_BUT_NOT_COLLECTED = (
    "consent_collection_ready_but_not_collected"
)
CONSENT_COLLECTION_STATE_READY_FOR_FUTURE_CAPTURE_BRANCH = (
    "consent_collection_ready_for_future_capture_branch"
)
CONSENT_COLLECTION_STATE_DEGRADED = "consent_collection_degraded"
CONSENT_COLLECTION_ELIGIBILITY_UNAVAILABLE = "consent_collection_eligibility_unavailable"
CONSENT_COLLECTION_ELIGIBILITY_DISABLED = "consent_collection_eligibility_disabled"
CONSENT_COLLECTION_ELIGIBILITY_BLOCKED = "consent_collection_eligibility_blocked"
CONSENT_COLLECTION_ELIGIBILITY_FUTURE_GATED = (
    "consent_collection_eligibility_future_gated"
)
CONSENT_COLLECTION_ELIGIBILITY_READY_NOT_APPROVED = (
    "consent_collection_eligibility_ready_not_approved"
)
CONSENT_COLLECTION_ELIGIBILITY_READY_NOT_COLLECTED = (
    "consent_collection_eligibility_ready_not_collected"
)
CONSENT_COLLECTION_ELIGIBILITY_FUTURE_CAPTURE_BRANCH = (
    "consent_collection_eligibility_future_capture_branch"
)
CONSENT_COLLECTION_BLOCKER_CONSENT_FLOW_REQUIRED = (
    "consent_collection_consent_flow_required"
)
CONSENT_COLLECTION_BLOCKER_SETUP_FOUNDATION_REQUIRED = (
    "consent_collection_setup_foundation_required"
)
CONSENT_COLLECTION_BLOCKER_POLICY_BLOCKED = "consent_collection_policy_blocked"
CONSENT_COLLECTION_BLOCKER_DATA_VISIBILITY_REQUIRED = (
    "consent_collection_data_visibility_required"
)
CONSENT_COLLECTION_BLOCKER_AUDIT_REQUIRED = "consent_collection_audit_required"
CONSENT_COLLECTION_BLOCKER_APPROVAL_REQUIRED = "consent_collection_approval_required"
CONSENT_COLLECTION_BLOCKER_FUTURE_CAPTURE_BRANCH = (
    "consent_collection_future_capture_branch_required"
)
CONSENT_COLLECTION_REASON_DEFAULT_UNAVAILABLE = "consent_collection_default_unavailable"
CONSENT_COLLECTION_REASON_CONFIG_MISSING = "consent_collection_config_missing"
CONSENT_COLLECTION_REASON_CONFIG_INVALID = "consent_collection_config_invalid"
CONSENT_COLLECTION_REASON_CONSENT_FLOW_REQUIRED = (
    "consent_collection_consent_flow_required"
)
CONSENT_COLLECTION_REASON_SETUP_FOUNDATION_REQUIRED = (
    "consent_collection_setup_foundation_required"
)
CONSENT_COLLECTION_REASON_POLICY_BLOCKED = "consent_collection_policy_blocked"
CONSENT_COLLECTION_REASON_DATA_VISIBILITY_BLOCKED = (
    "consent_collection_data_visibility_blocked"
)
CONSENT_COLLECTION_REASON_AUDIT_REQUIRED = "consent_collection_audit_required"
CONSENT_COLLECTION_REASON_APPROVAL_MISSING = "consent_collection_approval_missing"
CONSENT_COLLECTION_REASON_READY_BUT_NOT_COLLECTED = (
    "consent_collection_ready_but_not_collected"
)
CONSENT_COLLECTION_REASON_READY_FOR_FUTURE_CAPTURE_BRANCH = (
    "consent_collection_ready_for_future_capture_branch"
)
CONSENT_COLLECTION_REASON_READY_FUTURE_GATED = "consent_collection_ready_future_gated"
CONSENT_COLLECTION_PROVENANCE_CONSENT_FLOW = "consent_flow_readiness_state"
CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION = "provider_setup_foundation_state"
CONSENT_COLLECTION_PROVENANCE_DATA_VISIBILITY = "data_visibility_contract"
CONSENT_COLLECTION_PROVENANCE_AUDIT = "audit_policy"
CONSENT_COLLECTION_PROVENANCE_POLICY = "consent_collection_policy"
CONSENT_COLLECTION_PROVENANCE_APPROVAL = "future_consent_collection_approval"
CONSENT_COLLECTION_PROVENANCE_FUTURE_CAPTURE = "future_consent_capture_branch"
CONSENT_COLLECTION_APPROVAL_STATUS_MISSING = "consent-collection-approval-missing"
CONSENT_COLLECTION_APPROVAL_STATUS_FUTURE_GATED = (
    "consent-collection-approval-future-gated"
)
CONSENT_COLLECTION_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF = (
    "consent-collection-approval-ready-for-future-proof"
)
CONSENT_COLLECTION_GATE_BLOCKED = "consent-collection-gate-blocked"
CONSENT_COLLECTION_GATE_FUTURE_GATED = "consent-collection-gate-future-gated"
CONSENT_COLLECTION_GATE_LOCAL_PROOF = "consent-collection-gate-local-proof"
CONSENT_COLLECTION_CAPTURE_SURFACE_DISABLED = "consent-capture-surface-disabled"
CONSENT_COLLECTION_CAPTURE_SURFACE_PLANNED = "consent-capture-surface-planned"
CONSENT_COLLECTION_CAPTURE_SURFACE_READY_FUTURE_GATED = (
    "consent-capture-surface-ready-future-gated"
)
CONSENT_COLLECTION_CAPTURE_SETUP_READY = "setup-consent-capture-ready"
CONSENT_COLLECTION_CAPTURE_SETUP_REQUIRED = "setup-consent-capture-required"
CONSENT_COLLECTION_CAPTURE_EXECUTION_READY = "execution-consent-capture-ready"
CONSENT_COLLECTION_CAPTURE_EXECUTION_REQUIRED = "execution-consent-capture-required"
CONSENT_COLLECTION_DATA_VISIBILITY_REVIEW_READY = "data-visibility-review-ready"
CONSENT_COLLECTION_DATA_VISIBILITY_REVIEW_REQUIRED = "data-visibility-review-required"
CONSENT_COLLECTION_AUDIT_ENVELOPE_READY = "consent-audit-envelope-ready"
CONSENT_COLLECTION_AUDIT_ENVELOPE_REQUIRED = "consent-audit-envelope-required"
CONSENT_COLLECTION_PROVENANCE_READY = "consent-provenance-ready"
CONSENT_COLLECTION_PROVENANCE_REQUIRED = "consent-provenance-required"
CONSENT_COLLECTION_PERSISTENCE_DISABLED = "consent-persistence-disabled"
CONSENT_COLLECTION_PERSISTENCE_LOCAL_PROOF_ONLY = "consent-persistence-local-proof-only"
CONSENT_COLLECTION_VALIDATION_FAIL_CLOSED = "consent-collection-validation-fail-closed"
CONSENT_COLLECTION_VALIDATION_STATIC_READY = "consent-collection-validation-static-ready"
FUTURE_CONSENT_CAPTURE_BRANCH_HANDOFF_READY = (
    "future-consent-capture-branch-handoff-ready"
)
CONSENT_COLLECTION_FOLD_DOWN_READY = (
    "consent-collection-foundation-fold-down-ready-for-pr-release"
)
CONSENT_CAPTURE_TRANSITION_SCHEMA_VERSION = "provider-consent-capture-transition.v1"
CONSENT_CAPTURE_LOCAL_RECORD_SCHEMA_VERSION = "provider-consent-capture-local-record.v1"
CONSENT_CAPTURE_RECORD_STATE_MISSING = "consent_capture_record_missing"
CONSENT_CAPTURE_RECORD_STATE_INVALID = "consent_capture_record_invalid"
CONSENT_CAPTURE_RECORD_STATE_READY = "consent_capture_record_ready"
CONSENT_CAPTURE_RECORD_STATE_REVOKED = "consent_capture_record_revoked"
CONSENT_CAPTURE_RECORD_STATE_RESET = "consent_capture_record_reset"
CONSENT_CAPTURE_RECORD_STATE_NO_CONSENT_SELECTED = (
    "consent_capture_record_no_consent_selected"
)
CONSENT_CAPTURE_STATE_NOT_REQUESTED = "consent_capture_not_requested"
CONSENT_CAPTURE_STATE_BLOCKED_BY_COLLECTION = "consent_capture_blocked_by_collection"
CONSENT_CAPTURE_STATE_BLOCKED_BY_RECORD = "consent_capture_blocked_by_record"
CONSENT_CAPTURE_STATE_CAPTURED_LOCAL_ONLY = "consent_capture_captured_local_only"
CONSENT_CAPTURE_STATE_REVOKED_LOCAL_ONLY = "consent_capture_revoked_local_only"
CONSENT_CAPTURE_STATE_RESET_LOCAL_ONLY = "consent_capture_reset_local_only"
CONSENT_CAPTURE_WRITE_STATUS_BLOCKED = "consent_capture_write_blocked"
CONSENT_CAPTURE_WRITE_STATUS_LOCAL_SNAPSHOT = (
    "consent_capture_write_local_snapshot_only"
)
CONSENT_CAPTURE_WRITE_STATUS_REVOKED_LOCAL = "consent_capture_write_revoked_local_only"
CONSENT_CAPTURE_WRITE_STATUS_RESET_LOCAL = "consent_capture_write_reset_local_only"
CONSENT_CAPTURE_WRITE_BLOCKER_NONE = "none"
CONSENT_CAPTURE_WRITE_BLOCKER_COLLECTION_NOT_READY = (
    "consent_capture_collection_not_ready"
)
CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_MISSING = "consent_capture_record_missing"
CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_INVALID = "consent_capture_record_invalid"
CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_REVOKED = "consent_capture_record_revoked"
CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_RESET = "consent_capture_record_reset"
CONSENT_CAPTURE_WRITE_BLOCKER_NO_CONSENT_SELECTED = (
    "consent_capture_no_consent_selected"
)
CONSENT_CAPTURE_WRITE_REASON_COLLECTION_NOT_READY = (
    "consent_capture_collection_not_ready"
)
CONSENT_CAPTURE_WRITE_REASON_RECORD_MISSING = "consent_capture_record_missing"
CONSENT_CAPTURE_WRITE_REASON_RECORD_INVALID = "consent_capture_record_invalid"
CONSENT_CAPTURE_WRITE_REASON_RECORD_REVOKED = "consent_capture_record_revoked"
CONSENT_CAPTURE_WRITE_REASON_RECORD_RESET = "consent_capture_record_reset"
CONSENT_CAPTURE_WRITE_REASON_NO_CONSENT_SELECTED = (
    "consent_capture_no_consent_selected"
)
CONSENT_CAPTURE_WRITE_REASON_CAPTURED_LOCAL_ONLY = (
    "consent_capture_captured_local_only"
)
CONSENT_CAPTURE_PROVENANCE_COLLECTION_STATE = "consent_collection_state"
CONSENT_CAPTURE_PROVENANCE_LOCAL_RECORD = "local_consent_capture_record"
CONSENT_CAPTURE_LOCAL_SNAPSHOT_STATUS_READY = "consent-capture-local-snapshot-ready"
CONSENT_CAPTURE_LOCAL_SNAPSHOT_STATUS_EMPTY = "consent-capture-local-snapshot-empty"
CONSENT_CAPTURE_DURABLE_PERSISTENCE_DEFERRED = (
    "consent-capture-durable-persistence-deferred"
)
CONSENT_CAPTURE_DURABLE_PERSISTENCE_LOCAL_PROOF = (
    "consent-capture-durable-persistence-local-proof"
)
CONSENT_CAPTURE_DURABLE_PERSISTENCE_FAIL_CLOSED = (
    "consent-capture-durable-persistence-fail-closed"
)
CONSENT_RECORD_STORAGE_BOUNDARY_SCHEMA_VERSION = (
    "provider-consent-record-storage-boundary.v1"
)
CONSENT_RECORD_STORAGE_BOUNDARY_LOCAL_SNAPSHOT_ONLY = (
    "consent-record-storage-local-snapshot-only"
)
CONSENT_RECORD_DURABLE_STORAGE_DEFERRED = "consent-record-durable-storage-deferred"
CONSENT_RECORD_STORAGE_BOUNDARY_LOCAL_DURABLE_ONLY = (
    "consent-record-storage-local-durable-only"
)
CONSENT_RECORD_DURABLE_STORAGE_LOCAL_READY = "consent-record-durable-storage-local-ready"
CONSENT_RECORD_DURABLE_STORAGE_FAIL_CLOSED = (
    "consent-record-durable-storage-fail-closed"
)
CONSENT_RECORD_REVOCATION_MODEL_LOCAL_ONLY = "consent-record-revocation-local-only"
CONSENT_RECORD_RESET_MODEL_LOCAL_ONLY = "consent-record-reset-local-only"
CONSENT_RECORD_REVOCATION_MODEL_LOCAL_DURABLE = (
    "consent-record-revocation-local-durable"
)
CONSENT_RECORD_RESET_MODEL_LOCAL_DURABLE = "consent-record-reset-local-durable"
CONSENT_RECORD_NO_SECRETS_POSTURE_READY = "consent-record-no-secrets-ready"
CONSENT_RECORD_PROVIDER_PAYLOAD_EXCLUDED = "consent-record-provider-payload-excluded"
CONSENT_DURABLE_RECORD_SCHEMA_VERSION = "provider-durable-consent-record.v1"
CONSENT_DURABLE_RECORD_STALE_SCHEMA_VERSION = "provider-durable-consent-record.v0"
CONSENT_DURABLE_STORAGE_BOUNDARY_SCHEMA_VERSION = (
    "provider-durable-consent-storage-boundary.v1"
)
CONSENT_DURABLE_RECORD_STATE_MISSING = "durable_consent_record_missing"
CONSENT_DURABLE_RECORD_STATE_READY = "durable_consent_record_ready"
CONSENT_DURABLE_RECORD_STATE_INVALID = "durable_consent_record_invalid"
CONSENT_DURABLE_RECORD_STATE_CORRUPT = "durable_consent_record_corrupt"
CONSENT_DURABLE_RECORD_STATE_UNSUPPORTED_SCHEMA = (
    "durable_consent_record_unsupported_schema"
)
CONSENT_DURABLE_RECORD_STATE_STALE_SCHEMA = "durable_consent_record_stale_schema"
CONSENT_DURABLE_RECORD_STATE_REVOKED = "durable_consent_record_revoked"
CONSENT_DURABLE_RECORD_STATE_RESET = "durable_consent_record_reset"
CONSENT_DURABLE_RECORD_STATE_EXPIRED = "durable_consent_record_expired"
CONSENT_DURABLE_STORAGE_BOUNDARY_LOCAL_ONLY = "durable-consent-local-file-only"
CONSENT_DURABLE_STORAGE_STATE_MISSING = "durable-consent-storage-missing"
CONSENT_DURABLE_STORAGE_STATE_LOCAL_READY = "durable-consent-storage-local-ready"
CONSENT_DURABLE_STORAGE_STATE_FAIL_CLOSED = "durable-consent-storage-fail-closed"
CONSENT_DURABLE_MIGRATION_CURRENT_SCHEMA_READY = (
    "durable-consent-migration-current-schema-ready"
)
CONSENT_DURABLE_MIGRATION_STALE_SCHEMA_FAIL_CLOSED = (
    "durable-consent-migration-stale-schema-fail-closed"
)
CONSENT_DURABLE_MIGRATION_UNSUPPORTED_SCHEMA_FAIL_CLOSED = (
    "durable-consent-migration-unsupported-schema-fail-closed"
)
CONSENT_DURABLE_MIGRATION_NOT_APPLICABLE = "durable-consent-migration-not-applicable"
CONSENT_DURABLE_FAIL_REASON_NONE = "none"
CONSENT_DURABLE_FAIL_REASON_MISSING = "durable_consent_missing"
CONSENT_DURABLE_FAIL_REASON_INVALID = "durable_consent_invalid"
CONSENT_DURABLE_FAIL_REASON_CORRUPT = "durable_consent_corrupt"
CONSENT_DURABLE_FAIL_REASON_STALE_SCHEMA = "durable_consent_stale_schema"
CONSENT_DURABLE_FAIL_REASON_UNSUPPORTED_SCHEMA = (
    "durable_consent_unsupported_schema"
)
CONSENT_DURABLE_FAIL_REASON_REVOKED = "durable_consent_revoked"
CONSENT_DURABLE_FAIL_REASON_RESET = "durable_consent_reset"
CONSENT_DURABLE_FAIL_REASON_EXPIRED = "durable_consent_expired"
CONSENT_DURABLE_FAIL_REASON_NO_CONSENT_SELECTED = (
    "durable_consent_no_consent_selected"
)
CONSENT_DURABLE_CONSENT_STATE_MISSING = "durable_consent_missing"
CONSENT_DURABLE_CONSENT_STATE_GRANTED = "durable_consent_granted_local_only"
CONSENT_DURABLE_CONSENT_STATE_REVOKED = "durable_consent_revoked_local_only"
CONSENT_DURABLE_CONSENT_STATE_RESET = "durable_consent_reset_local_only"
CONSENT_DURABLE_CONSENT_STATE_EXPIRED = "durable_consent_expired_local_only"
CONSENT_DURABLE_CONSENT_STATE_BLOCKED = "durable_consent_blocked_fail_closed"
CONSENT_DURABLE_SETUP_REASON_MISSING = "durable_setup_consent_missing"
CONSENT_DURABLE_EXECUTION_REASON_MISSING = "durable_execution_consent_missing"
CONSENT_DURABLE_REASON_GRANTED = "durable_consent_present_local_only"
CONSENT_DURABLE_REASON_REVOKED = "durable_consent_revoked"
CONSENT_DURABLE_REASON_RESET = "durable_consent_reset"
CONSENT_DURABLE_REASON_EXPIRED = "durable_consent_expired"
CONSENT_DURABLE_REASON_FAIL_CLOSED = "durable_consent_fail_closed"
CONSENT_DURABLE_SEPARATION_STATE_READY = (
    "durable-setup-execution-consent-separated"
)
CONSENT_DURABLE_STATUS_PROOF_HIDDEN_TELEMETRY = (
    "durable-consent-status-hidden-telemetry"
)
CONSENT_DURABLE_DESKTOP_DISPLAY_SUPPRESSED = (
    "durable-consent-desktop-display-suppressed"
)
CONSENT_DURABLE_PROVIDER_SETUP_HANDOFF_READY = (
    "durable-consent-provider-setup-handoff-ready-future-gated"
)
CONSENT_DURABLE_PROVIDER_SETUP_HANDOFF_BLOCKED = (
    "durable-consent-provider-setup-handoff-blocked"
)
CONSENT_DURABLE_PROVIDER_EXECUTION_HANDOFF_READY = (
    "durable-consent-provider-execution-handoff-ready-future-gated"
)
CONSENT_DURABLE_PROVIDER_EXECUTION_HANDOFF_BLOCKED = (
    "durable-consent-provider-execution-handoff-blocked"
)
CONSENT_DURABLE_FUTURE_HANDOFF_CRITERIA_READY = (
    "durable-consent-future-handoff-criteria-ready-local-only"
)
CONSENT_DURABLE_FUTURE_HANDOFF_CRITERIA_BLOCKED = (
    "durable-consent-future-handoff-criteria-blocked"
)
CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD = "durable_local_consent_record"
CONSENT_DURABLE_PROVENANCE_LOCAL_STORE = "durable_local_consent_store"
CONSENT_DURABLE_DEFAULT_RECORD_ID = "local-durable-consent-record"
CONSENT_DURABLE_DEFAULT_AUDIT_EVENT_ID = "local-durable-consent-audit"
CONSENT_DURABLE_RECORD_FILENAME = "provider_durable_consent_record.json"
CONSENT_DURABLE_STORE_DIR_ENV = "NEXUS_PROVIDER_DURABLE_CONSENT_STORE_DIR"
CONSENT_DURABLE_STORE_DIRNAME = "provider_consent"
CONSENT_UX_STATE_SCHEMA_VERSION = "provider-user-operated-consent-ux-state.v1"
CONSENT_UX_INTENT_SCHEMA_VERSION = "provider-user-operated-consent-ux-intent.v1"
CONSENT_UX_STATE_BLOCKED_BY_DURABLE_CONSENT = (
    "consent_ux_blocked_by_durable_consent"
)
CONSENT_UX_STATE_READY_LOCAL_ONLY = "consent_ux_ready_local_only"
CONSENT_UX_STATE_REVOKED_LOCAL_ONLY = "consent_ux_revoked_local_only"
CONSENT_UX_STATE_RESET_LOCAL_ONLY = "consent_ux_reset_local_only"
CONSENT_UX_STATE_EXPIRED_LOCAL_ONLY = "consent_ux_expired_local_only"
CONSENT_UX_STATE_DEGRADED_FAIL_CLOSED = "consent_ux_degraded_fail_closed"
CONSENT_UX_INTENT_NONE = "consent_ux_intent_none"
CONSENT_UX_INTENT_SETUP_SELECTED = "consent_ux_intent_setup_selected_local_only"
CONSENT_UX_INTENT_EXECUTION_SELECTED = (
    "consent_ux_intent_execution_selected_local_only"
)
CONSENT_UX_INTENT_REVOKE_SELECTED = "consent_ux_intent_revoke_selected_local_only"
CONSENT_UX_INTENT_RESET_SELECTED = "consent_ux_intent_reset_selected_local_only"
CONSENT_UX_INTENT_BLOCKED = "consent_ux_intent_blocked_fail_closed"
CONSENT_UX_SURFACE_STATUS_ONLY_LOCAL = "consent-ux-status-only-local"
CONSENT_UX_SURFACE_CONTROLS_LOCAL_INTENT = "consent-ux-controls-local-intent"
CONSENT_UX_WRITE_LOCAL_INTENT_ONLY = "consent-ux-write-local-intent-only"
CONSENT_UX_WRITE_BLOCKED_FAIL_CLOSED = "consent-ux-write-blocked-fail-closed"
CONSENT_UX_DURABLE_HANDOFF_READY = "consent-ux-durable-handoff-ready"
CONSENT_UX_DURABLE_HANDOFF_BLOCKED = "consent-ux-durable-handoff-blocked"
CONSENT_UX_PROVIDER_SETUP_GATE_FUTURE_GATED = (
    "consent-ux-provider-setup-gate-future-gated"
)
CONSENT_UX_PROVIDER_SETUP_GATE_BLOCKED = "consent-ux-provider-setup-gate-blocked"
CONSENT_UX_PROVIDER_EXECUTION_GATE_DISABLED = (
    "consent-ux-provider-execution-gate-disabled"
)
CONSENT_UX_STATUS_PROOF_STATE = "consent-ux-status-proof-derived-from-durable-state"
CONSENT_UX_DESKTOP_DISPLAY_SUPPRESSED = "consent-ux-desktop-display-suppressed"
CONSENT_UX_LOCAL_ONLY_POSTURE = "consent-ux-local-only"
SETUP_COMPLETION_STATE_SCHEMA_VERSION = "provider-setup-completion-foundation-state.v1"
SETUP_COMPLETION_CONFIG_SCHEMA_VERSION = "provider-setup-completion-foundation-config.v1"
SETUP_COMPLETION_CONFIG_MIGRATION_POSTURE = (
    "safe-local-setup-completion-v1-no-secret-migration"
)
SETUP_COMPLETION_STATE_UNAVAILABLE = "setup_completion_unavailable"
SETUP_COMPLETION_STATE_BLOCKED_BY_CONSENT_UX = (
    "setup_completion_blocked_by_consent_ux"
)
SETUP_COMPLETION_STATE_BLOCKED_BY_PROFILE = (
    "setup_completion_blocked_by_profile"
)
SETUP_COMPLETION_STATE_BLOCKED_BY_CONFIG = "setup_completion_blocked_by_config"
SETUP_COMPLETION_STATE_BLOCKED_BY_NO_SECRETS = (
    "setup_completion_blocked_by_no_secrets"
)
SETUP_COMPLETION_STATE_BLOCKED_BY_VALIDATION = (
    "setup_completion_blocked_by_validation"
)
SETUP_COMPLETION_STATE_RESET_LOCAL_ONLY = "setup_completion_reset_local_only"
SETUP_COMPLETION_STATE_READY_LOCAL_ONLY = "setup_completion_ready_local_only"
SETUP_COMPLETION_STATE_READY_FOR_FUTURE_SDK_HANDOFF = (
    "setup_completion_ready_for_future_sdk_handoff"
)
SETUP_COMPLETION_ELIGIBILITY_UNAVAILABLE = "setup_completion_eligibility_unavailable"
SETUP_COMPLETION_ELIGIBILITY_BLOCKED = "setup_completion_eligibility_blocked"
SETUP_COMPLETION_ELIGIBILITY_RESET = "setup_completion_eligibility_reset"
SETUP_COMPLETION_ELIGIBILITY_LOCAL_READY = "setup_completion_eligibility_local_ready"
SETUP_COMPLETION_ELIGIBILITY_FUTURE_HANDOFF = (
    "setup_completion_eligibility_future_handoff"
)
SETUP_COMPLETION_BLOCKER_CONSENT_UX_REQUIRED = (
    "setup_completion_consent_ux_required"
)
SETUP_COMPLETION_BLOCKER_PROFILE_FINALIZATION_REQUIRED = (
    "setup_completion_profile_finalization_required"
)
SETUP_COMPLETION_BLOCKER_CONFIG_FINALIZATION_REQUIRED = (
    "setup_completion_config_finalization_required"
)
SETUP_COMPLETION_BLOCKER_NO_SECRETS_REQUIRED = (
    "setup_completion_no_secrets_required"
)
SETUP_COMPLETION_BLOCKER_VALIDATION_REQUIRED = (
    "setup_completion_validation_required"
)
SETUP_COMPLETION_BLOCKER_RESET_REQUESTED = "setup_completion_reset_requested"
SETUP_COMPLETION_BLOCKER_FUTURE_SDK_HANDOFF = (
    "setup_completion_future_sdk_handoff_required"
)
SETUP_COMPLETION_BLOCKER_NONE = "none"
SETUP_COMPLETION_REASON_DEFAULT_UNAVAILABLE = (
    "setup_completion_default_unavailable"
)
SETUP_COMPLETION_REASON_CONSENT_UX_REQUIRED = (
    "setup_completion_consent_ux_required"
)
SETUP_COMPLETION_REASON_PROFILE_MISSING = "setup_completion_profile_missing"
SETUP_COMPLETION_REASON_PROFILE_INVALID = "setup_completion_profile_invalid"
SETUP_COMPLETION_REASON_CONFIG_MISSING = "setup_completion_config_missing"
SETUP_COMPLETION_REASON_CONFIG_INVALID = "setup_completion_config_invalid"
SETUP_COMPLETION_REASON_NO_SECRETS_FAILED = "setup_completion_no_secrets_failed"
SETUP_COMPLETION_REASON_VALIDATION_FAILED = "setup_completion_validation_failed"
SETUP_COMPLETION_REASON_RESET_REQUESTED = "setup_completion_reset_requested"
SETUP_COMPLETION_REASON_READY_LOCAL_ONLY = "setup_completion_ready_local_only"
SETUP_COMPLETION_REASON_READY_FOR_FUTURE_SDK_HANDOFF = (
    "setup_completion_ready_for_future_sdk_handoff"
)
SETUP_COMPLETION_PROVENANCE_CONSENT_UX = "provider_user_operated_consent_ux_state"
SETUP_COMPLETION_PROVENANCE_PROFILE = "provider_profile_finalization"
SETUP_COMPLETION_PROVENANCE_CONFIG = "provider_config_finalization"
SETUP_COMPLETION_PROVENANCE_NO_SECRETS = "provider_setup_no_secrets_validation"
SETUP_COMPLETION_PROVENANCE_VALIDATION = "provider_setup_completion_validation"
SETUP_COMPLETION_PROVENANCE_RESET = "provider_setup_completion_reset"
SETUP_COMPLETION_PROVENANCE_HANDOFF = "future_provider_sdk_handoff"
SETUP_COMPLETION_PROFILE_MISSING = "setup_completion_profile_missing"
SETUP_COMPLETION_PROFILE_INVALID = "setup_completion_profile_invalid"
SETUP_COMPLETION_PROFILE_FINALIZED = "setup_completion_profile_finalized_local_only"
SETUP_COMPLETION_CONFIG_MISSING = "setup_completion_config_missing"
SETUP_COMPLETION_CONFIG_INVALID = "setup_completion_config_invalid"
SETUP_COMPLETION_CONFIG_FINALIZED = "setup_completion_config_finalized_local_only"
SETUP_COMPLETION_NO_SECRETS_BLOCKED = "setup_completion_no_secrets_blocked"
SETUP_COMPLETION_NO_SECRETS_READY = "setup_completion_no_secrets_ready"
SETUP_COMPLETION_VALIDATION_FAIL_CLOSED = "setup_completion_validation_fail_closed"
SETUP_COMPLETION_VALIDATION_LOCAL_READY = "setup_completion_validation_local_ready"
SETUP_COMPLETION_PERSISTENCE_BLOCKED = "setup_completion_persistence_blocked"
SETUP_COMPLETION_PERSISTENCE_LOCAL_METADATA_ONLY = (
    "setup_completion_persistence_local_metadata_only"
)
SETUP_COMPLETION_RESET_NONE = "setup_completion_reset_none"
SETUP_COMPLETION_RESET_REQUESTED = "setup_completion_reset_requested_local_only"
SETUP_COMPLETION_STATUS_PROOF_HIDDEN_TELEMETRY = (
    "setup-completion-status-hidden-telemetry"
)
SETUP_COMPLETION_STATUS_PROOF_PUBLIC_LOCAL_ASSIST = (
    "setup-completion-status-public-local-assist"
)
SETUP_COMPLETION_DESKTOP_DISPLAY_SUPPRESSED = (
    "setup-completion-desktop-display-suppressed"
)
SETUP_COMPLETION_DESKTOP_DISPLAY_VISIBLE = (
    "setup-completion-desktop-display-visible"
)
SETUP_COMPLETION_PROVIDER_SETUP_GATE_BLOCKED = (
    "setup-completion-provider-setup-gate-blocked"
)
SETUP_COMPLETION_PROVIDER_SETUP_GATE_FUTURE_GATED = (
    "setup-completion-provider-setup-gate-future-gated"
)
SETUP_COMPLETION_PROVIDER_EXECUTION_GATE_DISABLED = (
    "setup-completion-provider-execution-gate-disabled"
)
SETUP_COMPLETION_SDK_HANDOFF_BLOCKED = "setup-completion-sdk-handoff-blocked"
SETUP_COMPLETION_SDK_HANDOFF_READY_FUTURE_GATED = (
    "setup-completion-sdk-handoff-ready-future-gated"
)
SETUP_COMPLETION_FUNCTIONAL_AI_CRITERIA_PENDING = (
    "setup-completion-functional-ai-criteria-pending"
)
SETUP_COMPLETION_V18_CONTINUATION_PENDING = (
    "setup-completion-v18-continuation-pending"
)
CONSENT_UX_FUNCTIONAL_AI_CRITERIA_PENDING = "consent-ux-functional-ai-pending"
CONSENT_UX_V18_CONTINUATION_PENDING = "consent-ux-v1.8.0-continuation-pending"
CONSENT_CAPTURE_AUDIT_SCHEMA_VERSION = "provider-consent-capture-audit.v1"
CONSENT_CAPTURE_AUDIT_STATUS_LOCAL_PROOF = "consent-capture-audit-local-proof"
CONSENT_CAPTURE_AUDIT_STATUS_BLOCKED = "consent-capture-audit-blocked"
CONSENT_CAPTURE_SETUP_EXECUTION_SEPARATION_READY = (
    "setup-execution-consent-separation-ready"
)
CONSENT_CAPTURE_UI_STATUS_PROOF_HIDDEN_TELEMETRY = (
    "consent-capture-ui-status-hidden-telemetry"
)
CONSENT_CAPTURE_DESKTOP_DISPLAY_SUPPRESSED = (
    "consent-capture-desktop-display-suppressed"
)
CONSENT_CAPTURE_PROVIDER_SETUP_HANDOFF_READY = (
    "consent-capture-provider-setup-handoff-ready"
)
CONSENT_CAPTURE_FUNCTIONAL_AI_CRITERIA_PENDING = (
    "consent-capture-functional-ai-criteria-pending"
)
CONSENT_CAPTURE_V18_CONTINUATION_PENDING = (
    "consent-capture-v1.8.0-continuation-pending"
)
CAPABILITY_PACK_ELIGIBILITY_UNKNOWN = "capability-pack-eligibility-unknown"
CAPABILITY_PACK_ELIGIBILITY_BLOCKED = "capability-pack-eligibility-blocked"
CAPABILITY_PACK_ELIGIBILITY_FUTURE_GATED = "capability-pack-eligibility-future-gated"
CAPABILITY_PACK_ELIGIBILITY_INELIGIBLE = "capability-pack-eligibility-ineligible"
CAPABILITY_PACK_MANIFEST_MISSING = "manifest-missing"
CAPABILITY_PACK_MANIFEST_INVALID = "manifest-invalid"
CAPABILITY_PACK_MANIFEST_VALID_FUTURE_GATED = "manifest-valid-future-gated"
CAPABILITY_PACK_SOURCE_TRUST_UNVERIFIED = "source-trust-unverified"
CAPABILITY_PACK_SOURCE_TRUST_LOCAL_ONLY = "source-trust-local-only"
CAPABILITY_PACK_SOURCE_TRUST_FUTURE_GATED = "source-trust-future-gated"
CAPABILITY_PACK_COMPATIBILITY_BLOCKED = "compatibility-blocked"
CAPABILITY_PACK_COMPATIBILITY_FUTURE_GATED = "compatibility-future-gated"
CAPABILITY_PACK_REQUIREMENT_UNPROBED = "requirement-unprobed"
CAPABILITY_PACK_REQUIREMENT_MISSING = "requirement-missing"
CAPABILITY_PACK_REQUIREMENT_FUTURE_GATED = "requirement-future-gated"
CAPABILITY_PACK_INSTALL_INTENT_NONE = "install-intent-none"
CAPABILITY_PACK_INSTALL_INTENT_BLOCKED = "install-intent-blocked"
CAPABILITY_PACK_INSTALL_INTENT_FUTURE_GATED = "install-intent-future-gated"
CAPABILITY_PACK_DOWNLOAD_BLOCKED_REASON = "download_blocked_user_approval_required"
CAPABILITY_PACK_INSTALL_BLOCKED_REASON = "install_blocked_manifest_or_user_approval_required"
CAPABILITY_PACK_UPDATE_BLOCKED_REASON = "update_blocked_user_approval_required"
CAPABILITY_PACK_UNINSTALL_BLOCKED_REASON = "uninstall_blocked_no_installed_pack"
READINESS_ACTION_ALLOWED_LOCAL_READ_ONLY = "allowed_local_read_only"
READINESS_ACTION_FUTURE_USER_APPROVAL_REQUIRED = "future_user_approval_required"
PROVIDER_RUNTIME_STATE_CATEGORIES = (
    PROVIDER_RUNTIME_CATEGORY_NO_PROVIDER,
    PROVIDER_RUNTIME_CATEGORY_SETUP_DISABLED,
    PROVIDER_RUNTIME_CATEGORY_UNCONFIGURED,
    PROVIDER_RUNTIME_CATEGORY_UNAVAILABLE,
    PROVIDER_RUNTIME_CATEGORY_CONSENT_MISSING,
    PROVIDER_RUNTIME_CATEGORY_CAPABILITY_MISSING,
    PROVIDER_RUNTIME_CATEGORY_READY_FUTURE_GATED,
    PROVIDER_RUNTIME_CATEGORY_ERROR_DEGRADED,
)
PROVIDER_RUNTIME_REASON_CODES = (
    PROVIDER_RUNTIME_REASON_NO_PROVIDER_CONFIGURED,
    PROVIDER_RUNTIME_REASON_SETUP_DISABLED_LOCAL_ONLY,
    PROVIDER_RUNTIME_REASON_PROVIDER_UNCONFIGURED,
    PROVIDER_RUNTIME_REASON_PROVIDER_UNAVAILABLE,
    PROVIDER_RUNTIME_REASON_CONSENT_REQUIRED,
    PROVIDER_RUNTIME_REASON_CAPABILITY_MISSING,
    PROVIDER_RUNTIME_REASON_READY_FUTURE_GATED,
    PROVIDER_RUNTIME_REASON_INVALID_CONFIG_FAIL_CLOSED,
    PROVIDER_RUNTIME_REASON_MISSING_CONFIG_FAIL_CLOSED,
)
PROVIDER_RUNTIME_PROVENANCE_SOURCES = (
    PROVIDER_RUNTIME_PROVENANCE_DEFAULT_CONFIG,
    PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG,
    PROVIDER_RUNTIME_PROVENANCE_HARDWARE_SNAPSHOT,
    PROVIDER_RUNTIME_PROVENANCE_MANIFEST_STATE,
    PROVIDER_RUNTIME_PROVENANCE_VALIDATOR_FIXTURE,
    PROVIDER_RUNTIME_PROVENANCE_FUTURE_RUNTIME_CHECK,
)
PROVIDER_READINESS_STATES = (
    PROVIDER_READINESS_STATE_UNKNOWN,
    PROVIDER_READINESS_STATE_SETUP_DISABLED,
    PROVIDER_READINESS_STATE_SETUP_AVAILABLE_FUTURE_GATED,
    PROVIDER_READINESS_STATE_SETUP_INELIGIBLE,
    PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CONSENT,
    PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CAPABILITY,
    PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_MANIFEST,
    PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_POLICY,
    PROVIDER_READINESS_STATE_SETUP_CONFIG_REQUIRED,
    PROVIDER_READINESS_STATE_PROVIDER_READY_EXECUTION_GATED,
    PROVIDER_READINESS_STATE_DEGRADED,
)
PROVIDER_READINESS_REASON_CODES = (
    PROVIDER_READINESS_REASON_DEFAULT_LOCAL_ONLY,
    PROVIDER_READINESS_REASON_CONFIG_MISSING_FAIL_CLOSED,
    PROVIDER_READINESS_REASON_CONFIG_INVALID_FAIL_CLOSED,
    PROVIDER_READINESS_REASON_PROVIDER_UNCONFIGURED,
    PROVIDER_READINESS_REASON_CONSENT_MISSING,
    PROVIDER_READINESS_REASON_CAPABILITY_MISSING,
    PROVIDER_READINESS_REASON_MANIFEST_MISSING,
    PROVIDER_READINESS_REASON_MANIFEST_INVALID_INSTALL_BLOCKED,
    PROVIDER_READINESS_REASON_POLICY_BLOCKED,
    PROVIDER_READINESS_REASON_FUTURE_PROVIDER_GATED,
    PROVIDER_READINESS_REASON_PROVIDER_NOT_READY,
    PROVIDER_READINESS_REASON_PROVIDER_READY_EXECUTION_GATED,
)
PROVIDER_READINESS_PROVENANCE_SOURCES = (
    PROVIDER_READINESS_PROVENANCE_DEFAULT_CONFIG,
    PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG,
    PROVIDER_READINESS_PROVENANCE_RELEASE_SOURCE_TRUTH,
    PROVIDER_READINESS_PROVENANCE_HARDWARE_SNAPSHOT,
    PROVIDER_READINESS_PROVENANCE_CAPABILITY_MANIFEST,
    PROVIDER_READINESS_PROVENANCE_CONSENT_STATE,
    PROVIDER_READINESS_PROVENANCE_VALIDATOR_FIXTURE,
    PROVIDER_READINESS_PROVENANCE_FUTURE_RUNTIME_CHECK,
)
PROVIDER_ACTIVATION_STATES = (
    PROVIDER_ACTIVATION_STATE_UNKNOWN,
    PROVIDER_ACTIVATION_STATE_UNAVAILABLE,
    PROVIDER_ACTIVATION_STATE_DISABLED,
    PROVIDER_ACTIVATION_STATE_BLOCKED_BY_READINESS,
    PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CONSENT,
    PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CAPABILITY,
    PROVIDER_ACTIVATION_STATE_BLOCKED_BY_POLICY,
    PROVIDER_ACTIVATION_STATE_BLOCKED_BY_MANIFEST,
    PROVIDER_ACTIVATION_STATE_BLOCKED_BY_ADAPTER,
    PROVIDER_ACTIVATION_STATE_ELIGIBLE_FUTURE_GATED,
    PROVIDER_ACTIVATION_STATE_READY_EXECUTION_GATED,
    PROVIDER_ACTIVATION_STATE_DEGRADED,
    PROVIDER_ACTIVATION_STATE_FUNCTIONAL_AI_READY_FUTURE_VERSION,
)
PROVIDER_ACTIVATION_REASON_CODES = (
    PROVIDER_ACTIVATION_REASON_DEFAULT_UNAVAILABLE,
    PROVIDER_ACTIVATION_REASON_CONFIG_MISSING_FAIL_CLOSED,
    PROVIDER_ACTIVATION_REASON_CONFIG_INVALID_FAIL_CLOSED,
    PROVIDER_ACTIVATION_REASON_READINESS_BLOCKED,
    PROVIDER_ACTIVATION_REASON_CONSENT_REQUIRED,
    PROVIDER_ACTIVATION_REASON_CAPABILITY_REQUIRED,
    PROVIDER_ACTIVATION_REASON_POLICY_BLOCKED,
    PROVIDER_ACTIVATION_REASON_MANIFEST_REQUIRED,
    PROVIDER_ACTIVATION_REASON_ADAPTER_UNAVAILABLE,
    PROVIDER_ACTIVATION_REASON_FUTURE_GATED,
    PROVIDER_ACTIVATION_REASON_EXECUTION_GATED,
    PROVIDER_ACTIVATION_REASON_FUNCTIONAL_AI_FUTURE_VERSION,
)
PROVIDER_ACTIVATION_PROVENANCE_SOURCES = (
    PROVIDER_ACTIVATION_PROVENANCE_DEFAULT_CONFIG,
    PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG,
    PROVIDER_ACTIVATION_PROVENANCE_READINESS_STATE,
    PROVIDER_ACTIVATION_PROVENANCE_CAPABILITY_MANIFEST,
    PROVIDER_ACTIVATION_PROVENANCE_CONSENT_STATE,
    PROVIDER_ACTIVATION_PROVENANCE_ADAPTER_CONTRACT,
    PROVIDER_ACTIVATION_PROVENANCE_VALIDATOR_FIXTURE,
    PROVIDER_ACTIVATION_PROVENANCE_FUTURE_RUNTIME_CHECK,
    PROVIDER_ACTIVATION_PROVENANCE_RELEASE_SOURCE_TRUTH,
)
PROVIDER_EXECUTION_READINESS_STATES = (
    PROVIDER_EXECUTION_READINESS_STATE_UNKNOWN,
    PROVIDER_EXECUTION_READINESS_STATE_UNAVAILABLE,
    PROVIDER_EXECUTION_READINESS_STATE_DISABLED,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ACTIVATION,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROVIDER_PATH,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ADAPTER,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROMPT_GATE,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_MODEL_GATE,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_CONSENT,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_SAFETY,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_NETWORK,
    PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_POLICY,
    PROVIDER_EXECUTION_READINESS_STATE_READY_FUTURE_GATED,
    PROVIDER_EXECUTION_READINESS_STATE_READY_BUT_NOT_APPROVED,
    PROVIDER_EXECUTION_READINESS_STATE_DEGRADED,
    PROVIDER_EXECUTION_READINESS_STATE_FUNCTIONAL_AI_READY_FUTURE_VERSION,
)
PROVIDER_EXECUTION_REASON_CODES = (
    PROVIDER_EXECUTION_REASON_DEFAULT_UNAVAILABLE,
    PROVIDER_EXECUTION_REASON_CONFIG_MISSING_FAIL_CLOSED,
    PROVIDER_EXECUTION_REASON_CONFIG_INVALID_FAIL_CLOSED,
    PROVIDER_EXECUTION_REASON_ACTIVATION_BLOCKED,
    PROVIDER_EXECUTION_REASON_PROVIDER_PATH_MISSING,
    PROVIDER_EXECUTION_REASON_ADAPTER_UNAVAILABLE,
    PROVIDER_EXECUTION_REASON_PROMPT_GATE_BLOCKED,
    PROVIDER_EXECUTION_REASON_MODEL_GATE_BLOCKED,
    PROVIDER_EXECUTION_REASON_CONSENT_REQUIRED,
    PROVIDER_EXECUTION_REASON_SAFETY_EVAL_REQUIRED,
    PROVIDER_EXECUTION_REASON_NETWORK_BLOCKED,
    PROVIDER_EXECUTION_REASON_POLICY_BLOCKED,
    PROVIDER_EXECUTION_REASON_FUTURE_GATED,
    PROVIDER_EXECUTION_REASON_APPROVAL_MISSING,
    PROVIDER_EXECUTION_REASON_FUNCTIONAL_AI_FUTURE_VERSION,
)
PROVIDER_EXECUTION_PROVENANCE_SOURCES = (
    PROVIDER_EXECUTION_PROVENANCE_DEFAULT_CONFIG,
    PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG,
    PROVIDER_EXECUTION_PROVENANCE_ACTIVATION_STATE,
    PROVIDER_EXECUTION_PROVENANCE_PROVIDER_PATH_CONTRACT,
    PROVIDER_EXECUTION_PROVENANCE_ADAPTER_CONTRACT,
    PROVIDER_EXECUTION_PROVENANCE_PROMPT_GATE,
    PROVIDER_EXECUTION_PROVENANCE_MODEL_GATE,
    PROVIDER_EXECUTION_PROVENANCE_CONSENT_STATE,
    PROVIDER_EXECUTION_PROVENANCE_SAFETY_EVAL,
    PROVIDER_EXECUTION_PROVENANCE_NETWORK_POLICY,
    PROVIDER_EXECUTION_PROVENANCE_VALIDATOR_FIXTURE,
    PROVIDER_EXECUTION_PROVENANCE_FUTURE_RUNTIME_CHECK,
    PROVIDER_EXECUTION_PROVENANCE_RELEASE_SOURCE_TRUTH,
)
PROVIDER_PATH_READINESS_STATES = (
    PROVIDER_PATH_READINESS_STATE_UNKNOWN,
    PROVIDER_PATH_READINESS_STATE_UNAVAILABLE,
    PROVIDER_PATH_READINESS_STATE_DISABLED,
    PROVIDER_PATH_READINESS_STATE_UNSELECTED,
    PROVIDER_PATH_READINESS_STATE_SELECTION_REQUIRED,
    PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_POLICY,
    PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CONSENT,
    PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CAPABILITY,
    PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_MANIFEST,
    PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_SAFETY,
    PROVIDER_PATH_READINESS_STATE_READY_FUTURE_GATED,
    PROVIDER_PATH_READINESS_STATE_READY_BUT_NOT_APPROVED,
    PROVIDER_PATH_READINESS_STATE_DEGRADED,
    PROVIDER_PATH_READINESS_STATE_READY_FOR_FUTURE_EXECUTION_BRANCH,
)
PROVIDER_PATH_REASON_CODES = (
    PROVIDER_PATH_REASON_DEFAULT_UNAVAILABLE,
    PROVIDER_PATH_REASON_CONFIG_MISSING_FAIL_CLOSED,
    PROVIDER_PATH_REASON_CONFIG_INVALID_FAIL_CLOSED,
    PROVIDER_PATH_REASON_EXECUTION_READINESS_UNAVAILABLE,
    PROVIDER_PATH_REASON_UNSELECTED,
    PROVIDER_PATH_REASON_CONFIG_MISSING,
    PROVIDER_PATH_REASON_CONFIG_INVALID,
    PROVIDER_PATH_REASON_SETUP_CONSENT_REQUIRED,
    PROVIDER_PATH_REASON_EXECUTION_CONSENT_REQUIRED,
    PROVIDER_PATH_REASON_DATA_VISIBILITY_BLOCKED,
    PROVIDER_PATH_REASON_CAPABILITY_MISSING,
    PROVIDER_PATH_REASON_MANIFEST_MISSING,
    PROVIDER_PATH_REASON_SAFETY_BLOCKED,
    PROVIDER_PATH_REASON_POLICY_BLOCKED,
    PROVIDER_PATH_REASON_SETUP_APPROVAL_MISSING,
    PROVIDER_PATH_REASON_EXECUTION_APPROVAL_MISSING,
    PROVIDER_PATH_REASON_READY_FOR_FUTURE_EXECUTION_BRANCH,
    PROVIDER_PATH_REASON_FUNCTIONAL_AI_FUTURE_VERSION,
)
PROVIDER_PATH_PROVENANCE_SOURCES = (
    PROVIDER_PATH_PROVENANCE_DEFAULT_CONFIG,
    PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG,
    PROVIDER_PATH_PROVENANCE_EXECUTION_READINESS_STATE,
    PROVIDER_PATH_PROVENANCE_PROVIDER_SELECTION_CONTRACT,
    PROVIDER_PATH_PROVENANCE_PROVIDER_CONFIG_CONTRACT,
    PROVIDER_PATH_PROVENANCE_CONSENT_STATE,
    PROVIDER_PATH_PROVENANCE_DATA_VISIBILITY_CONTRACT,
    PROVIDER_PATH_PROVENANCE_CAPABILITY_CONTRACT,
    PROVIDER_PATH_PROVENANCE_MANIFEST_STATE,
    PROVIDER_PATH_PROVENANCE_SAFETY_EVAL,
    PROVIDER_PATH_PROVENANCE_AUDIT_POLICY,
    PROVIDER_PATH_PROVENANCE_FUTURE_RUNTIME_CHECK,
    PROVIDER_PATH_PROVENANCE_VALIDATOR_FIXTURE,
)
CONSENT_READINESS_STATES = (
    CONSENT_READINESS_STATE_UNKNOWN,
    CONSENT_READINESS_STATE_UNAVAILABLE,
    CONSENT_READINESS_STATE_DISABLED,
    CONSENT_READINESS_STATE_NOT_REQUIRED_FOR_LOCAL_STATUS,
    CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_SETUP,
    CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_EXECUTION,
    CONSENT_READINESS_STATE_BLOCKED_BY_POLICY,
    CONSENT_READINESS_STATE_BLOCKED_BY_DATA_VISIBILITY,
    CONSENT_READINESS_STATE_BLOCKED_BY_AUDIT_REQUIREMENTS,
    CONSENT_READINESS_STATE_READY_FUTURE_GATED,
    CONSENT_READINESS_STATE_READY_BUT_NOT_COLLECTED,
    CONSENT_READINESS_STATE_DEGRADED,
)
CONSENT_REASON_CODES = (
    CONSENT_REASON_SETUP_REQUIRED,
    CONSENT_REASON_EXECUTION_REQUIRED,
    CONSENT_REASON_POLICY_BLOCKED,
    CONSENT_REASON_DATA_VISIBILITY_BLOCKED,
    CONSENT_REASON_AUDIT_REQUIREMENTS_BLOCKED,
    CONSENT_REASON_READY_BUT_NOT_COLLECTED,
)
CONSENT_PROVENANCE_SOURCES = (
    CONSENT_PROVENANCE_DEFAULT_CONFIG,
    CONSENT_PROVENANCE_PROVIDER_PATH_CONTRACT,
    CONSENT_PROVENANCE_DATA_VISIBILITY_CONTRACT,
    CONSENT_PROVENANCE_AUDIT_POLICY,
    CONSENT_PROVENANCE_FUTURE_COLLECTION,
)
_ACTIVATION_CONFIG_OMITTED = object()
_EXECUTION_CONFIG_OMITTED = object()
_PATH_CONSENT_CONFIG_OMITTED = object()
_SETUP_FOUNDATION_CONFIG_OMITTED = object()
_CONSENT_COLLECTION_CONFIG_OMITTED = object()
_CONSENT_CAPTURE_RECORD_OMITTED = object()
_DURABLE_CONSENT_RECORD_OMITTED = object()
_CONSENT_UX_INTENT_OMITTED = object()
_SETUP_COMPLETION_CONFIG_OMITTED = object()


@dataclass(frozen=True)
class AIProviderRuntimeConfigSnapshot:
    schema_version: str
    config_state: str
    selected_provider_id: str
    provider_configured: bool
    provider_available: bool
    consent_granted: bool
    capability_ready: bool
    config_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderReadinessConfigSnapshot:
    schema_version: str
    config_state: str
    provider_configured: bool
    consent_granted: bool
    capability_ready: bool
    manifest_available: bool
    manifest_valid: bool
    policy_allows_setup: bool
    future_provider_setup_approved: bool
    provider_ready: bool
    install_intent_requested: bool
    config_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderActivationConfigSnapshot:
    schema_version: str
    config_state: str
    future_activation_approved: bool
    adapter_available: bool
    safety_eval_complete: bool
    prompt_execution_approved: bool
    model_execution_approved: bool
    functional_ai_ready: bool
    config_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderExecutionReadinessConfigSnapshot:
    schema_version: str
    config_state: str
    provider_path_selected: bool
    provider_adapter_selected: bool
    prompt_acceptance_approved: bool
    prompt_routing_approved: bool
    model_execution_approved: bool
    provider_visible_data_approved: bool
    network_external_approved: bool
    consent_granted: bool
    safety_eval_complete: bool
    policy_allows_execution: bool
    execution_approved: bool
    functional_ai_release_ready: bool
    config_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderPathConsentReadinessConfigSnapshot:
    schema_version: str
    config_state: str
    provider_path_selected: bool
    provider_config_present: bool
    provider_config_valid: bool
    provider_profile_available: bool
    provider_available: bool
    setup_consent_ready: bool
    execution_consent_ready: bool
    data_visibility_approved: bool
    audit_ready: bool
    capability_ready: bool
    manifest_available: bool
    manifest_valid: bool
    safety_eval_complete: bool
    policy_allows_provider_path: bool
    setup_approved: bool
    execution_approved: bool
    future_execution_branch_ready: bool
    functional_ai_release_ready: bool
    config_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderSetupFoundationConfigSnapshot:
    schema_version: str
    config_state: str
    setup_entry_enabled: bool
    provider_profile_draft_present: bool
    provider_profile_draft_valid: bool
    provider_config_draft_present: bool
    provider_config_draft_valid: bool
    local_persistence_ready: bool
    validation_passed: bool
    setup_foundation_approved: bool
    setup_consent_ready: bool
    execution_consent_ready: bool
    config_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderConsentCollectionFoundationConfigSnapshot:
    schema_version: str
    config_state: str
    consent_capture_surface_enabled: bool
    setup_consent_capture_ready: bool
    execution_consent_capture_ready: bool
    data_visibility_review_ready: bool
    audit_envelope_ready: bool
    provenance_ready: bool
    local_persistence_ready: bool
    validation_passed: bool
    policy_allows_collection: bool
    consent_collection_approved: bool
    future_capture_branch_ready: bool
    config_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderConsentCaptureRecordSnapshot:
    schema_version: str
    record_state: str
    local_write_requested: bool
    setup_consent_granted: bool
    execution_consent_granted: bool
    revoked: bool
    reset_requested: bool
    record_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderDurableConsentRecordSnapshot:
    schema_version: str
    record_state: str
    record_valid: bool
    record_id: str
    provider_profile_id: str
    setup_consent_granted: bool
    execution_consent_granted: bool
    setup_consent_revoked: bool
    execution_consent_revoked: bool
    setup_consent_reset_requested: bool
    execution_consent_reset_requested: bool
    setup_consent_expired: bool
    execution_consent_expired: bool
    setup_consent_expires_at_utc: str
    execution_consent_expires_at_utc: str
    revoked: bool
    reset_requested: bool
    expired: bool
    expires_at_utc: str
    captured_at_utc: str
    updated_at_utc: str
    provenance: str
    audit_event_id: str
    storage_boundary: str
    migration_posture: str
    fail_closed_reason: str
    no_secrets: bool
    provider_payload_excluded: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "record_state": self.record_state,
            "record_valid": self.record_valid,
            "record_id": self.record_id,
            "provider_profile_id": self.provider_profile_id,
            "setup_consent_granted": self.setup_consent_granted,
            "execution_consent_granted": self.execution_consent_granted,
            "setup_consent_revoked": self.setup_consent_revoked,
            "execution_consent_revoked": self.execution_consent_revoked,
            "setup_consent_reset_requested": self.setup_consent_reset_requested,
            "execution_consent_reset_requested": (
                self.execution_consent_reset_requested
            ),
            "setup_consent_expired": self.setup_consent_expired,
            "execution_consent_expired": self.execution_consent_expired,
            "setup_consent_expires_at_utc": self.setup_consent_expires_at_utc,
            "execution_consent_expires_at_utc": (
                self.execution_consent_expires_at_utc
            ),
            "revoked": self.revoked,
            "reset_requested": self.reset_requested,
            "expired": self.expired,
            "expires_at_utc": self.expires_at_utc,
            "captured_at_utc": self.captured_at_utc,
            "updated_at_utc": self.updated_at_utc,
            "provenance": self.provenance,
            "audit_event_id": self.audit_event_id,
            "storage_boundary": self.storage_boundary,
            "migration_posture": self.migration_posture,
            "fail_closed_reason": self.fail_closed_reason,
            "no_secrets": self.no_secrets,
            "provider_payload_excluded": self.provider_payload_excluded,
        }


@dataclass(frozen=True)
class AIProviderConsentUxIntentSnapshot:
    schema_version: str
    setup_intent_selected: bool
    execution_intent_selected: bool
    revoke_intent_selected: bool
    reset_intent_selected: bool
    local_write_requested: bool
    surface_enabled: bool
    provenance: str

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "setup_intent_selected": self.setup_intent_selected,
            "execution_intent_selected": self.execution_intent_selected,
            "revoke_intent_selected": self.revoke_intent_selected,
            "reset_intent_selected": self.reset_intent_selected,
            "local_write_requested": self.local_write_requested,
            "surface_enabled": self.surface_enabled,
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class AIProviderSetupCompletionConfigSnapshot:
    schema_version: str
    config_state: str
    setup_completion_approved: bool
    provider_profile_finalized: bool
    provider_profile_valid: bool
    provider_config_finalized: bool
    provider_config_valid: bool
    no_secrets_validated: bool
    local_persistence_ready: bool
    validation_passed: bool
    reset_requested: bool
    future_sdk_handoff_ready: bool
    config_valid: bool
    provenance: str


@dataclass(frozen=True)
class AIProviderChoiceSnapshot:
    provider_id: str
    label: str
    provider_kind: str
    availability: str
    consent_state: str
    privacy_scope: str
    visible_status: str
    configuration_state: str
    configured: bool
    requires_consent: bool
    provider_visible_data: str
    external_calls: str

    def as_dict(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "label": self.label,
            "provider_kind": self.provider_kind,
            "availability": self.availability,
            "consent_state": self.consent_state,
            "privacy_scope": self.privacy_scope,
            "visible_status": self.visible_status,
            "configuration_state": self.configuration_state,
            "configured": self.configured,
            "requires_consent": self.requires_consent,
            "provider_visible_data": self.provider_visible_data,
            "external_calls": self.external_calls,
        }

    def as_renderer_payload(self) -> dict[str, object]:
        return {
            "providerId": self.provider_id,
            "label": self.label,
            "providerKind": self.provider_kind,
            "availability": self.availability,
            "consentState": self.consent_state,
            "privacyScope": self.privacy_scope,
            "visibleStatus": self.visible_status,
            "configurationState": self.configuration_state,
            "configured": self.configured,
            "requiresConsent": self.requires_consent,
            "providerVisibleData": self.provider_visible_data,
            "externalCalls": self.external_calls,
        }


@dataclass(frozen=True)
class AIFoundationReadinessSnapshot:
    slice_id: str
    label: str
    state: str
    visible_status: str
    proof_status: str
    blocked_work: str

    def as_dict(self) -> dict[str, str]:
        return {
            "slice_id": self.slice_id,
            "label": self.label,
            "state": self.state,
            "visible_status": self.visible_status,
            "proof_status": self.proof_status,
            "blocked_work": self.blocked_work,
        }

    def as_renderer_payload(self) -> dict[str, str]:
        return {
            "sliceId": self.slice_id,
            "label": self.label,
            "state": self.state,
            "visibleStatus": self.visible_status,
            "proofStatus": self.proof_status,
            "blockedWork": self.blocked_work,
        }


@dataclass(frozen=True)
class AIReadinessActionPermissionSnapshot:
    action: str
    permission: str
    label: str

    def as_dict(self) -> dict[str, str]:
        return {
            "action": self.action,
            "permission": self.permission,
            "label": self.label,
        }

    def as_renderer_payload(self) -> dict[str, str]:
        return {
            "action": self.action,
            "permission": self.permission,
            "label": self.label,
        }


@dataclass(frozen=True)
class AIProviderStateSnapshot:
    package_id: str
    slice_ids: tuple[str, ...]
    state_id: str
    mode: str
    availability: str
    provider_label: str
    provider_kind: str
    status_label: str
    disabled_reason: str
    selected_provider_id: str
    provider_selection_state: str
    provider_selection_label: str
    provider_configuration_state: str
    provider_configuration_label: str
    provider_registry_state: str
    provider_registry_label: str
    configured_provider_count: int
    available_provider_count: int
    hardware_capability_state: str
    hardware_capability_label: str
    gpu_capability_state: str
    gpu_capability_label: str
    cpu_fallback_state: str
    cpu_fallback_label: str
    power_state: str
    power_state_label: str
    thermal_guardrail_state: str
    thermal_guardrail_label: str
    model_workload_state: str
    model_workload_label: str
    capability_recommendation_state: str
    capability_recommendation_label: str
    hardware_detection_level: str
    hardware_detection_label: str
    capability_snapshot_policy: str
    capability_snapshot_source: str
    capability_snapshot_budget_label: str
    ram_readiness_state: str
    ram_readiness_label: str
    disk_readiness_state: str
    disk_readiness_label: str
    model_workload_metadata_state: str
    model_workload_metadata_label: str
    capability_pack_lifecycle_state: str
    capability_pack_lifecycle_label: str
    capability_pack_download_state: str
    capability_pack_download_label: str
    capability_pack_manifest_schema_version: str
    capability_pack_manifest_state: str
    capability_pack_source_type: str
    capability_pack_checksum_state: str
    capability_pack_signature_state: str
    capability_pack_compatibility_state: str
    capability_pack_disk_requirement: str
    capability_pack_ram_requirement: str
    capability_pack_gpu_requirement: str
    capability_pack_install_state: str
    capability_pack_update_state: str
    capability_pack_uninstall_state: str
    data_classification_state: str
    data_classification_label: str
    data_classification_schema_version: str
    provider_visible_data_guarantee: str
    memory_context_state: str
    memory_context_label: str
    memory_indexing_state: str
    retrieval_state: str
    learning_state: str
    persistence_state: str
    future_memory_eligibility_marker: str
    consent_envelope_state: str
    audit_envelope_state: str
    secret_boundary_state: str
    network_egress_state: str
    audit_secrets_state: str
    audit_secrets_label: str
    windows_resilience_state: str
    windows_resilience_label: str
    offline_degraded_state: str
    offline_degraded_label: str
    persona_core_voice_state: str
    persona_core_voice_label: str
    voice_runtime_state: str
    voice_runtime_label: str
    validation_proof_gate_state: str
    validation_proof_gate_label: str
    abuse_eval_state: str
    abuse_eval_label: str
    release_proof_gate_state: str
    release_proof_gate_label: str
    core_desktop_copy_contract_version: str
    core_desktop_runtime_state_contract: str
    disabled_prompt_behavior_contract: str
    golden_provider_state_fixtures: str
    validator_expansion_state: str
    contract_ready_marker: str
    ui_ready_marker: str
    validator_ready_marker: str
    future_implementation_gated_marker: str
    privacy_scope: str
    privacy_label: str
    provider_visible_data: str
    provider_visible_data_label: str
    provider_visible_data_detail: str
    provider_interaction_state: str
    provider_interaction_label: str
    provider_interaction_detail: str
    provider_consent_boundary_label: str
    provider_next_action_label: str
    local_storage: str
    consent_state: str
    consent_label: str
    interaction_affordance: str
    interaction_label: str
    interaction_disabled_reason: str
    no_provider_fallback_label: str
    prompt_acceptance: str
    external_calls: str
    model_state: str
    capability_pack_state: str
    source_truth: str
    runtime_state_schema_version: str
    runtime_state_category: str
    runtime_state_label: str
    runtime_reason_code: str
    runtime_reason_label: str
    runtime_config_schema_version: str
    runtime_config_state: str
    runtime_config_label: str
    runtime_config_migration: str
    runtime_config_valid: bool
    runtime_fail_closed: bool
    runtime_provenance: str
    runtime_provenance_label: str
    surface_role: str
    provider_options: tuple[AIProviderChoiceSnapshot, ...]
    foundation_readiness_items: tuple[AIFoundationReadinessSnapshot, ...]
    provider_readiness_state: str = PROVIDER_READINESS_STATE_SETUP_DISABLED
    provider_readiness_label: str = "Provider readiness: setup disabled"
    setup_eligibility_state: str = PROVIDER_SETUP_ELIGIBILITY_DISABLED
    setup_eligibility_label: str = "Setup eligibility: disabled"
    setup_blocker_state: str = PROVIDER_SETUP_BLOCKER_SETUP_DISABLED
    setup_blocker_label: str = "Setup blocker: future USER approval required"
    readiness_reason_code: str = PROVIDER_READINESS_REASON_DEFAULT_LOCAL_ONLY
    readiness_reason_label: str = "Readiness reason: local-only default"
    readiness_provenance: str = PROVIDER_READINESS_PROVENANCE_DEFAULT_CONFIG
    readiness_provenance_label: str = "Readiness provenance: default config"
    readiness_state_schema_version: str = PROVIDER_READINESS_STATE_SCHEMA_VERSION
    readiness_config_schema_version: str = PROVIDER_READINESS_CONFIG_SCHEMA_VERSION
    readiness_config_state: str = PROVIDER_READINESS_CONFIG_STATE_DEFAULT
    readiness_config_label: str = "Readiness config: safe default local-only"
    readiness_config_migration: str = PROVIDER_READINESS_CONFIG_MIGRATION_POSTURE
    readiness_config_valid: bool = True
    future_provider_gate_status: str = PROVIDER_FUTURE_GATE_STATUS_SETUP_REQUIRED
    future_provider_gate_label: str = "Future provider gate: USER approval required before setup"
    capability_pack_eligibility_state: str = CAPABILITY_PACK_ELIGIBILITY_BLOCKED
    capability_pack_eligibility_label: str = "Capability-pack eligibility: blocked"
    capability_pack_manifest_validity_state: str = CAPABILITY_PACK_MANIFEST_MISSING
    capability_pack_manifest_validity_label: str = "Capability manifest: missing"
    capability_pack_source_trust_state: str = CAPABILITY_PACK_SOURCE_TRUST_UNVERIFIED
    capability_pack_source_trust_label: str = "Capability-pack source trust: unverified"
    capability_pack_compatibility_posture_state: str = CAPABILITY_PACK_COMPATIBILITY_BLOCKED
    capability_pack_compatibility_posture_label: str = "Capability-pack compatibility: blocked"
    capability_pack_cpu_requirement_posture: str = CAPABILITY_PACK_REQUIREMENT_UNPROBED
    capability_pack_gpu_requirement_posture: str = CAPABILITY_PACK_REQUIREMENT_UNPROBED
    capability_pack_ram_requirement_posture: str = CAPABILITY_PACK_REQUIREMENT_UNPROBED
    capability_pack_disk_requirement_posture: str = CAPABILITY_PACK_REQUIREMENT_UNPROBED
    install_intent_state: str = CAPABILITY_PACK_INSTALL_INTENT_BLOCKED
    install_intent_label: str = "Install intent: blocked"
    capability_pack_download_blocked_reason: str = CAPABILITY_PACK_DOWNLOAD_BLOCKED_REASON
    capability_pack_install_blocked_reason: str = CAPABILITY_PACK_INSTALL_BLOCKED_REASON
    capability_pack_update_blocked_reason: str = CAPABILITY_PACK_UPDATE_BLOCKED_REASON
    capability_pack_uninstall_blocked_reason: str = CAPABILITY_PACK_UNINSTALL_BLOCKED_REASON
    lane_boundary_schema_version: str = LANE_BOUNDARY_SCHEMA_VERSION
    public_lane_boundary_state: str = PUBLIC_LANE_BOUNDARY_LOCAL_ASSIST_ONLY
    public_lane_boundary_label: str = "Public Edition: deterministic no-provider assist; provider-visible data none"
    developer_lane_boundary_state: str = DEVELOPER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED
    developer_lane_boundary_label: str = "Developer lane: gated; private setup not configured"
    owner_lane_boundary_state: str = OWNER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED
    owner_lane_boundary_label: str = "Owner lane: gated; private setup not configured"
    private_setup_boundary_state: str = PRIVATE_SETUP_BOUNDARY_BLOCKED
    private_setup_authorized: bool = False
    private_material_visible: bool = False
    owner_memory_enabled: bool = False
    owner_agents_enabled: bool = False
    action_permission_matrix: tuple[AIReadinessActionPermissionSnapshot, ...] = ()
    provider_activation_state: str = PROVIDER_ACTIVATION_STATE_UNAVAILABLE
    provider_activation_label: str = "Provider activation: unavailable"
    activation_eligibility_state: str = PROVIDER_ACTIVATION_ELIGIBILITY_UNAVAILABLE
    activation_eligibility_label: str = "Activation eligibility: unavailable"
    activation_blocker_state: str = PROVIDER_ACTIVATION_BLOCKER_READINESS_REQUIRED
    activation_blocker_label: str = "Activation blocker: readiness required"
    activation_reason_code: str = PROVIDER_ACTIVATION_REASON_DEFAULT_UNAVAILABLE
    activation_reason_label: str = "Activation reason: activation foundation only"
    activation_provenance: str = PROVIDER_ACTIVATION_PROVENANCE_DEFAULT_CONFIG
    activation_provenance_label: str = "Activation provenance: default config"
    activation_state_schema_version: str = PROVIDER_ACTIVATION_STATE_SCHEMA_VERSION
    activation_config_schema_version: str = PROVIDER_ACTIVATION_CONFIG_SCHEMA_VERSION
    activation_config_state: str = PROVIDER_ACTIVATION_CONFIG_STATE_DEFAULT
    activation_config_label: str = "Activation config: safe default local-only"
    activation_config_migration: str = PROVIDER_ACTIVATION_CONFIG_MIGRATION_POSTURE
    activation_config_valid: bool = True
    future_activation_gate_status: str = PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_REQUIRED
    future_activation_gate_label: str = "Future activation gate: USER approval required before activation"
    provider_adapter_posture: str = PROVIDER_ADAPTER_POSTURE_NULL_LOCAL
    provider_adapter_label: str = "Provider adapter: null local adapter"
    provider_adapter_kind: str = PROVIDER_ADAPTER_KIND_NULL
    provider_adapter_availability_state: str = PROVIDER_ADAPTER_AVAILABILITY_UNAVAILABLE
    provider_adapter_availability_label: str = "Adapter availability: unavailable"
    provider_adapter_execution_posture: str = PROVIDER_ADAPTER_EXECUTION_POSTURE_DISABLED
    provider_adapter_execution_label: str = "Adapter execution: disabled"
    provider_metadata_contract_version: str = PROVIDER_METADATA_CONTRACT_VERSION
    provider_config_envelope_version: str = PROVIDER_CONFIG_ENVELOPE_VERSION
    provider_activation_handoff_state: str = PROVIDER_ACTIVATION_HANDOFF_STATE_FUTURE_GATED
    provider_activation_handoff_label: str = "Provider activation handoff: future-gated"
    future_sdk_integration_boundary: str = PROVIDER_SDK_INTEGRATION_BOUNDARY_FUTURE_APPROVAL
    prompt_execution_gate_state: str = PROMPT_EXECUTION_GATE_DISABLED
    prompt_execution_gate_label: str = "Prompt execution gate: disabled"
    model_execution_gate_state: str = MODEL_EXECUTION_GATE_DISABLED
    model_execution_gate_label: str = "Model execution gate: disabled"
    provider_execution_gate_state: str = PROVIDER_EXECUTION_GATE_DISABLED
    provider_execution_gate_label: str = "Provider execution gate: disabled"
    readiness_gate_state: str = READINESS_GATE_BLOCKED
    consent_gate_state: str = CONSENT_GATE_REQUIRED
    capability_gate_state: str = CAPABILITY_GATE_BLOCKED
    manifest_gate_state: str = MANIFEST_GATE_BLOCKED
    adapter_gate_state: str = ADAPTER_GATE_NULL_LOCAL
    safety_eval_gate_state: str = SAFETY_EVAL_GATE_PENDING
    network_egress_gate_state: str = NETWORK_EGRESS_BLOCKED
    memory_indexing_gate_state: str = MEMORY_INDEXING_DISABLED
    voice_core_sync_gate_state: str = VOICE_CORE_SYNC_GATE_PENDING_APPROVAL
    version_jump_gate_state: str = VERSION_JUMP_GATE_PENDING_FUNCTIONAL_AI
    functional_ai_criteria_state: str = FUNCTIONAL_AI_CRITERIA_PENDING
    functional_ai_criteria_label: str = "Functional AI: criteria pending for v1.8.0-prebeta"
    v18_prebeta_readiness_state: str = V18_PREBETA_READINESS_PENDING
    v18_prebeta_readiness_label: str = "v1.8.0-prebeta readiness: pending functional AI proof"
    provider_execution_readiness_state: str = PROVIDER_EXECUTION_READINESS_STATE_UNAVAILABLE
    provider_execution_readiness_label: str = "Execution readiness: unavailable"
    prompt_execution_readiness_state: str = PROVIDER_EXECUTION_READINESS_STATE_DISABLED
    prompt_execution_readiness_label: str = "Prompt execution readiness: disabled"
    model_execution_readiness_state: str = PROVIDER_EXECUTION_READINESS_STATE_DISABLED
    model_execution_readiness_label: str = "Model execution readiness: disabled"
    execution_eligibility_state: str = PROVIDER_EXECUTION_ELIGIBILITY_UNAVAILABLE
    execution_eligibility_label: str = "Execution eligibility: unavailable"
    execution_blocker_state: str = PROVIDER_EXECUTION_BLOCKER_ACTIVATION_REQUIRED
    execution_blocker_label: str = "Execution blocker: activation required"
    execution_reason_code: str = PROVIDER_EXECUTION_REASON_DEFAULT_UNAVAILABLE
    execution_reason_label: str = "Execution reason: execution readiness gates only"
    execution_provenance: str = PROVIDER_EXECUTION_PROVENANCE_DEFAULT_CONFIG
    execution_provenance_label: str = "Execution provenance: default config"
    execution_state_schema_version: str = PROVIDER_EXECUTION_READINESS_STATE_SCHEMA_VERSION
    execution_config_schema_version: str = PROVIDER_EXECUTION_READINESS_CONFIG_SCHEMA_VERSION
    execution_config_state: str = PROVIDER_EXECUTION_CONFIG_STATE_DEFAULT
    execution_config_label: str = "Execution config: safe default local-only"
    execution_config_migration: str = PROVIDER_EXECUTION_READINESS_CONFIG_MIGRATION_POSTURE
    execution_config_valid: bool = True
    execution_approval_status: str = PROVIDER_EXECUTION_APPROVAL_STATUS_MISSING
    execution_approval_label: str = "Execution approval: USER approval missing"
    provider_path_status: str = PROVIDER_PATH_STATUS_NOT_SELECTED
    provider_path_label: str = "Provider path: not selected"
    provider_selection_posture: str = PROVIDER_SELECTION_POSTURE_PENDING_APPROVAL
    provider_selection_posture_label: str = "Provider selection: pending USER approval"
    adapter_selection_posture: str = ADAPTER_SELECTION_POSTURE_NULL_LOCAL
    adapter_selection_posture_label: str = "Adapter selection: null local fallback"
    prompt_acceptance_gate_state: str = PROMPT_ACCEPTANCE_GATE_DISABLED
    prompt_acceptance_gate_label: str = "Prompt acceptance gate: disabled"
    prompt_routing_gate_state: str = PROMPT_ROUTING_GATE_DISABLED
    prompt_routing_gate_label: str = "Prompt routing gate: disabled"
    prompt_send_posture: str = PROMPT_SEND_POSTURE_DISABLED
    prompt_send_label: str = "Prompt send: disabled"
    local_action_result_schema_version: str = LOCAL_ACTION_RESULT_SCHEMA_VERSION
    local_action_result_state: str = LOCAL_ACTION_RESULT_IDLE
    local_action_result_label: str = "No-provider check: waiting for local action"
    local_action_result_detail: str = "Run the check to produce a deterministic no-provider result."
    local_action_result_provider_visible_data: str = "none"
    local_action_result_sent_to_provider: bool = False
    local_action_result_can_accept_prompts: bool = False
    local_action_result_prompt_send_posture: str = PROMPT_SEND_POSTURE_DISABLED
    local_action_result_network_egress_state: str = NETWORK_EGRESS_BLOCKED
    local_action_result_memory_indexing_state: str = MEMORY_INDEXING_DISABLED
    ai_control_center_diagnostics_schema_version: str = AI_CONTROL_CENTER_DIAGNOSTICS_SCHEMA_VERSION
    ai_control_center_diagnostic_state: str = AI_CONTROL_CENTER_DIAGNOSTIC_NO_PROVIDER_FAIL_CLOSED
    ai_control_center_diagnostic_label: str = "No provider configured; fail-closed"
    ai_control_center_provider_boundary_label: str = "Provider boundary: blocked"
    ai_control_center_provider_boundary_detail: str = "Provider, model, prompt, memory, downloads, and network paths remain disabled."
    ai_control_center_blocked_action_label: str = "Prompt/provider/model action blocked"
    ai_control_center_blocked_action_detail: str = "No provider action can run until a future USER-approved provider path exists."
    ai_control_center_unavailable_capability_label: str = "Capability packs unavailable"
    ai_control_center_unavailable_capability_detail: str = "Downloads, install, update, and uninstall execution remain blocked."
    ai_control_center_recovery_label: str = "Retry local check only"
    ai_control_center_recovery_detail: str = "Recovery remains local-only; provider setup and execution stay future-gated."
    ai_control_center_degraded_path_label: str = "Local guidance only"
    ai_control_center_degraded_path_detail: str = "The degraded no-provider path reports status without accepting prompts or sending data."
    ai_control_center_state_taxonomy: tuple[dict[str, str], ...] = ()
    local_ai_readiness_report: dict[str, object] | None = None
    model_execution_status: str = MODEL_EXECUTION_STATUS_DISABLED
    model_execution_status_label: str = "Model execution status: disabled"
    model_workload_readiness_posture: str = MODEL_WORKLOAD_READINESS_DISABLED
    model_workload_readiness_label: str = "Model workload readiness: disabled"
    provider_visible_data_execution_posture: str = PROVIDER_VISIBLE_DATA_EXECUTION_NONE
    provider_visible_data_execution_label: str = "Provider-visible execution data: none"
    external_call_readiness_state: str = EXTERNAL_CALL_READINESS_BLOCKED
    external_call_readiness_label: str = "External call readiness: blocked"
    safety_eval_readiness_state: str = SAFETY_EVAL_READINESS_PENDING
    safety_eval_readiness_label: str = "Safety/eval readiness: pending"
    data_classification_gate_state: str = DATA_CLASSIFICATION_GATE_LOCAL_ONLY
    data_classification_gate_label: str = "Data classification gate: local-only"
    execution_proof_marker: str = EXECUTION_PROOF_MARKER_PENDING
    future_execution_validation_marker: str = FUTURE_EXECUTION_VALIDATION_MARKER
    functional_ai_release_gate_state: str = FUNCTIONAL_AI_RELEASE_GATE_PENDING
    functional_ai_release_gate_label: str = "Functional-AI release gate: pending"
    v18_release_gate_state: str = V18_RELEASE_GATE_PENDING_FUNCTIONAL_AI
    v18_release_gate_label: str = "v1.8.0-prebeta release gate: pending functional AI proof"
    provider_path_readiness_state: str = PROVIDER_PATH_READINESS_STATE_UNAVAILABLE
    provider_path_readiness_label: str = "Provider path readiness: unavailable"
    provider_path_eligibility_state: str = PROVIDER_PATH_ELIGIBILITY_UNAVAILABLE
    provider_path_eligibility_label: str = "Provider path eligibility: unavailable"
    provider_path_blocker_state: str = PROVIDER_PATH_BLOCKER_EXECUTION_READINESS_REQUIRED
    provider_path_blocker_label: str = "Provider path blocker: execution readiness required"
    provider_path_reason_code: str = PROVIDER_PATH_REASON_DEFAULT_UNAVAILABLE
    provider_path_reason_label: str = "Provider path reason: readiness only"
    provider_path_provenance: str = PROVIDER_PATH_PROVENANCE_DEFAULT_CONFIG
    provider_path_provenance_label: str = "Provider path provenance: default config"
    provider_path_state_schema_version: str = PROVIDER_PATH_READINESS_STATE_SCHEMA_VERSION
    provider_path_config_schema_version: str = PROVIDER_PATH_READINESS_CONFIG_SCHEMA_VERSION
    provider_path_config_state: str = PROVIDER_PATH_CONFIG_STATE_DEFAULT
    provider_path_config_label: str = "Provider path config: safe default local-only"
    provider_path_config_migration: str = PROVIDER_PATH_READINESS_CONFIG_MIGRATION_POSTURE
    provider_path_config_valid: bool = True
    provider_path_approval_status: str = PROVIDER_PATH_APPROVAL_STATUS_MISSING
    provider_path_approval_label: str = "Provider path approval: USER approval missing"
    provider_profile_id: str = PROVIDER_PROFILE_ID_LOCAL_NULL
    provider_profile_kind: str = PROVIDER_PROFILE_KIND_NULL_LOCAL
    provider_profile_display_name: str = "Local/null provider profile"
    provider_profile_source: str = PROVIDER_PROFILE_SOURCE_LOCAL_SCAFFOLD
    provider_profile_metadata_contract_version: str = PROVIDER_PROFILE_METADATA_CONTRACT_VERSION
    provider_profile_available: bool = False
    provider_sdk_requirement_posture: str = PROVIDER_SDK_REQUIREMENT_PENDING_APPROVAL
    provider_network_requirement_posture: str = PROVIDER_NETWORK_REQUIREMENT_BLOCKED
    provider_config_status: str = PROVIDER_CONFIG_ENVELOPE_STATUS_MISSING
    provider_availability_posture: str = PROVIDER_AVAILABILITY_UNAVAILABLE
    provider_setup_approval_status: str = PROVIDER_SETUP_APPROVAL_STATUS_MISSING
    provider_execution_approval_status: str = PROVIDER_EXECUTION_APPROVAL_STATUS_PROVIDER_PATH_MISSING
    provider_visible_data_scope: str = PROVIDER_VISIBLE_DATA_REQUIREMENT_NONE
    local_null_provider_fallback_status: str = LOCAL_NULL_PROVIDER_FALLBACK_ACTIVE
    future_sdk_handoff_marker: str = FUTURE_SDK_HANDOFF_MARKER
    future_provider_setup_handoff_marker: str = FUTURE_PROVIDER_SETUP_HANDOFF_MARKER
    consent_readiness_state: str = CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_SETUP
    consent_readiness_label: str = "Consent readiness: required before provider setup"
    consent_state_schema_version: str = CONSENT_READINESS_STATE_SCHEMA_VERSION
    consent_config_schema_version: str = CONSENT_READINESS_CONFIG_SCHEMA_VERSION
    consent_config_migration: str = CONSENT_READINESS_CONFIG_MIGRATION_POSTURE
    setup_consent_state: str = CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_SETUP
    setup_consent_label: str = "Setup consent: required before provider setup"
    setup_consent_blocker_state: str = CONSENT_BLOCKER_SETUP_REQUIRED
    setup_consent_blocker_label: str = "Setup consent blocker: consent collection not approved"
    setup_consent_reason_code: str = CONSENT_REASON_SETUP_REQUIRED
    setup_consent_reason_label: str = "Setup consent reason: required before provider setup"
    setup_consent_provenance: str = CONSENT_PROVENANCE_PROVIDER_PATH_CONTRACT
    setup_consent_provenance_label: str = "Setup consent provenance: provider path contract"
    setup_consent_handoff_state: str = SETUP_CONSENT_HANDOFF_FUTURE_GATED
    setup_consent_handoff_label: str = "Setup consent handoff: future-gated"
    execution_consent_state: str = CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_EXECUTION
    execution_consent_label: str = "Execution consent: required before prompt/model execution"
    execution_consent_blocker_state: str = CONSENT_BLOCKER_EXECUTION_REQUIRED
    execution_consent_blocker_label: str = "Execution consent blocker: consent collection not approved"
    execution_consent_reason_code: str = CONSENT_REASON_EXECUTION_REQUIRED
    execution_consent_reason_label: str = "Execution consent reason: required before provider execution"
    execution_consent_provenance: str = CONSENT_PROVENANCE_PROVIDER_PATH_CONTRACT
    execution_consent_provenance_label: str = "Execution consent provenance: provider path contract"
    execution_consent_handoff_state: str = EXECUTION_CONSENT_HANDOFF_FUTURE_GATED
    execution_consent_handoff_label: str = "Execution consent handoff: future-gated"
    provider_visible_data_requirement_state: str = PROVIDER_VISIBLE_DATA_REQUIREMENT_NONE
    provider_visible_data_requirement_label: str = "Provider-visible data requirement: none"
    data_classification_posture_state: str = DATA_CLASSIFICATION_POSTURE_LOCAL_ONLY
    data_classification_posture_label: str = "Data classification posture: local-only"
    audit_envelope_posture_state: str = AUDIT_ENVELOPE_POSTURE_PLANNED
    audit_envelope_posture_label: str = "Audit envelope posture: planned; no collection"
    local_only_status_posture: str = LOCAL_ONLY_STATUS_POSTURE_ACTIVE
    local_only_status_label: str = "Local-only status: active"
    provider_setup_future_gated_posture: str = PROVIDER_SETUP_FUTURE_GATED_POSTURE
    provider_setup_future_gated_label: str = "Provider setup: future-gated"
    provider_execution_future_gated_posture: str = PROVIDER_EXECUTION_FUTURE_GATED_POSTURE
    provider_execution_future_gated_label: str = "Provider execution: disabled; future-gated"
    provider_path_gate_state: str = PROVIDER_PATH_GATE_BLOCKED
    provider_config_gate_state: str = PROVIDER_CONFIG_GATE_BLOCKED
    setup_consent_gate_state: str = SETUP_CONSENT_GATE_REQUIRED
    execution_consent_gate_state: str = EXECUTION_CONSENT_GATE_REQUIRED
    provider_visible_data_gate_state: str = PROVIDER_VISIBLE_DATA_GATE_NONE
    audit_gate_state: str = AUDIT_GATE_PLANNED
    setup_flow_readiness_state: str = SETUP_FLOW_STATE_UNAVAILABLE
    setup_flow_readiness_label: str = "Setup flow readiness: unavailable"
    setup_flow_eligibility_state: str = SETUP_FLOW_ELIGIBILITY_UNAVAILABLE
    setup_flow_eligibility_label: str = "Setup flow eligibility: unavailable"
    setup_flow_blocker_state: str = SETUP_FLOW_BLOCKER_PROVIDER_PATH_REQUIRED
    setup_flow_blocker_label: str = "Setup flow blocker: provider path readiness required"
    setup_flow_reason_code: str = SETUP_FLOW_REASON_DEFAULT_UNAVAILABLE
    setup_flow_reason_label: str = "Setup flow reason: setup readiness is local-only"
    setup_flow_provenance: str = SETUP_FLOW_PROVENANCE_PROVIDER_PATH
    setup_flow_provenance_label: str = "Setup flow provenance: provider path readiness state"
    setup_flow_state_schema_version: str = SETUP_FLOW_READINESS_STATE_SCHEMA_VERSION
    setup_flow_config_schema_version: str = SETUP_FLOW_READINESS_CONFIG_SCHEMA_VERSION
    setup_flow_config_state: str = PROVIDER_PATH_CONFIG_STATE_DEFAULT
    setup_flow_config_label: str = "Setup flow config: safe default local-only"
    setup_flow_config_migration: str = SETUP_FLOW_READINESS_CONFIG_MIGRATION_POSTURE
    setup_flow_config_valid: bool = True
    setup_flow_approval_status: str = SETUP_FLOW_APPROVAL_STATUS_MISSING
    setup_flow_approval_label: str = "Setup flow approval: USER approval missing"
    provider_setup_handoff_posture: str = PROVIDER_SETUP_HANDOFF_FUTURE_GATED
    provider_setup_handoff_label: str = "Provider setup handoff: future-gated"
    provider_consent_handoff_posture: str = PROVIDER_CONSENT_HANDOFF_FUTURE_GATED
    provider_consent_handoff_label: str = "Provider consent handoff: future-gated"
    provider_path_handoff_posture: str = PROVIDER_PATH_HANDOFF_FUTURE_GATED
    provider_path_handoff_label: str = "Provider path handoff: future-gated"
    consent_flow_readiness_state: str = CONSENT_FLOW_STATE_REQUIRED_FOR_SETUP
    consent_flow_readiness_label: str = "Consent flow readiness: required before setup"
    consent_flow_eligibility_state: str = CONSENT_FLOW_ELIGIBILITY_REQUIRED
    consent_flow_eligibility_label: str = "Consent flow eligibility: consent required"
    consent_flow_blocker_state: str = CONSENT_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED
    consent_flow_blocker_label: str = "Consent flow blocker: setup consent required"
    consent_flow_reason_code: str = CONSENT_FLOW_REASON_SETUP_REQUIRED
    consent_flow_reason_label: str = "Consent flow reason: setup consent required"
    consent_flow_provenance: str = CONSENT_FLOW_PROVENANCE_SETUP_CONSENT
    consent_flow_provenance_label: str = "Consent flow provenance: setup consent state"
    consent_flow_state_schema_version: str = CONSENT_FLOW_READINESS_STATE_SCHEMA_VERSION
    consent_flow_config_schema_version: str = CONSENT_FLOW_READINESS_CONFIG_SCHEMA_VERSION
    consent_flow_config_state: str = PROVIDER_PATH_CONFIG_STATE_DEFAULT
    consent_flow_config_label: str = "Consent flow config: safe default local-only"
    consent_flow_config_migration: str = CONSENT_FLOW_READINESS_CONFIG_MIGRATION_POSTURE
    consent_flow_config_valid: bool = True
    consent_flow_approval_status: str = CONSENT_FLOW_APPROVAL_STATUS_MISSING
    consent_flow_approval_label: str = "Consent flow approval: USER approval missing"
    consent_collection_posture: str = CONSENT_COLLECTION_POSTURE_PENDING_APPROVAL
    consent_collection_label: str = "Consent collection: pending USER approval"
    data_visibility_consent_posture: str = DATA_VISIBILITY_CONSENT_POSTURE_NONE_REQUIRED
    data_visibility_consent_label: str = "Data visibility consent: none required while provider-visible data is none"
    setup_flow_gate_state: str = SETUP_FLOW_GATE_BLOCKED
    consent_flow_gate_state: str = CONSENT_FLOW_GATE_REQUIRED
    setup_approval_gate_state: str = SETUP_APPROVAL_GATE_MISSING
    execution_approval_gate_state: str = EXECUTION_APPROVAL_GATE_MISSING
    desktop_ai_owned_readiness_display_state: str = AI_PROVIDER_STATUS_DISPLAY_SUPPRESSED
    desktop_ai_owned_readiness_display_label: str = "Desktop AI-owned readiness display: suppressed by default"
    provider_setup_contract_readiness_state: str = SETUP_CONTRACT_STATE_UNAVAILABLE
    provider_setup_contract_readiness_label: str = "Setup contract readiness: unavailable"
    provider_setup_contract_eligibility_state: str = SETUP_CONTRACT_ELIGIBILITY_UNAVAILABLE
    provider_setup_contract_eligibility_label: str = "Setup contract eligibility: unavailable"
    provider_setup_contract_blocker_state: str = SETUP_CONTRACT_BLOCKER_PROVIDER_PATH_REQUIRED
    provider_setup_contract_blocker_label: str = "Setup contract blocker: provider path readiness required"
    provider_setup_contract_reason_code: str = SETUP_CONTRACT_REASON_DEFAULT_UNAVAILABLE
    provider_setup_contract_reason_label: str = "Setup contract reason: setup contract is local-only"
    provider_setup_contract_provenance: str = SETUP_CONTRACT_PROVENANCE_SETUP_FLOW
    provider_setup_contract_provenance_label: str = "Setup contract provenance: setup flow readiness state"
    provider_setup_contract_state_schema_version: str = SETUP_CONTRACT_READINESS_STATE_SCHEMA_VERSION
    provider_setup_contract_config_schema_version: str = SETUP_CONTRACT_READINESS_CONFIG_SCHEMA_VERSION
    provider_setup_contract_config_state: str = PROVIDER_PATH_CONFIG_STATE_DEFAULT
    provider_setup_contract_config_label: str = "Setup contract config: safe default local-only"
    provider_setup_contract_config_migration: str = SETUP_CONTRACT_READINESS_CONFIG_MIGRATION_POSTURE
    provider_setup_contract_config_valid: bool = True
    provider_setup_contract_approval_status: str = SETUP_CONTRACT_APPROVAL_STATUS_MISSING
    provider_setup_contract_approval_label: str = "Setup contract approval: USER approval missing"
    provider_setup_contract_gate_state: str = SETUP_CONTRACT_GATE_BLOCKED
    provider_profile_gate_state: str = PROVIDER_PROFILE_GATE_BLOCKED
    capability_gate_state: str = CAPABILITY_GATE_BLOCKED
    manifest_gate_state: str = MANIFEST_GATE_BLOCKED
    safety_eval_gate_state: str = SAFETY_EVAL_GATE_BLOCKED
    network_gate_state: str = NETWORK_GATE_BLOCKED
    memory_indexing_gate_state: str = MEMORY_INDEXING_GATE_BLOCKED
    voice_core_sync_gate_state: str = VOICE_CORE_SYNC_GATE_BLOCKED
    version_jump_gate_state: str = VERSION_JUMP_GATE_PENDING
    provider_profile_required_fields: tuple[str, ...] = (
        "provider_id",
        "provider_kind",
        "display_name",
        "source",
        "metadata_contract_version",
    )
    provider_config_required_fields: tuple[str, ...] = (
        "config_status",
        "sdk_requirement",
        "network_requirement",
        "setup_approval",
        "execution_approval",
    )
    provider_setup_prerequisite_posture: str = PROVIDER_SETUP_PREREQUISITE_POSTURE_LOCAL_ONLY
    provider_setup_validation_posture: str = PROVIDER_SETUP_VALIDATION_POSTURE_STATIC
    provider_setup_ui_proof_posture: str = PROVIDER_SETUP_UI_PROOF_POSTURE_STATUS_ONLY
    future_setup_branch_handoff_state: str = FUTURE_SETUP_BRANCH_HANDOFF_READY
    provider_setup_contract_fold_down_posture: str = PROVIDER_SETUP_CONTRACT_FOLD_DOWN_READY
    provider_setup_foundation_state: str = SETUP_FOUNDATION_STATE_UNAVAILABLE
    provider_setup_foundation_label: str = "Setup implementation foundation: unavailable"
    provider_setup_foundation_eligibility_state: str = SETUP_FOUNDATION_ELIGIBILITY_UNAVAILABLE
    provider_setup_foundation_eligibility_label: str = "Setup foundation eligibility: unavailable"
    provider_setup_foundation_blocker_state: str = SETUP_FOUNDATION_BLOCKER_SETUP_CONTRACT_REQUIRED
    provider_setup_foundation_blocker_label: str = (
        "Setup foundation blocker: setup contract readiness required"
    )
    provider_setup_foundation_reason_code: str = SETUP_FOUNDATION_REASON_DEFAULT_UNAVAILABLE
    provider_setup_foundation_reason_label: str = "Setup foundation reason: local-only safe default"
    provider_setup_foundation_provenance: str = SETUP_FOUNDATION_PROVENANCE_SETUP_CONTRACT
    provider_setup_foundation_provenance_label: str = (
        "Setup foundation provenance: provider setup contract state"
    )
    provider_setup_foundation_state_schema_version: str = SETUP_FOUNDATION_STATE_SCHEMA_VERSION
    provider_setup_foundation_config_schema_version: str = SETUP_FOUNDATION_CONFIG_SCHEMA_VERSION
    provider_setup_foundation_config_state: str = PROVIDER_PATH_CONFIG_STATE_DEFAULT
    provider_setup_foundation_config_label: str = (
        "Setup foundation config: safe default local-only"
    )
    provider_setup_foundation_config_migration: str = SETUP_FOUNDATION_CONFIG_MIGRATION_POSTURE
    provider_setup_foundation_config_valid: bool = True
    provider_setup_foundation_setup_entry_state: str = SETUP_FOUNDATION_SETUP_ENTRY_DISABLED
    provider_setup_foundation_setup_entry_label: str = (
        "Setup entry point: disabled until USER-approved setup work"
    )
    provider_setup_foundation_profile_draft_status: str = SETUP_FOUNDATION_PROFILE_DRAFT_MISSING
    provider_setup_foundation_profile_draft_label: str = (
        "Provider profile draft: missing local-only draft"
    )
    provider_setup_foundation_config_draft_status: str = SETUP_FOUNDATION_CONFIG_DRAFT_MISSING
    provider_setup_foundation_config_draft_label: str = (
        "Provider config draft: missing local-only draft"
    )
    provider_setup_foundation_validation_status: str = SETUP_FOUNDATION_VALIDATION_FAIL_CLOSED
    provider_setup_foundation_validation_label: str = (
        "Setup foundation validation: fail-closed"
    )
    provider_setup_foundation_persistence_status: str = SETUP_FOUNDATION_PERSISTENCE_DISABLED
    provider_setup_foundation_persistence_label: str = (
        "Setup foundation persistence: disabled; no provider credentials stored"
    )
    provider_setup_foundation_approval_status: str = SETUP_FOUNDATION_APPROVAL_STATUS_MISSING
    provider_setup_foundation_approval_label: str = "Setup foundation approval: USER approval missing"
    provider_setup_foundation_gate_state: str = SETUP_FOUNDATION_GATE_BLOCKED
    local_null_provider_fallback_proof: str = LOCAL_NULL_PROVIDER_FALLBACK_PROOF
    provider_setup_implementation_handoff_state: str = FUTURE_PROVIDER_SETUP_IMPLEMENTATION_HANDOFF_READY
    provider_setup_implementation_fold_down_posture: str = PROVIDER_SETUP_IMPLEMENTATION_FOLD_DOWN_READY
    consent_collection_foundation_state: str = CONSENT_COLLECTION_STATE_UNAVAILABLE
    consent_collection_foundation_label: str = "Consent collection foundation: unavailable"
    consent_collection_eligibility_state: str = CONSENT_COLLECTION_ELIGIBILITY_UNAVAILABLE
    consent_collection_eligibility_label: str = "Consent collection eligibility: unavailable"
    consent_collection_blocker_state: str = CONSENT_COLLECTION_BLOCKER_CONSENT_FLOW_REQUIRED
    consent_collection_blocker_label: str = (
        "Consent collection blocker: consent flow readiness required"
    )
    consent_collection_reason_code: str = CONSENT_COLLECTION_REASON_DEFAULT_UNAVAILABLE
    consent_collection_reason_label: str = (
        "Consent collection reason: local-only safe default"
    )
    consent_collection_provenance: str = CONSENT_COLLECTION_PROVENANCE_CONSENT_FLOW
    consent_collection_provenance_label: str = (
        "Consent collection provenance: consent flow readiness state"
    )
    consent_collection_state_schema_version: str = (
        CONSENT_COLLECTION_FOUNDATION_STATE_SCHEMA_VERSION
    )
    consent_collection_config_schema_version: str = (
        CONSENT_COLLECTION_FOUNDATION_CONFIG_SCHEMA_VERSION
    )
    consent_collection_config_state: str = PROVIDER_PATH_CONFIG_STATE_DEFAULT
    consent_collection_config_label: str = (
        "Consent collection config: safe default local-only"
    )
    consent_collection_config_migration: str = (
        CONSENT_COLLECTION_FOUNDATION_CONFIG_MIGRATION_POSTURE
    )
    consent_collection_config_valid: bool = True
    consent_collection_approval_status: str = CONSENT_COLLECTION_APPROVAL_STATUS_MISSING
    consent_collection_approval_label: str = (
        "Consent collection approval: USER approval missing"
    )
    consent_collection_gate_state: str = CONSENT_COLLECTION_GATE_BLOCKED
    consent_capture_surface_state: str = CONSENT_COLLECTION_CAPTURE_SURFACE_DISABLED
    consent_capture_surface_label: str = (
        "Consent capture surface: disabled until USER-approved consent work"
    )
    setup_consent_capture_status: str = CONSENT_COLLECTION_CAPTURE_SETUP_REQUIRED
    setup_consent_capture_label: str = "Setup consent capture: required"
    execution_consent_capture_status: str = CONSENT_COLLECTION_CAPTURE_EXECUTION_REQUIRED
    execution_consent_capture_label: str = "Execution consent capture: required"
    consent_data_visibility_review_status: str = (
        CONSENT_COLLECTION_DATA_VISIBILITY_REVIEW_REQUIRED
    )
    consent_data_visibility_review_label: str = (
        "Consent data visibility review: required before capture"
    )
    consent_audit_envelope_status: str = CONSENT_COLLECTION_AUDIT_ENVELOPE_REQUIRED
    consent_audit_envelope_label: str = (
        "Consent audit envelope: required before capture"
    )
    consent_provenance_status: str = CONSENT_COLLECTION_PROVENANCE_REQUIRED
    consent_provenance_label: str = "Consent provenance: required before capture"
    consent_persistence_status: str = CONSENT_COLLECTION_PERSISTENCE_DISABLED
    consent_persistence_label: str = "Consent persistence: disabled; no consent stored"
    consent_collection_validation_status: str = CONSENT_COLLECTION_VALIDATION_FAIL_CLOSED
    consent_collection_validation_label: str = (
        "Consent collection validation: fail-closed"
    )
    consent_capture_transition_schema_version: str = CONSENT_CAPTURE_TRANSITION_SCHEMA_VERSION
    consent_capture_local_record_schema_version: str = CONSENT_CAPTURE_LOCAL_RECORD_SCHEMA_VERSION
    consent_capture_state: str = CONSENT_CAPTURE_STATE_NOT_REQUESTED
    consent_capture_label: str = "Consent capture: not requested"
    consent_capture_record_state: str = CONSENT_CAPTURE_RECORD_STATE_MISSING
    consent_capture_record_valid: bool = False
    consent_capture_local_write_requested: bool = False
    consent_capture_write_status: str = CONSENT_CAPTURE_WRITE_STATUS_BLOCKED
    consent_capture_write_label: str = "Consent write path: blocked"
    consent_capture_write_blocker: str = CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_MISSING
    consent_capture_write_reason: str = CONSENT_CAPTURE_WRITE_REASON_RECORD_MISSING
    consent_capture_provenance: str = CONSENT_CAPTURE_PROVENANCE_COLLECTION_STATE
    setup_consent_captured: bool = False
    execution_consent_captured: bool = False
    consent_capture_local_snapshot_status: str = CONSENT_CAPTURE_LOCAL_SNAPSHOT_STATUS_EMPTY
    consent_capture_durable_persistence_status: str = (
        CONSENT_CAPTURE_DURABLE_PERSISTENCE_DEFERRED
    )
    consent_record_storage_boundary_schema_version: str = (
        CONSENT_RECORD_STORAGE_BOUNDARY_SCHEMA_VERSION
    )
    consent_record_storage_boundary_state: str = (
        CONSENT_RECORD_STORAGE_BOUNDARY_LOCAL_SNAPSHOT_ONLY
    )
    consent_record_storage_boundary_label: str = (
        "Consent record storage boundary: local snapshot only"
    )
    consent_record_durable_storage_state: str = CONSENT_RECORD_DURABLE_STORAGE_DEFERRED
    consent_record_durable_storage_label: str = (
        "Consent record durable storage: deferred"
    )
    consent_record_revocation_model_state: str = CONSENT_RECORD_REVOCATION_MODEL_LOCAL_ONLY
    consent_record_revocation_model_label: str = (
        "Consent revocation model: local-only snapshot revocation"
    )
    consent_record_reset_model_state: str = CONSENT_RECORD_RESET_MODEL_LOCAL_ONLY
    consent_record_reset_model_label: str = (
        "Consent reset model: local-only snapshot reset"
    )
    consent_record_no_secrets_posture: str = CONSENT_RECORD_NO_SECRETS_POSTURE_READY
    consent_record_provider_payload_posture: str = CONSENT_RECORD_PROVIDER_PAYLOAD_EXCLUDED
    consent_capture_audit_schema_version: str = CONSENT_CAPTURE_AUDIT_SCHEMA_VERSION
    consent_capture_audit_status: str = CONSENT_CAPTURE_AUDIT_STATUS_BLOCKED
    consent_capture_audit_label: str = "Consent capture audit: blocked until local proof"
    setup_execution_consent_separation_state: str = (
        CONSENT_CAPTURE_SETUP_EXECUTION_SEPARATION_READY
    )
    setup_execution_consent_separation_label: str = (
        "Setup and execution consent remain separated"
    )
    consent_capture_ui_status_proof_state: str = (
        CONSENT_CAPTURE_UI_STATUS_PROOF_HIDDEN_TELEMETRY
    )
    consent_capture_ui_status_proof_label: str = (
        "Consent capture UI proof: hidden telemetry only"
    )
    consent_capture_desktop_display_state: str = CONSENT_CAPTURE_DESKTOP_DISPLAY_SUPPRESSED
    consent_capture_provider_setup_handoff_state: str = (
        CONSENT_CAPTURE_PROVIDER_SETUP_HANDOFF_READY
    )
    consent_capture_functional_ai_criteria_state: str = (
        CONSENT_CAPTURE_FUNCTIONAL_AI_CRITERIA_PENDING
    )
    consent_capture_v18_continuation_state: str = (
        CONSENT_CAPTURE_V18_CONTINUATION_PENDING
    )
    consent_capture_provider_visible_data: str = "none"
    consent_capture_sent_to_provider: bool = False
    consent_capture_can_accept_prompts: bool = False
    consent_capture_prompt_execution_state: str = PROMPT_EXECUTION_GATE_DISABLED
    consent_capture_network_egress_state: str = NETWORK_EGRESS_BLOCKED
    consent_capture_memory_state: str = MEMORY_INDEXING_DISABLED
    consent_capture_voice_state: str = VOICE_RUNTIME_DISABLED
    durable_consent_record_schema_version: str = CONSENT_DURABLE_RECORD_SCHEMA_VERSION
    durable_consent_storage_boundary_schema_version: str = (
        CONSENT_DURABLE_STORAGE_BOUNDARY_SCHEMA_VERSION
    )
    durable_consent_record_state: str = CONSENT_DURABLE_RECORD_STATE_MISSING
    durable_consent_record_valid: bool = False
    durable_consent_record_id: str = ""
    durable_consent_provider_profile_id: str = PROVIDER_PROFILE_ID_LOCAL_NULL
    durable_setup_consent_granted: bool = False
    durable_execution_consent_granted: bool = False
    durable_consent_revoked: bool = False
    durable_consent_reset_requested: bool = False
    durable_consent_expired: bool = False
    durable_consent_fail_closed_reason: str = CONSENT_DURABLE_FAIL_REASON_MISSING
    durable_consent_provenance: str = CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD
    durable_consent_audit_event_id: str = ""
    durable_consent_migration_posture: str = CONSENT_DURABLE_MIGRATION_NOT_APPLICABLE
    durable_consent_local_storage_boundary: str = (
        CONSENT_DURABLE_STORAGE_BOUNDARY_LOCAL_ONLY
    )
    durable_consent_storage_state: str = CONSENT_DURABLE_STORAGE_STATE_MISSING
    durable_consent_storage_label: str = "Durable consent storage: missing"
    durable_consent_no_secrets_posture: str = CONSENT_RECORD_NO_SECRETS_POSTURE_READY
    durable_consent_provider_payload_posture: str = (
        CONSENT_RECORD_PROVIDER_PAYLOAD_EXCLUDED
    )
    durable_setup_consent_state: str = CONSENT_DURABLE_CONSENT_STATE_MISSING
    durable_setup_consent_label: str = "Durable setup consent: missing"
    durable_setup_consent_reason_code: str = CONSENT_DURABLE_SETUP_REASON_MISSING
    durable_execution_consent_state: str = CONSENT_DURABLE_CONSENT_STATE_MISSING
    durable_execution_consent_label: str = "Durable execution consent: missing"
    durable_execution_consent_reason_code: str = (
        CONSENT_DURABLE_EXECUTION_REASON_MISSING
    )
    durable_setup_execution_consent_separation_state: str = (
        CONSENT_DURABLE_SEPARATION_STATE_READY
    )
    durable_setup_execution_consent_separation_label: str = (
        "Durable setup and execution consent remain separated"
    )
    durable_consent_status_proof_state: str = (
        CONSENT_DURABLE_STATUS_PROOF_HIDDEN_TELEMETRY
    )
    durable_consent_status_proof_label: str = (
        "Durable consent status proof: hidden telemetry only"
    )
    durable_consent_desktop_display_state: str = (
        CONSENT_DURABLE_DESKTOP_DISPLAY_SUPPRESSED
    )
    durable_consent_provider_setup_handoff_state: str = (
        CONSENT_DURABLE_PROVIDER_SETUP_HANDOFF_BLOCKED
    )
    durable_consent_provider_execution_handoff_state: str = (
        CONSENT_DURABLE_PROVIDER_EXECUTION_HANDOFF_BLOCKED
    )
    durable_consent_future_handoff_criteria_state: str = (
        CONSENT_DURABLE_FUTURE_HANDOFF_CRITERIA_BLOCKED
    )
    durable_consent_future_handoff_criteria_label: str = (
        "Durable consent future handoff criteria: blocked"
    )
    consent_ux_state_schema_version: str = CONSENT_UX_STATE_SCHEMA_VERSION
    consent_ux_intent_schema_version: str = CONSENT_UX_INTENT_SCHEMA_VERSION
    consent_ux_state: str = CONSENT_UX_STATE_BLOCKED_BY_DURABLE_CONSENT
    consent_ux_label: str = "Consent UX: blocked by durable consent"
    consent_ux_intent_state: str = CONSENT_UX_INTENT_NONE
    consent_ux_intent_label: str = "Consent UX intent: none"
    consent_ux_surface_state: str = CONSENT_UX_SURFACE_STATUS_ONLY_LOCAL
    consent_ux_surface_label: str = (
        "Consent UX surface: local status only; no provider action"
    )
    consent_ux_setup_display_state: str = CONSENT_DURABLE_CONSENT_STATE_MISSING
    consent_ux_setup_display_label: str = "Consent UX setup: missing"
    consent_ux_execution_display_state: str = CONSENT_DURABLE_CONSENT_STATE_MISSING
    consent_ux_execution_display_label: str = "Consent UX execution: missing"
    consent_ux_revocation_reset_state: str = CONSENT_UX_STATE_BLOCKED_BY_DURABLE_CONSENT
    consent_ux_revocation_reset_label: str = "Consent UX revoke/reset: blocked"
    consent_ux_write_posture: str = CONSENT_UX_WRITE_BLOCKED_FAIL_CLOSED
    consent_ux_write_label: str = "Consent UX write: blocked fail-closed"
    consent_ux_durable_handoff_state: str = CONSENT_UX_DURABLE_HANDOFF_BLOCKED
    consent_ux_durable_handoff_label: str = "Consent UX durable handoff: blocked"
    consent_ux_provider_setup_gate_state: str = CONSENT_UX_PROVIDER_SETUP_GATE_BLOCKED
    consent_ux_provider_execution_gate_state: str = (
        CONSENT_UX_PROVIDER_EXECUTION_GATE_DISABLED
    )
    consent_ux_status_proof_state: str = CONSENT_UX_STATUS_PROOF_STATE
    consent_ux_status_proof_label: str = (
        "Consent UX status proof: derived from durable local consent state"
    )
    consent_ux_desktop_display_state: str = CONSENT_UX_DESKTOP_DISPLAY_SUPPRESSED
    consent_ux_local_only_posture: str = CONSENT_UX_LOCAL_ONLY_POSTURE
    consent_ux_provider_visible_data: str = "none"
    consent_ux_sent_to_provider: bool = False
    consent_ux_can_accept_prompts: bool = False
    consent_ux_network_egress_state: str = NETWORK_EGRESS_BLOCKED
    consent_ux_memory_state: str = MEMORY_INDEXING_DISABLED
    consent_ux_voice_state: str = VOICE_RUNTIME_DISABLED
    consent_ux_functional_ai_criteria_state: str = (
        CONSENT_UX_FUNCTIONAL_AI_CRITERIA_PENDING
    )
    consent_ux_v18_continuation_state: str = CONSENT_UX_V18_CONTINUATION_PENDING
    provider_setup_completion_state_schema_version: str = (
        SETUP_COMPLETION_STATE_SCHEMA_VERSION
    )
    provider_setup_completion_config_schema_version: str = (
        SETUP_COMPLETION_CONFIG_SCHEMA_VERSION
    )
    provider_setup_completion_state: str = SETUP_COMPLETION_STATE_UNAVAILABLE
    provider_setup_completion_label: str = "Setup completion: unavailable"
    provider_setup_completion_eligibility_state: str = (
        SETUP_COMPLETION_ELIGIBILITY_UNAVAILABLE
    )
    provider_setup_completion_eligibility_label: str = (
        "Setup completion eligibility: unavailable"
    )
    provider_setup_completion_blocker_state: str = (
        SETUP_COMPLETION_BLOCKER_CONSENT_UX_REQUIRED
    )
    provider_setup_completion_blocker_label: str = (
        "Setup completion blocker: consent UX readiness required"
    )
    provider_setup_completion_reason_code: str = (
        SETUP_COMPLETION_REASON_DEFAULT_UNAVAILABLE
    )
    provider_setup_completion_reason_label: str = (
        "Setup completion reason: local-only safe default"
    )
    provider_setup_completion_provenance: str = SETUP_COMPLETION_PROVENANCE_CONSENT_UX
    provider_setup_completion_provenance_label: str = (
        "Setup completion provenance: user-operated consent UX state"
    )
    provider_setup_completion_config_state: str = PROVIDER_PATH_CONFIG_STATE_DEFAULT
    provider_setup_completion_config_label: str = (
        "Setup completion config: safe default local-only"
    )
    provider_setup_completion_config_migration: str = (
        SETUP_COMPLETION_CONFIG_MIGRATION_POSTURE
    )
    provider_setup_completion_config_valid: bool = True
    provider_setup_completion_profile_status: str = SETUP_COMPLETION_PROFILE_MISSING
    provider_setup_completion_profile_label: str = (
        "Setup completion profile: missing local finalization"
    )
    provider_setup_completion_config_status: str = SETUP_COMPLETION_CONFIG_MISSING
    provider_setup_completion_config_status_label: str = (
        "Setup completion config finalization: missing"
    )
    provider_setup_completion_no_secrets_status: str = (
        SETUP_COMPLETION_NO_SECRETS_BLOCKED
    )
    provider_setup_completion_no_secrets_label: str = (
        "Setup completion no-secrets posture: blocked"
    )
    provider_setup_completion_validation_status: str = (
        SETUP_COMPLETION_VALIDATION_FAIL_CLOSED
    )
    provider_setup_completion_validation_label: str = (
        "Setup completion validation: fail-closed"
    )
    provider_setup_completion_persistence_status: str = (
        SETUP_COMPLETION_PERSISTENCE_BLOCKED
    )
    provider_setup_completion_persistence_label: str = (
        "Setup completion persistence: blocked"
    )
    provider_setup_completion_reset_state: str = SETUP_COMPLETION_RESET_NONE
    provider_setup_completion_reset_label: str = "Setup completion reset: none"
    provider_setup_completion_setup_consent_state: str = (
        CONSENT_DURABLE_CONSENT_STATE_MISSING
    )
    provider_setup_completion_setup_consent_label: str = (
        "Setup completion setup consent: missing"
    )
    provider_setup_completion_execution_consent_state: str = (
        CONSENT_DURABLE_CONSENT_STATE_MISSING
    )
    provider_setup_completion_execution_consent_label: str = (
        "Setup completion execution consent: missing"
    )
    provider_setup_completion_status_proof_state: str = (
        SETUP_COMPLETION_STATUS_PROOF_HIDDEN_TELEMETRY
    )
    provider_setup_completion_status_proof_label: str = (
        "Setup completion status proof: hidden telemetry only"
    )
    provider_setup_completion_desktop_display_state: str = (
        SETUP_COMPLETION_DESKTOP_DISPLAY_SUPPRESSED
    )
    provider_setup_completion_provider_setup_gate_state: str = (
        SETUP_COMPLETION_PROVIDER_SETUP_GATE_BLOCKED
    )
    provider_setup_completion_provider_execution_gate_state: str = (
        SETUP_COMPLETION_PROVIDER_EXECUTION_GATE_DISABLED
    )
    provider_setup_completion_sdk_handoff_state: str = (
        SETUP_COMPLETION_SDK_HANDOFF_BLOCKED
    )
    provider_setup_completion_sdk_handoff_label: str = (
        "Setup completion SDK handoff: blocked"
    )
    provider_setup_completion_functional_ai_criteria_state: str = (
        SETUP_COMPLETION_FUNCTIONAL_AI_CRITERIA_PENDING
    )
    provider_setup_completion_v18_continuation_state: str = (
        SETUP_COMPLETION_V18_CONTINUATION_PENDING
    )
    provider_setup_completion_provider_visible_data: str = "none"
    provider_setup_completion_sent_to_provider: bool = False
    provider_setup_completion_can_accept_prompts: bool = False
    provider_setup_completion_network_egress_state: str = NETWORK_EGRESS_BLOCKED
    provider_setup_completion_memory_state: str = MEMORY_INDEXING_DISABLED
    provider_setup_completion_voice_state: str = VOICE_RUNTIME_DISABLED
    future_consent_capture_handoff_state: str = FUTURE_CONSENT_CAPTURE_BRANCH_HANDOFF_READY
    consent_collection_fold_down_posture: str = CONSENT_COLLECTION_FOLD_DOWN_READY

    def as_dict(self) -> dict[str, object]:
        return {
            "package_id": self.package_id,
            "slice_ids": self.slice_ids,
            "state_id": self.state_id,
            "mode": self.mode,
            "availability": self.availability,
            "provider_label": self.provider_label,
            "provider_kind": self.provider_kind,
            "status_label": self.status_label,
            "disabled_reason": self.disabled_reason,
            "selected_provider_id": self.selected_provider_id,
            "provider_selection_state": self.provider_selection_state,
            "provider_selection_label": self.provider_selection_label,
            "provider_configuration_state": self.provider_configuration_state,
            "provider_configuration_label": self.provider_configuration_label,
            "provider_registry_state": self.provider_registry_state,
            "provider_registry_label": self.provider_registry_label,
            "configured_provider_count": self.configured_provider_count,
            "available_provider_count": self.available_provider_count,
            "hardware_capability_state": self.hardware_capability_state,
            "hardware_capability_label": self.hardware_capability_label,
            "gpu_capability_state": self.gpu_capability_state,
            "gpu_capability_label": self.gpu_capability_label,
            "cpu_fallback_state": self.cpu_fallback_state,
            "cpu_fallback_label": self.cpu_fallback_label,
            "power_state": self.power_state,
            "power_state_label": self.power_state_label,
            "thermal_guardrail_state": self.thermal_guardrail_state,
            "thermal_guardrail_label": self.thermal_guardrail_label,
            "model_workload_state": self.model_workload_state,
            "model_workload_label": self.model_workload_label,
            "capability_recommendation_state": self.capability_recommendation_state,
            "capability_recommendation_label": self.capability_recommendation_label,
            "hardware_detection_level": self.hardware_detection_level,
            "hardware_detection_label": self.hardware_detection_label,
            "capability_snapshot_policy": self.capability_snapshot_policy,
            "capability_snapshot_source": self.capability_snapshot_source,
            "capability_snapshot_budget_label": self.capability_snapshot_budget_label,
            "ram_readiness_state": self.ram_readiness_state,
            "ram_readiness_label": self.ram_readiness_label,
            "disk_readiness_state": self.disk_readiness_state,
            "disk_readiness_label": self.disk_readiness_label,
            "model_workload_metadata_state": self.model_workload_metadata_state,
            "model_workload_metadata_label": self.model_workload_metadata_label,
            "capability_pack_lifecycle_state": self.capability_pack_lifecycle_state,
            "capability_pack_lifecycle_label": self.capability_pack_lifecycle_label,
            "capability_pack_download_state": self.capability_pack_download_state,
            "capability_pack_download_label": self.capability_pack_download_label,
            "capability_pack_manifest_schema_version": self.capability_pack_manifest_schema_version,
            "capability_pack_manifest_state": self.capability_pack_manifest_state,
            "capability_pack_source_type": self.capability_pack_source_type,
            "capability_pack_checksum_state": self.capability_pack_checksum_state,
            "capability_pack_signature_state": self.capability_pack_signature_state,
            "capability_pack_compatibility_state": self.capability_pack_compatibility_state,
            "capability_pack_disk_requirement": self.capability_pack_disk_requirement,
            "capability_pack_ram_requirement": self.capability_pack_ram_requirement,
            "capability_pack_gpu_requirement": self.capability_pack_gpu_requirement,
            "capability_pack_install_state": self.capability_pack_install_state,
            "capability_pack_update_state": self.capability_pack_update_state,
            "capability_pack_uninstall_state": self.capability_pack_uninstall_state,
            "data_classification_state": self.data_classification_state,
            "data_classification_label": self.data_classification_label,
            "data_classification_schema_version": self.data_classification_schema_version,
            "provider_visible_data_guarantee": self.provider_visible_data_guarantee,
            "memory_context_state": self.memory_context_state,
            "memory_context_label": self.memory_context_label,
            "memory_indexing_state": self.memory_indexing_state,
            "retrieval_state": self.retrieval_state,
            "learning_state": self.learning_state,
            "persistence_state": self.persistence_state,
            "future_memory_eligibility_marker": self.future_memory_eligibility_marker,
            "consent_envelope_state": self.consent_envelope_state,
            "audit_envelope_state": self.audit_envelope_state,
            "secret_boundary_state": self.secret_boundary_state,
            "network_egress_state": self.network_egress_state,
            "audit_secrets_state": self.audit_secrets_state,
            "audit_secrets_label": self.audit_secrets_label,
            "windows_resilience_state": self.windows_resilience_state,
            "windows_resilience_label": self.windows_resilience_label,
            "offline_degraded_state": self.offline_degraded_state,
            "offline_degraded_label": self.offline_degraded_label,
            "persona_core_voice_state": self.persona_core_voice_state,
            "persona_core_voice_label": self.persona_core_voice_label,
            "voice_runtime_state": self.voice_runtime_state,
            "voice_runtime_label": self.voice_runtime_label,
            "validation_proof_gate_state": self.validation_proof_gate_state,
            "validation_proof_gate_label": self.validation_proof_gate_label,
            "abuse_eval_state": self.abuse_eval_state,
            "abuse_eval_label": self.abuse_eval_label,
            "release_proof_gate_state": self.release_proof_gate_state,
            "release_proof_gate_label": self.release_proof_gate_label,
            "core_desktop_copy_contract_version": self.core_desktop_copy_contract_version,
            "core_desktop_runtime_state_contract": self.core_desktop_runtime_state_contract,
            "disabled_prompt_behavior_contract": self.disabled_prompt_behavior_contract,
            "golden_provider_state_fixtures": self.golden_provider_state_fixtures,
            "validator_expansion_state": self.validator_expansion_state,
            "contract_ready_marker": self.contract_ready_marker,
            "ui_ready_marker": self.ui_ready_marker,
            "validator_ready_marker": self.validator_ready_marker,
            "future_implementation_gated_marker": self.future_implementation_gated_marker,
            "privacy_scope": self.privacy_scope,
            "privacy_label": self.privacy_label,
            "provider_visible_data": self.provider_visible_data,
            "provider_visible_data_label": self.provider_visible_data_label,
            "provider_visible_data_detail": self.provider_visible_data_detail,
            "provider_interaction_state": self.provider_interaction_state,
            "provider_interaction_label": self.provider_interaction_label,
            "provider_interaction_detail": self.provider_interaction_detail,
            "provider_consent_boundary_label": self.provider_consent_boundary_label,
            "provider_next_action_label": self.provider_next_action_label,
            "local_storage": self.local_storage,
            "consent_state": self.consent_state,
            "consent_label": self.consent_label,
            "interaction_affordance": self.interaction_affordance,
            "interaction_label": self.interaction_label,
            "interaction_disabled_reason": self.interaction_disabled_reason,
            "no_provider_fallback_label": self.no_provider_fallback_label,
            "prompt_acceptance": self.prompt_acceptance,
            "external_calls": self.external_calls,
            "model_state": self.model_state,
            "capability_pack_state": self.capability_pack_state,
            "source_truth": self.source_truth,
            "runtime_state_schema_version": self.runtime_state_schema_version,
            "runtime_state_category": self.runtime_state_category,
            "runtime_state_label": self.runtime_state_label,
            "runtime_reason_code": self.runtime_reason_code,
            "runtime_reason_label": self.runtime_reason_label,
            "runtime_config_schema_version": self.runtime_config_schema_version,
            "runtime_config_state": self.runtime_config_state,
            "runtime_config_label": self.runtime_config_label,
            "runtime_config_migration": self.runtime_config_migration,
            "runtime_config_valid": self.runtime_config_valid,
            "runtime_fail_closed": self.runtime_fail_closed,
            "runtime_provenance": self.runtime_provenance,
            "runtime_provenance_label": self.runtime_provenance_label,
            "surface_role": self.surface_role,
            "provider_options": tuple(option.as_dict() for option in self.provider_options),
            "foundation_readiness_items": tuple(item.as_dict() for item in self.foundation_readiness_items),
            "provider_readiness_state": self.provider_readiness_state,
            "provider_readiness_label": self.provider_readiness_label,
            "setup_eligibility_state": self.setup_eligibility_state,
            "setup_eligibility_label": self.setup_eligibility_label,
            "setup_blocker_state": self.setup_blocker_state,
            "setup_blocker_label": self.setup_blocker_label,
            "readiness_reason_code": self.readiness_reason_code,
            "readiness_reason_label": self.readiness_reason_label,
            "readiness_provenance": self.readiness_provenance,
            "readiness_provenance_label": self.readiness_provenance_label,
            "readiness_state_schema_version": self.readiness_state_schema_version,
            "readiness_config_schema_version": self.readiness_config_schema_version,
            "readiness_config_state": self.readiness_config_state,
            "readiness_config_label": self.readiness_config_label,
            "readiness_config_migration": self.readiness_config_migration,
            "readiness_config_valid": self.readiness_config_valid,
            "future_provider_gate_status": self.future_provider_gate_status,
            "future_provider_gate_label": self.future_provider_gate_label,
            "capability_pack_eligibility_state": self.capability_pack_eligibility_state,
            "capability_pack_eligibility_label": self.capability_pack_eligibility_label,
            "capability_pack_manifest_validity_state": self.capability_pack_manifest_validity_state,
            "capability_pack_manifest_validity_label": self.capability_pack_manifest_validity_label,
            "capability_pack_source_trust_state": self.capability_pack_source_trust_state,
            "capability_pack_source_trust_label": self.capability_pack_source_trust_label,
            "capability_pack_compatibility_posture_state": self.capability_pack_compatibility_posture_state,
            "capability_pack_compatibility_posture_label": self.capability_pack_compatibility_posture_label,
            "capability_pack_cpu_requirement_posture": self.capability_pack_cpu_requirement_posture,
            "capability_pack_gpu_requirement_posture": self.capability_pack_gpu_requirement_posture,
            "capability_pack_ram_requirement_posture": self.capability_pack_ram_requirement_posture,
            "capability_pack_disk_requirement_posture": self.capability_pack_disk_requirement_posture,
            "install_intent_state": self.install_intent_state,
            "install_intent_label": self.install_intent_label,
            "capability_pack_download_blocked_reason": self.capability_pack_download_blocked_reason,
            "capability_pack_install_blocked_reason": self.capability_pack_install_blocked_reason,
            "capability_pack_update_blocked_reason": self.capability_pack_update_blocked_reason,
            "capability_pack_uninstall_blocked_reason": self.capability_pack_uninstall_blocked_reason,
            "action_permission_matrix": tuple(item.as_dict() for item in self.action_permission_matrix),
            "provider_activation_state": self.provider_activation_state,
            "provider_activation_label": self.provider_activation_label,
            "activation_eligibility_state": self.activation_eligibility_state,
            "activation_eligibility_label": self.activation_eligibility_label,
            "activation_blocker_state": self.activation_blocker_state,
            "activation_blocker_label": self.activation_blocker_label,
            "activation_reason_code": self.activation_reason_code,
            "activation_reason_label": self.activation_reason_label,
            "activation_provenance": self.activation_provenance,
            "activation_provenance_label": self.activation_provenance_label,
            "activation_state_schema_version": self.activation_state_schema_version,
            "activation_config_schema_version": self.activation_config_schema_version,
            "activation_config_state": self.activation_config_state,
            "activation_config_label": self.activation_config_label,
            "activation_config_migration": self.activation_config_migration,
            "activation_config_valid": self.activation_config_valid,
            "future_activation_gate_status": self.future_activation_gate_status,
            "future_activation_gate_label": self.future_activation_gate_label,
            "provider_adapter_posture": self.provider_adapter_posture,
            "provider_adapter_label": self.provider_adapter_label,
            "provider_adapter_kind": self.provider_adapter_kind,
            "provider_adapter_availability_state": self.provider_adapter_availability_state,
            "provider_adapter_availability_label": self.provider_adapter_availability_label,
            "provider_adapter_execution_posture": self.provider_adapter_execution_posture,
            "provider_adapter_execution_label": self.provider_adapter_execution_label,
            "provider_metadata_contract_version": self.provider_metadata_contract_version,
            "provider_config_envelope_version": self.provider_config_envelope_version,
            "provider_activation_handoff_state": self.provider_activation_handoff_state,
            "provider_activation_handoff_label": self.provider_activation_handoff_label,
            "future_sdk_integration_boundary": self.future_sdk_integration_boundary,
            "prompt_execution_gate_state": self.prompt_execution_gate_state,
            "prompt_execution_gate_label": self.prompt_execution_gate_label,
            "model_execution_gate_state": self.model_execution_gate_state,
            "model_execution_gate_label": self.model_execution_gate_label,
            "provider_execution_gate_state": self.provider_execution_gate_state,
            "provider_execution_gate_label": self.provider_execution_gate_label,
            "readiness_gate_state": self.readiness_gate_state,
            "consent_gate_state": self.consent_gate_state,
            "capability_gate_state": self.capability_gate_state,
            "manifest_gate_state": self.manifest_gate_state,
            "adapter_gate_state": self.adapter_gate_state,
            "safety_eval_gate_state": self.safety_eval_gate_state,
            "network_egress_gate_state": self.network_egress_gate_state,
            "memory_indexing_gate_state": self.memory_indexing_gate_state,
            "voice_core_sync_gate_state": self.voice_core_sync_gate_state,
            "version_jump_gate_state": self.version_jump_gate_state,
            "functional_ai_criteria_state": self.functional_ai_criteria_state,
            "functional_ai_criteria_label": self.functional_ai_criteria_label,
            "v18_prebeta_readiness_state": self.v18_prebeta_readiness_state,
            "v18_prebeta_readiness_label": self.v18_prebeta_readiness_label,
            "provider_execution_readiness_state": self.provider_execution_readiness_state,
            "provider_execution_readiness_label": self.provider_execution_readiness_label,
            "prompt_execution_readiness_state": self.prompt_execution_readiness_state,
            "prompt_execution_readiness_label": self.prompt_execution_readiness_label,
            "model_execution_readiness_state": self.model_execution_readiness_state,
            "model_execution_readiness_label": self.model_execution_readiness_label,
            "execution_eligibility_state": self.execution_eligibility_state,
            "execution_eligibility_label": self.execution_eligibility_label,
            "execution_blocker_state": self.execution_blocker_state,
            "execution_blocker_label": self.execution_blocker_label,
            "execution_reason_code": self.execution_reason_code,
            "execution_reason_label": self.execution_reason_label,
            "execution_provenance": self.execution_provenance,
            "execution_provenance_label": self.execution_provenance_label,
            "execution_state_schema_version": self.execution_state_schema_version,
            "execution_config_schema_version": self.execution_config_schema_version,
            "execution_config_state": self.execution_config_state,
            "execution_config_label": self.execution_config_label,
            "execution_config_migration": self.execution_config_migration,
            "execution_config_valid": self.execution_config_valid,
            "execution_approval_status": self.execution_approval_status,
            "execution_approval_label": self.execution_approval_label,
            "provider_path_status": self.provider_path_status,
            "provider_path_label": self.provider_path_label,
            "provider_selection_posture": self.provider_selection_posture,
            "provider_selection_posture_label": self.provider_selection_posture_label,
            "adapter_selection_posture": self.adapter_selection_posture,
            "adapter_selection_posture_label": self.adapter_selection_posture_label,
            "prompt_acceptance_gate_state": self.prompt_acceptance_gate_state,
            "prompt_acceptance_gate_label": self.prompt_acceptance_gate_label,
            "prompt_routing_gate_state": self.prompt_routing_gate_state,
            "prompt_routing_gate_label": self.prompt_routing_gate_label,
            "prompt_send_posture": self.prompt_send_posture,
            "prompt_send_label": self.prompt_send_label,
            "model_execution_status": self.model_execution_status,
            "model_execution_status_label": self.model_execution_status_label,
            "model_workload_readiness_posture": self.model_workload_readiness_posture,
            "model_workload_readiness_label": self.model_workload_readiness_label,
            "provider_visible_data_execution_posture": self.provider_visible_data_execution_posture,
            "provider_visible_data_execution_label": self.provider_visible_data_execution_label,
            "external_call_readiness_state": self.external_call_readiness_state,
            "external_call_readiness_label": self.external_call_readiness_label,
            "safety_eval_readiness_state": self.safety_eval_readiness_state,
            "safety_eval_readiness_label": self.safety_eval_readiness_label,
            "data_classification_gate_state": self.data_classification_gate_state,
            "data_classification_gate_label": self.data_classification_gate_label,
            "execution_proof_marker": self.execution_proof_marker,
            "future_execution_validation_marker": self.future_execution_validation_marker,
            "functional_ai_release_gate_state": self.functional_ai_release_gate_state,
            "functional_ai_release_gate_label": self.functional_ai_release_gate_label,
            "v18_release_gate_state": self.v18_release_gate_state,
            "v18_release_gate_label": self.v18_release_gate_label,
            "provider_path_readiness_state": self.provider_path_readiness_state,
            "provider_path_readiness_label": self.provider_path_readiness_label,
            "provider_path_eligibility_state": self.provider_path_eligibility_state,
            "provider_path_eligibility_label": self.provider_path_eligibility_label,
            "provider_path_blocker_state": self.provider_path_blocker_state,
            "provider_path_blocker_label": self.provider_path_blocker_label,
            "provider_path_reason_code": self.provider_path_reason_code,
            "provider_path_reason_label": self.provider_path_reason_label,
            "provider_path_provenance": self.provider_path_provenance,
            "provider_path_provenance_label": self.provider_path_provenance_label,
            "provider_path_state_schema_version": self.provider_path_state_schema_version,
            "provider_path_config_schema_version": self.provider_path_config_schema_version,
            "provider_path_config_state": self.provider_path_config_state,
            "provider_path_config_label": self.provider_path_config_label,
            "provider_path_config_migration": self.provider_path_config_migration,
            "provider_path_config_valid": self.provider_path_config_valid,
            "provider_path_approval_status": self.provider_path_approval_status,
            "provider_path_approval_label": self.provider_path_approval_label,
            "provider_profile_id": self.provider_profile_id,
            "provider_profile_kind": self.provider_profile_kind,
            "provider_profile_display_name": self.provider_profile_display_name,
            "provider_profile_source": self.provider_profile_source,
            "provider_profile_metadata_contract_version": self.provider_profile_metadata_contract_version,
            "provider_profile_available": self.provider_profile_available,
            "provider_sdk_requirement_posture": self.provider_sdk_requirement_posture,
            "provider_network_requirement_posture": self.provider_network_requirement_posture,
            "provider_config_status": self.provider_config_status,
            "provider_availability_posture": self.provider_availability_posture,
            "provider_setup_approval_status": self.provider_setup_approval_status,
            "provider_execution_approval_status": self.provider_execution_approval_status,
            "provider_visible_data_scope": self.provider_visible_data_scope,
            "local_null_provider_fallback_status": self.local_null_provider_fallback_status,
            "future_sdk_handoff_marker": self.future_sdk_handoff_marker,
            "future_provider_setup_handoff_marker": self.future_provider_setup_handoff_marker,
            "consent_readiness_state": self.consent_readiness_state,
            "consent_readiness_label": self.consent_readiness_label,
            "consent_state_schema_version": self.consent_state_schema_version,
            "consent_config_schema_version": self.consent_config_schema_version,
            "consent_config_migration": self.consent_config_migration,
            "setup_consent_state": self.setup_consent_state,
            "setup_consent_label": self.setup_consent_label,
            "setup_consent_blocker_state": self.setup_consent_blocker_state,
            "setup_consent_blocker_label": self.setup_consent_blocker_label,
            "setup_consent_reason_code": self.setup_consent_reason_code,
            "setup_consent_reason_label": self.setup_consent_reason_label,
            "setup_consent_provenance": self.setup_consent_provenance,
            "setup_consent_provenance_label": self.setup_consent_provenance_label,
            "setup_consent_handoff_state": self.setup_consent_handoff_state,
            "setup_consent_handoff_label": self.setup_consent_handoff_label,
            "execution_consent_state": self.execution_consent_state,
            "execution_consent_label": self.execution_consent_label,
            "execution_consent_blocker_state": self.execution_consent_blocker_state,
            "execution_consent_blocker_label": self.execution_consent_blocker_label,
            "execution_consent_reason_code": self.execution_consent_reason_code,
            "execution_consent_reason_label": self.execution_consent_reason_label,
            "execution_consent_provenance": self.execution_consent_provenance,
            "execution_consent_provenance_label": self.execution_consent_provenance_label,
            "execution_consent_handoff_state": self.execution_consent_handoff_state,
            "execution_consent_handoff_label": self.execution_consent_handoff_label,
            "provider_visible_data_requirement_state": self.provider_visible_data_requirement_state,
            "provider_visible_data_requirement_label": self.provider_visible_data_requirement_label,
            "data_classification_posture_state": self.data_classification_posture_state,
            "data_classification_posture_label": self.data_classification_posture_label,
            "audit_envelope_posture_state": self.audit_envelope_posture_state,
            "audit_envelope_posture_label": self.audit_envelope_posture_label,
            "local_only_status_posture": self.local_only_status_posture,
            "local_only_status_label": self.local_only_status_label,
            "provider_setup_future_gated_posture": self.provider_setup_future_gated_posture,
            "provider_setup_future_gated_label": self.provider_setup_future_gated_label,
            "provider_execution_future_gated_posture": self.provider_execution_future_gated_posture,
            "provider_execution_future_gated_label": self.provider_execution_future_gated_label,
            "provider_path_gate_state": self.provider_path_gate_state,
            "provider_config_gate_state": self.provider_config_gate_state,
            "setup_consent_gate_state": self.setup_consent_gate_state,
            "execution_consent_gate_state": self.execution_consent_gate_state,
            "provider_visible_data_gate_state": self.provider_visible_data_gate_state,
            "audit_gate_state": self.audit_gate_state,
            "setup_flow_readiness_state": self.setup_flow_readiness_state,
            "setup_flow_readiness_label": self.setup_flow_readiness_label,
            "setup_flow_eligibility_state": self.setup_flow_eligibility_state,
            "setup_flow_eligibility_label": self.setup_flow_eligibility_label,
            "setup_flow_blocker_state": self.setup_flow_blocker_state,
            "setup_flow_blocker_label": self.setup_flow_blocker_label,
            "setup_flow_reason_code": self.setup_flow_reason_code,
            "setup_flow_reason_label": self.setup_flow_reason_label,
            "setup_flow_provenance": self.setup_flow_provenance,
            "setup_flow_provenance_label": self.setup_flow_provenance_label,
            "setup_flow_state_schema_version": self.setup_flow_state_schema_version,
            "setup_flow_config_schema_version": self.setup_flow_config_schema_version,
            "setup_flow_config_state": self.setup_flow_config_state,
            "setup_flow_config_label": self.setup_flow_config_label,
            "setup_flow_config_migration": self.setup_flow_config_migration,
            "setup_flow_config_valid": self.setup_flow_config_valid,
            "setup_flow_approval_status": self.setup_flow_approval_status,
            "setup_flow_approval_label": self.setup_flow_approval_label,
            "provider_setup_handoff_posture": self.provider_setup_handoff_posture,
            "provider_setup_handoff_label": self.provider_setup_handoff_label,
            "provider_consent_handoff_posture": self.provider_consent_handoff_posture,
            "provider_consent_handoff_label": self.provider_consent_handoff_label,
            "provider_path_handoff_posture": self.provider_path_handoff_posture,
            "provider_path_handoff_label": self.provider_path_handoff_label,
            "consent_flow_readiness_state": self.consent_flow_readiness_state,
            "consent_flow_readiness_label": self.consent_flow_readiness_label,
            "consent_flow_eligibility_state": self.consent_flow_eligibility_state,
            "consent_flow_eligibility_label": self.consent_flow_eligibility_label,
            "consent_flow_blocker_state": self.consent_flow_blocker_state,
            "consent_flow_blocker_label": self.consent_flow_blocker_label,
            "consent_flow_reason_code": self.consent_flow_reason_code,
            "consent_flow_reason_label": self.consent_flow_reason_label,
            "consent_flow_provenance": self.consent_flow_provenance,
            "consent_flow_provenance_label": self.consent_flow_provenance_label,
            "consent_flow_state_schema_version": self.consent_flow_state_schema_version,
            "consent_flow_config_schema_version": self.consent_flow_config_schema_version,
            "consent_flow_config_state": self.consent_flow_config_state,
            "consent_flow_config_label": self.consent_flow_config_label,
            "consent_flow_config_migration": self.consent_flow_config_migration,
            "consent_flow_config_valid": self.consent_flow_config_valid,
            "consent_flow_approval_status": self.consent_flow_approval_status,
            "consent_flow_approval_label": self.consent_flow_approval_label,
            "consent_collection_posture": self.consent_collection_posture,
            "consent_collection_label": self.consent_collection_label,
            "data_visibility_consent_posture": self.data_visibility_consent_posture,
            "data_visibility_consent_label": self.data_visibility_consent_label,
            "setup_flow_gate_state": self.setup_flow_gate_state,
            "consent_flow_gate_state": self.consent_flow_gate_state,
            "setup_approval_gate_state": self.setup_approval_gate_state,
            "execution_approval_gate_state": self.execution_approval_gate_state,
            "desktop_ai_owned_readiness_display_state": self.desktop_ai_owned_readiness_display_state,
            "desktop_ai_owned_readiness_display_label": self.desktop_ai_owned_readiness_display_label,
            "provider_setup_contract_readiness_state": self.provider_setup_contract_readiness_state,
            "provider_setup_contract_readiness_label": self.provider_setup_contract_readiness_label,
            "provider_setup_contract_eligibility_state": self.provider_setup_contract_eligibility_state,
            "provider_setup_contract_eligibility_label": self.provider_setup_contract_eligibility_label,
            "provider_setup_contract_blocker_state": self.provider_setup_contract_blocker_state,
            "provider_setup_contract_blocker_label": self.provider_setup_contract_blocker_label,
            "provider_setup_contract_reason_code": self.provider_setup_contract_reason_code,
            "provider_setup_contract_reason_label": self.provider_setup_contract_reason_label,
            "provider_setup_contract_provenance": self.provider_setup_contract_provenance,
            "provider_setup_contract_provenance_label": self.provider_setup_contract_provenance_label,
            "provider_setup_contract_state_schema_version": self.provider_setup_contract_state_schema_version,
            "provider_setup_contract_config_schema_version": self.provider_setup_contract_config_schema_version,
            "provider_setup_contract_config_state": self.provider_setup_contract_config_state,
            "provider_setup_contract_config_label": self.provider_setup_contract_config_label,
            "provider_setup_contract_config_migration": self.provider_setup_contract_config_migration,
            "provider_setup_contract_config_valid": self.provider_setup_contract_config_valid,
            "provider_setup_contract_approval_status": self.provider_setup_contract_approval_status,
            "provider_setup_contract_approval_label": self.provider_setup_contract_approval_label,
            "provider_setup_contract_gate_state": self.provider_setup_contract_gate_state,
            "provider_profile_gate_state": self.provider_profile_gate_state,
            "capability_gate_state": self.capability_gate_state,
            "manifest_gate_state": self.manifest_gate_state,
            "safety_eval_gate_state": self.safety_eval_gate_state,
            "network_gate_state": self.network_gate_state,
            "memory_indexing_gate_state": self.memory_indexing_gate_state,
            "voice_core_sync_gate_state": self.voice_core_sync_gate_state,
            "version_jump_gate_state": self.version_jump_gate_state,
            "provider_profile_required_fields": self.provider_profile_required_fields,
            "provider_config_required_fields": self.provider_config_required_fields,
            "provider_setup_prerequisite_posture": self.provider_setup_prerequisite_posture,
            "provider_setup_validation_posture": self.provider_setup_validation_posture,
            "provider_setup_ui_proof_posture": self.provider_setup_ui_proof_posture,
            "future_setup_branch_handoff_state": self.future_setup_branch_handoff_state,
            "provider_setup_contract_fold_down_posture": self.provider_setup_contract_fold_down_posture,
            "provider_setup_foundation_state": self.provider_setup_foundation_state,
            "provider_setup_foundation_label": self.provider_setup_foundation_label,
            "provider_setup_foundation_eligibility_state": (
                self.provider_setup_foundation_eligibility_state
            ),
            "provider_setup_foundation_eligibility_label": (
                self.provider_setup_foundation_eligibility_label
            ),
            "provider_setup_foundation_blocker_state": self.provider_setup_foundation_blocker_state,
            "provider_setup_foundation_blocker_label": self.provider_setup_foundation_blocker_label,
            "provider_setup_foundation_reason_code": self.provider_setup_foundation_reason_code,
            "provider_setup_foundation_reason_label": self.provider_setup_foundation_reason_label,
            "provider_setup_foundation_provenance": self.provider_setup_foundation_provenance,
            "provider_setup_foundation_provenance_label": (
                self.provider_setup_foundation_provenance_label
            ),
            "provider_setup_foundation_state_schema_version": (
                self.provider_setup_foundation_state_schema_version
            ),
            "provider_setup_foundation_config_schema_version": (
                self.provider_setup_foundation_config_schema_version
            ),
            "provider_setup_foundation_config_state": self.provider_setup_foundation_config_state,
            "provider_setup_foundation_config_label": self.provider_setup_foundation_config_label,
            "provider_setup_foundation_config_migration": (
                self.provider_setup_foundation_config_migration
            ),
            "provider_setup_foundation_config_valid": self.provider_setup_foundation_config_valid,
            "provider_setup_foundation_setup_entry_state": (
                self.provider_setup_foundation_setup_entry_state
            ),
            "provider_setup_foundation_setup_entry_label": (
                self.provider_setup_foundation_setup_entry_label
            ),
            "provider_setup_foundation_profile_draft_status": (
                self.provider_setup_foundation_profile_draft_status
            ),
            "provider_setup_foundation_profile_draft_label": (
                self.provider_setup_foundation_profile_draft_label
            ),
            "provider_setup_foundation_config_draft_status": (
                self.provider_setup_foundation_config_draft_status
            ),
            "provider_setup_foundation_config_draft_label": (
                self.provider_setup_foundation_config_draft_label
            ),
            "provider_setup_foundation_validation_status": (
                self.provider_setup_foundation_validation_status
            ),
            "provider_setup_foundation_validation_label": (
                self.provider_setup_foundation_validation_label
            ),
            "provider_setup_foundation_persistence_status": (
                self.provider_setup_foundation_persistence_status
            ),
            "provider_setup_foundation_persistence_label": (
                self.provider_setup_foundation_persistence_label
            ),
            "provider_setup_foundation_approval_status": (
                self.provider_setup_foundation_approval_status
            ),
            "provider_setup_foundation_approval_label": (
                self.provider_setup_foundation_approval_label
            ),
            "provider_setup_foundation_gate_state": self.provider_setup_foundation_gate_state,
            "local_null_provider_fallback_proof": self.local_null_provider_fallback_proof,
            "provider_setup_implementation_handoff_state": (
                self.provider_setup_implementation_handoff_state
            ),
            "provider_setup_implementation_fold_down_posture": (
                self.provider_setup_implementation_fold_down_posture
            ),
            "consent_collection_foundation_state": self.consent_collection_foundation_state,
            "consent_collection_foundation_label": self.consent_collection_foundation_label,
            "consent_collection_eligibility_state": self.consent_collection_eligibility_state,
            "consent_collection_eligibility_label": self.consent_collection_eligibility_label,
            "consent_collection_blocker_state": self.consent_collection_blocker_state,
            "consent_collection_blocker_label": self.consent_collection_blocker_label,
            "consent_collection_reason_code": self.consent_collection_reason_code,
            "consent_collection_reason_label": self.consent_collection_reason_label,
            "consent_collection_provenance": self.consent_collection_provenance,
            "consent_collection_provenance_label": self.consent_collection_provenance_label,
            "consent_collection_state_schema_version": self.consent_collection_state_schema_version,
            "consent_collection_config_schema_version": self.consent_collection_config_schema_version,
            "consent_collection_config_state": self.consent_collection_config_state,
            "consent_collection_config_label": self.consent_collection_config_label,
            "consent_collection_config_migration": self.consent_collection_config_migration,
            "consent_collection_config_valid": self.consent_collection_config_valid,
            "consent_collection_approval_status": self.consent_collection_approval_status,
            "consent_collection_approval_label": self.consent_collection_approval_label,
            "consent_collection_gate_state": self.consent_collection_gate_state,
            "consent_capture_surface_state": self.consent_capture_surface_state,
            "consent_capture_surface_label": self.consent_capture_surface_label,
            "setup_consent_capture_status": self.setup_consent_capture_status,
            "setup_consent_capture_label": self.setup_consent_capture_label,
            "execution_consent_capture_status": self.execution_consent_capture_status,
            "execution_consent_capture_label": self.execution_consent_capture_label,
            "consent_data_visibility_review_status": (
                self.consent_data_visibility_review_status
            ),
            "consent_data_visibility_review_label": self.consent_data_visibility_review_label,
            "consent_audit_envelope_status": self.consent_audit_envelope_status,
            "consent_audit_envelope_label": self.consent_audit_envelope_label,
            "consent_provenance_status": self.consent_provenance_status,
            "consent_provenance_label": self.consent_provenance_label,
            "consent_persistence_status": self.consent_persistence_status,
            "consent_persistence_label": self.consent_persistence_label,
            "consent_collection_validation_status": self.consent_collection_validation_status,
            "consent_collection_validation_label": self.consent_collection_validation_label,
            "consent_capture_transition_schema_version": (
                self.consent_capture_transition_schema_version
            ),
            "consent_capture_local_record_schema_version": (
                self.consent_capture_local_record_schema_version
            ),
            "consent_capture_state": self.consent_capture_state,
            "consent_capture_label": self.consent_capture_label,
            "consent_capture_record_state": self.consent_capture_record_state,
            "consent_capture_record_valid": self.consent_capture_record_valid,
            "consent_capture_local_write_requested": (
                self.consent_capture_local_write_requested
            ),
            "consent_capture_write_status": self.consent_capture_write_status,
            "consent_capture_write_label": self.consent_capture_write_label,
            "consent_capture_write_blocker": self.consent_capture_write_blocker,
            "consent_capture_write_reason": self.consent_capture_write_reason,
            "consent_capture_provenance": self.consent_capture_provenance,
            "setup_consent_captured": self.setup_consent_captured,
            "execution_consent_captured": self.execution_consent_captured,
            "consent_capture_local_snapshot_status": (
                self.consent_capture_local_snapshot_status
            ),
            "consent_capture_durable_persistence_status": (
                self.consent_capture_durable_persistence_status
            ),
            "consent_record_storage_boundary_schema_version": (
                self.consent_record_storage_boundary_schema_version
            ),
            "consent_record_storage_boundary_state": (
                self.consent_record_storage_boundary_state
            ),
            "consent_record_storage_boundary_label": (
                self.consent_record_storage_boundary_label
            ),
            "consent_record_durable_storage_state": (
                self.consent_record_durable_storage_state
            ),
            "consent_record_durable_storage_label": (
                self.consent_record_durable_storage_label
            ),
            "consent_record_revocation_model_state": (
                self.consent_record_revocation_model_state
            ),
            "consent_record_revocation_model_label": (
                self.consent_record_revocation_model_label
            ),
            "consent_record_reset_model_state": self.consent_record_reset_model_state,
            "consent_record_reset_model_label": self.consent_record_reset_model_label,
            "consent_record_no_secrets_posture": self.consent_record_no_secrets_posture,
            "consent_record_provider_payload_posture": (
                self.consent_record_provider_payload_posture
            ),
            "consent_capture_audit_schema_version": (
                self.consent_capture_audit_schema_version
            ),
            "consent_capture_audit_status": self.consent_capture_audit_status,
            "consent_capture_audit_label": self.consent_capture_audit_label,
            "setup_execution_consent_separation_state": (
                self.setup_execution_consent_separation_state
            ),
            "setup_execution_consent_separation_label": (
                self.setup_execution_consent_separation_label
            ),
            "consent_capture_ui_status_proof_state": (
                self.consent_capture_ui_status_proof_state
            ),
            "consent_capture_ui_status_proof_label": (
                self.consent_capture_ui_status_proof_label
            ),
            "consent_capture_desktop_display_state": (
                self.consent_capture_desktop_display_state
            ),
            "consent_capture_provider_setup_handoff_state": (
                self.consent_capture_provider_setup_handoff_state
            ),
            "consent_capture_functional_ai_criteria_state": (
                self.consent_capture_functional_ai_criteria_state
            ),
            "consent_capture_v18_continuation_state": (
                self.consent_capture_v18_continuation_state
            ),
            "consent_capture_provider_visible_data": (
                self.consent_capture_provider_visible_data
            ),
            "consent_capture_sent_to_provider": self.consent_capture_sent_to_provider,
            "consent_capture_can_accept_prompts": self.consent_capture_can_accept_prompts,
            "consent_capture_prompt_execution_state": (
                self.consent_capture_prompt_execution_state
            ),
            "consent_capture_network_egress_state": (
                self.consent_capture_network_egress_state
            ),
            "consent_capture_memory_state": self.consent_capture_memory_state,
            "consent_capture_voice_state": self.consent_capture_voice_state,
            "durable_consent_record_schema_version": (
                self.durable_consent_record_schema_version
            ),
            "durable_consent_storage_boundary_schema_version": (
                self.durable_consent_storage_boundary_schema_version
            ),
            "durable_consent_record_state": self.durable_consent_record_state,
            "durable_consent_record_valid": self.durable_consent_record_valid,
            "durable_consent_record_id": self.durable_consent_record_id,
            "durable_consent_provider_profile_id": (
                self.durable_consent_provider_profile_id
            ),
            "durable_setup_consent_granted": self.durable_setup_consent_granted,
            "durable_execution_consent_granted": (
                self.durable_execution_consent_granted
            ),
            "durable_consent_revoked": self.durable_consent_revoked,
            "durable_consent_reset_requested": self.durable_consent_reset_requested,
            "durable_consent_expired": self.durable_consent_expired,
            "durable_consent_fail_closed_reason": (
                self.durable_consent_fail_closed_reason
            ),
            "durable_consent_provenance": self.durable_consent_provenance,
            "durable_consent_audit_event_id": self.durable_consent_audit_event_id,
            "durable_consent_migration_posture": (
                self.durable_consent_migration_posture
            ),
            "durable_consent_local_storage_boundary": (
                self.durable_consent_local_storage_boundary
            ),
            "durable_consent_storage_state": self.durable_consent_storage_state,
            "durable_consent_storage_label": self.durable_consent_storage_label,
            "durable_consent_no_secrets_posture": (
                self.durable_consent_no_secrets_posture
            ),
            "durable_consent_provider_payload_posture": (
                self.durable_consent_provider_payload_posture
            ),
            "durable_setup_consent_state": self.durable_setup_consent_state,
            "durable_setup_consent_label": self.durable_setup_consent_label,
            "durable_setup_consent_reason_code": (
                self.durable_setup_consent_reason_code
            ),
            "durable_execution_consent_state": (
                self.durable_execution_consent_state
            ),
            "durable_execution_consent_label": (
                self.durable_execution_consent_label
            ),
            "durable_execution_consent_reason_code": (
                self.durable_execution_consent_reason_code
            ),
            "durable_setup_execution_consent_separation_state": (
                self.durable_setup_execution_consent_separation_state
            ),
            "durable_setup_execution_consent_separation_label": (
                self.durable_setup_execution_consent_separation_label
            ),
            "durable_consent_status_proof_state": (
                self.durable_consent_status_proof_state
            ),
            "durable_consent_status_proof_label": (
                self.durable_consent_status_proof_label
            ),
            "durable_consent_desktop_display_state": (
                self.durable_consent_desktop_display_state
            ),
            "durable_consent_provider_setup_handoff_state": (
                self.durable_consent_provider_setup_handoff_state
            ),
            "durable_consent_provider_execution_handoff_state": (
                self.durable_consent_provider_execution_handoff_state
            ),
            "durable_consent_future_handoff_criteria_state": (
                self.durable_consent_future_handoff_criteria_state
            ),
            "durable_consent_future_handoff_criteria_label": (
                self.durable_consent_future_handoff_criteria_label
            ),
            "consent_ux_state_schema_version": self.consent_ux_state_schema_version,
            "consent_ux_intent_schema_version": self.consent_ux_intent_schema_version,
            "consent_ux_state": self.consent_ux_state,
            "consent_ux_label": self.consent_ux_label,
            "consent_ux_intent_state": self.consent_ux_intent_state,
            "consent_ux_intent_label": self.consent_ux_intent_label,
            "consent_ux_surface_state": self.consent_ux_surface_state,
            "consent_ux_surface_label": self.consent_ux_surface_label,
            "consent_ux_setup_display_state": self.consent_ux_setup_display_state,
            "consent_ux_setup_display_label": self.consent_ux_setup_display_label,
            "consent_ux_execution_display_state": (
                self.consent_ux_execution_display_state
            ),
            "consent_ux_execution_display_label": (
                self.consent_ux_execution_display_label
            ),
            "consent_ux_revocation_reset_state": (
                self.consent_ux_revocation_reset_state
            ),
            "consent_ux_revocation_reset_label": (
                self.consent_ux_revocation_reset_label
            ),
            "consent_ux_write_posture": self.consent_ux_write_posture,
            "consent_ux_write_label": self.consent_ux_write_label,
            "consent_ux_durable_handoff_state": self.consent_ux_durable_handoff_state,
            "consent_ux_durable_handoff_label": self.consent_ux_durable_handoff_label,
            "consent_ux_provider_setup_gate_state": (
                self.consent_ux_provider_setup_gate_state
            ),
            "consent_ux_provider_execution_gate_state": (
                self.consent_ux_provider_execution_gate_state
            ),
            "consent_ux_status_proof_state": self.consent_ux_status_proof_state,
            "consent_ux_status_proof_label": self.consent_ux_status_proof_label,
            "consent_ux_desktop_display_state": self.consent_ux_desktop_display_state,
            "consent_ux_local_only_posture": self.consent_ux_local_only_posture,
            "consent_ux_provider_visible_data": self.consent_ux_provider_visible_data,
            "consent_ux_sent_to_provider": self.consent_ux_sent_to_provider,
            "consent_ux_can_accept_prompts": self.consent_ux_can_accept_prompts,
            "consent_ux_network_egress_state": self.consent_ux_network_egress_state,
            "consent_ux_memory_state": self.consent_ux_memory_state,
            "consent_ux_voice_state": self.consent_ux_voice_state,
            "consent_ux_functional_ai_criteria_state": (
                self.consent_ux_functional_ai_criteria_state
            ),
            "consent_ux_v18_continuation_state": (
                self.consent_ux_v18_continuation_state
            ),
            "provider_setup_completion_state_schema_version": (
                self.provider_setup_completion_state_schema_version
            ),
            "provider_setup_completion_config_schema_version": (
                self.provider_setup_completion_config_schema_version
            ),
            "provider_setup_completion_state": self.provider_setup_completion_state,
            "provider_setup_completion_label": self.provider_setup_completion_label,
            "provider_setup_completion_eligibility_state": (
                self.provider_setup_completion_eligibility_state
            ),
            "provider_setup_completion_eligibility_label": (
                self.provider_setup_completion_eligibility_label
            ),
            "provider_setup_completion_blocker_state": (
                self.provider_setup_completion_blocker_state
            ),
            "provider_setup_completion_blocker_label": (
                self.provider_setup_completion_blocker_label
            ),
            "provider_setup_completion_reason_code": (
                self.provider_setup_completion_reason_code
            ),
            "provider_setup_completion_reason_label": (
                self.provider_setup_completion_reason_label
            ),
            "provider_setup_completion_provenance": (
                self.provider_setup_completion_provenance
            ),
            "provider_setup_completion_provenance_label": (
                self.provider_setup_completion_provenance_label
            ),
            "provider_setup_completion_config_state": (
                self.provider_setup_completion_config_state
            ),
            "provider_setup_completion_config_label": (
                self.provider_setup_completion_config_label
            ),
            "provider_setup_completion_config_migration": (
                self.provider_setup_completion_config_migration
            ),
            "provider_setup_completion_config_valid": (
                self.provider_setup_completion_config_valid
            ),
            "provider_setup_completion_profile_status": (
                self.provider_setup_completion_profile_status
            ),
            "provider_setup_completion_profile_label": (
                self.provider_setup_completion_profile_label
            ),
            "provider_setup_completion_config_status": (
                self.provider_setup_completion_config_status
            ),
            "provider_setup_completion_config_status_label": (
                self.provider_setup_completion_config_status_label
            ),
            "provider_setup_completion_no_secrets_status": (
                self.provider_setup_completion_no_secrets_status
            ),
            "provider_setup_completion_no_secrets_label": (
                self.provider_setup_completion_no_secrets_label
            ),
            "provider_setup_completion_validation_status": (
                self.provider_setup_completion_validation_status
            ),
            "provider_setup_completion_validation_label": (
                self.provider_setup_completion_validation_label
            ),
            "provider_setup_completion_persistence_status": (
                self.provider_setup_completion_persistence_status
            ),
            "provider_setup_completion_persistence_label": (
                self.provider_setup_completion_persistence_label
            ),
            "provider_setup_completion_reset_state": (
                self.provider_setup_completion_reset_state
            ),
            "provider_setup_completion_reset_label": (
                self.provider_setup_completion_reset_label
            ),
            "provider_setup_completion_setup_consent_state": (
                self.provider_setup_completion_setup_consent_state
            ),
            "provider_setup_completion_setup_consent_label": (
                self.provider_setup_completion_setup_consent_label
            ),
            "provider_setup_completion_execution_consent_state": (
                self.provider_setup_completion_execution_consent_state
            ),
            "provider_setup_completion_execution_consent_label": (
                self.provider_setup_completion_execution_consent_label
            ),
            "provider_setup_completion_status_proof_state": (
                self.provider_setup_completion_status_proof_state
            ),
            "provider_setup_completion_status_proof_label": (
                self.provider_setup_completion_status_proof_label
            ),
            "provider_setup_completion_desktop_display_state": (
                self.provider_setup_completion_desktop_display_state
            ),
            "provider_setup_completion_provider_setup_gate_state": (
                self.provider_setup_completion_provider_setup_gate_state
            ),
            "provider_setup_completion_provider_execution_gate_state": (
                self.provider_setup_completion_provider_execution_gate_state
            ),
            "provider_setup_completion_sdk_handoff_state": (
                self.provider_setup_completion_sdk_handoff_state
            ),
            "provider_setup_completion_sdk_handoff_label": (
                self.provider_setup_completion_sdk_handoff_label
            ),
            "provider_setup_completion_functional_ai_criteria_state": (
                self.provider_setup_completion_functional_ai_criteria_state
            ),
            "provider_setup_completion_v18_continuation_state": (
                self.provider_setup_completion_v18_continuation_state
            ),
            "provider_setup_completion_provider_visible_data": (
                self.provider_setup_completion_provider_visible_data
            ),
            "provider_setup_completion_sent_to_provider": (
                self.provider_setup_completion_sent_to_provider
            ),
            "provider_setup_completion_can_accept_prompts": (
                self.provider_setup_completion_can_accept_prompts
            ),
            "provider_setup_completion_network_egress_state": (
                self.provider_setup_completion_network_egress_state
            ),
            "provider_setup_completion_memory_state": (
                self.provider_setup_completion_memory_state
            ),
            "provider_setup_completion_voice_state": (
                self.provider_setup_completion_voice_state
            ),
            "future_consent_capture_handoff_state": self.future_consent_capture_handoff_state,
            "consent_collection_fold_down_posture": self.consent_collection_fold_down_posture,
        }

    def as_renderer_payload(self) -> dict[str, object]:
        return {
            "packageId": self.package_id,
            "sliceIds": list(self.slice_ids),
            "stateId": self.state_id,
            "mode": self.mode,
            "availability": self.availability,
            "providerLabel": self.provider_label,
            "providerKind": self.provider_kind,
            "statusLabel": self.status_label,
            "disabledReason": self.disabled_reason,
            "selectedProviderId": self.selected_provider_id,
            "providerSelectionState": self.provider_selection_state,
            "providerSelectionLabel": self.provider_selection_label,
            "providerConfigurationState": self.provider_configuration_state,
            "providerConfigurationLabel": self.provider_configuration_label,
            "providerRegistryState": self.provider_registry_state,
            "providerRegistryLabel": self.provider_registry_label,
            "configuredProviderCount": self.configured_provider_count,
            "availableProviderCount": self.available_provider_count,
            "hardwareCapabilityState": self.hardware_capability_state,
            "hardwareCapabilityLabel": self.hardware_capability_label,
            "gpuCapabilityState": self.gpu_capability_state,
            "gpuCapabilityLabel": self.gpu_capability_label,
            "cpuFallbackState": self.cpu_fallback_state,
            "cpuFallbackLabel": self.cpu_fallback_label,
            "powerState": self.power_state,
            "powerStateLabel": self.power_state_label,
            "thermalGuardrailState": self.thermal_guardrail_state,
            "thermalGuardrailLabel": self.thermal_guardrail_label,
            "modelWorkloadState": self.model_workload_state,
            "modelWorkloadLabel": self.model_workload_label,
            "capabilityRecommendationState": self.capability_recommendation_state,
            "capabilityRecommendationLabel": self.capability_recommendation_label,
            "hardwareDetectionLevel": self.hardware_detection_level,
            "hardwareDetectionLabel": self.hardware_detection_label,
            "capabilitySnapshotPolicy": self.capability_snapshot_policy,
            "capabilitySnapshotSource": self.capability_snapshot_source,
            "capabilitySnapshotBudgetLabel": self.capability_snapshot_budget_label,
            "ramReadinessState": self.ram_readiness_state,
            "ramReadinessLabel": self.ram_readiness_label,
            "diskReadinessState": self.disk_readiness_state,
            "diskReadinessLabel": self.disk_readiness_label,
            "modelWorkloadMetadataState": self.model_workload_metadata_state,
            "modelWorkloadMetadataLabel": self.model_workload_metadata_label,
            "capabilityPackLifecycleState": self.capability_pack_lifecycle_state,
            "capabilityPackLifecycleLabel": self.capability_pack_lifecycle_label,
            "capabilityPackDownloadState": self.capability_pack_download_state,
            "capabilityPackDownloadLabel": self.capability_pack_download_label,
            "capabilityPackManifestSchemaVersion": self.capability_pack_manifest_schema_version,
            "capabilityPackManifestState": self.capability_pack_manifest_state,
            "capabilityPackSourceType": self.capability_pack_source_type,
            "capabilityPackChecksumState": self.capability_pack_checksum_state,
            "capabilityPackSignatureState": self.capability_pack_signature_state,
            "capabilityPackCompatibilityState": self.capability_pack_compatibility_state,
            "capabilityPackDiskRequirement": self.capability_pack_disk_requirement,
            "capabilityPackRamRequirement": self.capability_pack_ram_requirement,
            "capabilityPackGpuRequirement": self.capability_pack_gpu_requirement,
            "capabilityPackInstallState": self.capability_pack_install_state,
            "capabilityPackUpdateState": self.capability_pack_update_state,
            "capabilityPackUninstallState": self.capability_pack_uninstall_state,
            "dataClassificationState": self.data_classification_state,
            "dataClassificationLabel": self.data_classification_label,
            "dataClassificationSchemaVersion": self.data_classification_schema_version,
            "providerVisibleDataGuarantee": self.provider_visible_data_guarantee,
            "memoryContextState": self.memory_context_state,
            "memoryContextLabel": self.memory_context_label,
            "memoryIndexingState": self.memory_indexing_state,
            "retrievalState": self.retrieval_state,
            "learningState": self.learning_state,
            "persistenceState": self.persistence_state,
            "futureMemoryEligibilityMarker": self.future_memory_eligibility_marker,
            "consentEnvelopeState": self.consent_envelope_state,
            "auditEnvelopeState": self.audit_envelope_state,
            "secretBoundaryState": self.secret_boundary_state,
            "networkEgressState": self.network_egress_state,
            "auditSecretsState": self.audit_secrets_state,
            "auditSecretsLabel": self.audit_secrets_label,
            "windowsResilienceState": self.windows_resilience_state,
            "windowsResilienceLabel": self.windows_resilience_label,
            "offlineDegradedState": self.offline_degraded_state,
            "offlineDegradedLabel": self.offline_degraded_label,
            "personaCoreVoiceState": self.persona_core_voice_state,
            "personaCoreVoiceLabel": self.persona_core_voice_label,
            "voiceRuntimeState": self.voice_runtime_state,
            "voiceRuntimeLabel": self.voice_runtime_label,
            "validationProofGateState": self.validation_proof_gate_state,
            "validationProofGateLabel": self.validation_proof_gate_label,
            "abuseEvalState": self.abuse_eval_state,
            "abuseEvalLabel": self.abuse_eval_label,
            "releaseProofGateState": self.release_proof_gate_state,
            "releaseProofGateLabel": self.release_proof_gate_label,
            "coreDesktopCopyContractVersion": self.core_desktop_copy_contract_version,
            "coreDesktopRuntimeStateContract": self.core_desktop_runtime_state_contract,
            "disabledPromptBehaviorContract": self.disabled_prompt_behavior_contract,
            "goldenProviderStateFixtures": self.golden_provider_state_fixtures,
            "validatorExpansionState": self.validator_expansion_state,
            "contractReadyMarker": self.contract_ready_marker,
            "uiReadyMarker": self.ui_ready_marker,
            "validatorReadyMarker": self.validator_ready_marker,
            "futureImplementationGatedMarker": self.future_implementation_gated_marker,
            "privacyScope": self.privacy_scope,
            "privacyLabel": self.privacy_label,
            "providerVisibleData": self.provider_visible_data,
            "providerVisibleDataLabel": self.provider_visible_data_label,
            "providerVisibleDataDetail": self.provider_visible_data_detail,
            "providerInteractionState": self.provider_interaction_state,
            "providerInteractionLabel": self.provider_interaction_label,
            "providerInteractionDetail": self.provider_interaction_detail,
            "providerConsentBoundaryLabel": self.provider_consent_boundary_label,
            "providerNextActionLabel": self.provider_next_action_label,
            "localActionResultSchemaVersion": self.local_action_result_schema_version,
            "localActionResultState": self.local_action_result_state,
            "localActionResultLabel": self.local_action_result_label,
            "localActionResultDetail": self.local_action_result_detail,
            "localActionResultProviderVisibleData": self.local_action_result_provider_visible_data,
            "localActionResultSentToProvider": self.local_action_result_sent_to_provider,
            "localActionResultCanAcceptPrompts": self.local_action_result_can_accept_prompts,
            "localActionResultPromptSendPosture": self.local_action_result_prompt_send_posture,
            "localActionResultNetworkEgressState": self.local_action_result_network_egress_state,
            "localActionResultMemoryIndexingState": self.local_action_result_memory_indexing_state,
            "aiControlCenterDiagnosticsSchemaVersion": (
                self.ai_control_center_diagnostics_schema_version
            ),
            "aiControlCenterDiagnosticState": self.ai_control_center_diagnostic_state,
            "aiControlCenterDiagnosticLabel": self.ai_control_center_diagnostic_label,
            "aiControlCenterProviderBoundaryLabel": (
                self.ai_control_center_provider_boundary_label
            ),
            "aiControlCenterProviderBoundaryDetail": (
                self.ai_control_center_provider_boundary_detail
            ),
            "aiControlCenterBlockedActionLabel": self.ai_control_center_blocked_action_label,
            "aiControlCenterBlockedActionDetail": self.ai_control_center_blocked_action_detail,
            "aiControlCenterUnavailableCapabilityLabel": (
                self.ai_control_center_unavailable_capability_label
            ),
            "aiControlCenterUnavailableCapabilityDetail": (
                self.ai_control_center_unavailable_capability_detail
            ),
            "aiControlCenterRecoveryLabel": self.ai_control_center_recovery_label,
            "aiControlCenterRecoveryDetail": self.ai_control_center_recovery_detail,
            "aiControlCenterDegradedPathLabel": self.ai_control_center_degraded_path_label,
            "aiControlCenterDegradedPathDetail": self.ai_control_center_degraded_path_detail,
            "aiControlCenterStateTaxonomy": [
                dict(item) for item in self.ai_control_center_state_taxonomy
            ],
            "localAiReadinessReport": dict(self.local_ai_readiness_report or {}),
            "localStorage": self.local_storage,
            "consentState": self.consent_state,
            "consentLabel": self.consent_label,
            "interactionAffordance": self.interaction_affordance,
            "interactionLabel": self.interaction_label,
            "interactionDisabledReason": self.interaction_disabled_reason,
            "noProviderFallbackLabel": self.no_provider_fallback_label,
            "promptAcceptance": self.prompt_acceptance,
            "externalCalls": self.external_calls,
            "modelState": self.model_state,
            "capabilityPackState": self.capability_pack_state,
            "sourceTruth": self.source_truth,
            "runtimeStateSchemaVersion": self.runtime_state_schema_version,
            "runtimeStateCategory": self.runtime_state_category,
            "runtimeStateLabel": self.runtime_state_label,
            "runtimeReasonCode": self.runtime_reason_code,
            "runtimeReasonLabel": self.runtime_reason_label,
            "runtimeConfigSchemaVersion": self.runtime_config_schema_version,
            "runtimeConfigState": self.runtime_config_state,
            "runtimeConfigLabel": self.runtime_config_label,
            "runtimeConfigMigration": self.runtime_config_migration,
            "runtimeConfigValid": self.runtime_config_valid,
            "runtimeFailClosed": self.runtime_fail_closed,
            "runtimeProvenance": self.runtime_provenance,
            "runtimeProvenanceLabel": self.runtime_provenance_label,
            "surfaceRole": self.surface_role,
            "providerOptions": [option.as_renderer_payload() for option in self.provider_options],
            "providerRegistry": [option.as_renderer_payload() for option in self.provider_options],
            "foundationReadiness": [item.as_renderer_payload() for item in self.foundation_readiness_items],
            "providerReadinessState": self.provider_readiness_state,
            "providerReadinessLabel": self.provider_readiness_label,
            "setupEligibilityState": self.setup_eligibility_state,
            "setupEligibilityLabel": self.setup_eligibility_label,
            "setupBlockerState": self.setup_blocker_state,
            "setupBlockerLabel": self.setup_blocker_label,
            "readinessReasonCode": self.readiness_reason_code,
            "readinessReasonLabel": self.readiness_reason_label,
            "readinessProvenance": self.readiness_provenance,
            "readinessProvenanceLabel": self.readiness_provenance_label,
            "readinessStateSchemaVersion": self.readiness_state_schema_version,
            "readinessConfigSchemaVersion": self.readiness_config_schema_version,
            "readinessConfigState": self.readiness_config_state,
            "readinessConfigLabel": self.readiness_config_label,
            "readinessConfigMigration": self.readiness_config_migration,
            "readinessConfigValid": self.readiness_config_valid,
            "futureProviderGateStatus": self.future_provider_gate_status,
            "futureProviderGateLabel": self.future_provider_gate_label,
            "capabilityPackEligibilityState": self.capability_pack_eligibility_state,
            "capabilityPackEligibilityLabel": self.capability_pack_eligibility_label,
            "capabilityPackManifestValidityState": self.capability_pack_manifest_validity_state,
            "capabilityPackManifestValidityLabel": self.capability_pack_manifest_validity_label,
            "capabilityPackSourceTrustState": self.capability_pack_source_trust_state,
            "capabilityPackSourceTrustLabel": self.capability_pack_source_trust_label,
            "capabilityPackCompatibilityPostureState": self.capability_pack_compatibility_posture_state,
            "capabilityPackCompatibilityPostureLabel": self.capability_pack_compatibility_posture_label,
            "capabilityPackCpuRequirementPosture": self.capability_pack_cpu_requirement_posture,
            "capabilityPackGpuRequirementPosture": self.capability_pack_gpu_requirement_posture,
            "capabilityPackRamRequirementPosture": self.capability_pack_ram_requirement_posture,
            "capabilityPackDiskRequirementPosture": self.capability_pack_disk_requirement_posture,
            "installIntentState": self.install_intent_state,
            "installIntentLabel": self.install_intent_label,
            "capabilityPackDownloadBlockedReason": self.capability_pack_download_blocked_reason,
            "capabilityPackInstallBlockedReason": self.capability_pack_install_blocked_reason,
            "capabilityPackUpdateBlockedReason": self.capability_pack_update_blocked_reason,
            "capabilityPackUninstallBlockedReason": self.capability_pack_uninstall_blocked_reason,
            "laneBoundarySchemaVersion": self.lane_boundary_schema_version,
            "publicLaneBoundaryState": self.public_lane_boundary_state,
            "publicLaneBoundaryLabel": self.public_lane_boundary_label,
            "developerLaneBoundaryState": self.developer_lane_boundary_state,
            "developerLaneBoundaryLabel": self.developer_lane_boundary_label,
            "ownerLaneBoundaryState": self.owner_lane_boundary_state,
            "ownerLaneBoundaryLabel": self.owner_lane_boundary_label,
            "privateSetupBoundaryState": self.private_setup_boundary_state,
            "privateSetupAuthorized": self.private_setup_authorized,
            "privateMaterialVisible": self.private_material_visible,
            "ownerMemoryEnabled": self.owner_memory_enabled,
            "ownerAgentsEnabled": self.owner_agents_enabled,
            "actionPermissionMatrix": [item.as_renderer_payload() for item in self.action_permission_matrix],
            "providerActivationState": self.provider_activation_state,
            "providerActivationLabel": self.provider_activation_label,
            "activationEligibilityState": self.activation_eligibility_state,
            "activationEligibilityLabel": self.activation_eligibility_label,
            "activationBlockerState": self.activation_blocker_state,
            "activationBlockerLabel": self.activation_blocker_label,
            "activationReasonCode": self.activation_reason_code,
            "activationReasonLabel": self.activation_reason_label,
            "activationProvenance": self.activation_provenance,
            "activationProvenanceLabel": self.activation_provenance_label,
            "activationStateSchemaVersion": self.activation_state_schema_version,
            "activationConfigSchemaVersion": self.activation_config_schema_version,
            "activationConfigState": self.activation_config_state,
            "activationConfigLabel": self.activation_config_label,
            "activationConfigMigration": self.activation_config_migration,
            "activationConfigValid": self.activation_config_valid,
            "futureActivationGateStatus": self.future_activation_gate_status,
            "futureActivationGateLabel": self.future_activation_gate_label,
            "providerAdapterPosture": self.provider_adapter_posture,
            "providerAdapterLabel": self.provider_adapter_label,
            "providerAdapterKind": self.provider_adapter_kind,
            "providerAdapterAvailabilityState": self.provider_adapter_availability_state,
            "providerAdapterAvailabilityLabel": self.provider_adapter_availability_label,
            "providerAdapterExecutionPosture": self.provider_adapter_execution_posture,
            "providerAdapterExecutionLabel": self.provider_adapter_execution_label,
            "providerMetadataContractVersion": self.provider_metadata_contract_version,
            "providerConfigEnvelopeVersion": self.provider_config_envelope_version,
            "providerActivationHandoffState": self.provider_activation_handoff_state,
            "providerActivationHandoffLabel": self.provider_activation_handoff_label,
            "futureSdkIntegrationBoundary": self.future_sdk_integration_boundary,
            "promptExecutionGateState": self.prompt_execution_gate_state,
            "promptExecutionGateLabel": self.prompt_execution_gate_label,
            "modelExecutionGateState": self.model_execution_gate_state,
            "modelExecutionGateLabel": self.model_execution_gate_label,
            "providerExecutionGateState": self.provider_execution_gate_state,
            "providerExecutionGateLabel": self.provider_execution_gate_label,
            "readinessGateState": self.readiness_gate_state,
            "consentGateState": self.consent_gate_state,
            "capabilityGateState": self.capability_gate_state,
            "manifestGateState": self.manifest_gate_state,
            "adapterGateState": self.adapter_gate_state,
            "safetyEvalGateState": self.safety_eval_gate_state,
            "networkEgressGateState": self.network_egress_gate_state,
            "memoryIndexingGateState": self.memory_indexing_gate_state,
            "voiceCoreSyncGateState": self.voice_core_sync_gate_state,
            "versionJumpGateState": self.version_jump_gate_state,
            "functionalAiCriteriaState": self.functional_ai_criteria_state,
            "functionalAiCriteriaLabel": self.functional_ai_criteria_label,
            "v18PrebetaReadinessState": self.v18_prebeta_readiness_state,
            "v18PrebetaReadinessLabel": self.v18_prebeta_readiness_label,
            "providerExecutionReadinessState": self.provider_execution_readiness_state,
            "providerExecutionReadinessLabel": self.provider_execution_readiness_label,
            "promptExecutionReadinessState": self.prompt_execution_readiness_state,
            "promptExecutionReadinessLabel": self.prompt_execution_readiness_label,
            "modelExecutionReadinessState": self.model_execution_readiness_state,
            "modelExecutionReadinessLabel": self.model_execution_readiness_label,
            "executionEligibilityState": self.execution_eligibility_state,
            "executionEligibilityLabel": self.execution_eligibility_label,
            "executionBlockerState": self.execution_blocker_state,
            "executionBlockerLabel": self.execution_blocker_label,
            "executionReasonCode": self.execution_reason_code,
            "executionReasonLabel": self.execution_reason_label,
            "executionProvenance": self.execution_provenance,
            "executionProvenanceLabel": self.execution_provenance_label,
            "executionStateSchemaVersion": self.execution_state_schema_version,
            "executionConfigSchemaVersion": self.execution_config_schema_version,
            "executionConfigState": self.execution_config_state,
            "executionConfigLabel": self.execution_config_label,
            "executionConfigMigration": self.execution_config_migration,
            "executionConfigValid": self.execution_config_valid,
            "executionApprovalStatus": self.execution_approval_status,
            "executionApprovalLabel": self.execution_approval_label,
            "providerPathStatus": self.provider_path_status,
            "providerPathLabel": self.provider_path_label,
            "providerSelectionPosture": self.provider_selection_posture,
            "providerSelectionPostureLabel": self.provider_selection_posture_label,
            "adapterSelectionPosture": self.adapter_selection_posture,
            "adapterSelectionPostureLabel": self.adapter_selection_posture_label,
            "promptAcceptanceGateState": self.prompt_acceptance_gate_state,
            "promptAcceptanceGateLabel": self.prompt_acceptance_gate_label,
            "promptRoutingGateState": self.prompt_routing_gate_state,
            "promptRoutingGateLabel": self.prompt_routing_gate_label,
            "promptSendPosture": self.prompt_send_posture,
            "promptSendLabel": self.prompt_send_label,
            "modelExecutionStatus": self.model_execution_status,
            "modelExecutionStatusLabel": self.model_execution_status_label,
            "modelWorkloadReadinessPosture": self.model_workload_readiness_posture,
            "modelWorkloadReadinessLabel": self.model_workload_readiness_label,
            "providerVisibleDataExecutionPosture": self.provider_visible_data_execution_posture,
            "providerVisibleDataExecutionLabel": self.provider_visible_data_execution_label,
            "externalCallReadinessState": self.external_call_readiness_state,
            "externalCallReadinessLabel": self.external_call_readiness_label,
            "safetyEvalReadinessState": self.safety_eval_readiness_state,
            "safetyEvalReadinessLabel": self.safety_eval_readiness_label,
            "dataClassificationGateState": self.data_classification_gate_state,
            "dataClassificationGateLabel": self.data_classification_gate_label,
            "executionProofMarker": self.execution_proof_marker,
            "futureExecutionValidationMarker": self.future_execution_validation_marker,
            "functionalAiReleaseGateState": self.functional_ai_release_gate_state,
            "functionalAiReleaseGateLabel": self.functional_ai_release_gate_label,
            "v18ReleaseGateState": self.v18_release_gate_state,
            "v18ReleaseGateLabel": self.v18_release_gate_label,
            "providerPathReadinessState": self.provider_path_readiness_state,
            "providerPathReadinessLabel": self.provider_path_readiness_label,
            "providerPathEligibilityState": self.provider_path_eligibility_state,
            "providerPathEligibilityLabel": self.provider_path_eligibility_label,
            "providerPathBlockerState": self.provider_path_blocker_state,
            "providerPathBlockerLabel": self.provider_path_blocker_label,
            "providerPathReasonCode": self.provider_path_reason_code,
            "providerPathReasonLabel": self.provider_path_reason_label,
            "providerPathProvenance": self.provider_path_provenance,
            "providerPathProvenanceLabel": self.provider_path_provenance_label,
            "providerPathStateSchemaVersion": self.provider_path_state_schema_version,
            "providerPathConfigSchemaVersion": self.provider_path_config_schema_version,
            "providerPathConfigState": self.provider_path_config_state,
            "providerPathConfigLabel": self.provider_path_config_label,
            "providerPathConfigMigration": self.provider_path_config_migration,
            "providerPathConfigValid": self.provider_path_config_valid,
            "providerPathApprovalStatus": self.provider_path_approval_status,
            "providerPathApprovalLabel": self.provider_path_approval_label,
            "providerProfileId": self.provider_profile_id,
            "providerProfileKind": self.provider_profile_kind,
            "providerProfileDisplayName": self.provider_profile_display_name,
            "providerProfileSource": self.provider_profile_source,
            "providerProfileMetadataContractVersion": self.provider_profile_metadata_contract_version,
            "providerProfileAvailable": self.provider_profile_available,
            "providerSdkRequirementPosture": self.provider_sdk_requirement_posture,
            "providerNetworkRequirementPosture": self.provider_network_requirement_posture,
            "providerConfigStatus": self.provider_config_status,
            "providerAvailabilityPosture": self.provider_availability_posture,
            "providerSetupApprovalStatus": self.provider_setup_approval_status,
            "providerExecutionApprovalStatus": self.provider_execution_approval_status,
            "providerVisibleDataScope": self.provider_visible_data_scope,
            "localNullProviderFallbackStatus": self.local_null_provider_fallback_status,
            "futureSdkHandoffMarker": self.future_sdk_handoff_marker,
            "futureProviderSetupHandoffMarker": self.future_provider_setup_handoff_marker,
            "consentReadinessState": self.consent_readiness_state,
            "consentReadinessLabel": self.consent_readiness_label,
            "consentStateSchemaVersion": self.consent_state_schema_version,
            "consentConfigSchemaVersion": self.consent_config_schema_version,
            "consentConfigMigration": self.consent_config_migration,
            "setupConsentState": self.setup_consent_state,
            "setupConsentLabel": self.setup_consent_label,
            "setupConsentBlockerState": self.setup_consent_blocker_state,
            "setupConsentBlockerLabel": self.setup_consent_blocker_label,
            "setupConsentReasonCode": self.setup_consent_reason_code,
            "setupConsentReasonLabel": self.setup_consent_reason_label,
            "setupConsentProvenance": self.setup_consent_provenance,
            "setupConsentProvenanceLabel": self.setup_consent_provenance_label,
            "setupConsentHandoffState": self.setup_consent_handoff_state,
            "setupConsentHandoffLabel": self.setup_consent_handoff_label,
            "executionConsentState": self.execution_consent_state,
            "executionConsentLabel": self.execution_consent_label,
            "executionConsentBlockerState": self.execution_consent_blocker_state,
            "executionConsentBlockerLabel": self.execution_consent_blocker_label,
            "executionConsentReasonCode": self.execution_consent_reason_code,
            "executionConsentReasonLabel": self.execution_consent_reason_label,
            "executionConsentProvenance": self.execution_consent_provenance,
            "executionConsentProvenanceLabel": self.execution_consent_provenance_label,
            "executionConsentHandoffState": self.execution_consent_handoff_state,
            "executionConsentHandoffLabel": self.execution_consent_handoff_label,
            "providerVisibleDataRequirementState": self.provider_visible_data_requirement_state,
            "providerVisibleDataRequirementLabel": self.provider_visible_data_requirement_label,
            "dataClassificationPostureState": self.data_classification_posture_state,
            "dataClassificationPostureLabel": self.data_classification_posture_label,
            "auditEnvelopePostureState": self.audit_envelope_posture_state,
            "auditEnvelopePostureLabel": self.audit_envelope_posture_label,
            "localOnlyStatusPosture": self.local_only_status_posture,
            "localOnlyStatusLabel": self.local_only_status_label,
            "providerSetupFutureGatedPosture": self.provider_setup_future_gated_posture,
            "providerSetupFutureGatedLabel": self.provider_setup_future_gated_label,
            "providerExecutionFutureGatedPosture": self.provider_execution_future_gated_posture,
            "providerExecutionFutureGatedLabel": self.provider_execution_future_gated_label,
            "providerPathGateState": self.provider_path_gate_state,
            "providerConfigGateState": self.provider_config_gate_state,
            "setupConsentGateState": self.setup_consent_gate_state,
            "executionConsentGateState": self.execution_consent_gate_state,
            "providerVisibleDataGateState": self.provider_visible_data_gate_state,
            "auditGateState": self.audit_gate_state,
            "setupFlowReadinessState": self.setup_flow_readiness_state,
            "setupFlowReadinessLabel": self.setup_flow_readiness_label,
            "setupFlowEligibilityState": self.setup_flow_eligibility_state,
            "setupFlowEligibilityLabel": self.setup_flow_eligibility_label,
            "setupFlowBlockerState": self.setup_flow_blocker_state,
            "setupFlowBlockerLabel": self.setup_flow_blocker_label,
            "setupFlowReasonCode": self.setup_flow_reason_code,
            "setupFlowReasonLabel": self.setup_flow_reason_label,
            "setupFlowProvenance": self.setup_flow_provenance,
            "setupFlowProvenanceLabel": self.setup_flow_provenance_label,
            "setupFlowStateSchemaVersion": self.setup_flow_state_schema_version,
            "setupFlowConfigSchemaVersion": self.setup_flow_config_schema_version,
            "setupFlowConfigState": self.setup_flow_config_state,
            "setupFlowConfigLabel": self.setup_flow_config_label,
            "setupFlowConfigMigration": self.setup_flow_config_migration,
            "setupFlowConfigValid": self.setup_flow_config_valid,
            "setupFlowApprovalStatus": self.setup_flow_approval_status,
            "setupFlowApprovalLabel": self.setup_flow_approval_label,
            "providerSetupHandoffPosture": self.provider_setup_handoff_posture,
            "providerSetupHandoffLabel": self.provider_setup_handoff_label,
            "providerConsentHandoffPosture": self.provider_consent_handoff_posture,
            "providerConsentHandoffLabel": self.provider_consent_handoff_label,
            "providerPathHandoffPosture": self.provider_path_handoff_posture,
            "providerPathHandoffLabel": self.provider_path_handoff_label,
            "consentFlowReadinessState": self.consent_flow_readiness_state,
            "consentFlowReadinessLabel": self.consent_flow_readiness_label,
            "consentFlowEligibilityState": self.consent_flow_eligibility_state,
            "consentFlowEligibilityLabel": self.consent_flow_eligibility_label,
            "consentFlowBlockerState": self.consent_flow_blocker_state,
            "consentFlowBlockerLabel": self.consent_flow_blocker_label,
            "consentFlowReasonCode": self.consent_flow_reason_code,
            "consentFlowReasonLabel": self.consent_flow_reason_label,
            "consentFlowProvenance": self.consent_flow_provenance,
            "consentFlowProvenanceLabel": self.consent_flow_provenance_label,
            "consentFlowStateSchemaVersion": self.consent_flow_state_schema_version,
            "consentFlowConfigSchemaVersion": self.consent_flow_config_schema_version,
            "consentFlowConfigState": self.consent_flow_config_state,
            "consentFlowConfigLabel": self.consent_flow_config_label,
            "consentFlowConfigMigration": self.consent_flow_config_migration,
            "consentFlowConfigValid": self.consent_flow_config_valid,
            "consentFlowApprovalStatus": self.consent_flow_approval_status,
            "consentFlowApprovalLabel": self.consent_flow_approval_label,
            "consentCollectionPosture": self.consent_collection_posture,
            "consentCollectionLabel": self.consent_collection_label,
            "dataVisibilityConsentPosture": self.data_visibility_consent_posture,
            "dataVisibilityConsentLabel": self.data_visibility_consent_label,
            "setupFlowGateState": self.setup_flow_gate_state,
            "consentFlowGateState": self.consent_flow_gate_state,
            "setupApprovalGateState": self.setup_approval_gate_state,
            "executionApprovalGateState": self.execution_approval_gate_state,
            "desktopAiOwnedReadinessDisplayState": self.desktop_ai_owned_readiness_display_state,
            "desktopAiOwnedReadinessDisplayLabel": self.desktop_ai_owned_readiness_display_label,
            "providerSetupContractReadinessState": self.provider_setup_contract_readiness_state,
            "providerSetupContractReadinessLabel": self.provider_setup_contract_readiness_label,
            "providerSetupContractEligibilityState": self.provider_setup_contract_eligibility_state,
            "providerSetupContractEligibilityLabel": self.provider_setup_contract_eligibility_label,
            "providerSetupContractBlockerState": self.provider_setup_contract_blocker_state,
            "providerSetupContractBlockerLabel": self.provider_setup_contract_blocker_label,
            "providerSetupContractReasonCode": self.provider_setup_contract_reason_code,
            "providerSetupContractReasonLabel": self.provider_setup_contract_reason_label,
            "providerSetupContractProvenance": self.provider_setup_contract_provenance,
            "providerSetupContractProvenanceLabel": self.provider_setup_contract_provenance_label,
            "providerSetupContractStateSchemaVersion": self.provider_setup_contract_state_schema_version,
            "providerSetupContractConfigSchemaVersion": self.provider_setup_contract_config_schema_version,
            "providerSetupContractConfigState": self.provider_setup_contract_config_state,
            "providerSetupContractConfigLabel": self.provider_setup_contract_config_label,
            "providerSetupContractConfigMigration": self.provider_setup_contract_config_migration,
            "providerSetupContractConfigValid": self.provider_setup_contract_config_valid,
            "providerSetupContractApprovalStatus": self.provider_setup_contract_approval_status,
            "providerSetupContractApprovalLabel": self.provider_setup_contract_approval_label,
            "providerSetupContractGateState": self.provider_setup_contract_gate_state,
            "providerProfileGateState": self.provider_profile_gate_state,
            "capabilityGateState": self.capability_gate_state,
            "manifestGateState": self.manifest_gate_state,
            "safetyEvalGateState": self.safety_eval_gate_state,
            "networkGateState": self.network_gate_state,
            "memoryIndexingGateState": self.memory_indexing_gate_state,
            "voiceCoreSyncGateState": self.voice_core_sync_gate_state,
            "versionJumpGateState": self.version_jump_gate_state,
            "providerProfileRequiredFields": list(self.provider_profile_required_fields),
            "providerConfigRequiredFields": list(self.provider_config_required_fields),
            "providerSetupPrerequisitePosture": self.provider_setup_prerequisite_posture,
            "providerSetupValidationPosture": self.provider_setup_validation_posture,
            "providerSetupUiProofPosture": self.provider_setup_ui_proof_posture,
            "futureSetupBranchHandoffState": self.future_setup_branch_handoff_state,
            "providerSetupContractFoldDownPosture": self.provider_setup_contract_fold_down_posture,
            "providerSetupFoundationState": self.provider_setup_foundation_state,
            "providerSetupFoundationLabel": self.provider_setup_foundation_label,
            "providerSetupFoundationEligibilityState": (
                self.provider_setup_foundation_eligibility_state
            ),
            "providerSetupFoundationEligibilityLabel": (
                self.provider_setup_foundation_eligibility_label
            ),
            "providerSetupFoundationBlockerState": self.provider_setup_foundation_blocker_state,
            "providerSetupFoundationBlockerLabel": self.provider_setup_foundation_blocker_label,
            "providerSetupFoundationReasonCode": self.provider_setup_foundation_reason_code,
            "providerSetupFoundationReasonLabel": self.provider_setup_foundation_reason_label,
            "providerSetupFoundationProvenance": self.provider_setup_foundation_provenance,
            "providerSetupFoundationProvenanceLabel": self.provider_setup_foundation_provenance_label,
            "providerSetupFoundationStateSchemaVersion": (
                self.provider_setup_foundation_state_schema_version
            ),
            "providerSetupFoundationConfigSchemaVersion": (
                self.provider_setup_foundation_config_schema_version
            ),
            "providerSetupFoundationConfigState": self.provider_setup_foundation_config_state,
            "providerSetupFoundationConfigLabel": self.provider_setup_foundation_config_label,
            "providerSetupFoundationConfigMigration": (
                self.provider_setup_foundation_config_migration
            ),
            "providerSetupFoundationConfigValid": self.provider_setup_foundation_config_valid,
            "providerSetupFoundationSetupEntryState": (
                self.provider_setup_foundation_setup_entry_state
            ),
            "providerSetupFoundationSetupEntryLabel": (
                self.provider_setup_foundation_setup_entry_label
            ),
            "providerSetupFoundationProfileDraftStatus": (
                self.provider_setup_foundation_profile_draft_status
            ),
            "providerSetupFoundationProfileDraftLabel": (
                self.provider_setup_foundation_profile_draft_label
            ),
            "providerSetupFoundationConfigDraftStatus": (
                self.provider_setup_foundation_config_draft_status
            ),
            "providerSetupFoundationConfigDraftLabel": (
                self.provider_setup_foundation_config_draft_label
            ),
            "providerSetupFoundationValidationStatus": (
                self.provider_setup_foundation_validation_status
            ),
            "providerSetupFoundationValidationLabel": (
                self.provider_setup_foundation_validation_label
            ),
            "providerSetupFoundationPersistenceStatus": (
                self.provider_setup_foundation_persistence_status
            ),
            "providerSetupFoundationPersistenceLabel": (
                self.provider_setup_foundation_persistence_label
            ),
            "providerSetupFoundationApprovalStatus": (
                self.provider_setup_foundation_approval_status
            ),
            "providerSetupFoundationApprovalLabel": (
                self.provider_setup_foundation_approval_label
            ),
            "providerSetupFoundationGateState": self.provider_setup_foundation_gate_state,
            "localNullProviderFallbackProof": self.local_null_provider_fallback_proof,
            "providerSetupImplementationHandoffState": (
                self.provider_setup_implementation_handoff_state
            ),
            "providerSetupImplementationFoldDownPosture": (
                self.provider_setup_implementation_fold_down_posture
            ),
            "consentCollectionFoundationState": self.consent_collection_foundation_state,
            "consentCollectionFoundationLabel": self.consent_collection_foundation_label,
            "consentCollectionEligibilityState": self.consent_collection_eligibility_state,
            "consentCollectionEligibilityLabel": self.consent_collection_eligibility_label,
            "consentCollectionBlockerState": self.consent_collection_blocker_state,
            "consentCollectionBlockerLabel": self.consent_collection_blocker_label,
            "consentCollectionReasonCode": self.consent_collection_reason_code,
            "consentCollectionReasonLabel": self.consent_collection_reason_label,
            "consentCollectionProvenance": self.consent_collection_provenance,
            "consentCollectionProvenanceLabel": self.consent_collection_provenance_label,
            "consentCollectionStateSchemaVersion": self.consent_collection_state_schema_version,
            "consentCollectionConfigSchemaVersion": self.consent_collection_config_schema_version,
            "consentCollectionConfigState": self.consent_collection_config_state,
            "consentCollectionConfigLabel": self.consent_collection_config_label,
            "consentCollectionConfigMigration": self.consent_collection_config_migration,
            "consentCollectionConfigValid": self.consent_collection_config_valid,
            "consentCollectionApprovalStatus": self.consent_collection_approval_status,
            "consentCollectionApprovalLabel": self.consent_collection_approval_label,
            "consentCollectionGateState": self.consent_collection_gate_state,
            "consentCaptureSurfaceState": self.consent_capture_surface_state,
            "consentCaptureSurfaceLabel": self.consent_capture_surface_label,
            "setupConsentCaptureStatus": self.setup_consent_capture_status,
            "setupConsentCaptureLabel": self.setup_consent_capture_label,
            "executionConsentCaptureStatus": self.execution_consent_capture_status,
            "executionConsentCaptureLabel": self.execution_consent_capture_label,
            "consentDataVisibilityReviewStatus": (
                self.consent_data_visibility_review_status
            ),
            "consentDataVisibilityReviewLabel": self.consent_data_visibility_review_label,
            "consentAuditEnvelopeStatus": self.consent_audit_envelope_status,
            "consentAuditEnvelopeLabel": self.consent_audit_envelope_label,
            "consentProvenanceStatus": self.consent_provenance_status,
            "consentProvenanceLabel": self.consent_provenance_label,
            "consentPersistenceStatus": self.consent_persistence_status,
            "consentPersistenceLabel": self.consent_persistence_label,
            "consentCollectionValidationStatus": self.consent_collection_validation_status,
            "consentCollectionValidationLabel": self.consent_collection_validation_label,
            "consentCaptureTransitionSchemaVersion": (
                self.consent_capture_transition_schema_version
            ),
            "consentCaptureLocalRecordSchemaVersion": (
                self.consent_capture_local_record_schema_version
            ),
            "consentCaptureState": self.consent_capture_state,
            "consentCaptureLabel": self.consent_capture_label,
            "consentCaptureRecordState": self.consent_capture_record_state,
            "consentCaptureRecordValid": self.consent_capture_record_valid,
            "consentCaptureLocalWriteRequested": (
                self.consent_capture_local_write_requested
            ),
            "consentCaptureWriteStatus": self.consent_capture_write_status,
            "consentCaptureWriteLabel": self.consent_capture_write_label,
            "consentCaptureWriteBlocker": self.consent_capture_write_blocker,
            "consentCaptureWriteReason": self.consent_capture_write_reason,
            "consentCaptureProvenance": self.consent_capture_provenance,
            "setupConsentCaptured": self.setup_consent_captured,
            "executionConsentCaptured": self.execution_consent_captured,
            "consentCaptureLocalSnapshotStatus": (
                self.consent_capture_local_snapshot_status
            ),
            "consentCaptureDurablePersistenceStatus": (
                self.consent_capture_durable_persistence_status
            ),
            "consentRecordStorageBoundarySchemaVersion": (
                self.consent_record_storage_boundary_schema_version
            ),
            "consentRecordStorageBoundaryState": (
                self.consent_record_storage_boundary_state
            ),
            "consentRecordStorageBoundaryLabel": (
                self.consent_record_storage_boundary_label
            ),
            "consentRecordDurableStorageState": (
                self.consent_record_durable_storage_state
            ),
            "consentRecordDurableStorageLabel": (
                self.consent_record_durable_storage_label
            ),
            "consentRecordRevocationModelState": (
                self.consent_record_revocation_model_state
            ),
            "consentRecordRevocationModelLabel": (
                self.consent_record_revocation_model_label
            ),
            "consentRecordResetModelState": self.consent_record_reset_model_state,
            "consentRecordResetModelLabel": self.consent_record_reset_model_label,
            "consentRecordNoSecretsPosture": self.consent_record_no_secrets_posture,
            "consentRecordProviderPayloadPosture": (
                self.consent_record_provider_payload_posture
            ),
            "consentCaptureAuditSchemaVersion": self.consent_capture_audit_schema_version,
            "consentCaptureAuditStatus": self.consent_capture_audit_status,
            "consentCaptureAuditLabel": self.consent_capture_audit_label,
            "setupExecutionConsentSeparationState": (
                self.setup_execution_consent_separation_state
            ),
            "setupExecutionConsentSeparationLabel": (
                self.setup_execution_consent_separation_label
            ),
            "consentCaptureUiStatusProofState": (
                self.consent_capture_ui_status_proof_state
            ),
            "consentCaptureUiStatusProofLabel": (
                self.consent_capture_ui_status_proof_label
            ),
            "consentCaptureDesktopDisplayState": (
                self.consent_capture_desktop_display_state
            ),
            "consentCaptureProviderSetupHandoffState": (
                self.consent_capture_provider_setup_handoff_state
            ),
            "consentCaptureFunctionalAiCriteriaState": (
                self.consent_capture_functional_ai_criteria_state
            ),
            "consentCaptureV18ContinuationState": (
                self.consent_capture_v18_continuation_state
            ),
            "consentCaptureProviderVisibleData": (
                self.consent_capture_provider_visible_data
            ),
            "consentCaptureSentToProvider": self.consent_capture_sent_to_provider,
            "consentCaptureCanAcceptPrompts": self.consent_capture_can_accept_prompts,
            "consentCapturePromptExecutionState": (
                self.consent_capture_prompt_execution_state
            ),
            "consentCaptureNetworkEgressState": (
                self.consent_capture_network_egress_state
            ),
            "consentCaptureMemoryState": self.consent_capture_memory_state,
            "consentCaptureVoiceState": self.consent_capture_voice_state,
            "durableConsentRecordSchemaVersion": (
                self.durable_consent_record_schema_version
            ),
            "durableConsentStorageBoundarySchemaVersion": (
                self.durable_consent_storage_boundary_schema_version
            ),
            "durableConsentRecordState": self.durable_consent_record_state,
            "durableConsentRecordValid": self.durable_consent_record_valid,
            "durableConsentRecordId": self.durable_consent_record_id,
            "durableConsentProviderProfileId": (
                self.durable_consent_provider_profile_id
            ),
            "durableSetupConsentGranted": self.durable_setup_consent_granted,
            "durableExecutionConsentGranted": (
                self.durable_execution_consent_granted
            ),
            "durableConsentRevoked": self.durable_consent_revoked,
            "durableConsentResetRequested": self.durable_consent_reset_requested,
            "durableConsentExpired": self.durable_consent_expired,
            "durableConsentFailClosedReason": (
                self.durable_consent_fail_closed_reason
            ),
            "durableConsentProvenance": self.durable_consent_provenance,
            "durableConsentAuditEventId": self.durable_consent_audit_event_id,
            "durableConsentMigrationPosture": (
                self.durable_consent_migration_posture
            ),
            "durableConsentLocalStorageBoundary": (
                self.durable_consent_local_storage_boundary
            ),
            "durableConsentStorageState": self.durable_consent_storage_state,
            "durableConsentStorageLabel": self.durable_consent_storage_label,
            "durableConsentNoSecretsPosture": (
                self.durable_consent_no_secrets_posture
            ),
            "durableConsentProviderPayloadPosture": (
                self.durable_consent_provider_payload_posture
            ),
            "durableSetupConsentState": self.durable_setup_consent_state,
            "durableSetupConsentLabel": self.durable_setup_consent_label,
            "durableSetupConsentReasonCode": (
                self.durable_setup_consent_reason_code
            ),
            "durableExecutionConsentState": self.durable_execution_consent_state,
            "durableExecutionConsentLabel": self.durable_execution_consent_label,
            "durableExecutionConsentReasonCode": (
                self.durable_execution_consent_reason_code
            ),
            "durableSetupExecutionConsentSeparationState": (
                self.durable_setup_execution_consent_separation_state
            ),
            "durableSetupExecutionConsentSeparationLabel": (
                self.durable_setup_execution_consent_separation_label
            ),
            "durableConsentStatusProofState": (
                self.durable_consent_status_proof_state
            ),
            "durableConsentStatusProofLabel": (
                self.durable_consent_status_proof_label
            ),
            "durableConsentDesktopDisplayState": (
                self.durable_consent_desktop_display_state
            ),
            "durableConsentProviderSetupHandoffState": (
                self.durable_consent_provider_setup_handoff_state
            ),
            "durableConsentProviderExecutionHandoffState": (
                self.durable_consent_provider_execution_handoff_state
            ),
            "durableConsentFutureHandoffCriteriaState": (
                self.durable_consent_future_handoff_criteria_state
            ),
            "durableConsentFutureHandoffCriteriaLabel": (
                self.durable_consent_future_handoff_criteria_label
            ),
            "consentUxStateSchemaVersion": self.consent_ux_state_schema_version,
            "consentUxIntentSchemaVersion": self.consent_ux_intent_schema_version,
            "consentUxState": self.consent_ux_state,
            "consentUxLabel": self.consent_ux_label,
            "consentUxIntentState": self.consent_ux_intent_state,
            "consentUxIntentLabel": self.consent_ux_intent_label,
            "consentUxSurfaceState": self.consent_ux_surface_state,
            "consentUxSurfaceLabel": self.consent_ux_surface_label,
            "consentUxSetupDisplayState": self.consent_ux_setup_display_state,
            "consentUxSetupDisplayLabel": self.consent_ux_setup_display_label,
            "consentUxExecutionDisplayState": (
                self.consent_ux_execution_display_state
            ),
            "consentUxExecutionDisplayLabel": (
                self.consent_ux_execution_display_label
            ),
            "consentUxRevocationResetState": (
                self.consent_ux_revocation_reset_state
            ),
            "consentUxRevocationResetLabel": (
                self.consent_ux_revocation_reset_label
            ),
            "consentUxWritePosture": self.consent_ux_write_posture,
            "consentUxWriteLabel": self.consent_ux_write_label,
            "consentUxDurableHandoffState": self.consent_ux_durable_handoff_state,
            "consentUxDurableHandoffLabel": self.consent_ux_durable_handoff_label,
            "consentUxProviderSetupGateState": (
                self.consent_ux_provider_setup_gate_state
            ),
            "consentUxProviderExecutionGateState": (
                self.consent_ux_provider_execution_gate_state
            ),
            "consentUxStatusProofState": self.consent_ux_status_proof_state,
            "consentUxStatusProofLabel": self.consent_ux_status_proof_label,
            "consentUxDesktopDisplayState": self.consent_ux_desktop_display_state,
            "consentUxLocalOnlyPosture": self.consent_ux_local_only_posture,
            "consentUxProviderVisibleData": self.consent_ux_provider_visible_data,
            "consentUxSentToProvider": self.consent_ux_sent_to_provider,
            "consentUxCanAcceptPrompts": self.consent_ux_can_accept_prompts,
            "consentUxNetworkEgressState": self.consent_ux_network_egress_state,
            "consentUxMemoryState": self.consent_ux_memory_state,
            "consentUxVoiceState": self.consent_ux_voice_state,
            "consentUxFunctionalAiCriteriaState": (
                self.consent_ux_functional_ai_criteria_state
            ),
            "consentUxV18ContinuationState": self.consent_ux_v18_continuation_state,
            "providerSetupCompletionStateSchemaVersion": (
                self.provider_setup_completion_state_schema_version
            ),
            "providerSetupCompletionConfigSchemaVersion": (
                self.provider_setup_completion_config_schema_version
            ),
            "providerSetupCompletionState": self.provider_setup_completion_state,
            "providerSetupCompletionLabel": self.provider_setup_completion_label,
            "providerSetupCompletionEligibilityState": (
                self.provider_setup_completion_eligibility_state
            ),
            "providerSetupCompletionEligibilityLabel": (
                self.provider_setup_completion_eligibility_label
            ),
            "providerSetupCompletionBlockerState": (
                self.provider_setup_completion_blocker_state
            ),
            "providerSetupCompletionBlockerLabel": (
                self.provider_setup_completion_blocker_label
            ),
            "providerSetupCompletionReasonCode": (
                self.provider_setup_completion_reason_code
            ),
            "providerSetupCompletionReasonLabel": (
                self.provider_setup_completion_reason_label
            ),
            "providerSetupCompletionProvenance": (
                self.provider_setup_completion_provenance
            ),
            "providerSetupCompletionProvenanceLabel": (
                self.provider_setup_completion_provenance_label
            ),
            "providerSetupCompletionConfigState": (
                self.provider_setup_completion_config_state
            ),
            "providerSetupCompletionConfigLabel": (
                self.provider_setup_completion_config_label
            ),
            "providerSetupCompletionConfigMigration": (
                self.provider_setup_completion_config_migration
            ),
            "providerSetupCompletionConfigValid": (
                self.provider_setup_completion_config_valid
            ),
            "providerSetupCompletionProfileStatus": (
                self.provider_setup_completion_profile_status
            ),
            "providerSetupCompletionProfileLabel": (
                self.provider_setup_completion_profile_label
            ),
            "providerSetupCompletionConfigStatus": (
                self.provider_setup_completion_config_status
            ),
            "providerSetupCompletionConfigStatusLabel": (
                self.provider_setup_completion_config_status_label
            ),
            "providerSetupCompletionNoSecretsStatus": (
                self.provider_setup_completion_no_secrets_status
            ),
            "providerSetupCompletionNoSecretsLabel": (
                self.provider_setup_completion_no_secrets_label
            ),
            "providerSetupCompletionValidationStatus": (
                self.provider_setup_completion_validation_status
            ),
            "providerSetupCompletionValidationLabel": (
                self.provider_setup_completion_validation_label
            ),
            "providerSetupCompletionPersistenceStatus": (
                self.provider_setup_completion_persistence_status
            ),
            "providerSetupCompletionPersistenceLabel": (
                self.provider_setup_completion_persistence_label
            ),
            "providerSetupCompletionResetState": (
                self.provider_setup_completion_reset_state
            ),
            "providerSetupCompletionResetLabel": (
                self.provider_setup_completion_reset_label
            ),
            "providerSetupCompletionSetupConsentState": (
                self.provider_setup_completion_setup_consent_state
            ),
            "providerSetupCompletionSetupConsentLabel": (
                self.provider_setup_completion_setup_consent_label
            ),
            "providerSetupCompletionExecutionConsentState": (
                self.provider_setup_completion_execution_consent_state
            ),
            "providerSetupCompletionExecutionConsentLabel": (
                self.provider_setup_completion_execution_consent_label
            ),
            "providerSetupCompletionStatusProofState": (
                self.provider_setup_completion_status_proof_state
            ),
            "providerSetupCompletionStatusProofLabel": (
                self.provider_setup_completion_status_proof_label
            ),
            "providerSetupCompletionDesktopDisplayState": (
                self.provider_setup_completion_desktop_display_state
            ),
            "providerSetupCompletionProviderSetupGateState": (
                self.provider_setup_completion_provider_setup_gate_state
            ),
            "providerSetupCompletionProviderExecutionGateState": (
                self.provider_setup_completion_provider_execution_gate_state
            ),
            "providerSetupCompletionSdkHandoffState": (
                self.provider_setup_completion_sdk_handoff_state
            ),
            "providerSetupCompletionSdkHandoffLabel": (
                self.provider_setup_completion_sdk_handoff_label
            ),
            "providerSetupCompletionFunctionalAiCriteriaState": (
                self.provider_setup_completion_functional_ai_criteria_state
            ),
            "providerSetupCompletionV18ContinuationState": (
                self.provider_setup_completion_v18_continuation_state
            ),
            "providerSetupCompletionProviderVisibleData": (
                self.provider_setup_completion_provider_visible_data
            ),
            "providerSetupCompletionSentToProvider": (
                self.provider_setup_completion_sent_to_provider
            ),
            "providerSetupCompletionCanAcceptPrompts": (
                self.provider_setup_completion_can_accept_prompts
            ),
            "providerSetupCompletionNetworkEgressState": (
                self.provider_setup_completion_network_egress_state
            ),
            "providerSetupCompletionMemoryState": (
                self.provider_setup_completion_memory_state
            ),
            "providerSetupCompletionVoiceState": (
                self.provider_setup_completion_voice_state
            ),
            "futureConsentCaptureHandoffState": self.future_consent_capture_handoff_state,
            "consentCollectionFoldDownPosture": self.consent_collection_fold_down_posture,
            "canAcceptPrompts": False,
            "requiresConsent": self.consent_state == PROVIDER_CONSENT_REQUIRED,
            "sentToProvider": False,
            "storedLocally": False,
        }


def _foundation_readiness_items() -> tuple[AIFoundationReadinessSnapshot, ...]:
    return (
        AIFoundationReadinessSnapshot(
            slice_id=SLC_017_ID,
            label="No-provider shell",
            state="green",
            visible_status="Disabled Assisted Desktop affordance and no-provider fallback are visible",
            proof_status="static-validation-green",
            blocked_work="provider calls",
        ),
        AIFoundationReadinessSnapshot(
            slice_id=SLC_018_ID,
            label="Provider/privacy boundary",
            state="green",
            visible_status="Consent-required provider state and provider-visible-data none are visible",
            proof_status="static-validation-green",
            blocked_work="provider SDK integration",
        ),
        AIFoundationReadinessSnapshot(
            slice_id=SLC_031_ID,
            label="Hardware capability planning",
            state=LOCAL_HARDWARE_CAPABILITY_STATE,
            visible_status="GPU capability is unprobed and CPU fallback is preserved",
            proof_status="planning-validation-green",
            blocked_work="hardware probing and model workload execution",
        ),
        AIFoundationReadinessSnapshot(
            slice_id=SLC_032_ID,
            label="Capability-pack lifecycle",
            state=CAPABILITY_PACK_LIFECYCLE_PLANNED,
            visible_status="Capability packs are not installed and downloads are blocked",
            proof_status="planning-validation-green",
            blocked_work="pack downloads and install/update/uninstall execution",
        ),
        AIFoundationReadinessSnapshot(
            slice_id=SLC_033_ID,
            label="Data, memory, context, audit, and secrets",
            state=MEMORY_CONTEXT_DISABLED,
            visible_status="Memory and context retention are disabled; no secrets are stored",
            proof_status="planning-validation-green",
            blocked_work="memory indexing and persistent context",
        ),
        AIFoundationReadinessSnapshot(
            slice_id=SLC_034_ID,
            label="Windows resilience and platform posture",
            state=WINDOWS_RESILIENCE_PLANNED,
            visible_status="Offline/degraded posture is planned; shortcuts and installers are untouched",
            proof_status="planning-validation-green",
            blocked_work="shortcut, installer, startup, and process-owner changes",
        ),
        AIFoundationReadinessSnapshot(
            slice_id=SLC_035_ID,
            label="Persona, Core, and voice boundary",
            state=PERSONA_CORE_VOICE_BOUNDARY_PLANNED,
            visible_status="ORIN/Core presence stays visual-only and voice runtime is disabled",
            proof_status="planning-validation-green",
            blocked_work="voice runtime and persona/Core sync",
        ),
        AIFoundationReadinessSnapshot(
            slice_id=SLC_036_ID,
            label="Validation, eval, abuse, and release proof gates",
            state=VALIDATION_PROOF_GATES_PLANNED,
            visible_status="Static proof gates are active; abuse/eval and release proof remain gated",
            proof_status="validation-green",
            blocked_work="release execution, artifacts, and live provider eval",
        ),
    )


def _foundation_readiness_fields() -> dict[str, object]:
    return {
        "capability_pack_lifecycle_state": CAPABILITY_PACK_LIFECYCLE_PLANNED,
        "capability_pack_lifecycle_label": "Capability packs: lifecycle planned",
        "capability_pack_download_state": CAPABILITY_PACK_DOWNLOADS_BLOCKED,
        "capability_pack_download_label": "Capability pack downloads: blocked",
        "data_classification_state": DATA_CLASSIFICATION_LOCAL_ONLY,
        "data_classification_label": "Data classification: local-only planning",
        "memory_context_state": MEMORY_CONTEXT_DISABLED,
        "memory_context_label": "Memory/context: disabled; no indexing",
        "audit_secrets_state": AUDIT_SECRETS_PLANNED,
        "audit_secrets_label": "Audit/secrets: planned; no secrets stored",
        "windows_resilience_state": WINDOWS_RESILIENCE_PLANNED,
        "windows_resilience_label": "Windows resilience: planning only",
        "offline_degraded_state": OFFLINE_DEGRADED_PLANNED,
        "offline_degraded_label": "Offline/degraded mode: planned",
        "persona_core_voice_state": PERSONA_CORE_VOICE_BOUNDARY_PLANNED,
        "persona_core_voice_label": "Persona/Core/voice: planning boundary",
        "voice_runtime_state": VOICE_RUNTIME_DISABLED,
        "voice_runtime_label": "Voice runtime: disabled",
        "validation_proof_gate_state": VALIDATION_PROOF_GATES_PLANNED,
        "validation_proof_gate_label": "Validation gates: static proof active",
        "abuse_eval_state": ABUSE_EVAL_PENDING,
        "abuse_eval_label": "Abuse/eval: pending future approval",
        "release_proof_gate_state": RELEASE_PROOF_PENDING,
        "release_proof_gate_label": "Release proof: pending future approval",
        "hardware_detection_level": HARDWARE_DETECTION_LEVEL_1,
        "hardware_detection_label": "Hardware detection: Level 1 safe local static snapshot",
        "capability_snapshot_policy": CAPABILITY_SNAPSHOT_POLICY_LOCAL_STATIC,
        "capability_snapshot_source": CAPABILITY_SNAPSHOT_SOURCE_DEFAULT,
        "capability_snapshot_budget_label": "Capability snapshot budget: static only; no heavy probe",
        "ram_readiness_state": RAM_READINESS_UNPROBED,
        "ram_readiness_label": "RAM readiness: unprobed",
        "disk_readiness_state": DISK_READINESS_UNPROBED,
        "disk_readiness_label": "Disk readiness: unprobed",
        "model_workload_metadata_state": MODEL_WORKLOAD_METADATA_PLANNED,
        "model_workload_metadata_label": "Model workload metadata: planned; no execution",
        "capability_pack_manifest_schema_version": CAPABILITY_PACK_MANIFEST_SCHEMA_VERSION,
        "capability_pack_manifest_state": CAPABILITY_PACK_MANIFEST_PLANNED,
        "capability_pack_source_type": CAPABILITY_PACK_SOURCE_LOCAL_ONLY,
        "capability_pack_checksum_state": CAPABILITY_PACK_CHECKSUM_REQUIRED,
        "capability_pack_signature_state": CAPABILITY_PACK_SIGNATURE_REQUIRED,
        "capability_pack_compatibility_state": CAPABILITY_PACK_COMPATIBILITY_UNPROVEN,
        "capability_pack_disk_requirement": "disk requirement: future manifest required",
        "capability_pack_ram_requirement": "ram requirement: future manifest required",
        "capability_pack_gpu_requirement": "gpu requirement: future manifest required",
        "capability_pack_install_state": CAPABILITY_PACK_INSTALL_BLOCKED,
        "capability_pack_update_state": CAPABILITY_PACK_UPDATE_BLOCKED,
        "capability_pack_uninstall_state": CAPABILITY_PACK_UNINSTALL_BLOCKED,
        "data_classification_schema_version": DATA_CLASSIFICATION_SCHEMA_VERSION,
        "provider_visible_data_guarantee": PROVIDER_VISIBLE_DATA_GUARANTEE_NONE,
        "memory_indexing_state": MEMORY_INDEXING_DISABLED,
        "retrieval_state": RETRIEVAL_DISABLED,
        "learning_state": LEARNING_DISABLED,
        "persistence_state": PERSISTENCE_DISABLED,
        "future_memory_eligibility_marker": FUTURE_MEMORY_ELIGIBILITY_GATED,
        "consent_envelope_state": CONSENT_ENVELOPE_REQUIRED,
        "audit_envelope_state": AUDIT_ENVELOPE_PLANNED,
        "secret_boundary_state": SECRET_BOUNDARY_NO_SECRETS,
        "network_egress_state": NETWORK_EGRESS_BLOCKED,
        "core_desktop_copy_contract_version": CORE_DESKTOP_COPY_CONTRACT_VERSION,
        "core_desktop_runtime_state_contract": CORE_DESKTOP_RUNTIME_STATE_CONTRACT,
        "disabled_prompt_behavior_contract": DISABLED_PROMPT_BEHAVIOR_CONTRACT,
        "golden_provider_state_fixtures": GOLDEN_PROVIDER_STATE_FIXTURES,
        "validator_expansion_state": VALIDATOR_EXPANSION_ACTIVE,
        "contract_ready_marker": CONTRACT_READY_MARKER,
        "ui_ready_marker": UI_READY_MARKER,
        "validator_ready_marker": VALIDATOR_READY_MARKER,
        "future_implementation_gated_marker": FUTURE_IMPLEMENTATION_GATED_MARKER,
        "foundation_readiness_items": _foundation_readiness_items(),
    }


def _provider_boundary_interaction_fields(
    *,
    interaction_label: str,
    interaction_detail: str,
) -> dict[str, str]:
    return {
        "provider_visible_data_detail": "No prompt, file, screen, memory, or telemetry is sent",
        "provider_interaction_state": PROVIDER_BOUNDARY_INTERACTION_PLAN_STATE,
        "provider_interaction_label": interaction_label,
        "provider_interaction_detail": interaction_detail,
        "provider_consent_boundary_label": "Consent boundary: provider setup required before prompts",
        "provider_next_action_label": "Next: provider setup is disabled in this local-only foundation seam",
    }


def _runtime_contract_fields(
    *,
    category: str,
    reason_code: str,
    provenance: str = PROVIDER_RUNTIME_PROVENANCE_DEFAULT_CONFIG,
    config_state: str = PROVIDER_RUNTIME_CONFIG_STATE_DEFAULT,
    config_valid: bool = True,
    fail_closed: bool = True,
) -> dict[str, object]:
    category_labels = {
        PROVIDER_RUNTIME_CATEGORY_NO_PROVIDER: "Runtime state: no provider",
        PROVIDER_RUNTIME_CATEGORY_SETUP_DISABLED: "Runtime state: provider setup disabled",
        PROVIDER_RUNTIME_CATEGORY_UNCONFIGURED: "Runtime state: provider unconfigured",
        PROVIDER_RUNTIME_CATEGORY_UNAVAILABLE: "Runtime state: provider unavailable",
        PROVIDER_RUNTIME_CATEGORY_CONSENT_MISSING: "Runtime state: consent required",
        PROVIDER_RUNTIME_CATEGORY_CAPABILITY_MISSING: "Runtime state: capability missing",
        PROVIDER_RUNTIME_CATEGORY_READY_FUTURE_GATED: "Runtime state: ready but future-gated",
        PROVIDER_RUNTIME_CATEGORY_ERROR_DEGRADED: "Runtime state: degraded and fail-closed",
    }
    reason_labels = {
        PROVIDER_RUNTIME_REASON_NO_PROVIDER_CONFIGURED: "Reason: no provider configured",
        PROVIDER_RUNTIME_REASON_SETUP_DISABLED_LOCAL_ONLY: "Reason: setup disabled in local-only seam",
        PROVIDER_RUNTIME_REASON_PROVIDER_UNCONFIGURED: "Reason: provider configuration missing",
        PROVIDER_RUNTIME_REASON_PROVIDER_UNAVAILABLE: "Reason: provider unavailable",
        PROVIDER_RUNTIME_REASON_CONSENT_REQUIRED: "Reason: consent required before provider use",
        PROVIDER_RUNTIME_REASON_CAPABILITY_MISSING: "Reason: capability proof missing",
        PROVIDER_RUNTIME_REASON_READY_FUTURE_GATED: "Reason: future USER approval required",
        PROVIDER_RUNTIME_REASON_INVALID_CONFIG_FAIL_CLOSED: "Reason: invalid config failed closed",
        PROVIDER_RUNTIME_REASON_MISSING_CONFIG_FAIL_CLOSED: "Reason: missing config failed closed",
    }
    config_labels = {
        PROVIDER_RUNTIME_CONFIG_STATE_DEFAULT: "Config: safe default local-only",
        PROVIDER_RUNTIME_CONFIG_STATE_MISSING: "Config: missing; safe fallback active",
        PROVIDER_RUNTIME_CONFIG_STATE_INVALID: "Config: invalid; safe fallback active",
        PROVIDER_RUNTIME_CONFIG_STATE_LOCAL: "Config: local-only",
    }
    provenance_labels = {
        PROVIDER_RUNTIME_PROVENANCE_DEFAULT_CONFIG: "Provenance: default config",
        PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG: "Provenance: local config",
        PROVIDER_RUNTIME_PROVENANCE_HARDWARE_SNAPSHOT: "Provenance: hardware snapshot",
        PROVIDER_RUNTIME_PROVENANCE_MANIFEST_STATE: "Provenance: manifest state",
        PROVIDER_RUNTIME_PROVENANCE_VALIDATOR_FIXTURE: "Provenance: validator fixture",
        PROVIDER_RUNTIME_PROVENANCE_FUTURE_RUNTIME_CHECK: "Provenance: future runtime check",
    }
    normalized_category = category if category in PROVIDER_RUNTIME_STATE_CATEGORIES else PROVIDER_RUNTIME_CATEGORY_ERROR_DEGRADED
    normalized_reason = reason_code if reason_code in PROVIDER_RUNTIME_REASON_CODES else PROVIDER_RUNTIME_REASON_INVALID_CONFIG_FAIL_CLOSED
    normalized_config = config_state if config_state in {
        PROVIDER_RUNTIME_CONFIG_STATE_DEFAULT,
        PROVIDER_RUNTIME_CONFIG_STATE_MISSING,
        PROVIDER_RUNTIME_CONFIG_STATE_INVALID,
        PROVIDER_RUNTIME_CONFIG_STATE_LOCAL,
    } else PROVIDER_RUNTIME_CONFIG_STATE_INVALID
    normalized_provenance = (
        provenance if provenance in PROVIDER_RUNTIME_PROVENANCE_SOURCES else PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG
    )
    return {
        "runtime_state_schema_version": PROVIDER_RUNTIME_STATE_SCHEMA_VERSION,
        "runtime_state_category": normalized_category,
        "runtime_state_label": category_labels[normalized_category],
        "runtime_reason_code": normalized_reason,
        "runtime_reason_label": reason_labels[normalized_reason],
        "runtime_config_schema_version": PROVIDER_RUNTIME_CONFIG_SCHEMA_VERSION,
        "runtime_config_state": normalized_config,
        "runtime_config_label": config_labels[normalized_config],
        "runtime_config_migration": PROVIDER_RUNTIME_CONFIG_MIGRATION_POSTURE,
        "runtime_config_valid": bool(config_valid),
        "runtime_fail_closed": bool(fail_closed),
        "runtime_provenance": normalized_provenance,
        "runtime_provenance_label": provenance_labels[normalized_provenance],
    }


def _default_readiness_action_permissions() -> tuple[AIReadinessActionPermissionSnapshot, ...]:
    return (
        AIReadinessActionPermissionSnapshot(
            action="view_provider_readiness_status",
            permission=READINESS_ACTION_ALLOWED_LOCAL_READ_ONLY,
            label="View provider readiness status: allowed",
        ),
        AIReadinessActionPermissionSnapshot(
            action="view_readiness_reason",
            permission=READINESS_ACTION_ALLOWED_LOCAL_READ_ONLY,
            label="View readiness reason: allowed",
        ),
        AIReadinessActionPermissionSnapshot(
            action="view_setup_blocker",
            permission=READINESS_ACTION_ALLOWED_LOCAL_READ_ONLY,
            label="View setup blocker: allowed",
        ),
        AIReadinessActionPermissionSnapshot(
            action="view_capability_pack_eligibility",
            permission=READINESS_ACTION_ALLOWED_LOCAL_READ_ONLY,
            label="View capability-pack eligibility: allowed",
        ),
        AIReadinessActionPermissionSnapshot(
            action="view_install_intent_posture",
            permission=READINESS_ACTION_ALLOWED_LOCAL_READ_ONLY,
            label="View install-intent posture: allowed",
        ),
        AIReadinessActionPermissionSnapshot(
            action="view_consent_requirement_posture",
            permission=READINESS_ACTION_ALLOWED_LOCAL_READ_ONLY,
            label="View consent requirement posture: allowed",
        ),
        AIReadinessActionPermissionSnapshot(
            action="future_consent_collection",
            permission=READINESS_ACTION_FUTURE_USER_APPROVAL_REQUIRED,
            label="Future consent collection: USER approval required",
        ),
        AIReadinessActionPermissionSnapshot(
            action="future_provider_setup",
            permission=READINESS_ACTION_FUTURE_USER_APPROVAL_REQUIRED,
            label="Future provider setup: USER approval required",
        ),
        AIReadinessActionPermissionSnapshot(
            action="future_provider_execution",
            permission=READINESS_ACTION_FUTURE_USER_APPROVAL_REQUIRED,
            label="Future provider execution: USER approval required",
        ),
    )


def _readiness_contract_fields(
    *,
    state: str,
    reason_code: str,
    setup_eligibility: str,
    setup_blocker: str,
    provenance: str = PROVIDER_READINESS_PROVENANCE_DEFAULT_CONFIG,
    config_state: str = PROVIDER_READINESS_CONFIG_STATE_DEFAULT,
    config_valid: bool = True,
    future_gate_status: str = PROVIDER_FUTURE_GATE_STATUS_SETUP_REQUIRED,
    capability_pack_eligibility: str = CAPABILITY_PACK_ELIGIBILITY_BLOCKED,
    manifest_validity: str = CAPABILITY_PACK_MANIFEST_MISSING,
    source_trust: str = CAPABILITY_PACK_SOURCE_TRUST_UNVERIFIED,
    compatibility_posture: str = CAPABILITY_PACK_COMPATIBILITY_BLOCKED,
    requirement_posture: str = CAPABILITY_PACK_REQUIREMENT_UNPROBED,
    install_intent: str = CAPABILITY_PACK_INSTALL_INTENT_BLOCKED,
) -> dict[str, object]:
    state_labels = {
        PROVIDER_READINESS_STATE_UNKNOWN: "Provider readiness: unknown",
        PROVIDER_READINESS_STATE_SETUP_DISABLED: "Provider readiness: setup disabled",
        PROVIDER_READINESS_STATE_SETUP_AVAILABLE_FUTURE_GATED: "Provider readiness: setup available after future approval",
        PROVIDER_READINESS_STATE_SETUP_INELIGIBLE: "Provider readiness: setup ineligible",
        PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CONSENT: "Provider readiness: blocked by consent",
        PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CAPABILITY: "Provider readiness: blocked by capability proof",
        PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_MANIFEST: "Provider readiness: blocked by capability manifest",
        PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_POLICY: "Provider readiness: blocked by policy",
        PROVIDER_READINESS_STATE_SETUP_CONFIG_REQUIRED: "Provider readiness: setup config required",
        PROVIDER_READINESS_STATE_PROVIDER_READY_EXECUTION_GATED: "Provider readiness: ready but execution gated",
        PROVIDER_READINESS_STATE_DEGRADED: "Provider readiness: degraded and fail-closed",
    }
    eligibility_labels = {
        PROVIDER_SETUP_ELIGIBILITY_DISABLED: "Setup eligibility: disabled",
        PROVIDER_SETUP_ELIGIBILITY_FUTURE_GATED: "Setup eligibility: future-gated",
        PROVIDER_SETUP_ELIGIBILITY_INELIGIBLE: "Setup eligibility: ineligible",
        PROVIDER_SETUP_ELIGIBILITY_BLOCKED: "Setup eligibility: blocked",
        PROVIDER_SETUP_ELIGIBILITY_CONFIG_REQUIRED: "Setup eligibility: config required",
        PROVIDER_SETUP_ELIGIBILITY_EXECUTION_GATED: "Setup eligibility: execution gated",
    }
    blocker_labels = {
        PROVIDER_SETUP_BLOCKER_NONE: "Setup blocker: none before execution gate",
        PROVIDER_SETUP_BLOCKER_SETUP_DISABLED: "Setup blocker: setup disabled",
        PROVIDER_SETUP_BLOCKER_CONSENT_REQUIRED: "Setup blocker: consent required",
        PROVIDER_SETUP_BLOCKER_CAPABILITY_REQUIRED: "Setup blocker: capability proof required",
        PROVIDER_SETUP_BLOCKER_MANIFEST_REQUIRED: "Setup blocker: capability manifest required",
        PROVIDER_SETUP_BLOCKER_POLICY_BLOCKED: "Setup blocker: policy blocked",
        PROVIDER_SETUP_BLOCKER_CONFIG_REQUIRED: "Setup blocker: provider config required",
        PROVIDER_SETUP_BLOCKER_CONFIG_INVALID: "Setup blocker: invalid config",
        PROVIDER_SETUP_BLOCKER_FUTURE_GATE: "Setup blocker: future USER approval required",
        PROVIDER_SETUP_BLOCKER_PROVIDER_NOT_READY: "Setup blocker: provider not ready",
    }
    reason_labels = {
        PROVIDER_READINESS_REASON_DEFAULT_LOCAL_ONLY: "Readiness reason: local-only default",
        PROVIDER_READINESS_REASON_CONFIG_MISSING_FAIL_CLOSED: "Readiness reason: missing config failed closed",
        PROVIDER_READINESS_REASON_CONFIG_INVALID_FAIL_CLOSED: "Readiness reason: invalid config failed closed",
        PROVIDER_READINESS_REASON_PROVIDER_UNCONFIGURED: "Readiness reason: provider unconfigured",
        PROVIDER_READINESS_REASON_CONSENT_MISSING: "Readiness reason: consent missing",
        PROVIDER_READINESS_REASON_CAPABILITY_MISSING: "Readiness reason: capability proof missing",
        PROVIDER_READINESS_REASON_MANIFEST_MISSING: "Readiness reason: capability manifest missing",
        PROVIDER_READINESS_REASON_MANIFEST_INVALID_INSTALL_BLOCKED: "Readiness reason: manifest invalid; install blocked",
        PROVIDER_READINESS_REASON_POLICY_BLOCKED: "Readiness reason: policy blocked",
        PROVIDER_READINESS_REASON_FUTURE_PROVIDER_GATED: "Readiness reason: provider setup future-gated",
        PROVIDER_READINESS_REASON_PROVIDER_NOT_READY: "Readiness reason: provider not ready",
        PROVIDER_READINESS_REASON_PROVIDER_READY_EXECUTION_GATED: "Readiness reason: provider execution future-gated",
    }
    provenance_labels = {
        PROVIDER_READINESS_PROVENANCE_DEFAULT_CONFIG: "Readiness provenance: default config",
        PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG: "Readiness provenance: local config",
        PROVIDER_READINESS_PROVENANCE_RELEASE_SOURCE_TRUTH: "Readiness provenance: release source truth",
        PROVIDER_READINESS_PROVENANCE_HARDWARE_SNAPSHOT: "Readiness provenance: hardware snapshot",
        PROVIDER_READINESS_PROVENANCE_CAPABILITY_MANIFEST: "Readiness provenance: capability manifest",
        PROVIDER_READINESS_PROVENANCE_CONSENT_STATE: "Readiness provenance: consent state",
        PROVIDER_READINESS_PROVENANCE_VALIDATOR_FIXTURE: "Readiness provenance: validator fixture",
        PROVIDER_READINESS_PROVENANCE_FUTURE_RUNTIME_CHECK: "Readiness provenance: future runtime check",
    }
    config_labels = {
        PROVIDER_READINESS_CONFIG_STATE_DEFAULT: "Readiness config: safe default local-only",
        PROVIDER_READINESS_CONFIG_STATE_MISSING: "Readiness config: missing; setup disabled",
        PROVIDER_READINESS_CONFIG_STATE_INVALID: "Readiness config: invalid; degraded fail-closed",
        PROVIDER_READINESS_CONFIG_STATE_LOCAL: "Readiness config: local-only",
    }
    future_gate_labels = {
        PROVIDER_FUTURE_GATE_STATUS_SETUP_REQUIRED: "Future provider gate: USER approval required before setup",
        PROVIDER_FUTURE_GATE_STATUS_EXECUTION_REQUIRED: "Future provider gate: USER approval required before execution",
    }
    eligibility_copy = {
        CAPABILITY_PACK_ELIGIBILITY_UNKNOWN: "Capability-pack eligibility: unknown",
        CAPABILITY_PACK_ELIGIBILITY_BLOCKED: "Capability-pack eligibility: blocked",
        CAPABILITY_PACK_ELIGIBILITY_FUTURE_GATED: "Capability-pack eligibility: future-gated",
        CAPABILITY_PACK_ELIGIBILITY_INELIGIBLE: "Capability-pack eligibility: ineligible",
    }
    manifest_copy = {
        CAPABILITY_PACK_MANIFEST_MISSING: "Capability manifest: missing",
        CAPABILITY_PACK_MANIFEST_INVALID: "Capability manifest: invalid",
        CAPABILITY_PACK_MANIFEST_VALID_FUTURE_GATED: "Capability manifest: valid but future-gated",
        CAPABILITY_PACK_MANIFEST_PLANNED: "Capability manifest: planned",
    }
    source_copy = {
        CAPABILITY_PACK_SOURCE_TRUST_UNVERIFIED: "Capability-pack source trust: unverified",
        CAPABILITY_PACK_SOURCE_TRUST_LOCAL_ONLY: "Capability-pack source trust: local-only",
        CAPABILITY_PACK_SOURCE_TRUST_FUTURE_GATED: "Capability-pack source trust: future-gated",
    }
    compatibility_copy = {
        CAPABILITY_PACK_COMPATIBILITY_UNPROVEN: "Capability-pack compatibility: unproven",
        CAPABILITY_PACK_COMPATIBILITY_BLOCKED: "Capability-pack compatibility: blocked",
        CAPABILITY_PACK_COMPATIBILITY_FUTURE_GATED: "Capability-pack compatibility: future-gated",
    }
    install_copy = {
        CAPABILITY_PACK_INSTALL_INTENT_NONE: "Install intent: none",
        CAPABILITY_PACK_INSTALL_INTENT_BLOCKED: "Install intent: blocked",
        CAPABILITY_PACK_INSTALL_INTENT_FUTURE_GATED: "Install intent: future-gated",
    }
    normalized_state = state if state in PROVIDER_READINESS_STATES else PROVIDER_READINESS_STATE_DEGRADED
    normalized_reason = (
        reason_code
        if reason_code in PROVIDER_READINESS_REASON_CODES
        else PROVIDER_READINESS_REASON_CONFIG_INVALID_FAIL_CLOSED
    )
    normalized_provenance = (
        provenance if provenance in PROVIDER_READINESS_PROVENANCE_SOURCES else PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG
    )
    normalized_config = (
        config_state
        if config_state
        in {
            PROVIDER_READINESS_CONFIG_STATE_DEFAULT,
            PROVIDER_READINESS_CONFIG_STATE_MISSING,
            PROVIDER_READINESS_CONFIG_STATE_INVALID,
            PROVIDER_READINESS_CONFIG_STATE_LOCAL,
        }
        else PROVIDER_READINESS_CONFIG_STATE_INVALID
    )
    return {
        "provider_readiness_state": normalized_state,
        "provider_readiness_label": state_labels[normalized_state],
        "setup_eligibility_state": setup_eligibility,
        "setup_eligibility_label": eligibility_labels.get(setup_eligibility, "Setup eligibility: blocked"),
        "setup_blocker_state": setup_blocker,
        "setup_blocker_label": blocker_labels.get(setup_blocker, "Setup blocker: policy blocked"),
        "readiness_reason_code": normalized_reason,
        "readiness_reason_label": reason_labels[normalized_reason],
        "readiness_provenance": normalized_provenance,
        "readiness_provenance_label": provenance_labels[normalized_provenance],
        "readiness_state_schema_version": PROVIDER_READINESS_STATE_SCHEMA_VERSION,
        "readiness_config_schema_version": PROVIDER_READINESS_CONFIG_SCHEMA_VERSION,
        "readiness_config_state": normalized_config,
        "readiness_config_label": config_labels[normalized_config],
        "readiness_config_migration": PROVIDER_READINESS_CONFIG_MIGRATION_POSTURE,
        "readiness_config_valid": bool(config_valid),
        "future_provider_gate_status": future_gate_status,
        "future_provider_gate_label": future_gate_labels.get(
            future_gate_status,
            "Future provider gate: USER approval required before setup",
        ),
        "capability_pack_eligibility_state": capability_pack_eligibility,
        "capability_pack_eligibility_label": eligibility_copy.get(
            capability_pack_eligibility,
            "Capability-pack eligibility: blocked",
        ),
        "capability_pack_manifest_validity_state": manifest_validity,
        "capability_pack_manifest_validity_label": manifest_copy.get(
            manifest_validity,
            "Capability manifest: missing",
        ),
        "capability_pack_source_trust_state": source_trust,
        "capability_pack_source_trust_label": source_copy.get(source_trust, "Capability-pack source trust: unverified"),
        "capability_pack_compatibility_posture_state": compatibility_posture,
        "capability_pack_compatibility_posture_label": compatibility_copy.get(
            compatibility_posture,
            "Capability-pack compatibility: blocked",
        ),
        "capability_pack_cpu_requirement_posture": requirement_posture,
        "capability_pack_gpu_requirement_posture": requirement_posture,
        "capability_pack_ram_requirement_posture": requirement_posture,
        "capability_pack_disk_requirement_posture": requirement_posture,
        "install_intent_state": install_intent,
        "install_intent_label": install_copy.get(install_intent, "Install intent: blocked"),
        "capability_pack_download_blocked_reason": CAPABILITY_PACK_DOWNLOAD_BLOCKED_REASON,
        "capability_pack_install_blocked_reason": CAPABILITY_PACK_INSTALL_BLOCKED_REASON,
        "capability_pack_update_blocked_reason": CAPABILITY_PACK_UPDATE_BLOCKED_REASON,
        "capability_pack_uninstall_blocked_reason": CAPABILITY_PACK_UNINSTALL_BLOCKED_REASON,
        "action_permission_matrix": _default_readiness_action_permissions(),
    }


def _activation_contract_fields(
    *,
    state: str,
    reason_code: str,
    eligibility: str,
    blocker: str,
    provenance: str = PROVIDER_ACTIVATION_PROVENANCE_DEFAULT_CONFIG,
    config_state: str = PROVIDER_ACTIVATION_CONFIG_STATE_DEFAULT,
    config_valid: bool = True,
    future_gate_status: str = PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_REQUIRED,
    adapter_available: bool = False,
    readiness_gate: str = READINESS_GATE_BLOCKED,
    consent_gate: str = CONSENT_GATE_REQUIRED,
    capability_gate: str = CAPABILITY_GATE_BLOCKED,
    manifest_gate: str = MANIFEST_GATE_BLOCKED,
    safety_eval_gate: str = SAFETY_EVAL_GATE_PENDING,
    functional_ai_criteria: str = FUNCTIONAL_AI_CRITERIA_PENDING,
    v18_readiness: str = V18_PREBETA_READINESS_PENDING,
) -> dict[str, object]:
    state_labels = {
        PROVIDER_ACTIVATION_STATE_UNKNOWN: "Provider activation: unknown",
        PROVIDER_ACTIVATION_STATE_UNAVAILABLE: "Provider activation: unavailable",
        PROVIDER_ACTIVATION_STATE_DISABLED: "Provider activation: disabled",
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_READINESS: "Provider activation: blocked by readiness",
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CONSENT: "Provider activation: blocked by consent",
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CAPABILITY: "Provider activation: blocked by capability proof",
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_POLICY: "Provider activation: blocked by policy",
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_MANIFEST: "Provider activation: blocked by capability manifest",
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_ADAPTER: "Provider activation: blocked by adapter boundary",
        PROVIDER_ACTIVATION_STATE_ELIGIBLE_FUTURE_GATED: "Provider activation: eligible after future approval",
        PROVIDER_ACTIVATION_STATE_READY_EXECUTION_GATED: "Provider activation: ready but execution gated",
        PROVIDER_ACTIVATION_STATE_DEGRADED: "Provider activation: degraded and fail-closed",
        PROVIDER_ACTIVATION_STATE_FUNCTIONAL_AI_READY_FUTURE_VERSION:
            "Provider activation: functional AI ready for future version",
    }
    eligibility_labels = {
        PROVIDER_ACTIVATION_ELIGIBILITY_UNAVAILABLE: "Activation eligibility: unavailable",
        PROVIDER_ACTIVATION_ELIGIBILITY_DISABLED: "Activation eligibility: disabled",
        PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED: "Activation eligibility: blocked",
        PROVIDER_ACTIVATION_ELIGIBILITY_FUTURE_GATED: "Activation eligibility: future-gated",
        PROVIDER_ACTIVATION_ELIGIBILITY_EXECUTION_GATED: "Activation eligibility: execution gated",
        PROVIDER_ACTIVATION_ELIGIBILITY_FUTURE_VERSION: "Activation eligibility: future version",
    }
    blocker_labels = {
        PROVIDER_ACTIVATION_BLOCKER_NONE: "Activation blocker: none before execution gate",
        PROVIDER_ACTIVATION_BLOCKER_READINESS_REQUIRED: "Activation blocker: readiness required",
        PROVIDER_ACTIVATION_BLOCKER_CONSENT_REQUIRED: "Activation blocker: consent required",
        PROVIDER_ACTIVATION_BLOCKER_CAPABILITY_REQUIRED: "Activation blocker: capability proof required",
        PROVIDER_ACTIVATION_BLOCKER_POLICY_BLOCKED: "Activation blocker: policy blocked",
        PROVIDER_ACTIVATION_BLOCKER_MANIFEST_REQUIRED: "Activation blocker: capability manifest required",
        PROVIDER_ACTIVATION_BLOCKER_ADAPTER_UNAVAILABLE: "Activation blocker: null adapter boundary",
        PROVIDER_ACTIVATION_BLOCKER_EXECUTION_GATE: "Activation blocker: execution gate",
        PROVIDER_ACTIVATION_BLOCKER_FUTURE_ACTIVATION_GATE: "Activation blocker: future USER approval required",
        PROVIDER_ACTIVATION_BLOCKER_CONFIG_INVALID: "Activation blocker: invalid config",
        PROVIDER_ACTIVATION_BLOCKER_VERSION_JUMP_REQUIRED: "Activation blocker: v1.8.0-prebeta version jump required",
    }
    reason_labels = {
        PROVIDER_ACTIVATION_REASON_DEFAULT_UNAVAILABLE: "Activation reason: activation foundation only",
        PROVIDER_ACTIVATION_REASON_CONFIG_MISSING_FAIL_CLOSED: "Activation reason: missing config failed closed",
        PROVIDER_ACTIVATION_REASON_CONFIG_INVALID_FAIL_CLOSED: "Activation reason: invalid config failed closed",
        PROVIDER_ACTIVATION_REASON_READINESS_BLOCKED: "Activation reason: readiness not satisfied",
        PROVIDER_ACTIVATION_REASON_CONSENT_REQUIRED: "Activation reason: consent required",
        PROVIDER_ACTIVATION_REASON_CAPABILITY_REQUIRED: "Activation reason: capability proof required",
        PROVIDER_ACTIVATION_REASON_POLICY_BLOCKED: "Activation reason: policy blocked",
        PROVIDER_ACTIVATION_REASON_MANIFEST_REQUIRED: "Activation reason: capability manifest required",
        PROVIDER_ACTIVATION_REASON_ADAPTER_UNAVAILABLE: "Activation reason: adapter unavailable",
        PROVIDER_ACTIVATION_REASON_FUTURE_GATED: "Activation reason: future activation approval required",
        PROVIDER_ACTIVATION_REASON_EXECUTION_GATED: "Activation reason: execution approval required",
        PROVIDER_ACTIVATION_REASON_FUNCTIONAL_AI_FUTURE_VERSION:
            "Activation reason: functional AI proof reserved for v1.8.0-prebeta",
    }
    provenance_labels = {
        PROVIDER_ACTIVATION_PROVENANCE_DEFAULT_CONFIG: "Activation provenance: default config",
        PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG: "Activation provenance: local config",
        PROVIDER_ACTIVATION_PROVENANCE_READINESS_STATE: "Activation provenance: readiness state",
        PROVIDER_ACTIVATION_PROVENANCE_CAPABILITY_MANIFEST: "Activation provenance: capability manifest",
        PROVIDER_ACTIVATION_PROVENANCE_CONSENT_STATE: "Activation provenance: consent state",
        PROVIDER_ACTIVATION_PROVENANCE_ADAPTER_CONTRACT: "Activation provenance: adapter contract",
        PROVIDER_ACTIVATION_PROVENANCE_VALIDATOR_FIXTURE: "Activation provenance: validator fixture",
        PROVIDER_ACTIVATION_PROVENANCE_FUTURE_RUNTIME_CHECK: "Activation provenance: future runtime check",
        PROVIDER_ACTIVATION_PROVENANCE_RELEASE_SOURCE_TRUTH: "Activation provenance: release source truth",
    }
    config_labels = {
        PROVIDER_ACTIVATION_CONFIG_STATE_DEFAULT: "Activation config: safe default local-only",
        PROVIDER_ACTIVATION_CONFIG_STATE_MISSING: "Activation config: missing; activation disabled",
        PROVIDER_ACTIVATION_CONFIG_STATE_INVALID: "Activation config: invalid; degraded fail-closed",
        PROVIDER_ACTIVATION_CONFIG_STATE_LOCAL: "Activation config: local-only",
    }
    future_gate_labels = {
        PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_REQUIRED:
            "Future activation gate: USER approval required before activation",
        PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_EXECUTION_REQUIRED:
            "Future activation gate: USER approval required before provider execution",
        PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_VERSION_JUMP_REQUIRED:
            "Future activation gate: v1.8.0-prebeta requires functional AI proof",
    }
    normalized_state = state if state in PROVIDER_ACTIVATION_STATES else PROVIDER_ACTIVATION_STATE_DEGRADED
    normalized_reason = (
        reason_code
        if reason_code in PROVIDER_ACTIVATION_REASON_CODES
        else PROVIDER_ACTIVATION_REASON_CONFIG_INVALID_FAIL_CLOSED
    )
    normalized_provenance = (
        provenance
        if provenance in PROVIDER_ACTIVATION_PROVENANCE_SOURCES
        else PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG
    )
    normalized_config = (
        config_state
        if config_state
        in {
            PROVIDER_ACTIVATION_CONFIG_STATE_DEFAULT,
            PROVIDER_ACTIVATION_CONFIG_STATE_MISSING,
            PROVIDER_ACTIVATION_CONFIG_STATE_INVALID,
            PROVIDER_ACTIVATION_CONFIG_STATE_LOCAL,
        }
        else PROVIDER_ACTIVATION_CONFIG_STATE_INVALID
    )
    adapter_availability = (
        PROVIDER_ADAPTER_AVAILABILITY_READY_FUTURE_GATED
        if adapter_available
        else PROVIDER_ADAPTER_AVAILABILITY_UNAVAILABLE
    )
    adapter_gate = ADAPTER_GATE_READY_FUTURE_GATED if adapter_available else ADAPTER_GATE_NULL_LOCAL
    functional_ai_label = (
        "Functional AI: criteria ready for v1.8.0-prebeta"
        if functional_ai_criteria == FUNCTIONAL_AI_CRITERIA_READY_FUTURE_VERSION
        else "Functional AI: criteria pending for v1.8.0-prebeta"
    )
    v18_label = (
        "v1.8.0-prebeta readiness: functional AI proof ready"
        if v18_readiness == V18_PREBETA_READINESS_READY
        else "v1.8.0-prebeta readiness: pending functional AI proof"
    )
    return {
        "provider_activation_state": normalized_state,
        "provider_activation_label": state_labels[normalized_state],
        "activation_eligibility_state": eligibility,
        "activation_eligibility_label": eligibility_labels.get(eligibility, "Activation eligibility: blocked"),
        "activation_blocker_state": blocker,
        "activation_blocker_label": blocker_labels.get(blocker, "Activation blocker: policy blocked"),
        "activation_reason_code": normalized_reason,
        "activation_reason_label": reason_labels[normalized_reason],
        "activation_provenance": normalized_provenance,
        "activation_provenance_label": provenance_labels[normalized_provenance],
        "activation_state_schema_version": PROVIDER_ACTIVATION_STATE_SCHEMA_VERSION,
        "activation_config_schema_version": PROVIDER_ACTIVATION_CONFIG_SCHEMA_VERSION,
        "activation_config_state": normalized_config,
        "activation_config_label": config_labels[normalized_config],
        "activation_config_migration": PROVIDER_ACTIVATION_CONFIG_MIGRATION_POSTURE,
        "activation_config_valid": bool(config_valid),
        "future_activation_gate_status": future_gate_status,
        "future_activation_gate_label": future_gate_labels.get(
            future_gate_status,
            "Future activation gate: USER approval required before activation",
        ),
        "provider_adapter_posture": PROVIDER_ADAPTER_POSTURE_NULL_LOCAL,
        "provider_adapter_label": "Provider adapter: null local adapter",
        "provider_adapter_kind": PROVIDER_ADAPTER_KIND_NULL,
        "provider_adapter_availability_state": adapter_availability,
        "provider_adapter_availability_label": (
            "Adapter availability: ready for future handoff" if adapter_available else "Adapter availability: unavailable"
        ),
        "provider_adapter_execution_posture": PROVIDER_ADAPTER_EXECUTION_POSTURE_DISABLED,
        "provider_adapter_execution_label": "Adapter execution: disabled",
        "provider_metadata_contract_version": PROVIDER_METADATA_CONTRACT_VERSION,
        "provider_config_envelope_version": PROVIDER_CONFIG_ENVELOPE_VERSION,
        "provider_activation_handoff_state": PROVIDER_ACTIVATION_HANDOFF_STATE_FUTURE_GATED,
        "provider_activation_handoff_label": "Provider activation handoff: future-gated",
        "future_sdk_integration_boundary": PROVIDER_SDK_INTEGRATION_BOUNDARY_FUTURE_APPROVAL,
        "prompt_execution_gate_state": PROMPT_EXECUTION_GATE_DISABLED,
        "prompt_execution_gate_label": "Prompt execution gate: disabled",
        "model_execution_gate_state": MODEL_EXECUTION_GATE_DISABLED,
        "model_execution_gate_label": "Model execution gate: disabled",
        "provider_execution_gate_state": PROVIDER_EXECUTION_GATE_DISABLED,
        "provider_execution_gate_label": "Provider execution gate: disabled",
        "readiness_gate_state": readiness_gate,
        "consent_gate_state": consent_gate,
        "capability_gate_state": capability_gate,
        "manifest_gate_state": manifest_gate,
        "adapter_gate_state": adapter_gate,
        "safety_eval_gate_state": safety_eval_gate,
        "network_egress_gate_state": NETWORK_EGRESS_BLOCKED,
        "memory_indexing_gate_state": MEMORY_INDEXING_DISABLED,
        "voice_core_sync_gate_state": VOICE_CORE_SYNC_GATE_PENDING_APPROVAL,
        "version_jump_gate_state": VERSION_JUMP_GATE_PENDING_FUNCTIONAL_AI,
        "functional_ai_criteria_state": functional_ai_criteria,
        "functional_ai_criteria_label": functional_ai_label,
        "v18_prebeta_readiness_state": v18_readiness,
        "v18_prebeta_readiness_label": v18_label,
    }


def _execution_readiness_contract_fields(
    *,
    state: str,
    reason_code: str,
    eligibility: str,
    blocker: str,
    provenance: str = PROVIDER_EXECUTION_PROVENANCE_DEFAULT_CONFIG,
    config_state: str = PROVIDER_EXECUTION_CONFIG_STATE_DEFAULT,
    config_valid: bool = True,
    approval_status: str = PROVIDER_EXECUTION_APPROVAL_STATUS_MISSING,
    provider_path_selected: bool = False,
    provider_adapter_selected: bool = False,
    prompt_acceptance_ready: bool = False,
    prompt_routing_ready: bool = False,
    model_execution_ready: bool = False,
    provider_visible_data_ready: bool = False,
    network_external_ready: bool = False,
    safety_ready: bool = False,
    functional_ai_release_ready: bool = False,
) -> dict[str, object]:
    state_labels = {
        PROVIDER_EXECUTION_READINESS_STATE_UNKNOWN: "Execution readiness: unknown",
        PROVIDER_EXECUTION_READINESS_STATE_UNAVAILABLE: "Execution readiness: unavailable",
        PROVIDER_EXECUTION_READINESS_STATE_DISABLED: "Execution readiness: disabled",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ACTIVATION:
            "Execution readiness: blocked by activation",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROVIDER_PATH:
            "Execution readiness: blocked by provider path",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ADAPTER:
            "Execution readiness: blocked by adapter",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROMPT_GATE:
            "Execution readiness: blocked by prompt gate",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_MODEL_GATE:
            "Execution readiness: blocked by model gate",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_CONSENT:
            "Execution readiness: blocked by consent",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_SAFETY:
            "Execution readiness: blocked by safety/eval",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_NETWORK:
            "Execution readiness: blocked by network approval",
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_POLICY:
            "Execution readiness: blocked by policy",
        PROVIDER_EXECUTION_READINESS_STATE_READY_FUTURE_GATED:
            "Execution readiness: ready but future-gated",
        PROVIDER_EXECUTION_READINESS_STATE_READY_BUT_NOT_APPROVED:
            "Execution readiness: ready but not approved",
        PROVIDER_EXECUTION_READINESS_STATE_DEGRADED:
            "Execution readiness: degraded and fail-closed",
        PROVIDER_EXECUTION_READINESS_STATE_FUNCTIONAL_AI_READY_FUTURE_VERSION:
            "Execution readiness: functional AI proof reserved for future version",
    }
    eligibility_labels = {
        PROVIDER_EXECUTION_ELIGIBILITY_UNAVAILABLE: "Execution eligibility: unavailable",
        PROVIDER_EXECUTION_ELIGIBILITY_DISABLED: "Execution eligibility: disabled",
        PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED: "Execution eligibility: blocked",
        PROVIDER_EXECUTION_ELIGIBILITY_FUTURE_GATED: "Execution eligibility: future-gated",
        PROVIDER_EXECUTION_ELIGIBILITY_READY_NOT_APPROVED:
            "Execution eligibility: ready but USER approval missing",
        PROVIDER_EXECUTION_ELIGIBILITY_FUTURE_VERSION: "Execution eligibility: future version",
    }
    blocker_labels = {
        PROVIDER_EXECUTION_BLOCKER_NONE: "Execution blocker: none before release gate",
        PROVIDER_EXECUTION_BLOCKER_ACTIVATION_REQUIRED: "Execution blocker: activation required",
        PROVIDER_EXECUTION_BLOCKER_PROVIDER_PATH_REQUIRED: "Execution blocker: provider path required",
        PROVIDER_EXECUTION_BLOCKER_ADAPTER_REQUIRED: "Execution blocker: adapter selection required",
        PROVIDER_EXECUTION_BLOCKER_PROMPT_GATE: "Execution blocker: prompt gate",
        PROVIDER_EXECUTION_BLOCKER_MODEL_GATE: "Execution blocker: model gate",
        PROVIDER_EXECUTION_BLOCKER_CONSENT_REQUIRED: "Execution blocker: consent required",
        PROVIDER_EXECUTION_BLOCKER_SAFETY_EVAL_REQUIRED: "Execution blocker: safety/eval required",
        PROVIDER_EXECUTION_BLOCKER_NETWORK_APPROVAL_REQUIRED:
            "Execution blocker: network approval required",
        PROVIDER_EXECUTION_BLOCKER_POLICY_BLOCKED: "Execution blocker: policy blocked",
        PROVIDER_EXECUTION_BLOCKER_CONFIG_INVALID: "Execution blocker: invalid config",
        PROVIDER_EXECUTION_BLOCKER_FUTURE_EXECUTION_GATE:
            "Execution blocker: future execution approval required",
        PROVIDER_EXECUTION_BLOCKER_APPROVAL_REQUIRED:
            "Execution blocker: provider/model execution approval required",
        PROVIDER_EXECUTION_BLOCKER_VERSION_JUMP_REQUIRED:
            "Execution blocker: v1.8.0-prebeta version jump required",
    }
    reason_labels = {
        PROVIDER_EXECUTION_REASON_DEFAULT_UNAVAILABLE: "Execution reason: execution readiness gates only",
        PROVIDER_EXECUTION_REASON_CONFIG_MISSING_FAIL_CLOSED:
            "Execution reason: missing config failed closed",
        PROVIDER_EXECUTION_REASON_CONFIG_INVALID_FAIL_CLOSED:
            "Execution reason: invalid config failed closed",
        PROVIDER_EXECUTION_REASON_ACTIVATION_BLOCKED:
            "Execution reason: activation foundation not satisfied",
        PROVIDER_EXECUTION_REASON_PROVIDER_PATH_MISSING:
            "Execution reason: provider path not selected",
        PROVIDER_EXECUTION_REASON_ADAPTER_UNAVAILABLE: "Execution reason: adapter unavailable",
        PROVIDER_EXECUTION_REASON_PROMPT_GATE_BLOCKED: "Execution reason: prompt gate blocked",
        PROVIDER_EXECUTION_REASON_MODEL_GATE_BLOCKED: "Execution reason: model gate blocked",
        PROVIDER_EXECUTION_REASON_CONSENT_REQUIRED: "Execution reason: consent required",
        PROVIDER_EXECUTION_REASON_SAFETY_EVAL_REQUIRED: "Execution reason: safety/eval required",
        PROVIDER_EXECUTION_REASON_NETWORK_BLOCKED: "Execution reason: network approval blocked",
        PROVIDER_EXECUTION_REASON_POLICY_BLOCKED: "Execution reason: policy blocked",
        PROVIDER_EXECUTION_REASON_FUTURE_GATED: "Execution reason: future execution approval required",
        PROVIDER_EXECUTION_REASON_APPROVAL_MISSING: "Execution reason: USER execution approval missing",
        PROVIDER_EXECUTION_REASON_FUNCTIONAL_AI_FUTURE_VERSION:
            "Execution reason: functional AI proof reserved for v1.8.0-prebeta",
    }
    provenance_labels = {
        PROVIDER_EXECUTION_PROVENANCE_DEFAULT_CONFIG: "Execution provenance: default config",
        PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG: "Execution provenance: local config",
        PROVIDER_EXECUTION_PROVENANCE_ACTIVATION_STATE: "Execution provenance: activation state",
        PROVIDER_EXECUTION_PROVENANCE_PROVIDER_PATH_CONTRACT:
            "Execution provenance: provider path contract",
        PROVIDER_EXECUTION_PROVENANCE_ADAPTER_CONTRACT: "Execution provenance: adapter contract",
        PROVIDER_EXECUTION_PROVENANCE_PROMPT_GATE: "Execution provenance: prompt gate",
        PROVIDER_EXECUTION_PROVENANCE_MODEL_GATE: "Execution provenance: model gate",
        PROVIDER_EXECUTION_PROVENANCE_CONSENT_STATE: "Execution provenance: consent state",
        PROVIDER_EXECUTION_PROVENANCE_SAFETY_EVAL: "Execution provenance: safety/eval",
        PROVIDER_EXECUTION_PROVENANCE_NETWORK_POLICY: "Execution provenance: network policy",
        PROVIDER_EXECUTION_PROVENANCE_VALIDATOR_FIXTURE: "Execution provenance: validator fixture",
        PROVIDER_EXECUTION_PROVENANCE_FUTURE_RUNTIME_CHECK:
            "Execution provenance: future runtime check",
        PROVIDER_EXECUTION_PROVENANCE_RELEASE_SOURCE_TRUTH:
            "Execution provenance: release source truth",
    }
    config_labels = {
        PROVIDER_EXECUTION_CONFIG_STATE_DEFAULT: "Execution config: safe default local-only",
        PROVIDER_EXECUTION_CONFIG_STATE_MISSING: "Execution config: missing; execution disabled",
        PROVIDER_EXECUTION_CONFIG_STATE_INVALID: "Execution config: invalid; degraded fail-closed",
        PROVIDER_EXECUTION_CONFIG_STATE_LOCAL: "Execution config: local-only",
    }
    approval_labels = {
        PROVIDER_EXECUTION_APPROVAL_STATUS_MISSING: "Execution approval: USER approval missing",
        PROVIDER_EXECUTION_APPROVAL_STATUS_FUTURE_GATED: "Execution approval: future-gated",
        PROVIDER_EXECUTION_APPROVAL_STATUS_GRANTED_FOR_PROOF:
            "Execution approval: granted for proof only",
    }
    normalized_state = (
        state if state in PROVIDER_EXECUTION_READINESS_STATES else PROVIDER_EXECUTION_READINESS_STATE_DEGRADED
    )
    normalized_reason = (
        reason_code
        if reason_code in PROVIDER_EXECUTION_REASON_CODES
        else PROVIDER_EXECUTION_REASON_CONFIG_INVALID_FAIL_CLOSED
    )
    normalized_provenance = (
        provenance
        if provenance in PROVIDER_EXECUTION_PROVENANCE_SOURCES
        else PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG
    )
    normalized_config = (
        config_state
        if config_state
        in {
            PROVIDER_EXECUTION_CONFIG_STATE_DEFAULT,
            PROVIDER_EXECUTION_CONFIG_STATE_MISSING,
            PROVIDER_EXECUTION_CONFIG_STATE_INVALID,
            PROVIDER_EXECUTION_CONFIG_STATE_LOCAL,
        }
        else PROVIDER_EXECUTION_CONFIG_STATE_INVALID
    )
    normalized_approval = (
        approval_status
        if approval_status
        in {
            PROVIDER_EXECUTION_APPROVAL_STATUS_MISSING,
            PROVIDER_EXECUTION_APPROVAL_STATUS_FUTURE_GATED,
            PROVIDER_EXECUTION_APPROVAL_STATUS_GRANTED_FOR_PROOF,
        }
        else PROVIDER_EXECUTION_APPROVAL_STATUS_MISSING
    )
    prompt_ready = bool(prompt_acceptance_ready and prompt_routing_ready)
    model_ready = bool(model_execution_ready)
    prompt_readiness = (
        PROVIDER_EXECUTION_READINESS_STATE_READY_FUTURE_GATED
        if prompt_ready
        else PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROMPT_GATE
    )
    model_readiness = (
        PROVIDER_EXECUTION_READINESS_STATE_READY_FUTURE_GATED
        if model_ready
        else PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_MODEL_GATE
    )
    provider_path_status = (
        PROVIDER_PATH_STATUS_SELECTED_FUTURE_GATED if provider_path_selected else PROVIDER_PATH_STATUS_NOT_SELECTED
    )
    adapter_posture = (
        ADAPTER_SELECTION_POSTURE_READY_FUTURE_GATED
        if provider_adapter_selected
        else ADAPTER_SELECTION_POSTURE_NULL_LOCAL
    )
    prompt_acceptance = PROMPT_ACCEPTANCE_GATE_FUTURE_GATED if prompt_acceptance_ready else PROMPT_ACCEPTANCE_GATE_DISABLED
    prompt_routing = PROMPT_ROUTING_GATE_FUTURE_GATED if prompt_routing_ready else PROMPT_ROUTING_GATE_DISABLED
    model_execution = MODEL_EXECUTION_STATUS_FUTURE_GATED if model_ready else MODEL_EXECUTION_STATUS_DISABLED
    model_workload_readiness = (
        MODEL_WORKLOAD_READINESS_FUTURE_GATED if model_ready else MODEL_WORKLOAD_READINESS_DISABLED
    )
    visible_data_posture = (
        PROVIDER_VISIBLE_DATA_EXECUTION_FUTURE_GATED
        if provider_visible_data_ready
        else PROVIDER_VISIBLE_DATA_EXECUTION_NONE
    )
    external_call_readiness = (
        EXTERNAL_CALL_READINESS_FUTURE_GATED if network_external_ready else EXTERNAL_CALL_READINESS_BLOCKED
    )
    safety_readiness = SAFETY_EVAL_READINESS_READY if safety_ready else SAFETY_EVAL_READINESS_PENDING
    execution_proof = (
        EXECUTION_PROOF_MARKER_READY_FUTURE_GATED
        if functional_ai_release_ready
        else EXECUTION_PROOF_MARKER_PENDING
    )
    functional_release_gate = (
        FUNCTIONAL_AI_RELEASE_GATE_READY_FUTURE_VERSION
        if functional_ai_release_ready
        else FUNCTIONAL_AI_RELEASE_GATE_PENDING
    )
    v18_release_gate = (
        V18_RELEASE_GATE_READY_FUTURE_VERSION
        if functional_ai_release_ready
        else V18_RELEASE_GATE_PENDING_FUNCTIONAL_AI
    )
    return {
        "provider_execution_readiness_state": normalized_state,
        "provider_execution_readiness_label": state_labels[normalized_state],
        "prompt_execution_readiness_state": prompt_readiness,
        "prompt_execution_readiness_label": (
            "Prompt execution readiness: future-gated" if prompt_ready else "Prompt execution readiness: disabled"
        ),
        "model_execution_readiness_state": model_readiness,
        "model_execution_readiness_label": (
            "Model execution readiness: future-gated" if model_ready else "Model execution readiness: disabled"
        ),
        "execution_eligibility_state": eligibility,
        "execution_eligibility_label": eligibility_labels.get(eligibility, "Execution eligibility: blocked"),
        "execution_blocker_state": blocker,
        "execution_blocker_label": blocker_labels.get(blocker, "Execution blocker: policy blocked"),
        "execution_reason_code": normalized_reason,
        "execution_reason_label": reason_labels[normalized_reason],
        "execution_provenance": normalized_provenance,
        "execution_provenance_label": provenance_labels[normalized_provenance],
        "execution_state_schema_version": PROVIDER_EXECUTION_READINESS_STATE_SCHEMA_VERSION,
        "execution_config_schema_version": PROVIDER_EXECUTION_READINESS_CONFIG_SCHEMA_VERSION,
        "execution_config_state": normalized_config,
        "execution_config_label": config_labels[normalized_config],
        "execution_config_migration": PROVIDER_EXECUTION_READINESS_CONFIG_MIGRATION_POSTURE,
        "execution_config_valid": bool(config_valid),
        "execution_approval_status": normalized_approval,
        "execution_approval_label": approval_labels[normalized_approval],
        "provider_path_status": provider_path_status,
        "provider_path_label": (
            "Provider path: selected for future-gated proof"
            if provider_path_selected
            else "Provider path: not selected"
        ),
        "provider_selection_posture": (
            PROVIDER_SELECTION_POSTURE_SELECTED_FUTURE_GATED
            if provider_path_selected
            else PROVIDER_SELECTION_POSTURE_PENDING_APPROVAL
        ),
        "provider_selection_posture_label": (
            "Provider selection: selected for future proof"
            if provider_path_selected
            else "Provider selection: pending USER approval"
        ),
        "adapter_selection_posture": adapter_posture,
        "adapter_selection_posture_label": (
            "Adapter selection: ready for future handoff"
            if provider_adapter_selected
            else "Adapter selection: null local fallback"
        ),
        "prompt_acceptance_gate_state": prompt_acceptance,
        "prompt_acceptance_gate_label": (
            "Prompt acceptance gate: future-gated" if prompt_acceptance_ready else "Prompt acceptance gate: disabled"
        ),
        "prompt_routing_gate_state": prompt_routing,
        "prompt_routing_gate_label": (
            "Prompt routing gate: future-gated" if prompt_routing_ready else "Prompt routing gate: disabled"
        ),
        "prompt_send_posture": PROMPT_SEND_POSTURE_DISABLED,
        "prompt_send_label": "Prompt send: disabled",
        "model_execution_status": model_execution,
        "model_execution_status_label": (
            "Model execution status: future-gated" if model_ready else "Model execution status: disabled"
        ),
        "model_workload_readiness_posture": model_workload_readiness,
        "model_workload_readiness_label": (
            "Model workload readiness: future-gated"
            if model_ready
            else "Model workload readiness: disabled"
        ),
        "provider_visible_data_execution_posture": visible_data_posture,
        "provider_visible_data_execution_label": (
            "Provider-visible execution data: future-gated"
            if provider_visible_data_ready
            else "Provider-visible execution data: none"
        ),
        "external_call_readiness_state": external_call_readiness,
        "external_call_readiness_label": (
            "External call readiness: future-gated"
            if network_external_ready
            else "External call readiness: blocked"
        ),
        "safety_eval_readiness_state": safety_readiness,
        "safety_eval_readiness_label": (
            "Safety/eval readiness: ready" if safety_ready else "Safety/eval readiness: pending"
        ),
        "data_classification_gate_state": DATA_CLASSIFICATION_GATE_LOCAL_ONLY,
        "data_classification_gate_label": "Data classification gate: local-only",
        "execution_proof_marker": execution_proof,
        "future_execution_validation_marker": FUTURE_EXECUTION_VALIDATION_MARKER,
        "functional_ai_release_gate_state": functional_release_gate,
        "functional_ai_release_gate_label": (
            "Functional-AI release gate: ready for future version"
            if functional_ai_release_ready
            else "Functional-AI release gate: pending"
        ),
        "v18_release_gate_state": v18_release_gate,
        "v18_release_gate_label": (
            "v1.8.0-prebeta release gate: ready for future version"
            if functional_ai_release_ready
            else "v1.8.0-prebeta release gate: pending functional AI proof"
        ),
    }


def _provider_path_consent_contract_fields(
    *,
    state: str,
    reason_code: str,
    eligibility: str,
    blocker: str,
    provenance: str = PROVIDER_PATH_PROVENANCE_DEFAULT_CONFIG,
    config_state: str = PROVIDER_PATH_CONFIG_STATE_DEFAULT,
    config_valid: bool = True,
    approval_status: str = PROVIDER_PATH_APPROVAL_STATUS_MISSING,
    provider_path_selected: bool = False,
    provider_config_present: bool = False,
    provider_config_valid: bool = True,
    provider_profile_available: bool = False,
    provider_available: bool = False,
    setup_consent_ready: bool = False,
    execution_consent_ready: bool = False,
    data_visibility_ready: bool = False,
    audit_ready: bool = False,
    capability_ready: bool = False,
    manifest_ready: bool = False,
    safety_ready: bool = False,
    setup_approved: bool = False,
    execution_approved: bool = False,
    future_execution_branch_ready: bool = False,
    functional_ai_release_ready: bool = False,
) -> dict[str, object]:
    state_labels = {
        PROVIDER_PATH_READINESS_STATE_UNKNOWN: "Provider path readiness: unknown",
        PROVIDER_PATH_READINESS_STATE_UNAVAILABLE: "Provider path readiness: unavailable",
        PROVIDER_PATH_READINESS_STATE_DISABLED: "Provider path readiness: disabled",
        PROVIDER_PATH_READINESS_STATE_UNSELECTED: "Provider path readiness: not selected",
        PROVIDER_PATH_READINESS_STATE_SELECTION_REQUIRED: "Provider path readiness: selection required",
        PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_POLICY: "Provider path readiness: blocked by policy",
        PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CONSENT: "Provider path readiness: blocked by consent",
        PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CAPABILITY: "Provider path readiness: blocked by capability",
        PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_MANIFEST: "Provider path readiness: blocked by manifest",
        PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_SAFETY: "Provider path readiness: blocked by safety/eval",
        PROVIDER_PATH_READINESS_STATE_READY_FUTURE_GATED:
            "Provider path readiness: ready but future-gated",
        PROVIDER_PATH_READINESS_STATE_READY_BUT_NOT_APPROVED:
            "Provider path readiness: ready but not approved",
        PROVIDER_PATH_READINESS_STATE_DEGRADED: "Provider path readiness: degraded and fail-closed",
        PROVIDER_PATH_READINESS_STATE_READY_FOR_FUTURE_EXECUTION_BRANCH:
            "Provider path readiness: ready for future execution branch",
    }
    eligibility_labels = {
        PROVIDER_PATH_ELIGIBILITY_UNAVAILABLE: "Provider path eligibility: unavailable",
        PROVIDER_PATH_ELIGIBILITY_DISABLED: "Provider path eligibility: disabled",
        PROVIDER_PATH_ELIGIBILITY_BLOCKED: "Provider path eligibility: blocked",
        PROVIDER_PATH_ELIGIBILITY_SELECTION_REQUIRED:
            "Provider path eligibility: selection required",
        PROVIDER_PATH_ELIGIBILITY_FUTURE_GATED: "Provider path eligibility: future-gated",
        PROVIDER_PATH_ELIGIBILITY_READY_NOT_APPROVED:
            "Provider path eligibility: ready but USER approval missing",
        PROVIDER_PATH_ELIGIBILITY_FUTURE_EXECUTION_BRANCH:
            "Provider path eligibility: future execution branch",
    }
    blocker_labels = {
        PROVIDER_PATH_BLOCKER_NONE: "Provider path blocker: none before future branch",
        PROVIDER_PATH_BLOCKER_EXECUTION_READINESS_REQUIRED:
            "Provider path blocker: execution readiness required",
        PROVIDER_PATH_BLOCKER_SELECTION_REQUIRED:
            "Provider path blocker: provider selection required",
        PROVIDER_PATH_BLOCKER_CONFIG_REQUIRED: "Provider path blocker: provider config required",
        PROVIDER_PATH_BLOCKER_CONFIG_INVALID: "Provider path blocker: provider config invalid",
        PROVIDER_PATH_BLOCKER_SETUP_CONSENT_REQUIRED:
            "Provider path blocker: setup consent required",
        PROVIDER_PATH_BLOCKER_EXECUTION_CONSENT_REQUIRED:
            "Provider path blocker: execution consent required",
        PROVIDER_PATH_BLOCKER_DATA_VISIBILITY_REQUIRED:
            "Provider path blocker: provider-visible data approval required",
        PROVIDER_PATH_BLOCKER_CAPABILITY_REQUIRED: "Provider path blocker: capability required",
        PROVIDER_PATH_BLOCKER_MANIFEST_REQUIRED: "Provider path blocker: manifest required",
        PROVIDER_PATH_BLOCKER_SAFETY_EVAL_REQUIRED: "Provider path blocker: safety/eval required",
        PROVIDER_PATH_BLOCKER_POLICY_BLOCKED: "Provider path blocker: policy blocked",
        PROVIDER_PATH_BLOCKER_SETUP_APPROVAL_REQUIRED:
            "Provider path blocker: setup approval required",
        PROVIDER_PATH_BLOCKER_EXECUTION_APPROVAL_REQUIRED:
            "Provider path blocker: provider execution approval required",
        PROVIDER_PATH_BLOCKER_VERSION_JUMP_REQUIRED:
            "Provider path blocker: v1.8.0-prebeta version jump required",
    }
    reason_labels = {
        PROVIDER_PATH_REASON_DEFAULT_UNAVAILABLE: "Provider path reason: readiness only",
        PROVIDER_PATH_REASON_CONFIG_MISSING_FAIL_CLOSED:
            "Provider path reason: missing config failed closed",
        PROVIDER_PATH_REASON_CONFIG_INVALID_FAIL_CLOSED:
            "Provider path reason: invalid config failed closed",
        PROVIDER_PATH_REASON_EXECUTION_READINESS_UNAVAILABLE:
            "Provider path reason: execution readiness unavailable",
        PROVIDER_PATH_REASON_UNSELECTED: "Provider path reason: provider path not selected",
        PROVIDER_PATH_REASON_CONFIG_MISSING: "Provider path reason: provider config missing",
        PROVIDER_PATH_REASON_CONFIG_INVALID: "Provider path reason: provider config invalid",
        PROVIDER_PATH_REASON_SETUP_CONSENT_REQUIRED:
            "Provider path reason: setup consent required",
        PROVIDER_PATH_REASON_EXECUTION_CONSENT_REQUIRED:
            "Provider path reason: execution consent required",
        PROVIDER_PATH_REASON_DATA_VISIBILITY_BLOCKED:
            "Provider path reason: provider-visible data approval blocked",
        PROVIDER_PATH_REASON_CAPABILITY_MISSING: "Provider path reason: capability missing",
        PROVIDER_PATH_REASON_MANIFEST_MISSING: "Provider path reason: manifest missing",
        PROVIDER_PATH_REASON_SAFETY_BLOCKED: "Provider path reason: safety/eval blocked",
        PROVIDER_PATH_REASON_POLICY_BLOCKED: "Provider path reason: policy blocked",
        PROVIDER_PATH_REASON_SETUP_APPROVAL_MISSING:
            "Provider path reason: setup approval missing",
        PROVIDER_PATH_REASON_EXECUTION_APPROVAL_MISSING:
            "Provider path reason: execution approval missing",
        PROVIDER_PATH_REASON_READY_FOR_FUTURE_EXECUTION_BRANCH:
            "Provider path reason: ready for future execution branch",
        PROVIDER_PATH_REASON_FUNCTIONAL_AI_FUTURE_VERSION:
            "Provider path reason: functional AI proof reserved for v1.8.0-prebeta",
    }
    provenance_labels = {
        PROVIDER_PATH_PROVENANCE_DEFAULT_CONFIG: "Provider path provenance: default config",
        PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG: "Provider path provenance: local config",
        PROVIDER_PATH_PROVENANCE_EXECUTION_READINESS_STATE:
            "Provider path provenance: execution readiness state",
        PROVIDER_PATH_PROVENANCE_PROVIDER_SELECTION_CONTRACT:
            "Provider path provenance: provider selection contract",
        PROVIDER_PATH_PROVENANCE_PROVIDER_CONFIG_CONTRACT:
            "Provider path provenance: provider config contract",
        PROVIDER_PATH_PROVENANCE_CONSENT_STATE: "Provider path provenance: consent state",
        PROVIDER_PATH_PROVENANCE_DATA_VISIBILITY_CONTRACT:
            "Provider path provenance: data visibility contract",
        PROVIDER_PATH_PROVENANCE_CAPABILITY_CONTRACT:
            "Provider path provenance: capability contract",
        PROVIDER_PATH_PROVENANCE_MANIFEST_STATE: "Provider path provenance: manifest state",
        PROVIDER_PATH_PROVENANCE_SAFETY_EVAL: "Provider path provenance: safety/eval",
        PROVIDER_PATH_PROVENANCE_AUDIT_POLICY: "Provider path provenance: audit policy",
        PROVIDER_PATH_PROVENANCE_FUTURE_RUNTIME_CHECK:
            "Provider path provenance: future runtime check",
        PROVIDER_PATH_PROVENANCE_VALIDATOR_FIXTURE:
            "Provider path provenance: validator fixture",
    }
    config_labels = {
        PROVIDER_PATH_CONFIG_STATE_DEFAULT: "Provider path config: safe default local-only",
        PROVIDER_PATH_CONFIG_STATE_MISSING: "Provider path config: missing; readiness disabled",
        PROVIDER_PATH_CONFIG_STATE_INVALID: "Provider path config: invalid; degraded fail-closed",
        PROVIDER_PATH_CONFIG_STATE_LOCAL: "Provider path config: local-only",
    }
    approval_labels = {
        PROVIDER_PATH_APPROVAL_STATUS_MISSING: "Provider path approval: USER approval missing",
        PROVIDER_PATH_APPROVAL_STATUS_FUTURE_GATED: "Provider path approval: future-gated",
        PROVIDER_PATH_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF:
            "Provider path approval: ready for future proof branch",
    }
    normalized_state = state if state in PROVIDER_PATH_READINESS_STATES else PROVIDER_PATH_READINESS_STATE_DEGRADED
    normalized_reason = (
        reason_code if reason_code in PROVIDER_PATH_REASON_CODES else PROVIDER_PATH_REASON_CONFIG_INVALID_FAIL_CLOSED
    )
    normalized_provenance = (
        provenance if provenance in PROVIDER_PATH_PROVENANCE_SOURCES else PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG
    )
    normalized_config = (
        config_state
        if config_state
        in {
            PROVIDER_PATH_CONFIG_STATE_DEFAULT,
            PROVIDER_PATH_CONFIG_STATE_MISSING,
            PROVIDER_PATH_CONFIG_STATE_INVALID,
            PROVIDER_PATH_CONFIG_STATE_LOCAL,
        }
        else PROVIDER_PATH_CONFIG_STATE_INVALID
    )
    provider_config_status = (
        PROVIDER_CONFIG_ENVELOPE_STATUS_INVALID
        if provider_config_present and not provider_config_valid
        else PROVIDER_CONFIG_ENVELOPE_STATUS_LOCAL_ONLY_READY
        if provider_config_present
        else PROVIDER_CONFIG_ENVELOPE_STATUS_MISSING
    )
    provider_path_status = (
        PROVIDER_PATH_STATUS_SELECTED_FUTURE_GATED if provider_path_selected else PROVIDER_PATH_STATUS_NOT_SELECTED
    )
    consent_readiness = (
        CONSENT_READINESS_STATE_BLOCKED_BY_DATA_VISIBILITY
        if setup_consent_ready and execution_consent_ready and not data_visibility_ready
        else CONSENT_READINESS_STATE_BLOCKED_BY_AUDIT_REQUIREMENTS
        if setup_consent_ready and execution_consent_ready and data_visibility_ready and not audit_ready
        else CONSENT_READINESS_STATE_READY_BUT_NOT_COLLECTED
        if setup_consent_ready and execution_consent_ready
        else CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_EXECUTION
        if setup_consent_ready
        else CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_SETUP
    )
    setup_eligibility = (
        PROVIDER_SETUP_ELIGIBILITY_CONFIG_REQUIRED
        if not provider_path_selected or not provider_config_present
        else PROVIDER_SETUP_ELIGIBILITY_BLOCKED
        if not setup_consent_ready or not capability_ready or not manifest_ready or not safety_ready
        else PROVIDER_SETUP_ELIGIBILITY_FUTURE_GATED
        if not setup_approved
        else PROVIDER_SETUP_ELIGIBILITY_EXECUTION_GATED
    )
    setup_blocker = (
        PROVIDER_SETUP_BLOCKER_CONFIG_REQUIRED
        if not provider_path_selected or not provider_config_present
        else PROVIDER_SETUP_BLOCKER_CONSENT_REQUIRED
        if not setup_consent_ready
        else PROVIDER_SETUP_BLOCKER_CAPABILITY_REQUIRED
        if not capability_ready
        else PROVIDER_SETUP_BLOCKER_MANIFEST_REQUIRED
        if not manifest_ready
        else PROVIDER_SETUP_BLOCKER_POLICY_BLOCKED
        if not safety_ready
        else PROVIDER_SETUP_BLOCKER_SETUP_DISABLED
    )
    return {
        "provider_path_readiness_state": normalized_state,
        "provider_path_readiness_label": state_labels[normalized_state],
        "provider_path_eligibility_state": eligibility,
        "provider_path_eligibility_label": eligibility_labels.get(eligibility, "Provider path eligibility: blocked"),
        "provider_path_blocker_state": blocker,
        "provider_path_blocker_label": blocker_labels.get(blocker, "Provider path blocker: policy blocked"),
        "provider_path_reason_code": normalized_reason,
        "provider_path_reason_label": reason_labels[normalized_reason],
        "provider_path_provenance": normalized_provenance,
        "provider_path_provenance_label": provenance_labels[normalized_provenance],
        "provider_path_state_schema_version": PROVIDER_PATH_READINESS_STATE_SCHEMA_VERSION,
        "provider_path_config_schema_version": PROVIDER_PATH_READINESS_CONFIG_SCHEMA_VERSION,
        "provider_path_config_state": normalized_config,
        "provider_path_config_label": config_labels[normalized_config],
        "provider_path_config_migration": PROVIDER_PATH_READINESS_CONFIG_MIGRATION_POSTURE,
        "provider_path_config_valid": bool(config_valid),
        "provider_path_approval_status": approval_status,
        "provider_path_approval_label": approval_labels.get(approval_status, approval_labels[PROVIDER_PATH_APPROVAL_STATUS_MISSING]),
        "provider_path_status": provider_path_status,
        "provider_path_label": (
            "Provider path: selected for future-gated readiness"
            if provider_path_selected
            else "Provider path: not selected"
        ),
        "provider_selection_posture": (
            PROVIDER_SELECTION_POSTURE_SELECTED_FUTURE_GATED
            if provider_path_selected
            else PROVIDER_SELECTION_POSTURE_PENDING_APPROVAL
        ),
        "provider_selection_posture_label": (
            "Provider selection: selected for future readiness"
            if provider_path_selected
            else "Provider selection: pending USER approval"
        ),
        "provider_profile_id": PROVIDER_PROFILE_ID_LOCAL_NULL,
        "provider_profile_kind": PROVIDER_PROFILE_KIND_NULL_LOCAL,
        "provider_profile_display_name": "Local/null provider profile",
        "provider_profile_source": PROVIDER_PROFILE_SOURCE_LOCAL_SCAFFOLD,
        "provider_profile_metadata_contract_version": PROVIDER_PROFILE_METADATA_CONTRACT_VERSION,
        "provider_profile_available": provider_profile_available,
        "provider_sdk_requirement_posture": PROVIDER_SDK_REQUIREMENT_PENDING_APPROVAL,
        "provider_network_requirement_posture": PROVIDER_NETWORK_REQUIREMENT_BLOCKED,
        "provider_config_status": provider_config_status,
        "provider_availability_posture": (
            PROVIDER_AVAILABILITY_READY_FUTURE_GATED if provider_available else PROVIDER_AVAILABILITY_UNAVAILABLE
        ),
        "provider_setup_approval_status": (
            PROVIDER_SETUP_APPROVAL_STATUS_FUTURE_GATED
            if setup_approved
            else PROVIDER_SETUP_APPROVAL_STATUS_MISSING
        ),
        "provider_execution_approval_status": PROVIDER_EXECUTION_APPROVAL_STATUS_PROVIDER_PATH_MISSING,
        "provider_visible_data_scope": PROVIDER_VISIBLE_DATA_REQUIREMENT_NONE,
        "local_null_provider_fallback_status": LOCAL_NULL_PROVIDER_FALLBACK_ACTIVE,
        "future_sdk_handoff_marker": FUTURE_SDK_HANDOFF_MARKER,
        "future_provider_setup_handoff_marker": FUTURE_PROVIDER_SETUP_HANDOFF_MARKER,
        "consent_readiness_state": consent_readiness,
        "consent_readiness_label": {
            CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_SETUP:
                "Consent readiness: setup consent required",
            CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_EXECUTION:
                "Consent readiness: execution consent required",
            CONSENT_READINESS_STATE_BLOCKED_BY_DATA_VISIBILITY:
                "Consent readiness: blocked by provider-visible data requirements",
            CONSENT_READINESS_STATE_BLOCKED_BY_AUDIT_REQUIREMENTS:
                "Consent readiness: blocked by audit requirements",
            CONSENT_READINESS_STATE_READY_BUT_NOT_COLLECTED:
                "Consent readiness: ready but not collected",
        }.get(consent_readiness, "Consent readiness: required before provider setup"),
        "consent_state_schema_version": CONSENT_READINESS_STATE_SCHEMA_VERSION,
        "consent_config_schema_version": CONSENT_READINESS_CONFIG_SCHEMA_VERSION,
        "consent_config_migration": CONSENT_READINESS_CONFIG_MIGRATION_POSTURE,
        "setup_consent_state": (
            CONSENT_READINESS_STATE_READY_BUT_NOT_COLLECTED
            if setup_consent_ready
            else CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_SETUP
        ),
        "setup_consent_label": (
            "Setup consent: ready but not collected"
            if setup_consent_ready
            else "Setup consent: required before provider setup"
        ),
        "setup_consent_blocker_state": (
            CONSENT_BLOCKER_NONE if setup_consent_ready else CONSENT_BLOCKER_SETUP_REQUIRED
        ),
        "setup_consent_blocker_label": (
            "Setup consent blocker: none before future setup approval"
            if setup_consent_ready
            else "Setup consent blocker: consent collection not approved"
        ),
        "setup_consent_reason_code": (
            CONSENT_REASON_READY_BUT_NOT_COLLECTED if setup_consent_ready else CONSENT_REASON_SETUP_REQUIRED
        ),
        "setup_consent_reason_label": (
            "Setup consent reason: ready but not collected"
            if setup_consent_ready
            else "Setup consent reason: required before provider setup"
        ),
        "setup_consent_provenance": CONSENT_PROVENANCE_PROVIDER_PATH_CONTRACT,
        "setup_consent_provenance_label": "Setup consent provenance: provider path contract",
        "setup_consent_handoff_state": SETUP_CONSENT_HANDOFF_FUTURE_GATED,
        "setup_consent_handoff_label": "Setup consent handoff: future-gated",
        "execution_consent_state": (
            CONSENT_READINESS_STATE_READY_BUT_NOT_COLLECTED
            if execution_consent_ready
            else CONSENT_READINESS_STATE_REQUIRED_FOR_PROVIDER_EXECUTION
        ),
        "execution_consent_label": (
            "Execution consent: ready but not collected"
            if execution_consent_ready
            else "Execution consent: required before prompt/model execution"
        ),
        "execution_consent_blocker_state": (
            CONSENT_BLOCKER_NONE if execution_consent_ready else CONSENT_BLOCKER_EXECUTION_REQUIRED
        ),
        "execution_consent_blocker_label": (
            "Execution consent blocker: none before future execution approval"
            if execution_consent_ready
            else "Execution consent blocker: consent collection not approved"
        ),
        "execution_consent_reason_code": (
            CONSENT_REASON_READY_BUT_NOT_COLLECTED
            if execution_consent_ready
            else CONSENT_REASON_EXECUTION_REQUIRED
        ),
        "execution_consent_reason_label": (
            "Execution consent reason: ready but not collected"
            if execution_consent_ready
            else "Execution consent reason: required before provider execution"
        ),
        "execution_consent_provenance": CONSENT_PROVENANCE_PROVIDER_PATH_CONTRACT,
        "execution_consent_provenance_label": "Execution consent provenance: provider path contract",
        "execution_consent_handoff_state": EXECUTION_CONSENT_HANDOFF_FUTURE_GATED,
        "execution_consent_handoff_label": "Execution consent handoff: future-gated",
        "provider_visible_data_requirement_state": (
            PROVIDER_VISIBLE_DATA_REQUIREMENT_NONE
            if data_visibility_ready or not provider_path_selected
            else PROVIDER_VISIBLE_DATA_REQUIREMENT_BLOCKED
        ),
        "provider_visible_data_requirement_label": (
            "Provider-visible data requirement: none"
            if data_visibility_ready or not provider_path_selected
            else "Provider-visible data requirement: blocked pending approval"
        ),
        "data_classification_posture_state": DATA_CLASSIFICATION_POSTURE_LOCAL_ONLY,
        "data_classification_posture_label": "Data classification posture: local-only",
        "audit_envelope_posture_state": AUDIT_ENVELOPE_POSTURE_PLANNED,
        "audit_envelope_posture_label": (
            "Audit envelope posture: ready for future proof" if audit_ready else "Audit envelope posture: planned; no collection"
        ),
        "local_only_status_posture": LOCAL_ONLY_STATUS_POSTURE_ACTIVE,
        "local_only_status_label": "Local-only status: active",
        "provider_setup_future_gated_posture": PROVIDER_SETUP_FUTURE_GATED_POSTURE,
        "provider_setup_future_gated_label": "Provider setup: future-gated",
        "provider_execution_future_gated_posture": PROVIDER_EXECUTION_FUTURE_GATED_POSTURE,
        "provider_execution_future_gated_label": "Provider execution: disabled; future-gated",
        "provider_path_gate_state": (
            PROVIDER_PATH_GATE_FUTURE_GATED if provider_path_selected else PROVIDER_PATH_GATE_BLOCKED
        ),
        "provider_config_gate_state": (
            PROVIDER_CONFIG_GATE_READY_FUTURE_GATED
            if provider_config_present and provider_config_valid
            else PROVIDER_CONFIG_GATE_BLOCKED
        ),
        "setup_consent_gate_state": (
            SETUP_CONSENT_GATE_READY_FUTURE_GATED if setup_consent_ready else SETUP_CONSENT_GATE_REQUIRED
        ),
        "execution_consent_gate_state": (
            EXECUTION_CONSENT_GATE_READY_FUTURE_GATED
            if execution_consent_ready
            else EXECUTION_CONSENT_GATE_REQUIRED
        ),
        "provider_visible_data_gate_state": (
            PROVIDER_VISIBLE_DATA_GATE_NONE if data_visibility_ready or not provider_path_selected else PROVIDER_VISIBLE_DATA_GATE_BLOCKED
        ),
        "audit_gate_state": AUDIT_GATE_READY_FUTURE_GATED if audit_ready else AUDIT_GATE_PLANNED,
        "setup_eligibility_state": setup_eligibility,
        "setup_eligibility_label": {
            PROVIDER_SETUP_ELIGIBILITY_CONFIG_REQUIRED:
                "Setup eligibility: provider path/config required",
            PROVIDER_SETUP_ELIGIBILITY_BLOCKED:
                "Setup eligibility: blocked by consent, capability, manifest, or safety",
            PROVIDER_SETUP_ELIGIBILITY_FUTURE_GATED:
                "Setup eligibility: future-gated pending USER approval",
            PROVIDER_SETUP_ELIGIBILITY_EXECUTION_GATED:
                "Setup eligibility: complete, execution still gated",
        }.get(setup_eligibility, "Setup eligibility: disabled"),
        "setup_blocker_state": setup_blocker,
        "setup_blocker_label": {
            PROVIDER_SETUP_BLOCKER_CONFIG_REQUIRED:
                "Setup blocker: provider path/config required",
            PROVIDER_SETUP_BLOCKER_CONSENT_REQUIRED:
                "Setup blocker: setup consent required",
            PROVIDER_SETUP_BLOCKER_CAPABILITY_REQUIRED:
                "Setup blocker: capability proof required",
            PROVIDER_SETUP_BLOCKER_MANIFEST_REQUIRED:
                "Setup blocker: manifest proof required",
            PROVIDER_SETUP_BLOCKER_POLICY_BLOCKED:
                "Setup blocker: safety/eval or policy approval required",
            PROVIDER_SETUP_BLOCKER_SETUP_DISABLED:
                "Setup blocker: future USER setup approval required",
        }.get(setup_blocker, "Setup blocker: future USER approval required"),
        "future_provider_gate_status": PROVIDER_FUTURE_GATE_STATUS_SETUP_REQUIRED,
        "future_provider_gate_label": "Future provider gate: USER approval required before setup",
        "provider_visible_data": "none",
        "provider_visible_data_label": "Provider-visible data: none",
        "provider_visible_data_detail": "No prompt, file, screen, memory, telemetry, or provider config is sent",
        "consent_state": PROVIDER_CONSENT_REQUIRED,
        "consent_label": "Consent required before provider setup",
        "provider_consent_boundary_label": (
            "Consent boundary: setup and execution consent are separate future gates"
        ),
        "provider_next_action_label": "Next: provider path and consent readiness remain local-only",
        "interaction_label": "Provider path readiness only",
        "interaction_disabled_reason": (
            "Provider setup, consent collection, prompt routing, and model execution require later USER approval"
        ),
        "functional_ai_release_gate_state": (
            FUNCTIONAL_AI_RELEASE_GATE_READY_FUTURE_VERSION
            if functional_ai_release_ready
            else FUNCTIONAL_AI_RELEASE_GATE_PENDING
        ),
        "functional_ai_release_gate_label": (
            "Functional-AI release gate: ready for future version"
            if functional_ai_release_ready
            else "Functional-AI release gate: pending"
        ),
        "v18_release_gate_state": (
            V18_RELEASE_GATE_READY_FUTURE_VERSION
            if functional_ai_release_ready
            else V18_RELEASE_GATE_PENDING_FUNCTIONAL_AI
        ),
        "v18_release_gate_label": (
            "v1.8.0-prebeta release gate: ready for future version"
            if functional_ai_release_ready
            else "v1.8.0-prebeta release gate: pending functional AI proof"
        ),
    }


def _provider_setup_consent_flow_contract_fields(path_state: AIProviderStateSnapshot) -> dict[str, object]:
    setup_state = SETUP_FLOW_STATE_UNAVAILABLE
    setup_eligibility = SETUP_FLOW_ELIGIBILITY_UNAVAILABLE
    setup_blocker = SETUP_FLOW_BLOCKER_PROVIDER_PATH_REQUIRED
    setup_reason = SETUP_FLOW_REASON_DEFAULT_UNAVAILABLE
    setup_provenance = SETUP_FLOW_PROVENANCE_PROVIDER_PATH
    setup_approval = SETUP_FLOW_APPROVAL_STATUS_MISSING
    consent_state = CONSENT_FLOW_STATE_REQUIRED_FOR_SETUP
    consent_eligibility = CONSENT_FLOW_ELIGIBILITY_REQUIRED
    consent_blocker = CONSENT_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED
    consent_reason = CONSENT_FLOW_REASON_SETUP_REQUIRED
    consent_provenance = CONSENT_FLOW_PROVENANCE_SETUP_CONSENT
    consent_approval = CONSENT_FLOW_APPROVAL_STATUS_MISSING
    setup_gate = SETUP_FLOW_GATE_BLOCKED
    consent_gate = CONSENT_FLOW_GATE_REQUIRED
    setup_approval_gate = SETUP_APPROVAL_GATE_MISSING
    execution_approval_gate = EXECUTION_APPROVAL_GATE_MISSING

    if path_state.provider_path_config_state == PROVIDER_PATH_CONFIG_STATE_MISSING:
        setup_state = SETUP_FLOW_STATE_DISABLED
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_DISABLED
        setup_reason = SETUP_FLOW_REASON_DEFAULT_UNAVAILABLE
        setup_provenance = SETUP_FLOW_PROVENANCE_PROVIDER_PATH
        consent_state = CONSENT_FLOW_STATE_UNAVAILABLE
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_UNAVAILABLE
        consent_blocker = CONSENT_FLOW_BLOCKER_COLLECTION_NOT_APPROVED
        consent_reason = CONSENT_FLOW_REASON_DEFAULT_UNAVAILABLE
        consent_provenance = CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION
    elif path_state.provider_path_config_state == PROVIDER_PATH_CONFIG_STATE_INVALID:
        setup_state = SETUP_FLOW_STATE_DEGRADED
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_reason = SETUP_FLOW_REASON_POLICY_BLOCKED
        setup_provenance = SETUP_FLOW_PROVENANCE_POLICY
        consent_state = CONSENT_FLOW_STATE_DEGRADED
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_BLOCKED
        consent_blocker = CONSENT_FLOW_BLOCKER_POLICY_BLOCKED
        consent_reason = CONSENT_FLOW_REASON_POLICY_BLOCKED
        consent_provenance = CONSENT_FLOW_PROVENANCE_AUDIT
    elif path_state.provider_path_readiness_state in {
        PROVIDER_PATH_READINESS_STATE_UNAVAILABLE,
        PROVIDER_PATH_READINESS_STATE_DISABLED,
        PROVIDER_PATH_READINESS_STATE_DEGRADED,
    }:
        setup_state = SETUP_FLOW_STATE_UNAVAILABLE
    elif path_state.provider_path_readiness_state in {
        PROVIDER_PATH_READINESS_STATE_UNSELECTED,
        PROVIDER_PATH_READINESS_STATE_SELECTION_REQUIRED,
    }:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_PROVIDER_PATH
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_reason = SETUP_FLOW_REASON_PROVIDER_PATH_REQUIRED
    elif path_state.provider_path_readiness_state == PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_POLICY:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_POLICY
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_blocker = SETUP_FLOW_BLOCKER_POLICY_BLOCKED
        setup_reason = SETUP_FLOW_REASON_POLICY_BLOCKED
        setup_provenance = SETUP_FLOW_PROVENANCE_POLICY
        consent_state = CONSENT_FLOW_STATE_BLOCKED_BY_POLICY
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_BLOCKED
        consent_blocker = CONSENT_FLOW_BLOCKER_POLICY_BLOCKED
        consent_reason = CONSENT_FLOW_REASON_POLICY_BLOCKED
        consent_provenance = CONSENT_FLOW_PROVENANCE_AUDIT
    elif path_state.provider_path_blocker_state == PROVIDER_PATH_BLOCKER_SETUP_CONSENT_REQUIRED:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_SETUP_CONSENT
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_blocker = SETUP_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED
        setup_reason = SETUP_FLOW_REASON_SETUP_CONSENT_REQUIRED
        setup_provenance = SETUP_FLOW_PROVENANCE_CONSENT
    elif path_state.provider_path_blocker_state == PROVIDER_PATH_BLOCKER_EXECUTION_CONSENT_REQUIRED:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_EXECUTION_CONSENT
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_blocker = SETUP_FLOW_BLOCKER_EXECUTION_CONSENT_REQUIRED
        setup_reason = SETUP_FLOW_REASON_EXECUTION_CONSENT_REQUIRED
        setup_provenance = SETUP_FLOW_PROVENANCE_CONSENT
        consent_state = CONSENT_FLOW_STATE_REQUIRED_FOR_EXECUTION
        consent_blocker = CONSENT_FLOW_BLOCKER_EXECUTION_CONSENT_REQUIRED
        consent_reason = CONSENT_FLOW_REASON_EXECUTION_REQUIRED
        consent_provenance = CONSENT_FLOW_PROVENANCE_EXECUTION_CONSENT
    elif path_state.provider_path_blocker_state == PROVIDER_PATH_BLOCKER_DATA_VISIBILITY_REQUIRED:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_SETUP_CONSENT
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_blocker = SETUP_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED
        setup_reason = SETUP_FLOW_REASON_SETUP_CONSENT_REQUIRED
        setup_provenance = SETUP_FLOW_PROVENANCE_CONSENT
        consent_state = CONSENT_FLOW_STATE_BLOCKED_BY_DATA_VISIBILITY
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_BLOCKED
        consent_blocker = CONSENT_FLOW_BLOCKER_DATA_VISIBILITY_REQUIRED
        consent_reason = CONSENT_FLOW_REASON_DATA_VISIBILITY_BLOCKED
        consent_provenance = CONSENT_FLOW_PROVENANCE_DATA_VISIBILITY
    elif path_state.audit_gate_state == AUDIT_GATE_PLANNED:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_SETUP_CONSENT
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_blocker = SETUP_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED
        setup_reason = SETUP_FLOW_REASON_SETUP_CONSENT_REQUIRED
        setup_provenance = SETUP_FLOW_PROVENANCE_CONSENT
        consent_state = CONSENT_FLOW_STATE_BLOCKED_BY_AUDIT_REQUIREMENTS
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_BLOCKED
        consent_blocker = CONSENT_FLOW_BLOCKER_AUDIT_REQUIRED
        consent_reason = CONSENT_FLOW_REASON_AUDIT_REQUIREMENTS_BLOCKED
        consent_provenance = CONSENT_FLOW_PROVENANCE_AUDIT
    elif path_state.provider_path_blocker_state == PROVIDER_PATH_BLOCKER_CAPABILITY_REQUIRED:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_CAPABILITY
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_blocker = SETUP_FLOW_BLOCKER_CAPABILITY_REQUIRED
        setup_reason = SETUP_FLOW_REASON_CAPABILITY_MISSING
        setup_provenance = SETUP_FLOW_PROVENANCE_CAPABILITY
        consent_state = CONSENT_FLOW_STATE_READY_BUT_NOT_COLLECTED
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_READY_NOT_COLLECTED
        consent_blocker = CONSENT_FLOW_BLOCKER_COLLECTION_NOT_APPROVED
        consent_reason = CONSENT_FLOW_REASON_READY_BUT_NOT_COLLECTED
        consent_provenance = CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION
    elif path_state.provider_path_blocker_state == PROVIDER_PATH_BLOCKER_MANIFEST_REQUIRED:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_MANIFEST
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_blocker = SETUP_FLOW_BLOCKER_MANIFEST_REQUIRED
        setup_reason = SETUP_FLOW_REASON_MANIFEST_MISSING
        setup_provenance = SETUP_FLOW_PROVENANCE_MANIFEST
        consent_state = CONSENT_FLOW_STATE_READY_BUT_NOT_COLLECTED
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_READY_NOT_COLLECTED
        consent_blocker = CONSENT_FLOW_BLOCKER_COLLECTION_NOT_APPROVED
        consent_reason = CONSENT_FLOW_REASON_READY_BUT_NOT_COLLECTED
        consent_provenance = CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION
    elif path_state.provider_path_blocker_state == PROVIDER_PATH_BLOCKER_SAFETY_EVAL_REQUIRED:
        setup_state = SETUP_FLOW_STATE_BLOCKED_BY_SAFETY
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_BLOCKED
        setup_blocker = SETUP_FLOW_BLOCKER_SAFETY_EVAL_REQUIRED
        setup_reason = SETUP_FLOW_REASON_SAFETY_BLOCKED
        setup_provenance = SETUP_FLOW_PROVENANCE_SAFETY
        consent_state = CONSENT_FLOW_STATE_READY_BUT_NOT_COLLECTED
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_READY_NOT_COLLECTED
        consent_blocker = CONSENT_FLOW_BLOCKER_COLLECTION_NOT_APPROVED
        consent_reason = CONSENT_FLOW_REASON_READY_BUT_NOT_COLLECTED
        consent_provenance = CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION
    elif path_state.provider_path_blocker_state == PROVIDER_PATH_BLOCKER_SETUP_APPROVAL_REQUIRED:
        setup_state = SETUP_FLOW_STATE_READY_BUT_NOT_APPROVED
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_READY_NOT_APPROVED
        setup_blocker = SETUP_FLOW_BLOCKER_SETUP_APPROVAL_REQUIRED
        setup_reason = SETUP_FLOW_REASON_SETUP_APPROVAL_MISSING
        setup_provenance = SETUP_FLOW_PROVENANCE_FUTURE_RUNTIME
        consent_state = CONSENT_FLOW_STATE_READY_BUT_NOT_COLLECTED
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_READY_NOT_COLLECTED
        consent_blocker = CONSENT_FLOW_BLOCKER_COLLECTION_NOT_APPROVED
        consent_reason = CONSENT_FLOW_REASON_READY_BUT_NOT_COLLECTED
        consent_provenance = CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION
    elif path_state.provider_path_readiness_state == PROVIDER_PATH_READINESS_STATE_READY_FOR_FUTURE_EXECUTION_BRANCH:
        setup_state = SETUP_FLOW_STATE_READY_FOR_FUTURE_SETUP_BRANCH
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_FUTURE_SETUP_BRANCH
        setup_blocker = SETUP_FLOW_BLOCKER_FUTURE_SETUP_BRANCH
        setup_reason = SETUP_FLOW_REASON_READY_FOR_FUTURE_SETUP_BRANCH
        setup_provenance = SETUP_FLOW_PROVENANCE_FUTURE_RUNTIME
        setup_approval = SETUP_FLOW_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF
        consent_state = CONSENT_FLOW_STATE_READY_FOR_FUTURE_CONSENT_BRANCH
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_FUTURE_CONSENT_BRANCH
        consent_blocker = CONSENT_FLOW_BLOCKER_FUTURE_CONSENT_BRANCH
        consent_reason = CONSENT_FLOW_REASON_READY_FOR_FUTURE_CONSENT_BRANCH
        consent_provenance = CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION
        consent_approval = CONSENT_FLOW_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF
        setup_gate = SETUP_FLOW_GATE_FUTURE_GATED
        consent_gate = CONSENT_FLOW_GATE_FUTURE_GATED
        setup_approval_gate = SETUP_APPROVAL_GATE_FUTURE_GATED
        execution_approval_gate = EXECUTION_APPROVAL_GATE_FUTURE_GATED
    else:
        setup_state = SETUP_FLOW_STATE_READY_FUTURE_GATED
        setup_eligibility = SETUP_FLOW_ELIGIBILITY_FUTURE_GATED
        setup_blocker = SETUP_FLOW_BLOCKER_SETUP_APPROVAL_REQUIRED
        setup_reason = SETUP_FLOW_REASON_SETUP_APPROVAL_MISSING
        setup_provenance = SETUP_FLOW_PROVENANCE_FUTURE_RUNTIME
        setup_approval = SETUP_FLOW_APPROVAL_STATUS_FUTURE_GATED
        consent_state = CONSENT_FLOW_STATE_READY_FUTURE_GATED
        consent_eligibility = CONSENT_FLOW_ELIGIBILITY_FUTURE_GATED
        consent_blocker = CONSENT_FLOW_BLOCKER_COLLECTION_NOT_APPROVED
        consent_reason = CONSENT_FLOW_REASON_READY_BUT_NOT_COLLECTED
        consent_provenance = CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION
        consent_approval = CONSENT_FLOW_APPROVAL_STATUS_FUTURE_GATED
        setup_gate = SETUP_FLOW_GATE_FUTURE_GATED
        consent_gate = CONSENT_FLOW_GATE_FUTURE_GATED
        setup_approval_gate = SETUP_APPROVAL_GATE_FUTURE_GATED

    setup_labels = {
        SETUP_FLOW_STATE_UNAVAILABLE: "Setup flow readiness: unavailable",
        SETUP_FLOW_STATE_DISABLED: "Setup flow readiness: disabled",
        SETUP_FLOW_STATE_BLOCKED_BY_PROVIDER_PATH: "Setup flow readiness: blocked by provider path",
        SETUP_FLOW_STATE_BLOCKED_BY_SETUP_CONSENT: "Setup flow readiness: blocked by setup consent",
        SETUP_FLOW_STATE_BLOCKED_BY_EXECUTION_CONSENT:
            "Setup flow readiness: blocked by execution consent",
        SETUP_FLOW_STATE_BLOCKED_BY_POLICY: "Setup flow readiness: blocked by policy",
        SETUP_FLOW_STATE_BLOCKED_BY_CAPABILITY: "Setup flow readiness: blocked by capability",
        SETUP_FLOW_STATE_BLOCKED_BY_MANIFEST: "Setup flow readiness: blocked by manifest",
        SETUP_FLOW_STATE_BLOCKED_BY_SAFETY: "Setup flow readiness: blocked by safety/eval",
        SETUP_FLOW_STATE_READY_FUTURE_GATED: "Setup flow readiness: ready but future-gated",
        SETUP_FLOW_STATE_READY_BUT_NOT_APPROVED:
            "Setup flow readiness: ready but USER approval missing",
        SETUP_FLOW_STATE_DEGRADED: "Setup flow readiness: degraded and fail-closed",
        SETUP_FLOW_STATE_READY_FOR_FUTURE_SETUP_BRANCH:
            "Setup flow readiness: ready for future setup branch",
    }
    setup_eligibility_labels = {
        SETUP_FLOW_ELIGIBILITY_UNAVAILABLE: "Setup flow eligibility: unavailable",
        SETUP_FLOW_ELIGIBILITY_DISABLED: "Setup flow eligibility: disabled",
        SETUP_FLOW_ELIGIBILITY_BLOCKED: "Setup flow eligibility: blocked",
        SETUP_FLOW_ELIGIBILITY_FUTURE_GATED: "Setup flow eligibility: future-gated",
        SETUP_FLOW_ELIGIBILITY_READY_NOT_APPROVED:
            "Setup flow eligibility: ready but USER approval missing",
        SETUP_FLOW_ELIGIBILITY_FUTURE_SETUP_BRANCH:
            "Setup flow eligibility: future setup branch",
    }
    setup_blocker_labels = {
        SETUP_FLOW_BLOCKER_PROVIDER_PATH_REQUIRED:
            "Setup flow blocker: provider path readiness required",
        SETUP_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED:
            "Setup flow blocker: setup consent required",
        SETUP_FLOW_BLOCKER_EXECUTION_CONSENT_REQUIRED:
            "Setup flow blocker: execution consent required",
        SETUP_FLOW_BLOCKER_POLICY_BLOCKED: "Setup flow blocker: policy blocked",
        SETUP_FLOW_BLOCKER_CAPABILITY_REQUIRED: "Setup flow blocker: capability proof required",
        SETUP_FLOW_BLOCKER_MANIFEST_REQUIRED: "Setup flow blocker: manifest proof required",
        SETUP_FLOW_BLOCKER_SAFETY_EVAL_REQUIRED:
            "Setup flow blocker: safety/eval proof required",
        SETUP_FLOW_BLOCKER_SETUP_APPROVAL_REQUIRED:
            "Setup flow blocker: USER setup approval required",
        SETUP_FLOW_BLOCKER_FUTURE_SETUP_BRANCH:
            "Setup flow blocker: future setup branch required",
    }
    setup_reason_labels = {
        SETUP_FLOW_REASON_DEFAULT_UNAVAILABLE:
            "Setup flow reason: setup readiness is local-only",
        SETUP_FLOW_REASON_PROVIDER_PATH_REQUIRED:
            "Setup flow reason: provider path readiness required",
        SETUP_FLOW_REASON_SETUP_CONSENT_REQUIRED:
            "Setup flow reason: setup consent required",
        SETUP_FLOW_REASON_EXECUTION_CONSENT_REQUIRED:
            "Setup flow reason: execution consent required",
        SETUP_FLOW_REASON_POLICY_BLOCKED: "Setup flow reason: policy blocked",
        SETUP_FLOW_REASON_CAPABILITY_MISSING: "Setup flow reason: capability proof missing",
        SETUP_FLOW_REASON_MANIFEST_MISSING: "Setup flow reason: manifest proof missing",
        SETUP_FLOW_REASON_SAFETY_BLOCKED: "Setup flow reason: safety/eval blocked",
        SETUP_FLOW_REASON_SETUP_APPROVAL_MISSING:
            "Setup flow reason: USER setup approval missing",
        SETUP_FLOW_REASON_READY_FOR_FUTURE_SETUP_BRANCH:
            "Setup flow reason: ready for future setup branch",
    }
    setup_provenance_labels = {
        SETUP_FLOW_PROVENANCE_PROVIDER_PATH:
            "Setup flow provenance: provider path readiness state",
        SETUP_FLOW_PROVENANCE_CONSENT: "Setup flow provenance: consent flow state",
        SETUP_FLOW_PROVENANCE_CAPABILITY: "Setup flow provenance: capability contract",
        SETUP_FLOW_PROVENANCE_MANIFEST: "Setup flow provenance: manifest state",
        SETUP_FLOW_PROVENANCE_SAFETY: "Setup flow provenance: safety/eval",
        SETUP_FLOW_PROVENANCE_POLICY: "Setup flow provenance: audit policy",
        SETUP_FLOW_PROVENANCE_FUTURE_RUNTIME:
            "Setup flow provenance: future runtime check",
    }
    consent_labels = {
        CONSENT_FLOW_STATE_UNAVAILABLE: "Consent flow readiness: unavailable",
        CONSENT_FLOW_STATE_DEGRADED: "Consent flow readiness: degraded and fail-closed",
        CONSENT_FLOW_STATE_BLOCKED_BY_POLICY: "Consent flow readiness: blocked by policy",
        CONSENT_FLOW_STATE_BLOCKED_BY_DATA_VISIBILITY:
            "Consent flow readiness: blocked by data visibility",
        CONSENT_FLOW_STATE_BLOCKED_BY_AUDIT_REQUIREMENTS:
            "Consent flow readiness: blocked by audit requirements",
        CONSENT_FLOW_STATE_REQUIRED_FOR_SETUP: "Consent flow readiness: required before setup",
        CONSENT_FLOW_STATE_REQUIRED_FOR_EXECUTION:
            "Consent flow readiness: required before execution",
        CONSENT_FLOW_STATE_READY_FUTURE_GATED:
            "Consent flow readiness: ready but future-gated",
        CONSENT_FLOW_STATE_READY_BUT_NOT_COLLECTED:
            "Consent flow readiness: ready but not collected",
        CONSENT_FLOW_STATE_READY_FOR_FUTURE_CONSENT_BRANCH:
            "Consent flow readiness: ready for future consent branch",
    }
    consent_eligibility_labels = {
        CONSENT_FLOW_ELIGIBILITY_UNAVAILABLE: "Consent flow eligibility: unavailable",
        CONSENT_FLOW_ELIGIBILITY_REQUIRED: "Consent flow eligibility: consent required",
        CONSENT_FLOW_ELIGIBILITY_BLOCKED: "Consent flow eligibility: blocked",
        CONSENT_FLOW_ELIGIBILITY_FUTURE_GATED: "Consent flow eligibility: future-gated",
        CONSENT_FLOW_ELIGIBILITY_READY_NOT_COLLECTED:
            "Consent flow eligibility: ready but not collected",
        CONSENT_FLOW_ELIGIBILITY_FUTURE_CONSENT_BRANCH:
            "Consent flow eligibility: future consent branch",
    }
    consent_blocker_labels = {
        CONSENT_FLOW_BLOCKER_SETUP_CONSENT_REQUIRED:
            "Consent flow blocker: setup consent required",
        CONSENT_FLOW_BLOCKER_EXECUTION_CONSENT_REQUIRED:
            "Consent flow blocker: execution consent required",
        CONSENT_FLOW_BLOCKER_POLICY_BLOCKED: "Consent flow blocker: policy blocked",
        CONSENT_FLOW_BLOCKER_DATA_VISIBILITY_REQUIRED:
            "Consent flow blocker: data visibility approval required",
        CONSENT_FLOW_BLOCKER_AUDIT_REQUIRED:
            "Consent flow blocker: audit envelope required",
        CONSENT_FLOW_BLOCKER_COLLECTION_NOT_APPROVED:
            "Consent flow blocker: consent collection not approved",
        CONSENT_FLOW_BLOCKER_FUTURE_CONSENT_BRANCH:
            "Consent flow blocker: future consent branch required",
    }
    consent_reason_labels = {
        CONSENT_FLOW_REASON_DEFAULT_UNAVAILABLE:
            "Consent flow reason: consent collection is local-only",
        CONSENT_FLOW_REASON_SETUP_REQUIRED:
            "Consent flow reason: setup consent required",
        CONSENT_FLOW_REASON_EXECUTION_REQUIRED:
            "Consent flow reason: execution consent required",
        CONSENT_FLOW_REASON_POLICY_BLOCKED: "Consent flow reason: policy blocked",
        CONSENT_FLOW_REASON_DATA_VISIBILITY_BLOCKED:
            "Consent flow reason: data visibility blocked",
        CONSENT_FLOW_REASON_AUDIT_REQUIREMENTS_BLOCKED:
            "Consent flow reason: audit requirements blocked",
        CONSENT_FLOW_REASON_READY_BUT_NOT_COLLECTED:
            "Consent flow reason: ready but not collected",
        CONSENT_FLOW_REASON_READY_FOR_FUTURE_CONSENT_BRANCH:
            "Consent flow reason: ready for future consent branch",
    }
    consent_provenance_labels = {
        CONSENT_FLOW_PROVENANCE_SETUP_CONSENT:
            "Consent flow provenance: setup consent state",
        CONSENT_FLOW_PROVENANCE_EXECUTION_CONSENT:
            "Consent flow provenance: execution consent state",
        CONSENT_FLOW_PROVENANCE_DATA_VISIBILITY:
            "Consent flow provenance: data visibility contract",
        CONSENT_FLOW_PROVENANCE_AUDIT: "Consent flow provenance: audit policy",
        CONSENT_FLOW_PROVENANCE_FUTURE_COLLECTION:
            "Consent flow provenance: future consent collection",
    }
    return {
        "setup_flow_readiness_state": setup_state,
        "setup_flow_readiness_label": setup_labels.get(setup_state, setup_labels[SETUP_FLOW_STATE_DEGRADED]),
        "setup_flow_eligibility_state": setup_eligibility,
        "setup_flow_eligibility_label": setup_eligibility_labels[setup_eligibility],
        "setup_flow_blocker_state": setup_blocker,
        "setup_flow_blocker_label": setup_blocker_labels[setup_blocker],
        "setup_flow_reason_code": setup_reason,
        "setup_flow_reason_label": setup_reason_labels[setup_reason],
        "setup_flow_provenance": setup_provenance,
        "setup_flow_provenance_label": setup_provenance_labels[setup_provenance],
        "setup_flow_state_schema_version": SETUP_FLOW_READINESS_STATE_SCHEMA_VERSION,
        "setup_flow_config_schema_version": SETUP_FLOW_READINESS_CONFIG_SCHEMA_VERSION,
        "setup_flow_config_state": path_state.provider_path_config_state,
        "setup_flow_config_label": "Setup flow config: safe default local-only",
        "setup_flow_config_migration": SETUP_FLOW_READINESS_CONFIG_MIGRATION_POSTURE,
        "setup_flow_config_valid": path_state.provider_path_config_valid,
        "setup_flow_approval_status": setup_approval,
        "setup_flow_approval_label": {
            SETUP_FLOW_APPROVAL_STATUS_MISSING: "Setup flow approval: USER approval missing",
            SETUP_FLOW_APPROVAL_STATUS_FUTURE_GATED: "Setup flow approval: future-gated",
            SETUP_FLOW_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF:
                "Setup flow approval: ready for future proof",
        }[setup_approval],
        "provider_setup_handoff_posture": PROVIDER_SETUP_HANDOFF_FUTURE_GATED,
        "provider_setup_handoff_label": "Provider setup handoff: future-gated",
        "provider_consent_handoff_posture": PROVIDER_CONSENT_HANDOFF_FUTURE_GATED,
        "provider_consent_handoff_label": "Provider consent handoff: future-gated",
        "provider_path_handoff_posture": PROVIDER_PATH_HANDOFF_FUTURE_GATED,
        "provider_path_handoff_label": "Provider path handoff: future-gated",
        "consent_flow_readiness_state": consent_state,
        "consent_flow_readiness_label": consent_labels[consent_state],
        "consent_flow_eligibility_state": consent_eligibility,
        "consent_flow_eligibility_label": consent_eligibility_labels[consent_eligibility],
        "consent_flow_blocker_state": consent_blocker,
        "consent_flow_blocker_label": consent_blocker_labels[consent_blocker],
        "consent_flow_reason_code": consent_reason,
        "consent_flow_reason_label": consent_reason_labels[consent_reason],
        "consent_flow_provenance": consent_provenance,
        "consent_flow_provenance_label": consent_provenance_labels[consent_provenance],
        "consent_flow_state_schema_version": CONSENT_FLOW_READINESS_STATE_SCHEMA_VERSION,
        "consent_flow_config_schema_version": CONSENT_FLOW_READINESS_CONFIG_SCHEMA_VERSION,
        "consent_flow_config_state": path_state.provider_path_config_state,
        "consent_flow_config_label": "Consent flow config: safe default local-only",
        "consent_flow_config_migration": CONSENT_FLOW_READINESS_CONFIG_MIGRATION_POSTURE,
        "consent_flow_config_valid": path_state.provider_path_config_valid,
        "consent_flow_approval_status": consent_approval,
        "consent_flow_approval_label": {
            CONSENT_FLOW_APPROVAL_STATUS_MISSING: "Consent flow approval: USER approval missing",
            CONSENT_FLOW_APPROVAL_STATUS_FUTURE_GATED: "Consent flow approval: future-gated",
            CONSENT_FLOW_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF:
                "Consent flow approval: ready for future proof",
        }[consent_approval],
        "consent_collection_posture": CONSENT_COLLECTION_POSTURE_PENDING_APPROVAL,
        "consent_collection_label": "Consent collection: pending USER approval",
        "data_visibility_consent_posture": DATA_VISIBILITY_CONSENT_POSTURE_NONE_REQUIRED,
        "data_visibility_consent_label": (
            "Data visibility consent: none required while provider-visible data is none"
        ),
        "setup_flow_gate_state": setup_gate,
        "consent_flow_gate_state": consent_gate,
        "setup_approval_gate_state": setup_approval_gate,
        "execution_approval_gate_state": execution_approval_gate,
        "desktop_ai_owned_readiness_display_state": AI_PROVIDER_STATUS_DISPLAY_SUPPRESSED,
        "desktop_ai_owned_readiness_display_label": (
            "Desktop AI-owned readiness display: suppressed by default"
        ),
    }


def build_provider_setup_consent_flow_readiness_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve local-only setup and consent flow readiness without enabling setup."""

    path_state = build_provider_path_consent_readiness_state(
        readiness_config,
        activation_config=activation_config,
        execution_config=execution_config,
        path_consent_config=path_consent_config,
        surface_role=surface_role,
    )
    flow_fields = _provider_setup_consent_flow_contract_fields(path_state)
    return replace(
        path_state,
        state_id=FAM007_PROVIDER_SETUP_CONSENT_FLOW_READINESS_STATE_ID,
        mode=FAM007_PROVIDER_SETUP_CONSENT_FLOW_READINESS_MODE,
        availability=FAM007_PROVIDER_SETUP_CONSENT_FLOW_READINESS_AVAILABILITY,
        status_label="Setup and consent flow readiness unavailable",
        disabled_reason=(
            "Provider setup flow and consent collection remain disabled until later USER approval"
        ),
        provider_next_action_label="Next: setup and consent flow readiness remains local-only",
        interaction_label="Setup and consent flow readiness only",
        interaction_disabled_reason=(
            "Provider setup, consent collection, prompt routing, and model execution require later USER approval"
        ),
        **flow_fields,
    )


def _provider_setup_contract_readiness_fields(flow_state: AIProviderStateSnapshot) -> dict[str, object]:
    contract_state = SETUP_CONTRACT_STATE_UNAVAILABLE
    contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_UNAVAILABLE
    contract_blocker = SETUP_CONTRACT_BLOCKER_PROVIDER_PATH_REQUIRED
    contract_reason = SETUP_CONTRACT_REASON_DEFAULT_UNAVAILABLE
    contract_provenance = SETUP_CONTRACT_PROVENANCE_SETUP_FLOW
    contract_approval = SETUP_CONTRACT_APPROVAL_STATUS_MISSING
    contract_gate = SETUP_CONTRACT_GATE_BLOCKED
    profile_gate = PROVIDER_PROFILE_GATE_BLOCKED
    capability_gate = CAPABILITY_GATE_BLOCKED
    manifest_gate = MANIFEST_GATE_BLOCKED
    safety_gate = SAFETY_EVAL_GATE_BLOCKED

    if flow_state.provider_path_config_state == PROVIDER_PATH_CONFIG_STATE_MISSING:
        contract_state = SETUP_CONTRACT_STATE_DISABLED
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_DISABLED
        contract_reason = SETUP_CONTRACT_REASON_DEFAULT_UNAVAILABLE
        contract_provenance = SETUP_CONTRACT_PROVENANCE_PROVIDER_PATH
    elif flow_state.provider_path_config_state == PROVIDER_PATH_CONFIG_STATE_INVALID:
        contract_state = SETUP_CONTRACT_STATE_DEGRADED
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_POLICY_BLOCKED
        contract_reason = SETUP_CONTRACT_REASON_POLICY_BLOCKED
        contract_provenance = SETUP_CONTRACT_PROVENANCE_POLICY
    elif flow_state.provider_path_config_state == PROVIDER_PATH_CONFIG_STATE_DEFAULT:
        contract_state = SETUP_CONTRACT_STATE_UNAVAILABLE
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_UNAVAILABLE
        contract_blocker = SETUP_CONTRACT_BLOCKER_PROVIDER_PATH_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_DEFAULT_UNAVAILABLE
        contract_provenance = SETUP_CONTRACT_PROVENANCE_SETUP_FLOW
    elif (
        flow_state.provider_path_status == PROVIDER_PATH_STATUS_SELECTED_FUTURE_GATED
        and flow_state.provider_config_status == PROVIDER_CONFIG_ENVELOPE_STATUS_MISSING
    ):
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_CONFIG
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_CONFIG_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_CONFIG_MISSING
        contract_provenance = SETUP_CONTRACT_PROVENANCE_CONFIG
    elif flow_state.provider_config_status == PROVIDER_CONFIG_ENVELOPE_STATUS_INVALID:
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_CONFIG
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_CONFIG_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_CONFIG_INVALID
        contract_provenance = SETUP_CONTRACT_PROVENANCE_CONFIG
    elif (
        flow_state.provider_path_config_state == PROVIDER_PATH_CONFIG_STATE_LOCAL
        and not flow_state.provider_profile_available
    ):
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_CONFIG
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_CONFIG_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_PROFILE_MISSING
        contract_provenance = SETUP_CONTRACT_PROVENANCE_PROFILE
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_DISABLED:
        contract_state = SETUP_CONTRACT_STATE_DISABLED
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_DISABLED
        contract_reason = SETUP_CONTRACT_REASON_DEFAULT_UNAVAILABLE
        contract_provenance = SETUP_CONTRACT_PROVENANCE_SETUP_FLOW
    elif (
        flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_UNAVAILABLE
        and flow_state.provider_path_config_state != PROVIDER_PATH_CONFIG_STATE_DEFAULT
    ):
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_PROVIDER_PATH
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_reason = SETUP_CONTRACT_REASON_PROVIDER_PATH_REQUIRED
        contract_provenance = SETUP_CONTRACT_PROVENANCE_PROVIDER_PATH
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_DEGRADED:
        contract_state = SETUP_CONTRACT_STATE_DEGRADED
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_POLICY_BLOCKED
        contract_reason = SETUP_CONTRACT_REASON_POLICY_BLOCKED
        contract_provenance = SETUP_CONTRACT_PROVENANCE_POLICY
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_BLOCKED_BY_PROVIDER_PATH:
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_PROVIDER_PATH
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_reason = SETUP_CONTRACT_REASON_PROVIDER_PATH_REQUIRED
        contract_provenance = SETUP_CONTRACT_PROVENANCE_PROVIDER_PATH
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_BLOCKED_BY_SETUP_CONSENT:
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_SETUP_CONSENT
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_SETUP_CONSENT_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_SETUP_CONSENT_REQUIRED
        contract_provenance = SETUP_CONTRACT_PROVENANCE_CONSENT
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_BLOCKED_BY_EXECUTION_CONSENT:
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_EXECUTION_CONSENT
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_EXECUTION_CONSENT_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_EXECUTION_CONSENT_REQUIRED
        contract_provenance = SETUP_CONTRACT_PROVENANCE_CONSENT
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_BLOCKED_BY_POLICY:
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_POLICY
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_POLICY_BLOCKED
        contract_reason = SETUP_CONTRACT_REASON_POLICY_BLOCKED
        contract_provenance = SETUP_CONTRACT_PROVENANCE_POLICY
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_BLOCKED_BY_CAPABILITY:
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_CAPABILITY
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_CAPABILITY_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_CAPABILITY_MISSING
        contract_provenance = SETUP_CONTRACT_PROVENANCE_CAPABILITY
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_BLOCKED_BY_MANIFEST:
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_MANIFEST
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_MANIFEST_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_MANIFEST_MISSING
        contract_provenance = SETUP_CONTRACT_PROVENANCE_MANIFEST
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_BLOCKED_BY_SAFETY:
        contract_state = SETUP_CONTRACT_STATE_BLOCKED_BY_SAFETY
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_BLOCKED
        contract_blocker = SETUP_CONTRACT_BLOCKER_SAFETY_EVAL_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_SAFETY_BLOCKED
        contract_provenance = SETUP_CONTRACT_PROVENANCE_SAFETY
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_READY_BUT_NOT_APPROVED:
        contract_state = SETUP_CONTRACT_STATE_READY_BUT_NOT_APPROVED
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_READY_NOT_APPROVED
        contract_blocker = SETUP_CONTRACT_BLOCKER_SETUP_APPROVAL_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_SETUP_APPROVAL_MISSING
        contract_provenance = SETUP_CONTRACT_PROVENANCE_FUTURE_RUNTIME
    elif flow_state.setup_flow_readiness_state == SETUP_FLOW_STATE_READY_FOR_FUTURE_SETUP_BRANCH:
        contract_state = SETUP_CONTRACT_STATE_READY_FOR_FUTURE_SETUP_BRANCH
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_FUTURE_SETUP_BRANCH
        contract_blocker = SETUP_CONTRACT_BLOCKER_FUTURE_SETUP_BRANCH
        contract_reason = SETUP_CONTRACT_REASON_READY_FOR_FUTURE_SETUP_BRANCH
        contract_provenance = SETUP_CONTRACT_PROVENANCE_FUTURE_RUNTIME
        contract_approval = SETUP_CONTRACT_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF
        contract_gate = SETUP_CONTRACT_GATE_FUTURE_GATED
        profile_gate = PROVIDER_PROFILE_GATE_READY_FUTURE_GATED
        capability_gate = CAPABILITY_GATE_READY_FUTURE_GATED
        manifest_gate = MANIFEST_GATE_READY_FUTURE_GATED
        safety_gate = SAFETY_EVAL_GATE_READY_FUTURE_GATED
    else:
        contract_state = SETUP_CONTRACT_STATE_READY_FUTURE_GATED
        contract_eligibility = SETUP_CONTRACT_ELIGIBILITY_FUTURE_GATED
        contract_blocker = SETUP_CONTRACT_BLOCKER_SETUP_APPROVAL_REQUIRED
        contract_reason = SETUP_CONTRACT_REASON_SETUP_APPROVAL_MISSING
        contract_provenance = SETUP_CONTRACT_PROVENANCE_FUTURE_RUNTIME
        contract_approval = SETUP_CONTRACT_APPROVAL_STATUS_FUTURE_GATED
        contract_gate = SETUP_CONTRACT_GATE_FUTURE_GATED
        profile_gate = PROVIDER_PROFILE_GATE_READY_FUTURE_GATED

    if contract_state not in {
        SETUP_CONTRACT_STATE_UNAVAILABLE,
        SETUP_CONTRACT_STATE_DISABLED,
        SETUP_CONTRACT_STATE_BLOCKED_BY_PROVIDER_PATH,
        SETUP_CONTRACT_STATE_BLOCKED_BY_CONFIG,
        SETUP_CONTRACT_STATE_DEGRADED,
    }:
        profile_gate = PROVIDER_PROFILE_GATE_READY_FUTURE_GATED
    if contract_state in {
        SETUP_CONTRACT_STATE_BLOCKED_BY_MANIFEST,
        SETUP_CONTRACT_STATE_BLOCKED_BY_SAFETY,
        SETUP_CONTRACT_STATE_BLOCKED_BY_POLICY,
        SETUP_CONTRACT_STATE_READY_BUT_NOT_APPROVED,
        SETUP_CONTRACT_STATE_READY_FUTURE_GATED,
        SETUP_CONTRACT_STATE_READY_FOR_FUTURE_SETUP_BRANCH,
    }:
        capability_gate = CAPABILITY_GATE_READY_FUTURE_GATED
    if contract_state in {
        SETUP_CONTRACT_STATE_BLOCKED_BY_SAFETY,
        SETUP_CONTRACT_STATE_BLOCKED_BY_POLICY,
        SETUP_CONTRACT_STATE_READY_BUT_NOT_APPROVED,
        SETUP_CONTRACT_STATE_READY_FUTURE_GATED,
        SETUP_CONTRACT_STATE_READY_FOR_FUTURE_SETUP_BRANCH,
    }:
        manifest_gate = MANIFEST_GATE_READY_FUTURE_GATED
    if contract_state in {
        SETUP_CONTRACT_STATE_BLOCKED_BY_POLICY,
        SETUP_CONTRACT_STATE_READY_BUT_NOT_APPROVED,
        SETUP_CONTRACT_STATE_READY_FUTURE_GATED,
        SETUP_CONTRACT_STATE_READY_FOR_FUTURE_SETUP_BRANCH,
    }:
        safety_gate = SAFETY_EVAL_GATE_READY_FUTURE_GATED

    contract_labels = {
        SETUP_CONTRACT_STATE_UNAVAILABLE: "Setup contract readiness: unavailable",
        SETUP_CONTRACT_STATE_DISABLED: "Setup contract readiness: disabled",
        SETUP_CONTRACT_STATE_BLOCKED_BY_PROVIDER_PATH:
            "Setup contract readiness: blocked by provider path",
        SETUP_CONTRACT_STATE_BLOCKED_BY_CONFIG: "Setup contract readiness: blocked by config/profile",
        SETUP_CONTRACT_STATE_BLOCKED_BY_SETUP_CONSENT:
            "Setup contract readiness: blocked by setup consent",
        SETUP_CONTRACT_STATE_BLOCKED_BY_EXECUTION_CONSENT:
            "Setup contract readiness: blocked by execution consent",
        SETUP_CONTRACT_STATE_BLOCKED_BY_POLICY: "Setup contract readiness: blocked by policy",
        SETUP_CONTRACT_STATE_BLOCKED_BY_CAPABILITY:
            "Setup contract readiness: blocked by capability",
        SETUP_CONTRACT_STATE_BLOCKED_BY_MANIFEST: "Setup contract readiness: blocked by manifest",
        SETUP_CONTRACT_STATE_BLOCKED_BY_SAFETY: "Setup contract readiness: blocked by safety/eval",
        SETUP_CONTRACT_STATE_READY_FUTURE_GATED:
            "Setup contract readiness: ready but future-gated",
        SETUP_CONTRACT_STATE_READY_BUT_NOT_APPROVED:
            "Setup contract readiness: ready but USER approval missing",
        SETUP_CONTRACT_STATE_DEGRADED: "Setup contract readiness: degraded and fail-closed",
        SETUP_CONTRACT_STATE_READY_FOR_FUTURE_SETUP_BRANCH:
            "Setup contract readiness: ready for future setup branch",
    }
    eligibility_labels = {
        SETUP_CONTRACT_ELIGIBILITY_UNAVAILABLE: "Setup contract eligibility: unavailable",
        SETUP_CONTRACT_ELIGIBILITY_DISABLED: "Setup contract eligibility: disabled",
        SETUP_CONTRACT_ELIGIBILITY_BLOCKED: "Setup contract eligibility: blocked",
        SETUP_CONTRACT_ELIGIBILITY_FUTURE_GATED: "Setup contract eligibility: future-gated",
        SETUP_CONTRACT_ELIGIBILITY_READY_NOT_APPROVED:
            "Setup contract eligibility: ready but USER approval missing",
        SETUP_CONTRACT_ELIGIBILITY_FUTURE_SETUP_BRANCH:
            "Setup contract eligibility: future setup branch",
    }
    blocker_labels = {
        SETUP_CONTRACT_BLOCKER_PROVIDER_PATH_REQUIRED:
            "Setup contract blocker: provider path readiness required",
        SETUP_CONTRACT_BLOCKER_CONFIG_REQUIRED:
            "Setup contract blocker: provider profile/config proof required",
        SETUP_CONTRACT_BLOCKER_SETUP_CONSENT_REQUIRED:
            "Setup contract blocker: setup consent required",
        SETUP_CONTRACT_BLOCKER_EXECUTION_CONSENT_REQUIRED:
            "Setup contract blocker: execution consent required",
        SETUP_CONTRACT_BLOCKER_POLICY_BLOCKED: "Setup contract blocker: policy blocked",
        SETUP_CONTRACT_BLOCKER_CAPABILITY_REQUIRED:
            "Setup contract blocker: capability proof required",
        SETUP_CONTRACT_BLOCKER_MANIFEST_REQUIRED:
            "Setup contract blocker: manifest proof required",
        SETUP_CONTRACT_BLOCKER_SAFETY_EVAL_REQUIRED:
            "Setup contract blocker: safety/eval proof required",
        SETUP_CONTRACT_BLOCKER_SETUP_APPROVAL_REQUIRED:
            "Setup contract blocker: USER setup approval required",
        SETUP_CONTRACT_BLOCKER_FUTURE_SETUP_BRANCH:
            "Setup contract blocker: future setup branch required",
    }
    reason_labels = {
        SETUP_CONTRACT_REASON_DEFAULT_UNAVAILABLE:
            "Setup contract reason: setup contract is local-only",
        SETUP_CONTRACT_REASON_PROVIDER_PATH_REQUIRED:
            "Setup contract reason: provider path readiness required",
        SETUP_CONTRACT_REASON_CONFIG_MISSING:
            "Setup contract reason: provider config proof missing",
        SETUP_CONTRACT_REASON_CONFIG_INVALID:
            "Setup contract reason: provider config proof invalid",
        SETUP_CONTRACT_REASON_PROFILE_MISSING:
            "Setup contract reason: provider profile proof missing",
        SETUP_CONTRACT_REASON_SETUP_CONSENT_REQUIRED:
            "Setup contract reason: setup consent required",
        SETUP_CONTRACT_REASON_EXECUTION_CONSENT_REQUIRED:
            "Setup contract reason: execution consent required",
        SETUP_CONTRACT_REASON_POLICY_BLOCKED: "Setup contract reason: policy blocked",
        SETUP_CONTRACT_REASON_CAPABILITY_MISSING:
            "Setup contract reason: capability proof missing",
        SETUP_CONTRACT_REASON_MANIFEST_MISSING:
            "Setup contract reason: manifest proof missing",
        SETUP_CONTRACT_REASON_SAFETY_BLOCKED:
            "Setup contract reason: safety/eval blocked",
        SETUP_CONTRACT_REASON_SETUP_APPROVAL_MISSING:
            "Setup contract reason: USER setup approval missing",
        SETUP_CONTRACT_REASON_READY_FOR_FUTURE_SETUP_BRANCH:
            "Setup contract reason: ready for future setup branch",
    }
    provenance_labels = {
        SETUP_CONTRACT_PROVENANCE_SETUP_FLOW:
            "Setup contract provenance: setup flow readiness state",
        SETUP_CONTRACT_PROVENANCE_PROVIDER_PATH:
            "Setup contract provenance: provider path readiness state",
        SETUP_CONTRACT_PROVENANCE_CONFIG:
            "Setup contract provenance: provider config envelope",
        SETUP_CONTRACT_PROVENANCE_PROFILE:
            "Setup contract provenance: provider profile metadata",
        SETUP_CONTRACT_PROVENANCE_CONSENT:
            "Setup contract provenance: setup/execution consent prerequisites",
        SETUP_CONTRACT_PROVENANCE_CAPABILITY:
            "Setup contract provenance: capability contract",
        SETUP_CONTRACT_PROVENANCE_MANIFEST:
            "Setup contract provenance: manifest state",
        SETUP_CONTRACT_PROVENANCE_SAFETY: "Setup contract provenance: safety/eval",
        SETUP_CONTRACT_PROVENANCE_POLICY: "Setup contract provenance: audit policy",
        SETUP_CONTRACT_PROVENANCE_FUTURE_RUNTIME:
            "Setup contract provenance: future setup contract check",
    }
    return {
        "provider_setup_contract_readiness_state": contract_state,
        "provider_setup_contract_readiness_label": contract_labels[contract_state],
        "provider_setup_contract_eligibility_state": contract_eligibility,
        "provider_setup_contract_eligibility_label": eligibility_labels[contract_eligibility],
        "provider_setup_contract_blocker_state": contract_blocker,
        "provider_setup_contract_blocker_label": blocker_labels[contract_blocker],
        "provider_setup_contract_reason_code": contract_reason,
        "provider_setup_contract_reason_label": reason_labels[contract_reason],
        "provider_setup_contract_provenance": contract_provenance,
        "provider_setup_contract_provenance_label": provenance_labels[contract_provenance],
        "provider_setup_contract_state_schema_version": SETUP_CONTRACT_READINESS_STATE_SCHEMA_VERSION,
        "provider_setup_contract_config_schema_version": SETUP_CONTRACT_READINESS_CONFIG_SCHEMA_VERSION,
        "provider_setup_contract_config_state": flow_state.provider_path_config_state,
        "provider_setup_contract_config_label": "Setup contract config: safe default local-only",
        "provider_setup_contract_config_migration": SETUP_CONTRACT_READINESS_CONFIG_MIGRATION_POSTURE,
        "provider_setup_contract_config_valid": flow_state.provider_path_config_valid,
        "provider_setup_contract_approval_status": contract_approval,
        "provider_setup_contract_approval_label": {
            SETUP_CONTRACT_APPROVAL_STATUS_MISSING:
                "Setup contract approval: USER approval missing",
            SETUP_CONTRACT_APPROVAL_STATUS_FUTURE_GATED:
                "Setup contract approval: future-gated",
            SETUP_CONTRACT_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF:
                "Setup contract approval: ready for future proof",
        }[contract_approval],
        "provider_setup_contract_gate_state": contract_gate,
        "provider_profile_gate_state": profile_gate,
        "capability_gate_state": capability_gate,
        "manifest_gate_state": manifest_gate,
        "safety_eval_gate_state": safety_gate,
        "network_gate_state": NETWORK_GATE_BLOCKED,
        "memory_indexing_gate_state": MEMORY_INDEXING_GATE_BLOCKED,
        "voice_core_sync_gate_state": VOICE_CORE_SYNC_GATE_BLOCKED,
        "version_jump_gate_state": VERSION_JUMP_GATE_PENDING,
        "provider_setup_prerequisite_posture": PROVIDER_SETUP_PREREQUISITE_POSTURE_LOCAL_ONLY,
        "provider_setup_validation_posture": PROVIDER_SETUP_VALIDATION_POSTURE_STATIC,
        "provider_setup_ui_proof_posture": PROVIDER_SETUP_UI_PROOF_POSTURE_STATUS_ONLY,
        "future_setup_branch_handoff_state": FUTURE_SETUP_BRANCH_HANDOFF_READY,
        "provider_setup_contract_fold_down_posture": PROVIDER_SETUP_CONTRACT_FOLD_DOWN_READY,
    }


def build_provider_setup_contract_readiness_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve local-only setup contract readiness without enabling provider setup."""

    flow_state = build_provider_setup_consent_flow_readiness_state(
        readiness_config,
        activation_config=activation_config,
        execution_config=execution_config,
        path_consent_config=path_consent_config,
        surface_role=surface_role,
    )
    contract_fields = _provider_setup_contract_readiness_fields(flow_state)
    return replace(
        flow_state,
        state_id=FAM007_PROVIDER_SETUP_CONTRACT_READINESS_STATE_ID,
        mode=FAM007_PROVIDER_SETUP_CONTRACT_READINESS_MODE,
        availability=FAM007_PROVIDER_SETUP_CONTRACT_READINESS_AVAILABILITY,
        status_label="Provider setup contract readiness unavailable",
        disabled_reason=(
            "Provider setup contract is status-only; setup execution remains pending USER approval"
        ),
        provider_next_action_label="Next: provider setup contract readiness remains local-only",
        interaction_label="Provider setup contract readiness only",
        interaction_disabled_reason=(
            "Provider setup, consent collection, prompt routing, and model execution require later USER approval"
        ),
        **contract_fields,
    )


def _provider_selection_options() -> tuple[AIProviderChoiceSnapshot, ...]:
    return (
        AIProviderChoiceSnapshot(
            provider_id=NO_PROVIDER_ID,
            label="No provider fallback",
            provider_kind="none",
            availability="disabled",
            consent_state="not-required",
            privacy_scope=NO_PROVIDER_PRIVACY_SCOPE,
            visible_status="Active fallback",
            configuration_state=PROVIDER_CONFIGURATION_FALLBACK_ACTIVE,
            configured=False,
            requires_consent=False,
            provider_visible_data="none",
            external_calls="blocked",
        ),
        AIProviderChoiceSnapshot(
            provider_id="local-capability-pack",
            label="Local capability pack",
            provider_kind="local",
            availability=PROVIDER_SELECTION_AVAILABILITY,
            consent_state=PROVIDER_CONSENT_REQUIRED,
            privacy_scope=NO_PROVIDER_PRIVACY_SCOPE,
            visible_status="Unavailable until installed and approved",
            configuration_state=PROVIDER_CONFIGURATION_UNCONFIGURED,
            configured=False,
            requires_consent=True,
            provider_visible_data="none",
            external_calls="blocked",
        ),
        AIProviderChoiceSnapshot(
            provider_id="external-provider",
            label="External provider",
            provider_kind="external",
            availability=PROVIDER_SELECTION_AVAILABILITY,
            consent_state=PROVIDER_CONSENT_REQUIRED,
            privacy_scope="external-disabled",
            visible_status="Unavailable until configured and approved",
            configuration_state=PROVIDER_CONFIGURATION_UNCONFIGURED,
            configured=False,
            requires_consent=True,
            provider_visible_data="none",
            external_calls="blocked",
        ),
    )


def build_default_provider_runtime_config() -> AIProviderRuntimeConfigSnapshot:
    """Return the safe local-only default provider runtime config."""

    return AIProviderRuntimeConfigSnapshot(
        schema_version=PROVIDER_RUNTIME_CONFIG_SCHEMA_VERSION,
        config_state=PROVIDER_RUNTIME_CONFIG_STATE_DEFAULT,
        selected_provider_id=NO_PROVIDER_ID,
        provider_configured=False,
        provider_available=False,
        consent_granted=False,
        capability_ready=False,
        config_valid=True,
        provenance=PROVIDER_RUNTIME_PROVENANCE_DEFAULT_CONFIG,
    )


def normalize_provider_runtime_config(
    config: AIProviderRuntimeConfigSnapshot | dict[str, object] | None,
) -> AIProviderRuntimeConfigSnapshot:
    """Normalize local config into a fail-closed provider runtime contract input."""

    if config is None:
        return AIProviderRuntimeConfigSnapshot(
            schema_version=PROVIDER_RUNTIME_CONFIG_SCHEMA_VERSION,
            config_state=PROVIDER_RUNTIME_CONFIG_STATE_MISSING,
            selected_provider_id=NO_PROVIDER_ID,
            provider_configured=False,
            provider_available=False,
            consent_granted=False,
            capability_ready=False,
            config_valid=False,
            provenance=PROVIDER_RUNTIME_PROVENANCE_DEFAULT_CONFIG,
        )

    if isinstance(config, AIProviderRuntimeConfigSnapshot):
        if config.schema_version == PROVIDER_RUNTIME_CONFIG_SCHEMA_VERSION and config.config_valid:
            return config
        return replace(
            build_default_provider_runtime_config(),
            config_state=PROVIDER_RUNTIME_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=config.provenance
            if config.provenance in PROVIDER_RUNTIME_PROVENANCE_SOURCES
            else PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG,
        )

    if not isinstance(config, dict):
        return replace(
            build_default_provider_runtime_config(),
            config_state=PROVIDER_RUNTIME_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG,
        )

    schema_version = str(config.get("schema_version") or "")
    selected_provider_id = str(config.get("selected_provider_id") or NO_PROVIDER_ID)
    provenance = str(config.get("provenance") or PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG)
    valid_provider_ids = {option.provider_id for option in _provider_selection_options()}
    config_valid = (
        bool(config.get("config_valid", True))
        and schema_version == PROVIDER_RUNTIME_CONFIG_SCHEMA_VERSION
        and selected_provider_id in valid_provider_ids
    )
    if not config_valid:
        return replace(
            build_default_provider_runtime_config(),
            config_state=PROVIDER_RUNTIME_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=provenance
            if provenance in PROVIDER_RUNTIME_PROVENANCE_SOURCES
            else PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG,
        )

    return AIProviderRuntimeConfigSnapshot(
        schema_version=schema_version,
        config_state=PROVIDER_RUNTIME_CONFIG_STATE_LOCAL,
        selected_provider_id=selected_provider_id,
        provider_configured=bool(config.get("provider_configured", False)),
        provider_available=bool(config.get("provider_available", False)),
        consent_granted=bool(config.get("consent_granted", False)),
        capability_ready=bool(config.get("capability_ready", False)),
        config_valid=True,
        provenance=provenance if provenance in PROVIDER_RUNTIME_PROVENANCE_SOURCES else PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG,
    )


def build_default_provider_readiness_config() -> AIProviderReadinessConfigSnapshot:
    """Return the safe local-only default provider readiness config."""

    return AIProviderReadinessConfigSnapshot(
        schema_version=PROVIDER_READINESS_CONFIG_SCHEMA_VERSION,
        config_state=PROVIDER_READINESS_CONFIG_STATE_DEFAULT,
        provider_configured=False,
        consent_granted=False,
        capability_ready=False,
        manifest_available=False,
        manifest_valid=False,
        policy_allows_setup=True,
        future_provider_setup_approved=False,
        provider_ready=False,
        install_intent_requested=False,
        config_valid=True,
        provenance=PROVIDER_READINESS_PROVENANCE_DEFAULT_CONFIG,
    )


def normalize_provider_readiness_config(
    config: AIProviderReadinessConfigSnapshot | dict[str, object] | None,
) -> AIProviderReadinessConfigSnapshot:
    """Normalize readiness config into a fail-closed local-only setup posture."""

    if config is None:
        return replace(
            build_default_provider_readiness_config(),
            config_state=PROVIDER_READINESS_CONFIG_STATE_MISSING,
            config_valid=False,
        )

    if isinstance(config, AIProviderReadinessConfigSnapshot):
        if config.schema_version == PROVIDER_READINESS_CONFIG_SCHEMA_VERSION and config.config_valid:
            return config
        return replace(
            build_default_provider_readiness_config(),
            config_state=PROVIDER_READINESS_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=config.provenance
            if config.provenance in PROVIDER_READINESS_PROVENANCE_SOURCES
            else PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG,
        )

    if not isinstance(config, dict):
        return replace(
            build_default_provider_readiness_config(),
            config_state=PROVIDER_READINESS_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG,
        )

    provenance = str(config.get("provenance") or PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG)
    schema_version = str(config.get("schema_version") or "")
    config_valid = bool(config.get("config_valid", True)) and schema_version == PROVIDER_READINESS_CONFIG_SCHEMA_VERSION
    if not config_valid:
        return replace(
            build_default_provider_readiness_config(),
            config_state=PROVIDER_READINESS_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=provenance
            if provenance in PROVIDER_READINESS_PROVENANCE_SOURCES
            else PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG,
        )

    return AIProviderReadinessConfigSnapshot(
        schema_version=schema_version,
        config_state=PROVIDER_READINESS_CONFIG_STATE_LOCAL,
        provider_configured=bool(config.get("provider_configured", False)),
        consent_granted=bool(config.get("consent_granted", False)),
        capability_ready=bool(config.get("capability_ready", False)),
        manifest_available=bool(config.get("manifest_available", False)),
        manifest_valid=bool(config.get("manifest_valid", False)),
        policy_allows_setup=bool(config.get("policy_allows_setup", True)),
        future_provider_setup_approved=bool(config.get("future_provider_setup_approved", False)),
        provider_ready=bool(config.get("provider_ready", False)),
        install_intent_requested=bool(config.get("install_intent_requested", False)),
        config_valid=True,
        provenance=provenance
        if provenance in PROVIDER_READINESS_PROVENANCE_SOURCES
        else PROVIDER_READINESS_PROVENANCE_LOCAL_CONFIG,
    )


def build_default_provider_activation_config() -> AIProviderActivationConfigSnapshot:
    """Return the safe local-only default provider activation config."""

    return AIProviderActivationConfigSnapshot(
        schema_version=PROVIDER_ACTIVATION_CONFIG_SCHEMA_VERSION,
        config_state=PROVIDER_ACTIVATION_CONFIG_STATE_DEFAULT,
        future_activation_approved=False,
        adapter_available=False,
        safety_eval_complete=False,
        prompt_execution_approved=False,
        model_execution_approved=False,
        functional_ai_ready=False,
        config_valid=True,
        provenance=PROVIDER_ACTIVATION_PROVENANCE_DEFAULT_CONFIG,
    )


def normalize_provider_activation_config(
    config: AIProviderActivationConfigSnapshot | dict[str, object] | None,
) -> AIProviderActivationConfigSnapshot:
    """Normalize activation config into a fail-closed local-only activation posture."""

    if config is None:
        return replace(
            build_default_provider_activation_config(),
            config_state=PROVIDER_ACTIVATION_CONFIG_STATE_MISSING,
            config_valid=False,
        )

    if isinstance(config, AIProviderActivationConfigSnapshot):
        if config.schema_version == PROVIDER_ACTIVATION_CONFIG_SCHEMA_VERSION and config.config_valid:
            return config
        return replace(
            build_default_provider_activation_config(),
            config_state=PROVIDER_ACTIVATION_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=config.provenance
            if config.provenance in PROVIDER_ACTIVATION_PROVENANCE_SOURCES
            else PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG,
        )

    if not isinstance(config, dict):
        return replace(
            build_default_provider_activation_config(),
            config_state=PROVIDER_ACTIVATION_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG,
        )

    schema_version = str(config.get("schema_version") or "")
    provenance = str(config.get("provenance") or PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG)
    config_valid = bool(config.get("config_valid", True)) and schema_version == PROVIDER_ACTIVATION_CONFIG_SCHEMA_VERSION
    if not config_valid:
        return replace(
            build_default_provider_activation_config(),
            config_state=PROVIDER_ACTIVATION_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=provenance
            if provenance in PROVIDER_ACTIVATION_PROVENANCE_SOURCES
            else PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG,
        )

    return AIProviderActivationConfigSnapshot(
        schema_version=schema_version,
        config_state=PROVIDER_ACTIVATION_CONFIG_STATE_LOCAL,
        future_activation_approved=bool(config.get("future_activation_approved", False)),
        adapter_available=bool(config.get("adapter_available", False)),
        safety_eval_complete=bool(config.get("safety_eval_complete", False)),
        prompt_execution_approved=bool(config.get("prompt_execution_approved", False)),
        model_execution_approved=bool(config.get("model_execution_approved", False)),
        functional_ai_ready=bool(config.get("functional_ai_ready", False)),
        config_valid=True,
        provenance=provenance
        if provenance in PROVIDER_ACTIVATION_PROVENANCE_SOURCES
        else PROVIDER_ACTIVATION_PROVENANCE_LOCAL_CONFIG,
    )


def build_default_provider_execution_readiness_config() -> AIProviderExecutionReadinessConfigSnapshot:
    """Return the safe local-only default execution-readiness config."""

    return AIProviderExecutionReadinessConfigSnapshot(
        schema_version=PROVIDER_EXECUTION_READINESS_CONFIG_SCHEMA_VERSION,
        config_state=PROVIDER_EXECUTION_CONFIG_STATE_DEFAULT,
        provider_path_selected=False,
        provider_adapter_selected=False,
        prompt_acceptance_approved=False,
        prompt_routing_approved=False,
        model_execution_approved=False,
        provider_visible_data_approved=False,
        network_external_approved=False,
        consent_granted=False,
        safety_eval_complete=False,
        policy_allows_execution=True,
        execution_approved=False,
        functional_ai_release_ready=False,
        config_valid=True,
        provenance=PROVIDER_EXECUTION_PROVENANCE_DEFAULT_CONFIG,
    )


def normalize_provider_execution_readiness_config(
    config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None,
) -> AIProviderExecutionReadinessConfigSnapshot:
    """Normalize execution-readiness config into a fail-closed local-only posture."""

    if config is None:
        return replace(
            build_default_provider_execution_readiness_config(),
            config_state=PROVIDER_EXECUTION_CONFIG_STATE_MISSING,
            config_valid=False,
        )

    if isinstance(config, AIProviderExecutionReadinessConfigSnapshot):
        if config.schema_version == PROVIDER_EXECUTION_READINESS_CONFIG_SCHEMA_VERSION and config.config_valid:
            return config
        return replace(
            build_default_provider_execution_readiness_config(),
            config_state=PROVIDER_EXECUTION_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=config.provenance
            if config.provenance in PROVIDER_EXECUTION_PROVENANCE_SOURCES
            else PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG,
        )

    if not isinstance(config, dict):
        return replace(
            build_default_provider_execution_readiness_config(),
            config_state=PROVIDER_EXECUTION_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG,
        )

    schema_version = str(config.get("schema_version") or "")
    provenance = str(config.get("provenance") or PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG)
    config_valid = (
        bool(config.get("config_valid", True))
        and schema_version == PROVIDER_EXECUTION_READINESS_CONFIG_SCHEMA_VERSION
    )
    if not config_valid:
        return replace(
            build_default_provider_execution_readiness_config(),
            config_state=PROVIDER_EXECUTION_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=provenance
            if provenance in PROVIDER_EXECUTION_PROVENANCE_SOURCES
            else PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG,
        )

    return AIProviderExecutionReadinessConfigSnapshot(
        schema_version=schema_version,
        config_state=PROVIDER_EXECUTION_CONFIG_STATE_LOCAL,
        provider_path_selected=bool(config.get("provider_path_selected", False)),
        provider_adapter_selected=bool(config.get("provider_adapter_selected", False)),
        prompt_acceptance_approved=bool(config.get("prompt_acceptance_approved", False)),
        prompt_routing_approved=bool(config.get("prompt_routing_approved", False)),
        model_execution_approved=bool(config.get("model_execution_approved", False)),
        provider_visible_data_approved=bool(config.get("provider_visible_data_approved", False)),
        network_external_approved=bool(config.get("network_external_approved", False)),
        consent_granted=bool(config.get("consent_granted", False)),
        safety_eval_complete=bool(config.get("safety_eval_complete", False)),
        policy_allows_execution=bool(config.get("policy_allows_execution", True)),
        execution_approved=bool(config.get("execution_approved", False)),
        functional_ai_release_ready=bool(config.get("functional_ai_release_ready", False)),
        config_valid=True,
        provenance=provenance
        if provenance in PROVIDER_EXECUTION_PROVENANCE_SOURCES
        else PROVIDER_EXECUTION_PROVENANCE_LOCAL_CONFIG,
    )


def build_default_provider_path_consent_readiness_config() -> AIProviderPathConsentReadinessConfigSnapshot:
    """Return the safe local-only default provider-path/consent readiness config."""

    return AIProviderPathConsentReadinessConfigSnapshot(
        schema_version=PROVIDER_PATH_READINESS_CONFIG_SCHEMA_VERSION,
        config_state=PROVIDER_PATH_CONFIG_STATE_DEFAULT,
        provider_path_selected=False,
        provider_config_present=False,
        provider_config_valid=True,
        provider_profile_available=False,
        provider_available=False,
        setup_consent_ready=False,
        execution_consent_ready=False,
        data_visibility_approved=False,
        audit_ready=False,
        capability_ready=False,
        manifest_available=False,
        manifest_valid=False,
        safety_eval_complete=False,
        policy_allows_provider_path=True,
        setup_approved=False,
        execution_approved=False,
        future_execution_branch_ready=False,
        functional_ai_release_ready=False,
        config_valid=True,
        provenance=PROVIDER_PATH_PROVENANCE_DEFAULT_CONFIG,
    )


def normalize_provider_path_consent_readiness_config(
    config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None,
) -> AIProviderPathConsentReadinessConfigSnapshot:
    """Normalize provider-path/consent readiness config into a fail-closed local-only posture."""

    if config is None:
        return replace(
            build_default_provider_path_consent_readiness_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_MISSING,
            config_valid=False,
        )

    if isinstance(config, AIProviderPathConsentReadinessConfigSnapshot):
        if config.schema_version == PROVIDER_PATH_READINESS_CONFIG_SCHEMA_VERSION and config.config_valid:
            return config
        return replace(
            build_default_provider_path_consent_readiness_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=config.provenance
            if config.provenance in PROVIDER_PATH_PROVENANCE_SOURCES
            else PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG,
        )

    if not isinstance(config, dict):
        return replace(
            build_default_provider_path_consent_readiness_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG,
        )

    schema_version = str(config.get("schema_version") or "")
    provenance = str(config.get("provenance") or PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG)
    config_valid = bool(config.get("config_valid", True)) and schema_version == PROVIDER_PATH_READINESS_CONFIG_SCHEMA_VERSION
    if not config_valid:
        return replace(
            build_default_provider_path_consent_readiness_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=provenance
            if provenance in PROVIDER_PATH_PROVENANCE_SOURCES
            else PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG,
        )

    return AIProviderPathConsentReadinessConfigSnapshot(
        schema_version=schema_version,
        config_state=PROVIDER_PATH_CONFIG_STATE_LOCAL,
        provider_path_selected=bool(config.get("provider_path_selected", False)),
        provider_config_present=bool(config.get("provider_config_present", False)),
        provider_config_valid=bool(config.get("provider_config_valid", True)),
        provider_profile_available=bool(config.get("provider_profile_available", False)),
        provider_available=bool(config.get("provider_available", False)),
        setup_consent_ready=bool(config.get("setup_consent_ready", False)),
        execution_consent_ready=bool(config.get("execution_consent_ready", False)),
        data_visibility_approved=bool(config.get("data_visibility_approved", False)),
        audit_ready=bool(config.get("audit_ready", False)),
        capability_ready=bool(config.get("capability_ready", False)),
        manifest_available=bool(config.get("manifest_available", False)),
        manifest_valid=bool(config.get("manifest_valid", False)),
        safety_eval_complete=bool(config.get("safety_eval_complete", False)),
        policy_allows_provider_path=bool(config.get("policy_allows_provider_path", True)),
        setup_approved=bool(config.get("setup_approved", False)),
        execution_approved=bool(config.get("execution_approved", False)),
        future_execution_branch_ready=bool(config.get("future_execution_branch_ready", False)),
        functional_ai_release_ready=bool(config.get("functional_ai_release_ready", False)),
        config_valid=True,
        provenance=provenance
        if provenance in PROVIDER_PATH_PROVENANCE_SOURCES
        else PROVIDER_PATH_PROVENANCE_LOCAL_CONFIG,
    )


def build_default_provider_setup_foundation_config() -> AIProviderSetupFoundationConfigSnapshot:
    """Return the safe local-only default provider setup foundation config."""

    return AIProviderSetupFoundationConfigSnapshot(
        schema_version=SETUP_FOUNDATION_CONFIG_SCHEMA_VERSION,
        config_state=PROVIDER_PATH_CONFIG_STATE_DEFAULT,
        setup_entry_enabled=False,
        provider_profile_draft_present=False,
        provider_profile_draft_valid=False,
        provider_config_draft_present=False,
        provider_config_draft_valid=False,
        local_persistence_ready=False,
        validation_passed=False,
        setup_foundation_approved=False,
        setup_consent_ready=False,
        execution_consent_ready=False,
        config_valid=True,
        provenance=SETUP_FOUNDATION_PROVENANCE_SETUP_CONTRACT,
    )


def normalize_provider_setup_foundation_config(
    config: AIProviderSetupFoundationConfigSnapshot | dict[str, object] | None,
) -> AIProviderSetupFoundationConfigSnapshot:
    """Normalize setup foundation config into a fail-closed local-only posture."""

    provenance_sources = {
        SETUP_FOUNDATION_PROVENANCE_SETUP_CONTRACT,
        SETUP_FOUNDATION_PROVENANCE_PROFILE_DRAFT,
        SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT,
        SETUP_FOUNDATION_PROVENANCE_VALIDATION,
        SETUP_FOUNDATION_PROVENANCE_CONSENT,
        SETUP_FOUNDATION_PROVENANCE_APPROVAL,
        SETUP_FOUNDATION_PROVENANCE_FUTURE_RUNTIME,
    }

    if config is None:
        return replace(
            build_default_provider_setup_foundation_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_MISSING,
            config_valid=False,
            provenance=SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT,
        )

    if isinstance(config, AIProviderSetupFoundationConfigSnapshot):
        if config.schema_version == SETUP_FOUNDATION_CONFIG_SCHEMA_VERSION and config.config_valid:
            return config
        return replace(
            build_default_provider_setup_foundation_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=config.provenance
            if config.provenance in provenance_sources
            else SETUP_FOUNDATION_PROVENANCE_VALIDATION,
        )

    if not isinstance(config, dict):
        return replace(
            build_default_provider_setup_foundation_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=SETUP_FOUNDATION_PROVENANCE_VALIDATION,
        )

    schema_version = str(config.get("schema_version") or "")
    provenance = str(config.get("provenance") or SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT)
    config_valid = bool(config.get("config_valid", True)) and schema_version == SETUP_FOUNDATION_CONFIG_SCHEMA_VERSION
    if not config_valid:
        return replace(
            build_default_provider_setup_foundation_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=provenance
            if provenance in provenance_sources
            else SETUP_FOUNDATION_PROVENANCE_VALIDATION,
        )

    return AIProviderSetupFoundationConfigSnapshot(
        schema_version=schema_version,
        config_state=PROVIDER_PATH_CONFIG_STATE_LOCAL,
        setup_entry_enabled=bool(config.get("setup_entry_enabled", False)),
        provider_profile_draft_present=bool(config.get("provider_profile_draft_present", False)),
        provider_profile_draft_valid=bool(config.get("provider_profile_draft_valid", False)),
        provider_config_draft_present=bool(config.get("provider_config_draft_present", False)),
        provider_config_draft_valid=bool(config.get("provider_config_draft_valid", False)),
        local_persistence_ready=bool(config.get("local_persistence_ready", False)),
        validation_passed=bool(config.get("validation_passed", False)),
        setup_foundation_approved=bool(config.get("setup_foundation_approved", False)),
        setup_consent_ready=bool(config.get("setup_consent_ready", False)),
        execution_consent_ready=bool(config.get("execution_consent_ready", False)),
        config_valid=True,
        provenance=provenance
        if provenance in provenance_sources
        else SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT,
    )


def _provider_setup_foundation_fields(
    contract_state: AIProviderStateSnapshot,
    setup_config: AIProviderSetupFoundationConfigSnapshot,
) -> dict[str, object]:
    foundation_state = SETUP_FOUNDATION_STATE_UNAVAILABLE
    foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_UNAVAILABLE
    foundation_blocker = SETUP_FOUNDATION_BLOCKER_SETUP_CONTRACT_REQUIRED
    foundation_reason = SETUP_FOUNDATION_REASON_DEFAULT_UNAVAILABLE
    foundation_provenance = SETUP_FOUNDATION_PROVENANCE_SETUP_CONTRACT
    foundation_approval = SETUP_FOUNDATION_APPROVAL_STATUS_MISSING
    foundation_gate = SETUP_FOUNDATION_GATE_BLOCKED

    setup_entry_state = (
        SETUP_FOUNDATION_SETUP_ENTRY_READY_LOCAL_DRAFT
        if setup_config.setup_entry_enabled
        else SETUP_FOUNDATION_SETUP_ENTRY_DISABLED
    )
    profile_draft_status = (
        SETUP_FOUNDATION_PROFILE_DRAFT_READY
        if setup_config.provider_profile_draft_present and setup_config.provider_profile_draft_valid
        else SETUP_FOUNDATION_PROFILE_DRAFT_INVALID
        if setup_config.provider_profile_draft_present
        else SETUP_FOUNDATION_PROFILE_DRAFT_MISSING
    )
    config_draft_status = (
        SETUP_FOUNDATION_CONFIG_DRAFT_READY
        if setup_config.provider_config_draft_present and setup_config.provider_config_draft_valid
        else SETUP_FOUNDATION_CONFIG_DRAFT_INVALID
        if setup_config.provider_config_draft_present
        else SETUP_FOUNDATION_CONFIG_DRAFT_MISSING
    )
    persistence_status = (
        SETUP_FOUNDATION_PERSISTENCE_LOCAL_DRAFT_ONLY
        if setup_config.local_persistence_ready
        else SETUP_FOUNDATION_PERSISTENCE_DISABLED
    )
    validation_status = (
        SETUP_FOUNDATION_VALIDATION_STATIC_READY
        if setup_config.validation_passed
        and setup_config.provider_profile_draft_present
        and setup_config.provider_profile_draft_valid
        and setup_config.provider_config_draft_present
        and setup_config.provider_config_draft_valid
        and setup_config.local_persistence_ready
        else SETUP_FOUNDATION_VALIDATION_FAIL_CLOSED
    )

    ready_contract_states = {
        SETUP_CONTRACT_STATE_READY_FUTURE_GATED,
        SETUP_CONTRACT_STATE_READY_BUT_NOT_APPROVED,
        SETUP_CONTRACT_STATE_READY_FOR_FUTURE_SETUP_BRANCH,
    }
    if setup_config.config_state == PROVIDER_PATH_CONFIG_STATE_MISSING:
        foundation_state = SETUP_FOUNDATION_STATE_DISABLED
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_DISABLED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_CONFIG_DRAFT_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_CONFIG_MISSING
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT
    elif setup_config.config_state == PROVIDER_PATH_CONFIG_STATE_INVALID:
        foundation_state = SETUP_FOUNDATION_STATE_DEGRADED
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_VALIDATION_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_CONFIG_INVALID
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_VALIDATION
    elif contract_state.provider_setup_contract_readiness_state not in ready_contract_states:
        foundation_state = SETUP_FOUNDATION_STATE_BLOCKED_BY_SETUP_CONTRACT
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_reason = SETUP_FOUNDATION_REASON_SETUP_CONTRACT_REQUIRED
    elif not setup_config.setup_entry_enabled:
        foundation_state = SETUP_FOUNDATION_STATE_DISABLED
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_DISABLED
        foundation_reason = SETUP_FOUNDATION_REASON_SETUP_ENTRY_DISABLED
    elif not setup_config.provider_profile_draft_present:
        foundation_state = SETUP_FOUNDATION_STATE_BLOCKED_BY_PROFILE
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_PROFILE_DRAFT_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_PROFILE_DRAFT_MISSING
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_PROFILE_DRAFT
    elif not setup_config.provider_profile_draft_valid:
        foundation_state = SETUP_FOUNDATION_STATE_BLOCKED_BY_VALIDATION
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_VALIDATION_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_PROFILE_DRAFT_INVALID
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_PROFILE_DRAFT
    elif not setup_config.provider_config_draft_present:
        foundation_state = SETUP_FOUNDATION_STATE_BLOCKED_BY_CONFIG
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_CONFIG_DRAFT_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_CONFIG_DRAFT_MISSING
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT
    elif not setup_config.provider_config_draft_valid:
        foundation_state = SETUP_FOUNDATION_STATE_BLOCKED_BY_VALIDATION
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_VALIDATION_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_CONFIG_DRAFT_INVALID
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT
    elif not setup_config.local_persistence_ready or not setup_config.validation_passed:
        foundation_state = SETUP_FOUNDATION_STATE_BLOCKED_BY_VALIDATION
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_VALIDATION_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_VALIDATION_FAILED
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_VALIDATION
    elif not setup_config.setup_consent_ready:
        foundation_state = SETUP_FOUNDATION_STATE_BLOCKED_BY_SETUP_CONSENT
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_SETUP_CONSENT_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_SETUP_CONSENT_REQUIRED
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_CONSENT
    elif not setup_config.execution_consent_ready:
        foundation_state = SETUP_FOUNDATION_STATE_BLOCKED_BY_EXECUTION_CONSENT
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_BLOCKED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_EXECUTION_CONSENT_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_EXECUTION_CONSENT_REQUIRED
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_CONSENT
    elif not setup_config.setup_foundation_approved:
        foundation_state = SETUP_FOUNDATION_STATE_READY_BUT_NOT_APPROVED
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_READY_NOT_APPROVED
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_APPROVAL_REQUIRED
        foundation_reason = SETUP_FOUNDATION_REASON_APPROVAL_MISSING
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_APPROVAL
        foundation_gate = SETUP_FOUNDATION_GATE_LOCAL_DRAFT
    elif contract_state.provider_setup_contract_readiness_state == SETUP_CONTRACT_STATE_READY_FOR_FUTURE_SETUP_BRANCH:
        foundation_state = SETUP_FOUNDATION_STATE_READY_FOR_FUTURE_SETUP_BRANCH
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_FUTURE_SETUP_BRANCH
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_FUTURE_SETUP_BRANCH
        foundation_reason = SETUP_FOUNDATION_REASON_READY_FOR_FUTURE_SETUP_BRANCH
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_FUTURE_RUNTIME
        foundation_approval = SETUP_FOUNDATION_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF
        foundation_gate = SETUP_FOUNDATION_GATE_FUTURE_GATED
    else:
        foundation_state = SETUP_FOUNDATION_STATE_READY_LOCAL_DRAFT
        foundation_eligibility = SETUP_FOUNDATION_ELIGIBILITY_LOCAL_DRAFT
        foundation_blocker = SETUP_FOUNDATION_BLOCKER_FUTURE_SETUP_BRANCH
        foundation_reason = SETUP_FOUNDATION_REASON_READY_LOCAL_DRAFT
        foundation_provenance = SETUP_FOUNDATION_PROVENANCE_FUTURE_RUNTIME
        foundation_approval = SETUP_FOUNDATION_APPROVAL_STATUS_FUTURE_GATED
        foundation_gate = SETUP_FOUNDATION_GATE_FUTURE_GATED

    foundation_labels = {
        SETUP_FOUNDATION_STATE_UNAVAILABLE: "Setup implementation foundation: unavailable",
        SETUP_FOUNDATION_STATE_DISABLED: "Setup implementation foundation: disabled",
        SETUP_FOUNDATION_STATE_BLOCKED_BY_SETUP_CONTRACT:
            "Setup implementation foundation: blocked by setup contract",
        SETUP_FOUNDATION_STATE_BLOCKED_BY_PROFILE:
            "Setup implementation foundation: blocked by provider profile draft",
        SETUP_FOUNDATION_STATE_BLOCKED_BY_CONFIG:
            "Setup implementation foundation: blocked by provider config draft",
        SETUP_FOUNDATION_STATE_BLOCKED_BY_VALIDATION:
            "Setup implementation foundation: validation failed closed",
        SETUP_FOUNDATION_STATE_BLOCKED_BY_SETUP_CONSENT:
            "Setup implementation foundation: blocked by setup consent",
        SETUP_FOUNDATION_STATE_BLOCKED_BY_EXECUTION_CONSENT:
            "Setup implementation foundation: blocked by execution consent",
        SETUP_FOUNDATION_STATE_READY_LOCAL_DRAFT:
            "Setup implementation foundation: local draft ready, future-gated",
        SETUP_FOUNDATION_STATE_READY_FUTURE_GATED:
            "Setup implementation foundation: ready but future-gated",
        SETUP_FOUNDATION_STATE_READY_BUT_NOT_APPROVED:
            "Setup implementation foundation: ready but USER approval missing",
        SETUP_FOUNDATION_STATE_DEGRADED:
            "Setup implementation foundation: degraded and fail-closed",
        SETUP_FOUNDATION_STATE_READY_FOR_FUTURE_SETUP_BRANCH:
            "Setup implementation foundation: ready for future setup branch",
    }
    eligibility_labels = {
        SETUP_FOUNDATION_ELIGIBILITY_UNAVAILABLE: "Setup foundation eligibility: unavailable",
        SETUP_FOUNDATION_ELIGIBILITY_DISABLED: "Setup foundation eligibility: disabled",
        SETUP_FOUNDATION_ELIGIBILITY_BLOCKED: "Setup foundation eligibility: blocked",
        SETUP_FOUNDATION_ELIGIBILITY_LOCAL_DRAFT:
            "Setup foundation eligibility: local draft only",
        SETUP_FOUNDATION_ELIGIBILITY_FUTURE_GATED:
            "Setup foundation eligibility: future-gated",
        SETUP_FOUNDATION_ELIGIBILITY_READY_NOT_APPROVED:
            "Setup foundation eligibility: ready but USER approval missing",
        SETUP_FOUNDATION_ELIGIBILITY_FUTURE_SETUP_BRANCH:
            "Setup foundation eligibility: future setup branch",
    }
    blocker_labels = {
        SETUP_FOUNDATION_BLOCKER_SETUP_CONTRACT_REQUIRED:
            "Setup foundation blocker: setup contract readiness required",
        SETUP_FOUNDATION_BLOCKER_PROFILE_DRAFT_REQUIRED:
            "Setup foundation blocker: provider profile draft required",
        SETUP_FOUNDATION_BLOCKER_CONFIG_DRAFT_REQUIRED:
            "Setup foundation blocker: provider config draft required",
        SETUP_FOUNDATION_BLOCKER_VALIDATION_REQUIRED:
            "Setup foundation blocker: local validation proof required",
        SETUP_FOUNDATION_BLOCKER_SETUP_CONSENT_REQUIRED:
            "Setup foundation blocker: setup consent prerequisite required",
        SETUP_FOUNDATION_BLOCKER_EXECUTION_CONSENT_REQUIRED:
            "Setup foundation blocker: execution consent prerequisite required",
        SETUP_FOUNDATION_BLOCKER_APPROVAL_REQUIRED:
            "Setup foundation blocker: USER setup foundation approval required",
        SETUP_FOUNDATION_BLOCKER_FUTURE_SETUP_BRANCH:
            "Setup foundation blocker: future setup branch required",
    }
    reason_labels = {
        SETUP_FOUNDATION_REASON_DEFAULT_UNAVAILABLE:
            "Setup foundation reason: local-only safe default",
        SETUP_FOUNDATION_REASON_SETUP_ENTRY_DISABLED:
            "Setup foundation reason: setup entry point disabled",
        SETUP_FOUNDATION_REASON_SETUP_CONTRACT_REQUIRED:
            "Setup foundation reason: setup contract readiness required",
        SETUP_FOUNDATION_REASON_CONFIG_MISSING:
            "Setup foundation reason: config snapshot missing",
        SETUP_FOUNDATION_REASON_CONFIG_INVALID:
            "Setup foundation reason: config snapshot invalid",
        SETUP_FOUNDATION_REASON_PROFILE_DRAFT_MISSING:
            "Setup foundation reason: provider profile draft missing",
        SETUP_FOUNDATION_REASON_PROFILE_DRAFT_INVALID:
            "Setup foundation reason: provider profile draft invalid",
        SETUP_FOUNDATION_REASON_CONFIG_DRAFT_MISSING:
            "Setup foundation reason: provider config draft missing",
        SETUP_FOUNDATION_REASON_CONFIG_DRAFT_INVALID:
            "Setup foundation reason: provider config draft invalid",
        SETUP_FOUNDATION_REASON_VALIDATION_FAILED:
            "Setup foundation reason: validation failed closed",
        SETUP_FOUNDATION_REASON_SETUP_CONSENT_REQUIRED:
            "Setup foundation reason: setup consent prerequisite required",
        SETUP_FOUNDATION_REASON_EXECUTION_CONSENT_REQUIRED:
            "Setup foundation reason: execution consent prerequisite required",
        SETUP_FOUNDATION_REASON_APPROVAL_MISSING:
            "Setup foundation reason: USER setup approval missing",
        SETUP_FOUNDATION_REASON_READY_LOCAL_DRAFT:
            "Setup foundation reason: local draft ready for future proof",
        SETUP_FOUNDATION_REASON_READY_FOR_FUTURE_SETUP_BRANCH:
            "Setup foundation reason: ready for future setup branch",
    }
    provenance_labels = {
        SETUP_FOUNDATION_PROVENANCE_SETUP_CONTRACT:
            "Setup foundation provenance: provider setup contract state",
        SETUP_FOUNDATION_PROVENANCE_PROFILE_DRAFT:
            "Setup foundation provenance: provider profile draft",
        SETUP_FOUNDATION_PROVENANCE_CONFIG_DRAFT:
            "Setup foundation provenance: provider config draft",
        SETUP_FOUNDATION_PROVENANCE_VALIDATION:
            "Setup foundation provenance: local validation proof",
        SETUP_FOUNDATION_PROVENANCE_CONSENT:
            "Setup foundation provenance: consent prerequisites",
        SETUP_FOUNDATION_PROVENANCE_APPROVAL:
            "Setup foundation provenance: future setup approval",
        SETUP_FOUNDATION_PROVENANCE_FUTURE_RUNTIME:
            "Setup foundation provenance: future provider setup check",
    }

    return {
        "provider_setup_foundation_state": foundation_state,
        "provider_setup_foundation_label": foundation_labels[foundation_state],
        "provider_setup_foundation_eligibility_state": foundation_eligibility,
        "provider_setup_foundation_eligibility_label": eligibility_labels[foundation_eligibility],
        "provider_setup_foundation_blocker_state": foundation_blocker,
        "provider_setup_foundation_blocker_label": blocker_labels[foundation_blocker],
        "provider_setup_foundation_reason_code": foundation_reason,
        "provider_setup_foundation_reason_label": reason_labels[foundation_reason],
        "provider_setup_foundation_provenance": foundation_provenance,
        "provider_setup_foundation_provenance_label": provenance_labels[foundation_provenance],
        "provider_setup_foundation_state_schema_version": SETUP_FOUNDATION_STATE_SCHEMA_VERSION,
        "provider_setup_foundation_config_schema_version": SETUP_FOUNDATION_CONFIG_SCHEMA_VERSION,
        "provider_setup_foundation_config_state": setup_config.config_state,
        "provider_setup_foundation_config_label": "Setup foundation config: local-only draft envelope",
        "provider_setup_foundation_config_migration": SETUP_FOUNDATION_CONFIG_MIGRATION_POSTURE,
        "provider_setup_foundation_config_valid": setup_config.config_valid,
        "provider_setup_foundation_setup_entry_state": setup_entry_state,
        "provider_setup_foundation_setup_entry_label": {
            SETUP_FOUNDATION_SETUP_ENTRY_DISABLED:
                "Setup entry point: disabled until USER-approved setup work",
            SETUP_FOUNDATION_SETUP_ENTRY_READY_LOCAL_DRAFT:
                "Setup entry point: local draft shell ready, execution disabled",
        }[setup_entry_state],
        "provider_setup_foundation_profile_draft_status": profile_draft_status,
        "provider_setup_foundation_profile_draft_label": {
            SETUP_FOUNDATION_PROFILE_DRAFT_MISSING:
                "Provider profile draft: missing local-only draft",
            SETUP_FOUNDATION_PROFILE_DRAFT_INVALID:
                "Provider profile draft: invalid local-only draft",
            SETUP_FOUNDATION_PROFILE_DRAFT_READY:
                "Provider profile draft: local-only draft validated",
        }[profile_draft_status],
        "provider_setup_foundation_config_draft_status": config_draft_status,
        "provider_setup_foundation_config_draft_label": {
            SETUP_FOUNDATION_CONFIG_DRAFT_MISSING:
                "Provider config draft: missing local-only draft",
            SETUP_FOUNDATION_CONFIG_DRAFT_INVALID:
                "Provider config draft: invalid local-only draft",
            SETUP_FOUNDATION_CONFIG_DRAFT_READY:
                "Provider config draft: local-only draft validated",
        }[config_draft_status],
        "provider_setup_foundation_validation_status": validation_status,
        "provider_setup_foundation_validation_label": {
            SETUP_FOUNDATION_VALIDATION_FAIL_CLOSED:
                "Setup foundation validation: fail-closed",
            SETUP_FOUNDATION_VALIDATION_STATIC_READY:
                "Setup foundation validation: static local proof ready",
        }[validation_status],
        "provider_setup_foundation_persistence_status": persistence_status,
        "provider_setup_foundation_persistence_label": {
            SETUP_FOUNDATION_PERSISTENCE_DISABLED:
                "Setup foundation persistence: disabled; no provider credentials stored",
            SETUP_FOUNDATION_PERSISTENCE_LOCAL_DRAFT_ONLY:
                "Setup foundation persistence: local draft metadata only; no secrets",
        }[persistence_status],
        "provider_setup_foundation_approval_status": foundation_approval,
        "provider_setup_foundation_approval_label": {
            SETUP_FOUNDATION_APPROVAL_STATUS_MISSING:
                "Setup foundation approval: USER approval missing",
            SETUP_FOUNDATION_APPROVAL_STATUS_FUTURE_GATED:
                "Setup foundation approval: future-gated",
            SETUP_FOUNDATION_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF:
                "Setup foundation approval: ready for future proof",
        }[foundation_approval],
        "provider_setup_foundation_gate_state": foundation_gate,
        "local_null_provider_fallback_proof": LOCAL_NULL_PROVIDER_FALLBACK_PROOF,
        "provider_setup_implementation_handoff_state": (
            FUTURE_PROVIDER_SETUP_IMPLEMENTATION_HANDOFF_READY
        ),
        "provider_setup_implementation_fold_down_posture": (
            PROVIDER_SETUP_IMPLEMENTATION_FOLD_DOWN_READY
        ),
    }


def build_provider_setup_implementation_foundation_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    setup_foundation_config: AIProviderSetupFoundationConfigSnapshot | dict[str, object] | None | object = (
        _SETUP_FOUNDATION_CONFIG_OMITTED
    ),
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve local setup implementation foundation without running provider setup."""

    contract_state = build_provider_setup_contract_readiness_state(
        readiness_config,
        activation_config=activation_config,
        execution_config=execution_config,
        path_consent_config=path_consent_config,
        surface_role=surface_role,
    )
    if setup_foundation_config is _SETUP_FOUNDATION_CONFIG_OMITTED:
        normalized_setup = build_default_provider_setup_foundation_config()
    else:
        normalized_setup = normalize_provider_setup_foundation_config(
            setup_foundation_config  # type: ignore[arg-type]
        )
    foundation_fields = _provider_setup_foundation_fields(contract_state, normalized_setup)
    return replace(
        contract_state,
        state_id=FAM007_PROVIDER_SETUP_IMPLEMENTATION_FOUNDATION_STATE_ID,
        mode=FAM007_PROVIDER_SETUP_IMPLEMENTATION_FOUNDATION_MODE,
        availability=FAM007_PROVIDER_SETUP_IMPLEMENTATION_FOUNDATION_AVAILABILITY,
        status_label=foundation_fields["provider_setup_foundation_label"],
        disabled_reason=(
            "Provider setup implementation foundation is local-only; real setup remains pending USER approval"
        ),
        provider_next_action_label="Next: local setup foundation proof remains future-gated",
        interaction_label="Provider setup implementation foundation only",
        interaction_disabled_reason=(
            "Provider setup, consent collection, prompt routing, and model execution require later USER approval"
        ),
        **foundation_fields,
    )


def build_default_provider_consent_collection_foundation_config() -> (
    AIProviderConsentCollectionFoundationConfigSnapshot
):
    """Return the safe local-only default consent collection foundation config."""

    return AIProviderConsentCollectionFoundationConfigSnapshot(
        schema_version=CONSENT_COLLECTION_FOUNDATION_CONFIG_SCHEMA_VERSION,
        config_state=PROVIDER_PATH_CONFIG_STATE_DEFAULT,
        consent_capture_surface_enabled=False,
        setup_consent_capture_ready=False,
        execution_consent_capture_ready=False,
        data_visibility_review_ready=False,
        audit_envelope_ready=False,
        provenance_ready=False,
        local_persistence_ready=False,
        validation_passed=False,
        policy_allows_collection=True,
        consent_collection_approved=False,
        future_capture_branch_ready=False,
        config_valid=True,
        provenance=CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION,
    )


def normalize_provider_consent_collection_foundation_config(
    config: AIProviderConsentCollectionFoundationConfigSnapshot | dict[str, object] | None,
) -> AIProviderConsentCollectionFoundationConfigSnapshot:
    """Normalize consent collection foundation config into a fail-closed posture."""

    provenance_sources = {
        CONSENT_COLLECTION_PROVENANCE_CONSENT_FLOW,
        CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION,
        CONSENT_COLLECTION_PROVENANCE_DATA_VISIBILITY,
        CONSENT_COLLECTION_PROVENANCE_AUDIT,
        CONSENT_COLLECTION_PROVENANCE_POLICY,
        CONSENT_COLLECTION_PROVENANCE_APPROVAL,
        CONSENT_COLLECTION_PROVENANCE_FUTURE_CAPTURE,
    }

    if config is None:
        return replace(
            build_default_provider_consent_collection_foundation_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_MISSING,
            config_valid=False,
            provenance=CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION,
        )

    if isinstance(config, AIProviderConsentCollectionFoundationConfigSnapshot):
        if (
            config.schema_version == CONSENT_COLLECTION_FOUNDATION_CONFIG_SCHEMA_VERSION
            and config.config_valid
        ):
            return config
        return replace(
            build_default_provider_consent_collection_foundation_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=config.provenance
            if config.provenance in provenance_sources
            else CONSENT_COLLECTION_PROVENANCE_AUDIT,
        )

    if not isinstance(config, dict):
        return replace(
            build_default_provider_consent_collection_foundation_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=CONSENT_COLLECTION_PROVENANCE_AUDIT,
        )

    schema_version = str(config.get("schema_version") or "")
    provenance = str(config.get("provenance") or CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION)
    config_valid = (
        bool(config.get("config_valid", True))
        and schema_version == CONSENT_COLLECTION_FOUNDATION_CONFIG_SCHEMA_VERSION
    )
    if not config_valid:
        return replace(
            build_default_provider_consent_collection_foundation_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=provenance
            if provenance in provenance_sources
            else CONSENT_COLLECTION_PROVENANCE_AUDIT,
        )

    return AIProviderConsentCollectionFoundationConfigSnapshot(
        schema_version=schema_version,
        config_state=PROVIDER_PATH_CONFIG_STATE_LOCAL,
        consent_capture_surface_enabled=bool(
            config.get("consent_capture_surface_enabled", False)
        ),
        setup_consent_capture_ready=bool(config.get("setup_consent_capture_ready", False)),
        execution_consent_capture_ready=bool(
            config.get("execution_consent_capture_ready", False)
        ),
        data_visibility_review_ready=bool(config.get("data_visibility_review_ready", False)),
        audit_envelope_ready=bool(config.get("audit_envelope_ready", False)),
        provenance_ready=bool(config.get("provenance_ready", False)),
        local_persistence_ready=bool(config.get("local_persistence_ready", False)),
        validation_passed=bool(config.get("validation_passed", False)),
        policy_allows_collection=bool(config.get("policy_allows_collection", True)),
        consent_collection_approved=bool(config.get("consent_collection_approved", False)),
        future_capture_branch_ready=bool(config.get("future_capture_branch_ready", False)),
        config_valid=True,
        provenance=provenance
        if provenance in provenance_sources
        else CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION,
    )


def build_default_provider_consent_capture_record() -> AIProviderConsentCaptureRecordSnapshot:
    """Return the fail-closed local consent capture record default."""

    return AIProviderConsentCaptureRecordSnapshot(
        schema_version=CONSENT_CAPTURE_LOCAL_RECORD_SCHEMA_VERSION,
        record_state=CONSENT_CAPTURE_RECORD_STATE_MISSING,
        local_write_requested=False,
        setup_consent_granted=False,
        execution_consent_granted=False,
        revoked=False,
        reset_requested=False,
        record_valid=False,
        provenance=CONSENT_CAPTURE_PROVENANCE_COLLECTION_STATE,
    )


def _has_consent_capture_action_flags(
    *,
    setup_consent_granted: bool,
    execution_consent_granted: bool,
    revoked: bool,
    reset_requested: bool,
) -> bool:
    return (
        setup_consent_granted
        or execution_consent_granted
        or revoked
        or reset_requested
    )


def normalize_provider_consent_capture_record(
    record: AIProviderConsentCaptureRecordSnapshot | dict[str, object] | None,
) -> AIProviderConsentCaptureRecordSnapshot:
    """Normalize a local-only consent capture write request into a safe record."""

    provenance_sources = {
        CONSENT_CAPTURE_PROVENANCE_COLLECTION_STATE,
        CONSENT_CAPTURE_PROVENANCE_LOCAL_RECORD,
    }

    if record is None:
        return build_default_provider_consent_capture_record()

    if isinstance(record, AIProviderConsentCaptureRecordSnapshot):
        normalized_provenance = (
            record.provenance
            if record.provenance in provenance_sources
            else CONSENT_CAPTURE_PROVENANCE_LOCAL_RECORD
        )
        action_flags_present = _has_consent_capture_action_flags(
            setup_consent_granted=record.setup_consent_granted,
            execution_consent_granted=record.execution_consent_granted,
            revoked=record.revoked,
            reset_requested=record.reset_requested,
        )
        if (
            record.schema_version == CONSENT_CAPTURE_LOCAL_RECORD_SCHEMA_VERSION
            and not record.record_valid
            and record.record_state == CONSENT_CAPTURE_RECORD_STATE_MISSING
            and not record.local_write_requested
            and not action_flags_present
        ):
            return replace(
                build_default_provider_consent_capture_record(),
                provenance=normalized_provenance,
            )
        if (
            record.schema_version == CONSENT_CAPTURE_LOCAL_RECORD_SCHEMA_VERSION
            and record.record_valid
        ):
            if action_flags_present and not record.local_write_requested:
                return replace(
                    build_default_provider_consent_capture_record(),
                    record_state=CONSENT_CAPTURE_RECORD_STATE_INVALID,
                    local_write_requested=True,
                    record_valid=False,
                    provenance=normalized_provenance,
                )
            return record
        return replace(
            build_default_provider_consent_capture_record(),
            record_state=CONSENT_CAPTURE_RECORD_STATE_INVALID,
            local_write_requested=record.local_write_requested or action_flags_present,
            record_valid=False,
            provenance=normalized_provenance,
        )

    if not isinstance(record, dict):
        return replace(
            build_default_provider_consent_capture_record(),
            record_state=CONSENT_CAPTURE_RECORD_STATE_INVALID,
            local_write_requested=True,
            record_valid=False,
            provenance=CONSENT_CAPTURE_PROVENANCE_LOCAL_RECORD,
        )

    schema_version = str(record.get("schema_version") or "")
    provenance = str(record.get("provenance") or CONSENT_CAPTURE_PROVENANCE_LOCAL_RECORD)
    setup_consent_granted = bool(record.get("setup_consent_granted", False))
    execution_consent_granted = bool(record.get("execution_consent_granted", False))
    revoked = bool(record.get("revoked", False))
    reset_requested = bool(record.get("reset_requested", False))
    action_flags_present = _has_consent_capture_action_flags(
        setup_consent_granted=setup_consent_granted,
        execution_consent_granted=execution_consent_granted,
        revoked=revoked,
        reset_requested=reset_requested,
    )
    local_write_requested = bool(
        record.get(
            "local_write_requested",
            action_flags_present,
        )
    )
    explicit_write_request_conflict = (
        "local_write_requested" in record
        and not local_write_requested
        and action_flags_present
    )
    record_valid = (
        bool(record.get("record_valid", True))
        and schema_version == CONSENT_CAPTURE_LOCAL_RECORD_SCHEMA_VERSION
        and not explicit_write_request_conflict
    )

    normalized_provenance = (
        provenance
        if provenance in provenance_sources
        else CONSENT_CAPTURE_PROVENANCE_LOCAL_RECORD
    )
    if not record_valid:
        return replace(
            build_default_provider_consent_capture_record(),
            record_state=CONSENT_CAPTURE_RECORD_STATE_INVALID,
            local_write_requested=local_write_requested or action_flags_present,
            record_valid=False,
            provenance=normalized_provenance,
        )

    if reset_requested:
        record_state = CONSENT_CAPTURE_RECORD_STATE_RESET
    elif revoked:
        record_state = CONSENT_CAPTURE_RECORD_STATE_REVOKED
    elif setup_consent_granted or execution_consent_granted:
        record_state = CONSENT_CAPTURE_RECORD_STATE_READY
    elif local_write_requested:
        record_state = CONSENT_CAPTURE_RECORD_STATE_NO_CONSENT_SELECTED
    else:
        record_state = CONSENT_CAPTURE_RECORD_STATE_MISSING

    return AIProviderConsentCaptureRecordSnapshot(
        schema_version=schema_version,
        record_state=record_state,
        local_write_requested=local_write_requested,
        setup_consent_granted=setup_consent_granted,
        execution_consent_granted=execution_consent_granted,
        revoked=revoked,
        reset_requested=reset_requested,
        record_valid=record_valid,
        provenance=normalized_provenance,
    )


def build_default_provider_durable_consent_record() -> AIProviderDurableConsentRecordSnapshot:
    """Return the fail-closed durable consent record default."""

    return AIProviderDurableConsentRecordSnapshot(
        schema_version=CONSENT_DURABLE_RECORD_SCHEMA_VERSION,
        record_state=CONSENT_DURABLE_RECORD_STATE_MISSING,
        record_valid=False,
        record_id="",
        provider_profile_id=PROVIDER_PROFILE_ID_LOCAL_NULL,
        setup_consent_granted=False,
        execution_consent_granted=False,
        setup_consent_revoked=False,
        execution_consent_revoked=False,
        setup_consent_reset_requested=False,
        execution_consent_reset_requested=False,
        setup_consent_expired=False,
        execution_consent_expired=False,
        setup_consent_expires_at_utc="",
        execution_consent_expires_at_utc="",
        revoked=False,
        reset_requested=False,
        expired=False,
        expires_at_utc="",
        captured_at_utc="",
        updated_at_utc="",
        provenance=CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD,
        audit_event_id="",
        storage_boundary=CONSENT_DURABLE_STORAGE_BOUNDARY_LOCAL_ONLY,
        migration_posture=CONSENT_DURABLE_MIGRATION_NOT_APPLICABLE,
        fail_closed_reason=CONSENT_DURABLE_FAIL_REASON_MISSING,
        no_secrets=True,
        provider_payload_excluded=True,
    )


def _parse_utc_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _now_utc(now_utc: datetime | None) -> datetime:
    if now_utc is None:
        return datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        return now_utc.replace(tzinfo=timezone.utc)
    return now_utc.astimezone(timezone.utc)


def _read_durable_consent_bool(
    record_payload: dict[str, object],
    field_name: str,
    *,
    default: bool,
) -> tuple[bool, bool]:
    if field_name not in record_payload:
        return default, False
    value = record_payload[field_name]
    if isinstance(value, bool):
        return value, False
    return default, True


def normalize_provider_durable_consent_record(
    record: AIProviderDurableConsentRecordSnapshot | dict[str, object] | None,
    *,
    now_utc: datetime | None = None,
) -> AIProviderDurableConsentRecordSnapshot:
    """Normalize a durable local consent record into a fail-closed state."""

    if record is None:
        return build_default_provider_durable_consent_record()

    if isinstance(record, AIProviderDurableConsentRecordSnapshot):
        record_payload = record.as_dict()
    elif isinstance(record, dict):
        record_payload = record
    else:
        return replace(
            build_default_provider_durable_consent_record(),
            record_state=CONSENT_DURABLE_RECORD_STATE_CORRUPT,
            fail_closed_reason=CONSENT_DURABLE_FAIL_REASON_CORRUPT,
            provenance=CONSENT_DURABLE_PROVENANCE_LOCAL_STORE,
        )

    schema_version = str(record_payload.get("schema_version") or "")
    if schema_version == CONSENT_DURABLE_RECORD_STALE_SCHEMA_VERSION:
        return replace(
            build_default_provider_durable_consent_record(),
            schema_version=schema_version,
            record_state=CONSENT_DURABLE_RECORD_STATE_STALE_SCHEMA,
            migration_posture=CONSENT_DURABLE_MIGRATION_STALE_SCHEMA_FAIL_CLOSED,
            fail_closed_reason=CONSENT_DURABLE_FAIL_REASON_STALE_SCHEMA,
            provenance=CONSENT_DURABLE_PROVENANCE_LOCAL_STORE,
        )
    if schema_version != CONSENT_DURABLE_RECORD_SCHEMA_VERSION:
        return replace(
            build_default_provider_durable_consent_record(),
            schema_version=schema_version,
            record_state=CONSENT_DURABLE_RECORD_STATE_UNSUPPORTED_SCHEMA,
            migration_posture=(
                CONSENT_DURABLE_MIGRATION_UNSUPPORTED_SCHEMA_FAIL_CLOSED
            ),
            fail_closed_reason=CONSENT_DURABLE_FAIL_REASON_UNSUPPORTED_SCHEMA,
            provenance=CONSENT_DURABLE_PROVENANCE_LOCAL_STORE,
        )

    record_state_hint = str(record_payload.get("record_state") or "")
    fail_closed_reason_hint = str(
        record_payload.get("fail_closed_reason") or CONSENT_DURABLE_FAIL_REASON_MISSING
    )
    record_valid_hint, record_valid_hint_invalid = _read_durable_consent_bool(
        record_payload,
        "record_valid",
        default=True,
    )
    if (
        record_state_hint == CONSENT_DURABLE_RECORD_STATE_MISSING
        and not record_valid_hint
        and not record_valid_hint_invalid
        and fail_closed_reason_hint == CONSENT_DURABLE_FAIL_REASON_MISSING
    ):
        provenance_hint = str(
            record_payload.get("provenance")
            or CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD
        )
        if provenance_hint not in {
            CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD,
            CONSENT_DURABLE_PROVENANCE_LOCAL_STORE,
        }:
            provenance_hint = CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD
        return replace(
            build_default_provider_durable_consent_record(),
            schema_version=schema_version,
            provenance=provenance_hint,
        )

    record_id = str(
        record_payload.get("record_id") or CONSENT_DURABLE_DEFAULT_RECORD_ID
    )
    provider_profile_id = str(
        record_payload.get("provider_profile_id") or PROVIDER_PROFILE_ID_LOCAL_NULL
    )
    boolean_field_invalid = False
    setup_consent_granted, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "setup_consent_granted",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    execution_consent_granted, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "execution_consent_granted",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    revoked, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "revoked",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    reset_requested, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "reset_requested",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    setup_consent_revoked, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "setup_consent_revoked",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    setup_consent_revoked = setup_consent_revoked or (
        revoked and setup_consent_granted
    )
    execution_consent_revoked, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "execution_consent_revoked",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    execution_consent_revoked = execution_consent_revoked or (
        revoked and execution_consent_granted
    )
    setup_consent_reset_requested, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "setup_consent_reset_requested",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    setup_consent_reset_requested = setup_consent_reset_requested or (
        reset_requested and setup_consent_granted
    )
    execution_consent_reset_requested, invalid_bool = (
        _read_durable_consent_bool(
            record_payload,
            "execution_consent_reset_requested",
            default=False,
        )
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    execution_consent_reset_requested = execution_consent_reset_requested or (
        reset_requested and execution_consent_granted
    )
    expires_at_utc = str(record_payload.get("expires_at_utc") or "")
    setup_consent_expires_at_utc = str(
        record_payload.get("setup_consent_expires_at_utc") or expires_at_utc
    )
    execution_consent_expires_at_utc = str(
        record_payload.get("execution_consent_expires_at_utc") or expires_at_utc
    )
    captured_at_utc = str(record_payload.get("captured_at_utc") or "")
    updated_at_utc = str(record_payload.get("updated_at_utc") or "")
    provenance = str(
        record_payload.get("provenance") or CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD
    )
    if provenance not in {
        CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD,
        CONSENT_DURABLE_PROVENANCE_LOCAL_STORE,
    }:
        provenance = CONSENT_DURABLE_PROVENANCE_LOCAL_RECORD
    audit_event_id = str(
        record_payload.get("audit_event_id")
        or CONSENT_DURABLE_DEFAULT_AUDIT_EVENT_ID
    )
    no_secrets, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "no_secrets",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    provider_payload_excluded, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "provider_payload_excluded",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    storage_boundary = str(
        record_payload.get("storage_boundary")
        or CONSENT_DURABLE_STORAGE_BOUNDARY_LOCAL_ONLY
    )

    expires_at = _parse_utc_timestamp(expires_at_utc)
    setup_expires_at = _parse_utc_timestamp(setup_consent_expires_at_utc)
    execution_expires_at = _parse_utc_timestamp(execution_consent_expires_at_utc)
    current_time = _now_utc(now_utc)
    invalid_expiry_timestamp = (
        (bool(expires_at_utc.strip()) and expires_at is None)
        or (
            bool(setup_consent_expires_at_utc.strip())
            and setup_expires_at is None
        )
        or (
            bool(execution_consent_expires_at_utc.strip())
            and execution_expires_at is None
        )
    )
    record_expired = expires_at is not None and expires_at <= current_time
    setup_consent_expired, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "setup_consent_expired",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    setup_consent_expired = setup_consent_expired or (
        setup_expires_at is not None
        and setup_consent_granted
        and setup_expires_at <= current_time
    )
    execution_consent_expired, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "execution_consent_expired",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    execution_consent_expired = execution_consent_expired or (
        execution_expires_at is not None
        and execution_consent_granted
        and execution_expires_at <= current_time
    )
    expired_flag_requested, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "expired",
        default=False,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    expired = (
        record_expired
        or expired_flag_requested
        or setup_consent_expired
        or execution_consent_expired
    )
    effective_setup_consent_expired = (
        setup_consent_expired or record_expired or expired_flag_requested
    )
    effective_execution_consent_expired = (
        execution_consent_expired or record_expired or expired_flag_requested
    )
    setup_consent_active = (
        setup_consent_granted
        and not setup_consent_revoked
        and not setup_consent_reset_requested
        and not effective_setup_consent_expired
        and not revoked
        and not reset_requested
    )
    execution_consent_active = (
        execution_consent_granted
        and not execution_consent_revoked
        and not execution_consent_reset_requested
        and not effective_execution_consent_expired
        and not revoked
        and not reset_requested
    )
    record_valid_flag, invalid_bool = _read_durable_consent_bool(
        record_payload,
        "record_valid",
        default=True,
    )
    boolean_field_invalid = boolean_field_invalid or invalid_bool
    record_valid = (
        record_valid_flag
        and bool(record_id)
        and bool(audit_event_id)
        and no_secrets
        and provider_payload_excluded
        and storage_boundary == CONSENT_DURABLE_STORAGE_BOUNDARY_LOCAL_ONLY
        and not invalid_expiry_timestamp
        and not boolean_field_invalid
    )

    record_state = CONSENT_DURABLE_RECORD_STATE_READY
    fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_NONE
    if not record_valid:
        record_state = CONSENT_DURABLE_RECORD_STATE_INVALID
        fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_INVALID
    elif reset_requested:
        record_state = CONSENT_DURABLE_RECORD_STATE_RESET
        fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_RESET
    elif revoked:
        record_state = CONSENT_DURABLE_RECORD_STATE_REVOKED
        fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_REVOKED
    elif expired:
        record_state = CONSENT_DURABLE_RECORD_STATE_EXPIRED
        fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_EXPIRED
    elif not (setup_consent_granted or execution_consent_granted):
        record_state = CONSENT_DURABLE_RECORD_STATE_INVALID
        record_valid = False
        fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_NO_CONSENT_SELECTED
    elif not (setup_consent_active or execution_consent_active):
        if setup_consent_reset_requested or execution_consent_reset_requested:
            record_state = CONSENT_DURABLE_RECORD_STATE_RESET
            fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_RESET
        elif setup_consent_revoked or execution_consent_revoked:
            record_state = CONSENT_DURABLE_RECORD_STATE_REVOKED
            fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_REVOKED
        elif effective_setup_consent_expired or effective_execution_consent_expired:
            record_state = CONSENT_DURABLE_RECORD_STATE_EXPIRED
            fail_closed_reason = CONSENT_DURABLE_FAIL_REASON_EXPIRED

    return AIProviderDurableConsentRecordSnapshot(
        schema_version=schema_version,
        record_state=record_state,
        record_valid=record_valid,
        record_id=record_id,
        provider_profile_id=provider_profile_id,
        setup_consent_granted=setup_consent_granted,
        execution_consent_granted=execution_consent_granted,
        setup_consent_revoked=setup_consent_revoked,
        execution_consent_revoked=execution_consent_revoked,
        setup_consent_reset_requested=setup_consent_reset_requested,
        execution_consent_reset_requested=execution_consent_reset_requested,
        setup_consent_expired=effective_setup_consent_expired,
        execution_consent_expired=effective_execution_consent_expired,
        setup_consent_expires_at_utc=setup_consent_expires_at_utc,
        execution_consent_expires_at_utc=execution_consent_expires_at_utc,
        revoked=revoked,
        reset_requested=reset_requested,
        expired=expired,
        expires_at_utc=expires_at_utc,
        captured_at_utc=captured_at_utc,
        updated_at_utc=updated_at_utc,
        provenance=provenance,
        audit_event_id=audit_event_id,
        storage_boundary=storage_boundary,
        migration_posture=CONSENT_DURABLE_MIGRATION_CURRENT_SCHEMA_READY,
        fail_closed_reason=fail_closed_reason,
        no_secrets=no_secrets,
        provider_payload_excluded=provider_payload_excluded,
    )


def resolve_default_provider_durable_consent_store_dir() -> Path:
    """Resolve the local-only durable consent store directory for desktop runtime."""

    override = os.environ.get(CONSENT_DURABLE_STORE_DIR_ENV, "").strip()
    if override:
        return Path(override)

    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        return Path(local_app_data) / "Nexus Desktop AI" / CONSENT_DURABLE_STORE_DIRNAME

    return (
        Path.home()
        / "AppData"
        / "Local"
        / "Nexus Desktop AI"
        / CONSENT_DURABLE_STORE_DIRNAME
    )


def _provider_durable_consent_record_path(store_dir: str | Path) -> Path:
    return Path(store_dir) / CONSENT_DURABLE_RECORD_FILENAME


def _clear_provider_durable_consent_record_path(record_path: Path) -> None:
    try:
        record_path.unlink(missing_ok=True)
    except OSError:
        if record_path.is_dir():
            return
        raise


def write_provider_durable_consent_record(
    store_dir: str | Path,
    record: AIProviderDurableConsentRecordSnapshot | dict[str, object],
    *,
    now_utc: datetime | None = None,
) -> AIProviderDurableConsentRecordSnapshot:
    """Persist a normalized durable consent record to an explicit local store."""

    normalized = normalize_provider_durable_consent_record(record, now_utc=now_utc)
    record_path = _provider_durable_consent_record_path(store_dir)
    if normalized.record_state in {
        CONSENT_DURABLE_RECORD_STATE_INVALID,
        CONSENT_DURABLE_RECORD_STATE_CORRUPT,
        CONSENT_DURABLE_RECORD_STATE_UNSUPPORTED_SCHEMA,
        CONSENT_DURABLE_RECORD_STATE_STALE_SCHEMA,
        CONSENT_DURABLE_RECORD_STATE_MISSING,
    }:
        _clear_provider_durable_consent_record_path(record_path)
        return normalized
    try:
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(
            json.dumps(normalized.as_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return replace(
            build_default_provider_durable_consent_record(),
            record_state=CONSENT_DURABLE_RECORD_STATE_CORRUPT,
            fail_closed_reason=CONSENT_DURABLE_FAIL_REASON_CORRUPT,
            provenance=CONSENT_DURABLE_PROVENANCE_LOCAL_STORE,
        )
    return normalized


def load_provider_durable_consent_record(
    store_dir: str | Path,
    *,
    now_utc: datetime | None = None,
) -> AIProviderDurableConsentRecordSnapshot:
    """Load a durable consent record from the explicit local store."""

    record_path = _provider_durable_consent_record_path(store_dir)
    if not record_path.exists():
        return build_default_provider_durable_consent_record()
    try:
        payload = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return replace(
            build_default_provider_durable_consent_record(),
            record_state=CONSENT_DURABLE_RECORD_STATE_CORRUPT,
            fail_closed_reason=CONSENT_DURABLE_FAIL_REASON_CORRUPT,
            provenance=CONSENT_DURABLE_PROVENANCE_LOCAL_STORE,
        )
    if not isinstance(payload, dict):
        return replace(
            build_default_provider_durable_consent_record(),
            record_state=CONSENT_DURABLE_RECORD_STATE_CORRUPT,
            fail_closed_reason=CONSENT_DURABLE_FAIL_REASON_CORRUPT,
            provenance=CONSENT_DURABLE_PROVENANCE_LOCAL_STORE,
        )
    payload.setdefault("provenance", CONSENT_DURABLE_PROVENANCE_LOCAL_STORE)
    return normalize_provider_durable_consent_record(payload, now_utc=now_utc)


def _durable_consent_scope_status(
    durable_record: AIProviderDurableConsentRecordSnapshot,
    *,
    scope: str,
) -> tuple[str, str, str]:
    granted = (
        durable_record.setup_consent_granted
        if scope == "setup"
        else durable_record.execution_consent_granted
    )
    revoked = (
        durable_record.setup_consent_revoked
        if scope == "setup"
        else durable_record.execution_consent_revoked
    )
    reset_requested = (
        durable_record.setup_consent_reset_requested
        if scope == "setup"
        else durable_record.execution_consent_reset_requested
    )
    expired = (
        durable_record.setup_consent_expired
        if scope == "setup"
        else durable_record.execution_consent_expired
    )
    title = "setup" if scope == "setup" else "execution"
    missing_reason = (
        CONSENT_DURABLE_SETUP_REASON_MISSING
        if scope == "setup"
        else CONSENT_DURABLE_EXECUTION_REASON_MISSING
    )

    fail_closed_record_states = {
        CONSENT_DURABLE_RECORD_STATE_INVALID,
        CONSENT_DURABLE_RECORD_STATE_CORRUPT,
        CONSENT_DURABLE_RECORD_STATE_UNSUPPORTED_SCHEMA,
        CONSENT_DURABLE_RECORD_STATE_STALE_SCHEMA,
    }
    if (
        durable_record.record_state == CONSENT_DURABLE_RECORD_STATE_INVALID
        and durable_record.fail_closed_reason
        == CONSENT_DURABLE_FAIL_REASON_NO_CONSENT_SELECTED
        and not granted
    ):
        return (
            CONSENT_DURABLE_CONSENT_STATE_MISSING,
            f"Durable {title} consent: missing",
            missing_reason,
        )
    if durable_record.record_state in fail_closed_record_states:
        return (
            CONSENT_DURABLE_CONSENT_STATE_BLOCKED,
            f"Durable {title} consent: blocked fail-closed",
            CONSENT_DURABLE_REASON_FAIL_CLOSED,
        )
    if durable_record.record_state == CONSENT_DURABLE_RECORD_STATE_MISSING:
        return (
            CONSENT_DURABLE_CONSENT_STATE_MISSING,
            f"Durable {title} consent: missing",
            missing_reason,
        )
    if not granted:
        return (
            CONSENT_DURABLE_CONSENT_STATE_MISSING,
            f"Durable {title} consent: missing",
            missing_reason,
        )
    if durable_record.reset_requested or reset_requested:
        return (
            CONSENT_DURABLE_CONSENT_STATE_RESET,
            f"Durable {title} consent: reset",
            CONSENT_DURABLE_REASON_RESET,
        )
    if durable_record.revoked or revoked:
        return (
            CONSENT_DURABLE_CONSENT_STATE_REVOKED,
            f"Durable {title} consent: revoked",
            CONSENT_DURABLE_REASON_REVOKED,
        )
    if expired:
        return (
            CONSENT_DURABLE_CONSENT_STATE_EXPIRED,
            f"Durable {title} consent: expired",
            CONSENT_DURABLE_REASON_EXPIRED,
        )
    return (
        CONSENT_DURABLE_CONSENT_STATE_GRANTED,
        f"Durable {title} consent: granted local-only",
        CONSENT_DURABLE_REASON_GRANTED,
    )


def _provider_consent_collection_foundation_fields(
    setup_foundation_state: AIProviderStateSnapshot,
    consent_config: AIProviderConsentCollectionFoundationConfigSnapshot,
) -> dict[str, object]:
    collection_state = CONSENT_COLLECTION_STATE_UNAVAILABLE
    collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_UNAVAILABLE
    collection_blocker = CONSENT_COLLECTION_BLOCKER_CONSENT_FLOW_REQUIRED
    collection_reason = CONSENT_COLLECTION_REASON_DEFAULT_UNAVAILABLE
    collection_provenance = CONSENT_COLLECTION_PROVENANCE_CONSENT_FLOW
    collection_approval = CONSENT_COLLECTION_APPROVAL_STATUS_MISSING
    collection_gate = CONSENT_COLLECTION_GATE_BLOCKED

    capture_surface_state = (
        CONSENT_COLLECTION_CAPTURE_SURFACE_READY_FUTURE_GATED
        if consent_config.consent_capture_surface_enabled
        else CONSENT_COLLECTION_CAPTURE_SURFACE_DISABLED
    )
    setup_capture_status = (
        CONSENT_COLLECTION_CAPTURE_SETUP_READY
        if consent_config.setup_consent_capture_ready
        else CONSENT_COLLECTION_CAPTURE_SETUP_REQUIRED
    )
    execution_capture_status = (
        CONSENT_COLLECTION_CAPTURE_EXECUTION_READY
        if consent_config.execution_consent_capture_ready
        else CONSENT_COLLECTION_CAPTURE_EXECUTION_REQUIRED
    )
    data_visibility_status = (
        CONSENT_COLLECTION_DATA_VISIBILITY_REVIEW_READY
        if consent_config.data_visibility_review_ready
        else CONSENT_COLLECTION_DATA_VISIBILITY_REVIEW_REQUIRED
    )
    audit_envelope_status = (
        CONSENT_COLLECTION_AUDIT_ENVELOPE_READY
        if consent_config.audit_envelope_ready
        else CONSENT_COLLECTION_AUDIT_ENVELOPE_REQUIRED
    )
    provenance_status = (
        CONSENT_COLLECTION_PROVENANCE_READY
        if consent_config.provenance_ready
        else CONSENT_COLLECTION_PROVENANCE_REQUIRED
    )
    persistence_status = (
        CONSENT_COLLECTION_PERSISTENCE_LOCAL_PROOF_ONLY
        if consent_config.local_persistence_ready
        else CONSENT_COLLECTION_PERSISTENCE_DISABLED
    )
    validation_status = (
        CONSENT_COLLECTION_VALIDATION_STATIC_READY
        if consent_config.validation_passed
        and consent_config.consent_capture_surface_enabled
        and consent_config.setup_consent_capture_ready
        and consent_config.execution_consent_capture_ready
        and consent_config.data_visibility_review_ready
        and consent_config.audit_envelope_ready
        and consent_config.provenance_ready
        and consent_config.local_persistence_ready
        else CONSENT_COLLECTION_VALIDATION_FAIL_CLOSED
    )

    ready_consent_flow_states = {
        CONSENT_FLOW_STATE_READY_FUTURE_GATED,
        CONSENT_FLOW_STATE_READY_BUT_NOT_COLLECTED,
        CONSENT_FLOW_STATE_READY_FOR_FUTURE_CONSENT_BRANCH,
    }
    ready_setup_foundation_states = {
        SETUP_FOUNDATION_STATE_READY_LOCAL_DRAFT,
        SETUP_FOUNDATION_STATE_READY_FUTURE_GATED,
        SETUP_FOUNDATION_STATE_READY_BUT_NOT_APPROVED,
        SETUP_FOUNDATION_STATE_READY_FOR_FUTURE_SETUP_BRANCH,
    }

    if consent_config.config_state == PROVIDER_PATH_CONFIG_STATE_MISSING:
        collection_state = CONSENT_COLLECTION_STATE_DISABLED
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_DISABLED
        collection_reason = CONSENT_COLLECTION_REASON_CONFIG_MISSING
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION
    elif consent_config.config_state == PROVIDER_PATH_CONFIG_STATE_INVALID:
        collection_state = CONSENT_COLLECTION_STATE_DEGRADED
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_BLOCKED
        collection_blocker = CONSENT_COLLECTION_BLOCKER_AUDIT_REQUIRED
        collection_reason = CONSENT_COLLECTION_REASON_CONFIG_INVALID
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_AUDIT
    elif not consent_config.policy_allows_collection:
        collection_state = CONSENT_COLLECTION_STATE_BLOCKED_BY_POLICY
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_BLOCKED
        collection_blocker = CONSENT_COLLECTION_BLOCKER_POLICY_BLOCKED
        collection_reason = CONSENT_COLLECTION_REASON_POLICY_BLOCKED
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_POLICY
    elif setup_foundation_state.consent_flow_readiness_state not in ready_consent_flow_states:
        collection_state = CONSENT_COLLECTION_STATE_BLOCKED_BY_CONSENT_FLOW
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_BLOCKED
        collection_reason = CONSENT_COLLECTION_REASON_CONSENT_FLOW_REQUIRED
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_CONSENT_FLOW
    elif (
        setup_foundation_state.provider_setup_foundation_state
        not in ready_setup_foundation_states
    ):
        collection_state = CONSENT_COLLECTION_STATE_BLOCKED_BY_SETUP_FOUNDATION
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_BLOCKED
        collection_blocker = CONSENT_COLLECTION_BLOCKER_SETUP_FOUNDATION_REQUIRED
        collection_reason = CONSENT_COLLECTION_REASON_SETUP_FOUNDATION_REQUIRED
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION
    elif not consent_config.consent_capture_surface_enabled:
        collection_state = CONSENT_COLLECTION_STATE_DISABLED
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_DISABLED
        collection_reason = CONSENT_COLLECTION_REASON_DEFAULT_UNAVAILABLE
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION
    elif (
        not consent_config.setup_consent_capture_ready
        or not consent_config.execution_consent_capture_ready
    ):
        collection_state = CONSENT_COLLECTION_STATE_BLOCKED_BY_CONSENT_FLOW
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_BLOCKED
        collection_reason = CONSENT_COLLECTION_REASON_CONSENT_FLOW_REQUIRED
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_CONSENT_FLOW
    elif not consent_config.data_visibility_review_ready:
        collection_state = CONSENT_COLLECTION_STATE_BLOCKED_BY_DATA_VISIBILITY
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_BLOCKED
        collection_blocker = CONSENT_COLLECTION_BLOCKER_DATA_VISIBILITY_REQUIRED
        collection_reason = CONSENT_COLLECTION_REASON_DATA_VISIBILITY_BLOCKED
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_DATA_VISIBILITY
    elif not consent_config.audit_envelope_ready or not consent_config.provenance_ready:
        collection_state = CONSENT_COLLECTION_STATE_BLOCKED_BY_AUDIT
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_BLOCKED
        collection_blocker = CONSENT_COLLECTION_BLOCKER_AUDIT_REQUIRED
        collection_reason = CONSENT_COLLECTION_REASON_AUDIT_REQUIRED
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_AUDIT
    elif not consent_config.local_persistence_ready or not consent_config.validation_passed:
        collection_state = CONSENT_COLLECTION_STATE_DEGRADED
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_BLOCKED
        collection_blocker = CONSENT_COLLECTION_BLOCKER_AUDIT_REQUIRED
        collection_reason = CONSENT_COLLECTION_REASON_AUDIT_REQUIRED
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_AUDIT
    elif not consent_config.consent_collection_approved:
        collection_state = CONSENT_COLLECTION_STATE_READY_BUT_NOT_APPROVED
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_READY_NOT_APPROVED
        collection_blocker = CONSENT_COLLECTION_BLOCKER_APPROVAL_REQUIRED
        collection_reason = CONSENT_COLLECTION_REASON_APPROVAL_MISSING
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_APPROVAL
        collection_gate = CONSENT_COLLECTION_GATE_LOCAL_PROOF
    elif consent_config.future_capture_branch_ready:
        collection_state = CONSENT_COLLECTION_STATE_READY_FOR_FUTURE_CAPTURE_BRANCH
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_FUTURE_CAPTURE_BRANCH
        collection_blocker = CONSENT_COLLECTION_BLOCKER_FUTURE_CAPTURE_BRANCH
        collection_reason = CONSENT_COLLECTION_REASON_READY_FOR_FUTURE_CAPTURE_BRANCH
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_FUTURE_CAPTURE
        collection_approval = CONSENT_COLLECTION_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF
        collection_gate = CONSENT_COLLECTION_GATE_FUTURE_GATED
    else:
        collection_state = CONSENT_COLLECTION_STATE_READY_BUT_NOT_COLLECTED
        collection_eligibility = CONSENT_COLLECTION_ELIGIBILITY_READY_NOT_COLLECTED
        collection_blocker = CONSENT_COLLECTION_BLOCKER_FUTURE_CAPTURE_BRANCH
        collection_reason = CONSENT_COLLECTION_REASON_READY_BUT_NOT_COLLECTED
        collection_provenance = CONSENT_COLLECTION_PROVENANCE_FUTURE_CAPTURE
        collection_approval = CONSENT_COLLECTION_APPROVAL_STATUS_FUTURE_GATED
        collection_gate = CONSENT_COLLECTION_GATE_FUTURE_GATED

    state_labels = {
        CONSENT_COLLECTION_STATE_UNAVAILABLE: "Consent collection foundation: unavailable",
        CONSENT_COLLECTION_STATE_DISABLED: "Consent collection foundation: disabled",
        CONSENT_COLLECTION_STATE_BLOCKED_BY_CONSENT_FLOW:
            "Consent collection foundation: blocked by consent flow",
        CONSENT_COLLECTION_STATE_BLOCKED_BY_SETUP_FOUNDATION:
            "Consent collection foundation: blocked by setup foundation",
        CONSENT_COLLECTION_STATE_BLOCKED_BY_POLICY:
            "Consent collection foundation: blocked by policy",
        CONSENT_COLLECTION_STATE_BLOCKED_BY_DATA_VISIBILITY:
            "Consent collection foundation: blocked by data visibility review",
        CONSENT_COLLECTION_STATE_BLOCKED_BY_AUDIT:
            "Consent collection foundation: blocked by audit envelope",
        CONSENT_COLLECTION_STATE_READY_FUTURE_GATED:
            "Consent collection foundation: ready but future-gated",
        CONSENT_COLLECTION_STATE_READY_BUT_NOT_APPROVED:
            "Consent collection foundation: ready but USER approval missing",
        CONSENT_COLLECTION_STATE_READY_BUT_NOT_COLLECTED:
            "Consent collection foundation: ready but no consent collected",
        CONSENT_COLLECTION_STATE_READY_FOR_FUTURE_CAPTURE_BRANCH:
            "Consent collection foundation: ready for future capture branch",
        CONSENT_COLLECTION_STATE_DEGRADED:
            "Consent collection foundation: degraded and fail-closed",
    }
    eligibility_labels = {
        CONSENT_COLLECTION_ELIGIBILITY_UNAVAILABLE:
            "Consent collection eligibility: unavailable",
        CONSENT_COLLECTION_ELIGIBILITY_DISABLED:
            "Consent collection eligibility: disabled",
        CONSENT_COLLECTION_ELIGIBILITY_BLOCKED:
            "Consent collection eligibility: blocked",
        CONSENT_COLLECTION_ELIGIBILITY_FUTURE_GATED:
            "Consent collection eligibility: future-gated",
        CONSENT_COLLECTION_ELIGIBILITY_READY_NOT_APPROVED:
            "Consent collection eligibility: ready but USER approval missing",
        CONSENT_COLLECTION_ELIGIBILITY_READY_NOT_COLLECTED:
            "Consent collection eligibility: ready but no consent collected",
        CONSENT_COLLECTION_ELIGIBILITY_FUTURE_CAPTURE_BRANCH:
            "Consent collection eligibility: future capture branch",
    }
    blocker_labels = {
        CONSENT_COLLECTION_BLOCKER_CONSENT_FLOW_REQUIRED:
            "Consent collection blocker: consent flow readiness required",
        CONSENT_COLLECTION_BLOCKER_SETUP_FOUNDATION_REQUIRED:
            "Consent collection blocker: setup foundation readiness required",
        CONSENT_COLLECTION_BLOCKER_POLICY_BLOCKED:
            "Consent collection blocker: policy blocks consent collection",
        CONSENT_COLLECTION_BLOCKER_DATA_VISIBILITY_REQUIRED:
            "Consent collection blocker: provider-visible data review required",
        CONSENT_COLLECTION_BLOCKER_AUDIT_REQUIRED:
            "Consent collection blocker: audit/provenance proof required",
        CONSENT_COLLECTION_BLOCKER_APPROVAL_REQUIRED:
            "Consent collection blocker: USER consent collection approval required",
        CONSENT_COLLECTION_BLOCKER_FUTURE_CAPTURE_BRANCH:
            "Consent collection blocker: future capture branch required",
    }
    reason_labels = {
        CONSENT_COLLECTION_REASON_DEFAULT_UNAVAILABLE:
            "Consent collection reason: local-only safe default",
        CONSENT_COLLECTION_REASON_CONFIG_MISSING:
            "Consent collection reason: config snapshot missing",
        CONSENT_COLLECTION_REASON_CONFIG_INVALID:
            "Consent collection reason: config snapshot invalid",
        CONSENT_COLLECTION_REASON_CONSENT_FLOW_REQUIRED:
            "Consent collection reason: consent flow readiness required",
        CONSENT_COLLECTION_REASON_SETUP_FOUNDATION_REQUIRED:
            "Consent collection reason: setup foundation readiness required",
        CONSENT_COLLECTION_REASON_POLICY_BLOCKED:
            "Consent collection reason: policy blocks collection",
        CONSENT_COLLECTION_REASON_DATA_VISIBILITY_BLOCKED:
            "Consent collection reason: data visibility review required",
        CONSENT_COLLECTION_REASON_AUDIT_REQUIRED:
            "Consent collection reason: audit/provenance proof required",
        CONSENT_COLLECTION_REASON_APPROVAL_MISSING:
            "Consent collection reason: USER approval missing",
        CONSENT_COLLECTION_REASON_READY_BUT_NOT_COLLECTED:
            "Consent collection reason: future capture not collected",
        CONSENT_COLLECTION_REASON_READY_FOR_FUTURE_CAPTURE_BRANCH:
            "Consent collection reason: ready for future capture branch",
        CONSENT_COLLECTION_REASON_READY_FUTURE_GATED:
            "Consent collection reason: ready but future-gated",
    }
    provenance_labels = {
        CONSENT_COLLECTION_PROVENANCE_CONSENT_FLOW:
            "Consent collection provenance: consent flow readiness state",
        CONSENT_COLLECTION_PROVENANCE_SETUP_FOUNDATION:
            "Consent collection provenance: provider setup foundation state",
        CONSENT_COLLECTION_PROVENANCE_DATA_VISIBILITY:
            "Consent collection provenance: data visibility contract",
        CONSENT_COLLECTION_PROVENANCE_AUDIT:
            "Consent collection provenance: audit policy",
        CONSENT_COLLECTION_PROVENANCE_POLICY:
            "Consent collection provenance: consent collection policy",
        CONSENT_COLLECTION_PROVENANCE_APPROVAL:
            "Consent collection provenance: future USER approval",
        CONSENT_COLLECTION_PROVENANCE_FUTURE_CAPTURE:
            "Consent collection provenance: future capture branch",
    }

    return {
        "consent_collection_foundation_state": collection_state,
        "consent_collection_foundation_label": state_labels[collection_state],
        "consent_collection_eligibility_state": collection_eligibility,
        "consent_collection_eligibility_label": eligibility_labels[collection_eligibility],
        "consent_collection_blocker_state": collection_blocker,
        "consent_collection_blocker_label": blocker_labels[collection_blocker],
        "consent_collection_reason_code": collection_reason,
        "consent_collection_reason_label": reason_labels[collection_reason],
        "consent_collection_provenance": collection_provenance,
        "consent_collection_provenance_label": provenance_labels[collection_provenance],
        "consent_collection_state_schema_version": (
            CONSENT_COLLECTION_FOUNDATION_STATE_SCHEMA_VERSION
        ),
        "consent_collection_config_schema_version": (
            CONSENT_COLLECTION_FOUNDATION_CONFIG_SCHEMA_VERSION
        ),
        "consent_collection_config_state": consent_config.config_state,
        "consent_collection_config_label": (
            "Consent collection config: local-only foundation envelope"
        ),
        "consent_collection_config_migration": (
            CONSENT_COLLECTION_FOUNDATION_CONFIG_MIGRATION_POSTURE
        ),
        "consent_collection_config_valid": consent_config.config_valid,
        "consent_collection_approval_status": collection_approval,
        "consent_collection_approval_label": {
            CONSENT_COLLECTION_APPROVAL_STATUS_MISSING:
                "Consent collection approval: USER approval missing",
            CONSENT_COLLECTION_APPROVAL_STATUS_FUTURE_GATED:
                "Consent collection approval: future-gated",
            CONSENT_COLLECTION_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF:
                "Consent collection approval: ready for future proof",
        }[collection_approval],
        "consent_collection_gate_state": collection_gate,
        "consent_capture_surface_state": capture_surface_state,
        "consent_capture_surface_label": {
            CONSENT_COLLECTION_CAPTURE_SURFACE_DISABLED:
                "Consent capture surface: disabled until USER-approved consent work",
            CONSENT_COLLECTION_CAPTURE_SURFACE_PLANNED:
                "Consent capture surface: planned only",
            CONSENT_COLLECTION_CAPTURE_SURFACE_READY_FUTURE_GATED:
                "Consent capture surface: local proof ready, future-gated",
        }[capture_surface_state],
        "setup_consent_capture_status": setup_capture_status,
        "setup_consent_capture_label": {
            CONSENT_COLLECTION_CAPTURE_SETUP_READY:
                "Setup consent capture: contract-ready, not collected",
            CONSENT_COLLECTION_CAPTURE_SETUP_REQUIRED:
                "Setup consent capture: required before collection",
        }[setup_capture_status],
        "execution_consent_capture_status": execution_capture_status,
        "execution_consent_capture_label": {
            CONSENT_COLLECTION_CAPTURE_EXECUTION_READY:
                "Execution consent capture: contract-ready, not collected",
            CONSENT_COLLECTION_CAPTURE_EXECUTION_REQUIRED:
                "Execution consent capture: required before collection",
        }[execution_capture_status],
        "consent_data_visibility_review_status": data_visibility_status,
        "consent_data_visibility_review_label": {
            CONSENT_COLLECTION_DATA_VISIBILITY_REVIEW_READY:
                "Consent data visibility review: local proof ready; provider-visible data remains none",
            CONSENT_COLLECTION_DATA_VISIBILITY_REVIEW_REQUIRED:
                "Consent data visibility review: required before capture",
        }[data_visibility_status],
        "consent_audit_envelope_status": audit_envelope_status,
        "consent_audit_envelope_label": {
            CONSENT_COLLECTION_AUDIT_ENVELOPE_READY:
                "Consent audit envelope: local proof ready",
            CONSENT_COLLECTION_AUDIT_ENVELOPE_REQUIRED:
                "Consent audit envelope: required before capture",
        }[audit_envelope_status],
        "consent_provenance_status": provenance_status,
        "consent_provenance_label": {
            CONSENT_COLLECTION_PROVENANCE_READY:
                "Consent provenance: local proof ready",
            CONSENT_COLLECTION_PROVENANCE_REQUIRED:
                "Consent provenance: required before capture",
        }[provenance_status],
        "consent_persistence_status": persistence_status,
        "consent_persistence_label": {
            CONSENT_COLLECTION_PERSISTENCE_DISABLED:
                "Consent persistence: disabled; no consent stored",
            CONSENT_COLLECTION_PERSISTENCE_LOCAL_PROOF_ONLY:
                "Consent persistence: local proof only; no user consent stored",
        }[persistence_status],
        "consent_collection_validation_status": validation_status,
        "consent_collection_validation_label": {
            CONSENT_COLLECTION_VALIDATION_FAIL_CLOSED:
                "Consent collection validation: fail-closed",
            CONSENT_COLLECTION_VALIDATION_STATIC_READY:
                "Consent collection validation: static local proof ready",
        }[validation_status],
        "future_consent_capture_handoff_state": FUTURE_CONSENT_CAPTURE_BRANCH_HANDOFF_READY,
        "consent_collection_fold_down_posture": CONSENT_COLLECTION_FOLD_DOWN_READY,
    }


def _provider_consent_capture_write_path_fields(
    collection_state: AIProviderStateSnapshot,
    consent_record: AIProviderConsentCaptureRecordSnapshot,
) -> dict[str, object]:
    ready_collection_states = {
        CONSENT_COLLECTION_STATE_READY_FUTURE_GATED,
        CONSENT_COLLECTION_STATE_READY_BUT_NOT_APPROVED,
        CONSENT_COLLECTION_STATE_READY_BUT_NOT_COLLECTED,
        CONSENT_COLLECTION_STATE_READY_FOR_FUTURE_CAPTURE_BRANCH,
    }
    capture_state = CONSENT_CAPTURE_STATE_NOT_REQUESTED
    write_status = CONSENT_CAPTURE_WRITE_STATUS_BLOCKED
    write_blocker = CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_MISSING
    write_reason = CONSENT_CAPTURE_WRITE_REASON_RECORD_MISSING
    setup_captured = False
    execution_captured = False
    snapshot_status = CONSENT_CAPTURE_LOCAL_SNAPSHOT_STATUS_EMPTY

    if collection_state.consent_collection_foundation_state not in ready_collection_states:
        capture_state = CONSENT_CAPTURE_STATE_BLOCKED_BY_COLLECTION
        write_blocker = CONSENT_CAPTURE_WRITE_BLOCKER_COLLECTION_NOT_READY
        write_reason = CONSENT_CAPTURE_WRITE_REASON_COLLECTION_NOT_READY
    elif (
        not consent_record.local_write_requested
        or consent_record.record_state == CONSENT_CAPTURE_RECORD_STATE_MISSING
    ):
        capture_state = CONSENT_CAPTURE_STATE_NOT_REQUESTED
        write_blocker = CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_MISSING
        write_reason = CONSENT_CAPTURE_WRITE_REASON_RECORD_MISSING
    elif (
        not consent_record.record_valid
        or consent_record.record_state == CONSENT_CAPTURE_RECORD_STATE_INVALID
    ):
        capture_state = CONSENT_CAPTURE_STATE_BLOCKED_BY_RECORD
        write_blocker = CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_INVALID
        write_reason = CONSENT_CAPTURE_WRITE_REASON_RECORD_INVALID
    elif consent_record.record_state == CONSENT_CAPTURE_RECORD_STATE_RESET:
        capture_state = CONSENT_CAPTURE_STATE_RESET_LOCAL_ONLY
        write_status = CONSENT_CAPTURE_WRITE_STATUS_RESET_LOCAL
        write_blocker = CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_RESET
        write_reason = CONSENT_CAPTURE_WRITE_REASON_RECORD_RESET
        snapshot_status = CONSENT_CAPTURE_LOCAL_SNAPSHOT_STATUS_READY
    elif consent_record.record_state == CONSENT_CAPTURE_RECORD_STATE_REVOKED:
        capture_state = CONSENT_CAPTURE_STATE_REVOKED_LOCAL_ONLY
        write_status = CONSENT_CAPTURE_WRITE_STATUS_REVOKED_LOCAL
        write_blocker = CONSENT_CAPTURE_WRITE_BLOCKER_RECORD_REVOKED
        write_reason = CONSENT_CAPTURE_WRITE_REASON_RECORD_REVOKED
        snapshot_status = CONSENT_CAPTURE_LOCAL_SNAPSHOT_STATUS_READY
    elif consent_record.record_state == CONSENT_CAPTURE_RECORD_STATE_NO_CONSENT_SELECTED:
        capture_state = CONSENT_CAPTURE_STATE_BLOCKED_BY_RECORD
        write_blocker = CONSENT_CAPTURE_WRITE_BLOCKER_NO_CONSENT_SELECTED
        write_reason = CONSENT_CAPTURE_WRITE_REASON_NO_CONSENT_SELECTED
    else:
        capture_state = CONSENT_CAPTURE_STATE_CAPTURED_LOCAL_ONLY
        write_status = CONSENT_CAPTURE_WRITE_STATUS_LOCAL_SNAPSHOT
        write_blocker = CONSENT_CAPTURE_WRITE_BLOCKER_NONE
        write_reason = CONSENT_CAPTURE_WRITE_REASON_CAPTURED_LOCAL_ONLY
        setup_captured = consent_record.setup_consent_granted
        execution_captured = consent_record.execution_consent_granted
        snapshot_status = CONSENT_CAPTURE_LOCAL_SNAPSHOT_STATUS_READY

    capture_labels = {
        CONSENT_CAPTURE_STATE_NOT_REQUESTED: "Consent capture: not requested",
        CONSENT_CAPTURE_STATE_BLOCKED_BY_COLLECTION:
            "Consent capture: blocked by collection foundation",
        CONSENT_CAPTURE_STATE_BLOCKED_BY_RECORD:
            "Consent capture: blocked by local record",
        CONSENT_CAPTURE_STATE_CAPTURED_LOCAL_ONLY:
            "Consent capture: local snapshot captured",
        CONSENT_CAPTURE_STATE_REVOKED_LOCAL_ONLY:
            "Consent capture: local snapshot revoked",
        CONSENT_CAPTURE_STATE_RESET_LOCAL_ONLY:
            "Consent capture: local snapshot reset",
    }
    write_labels = {
        CONSENT_CAPTURE_WRITE_STATUS_BLOCKED: "Consent write path: blocked",
        CONSENT_CAPTURE_WRITE_STATUS_LOCAL_SNAPSHOT:
            "Consent write path: local snapshot only",
        CONSENT_CAPTURE_WRITE_STATUS_REVOKED_LOCAL:
            "Consent write path: revoked local snapshot only",
        CONSENT_CAPTURE_WRITE_STATUS_RESET_LOCAL:
            "Consent write path: reset local snapshot only",
    }
    audit_status = (
        CONSENT_CAPTURE_AUDIT_STATUS_LOCAL_PROOF
        if snapshot_status == CONSENT_CAPTURE_LOCAL_SNAPSHOT_STATUS_READY
        else CONSENT_CAPTURE_AUDIT_STATUS_BLOCKED
    )
    audit_label = (
        "Consent capture audit: local snapshot proof ready"
        if audit_status == CONSENT_CAPTURE_AUDIT_STATUS_LOCAL_PROOF
        else "Consent capture audit: blocked until local proof"
    )

    return {
        "consent_capture_transition_schema_version": (
            CONSENT_CAPTURE_TRANSITION_SCHEMA_VERSION
        ),
        "consent_capture_local_record_schema_version": (
            CONSENT_CAPTURE_LOCAL_RECORD_SCHEMA_VERSION
        ),
        "consent_capture_state": capture_state,
        "consent_capture_label": capture_labels[capture_state],
        "consent_capture_record_state": consent_record.record_state,
        "consent_capture_record_valid": consent_record.record_valid,
        "consent_capture_local_write_requested": consent_record.local_write_requested,
        "consent_capture_write_status": write_status,
        "consent_capture_write_label": write_labels[write_status],
        "consent_capture_write_blocker": write_blocker,
        "consent_capture_write_reason": write_reason,
        "consent_capture_provenance": consent_record.provenance,
        "setup_consent_captured": setup_captured,
        "execution_consent_captured": execution_captured,
        "consent_capture_local_snapshot_status": snapshot_status,
        "consent_capture_durable_persistence_status": (
            CONSENT_CAPTURE_DURABLE_PERSISTENCE_DEFERRED
        ),
        "consent_record_storage_boundary_schema_version": (
            CONSENT_RECORD_STORAGE_BOUNDARY_SCHEMA_VERSION
        ),
        "consent_record_storage_boundary_state": (
            CONSENT_RECORD_STORAGE_BOUNDARY_LOCAL_SNAPSHOT_ONLY
        ),
        "consent_record_storage_boundary_label": (
            "Consent record storage boundary: local snapshot only"
        ),
        "consent_record_durable_storage_state": CONSENT_RECORD_DURABLE_STORAGE_DEFERRED,
        "consent_record_durable_storage_label": (
            "Consent record durable storage: deferred pending USER-approved storage work"
        ),
        "consent_record_revocation_model_state": (
            CONSENT_RECORD_REVOCATION_MODEL_LOCAL_ONLY
        ),
        "consent_record_revocation_model_label": (
            "Consent revocation model: local-only snapshot revocation"
        ),
        "consent_record_reset_model_state": CONSENT_RECORD_RESET_MODEL_LOCAL_ONLY,
        "consent_record_reset_model_label": (
            "Consent reset model: local-only snapshot reset"
        ),
        "consent_record_no_secrets_posture": CONSENT_RECORD_NO_SECRETS_POSTURE_READY,
        "consent_record_provider_payload_posture": (
            CONSENT_RECORD_PROVIDER_PAYLOAD_EXCLUDED
        ),
        "consent_capture_audit_schema_version": CONSENT_CAPTURE_AUDIT_SCHEMA_VERSION,
        "consent_capture_audit_status": audit_status,
        "consent_capture_audit_label": audit_label,
        "setup_execution_consent_separation_state": (
            CONSENT_CAPTURE_SETUP_EXECUTION_SEPARATION_READY
        ),
        "setup_execution_consent_separation_label": (
            "Setup and execution consent remain separate local record flags"
        ),
        "consent_capture_ui_status_proof_state": (
            CONSENT_CAPTURE_UI_STATUS_PROOF_HIDDEN_TELEMETRY
        ),
        "consent_capture_ui_status_proof_label": (
            "Consent capture UI proof: hidden telemetry only; no user-operable surface"
        ),
        "consent_capture_desktop_display_state": (
            CONSENT_CAPTURE_DESKTOP_DISPLAY_SUPPRESSED
        ),
        "consent_capture_provider_setup_handoff_state": (
            CONSENT_CAPTURE_PROVIDER_SETUP_HANDOFF_READY
        ),
        "consent_capture_functional_ai_criteria_state": (
            CONSENT_CAPTURE_FUNCTIONAL_AI_CRITERIA_PENDING
        ),
        "consent_capture_v18_continuation_state": (
            CONSENT_CAPTURE_V18_CONTINUATION_PENDING
        ),
        "consent_capture_provider_visible_data": "none",
        "consent_capture_sent_to_provider": False,
        "consent_capture_can_accept_prompts": False,
        "consent_capture_prompt_execution_state": PROMPT_EXECUTION_GATE_DISABLED,
        "consent_capture_network_egress_state": NETWORK_EGRESS_BLOCKED,
        "consent_capture_memory_state": MEMORY_INDEXING_DISABLED,
        "consent_capture_voice_state": VOICE_RUNTIME_DISABLED,
    }


def _provider_durable_consent_persistence_fields(
    durable_record: AIProviderDurableConsentRecordSnapshot,
) -> dict[str, object]:
    (
        setup_consent_state,
        setup_consent_label,
        setup_consent_reason,
    ) = _durable_consent_scope_status(durable_record, scope="setup")
    (
        execution_consent_state,
        execution_consent_label,
        execution_consent_reason,
    ) = _durable_consent_scope_status(durable_record, scope="execution")
    setup_handoff_state = (
        CONSENT_DURABLE_PROVIDER_SETUP_HANDOFF_READY
        if setup_consent_state == CONSENT_DURABLE_CONSENT_STATE_GRANTED
        else CONSENT_DURABLE_PROVIDER_SETUP_HANDOFF_BLOCKED
    )
    execution_handoff_state = (
        CONSENT_DURABLE_PROVIDER_EXECUTION_HANDOFF_READY
        if setup_consent_state == CONSENT_DURABLE_CONSENT_STATE_GRANTED
        and execution_consent_state == CONSENT_DURABLE_CONSENT_STATE_GRANTED
        else CONSENT_DURABLE_PROVIDER_EXECUTION_HANDOFF_BLOCKED
    )
    future_handoff_state = (
        CONSENT_DURABLE_FUTURE_HANDOFF_CRITERIA_READY
        if setup_consent_state == CONSENT_DURABLE_CONSENT_STATE_GRANTED
        else CONSENT_DURABLE_FUTURE_HANDOFF_CRITERIA_BLOCKED
    )
    future_handoff_label = (
        "Durable consent future handoff criteria: setup consent local proof ready"
        if future_handoff_state == CONSENT_DURABLE_FUTURE_HANDOFF_CRITERIA_READY
        else "Durable consent future handoff criteria: blocked by durable setup consent"
    )
    local_persistence_states = {
        CONSENT_DURABLE_RECORD_STATE_READY,
        CONSENT_DURABLE_RECORD_STATE_REVOKED,
        CONSENT_DURABLE_RECORD_STATE_RESET,
        CONSENT_DURABLE_RECORD_STATE_EXPIRED,
    }
    storage_state = (
        CONSENT_DURABLE_STORAGE_STATE_LOCAL_READY
        if durable_record.record_state in local_persistence_states
        else CONSENT_DURABLE_STORAGE_STATE_MISSING
        if durable_record.record_state == CONSENT_DURABLE_RECORD_STATE_MISSING
        else CONSENT_DURABLE_STORAGE_STATE_FAIL_CLOSED
    )
    storage_label = {
        CONSENT_DURABLE_STORAGE_STATE_LOCAL_READY:
            "Durable consent storage: local proof ready",
        CONSENT_DURABLE_STORAGE_STATE_MISSING:
            "Durable consent storage: missing",
        CONSENT_DURABLE_STORAGE_STATE_FAIL_CLOSED:
            "Durable consent storage: fail-closed",
    }[storage_state]
    persistence_status = (
        CONSENT_CAPTURE_DURABLE_PERSISTENCE_LOCAL_PROOF
        if storage_state == CONSENT_DURABLE_STORAGE_STATE_LOCAL_READY
        else CONSENT_CAPTURE_DURABLE_PERSISTENCE_FAIL_CLOSED
    )
    durable_storage_state = (
        CONSENT_RECORD_DURABLE_STORAGE_LOCAL_READY
        if storage_state == CONSENT_DURABLE_STORAGE_STATE_LOCAL_READY
        else CONSENT_RECORD_DURABLE_STORAGE_FAIL_CLOSED
    )
    durable_storage_label = (
        "Consent record durable storage: local proof ready"
        if durable_storage_state == CONSENT_RECORD_DURABLE_STORAGE_LOCAL_READY
        else "Consent record durable storage: fail-closed"
    )

    return {
        "consent_capture_durable_persistence_status": persistence_status,
        "consent_record_storage_boundary_schema_version": (
            CONSENT_RECORD_STORAGE_BOUNDARY_SCHEMA_VERSION
        ),
        "consent_record_storage_boundary_state": (
            CONSENT_RECORD_STORAGE_BOUNDARY_LOCAL_DURABLE_ONLY
        ),
        "consent_record_storage_boundary_label": (
            "Consent record storage boundary: local durable store only"
        ),
        "consent_record_durable_storage_state": durable_storage_state,
        "consent_record_durable_storage_label": durable_storage_label,
        "consent_record_revocation_model_state": (
            CONSENT_RECORD_REVOCATION_MODEL_LOCAL_DURABLE
        ),
        "consent_record_revocation_model_label": (
            "Consent revocation model: local durable revocation"
        ),
        "consent_record_reset_model_state": CONSENT_RECORD_RESET_MODEL_LOCAL_DURABLE,
        "consent_record_reset_model_label": "Consent reset model: local durable reset",
        "durable_consent_record_schema_version": durable_record.schema_version,
        "durable_consent_storage_boundary_schema_version": (
            CONSENT_DURABLE_STORAGE_BOUNDARY_SCHEMA_VERSION
        ),
        "durable_consent_record_state": durable_record.record_state,
        "durable_consent_record_valid": durable_record.record_valid,
        "durable_consent_record_id": durable_record.record_id,
        "durable_consent_provider_profile_id": durable_record.provider_profile_id,
        "durable_setup_consent_granted": durable_record.setup_consent_granted,
        "durable_execution_consent_granted": durable_record.execution_consent_granted,
        "durable_consent_revoked": durable_record.revoked,
        "durable_consent_reset_requested": durable_record.reset_requested,
        "durable_consent_expired": durable_record.expired,
        "durable_consent_fail_closed_reason": durable_record.fail_closed_reason,
        "durable_consent_provenance": durable_record.provenance,
        "durable_consent_audit_event_id": durable_record.audit_event_id,
        "durable_consent_migration_posture": durable_record.migration_posture,
        "durable_consent_local_storage_boundary": durable_record.storage_boundary,
        "durable_consent_storage_state": storage_state,
        "durable_consent_storage_label": storage_label,
        "durable_consent_no_secrets_posture": CONSENT_RECORD_NO_SECRETS_POSTURE_READY,
        "durable_consent_provider_payload_posture": (
            CONSENT_RECORD_PROVIDER_PAYLOAD_EXCLUDED
        ),
        "durable_setup_consent_state": setup_consent_state,
        "durable_setup_consent_label": setup_consent_label,
        "durable_setup_consent_reason_code": setup_consent_reason,
        "durable_execution_consent_state": execution_consent_state,
        "durable_execution_consent_label": execution_consent_label,
        "durable_execution_consent_reason_code": execution_consent_reason,
        "durable_setup_execution_consent_separation_state": (
            CONSENT_DURABLE_SEPARATION_STATE_READY
        ),
        "durable_setup_execution_consent_separation_label": (
            "Durable setup consent and durable execution consent are independent local states"
        ),
        "durable_consent_status_proof_state": (
            CONSENT_DURABLE_STATUS_PROOF_HIDDEN_TELEMETRY
        ),
        "durable_consent_status_proof_label": (
            "Durable consent status proof: hidden telemetry only; no user-operable consent UX"
        ),
        "durable_consent_desktop_display_state": (
            CONSENT_DURABLE_DESKTOP_DISPLAY_SUPPRESSED
        ),
        "durable_consent_provider_setup_handoff_state": setup_handoff_state,
        "durable_consent_provider_execution_handoff_state": execution_handoff_state,
        "durable_consent_future_handoff_criteria_state": future_handoff_state,
        "durable_consent_future_handoff_criteria_label": future_handoff_label,
        "consent_capture_provider_visible_data": "none",
        "consent_capture_sent_to_provider": False,
        "consent_capture_can_accept_prompts": False,
        "consent_capture_prompt_execution_state": PROMPT_EXECUTION_GATE_DISABLED,
        "consent_capture_network_egress_state": NETWORK_EGRESS_BLOCKED,
        "consent_capture_memory_state": MEMORY_INDEXING_DISABLED,
        "consent_capture_voice_state": VOICE_RUNTIME_DISABLED,
    }


def build_default_provider_consent_ux_intent() -> AIProviderConsentUxIntentSnapshot:
    """Return the fail-closed local consent UX intent default."""

    return AIProviderConsentUxIntentSnapshot(
        schema_version=CONSENT_UX_INTENT_SCHEMA_VERSION,
        setup_intent_selected=False,
        execution_intent_selected=False,
        revoke_intent_selected=False,
        reset_intent_selected=False,
        local_write_requested=False,
        surface_enabled=True,
        provenance="local_consent_ux_intent",
    )


def normalize_provider_consent_ux_intent(
    intent: AIProviderConsentUxIntentSnapshot | dict[str, object] | None,
) -> AIProviderConsentUxIntentSnapshot:
    """Normalize user-operated consent UX intent into local-only booleans."""

    if intent is None:
        return build_default_provider_consent_ux_intent()
    if isinstance(intent, AIProviderConsentUxIntentSnapshot):
        intent_payload = intent.as_dict()
    elif isinstance(intent, dict):
        intent_payload = intent
    else:
        return replace(
            build_default_provider_consent_ux_intent(),
            surface_enabled=False,
            provenance="invalid_local_consent_ux_intent",
        )

    if intent_payload.get("schema_version") != CONSENT_UX_INTENT_SCHEMA_VERSION:
        return replace(
            build_default_provider_consent_ux_intent(),
            surface_enabled=False,
            provenance="invalid_local_consent_ux_intent_schema",
        )

    def _intent_bool(field_name: str) -> bool:
        value = intent_payload.get(field_name)
        return value if isinstance(value, bool) else False

    return AIProviderConsentUxIntentSnapshot(
        schema_version=CONSENT_UX_INTENT_SCHEMA_VERSION,
        setup_intent_selected=_intent_bool("setup_intent_selected"),
        execution_intent_selected=_intent_bool("execution_intent_selected"),
        revoke_intent_selected=_intent_bool("revoke_intent_selected"),
        reset_intent_selected=_intent_bool("reset_intent_selected"),
        local_write_requested=_intent_bool("local_write_requested"),
        surface_enabled=_intent_bool("surface_enabled")
        if "surface_enabled" in intent_payload
        else True,
        provenance=str(intent_payload.get("provenance") or "local_consent_ux_intent"),
    )


def _provider_user_operated_consent_ux_fields(
    durable_state: AIProviderStateSnapshot,
    consent_intent: AIProviderConsentUxIntentSnapshot,
) -> dict[str, object]:
    record_state = durable_state.durable_consent_record_state
    setup_consent_state = durable_state.durable_setup_consent_state
    setup_consent_label = durable_state.durable_setup_consent_label
    setup_consent_reason = durable_state.durable_setup_consent_reason_code
    execution_consent_state = durable_state.durable_execution_consent_state
    execution_consent_label = durable_state.durable_execution_consent_label
    execution_consent_reason = durable_state.durable_execution_consent_reason_code
    durable_handoff_ready = record_state in {
        CONSENT_DURABLE_RECORD_STATE_READY,
        CONSENT_DURABLE_RECORD_STATE_REVOKED,
        CONSENT_DURABLE_RECORD_STATE_RESET,
        CONSENT_DURABLE_RECORD_STATE_EXPIRED,
    }
    setup_ready = setup_consent_state == CONSENT_DURABLE_CONSENT_STATE_GRANTED
    execution_ready = (
        execution_consent_state == CONSENT_DURABLE_CONSENT_STATE_GRANTED
    )
    blocked_by_invalid_record = record_state in {
        CONSENT_DURABLE_RECORD_STATE_MISSING,
        CONSENT_DURABLE_RECORD_STATE_INVALID,
        CONSENT_DURABLE_RECORD_STATE_CORRUPT,
        CONSENT_DURABLE_RECORD_STATE_UNSUPPORTED_SCHEMA,
        CONSENT_DURABLE_RECORD_STATE_STALE_SCHEMA,
    }
    if blocked_by_invalid_record:
        ux_state = CONSENT_UX_STATE_BLOCKED_BY_DURABLE_CONSENT
    elif durable_state.durable_consent_reset_requested:
        ux_state = CONSENT_UX_STATE_RESET_LOCAL_ONLY
    elif durable_state.durable_consent_revoked:
        ux_state = CONSENT_UX_STATE_REVOKED_LOCAL_ONLY
    elif durable_state.durable_consent_expired:
        ux_state = CONSENT_UX_STATE_EXPIRED_LOCAL_ONLY
    elif not (setup_ready or execution_ready):
        ux_state = CONSENT_UX_STATE_DEGRADED_FAIL_CLOSED
    else:
        ux_state = CONSENT_UX_STATE_READY_LOCAL_ONLY

    if not consent_intent.surface_enabled or blocked_by_invalid_record:
        intent_state = CONSENT_UX_INTENT_BLOCKED
    elif consent_intent.reset_intent_selected:
        intent_state = CONSENT_UX_INTENT_RESET_SELECTED
    elif consent_intent.revoke_intent_selected:
        intent_state = CONSENT_UX_INTENT_REVOKE_SELECTED
    elif consent_intent.execution_intent_selected:
        intent_state = CONSENT_UX_INTENT_EXECUTION_SELECTED
    elif consent_intent.setup_intent_selected:
        intent_state = CONSENT_UX_INTENT_SETUP_SELECTED
    else:
        intent_state = CONSENT_UX_INTENT_NONE

    surface_state = (
        CONSENT_UX_SURFACE_STATUS_ONLY_LOCAL
        if not consent_intent.surface_enabled or blocked_by_invalid_record
        else CONSENT_UX_SURFACE_CONTROLS_LOCAL_INTENT
    )
    write_posture = (
        CONSENT_UX_WRITE_LOCAL_INTENT_ONLY
        if consent_intent.local_write_requested and intent_state != CONSENT_UX_INTENT_BLOCKED
        else CONSENT_UX_WRITE_BLOCKED_FAIL_CLOSED
    )
    durable_handoff_state = (
        CONSENT_UX_DURABLE_HANDOFF_READY
        if durable_handoff_ready
        else CONSENT_UX_DURABLE_HANDOFF_BLOCKED
    )
    setup_gate_state = (
        CONSENT_UX_PROVIDER_SETUP_GATE_FUTURE_GATED
        if setup_ready
        else CONSENT_UX_PROVIDER_SETUP_GATE_BLOCKED
    )
    revocation_reset_state = (
        CONSENT_UX_STATE_BLOCKED_BY_DURABLE_CONSENT
        if blocked_by_invalid_record
        else CONSENT_UX_STATE_RESET_LOCAL_ONLY
        if durable_state.durable_consent_reset_requested
        or consent_intent.reset_intent_selected
        else CONSENT_UX_STATE_REVOKED_LOCAL_ONLY
        if durable_state.durable_consent_revoked or consent_intent.revoke_intent_selected
        else ux_state
    )

    ux_labels = {
        CONSENT_UX_STATE_BLOCKED_BY_DURABLE_CONSENT:
            "Consent UX: blocked by durable consent proof",
        CONSENT_UX_STATE_READY_LOCAL_ONLY:
            "Consent UX: local-only consent controls/status ready",
        CONSENT_UX_STATE_REVOKED_LOCAL_ONLY:
            "Consent UX: local consent revoked",
        CONSENT_UX_STATE_RESET_LOCAL_ONLY:
            "Consent UX: local consent reset requested",
        CONSENT_UX_STATE_EXPIRED_LOCAL_ONLY:
            "Consent UX: local consent expired",
        CONSENT_UX_STATE_DEGRADED_FAIL_CLOSED:
            "Consent UX: degraded and fail-closed",
    }
    intent_labels = {
        CONSENT_UX_INTENT_NONE: "Consent UX intent: none selected",
        CONSENT_UX_INTENT_SETUP_SELECTED:
            "Consent UX intent: setup consent selected locally",
        CONSENT_UX_INTENT_EXECUTION_SELECTED:
            "Consent UX intent: execution consent selected locally",
        CONSENT_UX_INTENT_REVOKE_SELECTED:
            "Consent UX intent: revoke selected locally",
        CONSENT_UX_INTENT_RESET_SELECTED:
            "Consent UX intent: reset selected locally",
        CONSENT_UX_INTENT_BLOCKED:
            "Consent UX intent: blocked fail-closed by durable state",
    }
    surface_labels = {
        CONSENT_UX_SURFACE_STATUS_ONLY_LOCAL:
            "Consent UX surface: local status only; no provider action",
        CONSENT_UX_SURFACE_CONTROLS_LOCAL_INTENT:
            "Consent UX surface: local intent controls; provider actions disabled",
    }
    write_labels = {
        CONSENT_UX_WRITE_LOCAL_INTENT_ONLY:
            "Consent UX write: local intent only; durable/provider payload unchanged",
        CONSENT_UX_WRITE_BLOCKED_FAIL_CLOSED:
            "Consent UX write: blocked fail-closed",
    }
    durable_labels = {
        CONSENT_UX_DURABLE_HANDOFF_READY:
            "Consent UX durable handoff: derived from local durable consent",
        CONSENT_UX_DURABLE_HANDOFF_BLOCKED:
            "Consent UX durable handoff: blocked by missing or invalid durable consent",
    }

    return {
        "consent_ux_state_schema_version": CONSENT_UX_STATE_SCHEMA_VERSION,
        "consent_ux_intent_schema_version": CONSENT_UX_INTENT_SCHEMA_VERSION,
        "consent_ux_state": ux_state,
        "consent_ux_label": ux_labels[ux_state],
        "consent_ux_intent_state": intent_state,
        "consent_ux_intent_label": intent_labels[intent_state],
        "consent_ux_surface_state": surface_state,
        "consent_ux_surface_label": surface_labels[surface_state],
        "consent_ux_setup_display_state": setup_consent_state,
        "consent_ux_setup_display_label": (
            setup_consent_label.replace("Durable", "Consent UX")
        ),
        "consent_ux_execution_display_state": execution_consent_state,
        "consent_ux_execution_display_label": (
            execution_consent_label.replace("Durable", "Consent UX")
        ),
        "consent_ux_revocation_reset_state": revocation_reset_state,
        "consent_ux_revocation_reset_label": (
            "Consent UX revoke/reset: local-only status derived from durable consent"
        ),
        "consent_ux_write_posture": write_posture,
        "consent_ux_write_label": write_labels[write_posture],
        "consent_ux_durable_handoff_state": durable_handoff_state,
        "consent_ux_durable_handoff_label": durable_labels[durable_handoff_state],
        "consent_ux_provider_setup_gate_state": setup_gate_state,
        "consent_ux_provider_execution_gate_state": (
            CONSENT_UX_PROVIDER_EXECUTION_GATE_DISABLED
        ),
        "consent_ux_status_proof_state": CONSENT_UX_STATUS_PROOF_STATE,
        "consent_ux_status_proof_label": (
            "Consent UX status proof: setup reason "
            f"{setup_consent_reason}; execution reason {execution_consent_reason}"
        ),
        "consent_ux_desktop_display_state": CONSENT_UX_DESKTOP_DISPLAY_SUPPRESSED,
        "consent_ux_local_only_posture": CONSENT_UX_LOCAL_ONLY_POSTURE,
        "consent_ux_provider_visible_data": "none",
        "consent_ux_sent_to_provider": False,
        "consent_ux_can_accept_prompts": False,
        "consent_ux_network_egress_state": NETWORK_EGRESS_BLOCKED,
        "consent_ux_memory_state": MEMORY_INDEXING_DISABLED,
        "consent_ux_voice_state": VOICE_RUNTIME_DISABLED,
        "consent_ux_functional_ai_criteria_state": (
            CONSENT_UX_FUNCTIONAL_AI_CRITERIA_PENDING
        ),
        "consent_ux_v18_continuation_state": CONSENT_UX_V18_CONTINUATION_PENDING,
    }


def build_provider_consent_collection_foundation_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    setup_foundation_config: AIProviderSetupFoundationConfigSnapshot | dict[str, object] | None | object = (
        _SETUP_FOUNDATION_CONFIG_OMITTED
    ),
    consent_collection_config: (
        AIProviderConsentCollectionFoundationConfigSnapshot | dict[str, object] | None | object
    ) = _CONSENT_COLLECTION_CONFIG_OMITTED,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve consent collection foundation without collecting consent."""

    setup_foundation_state = build_provider_setup_implementation_foundation_state(
        readiness_config,
        activation_config=activation_config,
        execution_config=execution_config,
        path_consent_config=path_consent_config,
        setup_foundation_config=setup_foundation_config,
        surface_role=surface_role,
    )
    if consent_collection_config is _CONSENT_COLLECTION_CONFIG_OMITTED:
        normalized_consent = build_default_provider_consent_collection_foundation_config()
    else:
        normalized_consent = normalize_provider_consent_collection_foundation_config(
            consent_collection_config  # type: ignore[arg-type]
        )
    collection_fields = _provider_consent_collection_foundation_fields(
        setup_foundation_state,
        normalized_consent,
    )
    return replace(
        setup_foundation_state,
        state_id=FAM007_PROVIDER_CONSENT_COLLECTION_FOUNDATION_STATE_ID,
        mode=FAM007_PROVIDER_CONSENT_COLLECTION_FOUNDATION_MODE,
        availability=FAM007_PROVIDER_CONSENT_COLLECTION_FOUNDATION_AVAILABILITY,
        status_label=collection_fields["consent_collection_foundation_label"],
        disabled_reason=(
            "Consent collection foundation is local-only; actual consent capture remains pending USER approval"
        ),
        provider_next_action_label="Next: consent collection foundation proof remains future-gated",
        interaction_label="Consent collection foundation only",
        interaction_disabled_reason=(
            "Consent capture, provider setup, prompt routing, and model execution require later USER approval"
        ),
        **collection_fields,
    )


def build_provider_consent_collection_implementation_foundation_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    setup_foundation_config: AIProviderSetupFoundationConfigSnapshot | dict[str, object] | None | object = (
        _SETUP_FOUNDATION_CONFIG_OMITTED
    ),
    consent_collection_config: (
        AIProviderConsentCollectionFoundationConfigSnapshot | dict[str, object] | None | object
    ) = _CONSENT_COLLECTION_CONFIG_OMITTED,
    consent_capture_record: (
        AIProviderConsentCaptureRecordSnapshot | dict[str, object] | None | object
    ) = _CONSENT_CAPTURE_RECORD_OMITTED,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve local consent capture/write-path proof without provider execution."""

    collection_state = build_provider_consent_collection_foundation_state(
        readiness_config,
        activation_config=activation_config,
        execution_config=execution_config,
        path_consent_config=path_consent_config,
        setup_foundation_config=setup_foundation_config,
        consent_collection_config=consent_collection_config,
        surface_role=surface_role,
    )
    if consent_capture_record is _CONSENT_CAPTURE_RECORD_OMITTED:
        normalized_record = build_default_provider_consent_capture_record()
    else:
        normalized_record = normalize_provider_consent_capture_record(
            consent_capture_record  # type: ignore[arg-type]
        )
    capture_fields = _provider_consent_capture_write_path_fields(
        collection_state,
        normalized_record,
    )
    return replace(
        collection_state,
        state_id=FAM007_PROVIDER_CONSENT_COLLECTION_IMPLEMENTATION_FOUNDATION_STATE_ID,
        mode=FAM007_PROVIDER_CONSENT_COLLECTION_IMPLEMENTATION_FOUNDATION_MODE,
        availability=(
            FAM007_PROVIDER_CONSENT_COLLECTION_IMPLEMENTATION_FOUNDATION_AVAILABILITY
        ),
        status_label=capture_fields["consent_capture_label"],
        disabled_reason=(
            "Consent capture write-path foundation is local-only; provider setup and execution remain pending USER approval"
        ),
        provider_next_action_label=(
            "Next: hardening validates local-only consent capture before provider setup remains future-gated"
        ),
        interaction_label="Consent capture write-path foundation only",
        interaction_disabled_reason=(
            "Local consent capture does not enable provider setup, prompt routing, or model execution"
        ),
        **capture_fields,
    )


def build_provider_durable_consent_persistence_foundation_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    setup_foundation_config: AIProviderSetupFoundationConfigSnapshot | dict[str, object] | None | object = (
        _SETUP_FOUNDATION_CONFIG_OMITTED
    ),
    consent_collection_config: (
        AIProviderConsentCollectionFoundationConfigSnapshot | dict[str, object] | None | object
    ) = _CONSENT_COLLECTION_CONFIG_OMITTED,
    consent_capture_record: (
        AIProviderConsentCaptureRecordSnapshot | dict[str, object] | None | object
    ) = _CONSENT_CAPTURE_RECORD_OMITTED,
    durable_consent_record: (
        AIProviderDurableConsentRecordSnapshot | dict[str, object] | None | object
    ) = _DURABLE_CONSENT_RECORD_OMITTED,
    durable_consent_store_dir: str | Path | None = None,
    now_utc: datetime | None = None,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve durable local consent persistence without provider execution."""

    capture_state = build_provider_consent_collection_implementation_foundation_state(
        readiness_config,
        activation_config=activation_config,
        execution_config=execution_config,
        path_consent_config=path_consent_config,
        setup_foundation_config=setup_foundation_config,
        consent_collection_config=consent_collection_config,
        consent_capture_record=consent_capture_record,
        surface_role=surface_role,
    )
    if durable_consent_record is _DURABLE_CONSENT_RECORD_OMITTED:
        normalized_durable_record = (
            load_provider_durable_consent_record(
                durable_consent_store_dir,
                now_utc=now_utc,
            )
            if durable_consent_store_dir is not None
            else build_default_provider_durable_consent_record()
        )
    else:
        normalized_durable_record = normalize_provider_durable_consent_record(
            durable_consent_record,  # type: ignore[arg-type]
            now_utc=now_utc,
        )
    durable_fields = _provider_durable_consent_persistence_fields(
        normalized_durable_record
    )
    return replace(
        capture_state,
        state_id=FAM007_PROVIDER_DURABLE_CONSENT_PERSISTENCE_FOUNDATION_STATE_ID,
        mode=FAM007_PROVIDER_DURABLE_CONSENT_PERSISTENCE_FOUNDATION_MODE,
        availability=(
            FAM007_PROVIDER_DURABLE_CONSENT_PERSISTENCE_FOUNDATION_AVAILABILITY
        ),
        status_label=durable_fields["durable_consent_storage_label"],
        disabled_reason=(
            "Durable consent persistence is local-only; provider setup and execution remain pending USER approval"
        ),
        provider_next_action_label=(
            "Next: validate durable local consent persistence before user-operated consent UX"
        ),
        interaction_label="Durable consent persistence foundation only",
        interaction_disabled_reason=(
            "Durable consent persistence does not enable provider setup, prompt routing, or model execution"
        ),
        **durable_fields,
    )


def build_provider_user_operated_consent_ux_foundation_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    setup_foundation_config: AIProviderSetupFoundationConfigSnapshot | dict[str, object] | None | object = (
        _SETUP_FOUNDATION_CONFIG_OMITTED
    ),
    consent_collection_config: (
        AIProviderConsentCollectionFoundationConfigSnapshot | dict[str, object] | None | object
    ) = _CONSENT_COLLECTION_CONFIG_OMITTED,
    consent_capture_record: (
        AIProviderConsentCaptureRecordSnapshot | dict[str, object] | None | object
    ) = _CONSENT_CAPTURE_RECORD_OMITTED,
    durable_consent_record: (
        AIProviderDurableConsentRecordSnapshot | dict[str, object] | None | object
    ) = _DURABLE_CONSENT_RECORD_OMITTED,
    consent_ux_intent: (
        AIProviderConsentUxIntentSnapshot | dict[str, object] | None | object
    ) = _CONSENT_UX_INTENT_OMITTED,
    durable_consent_store_dir: str | Path | None = None,
    now_utc: datetime | None = None,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve user-operated local consent UX without provider execution."""

    durable_state = build_provider_durable_consent_persistence_foundation_state(
        readiness_config,
        activation_config=activation_config,
        execution_config=execution_config,
        path_consent_config=path_consent_config,
        setup_foundation_config=setup_foundation_config,
        consent_collection_config=consent_collection_config,
        consent_capture_record=consent_capture_record,
        durable_consent_record=durable_consent_record,
        durable_consent_store_dir=durable_consent_store_dir,
        now_utc=now_utc,
        surface_role=surface_role,
    )
    if consent_ux_intent is _CONSENT_UX_INTENT_OMITTED:
        normalized_intent = build_default_provider_consent_ux_intent()
    else:
        normalized_intent = normalize_provider_consent_ux_intent(
            consent_ux_intent  # type: ignore[arg-type]
        )
    consent_ux_fields = _provider_user_operated_consent_ux_fields(
        durable_state,
        normalized_intent,
    )
    return replace(
        durable_state,
        state_id=FAM007_PROVIDER_USER_OPERATED_CONSENT_UX_FOUNDATION_STATE_ID,
        mode=FAM007_PROVIDER_USER_OPERATED_CONSENT_UX_FOUNDATION_MODE,
        availability=(
            FAM007_PROVIDER_USER_OPERATED_CONSENT_UX_FOUNDATION_AVAILABILITY
        ),
        status_label=consent_ux_fields["consent_ux_label"],
        disabled_reason=(
            "User-operated consent UX is local-only; provider setup and execution remain pending USER approval"
        ),
        provider_next_action_label=(
            "Next: validate local consent UX before provider setup completion remains future-gated"
        ),
        interaction_label="User-operated local consent UX foundation only",
        interaction_disabled_reason=(
            "Consent UX records local intent/status only and does not enable provider setup, prompt routing, or model execution"
        ),
        **consent_ux_fields,
    )


def build_default_provider_setup_completion_config() -> AIProviderSetupCompletionConfigSnapshot:
    """Return the fail-closed local setup completion default."""

    return AIProviderSetupCompletionConfigSnapshot(
        schema_version=SETUP_COMPLETION_CONFIG_SCHEMA_VERSION,
        config_state=PROVIDER_PATH_CONFIG_STATE_DEFAULT,
        setup_completion_approved=False,
        provider_profile_finalized=False,
        provider_profile_valid=False,
        provider_config_finalized=False,
        provider_config_valid=False,
        no_secrets_validated=False,
        local_persistence_ready=False,
        validation_passed=False,
        reset_requested=False,
        future_sdk_handoff_ready=False,
        config_valid=True,
        provenance=SETUP_COMPLETION_PROVENANCE_CONSENT_UX,
    )


def normalize_provider_setup_completion_config(
    config: AIProviderSetupCompletionConfigSnapshot | dict[str, object] | None,
) -> AIProviderSetupCompletionConfigSnapshot:
    """Normalize local setup completion config into fail-closed booleans."""

    provenance_sources = {
        SETUP_COMPLETION_PROVENANCE_CONSENT_UX,
        SETUP_COMPLETION_PROVENANCE_PROFILE,
        SETUP_COMPLETION_PROVENANCE_CONFIG,
        SETUP_COMPLETION_PROVENANCE_NO_SECRETS,
        SETUP_COMPLETION_PROVENANCE_VALIDATION,
        SETUP_COMPLETION_PROVENANCE_RESET,
        SETUP_COMPLETION_PROVENANCE_HANDOFF,
    }

    if config is None:
        return replace(
            build_default_provider_setup_completion_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_MISSING,
            config_valid=False,
            provenance=SETUP_COMPLETION_PROVENANCE_CONFIG,
        )

    if isinstance(config, AIProviderSetupCompletionConfigSnapshot):
        if (
            config.schema_version == SETUP_COMPLETION_CONFIG_SCHEMA_VERSION
            and config.config_valid
        ):
            return config
        return replace(
            build_default_provider_setup_completion_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=config.provenance
            if config.provenance in provenance_sources
            else SETUP_COMPLETION_PROVENANCE_VALIDATION,
        )

    if not isinstance(config, dict):
        return replace(
            build_default_provider_setup_completion_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=SETUP_COMPLETION_PROVENANCE_VALIDATION,
        )

    schema_version = str(config.get("schema_version") or "")
    provenance = str(config.get("provenance") or SETUP_COMPLETION_PROVENANCE_CONFIG)
    config_valid = (
        bool(config.get("config_valid", True))
        and schema_version == SETUP_COMPLETION_CONFIG_SCHEMA_VERSION
    )
    if not config_valid:
        return replace(
            build_default_provider_setup_completion_config(),
            config_state=PROVIDER_PATH_CONFIG_STATE_INVALID,
            config_valid=False,
            provenance=provenance
            if provenance in provenance_sources
            else SETUP_COMPLETION_PROVENANCE_VALIDATION,
        )

    return AIProviderSetupCompletionConfigSnapshot(
        schema_version=schema_version,
        config_state=PROVIDER_PATH_CONFIG_STATE_LOCAL,
        setup_completion_approved=bool(
            config.get("setup_completion_approved", False)
        ),
        provider_profile_finalized=bool(
            config.get("provider_profile_finalized", False)
        ),
        provider_profile_valid=bool(config.get("provider_profile_valid", False)),
        provider_config_finalized=bool(
            config.get("provider_config_finalized", False)
        ),
        provider_config_valid=bool(config.get("provider_config_valid", False)),
        no_secrets_validated=bool(config.get("no_secrets_validated", False)),
        local_persistence_ready=bool(config.get("local_persistence_ready", False)),
        validation_passed=bool(config.get("validation_passed", False)),
        reset_requested=bool(config.get("reset_requested", False)),
        future_sdk_handoff_ready=bool(
            config.get("future_sdk_handoff_ready", False)
        ),
        config_valid=True,
        provenance=provenance
        if provenance in provenance_sources
        else SETUP_COMPLETION_PROVENANCE_CONFIG,
    )


def _provider_setup_completion_fields(
    consent_ux_state: AIProviderStateSnapshot,
    setup_completion_config: AIProviderSetupCompletionConfigSnapshot,
) -> dict[str, object]:
    setup_consent_state = consent_ux_state.consent_ux_setup_display_state
    execution_consent_state = consent_ux_state.consent_ux_execution_display_state
    setup_consent_label = consent_ux_state.consent_ux_setup_display_label.replace(
        "Consent UX", "Setup completion"
    )
    execution_consent_label = (
        consent_ux_state.consent_ux_execution_display_label.replace(
            "Consent UX", "Setup completion"
        )
    )
    consent_ux_setup_ready = (
        consent_ux_state.consent_ux_provider_setup_gate_state
        == CONSENT_UX_PROVIDER_SETUP_GATE_FUTURE_GATED
    )
    profile_status = (
        SETUP_COMPLETION_PROFILE_FINALIZED
        if setup_completion_config.provider_profile_finalized
        and setup_completion_config.provider_profile_valid
        else SETUP_COMPLETION_PROFILE_INVALID
        if setup_completion_config.provider_profile_finalized
        else SETUP_COMPLETION_PROFILE_MISSING
    )
    config_status = (
        SETUP_COMPLETION_CONFIG_FINALIZED
        if setup_completion_config.provider_config_finalized
        and setup_completion_config.provider_config_valid
        else SETUP_COMPLETION_CONFIG_INVALID
        if setup_completion_config.provider_config_finalized
        else SETUP_COMPLETION_CONFIG_MISSING
    )
    no_secrets_status = (
        SETUP_COMPLETION_NO_SECRETS_READY
        if setup_completion_config.no_secrets_validated
        else SETUP_COMPLETION_NO_SECRETS_BLOCKED
    )
    validation_status = (
        SETUP_COMPLETION_VALIDATION_LOCAL_READY
        if setup_completion_config.validation_passed
        and profile_status == SETUP_COMPLETION_PROFILE_FINALIZED
        and config_status == SETUP_COMPLETION_CONFIG_FINALIZED
        and no_secrets_status == SETUP_COMPLETION_NO_SECRETS_READY
        and setup_completion_config.local_persistence_ready
        else SETUP_COMPLETION_VALIDATION_FAIL_CLOSED
    )
    persistence_status = (
        SETUP_COMPLETION_PERSISTENCE_LOCAL_METADATA_ONLY
        if setup_completion_config.local_persistence_ready
        else SETUP_COMPLETION_PERSISTENCE_BLOCKED
    )
    reset_state = (
        SETUP_COMPLETION_RESET_REQUESTED
        if setup_completion_config.reset_requested
        else SETUP_COMPLETION_RESET_NONE
    )

    completion_state = SETUP_COMPLETION_STATE_UNAVAILABLE
    completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_UNAVAILABLE
    completion_blocker = SETUP_COMPLETION_BLOCKER_CONSENT_UX_REQUIRED
    completion_reason = SETUP_COMPLETION_REASON_DEFAULT_UNAVAILABLE
    completion_provenance = SETUP_COMPLETION_PROVENANCE_CONSENT_UX
    setup_gate_state = SETUP_COMPLETION_PROVIDER_SETUP_GATE_BLOCKED
    sdk_handoff_state = SETUP_COMPLETION_SDK_HANDOFF_BLOCKED

    if setup_completion_config.config_state == PROVIDER_PATH_CONFIG_STATE_MISSING:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_CONFIG
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_CONFIG_FINALIZATION_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_CONFIG_MISSING
        completion_provenance = SETUP_COMPLETION_PROVENANCE_CONFIG
    elif setup_completion_config.config_state == PROVIDER_PATH_CONFIG_STATE_INVALID:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_VALIDATION
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_VALIDATION_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_CONFIG_INVALID
        completion_provenance = SETUP_COMPLETION_PROVENANCE_VALIDATION
    elif not consent_ux_setup_ready:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_CONSENT_UX
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_reason = SETUP_COMPLETION_REASON_CONSENT_UX_REQUIRED
    elif profile_status == SETUP_COMPLETION_PROFILE_MISSING:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_PROFILE
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_PROFILE_FINALIZATION_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_PROFILE_MISSING
        completion_provenance = SETUP_COMPLETION_PROVENANCE_PROFILE
    elif profile_status == SETUP_COMPLETION_PROFILE_INVALID:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_PROFILE
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_PROFILE_FINALIZATION_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_PROFILE_INVALID
        completion_provenance = SETUP_COMPLETION_PROVENANCE_PROFILE
    elif config_status == SETUP_COMPLETION_CONFIG_MISSING:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_CONFIG
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_CONFIG_FINALIZATION_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_CONFIG_MISSING
        completion_provenance = SETUP_COMPLETION_PROVENANCE_CONFIG
    elif config_status == SETUP_COMPLETION_CONFIG_INVALID:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_CONFIG
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_CONFIG_FINALIZATION_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_CONFIG_INVALID
        completion_provenance = SETUP_COMPLETION_PROVENANCE_CONFIG
    elif no_secrets_status != SETUP_COMPLETION_NO_SECRETS_READY:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_NO_SECRETS
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_NO_SECRETS_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_NO_SECRETS_FAILED
        completion_provenance = SETUP_COMPLETION_PROVENANCE_NO_SECRETS
    elif setup_completion_config.reset_requested:
        completion_state = SETUP_COMPLETION_STATE_RESET_LOCAL_ONLY
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_RESET
        completion_blocker = SETUP_COMPLETION_BLOCKER_RESET_REQUESTED
        completion_reason = SETUP_COMPLETION_REASON_RESET_REQUESTED
        completion_provenance = SETUP_COMPLETION_PROVENANCE_RESET
    elif validation_status != SETUP_COMPLETION_VALIDATION_LOCAL_READY:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_VALIDATION
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_VALIDATION_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_VALIDATION_FAILED
        completion_provenance = SETUP_COMPLETION_PROVENANCE_VALIDATION
    elif setup_completion_config.future_sdk_handoff_ready:
        completion_state = SETUP_COMPLETION_STATE_READY_FOR_FUTURE_SDK_HANDOFF
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_FUTURE_HANDOFF
        completion_blocker = SETUP_COMPLETION_BLOCKER_FUTURE_SDK_HANDOFF
        completion_reason = SETUP_COMPLETION_REASON_READY_FOR_FUTURE_SDK_HANDOFF
        completion_provenance = SETUP_COMPLETION_PROVENANCE_HANDOFF
        setup_gate_state = SETUP_COMPLETION_PROVIDER_SETUP_GATE_FUTURE_GATED
        sdk_handoff_state = SETUP_COMPLETION_SDK_HANDOFF_READY_FUTURE_GATED
    elif setup_completion_config.setup_completion_approved:
        completion_state = SETUP_COMPLETION_STATE_READY_LOCAL_ONLY
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_LOCAL_READY
        completion_blocker = SETUP_COMPLETION_BLOCKER_FUTURE_SDK_HANDOFF
        completion_reason = SETUP_COMPLETION_REASON_READY_LOCAL_ONLY
        completion_provenance = SETUP_COMPLETION_PROVENANCE_VALIDATION
        setup_gate_state = SETUP_COMPLETION_PROVIDER_SETUP_GATE_FUTURE_GATED
    else:
        completion_state = SETUP_COMPLETION_STATE_BLOCKED_BY_VALIDATION
        completion_eligibility = SETUP_COMPLETION_ELIGIBILITY_BLOCKED
        completion_blocker = SETUP_COMPLETION_BLOCKER_VALIDATION_REQUIRED
        completion_reason = SETUP_COMPLETION_REASON_VALIDATION_FAILED
        completion_provenance = SETUP_COMPLETION_PROVENANCE_VALIDATION

    completion_labels = {
        SETUP_COMPLETION_STATE_UNAVAILABLE: "Setup completion: unavailable",
        SETUP_COMPLETION_STATE_BLOCKED_BY_CONSENT_UX:
            "Setup completion: blocked by consent UX setup consent",
        SETUP_COMPLETION_STATE_BLOCKED_BY_PROFILE:
            "Setup completion: blocked by provider profile finalization",
        SETUP_COMPLETION_STATE_BLOCKED_BY_CONFIG:
            "Setup completion: blocked by provider config finalization",
        SETUP_COMPLETION_STATE_BLOCKED_BY_NO_SECRETS:
            "Setup completion: blocked by no-secrets validation",
        SETUP_COMPLETION_STATE_BLOCKED_BY_VALIDATION:
            "Setup completion: validation failed closed",
        SETUP_COMPLETION_STATE_RESET_LOCAL_ONLY:
            "Setup completion: local reset requested",
        SETUP_COMPLETION_STATE_READY_LOCAL_ONLY:
            "Setup completion: local-only foundation ready",
        SETUP_COMPLETION_STATE_READY_FOR_FUTURE_SDK_HANDOFF:
            "Setup completion: ready for future SDK handoff",
    }
    eligibility_labels = {
        SETUP_COMPLETION_ELIGIBILITY_UNAVAILABLE:
            "Setup completion eligibility: unavailable",
        SETUP_COMPLETION_ELIGIBILITY_BLOCKED:
            "Setup completion eligibility: blocked",
        SETUP_COMPLETION_ELIGIBILITY_RESET:
            "Setup completion eligibility: reset local-only",
        SETUP_COMPLETION_ELIGIBILITY_LOCAL_READY:
            "Setup completion eligibility: local-only ready",
        SETUP_COMPLETION_ELIGIBILITY_FUTURE_HANDOFF:
            "Setup completion eligibility: future SDK handoff gated",
    }
    blocker_labels = {
        SETUP_COMPLETION_BLOCKER_CONSENT_UX_REQUIRED:
            "Setup completion blocker: setup consent UX proof required",
        SETUP_COMPLETION_BLOCKER_PROFILE_FINALIZATION_REQUIRED:
            "Setup completion blocker: provider profile finalization required",
        SETUP_COMPLETION_BLOCKER_CONFIG_FINALIZATION_REQUIRED:
            "Setup completion blocker: provider config finalization required",
        SETUP_COMPLETION_BLOCKER_NO_SECRETS_REQUIRED:
            "Setup completion blocker: no-secrets validation required",
        SETUP_COMPLETION_BLOCKER_VALIDATION_REQUIRED:
            "Setup completion blocker: local validation proof required",
        SETUP_COMPLETION_BLOCKER_RESET_REQUESTED:
            "Setup completion blocker: local reset requested",
        SETUP_COMPLETION_BLOCKER_FUTURE_SDK_HANDOFF:
            "Setup completion blocker: future SDK handoff still requires USER approval",
        SETUP_COMPLETION_BLOCKER_NONE:
            "Setup completion blocker: none",
    }
    reason_labels = {
        SETUP_COMPLETION_REASON_DEFAULT_UNAVAILABLE:
            "Setup completion reason: local-only safe default",
        SETUP_COMPLETION_REASON_CONSENT_UX_REQUIRED:
            "Setup completion reason: setup consent must be present in local consent UX",
        SETUP_COMPLETION_REASON_PROFILE_MISSING:
            "Setup completion reason: provider profile finalization missing",
        SETUP_COMPLETION_REASON_PROFILE_INVALID:
            "Setup completion reason: provider profile finalization invalid",
        SETUP_COMPLETION_REASON_CONFIG_MISSING:
            "Setup completion reason: provider config finalization missing",
        SETUP_COMPLETION_REASON_CONFIG_INVALID:
            "Setup completion reason: provider config finalization invalid",
        SETUP_COMPLETION_REASON_NO_SECRETS_FAILED:
            "Setup completion reason: no-secrets posture not validated",
        SETUP_COMPLETION_REASON_VALIDATION_FAILED:
            "Setup completion reason: local setup completion validation failed",
        SETUP_COMPLETION_REASON_RESET_REQUESTED:
            "Setup completion reason: reset returns setup completion to blocked",
        SETUP_COMPLETION_REASON_READY_LOCAL_ONLY:
            "Setup completion reason: local setup completion foundation ready",
        SETUP_COMPLETION_REASON_READY_FOR_FUTURE_SDK_HANDOFF:
            "Setup completion reason: future SDK handoff criteria recorded",
    }
    provenance_labels = {
        SETUP_COMPLETION_PROVENANCE_CONSENT_UX:
            "Setup completion provenance: user-operated consent UX state",
        SETUP_COMPLETION_PROVENANCE_PROFILE:
            "Setup completion provenance: provider profile finalization",
        SETUP_COMPLETION_PROVENANCE_CONFIG:
            "Setup completion provenance: provider config finalization",
        SETUP_COMPLETION_PROVENANCE_NO_SECRETS:
            "Setup completion provenance: no-secrets validation",
        SETUP_COMPLETION_PROVENANCE_VALIDATION:
            "Setup completion provenance: local validation proof",
        SETUP_COMPLETION_PROVENANCE_RESET:
            "Setup completion provenance: local reset request",
        SETUP_COMPLETION_PROVENANCE_HANDOFF:
            "Setup completion provenance: future provider SDK handoff",
    }

    return {
        "provider_setup_completion_state_schema_version": (
            SETUP_COMPLETION_STATE_SCHEMA_VERSION
        ),
        "provider_setup_completion_config_schema_version": (
            SETUP_COMPLETION_CONFIG_SCHEMA_VERSION
        ),
        "provider_setup_completion_state": completion_state,
        "provider_setup_completion_label": completion_labels[completion_state],
        "provider_setup_completion_eligibility_state": completion_eligibility,
        "provider_setup_completion_eligibility_label": (
            eligibility_labels[completion_eligibility]
        ),
        "provider_setup_completion_blocker_state": completion_blocker,
        "provider_setup_completion_blocker_label": blocker_labels[completion_blocker],
        "provider_setup_completion_reason_code": completion_reason,
        "provider_setup_completion_reason_label": reason_labels[completion_reason],
        "provider_setup_completion_provenance": completion_provenance,
        "provider_setup_completion_provenance_label": (
            provenance_labels[completion_provenance]
        ),
        "provider_setup_completion_config_state": (
            setup_completion_config.config_state
        ),
        "provider_setup_completion_config_label": (
            "Setup completion config: local-only finalization envelope"
        ),
        "provider_setup_completion_config_migration": (
            SETUP_COMPLETION_CONFIG_MIGRATION_POSTURE
        ),
        "provider_setup_completion_config_valid": (
            setup_completion_config.config_valid
        ),
        "provider_setup_completion_profile_status": profile_status,
        "provider_setup_completion_profile_label": {
            SETUP_COMPLETION_PROFILE_MISSING:
                "Setup completion profile: missing local finalization",
            SETUP_COMPLETION_PROFILE_INVALID:
                "Setup completion profile: invalid local finalization",
            SETUP_COMPLETION_PROFILE_FINALIZED:
                "Setup completion profile: finalized local-only",
        }[profile_status],
        "provider_setup_completion_config_status": config_status,
        "provider_setup_completion_config_status_label": {
            SETUP_COMPLETION_CONFIG_MISSING:
                "Setup completion config finalization: missing",
            SETUP_COMPLETION_CONFIG_INVALID:
                "Setup completion config finalization: invalid",
            SETUP_COMPLETION_CONFIG_FINALIZED:
                "Setup completion config finalization: finalized local-only",
        }[config_status],
        "provider_setup_completion_no_secrets_status": no_secrets_status,
        "provider_setup_completion_no_secrets_label": {
            SETUP_COMPLETION_NO_SECRETS_BLOCKED:
                "Setup completion no-secrets posture: blocked",
            SETUP_COMPLETION_NO_SECRETS_READY:
                "Setup completion no-secrets posture: validated",
        }[no_secrets_status],
        "provider_setup_completion_validation_status": validation_status,
        "provider_setup_completion_validation_label": {
            SETUP_COMPLETION_VALIDATION_FAIL_CLOSED:
                "Setup completion validation: fail-closed",
            SETUP_COMPLETION_VALIDATION_LOCAL_READY:
                "Setup completion validation: local proof ready",
        }[validation_status],
        "provider_setup_completion_persistence_status": persistence_status,
        "provider_setup_completion_persistence_label": {
            SETUP_COMPLETION_PERSISTENCE_BLOCKED:
                "Setup completion persistence: blocked",
            SETUP_COMPLETION_PERSISTENCE_LOCAL_METADATA_ONLY:
                "Setup completion persistence: local metadata only; no secrets",
        }[persistence_status],
        "provider_setup_completion_reset_state": reset_state,
        "provider_setup_completion_reset_label": {
            SETUP_COMPLETION_RESET_NONE: "Setup completion reset: none",
            SETUP_COMPLETION_RESET_REQUESTED:
                "Setup completion reset: requested locally; fail-closed",
        }[reset_state],
        "provider_setup_completion_setup_consent_state": setup_consent_state,
        "provider_setup_completion_setup_consent_label": setup_consent_label,
        "provider_setup_completion_execution_consent_state": execution_consent_state,
        "provider_setup_completion_execution_consent_label": execution_consent_label,
        "provider_setup_completion_status_proof_state": (
            SETUP_COMPLETION_STATUS_PROOF_PUBLIC_LOCAL_ASSIST
        ),
        "provider_setup_completion_status_proof_label": (
            "Setup completion status proof: public local assist derived from consent UX "
            f"and reason {completion_reason}"
        ),
        "provider_setup_completion_desktop_display_state": (
            SETUP_COMPLETION_DESKTOP_DISPLAY_VISIBLE
        ),
        "provider_setup_completion_provider_setup_gate_state": setup_gate_state,
        "provider_setup_completion_provider_execution_gate_state": (
            SETUP_COMPLETION_PROVIDER_EXECUTION_GATE_DISABLED
        ),
        "provider_setup_completion_sdk_handoff_state": sdk_handoff_state,
        "provider_setup_completion_sdk_handoff_label": {
            SETUP_COMPLETION_SDK_HANDOFF_BLOCKED:
                "Setup completion SDK handoff: blocked pending future USER approval",
            SETUP_COMPLETION_SDK_HANDOFF_READY_FUTURE_GATED:
                "Setup completion SDK handoff: ready but future-gated",
        }[sdk_handoff_state],
        "provider_setup_completion_functional_ai_criteria_state": (
            SETUP_COMPLETION_FUNCTIONAL_AI_CRITERIA_PENDING
        ),
        "provider_setup_completion_v18_continuation_state": (
            SETUP_COMPLETION_V18_CONTINUATION_PENDING
        ),
        "provider_setup_completion_provider_visible_data": "none",
        "provider_setup_completion_sent_to_provider": False,
        "provider_setup_completion_can_accept_prompts": False,
        "provider_setup_completion_network_egress_state": NETWORK_EGRESS_BLOCKED,
        "provider_setup_completion_memory_state": MEMORY_INDEXING_DISABLED,
        "provider_setup_completion_voice_state": VOICE_RUNTIME_DISABLED,
    }


def build_local_ai_readiness_report() -> dict[str, object]:
    """Build the public-safe local AI readiness report without provider execution."""

    ready_conditions = (
        {
            "id": "provider-visible-data-none",
            "label": "Provider-visible data is none",
            "evidence": "providerVisibleData=none; sentToProvider=false",
        },
        {
            "id": "prompt-send-disabled",
            "label": "Prompt acceptance and prompt send are disabled",
            "evidence": "canAcceptPrompts=false; promptSendPosture=prompt-send-disabled",
        },
        {
            "id": "local-null-provider-boundary",
            "label": "Local/null provider boundary is active",
            "evidence": "provider profile is local/null and provider execution is disabled",
        },
        {
            "id": "public-lane-visible",
            "label": "Public Edition boundary is visible",
            "evidence": "Developer and Owner lanes remain gated",
        },
    )
    missing_requirements = (
        {
            "id": "provider-setup-approval",
            "label": "Provider setup approval is not granted",
            "reason": "Provider/model execution requires a later USER action gate",
        },
        {
            "id": "capability-proof",
            "label": "Capability-pack proof is not available",
            "reason": "Hardware, manifest, source, and compatibility proof are future-gated",
        },
        {
            "id": "private-lane-setup",
            "label": "Developer and Owner private setup are not configured",
            "reason": "Private roots, remotes, prompts, memory, and assets are excluded",
        },
    )
    blocked_paths = (
        {
            "id": "provider-model-execution",
            "label": "Provider/model execution",
            "state": "blocked",
            "gate": "USER-ACTION-FAM007-PROVIDER-MODEL-EXECUTION",
        },
        {
            "id": "prompt-send",
            "label": "Prompt send",
            "state": "disabled",
            "gate": "future provider/model approval",
        },
        {
            "id": "downloads-install",
            "label": "Downloads, install, update, and uninstall",
            "state": "blocked",
            "gate": "future capability-pack/FAM-008 approval",
        },
        {
            "id": "runtime-cache-memory",
            "label": "Runtime cache, memory, learning, and personalization",
            "state": "blocked",
            "gate": "future cache or memory USER approval",
        },
        {
            "id": "private-setup",
            "label": "Private Developer/Owner setup",
            "state": "blocked",
            "gate": "future private setup USER approval",
        },
    )
    local_evidence_checked = (
        "provider boundary payload",
        "prompt/model/provider execution gates",
        "network egress gate",
        "memory/indexing gate",
        "capability-pack install/download posture",
        "Public/Developer/Owner lane boundary posture",
    )
    safe_next_steps = (
        "Use this report as the local readiness summary for the current public-safe state.",
        "Keep provider-visible data at none until a future provider/model setup gate is approved.",
        "Treat capability-pack, cache, memory, private setup, and packaging paths as future-gated.",
    )
    trust_boundaries = (
        "No prompt is accepted or sent.",
        "No provider or model executes.",
        "No download, install, runtime cache, memory, learning, personalization, or private setup path runs.",
        "No hidden network behavior is authorized.",
    )
    return {
        "schemaVersion": LOCAL_AI_READINESS_REPORT_SCHEMA_VERSION,
        "state": LOCAL_AI_READINESS_REPORT_STATE_READY,
        "title": "Local AI Readiness Report",
        "summary": (
            "Local AI readiness is public-safe but not provider-ready: local boundary proof is ready, "
            "provider/model execution remains blocked, and no data leaves the machine."
        ),
        "generatedBy": "FAM-007 AI Control Center local deterministic report",
        "providerVisibleData": "none",
        "sentToProvider": False,
        "canAcceptPrompts": False,
        "promptSendPosture": PROMPT_SEND_POSTURE_DISABLED,
        "networkEgressState": NETWORK_EGRESS_BLOCKED,
        "memoryIndexingState": MEMORY_INDEXING_DISABLED,
        "copyMode": LOCAL_AI_READINESS_REPORT_COPY_MODE,
        "persistence": LOCAL_AI_READINESS_REPORT_PERSISTENCE,
        "readyConditions": tuple(dict(item) for item in ready_conditions),
        "missingRequirements": tuple(dict(item) for item in missing_requirements),
        "blockedPaths": tuple(dict(item) for item in blocked_paths),
        "localEvidenceChecked": local_evidence_checked,
        "safeNextSteps": safe_next_steps,
        "trustBoundaries": trust_boundaries,
        "usefulOutcome": (
            "The USER can decide what is locally ready, what is missing, what remains blocked, "
            "and which safe next steps exist before any provider/model/capability work is approved."
        ),
    }


def build_provider_setup_completion_foundation_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    setup_foundation_config: AIProviderSetupFoundationConfigSnapshot | dict[str, object] | None | object = (
        _SETUP_FOUNDATION_CONFIG_OMITTED
    ),
    consent_collection_config: (
        AIProviderConsentCollectionFoundationConfigSnapshot | dict[str, object] | None | object
    ) = _CONSENT_COLLECTION_CONFIG_OMITTED,
    consent_capture_record: (
        AIProviderConsentCaptureRecordSnapshot | dict[str, object] | None | object
    ) = _CONSENT_CAPTURE_RECORD_OMITTED,
    durable_consent_record: (
        AIProviderDurableConsentRecordSnapshot | dict[str, object] | None | object
    ) = _DURABLE_CONSENT_RECORD_OMITTED,
    consent_ux_intent: (
        AIProviderConsentUxIntentSnapshot | dict[str, object] | None | object
    ) = _CONSENT_UX_INTENT_OMITTED,
    setup_completion_config: (
        AIProviderSetupCompletionConfigSnapshot | dict[str, object] | None | object
    ) = _SETUP_COMPLETION_CONFIG_OMITTED,
    durable_consent_store_dir: str | Path | None = None,
    now_utc: datetime | None = None,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve local setup completion foundation without enabling provider execution."""

    consent_ux_state = build_provider_user_operated_consent_ux_foundation_state(
        readiness_config,
        activation_config=activation_config,
        execution_config=execution_config,
        path_consent_config=path_consent_config,
        setup_foundation_config=setup_foundation_config,
        consent_collection_config=consent_collection_config,
        consent_capture_record=consent_capture_record,
        durable_consent_record=durable_consent_record,
        consent_ux_intent=consent_ux_intent,
        durable_consent_store_dir=durable_consent_store_dir,
        now_utc=now_utc,
        surface_role=surface_role,
    )
    if setup_completion_config is _SETUP_COMPLETION_CONFIG_OMITTED:
        normalized_setup_completion = build_default_provider_setup_completion_config()
    else:
        normalized_setup_completion = normalize_provider_setup_completion_config(
            setup_completion_config  # type: ignore[arg-type]
        )
    setup_completion_fields = _provider_setup_completion_fields(
        consent_ux_state,
        normalized_setup_completion,
    )
    return replace(
        consent_ux_state,
        state_id=FAM007_PROVIDER_SETUP_COMPLETION_FOUNDATION_STATE_ID,
        mode=FAM007_PROVIDER_SETUP_COMPLETION_FOUNDATION_MODE,
        availability=FAM007_PROVIDER_SETUP_COMPLETION_FOUNDATION_AVAILABILITY,
        status_label="No AI executing",
        provider_label="No provider/model execution",
        disabled_reason=(
            "No provider, model, prompt send, downloads, memory, or runtime cache execution is approved"
        ),
        provider_next_action_label=(
            "Open NDAI for the AI Control Center; provider/model execution remains blocked"
        ),
        local_action_result_state=LOCAL_ACTION_RESULT_DETERMINISTIC_NO_PROVIDER,
        local_action_result_label="No-provider check: no provider configured",
        local_action_result_detail=(
            "Deterministic degraded result: no prompt was accepted or sent; provider-visible data remains none. Capability packs, private lanes, downloads, memory, and network remain blocked."
        ),
        local_action_result_provider_visible_data="none",
        local_action_result_sent_to_provider=False,
        local_action_result_can_accept_prompts=False,
        local_action_result_prompt_send_posture=PROMPT_SEND_POSTURE_DISABLED,
        local_action_result_network_egress_state=NETWORK_EGRESS_BLOCKED,
        local_action_result_memory_indexing_state=MEMORY_INDEXING_DISABLED,
        capability_pack_eligibility_label=(
            "Capability-pack eligibility: blocked until local capability proof"
        ),
        install_intent_label=(
            "Install intent: blocked; downloads and install execution remain disabled"
        ),
        lane_boundary_schema_version=LANE_BOUNDARY_SCHEMA_VERSION,
        public_lane_boundary_state=PUBLIC_LANE_BOUNDARY_LOCAL_ASSIST_ONLY,
        public_lane_boundary_label="Public Edition: deterministic no-provider assist; provider-visible data none",
        developer_lane_boundary_state=DEVELOPER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED,
        developer_lane_boundary_label="Developer lane: gated; private setup not configured",
        owner_lane_boundary_state=OWNER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED,
        owner_lane_boundary_label="Owner lane: gated; private setup not configured",
        private_setup_boundary_state=PRIVATE_SETUP_BOUNDARY_BLOCKED,
        private_setup_authorized=False,
        private_material_visible=False,
        owner_memory_enabled=False,
        owner_agents_enabled=False,
        interaction_affordance=LOCAL_ASSISTED_INTERACTION_AFFORDANCE,
        interaction_label="Run no-provider check",
        interaction_disabled_reason=(
            "No-provider check runs inside the AI Control Center only; prompts, providers, downloads, memory, and network remain blocked"
        ),
        no_provider_fallback_label="No-provider guard active",
        ai_control_center_diagnostic_state=AI_CONTROL_CENTER_DIAGNOSTIC_NO_PROVIDER_FAIL_CLOSED,
        ai_control_center_diagnostic_label="No provider configured; fail-closed",
        ai_control_center_provider_boundary_label="Provider boundary: blocked",
        ai_control_center_provider_boundary_detail=(
            "Provider, model, prompt, memory, downloads, and network paths remain disabled."
        ),
        ai_control_center_blocked_action_label="Prompt/provider/model action blocked",
        ai_control_center_blocked_action_detail=(
            "Provider actions are blocked until a future USER-approved provider path exists."
        ),
        ai_control_center_unavailable_capability_label="Capability packs unavailable",
        ai_control_center_unavailable_capability_detail=(
            "Capability eligibility requires future local proof; downloads and install execution remain disabled."
        ),
        ai_control_center_recovery_label="Retry local check only",
        ai_control_center_recovery_detail=(
            "Recovery remains local-only; provider setup and execution stay future-gated."
        ),
        ai_control_center_degraded_path_label="Local guidance only",
        ai_control_center_degraded_path_detail=(
            "The degraded no-provider path reports status without accepting prompts or sending data."
        ),
        ai_control_center_state_taxonomy=(
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_NO_PROVIDER_FAIL_CLOSED,
                "label": "No provider configured; fail-closed",
                "detail": "No provider/model execution path exists in this release.",
            },
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_PROVIDER_UNAVAILABLE,
                "label": "Provider unavailable",
                "detail": "Provider state cannot become active without future setup approval.",
            },
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_STALE_STATE,
                "label": "Stale state: fail-closed",
                "detail": "Stale or missing provider state remains disabled and requires a fresh local check.",
            },
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_FAILED_CHECK,
                "label": "Failed check: fail-closed",
                "detail": "A failed local check produces no provider result and sends no data.",
            },
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_RETRY_LOCAL_ONLY,
                "label": "Retry: local check only",
                "detail": "Retry is limited to the local no-provider check.",
            },
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_RECOVERY_LOCAL_ONLY,
                "label": "Recovery: local-only",
                "detail": "Recovery guidance cannot enable provider/model execution.",
            },
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_BLOCKED_ACTION,
                "label": "Blocked action",
                "detail": "Prompt, provider, model, memory, download, and private setup actions stay blocked.",
            },
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_UNAVAILABLE_CAPABILITY,
                "label": "Unavailable capability",
                "detail": "Capability packs require future proof and USER approval before install.",
            },
            {
                "state": AI_CONTROL_CENTER_DIAGNOSTIC_DEGRADED_NO_PROVIDER,
                "label": "Degraded no-provider path",
                "detail": "No-provider guidance is deterministic, local-only, and public-safe.",
            },
        ),
        local_ai_readiness_report=build_local_ai_readiness_report(),
        desktop_ai_owned_readiness_display_state=AI_PROVIDER_STATUS_DISPLAY_VISIBLE,
        desktop_ai_owned_readiness_display_label=(
            "Desktop AI-owned readiness display: no AI execution active"
        ),
        **setup_completion_fields,
    )


def build_provider_runtime_contract_state(
    config: AIProviderRuntimeConfigSnapshot | dict[str, object] | None = None,
    *,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve local provider runtime config into a fail-closed visible state."""

    normalized_config = normalize_provider_runtime_config(config)
    if normalized_config.config_state == PROVIDER_RUNTIME_CONFIG_STATE_MISSING:
        base_state = build_no_provider_ai_state(surface_role=surface_role)
        return replace(
            base_state,
            **_runtime_contract_fields(
                category=PROVIDER_RUNTIME_CATEGORY_NO_PROVIDER,
                reason_code=PROVIDER_RUNTIME_REASON_MISSING_CONFIG_FAIL_CLOSED,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=False,
                fail_closed=True,
            ),
        )
    if normalized_config.config_state == PROVIDER_RUNTIME_CONFIG_STATE_INVALID:
        base_state = build_no_provider_ai_state(surface_role=surface_role)
        return replace(
            base_state,
            status_label="AI unavailable - config failed closed",
            disabled_reason="Provider runtime config is invalid, so provider behavior is disabled",
            interaction_disabled_reason="Invalid provider runtime config failed closed; prompts remain disabled",
            **_runtime_contract_fields(
                category=PROVIDER_RUNTIME_CATEGORY_ERROR_DEGRADED,
                reason_code=PROVIDER_RUNTIME_REASON_INVALID_CONFIG_FAIL_CLOSED,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=False,
                fail_closed=True,
            ),
        )
    if normalized_config.selected_provider_id == NO_PROVIDER_ID:
        return build_local_ai_runtime_foundation_provider_boundary_state(surface_role=surface_role)
    if not normalized_config.provider_configured:
        base_state = build_local_provider_registry_state(surface_role=surface_role)
        return replace(
            base_state,
            **_runtime_contract_fields(
                category=PROVIDER_RUNTIME_CATEGORY_UNCONFIGURED,
                reason_code=PROVIDER_RUNTIME_REASON_PROVIDER_UNCONFIGURED,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=True,
                fail_closed=True,
            ),
        )
    if not normalized_config.provider_available:
        base_state = build_provider_selection_consent_state(
            selected_provider_id=normalized_config.selected_provider_id,
            surface_role=surface_role,
        )
        return replace(
            base_state,
            **_runtime_contract_fields(
                category=PROVIDER_RUNTIME_CATEGORY_UNAVAILABLE,
                reason_code=PROVIDER_RUNTIME_REASON_PROVIDER_UNAVAILABLE,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=True,
                fail_closed=True,
            ),
        )
    if not normalized_config.consent_granted:
        base_state = build_provider_selection_consent_state(
            selected_provider_id=normalized_config.selected_provider_id,
            surface_role=surface_role,
        )
        return replace(
            base_state,
            **_runtime_contract_fields(
                category=PROVIDER_RUNTIME_CATEGORY_CONSENT_MISSING,
                reason_code=PROVIDER_RUNTIME_REASON_CONSENT_REQUIRED,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=True,
                fail_closed=True,
            ),
        )
    if not normalized_config.capability_ready:
        base_state = build_local_hardware_capability_state(surface_role=surface_role)
        return replace(
            base_state,
            **_runtime_contract_fields(
                category=PROVIDER_RUNTIME_CATEGORY_CAPABILITY_MISSING,
                reason_code=PROVIDER_RUNTIME_REASON_CAPABILITY_MISSING,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=True,
                fail_closed=True,
            ),
        )

    base_state = build_local_ai_runtime_foundation_provider_boundary_state(surface_role=surface_role)
    return replace(
        base_state,
        **_runtime_contract_fields(
            category=PROVIDER_RUNTIME_CATEGORY_READY_FUTURE_GATED,
            reason_code=PROVIDER_RUNTIME_REASON_READY_FUTURE_GATED,
            provenance=normalized_config.provenance,
            config_state=normalized_config.config_state,
            config_valid=True,
            fail_closed=True,
        ),
    )


def build_provider_readiness_contract_state(
    config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve readiness/setup eligibility into visible local-only provider state."""

    normalized_config = normalize_provider_readiness_config(config)
    if normalized_config.config_state == PROVIDER_READINESS_CONFIG_STATE_MISSING:
        base_state = build_local_ai_runtime_foundation_provider_boundary_state(surface_role=surface_role)
        return replace(
            base_state,
            status_label="Provider setup disabled",
            disabled_reason="Provider readiness config is missing, so setup is disabled",
            interaction_disabled_reason="Missing provider readiness config failed closed; prompts remain disabled",
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_DISABLED,
                reason_code=PROVIDER_READINESS_REASON_CONFIG_MISSING_FAIL_CLOSED,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_DISABLED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_SETUP_DISABLED,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=False,
            ),
        )
    if normalized_config.config_state == PROVIDER_READINESS_CONFIG_STATE_INVALID:
        base_state = build_no_provider_ai_state(surface_role=surface_role)
        return replace(
            base_state,
            status_label="Provider readiness degraded",
            disabled_reason="Provider readiness config is invalid, so setup and provider behavior are disabled",
            interaction_disabled_reason="Invalid provider readiness config failed closed; prompts remain disabled",
            **_runtime_contract_fields(
                category=PROVIDER_RUNTIME_CATEGORY_ERROR_DEGRADED,
                reason_code=PROVIDER_RUNTIME_REASON_INVALID_CONFIG_FAIL_CLOSED,
                provenance=PROVIDER_RUNTIME_PROVENANCE_LOCAL_CONFIG,
                config_state=PROVIDER_RUNTIME_CONFIG_STATE_INVALID,
                config_valid=False,
                fail_closed=True,
            ),
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_DEGRADED,
                reason_code=PROVIDER_READINESS_REASON_CONFIG_INVALID_FAIL_CLOSED,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_BLOCKED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_CONFIG_INVALID,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=False,
                compatibility_posture=CAPABILITY_PACK_COMPATIBILITY_BLOCKED,
            ),
        )
    if normalized_config.config_state == PROVIDER_READINESS_CONFIG_STATE_DEFAULT:
        base_state = build_local_ai_runtime_foundation_provider_boundary_state(surface_role=surface_role)
        return replace(
            base_state,
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_DISABLED,
                reason_code=PROVIDER_READINESS_REASON_DEFAULT_LOCAL_ONLY,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_DISABLED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_SETUP_DISABLED,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
                config_valid=True,
            ),
        )
    if not normalized_config.policy_allows_setup:
        base_state = build_local_ai_runtime_foundation_provider_boundary_state(surface_role=surface_role)
        return replace(
            base_state,
            status_label="Provider setup blocked by policy",
            disabled_reason="Local policy blocks provider setup in this Workstream",
            interaction_disabled_reason="Provider setup is policy-blocked; prompts remain disabled",
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_POLICY,
                reason_code=PROVIDER_READINESS_REASON_POLICY_BLOCKED,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_BLOCKED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_POLICY_BLOCKED,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
            ),
        )
    if not normalized_config.provider_configured:
        base_state = build_local_provider_registry_state(surface_role=surface_role)
        return replace(
            base_state,
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_CONFIG_REQUIRED,
                reason_code=PROVIDER_READINESS_REASON_PROVIDER_UNCONFIGURED,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_CONFIG_REQUIRED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_CONFIG_REQUIRED,
                provenance=normalized_config.provenance,
                config_state=normalized_config.config_state,
            ),
        )
    if not normalized_config.consent_granted:
        base_state = build_provider_selection_consent_state(surface_role=surface_role)
        return replace(
            base_state,
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CONSENT,
                reason_code=PROVIDER_READINESS_REASON_CONSENT_MISSING,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_BLOCKED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_CONSENT_REQUIRED,
                provenance=PROVIDER_READINESS_PROVENANCE_CONSENT_STATE,
                config_state=normalized_config.config_state,
            ),
        )
    if not normalized_config.capability_ready:
        base_state = build_local_hardware_capability_state(surface_role=surface_role)
        return replace(
            base_state,
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CAPABILITY,
                reason_code=PROVIDER_READINESS_REASON_CAPABILITY_MISSING,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_BLOCKED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_CAPABILITY_REQUIRED,
                provenance=PROVIDER_READINESS_PROVENANCE_HARDWARE_SNAPSHOT,
                config_state=normalized_config.config_state,
                requirement_posture=CAPABILITY_PACK_REQUIREMENT_MISSING,
            ),
        )
    if not normalized_config.manifest_available:
        base_state = build_fam007_foundation_readiness_state(surface_role=surface_role)
        return replace(
            base_state,
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_MANIFEST,
                reason_code=PROVIDER_READINESS_REASON_MANIFEST_MISSING,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_BLOCKED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_MANIFEST_REQUIRED,
                provenance=PROVIDER_READINESS_PROVENANCE_CAPABILITY_MANIFEST,
                config_state=normalized_config.config_state,
                manifest_validity=CAPABILITY_PACK_MANIFEST_MISSING,
                source_trust=CAPABILITY_PACK_SOURCE_TRUST_UNVERIFIED,
            ),
        )
    if not normalized_config.manifest_valid:
        base_state = build_fam007_foundation_readiness_state(surface_role=surface_role)
        return replace(
            base_state,
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_MANIFEST,
                reason_code=PROVIDER_READINESS_REASON_MANIFEST_INVALID_INSTALL_BLOCKED,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_BLOCKED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_MANIFEST_REQUIRED,
                provenance=PROVIDER_READINESS_PROVENANCE_CAPABILITY_MANIFEST,
                config_state=normalized_config.config_state,
                manifest_validity=CAPABILITY_PACK_MANIFEST_INVALID,
                source_trust=CAPABILITY_PACK_SOURCE_TRUST_UNVERIFIED,
                compatibility_posture=CAPABILITY_PACK_COMPATIBILITY_BLOCKED,
                install_intent=CAPABILITY_PACK_INSTALL_INTENT_BLOCKED,
            ),
        )
    if not normalized_config.future_provider_setup_approved:
        base_state = build_fam007_foundation_readiness_state(surface_role=surface_role)
        return replace(
            base_state,
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_SETUP_AVAILABLE_FUTURE_GATED,
                reason_code=PROVIDER_READINESS_REASON_FUTURE_PROVIDER_GATED,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_FUTURE_GATED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_FUTURE_GATE,
                provenance=PROVIDER_READINESS_PROVENANCE_RELEASE_SOURCE_TRUTH,
                config_state=normalized_config.config_state,
                future_gate_status=PROVIDER_FUTURE_GATE_STATUS_SETUP_REQUIRED,
                capability_pack_eligibility=CAPABILITY_PACK_ELIGIBILITY_FUTURE_GATED,
                manifest_validity=CAPABILITY_PACK_MANIFEST_VALID_FUTURE_GATED,
                source_trust=CAPABILITY_PACK_SOURCE_TRUST_FUTURE_GATED,
                compatibility_posture=CAPABILITY_PACK_COMPATIBILITY_FUTURE_GATED,
                requirement_posture=CAPABILITY_PACK_REQUIREMENT_FUTURE_GATED,
                install_intent=CAPABILITY_PACK_INSTALL_INTENT_FUTURE_GATED
                if normalized_config.install_intent_requested
                else CAPABILITY_PACK_INSTALL_INTENT_NONE,
            ),
        )
    if not normalized_config.provider_ready:
        base_state = build_fam007_foundation_readiness_state(surface_role=surface_role)
        return replace(
            base_state,
            status_label="Provider readiness degraded",
            disabled_reason="Provider readiness check is not ready, so setup and provider behavior are disabled",
            interaction_disabled_reason="Provider readiness check failed closed; prompts remain disabled",
            **_readiness_contract_fields(
                state=PROVIDER_READINESS_STATE_DEGRADED,
                reason_code=PROVIDER_READINESS_REASON_PROVIDER_NOT_READY,
                setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_BLOCKED,
                setup_blocker=PROVIDER_SETUP_BLOCKER_PROVIDER_NOT_READY,
                provenance=PROVIDER_READINESS_PROVENANCE_FUTURE_RUNTIME_CHECK,
                config_state=normalized_config.config_state,
                future_gate_status=PROVIDER_FUTURE_GATE_STATUS_EXECUTION_REQUIRED,
                capability_pack_eligibility=CAPABILITY_PACK_ELIGIBILITY_FUTURE_GATED,
                manifest_validity=CAPABILITY_PACK_MANIFEST_VALID_FUTURE_GATED,
                source_trust=CAPABILITY_PACK_SOURCE_TRUST_LOCAL_ONLY,
                compatibility_posture=CAPABILITY_PACK_COMPATIBILITY_BLOCKED,
                requirement_posture=CAPABILITY_PACK_REQUIREMENT_FUTURE_GATED,
                install_intent=CAPABILITY_PACK_INSTALL_INTENT_BLOCKED,
            ),
        )

    base_state = build_fam007_foundation_readiness_state(surface_role=surface_role)
    return replace(
        base_state,
        **_readiness_contract_fields(
            state=PROVIDER_READINESS_STATE_PROVIDER_READY_EXECUTION_GATED,
            reason_code=PROVIDER_READINESS_REASON_PROVIDER_READY_EXECUTION_GATED,
            setup_eligibility=PROVIDER_SETUP_ELIGIBILITY_EXECUTION_GATED,
            setup_blocker=PROVIDER_SETUP_BLOCKER_NONE,
            provenance=PROVIDER_READINESS_PROVENANCE_FUTURE_RUNTIME_CHECK
            if normalized_config.provider_ready
            else PROVIDER_READINESS_PROVENANCE_RELEASE_SOURCE_TRUTH,
            config_state=normalized_config.config_state,
            future_gate_status=PROVIDER_FUTURE_GATE_STATUS_EXECUTION_REQUIRED,
            capability_pack_eligibility=CAPABILITY_PACK_ELIGIBILITY_FUTURE_GATED,
            manifest_validity=CAPABILITY_PACK_MANIFEST_VALID_FUTURE_GATED,
            source_trust=CAPABILITY_PACK_SOURCE_TRUST_LOCAL_ONLY,
            compatibility_posture=CAPABILITY_PACK_COMPATIBILITY_FUTURE_GATED,
            requirement_posture=CAPABILITY_PACK_REQUIREMENT_FUTURE_GATED,
            install_intent=CAPABILITY_PACK_INSTALL_INTENT_FUTURE_GATED
            if normalized_config.install_intent_requested
            else CAPABILITY_PACK_INSTALL_INTENT_NONE,
        ),
    )


def build_provider_activation_foundation_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve readiness plus activation gates into a local-only activation foundation state."""

    normalized_readiness = normalize_provider_readiness_config(readiness_config)
    if activation_config is _ACTIVATION_CONFIG_OMITTED:
        normalized_activation = build_default_provider_activation_config()
    else:
        normalized_activation = normalize_provider_activation_config(
            activation_config  # type: ignore[arg-type]
        )
    base_state = build_provider_readiness_contract_state(normalized_readiness, surface_role=surface_role)

    if normalized_activation.config_state == PROVIDER_ACTIVATION_CONFIG_STATE_MISSING:
        return replace(
            base_state,
            status_label="Provider activation disabled",
            disabled_reason="Provider activation config is missing, so activation is disabled",
            interaction_disabled_reason="Missing activation config failed closed; prompts remain disabled",
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_DISABLED,
                reason_code=PROVIDER_ACTIVATION_REASON_CONFIG_MISSING_FAIL_CLOSED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_DISABLED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_READINESS_REQUIRED,
                provenance=normalized_activation.provenance,
                config_state=normalized_activation.config_state,
                config_valid=False,
            ),
        )
    if normalized_activation.config_state == PROVIDER_ACTIVATION_CONFIG_STATE_INVALID:
        return replace(
            base_state,
            status_label="Provider activation degraded",
            disabled_reason="Provider activation config is invalid, so activation and provider behavior are disabled",
            interaction_disabled_reason="Invalid activation config failed closed; prompts remain disabled",
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_DEGRADED,
                reason_code=PROVIDER_ACTIVATION_REASON_CONFIG_INVALID_FAIL_CLOSED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_CONFIG_INVALID,
                provenance=normalized_activation.provenance,
                config_state=normalized_activation.config_state,
                config_valid=False,
            ),
        )

    activation_common = {
        "config_state": normalized_activation.config_state,
        "config_valid": normalized_activation.config_valid,
    }
    readiness_state = base_state.provider_readiness_state
    if normalized_readiness.config_state == PROVIDER_READINESS_CONFIG_STATE_INVALID:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_DEGRADED,
                reason_code=PROVIDER_ACTIVATION_REASON_CONFIG_INVALID_FAIL_CLOSED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_READINESS_REQUIRED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_READINESS_STATE,
                **activation_common,
            ),
        )
    if readiness_state == PROVIDER_READINESS_STATE_SETUP_DISABLED:
        return replace(
            base_state,
            status_label="Provider activation unavailable",
            disabled_reason="Provider activation is unavailable until readiness and later USER approval exist",
            interaction_disabled_reason="Activation foundation is status-only; prompts remain disabled",
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_UNAVAILABLE,
                reason_code=PROVIDER_ACTIVATION_REASON_DEFAULT_UNAVAILABLE,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_UNAVAILABLE,
                blocker=PROVIDER_ACTIVATION_BLOCKER_READINESS_REQUIRED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_DEFAULT_CONFIG,
                **activation_common,
            ),
        )
    if readiness_state == PROVIDER_READINESS_STATE_SETUP_CONFIG_REQUIRED:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_BLOCKED_BY_READINESS,
                reason_code=PROVIDER_ACTIVATION_REASON_READINESS_BLOCKED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_READINESS_REQUIRED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_READINESS_STATE,
                **activation_common,
            ),
        )
    if readiness_state == PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CONSENT:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CONSENT,
                reason_code=PROVIDER_ACTIVATION_REASON_CONSENT_REQUIRED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_CONSENT_REQUIRED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_CONSENT_STATE,
                consent_gate=CONSENT_GATE_REQUIRED,
                **activation_common,
            ),
        )
    if readiness_state == PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_CAPABILITY:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CAPABILITY,
                reason_code=PROVIDER_ACTIVATION_REASON_CAPABILITY_REQUIRED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_CAPABILITY_REQUIRED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_READINESS_STATE,
                consent_gate=CONSENT_GATE_READY,
                **activation_common,
            ),
        )
    if readiness_state == PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_MANIFEST:
        manifest_reason = (
            PROVIDER_ACTIVATION_REASON_MANIFEST_REQUIRED
            if base_state.capability_pack_manifest_validity_state == CAPABILITY_PACK_MANIFEST_MISSING
            else PROVIDER_ACTIVATION_REASON_MANIFEST_REQUIRED
        )
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_BLOCKED_BY_MANIFEST,
                reason_code=manifest_reason,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_MANIFEST_REQUIRED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_CAPABILITY_MANIFEST,
                readiness_gate=READINESS_GATE_READY,
                consent_gate=CONSENT_GATE_READY,
                capability_gate=CAPABILITY_GATE_READY,
                **activation_common,
            ),
        )
    if readiness_state == PROVIDER_READINESS_STATE_SETUP_BLOCKED_BY_POLICY:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_BLOCKED_BY_POLICY,
                reason_code=PROVIDER_ACTIVATION_REASON_POLICY_BLOCKED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_POLICY_BLOCKED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_READINESS_STATE,
                **activation_common,
            ),
        )
    if readiness_state == PROVIDER_READINESS_STATE_SETUP_AVAILABLE_FUTURE_GATED:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_ELIGIBLE_FUTURE_GATED,
                reason_code=PROVIDER_ACTIVATION_REASON_FUTURE_GATED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_FUTURE_GATED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_FUTURE_ACTIVATION_GATE,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_RELEASE_SOURCE_TRUTH,
                future_gate_status=PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_REQUIRED,
                readiness_gate=READINESS_GATE_READY,
                consent_gate=CONSENT_GATE_READY,
                capability_gate=CAPABILITY_GATE_READY,
                manifest_gate=MANIFEST_GATE_READY,
                **activation_common,
            ),
        )
    if readiness_state == PROVIDER_READINESS_STATE_DEGRADED:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_DEGRADED,
                reason_code=PROVIDER_ACTIVATION_REASON_READINESS_BLOCKED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_READINESS_REQUIRED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_READINESS_STATE,
                future_gate_status=PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_EXECUTION_REQUIRED,
                **activation_common,
            ),
        )
    if not normalized_activation.future_activation_approved:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_ELIGIBLE_FUTURE_GATED,
                reason_code=PROVIDER_ACTIVATION_REASON_FUTURE_GATED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_FUTURE_GATED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_FUTURE_ACTIVATION_GATE,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_RELEASE_SOURCE_TRUTH,
                future_gate_status=PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_REQUIRED,
                readiness_gate=READINESS_GATE_READY,
                consent_gate=CONSENT_GATE_READY,
                capability_gate=CAPABILITY_GATE_READY,
                manifest_gate=MANIFEST_GATE_READY,
                **activation_common,
            ),
        )
    if not normalized_activation.adapter_available:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_BLOCKED_BY_ADAPTER,
                reason_code=PROVIDER_ACTIVATION_REASON_ADAPTER_UNAVAILABLE,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_ADAPTER_UNAVAILABLE,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_ADAPTER_CONTRACT,
                future_gate_status=PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_EXECUTION_REQUIRED,
                readiness_gate=READINESS_GATE_READY,
                consent_gate=CONSENT_GATE_READY,
                capability_gate=CAPABILITY_GATE_READY,
                manifest_gate=MANIFEST_GATE_READY,
                **activation_common,
            ),
        )
    if not normalized_activation.safety_eval_complete:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_BLOCKED_BY_POLICY,
                reason_code=PROVIDER_ACTIVATION_REASON_POLICY_BLOCKED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_POLICY_BLOCKED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_RELEASE_SOURCE_TRUTH,
                future_gate_status=PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_EXECUTION_REQUIRED,
                adapter_available=True,
                readiness_gate=READINESS_GATE_READY,
                consent_gate=CONSENT_GATE_READY,
                capability_gate=CAPABILITY_GATE_READY,
                manifest_gate=MANIFEST_GATE_READY,
                **activation_common,
            ),
        )
    if not normalized_activation.prompt_execution_approved or not normalized_activation.model_execution_approved:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_READY_EXECUTION_GATED,
                reason_code=PROVIDER_ACTIVATION_REASON_EXECUTION_GATED,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_EXECUTION_GATED,
                blocker=PROVIDER_ACTIVATION_BLOCKER_EXECUTION_GATE,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_FUTURE_RUNTIME_CHECK,
                future_gate_status=PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_EXECUTION_REQUIRED,
                adapter_available=True,
                readiness_gate=READINESS_GATE_READY,
                consent_gate=CONSENT_GATE_READY,
                capability_gate=CAPABILITY_GATE_READY,
                manifest_gate=MANIFEST_GATE_READY,
                safety_eval_gate=SAFETY_EVAL_GATE_READY,
                **activation_common,
            ),
        )
    if normalized_activation.functional_ai_ready:
        return replace(
            base_state,
            **_activation_contract_fields(
                state=PROVIDER_ACTIVATION_STATE_FUNCTIONAL_AI_READY_FUTURE_VERSION,
                reason_code=PROVIDER_ACTIVATION_REASON_FUNCTIONAL_AI_FUTURE_VERSION,
                eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_FUTURE_VERSION,
                blocker=PROVIDER_ACTIVATION_BLOCKER_VERSION_JUMP_REQUIRED,
                provenance=PROVIDER_ACTIVATION_PROVENANCE_FUTURE_RUNTIME_CHECK,
                future_gate_status=PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_VERSION_JUMP_REQUIRED,
                adapter_available=True,
                readiness_gate=READINESS_GATE_READY,
                consent_gate=CONSENT_GATE_READY,
                capability_gate=CAPABILITY_GATE_READY,
                manifest_gate=MANIFEST_GATE_READY,
                safety_eval_gate=SAFETY_EVAL_GATE_READY,
                functional_ai_criteria=FUNCTIONAL_AI_CRITERIA_READY_FUTURE_VERSION,
                v18_readiness=V18_PREBETA_READINESS_READY,
                **activation_common,
            ),
        )

    return replace(
        base_state,
        **_activation_contract_fields(
            state=PROVIDER_ACTIVATION_STATE_READY_EXECUTION_GATED,
            reason_code=PROVIDER_ACTIVATION_REASON_EXECUTION_GATED,
            eligibility=PROVIDER_ACTIVATION_ELIGIBILITY_EXECUTION_GATED,
            blocker=PROVIDER_ACTIVATION_BLOCKER_EXECUTION_GATE,
            provenance=PROVIDER_ACTIVATION_PROVENANCE_FUTURE_RUNTIME_CHECK,
            future_gate_status=PROVIDER_FUTURE_ACTIVATION_GATE_STATUS_EXECUTION_REQUIRED,
            adapter_available=True,
            readiness_gate=READINESS_GATE_READY,
            consent_gate=CONSENT_GATE_READY,
            capability_gate=CAPABILITY_GATE_READY,
            manifest_gate=MANIFEST_GATE_READY,
            safety_eval_gate=SAFETY_EVAL_GATE_READY,
            **activation_common,
        ),
    )


def build_provider_execution_readiness_gates_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve activation foundation into local-only provider execution-readiness gates."""

    if activation_config is _ACTIVATION_CONFIG_OMITTED:
        activation_state = build_provider_activation_foundation_state(
            readiness_config,
            surface_role=surface_role,
        )
    else:
        activation_state = build_provider_activation_foundation_state(
            readiness_config,
            activation_config=activation_config,  # type: ignore[arg-type]
            surface_role=surface_role,
        )

    if execution_config is _EXECUTION_CONFIG_OMITTED:
        normalized_execution = build_default_provider_execution_readiness_config()
    else:
        normalized_execution = normalize_provider_execution_readiness_config(
            execution_config  # type: ignore[arg-type]
        )

    common = {
        "config_state": normalized_execution.config_state,
        "provider_path_selected": normalized_execution.provider_path_selected,
        "provider_adapter_selected": normalized_execution.provider_adapter_selected,
        "prompt_acceptance_ready": normalized_execution.prompt_acceptance_approved,
        "prompt_routing_ready": normalized_execution.prompt_routing_approved,
        "model_execution_ready": normalized_execution.model_execution_approved,
        "provider_visible_data_ready": normalized_execution.provider_visible_data_approved,
        "network_external_ready": normalized_execution.network_external_approved,
        "safety_ready": normalized_execution.safety_eval_complete,
        "functional_ai_release_ready": normalized_execution.functional_ai_release_ready,
    }

    if normalized_execution.config_state == PROVIDER_EXECUTION_CONFIG_STATE_MISSING:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness disabled",
            disabled_reason="Execution readiness config is missing, so execution remains disabled",
            interaction_disabled_reason="Missing execution-readiness config failed closed; prompts remain disabled",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_DISABLED,
                reason_code=PROVIDER_EXECUTION_REASON_CONFIG_MISSING_FAIL_CLOSED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_DISABLED,
                blocker=PROVIDER_EXECUTION_BLOCKER_ACTIVATION_REQUIRED,
                provenance=normalized_execution.provenance,
                config_valid=False,
                **common,
            ),
        )

    if normalized_execution.config_state == PROVIDER_EXECUTION_CONFIG_STATE_INVALID:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness degraded",
            disabled_reason="Execution readiness config is invalid, so execution remains disabled",
            interaction_disabled_reason="Invalid execution-readiness config failed closed; prompts remain disabled",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_DEGRADED,
                reason_code=PROVIDER_EXECUTION_REASON_CONFIG_INVALID_FAIL_CLOSED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_CONFIG_INVALID,
                provenance=normalized_execution.provenance,
                config_valid=False,
                **common,
            ),
        )

    activation_readiness = activation_state.provider_activation_state
    if activation_readiness in {
        PROVIDER_ACTIVATION_STATE_UNAVAILABLE,
        PROVIDER_ACTIVATION_STATE_DISABLED,
    }:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness unavailable",
            disabled_reason="Provider execution readiness is unavailable until activation prerequisites exist",
            interaction_disabled_reason="Execution readiness is status-only; prompts remain disabled",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_UNAVAILABLE,
                reason_code=PROVIDER_EXECUTION_REASON_DEFAULT_UNAVAILABLE,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_UNAVAILABLE,
                blocker=PROVIDER_EXECUTION_BLOCKER_ACTIVATION_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_ACTIVATION_STATE,
                **common,
            ),
        )

    if activation_readiness in {
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_READINESS,
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CONSENT,
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_CAPABILITY,
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_POLICY,
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_MANIFEST,
        PROVIDER_ACTIVATION_STATE_BLOCKED_BY_ADAPTER,
    }:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked",
            disabled_reason="Provider activation is blocked, so execution readiness is blocked",
            interaction_disabled_reason="Activation blockers must clear before execution readiness can advance",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ACTIVATION,
                reason_code=PROVIDER_EXECUTION_REASON_ACTIVATION_BLOCKED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_ACTIVATION_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_ACTIVATION_STATE,
                **common,
            ),
        )

    if activation_readiness == PROVIDER_ACTIVATION_STATE_DEGRADED:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness degraded",
            disabled_reason="Provider activation is degraded, so execution readiness fails closed",
            interaction_disabled_reason="Degraded activation keeps prompt and model execution disabled",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_DEGRADED,
                reason_code=PROVIDER_EXECUTION_REASON_ACTIVATION_BLOCKED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_ACTIVATION_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_ACTIVATION_STATE,
                **common,
            ),
        )

    if activation_readiness == PROVIDER_ACTIVATION_STATE_ELIGIBLE_FUTURE_GATED:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness future-gated",
            disabled_reason="Provider activation is future-gated, so execution readiness remains future-gated",
            interaction_disabled_reason="Future USER approval is required before execution readiness can advance",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_READY_FUTURE_GATED,
                reason_code=PROVIDER_EXECUTION_REASON_FUTURE_GATED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_FUTURE_GATED,
                blocker=PROVIDER_EXECUTION_BLOCKER_FUTURE_EXECUTION_GATE,
                provenance=PROVIDER_EXECUTION_PROVENANCE_ACTIVATION_STATE,
                approval_status=PROVIDER_EXECUTION_APPROVAL_STATUS_FUTURE_GATED,
                **common,
            ),
        )

    if not normalized_execution.provider_path_selected:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked by provider path",
            disabled_reason="No provider path has been selected for future execution proof",
            interaction_disabled_reason="Provider path selection is required before prompts can be routed",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROVIDER_PATH,
                reason_code=PROVIDER_EXECUTION_REASON_PROVIDER_PATH_MISSING,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_PROVIDER_PATH_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_PROVIDER_PATH_CONTRACT,
                **common,
            ),
        )

    if not normalized_execution.provider_adapter_selected:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked by adapter",
            disabled_reason="No provider adapter has been selected for future execution proof",
            interaction_disabled_reason="Adapter selection is required before provider execution can be considered",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ADAPTER,
                reason_code=PROVIDER_EXECUTION_REASON_ADAPTER_UNAVAILABLE,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_ADAPTER_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_ADAPTER_CONTRACT,
                **common,
            ),
        )

    if not normalized_execution.prompt_acceptance_approved or not normalized_execution.prompt_routing_approved:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked by prompt gate",
            disabled_reason="Prompt acceptance and routing proof are not approved",
            interaction_disabled_reason="Prompt sends remain disabled until prompt gates are approved",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_PROMPT_GATE,
                reason_code=PROVIDER_EXECUTION_REASON_PROMPT_GATE_BLOCKED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_PROMPT_GATE,
                provenance=PROVIDER_EXECUTION_PROVENANCE_PROMPT_GATE,
                **common,
            ),
        )

    if not normalized_execution.model_execution_approved:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked by model gate",
            disabled_reason="Model execution proof is not approved",
            interaction_disabled_reason="Model execution remains disabled until a later USER-approved branch",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_MODEL_GATE,
                reason_code=PROVIDER_EXECUTION_REASON_MODEL_GATE_BLOCKED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_MODEL_GATE,
                provenance=PROVIDER_EXECUTION_PROVENANCE_MODEL_GATE,
                **common,
            ),
        )

    if not normalized_execution.consent_granted:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked by consent",
            disabled_reason="Provider execution consent is not granted",
            interaction_disabled_reason="Consent is required before any provider-visible prompt path",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_CONSENT,
                reason_code=PROVIDER_EXECUTION_REASON_CONSENT_REQUIRED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_CONSENT_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_CONSENT_STATE,
                **common,
            ),
        )

    if not normalized_execution.safety_eval_complete:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked by safety/eval",
            disabled_reason="Safety and eval proof are not complete",
            interaction_disabled_reason="Safety/eval approval is required before provider/model execution",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_SAFETY,
                reason_code=PROVIDER_EXECUTION_REASON_SAFETY_EVAL_REQUIRED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_SAFETY_EVAL_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_SAFETY_EVAL,
                **common,
            ),
        )

    if not normalized_execution.network_external_approved:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked by network",
            disabled_reason="Network or external-call posture is not approved",
            interaction_disabled_reason="Network egress remains blocked",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_NETWORK,
                reason_code=PROVIDER_EXECUTION_REASON_NETWORK_BLOCKED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_NETWORK_APPROVAL_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_NETWORK_POLICY,
                **common,
            ),
        )

    if not normalized_execution.policy_allows_execution:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness blocked by policy",
            disabled_reason="Execution policy does not allow provider/model execution",
            interaction_disabled_reason="Policy approval is required before execution readiness can advance",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_POLICY,
                reason_code=PROVIDER_EXECUTION_REASON_POLICY_BLOCKED,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_BLOCKED,
                blocker=PROVIDER_EXECUTION_BLOCKER_POLICY_BLOCKED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_RELEASE_SOURCE_TRUTH,
                **common,
            ),
        )

    if not normalized_execution.execution_approved:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Execution readiness ready but not approved",
            disabled_reason="Execution proof gates are ready, but USER execution approval is missing",
            interaction_disabled_reason="Provider/model execution remains disabled until explicit USER approval",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_READY_BUT_NOT_APPROVED,
                reason_code=PROVIDER_EXECUTION_REASON_APPROVAL_MISSING,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_READY_NOT_APPROVED,
                blocker=PROVIDER_EXECUTION_BLOCKER_APPROVAL_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_FUTURE_RUNTIME_CHECK,
                approval_status=PROVIDER_EXECUTION_APPROVAL_STATUS_MISSING,
                **common,
            ),
        )

    if normalized_execution.functional_ai_release_ready:
        return replace(
            activation_state,
            state_id=FAM007_EXECUTION_READINESS_STATE_ID,
            mode=FAM007_EXECUTION_READINESS_MODE,
            availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
            status_label="Functional AI proof ready for future version",
            disabled_reason="Functional AI proof is reserved for a later v1.8.0-prebeta release decision",
            interaction_disabled_reason="v1.8.0-prebeta release execution remains a separate USER decision",
            **_execution_readiness_contract_fields(
                state=PROVIDER_EXECUTION_READINESS_STATE_FUNCTIONAL_AI_READY_FUTURE_VERSION,
                reason_code=PROVIDER_EXECUTION_REASON_FUNCTIONAL_AI_FUTURE_VERSION,
                eligibility=PROVIDER_EXECUTION_ELIGIBILITY_FUTURE_VERSION,
                blocker=PROVIDER_EXECUTION_BLOCKER_VERSION_JUMP_REQUIRED,
                provenance=PROVIDER_EXECUTION_PROVENANCE_FUTURE_RUNTIME_CHECK,
                approval_status=PROVIDER_EXECUTION_APPROVAL_STATUS_GRANTED_FOR_PROOF,
                **common,
            ),
        )

    return replace(
        activation_state,
        state_id=FAM007_EXECUTION_READINESS_STATE_ID,
        mode=FAM007_EXECUTION_READINESS_MODE,
        availability=FAM007_EXECUTION_READINESS_AVAILABILITY,
        status_label="Execution readiness future-gated",
        disabled_reason="Execution readiness proof is available only as a future-gated local contract",
        interaction_disabled_reason="Provider/model execution remains disabled",
        **_execution_readiness_contract_fields(
            state=PROVIDER_EXECUTION_READINESS_STATE_READY_FUTURE_GATED,
            reason_code=PROVIDER_EXECUTION_REASON_FUTURE_GATED,
            eligibility=PROVIDER_EXECUTION_ELIGIBILITY_FUTURE_GATED,
            blocker=PROVIDER_EXECUTION_BLOCKER_FUTURE_EXECUTION_GATE,
            provenance=PROVIDER_EXECUTION_PROVENANCE_FUTURE_RUNTIME_CHECK,
            approval_status=PROVIDER_EXECUTION_APPROVAL_STATUS_FUTURE_GATED,
            **common,
        ),
    )


def build_provider_path_consent_readiness_state(
    readiness_config: AIProviderReadinessConfigSnapshot | dict[str, object] | None = None,
    *,
    activation_config: AIProviderActivationConfigSnapshot | dict[str, object] | None | object = _ACTIVATION_CONFIG_OMITTED,
    execution_config: AIProviderExecutionReadinessConfigSnapshot | dict[str, object] | None | object = (
        _EXECUTION_CONFIG_OMITTED
    ),
    path_consent_config: AIProviderPathConsentReadinessConfigSnapshot | dict[str, object] | None | object = (
        _PATH_CONSENT_CONFIG_OMITTED
    ),
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Resolve execution-readiness gates into local-only provider path and consent readiness."""

    if execution_config is _EXECUTION_CONFIG_OMITTED:
        execution_state = build_provider_execution_readiness_gates_state(
            readiness_config,
            activation_config=activation_config,
            surface_role=surface_role,
        )
    else:
        execution_state = build_provider_execution_readiness_gates_state(
            readiness_config,
            activation_config=activation_config,
            execution_config=execution_config,  # type: ignore[arg-type]
            surface_role=surface_role,
        )

    if path_consent_config is _PATH_CONSENT_CONFIG_OMITTED:
        normalized_path = build_default_provider_path_consent_readiness_config()
    else:
        normalized_path = normalize_provider_path_consent_readiness_config(
            path_consent_config  # type: ignore[arg-type]
        )

    manifest_ready = bool(normalized_path.manifest_available and normalized_path.manifest_valid)
    common = {
        "config_state": normalized_path.config_state,
        "config_valid": normalized_path.config_valid,
        "provider_path_selected": normalized_path.provider_path_selected,
        "provider_config_present": normalized_path.provider_config_present,
        "provider_config_valid": normalized_path.provider_config_valid,
        "provider_profile_available": normalized_path.provider_profile_available,
        "provider_available": normalized_path.provider_available,
        "setup_consent_ready": normalized_path.setup_consent_ready,
        "execution_consent_ready": normalized_path.execution_consent_ready,
        "data_visibility_ready": normalized_path.data_visibility_approved,
        "audit_ready": normalized_path.audit_ready,
        "capability_ready": normalized_path.capability_ready,
        "manifest_ready": manifest_ready,
        "safety_ready": normalized_path.safety_eval_complete,
        "setup_approved": normalized_path.setup_approved,
        "execution_approved": normalized_path.execution_approved,
        "future_execution_branch_ready": normalized_path.future_execution_branch_ready,
        "functional_ai_release_ready": normalized_path.functional_ai_release_ready,
    }

    def _with_path_fields(
        *,
        state: str,
        reason_code: str,
        eligibility: str,
        blocker: str,
        provenance: str,
        approval_status: str = PROVIDER_PATH_APPROVAL_STATUS_MISSING,
        status_label: str,
        disabled_reason: str,
        interaction_disabled_reason: str,
    ) -> AIProviderStateSnapshot:
        path_fields = _provider_path_consent_contract_fields(
            state=state,
            reason_code=reason_code,
            eligibility=eligibility,
            blocker=blocker,
            provenance=provenance,
            approval_status=approval_status,
            **common,
        )
        path_fields["interaction_disabled_reason"] = interaction_disabled_reason
        return replace(
            execution_state,
            state_id=FAM007_PROVIDER_PATH_CONSENT_READINESS_STATE_ID,
            mode=FAM007_PROVIDER_PATH_CONSENT_READINESS_MODE,
            availability=FAM007_PROVIDER_PATH_CONSENT_READINESS_AVAILABILITY,
            status_label=status_label,
            disabled_reason=disabled_reason,
            **path_fields,
        )

    if normalized_path.config_state == PROVIDER_PATH_CONFIG_STATE_MISSING:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_DISABLED,
            reason_code=PROVIDER_PATH_REASON_CONFIG_MISSING_FAIL_CLOSED,
            eligibility=PROVIDER_PATH_ELIGIBILITY_DISABLED,
            blocker=PROVIDER_PATH_BLOCKER_CONFIG_REQUIRED,
            provenance=normalized_path.provenance,
            status_label="Provider path readiness disabled",
            disabled_reason="Provider path readiness config is missing, so readiness remains disabled",
            interaction_disabled_reason="Missing provider-path config failed closed; setup remains disabled",
        )

    if normalized_path.config_state == PROVIDER_PATH_CONFIG_STATE_INVALID:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_DEGRADED,
            reason_code=PROVIDER_PATH_REASON_CONFIG_INVALID_FAIL_CLOSED,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_CONFIG_INVALID,
            provenance=normalized_path.provenance,
            status_label="Provider path readiness degraded",
            disabled_reason="Provider path readiness config is invalid, so readiness fails closed",
            interaction_disabled_reason="Invalid provider-path config failed closed; setup remains disabled",
        )

    if execution_state.provider_execution_readiness_state in {
        PROVIDER_EXECUTION_READINESS_STATE_UNAVAILABLE,
        PROVIDER_EXECUTION_READINESS_STATE_DISABLED,
        PROVIDER_EXECUTION_READINESS_STATE_BLOCKED_BY_ACTIVATION,
        PROVIDER_EXECUTION_READINESS_STATE_DEGRADED,
    }:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_UNAVAILABLE,
            reason_code=PROVIDER_PATH_REASON_EXECUTION_READINESS_UNAVAILABLE,
            eligibility=PROVIDER_PATH_ELIGIBILITY_UNAVAILABLE,
            blocker=PROVIDER_PATH_BLOCKER_EXECUTION_READINESS_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_EXECUTION_READINESS_STATE,
            status_label="Provider path readiness unavailable",
            disabled_reason="Provider path readiness is unavailable until execution-readiness prerequisites exist",
            interaction_disabled_reason="Provider path readiness is status-only; setup and prompts remain disabled",
        )

    if not normalized_path.provider_path_selected:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_UNSELECTED,
            reason_code=PROVIDER_PATH_REASON_UNSELECTED,
            eligibility=PROVIDER_PATH_ELIGIBILITY_SELECTION_REQUIRED,
            blocker=PROVIDER_PATH_BLOCKER_SELECTION_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_PROVIDER_SELECTION_CONTRACT,
            status_label="Provider path readiness unselected",
            disabled_reason="No provider path has been selected for future setup proof",
            interaction_disabled_reason="Provider path selection requires later USER-approved setup work",
        )

    if not normalized_path.provider_config_present:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_SELECTION_REQUIRED,
            reason_code=PROVIDER_PATH_REASON_CONFIG_MISSING,
            eligibility=PROVIDER_PATH_ELIGIBILITY_SELECTION_REQUIRED,
            blocker=PROVIDER_PATH_BLOCKER_CONFIG_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_PROVIDER_CONFIG_CONTRACT,
            status_label="Provider path readiness needs config",
            disabled_reason="Provider configuration envelope is missing",
            interaction_disabled_reason="Provider setup remains disabled until a future setup branch supplies config proof",
        )

    if not normalized_path.provider_config_valid:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_DEGRADED,
            reason_code=PROVIDER_PATH_REASON_CONFIG_INVALID,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_CONFIG_INVALID,
            provenance=PROVIDER_PATH_PROVENANCE_PROVIDER_CONFIG_CONTRACT,
            status_label="Provider path readiness degraded",
            disabled_reason="Provider configuration envelope is invalid",
            interaction_disabled_reason="Invalid provider configuration keeps setup and execution disabled",
        )

    if not normalized_path.setup_consent_ready:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CONSENT,
            reason_code=PROVIDER_PATH_REASON_SETUP_CONSENT_REQUIRED,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_SETUP_CONSENT_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_CONSENT_STATE,
            status_label="Provider path readiness blocked by setup consent",
            disabled_reason="Setup consent readiness is not satisfied",
            interaction_disabled_reason="Consent collection remains disabled until later USER approval",
        )

    if not normalized_path.execution_consent_ready:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CONSENT,
            reason_code=PROVIDER_PATH_REASON_EXECUTION_CONSENT_REQUIRED,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_EXECUTION_CONSENT_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_CONSENT_STATE,
            status_label="Provider path readiness blocked by execution consent",
            disabled_reason="Execution consent readiness is not satisfied",
            interaction_disabled_reason="Prompt/model execution consent remains a later USER-approved gate",
        )

    if not normalized_path.data_visibility_approved:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CONSENT,
            reason_code=PROVIDER_PATH_REASON_DATA_VISIBILITY_BLOCKED,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_DATA_VISIBILITY_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_DATA_VISIBILITY_CONTRACT,
            status_label="Provider path readiness blocked by data visibility",
            disabled_reason="Provider-visible-data requirements are not approved",
            interaction_disabled_reason="Provider-visible data remains none",
        )

    if not normalized_path.capability_ready:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_CAPABILITY,
            reason_code=PROVIDER_PATH_REASON_CAPABILITY_MISSING,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_CAPABILITY_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_CAPABILITY_CONTRACT,
            status_label="Provider path readiness blocked by capability",
            disabled_reason="Capability readiness proof is missing",
            interaction_disabled_reason="Capability downloads and model workloads remain disabled",
        )

    if not manifest_ready:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_MANIFEST,
            reason_code=PROVIDER_PATH_REASON_MANIFEST_MISSING,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_MANIFEST_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_MANIFEST_STATE,
            status_label="Provider path readiness blocked by manifest",
            disabled_reason="Provider/capability manifest proof is missing",
            interaction_disabled_reason="Install, update, and model download paths remain disabled",
        )

    if not normalized_path.safety_eval_complete:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_SAFETY,
            reason_code=PROVIDER_PATH_REASON_SAFETY_BLOCKED,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_SAFETY_EVAL_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_SAFETY_EVAL,
            status_label="Provider path readiness blocked by safety/eval",
            disabled_reason="Safety/eval readiness proof is missing",
            interaction_disabled_reason="Provider setup and execution remain disabled before safety proof",
        )

    if not normalized_path.policy_allows_provider_path:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_BLOCKED_BY_POLICY,
            reason_code=PROVIDER_PATH_REASON_POLICY_BLOCKED,
            eligibility=PROVIDER_PATH_ELIGIBILITY_BLOCKED,
            blocker=PROVIDER_PATH_BLOCKER_POLICY_BLOCKED,
            provenance=PROVIDER_PATH_PROVENANCE_AUDIT_POLICY,
            status_label="Provider path readiness blocked by policy",
            disabled_reason="Policy does not allow provider path setup",
            interaction_disabled_reason="Policy approval is required before setup readiness can advance",
        )

    if not normalized_path.setup_approved:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_READY_BUT_NOT_APPROVED,
            reason_code=PROVIDER_PATH_REASON_SETUP_APPROVAL_MISSING,
            eligibility=PROVIDER_PATH_ELIGIBILITY_READY_NOT_APPROVED,
            blocker=PROVIDER_PATH_BLOCKER_SETUP_APPROVAL_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_FUTURE_RUNTIME_CHECK,
            status_label="Provider path readiness ready but setup approval missing",
            disabled_reason="Provider path readiness is locally satisfied, but setup approval is missing",
            interaction_disabled_reason="Provider setup remains disabled until explicit USER approval",
        )

    if not normalized_path.execution_approved:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_READY_BUT_NOT_APPROVED,
            reason_code=PROVIDER_PATH_REASON_EXECUTION_APPROVAL_MISSING,
            eligibility=PROVIDER_PATH_ELIGIBILITY_READY_NOT_APPROVED,
            blocker=PROVIDER_PATH_BLOCKER_EXECUTION_APPROVAL_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_FUTURE_RUNTIME_CHECK,
            status_label="Provider path readiness ready but execution approval missing",
            disabled_reason="Provider execution approval is missing",
            interaction_disabled_reason="Provider/model execution remains disabled until explicit USER approval",
        )

    if normalized_path.future_execution_branch_ready or normalized_path.functional_ai_release_ready:
        return _with_path_fields(
            state=PROVIDER_PATH_READINESS_STATE_READY_FOR_FUTURE_EXECUTION_BRANCH,
            reason_code=PROVIDER_PATH_REASON_READY_FOR_FUTURE_EXECUTION_BRANCH,
            eligibility=PROVIDER_PATH_ELIGIBILITY_FUTURE_EXECUTION_BRANCH,
            blocker=PROVIDER_PATH_BLOCKER_VERSION_JUMP_REQUIRED,
            provenance=PROVIDER_PATH_PROVENANCE_FUTURE_RUNTIME_CHECK,
            approval_status=PROVIDER_PATH_APPROVAL_STATUS_READY_FOR_FUTURE_PROOF,
            status_label="Provider path readiness ready for future execution branch",
            disabled_reason="Provider path readiness is proof-only and reserved for a future execution branch",
            interaction_disabled_reason="v1.8.0-prebeta remains pending functional-AI proof",
        )

    return _with_path_fields(
        state=PROVIDER_PATH_READINESS_STATE_READY_FUTURE_GATED,
        reason_code=PROVIDER_PATH_REASON_READY_FOR_FUTURE_EXECUTION_BRANCH,
        eligibility=PROVIDER_PATH_ELIGIBILITY_FUTURE_GATED,
        blocker=PROVIDER_PATH_BLOCKER_EXECUTION_APPROVAL_REQUIRED,
        provenance=PROVIDER_PATH_PROVENANCE_FUTURE_RUNTIME_CHECK,
        approval_status=PROVIDER_PATH_APPROVAL_STATUS_FUTURE_GATED,
        status_label="Provider path readiness future-gated",
        disabled_reason="Provider path readiness is local proof only",
        interaction_disabled_reason="Provider setup and execution remain disabled",
    )


def build_no_provider_ai_state(*, surface_role: str = "hud") -> AIProviderStateSnapshot:
    """Build the local-only no-provider state used before any provider is admitted."""

    normalized_surface = surface_role if surface_role in {"core", "hud", "combined"} else "hud"
    return AIProviderStateSnapshot(
        package_id=PACKAGE_ID,
        slice_ids=(SLC_017_ID, SLC_018_ID),
        state_id=STATE_ID,
        mode=NO_PROVIDER_MODE,
        availability=NO_PROVIDER_AVAILABILITY,
        provider_label="No AI provider",
        provider_kind="none",
        status_label="AI unavailable",
        disabled_reason="No local or remote provider is configured",
        selected_provider_id=NO_PROVIDER_ID,
        provider_selection_state=NO_PROVIDER_FALLBACK_SELECTION,
        provider_selection_label="No provider selected",
        provider_configuration_state=PROVIDER_CONFIGURATION_FALLBACK_ACTIVE,
        provider_configuration_label="No provider configured",
        provider_registry_state=LOCAL_PROVIDER_REGISTRY_STATE,
        provider_registry_label="Local provider registry: no configured providers",
        configured_provider_count=0,
        available_provider_count=0,
        hardware_capability_state=LOCAL_HARDWARE_CAPABILITY_STATE,
        hardware_capability_label="Hardware capability: planning only",
        gpu_capability_state=GPU_CAPABILITY_UNPROBED,
        gpu_capability_label="GPU acceleration: not evaluated",
        cpu_fallback_state=CPU_FALLBACK_PRESERVED,
        cpu_fallback_label="CPU fallback: preserved",
        power_state=POWER_STATE_NOT_EVALUATED,
        power_state_label="Power state: not evaluated",
        thermal_guardrail_state=THERMAL_GUARDRAILS_REQUIRED,
        thermal_guardrail_label="Thermal guardrails required before model workloads",
        model_workload_state=MODEL_WORKLOAD_DISABLED,
        model_workload_label="Model workloads: disabled",
        capability_recommendation_state=CAPABILITY_RECOMMENDATION_PENDING,
        capability_recommendation_label="Capability recommendation pending",
        **_foundation_readiness_fields(),
        privacy_scope=NO_PROVIDER_PRIVACY_SCOPE,
        privacy_label="Local shell only; nothing is sent",
        provider_visible_data="none",
        provider_visible_data_label="Provider-visible data: none",
        **_provider_boundary_interaction_fields(
            interaction_label="Provider boundary plan: no-provider fallback",
            interaction_detail="Choose and approve a provider before AI prompts can run",
        ),
        local_storage="none",
        consent_state="not required until a provider is configured",
        consent_label="No provider consent requested",
        interaction_affordance=NO_PROVIDER_INTERACTION_AFFORDANCE,
        interaction_label="Assisted Desktop unavailable",
        interaction_disabled_reason="Choose and approve a provider before AI prompts can run",
        no_provider_fallback_label="No-provider fallback active",
        prompt_acceptance="disabled",
        external_calls="blocked",
        model_state="not installed",
        capability_pack_state="not installed",
        source_truth="renderer-local no-provider shell",
        **_runtime_contract_fields(
            category=PROVIDER_RUNTIME_CATEGORY_NO_PROVIDER,
            reason_code=PROVIDER_RUNTIME_REASON_NO_PROVIDER_CONFIGURED,
        ),
        surface_role=normalized_surface,
        provider_options=_provider_selection_options(),
    )


def build_local_ai_runtime_foundation_provider_boundary_state(
    *,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Build the active local-only FAM-007 runtime-foundation provider boundary."""

    normalized_surface = surface_role if surface_role in {"core", "hud", "combined"} else "hud"
    return AIProviderStateSnapshot(
        package_id=PACKAGE_ID,
        slice_ids=(SLC_017_ID, SLC_018_ID),
        state_id=LOCAL_AI_RUNTIME_FOUNDATION_STATE_ID,
        mode=LOCAL_AI_RUNTIME_FOUNDATION_MODE,
        availability=LOCAL_AI_RUNTIME_FOUNDATION_AVAILABILITY,
        provider_label="No AI provider",
        provider_kind="local-runtime-foundation-scaffold",
        status_label="Local AI foundation: no provider",
        disabled_reason="Local AI runtime foundation is active, but provider execution is disabled",
        selected_provider_id=NO_PROVIDER_ID,
        provider_selection_state=NO_PROVIDER_FALLBACK_SELECTION,
        provider_selection_label="No-provider fallback active",
        provider_configuration_state=PROVIDER_CONFIGURATION_UNCONFIGURED,
        provider_configuration_label="Provider configuration: none",
        provider_registry_state=LOCAL_PROVIDER_REGISTRY_STATE,
        provider_registry_label="Local provider registry: no configured providers",
        configured_provider_count=0,
        available_provider_count=0,
        hardware_capability_state=LOCAL_HARDWARE_CAPABILITY_STATE,
        hardware_capability_label="Hardware capability: local planning only",
        gpu_capability_state=GPU_CAPABILITY_UNPROBED,
        gpu_capability_label="GPU acceleration: unprobed; no model workload active",
        cpu_fallback_state=CPU_FALLBACK_PRESERVED,
        cpu_fallback_label="CPU fallback: preserved",
        power_state=POWER_STATE_NOT_EVALUATED,
        power_state_label="Power state: not evaluated",
        thermal_guardrail_state=THERMAL_GUARDRAILS_REQUIRED,
        thermal_guardrail_label="Thermal guardrails required before model workloads",
        model_workload_state=MODEL_WORKLOAD_DISABLED,
        model_workload_label="Model workloads: disabled",
        capability_recommendation_state=CAPABILITY_RECOMMENDATION_PENDING,
        capability_recommendation_label="Capability recommendation pending hardware proof",
        **_foundation_readiness_fields(),
        privacy_scope=NO_PROVIDER_PRIVACY_SCOPE,
        privacy_label="Local runtime foundation only; nothing is sent",
        provider_visible_data="none",
        provider_visible_data_label="Provider-visible data: none",
        **_provider_boundary_interaction_fields(
            interaction_label="Provider boundary: local foundation active",
            interaction_detail="Local runtime foundation is visible while provider calls and prompts stay disabled",
        ),
        local_storage="none",
        consent_state=PROVIDER_CONSENT_REQUIRED,
        consent_label="Consent required before any provider setup",
        interaction_affordance=NO_PROVIDER_INTERACTION_AFFORDANCE,
        interaction_label="Assisted Desktop unavailable",
        interaction_disabled_reason="Local AI foundation is provider-disabled; consent and configuration are required before prompts can run",
        no_provider_fallback_label="No-provider fallback active",
        prompt_acceptance="disabled",
        external_calls="blocked",
        model_state="not installed",
        capability_pack_state="not installed",
        source_truth="renderer-local FAM-007 runtime foundation provider boundary",
        **_runtime_contract_fields(
            category=PROVIDER_RUNTIME_CATEGORY_SETUP_DISABLED,
            reason_code=PROVIDER_RUNTIME_REASON_SETUP_DISABLED_LOCAL_ONLY,
        ),
        surface_role=normalized_surface,
        provider_options=_provider_selection_options(),
    )


def build_provider_selection_consent_state(
    *,
    selected_provider_id: str = NO_PROVIDER_ID,
    surface_role: str = "hud",
) -> AIProviderStateSnapshot:
    """Build the local-only provider-selection scaffold with no-provider fallback."""

    normalized_surface = surface_role if surface_role in {"core", "hud", "combined"} else "hud"
    valid_provider_ids = {option.provider_id for option in _provider_selection_options()}
    requested_provider_id = selected_provider_id if selected_provider_id in valid_provider_ids else NO_PROVIDER_ID
    normalized_provider_id = NO_PROVIDER_ID if requested_provider_id != NO_PROVIDER_ID else requested_provider_id

    return AIProviderStateSnapshot(
        package_id=PACKAGE_ID,
        slice_ids=(SLC_017_ID, SLC_018_ID),
        state_id=PROVIDER_SELECTION_STATE_ID,
        mode=PROVIDER_SELECTION_MODE,
        availability=PROVIDER_SELECTION_AVAILABILITY,
        provider_label="No provider selected",
        provider_kind="selection-scaffold",
        status_label="Provider consent required",
        disabled_reason="Provider selection requires explicit consent and configuration",
        selected_provider_id=normalized_provider_id,
        provider_selection_state=NO_PROVIDER_FALLBACK_SELECTION,
        provider_selection_label="No-provider fallback active",
        provider_configuration_state=PROVIDER_CONFIGURATION_UNCONFIGURED,
        provider_configuration_label="No provider configured",
        provider_registry_state=LOCAL_PROVIDER_REGISTRY_STATE,
        provider_registry_label="Local provider registry: no configured providers",
        configured_provider_count=0,
        available_provider_count=0,
        hardware_capability_state=LOCAL_HARDWARE_CAPABILITY_STATE,
        hardware_capability_label="Hardware capability: planning only",
        gpu_capability_state=GPU_CAPABILITY_UNPROBED,
        gpu_capability_label="GPU acceleration: not evaluated",
        cpu_fallback_state=CPU_FALLBACK_PRESERVED,
        cpu_fallback_label="CPU fallback: preserved",
        power_state=POWER_STATE_NOT_EVALUATED,
        power_state_label="Power state: not evaluated",
        thermal_guardrail_state=THERMAL_GUARDRAILS_REQUIRED,
        thermal_guardrail_label="Thermal guardrails required before model workloads",
        model_workload_state=MODEL_WORKLOAD_DISABLED,
        model_workload_label="Model workloads: disabled",
        capability_recommendation_state=CAPABILITY_RECOMMENDATION_PENDING,
        capability_recommendation_label="Capability recommendation pending",
        **_foundation_readiness_fields(),
        privacy_scope=NO_PROVIDER_PRIVACY_SCOPE,
        privacy_label="Local selection only; nothing is sent",
        provider_visible_data="none",
        provider_visible_data_label="Provider-visible data: none",
        **_provider_boundary_interaction_fields(
            interaction_label="Provider boundary plan: consent required",
            interaction_detail="Provider selection remains local-only until consent and configuration are complete",
        ),
        local_storage="none",
        consent_state=PROVIDER_CONSENT_REQUIRED,
        consent_label="Consent required before a provider can be configured",
        interaction_affordance=NO_PROVIDER_INTERACTION_AFFORDANCE,
        interaction_label="Assisted Desktop setup paused",
        interaction_disabled_reason="Consent and provider configuration are required before prompts can run",
        no_provider_fallback_label="No-provider fallback active",
        prompt_acceptance="disabled",
        external_calls="blocked",
        model_state="not installed",
        capability_pack_state="not installed",
        source_truth="renderer-local provider-selection consent scaffold",
        **_runtime_contract_fields(
            category=PROVIDER_RUNTIME_CATEGORY_CONSENT_MISSING,
            reason_code=PROVIDER_RUNTIME_REASON_CONSENT_REQUIRED,
        ),
        surface_role=normalized_surface,
        provider_options=_provider_selection_options(),
    )


def build_local_provider_registry_state(*, surface_role: str = "hud") -> AIProviderStateSnapshot:
    """Build the local-only provider registry/configuration scaffold."""

    normalized_surface = surface_role if surface_role in {"core", "hud", "combined"} else "hud"
    return AIProviderStateSnapshot(
        package_id=PACKAGE_ID,
        slice_ids=(SLC_017_ID, SLC_018_ID),
        state_id=LOCAL_PROVIDER_REGISTRY_STATE_ID,
        mode=LOCAL_PROVIDER_REGISTRY_MODE,
        availability=LOCAL_PROVIDER_REGISTRY_AVAILABILITY,
        provider_label="No provider configured",
        provider_kind="local-registry-scaffold",
        status_label="Provider setup unavailable",
        disabled_reason="Provider registry is local-only and no AI provider is configured",
        selected_provider_id=NO_PROVIDER_ID,
        provider_selection_state=NO_PROVIDER_FALLBACK_SELECTION,
        provider_selection_label="No-provider fallback active",
        provider_configuration_state=PROVIDER_CONFIGURATION_UNCONFIGURED,
        provider_configuration_label="Provider configuration: none",
        provider_registry_state=LOCAL_PROVIDER_REGISTRY_STATE,
        provider_registry_label="Local provider registry: no configured providers",
        configured_provider_count=0,
        available_provider_count=0,
        hardware_capability_state=LOCAL_HARDWARE_CAPABILITY_STATE,
        hardware_capability_label="Hardware capability: planning only",
        gpu_capability_state=GPU_CAPABILITY_UNPROBED,
        gpu_capability_label="GPU acceleration: not evaluated",
        cpu_fallback_state=CPU_FALLBACK_PRESERVED,
        cpu_fallback_label="CPU fallback: preserved",
        power_state=POWER_STATE_NOT_EVALUATED,
        power_state_label="Power state: not evaluated",
        thermal_guardrail_state=THERMAL_GUARDRAILS_REQUIRED,
        thermal_guardrail_label="Thermal guardrails required before model workloads",
        model_workload_state=MODEL_WORKLOAD_DISABLED,
        model_workload_label="Model workloads: disabled",
        capability_recommendation_state=CAPABILITY_RECOMMENDATION_PENDING,
        capability_recommendation_label="Capability recommendation pending",
        **_foundation_readiness_fields(),
        privacy_scope=NO_PROVIDER_PRIVACY_SCOPE,
        privacy_label="Local registry only; nothing is sent",
        provider_visible_data="none",
        provider_visible_data_label="Provider-visible data: none",
        **_provider_boundary_interaction_fields(
            interaction_label="Provider boundary plan: registry local-only",
            interaction_detail="Provider configuration remains unconfigured and no-provider fallback stays active",
        ),
        local_storage="none",
        consent_state=PROVIDER_CONSENT_REQUIRED,
        consent_label="Consent required before provider configuration",
        interaction_affordance=NO_PROVIDER_INTERACTION_AFFORDANCE,
        interaction_label="Provider setup paused",
        interaction_disabled_reason="Provider configuration is local-only and requires consent before prompts can run",
        no_provider_fallback_label="No-provider fallback active",
        prompt_acceptance="disabled",
        external_calls="blocked",
        model_state="not installed",
        capability_pack_state="not installed",
        source_truth="renderer-local provider registry configuration scaffold",
        **_runtime_contract_fields(
            category=PROVIDER_RUNTIME_CATEGORY_UNCONFIGURED,
            reason_code=PROVIDER_RUNTIME_REASON_PROVIDER_UNCONFIGURED,
        ),
        surface_role=normalized_surface,
        provider_options=_provider_selection_options(),
    )


def build_local_hardware_capability_state(*, surface_role: str = "hud") -> AIProviderStateSnapshot:
    """Build the local-only hardware/capability planning scaffold.

    This records visible planning posture only. It does not probe hardware,
    choose acceleration, run model workloads, or make provider calls.
    """

    normalized_surface = surface_role if surface_role in {"core", "hud", "combined"} else "hud"
    return AIProviderStateSnapshot(
        package_id=PACKAGE_ID,
        slice_ids=(SLC_017_ID, SLC_018_ID, SLC_031_ID),
        state_id=LOCAL_HARDWARE_CAPABILITY_STATE_ID,
        mode=LOCAL_HARDWARE_CAPABILITY_MODE,
        availability=LOCAL_HARDWARE_CAPABILITY_AVAILABILITY,
        provider_label="No provider configured",
        provider_kind="local-hardware-planning-scaffold",
        status_label="Hardware capability planning",
        disabled_reason="Hardware capability planning is local-only and model workloads are disabled",
        selected_provider_id=NO_PROVIDER_ID,
        provider_selection_state=NO_PROVIDER_FALLBACK_SELECTION,
        provider_selection_label="No-provider fallback active",
        provider_configuration_state=PROVIDER_CONFIGURATION_UNCONFIGURED,
        provider_configuration_label="Provider configuration: none",
        provider_registry_state=LOCAL_PROVIDER_REGISTRY_STATE,
        provider_registry_label="Local provider registry: no configured providers",
        configured_provider_count=0,
        available_provider_count=0,
        hardware_capability_state=LOCAL_HARDWARE_CAPABILITY_STATE,
        hardware_capability_label="Hardware capability: local planning only",
        gpu_capability_state=GPU_CAPABILITY_UNPROBED,
        gpu_capability_label="GPU acceleration: unprobed; no model workload active",
        cpu_fallback_state=CPU_FALLBACK_PRESERVED,
        cpu_fallback_label="CPU fallback: preserved",
        power_state=POWER_STATE_NOT_EVALUATED,
        power_state_label="Power state: not evaluated",
        thermal_guardrail_state=THERMAL_GUARDRAILS_REQUIRED,
        thermal_guardrail_label="Thermal guardrails required before model workloads",
        model_workload_state=MODEL_WORKLOAD_DISABLED,
        model_workload_label="Model workloads: disabled",
        capability_recommendation_state=CAPABILITY_RECOMMENDATION_PENDING,
        capability_recommendation_label="Capability recommendation pending hardware proof",
        **_foundation_readiness_fields(),
        privacy_scope=NO_PROVIDER_PRIVACY_SCOPE,
        privacy_label="Local capability planning only; nothing is sent",
        provider_visible_data="none",
        provider_visible_data_label="Provider-visible data: none",
        **_provider_boundary_interaction_fields(
            interaction_label="Provider boundary plan: capability proof first",
            interaction_detail="Hardware proof and consent are required before model workloads can run",
        ),
        local_storage="none",
        consent_state=PROVIDER_CONSENT_REQUIRED,
        consent_label="Consent required before provider or capability setup",
        interaction_affordance=NO_PROVIDER_INTERACTION_AFFORDANCE,
        interaction_label="Hardware capability planning only",
        interaction_disabled_reason="Hardware proof and consent are required before model workloads can run",
        no_provider_fallback_label="No-provider fallback active",
        prompt_acceptance="disabled",
        external_calls="blocked",
        model_state="not installed",
        capability_pack_state="not installed",
        source_truth="renderer-local hardware capability planning scaffold",
        **_runtime_contract_fields(
            category=PROVIDER_RUNTIME_CATEGORY_CAPABILITY_MISSING,
            reason_code=PROVIDER_RUNTIME_REASON_CAPABILITY_MISSING,
        ),
        surface_role=normalized_surface,
        provider_options=_provider_selection_options(),
    )


def build_slc005_enforcement_proof_contract() -> dict[str, object]:
    """Build SLC-005 proof that every gated AI/private path remains blocked."""

    return {
        "schema": SLC005_ENFORCEMENT_PROOF_SCHEMA_VERSION,
        "proofScope": (
            "provider-model-execution",
            "prompt-acceptance-send",
            "downloads-install-execution",
            "runtime-cache-behavior",
            "memory-learning-personalization",
            "private-developer-owner-setup",
            "hidden-network-behavior",
        ),
        "blockedBehaviorMatrix": {
            "providerModelExecution": {
                "promptProviderModelExecution": "disabled",
                "providerSdkIntegrated": False,
                "modelExecutionEnabled": False,
                "modelDownloadsEnabled": False,
                "runtimeProviderExecutionEnabled": False,
                "providerExecutionGateState": PROVIDER_EXECUTION_GATE_DISABLED,
                "modelExecutionGateState": MODEL_EXECUTION_GATE_DISABLED,
            },
            "promptSend": {
                "promptAcceptance": "disabled",
                "promptAcceptanceGateState": PROMPT_ACCEPTANCE_GATE_DISABLED,
                "promptRoutingGateState": PROMPT_ROUTING_GATE_DISABLED,
                "promptSendPosture": PROMPT_SEND_POSTURE_DISABLED,
                "sentToProvider": False,
                "canAcceptPrompts": False,
                "providerVisibleData": "none",
            },
            "downloads": {
                "downloadsNetworkExternalCalls": "blocked",
                "capabilityPackDownloadsBlocked": True,
                "capabilityPackInstallBlocked": True,
                "capabilityPackUpdateBlocked": True,
                "capabilityPackUninstallBlocked": True,
                "installIntentState": CAPABILITY_PACK_INSTALL_INTENT_BLOCKED,
                "modelDownloadsEnabled": False,
            },
            "runtimeCache": {
                "cacheConsentState": "blocked-pending-user-cache-approval",
                "cacheIsNotMemory": True,
                "runtimeCacheBehaviorEnabled": False,
                "runtimeCacheState": "inactive",
            },
            "memory": {
                "memoryConsentState": "blocked-pending-user-memory-approval",
                "memoryContextState": MEMORY_CONTEXT_DISABLED,
                "memoryIndexingState": MEMORY_INDEXING_DISABLED,
                "retrievalState": RETRIEVAL_DISABLED,
                "learningState": LEARNING_DISABLED,
                "persistenceState": PERSISTENCE_DISABLED,
                "memoryWriteEnabled": False,
                "realOwnerMemoryEnabled": False,
                "realOwnerAgentsEnabled": False,
            },
            "privateSetup": {
                "privateSetupBoundaryState": PRIVATE_SETUP_BOUNDARY_BLOCKED,
                "privateSetupAuthorized": False,
                "privateMaterialVisible": False,
                "privateRepoCreated": False,
                "privateRootCreated": False,
                "privateRemoteConfigured": False,
                "developerLaneBoundaryState": DEVELOPER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED,
                "ownerLaneBoundaryState": OWNER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED,
            },
            "hiddenNetworkBehavior": {
                "networkEgressState": NETWORK_EGRESS_BLOCKED,
                "networkEgressGateState": NETWORK_EGRESS_BLOCKED,
                "externalCallsEnabled": False,
                "externalCallReadinessState": EXTERNAL_CALL_READINESS_BLOCKED,
                "hiddenExternalDependenciesAllowed": False,
                "providerNetworkRequirementPosture": PROVIDER_NETWORK_REQUIREMENT_BLOCKED,
            },
        },
        "negativeCanaries": (
            {
                "caseId": "provider-model-execution-attempt",
                "blockedBehavior": "providerModelExecution",
                "attemptedEnablement": "providerSdkIntegrated=true",
                "expectedOutcome": "blocked",
            },
            {
                "caseId": "prompt-send-attempt",
                "blockedBehavior": "promptSend",
                "attemptedEnablement": "canAcceptPrompts=true",
                "expectedOutcome": "blocked",
            },
            {
                "caseId": "capability-download-attempt",
                "blockedBehavior": "downloads",
                "attemptedEnablement": "capabilityPackDownloadsBlocked=false",
                "expectedOutcome": "blocked",
            },
            {
                "caseId": "runtime-cache-enable-attempt",
                "blockedBehavior": "runtimeCache",
                "attemptedEnablement": "runtimeCacheBehaviorEnabled=true",
                "expectedOutcome": "blocked",
            },
            {
                "caseId": "memory-indexing-attempt",
                "blockedBehavior": "memory",
                "attemptedEnablement": "memoryWriteEnabled=true",
                "expectedOutcome": "blocked",
            },
            {
                "caseId": "private-setup-attempt",
                "blockedBehavior": "privateSetup",
                "attemptedEnablement": "privateSetupAuthorized=true",
                "expectedOutcome": "blocked",
            },
            {
                "caseId": "hidden-network-attempt",
                "blockedBehavior": "hiddenNetworkBehavior",
                "attemptedEnablement": "hiddenExternalDependenciesAllowed=true",
                "expectedOutcome": "blocked",
            },
        ),
    }


def build_owner_ai_operational_foundation_gates_state() -> dict[str, object]:
    """Build the public-safe FAM-007 Owner AI foundation gate contract."""

    return {
        "schema": OWNER_AI_OPERATIONAL_FOUNDATION_GATES_SCHEMA_VERSION,
        "packageId": PACKAGE_ID,
        "protectedArtifactExclusion": {
            "protectedClasses": OWNER_AI_PROTECTED_ARTIFACT_CLASSES,
            "publicExclusionTargets": OWNER_AI_PUBLIC_EXCLUSION_TARGETS,
            "ownerPrivateMaterialAllowed": False,
            "privateDevMaterialAllowed": False,
            "privatePathAllowed": False,
            "secretAllowed": False,
            "privateModelOrCapabilityAssetAllowed": False,
        },
        "providerRuntimeDisabledState": {
            "providerVisibleData": "none",
            "providerVisibleDataGuarantee": PROVIDER_VISIBLE_DATA_GUARANTEE_NONE,
            "sentToProvider": False,
            "canAcceptPrompts": False,
            "promptProviderModelExecution": "disabled",
            "providerSdkIntegrated": False,
            "modelExecutionEnabled": False,
            "modelDownloadsEnabled": False,
            "runtimeProviderExecutionEnabled": False,
            "downloadsNetworkExternalCalls": "blocked",
            "networkEgressState": NETWORK_EGRESS_BLOCKED,
            "externalCallsEnabled": False,
        },
        "consentStateGates": {
            "cacheConsentState": "blocked-pending-user-cache-approval",
            "memoryConsentState": "blocked-pending-user-memory-approval",
            "cacheIsNotMemory": True,
            "runtimeCacheBehaviorEnabled": False,
            "memoryContextState": MEMORY_CONTEXT_DISABLED,
            "memoryIndexingState": MEMORY_INDEXING_DISABLED,
            "retrievalState": RETRIEVAL_DISABLED,
            "learningState": LEARNING_DISABLED,
            "persistenceState": PERSISTENCE_DISABLED,
            "memoryWriteEnabled": False,
            "consentErrorState": "blocked-state-visible-route-back-required",
        },
        "capabilityInstallIntentGates": {
            "installIntentState": CAPABILITY_PACK_INSTALL_INTENT_BLOCKED,
            "installIntentRequiredBeforeInstall": True,
            "pendingInstallState": "blocked-pending-explicit-user-install-intent",
            "capabilityPackDownloadsBlocked": True,
            "capabilityPackInstallBlocked": True,
            "capabilityPackUpdateBlocked": True,
            "capabilityPackUninstallBlocked": True,
        },
        "laneReadinessGates": {
            "userPublicLane": {
                "laneIdentity": "public-user-lane",
                "privateSetupRequired": False,
                "readinessState": "public-safe-gates-present",
                "boundaryDisplayState": PUBLIC_LANE_BOUNDARY_LOCAL_ASSIST_ONLY,
                "boundaryDisplayLabel": "Public Edition: deterministic no-provider assist; provider-visible data none",
            },
            "developerLane": {
                "laneIdentity": "developer-lane-future-gated",
                "privateRepoCreated": False,
                "privateRootCreated": False,
                "privateRemoteConfigured": False,
                "readinessState": "blocked-pending-user-private-dev-setup-approval",
                "boundaryDisplayState": DEVELOPER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED,
                "boundaryDisplayLabel": "Developer lane: gated; private setup not configured",
                "privateSetupAuthorized": False,
                "privateMaterialVisible": False,
            },
            "ownerLane": {
                "laneIdentity": "owner-lane-future-gated",
                "privateRepoCreated": False,
                "privateRootCreated": False,
                "privateRemoteConfigured": False,
                "readinessState": "blocked-pending-user-owner-setup-approval",
                "boundaryDisplayState": OWNER_LANE_BOUNDARY_PRIVATE_SETUP_BLOCKED,
                "boundaryDisplayLabel": "Owner lane: gated; private setup not configured",
                "privateSetupAuthorized": False,
                "privateMaterialVisible": False,
            },
        },
        "ownerAiMemoryAgentFoundationSchemas": {
            "memoryPrerequisiteSchema": "owner-ai-memory-prerequisites.v1",
            "agentPrerequisiteSchema": "owner-ai-agent-prerequisites.v1",
            "memoryBlockedState": "blocked-pending-user-owner-memory-approval",
            "agentBlockedState": "blocked-pending-user-owner-agent-approval",
            "realOwnerMemoryEnabled": False,
            "realOwnerAgentsEnabled": False,
            "publicSafeExamplesOnly": True,
        },
        "forbiddenMaterialPresence": {
            "privateRemoteUrl": False,
            "tokenOrCredential": False,
            "ownerSecret": False,
            "privatePath": False,
            "promptPayload": False,
            "memoryPayload": False,
            "privateAutomation": False,
            "modelArtifact": False,
            "capabilityPackAsset": False,
            "privateHostingSecret": False,
        },
        "slc005EnforcementProof": build_slc005_enforcement_proof_contract(),
    }


def build_fam007_foundation_readiness_state(*, surface_role: str = "hud") -> AIProviderStateSnapshot:
    """Build the local-only all-slice FAM-007 Workstream readiness scaffold."""

    normalized_surface = surface_role if surface_role in {"core", "hud", "combined"} else "hud"
    return AIProviderStateSnapshot(
        package_id=PACKAGE_ID,
        slice_ids=(
            SLC_017_ID,
            SLC_018_ID,
            SLC_031_ID,
            SLC_032_ID,
            SLC_033_ID,
            SLC_034_ID,
            SLC_035_ID,
            SLC_036_ID,
        ),
        state_id=FAM007_FOUNDATION_READINESS_STATE_ID,
        mode=FAM007_FOUNDATION_READINESS_MODE,
        availability=FAM007_FOUNDATION_READINESS_AVAILABILITY,
        provider_label="No provider configured",
        provider_kind="local-foundation-readiness-scaffold",
        status_label="FAM-007 foundation readiness",
        disabled_reason="All admitted FAM-007 branch-material seams are local-only and provider execution is disabled",
        selected_provider_id=NO_PROVIDER_ID,
        provider_selection_state=NO_PROVIDER_FALLBACK_SELECTION,
        provider_selection_label="No-provider fallback active",
        provider_configuration_state=PROVIDER_CONFIGURATION_UNCONFIGURED,
        provider_configuration_label="Provider configuration: none",
        provider_registry_state=LOCAL_PROVIDER_REGISTRY_STATE,
        provider_registry_label="Local provider registry: no configured providers",
        configured_provider_count=0,
        available_provider_count=0,
        hardware_capability_state=LOCAL_HARDWARE_CAPABILITY_STATE,
        hardware_capability_label="Hardware capability: local planning only",
        gpu_capability_state=GPU_CAPABILITY_UNPROBED,
        gpu_capability_label="GPU acceleration: unprobed; no model workload active",
        cpu_fallback_state=CPU_FALLBACK_PRESERVED,
        cpu_fallback_label="CPU fallback: preserved",
        power_state=POWER_STATE_NOT_EVALUATED,
        power_state_label="Power state: not evaluated",
        thermal_guardrail_state=THERMAL_GUARDRAILS_REQUIRED,
        thermal_guardrail_label="Thermal guardrails required before model workloads",
        model_workload_state=MODEL_WORKLOAD_DISABLED,
        model_workload_label="Model workloads: disabled",
        capability_recommendation_state=CAPABILITY_RECOMMENDATION_PENDING,
        capability_recommendation_label="Capability recommendation pending hardware proof",
        **_foundation_readiness_fields(),
        privacy_scope=NO_PROVIDER_PRIVACY_SCOPE,
        privacy_label="Local foundation planning only; nothing is sent",
        provider_visible_data="none",
        provider_visible_data_label="Provider-visible data: none",
        **_provider_boundary_interaction_fields(
            interaction_label="Provider boundary plan: local foundation only",
            interaction_detail="Provider consent, capability proof, and future USER approval are required before AI prompts can run",
        ),
        local_storage="none",
        consent_state=PROVIDER_CONSENT_REQUIRED,
        consent_label="Consent required before provider or capability setup",
        interaction_affordance=NO_PROVIDER_INTERACTION_AFFORDANCE,
        interaction_label="FAM-007 foundation readiness only",
        interaction_disabled_reason="Provider consent, capability proof, and future USER approval are required before AI prompts can run",
        no_provider_fallback_label="No-provider fallback active",
        prompt_acceptance="disabled",
        external_calls="blocked",
        model_state="not installed",
        capability_pack_state="not installed",
        source_truth="renderer-local FAM-007 foundation readiness scaffold",
        **_runtime_contract_fields(
            category=PROVIDER_RUNTIME_CATEGORY_READY_FUTURE_GATED,
            reason_code=PROVIDER_RUNTIME_REASON_READY_FUTURE_GATED,
        ),
        surface_role=normalized_surface,
        provider_options=_provider_selection_options(),
    )
