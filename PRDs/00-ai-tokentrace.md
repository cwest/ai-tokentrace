# Product Requirements Document: Token Usage Tracking Library (`ai-tokentrace`)

### **Strategic Overview**

**Project Mandate:**
Cost anxiety is a significant friction point for the widespread, large-scale adoption of AI. This project will create a library to effectively observe and monitor costs in applications using Google's Generative AI, providing developers with the tools to manage their operational expenses and scale their AI solutions with confidence.

**Core Principles:**
*   **Clarity and Transparency:** Provide clear, understandable, and transparent data about token consumption.
*   **Actionable Insights:** The data collected should empower developers to make informed decisions about cost optimization and agent performance.
*   **Minimal Overhead:** The token tracking mechanism should be lightweight and have a negligible impact on application performance.
*   **Excellent Developer Experience:** The library should be simple to integrate, configure, and use, with sensible defaults and clear documentation.

### **Problem Statement & User Need**

Developers building with Google's Generative AI libraries currently lack a standardized, built-in mechanism to track token consumption. This opacity leads to several challenges:
*   **Unpredictable Costs:** Without accurate token tracking, it's difficult to forecast, monitor, and control the operational costs associated with LLM interactions.
*   **Performance Blind Spots:** Developers cannot easily analyze the efficiency of their models and agents, making it hard to identify which interactions are the most "expensive" or where optimizations could be made.
*   **Onboarding Friction:** The fear of incurring unexpected costs ("cost anxiety") can be a significant barrier for new developers, hindering experimentation and wider adoption.

Therefore, developers need a simple, reliable, and integrated way to monitor token usage for every model interaction, enabling them to manage costs effectively and optimize their applications.

### **Target User Personas**

**"Alex, the Pragmatic Builder"**

*   **Role:** Senior Software Engineer at a tech company (50-200 employees).
*   **Goal:** To build and deploy a new customer-facing feature using an ADK-based agent or the `google-genai` library.
*   **Challenges:** Alex is responsible for the feature's budget. She needs to prove the ROI of the AI feature and is wary of unpredictable LLM costs that could kill the project's profitability. She needs clear, actionable data to justify the expense and optimize performance.

**"Priya, the Data-Driven PM"**

*   **Role:** Product Manager.
*   **Goal:** To understand the cost-effectiveness of the new AI feature and report on its ROI to leadership.
*   **Challenges:** Priya isn't a developer. She needs the cost data to be easily accessible and in a format she can use with tools like Google Sheets or a BI dashboard, without needing to ask an engineer for help every time.

### **User Stories**

1.  **Cost Monitoring:**
    *   **As a** Pragmatic Builder (Alex),
    *   **I want** to accurately track the token usage for each model interaction,
    *   **so that** I can monitor the operational costs of my feature and manage my budget effectively.
2.  **Performance Optimization:**
    *   **As a** Pragmatic Builder (Alex),
    *   **I want** to see a breakdown of token consumption per interaction,
    *   **so that** I can identify expensive operations and optimize my agent's performance and efficiency.
3.  **Reporting & Justification:**
    *   **As a** Pragmatic Builder (Alex),
    *   **I want** the token usage data to be exported in a structured, parseable format,
    *   **so that** I can build dashboards and reports to justify the feature's cost and demonstrate its value to stakeholders.
4.  **ROI Analysis:**
    *   **As a** Data-Driven PM (Priya),
    *   **I want** to easily ingest the token usage data into our analytics platform (e.g., BigQuery or a BI tool),
    *   **so that** I can analyze the cost-effectiveness of the AI feature and report on its ROI without needing an engineer's help.

### **Functional Requirements**

1.  **Token Counting Mechanism:**
    *   The system must implement a mechanism to capture token usage data for every model interaction.

2.  **Token Types:**
    *   The system must count and differentiate between three types of tokens where applicable:
        *   **Input Tokens:** Tokens sent to the LLM.
        *   **Output Tokens:** Tokens received from the LLM.
        *   **Thinking Tokens:** Tokens used during internal agent processing or tool use (ADK-specific).

