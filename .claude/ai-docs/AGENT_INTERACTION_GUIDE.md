# Agent Interaction Guide

## @-Command System

The TechLead agent serves as the primary interface and can delegate to other agents using @-commands.

### Available Commands

#### Direct Agent Invocation
```
@TechLead: Review the architecture and suggest improvements
@Researcher: Investigate best practices for real-time data processing
@Architect: Design a scalable microservices architecture
@QA: Create comprehensive Playwright tests for user authentication
@SelfHealing: Fix the failing tests in test_user_journey.py
```

#### Multi-Agent Coordination
```
@TechLead @Architect: Collaborate on system design decisions
@QA @SelfHealing: Work together to fix and validate test issues
```

#### Status and Reporting
```
@TechLead status: Show current project status
@all status: Get status from all active agents
@TechLead logs: Show recent activity logs
```

## Message Passing Protocol

### Message Structure
```python
{
    "id": "uuid",
    "timestamp": "ISO-8601",
    "from_agent": "AgentName",
    "to_agent": "AgentName",
    "type": "request|response|notification|error",
    "priority": "low|medium|high|critical",
    "payload": {
        "action": "string",
        "data": {},
        "context": {}
    },
    "thread_id": "uuid",  # For conversation threading
    "requires_response": bool
}
```

### Communication Channels

#### Synchronous Communication
- Direct file writes to `workspace/messages/{agent_name}/inbox/`
- Blocking calls with timeout handling
- Used for critical path operations

#### Asynchronous Communication
- Event-driven notifications via `workspace/events/`
- Non-blocking operations
- Used for parallel processing

#### Broadcast Communication
- System-wide announcements in `workspace/broadcasts/`
- All agents monitor this channel
- Used for global state changes

## Agent Capabilities Matrix

| Agent | Primary Model | Can Invoke | Blocked By | Parallel Safe |
|-------|--------------|------------|------------|---------------|
| TechLead 🔵 | Opus | All agents | None | No |
| Researcher 🟣 | Opus | None | TechLead | Yes |
| Architect 🟢 | Opus | DataEngineer, Backend, Frontend | TechLead | Yes |
| ProductOwner 🟠 | Sonnet | QA | TechLead, Researcher | Yes |
| DataEngineer 🧱 | Sonnet | DataScientist | Architect | Yes |
| DataScientist 🔬 | Sonnet | None | DataEngineer | Yes |
| BackendEngineer 🔴 | Sonnet | None | Architect | Yes |
| FrontendEngineer 🟡 | Sonnet | None | Architect | Yes |
| QA 🟤 | Sonnet | SelfHealing | ProductOwner | No |
| SelfHealing ⚫ | Sonnet | QA | QA | No |
| DeliveryLead 🟩 | Sonnet | All agents | None | No |

## Escalation Protocol

### When to Escalate to TechLead
1. Ambiguous requirements needing clarification
2. Conflicting specifications or constraints
3. Critical errors requiring system-wide changes
4. Resource conflicts between agents
5. Security or compliance concerns

### Escalation Message Format
```python
{
    "type": "escalation",
    "severity": "medium|high|critical",
    "reason": "detailed explanation",
    "attempted_solutions": [],
    "recommended_action": "string",
    "requires_user_input": bool
}
```

## Parallel Execution Rules

### Safe Parallel Operations
- Research and Architecture design
- Backend and Frontend development
- Unit test creation across modules
- Documentation updates
- Log analysis and reporting

### Sequential Requirements
1. Research → Specification
2. Specification → Architecture
3. Architecture → Implementation
4. Implementation → Testing
5. Testing → Self-Healing
6. Self-Healing → Delivery

### Resource Locking
- File-level locking via `.lock` files
- Agent-specific workspace isolation
- Atomic writes for shared resources
- Conflict resolution via TechLead

## Error Handling

### Retry Strategy
```python
retry_config = {
    "max_attempts": 3,
    "initial_delay": 2,  # seconds
    "max_delay": 30,
    "exponential_base": 2,
    "jitter": True
}
```

### Error Categories
1. **Recoverable**: Retry with exponential backoff
2. **Partially Recoverable**: Attempt self-healing
3. **Non-Recoverable**: Escalate to TechLead
4. **Critical**: Halt execution, notify user

## Logging and Transparency

### Log Levels by Agent
- **TechLead**: INFO and above
- **Researcher/Architect**: DEBUG and above
- **Implementation Agents**: INFO and above
- **QA/SelfHealing**: DEBUG and above
- **DeliveryLead**: INFO and above

### Log Retention
- Real-time logs: Last 24 hours
- Archived logs: 30 days
- Error logs: 90 days
- Audit logs: 1 year

### Transparency Requirements
- All decisions logged with rationale
- All agent interactions recorded
- All file modifications tracked
- All test results preserved