"""Tests for parallel crypto engine."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from textkit.config_manager import ConfigurationManager
from textkit.crypto_engine import (
    CRYPTOGRAPHY_AVAILABLE,
    CryptographyManager,
    ParallelCryptoEngine,
)
from textkit.exceptions import CryptoTransformationError


@pytest.mark.skipif(
    not CRYPTOGRAPHY_AVAILABLE,
    reason="cryptography library not available",
)
class TestParallelCryptoEngine:
    """Test suite for ParallelCryptoEngine."""

    @pytest.fixture
    def config_dir(self, tmp_path):
        """Create temporary config directory."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        return config_dir

    @pytest.fixture
    def crypto_manager(self, config_dir):
        """Create CryptographyManager instance."""
        config = ConfigurationManager(config_dir)
        manager = CryptographyManager(config)
        manager.ensure_key_pair()
        return manager

    @pytest.fixture
    def parallel_engine(self, crypto_manager):
        """Create ParallelCryptoEngine instance."""
        return ParallelCryptoEngine(crypto_manager, max_workers=4)

    @pytest.mark.asyncio
    async def test_initialization(self, parallel_engine):
        """Test parallel engine initialization."""
        assert parallel_engine.max_workers == 4
        assert parallel_engine.crypto_manager is not None

    @pytest.mark.asyncio
    async def test_encrypt_text_async(self, parallel_engine):
        """Test async text encryption."""
        text = "Hello, Parallel World!"
        encrypted = await parallel_engine.encrypt_text_async(text)

        assert encrypted
        assert isinstance(encrypted, str)
        assert encrypted != text

    @pytest.mark.asyncio
    async def test_decrypt_text_async(self, parallel_engine):
        """Test async text decryption."""
        text = "Hello, Parallel World!"
        encrypted = await parallel_engine.encrypt_text_async(text)
        decrypted = await parallel_engine.decrypt_text_async(encrypted)

        assert decrypted == text

    @pytest.mark.asyncio
    async def test_encrypt_decrypt_roundtrip_async(self, parallel_engine):
        """Test async encryption/decryption round trip."""
        test_cases = [
            "Simple text",
            "Text with special chars: !@#$%^&*()",
            "日本語テキスト",
            "Multi\nline\ntext",
            "",  # Empty string
            "A" * 1000,  # Long text
        ]

        for text in test_cases:
            encrypted = await parallel_engine.encrypt_text_async(text)
            decrypted = await parallel_engine.decrypt_text_async(encrypted)
            assert decrypted == text, f"Failed for: {text[:50]}"

    @pytest.mark.asyncio
    async def test_encrypt_batch_async_empty(self, parallel_engine):
        """Test batch encryption with empty list."""
        encrypted = await parallel_engine.encrypt_batch_async([])
        assert encrypted == []

    @pytest.mark.asyncio
    async def test_encrypt_batch_async_single(self, parallel_engine):
        """Test batch encryption with single text."""
        texts = ["Hello World"]
        encrypted = await parallel_engine.encrypt_batch_async(texts)

        assert len(encrypted) == 1
        assert encrypted[0] != texts[0]

    @pytest.mark.asyncio
    async def test_encrypt_batch_async_multiple(self, parallel_engine):
        """Test batch encryption with multiple texts."""
        texts = [
            "First text",
            "Second text",
            "Third text",
            "Fourth text",
            "Fifth text",
        ]
        encrypted = await parallel_engine.encrypt_batch_async(texts)

        assert len(encrypted) == len(texts)
        # All encrypted texts should be different
        assert len(set(encrypted)) == len(encrypted)
        # None should match original
        for enc, orig in zip(encrypted, texts):
            assert enc != orig

    @pytest.mark.asyncio
    async def test_decrypt_batch_async_empty(self, parallel_engine):
        """Test batch decryption with empty list."""
        decrypted = await parallel_engine.decrypt_batch_async([])
        assert decrypted == []

    @pytest.mark.asyncio
    async def test_encrypt_decrypt_batch_roundtrip(self, parallel_engine):
        """Test batch encryption/decryption round trip."""
        texts = [
            "Text 1",
            "Text 2",
            "Text 3",
            "日本語1",
            "日本語2",
            "",
            "A" * 100,
        ]

        encrypted = await parallel_engine.encrypt_batch_async(texts)
        decrypted = await parallel_engine.decrypt_batch_async(encrypted)

        assert decrypted == texts

    @pytest.mark.asyncio
    async def test_large_batch_encryption(self, parallel_engine):
        """Test encryption of large batch."""
        texts = [f"Text number {i}" for i in range(100)]
        encrypted = await parallel_engine.encrypt_batch_async(texts)
        decrypted = await parallel_engine.decrypt_batch_async(encrypted)

        assert decrypted == texts

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, parallel_engine):
        """Test concurrent encrypt and decrypt operations."""
        texts1 = ["Batch 1 - Text 1", "Batch 1 - Text 2"]
        texts2 = ["Batch 2 - Text 1", "Batch 2 - Text 2"]

        # Run two batch operations concurrently
        task1 = parallel_engine.encrypt_batch_async(texts1)
        task2 = parallel_engine.encrypt_batch_async(texts2)

        encrypted1, encrypted2 = await asyncio.gather(task1, task2)

        assert len(encrypted1) == len(texts1)
        assert len(encrypted2) == len(texts2)

        # Decrypt concurrently
        task1 = parallel_engine.decrypt_batch_async(encrypted1)
        task2 = parallel_engine.decrypt_batch_async(encrypted2)

        decrypted1, decrypted2 = await asyncio.gather(task1, task2)

        assert decrypted1 == texts1
        assert decrypted2 == texts2

    @pytest.mark.asyncio
    async def test_health_check(self, parallel_engine):
        """Test health check."""
        health = await parallel_engine.health_check()

        assert health["status"] == "healthy"
        assert health["max_workers"] == 4
        assert health["crypto_available"] is True
        assert "key_info" in health

    @pytest.mark.asyncio
    async def test_context_manager(self, parallel_engine):
        """Test async context manager."""
        async with parallel_engine as engine:
            text = "Context manager test"
            encrypted = await engine.encrypt_text_async(text)
            decrypted = await engine.decrypt_text_async(encrypted)
            assert decrypted == text

    @pytest.mark.asyncio
    async def test_semaphore_control(self, crypto_manager):
        """Test semaphore limits concurrency."""
        engine = ParallelCryptoEngine(crypto_manager, max_workers=2)

        # Create more tasks than workers
        texts = [f"Text {i}" for i in range(10)]
        encrypted = await engine.encrypt_batch_async(texts)

        # All should complete successfully despite worker limit
        assert len(encrypted) == 10

    @pytest.mark.asyncio
    async def test_error_handling_invalid_encrypted(self, parallel_engine):
        """Test error handling with invalid encrypted data."""
        with pytest.raises(CryptoTransformationError):
            await parallel_engine.decrypt_text_async("invalid_base64")

    @pytest.mark.asyncio
    async def test_batch_preserves_order(self, parallel_engine):
        """Test that batch operations preserve order."""
        texts = [f"Text {i:03d}" for i in range(50)]
        encrypted = await parallel_engine.encrypt_batch_async(texts)
        decrypted = await parallel_engine.decrypt_batch_async(encrypted)

        # Order should be preserved
        assert decrypted == texts
        for i, text in enumerate(decrypted):
            assert text == f"Text {i:03d}"
