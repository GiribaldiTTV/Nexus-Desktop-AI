# Branch Runtime Engineering Plans

`Docs/branch_plans/<branch_slug>.md` defines the Branch Runtime Engineering Plan shape and preserves durable historical branch-plan receipts. After the External Operational State Store transition, active branch planning state lives in `D:\Nexus Desktop AI\Governance State\branches\<branch_slug>\branch_plan.md` until it folds down as durable repo evidence.

Repo branch-plan files are not the long-term place to maintain active ledger rows. While active, detailed plan rows, UFD items, Branch Change Intent rows, Element-to-Phase rows, Workstream Entry review packets, Hardening plans, and Live Validation plans belong in the active external branch planning owner or in an explicitly USER-approved transition packet. Repo copies should reduce to plan shape, durable evidence pointers, fold-down receipts, and historical lookup paths.

Docs Source-Truth Reform Model: Compact Pointer Layer.

This layer sits under the branch authority model. It does not replace the branch authority record, backlog, roadmap, external operational state, Family Feature Vision, or canonical workstream doc.
Codex reaches this layer through the Main-first loader chain: load `Docs/Main.md`, then the governing phase/vision/branch authority owners, then the relevant Family Feature Vision under the recommended `Docs/family_feature_visions/` pattern when USER-approved content exists or when the selected feature-bearing route requires the layer before BP1, then the active branch plan from external operational state for branch-local engineering detail. Repo branch-plan files are historical or transition receipts only.

## Branch Planning Artifact Lifecycle

`Branch Planning` is the canonical phase between `Branch Readiness` and `Workstream`. It owns USER-facing planning review and orchestration validation before runtime/code implementation begins.

The Branch Planning stages are:

- BP1 - `USER Branch Vision Review`, artifact `USER_BRANCH_VISION_REVIEW.md`.
- BP2 - `USER Branch Plan Review`, artifact `USER_BRANCH_PLAN_REVIEW.md`.
- BP3 - `Workstream Entry / Orchestration Validation`, recorded in the Branch Planning packet, active external branch planning owner, and helper/validator output as required.

Branch Vision and Branch Plan are separate contracts:

- Branch Vision is what the branch is building and what it should become.
- Branch Plan is how Codex will build the accepted or waived Branch Vision.
- Family Feature Vision is the durable feature-category context beneath one Family Vision. It supplies BP1 `Feature Vision Context` and Deferred Feature Carryforward for selected feature-bearing branch routes that require the layer, but it is not active branch state, selected-next truth, or implementation approval.
- `Slice` is the canonical package deliverable unit. `SLC` is the current branch-planning alias for Slice-level implementation line items or preserved historical slice IDs. SLCs/slices are the engineering route inside a branch after vision acceptance, and they should not automatically become separate branches.
- `Seam` is the execution or validation checkpoint inside or between slices. A seam is the current bounded checkpoint, not the branch identity and not proof that the package is complete by itself.

The BP2 marker `SLC / Seam Plan:` remains valid for existing packets and historical traceability, but current plans must resolve that marker to a concrete Slice/SLC deliverable map plus seam sequence. Current source truth should prefer `Slice` for canonical package deliverables and use `SLC` only as an alias or historical ID.

## Planning applicability

A plan describes the approved objective, scope/owner, affected implementation, dependencies, proof, rollback and real USER decisions. Concrete deliverables can include code, documentation, governance enforcement or installation. Carry accepted planning and current actual approval with relevant deltas for an unchanged admitted repair. BP1/BP2/BP3 review applies when new product direction, a material plan/vision decision or branch/scope admission is actually required; it is not replayed merely because execution continues.


## Concrete USER-Facing Feature Classification Gate

Every Branch Readiness candidate matrix, BP1 Branch Vision, BP2 Branch Plan, BP3 Workstream Entry packet, Workstream approval packet, Hardening review, Live Validation / UTS packet, PR Readiness packet, and release-facing packet must classify planned and delivered work into these work-output categories:

- `Concrete USER-facing feature`
- `Runtime-facing behavior directly supporting a concrete USER-facing feature`
- `Foundation / infrastructure`
- `Diagnostic / status / trust-boundary`
- `Proof / validator / helper`
- `Governance / packet / documentation`
- `Cross-FAM dependency support`

`Concrete USER-facing feature` is the strict feature-delivery class. It must answer all three questions in plain USER language:

1. What can the USER now do that they could not do before?
2. What useful outcome does the system now produce?
3. Is that outcome more than explaining unavailable or blocked paths, proving boundaries, or reporting readiness?

Runtime-visible status, no-provider results, blocked-state explanations, provider-visible-data `none`, capability unavailable copy, truthful `AI not implemented` copy, validators, proof helpers, USER packets, RAR/UIREF carry-ins, and governance docs are not concrete feature delivery by themselves. They may be valuable foundation, trust-readiness, proof, or support work, but they cannot close a feature branch as a concrete runtime feature unless tied to a selected concrete USER-facing feature outcome.

If no delivered item qualifies as a `Concrete USER-facing feature`, the branch plan or phase packet must choose one legal disposition before PR Readiness:

- reject the plan as a feature branch
- reclassify the branch as a bounded foundation / infrastructure cycle
- hold before PR Readiness
- return to BP1 / BP planning to identify the real runtime carrier
- block until USER explicitly approves a foundation-only posture for PR consideration

PR Readiness is blocked unless one of these is true:

- the branch delivered a concrete USER-facing feature and that feature is hardened and validated according to source truth
- the branch is explicitly classified as a bounded foundation / infrastructure cycle and USER separately approves that posture for PR consideration

No branch may proceed to PR Readiness merely because validators pass, packets validate, proof helpers are green, diagnostic/status UI exists, trust-boundary UI exists, blocked-state copy exists, or source-truth artifacts were generated.

When this requirement is machine-checkable, keep it deterministic: fixtures or validators should reject TBD implementation output, BP2-will-decide-later language, proof packets labeled as concrete feature routes, and boundary-control labels without an implemented control. When the distinction requires human judgment, the branch plan must say which semantic review remains open instead of treating marker presence as green.

Infrastructure and setup can be branch-worthy only when tied to a selected implementation route or to an exact USER action gate. Creating User/Public, Developer, or Owner lanes by itself is groundwork, not a feature implementation carrier. When the legal answer is to pause, retarget, or rename, the branch plan must say so with `Route Disposition:` and `Retarget / Rename Recommendation:` before BP1 or BP2 continue.

Multi-slice branches are legal when the slices share one FAM, one package objective, one selected implementation route, one owner/worktree, aligned release/PR timing, and one validation/proof path that can cover the grouped scope. Split the work when family ownership, package objective, implementation route, private/runtime/provider action gate, release timing, validation path, risk class, or owner/worktree boundary diverges enough that one bounded Workstream package would blur authority or weaken proof.

## Visual Acceptance Target Planning Requirement

`Docs/phase_governance.md` owns the `Visual Acceptance Target Gate`. Branch plans carry the branch-local application of that gate.

When the selected implementation route includes a material visible UI/UX change, the active external branch plan must record a `Visual Acceptance Target Plan:` before Workstream runtime UI implementation begins. The plan must say whether the change is `Not Applicable With Reason`, `Concept Only`, `Design Candidates Reviewable`, `USER_ACCEPTED Visual Acceptance Target`, `USER_REVISED Visual Acceptance Target`, `USER_WAIVED Visual Acceptance Target`, `Implementation Match Proof Pending`, `Implementation Match Proof PASS`, `Implementation Match Proof REPAIR`, or `Blocked`.

Required branch-plan fields when the gate applies:

- `Visual Acceptance Target Plan:`
- `Material Visible Change Classification:`
- `Render Authority Level:`
- `Design Candidate Packet Path:` when USER selection is needed
- `Reviewable Visual Acceptance Target Path:` when a target is available for USER/ChatGPT/Codex review before USER acceptance
- `Design Candidate Media Included:`
- `Visual Selection Ledger:`
- `Rejected Pattern Ledger:`
- `Source-Truth Conflict Classification:`
- `USER Visual Target Decision State:`
- `Accepted Visual Acceptance Target Path:` after USER acceptance or revision
- `Implementation Match Proof Plan:`
- `Implementation Match Proof Evidence:` after code changes
- `Visual Target Exceptions / Waivers:`
- `Visual Target Next Legal Phase:`

BP1 should discover the visual purpose, source-truth conflicts, reference set, and whether the USER needs options before deciding final branch shape. BP2 should translate the accepted or waived visual direction into implementation proof requirements, state coverage, screenshot/video needs, rollback, implementation authority classification, functionality role contract, and implementation-match proof plan. BP3 should verify that Workstream may implement only the USER-accepted/revised/waived target or explicitly route unresolved visual direction back to BP1/BP2. Workstream must not implement a material visible UI/UX change before the target decision is legal. Hardening and Live Validation must compare actual implementation screenshots/video against the accepted target; they cannot replace the missing target with post-hoc visual judgment.

Required visual-proof chain fields when visible UI is material:

- `Visual Acceptance Chain:`
- `Implementation Authority Classification:`
- `Implementation Authority Table:`
- `Visual Family Relation Proof:`
- `Functionality Role Contract:`
- `Accepted Reference Set / Comparative Synthesis:`
- `Implementation Match Proof Plan:`
- `Pre-Live Visual Purpose Conformance:`
- `Packet Reviewability vs Product Acceptance:`

The required chain is `Vision Contract -> UIREF / Accepted Reference Set -> Visual Acceptance Target -> Implementation Match Proof -> Pre-Live Visual Purpose Conformance -> Live Validation -> UTS / PR`. `Packet Reviewability State` and `Product Acceptance` are separate axes. A reviewable packet, clean timestamped ZIP, helper pass, validator pass, UIREF citation, CSS marker similarity, screenshot path, or Codex summary can start USER review, but it cannot become `USER_ACCEPTED Visual Acceptance Target`, `Implementation Match Proof PASS`, or Live Validation green without row-by-row visual-family comparison and the required USER decision or waiver.

BP2/BP3 Workstream approval is invalid when a material visible UI plan lacks any of these:

- accepted or reviewable Visual Acceptance Target path, or explicit `Not Applicable With Reason`
- implementation authority classification: `Shared Primitive Consumed`, `Implementation Template Instantiated`, `Reference-Derived Implementation`, `One-Off Implementation`, `USER-Approved Exception`, `Reference Gap`, `Template Gap`, `Shared Primitive Gap`, or `Source-Truth Gap`
- accepted reference set and comparative synthesis
- visual family relation proof table
- functionality role contract for each new, detached, child, modal, dashboard, diagnostics, settings, doorway, status, or recovery surface
- state/contact-sheet coverage or explicit source-truth exception
- implementation-match proof plan and expected evidence path
- pre-Live visual purpose conformance plan

