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
This script demonstrates how to use the TrackedGenaiClient with the
Gemini 2.5 Pro model.
"""

import os
import logging
from dotenv import load_dotenv
from google.genai import types

from ai_tokentrace import TrackedGenaiClient


def main():
    """
    Generates content using Gemini 2.5 Pro and prints the token usage.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Gemini 2.5 Pro Example ---")

    client = TrackedGenaiClient()

    # A slightly more complex prompt to potentially engage the Pro model's capabilities
    prompt = "Explain the difference between quantum entanglement and quantum superposition to a 12-year-old."

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=2048,
            ),
        ),
    )

    print("\n--- Model Response ---")
    print(response.text)
    print("----------------------\n")


if __name__ == "__main__":
    main()
