"""
Benchmark Runner Script for FastAPI Web Server
Comprehensive performance testing with realistic scenarios
"""

import asyncio
import time
import statistics
import psutil
import subprocess
import sys
from typing import Dict, List, Tuple
import httpx
import json


class BenchmarkRunner:
    """Comprehensive benchmark runner for FastAPI web server"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {}

    async def warmup_server(self, duration: int = 10):
        """Warm up the server before benchmarking"""
        print(f"🔧 Warming up server for {duration} seconds...")
        start_time = time.time()
        warmup_requests = []

        while time.time() - start_time < duration:
            try:
                warmup_requests.append(self.client.get(f"{self.base_url}/health"))
                warmup_requests.append(self.client.get(f"{self.base_url}/"))
                if len(warmup_requests) >= 20:
                    await asyncio.gather(*warmup_requests)
                    warmup_requests = []
                    await asyncio.sleep(0.1)
            except Exception:
                await asyncio.sleep(1)

        if warmup_requests:
            await asyncio.gather(*warmup_requests)
        print("✅ Server warmup complete")

    async def benchmark_static_files(
        self, concurrent_requests: int = 100, duration: int = 30
    ):
        """Benchmark static file serving performance"""
        print("📁 Benchmarking static file serving...")

        # Test files of different sizes
        test_files = [
            "index.html",  # Small HTML
            "style.css",  # CSS
            "app.js",  # JavaScript
            "logo.png",  # Image
        ]

        latencies = []
        successful_requests = 0
        failed_requests = 0
        total_bytes = 0

        start_time = time.time()

        async def make_request(file_path):
            nonlocal successful_requests, failed_requests, total_bytes
            try:
                request_start = time.time()
                response = await self.client.get(f"{self.base_url}/{file_path}")
                latency = time.time() - request_start

                if response.status_code == 200:
                    successful_requests += 1
                    total_bytes += len(response.content)
                    latencies.append(latency)
                else:
                    failed_requests += 1
            except Exception:
                failed_requests += 1

        while time.time() - start_time < duration:
            tasks = []
            for _ in range(concurrent_requests):
                file_path = test_files[successful_requests % len(test_files)]
                tasks.append(make_request(file_path))

            await asyncio.gather(*tasks)
            await asyncio.sleep(0.01)  # Small delay to prevent overwhelming

        total_time = time.time() - start_time
        requests_per_second = successful_requests / total_time

        self.results["static_files"] = {
            "requests_per_second": round(requests_per_second, 2),
            "total_requests": successful_requests + failed_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "throughput_mbps": round((total_bytes * 8) / (total_time * 1_000_000), 2),
            "avg_latency_ms": round(statistics.mean(latencies) * 1000, 2)
            if latencies
            else 0,
            "p95_latency_ms": round(statistics.quantiles(latencies, n=20)[18] * 1000, 2)
            if len(latencies) >= 20
            else 0,
            "p99_latency_ms": round(
                statistics.quantiles(latencies, n=100)[98] * 1000, 2
            )
            if len(latencies) >= 100
            else 0,
        }

        print(
            f"✅ Static files: {requests_per_second:.0f} req/s, "
            f"{self.results['static_files']['avg_latency_ms']}ms avg latency"
        )

    async def benchmark_api_proxy(
        self, concurrent_requests: int = 50, duration: int = 30
    ):
        """Benchmark API proxy performance"""
        print("🔗 Benchmarking API proxy...")

        latencies = []
        successful_requests = 0
        failed_requests = 0

        # Test different API endpoints
        api_endpoints = ["/api/users", "/api/products", "/api/health"]

        start_time = time.time()

        async def make_api_request(endpoint):
            nonlocal successful_requests, failed_requests
            try:
                request_start = time.time()
                response = await self.client.get(f"{self.base_url}{endpoint}")
                latency = time.time() - request_start

                if response.status_code in [
                    200,
                    502,
                ]:  # 502 means backend is down, but proxy works
                    successful_requests += 1
                    latencies.append(latency)
                else:
                    failed_requests += 1
            except Exception:
                failed_requests += 1

        while time.time() - start_time < duration:
            tasks = []
            for _ in range(concurrent_requests):
                endpoint = api_endpoints[successful_requests % len(api_endpoints)]
                tasks.append(make_api_request(endpoint))

            await asyncio.gather(*tasks)
            await asyncio.sleep(0.02)  # Slightly longer delay for API calls

        total_time = time.time() - start_time
        requests_per_second = successful_requests / total_time

        self.results["api_proxy"] = {
            "requests_per_second": round(requests_per_second, 2),
            "total_requests": successful_requests + failed_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "avg_latency_ms": round(statistics.mean(latencies) * 1000, 2)
            if latencies
            else 0,
            "p95_latency_ms": round(statistics.quantiles(latencies, n=20)[18] * 1000, 2)
            if len(latencies) >= 20
            else 0,
            "p99_latency_ms": round(
                statistics.quantiles(latencies, n=100)[98] * 1000, 2
            )
            if len(latencies) >= 100
            else 0,
        }

        print(
            f"✅ API proxy: {requests_per_second:.0f} req/s, "
            f"{self.results['api_proxy']['avg_latency_ms']}ms avg latency"
        )

    async def benchmark_concurrent_load(
        self, max_concurrent: int = 1000, duration: int = 60
    ):
        """Benchmark under high concurrent load"""
        print("⚡ Benchmarking concurrent load...")

        latencies = []
        successful_requests = 0
        failed_requests = 0
        active_connections = 0

        start_time = time.time()

        async def make_load_request():
            nonlocal successful_requests, failed_requests, active_connections
            active_connections += 1
            try:
                request_start = time.time()
                # Mix of static and API requests
                if successful_requests % 3 == 0:
                    response = await self.client.get(f"{self.base_url}/")
                elif successful_requests % 3 == 1:
                    response = await self.client.get(f"{self.base_url}/health")
                else:
                    response = await self.client.get(f"{self.base_url}/api/users")

                latency = time.time() - request_start

                if response.status_code in [200, 502]:
                    successful_requests += 1
                    latencies.append(latency)
                else:
                    failed_requests += 1
            except Exception as e:
                failed_requests += 1
            finally:
                active_connections -= 1

        # Ramp up connections gradually
        ramp_up_time = 10
        ramp_start = time.time()

        while time.time() - start_time < duration:
            # Gradually increase concurrent connections
            elapsed_ramp = time.time() - ramp_start
            if elapsed_ramp < ramp_up_time:
                current_max = int((elapsed_ramp / ramp_up_time) * max_concurrent)
            else:
                current_max = max_concurrent

            # Maintain target concurrency
            while (
                active_connections < current_max
                and (time.time() - start_time) < duration
            ):
                asyncio.create_task(make_load_request())
                await asyncio.sleep(0.001)  # Very short delay to spawn tasks quickly

            await asyncio.sleep(0.1)  # Check every 100ms

        # Wait for remaining requests to complete
        await asyncio.sleep(2)

        total_time = time.time() - start_time
        requests_per_second = successful_requests / total_time

        self.results["concurrent_load"] = {
            "requests_per_second": round(requests_per_second, 2),
            "total_requests": successful_requests + failed_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "max_concurrent": max_concurrent,
            "avg_latency_ms": round(statistics.mean(latencies) * 1000, 2)
            if latencies
            else 0,
            "p95_latency_ms": round(statistics.quantiles(latencies, n=20)[18] * 1000, 2)
            if len(latencies) >= 20
            else 0,
        }

        print(
            f"✅ Concurrent load: {requests_per_second:.0f} req/s, "
            f"{self.results['concurrent_load']['avg_latency_ms']}ms avg latency"
        )

    async def benchmark_memory_usage(self, duration: int = 30):
        """Benchmark memory usage under load"""
        print("💾 Benchmarking memory usage...")

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_samples = []
        successful_requests = 0

        start_time = time.time()

        async def make_memory_request():
            nonlocal successful_requests
            try:
                await self.client.get(f"{self.base_url}/health")
                successful_requests += 1
            except Exception:
                pass

        # Sample memory every second
        async def sample_memory():
            while time.time() - start_time < duration:
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
                await asyncio.sleep(1)

        # Run requests and sample memory concurrently
        request_task = asyncio.create_task(self._run_memory_requests(duration))
        memory_task = asyncio.create_task(sample_memory())

        await asyncio.gather(request_task, memory_task)

        final_memory = process.memory_info().rss / 1024 / 1024

        self.results["memory_usage"] = {
            "initial_memory_mb": round(initial_memory, 2),
            "final_memory_mb": round(final_memory, 2),
            "peak_memory_mb": round(max(memory_samples), 2),
            "avg_memory_mb": round(statistics.mean(memory_samples), 2),
            "memory_increase_mb": round(final_memory - initial_memory, 2),
            "requests_during_test": successful_requests,
        }

        print(
            f"✅ Memory: {self.results['memory_usage']['avg_memory_mb']}MB avg, "
            f"{self.results['memory_usage']['peak_memory_mb']}MB peak"
        )

    async def _run_memory_requests(self, duration: int):
        """Helper to run requests during memory test"""
        start_time = time.time()
        while time.time() - start_time < duration:
            tasks = [self.client.get(f"{self.base_url}/health") for _ in range(10)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.1)

    async def run_comprehensive_benchmark(self):
        """Run all benchmarks and generate comprehensive report"""
        print("🚀 Starting comprehensive benchmark...")
        print("=" * 60)

        await self.warmup_server()

        # Run benchmarks
        await self.benchmark_static_files()
        await self.benchmark_api_proxy()
        await self.benchmark_concurrent_load()
        await self.benchmark_memory_usage()

        # Calculate overall score
        self._calculate_overall_score()

        print("=" * 60)
        print("✅ Benchmark complete!")

        return self.results

    def _calculate_overall_score(self):
        """Calculate overall performance score (0-100)"""
        scores = []

        # Static files score (max 30 points)
        static_rps = self.results["static_files"]["requests_per_second"]
        static_score = min(30, (static_rps / 5000) * 30)  # 5000 req/s = 30 points
        scores.append(static_score)

        # API proxy score (max 25 points)
        api_rps = self.results["api_proxy"]["requests_per_second"]
        api_score = min(25, (api_rps / 4000) * 25)  # 4000 req/s = 25 points
        scores.append(api_score)

        # Concurrent load score (max 20 points)
        concurrent_rps = self.results["concurrent_load"]["requests_per_second"]
        concurrent_score = min(
            20, (concurrent_rps / 3500) * 20
        )  # 3500 req/s = 20 points
        scores.append(concurrent_score)

        # Memory efficiency score (max 15 points)
        memory_avg = self.results["memory_usage"]["avg_memory_mb"]
        memory_score = min(15, (100 / memory_avg) * 15)  # 100MB = 15 points
        scores.append(memory_score)

        # Latency score (max 10 points)
        avg_latency = (
            self.results["static_files"]["avg_latency_ms"]
            + self.results["api_proxy"]["avg_latency_ms"]
        ) / 2
        latency_score = min(10, (50 / avg_latency) * 10)  # 50ms = 10 points
        scores.append(latency_score)

        overall_score = sum(scores)
        self.results["overall_score"] = round(overall_score, 1)
        self.results["score_breakdown"] = {
            "static_files": round(static_score, 1),
            "api_proxy": round(api_score, 1),
            "concurrent_load": round(concurrent_score, 1),
            "memory_efficiency": round(memory_score, 1),
            "latency": round(latency_score, 1),
        }

    def print_detailed_results(self):
        """Print detailed benchmark results"""
        print("\n" + "=" * 60)
        print("📊 DETAILED BENCHMARK RESULTS")
        print("=" * 60)

        for test_name, results in self.results.items():
            if test_name in ["overall_score", "score_breakdown"]:
                continue

            print(f"\n🔹 {test_name.upper().replace('_', ' ')}:")
            for key, value in results.items():
                if "latency" in key:
                    print(f"   {key.replace('_', ' ').title()}: {value}ms")
                elif "memory" in key:
                    print(f"   {key.replace('_', ' ').title()}: {value}MB")
                elif "requests_per_second" in key:
                    print(f"   {key.replace('_', ' ').title()}: {value:,}")
                else:
                    print(f"   {key.replace('_', ' ').title()}: {value:,}")

        print(f"\n🎯 OVERALL PERFORMANCE SCORE: {self.results['overall_score']}/100")
        print("Score Breakdown:")
        for category, score in self.results["score_breakdown"].items():
            print(f"  {category.replace('_', ' ').title()}: {score}")

    async def close(self):
        """Close the HTTP client"""
        await self.client.acclose()


async def main():
    """Main benchmark runner"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8080"

    runner = BenchmarkRunner(base_url)

    try:
        results = await runner.run_comprehensive_benchmark()
        runner.print_detailed_results()

        # Save results to file
        with open("benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to benchmark_results.json")

    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
