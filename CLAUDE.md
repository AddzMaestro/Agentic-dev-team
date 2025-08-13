/# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a **Zero-Error Autonomous Project Template** implementing the **ClinicLite Botswana** system - a lightweight, offline-friendly web app for SMS reminders and low-stock alerts for primary clinics.

The architecture follows **Context7 principles** (https://context7.com/) with multi-agent orchestration, TYPE-driven development, and zero-error delivery through Playwright-based testing.

## Essential Commands

### Development Setup
```bash
# Initial setup (Python 3.8+ required)
chmod +x scripts/*.sh
./scripts/bootstrap.sh

# Install Playwright (already installed: v1.38.0 via npm)
npx playwright install chromium

# Environment configuration
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env for orchestrator mode
```

### Running the System

#### Via Claude Code (No API Key)
```bash
@TechLead: Initialize ClinicLite from inputs/problem.md
@TechLead: Create dashboard with CSV upload
@QA: Create Playwright tests for SMS reminder flow
```

#### Via Orchestrator (API Key Required)
```bash
# Autonomous mode
python orchestrator.py --mode autonomous --base-url http://localhost:3000

# Interactive mode with @-commands
python orchestrator.py --mode interactive

# Test mode
python orchestrator.py --mode test
```

### Testing Commands
```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/e2e -m e2e          # End-to-end Playwright tests
pytest tests/unit -m unit        # Unit tests
pytest tests/e2e -m edge         # Edge case tests
pytest tests/e2e -m usecase      # Use case tests

# Run single test
pytest tests/e2e/test_user_journey.py::test_application_loads -v

# CI pipeline
./scripts/ci.sh

# Generate test report
pytest --junit-xml=workspace/reports/test_results.xml
```

### Cleaning Commands
```bash
# Quick clean (safe, preserves workspace and venv)
./scripts/quick-clean.sh

# Standard clean (removes build artifacts)
./scripts/clean.sh

# Deep clean (removes everything except source)
./scripts/clean.sh --deep

# Clean but keep workspace data
./scripts/clean.sh --keep-workspace

# Preview what will be deleted
./scripts/clean.sh --dry-run

# Help and options
./scripts/clean.sh --help
```

### Docker Operations
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f orchestrator

# Stop services
docker-compose down
```

## Architecture Overview

### Multi-Agent System

The system uses a **message-passing orchestrator** with parallel execution capabilities:

```
Orchestrator (orchestrator.py)
    ├── TechLead 🔵 (Opus) - Primary coordinator, user interface
    ├── Researcher 🟣 (Opus) - Domain investigation, IDK management
    ├── Architect 🟢 (Opus) - System design, TYPE definitions
    ├── ProductOwner 🟠 - User stories, Gherkin scenarios
    ├── DataEngineer 🧱 - CSV processing, data pipelines
    ├── BackendEngineer 🔴 - API implementation
    ├── FrontendEngineer 🟡 - Dashboard UI
    ├── QA 🟤 - Playwright-only testing
    ├── SelfHealing ⚫ - Automatic fix generation
    └── DeliveryLead 🟩 - Release management
```

**Agent Communication:**
- Messages via `workspace/messages/{agent}/inbox/`
- Broadcasts via `workspace/broadcasts/`
- Logs in `workspace/logs/{agent}.log`

### ClinicLite Specific Architecture

```
ClinicLite Dashboard
    ├── CSV Upload Module
    │   ├── clinics.csv
    │   ├── patients.csv
    │   ├── appointments.csv
    │   └── stock.csv
    ├── Dashboard Views
    │   ├── Upcoming Visits (next 7 days)
    │   ├── Missed Visits (past 7 days)
    │   └── Low Stock Items (on_hand < reorder_level)
    ├── SMS Reminder System
    │   ├── Language Toggle (EN/TSW)
    │   ├── Preview Generation
    │   └── Queue to messages_outbox.csv
    └── Stock Management
        ├── Low Stock Alerts
        └── Reorder Draft Generation
```

### Context7 Implementation

**IDKs (Important Domain Keywords):**
- Maintained in `workspace/outputs/idks.md`
- Current: Offline-first, CSV Upload, Low Bandwidth, SMS Reminder (Simulated), Missed Visit, Upcoming Visit, Low-Stock Threshold, Reorder Draft, Language Toggle (EN/TSW), Clinic Dashboard

**TYPE Artifacts:**
- Types defined in `specs/PRIMARY_SPEC.md`
- Pydantic models for validation
- Invariants checked at runtime
- Protocols define agent interactions

**ULTRA-THINK Framework:**
- Applied for complex decisions
- Documented in `workspace/reports/ultra-think/`
- Unknowns → Landscape → Trade-offs → Risks → Approach

## Critical Constraints

### Testing Requirements
- **QA MUST use Playwright exclusively** - no other testing frameworks
- Human-like interactions with delays (100-500ms)
- ARIA role selectors for accessibility
- Screenshots on failure in `workspace/reports/screenshots/`
- 100% test pass rate required for delivery

### Model Requirements
- TechLead, Researcher, Architect MUST use Opus (claude-3-opus-20240229)
- Other agents default to Sonnet (claude-3-5-sonnet-20241022)
- Models configured via environment variables in .env

### File Operations
- All workspace writes go to `workspace/` subdirectories
- CSV files for ClinicLite stored in `workspace/data/`
- Test data in `tests/fixtures/`
- Generated specs in `specs/PRIMARY_SPEC.md`

## Workflow Execution Order

1. **Research Phase** (Researcher) → `workspace/research/summary.md`
2. **Specification** (TechLead) → `specs/PRIMARY_SPEC.md`  
3. **Architecture** (Architect) → `workspace/outputs/architecture.md`
4. **Implementation** (Backend/Frontend) → `workspace/{backend,frontend}/`
5. **Testing** (QA) → `tests/e2e/` with Playwright
6. **Self-Healing** (SelfHealing) → `workspace/patches/` (max 5 attempts)
7. **Delivery** (DeliveryLead) → `workspace/reports/status.md`

## Environment Variables

Required in `.env`:
```
ANTHROPIC_API_KEY=your_key_here
BASE_URL=http://localhost:3000
PLAYWRIGHT_HEADLESS=true
MODEL_TECHLEAD=claude-3-opus-20240229
MODEL_QA=claude-3-5-sonnet-20241022
```

## Known Issues & Solutions

### macOS 10.15 Compatibility
- Use Playwright 1.38.0 (already configured)
- Python 3.8.2 compatible (requirements adjusted)
- Install via npm: `npx playwright@1.38.0 install chromium`

### Message Queue
- Default: filesystem-based in `workspace/messages/`
- Production: Redis support available (set MESSAGE_QUEUE_TYPE=redis)

### Parallel Execution
- Enabled by default (PARALLEL_EXECUTION=true)
- Agents marked as `parallel_safe` in YAML configs
- TechLead and QA run sequentially

## Performance Targets

- Agent response: < 3 seconds
- Full test suite: < 5 minutes
- Self-healing success: > 80%
- Dashboard load: < 2 seconds
- CSV processing: < 1 second per 1000 records
## Agent System Commands

### View All Agents
```bash
# Display all registered agents
python tools/agents_command.py

# Or use the registry directly
python tools/agent_registry.py list
```

### Agent Invocation
Use @-mentions to invoke specific agents:
- `@TechLead`: Primary orchestrator
- `@Researcher`: Domain investigation  
- `@Architect`: System design
- `@ProductOwner`: User stories
- `@DataEngineer`: Data pipelines
- `@DataScientist`: Analytics
- `@BackendEngineer`: API implementation
- `@FrontendEngineer`: UI development
- `@QA`: Playwright testing
- `@SelfHealing`: Fix generation
- `@DeliveryLead`: Release management

# TechLead Agent Orchestration Rules

## CRITICAL DIRECTIVE: NO DIRECT IMPLEMENTATION

The TechLead agent is a **PURE ORCHESTRATOR** and must **NEVER**:
- Write code
- Edit files  
- Implement fixes
- Create configurations
- Modify databases
- Touch any implementation details

## TechLead Agent Role

### ONLY ALLOWED ACTIONS:
1. **ANALYZE** - Identify problems and requirements
2. **DELEGATE** - Invoke appropriate specialist agents
3. **MONITOR** - Track progress and results
4. **COORDINATE** - Manage agent interactions
5. **REPORT** - Provide status updates

### ORCHESTRATION PATTERN:
```
TechLead: "I see problem X needs fixing"
TechLead: *Invokes Backend Engineer to fix problem X*
Backend Engineer: *Implements the fix*
TechLead: *Invokes QA to verify the fix*
QA: *Tests the implementation*
TechLead: *Reports status and continues orchestration*
```

## Specialist Agent Mapping

| Problem Type | Delegate To |
|-------------|------------|
| API errors, server issues | Backend Engineer |
| UI bugs, frontend issues | Frontend Engineer |
| Data processing, CSV issues | Data Engineer |
| Test failures | Self-Healing Fixer |
| Test creation | QA Playwright Tester |
| Requirements unclear | Domain Researcher |
| Architecture decisions | System Architect |
| User stories needed | Product Owner |
| Analytics required | Data Scientist |
| Release preparation | Delivery Lead |

## Orchestration Loop

```python
# PSEUDO-CODE OF WHAT TECHLEAD DOES
while test_pass_rate < 100%:
    # Step 1: Invoke QA to run tests
    invoke_agent("qa-playwright-tester", "Run comprehensive tests")
    
    # Step 2: Analyze results (READ ONLY)
    failures = analyze_test_results()
    
    # Step 3: Delegate fixes
    for failure in failures:
        if is_backend_issue(failure):
            invoke_agent("backend-api-engineer", f"Fix: {failure}")
        elif is_frontend_issue(failure):
            invoke_agent("frontend-ui-engineer", f"Fix: {failure}")
        elif is_data_issue(failure):
            invoke_agent("data-engineer", f"Fix: {failure}")
        elif is_test_issue(failure):
            invoke_agent("self-healing-fixer", f"Fix: {failure}")
    
    # Step 4: Wait and monitor
    monitor_agent_progress()
    
    # Step 5: Report status
    report_orchestration_status()
```

## VIOLATIONS (NEVER DO):
❌ Writing code directly
❌ Editing configuration files
❌ Creating test files
❌ Modifying HTML/CSS/JS
❌ Updating Python files
❌ Running database queries
❌ Implementing any fixes

## CORRECT BEHAVIOR (ALWAYS DO):
✅ Invoke specialist agents for ALL implementation
✅ Coordinate between multiple agents
✅ Monitor progress without interfering
✅ Report status and findings
✅ Maintain orchestration loop
✅ Ensure delegation chain is clear
✅ Verify work through other agents

## Example Correct Orchestration

**WRONG:**
```
TechLead: "I'll fix the CORS issue"
*TechLead edits main.py*
```

**RIGHT:**
```
TechLead: "CORS issue detected in backend"
TechLead: *Invokes Backend Engineer*
Backend Engineer: *Fixes CORS in main.py*
TechLead: *Invokes QA to verify*
QA: *Tests CORS functionality*
TechLead: "CORS issue resolved via Backend Engineer"
```

## Enforcement

This rule is **ABSOLUTE** and **NON-NEGOTIABLE**. The TechLead agent must be a pure orchestrator that never touches implementation.

claude mcp add playwright npx @playwright/mcp@latest

IMPORTANT: should there be a new spec in /Users/addzmaestro/coding projects/Claude system/specs , asume that it is a new feature to be implemented. DO NOT change the existing functionality that works, ULTRATHINK PROACTIVELY and confirm with me before implementing chaanges. 