"""
Performance monitoring and benchmarking for async text processing.

This module provides comprehensive performance monitoring capabilities
with real-time metrics, benchmarking tools, and optimization insights.
"""

from __future__ import annotations

import asyncio
import statistics
import time
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any, NamedTuple

import structlog

from components.config_manager.settings import ApplicationSettings, get_settings

# Initialize logger
logger = structlog.get_logger(__name__)


class PerformanceMetric(NamedTuple):
    """Single performance measurement."""

    timestamp: float
    operation: str
    duration: float
    data_size: int
    success: bool
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class PerformanceStats:
    """Aggregated performance statistics.

    Uses slots=True for 40-50% memory reduction per instance.
    """

    operation: str
    total_operations: int = 0
    successful_operations: int = 0
    total_duration: float = 0.0
    total_data_processed: int = 0
    min_duration: float = float("inf")
    max_duration: float = 0.0
    recent_durations: deque = field(default_factory=lambda: deque(maxlen=100))

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100

    @property
    def average_duration(self) -> float:
        """Calculate average operation duration."""
        if self.successful_operations == 0:
            return 0.0
        return self.total_duration / self.successful_operations

    @property
    def throughput_per_second(self) -> float:
        """Calculate data throughput per second."""
        if self.total_duration == 0:
            return 0.0
        return self.total_data_processed / self.total_duration

    @property
    def recent_average_duration(self) -> float:
        """Calculate recent average duration from last 100 operations."""
        if not self.recent_durations:
            return 0.0
        return statistics.mean(self.recent_durations)

    @property
    def percentile_95(self) -> float:
        """Calculate 95th percentile of recent durations."""
        if len(self.recent_durations) < 5:
            return 0.0
        return statistics.quantiles(self.recent_durations, n=20)[18]  # 95th percentile


