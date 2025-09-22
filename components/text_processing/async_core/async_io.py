"""
Async I/O operations for text processing with enhanced performance.

This module provides asynchronous file I/O, clipboard monitoring,
and stdin/stdout handling optimized for high-throughput text processing.
"""

from __future__ import annotations

import asyncio
import aiofiles
import time
from typing import AsyncIterator, Optional, List, Dict, Any, Union, Callable
from pathlib import Path
from dataclasses import dataclass
import structlog

from ..config_manager.settings import ApplicationSettings, get_settings
from ..exceptions import FileOperationError, ClipboardError

# Initialize logger
logger = structlog.get_logger(__name__)


@dataclass
class FileOperationResult:
    """Result of an async file operation."""
    success: bool
    file_path: Path
    operation: str
    data_size: int = 0
    duration: float = 0.0
    error_message: Optional[str] = None


class AsyncIOManager:
    """High-performance async I/O manager for text processing."""

    def __init__(
        self,
        settings: Optional[ApplicationSettings] = None,
        buffer_size: int = 1024 * 64,  # 64KB buffer
        max_concurrent_ops: int = 10
    ) -> None:
        """Initialize async I/O manager.

        Args:
            settings: Application settings
            buffer_size: Buffer size for file operations
            max_concurrent_ops: Maximum concurrent I/O operations
        """
        self.settings = settings or get_settings()
        self.buffer_size = buffer_size
        self.max_concurrent_ops = max_concurrent_ops

        # Concurrency control
        self._io_semaphore = asyncio.Semaphore(max_concurrent_ops)
        self._active_operations: Dict[str, asyncio.Task] = {}

        # Performance tracking
        self._operation_stats = {
            'read_operations': 0,
            'write_operations': 0,
            'total_bytes_read': 0,
            'total_bytes_written': 0,
            'total_read_time': 0.0,
            'total_write_time': 0.0
        }

        logger.info(
            "async_io_manager_initialized",
            buffer_size=buffer_size,
            max_concurrent_ops=max_concurrent_ops
        )

    async def read_file_async(
        self,
        file_path: Union[str, Path],
        encoding: str = 'utf-8',
        chunk_size: Optional[int] = None
    ) -> str:
        """Read file asynchronously with optimized buffering.

        Args:
            file_path: Path to file to read
            encoding: Text encoding
            chunk_size: Custom chunk size for reading

        Returns:
            File content as string

        Raises:
            FileOperationError: If file operation fails
        """
        file_path = Path(file_path)
        chunk_size = chunk_size or self.buffer_size
        start_time = time.perf_counter()

        async with self._io_semaphore:
            try:
                async with aiofiles.open(file_path, mode='r', encoding=encoding) as file:
                    content = await file.read()

                # Update statistics
                duration = time.perf_counter() - start_time
                data_size = len(content.encode(encoding))

                self._operation_stats['read_operations'] += 1
                self._operation_stats['total_bytes_read'] += data_size
                self._operation_stats['total_read_time'] += duration

                logger.debug(
                    "file_read_completed",
                    file_path=str(file_path),
                    size_bytes=data_size,
                    duration_ms=duration * 1000
                )

                return content

            except Exception as e:
                error_msg = f"Failed to read file {file_path}: {e}"
                logger.error("file_read_failed", file_path=str(file_path), error=str(e))
                raise FileOperationError(error_msg, {"file_path": str(file_path)}) from e

    async def write_file_async(
        self,
        file_path: Union[str, Path],
        content: str,
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> FileOperationResult:
        """Write file asynchronously with directory creation.

        Args:
            file_path: Path to file to write
            content: Content to write
            encoding: Text encoding
            create_dirs: Create parent directories if they don't exist

        Returns:
            FileOperationResult with operation details

        Raises:
            FileOperationError: If file operation fails
        """
        file_path = Path(file_path)
        start_time = time.perf_counter()

        async with self._io_semaphore:
            try:
                # Create parent directories if needed
                if create_dirs and not file_path.parent.exists():
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(file_path, mode='w', encoding=encoding) as file:
                    await file.write(content)

                # Update statistics
                duration = time.perf_counter() - start_time
                data_size = len(content.encode(encoding))

                self._operation_stats['write_operations'] += 1
                self._operation_stats['total_bytes_written'] += data_size
                self._operation_stats['total_write_time'] += duration

                logger.debug(
                    "file_write_completed",
                    file_path=str(file_path),
                    size_bytes=data_size,
                    duration_ms=duration * 1000
                )

                return FileOperationResult(
                    success=True,
                    file_path=file_path,
                    operation="write",
                    data_size=data_size,
                    duration=duration
                )

            except Exception as e:
                error_msg = f"Failed to write file {file_path}: {e}"
                logger.error("file_write_failed", file_path=str(file_path), error=str(e))
                raise FileOperationError(error_msg, {"file_path": str(file_path)}) from e

    async def read_file_streaming(
        self,
        file_path: Union[str, Path],
        encoding: str = 'utf-8',
        chunk_size: Optional[int] = None
    ) -> AsyncIterator[str]:
        """Read file as async stream for memory-efficient processing.

        Args:
            file_path: Path to file to read
            encoding: Text encoding
            chunk_size: Size of chunks to read

        Yields:
            File content chunks
        """
        file_path = Path(file_path)
        chunk_size = chunk_size or self.buffer_size

        async with self._io_semaphore:
            try:
                async with aiofiles.open(file_path, mode='r', encoding=encoding) as file:
                    while True:
                        chunk = await file.read(chunk_size)
                        if not chunk:
                            break

                        yield chunk

                logger.debug(
                    "file_streaming_completed",
                    file_path=str(file_path),
                    chunk_size=chunk_size
                )

            except Exception as e:
                error_msg = f"Failed to stream file {file_path}: {e}"
                logger.error("file_streaming_failed", file_path=str(file_path), error=str(e))
                raise FileOperationError(error_msg, {"file_path": str(file_path)}) from e

    async def write_file_streaming(
        self,
        file_path: Union[str, Path],
        content_stream: AsyncIterator[str],
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> FileOperationResult:
        """Write file from async stream.

        Args:
            file_path: Path to file to write
            content_stream: Async iterator of content chunks
            encoding: Text encoding
            create_dirs: Create parent directories if they don't exist

        Returns:
            FileOperationResult with operation details
        """
        file_path = Path(file_path)
        start_time = time.perf_counter()
        total_size = 0

        async with self._io_semaphore:
            try:
                # Create parent directories if needed
                if create_dirs and not file_path.parent.exists():
                    file_path.parent.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(file_path, mode='w', encoding=encoding) as file:
                    async for chunk in content_stream:
                        await file.write(chunk)
                        total_size += len(chunk.encode(encoding))

                duration = time.perf_counter() - start_time

                # Update statistics
                self._operation_stats['write_operations'] += 1
                self._operation_stats['total_bytes_written'] += total_size
                self._operation_stats['total_write_time'] += duration

                logger.debug(
                    "file_streaming_write_completed",
                    file_path=str(file_path),
                    size_bytes=total_size,
                    duration_ms=duration * 1000
                )

                return FileOperationResult(
                    success=True,
                    file_path=file_path,
                    operation="stream_write",
                    data_size=total_size,
                    duration=duration
                )

            except Exception as e:
                error_msg = f"Failed to stream write file {file_path}: {e}"
                logger.error("file_streaming_write_failed", file_path=str(file_path), error=str(e))
                raise FileOperationError(error_msg, {"file_path": str(file_path)}) from e

    async def batch_read_files(
        self,
        file_paths: List[Union[str, Path]],
        encoding: str = 'utf-8'
    ) -> Dict[Path, Union[str, Exception]]:
        """Read multiple files concurrently.

        Args:
            file_paths: List of file paths to read
            encoding: Text encoding

        Returns:
            Dictionary mapping file paths to content or exceptions
        """
        logger.info("batch_read_starting", file_count=len(file_paths))

        async def read_single_file(path: Union[str, Path]) -> tuple[Path, Union[str, Exception]]:
            path = Path(path)
            try:
                content = await self.read_file_async(path, encoding)
                return path, content
            except Exception as e:
                return path, e

        # Execute all reads concurrently
        tasks = [read_single_file(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build result dictionary
        result_dict = {}
        for result in results:
            if isinstance(result, Exception):
                # This shouldn't happen with return_exceptions=True, but handle it
                logger.error("unexpected_batch_read_error", error=str(result))
                continue

            path, content_or_exception = result
            result_dict[path] = content_or_exception

        successful_reads = sum(1 for content in result_dict.values() if not isinstance(content, Exception))
        logger.info(
            "batch_read_completed",
            total_files=len(file_paths),
            successful_reads=successful_reads,
            failed_reads=len(file_paths) - successful_reads
        )

        return result_dict

    async def batch_write_files(
        self,
        file_data: Dict[Union[str, Path], str],
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> Dict[Path, FileOperationResult]:
        """Write multiple files concurrently.

        Args:
            file_data: Dictionary mapping file paths to content
            encoding: Text encoding
            create_dirs: Create parent directories if they don't exist

        Returns:
            Dictionary mapping file paths to operation results
        """
        logger.info("batch_write_starting", file_count=len(file_data))

        async def write_single_file(path: Union[str, Path], content: str) -> tuple[Path, FileOperationResult]:
            path = Path(path)
            try:
                result = await self.write_file_async(path, content, encoding, create_dirs)
                return path, result
            except Exception as e:
                return path, FileOperationResult(
                    success=False,
                    file_path=path,
                    operation="write",
                    error_message=str(e)
                )

        # Execute all writes concurrently
        tasks = [write_single_file(path, content) for path, content in file_data.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build result dictionary
        result_dict = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error("unexpected_batch_write_error", error=str(result))
                continue

            path, operation_result = result
            result_dict[path] = operation_result

        successful_writes = sum(1 for result in result_dict.values() if result.success)
        logger.info(
            "batch_write_completed",
            total_files=len(file_data),
            successful_writes=successful_writes,
            failed_writes=len(file_data) - successful_writes
        )

        return result_dict

    async def read_stdin_async(
        self,
        timeout: Optional[float] = None,
        chunk_size: Optional[int] = None
    ) -> str:
        """Read from stdin asynchronously with timeout.

        Args:
            timeout: Read timeout in seconds
            chunk_size: Buffer size for reading

        Returns:
            Content from stdin

        Raises:
            asyncio.TimeoutError: If timeout is exceeded
        """
        chunk_size = chunk_size or self.buffer_size

        try:
            # Read from stdin in a thread to avoid blocking
            loop = asyncio.get_event_loop()

            async def read_stdin():
                import sys
                return await loop.run_in_executor(None, sys.stdin.read)

            if timeout:
                content = await asyncio.wait_for(read_stdin(), timeout=timeout)
            else:
                content = await read_stdin()

            logger.debug("stdin_read_completed", size_bytes=len(content.encode()))
            return content

        except asyncio.TimeoutError:
            logger.warning("stdin_read_timeout", timeout=timeout)
            raise
        except Exception as e:
            logger.error("stdin_read_failed", error=str(e))
            raise FileOperationError(f"Failed to read from stdin: {e}") from e

    async def write_stdout_async(self, content: str) -> None:
        """Write to stdout asynchronously.

        Args:
            content: Content to write to stdout
        """
        try:
            loop = asyncio.get_event_loop()

            async def write_stdout():
                import sys
                sys.stdout.write(content)
                sys.stdout.flush()

            await loop.run_in_executor(None, write_stdout)

            logger.debug("stdout_write_completed", size_bytes=len(content.encode()))

        except Exception as e:
            logger.error("stdout_write_failed", error=str(e))
            raise FileOperationError(f"Failed to write to stdout: {e}") from e

    def get_io_statistics(self) -> Dict[str, Any]:
        """Get I/O operation statistics.

        Returns:
            Dictionary with I/O performance metrics
        """
        stats = self._operation_stats.copy()

        # Calculate derived metrics
        total_read_time = stats['total_read_time']
        total_write_time = stats['total_write_time']

        stats.update({
            'average_read_speed_bytes_per_sec': (
                stats['total_bytes_read'] / total_read_time
                if total_read_time > 0 else 0
            ),
            'average_write_speed_bytes_per_sec': (
                stats['total_bytes_written'] / total_write_time
                if total_write_time > 0 else 0
            ),
            'average_read_time_ms': (
                total_read_time / stats['read_operations'] * 1000
                if stats['read_operations'] > 0 else 0
            ),
            'average_write_time_ms': (
                total_write_time / stats['write_operations'] * 1000
                if stats['write_operations'] > 0 else 0
            ),
            'total_operations': stats['read_operations'] + stats['write_operations'],
            'active_operations': len(self._active_operations)
        })

        return stats

    async def cleanup(self) -> None:
        """Clean up async I/O manager resources."""
        # Cancel any active operations
        if self._active_operations:
            logger.info("cancelling_active_operations", count=len(self._active_operations))

            for operation_id, task in self._active_operations.items():
                task.cancel()

            # Wait for cancellation to complete
            await asyncio.gather(*self._active_operations.values(), return_exceptions=True)
            self._active_operations.clear()

        logger.info("async_io_manager_cleanup_completed")


# Convenience functions for backward compatibility
async def read_file_async(
    file_path: Union[str, Path],
    encoding: str = 'utf-8'
) -> str:
    """Convenience function for async file reading.

    Args:
        file_path: Path to file to read
        encoding: Text encoding

    Returns:
        File content
    """
    io_manager = AsyncIOManager()
    return await io_manager.read_file_async(file_path, encoding)


async def write_file_async(
    file_path: Union[str, Path],
    content: str,
    encoding: str = 'utf-8'
) -> FileOperationResult:
    """Convenience function for async file writing.

    Args:
        file_path: Path to file to write
        content: Content to write
        encoding: Text encoding

    Returns:
        FileOperationResult
    """
    io_manager = AsyncIOManager()
    return await io_manager.write_file_async(file_path, content, encoding)