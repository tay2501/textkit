"""
Parallel cryptographic engine using asyncio for batch operations.

This module provides parallel encryption/decryption capabilities
optimized for Python 3.13+ with async/await and concurrent processing.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast

import structlog
from textkit.crypto_engine import (
    CryptographyManager,  # type: ignore[import-not-found]
)
from textkit.exceptions import (
    CryptoTransformationError,  # type: ignore[import-not-found]
)

logger = structlog.get_logger(__name__)


class ParallelCryptoEngine:
    """
    Parallel encryption engine using asyncio for batch operations.

    This class leverages Python 3.13's async capabilities to provide
    high-throughput batch encryption/decryption with configurable
    concurrency limits.

    Example:
        >>> from textkit.config_manager import ConfigurationManager
        >>> from textkit.crypto_engine import CryptographyManager
        >>> config = ConfigurationManager()
        >>> crypto_manager = CryptographyManager(config)
        >>> engine = ParallelCryptoEngine(crypto_manager, max_workers=4)
        >>> texts = ["Hello", "World", "Parallel", "Crypto"]
        >>> encrypted = await engine.encrypt_batch_async(texts)
        >>> decrypted = await engine.decrypt_batch_async(encrypted)
    """

    def __init__(
        self,
        crypto_manager: CryptographyManager,
        max_workers: int = 4,
    ) -> None:
        """
        Initialize parallel crypto engine.

        Args:
            crypto_manager: CryptographyManager instance for crypto operations
            max_workers: Maximum number of concurrent encryption/decryption tasks
        """
        self.crypto_manager = crypto_manager
        self.max_workers = max_workers
        self._semaphore: asyncio.Semaphore | None = None

    def _get_semaphore(self) -> asyncio.Semaphore:
        """Get or create semaphore for concurrency control."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_workers)
        return self._semaphore

    async def encrypt_text_async(self, text: str) -> str:
        """
        Encrypt text asynchronously.

        Args:
            text: Plain text to encrypt

        Returns:
            Base64 encoded encrypted text

        Raises:
            CryptoTransformationError: If encryption fails
        """
        semaphore = self._get_semaphore()
        async with semaphore:
            # Run CPU-bound encryption in thread pool
            loop = asyncio.get_running_loop()
            try:
                encrypted = await loop.run_in_executor(
                    None, self.crypto_manager.encrypt_text, text
                )
                return cast(str, encrypted)
            except Exception as e:
                raise CryptoTransformationError(
                    f"Async encryption failed: {e}",
                    {"text_length": len(text), "error_type": type(e).__name__},
                ) from e

    async def decrypt_text_async(self, encrypted_text: str) -> str:
        """
        Decrypt text asynchronously.

        Args:
            encrypted_text: Base64 encoded encrypted text

        Returns:
            Decrypted plain text

        Raises:
            CryptoTransformationError: If decryption fails
        """
        semaphore = self._get_semaphore()
        async with semaphore:
            # Run CPU-bound decryption in thread pool
            loop = asyncio.get_running_loop()
            try:
                decrypted = await loop.run_in_executor(
                    None, self.crypto_manager.decrypt_text, encrypted_text
                )
                return cast(str, decrypted)
            except Exception as e:
                raise CryptoTransformationError(
                    f"Async decryption failed: {e}",
                    {
                        "encrypted_length": len(encrypted_text),
                        "error_type": type(e).__name__,
                    },
                ) from e

    async def encrypt_batch_async(self, texts: list[str]) -> list[str]:
        """
        Encrypt multiple texts in parallel.

        Args:
            texts: List of plain texts to encrypt

        Returns:
            List of Base64 encoded encrypted texts in same order

        Raises:
            CryptoTransformationError: If any encryption fails
        """
        if not texts:
            return []

        logger.info(
            "Starting batch encryption",
            count=len(texts),
            max_workers=self.max_workers,
        )

        try:
            # Create tasks for all encryptions
            tasks = [self.encrypt_text_async(text) for text in texts]

            # Execute all tasks concurrently
            encrypted_texts = await asyncio.gather(*tasks)

            logger.info("Batch encryption completed", count=len(encrypted_texts))
            return list(encrypted_texts)

        except Exception as e:
            raise CryptoTransformationError(
                f"Batch encryption failed: {e}",
                {"batch_size": len(texts), "error_type": type(e).__name__},
            ) from e

    async def decrypt_batch_async(self, encrypted_texts: list[str]) -> list[str]:
        """
        Decrypt multiple texts in parallel.

        Args:
            encrypted_texts: List of Base64 encoded encrypted texts

        Returns:
            List of decrypted plain texts in same order

        Raises:
            CryptoTransformationError: If any decryption fails
        """
        if not encrypted_texts:
            return []

        logger.info(
            "Starting batch decryption",
            count=len(encrypted_texts),
            max_workers=self.max_workers,
        )

        try:
            # Create tasks for all decryptions
            tasks = [self.decrypt_text_async(text) for text in encrypted_texts]

            # Execute all tasks concurrently
            decrypted_texts = await asyncio.gather(*tasks)

            logger.info("Batch decryption completed", count=len(decrypted_texts))
            return list(decrypted_texts)

        except Exception as e:
            raise CryptoTransformationError(
                f"Batch decryption failed: {e}",
                {
                    "batch_size": len(encrypted_texts),
                    "error_type": type(e).__name__,
                },
            ) from e

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on parallel crypto engine.

        Returns:
            Dictionary with health status and configuration
        """
        return {
            "status": "healthy",
            "max_workers": self.max_workers,
            "crypto_available": self.crypto_manager.is_available(),
            "key_info": self.crypto_manager.get_key_info(),
        }

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        self._semaphore = None
