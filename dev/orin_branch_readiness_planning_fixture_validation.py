# NEXUS-SOURCE-OWNER: schema=source-owner-v1; owner=VALIDATOR-HELPER; ledger=SRCOWN-FIRSTPASS-VALIDATOR-010; surface=branch-readiness-planning-fixture-validator; status=shared
"""Regression fixtures for Branch Readiness product-system planning.

The governance validator is intentionally broad and source-truth heavy. This
fixture helper keeps one small regression seam focused on the failure pattern
where a broad implementation branch reaches a later phase with marker-only
planning.
"""

from __future__ import annotations

import json
import inspect
import re
import tempfile
import warnings
import zipfile
from pathlib import Path

import orin_branch_governance_validation as governance
import orin_external_state_validation as external_state
import orin_external_state_target_currentness_fixture_validation as target_currentness_fixture
from orin_external_state_common import DEFAULT_EXTERNAL_STATE_ROOT
from nexus_paths import WORKTREES_ROOT
import orin_rar_issue_candidate_durability_validation as rar_issue_durability
import orin_user_review_bundle as review_bundle
import orin_worktree_rebaseline_audit as rebaseline


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "dev" / "fixtures" / "branch_readiness_planning"
PR_REVIEW_CHURN_MATRIX_FIXTURE = (
    ROOT
    / "dev"
    / "fixtures"
    / "pr_review_churn"
    / "pr_276_rar_review_churn_matrix.json"
)
UI_REFERENCE_CATALOG_README = ROOT / "Docs" / "ui_reference_catalog" / "README.md"
FIXTURE_ORIGIN_MAIN = "b" * 40


def _pr_review_churn_receipt_exceeds_budget(
    connector_comments: object,
    total_budget: object,
    family_counts: object,
    same_family_budget: object,
) -> bool:
    """A root-cause receipt is required when total OR same-family churn exceeds budget."""
    over_total = (
        isinstance(connector_comments, int)
        and isinstance(total_budget, int)
        and connector_comments > total_budget
    )
    over_family = (
        isinstance(family_counts, dict)
        and isinstance(same_family_budget, int)
        and any(
            isinstance(count, int) and count > same_family_budget
            for count in family_counts.values()
        )
    )
    return over_total or over_family


SHALLOW_FIXTURE = FIXTURE_DIR / "shallow_live_validation_product_plan.md"
CONCRETE_FIXTURE = FIXTURE_DIR / "concrete_live_validation_product_plan.md"
VALID_BRANCH_RUNTIME_PLAN_FIXTURE = (
    FIXTURE_DIR / "valid_branch_runtime_engineering_plan.md"
)
SHALLOW_BRANCH_RUNTIME_PLAN_FIXTURE = (
    FIXTURE_DIR / "shallow_branch_runtime_engineering_plan.md"
)
BACKLOG_SPRAWL_FIXTURE = FIXTURE_DIR / "invalid_backlog_planning_sprawl.md"
FOLD_DOWN_FIXTURE = FIXTURE_DIR / "valid_pr_fold_down_packet.md"
VALID_BRANCH_VISION_CONTRACT_FIXTURE = (
    FIXTURE_DIR / "valid_branch_vision_contract_snapshot.md"
)
INVALID_PROPOSED_BRANCH_VISION_CONTRACT_FIXTURE = (
    FIXTURE_DIR / "invalid_proposed_branch_vision_contract_snapshot.md"
)
INVALID_BLOCKING_BRANCH_VISION_CONTRACT_FIXTURE = (
    FIXTURE_DIR / "invalid_blocking_branch_vision_question.md"
)
VALID_USER_FEEDBACK_DISPOSITION_FIXTURE = (
    FIXTURE_DIR / "valid_user_feedback_disposition.md"
)
VALID_USER_FEEDBACK_UNICODE_SUMMARY_FIXTURE = (
    FIXTURE_DIR / "valid_user_feedback_unicode_summary.md"
)
INVALID_USER_FEEDBACK_NO_OWNER_FIXTURE = (
    FIXTURE_DIR / "invalid_user_feedback_no_durable_owner.md"
)
INVALID_USER_FEEDBACK_BAD_ID_FIXTURE = (
    FIXTURE_DIR / "invalid_user_feedback_bad_id.md"
)
INVALID_USER_FEEDBACK_DUPLICATE_SUMMARY_FIXTURE = (
    FIXTURE_DIR / "invalid_user_feedback_duplicate_summary.md"
)
VALID_REBASELINE_OVERLAP_INTENT_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_overlap_intent.md"
)
INVALID_REBASELINE_OVERLAP_UNKNOWN_HIGH_RISK_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_overlap_unknown_high_risk.md"
)
INVALID_REBASELINE_OVERLAP_FALLBACK_ONLY_PASS_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_overlap_fallback_only_pass.md"
)
VALID_REBASELINE_OVERLAP_LOW_RISK_WARN_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_overlap_low_risk_warn.md"
)
INVALID_REBASELINE_OVERLAP_FIXTURE_HIGH_IMPACT_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_overlap_fixture_high_impact.md"
)
VALID_REBASELINE_OVERLAP_FIXTURE_LOW_IMPACT_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_overlap_fixture_low_impact.md"
)
VALID_ELEMENT_TO_PHASE_MATRIX_FIXTURE = (
    FIXTURE_DIR / "valid_element_to_phase_proof_matrix.md"
)
INVALID_ELEMENT_TO_PHASE_MISSING_HARDENING_FIXTURE = (
    FIXTURE_DIR / "invalid_element_to_phase_missing_hardening.md"
)
INVALID_ELEMENT_TO_PHASE_MISSING_LIVE_VALIDATION_FIXTURE = (
    FIXTURE_DIR / "invalid_element_to_phase_missing_live_validation.md"
)
VALID_ELEMENT_TO_PHASE_DEFERRED_FUTURE_FIXTURE = (
    FIXTURE_DIR / "valid_element_to_phase_deferred_future.md"
)
INVALID_ELEMENT_TO_PHASE_DUPLICATE_ID_FIXTURE = (
    FIXTURE_DIR / "invalid_element_to_phase_duplicate_id.md"
)
VALID_WORKSTREAM_ENTRY_WHOLE_PACKAGE_FIXTURE = (
    FIXTURE_DIR / "valid_workstream_entry_whole_package_analysis.md"
)
INVALID_WORKSTREAM_ENTRY_FIRST_SEAM_ONLY_FIXTURE = (
    FIXTURE_DIR / "invalid_workstream_entry_first_seam_only.md"
)
VALID_USER_BRANCH_PLAN_REVIEW_FIXTURE = (
    FIXTURE_DIR / "valid_user_branch_plan_review_gate.md"
)
INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_OUTCOME_FIXTURE = (
    FIXTURE_DIR / "invalid_user_branch_plan_review_missing_outcome.md"
)
INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_PACKET_FINDING_FIXTURE = (
    FIXTURE_DIR / "invalid_user_branch_plan_review_missing_packet_finding.md"
)
INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_HARDENING_FIXTURE = (
    FIXTURE_DIR / "invalid_user_branch_plan_review_missing_hardening.md"
)
INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_LIVE_VALIDATION_FIXTURE = (
    FIXTURE_DIR / "invalid_user_branch_plan_review_missing_live_validation.md"
)
INVALID_USER_BRANCH_PLAN_REVIEW_FIRST_SEAM_ONLY_FIXTURE = (
    FIXTURE_DIR / "invalid_user_branch_plan_review_first_seam_only.md"
)
INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_RESPONSE_DIGEST_FIXTURE = (
    FIXTURE_DIR / "invalid_user_branch_plan_review_missing_response_digest.md"
)
VALID_USER_BRANCH_PLAN_REVIEW_DEFERRED_SCOPE_FIXTURE = (
    FIXTURE_DIR / "valid_user_branch_plan_review_deferred_scope.md"
)
VALID_BRANCH_PLANNING_GATE_STATE_FIXTURE = (
    FIXTURE_DIR / "valid_branch_planning_review_gate_state.md"
)
INVALID_BRANCH_PLANNING_GATE_BYPASS_FIXTURE = (
    FIXTURE_DIR / "invalid_packet_validation_treated_as_user_acceptance.md"
)
VALID_BP1_BRANCH_VISION_REVIEW_FIXTURE = (
    FIXTURE_DIR / "valid_bp1_branch_vision_review.md"
)
VALID_BP1_FAM006_DOGFOOD_FIXTURE = (
    FIXTURE_DIR / "valid_bp1_fam006_ui_runtime_dogfood_review.md"
)
VALID_BP1_FAM007_DOGFOOD_FIXTURE = (
    FIXTURE_DIR / "valid_bp1_fam007_private_boundary_dogfood_review.md"
)
VALID_BP1_GOVERNANCE_DOGFOOD_FIXTURE = (
    FIXTURE_DIR / "valid_bp1_governance_source_truth_dogfood_review.md"
)
INVALID_BP1_MISSING_CONTEXT_FIXTURE = (
    FIXTURE_DIR / "invalid_bp1_missing_project_family_branch_context.md"
)
INVALID_BP1_SHALLOW_RECOMMENDATIONS_FIXTURE = (
    FIXTURE_DIR / "invalid_bp1_shallow_recommendations.md"
)
INVALID_BP1_TEMPLATE_SHELL_FIXTURE = (
    FIXTURE_DIR / "invalid_bp1_template_shell_review.md"
)
INVALID_BP1_PROCESS_MECHANICS_FIXTURE = (
    FIXTURE_DIR / "invalid_bp1_process_mechanics_review.md"
)
INVALID_BP1_COPIED_FILE_SURFACE_ONLY_FIXTURE = (
    FIXTURE_DIR / "invalid_bp1_copied_file_surface_map_only.md"
)
INVALID_BP1_GENERIC_USER_QUESTIONS_FIXTURE = (
    FIXTURE_DIR / "invalid_bp1_generic_user_questions.md"
)
INVALID_BP1_SLC_CENTERED_FIXTURE = (
    FIXTURE_DIR / "invalid_bp1_slc_centered_branch_vision_review.md"
)
INVALID_BP1_TECHNICAL_METADATA_FIXTURE = (
    FIXTURE_DIR / "invalid_bp1_technical_metadata.md"
)
INVALID_RUNTIME_FOCUS_ISSUE_ANCHORED_SELECTION_FIXTURE = (
    FIXTURE_DIR / "invalid_runtime_focus_issue_anchored_selection.md"
)
INVALID_RUNTIME_FOCUS_FOUNDATION_LABEL_SELECTION_FIXTURE = (
    FIXTURE_DIR / "invalid_runtime_focus_foundation_label_selection.md"
)
INVALID_BP2_MISSING_ACCEPTED_BP1_TRACE_FIXTURE = (
    FIXTURE_DIR / "invalid_bp2_missing_accepted_bp1_trace.md"
)
INVALID_BP2_PRODUCT_DESIGN_WORDING_FIXTURE = (
    FIXTURE_DIR / "invalid_bp2_product_design_contract_wording.md"
)
VALID_BP2_FAM006_DOGFOOD_FIXTURE = (
    FIXTURE_DIR / "valid_bp2_fam006_ui_runtime_dogfood_review.md"
)
VALID_BP2_FAM007_DOGFOOD_FIXTURE = (
    FIXTURE_DIR / "valid_bp2_fam007_private_boundary_dogfood_review.md"
)
INVALID_BP3_IMPLEMENTATION_WITH_PENDING_BP1_BP2_FIXTURE = (
    FIXTURE_DIR / "invalid_bp3_implementation_while_bp1_or_bp2_pending.md"
)
VALID_BP3_ACCEPTED_BP1_BP2_SLC_TRACE_FIXTURE = (
    FIXTURE_DIR / "valid_bp3_accepted_bp1_bp2_slc_traceability_complete.md"
)
VALID_BP3_FAM006_DOGFOOD_FIXTURE = (
    FIXTURE_DIR / "valid_bp3_fam006_ui_runtime_dogfood_review.md"
)
VALID_BP3_FAM007_DOGFOOD_FIXTURE = (
    FIXTURE_DIR / "valid_bp3_fam007_private_boundary_dogfood_review.md"
)
INVALID_USER_PACKET_ACTIVE_BRANCH_METADATA_FIXTURE = (
    FIXTURE_DIR / "invalid_user_packet_active_branch_metadata.md"
)
INVALID_USER_PACKET_ZIP_HASH_FIXTURE = (
    FIXTURE_DIR / "invalid_user_packet_zip_hash.md"
)
INVALID_USER_PACKET_DESKTOP_ACTIVE_UPLOAD_FIXTURE = (
    FIXTURE_DIR / "invalid_user_packet_desktop_active_upload_path.md"
)
INVALID_IMPLEMENTATION_ROUTE_PLANNING_ONLY_FIXTURE = (
    FIXTURE_DIR / "invalid_implementation_route_planning_only_lane_setup.md"
)
VALID_IMPLEMENTATION_ROUTE_SECURITY_BOUNDARY_FIXTURE = (
    FIXTURE_DIR / "valid_implementation_route_security_trust_boundary.md"
)
VALID_BR2_ROUTE_BLOCKER_PACKET_FIXTURE = (
    FIXTURE_DIR / "valid_br2_route_blocker_packet.md"
)
VALID_BR2_ROUTE_BLOCKER_NONE_WORD_ROUTE_FIXTURE = (
    FIXTURE_DIR / "valid_br2_route_blocker_none_word_route.md"
)
INVALID_BR2_ROUTE_BLOCKER_NO_ROUTE_CONTINUE_FIXTURE = (
    FIXTURE_DIR / "invalid_br2_route_blocker_no_route_continue_planning.md"
)
INVALID_BR2_ROUTE_BLOCKER_MARKER_ONLY_DEFERRAL_FIXTURE = (
    FIXTURE_DIR / "invalid_br2_route_blocker_marker_only_deferral.md"
)
INVALID_IMPLEMENTATION_ROUTE_FAKE_FEATURE_LABEL_FIXTURE = (
    FIXTURE_DIR / "invalid_implementation_route_fake_feature_label.md"
)
INVALID_IMPLEMENTATION_ROUTE_PROOF_BOUNDARY_LABEL_FIXTURE = (
    FIXTURE_DIR / "invalid_implementation_route_proof_boundary_label.md"
)
INVALID_IMPLEMENTATION_ROUTE_TBD_OUTPUT_FIXTURE = (
    FIXTURE_DIR / "invalid_implementation_route_tbd_output.md"
)
INVALID_IMPLEMENTATION_ROUTE_BLANK_SELECTED_ROUTE_FIXTURE = (
    FIXTURE_DIR / "invalid_implementation_route_blank_selected_route.md"
)
INVALID_IMPLEMENTATION_ROUTE_NEGATED_BEHAVIOR_FIXTURE = (
    FIXTURE_DIR / "invalid_implementation_route_negated_behavior.md"
)
INVALID_BR2_ROUTE_BLOCKER_PROOF_ONLY_ROUTE_FIXTURE = (
    FIXTURE_DIR / "invalid_br2_route_blocker_proof_only_route.md"
)
INVALID_SLC_SLICE_SEAM_AMBIGUITY_FIXTURE = (
    FIXTURE_DIR / "invalid_slc_slice_seam_terminology_ambiguity.md"
)
VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE = (
    FIXTURE_DIR / "valid_multi_slice_implementation_carrier.md"
)
VALID_REQUIRED_SEPARATE_BRANCH_CASE_FIXTURE = (
    FIXTURE_DIR / "valid_required_separate_branch_case.md"
)
VALID_IMPLEMENTATION_ROUTE_BP2_HOLD_ACTION_GATE_FIXTURE = (
    FIXTURE_DIR / "valid_implementation_route_bp2_hold_action_gate.md"
)
VALID_IMPLEMENTATION_ROUTE_RETARGET_RENAME_FIXTURE = (
    FIXTURE_DIR / "valid_implementation_route_retarget_rename.md"
)
VALID_MERGE_STABLE_SOURCE_TRUTH_PROJECTION_FIXTURE = (
    FIXTURE_DIR / "valid_merge_stable_source_truth_projection.md"
)
INVALID_MERGE_STABLE_SOURCE_TRUTH_PROJECTION_FIXTURE = (
    FIXTURE_DIR / "invalid_merge_stable_source_truth_projection.md"
)
VALID_CROSS_FAM_DEPENDENCY_CANDIDATE_FIXTURE = (
    FIXTURE_DIR / "valid_cross_fam_dependency_candidate.md"
)
INVALID_CROSS_FAM_DEPENDENCY_UNCLASSIFIED_FIXTURE = (
    FIXTURE_DIR / "invalid_cross_fam_dependency_unclassified.md"
)
VALID_FAMILY_FEATURE_VISION_FIXTURE = (
    FIXTURE_DIR / "valid_family_feature_vision.md"
)
INVALID_FAMILY_FEATURE_VISION_SLICE_SCOPED_FIXTURE = (
    FIXTURE_DIR / "invalid_family_feature_vision_slice_scoped.md"
)
INVALID_FAMILY_FEATURE_VISION_LIVE_STATE_FIXTURE = (
    FIXTURE_DIR / "invalid_family_feature_vision_live_state_deferred.md"
)
VALID_BR2_DEFERRED_CARRYFORWARD_MATRIX_FIXTURE = (
    FIXTURE_DIR / "valid_br2_deferred_carryforward_matrix.md"
)
INVALID_BR2_DEFERRED_CARRYFORWARD_MATRIX_FIXTURE = (
    FIXTURE_DIR / "invalid_br2_deferred_carryforward_missing_applicability.md"
)
VALID_VISUAL_ACCEPTANCE_ENFORCEMENT_FIXTURE = (
    FIXTURE_DIR / "valid_visual_acceptance_enforcement_chain.md"
)
INVALID_VISUAL_ACCEPTANCE_MISSING_TARGET_FIXTURE = (
    FIXTURE_DIR / "invalid_visual_acceptance_missing_target.md"
)
INVALID_VISUAL_ACCEPTANCE_SCREENSHOT_GREEN_FIXTURE = (
    FIXTURE_DIR / "invalid_visual_acceptance_screenshot_green.md"
)
INVALID_VISUAL_ACCEPTANCE_UIREF_NO_COMPARISON_FIXTURE = (
    FIXTURE_DIR / "invalid_visual_acceptance_uiref_no_comparison.md"
)
INVALID_VISUAL_ACCEPTANCE_TEMPLATE_CLAIM_FIXTURE = (
    FIXTURE_DIR / "invalid_visual_acceptance_template_claim.md"
)
INVALID_VISUAL_ACCEPTANCE_PACKET_REVIEWABILITY_ACCEPTANCE_FIXTURE = (
    FIXTURE_DIR / "invalid_visual_acceptance_packet_reviewability_acceptance.md"
)
INVALID_VISUAL_ACCEPTANCE_ROLE_AMBIGUOUS_FIXTURE = (
    FIXTURE_DIR / "invalid_visual_acceptance_role_ambiguous.md"
)
INVALID_VISUAL_ACCEPTANCE_REFERENCE_SET_AS_AUTHORITY_FIXTURE = (
    FIXTURE_DIR / "invalid_visual_acceptance_reference_set_as_authority.md"
)
VALID_REBASELINE_ADOPTION_REVIEW_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_review.md"
)
VALID_REBASELINE_ADOPTION_RESOLVED_NORMAL_PHASE_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_resolved_normal_phase.md"
)
VALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_REVIEWED_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_issue_candidate_reviewed.md"
)
VALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_REVIEWED_CLOSED_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_issue_candidate_reviewed_closed.md"
)
VALID_REBASELINE_ADOPTION_ACTIVE_NEGATED_DISCLAIMERS_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_active_negated_disclaimers.md"
)
VALID_REBASELINE_ADOPTION_NO_ISSUE_CANDIDATE_WORDING_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_no_issue_candidate_wording.md"
)
VALID_REBASELINE_ADOPTION_NO_ISSUE_CANDIDATE_GAP_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_no_issue_candidate_gap.md"
)
VALID_REBASELINE_ADOPTION_NO_USER_REVIEW_REQUIRED_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_no_user_review_required.md"
)
VALID_REBASELINE_ADOPTION_POST_PHRASE_NO_USER_DECISION_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_post_phrase_no_user_decision.md"
)
VALID_REBASELINE_ADOPTION_SHORT_MARKERS_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_short_markers.md"
)
VALID_REBASELINE_ADOPTION_NEGATED_READY_FOR_PHASE_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_negated_ready_for_phase.md"
)
VALID_REBASELINE_ADOPTION_DIRECT_NEGATED_GREEN_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_direct_negated_green.md"
)
VALID_REBASELINE_ADOPTION_RESOLVED_NEGATED_BLOCKER_FIXTURE = (
    FIXTURE_DIR / "valid_rebaseline_adoption_resolved_negated_blocker.md"
)
INVALID_REBASELINE_ADOPTION_MISSING_CODE_TRACE_MARKER_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_missing_code_trace_marker.md"
)
INVALID_REBASELINE_ADOPTION_MARKER_ONLY_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_marker_only.md"
)
INVALID_REBASELINE_ADOPTION_UNANCHORED_STAGE_RESOLVED_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_unanchored_stage_resolved.md"
)
INVALID_REBASELINE_ADOPTION_NEGATED_RESOLVED_STAGE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_negated_resolved_stage.md"
)
INVALID_REBASELINE_ADOPTION_UNANCHORED_STAGE_NO_IMPACT_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_unanchored_stage_no_impact.md"
)
INVALID_REBASELINE_ADOPTION_MISSING_CODE_TRACE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_missing_code_trace.md"
)
INVALID_REBASELINE_ADOPTION_MISSING_PRODUCT_EXPERIENCE_COMPARISON_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_missing_product_experience_comparison.md"
)
INVALID_REBASELINE_ADOPTION_EMPTY_CODE_TRACE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_empty_code_trace.md"
)
INVALID_REBASELINE_ADOPTION_NOOP_ACTIVE_ROWS_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_noop_active_rows.md"
)
INVALID_REBASELINE_ADOPTION_MISSING_PROOF_SURFACE_NOOP_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_missing_proof_surface_noop_rows.md"
)
INVALID_REBASELINE_ADOPTION_PARTIAL_NOOP_ACTIVE_ROWS_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_partial_noop_active_rows.md"
)
INVALID_REBASELINE_ADOPTION_EMPTY_ACCEPTED_REFERENCE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_empty_accepted_reference.md"
)
INVALID_REBASELINE_ADOPTION_MALFORMED_TABLE_ROWS_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_malformed_table_rows.md"
)
INVALID_REBASELINE_ADOPTION_TABLE_PREFACE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_table_preface.md"
)
INVALID_REBASELINE_ADOPTION_HEADER_ONLY_RAR_DECISION_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_header_only_rar_decision.md"
)
INVALID_REBASELINE_ADOPTION_MISSING_TABLE_SEPARATOR_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_missing_table_separator.md"
)
INVALID_REBASELINE_ADOPTION_OVERWIDE_TABLE_ROWS_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_overwide_table_rows.md"
)
INVALID_REBASELINE_ADOPTION_SPARSE_TABLE_ROWS_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_sparse_table_rows.md"
)
INVALID_REBASELINE_ADOPTION_UNRESOLVED_GREEN_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_unresolved_nonconformance_green.md"
)
INVALID_REBASELINE_ADOPTION_UNRESOLVED_HYPHENATED_NONCONFORMANCE_FIXTURE = (
    FIXTURE_DIR
    / "invalid_rebaseline_adoption_unresolved_hyphenated_nonconformance_green.md"
)
INVALID_REBASELINE_ADOPTION_UNRESOLVED_GREEN_SEPARATE_NEGATION_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_unresolved_green_separate_negation.md"
)
INVALID_REBASELINE_ADOPTION_UNRESOLVED_GREEN_CONJUNCTION_NEGATION_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_unresolved_green_conjunction_negation.md"
)
INVALID_REBASELINE_ADOPTION_UNRESOLVED_NO_ISSUE_CANDIDATE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_unresolved_no_issue_candidate.md"
)
INVALID_REBASELINE_ADOPTION_VALIDATION_SUMMARY_GREEN_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_validation_summary_green.md"
)
INVALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_GREEN_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_issue_candidate_green.md"
)
INVALID_REBASELINE_ADOPTION_REQUIRED_USER_REVIEW_NO_PACKET_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_required_user_review_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_VALIDATION_SUMMARY_REVIEW_NO_PACKET_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_validation_summary_review_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_USER_DECISION_NO_PACKET_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_user_decision_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_PACKET_PATH_WRONG_ROOT_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_packet_path_wrong_root.md"
)
INVALID_REBASELINE_ADOPTION_PACKET_PATH_ZIP_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_packet_path_zip.md"
)
INVALID_REBASELINE_ADOPTION_PACKET_PATH_CHILD_FOLDER_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_packet_path_child_folder.md"
)
INVALID_REBASELINE_ADOPTION_PACKET_PATH_TRAVERSAL_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_packet_path_traversal.md"
)
INVALID_REBASELINE_ADOPTION_PACKET_PATH_EXPLANATORY_USER_ROOT_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_packet_path_explanatory_user_root.md"
)
INVALID_REBASELINE_ADOPTION_PACKET_PATH_SUFFIX_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_packet_path_suffix.md"
)
INVALID_REBASELINE_ADOPTION_MISSING_NEXT_LEGAL_PHASE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_missing_next_legal_phase.md"
)
INVALID_REBASELINE_ADOPTION_REPO_LIVE_STATE_TRACKING_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_repo_live_state_tracking.md"
)
INVALID_REBASELINE_ADOPTION_MISSING_ISSUE_CANDIDATE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_missing_issue_candidate.md"
)
INVALID_REBASELINE_ADOPTION_PREFIXED_NO_CANDIDATE_PROSE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_prefixed_no_candidate_prose.md"
)
INVALID_REBASELINE_ADOPTION_HYPHENATED_NO_CANDIDATE_PROSE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_hyphenated_no_candidate_prose.md"
)
INVALID_REBASELINE_ADOPTION_PLACEHOLDER_ISSUE_CANDIDATE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_placeholder_issue_candidate.md"
)
INVALID_REBASELINE_ADOPTION_PARTIAL_ISSUE_CANDIDATE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_partial_issue_candidate.md"
)
INVALID_REBASELINE_ADOPTION_HISTORICAL_NONE_PROSE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_historical_none_prose.md"
)
INVALID_REBASELINE_ADOPTION_STANDALONE_ISSUE_ID_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_standalone_issue_id.md"
)
INVALID_REBASELINE_ADOPTION_CURRENT_ISSUE_CANDIDATE_UNTABLED_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_current_issue_candidate_untabled.md"
)
INVALID_REBASELINE_ADOPTION_CURRENT_MARKER_ISSUE_CANDIDATE_UNTABLED_FIXTURE = (
    FIXTURE_DIR
    / "invalid_rebaseline_adoption_current_marker_issue_candidate_untabled.md"
)
INVALID_REBASELINE_ADOPTION_CURRENT_ISSUE_CANDIDATE_EMBEDDED_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_current_issue_candidate_embedded_status.md"
)
INVALID_REBASELINE_ADOPTION_CURRENT_ISSUE_CANDIDATE_HYPHENATED_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_current_issue_candidate_hyphenated_status.md"
)
INVALID_REBASELINE_ADOPTION_CURRENT_ISSUE_CANDIDATE_POSITIVE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_current_issue_candidate_positive_status.md"
)
INVALID_REBASELINE_ADOPTION_NOT_YET_USER_REVIEWED_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_not_yet_user_reviewed_issue_candidate.md"
)
INVALID_REBASELINE_ADOPTION_LINKED_CLOSED_CLAIM_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_linked_closed_claim.md"
)
INVALID_REBASELINE_ADOPTION_ACCEPTED_REFERENCE_ISSUE_CANDIDATE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_accepted_reference_issue_candidate.md"
)
INVALID_REBASELINE_ADOPTION_PENDING_REVIEW_NO_PACKET_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_pending_review_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_ACTIVE_REVIEW_NO_PACKET_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_active_review_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_BARE_RAR3_NO_PACKET_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_bare_rar3_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_UNRESOLVED_ROW_NO_PACKET_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_unresolved_row_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_ACCEPTED_REFERENCE_GAP_NO_PACKET_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_accepted_reference_gap_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_CONTRADICTORY_NO_DECISION_NO_PACKET_FIXTURE = (
    FIXTURE_DIR
    / "invalid_rebaseline_adoption_contradictory_no_decision_no_packet.md"
)
INVALID_REBASELINE_ADOPTION_ZIP_OUTSIDE_USER_ROOT_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_zip_outside_user_root.md"
)
INVALID_REBASELINE_ADOPTION_ZIP_CHILD_FOLDER_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_zip_child_folder.md"
)
INVALID_REBASELINE_ADOPTION_ZIP_SPACED_OFFROOT_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_zip_spaced_offroot.md"
)
INVALID_REBASELINE_ADOPTION_ZIP_EXPLANATORY_USER_ROOT_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_zip_explanatory_user_root.md"
)
INVALID_REBASELINE_ADOPTION_ZIP_SUFFIX_PATH_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_zip_suffix_path.md"
)
INVALID_REBASELINE_ADOPTION_ZIP_TRAVERSAL_PATH_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_zip_traversal_path.md"
)
INVALID_REBASELINE_ADOPTION_ZIP_ROOT_TRAVERSAL_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_zip_root_traversal.md"
)
INVALID_REBASELINE_ADOPTION_NORMAL_PHASE_WHILE_ACTIVE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_normal_phase_while_active.md"
)
INVALID_REBASELINE_ADOPTION_VALIDATION_SUMMARY_PHASE_ADVANCE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_validation_summary_phase_advance.md"
)
INVALID_REBASELINE_ADOPTION_ACTIVE_STAGE_NORMAL_PHASE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_active_stage_normal_phase.md"
)
INVALID_REBASELINE_ADOPTION_CONCRETE_PHASE_WHILE_ACTIVE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_concrete_phase_while_active.md"
)
INVALID_REBASELINE_ADOPTION_MIXED_DISCLAIMER_PHASE_ADVANCE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_mixed_disclaimer_phase_advance.md"
)
INVALID_REBASELINE_ADOPTION_COMMA_MIXED_DISCLAIMER_PHASE_ADVANCE_FIXTURE = (
    FIXTURE_DIR
    / "invalid_rebaseline_adoption_comma_mixed_disclaimer_phase_advance.md"
)
INVALID_REBASELINE_ADOPTION_MOVE_INTO_PHASE_ADVANCE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_move_into_phase_advance.md"
)
INVALID_REBASELINE_ADOPTION_GO_TO_PHASE_ADVANCE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_go_to_phase_advance.md"
)
INVALID_REBASELINE_ADOPTION_BARE_PHASE_NEXT_STEP_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_bare_phase_next_step.md"
)
INVALID_REBASELINE_ADOPTION_NOT_BLOCKED_PHASE_ADVANCE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_not_blocked_phase_advance.md"
)
INVALID_REBASELINE_ADOPTION_GENERIC_PHASE_CLAIM_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_generic_phase_claim.md"
)
INVALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_DISPOSITION_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_issue_candidate_disposition.md"
)
INVALID_REBASELINE_ADOPTION_NEGATED_ISSUE_DISPOSITION_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_negated_issue_disposition.md"
)
INVALID_REBASELINE_ADOPTION_REQUIRED_REVIEW_NOT_COMPLETE_FIXTURE = (
    FIXTURE_DIR / "invalid_rebaseline_adoption_required_review_not_complete.md"
)
VALID_RAR_ISSUE_DURABILITY_CARRY_FORWARD_FIXTURE = (
    FIXTURE_DIR / "valid_rar_issue_candidate_durability_carry_forward.md"
)
VALID_RAR_ISSUE_DURABILITY_USER_DISPOSITIONS_FIXTURE = (
    FIXTURE_DIR / "valid_rar_issue_candidate_durability_user_dispositions.md"
)
VALID_RAR_ISSUE_DURABILITY_GITHUB_PENDING_FIXTURE = (
    FIXTURE_DIR / "valid_rar_issue_candidate_durability_github_pending.md"
)
INVALID_RAR_ISSUE_DURABILITY_PACKETED_ONLY_FIXTURE = (
    FIXTURE_DIR / "invalid_rar_issue_candidate_packeted_only.md"
)
INVALID_RAR_ISSUE_DURABILITY_DEFERRED_MISSING_OWNER_FIXTURE = (
    FIXTURE_DIR / "invalid_rar_issue_candidate_deferred_missing_owner.md"
)
INVALID_RAR_ISSUE_DURABILITY_STALE_GITHUB_CLOSED_FIXTURE = (
    FIXTURE_DIR / "invalid_rar_issue_candidate_stale_github_closed.md"
)
INVALID_RAR_ISSUE_DURABILITY_DUPLICATE_LINEAGE_FIXTURE = (
    FIXTURE_DIR / "invalid_rar_issue_candidate_duplicate_lineage.md"
)
INVALID_RAR_ISSUE_DURABILITY_REPAIRED_UNVERIFIED_FIXTURE = (
    FIXTURE_DIR / "invalid_rar_issue_candidate_repaired_unverified.md"
)
EXPECTED_SHALLOW_FAILURE_SNIPPETS = (
    "placeholder/self-assessed wording",
    "is too shallow",
    "Scale / Data Volume Model must name concrete scale pressure",
    "Planning Adequacy Review must explain why the plan is not shallow",
    "Whole-System Interaction Map must describe multiple interacting pieces",
    "Runtime Branch Engineering Contract value for 'Planned Runtime Delta:'",
    "Workstream Seam Map must map multiple seams",
)
EXPECTED_NEGATIVE_APPROVAL_FAILURE_SNIPPET = (
    "requires Runtime Implementation Approval to be approved, granted, or waived"
)
EXPECTED_MISSING_PLAN_PATH_FAILURE_SNIPPET = (
    "Branch Runtime Engineering Plan Path: points to missing file"
)
EXPECTED_BRANCH_RUNTIME_PLAN_FAILURE_SNIPPETS = (
    "Branch Runtime Engineering Plan value for 'Current Runtime Baseline:'",
    "Branch Runtime Engineering Plan marker 'Planned Runtime Delta:'",
    "Branch Runtime Engineering Plan value for 'Per-Seam Implementation Checklist:'",
)
EXPECTED_BRANCH_RUNTIME_PLAN_MISSING_REVIEW_GATE_FAILURE_SNIPPET = (
    "Workstream Entry planning is missing '## USER Branch Plan Review Gate'"
)
EXPECTED_RUNTIME_DIRECT_PROOF_FAILURE_SNIPPET = (
    "must not classify diagnostic/direct runtime evidence as formal USER launcher proof"
)
EXPECTED_RUNTIME_EXACT_LAUNCHER_FAILURE_SNIPPET = (
    "must name the exact normal USER desktop runtime launcher path"
)
EXPECTED_RUNTIME_PHOTO_VIDEO_FAILURE_SNIPPET = (
    "must name photo/video, ordered frame-sequence, or focused screenshot proof"
)
EXPECTED_RUNTIME_PACKET_EVIDENCE_FAILURE_SNIPPET = (
    "must name the USER review packet, USER review hub, or UTS evidence destination"
)
EXPECTED_PROPOSED_VISION_FAILURE_SNIPPET = (
    "Branch Vision Snapshot Status cannot stay Proposed"
)
EXPECTED_BLOCKING_VISION_FAILURE_SNIPPET = (
    "Open Vision Questions must be None, queued non-blocking, or Deferred With Waiver"
)
EXPECTED_UFD_NO_OWNER_FAILURE_SNIPPET = (
    "No Durable Owner Needed requires No-Action Reason"
)
EXPECTED_UFD_BAD_ID_FAILURE_SNIPPET = "Feedback ID must use the UFD-* namespace"
EXPECTED_UFD_DUPLICATE_SUMMARY_FAILURE_SNIPPET = "duplicate UFD Feedback Summary"
EXPECTED_REBASELINE_UNKNOWN_RISK_FAILURE_SNIPPET = (
    "Semantic Merge Risk Unknown is blocked for high-risk overlap surfaces"
)
EXPECTED_REBASELINE_FALLBACK_ONLY_FAILURE_SNIPPET = (
    "Fallback Evidence cannot be used as a compatibility bypass"
)
EXPECTED_REBASELINE_FIXTURE_HIGH_IMPACT_FAILURE_SNIPPET = (
    "Regression / Gating Impact Medium, High, or Unknown blocks fixture/test overlap"
)
EXPECTED_ELEMENT_MATRIX_HARDENING_FAILURE_SNIPPET = "Hardening Proof Plan"
EXPECTED_ELEMENT_MATRIX_LIVE_VALIDATION_FAILURE_SNIPPET = (
    "Live Validation Proof / Waiver Plan"
)
EXPECTED_ELEMENT_MATRIX_DUPLICATE_ID_FAILURE_SNIPPET = "duplicates an Element ID"
EXPECTED_WORKSTREAM_ENTRY_FIRST_SEAM_FAILURE_SNIPPET = (
    "Workstream Entry Whole-Package Summary must include"
)
EXPECTED_USER_BRANCH_PLAN_MISSING_OUTCOME_FAILURE_SNIPPET = (
    "Planned User-Facing Outcome:"
)
EXPECTED_USER_BRANCH_PLAN_MISSING_PACKET_FINDING_FAILURE_SNIPPET = (
    "USER Review Packet Finding:"
)
EXPECTED_USER_BRANCH_PLAN_MISSING_HARDENING_FAILURE_SNIPPET = "Hardening Plan:"
EXPECTED_USER_BRANCH_PLAN_MISSING_LIVE_VALIDATION_FAILURE_SNIPPET = (
    "Live Validation / UTS Plan:"
)
EXPECTED_USER_BRANCH_PLAN_FIRST_SEAM_FAILURE_SNIPPET = (
    "cannot be satisfied by first-seam-only implementation planning"
)
EXPECTED_USER_BRANCH_PLAN_MISSING_RESPONSE_DIGEST_FAILURE_SNIPPET = (
    "USER Review Response:"
)
EXPECTED_BRANCH_PLANNING_GATE_BYPASS_FAILURE_SNIPPET = (
    "Packet Validation Treated As USER Acceptance"
)
EXPECTED_BP1_CONTEXT_FAILURE_SNIPPET = "Project Vision Context"
EXPECTED_RAR_MARKER_ONLY_FAILURE_SNIPPET = "Rebaseline Adoption Review Missing"
EXPECTED_RAR_STAGE_FAILURE_SNIPPET = (
    "Rebaseline Adoption Review Missing: RAR Stage must name RAR0-RAR4"
)
EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET = "Code-To-Visual Trace Missing"
EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET = (
    "Product Experience Contract Nonconformance Unresolved"
)
EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET = "Owned Surface Issue Candidate Missing"
EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET = "Normal Phase Progression Blocked By RAR"
EXPECTED_RAR_ISSUE_DISPOSITION_FAILURE_SNIPPET = "Issue Candidate Disposition Missing"
EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET = "RAR USER Packet Missing"
EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET = "RAR Issue Candidate Durability Missing"
EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET = "Visual Acceptance Target Missing"
EXPECTED_IMPLEMENTATION_MATCH_PROOF_FAILURE_SNIPPET = (
    "Implementation Match Proof Plan Missing"
)
EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET = "Visual Family Relation Proof Missing"
EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET = "Implementation Authority Classification Missing"
EXPECTED_FUNCTIONALITY_ROLE_FAILURE_SNIPPET = "Functionality Role Contract Missing"
EXPECTED_PRE_LIVE_VISUAL_PURPOSE_FAILURE_SNIPPET = "Pre-Live Visual Purpose Conformance Missing"
EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET = (
    "Packet Reviewability Treated As Product Acceptance"
)
EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET = (
    "Screenshot Path Treated As Visual Acceptance"
)
EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET = (
    "Helper Green Treated As Visual Acceptance"
)
EXPECTED_CSS_VISUAL_FAMILY_FAILURE_SNIPPET = (
    "CSS Similarity Treated As Visual Family Proof"
)
EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET = "Template Claim Unsupported"
EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET = "Shared Primitive Claim Unsupported"
EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET = (
    "Accepted Reference Not Compared"
)
EXPECTED_IMPLEMENTATION_FIRST_TARGET_FAILURE_SNIPPET = (
    "Implementation-First Visual Target Backfill"
)
EXPECTED_BP1_SHALLOW_RECOMMENDATION_FAILURE_SNIPPET = (
    "Codex Recommendations are too shallow"
)
EXPECTED_BP1_TEMPLATE_SHELL_FAILURE_SNIPPET = "template-shell BP1 wording"
EXPECTED_BP1_COPIED_SURFACE_FAILURE_SNIPPET = "copied-file list cannot be the BP1 Surface Map"
EXPECTED_BP1_GENERIC_QUESTIONS_FAILURE_SNIPPET = (
    "USER Design Questions must ask branch-specific decision-driving questions"
)
EXPECTED_BP1_SLC_CENTERED_FAILURE_SNIPPET = "BP1 cannot be SLC-centered"
EXPECTED_BP1_TECHNICAL_METADATA_FAILURE_SNIPPET = (
    "BP1 must not center active branch technical metadata"
)
EXPECTED_RUNTIME_FOCUS_ISSUE_ANCHORED_FAILURE_SNIPPET = (
    "Runtime focus selection cannot use issue evidence as BR2/BP1 branch identity"
)
EXPECTED_RUNTIME_FOCUS_FOUNDATION_LABEL_FAILURE_SNIPPET = (
    "Runtime focus selection must name a concrete feature outcome"
)
EXPECTED_BP2_ACCEPTED_BP1_TRACE_FAILURE_SNIPPET = "Accepted BP1 trace"
EXPECTED_BP2_PRODUCT_DESIGN_WORDING_FAILURE_SNIPPET = (
    "BP2 must be engineering-plan-first"
)
EXPECTED_BP3_PENDING_FAILURE_SNIPPET = (
    "BP3 cannot approve implementation while BP1 or BP2 is pending"
)
EXPECTED_USER_PACKET_ACTIVE_METADATA_FAILURE_SNIPPET = (
    "USER-facing packet file contains active technical metadata"
)
EXPECTED_USER_PACKET_ZIP_HASH_FAILURE_SNIPPET = (
    "USER-facing packet file contains ZIP/hash technical metadata"
)
EXPECTED_USER_PACKET_DESKTOP_ACTIVE_UPLOAD_FAILURE_SNIPPET = (
    "USER-facing packet file routes active upload/review to Desktop or OneDrive"
)
EXPECTED_IMPLEMENTATION_ROUTE_FAILURE_SNIPPET = (
    "Implementation-bearing route required"
)
EXPECTED_BR2_NO_ROUTE_CONTINUE_FAILURE_SNIPPET = (
    "BR2 blocker packet with no concrete available route"
)
EXPECTED_BR2_MARKER_ONLY_DEFERRAL_FAILURE_SNIPPET = (
    "BR2 blocker packet must offer deferral to a concrete feature route"
)
EXPECTED_FAKE_FEATURE_LABEL_FAILURE_SNIPPET = (
    "Feature label cannot substitute for concrete implementation behavior"
)
EXPECTED_PROOF_BOUNDARY_LABEL_FAILURE_SNIPPET = (
    "Proof/setup/boundary labels cannot substitute for real feature implementation"
)
EXPECTED_TBD_IMPLEMENTATION_OUTPUT_FAILURE_SNIPPET = (
    "Implementation-bearing route cannot defer implementation output to BP2 or a later decision"
)
EXPECTED_BLANK_SELECTED_ROUTE_FAILURE_SNIPPET = (
    "Implementation-bearing route marker requires a value: Selected Implementation Route:"
)
EXPECTED_NEGATED_ROUTE_BEHAVIOR_FAILURE_SNIPPET = (
    "Implementation-bearing route cannot negate implementation behavior"
)
EXPECTED_BR2_PROOF_ONLY_ROUTE_FAILURE_SNIPPET = (
    "BR2 blocker packet concrete routes cannot be proof/readiness labels only"
)
EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET = "SLC / Slice / Seam terminology ambiguity"
EXPECTED_MERGE_STABLE_PROJECTION_FAILURE_SNIPPET = "PR creation pending"
EXPECTED_CROSS_FAM_UNCLASSIFIED_FAILURE_SNIPPET = (
    "Cross-FAM Dependency Scope Unclassified"
)


def _collect_failures():
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    return failures, require


def _validate_fixture(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures, require = _collect_failures()
    governance._validate_product_definition_plan(
        require,
        path.as_posix(),
        text,
        branch_class="implementation",
        current_phase="Live Validation",
        blockers=[],
        next_legal_phase="Live Validation",
    )
    governance._validate_runtime_engineering_contract(
        require,
        path.as_posix(),
        text,
        branch_class="implementation",
        current_phase="Live Validation",
    )
    return failures


def _validate_runtime_contract_text(text: str, *, phase: str) -> list[str]:
    failures, require = _collect_failures()
    governance._validate_runtime_engineering_contract(
        require,
        "<runtime-contract-fixture>",
        text,
        branch_class="implementation",
        current_phase=phase,
    )
    return failures


def _validate_branch_runtime_plan_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    governance._validate_branch_runtime_engineering_plan(
        require,
        "<branch-runtime-engineering-plan-fixture>",
        text,
    )
    return failures


def _without_user_branch_plan_review_gate(text: str) -> str:
    marker = "\n## USER Branch Plan Review Gate\n"
    start = text.find(marker)
    if start == -1:
        return text
    next_heading = text.find("\n## ", start + len(marker))
    if next_heading == -1:
        return text[:start].rstrip() + "\n"
    return text[:start].rstrip() + "\n" + text[next_heading:].lstrip()


def _validate_branch_vision_contract_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    governance._validate_branch_vision_contract_snapshot(
        require,
        "<branch-vision-contract-fixture>",
        text,
    )
    return failures


def _validate_user_feedback_disposition_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    governance._validate_user_feedback_disposition(
        require,
        "<user-feedback-disposition-fixture>",
        text,
    )
    return failures


def _validate_branch_change_intent_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    governance._validate_branch_change_intent_ledger(
        require,
        "<branch-change-intent-fixture>",
        text,
    )
    return failures


def _validate_element_to_phase_matrix_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    governance._validate_element_to_phase_proof_matrix(
        require,
        "<element-to-phase-proof-matrix-fixture>",
        text,
        require_matrix=True,
    )
    return failures


def _validate_workstream_entry_whole_package_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    analysis = governance._extract_marker_value(
        text, "Workstream Entry Whole-Package Analysis:"
    )
    summary = governance._extract_marker_value(
        text, "Workstream Entry Whole-Package Summary:"
    )
    normalized_analysis = governance._normalized_planning_value(analysis)
    normalized_summary = governance._normalized_planning_value(summary)

    require(
        bool(analysis),
        "Workstream Entry Whole-Package Analysis marker is missing",
    )
    require(
        bool(summary),
        "Workstream Entry Whole-Package Summary marker is missing",
    )
    require(
        not normalized_analysis.startswith("not required")
        and "first-seam-only" not in normalized_analysis
        and "first seam only" not in normalized_analysis,
        "Workstream Entry Whole-Package Analysis cannot be waived by first-seam-only wording",
    )
    required_summary_phrases = (
        "all admitted slices/seams",
        "completion strategy",
        "entry-seam recommendation",
        "seam dependency map",
        "future-gated",
        "preservation surfaces",
        "validation plan",
        "hardening h1",
        "live validation lv1",
        "uts handoff",
        "exact implementation approval text",
    )
    for phrase in required_summary_phrases:
        require(
            phrase in normalized_summary,
            f"Workstream Entry Whole-Package Summary must include {phrase}",
        )
    return failures


def _validate_runtime_focus_selection_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    normalized = governance._normalized_planning_value(text)
    runtime_focus_packet = (
        "runtime focus selection" in normalized
        or "runtime focus options" in normalized
        or "neutral family runtime survey" in normalized
        or "runtime feature focus" in normalized
        or "feature carrier selection" in normalized
        or "feature implementation options" in normalized
        or "actual feature implementation" in normalized
    )
    if not runtime_focus_packet:
        return failures
    issue_identity_phrases = (
        "issue #258 role: br2/bp1 branch identity",
        "issue #258 as the selection source before surveying",
        "selected because issue #258",
        "github issue #258 as the selection source",
    )
    issue_identity_present = any(phrase in normalized for phrase in issue_identity_phrases)
    issue_deferred_present = (
        "future bp2/bp3 proof input" in normalized
        or "issue evidence is not deferred to later proof planning" in normalized
    )
    neutral_survey_present = (
        "family vision" in normalized
        and "backlog" in normalized
        and "roadmap" in normalized
        and "workstream history" in normalized
        and "remaining runtime layers" in normalized
    )
    foundation_label_present = any(
        phrase in normalized
        for phrase in (
            "active overlay recording execution foundation",
            "persistence foundation",
            "infrastructure foundation",
            "execution foundation",
            "dashboard overlay profile persistence and restart hydration runtime foundation",
        )
    ) and "recommended runtime focus:" in normalized
    concrete_outcome_markers = (
        "feature outcome:",
        "user-visible feature outcome:",
        "what user gets:",
        "what the user gets:",
        "actual feature outcome:",
        "concrete feature outcome:",
    )
    concrete_outcome_present = any(phrase in normalized for phrase in concrete_outcome_markers)
    missing_concrete_outcome_present = any(
        phrase in normalized
        for phrase in (
            "feature outcome: missing",
            "feature outcome: `missing",
            "user-visible feature outcome: missing",
            "user-visible feature outcome: `missing",
            "actual feature outcome: missing",
            "actual feature outcome: `missing",
            "concrete feature outcome: missing",
            "concrete feature outcome: `missing",
            "what user gets: missing",
            "what user gets: `missing",
            "what the user gets: missing",
            "what the user gets: `missing",
        )
    )
    require(
        not issue_identity_present,
        "Runtime focus selection cannot use issue evidence as BR2/BP1 branch identity",
    )
    require(
        neutral_survey_present,
        "Runtime focus selection must survey family/runtime source truth before issue evidence",
    )
    require(
        issue_deferred_present,
        "Runtime focus selection must defer issue evidence to future BP2/BP3 proof input",
    )
    require(
        not foundation_label_present
        or (concrete_outcome_present and not missing_concrete_outcome_present),
        "Runtime focus selection must name a concrete feature outcome when infrastructure, groundwork, persistence, execution, schema, hydration, or foundation labels are used",
    )
    return failures


def _validate_user_branch_plan_review_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    governance._validate_user_branch_plan_review_gate(
        require,
        "<user-branch-plan-review-fixture>",
        text,
        require_gate=True,
    )
    return failures


def _validate_bp1_branch_vision_review_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    normalized = governance._normalized_planning_value(text)
    required_markers = (
        "USER Branch Vision Review:",
        "Review Status:",
        "Contract Status:",
        "Packet Reviewability State:",
        "USER Gate State:",
        "USER Response Proof:",
        "USER Response Digested:",
        "Project Vision Context:",
        "Family Vision Context:",
        "Feature Vision Context:",
        "Branch Goal:",
        "End-State Vision:",
        "What Will I Actually See, And Where Will I See It?:",
        "How It Will Function:",
        "User Experience Flow:",
        "Surface Map:",
        "Product Options / Design Paths:",
        "Codex Recommendations:",
        "Why This Fits The Nexus Vision:",
        "USER Design Questions:",
        "USER Response:",
        "Codex Digest:",
        "Accepted Branch Vision:",
        "Design Assumption Ledger:",
        "Acceptance / Revision / Rejection / Waiver Decision:",
    )
    for marker in required_markers:
        require(marker in text, f"BP1 Branch Vision Review missing {marker}")
    for marker in (
        "Project Vision Context:",
        "Family Vision Context:",
        "Feature Vision Context:",
        "Branch Goal:",
    ):
        value = governance._extract_marker_value(text, marker)
        require(bool(value), f"BP1 Branch Vision Review missing {marker}")
    recommendations = governance._extract_marker_value(text, "Codex Recommendations:")
    require(
        governance._planning_word_count(recommendations) >= 16
        and "placement" in recommendations.casefold()
        and "tradeoff" in recommendations.casefold(),
        "Codex Recommendations are too shallow for BP1 Branch Vision Review",
    )
    require(
        "user response" in recommendations.casefold(),
        "Codex Recommendations must leave USER response space for BP1 review",
    )
    substantive_markers = (
        "Project Vision Context:",
        "Family Vision Context:",
        "Feature Vision Context:",
        "Branch Goal:",
        "End-State Vision:",
        "What Will I Actually See, And Where Will I See It?:",
        "How It Will Function:",
        "User Experience Flow:",
        "Surface Map:",
        "Product Options / Design Paths:",
        "USER Design Questions:",
    )
    for marker in substantive_markers:
        value = governance._extract_marker_value(text, marker)
        require(
            governance._planning_word_count(value) >= 10,
            f"{marker} is too shallow for BP1 substantive review",
        )
    template_shell_phrases = (
        "review `docs/nexus_vision.md`",
        "review the relevant `docs/family_visions/` owner",
        "must explain how this branch supports",
        "family vision context: this bp1 review asks whether",
        "confirm that this branch goal is the right product direction",
        "describe the intended user-visible or source-truth end state",
        "review the copied branch-specific files and note any changes",
        "does this branch vision match what the user wants this branch to become",
        "create an accepted user-facing branch vision",
        "when bp1 closes",
        "bp1 captures",
        "option a accepts the vision, option b revises it, option c waives",
        "use this packet to decide",
        "what exact outcome should user expect to see",
        "user will see a local user hub packet",
        "the accepted bp1 vision will become the target for bp2",
        "user reads the fam-007 packet",
        "name the concrete branch outcome",
        "user should be able to point to the accepted outcome",
        "user should see an applied explanation",
        "the branch vision functions as the product and governance target",
        "strongest implied",
        "narrower surface path",
        "broader owner/family impact path",
        "choose the most concrete",
        "which concrete outcome should user expect",
    )
    for phrase in template_shell_phrases:
        require(
            phrase not in normalized,
            "template-shell BP1 wording must not pass reviewability checks",
        )
    surface_map = governance._extract_marker_value(text, "Surface Map:")
    normalized_surface_map = governance._normalized_planning_value(surface_map)
    require(
        " copied as " not in normalized_surface_map
        or any(
            term in normalized_surface_map
            for term in (
                "decision surface",
                "experience surface",
                "review surface",
                "user will see",
                "owner",
            )
        ),
        "copied-file list cannot be the BP1 Surface Map",
    )
    require(
        "review surface" in normalized_surface_map
        and "decision surface" in normalized_surface_map,
        "Surface Map must distinguish review and decision surfaces",
    )
    options = governance._extract_marker_value(text, "Product Options / Design Paths:")
    require(
        "option" in options.casefold()
        and (
            "tradeoff" in options.casefold()
            or "risk" in options.casefold()
            or "defer" in options.casefold()
        ),
        "Product Options / Design Paths must include real options and tradeoffs",
    )
    user_questions = governance._extract_marker_value(text, "USER Design Questions:")
    require(
        user_questions.count("?") >= 2
        and "does this branch vision match what the user wants" not in user_questions.casefold(),
        "USER Design Questions must ask branch-specific decision-driving questions",
    )
    require(
        "bp1 center: slc" not in normalized and "slc-centered: yes" not in normalized,
        "BP1 cannot be SLC-centered; SLCs are engineering route details after vision acceptance",
    )
    for metadata_marker in (
        "Source HEAD:",
        "origin/main:",
        "Ahead/Behind:",
        "Current PR State:",
        "Worktree Cleanliness:",
    ):
        require(
            metadata_marker not in text,
            "BP1 must not center active branch technical metadata",
        )
    return failures


def _validate_bp2_branch_plan_review_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    required_markers = (
        "USER Branch Plan Review:",
        "Packet Reviewability State:",
        "USER Gate State:",
        "USER Response Proof:",
        "USER Response Digested:",
        "Accepted Branch Vision Summary:",
        "Implementation Package Summary:",
        "Branch Scope Size Test:",
        "SLC / Seam Plan:",
        "Affected Surfaces:",
        "Likely Files:",
        "Validators / Helpers:",
        "Proof Requirements:",
        "Element-to-Phase Proof Matrix:",
        "H1 Expectations:",
        "LV / UTS Expectations:",
        "Rollback / Safety Plan:",
        "Future-Gated Boundaries:",
        "Plan Acceptance Checklist:",
        "Exact BP3 Approval Text:",
    )
    for marker in required_markers:
        require(marker in text, f"BP2 Branch Plan Review missing {marker}")
    accepted_trace = governance._extract_marker_value(text, "Accepted Branch Vision Summary:")
    require(
        "bp1 accepted" in accepted_trace.casefold()
        or "bp1 waived" in accepted_trace.casefold(),
        "Accepted BP1 trace is required before BP2 can be green",
    )
    stale_product_design_phrases = (
        "required user-facing product/design planning gate",
        "Do I actually like what Codex is about to build",
        "USER Branch Plan Contract: a required user-facing product/design",
    )
    for phrase in stale_product_design_phrases:
        require(
            phrase.casefold() not in text.casefold(),
            "BP2 must be engineering-plan-first and must not reuse BP1/product-design contract wording",
        )
    substantive_markers = (
        "Implementation Package Summary:",
        "Branch Scope Size Test:",
        "SLC / Seam Plan:",
        "Affected Surfaces:",
        "Likely Files:",
        "Validators / Helpers:",
        "Proof Requirements:",
        "Element-to-Phase Proof Matrix:",
        "H1 Expectations:",
        "LV / UTS Expectations:",
        "Rollback / Safety Plan:",
        "Future-Gated Boundaries:",
        "Plan Acceptance Checklist:",
        "Exact BP3 Approval Text:",
    )
    for marker in substantive_markers:
        value = governance._extract_marker_value(text, marker)
        require(
            governance._planning_word_count(value) >= 10,
            f"{marker} is too shallow for BP2 substantive engineering-plan review",
        )
    normalized = governance._normalized_planning_value(text)
    for phrase in (
        "see copied files",
        "see source files",
        "implementation options: accept revise waive reject",
        "generic implementation plan",
        "tbd",
        "placeholder",
    ):
        require(
            phrase not in normalized,
            "BP2 template-shell review artifact must not pass reviewability checks",
        )
    return failures


def _validate_bp3_orchestration_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    normalized = governance._normalized_planning_value(text)
    for marker in (
        "BP1 Contract Status:",
        "BP2 Contract Status:",
        "BP1 USER Gate State:",
        "BP2 USER Gate State:",
        "BP3 Packet Reviewability State:",
        "BP3 USER Gate State:",
        "Branch Plan Matches Accepted Branch Vision:",
        "Branch Package Size:",
        "SLC Traceability:",
        "Future-Gated Boundaries:",
        "Workstream Entry Seam:",
        "Implementation Approval:",
    ):
        require(marker in text, f"BP3 Orchestration Validation missing {marker}")
    bp1 = governance._normalized_planning_value(
        governance._extract_marker_value(text, "BP1 Contract Status:")
    )
    bp2 = governance._normalized_planning_value(
        governance._extract_marker_value(text, "BP2 Contract Status:")
    )
    bp1_gate = governance._normalized_planning_value(
        governance._extract_marker_value(text, "BP1 USER Gate State:")
    )
    bp2_gate = governance._normalized_planning_value(
        governance._extract_marker_value(text, "BP2 USER Gate State:")
    )
    bp3_gate = governance._normalized_planning_value(
        governance._extract_marker_value(text, "BP3 USER Gate State:")
    )
    implementation_approval = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Implementation Approval:")
    )
    if "approve" in implementation_approval or "approved" in implementation_approval:
        require(
            bp1.startswith(("complete", "waived by user"))
            and bp2.startswith(("complete", "waived by user")),
            "BP3 cannot approve implementation while BP1 or BP2 is pending",
        )
        require(
            bp1_gate.startswith(("user accepted", "user waived"))
            and bp2_gate.startswith(("user accepted", "user waived"))
            and bp3_gate.startswith(("user approved", "user waived")),
            "BP3 cannot approve implementation while a USER review gate is pending",
        )
    require(
        "slc traceability: complete" in normalized,
        "BP3 requires complete SLC traceability to BP1 and BP2",
    )
    substantive_markers = (
        "Branch Plan Matches Accepted Branch Vision:",
        "Branch Package Size:",
        "Future-Gated Boundaries:",
        "Workstream Entry Seam:",
        "Implementation Approval:",
    )
    for marker in substantive_markers:
        value = governance._extract_marker_value(text, marker)
        require(
            governance._planning_word_count(value) >= 8,
            f"{marker} is too shallow for BP3 substantive orchestration review",
        )
    if "approved" in implementation_approval or "approve" in implementation_approval:
        require(
            (
                "admitted same-branch workstream package" in implementation_approval
                or "bounded workstream package" in implementation_approval
            )
            and "entry checkpoint" in implementation_approval
            and "workstream green" in implementation_approval,
            "BP3 implementation approval must name bounded Workstream package execution, entry checkpoint, and Workstream Green continuation",
        )
    return failures


def _validate_branch_planning_gate_state_packet_text(text: str) -> list[str]:
    substantive_bp1_text = (
        "# Fixture USER Branch Vision Review\n\n"
        "USER Branch Vision Review: BP1\n\n"
        "## Packet Reviewability State\nReviewable\n\n"
        "## USER Gate State\nPending USER Review\n\n"
        "## USER Response Proof\nPending USER response.\n\n"
        "## USER Response Digested\nNo - pending USER response.\n\n"
        "## Project Vision Context\n"
        "This fixture keeps Nexus branch planning USER-readable before engineering work by proving packet reviewability and USER acceptance stay separate states.\n\n"
        "## Family Vision Context\n"
        "The fixture family context requires branch-specific review gates, clear owner routing, and no implementation authority before USER closes the gate.\n\n"
        "## Feature Vision Context\n"
        "This review-gate feature protects BP1, BP2, and BP3 packets from becoming false implementation approvals when only reviewability was proven.\n\n"
        "## Branch Goal\n"
        "Demonstrate that the branch planning packet can be reviewable while USER acceptance remains pending and Workstream implementation stays blocked.\n\n"
        "## End-State Vision\n"
        "USER receives a readable planning packet where reviewability, gate state, response proof, and implementation authority are each explicit and auditable.\n\n"
        "## What Will I Actually See, And Where Will I See It?\n"
        "USER sees the BP1 review file in the local USER review packet and can distinguish navigation context from the actual decision surface.\n\n"
        "## How It Will Function\n"
        "BP1 prepares the vision for review, BP2 waits for a legal USER response, and BP3 cannot request implementation while earlier gates remain open.\n\n"
        "## User Experience Flow\n"
        "USER opens START_HERE, reviews the branch vision, checks pending decisions, and responds before Codex can prepare the next planning gate.\n\n"
        "## Surface Map\n"
        "Review surface is USER_BRANCH_VISION_REVIEW.md; decision surface is the USER response; proof surface is the Codex digest; later BP2 and BP3 files trace to this gate state.\n\n"
        "## Product Options / Design Paths\n"
        "Option A keeps the packet reviewable with USER response pending until a clear receipt arrives, with the tradeoff that later stages wait. Option B revises the review packet before acceptance if the vision, decision surface, or proof path is unclear, reducing risk before BP2. Option C waives or rejects the gate with explicit USER text and keeps later stages bounded or deferred.\n\n"
        "## Codex Recommendations\n"
        "Recommendation one keeps reviewability and acceptance independent because packet hygiene can pass while USER intent remains undecided, with the tradeoff that later stages must wait for a clear receipt. USER response: pending. Recommendation two keeps implementation language blocked because false green validation is the core risk this fixture protects against. USER response: pending.\n\n"
        "## Why This Fits The Nexus Vision\n"
        "This supports Nexus by making governance decisions inspectable, USER-controlled, and resistant to Codex treating generated artifacts as permission.\n\n"
        "## USER Design Questions\n"
        "Should this review gate remain pending until USER gives explicit acceptance text? Which packet field should Codex cite as proof before preparing the next gate?\n"
    )
    packet_files = {
        "START_HERE.md": text
        + "\nPrimary USER Review File: `USER Review/USER_BRANCH_PLAN_REVIEW.md`\n",
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/{review_bundle.USER_BRANCH_VISION_REVIEW_FILE}": substantive_bp1_text,
        f"{review_bundle.USER_REVIEW_DIR_NAME}/{review_bundle.USER_BRANCH_PLAN_REVIEW_FILE}": text,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/USER_REVIEW_FOLDER_AND_FILE_DIGEST.md": text,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/GOVERNANCE_REQUIRED_FILES_SCAN.md": text,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md": text,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/BRANCH_VISION_VALIDATION_CHECKLIST.md": text,
        f"{review_bundle.SOURCE_TRUTH_CONTEXT_DIR_NAME}/Main.md": text,
    }
    result = review_bundle._validate_workstream_entry_packet_decision_path(
        packet_files,
        expected_branch="fixture-branch",
        expected_head="0" * 40,
        expected_origin_main="1" * 40,
    )
    return result.failures


def _validate_user_packet_metadata_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    active_metadata_markers = (
        "HEAD",
        "Source HEAD:",
        "origin/main:",
        "Merge Base:",
        "Ahead/Behind:",
        "Upstream:",
        "Worktree Cleanliness:",
        "Validation Status:",
        "PR State:",
        "Current Branch State:",
    )
    for marker in active_metadata_markers:
        require(
            marker not in text,
            "USER-facing packet file contains active technical metadata",
        )
    hash_markers = (
        "ZIP SHA",
        "ZIP SHA256",
        "ZIP hash",
        "packet hash",
        "upload hash",
    )
    for marker in hash_markers:
        require(
            marker.casefold() not in text.casefold(),
            "USER-facing packet file contains ZIP/hash technical metadata",
        )
    active_upload_markers = (
        "Desktop review bundle",
        "USER Desktop review bundle",
        "OneDrive active review path",
        "Upload from C:\\Users\\anden\\OneDrive\\Desktop",
        "Upload ZIP: C:\\Users\\anden\\OneDrive\\Desktop",
        "Review Location: C:\\Users\\anden\\OneDrive\\Desktop",
    )
    for marker in active_upload_markers:
        require(
            marker.casefold() not in text.casefold(),
            "USER-facing packet file routes active upload/review to Desktop or OneDrive",
        )
    return failures


def _validate_implementation_bearing_route_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    required_markers = (
        "Selected Implementation Route:",
        "Implementation Route Class:",
        "Concrete Deliverable:",
        "Implementation Output:",
        "Infrastructure / Setup Relationship:",
        "USER Action Gate:",
        "Route Disposition:",
        "Retarget / Rename Recommendation:",
    )
    for marker in required_markers:
        require(marker in text, f"Implementation-bearing route missing {marker}")

    def same_line_marker_value(marker: str) -> str:
        normalized_marker = marker.rstrip(":")
        pattern = re.compile(
            rf"^[ \t]*(?:-[ \t]*)?{re.escape(normalized_marker)}:"
            r"[ \t]*`?([^\r\n]*?)`?[ \t]*$",
            flags=re.M,
        )
        matches = pattern.findall(text)
        if not matches:
            return ""
        return matches[-1].strip().strip("`").strip()

    marker_values = {
        marker: same_line_marker_value(marker) for marker in required_markers
    }
    for marker, value in marker_values.items():
        require(
            bool(governance._normalized_planning_value(value)),
            f"Implementation-bearing route marker requires a value: {marker}",
        )

    selected_route = marker_values["Selected Implementation Route:"]
    deliverable = marker_values["Concrete Deliverable:"]
    implementation_output = marker_values["Implementation Output:"]
    setup_relationship = marker_values["Infrastructure / Setup Relationship:"]
    user_gate = marker_values["USER Action Gate:"]
    route_disposition = marker_values["Route Disposition:"]
    retarget = marker_values["Retarget / Rename Recommendation:"]
    combined_route = governance._normalized_planning_value(
        "\n".join((selected_route, deliverable, implementation_output))
    )
    setup_normalized = governance._normalized_planning_value(setup_relationship)
    disposition_normalized = governance._normalized_planning_value(route_disposition)
    retarget_normalized = governance._normalized_planning_value(retarget)
    full_normalized = governance._normalized_planning_value(text)

    concrete_terms = (
        "implementation",
        "enforcement",
        "runtime",
        "validator",
        "helper",
        "source-truth",
        "source truth",
        "consent shell",
        "trust-boundary",
        "security",
        "capability-pack",
        "memory/cache",
        "provider",
        "user-facing",
        "workflow",
    )
    concrete_behavior_terms = (
        "enforce",
        "block",
        "validate",
        "fail-closed",
        "detect",
        "route",
        "render",
        "persist",
        "execute",
        "launch",
        "open",
        "save",
        "load",
        "sync",
        "consent",
        "control",
        "runtime",
        "validator",
        "helper",
        "source-truth",
        "source truth",
        "user-facing",
    )
    actual_implementation_terms = (
        "implement",
        "implements",
        "implemented",
        "enforce",
        "enforces",
        "enforcement",
        "block",
        "blocks",
        "blocked",
        "reject",
        "rejects",
        "prevent",
        "prevents",
        "fail-closed",
        "fails closed",
        "validate",
        "validates",
        "render",
        "renders",
        "persist",
        "persists",
        "execute",
        "executes",
        "route",
        "routes",
        "disable",
        "disables",
        "update",
        "updates",
        "create",
        "creates",
    )
    implemented_target_terms = (
        "behavior",
        "control",
        "workflow",
        "surface",
        "state",
        "transition",
        "enforcement",
        "consent shell",
        "consent-shell",
        "trust-boundary",
        "boundary",
        "exclusion",
        "suppression",
        "validator",
        "helper",
        "source-truth",
        "source truth",
        "runtime",
        "user-facing",
    )
    evidence_only_route_terms = (
        "proof package",
        "proof packet",
        "validation proof",
        "setup proof",
        "packet proof",
        "readiness proof",
        "registry proof",
        "boundary proof",
        "proof-only",
        "proof as",
        "proof of",
        "review packet",
        "packet generation",
        "decision path",
        "decision-ready",
        "readiness matrix",
        "validation plan",
        "planning candidate",
        "boundary controls",
        "boundary-control labels",
    )
    tbd_route_terms = (
        "implementation output is tbd",
        "tbd",
        "to be determined",
        "figured out later",
        "will be figured out",
        "will choose",
        "choose the validator",
        "decide later",
        "selected later",
        "later during bp2",
        "after user reviews more options",
        "bp2 will choose",
        "bp2 will decide",
    )
    negated_real_behavior_terms = (
        "does not add behavior",
        "does not add implementation",
        "does not add state",
        "does not change behavior",
        "does not change state",
        "does not enforce",
        "does not implement",
        "doesn't add behavior",
        "doesn't add implementation",
        "doesn't change behavior",
        "doesn't change state",
        "doesn't enforce",
        "doesn't implement",
        "will not add behavior",
        "will not add implementation",
        "will not change behavior",
        "will not change state",
        "will not enforce",
        "will not implement",
        "no enforcement behavior",
        "no helper behavior",
        "no implemented behavior",
        "no implemented control",
        "no validator behavior",
        "no runtime behavior",
        "no source-truth behavior",
        "no source truth behavior",
        "no user-facing surface",
        "no state transition",
        "no behavior changes",
        "behavior changes are deferred",
        "changes are deferred",
        "behavior is deferred",
        "without implemented behavior",
        "without naming the control behavior",
        "without naming the actual control",
    )
    planning_only_terms = (
        "planning-only",
        "readiness-only",
        "setup-only",
        "lane setup only",
        "choose later branches",
        "identify later branches",
        "no implementation route",
        "no product/runtime/source-truth/helper deliverable",
        "implementation output: none",
    )
    fake_feature_terms = (
        "setup feature",
        "readiness feature",
        "planning feature",
        "decision feature",
        "decision matrix feature",
        "registry feature",
        "skeleton feature",
        "packet feature",
        "review feature",
        "feature implementation label",
        "feature label",
    )
    real_behavior_present = (
        any(term in combined_route for term in actual_implementation_terms)
        and any(term in combined_route for term in implemented_target_terms)
        and not any(term in combined_route for term in negated_real_behavior_terms)
    )
    negated_real_behavior_detected = any(
        term in combined_route for term in negated_real_behavior_terms
    )
    evidence_only_detected = any(
        term in combined_route for term in evidence_only_route_terms
    )
    require(
        governance._planning_word_count(deliverable) >= 8
        and governance._planning_word_count(implementation_output) >= 8
        and any(term in combined_route for term in concrete_terms)
        and real_behavior_present
        and not any(term in combined_route for term in planning_only_terms),
        (
            "Implementation-bearing route required: concrete deliverable and "
            "implementation output must be named before BP1"
        ),
    )
    require(
        not negated_real_behavior_detected,
        (
            "Implementation-bearing route cannot negate implementation behavior: "
            "name the control, behavior, surface, or state transition that "
            "Workstream will implement or enforce"
        ),
    )
    require(
        not evidence_only_detected or real_behavior_present,
        (
            "Proof/setup/boundary labels cannot substitute for real feature "
            "implementation: name the actual control, behavior, surface, or "
            "state transition Workstream will implement or enforce"
        ),
    )
    require(
        not any(term in combined_route for term in tbd_route_terms),
        (
            "Implementation-bearing route cannot defer implementation output "
            "to BP2 or a later decision: name the actual route behavior before BP1"
        ),
    )
    fake_feature_detected = any(term in combined_route for term in fake_feature_terms)
    negated_behavior_terms = (
        "no runtime",
        "no source-truth",
        "no source truth",
        "no helper",
        "no validator",
        "no enforcement",
        "no consent-shell",
        "no user-facing",
        "no boundary behavior",
        "no behavior changes",
        "without runtime",
        "without source-truth",
        "without source truth",
        "without helper",
        "without validator",
        "without enforcement",
        "without user-facing",
        "without boundary behavior",
    )
    require(
        not fake_feature_detected
        or (
            real_behavior_present
            and any(term in combined_route for term in concrete_behavior_terms)
            and not any(term in combined_route for term in negated_behavior_terms)
        ),
        (
            "Feature label cannot substitute for concrete implementation behavior: "
            "name the behavior, source-truth/helper/validator/runtime output, and proof"
        ),
    )

    if any(
        term in full_normalized
        for term in (
            "lane setup",
            "repo/root/remote",
            "private root",
            "private remote",
            "skeleton setup",
            "registry creation",
        )
    ):
        require(
            "execution-enabling" in setup_normalized
            or "selected implementation route" in setup_normalized
            or "exact user action gate" in setup_normalized,
            (
                "Infrastructure/setup work must be tied to the selected "
                "implementation route or an exact USER action gate"
            ),
        )

    require(
        "Dev lane" not in text,
        "Use Developer lane, not Dev lane, in current branch-planning text",
    )
    if "developer" in full_normalized:
        require(
            "Developer lane" in text,
            "Developer lane terminology must be explicit when developer lane scope appears",
        )

    if "hold" in disposition_normalized:
        exact_gate = governance._extract_marker_value(text, "Exact USER Action Gate:")
        blocked_scope = governance._extract_marker_value(text, "Blocked Scope:")
        require(
            governance._planning_word_count(exact_gate) >= 10,
            "BP2 HOLD requires an exact USER action gate",
        )
        require(
            governance._planning_word_count(blocked_scope) >= 8,
            "BP2 HOLD requires blocked scope",
        )
    if "retarget" in disposition_normalized or "rename" in disposition_normalized:
        require(
            ("retarget" in retarget_normalized or "rename" in retarget_normalized)
            and any(term in retarget_normalized for term in concrete_terms),
            "Route retarget/rename disposition requires a concrete recommendation",
        )

    require(
        governance._planning_word_count(user_gate) >= 6,
        "Implementation-bearing route must name pending USER action gate posture",
    )
    return failures


def _validate_cross_fam_dependency_packet_text(text: str) -> list[str]:
    record_starts = list(
        re.finditer(r"(?im)^\s*(?:-\s*)?Cross-FAM Dependency Map:", text)
    )
    if len(record_starts) > 1:
        failures: list[str] = []
        for index, record_start in enumerate(record_starts):
            record_end = (
                record_starts[index + 1].start()
                if index + 1 < len(record_starts)
                else len(text)
            )
            record_text = text[record_start.start() : record_end]
            failures.extend(
                f"Cross-FAM dependency record {index + 1}: {failure}"
                for failure in _validate_cross_fam_dependency_packet_text(record_text)
            )
        return failures

    failures, require = _collect_failures()
    required_markers = (
        "Cross-FAM Dependency Map:",
        "Dependency ID:",
        "Originating FAM:",
        "Originating FFV / Element:",
        "Affected FAMs:",
        "Affected FFV / Element or Not Created:",
        "Dependency Scope Class:",
        "Carry-In / Deferral / Transfer Decision:",
        "Required Contract / Capability:",
        "Suggested Grouping:",
        "Proof Expectation:",
        "Durable Disposition:",
        "Affected FAM Receipt / Fold-Down Target:",
        "Worktree-To-Worktree Mutation:",
    )
    for marker in required_markers:
        require(marker in text, f"Cross-FAM dependency packet missing {marker}")

    normalized_text = governance._normalized_planning_value(text)
    scope_class = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Dependency Scope Class")
    )
    affected_fams = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Affected FAMs")
    )
    affected_ffv = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Affected FFV / Element or Not Created")
    )
    disposition = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Durable Disposition")
    )
    receipt = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Affected FAM Receipt / Fold-Down Target")
    )
    mutation = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Worktree-To-Worktree Mutation")
    )

    allowed_scope_classes = {
        "awareness only",
        "compatibility default",
        "future adoption",
        "local fam only",
        "cross-fam awareness",
        "dependency-bounded cross-fam work",
        "priority carry-in",
        "platform contract",
        "coordinated cross-fam patch",
        "repo-wide migration / halt",
        "transferred fam work",
    }
    require(
        scope_class in allowed_scope_classes,
        "Cross-FAM Dependency Scope Unclassified",
    )
    require(
        "fam-" in affected_fams.casefold(),
        "Cross-FAM dependency packet must name affected FAM ownership",
    )
    require(
        "not created" in affected_ffv.casefold()
        or re.search(r"\bF\d+-FF\d{2}(?:-E\d{2})?\b", affected_ffv, re.IGNORECASE),
        "Cross-FAM dependency packet must name affected FFV / element or Not Created",
    )
    require(
        disposition
        and disposition.casefold()
        not in {"pending", "todo", "tbd", "none", "n/a", "not applicable"},
        "Cross-FAM dependency packet requires a durable disposition",
    )
    require(
        receipt
        and receipt.casefold()
        not in {"pending", "todo", "tbd", "none", "n/a", "not applicable"},
        "Cross-FAM dependency packet requires affected-FAM receipt or fold-down target",
    )
    require(
        "blocked" in mutation.casefold()
        or "not approved" in mutation.casefold()
        or "none" in mutation.casefold(),
        "Cross-FAM dependency packet must block direct worktree-to-worktree mutation",
    )
    live_repo_ledger_terms = (
        "current branch status",
        "active worktree assignment",
        "selected-next truth",
        "pending pr",
        "release-window status",
        "live dependency queue",
    )
    for term in live_repo_ledger_terms:
        require(
            term not in normalized_text,
            f"Cross-FAM dependency packet must not create repo live-state ledger term: {term}",
        )
    return failures


def _owning_fam_from_ffv(path: Path, text: str) -> str:
    candidates = (
        re.search(r"\bFAM-(\d{3})\b", path.name),
        re.search(r"\bF(\d+)-FF\d{2}\b", path.name, re.IGNORECASE),
        re.search(r"\bF(\d+)-FF\d{2}\b", text, re.IGNORECASE),
    )
    for match in candidates:
        if not match:
            continue
        raw = match.group(1)
        if len(raw) == 3:
            return f"FAM-{raw}"
        return f"FAM-{int(raw):03d}"
    return ""


def _validate_family_feature_vision_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    required_markers = (
        "Family Feature Vision ID:",
        "Parent FAM:",
        "Feature Category:",
        "Category-Level Purpose:",
        "USER-Facing Surfaces:",
        "Experience Flow:",
        "Included Capabilities:",
        "Explicit Non-Goals:",
        "Durable Feature Element Inventory:",
        "Deferred Feature Carryforward:",
        "Design Options:",
        "Proof Expectations:",
        "Branch Readiness Consumption Notes:",
        "BP1 Context Notes:",
        "Fold-Down History:",
        "Active-State Wording Scan:",
    )
    for marker in required_markers:
        require(marker in text, f"Family Feature Vision missing {marker}")
        value = governance._extract_marker_value(text, marker)
        require(bool(value), f"Family Feature Vision must give a real value for {marker}")

    ffv_id = governance._extract_marker_value(text, "Family Feature Vision ID:")
    parent_fam = governance._extract_marker_value(text, "Parent FAM:")
    feature_category = governance._extract_marker_value(text, "Feature Category:")
    normalized_category = governance._normalized_planning_value(feature_category)
    require(
        re.search(r"\bF\d+-FF\d{2}\b", ffv_id) is not None,
        "Family Feature Vision Compact ID Missing",
    )
    require(
        re.search(r"\bFAM-\d{3}\b", parent_fam) is not None,
        "Family Feature Vision Parent FAM Missing",
    )
    require(
        not any(
            term in normalized_category
            for term in (
                "slice",
                "slc",
                "seam",
                "branch route",
                "implementation package",
                "selected next",
            )
        ),
        "Family Feature Vision Slice-Scoped",
    )

    element_inventory = governance._extract_marker_value(
        text,
        "Durable Feature Element Inventory:",
    )
    require(
        re.search(r"\bF\d+-FF\d{2}-E\d{2}\b", element_inventory) is not None,
        "FFV Element Proof Chain Missing",
    )

    deferred = governance._extract_marker_value(text, "Deferred Feature Carryforward:")
    normalized_deferred = governance._normalized_planning_value(deferred)
    for term in ("deferred item", "dependency trigger", "grouping recommendation", "proof expectation", "durable disposition"):
        require(
            term in normalized_deferred,
            f"Deferred Feature Carryforward missing {term}",
        )
    live_state_terms = (
        "active",
        "current branch",
        "selected next",
        "pending pr",
        "in progress",
        "next branch",
        "release window status",
    )
    for term in live_state_terms:
        require(
            re.search(rf"\b{re.escape(term)}\b", normalized_deferred) is None,
            f"FFV Live-State Leakage: Deferred Feature Carryforward contains {term}",
        )

    return failures


def _validate_br2_deferred_carryforward_matrix_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    required_markers = (
        "Option name:",
        "Main feature/package objective:",
        "Applicable deferred carryforward items:",
        "Reason each deferred item is applicable:",
        "Dependency trigger:",
        "Recommended grouping:",
        "Deferred items that remain future-gated:",
        "Reason future-gated items remain deferred:",
        "Validation/proof expectations:",
    )
    for marker in required_markers:
        require(marker in text, f"BR2 Deferred Carryforward matrix missing {marker}")
        require(
            bool(governance._extract_marker_value(text, marker)),
            f"BR2 Deferred Carryforward matrix must give a real value for {marker}",
        )
    normalized = governance._normalized_planning_value(text)
    require(
        "deferred item" in normalized or "none" in governance._normalized_planning_value(
            governance._extract_marker_value(text, "Applicable deferred carryforward items:")
        ),
        "Deferred Carryforward Applicability Missing",
    )
    require(
        "dependency trigger" in normalized,
        "Deferred Carryforward Applicability Missing: dependency trigger not explained",
    )
    require(
        "grouping recommendation" in normalized,
        "Deferred Carryforward Applicability Missing: grouping recommendation not explained",
    )
    require(
        "separate branch for every deferred item" not in normalized
        and "one branch per deferred item" not in normalized,
        "Deferred Carryforward Branch Sprawl",
    )
    return failures


def _validate_rebaseline_adoption_review_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    normalized = governance._normalized_planning_value(text)

    required_markers = (
        "RAR Stage:",
        "Trigger Reason:",
        "Source-Truth Files Loaded:",
        "Incoming Standard / Change Summary:",
        "Merged Standard Source:",
        "Rebaseline / Re-entry Event:",
        "Current Branch Implementation Inventory:",
        "Owned Surface Inventory:",
        "Affected File Inventory:",
        "Affected Surface Inventory:",
        "Code-To-Visual Trace Matrix:",
        "Affected Branch Artifacts:",
        "Affected Product Surfaces:",
        "Implemented / Touched UI-UX Surfaces:",
        "Implemented / Touched Runtime-Backend Surfaces:",
        "Affected Proof Claims:",
        "Merged Standard Comparison Result:",
        "Frontend / Backend Contract Findings:",
        "Reference / Template / Primitive Classification:",
        "Accepted Reference Set / Comparative Synthesis:",
        "Accepted Reference / Template / Primitive Comparator Matrix:",
        "UI Reference / Template / Shared Primitive Dependency:",
        "NDAI Product Experience Contract Comparison:",
        "UI Element Inventory:",
        "Backend / State Ownership Trace:",
        "Screenshot / Video / Contact-Sheet Evidence:",
        "Visual Element / Element-Group Inspection Ledger:",
        "Vision-To-Proof Matrix:",
        "Scope Coverage Manifest:",
        "Owned-Surface Nonconformance Ledger:",
        "Current Branch Repair Candidates:",
        "Previous / Historical Branch Issue Candidates:",
        "Current Violation Findings:",
        "Issue-Candidate Table:",
        "Issue Candidate Disposition:",  # Required even when no issue candidate exists.
        "Repair / Waiver / Defer / Route Decision Table:",
        "Adoption Disposition:",
        "Repair / Waiver / Blocker:",
        "Validation Summary:",
        "USER Packet Path:",
        "USER Packet ZIP Path:",
        "Next Legal Phase:",
        "Exact Next USER Decision:",
        "No Repo Live-State Tracking:",
    )
    short_value_allowed_markers = {
        "RAR Stage:",
        "Current Branch Repair Candidates:",
        "Previous / Historical Branch Issue Candidates:",
        "Current Violation Findings:",
        "Issue-Candidate Table:",
        "Issue Candidate Disposition:",
        "Repair / Waiver / Defer / Route Decision Table:",
        "Repair / Waiver / Blocker:",
        "Exact Next USER Decision:",
    }

    def is_allowed_short_marker_value(marker: str, value: str) -> bool:
        normalized_value = governance._normalized_planning_value(value).strip(" .;:")
        if marker == "RAR Stage:" and re.fullmatch(r"rar[0-4]", normalized_value):
            return True
        return marker in short_value_allowed_markers and normalized_value in {
            "none",
            "n/a",
            "not applicable",
        }

    for marker in required_markers:
        value = governance._extract_marker_value(text, marker)
        require(bool(value), f"Rebaseline Adoption Review Missing: {marker}")
        require(
            governance._planning_word_count(value) >= 3
            or is_allowed_short_marker_value(marker, value),
            f"Rebaseline Adoption Review Missing: {marker} is too shallow",
        )

    rar_stage = governance._extract_marker_value(text, "RAR Stage:")
    normalized_rar_stage = governance._normalized_planning_value(rar_stage).strip(
        " .;:"
    )
    active_rar_stage = re.match(r"^rar[0-4]\b", normalized_rar_stage) is not None
    negated_resolved_rar_stage = (
        re.match(
            r"^resolved\b[\s?:,;/-]*(?:no|not|false|pending|unresolved|blocked)\b",
            normalized_rar_stage,
        )
        is not None
        or re.match(
            r"^no applicable impact\b[\s?:,;/-]*(?:no|not|false|pending|unresolved|blocked)\b",
            normalized_rar_stage,
        )
        is not None
    )
    resolved_rar_stage = (
        not negated_resolved_rar_stage
        and (
            re.match(r"^resolved\b", normalized_rar_stage) is not None
            or re.match(r"^no applicable impact\b", normalized_rar_stage) is not None
        )
    )
    require(
        active_rar_stage or resolved_rar_stage,
        "Rebaseline Adoption Review Missing: RAR Stage must name RAR0-RAR4 or a resolved disposition",
    )

    code_trace_header = (
        "| Surface | Element Group | Source File / Code Region | Backend / State Owner | "
        "Rendered Evidence | Accepted Reference | Visual Match | Behavior Match | "
        "Status | Defect / Gap | Next Legal Action |"
    )
    accepted_reference_header = (
        "| Element Class | Implementation Authority | Accepted Reference Set | "
        "Invariant Traits | Feature-Specific Traits | Target Surface | "
        "Primitive/Template/Reference-Derived/Exception | Evidence | Gap / Issue |"
    )
    issue_candidate_header = (
        "| Issue Candidate | Owner FAM | Surface | Element Group | Defect Class | "
        "Evidence | Proposed Carrier | GitHub Issue Mutation Approved? |"
    )
    rar_decision_header = (
        "| RAR USER Decision | Meaning | What It Authorizes | What It Does Not Authorize |"
    )
    require(code_trace_header in text, "Code-To-Visual Trace Missing")
    require(
        accepted_reference_header in text,
        "Accepted Reference Comparator Missing",
    )
    require(issue_candidate_header in text, "Owned Surface Issue Candidate Missing")
    require(rar_decision_header in text, "RAR USER Packet Missing")

    def table_rows_after_header(header: str, expected_columns: int) -> list[list[str]]:
        lines = text.splitlines()
        try:
            header_index = next(
                index for index, line in enumerate(lines) if line.strip() == header
            )
        except StopIteration:
            return []
        rows: list[list[str]] = []
        seen_separator = False
        for offset, line in enumerate(lines[header_index + 1 :], start=header_index + 1):
            if not line.strip().startswith("|"):
                if rows or seen_separator:
                    break
                if line.strip():
                    return [[line.strip()]]
                continue
            cells = governance._markdown_table_cells(line)
            if governance._is_markdown_table_separator(cells):
                if len(cells) != expected_columns:
                    rows.append(cells)
                seen_separator = True
                continue
            if not seen_separator:
                if offset + 1 < len(lines):
                    next_cells = governance._markdown_table_cells(lines[offset + 1])
                    if governance._is_markdown_table_separator(next_cells):
                        break
                continue
            if seen_separator and offset + 1 < len(lines):
                next_cells = governance._markdown_table_cells(lines[offset + 1])
                if governance._is_markdown_table_separator(next_cells):
                    break
            rows.append(cells)
        return rows

    def is_placeholder_table_cell(value: str) -> bool:
        normalized = governance._normalized_planning_value(value).strip(" .;:")
        return normalized in {"", "tbd", "todo", "placeholder"} or normalized.startswith(
            ("tbd ", "todo ", "placeholder ")
        )

    def is_noop_evidence_cell(value: str) -> bool:
        normalized = governance._normalized_planning_value(value).strip(" .;:")
        return normalized in {
            "",
            "none",
            "n/a",
            "no",
            "not applicable",
            "not applicable with reason",
            "validation summary",
        } or normalized.startswith(("not applicable ", "none "))

    def is_noop_evidence_row(row: list[str]) -> bool:
        return all(is_noop_evidence_cell(cell) for cell in row)

    def code_trace_row_is_substantive(row: list[str]) -> bool:
        if len(row) != 11:
            return False
        required_columns = (0, 1, 2, 3, 4, 5, 6, 7, 8, 10)
        return all(not is_noop_evidence_cell(row[index]) for index in required_columns)

    def accepted_reference_row_is_substantive(row: list[str]) -> bool:
        if len(row) != 9:
            return False
        required_columns = (0, 1, 2, 3, 5, 6, 7)
        return all(not is_noop_evidence_cell(row[index]) for index in required_columns)

    def substantive_rows(rows: list[list[str]], expected_columns: int) -> list[list[str]]:
        real_rows: list[list[str]] = []
        for row in rows:
            if len(row) != expected_columns:
                continue
            if any(is_placeholder_table_cell(cell) for cell in row[:expected_columns]):
                continue
            real_rows.append(row)
        return real_rows

    def has_malformed_substantive_table_row(
        rows: list[list[str]], expected_columns: int
    ) -> bool:
        return any(
            len(row) != expected_columns
            or any(is_placeholder_table_cell(cell) for cell in row[:expected_columns])
            for row in rows
        )

    def has_real_issue_candidate_row(rows: list[list[str]]) -> bool:
        for row in rows:
            if len(row) != 8:
                continue
            candidate = governance._normalized_planning_value(row[0])
            owner = governance._normalized_planning_value(row[1])
            surface = governance._normalized_planning_value(row[2])
            element_group = governance._normalized_planning_value(row[3])
            defect_class = governance._normalized_planning_value(row[4])
            evidence = governance._normalized_planning_value(row[5])
            proposed_carrier = governance._normalized_planning_value(row[6])
            github_issue_approved = governance._normalized_planning_value(row[7])
            false_candidate = (
                not candidate
                or candidate in {"none", "n/a", "not applicable"}
                or "no issue candidate" in candidate
                or "missing candidate" in candidate
            )
            if (
                not false_candidate
                and not any(
                    is_placeholder_table_cell(cell)
                    for cell in (
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                    )
                )
                and owner not in {"", "none", "n/a", "not applicable"}
                and surface not in {"", "none", "n/a", "not applicable"}
                and element_group not in {"", "none", "n/a", "not applicable"}
                and defect_class not in {"", "none", "n/a", "not applicable"}
                and evidence not in {"", "none", "n/a", "not applicable"}
                and proposed_carrier not in {"", "none", "n/a", "not applicable"}
                and github_issue_approved in {"yes", "no"}
            ):
                return True
        return False

    raw_code_trace_rows = table_rows_after_header(code_trace_header, 11)
    raw_accepted_reference_rows = table_rows_after_header(accepted_reference_header, 9)
    raw_rar_decision_rows = table_rows_after_header(rar_decision_header, 4)
    code_trace_rows = substantive_rows(raw_code_trace_rows, 11)
    accepted_reference_rows = substantive_rows(raw_accepted_reference_rows, 9)
    rar_decision_rows = substantive_rows(raw_rar_decision_rows, 4)
    issue_candidate_rows = table_rows_after_header(issue_candidate_header, 8)
    require(
        bool(code_trace_rows)
        and not has_malformed_substantive_table_row(raw_code_trace_rows, 11),
        "Code-To-Visual Trace Missing",
    )
    require(
        bool(accepted_reference_rows)
        and not has_malformed_substantive_table_row(raw_accepted_reference_rows, 9),
        "Accepted Reference Comparator Missing",
    )
    require(
        bool(rar_decision_rows)
        and not has_malformed_substantive_table_row(raw_rar_decision_rows, 4),
        "RAR USER Packet Missing",
    )

    def marker_claims_material_surface(value: str) -> bool:
        normalized = governance._normalized_planning_value(value).strip(" .;:")
        if normalized in {
            "",
            "none",
            "n/a",
            "not applicable",
            "not applicable with reason",
        }:
            return False
        if "none with reason" in normalized:
            return False
        no_material_surface_patterns = (
            r"\bno\s+(?:(?:owned|affected|implemented|touched|changed|visible|material|product|ui|ui[-\s]?ux|runtime|runtime[-\s]?backend)\s+){0,4}(?:surface|surfaces|ui|runtime|product|visible|mutation)s?\s+(?:(?:is|are|was|were)\s+)?(?:changed|affected|implemented|touched|present|identified|owned|in\s+scope)\b",
            r"\bno\s+(?:changed|affected|implemented|touched|owned|visible|material)\s+(?:surface|surfaces|ui|runtime|product|visible|mutation)s?\b",
            r"\b(?:no|not\s+applicable)\s+(?:owned\s+|affected\s+|implemented\s+|touched\s+|changed\s+|visible\s+|material\s+)?(?:surface|surfaces)\s+(?:for|in)\s+this\s+(?:branch|review|fixture|packet)\b",
        )
        if any(re.search(pattern, normalized) for pattern in no_material_surface_patterns):
            return False
        return True

    review_claims_material_surfaces = any(
        marker_claims_material_surface(governance._extract_marker_value(text, marker))
        for marker in (
            "Owned Surface Inventory:",
            "Affected Surface Inventory:",
            "Affected Product Surfaces:",
            "Implemented / Touched UI-UX Surfaces:",
            "Implemented / Touched Runtime-Backend Surfaces:",
        )
    )
    trace_proof_required_for_material_surfaces = (
        (active_rar_stage or resolved_rar_stage) and review_claims_material_surfaces
    )
    if trace_proof_required_for_material_surfaces:
        require(
            all(
                not is_noop_evidence_row(row)
                and code_trace_row_is_substantive(row)
                for row in code_trace_rows
            ),
            "Code-To-Visual Trace Missing",
        )
        require(
            all(
                not is_noop_evidence_row(row)
                and accepted_reference_row_is_substantive(row)
                for row in accepted_reference_rows
            ),
            "Accepted Reference Comparator Missing",
        )

    issue_candidate_disposition = governance._extract_marker_value(
        text, "Issue Candidate Disposition:"
    )
    decision_table = governance._extract_marker_value(
        text, "Repair / Waiver / Defer / Route Decision Table:"
    )
    unresolved_statuses = (
        "nonconforming",
        "unproven",
        "partial",
        "exception needed",
        "source-truth gap",
        "reference gap",
        "template gap",
        "shared primitive gap",
        "issue candidate",
    )
    unresolved_comparison_statuses = (
        "mismatch",
        "unproven",
        "partial",
        "nonconforming",
        "exception needed",
        "source-truth gap",
        "reference gap",
        "template gap",
        "shared primitive gap",
    )

    def normalize_rar_status_cell(value: str) -> str:
        normalized_cell = governance._normalized_planning_value(value)
        normalized_cell = normalized_cell.replace("issue-candidate", "issue candidate")
        normalized_cell = normalized_cell.replace("non-conforming", "nonconforming")
        normalized_cell = re.sub(
            r"\b(current|unresolved|active|pending)-(?=issue candidate\b)",
            r"\1 ",
            normalized_cell,
        )
        normalized_cell = re.sub(
            r"\b(current|unresolved|active|pending)\s*[/_]\s*(?=issue candidate\b)",
            r"\1 ",
            normalized_cell,
        )
        return normalized_cell.strip(" .;:")

    def cell_negates_issue_candidate_status(value: str) -> bool:
        normalized_cell = normalize_rar_status_cell(value)
        return bool(
            normalized_cell in {"none", "n/a", "not applicable", "not applicable with reason"}
            or re.search(
                r"\b(?:no|not|without)\s+(?:current\s+|unresolved\s+|active\s+|pending\s+)?issue candidates?\b",
                normalized_cell,
            )
            or re.search(
                r"\bissue candidates?\s+(?:is\s+|are\s+)?not\s+(?:applicable|needed|required|present|open|active)\b",
                normalized_cell,
            )
        )

    def cell_negates_unresolved_status(value: str, status: str) -> bool:
        if status == "issue candidate":
            return cell_negates_issue_candidate_status(value)
        normalized_cell = normalize_rar_status_cell(value)
        if normalized_cell in {"none", "n/a", "not applicable", "not applicable with reason"}:
            return True
        normalized_status = governance._normalized_planning_value(status).strip(" .;:")
        status_pattern = re.escape(normalized_status).replace(r"\ ", r"\s+")
        plural_suffix = r"s?" if normalized_status.endswith("gap") else ""
        return bool(
            re.search(
                rf"\b(?:no|not|without)\s+(?:current\s+|unresolved\s+|active\s+|pending\s+|open\s+)?{status_pattern}{plural_suffix}\b",
                normalized_cell,
            )
            or re.search(
                rf"\bno\b(?:(?!\b(?:but|however|yet)\b|[.;]).){{0,120}}\b{status_pattern}{plural_suffix}\b",
                normalized_cell,
            )
            or re.search(
                rf"\b{status_pattern}{plural_suffix}\s+(?:is\s+|are\s+|was\s+|were\s+)?not\s+(?:applicable|needed|required|present|open|active)\b",
                normalized_cell,
            )
        )

    def contains_non_negated_rar_phrase(value: str, phrases: tuple[str, ...]) -> bool:
        if not value:
            return False
        normalized_value = governance._normalized_planning_value(value)
        for phrase in phrases:
            normalized_phrase = governance._normalized_planning_value(phrase)
            for match in re.finditer(re.escape(normalized_phrase), normalized_value):
                prefix = normalized_value[max(0, match.start() - 48) : match.start()]
                suffix = normalized_value[match.end() : match.end() + 24]
                if re.search(
                    r"(?:^|[\s;:,.(\[])(?:no|not|without)\s+(?:further\s+|active\s+|current\s+|separate\s+)?(?:user\s+)?$",
                    prefix,
                ):
                    continue
                if re.search(
                    r"(?:^|[\s;:,.(\[])(?:no|not)\s+(?:further\s+|active\s+|current\s+)?$",
                    prefix,
                ):
                    continue
                if re.search(
                    r"(?:^|[\s;:,.(\[])(?:does|do|did|will|would|should|must)?\s*not\s+(?:require|need)\s+(?:a\s+|an\s+|the\s+|any\s+)?(?:further\s+|active\s+|current\s+|separate\s+)?(?:user\s+)?$",
                    prefix,
                ):
                    continue
                if re.search(
                    r"(?:^|[\s;:,.(\[])(?:is|are|was|were|remains?|remain)\s+not\s+$",
                    prefix,
                ):
                    continue
                if re.match(r"^\s+needed\b", suffix):
                    continue
                if re.match(
                    r"^\s+(?:is|are|was|were|remains?|remain)?\s*not\s+(?:required|needed|approved|active|open)\b",
                    suffix,
                ):
                    continue
                return True
        return False

    def cell_has_unresolved_status(value: str) -> bool:
        normalized_cell = normalize_rar_status_cell(value)
        return any(
            normalized_cell == status
            or normalized_cell.startswith(f"{status} ")
            or f" {status} " in f" {normalized_cell} "
            for status in unresolved_statuses
            if not cell_negates_unresolved_status(value, status)
        )

    def cell_has_unresolved_comparison(value: str) -> bool:
        normalized_cell = normalize_rar_status_cell(value)
        if normalized_cell in {"none", "n/a", "not applicable", "not applicable with reason"}:
            return False
        return any(
            normalized_cell == status
            or normalized_cell.startswith(f"{status} ")
            or f" {status} " in f" {normalized_cell} "
            for status in unresolved_comparison_statuses
            if not cell_negates_unresolved_status(value, status)
        )

    def cell_has_issue_candidate_status(value: str) -> bool:
        normalized_cell = normalize_rar_status_cell(value)
        if cell_negates_issue_candidate_status(value):
            return False
        return (
            normalized_cell == "issue candidate"
            or normalized_cell.startswith("issue candidate ")
            or f" issue candidate " in f" {normalized_cell} "
        )

    def user_review_action_requires_packet(value: str) -> bool:
        normalized_action = governance._normalized_planning_value(value)
        return any(
            token in normalized_action
            for token in (
                "user",
                "review",
                "decision",
                "waiver",
                "issue candidate",
                "issue-candidate",
                "github issue",
                "route",
                "defer",
            )
        )

    def code_trace_row_requires_user_packet(row: list[str]) -> bool:
        if len(row) <= 10:
            return False
        unresolved_evidence = (
            cell_has_unresolved_status(row[8])
            or cell_has_unresolved_comparison(row[6])
            or cell_has_unresolved_comparison(row[7])
            or cell_has_unresolved_comparison(row[9])
        )
        if not unresolved_evidence:
            return False
        return user_review_action_requires_packet(" ".join((row[9], row[10])))

    def accepted_reference_row_requires_user_packet(row: list[str]) -> bool:
        if len(row) <= 8:
            return False
        unresolved_evidence = (
            cell_has_unresolved_status(row[8])
            or cell_has_unresolved_comparison(row[8])
        )
        if not unresolved_evidence:
            return False
        return user_review_action_requires_packet(row[8])

    user_review_packet_phrases = (
        "rar3",
        "rar3 user review gate",
        "user review gate remains active",
        "user review pending",
        "pending user review",
        "pending user",
        "user reviews",
        "user should review",
        "user review required",
        "user review is required",
        "user review is still required",
        "requires user review",
        "required user review",
        "must review",
        "user must review",
        "user decision",
        "user decision needed",
        "user decision required",
        "requires user decision",
        "user judgment required",
        "user judgment is required",
        "user judgment needed",
        "needs user judgment",
        "need user judgment",
        "requires user judgment",
        "user judgment before",
        "user visual judgment",
        "needs user visual judgment",
        "user adjudication required",
        "needs user adjudication",
        "user approval",
        "approval required",
        "user waiver",
        "waiver required",
        "waiver decision",
        "before waiver",
        "review issue candidate",
        "reviews rar issue candidates",
    )

    def rar_decision_row_requires_user_packet(row: list[str]) -> bool:
        return contains_non_negated_rar_phrase(
            " ".join(row),
            user_review_packet_phrases,
        )

    unresolved_row_user_review_required = any(
        code_trace_row_requires_user_packet(row) for row in code_trace_rows
    ) or any(
        accepted_reference_row_requires_user_packet(row)
        for row in accepted_reference_rows
    ) or any(
        rar_decision_row_requires_user_packet(row) for row in rar_decision_rows
    )
    active_rar_values = governance._normalized_planning_value(
        " ".join(
            governance._extract_marker_value(text, marker)
            for marker in (
                "RAR Stage:",
                "Merged Standard Comparison Result:",
                "Current Violation Findings:",
                "Issue Candidate Disposition:",
                "Repair / Waiver / Defer / Route Decision Table:",
                "Adoption Disposition:",
                "Repair / Waiver / Blocker:",
                "Validation Summary:",
                "Exact Next USER Decision:",
                "Next Legal Phase:",
            )
        )
    )
    pending_user_review_required = contains_non_negated_rar_phrase(
        active_rar_values,
        user_review_packet_phrases,
    ) or unresolved_row_user_review_required

    normalized_product_experience_comparison = governance._normalized_planning_value(
        governance._extract_marker_value(
            text, "NDAI Product Experience Contract Comparison:"
        )
    )
    for quality in (
        "deterministic",
        "intuitive",
        "immersive",
        "predictable",
        "reliable",
        "consistent",
    ):
        require(
            quality in normalized_product_experience_comparison,
            "NDAI Product Experience Contract Comparison Missing",
        )

    for forbidden in (
        "validator green is sufficient",
        "helper pass is sufficient",
        "screenshot exists therefore accepted",
        "template consumed without approved source",
        "shared primitive consumed without approved source",
    ):
        require(
            forbidden not in normalized,
            "Circular Validation Evidence",
        )

    user_packet_path = governance._extract_marker_value(text, "USER Packet Path:")
    user_packet_zip = governance._extract_marker_value(text, "USER Packet ZIP Path:")
    user_packet_path_not_required = "not required" in user_packet_path.casefold()
    user_packet_zip_not_required = "not required" in user_packet_zip.casefold()

    def canonical_windows_path(path: str) -> str | None:
        parts = [part for part in path.split("\\") if part]
        if not parts or re.fullmatch(r"[A-Za-z]:", parts[0]) is None:
            return None
        stack = [parts[0]]
        for part in parts[1:]:
            if part == ".":
                continue
            if part == "..":
                if len(stack) == 1:
                    return None
                stack.pop()
                continue
            stack.append(part)
        return stack[0] + "\\" + "\\".join(stack[1:])

    def has_dot_or_traversal_segment(path: str) -> bool:
        return any(part in {".", ".."} for part in path.split("\\"))

    def has_invalid_path_suffix(suffix: str) -> bool:
        if not suffix or suffix[0].isspace():
            return False
        if suffix[0] == "`":
            suffix = suffix[1:]
            if not suffix or suffix[0].isspace():
                return False
        terminal_punctuation = {",", ";", ":", ")", "]", "."}
        terminal_index = 0
        while (
            terminal_index < len(suffix)
            and suffix[terminal_index] in terminal_punctuation
        ):
            terminal_index += 1
        if terminal_index == 0:
            return True
        return terminal_index < len(suffix) and not suffix[terminal_index].isspace()

    def normalized_user_packet_paths(value: str) -> tuple[list[str], bool]:
        normalized_value = value.replace("/", "\\")
        spans: list[tuple[int, int]] = []
        paths: list[str] = []
        invalid_path_seen = False
        packet_path_pattern = re.compile(
            r"\b[A-Za-z]:\\(?:Nexus USER\\[A-Za-z0-9_-]+(?:\\[^\s|,;:)\]]+)*|[^\s|,;:)\]]+)",
            re.IGNORECASE,
        )
        for match in packet_path_pattern.finditer(normalized_value):
            if any(match.start() >= start and match.end() <= end for start, end in spans):
                continue
            spans.append(match.span())
            if has_invalid_path_suffix(normalized_value[match.end() :]):
                invalid_path_seen = True
                continue
            raw_path = match.group(0)
            if has_dot_or_traversal_segment(raw_path):
                invalid_path_seen = True
                continue
            canonical_path = canonical_windows_path(raw_path)
            if canonical_path is None or canonical_path.casefold().endswith(".zip"):
                invalid_path_seen = True
                continue
            paths.append(canonical_path)
        return paths, invalid_path_seen

    def normalized_windows_zip_paths(value: str) -> tuple[list[str], bool]:
        normalized_value = value.replace("/", "\\")
        spans: list[tuple[int, int]] = []
        paths: list[str] = []
        invalid_suffix_seen = False
        zip_path_patterns = (
            re.compile(
                r"\b[A-Za-z]:\\Nexus USER\\[A-Za-z0-9_-]+-\d{8}-\d{6}\.zip",
                re.IGNORECASE,
            ),
            re.compile(r"\b[A-Za-z]:\\[^|,;:)\]\r\n]+?\.zip", re.IGNORECASE),
        )

        for pattern in zip_path_patterns:
            for match in pattern.finditer(normalized_value):
                if any(
                    max(match.start(), start) < min(match.end(), end)
                    for start, end in spans
                ):
                    continue
                spans.append(match.span())
                if has_invalid_path_suffix(normalized_value[match.end() :]):
                    invalid_suffix_seen = True
                    continue
                raw_path = match.group(0)
                if has_dot_or_traversal_segment(raw_path):
                    invalid_suffix_seen = True
                    continue
                canonical_path = canonical_windows_path(raw_path)
                if canonical_path is None:
                    invalid_suffix_seen = True
                    continue
                paths.append(canonical_path)
        return paths, invalid_suffix_seen

    user_packet_zip_paths, user_packet_zip_invalid_suffix_seen = (
        normalized_windows_zip_paths(user_packet_zip)
    )
    user_packet_paths, user_packet_path_invalid_seen = normalized_user_packet_paths(
        user_packet_path
    )
    user_packet_path_is_rooted = (
        not user_packet_path_invalid_seen
        and len(user_packet_paths) == 1
        and re.fullmatch(
            r"c:\\nexus user\\[a-z0-9_-]+",
            user_packet_paths[0].casefold(),
        )
        is not None
    )
    deterministic_user_zip_paths = [
        path
        for path in user_packet_zip_paths
        if re.fullmatch(
            r"c:\\nexus user\\[a-z0-9_-]+-\d{8}-\d{6}\.zip",
            path.casefold(),
        )
        is not None
    ]
    user_packet_zip_is_deterministic = (
        not user_packet_zip_invalid_suffix_seen
        and len(user_packet_zip_paths) == 1
        and len(deterministic_user_zip_paths) == 1
    )
    user_packet_folder_label = (
        user_packet_paths[0].split("\\")[-1].casefold()
        if user_packet_path_is_rooted
        else ""
    )
    user_packet_zip_label = ""
    if user_packet_zip_is_deterministic:
        zip_name = deterministic_user_zip_paths[0].split("\\")[-1]
        zip_label_match = re.fullmatch(
            r"([A-Za-z0-9_-]+)-\d{8}-\d{6}\.zip",
            zip_name,
            re.IGNORECASE,
        )
        user_packet_zip_label = (
            zip_label_match.group(1).casefold() if zip_label_match else ""
        )
    user_packet_label_matches = (
        not (user_packet_path_is_rooted and user_packet_zip_is_deterministic)
        or user_packet_folder_label == user_packet_zip_label
    )
    require(
        user_packet_path_is_rooted
        or (user_packet_path_not_required and not pending_user_review_required),
        "RAR USER Packet Missing",
    )
    require(
        user_packet_zip_is_deterministic
        or (user_packet_zip_not_required and not pending_user_review_required),
        "RAR USER Packet Missing",
    )
    require(user_packet_label_matches, "RAR USER Packet Missing")

    no_live_state = governance._extract_marker_value(text, "No Repo Live-State Tracking:")
    normalized_no_live_state = governance._normalized_planning_value(no_live_state)
    repo_live_state_patterns = (
        r"\b(?:active|live|current)\b[^.;]{0,100}\b(?:track(?:s|ed|ing)?|stor(?:es|ed|ing)?|record(?:s|ed|ing)?|writ(?:es|ten|ing)?|ledger)\b[^.;]{0,100}\b(?:repo|repository|docs?/)",
        r"\b(?:repo|repository)\s+(?:doc|docs|file|files|source truth|record|records)\b[^.;]{0,100}\b(?:track(?:s|ed|ing)?|stor(?:es|ed|ing)?|record(?:s|ed|ing)?|contain(?:s|ed|ing)?|ledger)\b[^.;]{0,100}\b(?:active|live|current|rar)\b",
        r"\bdocs/[^\s,;:]+[^.;]{0,100}\b(?:track(?:s|ed|ing)?|stor(?:es|ed|ing)?|record(?:s|ed|ing)?|contain(?:s|ed|ing)?|ledger)\b[^.;]{0,100}\b(?:active|live|current|rar)\b",
    )
    repo_live_state_leak = any(
        re.search(pattern, normalized_no_live_state)
        for pattern in repo_live_state_patterns
    )
    require(
        not repo_live_state_leak
        and (
            "c:\\nexus governance state" in no_live_state.casefold()
            or "external" in no_live_state.casefold()
        ),
        "RAR Live Adoption Ledger In Repo",
    )

    previous_candidates = governance._extract_marker_value(
        text, "Previous / Historical Branch Issue Candidates:"
    )

    def no_issue_candidates_declared(value: str) -> bool:
        normalized_value = governance._normalized_planning_value(value).strip(" .;:")
        if not normalized_value:
            return False
        if normalized_value in {
            "none",
            "n/a",
            "not applicable",
            "none recorded",
            "none recorded for this fixture",
            "none with reason",
        }:
            return True
        normalized_value = normalized_value.replace("issue-candidate", "issue candidate")
        concrete_issue_candidate_pattern = (
            r"\bissue candidate\s+(?!is\b|are\b)[a-z0-9][a-z0-9_-]*"
        )
        standalone_issue_candidate_id_pattern = r"\bf\d+-hist-\d+\b"
        no_candidate_wording = normalized_value.startswith(
            (
                "none recorded",
                "none with reason",
                "no previous issue candidate",
                "no previous issue candidates",
                "no historical issue candidate",
                "no historical issue candidates",
                "no previous / historical issue candidate",
                "no previous / historical issue candidates",
                "no issue candidate is applicable",
                "no issue candidates are applicable",
            )
        )
        if no_candidate_wording and re.search(
            concrete_issue_candidate_pattern,
            normalized_value,
        ):
            return False
        if no_candidate_wording and re.search(
            standalone_issue_candidate_id_pattern,
            normalized_value,
        ):
            return False
        if no_candidate_wording:
            return True
        if re.search(concrete_issue_candidate_pattern, normalized_value):
            return False
        if re.search(standalone_issue_candidate_id_pattern, normalized_value):
            return False
        return False

    previous_candidates_absent = no_issue_candidates_declared(previous_candidates)
    if not previous_candidates_absent:
        require(
            has_real_issue_candidate_row(issue_candidate_rows),
            "Owned Surface Issue Candidate Missing",
        )

    adoption_disposition = governance._extract_marker_value(
        text, "Adoption Disposition:"
    )
    code_trace_has_issue_candidate = any(
        len(row) > 8 and cell_has_issue_candidate_status(row[8])
        for row in code_trace_rows
    )
    accepted_reference_has_issue_candidate = any(
        len(row) > 8 and cell_has_issue_candidate_status(row[8])
        for row in accepted_reference_rows
    )
    current_issue_candidate_values = governance._normalized_planning_value(
        " ".join(
            governance._extract_marker_value(text, marker)
            for marker in (
                "Current Branch Repair Candidates:",
                "Current Violation Findings:",
            )
        )
    )
    current_markers_have_issue_candidate = contains_non_negated_rar_phrase(
        current_issue_candidate_values,
        (
            "issue candidate",
            "issue-candidate",
        ),
    )
    if (
        code_trace_has_issue_candidate
        or accepted_reference_has_issue_candidate
        or current_markers_have_issue_candidate
    ):
        require(
            has_real_issue_candidate_row(issue_candidate_rows),
            "Owned Surface Issue Candidate Missing",
        )

    normalized_issue_candidate_disposition = governance._normalized_planning_value(
        issue_candidate_disposition
    )
    normalized_decision_table = governance._normalized_planning_value(decision_table)
    pending_issue_candidate_review = any(
        phrase in normalized_decision_table or phrase in normalized_issue_candidate_disposition
        for phrase in (
            "user review pending",
            "pending user review",
            "pending user",
            "user reviews",
            "user should review",
            "review issue candidate",
        )
    )
    completed_issue_candidate_disposition = any(
        phrase in normalized_issue_candidate_disposition or phrase in normalized_decision_table
        for phrase in (
            "issue candidate packet user-reviewed",
            "issue candidate packet user reviewed",
            "user-reviewed",
            "user reviewed",
            "user waiver recorded",
            "repair completed and revalidated",
            "route back to earlier gate",
        )
    )
    incomplete_issue_candidate_disposition = any(
        phrase in normalized_issue_candidate_disposition or phrase in normalized_decision_table
        for phrase in (
            "not fully user reviewed",
            "not fully user-reviewed",
            "not completely user reviewed",
            "not completely user-reviewed",
            "partially user reviewed",
            "partially user-reviewed",
            "incomplete user reviewed",
            "incomplete user-reviewed",
            "user review incomplete",
            "user-reviewed incomplete",
            "user reviewed incomplete",
        )
    )
    negated_issue_candidate_disposition = any(
        phrase in normalized_issue_candidate_disposition or phrase in normalized_decision_table
        for phrase in (
            "not user reviewed",
            "not user-reviewed",
            "not yet user reviewed",
            "not yet user-reviewed",
            "no user review",
            "without user review",
            "not waived",
            "not repaired",
            "not routed",
            "not yet waived",
            "not yet repaired",
            "not yet routed",
            "not yet blocked",
            "not blocked yet",
            "without active user decision",
            "is required before",
            "required before",
            "has not happened",
            "not happened",
        )
    ) or incomplete_issue_candidate_disposition
    completed_issue_candidate_disposition = (
        completed_issue_candidate_disposition
        and not incomplete_issue_candidate_disposition
    )
    issue_candidate_disposition_text = (
        f"{normalized_issue_candidate_disposition} {normalized_decision_table}"
    )
    non_negated_blocked_disposition = (
        re.search(
            r"(?<![a-z0-9_-])blocked(?![a-z0-9_-])",
            issue_candidate_disposition_text,
        )
        is not None
        and re.search(
            r"\b(?:not|no\s+longer)\s+blocked\b|\bnot\s+yet\s+blocked\b|\bnot\s+blocked\s+yet\b",
            issue_candidate_disposition_text,
        )
        is None
    )
    issue_candidate_disposition_completed = (
        (
            completed_issue_candidate_disposition
            or (non_negated_blocked_disposition and not pending_issue_candidate_review)
        )
        and not negated_issue_candidate_disposition
    )

    def code_trace_row_has_unresolved_rar_evidence(row: list[str]) -> bool:
        if len(row) != 11:
            return False
        status_cell = row[8]
        issue_candidate_dispositioned = (
            cell_has_issue_candidate_status(status_cell)
            and issue_candidate_disposition_completed
        )
        status_unresolved = cell_has_unresolved_status(status_cell)
        comparison_unresolved = (
            cell_has_unresolved_comparison(row[6])
            or cell_has_unresolved_comparison(row[7])
            or cell_has_unresolved_comparison(row[9])
        )
        return (status_unresolved or comparison_unresolved) and not issue_candidate_dispositioned

    def accepted_reference_row_has_unresolved_rar_evidence(row: list[str]) -> bool:
        if len(row) != 9:
            return False
        gap_issue_cell = row[8]
        issue_candidate_dispositioned = (
            cell_has_issue_candidate_status(gap_issue_cell)
            and issue_candidate_disposition_completed
        )
        status_unresolved = cell_has_unresolved_status(gap_issue_cell)
        comparison_unresolved = cell_has_unresolved_comparison(gap_issue_cell)
        return (status_unresolved or comparison_unresolved) and not issue_candidate_dispositioned

    def row_has_unresolved_rar_evidence(row: list[str]) -> bool:
        if len(row) <= 8:
            return False
        if len(row) == 11:
            return code_trace_row_has_unresolved_rar_evidence(row)
        if len(row) == 9:
            return accepted_reference_row_has_unresolved_rar_evidence(row)
        return False

    code_trace_unresolved_present = any(
        row_has_unresolved_rar_evidence(row)
        for row in code_trace_rows
    )
    accepted_reference_unresolved_present = any(
        row_has_unresolved_rar_evidence(row)
        for row in accepted_reference_rows
    )
    unresolved_present = (
        code_trace_unresolved_present or accepted_reference_unresolved_present
    )
    normalized_adoption_disposition = governance._normalized_planning_value(
        adoption_disposition
    )
    green_claim_phrases = (
        "adoption green with evidence",
        "green with evidence",
        "resolved with evidence",
        "all rar checks are green",
        "all rebaseline adoption checks are green",
        "all adoption checks are green",
        "rar checks are green",
        "adoption checks are green",
        "rar green",
        "adoption green",
        "rar closed",
        "adoption closed",
        "rar is closed",
        "adoption is closed",
        "rar was closed",
        "adoption was closed",
    )
    def contains_non_negated_phrase(value: str, phrases: tuple[str, ...]) -> bool:
        negated_spans: list[tuple[int, int]] = []
        ordered_phrases = sorted(phrases, key=len, reverse=True)
        for phrase in ordered_phrases:
            token_pattern = re.compile(
                rf"(?<![a-z0-9_-]){re.escape(phrase)}(?![a-z0-9_-])"
            )
            for match in token_pattern.finditer(value):
                if any(
                    match.start() >= start and match.end() <= end
                    for start, end in negated_spans
                ):
                    continue
                prefix = value[max(0, match.start() - 24) : match.start()]
                if re.search(
                    r"(?:^|[\s;:,(\[])(?:not|no)\s+(?:all\s+)?$",
                    prefix,
                ):
                    negated_spans.append(match.span())
                    continue
                if re.search(r"(?:^|[\s;:,(\[])(?:cannot|can't)\s+(?:be\s+)?$", prefix):
                    negated_spans.append(match.span())
                    continue
                if re.search(r"(?:^|[\s;:,(\[])without\s+$", prefix):
                    negated_spans.append(match.span())
                    continue
                return True
        return False

    green_claim_scope = governance._normalized_planning_value(
        " ".join(
            governance._extract_marker_value(text, marker)
            for marker in (
                "Merged Standard Comparison Result:",
                "Current Violation Findings:",
                "Issue Candidate Disposition:",
                "Repair / Waiver / Defer / Route Decision Table:",
                "Adoption Disposition:",
                "Repair / Waiver / Blocker:",
                "Validation Summary:",
                "Exact Next USER Decision:",
            )
        )
    )
    claims_green = contains_non_negated_phrase(
        green_claim_scope, green_claim_phrases
    )
    require(
        not (unresolved_present and claims_green),
        "Product Experience Contract Nonconformance Unresolved",
    )
    require(
        not (unresolved_present and resolved_rar_stage),
        "Product Experience Contract Nonconformance Unresolved",
    )

    issue_candidate_disposition_required = (
        has_real_issue_candidate_row(issue_candidate_rows)
        or not previous_candidates_absent
        or code_trace_has_issue_candidate
        or accepted_reference_has_issue_candidate
        or current_markers_have_issue_candidate
    )
    if issue_candidate_disposition_required:
        require(
            not negated_issue_candidate_disposition
            and (pending_issue_candidate_review or completed_issue_candidate_disposition),
            "Issue Candidate Disposition Missing",
        )

    normal_phase = governance._extract_marker_value(text, "Next Legal Phase:")
    phase_advancement_scope = governance._normalized_planning_value(
        " ".join(
            governance._extract_marker_value(text, marker)
            for marker in (
                "Merged Standard Comparison Result:",
                "Current Violation Findings:",
                "Issue Candidate Disposition:",
                "Repair / Waiver / Defer / Route Decision Table:",
                "Adoption Disposition:",
                "Repair / Waiver / Blocker:",
                "Validation Summary:",
                "Exact Next USER Decision:",
            )
        )
    )
    active_rar_tokens = (
        "rar user review gate remains active",
        "remains active",
        "pending user",
        "user review pending",
        "issue candidate pending",
        "repair remains required",
        "repair required",
        "waiver required",
        "blocker active",
        "blocked",
        "required before normal phase progression",
    )
    active_rar_context = active_rar_stage or contains_non_negated_phrase(
        active_rar_values,
        active_rar_tokens,
    )
    normalized_next_phase = governance._normalized_planning_value(normal_phase)
    phase_advancement_marker_values = " ".join(
        (
            active_rar_values,
            phase_advancement_scope,
        )
    )
    next_phase_values = normalized_next_phase
    advancement_tokens = (
        "branch readiness",
        "br1",
        "br2",
        "bp1",
        "bp2",
        "bp3",
        "workstream",
        "hardening",
        "live validation",
        "lv1",
        "uts",
        "pr readiness",
        "release readiness",
        "pr creation",
        "merge",
        "release",
    )
    phase_token_pattern = "|".join(
        re.escape(token).replace(r"\ ", r"\s+") for token in advancement_tokens
    )

    negation_tokens = (
        "does not authorize",
        "do not authorize",
        "not authorize",
        "does not approve",
        "do not approve",
        "not approve",
        "does not permit",
        "do not permit",
        "not permit",
        "not authorized",
        "not approved",
        "without authorizing",
        "blocked",
        "remains blocked",
        "stays blocked",
        "held",
        "remains held",
        "does not advance",
        "do not advance",
        "not advance",
        "does not proceed",
        "do not proceed",
        "not proceed",
        "not ready for",
        "not yet ready for",
        "not green for",
        "not yet green for",
        "cannot proceed",
        "must not proceed",
    )
    phase_disclaimer_tokens = tuple(
        token for token in negation_tokens if token not in {"blocked", "held"}
    )
    phase_blocker_tokens = (
        "blocked",
        "remains blocked",
        "stays blocked",
        "held",
        "remains held",
        "stays held",
        "paused",
        "remains paused",
        "deferred",
        "remains deferred",
    )
    phase_action_token_pattern = (
        r"proceed(?:s|ed|ing)?|advance(?:s|d|ment|ing)?|enter(?:s|ed|ing)?|"
        r"resume(?:s|d|ing)?|move(?:s|d|ing)?|continue(?:s|d|ing)?|"
        r"go(?:es|ing)?|start(?:s|ed|ing)?|begin(?:s|ning|gan)?|green|ready"
    )
    phase_disclaimer_token_pattern = "|".join(
        re.escape(token).replace(r"\ ", r"\s+") for token in phase_disclaimer_tokens
    )
    phase_blocker_token_pattern = "|".join(
        re.escape(token).replace(r"\ ", r"\s+") for token in phase_blocker_tokens
    )
    phase_clause_boundary_pattern = r"\b(?:but|however|yet|although|though|while)\b"
    negated_phase_list_pattern = re.compile(
        rf"\b(?:{phase_disclaimer_token_pattern})\b"
        rf"(?:(?!\b(?:{phase_action_token_pattern})\b|[.;]|{phase_clause_boundary_pattern}).){{0,180}}"
        rf"\b(?:{phase_token_pattern})\b"
        rf"(?:\s*,\s*(?:or\s+|and\s+)?\b(?:{phase_token_pattern})\b)*"
    )
    phase_claim_clause_pattern = rf"[,.;]|\b(?:and|but|however|yet|although|though|while)\b"

    def phase_clause_explicitly_blocks_or_holds(clause: str) -> bool:
        if not any(token in clause for token in advancement_tokens):
            return False
        if not re.search(rf"\b(?:{phase_blocker_token_pattern})\b", clause):
            return False
        if re.search(
            rf"\b(?:not|no\s+longer)\s+blocked\b|\bno\s+blockers?\b",
            clause,
        ) and re.search(rf"\b(?:{phase_action_token_pattern})\b", clause):
            return False
        return True

    def phase_clause_denies_phase_without_advancement(clause: str) -> bool:
        if not re.search(rf"\b(?:{phase_token_pattern})(?:\s+stage\s+\d+)?\b", clause):
            return False
        if not re.search(rf"\b(?:{phase_disclaimer_token_pattern})\b", clause):
            return False
        # Keep mixed denial/action clauses so "not approved so continue to PR
        # Readiness" remains an invalid advancement request.
        if re.search(
            rf"\b(?:so|therefore|then|now)\b[\w\s/-]{{0,120}}"
            rf"\b(?:{phase_action_token_pattern})\b",
            clause,
        ):
            return False
        return True

    def strip_negated_phase_disclaimers(value: str) -> str:
        value = negated_phase_list_pattern.sub(" ", value)
        clauses = re.split(phase_claim_clause_pattern, value)
        kept: list[str] = []
        for clause in clauses:
            if phase_clause_explicitly_blocks_or_holds(clause):
                continue
            if phase_clause_denies_phase_without_advancement(clause):
                continue
            kept.append(clause)
        return " ".join(kept)

    phase_advancement_marker_values = strip_negated_phase_disclaimers(
        phase_advancement_marker_values
    )
    next_phase_values = strip_negated_phase_disclaimers(next_phase_values)
    phase_advancement_next_step_scope = strip_negated_phase_disclaimers(
        governance._normalized_planning_value(
            " ".join(
                governance._extract_marker_value(text, marker)
                for marker in (
                    "Repair / Waiver / Defer / Route Decision Table:",
                    "Adoption Disposition:",
                    "Repair / Waiver / Blocker:",
                    "Exact Next USER Decision:",
                )
            )
        )
    )
    phase_advancement_action_pattern = re.compile(
        rf"(?:"
        rf"\b(?:proceed(?:s|ed|ing)?|advance(?:s|d|ment|ing)?|enter(?:s|ed|ing)?|resume(?:s|d|ing)?|move(?:s|d|ing)?\s+(?:to|into)|continue(?:s|d|ing)?\s+(?:to|into)|go(?:es|ing)?\s+(?:to|into)|start(?:s|ed|ing)?(?:\s+(?:to|into))?|begin(?:s|ning|gan)?(?:\s+(?:to|into))?|green\s+for|ready\s+for)\b"
        rf"[\w\s/-]{{0,120}}\b(?:{phase_token_pattern})\b"
        rf"|"
        rf"\b(?:{phase_token_pattern})\b[\w\s/-]{{0,120}}"
        rf"\b(?:proceed(?:s|ed|ing)?|advance(?:s|d|ment|ing)?|enter(?:s|ed|ing)?|resume(?:s|d|ing)?|move(?:s|d|ing)?|continue(?:s|d|ing)?|go(?:es|ing)?|start(?:s|ed|ing)?|begin(?:s|ning|gan)?|green|ready)\b"
        rf")"
    )
    concrete_next_phase_requested = any(
        token in next_phase_values
        for token in advancement_tokens
    )
    concrete_marker_advancement_requested = (
        phase_advancement_action_pattern.search(phase_advancement_marker_values)
        is not None
    )
    bare_phase_next_step_pattern = re.compile(
        rf"(?:"
        rf"^\s*\b(?:{phase_token_pattern})(?:\s+stage\s+\d+)?\b\s*$"
        rf"|"
        rf"\b(?:{phase_token_pattern})(?:\s+stage\s+\d+)?\b\s+"
        rf"(?:after|once|when|upon|on)\s+[\w\s/-]{{0,80}}"
        rf"\b(?:validation|green|review|approval|waiver|repair|closeout|resolved)\b"
        rf")"
    )
    concrete_marker_bare_phase_requested = (
        bare_phase_next_step_pattern.search(phase_advancement_next_step_scope)
        is not None
    )
    concrete_advancement_requested = concrete_next_phase_requested or (
        concrete_marker_advancement_requested or concrete_marker_bare_phase_requested
    )

    def normal_phase_progression_claimed(value: str) -> bool:
        clauses = re.split(phase_claim_clause_pattern, value)
        for clause in clauses:
            cleaned_clause = clause
            for blocker_phrase in (
                "required before normal phase progression",
                "before normal phase progression",
            ):
                cleaned_clause = cleaned_clause.replace(blocker_phrase, "")
            for match in re.finditer(r"\bnormal phase progression\b", cleaned_clause):
                local_context = cleaned_clause[
                    max(0, match.start() - 80) : match.end() + 80
                ]
                if any(token in local_context for token in negation_tokens):
                    continue
                return True
        return False

    generic_advancement_requested = normal_phase_progression_claimed(
        " ".join(
            (
                phase_advancement_marker_values,
                next_phase_values,
            )
        )
    )
    advancement_requested = (
        generic_advancement_requested
        or concrete_advancement_requested
    )
    require(
        not (advancement_requested and active_rar_context),
        "Normal Phase Progression Blocked By RAR",
    )
    return failures


def _validate_visual_acceptance_enforcement_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    normalized = governance._normalized_planning_value(text)

    required_markers = (
        "Material Visible Change Classification:",
        "Visual Acceptance Target Plan:",
        "Render Authority Level:",
        "Implementation Authority Classification:",
        "Accepted Reference Set / Comparative Synthesis:",
        "Visual Family Relation Proof:",
        "Implementation Authority Table:",
        "Functionality Role Contract:",
        "Implementation Match Proof Plan:",
        "Pre-Live Visual Purpose Conformance:",
        "Visual Acceptance Chain:",
        "Packet Reviewability vs Product Acceptance:",
    )
    marker_failures = {
        "Visual Acceptance Target Plan:": EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET,
        "Implementation Authority Classification:": EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET,
        "Accepted Reference Set / Comparative Synthesis:": EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET,
        "Visual Family Relation Proof:": EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET,
        "Implementation Authority Table:": EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET,
        "Functionality Role Contract:": EXPECTED_FUNCTIONALITY_ROLE_FAILURE_SNIPPET,
        "Implementation Match Proof Plan:": EXPECTED_IMPLEMENTATION_MATCH_PROOF_FAILURE_SNIPPET,
        "Pre-Live Visual Purpose Conformance:": EXPECTED_PRE_LIVE_VISUAL_PURPOSE_FAILURE_SNIPPET,
    }
    for marker in required_markers:
        value = governance._extract_marker_value(text, marker)
        require(
            bool(value) and governance._planning_word_count(value) >= 3,
            marker_failures.get(marker, f"Visual Acceptance Chain Missing: {marker}"),
        )

    visual_family_header = (
        "| Surface / Window | Role Classification | Implementation Authority | Accepted Reference | "
        "Element Group | Invariant Traits | Feature-Specific Traits | Rendered Evidence | "
        "Visual Match | Functional Match | Verdict | Next Legal Action |"
    )
    implementation_authority_header = (
        "| Surface / Window | Approved Template? | Approved Shared Primitive? | Promoted Reference Consumed? | "
        "Reference-Derived? | One-Off? | Gap / Exception | Proof Required |"
    )
    functionality_role_header = (
        "| Window / Surface | Product Role | Parent / Launch Source | Primary Actions | Secondary Actions | "
        "Non-Goals | Backend / State Owner | UI-Visible Truth Mapping | Recovery / Failure Behavior | "
        "Separate Surface Justification |"
    )
    visual_chain_header = (
        "| Gate | Required Visual Proof | What Cannot Prove It | Blocking Condition | USER Decision Needed? |"
    )

    def table_rows_after_header(header: str, expected_columns: int) -> list[list[str]]:
        lines = text.splitlines()
        try:
            header_index = next(
                index for index, line in enumerate(lines) if line.strip() == header
            )
        except StopIteration:
            return []
        rows: list[list[str]] = []
        seen_separator = False
        for line in lines[header_index + 1 :]:
            if not line.strip().startswith("|"):
                if rows or seen_separator:
                    break
                if line.strip():
                    return [[line.strip()]]
                continue
            cells = governance._markdown_table_cells(line)
            if governance._is_markdown_table_separator(cells):
                if len(cells) != expected_columns:
                    rows.append(cells)
                seen_separator = True
                continue
            if not seen_separator:
                continue
            rows.append(cells)
        return rows

    def is_placeholder_cell(value: str) -> bool:
        normalized_value = governance._normalized_planning_value(value).strip(" .;:")
        return normalized_value in {
            "",
            "tbd",
            "todo",
            "placeholder",
            "none",
            "n/a",
            "not applicable",
        } or normalized_value.startswith(("tbd ", "todo ", "placeholder "))

    def has_substantive_label_value(label: str) -> bool:
        return bool(substantive_label_values(label))

    def substantive_label_values(label: str) -> list[str]:
        label_pattern = re.escape(label)
        values: list[str] = []
        for match in re.finditer(
            rf"(?im){label_pattern}\s*([^\n|]+)",
            text,
        ):
            value = governance._normalized_planning_value(match.group(1)).strip(
                " .;:`"
            )
            if not value or is_placeholder_cell(value):
                continue
            if any(
                placeholder in value
                for placeholder in (
                    "to be determined",
                    "pending user review",
                    "pending user decision",
                    "pending approval",
                    "pending review",
                    "not yet defined",
                    "not selected",
                    "not approved",
                    "missing",
                    "omitted",
                )
            ):
                continue
            values.append(value)
        return values

    def is_affirmative_authority_cell(value: str) -> bool:
        normalized_value = governance._normalized_planning_value(value).strip(" .;:")
        return bool(
            re.match(
                r"^(yes|approved)(?:\b|[\s:;-])",
                normalized_value,
            )
        )

    def substantive_rows(rows: list[list[str]], expected_columns: int) -> list[list[str]]:
        return [
            row
            for row in rows
            if len(row) == expected_columns
            and not any(is_placeholder_cell(cell) for cell in row[:expected_columns])
        ]

    def has_incomplete_table_rows(rows: list[list[str]], expected_columns: int) -> bool:
        return any(
            len(row) != expected_columns
            or any(is_placeholder_cell(cell) for cell in row[:expected_columns])
            for row in rows
        )

    def catalog_currently_promotes_templates() -> bool:
        try:
            catalog_text = governance._normalized_planning_value(
                UI_REFERENCE_CATALOG_README.read_text(encoding="utf-8")
            )
        except OSError:
            return False
        return (
            "current implementation-template status: no catalog record currently promotes"
            not in catalog_text
        )

    def catalog_currently_promotes_shared_primitives() -> bool:
        try:
            catalog_text = governance._normalized_planning_value(
                UI_REFERENCE_CATALOG_README.read_text(encoding="utf-8")
            )
        except OSError:
            return False
        return (
            "current shared-primitive status: no catalog record currently promotes"
            not in catalog_text
        )

    def source_values_point_at_reference_records(values: list[str]) -> bool:
        return any(
            "docs/ui_reference_catalog/uiref-" in value
            or re.search(r"\buiref-\d{3}\b", value)
            for value in values
        )

    visual_family_table_rows = table_rows_after_header(visual_family_header, 12)
    implementation_authority_table_rows = table_rows_after_header(
        implementation_authority_header,
        8,
    )
    functionality_role_table_rows = table_rows_after_header(
        functionality_role_header,
        10,
    )
    visual_chain_table_rows = table_rows_after_header(visual_chain_header, 5)
    visual_family_rows = substantive_rows(
        visual_family_table_rows,
        12,
    )
    implementation_authority_rows = substantive_rows(
        implementation_authority_table_rows,
        8,
    )
    functionality_role_rows = substantive_rows(
        functionality_role_table_rows,
        10,
    )
    visual_chain_rows = substantive_rows(
        visual_chain_table_rows,
        5,
    )
    require(
        not has_incomplete_table_rows(visual_family_table_rows, 12),
        EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET,
    )
    require(
        not has_incomplete_table_rows(implementation_authority_table_rows, 8),
        EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET,
    )
    require(
        not has_incomplete_table_rows(functionality_role_table_rows, 10),
        EXPECTED_FUNCTIONALITY_ROLE_FAILURE_SNIPPET,
    )
    require(
        not has_incomplete_table_rows(visual_chain_table_rows, 5),
        "Visual Acceptance Chain Missing",
    )
    require(bool(visual_family_rows), EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET)
    require(
        bool(implementation_authority_rows),
        EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET,
    )
    require(bool(functionality_role_rows), EXPECTED_FUNCTIONALITY_ROLE_FAILURE_SNIPPET)
    require(bool(visual_chain_rows), "Visual Acceptance Chain Missing")

    visual_target = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Visual Acceptance Target Plan:")
    )
    placeholder_visual_target_terms = (
        "tbd",
        "todo",
        "placeholder",
        "to be determined",
        "pending user review",
        "pending user decision",
        "pending approval",
        "pending review",
        "not yet defined",
        "not selected",
        "missing",
        "omitted",
        "none",
        "no target",
    )
    def has_reasoned_not_applicable(value: str) -> bool:
        if "not applicable with reason" not in value:
            return False
        reason = value.split("not applicable with reason", 1)[1].strip(" .:-")
        return governance._planning_word_count(reason) >= 3

    visual_target_not_applicable = has_reasoned_not_applicable(visual_target)
    visual_target_path_labels = (
        "Reviewable Visual Acceptance Target Path:",
        "Accepted Visual Acceptance Target Path:",
        "Design Candidate Packet Path:",
    )
    visual_target_path_values = [
        value
        for label in visual_target_path_labels
        for value in substantive_label_values(label)
    ]

    def is_reviewable_visual_target_path(value: str) -> bool:
        normalized_value = governance._normalized_planning_value(value)
        if any(term in normalized_value for term in placeholder_visual_target_terms):
            return False
        if "docs/ui_reference_catalog/" in normalized_value:
            return False
        has_artifact_extension = re.search(
            r"\.(?:md|png|jpg|jpeg|webp|mp4|mov|zip|pdf|html)\b",
            normalized_value,
            re.IGNORECASE,
        )
        has_path_context = re.search(
            r"(?:[a-z]:\\|\\\\|\\|/|c:\\nexus user\\|user review|"
            r"review aids|source truth context)",
            normalized_value,
            re.IGNORECASE,
        )
        return bool(has_artifact_extension and has_path_context)

    require(
        bool(visual_target)
        and (
            "visual acceptance target" in visual_target
            or visual_target_not_applicable
        )
        and not any(
            forbidden in visual_target
            for forbidden in (
                "after implementation",
                "after workstream",
                "backfill",
                "packet path only",
                "screenshot only",
            )
        ),
        EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET,
    )
    require(
        not any(term in visual_target for term in placeholder_visual_target_terms),
        EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET,
    )
    require(
        visual_target_not_applicable
        or any(is_reviewable_visual_target_path(value) for value in visual_target_path_values),
        EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET,
    )

    implementation_match_proof = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Implementation Match Proof Plan:")
    )
    placeholder_implementation_match_terms = placeholder_visual_target_terms + (
        "pending proof",
        "future proof",
        "future review",
        "to be supplied",
    )
    implementation_match_evidence_terms = (
        "screenshot",
        "video",
        "ordered-frame",
        "frame proof",
        "rendered",
        "comparison",
        "compare",
        "trace",
        "code region",
    )
    require(
        not any(term in implementation_match_proof for term in placeholder_implementation_match_terms),
        EXPECTED_IMPLEMENTATION_MATCH_PROOF_FAILURE_SNIPPET,
    )
    require(
        any(term in implementation_match_proof for term in implementation_match_evidence_terms),
        EXPECTED_IMPLEMENTATION_MATCH_PROOF_FAILURE_SNIPPET,
    )

    authority_marker = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Implementation Authority Classification:")
    )
    authority_scope = governance._normalized_planning_value(
        " ".join(
            (
                authority_marker,
                " ".join(" ".join(row) for row in implementation_authority_rows),
                " ".join(
                    row[2] for row in visual_family_rows if len(row) >= 3
                ),
            )
        )
    )
    authority_terms = (
        "shared primitive consumed",
        "implementation template instantiated",
        "reference-derived implementation",
        "one-off implementation",
        "user-approved exception",
        "reference gap",
        "template gap",
        "shared primitive gap",
        "source-truth gap",
    )
    table_claims_template = any(
        len(row) >= 2 and is_affirmative_authority_cell(row[1])
        for row in implementation_authority_rows
    )
    table_claims_shared_primitive = any(
        len(row) >= 3 and is_affirmative_authority_cell(row[2])
        for row in implementation_authority_rows
    )

    def has_affirmative_template_reference(value: str) -> bool:
        action_pattern = re.compile(
            r"\b(?:claim|claims|claimed|consume|consumes|consumed|instantiate|"
            r"instantiates|instantiated|use|uses|used|using|approved)\b"
        )
        negation_terms = (
            "not approved",
            "not consumed",
            "not instantiated",
            "not used",
            "no approved",
            "no template",
            "without approved",
            "does not consume",
            "does not instantiate",
        )
        for match in re.finditer(r"\bai control center template\b", value):
            local_context = value[max(0, match.start() - 80) : match.end() + 80]
            for clause in re.split(
                r"[.;]|\b(?:but|however|yet|although|though|while|then)\b",
                local_context,
            ):
                if not action_pattern.search(clause):
                    continue
                if any(negation in clause for negation in negation_terms):
                    continue
                return True
        return False

    require(
        any(term in authority_scope for term in authority_terms),
        EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET,
    )
    marker_authority_matches = [
        term for term in authority_terms if term in authority_marker
    ]
    require(
        len(marker_authority_matches) == 1,
        EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET,
    )
    if (
        "implementation template instantiated" in authority_scope
        or "approved template? yes" in authority_scope
        or "template consumed" in authority_scope
        or has_affirmative_template_reference(authority_scope)
        or table_claims_template
    ):
        template_source_values = substantive_label_values("Template source path:")
        require(
            bool(template_source_values),
            EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET,
        )
        require(
            catalog_currently_promotes_templates()
            and not source_values_point_at_reference_records(template_source_values),
            EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET,
        )
        require(
            has_substantive_label_value("Template consumer contract:"),
            EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET,
        )
    if (
        "shared primitive consumed" in authority_scope
        or "approved shared primitive? yes" in authority_scope
        or "shared primitive consumed" in normalized
        or table_claims_shared_primitive
    ):
        primitive_source_values = substantive_label_values("Primitive source path:")
        require(
            bool(primitive_source_values),
            EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET,
        )
        require(
            catalog_currently_promotes_shared_primitives()
            and not source_values_point_at_reference_records(primitive_source_values),
            EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET,
        )
        require(
            has_substantive_label_value("Primitive consumer contract:"),
            EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET,
        )

    reference_scope = governance._normalized_planning_value(
        governance._extract_marker_value(
            text, "Accepted Reference Set / Comparative Synthesis:"
        )
    )
    reference_comparison_blockers = (
        "not compared",
        "not yet compared",
        "without comparison",
        "comparison later",
        "compare later",
        "later comparison",
        "future comparison",
        "future compare",
        "comparison pending",
        "pending comparison",
        "to be compared",
        "will compare",
        "will be compared",
    )
    require(
        (
            "uiref" in reference_scope
            or "accepted reference" in reference_scope
            or "promoted reference" in reference_scope
        )
        and any(
            token in reference_scope
            for token in ("element-by-element", "row-by-row", "side-by-side")
        ),
        EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET,
    )
    require(
        not any(blocker in reference_scope for blocker in reference_comparison_blockers),
        EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET,
    )

    pre_live_scope = governance._normalized_planning_value(
        governance._extract_marker_value(
            text, "Pre-Live Visual Purpose Conformance:"
        )
    )
    require(
        bool(pre_live_scope)
        and "before live validation" in pre_live_scope
        and "implementation match" in pre_live_scope,
        EXPECTED_PRE_LIVE_VISUAL_PURPOSE_FAILURE_SNIPPET,
    )

    reviewability_acceptance_target = (
        r"(?:(?:product|visual|user visual|user)\s+acceptance|"
        r"(?:product|visual|user visual|user)\s+accepted|acceptance|accepted)"
    )
    false_green_pending_negation = (
        r"(?!\s*(?:[,;:.-]\s*)?(?:which\s+)?"
        r"(?:remains|stays|is\s+pending|pending|requires|only\s+after|after|until|separate))"
    )
    packet_reviewability_false_green_pattern = re.compile(
        r"(?:"
        r"(?:packet reviewability|reviewable\s+packet|reviewable status|reviewability status|packet status)\s+"
        r"(?:proves|equals|is|means)\s+"
        + reviewability_acceptance_target
        + r")\b"
        + false_green_pending_negation,
        re.IGNORECASE,
    )
    require(
        packet_reviewability_false_green_pattern.search(normalized) is None,
        EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET,
    )

    for pattern, snippet in (
        (
            r"\bscreenshot\s+exists\s+therefore\s+accepted\b|"
            r"\bscreenshot(?:s|\s+(?:exists|existence|paths?))?\s+(?:therefore\s+)?"
            r"(?:prove(?:s)?|equals|is|mean(?:s)?|therefore)\s+"
            + reviewability_acceptance_target
            + r"\b"
            + false_green_pending_negation,
            EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET,
        ),
        (
            r"\b(?:(?:helper|validator)(?:\s+(?:output|result|validation))?"
            r"\s+(?:green|pass|passed)|validation\s+pass(?:ed)?)\s+"
            r"(?:proves|equals|is|means|therefore)\s+"
            + reviewability_acceptance_target
            + r"\b"
            + false_green_pending_negation,
            EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET,
        ),
        (
            r"\bcss\s+(?:marker\s+)?similarity\s+(?:proves|equals|is|means)\s+visual\s+family\b",
            EXPECTED_CSS_VISUAL_FAMILY_FAILURE_SNIPPET,
        ),
        (
            r"\buiref\s+citation\s+alone\s+is\s+sufficient\b|\b(?:uiref|reference)\s+citation\s+(?:alone\s+)?(?:proves|equals|is|means)\s+(?:(?:visual|product)\s+)?(?:acceptance|accepted|proof|sufficient)\b"
            + false_green_pending_negation,
            EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET,
        ),
        (
            r"\breference\s+cited\s+but\s+not\s+compared\b",
            EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET,
        ),
        (
            r"\bimplementation-first\s+visual\s+target\s+backfill\b",
            EXPECTED_IMPLEMENTATION_FIRST_TARGET_FAILURE_SNIPPET,
        ),
        (
            r"\bvisual\s+target\s+created\s+after\s+implementation\b",
            EXPECTED_IMPLEMENTATION_FIRST_TARGET_FAILURE_SNIPPET,
        ),
    ):
        require(re.search(pattern, normalized) is None, snippet)

    role_scope = governance._normalized_planning_value(
        " ".join(
            (
                governance._extract_marker_value(text, "Functionality Role Contract:"),
                " ".join(" ".join(row) for row in functionality_role_rows),
            )
        )
    )
    require(
        "role ambiguous" not in role_scope
        and "unrouted detached child" not in role_scope
        and "unclear parent" not in role_scope,
        EXPECTED_FUNCTIONALITY_ROLE_FAILURE_SNIPPET,
    )

    unresolved_visual_verdicts = (
        "unproven",
        "partial",
        "nonconforming",
        "reference gap",
        "template gap",
        "shared primitive gap",
        "source-truth gap",
        "mismatch",
        "not compared",
        "not reviewed",
        "not evaluated",
        "uncompared",
        "unreviewed",
        "comparison missing",
    )
    green_visual_verdict_pattern = re.compile(
        r"\b(?:conforming|green|pass|accepted|resolved)\b"
    )
    for row in visual_family_rows:
        visual_match = governance._normalized_planning_value(row[8]).strip(" .;:")
        functional_match = governance._normalized_planning_value(row[9]).strip(" .;:")
        verdict = governance._normalized_planning_value(row[10]).strip(" .;:")
        next_action = governance._normalized_planning_value(row[11])
        comparison_scope = " ".join((visual_match, functional_match, verdict))
        if any(status in comparison_scope for status in unresolved_visual_verdicts):
            require(
                green_visual_verdict_pattern.search(verdict) is None,
                EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET,
            )
            require(
                any(
                    token in next_action
                    for token in ("repair", "block", "user decision", "issue candidate", "defer")
                ),
                EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET,
            )

    return failures


def _validate_visual_acceptance_enforcement_fixtures() -> list[str]:
    failures: list[str] = []

    branch_plan_readme = ROOT / "Docs" / "branch_plans" / "README.md"
    branch_plan_text = branch_plan_readme.read_text(encoding="utf-8")
    for required_label in (
        "Implementation Authority Classification:",
        "Render Authority Level:",
        "Reviewable Visual Acceptance Target Path:",
        "Visual Family Relation Proof:",
        "Functionality Role Contract:",
        "Pre-Live Visual Purpose Conformance:",
    ):
        if f"`{required_label}`" not in branch_plan_text:
            failures.append(
                "Branch Planning README visual-proof field label drift: "
                f"{required_label}"
            )
    for stale_label in (
        "`Visual Family Relation Proof Table:`",
        "`Functionality Role Contract Table:`",
        "`Pre-Live Visual Purpose Conformance Plan:`",
    ):
        if stale_label in branch_plan_text:
            failures.append(
                "Branch Planning README still documents stale visual-proof label "
                f"{stale_label}"
            )

    valid_text = VALID_VISUAL_ACCEPTANCE_ENFORCEMENT_FIXTURE.read_text(
        encoding="utf-8"
    )
    valid_failures = _validate_visual_acceptance_enforcement_text(valid_text)
    if valid_failures:
        failures.append(
            "Valid Visual Acceptance enforcement fixture unexpectedly failed: "
            + "; ".join(valid_failures[:5])
        )

    generated_missing_render_authority = valid_text.replace(
        "Render Authority Level: Visual Acceptance Target - reviewable target packet exists before Workstream and USER acceptance remains pending.\n\n",
        "",
    )
    generated_missing_render_authority_failures = "\n".join(
        _validate_visual_acceptance_enforcement_text(
            generated_missing_render_authority
        )
    )
    if "Visual Acceptance Chain Missing: Render Authority Level:" not in generated_missing_render_authority_failures:
        failures.append(
            "Generated Visual Acceptance fixture did not reject missing Render Authority Level"
        )

    invalid_cases = (
        (
            INVALID_VISUAL_ACCEPTANCE_MISSING_TARGET_FIXTURE,
            EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET,
            "missing Visual Acceptance Target",
        ),
        (
            INVALID_VISUAL_ACCEPTANCE_SCREENSHOT_GREEN_FIXTURE,
            EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET,
            "screenshot path treated as Visual Acceptance",
        ),
        (
            INVALID_VISUAL_ACCEPTANCE_UIREF_NO_COMPARISON_FIXTURE,
            EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET,
            "UIREF citation without element comparison",
        ),
        (
            INVALID_VISUAL_ACCEPTANCE_TEMPLATE_CLAIM_FIXTURE,
            EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET,
            "template claim without approved template source",
        ),
        (
            INVALID_VISUAL_ACCEPTANCE_PACKET_REVIEWABILITY_ACCEPTANCE_FIXTURE,
            EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET,
            "packet reviewability treated as product acceptance",
        ),
        (
            INVALID_VISUAL_ACCEPTANCE_ROLE_AMBIGUOUS_FIXTURE,
            EXPECTED_FUNCTIONALITY_ROLE_FAILURE_SNIPPET,
            "role-ambiguous window allowed to continue",
        ),
        (
            INVALID_VISUAL_ACCEPTANCE_REFERENCE_SET_AS_AUTHORITY_FIXTURE,
            EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET,
            "accepted reference set compared used as implementation authority",
        ),
    )
    for fixture, expected_snippet, label in invalid_cases:
        result = _validate_visual_acceptance_enforcement_text(
            fixture.read_text(encoding="utf-8")
        )
        if expected_snippet not in "\n".join(result):
            failures.append(
                f"Invalid Visual Acceptance fixture did not reject {label}"
            )

    generated_incomplete_second_visual_row = valid_text.replace(
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Match planned through row-by-row comparison | Match planned through local diagnostic action proof | CONFORMING WHEN PROVEN | Continue only after Pre-Live proof is green |",
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Match planned through row-by-row comparison | Match planned through local diagnostic action proof | CONFORMING WHEN PROVEN | Continue only after Pre-Live proof is green |\n| AI readiness child window | TBD | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame and compact controls | Readiness content may differ | TBD | Match planned | Match planned | CONFORMING WHEN PROVEN | Continue only after Pre-Live proof is green |",
    )
    generated_incomplete_row_failures = _validate_visual_acceptance_enforcement_text(
        generated_incomplete_second_visual_row
    )
    if EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET not in "\n".join(
        generated_incomplete_row_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject incomplete second visual row"
        )

    generated_visual_family_template_authority_claim = valid_text.replace(
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Match planned through row-by-row comparison | Match planned through local diagnostic action proof | CONFORMING WHEN PROVEN | Continue only after Pre-Live proof is green |",
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Implementation Template Instantiated | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Match planned through row-by-row comparison | Match planned through local diagnostic action proof | CONFORMING WHEN PROVEN | Continue only after Pre-Live proof is green |",
    )
    generated_visual_family_template_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_visual_family_template_authority_claim
        )
    )
    if EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_visual_family_template_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject template claim hidden in visual-family row"
        )

    generated_visual_match_columns_unresolved_claim = valid_text.replace(
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Match planned through row-by-row comparison | Match planned through local diagnostic action proof | CONFORMING WHEN PROVEN | Continue only after Pre-Live proof is green |",
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Mismatch | Unproven | CONFORMING | Continue |",
    )
    generated_visual_match_unresolved_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_visual_match_columns_unresolved_claim
        )
    )
    if EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET not in "\n".join(
        generated_visual_match_unresolved_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject unresolved match columns with green verdict"
        )

    generated_visual_match_not_compared_green_claim = valid_text.replace(
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Match planned through row-by-row comparison | Match planned through local diagnostic action proof | CONFORMING WHEN PROVEN | Continue only after Pre-Live proof is green |",
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Not compared | Not compared | CONFORMING | Continue |",
    )
    generated_not_compared_green_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_visual_match_not_compared_green_claim
        )
    )
    if EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET not in "\n".join(
        generated_not_compared_green_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject not-compared match columns with green verdict"
        )

    generated_reference_not_compared_claim = valid_text.replace(
        "Accepted Reference Set / Comparative Synthesis: UIREF-001, UIREF-002, UIREF-003, UIREF-004, AI Dashboard, and AI Control Center are compared element-by-element for invariant chrome, controls, rows, cards, spacing, typography, glow, and visible state behavior.",
        "Accepted Reference Set / Comparative Synthesis: UIREF-001 is cited but not compared.",
    )
    generated_reference_not_compared_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_reference_not_compared_claim
        )
    )
    if EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET not in "\n".join(
        generated_reference_not_compared_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject negated accepted-reference comparison"
        )

    generated_reference_later_comparison_claim = valid_text.replace(
        "Accepted Reference Set / Comparative Synthesis: UIREF-001, UIREF-002, UIREF-003, UIREF-004, AI Dashboard, and AI Control Center are compared element-by-element for invariant chrome, controls, rows, cards, spacing, typography, glow, and visible state behavior.",
        "Accepted Reference Set / Comparative Synthesis: UIREF-001 and AI Control Center comparison later.",
    )
    generated_reference_later_comparison_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_reference_later_comparison_claim
        )
    )
    if EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET not in "\n".join(
        generated_reference_later_comparison_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject future-only accepted-reference comparison"
        )

    generated_visual_nonconforming_blocker_claim = valid_text.replace(
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Match planned through row-by-row comparison | Match planned through local diagnostic action proof | CONFORMING WHEN PROVEN | Continue only after Pre-Live proof is green |",
        "| AI diagnostics child window | Detached child diagnostics surface launched from AI Dashboard | Reference-Derived Implementation | UIREF-001, UIREF-002, AI Dashboard, AI Control Center | Window frame and compact control cluster | Seamless rounded NDAI frame, compact top-right control cluster, deterministic glow and spacing | Diagnostics title and local readiness rows may differ by content only | Focused screenshot set and ordered-frame proof | Mismatch | Unproven | NONCONFORMING | Repair before continuing |",
    )
    generated_visual_nonconforming_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_visual_nonconforming_blocker_claim
        )
    )
    if EXPECTED_VISUAL_FAMILY_RELATION_FAILURE_SNIPPET in "\n".join(
        generated_visual_nonconforming_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture falsely rejected nonconforming blocker row as green"
        )

    generated_shared_primitive_claim = valid_text.replace(
        "Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Shared Primitive Consumed - the branch claims a shared primitive but omits the primitive source path.",
    ).replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | None | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | No | Yes | Yes - UIREF-001 and UIREF-002 | No | No | None | Element-by-element visual family proof before Workstream and Pre-Live. |",
    )
    generated_shared_primitive_failures = _validate_visual_acceptance_enforcement_text(
        generated_shared_primitive_claim
    )
    if EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_shared_primitive_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject shared primitive claim without source"
        )

    generated_placeholder_visual_target_claim = valid_text.replace(
        "Visual Acceptance Target Plan: Visual Acceptance Target is defined before Workstream from UIREF-001 through UIREF-004 and the accepted AI Dashboard / AI Control Center comparator set.",
        "Visual Acceptance Target Plan: Visual Acceptance Target is TBD pending USER review.",
    )
    generated_placeholder_target_failures = _validate_visual_acceptance_enforcement_text(
        generated_placeholder_visual_target_claim
    )
    if EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET not in "\n".join(
        generated_placeholder_target_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject placeholder target plan"
        )

    generated_missing_reviewable_target_path = valid_text.replace(
        "Reviewable Visual Acceptance Target Path: C:\\Nexus USER\\FAM-007\\Review Aids\\AI_Diagnostics_Visual_Acceptance_Target.md.\n\n",
        "",
    )
    generated_missing_target_path_failures = _validate_visual_acceptance_enforcement_text(
        generated_missing_reviewable_target_path
    )
    if EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET not in "\n".join(
        generated_missing_target_path_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject target plan without reviewable path"
        )

    generated_bare_not_applicable_target = generated_missing_reviewable_target_path.replace(
        "Visual Acceptance Target Plan: Visual Acceptance Target is defined before Workstream from UIREF-001 through UIREF-004 and the accepted AI Dashboard / AI Control Center comparator set.",
        "Visual Acceptance Target Plan: Visual Acceptance Target Not Applicable.",
    )
    generated_bare_not_applicable_failures = _validate_visual_acceptance_enforcement_text(
        generated_bare_not_applicable_target
    )
    if EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET not in "\n".join(
        generated_bare_not_applicable_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject bare not-applicable target plan"
        )

    generated_uiref_only_target_path = valid_text.replace(
        "Reviewable Visual Acceptance Target Path: C:\\Nexus USER\\FAM-007\\Review Aids\\AI_Diagnostics_Visual_Acceptance_Target.md.",
        "Reviewable Visual Acceptance Target Path: Docs/ui_reference_catalog/UIREF-001_top_level_window_frame.md.",
    )
    generated_uiref_only_target_failures = _validate_visual_acceptance_enforcement_text(
        generated_uiref_only_target_path
    )
    if EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET not in "\n".join(
        generated_uiref_only_target_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject UIREF-only visual target path"
        )

    generated_prose_only_target_path = valid_text.replace(
        "Reviewable Visual Acceptance Target Path: C:\\Nexus USER\\FAM-007\\Review Aids\\AI_Diagnostics_Visual_Acceptance_Target.md.",
        "Reviewable Visual Acceptance Target Path: visual acceptance target ready for review.",
    )
    generated_prose_only_target_failures = _validate_visual_acceptance_enforcement_text(
        generated_prose_only_target_path
    )
    if EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET not in "\n".join(
        generated_prose_only_target_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject prose-only visual target path"
        )

    generated_bare_slash_target_path = valid_text.replace(
        "Reviewable Visual Acceptance Target Path: C:\\Nexus USER\\FAM-007\\Review Aids\\AI_Diagnostics_Visual_Acceptance_Target.md.",
        "Reviewable Visual Acceptance Target Path: review/ready target.",
    )
    generated_bare_slash_target_failures = _validate_visual_acceptance_enforcement_text(
        generated_bare_slash_target_path
    )
    if EXPECTED_VISUAL_ACCEPTANCE_TARGET_FAILURE_SNIPPET not in "\n".join(
        generated_bare_slash_target_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject bare-slash visual target path"
        )

    generated_placeholder_implementation_match_claim = valid_text.replace(
        "Implementation Match Proof Plan: Workstream must trace code regions to the rendered child window and produce focused screenshots or ordered-frame proof for every listed element group before Pre-Live.",
        "Implementation Match Proof Plan: TBD pending review.",
    )
    generated_placeholder_match_failures = _validate_visual_acceptance_enforcement_text(
        generated_placeholder_implementation_match_claim
    )
    if EXPECTED_IMPLEMENTATION_MATCH_PROOF_FAILURE_SNIPPET not in "\n".join(
        generated_placeholder_match_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject placeholder implementation match proof plan"
        )

    generated_vague_implementation_match_claim = valid_text.replace(
        "Implementation Match Proof Plan: Workstream must trace code regions to the rendered child window and produce focused screenshots or ordered-frame proof for every listed element group before Pre-Live.",
        "Implementation Match Proof Plan: Workstream will confirm implementation matches before Pre-Live.",
    )
    generated_vague_match_failures = _validate_visual_acceptance_enforcement_text(
        generated_vague_implementation_match_claim
    )
    if EXPECTED_IMPLEMENTATION_MATCH_PROOF_FAILURE_SNIPPET not in "\n".join(
        generated_vague_match_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject vague implementation match proof plan"
        )

    generated_placeholder_template_source_claim = valid_text.replace(
        "Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Implementation Template Instantiated - the branch claims an AI Control Center template. Template source path: TBD.",
    ).replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | Yes | No | Yes - UIREF-001 and UIREF-002 | No | No | No gap claimed | Approved template source path and element-by-element proof before Workstream and Pre-Live. |",
    )
    generated_placeholder_template_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_placeholder_template_source_claim
        )
    )
    if EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_placeholder_template_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject placeholder template source path"
        )

    generated_placeholder_primitive_source_claim = valid_text.replace(
        "Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Shared Primitive Consumed - the branch claims a shared primitive. Primitive source path: none.",
    ).replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | No | Yes | Yes - UIREF-001 and UIREF-002 | No | No | No gap claimed | Approved primitive source path and element-by-element proof before Workstream and Pre-Live. |",
    )
    generated_placeholder_primitive_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_placeholder_primitive_source_claim
        )
    )
    if EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_placeholder_primitive_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject placeholder primitive source path"
        )

    generated_dual_authority_claim = valid_text.replace(
        "Implementation Authority Classification: Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Implementation Authority Classification: Reference-Derived Implementation and One-Off Implementation.",
    )
    generated_dual_authority_failures = _validate_visual_acceptance_enforcement_text(
        generated_dual_authority_claim
    )
    if EXPECTED_IMPLEMENTATION_AUTHORITY_FAILURE_SNIPPET not in "\n".join(
        generated_dual_authority_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject dual authority classification"
        )

    generated_template_source_no_contract_claim = valid_text.replace(
        "Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Implementation Template Instantiated - the branch claims an AI Control Center template. Template source path: Docs/ui_reference_catalog/UIREF-001_top_level_window_frame.md.",
    ).replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | Yes | No | Yes - UIREF-001 and UIREF-002 | No | No | No gap claimed | Approved template source path and element-by-element proof before Workstream and Pre-Live. |",
    )
    generated_template_no_contract_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_template_source_no_contract_claim
        )
    )
    if EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_template_no_contract_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject template source without consumer contract"
        )

    generated_template_uiref_source_claim = valid_text.replace(
        "Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Implementation Template Instantiated - the branch claims an AI Control Center template. Template source path: Docs/ui_reference_catalog/UIREF-001_top_level_window_frame.md. Template consumer contract: instantiate the claimed template and prove all non-editable visual invariants.",
    ).replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | Yes | No | Yes - UIREF-001 and UIREF-002 | No | No | No gap claimed | Approved template source path and element-by-element proof before Workstream and Pre-Live. |",
    )
    generated_template_uiref_source_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_template_uiref_source_claim
        )
    )
    if EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_template_uiref_source_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject UIREF path as template source"
        )

    generated_primitive_source_no_contract_claim = valid_text.replace(
        "Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Shared Primitive Consumed - the branch claims a shared primitive. Primitive source path: Docs/ui_reference_catalog/UIREF-002_window_control_cluster.md.",
    ).replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | No | Yes | Yes - UIREF-001 and UIREF-002 | No | No | No gap claimed | Approved primitive source path and element-by-element proof before Workstream and Pre-Live. |",
    )
    generated_primitive_no_contract_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_primitive_source_no_contract_claim
        )
    )
    if EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_primitive_no_contract_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject primitive source without consumer contract"
        )

    generated_table_only_template_claim = valid_text.replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | Yes | No | Yes - UIREF-001 and UIREF-002 | No | No | No gap claimed | Approved template source path and element-by-element proof before Workstream and Pre-Live. |",
    )
    generated_table_only_template_failures = _validate_visual_acceptance_enforcement_text(
        generated_table_only_template_claim
    )
    if EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_table_only_template_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject table-only template claim"
        )

    generated_table_only_primitive_claim = valid_text.replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | No | Yes | Yes - UIREF-001 and UIREF-002 | No | No | No gap claimed | Approved primitive source path and element-by-element proof before Workstream and Pre-Live. |",
    )
    generated_table_only_primitive_failures = _validate_visual_acceptance_enforcement_text(
        generated_table_only_primitive_claim
    )
    if EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET not in "\n".join(
        generated_table_only_primitive_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject table-only primitive claim"
        )

    generated_negative_authority_cells = valid_text.replace(
        "| AI diagnostics child window | No | No | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
        "| AI diagnostics child window | No approved template exists | No approved shared primitive exists | Yes - UIREF-001 and UIREF-002 | Yes - AI Dashboard and AI Control Center comparator synthesis | No | No gap; reference-derived proof required | Element-by-element visual family proof before Workstream and Pre-Live. |",
    )
    generated_negative_authority_failures = "\n".join(
        _validate_visual_acceptance_enforcement_text(
            generated_negative_authority_cells
        )
    )
    if (
        EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET
        in generated_negative_authority_failures
        or EXPECTED_SHARED_PRIMITIVE_CLAIM_FAILURE_SNIPPET
        in generated_negative_authority_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture falsely rejected negative template/shared primitive authority cells"
        )

    generated_negative_template_reference = valid_text.replace(
        "Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Reference-Derived Implementation - the AI Control Center template is not approved or consumed for this surface class.",
    )
    generated_negative_template_reference_failures = "\n".join(
        _validate_visual_acceptance_enforcement_text(
            generated_negative_template_reference
        )
    )
    if EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET in generated_negative_template_reference_failures:
        failures.append(
            "Generated Visual Acceptance fixture falsely rejected negative AI Control Center template reference"
        )

    generated_negated_but_used_template_reference = valid_text.replace(
        "Reference-Derived Implementation - no approved template or shared primitive exists for this surface class.",
        "Reference-Derived Implementation - the AI Control Center template is not approved but is used for this surface class.",
    )
    generated_negated_but_used_template_failures = "\n".join(
        _validate_visual_acceptance_enforcement_text(
            generated_negated_but_used_template_reference
        )
    )
    if EXPECTED_TEMPLATE_CLAIM_FAILURE_SNIPPET not in generated_negated_but_used_template_failures:
        failures.append(
            "Generated Visual Acceptance fixture did not reject negated-but-used AI Control Center template reference"
        )

    generated_packet_reviewability_means_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet reviewability means product acceptance.",
    )
    generated_reviewability_means_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_packet_reviewability_means_acceptance
        )
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_reviewability_means_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject packet reviewability means product acceptance"
        )

    generated_packet_reviewability_is_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet reviewability is product acceptance.",
    )
    generated_reviewability_is_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_packet_reviewability_is_acceptance
        )
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_reviewability_is_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject packet reviewability is product acceptance"
        )

    generated_packet_reviewability_proves_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet reviewability proves product acceptance.",
    )
    generated_reviewability_proves_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_packet_reviewability_proves_acceptance
        )
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_reviewability_proves_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject packet reviewability proves product acceptance"
        )

    generated_packet_reviewability_user_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet reviewability means USER acceptance.",
    )
    generated_reviewability_user_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_packet_reviewability_user_acceptance
        )
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_reviewability_user_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject packet reviewability means USER acceptance"
        )

    generated_packet_reviewability_bare_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet reviewability means acceptance.",
    )
    generated_reviewability_bare_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_packet_reviewability_bare_acceptance
        )
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_reviewability_bare_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject packet reviewability means acceptance"
        )

    generated_reviewable_packet_product_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: A reviewable packet means product acceptance.",
    )
    generated_reviewable_packet_product_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_reviewable_packet_product_acceptance
        )
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_reviewable_packet_product_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject reviewable packet means product acceptance"
        )

    generated_reviewable_status_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Reviewable status proves acceptance.",
    )
    generated_reviewable_status_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_reviewable_status_acceptance
        )
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_reviewable_status_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject reviewable status proves acceptance"
        )

    generated_reviewable_status_scoped_accepted = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet Reviewability means product accepted; reviewable status means visual accepted.",
    )
    generated_reviewable_status_scoped_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_reviewable_status_scoped_accepted
        )
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_reviewable_status_scoped_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject product/visual accepted reviewability claims"
        )

    generated_packet_status_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet status means accepted.",
    )
    generated_packet_status_failures = _validate_visual_acceptance_enforcement_text(
        generated_packet_status_acceptance
    )
    if EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_packet_status_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject packet status means accepted"
        )

    generated_packet_reviewability_pending_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet reviewability means product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
    )
    generated_reviewability_pending_failures = "\n".join(
        _validate_visual_acceptance_enforcement_text(
            generated_packet_reviewability_pending_acceptance
        )
    )
    if (
        EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET
        in generated_reviewability_pending_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture falsely rejected pending packet reviewability wording"
        )

    generated_packet_reviewability_punctuated_pending = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: Packet reviewability means product acceptance, which remains pending until USER visual acceptance.",
    )
    generated_punctuated_reviewability_failures = "\n".join(
        _validate_visual_acceptance_enforcement_text(
            generated_packet_reviewability_punctuated_pending
        )
    )
    if (
        EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET
        in generated_punctuated_reviewability_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture falsely rejected punctuated pending packet reviewability wording"
        )

    generated_reviewable_packet_pending_acceptance = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: A reviewable packet means product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
    )
    generated_reviewable_packet_pending_failures = "\n".join(
        _validate_visual_acceptance_enforcement_text(
            generated_reviewable_packet_pending_acceptance
        )
    )
    if (
        EXPECTED_PACKET_REVIEWABILITY_PRODUCT_ACCEPTANCE_FAILURE_SNIPPET
        in generated_reviewable_packet_pending_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture falsely rejected pending reviewable-packet wording"
        )

    generated_helper_green_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: helper green proves visual acceptance for this review packet.",
    )
    generated_helper_green_failures = _validate_visual_acceptance_enforcement_text(
        generated_helper_green_claim
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_helper_green_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject helper-green visual acceptance claim"
        )

    generated_helper_green_means_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: helper green means visual acceptance for this review packet.",
    )
    generated_helper_green_means_failures = _validate_visual_acceptance_enforcement_text(
        generated_helper_green_means_claim
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_helper_green_means_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject helper-green means visual acceptance claim"
        )

    generated_helper_green_bare_acceptance_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: helper green means acceptance for this review packet.",
    )
    generated_helper_green_bare_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_helper_green_bare_acceptance_claim
        )
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_helper_green_bare_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject helper-green means acceptance claim"
        )

    generated_helper_green_therefore_acceptance_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: helper green therefore accepted for this review packet.",
    )
    generated_helper_green_therefore_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_helper_green_therefore_acceptance_claim
        )
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_helper_green_therefore_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject helper-green therefore accepted claim"
        )

    generated_helper_green_user_acceptance_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: helper green means USER acceptance for this review packet.",
    )
    generated_helper_green_user_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_helper_green_user_acceptance_claim
        )
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_helper_green_user_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject helper-green means USER acceptance claim"
        )

    generated_helper_pass_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: helper pass proves visual acceptance for this review packet.",
    )
    generated_helper_pass_failures = _validate_visual_acceptance_enforcement_text(
        generated_helper_pass_claim
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_helper_pass_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject helper-pass visual acceptance claim"
        )

    generated_helper_output_result_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: helper output green means visual acceptance; helper result pass proves product acceptance.",
    )
    generated_helper_output_result_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_helper_output_result_claim
        )
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_helper_output_result_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject helper-output/result acceptance claims"
        )

    generated_validator_passed_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: validator passed means visual acceptance for this review packet.",
    )
    generated_validator_passed_failures = _validate_visual_acceptance_enforcement_text(
        generated_validator_passed_claim
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_validator_passed_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject validator-passed visual acceptance claim"
        )

    generated_validator_passed_accepted_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: validator passed means accepted for this review packet.",
    )
    generated_validator_passed_accepted_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_validator_passed_accepted_claim
        )
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_validator_passed_accepted_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject validator-passed accepted claim"
        )

    generated_validation_pass_acceptance_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: validation pass proves acceptance for this review packet.",
    )
    generated_validation_pass_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_validation_pass_acceptance_claim
        )
    )
    if EXPECTED_HELPER_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_validation_pass_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject validation pass acceptance claim"
        )

    generated_screenshot_equals_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: screenshot path equals visual acceptance for this review packet.",
    )
    generated_screenshot_equals_failures = _validate_visual_acceptance_enforcement_text(
        generated_screenshot_equals_claim
    )
    if EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_screenshot_equals_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject screenshot-path equals visual acceptance claim"
        )

    generated_screenshot_user_acceptance_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: screenshot path means USER acceptance for this review packet.",
    )
    generated_screenshot_user_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_screenshot_user_acceptance_claim
        )
    )
    if EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_screenshot_user_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject screenshot-path USER acceptance claim"
        )

    generated_screenshot_exists_acceptance_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: screenshot exists proves visual acceptance; screenshot exists means visual acceptance.",
    )
    generated_screenshot_exists_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_screenshot_exists_acceptance_claim
        )
    )
    if EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_screenshot_exists_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject screenshot-exists visual acceptance claims"
        )

    generated_screenshot_plural_acceptance_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: screenshots prove visual acceptance; screenshot paths mean USER acceptance.",
    )
    generated_screenshot_plural_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_screenshot_plural_acceptance_claim
        )
    )
    if EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_screenshot_plural_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject plural screenshot visual acceptance claims"
        )

    generated_screenshot_product_acceptance_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: screenshot path means product acceptance for this review packet.",
    )
    generated_screenshot_product_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_screenshot_product_acceptance_claim
        )
    )
    if EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_screenshot_product_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject screenshot-path product acceptance claim"
        )

    generated_screenshot_proves_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: screenshot proves visual acceptance for this review packet.",
    )
    generated_screenshot_proves_failures = _validate_visual_acceptance_enforcement_text(
        generated_screenshot_proves_claim
    )
    if EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_screenshot_proves_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject bare screenshot proves visual acceptance claim"
        )

    generated_screenshot_existence_claim = valid_text.replace(
        "Packet Reviewability vs Product Acceptance: The packet can become reviewable only after the tables are complete; product acceptance remains pending until USER visual acceptance, USER waiver, or approved defer/repair route.",
        "Packet Reviewability vs Product Acceptance: screenshot existence proves visual acceptance for this review packet.",
    )
    generated_screenshot_existence_failures = _validate_visual_acceptance_enforcement_text(
        generated_screenshot_existence_claim
    )
    if EXPECTED_SCREENSHOT_VISUAL_ACCEPTANCE_FAILURE_SNIPPET not in "\n".join(
        generated_screenshot_existence_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject screenshot-existence proves visual acceptance claim"
        )

    generated_css_similarity_claim = valid_text.replace(
        "Visual Family Relation Proof: Row-by-row comparison maps title stack, frame, window control cluster, card borders, typography, spacing, glow, states, and scroll behavior against UIREF-001 through UIREF-004.",
        "Visual Family Relation Proof: CSS similarity proves visual family for title stack, frame, window controls, cards, spacing, glow, states, and scroll behavior.",
    )
    generated_css_similarity_failures = _validate_visual_acceptance_enforcement_text(
        generated_css_similarity_claim
    )
    if EXPECTED_CSS_VISUAL_FAMILY_FAILURE_SNIPPET not in "\n".join(
        generated_css_similarity_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject CSS similarity as visual-family proof"
        )

    generated_css_similarity_is_claim = valid_text.replace(
        "Visual Family Relation Proof: Row-by-row comparison maps title stack, frame, window control cluster, card borders, typography, spacing, glow, states, and scroll behavior against UIREF-001 through UIREF-004.",
        "Visual Family Relation Proof: CSS similarity is visual family for title stack, frame, window controls, cards, spacing, glow, states, and scroll behavior.",
    )
    generated_css_similarity_is_failures = _validate_visual_acceptance_enforcement_text(
        generated_css_similarity_is_claim
    )
    if EXPECTED_CSS_VISUAL_FAMILY_FAILURE_SNIPPET not in "\n".join(
        generated_css_similarity_is_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject CSS similarity is visual-family claim"
        )

    generated_uiref_citation_acceptance_claim = (
        valid_text
        + "\nAccepted Reference Set / Comparative Synthesis: UIREF citation proves visual acceptance.\n"
    )
    generated_uiref_citation_acceptance_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_uiref_citation_acceptance_claim
        )
    )
    if EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET not in "\n".join(
        generated_uiref_citation_acceptance_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject UIREF citation as visual acceptance"
        )

    generated_reference_citation_product_claim = (
        valid_text
        + "\nAccepted Reference Set / Comparative Synthesis: reference citation means product acceptance.\n"
    )
    generated_reference_citation_product_failures = (
        _validate_visual_acceptance_enforcement_text(
            generated_reference_citation_product_claim
        )
    )
    if EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET not in "\n".join(
        generated_reference_citation_product_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject reference citation as product acceptance"
        )

    generated_uiref_citation_pending_claim = valid_text.replace(
        "Accepted Reference Set / Comparative Synthesis: UIREF-001, UIREF-002, UIREF-003, UIREF-004, AI Dashboard, and AI Control Center are compared element-by-element for invariant chrome, controls, rows, cards, spacing, typography, glow, and visible state behavior.",
        "Accepted Reference Set / Comparative Synthesis: UIREF-001, UIREF-002, UIREF-003, UIREF-004, AI Dashboard, and AI Control Center are compared element-by-element for invariant chrome, controls, rows, cards, spacing, typography, glow, and visible state behavior. UIREF citation means visual proof remains pending until comparison.",
    )
    generated_uiref_citation_pending_failures = "\n".join(
        _validate_visual_acceptance_enforcement_text(
            generated_uiref_citation_pending_claim
        )
    )
    if (
        EXPECTED_ACCEPTED_REFERENCE_NOT_COMPARED_FAILURE_SNIPPET
        in generated_uiref_citation_pending_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture falsely rejected pending UIREF citation wording"
        )

    generated_implementation_backfill_claim = valid_text.replace(
        "Visual Acceptance Target Plan: Visual Acceptance Target is defined before Workstream from UIREF-001 through UIREF-004 and the accepted AI Dashboard / AI Control Center comparator set.",
        "Visual Acceptance Target Plan: Visual target created after implementation and used as implementation-first visual target backfill.",
    )
    generated_backfill_failures = _validate_visual_acceptance_enforcement_text(
        generated_implementation_backfill_claim
    )
    if EXPECTED_IMPLEMENTATION_FIRST_TARGET_FAILURE_SNIPPET not in "\n".join(
        generated_backfill_failures
    ):
        failures.append(
            "Generated Visual Acceptance fixture did not reject implementation-first visual target backfill"
        )

    return failures


def _validate_family_feature_vision_scaffolding_source_truth() -> list[str]:
    failures: list[str] = []
    ffv_dir = ROOT / "Docs" / "family_feature_visions"
    expected_files = {
        "README.md": (
            "Family Feature Vision",
            "durable feature-category",
            "Deferred Feature Carryforward",
            "not active branch state",
        ),
        "index.md": (
            "Family Feature Vision Index",
            "F<family>-FF<two digits>",
            "compact durable registry",
        ),
        "TEMPLATE.md": (
            "Family Feature Vision ID:",
            "Feature Category:",
            "Deferred Feature Carryforward:",
            "Active-State Wording Scan:",
        ),
    }
    if not ffv_dir.is_dir():
        return ["Missing generic Family Feature Vision scaffolding directory: Docs/family_feature_visions"]
    for file_name, markers in expected_files.items():
        path = ffv_dir / file_name
        if not path.is_file():
            failures.append(f"Missing generic Family Feature Vision scaffold file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(
                    f"{path.relative_to(ROOT)} missing Family Feature Vision scaffold marker {marker!r}"
                )
    return failures


def _iter_current_worktree_ffv_content_files() -> list[Path]:
    ffv_dir = ROOT / "Docs" / "family_feature_visions"
    if not ffv_dir.is_dir():
        return []
    scaffold_names = {"index.md", "readme.md", "template.md"}
    return sorted(
        path
        for path in ffv_dir.glob("*.md")
        if path.name.casefold() not in scaffold_names
    )


def _validate_current_worktree_family_feature_vision_files() -> list[str]:
    """Apply the binding FFV content standard to admitted repo FFV files."""

    failures: list[str] = []
    for path in _iter_current_worktree_ffv_content_files():
        text = path.read_text(encoding="utf-8")
        for failure in _validate_family_feature_vision_text(text):
            failures.append(f"{path.relative_to(ROOT)}: {failure}")
    return failures


def _validate_current_worktree_ffv_dependency_records() -> list[str]:
    """Scan tracked FFVs in the current worktree for loose cross-FAM dependencies."""

    failures: list[str] = []

    trigger_terms = (
        "dependency",
        "carry-in",
        "platform contract",
        "affected fam",
        "installer",
        "packaging",
        "shortcut",
        "update",
        "patch",
    )
    for path in _iter_current_worktree_ffv_content_files():
        text = path.read_text(encoding="utf-8")
        owning_fam = _owning_fam_from_ffv(path, text)
        mentioned_fams = sorted(set(re.findall(r"\bFAM-\d{3}\b", text)))
        other_fams = [fam for fam in mentioned_fams if fam != owning_fam]
        normalized_text = governance._normalized_planning_value(text)
        if not other_fams:
            continue
        if not any(term in normalized_text for term in trigger_terms):
            continue
        if "Cross-FAM Dependency" not in text and "Dependency Scope Class:" not in text:
            failures.append(
                f"{path.relative_to(ROOT)}: Cross-FAM dependency content mentions "
                f"{', '.join(other_fams)} but lacks a Cross-FAM Dependency record"
            )
            continue
        record_failures = _validate_cross_fam_dependency_packet_text(text)
        if record_failures:
            failures.append(
                f"{path.relative_to(ROOT)}: Cross-FAM dependency record invalid: "
                + "; ".join(record_failures[:5])
            )
    return failures


def _validate_implementation_bearing_source_truth() -> list[str]:
    failures, require = _collect_failures()
    source_truth_markers = {
        ROOT / "Docs" / "phase_governance.md": (
            "Implementation-Bearing Branch Standard",
            "Branch / Slice / SLC / Seam Terminology Model",
            "Selected Implementation Route:",
            "Real Feature Implementation Definition",
            "BR2 Blocker Packet Rule",
            "Slice Definition:",
            "SLC Classification:",
            "Seam Definition:",
            "Multi-Slice Branch Rule:",
            "Developer lane",
        ),
        ROOT / "Docs" / "branch_plans" / "README.md": (
            "Implementation-Bearing Route Requirement",
            "Real feature implementation",
            "Infrastructure / Lane Groundwork Blockers:",
            "Infrastructure / Setup Relationship:",
            "`SLC` is the current branch-planning alias",
            "Multi-slice branches are legal",
            "Developer lane",
        ),
        ROOT / "Docs" / "validation_helper_registry.md": (
            "Implementation-Bearing Branch Planning Validation Invariant",
            "planning-only lane/setup carrier",
            "invalid SLC/Slice/Seam terminology ambiguity packet",
            "valid multi-slice implementation carrier",
            "boundary-control labels",
            "Developer lane",
        ),
    }
    for path, markers in source_truth_markers.items():
        if not path.is_file():
            failures.append(f"Missing implementation-bearing source truth owner: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            require(
                marker in text,
                f"Implementation-bearing source truth missing {marker!r} in {path}",
            )
    return failures


def _validate_slice_slc_seam_model_text(text: str) -> list[str]:
    return external_state.validate_slice_slc_seam_model_text(text)


def _validate_br2_route_blocker_packet_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    required_markers = (
        "BR2 Route Resolution Status:",
        "Infrastructure / Lane Groundwork Blockers:",
        "Required Before This Route Can Proceed:",
        "Concrete Feature Routes Available Now:",
        "Deferrable Groundwork:",
        "Non-Deferrable Groundwork:",
        "Codex Recommendation:",
        "Exact USER Decision Needed:",
        "Route Disposition:",
    )
    for marker in required_markers:
        require(marker in text, f"BR2 route blocker packet missing {marker}")
    normalized = governance._normalized_planning_value(text)
    routes_available = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Concrete Feature Routes Available Now:")
    )
    exact_decision = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Exact USER Decision Needed:")
    )
    required_before = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Required Before This Route Can Proceed:")
    )
    deferrable_groundwork = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Deferrable Groundwork:")
    )
    codex_recommendation = governance._normalized_planning_value(
        governance._extract_marker_value(text, "Codex Recommendation:")
    )
    deferral_decision_text = "\n".join(
        (
            required_before,
            deferrable_groundwork,
            codex_recommendation,
            exact_decision,
        )
    )
    require(
        "hold" in normalized
        or "retarget" in normalized
        or "rename" in normalized
        or "no active branch" in normalized,
        "BR2 blocker packet must stop for hold, retarget, rename, or No Active Branch",
    )
    explicit_no_available_routes = routes_available in {
        "none",
        "none.",
        "none;",
        "none; continue planning anyway.",
        "no concrete feature routes available now",
        "no concrete feature routes available now.",
    }
    if explicit_no_available_routes:
        require(
            "no active branch" in normalized
            and "no remaining implementation-bearing route" in normalized
            and "continue planning" not in routes_available
            and "continue planning" not in exact_decision,
            (
                "BR2 blocker packet with no concrete available route must stop on "
                "No Active Branch or non-deferrable groundwork"
            ),
        )
    else:
        proof_only_route_terms = (
            "proof",
            "proof packet",
            "setup proof",
            "packet proof",
            "readiness proof",
            "readiness matrix",
            "decision path",
            "boundary controls",
            "validation plan",
            "planning candidate",
        )
        route_behavior_terms = (
            "control",
            "enforcement",
            "artifact exclusion",
            "disabled-state",
            "install-intent gate",
            "consent-state enforcement",
            "fail-closed",
            "reject",
            "block",
            "gate",
            "implements",
            "implement",
        )
        require(
            any(
                term in routes_available
                for term in (
                    "security/trust-boundary enforcement control",
                    "trust-boundary enforcement control",
                    "provider/runtime consent",
                    "consent shell",
                    "capability-pack install-intent gate",
                    "memory/cache consent-state enforcement",
                    "agent",
                    "runtime",
                    "source-truth",
                    "source truth",
                    "validator",
                    "helper",
                    "feature route",
                )
            ),
            "BR2 blocker packet must name at least one concrete feature route available now",
        )
        require(
            not any(term in routes_available for term in proof_only_route_terms)
            or any(term in routes_available for term in route_behavior_terms),
            (
                "BR2 blocker packet concrete routes cannot be proof/readiness "
                "labels only: name a control, behavior, gate, enforcement, or "
                "state transition that can be implemented"
            ),
        )
    require(
        "approve prerequisite groundwork" in normalized
        or "approve the prerequisite groundwork" in normalized,
        "BR2 blocker packet must offer prerequisite-groundwork approval path",
    )
    require(
        "defer" in deferral_decision_text
        and (
            "concrete feature route" in deferral_decision_text
            or "concrete worktree-focused feature route" in deferral_decision_text
            or "implementation-bearing route" in deferral_decision_text
        ),
        "BR2 blocker packet must offer deferral to a concrete feature route",
    )
    require(
        "non-deferrable" in normalized and "no remaining implementation-bearing route" in normalized,
        "BR2 blocker packet must state when continued deferral stops being legal",
    )
    require(
        "Dev lane" not in text,
        "Use Developer lane, not Dev lane, in current branch-planning text",
    )
    return failures


def _validate_active_external_branch_plan_posture(
    state_root: Path | None = None,
) -> list[str]:
    failures: list[str] = []
    state_root = DEFAULT_EXTERNAL_STATE_ROOT if state_root is None else state_root
    active_state = state_root / "central" / "active_branch_authority_state.md"
    if not active_state.is_file():
        return failures

    active_text = active_state.read_text(encoding="utf-8")
    plan_value = governance._extract_marker_value(
        active_text, "Branch Runtime Engineering Plan:"
    ).strip("` ")
    branch_state_value = governance._extract_marker_value(
        active_text, "Branch State:"
    ).strip("` ")
    plan_path = Path(plan_value) if plan_value else None
    branch_state_path = Path(branch_state_value) if branch_state_value else None
    branch_state_text = (
        branch_state_path.read_text(encoding="utf-8")
        if branch_state_path and branch_state_path.is_file()
        else ""
    )
    active_routes_to_bp1 = "BP1 USER Branch Vision Review" in {
        governance._extract_marker_value(active_text, "Next Gate:").strip("` "),
        governance._extract_marker_value(active_text, "Next Legal Phase:").strip("` "),
        governance._extract_marker_value(branch_state_text, "Next Legal Phase:").strip(
            "` "
        ),
    }
    if not active_routes_to_bp1:
        active_routes_to_bp1 = (
            "Next Gate: `BP1 USER Branch Vision Review`" in active_text
            or "Next Legal Phase: `BP1 USER Branch Vision Review`" in active_text
            or "Next Legal Phase: `BP1 USER Branch Vision Review`"
            in branch_state_text
        )
    if not active_routes_to_bp1:
        active_routes_to_bp1 = (
            "Next Gate: BP1 USER Branch Vision Review" in active_text
            or "Next Legal Phase: BP1 USER Branch Vision Review" in active_text
            or "Next Legal Phase: BP1 USER Branch Vision Review" in branch_state_text
        )
    if not active_routes_to_bp1:
        return failures
    if not plan_path or not plan_path.is_file():
        return [
            "External active branch state routes to BP1 without an existing active branch plan"
        ]

    plan_text = plan_path.read_text(encoding="utf-8")
    required_route_markers = (
        "Selected Implementation Route:",
        "Implementation Route Class:",
        "Concrete Deliverable:",
        "Implementation Output:",
        "Infrastructure / Setup Relationship:",
        "USER Action Gate:",
        "Route Disposition:",
        "Retarget / Rename Recommendation:",
    )
    has_route_markers = all(marker in plan_text for marker in required_route_markers)
    route_resolution_status = external_state.markdown_field_value(
        plan_text, "BR2 Route Resolution Status"
    )
    route_disposition = governance._normalized_planning_value(
        external_state.markdown_field_value(plan_text, "Route Disposition") or ""
    )
    has_hold_or_retarget = bool(route_resolution_status) or any(
        disposition in route_disposition
        for disposition in ("hold", "retarget", "rename")
    )
    if has_hold_or_retarget:
        failures.append(
            "External active branch state routes to BP1 while active branch plan is still HOLD/RETARGET route resolution"
        )
    if not has_route_markers:
        failures.append(
            "External active branch state routes to BP1 without implementation-bearing route fields in active branch plan"
        )
    else:
        failures.extend(_validate_implementation_bearing_route_text(plan_text))
    return failures


def _validate_merge_stable_projection_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    stale_lines = governance._stale_pre_pr_lines(text)
    require(
        not stale_lines,
        (
            "Merge-Stable Source Truth Projection Missing: "
            + "; ".join(line for _, line in stale_lines)
        ),
    )
    return failures


def _validate_merge_stable_projection_helpers() -> list[str]:
    failures, require = _collect_failures()
    broad_allowlist_failures = governance._stale_pre_pr_lines(
        "Status: PR creation pending after blocker scan."
    )
    require(
        bool(broad_allowlist_failures),
        "Merge-stable stale pre-PR detector must not allow blocker/scan wording",
    )
    adjacent_paths = governance._collect_merge_stable_detail_record_paths(
        (
            "Assignment Status: Historical merged-unreleased after PR #201.\n"
            "Branch Authority Record: "
            "`Docs/branch_records/feature_example_merge_stable_fixture.md`\n"
        )
    )
    require(
        "Docs/branch_records/feature_example_merge_stable_fixture.md" in adjacent_paths,
        (
            "Merge-stable detail record collection must capture canonical record paths "
            "from adjacent merge-status blocks"
        ),
    )

    standing_path = governance.STANDING_GOVERNANCE_INTAKE_RECORD.as_posix()
    active_standing_record = (
        "## Branch Identity\n"
        "Branch: `feature/release-readiness-source-truth-intake`\n\n"
        "## Post-Merge State\n"
        "No Active Branch\n"
    )
    invalid_merge_stable_record = (
        "## Branch Identity\n"
        "Branch: `feature/example-merged-branch`\n\n"
        "## Current Phase\n"
        "Phase: `PR Readiness`\n\n"
        "## Phase Status\n"
        "`Active Branch`\n\n"
        "## Post-Merge State\n"
        "No Active Branch\n"
    )
    invalid_failures: list[str] = []
    governance._run_merge_target_authority_projection_gate(
        lambda condition, message: invalid_failures.append(message) if not condition else None,
        active_branch_record_paths={standing_path},
        active_branch_record_path=standing_path,
        active_branch_record_text=active_standing_record,
        merge_stable_branch_record_path=(
            "Docs/branch_records/feature_example_merged_branch.md"
        ),
        merge_stable_branch_record_text=invalid_merge_stable_record,
    )
    require(
        any("Historical Traceability" in failure for failure in invalid_failures),
        "Standing Governance intake must not bypass malformed merge-stable phase validation",
    )
    require(
        any("still declares `Active Branch`" in failure for failure in invalid_failures),
        "Standing Governance intake must not bypass malformed merge-stable phase-status validation",
    )

    valid_merge_stable_record = invalid_merge_stable_record.replace(
        "Phase: `PR Readiness`", "Phase: `Historical Traceability`"
    ).replace("`Active Branch`", "Historical merged-unreleased projection")
    valid_failures: list[str] = []
    governance._run_merge_target_authority_projection_gate(
        lambda condition, message: valid_failures.append(message) if not condition else None,
        active_branch_record_paths={standing_path},
        active_branch_record_path=standing_path,
        active_branch_record_text=active_standing_record,
        merge_stable_branch_record_path=(
            "Docs/branch_records/feature_example_merged_branch.md"
        ),
        merge_stable_branch_record_text=valid_merge_stable_record,
    )
    require(
        not valid_failures,
        "Valid historical merge-stable projection unexpectedly failed with standing intake active: "
        + "; ".join(valid_failures[:3]),
    )
    return failures


def _validate_pr_review_churn_matrix_fixture() -> list[str]:
    failures, require = _collect_failures()
    relative_matrix = PR_REVIEW_CHURN_MATRIX_FIXTURE.relative_to(ROOT)
    require(
        PR_REVIEW_CHURN_MATRIX_FIXTURE.exists(),
        f"{relative_matrix}: PR review churn matrix fixture is missing",
    )
    if not PR_REVIEW_CHURN_MATRIX_FIXTURE.exists():
        return failures

    try:
        matrix = json.loads(PR_REVIEW_CHURN_MATRIX_FIXTURE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{relative_matrix}: invalid JSON: {exc}"]

    require(
        matrix.get("schema") == "nexus-pr-review-churn-matrix-v1",
        f"{relative_matrix}: unexpected schema",
    )
    budget = matrix.get("review_churn_budget")
    require(
        isinstance(budget, dict),
        f"{relative_matrix}: review_churn_budget must be present",
    )
    if isinstance(budget, dict):
        total_budget = budget.get("max_connector_comments_before_root_cause_receipt")
        same_family_budget = budget.get(
            "max_same_family_comments_before_root_cause_receipt"
        )
        require(
            isinstance(total_budget, int) and total_budget > 0,
            (
                f"{relative_matrix}: max_connector_comments_before_root_cause_receipt "
                "must be a positive integer"
            ),
        )
        require(
            isinstance(same_family_budget, int) and same_family_budget > 0,
            (
                f"{relative_matrix}: max_same_family_comments_before_root_cause_receipt "
                "must be a positive integer"
            ),
        )
        receipts = budget.get("root_cause_receipts")
        require(
            isinstance(receipts, list) and bool(receipts),
            f"{relative_matrix}: root_cause_receipts must be a non-empty list",
        )
        if isinstance(receipts, list):
            for receipt in receipts:
                if not isinstance(receipt, dict):
                    failures.append(
                        f"{relative_matrix}: root-cause receipt must be an object"
                    )
                    continue
                pr_number = receipt.get("pr")
                connector_comments = receipt.get("connector_comments")
                require(
                    isinstance(pr_number, int) and pr_number > 0,
                    f"{relative_matrix}: root-cause receipt pr must be a positive integer",
                )
                require(
                    _pr_review_churn_receipt_exceeds_budget(
                        connector_comments,
                        total_budget,
                        receipt.get("observed_family_counts"),
                        same_family_budget,
                    ),
                    (
                        f"{relative_matrix}: root-cause receipt must exceed the "
                        "configured total or same-family budget"
                    ),
                )
                require(
                    receipt.get("pr_readiness_stage_1_failure") is True,
                    (
                        f"{relative_matrix}: high-churn receipt must mark "
                        "pr_readiness_stage_1_failure true"
                    ),
                )
                family_counts = receipt.get("observed_family_counts")
                require(
                    isinstance(family_counts, dict) and bool(family_counts),
                    (
                        f"{relative_matrix}: root-cause receipt must include "
                        "observed_family_counts"
                    ),
                )
                for field in (
                    "root_cause",
                    "prevention_summary",
                    "receipt_file",
                    "receipt_marker",
                ):
                    value = receipt.get(field)
                    require(
                        isinstance(value, str) and bool(value.strip()),
                        f"{relative_matrix}: root-cause receipt missing {field}",
                    )
                changes = receipt.get("preventive_changes")
                require(
                    isinstance(changes, list)
                    and bool(changes)
                    and all(isinstance(item, str) and item.strip() for item in changes),
                    (
                        f"{relative_matrix}: root-cause receipt preventive_changes "
                        "must be a non-empty string list"
                    ),
                )
                receipt_file = receipt.get("receipt_file")
                receipt_marker = receipt.get("receipt_marker")
                if isinstance(receipt_file, str) and receipt_file.strip():
                    receipt_path = ROOT / receipt_file.replace("\\", "/")
                    require(
                        receipt_path.exists(),
                        (
                            f"{relative_matrix}: root-cause receipt file is missing: "
                            f"{receipt_file}"
                        ),
                    )
                    if (
                        receipt_path.exists()
                        and isinstance(receipt_marker, str)
                        and receipt_marker.strip()
                    ):
                        require(
                            receipt_marker
                            in receipt_path.read_text(encoding="utf-8"),
                            (
                                f"{relative_matrix}: root-cause receipt marker "
                                f"not found in {receipt_file}"
                            ),
                        )
        if isinstance(total_budget, int) and isinstance(same_family_budget, int):
            require(
                _pr_review_churn_receipt_exceeds_budget(
                    total_budget + 1,
                    total_budget,
                    {
                        "generated-total-only-family-a": same_family_budget,
                        "generated-total-only-family-b": same_family_budget,
                    },
                    same_family_budget,
                ),
                f"{relative_matrix}: generated total-only churn receipt variant must be legal",
            )
            require(
                _pr_review_churn_receipt_exceeds_budget(
                    total_budget,
                    total_budget,
                    {"generated-same-family-only": same_family_budget + 1},
                    same_family_budget,
                ),
                f"{relative_matrix}: generated same-family-only churn receipt variant must be legal",
            )
            require(
                not _pr_review_churn_receipt_exceeds_budget(
                    total_budget,
                    total_budget,
                    {"generated-within-budget": same_family_budget},
                    same_family_budget,
                ),
                f"{relative_matrix}: generated within-budget churn receipt variant must stay illegal",
            )
    families = matrix.get("families")
    require(
        isinstance(families, list) and bool(families),
        f"{relative_matrix}: families must be a non-empty list",
    )
    if not isinstance(families, list):
        return failures

    required_families = {
        "rar-status-green-parser",
        "rar-phase-advancement-parser",
        "rar-issue-candidate-disposition-parser",
        "rar-user-packet-proof-parser",
        "rar-code-to-visual-reference-parser",
        "rar-table-row-parser",
        "rar-path-suffix-parser",
        "rar-short-marker-parser",
        "repo-live-state-boundary-parser",
        "pr-readiness-review-risk-parser",
        "visual-acceptance-proof-chain-parser",
        "pr2-comment-family-classifier",
        "pr2-thread-pagination-and-approval-latch",
    }
    observed_families = {
        family.get("family_id") for family in families if isinstance(family, dict)
    }
    require(
        required_families.issubset(observed_families),
        (
            f"{relative_matrix}: missing required PR review churn families "
            f"{sorted(required_families - observed_families)}"
        ),
    )
    require(
        len(observed_families) == len(families),
        f"{relative_matrix}: duplicate or missing family_id values",
    )

    pre_pr_firewall = matrix.get("pre_pr_firewall")
    require(
        isinstance(pre_pr_firewall, dict),
        f"{relative_matrix}: pre_pr_firewall must be present",
    )
    if isinstance(pre_pr_firewall, dict):
        purpose = pre_pr_firewall.get("purpose")
        require(
            isinstance(purpose, str)
            and "before PR Readiness Stage 2" in purpose
            and "connector" in purpose.casefold(),
            (
                f"{relative_matrix}: pre_pr_firewall purpose must name the "
                "pre-PR/connector replay boundary"
            ),
        )
        validation_commands = pre_pr_firewall.get("validation_commands")
        require(
            isinstance(validation_commands, list) and bool(validation_commands),
            f"{relative_matrix}: pre_pr_firewall validation_commands must be non-empty",
        )
        if isinstance(validation_commands, list):
            for command_entry in validation_commands:
                if not isinstance(command_entry, dict):
                    failures.append(
                        f"{relative_matrix}: pre_pr_firewall validation command must be an object"
                    )
                    continue
                command_name = command_entry.get("name")
                command = command_entry.get("command")
                covers = command_entry.get("covers_families")
                require(
                    isinstance(command_name, str) and bool(command_name.strip()),
                    f"{relative_matrix}: pre_pr_firewall validation command missing name",
                )
                require(
                    isinstance(command, list)
                    and bool(command)
                    and all(isinstance(item, str) and item.strip() for item in command),
                    f"{relative_matrix}: pre_pr_firewall validation command must be a string list",
                )
                if (
                    isinstance(command, list)
                    and any(
                        isinstance(item, str)
                        and item.replace("\\", "/").casefold().endswith(".py")
                        for item in command
                    )
                ):
                    require(
                        bool(command)
                        and isinstance(command[0], str)
                        and command[0].casefold()
                        in {"{python}", "{python_executable}"},
                        (
                            f"{relative_matrix}: pre_pr_firewall Python validation "
                            "commands must use the portable {python} token"
                        ),
                    )
                require(
                    isinstance(covers, list)
                    and bool(covers)
                    and all(family_id in observed_families for family_id in covers),
                    (
                        f"{relative_matrix}: pre_pr_firewall validation command "
                        "covers_families must reference known families"
                    ),
                )
        corpus = pre_pr_firewall.get("connector_corpus_replay")
        require(
            isinstance(corpus, list) and bool(corpus),
            f"{relative_matrix}: pre_pr_firewall connector_corpus_replay must be non-empty",
        )
        if isinstance(corpus, list):
            for row in corpus:
                if not isinstance(row, dict):
                    failures.append(
                        f"{relative_matrix}: pre_pr_firewall corpus row must be an object"
                    )
                    continue
                require(
                    row.get("family_id") in observed_families,
                    (
                        f"{relative_matrix}: pre_pr_firewall corpus row must "
                        "reference a known family"
                    ),
                )
                comment = row.get("comment")
                require(
                    isinstance(comment, str) and bool(comment.strip()),
                    f"{relative_matrix}: pre_pr_firewall corpus row missing comment text",
                )
        unknown_guardrails = pre_pr_firewall.get("unknown_comment_guardrails")
        require(
            isinstance(unknown_guardrails, list)
            and bool(unknown_guardrails)
            and all(
                isinstance(comment, str) and comment.strip()
                for comment in unknown_guardrails
            ),
            (
                f"{relative_matrix}: pre_pr_firewall unknown_comment_guardrails "
                "must be a non-empty string list"
            ),
        )

    required_list_fields = (
        "representative_comment_patterns",
        "source_truth",
        "implementation",
        "fixture_coverage",
        "generated_mutation_coverage",
        "sibling_variant_replay",
    )
    for family in families:
        if not isinstance(family, dict):
            failures.append(f"{relative_matrix}: family entry must be an object")
            continue
        family_id = family.get("family_id", "<missing-family-id>")
        for field in required_list_fields:
            value = family.get(field)
            require(
                isinstance(value, list) and bool(value),
                f"{relative_matrix}: {family_id} {field} must be a non-empty list",
            )
            if not isinstance(value, list):
                continue
            require(
                all(isinstance(item, str) and item.strip() for item in value),
                f"{relative_matrix}: {family_id} {field} contains a blank value",
            )
        for field in ("source_truth", "implementation", "fixture_coverage"):
            for item in family.get(field, []):
                if not isinstance(item, str) or not item.strip():
                    continue
                item_path = ROOT / item.replace("\\", "/")
                require(
                    item_path.exists(),
                    f"{relative_matrix}: {family_id} references missing {field} path {item}",
                )

    changed_file_coverage = matrix.get("changed_file_coverage")
    require(
        isinstance(changed_file_coverage, dict) and bool(changed_file_coverage),
        f"{relative_matrix}: changed_file_coverage must be a non-empty object",
    )
    if isinstance(changed_file_coverage, dict):
        relative_matrix_path = relative_matrix.as_posix()
        for path, family_ids in changed_file_coverage.items():
            require(
                isinstance(path, str)
                and (
                    path.startswith("dev/")
                    or path.startswith("Docs/")
                    or path.startswith("docs/")
                ),
                f"{relative_matrix}: changed-file coverage key must be a gated repo path",
            )
            require(
                (ROOT / str(path)).exists(),
                f"{relative_matrix}: changed-file coverage path is missing: {path}",
            )
            require(
                isinstance(family_ids, list) and bool(family_ids),
                f"{relative_matrix}: {path} must map to one or more review families",
            )
            if not isinstance(family_ids, list):
                continue
            for family_id in family_ids:
                require(
                    family_id in observed_families,
                    f"{relative_matrix}: {path} references unknown review family {family_id}",
                )
                matching_family = next(
                    (
                        family
                        for family in families
                        if isinstance(family, dict)
                        and family.get("family_id") == family_id
                    ),
                    {},
                )
                require(
                    path == relative_matrix_path
                    or any(
                        path in matching_family.get(field, [])
                        for field in (
                            "source_truth",
                            "implementation",
                            "fixture_coverage",
                        )
                    ),
                    f"{relative_matrix}: {path} must also appear in source-truth, implementation, or fixture coverage for {family_id}",
                )

    return failures


def _runtime_overlap_ledger_text() -> str:
    return """# Runtime Overlap Fixture

## Branch Change Intent Ledger

### Changed Surface: main.py

Surface Class: runtime
Change Intent: preserve runtime launch behavior while reconciling an overlapping main entrypoint change.
Why This File Was Touched: the branch changed the runtime entrypoint for a governed behavior fix.
Owned Behavior / Fact Class: runtime launch behavior and validation entrypoint.
Canonical Owner / Source Owner: main.py.
Resolution Owner: Current Branch
Shared Surface: Yes.
Overlap Risk: Medium.
Expected Conflict Risk: Medium.
Semantic Merge Risk: Medium
Regression / Gating Impact: Low
Conflict Resolution Rule: compare incoming runtime intent against the branch ledger and stop for USER decision when behavior changes.
Rebaseline Handling: rerun runtime and governance validation before requesting mutation.
Validation Proof: validation required after repair: branch governance validation and compileall.
Fallback Evidence: fallback evidence may classify risk, but it is not a compatibility bypass.
USER Decision / Waiver: USER approval required before mutation.
Fold-Down Target: compact branch receipt when durable.
"""


def _validate_rebaseline_overlap_helper_matrix() -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(
        rebaseline._overall_overlap_gate_result([]) == "Not Applicable",
        "Rebaseline helper no-overlap matrix did not return Not Applicable",
    )
    require(
        governance._bot_review_comment_is_green_signal(
            "Codex Review: Didn't find any major issues. Chef's kiss."
        ),
        "Governance validator did not recognize Codex green review comment as a bot-review signal",
    )
    require(
        governance._bot_review_comment_is_green_signal(
            "Codex Review: Didn\u2019t find any major issues. Chef\u2019s kiss."
        ),
        "Governance validator did not normalize smart apostrophes in Codex green review comments",
    )
    require(
        not governance._bot_review_comment_is_green_signal(
            "Here are some automated review suggestions for this pull request."
        ),
        "Governance validator treated a Codex suggestion comment as a green bot-review signal",
    )
    require(
        not governance._bot_review_comment_is_green_signal(
            "Codex Review: looks good overall, but there is one major issue to fix."
        ),
        "Governance validator treated a contrastive Codex review comment as a green bot-review signal",
    )
    require(
        not governance._phase_status_bot_approval_proven(
            "Bot approval proof: `Comment addressed`"
        ),
        "Governance validator treated comment-addressed closeout as bot approval proof",
    )
    require(
        not governance._phase_status_bot_approval_proven(
            "Bot approval proof: `not required after same-head comment-addressed closeout`"
        ),
        "Governance validator treated historical no-later-thumbs-up wording as bot approval proof",
    )
    require(
        governance._phase_status_bot_approval_proven(
            "Bot approval proof: `Approved by Codex Connector bot thumbs-up`"
        ),
        "Governance validator did not accept an explicit Codex Connector thumbs-up approval proof",
    )
    require(
        governance._phase_status_bot_approval_proven(
            "Bot approval proof: `Comment addressed, then approved by later thumbs-up`"
        ),
        "Governance validator rejected explicit approval proof that mentioned repaired comments",
    )
    require(
        not governance._fallback_bot_approval_clears_comment_latch(
            phase_status_section="",
            bot_comment_count=1,
            bot_approval=True,
        ),
        "Governance validator let unordered fallback bot approval clear a prior bot comment",
    )
    require(
        governance._fallback_bot_approval_clears_comment_latch(
            phase_status_section=(
                "Bot approval proof: `Comment addressed, then approved by later thumbs-up`"
            ),
            bot_comment_count=1,
            bot_approval=True,
        ),
        "Governance validator rejected ordered later approval proof for fallback bot comments",
    )
    require(
        not governance._fallback_bot_approval_clears_comment_latch(
            phase_status_section="Bot approval proof: `Approved by Codex Connector bot thumbs-up`",
            bot_comment_count=1,
            bot_approval=True,
        ),
        "Governance validator treated an unordered approval marker as ordered fallback proof",
    )
    require(
        not governance._fallback_bot_approval_clears_comment_latch(
            phase_status_section=(
                "Bot approval proof: `Codex Connector thumbs-up before repair`"
            ),
            bot_comment_count=1,
            bot_approval=True,
        ),
        "Governance validator treated pre-repair approval wording as ordered fallback proof",
    )
    require(
        not governance._watcher_fallback_current_head_bot_approval_proven(
            "Bot approval proof: `Approved by Codex Connector bot thumbs-up`"
        ),
        "Governance validator let unordered watcher fallback approval prove current-head approval",
    )
    require(
        not governance._watcher_fallback_current_head_bot_approval_proven(
            "Bot approval proof: `Codex Connector thumbs-up before repair`"
        ),
        "Governance validator let pre-repair watcher fallback approval prove current-head approval",
    )
    require(
        governance._watcher_fallback_current_head_bot_approval_proven(
            "Bot approval proof: `Comment addressed, then approved by later thumbs-up after current head`"
        ),
        "Governance validator rejected ordered current-head watcher fallback approval proof",
    )
    for fallback_view in (
        governance._automation_closeout_repair_fallback_pr_view_for_branch,
        governance._pr101_closeout_canon_repair_fallback_pr_view_for_branch,
        governance._pr102_closeout_canon_repair_fallback_pr_view_for_branch,
        governance._pr103_closeout_canon_repair_fallback_pr_view_for_branch,
        governance._active_branch_watcher_fallback_pr_view_for_branch,
    ):
        source = inspect.getsource(fallback_view)
        require(
            'watcher_state.get("botApproval")' not in source,
            (
                "Governance validator fallback PR view still trusts raw watcher "
                f"botApproval in {fallback_view.__name__}"
            ),
        )
    require(
        rebaseline._overlap_intent_missing_status("PASS").startswith("No -"),
        "Rebaseline helper did not return non-blocking intent-missing status for PASS",
    )
    blocked_state, blocked_recommendation = rebaseline._apply_overlap_recommendation(
        "Blocked",
        "Worktree has local changes; do not baseline until the owner reviews or commits/stashes them.",
        "WARN",
    )
    require(
        blocked_state == "Blocked" and "Overlap warning also present" in blocked_recommendation,
        "Rebaseline helper downgraded a dirty-worktree Blocked recommendation when overlap WARN was present",
    )

    missing_runtime = rebaseline._assess_overlap_file("main.py", {})
    require(
        missing_runtime["per_file_result"] == "BLOCKED",
        "Rebaseline helper did not block high-risk runtime overlap with missing ledger",
    )

    runtime_entries = rebaseline._branch_change_intent_entries(_runtime_overlap_ledger_text())
    runtime_with_ledger = rebaseline._assess_overlap_file("main.py", runtime_entries)
    require(
        runtime_with_ledger["branch_intent_present"] == "YES"
        and runtime_with_ledger["per_file_result"] == "PASS",
        "Rebaseline helper did not PASS/evidence-present high-risk runtime overlap with a valid ledger",
    )

    source_truth_missing = rebaseline._assess_overlap_file("Docs/Main.md", {})
    require(
        rebaseline._surface_class("Docs/Main.md") == "governance/source-truth"
        and source_truth_missing["per_file_result"] == "BLOCKED",
        "Rebaseline helper did not classify Docs/Main.md as blocked source-truth overlap without ledger",
    )

    low_reference_missing = rebaseline._assess_overlap_file("Docs/incident_patterns.md", {})
    require(
        rebaseline._surface_class("Docs/incident_patterns.md") == "documentation/reference"
        and low_reference_missing["per_file_result"] == "WARN",
        "Rebaseline helper did not WARN on low-risk reference overlap without ledger",
    )

    valid_entries = rebaseline._branch_change_intent_entries(
        VALID_REBASELINE_OVERLAP_INTENT_FIXTURE.read_text(encoding="utf-8")
    )
    mismatch = rebaseline._assess_overlap_file("Docs/Main.md", valid_entries)
    require(
        mismatch["per_file_result"] == "BLOCKED",
        "Rebaseline helper did not block branch plan ledger path mismatch",
    )

    high_impact_entries = rebaseline._branch_change_intent_entries(
        INVALID_REBASELINE_OVERLAP_FIXTURE_HIGH_IMPACT_FIXTURE.read_text(encoding="utf-8")
    )
    high_impact = rebaseline._assess_overlap_file(
        "dev/fixtures/branch_readiness_planning/valid_user_feedback_disposition.md",
        high_impact_entries,
    )
    require(
        high_impact["per_file_result"] == "BLOCKED",
        "Rebaseline helper did not block fixture/test overlap with high regression impact",
    )

    low_impact_entries = rebaseline._branch_change_intent_entries(
        VALID_REBASELINE_OVERLAP_FIXTURE_LOW_IMPACT_FIXTURE.read_text(encoding="utf-8")
    )
    low_impact = rebaseline._assess_overlap_file(
        "dev/fixtures/branch_readiness_planning/reference_only_example.md",
        low_impact_entries,
    )
    require(
        low_impact["per_file_result"] == "PASS",
        "Rebaseline helper did not accept fixture/test overlap with low regression impact and valid ledger",
    )

    fam_role = rebaseline._worktree_role(WORKTREES_ROOT / "FAM-006")
    require(
        "FAM-006 implementation lane" not in fam_role
        and "runtime-active candidate" in fam_role,
        "Rebaseline helper still treats FAM-006 as a permanent lane instead of a generic runtime slot",
    )

    return failures


def _validate_compact_backlog_text(text: str) -> list[str]:
    failures, require = _collect_failures()
    governance._validate_branch_runtime_backlog_compactness(
        require,
        "<backlog-compactness-fixture>",
        text,
    )
    return failures


def _validate_missing_plan_pointer_text() -> list[str]:
    failures, require = _collect_failures()
    governance._validate_branch_runtime_engineering_plan_pointer(
        require,
        "<missing-plan-pointer-fixture>",
        (
            "Branch Runtime Engineering Plan: Accepted\n"
            "Branch Runtime Engineering Plan Path: "
            "Docs/branch_plans/missing_runtime_plan_fixture.md\n"
            "Engineering Plan Status: Accepted\n"
        ),
        branch_class="implementation",
        current_phase="Workstream",
    )
    return failures


def _validate_user_review_bundle_identity_guard() -> list[str]:
    source_path = "Docs/Main.md"
    copied_path = f"{review_bundle.SOURCE_TRUTH_CONTEXT_DIR_NAME}/Main.md"
    current_branch = review_bundle._git_output("rev-parse", "--abbrev-ref", "HEAD")
    current_head = review_bundle._git_output("rev-parse", "HEAD")
    current_origin_main = review_bundle._git_output("rev-parse", "origin/main")
    source_text = review_bundle._git_file_text(current_head, source_path) or ""
    common = "Decision Path Summary: workstream implementation approval\nUSER Decision: approve workstream implementation\n"
    packet_files = {
        "START_HERE.md": (
            "# Review\n\n"
            "USER Decision This Packet Supports: approve workstream implementation\n\n"
            "Primary USER Review File: `USER Review/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md`\n\n"
            "## Files\n\n"
            "| Source path | Copied path |\n"
            "| --- | --- |\n"
            f"| `{source_path}` | `{copied_path}` |\n"
        ),
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/USER_REVIEW_FOLDER_AND_FILE_DIGEST.md": common,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/GOVERNANCE_REQUIRED_FILES_SCAN.md": common,
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md": common,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/BRANCH_VISION_VALIDATION_CHECKLIST.md": common,
        copied_path: source_text,
    }

    valid_result = review_bundle._validate_workstream_entry_packet_decision_path(
        packet_files,
        expected_branch=current_branch,
        expected_head=current_head,
        expected_origin_main=current_origin_main,
        enforce_identity=True,
    )
    failures: list[str] = []
    if valid_result.failures:
        failures.append(
            "Valid USER review bundle identity fixture unexpectedly failed: "
            + "; ".join(valid_result.failures[:5])
        )

    wrong_result = review_bundle._validate_workstream_entry_packet_decision_path(
        packet_files,
        expected_branch="wrong-branch",
        expected_head="0" * 40,
        expected_origin_main="1" * 40,
        enforce_identity=True,
    )
    wrong_failures = "\n".join(wrong_result.failures)
    for expected in (
        "expected branch",
        "expected HEAD",
        "expected origin/main",
    ):
        if expected not in wrong_failures:
            failures.append(
                "Invalid USER review bundle identity fixture did not reject "
                f"{expected}"
            )

    false_green_packet_files = dict(packet_files)
    false_green_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nVisual Acceptance: screenshot exists therefore accepted.\n"
    )
    if "screenshot-as-visual-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(false_green_packet_files)
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject screenshot existence as visual acceptance"
        )
    screenshot_accepted_packet_files = dict(packet_files)
    screenshot_accepted_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nVisual Acceptance: screenshot path equals accepted.\n"
    )
    if "screenshot-as-visual-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            screenshot_accepted_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject screenshot path as accepted"
        )
    screenshot_user_acceptance_packet_files = dict(packet_files)
    screenshot_user_acceptance_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nVisual Acceptance: screenshot path means USER acceptance.\n"
        + "Visual Acceptance: screenshot is USER accepted.\n"
        + "Visual Acceptance: screenshot exists proves visual acceptance.\n"
        + "Visual Acceptance: screenshot exists means visual acceptance.\n"
        + "Visual Acceptance: screenshots prove visual acceptance.\n"
        + "Visual Acceptance: screenshot paths mean USER acceptance.\n"
    )
    if "screenshot-as-visual-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            screenshot_user_acceptance_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject screenshot path as USER acceptance"
        )
    helper_acceptance_packet_files = dict(packet_files)
    helper_acceptance_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nVisual Acceptance: helper green means acceptance.\n"
        + "Visual Acceptance: helper green means USER acceptance.\n"
        + "Visual Acceptance: helper output green means visual acceptance.\n"
        + "Visual Acceptance: helper result pass proves product acceptance.\n"
        + "Visual Acceptance: validator passed means accepted.\n"
        + "Visual Acceptance: helper green therefore accepted.\n"
        + "Visual Acceptance: validator passed therefore accepted.\n"
    )
    if "helper-green-as-visual-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            helper_acceptance_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject helper or validator green as acceptance"
        )
    uiref_citation_acceptance_packet_files = dict(packet_files)
    uiref_citation_acceptance_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nVisual Acceptance: UIREF citation proves visual acceptance.\n"
    )
    if "uiref-citation-as-visual-proof" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            uiref_citation_acceptance_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject UIREF citation as visual acceptance"
        )
    reference_citation_acceptance_packet_files = dict(packet_files)
    reference_citation_acceptance_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nVisual Acceptance: reference citation means product acceptance.\n"
    )
    if "uiref-citation-as-visual-proof" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            reference_citation_acceptance_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject reference citation as product acceptance"
        )
    uiref_citation_pending_packet_files = dict(packet_files)
    uiref_citation_pending_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nVisual Acceptance: UIREF citation means visual proof remains pending until comparison.\n"
    )
    if "uiref-citation-as-visual-proof" in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            uiref_citation_pending_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture falsely rejected pending UIREF citation wording"
        )
    unsafe_reviewability_packet_files = dict(packet_files)
    unsafe_reviewability_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nPacket Reviewability means product acceptance.\n"
        + "Packet Reviewability means product accepted.\n"
        + "Reviewable status means visual accepted.\n"
    )
    if "packet-reviewability-as-product-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            unsafe_reviewability_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject packet reviewability as product acceptance"
        )
    pending_reviewability_packet_files = dict(packet_files)
    pending_reviewability_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nPacket Reviewability means product acceptance, which remains pending until USER acceptance or waiver.\n"
    )
    if "packet-reviewability-as-product-acceptance" in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            pending_reviewability_packet_files
        )
    ):
        failures.append(
            "Valid USER review bundle fixture falsely rejected punctuated pending packet reviewability wording"
        )
    unsafe_user_acceptance_packet_files = dict(packet_files)
    unsafe_user_acceptance_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nPacket Reviewability means USER acceptance.\n"
        + "A reviewable packet means USER accepted.\n"
    )
    if "packet-reviewability-as-product-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            unsafe_user_acceptance_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject packet reviewability as USER acceptance"
        )
    unsafe_status_acceptance_packet_files = dict(packet_files)
    unsafe_status_acceptance_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nReviewable status proves acceptance.\n"
        + "Packet status means accepted.\n"
    )
    if "packet-reviewability-as-product-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            unsafe_status_acceptance_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject reviewable or packet status as acceptance"
        )
    unsafe_packet_validation_packet_files = dict(packet_files)
    unsafe_packet_validation_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nPacket validation means USER accepted.\n"
    )
    if "packet-validation-as-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            unsafe_packet_validation_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject packet validation as USER accepted"
        )
    unsafe_validation_pass_packet_files = dict(packet_files)
    unsafe_validation_pass_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nValidation pass proves acceptance.\n"
        + "Validation passed means USER accepted.\n"
    )
    if "packet-validation-as-acceptance" not in "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            unsafe_validation_pass_packet_files
        )
    ):
        failures.append(
            "Invalid USER review bundle fixture did not reject validation pass as acceptance"
        )
    safe_reviewability_packet_files = dict(packet_files)
    safe_reviewability_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nPacket Reviewability means product acceptance remains pending until USER acceptance or waiver.\n"
    )
    safe_false_green_failures = "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            safe_reviewability_packet_files
        )
    )
    if "packet-reviewability-as-product-acceptance" in safe_false_green_failures:
        failures.append(
            "Valid USER review bundle fixture falsely rejected pending product acceptance wording"
        )
    safe_user_acceptance_packet_files = dict(packet_files)
    safe_user_acceptance_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nPacket Reviewability means USER acceptance remains pending until USER acceptance or waiver.\n"
    )
    safe_user_acceptance_failures = "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            safe_user_acceptance_packet_files
        )
    )
    if "packet-reviewability-as-product-acceptance" in safe_user_acceptance_failures:
        failures.append(
            "Valid USER review bundle fixture falsely rejected pending USER acceptance wording"
        )
    safe_packet_validation_packet_files = dict(packet_files)
    safe_packet_validation_packet_files[
        f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ] = (
        packet_files[
            f"{review_bundle.USER_REVIEW_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        ]
        + "\nPacket validation means USER acceptance remains pending until USER acceptance or waiver.\n"
    )
    safe_packet_validation_failures = "\n".join(
        review_bundle._active_review_aid_false_green_failures(
            safe_packet_validation_packet_files
        )
    )
    if "packet-validation-as-acceptance" in safe_packet_validation_failures:
        failures.append(
            "Valid USER review bundle fixture falsely rejected pending packet validation wording"
        )
    return failures


def _validate_workstream_entry_packet_existing_bp1_substance_guard() -> list[str]:
    source_path = "Docs/Main.md"
    copied_path = f"{review_bundle.SOURCE_TRUTH_CONTEXT_DIR_NAME}/Main.md"
    current_branch = review_bundle._git_output("rev-parse", "--abbrev-ref", "HEAD")
    current_head = review_bundle._git_output("rev-parse", "HEAD")
    current_origin_main = review_bundle._git_output("rev-parse", "origin/main")
    source_text = review_bundle._git_file_text(current_head, source_path) or ""
    common = (
        "# Existing Packet Fixture\n\n"
        "USER Decision This Packet Supports: workstream entry final decision review\n"
        "Decision Path Summary: workstream entry final decision review\n"
        "USER Decision: Workstream Entry final decision review; implementation remains "
        "blocked pending separate USER approval.\n"
    )
    packet_files = {
        "START_HERE.md": (
            "# Review\n\n"
            "USER Decision This Packet Supports: workstream entry final decision review\n\n"
            "## Files\n\n"
            "| Source path | Copied path |\n"
            "| --- | --- |\n"
            f"| `{source_path}` | `{copied_path}` |\n"
        ),
        f"{review_bundle.USER_REVIEW_DIR_NAME}/{review_bundle.USER_BRANCH_VISION_REVIEW_FILE}": (
            INVALID_BP1_TEMPLATE_SHELL_FIXTURE.read_text(encoding="utf-8")
        ),
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/USER_REVIEW_FOLDER_AND_FILE_DIGEST.md": common,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/GOVERNANCE_REQUIRED_FILES_SCAN.md": common,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md": common,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/BRANCH_VISION_VALIDATION_CHECKLIST.md": common,
        copied_path: source_text,
    }

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        packet_dir = Path(temp_dir)
        for relative_path, text in packet_files.items():
            path = packet_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

        result = review_bundle.validate_workstream_entry_packet_folder(
            packet_dir,
            expected_branch=current_branch,
            expected_head=current_head,
            expected_origin_main=current_origin_main,
        )

    if EXPECTED_BP1_TEMPLATE_SHELL_FAILURE_SNIPPET not in "\n".join(result.failures):
        failures.append(
            "Existing Workstream Entry packet folder validation did not reject "
            "template-shell BP1 review content"
        )
    return failures


def _validate_user_review_bundle_export_zip_identity_guard() -> list[str]:
    source_path = "Docs/Main.md"
    copied_path = f"{review_bundle.SOURCE_TRUTH_CONTEXT_DIR_NAME}/Main.md"
    current_branch = review_bundle._git_output("rev-parse", "--abbrev-ref", "HEAD")
    current_head = review_bundle._git_output("rev-parse", "HEAD")
    current_origin_main = review_bundle._git_output("rev-parse", "origin/main")
    source_text = review_bundle._git_file_text(current_head, source_path) or ""
    common = (
        "Decision Path Summary: workstream implementation approval\n"
        "USER Decision: approve workstream implementation\n"
    )
    plan_headings = (
        "Contract Status",
        "Packet Reviewability State",
        "USER Gate State",
        "USER Response Proof",
        "USER Response Digested",
        "Acceptance / Waiver / Revision / Rejection Receipt",
        "Contract Version / Revision",
        "Plain-English Branch Summary",
        "What Will I Actually See, And Where Will I See It?",
        "End-State Vision",
        "Visual / Functional Walkthrough",
        "Surface Map",
        "Implementation Options",
        "Recommended Direction",
        "Why This Fits The Nexus Vision",
        "USER Plan Review Decision",
        "USER Decisions Needed",
        "USER Response",
        "Codex Response Digest",
        "Implementation Constraints Created By USER Response",
        "USER Rejected / Deferred Ideas",
        "Vision Delta / Source-Truth Impact",
        "Contract Change Log",
        "Current Branch Scope",
        "Future-Gated Scope",
        "Implementation Staging Notes",
        "Workstream Entry Result",
        "Contract Completion Checklist",
        "Exact USER Decision Supported",
    )
    vision_review_text = (
        "# Fixture USER Branch Vision Review\n\n"
        "USER Branch Vision Review: BP1\n\n"
        "## Review Status\nAccepted by USER for this fixture identity guard.\n\n"
        "## Contract Status\nComplete - fixture USER acceptance is recorded for implementation-ready validation.\n\n"
        "## Packet Reviewability State\nReviewable\n\n"
        "## USER Gate State\nUSER Accepted\n\n"
        "## Contract Revision\nv2 - substantive fixture packet.\n\n"
        "## Project Vision Context\n"
        "This fixture branch supports Nexus by requiring a readable USER vision review before engineering planning. "
        "It protects local-first, inspectable planning and prevents validators from treating a marker-only packet as product direction.\n\n"
        "## Family Vision Context\n"
        "The fixture family context requires branch-specific outcomes, boundaries, and USER decisions before BP2. "
        "Family direction remains the durable owner when the response changes reusable behavior.\n\n"
        "## Feature Vision Context\n"
        "The feature context is a governance review packet that must explain what the branch is trying to prove, "
        "which review surfaces matter, and which implementation behavior remains future-gated.\n\n"
        "## Branch Goal\n"
        "Create a substantive BP1 branch vision that USER can accept, revise, reject, or waive before Codex creates a BP2 engineering plan from it.\n\n"
        "## End-State Vision\n"
        "USER has a concrete accepted or revised branch vision, and later BP2/BP3 proof can trace engineering seams back to that accepted direction.\n\n"
        "## What Will I Actually See, And Where Will I See It?\n"
        "USER sees a decision-focused BP1 review in the local USER hub, with START_HERE used only to navigate supporting source context.\n\n"
        "## How It Will Function\n"
        "BP1 establishes product or governance direction, BP2 converts that accepted direction into implementation planning, and BP3 verifies orchestration before implementation approval.\n\n"
        "## User Experience Flow\n"
        "USER reads START_HERE, reviews the BP1 branch vision, chooses an option or revision, answers design questions, and waits for Codex to digest the response.\n\n"
        "## Surface Map\n"
        "Review surface is USER_BRANCH_VISION_REVIEW.md; context surface is START_HERE; decision surface is USER Response plus Codex Digest; proof surface is later BP2/BP3 traceability.\n\n"
        "## Product Options / Design Paths\n"
        "Option A accepts the fixture vision as scoped and lets BP2 begin from a clear branch-specific outcome, with the tradeoff of one deliberate review pause. Option B revises review surfaces, experience flow, or branch boundaries before BP2 to reduce implementation risk. Option C waives or rejects BP1 and keeps implementation blocked or deferred until USER gives a safer direction.\n\n"
        "## Codex Recommendations\n"
        "Recommendation one keeps packet placement in the local USER hub, names BP1/BP2/BP3 behavior, explains tradeoffs around review time, and cites risk from shallow branch vision because marker-only packet validation can otherwise bypass USER intent. USER response: accepted for fixture. Recommendation two keeps copied files as context instead of the vision so USER can decide from applied branch-specific substance. USER response: accepted for fixture.\n\n"
        "## Why This Fits The Nexus Vision\n"
        "This keeps Nexus planning USER-controlled and inspectable because Codex must explain the branch outcome before engineering seams become the default direction.\n\n"
        "## USER Design Questions\n"
        "What exact fixture outcome should USER inspect before BP2 turns this into engineering seams? Which review surface, experience flow, or branch boundary must remain future-gated if this BP1 review is revised?\n\n"
        "## USER Response\nFixture USER accepted the branch vision for zip identity validation.\n\n"
        "## Codex Digest\nFixture Codex digest records BP1 accepted for this implementation-ready packet identity guard.\n\n"
        "## USER Response Proof\nAccepted by fixture USER.\n\n"
        "## USER Response Digested\nYes - fixture acceptance was digested.\n\n"
        "## Accepted Branch Vision\nFixture accepted Branch Vision requires substantive review packets before implementation-ready validation can pass.\n\n"
        "## Family-Vision Versus Branch-Only Vision Impact\nBranch-only unless USER response creates a reusable family standard.\n\n"
        "## Must-Have Behavior\nBP1 remains a USER gate before BP2.\n\n"
        "## Future-Gated Decisions And Regression-Risk Controls\nRegression-risk control: packet validation is reviewability evidence, not USER acceptance.\n\n"
        "## Deferred And Future-Gated Ideas\nImplementation remains future-gated.\n\n"
        "## Vision Question Queue\nPending USER review.\n\n"
        "## Design Assumption Ledger\nUSER Branch Vision acceptance is required unless explicitly waived.\n\n"
        "## Acceptance / Revision / Rejection / Waiver Decision\nAccepted by fixture USER.\n"
    )
    packet_files = {
        "START_HERE.md": (
            "# Review\n\n"
            "Review Purpose: Fixture packet.\n"
            "USER Decision This Packet Supports: approve workstream implementation\n"
            "Bundle File Count: 8\n"
            "Expected File Count: 1\n"
            "Copied File Count: 1\n"
            "Extra Bundle File Count: 6\n\n"
            "| Source path | Copied path |\n"
            "| --- | --- |\n"
            f"| `{source_path}` | `{copied_path}` |\n"
        ),
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/{review_bundle.USER_BRANCH_VISION_REVIEW_FILE}": vision_review_text,
        f"{review_bundle.USER_REVIEW_DIR_NAME}/{review_bundle.USER_BRANCH_PLAN_REVIEW_FILE}": "\n".join(
            f"## {heading}\nComplete.\n" for heading in plan_headings
        ).replace(
            "## Packet Reviewability State\nComplete.\n",
            "## Packet Reviewability State\nReviewable\n",
        ).replace(
            "## USER Gate State\nComplete.\n",
            "## USER Gate State\nUSER Accepted\n",
        ).replace(
            "## Exact USER Decision Supported\nComplete.\n",
            "## Exact USER Decision Supported\nApprove bounded workstream implementation.\n",
        ),
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/USER_REVIEW_FOLDER_AND_FILE_DIGEST.md": common,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/GOVERNANCE_REQUIRED_FILES_SCAN.md": common,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md": common,
        f"{review_bundle.REVIEW_AIDS_DIR_NAME}/BRANCH_VISION_VALIDATION_CHECKLIST.md": common,
        copied_path: source_text,
    }

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        export_zip = Path(temp_dir) / "Governance-20260601-120000.zip"
        with zipfile.ZipFile(export_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, text in packet_files.items():
                archive.writestr(name, text)

        try:
            review_bundle._validate_export_zip(
                export_zip,
                source_branch=current_branch,
                source_head=current_head,
                origin_main=current_origin_main,
                expected_label="Governance",
                expected_entries=set(packet_files),
            )
        except ValueError as exc:
            failures.append(
                "Valid USER review export zip identity fixture unexpectedly failed: "
                f"{exc}"
            )

        try:
            review_bundle._validate_export_zip(
                export_zip,
                source_branch="wrong-branch",
                source_head="0" * 40,
                origin_main="1" * 40,
                expected_label="Governance",
                expected_entries=set(packet_files),
            )
        except ValueError as exc:
            wrong_failures = str(exc)
        else:
            wrong_failures = ""
            failures.append("Invalid USER review export zip identity fixture unexpectedly passed")

        stable_zip = Path(temp_dir) / "Governance.zip"
        with zipfile.ZipFile(stable_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, text in packet_files.items():
                archive.writestr(name, text)
        try:
            review_bundle._validate_export_zip(
                stable_zip,
                source_branch=current_branch,
                source_head=current_head,
                origin_main=current_origin_main,
                expected_label="Governance",
                expected_entries=set(packet_files),
            )
        except ValueError as exc:
            stale_name_failures = str(exc)
        else:
            stale_name_failures = ""
            failures.append("Invalid stable-name USER review export zip unexpectedly passed")
        if "creation timestamp" not in stale_name_failures:
            failures.append(
                "Invalid stable-name USER review export zip did not reject missing timestamp"
            )
    for expected in (
        "expected branch",
        "expected HEAD",
        "expected origin/main",
    ):
        if expected not in wrong_failures:
            failures.append(
                "Invalid USER review export zip identity fixture did not reject "
                f"{expected}"
            )
    return failures


def _validate_user_review_bundle_export_zip_cleanup_guard() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        review_root = Path(temp_dir)
        legacy_zip = review_root / "FAM-007.zip"
        stale_timestamped_zip = review_root / "FAM-007-20260601-111111.zip"
        other_label_zip = review_root / "FAM-006-20260601-111111.zip"
        malformed_same_label_zip = review_root / "FAM-007-not-a-timestamp.zip"
        export_zip = review_root / "FAM-007-20260601-222222.zip"
        for path in (
            legacy_zip,
            stale_timestamped_zip,
            other_label_zip,
            malformed_same_label_zip,
        ):
            path.write_text("fixture", encoding="utf-8")

        review_bundle._remove_stale_same_label_export_zips(
            review_root,
            "FAM-007",
            export_zip,
        )

        if legacy_zip.exists():
            failures.append("USER review zip cleanup left legacy same-name FAM-007.zip")
        if stale_timestamped_zip.exists():
            failures.append(
                "USER review zip cleanup left previous same-label timestamped FAM-007 zip"
            )
        if not other_label_zip.exists():
            failures.append("USER review zip cleanup removed a different worktree-label zip")
        if not malformed_same_label_zip.exists():
            failures.append(
                "USER review zip cleanup removed a non-timestamped same-prefix file"
            )
    return failures


def _write_local_user_packet_fixture(packet_dir: Path) -> None:
    (packet_dir / review_bundle.USER_REVIEW_DIR_NAME).mkdir(parents=True, exist_ok=True)
    (packet_dir / review_bundle.REVIEW_AIDS_DIR_NAME).mkdir(parents=True, exist_ok=True)
    (packet_dir / review_bundle.SOURCE_TRUTH_CONTEXT_DIR_NAME).mkdir(parents=True, exist_ok=True)
    (packet_dir / "START_HERE.md").write_text(
        "# START HERE\n\n"
        "Review Purpose: fixture packet validation.\n"
        "Local USER Hub Folder: fixture local hub.\n"
        "Review Order: open USER Review/FIXTURE_REVIEW.md first.\n"
        "USER Decision This Packet Supports: fixture review only.\n"
        "Pending USER Decisions: none for fixture.\n"
        "## Source Truth File Map\n\n"
        "| Source Path | Copied Path |\n"
        "| `Docs/Main.md` | `Source Truth Context/Docs__Main.md` |\n\n"
        "Bundle File Count: 4\n"
        "Expected File Count: 1\n"
        "Copied File Count: 1\n"
        "Extra Bundle File Count: 2\n",
        encoding="utf-8",
    )
    (packet_dir / review_bundle.USER_REVIEW_DIR_NAME / "FIXTURE_REVIEW.md").write_text(
        "# Fixture Review\n\n"
        "## Current Gate\n\n"
        "This is the only primary USER review file for the current fixture gate.\n\n"
        "## Review Context\n\n"
        "The fixture models a meaningful local USER packet decision surface. It must "
        "contain enough plain-language content for the packet helper to distinguish "
        "a real review file from an empty placeholder, a copied file list, or a "
        "template shell. The fixture does not approve implementation, does not "
        "approve PR Readiness, does not approve merge, and does not treat packet "
        "validation as USER acceptance. It exists so validation can prove a current "
        "packet has one readable decision file, supporting aids, copied context, "
        "folder and ZIP parity, and no stale active gate language.\n\n"
        "## USER Decision\n\n"
        "For this fixture only, the expected decision is that the packet is "
        "reviewable as a validation model and no product gate is accepted by the "
        "helper result.\n",
        encoding="utf-8",
    )
    (packet_dir / review_bundle.REVIEW_AIDS_DIR_NAME / "FIXTURE_AID.md").write_text(
        "# Fixture Aid\n\nSupporting review aid.\n",
        encoding="utf-8",
    )
    (
        packet_dir
        / review_bundle.SOURCE_TRUTH_CONTEXT_DIR_NAME
        / "Docs__Main.md"
    ).write_text(
        (ROOT / "Docs" / "Main.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def _zip_local_user_packet_fixture(packet_dir: Path, export_zip: Path) -> None:
    with zipfile.ZipFile(export_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(packet_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(packet_dir).as_posix())


def _validate_local_user_packet_folder_zip_guard() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        review_root = Path(temp_dir)
        packet_dir = review_root / "Governance"
        export_zip = review_root / "Governance-20260617-111111.zip"
        _write_local_user_packet_fixture(packet_dir)
        _zip_local_user_packet_fixture(packet_dir, export_zip)

        live_origin_main = review_bundle._git_output("rev-parse", "origin/main")
        fixture_origin_main = (
            FIXTURE_ORIGIN_MAIN if live_origin_main == "UNKNOWN" else live_origin_main
        )
        original_git_output = review_bundle._git_output
        identity_kwargs = {
            "expected_branch": original_git_output("rev-parse", "--abbrev-ref", "HEAD"),
            "expected_head": original_git_output("rev-parse", "HEAD"),
            "expected_origin_main": fixture_origin_main,
        }

        def validate_packet(*args: object, **kwargs: object):
            kwargs.update(identity_kwargs)
            original = review_bundle._git_output
            if live_origin_main == "UNKNOWN":
                def fixture_git_output(*git_args: str) -> str:
                    if git_args == ("rev-parse", "origin/main"):
                        return fixture_origin_main
                    return original(*git_args)

                review_bundle._git_output = fixture_git_output
            try:
                return review_bundle.validate_local_user_packet(*args, **kwargs)
            finally:
                review_bundle._git_output = original

        result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if result.failures:
            failures.append(
                "Valid local USER packet folder/ZIP fixture unexpectedly failed: "
                + "; ".join(result.failures[:5])
            )

        bad_metadata_aid = packet_dir / review_bundle.REVIEW_AIDS_DIR_NAME / "BAD_METADATA_AID.md"
        bad_metadata_aid.write_text(
            "# Bad Metadata Aid\n\nSource HEAD: 0123456789012345678901234567890123456789\n",
            encoding="utf-8",
        )
        _zip_local_user_packet_fixture(packet_dir, export_zip)
        bad_metadata_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any(
            "BAD_METADATA_AID.md" in failure and "technical metadata" in failure
            for failure in bad_metadata_result.failures
        ):
            failures.append("Local USER packet validation did not reject technical metadata in Review Aids")
        bad_metadata_aid.unlink()
        _zip_local_user_packet_fixture(packet_dir, export_zip)

        bad_validation_aid = packet_dir / review_bundle.REVIEW_AIDS_DIR_NAME / "BAD_VALIDATION_STATUS_AID.md"
        bad_validation_aid.write_text(
            "# Bad Validation Status Aid\n\nValidation Summary: green-by-helper-output.\n",
            encoding="utf-8",
        )
        _zip_local_user_packet_fixture(packet_dir, export_zip)
        bad_validation_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any(
            "BAD_VALIDATION_STATUS_AID.md" in failure and "technical metadata" in failure
            for failure in bad_validation_result.failures
        ):
            failures.append("Local USER packet validation did not reject validation status in Review Aids")
        bad_validation_aid.unlink()
        _zip_local_user_packet_fixture(packet_dir, export_zip)

        changed_aid = packet_dir / review_bundle.REVIEW_AIDS_DIR_NAME / "FIXTURE_AID.md"
        changed_aid.write_text(
            "# Fixture Aid\n\nChanged after ZIP creation; same filename, stale ZIP content.\n",
            encoding="utf-8",
        )
        stale_content_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any("content hash mismatch" in failure for failure in stale_content_result.failures):
            failures.append("Local USER packet validation did not reject stale ZIP content with matching file names")
        changed_aid.write_text(
            "# Fixture Aid\n\nSupporting review aid.\n",
            encoding="utf-8",
        )
        _zip_local_user_packet_fixture(packet_dir, export_zip)

        copied_zip_dir = review_root / "Copied Zip Outside User Hub"
        copied_zip_dir.mkdir()
        copied_zip = copied_zip_dir / export_zip.name
        copied_zip.write_bytes(export_zip.read_bytes())
        copied_zip_result = validate_packet(
            packet_dir,
            export_zip=copied_zip,
            worktree_label="Governance",
        )
        if not any("must live beside the packet folder" in failure for failure in copied_zip_result.failures):
            failures.append("Local USER packet validation did not reject ZIP outside packet folder parent")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(export_zip, "a", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    f"{review_bundle.REVIEW_AIDS_DIR_NAME}/FIXTURE_AID.md",
                    "# Fixture Aid\n\nDuplicate ZIP member fixture.\n",
                )
        duplicate_zip_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any("duplicate ZIP entries" in failure for failure in duplicate_zip_result.failures):
            failures.append("Local USER packet validation did not reject duplicate ZIP member names")
        _zip_local_user_packet_fixture(packet_dir, export_zip)

        stale_zip = review_root / "Governance-20260617-101010.zip"
        stale_zip.write_text("stale fixture", encoding="utf-8")
        stale_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any("Stale same-label USER packet ZIP remains" in failure for failure in stale_result.failures):
            failures.append("Local USER packet validation did not reject stale same-label timestamped ZIP")
        stale_zip.unlink()

        stable_zip = review_root / "Governance.zip"
        stable_zip.write_text("legacy stable fixture", encoding="utf-8")
        stable_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any("Stable-name USER packet ZIP is not allowed" in failure for failure in stable_result.failures):
            failures.append("Local USER packet validation did not reject stable-name Governance.zip")
        stable_zip.unlink()

        embedded_zip = packet_dir / review_bundle.REVIEW_AIDS_DIR_NAME / "NESTED_PACKET.zip"
        embedded_zip.write_bytes(export_zip.read_bytes())
        _zip_local_user_packet_fixture(packet_dir, export_zip)
        embedded_zip_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any("must not embed ZIP artifacts" in failure for failure in embedded_zip_result.failures):
            failures.append("Local USER packet validation did not reject embedded packet ZIP artifacts")
        embedded_zip.unlink()

        extra_primary = packet_dir / review_bundle.USER_REVIEW_DIR_NAME / "SECOND_REVIEW.md"
        extra_primary.write_text("# Second Review\n\nInvalid extra primary file.\n", encoding="utf-8")
        _zip_local_user_packet_fixture(packet_dir, export_zip)
        multi_primary_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any("exactly one primary USER review file" in failure for failure in multi_primary_result.failures):
            failures.append("Local USER packet validation did not reject multiple primary USER review files")
        extra_primary.unlink()

        _zip_local_user_packet_fixture(packet_dir, export_zip)
        (packet_dir / review_bundle.REVIEW_AIDS_DIR_NAME / "ZIP_MISMATCH.md").write_text(
            "# ZIP Mismatch\n\nThis file was added after ZIP creation.\n",
            encoding="utf-8",
        )
        mismatch_result = validate_packet(
            packet_dir,
            export_zip=export_zip,
            worktree_label="Governance",
        )
        if not any("Folder/ZIP parity failed" in failure for failure in mismatch_result.failures):
            failures.append("Local USER packet validation did not reject folder/ZIP parity drift")
    return failures


def _validate_active_overlay_user_branch_plan_review_metadata_guard() -> list[str]:
    source_path = "Docs/branch_plans/feature_fam_006_active_overlay_recording_runtime_foundation.md"
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir)
        review_bundle._write_user_branch_plan_review(
            target=target,
            title="Active Overlay Recording Runtime Foundation",
            review_purpose="Fixture packet metadata guard.",
            source_branch="feature/fam-006-active-overlay-recording-runtime-foundation",
            source_head=review_bundle._git_output("rev-parse", "HEAD"),
            upstream="origin/feature/fam-006-active-overlay-recording-runtime-foundation",
            origin_main=review_bundle._git_output("rev-parse", "origin/main"),
            exact_user_decision="I approve PR Readiness Stage 1 analysis.",
            pending_user_decisions=["Runtime implementation remains pending USER approval."],
            copied=[(source_path, "feature_fam_006_active_overlay_recording_runtime_foundation.md")],
        )
        text = (target / review_bundle.USER_BRANCH_PLAN_REVIEW_FILE).read_text(encoding="utf-8")

    metadata_failures = review_bundle._user_facing_technical_metadata_failures(
        {review_bundle.USER_BRANCH_PLAN_REVIEW_FILE: text}
    )
    if metadata_failures:
        failures.append(
            "Active Overlay USER Branch Plan Review fixture unexpectedly emitted "
            "USER-facing technical metadata: "
            + "; ".join(metadata_failures[:5])
        )
    if "HEAD changes" in text:
        failures.append(
            "Active Overlay USER Branch Plan Review fixture still contains stale HEAD-change wording"
        )
    return failures


def _validate_fam007_workstream_approval_packet_metadata_guard() -> list[str]:
    source_path = (
        "Docs/branch_plans/"
        "feature_fam_007_breakpoint_2_dev_owner_skeleton_action_gate_readiness.md"
    )
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir)
        review_bundle._write_user_branch_plan_review(
            target=target,
            title="FAM-007 Breakpoint 2 Dev Owner Skeleton Action Gate Readiness",
            review_purpose="Fixture packet metadata guard.",
            source_branch=(
                "feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
            ),
            source_head=review_bundle._git_output("rev-parse", "HEAD"),
            upstream=(
                "origin/feature/fam-007-breakpoint-2-dev-owner-skeleton-action-gate-readiness"
            ),
            origin_main=review_bundle._git_output("rev-parse", "origin/main"),
            exact_user_decision="Approve bounded workstream implementation.",
            pending_user_decisions=[
                "Private/runtime/provider/model/cache/memory behavior remains pending USER approval."
            ],
            copied=[
                (
                    source_path,
                    "feature_fam_007_breakpoint_2_dev_owner_skeleton_action_gate_readiness.md",
                )
            ],
        )
        text = (target / review_bundle.USER_BRANCH_PLAN_REVIEW_FILE).read_text(encoding="utf-8")

    metadata_failures = review_bundle._user_facing_technical_metadata_failures(
        {review_bundle.USER_BRANCH_PLAN_REVIEW_FILE: text}
    )
    if metadata_failures:
        failures.append(
            "FAM-007 workstream approval USER Branch Plan Review fixture unexpectedly "
            "emitted USER-facing technical metadata: "
            + "; ".join(metadata_failures[:5])
        )
    if "validation summary" in text.casefold():
        failures.append(
            "FAM-007 workstream approval packet still emits forbidden validation-summary wording"
        )
    if "seam 1 only" in text.casefold() or "first bounded workstream seam only" in text.casefold():
        failures.append(
            "FAM-007 workstream approval packet must not treat the entry seam as terminal Workstream authority"
        )
    return failures


def _validate_fam007_bp3_packet_generation_guard() -> list[str]:
    failures: list[str] = []
    exact_decision = (
        "I approve BP3 Workstream Entry / Orchestration Validation for the "
        "FAM-007 Dev/Owner Skeleton Readiness packet review; Workstream "
        "implementation remains pending separate USER approval."
    )
    copied = [
        (
            "Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md",
            "feature_fam_007_dev_owner_skeleton_readiness.md",
        )
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir)
        review_bundle._write_workstream_entry_packet_digests(
            target=target,
            source_branch="feature/fam-007-dev-owner-skeleton-readiness",
            source_head="fixture-head",
            origin_main="fixture-origin-main",
            packet_folder=target,
            export_zip=target / "FAM-007-20260601-120000.zip",
            copied=copied,
            extra_bundle_files=["USER Review/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"],
            bundle_file_count=6,
            expected_count=len(copied),
            copied_count=len(copied),
            exact_user_decision=exact_decision,
            pending_user_decisions=["Workstream implementation remains pending USER approval."],
        )
        packet_files = {
            "START_HERE.md": (
                "USER Decision This Packet Supports: "
                f"{exact_decision}\n"
                "Decision Path Summary: bp3 orchestration review\n"
                "BP3 Packet Reviewability State: Reviewable\n"
                "BP3 USER Gate State: Pending USER Review\n"
            )
        }
        for path in target.glob("*.md"):
            packet_files[path.name] = path.read_text(encoding="utf-8")

    result = review_bundle._validate_workstream_entry_packet_decision_path(
        packet_files,
        expected_branch="feature/fam-007-dev-owner-skeleton-readiness",
        expected_head="fixture-head",
        expected_origin_main="fixture-origin-main",
    )
    if result.status != review_bundle.DECISION_STATUS_BP3_ORCHESTRATION_REVIEW:
        failures.append(
            "FAM-007 BP3 generated packet did not classify as bp3-orchestration-review: "
            f"{result.status}; {result.failures[:3]}"
        )
    combined = "\n".join(packet_files.values()).casefold()
    if "workstream entry final decision review" in combined:
        failures.append(
            "FAM-007 BP3 generated packet still emits stale Workstream Entry final-decision wording"
        )
    if "implementation approval: approved" in combined:
        failures.append(
            "FAM-007 BP3 generated packet incorrectly approves implementation"
        )
    if "seam 1 only" in combined or "first bounded workstream seam only" in combined:
        failures.append(
            "FAM-007 BP3 generated packet must not emit first-seam-only Workstream approval wording"
        )
    primary_digest = packet_files.get("WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md", "")
    required_primary_sections = [
        "## Plain-Language BP3 Readiness Summary",
        "## Accepted BP1 Vision Traceability",
        "## Accepted BP2 Plan Traceability",
        "## Proposed Workstream Implementation Order",
        "## Seam / SLC Readiness Assessment",
        "## Expected Files / Helpers / Validators / Fixtures / Review Artifacts",
        "## Direct Proof Plan",
        "## Rollback And Reversibility Posture",
        "## Drift Controls",
        "## Unresolved Blockers And Pending USER Decisions",
        "## Codex Readiness Recommendation",
        "## Specific USER Readiness Questions",
        "## Exact BP3 USER Decision Options",
    ]
    missing_sections = [
        section for section in required_primary_sections if section not in primary_digest
    ]
    if missing_sections:
        failures.append(
            "FAM-007 BP3 primary digest is missing readiness-contract sections: "
            + "; ".join(missing_sections)
        )
    required_primary_proof_terms = [
        "No-private-action proof",
        "Public-leak prevention",
        "Provider-state inactivity",
        "Runtime/cache/memory deferral",
        "GitHub Desktop binding absence",
        "Backup/import deferral",
        "Artifact identity proof",
        "External-state proof",
    ]
    missing_proof_terms = [
        term for term in required_primary_proof_terms if term not in primary_digest
    ]
    if missing_proof_terms:
        failures.append(
            "FAM-007 BP3 primary digest is missing direct-proof topics: "
            + "; ".join(missing_proof_terms)
        )
    if "Seam 5 - Packet, fixture, validator, and fold-down proof" not in primary_digest:
        failures.append(
            "FAM-007 BP3 primary digest must cover the full accepted seam route, "
            "not only the first Workstream seam"
        )
    return failures


def _validate_fam006_bp3_packet_generation_guard() -> list[str]:
    failures: list[str] = []
    exact_decision = (
        "I accept the FAM-006 BP2 Option C Branch Plan and approve Codex to "
        "prepare BP3 Workstream Entry / Orchestration Validation. BP3 must "
        "validate the Dashboard Recording Card, Recording Studio, minimal Log "
        "Viewer Studio launch/folder shell, native/export log boundary, "
        "open-folder pre-session usability, issue #258 target-reliability line "
        "item, deferred carryforward, Element-to-Phase proof, rollback, "
        "validation, Live Validation, UTS expectations, visual-system inheritance "
        "proof, branch-sprawl safety, and slice/SLC/seam sequencing. Workstream "
        "implementation remains pending separate USER approval."
    )
    copied = [
        (
            "Docs/family_feature_visions/FAM-006_recording.md",
            "FAM-006_recording.md",
        ),
        (
            "Docs/branch_records/feature_fam_006_dashboard_recording_start_stop_local_file.md",
            "feature_fam_006_dashboard_recording_start_stop_local_file.md",
        ),
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir)
        review_bundle._write_workstream_entry_packet_digests(
            target=target,
            source_branch="feature/fam-006-dashboard-recording-start-stop-local-file",
            source_head="fixture-head",
            origin_main="fixture-origin-main",
            packet_folder=target,
            export_zip=target / "FAM-006-20260601-120000.zip",
            copied=copied,
            extra_bundle_files=["USER Review/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"],
            bundle_file_count=7,
            expected_count=len(copied),
            copied_count=len(copied),
            exact_user_decision=exact_decision,
            pending_user_decisions=["Workstream implementation remains pending USER approval."],
        )
        packet_files = {
            "START_HERE.md": (
                "USER Decision This Packet Supports: "
                f"{exact_decision}\n"
                "Decision Path Summary: bp3 orchestration review\n"
                "BP3 Packet Reviewability State: Reviewable\n"
                "BP3 USER Gate State: Pending USER Review\n"
            )
        }
        for path in target.glob("*.md"):
            packet_files[path.name] = path.read_text(encoding="utf-8")

    result = review_bundle._validate_workstream_entry_packet_decision_path(
        packet_files,
        expected_branch="feature/fam-006-dashboard-recording-start-stop-local-file",
        expected_head="fixture-head",
        expected_origin_main="fixture-origin-main",
    )
    if result.status != review_bundle.DECISION_STATUS_BP3_ORCHESTRATION_REVIEW:
        failures.append(
            "FAM-006 BP3 generated packet did not classify as bp3-orchestration-review: "
            f"{result.status}; {result.failures[:3]}"
        )

    stale_support_packet_files = dict(packet_files)
    stale_support_packet_files[review_bundle.USER_BRANCH_VISION_REVIEW_FILE] = (
        "FAM-006 BP3 support context.\n"
        "USER Accepted - BP1 Branch Vision accepted after Option F planning "
        "solidification. BP2 remains Pending USER Review.\n"
    )
    stale_support_result = review_bundle._validate_workstream_entry_packet_decision_path(
        stale_support_packet_files,
        expected_branch="feature/fam-006-dashboard-recording-start-stop-local-file",
        expected_head="fixture-head",
        expected_origin_main="fixture-origin-main",
    )
    if not any("stale BP2-active wording" in failure for failure in stale_support_result.failures):
        failures.append(
            "FAM-006 BP3 packet validation did not reject stale BP2-pending wording "
            "inside a generated support file"
        )

    combined = "\n".join(packet_files.values()).casefold()
    forbidden_terms = [
        "workstream entry final decision review",
        "implementation approval: approved",
        "approve bounded workstream package implementation",
    ]
    stale_terms = [term for term in forbidden_terms if term in combined]
    if stale_terms:
        failures.append(
            "FAM-006 BP3 generated packet emitted stale implementation/final-review wording: "
            + "; ".join(stale_terms)
        )

    primary_digest = packet_files.get("WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md", "")
    required_sections = [
        "## Plain-Language BP3 Readiness Summary",
        "## Accepted BP1 Vision Traceability",
        "## Accepted BP2 Plan Traceability",
        "## Option C Whole-Package Coherence Test",
        "## Surface Admit / Split / Defer Findings",
        "## Proposed Slice / SLC / Seam Sequence",
        "## Direct Proof Plan",
        "## Rollback And Reversibility Posture",
        "## Validation / H1 / Live Validation / UTS Plan",
        "## Visual-System Inheritance Proof",
        "## Deferred Carryforward Applicability",
        "## Exact BP3 USER Decision Options",
    ]
    missing_sections = [section for section in required_sections if section not in primary_digest]
    if missing_sections:
        failures.append(
            "FAM-006 BP3 primary digest is missing substantive orchestration sections: "
            + "; ".join(missing_sections)
        )

    required_proof_terms = [
        "Dashboard Recording Card proof",
        "Recording Studio proof",
        "Log Viewer shell proof",
        "Native/export boundary proof",
        "Issue #258 proof",
        "Option C remains one coherent bounded",
        "Return to BP2",
    ]
    missing_proof_terms = [term for term in required_proof_terms if term not in primary_digest]
    if missing_proof_terms:
        failures.append(
            "FAM-006 BP3 primary digest is missing direct-proof topics: "
            + "; ".join(missing_proof_terms)
        )

    return failures


def _validate_fam007_workstream_implementation_packet_priority_guard() -> list[str]:
    failures: list[str] = []
    exact_decision = (
        "BP1, BP2, and BP3 are accepted; approve bounded Workstream package "
        "implementation for the FAM-007 Dev/Owner Skeleton Readiness same-branch "
        "package with Seam 1 as the entry checkpoint and continuation until "
        "Workstream Green."
    )
    copied = [
        (
            "Docs/branch_records/feature_fam_007_dev_owner_skeleton_readiness.md",
            "feature_fam_007_dev_owner_skeleton_readiness.md",
        )
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir)
        review_bundle._write_workstream_entry_packet_digests(
            target=target,
            source_branch="feature/fam-007-dev-owner-skeleton-readiness",
            source_head="fixture-head",
            origin_main="fixture-origin-main",
            packet_folder=target,
            export_zip=target / "FAM-007-20260601-120000.zip",
            copied=copied,
            extra_bundle_files=["USER Review/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"],
            bundle_file_count=6,
            expected_count=len(copied),
            copied_count=len(copied),
            exact_user_decision=exact_decision,
            pending_user_decisions=[
                "Hardening, Live Validation, PR, merge, release, private setup, "
                "provider/runtime/cache/memory behavior, and cleanup remain future "
                "USER decisions."
            ],
        )
        packet_files = {
            "START_HERE.md": (
                "USER Decision This Packet Supports: "
                f"{exact_decision}\n"
                "Decision Path Summary: implementation-ready - BP1, BP2, and BP3 "
                "are accepted; bounded Workstream package implementation is "
                "approved by this packet with Seam 1 as the entry checkpoint.\n"
            )
        }
        for path in target.glob("*.md"):
            packet_files[path.name] = path.read_text(encoding="utf-8")
        review_bundle._write_user_branch_plan_review(
            target=target,
            title="FAM-007 Dev/Owner Skeleton Readiness",
            review_purpose="Fixture Workstream implementation approval support file.",
            source_branch="feature/fam-007-dev-owner-skeleton-readiness",
            source_head="fixture-head",
            upstream="origin/feature/fam-007-dev-owner-skeleton-readiness",
            origin_main="fixture-origin-main",
            exact_user_decision=exact_decision,
            pending_user_decisions=[
                "Hardening, Live Validation, PR, merge, release, private setup, "
                "provider/runtime/cache/memory behavior, and cleanup remain future "
                "USER decisions."
            ],
            copied=copied,
        )
        branch_plan_review = (
            target / review_bundle.USER_BRANCH_PLAN_REVIEW_FILE
        ).read_text(encoding="utf-8")
        packet_files[review_bundle.USER_BRANCH_PLAN_REVIEW_FILE] = branch_plan_review

    result = review_bundle._validate_workstream_entry_packet_decision_path(
        packet_files,
        expected_branch="feature/fam-007-dev-owner-skeleton-readiness",
        expected_head="fixture-head",
        expected_origin_main="fixture-origin-main",
        require_implementation_ready=True,
    )
    if result.status != review_bundle.DECISION_STATUS_IMPLEMENTATION_READY:
        failures.append(
            "FAM-007 Workstream implementation approval packet did not classify "
            f"as implementation-ready: {result.status}; {result.failures[:3]}"
        )
    combined = "\n".join(packet_files.values()).casefold()
    forbidden_bp3_review_terms = [
        "bp3 packet reviewability state: reviewable",
        "bp3 user gate state: pending user review",
        "workstream implementation itself remains a separate future user decision",
        "exact bp3 user decision options",
    ]
    emitted_forbidden_terms = [
        term for term in forbidden_bp3_review_terms if term in combined
    ]
    if emitted_forbidden_terms:
        failures.append(
            "FAM-007 Workstream implementation approval packet emitted BP3 review "
            "or pending-gate wording despite implementation approval: "
            + "; ".join(emitted_forbidden_terms)
        )
    support_file_forbidden_terms = [
        "pending user response",
        "bp3 active - workstream entry / orchestration validation",
        "workstream implementation remains pending separate user approval",
        "this packet does not authorize workstream implementation",
    ]
    emitted_support_file_terms = [
        term for term in support_file_forbidden_terms
        if term in branch_plan_review.casefold()
    ]
    if emitted_support_file_terms:
        failures.append(
            "FAM-007 Workstream implementation approval support BP2 file emitted "
            "pending or BP3-only wording: "
            + "; ".join(emitted_support_file_terms)
        )
    support_file_required_terms = [
        "Complete - USER accepted the BP2 Branch Plan Contract; BP3 is accepted",
        "Status: Accepted by USER - this BP2 support file is closed as accepted engineering-plan context",
        "Implementation-ready - BP1, BP2, and BP3 are accepted",
    ]
    missing_support_terms = [
        term for term in support_file_required_terms if term not in branch_plan_review
    ]
    if missing_support_terms:
        failures.append(
            "FAM-007 Workstream implementation approval support BP2 file is missing "
            "accepted implementation-ready context: "
            + "; ".join(missing_support_terms)
        )
    required_terms = [
        "bounded Workstream package implementation is approved",
        "Seam 1 as the entry checkpoint",
        "Continuation must proceed one active same-branch seam at a time until Workstream Green",
    ]
    missing_required_terms = [term for term in required_terms if term not in "\n".join(packet_files.values())]
    if missing_required_terms:
        failures.append(
            "FAM-007 Workstream implementation approval packet is missing "
            "implementation-ready terms: "
            + "; ".join(missing_required_terms)
        )
    return failures


def _validate_fam006_workstream_approval_review_packet_guard() -> list[str]:
    failures: list[str] = []
    exact_decision = (
        "Does USER approve bounded FAM-006 Workstream/runtime implementation "
        "for the accepted Option C package: Dashboard Recording Card, Recording "
        "Studio, minimal Log Viewer Studio launch/folder shell, native/export "
        "log boundary, open-folder pre-session usability, issue #258 target "
        "reliability, deferred carryforward applicability, Element-to-Phase "
        "proof, rollback, validation, H1, Live Validation, UTS, visual-system "
        "inheritance, and slice/SLC/seam sequencing? Workstream implementation "
        "remains pending until USER approves this packet."
    )
    copied = [
        (
            "Docs/family_feature_visions/FAM-006_recording.md",
            "FAM-006_recording.md",
        ),
        (
            "Docs/branch_records/feature_fam_006_dashboard_recording_start_stop_local_file.md",
            "feature_fam_006_dashboard_recording_start_stop_local_file.md",
        ),
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir)
        review_bundle._write_workstream_entry_packet_digests(
            target=target,
            source_branch="feature/fam-006-dashboard-recording-start-stop-local-file",
            source_head="fixture-head",
            origin_main="fixture-origin-main",
            packet_folder=target,
            export_zip=target / "FAM-006-20260609-120000.zip",
            copied=copied,
            extra_bundle_files=["USER Review/WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"],
            bundle_file_count=7,
            expected_count=len(copied),
            copied_count=len(copied),
            exact_user_decision=exact_decision,
            pending_user_decisions=[
                "Runtime mutation, issue closeout, PR Readiness, merge, release, "
                "branch cleanup, Governance/FAM-007/neutral-main mutation, "
                "provider/model/private work, and full Log Viewer/export/tray/"
                "keybind/settings/Native Log Loader scope remain pending."
            ],
        )
        packet_files = {
            "START_HERE.md": (
                "USER Decision This Packet Supports: "
                f"{exact_decision}\n"
                "Decision Path Summary: workstream implementation approval review - "
                "BP1, BP2, and BP3 are accepted; bounded FAM-006 Workstream/runtime "
                "implementation approval packet is Reviewable; USER implementation "
                "approval remains pending.\n"
                "Packet Reviewability State: Reviewable\n"
                "USER Gate State: Pending USER Review - Workstream/runtime "
                "implementation approval remains pending\n"
            )
        }
        for path in target.glob("*.md"):
            packet_files[path.name] = path.read_text(encoding="utf-8")
        review_bundle._write_user_branch_plan_review(
            target=target,
            title="FAM-006 Dashboard Recording Start/Stop To Local File",
            review_purpose="Fixture Workstream implementation approval review support file.",
            source_branch="feature/fam-006-dashboard-recording-start-stop-local-file",
            source_head="fixture-head",
            upstream="origin/feature/fam-006-dashboard-recording-start-stop-local-file",
            origin_main="fixture-origin-main",
            exact_user_decision=exact_decision,
            pending_user_decisions=[
                "Runtime mutation, issue closeout, PR Readiness, merge, release, "
                "branch cleanup, Governance/FAM-007/neutral-main mutation, "
                "provider/model/private work, and full Log Viewer/export/tray/"
                "keybind/settings/Native Log Loader scope remain pending."
            ],
            copied=copied,
        )
        branch_plan_review = (
            target / review_bundle.USER_BRANCH_PLAN_REVIEW_FILE
        ).read_text(encoding="utf-8")
        packet_files[review_bundle.USER_BRANCH_PLAN_REVIEW_FILE] = branch_plan_review
        review_bundle._write_user_branch_vision_review(
            target=target,
            title="FAM-006 Workstream Implementation Approval Review - Option C",
            review_purpose="Fixture Workstream implementation approval review accepted BP1 support file.",
            exact_user_decision=exact_decision,
            pending_user_decisions=[
                "Runtime mutation, issue closeout, PR Readiness, merge, release, "
                "branch cleanup, Governance/FAM-007/neutral-main mutation, "
                "provider/model/private work, and full Log Viewer/export/tray/"
                "keybind/settings/Native Log Loader scope remain pending."
            ],
            copied=copied,
        )
        branch_vision_review = (
            target / review_bundle.USER_BRANCH_VISION_REVIEW_FILE
        ).read_text(encoding="utf-8")
        packet_files[review_bundle.USER_BRANCH_VISION_REVIEW_FILE] = branch_vision_review

    result = review_bundle._validate_workstream_entry_packet_decision_path(
        packet_files,
        expected_branch="feature/fam-006-dashboard-recording-start-stop-local-file",
        expected_head="fixture-head",
        expected_origin_main="fixture-origin-main",
    )
    if (
        result.status
        != review_bundle.DECISION_STATUS_WORKSTREAM_IMPLEMENTATION_APPROVAL_REVIEW
    ):
        failures.append(
            "FAM-006 Workstream implementation approval review packet did not "
            f"classify as pending approval review: {result.status}; "
            f"{result.failures[:3]}"
        )
    combined = "\n".join(packet_files.values())
    required_terms = [
        "Dashboard Recording Card",
        "Recording Studio",
        "minimal Log Viewer Studio",
        "native/export log boundary",
        "issue #258 target reliability",
        "SLC-051 / Seam 1 target reliability",
        "A green first seam is continuation proof, not package completion",
        "Single-seam or single-slice authority is not granted",
        "Workstream/runtime implementation remains pending until USER approves",
    ]
    missing_required_terms = [term for term in required_terms if term not in combined]
    if missing_required_terms:
        failures.append(
            "FAM-006 Workstream implementation approval review packet is missing "
            "required bounded-package terms: "
            + "; ".join(missing_required_terms)
        )
    combined_normalized = combined.casefold()
    forbidden_terms = [
        "fam-007 dev/owner",
        "fam-007 breakpoint",
        "dev/owner",
        "action-gate registry",
        "bounded workstream package implementation is approved by this packet",
        "bp3 is not accepted",
        "bp2 remains pending",
    ]
    emitted_forbidden_terms = [
        term for term in forbidden_terms if term in combined_normalized
    ]
    if emitted_forbidden_terms:
        failures.append(
            "FAM-006 Workstream implementation approval review packet emitted "
            "wrong-family, approved-implementation, or stale-gate wording: "
            + "; ".join(emitted_forbidden_terms)
        )
    side_aid_required_terms = [
        "Accepted BP1 Context",
        "USER Accepted - BP1 Branch Vision accepted by USER",
        "BP2 answered: Option C was accepted by USER as the Branch Plan",
        "BP3 answered: Option C was accepted by USER as one coherent bounded Workstream package",
        "Workstream/runtime implementation approval remains Pending USER Review",
    ]
    missing_side_aid_terms = [
        term for term in side_aid_required_terms if term not in branch_vision_review
    ]
    if missing_side_aid_terms:
        failures.append(
            "FAM-006 Workstream implementation approval review BP1 support aid "
            "is missing accepted-context terms: "
            + "; ".join(missing_side_aid_terms)
        )
    side_aid_forbidden_terms = [
        "Draft - update to Complete",
        "BP1 packet is ready for USER Branch Vision Review, but acceptance is not recorded",
        "USER must accept, revise, waive, reject, or block BP1 before BP2 preparation can be green",
        "BP2 remains Pending USER Review",
        "BP3 remains Pending USER Review",
        "BP3 may be prepared only after BP2 is accepted or waived",
        "BP3 must answer whether Option C is accepted",
        "Workstream Entry remains pending",
    ]
    emitted_side_aid_forbidden_terms = [
        term
        for term in side_aid_forbidden_terms
        if term.casefold() in branch_vision_review.casefold()
    ]
    if emitted_side_aid_forbidden_terms:
        failures.append(
            "FAM-006 Workstream implementation approval review BP1 support aid "
            "emitted stale BP1/BP2/BP3 gate wording: "
            + "; ".join(emitted_side_aid_forbidden_terms)
        )
    return failures


def _validate_primary_user_review_file_stage_priority() -> list[str]:
    failures: list[str] = []
    bp3_trace_decision = (
        "I approve BP3 Workstream Entry / Orchestration Validation against "
        "accepted BP1 vision and BP2 branch plan traceability."
    )
    if (
        review_bundle._primary_user_review_file(bp3_trace_decision)
        != "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ):
        failures.append(
            "BP3 primary USER review routing must prioritize Workstream Entry / "
            "Orchestration over BP1/BP2 traceability wording"
        )
    bp3_prerequisite_first_decision = (
        "BP1 and BP2 are accepted; approve BP3 orchestration validation for "
        "Workstream Entry."
    )
    if (
        review_bundle._primary_user_review_file(bp3_prerequisite_first_decision)
        != "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ):
        failures.append(
            "BP3 primary USER review routing must prefer the requested BP3 gate "
            "over prerequisite BP1/BP2 mentions"
        )
    workstream_implementation_decision = "Approve bounded workstream implementation."
    if (
        review_bundle._primary_user_review_file(workstream_implementation_decision)
        != "WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
    ):
        failures.append(
            "Workstream implementation approval packets must route the primary "
            "USER review file to WORKSTREAM_ENTRY_ANALYSIS_DIGEST.md"
        )
    bp2_trace_decision = (
        "I approve BP2 Branch Plan Review after accepted BP1 branch vision proof."
    )
    if (
        review_bundle._primary_user_review_file(bp2_trace_decision)
        != review_bundle.USER_BRANCH_PLAN_REVIEW_FILE
    ):
        failures.append(
            "BP2 primary USER review routing must remain USER_BRANCH_PLAN_REVIEW.md "
            "when BP2 text mentions accepted BP1 proof"
        )
    bp2_prerequisite_first_decision = (
        "BP1 is accepted; approve BP2 Branch Plan Review for engineering planning."
    )
    if (
        review_bundle._primary_user_review_file(bp2_prerequisite_first_decision)
        != review_bundle.USER_BRANCH_PLAN_REVIEW_FILE
    ):
        failures.append(
            "BP2 primary USER review routing must prefer the requested BP2 gate "
            "over prerequisite BP1 mentions"
        )
    bp1_preview_decision = (
        "I approve BP1 Branch Vision Review before BP2 Branch Plan Review and "
        "BP3 orchestration planning begin."
    )
    if (
        review_bundle._primary_user_review_file(bp1_preview_decision)
        != review_bundle.USER_BRANCH_VISION_REVIEW_FILE
    ):
        failures.append(
            "BP1 primary USER review routing must remain USER_BRANCH_VISION_REVIEW.md "
            "when BP1 text previews later BP2/BP3 gates"
        )
    return failures


def _validate_rar_issue_candidate_durability_fixtures() -> list[str]:
    failures: list[str] = []

    def row(
        candidate_id: str,
        disposition: str = "ACTIVE_PENDING_USER_DECISION",
        blocking: str = "YES",
        github_issue: str = "NONE - issue mutation not approved",
        carrier: str = "Owner FAM-006; reason current RAR adoption gap; carrier FAM-006 RAR repair; trigger next RAR review",
        decision: str = "USER must review repair, waiver with reason and scope, route, deferral, or approved GitHub issue creation.",
    ) -> str:
        return (
            f"| {candidate_id} | FAM-006 | HUD Dashboard | Window control cluster | "
            "Legacy close control diverges from UIREF-002 | RAR contact sheet row HUD-CTRL-01 | "
            f"{disposition} | {blocking} | {carrier} | {github_issue} | "
            "Verified from RAR packet receipt 20260620 | "
            f"{decision} |"
        )

    def table(*rows: str) -> str:
        return "\n".join(
            (
                "Issue Candidate Decision Surface:",
                "",
                rar_issue_durability.DECISION_SURFACE_HEADER,
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                *rows,
            )
        )

    def packet_with_sections(
        root: Path,
        primary_text: str | None = None,
        review_aid_text: str | None = None,
    ) -> Path:
        packet = root / "FAM-006"
        user_review = packet / "USER Review"
        review_aids = packet / "Review Aids"
        context = packet / "Source Truth Context"
        user_review.mkdir(parents=True)
        review_aids.mkdir(parents=True)
        context.mkdir(parents=True)
        (packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        if primary_text is not None:
            (user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
                primary_text,
                encoding="utf-8",
            )
        if review_aid_text is not None:
            (review_aids / "RAR_ISSUE_CANDIDATE_REVIEW_AID.md").write_text(
                review_aid_text,
                encoding="utf-8",
            )
        (context / "COPIED_CONTEXT.md").write_text(
            "# Copied Source Truth Context\n\nNo active issue-candidate decision surface lives in copied context.",
            encoding="utf-8",
        )
        return packet

    def snapshot(state: str) -> dict[str, rar_issue_durability.GitHubIssueSnapshot]:
        return {
            "275": rar_issue_durability.GitHubIssueSnapshot(
                issue="275",
                state=state,
                source="gh issue view 275 --json state,updatedAt",
                last_verified="2026-06-25",
            )
        }

    valid_cases = (
        VALID_RAR_ISSUE_DURABILITY_CARRY_FORWARD_FIXTURE,
        VALID_RAR_ISSUE_DURABILITY_USER_DISPOSITIONS_FIXTURE,
        VALID_RAR_ISSUE_DURABILITY_GITHUB_PENDING_FIXTURE,
    )
    for fixture in valid_cases:
        case_failures = rar_issue_durability.validate_text(
            fixture.read_text(encoding="utf-8"), source=str(fixture)
        )
        if case_failures:
            failures.append(
                f"Valid RAR issue-candidate durability fixture unexpectedly failed: {fixture}: "
                + "; ".join(case_failures[:5])
            )

    invalid_cases = (
        (
            INVALID_RAR_ISSUE_DURABILITY_PACKETED_ONLY_FIXTURE,
            EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET,
        ),
        (
            INVALID_RAR_ISSUE_DURABILITY_DEFERRED_MISSING_OWNER_FIXTURE,
            "deferred disposition requires durable owner",
        ),
        (
            INVALID_RAR_ISSUE_DURABILITY_STALE_GITHUB_CLOSED_FIXTURE,
            "unknown/stale GitHub state cannot close candidate",
        ),
        (
            INVALID_RAR_ISSUE_DURABILITY_DUPLICATE_LINEAGE_FIXTURE,
            "duplicate/conflicting lineage",
        ),
        (
            INVALID_RAR_ISSUE_DURABILITY_REPAIRED_UNVERIFIED_FIXTURE,
            "repaired disposition requires independent verification evidence",
        ),
    )
    for fixture, expected_snippet in invalid_cases:
        case_failures = rar_issue_durability.validate_text(
            fixture.read_text(encoding="utf-8"), source=str(fixture)
        )
        if expected_snippet not in "\n".join(case_failures):
            failures.append(
                f"Invalid RAR issue-candidate durability fixture did not fail on {expected_snippet!r}: {fixture}"
            )

    generated_packeted_only_reviewed_text = (
        VALID_RAR_ISSUE_DURABILITY_CARRY_FORWARD_FIXTURE.read_text(encoding="utf-8")
        .replace("ACTIVE_PENDING_USER_DECISION", "Issue Candidate Packet USER-Reviewed")
        .replace(
            "USER must review the RAR packet and choose repair, waiver with reason, deferred owner/trigger, route, or approved GitHub issue creation before normal progression.",
            "The candidate was packeted only, so normal progression may continue.",
        )
    )
    generated_packeted_only_failures = rar_issue_durability.validate_text(
        generated_packeted_only_reviewed_text, source="generated packeted-only RAR"
    )
    if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
        generated_packeted_only_failures
    ):
        failures.append(
            "Generated RAR durability adversarial case did not reject packeted-only reviewed wording"
        )

    documented_label_failures = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-030",
                disposition="Repaired And Independently Verified",
                blocking="NO",
                carrier="Owner FAM-006; reason repaired in LV proof; carrier FAM-006 RAR repair; trigger regression only",
                decision="Independent verification revalidated the repair; no current USER decision is needed.",
            ),
            row(
                "FAM006-RAR-031",
                disposition="USER Waived With Reason And Scope",
                blocking="NO",
                carrier="Owner FAM-006; reason USER accepted exception; scope HUD Dashboard current branch only; trigger reopened HUD work",
                decision="USER waived this item because the current branch excludes the surface; scope HUD Dashboard current branch only.",
            ),
            row(
                "FAM006-RAR-032",
                disposition="Mapped To Open GitHub Issue",
                blocking="NO",
                github_issue="#275",
                carrier="Owner FAM-006; reason mapped to open issue; carrier GitHub issue #275; trigger issue closeout review",
                decision="Track through open issue #275; owner FAM-006 reviews on trigger when issue closes.",
            ),
        ),
        source="generated documented disposition labels",
        github_snapshot=snapshot("OPEN"),
    )
    if documented_label_failures:
        failures.append(
            "Generated RAR fixture rejected documented durable-disposition labels: "
            + "; ".join(documented_label_failures[:5])
        )

    no_decision_affirmative_proof_failures = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-034",
                disposition="REPAIRED_VERIFIED",
                blocking="NO",
                carrier="FAM-006 external RAR ledger.",
                decision=(
                    "No current USER decision is needed because independent "
                    "verification revalidated the repair."
                ),
            ),
            row(
                "FAM006-RAR-035",
                disposition="USER_WAIVED_WITH_REASON",
                blocking="NO",
                carrier="FAM-006 external RAR ledger.",
                decision=(
                    "No current USER decision is needed because USER waived this "
                    "with reason current branch excludes the surface and scope HUD "
                    "Dashboard current branch only."
                ),
            ),
            row(
                "FAM006-RAR-036",
                disposition="ROUTED_TO_LEGAL_CARRIER",
                blocking="NO",
                carrier="Routed to FAM-006 legal carrier.",
                decision="No current USER decision because carrier acceptance receipt recorded.",
            ),
        ),
        source="generated no-decision affirmative proof wording",
    )
    if no_decision_affirmative_proof_failures:
        failures.append(
            "Generated RAR fixture falsely rejected affirmative no-decision proof wording: "
            + "; ".join(no_decision_affirmative_proof_failures[:5])
        )

    duplicate_disposition_conflict = rar_issue_durability.validate_text(
        table(
            row("FAM006-RAR-033"),
            row(
                "FAM006-RAR-033",
                disposition="USER_WAIVED_WITH_REASON",
                blocking="NO",
                carrier="Owner FAM-006; reason USER accepted exception; carrier FAM-006 RAR repair; trigger reopened HUD work; scope HUD Dashboard current branch only",
                decision="USER waived this item because current branch excludes the surface; scope HUD Dashboard current branch only.",
            ),
        ),
        source="generated duplicate disposition conflict",
    )
    if "duplicate/conflicting lineage" not in "\n".join(duplicate_disposition_conflict):
        failures.append(
            "Generated RAR fixture did not reject duplicate lineage with conflicting disposition fields"
        )

    eight_active_rows = tuple(row(f"FAM006-RAR-{index:03d}") for index in range(1, 9))
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        ledger = temp_root / "external_ledger.md"
        ledger.write_text(table(*eight_active_rows), encoding="utf-8")

        omitted_packet = packet_with_sections(
            temp_root / "omitted",
            primary_text=table(row("FAM006-RAR-999")),
        )
        omitted_failures = rar_issue_durability.validate_packet_folder(
            omitted_packet,
            external_ledger=ledger,
        )
        if "external RAR issue candidate FAM006-RAR-001 missing" not in "\n".join(
            omitted_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture did not reject active external candidates omitted from current packet"
            )

        carried_packet = packet_with_sections(
            temp_root / "carried",
            primary_text=table(*eight_active_rows),
        )
        carried_failures = rar_issue_durability.validate_packet_folder(
            carried_packet,
            external_ledger=ledger,
        )
        if carried_failures:
            failures.append(
                "Generated RAR packet/ledger fixture rejected active candidates carried into the primary USER surface: "
                + "; ".join(carried_failures[:5])
            )

        review_aid_only_packet = packet_with_sections(
            temp_root / "review-aid-only",
            review_aid_text=table(row("FAM006-RAR-010")),
        )
        review_aid_failures = rar_issue_durability.validate_packet_folder(
            review_aid_only_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject issue-candidate table present only in Review Aids"
            )

        same_basename_review_aid_packet = temp_root / "same-basename-review-aid-only" / "FAM-006"
        same_basename_review_aids = same_basename_review_aid_packet / "Review Aids"
        same_basename_context = same_basename_review_aid_packet / "Source Truth Context"
        same_basename_review_aids.mkdir(parents=True)
        same_basename_context.mkdir(parents=True)
        (same_basename_review_aid_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (same_basename_review_aids / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-036")),
            encoding="utf-8",
        )
        (same_basename_context / "COPIED_CONTEXT.md").write_text(
            table(row("FAM006-RAR-CONTEXT-03")),
            encoding="utf-8",
        )
        same_basename_failures = rar_issue_durability.validate_packet_folder(
            same_basename_review_aid_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            same_basename_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject Review Aids-only decision table with the primary basename"
            )

        nested_review_aid_primary_packet = temp_root / "nested-review-aid-user-review" / "FAM-006"
        nested_review_aid_user_review = nested_review_aid_primary_packet / "Review Aids" / "USER Review"
        nested_review_aid_context = nested_review_aid_primary_packet / "Source Truth Context"
        nested_review_aid_user_review.mkdir(parents=True)
        nested_review_aid_context.mkdir(parents=True)
        (nested_review_aid_primary_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (nested_review_aid_user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-046")),
            encoding="utf-8",
        )
        (nested_review_aid_context / "COPIED_CONTEXT.md").write_text(
            "# Copied Source Truth Context\n",
            encoding="utf-8",
        )
        nested_review_aid_failures = rar_issue_durability.validate_packet_folder(
            nested_review_aid_primary_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            nested_review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject nested Review Aids/USER Review issue-candidate table as primary"
            )

        nested_context_primary_packet = temp_root / "nested-context-user-review" / "FAM-006"
        nested_context_user_review = nested_context_primary_packet / "Source Truth Context" / "USER Review"
        nested_context_user_review.mkdir(parents=True)
        (nested_context_primary_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (nested_context_user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-047")),
            encoding="utf-8",
        )
        nested_context_primary_failures = rar_issue_durability.validate_packet_folder(
            nested_context_primary_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            nested_context_primary_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject nested Source Truth Context/USER Review issue-candidate table as primary"
            )

        mention_only_packet = packet_with_sections(
            temp_root / "mention-only-primary",
            primary_text=None,
        )
        (
            mention_only_packet
            / "USER Review"
            / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md"
        ).write_text(
            "# RAR Issue Candidate Decision Surface\n\nIssue Candidate: FAM006-RAR-048 still needs USER disposition.",
            encoding="utf-8",
        )
        mention_only_packet_failures = rar_issue_durability.validate_packet_folder(
            mention_only_packet
        )
        if "Issue Candidate Decision Surface Missing" not in "\n".join(
            mention_only_packet_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject primary issue-candidate mention without decision table"
            )

        plural_mention_only_packet = packet_with_sections(
            temp_root / "plural-mention-only-primary",
            primary_text=None,
        )
        (
            plural_mention_only_packet
            / "USER Review"
            / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md"
        ).write_text(
            "# RAR Issue Candidate Decision Surface\n\nIssue candidates FAM006-RAR-055 and FAM006-RAR-056 still need USER disposition.",
            encoding="utf-8",
        )
        plural_mention_only_packet_failures = rar_issue_durability.validate_packet_folder(
            plural_mention_only_packet
        )
        if "Issue Candidate Decision Surface Missing" not in "\n".join(
            plural_mention_only_packet_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject plural issue-candidates mention without decision table"
            )

        nested_user_review_historical_packet = temp_root / "nested-user-review-historical-only" / "FAM-006"
        nested_user_review_historical = nested_user_review_historical_packet / "USER Review" / "Historical"
        nested_user_review_historical.mkdir(parents=True)
        (nested_user_review_historical_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (nested_user_review_historical / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-051")),
            encoding="utf-8",
        )
        nested_user_review_historical_failures = rar_issue_durability.validate_packet_folder(
            nested_user_review_historical_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            nested_user_review_historical_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject nested USER Review/Historical issue-candidate table as primary"
            )

        direct_historical_user_review_packet = (
            temp_root / "direct-historical-user-review-only" / "FAM-006"
        )
        direct_historical_user_review = direct_historical_user_review_packet / "USER Review"
        direct_historical_user_review.mkdir(parents=True)
        (direct_historical_user_review_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (direct_historical_user_review / "HISTORICAL_RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-076")),
            encoding="utf-8",
        )
        direct_historical_user_review_failures = rar_issue_durability.validate_packet_folder(
            direct_historical_user_review_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            direct_historical_user_review_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject direct historical USER Review issue-candidate table as primary"
            )

        routed_nested_user_review_packet = temp_root / "routed-nested-user-review" / "FAM-006"
        routed_nested_user_review_historical = (
            routed_nested_user_review_packet / "USER Review" / "Historical"
        )
        routed_nested_user_review_historical.mkdir(parents=True)
        (routed_nested_user_review_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary issue-candidate decision file: USER Review/Historical/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (routed_nested_user_review_historical / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-052")),
            encoding="utf-8",
        )
        routed_nested_user_review_failures = rar_issue_durability.validate_packet_folder(
            routed_nested_user_review_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            routed_nested_user_review_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject START_HERE-routed nested USER Review/Historical issue-candidate table"
            )

        routed_helper_output_packet = temp_root / "routed-helper-output-only" / "FAM-006"
        routed_helper_output = routed_helper_output_packet / "Helper-Output"
        routed_helper_context = routed_helper_output_packet / "Source Truth Context"
        routed_helper_output.mkdir(parents=True)
        routed_helper_context.mkdir(parents=True)
        (routed_helper_output_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary issue-candidate decision file: Helper-Output/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (routed_helper_output / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-060")),
            encoding="utf-8",
        )
        (routed_helper_context / "COPIED_CONTEXT.md").write_text(
            "# Copied Source Truth Context\n",
            encoding="utf-8",
        )
        routed_helper_output_failures = rar_issue_durability.validate_packet_folder(
            routed_helper_output_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            routed_helper_output_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject START_HERE-routed helper-output issue-candidate table"
            )

        hidden_nested_user_review_packet = temp_root / "hidden-nested-user-review-candidate" / "FAM-006"
        hidden_nested_primary = hidden_nested_user_review_packet / "USER Review"
        hidden_nested_historical = hidden_nested_user_review_packet / "USER Review" / "Historical"
        hidden_nested_primary.mkdir(parents=True)
        hidden_nested_historical.mkdir(parents=True)
        (hidden_nested_user_review_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (hidden_nested_primary / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-053")),
            encoding="utf-8",
        )
        (hidden_nested_historical / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-054")),
            encoding="utf-8",
        )
        hidden_nested_user_review_failures = rar_issue_durability.validate_packet_folder(
            hidden_nested_user_review_packet
        )
        if "supporting/context RAR issue candidate FAM006-RAR-054 missing" not in "\n".join(
            hidden_nested_user_review_failures
        ):
            failures.append(
                "Generated RAR packet fixture allowed active nested USER Review/Historical candidate absent from primary decision surface"
            )

        routed_review_aid_packet = temp_root / "routed-review-aid-only" / "FAM-006"
        routed_review_aid = routed_review_aid_packet / "Review Aids"
        routed_review_context = routed_review_aid_packet / "Source Truth Context"
        routed_review_aid.mkdir(parents=True)
        routed_review_context.mkdir(parents=True)
        (routed_review_aid_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary issue-candidate decision file: Review Aids/RAR_ISSUE_CANDIDATE_REVIEW_AID.md\n",
            encoding="utf-8",
        )
        (routed_review_aid / "RAR_ISSUE_CANDIDATE_REVIEW_AID.md").write_text(
            table(row("FAM006-RAR-040")),
            encoding="utf-8",
        )
        (routed_review_context / "COPIED_CONTEXT.md").write_text(
            table(row("FAM006-RAR-CONTEXT-04")),
            encoding="utf-8",
        )
        routed_review_aid_failures = rar_issue_durability.validate_packet_folder(
            routed_review_aid_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            routed_review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject START_HERE-routed Review Aids issue-candidate table"
            )

        hidden_review_aid_packet = temp_root / "hidden-review-aid-candidate" / "FAM-006"
        hidden_user_review = hidden_review_aid_packet / "USER Review"
        hidden_review_aids = hidden_review_aid_packet / "Review Aids"
        hidden_context = hidden_review_aid_packet / "Source Truth Context"
        hidden_user_review.mkdir(parents=True)
        hidden_review_aids.mkdir(parents=True)
        hidden_context.mkdir(parents=True)
        (hidden_review_aid_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (hidden_user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-041")),
            encoding="utf-8",
        )
        (hidden_review_aids / "RAR_ISSUE_CANDIDATE_REVIEW_AID.md").write_text(
            table(row("FAM006-RAR-042")),
            encoding="utf-8",
        )
        (hidden_context / "COPIED_CONTEXT.md").write_text(
            "# Copied Source Truth Context\n",
            encoding="utf-8",
        )
        hidden_review_aid_failures = rar_issue_durability.validate_packet_folder(
            hidden_review_aid_packet
        )
        if "supporting/context RAR issue candidate FAM006-RAR-042 missing" not in "\n".join(
            hidden_review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture allowed active Review Aids candidate absent from primary decision surface"
            )

        same_id_same_lineage_review_aid_packet = temp_root / "same-id-same-lineage-review-aid" / "FAM-006"
        same_id_same_lineage_user_review = same_id_same_lineage_review_aid_packet / "USER Review"
        same_id_same_lineage_review_aids = same_id_same_lineage_review_aid_packet / "Review Aids"
        same_id_same_lineage_user_review.mkdir(parents=True)
        same_id_same_lineage_review_aids.mkdir(parents=True)
        (same_id_same_lineage_review_aid_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (same_id_same_lineage_user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-063")),
            encoding="utf-8",
        )
        (same_id_same_lineage_review_aids / "RAR_ISSUE_CANDIDATE_REVIEW_AID.md").write_text(
            table(row("FAM006-RAR-063")),
            encoding="utf-8",
        )
        same_id_same_lineage_review_aid_failures = rar_issue_durability.validate_packet_folder(
            same_id_same_lineage_review_aid_packet
        )
        if same_id_same_lineage_review_aid_failures:
            failures.append(
                "Generated RAR packet fixture rejected supporting Review Aids candidate with matching lineage: "
                + "; ".join(same_id_same_lineage_review_aid_failures[:5])
            )

        same_id_different_lineage_review_aid_packet = (
            temp_root / "same-id-different-lineage-review-aid" / "FAM-006"
        )
        same_id_different_lineage_user_review = same_id_different_lineage_review_aid_packet / "USER Review"
        same_id_different_lineage_review_aids = same_id_different_lineage_review_aid_packet / "Review Aids"
        same_id_different_lineage_user_review.mkdir(parents=True)
        same_id_different_lineage_review_aids.mkdir(parents=True)
        (same_id_different_lineage_review_aid_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (same_id_different_lineage_user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-064")),
            encoding="utf-8",
        )
        (same_id_different_lineage_review_aids / "RAR_ISSUE_CANDIDATE_REVIEW_AID.md").write_text(
            table(
                "| FAM006-RAR-064 | FAM-006 | Log Viewer Studio | Status row | Folder status mismatch | RAR contact sheet row LOG-STATUS-064 | ACTIVE_PENDING_USER_DECISION | YES | Owner FAM-006; reason current RAR adoption gap; carrier FAM-006 RAR repair; trigger next RAR review | NONE - issue mutation not approved | Verified from RAR packet receipt 20260620 | USER must review repair, waiver with reason and scope, route, deferral, or approved GitHub issue creation. |"
            ),
            encoding="utf-8",
        )
        same_id_different_lineage_review_aid_failures = rar_issue_durability.validate_packet_folder(
            same_id_different_lineage_review_aid_packet
        )
        if "supporting/context RAR issue candidate FAM006-RAR-064 missing" not in "\n".join(
            same_id_different_lineage_review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture allowed same-ID supporting Review Aids candidate with different lineage"
            )

        hidden_context_packet = temp_root / "hidden-context-candidate" / "FAM-006"
        hidden_context_user_review = hidden_context_packet / "USER Review"
        hidden_context_folder = hidden_context_packet / "Source Truth Context"
        hidden_context_user_review.mkdir(parents=True)
        hidden_context_folder.mkdir(parents=True)
        (hidden_context_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (hidden_context_user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-043")),
            encoding="utf-8",
        )
        (hidden_context_folder / "COPIED_CONTEXT.md").write_text(
            table(row("FAM006-RAR-044")),
            encoding="utf-8",
        )
        hidden_context_failures = rar_issue_durability.validate_packet_folder(
            hidden_context_packet
        )
        if "supporting/context RAR issue candidate FAM006-RAR-044 missing" not in "\n".join(
            hidden_context_failures
        ):
            failures.append(
                "Generated RAR packet fixture allowed active copied-context candidate absent from primary decision surface"
            )

        copied_context_only_packet = temp_root / "copied-context-only" / "FAM-006"
        copied_context = copied_context_only_packet / "Source Truth Context"
        copied_context.mkdir(parents=True)
        (copied_context_only_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (copied_context / "COPIED_CONTEXT.md").write_text(
            table(row("FAM006-RAR-038")),
            encoding="utf-8",
        )
        copied_context_only_failures = rar_issue_durability.validate_packet_folder(
            copied_context_only_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            copied_context_only_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject issue-candidate table present only in Source Truth Context"
            )

        nested_review_aid_only_packet = temp_root / "nested-review-aid-only" / "FAM-006"
        nested_review_aid_user_review = (
            nested_review_aid_only_packet / "Review Aids" / "USER Review"
        )
        nested_review_aid_user_review.mkdir(parents=True)
        (nested_review_aid_only_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (nested_review_aid_user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-039")),
            encoding="utf-8",
        )
        nested_review_aid_only_failures = rar_issue_durability.validate_packet_folder(
            nested_review_aid_only_packet
        )
        if "primary USER decision surface missing" not in "\n".join(
            nested_review_aid_only_failures
        ):
            failures.append(
                "Generated RAR packet fixture allowed nested Review Aids/USER Review copy as a primary decision surface"
            )

        nested_context_only_packet = temp_root / "nested-context-only" / "FAM-006"
        nested_context_user_review = (
            nested_context_only_packet / "Source Truth Context" / "USER Review"
        )
        nested_context_user_review.mkdir(parents=True)
        (nested_context_only_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (nested_context_user_review / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-040")),
            encoding="utf-8",
        )
        nested_context_only_failures = rar_issue_durability.validate_packet_folder(
            nested_context_only_packet
        )
        if "primary USER decision surface missing" not in "\n".join(
            nested_context_only_failures
        ):
            failures.append(
                "Generated RAR packet fixture allowed nested Source Truth Context/USER Review copy as a primary decision surface"
            )

        primary_packet = packet_with_sections(
            temp_root / "primary",
            primary_text=table(row("FAM006-RAR-011")),
        )
        primary_failures = rar_issue_durability.validate_packet_folder(primary_packet)
        if primary_failures:
            failures.append(
                "Generated RAR packet fixture rejected a primary USER issue-candidate decision surface: "
                + "; ".join(primary_failures[:5])
            )

        malformed_review_aid_packet = packet_with_sections(
            temp_root / "malformed-review-aid-with-primary",
            primary_text=table(row("FAM006-RAR-057")),
            review_aid_text="\n".join(
                (
                    "Issue Candidate Decision Surface:",
                    "",
                    rar_issue_durability.DECISION_SURFACE_HEADER,
                    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| FAM006-RAR-058 | FAM-006 | HUD Dashboard | Window control cluster | Legacy close control diverges | Evidence with unescaped | pipe | ACTIVE_PENDING_USER_DECISION | YES | Owner FAM-006; reason current RAR gap; carrier FAM-006 RAR repair; trigger next RAR review | NONE - issue mutation not approved | Verified from RAR packet receipt 20260620 | USER must review repair, waiver, route, deferral, or approved GitHub issue creation. |",
                )
            ),
        )
        malformed_review_aid_failures = rar_issue_durability.validate_packet_folder(
            malformed_review_aid_packet
        )
        if "malformed supporting/context RAR issue candidate row" not in "\n".join(
            malformed_review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject malformed supporting Review Aids issue-candidate rows"
            )

        packeted_only_review_aid_packet = packet_with_sections(
            temp_root / "packeted-only-review-aid-with-primary",
            primary_text=table(row("FAM006-RAR-049")),
            review_aid_text=(
                "# RAR Review Aid\n\n"
                "The issue candidate was packeted only, so normal progression may continue."
            ),
        )
        packeted_only_review_aid_failures = rar_issue_durability.validate_packet_folder(
            packeted_only_review_aid_packet
        )
        if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
            packeted_only_review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject packeted-only closure wording in Review Aids when a primary table exists"
            )

        packeted_only_start_here_packet = packet_with_sections(
            temp_root / "packeted-only-start-here-with-primary",
            primary_text=table(row("FAM006-RAR-050")),
        )
        (packeted_only_start_here_packet / "START_HERE.md").write_text(
            "# START HERE\n\n"
            "Primary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n\n"
            "The RAR issue candidate packet was USER-reviewed and packeted only, so normal progression may continue.\n",
            encoding="utf-8",
        )
        packeted_only_start_here_failures = rar_issue_durability.validate_packet_folder(
            packeted_only_start_here_packet
        )
        if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
            packeted_only_start_here_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject packeted-only closure wording in START_HERE when a primary table exists"
            )

        hyphenated_packeted_only_start_here_packet = packet_with_sections(
            temp_root / "hyphenated-packeted-only-start-here-with-primary",
            primary_text=table(row("FAM006-RAR-070")),
        )
        (hyphenated_packeted_only_start_here_packet / "START_HERE.md").write_text(
            "# START HERE\n\n"
            "Primary USER review file: USER Review/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n\n"
            "The issue candidate was packeted-only, so normal progression may continue.\n",
            encoding="utf-8",
        )
        hyphenated_packeted_only_start_here_failures = rar_issue_durability.validate_packet_folder(
            hyphenated_packeted_only_start_here_packet
        )
        if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
            hyphenated_packeted_only_start_here_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject hyphenated packeted-only closure wording in START_HERE"
            )

        hyphenated_packet_reviewed_only_review_aid_packet = packet_with_sections(
            temp_root / "hyphenated-packet-reviewed-only-review-aid-with-primary",
            primary_text=table(row("FAM006-RAR-071")),
            review_aid_text=(
                "# RAR Review Aid\n\n"
                "This issue candidate is packet-reviewed-only and may continue without durable disposition."
            ),
        )
        hyphenated_packet_reviewed_only_review_aid_failures = (
            rar_issue_durability.validate_packet_folder(hyphenated_packet_reviewed_only_review_aid_packet)
        )
        if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
            hyphenated_packet_reviewed_only_review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject hyphenated packet-reviewed-only closure wording in Review Aids"
            )

        separator_packet_reviewed_only_review_aid_packet = packet_with_sections(
            temp_root / "separator-packet-reviewed-only-review-aid-with-primary",
            primary_text=table(row("FAM006-RAR-075")),
            review_aid_text=(
                "# RAR Review Aid\n\n"
                "This issue candidate is packet_reviewed_only and normal-progression may continue."
            ),
        )
        separator_packet_reviewed_only_review_aid_failures = (
            rar_issue_durability.validate_packet_folder(separator_packet_reviewed_only_review_aid_packet)
        )
        if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
            separator_packet_reviewed_only_review_aid_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject separator-normalized packet_reviewed_only closure wording"
            )

        active_repaired_packeted_only_packet = packet_with_sections(
            temp_root / "active-repaired-packeted-only-with-primary",
            primary_text=table(row("FAM006-RAR-061")),
            review_aid_text=(
                "# RAR Review Aid\n\n"
                "The candidate is repaired and replaced because it was packeted only, so progression may continue."
            ),
        )
        active_repaired_packeted_only_failures = rar_issue_durability.validate_packet_folder(
            active_repaired_packeted_only_packet
        )
        if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
            active_repaired_packeted_only_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject active repaired/replaced packeted-only closure wording"
            )

        active_not_durable_packeted_only_packet = packet_with_sections(
            temp_root / "active-not-durable-packeted-only-with-primary",
            primary_text=table(row("FAM006-RAR-062")),
            review_aid_text=(
                "# RAR Review Aid\n\n"
                "The issue candidate was packeted only and not durable, so normal progression may continue."
            ),
        )
        active_not_durable_packeted_only_failures = rar_issue_durability.validate_packet_folder(
            active_not_durable_packeted_only_packet
        )
        if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
            active_not_durable_packeted_only_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject active not-durable packeted-only closure wording"
            )

        historical_worded_packeted_only_closure_packet = packet_with_sections(
            temp_root / "historical-worded-packeted-only-closure-with-primary",
            primary_text=table(row("FAM006-RAR-065")),
            review_aid_text=(
                "# RAR Review Aid\n\n"
                "The issue candidate was previously packeted only, so normal progression may continue."
            ),
        )
        historical_worded_packeted_only_closure_failures = (
            rar_issue_durability.validate_packet_folder(
                historical_worded_packeted_only_closure_packet
            )
        )
        if EXPECTED_RAR_ISSUE_DURABILITY_FAILURE_SNIPPET not in "\n".join(
            historical_worded_packeted_only_closure_failures
        ):
            failures.append(
                "Generated RAR packet fixture did not reject historical-worded packeted-only progression closure"
            )

        routed_packet = temp_root / "routed-primary" / "FAM-006"
        routed_review = routed_packet / "Review Aids"
        routed_decisions = routed_packet / "Issue Decisions"
        routed_context = routed_packet / "Source Truth Context"
        routed_review.mkdir(parents=True)
        routed_decisions.mkdir(parents=True)
        routed_context.mkdir(parents=True)
        (routed_packet / "START_HERE.md").write_text(
            "# START HERE\n\nPrimary issue-candidate decision file: Issue Decisions/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (routed_decisions / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-034")),
            encoding="utf-8",
        )
        (routed_review / "RAR_ISSUE_CANDIDATE_REVIEW_AID.md").write_text(
            "# RAR Issue Candidate Review Aid\n\nSupporting narrative only; no active decision table.",
            encoding="utf-8",
        )
        (routed_context / "COPIED_CONTEXT.md").write_text(
            "# Copied Source Truth Context\n\nNo active issue-candidate decision surface lives in copied context.",
            encoding="utf-8",
        )
        routed_primary_failures = rar_issue_durability.validate_packet_folder(routed_packet)
        if routed_primary_failures:
            failures.append(
                "Generated RAR packet fixture rejected START_HERE-routed primary issue-candidate decision file: "
                + "; ".join(routed_primary_failures[:5])
            )

        legacy_ledger = temp_root / "legacy_ledger.md"
        legacy_ledger.write_text(
            "\n".join(
                (
                    "Legacy Issue Candidate Table:",
                    "",
                    rar_issue_durability.LEGACY_RAR_HEADER,
                    "| --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| FAM006-RAR-037 | FAM-006 | HUD Dashboard | Window control cluster | Legacy close control diverges from UIREF-002 | Legacy RAR row HUD-037 | Owner FAM-006 RAR repair | No |",
                )
            ),
            encoding="utf-8",
        )
        legacy_carried = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "legacy-carried",
                primary_text=table(row("FAM006-RAR-037")),
            ),
            external_ledger=legacy_ledger,
        )
        legacy_rows = rar_issue_durability.parse_external_candidate_rows(
            legacy_ledger.read_text(encoding="utf-8"),
            source=str(legacy_ledger),
        )
        if not legacy_rows or legacy_rows[0].github_issue != "NONE - issue mutation not approved":
            failures.append(
                "Generated RAR legacy import fixture did not preserve non-approved GitHub issue mutation state"
            )
        if legacy_carried:
            failures.append(
                "Generated RAR packet/ledger fixture rejected a recognized legacy external issue-candidate ledger carried into the primary packet: "
                + "; ".join(legacy_carried[:5])
            )

        legacy_approved_ledger = temp_root / "legacy_approved_ledger.md"
        legacy_approved_ledger.write_text(
            "\n".join(
                (
                    "Legacy Issue Candidate Table:",
                    "",
                    rar_issue_durability.LEGACY_RAR_HEADER,
                    "| --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| FAM006-RAR-080 | FAM-006 | HUD Dashboard | Window control cluster | Legacy close control diverges from UIREF-002 | Legacy RAR row HUD-080 | Owner FAM-006 RAR repair | Yes |",
                )
            ),
            encoding="utf-8",
        )
        legacy_approved_rows = rar_issue_durability.parse_external_candidate_rows(
            legacy_approved_ledger.read_text(encoding="utf-8"),
            source=str(legacy_approved_ledger),
        )
        if not legacy_approved_rows or legacy_approved_rows[0].github_issue != "PENDING":
            failures.append(
                "Generated RAR legacy import fixture did not preserve approved GitHub issue mutation state as PENDING"
            )

        malformed_legacy_ledger = temp_root / "malformed_legacy_ledger.md"
        malformed_legacy_ledger.write_text(
            "\n".join(
                (
                    "Legacy Issue Candidate Table:",
                    "",
                    rar_issue_durability.LEGACY_RAR_HEADER,
                    "| --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| FAM006-RAR-038 | FAM-006 | HUD Dashboard | Window control cluster | Legacy close control diverges | extra defect fragment | Legacy RAR row HUD-038 | Owner FAM-006 RAR repair | No |",
                )
            ),
            encoding="utf-8",
        )
        malformed_legacy_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "malformed-legacy-ledger",
                primary_text=table(row("FAM006-RAR-038")),
            ),
            external_ledger=malformed_legacy_ledger,
        )
        if "malformed external RAR issue candidate row" not in "\n".join(malformed_legacy_failures):
            failures.append(
                "Generated RAR packet/ledger fixture did not reject malformed legacy external issue-candidate rows"
            )

        blank_id_legacy_ledger = temp_root / "blank_id_legacy_ledger.md"
        blank_id_legacy_ledger.write_text(
            "\n".join(
                (
                    "Legacy Issue Candidate Table:",
                    "",
                    rar_issue_durability.LEGACY_RAR_HEADER,
                    "| --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| FAM006-RAR-084 | FAM-006 | HUD Dashboard | Window control cluster | Legacy close control diverges from UIREF-002 | Legacy RAR row HUD-084 | Owner FAM-006 RAR repair | No |",
                    "|  | FAM-006 | HUD Dashboard | Window control cluster | Blank candidate identifier should not disappear | Legacy RAR row HUD-BLANK | Owner FAM-006 RAR repair | No |",
                )
            ),
            encoding="utf-8",
        )
        blank_id_legacy_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "blank-id-legacy-ledger",
                primary_text=table(row("FAM006-RAR-084")),
            ),
            external_ledger=blank_id_legacy_ledger,
        )
        if "malformed external RAR issue candidate row" not in "\n".join(
            blank_id_legacy_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture allowed blank-ID legacy external issue-candidate rows to disappear"
            )

        incidental_mention_ledger = temp_root / "incidental_mention_ledger.md"
        incidental_mention_ledger.write_text(table(row("FAM006-RAR-039")), encoding="utf-8")
        incidental_mention_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "incidental-mention",
                primary_text=(
                    "Narrative note mentions FAM006-RAR-039, but the active decision row below is different.\n\n"
                    + table(row("FAM006-RAR-999"))
                ),
            ),
            external_ledger=incidental_mention_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-039 missing" not in "\n".join(
            incidental_mention_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture allowed incidental text mention to satisfy active candidate carry-forward"
            )

        incidental_lineage_ledger = temp_root / "incidental_lineage_ledger.md"
        incidental_lineage_ledger.write_text(table(row("FAM006-RAR-059")), encoding="utf-8")
        incidental_lineage_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "incidental-lineage",
                primary_text=(
                    "Lineage note: predecessor FAM006-RAR-059 remains under review.\n\n"
                    + table(row("FAM006-RAR-999"))
                ),
            ),
            external_ledger=incidental_lineage_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-059 missing" not in "\n".join(
            incidental_lineage_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture allowed incidental lineage prose without a current successor row"
            )

        ambiguous_directional_lineage_ledger = temp_root / "ambiguous_directional_lineage_ledger.md"
        ambiguous_directional_lineage_ledger.write_text(table(row("FAM006-RAR-066")), encoding="utf-8")
        ambiguous_directional_lineage_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "ambiguous-directional-lineage",
                primary_text=(
                    "Lineage note: predecessor FAM006-RAR-066 remains under review alongside FAM006-RAR-999.\n\n"
                    + table(row("FAM006-RAR-999"))
                ),
            ),
            external_ledger=ambiguous_directional_lineage_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-066 missing" not in "\n".join(
            ambiguous_directional_lineage_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture allowed ambiguous predecessor prose without a directional successor mapping"
            )

        unrelated_current_lineage_ledger = temp_root / "unrelated_current_lineage_ledger.md"
        unrelated_current_lineage_ledger.write_text(table(row("FAM006-RAR-069")), encoding="utf-8")
        unrelated_current_lineage_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "unrelated-current-lineage",
                primary_text=(
                    "Lineage note: predecessor FAM006-RAR-069 remains under review while unrelated current row "
                    "FAM006-RAR-999 is reviewed separately.\n\n"
                    + table(row("FAM006-RAR-999"))
                ),
            ),
            external_ledger=unrelated_current_lineage_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-069 missing" not in "\n".join(
            unrelated_current_lineage_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture allowed unrelated current-row lineage prose without a directional successor mapping"
            )

        directional_lineage_ledger = temp_root / "directional_lineage_ledger.md"
        directional_lineage_ledger.write_text(table(row("FAM006-RAR-067")), encoding="utf-8")
        directional_lineage_carried = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "directional-lineage-carried",
                primary_text=(
                    table(row("FAM006-RAR-067-A"))
                    + "\n\nLineage: successor FAM006-RAR-067-A replaces predecessor FAM006-RAR-067."
                ),
            ),
            external_ledger=directional_lineage_ledger,
        )
        if directional_lineage_carried:
            failures.append(
                "Generated RAR packet/ledger fixture rejected explicit directional successor/predecessor lineage: "
                + "; ".join(directional_lineage_carried[:5])
            )

        windows_routed_primary_packet = temp_root / "windows-routed-primary" / "FAM-006"
        windows_issue_decisions = windows_routed_primary_packet / "Issue Decisions"
        windows_issue_decisions.mkdir(parents=True)
        (windows_routed_primary_packet / "START_HERE.md").write_text(
            "# START HERE\n\n"
            "Primary issue candidate decision file: Issue Decisions\\RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md\n",
            encoding="utf-8",
        )
        (windows_issue_decisions / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-078")),
            encoding="utf-8",
        )
        windows_routed_primary_failures = rar_issue_durability.validate_packet_folder(
            windows_routed_primary_packet
        )
        if windows_routed_primary_failures:
            failures.append(
                "Generated RAR packet fixture rejected START_HERE Windows-separator routed primary issue decision file: "
                + "; ".join(windows_routed_primary_failures[:5])
            )

        negated_routed_primary_packet = temp_root / "negated-routed-primary" / "FAM-006"
        negated_issue_decisions = negated_routed_primary_packet / "Issue Decisions"
        negated_issue_decisions.mkdir(parents=True)
        (negated_routed_primary_packet / "START_HERE.md").write_text(
            "# START HERE\n\n"
            "Do not use Issue Decisions/RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md as the primary decision file.\n",
            encoding="utf-8",
        )
        (negated_issue_decisions / "RAR_ISSUE_CANDIDATE_DECISION_SURFACE.md").write_text(
            table(row("FAM006-RAR-081")),
            encoding="utf-8",
        )
        negated_routed_primary_failures = rar_issue_durability.validate_packet_folder(
            negated_routed_primary_packet
        )
        if "Issue Candidate Table Only In Copied Context" not in "\n".join(
            negated_routed_primary_failures
        ):
            failures.append(
                "Generated RAR packet fixture allowed negated START_HERE issue-candidate route as the primary decision file"
            )

        negated_lineage_ledger = temp_root / "negated_lineage_ledger.md"
        negated_lineage_ledger.write_text(table(row("FAM006-RAR-067")), encoding="utf-8")
        negated_lineage_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "negated-lineage",
                primary_text=(
                    table(row("FAM006-RAR-999"))
                    + "\n\nLineage: successor FAM006-RAR-999 is not a replacement for predecessor FAM006-RAR-067."
                ),
            ),
            external_ledger=negated_lineage_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-067 missing" not in "\n".join(
            negated_lineage_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture allowed negated successor/predecessor lineage to carry an external candidate"
            )

        same_id_different_lineage_ledger = temp_root / "same_id_different_lineage_ledger.md"
        same_id_different_lineage_ledger.write_text(table(row("FAM006-RAR-045")), encoding="utf-8")
        same_id_different_lineage_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "same-id-different-lineage",
                primary_text=table(
                    "| FAM006-RAR-045 | FAM-006 | Log Viewer Studio | Status row | Folder status mismatch | RAR contact sheet row LOG-STATUS-045 | ACTIVE_PENDING_USER_DECISION | YES | Owner FAM-006; reason current RAR adoption gap; carrier FAM-006 RAR repair; trigger next RAR review | NONE - issue mutation not approved | Verified from RAR packet receipt 20260620 | USER must review repair, waiver with reason and scope, route, deferral, or approved GitHub issue creation. |"
                ),
            ),
            external_ledger=same_id_different_lineage_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-045 missing" not in "\n".join(
            same_id_different_lineage_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture allowed same candidate ID with different surface/element/defect lineage"
            )

        legacy_duplicate_lineage_ledger = temp_root / "legacy_duplicate_lineage_ledger.md"
        legacy_duplicate_lineage_ledger.write_text(
            "\n".join(
                (
                    "Legacy Issue Candidate Table:",
                    "",
                    rar_issue_durability.LEGACY_RAR_HEADER,
                    "| --- | --- | --- | --- | --- | --- | --- | --- |",
                    "| FAM006-RAR-068 | FAM-006 | HUD Dashboard | Window control cluster | Legacy close control diverges from UIREF-002 | Legacy RAR row HUD-068 | Owner FAM-006 RAR repair | No |",
                    "| FAM006-RAR-068 | FAM-006 | Log Viewer Studio | Status row | Folder status mismatch | Legacy RAR row LOG-068 | Owner FAM-006 RAR repair | No |",
                )
            ),
            encoding="utf-8",
        )
        legacy_duplicate_lineage_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "legacy-duplicate-lineage-missing",
                primary_text=table(row("FAM006-RAR-068")),
            ),
            external_ledger=legacy_duplicate_lineage_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-068 missing" not in "\n".join(
            legacy_duplicate_lineage_failures
        ):
            failures.append(
                "Generated RAR packet/ledger fixture allowed one same-ID legacy row to hide a second same-ID different-lineage row"
            )

        terminal_ledger = temp_root / "terminal_ledger.md"
        terminal_ledger.write_text(
            table(
                row(
                    "FAM006-RAR-012",
                    disposition="REPAIRED_VERIFIED",
                    blocking="NO",
                    carrier="Owner FAM-006; reason fixed in repair; carrier FAM-006 LV proof; trigger regression only",
                    decision="Independent verification revalidated the repair; no current USER decision is needed.",
                )
            ),
            encoding="utf-8",
        )
        terminal_absent_failures = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "terminal-absent",
                primary_text=table(row("FAM006-RAR-013")),
            ),
            external_ledger=terminal_ledger,
        )
        if terminal_absent_failures:
            failures.append(
                "Generated RAR terminal-lineage fixture forced a repaired terminal candidate into a later packet: "
                + "; ".join(terminal_absent_failures[:5])
            )

        renamed_ledger = temp_root / "renamed_ledger.md"
        renamed_ledger.write_text(table(row("FAM006-RAR-014")), encoding="utf-8")
        renamed_no_lineage = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "renamed-no-lineage",
                primary_text=table(row("FAM006-RAR-014A")),
            ),
            external_ledger=renamed_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-014 missing" not in "\n".join(
            renamed_no_lineage
        ):
            failures.append(
                "Generated RAR renamed-candidate fixture did not reject rename/regroup without lineage"
            )
        renamed_with_lineage = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "renamed-with-lineage",
                primary_text=(
                    table(row("FAM006-RAR-014A"))
                    + "\n\nLineage: successor FAM006-RAR-014A replaces predecessor FAM006-RAR-014."
                ),
            ),
            external_ledger=renamed_ledger,
        )
        if renamed_with_lineage:
            failures.append(
                "Generated RAR renamed-candidate fixture rejected explicit predecessor/successor lineage: "
                + "; ".join(renamed_with_lineage[:5])
            )

        suffix_renamed_ledger = temp_root / "suffix_renamed_ledger.md"
        suffix_renamed_ledger.write_text(table(row("FAM006-RAR-015")), encoding="utf-8")
        suffix_renamed_no_predecessor = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "suffix-renamed-no-predecessor",
                primary_text=(
                    table(row("FAM006-RAR-015-A"))
                    + "\n\nLineage: successor FAM006-RAR-015-A is ready for review."
                ),
            ),
            external_ledger=suffix_renamed_ledger,
        )
        if "external RAR issue candidate FAM006-RAR-015 missing" not in "\n".join(
            suffix_renamed_no_predecessor
        ):
            failures.append(
                "Generated RAR suffix-renamed fixture allowed substring lineage without exact predecessor candidate ID"
            )
        suffix_renamed_with_lineage = rar_issue_durability.validate_packet_folder(
            packet_with_sections(
                temp_root / "suffix-renamed-with-lineage",
                primary_text=(
                    table(row("FAM006-RAR-015-A"))
                    + "\n\nLineage: successor FAM006-RAR-015-A replaces predecessor FAM006-RAR-015."
                ),
            ),
            external_ledger=suffix_renamed_ledger,
        )
        if suffix_renamed_with_lineage:
            failures.append(
                "Generated RAR suffix-renamed fixture rejected explicit predecessor/successor lineage: "
                + "; ".join(suffix_renamed_with_lineage[:5])
            )

    historical_packeted_only_text = (
        "# Historical packeted-only repair\n\n"
        "Prior invalid state was packeted only and not durable.\n\n"
        + table(row("FAM006-RAR-020"))
    )
    historical_packeted_only_failures = rar_issue_durability.validate_text(
        historical_packeted_only_text,
        source="generated historical packeted-only RAR",
    )
    if historical_packeted_only_failures:
        failures.append(
            "Generated RAR historical packeted-only fixture was falsely rejected: "
            + "; ".join(historical_packeted_only_failures[:5])
        )

    hyphenated_issue_candidate_missing_surface = rar_issue_durability.validate_text(
        "# RAR issue-candidate summary\n\nIssue-Candidate Table: FAM006-RAR-030 pending USER decision.",
        source="generated hyphenated issue-candidate missing table",
    )
    if "Issue Candidate Decision Surface Missing" not in "\n".join(
        hyphenated_issue_candidate_missing_surface
    ):
        failures.append(
            "Generated RAR fixture did not reject hyphenated issue-candidate mention without decision table"
        )

    plural_issue_candidates_missing_surface = rar_issue_durability.validate_text(
        "# RAR issue-candidates summary\n\nIssue-candidates FAM006-RAR-030 and FAM006-RAR-031 are pending USER decision.",
        source="generated plural issue-candidates missing table",
    )
    if "Issue Candidate Decision Surface Missing" not in "\n".join(
        plural_issue_candidates_missing_surface
    ):
        failures.append(
            "Generated RAR fixture did not reject plural issue-candidates mention without decision table"
        )

    no_issue_candidate_applicable = rar_issue_durability.validate_text(
        "# RAR no-impact summary\n\nNo issue candidate is applicable for this RAR review.",
        source="generated no issue candidate applicable",
    )
    if no_issue_candidate_applicable:
        failures.append(
            "Generated RAR fixture rejected explicit no issue candidate applicable wording: "
            + "; ".join(no_issue_candidate_applicable[:5])
        )

    no_issue_candidates_applicable = rar_issue_durability.validate_text(
        "# RAR no-impact summary\n\nNo issue candidates are applicable for this RAR review.",
        source="generated no issue candidates applicable",
    )
    if no_issue_candidates_applicable:
        failures.append(
            "Generated RAR fixture rejected explicit no issue candidates applicable wording: "
            + "; ".join(no_issue_candidates_applicable[:5])
        )

    no_candidate_with_concrete_id = rar_issue_durability.validate_text(
        "# RAR issue-candidate summary\n\nNo issue candidates are applicable, but Issue Candidate FAM006-RAR-090 remains pending USER disposition.",
        source="generated no-candidate wording with concrete candidate ID",
    )
    if "Issue Candidate Decision Surface Missing" not in "\n".join(
        no_candidate_with_concrete_id
    ):
        failures.append(
            "Generated RAR fixture let no-candidate wording hide a concrete issue candidate ID"
        )

    waiver_without_reason = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-021",
                disposition="USER_WAIVED_WITH_REASON",
                blocking="NO",
                carrier="Owner FAM-006; scope HUD Dashboard only; trigger reopened HUD work",
                decision="USER waived this item.",
            )
        ),
        source="generated waiver missing reason",
    )
    if "USER rejection/waiver requires reason" not in "\n".join(waiver_without_reason):
        failures.append("Generated RAR fixture did not reject USER waiver without reason")

    rejection_without_reason = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-022",
                disposition="USER_REJECTED_WITH_REASON",
                blocking="NO",
                carrier="Owner FAM-006; trigger reopened HUD work",
                decision="USER rejected this item.",
            )
        ),
        source="generated rejection missing reason",
    )
    if "USER rejection/waiver requires reason" not in "\n".join(rejection_without_reason):
        failures.append("Generated RAR fixture did not reject USER rejection without reason")

    waiver_with_negated_reason_scope = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-085",
                disposition="USER_WAIVED_WITH_REASON",
                blocking="NO",
                carrier="Owner FAM-006; no reason was recorded; no scope was approved.",
                decision="USER waiver record is incomplete and cannot close this candidate.",
            )
        ),
        source="generated waiver negated reason and scope",
    )
    waiver_with_negated_failures = "\n".join(waiver_with_negated_reason_scope)
    if (
        "USER rejection/waiver requires reason" not in waiver_with_negated_failures
        or "USER waiver requires scope" not in waiver_with_negated_failures
    ):
        failures.append(
            "Generated RAR fixture did not reject USER waiver with negated reason/scope language"
        )

    terminal_blocking_failure = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-028",
                disposition="USER_REJECTED_WITH_REASON",
                blocking="YES",
                carrier="Owner FAM-006; reason USER rejected this repair route; trigger replacement option review",
                decision="USER rejected this item because the proposed issue route was wrong.",
            )
        ),
        source="generated terminal disposition still blocking",
    )
    if "terminal disposition cannot remain progression blocking" not in "\n".join(
        terminal_blocking_failure
    ):
        failures.append(
            "Generated RAR fixture did not reject terminal disposition rows that still block progression"
        )

    routed_negated_receipt = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-029",
                disposition="ROUTED_TO_LEGAL_CARRIER",
                blocking="NO",
                carrier="Target FAM-006 branch not accepted; no receipt yet.",
                decision="No current USER decision because routing is proposed but carrier acceptance receipt is pending.",
            )
        ),
        source="generated routed disposition negated receipt",
    )
    if "routed disposition requires carrier acceptance/receipt" not in "\n".join(
        routed_negated_receipt
    ):
        failures.append("Generated RAR fixture did not reject routed disposition with negated receipt language")

    routed_approved_without_carrier_receipt = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-072",
                disposition="ROUTED_TO_LEGAL_CARRIER",
                blocking="NO",
                carrier="USER approved routing to FAM-006.",
                decision="No current USER decision because routing approval exists but carrier acceptance has not been recorded.",
            )
        ),
        source="generated routed disposition approved without carrier receipt",
    )
    if "routed disposition requires carrier acceptance/receipt" not in "\n".join(
        routed_approved_without_carrier_receipt
    ):
        failures.append("Generated RAR fixture did not reject routed disposition with approval but no carrier receipt")

    routed_awaiting_receipt = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-073",
                disposition="ROUTED_TO_LEGAL_CARRIER",
                blocking="NO",
                carrier="Routed to FAM-006 and awaiting carrier acceptance receipt.",
                decision="No current USER decision because the target carrier receipt remains pending.",
            )
        ),
        source="generated routed disposition awaiting receipt",
    )
    if "routed disposition requires carrier acceptance/receipt" not in "\n".join(routed_awaiting_receipt):
        failures.append("Generated RAR fixture did not reject routed disposition awaiting receipt")

    deferred_negated_owner = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-086",
                disposition="DEFERRED_WITH_OWNER",
                blocking="NO",
                carrier="No owner assigned; reason backlog; trigger next review.",
                decision="Candidate remains deferred, but durable ownership has not been recorded.",
            )
        ),
        source="generated deferred disposition negated owner",
    )
    if "deferred disposition requires durable owner" not in "\n".join(
        deferred_negated_owner
    ):
        failures.append("Generated RAR fixture did not reject deferred disposition with negated owner")

    active_carry_forward_negated_owner = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-087",
                disposition="ACTIVE_PENDING_USER_DECISION",
                blocking="NO",
                carrier="No owner assigned; reason current RAR adoption gap; carrier FAM-006 RAR repair; trigger next RAR review.",
                decision="USER still needs a decision, but this record has no durable owner.",
            )
        ),
        source="generated active carry-forward negated owner",
    )
    if "non-blocking active carry-forward requires" not in "\n".join(
        active_carry_forward_negated_owner
    ):
        failures.append(
            "Generated RAR fixture did not reject non-blocking active carry-forward with negated owner"
        )

    placeholder_required_fields = rar_issue_durability.validate_text(
        table(
            "| FAM006-RAR-075 | UNKNOWN | TBD | Window control cluster | UNKNOWN | "
            "RAR contact sheet row HUD-CTRL-075 | ACTIVE_PENDING_USER_DECISION | YES | "
            "Owner FAM-006; reason current RAR adoption gap; carrier FAM-006 RAR repair; trigger next RAR review | "
            "NONE - issue mutation not approved | Verified from RAR packet receipt 20260620 | "
            "USER must review repair, waiver with reason and scope, route, deferral, or approved GitHub issue creation. |"
        ),
        source="generated placeholder required fields",
    )
    placeholder_required_failures = "\n".join(placeholder_required_fields)
    if (
        "Owning FAM missing" not in placeholder_required_failures
        or "Surface missing" not in placeholder_required_failures
        or "Defect missing" not in placeholder_required_failures
    ):
        failures.append("Generated RAR fixture did not reject placeholder required fields")

    escaped_pipe_valid = rar_issue_durability.validate_text(
        table(
            "| FAM006-RAR-079 | FAM-006 | HUD Dashboard | Status row | "
            "PASS \\| FAIL label comparison must remain one cell | "
            "RAR contact sheet row HUD-PIPE-079 | ACTIVE_PENDING_USER_DECISION | YES | "
            "Owner FAM-006; reason current RAR adoption gap; carrier FAM-006 RAR repair; trigger next RAR review | "
            "NONE - issue mutation not approved | Verified from RAR packet receipt 20260620 | "
            "USER must review repair, waiver with reason and scope, route, deferral, or approved GitHub issue creation. |"
        ),
        source="generated escaped-pipe valid row",
    )
    if escaped_pipe_valid:
        failures.append(
            "Generated RAR fixture rejected escaped Markdown pipe inside a valid issue-candidate cell: "
            + "; ".join(escaped_pipe_valid[:5])
        )

    stale_verified_from_helper = rar_issue_durability.validate_text(
        table(
            "| FAM006-RAR-082 | FAM-006 | HUD Dashboard | Window control cluster | "
            "Legacy close control diverges from UIREF-002 | RAR contact sheet row HUD-CTRL-082 | "
            "ACTIVE_PENDING_USER_DECISION | YES | "
            "Owner FAM-006; reason current RAR adoption gap; carrier FAM-006 RAR repair; trigger next RAR review | "
            "NONE - issue mutation not approved | Verified from helper output | "
            "USER must review repair, waiver with reason and scope, route, deferral, or approved GitHub issue creation. |"
        ),
        source="generated stale helper-output freshness text",
    )
    if "Last Verified requires dated or receipt-based freshness evidence" not in "\n".join(
        stale_verified_from_helper
    ):
        failures.append(
            "Generated RAR fixture did not reject undated helper-output freshness wording"
        )

    stale_verified_from_notes = rar_issue_durability.validate_text(
        table(
            "| FAM006-RAR-083 | FAM-006 | HUD Dashboard | Window control cluster | "
            "Legacy close control diverges from UIREF-002 | RAR contact sheet row HUD-CTRL-083 | "
            "ACTIVE_PENDING_USER_DECISION | YES | "
            "Owner FAM-006; reason current RAR adoption gap; carrier FAM-006 RAR repair; trigger next RAR review | "
            "NONE - issue mutation not approved | Verified from old notes | "
            "USER must review repair, waiver with reason and scope, route, deferral, or approved GitHub issue creation. |"
        ),
        source="generated stale notes freshness text",
    )
    if "Last Verified requires dated or receipt-based freshness evidence" not in "\n".join(
        stale_verified_from_notes
    ):
        failures.append(
            "Generated RAR fixture did not reject undated old-notes freshness wording"
        )

    github_creation_approved_receipt = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-076",
                disposition="GITHUB_CREATION_APPROVED_PENDING",
                blocking="YES",
                github_issue="PENDING",
                carrier="USER approved GitHub issue creation; approval receipt recorded in RAR3 packet 20260620.",
                decision="Issue mutation remains pending execution until the approved GitHub action is performed.",
            )
        ),
        source="generated GitHub creation pending with completed approval receipt",
    )
    if github_creation_approved_receipt:
        failures.append(
            "Generated RAR fixture falsely rejected GitHub issue creation with completed USER approval receipt: "
            + "; ".join(github_creation_approved_receipt[:5])
        )

    github_creation_not_approved = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-074",
                disposition="GITHUB_CREATION_APPROVED_PENDING",
                blocking="YES",
                github_issue="PENDING",
                carrier="Issue creation is not approved; no USER approval receipt yet.",
                decision="No issue mutation may occur because approval is missing.",
            )
        ),
        source="generated GitHub creation pending without positive approval",
    )
    if "approved issue creation requires USER approval receipt" not in "\n".join(
        github_creation_not_approved
    ):
        failures.append("Generated RAR fixture did not reject GitHub issue creation pending without positive approval")

    github_creation_future_approval = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-077",
                disposition="GITHUB_CREATION_APPROVED_PENDING",
                blocking="YES",
                github_issue="PENDING",
                carrier="Approval planned after USER review; USER approval will be requested later.",
                decision="GitHub issue mutation is expected later but not approved now.",
            )
        ),
        source="generated GitHub creation pending with future approval wording",
    )
    if "approved issue creation requires USER approval receipt" not in "\n".join(
        github_creation_future_approval
    ):
        failures.append("Generated RAR fixture did not reject future approval wording for GitHub issue creation")

    repaired_negated_verification = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-088",
                disposition="REPAIRED_VERIFIED",
                blocking="NO",
                carrier="Owner FAM-006; reason repair claimed; carrier FAM-006 RAR repair; trigger regression only",
                decision="The repair is not independently verified.",
            )
        ),
        source="generated repaired disposition negated verification",
    )
    if "repaired disposition requires independent verification evidence" not in "\n".join(
        repaired_negated_verification
    ):
        failures.append(
            "Generated RAR fixture did not reject repaired disposition with negated verification"
        )

    no_decision_negated_verification = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-090",
                disposition="REPAIRED_VERIFIED",
                blocking="NO",
                carrier="Owner FAM-006; reason repair claimed; carrier FAM-006 RAR repair; trigger regression only",
                decision="No current USER decision is needed because the repair is not independently verified.",
            )
        ),
        source="generated no-decision repaired disposition negated verification",
    )
    if "repaired disposition requires independent verification evidence" not in "\n".join(
        no_decision_negated_verification
    ):
        failures.append(
            "Generated RAR fixture did not reject no-decision wording with negated verification"
        )

    closed_issue_negated_verification = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-089",
                disposition="MAPPED_CLOSED_GITHUB_ISSUE_RECONCILED",
                blocking="NO",
                github_issue="#275",
                carrier="Owner FAM-006; reason issue closed; carrier GitHub issue #275; trigger regression only",
                decision="The closed issue reconciliation is not independently verified.",
            )
        ),
        source="generated closed issue mapping negated verification",
        github_snapshot=snapshot("CLOSED"),
    )
    if "closed GitHub issue mapping requires independent repair/reconciliation evidence" not in "\n".join(
        closed_issue_negated_verification
    ):
        failures.append(
            "Generated RAR fixture did not reject closed issue mapping with negated verification"
        )

    nonblocking_missing_fields = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-023",
                disposition="DEFERRED_WITH_OWNER",
                blocking="NO",
                carrier="Owner FAM-006; reason waits for later work",
                decision="USER decision is not needed now.",
            )
        ),
        source="generated nonblocking missing carry-forward fields",
    )
    if "non-blocking active carry-forward requires" not in "\n".join(
        nonblocking_missing_fields
    ):
        failures.append(
            "Generated RAR fixture did not reject non-blocking active carry-forward missing carrier/trigger"
        )

    mapped_open_snapshot_closed = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-024",
                disposition="MAPPED_OPEN_GITHUB_ISSUE",
                blocking="NO",
                github_issue="#275",
                carrier="Owner FAM-006; reason issue remains open; carrier GitHub issue #275; trigger issue closeout review",
                decision="Track through open issue #275; owner FAM-006 reviews on trigger when issue closes.",
            )
        ),
        source="generated open mapping closed snapshot",
        github_snapshot=snapshot("CLOSED"),
    )
    if "RAR GitHub Issue Mapping Stale" not in "\n".join(mapped_open_snapshot_closed):
        failures.append(
            "Generated RAR GitHub fixture did not reject mapped-open candidate when snapshot is closed"
        )

    mapped_closed_snapshot_open = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-025",
                disposition="MAPPED_CLOSED_GITHUB_ISSUE_RECONCILED",
                blocking="NO",
                github_issue="#275",
                carrier="Owner FAM-006; reason issue closed; carrier GitHub issue #275; trigger regression only",
                decision="Independent repair evidence verified and reconciled the closed GitHub issue.",
            )
        ),
        source="generated closed mapping open snapshot",
        github_snapshot=snapshot("OPEN"),
    )
    if "RAR GitHub Issue Mapping Stale" not in "\n".join(mapped_closed_snapshot_open):
        failures.append(
            "Generated RAR GitHub fixture did not reject mapped-closed candidate when snapshot is open"
        )

    mapped_open_prefixed_issue_number = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-027",
                disposition="MAPPED_OPEN_GITHUB_ISSUE",
                blocking="NO",
                github_issue="FAM-006 GitHub issue #275",
                carrier="Owner FAM-006; reason issue remains open; carrier GitHub issue #275; trigger issue closeout review",
                decision="Track through open issue #275; owner FAM-006 reviews on trigger when issue closes.",
            )
        ),
        source="generated open mapping prefixed issue number",
        github_snapshot=snapshot("OPEN"),
    )
    if mapped_open_prefixed_issue_number:
        failures.append(
            "Generated RAR GitHub fixture rejected a # issue number when an earlier FAM number was present: "
            + "; ".join(mapped_open_prefixed_issue_number[:5])
        )

    with tempfile.TemporaryDirectory() as snapshot_temp_dir:
        raw_github_snapshot_path = Path(snapshot_temp_dir) / "github_snapshot_updated_at.json"
        raw_github_snapshot_path.write_text(
            json.dumps(
                {
                    "275": {
                        "state": "OPEN",
                        "updatedAt": "2026-06-25T10:20:30Z",
                        "source": "gh issue view 275 --json state,updatedAt",
                    }
                }
            ),
            encoding="utf-8",
        )
        raw_github_snapshot = rar_issue_durability.load_github_snapshot(raw_github_snapshot_path)
        mapped_open_updated_at_snapshot = rar_issue_durability.validate_text(
            table(
                row(
                    "FAM006-RAR-029",
                    disposition="MAPPED_OPEN_GITHUB_ISSUE",
                    blocking="NO",
                    github_issue="#275",
                    carrier="Owner FAM-006; reason issue remains open; carrier GitHub issue #275; trigger issue closeout review",
                    decision="Track through open issue #275; owner FAM-006 reviews on trigger when issue closes.",
                )
            ),
            source="generated open mapping raw updatedAt snapshot",
            github_snapshot=raw_github_snapshot,
        )
        if mapped_open_updated_at_snapshot:
            failures.append(
                "Generated RAR GitHub fixture rejected gh issue view state/updatedAt snapshot freshness: "
                + "; ".join(mapped_open_updated_at_snapshot[:5])
            )

    mapped_closed_snapshot_closed = rar_issue_durability.validate_text(
        table(
            row(
                "FAM006-RAR-026",
                disposition="MAPPED_CLOSED_GITHUB_ISSUE_RECONCILED",
                blocking="NO",
                github_issue="#275",
                carrier="Owner FAM-006; reason issue closed; carrier GitHub issue #275; trigger regression only",
                decision="Independent repair evidence verified and reconciled the closed GitHub issue.",
            )
        ),
        source="generated closed mapping closed snapshot",
        github_snapshot=snapshot("CLOSED"),
    )
    if mapped_closed_snapshot_closed:
        failures.append(
            "Generated RAR GitHub fixture rejected closed mapping with closed snapshot plus independent reconciliation: "
            + "; ".join(mapped_closed_snapshot_closed[:5])
        )

    return failures


def validate() -> list[str]:
    failures: list[str] = []
    for fixture in (
        SHALLOW_FIXTURE,
        CONCRETE_FIXTURE,
        VALID_BRANCH_RUNTIME_PLAN_FIXTURE,
        SHALLOW_BRANCH_RUNTIME_PLAN_FIXTURE,
        BACKLOG_SPRAWL_FIXTURE,
        FOLD_DOWN_FIXTURE,
        VALID_BRANCH_VISION_CONTRACT_FIXTURE,
        INVALID_PROPOSED_BRANCH_VISION_CONTRACT_FIXTURE,
        INVALID_BLOCKING_BRANCH_VISION_CONTRACT_FIXTURE,
        VALID_USER_FEEDBACK_DISPOSITION_FIXTURE,
        VALID_USER_FEEDBACK_UNICODE_SUMMARY_FIXTURE,
        INVALID_USER_FEEDBACK_NO_OWNER_FIXTURE,
        INVALID_USER_FEEDBACK_BAD_ID_FIXTURE,
        INVALID_USER_FEEDBACK_DUPLICATE_SUMMARY_FIXTURE,
        VALID_REBASELINE_OVERLAP_INTENT_FIXTURE,
        INVALID_REBASELINE_OVERLAP_UNKNOWN_HIGH_RISK_FIXTURE,
        INVALID_REBASELINE_OVERLAP_FALLBACK_ONLY_PASS_FIXTURE,
        VALID_REBASELINE_OVERLAP_LOW_RISK_WARN_FIXTURE,
        INVALID_REBASELINE_OVERLAP_FIXTURE_HIGH_IMPACT_FIXTURE,
        VALID_REBASELINE_OVERLAP_FIXTURE_LOW_IMPACT_FIXTURE,
        VALID_ELEMENT_TO_PHASE_MATRIX_FIXTURE,
        INVALID_ELEMENT_TO_PHASE_MISSING_HARDENING_FIXTURE,
        INVALID_ELEMENT_TO_PHASE_MISSING_LIVE_VALIDATION_FIXTURE,
        VALID_ELEMENT_TO_PHASE_DEFERRED_FUTURE_FIXTURE,
        INVALID_ELEMENT_TO_PHASE_DUPLICATE_ID_FIXTURE,
        VALID_WORKSTREAM_ENTRY_WHOLE_PACKAGE_FIXTURE,
        INVALID_WORKSTREAM_ENTRY_FIRST_SEAM_ONLY_FIXTURE,
        VALID_USER_BRANCH_PLAN_REVIEW_FIXTURE,
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_OUTCOME_FIXTURE,
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_PACKET_FINDING_FIXTURE,
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_HARDENING_FIXTURE,
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_LIVE_VALIDATION_FIXTURE,
        INVALID_USER_BRANCH_PLAN_REVIEW_FIRST_SEAM_ONLY_FIXTURE,
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_RESPONSE_DIGEST_FIXTURE,
        VALID_USER_BRANCH_PLAN_REVIEW_DEFERRED_SCOPE_FIXTURE,
        VALID_BRANCH_PLANNING_GATE_STATE_FIXTURE,
        INVALID_BRANCH_PLANNING_GATE_BYPASS_FIXTURE,
        VALID_BP1_BRANCH_VISION_REVIEW_FIXTURE,
        VALID_BP1_FAM006_DOGFOOD_FIXTURE,
        VALID_BP1_FAM007_DOGFOOD_FIXTURE,
        VALID_BP1_GOVERNANCE_DOGFOOD_FIXTURE,
        INVALID_BP1_MISSING_CONTEXT_FIXTURE,
        INVALID_BP1_SHALLOW_RECOMMENDATIONS_FIXTURE,
        INVALID_BP1_TEMPLATE_SHELL_FIXTURE,
        INVALID_BP1_PROCESS_MECHANICS_FIXTURE,
        INVALID_BP1_COPIED_FILE_SURFACE_ONLY_FIXTURE,
        INVALID_BP1_GENERIC_USER_QUESTIONS_FIXTURE,
        INVALID_BP1_SLC_CENTERED_FIXTURE,
        INVALID_BP1_TECHNICAL_METADATA_FIXTURE,
        INVALID_RUNTIME_FOCUS_ISSUE_ANCHORED_SELECTION_FIXTURE,
        INVALID_BP2_MISSING_ACCEPTED_BP1_TRACE_FIXTURE,
        VALID_BP2_FAM006_DOGFOOD_FIXTURE,
        VALID_BP2_FAM007_DOGFOOD_FIXTURE,
        INVALID_BP3_IMPLEMENTATION_WITH_PENDING_BP1_BP2_FIXTURE,
        VALID_BP3_ACCEPTED_BP1_BP2_SLC_TRACE_FIXTURE,
        VALID_BP3_FAM006_DOGFOOD_FIXTURE,
        VALID_BP3_FAM007_DOGFOOD_FIXTURE,
        INVALID_IMPLEMENTATION_ROUTE_PLANNING_ONLY_FIXTURE,
        VALID_IMPLEMENTATION_ROUTE_SECURITY_BOUNDARY_FIXTURE,
        VALID_BR2_ROUTE_BLOCKER_PACKET_FIXTURE,
        INVALID_BR2_ROUTE_BLOCKER_NO_ROUTE_CONTINUE_FIXTURE,
        INVALID_IMPLEMENTATION_ROUTE_FAKE_FEATURE_LABEL_FIXTURE,
        VALID_IMPLEMENTATION_ROUTE_BP2_HOLD_ACTION_GATE_FIXTURE,
        VALID_IMPLEMENTATION_ROUTE_RETARGET_RENAME_FIXTURE,
        VALID_MERGE_STABLE_SOURCE_TRUTH_PROJECTION_FIXTURE,
        INVALID_MERGE_STABLE_SOURCE_TRUTH_PROJECTION_FIXTURE,
        VALID_CROSS_FAM_DEPENDENCY_CANDIDATE_FIXTURE,
        INVALID_CROSS_FAM_DEPENDENCY_UNCLASSIFIED_FIXTURE,
        VALID_FAMILY_FEATURE_VISION_FIXTURE,
        INVALID_FAMILY_FEATURE_VISION_SLICE_SCOPED_FIXTURE,
        INVALID_FAMILY_FEATURE_VISION_LIVE_STATE_FIXTURE,
        VALID_BR2_DEFERRED_CARRYFORWARD_MATRIX_FIXTURE,
        INVALID_BR2_DEFERRED_CARRYFORWARD_MATRIX_FIXTURE,
        VALID_RAR_ISSUE_DURABILITY_CARRY_FORWARD_FIXTURE,
        VALID_RAR_ISSUE_DURABILITY_USER_DISPOSITIONS_FIXTURE,
        VALID_RAR_ISSUE_DURABILITY_GITHUB_PENDING_FIXTURE,
        INVALID_RAR_ISSUE_DURABILITY_PACKETED_ONLY_FIXTURE,
        INVALID_RAR_ISSUE_DURABILITY_DEFERRED_MISSING_OWNER_FIXTURE,
        INVALID_RAR_ISSUE_DURABILITY_STALE_GITHUB_CLOSED_FIXTURE,
        INVALID_RAR_ISSUE_DURABILITY_DUPLICATE_LINEAGE_FIXTURE,
        INVALID_RAR_ISSUE_DURABILITY_REPAIRED_UNVERIFIED_FIXTURE,
    ):
        if not fixture.is_file():
            failures.append(f"Missing Branch Readiness planning fixture: {fixture}")

    if failures:
        return failures

    shallow_failures = _validate_fixture(SHALLOW_FIXTURE)
    if not shallow_failures:
        failures.append(
            "Shallow Live Validation fixture unexpectedly passed planning validation"
        )
    else:
        shallow_text = "\n".join(shallow_failures)
        for snippet in EXPECTED_SHALLOW_FAILURE_SNIPPETS:
            if snippet not in shallow_text:
                failures.append(
                    "Shallow Live Validation fixture did not report expected "
                    f"failure snippet: {snippet!r}"
                )

    concrete_failures = _validate_fixture(CONCRETE_FIXTURE)
    if concrete_failures:
        failures.append(
            "Concrete Live Validation fixture unexpectedly failed planning validation: "
            + "; ".join(concrete_failures[:5])
        )

    concrete_text = CONCRETE_FIXTURE.read_text(encoding="utf-8")
    negative_approval_text = concrete_text.replace(
        (
            "Runtime Implementation Approval: USER approved implementation before "
            "this Live Validation fixture; runtime approval is not inferred from planning."
        ),
        "Runtime Implementation Approval: Not approved by USER.",
    )
    negative_approval_failures = _validate_runtime_contract_text(
        negative_approval_text,
        phase="Workstream",
    )
    if EXPECTED_NEGATIVE_APPROVAL_FAILURE_SNIPPET not in "\n".join(
        negative_approval_failures
    ):
        failures.append(
            "Negative runtime approval fixture did not reject "
            "`Runtime Implementation Approval: Not approved by USER`"
        )

    shallow_release_failures = _validate_runtime_contract_text(
        SHALLOW_FIXTURE.read_text(encoding="utf-8"),
        phase="Release Readiness",
    )
    if "Runtime Branch Engineering Contract value for 'Planned Runtime Delta:'" not in "\n".join(
        shallow_release_failures
    ):
        failures.append(
            "Shallow Release Readiness fixture did not prove runtime contract enforcement"
        )

    concrete_release_failures = _validate_runtime_contract_text(
        concrete_text,
        phase="Release Readiness",
    )
    if concrete_release_failures:
        failures.append(
            "Concrete Release Readiness runtime contract fixture unexpectedly failed: "
            + "; ".join(concrete_release_failures[:5])
        )

    valid_plan_failures = _validate_branch_runtime_plan_text(
        VALID_BRANCH_RUNTIME_PLAN_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_plan_failures:
        failures.append(
            "Valid Branch Runtime Engineering Plan fixture unexpectedly failed: "
            + "; ".join(valid_plan_failures[:5])
        )

    valid_plan_text = VALID_BRANCH_RUNTIME_PLAN_FIXTURE.read_text(encoding="utf-8")
    runtime_negative_cases = (
        (
            "direct runtime primary proof",
            valid_plan_text.replace(
                (
                    "Troubleshooting Mode Decision: Troubleshooting launcher and direct runtime "
                    "routes are diagnostic supporting evidence only and do not replace normal "
                    "launcher proof without parity."
                ),
                (
                    "Troubleshooting Mode Decision: Direct runtime and Dev Toolkit proof are "
                    "formal proof passed for exact USER launcher proof."
                ),
            ),
            EXPECTED_RUNTIME_DIRECT_PROOF_FAILURE_SNIPPET,
        ),
        (
            "missing exact USER launcher path",
            valid_plan_text.replace(
                (
                    "Exact USER Desktop Launcher Path: Formal proof uses the exact normal "
                    "USER desktop runtime launcher path C:\\Users\\anden\\OneDrive\\Desktop\\Nexus Desktop Launcher.lnk "
                    "unless USER waiver is recorded."
                ),
                "Exact USER Desktop Launcher Path: Formal proof uses the current helper launch path unless logs are present.",
            ),
            EXPECTED_RUNTIME_EXACT_LAUNCHER_FAILURE_SNIPPET,
        ),
        (
            "missing photo/video proof",
            valid_plan_text.replace(
                (
                    "Photo / Video Proof Plan: Visible user-facing claims require photo, video, "
                    "ordered frame-sequence, or focused screenshot adjudication instead of "
                    "screenshot-exists metadata."
                ),
                "Photo / Video Proof Plan: Visible user-facing claims are complete when screenshot exists metadata is present.",
            ),
            EXPECTED_RUNTIME_PHOTO_VIDEO_FAILURE_SNIPPET,
        ),
        (
            "missing USER packet evidence",
            valid_plan_text.replace(
                (
                    "USER Packet Evidence Plan: C:\\Nexus USER review hub and UTS packet record "
                    "evidence references with PASS, FAIL, BLOCKED, UNPROVEN, or WAIVED disposition."
                ),
                "USER Packet Evidence Plan: Helper output stores proof internally for later review.",
            ),
            EXPECTED_RUNTIME_PACKET_EVIDENCE_FAILURE_SNIPPET,
        ),
    )
    for label, text, expected_snippet in runtime_negative_cases:
        case_failures = _validate_branch_runtime_plan_text(text)
        if expected_snippet not in "\n".join(case_failures):
            failures.append(
                f"Runtime observability negative fixture '{label}' did not report "
                f"expected failure snippet: {expected_snippet!r}"
            )

    missing_review_gate_failures = _validate_branch_runtime_plan_text(
        _without_user_branch_plan_review_gate(
            VALID_BRANCH_RUNTIME_PLAN_FIXTURE.read_text(encoding="utf-8")
        )
    )
    if EXPECTED_BRANCH_RUNTIME_PLAN_MISSING_REVIEW_GATE_FAILURE_SNIPPET not in "\n".join(
        missing_review_gate_failures
    ):
        failures.append(
            "Pre-implementation Branch Runtime Engineering Plan fixture did not "
            "reject a missing USER Branch Plan Review Gate"
        )

    shallow_plan_failures = _validate_branch_runtime_plan_text(
        SHALLOW_BRANCH_RUNTIME_PLAN_FIXTURE.read_text(encoding="utf-8")
    )
    if not shallow_plan_failures:
        failures.append(
            "Shallow Branch Runtime Engineering Plan fixture unexpectedly passed"
        )
    else:
        shallow_plan_text = "\n".join(shallow_plan_failures)
        for snippet in EXPECTED_BRANCH_RUNTIME_PLAN_FAILURE_SNIPPETS:
            if snippet not in shallow_plan_text:
                failures.append(
                    "Shallow Branch Runtime Engineering Plan fixture did not report "
                    f"expected failure snippet: {snippet!r}"
                )

    backlog_sprawl_failures = _validate_compact_backlog_text(
        BACKLOG_SPRAWL_FIXTURE.read_text(encoding="utf-8")
    )
    if not backlog_sprawl_failures:
        failures.append("Backlog planning-sprawl fixture unexpectedly passed")

    fold_down_failures = _validate_branch_runtime_plan_text(
        FOLD_DOWN_FIXTURE.read_text(encoding="utf-8")
    )
    if fold_down_failures:
        failures.append(
            "Valid PR fold-down Branch Runtime Engineering Plan fixture unexpectedly failed: "
            + "; ".join(fold_down_failures[:5])
        )

    missing_plan_failures = _validate_missing_plan_pointer_text()
    if EXPECTED_MISSING_PLAN_PATH_FAILURE_SNIPPET not in "\n".join(
        missing_plan_failures
    ):
        failures.append(
            "Missing Branch Runtime Engineering Plan path fixture did not reject "
            "an accepted plan pointer to a nonexistent file"
        )

    valid_vision_failures = _validate_branch_vision_contract_text(
        VALID_BRANCH_VISION_CONTRACT_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_vision_failures:
        failures.append(
            "Valid Branch Vision Contract Snapshot fixture unexpectedly failed: "
            + "; ".join(valid_vision_failures[:5])
        )

    proposed_vision_failures = _validate_branch_vision_contract_text(
        INVALID_PROPOSED_BRANCH_VISION_CONTRACT_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_PROPOSED_VISION_FAILURE_SNIPPET not in "\n".join(
        proposed_vision_failures
    ):
        failures.append(
            "Invalid proposed-only Branch Vision Contract fixture did not reject "
            "Codex/ChatGPT recommendations without USER acceptance"
        )

    blocking_vision_failures = _validate_branch_vision_contract_text(
        INVALID_BLOCKING_BRANCH_VISION_CONTRACT_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BLOCKING_VISION_FAILURE_SNIPPET not in "\n".join(
        blocking_vision_failures
    ):
        failures.append(
            "Invalid blocking Branch Vision Contract fixture did not reject "
            "open blocking vision questions"
        )

    valid_ufd_failures = _validate_user_feedback_disposition_text(
        VALID_USER_FEEDBACK_DISPOSITION_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_ufd_failures:
        failures.append(
            "Valid USER Feedback Disposition fixture unexpectedly failed: "
            + "; ".join(valid_ufd_failures[:5])
        )

    valid_unicode_ufd_failures = _validate_user_feedback_disposition_text(
        VALID_USER_FEEDBACK_UNICODE_SUMMARY_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_unicode_ufd_failures:
        failures.append(
            "Valid USER Feedback Disposition Unicode summary fixture unexpectedly failed: "
            + "; ".join(valid_unicode_ufd_failures[:5])
        )

    no_owner_ufd_failures = _validate_user_feedback_disposition_text(
        INVALID_USER_FEEDBACK_NO_OWNER_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_UFD_NO_OWNER_FAILURE_SNIPPET not in "\n".join(no_owner_ufd_failures):
        failures.append(
            "Invalid USER Feedback Disposition no-owner fixture did not reject "
            "No Durable Owner Needed without No-Action Reason"
        )

    bad_id_ufd_failures = _validate_user_feedback_disposition_text(
        INVALID_USER_FEEDBACK_BAD_ID_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_UFD_BAD_ID_FAILURE_SNIPPET not in "\n".join(bad_id_ufd_failures):
        failures.append(
            "Invalid USER Feedback Disposition bad-ID fixture did not reject "
            "non-UFD feedback ID namespace"
        )

    duplicate_summary_failures = _validate_user_feedback_disposition_text(
        INVALID_USER_FEEDBACK_DUPLICATE_SUMMARY_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_UFD_DUPLICATE_SUMMARY_FAILURE_SNIPPET not in "\n".join(
        duplicate_summary_failures
    ):
        failures.append(
            "Invalid USER Feedback Disposition duplicate-summary fixture did not reject "
            "duplicate meaningful feedback"
        )

    valid_overlap_failures = _validate_branch_change_intent_text(
        VALID_REBASELINE_OVERLAP_INTENT_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_overlap_failures:
        failures.append(
            "Valid Rebaseline Overlap Intent fixture unexpectedly failed: "
            + "; ".join(valid_overlap_failures[:5])
        )

    invalid_overlap_failures = _validate_branch_change_intent_text(
        INVALID_REBASELINE_OVERLAP_UNKNOWN_HIGH_RISK_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_REBASELINE_UNKNOWN_RISK_FAILURE_SNIPPET not in "\n".join(
        invalid_overlap_failures
    ):
        failures.append(
            "Invalid Rebaseline Overlap Intent fixture did not reject Unknown "
            "semantic merge risk for a high-risk overlap surface"
        )

    fallback_only_failures = _validate_branch_change_intent_text(
        INVALID_REBASELINE_OVERLAP_FALLBACK_ONLY_PASS_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_REBASELINE_FALLBACK_ONLY_FAILURE_SNIPPET not in "\n".join(
        fallback_only_failures
    ):
        failures.append(
            "Invalid Rebaseline Overlap Intent fixture did not reject fallback-only "
            "PASS / compatibility-bypass wording after the effective point"
        )

    low_risk_warn_failures = _validate_branch_change_intent_text(
        VALID_REBASELINE_OVERLAP_LOW_RISK_WARN_FIXTURE.read_text(encoding="utf-8")
    )
    if low_risk_warn_failures:
        failures.append(
            "Valid low-risk WARN Rebaseline Overlap Intent fixture unexpectedly failed: "
            + "; ".join(low_risk_warn_failures[:5])
        )

    high_impact_fixture_failures = _validate_branch_change_intent_text(
        INVALID_REBASELINE_OVERLAP_FIXTURE_HIGH_IMPACT_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_REBASELINE_FIXTURE_HIGH_IMPACT_FAILURE_SNIPPET not in "\n".join(
        high_impact_fixture_failures
    ):
        failures.append(
            "Invalid Rebaseline Overlap fixture/test fixture did not reject High "
            "Regression / Gating Impact"
        )

    low_impact_fixture_failures = _validate_branch_change_intent_text(
        VALID_REBASELINE_OVERLAP_FIXTURE_LOW_IMPACT_FIXTURE.read_text(encoding="utf-8")
    )
    if low_impact_fixture_failures:
        failures.append(
            "Valid low-impact fixture/test Rebaseline Overlap Intent fixture unexpectedly failed: "
            + "; ".join(low_impact_fixture_failures[:5])
        )

    valid_matrix_failures = _validate_element_to_phase_matrix_text(
        VALID_ELEMENT_TO_PHASE_MATRIX_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_matrix_failures:
        failures.append(
            "Valid Element-to-Phase Proof Matrix fixture unexpectedly failed: "
            + "; ".join(valid_matrix_failures[:5])
        )

    missing_hardening_failures = _validate_element_to_phase_matrix_text(
        INVALID_ELEMENT_TO_PHASE_MISSING_HARDENING_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_ELEMENT_MATRIX_HARDENING_FAILURE_SNIPPET not in "\n".join(
        missing_hardening_failures
    ):
        failures.append(
            "Invalid Element-to-Phase Proof Matrix fixture did not reject missing "
            "Hardening proof path"
        )

    missing_live_validation_failures = _validate_element_to_phase_matrix_text(
        INVALID_ELEMENT_TO_PHASE_MISSING_LIVE_VALIDATION_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_ELEMENT_MATRIX_LIVE_VALIDATION_FAILURE_SNIPPET not in "\n".join(
        missing_live_validation_failures
    ):
        failures.append(
            "Invalid Element-to-Phase Proof Matrix fixture did not reject missing "
            "Live Validation proof or waiver path"
        )

    deferred_future_matrix_failures = _validate_element_to_phase_matrix_text(
        VALID_ELEMENT_TO_PHASE_DEFERRED_FUTURE_FIXTURE.read_text(encoding="utf-8")
    )
    if deferred_future_matrix_failures:
        failures.append(
            "Valid deferred/future Element-to-Phase Proof Matrix fixture unexpectedly failed: "
            + "; ".join(deferred_future_matrix_failures[:5])
        )

    duplicate_matrix_failures = _validate_element_to_phase_matrix_text(
        INVALID_ELEMENT_TO_PHASE_DUPLICATE_ID_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_ELEMENT_MATRIX_DUPLICATE_ID_FAILURE_SNIPPET not in "\n".join(
        duplicate_matrix_failures
    ):
        failures.append(
            "Invalid Element-to-Phase Proof Matrix fixture did not reject duplicate "
            "Element ID values"
        )

    valid_whole_package_failures = _validate_workstream_entry_whole_package_text(
        VALID_WORKSTREAM_ENTRY_WHOLE_PACKAGE_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_whole_package_failures:
        failures.append(
            "Valid Workstream Entry Whole-Package Analysis fixture unexpectedly failed: "
            + "; ".join(valid_whole_package_failures[:5])
        )

    first_seam_only_failures = _validate_workstream_entry_whole_package_text(
        INVALID_WORKSTREAM_ENTRY_FIRST_SEAM_ONLY_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_WORKSTREAM_ENTRY_FIRST_SEAM_FAILURE_SNIPPET not in "\n".join(
        first_seam_only_failures
    ):
        failures.append(
            "Invalid Workstream Entry fixture did not reject first-seam-only analysis"
        )

    valid_branch_review_failures = _validate_user_branch_plan_review_text(
        VALID_USER_BRANCH_PLAN_REVIEW_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_branch_review_failures:
        failures.append(
            "Valid USER Branch Plan Review fixture unexpectedly failed: "
            + "; ".join(valid_branch_review_failures[:5])
        )

    missing_outcome_failures = _validate_user_branch_plan_review_text(
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_OUTCOME_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_USER_BRANCH_PLAN_MISSING_OUTCOME_FAILURE_SNIPPET not in "\n".join(
        missing_outcome_failures
    ):
        failures.append(
            "Invalid USER Branch Plan Review fixture did not reject missing "
            "planned user-facing outcome"
        )

    missing_packet_finding_failures = _validate_user_branch_plan_review_text(
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_PACKET_FINDING_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_USER_BRANCH_PLAN_MISSING_PACKET_FINDING_FAILURE_SNIPPET not in "\n".join(
        missing_packet_finding_failures
    ):
        failures.append(
            "Invalid USER Branch Plan Review fixture did not reject missing "
            "USER Review Packet Finding"
        )

    missing_review_hardening_failures = _validate_user_branch_plan_review_text(
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_HARDENING_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_USER_BRANCH_PLAN_MISSING_HARDENING_FAILURE_SNIPPET not in "\n".join(
        missing_review_hardening_failures
    ):
        failures.append(
            "Invalid USER Branch Plan Review fixture did not reject missing "
            "Hardening plan"
        )

    missing_review_live_validation_failures = _validate_user_branch_plan_review_text(
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_LIVE_VALIDATION_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_USER_BRANCH_PLAN_MISSING_LIVE_VALIDATION_FAILURE_SNIPPET not in "\n".join(
        missing_review_live_validation_failures
    ):
        failures.append(
            "Invalid USER Branch Plan Review fixture did not reject missing "
            "Live Validation / UTS plan"
        )

    first_seam_review_failures = _validate_user_branch_plan_review_text(
        INVALID_USER_BRANCH_PLAN_REVIEW_FIRST_SEAM_ONLY_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_USER_BRANCH_PLAN_FIRST_SEAM_FAILURE_SNIPPET not in "\n".join(
        first_seam_review_failures
    ):
        failures.append(
            "Invalid USER Branch Plan Review fixture did not reject first-seam-only "
            "implementation breakdown"
        )

    missing_response_digest_failures = _validate_user_branch_plan_review_text(
        INVALID_USER_BRANCH_PLAN_REVIEW_MISSING_RESPONSE_DIGEST_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_USER_BRANCH_PLAN_MISSING_RESPONSE_DIGEST_FAILURE_SNIPPET not in "\n".join(
        missing_response_digest_failures
    ):
        failures.append(
            "Invalid USER Branch Plan Review fixture did not reject missing "
            "USER response / Codex digest markers"
        )

    deferred_review_failures = _validate_user_branch_plan_review_text(
        VALID_USER_BRANCH_PLAN_REVIEW_DEFERRED_SCOPE_FIXTURE.read_text(encoding="utf-8")
    )
    if deferred_review_failures:
        failures.append(
            "Valid deferred-scope USER Branch Plan Review fixture unexpectedly failed: "
            + "; ".join(deferred_review_failures[:5])
        )

    valid_gate_state_failures = _validate_branch_planning_gate_state_packet_text(
        VALID_BRANCH_PLANNING_GATE_STATE_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_gate_state_failures:
        failures.append(
            "Valid Branch Planning review-gate state fixture unexpectedly failed: "
            + "; ".join(valid_gate_state_failures[:5])
        )

    gate_bypass_failures = _validate_branch_planning_gate_state_packet_text(
        INVALID_BRANCH_PLANNING_GATE_BYPASS_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BRANCH_PLANNING_GATE_BYPASS_FAILURE_SNIPPET not in "\n".join(
        gate_bypass_failures
    ):
        failures.append(
            "Invalid Branch Planning review-gate fixture did not reject packet "
            "validation treated as USER acceptance"
        )

    failures.extend(_validate_primary_user_review_file_stage_priority())

    valid_bp1_failures = _validate_bp1_branch_vision_review_text(
        VALID_BP1_BRANCH_VISION_REVIEW_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_bp1_failures:
        failures.append(
            "Valid BP1 Branch Vision Review fixture unexpectedly failed: "
            + "; ".join(valid_bp1_failures[:5])
        )

    for fixture, label in (
        (VALID_BP1_FAM006_DOGFOOD_FIXTURE, "FAM-006 UI/runtime BP1 dogfood"),
        (VALID_BP1_FAM007_DOGFOOD_FIXTURE, "FAM-007 private-boundary BP1 dogfood"),
        (VALID_BP1_GOVERNANCE_DOGFOOD_FIXTURE, "Governance source-truth BP1 dogfood"),
    ):
        dogfood_failures = _validate_bp1_branch_vision_review_text(
            fixture.read_text(encoding="utf-8")
        )
        if dogfood_failures:
            failures.append(
                f"Valid {label} fixture unexpectedly failed: "
                + "; ".join(dogfood_failures[:5])
            )

    missing_context_failures = _validate_bp1_branch_vision_review_text(
        INVALID_BP1_MISSING_CONTEXT_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP1_CONTEXT_FAILURE_SNIPPET not in "\n".join(missing_context_failures):
        failures.append(
            "Invalid BP1 missing-context fixture did not reject missing Project/Family/Feature context"
        )

    shallow_recommendation_failures = _validate_bp1_branch_vision_review_text(
        INVALID_BP1_SHALLOW_RECOMMENDATIONS_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP1_SHALLOW_RECOMMENDATION_FAILURE_SNIPPET not in "\n".join(
        shallow_recommendation_failures
    ):
        failures.append(
            "Invalid BP1 shallow-recommendations fixture did not reject shallow recommendations"
        )

    template_shell_failures = _validate_bp1_branch_vision_review_text(
        INVALID_BP1_TEMPLATE_SHELL_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP1_TEMPLATE_SHELL_FAILURE_SNIPPET not in "\n".join(
        template_shell_failures
    ):
        failures.append(
            "Invalid BP1 template-shell fixture did not reject instructional placeholder content"
        )

    process_mechanics_failures = _validate_bp1_branch_vision_review_text(
        INVALID_BP1_PROCESS_MECHANICS_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP1_TEMPLATE_SHELL_FAILURE_SNIPPET not in "\n".join(
        process_mechanics_failures
    ):
        failures.append(
            "Invalid BP1 process-mechanics fixture did not reject process-only BP1 review content"
        )

    copied_surface_failures = _validate_bp1_branch_vision_review_text(
        INVALID_BP1_COPIED_FILE_SURFACE_ONLY_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP1_COPIED_SURFACE_FAILURE_SNIPPET not in "\n".join(
        copied_surface_failures
    ):
        failures.append(
            "Invalid BP1 copied-file surface fixture did not reject copied-file-list-only surface map"
        )

    generic_questions_failures = _validate_bp1_branch_vision_review_text(
        INVALID_BP1_GENERIC_USER_QUESTIONS_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP1_GENERIC_QUESTIONS_FAILURE_SNIPPET not in "\n".join(
        generic_questions_failures
    ):
        failures.append(
            "Invalid BP1 generic-questions fixture did not reject non-decision-driving USER questions"
        )

    slc_centered_failures = _validate_bp1_branch_vision_review_text(
        INVALID_BP1_SLC_CENTERED_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP1_SLC_CENTERED_FAILURE_SNIPPET not in "\n".join(
        slc_centered_failures
    ):
        failures.append(
            "Invalid BP1 SLC-centered fixture did not reject SLC-centered branch vision"
        )

    technical_metadata_failures = _validate_bp1_branch_vision_review_text(
        INVALID_BP1_TECHNICAL_METADATA_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP1_TECHNICAL_METADATA_FAILURE_SNIPPET not in "\n".join(
        technical_metadata_failures
    ):
        failures.append(
            "Invalid BP1 technical-metadata fixture did not reject active branch metadata"
        )

    runtime_focus_issue_failures = _validate_runtime_focus_selection_text(
        INVALID_RUNTIME_FOCUS_ISSUE_ANCHORED_SELECTION_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_RUNTIME_FOCUS_ISSUE_ANCHORED_FAILURE_SNIPPET not in "\n".join(
        runtime_focus_issue_failures
    ):
        failures.append(
            "Invalid runtime-focus issue-anchored fixture did not reject issue-shaped selection"
        )

    runtime_focus_foundation_failures = _validate_runtime_focus_selection_text(
        INVALID_RUNTIME_FOCUS_FOUNDATION_LABEL_SELECTION_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_RUNTIME_FOCUS_FOUNDATION_LABEL_FAILURE_SNIPPET not in "\n".join(
        runtime_focus_foundation_failures
    ):
        failures.append(
            "Invalid runtime-focus foundation-label fixture did not reject non-feature selection"
        )

    missing_bp1_trace_failures = _validate_bp2_branch_plan_review_text(
        INVALID_BP2_MISSING_ACCEPTED_BP1_TRACE_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP2_ACCEPTED_BP1_TRACE_FAILURE_SNIPPET not in "\n".join(
        missing_bp1_trace_failures
    ):
        failures.append(
            "Invalid BP2 missing-accepted-BP1 fixture did not reject missing accepted BP1 trace"
        )

    product_design_wording_failures = _validate_bp2_branch_plan_review_text(
        INVALID_BP2_PRODUCT_DESIGN_WORDING_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_BP2_PRODUCT_DESIGN_WORDING_FAILURE_SNIPPET not in "\n".join(
        product_design_wording_failures
    ):
        failures.append(
            "Invalid BP2 product-design wording fixture did not reject stale BP1 contract wording"
        )

    for fixture, label in (
        (VALID_BP2_FAM006_DOGFOOD_FIXTURE, "FAM-006 UI/runtime BP2 dogfood"),
        (VALID_BP2_FAM007_DOGFOOD_FIXTURE, "FAM-007 private-boundary BP2 dogfood"),
    ):
        dogfood_failures = _validate_bp2_branch_plan_review_text(
            fixture.read_text(encoding="utf-8")
        )
        if dogfood_failures:
            failures.append(
                f"Valid {label} fixture unexpectedly failed: "
                + "; ".join(dogfood_failures[:5])
            )

    bp3_pending_failures = _validate_bp3_orchestration_text(
        INVALID_BP3_IMPLEMENTATION_WITH_PENDING_BP1_BP2_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_BP3_PENDING_FAILURE_SNIPPET not in "\n".join(bp3_pending_failures):
        failures.append(
            "Invalid BP3 pending-BP1/BP2 fixture did not reject implementation approval"
        )

    valid_bp3_failures = _validate_bp3_orchestration_text(
        VALID_BP3_ACCEPTED_BP1_BP2_SLC_TRACE_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_bp3_failures:
        failures.append(
            "Valid BP3 accepted-BP1/BP2 fixture unexpectedly failed: "
            + "; ".join(valid_bp3_failures[:5])
        )

    for fixture, label in (
        (VALID_BP3_FAM006_DOGFOOD_FIXTURE, "FAM-006 UI/runtime BP3 dogfood"),
        (VALID_BP3_FAM007_DOGFOOD_FIXTURE, "FAM-007 private-boundary BP3 dogfood"),
    ):
        dogfood_failures = _validate_bp3_orchestration_text(
            fixture.read_text(encoding="utf-8")
        )
        if dogfood_failures:
            failures.append(
                f"Valid {label} fixture unexpectedly failed: "
                + "; ".join(dogfood_failures[:5])
            )

    implementation_route_source_truth_failures = (
        _validate_implementation_bearing_source_truth()
    )
    if implementation_route_source_truth_failures:
        failures.append(
            "Implementation-bearing source truth unexpectedly failed: "
            + "; ".join(implementation_route_source_truth_failures[:5])
        )

    terminology_ambiguity_failures = _validate_slice_slc_seam_model_text(
        INVALID_SLC_SLICE_SEAM_AMBIGUITY_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
        terminology_ambiguity_failures
    ):
        failures.append(
            "Invalid SLC/Slice/Seam terminology fixture did not reject ambiguity"
        )

    spaced_slc_seam_alias_matrix = (
        "SLC 1 is the seam for the consent shell.",
        "SLC 1 means seam for the consent shell.",
    )
    for phrase in spaced_slc_seam_alias_matrix:
        spaced_slc_seam_failures = _validate_slice_slc_seam_model_text(
            f"""
# Invalid Spaced SLC Seam Alias Matrix Case

SLC is shorthand for Slice and remains a Slice-level deliverable.
{phrase}
"""
        )
        if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
            spaced_slc_seam_failures
        ):
            failures.append(
                "Invalid spaced SLC seam alias fixture did not reject: " + phrase
            )

    for fixture, label in (
        (
            VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE,
            "multi-slice implementation carrier",
        ),
        (
            VALID_REQUIRED_SEPARATE_BRANCH_CASE_FIXTURE,
            "required separate-branch case",
        ),
    ):
        terminology_failures = _validate_slice_slc_seam_model_text(
            fixture.read_text(encoding="utf-8")
        )
        if terminology_failures:
            failures.append(
                f"Valid {label} fixture unexpectedly failed: "
                + "; ".join(terminology_failures[:5])
            )

    prose_only_multi_slice_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Multi-Slice Carrier: FAM-007 provider consent shell and artifact "
            "exclusion control.",
            "Package Summary: This is a multi-slice FAM-007 provider consent "
            "shell and artifact exclusion control without future multi-slice "
            "scope creep.",
        )
        .replace(
            "Shared Owner / Worktree: One FAM-007 branch/worktree owns all "
            "slices because they serve the same public-safe provider-boundary "
            "route and one package objective.\n\n",
            "",
        )
    )
    if "Multi-slice carrier missing Shared Owner / Worktree:" not in "\n".join(
        prose_only_multi_slice_failures
    ):
        failures.append(
            "Invalid prose-only multi-slice fixture did not enforce required "
            "multi-slice evidence without the exact carrier marker"
        )

    negated_multi_slice_carrier_failures = _validate_slice_slc_seam_model_text(
        """
# Valid Non-Multi-Slice Branch Plan

Not a Multi-Slice Carrier: This branch owns one Slice-level deliverable and
does not require multi-slice-only owner, split, or shared validation fields.

Selected Implementation Route: One branch-local governance validation repair
that keeps Slice/SLC terminology distinct from seam routing.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
    )
    if negated_multi_slice_carrier_failures:
        failures.append(
            "Valid negated multi-slice carrier declaration unexpectedly failed: "
            + "; ".join(negated_multi_slice_carrier_failures[:5])
        )

    negative_multi_slice_marker_failures = _validate_slice_slc_seam_model_text(
        """
# Valid Single-Slice Branch Plan With Negative Multi-Slice Marker

Multi-Slice Carrier: No

Selected Implementation Route: One branch-local governance validation repair
that keeps the current branch scoped to one Slice-level deliverable.

Concrete Deliverable: A single SLC-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
    )
    if negative_multi_slice_marker_failures:
        failures.append(
            "Valid negative Multi-Slice Carrier marker unexpectedly failed: "
            + "; ".join(negative_multi_slice_marker_failures[:5])
        )

    stale_negative_marker_with_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Multi-Slice Carrier: FAM-007 provider consent shell and artifact "
            "exclusion control.",
            "Multi-Slice Carrier: No",
        )
        .replace(
            "Shared Owner / Worktree: One FAM-007 branch/worktree owns all "
            "slices because they serve the same public-safe provider-boundary "
            "route and one package objective.\n\n",
            "",
        )
    )
    if "Multi-slice carrier missing Shared Owner / Worktree:" not in "\n".join(
        stale_negative_marker_with_slice_map_failures
    ):
        failures.append(
            "Invalid stale negative carrier marker fixture did not enforce "
            "multi-slice evidence when Slice Map names multiple deliverables"
        )

    no_split_multi_slice_marker_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Multi-Slice Carrier: FAM-007 provider consent shell and artifact "
            "exclusion control.",
            "Multi-Slice Carrier: No split required; this multi-slice carrier "
            "remains branch-local because all slices serve one package route.",
        )
        .replace(
            "Shared Owner / Worktree: One FAM-007 branch/worktree owns all "
            "slices because they serve the same public-safe provider-boundary "
            "route and one package objective.\n\n",
            "",
        )
    )
    if "Multi-slice carrier missing Shared Owner / Worktree:" not in "\n".join(
        no_split_multi_slice_marker_failures
    ):
        failures.append(
            "Invalid no-split multi-slice marker fixture did not enforce "
            "required multi-slice evidence"
        )

    future_gated_multi_slice_failures = _validate_slice_slc_seam_model_text(
        """
# Valid Single-Slice Branch Plan With Future-Gated Multi-Slice Boundary

Selected Implementation Route: One branch-local governance validation repair
that keeps the current branch scoped to one Slice-level deliverable.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.

Future-Gated Boundaries: Future multi-slice package expansion remains
USER-gated and outside this current branch plan.
"""
    )
    if future_gated_multi_slice_failures:
        failures.append(
            "Valid future-gated multi-slice boundary unexpectedly triggered "
            "current multi-slice carrier enforcement: "
            + "; ".join(future_gated_multi_slice_failures[:5])
        )

    package_summary_future_gated_multi_slice_failures = (
        _validate_slice_slc_seam_model_text(
            """
# Valid Single-Slice Branch Plan With Package Summary Future-Gated Boundary

Package Summary: Future multi-slice package expansion remains USER-gated and
outside this current branch plan.

Selected Implementation Route: One branch-local governance validation repair
that keeps the current branch scoped to one Slice-level deliverable.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
        )
    )
    if package_summary_future_gated_multi_slice_failures:
        failures.append(
            "Valid package-summary future-gated multi-slice boundary unexpectedly "
            "triggered current multi-slice carrier enforcement: "
            + "; ".join(package_summary_future_gated_multi_slice_failures[:5])
        )

    package_summary_postfixed_future_gated_multi_slice_failures = (
        _validate_slice_slc_seam_model_text(
            """
# Valid Package Summary With Postfixed Future-Gated Multi-Slice Boundary

Package Summary: Multi-slice package expansion remains future-gated and outside
this current branch plan.

Selected Implementation Route: One branch-local governance validation repair
that keeps the current branch scoped to one Slice-level deliverable.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
        )
    )
    if package_summary_postfixed_future_gated_multi_slice_failures:
        failures.append(
            "Valid package-summary postfixed future-gated multi-slice boundary "
            "unexpectedly triggered current multi-slice carrier enforcement: "
            + "; ".join(package_summary_postfixed_future_gated_multi_slice_failures[:5])
        )

    explanatory_negative_multi_slice_marker_failures = (
        _validate_slice_slc_seam_model_text(
            """
# Valid Explanatory Negative Multi-Slice Marker

Multi-Slice Carrier: Not applicable; future multi-slice expansion remains USER-gated.

Selected Implementation Route: One branch-local governance validation repair
that keeps the current branch scoped to one Slice-level deliverable.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
        )
    )
    if explanatory_negative_multi_slice_marker_failures:
        failures.append(
            "Valid explanatory negative multi-slice marker unexpectedly triggered "
            "current multi-slice carrier enforcement: "
            + "; ".join(explanatory_negative_multi_slice_marker_failures[:5])
        )

    future_gated_only_multi_slice_marker_failures = (
        _validate_slice_slc_seam_model_text(
            """
# Valid Future-Gated-Only Multi-Slice Marker

Multi-Slice Carrier: Future-gated only; multi-slice expansion remains USER-gated and non-current.

Selected Implementation Route: One branch-local governance validation repair
that keeps the current branch scoped to one Slice-level deliverable.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
        )
    )
    if future_gated_only_multi_slice_marker_failures:
        failures.append(
            "Valid future-gated-only multi-slice marker unexpectedly triggered "
            "current multi-slice carrier enforcement: "
            + "; ".join(future_gated_only_multi_slice_marker_failures[:5])
        )

    route_policy_multi_slice_reference_failures = _validate_slice_slc_seam_model_text(
        """
# Valid Single-Slice Governance Repair That Mentions Multi-Slice Policy

Selected Implementation Route: Implement governance validator behavior that
prevents multi-slice branches from splitting incorrectly.

Concrete Deliverable: A validator repair that checks multi-slice carrier policy
without making this governance branch a multi-slice implementation carrier.

Implementation Route Class: governance/source-truth validator implementation.
"""
    )
    if route_policy_multi_slice_reference_failures:
        failures.append(
            "Valid route-policy multi-slice reference unexpectedly triggered "
            "current multi-slice carrier enforcement: "
            + "; ".join(route_policy_multi_slice_reference_failures[:5])
        )

    package_summary_policy_multi_slice_reference_failures = (
        _validate_slice_slc_seam_model_text(
            """
# Valid Package Summary That Mentions Multi-Slice Policy

Package Summary: This governance package validates multi-slice carrier policy
without making this branch a multi-slice implementation carrier.

Selected Implementation Route: One branch-local governance validation repair
that keeps the current branch scoped to one Slice-level deliverable.

Concrete Deliverable: A validator repair that checks multi-slice carrier policy
without creating current multi-slice package scope.
"""
        )
    )
    if package_summary_policy_multi_slice_reference_failures:
        failures.append(
            "Valid package-summary multi-slice policy reference unexpectedly "
            "triggered current multi-slice carrier enforcement: "
            + "; ".join(package_summary_policy_multi_slice_reference_failures[:5])
        )

    postfixed_negated_multi_slice_failures = _validate_slice_slc_seam_model_text(
        """
# Valid Single-Slice Branch Plan With Postfixed Multi-Slice Negation

Package Summary: Multi-slice not required for this branch; the current route
owns one Slice-level governance validator repair.

Selected Implementation Route: One branch-local governance validation repair
that keeps Slice/SLC terminology distinct from seam routing.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
    )
    if postfixed_negated_multi_slice_failures:
        failures.append(
            "Valid postfixed multi-slice negation unexpectedly triggered "
            "current multi-slice carrier enforcement: "
            + "; ".join(postfixed_negated_multi_slice_failures[:5])
        )

    postfixed_negated_multiple_slices_failures = _validate_slice_slc_seam_model_text(
        """
# Valid Single-Slice Branch Plan With Postfixed Multiple-Slices Negation

Package Summary: Multiple slices not required for this branch; the current
route owns one Slice-level governance validator repair.

Selected Implementation Route: One branch-local governance validation repair
that keeps Slice/SLC terminology distinct from seam routing.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
    )
    if postfixed_negated_multiple_slices_failures:
        failures.append(
            "Valid postfixed multiple-slices negation unexpectedly triggered "
            "current multi-slice carrier enforcement: "
            + "; ".join(postfixed_negated_multiple_slices_failures[:5])
        )

    prefixed_negated_multiple_slices_failures = _validate_slice_slc_seam_model_text(
        """
# Valid Single-Slice Branch Plan With Prefixed Multiple-Slices Negation

Package Summary: This branch is not multiple slices; the current route owns
one Slice-level governance validator repair.

Selected Implementation Route: One branch-local governance validation repair
that keeps Slice/SLC terminology distinct from seam routing.

Concrete Deliverable: A single Slice-level validator proof for branch planning
terminology without creating a multi-slice package carrier.
"""
    )
    if prefixed_negated_multiple_slices_failures:
        failures.append(
            "Valid prefixed multiple-slices negation unexpectedly triggered "
            "current multi-slice carrier enforcement: "
            + "; ".join(prefixed_negated_multiple_slices_failures[:5])
        )

    slice_map_only_multi_slice_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Multi-Slice Carrier: FAM-007 provider consent shell and artifact "
            "exclusion control.\n",
            "",
        )
        .replace(
            "Shared Owner / Worktree: One FAM-007 branch/worktree owns all "
            "slices because they serve the same public-safe provider-boundary "
            "route and one package objective.\n\n",
            "",
        )
    )
    if "Multi-slice carrier missing Shared Owner / Worktree:" not in "\n".join(
        slice_map_only_multi_slice_failures
    ):
        failures.append(
            "Invalid Slice Map-only multi-slice fixture did not infer current "
            "multi-slice carrier enforcement"
        )

    slc_id_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map: SLC-001 implements consent-shell disabled-state source-truth "
            "and review copy. slc-002 implements public artifact exclusion "
            "validator/helper enforcement.",
        )
    )
    if slc_id_slice_map_failures:
        failures.append(
            "Valid SLC-ID Slice Map fixture unexpectedly failed: "
            + "; ".join(slc_id_slice_map_failures[:5])
        )

    multiline_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map:\n"
            "- Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy.\n"
            "- Slice 2 / SLC-002 implements public artifact exclusion "
            "validator/helper enforcement.\n"
            "- Slice 3 / SLC-003 implements packet proof and future-gated "
            "boundary preservation.",
        )
    )
    if multiline_slice_map_failures:
        failures.append(
            "Valid multiline Slice Map fixture unexpectedly failed: "
            + "; ".join(multiline_slice_map_failures[:5])
        )

    numbered_multiline_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map:\n"
            "1. Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy.\n"
            "2. Slice 2 / SLC-002 implements public artifact exclusion "
            "validator/helper enforcement.\n"
            "3. Slice 3 / SLC-003 implements packet proof and future-gated "
            "boundary preservation.",
        )
    )
    if numbered_multiline_slice_map_failures:
        failures.append(
            "Valid numbered multiline Slice Map fixture unexpectedly failed: "
            + "; ".join(numbered_multiline_slice_map_failures[:5])
        )

    colon_labeled_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map:\n"
            "- SLC-001: consent-shell disabled-state source-truth and review copy.\n"
            "- SLC-002: public artifact exclusion validator/helper enforcement.\n"
            "- SLC-003: packet proof and future-gated boundary preservation.",
        )
    )
    if colon_labeled_slice_map_failures:
        failures.append(
            "Valid colon-labeled Slice Map fixture unexpectedly failed: "
            + "; ".join(colon_labeled_slice_map_failures[:5])
        )

    same_sentence_slc_id_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map: SLC-001 and SLC-002 implement consent-shell disabled-state "
            "source-truth, review copy, and public artifact exclusion "
            "validator/helper enforcement.",
        )
    )
    if same_sentence_slc_id_slice_map_failures:
        failures.append(
            "Valid same-sentence SLC-ID Slice Map fixture unexpectedly failed: "
            + "; ".join(same_sentence_slc_id_slice_map_failures[:5])
        )

    single_slc_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy.",
        )
    )
    if "Multi-slice carrier must map at least two slices" not in "\n".join(
        single_slc_slice_map_failures
    ):
        failures.append(
            "Invalid single SLC Slice Map fixture did not reject one deliverable "
            "written with Slice plus SLC wording"
        )

    mismatched_slice_slc_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map: Slice 1 / SLC-002 implements consent-shell disabled-state "
            "source-truth and review copy.",
        )
    )
    if "Multi-slice carrier must map at least two slices" not in "\n".join(
        mismatched_slice_slc_slice_map_failures
    ):
        failures.append(
            "Invalid mismatched Slice/SLC Slice Map fixture did not reject one "
            "mapped entry written with two label namespaces"
        )

    mismatched_pair_plus_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map: Slice 1 / SLC-002 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 3 / SLC-003 implements public "
            "artifact exclusion validator/helper enforcement.",
        )
    )
    if (
        "Multi-slice carrier Slice Map contains mismatched Slice/SLC alias pair"
        not in "\n".join(mismatched_pair_plus_slice_map_failures)
    ):
        failures.append(
            "Invalid mismatched Slice/SLC pair plus another slice fixture did not "
            "reject ambiguous alias-pair wording"
        )

    duplicate_slice_id_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map: Slice 1 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 1 implements public artifact "
            "exclusion validator/helper enforcement.",
        )
    )
    if "Multi-slice carrier must map at least two slices" not in "\n".join(
        duplicate_slice_id_slice_map_failures
    ):
        failures.append(
            "Invalid duplicate Slice ID Slice Map fixture did not reject two "
            "mapped entries for the same slice"
        )

    duplicate_slice_slc_pair_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 1 / SLC-001 implements public "
            "artifact exclusion validator/helper enforcement.",
        )
    )
    if "Multi-slice carrier must map at least two slices" not in "\n".join(
        duplicate_slice_slc_pair_slice_map_failures
    ):
        failures.append(
            "Invalid duplicate Slice/SLC pair Slice Map fixture did not reject "
            "two mapped entries for the same zero-padded SLC alias"
        )

    repeated_generic_slice_map_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Slice Map: Slice 1 / SLC-001 implements consent-shell disabled-state "
            "source-truth and review copy. Slice 2 / SLC-002 implements public "
            "artifact exclusion validator/helper enforcement. Slice 3 / SLC-003 "
            "implements packet proof and future-gated boundary preservation.",
            "Slice Map: The current slice implements consent-shell disabled-state "
            "source-truth and review copy. The same slice validates helper "
            "enforcement. This slice records packet proof.",
        )
    )
    if "Multi-slice carrier must map at least two slices" not in "\n".join(
        repeated_generic_slice_map_failures
    ):
        failures.append(
            "Invalid repeated generic slice-map fixture did not reject prose-only "
            "slice mentions without distinct Slice/SLC identifiers"
        )

    slc_id_branch_ambiguity_failures = _validate_slice_slc_seam_model_text(
        """
# Invalid SLC ID Branch Split Ambiguity

SLC is shorthand for Slice and remains a Slice-level deliverable.
SLC-001 is a separate branch for the consent shell.
"""
    )
    if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
        slc_id_branch_ambiguity_failures
    ):
        failures.append(
            "Invalid SLC-ID branch ambiguity fixture did not reject SLC-as-branch "
            "wording after valid alias wording"
        )

    plural_slc_branch_ambiguity_failures = _validate_slice_slc_seam_model_text(
        """
# Invalid Plural SLC Branch Split Ambiguity

SLC is shorthand for Slice and remains a Slice-level deliverable.
SLCs are separate branches for the consent shell and artifact boundary.
"""
    )
    if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
        plural_slc_branch_ambiguity_failures
    ):
        failures.append(
            "Invalid plural SLC branch ambiguity fixture did not reject SLCs-as-branches "
            "wording after valid alias wording"
        )

    coordinated_slc_branch_ambiguity_failures = _validate_slice_slc_seam_model_text(
        """
# Invalid Coordinated SLC Branch Split Ambiguity

SLC is shorthand for Slice and remains a Slice-level deliverable.
SLC-001 and SLC-002 are separate branches for the consent shell and artifact boundary.
"""
    )
    if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
        coordinated_slc_branch_ambiguity_failures
    ):
        failures.append(
            "Invalid coordinated SLC branch ambiguity fixture did not reject "
            "numbered SLCs-as-branches wording after valid alias wording"
        )

    bare_slc_branch_ambiguity_failures = _validate_slice_slc_seam_model_text(
        """
# Invalid Bare SLC Branch Identity Ambiguity

SLC is shorthand for Slice and remains a Slice-level deliverable.
SLC-001 is a branch for the consent shell.
"""
    )
    if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
        bare_slc_branch_ambiguity_failures
    ):
        failures.append(
            "Invalid bare SLC branch identity fixture did not reject SLC-as-branch "
            "wording without the word separate"
        )

    plural_bare_slc_branch_ambiguity_failures = _validate_slice_slc_seam_model_text(
        """
# Invalid Plural Bare SLC Branch Identity Ambiguity

SLC is shorthand for Slice and remains a Slice-level deliverable.
SLCs are branches for the consent shell and artifact boundary.
"""
    )
    if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
        plural_bare_slc_branch_ambiguity_failures
    ):
        failures.append(
            "Invalid plural bare SLC branch identity fixture did not reject "
            "SLCs-as-branches wording without the word separate"
        )

    coordinated_bare_slc_branch_ambiguity_failures = (
        _validate_slice_slc_seam_model_text(
            """
# Invalid Coordinated Bare SLC Branch Identity Ambiguity

SLC is shorthand for Slice and remains a Slice-level deliverable.
SLC-001 and SLC-002 are branches for the consent shell and artifact boundary.
"""
        )
    )
    if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
        coordinated_bare_slc_branch_ambiguity_failures
    ):
        failures.append(
            "Invalid coordinated bare SLC branch identity fixture did not reject "
            "numbered SLCs-as-branches wording without the word separate"
        )

    adjective_slc_branch_ambiguity_failures = _validate_slice_slc_seam_model_text(
        """
# Invalid SLC Branch Adjective Ambiguity

SLC is shorthand for Slice and remains a Slice-level deliverable.
The SLC-001 branch owns the consent shell while SLC-002 branch owns the artifact boundary.
"""
    )
    if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
        adjective_slc_branch_ambiguity_failures
    ):
        failures.append(
            "Invalid SLC branch adjective fixture did not reject numbered "
            "SLC-as-branch wording after valid alias wording"
        )

    slc_branch_identity_matrix = (
        "SLC-001 branch owns the consent shell.",
        "SLC-001 owns a branch for the consent shell.",
        "SLC-002 has its own branch for the artifact boundary.",
        "SLC 1 is a branch for the consent shell.",
        "SLC 1 owns a branch for the consent shell.",
        "SLC 1 and SLC 2 own branches for the consent shell and artifact boundary.",
        "SLCs own branches for the consent shell and artifact boundary.",
        "SLC-001 and SLC-002 own branches for the consent shell and artifact boundary.",
        "SLC-001 and SLC-002 have branches for the consent shell and artifact boundary.",
        "Create a branch for SLC-003.",
        "Each SLC has a branch for implementation.",
    )
    for phrase in slc_branch_identity_matrix:
        matrix_failures = _validate_slice_slc_seam_model_text(
            f"""
# Invalid SLC Branch Identity Matrix Case

SLC is shorthand for Slice and remains a Slice-level deliverable.
{phrase}
"""
        )
        if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(matrix_failures):
            failures.append(
                "Invalid SLC branch identity matrix fixture did not reject: "
                + phrase
            )

    branch_planning_alias_failures = _validate_slice_slc_seam_model_text(
        """
# Valid SLC Branch-Planning Alias Wording

SLC is a branch-planning alias for Slice-level line items and preserved
historical Slice IDs, not a seam or separate branch.
"""
    )
    if branch_planning_alias_failures:
        failures.append(
            "Valid SLC branch-planning alias fixture unexpectedly failed: "
            + "; ".join(branch_planning_alias_failures[:5])
        )

    branch_material_alias_failures = _validate_slice_slc_seam_model_text(
        """
# Valid SLC Branch-Material Alias Wording

SLC is shorthand for Slice and remains a Slice-level deliverable.
SLC-001 branch-material scaffolding is historical wording for one Slice-level
line item, not a seam or separate branch.
"""
    )
    if branch_material_alias_failures:
        failures.append(
            "Valid SLC branch-material alias fixture unexpectedly failed: "
            + "; ".join(branch_material_alias_failures[:5])
        )

    negated_same_branch_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Split Decision: Split not required; same branch remains legal because "
            "the slices share one FAM, one package, one selected implementation "
            "route, one owner/worktree, aligned PR timing, and one validation/proof path.",
            "Split Decision: same branch is not legal for this work; split required.",
        )
    )
    if "Multi-slice carrier must prove why the grouped branch is legal" not in "\n".join(
        negated_same_branch_failures
    ):
        failures.append(
            "Invalid negated same-branch multi-slice fixture did not reject split-required wording"
        )

    undecided_same_branch_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Split Decision: Split not required; same branch remains legal because "
            "the slices share one FAM, one package, one selected implementation "
            "route, one owner/worktree, aligned PR timing, and one validation/proof path.",
            "Split Decision: pending decision whether same branch can remain "
            "legal after USER review.",
        )
    )
    if "Multi-slice carrier must prove why the grouped branch is legal" not in "\n".join(
        undecided_same_branch_failures
    ):
        failures.append(
            "Invalid undecided same-branch multi-slice fixture did not reject "
            "pending split-decision wording"
        )

    affirmative_same_branch_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Split Decision: Split not required; same branch remains legal because "
            "the slices share one FAM, one package, one selected implementation "
            "route, one owner/worktree, aligned PR timing, and one validation/proof path.",
            "Split Decision: The same branch can remain legal because the slices "
            "share one FAM, one package, one selected implementation route, one "
            "owner/worktree, aligned PR timing, and one validation/proof path.",
        )
    )
    if affirmative_same_branch_failures:
        failures.append(
            "Valid affirmative same-branch multi-slice fixture unexpectedly failed: "
            + "; ".join(affirmative_same_branch_failures[:5])
        )

    no_split_required_same_branch_failures = _validate_slice_slc_seam_model_text(
        VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Split Decision: Split not required; same branch remains legal because "
            "the slices share one FAM, one package, one selected implementation "
            "route, one owner/worktree, aligned PR timing, and one validation/proof path.",
            "Split Decision: No split required; same branch remains legal because "
            "the slices share one FAM, one package, one selected implementation "
            "route, one owner/worktree, aligned PR timing, and one validation/proof path.",
        )
    )
    if no_split_required_same_branch_failures:
        failures.append(
            "Valid no-split-required same-branch multi-slice fixture unexpectedly failed: "
            + "; ".join(no_split_required_same_branch_failures[:5])
        )

    no_separate_branch_required_same_branch_failures = (
        _validate_slice_slc_seam_model_text(
            VALID_MULTI_SLICE_IMPLEMENTATION_CARRIER_FIXTURE.read_text(
                encoding="utf-8"
            ).replace(
                "Split Decision: Split not required; same branch remains legal because "
                "the slices share one FAM, one package, one selected implementation "
                "route, one owner/worktree, aligned PR timing, and one validation/proof path.",
                "Split Decision: No separate branch required; same branch remains legal "
                "because the slices share one FAM, one package, one selected "
                "implementation route, one owner/worktree, aligned PR timing, and "
                "one validation/proof path.",
            )
        )
    )
    if no_separate_branch_required_same_branch_failures:
        failures.append(
            "Valid no-separate-branch-required same-branch multi-slice fixture unexpectedly failed: "
            + "; ".join(no_separate_branch_required_same_branch_failures[:5])
        )

    negated_split_required_failures = _validate_slice_slc_seam_model_text(
        VALID_REQUIRED_SEPARATE_BRANCH_CASE_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Split Required: Yes. The private Owner lane memory route must wait "
            "for a separate USER-approved carrier because it crosses private "
            "storage, provider/runtime/cache/memory behavior, and owner/worktree "
            "boundaries.",
            "Split Required: Not required; keep same branch.",
        )
    )
    if (
        "Required separate branch case must explicitly require a split"
        not in "\n".join(negated_split_required_failures)
    ):
        failures.append(
            "Invalid negated required-separate-branch fixture did not reject "
            "not-required same-branch wording"
        )

    generic_required_split_failures = _validate_slice_slc_seam_model_text(
        VALID_REQUIRED_SEPARATE_BRANCH_CASE_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Split Required: Yes. The private Owner lane memory route must wait "
            "for a separate USER-approved carrier because it crosses private "
            "storage, provider/runtime/cache/memory behavior, and owner/worktree "
            "boundaries.",
            "Split Required: USER approval required before deciding whether to split.",
        )
    )
    if (
        "Required separate branch case must explicitly require a split"
        not in "\n".join(generic_required_split_failures)
    ):
        failures.append(
            "Invalid generic-required separate-branch fixture did not reject "
            "undecided split wording"
        )

    blocked_same_branch_required_split_failures = _validate_slice_slc_seam_model_text(
        VALID_REQUIRED_SEPARATE_BRANCH_CASE_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Split Required: Yes. The private Owner lane memory route must wait "
            "for a separate USER-approved carrier because it crosses private "
            "storage, provider/runtime/cache/memory behavior, and owner/worktree "
            "boundaries.",
            "Split Required: Yes. Same branch is blocked; separate branch required "
            "because the route crosses private storage, provider/runtime/cache/memory "
            "behavior, and owner/worktree boundaries.",
        )
    )
    if blocked_same_branch_required_split_failures:
        failures.append(
            "Valid blocked-same-branch required-separate-branch fixture "
            "unexpectedly failed: "
            + "; ".join(blocked_same_branch_required_split_failures[:5])
        )

    planning_only_route_failures = _validate_implementation_bearing_route_text(
        INVALID_IMPLEMENTATION_ROUTE_PLANNING_ONLY_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_IMPLEMENTATION_ROUTE_FAILURE_SNIPPET not in "\n".join(
        planning_only_route_failures
    ):
        failures.append(
            "Invalid planning-only implementation-route fixture did not reject "
            "lane/setup-only carrier admission"
        )

    for fixture, label in (
        (
            VALID_IMPLEMENTATION_ROUTE_SECURITY_BOUNDARY_FIXTURE,
            "security/trust-boundary implementation route",
        ),
        (
            VALID_IMPLEMENTATION_ROUTE_BP2_HOLD_ACTION_GATE_FIXTURE,
            "BP2 HOLD exact USER action gate route",
        ),
        (
            VALID_IMPLEMENTATION_ROUTE_RETARGET_RENAME_FIXTURE,
            "retarget/rename implementation route",
        ),
    ):
        route_failures = _validate_implementation_bearing_route_text(
            fixture.read_text(encoding="utf-8")
        )
        if route_failures:
            failures.append(
                f"Valid {label} fixture unexpectedly failed: "
                + "; ".join(route_failures[:5])
            )

    external_retarget_failures = external_state.validate_implementation_route_values(
        VALID_IMPLEMENTATION_ROUTE_RETARGET_RENAME_FIXTURE.read_text(encoding="utf-8")
    )
    if external_retarget_failures:
        failures.append(
            "External-state validator retarget/rename fixture unexpectedly failed: "
            + "; ".join(external_retarget_failures[:5])
        )

    br2_blocker_failures = _validate_br2_route_blocker_packet_text(
        VALID_BR2_ROUTE_BLOCKER_PACKET_FIXTURE.read_text(encoding="utf-8")
    )
    if br2_blocker_failures:
        failures.append(
            "Valid BR2 route blocker packet fixture unexpectedly failed: "
            + "; ".join(br2_blocker_failures[:5])
        )

    br2_none_word_failures = _validate_br2_route_blocker_packet_text(
        VALID_BR2_ROUTE_BLOCKER_NONE_WORD_ROUTE_FIXTURE.read_text(encoding="utf-8")
    )
    if br2_none_word_failures:
        failures.append(
            "Valid BR2 none-word route blocker packet fixture unexpectedly failed: "
            + "; ".join(br2_none_word_failures[:5])
        )

    no_route_continue_failures = _validate_br2_route_blocker_packet_text(
        INVALID_BR2_ROUTE_BLOCKER_NO_ROUTE_CONTINUE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_BR2_NO_ROUTE_CONTINUE_FAILURE_SNIPPET not in "\n".join(
        no_route_continue_failures
    ):
        failures.append(
            "Invalid BR2 no-route continue-planning fixture did not reject "
            "continued planning after no concrete route remained"
        )

    marker_only_deferral_failures = _validate_br2_route_blocker_packet_text(
        INVALID_BR2_ROUTE_BLOCKER_MARKER_ONLY_DEFERRAL_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_BR2_MARKER_ONLY_DEFERRAL_FAILURE_SNIPPET not in "\n".join(
        marker_only_deferral_failures
    ):
        failures.append(
            "Invalid BR2 marker-only deferral fixture did not reject missing "
            "deferral decision wording outside marker labels"
        )

    fake_feature_label_failures = _validate_implementation_bearing_route_text(
        INVALID_IMPLEMENTATION_ROUTE_FAKE_FEATURE_LABEL_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_FAKE_FEATURE_LABEL_FAILURE_SNIPPET not in "\n".join(
        fake_feature_label_failures
    ):
        failures.append(
            "Invalid fake-feature-label implementation-route fixture did not "
            "reject setup/readiness/packet feature wording"
        )

    proof_boundary_label_failures = _validate_implementation_bearing_route_text(
        INVALID_IMPLEMENTATION_ROUTE_PROOF_BOUNDARY_LABEL_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_PROOF_BOUNDARY_LABEL_FAILURE_SNIPPET not in "\n".join(
        proof_boundary_label_failures
    ):
        failures.append(
            "Invalid proof/boundary-label implementation-route fixture did not "
            "reject proof or boundary-control wording without implemented behavior"
        )

    tbd_output_failures = _validate_implementation_bearing_route_text(
        INVALID_IMPLEMENTATION_ROUTE_TBD_OUTPUT_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_TBD_IMPLEMENTATION_OUTPUT_FAILURE_SNIPPET not in "\n".join(
        tbd_output_failures
    ):
        failures.append(
            "Invalid TBD implementation-output fixture did not reject BP2-will-decide-later wording"
        )

    blank_selected_route_failures = _validate_implementation_bearing_route_text(
        INVALID_IMPLEMENTATION_ROUTE_BLANK_SELECTED_ROUTE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_BLANK_SELECTED_ROUTE_FAILURE_SNIPPET not in "\n".join(
        blank_selected_route_failures
    ):
        failures.append(
            "Invalid blank selected-route fixture did not reject missing route marker value"
        )

    negated_route_behavior_failures = _validate_implementation_bearing_route_text(
        INVALID_IMPLEMENTATION_ROUTE_NEGATED_BEHAVIOR_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_NEGATED_ROUTE_BEHAVIOR_FAILURE_SNIPPET not in "\n".join(
        negated_route_behavior_failures
    ):
        failures.append(
            "Invalid negated-behavior route fixture did not reject explicit "
            "non-implementation wording"
        )

    proof_only_br2_failures = _validate_br2_route_blocker_packet_text(
        INVALID_BR2_ROUTE_BLOCKER_PROOF_ONLY_ROUTE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_BR2_PROOF_ONLY_ROUTE_FAILURE_SNIPPET not in "\n".join(
        proof_only_br2_failures
    ):
        failures.append(
            "Invalid BR2 proof-only route fixture did not reject proof/readiness route wording"
        )

    active_external_source = inspect.getsource(_validate_active_external_branch_plan_posture)
    if 'Path("C:/Nexus Governance State")' in active_external_source:
        failures.append(
            "Active external branch-plan posture validation must use DEFAULT_EXTERNAL_STATE_ROOT"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_state_root = Path(temp_dir)
        temp_central = temp_state_root / "central"
        temp_branch = temp_state_root / "branches" / "feature_fixture"
        temp_central.mkdir(parents=True)
        temp_branch.mkdir(parents=True)
        temp_plan = temp_branch / "branch_plan.md"
        temp_plan.write_text(
            "# Fixture Active Branch Plan\n\n"
            "Selected Implementation Route: Concrete control shell\n",
            encoding="utf-8",
        )
        (temp_central / "active_branch_authority_state.md").write_text(
            "# Fixture Active Branch Authority State\n\n"
            f"Branch Runtime Engineering Plan: `{temp_plan}`\n"
            "Next Legal Phase: `BP1 USER Branch Vision Review`\n",
            encoding="utf-8",
        )
        central_only_failures = _validate_active_external_branch_plan_posture(
            temp_state_root
        )
        external_validator_failures = external_state.validate_active_branch_plan_posture(
            temp_state_root
        )
        if (
            "External active branch state routes to BP1 without implementation-bearing route fields in active branch plan"
            not in "\n".join(central_only_failures)
        ):
            failures.append(
                "Central active-state Next Legal Phase fixture did not reject "
                "missing implementation-bearing route fields"
            )
        if (
            "External active branch state routes to BP1 without implementation-bearing route fields in active branch plan"
            not in "\n".join(external_validator_failures)
        ):
            failures.append(
                "External-state validator fixture did not reject missing "
                "implementation-bearing route fields"
            )
        temp_plan.write_text(
            "# Fixture Active Branch Plan\n\n"
            "Selected Implementation Route: Planning feature for later branch selection\n"
            "Implementation Route Class: governance/source-truth planning\n"
            "Concrete Deliverable: Readiness proof packet that documents route options only\n"
            "Implementation Output: BP2 will decide implementation output later\n"
            "Infrastructure / Setup Relationship: Lane setup only\n"
            "USER Action Gate: USER chooses later after more options\n"
            "Route Disposition: PROCEED\n"
            "Retarget / Rename Recommendation: None\n",
            encoding="utf-8",
        )
        marker_only_route_failures = external_state.validate_active_branch_plan_posture(
            temp_state_root
        )
        marker_only_route_failure_text = "\n".join(marker_only_route_failures)
        if (
            "External active branch plan route values cannot defer implementation output"
            not in marker_only_route_failure_text
            or "External active branch plan route values cannot label planning"
            not in marker_only_route_failure_text
        ):
            failures.append(
                "External-state validator fixture did not reject populated "
                "planning-only/TBD route values"
            )

        temp_plan.write_text(
            "# Fixture Active Branch Plan\n\n"
            "- Selected Implementation Route: Implement source-truth validator "
            "control for security trust-boundary enforcement behavior\n"
            "- Implementation Route Class: governance/source-truth validator "
            "implementation\n"
            "- Concrete Deliverable: Validator enforcement behavior blocks public "
            "provider execution when required consent markers are missing.\n"
            "- Implementation Output: Workstream implements validator behavior "
            "that rejects unsafe public trust-boundary state transitions before "
            "BP1.\n"
            "- Infrastructure / Setup Relationship: Execution-enabling for the "
            "selected implementation route and exact USER action gate.\n"
            "- USER Action Gate: USER approves this implementation-bearing "
            "validation route before BP1 proceeds.\n"
            "- Route Disposition: PROCEED\n"
            "- Retarget / Rename Recommendation: None\n\n"
            "SLC is the seam.\n",
            encoding="utf-8",
        )
        external_terminology_failures = (
            external_state.validate_active_branch_plan_posture(temp_state_root)
        )
        if EXPECTED_SLC_SLICE_SEAM_FAILURE_SNIPPET not in "\n".join(
            external_terminology_failures
        ):
            failures.append(
                "External-state validator fixture did not reject active branch-plan "
                "SLC/Slice/Seam terminology ambiguity"
            )

        temp_plan.write_text(
            "# Fixture Active Branch Plan\n\n"
            "- Selected Implementation Route: Implement source-truth validator "
            "control for security trust-boundary enforcement behavior\n"
            "- Implementation Route Class: governance/source-truth validator "
            "implementation\n"
            "- Concrete Deliverable: Validator enforcement behavior blocks public "
            "provider execution when required consent markers are missing.\n"
            "- Implementation Output: Workstream implements validator behavior "
            "that rejects unsafe public trust-boundary state transitions before "
            "BP1.\n"
            "- Infrastructure / Setup Relationship: Execution-enabling for the "
            "selected implementation route and exact USER action gate.\n"
            "- USER Action Gate: USER approves this implementation-bearing "
            "validation route before BP1 proceeds.\n"
            "- Route Disposition: PROCEED\n"
            "- Retarget / Rename Recommendation: None\n\n"
            "SLC is shorthand for Slice and remains a Slice-level deliverable, "
            "not a seam or separate branch.\n",
            encoding="utf-8",
        )
        external_shorthand_failures = (
            external_state.validate_active_branch_plan_posture(temp_state_root)
        )
        if external_shorthand_failures:
            failures.append(
                "External-state validator shorthand-for-Slice fixture unexpectedly failed: "
                + "; ".join(external_shorthand_failures[:5])
            )

        temp_plan.write_text(
            "# Fixture Active Branch Plan\n\n"
            "- Selected Implementation Route: Implement source-truth validator "
            "control for security trust-boundary enforcement behavior\n"
            "- Implementation Route Class: governance/source-truth validator "
            "implementation\n"
            "- Concrete Deliverable: Validator enforcement behavior blocks public "
            "provider execution when required consent markers are missing.\n"
            "- Implementation Output: Workstream implements validator behavior "
            "that rejects unsafe public trust-boundary state transitions before "
            "BP1.\n"
            "- Infrastructure / Setup Relationship: Execution-enabling for the "
            "selected implementation route and exact USER action gate.\n"
            "- USER Action Gate: USER approves this implementation-bearing "
            "validation route before BP1 proceeds.\n"
            "- Route Disposition: PROCEED\n"
            "- Retarget / Rename Recommendation: None\n",
            encoding="utf-8",
        )
        (temp_central / "active_branch_authority_state.md").write_text(
            "# Fixture Active Branch Authority State\n\n"
            f"- Branch Runtime Engineering Plan: `{temp_plan}`\n"
            "- Next Legal Phase: `BP1 USER Branch Vision Review`\n",
            encoding="utf-8",
        )
        bulleted_marker_failures = external_state.validate_active_branch_plan_posture(
            temp_state_root
        )
        if bulleted_marker_failures:
            failures.append(
                "External-state validator bulleted-marker fixture unexpectedly failed: "
                + "; ".join(bulleted_marker_failures[:5])
            )

        (temp_central / "active_branch_authority_state.md").write_text(
            "# Fixture Active Branch Authority State\n\n"
            "- Branch Runtime Engineering Plan: Accepted\n"
            f"- Branch Runtime Engineering Plan Path: `{temp_plan}`\n"
            "- Next Legal Phase: `BP1 USER Branch Vision Review`\n",
            encoding="utf-8",
        )
        plan_path_marker_failures = external_state.validate_active_branch_plan_posture(
            temp_state_root
        )
        if plan_path_marker_failures:
            failures.append(
                "External-state validator Branch Runtime Engineering Plan Path fixture "
                "unexpectedly failed: "
                + "; ".join(plan_path_marker_failures[:5])
            )

        temp_plan.write_text(
            "# Fixture Active Branch Plan\n\n"
            "- Selected Implementation Route: Implement source-truth validator "
            "control for security trust-boundary enforcement behavior\n"
            "- Implementation Route Class: governance/source-truth validator "
            "implementation\n"
            "- Concrete Deliverable: Validator enforcement behavior blocks public "
            "provider execution when required consent markers are missing.\n"
            "- Implementation Output: Workstream implements validator behavior "
            "that rejects unsafe public trust-boundary state transitions before "
            "BP1.\n"
            "- Infrastructure / Setup Relationship: Execution-enabling for the "
            "selected implementation route and exact USER action gate.\n"
            "- USER Action Gate: USER approves this implementation-bearing "
            "validation route before BP1 proceeds.\n"
            "- Route Disposition: hold\n"
            "- Retarget / Rename Recommendation: None\n",
            encoding="utf-8",
        )
        lowercase_hold_failures = external_state.validate_active_branch_plan_posture(
            temp_state_root
        )
        if (
            "External active branch state routes to BP1 while active branch plan "
            "is still HOLD/RETARGET route resolution"
            not in "\n".join(lowercase_hold_failures)
        ):
            failures.append(
                "External-state validator fixture did not reject lowercase "
                "HOLD/RETARGET route disposition before BP1"
            )

    active_packet_metadata_failures = _validate_user_packet_metadata_text(
        INVALID_USER_PACKET_ACTIVE_BRANCH_METADATA_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_USER_PACKET_ACTIVE_METADATA_FAILURE_SNIPPET not in "\n".join(
        active_packet_metadata_failures
    ):
        failures.append(
            "Invalid USER packet active-metadata fixture did not reject branch metadata"
        )

    zip_hash_packet_failures = _validate_user_packet_metadata_text(
        INVALID_USER_PACKET_ZIP_HASH_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_USER_PACKET_ZIP_HASH_FAILURE_SNIPPET not in "\n".join(
        zip_hash_packet_failures
    ):
        failures.append(
            "Invalid USER packet ZIP-hash fixture did not reject hash metadata"
        )

    desktop_upload_packet_failures = _validate_user_packet_metadata_text(
        INVALID_USER_PACKET_DESKTOP_ACTIVE_UPLOAD_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_USER_PACKET_DESKTOP_ACTIVE_UPLOAD_FAILURE_SNIPPET not in "\n".join(
        desktop_upload_packet_failures
    ):
        failures.append(
            "Invalid USER packet Desktop/OneDrive upload fixture did not reject active upload path"
        )

    valid_merge_stable_failures = _validate_merge_stable_projection_text(
        VALID_MERGE_STABLE_SOURCE_TRUTH_PROJECTION_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_merge_stable_failures:
        failures.append(
            "Valid Merge-Stable Source Truth Projection fixture unexpectedly failed: "
            + "; ".join(valid_merge_stable_failures[:5])
        )

    invalid_merge_stable_failures = _validate_merge_stable_projection_text(
        INVALID_MERGE_STABLE_SOURCE_TRUTH_PROJECTION_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_MERGE_STABLE_PROJECTION_FAILURE_SNIPPET not in "\n".join(
        invalid_merge_stable_failures
    ):
        failures.append(
            "Invalid Merge-Stable Source Truth Projection fixture did not reject "
            "stale PR creation pending wording"
        )

    valid_cross_fam_text = VALID_CROSS_FAM_DEPENDENCY_CANDIDATE_FIXTURE.read_text(
        encoding="utf-8"
    )
    valid_cross_fam_failures = _validate_cross_fam_dependency_packet_text(
        valid_cross_fam_text
    )
    if valid_cross_fam_failures:
        failures.append(
            "Valid cross-FAM dependency candidate fixture unexpectedly failed: "
            + "; ".join(valid_cross_fam_failures[:5])
        )

    for documented_scope_class in (
        "Awareness Only",
        "Compatibility Default",
        "Future Adoption",
    ):
        documented_scope_text = re.sub(
            r"Dependency Scope Class: .+",
            f"Dependency Scope Class: {documented_scope_class}",
            valid_cross_fam_text,
        )
        documented_scope_failures = _validate_cross_fam_dependency_packet_text(
            documented_scope_text
        )
        if documented_scope_failures:
            failures.append(
                "Documented cross-FAM dependency scope class unexpectedly failed "
                f"({documented_scope_class}): "
                + "; ".join(documented_scope_failures[:5])
            )

    invalid_cross_fam_failures = _validate_cross_fam_dependency_packet_text(
        INVALID_CROSS_FAM_DEPENDENCY_UNCLASSIFIED_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_CROSS_FAM_UNCLASSIFIED_FAILURE_SNIPPET not in "\n".join(
        invalid_cross_fam_failures
    ):
        failures.append(
            "Invalid cross-FAM dependency fixture did not reject unclassified "
            "affected-FAM dependency work"
        )

    invalid_cross_fam_text = INVALID_CROSS_FAM_DEPENDENCY_UNCLASSIFIED_FIXTURE.read_text(
        encoding="utf-8"
    )
    mixed_cross_fam_failures = _validate_cross_fam_dependency_packet_text(
        invalid_cross_fam_text + "\n\n" + valid_cross_fam_text
    )
    if EXPECTED_CROSS_FAM_UNCLASSIFIED_FAILURE_SNIPPET not in "\n".join(
        mixed_cross_fam_failures
    ):
        failures.append(
            "Mixed cross-FAM dependency fixture did not reject an invalid record "
            "before a valid record"
        )

    bulleted_mixed_cross_fam_failures = _validate_cross_fam_dependency_packet_text(
        invalid_cross_fam_text.replace(
            "Cross-FAM Dependency Map:", "- Cross-FAM Dependency Map:"
        )
        + "\n\n"
        + valid_cross_fam_text.replace(
            "Cross-FAM Dependency Map:", "- Cross-FAM Dependency Map:"
        )
    )
    if EXPECTED_CROSS_FAM_UNCLASSIFIED_FAILURE_SNIPPET not in "\n".join(
        bulleted_mixed_cross_fam_failures
    ):
        failures.append(
            "Bulleted mixed cross-FAM dependency fixture did not reject an invalid "
            "record before a valid record"
        )

    compact_ffv_owner = _owning_fam_from_ffv(
        Path("Docs/family_feature_visions/F8-FF01.md"),
        "# FAM-008 Packaging Update Visibility\n\n"
        "Durable feature-category direction for packaging, update, and restart continuity.",
    )
    if compact_ffv_owner != "FAM-008":
        failures.append(
            "Compact Family Feature Vision filename fixture did not resolve owning FAM"
        )

    valid_ffv_failures = _validate_family_feature_vision_text(
        VALID_FAMILY_FEATURE_VISION_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_ffv_failures:
        failures.append(
            "Valid Family Feature Vision fixture unexpectedly failed: "
            + "; ".join(valid_ffv_failures[:5])
        )

    slice_scoped_ffv_failures = _validate_family_feature_vision_text(
        INVALID_FAMILY_FEATURE_VISION_SLICE_SCOPED_FIXTURE.read_text(encoding="utf-8")
    )
    if "Family Feature Vision Slice-Scoped" not in "\n".join(slice_scoped_ffv_failures):
        failures.append(
            "Invalid Family Feature Vision slice-scoped fixture did not reject "
            "Slice/SLC/branch-route feature identity"
        )

    live_state_ffv_failures = _validate_family_feature_vision_text(
        INVALID_FAMILY_FEATURE_VISION_LIVE_STATE_FIXTURE.read_text(encoding="utf-8")
    )
    if "FFV Live-State Leakage" not in "\n".join(live_state_ffv_failures):
        failures.append(
            "Invalid Family Feature Vision live-state fixture did not reject "
            "active branch-state wording in deferred carryforward"
        )

    valid_deferred_matrix_failures = _validate_br2_deferred_carryforward_matrix_text(
        VALID_BR2_DEFERRED_CARRYFORWARD_MATRIX_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_deferred_matrix_failures:
        failures.append(
            "Valid BR2 Deferred Carryforward matrix fixture unexpectedly failed: "
            + "; ".join(valid_deferred_matrix_failures[:5])
        )

    invalid_deferred_matrix_failures = _validate_br2_deferred_carryforward_matrix_text(
        INVALID_BR2_DEFERRED_CARRYFORWARD_MATRIX_FIXTURE.read_text(encoding="utf-8")
    )
    if "Deferred Carryforward Applicability Missing" not in "\n".join(
        invalid_deferred_matrix_failures
    ):
        failures.append(
            "Invalid BR2 Deferred Carryforward matrix fixture did not reject "
            "missing applicability/dependency/grouping proof"
        )

    failures.extend(_validate_visual_acceptance_enforcement_fixtures())

    valid_rar_failures = _validate_rebaseline_adoption_review_text(
        VALID_REBASELINE_ADOPTION_REVIEW_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_rar_failures:
        failures.append(
            "Valid RAR adoption review fixture unexpectedly failed: "
            + "; ".join(valid_rar_failures[:5])
        )

    valid_resolved_rar_failures = _validate_rebaseline_adoption_review_text(
        VALID_REBASELINE_ADOPTION_RESOLVED_NORMAL_PHASE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if valid_resolved_rar_failures:
        failures.append(
            "Valid resolved RAR normal-phase fixture unexpectedly failed: "
            + "; ".join(valid_resolved_rar_failures[:5])
        )

    generated_resolved_unresolved_row_text = (
        VALID_REBASELINE_ADOPTION_RESOLVED_NORMAL_PHASE_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Adoption Disposition: Resolved With Evidence after RAR comparison and validation closeout.",
            "Adoption Disposition: RAR comparison completed after validation closeout.",
        )
        .replace(
            "| None | None | Not Applicable With Reason | None | Not Applicable With Reason | Not Applicable With Reason | Not Applicable With Reason | Not Applicable With Reason | CONFORMING | None | Continue |",
            "| HUD Dashboard | Window control cluster | desktop/desktop_renderer.py HUD close control | FAM-006 desktop renderer | focused screenshot packet missing | UIREF-002 | Mismatch | Unproven | NONCONFORMING | unresolved visual mismatch remains | Repair before closeout |",
            1,
        )
    )
    generated_resolved_unresolved_row_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_resolved_unresolved_row_text
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        generated_resolved_unresolved_row_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject resolved RAR with unresolved product-experience row"
        )

    generated_resolved_visual_mismatch_text = (
        VALID_REBASELINE_ADOPTION_RESOLVED_NORMAL_PHASE_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "| None | None | Not Applicable With Reason | None | Not Applicable With Reason | Not Applicable With Reason | Not Applicable With Reason | Not Applicable With Reason | CONFORMING | None | Continue |",
            "| HUD Dashboard | Window control cluster | desktop/desktop_renderer.py | FAM-006 desktop renderer | screenshot | UIREF-002 | Mismatch | Unproven | CONFORMING | comparison columns remain unresolved | Continue |",
        )
    )
    generated_resolved_visual_mismatch_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_resolved_visual_mismatch_text
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        generated_resolved_visual_mismatch_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject resolved RAR with unresolved visual/behavior comparison cells"
        )

    generated_status_green_visual_user_packet_text = (
        VALID_REBASELINE_ADOPTION_NO_USER_REVIEW_REQUIRED_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "| None | None | Not Applicable With Reason | None | Not Applicable With Reason | Not Applicable With Reason | Not Applicable With Reason | Not Applicable With Reason | CONFORMING | None | Continue |",
            "| HUD Dashboard | Window control cluster | desktop/desktop_renderer.py | FAM-006 desktop renderer | screenshot | UIREF-002 | Mismatch | Unproven | CONFORMING | comparison columns remain unresolved | USER waiver required before closeout |",
        )
    )
    generated_status_green_visual_user_packet_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_status_green_visual_user_packet_text
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        generated_status_green_visual_user_packet_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not require a USER packet when unresolved comparison cells requested USER waiver despite CONFORMING status"
        )

    generated_status_green_gap_user_packet_text = (
        VALID_REBASELINE_ADOPTION_NO_USER_REVIEW_REQUIRED_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "| None | None | Not Applicable With Reason | None | Not Applicable With Reason | Not Applicable With Reason | Not Applicable With Reason | Not Applicable With Reason | CONFORMING | None | Continue |",
            "| HUD Dashboard | Window control cluster | desktop/desktop_renderer.py | FAM-006 desktop renderer | screenshot | UIREF-002 | Mismatch | Unproven | CONFORMING | USER visual judgment required for unresolved comparison | Continue |",
        )
    )
    generated_status_green_gap_user_packet_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_status_green_gap_user_packet_text
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        generated_status_green_gap_user_packet_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not require a USER packet when unresolved comparison cells placed USER judgment in Defect / Gap"
        )

    generated_resolved_accepted_reference_gap_text = (
        VALID_REBASELINE_ADOPTION_RESOLVED_NORMAL_PHASE_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "| None | Not Applicable With Reason | Not Applicable With Reason | None | None | None | Not Applicable With Reason | validation summary | None |",
            "| Window control cluster | Accepted Reference | UIREF-002 and FAM-002 | compact placement and Nexus glow | labels may differ | HUD Dashboard | Reference-Derived | screenshot | visual mismatch remains unresolved |",
        )
    )
    generated_resolved_accepted_reference_gap_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_resolved_accepted_reference_gap_text
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        generated_resolved_accepted_reference_gap_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject resolved RAR with unresolved accepted-reference gap cell"
        )

    generated_status_green_reference_user_packet_text = (
        VALID_REBASELINE_ADOPTION_NO_USER_REVIEW_REQUIRED_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "| None | Not Applicable With Reason | Not Applicable With Reason | None | None | None | Not Applicable With Reason | validation summary | No issue candidate applicable |",
            "| Window control cluster | Accepted Reference | UIREF-002 and FAM-002 | compact placement and Nexus glow | labels may differ | HUD Dashboard | Reference-Derived | screenshot | visual mismatch requires USER waiver before closeout |",
        )
    )
    generated_status_green_reference_user_packet_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_status_green_reference_user_packet_text
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        generated_status_green_reference_user_packet_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not require a USER packet when accepted-reference gap cells requested USER waiver"
        )

    valid_reviewed_issue_candidate_rar_failures = (
        _validate_rebaseline_adoption_review_text(
            VALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_REVIEWED_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if valid_reviewed_issue_candidate_rar_failures:
        failures.append(
            "Valid reviewed issue-candidate RAR fixture unexpectedly failed: "
            + "; ".join(valid_reviewed_issue_candidate_rar_failures[:5])
        )

    valid_reviewed_issue_candidate_closed_failures = (
        _validate_rebaseline_adoption_review_text(
            VALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_REVIEWED_CLOSED_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if valid_reviewed_issue_candidate_closed_failures:
        failures.append(
            "Valid reviewed issue-candidate RAR fixture with adoption-closed wording unexpectedly failed: "
            + "; ".join(valid_reviewed_issue_candidate_closed_failures[:5])
        )

    generated_reviewed_issue_candidate_not_blocked_text = (
        VALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_REVIEWED_CLOSED_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Issue Candidate Disposition: Issue Candidate Packet USER-Reviewed for F6-HIST-001, while GitHub issue mutation remains unapproved.",
            "Issue Candidate Disposition: Issue Candidate Packet USER-Reviewed for F6-HIST-001 and not blocked for normal phase progression, while GitHub issue mutation remains unapproved.",
        )
    )
    generated_reviewed_issue_candidate_not_blocked_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_reviewed_issue_candidate_not_blocked_text
        )
    )
    if generated_reviewed_issue_candidate_not_blocked_failures:
        failures.append(
            "Generated RAR adversarial matrix falsely rejected USER-reviewed not-blocked issue-candidate closeout wording: "
            + "; ".join(generated_reviewed_issue_candidate_not_blocked_failures[:5])
        )

    valid_active_negated_disclaimers_rar_failures = (
        _validate_rebaseline_adoption_review_text(
            VALID_REBASELINE_ADOPTION_ACTIVE_NEGATED_DISCLAIMERS_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if valid_active_negated_disclaimers_rar_failures:
        failures.append(
            "Valid active RAR fixture with negated disclaimers failed: "
            + "; ".join(valid_active_negated_disclaimers_rar_failures[:5])
        )

    valid_no_issue_candidate_wording_failures = _validate_rebaseline_adoption_review_text(
        VALID_REBASELINE_ADOPTION_NO_ISSUE_CANDIDATE_WORDING_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if valid_no_issue_candidate_wording_failures:
        failures.append(
            "Valid no-issue-candidate wording RAR fixture unexpectedly failed: "
            + "; ".join(valid_no_issue_candidate_wording_failures[:5])
        )

    valid_no_issue_candidate_gap_failures = _validate_rebaseline_adoption_review_text(
        VALID_REBASELINE_ADOPTION_NO_ISSUE_CANDIDATE_GAP_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if valid_no_issue_candidate_gap_failures:
        failures.append(
            "Valid no-issue-candidate accepted-reference gap RAR fixture unexpectedly failed: "
            + "; ".join(valid_no_issue_candidate_gap_failures[:5])
        )

    valid_no_user_review_required_failures = _validate_rebaseline_adoption_review_text(
        VALID_REBASELINE_ADOPTION_NO_USER_REVIEW_REQUIRED_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if valid_no_user_review_required_failures:
        failures.append(
            "Valid no-USER-review-required RAR fixture unexpectedly failed: "
            + "; ".join(valid_no_user_review_required_failures[:5])
        )

    generated_no_user_approval_required_text = (
        VALID_REBASELINE_ADOPTION_NO_USER_REVIEW_REQUIRED_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "No USER decision needed after resolved no-impact closeout",
            "No USER approval required after resolved no-impact closeout",
        )
    )
    generated_no_user_approval_required_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_no_user_approval_required_text
        )
    )
    if generated_no_user_approval_required_failures:
        failures.append(
            "Generated RAR adversarial matrix falsely rejected no USER approval required wording: "
            + "; ".join(generated_no_user_approval_required_failures[:5])
        )

    generated_no_user_decision_required_text = (
        VALID_REBASELINE_ADOPTION_NO_USER_REVIEW_REQUIRED_FIXTURE.read_text(
            encoding="utf-8"
        ).replace(
            "Exact Next USER Decision: No USER review required for this resolved fixture.",
            "Exact Next USER Decision: Resolved closeout does not require USER decision.",
        )
    )
    generated_no_user_decision_required_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_no_user_decision_required_text
        )
    )
    if generated_no_user_decision_required_failures:
        failures.append(
            "Generated RAR adversarial matrix falsely rejected no USER decision required wording: "
            + "; ".join(generated_no_user_decision_required_failures[:5])
        )

    valid_post_phrase_no_user_decision_failures = (
        _validate_rebaseline_adoption_review_text(
            VALID_REBASELINE_ADOPTION_POST_PHRASE_NO_USER_DECISION_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if valid_post_phrase_no_user_decision_failures:
        failures.append(
            "Valid post-phrase no-USER-decision RAR fixture unexpectedly failed: "
            + "; ".join(valid_post_phrase_no_user_decision_failures[:5])
        )

    valid_short_markers_failures = _validate_rebaseline_adoption_review_text(
        VALID_REBASELINE_ADOPTION_SHORT_MARKERS_FIXTURE.read_text(encoding="utf-8")
    )
    if valid_short_markers_failures:
        failures.append(
            "Valid short-marker RAR fixture unexpectedly failed: "
            + "; ".join(valid_short_markers_failures[:5])
        )

    valid_negated_ready_for_phase_failures = _validate_rebaseline_adoption_review_text(
        VALID_REBASELINE_ADOPTION_NEGATED_READY_FOR_PHASE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if valid_negated_ready_for_phase_failures:
        failures.append(
            "Valid negated-ready-for-phase RAR fixture unexpectedly failed: "
            + "; ".join(valid_negated_ready_for_phase_failures[:5])
        )

    generated_negated_ready_for_phase_text = (
        VALID_REBASELINE_ADOPTION_SHORT_MARKERS_FIXTURE.read_text(encoding="utf-8")
        .replace(
            "Exact Next USER Decision: none",
            "Exact Next USER Decision: not ready for PR Readiness; USER must keep RAR3 active until review closes.",
        )
    )
    generated_negated_ready_for_phase_failures = (
        _validate_rebaseline_adoption_review_text(generated_negated_ready_for_phase_text)
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET in "\n".join(
        generated_negated_ready_for_phase_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix falsely rejected negated ready-for phase wording"
        )

    generated_blocked_phase_disclaimer_text = (
        VALID_REBASELINE_ADOPTION_ACTIVE_NEGATED_DISCLAIMERS_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Exact Next USER Decision: USER reviews RAR issue candidates; normal phase progression is not authorized; this does not authorize PR creation, merge, or release.",
            "Exact Next USER Decision: USER keeps Workstream blocked until RAR3 closes; PR creation remains blocked pending separate approval.",
        )
    )
    generated_blocked_phase_disclaimer_failures = (
        _validate_rebaseline_adoption_review_text(generated_blocked_phase_disclaimer_text)
    )
    if generated_blocked_phase_disclaimer_failures:
        failures.append(
            "Generated RAR adversarial matrix falsely rejected blocked/held phase disclaimer wording: "
            + "; ".join(generated_blocked_phase_disclaimer_failures[:5])
        )

    valid_direct_negated_green_failures = _validate_rebaseline_adoption_review_text(
        VALID_REBASELINE_ADOPTION_DIRECT_NEGATED_GREEN_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if valid_direct_negated_green_failures:
        failures.append(
            "Valid direct-negated green RAR fixture unexpectedly failed: "
            + "; ".join(valid_direct_negated_green_failures[:5])
        )

    valid_resolved_negated_blocker_failures = (
        _validate_rebaseline_adoption_review_text(
            VALID_REBASELINE_ADOPTION_RESOLVED_NEGATED_BLOCKER_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if valid_resolved_negated_blocker_failures:
        failures.append(
            "Valid resolved RAR fixture with negated blocker wording failed: "
            + "; ".join(valid_resolved_negated_blocker_failures[:5])
        )

    missing_code_trace_marker_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MISSING_CODE_TRACE_MARKER_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if "Rebaseline Adoption Review Missing: Code-To-Visual Trace Matrix:" not in "\n".join(
        missing_code_trace_marker_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing Code-To-Visual Trace Matrix marker"
        )

    marker_only_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MARKER_ONLY_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_RAR_MARKER_ONLY_FAILURE_SNIPPET not in "\n".join(
        marker_only_rar_failures
    ):
        failures.append(
            "Invalid marker-only RAR fixture did not reject shallow adoption markers"
        )

    missing_next_legal_phase_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MISSING_NEXT_LEGAL_PHASE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_MARKER_ONLY_FAILURE_SNIPPET not in "\n".join(
        missing_next_legal_phase_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing Next Legal Phase marker"
        )

    missing_product_experience_comparison_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_MISSING_PRODUCT_EXPERIENCE_COMPARISON_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if "NDAI Product Experience Contract Comparison Missing" not in "\n".join(
        missing_product_experience_comparison_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject Product Experience quality terms missing from comparison marker"
        )

    repo_live_state_tracking_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_REPO_LIVE_STATE_TRACKING_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if "RAR Live Adoption Ledger In Repo" not in "\n".join(
        repo_live_state_tracking_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject repo live-state tracking despite external-state mention"
        )

    unanchored_stage_resolved_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_UNANCHORED_STAGE_RESOLVED_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_STAGE_FAILURE_SNIPPET not in "\n".join(
        unanchored_stage_resolved_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject unanchored resolved stage wording"
        )

    negated_resolved_stage_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_NEGATED_RESOLVED_STAGE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_STAGE_FAILURE_SNIPPET not in "\n".join(
        negated_resolved_stage_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject negated resolved stage wording"
        )

    unanchored_stage_no_impact_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_UNANCHORED_STAGE_NO_IMPACT_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_STAGE_FAILURE_SNIPPET not in "\n".join(
        unanchored_stage_no_impact_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject unanchored no-impact stage wording"
        )

    missing_code_trace_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MISSING_CODE_TRACE_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in "\n".join(
        missing_code_trace_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing code-to-visual trace"
        )

    empty_code_trace_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_EMPTY_CODE_TRACE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in "\n".join(
        empty_code_trace_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject header-only code-to-visual trace"
        )

    noop_active_rows_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_NOOP_ACTIVE_ROWS_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in "\n".join(
        noop_active_rows_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject no-op active evidence rows"
        )

    missing_proof_surface_noop_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MISSING_PROOF_SURFACE_NOOP_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in "\n".join(
        missing_proof_surface_noop_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject no-op rows when active surfaces are phrased as missing proof"
        )

    generated_missing_proof_surface_text = (
        INVALID_REBASELINE_ADOPTION_NOOP_ACTIVE_ROWS_FIXTURE.read_text(encoding="utf-8")
        .replace(
            "Owned Surface Inventory: HUD Dashboard, Recording Studio, and Log Viewer Studio surfaces.",
            "Owned Surface Inventory: no verified proof yet for Recording Studio surface; Log Viewer Studio surface remains named for review.",
        )
        .replace(
            "Affected Surface Inventory: Recording Studio window controls, Log Viewer Studio controls, HUD Dashboard close control, buttons, rows, and scrollbars.",
            "Affected Surface Inventory: no focused proof yet for Recording Studio surface and Log Viewer Studio surface.",
        )
    )
    generated_missing_proof_surface_failures = _validate_rebaseline_adoption_review_text(
        generated_missing_proof_surface_text
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in "\n".join(
        generated_missing_proof_surface_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject missing-proof surface wording with no-op rows"
        )

    generated_resolved_surface_noop_text = (
        INVALID_REBASELINE_ADOPTION_NOOP_ACTIVE_ROWS_FIXTURE.read_text(encoding="utf-8")
        .replace(
            "RAR Stage: RAR3 USER Review Gate remains active for affected surface review.",
            "RAR Stage: Resolved after RAR4 disposition and validation closeout.",
        )
        .replace(
            "Next Legal Phase: RAR3 USER Review Gate remains active until USER reviews issue candidates or waives them.",
            "Next Legal Phase: normal phase progression after resolved RAR closeout.",
        )
    )
    generated_resolved_surface_noop_failures = _validate_rebaseline_adoption_review_text(
        generated_resolved_surface_noop_text
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in "\n".join(
        generated_resolved_surface_noop_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject resolved RAR with named surfaces and no-op trace rows"
        )

    partial_noop_active_rows_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PARTIAL_NOOP_ACTIVE_ROWS_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in "\n".join(
        partial_noop_active_rows_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject partial no-op active evidence rows"
        )

    empty_accepted_reference_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_EMPTY_ACCEPTED_REFERENCE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if "Accepted Reference Comparator Missing" not in "\n".join(
        empty_accepted_reference_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject header-only accepted-reference comparator"
        )

    malformed_table_rows_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MALFORMED_TABLE_ROWS_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    malformed_table_failures_joined = "\n".join(malformed_table_rows_rar_failures)
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in malformed_table_failures_joined:
        failures.append("Invalid RAR fixture did not reject malformed code-trace row")
    if "Accepted Reference Comparator Missing" not in malformed_table_failures_joined:
        failures.append(
            "Invalid RAR fixture did not reject malformed accepted-reference row"
        )

    table_preface_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_TABLE_PREFACE_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in "\n".join(
        table_preface_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject non-table text before table separator"
        )

    header_only_rar_decision_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_HEADER_ONLY_RAR_DECISION_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        header_only_rar_decision_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject header-only USER decision table"
        )

    missing_table_separator_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MISSING_TABLE_SEPARATOR_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    missing_table_separator_failures_joined = "\n".join(
        missing_table_separator_rar_failures
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in missing_table_separator_failures_joined:
        failures.append(
            "Invalid RAR fixture did not reject code-trace rows without a markdown separator"
        )
    if "Accepted Reference Comparator Missing" not in missing_table_separator_failures_joined:
        failures.append(
            "Invalid RAR fixture did not reject accepted-reference rows without a markdown separator"
        )

    overwide_table_rows_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_OVERWIDE_TABLE_ROWS_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    overwide_table_failures_joined = "\n".join(overwide_table_rows_rar_failures)
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in overwide_table_failures_joined:
        failures.append("Invalid RAR fixture did not reject overwide code-trace row")
    if "Accepted Reference Comparator Missing" not in overwide_table_failures_joined:
        failures.append(
            "Invalid RAR fixture did not reject overwide accepted-reference row"
        )

    sparse_table_rows_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_SPARSE_TABLE_ROWS_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    sparse_table_failures_joined = "\n".join(sparse_table_rows_rar_failures)
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET not in sparse_table_failures_joined:
        failures.append(
            "Invalid RAR fixture did not reject sparse code-trace row"
        )
    if "Accepted Reference Comparator Missing" not in sparse_table_failures_joined:
        failures.append(
            "Invalid RAR fixture did not reject sparse accepted-reference row"
        )

    unresolved_green_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_UNRESOLVED_GREEN_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        unresolved_green_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject unresolved nonconformance claimed green"
        )

    unresolved_hyphenated_nonconformance_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_UNRESOLVED_HYPHENATED_NONCONFORMANCE_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        unresolved_hyphenated_nonconformance_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject hyphenated non-conforming status claimed green"
        )

    unresolved_green_separate_negation_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_UNRESOLVED_GREEN_SEPARATE_NEGATION_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        unresolved_green_separate_negation_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject unresolved green claim with separate negation"
        )

    unresolved_green_conjunction_negation_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_UNRESOLVED_GREEN_CONJUNCTION_NEGATION_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        unresolved_green_conjunction_negation_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject unresolved green claim after unrelated negation"
        )

    unresolved_no_issue_candidate_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_UNRESOLVED_NO_ISSUE_CANDIDATE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        unresolved_no_issue_candidate_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject unresolved status with no issue-candidate wording"
        )

    validation_summary_green_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_VALIDATION_SUMMARY_GREEN_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        validation_summary_green_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject unresolved green claim outside Adoption Disposition"
        )

    issue_candidate_green_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_GREEN_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        issue_candidate_green_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject issue candidate row claimed green"
        )

    missing_issue_candidate_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MISSING_ISSUE_CANDIDATE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        missing_issue_candidate_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing historical issue candidate disposition"
        )

    prefixed_no_candidate_prose_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PREFIXED_NO_CANDIDATE_PROSE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        prefixed_no_candidate_prose_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject prefixed no-candidate prose naming a candidate"
        )

    hyphenated_no_candidate_prose_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_HYPHENATED_NO_CANDIDATE_PROSE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        hyphenated_no_candidate_prose_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject hyphenated no-candidate prose naming a candidate"
        )

    placeholder_issue_candidate_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PLACEHOLDER_ISSUE_CANDIDATE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        placeholder_issue_candidate_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject placeholder issue-candidate row"
        )

    partial_issue_candidate_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PARTIAL_ISSUE_CANDIDATE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        partial_issue_candidate_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject partial issue-candidate row"
        )

    historical_none_prose_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_HISTORICAL_NONE_PROSE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        historical_none_prose_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject historical issue candidate hidden by none prose"
        )

    standalone_issue_id_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_STANDALONE_ISSUE_ID_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        standalone_issue_id_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject standalone historical issue-candidate ID"
        )

    current_issue_candidate_untabled_rar_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_CURRENT_ISSUE_CANDIDATE_UNTABLED_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        current_issue_candidate_untabled_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject untabled current issue candidate"
        )

    current_marker_issue_candidate_untabled_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_CURRENT_MARKER_ISSUE_CANDIDATE_UNTABLED_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        current_marker_issue_candidate_untabled_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject current-marker issue candidate without issue-candidate row"
        )

    current_issue_candidate_embedded_rar_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_CURRENT_ISSUE_CANDIDATE_EMBEDDED_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        current_issue_candidate_embedded_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject embedded current issue-candidate status"
        )

    current_issue_candidate_hyphenated_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_CURRENT_ISSUE_CANDIDATE_HYPHENATED_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        current_issue_candidate_hyphenated_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject hyphenated current issue-candidate status"
        )

    current_issue_candidate_positive_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_CURRENT_ISSUE_CANDIDATE_POSITIVE_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        current_issue_candidate_positive_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject positive current issue-candidate status"
        )

    generated_issue_candidate_base_text = (
        VALID_REBASELINE_ADOPTION_SHORT_MARKERS_FIXTURE.read_text(encoding="utf-8")
    )
    generated_issue_candidate_base_row = (
        "| None | None | Not Applicable With Reason | None | Not Applicable With Reason | "
        "Not Applicable With Reason | Not Applicable With Reason | "
        "Not Applicable With Reason | CONFORMING | None | Continue |"
    )
    for generated_issue_candidate_status in (
        "ISSUE CANDIDATE",
        "ISSUE-CANDIDATE",
        "CURRENT ISSUE CANDIDATE",
        "CURRENT-ISSUE-CANDIDATE",
        "CURRENT / ISSUE CANDIDATE",
        "CURRENT/ISSUE-CANDIDATE",
        "UNRESOLVED ISSUE CANDIDATE",
        "PENDING ISSUE-CANDIDATE",
    ):
        generated_issue_candidate_text = generated_issue_candidate_base_text.replace(
            generated_issue_candidate_base_row,
            "| HUD Dashboard | Close control | desktop/desktop_renderer.py | "
            "FAM-006 | screenshot | UIREF-002 | Mismatch | Mismatch | "
            f"{generated_issue_candidate_status} | Large CLOSE pill needs issue routing | "
            "Prepare issue candidate |",
        )
        generated_issue_candidate_failures = _validate_rebaseline_adoption_review_text(
            generated_issue_candidate_text
        )
        generated_issue_candidate_failure_text = "\n".join(
            generated_issue_candidate_failures
        )
        if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in (
            generated_issue_candidate_failure_text
        ) or EXPECTED_RAR_ISSUE_DISPOSITION_FAILURE_SNIPPET not in (
            generated_issue_candidate_failure_text
        ):
            failures.append(
                "Generated RAR adversarial matrix did not reject issue-candidate "
                f"status spelling: {generated_issue_candidate_status}"
            )

    not_yet_user_reviewed_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_NOT_YET_USER_REVIEWED_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_DISPOSITION_FAILURE_SNIPPET not in "\n".join(
        not_yet_user_reviewed_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject not-yet-user-reviewed issue candidate disposition"
        )

    generated_not_fully_user_reviewed_text = (
        INVALID_REBASELINE_ADOPTION_NOT_YET_USER_REVIEWED_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Issue Candidate Disposition: Issue Candidate F6-HIST-001 is not yet user reviewed.",
            "Issue Candidate Disposition: Issue Candidate Packet is not fully USER-Reviewed for F6-HIST-001.",
        )
        .replace(
            "Repair / Waiver / Defer / Route Decision Table: issue candidate F6-HIST-001 is not yet blocked, waived, repaired, or routed.",
            "Repair / Waiver / Defer / Route Decision Table: issue candidate F6-HIST-001 is not fully USER-Reviewed, waived, repaired, or routed.",
        )
    )
    generated_not_fully_user_reviewed_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_not_fully_user_reviewed_text
        )
    )
    if EXPECTED_RAR_ISSUE_DISPOSITION_FAILURE_SNIPPET not in "\n".join(
        generated_not_fully_user_reviewed_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject not-fully-USER-reviewed issue candidate disposition"
        )

    linked_closed_claim_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_LINKED_CLOSED_CLAIM_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_UNRESOLVED_GREEN_FAILURE_SNIPPET not in "\n".join(
        linked_closed_claim_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject linked closed claim with unresolved row"
        )

    accepted_reference_issue_candidate_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_ACCEPTED_REFERENCE_ISSUE_CANDIDATE_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_ISSUE_CANDIDATE_FAILURE_SNIPPET not in "\n".join(
        accepted_reference_issue_candidate_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject accepted-reference issue-candidate status"
        )

    pending_review_no_packet_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PENDING_REVIEW_NO_PACKET_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_CODE_TRACE_FAILURE_SNIPPET in "\n".join(
        pending_review_no_packet_rar_failures
    ):
        failures.append(
            "Invalid pending-review no-packet RAR fixture failed for the wrong reason"
        )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        pending_review_no_packet_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing USER packet for pending review"
        )

    active_review_no_packet_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ACTIVE_REVIEW_NO_PACKET_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        active_review_no_packet_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing USER packet for active review gate"
        )

    required_user_review_no_packet_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_REQUIRED_USER_REVIEW_NO_PACKET_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        required_user_review_no_packet_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject required USER review without packet proof"
        )

    validation_summary_review_no_packet_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_VALIDATION_SUMMARY_REVIEW_NO_PACKET_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        validation_summary_review_no_packet_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject validation-summary review requirement without USER packet"
        )

    user_decision_no_packet_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_USER_DECISION_NO_PACKET_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        user_decision_no_packet_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject required USER decision without packet proof"
        )

    generated_rar_decision_no_packet_text = (
        VALID_REBASELINE_ADOPTION_SHORT_MARKERS_FIXTURE.read_text(encoding="utf-8")
        .replace("RAR Stage: RAR3", "RAR Stage: RAR2")
        .replace(
            r"USER Packet Path: C:\Nexus USER\FAM-006",
            "USER Packet Path: not required",
        )
        .replace(
            r"USER Packet ZIP Path: C:\Nexus USER\FAM-006-20260620-120000.zip.",
            "USER Packet ZIP Path: not required",
        )
        .replace(
            "| None | No issue-candidate decision needed | Nothing new | Runtime mutation, sibling mutation, PR, merge, release, or issue creation |",
            "| Review issue candidate | USER must review the issue candidate before route selection | Reviewability only | Runtime mutation, sibling mutation, PR, merge, release, or issue creation |",
        )
    )
    generated_rar_decision_no_packet_failures = (
        _validate_rebaseline_adoption_review_text(generated_rar_decision_no_packet_text)
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        generated_rar_decision_no_packet_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject USER review wording "
            "inside the RAR decision table without deterministic USER packet proof"
        )

    generated_user_judgment_base_text = (
        VALID_REBASELINE_ADOPTION_SHORT_MARKERS_FIXTURE.read_text(encoding="utf-8")
        .replace("RAR Stage: RAR3", "RAR Stage: RAR2")
        .replace(
            r"USER Packet Path: C:\Nexus USER\FAM-006",
            "USER Packet Path: not required",
        )
        .replace(
            r"USER Packet ZIP Path: C:\Nexus USER\FAM-006-20260620-120000.zip.",
            "USER Packet ZIP Path: not required",
        )
    )
    for generated_user_judgment_marker, generated_user_judgment_value in (
        (
            "Exact Next USER Decision:",
            "USER judgment required before route selection.",
        ),
        (
            "Exact Next USER Decision:",
            "route selection needs USER judgment.",
        ),
        (
            "Next Legal Phase:",
            "USER review required before route selection.",
        ),
        (
            "Repair / Waiver / Blocker:",
            "Requires USER judgment before route selection.",
        ),
        (
            "Validation Summary:",
            "USER adjudication required before normal phase progression.",
        ),
        (
            "Current Violation Findings:",
            "USER visual judgment required before route selection.",
        ),
    ):
        generated_user_judgment_text = re.sub(
            rf"^{re.escape(generated_user_judgment_marker)}.*$",
            lambda _match: (
                f"{generated_user_judgment_marker} {generated_user_judgment_value}"
            ),
            generated_user_judgment_base_text,
            flags=re.MULTILINE,
        )
        generated_user_judgment_failures = _validate_rebaseline_adoption_review_text(
            generated_user_judgment_text
        )
        if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
            generated_user_judgment_failures
        ):
            failures.append(
                "Generated RAR adversarial matrix did not reject USER judgment "
                "wording without deterministic USER packet proof: "
                f"{generated_user_judgment_marker} {generated_user_judgment_value}"
            )

    packet_path_wrong_root_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PACKET_PATH_WRONG_ROOT_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        packet_path_wrong_root_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject USER packet folder outside C:\\Nexus USER"
        )

    packet_path_zip_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PACKET_PATH_ZIP_FIXTURE.read_text(encoding="utf-8")
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        packet_path_zip_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject USER packet folder marker pointing at ZIP"
        )

    packet_path_child_folder_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PACKET_PATH_CHILD_FOLDER_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        packet_path_child_folder_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject USER packet path pointing at a child folder"
        )

    packet_path_traversal_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PACKET_PATH_TRAVERSAL_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        packet_path_traversal_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject traversal USER packet folder path"
        )

    packet_path_explanatory_user_root_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_PACKET_PATH_EXPLANATORY_USER_ROOT_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        packet_path_explanatory_user_root_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject off-root USER packet folder with later root mention"
        )

    packet_path_suffix_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_PACKET_PATH_SUFFIX_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        packet_path_suffix_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject suffixed USER packet folder token"
        )

    generated_rar_short_marker_text = (
        VALID_REBASELINE_ADOPTION_SHORT_MARKERS_FIXTURE.read_text(encoding="utf-8")
    )

    def generated_rar_marker_text(marker: str, value: str) -> str:
        return re.sub(
            rf"^{re.escape(marker)}.*$",
            lambda _match: f"{marker} {value}",
            generated_rar_short_marker_text,
            flags=re.MULTILINE,
        )

    generated_invalid_packet_path_suffixes = (
        r"C:\Nexus USER\FAM-006`extra",
        r"C:\Nexus USER\FAM-006.zip",
        r"C:\Nexus USER\FAM-006.md",
        r"C:\Nexus USER\FAM-006;extra",
        r"C:\Nexus USER\FAM-006,extra",
        r"C:\Nexus USER\FAM-006)extra",
        r"C:\Nexus USER\FAM-006).md",
        r"C:\Nexus USER\FAM-006]extra",
        r"C:\Nexus USER\FAM-006].zip",
        r"C:\Nexus USER\FAM-006:extra",
    )
    for generated_packet_path in generated_invalid_packet_path_suffixes:
        generated_packet_path_failures = _validate_rebaseline_adoption_review_text(
            generated_rar_marker_text("USER Packet Path:", generated_packet_path)
        )
        if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
            generated_packet_path_failures
        ):
            failures.append(
                "Generated RAR adversarial matrix did not reject suffixed "
                f"USER packet folder token: {generated_packet_path}"
            )

    generated_valid_packet_path_wrappers = (
        r"C:\Nexus USER\FAM-006.",
        r"C:\Nexus USER\FAM-006,",
        r"C:\Nexus USER\FAM-006).",
        r"`C:\Nexus USER\FAM-006`.",
    )
    for generated_packet_path in generated_valid_packet_path_wrappers:
        generated_packet_path_failures = _validate_rebaseline_adoption_review_text(
            generated_rar_marker_text("USER Packet Path:", generated_packet_path)
        )
        if generated_packet_path_failures:
            failures.append(
                "Generated RAR adversarial matrix falsely rejected terminal "
                f"USER packet folder punctuation: {generated_packet_path}: "
                + "; ".join(generated_packet_path_failures[:5])
            )

    generated_mismatched_packet_zip_label_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_rar_marker_text(
                "USER Packet ZIP Path:",
                r"C:\Nexus USER\FAM-007-20260620-120000.zip",
            )
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        generated_mismatched_packet_zip_label_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject mismatched USER packet "
            "folder and ZIP worktree labels"
        )

    bare_rar3_no_packet_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_BARE_RAR3_NO_PACKET_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        bare_rar3_no_packet_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing USER packet for bare RAR3 stage"
        )

    unresolved_row_no_packet_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_UNRESOLVED_ROW_NO_PACKET_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        unresolved_row_no_packet_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject unresolved USER-facing row without packet"
        )

    accepted_reference_gap_no_packet_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ACCEPTED_REFERENCE_GAP_NO_PACKET_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        accepted_reference_gap_no_packet_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject accepted-reference USER-review gap without packet"
        )

    generated_accepted_reference_gap_text = (
        INVALID_REBASELINE_ADOPTION_UNRESOLVED_ROW_NO_PACKET_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "| HUD Dashboard | Window control cluster | desktop/desktop_renderer.py HUD close region | FAM-006 desktop renderer | focused screenshot packet | UIREF-002 and AI Control Center seed | Mismatch | Unproven | NONCONFORMING | USER visual judgment required for close-control treatment | USER visual judgment decides repair or waiver |",
            "| HUD Dashboard | Window control cluster | desktop/desktop_renderer.py HUD close region | FAM-006 desktop renderer | focused screenshot packet | UIREF-002 and AI Control Center seed | Match | Match | CONFORMING | None | Continue after accepted-reference review |",
        )
        .replace(
            "| Window control cluster | Accepted Reference | UIREF-002 and FAM-002 | compact placement and Nexus glow | labels may differ | HUD Dashboard | Reference-Derived | screenshot | visual judgment packet missing |",
            "| Window control cluster | Accepted Reference | UIREF-002 and FAM-002 | compact placement and Nexus glow | labels may differ | HUD Dashboard | Reference-Derived | screenshot | REFERENCE GAP - USER review / waiver required before route |",
        )
    )
    generated_accepted_reference_gap_failures = _validate_rebaseline_adoption_review_text(
        generated_accepted_reference_gap_text
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        generated_accepted_reference_gap_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject accepted-reference USER-review gap without packet"
        )

    contradictory_no_decision_no_packet_rar_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_CONTRADICTORY_NO_DECISION_NO_PACKET_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        contradictory_no_decision_no_packet_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing USER packet for contradictory active review gate"
        )

    zip_outside_user_root_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ZIP_OUTSIDE_USER_ROOT_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        zip_outside_user_root_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject USER packet ZIP outside C:\\Nexus USER"
        )

    zip_child_folder_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ZIP_CHILD_FOLDER_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        zip_child_folder_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject USER packet ZIP inside packet folder"
        )

    zip_spaced_offroot_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ZIP_SPACED_OFFROOT_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        zip_spaced_offroot_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject spaced off-root USER packet ZIP"
        )

    zip_explanatory_user_root_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ZIP_EXPLANATORY_USER_ROOT_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        zip_explanatory_user_root_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject off-root ZIP path with earlier USER-root mention"
        )

    zip_suffix_path_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ZIP_SUFFIX_PATH_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        zip_suffix_path_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject suffixed non-ZIP USER packet path"
        )

    generated_invalid_zip_suffixes = (
        r"C:\Nexus USER\FAM-006-20260620-120000.zip.tmp",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip`extra",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip;extra",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip,extra",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip)extra",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip).tmp",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip]extra",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip].md",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip:extra",
    )
    for generated_zip_path in generated_invalid_zip_suffixes:
        generated_zip_path_failures = _validate_rebaseline_adoption_review_text(
            generated_rar_marker_text("USER Packet ZIP Path:", generated_zip_path)
        )
        if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
            generated_zip_path_failures
        ):
            failures.append(
                "Generated RAR adversarial matrix did not reject suffixed "
                f"USER packet ZIP token: {generated_zip_path}"
            )

    generated_valid_zip_wrappers = (
        r"C:\Nexus USER\FAM-006-20260620-120000.zip.",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip,",
        r"C:\Nexus USER\FAM-006-20260620-120000.zip).",
        r"`C:\Nexus USER\FAM-006-20260620-120000.zip`.",
    )
    for generated_zip_path in generated_valid_zip_wrappers:
        generated_zip_path_failures = _validate_rebaseline_adoption_review_text(
            generated_rar_marker_text("USER Packet ZIP Path:", generated_zip_path)
        )
        if generated_zip_path_failures:
            failures.append(
                "Generated RAR adversarial matrix falsely rejected terminal "
                f"USER packet ZIP punctuation: {generated_zip_path}: "
                + "; ".join(generated_zip_path_failures[:5])
            )

    zip_traversal_path_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ZIP_TRAVERSAL_PATH_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        zip_traversal_path_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject traversal USER packet ZIP path"
        )

    zip_root_traversal_path_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ZIP_ROOT_TRAVERSAL_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_USER_PACKET_FAILURE_SNIPPET not in "\n".join(
        zip_root_traversal_path_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject root-normalizing traversal USER packet ZIP path"
        )

    normal_phase_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_NORMAL_PHASE_WHILE_ACTIVE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        normal_phase_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject normal phase progression while RAR remains active"
        )

    validation_summary_phase_advance_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_VALIDATION_SUMMARY_PHASE_ADVANCE_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        validation_summary_phase_advance_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject validation-summary phase advancement while RAR remains active"
        )

    active_stage_normal_phase_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ACTIVE_STAGE_NORMAL_PHASE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        active_stage_normal_phase_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject normal phase progression for active RAR stage"
        )

    concrete_phase_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_CONCRETE_PHASE_WHILE_ACTIVE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        concrete_phase_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject concrete phase progression while RAR remains active"
        )

    mixed_disclaimer_phase_advance_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MIXED_DISCLAIMER_PHASE_ADVANCE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        mixed_disclaimer_phase_advance_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject mixed disclaimer plus affirmative phase advancement"
        )

    generated_waiver_not_approved_continue_text = (
        INVALID_REBASELINE_ADOPTION_MIXED_DISCLAIMER_PHASE_ADVANCE_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Exact Next USER Decision: this does not authorize PR Readiness but proceeds to Workstream now.",
            "Exact Next USER Decision: waiver not approved so continue to PR Readiness.",
        )
    )
    generated_waiver_not_approved_continue_failures = (
        _validate_rebaseline_adoption_review_text(
            generated_waiver_not_approved_continue_text
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        generated_waiver_not_approved_continue_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject waiver-not-approved phase advancement"
        )

    generated_phase_first_denial_text = (
        INVALID_REBASELINE_ADOPTION_MIXED_DISCLAIMER_PHASE_ADVANCE_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Exact Next USER Decision: this does not authorize PR Readiness but proceeds to Workstream now.",
            "Exact Next USER Decision: PR Readiness is not approved while RAR review remains active.",
        )
    )
    generated_phase_first_denial_failures = "\n".join(
        _validate_rebaseline_adoption_review_text(generated_phase_first_denial_text)
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET in generated_phase_first_denial_failures:
        failures.append(
            "Generated RAR adversarial matrix falsely rejected phase-first denial wording"
        )

    generated_no_release_impact_text = (
        INVALID_REBASELINE_ADOPTION_MIXED_DISCLAIMER_PHASE_ADVANCE_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Exact Next USER Decision: this does not authorize PR Readiness but proceeds to Workstream now.",
            "Exact Next USER Decision: USER reviews RAR issue candidates; no release impact is claimed and normal phase progression remains blocked.",
        )
    )
    generated_no_release_impact_failures = "\n".join(
        _validate_rebaseline_adoption_review_text(generated_no_release_impact_text)
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET in generated_no_release_impact_failures:
        failures.append(
            "Generated RAR adversarial matrix falsely rejected passive no-release-impact wording"
        )

    generated_although_phase_advance_text = (
        INVALID_REBASELINE_ADOPTION_MIXED_DISCLAIMER_PHASE_ADVANCE_FIXTURE.read_text(
            encoding="utf-8"
        )
        .replace(
            "Exact Next USER Decision: this does not authorize PR Readiness but proceeds to Workstream now.",
            "Exact Next USER Decision: this does not authorize merge although PR Readiness may proceed.",
        )
    )
    generated_although_phase_advance_failures = (
        _validate_rebaseline_adoption_review_text(generated_although_phase_advance_text)
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        generated_although_phase_advance_failures
    ):
        failures.append(
            "Generated RAR adversarial matrix did not reject although/though/while mixed disclaimer phase advancement"
        )

    comma_mixed_disclaimer_phase_advance_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_COMMA_MIXED_DISCLAIMER_PHASE_ADVANCE_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        comma_mixed_disclaimer_phase_advance_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject comma-mixed disclaimer plus affirmative phase advancement"
        )

    move_into_phase_advance_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_MOVE_INTO_PHASE_ADVANCE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        move_into_phase_advance_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject move-into phase advancement while RAR remains active"
        )

    go_to_phase_advance_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_GO_TO_PHASE_ADVANCE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        go_to_phase_advance_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject go-to phase advancement while RAR remains active"
        )

    bare_phase_next_step_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_BARE_PHASE_NEXT_STEP_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        bare_phase_next_step_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject bare phase next-step wording while RAR remains active"
        )

    not_blocked_phase_advance_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_NOT_BLOCKED_PHASE_ADVANCE_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        not_blocked_phase_advance_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject not-blocked phase advancement while RAR remains active"
        )

    generic_phase_claim_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_GENERIC_PHASE_CLAIM_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_NORMAL_PHASE_FAILURE_SNIPPET not in "\n".join(
        generic_phase_claim_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject generic normal phase progression claim while RAR remains active"
        )

    issue_disposition_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_ISSUE_CANDIDATE_DISPOSITION_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_DISPOSITION_FAILURE_SNIPPET not in "\n".join(
        issue_disposition_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject missing mixed-case issue-candidate disposition"
        )

    negated_issue_disposition_rar_failures = _validate_rebaseline_adoption_review_text(
        INVALID_REBASELINE_ADOPTION_NEGATED_ISSUE_DISPOSITION_FIXTURE.read_text(
            encoding="utf-8"
        )
    )
    if EXPECTED_RAR_ISSUE_DISPOSITION_FAILURE_SNIPPET not in "\n".join(
        negated_issue_disposition_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject negated issue-candidate disposition"
        )

    required_review_not_complete_rar_failures = (
        _validate_rebaseline_adoption_review_text(
            INVALID_REBASELINE_ADOPTION_REQUIRED_REVIEW_NOT_COMPLETE_FIXTURE.read_text(
                encoding="utf-8"
            )
        )
    )
    if EXPECTED_RAR_ISSUE_DISPOSITION_FAILURE_SNIPPET not in "\n".join(
        required_review_not_complete_rar_failures
    ):
        failures.append(
            "Invalid RAR fixture did not reject required-but-incomplete USER review disposition"
        )

    failures.extend(_validate_rar_issue_candidate_durability_fixtures())

    failures.extend(_validate_family_feature_vision_scaffolding_source_truth())
    failures.extend(_validate_current_worktree_family_feature_vision_files())
    failures.extend(_validate_current_worktree_ffv_dependency_records())

    failures.extend(_validate_merge_stable_projection_helpers())

    failures.extend(_validate_rebaseline_overlap_helper_matrix())
    failures.extend(_validate_pr_review_churn_matrix_fixture())

    failures.extend(_validate_user_review_bundle_identity_guard())
    failures.extend(_validate_workstream_entry_packet_existing_bp1_substance_guard())
    failures.extend(_validate_user_review_bundle_export_zip_identity_guard())
    failures.extend(_validate_user_review_bundle_export_zip_cleanup_guard())
    failures.extend(_validate_local_user_packet_folder_zip_guard())
    failures.extend(_validate_active_overlay_user_branch_plan_review_metadata_guard())
    failures.extend(_validate_fam007_workstream_approval_packet_metadata_guard())
    failures.extend(_validate_fam007_bp3_packet_generation_guard())
    failures.extend(_validate_fam006_bp3_packet_generation_guard())
    failures.extend(_validate_fam007_workstream_implementation_packet_priority_guard())
    failures.extend(_validate_fam006_workstream_approval_review_packet_guard())

    try:
        if target_currentness_fixture.main() != 0:
            failures.append("Target-scoped external-state currentness fixture helper returned failure")
    except Exception as exc:  # noqa: BLE001 - fixture failures must become a validation result
        failures.append(f"Target-scoped external-state currentness fixture raised: {exc}")

    return failures


def historical_main() -> int:
    failures = validate()
    if failures:
        print("FAIL: Branch Readiness planning fixture validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: Branch Readiness planning fixture validation passed")
    return 0


def main() -> int:
    import argparse,hashlib,subprocess,sys,tempfile
    import ast,copy
    parser=argparse.ArgumentParser(description='Current binding/refusal fixtures; broad historical planning diagnostics are explicit.')
    parser.add_argument('--historical-diagnostic',action='store_true')
    args=parser.parse_args()
    if args.historical_diagnostic:return historical_main()
    failures=[]
    tree=ast.parse((ROOT/'dev/orin_branch_governance_validation.py').read_bytes())
    nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name=='_current_infrastructure_pr_proof']
    current={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<current infrastructure PR fixtures>','exec'),current)
    current_proof=current['_current_infrastructure_pr_proof']
    facts={'head':'1'*40,'branch':'feature/fixture','mergeBase':'2'*40,'originMain':'2'*40,'dirt':[]}
    assignment={'phase':'PR Readiness','base':'2'*40,'canonicalMainMutation':False}
    qualification={'result':'PASS','sourceSHA256':'A'*64}
    policy={'capture':'DIRECT_GITHUB_API','requiredChecks':[{'context':'fixture','appId':None}],'requiredReviews':1,'requiresAdditionalReview':False,'requiresResolvedConversations':False}
    pr={'state':'OPEN','headRefName':'feature/fixture','headRefOid':'1'*40,'baseRefName':'main','isDraft':False,'mergeable':'MERGEABLE','statusCheckRollup':[{'__typename':'CheckRun','name':'fixture','status':'COMPLETED','conclusion':'SUCCESS'}],'reviewDecision':'APPROVED','capturedReviewPolicy':policy}
    review={'result':'PASS','head':'1'*40,'reviewer':'/root/distinct-fixture-reviewer'}
    scenarios=[('infra-positive',{}, {}, {}, {},'PASS'),('infra-missing-PR',{}, {},None,{},'PENDING'),('infra-missing-checks',{}, {},{'statusCheckRollup':[]},{},'PENDING'),('infra-missing-review',{}, {},{},None,'PENDING'),('infra-stale-head',{}, {},{'headRefOid':'0'*40},{},'BLOCK'),('infra-dirty',{'dirt':[' M file']},{},{},{},'BLOCK'),('infra-main-drift',{'originMain':'3'*40},{},{},{},'BLOCK'),('infra-stale-qualification',{}, {'sourceSHA256':'B'*64},{},{},'BLOCK'),('infra-skipped-only',{}, {},{'statusCheckRollup':[{'__typename':'CheckRun','name':'fixture','status':'COMPLETED','conclusion':'SKIPPED'}]},{},'PASS')]
    for label,change_facts,change_q,change_pr,change_review,expected in scenarios:
        result=current_proof({**facts,**change_facts},assignment,{**qualification,**change_q},'A'*64,None if change_pr is None else{**copy.deepcopy(pr),**change_pr},None if change_review is None else{**review,**change_review})
        if result['result']!=expected:failures.append(label+': '+str(result))
    for label,changes in [('infra-closed',{'state':'CLOSED'}),('infra-pending-plus-failure',{'statusCheckRollup':[{'__typename':'CheckRun','name':'fixture','status':'IN_PROGRESS'},{'__typename':'CheckRun','name':'fixture','status':'COMPLETED','conclusion':'FAILURE'}]}),('infra-pending-plus-requested-changes',{'statusCheckRollup':[{'__typename':'CheckRun','name':'fixture','status':'IN_PROGRESS'}],'reviewDecision':'CHANGES_REQUESTED'})]:
        result=current_proof(facts,assignment,qualification,'A'*64,{**copy.deepcopy(pr),**changes},review)
        if result['result']!='BLOCK':failures.append(label+': adverse current evidence hidden as pending')
    result=current_proof(facts,assignment,qualification,'A'*64,{**copy.deepcopy(pr),'statusCheckRollup':[],'reviewDecision':'CHANGES_REQUESTED'},review)
    if result['result']!='BLOCK':failures.append('infra-no-checks-requested-changes: adverse review hidden as pending')
    for label,changes,expected in [('infra-review-required',{'reviewDecision':'REVIEW_REQUIRED'},'PENDING'),('infra-review-null-unverified',{'reviewDecision':None},'PENDING'),('infra-review-null-not-required',{'reviewDecision':None,'capturedReviewPolicy':{**policy,'requiredReviews':0}},'PASS'),('infra-empty-review-not-required',{'reviewDecision':'','statusCheckRollup':[],'capturedReviewPolicy':{**policy,'requiredChecks':[],'requiredReviews':0}},'PASS'),('infra-missing-policy',{'capturedReviewPolicy':None},'PENDING'),('infra-codeowner-review-required',{'reviewDecision':'','capturedReviewPolicy':{**policy,'requiredReviews':0,'requiresAdditionalReview':True}},'PENDING'),('infra-unresolved-conversation',{'capturedReviewPolicy':{**policy,'requiresResolvedConversations':True},'conversationCaptureComplete':True,'unresolvedReviewThreads':1},'PENDING'),('infra-truncated-conversations',{'capturedReviewPolicy':{**policy,'requiresResolvedConversations':True},'conversationCaptureComplete':False,'unresolvedReviewThreads':0},'PENDING'),('infra-conversations-resolved',{'capturedReviewPolicy':{**policy,'requiresResolvedConversations':True},'conversationCaptureComplete':True,'unresolvedReviewThreads':0},'PASS'),('infra-required-provider-unproven',{'capturedReviewPolicy':{**policy,'requiredChecks':[{'context':'fixture','appId':42}]}},'PENDING'),('infra-required-provider-proven',{'capturedReviewPolicy':{**policy,'requiredChecks':[{'context':'fixture','appId':42}]},'capturedProviderRuns':[{'id':1,'name':'fixture','head':'1'*40,'appId':42,'status':'completed','conclusion':'success'}]},'PASS'),('infra-required-provider-failure',{'capturedReviewPolicy':{**policy,'requiredChecks':[{'context':'fixture','appId':42}]},'capturedProviderRuns':[{'id':1,'name':'fixture','head':'1'*40,'appId':42,'status':'completed','conclusion':'failure'}]},'BLOCK'),('infra-malformed-check-name',{'statusCheckRollup':[{'__typename':'CheckRun','name':[],'status':'COMPLETED','conclusion':'SUCCESS'}]},'BLOCK'),('infra-malformed-provider-records',{'capturedProviderRuns':{}},'BLOCK')]:
        result=current_proof(facts,assignment,qualification,'A'*64,{**copy.deepcopy(pr),**changes},review)
        if result['result']!=expected:failures.append(label+': '+str(result))
    main_node=next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name=='main')
    infra=next(node for node in ast.walk(main_node)if isinstance(node,ast.If)and 'SOURCE_TRUTH_GOVERNANCE_INFRASTRUCTURE'in ast.unparse(node.test))
    calls={node.func.id for node in ast.walk(infra)if isinstance(node,ast.Call)and isinstance(node.func,ast.Name)}
    if calls&{'_parse_backlog_sections','_run_pr_readiness_gate','_run_release_readiness_health_gate'}:failures.append('current infrastructure dispatch reaches historical product gate')
    cases=(('current-source',[], 'PASS'),('missing-assignment',['--worktree-confinement-gate'],'BLOCK'),
           ('missing-PR-authority',['--pr-readiness-gate'],'BLOCK'),('missing-release-authority',['--release-readiness-health-gate'],'BLOCK'),
           ('retired-standing-route',['--standing-governance-intake-gate'],'BLOCK'),
           ('source-mode-authority',['--authorization-sha256','A'*64],'BLOCK'))
    for label,operands,expected in cases:
        result=subprocess.run([sys.executable,'-B',str(ROOT/'dev/orin_branch_governance_validation.py'),*operands],cwd=ROOT,capture_output=True,text=True,timeout=20)
        try:
            proof=json.loads(result.stdout)
            if proof.get('result')!=expected or proof.get('executionAuthorized')is not False:raise ValueError('wrong disposition or implicit execution authority')
        except (ValueError,TypeError)as error:failures.append(label+': '+str(error))
    evidence=Path(r'D:\Nexus Desktop AI\USER\Governance\Checkpoint1-Completion-Scoped-Repair-20260911\continuation-000006\connected-repair-20261011')
    count=len(cases)+len(scenarios)+19
    with tempfile.TemporaryDirectory(prefix='product-binding-fixture-',dir=evidence)as directory:
        folder=Path(directory);authority=folder/'owner.md';assignment=folder/'assignment.json'
        approval=Path(r'C:\Users\anden\.codex\attachments\54ab6877-d801-47b3-8c1e-f48e70b2a2f2\Pasted text.txt')
        digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest().upper()
        git=lambda *args:subprocess.check_output(['git','-C',str(ROOT),*args],text=True,timeout=15).strip()
        head=git('rev-parse','HEAD');branch=git('branch','--show-current');base=git('merge-base','HEAD','origin/main')
        body=f'## Current Phase\n\nPhase: `Workstream`\nCurrent HEAD: `{head}`\nBranch: `{branch}`\nWorktree: `{ROOT}`\nPreserved Dirt Disposition: `SOLE_WRITER_PRESERVED`\n'
        authority.write_text(body,encoding='utf8')
        row={'root':str(ROOT),'head':head,'branch':branch,'base':base,'phase':'Workstream','owner':'fixture-only','scope':'read-only fixture','canonicalMainMutation':False,'authorizationSHA256':digest(approval),'selectedOwner':{'path':str(authority),'sha256':digest(authority)}}
        for label,change,expected in [('valid-selected-read-only',{},'PASS'),('wrong-head',{'head':'0'*40},'BLOCK'),('wrong-root',{'root':str(folder)},'BLOCK'),('wrong-phase',{'phase':'Live Validation'},'BLOCK'),('wrong-approval',{'authorizationSHA256':'A'*64},'BLOCK'),('unselected-owner',{'selectedOwner':{'path':str(authority),'sha256':'A'*64}},'BLOCK'),('release-health-inapplicable',{'phase':'Release Readiness'},'BLOCK')]:
            if label=='release-health-inapplicable':
                authority.write_text(body.replace('`Workstream`','`Release Readiness`'),encoding='utf8');change['selectedOwner']={'path':str(authority),'sha256':digest(authority)}
            assignment.write_text(json.dumps({**row,**change}),encoding='utf8')
            operands=['--worktree-confinement-gate','--current-assignment',str(assignment),'--assignment-sha256',digest(assignment),'--approval-file',str(approval),'--authorization-sha256',digest(approval),'--current-authority',str(authority),'--current-authority-sha256',digest(authority)]
            if label=='release-health-inapplicable':operands[0]='--release-readiness-health-gate'
            run=subprocess.run([sys.executable,'-B',str(ROOT/'dev/orin_branch_governance_validation.py'),*operands],cwd=ROOT,capture_output=True,text=True,timeout=20)
            try:
                value=json.loads(run.stdout)
                if value.get('result')!=expected or value.get('executionAuthorized')is not False:raise ValueError(str(value.get('failures')))
            except (ValueError,TypeError)as error:failures.append(label+': '+str(error))
            count+=1
    print(('BLOCK'if failures else 'PASS')+f': {count} current binding/source/refusal fixtures; no actual operational assignment or execution authority created')
    for failure in failures:print('- '+failure)
    return 1 if failures else 0


if __name__=='__main__':raise SystemExit(main())
