# 🚀 Autonomous Agent System - Quick Setup Guide

## What You're About to Experience

This is a **fully autonomous development system** that will:
- 🤖 **Build your entire project with minimal human intervention**
- 🔄 **Self-heal when tests fail (up to 5 attempts)**
- ✨ **Create new specialized agents on-demand**
- ✅ **Continue until >70% test coverage achieved**
- 🎯 **Deliver production-ready, zero-error code**

## ⚡ 2-Minute Setup

### Step 0: Clone the Repository
```bash
git clone https://github.com/AddzMaestro/Agentic-dev-team.git
cd Agentic-dev-team
```

### Step 1: Run the Setup Script
```bash
./quick_setup.sh
```

This will:
- Check prerequisites (Python 3.8+, Node.js, Git)
- Create virtual environment
- Install all dependencies
- Setup Playwright with Chromium
- Create project structure
- Generate .env configuration
- Create sample problem statement

### Step 2: Add Your API Key
```bash
nano .env
# Replace 'your_api_key_here' with your actual ANTHROPIC_API_KEY
```

### Step 3: Setup Claude Hooks (Essential for Autonomous Features)
Claude hooks enable the autonomous workflow by enforcing test requirements, adding orchestration context, and creating dynamic agents.

**Quick Setup (Recommended)**:
```bash
# Run the automated hook installer
bash claude_hooks_setup.md

# This configures:
# ✅ Stop gate - Blocks exit until >70%% tests pass
# ✅ Context injection - Adds orchestration contracts
# ✅ Agent creator - Enables dynamic agent generation
# ✅ Safety guards - Prevents dangerous commands
```

**Manual Setup** (if you prefer control):
```bash
# 1. Copy project hooks to Claude directory
mkdir -p ~/.claude/hooks
cp .claude/hooks/* ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py

# 2. Configure Claude settings
python3 -c "
import json, pathlib
settings_path = pathlib.Path.home() / '.claude' / 'settings.json'
settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
hooks = settings.setdefault('hooks', {})

# Essential autonomous hooks
hooks['Stop'] = [{'hooks': [{'type': 'command', 'command': '\$CLAUDE_PROJECT_DIR/.claude/hooks/stop_gate.py'}]}]
hooks['UserPromptSubmit'] = [{'hooks': [{'type': 'command', 'command': '\$CLAUDE_PROJECT_DIR/.claude/hooks/user_prompt_submit.py'}]}]
hooks['ToolCallSubmit'] = [{'hooks': [{'type': 'command', 'command': '\$CLAUDE_PROJECT_DIR/.claude/hooks/agent_creator.py'}]}]

settings_path.parent.mkdir(exist_ok=True)
settings_path.write_text(json.dumps(settings, indent=2))
print('✅ Hooks configured successfully')
"
```

**Verify Hook Installation**:
```bash
# Check if hooks are active
cat ~/.claude/settings.json | grep -A 2 "Stop\|UserPrompt\|ToolCall"

# Expected output should show the three essential hooks
```

**Why Are Hooks Essential?**

