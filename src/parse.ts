import { CheckStatus, ReleaseCheck, ReleaseManifest, ReleaseWaiver } from "./types";

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

const utcTimestamp = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?Z$/;

export function isUtcIso8601Timestamp(value: string): boolean {
  const match = utcTimestamp.exec(value);
  if (!match) return false;
  const [, yearText, monthText, dayText, hourText, minuteText, secondText] = match;
  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  const hour = Number(hourText);
  const minute = Number(minuteText);
  const second = secondText === undefined ? 0 : Number(secondText);
  if (month < 1 || month > 12 || hour > 23 || minute > 59 || second > 59) return false;
  const daysInMonth = [31, year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return day >= 1 && day <= daysInMonth[month - 1];
}

export function compareUtcIso8601Timestamps(left: string, right: string): number {
  const leftMatch = utcTimestamp.exec(left)!;
  const rightMatch = utcTimestamp.exec(right)!;
  const leftSecond = leftMatch[6] ?? "00";
  const rightSecond = rightMatch[6] ?? "00";
  const leftWhole = `${leftMatch[1]}-${leftMatch[2]}-${leftMatch[3]}T${leftMatch[4]}:${leftMatch[5]}:${leftSecond}`;
  const rightWhole = `${rightMatch[1]}-${rightMatch[2]}-${rightMatch[3]}T${rightMatch[4]}:${rightMatch[5]}:${rightSecond}`;
  if (leftWhole < rightWhole) return -1;
  if (leftWhole > rightWhole) return 1;
  const precision = Math.max(leftMatch[7]?.length ?? 0, rightMatch[7]?.length ?? 0);
  const leftFraction = (leftMatch[7] ?? "").padEnd(precision, "0");
  const rightFraction = (rightMatch[7] ?? "").padEnd(precision, "0");
  return leftFraction < rightFraction ? -1 : leftFraction > rightFraction ? 1 : 0;
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

function parseWaiver(value: unknown, index: number): ReleaseWaiver {
  const waiver = asRecord(value, `waivers[${index}]`);
  const checkId = nonEmptyString(waiver.checkId, `waivers[${index}].checkId`);
  const reason = nonEmptyString(waiver.reason, `waivers[${index}].reason`);
  const expiresAt = nonEmptyString(waiver.expiresAt, `waivers[${index}].expiresAt`);
  if (!isUtcIso8601Timestamp(expiresAt)) {
    throw new ManifestError(`waivers[${index}].expiresAt must be a valid UTC ISO-8601 timestamp ending in Z.`);
  }
  return { checkId, reason, expiresAt };
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
  if (manifest.waivers === undefined) return { releaseId, checks };
  if (!Array.isArray(manifest.waivers)) throw new ManifestError("waivers must be an array when provided.");
  const waivers = manifest.waivers.map(parseWaiver);
  const waiverIds = new Set<string>();
  for (const waiver of waivers) {
    if (waiverIds.has(waiver.checkId)) throw new ManifestError(`Duplicate waiver check id: ${waiver.checkId}.`);
    waiverIds.add(waiver.checkId);
    const check = checks.find((candidate) => candidate.id === waiver.checkId);
    if (!check) throw new ManifestError(`Waiver references unknown check id: ${waiver.checkId}.`);
    if (!check.required || check.status !== "failed") {
      throw new ManifestError(`Waiver must reference a required failed check: ${waiver.checkId}.`);
    }
  }
  return { releaseId, checks, waivers };
}
