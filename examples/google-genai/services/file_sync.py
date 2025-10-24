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
JsonlFileTokenUsageService in a synchronous application.
"""

import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

from ai_tokentrace import TrackedGenaiClient
from ai_tokentrace.services import JsonlFileTokenUsageService


def verify_file_output(log_file: Path):
    """Reads and prints the last line of the log file."""
    print(f"Verifying output in: {log_file}")
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                print("\n--- Last Logged Record ---")
                print(lines[-1].strip())
                print("--------------------------\n")
            else:
                print("Log file is empty.")
    except Exception as e:
        print(f"Error reading log file: {e}")


def main():
    """
    Generates content and saves token usage to a JSONL file synchronously.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Synchronous File Service Example ---")

    # Define the output file path
    output_dir = Path("examples/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "token_usage_sync.jsonl"

    # Initialize the service
    service = JsonlFileTokenUsageService(file_path=log_file)
    print(f"Token usage will be saved to: {log_file}")

    # Initialize the client with the service
    client = TrackedGenaiClient(service=service)

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents="Tell me a one-liner joke about programming.",
    )

    print("\n--- Model Response ---")
    print(response.text)
    print("----------------------\n")
    print("Token usage record saved to file.")

    # NOTE: In a short-lived script like this, the main thread might exit
    # before the background logging task completes, leading to lost logs
    # or RuntimeErrors. We add a small sleep here to allow it to finish.
    # Long-running applications typically don't need this.
    time.sleep(1)

    # Verify output
    verify_file_output(log_file)


if __name__ == "__main__":
    main()
