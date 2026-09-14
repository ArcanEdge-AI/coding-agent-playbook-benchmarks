# Research history and limits

These are separate experiments. Task counts, model effort, instruction placement, runtime, retry policy and scoring differ. Reported passing checks are not independent estimates of future task reliability.

| Stage | Recorded result | What it establishes and what it does not |
|---|---|---|
| Initial skill pilot | 80 responses; 56 executable Python checks | A small initial screen. It did not establish global-free isolation or complete live skill workflows. |
| Broad skill inventory | 468 discovered entries, 437 distinct entrypoint contexts; 2,108 main responses and 23 diagnostics/recoveries | 4,200/4,216 offered-choice checks passed. Across 360 paired requests, 12 candidate improvements, 0 regressions and 348 both passing. The cases have a ceiling and were not live integrations. |
| Targeted skill remediation | 125 total requests; final 68/68 requests accepted | Eleven skill areas, multiple revisions and retained failed attempts. Final acceptance is not first-attempt reliability. Forty final Python assertions passed. |
| Installed skill corrections | 100 instruction files: 85 entrypoints and 15 references; 405 output-only requests | Final-source checks passed 640/640 decisions and 48/48 open-ended probes, with 20 named executable checks. Earlier failures remain in the archive. This does not prove global-free or end-to-end performance. |
| Isolation correction | An evaluation stopped after 31/48 planned calls | The old configuration did not establish the claimed absence of installed globals. Earlier output and artifact results survive; their global-free claims do not. See the correction below. |
| Controlled custom-base screen | 48 calls | A separate policy screen using custom base instructions. It is not equivalent to retaining the native base and adding a global file. |
| Native-global response screen | 42 calls per arm, 126 total; six settings and seven fixtures | None, previous and revised globals all met 42/42 frozen core criteria and 102/102 interval assertions per arm. Previous globals proposed needless delegation in 4/6 trivial edits; none and revised did so in 0/6. No helpers actually executed in this screen. |
| Real TypeScript feature | Six settings per arm, 12 coding sessions | Frozen checks improved from 254/264 without globals to 260/264 with previous globals; separate review checks changed from 8/12 to 7/12. An empty-waiver contract ambiguity and timeout qualifications prevent simple model ranking. |
| Known-answer coding calibration | 18/18 accepted across scheduler, ledger and decoder tasks | Every setting hit 3/3; the suite was too easy to detect improvement. No global comparison was run on this saturated suite. |
| DeepSWE calibration and matched globals | Three tasks × six settings per arm | Real repository editing, independent selected tests and committed patches under a 20-minute author cap. See the dedicated package for all three arms, costs, failures and oracle limitations. |

The skill studies used Astra/Sol/Terra at xhigh and Luna at max. The later global/coding studies used Luna at medium/high/max and Terra/Sol/Astra at high. These are different routes, not interchangeable rows.

## Isolation correction

The early runner used `project_doc_max_bytes=0`, `model_instructions_file`, and `--ignore-user-config`. Later prompt inspection retained the installed global AGENTS.md. The debug command was not a byte-for-byte capture of every historical inference payload, which was not retained; therefore the precise old payloads are unknown. The observed discovery behavior invalidates the assurance that these runs were global-free.

An empty, separately authenticated home and startup inspection established the later controlled configuration. Every later native-global response-screen startup was checked before inference. DeepSWE additionally preserves actual native session metadata, base instructions and initial context, and checks treatment occurrence and paired prompt parity. This does not retroactively repair the earlier skill isolation claim.

The lesson is to inspect the effective context and actual capabilities, not infer them from configuration names. In DeepSWE, `features.multi_agent=false` did not remove native helper tools. Baseline subjects used no helpers; previous-global subjects used 19. The approved full-workflow comparison held that availability constant and measured the difference instead of silently changing tools between arms.

## What survived the research

Directly rewriting a conflicting rule and its references was more dependable in the observed skill probes than appending a generic exception. Preserving supplied choices, quantities, units, attribution and already granted authority produced useful targeted corrections. These are bounded observations; isolated skill baselines and real workflows still require further evaluation.

The controlled response screen showed no core-score gain from either long global file. Input totals were 275,119 without globals, 495,535 with previous globals and 505,363 with the revised candidate. Those are tokens, not dollar charges, and they cannot predict full coding-workflow costs. The original TypeScript and DeepSWE studies illustrate why actual code, hidden tests, task ambiguity, submission state and resource limits must also be inspected.

The revised global candidate was prepared before DeepSWE. Its nine substitutions address conditional delegation, permission reuse, scoped blockers, instruction hierarchy, supplied choices, fact fidelity, observable validation and bounded completion. Luna/max helper routing was retained as an unresolved hypothesis. Applying the candidate is an authorized configuration decision; it is not itself evidence that the candidate improves reliability.

For provenance, [the source index](source-index.json) identifies the original reports and preserved artifact hashes. Guides retain the isolation correction. Previous reports' statements that globals were unchanged describe their historical runs; the later installation is separately recorded in the DeepSWE package.

## Completed DeepSWE, credit analysis and paused follow-up

All three DeepSWE arms completed, totaling 54 scored attempts. Raw full passes were 2/18, 6/18 and 4/18; the common 17-pair set excluding the baseline-only grader interference yielded 2/17, 5/17 and 3/17. The [completed report](deepswe-2026-09/results.md) preserves exact denominators, oracle limits and individual outcomes.

The later [credit analysis](deepswe-2026-09/credits.md) used those existing session records, with no additional scored inference. Standard equivalents were 580.08, 724.22 and 884.19 credits. Direct Luna helper cost was only 6.7% and 4.2% of the two instruction-enabled arms; token shares alone overstated their direct credit share. The comparison still does not isolate delegation from other instruction changes.

The user selected a repeated comparison of current globals intact against only delegation instructions removed plus helper tools disabled. [Preparation was paused for additional cost](deepswe-delegation-ablation-2026-09/README.md) before any of 48 proposed scored runs. One small disabled capability probe completed; the enabled probe failed a harness preflight assertion before inference. No comparative coding outcome follows. The proposed instruction copies, unresolved gate and portable draft scripts are retained for a future explicitly authorized continuation. Installed globals were unchanged by this preparation. [Continue from this repository](CONTINUE.md).
