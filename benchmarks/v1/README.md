# Reusable coding-agent evaluation — v1 preparation

**Status: planning foundation, not a runnable or validated benchmark.** No new scored runs, inference budget, or installed-global changes are authorized by these files.

The goal is acceptable, maintainable repository changes per total workflow cost, including failed attempts and all subagents. Start with the [full evaluation plan](../../research/evaluation-v1/PLAN.md).

## Included

| Asset | Purpose |
|---|---|
| [Task catalog](manifest.json) | 24 proposed scenarios across fixes, features, refactoring, state/concurrency, tests, and cross-module work |
| [Maintainability rubric](rubrics/maintainability.md) | Anchored blinded review of architectural fit, appropriate complexity, clarity/changeability, and validation/delivery |
| [Initial comparison template](../../protocols/initial-globals-delegation.json) | A: no custom globals with helpers; B: non-delegation globals without helpers; C: full globals with helpers |
| [Future revision template](../../protocols/candidate-vs-incumbent.json) | Incumbent versus candidate with unrelated capabilities and settings held constant |
| [Planning validator](../../tools/benchmark/validate_plan.py) and [unit tests](../../tools/benchmark/test_validate_plan.py) | Offline structural checks for the catalog, split separation, causal comparisons, attempt arithmetic, and explicit unapproved state |

A and C share the same enforced helper route; A may delegate naturally. C versus A tests the full globals. C versus B tests the complete delegation package, not tool availability alone or cheap-versus-expensive helper models. The future revision template leaves helper capability unresolved until an incumbent is selected; freeze it identically for both conditions.

## Run the offline checks

From the repository root, using Python 3.12 or later and only its standard library:

```sh
python -B tools/benchmark/validate_plan.py
python -B -m unittest discover -s tools/benchmark -p 'test_*.py' -v
```

On Windows, `py -3.12 -B` can replace `python -B`.

A successful validator returns `planning_metadata_valid` while explicitly retaining `ready_for_scored_execution: false` and `inference_authorized: false`. Exit code 1 reports inconsistent or missing metadata. These scripts do not run agents, inspect credentials, make network calls, validate real task packages, test sandbox enforcement, or certify billing limits.

The checker intentionally supports the checked-in planning templates only. An authorized study belongs in its own versioned research directory, with a dedicated execution/readiness gate and actual evidence. Do not turn these templates into a claimed authorization by changing a Boolean.

## Still required before a scored pilot

1. Author real task packages with pinned repositories/images, clear visible requirements, protected acceptance tests, reference solutions, incorrect/no-op controls, and independent validation. Select source families and splits, then a development smoke subset.
2. Repair and independently validate the new runtime's effective context, helper enabled/disabled controls, descendant accounting and termination, explicit deadline/commit contract, grading, and report pipeline. Preserve archived runtimes rather than editing history in place.
3. Calibrate the human rubric and define blinded review/adjudication. Freeze decision thresholds, weighting, randomization, sample-size rationale, and exclusion rules before confirmation.
4. Produce a costed, bounded pilot proposal with reserves and stop rules. Obtain separate authorization before any model probe or scored run.

All 24 catalog entries are currently **proposed**, with unassigned splits and no task package/source selected. The 12 development + 12 confirmation target and four-task smoke subset are design targets. Public scenario titles are not sealed confirmation cases. Actual protected tasks must be independently authored and kept out of the tuning process.

Illustrative counts are 12 author attempts for initial calibration, 72 for a three-condition confirmation batch, 8 for a two-condition smoke check, and 48 for a two-condition confirmation batch. None is an approved schedule, sufficient-power guarantee, or spending authorization; probes, review, and research overhead require separate costing.

## Relationship to the archive

The [completed 54-run study](../../research/deepswe-2026-09/README.md) remains historical exploratory evidence. Its instruction snapshots, grades, accounting, and original conditions are unchanged. The [paused delegation preparation](../../research/deepswe-delegation-ablation-2026-09/README.md) remains paused and unvalidated; do not automatically run its former 48-start proposal.

Use the [continuation guide](../../research/CONTINUE.md) for existing offline verification commands and the new preparation path. Never pool new v1 outcomes with historical results or describe catalog/unit-test checks as coding-agent benchmark passes.
