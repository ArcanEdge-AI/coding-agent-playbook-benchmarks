import { readFileSync } from "node:fs";
import { formatHuman, formatJson } from "./format";
import { evaluateManifest } from "./evaluate";
import { ManifestError, isUtcIso8601Timestamp, parseManifestJson } from "./parse";

export const EXIT = { ready: 0, blocked: 2, invalidInput: 65, usage: 64 } as const;

export function run(argv: string[], io: Pick<NodeJS.Process, "stdout" | "stderr"> = process): number {
  let json = false;
  let asOf: string | undefined;
  const positional: string[] = [];
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--json") {
      if (json) return usage(io);
      json = true;
    } else if (argument === "--as-of") {
      if (asOf !== undefined || index + 1 >= argv.length || argv[index + 1].startsWith("--")) return usage(io);
      asOf = argv[index + 1];
      index += 1;
    } else if (argument.startsWith("-")) {
      return usage(io);
    } else {
      positional.push(argument);
    }
  }
  if (positional.length !== 1) {
    return usage(io);
  }
  if (asOf !== undefined && !isUtcIso8601Timestamp(asOf)) {
    io.stderr.write("Error: as-of must be a valid UTC ISO-8601 timestamp ending in Z.\n");
    return EXIT.invalidInput;
  }
  try {
    const manifest = parseManifestJson(readFileSync(positional[0], "utf8"));
    const result = evaluateManifest(manifest, asOf);
    io.stdout.write(json ? formatJson(result) : formatHuman(result));
    return result.ready ? EXIT.ready : EXIT.blocked;
  } catch (error) {
    const message = error instanceof ManifestError ? error.message : `Unable to read manifest: ${(error as Error).message}`;
    io.stderr.write(`Error: ${message}\n`);
    return EXIT.invalidInput;
  }
}

function usage(io: Pick<NodeJS.Process, "stdout" | "stderr">): number {
  io.stderr.write("Usage: release-readiness <manifest.json> [--json] [--as-of <UTC ISO-8601 timestamp>]\n");
  return EXIT.usage;
}

if (require.main === module) process.exitCode = run(process.argv.slice(2));
