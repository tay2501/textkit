"""
Async capabilities demonstration script for TextKit.

This script showcases the powerful async text processing features
including streaming, performance monitoring, and concurrent operations.
"""

import asyncio
import time
from pathlib import Path
import tempfile

from components.text_processing.async_core import (
    AsyncTextTransformationEngine,
    ChunkedProcessor,
    PerformanceMonitor,
    AsyncBenchmark,
    AsyncIOManager
)


async def demonstrate_basic_async_transformation():
    """Demonstrate basic async text transformation."""
    print("=== Basic Async Transformation Demo ===")

    async_engine = AsyncTextTransformationEngine()

    # Simple transformation
    text = "hello async world!"
    result = await async_engine.transform_async(text, "/u")
    print(f"Input:  {text}")
    print(f"Output: {result}")

    # Multiple transformations
    transformations = [
        ("test 123", "/u"),
        ("LOWER CASE", "/l"),
        ("replace this", "/r/this/that/")
    ]

    print("\nBatch transformations:")
    batch_results = await async_engine.transform_batch_async(transformations)

    for i, ((text, rule), result) in enumerate(zip(transformations, batch_results)):
        print(f"  {i+1}. '{text}' with '{rule}' -> '{result}'")

    print()


async def demonstrate_streaming_processing():
    """Demonstrate streaming text processing."""
    print("=== Streaming Processing Demo ===")

    async_engine = AsyncTextTransformationEngine(chunk_size=100)

    # Create large text for streaming
    large_text = "This is a test sentence for streaming. " * 50  # ~2KB
    print(f"Processing {len(large_text)} characters with streaming...")

    start_time = time.perf_counter()

    # Process with streaming enabled
    stream_result = await async_engine.transform_async(
        large_text,
        "/u",
        enable_streaming=True
    )

    if hasattr(stream_result, '__aiter__'):
        # Stream processing
        chunks_processed = 0
        result_parts = []

        async for chunk in stream_result:
            result_parts.append(chunk)
            chunks_processed += 1

        final_result = ''.join(result_parts)
        print(f"Processed in {chunks_processed} chunks")
    else:
        # Direct processing (for smaller text)
        final_result = stream_result
        print("Processed directly (text was small)")

    processing_time = time.perf_counter() - start_time
    print(f"Processing time: {processing_time*1000:.2f}ms")
    print(f"Throughput: {len(large_text)/processing_time:.0f} chars/second")
    print()


async def demonstrate_chunked_processing():
    """Demonstrate adaptive chunked processing."""
    print("=== Chunked Processing Demo ===")

    processor = ChunkedProcessor()

    # Test with different sized texts
    test_texts = [
        ("Small text", "small " * 10),
        ("Medium text", "medium " * 100),
        ("Large text", "large " * 1000)
    ]

    for name, text in test_texts:
        start_time = time.perf_counter()
        result = await processor.process_chunks(text, "/u")
        processing_time = time.perf_counter() - start_time

        print(f"{name}: {len(text)} chars -> {processing_time*1000:.2f}ms")

    # Show performance info
    perf_info = processor.get_performance_info()
    print(f"\nOptimal chunk size: {perf_info['optimal_chunk_size']:,} bytes")
    print(f"Performance samples: {perf_info['performance_samples']}")
    if perf_info['average_throughput_chars_per_sec'] > 0:
        print(f"Average throughput: {perf_info['average_throughput_chars_per_sec']:,.0f} chars/sec")

    print()


