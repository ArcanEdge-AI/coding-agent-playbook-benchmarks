import { EvaluationResult, ReleaseManifest } from "./types";

export function evaluateManifest(manifest: ReleaseManifest): EvaluationResult {
  const checks = [...manifest.checks]
    .sort((left, right) => (left.id < right.id ? -1 : left.id > right.id ? 1 : 0))
    .map((check) => ({ ...check, blocking: check.required && check.status !== "passed" }));
  const blockingCount = checks.filter((check) => check.blocking).length;
  const nonBlockingIssueCount = checks.filter((check) => !check.blocking && check.status !== "passed").length;
  return { releaseId: manifest.releaseId, checks, blockingCount, nonBlockingIssueCount, ready: blockingCount === 0 };
}
