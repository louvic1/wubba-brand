// Screenshots of every page at desktop and mobile widths, for review.
// node tools/shoot.mjs [outDir] [pages...]
import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import { playwright as loadPlaywright, launchOptions } from "./browser.mjs";
import { serve } from "./serve.mjs";


const out = process.argv[2] || "tests/shots";
const only = process.argv.slice(3);
const PAGES = ["/", "/series", "/offer", "/about", "/brief", "/privacy", "/nope"];
const SIZES = { desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } };

await mkdir(out, { recursive: true });
const { server, url } = await serve("dist");
const browser = await loadPlaywright().chromium.launch(launchOptions());
for (const [name, viewport] of Object.entries(SIZES)) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: name === "mobile" ? 2 : 1, reducedMotion: "reduce" });
  const page = await context.newPage();
  for (const path of only.length ? only : PAGES) {
    await page.goto(url + path, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    const slug = path === "/" ? "home" : path.slice(1);
    await page.screenshot({ path: join(out, `${slug}-${name}.png`), fullPage: true });
    await page.screenshot({ path: join(out, `${slug}-${name}-fold.png`) });
  }
  await context.close();
}
await browser.close();
server.close();
console.log("shots in", out);
