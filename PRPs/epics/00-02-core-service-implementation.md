# Epic Plan: 00-02 Core Service Implementation

**Parent Plan:** [../00-implementation-plan-ai-tokentrace.md](../00-implementation-plan-ai-tokentrace.md)

## Overview
This epic focuses on building the core functionality of the `ai-tokentrace` library: the `TokenUsageService`. This includes defining the service interface and implementing all the required backend exporters (Logging, JSONL, Firestore, Pub/Sub).

## Implementation Tasks

### Phase 2: Core Service Implementation (Effort: ~5 hours)
1.  **Define `TokenUsageService` Abstract Base Class**
    -   Description: Create the abstract base class (`TokenUsageService`) with a single abstract method `export(record: TokenUsageRecord)`.
    -   Files to create: `src/ai_tokentrace/services.py`

2.  **Implement `LoggingTokenUsageService`**
    -   Description: Create the default implementation that logs the token usage record as a JSON string to a logger named `ai_tokentrace`.
    -   Files to modify: `src/ai_tokentrace/services.py`

3.  **Implement `JsonlFileTokenUsageService`**
    -   Description: Create the implementation that appends the token usage record as a JSON line to a specified file.
    -   Files to modify: `src/ai_tokentrace/services.py`

4.  **Implement Cloud Backends (`Firestore` and `PubSub`)**
    -   Description: Implement the services for Firestore and Pub/Sub. These will require optional dependencies, which should be added to `pyproject.toml`.
    -   Files to modify: `src/ai_tokentrace/services.py`, `pyproject.toml`

5.  **Implement Fail-Safe Error Handling**
    -   Description: Wrap the export logic in all `TokenUsageService` implementations (except the default logger) in a try/except block. On failure, the error must be logged without raising an exception.
    -   Files to modify: `src/ai_tokentrace/services.py`

6.  **Add Unit Tests for Services**
    -   Description: Write `pytest` unit tests for each `TokenUsageService` implementation, including tests for the fail-safe error handling. Use mocking for the cloud services.
    -   Files to create: `tests/test_services.py`

## Success Criteria
- [ ] The `TokenUsageService` abstract base class is defined.
- [ ] All four backend services (Logging, JSONL, Firestore, Pub/Sub) are implemented.
- [ ] All services have fail-safe error handling.
- [ ] Unit tests with high coverage exist for all services.
