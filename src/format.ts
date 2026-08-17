import { EvaluationResult } from "./types";

export function formatHuman(result: EvaluationResult): string {
  const lines = [
    `Release: ${result.releaseId}`,
    `Status: ${result.ready ? "READY" : "BLOCKED"}`,
    `Blocking checks: ${result.blockingCount}`,
    `Non-blocking issues: ${result.nonBlockingIssueCount}`,
    "Checks:"
  ];
  for (const check of result.checks) {
    const severity = check.blocking ? "BLOCKING" : check.status === "passed" ? "OK" : "NOTICE";
    lines.push(`- [${severity}] ${check.id}: ${check.status}${check.summary ? ` — ${check.summary}` : ""}`);
  }
  return `${lines.join("\n")}\n`;
}

export function formatJson(result: EvaluationResult): string {
  return `${JSON.stringify(result, null, 2)}\n`;
}

