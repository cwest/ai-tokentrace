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
AsyncJsonlFileTokenUsageService to save token usage to a file.
"""

import os
import asyncio
import logging
import aiofiles
from pathlib import Path
from dotenv import load_dotenv

from ai_tokentrace import TrackedGenaiClient
from ai_tokentrace.services import AsyncJsonlFileTokenUsageService


async def verify_file_output(log_file: Path):
    """Reads and prints the last line of the log file."""
    print(f"Verifying output in: {log_file}")
    try:
        async with aiofiles.open(log_file, "r", encoding="utf-8") as f:
            lines = await f.readlines()
            if lines:
                print("\n--- Last Logged Record ---")
                print(lines[-1].strip())
                print("--------------------------\n")
            else:
                print("Log file is empty.")
    except Exception as e:
        print(f"Error reading log file: {e}")


async def main():
    """
    Generates content and saves token usage to a JSONL file asynchronously.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Async File Service Example ---")

    # Define the output file path
    output_dir = Path("examples/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "token_usage_async.jsonl"

    # Initialize the async service
    service = AsyncJsonlFileTokenUsageService(file_path=log_file)
    print(f"Token usage will be saved to: {log_file}")

    # Initialize the client with the service and use async context manager
    async with TrackedGenaiClient(service=service) as client:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents="Tell me a joke about a file system.",
        )

        print("\n--- Model Response ---")
        print(response.text)
        print("----------------------\n")
        print("Token usage record saved to file.")

    # Verify output
    await verify_file_output(log_file)


if __name__ == "__main__":
    asyncio.run(main())
