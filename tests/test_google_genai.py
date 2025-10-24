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

import os
import sys
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from ai_tokentrace.google_genai import TrackedGenaiClient


# Since we are testing our wrapper, we need to patch the actual `genai.Client`
# that our wrapper will try to instantiate.
@patch("ai_tokentrace.google_genai.genai.Client")
class TestTrackedGenaiClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_service = MagicMock()

    def test_auth_method_with_api_key_arg(self, mock_genai_client):
        """Verify auth method is 'api_key' when passed as an argument."""
        client = TrackedGenaiClient(service=self.mock_service, api_key="test-key")
        self.assertEqual(client._auth_method, "api_key")
        mock_genai_client.assert_called_once_with(api_key="test-key")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-env"})
    def test_auth_method_with_api_key_env(self, mock_genai_client):
        """Verify auth method is 'api_key' when present as an env var."""
        client = TrackedGenaiClient(service=self.mock_service)
        self.assertEqual(client._auth_method, "api_key")
        mock_genai_client.assert_called_once_with()

    def test_auth_method_with_credentials_arg(self, mock_genai_client):
        """Verify auth method is 'service_account' when credentials are passed."""
        mock_creds = MagicMock()
        client = TrackedGenaiClient(service=self.mock_service, credentials=mock_creds)
        self.assertEqual(client._auth_method, "service_account")
        mock_genai_client.assert_called_once_with(credentials=mock_creds)

    def test_auth_method_with_vertexai_arg(self, mock_genai_client):
        """Verify auth method is 'adc' when vertexai=True."""
        client = TrackedGenaiClient(
            service=self.mock_service,
            vertexai=True,
            project="test-project",
            location="us-central1",
        )
        self.assertEqual(client._auth_method, "adc")
        self.assertEqual(client._project_id, "test-project")
        self.assertEqual(client._location, "us-central1")
        mock_genai_client.assert_called_once_with(
            vertexai=True, project="test-project", location="us-central1"
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_auth_method_fallback_to_adc(self, mock_genai_client):
        """Verify auth method falls back to 'adc' when no other config is provided."""
        client = TrackedGenaiClient(service=self.mock_service)
        self.assertEqual(client._auth_method, "adc")
        mock_genai_client.assert_called_once_with()

    def test_agent_name_default(self, mock_genai_client):
        """Verify agent_name defaults to the script name."""
        with patch.object(sys, "argv", ["/path/to/my_script.py"]):
            client = TrackedGenaiClient(service=self.mock_service)
            self.assertEqual(client._agent_name, "my_script.py")

    def test_agent_name_override(self, mock_genai_client):
        """Verify agent_name can be overridden."""
        client = TrackedGenaiClient(
            service=self.mock_service, agent_name="custom-agent"
        )
        self.assertEqual(client._agent_name, "custom-agent")

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_content_wrapper(self, mock_genai_client):
        """Verify sync generate_content is wrapped."""
        mock_response = MagicMock()
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 20
        mock_client_instance = mock_genai_client.return_value
        original_method = mock_client_instance.models.generate_content
        original_method.return_value = mock_response

        client = TrackedGenaiClient(
            service=self.mock_service,
            vertexai=True,
            project="p",
            location="l",
            agent_name="test-agent",
        )
        client.models.generate_content(model="gemini-pro", prompt="test")

        original_method.assert_called_once_with(model="gemini-pro", prompt="test")
        self.mock_service.export.assert_called_once()
        exported_record = self.mock_service.export.call_args[0][0]
        self.assertEqual(exported_record.agent_name, "test-agent")
        self.assertEqual(exported_record.method_name, "generate_content")

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_content_with_extended_metadata(self, mock_genai_client):
        """Verify generate_content captures extended metadata."""
        mock_response = MagicMock()
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 20
        mock_response.usage_metadata.cached_content_token_count = 5
        mock_response.usage_metadata.tool_use_prompt_token_count = 3
        mock_response.usage_metadata.thoughts_token_count = 7

        mock_client_instance = mock_genai_client.return_value
        original_method = mock_client_instance.models.generate_content
        original_method.return_value = mock_response

        client = TrackedGenaiClient(
            service=self.mock_service, vertexai=True, project="p", location="l"
        )
        client.models.generate_content(model="gemini-pro", prompt="test")

        self.mock_service.export.assert_called_once()
        record = self.mock_service.export.call_args[0][0]
        self.assertEqual(record.input_tokens, 10)
        self.assertEqual(record.output_tokens, 20)
        self.assertEqual(record.cached_content_tokens, 5)
        self.assertEqual(record.tool_use_prompt_tokens, 3)
        self.assertEqual(record.thinking_tokens, 7)

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_content_stream_wrapper(self, mock_genai_client):
        """Verify sync generate_content_stream is wrapped."""
        mock_chunk = MagicMock()
        mock_chunk.usage_metadata.prompt_token_count = 5
        mock_chunk.usage_metadata.candidates_token_count = 10
        mock_client_instance = mock_genai_client.return_value
        original_method = mock_client_instance.models.generate_content_stream
        original_method.return_value = [mock_chunk, mock_chunk]  # Stream two chunks

        client = TrackedGenaiClient(
            service=self.mock_service, vertexai=True, project="p", location="l"
        )
        stream = client.models.generate_content_stream(
            model="gemini-pro", prompt="test"
        )
        list(stream)  # Consume the stream

        original_method.assert_called_once_with(model="gemini-pro", prompt="test")
        self.assertEqual(self.mock_service.export.call_count, 1)
        exported_record = self.mock_service.export.call_args[0][0]
        self.assertEqual(exported_record.method_name, "generate_content_stream")

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_images_wrapper(self, mock_genai_client):
        """Verify sync generate_images is wrapped and tracks images."""
        mock_response = MagicMock()
        # Simulate 2 generated images
        mock_response.generated_images = ["img1", "img2"]
        # Ensure it doesn't have usage_metadata
        del mock_response.usage_metadata

        mock_client_instance = mock_genai_client.return_value
        original_method = mock_client_instance.models.generate_images
        original_method.return_value = mock_response

        client = TrackedGenaiClient(
            service=self.mock_service, vertexai=True, project="p", location="l"
        )
        client.models.generate_images(model="imagen-3", prompt="test")

        original_method.assert_called_once_with(model="imagen-3", prompt="test")
        self.mock_service.export.assert_called_once()
        record = self.mock_service.export.call_args[0][0]
        self.assertEqual(record.images_generated, 2)
        self.assertEqual(record.input_tokens, 0)
        self.assertEqual(record.output_tokens, 0)
        self.assertEqual(record.method_name, "generate_images")

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_videos_wrapper(self, mock_genai_client):
        """Verify sync generate_videos is wrapped and tracks videos."""
        mock_response = MagicMock()
        # generate_videos returns an operation, but we track the call itself.

        mock_client_instance = mock_genai_client.return_value
        original_method = mock_client_instance.models.generate_videos
        original_method.return_value = mock_response

        client = TrackedGenaiClient(
            service=self.mock_service, vertexai=True, project="p", location="l"
        )

        # Test with explicit config
        mock_config = MagicMock()
        mock_config.number_of_videos = 2
        client.models.generate_videos(model="veo-3", prompt="test", config=mock_config)

        original_method.assert_called_with(
            model="veo-3", prompt="test", config=mock_config
        )
        self.assertEqual(self.mock_service.export.call_count, 1)
        record = self.mock_service.export.call_args[0][0]
        self.assertEqual(record.videos_generated, 2)
        self.assertEqual(record.method_name, "generate_videos")

        # Test with default (no config)
        client.models.generate_videos(model="veo-3", prompt="test")
        self.assertEqual(self.mock_service.export.call_count, 2)
        record = self.mock_service.export.call_args[0][0]
        self.assertEqual(record.videos_generated, 1)  # Default

    @patch.dict(os.environ, {}, clear=True)
    async def test_generate_content_async_wrapper(self, mock_genai_client):
        """Verify async generate_content is wrapped."""
        self.mock_service.export = AsyncMock()
        mock_response = MagicMock()
        mock_response.usage_metadata.prompt_token_count = 15
        mock_response.usage_metadata.candidates_token_count = 25

        mock_client_instance = mock_genai_client.return_value
        # Use AsyncMock for the async method
        mock_client_instance.aio.models.generate_content = AsyncMock(
            return_value=mock_response
        )
        original_method = mock_client_instance.aio.models.generate_content

        client = TrackedGenaiClient(
            service=self.mock_service, vertexai=True, project="p", location="l"
        )
        await client.aio.models.generate_content(model="gemini-pro", prompt="test")

        original_method.assert_awaited_once_with(model="gemini-pro", prompt="test")
        self.mock_service.export.assert_awaited_once()
        exported_record = self.mock_service.export.call_args[0][0]
        self.assertEqual(exported_record.method_name, "generate_content")

    @patch.dict(os.environ, {}, clear=True)
    async def test_generate_content_stream_async_wrapper(self, mock_genai_client):
        """Verify async generate_content_stream is wrapped."""
        self.mock_service.export = AsyncMock()
        mock_chunk = MagicMock()
        mock_chunk.usage_metadata.prompt_token_count = 8
        mock_chunk.usage_metadata.candidates_token_count = 12

        async def mock_stream_generator():
            yield mock_chunk
            yield mock_chunk

        mock_client_instance = mock_genai_client.return_value
        # Use AsyncMock that returns the async generator
        mock_client_instance.aio.models.generate_content_stream = AsyncMock(
            return_value=mock_stream_generator()
        )
        original_method = mock_client_instance.aio.models.generate_content_stream

        client = TrackedGenaiClient(
            service=self.mock_service, vertexai=True, project="p", location="l"
        )
        stream = client.aio.models.generate_content_stream(
            model="gemini-pro", prompt="test"
        )
        async for _ in stream:
            pass  # Consume the stream

        original_method.assert_awaited_once_with(model="gemini-pro", prompt="test")
        self.assertEqual(self.mock_service.export.call_count, 1)
        exported_record = self.mock_service.export.call_args[0][0]
        self.assertEqual(exported_record.method_name, "generate_content_stream")

    @patch.dict(os.environ, {}, clear=True)
    async def test_generate_images_async_wrapper(self, mock_genai_client):
        """Verify async generate_images is wrapped and tracks images."""
        self.mock_service.export = AsyncMock()
        mock_response = MagicMock()
        mock_response.generated_images = ["img1"]
        del mock_response.usage_metadata

        mock_client_instance = mock_genai_client.return_value
        # Use AsyncMock for the async method
        mock_client_instance.aio.models.generate_images = AsyncMock(
            return_value=mock_response
        )
        original_method = mock_client_instance.aio.models.generate_images

        client = TrackedGenaiClient(
            service=self.mock_service, vertexai=True, project="p", location="l"
        )
        await client.aio.models.generate_images(model="imagen-3", prompt="test")

        original_method.assert_awaited_once_with(model="imagen-3", prompt="test")
        self.mock_service.export.assert_awaited_once()
        record = self.mock_service.export.call_args[0][0]
        self.assertEqual(record.images_generated, 1)
        self.assertEqual(record.input_tokens, 0)
        self.assertEqual(record.output_tokens, 0)
        self.assertEqual(record.method_name, "generate_images")

    def test_getattr_delegation(self, mock_genai_client):
        """Verify that other attributes are delegated to the underlying client."""
        mock_client_instance = mock_genai_client.return_value
        mock_client_instance.some_other_attribute = "test_value"

        client = TrackedGenaiClient(service=self.mock_service)
        self.assertEqual(client.some_other_attribute, "test_value")

    async def test_aclose_method(self, mock_genai_client):
        """Verify the aclose method is delegated."""
        mock_client_instance = mock_genai_client.return_value
        mock_client_instance.aio.aclose = AsyncMock()

        client = TrackedGenaiClient(service=self.mock_service)
        await client.aclose()

        mock_client_instance.aio.aclose.assert_awaited_once()

    async def test_async_context_manager(self, mock_genai_client):
        """Verify the async context manager closes the client."""
        mock_client_instance = mock_genai_client.return_value
        mock_client_instance.aio.aclose = AsyncMock()

        async with TrackedGenaiClient(service=self.mock_service):
            pass  # Client is used within this block

        mock_client_instance.aio.aclose.assert_awaited_once()
