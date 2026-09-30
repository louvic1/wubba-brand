// The social card (1200x630) shown when wubba.studio is shared in a message or a post.
// The proof leads: 98.8M with the green point, then what it counts, then who we are.
// node tools/og.mjs   -> src/assets/img/og.png  (then rebuild)
import { readFile } from "node:fs/promises";
import { playwright as loadPlaywright, launchOptions } from "./browser.mjs";
import { serve } from "./serve.mjs";

const mark = await readFile("src/partials/logo-wordmark.svg", "utf8");
const html = `<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/css/site.css">
<style>
  html, body { margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #000; }
  .og { box-sizing: border-box; width: 1200px; height: 630px; padding: 56px 64px 52px; display: grid; grid-template-rows: auto 1fr auto auto; }
  .og__top { display: flex; justify-content: space-between; align-items: center; }
  .og .wordmark { width: 168px; color: #fff; }
  .og__top span { font: 500 20px/1 var(--mono); color: #8f8f8f; }
  .og__num { align-self: end; margin: 0 0 0 -0.035em; font: 700 350px/0.78 var(--display); letter-spacing: -0.04em; color: #fff; white-space: nowrap; }
  .og__cap { margin: 22px 0 0; padding-top: 16px; border-top: 1px solid #3a3a3a; display: flex; justify-content: space-between; gap: 24px; font: 500 22px/1.2 var(--mono); color: #b9b9b9; }
  .og__line { margin: 22px 0 0; font: 600 27px/1.25 var(--display); letter-spacing: -0.015em; color: #fff; }
</style></head><body><div class="og">
<div class="og__top">${mark}<span>wubba.studio</span></div>
<p class="og__num">98<span class="point">.</span>8M</p>
<p class="og__cap"><span>views across the series and its reposts</span><span>X, Instagram &amp; YouTube</span></p>
<p class="og__line">We build AI streamers who test gaming gear where it has no business working.</p>
</div></body></html>`;

const { server, url } = await serve("src");
const browser = await loadPlaywright().chromium.launch(launchOptions());
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.route(`${url}/_og.html`, (route) => route.fulfill({ status: 200, contentType: "text/html", body: html }));
await page.goto(`${url}/_og.html`, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
// the figure's glyphs, not its box (the box is widened by the optical negative margin)
const fits = await page.evaluate(() => {
  const range = document.createRange();
  range.selectNodeContents(document.querySelector(".og__num"));
  const r = range.getBoundingClientRect();
  return document.querySelector(".og").scrollHeight <= 630 && r.left >= 40 && r.right <= 1160;
});
if (!fits) throw new Error("the social card overflows");
await page.screenshot({ path: "src/assets/img/og.png" });
await browser.close();
server.close();
console.log("wrote src/assets/img/og.png");
