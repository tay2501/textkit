"""Test suite for CryptoTransformations validation improvements."""

import base64

import pytest

from components.crypto_engine.crypto_transformations import CryptoTransformations
from projects.textkit.exceptions import TransformationError


class TestCryptoTransformationsValidation:
    """Test suite for input validation in CryptoTransformations."""

    def test_decrypt_empty_text_raises_error(self):
        """Test that decrypting empty text raises TransformationError."""
        crypto = CryptoTransformations()

        with pytest.raises(
            TransformationError,
            match="No encrypted text provided"
        ):
            crypto.decrypt_text("")

    def test_decrypt_whitespace_only_text_raises_error(self):
        """Test that decrypting whitespace-only text raises TransformationError."""
        crypto = CryptoTransformations()

        with pytest.raises(
            TransformationError,
            match="No encrypted text provided"
        ):
            crypto.decrypt_text("   ")

    def test_decrypt_without_crypto_manager_raises_error(self):
        """Test that decrypting without crypto manager raises TransformationError."""
        crypto = CryptoTransformations()

        with pytest.raises(
            TransformationError,
            match="Cryptography manager not configured"
        ):
            crypto.decrypt_text("some_encrypted_text")
