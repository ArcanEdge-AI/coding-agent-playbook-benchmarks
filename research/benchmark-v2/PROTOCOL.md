# Benchmark v2 protocol

Status: proposed experiment design; no live control validation or scored inference has been performed for v2. Numerical pilot sizes and example adoption margins below are planning choices, not measured power or an approved budget.

## 1. State exactly which question a comparison answers

| Comparison | Control | Candidate | What it can establish |
|---|---|---|---|
| Global instruction effect | Native base + identical repository guidance, no custom globals | Same setup + selected engineering globals | Effect of that instruction package with helper capability/routing held fixed, preferably disabled initially |
| Delegation package | Selected globals with only delegation provisions removed; helpers disabled | Intact selected globals; helpers enabled on a fixed route | Incremental effect of delegation instructions plus capability, including their overhead |
| Future global revision | Accepted instruction version | One proposed revision | Revision effect with the same runtime, helper policy and task contract |
| Cheaper helper route | Helpers enabled with one frozen route | Same policy/capability with the cheaper route | Effect of route configuration; no change to orchestration policy apart from necessary route identifiers |

Do not conflate the first two questions. The initial pilot follows the previously selected delegation-package comparison. To answer the overall globals-versus-native question, subsequently compare the selected complete setup against a contemporaneous native baseline, or use a separately budgeted three-arm study. Historical scores are not a contemporaneous control.

Use a reviewed exact diff and effective-context capture. A package-level result cannot identify the contribution of one sentence. Do not change instructions, root model, effort, helper route, task definitions, or submission rules mid-study. When the installed file differs from the archived snapshot, create a new snapshot and study ID; do not overwrite historical bytes. The helper-route comparison is a separate experiment, not an extra arm hidden inside the initial pilot.

Retain safety and authorization boundaries. A correctness benchmark cannot justify removing safeguards it does not test. Dedicated boundary fixtures may be run separately without pooling their scores with coding tasks.

## 2. Build a reusable suite, not an endlessly reused confirmation set

Maintain three explicit partitions. **Development** tasks may be inspected and used to tune prompts. **Regression** tasks retain known failure modes and detect regressions on every candidate. **Confirmation** tasks and graders are withheld from the instruction author and tested agents until the candidate and analysis are frozen.

Keep holdout artifacts in a private evaluator-controlled location, not merely a different directory in this public repository. Publish their hashes and opaque IDs when appropriate; do not expose private repository content, solutions, or customer data. Hidden tests need a separate evaluator filesystem/identity, not just a filename the subject is told not to open. Remove solution history, benchmark reports, grader files, and other attempts from the subject workspace; restrict network access to prevent fetching them.

The existing three DeepSWE tasks are familiar regression/calibration evidence, with documented oracle defects. They are not new confirmation data. Preserve original graders and scores. A corrected grader becomes a new task/grader version; never silently rescore history or claim that a known task became unseen by renaming it.

Select representative real-repository work: bounded bugs, cross-layer features, refactors, data integrity, concurrent cleanup, and genuinely parallel work. Include small tasks where delegation should be unnecessary and larger tasks where it may help. Freeze task-family proportions before comparing; do not choose tasks because one condition already won on them. Languages alone are not sufficient diversity. Confirm later on the actual language/framework mix used in production rather than claiming three languages cover all ArcanEdge work.

Each task is admitted only after the [fixture requirements](TASKS.md) pass. Check that the initial implementation fails the feature requirement, existing regressions pass, a reference implementation passes, and at least two plausible faulty implementations fail. Include boundary and metamorphic/property checks where relevant; avoid testing a single preferred implementation. Calibrate difficulty using development tasks only. Saturated tasks and tasks nobody can finish provide little discrimination; retain them as separate smoke/stress cases rather than manipulating scored results after seeing arm outcomes.

## 3. Stage spending instead of multiplying every model immediately

**Offline preparation:** build and validate task fixtures/graders; audit old aggregates; verify exact treatments; produce the schedule; test reporting and budget handling. No inference required.

**Runtime probe gate:** after separate authorization, run minimal enabled and disabled probes against the exact chosen model/runtime. Enabled must execute a real native child on the intended route. Disabled must reject a direct delegation attempt at the runtime boundary and show no descendants; absence of a child or a model's claim alone is insufficient. Check every supported spawn route, including wrappers and recursion. Capture exposed capabilities and actual session lineage. An assertion about a particular prompt tag is not a substitute for this evidence. If the runtime cannot enforce the distinction, stop and redesign; do not mark it disabled by instruction alone.

**Proposed development pilot:** one representative main-agent model/effort; six new validated tasks; two fresh attempts per task per condition; two conditions = **24 scored starts**. The six specifications in `TASKS.md` are not yet executable. Choose the root from the user's intended production workflow, not from the largest observed historical win. The model and budgets intentionally remain unset. This pilot checks discrimination, repeat variability, workflow integrity and rough economics; it is not a statistically powered confirmation.

