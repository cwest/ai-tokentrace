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
Imagen 4 model to generate images.
"""

import os
import logging
from dotenv import load_dotenv
from google.genai import types

from ai_tokentrace import TrackedGenaiClient


def main():
    """
    Generates an image using Imagen 4 and prints the token usage (if available).
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    print("--- Running Imagen 4 Example ---")

    client = TrackedGenaiClient()

    # Ensure output directory exists
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Imagen models use generate_images with the 'prompt' parameter.
        response = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt="A photorealistic landscape of a futuristic city at sunset.",
            config=types.GenerateImagesConfig(
                number_of_images=1,
            ),
        )

        print("\n--- Image Generation Successful ---")
        if response.generated_images:
            print(f"Generated {len(response.generated_images)} image(s).")
            for i, generated_image in enumerate(response.generated_images):
                # The SDK typically returns an object with an .image attribute that is a PIL Image
                img = generated_image.image
                filename = os.path.join(output_dir, f"imagen_4_image_{i+1}.png")
                img.save(filename)
                print(f"Saved image to: {filename}")
        else:
            print("No images generated.")
        print("-----------------------------------\n")

    except Exception as e:
        print(f"\nError generating image: {e}")
        print(
            "\nNote: If you receive a 400/500 error, ensure your API key has access to Imagen 4."
        )


if __name__ == "__main__":
    main()