async def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    print("=== Performance Monitoring Demo ===")

    monitor = PerformanceMonitor()
    async_engine = AsyncTextTransformationEngine()

    # Set performance alert thresholds
    monitor.set_alert_threshold("text_transformation", max_duration=0.1, min_throughput=10000)

    # Test different operations
    operations = [
        ("Short text", "hello", "/u"),
        ("Medium text", "test " * 100, "/u"),
        ("Long text", "performance " * 500, "/r/performance/PERF/")
    ]

    for name, text, rule in operations:
        result = await monitor.measure_operation(
            "text_transformation",
            async_engine.transform_async,
            text, rule,
            data_size=len(text)
        )
        print(f"Processed: {name} -> {len(result)} chars")

    # Show performance statistics
    stats = monitor.get_stats("text_transformation")
    print("\nPerformance Statistics:")
    print(f"- Total operations: {stats['total_operations']}")
    print(f"- Success rate: {stats['success_rate_percent']:.1f}%")
    print(f"- Average duration: {stats['average_duration_ms']:.2f}ms")
    print(f"- Throughput: {stats['throughput_bytes_per_sec']:,.0f} bytes/sec")
    print(f"- 95th percentile: {stats['percentile_95_ms']:.2f}ms")

    # System overview
    overview = monitor.get_system_overview()
    print("\nSystem Overview:")
    print(f"- Uptime: {overview['uptime_seconds']:.1f}s")
    print(f"- Total data processed: {overview['total_data_processed_bytes']:,} bytes")
    print(f"- System throughput: {overview['average_system_throughput_bytes_per_sec']:,.0f} bytes/sec")

    print()


async def demonstrate_async_io():
    """Demonstrate async I/O capabilities."""
    print("=== Async I/O Demo ===")

    io_manager = AsyncIOManager()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        test_files = {
            temp_path / "file1.txt": "First file content\nWith multiple lines",
            temp_path / "file2.txt": "Second file content\nAlso with multiple lines",
            temp_path / "file3.txt": "Third file content\nAnd some more text"
        }

        print("Writing files concurrently...")
        start_time = time.perf_counter()

        # Batch write files
        write_results = await io_manager.batch_write_files(test_files)
        write_time = time.perf_counter() - start_time

        successful_writes = sum(1 for result in write_results.values() if result.success)
        print(f"Wrote {successful_writes}/{len(test_files)} files in {write_time*1000:.2f}ms")

        # Batch read files
        print("Reading files concurrently...")
        start_time = time.perf_counter()

        file_paths = list(test_files.keys())
        read_results = await io_manager.batch_read_files(file_paths)
        read_time = time.perf_counter() - start_time

        successful_reads = sum(1 for content in read_results.values()
                              if not isinstance(content, Exception))
        print(f"Read {successful_reads}/{len(file_paths)} files in {read_time*1000:.2f}ms")

        # Show I/O statistics
        stats = io_manager.get_io_statistics()
        print("\nI/O Statistics:")
        print(f"- Read operations: {stats['read_operations']}")
        print(f"- Write operations: {stats['write_operations']}")
        print(f"- Read speed: {stats['average_read_speed_bytes_per_sec']:,.0f} bytes/sec")
        print(f"- Write speed: {stats['average_write_speed_bytes_per_sec']:,.0f} bytes/sec")

    print()


async def demonstrate_benchmarking():
    """Demonstrate async benchmarking capabilities."""
    print("=== Benchmarking Demo ===")

    monitor = PerformanceMonitor()
    benchmark = AsyncBenchmark(monitor)

    # Functions to benchmark
    async def sync_style_transform(text: str, rule: str):
        """Simulate synchronous-style transformation."""
        await asyncio.sleep(0.001)  # Simulate processing delay
        engine = AsyncTextTransformationEngine()
        return await engine.transform_async(text, rule)

    async def optimized_transform(text: str, rule: str):
        """Simulate optimized transformation."""
        await asyncio.sleep(0.0005)  # Faster processing
        engine = AsyncTextTransformationEngine()
        return await engine.transform_async(text, rule)

    # Test cases
    test_cases = [
        (("hello",), {"rule": "/u"}),
        (("world",), {"rule": "/u"}),
        (("benchmark test",), {"rule": "/r/test/TEST/"})
    ]

    print("Benchmarking transformation functions...")

    # Compare functions
    comparison = await benchmark.compare_functions(
        [sync_style_transform, optimized_transform],
        test_cases,
        iterations=20
    )

    print("\nBenchmark Results:")
    print(f"Fastest function: {comparison['comparison']['fastest_function']}")
    print(f"Speed improvement: {comparison['comparison']['speed_improvement_factor']:.2f}x")

    for perf in comparison['comparison']['relative_performance']:
        print(f"- {perf['function']}: {perf['relative_speed']:.2f}x relative speed")

    print()


