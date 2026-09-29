// Rendu HTML -> PNG au pixel près avec Chromium (Playwright).
// node render.mjs page.html sortie.png largeur hauteur [échelle] [transparent]
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require("playwright");
} catch {
  playwright = require("/opt/node22/lib/node_modules/playwright");
}

const [input, output, w, h, scale = "1", transparent = "0"] = process.argv.slice(2);
const browser = await playwright.chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
});
const auto = h === "auto";
const page = await browser.newPage({
  viewport: { width: Number(w), height: auto ? 1000 : Number(h) },
  deviceScaleFactor: Number(scale),
});
await page.goto(pathToFileURL(resolve(input)).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: output, omitBackground: transparent === "1", fullPage: auto });
await browser.close();
console.log(`wrote ${output} ${w}x${h} @${scale}x`);
