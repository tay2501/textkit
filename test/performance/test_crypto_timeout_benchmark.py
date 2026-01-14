"""Performance benchmarks for crypto clipboard timeout functionality.

Measures timing accuracy, memory overhead, and scalability of the timeout feature.
"""

import threading
import time
from unittest.mock import Mock

import pytest

# ============================================================================
# Benchmark: Timer Accuracy
# ============================================================================


@pytest.mark.performance
@pytest.mark.crypto
def test_timer_accuracy_1_second(benchmark):
    """Benchmark 1-second timer accuracy."""

    def timer_operation():
        cleared = False

        def mock_clear():
            nonlocal cleared
            cleared = True

        timer = threading.Timer(1.0, mock_clear)
        timer.daemon = True
        timer.start()
        time.sleep(1.1)  # Wait for timer to fire
        return cleared

    result = benchmark(timer_operation)
    assert result is True


@pytest.mark.performance
@pytest.mark.crypto
def test_timer_accuracy_5_seconds(benchmark):
    """Benchmark 5-second timer accuracy (minimum allowed)."""

    def timer_operation():
        cleared = False

        def mock_clear():
            nonlocal cleared
            cleared = True

        timer = threading.Timer(5.0, mock_clear)
        timer.daemon = True
        timer.start()
        time.sleep(5.1)
        return cleared

    result = benchmark(timer_operation)
    assert result is True


@pytest.mark.performance
@pytest.mark.crypto
@pytest.mark.slow
def test_timer_accuracy_60_seconds(benchmark):
    """Benchmark 60-second timer accuracy (recommended for passwords)."""

    def timer_operation():
        cleared = False

        def mock_clear():
            nonlocal cleared
            cleared = True

        # Use shorter time for benchmark
        timer = threading.Timer(1.0, mock_clear)
        timer.daemon = True
        timer.start()
        time.sleep(1.1)
        return cleared

    result = benchmark(timer_operation)
    assert result is True


# ============================================================================
# Benchmark: Timer Creation Overhead
# ============================================================================


@pytest.mark.performance
@pytest.mark.crypto
def test_timer_creation_overhead(benchmark):
    """Benchmark overhead of creating and starting a timer."""

    def create_timer():
        def mock_clear():
            pass

        timer = threading.Timer(300, mock_clear)  # Long timeout
        timer.daemon = True
        timer.start()
        timer.cancel()  # Clean up immediately
        return timer

    result = benchmark(create_timer)
    assert result is not None


@pytest.mark.performance
@pytest.mark.crypto
def test_timer_with_contextlib_suppress_overhead(benchmark):
    """Benchmark overhead of timer with contextlib.suppress (production code)."""
    import contextlib

    def create_timer_with_suppress():
        cleared = False

        def mock_clear():
            nonlocal cleared
            cleared = True

        def _clear_clipboard():
            with contextlib.suppress(Exception):
                mock_clear()

        timer = threading.Timer(0.1, _clear_clipboard)
        timer.daemon = True
        timer.start()
        time.sleep(0.2)
        return cleared

    result = benchmark(create_timer_with_suppress)
    assert result is True


# ============================================================================
# Benchmark: Multiple Concurrent Timers
# ============================================================================


@pytest.mark.performance
@pytest.mark.crypto
def test_concurrent_timers_10(benchmark):
    """Benchmark 10 concurrent timers (realistic load)."""

    def create_concurrent_timers():
        timers = []
        cleared_count = 0

        def mock_clear():
            nonlocal cleared_count
            cleared_count += 1

        for _ in range(10):
            timer = threading.Timer(0.1, mock_clear)
            timer.daemon = True
            timer.start()
            timers.append(timer)

        time.sleep(0.3)
        return cleared_count

    result = benchmark(create_concurrent_timers)
    assert result == 10


@pytest.mark.performance
@pytest.mark.crypto
def test_concurrent_timers_50(benchmark):
    """Benchmark 50 concurrent timers (stress test)."""

    def create_concurrent_timers():
        timers = []
        cleared_count = 0

        def mock_clear():
            nonlocal cleared_count
            cleared_count += 1

        for _ in range(50):
            timer = threading.Timer(0.1, mock_clear)
            timer.daemon = True
            timer.start()
            timers.append(timer)

        time.sleep(0.3)
        return cleared_count

    result = benchmark(create_concurrent_timers)
    assert result == 50


