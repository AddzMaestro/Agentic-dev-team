#!/usr/bin/env bash
# Activate and register agents in Claude Code system

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Activating Context7 Agent System${NC}"
echo "======================================"

# 1. Generate agent registry
echo -e "${YELLOW}Step 1:${NC} Generating agent registry..."
python3 tools/agent_registry.py save
echo -e "${GREEN}✓${NC} Registry saved to .claude/agent_registry.json"

# 2. Display registered agents
echo -e "\n${YELLOW}Step 2:${NC} Registered agents:"
python3 tools/agent_registry.py list

# 3. Create agent command aliases
echo -e "\n${YELLOW}Step 3:${NC} Creating agent command interface..."

# Create the agents command script
cat > tools/agents_command.py << 'EOF'
#!/usr/bin/env python3
"""
Agents command for Claude Code
Shows all registered agents when /agents is typed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.agent_registry import AgentRegistry

if __name__ == "__main__":
    print(AgentRegistry.display_agents())
    
    # Show invocation help
    print("\n📝 INVOCATION EXAMPLES:")
    print("-" * 40)
    print("@TechLead: Initialize ClinicLite project")
    print("@Researcher: Investigate SMS gateway options")  
    print("@Architect: Design offline-first architecture")
    print("@QA: Create Playwright tests for CSV upload")
    print("-" * 40)
EOF

chmod +x tools/agents_command.py

echo -e "${GREEN}✓${NC} Agent command interface created"

# 4. Update CLAUDE.md with agent invocation
echo -e "\n${YELLOW}Step 4:${NC} Updating CLAUDE.md with agent system..."

# Add agent system section to CLAUDE.md if not exists
if ! grep -q "## Agent System Commands" CLAUDE.md 2>/dev/null; then
    cat >> CLAUDE.md << 'EOF'

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
EOF
    echo -e "${GREEN}✓${NC} CLAUDE.md updated"
else
    echo -e "${GREEN}✓${NC} CLAUDE.md already contains agent system"
fi

# 5. Create symbolic link for /agents command
echo -e "\n${YELLOW}Step 5:${NC} Setting up /agents command..."

# Create agents wrapper
cat > agents << 'EOF'
#!/usr/bin/env python3
import os
import sys
os.system("python3 tools/agents_command.py")
EOF

chmod +x agents
echo -e "${GREEN}✓${NC} /agents command ready"

echo -e "\n${GREEN}✅ Agent System Activated!${NC}"
echo ""
echo "You can now use:"
echo "  • ${BLUE}./agents${NC} - View all registered agents"
echo "  • ${BLUE}@AgentName${NC} - Invoke specific agent"
echo "  • ${BLUE}python tools/agent_registry.py list${NC} - Detailed agent view"
echo ""
echo "The agents are now registered in the system!"