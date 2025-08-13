#!/usr/bin/env python3
"""
Zero-Error Autonomous Orchestrator
Implements Context7 principles with multi-agent coordination
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import logging
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

import click
import yaml
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(
    "workspace/logs/orchestrator.log",
    rotation="1 day",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level=os.getenv("LOG_LEVEL", "INFO")
)
logger.add(sys.stderr, level="INFO")

console = Console()

# ============================================================================
# Data Models
# ============================================================================

class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    ESCALATION = "escalation"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    COMPLETED = "completed"

class AgentMessage(BaseModel):
    """Message structure for inter-agent communication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    from_agent: str
    to_agent: str
    type: MessageType
    priority: Priority = Priority.MEDIUM
    payload: Dict[str, Any]
    thread_id: Optional[str] = None
    requires_response: bool = False
    context: Optional[Dict[str, Any]] = None

@dataclass
class AgentConfig:
    """Configuration for an agent"""
    name: str
    emoji: str
    model: str
    role_file: Path
    context_policy: Dict[str, Any]
    files_allowed: List[str]
    can_invoke: List[str] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)
    parallel_safe: bool = True

# ============================================================================
# Message Queue System
# ============================================================================

class MessageQueue:
    """File-based message queue for agent communication"""
    
    def __init__(self, base_path: Path = Path("workspace/messages")):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    async def send(self, message: AgentMessage):
        """Send a message to an agent's inbox"""
        inbox = self.base_path / message.to_agent / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        
        message_file = inbox / f"{message.timestamp.isoformat()}_{message.id}.json"
        message_file.write_text(message.model_dump_json(indent=2))
        
        logger.info(f"Message {message.id} sent from {message.from_agent} to {message.to_agent}")
        
    async def receive(self, agent_name: str) -> Optional[AgentMessage]:
        """Receive the next message for an agent"""
        inbox = self.base_path / agent_name / "inbox"
        if not inbox.exists():
            return None
            
        messages = sorted(inbox.glob("*.json"))
        if not messages:
            return None
            
        message_file = messages[0]
        message_data = json.loads(message_file.read_text())
        message = AgentMessage(**message_data)
        
        # Move to processed
        processed = self.base_path / agent_name / "processed"
        processed.mkdir(parents=True, exist_ok=True)
        message_file.rename(processed / message_file.name)
        
        return message
        
    async def broadcast(self, message: AgentMessage):
        """Broadcast a message to all agents"""
        broadcast_dir = self.base_path / "broadcasts"
        broadcast_dir.mkdir(parents=True, exist_ok=True)
        
        message_file = broadcast_dir / f"{message.timestamp.isoformat()}_{message.id}.json"
        message_file.write_text(message.model_dump_json(indent=2))
        
        logger.info(f"Broadcast message {message.id} from {message.from_agent}")

# ============================================================================
# Agent Base Class
# ============================================================================

