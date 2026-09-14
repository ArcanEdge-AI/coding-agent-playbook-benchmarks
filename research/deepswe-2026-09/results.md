# DeepSWE: no globals, previous globals and revised globals

State: **completed**. Audited matched triplets: **18/18**. The revised text is the nine-change candidate prepared before DeepSWE testing. It has been applied to the installed globals and maintained Codex source at the user's request. This run tests that candidate without further instruction tuning.

| Measure | No custom globals | Previous globals | Revised globals |
|---|---:|---:|---:|
| Raw complete passes | 2/18 | 6/18 | 4/18 |
| Passes excluding confirmed grader interference | 2/17 | 5/17 | 3/17 |
| Author timeouts | 4 | 6 | 8 |
| Empty committed patches | 4 | 6 | 6 |
| Native author minutes | 231.8 | 257.7 | 262.5 |
| Native helpers | 0 | 19 | 10 |
| Reported input tokens (root + helpers) | 74,016,319 | 147,164,023 | 148,560,215 |
| Cached subset of input | 71,626,112 | 141,521,536 | 144,364,800 |
| Uncached input | 2,390,207 | 5,642,487 | 4,195,415 |
| Reported output tokens (root + helpers) | 517,659 | 857,919 | 734,253 |

Whole-task success requires every selected feature and regression test. Raw scores are unchanged. The matched comparison excludes slots 010 for confirmed grader interference; it does not substitute an alternate score. Empty patches overlap with timeouts. Existing regression tests passing on an unchanged submission do not mean the feature was implemented.

Direct two-arm comparisons retain all valid pairs in those two arms: revised versus none has **17** pairs and **2 → 3** full passes; revised versus previous has **18** pairs and **6 → 4** full passes. A baseline-only grader defect does not invalidate a previous-versus-revised pair. Denominator clarification (local archive: `REPORTING-NOTE.md`).

## Model and effort settings

| Root setting | No custom globals | Previous globals | Revised globals |
|---|---:|---:|---:|
| luna-medium | 0/3 | 1/3 | 1/3 |
| luna-high | 1/3 | 2/3 | 1/3 |
| luna-max | 0/3 | 0/3 | 0/3 |
| terra-high | 0/3 | 1/3 | 1/3 |
| sol-high | 1/3 | 1/3 | 0/3 |
| astra-high | 0/3 | 1/3 | 1/3 |

## Per-task results

Arrows mean **none → previous → revised**. Feature and regression counts describe the committed patch, not uncommitted work left after a timeout.