**Confirmation:** freeze the candidate after development, then run both conditions contemporaneously on independent holdout tasks with repeats. Choose task count and repeats from the minimum effect worth acting on, variability, paired discordance, and an explicit cost ceiling. Prefer more independent tasks before adding many repeats of the same few tasks. Do not claim that a preset 12, 24, or 48 runs guarantees an answer. If uncertainty remains at the authorized limit, report it as inconclusive.

**Model transfer:** only after a useful result, repeat a bounded confirmation on other main-agent models. Analyze model strata separately and explicitly test differences; avoid announcing a universal policy or ranking from pooled model averages.

## 4. Match execution and make completion requirements explicit

Run fresh isolated sessions against identical source commits, repository guidance, dependencies/lockfiles, CPU/memory limits, tools, network policy, and test environments. Freeze CLI version, actual root model/effort, speed tier, child model/effort, concurrency, cache policy and usage-rate card. Record timestamps and actual routed models. Where a server-side model cannot be pinned, record the alias and dates, interleave conditions, and qualify longitudinal comparisons.

The supplied scheduler alternates condition order within each task across repeats, balances first condition across tasks, and shuffles pair order from a fixed seed. It does not promise deterministic model output. Keep each pair close in time with matched resource availability; do not run all controls and then all candidates. Prevent cross-run memory and workspace leakage. Record cached and uncached usage rather than assuming caching was equal or deleting inconvenient cache effects.

Supply an explicit benchmark Git identity identically in both conditions. State the author deadline, its start event, the grader allowance, permitted actions, and the committed-patch submission rule in the task envelope. Start the author clock after environment preparation. Provide identical remaining-time signals where supported. This is a deliberate v2 protocol change, not a retroactive repair of the undisclosed historical cap.

The harness captures committed and uncommitted artifacts at stop, but only the declared submitted patch counts toward delivered success. Uncommitted work is diagnostic. Test the committed artifact in a clean evaluator checkout. Do not overlay grading files in a way that deletes helpers required by the submission. Stop descendants when the author ends; record any trailing usage. A timeout with a passing submitted patch is distinguishable from a finished session with no implementation.

## 5. Score code quality and completion independently

The primary outcome is **accepted delivery**, requiring an in-scope submitted implementation, all task-specific feature/regression/build gates, no disqualifying integrity/safety defect, and a completed independent maintainability review. Preserve functional pass, submission, timeout, review result and integrity status as separate fields.

Give reviewers the task, baseline, submitted patch, and relevant test evidence, but not the instruction condition, cost, model name, or run order. Use randomized IDs and counterbalanced side-by-side order. Redact incidental treatment labels without altering implementation evidence. Agent explanations and self-reported test results are not correctness evidence. A different model can assist review but is not the sole independent production-quality authority; calibrate against human judgments and record the review model/version and cost separately.

### Maintainability rubric

Score each dimension 0, 1, or 2 with file/line evidence. **0** = material defect requiring rework; **1** = acceptable with a minor issue; **2** = clean and appropriate. Do not force a spread or reward verbosity.

| Dimension | What to inspect |
|---|---|
| Architectural fit | Uses the existing seams and conventions; necessary dependencies are explicit |
| Proportional complexity | No speculative framework, duplicated path, needless abstraction or unexplained dependency |
| Reliability | Relevant error handling, boundary behavior, cancellation/resource cleanup and data integrity |
| Changeability | Clear contracts/naming, limited coupling, and understandable intent |
| Test quality and scope | Meaningful regression coverage, no weakened tests, unrelated churn or missing deliverables |

Recommended gate for review: no dimension scores 0 and no disqualifying defect. Freeze the gate before running; report the dimension scores rather than only a summed score. A small diff is not automatically good architecture. A larger change can be required by the task. Security/performance/accessibility gates must be declared where relevant, not assumed from this rubric.

Review all submitted functionally passing patches, and review a preselected sample of failures for diagnosis. Independently double-review at least a predeclared fraction plus disputed/material findings; resolve disagreements before unblinding. Store both raw reviews and adjudication. Pending review is unknown, not failure or success. Do not label an unreviewed patch production-ready.

## 6. Count the whole workflow cost

For every native root and descendant, including retries and replacements, use the recorded actual model and frozen rate card:

`credits = ((input - cached_input) * input_rate + cached_input * cached_rate + output * output_rate) / 1_000_000`

Reuse the existing audited session-accounting implementation, but validate its event assumptions against the new runtime before trusting new logs. Exclude inherited history and duplicate cumulative usage; do not add reasoning output twice. Missing final usage is unknown, not free. Root coordination, helper review, retries and integration are included in native session costs. The direct helper share alone cannot establish savings.