class PerformanceMonitor:
    """Real-time performance monitoring for async operations."""

    def __init__(
        self,
        settings: ApplicationSettings | None = None,
        max_metrics_history: int = 10000,
    ) -> None:
        """Initialize performance monitor.

        Args:
            settings: Application settings
            max_metrics_history: Maximum number of metrics to keep in history
        """
        self.settings = settings or get_settings()
        self.max_metrics_history = max_metrics_history

        # Metrics storage
        self._metrics: deque[PerformanceMetric] = deque(maxlen=max_metrics_history)
        self._stats: dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self._start_time = time.perf_counter()

        # Real-time monitoring
        self._monitoring_enabled = True
        self._alert_thresholds: dict[str, dict[str, float]] = {}

        logger.info("performance_monitor_initialized", max_history=max_metrics_history)

    async def measure_operation(
        self,
        operation_name: str,
        operation_func: Callable,
        *args,
        data_size: int | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> Any:
        """Measure the performance of an async operation.

        Args:
            operation_name: Name of the operation being measured
            operation_func: Async function to measure
            *args: Arguments to pass to the function
            data_size: Size of data being processed (optional)
            metadata: Additional metadata to store with the metric
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the operation function
        """
        if not self._monitoring_enabled:
            return await operation_func(*args, **kwargs)

        start_time = time.perf_counter()
        success = False
        result = None
        error = None

        try:
            result = await operation_func(*args, **kwargs)
            success = True
            return result

        except Exception as e:
            error = e
            raise

        finally:
            duration = time.perf_counter() - start_time

            # Estimate data size if not provided
            if data_size is None:
                data_size = self._estimate_data_size(args, kwargs, result)

            # Create metric
            metric = PerformanceMetric(
                timestamp=time.perf_counter(),
                operation=operation_name,
                duration=duration,
                data_size=data_size,
                success=success,
                metadata=metadata or {},
            )

            # Store metric
            self._metrics.append(metric)
            self._update_stats(metric)

            # Check for performance alerts
            await self._check_performance_alerts(operation_name, metric)

            # Log performance data
            logger.debug(
                "operation_measured",
                operation=operation_name,
                duration_ms=duration * 1000,
                data_size=data_size,
                success=success,
                error=str(error) if error else None,
            )

    def _estimate_data_size(self, args: tuple, kwargs: dict, result: Any) -> int:
        """Estimate data size from function arguments and result.

        Args:
            args: Function arguments
            kwargs: Function keyword arguments
            result: Function result

        Returns:
            Estimated data size in bytes
        """
        total_size = 0

        # Check common string arguments
        for arg in args:
            if isinstance(arg, str):
                total_size += len(arg.encode("utf-8"))

        for value in kwargs.values():
            if isinstance(value, str):
                total_size += len(value.encode("utf-8"))

        # Check result size
        if isinstance(result, str):
            total_size += len(result.encode("utf-8"))

        return total_size

    def _update_stats(self, metric: PerformanceMetric) -> None:
        """Update aggregated statistics with new metric.

        Args:
            metric: New performance metric
        """
        # Initialize stats for operation if it doesn't exist
        if metric.operation not in self._stats:
            self._stats[metric.operation] = PerformanceStats(operation=metric.operation)

        stats = self._stats[metric.operation]

        # Update counters
        stats.total_operations += 1
        if metric.success:
            stats.successful_operations += 1
            stats.total_duration += metric.duration
            stats.total_data_processed += metric.data_size

            # Update min/max durations
            stats.min_duration = min(stats.min_duration, metric.duration)
            stats.max_duration = max(stats.max_duration, metric.duration)

            # Add to recent durations
            stats.recent_durations.append(metric.duration)

    async def _check_performance_alerts(
        self, operation_name: str, metric: PerformanceMetric
    ) -> None:
        """Check for performance alerts and log warnings.

        Args:
            operation_name: Name of the operation
            metric: Performance metric to check
        """
        if operation_name not in self._alert_thresholds:
            return

        thresholds = self._alert_thresholds[operation_name]

        # Check duration threshold
        if (
            "max_duration" in thresholds
            and metric.duration > thresholds["max_duration"]
        ):
            logger.warning(
                "performance_alert_duration",
                operation=operation_name,
                actual_duration=metric.duration,
                threshold=thresholds["max_duration"],
            )

        # Check throughput threshold
        if "min_throughput" in thresholds and metric.data_size > 0:
            throughput = metric.data_size / metric.duration
            if throughput < thresholds["min_throughput"]:
                logger.warning(
                    "performance_alert_throughput",
                    operation=operation_name,
                    actual_throughput=throughput,
                    threshold=thresholds["min_throughput"],
                )

    def set_alert_threshold(
        self,
        operation_name: str,
        max_duration: float | None = None,
        min_throughput: float | None = None,
    ) -> None:
        """Set performance alert thresholds for an operation.

        Args:
            operation_name: Name of the operation
            max_duration: Maximum acceptable duration in seconds
            min_throughput: Minimum acceptable throughput in bytes/second
        """
        if operation_name not in self._alert_thresholds:
            self._alert_thresholds[operation_name] = {}

        if max_duration is not None:
            self._alert_thresholds[operation_name]["max_duration"] = max_duration

        if min_throughput is not None:
            self._alert_thresholds[operation_name]["min_throughput"] = min_throughput

        logger.info(
            "alert_threshold_set",
            operation=operation_name,
            max_duration=max_duration,
            min_throughput=min_throughput,
        )

    def get_stats(self, operation_name: str | None = None) -> dict[str, Any]:
        """Get performance statistics.

        Args:
            operation_name: Specific operation to get stats for (optional)

        Returns:
            Dictionary with performance statistics
        """
        if operation_name:
            if operation_name not in self._stats:
                return {}

            stats = self._stats[operation_name]
            return {
                "operation": operation_name,
                "total_operations": stats.total_operations,
                "successful_operations": stats.successful_operations,
                "success_rate_percent": stats.success_rate,
                "average_duration_ms": stats.average_duration * 1000,
                "recent_average_duration_ms": stats.recent_average_duration * 1000,
                "min_duration_ms": stats.min_duration * 1000
                if stats.min_duration != float("inf")
                else 0,
                "max_duration_ms": stats.max_duration * 1000,
                "throughput_bytes_per_sec": stats.throughput_per_second,
                "percentile_95_ms": stats.percentile_95 * 1000,
                "total_data_processed_bytes": stats.total_data_processed,
            }

        # Return all stats
        return {operation: self.get_stats(operation) for operation in self._stats}

    def get_recent_metrics(self, count: int = 100) -> list[dict[str, Any]]:
        """Get recent performance metrics.

        Args:
            count: Number of recent metrics to return

        Returns:
            List of recent metrics
        """
        recent_metrics = list(self._metrics)[-count:]
        return [
            {
                "timestamp": metric.timestamp,
                "operation": metric.operation,
                "duration_ms": metric.duration * 1000,
                "data_size_bytes": metric.data_size,
                "success": metric.success,
                "metadata": metric.metadata,
            }
            for metric in recent_metrics
        ]

    def clear_metrics(self) -> None:
        """Clear all stored metrics and statistics."""
        self._metrics.clear()
        self._stats.clear()
        self._start_time = time.perf_counter()
        logger.info("performance_metrics_cleared")

    def enable_monitoring(self) -> None:
        """Enable performance monitoring."""
        self._monitoring_enabled = True
        logger.info("performance_monitoring_enabled")

    def disable_monitoring(self) -> None:
        """Disable performance monitoring."""
        self._monitoring_enabled = False
        logger.info("performance_monitoring_disabled")

    def get_system_overview(self) -> dict[str, Any]:
        """Get system-wide performance overview.

        Returns:
            Dictionary with system performance overview
        """
        total_operations = sum(stats.total_operations for stats in self._stats.values())
        total_successful = sum(
            stats.successful_operations for stats in self._stats.values()
        )
        total_duration = sum(stats.total_duration for stats in self._stats.values())
        total_data = sum(stats.total_data_processed for stats in self._stats.values())

        uptime = time.perf_counter() - self._start_time

        return {
            "uptime_seconds": uptime,
            "total_operations": total_operations,
            "successful_operations": total_successful,
            "overall_success_rate_percent": (total_successful / total_operations * 100)
            if total_operations > 0
            else 0,
            "total_processing_time_seconds": total_duration,
            "total_data_processed_bytes": total_data,
            "average_system_throughput_bytes_per_sec": total_data / uptime
            if uptime > 0
            else 0,
            "operations_tracked": len(self._stats),
            "metrics_stored": len(self._metrics),
            "monitoring_enabled": self._monitoring_enabled,
        }


class AsyncBenchmark:
    """Comprehensive async benchmarking toolkit."""

    def __init__(
        self,
        monitor: PerformanceMonitor | None = None,
        settings: ApplicationSettings | None = None,
    ) -> None:
        """Initialize async benchmark.

        Args:
            monitor: Performance monitor instance
            settings: Application settings
        """
        self.monitor = monitor or PerformanceMonitor()
        self.settings = settings or get_settings()

    def _calculate_benchmark_stats(
        self, case_name: str, args: tuple, kwargs: dict, iterations: int,
        successful_runs: int, durations: list[float]
    ) -> dict[str, Any]:
        """Calculate statistics for a benchmark case.

        Args:
            case_name: Name of the test case
            args: Function arguments
            kwargs: Function keyword arguments
            iterations: Total number of iterations
            successful_runs: Number of successful runs
            durations: List of execution durations

        Returns:
            Case statistics dictionary
        """
        return {
            "case_name": case_name,
            "args_size": len(str(args)),
            "kwargs_size": len(str(kwargs)),
            "iterations": iterations,
            "successful_runs": successful_runs,
            "success_rate_percent": (successful_runs / iterations) * 100,
            "min_duration_ms": min(durations) * 1000,
            "max_duration_ms": max(durations) * 1000,
            "mean_duration_ms": statistics.mean(durations) * 1000,
            "median_duration_ms": statistics.median(durations) * 1000,
            "stdev_duration_ms": statistics.stdev(durations) * 1000 if len(durations) > 1 else 0,
            "percentile_95_ms": statistics.quantiles(durations, n=20)[18] * 1000
            if len(durations) > 5 else 0,
            "percentile_99_ms": statistics.quantiles(durations, n=100)[98] * 1000
            if len(durations) > 10 else 0,
        }

    def _calculate_overall_summary(self, durations: list[float], test_cases_count: int) -> dict[str, Any]:
        """Calculate overall benchmark summary.

        Args:
            durations: All execution durations across test cases
            test_cases_count: Number of test cases

        Returns:
            Summary statistics dictionary
        """
        if not durations:
            return {}

        return {
            "total_test_cases": test_cases_count,
            "total_iterations": len(durations),
            "overall_min_duration_ms": min(durations) * 1000,
            "overall_max_duration_ms": max(durations) * 1000,
            "overall_mean_duration_ms": statistics.mean(durations) * 1000,
            "overall_median_duration_ms": statistics.median(durations) * 1000,
            "overall_stdev_duration_ms": statistics.stdev(durations) * 1000
            if len(durations) > 1 else 0,
            "overall_percentile_95_ms": statistics.quantiles(durations, n=20)[18] * 1000
            if len(durations) > 5 else 0,
            "overall_percentile_99_ms": statistics.quantiles(durations, n=100)[98] * 1000
            if len(durations) > 10 else 0,
        }

    async def benchmark_function(
        self,
        func: Callable,
        test_cases: list[tuple],
        iterations: int = 100,
        warmup_iterations: int = 10,
    ) -> dict[str, Any]:
        """Benchmark an async function with multiple test cases.

        Args:
            func: Async function to benchmark
            test_cases: List of (args, kwargs) tuples for test cases
            iterations: Number of iterations per test case
            warmup_iterations: Number of warmup iterations

        Returns:
            Comprehensive benchmark results
        """
        logger.info(
            "benchmark_starting",
            function=func.__name__,
            test_cases=len(test_cases),
            iterations=iterations,
        )

        results: dict[str, Any] = {"function_name": func.__name__, "test_cases": [], "summary": {}}
        all_durations: list[float] = []

        for case_index, (args, kwargs) in enumerate(test_cases):
            case_name = f"case_{case_index}"

            # Warmup phase
            for _ in range(warmup_iterations):
                with suppress(Exception):
                    await func(*args, **kwargs)

            # Benchmark phase
            case_durations, successful_runs = await self._run_benchmark_iterations(
                func, args, kwargs, iterations, case_name
            )
            all_durations.extend(case_durations)

            # Calculate and store case statistics
            case_stats = self._calculate_benchmark_stats(
                case_name, args, kwargs, iterations, successful_runs, case_durations
            )
            results["test_cases"].append(case_stats)

        # Calculate overall summary
        results["summary"] = self._calculate_overall_summary(all_durations, len(test_cases))

        logger.info(
            "benchmark_completed",
            function=func.__name__,
            total_duration=sum(all_durations),
            mean_duration_ms=statistics.mean(all_durations) * 1000 if all_durations else 0,
        )

        return results

    async def _run_benchmark_iterations(
        self, func: Callable, args: tuple, kwargs: dict, iterations: int, case_name: str
    ) -> tuple[list[float], int]:
        """Run benchmark iterations for a single test case.

        Args:
            func: Function to benchmark
            args: Function arguments
            kwargs: Function keyword arguments
            iterations: Number of iterations
            case_name: Name of the test case for logging

        Returns:
            Tuple of (durations list, successful run count)
        """
        durations: list[float] = []
        successful_runs = 0

        for iteration in range(iterations):
            start_time = time.perf_counter()

            try:
                await func(*args, **kwargs)
                successful_runs += 1
            except Exception as e:
                logger.debug(
                    "benchmark_iteration_failed",
                    case=case_name,
                    iteration=iteration,
                    error=str(e),
                )

            duration = time.perf_counter() - start_time
            durations.append(duration)

        return durations, successful_runs

    async def compare_functions(
        self, functions: list[Callable], test_cases: list[tuple], iterations: int = 50
    ) -> dict[str, Any]:
        """Compare performance of multiple async functions.

        Args:
            functions: List of async functions to compare
            test_cases: List of (args, kwargs) tuples for test cases
            iterations: Number of iterations per function

        Returns:
            Comparison results
        """
        logger.info(
            "function_comparison_starting",
            functions=[f.__name__ for f in functions],
            test_cases=len(test_cases),
        )

        results = {"functions": [], "comparison": {}}

        # Benchmark each function
        for func in functions:
            func_results = await self.benchmark_function(func, test_cases, iterations)
            results["functions"].append(func_results)

        # Generate comparison
        if len(functions) > 1:
            function_names = [f.__name__ for f in functions]
            mean_durations = [
                func_result["summary"]["overall_mean_duration_ms"]
                for func_result in results["functions"]
            ]

            fastest_index = mean_durations.index(min(mean_durations))
            slowest_index = mean_durations.index(max(mean_durations))

            results["comparison"] = {
                "fastest_function": function_names[fastest_index],
                "slowest_function": function_names[slowest_index],
                "speed_improvement_factor": mean_durations[slowest_index]
                / mean_durations[fastest_index],
                "relative_performance": [
                    {
                        "function": name,
                        "relative_speed": min(mean_durations) / duration,
                        "slowdown_factor": duration / min(mean_durations),
                    }
                    for name, duration in zip(
                        function_names, mean_durations, strict=False
                    )
                ],
            }

        return results

    async def _run_stress_phase(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        concurrency: int,
        duration_seconds: float,
    ) -> dict[str, Any]:
        """Execute a single stress test phase at a specific concurrency level.

        Args:
            func: Async function to stress test
            args: Function arguments
            kwargs: Function keyword arguments
            concurrency: Number of concurrent calls to maintain
            duration_seconds: Duration of the stress test phase

        Returns:
            Phase statistics dictionary
        """

        async def _stress_worker(
            counters: dict[str, int],
            durations_list: list[float],
        ) -> None:
            """Execute a single stress test iteration."""
            start_time = time.perf_counter()
            try:
                await func(*args, **kwargs)
                counters["successful"] += 1
            except Exception:
                counters["errors"] += 1

            duration = time.perf_counter() - start_time
            durations_list.append(duration)
            counters["completed"] += 1

        phase_start = time.perf_counter()
        counters: dict[str, int] = {"completed": 0, "successful": 0, "errors": 0}
        durations: list[float] = []

        logger.info("stress_phase_starting", concurrency=concurrency)

        # Create and manage concurrent workers
        tasks: list[asyncio.Task] = []
        end_time = time.perf_counter() + duration_seconds

        while time.perf_counter() < end_time:
            # Maintain target concurrency
            while len(tasks) < concurrency and time.perf_counter() < end_time:
                task = asyncio.create_task(_stress_worker(counters, durations))
                tasks.append(task)

            # Clean up completed tasks
            tasks = [task for task in tasks if not task.done()]

            # Small delay to prevent busy waiting
            await asyncio.sleep(0.01)

        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        phase_duration = time.perf_counter() - phase_start
        return self._calculate_phase_stats(concurrency, phase_duration, counters, durations)

    def _calculate_phase_stats(
        self,
        concurrency: int,
        phase_duration: float,
        counters: dict[str, int],
        durations: list[float],
    ) -> dict[str, Any]:
        """Calculate statistics for a stress test phase.

        Args:
            concurrency: Concurrency level of the phase
            phase_duration: Total duration of the phase in seconds
            counters: Dictionary with completed, successful, error counts
            durations: List of individual call durations

        Returns:
            Phase statistics dictionary
        """
        completed_calls = counters["completed"]
        successful_calls = counters["successful"]
        error_count = counters["errors"]

        return {
            "concurrency_level": concurrency,
            "phase_duration_seconds": phase_duration,
            "completed_calls": completed_calls,
            "successful_calls": successful_calls,
            "error_count": error_count,
            "success_rate_percent": (successful_calls / completed_calls * 100)
            if completed_calls > 0
            else 0,
            "calls_per_second": completed_calls / phase_duration,
            "successful_calls_per_second": successful_calls / phase_duration,
            "mean_duration_ms": statistics.mean(durations) * 1000 if durations else 0,
            "median_duration_ms": statistics.median(durations) * 1000 if durations else 0,
            "max_duration_ms": max(durations) * 1000 if durations else 0,
            "percentile_95_ms": statistics.quantiles(durations, n=20)[18] * 1000
            if len(durations) > 5
            else 0,
        }

    def _generate_stress_recommendations(
        self, stress_phases: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate recommendations from stress test results.

        Args:
            stress_phases: List of stress test phase statistics

        Returns:
            Recommendations dictionary
        """
        if not stress_phases:
            return {}

        best_phase = max(stress_phases, key=lambda x: x["successful_calls_per_second"])

        return {
            "optimal_concurrency": best_phase["concurrency_level"],
            "max_throughput_calls_per_sec": best_phase["successful_calls_per_second"],
            "performance_degradation_threshold": self._find_degradation_threshold(
                stress_phases
            ),
        }

    async def stress_test(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        concurrent_calls: list[int] | None = None,
        duration_seconds: float = 10.0,
    ) -> dict[str, Any]:
        """Perform stress testing with varying concurrency levels.

        Args:
            func: Async function to stress test
            args: Function arguments
            kwargs: Function keyword arguments
            concurrent_calls: List of concurrency levels to test
            duration_seconds: Duration of each stress test phase

        Returns:
            Stress test results
        """
        if concurrent_calls is None:
            concurrent_calls = [1, 5, 10, 20, 50]

        logger.info(
            "stress_test_starting",
            function=func.__name__,
            concurrency_levels=concurrent_calls,
            duration_seconds=duration_seconds,
        )

        results: dict[str, Any] = {
            "function_name": func.__name__,
            "stress_phases": [],
            "recommendations": {},
        }

        # Run each stress phase
        for concurrency in concurrent_calls:
            phase_stats = await self._run_stress_phase(
                func, args, kwargs, concurrency, duration_seconds
            )
            results["stress_phases"].append(phase_stats)

        # Generate recommendations
        results["recommendations"] = self._generate_stress_recommendations(
            results["stress_phases"]
        )

        logger.info("stress_test_completed", total_phases=len(results["stress_phases"]))

        return results

    def _find_degradation_threshold(self, phases: list[dict[str, Any]]) -> int | None:
        """Find the concurrency level where performance starts degrading.

        Args:
            phases: List of stress test phase results

        Returns:
            Concurrency level where degradation begins
        """
        if len(phases) < 2:
            return None

        # Look for the first phase where throughput decreases significantly
        for i in range(1, len(phases)):
            current_throughput = phases[i]["successful_calls_per_second"]
            previous_throughput = phases[i - 1]["successful_calls_per_second"]

            # If throughput drops by more than 10%
            if current_throughput < previous_throughput * 0.9:
                return phases[i]["concurrency_level"]

        return None
