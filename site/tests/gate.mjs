// The gate: a mechanical pass/fail check of the built site (loop engineering, step 4a).
// It serves dist/ like Vercel would, drives Chromium through every page and viewport,
// and exits 1 on any failure. Run: node tests/gate.mjs   (after node build.mjs)

import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { playwright as loadPlaywright, launchOptions } from "../tools/browser.mjs";
import { serve } from "../tools/serve.mjs";

const AXE = await readFile(new URL("../node_modules/axe-core/axe.min.js", import.meta.url), "utf8");

const PAGES = ["/", "/series", "/offer", "/about", "/brief", "/privacy", "/does-not-exist"];
const VIEWPORTS = [
  [360, 740],
  [390, 844],
  [768, 1024],
  [1024, 768],
  [1440, 900],
  [1920, 1080],
];

const failures = [];
const warnings = [];
const fail = (where, what) => failures.push(`${where}: ${what}`);
const warn = (where, what) => warnings.push(`${where}: ${what}`);

const { server, url } = await serve("dist");
const browser = await loadPlaywright().chromium.launch(launchOptions());

async function open(context, path, where) {
  const page = await context.newPage();
  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    if (path === "/does-not-exist" && msg.text().includes("404")) return; // the 404 page itself
    fail(where, `console error: ${msg.text()}`);
  });
  page.on("pageerror", (error) => fail(where, `page error: ${error.message}`));
  page.on("requestfailed", (req) => {
    if (!req.url().startsWith("mailto:")) fail(where, `request failed: ${req.url()} ${req.failure()?.errorText}`);
  });
  page.on("response", (res) => {
    const isPage = res.url() === url + path;
    if (res.status() >= 400 && !(isPage && path === "/does-not-exist")) fail(where, `HTTP ${res.status()} for ${res.url()}`);
  });
  const response = await page.goto(url + path, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  return { page, response };
}

// ------------------------------------------------------------------ every page, every viewport

for (const [width, height] of VIEWPORTS) {
  const context = await browser.newContext({ viewport: { width, height }, reducedMotion: "reduce" });
  for (const path of PAGES) {
    const where = `${path} @${width}`;
    const { page, response } = await open(context, path, where);

    if (path === "/does-not-exist" && response.status() !== 404) fail(where, `expected 404, got ${response.status()}`);

    const overflow = await page.evaluate(() => {
      const doc = document.documentElement;
      if (doc.scrollWidth <= window.innerWidth + 1) return null;
      const culprits = [...document.querySelectorAll("body *")]
        .filter((el) => el.getBoundingClientRect().right > window.innerWidth + 1 && getComputedStyle(el).position !== "fixed")
        .slice(0, 4)
        .map((el) => `${el.tagName.toLowerCase()}.${[...el.classList].join(".")}`);
      return `${doc.scrollWidth}px wide: ${culprits.join(", ")}`;
    });
    if (overflow) fail(where, `horizontal overflow, ${overflow}`);

    // buttons must not wrap onto two lines
    const wrapped = await page.evaluate(() =>
      [...document.querySelectorAll(".btn")]
        .filter((b) => b.offsetParent && b.getBoundingClientRect().height > 64)
        .map((b) => b.textContent.trim()),
    );
    if (wrapped.length) fail(where, `button text wraps: ${wrapped.join(" | ")}`);

    // touch targets (WCAG 2.2, 2.5.8): 24px minimum for controls outside running text
    const small = await page.evaluate(() =>
      [...document.querySelectorAll("button, .btn, .chip span, .bar__nav a, .foot__list a, .foot__base a, .link-ext, input:not(.chip input), textarea")]
        .filter((el) => el.offsetParent)
        .map((el) => [el, el.getBoundingClientRect()])
        .filter(([, r]) => r.width > 0 && (r.width < 24 || r.height < 24))
        .map(([el, r]) => `${el.tagName.toLowerCase()}.${[...el.classList].join(".")} ${Math.round(r.width)}x${Math.round(r.height)}`),
    );
    if (small.length) fail(where, `targets under 24px: ${small.join(", ")}`);

    if (width === 390 || width === 1440) {
      // content must be visible with reduced motion
      const hidden = await page.evaluate(() =>
        [...document.querySelectorAll("main h1, main h2, main p, main .btn, .figure__num .g")]
          .filter((el) => el.offsetParent && !el.closest(".sr-only") && Number(getComputedStyle(el).opacity) < 0.99)
          .map((el) => el.textContent.trim().slice(0, 40)),
      );
      if (hidden.length) fail(where, `invisible with reduced motion: ${hidden.join(" | ")}`);

      await page.addScriptTag({ content: AXE });
      const result = await page.evaluate(async () =>
        axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"] } }),
      );
      for (const v of result.violations) {
        const text = `axe ${v.id} (${v.impact}): ${v.help} [${v.nodes
          .slice(0, 3)
          .map((n) => n.target.join(" "))
          .join(", ")}]`;
        if (v.impact === "serious" || v.impact === "critical") fail(where, text);
        else warn(where, text);
      }
    }

    if (width === 1440) {
      const checks = await page.evaluate(() => {
        const out = [];
        const text = document.body.innerText;
        if (/[—–]/.test(text)) out.push("an em or en dash is visible");
        const h1 = document.querySelectorAll("h1").length;
        if (h1 !== 1) out.push(`${h1} h1 elements`);
        let last = 0;
        for (const h of document.querySelectorAll("h1, h2, h3, h4")) {
          const level = Number(h.tagName[1]);
          if (last && level > last + 1) out.push(`heading jumps from h${last} to h${level}: "${h.textContent.trim().slice(0, 40)}"`);
          last = level;
        }
        if (document.documentElement.lang !== "en") out.push("html lang is not en");
        for (const sel of ['meta[name="description"]', 'link[rel="canonical"]', 'meta[property="og:image"]', 'link[rel="icon"]']) {
          if (!document.querySelector(sel)) out.push(`missing ${sel}`);
        }
        if (!document.title || document.title.length > 90) out.push(`title "${document.title}"`);
        const first = document.querySelector("a, button, input, textarea");
        if (!first?.classList.contains("skip")) out.push("the skip link is not the first focusable element");
        return out;
      });
      checks.forEach((c) => fail(where, c));

      const source = await (await fetch(url + path)).text();
      if (/\{\{|\}\}/.test(source)) fail(where, "a template tag leaked into the page");

      // every internal link resolves, anchors included
      const links = await page.evaluate(() =>
        [...new Set([...document.querySelectorAll("a[href]")].map((a) => a.getAttribute("href")))].filter(
          (h) => h.startsWith("/") || h.startsWith("#"),
        ),
      );
      for (const href of links) {
        const [target, anchor] = href.split("#");
        if (!target) {
          if (!(await page.evaluate((id) => !!document.getElementById(id), anchor))) fail(where, `anchor #${anchor} is missing`);
          continue;
        }
        const res = await fetch(url + (target || path));
        const ok = res.status === 200 || (target === "/does-not-exist" && res.status === 404);
        if (!ok) fail(where, `link ${href} returns ${res.status}`);
        if (anchor) {
          const body = await res.text();
          if (!body.includes(`id="${anchor}"`)) fail(where, `link ${href} points to a missing anchor`);
        }
      }
    }
    await page.close();
  }
  await context.close();
}

