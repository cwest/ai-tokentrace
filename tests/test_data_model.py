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

import pytest
from pydantic import ValidationError

from ai_tokentrace.data_model import TokenUsageRecord


def test_token_usage_record_api_key_success():
    """
    Tests that a TokenUsageRecord can be successfully created with the
    'api_key' authentication method.
    """
    record = TokenUsageRecord(
        model_name="gemini-2.5-pro",
        method_name="generate_content",
        authentication_method="api_key",
        input_tokens=10,
        output_tokens=20,
    )
    assert record.authentication_method == "api_key"
    assert record.project_id is None
    assert record.location is None


def test_token_usage_record_vertex_ai_success():
    """
    Tests that a TokenUsageRecord can be successfully created with a
    Vertex AI authentication method and the required fields.
    """
    record = TokenUsageRecord(
        model_name="gemini-2.5-pro",
        method_name="generate_content",
        authentication_method="service_account",
        project_id="my-project",
        location="us-central1",
        input_tokens=10,
        output_tokens=20,
    )
    assert record.authentication_method == "service_account"
    assert record.project_id == "my-project"
    assert record.location == "us-central1"


def test_token_usage_record_vertex_ai_missing_fields():
    """
    Tests that a ValidationError is raised when a Vertex AI
    authentication method is used without the required 'project_id' and
    'location' fields.
    """
    with pytest.raises(ValidationError):
        TokenUsageRecord(
            model_name="gemini-2.5-pro",
            method_name="generate_content",
            authentication_method="adc",
            input_tokens=10,
            output_tokens=20,
        )


def test_token_usage_record_thinking_tokens():
    """
    Tests that thinking_tokens can be set.
    """
    record = TokenUsageRecord(
        model_name="gemini-2.5-pro",
        method_name="generate_content",
        authentication_method="api_key",
        input_tokens=10,
        output_tokens=20,
        thinking_tokens=5,
    )
    assert record.thinking_tokens == 5


def test_token_usage_record_images_generated():
    """
    Tests that images_generated can be set and defaults to 0.
    """
    # Default case
    record_default = TokenUsageRecord(
        model_name="gemini-2.5-pro",
        method_name="generate_content",
        authentication_method="api_key",
        input_tokens=10,
        output_tokens=20,
    )
    assert record_default.images_generated == 0

    # Explicit case
    record_explicit = TokenUsageRecord(
        model_name="imagen-3",
        method_name="generate_images",
        authentication_method="api_key",
        input_tokens=0,
        output_tokens=0,
        images_generated=2,
    )
    assert record_explicit.images_generated == 2


def test_token_usage_record_all_fields():
    """
    Tests that all optional fields can be set correctly.
    """
    record = TokenUsageRecord(
        model_name="gemini-2.5-pro",
        method_name="generate_content",
        authentication_method="api_key",
        input_tokens=100,
        output_tokens=200,
        thinking_tokens=50,
        cached_content_tokens=1000,
        tool_use_prompt_tokens=20,
        images_generated=1,
        videos_generated=1,
    )
    assert record.thinking_tokens == 50
    assert record.cached_content_tokens == 1000
    assert record.tool_use_prompt_tokens == 20
    assert record.images_generated == 1
    assert record.videos_generated == 1
