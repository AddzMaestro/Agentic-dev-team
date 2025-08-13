#!/usr/bin/env python3
"""
Stop gate:
- If tests aren't green, block the stop and nudge Claude to continue (stderr -> Claude)
- Uses a small attempt counter to avoid infinite loops
"""
import sys, json, os

data = json.load(sys.stdin)
project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

# Inputs we check
reports = os.path.join(project, "workspace", "reports")
result_path = os.path.join(reports, "last_test_result.json")
state_path  = os.path.join(project, ".claude", "state.json")

def read_json(p, default):
    try:
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return default

# Gate on test status
passed = False
jr = read_json(result_path, {})
passed = bool(jr.get("passed", False))

# Autonomous mode: max 5 retries for self-healing
state = read_json(state_path, {"attempts": 0})
attempts = int(state.get("attempts", 0))

stop_hook_active = bool(data.get("stop_hook_active", False))

if not passed and attempts < 5 and not stop_hook_active:
    state["attempts"] = attempts + 1
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f: json.dump(state, f, indent=2)

    # Tell Claude exactly what to do next (stderr goes to Claude when exit 2 on Stop)
    guidance = f"""
AUTONOMOUS MODE: Tests not green (attempt {attempts+1}/5). Continue automatically:

- If tests don't exist or are failing:
  1) QA (🟤): write/repair Playwright tests in ./tests/e2e/test_user_journey.py
  2) Run tests via: `python tools/test_runner.py` (writes workspace/reports/last_test_result.json)

- If tests fail:
  1) SelfHealing (⚫): propose minimal patches under ./workspace/patches/*.md
  2) Apply patches and re-run `python tools/test_runner.py`
  3) Repeat until 100% pass or 5 attempts.

Remember:
- Keep perfect Context × Model × Prompt balance.
- Respect TYPE-first and curated context.
"""
    sys.stderr.write(guidance.strip()+"\n")
    sys.exit(2)  # blocks the stop; Claude sees guidance and keeps going

# If green or we've tried enough, allow stop and reset attempts
if attempts != 0:
    try:
        with open(state_path, "w", encoding="utf-8") as f: json.dump({"attempts": 0}, f)
    except Exception:
        pass

print("Stop OK")  # visible in transcript (Ctrl-R)
sys.exit(0)