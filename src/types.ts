export type CheckStatus = "passed" | "failed" | "missing";

export interface ReleaseCheck {
  id: string;
  required: boolean;
  status: CheckStatus;
  summary?: string;
}

export interface ReleaseWaiver {
  checkId: string;
  reason: string;
  expiresAt: string;
}

export interface ReleaseManifest {
  releaseId: string;
  checks: ReleaseCheck[];
  waivers?: ReleaseWaiver[];
}

export interface EvaluatedWaiver extends ReleaseWaiver {
  state: "active" | "expired";
}

export interface EvaluatedCheck extends ReleaseCheck {
  blocking: boolean;
  waiver?: EvaluatedWaiver;
}

export interface EvaluationResult {
  releaseId: string;
  checks: EvaluatedCheck[];
  blockingCount: number;
  nonBlockingIssueCount: number;
  ready: boolean;
}
