# Epic Plan: 00-04 ADK Integration

**Parent Plan:** [../00-implementation-plan-ai-tokentrace.md](../00-implementation-plan-ai-tokentrace.md)

## Overview
This epic focuses on building the integration for tracking token usage within the Agent Development Kit (ADK). This includes creating a global plugin for holistic tracking and granular callbacks for per-agent tracking.

## Implementation Tasks

### Phase 4: ADK Integration (Effort: ~4 hours)
1.  **Define ADK Integration Dependencies**
    -   Description: Add an `[adk]` extra in `pyproject.toml` for the `google-ai-generativelanguage-adk` dependency.
    -   Files to modify: `pyproject.toml`

2.  **Implement Global ADK Plugin**
    -   Description: Create a `TokenTrackingPlugin` for the ADK that hooks into the agent lifecycle to automatically capture token usage for all interactions within a `Runner`.
    -   Files to create: `src/ai_tokentrace/adk.py`

3.  **Implement Granular ADK Callbacks**
    -   Description: Implement a set of callbacks that can be attached to individual agents for more fine-grained token tracking.
    -   Files to modify: `src/ai_tokentrace/adk.py`

4.  **Add Unit Tests for ADK Integration**
    -   Description: Write unit tests for the plugin and callbacks. This will require mocking ADK components like the `Runner` and `Agent`.
    -   Files to create: `tests/test_adk.py`

## Success Criteria
- [ ] The `[adk]` optional dependency is defined in `pyproject.toml`.
- [ ] The `TokenTrackingPlugin` is implemented and functional.
- [ ] Granular callbacks for per-agent tracking are implemented.
- [ ] Unit tests with high coverage exist for all ADK integration components.