3.  **Cost Calculation Data Fields:**
    *   To enable accurate external cost calculation, each exported record must contain the following data points:
        *   **`timestamp`**: The ISO 8601 timestamp of when the log entry was created.
        *   **`agent_name`**: The identifier for the agent that performed the interaction (if applicable).
        *   **`session_id`**: An identifier to group all interactions within a single user session (if applicable).
        *   **`user_id`**: The identifier for the end-user initiating the request.
        *   **`model_name`**: The specific model used for the interaction (e.g., `gemini-1.5-pro-latest`).
        *   **`authentication_method`**: The method used for authentication (e.g., `api_key`, `service_account`, `adc`).
        *   **`project_id`**: The Google Cloud Project ID associated with the request.
        *   **`location`**: The GCP region or location where the request was processed.
        *   **`input_tokens`**: The count of tokens sent to the model.
        *   **`output_tokens`**: The count of tokens received from the model.
        *   **`thinking_tokens`**: The count of tokens used for internal processing (if applicable).

4.  **Token Usage Service Architecture:**
    *   The system must introduce a service, the `TokenUsageService`, responsible for exporting captured token usage data.
    *   The design of the `TokenUsageService` must be modeled on the existing ADK `SessionService` pattern to ensure architectural consistency.

5.  **`TokenUsageService` Implementations:**
    *   The library will provide the following concrete implementations for data export:
        *   **`LoggingTokenUsageService` (Default):** Logs token usage data to a logger named `ai_tokentrace` using Python's standard `logging` module.
        *   **`JsonlFileTokenUsageService`:** Appends data to a local file in JSONL format.
        *   **`FirestoreTokenUsageService`:** Writes data as a new document to a Firestore collection.
        *   **`PubSubTokenUsageService`:** Publishes data as a message to a Pub/Sub topic.

6.  **Comprehensive Tracking Scope:**
    *   The token tracking mechanism must capture usage from:
        *   **ADK Agent Interactions:** All calls made through the standard agent lifecycle.
        *   **Direct `google.genai` Calls:** Ad-hoc, standalone calls made directly to the `google.genai` library.

7.  **Default Logging Behavior:**
    *   By default, the `LoggingTokenUsageService` will be active.
    *   It will log a JSON-formatted string to a logger named `ai_tokentrace` at the `INFO` level.
    *   This allows developers to see token usage in their console during development without any configuration, and to redirect the output in production using standard Python logging handlers.

### **Architectural Approach & Design Principles**

1.  **Standalone Library & Dependencies:**
    *   The core functionality will be developed as a standalone, distributable Python library named `ai-tokentrace`.
    *   The core library will have minimal dependencies, primarily `google-genai` for API interaction and `pydantic` for data validation.
    *   The integration points for the ADK will be an optional layer, ensuring that developers who only need to track direct `google-genai` calls do not need to install the ADK.

2.  **Multiple Integration Points:**
    *   The library will offer multiple integration points for the ADK framework:
        *   **Global Plugin:** For holistic, automatic tracking across all agents in a `Runner`.
        *   **Granular Callbacks:** For selective, per-agent tracking.

3.  **`google-genai` Coverage (Wrapper Pattern):**
    *   The library will provide a **Wrapper Class** (e.g., `TrackedGenaiClient`) that mirrors the `genai.Client` interface.
    *   This wrapper will allow developers to either pass in a pre-configured `genai.Client` instance or have one created, ensuring flexibility.

4.  **Data Integrity with Pydantic:**
    *   The library will use **Pydantic** for data modeling and validation to ensure a clear and reliable schema for all exported data.

### **Library Design & Distribution Requirements**

1.  **API Design Philosophy:**
    *   **Simple, Explicit, and Consistent:** The API will be designed for ease of use, with clear naming and predictable behavior, consistent with `google-genai` and `ADK` patterns.
    *   **Sensible Defaults:** The library will be usable out-of-the-box, defaulting to the `LoggingTokenUsageService` to provide immediate feedback during development.

2.  **Packaging & Distribution:**
    *   The library will be packaged and distributed on the Python Package Index (PyPI).

