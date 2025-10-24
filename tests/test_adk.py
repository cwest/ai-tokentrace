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

import pytest
from unittest.mock import MagicMock, patch
from ai_tokentrace.data_model import TokenUsageRecord
from ai_tokentrace.adk import TokenTrackingPlugin


# Mock ADK availability for tests even if not installed
@pytest.fixture(autouse=True)
def mock_adk_available():
    with patch("ai_tokentrace.adk.ADK_AVAILABLE", True):
        yield


def test_plugin_initialization():
    service = MagicMock()
    plugin = TokenTrackingPlugin(
        service=service, agent_name="test-agent", tracked_agents=["agent1"]
    )
    assert plugin.service == service
    assert plugin._explicit_agent_name == "test-agent"
    assert plugin._tracked_agents == {"agent1"}


def test_after_model_callback_extracts_usage():
    mock_service = MagicMock()
    plugin = TokenTrackingPlugin(service=mock_service, agent_name="test-agent")

    mock_runner = MagicMock()
    mock_response = MagicMock()
    mock_response.usage_metadata = MagicMock()
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 20
    mock_response.usage_metadata.total_token_count = 30
    mock_response.usage_metadata.thinking_token_count = None
    mock_response.usage_metadata.cached_content_token_count = None

    plugin.after_model_callback(mock_runner, mock_response, model_name="gemini-pro")

    assert mock_service.export.called
    record = mock_service.export.call_args[0][0]
    assert isinstance(record, TokenUsageRecord)
    assert record.agent_name == "test-agent"
    assert record.model_name == "gemini-pro"
    assert record.input_tokens == 10
    assert record.output_tokens == 20


def test_after_model_callback_infers_agent_name():
    mock_service = MagicMock()
    plugin = TokenTrackingPlugin(service=mock_service)  # No explicit agent name

    mock_runner = MagicMock()
    mock_runner.agent.name = "inferred-agent"

    mock_response = MagicMock()
    mock_response.usage_metadata = MagicMock()
    mock_response.usage_metadata.prompt_token_count = 5
    mock_response.usage_metadata.candidates_token_count = 5
    mock_response.usage_metadata.thinking_token_count = 0
    mock_response.usage_metadata.cached_content_token_count = 0

    plugin.after_model_callback(mock_runner, mock_response, model_name="gemini-flash")

    assert mock_service.export.called
    record = mock_service.export.call_args[0][0]
    assert record.agent_name == "inferred-agent"


def test_after_model_callback_no_usage_metadata():
    mock_service = MagicMock()
    plugin = TokenTrackingPlugin(service=mock_service)

    mock_runner = MagicMock()
    mock_response = MagicMock()
    del mock_response.usage_metadata

    plugin.after_model_callback(mock_runner, mock_response)

    assert not mock_service.export.called


def test_plugin_uses_global_service_if_none_provided():
    with patch("ai_tokentrace.adk.get_global_service") as mock_get_global:
        mock_global_service = MagicMock()
        mock_get_global.return_value = mock_global_service

        plugin = TokenTrackingPlugin(service=None)

        mock_runner = MagicMock()
        mock_runner.agent.name = "global-agent"

        mock_response = MagicMock()
        mock_response.usage_metadata.prompt_token_count = 5
        mock_response.usage_metadata.candidates_token_count = 5
        mock_response.usage_metadata.thinking_token_count = 0
        mock_response.usage_metadata.cached_content_token_count = 0

        plugin.after_model_callback(mock_runner, mock_response)

        assert mock_global_service.export.called


def test_granular_tracking_filters_agents():
    mock_service = MagicMock()
    # Only track 'agent-a'
    plugin = TokenTrackingPlugin(service=mock_service, tracked_agents=["agent-a"])

    # Test with tracked agent
    mock_runner_a = MagicMock()
    mock_runner_a.agent.name = "agent-a"
    mock_response = MagicMock()
    mock_response.usage_metadata.prompt_token_count = 5
    mock_response.usage_metadata.candidates_token_count = 5
    mock_response.usage_metadata.thinking_token_count = 0
    mock_response.usage_metadata.cached_content_token_count = 0

    plugin.after_model_callback(mock_runner_a, mock_response)
    assert mock_service.export.call_count == 1
    assert mock_service.export.call_args[0][0].agent_name == "agent-a"

    # Test with untracked agent
    mock_runner_b = MagicMock()
    mock_runner_b.agent.name = "agent-b"

    plugin.after_model_callback(mock_runner_b, mock_response)
    # Call count should still be 1
    assert mock_service.export.call_count == 1
