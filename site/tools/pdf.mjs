// Prints the home page (print stylesheet) to the one-sheet PDF offered in the footer.
// node tools/pdf.mjs   -> src/static/wubba-one-sheet.pdf  (then rebuild)
import { playwright as loadPlaywright, launchOptions } from "./browser.mjs";
import { serve } from "./serve.mjs";


const { server, url } = await serve("dist");
const browser = await loadPlaywright().chromium.launch(launchOptions());
const page = await browser.newPage({ viewport: { width: 1200, height: 1600 } });
await page.emulateMedia({ media: "print", reducedMotion: "reduce" });
await page.goto(url + "/", { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.pdf({ path: "src/static/wubba-one-sheet.pdf", format: "A4", printBackground: true, preferCSSPageSize: true });
await page.screenshot({ path: "tests/shots/print-preview.png", fullPage: true });
await browser.close();
server.close();
console.log("wrote src/static/wubba-one-sheet.pdf");
