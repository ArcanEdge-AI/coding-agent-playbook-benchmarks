import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { EXIT, run } from "../cli";
import { evaluateManifest } from "../evaluate";
import { formatHuman } from "../format";
import { ManifestError, parseManifestJson } from "../parse";

test("parser rejects malformed JSON, duplicate IDs, and invalid statuses", () => {
  assert.throws(() => parseManifestJson("{"), ManifestError);
  assert.throws(() => parseManifestJson('{"releaseId":"x","checks":[{"id":"a","required":true,"status":"passed"},{"id":"a","required":false,"status":"failed"}]}'), /Duplicate check id/);
  assert.throws(() => parseManifestJson('{"releaseId":"x","checks":[{"id":"a","required":true,"status":"unknown"}]}'), /must be passed/);
});

test("required failed or missing checks block while optional issues do not", () => {
  const result = evaluateManifest(parseManifestJson('{"releaseId":"r-1","checks":[{"id":"z","required":false,"status":"failed"},{"id":"b","required":true,"status":"missing"},{"id":"a","required":true,"status":"passed"}]}'));
  assert.equal(result.ready, false);
  assert.equal(result.blockingCount, 1);
  assert.equal(result.nonBlockingIssueCount, 1);
  assert.deepEqual(result.checks.map((check) => check.id), ["a", "b", "z"]);
});

test("human formatting is stable and includes classifications", () => {
  const result = evaluateManifest(parseManifestJson('{"releaseId":"r-2","checks":[{"id":"x","required":false,"status":"failed","summary":"optional"}]}'));
  assert.equal(formatHuman(result), "Release: r-2\nStatus: READY\nBlocking checks: 0\nNon-blocking issues: 1\nChecks:\n- [NOTICE] x: failed — optional\n");
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

