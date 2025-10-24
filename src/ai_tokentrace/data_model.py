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

from datetime import datetime, UTC
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class TokenUsageRecord(BaseModel):
    """
    A Pydantic model representing a single record of token usage.
    """

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    agent_name: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    model_name: str
    method_name: str
    authentication_method: Literal["api_key", "service_account", "adc"]
    project_id: Optional[str] = None
    location: Optional[str] = None
    input_tokens: int
    output_tokens: int
    thinking_tokens: Optional[int] = None
    cached_content_tokens: Optional[int] = None
    tool_use_prompt_tokens: Optional[int] = None
    images_generated: int = 0
    videos_generated: int = 0

    @model_validator(mode="after")
    def check_vertex_ai_fields(self):
        if self.authentication_method in ["service_account", "adc"]:
            if not self.project_id or not self.location:
                raise ValueError(
                    "project_id and location are required for Vertex AI authentication methods"
                )
        return self
