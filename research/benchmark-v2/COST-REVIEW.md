# Offline review of the existing cost increase

Source: [`deepswe-2026-09/credits.json`](../deepswe-2026-09/credits.json) at repository commit `a3eafe072bcec8b801bbf28853ebbe016803838c`. These are differences between published aggregates, not a new model experiment, independent native-session audit, or measured billing ledger.

For all 18 valid previous-versus-revised pairs, subtracting previous from revised gives:

| Component | Change in estimated Standard credits |
|---|---:|
| Total | +159.972401 |
| Main agent | +171.561375 |
| Direct helpers | -11.588974 |
| Uncached input | -8.228465 |
| Cached input | +152.501376 |
| Output | +15.699490 |

The role rows sum to the total, and the three token-category rows independently sum to the same total. **Do not add both breakdowns together.** The main-agent cost increase exceeds the net increase because direct helper cost fell. Most of the net increase is in priced cached input; this does not mean caching caused the increase or that cached input was more expensive than uncached input. Model mixture, number of requests, context length and service cache behavior can all matter, and these aggregates do not separate their effects.

The model-weighted contribution can be reproduced without inference:

```sh
python -B research/benchmark-v2/tools/review_costs.py research/deepswe-2026-09/credits.json
python -B research/benchmark-v2/tools/review_costs.py research/deepswe-2026-09/credits.json --matched-17
```

The model breakdown groups sessions by actual model, including helpers; it is **not** a breakdown by root assignment. The matched-17 output is separate and must not be combined with the all-18 comparison. The original credit calculator and native-session verifier remain the authority for the archived arithmetic.

## Further analysis requiring the retained local evidence

Review each paired patch and timeline, distinguishing requested-behavior defects, valid alternatives rejected by the grader, missing submissions, and genuine infrastructure faults. Independently label main-agent spans for discovery, implementation, assignment preparation, child-output review, integration and repeated validation, retaining unknown/mixed spans. Check whether higher context cost reflects more root requests, larger contexts or model/session routing. Record the classification method and disagreements.

Do not infer these mechanisms from cost shares or invent a new maintainability score from aggregate test results. An independent blind patch review is possible only when the retained patches are available. Any such analysis is new supplementary evidence; the original scored results and exclusions remain immutable.
