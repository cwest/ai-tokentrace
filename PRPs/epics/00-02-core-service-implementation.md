# Epic Plan: 00-02 Core Service Implementation

**Parent Plan:** [../00-implementation-plan-ai-tokentrace.md](../00-implementation-plan-ai-tokentrace.md)

## Overview
This epic focuses on building the core functionality of the `ai-tokentrace` library: the `TokenUsageService`. This includes defining the service interface and implementing all the required backend exporters (Logging, JSONL, Firestore, Pub/Sub) with a robust, non-blocking, dual sync/async API.

## Implementation Tasks

### Phase 2: Core Service Implementation (Effort: ~9 hours)
1.  **Define `TokenUsageService` Abstract Base Class**
    -   Description: Create the abstract base class (`TokenUsageService`) with a core `async def aexport()` method and a synchronous `export()` wrapper.
    -   Files to create: `src/ai_tokentrace/services.py`

2.  **Implement Dual Sync/Async API Helper**
    -   Description: Create a helper utility that manages a background event loop on a separate thread. This will allow synchronous methods to call async methods in a non-blocking, "fire-and-forget" manner.
    -   Files to create: `src/ai_tokentrace/async_utils.py`

3.  **Implement `LoggingTokenUsageService`**
    -   Description: Create the default implementation that logs the token usage record as a JSON string to a logger named `ai_tokentrace`.
    -   Files to modify: `src/ai_tokentrace/services.py`

4.  **Implement `JsonlFileTokenUsageService`**
    -   Description: Create the implementation that appends the token usage record as a JSON line to a specified file using `aiofiles`.
    -   Files to modify: `src/ai_tokentrace/services.py`

5.  **Implement Cloud Backends (`Firestore` and `PubSub`)**
    -   Description: Implement the services for Firestore and Pub/Sub using their `AsyncClient` libraries. Use a lazy-import pattern for the optional dependencies.
    -   Files to modify: `src/ai_tokentrace/services.py`, `pyproject.toml`

6.  **Implement Fail-Safe Error Handling**
    -   Description: Wrap the export logic in all `aexport` implementations in a try/except block. On failure, the error must be logged without raising an exception.
    -   Files to modify: `src/ai_tokentrace/services.py`

7.  **Add Unit Tests for Services**
    -   Description: Write fast `pytest` unit tests for each service. For cloud services, use mocks to test internal logic and error handling in isolation.
    -   Files to create: `tests/test_services.py`

8.  **Configure Emulators for Integration Testing**
    -   Description: Create a `Procfile.dev` to define the exact `gcloud` commands for running the emulators. **Note:** The emulators require a Java 8+ JRE. The Pub/Sub emulator requires the `beta` component. Create a corresponding `.env.dev` to configure the emulator hosts for the client libraries.
        ```Procfile.dev
        firestore: gcloud emulators firestore start --project=ai-tokentrace-local --host-port=localhost:8080
        pubsub: gcloud beta emulators pubsub start --project=ai-tokentrace-local --host-port=localhost:8085
        ```
    -   Files to create: `Procfile.dev`, `.env.dev`

9.  **Orchestrate Integration Test Suite**
    -   Description: Add `honcho` as a dev dependency. Create a `poe` task (`test:integration`) that uses `honcho` to start the emulators and run the integration test suite, ensuring emulators are terminated afterward.
    -   Files to modify: `pyproject.toml`

10. **Add Integration Tests for Cloud Services**
    -   Description: Write `pytest` integration tests for the Firestore and Pub/Sub services that run against the local emulators to verify real-world behavior.
    -   Files to create: `tests/test_services_integration.py`

11. **Update README with Java Setup Guide**
    -   Description: Update the `README.md` to include a guide for setting up a Java JRE. Recommend `SDKMAN!` as the preferred tool for managing Java installations.
    -   Files to modify: `README.md`

## Success Criteria
- [ ] The `TokenUsageService` provides both a sync `export` and an async `aexport` method.
- [ ] A background event loop manager is implemented for the sync API.
- [ ] All four backend services (Logging, JSONL, Firestore, Pub/Sub) are implemented.
- [ ] All services have fail-safe error handling.
- [ ] Unit tests with mocks exist for all services.
- [ ] `Procfile.dev` and `.env.dev` are configured to run the emulators.
- [ ] A `poe` task (`test:integration`) is configured to orchestrate the test suite.
- [ ] Integration tests exist for cloud services, running against the local emulators.
- [ ] `README.md` is updated with Java installation instructions.
