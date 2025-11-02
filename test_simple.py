#!/usr/bin/env python3
"""
Simple FastAPI Server Test
Tests the FastAPI server with automatic retry and wait functionality
"""

import requests
import time
import sys
import urllib3
from typing import Optional

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SimpleFastAPITester:
    """Simple test class for FastAPI server with retry logic"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        max_retries: int = 10,
        retry_delay: float = 1.0,
    ):
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()

        # Disable SSL verification for self-signed certificates if using HTTPS
        if base_url.startswith("https://"):
            self.session.verify = False

    def wait_for_server(self) -> bool:
        """Wait for server to become available"""
        print(f"⏳ Waiting for server at {self.base_url}...")

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(f"{self.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        print(f"✅ Server is ready after {attempt + 1} attempts")
                        return True
            except requests.exceptions.RequestException:
                pass

            if attempt < self.max_retries - 1:
                print(
                    f"  Attempt {attempt + 1}/{self.max_retries} failed, retrying in {self.retry_delay}s..."
                )
                time.sleep(self.retry_delay)

        print(f"❌ Server not available after {self.max_retries} attempts")
        return False

    def test_basic_endpoints(self) -> bool:
        """Test basic server endpoints"""
        print("\n🧪 Testing basic endpoints...")

        endpoints = [
            ("/", "Root endpoint"),
            ("/docs", "API Documentation"),
            ("/api/health", "Health Check"),
            ("/api/info", "API Info"),
            ("/api/users", "Users API"),
        ]

        all_passed = True

        for endpoint, description in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {description}: OK")
                else:
                    print(f"❌ {description}: Failed (Status: {response.status_code})")
                    all_passed = False
            except requests.exceptions.RequestException as e:
                print(f"❌ {description}: Connection failed - {e}")
                all_passed = False

            time.sleep(0.2)  # Small delay between requests

        return all_passed

    def test_api_functionality(self) -> bool:
        """Test API functionality"""
        print("\n🔧 Testing API functionality...")

        try:
            # Test echo endpoint
            test_message = "Hello FastAPI!"
            response = self.session.get(
                f"{self.base_url}/api/echo/{test_message}", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("original_message") == test_message:
                    print("✅ Echo endpoint: OK")
                else:
                    print(f"❌ Echo endpoint: Invalid response")
                    return False
            else:
                print(f"❌ Echo endpoint: Failed (Status: {response.status_code})")
                return False

            # Test math endpoint
            response = self.session.get(
                f"{self.base_url}/api/math/square/5", timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("square") == 25:
                    print("✅ Math endpoint: OK")
                else:
                    print(f"❌ Math endpoint: Invalid response")
                    return False
            else:
                print(f"❌ Math endpoint: Failed (Status: {response.status_code})")
                return False

            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ API functionality test failed: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🚀 FastAPI Server Simple Test")
        print("=" * 40)

        # Wait for server
        if not self.wait_for_server():
            return False

        # Test basic endpoints
        basic_ok = self.test_basic_endpoints()

        # Test API functionality
        api_ok = self.test_api_functionality()

        # Print summary
        print("\n" + "=" * 40)
        print("📊 TEST SUMMARY")
        print("=" * 40)

        if basic_ok and api_ok:
            print("✅ All tests passed! Server is working correctly.")
            print(f"\n🌐 Server is running at: {self.base_url}")
            print(f"📚 Documentation: {self.base_url}/docs")
            print(f"❤️  Health Check: {self.base_url}/api/health")
            return True
        else:
            print("❌ Some tests failed. Please check server configuration.")
            return False


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Simple FastAPI Server Test")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the FastAPI server (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=10,
        help="Maximum number of retry attempts (default: 10)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between retries in seconds (default: 1.0)",
    )

    args = parser.parse_args()

    # Create tester and run tests
    tester = SimpleFastAPITester(
        base_url=args.url, max_retries=args.retries, retry_delay=args.delay
    )

    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
