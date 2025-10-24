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
"""Core service definitions for exporting token usage data.

This module defines the concrete implementations for the token usage export
services. It provides both synchronous and asynchronous classes for each backend
(e.g., Logging, Firestore).

The synchronous classes are lightweight, non-blocking wrappers that instantiate
and manage their asynchronous counterparts in a background thread, providing a
user-friendly API for all application types.
"""

import logging
from pathlib import Path
from typing import Protocol, runtime_checkable

import aiofiles

from .async_utils import run_async_in_background
from .data_model import TokenUsageRecord

_logger = logging.getLogger(__name__)


@runtime_checkable
class TokenUsageService(Protocol):
    """Protocol defining the interface for a synchronous token usage service."""

    def export(self, record: TokenUsageRecord) -> None:
        """Exports a token usage record."""
        ...


# --- Global Service Management ---

_global_service: TokenUsageService | None = None


def get_global_service() -> TokenUsageService:
    """Returns the global TokenUsageService, creating a default one if necessary."""
    global _global_service
    if _global_service is None:
        _global_service = LoggingTokenUsageService()
    return _global_service


def set_global_service(service: TokenUsageService) -> None:
    """Sets the global TokenUsageService."""
    global _global_service
    _global_service = service


# --- Logging Services ---


class _BaseLoggingService:
    """Base class for logging services, holding shared configuration."""

    def __init__(self, logger_name: str = "ai_tokentrace"):
        self._logger_name = logger_name


class AsyncLoggingTokenUsageService(_BaseLoggingService):
    """Asynchronously logs token usage records to the standard logger.

    This service provides an async `export` method for non-blocking logging
    in asynchronous applications.
    """

    def __init__(self, logger_name: str = "ai_tokentrace"):
        """Initializes the async logging service.

        Args:
            logger_name: The name of the logger to use (defaults to "ai_tokentrace").
        """
        super().__init__(logger_name)
        self._logger = logging.getLogger(self._logger_name)

    async def export(self, record: TokenUsageRecord) -> None:
        """Asynchronously logs the token usage record as a JSON string.

        Args:
            record: The `TokenUsageRecord` to export.
        """
        self._logger.info(record.model_dump_json())


class LoggingTokenUsageService(_BaseLoggingService):
    """Synchronously logs token usage records in a non-blocking manner.

    This service provides a standard synchronous `export` method that is safe
    to call from any application without blocking the main thread.
    """

    def __init__(self, logger_name: str = "ai_tokentrace"):
        """Initializes the sync logging service.

        Args:
            logger_name: The name of the logger to use (defaults to "ai_tokentrace").
        """
        super().__init__(logger_name)
        self._async_service = AsyncLoggingTokenUsageService(self._logger_name)

    def export(self, record: TokenUsageRecord) -> None:
        """Synchronously logs a record in a non-blocking, fire-and-forget manner.

        Args:
            record: The `TokenUsageRecord` to export.
        """
        run_async_in_background(self._async_service.export(record))


# --- JSONL File Services ---


class _BaseJsonlFileService:
    """Base class for JSONL file services, holding shared configuration."""

    def __init__(self, file_path: Path | str):
        self._file_path = Path(file_path)


class AsyncJsonlFileTokenUsageService(_BaseJsonlFileService):
    """Asynchronously appends token usage records to a JSON Lines file."""

    def __init__(self, file_path: Path | str):
        """Initializes the async JSONL file service.

        Args:
            file_path: The path to the JSONL file.
        """
        super().__init__(file_path)

    async def export(self, record: TokenUsageRecord) -> None:
        """Asynchronously appends the record as a new line in the JSONL file.

        Args:
            record: The `TokenUsageRecord` to export.
        """
        try:
            async with aiofiles.open(self._file_path, "a", encoding="utf-8") as f:
                await f.write(record.model_dump_json() + "\n")
        except Exception:
            _logger.exception("Failed to export token usage record to JSONL file.")


class JsonlFileTokenUsageService(_BaseJsonlFileService):
    """Synchronously appends token usage records to a JSON Lines file."""

    def __init__(self, file_path: Path | str):
        """Initializes the sync JSONL file service.

        Args:
            file_path: The path to the JSONL file.
        """
        super().__init__(file_path)
        self._async_service = AsyncJsonlFileTokenUsageService(self._file_path)

    def export(self, record: TokenUsageRecord) -> None:
        """Synchronously appends a record in a non-blocking, fire-and-forget manner.

        Args:
            record: The `TokenUsageRecord` to export.
        """
        run_async_in_background(self._async_service.export(record))


