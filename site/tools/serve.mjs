// Static server that behaves like Vercel with cleanUrls: /series -> series.html, unknown -> 404.html.
import http from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize, resolve } from "node:path";

const TYPES = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8", ".json": "application/json", ".webmanifest": "application/manifest+json",
  ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon", ".webp": "image/webp", ".jpg": "image/jpeg",
  ".woff2": "font/woff2", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8", ".pdf": "application/pdf",
  ".mp4": "video/mp4", ".webm": "video/webm",
};

async function exists(path) {
  try { return (await stat(path)).isFile(); } catch { return false; }
}

export function serve(dir, port = 0) {
  const root = resolve(dir);
  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, "http://x");
    let path = normalize(decodeURIComponent(url.pathname)).replace(/^(\.\.[/\\])+/, "");
    let file = join(root, path);
    if (path.endsWith("/")) file = join(file, "index.html");
    else if (!extname(path) && (await exists(file + ".html"))) file += ".html";
    let status = 200;
    if (!file.startsWith(root) || !(await exists(file))) {
      status = 404;
      file = join(root, "404.html");
    }
    const body = await readFile(file);
    res.writeHead(status, { "Content-Type": TYPES[extname(file)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(body);
  });
  return new Promise((ok) => server.listen(port, "127.0.0.1", () => ok({ server, url: `http://127.0.0.1:${server.address().port}` })));
}

if (process.argv[1] && process.argv[1].endsWith("serve.mjs")) {
  const { url } = await serve(process.argv[2] || "dist", Number(process.argv[3] || 4173));
  console.log(`serving on ${url}`);
}
