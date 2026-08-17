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

## License

MIT. See [LICENSE](LICENSE).

