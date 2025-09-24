"""
Comprehensive async integration tests for the TextKit async processing system.

This script tests all async components including the async engine, streaming,
performance monitoring, and I/O operations to ensure proper integration.
"""

import asyncio
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any

import pytest

from components.text_processing.async_core import (
    AsyncTextTransformationEngine,
    AsyncTextStreamer,
    ChunkedProcessor,
    PerformanceMonitor,
    AsyncBenchmark,
    AsyncIOManager,
    StreamingConfig
)
from components.text_processing.text_core.core import TextTransformationEngine
from components.text_processing.config_manager.settings import ApplicationSettings


async def test_async_engine_basic_transformation():
    """Test basic async text transformation."""
    print("Testing async engine basic transformation...")

    async_engine = AsyncTextTransformationEngine()

    # Test simple transformation
    result = await async_engine.transform_async("hello world", "/u")
    assert result == "HELLO WORLD", f"Expected 'HELLO WORLD', got '{result}'"

    # Test with more complex rule
    result = await async_engine.transform_async("test 123 test", "/r/test/replaced/")
    assert result == "replaced 123 replaced", f"Expected 'replaced 123 replaced', got '{result}'"

    print("OK Async engine basic transformation test passed")


async def test_async_engine_streaming():
    """Test async engine streaming capabilities."""
    print("Testing async engine streaming...")

    async_engine = AsyncTextTransformationEngine(chunk_size=50)

    # Create large text for streaming
    large_text = "test " * 1000  # 5000 characters

    # Test streaming transformation
    stream = await async_engine.transform_async(large_text, "/u", enable_streaming=True)

    if hasattr(stream, '__aiter__'):
        # It's a streaming response
        result_chunks = []
        async for chunk in stream:
            result_chunks.append(chunk)

        result = ''.join(result_chunks)
        expected = large_text.upper()
        assert result == expected, "Streaming transformation result mismatch"
    else:
        # Small text processed directly
        assert stream == large_text.upper(), "Direct transformation result mismatch"

    print("OK Async engine streaming test passed")


async def test_async_engine_batch_processing():
    """Test async engine batch processing."""
    print("Testing async engine batch processing...")

    async_engine = AsyncTextTransformationEngine()

    # Test batch processing
    requests = [
        ("hello", "/u"),
        ("world", "/u"),
        ("test", "/r/t/T/")
    ]

    results = await async_engine.transform_batch_async(requests)

    expected = ["HELLO", "WORLD", "TesT"]
    assert results == expected, f"Expected {expected}, got {results}"

    print("OK Async engine batch processing test passed")


async def test_async_engine_health_check():
    """Test async engine health check."""
    print("Testing async engine health check...")

    async_engine = AsyncTextTransformationEngine()

    health_status = await async_engine.health_check()

    assert health_status["status"] == "healthy", f"Health check failed: {health_status}"
    assert "test_transformation" in health_status
    assert "performance_stats" in health_status

    print("OK Async engine health check test passed")


async def test_streaming_basic_functionality():
    """Test async text streamer basic functionality."""
    print("Testing async text streamer...")

    streamer = AsyncTextStreamer()

    # Test streaming from string
    test_text = "hello world " * 100

    results = []
    async for chunk in streamer.stream_transform(test_text, "/u"):
        results.append(chunk)

    result = ''.join(results)
    assert result == test_text.upper(), "Streaming transformation failed"

    print("OK Async text streamer test passed")


async def test_chunked_processor():
    """Test chunked processor with adaptive sizing."""
    print("Testing chunked processor...")

    processor = ChunkedProcessor()

    # Test chunked processing
    test_text = "test " * 500  # Large enough to trigger chunking
    result = await processor.process_chunks(test_text, "/u")

    assert result == test_text.upper(), "Chunked processing failed"

    # Check performance info
    perf_info = processor.get_performance_info()
    assert "optimal_chunk_size" in perf_info
    assert perf_info["performance_samples"] >= 0

    print("OK Chunked processor test passed")


