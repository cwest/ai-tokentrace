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
Gemini 2.5 Flash model with "thinking" enabled.
"""

import os
import logging
from dotenv import load_dotenv
from google.genai import types

from ai_tokentrace import TrackedGenaiClient


def main():
    """
    Generates content using Gemini 2.5 Flash with thinking and prints the token usage.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Gemini 2.5 Flash (Thinking) Example ---")

    client = TrackedGenaiClient()

    # A riddle that benefits from "thinking"
    prompt = "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=1024,
                )
            ),
        )

        print("\n--- Model Response ---")
        print(response.text)
        print("----------------------\n")
    except Exception as e:
        print(f"\nError running with thinking config: {e}")
        print("This might be because the model doesn't support 'thinking_config'.")


if __name__ == "__main__":
    main()
