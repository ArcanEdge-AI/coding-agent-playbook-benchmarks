# Release Readiness Benchmark Fixture

This is a compact, public, synthetic TypeScript fixture for evaluating coding-agent workflows. It has no customer data, production dependencies, network calls, clock dependence, or paid-service requirement.

The baseline `release-readiness` CLI reads a JSON release manifest, validates it, and reports whether required checks are ready. Required `failed` or `missing` checks block a release; optional issues are reported without blocking. Check output is ordered by ID for deterministic results.

## Prerequisites and setup

Use Node.js 22 or later. Install exactly from the committed lockfile:

```sh
npm ci
```

Run the baseline checks:

```sh
npm run typecheck
npm test
npm run cli -- examples/ready.json
npm run cli -- examples/blocked.json --json
```

Exit codes: `0` means ready, `2` means valid input with blocking checks, `64` means invalid CLI usage, and `65` means unreadable or invalid manifest input.

## Baseline versus measured work

The TypeScript fixture intentionally contains only the green baseline. Do not treat its baseline test output as a benchmark result. A later, separately recorded session may perform [Benchmark 001](benchmark-001/TASK.md), then follow its [acceptance](benchmark-001/ACCEPTANCE.md) and [reset](benchmark-001/RESET.md) instructions. The future feature is not implemented in this baseline.

## Instruction and skill research

The [research archive](research/README.md) records the skill studies, their isolation correction, controlled global-instruction screens, known-answer coding calibration, and the completed [three-arm DeepSWE comparison](research/deepswe-2026-09/README.md). It includes instruction snapshots, compact results, source provenance, replay instructions, [credit accounting](research/deepswe-2026-09/credits.md), and both retained guides. The [continuation guide](research/CONTINUE.md) identifies the current evidence, portable tools, and the delegation experiment paused before scored execution. These studies are separate from the original Benchmark 001 fixture and do not alter its acceptance contract.

## Reusable evaluation suite — preparation

The [v1 preparation guide](benchmarks/v1/README.md) and [evaluation plan](research/evaluation-v1/PLAN.md) define the next comparison: acceptable, maintainable code per total workflow cost, including all subagents and failed attempts. They include a [24-scenario task backlog](benchmarks/v1/manifest.json), a [blinded maintainability rubric](benchmarks/v1/rubrics/maintainability.md), an [initial globals/delegation protocol](protocols/initial-globals-delegation.json), and an [incumbent-versus-candidate template](protocols/candidate-vs-incumbent.json) for future changes.

Run the planning-only checks with Python 3.12 or later:

```sh
python -B tools/benchmark/validate_plan.py
python -B -m unittest discover -s tools/benchmark -p 'test_*.py' -v
```

This is a planning foundation, **not 24 implemented tasks or a validated execution harness**. The checks do not call models or authorize spending. Task packages, protected confirmation cases, runtime controls, and a separately approved pilot remain required. Historical results and installed globals are unchanged.

## License

MIT. See [LICENSE](LICENSE).

