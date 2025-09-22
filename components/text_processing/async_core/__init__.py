"""
Async text processing core module.

This module provides asynchronous text processing capabilities
with streaming, chunked processing, performance optimization,
and memory-efficient I/O operations.
"""

from .async_engine import AsyncTextTransformationEngine, shutdown_async_engine
from .streaming import AsyncTextStreamer, ChunkedProcessor, StreamingConfig
from .performance import PerformanceMonitor, AsyncBenchmark, PerformanceMetric
from .async_io import AsyncIOManager, FileOperationResult, read_file_async, write_file_async

__all__ = [
    # Core async engine
    'AsyncTextTransformationEngine',
    'shutdown_async_engine',

    # Streaming and processing
    'AsyncTextStreamer',
    'ChunkedProcessor',
    'StreamingConfig',

    # Performance monitoring
    'PerformanceMonitor',
    'AsyncBenchmark',
    'PerformanceMetric',

    # Async I/O
    'AsyncIOManager',
    'FileOperationResult',
    'read_file_async',
    'write_file_async'
]