// ------------------------------------------------------------------ behaviour

{
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, permissions: ["clipboard-read", "clipboard-write"] });
  const where = "behaviour @1440";
  const { page } = await open(context, "/", where);

  // entrance motion must finish with everything visible
  await page.waitForTimeout(2200);
  const stuck = await page.evaluate(() =>
    [...document.querySelectorAll(".figure__num .g, .figure__num .point, .hero__title, .hero__actions, .figure__cap .cell")]
      .filter((el) => Number(getComputedStyle(el).opacity) < 0.99)
      .map((el) => el.className),
  );
  if (stuck.length) fail(where, `entrance motion left elements hidden: ${stuck.join(", ")}`);

  // builder: chips drive the sentence, the idea lands in the brief
  await page.click('label.chip:has(input[value="keyboard"])');
  await page.click('label.chip:has(input[value="cockpit"])');
  await page.waitForTimeout(450);
  const idea = await page.textContent("[data-idea]");
  if (!idea.includes("keyboard") || !idea.includes("in a cockpit")) fail(where, `idea line reads "${idea}"`);
  await page.click("[data-use-idea]");
  const brief = await page.inputValue("[data-message]");
  if (!brief.startsWith("Idea: an AI streamer tests our keyboard in a cockpit.")) fail(where, `brief after "add" reads "${brief.slice(0, 80)}"`);
  const counter = await page.textContent("[data-count]");
  if (!counter.startsWith(String(brief.length))) fail(where, `counter reads "${counter}" for ${brief.length} characters`);
  await page.click("[data-shuffle]");
  await page.waitForTimeout(450);
  const shuffled = await page.textContent("[data-idea]");
  if (shuffled === idea) fail(where, "shuffle did not change the idea");

  // form: empty submit shows both errors and focuses the email field
  await page.fill("[data-message]", "");
  await page.click('[data-form] button[type="submit"]');
  const errors = await page.evaluate(() => ({
    fields: [...document.querySelectorAll("[data-field].is-error")].length,
    invalid: [...document.querySelectorAll('[aria-invalid="true"]')].length,
    focus: document.activeElement?.id,
  }));
  if (errors.fields !== 2 || errors.invalid !== 2) fail(where, `empty submit: ${JSON.stringify(errors)}`);
  if (errors.focus !== "f-email") fail(where, `empty submit focuses ${errors.focus}`);
  await page.fill("#f-email", "name@brand");
  await page.click('[data-form] button[type="submit"]');
  const emailError = await page.textContent("#f-email-err");
  if (!emailError.includes("incomplete")) fail(where, `bad email shows "${emailError}"`);
  await page.fill("#f-email", "name@brand.com");
  await page.fill("[data-message]", "A headset launching in March. We need paid cuts for Meta.");
  const cleared = await page.evaluate(() => document.querySelectorAll("[data-field].is-error").length);
  if (cleared) fail(where, "errors stay after the fields are corrected");
  await page.click('[data-form] button[type="submit"]');
  await page.waitForTimeout(200);
  const sent = await page.evaluate(() => ({
    sent: document.querySelector("[data-form]").classList.contains("is-sent"),
    title: document.querySelector("[data-status-title]").textContent,
  }));
  if (!sent.sent || !sent.title.includes("email app")) fail(where, `valid submit: ${JSON.stringify(sent)}`);

  // copy the address
  await page.click("[data-copy]");
  await page.waitForTimeout(400);
  const label = await page.textContent("[data-copy-label]");
  if (label.trim() !== "Copied") fail(where, `copy button reads "${label}"`);
  const clip = await page.evaluate(() => navigator.clipboard.readText());
  if (clip !== "contact@wubba.studio") fail(where, `clipboard holds "${clip}"`);
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const where = "menu @390";
  const { page } = await open(context, "/offer", where);
  await page.click("[data-menu-toggle]");
  await page.waitForTimeout(350);
  const opened = await page.evaluate(() => ({
    open: document.querySelector("[data-menu]").classList.contains("is-open"),
    expanded: document.querySelector("[data-menu-toggle]").getAttribute("aria-expanded"),
    mainInert: document.querySelector("main").inert,
    focus: document.activeElement?.textContent.trim(),
    current: document.querySelector('[data-menu] a[aria-current="page"]')?.textContent.trim(),
  }));
  if (!opened.open || opened.expanded !== "true" || !opened.mainInert) fail(where, `open state ${JSON.stringify(opened)}`);
  if (opened.focus !== "Home") fail(where, `focus goes to "${opened.focus}" when the menu opens`);
  if (opened.current !== "The offer") fail(where, `current page in menu is "${opened.current}"`);
  for (let i = 0; i < 8; i++) await page.keyboard.press("Tab");
  const inside = await page.evaluate(() => !!document.activeElement.closest("[data-menu], [data-menu-toggle]"));
  if (!inside) fail(where, "focus escapes the open menu");
  await page.keyboard.press("Escape");
  await page.waitForTimeout(250);
  const closed = await page.evaluate(() => ({
    open: document.querySelector("[data-menu]").classList.contains("is-open"),
    focusOnToggle: document.activeElement === document.querySelector("[data-menu-toggle]"),
    mainInert: document.querySelector("main").inert,
  }));
  if (closed.open || !closed.focusOnToggle || closed.mainInert) fail(where, `after Escape ${JSON.stringify(closed)}`);
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const where = "prefill /brief?product=monitor&place=desert";
  const { page } = await open(context, "/brief?product=monitor&place=desert", where);
  const idea = await page.textContent("[data-idea]");
  if (!idea.includes("monitor") || !idea.includes("in the desert")) fail(where, `idea reads "${idea}"`);
  await context.close();
}

