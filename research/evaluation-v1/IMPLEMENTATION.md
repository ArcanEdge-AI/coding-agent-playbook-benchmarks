# Evaluation plan implementation status

This is the implementation status for the [evaluation design](PLAN.md). Statements in the original design describing all assets as planning-only are superseded by this file and the [runnable development guide](../../benchmarks/v1/README.md).

## Implemented and checked

- Twelve synthetic development task packages with 32 executable Python, TypeScript, and Go source files; four-task smoke selection; immutable package/evaluator/check hashes.
- Fresh standalone repository export, explicit deadlines, fixture-only Git identity, and preserved pre-existing untracked edits.
- External reference, alternative, no-op and distinct incorrect-implementation controls. Test-writing tasks must pass the correct implementation and reject designated mutants.
- A Docker-only untrusted grading interface; expected outputs and reference solutions remain in the host controller rather than the candidate container. No model-launch functionality is hidden in grading or setup.
- Frozen randomized matched schedules for the initial A/B/C and future incumbent/candidate comparisons; clean per-attempt workspaces; no retries or overwriting existing results.
- Own-session root/descendant cost accounting, cache/reasoning overlap handling, missing-usage flags, explicit invalid-run overhead, and route mismatch detection. The historical native parser is reused, not edited.
- Blinded human-review packets with an external mapping, artifact-bound scores, evidence requirements, and no automatic acceptance of unreviewed code.
- JSON and Markdown reports with incomplete-study flags, failed-attempt spending, task-weighted cost/acceptance ratios, paired source-cluster exploratory intervals, and no automatic promotion.
- **54 new harness unit tests passed.** **46 grading controls passed** across the twelve tasks. Go claim controls ran with the race detector. These are offline implementation checks, not agent benchmark outcomes.

Detailed control evidence: [development-controls.json](development-controls.json). The evaluator answers remain in the separately delivered private bundle; [evaluator-bundle.json](evaluator-bundle.json) identifies it. Local runtime versions and file hashes are in [implementation-verification.json](implementation-verification.json).

## Deliberate submission-contract change

The implemented development tasks grade the final workspace snapshot under an explicit 1,200-second deadline. A new commit is not required. Both previously unexecuted protocol templates now state this contract, and the preparer rejects a commit-required protocol rather than silently using workspace output. This separates code evaluation from the historical undisclosed deadline/commit timing issue. It is a new development design; the original 54-run committed-submission scores and archived runtimes remain immutable.

## Not completed or validated

The selected native Codex author executor, effective global-instruction isolation, actual enabled/disabled helper controls, helper-route enforcement, and descendant resource limits still need live runtime validation. Docker is not available in the implementation environment, so container isolation was not operationally demonstrated. The native session parser was not revalidated against a new live session format. There are no new scored model runs or new conclusions about globals/delegation.

The twelve fixtures are intentionally development/calibration material. They are compact synthetic repositories, not a claim of production complexity or statistically independent real-world sources. Their discriminatory difficulty is unknown until an authorized pilot. Twelve independently authored protected confirmation tasks remain outstanding. Human review calibration, double-review adjudication, maintenance follow-ups, power-based sample sizing, and automatic promotion are not implemented by the offline CLI.

## Authority

Repository implementation is not permission to resume the paused 48-run experiment, call models, purchase credits, modify installed globals, or switch authentication/billing routes. First validate the operational controls, freeze the actual treatment bytes and runtime, then obtain a bounded pilot budget. No amount of passing metadata/unit tests substitutes for those gates.
