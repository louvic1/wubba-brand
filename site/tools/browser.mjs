// One place to find Playwright and a Chromium binary, in the cloud container or on a laptop.
import { createRequire } from "node:module";
import { existsSync } from "node:fs";

const require = createRequire(import.meta.url);
const CLOUD_CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

export function playwright() {
  try {
    return require("playwright");
  } catch {
    return require("/opt/node22/lib/node_modules/playwright");
  }
}

export function launchOptions() {
  const executablePath = process.env.CHROMIUM_PATH || (existsSync(CLOUD_CHROMIUM) ? CLOUD_CHROMIUM : undefined);
  return executablePath ? { executablePath } : {};
}