class Agent:
    """Base class for all agents"""
    
    def __init__(self, config: AgentConfig, anthropic_client: AsyncAnthropic):
        self.config = config
        self.client = anthropic_client
        self.status = AgentStatus.IDLE
        self.message_queue = MessageQueue()
        self.workspace = Path("workspace")
        self.logs_dir = self.workspace / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup agent-specific logger
        self.logger = logger.bind(agent=config.name)
        self.log_file = self.logs_dir / f"{config.name.lower().replace(' ', '_')}.log"
        
    async def load_context(self) -> str:
        """Load agent's role and context"""
        role_content = self.config.role_file.read_text() if self.config.role_file.exists() else ""
        
        # Load allowed files
        context_parts = [role_content]
        for pattern in self.config.files_allowed:
            files = Path(".").glob(pattern)
            for file in files:
                if file.exists() and file.is_file():
                    context_parts.append(f"\n# File: {file}\n{file.read_text()}")
                    
        return "\n\n".join(context_parts)
        
    @retry(
        stop=stop_after_attempt(int(os.getenv("MAX_RETRIES", "3"))),
        wait=wait_exponential(multiplier=2, min=2, max=30)
    )
    async def invoke_llm(self, prompt: str, context: str) -> str:
        """Invoke the LLM with retry logic"""
        try:
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=4000,
                temperature=0.3,
                system=context,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"LLM invocation failed: {e}")
            raise
            
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process an incoming message"""
        self.status = AgentStatus.BUSY
        self.logger.info(f"Processing message {message.id} from {message.from_agent}")
        
        try:
            context = await self.load_context()
            
            # Add message context
            prompt = f"""
            Message Type: {message.type}
            Priority: {message.priority}
            From: {message.from_agent}
            
            Payload:
            {json.dumps(message.payload, indent=2)}
            
            Context:
            {json.dumps(message.context or {}, indent=2)}
            
            Please process this message according to your role and respond appropriately.
            """
            
            response_text = await self.invoke_llm(prompt, context)
            
            # Create response message if required
            if message.requires_response:
                response = AgentMessage(
                    from_agent=self.config.name,
                    to_agent=message.from_agent,
                    type=MessageType.RESPONSE,
                    priority=message.priority,
                    payload={"response": response_text},
                    thread_id=message.thread_id or message.id,
                    requires_response=False
                )
                
                await self.message_queue.send(response)
                return response
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self.status = AgentStatus.ERROR
            
            # Send error message
            error_msg = AgentMessage(
                from_agent=self.config.name,
                to_agent=message.from_agent,
                type=MessageType.ERROR,
                priority=Priority.HIGH,
                payload={"error": str(e)},
                thread_id=message.thread_id
            )
            await self.message_queue.send(error_msg)
            
        finally:
            self.status = AgentStatus.IDLE
            
        return None
        
    async def run(self):
        """Main agent loop"""
        self.logger.info(f"{self.config.emoji} {self.config.name} started")
        
        while True:
            try:
                # Check for messages
                message = await self.message_queue.receive(self.config.name)
                if message:
                    await self.process_message(message)
                else:
                    await asyncio.sleep(1)  # No messages, wait
                    
            except KeyboardInterrupt:
                self.logger.info(f"{self.config.name} shutting down")
                break
            except Exception as e:
                self.logger.error(f"Agent error: {e}")
                self.status = AgentStatus.ERROR
                await asyncio.sleep(5)  # Wait before retrying

# ============================================================================
# Specialized Agents
# ============================================================================

class TechLeadAgent(Agent):
    """TechLead agent with special user interaction capabilities"""
    
    async def handle_user_command(self, command: str) -> str:
        """Handle @TechLead commands from user"""
        self.logger.info(f"Handling user command: {command}")
        
        # Parse @-mentions
        mentions = []
        words = command.split()
        for word in words:
            if word.startswith("@") and word[1:] != "TechLead":
                mentions.append(word[1:].rstrip(":"))
                
        if mentions:
            # Delegate to other agents
            for agent_name in mentions:
                message = AgentMessage(
                    from_agent="TechLead",
                    to_agent=agent_name,
                    type=MessageType.REQUEST,
                    priority=Priority.HIGH,
                    payload={"command": command},
                    requires_response=True
                )
                await self.message_queue.send(message)
                
        # Process with TechLead logic
        context = await self.load_context()
        response = await self.invoke_llm(command, context)
        
        return response

# ============================================================================
# Orchestrator
# ============================================================================

class Orchestrator:
    """Main orchestrator for managing all agents"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.configs: Dict[str, AgentConfig] = {}
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.message_queue = MessageQueue()
        self.parallel_execution = os.getenv("PARALLEL_EXECUTION", "true").lower() == "true"
        
    def load_agent_configs(self):
        """Load agent configurations from YAML files"""
        agent_dir = Path("agents")
        if not agent_dir.exists():
            logger.error("Agents directory not found")
            return
            
        for yaml_file in agent_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                config_data = yaml.safe_load(f)
                
            # Resolve environment variables in model name
            model = config_data.get("model", "")
            if model.startswith("${") and model.endswith("}"):
                env_var = model[2:-1]
                model = os.getenv(env_var, "claude-3-5-sonnet-20241022")
                
            config = AgentConfig(
                name=config_data["name"],
                emoji=config_data.get("emoji", "🤖"),
                model=model,
                role_file=Path(f".claude/agents/{yaml_file.stem}.md"),
                context_policy=config_data.get("context_policy", {}),
                files_allowed=config_data.get("files_allowed", []),
                can_invoke=config_data.get("can_invoke", []),
                blocked_by=config_data.get("blocked_by", []),
                parallel_safe=config_data.get("parallel_safe", True)
            )
            
            self.configs[config.name] = config
            logger.info(f"Loaded config for {config.name}")
            
    def create_agents(self):
        """Create agent instances"""
        for name, config in self.configs.items():
            if "TechLead" in name:
                agent = TechLeadAgent(config, self.client)
            else:
                agent = Agent(config, self.client)
                
            self.agents[name] = agent
            logger.info(f"Created agent: {config.emoji} {name}")
            
    async def execute_workflow(self, problem_file: Path = Path("inputs/problem.md")):
        """Execute the main workflow"""
        console.print("[bold green]Starting Zero-Error Autonomous Workflow[/bold green]")
        
        # Read problem statement
        problem = problem_file.read_text() if problem_file.exists() else ""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Phase -1: MetaAgent Orchestration (if available)
            meta_agent_yaml = Path("agents/meta_agent.yaml")
            if meta_agent_yaml.exists():
                task = progress.add_task("🔵 MetaAgent: Creating task graph and context map...", total=1)
                try:
                    # MetaAgent creates the execution plan
                    await self.run_agent_task("MetaAgent", {
                        "action": "orchestrate",
                        "problem": problem,
                        "mode": "autonomous",
                        "outputs": [
                            "workspace/outputs/task_graph.json",
                            "workspace/outputs/context_map.json"
                        ]
                    })
                    progress.update(task, completed=1)
                    logger.info("MetaAgent orchestration complete")
                except Exception as e:
                    logger.warning(f"MetaAgent orchestration skipped: {e}")
                    progress.update(task, completed=1)
            
            # Phase 0: Research
            task = progress.add_task("🟣 Researcher: Investigating problem space...", total=1)
            await self.run_agent_task("Researcher", {
                "action": "research",
                "problem": problem
            })
            progress.update(task, completed=1)
            
            # Phase 1: Specification
            task = progress.add_task("🔵 TechLead: Creating specification...", total=1)
            await self.run_agent_task("TechLead", {
                "action": "create_spec",
                "research": self.read_workspace_file("research/summary.md"),
                "problem": problem
            })
            progress.update(task, completed=1)
            
            # Phase 2: Parallel Planning
            if self.parallel_execution:
                tasks = []
                
                task_po = progress.add_task("🟠 ProductOwner: Creating backlog...", total=1)
                tasks.append(self.run_agent_task("ProductOwner", {
                    "action": "create_backlog",
                    "spec": self.read_workspace_file("../specs/PRIMARY_SPEC.md")
                }))
                
                task_arch = progress.add_task("🟢 Architect: Designing system...", total=1)
                tasks.append(self.run_agent_task("Architect", {
                    "action": "design",
                    "spec": self.read_workspace_file("../specs/PRIMARY_SPEC.md")
                }))
                
                await asyncio.gather(*tasks)
                progress.update(task_po, completed=1)
                progress.update(task_arch, completed=1)
                
            # Phase 3: Implementation (if needed)
            # This would be expanded based on architecture results
            
            # Phase 4: Testing
            task = progress.add_task("🟤 QA: Running Playwright tests...", total=1)
            test_result = await self.run_agent_task("QA", {
                "action": "test",
                "test_plan": "e2e"
            })
            progress.update(task, completed=1)
            
            # Phase 5: Self-Healing (if tests fail)
            if not self.check_tests_passing():
                task = progress.add_task("⚫ SelfHealing: Fixing failures...", total=5)
                for attempt in range(5):
                    await self.run_agent_task("SelfHealing", {
                        "action": "fix",
                        "test_results": self.read_workspace_file("reports/last_test_result.json")
                    })
                    progress.update(task, advance=1)
                    
                    if self.check_tests_passing():
                        break
                        
            # Phase 6: Delivery
            task = progress.add_task("🟩 DeliveryLead: Finalizing delivery...", total=1)
            await self.run_agent_task("DeliveryLead", {
                "action": "finalize",
                "test_results": self.read_workspace_file("reports/last_test_result.json")
            })
            progress.update(task, completed=1)
            
        console.print("[bold green]✅ Workflow completed![/bold green]")
        
    async def run_agent_task(self, agent_name: str, payload: Dict[str, Any]):
        """Run a specific agent task"""
        if agent_name not in self.agents:
            logger.error(f"Agent {agent_name} not found")
            return
            
        message = AgentMessage(
            from_agent="Orchestrator",
            to_agent=agent_name,
            type=MessageType.REQUEST,
            priority=Priority.HIGH,
            payload=payload,
            requires_response=True
        )
        
        await self.message_queue.send(message)
        
        # Wait for response (simplified - in production would use proper async waiting)
        await asyncio.sleep(2)
        
    def read_workspace_file(self, path: str) -> str:
        """Read a file from workspace"""
        file_path = Path("workspace") / path
        return file_path.read_text() if file_path.exists() else ""
        
    def check_tests_passing(self) -> bool:
        """Check if all tests are passing"""
        result_file = Path("workspace/reports/last_test_result.json")
        if not result_file.exists():
            return False
            
        try:
            result = json.loads(result_file.read_text())
            return result.get("passed", 0) == result.get("total", 1)
        except:
            return False
            
    async def interactive_mode(self):
        """Run in interactive mode with @-commands"""
        console.print("[bold]Interactive Mode - Use @TechLead to interact[/bold]")
        
        techlead = self.agents.get("TechLead")
        if not techlead:
            console.print("[red]TechLead agent not found![/red]")
            return
            
        while True:
            try:
                command = console.input("[cyan]You>[/cyan] ")
                
                if command.lower() in ["exit", "quit"]:
                    break
                    
                if command.startswith("@"):
                    response = await techlead.handle_user_command(command)
                    console.print(f"[green]TechLead>[/green] {response}")
                else:
                    console.print("[yellow]Use @TechLead to interact with the system[/yellow]")
                    
            except KeyboardInterrupt:
                break
                
        console.print("[bold]Goodbye![/bold]")

# ============================================================================
# CLI Interface
# ============================================================================

@click.command()
@click.option("--mode", type=click.Choice(["autonomous", "interactive", "test"]), 
              default="autonomous", help="Execution mode")
@click.option("--base-url", default="http://localhost:3000", 
              help="Base URL for testing")
@click.option("--problem", type=click.Path(exists=True), 
              default="inputs/problem.md", help="Problem statement file")
def main(mode: str, base_url: str, problem: str):
    """Zero-Error Autonomous Orchestrator"""
    
    # Set base URL in environment
    os.environ["BASE_URL"] = base_url
    
    # Create orchestrator
    orchestrator = Orchestrator()
    orchestrator.load_agent_configs()
    orchestrator.create_agents()
    
    # Run based on mode
    if mode == "autonomous":
        asyncio.run(orchestrator.execute_workflow(Path(problem)))
    elif mode == "interactive":
        asyncio.run(orchestrator.interactive_mode())
    elif mode == "test":
        # Run test suite
        os.system("pytest tests/")

if __name__ == "__main__":
    main()