# 000 - Shared Patterns Reference

This document contains templates and boilerplate code that specs can reference to avoid repetition.

## Spec Template

Standard template for new specification documents:

```markdown
# XXX - Feature Name

**Purpose:** One-line description of what this does and why

**Requirements:**
- Key functional requirement 1
- Key functional requirement 2
- Important constraints or non-functional requirements

**Design Approach:**
- High-level design decision 1
- High-level design decision 2
- Key technical choices and rationale

**Implementation Notes:**
- Critical implementation details only
- Dependencies or special considerations
- Integration points with existing code
```

## Code Patterns

### Python Tool Structure

Tools in `packages/lsimons-agent/src/lsimons_agent/tools/`:

```python
def tool_name(arg: str) -> str:
    """Tool description for the LLM."""
    # Implementation
    return result
```

### Test Structure

Tests mirror source structure in `packages/*/tests/`:

```python
def test_feature_does_thing():
    result = feature()
    assert result == expected
```