Branches must not claim a template or shared primitive without the approved source path and consumer contract. If no approved implementation source exists, the branch must classify the surface as `Reference-Derived Implementation`, `One-Off Implementation`, or a gap/exception value and prove element-by-element parity against the accepted reference set before green.

Branch-local external plans may keep detailed target ledgers and packet paths. Repo branch-plan files remain compact pointer and schema owners; they must not become live visual-target ledgers.

When BR2 cannot complete because infrastructure or lane groundwork blocks the selected route, the active branch plan or BR2 packet must include:

- Infrastructure / Lane Groundwork Blockers:
- Required Before This Route Can Proceed:
- Concrete Feature Routes Available Now:
- Deferrable Groundwork:
- Non-Deferrable Groundwork:
- Codex Recommendation:
- Exact USER Decision Needed:

The packet should explain plainly what must exist before Owner, Developer, or User/Public AI work can begin, which prerequisites USER may approve now, which routes can proceed without those prerequisites, and when continued deferral leaves no remaining implementation-bearing route. BR2 may remain blocked or recommend No Active Branch, but it must not complete as green by naming only future planning, lane setup, or later branch selection.

Current planning terminology must use `User/Public lane`, `Developer lane`, and `Owner lane` as lanes or environments, not product version numbers. Use `Developer lane`, not `Dev lane`, in new branch planning packets and active branch plans. Historical branch names, accepted private repo placeholders, and clearly labeled receipts may preserve older wording as traceability only.

BP1 becomes green only when USER accepts the Branch Vision or explicitly waives BP1. BP2 becomes green only when USER accepts the Branch Plan or explicitly waives BP2. BP3 may return bounded Workstream implementation approval for the admitted same-branch package, naming the entry seam or initial seam sequence, only when BP1 and BP2 are accepted or waived, BP3 is approved or waived by USER, and orchestration validation is green.

Branch Planning uses two independent state axes:

- `Packet Reviewability State`: `Missing`, `Generated`, `Validation Failed`, `Reviewable`, `Stale`, or `Superseded`.
- `USER Gate State`: `Pending USER Review`, `USER Revision Requested`, `USER Accepted`, `USER Approved`, `USER Waived`, `USER Rejected`, `USER Blocked`, or `Superseded`.

`Packet Reviewability State: Reviewable` means the packet is ready for USER inspection. It is not USER acceptance, waiver, approval, implementation authority, or next-gate authority. USER gate closure requires a USER response, Codex digest of that response, and an acceptance / waiver / revision / rejection receipt recorded in the review packet, branch plan owner, branch authority receipt, or external operational state. Missing proof blocks on `Branch Planning Acceptance Receipt Missing`, and any helper, validator, or Codex digest that treats packet validation as USER acceptance blocks on `Packet Validation Treated As USER Acceptance`.

Every Slice/SLC must trace to a BP1 accepted Branch Vision requirement and a BP2 Branch Plan line item. If BP2 exposes a vision gap or changes the accepted Branch Vision, Codex must route back to BP1 instead of treating the engineering plan as a new vision owner.

For a selected feature-bearing branch route, BP1 entry is blocked on `Family Feature Vision Required For Selected Feature` until the required USER-approved Family Feature Vision exists and passes the `Feature Vision Sufficiency Check`. If the route is governance-only, release-support, pure helper/validator, source-truth-only, or otherwise non-product, the branch planning packet may record `Family Feature Vision Not Applicable` with the reason. When a USER-approved Family Feature Vision exists for the selected implementation route, BP1 must cite it as the durable `Feature Vision Context`. BP2 must carry forward BP1's accepted disposition for applicable deferred feature items, and BP3 must verify that applicable deferrals are either included in the admitted package, explicitly future-gated with reason, or routed to the correct future owner. Branch plans may record active gate state and branch-local choices for those items, but the durable deferred-item facts belong in the Family Feature Vision after USER-approved fold-down.

## Vision Carrydown Chain

Branch Planning consumes vision in this order:

```text
Project Vision -> Family Vision -> Family Feature Vision -> Branch Vision Contract Snapshot -> BP2/BP3 engineering plan -> Workstream/Hardening/Live Validation proof
```

BP1 owns the branch-specific vision contract. It must state which source-truth vision layers were loaded, which Family Feature Vision or not-applicable reason applies, which durable elements are selected or deferred, and where the USER can inspect the branch's product outcome, surface map, options, recommendations, and unresolved questions.

Project Vision includes the NDAI Product Experience Contract: deterministic, intuitive, immersive, predictable, reliable, and consistent. BP1 must summarize how the selected route is expected to preserve those qualities for in-scope user-facing behavior, runtime-visible state, assistant interaction, recovery behavior, and proof surfaces. BP2 must translate the applicable qualities into engineering/proof requirements. BP3, Workstream, Hardening, Live Validation, UTS, PR Readiness, Release Readiness, and RAR must compare observed or planned behavior against those accepted requirements instead of treating helper/validator green, marker presence, or attractive screenshots as sufficient proof.

Reference Standard carrydown uses the existing phase machine. BR1/BR2 must ask whether applicable Reference Standards already exist or whether the branch has a reference gap. BP1 identifies which Reference Standards shape the branch vision and which missing standards require USER decision. BP2 states whether the branch will consume a Shared Primitive, instantiate a Template, derive from an Accepted Reference Set, or request a USER-approved exception. BP3 verifies that Workstream has a proof plan for those choices. Workstream records reference gaps rather than inventing a new standard. Hardening and Live Validation prove adoption against the accepted reference, template, primitive, or exception. PR Readiness Stage 1 reviews whether the Reference Standard worked, whether repeated same-class repair cycles occurred, and whether a repair, supersession, or deferred reference candidate must be folded down before PR Stage 2.

`Reference Candidate Sync Review:` is required when BR/BP/RAR/Workstream/Hardening/LV/UTS/PR Readiness proposes, consumes, supersedes, varies, or depends on a same-class Reference Standard, Template, Shared Primitive, accepted comparator, token, geometry rule, visual grammar, control-state rule, backend behavior rule, proof standard, naming rule, or applicability rule. The review must state whether promoted repo references were checked, whether admitted external same-class candidates or collisions were checked when available, whether the branch is proposing a new candidate, whether a conflict key exists, whether any collision affects the branch's current scope, and whether USER review is needed. External candidates are evidence only; they cannot be called canon, USER acceptance, template/shared-primitive authority, or consuming-FAM adoption proof before promotion.

Required Reference Candidate Sync fields:

- `Promoted Reference Check:`
- `External Candidate Check:`
- `Candidate Proposal Status:`
- `Conflict Key:`
- `Same-Class Candidate Result:`
- `Collision Status:`
- `Proposed Resolution:`
- `Candidate / Collision USER Decision Needed:`
- `No Candidate-As-Canon Boundary:`

Required candidate table:

| Candidate ID | Domain | Element / Behavior Class | Trait / State | Applicability Scope | Proposed Rule / Value | Owning Branch / FAM | Evidence | Conflict Key | Existing Promoted Reference | External Candidate Conflict | Proposed Resolution | USER Decision Needed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Required collision table:

| Collision ID | Domain | Trait / Rule | Candidate A | Candidate B | Conflict | Affected FAMs | Blocking Scope | Recommended Resolution | USER Decision Needed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Required promotion/supersession table:

| Candidate | Promotion Type | Required Repo Updates | Clarification / Variant / Supersession / Retirement | Atomicity Risk | USER Gate |
| --- | --- | --- | --- | --- | --- |

`Future-Proof Implementation Review:` is required when BP2/BP3, Workstream, Hardening, Live Validation, RAR, or PR Readiness evaluates a feature, UI surface, runtime state, backend-to-visual path, proof hook, or same-class reference/template/primitive adoption that could reasonably receive same-class additions later. Future-proofing means the current admitted feature is implemented so foreseeable same-class additions can be added later without brittle one-off layout, state, proof, or UI rewrites. It does not authorize speculative future feature implementation.

Required Future-Proof fields:

- `Current Feature:`
- `Foreseeable Same-Class Additions:`
- `Contract / Reference / Template / Primitive Basis:`
- `Layout Derivation Rule:`
- `State / Runtime Derivation Rule:`
- `Magic Values Avoided:`
- `Extension Boundaries:`
- `Future-Gated Items:`
- `Template / Shared Primitive / Reference Gap:`
- `Source-Truth Gap:`
- `Implementation Gap:`
- `Proof Expectations:`
- `Disposition:`

Allowed Future-Proof dispositions are `Future-Proof Complete`, `Future-Proof Partial`, `Implementation Gap`, `Template Gap`, `Shared Primitive Gap`, `Reference Gap`, `Source-Truth Gap`, `Future-Gated Dependency`, `Exception Needed`, `Issue Candidate`, `Reference Effectiveness Warning`, and `Blocked Pending USER Decision`. `Future-Proof Partial`, `Implementation Gap`, `Template Gap`, `Shared Primitive Gap`, `Reference Gap`, `Source-Truth Gap`, `Exception Needed`, `Issue Candidate`, `Reference Effectiveness Warning`, and `Blocked Pending USER Decision` block normal progression until repaired, waived, routed, deferred, or accepted by the correct source-truth owner.

| Future-Proof Rule | Owner | Required Carrydown | Enforcement Path | Status |
| --- | --- | --- | --- | --- |
| Current implementation derives from accepted contracts, references, templates, primitives, content rules, state models, and proof hooks where available. | Project Vision, FAM-002, applicable UIREF / reference owner, and consuming FAM branch plan. | BP2 names derivation; BP3 verifies proof plan; Workstream implements from derivation; Hardening/LV prove the result. | Manual phase review now; future helper/validator checks when machine-checkable. | Binding now. |
| Magic values are allowed only when named, justified, source-owned, and proven across relevant states. | Consuming FAM branch plan plus applicable reference owner. | BP2/BP3 and Workstream must record why the value is stable; Hardening/LV test relevant state/size/content variants. | Manual review now; future brittle-pattern scanner expected. | Binding now. |
| Future-proofing does not silently implement future scope. | Phase governance and branch-planning owner. | Future items stay under `Future-Gated Items` or deferred owner/trigger/proof fields. | Phase review and RAR issue-candidate routing. | Binding now. |
| Missing template/shared primitive/reference/source truth is a gap, not local invention authority. | Reference Standard owner, UIREF catalog when UI, or future non-UI reference owner. | Branch records `Template Gap`, `Shared Primitive Gap`, `Reference Gap`, or `Source-Truth Gap` and routes the gap. | RAR, Hardening, PR Readiness Stage 1. | Binding now. |

