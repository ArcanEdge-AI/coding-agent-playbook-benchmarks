# Reusable coding-agent evaluation — development implementation

**Implemented:** 12 executable synthetic development tasks, an isolated-workspace exporter, external grading controller, mutation-test evaluation, paired schedule preparation, native usage intake, blinded review packets, and cost/uncertainty reports.

**Not established:** a validated live Codex executor, Docker isolation on the selected production host, 12 protected confirmation tasks, calibrated human reviewers, or an approved inference budget. No command in the new tools starts a model. The original 54 scored attempts remain unchanged.

## What is in GitHub

| Asset | Role |
|---|---|
| [Development packages](tasks/development.json) | 12 content-addressed task specifications and 32 actual source files, exported into standalone Git repositories |
| [Suite tool](../../tools/benchmark/suite.py) | Catalog validation, fresh workspace export, reference/no-op/alternative/mutant controls, and Docker-only grading for untrusted submissions |
| [Study tool](../../tools/benchmark/study.py) | Frozen randomized paired schedules, result intake, root/helper credit accounting, blinded review, and JSON/Markdown reports |
| [Harness tests](../../tools/benchmark/test_execution.py) | 54 offline tests; no credentials or model calls |
| [Control results](../../research/evaluation-v1/development-controls.json) | 46 successful grading controls on the 12 tasks; these are not coding-agent results |
| [Maintainability rubric](rubrics/maintainability.md) | Four human-scored dimensions; unreviewed code never automatically counts as acceptable |
| [Initial protocol](../../protocols/initial-globals-delegation.json) / [revision protocol](../../protocols/candidate-vs-incumbent.json) | Unapproved A/B/C and incumbent/candidate templates |
| [Implementation status](../../research/evaluation-v1/IMPLEMENTATION.md) | Tested scope, remaining gates, and deliberate differences from the historical submission protocol |

The original [24-scenario catalog](manifest.json) remains the planning backlog, not the implementation registry. `tasks/development.json` is authoritative for runnable development packages. These compact synthetic fixtures are calibration/regression material, not evidence of production-workload representativeness or difficulty. Actual confirmation tasks must be independently authored and protected from tuning; relabeling these cases is not confirmation.

## Requirements

Python 3.12+ for the harness, Node.js 22.6+ with TypeScript stripping for TypeScript fixtures, and Go 1.23+ for Go fixtures. STATE-01 also needs CGO and a C compiler for `-race`. No third-party language dependencies are required. Local verification used Python 3.13.5, Node 22.16.0, and Go 1.23.2 on Linux; Windows-specific execution and Docker isolation have not been exercised here.

## Run offline checks

```sh
python -B tools/benchmark/suite.py validate
python -B -m unittest discover -s tools/benchmark -p 'test_*.py' -v
```

The original `validate_plan.py` still checks the unapproved planning catalog/templates. The new suite validator checks actual package identities. Neither certifies live runtime controls or spending authorization.

## Export a real coding task

```sh
python -B tools/benchmark/suite.py export --task FIX-01 --out /absolute/external/workspaces/fix-01
```

The destination must not exist and must be outside this repository. Export writes real source files, TASK.md, common repository guidance, and an initial Git commit with an explicit benchmark identity. FLOW-04 applies its user-owned notes **after** that commit, preserving them as pre-existing untracked work. Existing workspaces are never reset or reused.

All implemented tasks disclose a 1,200-second deadline and use **final workspace snapshot submission**. Commits are optional in these new development cases. Both unexecuted protocol templates now declare that contract. Historical committed-submission experiments are not rescored or pooled with these tasks. A commit-based campaign requires a separately implemented submission adapter; the preparer rejects a mismatched contract.

## Protected evaluators

The evaluator bundle is distributed separately as `ArcanEdge_Evaluator_Bundle_v1.zip` in the implementation conversation. Keep `evaluators.json` outside this repository and outside all subject workspaces. The public catalog pins each evaluator's canonical SHA-256; [bundle metadata](../../research/evaluation-v1/evaluator-bundle.json) pins the complete bundle. Do not upload the bundle to this public repository.

Reference, alternative, deliberately wrong implementations, expected outputs, and mutation controls are evaluator-only assets. They are not copied into exported repositories or their Git objects. For grading, the host controller retains expected answers; candidate containers receive only the candidate files and test **inputs**, never expected outputs or reference solutions.

Validate only the frozen, trusted controls locally:

```sh
python -B tools/benchmark/suite.py controls --bundle /private/evaluators.json --out /external/control-results.json --trusted-local-controls
```

