"""
Async text processing core module.

This module provides asynchronous text processing capabilities
with streaming, chunked processing, performance optimization,
and memory-efficient I/O operations.
"""

from .async_engine import AsyncTextTransformationEngine, shutdown_async_engine
from .async_io import (
    AsyncIOManager,
    FileOperationResult,
    read_file_async,
    write_file_async,
)
from .performance import AsyncBenchmark, PerformanceMetric, PerformanceMonitor
from .streaming import AsyncTextStreamer, ChunkedProcessor, StreamingConfig

__all__ = [
    "AsyncBenchmark",
    # Async I/O
    "AsyncIOManager",
    # Streaming and processing
    "AsyncTextStreamer",
    # Core async engine
    "AsyncTextTransformationEngine",
    "ChunkedProcessor",
    "FileOperationResult",
    "PerformanceMetric",
    # Performance monitoring
    "PerformanceMonitor",
    "StreamingConfig",
    "read_file_async",
    "shutdown_async_engine",
    "write_file_async",
]
