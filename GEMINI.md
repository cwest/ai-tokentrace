# Gemini Code Assistant Context

## Project Overview

`ai-tokentrace` is a Python library designed for GenAI cost observability. Its
primary purpose is to provide developers with a clear and transparent way to
track token consumption in applications built with Google's Generative AI. This
helps manage operational costs, optimize application performance, and reduce
"cost anxiety" for developers.

The library is built as a standalone, distributable package with minimal
dependencies, primarily `google-genai` and `pydantic`. It supports Python 3.9
and newer.

## Building and Running

The project uses `uv` for environment and dependency management, and
`poethepoet` as a task runner.

- **Setup:** To set up the development environment, create a virtual environment
  and install all dependencies:

  ```bash
  uv sync
  ```

  `uv` will automatically create a `.venv` directory if one doesn't exist and
  manage it for subsequent commands.

- **Running Tests:** The test suite is run using `pytest` via the `poe` task
  runner:

  ```bash
  uv run poe test
  ```

- **Linting and Formatting:** Code quality is maintained with `ruff`, also run
  via `poe`:

  ```bash
  # Check for linting errors
  uv run poe lint

  # Format the code
  uv run poe format
  ```

## Development Conventions

- **Dependency Management:** All project metadata and dependencies are managed
  in `pyproject.toml`.
- **Code Quality:** The project uses `ruff` for both linting and formatting.
  Pre-commit hooks are configured in `.pre-commit-config.yaml` to automatically
  enforce code style and add license headers.
- **Testing:** The project uses `pytest` for unit testing. Tests are located in
  the `tests/` directory.
- **Data Modeling:** Pydantic is used for data modeling and validation to ensure
  a clear and reliable schema for all exported data.
- **Commit Messages:** All commit messages must adhere to the Conventional
  Commits specification.

## Gemini Added Memories

### Google GenAI SDK Usage Guide (Effective 2025)

This is a comprehensive guide based on the official `codegen_instructions.md`
for the `google-genai` Python library.

#### 1. Core Principles

- **Primary SDK:** The official and only supported Python package is
  `google-genai`. The `google-generativeai` package is **deprecated** and must
  not be used.
- **Installation:** `uv pip install google-genai`
- **Import Convention:** `from google import genai`
- **Authentication:** The `GEMINI_API_KEY` environment variable is automatically
  used.
- **Client Initialization:** Always start with `client = genai.Client()`.

#### 2. Common Usage Patterns

**Basic Inference (Text & Multimodal)**

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a story about a magic backpack."
)
print(response.text)
```

**Streaming Content**

```python
from google import genai

client = genai.Client()
stream = client.models.generate_content_stream(
    model="gemini-2.5-pro",
    contents="Write a long story about a magic backpack."
)
for chunk in stream:
    print(chunk.text, end="")
```

**Multi-turn Chat**

```python
from google import genai

client = genai.Client()
chat = client.chats.create(model="gemini-1.5-pro-latest")

response = chat.send_message("Hello! Tell me a fact about the earth.")
print(response.text)

response = chat.send_message("How far is it from the sun?")
print(response.text)
```

**Image Generation**

*Multimodal Model (e.g., Gemini 2.5 Flash Image)*
```python
from google import genai
from PIL import Image
from io import BytesIO

client = genai.Client()
# Uses generate_content; images are in the response parts
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A watercolor painting of a hamster wearing a wizard hat."
)
for part in response.candidates[0].content.parts:
    if part.inline_data:
        image = Image.open(BytesIO(part.inline_data.data))
```

*Pure Image Model (e.g., Imagen 4)*
```python
from google import genai

client = genai.Client()
# Uses generate_images; images are in response.generated_images
response = client.models.generate_images(
    model="imagen-4.0-generate-001",
    prompt="A photorealistic landscape of a futuristic city."
)
# response.generated_images contains the image data
```

**Video Generation**

```python
from google import genai

client = genai.Client()
response = client.models.generate_videos(
    model="gemini-2.5-pro",
    prompt="A fluffy white cat chasing a red laser dot on a wooden floor."
)
# response.videos contains generated video data
```

#### 3. Advanced Configuration

**Generation Config** Use `types.GenerateContentConfig` for detailed control.

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="...",
    config=types.GenerateContentConfig(
        temperature=1.0,
        max_output_tokens=1024,
        system_instruction="You are a helpful coding assistant."
    )
)
```

**Thinking Models & Token Limits** Enable "thinking" for supported models (like
Gemini 2.5 Pro/Flash) and control output length.

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Solve this complex riddle...",
    config=types.GenerateContentConfig(
        max_output_tokens=1024, # Limit standard output tokens
        thinking_config=types.ThinkingConfig(
            include_thoughts=True, # Request thinking process in response
            thinking_budget=2048   # Set a separate budget for thinking tokens
        )
    )
)
# Thinking tokens are tracked separately in usage_metadata.thoughts_token_count
```

**Structured Outputs with Pydantic** Force the model to return JSON matching a
Pydantic schema.

```python
from google import genai
from pydantic import BaseModel

class City(BaseModel):
    name: str
    population: int
    country: str

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Give me information about Tokyo.",
    response_schema=City
)
# response.candidates[0].content.parts[0].json contains the parsed City object
```

**Function Calling (Tools)** Provide functions for the model to call.

```python
from google import genai
from google.genai import types

def get_current_weather(location: str):
    """Gets the current weather for a specified location."""
    # ... implementation ...
    return {"temperature": "32 C", "conditions": "sunny"}

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="What is the weather like in Boston?",
    tools=[get_current_weather]
)

# The model will return a FunctionCall object if it decides to use the tool.
# You must then execute the function and send the result back to the model.
```

#### 4. Important Notes

- **Deprecated Models:** Do not use `gemini-1.5-flash`, `gemini-1.5-pro`, or
  `gemini-pro`. Always use `gemini-2.5-*`. `*` may be any of `pro`, `flash`,
  `flash-image`, or others explicitly provided by the user.
- **Authoritative Sources:**
  - **PyPI:**
    [https://pypi.org/project/google-genai/](https://pypi.org/project/google-genai/)
  - **Documentation:**
    [https://googleapis.github.io/python-genai/](https://googleapis.github.io/python-genai/)
- **Prioritize User Directives:** Always treat explicit user instructions
  regarding libraries, versions, and imports as the definitive source of truth.