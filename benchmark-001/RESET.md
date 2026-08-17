# Reset Benchmark 001

The frozen baseline is tagged `benchmark-001-baseline-v1`. The playbook's Benchmark 001 specification records the tag's exact commit SHA; verify the two agree before a measured run.

Start from a disposable clone or checkout, then run:

```sh
git fetch --tags origin
git switch --detach benchmark-001-baseline-v1
git rev-parse HEAD
git status --short
```

The reported commit must match the SHA in the playbook specification, and `git status --short` must be empty. Do not use these instructions to discard work in another checkout. Create a new branch from the detached baseline before implementing the benchmark task.
