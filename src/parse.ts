import { CheckStatus, ReleaseCheck, ReleaseManifest } from "./types";

export class ManifestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ManifestError";
  }
}

const statuses = new Set<CheckStatus>(["passed", "failed", "missing"]);

function asRecord(value: unknown, label: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new ManifestError(`${label} must be an object.`);
  }
  return value as Record<string, unknown>;
}

function nonEmptyString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.trim() === "") {
    throw new ManifestError(`${label} must be a non-empty string.`);
  }
  return value;
}

function parseCheck(value: unknown, index: number): ReleaseCheck {
  const check = asRecord(value, `checks[${index}]`);
  const id = nonEmptyString(check.id, `checks[${index}].id`);
  if (typeof check.required !== "boolean") {
    throw new ManifestError(`checks[${index}].required must be a boolean.`);
  }
  if (typeof check.status !== "string" || !statuses.has(check.status as CheckStatus)) {
    throw new ManifestError(`checks[${index}].status must be passed, failed, or missing.`);
  }
  if (check.summary !== undefined && typeof check.summary !== "string") {
    throw new ManifestError(`checks[${index}].summary must be a string when provided.`);
  }
  return { id, required: check.required, status: check.status as CheckStatus, summary: check.summary as string | undefined };
}

export function parseManifestJson(input: string): ReleaseManifest {
  let value: unknown;
  try {
    value = JSON.parse(input);
  } catch {
    throw new ManifestError("Manifest must be valid JSON.");
  }
  return parseManifest(value);
}

export function parseManifest(value: unknown): ReleaseManifest {
  const manifest = asRecord(value, "manifest");
  const releaseId = nonEmptyString(manifest.releaseId, "releaseId");
  if (!Array.isArray(manifest.checks)) {
    throw new ManifestError("checks must be an array.");
  }
  const checks = manifest.checks.map(parseCheck);
  const ids = new Set<string>();
  for (const check of checks) {
    if (ids.has(check.id)) throw new ManifestError(`Duplicate check id: ${check.id}.`);
    ids.add(check.id);
  }
  return { releaseId, checks };
}