| Slot | Root setting | Task | Whole-task reward | Feature checks | Regression checks | Revised status | Revised helpers | Evidence |
|---|---|---|---|---|---|---|---:|---|
| 001 | luna-high | Links | 0 → 1 → 0 | 59/60 → 60/60 → 59/60 | 1131/1131 → 1131/1131 → 1131/1131 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-001/obsidian-linter-link-format-conv__JSCXYnK/result.json`) |
| 002 | luna-high | Go | 1 → 1 → 1 | 30/30 → 30/30 → 30/30 | 12/12 → 12/12 → 12/12 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-002/kcp-go-multiplexed-kcp-streams__LSwCLNW/result.json`) |
| 003 | sol-high | Python | 0 → 0 → 0 | 0/72 → 0/72 → 0/72 | 1286/1286 → 1286/1286 → 1286/1286 | timeout | 3 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-003/python-statemachine-state-data-s__BzsaFTq/result.json`) |
| 004 | terra-high | Go | 0 → 1 → 1 | 29/30 → 30/30 → 30/30 | 12/12 → 12/12 → 12/12 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-004/kcp-go-multiplexed-kcp-streams__DXHzB34/result.json`) |
| 005 | luna-max | Go | 0 → 0 → 0 | 0/30 → 0/30 → 0/30 | 12/12 → 12/12 → 12/12 | timeout | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-005/kcp-go-multiplexed-kcp-streams__a2yBbmd/result.json`) |
| 006 | sol-high | Links | 0 → 1 → 0 | 58/60 → 60/60 → 58/60 | 1131/1131 → 1131/1131 → 1131/1131 | completed | 2 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-006/obsidian-linter-link-format-conv__zaitT4u/result.json`) |
| 007 | luna-high | Python | 0 → 0 → 0 | 67/72 → 0/72 → 65/72 | 1286/1286 → 1286/1286 → 1286/1286 | timeout | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-007/python-statemachine-state-data-s__5RQ9CuX/result.json`) |
| 008 | luna-max | Python | 0 → 0 → 0 | 0/72 → 0/72 → 0/72 | 1286/1286 → 1286/1286 → 1286/1286 | timeout | 1 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-008/python-statemachine-state-data-s__piVNLBj/result.json`) |
| 009 | astra-high | Python | 0 → 0 → 0 | 69/72 → 69/72 → 0/72 | 1286/1286 → 1286/1286 → 1286/1286 | timeout | 1 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-009/python-statemachine-state-data-s__zkxwGvg/result.json`) |
| 010 | astra-high | Go | 0 → 1 → 1 | 0/30 → 30/30 → 30/30 | 0/12 → 12/12 → 12/12 | timeout; excluded: confirmed grader interference | 1 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-010/kcp-go-multiplexed-kcp-streams__iJt4kkE/result.json`) |
| 011 | luna-medium | Go | 0 → 0 → 1 | 13/30 → 26/30 → 30/30 | 12/12 → 12/12 → 12/12 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-011/kcp-go-multiplexed-kcp-streams__iQU8z4A/result.json`) |
| 012 | luna-medium | Links | 0 → 1 → 0 | 58/60 → 60/60 → 58/60 | 1131/1131 → 1131/1131 → 1131/1131 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-012/obsidian-linter-link-format-conv__t6oSxHD/result.json`) |
| 013 | astra-high | Links | 0 → 0 → 0 | 59/60 → 59/60 → 59/60 | 1131/1131 → 1131/1131 → 1131/1131 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-013/obsidian-linter-link-format-conv__gSYQ7Dp/result.json`) |
| 014 | terra-high | Python | 0 → 0 → 0 | 67/72 → 0/72 → 0/72 | 1262/1286 → 1286/1286 → 1286/1286 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-014/python-statemachine-state-data-s__NtKqTPS/result.json`) |
| 015 | sol-high | Go | 1 → 0 → 0 | 30/30 → 0/30 → 0/30 | 12/12 → 12/12 → 12/12 | timeout | 2 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-015/kcp-go-multiplexed-kcp-streams__kCLp8nJ/result.json`) |
| 016 | terra-high | Links | 0 → 0 → 0 | 59/60 → 59/60 → 58/60 | 1131/1131 → 1131/1131 → 1131/1131 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-016/obsidian-linter-link-format-conv__PpAMr8g/result.json`) |
| 017 | luna-medium | Python | 0 → 0 → 0 | 43/72 → 39/72 → 67/72 | 1284/1286 → 1286/1286 → 1286/1286 | completed | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-017/python-statemachine-state-data-s__JdA9zFY/result.json`) |
| 018 | luna-max | Links | 0 → 0 → 0 | 0/60 → 0/60 → 59/60 | 1131/1131 → 1131/1131 → 1131/1131 | timeout | 0 | Evidence (local archive: `../deepswe-updated-global-v1/runs-full/updated-018/obsidian-linter-link-format-conv__oojCfDw/result.json`) |

## Interpretation

The revised instructions did not outperform the previous instructions on the frozen whole-task acceptance criterion. Raw full passes were **2/18 without custom globals, 6/18 with previous globals and 4/18 with revised globals**. The shared comparison excluding the confirmed baseline Go grader fault is **2/17, 5/17 and 3/17**. Direct previous-versus-revised comparison retains all eighteen valid pairs: one whole-task gain, three losses and fourteen unchanged outcomes. This is mixed exploratory evidence, not a validated instruction upgrade or proof of a general decline.

The result is more informative than the full-pass totals alone:

- Revised Luna/medium improved Go from 26/30 to 30/30 feature checks and Python from 39/72 to 67/72 versus previous globals. Revised Luna/high Python submitted a 65/72 patch after the previous arm submitted none. Revised Luna/max links submitted a 59/60 patch after neither earlier arm committed a feature patch.
- Revised Astra/Python lost its earlier 69/72 submitted coverage because it timed out before committing. Revised Sol/links missed trailing destination whitespace; revised Luna/medium links lost the filename alt text when dropping image dimensions. These are substantive submission or requested-behavior losses.
- Some raw declines are oracle effects: Luna/high links lost its previous full pass only because valid angle-bracket syntax was rejected. Terra/links' additional miss has the same cause; its actual whitespace-conversion miss already existed in both prior arms. Luna/max links and Astra/links also missed only that oracle check. No alternate rewards are substituted.

Across all eighteen direct previous-versus-revised pairs, the number of passed feature checks increased in **four**, stayed the same in **nine**, and declined in **five**. Equal totals can still hide different failures, as the Luna/medium link notes show. Every selected regression check passed in the revised arm, as in the previous arm, but six revised submissions contained no committed changes. Unchanged starter regressions passing cannot establish that an unsubmitted implementation preserved behavior.

The resource tradeoff was also mixed. Relative to previous globals, revised globals used **10 rather than 19 helpers**, **25.6% less uncached input** (4,195,415 versus 5,642,487) and **14.4% fewer output tokens** (734,253 versus 857,919). Total reported input, including the large cached subset, increased **0.9%** to 148,560,215. Summed native author time increased **1.9%**, from 257.7 to 262.5 minutes. These observations do not imply a dollar or subscription-quota saving. No-global author time was 231.8 minutes, with 2,390,207 uncached input and 517,659 output tokens.

Author timeouts increased from six to eight versus previous globals, while empty committed patches stayed at six. Three revised timeouts nevertheless retained committed feature patches; one passed all selected tests. The external twenty-minute cap was not disclosed to authors, so these outcomes reflect this submission protocol and budget, not unrestricted coding ability or informed deadline planning.

The safeguard and routing questions remain open. Terra still stopped its Python submission for Git attribution details but handled the same obstacle locally in TypeScript. Observed helpers all followed Luna/max routing; that confirms compliance with the configured route, not that it is the best route. The [behavior and safeguards review](behavior.md) records these examples, an attribution concern, validation limits and the important categories this test did not exercise.

All eighteen revised contexts and results passed the audit, with ten native helpers, no usage arithmetic anomalies and no missing session-usage records. The CLI error-event review found only the expected under-development-feature warning. There were no invalid revised attempts or newly diagnosed grader faults. Earlier faults and oracle limitations remain documented without rescoring.

The nine authorized changes remain installed and mirrored in the maintained Codex source. The practical conclusion is to retain this as a tested candidate with known tradeoffs, not advertise it as a proven reliability improvement. Any further optimization should be a separately defined experiment with explicit submission assumptions, meaningful acceptance contracts, repeated trials and unseen tasks. The current three-task, single-attempt sample cannot justify a universal global policy, a model ranking or a causal claim about one changed sentence. No additional experiment was started here.


## What this comparison controls

All three arms retain the native base instructions, task prompts, source commits, selected acceptance tests, task images, CLI `0.154.0-alpha.6.2`, model/effort routes, schedule and concurrency of two. Containers use 2 CPUs and 8 GiB. The 1,200-second author cap includes preflight; the unchanged upstream prompt does not disclose this shortened cap. Grading retains its 1,800-second limit and committed-patch extraction. Subjects receive no earlier answers or grading feedback. No valid failure or timeout is retried.

Only the custom global text differs. Skills, optional references, memories, apps and web remain absent. Native helper tools were available in every arm despite the legacy `features.multi_agent=false` setting. The preflight field `helpers: 0` is historical intent, not an observed count. Actual root/helper sessions determine the helper and usage totals. Conditional delegation is part of the revised treatment; Luna/max helper routing remains unchanged.

Usage sums each native session's own reported totals, excluding inherited fork history and duplicate cumulative notifications. Cached input is already included in input. Root author time includes helper activity inside that interval. These are observed tokens and elapsed time, not billed cost or subscription-quota consumption; interrupted requests may not emit final usage. Context, tests and session audit (local archive: `result-audit-full.json`), [usage arithmetic checks](tools/test_session_accounting.py).

## Limits of the evidence

- Three previously observed calibration tasks and one attempt per setting/task/arm cannot establish a reliable general instruction effect or a model ranking. Arms ran sequentially with unblinded analysis; service load and cache behavior may differ.
- The baseline Astra/Go grader overlay removed author test helpers still referenced elsewhere. Its raw zero is inconclusive for coding quality and is excluded from matched effect claims. Baseline diagnosis (local archive: `../deepswe-calibration-v1/go-overlay-diagnostic-v2.json`).
- The link oracle rejects a valid CommonMark angle-bracket destination containing spaces; Python's active-state-without-data contract is implicit. These are known acceptance-contract limitations, not grounds for editing scores after seeing results. Oracle review (local archive: `../deepswe-calibration-v1/oracle-review.md`).
- A timeout or missing committed patch is a workflow outcome under this budget. It is not a verdict on the correctness of unfinished or uncommitted code. A build failure or suite hang can cause many missing checks without demonstrating that many independent defects.
- The selected upstream regression tests do not cover each project's entire behavior. This study does not separately validate every safeguard, optimal model routing, installed skills, optional reference loading or real production operations.

## Installation and preservation

The installed revision is frozen in [updated-global.md](instructions/revised.md), SHA256 `03f0069eeba198806c29dbc24a88097220c7fd5af10aaff265d8b377b8b5e325`. Its normalized body matches the previously prepared candidate. Only the nine substitutions were applied; the installed wrapper and all other bytes were preserved. [Installation provenance and backups](provenance.json), [instruction diff with normalized line endings](instructions/changes.patch), runtime-only provenance diff (local archive: `runtime-diff.patch`), finite run plan (local archive: `PLAN.md`).

All earlier study artifacts remain sealed and untouched. Their historical live-source checks still expect the old globals, so the new preservation verification explicitly records the authorized installed/source deltas. No research helper agents or auxiliary worktrees are used. Full local evidence remains in this archive; the benchmark repository receives a portable, compact research package.


This is a portable rendering of the local report. Archive locators are not repository links. Native sessions and individual patches remain in the original archive; see [provenance](provenance.json).
