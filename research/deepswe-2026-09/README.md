# DeepSWE global instruction comparison

This is an exploratory, time-limited local comparison, not an official leaderboard reproduction. It uses three known calibration tasks and one attempt per root setting/task/arm. No universal instruction benefit or model ranking follows from this sample.

Arms:

1. **None:** native Codex base instructions and repository instructions, no custom global file.
2. **Previous:** the complete prior installed global file, including mandatory repository delegation.
3. **Revised:** the previously prepared nine-change candidate, including conditional delegation and reuse of existing authority. It was applied to the user's installed globals and maintained Codex source when this third arm was authorized.

The [results](results.md) and [machine-readable measurements](results.json) identify completion state. [Snapshots](instructions/) preserve the exact previous and revised global bytes; `substitutions.json` gives the nine replacements. The prepared revised body predates DeepSWE and was not tuned using task answers.

[Selected test names](acceptance-tests.json) and [per-attempt statuses and session usage](graded-outcomes.json) allow reward and token-total recomputation without copying raw transcripts. Run `python -B tools/verify_results.py` from this directory to reconcile those records with the report. The export includes original CTRF, reward and patch hashes for archive verification.

[Per-attempt review notes](review-notes.json) distinguish observed acceptance failures, submission failures, oracle ambiguities and author-reported validation. These notes explain the original grades without changing them.

The [behavior and safeguards review](behavior.md) examines delegation, submission, attribution, blocked checks and the limits of the tested safeguards without adding a retrospective score.

The later [credit analysis](credits.md) prices the same 54 recorded attempts without new inference. Run `python -B tools/credit_costs.py --check` to verify it. The [planned delegation ablation](../deepswe-delegation-ablation-2026-09/README.md) was paused for cost before any scored runs and does not add a fourth measured arm. See the repository [continuation guide](../CONTINUE.md).

## Fixed protocol

| Control | Value |
|---|---|
| DeepSWE | `datacurve-ai/deep-swe`, commit `0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea` |
| Pier | `datacurve-ai/pier`, commit `0c802fc067a425345b24d1c69411aa98acf61a1d` (0.3.1) |
| Codex CLI | `0.154.0-alpha.6.2` |
| Root routes | Luna medium/high/max; Terra high; Sol high; Astra high |
| Sample | TypeScript link conversion, Python scoped state data, Go KCP streams |
| Attempts | 18 per arm, one per task/setting, same fixed order |
| Concurrency | 2 |
| Container resources | 2 CPUs, 8 GiB per author/grader container |
| Author cap | 1,200 seconds including preflight; native author time recorded separately |
| Grader cap | 1,800 seconds |
| Submission | Committed patch only; task prompt requires branch and commit |
| Retry | No retry of a valid failure or timeout |
| Excluded context | Skills, optional reference documents, memory, apps and web |
| Primary result | Every selected upstream feature and regression test passes |

The unchanged upstream author prompt does not disclose the shorter external deadline. The original upstream author default is three hours. These budgeted workflow outcomes should not be described as unrestricted model coding ability.

Task selection used a frozen SHA256 ordering by seed and task ID within each language's prebuilt CPU tasks. The initially selected Python entry had TypeScript source despite Python metadata and was replaced before inference using the same ordering. [Selection and amendment](selection.json), [schedule](schedule.json), [image IDs and digests](images.json).

Reference solutions passed twice in fresh graders and unmodified starters failed all feature checks while passing selected regression checks. [Environment controls](environment-checks.json). Source-file hashes are preserved in `upstream-index.json`. The selected tests do not cover every project behavior.

Native helper tools remained available in every arm despite `features.multi_agent=false`; the unchanged legacy preflight field `helpers: 0` is not an actual count. The baseline created no helpers. Actual native root/helper sessions are audited and summed; parent/child inheritance and duplicate cumulative events are removed. [Accounting implementation](tools/session_accounting.py), [hand-calculated fixtures](tools/test_session_accounting.py). This comparison does not isolate delegation from the rest of the instruction treatment.

## Known limitations

- Baseline Astra/Go suffered grader-overlay interference: hidden preparation removed submitted test helpers still referenced by another submitted file. Retain its raw zero, but exclude the corresponding slot from matched instruction-effect claims. No alternative reward is invented.
- The link oracle rejects a valid CommonMark angle-bracket destination containing spaces. Python leaves an active state without declared data's return contract implicit. Task-contract ambiguity limits interpretation of otherwise valid implementations.
- Timeouts and empty committed patches measure completion under this cap. Many missing tests after one build error or suite hang do not establish many separate bugs. Existing regression tests passing on unchanged code are not feature improvements.
- Three observed tasks, sequential arms, a single sample per cell and unblinded analysis do not establish repeatable causal effects. The same tasks must be excluded from a later confirmation set used for general claims.
- Reported tokens are not prices, billing or account-quota usage. Cached input is a subset of input. Interrupted requests may not emit final usage. Raw Pier usage can omit helper sessions, so audited all-session usage is used.

The baseline's three invalid Git-control starts and previous arm's two interrupted helper-control discovery starts remain in the local archive and are excluded from the scored arms. Their resource use is not silently counted as a valid scored result. The revised arm has its own frozen 18-root-start budget.

## Reproducing the setup

Use the [replay guide](REPLAY.md) and the checked-in runtime extensions. A replay creates fresh evidence; it never overwrites the recorded results. Exact historical model availability, service responses and container tags may change, so the preparation script checks pinned source hashes and image digests and stops on drift.

Full original native sessions, patches, startup captures and test reports remain in the local evidence archive. [Archive provenance](provenance.json) records original hashes; the repository contains compact measurements instead of raw transcripts or authentication data. This distinction limits what an outside reviewer can independently verify from this repository alone.
