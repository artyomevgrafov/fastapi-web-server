#!/usr/bin/env python3
"""
HTTPS Test Script for FastAPI Server
Tests the FastAPI server with SSL/TLS enabled
"""

import requests
import time
import sys
import urllib3
from typing import Dict, Any

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HTTPSFastAPITester:
    """Test class for FastAPI server with HTTPS functionality"""

    def __init__(self, base_url: str = "https://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        # Disable SSL verification for self-signed certificates
        self.session.verify = False
        self.results = {}

    def test_root_endpoint(self) -> bool:
        """Test the root endpoint over HTTPS"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("✅ Root endpoint (HTTPS): OK")
                self.results["root"] = True
                return True
            else:
                print(
                    f"❌ Root endpoint (HTTPS): Failed (Status: {response.status_code})"
                )
                self.results["root"] = False
                return False
        except requests.exceptions.SSLError as e:
            print(f"❌ Root endpoint (HTTPS): SSL Error - {e}")
            self.results["root"] = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Root endpoint (HTTPS): Connection failed - {e}")
            self.results["root"] = False
            return False

    def test_api_docs(self) -> bool:
        """Test the API documentation endpoint over HTTPS"""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                print("✅ API Documentation (HTTPS): OK")
                self.results["docs"] = True
                return True
            else:
                print(
                    f"❌ API Documentation (HTTPS): Failed (Status: {response.status_code})"
                )
                self.results["docs"] = False
                return False
        except requests.exceptions.SSLError as e:
            print(f"❌ API Documentation (HTTPS): SSL Error - {e}")
            self.results["docs"] = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ API Documentation (HTTPS): Connection failed - {e}")
            self.results["docs"] = False
            return False

    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint over HTTPS"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Health endpoint (HTTPS): OK")
                    self.results["health"] = True
                    return True
                else:
                    print(f"❌ Health endpoint (HTTPS): Invalid response - {data}")
                    self.results["health"] = False
                    return False
            else:
                print(
                    f"❌ Health endpoint (HTTPS): Failed (Status: {response.status_code})"
                )
                self.results["health"] = False
                return False
        except requests.exceptions.SSLError as e:
            print(f"❌ Health endpoint (HTTPS): SSL Error - {e}")
            self.results["health"] = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Health endpoint (HTTPS): Connection failed - {e}")
            self.results["health"] = False
            return False

    def test_api_info(self) -> bool:
        """Test the API info endpoint over HTTPS"""
        try:
            response = self.session.get(f"{self.base_url}/api/info")
            if response.status_code == 200:
                data = response.json()
                if data.get("server_name") == "FastAPI Web Server":
                    print("✅ API Info endpoint (HTTPS): OK")
                    self.results["api_info"] = True
                    return True
                else:
                    print(f"❌ API Info endpoint (HTTPS): Invalid response - {data}")
                    self.results["api_info"] = False
                    return False
            else:
                print(
                    f"❌ API Info endpoint (HTTPS): Failed (Status: {response.status_code})"
                )
                self.results["api_info"] = False
                return False
        except requests.exceptions.SSLError as e:
            print(f"❌ API Info endpoint (HTTPS): SSL Error - {e}")
            self.results["api_info"] = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ API Info endpoint (HTTPS): Connection failed - {e}")
            self.results["api_info"] = False
            return False

    def test_users_endpoint(self) -> bool:
        """Test the users API endpoints over HTTPS"""
        try:
            # Test GET users
            response = self.session.get(f"{self.base_url}/api/users")
            if response.status_code == 200:
                users = response.json()
                print(f"✅ GET Users endpoint (HTTPS): OK (Found {len(users)} users)")

                # Test creating a new user
                new_user = {
                    "name": "Test User",
                    "email": f"test{int(time.time())}@example.com",
                    "age": 30,
                }
                response = self.session.post(
                    f"{self.base_url}/api/users", json=new_user
                )
                if response.status_code == 200:
                    created_user = response.json()
                    print("✅ POST Users endpoint (HTTPS): OK")

                    # Test getting the created user
                    user_id = created_user["id"]
                    response = self.session.get(f"{self.base_url}/api/users/{user_id}")
                    if response.status_code == 200:
                        print("✅ GET User by ID endpoint (HTTPS): OK")
                        self.results["users"] = True
                        return True
                    else:
                        print(
                            f"❌ GET User by ID (HTTPS): Failed (Status: {response.status_code})"
                        )
                else:
                    print(
                        f"❌ POST Users (HTTPS): Failed (Status: {response.status_code})"
                    )
            else:
                print(f"❌ GET Users (HTTPS): Failed (Status: {response.status_code})")

            self.results["users"] = False
            return False

        except requests.exceptions.SSLError as e:
            print(f"❌ Users endpoints (HTTPS): SSL Error - {e}")
            self.results["users"] = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Users endpoints (HTTPS): Connection failed - {e}")
            self.results["users"] = False
            return False

    def test_echo_endpoint(self) -> bool:
        """Test the echo endpoint over HTTPS"""
        try:
            test_message = "Hello FastAPI!"
            response = self.session.get(f"{self.base_url}/api/echo/{test_message}")
            if response.status_code == 200:
                data = response.json()
                if data.get("original_message") == test_message:
                    print("✅ Echo endpoint (HTTPS): OK")
                    self.results["echo"] = True
                    return True
                else:
                    print(f"❌ Echo endpoint (HTTPS): Invalid response - {data}")
                    self.results["echo"] = False
                    return False
            else:
                print(
                    f"❌ Echo endpoint (HTTPS): Failed (Status: {response.status_code})"
                )
                self.results["echo"] = False
                return False
        except requests.exceptions.SSLError as e:
            print(f"❌ Echo endpoint (HTTPS): SSL Error - {e}")
            self.results["echo"] = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Echo endpoint (HTTPS): Connection failed - {e}")
            self.results["echo"] = False
            return False

    def test_math_endpoints(self) -> bool:
        """Test the math calculation endpoints over HTTPS"""
        try:
            # Test square endpoint
            number = 5
            response = self.session.get(f"{self.base_url}/api/math/square/{number}")
            if response.status_code == 200:
                data = response.json()
                if data.get("square") == number**2:
                    print("✅ Math square endpoint (HTTPS): OK")

                    # Test cube endpoint
                    response = self.session.get(
                        f"{self.base_url}/api/math/cube/{number}"
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("cube") == number**3:
                            print("✅ Math cube endpoint (HTTPS): OK")
                            self.results["math"] = True
                            return True
                        else:
                            print(
                                f"❌ Math cube endpoint (HTTPS): Invalid response - {data}"
                            )
                    else:
                        print(
                            f"❌ Math cube endpoint (HTTPS): Failed (Status: {response.status_code})"
                        )
                else:
                    print(f"❌ Math square endpoint (HTTPS): Invalid response - {data}")
            else:
                print(
                    f"❌ Math square endpoint (HTTPS): Failed (Status: {response.status_code})"
                )

            self.results["math"] = False
            return False

        except requests.exceptions.SSLError as e:
            print(f"❌ Math endpoints (HTTPS): SSL Error - {e}")
            self.results["math"] = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Math endpoints (HTTPS): Connection failed - {e}")
            self.results["math"] = False
            return False

    def test_ssl_certificate(self) -> bool:
        """Test SSL certificate information"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                # Check if we're actually using HTTPS
                if response.url.startswith("https://"):
                    print("✅ SSL Certificate: Connection secured with HTTPS")
                    self.results["ssl"] = True
                    return True
                else:
                    print("⚠️  SSL Certificate: Connection not using HTTPS")
                    self.results["ssl"] = False
                    return False
            else:
                print(
                    f"❌ SSL Certificate test failed (Status: {response.status_code})"
                )
                self.results["ssl"] = False
                return False
        except requests.exceptions.SSLError as e:
            print(f"❌ SSL Certificate: Error - {e}")
            self.results["ssl"] = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ SSL Certificate: Connection failed - {e}")
            self.results["ssl"] = False
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all HTTPS tests and return results"""
        print("🔐 Running FastAPI Server HTTPS Tests")
        print("=" * 50)
        print(f"Testing server at: {self.base_url}")
        print("SSL verification disabled for self-signed certificates")
        print("=" * 50)

        tests = [
            self.test_ssl_certificate,
            self.test_root_endpoint,
            self.test_api_docs,
            self.test_health_endpoint,
            self.test_api_info,
            self.test_users_endpoint,
            self.test_echo_endpoint,
            self.test_math_endpoints,
        ]

        for test in tests:
            test()
            time.sleep(0.5)  # Small delay between tests

        return self.results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 HTTPS TEST SUMMARY")
        print("=" * 50)

        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")

        if failed_tests == 0:
            print(
                "\n🎉 All HTTPS tests passed! FastAPI server is working correctly with SSL."
            )
        else:
            print(
                f"\n⚠️  {failed_tests} test(s) failed. Please check the server SSL configuration."
            )

        print(f"\n🔐 Access points (HTTPS):")
        print(f"  Web Interface: {self.base_url}")
        print(f"  API Documentation: {self.base_url}/docs")
        print(f"  Health Check: {self.base_url}/api/health")
        print(f"\n⚠️  Note: Using self-signed certificate - SSL verification disabled")


def main():
    """Main function to run HTTPS tests"""
    # Check if requests library is available
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' library is required but not installed.")
        print("Install it with: pip install requests")
        sys.exit(1)

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Test FastAPI Server with HTTPS")
    parser.add_argument(
        "--url",
        default="https://localhost:8000",
        help="Base URL of the FastAPI server (default: https://localhost:8000)",
    )
    parser.add_argument("--port", type=int, help="Port number (overrides URL port)")

    args = parser.parse_args()

    # Construct base URL
    base_url = args.url
    if args.port:
        from urllib.parse import urlparse

        parsed = urlparse(base_url)
        base_url = f"{parsed.scheme}://{parsed.hostname}:{args.port}"

    print(f"Testing FastAPI HTTPS server at: {base_url}")
    print("Make sure the server is running with SSL enabled before testing!")
    print()

    # Run tests
    tester = HTTPSFastAPITester(base_url)
    tester.run_all_tests()
    tester.print_summary()

    # Exit with appropriate code
    if all(tester.results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
