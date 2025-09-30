"""
Performance monitoring mixin for transformers.

Provides standardized performance monitoring patterns that can be mixed
into transformer classes for consistent performance tracking.
"""

import time
import functools
from typing import Any, Callable, Dict, Optional, List, TypeVar
from collections import defaultdict, deque

T = TypeVar('T')


class PerformanceMixin:
    """Mixin providing performance monitoring for transformers.

    Provides methods for tracking execution times, memory usage,
    and performance statistics that can be used by transformer classes.
    """

    def __init__(self, *args, **kwargs):
        """Initialize performance monitoring."""
        super().__init__(*args, **kwargs)
        self._performance_stats = defaultdict(list)
        self._recent_operations = deque(maxlen=100)  # Keep last 100 operations
        self._operation_count = defaultdict(int)

    def track_performance(
        self,
        rule_name: str,
        elapsed_ms: float,
        input_length: int,
        output_length: int,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track performance metrics for a transformation.

        Args:
            rule_name: Name of the transformation rule
            elapsed_ms: Time elapsed in milliseconds
            input_length: Length of input text
            output_length: Length of output text
            context: Additional context for tracking
        """
        operation_data = {
            "rule_name": rule_name,
            "elapsed_ms": elapsed_ms,
            "input_length": input_length,
            "output_length": output_length,
            "timestamp": time.time(),
            "transformer": self.__class__.__name__,
            "throughput_chars_per_sec": (input_length / elapsed_ms * 1000) if elapsed_ms > 0 else 0,
            "compression_ratio": output_length / input_length if input_length > 0 else 1.0,
            **(context or {})
        }

        # Store in performance stats
        self._performance_stats[rule_name].append(operation_data)
        self._recent_operations.append(operation_data)
        self._operation_count[rule_name] += 1

        # Log performance warning if needed
        if hasattr(self, 'log_performance_warning'):
            self.log_performance_warning(rule_name, elapsed_ms)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics.

        Returns:
            Dictionary containing performance statistics
        """
        stats = {
            "transformer": self.__class__.__name__,
            "total_operations": sum(self._operation_count.values()),
            "rule_stats": {},
            "recent_operations": list(self._recent_operations)[-10:],  # Last 10 operations
            "averages": {}
        }

        # Calculate statistics per rule
        for rule_name, operations in self._performance_stats.items():
            if operations:
                elapsed_times = [op["elapsed_ms"] for op in operations]
                input_lengths = [op["input_length"] for op in operations]
                throughputs = [op["throughput_chars_per_sec"] for op in operations]

                rule_stats = {
                    "operation_count": len(operations),
                    "avg_elapsed_ms": sum(elapsed_times) / len(elapsed_times),
                    "min_elapsed_ms": min(elapsed_times),
                    "max_elapsed_ms": max(elapsed_times),
                    "avg_input_length": sum(input_lengths) / len(input_lengths),
                    "avg_throughput": sum(throughputs) / len(throughputs),
                    "total_characters_processed": sum(input_lengths)
                }

                stats["rule_stats"][rule_name] = rule_stats

        # Calculate overall averages
        if self._recent_operations:
            all_elapsed = [op["elapsed_ms"] for op in self._recent_operations]
            all_throughput = [op["throughput_chars_per_sec"] for op in self._recent_operations]

            stats["averages"] = {
                "avg_elapsed_ms": sum(all_elapsed) / len(all_elapsed),
                "avg_throughput": sum(all_throughput) / len(all_throughput),
                "operations_per_minute": self._calculate_operations_per_minute()
            }

        return stats

    def _calculate_operations_per_minute(self) -> float:
        """Calculate operations per minute based on recent activity.

        Returns:
            Operations per minute
        """
        if len(self._recent_operations) < 2:
            return 0.0

        # Get time span of recent operations
        recent_list = list(self._recent_operations)
        time_span = recent_list[-1]["timestamp"] - recent_list[0]["timestamp"]

        if time_span > 0:
            return len(recent_list) / time_span * 60
        return 0.0

    def get_slow_operations(self, threshold_ms: float = 1000.0) -> List[Dict[str, Any]]:
        """Get operations that exceeded the performance threshold.

        Args:
            threshold_ms: Threshold in milliseconds

        Returns:
            List of slow operations
        """
        slow_ops = []
        for operations in self._performance_stats.values():
            for op in operations:
                if op["elapsed_ms"] > threshold_ms:
                    slow_ops.append(op)

        # Sort by elapsed time (slowest first)
        return sorted(slow_ops, key=lambda x: x["elapsed_ms"], reverse=True)

    def reset_performance_stats(self) -> None:
        """Reset all performance statistics."""
        self._performance_stats.clear()
        self._recent_operations.clear()
        self._operation_count.clear()

    @staticmethod
    def performance_tracked(rule_name: Optional[str] = None):
        """Decorator for automatic performance tracking.

        Args:
            rule_name: Optional rule name for tracking

        Returns:
            Decorator function
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(self, text: str, *args, **kwargs) -> T:
                effective_rule_name = rule_name or func.__name__
                start_time = time.perf_counter()

                try:
                    result = func(self, text, *args, **kwargs)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000

                    # Track performance if the mixin is available
                    if hasattr(self, 'track_performance'):
                        self.track_performance(
                            effective_rule_name,
                            elapsed_ms,
                            len(text),
                            len(result) if isinstance(result, str) else 0,
                            {"function": func.__name__}
                        )

                    return result

                except Exception as e:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000

                    # Track failed operation
                    if hasattr(self, 'track_performance'):
                        self.track_performance(
                            effective_rule_name,
                            elapsed_ms,
                            len(text),
                            0,  # No output on failure
                            {"function": func.__name__, "error": str(e)}
                        )

                    raise

            return wrapper
        return decorator

    def benchmark_rule(
        self,
        rule_name: str,
        test_texts: List[str],
        iterations: int = 1
    ) -> Dict[str, Any]:
        """Benchmark a specific transformation rule.

        Args:
            rule_name: Name of the rule to benchmark
            test_texts: List of test texts to use
            iterations: Number of iterations per test text

        Returns:
            Benchmark results
        """
        if not hasattr(self, 'transform'):
            raise AttributeError("Transformer must have a 'transform' method for benchmarking")

        results = {
            "rule_name": rule_name,
            "test_count": len(test_texts),
            "iterations": iterations,
            "individual_results": [],
            "summary": {}
        }

        all_times = []

        for i, text in enumerate(test_texts):
            text_results = {
                "test_index": i,
                "input_length": len(text),
                "times_ms": [],
                "output_length": None,
                "error": None
            }

            for iteration in range(iterations):
                start_time = time.perf_counter()
                try:
                    result = self.transform(text, rule_name)
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    text_results["times_ms"].append(elapsed_ms)
                    all_times.append(elapsed_ms)

                    if text_results["output_length"] is None:
                        text_results["output_length"] = len(result) if isinstance(result, str) else 0

                except Exception as e:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    text_results["times_ms"].append(elapsed_ms)
                    text_results["error"] = str(e)
                    all_times.append(elapsed_ms)

            # Calculate statistics for this test text
            if text_results["times_ms"]:
                text_results["avg_ms"] = sum(text_results["times_ms"]) / len(text_results["times_ms"])
                text_results["min_ms"] = min(text_results["times_ms"])
                text_results["max_ms"] = max(text_results["times_ms"])

            results["individual_results"].append(text_results)

        # Calculate overall summary
        if all_times:
            results["summary"] = {
                "total_operations": len(all_times),
                "avg_time_ms": sum(all_times) / len(all_times),
                "min_time_ms": min(all_times),
                "max_time_ms": max(all_times),
                "total_time_ms": sum(all_times),
                "operations_per_second": len(all_times) / (sum(all_times) / 1000) if sum(all_times) > 0 else 0
            }

        return results
