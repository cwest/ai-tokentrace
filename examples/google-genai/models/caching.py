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
This script demonstrates how to use the TrackedGenaiClient with context caching
to capture cached_content_tokens.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from google.genai import types

from ai_tokentrace import TrackedGenaiClient


async def main():
    """
    Demonstrates context caching with Gemini 2.5 Flash and tracks token usage.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Context Caching Example ---")

    # We need enough content to meet the minimum caching requirement (usually 32k tokens).
    # We'll generate some repetitive text to reach this.
    # "word " is 1 token usually. 33000 words should be enough.
    large_text = "repetition " * 33000

    async with TrackedGenaiClient(
        http_options={"base_url": "https://generativelanguage.googleapis.com/"}
    ) as client:
        cache_name = None
        try:
            print("Creating cache (this may take a moment)...")

            cache = await client.aio.caches.create(
                model="gemini-2.5-flash",
                config=types.CreateCachedContentConfig(
                    contents=[
                        types.Content(role="user", parts=[types.Part(text=large_text)])
                    ],
                    display_name="test-cache",
                    ttl="600s",
                ),
            )
            cache_name = cache.name
            print(f"Created cache: {cache_name}")

            print("Generating content using cache...")
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents="What is the repeated word in the cached content?",
                config=types.GenerateContentConfig(cached_content=cache_name),
            )

            print("\n--- Model Response ---")
            print(response.text)
            print("----------------------\n")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

        finally:
            if cache_name:
                print(f"Deleting cache: {cache_name}")
                await client.aio.caches.delete(name=cache_name)


if __name__ == "__main__":
    asyncio.run(main())
