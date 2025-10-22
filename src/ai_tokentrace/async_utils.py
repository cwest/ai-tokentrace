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
"""Utilities for managing asynchronous operations."""

import asyncio
import atexit
import threading
from collections.abc import Coroutine


class _AsyncManager:
    """Manages a dedicated event loop on a background thread."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
            self.thread.start()
            atexit.register(self.shutdown)
            self._initialized = True

    def submit(self, coro: Coroutine) -> None:
        """Submits a coroutine to the background event loop.

        This is a fire-and-forget operation.

        Args:
            coro: The coroutine to run.
        """
        self.loop.call_soon_threadsafe(asyncio.create_task, coro)

    def shutdown(self):
        """Shuts down the background event loop."""
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=2)


def run_async_in_background(coro: Coroutine) -> None:
    """Runs a coroutine on a background event loop without blocking.

    Args:
        coro: The coroutine to run.
    """
    manager = _AsyncManager()
    manager.submit(coro)