| Affected Phase | Required Future-Proof Question | Required Evidence | Blocking Condition |
| --- | --- | --- | --- |
| BP2 | How will the engineering plan support foreseeable same-class additions without one-off layout/state/proof rewrites? | Derivation rule, state/runtime rule, extension boundaries, future-gated items, gap disposition. | `Future-Proof Review Missing` or unresolved gap. |
| BP3 | Does the Workstream proof plan cover extension boundaries, same-class additions, and future-gated gaps? | BP2 trace, proof expectations, validator/helper plan, USER-review path for gaps. | `Future-Proof Proof Plan Missing`. |
| Workstream | Did implementation follow the derivation rules instead of screenshot-tuned fixes? | Code-to-visual trace, implementation notes, direct verification, gap rows when needed. | `Magic Value Unjustified`, `Future Scope Implemented By Inference`, or unresolved implementation gap. |
| Hardening | Are brittle layouts, magic pixels, hardcoded assumptions, and backend-to-visual truth drift absent or dispositioned? | State/size/content variation review, source inspection, proof manifest. | `Brittle Implementation Unresolved`. |
| Live Validation / UTS | Does rendered behavior prove the current and relevant same-class extension states, not only a default screenshot? | Focused screenshots/video/ordered frames, state coverage, USER manual validation or waiver when needed. | `One-State Future-Proof Proof`, `Default-Only Future-Proof Proof`, or manual validation pending. |
| RAR | Does merged source truth reveal old/current branch output that is not future-proof? | Adoption ledger, issue-candidate table, accepted-reference comparison, code-to-visual trace. | `Future-Proof Adoption Review Missing` or unresolved nonconformance/gap. |
| PR Readiness Stage 1 | Did repeated repair cycles show the reference/template/primitive was ineffective? | Repair-cycle count, Reference Effectiveness Warning, fold-down candidate if needed. | `Reference Effectiveness Warning Unrouted` or `Reference Standard Repair Candidate Required`. |

| Gap Type | Meaning | Legal Response | USER Decision Needed? |
| --- | --- | --- | --- |
| `Implementation Gap` | Current admitted feature can be fixed in the current legal carrier. | Repair during approved Workstream/Hardening/RAR scope, then revalidate. | Only if repair expands scope or changes accepted behavior. |
| `Template Gap` | A reusable template is needed but not promoted/approved. | Record gap, route to template/reference owner, or derive from accepted reference with USER review. | Yes when promotion, waiver, or local exception is needed. |
| `Shared Primitive Gap` | Reusable implementation source is needed but not approved. | Record gap; do not claim primitive consumption; defer or request primitive work. | Yes for primitive implementation/promotion. |
| `Reference Gap` | Comparator is missing/ambiguous/ineffective. | Route to reference owner or use accepted reference set with explicit limitation. | Yes when USER judgment or new standard promotion is needed. |
| `Source-Truth Gap` | Durable rule owner is missing or conflicting. | Stop or route to Governance/source owner. | Yes for source-truth repair. |
| `Future-Gated Dependency` | Same-class future work exists but is outside current admitted scope. | Keep future-gated with owner, trigger, proof expectation. | Usually no unless USER wants to expand current scope. |
| `Issue Candidate` | Defect is real but out of current legal repair scope or historical. | Prepare issue candidate; issue mutation remains separately USER-gated. | Yes before GitHub issue creation/mutation. |

| Magic / Brittle Pattern | Why It Is Bad | Required Derivation / Proof | Incident Pattern Needed? |
| --- | --- | --- | --- |
| Magic-pixel layout fix | Works only for one screenshot or current content. | Derive from token, gutter, content rule, breakpoint, or accepted reference; prove content/size variants. | Yes if repeated. |
| Screenshot-tuned UI | Optimizes for one proof image instead of product behavior. | Prove default, variant, hover/focus/disabled/error/resize states as applicable. | Yes if it reaches LV/UTS. |
| One-state-only layout proof | Cannot prove future additions or user states. | Add state matrix and focused evidence for relevant states. | Yes when accepted as green. |
| Default-size-only window proof | Hides resize, scroll, overflow, DPI, and multi-monitor defects. | Use UIREF-007 minimum/default/medium/wide/maximum proof. | Yes when repeated. |
| Same-class control divergence | Breaks immersion and predictability. | Compare against UIREF/FAM-002/accepted reference or record exception. | Yes if repeated. |
| Backend-visible state without owner | UI can claim status that runtime cannot prove. | Name state owner, lifecycle, inputs/outputs, failure/recovery, proof hooks. | Yes when validator green missed it. |
| Future feature silently implemented | Smuggles scope under future-proofing. | Keep future items under `Future-Gated Items` with owner/trigger/proof. | Yes if repeated. |

BP2 owns the engineering translation of the accepted or waived BP1 contract. It must map selected vision elements to Slice/SLC/seam deliverables, affected files/surfaces, validators/helpers, proof outputs, rollback, risks, and deferred/future-gated boundaries. BP2 is not allowed to become a new product vision owner by changing UI behavior, workflow, feature scope, or deferred-item disposition without returning to BP1 or recording an explicit USER waiver.

BP3 owns orchestration readiness. It must prove the Workstream package implements the accepted or waived BP1/BP2 vision chain and must identify any missing vision layer, weak FFV sufficiency, unplanned deferred item, or unsupported proof path before Workstream implementation can be requested.

Workstream, Hardening, and Live Validation must carry the same selected vision elements forward. Live Validation must compare observed behavior and USER-facing proof against the applied Project Vision, Family Vision, Family Feature Vision when present, accepted Branch Vision Contract Snapshot, and accepted BP2/BP3 proof plan.

## Family Feature Vision Element Traceability

Family Feature Vision elements are durable vision units. They are not Slices, SLCs, seams, branch routes, or implementation status rows.

Allowed element lifecycle terms:

- `Visioned` = the element exists in the Family Feature Vision inventory.
- `Selected` = BP1 chooses the element for the branch vision.
- `Planned` = BP2/BP3 maps the selected element to branch-local Slice/SLC/seam work and proof.
- `Implemented` = Workstream changes code, source truth, artifacts, or behavior for that element.
- `Hardened` = Hardening inspects that element for defects, regressions, boundary leaks, weak proof, stale assumptions, and deferral integrity.
- `Live Validated` = Live Validation proves the element through the real user/app path when applicable, or records an allowed proof category or waiver for non-UI/non-runtime elements.
- `Deferred` = the element is not in current branch scope and has owner, reason, trigger, proof expectation, and return path.
- `Blocked` = source truth, USER approval, external state, branch plan, private/provider/runtime boundary, or validation prevents the element from moving forward.

Required proof chain:

```text
FFV element -> BP1 selected/deferred -> BP2/BP3 mapped to branch-local Slice/SLC/seam -> Workstream implemented -> Hardening inspected -> Live Validation proven -> USER packet evidence
```

BP1 packets for selected feature-bearing routes must include a selected/deferred FFV element matrix. That matrix names each relevant FFV element ID, whether it is selected or deferred, why it is grouped or deferred, the dependency trigger, the expected proof, and the owner or return path. A BP1 packet cannot pass by citing the Family Feature Vision generally while omitting the elements that determine branch scope.

BP2 and BP3 packets must map every selected FFV element to branch-local Slice/SLC/seam work, affected surfaces, proof outputs, rollback/safety posture, and future-gated boundaries. If BP2 or BP3 changes which FFV elements are selected, defers an element BP1 selected, or pulls in a new element BP1 did not accept, Codex must return to BP1 or record an explicit USER waiver before Workstream implementation can be requested.

Workstream, Hardening, and Live Validation must carry the same selected FFV element IDs forward. Broad inference, nearby proof, fixture-only proof, validator pass, or a general statement that the branch implemented the feature is not enough for a user-visible, runtime-visible, UI, workflow, provider, helper, validator, or source-truth element. Each such element needs element-specific evidence or a named waiver.

BP2/BP3 proof plans must also identify evidence independence for every material selected element. The plan must name `Claim:`, `Claim Class:`, `Source-Truth Owner:`, `Minimum Proof Strength:`, `Expected Independent Evidence:`, `Evidence Class:`, `Known Limitation:`, and `Adjudication / Waiver Path:` when the element affects product behavior, UI/UX, runtime behavior, workflow hierarchy, proof-visible output, helper/validator behavior, source-truth ownership, security/privacy boundary, failure/recovery behavior, external live truth, or subjective USER judgment. The branch plan defines expected behavior; it does not prove the behavior by itself. Marker presence, helper green, generated manifests, screenshot existence, copied file lists, or BP2/BP3 prose are supporting evidence only until compared against the applied vision chain and independent proof. If the minimum proof strength cannot be reached, BP2/BP3 must predeclare `Manual USER Validation`, `USER Waiver`, `Repair Required`, or `Blocked` instead of letting Workstream or Live Validation report an overclaimed green result.

Claim/evidence matrix rows use these governed fields:

- `Claim:`
- `Claim Class:`
- `Source-Truth Owner:`
- `Minimum Proof Strength:`
- `Expected Independent Evidence:`
- `Evidence Class:`
- `Evidence Provided / Expected:`
- `Known Limitation:`
- `Codex Adjudication / Waiver Path:`
- `Disposition:`

Vision-To-Proof Matrix rows carry the same claims into Hardening and Live Validation. Each material accepted requirement must include:

- `Requirement / Claim ID:`
- `Accepted Vision Source:`
- `Accepted Requirement:`
- `Implementation Evidence Expected:`
- `Observed Runtime Evidence Expected:`
- `Comparison Evidence Expected:`
- `Reference Surface / Baseline:`
- `Codex Adjudication Plan:`
- `USER Validation Need:`
- `Final Verdict Path:`

Hardening reviews these rows for proof gaps before Live Validation. Live Validation fills the observed evidence, comparison evidence, adjudication result, USER validation need, and final verdict. A row that only says helper output, marker, manifest, screenshot, video, or log exists is incomplete until it records what accepted requirement the artifact proves and how Codex compared it.

Runtime/backend-affecting BP2/BP3 proof plans must also carry the Backend Predictability / Reliability Contract from `Docs/phase_governance.md`. The plan must define state owner, deterministic inputs and outputs, lifecycle/state-machine states, config/schema delta, migration or compatibility impact, idempotency, retry behavior, concurrency/reentrancy assumptions, failure/fallback/recovery behavior, logging/observability proof, security/privacy boundary, provider/model/cache/private boundary when applicable, UI/user-visible contract impact, validation/proof path, rollback/reversibility path, degraded/disabled/unavailable behavior, and user-facing status/error mapping. Frontend/backend contract consistency is required when UI exposes runtime/backend state: every visible state label, disabled or blocked action, recovery option, success/failure claim, degraded state, and unavailable state must map to runtime truth, policy truth, or a USER-approved exception. Backend logs support diagnosis; they are not USER-facing proof by themselves.