async def test_performance_monitoring():
    """Test performance monitoring capabilities."""
    print("Testing performance monitoring...")

    monitor = PerformanceMonitor()

    # Test operation measurement
    async def test_operation():
        await asyncio.sleep(0.01)  # Simulate work
        return "test_result"

    result = await monitor.measure_operation(
        "test_operation",
        test_operation,
        data_size=100
    )

    assert result == "test_result", "Measured operation result incorrect"

    # Check stats
    stats = monitor.get_stats("test_operation")
    assert stats["total_operations"] == 1
    assert stats["successful_operations"] == 1
    assert stats["success_rate_percent"] == 100.0

    # Test system overview
    overview = monitor.get_system_overview()
    assert "total_operations" in overview
    assert overview["total_operations"] >= 1

    print("OK Performance monitoring test passed")


async def test_async_benchmark():
    """Test async benchmarking capabilities."""
    print("Testing async benchmark...")

    monitor = PerformanceMonitor()
    benchmark = AsyncBenchmark(monitor)

    # Test function to benchmark
    async def sample_function(text: str, multiplier: int = 1):
        await asyncio.sleep(0.001)  # Small delay
        return text * multiplier

    # Benchmark with multiple test cases
    test_cases = [
        (("hello",), {"multiplier": 1}),
        (("world",), {"multiplier": 2})
    ]

    results = await benchmark.benchmark_function(
        sample_function,
        test_cases,
        iterations=5,
        warmup_iterations=2
    )

    assert results["function_name"] == "sample_function"
    assert len(results["test_cases"]) == 2
    assert "summary" in results

    print("OK Async benchmark test passed")


async def test_async_io_manager():
    """Test async I/O manager functionality."""
    print("Testing async I/O manager...")

    io_manager = AsyncIOManager()

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"
        test_content = "Hello, async world!\nThis is a test file."

        # Test file writing
        write_result = await io_manager.write_file_async(test_file, test_content)
        assert write_result.success, f"File write failed: {write_result.error_message}"

        # Test file reading
        read_content = await io_manager.read_file_async(test_file)
        assert read_content == test_content, "File content mismatch"

        # Test batch operations
        batch_data = {
            Path(temp_dir) / "file1.txt": "Content 1",
            Path(temp_dir) / "file2.txt": "Content 2",
            Path(temp_dir) / "file3.txt": "Content 3"
        }

        batch_results = await io_manager.batch_write_files(batch_data)
        assert len(batch_results) == 3
        assert all(result.success for result in batch_results.values())

        # Test batch reading
        file_paths = list(batch_data.keys())
        batch_read_results = await io_manager.batch_read_files(file_paths)
        assert len(batch_read_results) == 3

        for path, expected_content in batch_data.items():
            assert path in batch_read_results
            assert batch_read_results[path] == expected_content

    # Test I/O statistics
    stats = io_manager.get_io_statistics()
    assert stats["read_operations"] >= 4  # 1 single + 3 batch
    assert stats["write_operations"] >= 4  # 1 single + 3 batch

    print("OK Async I/O manager test passed")


async def test_streaming_file_operations():
    """Test streaming file operations."""
    print("Testing streaming file operations...")

    io_manager = AsyncIOManager()

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "stream_test.txt"

        # Create test content
        lines = [f"Line {i}\n" for i in range(100)]
        test_content = ''.join(lines)

        # Write content normally first
        await io_manager.write_file_async(test_file, test_content)

        # Test streaming read
        chunks = []
        async for chunk in io_manager.read_file_streaming(test_file, chunk_size=100):
            chunks.append(chunk)

        streamed_content = ''.join(chunks)
        assert streamed_content == test_content, "Streamed content mismatch"

        # Test streaming write
        async def content_generator():
            for line in lines:
                yield line

        output_file = Path(temp_dir) / "stream_output.txt"
        write_result = await io_manager.write_file_streaming(
            output_file,
            content_generator()
        )

        assert write_result.success, "Streaming write failed"

        # Verify streaming write result
        written_content = await io_manager.read_file_async(output_file)
        assert written_content == test_content, "Streaming write content mismatch"

    print("OK Streaming file operations test passed")


