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
Veo 3 model to generate videos.
"""

import os
import time
import logging
from dotenv import load_dotenv
from google.genai import types

from ai_tokentrace import TrackedGenaiClient


def main():
    """
    Generates a video using Veo 3 and prints the status.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Veo 3 Video Generation Example ---")

    client = TrackedGenaiClient()

    # Ensure output directory exists
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)

    try:
        print("Starting video generation operation...")
        # generate_videos returns a Long Running Operation (LRO)
        operation = client.models.generate_videos(
            model="veo-3.0-generate-001",
            prompt="A cute red panda eating bamboo in a misty forest, cinematic 4k.",
            config=types.GenerateVideosConfig(
                number_of_videos=1,
            ),
        )

        print(f"Operation started: {operation.name}")
        print("Polling for completion (this may take a while)...")

        # Poll operation
        while not operation.done:
            time.sleep(10)
            print(".", end="", flush=True)
            operation = client.operations.get(operation)
        print("\nOperation complete!")

        if operation.result and operation.result.generated_videos:
            print(f"Generated {len(operation.result.generated_videos)} video(s).")
            for i, generated_video in enumerate(operation.result.generated_videos):
                video = generated_video.video

                if video.uri:
                    print(f"Video {i+1} is available at URI: {video.uri}")
                elif video.video_bytes:  # Checking for video_bytes based on some SDK versions using this name for raw data
                    filename = os.path.join(output_dir, f"veo_3_video_{i+1}.mp4")
                    with open(filename, "wb") as f:
                        f.write(video.video_bytes)
                    print(f"Saved video to: {filename}")
                elif (
                    hasattr(video, "data") and video.data
                ):  # Fallback to 'data' if video_bytes isn't it
                    filename = os.path.join(output_dir, f"veo_3_video_{i+1}.mp4")
                    with open(filename, "wb") as f:
                        f.write(video.data)
                    print(f"Saved video to: {filename}")
                else:
                    # Fallback: try to use .save() if it exists, just in case
                    filename = os.path.join(output_dir, f"veo_3_video_{i+1}.mp4")
                    try:
                        video.save(filename)
                        print(f"Saved video to: {filename}")
                    except Exception as e:
                        print(f"Could not save video {i+1}. Details: {video}")
                        print(f"Save error: {e}")
        else:
            print("No videos generated or operation failed.")
            if operation.error:
                print(f"Operation error: {operation.error}")

    except Exception as e:
        print(f"\nError generating video: {e}")
        if "400" in str(e) or "500" in str(e) or "404" in str(e):
            print(
                "\nNote: Veo 3 on the Gemini Developer API might require allowlisting or Vertex AI."
            )


if __name__ == "__main__":
    main()
