# Continue the research from this repository

## Current state and authority

The latest completed coding study is `deepswe-2026-09`: **54 scored attempts, 18 per instruction arm**. Its revised arm is complete. The later delegation ablation is **paused by the user for additional cost**, with **0 of 48 planned scored attempts started**. Do not automatically resume, retry, purchase credits, redeem credits, or launch model calls. Obtain a new request authorizing further inference before executing another experiment. Offline inspection, recomputation and preparation do not require paid inference.

No global instructions were changed by the paused ablation. Its `current.md` is the exact installed revised snapshot at preparation time, SHA256 `03f0069eeba198806c29dbc24a88097220c7fd5af10aaff265d8b377b8b5e325`. Preserve that snapshot as historical evidence. If the user's installed globals have changed, define and snapshot a new treatment instead of quietly replacing the old one.

## Start here

1. Read [completed results](deepswe-2026-09/results.md), [credit analysis](deepswe-2026-09/credits.md), and [behavior/safeguard observations](deepswe-2026-09/behavior.md).
2. Read [research history](history.md) before interpreting the earlier skill and synthetic tests. Keep the [prompting guide](guides/prompting-evidence-guide.md) and [skills guide](guides/skill-maintenance-guide.md) separate.
3. Verify the data with the offline commands below. Do not rerun model experiments merely to recover existing numbers.
4. For delegation work, read the [paused experiment status](deepswe-delegation-ablation-2026-09/README.md), exact instruction diff, and draft-runtime limitation before changing or executing its scripts.

From the repository root:

```sh
python -B research/deepswe-2026-09/tools/verify_results.py
python -B research/deepswe-2026-09/tools/credit_costs.py --check
python -B -m unittest discover -s research/deepswe-2026-09/tools -p test_session_accounting.py
python -B research/deepswe-delegation-ablation-2026-09/tools/verify_preparation.py
```

On Windows, `py -3.12 -B` can replace `python -B`. All four commands use checked-in data and make no model calls. The repository's TypeScript fixture has its own `npm test` and `npm run typecheck`; those are not research outcomes.

## What the completed study supports

Raw full passes were **2/18 without globals, 6/18 with previous globals, and 4/18 with revised globals**. Excluding the baseline-only grader fault from the matched three-arm set gives **2/17, 5/17, 3/17**. Previous versus revised retains all 18 valid pairs. Standard credit equivalents were **580.08, 724.22, and 884.19**, totaling **2,188.49**. Direct helper credits were **0, 48.33, and 36.75**.

The revised arm used fewer helper tokens but cost more estimated credits after model and cache weighting. Helpers accounted for only about 4–7% of credit equivalents in the instruction-enabled arms. These observations do not isolate the effect of delegation: other instructions changed simultaneously. Neither mandatory delegation, the selected helper route, nor every safeguard is established as beneficial by this experiment.

Three known tasks, one attempt per original cell, sequential arms, an undisclosed twenty-minute author cap, and known oracle issues limit general conclusions. A confirmation study should use clear, difficult, previously unseen tasks and repeated, controlled conditions. Do not tune instructions against these task answers and then present the same tasks as an unseen confirmation set.

## Reusable assets and environment

| Need | Repository location |
|---|---|
| Original study recipe and portable preparation/run CLI | [REPLAY.md](deepswe-2026-09/REPLAY.md), [tools/replay.py](deepswe-2026-09/tools/replay.py) |
| Pinned source and image identity | `deepswe-2026-09/upstream-index.json`, `images.json`, `runtime-packages.json` |
| Exact original instruction treatments | `deepswe-2026-09/instructions/` |
| Test identities, per-attempt grades and usage | `acceptance-tests.json`, `graded-outcomes.json` |
| Native root/helper accounting with inherited-history exclusion | `deepswe-2026-09/tools/session_accounting.py` |
| Model-weighted credits and frozen rate card | `deepswe-2026-09/tools/credit_costs.py`, `credit-rates.json` |
| Paused ablation instruction edits, status and draft runner | `deepswe-delegation-ablation-2026-09/` |

The pinned experiment used DeepSWE commit `0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea`, Pier commit `0c802fc067a425345b24d1c69411aa98acf61a1d` (0.3.1), Codex CLI `0.154.0-alpha.6.2`, Docker CPU task images, and an authenticated evaluation profile. See the existing replay guide for exact setup and arguments. Authentication is supplied through an external local auth-file path; it is never checked into this repository. API-key billing is a different route and should not silently replace the recorded ChatGPT-authenticated route.

Generated workspaces must be outside the repository and outside preserved evidence. The scripts require explicit local paths; there is no dependency on the original task's private absolute path. Never create a new attempt in a directory containing a previous start marker. Save source/image/runtime identities and the exact proposed budget before paid execution.

## Next unresolved delegation step

The user selected **current globals intact with helpers available** versus **the same globals with delegation clauses removed and helpers disabled**. This tests the whole delegation setup, not only tool availability. The planned design was four models at high reasoning, three tasks, two repeats, two conditions; helpers would use Luna/max. The contemplated 48 scored runs were paused for cost, and the budget is not active authorization.

One short disabled capability probe completed, with zero child sessions and a `CONTROL_UNAVAILABLE` response. The enabled probe stopped at a preflight assertion before inference. The assertion expected `<multi_agent_role>` in the captured Linux prompt; that expectation was not valid for the observed probe context. Separate offline debug checks showed that `agents.enabled` changes context under some configurations. **The paired runtime control is not yet validated.** Do not equate absent prompt text or a model's response with proof that all helper tools are disabled. The earlier `features.multi_agent=false` flag did not stop actual V1 helper calls.

After renewed authorization, first inspect the draft capability gate against the exact selected model/runtime and obtain direct native execution evidence for both settings, including an actual enabled child and no disabled children. Preserve the failed probe; do not count it as a coding failure. Fix and test prompt-parity, route and accounting checks before freezing any scored schedule. The draft runner has not passed a scored end-to-end run and must not be described as production-ready.

Prefer a bounded next step agreed with the user; the prior 48-run proposal estimated 2,800–3,400 Standard credits and was declined for that additional cost. Do not infer a Pro subscription percentage or a hard credit cap from that estimate. If inference is later authorized, record an explicit budget and stop rules, include failed attempts in cost per correct solution, and report uncertainty and non-delegating enabled runs.

## Evidence retention and publication

Full native sessions, committed patches, verifier logs and original probes remain in separate local archives identified by `provenance.json` and source indexes. Repository copies contain compact grades, per-session token totals, instruction snapshots and hashes. The originals are needed for new transcript-level claims, but not to recompute the published grades or credit totals. An archive hash is not independently inspectable raw evidence.

Keep prior measured artifacts immutable. Append a new study directory for new conditions or corrected measurements, describe exclusions without inventing replacement scores, and update this guide plus `research/README.md`. Review generated files for auth data, private paths and raw transcripts before committing or publishing. Never install new global instructions as a side effect of a benchmark run.

The repository's `.gitattributes` disables newline conversion inside `research/` so historical instruction bytes and hashes survive Windows and Linux checkouts. Preserve that rule when moving the research to another repository.