async def demonstrate_concurrent_operations():
    """Demonstrate concurrent async operations."""
    print("=== Concurrent Operations Demo ===")

    async_engine = AsyncTextTransformationEngine()

    # Create multiple concurrent tasks
    async def concurrent_task(task_id: int, delay: float):
        await asyncio.sleep(delay)  # Simulate varying processing times
        text = f"Task {task_id} text"
        result = await async_engine.transform_async(text, "/u")
        return task_id, result, delay

    print("Running 10 concurrent transformation tasks...")
    start_time = time.perf_counter()

    # Create tasks with different delays
    tasks = [
        concurrent_task(i, 0.01 + (i % 3) * 0.005)
        for i in range(10)
    ]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start_time

    print(f"Completed {len(results)} tasks in {total_time*1000:.2f}ms")

    # Show results
    for task_id, result, delay in sorted(results):
        print(f"  Task {task_id}: '{result}' (simulated delay: {delay*1000:.1f}ms)")

    # Calculate efficiency
    total_simulated_time = sum(delay for _, _, delay in results)
    efficiency = (total_simulated_time / total_time) * 100
    print(f"\nConcurrency efficiency: {efficiency:.1f}%")
    print(f"(Completed {total_simulated_time:.3f}s of work in {total_time:.3f}s)")

    print()


async def demonstrate_integrated_workflow():
    """Demonstrate complete integrated async workflow."""
    print("=== Integrated Workflow Demo ===")

    # Create components
    async_engine = AsyncTextTransformationEngine()
    monitor = PerformanceMonitor()
    io_manager = AsyncIOManager()

    with tempfile.TemporaryDirectory() as temp_dir:
        input_file = Path(temp_dir) / "input.txt"
        output_file = Path(temp_dir) / "output.txt"

        # Create sample input
        sample_text = """This is a sample document for processing.
It contains multiple lines of text.
Each line will be transformed using async processing.
The result will demonstrate the integrated workflow."""

        print("Integrated workflow: File -> Transform -> File")

        async def integrated_workflow():
            # Step 1: Write input file
            await io_manager.write_file_async(input_file, sample_text)
            print("1. Input file created")

            # Step 2: Read and transform
            content = await io_manager.read_file_async(input_file)
            transformed = await async_engine.transform_async(content, "/u")
            print("2. Content transformed")

            # Step 3: Write output
            result = await io_manager.write_file_async(output_file, transformed)
            print("3. Output file written")

            return result

        # Execute with monitoring
        start_time = time.perf_counter()

        write_result = await monitor.measure_operation(
            "integrated_workflow",
            integrated_workflow,
            data_size=len(sample_text)
        )

        total_time = time.perf_counter() - start_time

        print(f"\nWorkflow completed in {total_time*1000:.2f}ms")
        print(f"Input size: {len(sample_text)} characters")
        print(f"Output size: {write_result.data_size} characters")

        # Show workflow stats
        workflow_stats = monitor.get_stats("integrated_workflow")
        print(f"Workflow throughput: {workflow_stats['throughput_bytes_per_sec']:,.0f} bytes/sec")

    print()


async def main():
    """Run all async demonstrations."""
    print("TextKit Async Processing Demonstration\n")

    demonstrations = [
        demonstrate_basic_async_transformation,
        demonstrate_streaming_processing,
        demonstrate_chunked_processing,
        demonstrate_performance_monitoring,
        demonstrate_async_io,
        demonstrate_benchmarking,
        demonstrate_concurrent_operations,
        demonstrate_integrated_workflow
    ]

    for demo in demonstrations:
        try:
            await demo()
        except Exception as e:
            print(f"Demo failed: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=== Demo Complete ===")
    print("Key Async Features Demonstrated:")
    print("- High-performance async text transformation")
    print("- Streaming and chunked processing for large texts")
    print("- Real-time performance monitoring and metrics")
    print("- Concurrent async I/O operations")
    print("- Comprehensive benchmarking capabilities")
    print("- Integrated async workflows")
    print("- Memory-efficient processing patterns")


if __name__ == "__main__":
    asyncio.run(main())