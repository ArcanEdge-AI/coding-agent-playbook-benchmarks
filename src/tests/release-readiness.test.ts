import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { EXIT, run } from "../cli";
import { evaluateManifest } from "../evaluate";
import { formatHuman, formatJson } from "../format";
import { ManifestError, parseManifestJson } from "../parse";

test("parser rejects malformed JSON, duplicate IDs, and invalid statuses", () => {
  assert.throws(() => parseManifestJson("{"), ManifestError);
  assert.throws(() => parseManifestJson('{"releaseId":"x","checks":[{"id":"a","required":true,"status":"passed"},{"id":"a","required":false,"status":"failed"}]}'), /Duplicate check id/);
  assert.throws(() => parseManifestJson('{"releaseId":"x","checks":[{"id":"a","required":true,"status":"unknown"}]}'), /must be passed/);
});

test("parser validates scoped waiver structure, timestamps, uniqueness, and applicability", () => {
  const base = '{"releaseId":"w","checks":[{"id":"failed","required":true,"status":"failed"},{"id":"passed","required":true,"status":"passed"},{"id":"optional","required":false,"status":"failed"},{"id":"missing","required":true,"status":"missing"}]';
  assert.throws(() => parseManifestJson(`${base},"waivers":{}}`), /waivers must be an array/);
  assert.throws(() => parseManifestJson(`${base},"waivers":[null]}`), /waivers\[0\] must be an object/);
  assert.throws(() => parseManifestJson(`${base},"waivers":[{"checkId":"","reason":"reason","expiresAt":"2026-02-01T00:00:00Z"}]}`), /checkId/);
  assert.throws(() => parseManifestJson(`${base},"waivers":[{"checkId":"failed","reason":"","expiresAt":"2026-02-01T00:00:00Z"}]}`), /reason/);
  assert.throws(() => parseManifestJson(`${base},"waivers":[{"checkId":"failed","reason":"reason","expiresAt":"2026-02-30T00:00:00Z"}]}`), /expiresAt/);
  assert.throws(() => parseManifestJson(`${base},"waivers":[{"checkId":"failed","reason":"reason","expiresAt":"2026-02-01T00:00:00+00:00"}]}`), /expiresAt/);
  assert.throws(() => parseManifestJson(`${base},"waivers":[{"checkId":"unknown","reason":"reason","expiresAt":"2026-02-01T00:00:00Z"}]}`), /unknown/);
  assert.throws(() => parseManifestJson(`${base},"waivers":[{"checkId":"failed","reason":"one","expiresAt":"2026-02-01T00:00:00Z"},{"checkId":"failed","reason":"two","expiresAt":"2026-02-02T00:00:00Z"}]}`), /Duplicate waiver/);
  for (const checkId of ["passed", "optional", "missing"]) {
    assert.throws(() => parseManifestJson(`${base},"waivers":[{"checkId":"${checkId}","reason":"reason","expiresAt":"2026-02-01T00:00:00Z"}]}`), /required failed/);
  }
  assert.equal(evaluateManifest(parseManifestJson(`${base},"waivers":[]}`)).ready, false);
});

test("required failed or missing checks block while optional issues do not", () => {
  const result = evaluateManifest(parseManifestJson('{"releaseId":"r-1","checks":[{"id":"z","required":false,"status":"failed"},{"id":"b","required":true,"status":"missing"},{"id":"a","required":true,"status":"passed"}]}'));
  assert.equal(result.ready, false);
  assert.equal(result.blockingCount, 1);
  assert.equal(result.nonBlockingIssueCount, 1);
  assert.deepEqual(result.checks.map((check) => check.id), ["a", "b", "z"]);
});

test("active waivers apply through their boundary and expired waivers remain blocking", () => {
  const manifest = parseManifestJson('{"releaseId":"w-1","checks":[{"id":"z","required":true,"status":"failed"},{"id":"a","required":true,"status":"passed"}],"waivers":[{"checkId":"z","reason":"bounded exception","expiresAt":"2026-08-20T00:00:00.500Z"}]}');
  assert.throws(() => evaluateManifest(manifest), /as-of/);
  const active = evaluateManifest(manifest, "2026-08-20T00:00:00.500Z");
  assert.equal(active.ready, true);
  assert.equal(active.blockingCount, 0);
  assert.equal(active.nonBlockingIssueCount, 1);
  assert.deepEqual(active.checks.map((check) => check.id), ["a", "z"]);
  assert.deepEqual(active.checks[1].waiver, { checkId: "z", reason: "bounded exception", expiresAt: "2026-08-20T00:00:00.500Z", state: "active" });
  const expired = evaluateManifest(manifest, "2026-08-20T00:00:00.5001Z");
  assert.equal(expired.ready, false);
  assert.equal(expired.blockingCount, 1);
  assert.equal(expired.checks[1].waiver?.state, "expired");
});

test("human formatting is stable and includes classifications", () => {
  const result = evaluateManifest(parseManifestJson('{"releaseId":"r-2","checks":[{"id":"x","required":false,"status":"failed","summary":"optional"}]}'));
  assert.equal(formatHuman(result), "Release: r-2\nStatus: READY\nBlocking checks: 0\nNon-blocking issues: 1\nChecks:\n- [NOTICE] x: failed — optional\n");
});

