# ArcanEdge Coding-Agent Evaluation Plan

**Status:** Proposed protocol and task-design backlog, with offline planning scaffolding. Not a runnable benchmark, scored study, budget authorization, or change to installed instructions.

**Prepared:** September 13, 2026. Research baseline: `a3eafe072bcec8b801bbf28853ebbe016803838c`.

## 1. Decision to support

Determine whether custom Codex globals produce more acceptable repository changes at lower total workflow cost, and whether the selected cheap-subagent delegation setup improves that balance. Preserve a reusable regression suite for future changes.

Keep three conclusions distinct:

- **Better and cheaper:** Evidence supports higher acceptance/quality and lower cost per acceptable solution.
- **Cheaper without material quality loss:** Cost falls while quality meets a predeclared non-inferiority standard. This is not proof that quality improved.
- **Trade-off or inconclusive:** Quality requires more spending, quality falls, or uncertainty does not distinguish a useful improvement from noise.

No finite suite guarantees improvement everywhere. Scope claims to the task distribution, main model, runtime, and resource policy actually tested. Confirm transfer to other models separately.

## 2. Preserve the existing evidence

Keep the completed 54-run study, instruction snapshots, scores, accounting, and original runtime assumptions unchanged. Its three previously observed tasks remain legacy diagnostics/regressions, not unseen confirmation tasks. Do not pool old and new results into one success rate.

Reuse the existing grading controls, isolated runtime preparation, native root/descendant accounting, frozen rate calculations, and compact exports where they pass new validation. The paused delegation runner remains unvalidated. This protocol is a new design, not permission to resume the former 48-run proposal.

Repository preparation does not authorize model calls, retries, credit purchases, changes to installed globals, or automatic experiments. Separately authorize each inference stage and its budget. Preserve the same authentication/billing route across conditions; do not silently substitute API billing.

## 3. Initial conditions and causal questions

Use one fixed main model and reasoning level: the combination most representative of the intended workflow. Freeze actual supported identifiers in the selected runtime, rather than assuming historical model aliases still work.

| Condition | Custom globals | Helpers |
|---|---|---|
| A — No custom globals | None; retain native base and common repository instructions | Available with the same enforced cheap-helper model, effort, and limits as C |
| B — Globals without delegation | Candidate's exact non-delegation text | Effectively disabled and verified |
| C — Full globals | Same core text plus delegation instructions | Available with the same enforced route and limits as A |

**C versus A** estimates the full custom-global effect with capabilities and helper routing held equal. A can delegate naturally; it is not forced to remain single-agent. A is a tool-matched no-custom-globals baseline, not necessarily an unmodified shipping configuration.

**C versus B** estimates the selected delegation package: its instructions plus helper availability. It does not isolate availability alone. A versus B is not a pure instruction contrast because capabilities differ.

Generate B with explicit reviewed edits and verify byte parity of all retained text. Do not remove security or authorization rules merely to shorten B. Audit actual helper routes and overrides; equal defaults alone are insufficient. Enabled runs that choose not to delegate remain in their assigned condition.

A later helper-routing experiment may change only helper model/effort under routing-neutral instructions and identical orchestration limits. C versus B cannot establish that a cheap helper is superior to a more expensive helper or identify the contribution of one sentence.

After initial references exist, routine changes normally need only incumbent versus candidate. Keep a no-globals anchor for major changes or periodic checks, not every edit.

## 4. Reusable task bank

Target **24 newly authored tasks**: 12 development and 12 protected confirmation tasks. A four-task smoke set is a subset of development. These are authoring targets, not a sample-size guarantee.

The machine-readable [task catalog](../../benchmarks/v1/manifest.json) contains 24 **proposed scenarios**, not known bugs or implemented tests. All start with unassigned split/source and no validated task package. Do not relabel public scenarios as sealed evidence: actual confirmation packages must be independently authored and protected from instruction tuning.

Cover targeted fixes, features, refactoring, state/concurrency, test work, and longer cross-module delivery. Include small coherent tasks where delegation may add overhead and decomposable tasks where it might help. Label suitability before seeing outcomes; spawning helpers is never itself a success criterion.

Use multiple independent source/problem families, initially aiming for at least six. Reserve whole repositories for confirmation where feasible. At minimum, keep related bugs and variants in the same split. Do not inflate independent sample size with many variations of one problem.

