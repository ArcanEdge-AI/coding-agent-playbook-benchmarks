# Benchmark 001: Scoped expiring waivers

Starting from the frozen baseline commit, add support for narrowly scoped, expiring waivers for failed required checks.

## Required behavior

Extend the manifest schema with an optional `waivers` array. Each waiver must contain a non-empty unique `checkId`, a non-empty `reason`, and an `expiresAt` UTC ISO-8601 timestamp ending in `Z`. Add a required CLI option `--as-of <UTC ISO-8601 timestamp ending in Z>` whenever the input has waivers. Never read the system clock.

A waiver is valid only when it names an existing required check whose status is `failed`. At or before `expiresAt`, it changes that check from blocking to non-blocking and marks the result as waived. An expired waiver is ignored for readiness but reported deterministically. Unknown check IDs, duplicate waiver check IDs, malformed waiver objects/timestamps, a waiver for an optional/passed/missing check, or using waivers without `--as-of` are invalid input and must use the documented invalid-input exit code.

Keep existing no-waiver behavior compatible. Human and JSON output must make active and expired waivers observable, remain stably ordered by check ID, and preserve the existing documented exit-code meanings. Update tests, examples, README, and public API exports as needed.

## Non-goals

Do not add persistence, a database, accounts, network calls, a live clock, third-party packages, CI configuration, private services, or a generic policy engine. Do not change unrelated baseline behavior.