# --- Firestore Services ---


class _BaseFirestoreService:
    """Base class for Firestore services, holding shared configuration."""

    def __init__(self, collection_name: str = "token_usage_records"):
        self._collection_name = collection_name


class AsyncFirestoreTokenUsageService(_BaseFirestoreService):
    """Asynchronously exports token usage records to Google Cloud Firestore."""

    def __init__(self, collection_name: str = "token_usage_records"):
        """Initializes the async Firestore service.

        Args:
            collection_name: The name of the Firestore collection to use.
        """
        super().__init__(collection_name)
        try:
            from google.cloud.firestore import AsyncClient
        except ImportError:
            raise ImportError(
                "The 'google-cloud-firestore' library is required to use this service. "
                "Please install it with: pip install 'ai-tokentrace[firestore]' "
                "(or uv pip install 'ai-tokentrace[firestore]')"
            )
        self._client = AsyncClient()
        self._collection = self._client.collection(self._collection_name)

    async def export(self, record: TokenUsageRecord) -> None:
        """Asynchronously exports the record to a new document in the Firestore collection.

        Args:
            record: The `TokenUsageRecord` to export.
        """
        try:
            await self._collection.add(record.model_dump())
        except Exception:
            _logger.exception("Failed to export token usage record to Firestore.")


class FirestoreTokenUsageService(_BaseFirestoreService):
    """Synchronously exports token usage records to Google Cloud Firestore."""

    def __init__(self, collection_name: str = "token_usage_records"):
        """Initializes the sync Firestore service.

        Args:
            collection_name: The name of the Firestore collection to use.
        """
        super().__init__(collection_name)
        self._async_service = AsyncFirestoreTokenUsageService(self._collection_name)

    def export(self, record: TokenUsageRecord) -> None:
        """Synchronously exports a record in a non-blocking, fire-and-forget manner.

        Args:
            record: The `TokenUsageRecord` to export.
        """
        run_async_in_background(self._async_service.export(record))


# --- Pub/Sub Services ---


class _BasePubSubService:
    """Base class for Pub/Sub services, holding shared configuration."""

    def __init__(self, topic_id: str, project_id: str):
        self._topic_id = topic_id
        self._project_id = project_id


class AsyncPubSubTokenUsageService(_BasePubSubService):
    """Asynchronously publishes token usage records to a Google Cloud Pub/Sub topic."""

    def __init__(self, topic_id: str, project_id: str):
        """Initializes the async Pub/Sub service.

        Args:
            topic_id: The ID of the Pub/Sub topic to publish to.
            project_id: The Google Cloud project ID.
        """
        super().__init__(topic_id, project_id)
        try:
            from google.cloud.pubsub_v1 import PublisherClient
        except ImportError:
            raise ImportError(
                "The 'google-cloud-pubsub' library is required to use this service. "
                "Please install it with: pip install 'ai-tokentrace[pubsub]' "
                "(or uv pip install 'ai-tokentrace[pubsub]')"
            )

        self._publisher = PublisherClient()
        self._topic_path = self._publisher.topic_path(self._project_id, self._topic_id)

    async def export(self, record: TokenUsageRecord) -> None:
        """Asynchronously publishes the record as a message to the Pub/Sub topic.

        Args:
            record: The `TokenUsageRecord` to export.
        """
        try:
            future = self._publisher.publish(
                self._topic_path, data=record.model_dump_json().encode("utf-8")
            )
            future.result()
        except Exception:
            _logger.exception("Failed to publish token usage record to Pub/Sub.")


class PubSubTokenUsageService(_BasePubSubService):
    """Synchronously publishes token usage records to a Google Cloud Pub/Sub topic."""

    def __init__(self, topic_id: str, project_id: str):
        """Initializes the sync Pub/Sub service.

        Args:
            topic_id: The ID of the Pub/Sub topic to publish to.
            project_id: The Google Cloud project ID.
        """
        super().__init__(topic_id, project_id)
        self._async_service = AsyncPubSubTokenUsageService(
            self._topic_id, self._project_id
        )

    def export(self, record: TokenUsageRecord) -> None:
        """Synchronously publishes a record in a non-blocking, fire-and-forget manner.

        Args:
            record: The `TokenUsageRecord` to export.
        """
        run_async_in_background(self._async_service.export(record))
