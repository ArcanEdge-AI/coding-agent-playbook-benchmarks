import { ManifestError, compareUtcIso8601Timestamps, isUtcIso8601Timestamp } from "./parse";
import { EvaluationResult, ReleaseManifest } from "./types";

export function evaluateManifest(manifest: ReleaseManifest, asOf?: string): EvaluationResult {
  const waivers = manifest.waivers ?? [];
  if (waivers.length > 0 && asOf === undefined) {
    throw new ManifestError("An as-of UTC timestamp is required when waivers are present.");
  }
  if (asOf !== undefined && !isUtcIso8601Timestamp(asOf)) {
    throw new ManifestError("as-of must be a valid UTC ISO-8601 timestamp ending in Z.");
  }
  const waiversByCheckId = new Map(waivers.map((waiver) => [waiver.checkId, waiver]));
  const checks = [...manifest.checks]
    .sort((left, right) => (left.id < right.id ? -1 : left.id > right.id ? 1 : 0))
    .map((check) => {
      const waiver = waiversByCheckId.get(check.id);
      if (!waiver) return { ...check, blocking: check.required && check.status !== "passed" };
      const state: "active" | "expired" = compareUtcIso8601Timestamps(asOf!, waiver.expiresAt) <= 0 ? "active" : "expired";
      return {
        ...check,
        blocking: state === "expired",
        waiver: { ...waiver, state }
      };
    });
  const blockingCount = checks.filter((check) => check.blocking).length;
  const nonBlockingIssueCount = checks.filter((check) => !check.blocking && check.status !== "passed").length;
  return { releaseId: manifest.releaseId, checks, blockingCount, nonBlockingIssueCount, ready: blockingCount === 0 };
}
