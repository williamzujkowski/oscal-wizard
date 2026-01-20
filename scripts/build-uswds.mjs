import { copyFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const repoRoot = path.resolve(__dirname, "..");
const distDir = path.join(repoRoot, "node_modules", "@uswds", "uswds", "dist");
const targetDir = path.join(repoRoot, "web", "static", "uswds");

const assets = ["uswds.min.css", "uswds.min.js"];

await mkdir(targetDir, { recursive: true });

await Promise.all(
  assets.map(async (asset) => {
    const src = path.join(distDir, asset);
    const dest = path.join(targetDir, asset);
    await copyFile(src, dest);
  })
);

console.log("USWDS assets copied to web/static/uswds");
