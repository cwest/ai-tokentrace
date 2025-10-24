# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ADK integration for ai-tokentrace.

This module provides a plugin for the Google Agent Development Kit (ADK)
to automatically track token usage.
"""

import logging
from typing import Any, Optional, Sequence

from .data_model import TokenUsageRecord
from .services import TokenUsageService, get_global_service

logger = logging.getLogger(__name__)

try:
    from google.adk.plugins import BasePlugin
    from google.genai.types import GenerateContentResponse

    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    BasePlugin = object  # type: ignore
    GenerateContentResponse = Any  # type: ignore


class TokenTrackingPlugin(BasePlugin):
    """
    ADK plugin to track token usage from model calls.
    """

    def __init__(
        self,
        service: Optional[TokenUsageService] = None,
        agent_name: Optional[str] = None,
        tracked_agents: Optional[Sequence[str]] = None,
    ):
        """
        Initialize the plugin.

        Args:
            service: The TokenUsageService to use for exporting data.
                     If None, uses the global default service.
            agent_name: Optional name override for the agent. If provided, ALL
                        tracked usage will be attributed to this name, regardless
                        of the actual agent name.
            tracked_agents: Optional list of agent names to track. If provided,
                            only agents with names in this list will be tracked.
                            If None or empty, all agents are tracked.
        """
        if not ADK_AVAILABLE:
            logger.warning(
                "google-adk is not installed. TokenTrackingPlugin will be inactive."
            )

        self.service = service
        self._explicit_agent_name = agent_name
        self._tracked_agents = set(tracked_agents) if tracked_agents else None

    def _get_service(self) -> TokenUsageService:
        """Returns the configured service or the global default."""
        return self.service or get_global_service()

    def after_model_callback(
        self,
        runner: Any,
        response: Any,
        **kwargs: Any,
    ) -> None:
        """
        Hook called after a model call.

        Args:
            runner: The ADK runner instance.
            response: The response from the model (likely a google.genai.types.GenerateContentResponse).
            **kwargs: Additional arguments.
        """
        if not ADK_AVAILABLE:
            return

        # Try to extract usage metadata from the response.
        # We assume response might be a GenerateContentResponse or similar
        # that has a usage_metadata attribute.
        usage_metadata = getattr(response, "usage_metadata", None)

        if usage_metadata:
            # Determine actual agent name from runner if possible
            actual_agent_name = None
            if hasattr(runner, "agent") and hasattr(runner.agent, "name"):
                actual_agent_name = runner.agent.name

            # Check if we should track this agent
            if self._tracked_agents and actual_agent_name not in self._tracked_agents:
                return

            # Determine final agent name to record
            final_agent_name = (
                self._explicit_agent_name or actual_agent_name or "adk-agent"
            )

            # Determine model name if possible (might be in kwargs or runner)
            model_name = kwargs.get("model_name", "unknown-adk-model")

            # Extract token counts safely
            input_tokens = getattr(usage_metadata, "prompt_token_count", 0)
            output_tokens = getattr(usage_metadata, "candidates_token_count", 0)
            thinking_tokens = getattr(usage_metadata, "thinking_token_count", None)
            cached_content_tokens = getattr(
                usage_metadata, "cached_content_token_count", None
            )

            record = TokenUsageRecord(
                agent_name=final_agent_name,
                model_name=model_name,
                method_name="adk.generate_content",  # Indicate it came via ADK
                authentication_method="api_key",  # Default for now
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                thinking_tokens=thinking_tokens,
                cached_content_tokens=cached_content_tokens,
            )

            try:
                self._get_service().export(record)
            except Exception as e:
                logger.error(f"Failed to export token usage in ADK plugin: {e}")
