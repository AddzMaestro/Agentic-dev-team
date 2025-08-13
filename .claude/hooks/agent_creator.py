#!/usr/bin/env python3
"""
Dynamic Agent Creator Hook
Creates specialized agents on-demand when MetaAgent detects novel requirements
"""
import sys
import json
import os
import uuid
from pathlib import Path
from datetime import datetime

def create_agent_definition(agent_spec):
    """Generate agent definition file from specification"""
    agent_id = f"dynamic_{agent_spec['expertise']}_{uuid.uuid4().hex[:4]}"
    
    definition = f"""---
name: {agent_id}
description: Dynamically created agent for {agent_spec['purpose']}
model: {agent_spec.get('model', 'sonnet')}
created: {datetime.now().isoformat()}
expires: {agent_spec.get('expires', '24h')}
---

You are {agent_id}, a specialized agent created for: {agent_spec['purpose']}

**Core Expertise**: {agent_spec['expertise']}

**Primary Responsibilities**:
{chr(10).join(f"- {r}" for r in agent_spec.get('responsibilities', []))}

**Context Access**:
{chr(10).join(f"- {f}" for f in agent_spec.get('files_allowed', []))}

**Success Criteria**:
{chr(10).join(f"- {c}" for c in agent_spec.get('success_criteria', []))}

**Constraints**:
- Follow Context7 principles
- Maintain TYPE-first development
- All changes must have corresponding Playwright tests
- Report progress to MetaAgent

**Output Format**:
Provide clear, actionable results that can be validated through tests.
"""
    
    return agent_id, definition

def register_agent(agent_id, definition):
    """Register the new agent in the system"""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    
    # Save agent definition
    agent_file = Path(project_dir) / ".claude" / "agents" / f"{agent_id}.md"
    agent_file.parent.mkdir(parents=True, exist_ok=True)
    agent_file.write_text(definition)
    
    # Update dynamic agents registry
    registry_file = Path(project_dir) / "workspace" / "outputs" / "dynamic_agents.json"
    if registry_file.exists():
        registry = json.loads(registry_file.read_text())
    else:
        registry = {"agents": {}, "total_created": 0, "active_count": 0}
    
    registry["agents"][agent_id] = {
        "created": datetime.now().isoformat(),
        "status": "active",
        "definition_path": str(agent_file)
    }
    registry["total_created"] += 1
    registry["active_count"] += 1
    
    registry_file.write_text(json.dumps(registry, indent=2))
    
    return agent_file

def main():
    """Hook entry point for ToolCallSubmit"""
    try:
        data = json.load(sys.stdin)
        tool_name = data.get("tool", {}).get("name", "")
        
        # Only intercept agent creation commands
        if tool_name != "CreateAgent":
            sys.exit(0)  # Pass through
        
        # Extract agent specification
        params = data.get("tool", {}).get("parameters", {})
        agent_spec = params.get("specification", {})
        
        if not agent_spec:
            sys.stderr.write("Error: No agent specification provided\n")
            sys.exit(1)
        
        # Validate required fields
        required = ["expertise", "purpose", "responsibilities"]
        missing = [f for f in required if f not in agent_spec]
        if missing:
            sys.stderr.write(f"Error: Missing required fields: {missing}\n")
            sys.exit(1)
        
        # Create and register the agent
        agent_id, definition = create_agent_definition(agent_spec)
        agent_file = register_agent(agent_id, definition)
        
        # Provide feedback
        response = {
            "agent_id": agent_id,
            "definition_path": str(agent_file),
            "status": "created",
            "message": f"Successfully created agent {agent_id}"
        }
        
        sys.stdout.write(json.dumps(response, indent=2) + "\n")
        sys.exit(0)
        
    except Exception as e:
        sys.stderr.write(f"Agent creation failed: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()