This explicitly runs the authored, hash-bound control code. It is not a safe local route for arbitrary agent patches. Untrusted grading requires an already-installed, digest-pinned Docker image containing the runtimes above:

```sh
python -B tools/benchmark/suite.py grade --task FIX-01 --workspace /external/workspaces/fix-01 --bundle /private/evaluators.json --image YOUR_GRADER_IMAGE@sha256:YOUR_VERIFIED_DIGEST --out /external/grade.json
```

The image placeholder must be replaced with a real digest. There is no automatic image pull or local fallback. The sandbox request disables network, drops capabilities, uses a read-only root, applies CPU/memory/process limits, and runs unprivileged. These request controls have unit coverage, **not live Docker validation**. Host-level controls must also prevent the author runtime from reading the benchmark checkout, evaluators, credentials, or other attempts. Treat isolation as unvalidated until the selected host passes operational probes.

## Prepare matched comparisons without spending

```sh
python -B tools/benchmark/study.py prepare --protocol protocols/initial-globals-delegation.json --tasks smoke --repeats 1 --seed 20260913 --out /external/studies/pilot-draft
```

This freezes catalog/protocol/schedule hashes and creates 12 fresh workspaces: four tasks × three conditions. It does not install globals or launch an author. A/C retain matched helper capability; B is the no-delegation package. For future instruction revisions, use `protocols/candidate-vs-incumbent.json` to prepare eight smoke workspaces.

Preparation writes `readiness.json` with unresolved runtime, instruction/model, review, and authorization gates. A capability flag or model self-report is not a verified control. Do not use the historical paused runner simply because these workspaces exist.

## Collect costs, review, and reports

The native-usage command reuses the archive's own-session parser without changing it. It rejects arithmetic anomalies and mixed model/effort sessions requiring finer accounting. Compatibility with a new native session format must still be checked operationally.

```sh
python -B tools/benchmark/study.py native-usage --trial /private/native-trial --out /external/usage.json
python -B tools/benchmark/study.py record --study /external/studies/pilot-draft --run RUN_ID --grade /external/grade.json --usage /external/usage.json --rates research/deepswe-2026-09/credit-rates.json --kind imported --termination completed
```

Run IDs come from the frozen schedule. The record binds task, grader/check identities, artifact, schedule, raw usage, and rate-card hashes. Failed attempts retain their cost. Missing usage remains incomplete rather than free. Root/helper route violations are retained as invalid attempts, not silently scored or discarded. Missing graders can be recorded with `--invalid-reason` and no `--grade`, preserving observed expenditure. `simulation` is a distinct data kind and cannot be pooled with imported results or used to infer instruction effects.

Use an explicitly selected, frozen rate card. The historical rates above are a reproducibility example, not a current billing claim. Human review/repair effort remains unmeasured unless independently collected; do not turn it into estimated labor cost.

```sh
python -B tools/benchmark/study.py review-packets --study /external/studies/pilot-draft --out /external/blind-packets --mapping /private/reviewer-map.json
python -B tools/benchmark/study.py attach-review --study /external/studies/pilot-draft --mapping /private/reviewer-map.json --packet PACKET_ID --review /external/completed-review.json
python -B tools/benchmark/study.py report --study /external/studies/pilot-draft --out /external/report.json
```

The packet mapping must stay outside the reviewer directory. Packets omit direct condition/model/cost labels and include a diff, task, independent checks, and a blank human rubric. They do not invent a captured agent handoff. Reviews require evidence, a human reviewer identity, and the exact graded artifact hash. Additional reviewers/adjudication remain a manual process; the first attachment is immutable, not silently overwritten.

Reports include known root/helper/workflow costs, invalid-run overhead, failed-attempt cost, pending reviews, missing results, task-weighted cost per acceptable solution, and exploratory paired source-cluster intervals. Fewer than six source groups suppress intervals. Undefined ratio draws are not discarded. These are not power or confidence-coverage guarantees. Promotion stays **not evaluated** until runtime controls, budget authorization, and the confirmatory protocol are independently established.

## Next execution gates

Implement and validate the selected live Codex adapter and exact enabled/disabled capability enforcement; freeze actual instruction bytes, model/effort and helper routes; validate Docker grading and descendant termination on the target host; calibrate the human rubric; independently author protected confirmation tasks; and obtain a separately bounded inference budget. The maintenance-follow-up experiment and automatic promotion remain unimplemented. No global instructions, historical results, or paid experiments were changed by this implementation.
