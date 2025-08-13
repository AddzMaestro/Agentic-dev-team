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