3.  **Python Version Support:**
    *   The library must support **Python 3.9 and newer** to align with its core dependencies.

4.  **Versioning Strategy:**
    *   The library will adhere to the **Semantic Versioning 2.0.0** specification.

5.  **Installation Experience:**
    *   The installation command will be `pip install ai-tokentrace`.
    *   Optional dependencies for backends will be managed via extras: `pip install ai-tokentrace[firestore]`.
6.  **Public Changelog:** The project must maintain a `CHANGELOG.md` file. This file will be **automatically generated from the commit history** based on the Conventional Commits standard, and its format will adhere to the principles of **Keep a Changelog**.

### **Development and Maintainability Standards**

1.  **Dependency Management:**
    *   The project will use a `pyproject.toml` file to manage all project metadata, dependencies, and tool configurations, adhering to modern Python packaging standards (PEP 621). We will not use `requirements.txt` files.
2.  **Development Tooling:**
    *   The project will use `uv` as the standard tool for managing virtual environments and installing dependencies during development, ensuring speed and consistency.
3.  **Multi-Version Testing:**
    *   The test suite must be automated (e.g., via GitHub Actions) to run against all supported Python versions (3.9 and newer) to guarantee compatibility.
4.  **Automated Quality Gates:**
    *   The project will use pre-commit hooks to automatically run formatters, linters, and a fast subset of unit tests before each commit. This ensures that all code entering the repository consistently meets our quality standards.
5.  **Continuous Integration (CI):** The project will use **GitHub Actions** for its CI pipeline. All code must pass this pipeline before being merged. The pipeline will run the full test suite across all supported Python versions, enforce code formatting, and run the linter.
6.  **Commit Message Standard:** All commit messages must adhere to the **Conventional Commits specification**. This is a mandatory requirement to enable automated versioning and changelog generation.
7.  **Automated Release Process:** The project will use an automated tool (e.g., `semantic-release` or `release-please`) integrated with the CI pipeline to manage releases. The release process must:
    *   Automatically determine the next version number based on the Conventional Commits history.
    *   Update the version string in `pyproject.toml`.
    *   Generate and update the `CHANGELOG.md` file.
    *   Create a versioned git tag for the new release.

### **Non-Functional Requirements**

1.  **License Compatibility:**
    *   All dependencies must be compatible with the **Apache 2.0 license**.
2.  **Performance Overhead:**
    *   The tracking mechanism must add negligible latency (<5ms per call on average).
3.  **Security:**
    *   The library must not log PII or sensitive data from prompts or responses by default.
4.  **Reliability (Fail-Safe):**
    *   If a data sink is unavailable, the service must log the error and allow the primary application logic to proceed without interruption.
5.  **Unit Testing:**
    *   The library must have a comprehensive unit test suite (`pytest`) with high code coverage (>90%).
6.  **Documentation:**
    *   The library must have a clear user guide with complete examples for each feature.
    *   The API reference documentation must be automatically generated from the Python docstrings in the source code to ensure it is always up-to-date.

### **Success Metrics & KPIs**

1.  **Adoption and Engagement:** Number of active projects using the library.
2.  **Architectural Flexibility:** Distribution of `TokenUsageService` implementations being used.
3.  **Developer Confidence:** Qualitative feedback confirming the tool reduces "cost anxiety."
4.  **Performance Adherence:** Average latency overhead remains within the defined NFR.

### **Risks and Dependencies**

1.  **`google-genai` API Stability:** Breaking changes in the `usage_metadata` field could impact parsing logic.
2.  **Performance Under High Load:** Cumulative impact of latency could become significant at extreme scale.
3.  **Configuration Complexity:** Setup for cloud backends could be a barrier if not well-documented.

### **Out of Scope**

1.  **Internal Cost Calculation:** The library exports data for cost analysis but does not perform the calculation.
2.  **Data Visualization:** The library does not provide any UI or dashboarding tools.
3.  **Support for Other Model Providers:** The initial version is exclusively for the `google-genai` ecosystem.