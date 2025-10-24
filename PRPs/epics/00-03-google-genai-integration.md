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

3.  **Implement Automatic `agent_name` Population**
    -   Description: Enhance the `TrackedGenaiClient` to automatically populate the `agent_name` field in the `TokenUsageRecord` using the running script's filename as a default, while allowing user overrides.
    -   Files to modify: `src/ai_tokentrace/google_genai.py`

### Phase 4: Examples and Documentation (Effort: ~4 hours)
1.  **Create Examples Directory and README**
    -   Description: Create a top-level `examples/google-genai/` directory with a `README.md` explaining how to set up the environment (e.g., `.env` file for `GEMINI_API_KEY`) and run the example scripts.

2.  **Add Core Generation Examples**
    -   Description: Create runnable scripts demonstrating the four primary interaction patterns: sync generate, sync stream, async generate, and async stream. These examples will use the `LoggingTokenUsageService` to print token usage to the console.

3.  **Add Model-Specific Examples**
    -   Description: Create a set of scripts to demonstrate usage with different models and configurations to highlight the library's ability to capture varied token types (e.g., thinking tokens).
    -   Examples to include:
        -   Gemini 2.5 Pro with default reasoning tokens.
        -   Gemini 2.5 Pro with a custom `thinking_budget`.
        -   Gemini 2.5 Flash with and without a `thinking_budget`.
        -   Gemini 2.5 Flash Lite.

4.  **Add Image Generation Examples**
    -   Description: Create scripts demonstrating how the wrapper handles image generation models.
    -   Examples to include:
        -   Gemini 2.5 Flash Image.
        -   Imagen 4.

5.  **Add Service-Specific Examples**
    -   Description: Create scripts that demonstrate how to configure and use the `TrackedGenaiClient` with each of the available backend services.
    -   Examples to include:
        -   `FileTokenUsageService`
        -   `FirestoreTokenUsageService` (using the emulator)
        -   `PubSubTokenUsageService` (using the emulator)

## Success Criteria
- [x] The `TrackedGenaiClient` is implemented.
- [x] The client correctly captures and exports token usage data.
- [x] Unit tests with high coverage exist for the client wrapper.
- [x] The `agent_name` is automatically populated by default.
- [x] A comprehensive `examples/google-genai/` directory exists with runnable scripts.
- [x] Examples cover sync, async, streaming, and various model configurations.
- [x] Examples demonstrate usage with all available `TokenUsageService` backends.
- [x] The project's main `README.md` is updated to point to the new examples.
