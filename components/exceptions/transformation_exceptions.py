"""
Transformation exception classes for text processing operations.

Provides specialized exceptions for different types of transformation failures
with enhanced context for debugging and recovery.
"""

from typing import Any, Dict, List, Optional, Union
from .base_exceptions import BaseTextProcessingError


class TransformationError(BaseTextProcessingError):
    """Base exception for all transformation operation failures.

    Used for general transformation errors during text processing operations.
    """

    def __init__(
        self,
        message: str,
        rule_name: Optional[str] = None,
        input_length: Optional[int] = None,
        processing_stage: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize transformation error.

        Args:
            message: Error description
            rule_name: Name of the transformation rule that failed
            input_length: Length of input text that was being processed
            processing_stage: Stage of processing where error occurred
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if rule_name:
            self.add_context("rule_name", rule_name)
        if input_length is not None:
            self.add_context("input_length", input_length)
        if processing_stage:
            self.add_context("processing_stage", processing_stage)


class TransformationTimeoutError(TransformationError):
    """Exception for transformation operations that exceed time limits."""

    def __init__(
        self,
        message: str,
        timeout_seconds: float,
        elapsed_seconds: Optional[float] = None,
        **kwargs
    ) -> None:
        """Initialize transformation timeout error.

        Args:
            message: Error description
            timeout_seconds: The timeout limit that was exceeded
            elapsed_seconds: Actual time elapsed before timeout
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.add_context("timeout_seconds", timeout_seconds)
        if elapsed_seconds is not None:
            self.add_context("elapsed_seconds", elapsed_seconds)


class TransformationRuleError(TransformationError):
    """Exception for transformation rule-specific errors."""

    def __init__(
        self,
        message: str,
        rule_name: str,
        rule_args: Optional[List[str]] = None,
        available_rules: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """Initialize transformation rule error.

        Args:
            message: Error description
            rule_name: Name of the problematic rule
            rule_args: Arguments provided to the rule
            available_rules: List of available rules for reference
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, rule_name=rule_name, **kwargs)

        if rule_args:
            self.add_context("rule_args", rule_args)
        if available_rules:
            self.add_context("available_rules", available_rules)


class EncodingTransformationError(TransformationError):
    """Exception for character encoding transformation failures."""

    def __init__(
        self,
        message: str,
        source_encoding: Optional[str] = None,
        target_encoding: Optional[str] = None,
        error_position: Optional[int] = None,
        encoding_confidence: Optional[float] = None,
        **kwargs
    ) -> None:
        """Initialize encoding transformation error.

        Args:
            message: Error description
            source_encoding: Source character encoding
            target_encoding: Target character encoding
            error_position: Position in text where error occurred
            encoding_confidence: Confidence level of encoding detection
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if source_encoding:
            self.add_context("source_encoding", source_encoding)
        if target_encoding:
            self.add_context("target_encoding", target_encoding)
        if error_position is not None:
            self.add_context("error_position", error_position)
        if encoding_confidence is not None:
            self.add_context("encoding_confidence", encoding_confidence)


class CryptoTransformationError(TransformationError):
    """Exception for cryptographic transformation failures."""

    def __init__(
        self,
        message: str,
        crypto_operation: Optional[str] = None,
        algorithm: Optional[str] = None,
        key_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Initialize crypto transformation error.

        Args:
            message: Error description
            crypto_operation: Type of crypto operation (encrypt/decrypt/hash)
            algorithm: Cryptographic algorithm used
            key_info: Non-sensitive key information (length, type, etc.)
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)

        if crypto_operation:
            self.add_context("crypto_operation", crypto_operation)
        if algorithm:
            self.add_context("algorithm", algorithm)
        if key_info:
            # Ensure no sensitive key data is included
            safe_key_info = {
                k: v for k, v in key_info.items()
                if k.lower() not in ('key', 'secret', 'password', 'passphrase')
            }
            self.add_context("key_info", safe_key_info)
