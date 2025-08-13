#!/usr/bin/env python3
"""
UserPromptSubmit injector:
- Adds your orchestration contract into the prompt context (stdout -> context for this hook)
- Optionally blocks dangerous prompts (exit 2)
"""
import sys, json, re, os
data = json.load(sys.stdin)
prompt = data.get("prompt","")

# Block obviously dangerous intents (adjust as you like)
blocked = [
    r"rm\s+-rf\s+/",
    r"curl\s+[^|]+?\|\s*bash",
    r"dd\s+if=/dev/zero",
]
if any(re.search(p, prompt, re.I) for p in blocked):
    sys.stderr.write("Blocked: prompt matched a dangerous pattern. Rephrase safely.\n")
    sys.exit(2)   # blocks the prompt entirely

# Inject orchestration contract (stdout is ADDED TO CONTEXT for this hook)
injection = f"""
ORCHESTRATION CONTRACT
----------------------
- Perfect balance of Context × Model × Prompt for every step.
- Follow Context7 and TYPE-first (Types, Invariants, Protocols, Examples).
- Maintain 8–12 IDKs in ./workspace/outputs/idks.md; reuse them in names/headings.
- Sub-agents get curated context only (files the TechLead intentionally provides).
- QA and SelfHealing MUST use Playwright (pytest), human-like mouse/pauses, aria roles.
- Closed loop: Research → SPEC → Backlog → Architecture → QA (tests) → Impl → SelfHealing (≤5) → Delivery.
- SPEC MUST follow ./specs/spec_template.md exactly; QA tests map 1:1 to Low-Level Tasks.

When uncertain:
- ULTRA-THINK: Unknowns → Options → Pre-mortem → Micro-plan (with file paths) → Evidence (log to ./workspace/reports).
"""
sys.stdout.write(injection.strip()+"\n")
sys.exit(0)  # success: injection is appended to Claude's context