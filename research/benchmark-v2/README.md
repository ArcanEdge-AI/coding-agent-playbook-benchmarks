# Repeatable instruction and delegation benchmark — v2 preparation

**Status: offline planning/reporting tools implemented; coding task fixtures and live runtime controls are not yet validated. No paid inference is authorized or started by this package.**

The objective is to determine whether custom global instructions deliver more acceptable, maintainable code per total workflow credit, and whether suitable cheaper-helper delegation improves that balance. This package makes future changes comparable without overwriting the September studies.

## Start here

- [Protocol and adoption rules](PROTOCOL.md): separate questions, matched runs, grading, budgets, and confirmation.
- [Reusable task bank and fixture requirements](TASKS.md): six concrete development specifications, historical regression cases, and private holdout rules. Specifications are **not executable fixtures**.
- [Pilot manifest](pilot.json): a proposed 24-start, one-root-model comparison; unselected settings and authorization deliberately remain unset.
- [Existing-cost review](COST-REVIEW.md): what the published aggregates can establish before more inference.
- [Offline tools](tools/benchmark.py) and [unit tests](tools/test_benchmark.py).

This is a new protocol, not a silent resumption of the paused 48-run study. The original instruction snapshots, raw scores, scripts, and acceptance contracts remain unchanged. The proposal preserves the user's selected **whole delegation setup** comparison. It does not establish a benefit from delegation or introduce new installed globals.

## Offline commands

Run from the repository root with Python 3.10 or later; only the standard library is used:

```sh
python -B -m unittest discover -s research/benchmark-v2/tools -p 'test_*.py' -v
python -B research/benchmark-v2/tools/benchmark.py check research/benchmark-v2/pilot.json
python -B research/benchmark-v2/tools/benchmark.py schedule research/benchmark-v2/pilot.json
python -B research/benchmark-v2/tools/benchmark.py check research/benchmark-v2/pilot.json --require-prepared
python -B research/benchmark-v2/tools/review_costs.py research/deepswe-2026-09/credits.json
python -B research/benchmark-v2/tools/review_costs.py research/deepswe-2026-09/credits.json --matched-17
```

`--require-prepared` is expected to exit **1** on the checked-in draft. Invalid input exits 2. Normal draft checks and schedule previews exit 0 and report blockers. A schedule is always a preview, never execution authorization. The preparation check detects missing fields; it does **not** verify that evidence references are genuine, hash the referenced artifacts, prove native controls, or grant spending permission. Those reviews are mandatory before any separate executor is used.

No command launches Codex, reads credentials, contacts a service, purchases credits, or changes installed instructions. There is no inference runner or automatic paid CI in this package. The archived draft runner must not be treated as validated by these unit tests.

## Report later scored attempts

The reporter consumes an audited JSON array; it does not manufacture external grades from agent claims. Every row has this shape (values below are illustrative, **not a recorded result**):

```json
{
  "study_id": "delegation-package-v2-development",
  "task_id": "ts-boundary-validation",
  "repeat": 1,
  "condition": "current-with-helpers",
  "status": "completed",
  "submitted": true,
  "functional_pass": true,
  "quality_pass": null,
  "root_credits": 10.0,
  "helper_credits": 1.0,
  "helper_count": 1
}
```

`status` is `completed`, `timeout`, or `infrastructure_invalid`. `submitted` means a feature implementation reached the stated committed-patch submission boundary, not merely that starter regressions passed. A committed implementation can pass after its author times out. `quality_pass: null` means review is pending; missing usage is `null`, never zero. `helper_count` counts all native descendants. Grades, source hashes, session lineage, actual routes, patches, elapsed time, and reviewer evidence must be retained in the associated run bundle described in the protocol.

```sh
python -B research/benchmark-v2/tools/benchmark.py summarize research/benchmark-v2/pilot.json --results /path/to/audited-results.json
```

The report keeps missing starts, invalid infrastructure, pending reviews, and known cost subtotals visible. Head-to-head metrics use only complete valid pairs; total recorded spending also includes unmatched and invalid attempts. Missing usage or pending acceptance prevents a misleading cost-per-accepted number. Enabled runs that choose not to delegate remain in their assigned condition. Results are descriptive: no confidence intervals, power calculation, significance test, causal trace classification, or automatic winner selection is implemented.

## What must happen before scored execution

Build and independently validate the task fixtures and graders; select and freeze the root runtime and all artifact hashes; validate native enabled/disabled controls plus prompt parity and accounting; register the analysis and task mix; obtain explicit probe/scored-run authorization and a budget. The [continuation guide](../CONTINUE.md) retains the original pause and evidence-preservation rules.
