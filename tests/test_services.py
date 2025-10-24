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
"""Unit tests for the token usage export services."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from ai_tokentrace.data_model import TokenUsageRecord
from ai_tokentrace.services import (
    AsyncFirestoreTokenUsageService,
    AsyncJsonlFileTokenUsageService,
    AsyncLoggingTokenUsageService,
    AsyncPubSubTokenUsageService,
    FirestoreTokenUsageService,
    JsonlFileTokenUsageService,
    LoggingTokenUsageService,
    PubSubTokenUsageService,
)

# --- Fixtures ---


@pytest.fixture
def sample_record() -> TokenUsageRecord:
    """Provides a sample TokenUsageRecord for testing."""
    return TokenUsageRecord(
        model_name="gemini-2.5-pro",
        method_name="generate_content",
        authentication_method="api_key",
        input_tokens=10,
        output_tokens=20,
    )


# --- Logging Service Tests ---


@patch("ai_tokentrace.services.logging.getLogger")
async def test_async_logging_service_export(
    mock_get_logger: MagicMock, sample_record: TokenUsageRecord
):
    """Verifies that the async logging service logs the record correctly."""
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    service = AsyncLoggingTokenUsageService(logger_name="test_logger")

    await service.export(sample_record)

    mock_get_logger.assert_called_once_with("test_logger")
    mock_logger.info.assert_called_once_with(sample_record.model_dump_json())


@patch("ai_tokentrace.services.run_async_in_background")
def test_sync_logging_service_export(
    mock_run_async: MagicMock,
    sample_record: TokenUsageRecord,
):
    """Verifies that the sync logging service correctly calls the async wrapper."""
    service = LoggingTokenUsageService(logger_name="test_logger")
    # Replace the real async method with a mock to check the call
    service._async_service.export = MagicMock()

    service.export(sample_record)

    # Verify that the background runner was called with the coroutine
    # that results from calling the mocked async method.
    mock_run_async.assert_called_once_with(service._async_service.export.return_value)
    service._async_service.export.assert_called_once_with(sample_record)


# --- JSONL File Service Tests ---


@patch("ai_tokentrace.services.aiofiles.open")
async def test_async_jsonl_service_export(
    mock_aio_open: MagicMock, tmp_path: Path, sample_record: TokenUsageRecord
):
    """Verifies that the async JSONL service writes the record correctly."""
    file_path = tmp_path / "test.jsonl"
    mock_async_file = AsyncMock()
    mock_aio_open.return_value = mock_async_file

    service = AsyncJsonlFileTokenUsageService(file_path=file_path)
    await service.export(sample_record)

    mock_aio_open.assert_called_once_with(file_path, "a", encoding="utf-8")
    mock_async_file.__aenter__.return_value.write.assert_called_once_with(
        sample_record.model_dump_json() + "\n"
    )


@patch("ai_tokentrace.services.run_async_in_background")
def test_sync_jsonl_service_export(
    mock_run_async: MagicMock, tmp_path: Path, sample_record: TokenUsageRecord
):
    """Verifies that the sync JSONL service correctly calls the async wrapper."""
    file_path = tmp_path / "test.jsonl"
    service = JsonlFileTokenUsageService(file_path=file_path)
    service._async_service.export = MagicMock()

    service.export(sample_record)

    mock_run_async.assert_called_once_with(service._async_service.export.return_value)
    service._async_service.export.assert_called_once_with(sample_record)


# --- Firestore Service Tests ---


@patch("google.cloud.firestore_v1.async_client.AsyncClient.__init__", return_value=None)
async def test_async_firestore_service_export(
    mock_client_init: MagicMock, sample_record: TokenUsageRecord
):
    """Verifies that the async Firestore service exports the record correctly."""
    service = AsyncFirestoreTokenUsageService(collection_name="test_collection")

    # Manually create and assign the mock client instance and its sub-mocks
    mock_client_instance = MagicMock()
    mock_collection = MagicMock()
    mock_collection.add = AsyncMock()
    mock_client_instance.collection.return_value = mock_collection
    service._client = mock_client_instance
    # Re-set the collection since __init__ was mocked
    service._collection = service._client.collection(service._collection_name)

    await service.export(sample_record)

    service._client.collection.assert_called_once_with("test_collection")
    service._collection.add.assert_called_once_with(sample_record.model_dump())


@patch("ai_tokentrace.services.run_async_in_background")
@patch("google.cloud.firestore_v1.async_client.AsyncClient.__init__", return_value=None)
def test_sync_firestore_service_export(
    mock_client_init: MagicMock,
    mock_run_async: MagicMock,
    sample_record: TokenUsageRecord,
):
    """Verifies that the sync Firestore service correctly calls the async wrapper."""
    service = FirestoreTokenUsageService(collection_name="test_collection")
    service._async_service.export = MagicMock()

    service.export(sample_record)

    mock_run_async.assert_called_once_with(service._async_service.export.return_value)
    service._async_service.export.assert_called_once_with(sample_record)


# --- Pub/Sub Service Tests ---


@patch("google.cloud.pubsub_v1.PublisherClient.__init__", return_value=None)
async def test_async_pubsub_service_export(
    mock_client_init: MagicMock, sample_record: TokenUsageRecord
):
    """Verifies that the async Pub/Sub service exports the record correctly."""
    service = AsyncPubSubTokenUsageService(
        topic_id="test-topic", project_id="test-proj"
    )

    # Manually create and assign the mock publisher instance
    mock_publisher_instance = MagicMock()
    mock_publisher_instance.publish.return_value = MagicMock()  # Mock the future
    mock_publisher_instance.topic_path.return_value = (
        "projects/test-proj/topics/test-topic"
    )
    service._publisher = mock_publisher_instance
    # Re-set the topic path since __init__ was mocked
    service._topic_path = service._publisher.topic_path(
        service._project_id, service._topic_id
    )

    await service.export(sample_record)

    service._publisher.topic_path.assert_called_once_with("test-proj", "test-topic")
    service._publisher.publish.assert_called_once_with(
        "projects/test-proj/topics/test-topic",
        data=sample_record.model_dump_json().encode("utf-8"),
    )


@patch("ai_tokentrace.services.run_async_in_background")
@patch("google.cloud.pubsub_v1.PublisherClient.__init__", return_value=None)
def test_sync_pubsub_service_export(
    mock_client_init: MagicMock,
    mock_run_async: MagicMock,
    sample_record: TokenUsageRecord,
):
    """Verifies that the sync Pub/Sub service correctly calls the async wrapper."""
    service = PubSubTokenUsageService(topic_id="test-topic", project_id="test-proj")
    service._async_service.export = MagicMock()

    service.export(sample_record)

    mock_run_async.assert_called_once_with(service._async_service.export.return_value)
    service._async_service.export.assert_called_once_with(sample_record)
