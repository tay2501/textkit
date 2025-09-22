"""
Asynchronous text transformation engine.

This module provides high-performance async text processing with
streaming support, memory optimization, and concurrent execution.
"""

from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator, Optional, List, Tuple, Dict, Any, Union
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import structlog

from ..text_core.models import TextTransformationRequest, TextTransformationResponse
from ..text_core.core import TextTransformationEngine
from ..config_manager.settings import ApplicationSettings, get_settings
from ..exceptions import ValidationError, TransformationError

# Initialize logger
logger = structlog.get_logger(__name__)

# Global thread pool for CPU-bound operations
_cpu_executor: Optional[ThreadPoolExecutor] = None


def get_cpu_executor() -> ThreadPoolExecutor:
    """Get or create the global CPU executor."""
    global _cpu_executor
    if _cpu_executor is None:
        settings = get_settings()
        max_workers = min(4, (asyncio.get_event_loop().get_debug() and 2) or 4)
        _cpu_executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="textkit-cpu"
        )
        logger.info("cpu_executor_created", max_workers=max_workers)
    return _cpu_executor


class AsyncTextTransformationEngine:
    """Asynchronous text transformation engine.

    Provides high-performance async text processing with:
    - Concurrent rule execution
    - Streaming text processing
    - Memory-efficient chunked processing
    - Performance monitoring
    """

    def __init__(
        self,
        sync_engine: Optional[TextTransformationEngine] = None,
        settings: Optional[ApplicationSettings] = None,
        chunk_size: int = 1024 * 1024,  # 1MB chunks
        max_concurrent_chunks: int = 4
    ) -> None:
        """Initialize async transformation engine.

        Args:
            sync_engine: Underlying synchronous engine
            settings: Application settings
            chunk_size: Size of text chunks for processing
            max_concurrent_chunks: Maximum concurrent chunk processing
        """
        self.sync_engine = sync_engine or TextTransformationEngine()
        self.settings = settings or get_settings()
        self.chunk_size = chunk_size
        self.max_concurrent_chunks = max_concurrent_chunks

        # Performance tracking
        self._stats = {
            'total_requests': 0,
            'total_characters': 0,
            'total_time': 0.0,
            'average_throughput': 0.0
        }

        logger.info(
            "async_engine_initialized",
            chunk_size=chunk_size,
            max_concurrent_chunks=max_concurrent_chunks
        )

    async def transform_async(
        self,
        text: str,
        rule_string: str,
        enable_streaming: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """Transform text asynchronously.

        Args:
            text: Input text to transform
            rule_string: Transformation rules
            enable_streaming: Enable streaming response

        Returns:
            Transformed text or async iterator for streaming
        """
        start_time = time.perf_counter()

        try:
            # Validate input using Pydantic
            request = TextTransformationRequest(
                text=text,
                rule_string=rule_string
            )

            # Update stats
            self._stats['total_requests'] += 1
            self._stats['total_characters'] += len(text)

            # Choose processing strategy based on text size
            if len(text) <= self.chunk_size or not enable_streaming:
                # Small text: process directly
                result = await self._transform_direct(request)

                # Update performance stats
                processing_time = time.perf_counter() - start_time
                self._update_stats(processing_time, len(text))

                return result
            else:
                # Large text: use streaming/chunked processing
                return self._transform_streaming(request)

        except Exception as e:
            logger.error(
                "async_transformation_failed",
                error=str(e),
                text_length=len(text),
                rule_string=rule_string
            )
            raise

    async def _transform_direct(self, request: TextTransformationRequest) -> str:
        """Transform text directly (non-streaming).

        Args:
            request: Validated transformation request

        Returns:
            Transformed text
        """
        loop = asyncio.get_event_loop()

        # Run synchronous transformation in thread pool
        result = await loop.run_in_executor(
            get_cpu_executor(),
            self.sync_engine.apply_transformations,
            request.text,
            request.rule_string
        )

        logger.debug(
            "direct_transformation_completed",
            text_length=len(request.text),
            result_length=len(result)
        )

        return result

    async def _transform_streaming(
        self,
        request: TextTransformationRequest
    ) -> AsyncIterator[str]:
        """Transform text using streaming/chunked processing.

        Args:
            request: Validated transformation request

        Yields:
            Transformed text chunks
        """
        try:
            # Split text into chunks
            chunks = self._create_chunks(request.text)

            # Process chunks concurrently with semaphore
            semaphore = asyncio.Semaphore(self.max_concurrent_chunks)

            async def process_chunk(chunk: str, chunk_id: int) -> Tuple[int, str]:
                async with semaphore:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        get_cpu_executor(),
                        self.sync_engine.apply_transformations,
                        chunk,
                        request.rule_string
                    )
                    return chunk_id, result

            # Create tasks for all chunks
            tasks = [
                process_chunk(chunk, i)
                for i, chunk in enumerate(chunks)
            ]

            # Process chunks and yield results in order
            results = {}
            next_chunk_id = 0

            for completed_task in asyncio.as_completed(tasks):
                chunk_id, result = await completed_task
                results[chunk_id] = result

                # Yield results in order
                while next_chunk_id in results:
                    yield results.pop(next_chunk_id)
                    next_chunk_id += 1

        except Exception as e:
            logger.error(
                "streaming_transformation_failed",
                error=str(e),
                text_length=len(request.text)
            )
            raise TransformationError(f"Streaming transformation failed: {e}") from e

    def _create_chunks(self, text: str) -> List[str]:
        """Create text chunks for processing.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i:i + self.chunk_size]

            # Try to break on word boundaries
            if i + self.chunk_size < len(text) and not chunk.endswith(' '):
                last_space = chunk.rfind(' ')
                if last_space > self.chunk_size * 0.8:  # Don't break too early
                    chunk = chunk[:last_space]

            chunks.append(chunk)

        logger.debug(
            "text_chunked",
            total_length=len(text),
            num_chunks=len(chunks),
            chunk_size=self.chunk_size
        )

        return chunks

    async def transform_batch_async(
        self,
        requests: List[Tuple[str, str]]
    ) -> List[str]:
        """Transform multiple texts concurrently.

        Args:
            requests: List of (text, rule_string) tuples

        Returns:
            List of transformed texts
        """
        start_time = time.perf_counter()

        try:
            # Create concurrent tasks
            tasks = [
                self.transform_async(text, rules)
                for text, rules in requests
            ]

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        "batch_item_failed",
                        item_index=i,
                        error=str(result)
                    )
                    final_results.append("")  # Return empty string for failed items
                else:
                    final_results.append(result)

            processing_time = time.perf_counter() - start_time
            logger.info(
                "batch_transformation_completed",
                batch_size=len(requests),
                processing_time=processing_time,
                throughput=len(requests) / processing_time
            )

            return final_results

        except Exception as e:
            logger.error(
                "batch_transformation_failed",
                error=str(e),
                batch_size=len(requests)
            )
            raise

    def _update_stats(self, processing_time: float, character_count: int) -> None:
        """Update performance statistics.

        Args:
            processing_time: Time taken for processing
            character_count: Number of characters processed
        """
        self._stats['total_time'] += processing_time
        if self._stats['total_time'] > 0:
            self._stats['average_throughput'] = (
                self._stats['total_characters'] / self._stats['total_time']
            )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        return {
            **self._stats,
            'characters_per_second': self._stats['average_throughput'],
            'requests_per_second': (
                self._stats['total_requests'] / self._stats['total_time']
                if self._stats['total_time'] > 0 else 0
            )
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform async health check.

        Returns:
            Health status information
        """
        try:
            # Test basic transformation
            test_start = time.perf_counter()
            test_result = await self.transform_async("test", "/u")
            test_time = time.perf_counter() - test_start

            return {
                "status": "healthy",
                "test_transformation": test_result == "TEST",
                "test_time_ms": test_time * 1000,
                "cpu_executor_active": _cpu_executor is not None,
                "performance_stats": self.get_performance_stats()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "performance_stats": self.get_performance_stats()
            }

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        pass


# Decorator for async timing
def async_timed(func):
    """Decorator to time async functions."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            logger.debug(
                "async_function_timed",
                function=func.__name__,
                duration_ms=(end_time - start_time) * 1000
            )
    return wrapper


# Utility function for graceful shutdown
async def shutdown_async_engine():
    """Gracefully shutdown async engine resources."""
    global _cpu_executor
    if _cpu_executor:
        _cpu_executor.shutdown(wait=True)
        _cpu_executor = None
        logger.info("async_engine_shutdown_completed")