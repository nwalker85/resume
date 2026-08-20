#!/usr/bin/env bash
# Print resume.html to resume.pdf via headless Chrome (US Letter via CSS @page).
# HTTP, not file://, so remote fonts load.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
HTML_FILE="${1:-resume.html}"
HTML_PATH="${DIR}/${HTML_FILE}"
OUT="${DIR}/resume.pdf"
TMP_OUT="${OUT}.tmp"

CHROME=""
for c in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
  google-chrome-stable \
  google-chrome \
  chromium \
  chromium-browser
do
  if [[ "$c" == /* && -x "$c" ]]; then
    CHROME="$c"
    break
  fi
  if [[ "$c" != /* ]] && command -v "$c" >/dev/null 2>&1; then
    CHROME="$(command -v "$c")"
    break
  fi
done

if [[ -z "$CHROME" ]]; then
  echo "Install Chrome, Chromium, or Edge to print this résumé." >&2
  exit 1
fi

if [[ ! -f "$HTML_PATH" ]]; then
  echo "Résumé HTML not found: $HTML_PATH" >&2
  exit 1
fi

PORT="${RESUME_HTTP_PORT:-$((9844 + RANDOM % 100))}"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

(cd "$DIR" && python3 -m http.server "$PORT" >/dev/null 2>&1) &
SERVER_PID=$!
sleep 1.2

"$CHROME" \
  --headless=new \
  --disable-gpu \
  --disable-dev-shm-usage \
  --no-first-run \
  --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw \
  --virtual-time-budget=40000 \
  --print-to-pdf="$TMP_OUT" \
  "http://127.0.0.1:${PORT}/${HTML_FILE}"

python3 - <<PY
from pathlib import Path
tmp = Path("$TMP_OUT")
out = Path("$OUT")
data = tmp.read_bytes()
assert data.startswith(b"%PDF"), "resume.pdf is not a PDF"
assert tmp.stat().st_size > 50_000, f"print too small ({tmp.stat().st_size}); leaving existing résumé in place"
tmp.replace(out)
print(f"Wrote {out} ({out.stat().st_size} bytes)")
PY
