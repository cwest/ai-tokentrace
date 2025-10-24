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
This script demonstrates how to use the TrackedGenaiClient for a synchronous
`generate_content_stream` call.
"""

import os
import logging
from dotenv import load_dotenv

from ai_tokentrace import TrackedGenaiClient


def main():
    """
    Generates content via a stream and prints the token usage for each chunk.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Synchronous Stream Example ---")

    client = TrackedGenaiClient()

    stream = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents="Tell me a long story about a dragon who loves to cook.",
    )

    print("\n--- Model Response (Streaming) ---")
    full_response = ""
    for chunk in stream:
        full_response += chunk.text
        print(chunk.text, end="", flush=True)

    print("\n----------------------------------\n")


if __name__ == "__main__":
    main()
