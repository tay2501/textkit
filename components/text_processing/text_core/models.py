"""
Pydantic models for text processing requests and responses.

This module contains all Pydantic models used for data validation
and serialization throughout the text processing toolkit.
"""

from __future__ import annotations

from typing import Annotated, Optional, Any, Dict, List
from pydantic import BaseModel, Field, field_validator, ConfigDict, ValidationInfo
import structlog

# Logger for validation messages
logger = structlog.get_logger(__name__)


class TextTransformationRequest(BaseModel):
    """Pydantic model for text transformation requests.

    Uses modern Pydantic v2 patterns for comprehensive validation.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid',
        frozen=False  # Allow mutation for processing
    )

    text: Annotated[str, Field(
        min_length=0,  # Allow empty text for edge cases
        max_length=10_000_000,  # 10MB text limit
        description="Input text to be transformed"
    )]

    rule_string: Annotated[str, Field(
        min_length=1,
        pattern=r'^[/-].*',
        description="Transformation rule string (must start with / or -)"
    )]

    config_override: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional configuration overrides"
    )

    @field_validator('rule_string', mode='after')
    @classmethod
    def validate_rule_format(cls, v: str, info: ValidationInfo) -> str:
        """Enhanced validation for rule string format."""
        if not v.strip():
            raise ValueError("Rule string cannot be empty")

        # Check for balanced quotes if present
        if "'" in v or '"' in v:
            single_quotes = v.count("'")
            double_quotes = v.count('"')

            if single_quotes % 2 != 0:
                raise ValueError("Unbalanced single quotes in rule string")
            if double_quotes % 2 != 0:
                raise ValueError("Unbalanced double quotes in rule string")

        # Log rule validation for monitoring
        logger.debug(
            "rule_validation_passed",
            rule_string=v,
            validation_context=info.data
        )

        return v

    @field_validator('text', mode='after')
    @classmethod
    def validate_text_content(cls, v: str, info: ValidationInfo) -> str:
        """Validate text content for potential issues."""
        # Check for extremely long lines that might cause performance issues
        lines = v.split('\n')
        max_line_length = 100_000  # 100k chars per line

        for i, line in enumerate(lines):
            if len(line) > max_line_length:
                logger.warning(
                    "very_long_line_detected",
                    line_number=i + 1,
                    line_length=len(line),
                    max_allowed=max_line_length
                )

        return v


class TextTransformationResponse(BaseModel):
    """Pydantic model for text transformation responses."""

    model_config = ConfigDict(
        frozen=True,  # Immutable response
        extra='forbid'
    )

    transformed_text: str = Field(
        description="The transformed text result"
    )

    applied_rules: List[str] = Field(
        description="List of rules that were applied"
    )

    processing_time_ms: float = Field(
        ge=0.0,
        description="Processing time in milliseconds"
    )

    warnings: Optional[List[str]] = Field(
        default=None,
        description="Any warnings generated during processing"
    )


class RuleValidationRequest(BaseModel):
    """Pydantic model for rule validation requests."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )

    rule_string: Annotated[str, Field(
        min_length=1,
        description="Rule string to validate"
    )]

    strict_mode: bool = Field(
        default=True,
        description="Whether to use strict validation"
    )


class RuleValidationResponse(BaseModel):
    """Pydantic model for rule validation responses."""

    model_config = ConfigDict(
        frozen=True,
        extra='forbid'
    )

    is_valid: bool = Field(
        description="Whether the rule string is valid"
    )

    parsed_rules: Optional[List[tuple[str, List[str]]]] = Field(
        default=None,
        description="Parsed rules if validation succeeded"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error message if validation failed"
    )

    suggestions: Optional[List[str]] = Field(
        default=None,
        description="Suggestions for fixing invalid rules"
    )


class ConfigurationModel(BaseModel):
    """Pydantic model for application configuration."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='allow'  # Allow additional config fields
    )

    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    max_text_length: Annotated[int, Field(
        gt=0,
        le=100_000_000,  # 100MB limit
        description="Maximum allowed text length"
    )] = 10_000_000

    auto_clipboard_monitoring: bool = Field(
        default=False,
        description="Enable automatic clipboard monitoring"
    )

    clipboard_check_interval: Annotated[float, Field(
        ge=0.1,
        le=10.0,
        description="Clipboard check interval in seconds"
    )] = 1.0

    enable_crypto: bool = Field(
        default=True,
        description="Enable cryptographic features"
    )

    log_level: str = Field(
        default="INFO",
        pattern=r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$',
        description="Logging level"
    )

    @field_validator('max_text_length', mode='after')
    @classmethod
    def validate_memory_implications(cls, v: int) -> int:
        """Validate text length against memory constraints."""
        # Rough estimate: 1 char = 1 byte + Python overhead
        estimated_memory_mb = (v * 4) / (1024 * 1024)  # 4x overhead estimate

        if estimated_memory_mb > 1000:  # 1GB warning
            logger.warning(
                "high_memory_configuration",
                max_text_length=v,
                estimated_memory_mb=estimated_memory_mb
            )

        return v