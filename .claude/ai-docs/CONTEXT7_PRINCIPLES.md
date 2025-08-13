# Context7 Principles and Standards
> Reference: https://context7.com/

## Core Philosophy
Context7 represents the optimal balance of **Context × Model × Prompt** for AI engineering excellence.

## The Seven Contexts

### 1. **ROLE** - Who the agent is
- Clear identity and expertise domain
- Specific capabilities and boundaries
- Authority level and decision scope

### 2. **GOAL** - What success looks like
- Measurable objectives
- Clear acceptance criteria
- Aligned with system-wide outcomes

### 3. **CONSTRAINTS** - Boundaries and limitations
- Technical constraints (memory, compute, API limits)
- Business rules and compliance requirements
- Ethical guidelines and safety measures

### 4. **TOOLS** - Available capabilities
- File system operations
- API integrations
- Testing frameworks (Playwright mandatory for QA)
- Communication channels

### 5. **KNOWLEDGE/CONTEXT** - Information access
- Domain expertise requirements
- Access to documentation and specs
- Historical context and decisions
- IDKs (Important Domain Keywords) - maintain 8-12 terms

### 6. **EXAMPLES/TESTS** - Concrete demonstrations
- Input/output examples
- Edge cases and error handling
- Test coverage requirements
- Success/failure patterns

### 7. **OUTPUT FORMAT** - Structured deliverables
- File formats and naming conventions
- Communication protocols
- Logging standards
- Quality gates and validation

## TYPE-First Development

### Types
- Define all data structures explicitly
- Use Pydantic models for validation
- Maintain type hints throughout codebase

### Invariants
- Document assumptions that must always hold
- Implement runtime checks for critical invariants
- Log invariant violations for debugging

### Protocols
- Define clear interfaces between components
- Use abstract base classes for contracts
- Document communication patterns

### Examples
- Provide concrete usage examples
- Include both success and failure cases
- Maintain example-driven documentation

## Agent Orchestration Principles

### Perfect Context Curation
- TechLead agent curates context for all sub-agents
- Each agent receives only necessary information
- Minimize context pollution and confusion

### Model Selection Strategy
- **Opus (claude-3-opus-20240229)**: TechLead, Researcher, Architect
- **Sonnet (claude-3-5-sonnet-20241022)**: All other agents by default
- Dynamic escalation to Opus when complexity demands

### Communication Protocol
- Asynchronous message passing via workspace files
- Structured logging in workspace/logs/
- Clear handoff points between agents
- @-mention system for direct agent invocation

## Quality Gates

### Testing Requirements
- **Unit Tests**: 80% code coverage minimum
- **Integration Tests**: All agent interactions
- **E2E Tests**: Playwright-based user journeys
- **Edge Cases**: Documented and tested
- **Performance**: Response time < 3s for user interactions

### Self-Healing Protocol
1. Run tests → Identify failures
2. Analyze logs → Diagnose root cause
3. Generate patches → Apply fixes
4. Re-test → Validate fixes
5. Maximum 5 self-healing attempts

## IDKs (Important Domain Keywords)
Maintain 8-12 domain-specific terms that represent core concepts:
- Updated by Researcher agent
- Referenced in all specifications
- Used for context alignment
- Stored in workspace/outputs/idks.md

## ULTRA-THINK Framework
Before any major decision or implementation:

### Unknowns
- List what we don't know
- Identify information gaps
- Document assumptions

### Options
- Generate multiple approaches
- Evaluate trade-offs
- Consider alternatives

### Pre-mortem
- Anticipate failure modes
- Identify risks
- Plan mitigations

### Micro-plan
- Break down into atomic tasks
- Define clear dependencies
- Establish success criteria

### Evidence
- Gather supporting data
- Validate assumptions
- Document decisions

## Delivery Standards

### File Organization
```
.claude/           # Claude-specific configuration
  ai-docs/        # AI documentation (this directory)
  agents/         # Agent role specifications
agents/           # Agent YAML configurations
prompts/          # System prompts and templates
specs/            # Specifications and requirements
workspace/        # Runtime artifacts
  research/       # Research findings
  outputs/        # Generated artifacts
  reports/        # Status and analytics
  patches/        # Self-healing patches
  logs/          # Execution logs
tests/           # Test suites
  unit/          # Unit tests
  integration/   # Integration tests
  e2e/           # End-to-end Playwright tests
```

### Logging Standards
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include timestamp, agent, action, outcome
- Separate log files per agent in workspace/logs/

### Success Criteria
- All tests passing (100% green)
- No critical security vulnerabilities
- Performance within defined thresholds
- Documentation complete and accurate
- Code review approved by TechLead agent