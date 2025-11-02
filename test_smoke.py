"""
Smoke tests for FastAPI Security Proxy Server
Basic functionality tests for production readiness
"""

import pytest
import httpx
import asyncio
from pathlib import Path
import sys

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "app"))


@pytest.fixture
async def client():
    """Async HTTP client for testing"""
    async with httpx.AsyncClient(
        base_url="http://localhost:8080", timeout=10.0
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health endpoint returns 200"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "features" in data


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint returns server info"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "server" in data
    assert "version" in data
    assert "config" in data


@pytest.mark.asyncio
async def test_security_stats_endpoint(client):
    """Test security stats endpoint"""
    response = await client.get("/security/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "blocked_ips" in data
    assert "rate_limited_requests" in data


@pytest.mark.asyncio
async def test_monitoring_stats_endpoint(client):
    """Test monitoring stats endpoint"""
    response = await client.get("/monitoring/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_attacks" in data
    assert "recent_attacks" in data


@pytest.mark.asyncio
async def test_static_file_serving(client):
    """Test static file serving with ETag headers"""
    # Create a test file
    test_dir = Path("data/htdocs")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "test.html"
    test_file.write_text("<html><body>Test</body></html>")

    response = await client.get("/test.html")
    assert response.status_code == 200
    assert "etag" in response.headers
    assert "accept-ranges" in response.headers
    assert response.headers["accept-ranges"] == "bytes"
    assert "cache-control" in response.headers


@pytest.mark.asyncio
async def test_security_headers(client):
    """Test security headers are present"""
    response = await client.get("/health")
    security_headers = [
        "x-frame-options",
        "x-content-type-options",
        "x-xss-protection",
        "referrer-policy",
        "content-security-policy",
    ]

    for header in security_headers:
        assert header in response.headers, f"Missing security header: {header}"


@pytest.mark.asyncio
async def test_api_proxy_routing(client):
    """Test API proxy routing"""
    response = await client.get("/api/test")
    # Should either proxy successfully or return appropriate error
    assert response.status_code in [200, 502, 404]


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_rate_limiting(client):
    """Test rate limiting functionality"""
    # Make multiple rapid requests to trigger rate limiting
    responses = []
    for _ in range(10):
        response = await client.get("/health")
        responses.append(response.status_code)

    # Should not all be 429 (rate limited) in normal operation
    assert 200 in responses, "All requests were rate limited"


def test_config_loading():
    """Test configuration loads correctly"""
    from app.config import server_config, security_config, features_config

    assert server_config.host == "0.0.0.0"
    assert server_config.port == 443
    assert security_config.rate_limiting_enabled is True
    assert features_config.security_enabled is True


@pytest.mark.asyncio
async def test_concurrent_requests(client):
    """Test handling of concurrent requests"""
    tasks = [client.get("/health") for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    for response in responses:
        assert response.status_code == 200


if __name__ == "__main__":
    # Run tests directly
    import subprocess
    import sys

    sys.exit(subprocess.run(["pytest", __file__, "-v"]).returncode)