Reflect the actual language/workload mix. Freeze sampling weights before scoring and report an unweighted diagnostic view alongside weighted results. Weights remain provisional until informed by representative real work. Do not pick tasks because a candidate wins on them. Difficulty calibration belongs on development tasks.

### Required task package

Every scored task needs a stable ID/version, provenance and permission for use, immutable base revision/image, exact visible specification, common repository instructions, existing tests, evaluator-only checks, requirement-to-test mapping, private reference patch, deliberately incorrect controls, resource/submission contract, review rubric, split/family metadata, and recorded validation evidence.

Validate the evaluator before trusting a task:

1. A known correct reference passes all required checks.
2. A no-op fails the task-specific requirement.
3. Plausible incorrect patches fail.
4. Different valid implementations are accepted.
5. For test-writing tasks, submitted tests reject designated faulty implementations without rejecting the correct implementation.

Test stated behavior, not hidden requirements, variable names, or a preferred reference algorithm. Existing regression tests passing on an unchanged repository do not establish feature implementation.

Keep reference solutions, hidden tests, grader credentials, and prior answers outside subject filesystem/network access and accessible Git objects. `.gitignore` is not isolation. Store private evidence externally; public manifests may contain opaque identifiers and hashes, not sensitive paths or secrets.

## 5. Acceptance and quality

Keep functional correctness, delivery, maintainability, and cost separately visible. An **acceptable solution** is a valid submitted artifact that passes required feature/regression checks, has no disqualifying integrity/safety failure, and meets the frozen maintainability threshold.

Run applicable builds, type/lint checks, and deterministic integrity/security checks. Distinguish new problems from a frozen pre-existing diagnostic baseline.

State submission requirements and time limits explicitly. If a commit is required, supply the same authorized benchmark identity in every condition. Save the submitted artifact and final workspace separately. Missing a required commit is a delivery failure; do not substitute a diagnostic workspace grade into the primary submission score or claim the unsubmitted code was independently proven wrong.

The authoritative evaluator is immutable. Agent-side test improvements may be legitimate; do not confuse them with weakening evaluator-owned acceptance tests.

### Blinded maintainability review

Use [the anchored rubric](../../benchmarks/v1/rubrics/maintainability.md): architectural fit, appropriate complexity, clarity/changeability, and validation/delivery quality. Proposed scores are 0–3 with at least 2 in each dimension and no blocker for acceptance. Calibrate and freeze thresholds before confirmation; they are design choices, not measured findings.

For the first study, have a human review every functionally passing submission, blinded to condition, model, usage, and cost. Double-score a predefined subset and adjudicate disagreements. Preserve evidence and rejected patches. An AI reviewer may assist but is not the acceptance authority until calibrated against humans.

Do not reward low line counts, more comments, more helpers, or resemblance to instruction wording. Necessary security, accessibility, integrity, and tests are not over-engineering.

### Secondary maintenance follow-up

Preselect a small subset. After the initial submission, give a fresh maintainer the same ordinary follow-up request with fixed model, instructions, and budget. Hide condition labels and helper history. Do not disclose the future feature to the original agent or score its initial implementation against that unstated requirement.

Measure follow-up success, regressions, credits, review effort, and rework. Report pipeline success over all original attempts, retaining initial failures as pipeline failures. Report conditional follow-up cost among eligible passing artifacts separately to expose selection effects. Keep this secondary and bounded.

## 6. Whole-workflow cost

Reuse native per-session accounting after validating it against the chosen runtime. Include every root and descendant's own usage once, all internal retries, and failed attempts. Exclude inherited history and duplicate cumulative notifications. Preserve raw uncached/cached input, output, reasoning breakdown, and overlapping-category semantics.

For a balanced schedule:

`cost_per_acceptable_solution = total_workflow_credits_across_all_attempts / acceptable_solutions`

Zero acceptable solutions means no finite observed cost per success, never zero. Also report cost per functionally passing solution. For unequal repeats/weights, divide weighted per-task mean cost by weighted per-task acceptance probability; selectively repeated tasks must not gain accidental weight.

Maintain separate ledgers for:

