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
    const greens = async () =>
      page.evaluate(() =>
        [...document.querySelectorAll(".btn--green")]
          .filter((b) => {
            const r = b.getBoundingClientRect();
            const style = getComputedStyle(b);
            return b.offsetParent && style.visibility === "visible" && Number(style.opacity) > 0.5 && r.bottom > 0 && r.top < innerHeight;
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

    // the closing band: every word and button sits on the green disc
    const offDisc = await page.evaluate(() => {
      const disc = document.querySelector(".disc-band__disc");
      if (!disc) return [];
      const d = disc.getBoundingClientRect();
      const cx = d.left + d.width / 2;
      const cy = d.top + d.height / 2;
      const r = d.width / 2 - 6;
      const inside = (x, y) => (x - cx) ** 2 + (y - cy) ** 2 <= r * r;
      const out = [];
      for (const el of document.querySelectorAll(".disc-band__in > :not(.disc-band__disc)")) {
        // line boxes, not the element box: ragged lines may leave the corners empty
        const range = document.createRange();
        range.selectNodeContents(el);
        const rects = [...range.getClientRects()].filter((q) => q.width > 1);
        if (el.classList.contains("btn")) rects.push(el.getBoundingClientRect());
        for (const q of rects) {
          if (![[q.left, q.top], [q.right, q.top], [q.left, q.bottom], [q.right, q.bottom]].every(([x, y]) => inside(x, y))) {
            out.push(`${el.tagName.toLowerCase()}.${el.className} "${el.textContent.trim().slice(0, 30)}"`);
            break;
          }
        }
      }
      return out;
    });
    if (offDisc.length) fail(where, `off the green disc: ${offDisc.join(", ")}`);

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
        return [...document.querySelectorAll(".field__box, .chip input:not(:checked) + span, .btn--line, .copy, .mail")]
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

// ------------------------------------------------------------------ the first screen tells the whole hook

for (const [width, height] of [
  [1280, 720],
  [1366, 768],
  [1440, 900],
  [390, 844],
]) {
  const context = await browser.newContext({ viewport: { width, height }, reducedMotion: "reduce" });
  const where = `fold @${width}x${height}`;
  const { page } = await open(context, "/", where);
  const fold = await page.evaluate(() => {
    const bottom = (s) => document.querySelector(s).getBoundingClientRect().bottom;
    const title = parseFloat(getComputedStyle(document.querySelector(".hero__title")).fontSize);
    const h2 = parseFloat(getComputedStyle(document.querySelector("main .h2")).fontSize);
    return { twist: bottom(".hero__twist"), actions: bottom(".hero__actions"), title, h2 };
  });
  if (fold.twist > height) fail(where, `"The guy in it doesn't exist." ends at ${Math.round(fold.twist)}px, below the fold`);
  if (fold.actions > height) fail(where, "the hero actions sit below the fold");
  if (width >= 1280 && fold.title < fold.h2 * 0.95) fail(where, `the headline (${fold.title}px) is smaller than the section headings (${fold.h2}px)`);
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

  // the bar's green action waits until the hero's has scrolled away
  const barAtTop = await page.evaluate(() => getComputedStyle(document.querySelector(".bar__cta")).visibility);
  await page.evaluate(() => document.querySelector(".pitch").scrollIntoView());
  await page.waitForTimeout(500);
  const barLater = await page.evaluate(() => getComputedStyle(document.querySelector(".bar__cta")).visibility);
  if (barAtTop !== "hidden" || barLater !== "visible") fail(where, `bar action is ${barAtTop} at the top and ${barLater} further down`);

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
      primary: document.querySelector("[data-handoff-actions] .btn").textContent.trim(),
    };
  });
  if (handoff.sent) fail(where, "the fallback reports the brief as sent");
  if (!handoff.open || !handoff.fieldsVisible || !handoff.footHidden || !handoff.focus) fail(where, `hand-off state ${JSON.stringify({ ...handoff, ready: undefined })}`);
  if (!handoff.title.startsWith("One more step")) fail(where, `hand-off title "${handoff.title}"`);
  if (!handoff.ready.startsWith(text) || !handoff.ready.includes("Reply to: name@brand.com")) fail(where, `hand-off brief reads "${handoff.ready}"`);
  if (handoff.gmailTo !== "contact@wubba.studio" || !handoff.gmailBody?.startsWith(text)) fail(where, `Gmail link: to=${handoff.gmailTo}`);
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
  if (!long.note || long.mailto > 3600 || long.gmail < 2900) fail(where, `long brief ${JSON.stringify(long)}`);

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
  const where = "prefill /brief?product=monitor&place=desert";
  const { page } = await open(context, "/brief?product=monitor&place=desert", where);
  const idea = await page.textContent("[data-idea]");
  if (!idea.includes("monitor") || !idea.includes("in the desert")) fail(where, `idea reads "${idea}"`);
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

// ------------------------------------------------------------------ the one-sheet prints on one white page

{
  const context = await browser.newContext({ viewport: { width: 1200, height: 1600 }, reducedMotion: "reduce" });
  const where = "one-sheet";
  const { page } = await open(context, "/", where);
  await page.emulateMedia({ media: "print", reducedMotion: "reduce" });
  const pdf = await page.pdf({ format: "A4", printBackground: true, preferCSSPageSize: true });
  const pages = (pdf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
  if (pages !== 1) fail(where, `prints on ${pages} pages`);
  const ground = await page.evaluate(() => [getComputedStyle(document.documentElement).colorScheme, getComputedStyle(document.body).backgroundColor]);
  if (ground[0] !== "light" || ground[1] !== "rgb(255, 255, 255)") fail(where, `prints on ${ground.join(" / ")}`);
  await context.close();
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
