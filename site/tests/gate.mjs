// The gate: a mechanical pass/fail check of the built site (loop engineering, step 4a).
// It serves dist/ like Vercel would, drives Chromium through every page and viewport,
// and exits 1 on any failure. Run: node tests/gate.mjs   (after node build.mjs)

import { readFile, readdir, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { playwright as loadPlaywright, launchOptions } from "../tools/browser.mjs";
import { serve } from "../tools/serve.mjs";

const AXE = await readFile(new URL("../node_modules/axe-core/axe.min.js", import.meta.url), "utf8");

const PAGES = ["/", "/series", "/offer", "/about", "/brief", "/privacy", "/does-not-exist"];
const VIEWPORTS = [
  [360, 740],
  [390, 844],
  [600, 900],
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

// expected: requests a test fails on purpose (an endpoint answering 500, for instance)
async function open(context, path, where, expected = null) {
  const page = await context.newPage();
  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    if (path === "/does-not-exist" && msg.text().includes("404")) return; // the 404 page itself
    if (expected?.test(msg.location()?.url ?? "")) return;
    fail(where, `console error: ${msg.text()}`);
  });
  page.on("pageerror", (error) => fail(where, `page error: ${error.message}`));
  page.on("requestfailed", (req) => {
    if (!/^(mailto:|https:\/\/mail\.google\.com)/.test(req.url())) fail(where, `request failed: ${req.url()} ${req.failure()?.errorText}`);
  });
  page.on("response", (res) => {
    const isPage = res.url() === url + path;
    if (expected?.test(res.url())) return;
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

    if (width === VIEWPORTS[0][0]) {
      const copy = await page.locator("body").innerText();
      if (/\b(?:call|calls|phone|meeting)\b|\b(?:1:1|16:9)\b/i.test(copy)) fail(where, "page text mentions a call or an obsolete aspect ratio");
    }

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
      [...document.querySelectorAll("button, .btn, .chip span, .bar__nav a, .foot__list a, .foot__base a, .link-ext, .disc-band__try, input:not(.chip input), textarea")]
        .filter((el) => el.offsetParent)
        .map((el) => [el, el.getBoundingClientRect()])
        .filter(([, r]) => r.width > 0 && (r.width < 24 || r.height < 24))
        .map(([el, r]) => `${el.tagName.toLowerCase()}.${[...el.classList].join(".")} ${Math.round(r.width)}x${Math.round(r.height)}`),
    );
    if (small.length) fail(where, `targets under 24px: ${small.join(", ")}`);

    // one green action per screen: at the top of the page, and wherever a primary action is in view
    await page.waitForTimeout(80);
    // counted by what is painted, not by class: the bar's button stays a .btn--green while it shows as an outline
    const greens = async () =>
      page.evaluate(() =>
        [...document.querySelectorAll(".btn")]
          .filter((b) => {
            const r = b.getBoundingClientRect();
            const style = getComputedStyle(b);
            const green = style.backgroundColor === "rgb(114, 172, 14)" || style.backgroundColor === "rgb(134, 198, 28)";
            return green && b.offsetParent && style.visibility === "visible" && Number(style.opacity) > 0.5 && r.bottom > 0 && r.top < innerHeight;
          })
          .map((b) => b.textContent.trim()),
      );
    const topGreens = await greens();
    if (topGreens.length > 1) fail(where, `${topGreens.length} green buttons on the first screen: ${topGreens.join(" | ")}`);
    for (const selector of ["[data-form]", ".disc-band"]) {
      if (!(await page.$(selector))) continue;
      await page.evaluate((s) => document.querySelector(s).scrollIntoView({ block: "center" }), selector);
      await page.waitForTimeout(80);
      const seen = await greens();
      if (seen.length > 1) fail(where, `${seen.length} green buttons around ${selector}: ${seen.join(" | ")}`);
    }
    await page.evaluate(() => scrollTo(0, 0));

    // the closing band: black type sits on the disc, white type stays off it, and the crop is decisive:
    // exactly half at the bottom, and either a clear margin or the same clear bleed on both sides
    const band = await page.evaluate(() => {
      const disc = document.querySelector(".disc-band__disc");
      if (!disc) return null;
      const d = disc.getBoundingClientRect();
      const b = document.querySelector(".disc-band").getBoundingClientRect();
      const cx = d.left + d.width / 2;
      const cy = d.top + d.height / 2;
      const r = d.width / 2;
      const dist = (x, y) => Math.hypot(x - cx, y - cy);
      const out = [];
      // the button and the idea sit on the disc; the heading stays on black above it
      for (const el of document.querySelectorAll(".disc-band__acts > *, .disc-band__h")) {
        const black = !!el.closest(".disc-band__acts");
        const range = document.createRange();
        range.selectNodeContents(el);
        const rects = [...range.getClientRects()].filter((q) => q.width > 1);
        if (el.classList.contains("btn")) rects.push(el.getBoundingClientRect());
        for (const q of rects) {
          const corners = [[q.left, q.top], [q.right, q.top], [q.left, q.bottom], [q.right, q.bottom]];
          const bad = black ? corners.some(([x, y]) => dist(x, y) > r - 6) : corners.some(([x, y]) => dist(x, y) < r + 4);
          if (bad) {
            out.push(`${black ? "off" : "on"} the disc: "${el.textContent.trim().slice(0, 30)}"`);
            break;
          }
        }
      }
      const left = b.left - d.left;
      const right = d.right - b.right;
      const width = b.width;
      if (Math.abs(cy - b.bottom) > 1.5) out.push(`disc centre ${Math.round(cy - b.bottom)}px off the band's bottom edge`);
      if (Math.abs(left - right) > 2) out.push(`uneven crop: ${Math.round(left)}px left, ${Math.round(right)}px right`);
      const margin = -left;
      if (margin >= 0 ? margin < width * 0.07 : -margin < d.width * 0.08) out.push(`indecisive crop: ${Math.round(margin)}px at the sides`);
      return out;
    });
    if (band?.length) fail(where, `closing band: ${band.join(", ")}`);

    if (width === 390 || width === 1440) {
      // content must be visible with reduced motion
      const hidden = await page.evaluate(() =>
        [...document.querySelectorAll("main h1, main h2, main p, main .btn, .figure__num .g")]
          .filter((el) => el.offsetParent && !el.closest(".sr-only") && Number(getComputedStyle(el).opacity) < 0.99)
          .map((el) => el.textContent.trim().slice(0, 40)),
      );
      if (hidden.length) fail(where, `invisible with reduced motion: ${hidden.join(" | ")}`);

      // borders that show where to type or tap need 3:1 against the page (WCAG 1.4.11)
      const faint = await page.evaluate(() => {
        const lum = (rgb) => {
          const [r, g, b] = rgb.match(/\d+(\.\d+)?/g).slice(0, 3).map((v) => {
            const c = Number(v) / 255;
            return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
          });
          return 0.2126 * r + 0.7152 * g + 0.0722 * b;
        };
        return [...document.querySelectorAll(".field__box, .builder__other input, .chip input:not(:checked) + span, .btn--line, .copy, .mail")]
          .filter((el) => el.offsetParent)
          .map((el) => [el, (lum(getComputedStyle(el).borderTopColor) + 0.05) / 0.05])
          .filter(([, ratio]) => ratio < 3)
          .map(([el, ratio]) => `${el.className} ${ratio.toFixed(2)}:1`);
      });
      if (faint.length) fail(where, `UI borders under 3:1: ${[...new Set(faint)].slice(0, 4).join(", ")}`);

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
      const checks = await page.evaluate((lost) => {
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
        const required = ['meta[name="description"]', 'meta[property="og:image"]', 'link[rel="icon"]'];
        required.push(lost ? 'meta[name="robots"][content="noindex"]' : 'link[rel="canonical"]');
        for (const sel of required) if (!document.querySelector(sel)) out.push(`missing ${sel}`);
        if (lost && document.querySelector('link[rel="canonical"]')) out.push("the 404 page declares a canonical URL");
        if (!document.title || document.title.length > 90) out.push(`title "${document.title}"`);
        const first = document.querySelector("a, button, input, textarea");
        if (!first?.classList.contains("skip")) out.push("the skip link is not the first focusable element");
        return out;
      }, path === "/does-not-exist");
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
        const res = await fetch(url + target);
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

// the builder's three custom fields stay fully visible at phone, tablet and desktop widths
for (const width of [360, 390, 768, 1024, 1440]) {
  for (const path of ["/", "/brief"]) {
    const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: "reduce" });
    const where = `builder custom fields ${path} @${width}`;
    const { page } = await open(context, path, where);
    for (const [name, text] of [["product", "a standing desk"], ["place", "inside a volcano"], ["game", "Valorant"]]) {
      await page.click(`label.chip:has(input[name="${name}"][value="other"])`);
      await page.fill(`#b-${name}`, text);
    }
    const fields = await page.evaluate(() => ({
      width: document.documentElement.scrollWidth,
      viewport: innerWidth,
      fields: [...document.querySelectorAll(".builder__other input")].map((el) => {
        const rect = el.getBoundingClientRect();
        return {
          id: el.id,
          hidden: el.closest("[data-other]").hidden,
          left: rect.left,
          right: rect.right,
          width: rect.width,
          height: rect.height,
          border: getComputedStyle(el).borderTopColor,
          background: getComputedStyle(document.body).backgroundColor,
        };
      }),
    }));
    if (fields.width > fields.viewport + 1) fail(where, `horizontal overflow ${fields.width}px`);
    for (const field of fields.fields) {
      if (field.hidden || field.left < 0 || field.right > fields.viewport + 1) fail(where, `${field.id} is hidden or cut off (${field.left} to ${field.right})`);
      if (field.width < 24 || field.height < 24) fail(where, `${field.id} target is ${field.width}x${field.height}`);
      if (field.border !== "rgb(107, 107, 107)" || field.background !== "rgb(0, 0, 0)") fail(where, `${field.id} does not use the contrast-tested input border`);
    }
    await context.close();
  }
}

// the offer shows one vertical frame repeated three times at phone, tablet and desktop widths
for (const width of [360, 768, 1440]) {
  const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: "reduce" });
  const where = `format frames @${width}`;
  const { page } = await open(context, "/offer", where);
  const frames = await page.locator(".formats__frames .frame").evaluateAll((els) => els.map((el) => {
    const rect = el.getBoundingClientRect();
    return { width: rect.width, height: rect.height, left: rect.left, right: rect.right };
  }));
  if (frames.length !== 3 || frames.some((frame) => frame.right > width + 1)) fail(where, "the three frames are missing or cut off");
  if (frames.some((frame) => Math.abs(frame.width - frames[0].width) > 1 || Math.abs(frame.height - frames[0].height) > 1)) fail(where, "the 9:16 frames are not the same size");
  if (frames.some((frame) => Math.abs(frame.width / frame.height - 9 / 16) > 0.02)) fail(where, "a format frame is not 9:16");
  await context.close();
}

