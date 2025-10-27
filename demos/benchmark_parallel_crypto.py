"""
Benchmark script for ParallelCryptoEngine.

Compares performance between sequential and parallel encryption/decryption.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

import structlog

from textkit.config_manager import ConfigurationManager
from textkit.crypto_engine import CryptographyManager, ParallelCryptoEngine

logger = structlog.get_logger(__name__)


def format_time(seconds: float) -> str:
    """Format time in appropriate unit."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    else:
        return f"{seconds:.2f}s"


def benchmark_sequential(crypto_manager: CryptographyManager, texts: list[str]) -> float:
    """Benchmark sequential encryption/decryption."""
    start = time.perf_counter()

    encrypted = [crypto_manager.encrypt_text(text) for text in texts]
    decrypted = [crypto_manager.decrypt_text(enc) for enc in encrypted]

    elapsed = time.perf_counter() - start
    assert decrypted == texts  # Verify correctness
    return elapsed


async def benchmark_parallel(
    parallel_engine: ParallelCryptoEngine, texts: list[str]
) -> float:
    """Benchmark parallel encryption/decryption."""
    start = time.perf_counter()

    encrypted = await parallel_engine.encrypt_batch_async(texts)
    decrypted = await parallel_engine.decrypt_batch_async(encrypted)

    elapsed = time.perf_counter() - start
    assert decrypted == texts  # Verify correctness
    return elapsed


async def run_benchmarks():
    """Run comprehensive benchmarks."""
    print("\n" + "=" * 80)
    print("ParallelCryptoEngine Performance Benchmark")
    print("=" * 80 + "\n")

    # Setup
    config_dir = Path(__file__).parent.parent / "test_config_benchmark"
    config_dir.mkdir(exist_ok=True)

    config = ConfigurationManager(config_dir)
    crypto_manager = CryptographyManager(config)
    crypto_manager.ensure_key_pair()

    test_cases = [
        ("Small texts (10 items, 50 chars)", 10, 50),
        ("Medium texts (50 items, 200 chars)", 50, 200),
        ("Large texts (100 items, 1000 chars)", 100, 1000),
        ("Very large batch (200 items, 500 chars)", 200, 500),
    ]

    results = []

    for description, count, text_size in test_cases:
        print(f"\n{description}")
        print("-" * 60)

        # Generate test texts
        texts = [f"Test text {i:04d} " + "x" * (text_size - 20) for i in range(count)]

        # Benchmark sequential
        seq_time = benchmark_sequential(crypto_manager, texts)

        # Benchmark parallel with different worker counts
        parallel_times = {}
        for workers in [2, 4, 8]:
            parallel_engine = ParallelCryptoEngine(crypto_manager, max_workers=workers)
            par_time = await benchmark_parallel(parallel_engine, texts)
            parallel_times[workers] = par_time

        # Calculate speedups
        print(f"  Sequential:           {format_time(seq_time)}")
        for workers, par_time in parallel_times.items():
            speedup = seq_time / par_time
            print(
                f"  Parallel ({workers} workers):   {format_time(par_time)} "
                f"(speedup: {speedup:.2f}x)"
            )

        best_time = min(parallel_times.values())
        best_speedup = seq_time / best_time
        results.append(
            {
                "description": description,
                "count": count,
                "seq_time": seq_time,
                "best_par_time": best_time,
                "speedup": best_speedup,
            }
        )

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80 + "\n")

    total_seq = sum(r["seq_time"] for r in results)
    total_par = sum(r["best_par_time"] for r in results)
    overall_speedup = total_seq / total_par

    print(f"Total sequential time:  {format_time(total_seq)}")
    print(f"Total parallel time:    {format_time(total_par)}")
    print(f"Overall speedup:        {overall_speedup:.2f}x")
    print(f"\nAverage speedup:        {sum(r['speedup'] for r in results) / len(results):.2f}x")

    # Cleanup
    import shutil

    shutil.rmtree(config_dir, ignore_errors=True)

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_benchmarks())
