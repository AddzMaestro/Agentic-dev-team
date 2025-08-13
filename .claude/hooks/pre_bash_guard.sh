#!/usr/bin/env bash
# Blocks risky shell commands unless explicitly allowlisted
set -euo pipefail

payload="$(cat)"

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Warning: jq is not installed. Pre-bash guard is disabled." >&2
    exit 0
fi

cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""')"

# Skip guard if you really want to (export ALLOW_RISKY=1)
if [[ "${ALLOW_RISKY:-0}" == "1" ]]; then
  exit 0
fi

# Allowlist (safe patterns you run often)
ALLOW_REGEX='^(ls|pwd|cat|echo|git\s+(status|diff|add|commit|push|pull)|npm\s+(i|install|run)|pnpm|yarn|python3?\s+.*|pytest|uvicorn|poetry|node\s+.*|docker(\s+compose)?\s+.*)$'

# Blocklist (expand as needed)
RISKY_REGEX='
  (rm\s+-rf\s+\/)|(rm\s+-rf\s+[^ ]+)|
  (sudo\s+)|
  (mkfs\.)|
  (dd\s+if=.+\s+of=\/dev\/)|
  (chown\s+-R\s+root)|
  (chmod\s+-R\s+777)|
  (curl\s+.*\|\s*sh)|
  (wget\s+.*\|\s*sh)
'

if [[ -z "$cmd" ]]; then
  exit 0
fi

if [[ "$cmd" =~ $ALLOW_REGEX ]]; then
  exit 0
fi

if echo "$cmd" | grep -Eqi "$RISKY_REGEX"; then
  echo "Blocked risky command: $cmd
Tip: set ALLOW_RISKY=1 temporarily if you really intend this." 1>&2
  # Exit code 2 = politely block (Claude adapts)
  exit 2
fi

exit 0