BP2/BP3 proof plans must also carry the Hardening / Live Validation repair-loop route when runtime, desktop, UI, workflow, helper/validator, source-truth, or USER-gated proof can fail after Hardening. The plan must state what LV blockers repair first, what post-LV-repair Hardening rerun must inspect, what LV proof must rerun or reconfirm after Hardening, and what USER validation state counts as final. A pre-repair Hardening pass is planning/evidence history only after LV-driven repairs change branch files or proof surfaces; it cannot be the final PR Readiness basis.

Scope Coverage Manifest rows carry completeness proof into Workstream, Hardening, Live Validation, PR Readiness, and any same-turn repair closeout that claims `green`, `complete`, `LV passed`, `PR-ready`, `accepted`, `no drift`, `all fixed`, or equivalent full-scope success. The active branch plan, USER review packet, helper output, validator output, or Codex digest must include or reference:

- `Coverage Objective:`
- `Phase / Gate:`
- `Source-Truth Owners Loaded:`
- `Inventory Roots:`
- `File Classes Included:`
- `File Classes Excluded:`
- `Runtime / UI Surfaces Included:`
- `Claims Inventoried:`
- `Visual Elements Or Element Groups Inventoried:`
- `Files Read Directly:`
- `Files Searched Only:`
- `Files Not Read With Reason:`
- `Validators Run:`
- `Helpers Run:`
- `Independent Proof Reviewed:`
- `Photo / Video Evidence Reviewed:`
- `USER Packet Evidence Reviewed:`
- `Human-Judgment Areas:`
- `Known Blind Spots:`
- `Sampling Used:`
- `If Sampling Used, Why:`
- `Coverage Disposition:`

Coverage dispositions must use `Checked`, `Not Applicable`, `Deferred With Reason`, `Repair Required`, `USER Review Required`, or `Blocked`. A branch plan or repair digest that uses broad words such as `all`, `every`, `whole window`, `all text`, `all buttons`, `multiple issues`, or a numbered issue set must convert that scope into atomic repair targets or a justified complete-class scan. Each target needs owner, surface, file/code path, expected fix, proof method, and final disposition. One repaired sample cannot close a broad-class complaint unless the manifest proves why sampling is sufficient and what remains untested.

When the selected element creates or changes user-facing UI, BP2/BP3 must classify each visible surface as `Nexus-Owned Product Surface`, `Platform-Native Exception`, `Diagnostic / Developer Surface`, or `External Surface`. `Nexus-Owned Product Surface` rows must name the inherited FAM-002 component grammar and window chrome/frame treatment. `Platform-Native Exception` rows must name the platform reason, why custom NDAI chrome would be wrong or unsafe, and the proof that the exception is deliberate.

When the selected element creates, changes, or visually accepts a Nexus-owned top-level, standalone, restorable, independently opened, movable, resizable, or geometry-persisted product window, BP1/BP2/BP3 must include an `NDAI Top-Level Window Control Grammar Matrix:` or equivalent section. The matrix must name `Window Name:`, `Window Role:`, `Window Class:`, `Control Placement:`, `Window-Level Control Set:`, `Close Control Treatment:`, `Minimize Applicability:`, `Maximize / Restore Applicability:`, `Large Labeled Close Button Disposition:`, `Content/Footer Close Actions:`, `Accessibility / Tooltip / Keyboard Treatment:`, `Hitbox / Focus / Hover / Pressed State Coverage:`, `FAM-002 Control Grammar Consumed:`, `FAM-003 Recovery Route Dependency:`, `Exception Reason:`, and `Proof Method:`. A large labeled header `CLOSE` button on a top-level product window must be recorded as an exception, not accepted as the default mature window-control grammar. Modal dialogs, child windows, footer/content actions, platform-native exceptions, and temporary proof/dev surfaces may use larger explicit close/cancel/exit actions only with a reason and proof path.

When the selected element creates, touches, restores, moves, resizes, persists, or proves a standalone/top-level/restorable Nexus-owned product window, BP1/BP2/BP3 must include a `Standalone Window Geometry Recovery Matrix:` or equivalent branch-plan section. The matrix must name `Window Name:`, `Owning FAM:`, `Surface Type:`, `Window Class:`, `Geometry Persistence Behavior:`, `Default Position / Size Behavior:`, `Reset Position / Size Route:`, `FAM-003 Dependency Status:`, `FAM-002 Presentation Standard Consumed:`, `FAM-008 Setup / Education Dependency:`, `Troubleshooting / Fallback Behavior:`, `Proof Method:`, and `Not Applicable Reason:`. Child windows, anchored child panels, platform-native dialogs, temporary dev/proof tools, and non-restorable surfaces may be `Not Applicable` only with a reason and proof path. A persisted or independently restorable product window without an offscreen/corrupt/missing-monitor recovery route blocks branch advancement on `Window Position / Size Reset Route Missing` or `Offscreen Window Recovery Path Missing`.

When the selected element creates, changes, resizes, scrolls, proves, or visually accepts a Nexus-owned product window or surface that has geometry, size-state composition, responsive layout, fullscreen/maximize behavior, or multi-monitor posture, BP1/BP2/BP3 and RAR must include a `Window Geometry / Resize Matrix:` or equivalent section. The matrix must name `Window / Surface Name:`, `Owning FAM / Worktree:`, `Window Classification:`, `Accepted Reference Set:`, `Minimum Supported Size:`, `Default Size:`, `Maximum Useful Size:`, `Fullscreen / Maximize Policy:`, `Resize Mechanics:`, `Cursor Transition / Resize Grip Policy:`, `Breakpoint / Reflow Policy:`, `Scroll / Wrap / Truncate / Collapse Policy:`, `Active Content / Footer Attachment:`, `DPI / Display Scale Proof:`, `Multi-Monitor / Portrait Proof:`, `Geometry Recovery Route:`, `Code-To-Visual Trace:`, `Screenshot / Video / Contact-Sheet Evidence:`, and `Disposition:`. Valid classifications include `Compact Settings / Tool Window`, `Dashboard / Parent-Class Window`, `Embedded Child Surface`, `Detached Child Window`, `Detached Child Dashboard / Child-Parent Window`, `Modal / Dirty-Guard / Confirmation Surface`, `Platform-Native Exception`, `Temporary Diagnostic / Proof Surface`, and `Not Applicable With Reason`. A branch must not claim geometry/resize green from default-size proof, marker presence, global zoom behavior, or a single attractive screenshot. Out-of-scope owned window drift must become a USER-reviewable issue candidate or explicit waiver candidate before normal progression resumes; GitHub issue creation remains USER-gated.

Active implementation status for selected elements belongs in the active external branch plan or approved branch-planning packet. Family Feature Vision records own only the durable `Visioned` inventory, deferred facts, proof expectations, and fold-down receipts.

When a branch re-enters planning or proof after merged governance standards land on `origin/main`, the active branch plan or review packet must carry a `Merged Vision Standard Adoption Review:`. The review must name the merged standard source, the rebaseline or re-entry event, current branch implementation inventory, affected branch artifacts, affected product surfaces, implemented or touched UI/UX surfaces, implemented or touched runtime/backend surfaces, affected proof claims, merged standard comparison result, frontend/backend contract findings, `Reference / Template / Primitive Classification:`, `Reference Candidate Sync Review:`, `Accepted Reference Set / Comparative Synthesis:`, UI reference / template / shared primitive dependency result, current violation findings, adoption disposition, repair/waiver/blocker, issue-candidate disposition, and a `No Repo Live-State Tracking:` statement. When UI/UX standards are affected, the review must say what the branch already implemented or touched and whether those surfaces currently violate the Project Vision, FAM-002 presentation grammar, applicable Family Vision / Family Feature Vision, UIREF records, Visual Inheritance Matrix, Scope Coverage Manifest, Vision-To-Proof Matrix, or Live Validation proof rules. The review must not call a UIREF record a template or claim shared primitive consumption unless it names the approved implementation template or shared primitive source. It also must not call an external Reference Candidate canon or claim candidate evidence proves consuming-FAM adoption. When backend/runtime standards are affected, the review must say what the branch already implemented or touched and whether those surfaces currently violate the Backend Predictability / Reliability Contract, Runtime Branch Engineering Contract, state/config/schema delta, failure/fallback/recovery route, frontend/backend truth mapping, logging/observability proof, or rollback/reversibility path. When the `Rebaseline Adoption & Reconciliation Phase` (`RAR`) trigger is active, normal branch progression remains blocked until the active plan or packet also includes `RAR Stage:`, `Trigger Reason:`, `Source-Truth Files Loaded:`, `Incoming Standard / Change Summary:`, `Owned Surface Inventory:`, `Affected File Inventory:`, `Affected Surface Inventory:`, `Code-To-Visual Trace Matrix:`, `Reference / Template / Primitive Classification:`, `Reference Candidate Sync Review:`, `Accepted Reference Set / Comparative Synthesis:`, `Accepted Reference / Template / Primitive Comparator Matrix:`, `NDAI Product Experience Contract Comparison:`, `UI Element Inventory:`, `Backend / State Ownership Trace:`, `Screenshot / Video / Contact-Sheet Evidence:`, `Visual Element / Element-Group Inspection Ledger:`, `Vision-To-Proof Matrix:`, `Scope Coverage Manifest:`, `Owned-Surface Nonconformance Ledger:`, `Current Branch Repair Candidates:`, `Previous / Historical Branch Issue Candidates:`, `Issue-Candidate Table:`, `Issue Candidate Decision Surface:`, `Repair / Waiver / Defer / Route Decision Table:`, `Validation Summary:`, `USER Packet Path:`, `USER Packet ZIP Path:`, and `Exact Next USER Decision:` when USER review is needed. This review may live in the active external branch plan, BP1/BP2/BP3 packet, Hardening packet, Live Validation packet, PR Readiness packet, USER review packet, or Codex digest according to the current phase; repo historical branch-plan receipts must not be used as live adoption ledgers. If already-implemented or previous branch output appears defective but is outside the current branch's legal repair scope, the packet must prepare a USER-reviewable GitHub issue candidate for USER review, but issue creation/mutation remains blocked until USER explicitly approves that exact GitHub action.

RAR packet carrydown is substantive, not marker-only. The active branch plan or USER packet must include both named ledgers, even when one says `None`: `Current Branch Active Repair Ledger:` and `Historical / Previous Branch Issue Candidate Ledger:`. It must also decompose owned/touched surfaces into element-group rows rather than broad window-level summaries when UI/UX, runtime status, proof, or USER-facing behavior is affected. The `Scope Coverage Manifest:` must state exactly what surfaces, files, element groups, states, screenshots/videos/contact sheets, backend/state claims, accepted references, validators/helpers, and issue-candidate classes were reviewed; what was excluded; whether sampling was used; and why sampling is valid. `RAR Shallow Audit`, `RAR Ledger Pair Missing`, `RAR Element Group Rows Missing`, `RAR Sampling Justification Missing`, `RAR Comparator Classification Missing`, and `RAR Row Disposition Missing` block normal progression. A RAR packet cannot close from a single repaired sample, helper-green result, screenshot folder listing, or Codex summary unless the row-addressable ledgers prove the whole approved scope or route the unproven remainder to repair, waiver, issue-candidate review, reference/source-truth gap, or out-of-scope disposition.

