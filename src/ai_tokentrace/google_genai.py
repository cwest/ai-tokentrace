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
Provides a wrapper for the `google.genai` client to track token usage.
"""

import os
import sys
from google import genai

from .data_model import TokenUsageRecord
from .services import LoggingTokenUsageService, AsyncLoggingTokenUsageService


class TrackedGenaiClient:
    """
    A wrapper for the `google.genai` client that tracks token usage.

    This class mirrors the `google.genai.Client` interface, automatically
    capturing and exporting token usage data for supported API calls.
    It also supports asynchronous context management.
    """

    def __init__(self, service=None, agent_name: str | None = None, *args, **kwargs):
        self.service = service
        self._agent_name = agent_name or os.path.basename(sys.argv[0])
        self._auth_method, self._project_id, self._location = (
            self._determine_auth_details(*args, **kwargs)
        )
        self.client = genai.Client(*args, **kwargs)

        # Wrap the underlying client's methods
        self._wrap_methods()

    def _determine_auth_details(self, *args, **kwargs):
        """
        Determines the authentication method, project, and location based on
        client initialization parameters and environment variables.
        """
        project_id = kwargs.get("project")
        location = kwargs.get("location")

        if kwargs.get("api_key"):
            return "api_key", project_id, location

        if kwargs.get("credentials"):
            return "service_account", project_id, location

        if kwargs.get("vertexai", False):
            return "adc", project_id, location

        # Fallback to environment variables if no direct args are provided
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            return "api_key", project_id, location

        # Default fallback if no other method is specified.
        return "adc", project_id, location

    def _wrap_methods(self):
        """Wraps methods on the client for tracking."""
        # Sync methods
        original_generate_content = self.client.models.generate_content
        original_generate_content_stream = self.client.models.generate_content_stream
        original_generate_images = self.client.models.generate_images
        original_generate_videos = self.client.models.generate_videos

        def sync_wrapper(func, *args, **kwargs):
            if self.service is None:
                self.service = LoggingTokenUsageService()
            model_name = kwargs.get("model") or (args[0] if args else None)
            response = func(*args, **kwargs)
            self._capture_usage_sync(response, model_name, "generate_content")
            return response

        def sync_stream_wrapper(func, *args, **kwargs):
            if self.service is None:
                self.service = LoggingTokenUsageService()
            model_name = kwargs.get("model") or (args[0] if args else None)
            stream = func(*args, **kwargs)
            last_chunk = None
            for chunk in stream:
                last_chunk = chunk
                yield chunk
            if last_chunk:
                self._capture_usage_sync(
                    last_chunk, model_name, "generate_content_stream"
                )

        def sync_image_wrapper(func, *args, **kwargs):
            if self.service is None:
                self.service = LoggingTokenUsageService()
            model_name = kwargs.get("model") or (args[0] if args else None)
            response = func(*args, **kwargs)
            images_generated = (
                len(response.generated_images)
                if getattr(response, "generated_images", None)
                else 0
            )
            self._capture_usage_sync(
                response,
                model_name,
                "generate_images",
                images_generated=images_generated,
            )
            return response

        def sync_video_wrapper(func, *args, **kwargs):
            if self.service is None:
                self.service = LoggingTokenUsageService()
            model_name = kwargs.get("model") or (args[0] if args else None)

            config = kwargs.get("config")
            videos_generated = 1
            if config:
                if (
                    hasattr(config, "number_of_videos")
                    and config.number_of_videos is not None
                ):
                    videos_generated = config.number_of_videos
                elif isinstance(config, dict) and "number_of_videos" in config:
                    videos_generated = config["number_of_videos"]

            response = func(*args, **kwargs)
            self._capture_usage_sync(
                response,
                model_name,
                "generate_videos",
                videos_generated=videos_generated,
            )
            return response

        self.client.models.generate_content = lambda *a, **kw: sync_wrapper(
            original_generate_content, *a, **kw
        )
        self.client.models.generate_content_stream = (
            lambda *a, **kw: sync_stream_wrapper(
                original_generate_content_stream, *a, **kw
            )
        )
        self.client.models.generate_images = lambda *a, **kw: sync_image_wrapper(
            original_generate_images, *a, **kw
        )
        self.client.models.generate_videos = lambda *a, **kw: sync_video_wrapper(
            original_generate_videos, *a, **kw
        )

        # Async methods
        original_generate_content_async = self.client.aio.models.generate_content
        original_generate_content_stream_async = (
            self.client.aio.models.generate_content_stream
        )
        original_generate_images_async = self.client.aio.models.generate_images
        original_generate_videos_async = self.client.aio.models.generate_videos

        async def async_wrapper(func, *args, **kwargs):
            if self.service is None:
                self.service = AsyncLoggingTokenUsageService()
            model_name = kwargs.get("model") or (args[0] if args else None)
            response = await func(*args, **kwargs)
            await self._capture_usage_async(response, model_name, "generate_content")
            return response

        async def async_stream_wrapper(func, *args, **kwargs):
            if self.service is None:
                self.service = AsyncLoggingTokenUsageService()
            model_name = kwargs.get("model") or (args[0] if args else None)
            stream = await func(*args, **kwargs)
            last_chunk = None
            async for chunk in stream:
                last_chunk = chunk
                yield chunk
            if last_chunk:
                await self._capture_usage_async(
                    last_chunk, model_name, "generate_content_stream"
                )

        async def async_image_wrapper(func, *args, **kwargs):
            if self.service is None:
                self.service = AsyncLoggingTokenUsageService()
            model_name = kwargs.get("model") or (args[0] if args else None)
            response = await func(*args, **kwargs)
            images_generated = (
                len(response.generated_images)
                if getattr(response, "generated_images", None)
                else 0
            )
            await self._capture_usage_async(
                response,
                model_name,
                "generate_images",
                images_generated=images_generated,
            )
            return response

        async def async_video_wrapper(func, *args, **kwargs):
            if self.service is None:
                self.service = AsyncLoggingTokenUsageService()
            model_name = kwargs.get("model") or (args[0] if args else None)

            config = kwargs.get("config")
            videos_generated = 1
            if config:
                if (
                    hasattr(config, "number_of_videos")
                    and config.number_of_videos is not None
                ):
                    videos_generated = config.number_of_videos
                elif isinstance(config, dict) and "number_of_videos" in config:
                    videos_generated = config["number_of_videos"]

            response = await func(*args, **kwargs)
            await self._capture_usage_async(
                response,
                model_name,
                "generate_videos",
                videos_generated=videos_generated,
            )
            return response

        self.client.aio.models.generate_content = lambda *a, **kw: async_wrapper(
            original_generate_content_async, *a, **kw
        )
        self.client.aio.models.generate_content_stream = (
            lambda *a, **kw: async_stream_wrapper(
                original_generate_content_stream_async, *a, **kw
            )
        )
        self.client.aio.models.generate_images = lambda *a, **kw: async_image_wrapper(
            original_generate_images_async, *a, **kw
        )
        self.client.aio.models.generate_videos = lambda *a, **kw: async_video_wrapper(
            original_generate_videos_async, *a, **kw
        )

    def _create_record(
        self, response, model_name, method_name, images_generated=0, videos_generated=0
    ):
        """Creates a TokenUsageRecord from a response object."""
        try:
            usage = getattr(response, "usage_metadata", None)
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            thinking_tokens = (
                getattr(usage, "thoughts_token_count", None) if usage else None
            )
            cached_content_tokens = (
                getattr(usage, "cached_content_token_count", None) if usage else None
            )
            tool_use_prompt_tokens = (
                getattr(usage, "tool_use_prompt_token_count", None) if usage else None
            )

            # If we have neither tokens nor images nor videos, we can't create a meaningful record
            if (
                input_tokens == 0
                and output_tokens == 0
                and images_generated == 0
                and videos_generated == 0
            ):
                return None

            return TokenUsageRecord(
                agent_name=self._agent_name,
                model_name=model_name,
                method_name=method_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                thinking_tokens=thinking_tokens,
                cached_content_tokens=cached_content_tokens,
                tool_use_prompt_tokens=tool_use_prompt_tokens,
                images_generated=images_generated,
                videos_generated=videos_generated,
                authentication_method=self._auth_method,
                project_id=self._project_id,
                location=self._location,
            )
        except (AttributeError, ValueError):
            return None

    def _capture_usage_sync(
        self, response, model_name, method_name, images_generated=0, videos_generated=0
    ):
        """Synchronously captures and exports a token usage record."""
        record = self._create_record(
            response,
            model_name,
            method_name,
            images_generated=images_generated,
            videos_generated=videos_generated,
        )
        if record:
            self.service.export(record)

    async def _capture_usage_async(
        self, response, model_name, method_name, images_generated=0, videos_generated=0
    ):
        """Asynchronously captures and exports a token usage record."""
        record = self._create_record(
            response,
            model_name,
            method_name,
            images_generated=images_generated,
            videos_generated=videos_generated,
        )
        if record:
            await self.service.export(record)

    async def aclose(self):
        """Closes the underlying asynchronous client."""
        await self.client.aio.aclose()

    async def __aenter__(self):
        """Enters the asynchronous context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exits the asynchronous context manager and closes the client."""
        await self.aclose()

    def __getattr__(self, name):
        """
        Delegates all other attribute access to the underlying client.
        """
        return getattr(self.client, name)
