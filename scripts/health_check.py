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

"""Health check script for Google Cloud emulators."""

import os
import sys
import time

from google.api_core import exceptions
from google.cloud import firestore
from google.cloud import pubsub_v1


def check_firestore():
    """Checks if the Firestore emulator is available."""
    try:
        client = firestore.Client()
        # The collection and document names don't matter, this is just to check
        # the connection.
        client.collection("health").document("check").set({"status": "ok"})
        return True
    except exceptions.ServiceUnavailable:
        return False
    except Exception as e:
        print(
            f"An unexpected error occurred while checking Firestore: {e}",
            file=sys.stderr,
        )
        return False


def check_pubsub():
    """Checks if the Pub/Sub emulator is available."""
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "test-project-id")
        client = pubsub_v1.PublisherClient()
        client.list_topics(request={"project": f"projects/{project_id}"})
        return True
    except exceptions.ServiceUnavailable:
        return False
    except Exception as e:
        print(
            f"An unexpected error occurred while checking Pub/Sub: {e}", file=sys.stderr
        )
        return False


def main():
    """Waits for emulators to be ready."""
    print("--- Waiting for emulators to start ---")
    max_wait = 30  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        firestore_ready = check_firestore()
        pubsub_ready = check_pubsub()

        if firestore_ready and pubsub_ready:
            print("--- Emulators are ready! ---")
            return

        print(
            f"Firestore ready: {firestore_ready}, Pub/Sub ready: {pubsub_ready}. "
            "Retrying in 2 seconds..."
        )
        time.sleep(2)

    print("--- Emulators did not start in time. ---", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