// ------------------------------------------------------------------ the first screen tells the whole hook

// real browser windows: laptops with their toolbars, phones upright, phones on their side
for (const [width, height] of [
  [1280, 609],
  [1366, 657],
  [1440, 789],
  [1536, 730],
  [1024, 672],
  [1024, 600],
  [1920, 969],
  [390, 664],
  [375, 553],
  [844, 390],
  [926, 428],
  [812, 375],
  [740, 360],
  [667, 375],
]) {
  const context = await browser.newContext({ viewport: { width, height }, reducedMotion: "reduce" });
  const where = `fold @${width}x${height}`;
  const { page } = await open(context, "/", where);
  const fold = await page.evaluate(() => {
    const bottom = (s) => document.querySelector(s).getBoundingClientRect().bottom;
    const title = parseFloat(getComputedStyle(document.querySelector(".hero__title")).fontSize);
    const h2 = parseFloat(getComputedStyle(document.querySelector("main .h2")).fontSize);
    const bar = getComputedStyle(document.querySelector(".bar__cta")).backgroundColor === "rgb(114, 172, 14)";
    // the figure's glyphs against the column it sits in, and that column against the page grid
    const glyphs = document.createRange();
    glyphs.selectNodeContents(document.querySelector(".figure__num"));
    const figure = document.querySelector(".figure").getBoundingClientRect().width;
    const hero = document.querySelector(".hero");
    const style = getComputedStyle(hero);
    const grid = hero.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
    return { twist: bottom(".hero__twist"), actions: bottom(".hero__actions"), bar, title, h2, span: glyphs.getBoundingClientRect().width / figure, column: figure / grid };
  });
  if (fold.span < 0.7 || fold.column < 0.45) fail(where, `98.8M spans ${Math.round(fold.span * 100)}% of a column ${Math.round(fold.column * 100)}% of the grid`);
  if (fold.twist > height) fail(where, `"The guy in it doesn't exist." ends at ${Math.round(fold.twist)}px, below the fold`);
  if (fold.actions > height && !fold.bar) fail(where, "no green action on the first screen");
  if (fold.actions <= height && fold.bar) fail(where, "two green actions on the first screen");
  if (width >= 1280 && fold.title < fold.h2 * 0.95) fail(where, `the headline (${fold.title}px) is smaller than the section headings (${fold.h2}px)`);
  await context.close();
}

