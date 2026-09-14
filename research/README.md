# Instruction and skill evaluation research

This folder records the September 2026 evaluation of skill wording, global instructions and real coding tasks. The studies answer different questions and must not be pooled into one success rate.

The [DeepSWE comparison](deepswe-2026-09/README.md) is completed: **54 scored attempts**, comparing no custom globals, previous globals, and the previously prepared revised globals across three tasks and six model/effort settings. The [credit analysis](deepswe-2026-09/credits.md) recomputes costs from recorded root and helper usage. Earlier studies and corrections are summarized in [the research history](history.md).

The [delegation ablation](deepswe-delegation-ablation-2026-09/README.md) was paused by the user for cost before any of its 48 planned scored attempts. Its preparation and probe status are retained; it has no comparative coding results. **No further inference is authorized by this archive.** Use the [continuation guide](CONTINUE.md) to pick up the work from this repository.

The [prompting evidence guide](guides/prompting-evidence-guide.md) and [skill maintenance guide](guides/skill-maintenance-guide.md) are retained separately. They are practical guidance with explicit evidence limits, not validated universal policies.

## Next study: reusable evaluation v1

The [evaluation plan](evaluation-v1/PLAN.md) and [preparation guide](../benchmarks/v1/README.md) define a new path for testing acceptable code per total workflow cost. The repository now includes a [24-scenario authoring backlog](../benchmarks/v1/manifest.json), a [blinded maintainability rubric](../benchmarks/v1/rubrics/maintainability.md), [initial globals/delegation conditions](../protocols/initial-globals-delegation.json), and a [future revision template](../protocols/candidate-vs-incumbent.json).

These are proposed designs and offline planning tools, **not implemented task packages, validated runtime controls, scored results, or inference authorization**. Development/confirmation splits and model/budget choices remain unresolved. Public scenario descriptions are not sealed confirmation evidence. The next implementation work is task authoring and independent grader/runtime validation, followed by a separately approved pilot. Do not automatically restart the old 48-run proposal.

The [offline validator](../tools/benchmark/validate_plan.py) checks metadata consistency only. Its [unit tests](../tools/benchmark/test_validate_plan.py) are tests of the planning tool, not coding-agent performance. Existing experimental artifacts remain unchanged.

## Evidence levels

- Structural parsing checks that a file is well formed; it does not prove runtime discovery or behavior.
- Offered-choice and free-form responses reveal decisions or proposed behavior; they do not prove that a live workflow succeeds.
- Independently executed artifact checks establish the behavior they actually test.
- Repository tasks with frozen external grading measure committed implementations and completion under the stated runtime budget.
- General reliability claims require sufficiently difficult, clear tasks, matched repeated runs and a confirmation set that was not used to revise the instructions.

## Archive boundary

This repository holds portable protocols, instruction snapshots, compact measurements, reusable accounting/verification code, and source checksums. Full local evidence includes prompts, native sessions, patches, individual grading reports, runtime probes, all failed attempts and preserved historical artifacts. It is not copied wholesale into a public repository. Raw sessions can contain machine context and sensitive material; the published package does not include authentication files, private local paths or full transcripts.

The source index names archive-relative artifacts and hashes, so a holder of the original archive can verify correspondence. A digest is an integrity reference, not a substitute for publicly available raw evidence. Model self-reports are not used as the sole correctness measure.
