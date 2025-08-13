# Agent Creation Instructions for Claude Code

## How to Use These Files

These instruction files are designed for manual agent creation in Claude Code using the `/agent` command.

### Step-by-Step Process:

1. **Open Claude Code**
2. **Type `/agent` to start the agent creation wizard**
3. **For each agent file (01-TechLead.md through 11-DeliveryLead.md):**
   - Enter the **Agent Name** from the file
   - Copy the **Description** for the agent description field
   - Copy everything under **Instructions to Copy-Paste** into the agent instructions field
   - Save the agent

### Agent Creation Order:

Create agents in this sequence for proper dependency management:

1. **01-TechLead.md** - Primary orchestrator (Opus model recommended)
2. **02-Researcher.md** - Domain expert (Opus model recommended)
3. **03-Architect.md** - System designer (Opus model recommended)
4. **04-ProductOwner.md** - Requirements manager (Sonnet model)
5. **05-DataEngineer.md** - Data pipeline builder (Sonnet model)
6. **06-DataScientist.md** - Analytics engine (Sonnet model)
7. **07-BackendEngineer.md** - API developer (Sonnet model)
8. **08-FrontendEngineer.md** - UI builder (Sonnet model)
9. **09-QA.md** - Test engineer (Sonnet model)
10. **10-SelfHealing.md** - Auto-fixer (Sonnet model)
11. **11-DeliveryLead.md** - Release manager (Sonnet model)

### Agent Dependencies:

- **TechLead** → Can invoke ALL agents
- **Architect** → Can invoke: DataEngineer, BackendEngineer, FrontendEngineer
- **ProductOwner** → Can invoke: QA
- **DataEngineer** → Can invoke: DataScientist
- **QA** → Can invoke: SelfHealing
- **SelfHealing** → Can invoke: QA
- **DeliveryLead** → Can invoke ALL agents

### Quick Copy Format:

Each file contains:
```
Agent Name: [Simple name without emoji]
Description: [One-line description]
Instructions: [Full prompt to copy-paste]
```

### After Creating All Agents:

Once all agents are created, you can:
1. Use `/agents` to see your created agents
2. Invoke specific agents with `@AgentName`
3. Chain agents based on their dependencies
4. Run the TechLead agent to orchestrate all others

### Testing Your Agents:

Start with a simple test:
```
@TechLead: Initialize the ClinicLite project structure
```

The TechLead should then orchestrate other agents as needed.

### Important Notes:

- The TechLead agent has been modified to NOT create/modify code directly - it only orchestrates
- Each agent has specific responsibilities following Context7 principles
- Agents marked as "parallel_safe" can run simultaneously
- QA agent MUST use Playwright for all testing
- SelfHealing has maximum 5 attempts to fix failures

### Color Legend (for reference):

- 🔵 Blue - TechLead (Orchestrator)
- 🟣 Purple - Researcher (Domain Expert)
- 🟢 Green - Architect (System Design)
- 🟠 Orange - ProductOwner (Requirements)
- 🧱 Brick - DataEngineer (ETL/Pipeline)
- 🔬 Cyan - DataScientist (Analytics)
- 🔴 Red - BackendEngineer (APIs)
- 🟡 Yellow - FrontendEngineer (UI)
- 🟤 Brown - QA (Testing)
- ⚫ Black - SelfHealing (Auto-fix)
- 🟩 Bright Green - DeliveryLead (Release)