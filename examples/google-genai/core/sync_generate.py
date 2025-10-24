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
This script demonstrates how to use the TrackedGenaiClient for a basic
synchronous `generate_content` call.
"""

import os
import logging
from dotenv import load_dotenv

from ai_tokentrace import TrackedGenaiClient


def main():
    """
    Generates content synchronously and prints the token usage.
    """
    # Configure basic logging to ensure the token trace is visible
    logging.basicConfig(level=logging.INFO)

    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        logging.error("Please create a .env file and add your API key.")
        return

    print("--- Running Synchronous Generate Content Example ---")

    # The TrackedGenaiClient wraps the standard genai.Client
    # and automatically captures token usage. The default service is
    # LoggingTokenUsageService, which uses Python's logging module.
    client = TrackedGenaiClient()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Write a short story about a robot who discovers music.",
    )

    print("\n--- Model Response ---")
    print(response.text)
    print("----------------------\n")


if __name__ == "__main__":
    main()
