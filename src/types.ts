export type CheckStatus = "passed" | "failed" | "missing";

export interface ReleaseCheck {
  id: string;
  required: boolean;
  status: CheckStatus;
  summary?: string;
}

export interface ReleaseManifest {
  releaseId: string;
  checks: ReleaseCheck[];
}

export interface EvaluatedCheck extends ReleaseCheck {
  blocking: boolean;
}

export interface EvaluationResult {
  releaseId: string;
  checks: EvaluatedCheck[];
  blockingCount: number;
  nonBlockingIssueCount: number;
  ready: boolean;
}

