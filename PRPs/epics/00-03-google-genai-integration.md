# Epic Plan: 00-03 `google-genai` Integration

**Parent Plan:** [../00-implementation-plan-ai-tokentrace.md](../00-implementation-plan-ai-tokentrace.md)

## Overview
This epic focuses on building the integration for tracking token usage from direct calls to the `google-genai` library. This will be achieved by creating a wrapper class that mimics the `google-genai` client's interface.

## Implementation Tasks

### Phase 3: `google-genai` Integration (Effort: ~3 hours)
1.  **Implement `TrackedGenaiClient` Wrapper**
    -   Description: Create a wrapper class that mirrors the `google.genai` client interface. It will intercept model calls, extract `usage_metadata`, and export it via a configured `TokenUsageService`.
    -   Files to create: `src/ai_tokentrace/google_genai.py`

2.  **Add Unit Tests for the Wrapper**
    -   Description: Write unit tests to verify that the wrapper correctly calls the underlying `google.genai` client and properly invokes the `TokenUsageService` with the extracted data.
    -   Files to create: `tests/test_google_genai.py`

## Success Criteria
- [ ] The `TrackedGenaiClient` is implemented.
- [ ] The client correctly captures and exports token usage data.
- [ ] Unit tests with high coverage exist for the client wrapper.
