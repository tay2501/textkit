"""
Advanced streaming text processing with async support.

This module provides high-performance streaming capabilities for large text
processing operations with memory optimization and backpressure handling.
"""

from __future__ import annotations

import asyncio
import time
from typing import AsyncIterator, Optional, Union, Dict, Any, List
from dataclasses import dataclass
import structlog

from ..text_core.core import TextTransformationEngine
from ..config_manager.settings import ApplicationSettings, get_settings

# Initialize logger
logger = structlog.get_logger(__name__)


@dataclass
class StreamingConfig:
    """Configuration for streaming operations."""
    chunk_size: int = 1024 * 64  # 64KB chunks
    max_buffer_size: int = 1024 * 1024 * 10  # 10MB buffer limit
    enable_backpressure: bool = True
    max_concurrent_streams: int = 5
    timeout_seconds: float = 30.0


class AsyncTextStreamer:
    """High-performance async text streamer with backpressure handling."""

    def __init__(
        self,
        sync_engine: Optional[TextTransformationEngine] = None,
        config: Optional[StreamingConfig] = None,
        settings: Optional[ApplicationSettings] = None
    ) -> None:
        """Initialize async text streamer.

        Args:
            sync_engine: Underlying synchronous transformation engine
            config: Streaming configuration
            settings: Application settings
        """
        self.sync_engine = sync_engine or TextTransformationEngine()
        self.config = config or StreamingConfig()
        self.settings = settings or get_settings()

        # Streaming state
        self._active_streams: Dict[str, asyncio.Task] = {}
        self._stream_semaphore = asyncio.Semaphore(self.config.max_concurrent_streams)
        self._buffer_size = 0

        logger.info(
            "async_streamer_initialized",
            chunk_size=self.config.chunk_size,
            max_concurrent_streams=self.config.max_concurrent_streams
        )

    async def stream_transform(
        self,
        text_source: Union[str, AsyncIterator[str]],
        rule_string: str,
        stream_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Stream text transformation with backpressure handling.

        Args:
            text_source: Text string or async iterator of text chunks
            rule_string: Transformation rules to apply
            stream_id: Optional stream identifier for tracking

        Yields:
            Transformed text chunks
        """
        async with self._stream_semaphore:
            stream_id = stream_id or f"stream_{id(text_source)}"

            try:
                # Register active stream
                current_task = asyncio.current_task()
                if current_task:
                    self._active_streams[stream_id] = current_task

                # Handle different input types
                if isinstance(text_source, str):
                    async for chunk in self._stream_from_string(text_source, rule_string):
                        yield chunk
                else:
                    async for chunk in self._stream_from_iterator(text_source, rule_string):
                        yield chunk

            except asyncio.CancelledError:
                logger.warning("stream_cancelled", stream_id=stream_id)
                raise
            except Exception as e:
                logger.error("stream_error", stream_id=stream_id, error=str(e))
                raise
            finally:
                # Clean up
                self._active_streams.pop(stream_id, None)

    async def _stream_from_string(
        self,
        text: str,
        rule_string: str
    ) -> AsyncIterator[str]:
        """Stream transformation from a string input.

        Args:
            text: Input text to transform
            rule_string: Transformation rules

        Yields:
            Transformed text chunks
        """
        # Split into chunks for streaming
        for i in range(0, len(text), self.config.chunk_size):
            chunk = text[i:i + self.config.chunk_size]

            # Apply backpressure if needed
            if self.config.enable_backpressure:
                await self._check_backpressure()

            # Transform chunk
            try:
                transformed_chunk = await asyncio.to_thread(
                    self.sync_engine.apply_transformations,
                    chunk,
                    rule_string
                )

                # Update buffer tracking
                self._buffer_size += len(transformed_chunk)

                yield transformed_chunk

                # Reduce buffer size after yielding
                self._buffer_size -= len(transformed_chunk)

            except Exception as e:
                logger.error("chunk_transformation_failed", error=str(e))
                yield chunk  # Return original chunk on error

    async def _stream_from_iterator(
        self,
        text_iterator: AsyncIterator[str],
        rule_string: str
    ) -> AsyncIterator[str]:
        """Stream transformation from an async iterator.

        Args:
            text_iterator: Async iterator of text chunks
            rule_string: Transformation rules

        Yields:
            Transformed text chunks
        """
        async for chunk in text_iterator:
            if self.config.enable_backpressure:
                await self._check_backpressure()

            try:
                transformed_chunk = await asyncio.to_thread(
                    self.sync_engine.apply_transformations,
                    chunk,
                    rule_string
                )

                self._buffer_size += len(transformed_chunk)
                yield transformed_chunk
                self._buffer_size -= len(transformed_chunk)

            except Exception as e:
                logger.error("iterator_chunk_transformation_failed", error=str(e))
                yield chunk

    async def _check_backpressure(self) -> None:
        """Check and handle backpressure conditions."""
        if self._buffer_size > self.config.max_buffer_size:
            logger.warning(
                "backpressure_triggered",
                buffer_size=self._buffer_size,
                max_buffer_size=self.config.max_buffer_size
            )

            # Wait until buffer reduces
            while self._buffer_size > self.config.max_buffer_size * 0.8:
                await asyncio.sleep(0.01)  # Small delay to allow buffer to drain

    async def cancel_stream(self, stream_id: str) -> bool:
        """Cancel an active stream.

        Args:
            stream_id: ID of stream to cancel

        Returns:
            True if stream was cancelled successfully
        """
        if stream_id in self._active_streams:
            task = self._active_streams[stream_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            return True
        return False

    def get_active_streams(self) -> List[str]:
        """Get list of active stream IDs.

        Returns:
            List of active stream identifiers
        """
        return list(self._active_streams.keys())

    def get_buffer_info(self) -> Dict[str, Any]:
        """Get current buffer information.

        Returns:
            Dictionary with buffer metrics
        """
        return {
            "current_buffer_size": self._buffer_size,
            "max_buffer_size": self.config.max_buffer_size,
            "buffer_utilization": self._buffer_size / self.config.max_buffer_size,
            "active_streams": len(self._active_streams)
        }


class ChunkedProcessor:
    """Optimized chunked text processor with intelligent chunk sizing."""

    def __init__(
        self,
        sync_engine: Optional[TextTransformationEngine] = None,
        settings: Optional[ApplicationSettings] = None
    ) -> None:
        """Initialize chunked processor.

        Args:
            sync_engine: Underlying synchronous transformation engine
            settings: Application settings
        """
        self.sync_engine = sync_engine or TextTransformationEngine()
        self.settings = settings or get_settings()

        # Adaptive chunk sizing
        self._optimal_chunk_size = 1024 * 64  # Start with 64KB
        self._chunk_performance_history: List[tuple[int, float]] = []
        self._max_history = 10

    async def process_chunks(
        self,
        text: str,
        rule_string: str,
        max_concurrent: int = 4
    ) -> str:
        """Process text using optimized chunking strategy.

        Args:
            text: Input text to process
            rule_string: Transformation rules
            max_concurrent: Maximum concurrent chunk processors

        Returns:
            Processed text result
        """
        if len(text) <= self._optimal_chunk_size:
            # Small text - process directly
            return await asyncio.to_thread(
                self.sync_engine.apply_transformations,
                text,
                rule_string
            )

        # Create optimized chunks
        chunks = self._create_optimized_chunks(text)

        # Process chunks concurrently
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_single_chunk(chunk: str, index: int) -> tuple[int, str]:
            async with semaphore:
                start_time = time.perf_counter()

                result = await asyncio.to_thread(
                    self.sync_engine.apply_transformations,
                    chunk,
                    rule_string
                )

                processing_time = time.perf_counter() - start_time

                # Track performance for adaptive sizing
                self._update_chunk_performance(len(chunk), processing_time)

                return index, result

        # Create and execute tasks
        tasks = [
            process_single_chunk(chunk, i)
            for i, chunk in enumerate(chunks)
        ]

        # Gather results in order
        results = await asyncio.gather(*tasks)
        results.sort(key=lambda x: x[0])  # Sort by index

        # Combine results
        return ''.join(result[1] for result in results)

    def _create_optimized_chunks(self, text: str) -> List[str]:
        """Create optimized text chunks with word boundary awareness.

        Args:
            text: Text to chunk

        Returns:
            List of optimized text chunks
        """
        if len(text) <= self._optimal_chunk_size:
            return [text]

        chunks = []
        position = 0

        while position < len(text):
            # Calculate chunk end position
            chunk_end = min(position + self._optimal_chunk_size, len(text))

            # Try to break on word boundaries
            if chunk_end < len(text):
                # Look for good break points
                for break_char in ['\n\n', '\n', '. ', '? ', '! ', ' ']:
                    break_pos = text.rfind(break_char, position, chunk_end)
                    if break_pos > position + self._optimal_chunk_size * 0.7:
                        chunk_end = break_pos + len(break_char)
                        break

            chunk = text[position:chunk_end]
            chunks.append(chunk)
            position = chunk_end

        logger.debug(
            "text_chunked",
            total_length=len(text),
            num_chunks=len(chunks),
            optimal_chunk_size=self._optimal_chunk_size
        )

        return chunks

    def _update_chunk_performance(self, chunk_size: int, processing_time: float) -> None:
        """Update chunk performance history for adaptive sizing.

        Args:
            chunk_size: Size of processed chunk
            processing_time: Time taken to process chunk
        """
        self._chunk_performance_history.append((chunk_size, processing_time))

        # Keep only recent history
        if len(self._chunk_performance_history) > self._max_history:
            self._chunk_performance_history.pop(0)

        # Adjust optimal chunk size based on performance
        if len(self._chunk_performance_history) >= 5:
            self._adjust_optimal_chunk_size()

    def _adjust_optimal_chunk_size(self) -> None:
        """Adjust optimal chunk size based on performance history."""
        if len(self._chunk_performance_history) < 3:
            return

        # Calculate throughput (chars per second) for recent chunks
        throughputs = []
        for chunk_size, processing_time in self._chunk_performance_history[-5:]:
            if processing_time > 0:
                throughput = chunk_size / processing_time
                throughputs.append(throughput)

        if not throughputs:
            return

        # Find the chunk size with best throughput
        best_throughput = max(throughputs)
        best_index = throughputs.index(best_throughput)
        best_chunk_size = self._chunk_performance_history[-(len(throughputs) - best_index)][0]

        # Gradually adjust toward optimal size
        adjustment_factor = 0.1
        size_diff = best_chunk_size - self._optimal_chunk_size
        self._optimal_chunk_size += int(size_diff * adjustment_factor)

        # Keep within reasonable bounds
        self._optimal_chunk_size = max(1024 * 16, min(1024 * 512, self._optimal_chunk_size))

        logger.debug(
            "chunk_size_adjusted",
            old_size=self._optimal_chunk_size - int(size_diff * adjustment_factor),
            new_size=self._optimal_chunk_size,
            best_throughput=best_throughput
        )

    def get_performance_info(self) -> Dict[str, Any]:
        """Get chunked processor performance information.

        Returns:
            Dictionary with performance metrics
        """
        if not self._chunk_performance_history:
            return {
                "optimal_chunk_size": self._optimal_chunk_size,
                "performance_samples": 0
            }

        # Calculate average throughput
        total_throughput = 0
        sample_count = 0

        for chunk_size, processing_time in self._chunk_performance_history:
            if processing_time > 0:
                total_throughput += chunk_size / processing_time
                sample_count += 1

        avg_throughput = total_throughput / sample_count if sample_count > 0 else 0

        return {
            "optimal_chunk_size": self._optimal_chunk_size,
            "performance_samples": len(self._chunk_performance_history),
            "average_throughput_chars_per_sec": avg_throughput,
            "recent_chunk_sizes": [cs for cs, _ in self._chunk_performance_history[-3:]],
            "recent_processing_times": [pt for _, pt in self._chunk_performance_history[-3:]]
        }