- **Agent workflow:** roots, helpers, internal retries, metered tools, and any fixed normal review/repair stage included in the treatment.
- **Human delivery effort:** observed review/repair minutes. Do not convert guesses into measured labor cost or combine units without an agreed conversion rate.
- **Research overhead:** task/reference authoring, experimental grading, probes, invalid-run diagnosis, and research-only maintenance tests.

Keep frozen-rate normalized credits for longitudinal comparison and actual billing only when independently observed. Do not equate estimated credits with quota percentages or exact deductions. Preserve raw usage for transparent repricing without rewriting historical results.

Parent/child cost, coordination activity, wall time, caching, and routes are diagnostics. Low direct helper cost does not prove savings; count the complete workflow.

## 7. Runtime readiness and execution controls

Before scored inference, require independent evidence for reference/no-op/incorrect-patch grading, hidden-test isolation, actual enabled child execution, effective disabled capability including alternative helper routes, descendant accounting/termination, exact instruction capture, and clean end-to-end extraction/grading/reporting on a disposable fixture.

The archived `<multi_agent_role>` assertion is not a sufficient capability gate. Merely removing it does not repair the control. A disabled model's self-report or absence of children is insufficient by itself; verify tool/access enforcement. Probes that invoke models require their own explicit authorization.

Hold constant main model/effort, helper route where available, runtime/harness revisions, images, dependencies, repo state, context sources, permissions, compute, concurrency policy, submission requirements, and resource policy. Capture effective prompts and hashes; exclude unrelated installed globals, skills, memories, and prior attempts.

Use clean sessions/workspaces. Freeze networking and cache policy; record provider caching rather than assuming identical cache states. Disclose deadlines and apply one common **total workflow** resource allowance: helpers do not each receive another full allowance. Include descendants in termination and cost.

Run randomized matched task/repeat blocks, with conditions close together and balanced host load. Freeze the seed and schedule. Do not run every A then every B then every C. Do not coach later conditions with earlier results.

No mid-confirmation changes to instructions, tests, runtime, or resource policy. A material change starts a new version. Predeclare treatment of provider/model changes and infrastructure faults; never silently pool incompatible results.

## 8. Budget gates and sample size

**Offline preparation:** Validate metadata, task packages, grading, accounting, and deterministic runner behavior. Offline planning checks are not proof of runtime readiness. Do not hide inference inside setup.

**Calibration proposal:** Four development tasks × three conditions × one attempt = **12 author attempts**, plus separately budgeted probes and review. Establish feasibility and indicative costs, not a winner. Freeze any development-driven resource changes before confirmation.

**Confirmation proposal:** Twelve protected tasks × three conditions × two repeats = **72 author attempts** on one main model. This is an illustrative first batch, not a promise of sufficient power. Use pilot evidence plus plausible variance ranges and sensitivity analysis to select the final design. The pilot cannot precisely estimate every variance component. More independent tasks may be needed.

Future examples: four smoke tasks × two conditions × one repeat = 8 attempts; twelve tasks × two conditions × two repeats = 48. Most edits should not automatically progress to expensive confirmation.

Before each paid stage, record task/model/attempt limits, aggregate estimate, planning reserve, in-flight exposure, stop rules, and allowed conclusions. A delayed estimated-credit monitor is not a hard billing cap. Use tested runtime limits where supported and stop new launches before reserves are exhausted. Include probes, grading, invalid infrastructure, and follow-ups in the approved research budget.

Budget stops produce partial evidence, not a winner. Never silently extend, replace valid failures, buy credits, or change instructions. The machine-readable [initial protocol](../../protocols/initial-globals-delegation.json) leaves model choices, budgets, thresholds, and runtime evidence unresolved intentionally.

## 9. Analysis and promotion

Freeze C–A and C–B as the primary contrasts. Account for multiple comparisons for joint confirmatory claims; do not search many subgroups for favorable results.

Use paired task-level effects and uncertainty intervals. Repeats are nested within tasks, not independent new tasks. Keep conditions paired in resampling and account for shared repository/family dependence, or restrict claims to the fixed suite. Few independent groups make intervals unstable; disclose that limitation.

Report acceptance, functional pass rate, delivery failures/timeouts, rubric dimensions, cost per acceptable solution, mean attempt cost, wall time, and observed human effort. Include per-task outcomes and only preregistered category analyses with appropriate caution.

