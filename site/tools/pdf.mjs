// Prints the home page (print stylesheet) to the one-sheet PDF offered in the footer.
// node tools/pdf.mjs   -> src/static/wubba-one-sheet.pdf  (run after a build; rebuild afterwards)
// The file's dates are pinned so the PDF only changes when the page does.
import { writeFile } from "node:fs/promises";
import { playwright as loadPlaywright, launchOptions } from "./browser.mjs";
import { serve } from "./serve.mjs";

const { server, url } = await serve("dist");
const browser = await loadPlaywright().chromium.launch(launchOptions());
const page = await browser.newPage({ viewport: { width: 1200, height: 1600 } });
await page.emulateMedia({ media: "print", reducedMotion: "reduce" });
await page.goto(url + "/", { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
const pdf = Buffer.from(await page.pdf({ format: "A4", printBackground: true, preferCSSPageSize: true }));
const pages = (pdf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
if (pages !== 1) throw new Error(`the one-sheet runs to ${pages} pages`);
// same length, fixed value: the byte offsets inside the PDF stay valid
const pinned = Buffer.from(
  pdf.toString("latin1").replace(/\/(CreationDate|ModDate) \(D:\d{14}/g, (_, key) => `/${key} (D:20260901000000`),
  "latin1",
);
if (pinned.length !== pdf.length) throw new Error("pinning the PDF dates changed its length");
await writeFile("src/static/wubba-one-sheet.pdf", pinned);
await page.screenshot({ path: "tests/shots/print-preview.png", fullPage: true });
await browser.close();
server.close();
console.log("wrote src/static/wubba-one-sheet.pdf (1 page)");
