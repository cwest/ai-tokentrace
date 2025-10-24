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
AsyncPubSubTokenUsageService.

NOTE: This example requires a Pub/Sub emulator to be running locally
if you don't have Google Cloud credentials configured.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.api_core.exceptions import AlreadyExists

from ai_tokentrace import TrackedGenaiClient
from ai_tokentrace.services import AsyncPubSubTokenUsageService


def create_topic_if_not_exists(project_id: str, topic_id: str):
    """Creates a Pub/Sub topic if it doesn't already exist."""
    publisher = PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    try:
        publisher.create_topic(request={"name": topic_path})
        print(f"Created topic: {topic_path}")
    except AlreadyExists:
        print(f"Topic already exists: {topic_path}")
    except Exception as e:
        print(f"Error creating topic: {e}")


def ensure_subscription(project_id: str, topic_id: str, subscription_id: str):
    """Ensures a subscription exists for the topic."""
    subscriber = SubscriberClient()
    topic_path = subscriber.topic_path(project_id, topic_id)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    try:
        subscriber.create_subscription(
            request={"name": subscription_path, "topic": topic_path}
        )
        print(f"Created subscription: {subscription_path}")
    except AlreadyExists:
        print(f"Subscription already exists: {subscription_path}")
    except Exception as e:
        print(f"Error creating subscription: {e}")
    finally:
        subscriber.close()


def pull_and_verify_message(project_id: str, subscription_id: str):
    """Pulls and verifies the message from the subscription."""
    subscriber = SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    print("Pulling message from subscription...")
    try:
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": 1},
            timeout=5.0,
        )

        if response.received_messages:
            for received_message in response.received_messages:
                print("\n--- Verified Pub/Sub Message ---")
                print(f"Data: {received_message.message.data.decode('utf-8')}")
                print("--------------------------------\n")
                subscriber.acknowledge(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": [received_message.ack_id],
                    }
                )
        else:
            print("No messages received during verification.")

    except Exception as e:
        print(f"Error pulling message: {e}")
    finally:
        subscriber.close()


async def main():
    """
    Generates content and publishes token usage to Pub/Sub asynchronously.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    # Check for Pub/Sub emulator or credentials
    if not os.getenv("PUBSUB_EMULATOR_HOST") and not os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    ):
        print(
            "WARNING: Neither PUBSUB_EMULATOR_HOST nor GOOGLE_APPLICATION_CREDENTIALS is set."
        )
        print("This example might fail if it cannot authenticate to Pub/Sub.")

    print("--- Running Async Pub/Sub Service Example ---")

    # Set project and topic for the example.
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "demo-project")
    topic_id = "token-usage-topic-async"
    subscription_id = "token-usage-sub-async"

    # Ensure topic and subscription exist
    create_topic_if_not_exists(project_id, topic_id)
    ensure_subscription(project_id, topic_id, subscription_id)

    # Initialize the async service
    service = AsyncPubSubTokenUsageService(topic_id=topic_id, project_id=project_id)
    print(f"Token usage will be published to: projects/{project_id}/topics/{topic_id}")

    # Initialize the client with the service and use async context manager
    async with TrackedGenaiClient(service=service) as client:
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents="Tell me a joke about event-driven architecture.",
            )

            print("\n--- Model Response ---")
            print(response.text)
            print("----------------------\n")
            print("Token usage record published to Pub/Sub.")

        except Exception as e:
            print(f"\nError: {e}")
            print("Ensure Pub/Sub is reachable and the topic exists.")

    # Verify message was published
    await asyncio.to_thread(pull_and_verify_message, project_id, subscription_id)


if __name__ == "__main__":
    asyncio.run(main())
