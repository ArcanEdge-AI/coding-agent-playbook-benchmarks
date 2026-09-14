# Release Readiness Benchmark Fixture

This is a compact, public, synthetic TypeScript fixture for evaluating coding-agent workflows. It has no customer data, production dependencies, network calls, clock dependence, or paid-service requirement.

The baseline `release-readiness` CLI reads a JSON release manifest, validates it, and reports whether required checks are ready. Required `failed` or `missing` checks block a release; optional issues are reported without blocking. Check output is ordered by ID for deterministic results.

## Prerequisites and setup

Use Node.js 22 or later. Install exactly from the committed lockfile:

```sh
npm ci
```

Run the checks:

```sh
npm run typecheck
npm test
npm run cli -- examples/ready.json
npm run cli -- examples/blocked.json --json
npm run cli -- examples/waived.json --as-of 2026-08-19T00:00:00Z
npm run cli -- examples/waived.json --json --as-of 2026-08-21T00:00:00Z
```

Exit codes: `0` means ready, `2` means valid input with blocking checks, `64` means invalid CLI usage, and `65` means unreadable or invalid manifest input.

## Expiring waivers

Manifests may include a `waivers` array for failed required checks. Each waiver has a unique `checkId`, non-empty `reason`, and a real UTC ISO-8601 `expiresAt` timestamp ending in `Z`. A manifest with one or more waivers requires `--as-of <UTC timestamp>`; the CLI never reads the system clock. At or before its expiry, a waiver makes only its targeted failed required check non-blocking. After expiry, it is reported as expired and remains blocking. Human output labels active waivers as `WAIVED`; JSON includes nested waiver metadata with an `active` or `expired` state.

## Baseline versus measured work

This repository contains the green baseline plus the scoped, expiring-waiver feature used by [Benchmark 001](benchmark-001/TASK.md). Do not treat local test output as a benchmark result.

## Instruction and skill research

The [research archive](research/README.md) records the skill studies, their isolation correction, controlled global-instruction screens, known-answer coding calibration, and the completed [three-arm DeepSWE comparison](research/deepswe-2026-09/README.md). It includes instruction snapshots, compact results, source provenance, replay instructions, [credit accounting](research/deepswe-2026-09/credits.md), and both retained guides. The [continuation guide](research/CONTINUE.md) identifies the current evidence, portable tools, and the delegation experiment paused before scored execution. These studies are separate from the original Benchmark 001 fixture and do not alter its acceptance contract.

## License

MIT. See [LICENSE](LICENSE).
