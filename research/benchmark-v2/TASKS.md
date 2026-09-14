# Reusable task bank and admission contract

**These six development specifications are proposed task designs, not executable coding fixtures or measured outcomes.** No task is marked validated in `pilot.json`. Build them in realistic, licensed/sanitized repository snapshots before running agents. Do not publish private client code or future holdout solutions. They are intentionally visible development cases and must never be described as unseen confirmation tasks.

## Proposed development set

| ID | Task and required behavior | Independent acceptance checks | Delegation characteristic |
|---|---|---|---|
| `ts-boundary-validation` | Repair a manifest validator without changing its public return type. Reject duplicate IDs and contradictory required-check states; preserve optional-check semantics and deterministic output. Supply exact empty/null/whitespace contracts in the task. | Reject valid-looking invalid manifests; accept legitimate existing inputs; preserve CLI exit codes, sorting, build/types and unrelated fields. Verify failed behavior before the repair. | Small coherent bug; direct completion should be possible without coordination |
| `ts-cross-layer-feature` | Add a bounded filter to an existing API, service and client adapter. Preserve no-filter behavior and existing pagination semantics; define ordering and empty-result behavior explicitly. | API validation, service selection, pagination boundaries and client serialization; regression/build checks; no second competing data path. | Multi-file task with shared integration responsibilities |
| `py-transaction-import` | Implement an atomic batch import with idempotency keys using the repository's storage abstraction. Exact duplicates are no-ops; conflicting duplicates fail; a rejected batch leaves storage unchanged. | Duplicate inside/across batches, rollback after partial progress, malformed input, retry after failure, stable summary counts and existing imports. | Bounded data-integrity work; independent adversarial review may help |
| `py-compatible-refactor` | Consolidate two duplicated parsing paths behind the existing interface without changing output/error types or documented normalization. No new parsing framework. | Differential tests over valid/invalid inputs, legacy edge cases, no public API break, meaningful focused tests and clear ownership. | Maintainability signal even when both solutions pass functionality |
| `go-cancellation-cleanup` | Fix cancellation and close behavior in an existing worker pipeline. Cancelled work must stop; resources must be released; repeated close must be safe; preserve error propagation. | Deterministic channel-based tests, blocked producer/consumer cases, repeated close, cancellation races, original regressions and race detector where supported. Avoid relying on fragile sleeps alone. | Tightly coupled reasoning; extra writers may hurt rather than help |
| `go-independent-adapters` | Add two bounded adapters to an existing shared interface plus registration/integration. Define exact error and empty-input behavior. Reuse existing conversion helpers. | Separate adapter contracts plus registry integration, unsupported inputs, errors, deterministic output and compatibility. | Genuine independent implementation units with an integration gate |

These are family-level descriptions. A task author must turn each into a complete unambiguous request, starting source, expected public behavior, and independent tests. Do not use one tiny synthetic fixture as a substitute for realistic multi-file work. Freeze the mix before treatment outcomes are visible, and pilot difficulty without claiming a general policy from six tasks.

## Every admitted fixture must contain

An evaluator-controlled bundle with `TASK.md`, pinned baseline commit, source/license record, environment/lockfile or image digest, source-visible regression tests, independent feature/regression grader, reference patch, at least two plausible faulty patches, and a machine-readable task manifest. The task manifest records `id`, `version`, `split`, `language`, `task_family`, complexity/delegability tags, `used_for_tuning`, source commit, prompt/grader SHA256, environment digest, allowed paths/actions, explicit deadline/submission envelope, acceptance contract, and preflight evidence.

Preflight must show that the starting source passes intended starter regressions but fails the requested feature tests; the reference patch passes every declared gate; plausible incorrect patches fail relevant checks; and different valid implementation choices are not rejected. Re-run the grader in clean checkouts to check determinism and avoid overlay contamination. Version any changed contract, environment or grader. Do not reuse a grader with known unfair checks just because it existed historically.

Tasks must not depend on real credentials, external writes, purchased services, production databases, unstable clocks, or data belonging to clients without permission. Include controlled failure fixtures for unavailable capabilities. A grader should test observable behavior rather than infer quality from diff size, commit count, or a model's narrative.

## Regression inventory

Keep the archived TypeScript link conversion, Python state-data, and Go multiplexed-stream tasks as **historical regression/calibration** sources. The archive documents valid syntax rejected by the link oracle, implicit Python contract details, and a Go overlay fault. Correcting those creates new versioned fixtures with their own preflight records, not replacement historical results. Benchmark 001 remains a separate public fixture with its original acceptance contract.

## Confirmation partition

Select fresh tasks from different issues and, where feasible, different repositories in the intended workload. Reserve them before instruction editing and keep requests, solutions and grader details outside the instruction-authoring environment. Public hashes/opaque IDs can establish which fixtures were frozen without exposing them. The tested agent receives the task request and permitted source at execution, never the reference solution or hidden grader.

A developer who authored these six specifications should not call them personally unseen. A held-out parameter change on the same familiar solution is also weak confirmation. Record repository/task-family overlap. Once confirmation feedback guides an instruction revision, retire those cases to regression and select fresh confirmation tasks. Repeatedly checking an unchanged private suite is still adaptive reuse; log it and limit feedback.

## Task promotion checklist

1. Complete source, task and grader bundles; record licensing/privacy review and all hashes.
2. Validate baseline/reference/faulty implementations and deterministic clean-room grading.
3. Have an independent reviewer check ambiguity, meaningful difficulty, and rubric applicability.
4. Fill the exact manifest fields and set `status: validated` only with retained evidence.
5. Freeze partition, sampling weights, runtime and schedule before inference authorization.

An admission checklist or a non-null evidence filename is not proof of those steps. The included preparation tool only reports missing fields; the evaluator must inspect and verify the actual bundles.
