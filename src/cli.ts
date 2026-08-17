import { readFileSync } from "node:fs";
import { formatHuman, formatJson } from "./format";
import { evaluateManifest } from "./evaluate";
import { ManifestError, parseManifestJson } from "./parse";

export const EXIT = { ready: 0, blocked: 2, invalidInput: 65, usage: 64 } as const;

export function run(argv: string[], io: Pick<NodeJS.Process, "stdout" | "stderr"> = process): number {
  const json = argv.includes("--json");
  const positional = argv.filter((argument) => argument !== "--json");
  if (positional.length !== 1 || argv.length !== positional.length + (json ? 1 : 0)) {
    io.stderr.write("Usage: release-readiness <manifest.json> [--json]\n");
    return EXIT.usage;
  }
  try {
    const manifest = parseManifestJson(readFileSync(positional[0], "utf8"));
    const result = evaluateManifest(manifest);
    io.stdout.write(json ? formatJson(result) : formatHuman(result));
    return result.ready ? EXIT.ready : EXIT.blocked;
  } catch (error) {
    const message = error instanceof ManifestError ? error.message : `Unable to read manifest: ${(error as Error).message}`;
    io.stderr.write(`Error: ${message}\n`);
    return EXIT.invalidInput;
  }
}

if (require.main === module) process.exitCode = run(process.argv.slice(2));

