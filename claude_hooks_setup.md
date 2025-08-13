bash <<'SETUP'
set -euo pipefail

HOOK_DIR="$HOME/.claude/hooks"
SETTINGS="$HOME/.claude/settings.json"

mkdir -p "$HOOK_DIR"

cat > "$HOOK_DIR/pre_bash_guard.sh" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail
payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""' || true)"
if [[ "${ALLOW_RISKY:-0}" == "1" ]]; then exit 0; fi
ALLOW_REGEX='^(ls|pwd|cat|echo|git\s+(status|diff|add|commit|push|pull)|npm\s+(i|install|run)|pnpm|yarn|python3?\s+.*|pytest|uvicorn|poetry|node\s+.*|docker(\s+compose)?\s+.*)$'
RISKY_REGEX='(rm\s+-rf\s+\/)|(rm\s+-rf\s+[^ ]+)|(sudo\s+)|(mkfs\.)|(dd\s+if=.+\s+of=\/dev\/)|(chown\s+-R\s+root)|(chmod\s+-R\s+777)|(curl\s+.*\|\s*sh)|(wget\s+.*\|\s*sh)'
[[ -z "${cmd:-}" ]] && exit 0
if [[ "$cmd" =~ $ALLOW_REGEX ]]; then exit 0; fi
if echo "$cmd" | grep -Eqi "$RISKY_REGEX"; then
  echo "Blocked risky command: $cmd
Tip: export ALLOW_RISKY=1 if you really intend this (temporarily)." 1>&2
  exit 2
fi
exit 0
BASH

cat > "$HOOK_DIR/post_edit_format_and_lint.sh" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail
payload="$(cat)"
mapfile -t files < <(printf '%s' "$payload" | jq -r '
  (.tool_input.file_path? // empty) as $one
  | ([$one] + (.tool_input.edits? // [] | map(.file_path)))
  | flatten | unique | .[]?' || true)
format_one () {
  f="$1"; [ -f "$f" ] || return 0
  case "$f" in
    *.js|*.jsx|*.ts|*.tsx|*.json|*.css|*.scss|*.md|*.html|*.yaml|*.yml)
      if command -v npx >/dev/null 2>&1; then
        npx prettier --write "$f" || true
        if [[ "$f" =~ \.(js|jsx|ts|tsx)$ ]] && npx -y eslint -v >/dev/null 2>&1; then
          npx eslint --fix "$f" || true
        fi
      fi
      ;;
    *.py)
      command -v ruff >/dev/null 2>&1 && ruff check --fix "$f" || true
      command -v black >/dev/null 2>&1 && black -q "$f" || true
      ;;
    *.go)
      command -v gofmt >/dev/null 2>&1 && gofmt -w "$f" || true
      ;;
    *) : ;;
  esac
}
for f in "${files[@]:-}"; do format_one "$f"; done
exit 0
BASH

cat > "$HOOK_DIR/post_edit_unit_tests.sh" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail
run_pytests () { command -v pytest >/dev/null 2>&1 && pytest -q --maxfail=1; }
run_vitest () { command -v npx >/dev/null 2>&1 && npx -y vitest --version >/dev/null 2>&1 && npx vitest --run --reporter=line; }
run_jest   () { command -v npx >/dev/null 2>&1 && npx -y jest --version   >/dev/null 2>&1 && npx jest --runInBand; }
(run_pytests && exit 0) || true
(run_vitest  && exit 0) || true
(run_jest    && exit 0) || true
echo "No unit test runner detected (pytest/vitest/jest). Skipping." 1>&2
exit 0
BASH

cat > "$HOOK_DIR/e2e_smoke_playwright.sh" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail
payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""' || true)"
if ! echo "$cmd" | grep -Eiq "(npm run (dev|start)|pnpm (dev|start)|yarn (dev|start)|uvicorn|flask run|docker compose up|bun run (dev|start))"; then
  exit 0
fi
if ! command -v npx >/dev/null 2>&1 || ! npx -y playwright --version >/dev/null 2>&1; then
  echo "Playwright not installed. Skipping smoke test." 1>&2
  exit 0
fi
npx playwright install >/dev/null 2>&1 || true
mkdir -p e2e/artifacts
if [ ! -f e2e/smoke.spec.ts ]; then
  cat > e2e/smoke.spec.ts <<'TS'
import { test, expect } from '@playwright/test';
import fs from 'fs';
test('smoke: home loads', async ({ page }) => {
  const url = process.env.SMOKE_URL || 'http://localhost:3000';
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await expect(page).toHaveTitle(/.+/);
  fs.mkdirSync('e2e/artifacts', { recursive: true });
  await page.screenshot({ path: 'e2e/artifacts/smoke-home.png', fullPage: true });
});
TS
fi
npx playwright test e2e/smoke.spec.ts --reporter=line
BASH

cat > "$HOOK_DIR/notify_mac.sh" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail
osascript -e 'display notification "Awaiting your input" with title "Claude Code"'
exit 0
BASH

chmod +x "$HOOK_DIR"/*.sh || true

# Ensure jq exists
if ! command -v jq >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    brew install jq
  else
    echo "Please install Homebrew (brew.sh) then run: brew install jq"
  fi
fi

python3 - "$SETTINGS" <<'PY'
import json, pathlib, sys
settings_path = pathlib.Path(sys.argv[1]).expanduser()
settings = {}
if settings_path.exists():
  try: settings = json.loads(settings_path.read_text())
  except Exception: pass
def add(hooks, t, e):
  arr = hooks.setdefault(t, [])
  cmd = e["hooks"][0]["command"]
  for x in arr:
    try:
      if x["hooks"][0]["command"] == cmd and x.get("matcher","") == e.get("matcher",""):
        return
    except Exception: pass
  arr.append(e)
hooks = settings.setdefault("hooks", {})
add(hooks,"PreToolUse",{"matcher":"Bash","hooks":[{"type":"command","command":"bash $HOME/.claude/hooks/pre_bash_guard.sh"}]})
add(hooks,"PostToolUse",{"matcher":"Edit|Write|MultiEdit","hooks":[
  {"type":"command","command":"bash $HOME/.claude/hooks/post_edit_format_and_lint.sh"},
  {"type":"command","command":"bash $HOME/.claude/hooks/post_edit_unit_tests.sh"}]})
add(hooks,"PostToolUse",{"matcher":"Bash","hooks":[{"type":"command","command":"bash $HOME/.claude/hooks/e2e_smoke_playwright.sh"}]})
add(hooks,"Notification",{"hooks":[{"type":"command","command":"bash $HOME/.claude/hooks/notify_mac.sh"}]})
settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, indent=2)+"\n")
print("Updated", settings_path)
PY
SETUP
