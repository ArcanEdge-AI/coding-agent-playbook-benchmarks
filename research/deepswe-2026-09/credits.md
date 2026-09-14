# Credit cost and delegation interpretation

This analysis prices the existing **54 scored attempts** using OpenAI's [published Codex credit rates](https://learn.chatgpt.com/docs/pricing#token-rates), retrieved September 13, 2026. It makes no additional model calls. [Exact rates](credit-rates.json), [recomputed totals](credits.json), [original session usage](graded-outcomes.json).

| Condition | Attempts | Raw full passes | Standard credit equivalent | Direct helper credits | Helper share |
|---|---:|---:|---:|---:|---:|
| No custom globals | 18 | 2 | 580.08 | 0.00 | 0.0% |
| Previous globals | 18 | 6 | 724.22 | 48.33 | 6.7% |
| Revised globals | 18 | 4 | 884.19 | 36.75 | 4.2% |
| Total | 54 | 12 | 2,188.49 | 85.08 | 3.9% |

For each session, credits equal `((input - cached_input) × input_rate + cached_input × cached_rate + output × output_rate) / 1,000,000`. Cached input is a subset of input; reasoning output is already included in output. Each session uses its actual recorded model's rate. Root and child histories were already deduplicated by the native usage audit. Failed attempts and timeouts consume credits and remain in the numerator.

## What changes when tokens are priced

Luna helpers accounted for approximately 52% and 41% of uncached tokens in the previous and revised arms, but only **6.7% and 4.2% of estimated credits**. A raw-token share overstates their direct credit share because Luna's rates are much lower than the larger root models. Coordination can also consume root tokens; that indirect cost cannot be isolated from these observations.

Across the 18 valid previous-versus-revised pairs, the revised arm cost **22.1% more estimated credits** and produced **4 full passes versus 6**. Credits per full pass rose from **120.70 to 221.05**, an **83.1% increase**. This is descriptive evidence on this sample, not a universal policy result. The earlier raw-token comparison did not include the model weighting and discounted cached-input charges used here.

The all-three-arm matched comparison excludes slot 010 for the confirmed baseline-only grader defect; its 17-attempt credit and pass totals are provided separately in `credits.json`. Preserve the baseline's raw zero without treating it as a demonstrated coding failure. See [grading and denominator limitations](results.md).

The experiments do **not** establish that subagents caused either the gains over baseline or the revised arm's losses: other global clauses changed too. Mandatory delegation has not demonstrated enough repeatable benefit to justify a universal requirement. Direct helper cost alone is also insufficient reason to declare all delegation uneconomical. A clean repeated ablation would be needed to separate these effects; the [planned follow-up](../deepswe-delegation-ablation-2026-09/README.md) was stopped for cost before any scored runs.

## Pro 20× and billing limits

These are **Standard-speed credit equivalents**, not measured purchased-credit deductions or a percentage of a monthly Pro allowance. The $200 Pro 20× plan provides included usage limits relative to Plus, and purchased credits can extend usage after included limits. The published documentation does not provide a fixed monthly credit allocation for this calculation. Do not divide the estimates by 20 or assume the subscription price purchases an equivalent top-up balance. [Plan rules](https://learn.chatgpt.com/docs/pricing).

Actual per-request speed tiers and before/after billing balances were not captured. [Fast mode has higher rates](https://learn.chatgpt.com/docs/agent-configuration/speed). Interrupted requests can omit their final usage. Earlier invalid/interrupted starts, the earlier skill and prompt studies, the research-controller conversation, and the later capability probe are outside these 54 scored totals. No financial charge or quota consumption is inferred from the estimates alone.

## Recompute without inference

From this directory:

```sh
python -B tools/verify_results.py
python -B tools/credit_costs.py --check
```

`credit_costs.py` without `--check` regenerates `credits.json` from the checked-in session usage and frozen rate card. It has no network or model access.