// ------------------------------------------------------------------ the first frame, motion on

{
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  for (const [path, folded] of [["/", true], ["/offer", true], ["/does-not-exist", true], ["/brief", true], ["/series", false], ["/about", false]]) {
    const where = `first frame ${path}`;
    const page = await context.newPage();
    await page.goto(url + path, { waitUntil: "commit" });
    await page.waitForSelector(".bar__cta", { state: "attached" });
    const state = await page.evaluate(() => {
      const cta = document.querySelector(".bar__cta");
      const style = getComputedStyle(cta);
      return { green: style.backgroundColor === "rgb(114, 172, 14)", visibility: style.visibility, width: Math.round(cta.getBoundingClientRect().width) };
    });
    if (folded && state.green) fail(where, `the bar's button is green before the page's own shows (${JSON.stringify(state)})`);
    if (!folded && !state.green) fail(where, "the bar's button is not green on a page without its own action");
    if (state.visibility !== "visible" || state.width < 80) fail(where, `the bar's button is not in place (${JSON.stringify(state)})`);
    await page.close();
  }
  await context.close();
}

// ------------------------------------------------------------------ reveals only ever draw in, motion on

// sampled every frame from the navigation's commit: the line never shrinks, the point never jumps up
for (const [path, width, height] of [["/series", 1440, 900], ["/", 2560, 1440]]) {
  const where = `reveal ${path} @${width}x${height}`;
  const context = await browser.newContext({ viewport: { width, height } });
  const page = await context.newPage();
  await page.addInitScript(() => {
    window.__reveal = [];
    const start = performance.now();
    const tick = () => {
      const point = document.querySelector(".card__point, .scene__point");
      const line = document.querySelector(".card__horizon") || document.querySelector(".scene__horizon");
      if (point && line) {
        const lineBox = line.getBoundingClientRect();
        const drawn = line.classList.contains("card__horizon")
          ? lineBox.width
          : lineBox.width * new DOMMatrix(getComputedStyle(line, "::before").transform).a;
        window.__reveal.push({ lift: lineBox.top - point.getBoundingClientRect().bottom, drawn, full: lineBox.width, opacity: Number(getComputedStyle(point).opacity) });
      }
      if (performance.now() - start < 2600) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });
  await page.goto(url + path, { waitUntil: "commit" });
  await page.waitForTimeout(2900);
  const frames = await page.evaluate(() => window.__reveal);
  const jump = frames.findIndex((f, i) => i && f.opacity > 0.05 && f.lift > frames[i - 1].lift + 3);
  const shrink = frames.findIndex((f, i) => i && f.drawn < frames[i - 1].drawn - 1);
  const last = frames.at(-1);
  if (!frames.length) fail(where, "no frames sampled");
  else {
    if (jump > 0) fail(where, `the point jumps up ${Math.round(frames[jump].lift - frames[jump - 1].lift)}px after first paint`);
    if (shrink > 0) fail(where, "the horizon shrinks after first paint");
    if (last.drawn < last.full - 1 || last.lift > 3 || last.opacity < 0.99) fail(where, `the reveal does not finish (${JSON.stringify(last)})`);
  }
  await context.close();
}

// ------------------------------------------------------------------ behaviour

{
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, permissions: ["clipboard-read", "clipboard-write"] });
  const where = "behaviour @1440";
  const { page } = await open(context, "/", where);

  // entrance motion must finish with everything visible
  await page.waitForTimeout(2400);
  const stuck = await page.evaluate(() =>
    [...document.querySelectorAll(".figure__num .g, .figure__num .point, .hero__title, .hero__actions, .figure__cap .cell, .hero__twist")]
      .filter((el) => Number(getComputedStyle(el).opacity) < 0.99)
      .map((el) => el.className),
  );
  if (stuck.length) fail(where, `entrance motion left elements hidden: ${stuck.join(", ")}`);

  // the figure copies as the number it shows, once (a real copy: hidden screen-reader text stays out)
  await page.evaluate(() => {
    const range = document.createRange();
    range.setStartBefore(document.querySelector(".figure__num"));
    range.setEndAfter(document.querySelector(".cell__lead"));
    getSelection().removeAllRanges();
    getSelection().addRange(range);
  });
  await page.keyboard.press("ControlOrMeta+C");
  const copiedFigure = await page.evaluate(() => navigator.clipboard.readText());
  await page.evaluate(() => getSelection().removeAllRanges());
  if (!/^98\.8M\s+views across the series and its reposts/.test(copiedFigure)) fail(where, `the figure copies as "${copiedFigure.slice(0, 60)}"`);

  // ...and it is one piece of visible text: find-in-page lands on it, a triple click takes all of it
  const found = await page.evaluate(() => {
    getSelection().removeAllRanges();
    const hit = window.find("98.8M", false, false, false, false, false, false);
    const range = hit ? getSelection().getRangeAt(0).getBoundingClientRect() : null;
    const figure = document.querySelector(".figure__num").getBoundingClientRect();
    getSelection().removeAllRanges();
    return hit && range.width > figure.width * 0.8;
  });
  if (!found) fail(where, "find-in-page does not land on the visible 98.8M");
  const figureBox = await page.locator(".figure__num").boundingBox();
  await page.mouse.click(figureBox.x + figureBox.width * 0.3, figureBox.y + figureBox.height / 2, { clickCount: 3 });
  const tripled = await page.evaluate(() => getSelection().toString().trim());
  await page.evaluate(() => getSelection().removeAllRanges());
  if (tripled !== "98.8M") fail(where, `a triple click on the figure selects "${tripled}"`);

  // the bar's button is an outline while the hero's green action shows, green once it has scrolled
  // away, and it changes in place: the navigation never moves
  const barState = () =>
    page.evaluate(() => ({
      background: getComputedStyle(document.querySelector(".bar__cta")).backgroundColor,
      nav: Math.round(document.querySelector(".bar__nav").getBoundingClientRect().left),
    }));
  const barAtTop = await barState();
  await page.evaluate(() => document.querySelector(".pitch").scrollIntoView());
  await page.waitForTimeout(500);
  const barLater = await barState();
  if (barAtTop.background === "rgb(114, 172, 14)" || barLater.background !== "rgb(114, 172, 14)") fail(where, `bar button is ${barAtTop.background} at the top and ${barLater.background} further down`);
  if (barAtTop.nav !== barLater.nav) fail(where, `the navigation moves ${barLater.nav - barAtTop.nav}px when the bar's button changes`);

  // builder: presets drive all three slots and the idea lands in the brief
  await page.click('label.chip:has(input[value="keyboard"])');
  await page.click('label.chip:has(input[value="cockpit"])');
  await page.click('label.chip:has(input[value="chess"])');
  await page.waitForTimeout(450);
  const idea = await page.textContent("[data-idea]");
  if (!idea.includes("keyboard") || !idea.includes("in a cockpit") || !idea.includes("playing chess")) fail(where, `idea line reads "${idea}"`);
  await page.click("[data-use-idea]");
  const brief = await page.inputValue("[data-message]");
  if (!brief.startsWith("Idea: an AI streamer tests our keyboard in a cockpit, playing chess.")) fail(where, `brief after "add" reads "${brief.slice(0, 100)}"`);
  const counter = await page.textContent("[data-count]");
  if (!counter.startsWith(String(brief.length))) fail(where, `counter reads "${counter}" for ${brief.length} characters`);

  // custom choices appear on selection, take pointer focus, and update the line after a short pause
  const customCases = [
    ["product", "standing desk", "your standing desk"],
    ["place", "inside a volcano", "inside a volcano"],
    ["game", "Tetris", "Tetris"],
  ];
  for (const [name, typed, expected] of customCases) {
    await page.click(`label.chip:has(input[name="${name}"][value="other"])`);
    await page.waitForTimeout(20);
    const custom = page.locator(`#b-${name}`);
    if (!(await custom.isVisible()) || (await page.evaluate(() => document.activeElement?.id)) !== `b-${name}`) fail(where, `${name} custom field did not reveal with focus`);
    await custom.fill(typed);
    await page.waitForTimeout(350);
    const current = await page.textContent("[data-idea]");
    if (!current.includes(expected)) fail(where, `${name} custom value is missing from "${current}"`);
    const animated = await page.locator(`[data-slot="${name}"]`).evaluate((el) => el.classList.contains("is-exit") || el.classList.contains("is-enter-start"));
    if (animated) fail(where, `${name} custom text uses the swap animation`);
    if (name === "product") {
      await custom.fill("  standing   desk  ");
      await page.waitForTimeout(350);
      const normalized = await page.textContent("[data-idea]");
      if (!normalized.includes("your standing desk")) fail(where, `product whitespace was not normalized in "${normalized}"`);
    }
  }

  // arrowing onto the other radio reveals its field without moving radio focus
  await page.click('label.chip:has(input[name="product"][value="energy drink"])');
  await page.keyboard.press("ArrowRight");
  const keyboardOther = await page.evaluate(() => ({
    selected: document.querySelector('input[name="product"]:checked')?.value,
    focus: document.activeElement?.value,
    hidden: document.querySelector('[data-other="product"]').hidden,
  }));
  if (keyboardOther.selected !== "other" || keyboardOther.focus !== "other" || keyboardOther.hidden) fail(where, `keyboard selection moved focus or hid the field (${JSON.stringify(keyboardOther)})`);

  // an empty custom choice leaves the existing brief intact and returns focus to its field
  const fallbacks = { product: "your product", place: "somewhere it has no business working", game: "your community’s game" };
  const announcements = { product: "Type your product first.", place: "Type the place first.", game: "Type the game first." };
  for (const name of ["product", "place", "game"]) {
    for (const [group, value] of [["product", "headset"], ["place", "ocean"], ["game", "counter-strike-2"]]) {
      await page.click(`label.chip:has(input[name="${group}"][value="${value}"])`);
    }
    const before = await page.inputValue("[data-message]");
    await page.click(`label.chip:has(input[name="${name}"][value="other"])`);
    await page.waitForTimeout(20);
    await page.fill(`#b-${name}`, "");
    await page.waitForTimeout(350);
    const line = await page.textContent("[data-idea]");
    if (!line.includes(fallbacks[name])) fail(where, `empty ${name} does not use its fallback in "${line}"`);
    await page.click("[data-use-idea]");
    await page.waitForTimeout(20);
    const after = await page.inputValue("[data-message]");
    const focus = await page.evaluate(() => document.activeElement?.id);
    const message = await page.locator('p.sr-only[aria-live="polite"]').textContent();
    if (after !== before || focus !== `b-${name}` || message !== announcements[name]) fail(where, `empty ${name} changed the brief or missed focus/announcement (${focus}, ${message})`);
  }

  // shuffle draws only from the preset chips
  for (let i = 0; i < 20; i++) {
    await page.click("[data-shuffle]");
    const selected = await page.locator('[data-builder] input[type="radio"]:checked').evaluateAll((inputs) => inputs.map((input) => input.value));
    if (selected.length !== 3 || selected.includes("other")) fail(where, `shuffle selected ${selected.join(", ")}`);
  }
  await page.click("[data-shuffle]");

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

  // no maxlength: a long paste is kept and refused with a message, never cut silently
  await page.fill("#f-email", "name@brand.com");
  await page.fill("[data-message]", "x".repeat(4100));
  if ((await page.inputValue("[data-message]")).length !== 4100) fail(where, "the brief was truncated on input");
  await page.click('[data-form] button[type="submit"]');
  const longError = await page.textContent("#f-msg-err");
  if (!longError.includes("4,000")) fail(where, `a 4,100 character brief shows "${longError}"`);

  const text = "A headset launching in March. We need paid cuts for Meta.";
  await page.fill("[data-message]", text);
  const cleared = await page.evaluate(() => document.querySelectorAll("[data-field].is-error").length);
  if (cleared) fail(where, "errors stay after the fields are corrected");

  // without an endpoint: the brief is handed to email, visibly, and never reported as sent
  await page.click('[data-form] button[type="submit"]');
  await page.waitForTimeout(300);
  const handoff = await page.evaluate(() => {
    const form = document.querySelector("[data-form]");
    const gmail = new URL(document.querySelector("[data-handoff-gmail]").href);
    const mail = document.querySelector("[data-handoff-mailto]").href;
    return {
      sent: form.classList.contains("is-sent"),
      open: !document.querySelector("[data-handoff]").hidden,
      fieldsVisible: !!document.querySelector("[data-message]").offsetParent,
      footHidden: document.querySelector("[data-form-foot]").hidden,
      focus: document.activeElement?.hasAttribute("data-handoff-title"),
      title: document.querySelector("[data-handoff-title]").textContent,
      ready: document.querySelector("[data-handoff-body]").value,
      gmailTo: gmail.searchParams.get("to"),
      gmailBody: gmail.searchParams.get("body"),
      mailto: decodeURIComponent(mail),
      outlookTo: new URL(document.querySelector("[data-handoff-outlook]").href).searchParams.get("to"),
      primary: document.querySelector("[data-handoff-actions] .btn").textContent.trim(),
    };
  });
  if (handoff.sent) fail(where, "the fallback reports the brief as sent");
  if (!handoff.open || !handoff.fieldsVisible || !handoff.footHidden || !handoff.focus) fail(where, `hand-off state ${JSON.stringify({ ...handoff, ready: undefined })}`);
  if (!handoff.title.startsWith("One more step")) fail(where, `hand-off title "${handoff.title}"`);
  if (!handoff.ready.startsWith(text) || !handoff.ready.includes("Reply to: name@brand.com")) fail(where, `hand-off brief reads "${handoff.ready}"`);
  if (handoff.gmailTo !== "contact@wubba.studio" || !handoff.gmailBody?.startsWith(text)) fail(where, `Gmail link: to=${handoff.gmailTo}`);
  if (handoff.outlookTo !== "contact@wubba.studio") fail(where, `Outlook link: to=${handoff.outlookTo}`);
  if (!handoff.mailto.startsWith("mailto:contact@wubba.studio?subject=Brief for Wubba&body=" + text)) fail(where, `mailto link: ${handoff.mailto.slice(0, 90)}`);
  if (!handoff.primary.startsWith("Open in Gmail")) fail(where, `the hand-off leads with "${handoff.primary}" on desktop`);

  await page.click("[data-handoff-copy]");
  await page.waitForTimeout(400);
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  if (!copied.startsWith(text)) fail(where, `"Copy the brief" put "${copied.slice(0, 40)}" on the clipboard`);
  const copyLabel = await page.textContent("[data-handoff-copy-label]");
  if (copyLabel.trim() !== "Copied") fail(where, `copy button reads "${copyLabel}"`);

  // editing the brief closes the stale hand-off and brings the button back
  await page.type("[data-message]", " Budget in the call.");
  const reopened = await page.evaluate(() => ({
    handoff: document.querySelector("[data-handoff]").hidden,
    foot: document.querySelector("[data-form-foot]").hidden,
  }));
  if (!reopened.handoff || reopened.foot) fail(where, `after an edit ${JSON.stringify(reopened)}`);

  // a long brief: the mailto: link is shortened and the page says so
  await page.fill("[data-message]", "Long brief. ".repeat(250));
  await page.click('[data-form] button[type="submit"]');
  await page.waitForTimeout(200);
  const long = await page.evaluate(() => ({
    note: !document.querySelector("[data-handoff-long]").hidden,
    mailto: document.querySelector("[data-handoff-mailto]").href.length,
    gmail: new URL(document.querySelector("[data-handoff-gmail]").href).searchParams.get("body").length,
  }));
  if (!long.note || long.mailto > 2000 || long.gmail < 2900) fail(where, `long brief ${JSON.stringify(long)}`);

  // once a way to send was picked, the panel says what comes next, never that the email went out,
  // and the brief can be cleared
  await page.evaluate(() => {
    const link = document.querySelector("[data-handoff-gmail]");
    link.addEventListener("click", (event) => event.preventDefault(), { once: true });
    link.click();
  });
  const after = await page.evaluate(() => ({
    title: document.querySelector("[data-handoff-title]").textContent,
    clear: !document.querySelector("[data-handoff-clear]").hidden,
    sent: document.querySelector("[data-form]").classList.contains("is-sent"),
  }));
  if (!after.title.startsWith("Sent it?") || !after.clear || after.sent) fail(where, `after the hand-off ${JSON.stringify(after)}`);
  await page.click("[data-handoff-clear]");
  const clearedBrief = await page.evaluate(() => ({ message: document.querySelector("[data-message]").value, handoff: document.querySelector("[data-handoff]").hidden }));
  if (clearedBrief.message || !clearedBrief.handoff) fail(where, `"Clear the brief" leaves ${JSON.stringify(clearedBrief)}`);

  // the draft survives a reload in the same tab
  await page.fill("[data-message]", text);
  await page.waitForTimeout(400);
  await page.reload({ waitUntil: "networkidle" });
  const restored = await page.evaluate(() => ({ email: document.querySelector("#f-email").value, message: document.querySelector("[data-message]").value }));
  if (restored.email !== "name@brand.com" || restored.message !== text) fail(where, `draft after reload ${JSON.stringify(restored)}`);

  // copy the address
  await page.click("[data-copy]");
  await page.waitForTimeout(400);
  const label = await page.textContent("[data-copy-label]");
  if (label.trim() !== "Copied") fail(where, `copy button reads "${label}"`);
  const clip = await page.evaluate(() => navigator.clipboard.readText());
  if (clip !== "contact@wubba.studio") fail(where, `clipboard holds "${clip}"`);
  await context.close();
}

