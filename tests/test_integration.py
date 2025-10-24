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
#
"""Integration tests for the token usage export services."""

import asyncio
import json
import os
from datetime import datetime, timezone

import pytest
from ai_tokentrace.data_model import TokenUsageRecord
from ai_tokentrace.services import (
    AsyncFirestoreTokenUsageService,
    AsyncPubSubTokenUsageService,
)
from google.api_core import exceptions
from google.cloud import pubsub_v1
from google.cloud.firestore import AsyncClient

# --- Fixtures ---


@pytest.fixture
def sample_record() -> TokenUsageRecord:
    """Provides a sample TokenUsageRecord for testing."""
    return TokenUsageRecord(
        model_name="gemini-2.5-pro",
        method_name="generate_content",
        authentication_method="api_key",
        input_tokens=15,
        output_tokens=35,
        timestamp=datetime.now(
            timezone.utc
        ),  # Use a fixed timestamp for easier comparison
    )


# --- Firestore Integration Tests ---


@pytest.mark.integration
@pytest.mark.asyncio
async def test_firestore_integration_export(sample_record: TokenUsageRecord):
    """Verifies end-to-end export to the Firestore emulator."""
    collection_name = "integration_test_records"
    service = AsyncFirestoreTokenUsageService(collection_name=collection_name)
    firestore_client = AsyncClient()
    collection_ref = firestore_client.collection(collection_name)

    # 0. Cleanup: Delete all documents in the collection to ensure a clean slate.
    docs = collection_ref.stream()
    async for doc in docs:
        await doc.reference.delete()

    # 1. Export the record
    await service.export(sample_record)

    # 2. Verify the record was written
    # Allow a moment for the write to complete
    await asyncio.sleep(0.1)
    docs = collection_ref.where("model_name", "==", "gemini-2.5-pro").stream()
    found_docs = [doc.to_dict() async for doc in docs]

    assert len(found_docs) == 1
    # Pydantic model dump will have float timestamps
    found_docs[0]["timestamp"] = found_docs[0]["timestamp"].timestamp()
    sample_record_dict = sample_record.model_dump()
    sample_record_dict["timestamp"] = sample_record_dict["timestamp"].timestamp()

    assert found_docs[0] == sample_record_dict


# --- Pub/Sub Integration Tests ---


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pubsub_integration_export(sample_record: TokenUsageRecord):
    """Verifies end-to-end export to the Pub/Sub emulator."""
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    topic_id = "integration-test-topic"
    subscription_id = "integration-test-subscription"

    # Setup: Create Topic and Subscription
    publisher_client = pubsub_v1.PublisherClient()
    subscriber_client = pubsub_v1.SubscriberClient()
    topic_path = publisher_client.topic_path(project_id, topic_id)
    subscription_path = subscriber_client.subscription_path(project_id, subscription_id)

    try:
        publisher_client.create_topic(request={"name": topic_path})
    except exceptions.AlreadyExists:
        pass  # Topic may exist from previous runs

    try:
        subscriber_client.create_subscription(
            request={"name": subscription_path, "topic": topic_path}
        )
    except exceptions.AlreadyExists:
        pass  # Subscription may exist from previous runs

    # 1. Export the record
    service = AsyncPubSubTokenUsageService(topic_id=topic_id, project_id=project_id)
    await service.export(sample_record)

    # 2. Verify the message was published
    response = subscriber_client.pull(
        request={"subscription": subscription_path, "max_messages": 1}
    )

    assert len(response.received_messages) == 1
    message = response.received_messages[0]
    subscriber_client.acknowledge(
        request={"subscription": subscription_path, "ack_ids": [message.ack_id]}
    )

    # The data is a JSON string, so we need to load it
    received_data = json.loads(message.message.data.decode("utf-8"))
    # Timestamps will have different formats, so we compare the parsed versions
    received_timestamp = datetime.fromisoformat(received_data["timestamp"])
    assert received_timestamp.date() == sample_record.timestamp.date()
    assert received_data["model_name"] == sample_record.model_name
    assert received_data["input_tokens"] == sample_record.input_tokens
    assert received_data["output_tokens"] == sample_record.output_tokens
