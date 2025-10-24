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
Gemini 2.5 Flash Image model to generate images.
"""

import os
import logging
import io
from PIL import Image
from dotenv import load_dotenv

from ai_tokentrace import TrackedGenaiClient


def main():
    """
    Generates an image using Gemini 2.5 Flash Image and prints the token usage.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Gemini 2.5 Flash Image Example ---")

    client = TrackedGenaiClient()

    # Ensure output directory exists
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Gemini 2.5 Flash Image uses generate_content to produce images.
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents="A cute baby capybara wearing a tiny top hat, watercolor style.",
        )

        print("\n--- Generation Successful ---")

        image_count = 0
        if (
            response.candidates
            and response.candidates[0].content
            and response.candidates[0].content.parts
        ):
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_count += 1
                    print(
                        f"Found generated image (MIME type: {part.inline_data.mime_type})"
                    )

                    # Save the image
                    img = Image.open(io.BytesIO(part.inline_data.data))
                    filename = os.path.join(
                        output_dir, f"gemini_flash_image_{image_count}.png"
                    )
                    img.save(filename)
                    print(f"Saved image to: {filename}")

                elif part.text:
                    print(f"Text response: {part.text}")

        if image_count > 0:
            print(f"Total images generated: {image_count}")
        else:
            print("No images found in response.")

        print("-----------------------------\n")

    except Exception as e:
        print(f"\nError generating content: {e}")


if __name__ == "__main__":
    main()