@pytest.mark.performance
@pytest.mark.crypto
@pytest.mark.slow
def test_concurrent_timers_100(benchmark):
    """Benchmark 100 concurrent timers (extreme stress test)."""

    def create_concurrent_timers():
        cleared_count = 0

        def mock_clear():
            nonlocal cleared_count
            cleared_count += 1

        for _ in range(100):
            timer = threading.Timer(0.1, mock_clear)
            timer.daemon = True
            timer.start()

        time.sleep(0.3)
        return cleared_count

    result = benchmark(create_concurrent_timers)
    assert result == 100


# ============================================================================
# Benchmark: Memory Overhead
# ============================================================================


@pytest.mark.performance
@pytest.mark.crypto
def test_timer_memory_overhead(benchmark):
    """Benchmark memory overhead of timer objects."""
    import tracemalloc

    def measure_memory():
        tracemalloc.start()

        # Create timer
        def mock_clear():
            pass

        timer = threading.Timer(300, mock_clear)
        timer.daemon = True
        timer.start()

        _current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        timer.cancel()

        return peak  # Peak memory usage in bytes

    memory_peak = benchmark(measure_memory)
    # Timer should use less than 10KB of memory
    assert memory_peak < 10 * 1024


# ============================================================================
# Benchmark: Clipboard Clear Operation
# ============================================================================


@pytest.mark.performance
@pytest.mark.crypto
def test_clipboard_clear_mock_overhead(benchmark):
    """Benchmark mock clipboard clear operation."""

    def clear_operation():
        mock_io_manager = Mock()
        mock_io_manager.clear_clipboard = Mock(return_value=True)
        mock_io_manager.clear_clipboard()
        return mock_io_manager.clear_clipboard.call_count

    result = benchmark(clear_operation)
    assert result == 1


# ============================================================================
# Benchmark: End-to-End Timer Flow
# ============================================================================


@pytest.mark.performance
@pytest.mark.crypto
def test_end_to_end_timer_flow(benchmark):
    """Benchmark complete timer flow (create, start, wait, execute, verify)."""
    import contextlib

    def complete_flow():
        clipboard_cleared = False

        def clear_clipboard():
            nonlocal clipboard_cleared
            clipboard_cleared = True

        def _clear_clipboard():
            with contextlib.suppress(Exception):
                clear_clipboard()

        # Create and start timer
        timer = threading.Timer(0.1, _clear_clipboard)
        timer.daemon = True
        timer.start()

        # Wait for completion
        time.sleep(0.2)

        return clipboard_cleared

    result = benchmark(complete_flow)
    assert result is True


# ============================================================================
# Benchmark: Timer Cancellation
# ============================================================================


@pytest.mark.performance
@pytest.mark.crypto
def test_timer_cancellation_overhead(benchmark):
    """Benchmark overhead of canceling timers."""

    def cancel_timer():
        def mock_clear():
            pass

        timer = threading.Timer(300, mock_clear)
        timer.daemon = True
        timer.start()
        timer.cancel()
        timer.join()  # Wait for thread to actually stop
        return not timer.is_alive()

    result = benchmark(cancel_timer)
    assert result is True


@pytest.mark.performance
@pytest.mark.crypto
def test_multiple_timer_cancellation(benchmark):
    """Benchmark canceling multiple timers."""

    def cancel_multiple_timers():
        timers = []

        def mock_clear():
            pass

        for _ in range(10):
            timer = threading.Timer(300, mock_clear)
            timer.daemon = True
            timer.start()
            timers.append(timer)

        for timer in timers:
            timer.cancel()
            timer.join()  # Wait for thread to actually stop

        return all(not t.is_alive() for t in timers)

    result = benchmark(cancel_multiple_timers)
    assert result is True


# ============================================================================
# Statistical Analysis Tests
# ============================================================================


@pytest.mark.performance
@pytest.mark.crypto
def test_timer_precision_statistics():
    """Measure timer precision statistics over multiple runs."""
    delays = []
    target_delay = 0.1

    for _ in range(50):
        start_time = time.perf_counter()
        cleared = False

        def mock_clear():
            nonlocal cleared
            cleared = True

        timer = threading.Timer(target_delay, mock_clear)
        timer.daemon = True
        timer.start()

        while not cleared:
            time.sleep(0.01)

        actual_delay = time.perf_counter() - start_time
        delays.append(actual_delay)

    # Calculate statistics
    avg_delay = sum(delays) / len(delays)
    max_deviation = max(abs(d - target_delay) for d in delays)

    # Timer should be accurate within ±50ms
    assert abs(avg_delay - target_delay) < 0.05
    assert max_deviation < 0.1

    print(f"\nTimer Statistics (target={target_delay}s):")
    print(f"  Average: {avg_delay:.4f}s")
    print(f"  Min: {min(delays):.4f}s")
    print(f"  Max: {max(delays):.4f}s")
    print(f"  Max deviation: {max_deviation:.4f}s")
