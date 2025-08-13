# Specification Template
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.
> Based on Context7 principles - https://context7.com/

## High-Level Objective

- [High level goal goes here - what do you want to build?]

## Mid-Level Objectives

- [List of mid-level objectives - what are the steps to achieve the high-level objective?]
- [Each objective should be concrete and measurable]
- [But not too detailed - save details for implementation notes]

## IDKs (Important Domain Keywords)
> Maintain 8-12 domain-specific terms that are crucial for this project

1. **[Term]**: [Brief definition and why it's important]
2. **[Term]**: [Brief definition and why it's important]
3. **[Term]**: [Brief definition and why it's important]
4. **[Term]**: [Brief definition and why it's important]
5. **[Term]**: [Brief definition and why it's important]
6. **[Term]**: [Brief definition and why it's important]
7. **[Term]**: [Brief definition and why it's important]
8. **[Term]**: [Brief definition and why it's important]

## TYPE Artifacts

### Types (Data Structures)
```python
# Define the core data types for this project
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class [CoreType](BaseModel):
    """[Description of this type and its purpose]"""
    field1: str
    field2: Optional[int]
    field3: List[str]
    
class [AnotherType](BaseModel):
    """[Description]"""
    pass
```

### Invariants (What must always be true)
1. **[Invariant Name]**: [Description of what must always hold true]
2. **[Invariant Name]**: [Description of what must always hold true]
3. **[Invariant Name]**: [Description of what must always hold true]

### Protocols (Interfaces and Contracts)
```python
from abc import ABC, abstractmethod

class [ProtocolName](ABC):
    """[Description of this protocol/interface]"""
    
    @abstractmethod
    def method_name(self, param: Type) -> ReturnType:
        """[What this method should do]"""
        pass
```

### Examples (Concrete Usage)
```python
# Example 1: [Scenario description]
example_input = {
    "field": "value"
}
expected_output = {
    "result": "processed"
}

# Example 2: [Error handling scenario]
error_input = {
    "field": None
}
expected_error = ValidationError("field is required")
```

## Implementation Notes
- [Important technical details - what are the important technical details?]
- [Dependencies and requirements - what are the dependencies and requirements?]
- [Coding standards to follow - what are the coding standards to follow?]
- [Performance requirements - what are the performance requirements?]
- [Security considerations - what security measures must be implemented?]
- [Testing strategy - how should this be tested?]

## Context

### Beginning Context
- [List of files that exist at start - what files exist at start?]
- [Current system state - what is already implemented?]
- [Available resources - what tools/libraries are available?]

### Ending Context  
- [List of files that will exist at end - what files will exist at end?]
- [Final system state - what will be implemented?]
- [Success criteria - how do we know we're done?]

## Low-Level Tasks
> Ordered from start to finish. Each task maps 1:1 with a QA test.

### Task 1: [First task - what is the first task?]
```yaml
agent: [Which agent should handle this]
description: [What needs to be done]
acceptance_criteria:
  - [Specific measurable outcome]
  - [Another measurable outcome]
test_mapping: test_[task_name].py::test_[specific_test]
dependencies: []
estimated_duration: [X hours/minutes]

# Execution prompt
prompt: |
  [What prompt would you run to complete this task?]
  [What file do you want to CREATE or UPDATE?]
  [What function do you want to CREATE or UPDATE?]
  [What are details you want to add to drive the code changes?]
```

### Task 2: [Second task - what is the second task?]
```yaml
agent: [Which agent should handle this]
description: [What needs to be done]
acceptance_criteria:
  - [Specific measurable outcome]
test_mapping: test_[task_name].py::test_[specific_test]
dependencies: [Task 1]
estimated_duration: [X hours/minutes]

# Execution prompt
prompt: |
  [Detailed prompt for this task]
```

### Task 3: [Third task - what is the third task?]
```yaml
agent: [Which agent should handle this]
description: [What needs to be done]
acceptance_criteria:
  - [Specific measurable outcome]
test_mapping: test_[task_name].py::test_[specific_test]
dependencies: [Task 1, Task 2]
estimated_duration: [X hours/minutes]

# Execution prompt
prompt: |
  [Detailed prompt for this task]
```

## Test Plan

### Unit Tests
- [ ] Test for [Type/Function 1]
- [ ] Test for [Type/Function 2]
- [ ] Test for [Type/Function 3]

### Integration Tests
- [ ] Test [Component A] integrates with [Component B]
- [ ] Test [API endpoint] handles [scenario]

### End-to-End Tests (Playwright)
- [ ] Test complete user journey for [feature]
- [ ] Test error handling for [edge case]
- [ ] Test performance under [condition]

### Edge Cases
- [ ] [Edge case 1]: [How to test]
- [ ] [Edge case 2]: [How to test]

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | L/M/H | L/M/H | [Mitigation strategy] |

## Success Metrics

- [ ] All tests passing (100% green)
- [ ] Code coverage > 80%
- [ ] Performance: [specific metric]
- [ ] Security: No critical vulnerabilities
- [ ] Documentation: Complete and accurate

## Notes

- [Any additional context or considerations]
- [Links to relevant documentation]
- [Contact points for questions]