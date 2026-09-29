#!/usr/bin/env bash
# Stop hook: the site's mechanical gate (loop engineering, step 4a).
# Runs only when site/ changed since the last green run. It rebuilds, reprints the one-sheet PDF,
# rebuilds again and runs the gate. While the gate is red it blocks the stop and hands the failures
# back; after 5 blocks in a row it lets the stop through so it never spins forever.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SITE="$ROOT/site"
STATE="$ROOT/.claude/hooks/.site-gate"
[ -d "$SITE/src" ] || exit 0
mkdir -p "$STATE"

say() { jq -n --arg m "$1" '{systemMessage: $m}'; }

# the PDF and the social card are outputs, so they stay out of the hash
HASH=$(cd "$SITE" && find src build.mjs site.config.json tests/gate.mjs tests/fixtures tools -type f \
  ! -name 'wubba-one-sheet.pdf' ! -name 'og.png' -print0 2>/dev/null \
  | sort -z | xargs -0 sha1sum | sha1sum | cut -c1-40)
if [ "$(cat "$STATE/green" 2>/dev/null)" = "$HASH" ]; then
  rm -f "$STATE/blocks"
  exit 0
fi

if [ ! -f "$SITE/node_modules/axe-core/axe.min.js" ]; then
  say "Site gate skipped: run npm install in site/ first."
  exit 0
fi

OUT=$(cd "$SITE" && node build.mjs 2>&1 && node tools/pdf.mjs 2>&1 && node build.mjs 2>&1 && node tests/gate.mjs 2>&1)
if [ $? -eq 0 ]; then
  echo "$HASH" > "$STATE/green"
  rm -f "$STATE/blocks"
  say "Site gate green."
  exit 0
fi

BLOCKS=$(( $(cat "$STATE/blocks" 2>/dev/null || echo 0) + 1 ))
echo "$BLOCKS" > "$STATE/blocks"
FAILS=$(printf '%s\n' "$OUT" | grep -E '^FAIL|rror' | head -25)
if [ "$BLOCKS" -gt 5 ]; then
  rm -f "$STATE/blocks"
  say "Site gate still red after 5 attempts, stopping anyway:
$FAILS"
  exit 0
fi
jq -n --arg f "$FAILS" '{decision: "block", reason: ("The site gate (site/tests/gate.mjs) is red. Fix these before stopping:\n" + $f)}'
exit 0
