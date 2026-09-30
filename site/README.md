# wubba.studio

The site, rebuilt on the new identity: black, white, the green point, Sora, Figtree and JetBrains Mono. Plain HTML, CSS and JavaScript. No framework, no dependencies at runtime.

## Pages

| Path | Page |
|---|---|
| `/` | Home, laid out as a media kit: the headline and the figure, the first series, the problem and the offer, the brief |
| `/series` | The first series: the count, the record, the format your film keeps |
| `/offer` | How a campaign runs, the kit, rights and terms, questions |
| `/about` | Wubba, in the first person, without a name, a face or a city |
| `/brief` | The brief form and the idea builder |
| `/privacy` | What the form collects |
| `404` | Page not found |

## Work on it

```bash
cd site
npm install             # once, for the tests (axe-core, and pdf.js to read the text of the PDFs)
npm run build           # src/ -> dist/ (production) and preview/ (claude.ai preview)
node tools/serve.mjs    # http://127.0.0.1:4173, behaves like Vercel (clean URLs, 404 page)
npm test                # build, then the gate: every page at 7 widths, real windows (laptops, phones upright and on their side), the first frame and the reveals with motion on, contrast, accessibility, links, form, menu, film, the print of every page and the text of the PDFs
npm run assets          # redraw the social card and reprint the one-sheet PDF (needs Chromium, run before committing)
npm run shots           # screenshots of every page in tests/shots/
```

Sources live in `src/`:

- `src/pages/*.html`: one file per page. The comment at the top holds its title, description and path.
- `src/partials/`: header, footer, the brief block, the film slot, the logo, the icon sprite.
- `src/assets/css/site.css`: every style, tokens first. `src/assets/js/site.js`: every behaviour.
- `site.config.json`: links and switches (see below).

`dist/` gets every file under `assets/` renamed with a hash of its content (`site.1a2b3c4d.css`), and the pages point at those names, so the year-long cache in `vercel.json` never serves an old file after a deploy. `preview/` keeps plain names.

The logo files and fonts come from `../src/site_assets.py`, the same drawing as the brand kit.

## Things only you can fill in

Edit `site.config.json`, then rebuild:

- `tf1`: the URL of the TF1 fact-check. The "Read the TF1 fact-check" link stays hidden until it is set.
- `instagram`: the account where the series lives. It drives the "The first series on Instagram" links (hero, home and title card). Check it is the link you want public. Once a link to the series post itself exists, it can take its place.
- `video.src` and `video.poster`: drop the series film (MP4, vertical, muted loop) and a still into `src/assets/media/`, then point these at `/assets/media/...`. The film replaces the title card everywhere, with Pause and Sound buttons, and the hero button becomes "Watch the film".
- `formEndpoint`: where briefs are sent (a Vercel function, Formspree, Basin...). It receives a JSON POST: `{ email, message, page }`. Until it is set, the form writes the brief as an email and offers four ways to send it: Gmail, Outlook, the visitor's email app, or copy. It never says "sent" unless the endpoint answered.

## Deploy on Vercel (later)

Import the repository, set the root directory to `site`. `vercel.json` already sets the build command (`node build.mjs`), the output folder (`dist`), clean URLs, caching for assets and a few security headers.

## The loop

`.claude/settings.json` runs `.claude/hooks/site-gate.sh` whenever Claude Code tries to stop. If anything in `site/` changed since the last green run, it rebuilds, reprints the one-sheet PDF, rebuilds again and runs the gate; while the gate is red, the stop is refused with the list of failures. It gives up after 5 refusals in a row so it can never spin forever. `tests/fixtures/film.webm` is a two-second stand-in film the gate uses to check the film controls.
