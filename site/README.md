# wubba.studio

The site, rebuilt on the new identity: black, white, the green point, Sora, Figtree and JetBrains Mono. Plain HTML, CSS and JavaScript. No framework, no dependencies at runtime.

## Pages

| Path | Page |
|---|---|
| `/` | Home, laid out as a media kit: the figure, the facts, the offer, the brief |
| `/series` | The first series and its record |
| `/offer` | How a campaign runs, the kit, rights and terms, questions |
| `/about` | Wubba, in the first person, without a name, a face or a city |
| `/brief` | The brief builder and form |
| `/privacy` | What the form collects |
| `404` | Page not found |

## Work on it

```bash
cd site
node build.mjs          # src/ -> dist/ (production) and preview/ (claude.ai preview)
node tools/serve.mjs    # http://127.0.0.1:4173, behaves like Vercel (clean URLs, 404 page)
npm install             # once, for the tests
node tests/gate.mjs     # the gate: every page at 6 widths, console errors, overflow, accessibility, links, form, menu
```

Sources live in `src/`:

- `src/pages/*.html`: one file per page. The comment at the top holds its title, description and path.
- `src/partials/`: header, footer, the brief block, the video slot, the logo, the icon sprite.
- `src/assets/css/site.css`: every style, tokens first. `src/assets/js/site.js`: every behaviour.
- `site.config.json`: links and switches (see below).

`tools/og.mjs` redraws the social card, `tools/pdf.mjs` prints the one-sheet PDF from the home page, `tools/shoot.mjs` takes screenshots. The logo files and fonts come from `../src/site_assets.py`, the same drawing as the brand kit.

## Things only you can fill in

Edit `site.config.json`, then rebuild:

- `tf1`: the URL of the TF1 fact-check. The "Read the TF1 fact-check" link stays hidden until it is set.
- `instagram`: set to `https://www.instagram.com/soren.ellison/`. Check it is the link you want public.
- `video.src` and `video.poster`: drop the series film (MP4, vertical, muted loop) and a still into `src/assets/media/`, then point these at `/assets/media/...`. The title card is replaced by the film everywhere.
- `formEndpoint`: where briefs are sent (a Vercel function, Formspree, Basin...). Until it is set, the form opens the visitor's email app with the brief already written, addressed to contact@wubba.studio.

## Deploy on Vercel (later)

Import the repository, set the root directory to `site`. `vercel.json` already sets the build command (`node build.mjs`), the output folder (`dist`), clean URLs, caching for assets and a few security headers.

## The loop

`.claude/settings.json` runs `.claude/hooks/site-gate.sh` whenever Claude Code tries to stop. If anything in `site/` changed since the last green run, it rebuilds and runs the gate; while the gate is red, the stop is refused with the list of failures. It gives up after 5 refusals in a row so it can never spin forever.
