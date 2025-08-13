# ULTRA-THINK Framework

> Deep thinking protocol for complex decision-making and problem-solving

## Overview

ULTRA-THINK is a structured approach to ensure thorough analysis before implementation. Use this framework for:
- Major architectural decisions
- Complex problem solving
- Risk assessment
- Implementation planning
- Debugging difficult issues

## The ULTRA-THINK Process

### U - Unknowns
*Identify what we don't know*

#### Questions to Ask:
- What information is missing?
- What assumptions are we making?
- What are the hidden dependencies?
- What edge cases haven't been considered?
- What could surprise us later?

#### Documentation Format:
```markdown
## Unknowns
1. **[Unknown Category]**: [Description]
   - Impact: [High/Medium/Low]
   - Investigation needed: [Yes/No]
   - Blocking: [Yes/No]
```

### L - Landscape
*Map the solution space*

#### Areas to Explore:
- Existing solutions and patterns
- Available tools and libraries
- Technical constraints
- Business requirements
- Timeline and resources

#### Documentation Format:
```markdown
## Landscape Analysis
- **Current State**: [Description]
- **Desired State**: [Description]
- **Gap Analysis**: [What needs to change]
- **Available Resources**: [List]
- **Constraints**: [List]
```

### T - Trade-offs
*Evaluate options and their implications*

#### Consideration Matrix:
| Option | Pros | Cons | Risk | Effort | Recommendation |
|--------|------|------|------|--------|----------------|
| A | | | L/M/H | S/M/L | Yes/No |
| B | | | L/M/H | S/M/L | Yes/No |

#### Key Trade-offs to Consider:
- Performance vs. Complexity
- Speed vs. Quality
- Flexibility vs. Simplicity
- Cost vs. Features
- Short-term vs. Long-term

### R - Risks
*Anticipate what could go wrong*

#### Risk Assessment:
```markdown
## Risk Register
| Risk | Probability | Impact | Mitigation | Owner | Status |
|------|------------|--------|------------|-------|--------|
| [Risk Description] | L/M/H | L/M/H | [Strategy] | [Agent] | [Status] |
```

#### Pre-mortem Questions:
- What could cause this to fail?
- What are the worst-case scenarios?
- What dependencies could break?
- What assumptions could be wrong?
- How would we recover from failure?

### A - Approach
*Define the implementation strategy*

#### Micro-plan Structure:
```markdown
## Implementation Approach

### Phase 1: Foundation
1. [ ] Task 1 (Owner: Agent, Duration: Xh)
2. [ ] Task 2 (Owner: Agent, Duration: Xh)

### Phase 2: Core Implementation
1. [ ] Task 3 (Owner: Agent, Duration: Xh)
2. [ ] Task 4 (Owner: Agent, Duration: Xh)

### Phase 3: Testing & Validation
1. [ ] Task 5 (Owner: Agent, Duration: Xh)
2. [ ] Task 6 (Owner: Agent, Duration: Xh)

### Dependencies:
- Task 2 depends on Task 1
- Task 4 can run parallel with Task 3

### Success Criteria:
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete
```

## When to Use ULTRA-THINK

### Mandatory Triggers:
- 🔴 **Critical Path Changes**: Modifications affecting core functionality
- 🔴 **Architecture Decisions**: System design choices
- 🔴 **Breaking Changes**: API or interface modifications
- 🔴 **Security Implementations**: Authentication, authorization, encryption
- 🔴 **Data Model Changes**: Database schema modifications

### Recommended Triggers:
- 🟡 **Complex Integrations**: Third-party service connections
- 🟡 **Performance Optimizations**: Algorithm or query improvements
- 🟡 **New Feature Development**: Significant functionality additions
- 🟡 **Debugging Persistent Issues**: Problems lasting > 30 minutes
- 🟡 **Refactoring**: Major code restructuring

## ULTRA-THINK Template

```markdown
# ULTRA-THINK Analysis: [Problem/Decision Name]
Date: [ISO-8601]
Agent: [Agent Name]
Context: [Brief description]

## U - Unknowns
### Known Unknowns
- [ ] Unknown 1: [Description]
- [ ] Unknown 2: [Description]

### Unknown Unknowns (Potential Surprises)
- [ ] Area 1: [Where surprises might emerge]
- [ ] Area 2: [Where surprises might emerge]

## L - Landscape
### Current State
[Description of how things are now]

### Desired State
[Description of the goal]

### Solution Space
- Option A: [Description]
- Option B: [Description]
- Option C: [Description]

## T - Trade-offs
| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Performance | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Complexity | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Time to Implement | 2 days | 1 day | 3 days |
| Maintenance | Low | High | Medium |
| **Recommendation** | No | No | **Yes** |

## R - Risks
### High Priority Risks
1. **Risk**: [Description]
   - **Probability**: High
   - **Impact**: Critical
   - **Mitigation**: [Strategy]

### Medium Priority Risks
[List]

### Low Priority Risks
[List]

## A - Approach
### Micro-plan
1. **Step 1**: [Action] (30 min)
   - Input: [What's needed]
   - Output: [What's produced]
   - Validation: [How to verify]

2. **Step 2**: [Action] (45 min)
   - Input: [What's needed]
   - Output: [What's produced]
   - Validation: [How to verify]

### Success Metrics
- [ ] Metric 1: [Measurable outcome]
- [ ] Metric 2: [Measurable outcome]
- [ ] Metric 3: [Measurable outcome]

### Rollback Plan
1. [Step to reverse changes]
2. [Step to restore previous state]
3. [Verification steps]

## Decision
**Selected Approach**: [Option X]
**Rationale**: [2-3 sentences explaining why]
**Next Action**: [Immediate next step]
```

## Evidence Gathering

### Required Evidence Types:
- **Logs**: System logs, error traces, performance metrics
- **Tests**: Unit test results, integration test outcomes
- **Benchmarks**: Performance comparisons, load test results
- **Research**: Documentation, best practices, case studies
- **Experiments**: Proof of concepts, prototypes

### Evidence Storage:
```
workspace/reports/ultra-think/
├── [timestamp]_[problem_name]/
│   ├── analysis.md          # ULTRA-THINK analysis
│   ├── evidence/            # Supporting materials
│   │   ├── logs/
│   │   ├── benchmarks/
│   │   └── research/
│   └── decision.md         # Final decision record
```

## Review Checklist

Before proceeding with implementation:
- [ ] All unknowns identified or investigated
- [ ] Landscape thoroughly mapped
- [ ] Trade-offs explicitly evaluated
- [ ] Risks assessed and mitigations planned
- [ ] Approach broken down into atomic steps
- [ ] Evidence supports the decision
- [ ] Success criteria clearly defined
- [ ] Rollback plan documented
- [ ] TechLead agent reviewed (if critical)

## Continuous Learning

### Post-Implementation Review:
- Were the unknowns accurately identified?
- Did unexpected issues arise?
- Were the trade-offs correctly evaluated?
- Did the risks materialize?
- Was the approach effective?

### Lessons Learned:
Document insights in `workspace/reports/lessons_learned.md` for future reference.