Without hooks, the autonomous system can't:
- ❌ Enforce 100% test passing requirement (manual exit possible)
- ❌ Automatically inject orchestration context (agents won't coordinate properly)
- ❌ Create dynamic agents on-demand (limited to pre-defined agents)
- ❌ Prevent dangerous bash commands (potential system damage)

With hooks enabled, you get:
- ✅ **True Autonomy**: System runs until >70% tests pass, no exceptions
- ✅ **Perfect Coordination**: All agents get proper context automatically
- ✅ **Dynamic Scaling**: New specialized agents created as needed
- ✅ **Safety First**: Dangerous commands blocked before execution

### Step 4: Start Autonomous Development
```bash
# Option A: Fully Autonomous (Fire & Forget)
python orchestrator.py --mode autonomous

# Option B: Claude Code (Interactive)
# Open in Claude Code and say:
@TechLead: Initialize ClinicLite from inputs/problem.md

# Option C: Interactive CLI
python orchestrator.py --mode interactive
# Then: @MetaAgent: Build the system in inputs/problem.md
```

### Step 4: Watch the Magic
```bash
# Monitor real-time progress
tail -f workspace/logs/orchestrator.log

# Check test status
watch -n 1 'cat workspace/reports/last_test_result.json | jq .'

# View agent messages
ls workspace/messages/*/inbox/
```

## 🤖 The Autonomous Agent Orchestra

### Master Orchestrators (Opus Models)
- **🔵 MetaAgent** - Creates new agents, manages task graphs
- **🔵 TechLead** - Technical coordinator, user interface
- **🟣 Researcher** - Domain investigation, requirements
- **🟢 Architect** - System design, TYPE definitions

### Implementation Specialists (Sonnet Models)
- **🟠 ProductOwner** - User stories, acceptance criteria
- **🧱 DataEngineer** - Data pipelines, CSV processing
- **🔬 DataScientist** - Analytics, ML models
- **🔴 BackendEngineer** - APIs, server logic
- **🟡 FrontendEngineer** - React UI, offline PWA
- **🟤 QA** - Playwright test creation
- **⚫ SelfHealing** - Automatic test fixes
- **🟩 DeliveryLead** - Release management

### Dynamic Agents (Created as Needed)
- **dynamic_cache_optimizer_xxx** - Performance tuning
- **dynamic_security_auditor_xxx** - Security analysis
- **dynamic_[expertise]_xxx** - Any specialized need

## 🔄 The Autonomous Loop

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Problem → MetaAgent → Task Graph → Agents     │
│     ↑                                    ↓      │
│     └──── Tests Pass ← Self-Heal ← Tests Fail  │
│                                                 │
└─────────────────────────────────────────────────┘
```

The system runs this loop **continuously** until all tests pass:

1. **MetaAgent** analyzes the problem
2. Creates a **task graph** with execution plan
3. **Orchestrates agents** in parallel when possible
4. **Runs Playwright tests** after implementation
5. If tests fail → **SelfHealing** generates fixes
6. Applies patches and retests
7. If still failing after 5 attempts → **MetaAgent creates specialist**
8. Continues until **>70% green**

## 📋 Your First Autonomous Project

The setup creates a sample project in `inputs/problem.md`:

```markdown
# ClinicLite Botswana - Rural Clinic Management

A lightweight, offline-capable web app for rural clinics with:
- CSV upload dashboard
- Appointment management
- SMS reminders (simulated)
- Stock monitoring
- English/Setswana support
```

To build it autonomously:
```bash
python orchestrator.py --mode autonomous
```

The system will:
1. Research clinic requirements
2. Design the architecture
3. Build backend APIs
4. Create React frontend
5. Write comprehensive tests
6. Fix any failures automatically
7. Deliver working system

## 🎮 Usage Modes Explained

### Mode 1: Fully Autonomous (Recommended)
```bash
python orchestrator.py --mode autonomous
```
- Runs without any intervention
- Continues until 100% tests pass
- Self-heals failures automatically
- Creates new agents if needed

### Mode 2: Claude Code Integration
```bash
# In Claude Code, use @-commands:
@TechLead: Start autonomous development
@MetaAgent: Create a caching system
@QA: Write tests for login flow
```
- Interactive with visual feedback
- Direct agent invocation
- See results in real-time

### Mode 3: Interactive CLI
```bash
python orchestrator.py --mode interactive

# Then interact with agents:
> @Architect: Design the database schema
> @BackendEngineer: Implement the API
> @SelfHealing: Fix the failing tests
```
- Command-line interaction
- Direct agent control
- Good for debugging

### Mode 4: Continuous Operation (24/7)
```bash
./scripts/loop.sh
```
- Runs indefinitely
- Processes task queue
- Ideal for CI/CD pipelines

## 🛡️ Safety Features

### Automatic Stop Gates
- **Test Gate**: Won't stop until tests pass
- **Retry Limit**: Max 5 self-healing attempts
- **Timeout**: 1-hour maximum runtime
- **Manual Stop**: `touch .claude/stop`

### Context Isolation
- Agents only see authorized files
- No system file access
- Sandboxed execution

### Hook System
- `stop_gate.py` - Enforces test passing
- `user_prompt_submit.py` - Validates commands
- `agent_creator.py` - Controls agent creation

## 📊 Monitoring & Debugging

### Real-Time Status
```bash
# Overall status
cat workspace/reports/status.md

# Test results
cat workspace/reports/last_test_result.json | jq .

# Agent activity
tail -f workspace/logs/*.log

# Message queue
ls -la workspace/messages/*/inbox/
```

### Performance Metrics
- Agent response: < 3 seconds
- Test suite: < 5 minutes
- Self-healing: > 80% success
- Full pipeline: < 30 minutes

## 🔧 Configuration Options

### Key Environment Variables (.env)
```bash
# Models (Opus for reasoning, Sonnet for implementation)
MODEL_METAAGENT=claude-3-opus-20240229
MODEL_TECHLEAD=claude-3-opus-20240229
MODEL_QA=claude-3-5-sonnet-20241022

# Autonomous Behavior
MAX_SELF_HEAL_ATTEMPTS=5     # Retry limit
PARALLEL_EXECUTION=true       # Run agents in parallel
AUTO_CREATE_AGENTS=true       # Dynamic agent creation
STOP_GATE_ACTIVE=true        # Enforce test passing

# Testing
PLAYWRIGHT_HEADLESS=true     # Background testing
TEST_TIMEOUT=30000          # 30 second timeout
BASE_URL=http://localhost:3000
```

## 🚨 Troubleshooting

### Issue: Dependencies Won't Install
```bash
# Fix pip/setuptools
pip install --upgrade pip setuptools wheel

# Install core packages manually
pip install anthropic playwright pytest loguru pydantic
```

### Issue: Playwright Not Working
```bash
# Reinstall Playwright
pip install playwright==1.38.0
playwright install chromium --with-deps
```

### Issue: Tests Keep Failing
```bash
# Check test logs
cat workspace/reports/last_test_result.json

# View screenshots
ls workspace/reports/screenshots/

# Manually trigger self-healing
@SelfHealing: Fix all failing tests
```

### Issue: Agent Not Responding
```bash
# Check agent logs
tail -f workspace/logs/<agent_name>.log

# Check message queue
ls workspace/messages/<agent_name>/inbox/

# Restart orchestrator
pkill -f orchestrator.py
python orchestrator.py --mode autonomous
```

### Issue: Hooks Not Working (Autonomous Features Disabled)

**Symptoms**:
- Claude Code exits before tests pass 100%
- Agents don't have proper orchestration context
- Dynamic agents not being created
- No safety blocking for dangerous commands

**Diagnosis**:
```bash
# Check if hooks are configured
ls ~/.claude/hooks/
cat ~/.claude/settings.json | jq '.hooks'

# Test hook execution
python3 .claude/hooks/stop_gate.py < /dev/null
```

**Fix**:
```bash
# Reinstall hooks
bash claude_hooks_setup.md

# Or manual reinstall
mkdir -p ~/.claude/hooks
cp .claude/hooks/* ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py

# Verify configuration
cat ~/.claude/settings.json | grep -A 5 "hooks"
```

### Issue: Stop Gate Not Triggering

**Symptoms**:
- Claude Code exits even when tests are failing
- No "continue automatically" messages

**Fix**:
```bash
# Check test results file exists
ls workspace/reports/last_test_result.json

# Run tests manually to generate results
python tools/test_runner.py

# Test stop gate manually
echo '{"stop_hook_active": false}' | python3 .claude/hooks/stop_gate.py

# Expected: Should show guidance to continue
```

### Issue: Infinite Loop
The system has protections:
- Max 5 self-healing attempts
- 1-hour timeout
- Manual stop: `touch .claude/stop`

## 📈 Success Indicators

You'll know the system is working when you see:

✅ **In Logs:**
```
[INFO] MetaAgent: Task graph created with 12 nodes
[INFO] TechLead: Orchestrating parallel execution
[INFO] QA: Running Playwright tests...
[INFO] Tests: 24/24 passing (100%)
[INFO] DeliveryLead: Zero-error delivery achieved
```

✅ **In Test Results:**
```json
{
  "passed": true,
  "total": 24,
  "passed_count": 24,
  "failed_count": 0,
  "duration": "45.2s"
}
```

✅ **In Status Report:**
```markdown
## Project Status: COMPLETE ✅
- All tests passing (100%)
- Zero errors detected
- Ready for production
```

## 🎯 Next Steps

After setup, follow this sequence:

1. **Verify hooks are working** (Critical!)
   ```bash
   # Should show hook configuration
   cat ~/.claude/settings.json | grep -A 5 "hooks"
   
   # If no hooks configured, autonomous features won't work!
   # Re-run: bash claude_hooks_setup.md
   ```

2. **Modify the problem statement**
   ```bash
   nano inputs/problem.md
   # Add your own requirements
   ```

3. **Run autonomous development**
   ```bash
   python orchestrator.py --mode autonomous
   
   # With hooks: Will run until 100% tests pass
   # Without hooks: May exit early with failing tests
   ```

4. **Monitor progress**
   ```bash
   tail -f workspace/logs/orchestrator.log
   ```

5. **Review generated code**
   ```bash
   ls workspace/backend/
   ls workspace/frontend/
   ```

6. **Run the application**
   ```bash
   cd workspace/backend && python main.py
   cd workspace/frontend && npm start
   ```

**🚨 Important**: If autonomous mode exits before reaching 100% test coverage, your hooks are likely not configured properly. Re-run the hook setup in Step 3.

## 🚀 Advanced Usage

### Creating Custom Agents
```python
# Request via MetaAgent
@MetaAgent: Create a performance optimizer agent

# MetaAgent will:
# 1. Design agent specification
# 2. Generate agent code
# 3. Register in system
# 4. Invoke for task
```

### Custom Task Graphs
```json
// workspace/outputs/task_graph.json
{
  "nodes": [
    {"id": "custom_analysis", "agent": "dynamic_analyzer"},
    {"id": "optimization", "agent": "dynamic_optimizer"}
  ],
  "edges": [
    {"from": "custom_analysis", "to": "optimization"}
  ]
}
```

### Parallel Agent Execution
```yaml
# Agents that can run simultaneously
parallel_groups:
  - [DataEngineer, FrontendEngineer, Researcher]
  - [QA, SelfHealing]
  - [BackendEngineer, DataScientist]
```

## 💡 Pro Tips

1. **Let it run**: Don't interrupt the autonomous process
2. **Trust self-healing**: It usually fixes issues within 3 attempts
3. **Check logs**: Most issues are visible in orchestrator.log
4. **Use parallel mode**: Speeds up development significantly
5. **Keep tests simple**: Playwright tests should be straightforward

## 📚 Resources

- **Documentation**: [README.md](README.md)
- **Context7 Principles**: [.claude/ai-docs/CONTEXT7_PRINCIPLES.md]
- **Agent Guide**: [.claude/ai-docs/AGENT_INTERACTION_GUIDE.md]
- **API Specs**: Generated in `workspace/outputs/api_spec.yaml`

## 🎉 Ready to Go!

You now have a fully autonomous development system that will:
- Build your project from a simple description
- Test everything with Playwright
- Fix any failures automatically
- Deliver production-ready code

**Start your first autonomous build:**
```bash
python orchestrator.py --mode autonomous
```

Then sit back and watch as 12+ AI agents collaborate to build your project! 🚀

## 📋 Quick Reference

### Essential Hook Commands
```bash
# Install hooks (run once per system)
bash claude_hooks_setup.md

# Verify hooks are active
cat ~/.claude/settings.json | grep -A 2 "Stop\|UserPrompt"

# Test stop gate manually
echo '{"stop_hook_active": false}' | python3 .claude/hooks/stop_gate.py

# Disable hooks temporarily
export CLAUDE_DISABLE_HOOKS=1

# Re-enable hooks
unset CLAUDE_DISABLE_HOOKS
```

### Autonomous Mode Commands
```bash
# Start fully autonomous mode (requires hooks)
python orchestrator.py --mode autonomous

# Interactive mode with Claude Code
@TechLead: Initialize project from inputs/problem.md

# Check if tests are passing
cat workspace/reports/last_test_result.json | jq '.passed'

# Monitor agent activity
tail -f workspace/logs/orchestrator.log
```

### Common Issues & Quick Fixes
| Problem | Quick Fix |
|---------|-----------|
| Exits before tests pass | `bash claude_hooks_setup.md` |
| No orchestration context | Check `~/.claude/settings.json` has hooks |
| Tests not running | `python tools/test_runner.py` |
| Agents not coordinating | Restart with hooks: `python orchestrator.py --mode autonomous` |

---

*"From problem to production without human intervention"* - The promise of autonomous development, delivered.