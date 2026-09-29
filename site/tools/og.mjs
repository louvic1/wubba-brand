// The social card (1200x630) shown when wubba.studio is shared.
// node tools/og.mjs   -> src/assets/img/og.png
import { readFile, writeFile } from "node:fs/promises";
import { playwright as loadPlaywright, launchOptions } from "./browser.mjs";
import { serve } from "./serve.mjs";


const mark = await readFile("src/partials/logo-wordmark.svg", "utf8");
const html = `<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/css/site.css">
<style>
  html, body { margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #000; }
  .og { position: relative; box-sizing: border-box; width: 1200px; height: 630px; padding: 64px 72px; display: grid; grid-template-rows: auto 1fr auto; }
  .og .wordmark { width: 230px; color: #fff; }
  .og h1 { align-self: center; margin: 0; font: 700 64px/1.04 var(--display); letter-spacing: -0.035em; color: #fff; max-width: 17em; text-wrap: balance; }
  .og p { margin: 0; display: flex; justify-content: space-between; font: 500 22px/1 var(--mono); color: #8f8f8f; }
</style></head><body><div class="og">${mark}
<h1>We build AI streamers who test gaming gear where it has no business working.</h1>
<p><span>wubba.studio</span><span>@wubbastudio</span></p></div></body></html>`;
await writeFile("dist/_og.html", html);
const { server, url } = await serve("dist");
const browser = await loadPlaywright().chromium.launch(launchOptions());
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.goto(url + "/_og.html", { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: "src/assets/img/og.png" });
await browser.close();
server.close();
console.log("wrote src/assets/img/og.png");
