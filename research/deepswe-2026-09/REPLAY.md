# Replay recipe

The historical study used Windows Python 3.12 with Docker Desktop Linux containers. The runtime files here are exact copies of the exercised extensions. The portable preparation wrapper is new; its offline configuration checks are separate from a fresh end-to-end replay. Do not describe generated configuration alone as a completed benchmark.

1. Obtain the pinned [DeepSWE source](https://github.com/datacurve-ai/deep-swe/tree/0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea) and [Pier source](https://github.com/datacurve-ai/pier/tree/0c802fc067a425345b24d1c69411aa98acf61a1d). Use source archives or checkouts with original LF bytes; avoid Git newline conversion. The wrapper verifies every indexed source file, not merely a branch name.
2. Create a separate Python 3.12 environment. `requirements-observed.txt` records exact observed package versions (Windows-only dependencies carry platform markers). Install them, then install the pinned Pier checkout with `--no-deps -e`. This is an observed environment inventory, not a wheel-hash lock or a guarantee that packages remain available.
3. Pull the three recorded image tags from `images.json`. The wrapper requires their recorded IDs and digests. Verify Docker has capacity for two author/grader trials, each at 2 CPUs and 8 GiB. Do not stop unrelated workloads.
4. Use an existing authorized Codex sign-in profile. Pass its `auth.json` path as `--auth-file`; do not copy the file into this repository or print its contents. Generated private configuration and evidence must live outside this repository, separate from pinned sources.
5. Before spending inference on a new environment, repeat the three nop and six reference-solution grading controls with Pier, then run `CleanCodex` with `probe_only: true` for each task image. A probe runs no model inference. Verify filesystem denial, workspace/Git operations, direct/proxy network denial, CLI version, required model/effort routes and exact startup context. Keep failed controls and do not proceed until they are explained.
6. Prepare one arm using the command shape below. Preparation checks source hashes and local image digests, creates new configs, and freezes their hashes. It does not run subjects or modify installed instructions. Start only the intended arm; each run consumes up to 18 model sessions plus any native helpers.

```text
python tools/replay.py prepare --arm none --work-dir <new-external-directory> --deep <pinned-deepswe-source> --pier-source <pinned-pier-source> --pier <pinned-environment-pier-executable> --auth-file <existing-auth-json>
python tools/replay.py run --work-dir <same-external-directory>
```

Use `previous` and `revised` in separate new work directories for the other arms. Do not use one arm's patches, answers, failures or intermediate results to coach another. The global text is placed only in each subject container's isolated home. Default native base instructions and repository instructions remain in all arms.

The wrapper allows one start per slot and stops queued starts after an infrastructure failure; valid author timeouts are recorded and not retried. Create a `PAUSE` file in the work directory to prevent queued starts while allowing current trials to drain. An interrupted or invalid arm needs explicit adjudication; the wrapper deliberately has no resume or force-overwrite mode.

## Acceptance and audit

Retain the complete result tree, including `startup-input.json`, `preflight.json`, native `sessions/`, instruction timing, submission status, `artifacts/model.patch`, `verifier/ctrf.json` and `verifier/reward.json`. Match each result to its frozen task/model/effort slot. Compare native base instructions, unchanged prompt context and selected test names across arms, removing only the exact global wrapper, recorded date and ephemeral argument-directory suffix.

Whole-task success requires all selected feature and regression checks. Confirm reward values against individual CTRF entries, and inspect build/collection failures before interpreting zero or missing checks. Preserve original rewards if a grader defect is diagnosed. Only committed patches are submitted; report timeouts, partial commits and empty patches separately.

Use `tools/session_accounting.py` to sum each native root/helper session's own usage, excluding inherited history. Require valid parent lineage, actual model/effort routes, no usage arithmetic anomalies and explicit missing-usage reporting. The pinned Pier single-session token field is not sufficient when helpers run. Run the hand-calculated accounting fixtures with:

```text
python -B -m unittest discover -s tools -p test_session_accounting.py
```

After all required evidence is captured, verify the run's owner label has no remaining containers. Inspect exact owned containers before removal and preserve any still needed for diagnosis. Do not run broad Docker prune commands. Seal raw evidence with file hashes and publish only reviewed, portable artifacts. Record any deviation from the original protocol as a new experiment.
