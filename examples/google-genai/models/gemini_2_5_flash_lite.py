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
Gemini 2.5 Flash Lite model.
"""

import os
import logging
from dotenv import load_dotenv
from google.genai import types

from ai_tokentrace import TrackedGenaiClient


def main():
    """
    Generates content using Gemini 2.5 Flash Lite and prints the token usage.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Gemini 2.5 Flash Lite Example ---")

    client = TrackedGenaiClient()

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents="List 5 fun facts about capybaras.",
        config=types.GenerateContentConfig(
            max_output_tokens=256,
        ),
    )

    print("\n--- Model Response ---")
    print(response.text)
    print("----------------------\n")


if __name__ == "__main__":
    main()
