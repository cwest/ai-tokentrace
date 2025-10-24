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
FirestoreTokenUsageService.

NOTE: This example requires a Firestore emulator to be running locally
if you don't have Google Cloud credentials configured.
"""

import os
import time
import logging
from dotenv import load_dotenv
from google.cloud.firestore import Client, Query

from ai_tokentrace import TrackedGenaiClient
from ai_tokentrace.services import FirestoreTokenUsageService


def verify_document(project_id: str, collection_name: str):
    """Verifies the document by querying the most recent one."""
    client = Client(project=project_id)
    collection = client.collection(collection_name)

    print("Querying Firestore for the most recent document...")
    try:
        # Query for the most recent document based on timestamp
        query = collection.order_by("timestamp", direction=Query.DESCENDING).limit(1)
        docs = list(query.stream())

        if docs:
            for doc in docs:
                print(f"\n--- Verified Firestore Document (ID: {doc.id}) ---")
                print(doc.to_dict())
                print("--------------------------------------------------\n")
        else:
            print("No documents found during verification.")

    except Exception as e:
        print(f"Error querying Firestore: {e}")
    finally:
        client.close()


def main():
    """
    Generates content and saves token usage to Firestore.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    # Check for Firestore emulator or credentials
    if not os.getenv("FIRESTORE_EMULATOR_HOST") and not os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    ):
        print(
            "WARNING: Neither FIRESTORE_EMULATOR_HOST nor GOOGLE_APPLICATION_CREDENTIALS is set."
        )
        print("This example might fail if it cannot authenticate to Firestore.")

    print("--- Running Firestore Service Example ---")

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "demo-project")
    collection_name = "example_token_usage"

    # Initialize the service
    # It will use the 'token_usage_logs' collection by default.
    service = FirestoreTokenUsageService(collection_name=collection_name)
    print(
        f"Token usage will be saved to Firestore collection: {service._collection_name}"
    )

    # Initialize the client with the service
    client = TrackedGenaiClient(service=service)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", contents="Tell me a joke about a database."
        )

        print("\n--- Model Response ---")
        print(response.text)
        print("----------------------\n")
        print("Token usage record saved to Firestore.")

    except Exception as e:
        print(f"\nError: {e}")
        print("Ensure Firestore is reachable (e.g., emulator is running).")

    # Allow background task to complete
    time.sleep(1)

    # Verify document was saved
    verify_document(project_id, collection_name)


if __name__ == "__main__":
    main()
