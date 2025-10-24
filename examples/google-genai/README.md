# AI Tokentrace `google-genai` Examples

This directory contains runnable examples demonstrating how to use the `TrackedGenaiClient` to capture token usage from the `google-genai` library.

## Directory Structure & Available Examples

### Core Interaction Patterns (`core/`)
Basic examples demonstrating the four primary interaction patterns.
*   `sync_generate.py`: Basic synchronous content generation.
*   `async_generate.py`: Asynchronous content generation.
*   `sync_stream.py`: Synchronous streaming of content.
*   `async_stream.py`: Asynchronous streaming of content.

### Models and Features (`models/`)
Examples demonstrating usage with specific models and advanced features.
*   `gemini_2_5_pro.py`: Using the Gemini 2.5 Pro model, including "thinking" capabilities.
*   `gemini_2_5_flash_lite.py`: Using the lightweight Gemini 2.5 Flash Lite model.
*   `gemini_2_5_flash_thinking.py`: Demonstrating thinking tokens with Gemini 2.5 Flash.
*   `caching.py`: Demonstrating context caching and capturing `cached_content_tokens`.
*   `google_search.py`: Demonstrating server-side tool use (Google Search) and capturing `tool_use_prompt_tokens`.

### Image Generation (`images/`)
*   `gemini_2_5_flash_image.py`: Generating images with Gemini 2.5 Flash.
*   `imagen_4.py`: Generating images with Imagen 4.

### Video Generation (`video/`)
*   `veo_3.py`: Generating videos with Veo 3.

### Service Backends (`services/`)
Examples demonstrating how to use different export backends.
*   `file_sync.py` / `file_async.py`: Exporting to JSONL files.
*   `firestore_sync.py` / `firestore_async.py`: Exporting to Google Cloud Firestore.
*   `pubsub_sync.py` / `pubsub_async.py`: Exporting to Google Cloud Pub/Sub.

## Setup

1.  **Install Dependencies:**
    Ensure you have the project's dependencies installed. From the root of the repository, run:
    ```bash
    uv sync
    ```

2.  **Set Your API Key:**
    The examples require a Google AI API key. The recommended way to configure this is to create a `.env` file in the root of this repository.

    Create a file named `.env` and add your key:
    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

    The scripts will automatically load this key.

## Running the Examples

All examples can be run directly as Python modules from the root of the repository using `uv`.

For example, to run the basic synchronous example:
```bash
uv run python -m examples.google-genai.core.sync_generate
```

To run the Google Search example:
```bash
uv run python -m examples.google-genai.models.google_search
```

### A Note on `RuntimeWarning` in Synchronous Examples

When you run the synchronous examples in `core/` (`sync_generate.py`, `sync_stream.py`), you may see a `RuntimeWarning` that a coroutine was "never awaited."

This is expected behavior. The synchronous `LoggingTokenUsageService` uses a "fire-and-forget" mechanism to send logs in the background without blocking the main application. In a short script like these examples, the main script often finishes before the background task has a chance to complete, triggering the warning. In a long-running application, this would not be an issue.