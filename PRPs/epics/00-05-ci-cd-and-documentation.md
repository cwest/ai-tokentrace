# Epic Plan: 0-05 CI/CD and Documentation

**Parent Plan:** [../00-implementation-plan-ai-tokentrace.md](../00-implementation-plan-ai-tokentrace.md)

## Overview
This epic focuses on the final steps to make the `ai-tokentrace` library a production-ready, distributable package. This includes setting up the full CI/CD pipeline, generating documentation, and preparing for the initial release.

## Implementation Tasks

### Phase 5: CI/CD and Documentation (Effort: ~4 hours)
1.  **Create GitHub Actions CI Workflow**
    -   Description: Set up a CI workflow to run `pre-commit` checks and the `pytest` suite across all supported Python versions (3.9+). The CI steps will use `uv run poe ...` commands.
    -   Files to create: `.github/workflows/ci.yml`

2.  **Set up Automated Release Workflow**
    -   Description: Configure `release-please` via a GitHub Action to automate releases to PyPI. This must be configured to automatically generate and update a `CHANGELOG.md` file based on Conventional Commits.
    -   Files to create: `.github/workflows/release.yml`, `CHANGELOG.md`

3.  **Set up Automated API Documentation**
    -   Description: Add a tool like `pdoc` or `Sphinx` to the development dependencies. Configure it to generate HTML API documentation from source code docstrings. Create a `poe docs` task for this.
    -   Files to modify: `pyproject.toml`

4.  **Add Project Documentation (User Guide)**
    -   Description: Update the `README.md` with project goals, installation instructions, and usage examples for both the `TrackedGenaiClient` and the ADK integrations.
    -   Files to modify: `README.md`

## Success Criteria
- [ ] The CI workflow is functional and passes on all supported Python versions.
- [ ] The automated release workflow is configured.
- [ ] The `poe docs` task successfully generates API documentation.
- [ ] The `README.md` is updated to be a comprehensive user guide.
- [ ] The `CHANGELOG.md` file is created.
