#!/usr/bin/env python3
"""
Agent Registry for Claude Code
Registers all agents so they appear in /agents command
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

class AgentRegistry:
    """Registry for all Context7 agents"""
    
    # Agent definitions with color codes and models
    AGENTS = {
        "TechLead": {
            "emoji": "🔵",
            "color": "\033[34m",  # Blue
            "model": "claude-3-opus-20240229",
            "priority": 1,
            "can_invoke": ["all"],
            "parallel": False,
            "description": "Primary orchestrator and user interface"
        },
        "Researcher": {
            "emoji": "🟣", 
            "color": "\033[35m",  # Purple
            "model": "claude-3-opus-20240229",
            "priority": 2,
            "can_invoke": [],
            "parallel": True,
            "description": "Domain investigation and IDK management"
        },
        "Architect": {
            "emoji": "🟢",
            "color": "\033[32m",  # Green
            "model": "claude-3-opus-20240229",
            "priority": 3,
            "can_invoke": ["DataEngineer", "BackendEngineer", "FrontendEngineer"],
            "parallel": True,
            "description": "System design and TYPE definitions"
        },
        "ProductOwner": {
            "emoji": "🟠",
            "color": "\033[33m",  # Orange/Yellow
            "model": "claude-3-5-sonnet-20241022",
            "priority": 4,
            "can_invoke": ["QA"],
            "parallel": True,
            "description": "User stories and requirements"
        },
        "DataEngineer": {
            "emoji": "🧱",
            "color": "\033[31m",  # Red (brick-like)
            "model": "claude-3-5-sonnet-20241022",
            "priority": 5,
            "can_invoke": ["DataScientist"],
            "parallel": True,
            "description": "Data pipelines and ETL"
        },
        "DataScientist": {
            "emoji": "🔬",
            "color": "\033[36m",  # Cyan
            "model": "claude-3-5-sonnet-20241022",
            "priority": 6,
            "can_invoke": [],
            "parallel": True,
            "description": "Analytics and predictions"
        },
        "BackendEngineer": {
            "emoji": "🔴",
            "color": "\033[91m",  # Bright Red
            "model": "claude-3-5-sonnet-20241022",
            "priority": 7,
            "can_invoke": [],
            "parallel": True,
            "description": "API and server implementation"
        },
        "FrontendEngineer": {
            "emoji": "🟡",
            "color": "\033[93m",  # Bright Yellow
            "model": "claude-3-5-sonnet-20241022",
            "priority": 8,
            "can_invoke": [],
            "parallel": True,
            "description": "UI and dashboard"
        },
        "QA": {
            "emoji": "🟤",
            "color": "\033[33m",  # Brown
            "model": "claude-3-5-sonnet-20241022",
            "priority": 9,
            "can_invoke": ["SelfHealing"],
            "parallel": False,
            "description": "Playwright testing"
        },
        "SelfHealing": {
            "emoji": "⚫",
            "color": "\033[90m",  # Dark Gray
            "model": "claude-3-5-sonnet-20241022",
            "priority": 10,
            "can_invoke": ["QA"],
            "parallel": False,
            "description": "Automatic fix generation"
        },
        "DeliveryLead": {
            "emoji": "🟩",
            "color": "\033[92m",  # Bright Green
            "model": "claude-3-5-sonnet-20241022",
            "priority": 11,
            "can_invoke": ["all"],
            "parallel": False,
            "description": "Release management"
        }
    }
    
    @classmethod
    def get_all_agents(cls) -> Dict[str, Any]:
        """Return all registered agents"""
        return cls.AGENTS
    
    @classmethod
    def get_agent(cls, name: str) -> Dict[str, Any]:
        """Get a specific agent by name"""
        return cls.AGENTS.get(name, {})
    
    @classmethod
    def display_agents(cls) -> str:
        """Display all agents in a formatted way"""
        NC = "\033[0m"  # No Color
        output = []
        output.append("\n" + "="*60)
        output.append("📋 REGISTERED AGENTS (Context7 System)")
        output.append("="*60 + "\n")
        
        for name, agent in sorted(cls.AGENTS.items(), key=lambda x: x[1]["priority"]):
            color = agent["color"]
            emoji = agent["emoji"]
            model = "Opus" if "opus" in agent["model"] else "Sonnet"
            
            # Main agent line
            output.append(f"{color}{emoji} {name} ({model}){NC}")
            output.append(f"   ├── {agent['description']}")
            
            # Can invoke
            if agent["can_invoke"]:
                if agent["can_invoke"] == ["all"]:
                    output.append(f"   ├── Can invoke: ALL agents")
                else:
                    output.append(f"   ├── Can invoke: {', '.join(agent['can_invoke'])}")
            
            # Parallel execution
            output.append(f"   └── Parallel: {'✓' if agent['parallel'] else '✗'}")
            output.append("")
        
        output.append("="*60)
        output.append(f"Total Agents: {len(cls.AGENTS)}")
        output.append(f"Opus Models: {sum(1 for a in cls.AGENTS.values() if 'opus' in a['model'])}")
        output.append(f"Sonnet Models: {sum(1 for a in cls.AGENTS.values() if 'sonnet' in a['model'])}")
        output.append("="*60 + "\n")
        
        return "\n".join(output)
    
    @classmethod
    def export_for_claude(cls) -> Dict[str, Any]:
        """Export agent configuration for Claude Code"""
        return {
            "agents": cls.AGENTS,
            "invocation_map": {
                f"@{name}": {
                    "agent": name,
                    "emoji": agent["emoji"],
                    "model": agent["model"]
                }
                for name, agent in cls.AGENTS.items()
            },
            "execution_order": sorted(
                cls.AGENTS.keys(), 
                key=lambda x: cls.AGENTS[x]["priority"]
            )
        }
    
    @classmethod
    def save_registry(cls, path: str = ".claude/agent_registry.json"):
        """Save agent registry to file"""
        registry_data = cls.export_for_claude()
        Path(path).parent.mkdir(exist_ok=True)
        
        with open(path, "w") as f:
            json.dump(registry_data, f, indent=2)
        
        return path

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        print(AgentRegistry.display_agents())
    elif len(sys.argv) > 1 and sys.argv[1] == "save":
        path = AgentRegistry.save_registry()
        print(f"✅ Agent registry saved to {path}")
    else:
        # Default: show agents
        print(AgentRegistry.display_agents())