Primary descriptive metric: **sum of total agent credits on valid matched attempts / number of accepted deliveries**. Failed valid attempts stay in the numerator. Zero accepted deliveries, incomplete cost coverage, or pending required reviews means the ratio is undefined/pending, not zero. Also report functional-only cost per pass, submission and timeout rates, paired wins/losses/ties, per-task and per-model distributions, wall time, helper usage, and enabled runs that did not delegate. Do not select only runs where the enabled agent actually delegated; that is a post-treatment selection.

Keep separate ledgers for scored workflow credits, invalid/incomplete starts, probes, evaluator/model-grader cost, research-controller usage, human review time, and infrastructure. Report the full study expenditure as well as comparable workflow economics. A cost-effective workflow is not necessarily a cost-effective experiment. Standard credit equivalents are not actual billing deductions or a percentage of a Pro allowance. Record actual billing data only when available; never infer it from the subscription price. Preserve old rates and optionally reprice both conditions under one newer rate card as a separate analysis.

To understand mechanisms, code preserved transcripts for planning, discovery, implementation, delegation setup, waiting, integration, verification, and rework. Retain an unknown/mixed category and evidence spans. Compare phase totals and matched pairs; do not claim counterfactual main-agent work saved from a helper's self-report. Aggregate credit files alone cannot establish these mechanisms.

## 7. Pre-register analysis and stopping

Before starting, record the primary comparison, task weights, acceptance rules, exclusions, number of pairs, maximum expenditure, handling of missing data, effect sizes worth acting on, and analysis procedure. Count tasks as the generalization unit; repeats and individual assertions are not new independent tasks. Use task-clustered paired uncertainty analysis, preserving both arms and repeats when resampling; account for shared repositories if several tasks come from one source. With few tasks, state the instability rather than presenting narrow run-level intervals. The included reporter is descriptive only; confidence intervals/power calculations must be added and reviewed before confirmatory claims.

Assess acceptance reliability, maintainability and cost separately. Suggested decision policy to approve before confirmation: adopt only when acceptance is not materially worse, no important quality/safety regression appears, and savings or quality gains are large enough to matter. For example, a 5-percentage-point acceptance non-inferiority margin and a 15% cost reduction could be business thresholds, **not validated defaults**. Specify how confidence bounds must meet them. Failure to detect a difference is not evidence of equivalence. Better quality at higher cost is a tradeoff, not automatically a win.

Use fixed, authorized batches. Do not keep sampling until a favorable significance result appears. A sequential design needs its own predeclared valid stopping method. Stop on runtime leakage, wrong route, unexpected prompt drift, invalid grader, missing usage, pause requests, or budget exhaustion; preserve the evidence. Classify infrastructure exclusions without arm-based discretion, remove the affected pair from comparative metrics, and retain all spending. Never retry a valid coding failure out of the denominator. Replacement infrastructure trials need documented approval and new identifiers, not overwriting the original row.

Require authorization covering probes and scored starts, a total estimated-credit ceiling, per-attempt reserve and maximum attempts. Before launching a pair, reserve both attempts plus pending usage and probe allowance. Runtime checks should stop new requests when possible; in-flight requests and missing usage can overshoot. Unless the provider enforces a hard cap, label these as spending guards, not guaranteed billing limits. Do not redeem or purchase credits, switch billing routes, or resume the old schedule as a side effect of preparing this package.

## 8. Future instruction-change workflow

Save an immutable incumbent and candidate; write a one-paragraph hypothesis and exact diff; run offline checks; use the fixed development/regression suite under both versions; review failures without changing the current study; freeze a candidate; confirm on protected holdouts; then make a separate adoption decision. A task used to guide edits becomes development/regression evidence, not an untouched holdout. Refresh heldouts periodically and disclose repeated evaluation; use a gatekeeper with limited feedback to reduce adaptive overfitting.

Keep each study under a new ID with its protocol, instruction hashes, source/image/runtime identities, seed and schedule, artifact hashes, native evidence references, run status, grader results, blinded reviews, rate card, cost ledger, exclusions, uncertainty, and decision. Keep private sessions/credentials outside the public repository. Re-run the contemporaneous incumbent when runtime/model service behavior changes; do not compare a new model against months-old control results as an instruction-only effect.

## Method references

The design above is a proposal tailored to this archive, not a claim that external guidance validates its sample size or margins. OpenAI's [evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) supports task-specific evaluation, representative data, automated grading calibrated with human review, and continued evaluation. The repository's [continuation guide](../CONTINUE.md), [results](../deepswe-2026-09/results.md), [behavior review](../deepswe-2026-09/behavior.md), and [paused experiment](../deepswe-delegation-ablation-2026-09/README.md) provide the specific evidence and unresolved controls motivating this protocol.
