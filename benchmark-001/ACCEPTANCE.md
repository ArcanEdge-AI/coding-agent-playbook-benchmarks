# Benchmark 001 acceptance

The implementation is accepted only after it meets every applicable criterion below from the frozen baseline.

- Existing manifests without waivers preserve their prior readiness and exit codes.
- Active waivers affect only failed required checks and only when `--as-of` is supplied at or before their expiry.
- Invalid, unknown, duplicate, expired, and inapplicable waiver cases have deterministic, tested behavior as specified in [TASK.md](TASK.md).
- Output is stable by check ID and clearly distinguishes normal, active-waived, and expired-waiver cases in both human and JSON forms.
- Parser, evaluator, formatter/API, and CLI exit-code coverage includes the new edge cases.
- `npm ci`, `npm run typecheck`, and `npm test` pass. Include CLI smoke checks using public synthetic examples.
- Before declaring completion, request an independent code review, correct substantiated findings, and rerun the affected validation. Record the commands and results in the session handoff.

There is no line-count, elapsed-time, private-service, or paid-tool requirement. Keep the diff focused and do not commit benchmark results to this repository.

