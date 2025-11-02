"""
Performance Benchmark Tests
Тесты производительности

This module provides comprehensive performance testing for the FastAPI server
including static file serving, API proxying, and concurrent load testing.
"""

import asyncio
import time
import statistics
import httpx
import json
from typing import Dict, List, Any
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """
    Performance benchmarking tool for FastAPI server
    Инструмент бенчмаркинга производительности для сервера FastAPI
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {}

    async def benchmark_static_files(
        self, concurrent_requests: int = 10
    ) -> Dict[str, Any]:
        """
        Benchmark static file serving performance
        Тестирование производительности обслуживания статических файлов
        """
        test_files = [
            "/static/css/corporate.css",
            "/static/js/app.js",
            "/static/images/logo.png",
            "/static/favicon.ico",
            "/",
        ]

        results = []

        for file_path in test_files:
            logger.info(f"Benchmarking static file: {file_path}")

            # Single request timing
            start_time = time.time()
            try:
                response = await self.client.get(f"{self.base_url}{file_path}")
                single_time = time.time() - start_time
                single_success = response.status_code == 200
            except Exception as e:
                single_time = float("inf")
                single_success = False
                logger.error(f"Error benchmarking {file_path}: {e}")

            # Concurrent requests timing
            concurrent_times = []
            concurrent_successes = 0

            async def make_request():
                try:
                    req_start = time.time()
                    resp = await self.client.get(f"{self.base_url}{file_path}")
                    req_time = time.time() - req_start
                    if resp.status_code == 200:
                        return req_time, True
                    return req_time, False
                except Exception:
                    return float("inf"), False

            tasks = [make_request() for _ in range(concurrent_requests)]
            concurrent_results = await asyncio.gather(*tasks)

            for req_time, success in concurrent_results:
                concurrent_times.append(req_time)
                if success:
                    concurrent_successes += 1

            result = {
                "file": file_path,
                "single_request": {
                    "time_ms": round(single_time * 1000, 2),
                    "success": single_success,
                },
                "concurrent_requests": {
                    "count": concurrent_requests,
                    "avg_time_ms": round(statistics.mean(concurrent_times) * 1000, 2),
                    "min_time_ms": round(min(concurrent_times) * 1000, 2),
                    "max_time_ms": round(max(concurrent_times) * 1000, 2),
                    "success_rate": round(
                        concurrent_successes / concurrent_requests * 100, 1
                    ),
                },
            }
            results.append(result)

        return {
            "static_files": results,
            "summary": {
                "total_files": len(results),
                "avg_single_time_ms": round(
                    statistics.mean([r["single_request"]["time_ms"] for r in results]),
                    2,
                ),
                "avg_concurrent_time_ms": round(
                    statistics.mean(
                        [r["concurrent_requests"]["avg_time_ms"] for r in results]
                    ),
                    2,
                ),
            },
        }

    async def benchmark_api_proxy(
        self, target_endpoints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Benchmark API proxy performance
        Тестирование производительности прокси API
        """
        if target_endpoints is None:
            target_endpoints = [
                "/api/health",
                "/api/users",
                "/api/products",
                "/api/orders",
            ]

        results = []

        for endpoint in target_endpoints:
            logger.info(f"Benchmarking API proxy: {endpoint}")

            # Test both GET and POST requests
            for method in ["GET", "POST"]:
                times = []
                successes = 0

                async def test_request():
                    try:
                        start = time.time()
                        if method == "GET":
                            response = await self.client.get(
                                f"{self.base_url}{endpoint}"
                            )
                        else:
                            response = await self.client.post(
                                f"{self.base_url}{endpoint}", json={"test": "data"}
                            )
                        req_time = time.time() - start
                        success = response.status_code in [
                            200,
                            201,
                            404,
                        ]  # 404 is expected for non-existent endpoints
                        return req_time, success
                    except Exception:
                        return float("inf"), False

                # Run 10 requests for each endpoint/method
                tasks = [test_request() for _ in range(10)]
                request_results = await asyncio.gather(*tasks)

                for req_time, success in request_results:
                    times.append(req_time)
                    if success:
                        successes += 1

                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "avg_time_ms": round(statistics.mean(times) * 1000, 2),
                    "min_time_ms": round(min(times) * 1000, 2),
                    "max_time_ms": round(max(times) * 1000, 2),
                    "success_rate": round(successes / len(times) * 100, 1),
                    "requests_per_second": round(
                        1 / statistics.mean(times) if statistics.mean(times) > 0 else 0,
                        1,
                    ),
                }
                results.append(result)

        return {
            "api_proxy": results,
            "summary": {
                "total_endpoints": len(target_endpoints),
                "avg_response_time_ms": round(
                    statistics.mean([r["avg_time_ms"] for r in results]), 2
                ),
                "avg_requests_per_second": round(
                    statistics.mean([r["requests_per_second"] for r in results]), 1
                ),
            },
        }

    async def benchmark_concurrent_load(
        self, total_requests: int = 1000, concurrent_clients: int = 100
    ) -> Dict[str, Any]:
        """
        Benchmark concurrent load handling
        Тестирование обработки конкурентной нагрузки
        """
        logger.info(
            f"Starting concurrent load test: {total_requests} requests with {concurrent_clients} clients"
        )

        request_types = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/api/health", "GET"),
            ("/static/css/corporate.css", "GET"),
        ]

        semaphore = asyncio.Semaphore(concurrent_clients)
        results = []
        completed = 0

        async def make_load_request():
            nonlocal completed
            async with semaphore:
                import random

                path, method = random.choice(request_types)

                start_time = time.time()
                try:
                    if method == "GET":
                        response = await self.client.get(f"{self.base_url}{path}")
                    else:
                        response = await self.client.post(f"{self.base_url}{path}")

                    response_time = time.time() - start_time
                    success = response.status_code in [200, 201, 404]

                    result = {
                        "path": path,
                        "method": method,
                        "time_ms": round(response_time * 1000, 2),
                        "success": success,
                        "status_code": response.status_code,
                    }
                    results.append(result)

                except Exception as e:
                    result = {
                        "path": path,
                        "method": method,
                        "time_ms": float("inf"),
                        "success": False,
                        "error": str(e),
                    }
                    results.append(result)

                completed += 1
                if completed % 100 == 0:
                    logger.info(
                        f"Progress: {completed}/{total_requests} requests completed"
                    )

        # Create and run all requests
        tasks = [make_load_request() for _ in range(total_requests)]
        start_time = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Calculate statistics
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        response_times = [r["time_ms"] for r in successful_requests]

        return {
            "concurrent_load": {
                "total_requests": total_requests,
                "concurrent_clients": concurrent_clients,
                "total_time_seconds": round(total_time, 2),
                "requests_per_second": round(total_requests / total_time, 1),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "success_rate": round(
                    len(successful_requests) / total_requests * 100, 1
                ),
                "avg_response_time_ms": round(statistics.mean(response_times), 2)
                if response_times
                else 0,
                "p95_response_time_ms": round(
                    statistics.quantiles(response_times, n=20)[18], 2
                )
                if len(response_times) >= 20
                else 0,
                "p99_response_time_ms": round(
                    statistics.quantiles(response_times, n=100)[98], 2
                )
                if len(response_times) >= 100
                else 0,
            }
        }

    async def benchmark_memory_usage(self, duration: int = 60) -> Dict[str, Any]:
        """
        Benchmark memory usage over time
        Тестирование использования памяти с течением времени
        """
        logger.info(f"Starting memory usage benchmark for {duration} seconds")

        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_samples = []
        start_time = time.time()

        # Monitor memory while making continuous requests
        async def monitor_memory():
            while time.time() - start_time < duration:
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
                await asyncio.sleep(1)

        # Make continuous requests during monitoring
        async def make_requests():
            while time.time() - start_time < duration:
                try:
                    await self.client.get(f"{self.base_url}/health")
                    await asyncio.sleep(0.1)  # 10 requests per second
                except Exception:
                    await asyncio.sleep(1)

        await asyncio.gather(monitor_memory(), make_requests())

        return {
            "memory_usage": {
                "duration_seconds": duration,
                "avg_memory_mb": round(statistics.mean(memory_samples), 2),
                "max_memory_mb": round(max(memory_samples), 2),
                "min_memory_mb": round(min(memory_samples), 2),
                "memory_samples": len(memory_samples),
            }
        }

    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """
        Run comprehensive performance benchmark
        Запуск комплексного теста производительности
        """
        logger.info("🚀 Starting comprehensive performance benchmark")

        start_time = time.time()

        # Run all benchmark tests
        static_results = await self.benchmark_static_files()
        api_results = await self.benchmark_api_proxy()
        load_results = await self.benchmark_concurrent_load()
        memory_results = await self.benchmark_memory_usage()

        total_time = time.time() - start_time

        # Generate overall score (0-100)
        scores = []

        # Static files score
        static_score = min(
            100, 5000 / static_results["summary"]["avg_concurrent_time_ms"] * 100
        )
        scores.append(static_score)

        # API proxy score
        api_score = min(100, api_results["summary"]["avg_requests_per_second"] * 10)
        scores.append(api_score)

        # Load test score
        load_score = min(
            100, load_results["concurrent_load"]["requests_per_second"] * 2
        )
        scores.append(load_score)

        # Memory efficiency score
        memory_score = max(
            0, 100 - (memory_results["memory_usage"]["avg_memory_mb"] / 10)
        )
        scores.append(memory_score)

        overall_score = round(statistics.mean(scores), 1)

        return {
            "overall_score": overall_score,
            "benchmark_duration_seconds": round(total_time, 2),
            "static_files": static_results,
            "api_proxy": api_results,
            "concurrent_load": load_results,
            "memory_usage": memory_results,
            "timestamp": time.time(),
            "server_info": {
                "base_url": self.base_url,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            },
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


def print_benchmark_results(results: Dict[str, Any]):
    """
    Print benchmark results in a readable format
    Вывод результатов бенчмарка в читаемом формате
    """
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE BENCHMARK RESULTS / РЕЗУЛЬТАТЫ ТЕСТА ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 80)

    print(f"\n🏆 Overall Score: {results['overall_score']}/100")
    print(f"⏱️  Benchmark Duration: {results['benchmark_duration_seconds']}s")

    # Static files results
    static = results["static_files"]
    print(f"\n📁 Static Files ({static['summary']['total_files']} files):")
    print(f"   Average Response Time: {static['summary']['avg_concurrent_time_ms']}ms")

    # API proxy results
    api = results["api_proxy"]
    print(f"\n🔗 API Proxy ({api['summary']['total_endpoints']} endpoints):")
    print(f"   Average Response Time: {api['summary']['avg_response_time_ms']}ms")
    print(f"   Requests per Second: {api['summary']['avg_requests_per_second']}")

    # Load test results
    load = results["concurrent_load"]
    print(f"\n⚡ Concurrent Load ({load['total_requests']} requests):")
    print(f"   Requests per Second: {load['requests_per_second']}")
    print(f"   Success Rate: {load['success_rate']}%")
    print(f"   Average Response Time: {load['avg_response_time_ms']}ms")
    print(f"   P95 Response Time: {load['p95_response_time_ms']}ms")

    # Memory usage
    memory = results["memory_usage"]
    print(f"\n💾 Memory Usage ({memory['duration_seconds']}s):")
    print(f"   Average Memory: {memory['avg_memory_mb']}MB")
    print(f"   Peak Memory: {memory['max_memory_mb']}MB")


async def main():
    """
    Main benchmark function
    Главная функция бенчмарка
    """
    benchmark = PerformanceBenchmark()

    try:
        results = await benchmark.run_comprehensive_benchmark()
        print_benchmark_results(results)

        # Save results to file
        output_file = "benchmark_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Detailed results saved to: {output_file}")

        # Performance assessment
        score = results["overall_score"]
        if score >= 80:
            print("\n🎉 EXCELLENT PERFORMANCE - Ready for production!")
        elif score >= 60:
            print("\n✅ GOOD PERFORMANCE - Suitable for production")
        elif score >= 40:
            print("\n⚠️  MODERATE PERFORMANCE - Needs optimization")
        else:
            print("\n🚨 POOR PERFORMANCE - Significant optimization required")

    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        print(f"❌ Benchmark failed: {e}")

    finally:
        await benchmark.close()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
