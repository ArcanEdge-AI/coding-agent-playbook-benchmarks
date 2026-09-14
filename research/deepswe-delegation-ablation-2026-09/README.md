# Delegation ablation: paused before scored execution

**Paused by the user for additional cost. Zero of 48 planned scored attempts started. There are no comparative coding results from this experiment.** No automatic resume or new inference is authorized. [Machine-readable status](status.json), [continuation guide](../CONTINUE.md).

The selected comparison was the current installed globals intact versus the same file with only delegation instructions removed and native subagent tools disabled. The user chose this package-level comparison after distinguishing it from an experiment that would keep instruction text identical. The installed global file was not changed.

## Prepared artifacts

- [Current instruction snapshot](instructions/current.md): 29,466 bytes.
- [Proposed instructions without subagents](instructions/without-subagents.md): 15,599 bytes.
- [Exact diff](instructions.patch) and [13 edit operations](instruction-edits.json). Unrelated bytes, general engineering requirements, authorization rules and worktree cleanup requirements are preserved. These edits are untested proposals, not applied global changes.
- [Historical proposed protocol](proposed-protocol.md): four models at high reasoning, three known tasks, two repetitions, two conditions, 48 scored starts. Its recorded budget is an inactive proposal after the user's pause.
- [Draft native runtime](controlled_codex.py), [runtime changes](runtime.patch), and [draft runner/accounting code](draft/).

## What actually ran

| Probe | Result | Native model inference | Helpers | Standard credit equivalent |
|---|---|---:|---:|---:|
| Without subagents | Completed; returned `CONTROL_UNAVAILABLE` | One Luna/max root | 0 | 0.07143 |
| Current globals | Preflight assertion failed | None | 0 | None recorded |

The disabled probe reported 12,984 uncached input tokens, no cached input, and 217 output tokens, including 208 reasoning-output tokens. This separate probe is excluded from the [54 scored-run credit totals](../deepswe-2026-09/credits.md). Neither row is a scored coding attempt.

The enabled probe failed because the harness required `<multi_agent_role>` in its captured Linux startup context. That exact expectation was not satisfied. Offline Windows and Linux debug checks showed `agents.enabled` changing delegation context under some configurations, but those checks did not resolve the failing selected-model probe. The control gate remains unvalidated. The earlier legacy `features.multi_agent=false` setting had allowed real V1 helper execution, so a config value or model self-report alone is insufficient evidence.

## Continuing safely and reproducibly

Start with [research/CONTINUE.md](../CONTINUE.md). Verify the prepared instruction edits without inference:

```sh
python -B research/deepswe-delegation-ablation-2026-09/tools/verify_preparation.py
```

[prepare_workspace.py](tools/prepare_workspace.py) can copy the draft runtime into a **new external directory** using explicit source, executable and auth-file paths. `--help` lists those arguments. Preparation does not read auth contents, launch models, install global instructions, or resume the paused experiment. The original task's private workspace is not required to prepare a new attempt.

The draft runner is retained to avoid rebuilding the orchestration, accounting and export logic. **It is not a validated runnable benchmark.** Its capability assertion must be investigated, the paired runtime gate fixed and verified, and the runner reviewed before scoring. The copied draft has no scored end-to-end validation. After a new user request authorizes inference and a budget, use new evidence directories and keep the original failed probe record. Do not run these scripts automatically just because they exist.

The [provenance record](provenance.json) hashes local preparation artifacts without including private paths or raw transcripts. The study was paused, not sealed as a completed experiment.
