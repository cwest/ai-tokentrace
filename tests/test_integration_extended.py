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
import pytest
from google.genai import types
from ai_tokentrace import TrackedGenaiClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_google_search_tool_use():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")

    async with TrackedGenaiClient(http_options={"api_version": "v1beta"}) as client:
        prompt = "What is the current stock price of Alphabet Inc (GOOG)?"
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        )
        assert response.text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_context_caching():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")

    # Enough content to meet minimum caching requirement
    large_text = "repetition " * 33000
    cache_name = None

    # Use explicit base URL to avoid potential local proxy issues seen in examples
    async with TrackedGenaiClient(
        http_options={"base_url": "https://generativelanguage.googleapis.com/"}
    ) as client:
        try:
            cache = await client.aio.caches.create(
                model="gemini-2.5-flash",
                config=types.CreateCachedContentConfig(
                    contents=[
                        types.Content(role="user", parts=[types.Part(text=large_text)])
                    ],
                    ttl="600s",
                ),
            )
            cache_name = cache.name

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents="What is the repeated word?",
                config=types.GenerateContentConfig(cached_content=cache_name),
            )
            assert response.text
        finally:
            if cache_name:
                await client.aio.caches.delete(name=cache_name)
