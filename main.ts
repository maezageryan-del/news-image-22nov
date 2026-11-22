// main.ts — entrypoint for the news-image-20261122 bounty.
// Copies the pre-rendered entry.png (drawn by render.py from stories.json:
// the 22 November 2026 broadsheet, 1024x1024) byte-for-byte to
// $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
// Node 22, standard library only. No network access.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const outPath = join(outDir, "entry.png");

let png: Buffer;
try {
  png = readFileSync(sourcePath);
} catch {
  fail(`cannot read ${sourcePath}`);
}

if (png.length < 8 || !png.subarray(0, 8).equals(PNG_MAGIC)) {
  fail("entry.png does not start with PNG magic bytes");
}

try {
  mkdirSync(outDir, { recursive: true });
  writeFileSync(outPath, png);
} catch (err) {
  fail(`cannot write ${outPath}: ${String(err)}`);
}

const written = readFileSync(outPath);
if (written.length !== png.length || !written.equals(png)) {
  fail("output does not match entry.png byte-for-byte");
}

console.log(`Wrote ${outPath} (${written.length} bytes, verified byte-for-byte)`);
