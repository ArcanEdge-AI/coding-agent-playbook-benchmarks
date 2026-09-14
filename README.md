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

This repository intentionally contains only the green baseline. Do not treat its baseline test output as a benchmark result. A later, separately recorded session may perform [Benchmark 001](benchmark-001/TASK.md), then follow its [acceptance](benchmark-001/ACCEPTANCE.md) and [reset](benchmark-001/RESET.md) instructions. The future feature is not implemented in this baseline.

## Instruction and skill research

The [research archive](research/README.md) records the skill studies, their isolation correction, controlled global-instruction screens, known-answer coding calibration, and the completed [three-arm DeepSWE comparison](research/deepswe-2026-09/README.md). It includes instruction snapshots, compact results, source provenance, replay instructions, [credit accounting](research/deepswe-2026-09/credits.md), and both retained guides. The [continuation guide](research/CONTINUE.md) identifies the current evidence, portable tools, and the delegation experiment paused before scored execution. These studies are separate from the original Benchmark 001 fixture and do not alter its acceptance contract.

## Repeatable benchmark preparation

The [v2 benchmark package](research/benchmark-v2/README.md) adds a reusable comparison protocol, six development-task specifications, a draft paired pilot manifest, blinded maintainability criteria, and tested offline planning/reporting tools. It separates instruction effects, delegation-package effects, and helper-route comparisons, and defines protected confirmation data for future revisions.

The task specifications are not yet executable fixtures, the live runtime controls remain unvalidated, and no paid inference is authorized. This package does not change installed globals, historical results, or the original fixture. Start with the v2 README for offline commands and remaining prerequisites.

## License

MIT. See [LICENSE](LICENSE).