// with an endpoint: "Sending…", a real sent state that can be undone, and the hand-off when it fails
for (const status of [200, 500]) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const where = `endpoint ${status}`;
  const { page } = await open(context, "/brief", where, /\/api\/brief$/);
  let posted = null;
  await page.route("**/api/brief", async (route) => {
    posted = route.request().postDataJSON();
    await new Promise((r) => setTimeout(r, 300));
    await route.fulfill({ status, contentType: "application/json", body: "{}" });
  });
  await page.evaluate(() => (document.querySelector("[data-form]").dataset.endpoint = "/api/brief"));
  await page.fill("#f-email", "name@brand.com");
  await page.fill("[data-message]", "A chair launching in May.");
  await page.click('[data-form] button[type="submit"]');
  await page.waitForTimeout(200);
  const busy = await page.evaluate(() => ({
    label: document.querySelector("[data-submit-label]").textContent,
    busy: document.querySelector("[data-form]").getAttribute("aria-busy"),
  }));
  if (busy.label !== "Sending…" || busy.busy !== "true") fail(where, `while sending ${JSON.stringify(busy)}`);
  await page.waitForTimeout(700);
  const after = await page.evaluate(() => ({
    sent: document.querySelector("[data-form]").classList.contains("is-sent"),
    handoff: !document.querySelector("[data-handoff]").hidden,
    title: document.querySelector("[data-handoff-title]").textContent,
    focus: document.activeElement?.hasAttribute("data-status"),
  }));
  if (posted?.email !== "name@brand.com" || posted?.message !== "A chair launching in May.") fail(where, `posted ${JSON.stringify(posted)}`);
  if (status === 200) {
    if (!after.sent || after.handoff || !after.focus) fail(where, `after a 200 ${JSON.stringify(after)}`);
    await page.click("[data-edit]");
    const back = await page.evaluate(() => ({
      sent: document.querySelector("[data-form]").classList.contains("is-sent"),
      message: document.querySelector("[data-message]").value,
    }));
    if (back.sent || back.message !== "A chair launching in May.") fail(where, `"Edit the brief" ${JSON.stringify(back)}`);
  } else if (after.sent || !after.handoff || !after.title.startsWith("It didn’t go through")) {
    fail(where, `after a 500 ${JSON.stringify(after)}`);
  }
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  const where = "hand-off on a phone";
  const { page } = await open(context, "/brief", where);
  await page.fill("#f-email", "name@brand.com");
  await page.fill("[data-message]", "A mouse launching in June.");
  await page.click('[data-form] button[type="submit"]');
  await page.waitForTimeout(300);
  const primary = await page.evaluate(() => {
    const first = document.querySelector("[data-handoff-actions] .btn");
    return `${first.textContent.trim()} ${first.classList.contains("btn--green")}`;
  });
  if (primary !== "Open my email app true") fail(where, `the hand-off leads with "${primary}"`);
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
    barAction: getComputedStyle(document.querySelector(".bar__cta")).visibility,
  }));
  if (!opened.open || opened.expanded !== "true" || !opened.mainInert) fail(where, `open state ${JSON.stringify(opened)}`);
  if (opened.focus !== "Home") fail(where, `focus goes to "${opened.focus}" when the menu opens`);
  if (opened.current !== "The offer") fail(where, `current page in menu is "${opened.current}"`);
  if (opened.barAction !== "hidden") fail(where, "the bar keeps its green action while the menu shows its own");
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press("Tab");
    const behind = await page.evaluate(() => !!document.activeElement.closest("main, footer, .skip"));
    if (behind) {
      fail(where, "focus reaches the page behind the open menu");
      break;
    }
  }
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
  const where = "prefill /brief?product=monitor&place=desert&game=minecraft";
  const { page } = await open(context, "/brief?product=monitor&place=desert&game=minecraft", where);
  const idea = await page.textContent("[data-idea]");
  if (!idea.includes("monitor") || !idea.includes("in the desert") || !idea.includes("playing Minecraft")) fail(where, `idea reads "${idea}"`);
  const written = await page.inputValue("[data-message]");
  if (!written.startsWith("Idea: an AI streamer tests our monitor in the desert, playing Minecraft.")) fail(where, `the brief starts "${written.slice(0, 80)}"`);
  await page.close();
  const defaultGame = await open(context, "/brief?product=keyboard&place=cockpit", `${where} default game`);
  const defaultIdea = await defaultGame.page.textContent("[data-idea]");
  const defaultBrief = await defaultGame.page.inputValue("[data-message]");
  if (!defaultIdea.includes("playing Counter-Strike 2") || !defaultBrief.startsWith("Idea: an AI streamer tests our keyboard in a cockpit, playing Counter-Strike 2.")) fail(`${where} default game`, `default game missing from idea or brief (${defaultIdea})`);
  await context.close();
}

