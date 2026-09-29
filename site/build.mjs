// Builds wubba.studio into two folders from src/:
//   dist/     the production site (clean URLs, for Vercel)
//   preview/  the same site with file links, for the claude.ai preview
// No dependencies. Run: node site/build.mjs

import { cp, mkdir, readdir, readFile, rm, writeFile } from "node:fs/promises";
import { basename, dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const SRC = join(ROOT, "src");
const config = JSON.parse(await readFile(join(ROOT, "site.config.json"), "utf8"));

const escape = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

async function loadPartials() {
  const partials = {};
  for (const file of await readdir(join(SRC, "partials"))) {
    partials[basename(file, extname(file))] = (await readFile(join(SRC, "partials", file), "utf8")).trim();
  }
  return partials;
}

// {{#if key}} … {{else}} … {{/if}}, nesting allowed
function conditionals(text, vars) {
  const open = /\{\{#if (\w+)\}\}/g;
  let match;
  while ((match = open.exec(text))) {
    let depth = 1;
    let i = match.index + match[0].length;
    let elseAt = -1;
    const tokens = /\{\{(#if \w+|else|\/if)\}\}/g;
    tokens.lastIndex = i;
    let token;
    while ((token = tokens.exec(text))) {
      if (token[1].startsWith("#if")) depth += 1;
      else if (token[1] === "else" && depth === 1) elseAt = token.index;
      else if (token[1] === "/if" && --depth === 0) break;
    }
    if (!token) throw new Error(`unclosed {{#if ${match[1]}}}`);
    const body = text.slice(i, elseAt >= 0 ? elseAt : token.index);
    const alt = elseAt >= 0 ? text.slice(elseAt + "{{else}}".length, token.index) : "";
    const chosen = vars[match[1]] ? body : alt;
    text = text.slice(0, match.index) + chosen + text.slice(token.index + token[0].length);
    open.lastIndex = match.index;
  }
  return text;
}

function render(template, vars, partials, depth = 0) {
  if (depth > 8) throw new Error("partials nest too deep");
  let out = template.replace(/\{\{> ([\w-]+)\}\}/g, (_, name) => {
    if (!(name in partials)) throw new Error(`missing partial ${name}`);
    return render(partials[name], vars, partials, depth + 1);
  });
  out = conditionals(out, vars);
  return out.replace(/\{\{(\w+)\}\}/g, (_, key) => {
    if (!(key in vars)) throw new Error(`missing variable ${key}`);
    return escape(vars[key]);
  });
}

function pageMeta(source) {
  const block = source.match(/^<!--([\s\S]*?)-->\s*/);
  if (!block) throw new Error("page is missing its meta block");
  const meta = {};
  for (const line of block[1].split("\n")) {
    const at = line.indexOf(":");
    if (at > 0) meta[line.slice(0, at).trim()] = line.slice(at + 1).trim();
  }
  return { meta, body: source.slice(block[0].length) };
}

function markCurrent(html, nav) {
  return html.replace(/data-nav="([\w-]+)"/g, (all, key) => (key === nav ? `${all} aria-current="page"` : all));
}

// production links (/series) become file links (series.html) for the preview
function fileLinks(html) {
  return html
    .replace(/(href|src|poster)="\/(?=[#"])/g, '$1="index.html')
    .replace(/(href|src|poster)="\/(series|offer|about|brief|privacy)(?=[#"])/g, '$1="$2.html')
    .replace(/(href|src|poster|data-src)="\/(?!\/)/g, '$1="');
}

// The claude.ai frame refuses form actions pointing at mailto: and has no use for a web manifest,
// so the preview drops both; the script still handles the form.
function previewSafe(html) {
  return html
    .replace(/<link rel="manifest"[^>]*>\s*/, "")
    .replace(/ action="mailto:[^"]*" method="post" enctype="text\/plain"/g, "");
}

// claude.ai pages start with <title>; the platform supplies <html>, <head> and <body>
function artifactPage(html) {
  const head = html.match(/<head>([\s\S]*?)<\/head>/)[1];
  const body = html.match(/<body>([\s\S]*?)<\/body>/)[1];
  const title = head.match(/<title>[\s\S]*?<\/title>/)[0];
  const rest = head
    .replace(title, "")
    .replace(/<meta charset[^>]*>\s*/, "")
    .replace(/<meta name="viewport"[^>]*>\s*/, "");
  return `<title>wubba.studio</title>\n${rest.trim()}\n${body.trim()}\n`;
}

async function build() {
  const partials = await loadPartials();
  const pagesDir = join(SRC, "pages");
  const pages = [];
  for (const file of (await readdir(pagesDir)).filter((f) => f.endsWith(".html"))) {
    const { meta, body } = pageMeta(await readFile(join(pagesDir, file), "utf8"));
    const vars = {
      ...config,
      ...meta,
      year: new Date().getFullYear(),
      video: config.video?.src ?? "",
      videoPoster: config.video?.poster ?? "",
    };
    const html = markCurrent(render(body, vars, partials), meta.nav);
    if (/\{\{|\}\}/.test(html)) throw new Error(`unrendered template tag in ${file}`);
    pages.push({ file, meta, html });
  }

  for (const out of ["dist", "preview"]) {
    await rm(join(ROOT, out), { recursive: true, force: true });
    await mkdir(join(ROOT, out), { recursive: true });
    await cp(join(SRC, "assets"), join(ROOT, out, "assets"), { recursive: true });
    await cp(join(SRC, "static"), join(ROOT, out), { recursive: true });
  }

  for (const { file, html } of pages) {
    await writeFile(join(ROOT, "dist", file), html);
    const preview = previewSafe(fileLinks(html));
    await writeFile(join(ROOT, "preview", file), file === "index.html" ? artifactPage(preview) : preview);
  }
  // full document of the home page for local checks of the preview folder
  await writeFile(join(ROOT, "preview", "_home.html"), fileLinks(pages.find((p) => p.file === "index.html").html));

  const listed = pages.filter((p) => !["404.html"].includes(p.file));
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${listed
    .map((p) => `  <url><loc>${config.origin}${p.meta.path === "/" ? "/" : p.meta.path}</loc></url>`)
    .join("\n")}\n</urlset>\n`;
  await writeFile(join(ROOT, "dist", "sitemap.xml"), sitemap);
  console.log(`built ${pages.length} pages into dist/ and preview/`);
}

await build();