Illustrative promotion targets, **not approved policy**:

- At least 20% observed cost-per-acceptable-solution reduction, with uncertainty supporting genuine savings and ruling out a quality loss larger than an agreed margin (5 percentage points is only an example).
- Claiming *at least* 20% savings requires the uncertainty bound to support that magnitude, not merely the point estimate.
- Claiming *better and cheaper* requires quality/acceptance improvement as well as lower cost; non-inferiority alone does not establish better code.
- Critical regressions trigger investigation. No failures in a small suite do not prove universal safety.
- Unmet criteria mean retain the incumbent and report inconclusive or an explicit trade-off. Nonsignificance is not equivalence.

Use a fixed final analysis or a prespecified valid sequential design. Do not repeatedly check ordinary intervals and stop at the first favorable result. Operational safety/budget stops do not create efficacy evidence.

Predeclare invalidity/adjudication and replacement rules. Never retry a valid coding failure to improve a score. Preserve invalid attempts and their expenditure in the research ledger; distinguish infrastructure failure from agent failure and apply exclusions consistently across comparisons.

## 10. Future instruction changes

`freeze candidate -> offline checks -> smoke -> development comparison -> protected confirmation for significant promotions -> decision record`

Version instructions, tasks, grader, rubric, model, runtime, and rate card. Rerun the incumbent alongside the candidate after model/runtime changes; historical scores alone are not a matched current control.

Maintain a stable regression core, but retire confirmation status when detailed outcomes inform tuning. Replenish protected cases with independently authored work, not renamed variants. Keep related tasks together.

Maintain a separately reported safety/authority suite using inert fixtures: preserve user edits, refuse unauthorized destructive operations, respect spending/credential limits, and report checks honestly. Do not let many easy policy assertions drown out coding-task outcomes.

Keep implementation small: manifests, a validated runner, independent evaluators, an anchored rubric, and reproducible reports. Do not build an unrelated dashboard or add skills/apps/memory unless they represent a separately declared real workflow.

## 11. Repository implementation and next work

Start at [the v1 preparation guide](../../benchmarks/v1/README.md). The catalog, protocol, rubric, and offline consistency checker are preparation assets. They do not implement the 24 task repositories, private tests/reference patches, controlled inference runner, or statistical reporting pipeline.

Next implementation sequence:

1. Author and independently validate task packages; assign source families/splits and select the smoke subset.
2. Repair and validate runtime capability, context, submission, resource, and accounting controls without editing archived runtimes in place.
3. Add blinded review collection and a reproducible report with explicit missing evidence.
4. Freeze a costed pilot proposal; obtain separate inference approval; only then execute.

Every future run record needs run/task/version IDs, family/split, condition/repeat, snapshot hashes, actual model/effort and lineage, usage completeness, credit versions, timing/termination, submitted artifact identity, individual grades, blinded review, functional/delivery/acceptable outcomes, invalidity adjudication, and private evidence identities/hashes.

No successful metadata validation may be described as a completed benchmark or authorization to run one.

## 12. Sources and provenance

This repository version adapts the conversation's `ArcanEdge_Coding_Agent_Evaluation_Plan.md`. The 24 task scenarios are retained in the manifest. Proposed counts, rubric thresholds, matrix, budget gates, and implementation choices are ArcanEdge-specific designs, not measured findings.

Historical evidence: [continuation](../CONTINUE.md), [replay controls](../deepswe-2026-09/REPLAY.md), [behavior and limitations](../deepswe-2026-09/behavior.md), and [paused delegation status](../deepswe-delegation-ablation-2026-09/README.md).

Methodological references carried forward from the plan:

- OpenAI, Evaluation best practices: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- Anthropic, Demystifying evals for AI agents: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Kapoor et al., AI Agents That Matter (2024): https://arxiv.org/abs/2407.01502
- NIST/SEMATECH, Randomized block designs: https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm
- OpenAI, Why SWE-bench Verified no longer measures frontier coding capabilities: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- Agarwal et al., Deep Reinforcement Learning at the Edge of the Statistical Precipice (2021): https://arxiv.org/abs/2108.13264

These references motivate the design; they do not validate a particular coding-agent sample size or the unbuilt v1 runtime.