// ------------------------------------------------------------------ the film controls, with a stand-in film

{
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const where = "film controls";
  const home = await (await fetch(url + "/")).text();
  const assets = home.match(/<link rel="stylesheet"[^>]*>|<script type="module"[^>]*><\/script>|<svg xmlns[\s\S]*?<\/svg>/g).join("\n");
  const fixture = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>film</title>${assets}</head><body><main>
<div class="film" data-film style="width:320px"><video muted loop playsinline preload="none" data-src="/_fixture.webm" aria-label="test film"></video>
<div class="film__controls"><button class="film__btn" type="button" data-film-play><svg class="icon" aria-hidden="true"><use href="#i-pause"/></svg><span data-film-play-label>Pause</span></button>
<button class="film__btn" type="button" data-film-sound><svg class="icon" aria-hidden="true"><use href="#i-sound"/></svg><span data-film-sound-label>Sound on</span></button></div></div>
</main></body></html>`;
  await writeFile("dist/_film.html", fixture);
  await writeFile("dist/_fixture.webm", await readFile(new URL("./fixtures/film.webm", import.meta.url)));
  const { page } = await open(context, "/_film.html", where);
  await page.waitForTimeout(1200);
  const state = () =>
    page.evaluate(() => {
      const v = document.querySelector("video");
      return {
        paused: v.paused,
        muted: v.muted,
        play: document.querySelector("[data-film-play-label]").textContent,
        sound: document.querySelector("[data-film-sound-label]").textContent,
      };
    });
  const auto = await state();
  if (auto.paused || auto.play !== "Pause") fail(where, `in view it should play: ${JSON.stringify(auto)}`);
  await page.click("[data-film-play]");
  await page.waitForTimeout(200);
  const paused = await state();
  if (!paused.paused || paused.play !== "Play") fail(where, `after Pause ${JSON.stringify(paused)}`);
  await page.click("[data-film-sound]");
  await page.waitForTimeout(300);
  const sound = await state();
  if (sound.muted || sound.sound !== "Sound off" || sound.paused) fail(where, `after Sound on ${JSON.stringify(sound)}`);
  await context.close();
  await rm("dist/_film.html");
  await rm("dist/_fixture.webm");
}

// ------------------------------------------------------------------ print: the one-sheet and every page

// the text a PDF reader finds in a PDF (pdf.js, in stream order), or null when pdf.js is not installed
let pdfjs = null;
try {
  pdfjs = await import("pdfjs-dist/legacy/build/pdf.mjs");
} catch {
  warn("print", "PDF text checks skipped: run npm install in site/");
}
async function pdfText(buffer) {
  if (!pdfjs) return null;
  const task = pdfjs.getDocument({ data: new Uint8Array(buffer), disableFontFace: true, verbosity: 0 });
  const doc = await task.promise;
  let text = "";
  for (let i = 1; i <= doc.numPages; i++) {
    const content = await (await doc.getPage(i)).getTextContent();
    text += content.items.map((item) => item.str + (item.hasEOL ? "\n" : "")).join("") + "\n";
  }
  await task.destroy();
  return text;
}
const pageCount = (pdf) => (pdf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;

{
  const context = await browser.newContext({ viewport: { width: 1200, height: 1600 }, reducedMotion: "reduce" });
  const where = "one-sheet";
  const { page } = await open(context, "/", where);
  await page.emulateMedia({ media: "print", reducedMotion: "reduce" });
  const pdf = await page.pdf({ format: "A4", printBackground: true, preferCSSPageSize: true });
  if (pageCount(pdf) !== 1) fail(where, `prints on ${pageCount(pdf)} pages`);
  const ground = await page.evaluate(() => [getComputedStyle(document.documentElement).colorScheme, getComputedStyle(document.body).backgroundColor]);
  if (ground[0] !== "light" || ground[1] !== "rgb(255, 255, 255)") fail(where, `prints on ${ground.join(" / ")}`);

  // the figure is text in every PDF: the one-sheet as shipped, and a print made after the motion played
  const shipped = await pdfText(await readFile(join("dist", "wubba-one-sheet.pdf")));
  if (shipped !== null && !shipped.includes("98.8M")) fail(where, `the shipped PDF reads "${(shipped.match(/9\S*\s?\S*8M/) || ["no figure"])[0]}"`);
  const moving = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const { page: played } = await open(moving, "/", "print / after motion");
  await played.waitForTimeout(2200);
  await played.emulateMedia({ media: "print" });
  const after = await pdfText(await played.pdf({ format: "A4", printBackground: true }));
  if (after !== null && !(after.includes("98.8M") && after.includes("We build AI streamers"))) fail("print / after motion", "the hero prints as an image, not text");
  await moving.close();

  await context.close();

  // every other page prints short, without the screen-only devices
  const paper = await browser.newContext({ viewport: { width: 1200, height: 1600 }, reducedMotion: "reduce" });
  for (const [path, most] of [["/offer", 3], ["/series", 2], ["/about", 2], ["/brief", 1], ["/privacy", 2], ["/does-not-exist", 1]]) {
    const { page: sheetPage } = await open(paper, path, `print ${path}`);
    await sheetPage.emulateMedia({ media: "print", reducedMotion: "reduce" });
    const sheet = await sheetPage.pdf({ format: "A4", printBackground: true, preferCSSPageSize: true });
    if (pageCount(sheet) > most) fail(`print ${path}`, `runs to ${pageCount(sheet)} pages (at most ${most})`);
    const shown = await sheetPage.evaluate(() => [...document.querySelectorAll(".disc-band, .card, .builder")].filter((el) => el.getClientRects().length > 0).length);
    if (shown) fail(`print ${path}`, "prints the disc band, the title card or the idea builder");
    if (path === "/offer") {
      const frames = await sheetPage.evaluate(() => getComputedStyle(document.querySelector(".formats__frames")).display);
      if (frames !== "none") fail("print /offer", "the format frames remain visible in print");
    }
    if (path === "/series") {
      const text = await pdfText(sheet);
      if (text !== null && !text.includes("98.8M")) fail(`print ${path}`, "the figure does not print as 98.8M");
    }
    await sheetPage.close();
  }
  await paper.close();
}

// ------------------------------------------------------------------ weight and the preview build

{
  const home = await readFile(join("dist", "index.html"), "utf8");
  const files = ["index.html", ...[...home.matchAll(/(?:href|src)="\/(assets\/(?:css|js|fonts)\/[^"]+)"/g)].map((m) => m[1])];
  const css = files.find((f) => f.endsWith(".css"));
  const cssText = await readFile(join("dist", css), "utf8");
  for (const m of cssText.matchAll(/url\("\.\.\/(fonts\/[^"]+)"\)/g)) files.push(`assets/${m[1]}`);
  let bytes = 0;
  for (const f of new Set(files)) bytes += (await readFile(join("dist", f))).length;
  if (bytes > 320 * 1024) fail("weight", `home page payload ${Math.round(bytes / 1024)} KB (budget 320 KB)`);
  else warn("weight", `home page payload ${Math.round(bytes / 1024)} KB across ${new Set(files).size} files`);
  if (!/\.[0-9a-f]{8}\.css$/.test(css)) fail("cache", `the stylesheet is not fingerprinted: ${css}`);

  for (const file of (await readdir("preview")).filter((f) => f.endsWith(".html"))) {
    const html = await readFile(join("preview", file), "utf8");
    if (html.includes("wubba-one-sheet.pdf")) fail(`preview/${file}`, "offers a download the preview frame blocks");
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