test("waiver formatting makes active and expired states observable without changing no-waiver JSON", () => {
  const noWaiver = evaluateManifest(parseManifestJson('{"releaseId":"r","checks":[]}'));
  assert.equal(formatJson(noWaiver), '{\n  "releaseId": "r",\n  "checks": [],\n  "blockingCount": 0,\n  "nonBlockingIssueCount": 0,\n  "ready": true\n}\n');
  const manifest = parseManifestJson('{"releaseId":"r","checks":[{"id":"x","required":true,"status":"failed"}],"waivers":[{"checkId":"x","reason":"temporary","expiresAt":"2026-01-02T00:00:00Z"}]}');
  assert.match(formatHuman(evaluateManifest(manifest, "2026-01-01T00:00:00Z")), /\[WAIVED\].*waiver active/);
  assert.match(formatHuman(evaluateManifest(manifest, "2026-01-03T00:00:00Z")), /\[BLOCKING\].*waiver expired/);
  assert.match(formatJson(evaluateManifest(manifest, "2026-01-03T00:00:00Z")), /"state": "expired"/);
});

test("CLI returns documented exit codes and JSON output", () => {
  const directory = mkdtempSync(join(tmpdir(), "release-readiness-"));
  const readyPath = join(directory, "ready.json");
  const badPath = join(directory, "bad.json");
  writeFileSync(readyPath, '{"releaseId":"r-3","checks":[]}');
  writeFileSync(badPath, "not json");
  let stdout = "";
  let stderr = "";
  const io = { stdout: { write: (value: string) => { stdout += value; return true; } }, stderr: { write: (value: string) => { stderr += value; return true; } } } as unknown as Pick<NodeJS.Process, "stdout" | "stderr">;
  assert.equal(run([readyPath, "--json"], io), EXIT.ready);
  assert.match(stdout, /"ready": true/);
  assert.equal(run([badPath], io), EXIT.invalidInput);
  assert.match(stderr, /Manifest must be valid JSON/);
  assert.equal(run([], io), EXIT.usage);
});

test("CLI supports flexible waiver options and preserves invalid-input versus usage exits", () => {
  const directory = mkdtempSync(join(tmpdir(), "release-readiness-waiver-"));
  const waiverPath = join(directory, "waiver.json");
  const noWaiverPath = join(directory, "no-waiver.json");
  writeFileSync(waiverPath, '{"releaseId":"r","checks":[{"id":"x","required":true,"status":"failed"}],"waivers":[{"checkId":"x","reason":"temporary","expiresAt":"2026-01-02T00:00:00Z"}]}');
  writeFileSync(noWaiverPath, '{"releaseId":"r","checks":[]}');
  const output = () => {
    let stdout = "";
    let stderr = "";
    return { io: { stdout: { write: (value: string) => { stdout += value; return true; } }, stderr: { write: (value: string) => { stderr += value; return true; } } } as unknown as Pick<NodeJS.Process, "stdout" | "stderr">, read: () => ({ stdout, stderr }) };
  };
  let capture = output();
  assert.equal(run(["--json", "--as-of", "2026-01-01T00:00:00Z", waiverPath], capture.io), EXIT.ready);
  assert.match(capture.read().stdout, /"state": "active"/);
  capture = output();
  assert.equal(run([waiverPath, "--as-of", "2026-01-03T00:00:00Z", "--json"], capture.io), EXIT.blocked);
  assert.match(capture.read().stdout, /"state": "expired"/);
  capture = output();
  assert.equal(run([waiverPath], capture.io), EXIT.invalidInput);
  assert.equal(run([noWaiverPath, "--as-of", "2026-01-01T00:00:00Z"], capture.io), EXIT.ready);
  assert.equal(run([noWaiverPath, "--as-of", "invalid"], capture.io), EXIT.invalidInput);
  assert.equal(run([noWaiverPath, "--json", "--json"], capture.io), EXIT.usage);
  assert.equal(run([noWaiverPath, "--as-of"], capture.io), EXIT.usage);
  assert.equal(run([noWaiverPath, "--unknown"], capture.io), EXIT.usage);
  assert.equal(run([noWaiverPath, "extra"], capture.io), EXIT.usage);
});

test("CLI treats invalid waiver manifests as invalid input", () => {
  const directory = mkdtempSync(join(tmpdir(), "release-readiness-invalid-waiver-"));
  const cases = [
    ["unknown", '{"releaseId":"r","checks":[],"waivers":[{"checkId":"x","reason":"reason","expiresAt":"2026-01-01T00:00:00Z"}]}'],
    ["duplicate", '{"releaseId":"r","checks":[{"id":"x","required":true,"status":"failed"}],"waivers":[{"checkId":"x","reason":"one","expiresAt":"2026-01-01T00:00:00Z"},{"checkId":"x","reason":"two","expiresAt":"2026-01-02T00:00:00Z"}]}'],
    ["malformed", '{"releaseId":"r","checks":[{"id":"x","required":true,"status":"failed"}],"waivers":[{"checkId":"x","reason":"reason","expiresAt":"invalid"}]}'],
    ["inapplicable", '{"releaseId":"r","checks":[{"id":"x","required":false,"status":"failed"}],"waivers":[{"checkId":"x","reason":"reason","expiresAt":"2026-01-01T00:00:00Z"}]}']
  ];
  for (const [name, contents] of cases) {
    const path = join(directory, `${name}.json`);
    writeFileSync(path, contents);
    const io = { stdout: { write: () => true }, stderr: { write: () => true } } as unknown as Pick<NodeJS.Process, "stdout" | "stderr">;
    assert.equal(run([path, "--as-of", "2026-01-01T00:00:00Z"], io), EXIT.invalidInput, name);
  }
});