// ------------------------------------------------------------------ weight and the preview build

{
  const files = ["index.html", "assets/css/site.css", "assets/js/site.js", "assets/fonts/sora.woff2", "assets/fonts/figtree.woff2", "assets/fonts/jetbrains-mono.woff2"];
  let bytes = 0;
  for (const f of files) bytes += (await readFile(join("dist", f))).length;
  if (bytes > 320 * 1024) fail("weight", `home page payload ${Math.round(bytes / 1024)} KB (budget 320 KB)`);
  else warn("weight", `home page payload ${Math.round(bytes / 1024)} KB`);

  for (const file of (await readdir("preview")).filter((f) => f.endsWith(".html"))) {
    const html = await readFile(join("preview", file), "utf8");
    for (const [, raw] of html.matchAll(/(?:href|src)="([^"]*)"/g)) {
      if (/^[a-z][a-z0-9+.-]*:/i.test(raw) || raw.startsWith("//") || raw.startsWith("#") || !raw) continue;
      const href = raw.split(/[?#]/)[0];
      try {
        await readFile(join("preview", href));
      } catch {
        fail(`preview/${file}`, `broken link ${href}`);
      }
    }
  }
}

await browser.close();
server.close();

for (const w of warnings) console.log(`warn  ${w}`);
for (const f of failures) console.log(`FAIL  ${f}`);
console.log(failures.length ? `\ngate: RED, ${failures.length} failure(s)` : `\ngate: GREEN (${warnings.length} warning(s))`);
process.exit(failures.length ? 1 : 0);
