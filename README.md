# ai-tokentrace

`ai-tokentrace` is a Python library designed for GenAI cost observability. Its primary purpose is to provide developers with a clear and transparent way to track token consumption in applications built with Google's Generative AI. This helps manage operational costs, optimize application performance, and reduce "cost anxiety" for developers.

## Features

*   **Automatic Token Tracking:** Seamlessly integrates with the `google-genai` SDK to capture token usage from every API call.
*   **ADK Integration:** Provides a plugin for the Google Agent Development Kit (ADK) to automatically track token usage from agents.
*   **Multiple Backends:** Export token usage data to various destinations, including:
    *   Standard logging (for local development and debugging).
    *   JSONL files (for simple, structured data storage).
    *   Google Cloud Firestore (for scalable, queryable storage).
    *   Google Cloud Pub/Sub (for event-driven processing and analytics).
*   **Async Support:** Fully supports asynchronous applications with non-blocking export operations.
*   **Detailed Metrics:** Captures a comprehensive set of usage metrics, including:
    *   Input and Output tokens
    *   Thinking tokens (for models with reasoning capabilities)
    *   Cached content tokens (when using context caching)
    *   Tool use prompt tokens (for server-side tools like Google Search)
    *   Image and Video generation counts
    *   Rich metadata (model name, method name, agent name, etc.)

## Getting Started

To set up the development environment, you'll need Python 3.9+ and `uv`.

1.  **Install all dependencies and create the virtual environment:**
    ```bash
    uv sync
    ```

`uv` will automatically create a virtual environment in `.venv` if one doesn't exist, and then install all dependencies from `pyproject.toml`.

From here, `uv` will automatically use the virtual environment in this directory. For example, to run a command, use `uv run <command>`.

## Installation

You can install `ai-tokentrace` with specific extras depending on your needs:

```bash
# Basic installation
pip install ai-tokentrace

# With Google Cloud Firestore support
pip install "ai-tokentrace[firestore]"

# With Google Cloud Pub/Sub support
pip install "ai-tokentrace[pubsub]"

# With Google Agent Development Kit (ADK) support
pip install "ai-tokentrace[adk]"
```

## Usage

### Google GenAI SDK

See the [examples/google-genai/](examples/google-genai/) directory for runnable scripts demonstrating how to use `ai-tokentrace` with the `google-genai` SDK.

### Agent Development Kit (ADK)

To track token usage in your ADK agents, use the `TokenTrackingPlugin`:

```python
from google.adk.runners import InMemoryRunner
from ai_tokentrace.adk import TokenTrackingPlugin

# ... define your agent ...

# Create the plugin (uses default logging service if none provided)
tracking_plugin = TokenTrackingPlugin()

# Or configure it with a specific service and options
# from ai_tokentrace.services import FirestoreTokenUsageService
# tracking_plugin = TokenTrackingPlugin(
#     service=FirestoreTokenUsageService(),
#     tracked_agents=["my-critical-agent"] # Optional: only track specific agents
# )

# Add the plugin to your runner
runner = InMemoryRunner(agent=my_agent, plugins=[tracking_plugin])

# Run your agent as usual
result = runner.run(agent_input=...)
```

### Java JRE Setup

Running the integration tests requires a Java JRE to run the Google Cloud emulators. We recommend using [SDKMAN!](https://sdkman.io/) to install and manage Java versions.

1.  **Install SDKMAN!:**
    ```bash
    curl -s "https://get.sdkman.io" | bash
    ```
    Follow the on-screen instructions to complete the installation.

2.  **Install Java:**
    ```bash
    sdk install java
    ```

This will install a suitable version of the Java JRE and make it available in your shell.
