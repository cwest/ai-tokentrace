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
This script demonstrates how to use the TrackedGenaiClient for an asynchronous
`generate_content` call.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

from ai_tokentrace import TrackedGenaiClient


async def main():
    """
    Generates content asynchronously and prints the token usage.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Asynchronous Generate Content Example ---")

    # The TrackedGenaiClient supports the async context manager protocol
    # to ensure resources are properly cleaned up.
    async with TrackedGenaiClient() as client:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash", contents="Write a short poem about the sun."
        )

        print("\n--- Model Response ---")
        print(response.text)
        print("----------------------\n")


if __name__ == "__main__":
    asyncio.run(main())