RAR row statuses must use `CONFORMING`, `NONCONFORMING`, `UNPROVEN`, `PARTIAL`, `EXCEPTION NEEDED`, `ISSUE CANDIDATE`, `SOURCE-TRUTH GAP`, `REFERENCE GAP`, `TEMPLATE GAP`, `SHARED PRIMITIVE GAP`, or `OUT OF CURRENT SCOPE`. Any unresolved status other than `CONFORMING` or justified `OUT OF CURRENT SCOPE` blocks normal BP, Workstream, Hardening, Live Validation, PR Readiness, or Release Readiness progression until repaired, explicitly waived, routed to an approved issue candidate, or dispositioned by the correct source-truth owner. RAR must include these tables when the trigger touches UI/UX, runtime status, or proof claims: `| Surface | Element Group | Source File / Code Region | Backend / State Owner | Rendered Evidence | Accepted Reference | Visual Match | Behavior Match | Status | Defect / Gap | Next Legal Action |`; `| Element Class | Implementation Authority | Accepted Reference Set | Invariant Traits | Feature-Specific Traits | Target Surface | Primitive/Template/Reference-Derived/Exception | Evidence | Gap / Issue |`; `| Issue Candidate | Owner FAM | Surface | Element Group | Defect Class | Evidence | Proposed Carrier | GitHub Issue Mutation Approved? |`; `| Candidate ID | Owning FAM | Surface | Element Group | Defect | Evidence Pointer | Current Disposition | Progression Blocking? | Proposed Carrier | GitHub Issue | Last Verified | Exact USER Decision Needed |`; and `| RAR USER Decision | Meaning | What It Authorizes | What It Does Not Authorize |`. The expanded issue-candidate decision table is the authoritative current disposition surface when active candidates exist. It must live in the current primary USER decision surface selected and routed through the external USER lifecycle owner; copies in supporting review aids, source-truth context, historical receipts, or helper output are supporting evidence only. `Packeted only` or `Issue Candidate Packet USER-Reviewed` wording cannot clear the issue-candidate durability requirement unless every row has a legal durable disposition, exact-token lineage or predecessor/successor mapping, owner/route, GitHub mapping state when applicable, last-verified receipt/date evidence, and remaining USER decision. Mapped GitHub rows require a deterministic read-only snapshot or live-read proof for the issue number; open/closed mismatches, unknown state, stale state, or unavailable state cannot close the candidate. Terminal repaired/rejected/waived/closed-reconciled rows may be absent from a later packet only when the external/history ledger shows no current USER decision remains.

When active issue candidates may lead to GitHub issue creation, the packet must add an `Issue Candidate Consolidation Gate:` or equivalent primary USER decision table. The gate groups atomic candidates by owning FAM, surface, defect class, likely repair carrier, and validation/proof path, while preserving every atomic candidate ID. Group rows must include `Group ID`, `Group Title`, `Owning FAM`, `Surfaces Included`, `Candidate IDs Included`, `Defect Classes Included`, `Evidence Summary`, `Recommended GitHub Issue Title / Body`, `Proposed Carrier Or Future BR1/BR2 Route`, `Progression Impact`, and USER choices to create, map existing, defer, split, merge, reject, or waive. A grouped GitHub issue recommendation cannot replace the atomic candidate table, and a branch cannot request GitHub issue mutation from ungrouped active candidates unless USER explicitly requests one issue for one candidate.

BP1/BP2/BP3 packets created after a rebaseline must not treat old branch packets as green proof when the branch now touches standards merged after those packets were generated. BP1 refreshes the branch vision only when the accepted vision chain changed or was insufficient. BP2 updates engineering/proof-plan matrices when implementation proof, UI inheritance, claim class, minimum proof strength, or USER validation routing changed. BP3 verifies Workstream readiness against the updated adoption review before implementation approval can be requested.

Branch Planning review evidence and its temporary upload are delivered through the current external USER lifecycle owner, routed by `Docs/governance_efficiency_operating_model.md#user-review-hub-rule`. It selects the approved continuing collection and current evidence set; a caller label never selects a new top-level USER directory.

Cloud-backed Desktop or OneDrive locations do not become current USER review owners or transports. USER-facing packet files should focus on vision, plan, context, options, risks, proof expectations, and USER decisions. Active branch status, current HEAD, current origin/main, ahead/behind, upstream, worktree cleanliness, current validation state, current PR state, ZIP hash, and similar mutable technical proof belong in helper output, validator output, Codex chat digest, or external operational state.

## Ownership Model

- Backlog entries remain compact registry, status, and pointer surfaces.
- Roadmap entries remain compact stage-breakpoint schedule and milestone-checkpoint reference surfaces.
- Branch authority records remain durable identity, approval, and historical receipt surfaces; active branch authority lives in external operational state or Git/GitHub/helper-derived truth.
- Branch Runtime Engineering Plans define detailed runtime execution planning. Their active operational copy belongs in external operational state after transition; repo copies are standards, transition evidence, retirement-index entries, or historical receipts.
- Canonical workstream docs and family dossiers receive durable promoted lessons only after PR Readiness fold-down decides what should survive beyond the active branch.

## Required Runtime Plan Markers

Runtime-focused plans must include:

- Plan Identity:
- Owning Branch:
- Worktree Path:
- Branch Authority Record Pointer:
- Current Phase: pointer to the matching external current owner, or an explicitly identified derived/historical snapshot; never an independent live plan value
- Branch Runtime Engineering Plan:
- Engineering Plan Status:
- Current Runtime Baseline:
- Branch Purpose:
- Planned Runtime Delta:
- User-Facing Delta:
- Source-Truth Delta:
- State / Config / Schema Delta:
- Validator / Helper Delta:
- Expected Changed Files / Surfaces:
- Workstream / Seam Map:
- Per-Seam Implementation Checklist:
- Per-Seam Validation Checklist:
- Per-Seam User-Facing Proof Checklist:
- Future-Gated Items:
- GitHub Issue Relevance Review:
- Issue Scan Source:
- Issue Relevance Classification:
- Issue Disposition:
- Approval-Boundary Audit:
- FAM / Shared-Surface Overlap Forecast:
- Open Questions:
- Feature Vision Context:
- Deferred Feature Carryforward Review:
- USER Planning Decisions:
- Plan Revision History:
- Plan-To-Implementation Traceability Table:
- Claim / Evidence Matrix:
- Vision-To-Proof Matrix:
- Merged Vision Standard Adoption Review:
- NDAI Product Experience Contract Comparison:
- RAR Stage:
- Trigger Reason:
- Source-Truth Files Loaded:
- Incoming Standard / Change Summary:
- Owned Surface Inventory:
- Affected File Inventory:
- Affected Surface Inventory:
- Code-To-Visual Trace Matrix:
- Reference / Template / Primitive Classification:
- Accepted Reference Set / Comparative Synthesis:
- Accepted Reference / Template / Primitive Comparator Matrix:
- UI Element Inventory:
- Backend / State Ownership Trace:
- Screenshot / Video / Contact-Sheet Evidence:
- Visual Element / Element-Group Inspection Ledger:
- Owned-Surface Nonconformance Ledger:
- Current Branch Repair Candidates:
- Previous / Historical Branch Issue Candidates:
- Issue-Candidate Table:
- Repair / Waiver / Defer / Route Decision Table:
- Validation Summary:
- USER Packet Path:
- USER Packet ZIP Path:
- Exact Next USER Decision:
- Implemented / Touched Runtime-Backend Surfaces:
- Frontend / Backend Contract Findings:
- Reference / Template / Primitive Classification:
- Accepted Reference Set / Comparative Synthesis:
- UI Reference / Template / Shared Primitive Dependency:
- Issue Candidate Disposition:
- Backend Predictability / Reliability Contract:
- Runtime / Backend Surface:
- State Owner:
- Deterministic Inputs:
- Deterministic Outputs:
- Lifecycle / State Machine:
- Config / Schema Delta:
- Migration / Compatibility Impact:
- Idempotency Behavior:
- Retry Behavior:
- Concurrency / Reentrancy Assumptions:
- Failure Behavior:
- Fallback Behavior:
- Recovery Route:
- Logging / Observability Proof:
- Security / Privacy Boundary:
- Provider / Model / Cache / Private Boundary:
- UI / User-Visible Contract Impact:
- Validation / Proof Path:
- Rollback / Reversibility Path:
- Degraded / Disabled / Unavailable State Behavior:
- User-Facing Status / Error Mapping:
- Rebaseline Issue Candidate Review:
- Candidate Needed:
- Candidate Title:
- Affected FAM / FFV / Surface:
- Evidence Source:
- Expected Behavior:
- Owner Recommendation:
- Severity:
- USER Approval Required Before GitHub Mutation:
- Accepted Vision Source:
- Accepted Requirement:
- Claim Class:
- Minimum Proof Strength:
- Evidence Provided / Expected:
- Evidence Independence:
- Reference Surface / Baseline:
- Observed Runtime Evidence:
- Comparison Evidence:
- Limitation:
- USER Validation / Waiver Path:
- Hardening Comparison Checklist:
- Live Validation Proof Or Waiver Checklist:
- Runtime Observability Decision Matrix:
- Exact USER Desktop Launcher Path:
- Launcher Parity Proof Plan:
- Photo / Video Proof Plan:
- Manual USER Validation Plan:
- Troubleshooting Mode Decision:
- USER Packet Evidence Plan:
- PR Readiness Fold-Down / Retention Checklist:
- Release Readiness Public-Scope Translation Checklist:
- USER Planning Review:
- PR Fold-Down Packet:
- Runtime Implementation Approval:

## Element-to-Phase Proof Matrix

Runtime/user-facing branches that plan, create, touch, affect, defer, or preserve product/runtime/UI/source-truth/helper/workflow elements must carry reviewable proof paths for newly admitted or materially changed elements. Reuse accepted coverage for an unchanged approved repair; a repeated matrix is not a continuation prerequisite.

The matrix extends the active Branch Runtime Engineering Plan from external operational state or an approved transition owner and points to the existing Element Validation Ledger owner. It proves the planned Workstream implementation path, Workstream proof path, Hardening proof path, Live Validation proof or waiver path, UTS / USER acceptance path, and current/future boundary for every element before implementation begins. It must not create a new global ledger or duplicate backlog, roadmap, worktree-slot, or Main live state.

Matrix markers:

- Matrix Status: allowed values are `Required`, `Present`, `Accepted`, `Blocked`, `Folded`, `Historical`, or `Not Required with reason`
- USER Review Status: allowed values are `Pending`, `Accepted`, `Revised`, `Waived`, or `Needs USER Decision`
- Open Element Questions: allowed values are `None`, `Queued`, `Blocking`, or `Deferred With Waiver`
 - Element Coverage Owner: must name the active `D:\Nexus Desktop AI\Governance State\branches\<branch_slug>\branch_plan.md` owner before implementation, or a concrete folded source-truth owner after PR Readiness
- Element Validation Ledger Owner: must name the concrete Element Validation Ledger owner path or source-truth owner

Required table shape:

| Element ID | Element / Surface | Element Classification | Workstream Implementation Plan | Workstream Proof Plan | Hardening Proof Plan | Live Validation Proof / Waiver Plan | UTS / USER Acceptance Path | Future / Deferred Boundary | USER Decision State | Source Owner / Ledger Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Allowed `Element Classification` values are `Planned`, `Created`, `Touched`, `Affected`, `Deferred`, `Future`, `Dependency-Only`, and `Non-Gating Supporting`.

Every planned/current created/touched/affected user-facing, runtime, UI, provider, validation/helper, source-truth, or workflow element must name a Workstream implementation path, Workstream proof path, Hardening proof path, Live Validation proof or waiver path, and UTS / USER acceptance path when those elements are newly admitted or materially changed. Unchanged continuation carries accepted coverage. Future/deferred/dependency-only/non-gating elements must name the boundary that keeps them out of current release gating. Element IDs must be unique inside the matrix. Missing or incomplete matrix coverage blocks Workstream entry or continuation on `Element-to-Phase Proof Matrix Missing` or `Element-to-Phase Proof Path Missing`.

## Runtime Observability Decision Matrix

Runtime, desktop, user-facing, file/folder, Dev Toolkit, bridge, window, recording, launch, or validation-critical branches must include a `Runtime Observability Decision Matrix` before Workstream implementation begins.

The matrix is a branch-planning surface, not a live operational ledger. Active decision details live in the external branch plan while active and fold down only as durable receipt truth after PR Readiness.

Required matrix shape:

| Element / Scenario | Normal Runtime Log | Troubleshooting Log | Dev Toolkit Instrumentation | Exact USER Desktop Launcher Proof | Launcher Parity Proof | Photo / Video Proof | Manual USER Validation | Privacy / Redaction | User-Visible Folder / Label Impact | UTS / Packet Evidence | Future-Gated Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Allowed values:

- `Required`
- `Not Required With Reason`
- `Supporting Evidence Only`
- `USER Waiver Required`
- `Future-Gated`

Rules:

- `Exact USER Desktop Launcher Proof` is required for formal Live Validation of desktop/user-facing runtime behavior unless USER explicitly waives it.
- `Launcher Parity Proof` is required before a troubleshooting runtime launcher may substitute for the normal desktop runtime launcher. The parity proof must show both launchers start the same product runtime/build, use the same product data roots and user-visible behavior, and differ only by admitted diagnostic flags, diagnostic evidence roots, log level, and troubleshooting disclosure.
- `Photo / Video Proof` is required for visible USER-facing closeout claims. Screenshot-only evidence is allowed only when a still photo can prove the claim; motion, interaction, launch, focus, hover, click, resize, open/close, tray, or window lifecycle claims require video or ordered frame-sequence evidence when a single image cannot prove the behavior.
- If a required claim cannot be proven in photo/video, the plan must set `Manual USER Validation` to `Required` or record `USER Waiver Required`; Codex cannot mark the claim proven by helper output alone.
- Direct runtime, helper, WebView, sandbox/offscreen, generated-shortcut, marker, manifest, log, or Dev Toolkit proof may support diagnosis and consistency, but it must not be represented as exact USER launcher proof.
- Any product/user-visible folder or label surfaced by the branch must be checked for client-like language and must not expose worktree, branch, FAM, developer, owner-only, or internal implementation paths unless USER accepts that product-facing concept.
- `USER Packet Evidence Plan:` must state where the USER can review the evidence, which raw evidence paths remain external/helper-owned, and how PASS / FAIL / BLOCKED / UNPROVEN / WAIVED dispositions will be reported without turning repo docs into a live evidence ledger.

## Branch Planning Review Packet

At a genuine USER plan/implementation decision, return readable applicable planning evidence through the selected external publication owner. Identify one decision, its current owners/scope, affected proof, limits and exact needed approval. Honor requested full detail. An accepted current plan carries into in-scope continuation; another packet or ZIP is not required solely for repair progress. Evidence reviewability is not USER acceptance.


## USER Review Packet Human-Readability QA

USER-facing Branch Planning packets must be readable decision aids, not validator logs, metadata dumps, or Codex status digests.

Every generated USER-facing packet must include:

- plain-language purpose
- exact USER decision requested
- what USER will see, inspect, or approve
- what will change
- options, tradeoffs, and Codex recommendation
- open USER questions
- files to inspect
- explicit pending/not-approved boundaries

Technical freshness proof such as current branch head, origin/main, ahead/behind, live PR state, ZIP hash, and validation logs belongs in helper output, validator output, external operational state, or the Codex return digest unless a copied source-truth file already contains historical receipt text. `USER Review Packet Human-Readability Missing` blocks when the packet is structurally valid but not useful for USER review. `USER Review Packet Metadata Dump` blocks when mutable technical proof becomes the primary USER-facing content.

## Architecture / Experience / Policy Impact Matrix

When Branch Readiness or Branch Planning touches product, runtime, UI, provider, cache, AI-native, capability-pack, privacy, trust, or source-truth ownership work, the packet must include this matrix or an explicit `No Impact` finding:

| Owner Class | Named Owner | Touches? | Impact Type | Current Branch Scope | Deferred / Future Scope | Proof / Validation Needed |
| --- | --- | --- | --- | --- | --- | --- |
| Architecture Layer | `<named architecture layer>` | Yes / No | No Impact / Consume Existing / Extend Existing / Change Existing / New Candidate / USER Decision Required | `<scope>` | `<boundary>` | `<proof>` |
| Experience Layer | `<named experience layer>` | Yes / No | No Impact / Consume Existing / Extend Existing / Change Existing / New Candidate / USER Decision Required | `<scope>` | `<boundary>` | `<proof>` |
| Cross-Family Policy Owner | `<named policy owner>` | Yes / No | No Impact / Consume Existing / Extend Existing / Change Existing / New Candidate / USER Decision Required | `<scope>` | `<boundary>` | `<proof>` |

The matrix is a routing/proof surface, not a ledger and not implementation approval. `New Candidate` rows must cite the `Source-Truth Placement Preflight` and `No Existing Owner Fits` proof before a new owner can be proposed.

## USER Branch Vision Review Gate

`USER Branch Vision Review Gate` is the named BP1 USER-facing checkpoint. It defines the branch goal, end-state, product shape, user-facing behavior, surfaces, options, Codex recommendations, USER decisions, and acceptance status before engineering planning.

Required BP1 markers:

- USER Branch Vision Review:
- Review Status:
- Contract Status:
- Packet Reviewability State:
- USER Gate State:
- Contract Revision:
- Project Vision Context:
- Family Vision Context:
- Feature Vision Context:
- Codex Understanding:
- Branch Goal:
- End-State Vision:
- What Will I Actually See, And Where Will I See It?:
- How It Will Function:
- User Experience Flow:
- Surface Map:
- Product Options / Design Paths:
- Codex Recommendations:
- Why This Fits The Nexus Vision:
- USER Design Questions:
- USER Response:
- Codex Digest:
- USER Response Proof:
- USER Response Digested:
- Accepted Branch Vision:
- Family-Vision Versus Branch-Only Vision Impact:
- Must-Have Behavior:
- Must-Not-Do / Regression-Risk Rules:
- Deferred And Future-Gated Ideas:
- Vision Question Queue:
- Design Assumption Ledger:
- Acceptance / Revision / Rejection / Waiver Decision:

Codex recommendations in BP1 must be line-item recommendations with enough detail for USER to visualize placement, behavior, flow, tradeoffs, risks, and Codex reasoning. Each recommendation should leave USER response space under that item.

Substantive BP1 artifact rule: `USER_BRANCH_VISION_REVIEW.md` must be an applied branch vision contract, not a template, instruction sheet, copied-file manifest, or marker-only packet. It must digest applicable project, family, feature, branch, package, architecture, policy, and experience context into plain language; define the branch goal and end-state vision; explain what USER will actually see, review, decide, and rely on; describe how the intended feature, readiness, source-truth, or governance outcome will function; map review, decision, experience, and proof surfaces; present real product/design paths with tradeoffs; give branch-specific Codex recommendations; explain Nexus/family fit; ask branch-specific USER design questions; and separate accepted branch vision from BP2 planning preview and future-gated implementation. A copied-file list can support `START_HERE.md` or helper manifests, but it cannot satisfy `Surface Map:` by itself. Template-shell language such as "review the relevant owner," "describe the intended end state," generic accept/revise/waive/reject options, generic Codex recommendations, or broad non-decision-driving USER questions blocks BP1 on `BP1 Template-Shell Review Artifact`, `USER Review Artifact Substantive Content Missing`, `Copied File List Treated As Surface Map`, `Generic Codex Recommendations`, or `Generic USER Questions`.

BP1 must not be SLC-centered. SLCs may be mentioned as later engineering route candidates only after the branch vision and product direction are understandable. BP1 must not center active branch technical metadata such as current HEAD, origin/main, ahead/behind, upstream, current validation state, or current PR state.

## USER Branch Plan Review Gate

`USER Branch Plan Review Gate` is the named BP2 USER-facing engineering checkpoint. It wraps the accepted or waived BP1 result, active external branch plan or transition-approved branch plan, Element-to-Phase Proof Matrix, Hardening plan, Live Validation / UTS plan, UFD items, and Branch Change Intent Ledger when present into a plain-language engineering packet before BP3 orchestration validation. The packet must help USER answer whether the implementation plan correctly builds the accepted Branch Vision, not merely prove that governance markers exist.

Required review markers:

- USER Branch Plan Review:
- Review Status:
- Contract Status:
- Packet Reviewability State:
- USER Gate State:
- USER Response Proof:
- USER Response Digested:
- Acceptance / Waiver / Revision / Rejection Receipt:
- Contract Version / Revision:
- Accepted Branch Vision Summary:
- Implementation Package Summary:
- Branch Scope Size Test:
- SLC / Seam Plan:
- Affected Surfaces:
- Likely Files:
- Validators / Helpers:
- Proof Requirements:
- Element-to-Phase Proof Matrix:
- H1 Expectations:
- LV / UTS Expectations:
- Runtime Observability Decision Matrix:
- Exact USER Desktop Launcher Path:
- Launcher Parity Proof Plan:
- Photo / Video Proof Plan:
- Manual USER Validation Plan:
- Troubleshooting Mode Decision:
- Rollback / Safety Plan:
- Open Engineering Risks:
- Future-Gated Boundaries:
- Line-Item USER Plan Review:
- Plan Acceptance Checklist:
- Exact BP3 Approval Text:
- USER Review Hub Packet:
- USER Review Packet Finding:
- Plain-Language Branch Goal:
- What Will I Actually See, And Where Will I See It?:
- Planned User-Facing Outcome:
- End-State Vision:
- Visual / Behavioral Description:
- Visual / Functional Walkthrough:
- Surface Map:
- Implementation Breakdown:
- Element-to-Phase Proof Matrix:
- Hardening Plan:
- Live Validation / UTS Plan:
- Open USER Questions:
- USER Plan Review Questions:
- Codex Recommendations:
- Implementation Options:
- Recommended Direction:
- Why This Fits The Nexus Vision:
- USER Plan Review Decision:
- Current Branch Scope:
- Future-Gated Scope:
- Implementation Staging Notes:
- USER Decisions Needed:
- Alternatives / Tradeoffs:
- USER Review Response:
- Codex Response Digest:
- Implementation Constraints Created By USER Response:
- USER Rejected / Deferred Ideas:
- Vision Delta / Source-Truth Impact:
- Contract Change Log:
- Workstream Entry Result:
- Contract Completion Checklist:
- Accepted Scope:
- Deferred Scope:
- Rejected Scope:
- Exact USER Decision Needed:
- Implementation Approval:

`Review Status:` must use `Accepted by USER`, `Revised by USER`, `Deferred With Waiver`, `Rejected by USER`, or `Needs USER Decision`. `Contract Status:` is the closed-loop BP2 Branch Plan Contract state and must use `Draft`, `Pending USER Response`, `Pending Codex Digest`, `Pending USER Confirmation`, `Complete`, or `Waived by USER`. `Packet Reviewability State:` must use `Missing`, `Generated`, `Validation Failed`, `Reviewable`, `Stale`, or `Superseded`. `USER Gate State:` must use `Pending USER Review`, `USER Revision Requested`, `USER Accepted`, `USER Approved`, `USER Waived`, `USER Rejected`, `USER Blocked`, or `Superseded`. A packet can be reviewable while the USER gate remains pending; helpers and validators must report those states separately. The packet must give USER answer paths to accept the engineering plan, accept with changes, route back to BP1 because the plan changes the accepted Branch Vision, explicitly waive remaining BP2 questions, reject and request a narrower branch or plan, or pause as unclear. `USER_BRANCH_PLAN_REVIEW.md` is the BP2 USER Branch Plan Review: a required user-facing engineering-plan artifact derived from accepted or waived BP1, not the primary product/design vision contract and not a normal Codex status digest. It must present the accepted Branch Vision summary, implementation package summary, branch scope size test, SLC/seam plan, affected surfaces, likely files, validators/helpers, proof requirements, Element-to-Phase Proof Matrix, H1 expectations, LV/UTS expectations, rollback/safety plan, open engineering risks, future-gated boundaries, line-item USER plan review, USER response area, Codex response digest, implementation constraints created from USER response, rejected/deferred ideas, source-truth impact, change log, plan acceptance checklist, and exact BP3 approval text when ready. The primary BP2 decision surface is whether the engineering plan correctly builds the accepted BP1 vision and preserves future-gated boundaries; if the engineering plan changes product direction, user-facing behavior, surfaces, scope, or future-gated boundaries, it must route back to BP1 before implementation approval.

Substantive BP2 artifact rule: `USER_BRANCH_PLAN_REVIEW.md` must translate the accepted or waived BP1 branch vision into an applied engineering plan. It must define the largest safe coherent branch scope, describe seams/SLCs as engineering route details inside the accepted vision, identify likely files, helpers, validators, review artifacts, proof outputs, risk controls, rollback/reversibility posture, implementation options with tradeoffs, and Codex recommendation, and prove alignment to BP1. For runtime, desktop, user-facing, file/folder, launch, bridge, Dev Toolkit, or validation-critical work, BP2 must also include the `Runtime Observability Decision Matrix`, `Vision-To-Proof Matrix`, exact USER desktop launcher proof plan, launcher parity proof plan if a troubleshooting launcher may be used, photo/video proof plan, manual USER validation plan for unphotographable claims, troubleshooting-mode decision, privacy/redaction constraints, reference surface / baseline expectations, and USER packet evidence plan. A BP2 packet that merely repeats BP1 vision headings, lists markers, says "see copied files," or presents generic implementation choices blocks on `BP2 Template-Shell Review Artifact` or `USER Review Artifact Substantive Content Missing`. BP2 must keep BP3 and Workstream future-gated until USER accepts or waives BP2 and BP3 validates orchestration.

The BP2 Branch Plan Contract lifecycle is closed loop: Codex proposes the engineering plan derived from BP1, USER responds, Codex digests the response, Codex converts that response into explicit implementation constraints, Codex identifies source-truth and review-packet impact, and any plan-changing digest returns `Contract Status:` to `Pending USER Confirmation`. Codex must update the branch record, branch plan, family vision, backlog, roadmap, validation helper registry, review packet, or other required source truth when USER feedback changes branch direction, feature shape, UI behavior, workflow, end-state vision, implementation scope, future-gated boundaries, or seam order. Codex then delivers selected evidence for renewed pending review through the external USER lifecycle owner. The cycle repeats until USER explicitly confirms the final contract as `Complete` or explicitly waives the gate. BP3 preparation may proceed only when `Contract Status:` is `Complete` or `Waived by USER` and `USER Gate State:` is `USER Accepted` or `USER Waived`.

Waiver semantics are strict. A waiver must be explicit USER text naming the contract and branch; Codex must record it in the branch record, branch plan, and review packet, set `Contract Status:` to `Waived by USER`, preserve pending boundaries, and cite the waiver in exact implementation approval text. A pending review is stale when its declared subject or selected evidence disagrees with the current selection verified by the external USER lifecycle owner, or when its transport lacks selected-file parity. For completed reviews, inspect the retained review evidence and acceptance/waiver disposition; advancing HEAD alone does not invalidate accepted evidence or require retaining a completed ZIP. A conflict between `USER_BRANCH_PLAN_REVIEW.md` Contract Status and the branch plan or branch record remains blocking, as does implementation approval text returned while Contract Status is `Draft`, `Pending USER Response`, `Pending Codex Digest`, or `Pending USER Confirmation`.

Missing or shallow accepted BP1 trace, package summary, branch scope size test, SLC/seam plan, affected surfaces, likely files, validators/helpers, proof requirements, matrix, H1/LV/UTS expectations, rollback/safety plan, risks, future-gated boundaries, USER plan review, USER response/digest or waiver, implementation constraints, source-truth impact, completion checklist, local USER hub packet proof, `USER Review Packet Finding:`, `Packet Reviewability State:`, `USER Gate State:`, USER acceptance/waiver/approval proof, or exact USER decision blocks BP3 and Workstream implementation on `USER Branch Plan Review Missing`, `BP2 Review Packet Ready But USER Response Pending`, or `BP2 USER Acceptance Proof Missing`. A required review that is stale for its declared subject/current selection, not loaded, not digested, missing a clear primary review entrypoint, missing `USER_BRANCH_VISION_REVIEW.md` when BP1 applies, missing `USER_BRANCH_PLAN_REVIEW.md` when BP2 applies, missing current delivery proof during pending review or retained acceptance/waiver disposition after completed review, and not explicitly waived blocks on `USER Review Packet Stale` or `USER Review Packet Not Digested`. A first-seam-only packet cannot satisfy BP3 when multiple slices or seams are admitted.

## Workstream Entry Whole-Package Analysis Gate

Review interacting deliverables and dependencies proportionately before their first implementation or a material change. One coherent slice is valid. Carry accepted direction/planning and qualified evidence into unchanged same-phase repair; only real new decisions, missing approval, safety/proof or phase boundaries block the affected action. Actual runtime/user-facing proof and human-result gates remain applicable.


## Vision Contract Snapshot Markers

Runtime/user-facing branches that affect product behavior, UI/UX, workflow hierarchy, visual standards, setup/activation behavior, provider/model/memory/voice/Core behavior, acceptance criteria, or any design assumption must include a Branch Vision Contract Snapshot before Workstream implementation.

Small docs-only, metadata-only, release-body-format, typo/format, or validator-only branches may record `Vision Contract Required: No` with a reason when there is no product, runtime, or user-facing impact.

Branch Vision Contract Snapshot markers:

- Vision Contract Required:
- Vision Contract Requirement Reason:
- Branch Vision Snapshot Status:
- Open Vision Questions:
- USER Vision Green:
- Implementation Scope:
- Seam Map:
- Stop Conditions:
- Design Assumption Ledger:
- Vision Question Queue:
- Question Severity Policy:
- Vision-to-Implementation Traceability:
- Branch Plan Revision Packet:

Allowed design assumption decision states:

- Proposed by Codex
- Recommended by ChatGPT
- Accepted by USER
- Revised by USER
- Rejected by USER
- Deferred by USER
- Deferred With Waiver
- Superseded
- Needs USER Decision

Only `Accepted by USER`, `Revised by USER`, or `Deferred With Waiver` design states are implementation-safe for user-facing/runtime behavior. Codex and ChatGPT recommendations remain proposed evidence until USER accepts, revises, rejects, defers, waives, or supersedes them.

`USER Vision Green: Yes` means the branch may implement the accepted branch plan without repeatedly reopening broad design unless new repo truth triggers a Level 2 or Level 3 vision question.

Vision update ownership follows the `Vision Update Decision Matrix` in `Docs/phase_governance.md`: branch-specific or unresolved ideas stay in the active external branch planning owner, reusable USER-accepted family standards fold into family vision or family dossiers, and project-wide USER-accepted standards fold into `Docs/nexus_vision.md`. Codex must not promote proposed or unresolved ideas into durable vision owners by inference.

Question severity:

- Level 1 - Non-blocking question: record in the vision/question queue, continue using the accepted plan, and return at the next appropriate review point.
- Level 2 - Seam-blocking question: pause the affected seam, return a Vision Question Digest, and continue unaffected areas only when the plan and source truth support that path.
- Level 3 - Workstream-breaking question: return a Branch Plan Revision Packet and require USER decision before continuing affected Workstream scope.

Vision Question Digest fields:

- Question
- Why it matters
- Affected branch/seam
- Current accepted vision
- Codex recommendation
- Alternative options
- Risk of each option
- Whether work can continue without this answer
- Recommended USER decision
- Exact USER decision needed

Branch Plan Revision Packet fields:

