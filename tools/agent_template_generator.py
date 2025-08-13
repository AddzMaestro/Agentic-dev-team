#!/usr/bin/env python3
"""
Agent Template Generator
Creates specialized agent definitions based on requirements
"""
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

class AgentTemplateGenerator:
    """Generate agent definitions from templates"""
    
    # Base templates for different agent types
    TEMPLATES = {
        "analyzer": {
            "base_expertise": "analysis and investigation",
            "model": "claude-3-5-sonnet-20241022",
            "responsibilities": [
                "Analyze the specific domain area",
                "Identify patterns and anomalies",
                "Generate actionable insights",
                "Document findings comprehensively"
            ]
        },
        "implementer": {
            "base_expertise": "implementation and coding",
            "model": "claude-3-5-sonnet-20241022",
            "responsibilities": [
                "Implement specified functionality",
                "Follow existing code patterns",
                "Ensure test coverage",
                "Document code changes"
            ]
        },
        "optimizer": {
            "base_expertise": "performance optimization",
            "model": "claude-3-5-sonnet-20241022",
            "responsibilities": [
                "Identify performance bottlenecks",
                "Implement optimization strategies",
                "Measure improvements",
                "Ensure no regression"
            ]
        },
        "integrator": {
            "base_expertise": "system integration",
            "model": "claude-3-5-sonnet-20241022",
            "responsibilities": [
                "Connect disparate systems",
                "Implement API integrations",
                "Handle data transformation",
                "Ensure reliable communication"
            ]
        },
        "validator": {
            "base_expertise": "validation and quality assurance",
            "model": "claude-3-5-sonnet-20241022",
            "responsibilities": [
                "Validate implementation against requirements",
                "Create comprehensive test cases",
                "Ensure edge cases are covered",
                "Report validation results"
            ]
        }
    }
    
    @classmethod
    def generate_agent(
        cls,
        purpose: str,
        expertise: str,
        template_type: str = "implementer",
        specific_requirements: Optional[List[str]] = None,
        files_allowed: Optional[List[str]] = None,
        model_override: Optional[str] = None,
        lifetime_hours: int = 24
    ) -> Dict:
        """Generate a complete agent specification"""
        
        # Get base template
        template = cls.TEMPLATES.get(template_type, cls.TEMPLATES["implementer"])
        
        # Generate unique agent ID
        agent_id = f"dynamic_{expertise.lower().replace(' ', '_')}_{uuid.uuid4().hex[:4]}"
        
        # Combine responsibilities
        responsibilities = template["responsibilities"].copy()
        if specific_requirements:
            responsibilities.extend(specific_requirements)
        
        # Determine files access
        if not files_allowed:
            files_allowed = [
                "./workspace/**",
                f"./workspace/outputs/{agent_id}/**"
            ]
        
        # Create agent specification
        spec = {
            "agent_id": agent_id,
            "purpose": purpose,
            "expertise": f"{expertise} ({template['base_expertise']})",
            "model": model_override or template["model"],
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(hours=lifetime_hours)).isoformat(),
            "template_type": template_type,
            "responsibilities": responsibilities,
            "files_allowed": files_allowed,
            "success_criteria": [
                "Complete assigned task successfully",
                "All tests pass",
                "No regression in existing functionality",
                "Clear documentation of changes"
            ],
            "context_policy": {
                "receive_only_curated": True,
                "max_context_files": 10
            }
        }
        
        return spec
    
    @classmethod
    def create_agent_file(cls, spec: Dict) -> Path:
        """Create the actual agent definition file"""
        
        agent_id = spec["agent_id"]
        
        # Generate markdown definition
        definition = f"""---
name: {agent_id}
description: Dynamic agent for {spec['purpose']}
model: {spec['model']}
created: {spec['created']}
expires: {spec['expires']}
template: {spec['template_type']}
---

# {agent_id}

You are a specialized agent created dynamically for a specific purpose.

## Identity
- **Name**: {agent_id}
- **Expertise**: {spec['expertise']}
- **Purpose**: {spec['purpose']}
- **Model**: {spec['model']}

## Responsibilities
{chr(10).join(f"- {r}" for r in spec['responsibilities'])}

## Context Access
You have access to the following files/directories:
{chr(10).join(f"- `{f}`" for f in spec['files_allowed'])}

## Success Criteria
Your task is complete when:
{chr(10).join(f"- {c}" for c in spec['success_criteria'])}

## Operational Guidelines
1. **Context7 Compliance**: Follow TYPE-first development principles
2. **Testing**: All changes must have corresponding Playwright tests
3. **Documentation**: Document your approach and decisions
4. **Communication**: Report progress and blockers to MetaAgent
5. **Efficiency**: Complete tasks with minimal iterations

## Output Format
Provide structured output that includes:
- **Status**: Current progress and completion state
- **Actions Taken**: List of specific changes made
- **Test Results**: Validation of functionality
- **Next Steps**: If task is incomplete

## Constraints
- Stay within your defined expertise area
- Do not modify files outside your allowed access
- Ensure backward compatibility
- Maintain existing test coverage

## Expiration
This agent expires at: {spec['expires']}
After expiration, the agent definition may be archived or removed.
"""
        
        # Save to file
        project_dir = Path.cwd()
        agent_file = project_dir / ".claude" / "agents" / f"{agent_id}.md"
        agent_file.parent.mkdir(parents=True, exist_ok=True)
        agent_file.write_text(definition)
        
        # Update registry
        registry_file = project_dir / "workspace" / "outputs" / "dynamic_agents.json"
        if registry_file.exists():
            registry = json.loads(registry_file.read_text())
        else:
            registry = {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0.0"
                },
                "agents": {},
                "total_created": 0,
                "active_count": 0,
                "retired_count": 0
            }
        
        registry["agents"][agent_id] = {
            "spec": spec,
            "file_path": str(agent_file),
            "status": "active"
        }
        registry["total_created"] += 1
        registry["active_count"] += 1
        
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        registry_file.write_text(json.dumps(registry, indent=2))
        
        return agent_file

def main():
    """CLI interface for agent generation"""
    if len(sys.argv) < 3:
        print("Usage: agent_template_generator.py <purpose> <expertise> [template_type]")
        print("Template types: analyzer, implementer, optimizer, integrator, validator")
        sys.exit(1)
    
    purpose = sys.argv[1]
    expertise = sys.argv[2]
    template_type = sys.argv[3] if len(sys.argv) > 3 else "implementer"
    
    # Generate agent
    spec = AgentTemplateGenerator.generate_agent(
        purpose=purpose,
        expertise=expertise,
        template_type=template_type
    )
    
    # Create agent file
    agent_file = AgentTemplateGenerator.create_agent_file(spec)
    
    print(f"✅ Created agent: {spec['agent_id']}")
    print(f"   File: {agent_file}")
    print(f"   Expires: {spec['expires']}")
    
    # Output JSON for programmatic use
    print("\n" + json.dumps(spec, indent=2))

if __name__ == "__main__":
    main()