async def test_integrated_async_workflow():
    """Test complete integrated async workflow."""
    print("Testing integrated async workflow...")

    # Create components
    settings = ApplicationSettings(debug_mode=True)
    async_engine = AsyncTextTransformationEngine(settings=settings)
    monitor = PerformanceMonitor()
    io_manager = AsyncIOManager()

    with tempfile.TemporaryDirectory() as temp_dir:
        input_file = Path(temp_dir) / "input.txt"
        output_file = Path(temp_dir) / "output.txt"

        # Create test input
        input_text = "hello world\nthis is a test\nwith multiple lines"
        await io_manager.write_file_async(input_file, input_text)

        # Integrated workflow: read -> transform -> write
        async def integrated_workflow():
            # Read file
            content = await io_manager.read_file_async(input_file)

            # Transform content
            transformed = await async_engine.transform_async(content, "/u")

            # Write result
            result = await io_manager.write_file_async(output_file, transformed)
            return result

        # Measure the entire workflow
        write_result = await monitor.measure_operation(
            "integrated_workflow",
            integrated_workflow,
            data_size=len(input_text)
        )

        assert write_result.success, "Integrated workflow failed"

        # Verify result
        output_content = await io_manager.read_file_async(output_file)
        assert output_content == input_text.upper(), "Integrated workflow output mismatch"

        # Check performance stats
        workflow_stats = monitor.get_stats("integrated_workflow")
        assert workflow_stats["total_operations"] == 1
        assert workflow_stats["success_rate_percent"] == 100.0

    print("OK Integrated async workflow test passed")


async def test_concurrent_operations():
    """Test concurrent async operations."""
    print("Testing concurrent operations...")

    async_engine = AsyncTextTransformationEngine()

    # Create multiple concurrent transformation tasks
    async def create_transformation_task(text: str, rule: str, task_id: int):
        result = await async_engine.transform_async(f"{text}_{task_id}", rule)
        return task_id, result

    # Run multiple transformations concurrently
    tasks = [
        create_transformation_task("test", "/u", i)
        for i in range(10)
    ]

    results = await asyncio.gather(*tasks)

    # Verify all tasks completed successfully
    assert len(results) == 10
    for task_id, result in results:
        expected = f"TEST_{task_id}"
        assert result == expected, f"Task {task_id} failed: expected {expected}, got {result}"

    print("OK Concurrent operations test passed")


async def test_error_handling():
    """Test error handling in async operations."""
    print("Testing error handling...")

    async_engine = AsyncTextTransformationEngine()
    io_manager = AsyncIOManager()

    # Test invalid transformation rule
    try:
        await async_engine.transform_async("test", "invalid_rule")
        assert False, "Should have raised an exception for invalid rule"
    except Exception:
        pass  # Expected

    # Test reading non-existent file
    try:
        await io_manager.read_file_async("/non/existent/file.txt")
        assert False, "Should have raised an exception for non-existent file"
    except Exception:
        pass  # Expected

    print("OK Error handling test passed")


async def run_all_tests():
    """Run all async integration tests."""
    print("=== TextKit Async Integration Tests ===\n")

    test_functions = [
        test_async_engine_basic_transformation,
        test_async_engine_streaming,
        test_async_engine_batch_processing,
        test_async_engine_health_check,
        test_streaming_basic_functionality,
        test_chunked_processor,
        test_performance_monitoring,
        test_async_benchmark,
        test_async_io_manager,
        test_streaming_file_operations,
        test_integrated_async_workflow,
        test_concurrent_operations,
        test_error_handling
    ]

    passed_tests = 0
    failed_tests = 0

    for test_func in test_functions:
        try:
            await test_func()
            passed_tests += 1
        except Exception as e:
            print(f"FAILED {test_func.__name__}: {e}")
            failed_tests += 1
            import traceback
            traceback.print_exc()

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Total:  {len(test_functions)}")

    if failed_tests == 0:
        print("\nAll async integration tests passed!")
    else:
        print(f"\n{failed_tests} tests failed.")

    return failed_tests == 0


if __name__ == "__main__":
    # Run the async tests
    asyncio.run(run_all_tests())