- Current accepted plan
- Discovered issue
- Why current plan is insufficient
- Proposed revision
- Affected seams
- Files/surfaces affected
- Validation impact
- Whether this stays in current Workstream
- Whether this moves to future branch
- Codex recommendation
- Exact USER decision needed

## USER Feedback Disposition Markers

`USER Feedback Disposition` is the active branch-plan mechanism for preserving meaningful USER feedback without creating another permanent feedback ledger.

Meaningful feedback requires a UFD item when it affects branch scope, accepted vision, user-facing behavior, runtime behavior, validation proof, future work, reusable product standards, approval boundaries, or a USER decision.

Minor comments, acknowledgements, typo-level notes, duplicate remarks, or non-actionable conversation may close with no durable UFD item only when Codex records the no-action reason in the active external branch planning owner or return digest.

Minimum UFD ledger markers:

- USER Feedback Disposition Required:
- UFD Ledger Status:
- UFD Ledger Owner:
- Open UFD Count:
- Blocking UFD Count:
- Fold-Down Status:

Each meaningful feedback item uses a repeatable `### UFD Item: UFD-<scope>-YYYYMMDD-NNN` block.

Minimum UFD item markers:

- Feedback ID:
- Feedback Summary:
- Feedback Source:
- Feedback Phase:
- Disposition Type:
- USER Decision State:
- Owner Class:
- Canonical Owner File:
- Workstream Severity:
- Status:
- Fold-Down Target:
- Pointer Locations:

Allowed UFD decision states:

- Proposed by Codex
- Recommended by ChatGPT
- Accepted by USER
- Revised by USER
- Rejected by USER
- Deferred by USER
- Deferred With Waiver
- Superseded
- Needs USER Decision

Allowed UFD ledger status values:

- Open
- Queued
- Blocking
- Closed
- Folded Down
- Deferred
- Superseded
- Pending
- Complete
- Not Required
- Not Applicable

Allowed UFD item status values:

- Open
- Queued
- Blocking
- Closed
- Folded Down
- Deferred
- Superseded

Allowed UFD owner classes:

- Branch Plan
- Branch Record
- Backlog Pointer
- Roadmap Pointer
- Nexus Vision
- Family Vision / Dossier
- Workstream Doc
- Governance Receipt
- No Durable Owner Needed

`No Durable Owner Needed` is valid only when the item is closed as minor/no-action, duplicate, superseded, or non-actionable, with `No-Action Reason:` recorded in the active external branch planning owner or return digest.

Pointer locations may carry UFD ID, short title, canonical owner, compact status, and fold-down status only. They must not carry full feedback text, full decision history, or live implementation state.

UFD IDs use `UFD-<scope>-YYYYMMDD-NNN`. Do not use `FBK-*`, because it collides visually with historical `FB-###` workstream records.

## USER Feedback Disposition Fold-Down

At PR Readiness, every UFD item must be migrated, deferred with waiver, rejected/no-action with reason, closed, or explicitly carried to a future owner.

The fold-down receipt must preserve a lookup path from every UFD ID to its final owner after branch-plan fold-down and retirement.

Branch records carry compact UFD status and pointers only. Backlog carries future-candidate pointers only after USER accepts the future-work disposition. Nexus Vision and family vision owners receive only accepted reusable standards, not branch-local unresolved feedback.

## Branch Change Intent Ledger

`Branch Change Intent Ledger` is required when `Pre-Rebaseline Impact Audit` reports non-empty `Rebaseline Overlap Files:` for the active branch/worktree. It preserves why the branch touched an overlapping file before Codex accepts incoming `origin/main` changes.

 Runtime branches keep this ledger inside the active external Branch Runtime Engineering Plan. Non-runtime branches with overlap must admit or update the smallest source-truth-supported external Branch Engineering Plan under `D:\Nexus Desktop AI\Governance State\branches\<branch_slug>\branch_plan.md` before rebaseline mutation can proceed.

Each overlapping file uses a repeatable block:

### Changed Surface: <path>

- Surface Class:
- Change Intent:
- Why This File Was Touched:
- Owned Behavior / Fact Class:
- Canonical Owner / Source Owner:
- Resolution Owner:
- Shared Surface:
- Overlap Risk:
- Expected Conflict Risk:
- Semantic Merge Risk:
- Regression / Gating Impact:
- Conflict Resolution Rule:
- Rebaseline Handling:
- Validation Proof:
- Fallback Evidence:
- USER Decision / Waiver:
- Fold-Down Target:

`Surface Class:` values are `governance/source-truth`, `runtime`, `desktop/UI`, `Core visual`, `validator/helper`, `fixture/test`, `configuration/state/schema`, `release/public-output`, `prompt/template`, `automation/watcher`, `build/packaging`, `documentation/reference`, or `asset/media`.

`Semantic Merge Risk:` values are `None`, `Low`, `Medium`, `High`, or `Unknown`. For high-risk surface classes, `Unknown` is `BLOCKED` until evidence or USER decision resolves it.

`Regression / Gating Impact:` values are `None`, `Low`, `Medium`, `High`, or `Unknown`. For `fixture/test` overlap, `Medium`, `High`, or `Unknown` is `BLOCKED` because it can change validator truth, regression coverage, or release gating; `None` or `Low` may be WARN or PASS only when the ledger and fallback evidence support that classification.

`Resolution Owner:` values are `Current Branch`, `Incoming/Folded Owner`, `Originating Lane`, `Approved Source Owner/Carrier`, `USER Decision`, or `Future Branch`.

`Approved Source Owner/Carrier` means the named owner and carrier selected by current USER approval and its current assignment. This value does not authorize a standing lane, create an assignment or expand the approved write scope.

When overlap evidence is missing, weak, stale, or conflicting, Codex must run `Rebaseline Overlap Failure Procedure` and return a packet with `Overall Overlap Gate Result:`, per-file `Per-File Result: PASS / WARN / BLOCKED`, `Recommended Resolution:`, `Validation Required:`, `USER Decision Needed:`, and `Rebaseline Mutation Status:`. Fallback evidence supports classification and USER decision-making only; after the effective point it cannot produce `PASS` without branch-owned change-intent evidence.

A new branch or material vision/plan/scope decision receives its applicable USER review. Existing accepted planning and actual implementation approval carry into their in-scope corrections. Workstream records the implemented delta and affected proof; no repeated BP1/BP2/BP3 packet, element ledger or single-slice waiver is required solely for that continuation. Preserve real runtime, phase and human-result prerequisites.


If USER feedback is meaningful to current branch scope, future branch scope, accepted vision, validation proof, or reusable product standards, Workstream Entry and later seam packets must either add or update a UFD item or state the no-action reason.

## GitHub Issue Relevance Review

Active external branch plans, Branch Readiness packets, and rebaseline/reconciliation packets must include `GitHub Issue Relevance Review:` when live GitHub issues, returned UTS issue forms, PR review repairs, diagnostics reports, or release-window evidence could affect branch scope, proof, or closeout.

Required fields:

- `Issue Scan Source:`
- `Issue Number:`
- `Issue Title:`
- `Live GitHub State:`
- `Issue Relevance Classification:`
- `Affected FAM / FFV / Branch Surface:`
- `Issue Disposition:`
- `Disposition Reason:`
- `Owner / Route:`
- `USER Decision Required:`
- `Durable Receipt Target:`

Allowed `Issue Relevance Classification:` values are `Relevant To Current FAM`, `Relevant To Other FAM`, `Cross-FAM`, `Duplicate / Superseded`, `Not Applicable`, `Needs USER Triage`, and `Live State Unknown`.

Allowed `Issue Disposition:` values are `Include In Branch Scope`, `Defer With Reason`, `Route To Another Owner`, `Block Pending USER Decision`, `Not Applicable With Reason`, `Closeout Candidate`, `Already Closed`, and `USER Decision Required`.

The active branch plan may carry temporary issue scan evidence only while the branch is active. Repo branch-plan receipts after fold-down must preserve only compact durable issue receipts, approved closeout summaries, or pointers to GitHub/helper evidence. They must not become active issue ledgers, live issue queues, or substitutes for GitHub issue truth.

Hardening compares actual implementation against the plan and records extra behavior, skipped items, UI copy integrity, validator coverage, and future-gated item checks.

Hardening also compares actual behavior against the accepted Branch Vision Contract Snapshot when one is required.

Hardening also checks UFD items that affect accepted scope, skipped items, user-facing behavior, validation proof, and future-gated items.

Live Validation records proof or waiver posture against the plan. Disabled/status-only branches must include a static proof substitute and waiver reason.

Live Validation compares observed user-facing behavior against accepted vision and records waiver posture when a branch is disabled/status-only or static-proof-only.

Live Validation must not mark user-facing feedback accepted unless the UFD item is implemented, waived, deferred, rejected/no-action with reason, or carried to a named future owner.

PR Readiness compares the whole branch against the plan and produces the `PR Fold-Down Packet:`. That packet decides what durable content moves into the structured branch receipt, what promotes to a canonical workstream or family dossier, and when the plan is retired from active planning posture.

PR Readiness also folds reusable vision updates into the correct durable owner: Nexus Vision, family vision/family dossier, workstream doc, structured branch receipt, or validated historical receipt. Branch-specific snapshots should not become permanent branch-specific vision file sprawl.

Release Readiness translates the plan into public release language: user-visible highlights, excluded work, future-gated capabilities, and public body wording without internal governance jargon.

## Fold-Down Model

Branch plans are canonical while the owning branch is active. They are not permanent backlog, roadmap, or release-state ledgers.

At PR Readiness, the `PR Fold-Down Packet:` must classify plan content into one of these outcomes:

- migrated into the branch authority record as a structured traceability receipt
- promoted to a canonical workstream or family dossier because future branches should reuse it
- retired from active planning posture because it was superseded, rejected, future-gated, or fully folded down

Branch plans are not deleted by default. Deletion requires a separate USER decision after reference scans prove the plan's durable content and useful historical evidence are preserved elsewhere.

Fold-down must preserve USER decisions, approval boundaries, future-gated items, validator/helper proof, user-facing proof, and plan-to-implementation traceability. It must not preserve stale active phase, live PR, latest-release, worktree dirty-state, or watcher state as current truth.

`Docs/branch_plans/retirement_index.md` owns the current historical branch-plan retirement posture. A plan listed there is retained as a historical receipt, not an active execution blueprint. Future branches must create or admit their own active plan instead of reusing a retired plan by inertia.

## Compact Pointer Rule

The backlog and roadmap must not own detailed runtime plan narrative. They may point to the branch authority record, active external branch plan, repo branch-plan historical receipt, canonical workstream docs, or family dossiers. Detailed checklist fields such as `Per-Seam Implementation Checklist:`, `PR Readiness Fold-Down / Retention Checklist:`, and `Release Readiness Public-Scope Translation Checklist:` belong in the external plan layer or the folded historical record, not in backlog or roadmap.
