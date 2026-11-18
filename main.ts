import { copyFileSync, statSync } from "node:fs";
import { join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = join(import.meta.dirname, "entry.png");
const dst = join(outDir, "entry.png");
copyFileSync(src, dst);
if (statSync(src).size !== statSync(dst).size) {
  throw new Error("entry.png copy size mismatch");
}
