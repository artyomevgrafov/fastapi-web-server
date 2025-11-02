#!/usr/bin/env python3
"""
Test Script for FastAPI Server
Verifies that the FastAPI server is working correctly
"""

import requests
import time
import sys
from typing import Dict, Any


class FastAPITester:
    """Test class for FastAPI server functionality"""

    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}

    def test_root_endpoint(self) -> bool:
        """Test the root endpoint"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("✅ Root endpoint: OK")
                self.results["root"] = True
                return True
            else:
                print(f"❌ Root endpoint: Failed (Status: {response.status_code})")
                self.results["root"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Root endpoint: Connection failed - {e}")
            self.results["root"] = False
            return False

    def test_api_docs(self) -> bool:
        """Test the API documentation endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                print("✅ API Documentation: OK")
                self.results["docs"] = True
                return True
            else:
                print(f"❌ API Documentation: Failed (Status: {response.status_code})")
                self.results["docs"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ API Documentation: Connection failed - {e}")
            self.results["docs"] = False
            return False

    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Health endpoint: OK")
                    self.results["health"] = True
                    return True
                else:
                    print(f"❌ Health endpoint: Invalid response - {data}")
                    self.results["health"] = False
                    return False
            else:
                print(f"❌ Health endpoint: Failed (Status: {response.status_code})")
                self.results["health"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Health endpoint: Connection failed - {e}")
            self.results["health"] = False
            return False

    def test_api_info(self) -> bool:
        """Test the API info endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/info")
            if response.status_code == 200:
                data = response.json()
                if data.get("server_name") == "FastAPI Web Server":
                    print("✅ API Info endpoint: OK")
                    self.results["api_info"] = True
                    return True
                else:
                    print(f"❌ API Info endpoint: Invalid response - {data}")
                    self.results["api_info"] = False
                    return False
            else:
                print(f"❌ API Info endpoint: Failed (Status: {response.status_code})")
                self.results["api_info"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ API Info endpoint: Connection failed - {e}")
            self.results["api_info"] = False
            return False

    def test_users_endpoint(self) -> bool:
        """Test the users API endpoints"""
        try:
            # Test GET users
            response = self.session.get(f"{self.base_url}/api/users")
            if response.status_code == 200:
                users = response.json()
                print(f"✅ GET Users endpoint: OK (Found {len(users)} users)")

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
                    print("✅ POST Users endpoint: OK")

                    # Test getting the created user
                    user_id = created_user["id"]
                    response = self.session.get(f"{self.base_url}/api/users/{user_id}")
                    if response.status_code == 200:
                        print("✅ GET User by ID endpoint: OK")
                        self.results["users"] = True
                        return True
                    else:
                        print(
                            f"❌ GET User by ID: Failed (Status: {response.status_code})"
                        )
                else:
                    print(f"❌ POST Users: Failed (Status: {response.status_code})")
            else:
                print(f"❌ GET Users: Failed (Status: {response.status_code})")

            self.results["users"] = False
            return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Users endpoints: Connection failed - {e}")
            self.results["users"] = False
            return False

    def test_echo_endpoint(self) -> bool:
        """Test the echo endpoint"""
        try:
            test_message = "Hello FastAPI!"
            response = self.session.get(f"{self.base_url}/api/echo/{test_message}")
            if response.status_code == 200:
                data = response.json()
                if data.get("original_message") == test_message:
                    print("✅ Echo endpoint: OK")
                    self.results["echo"] = True
                    return True
                else:
                    print(f"❌ Echo endpoint: Invalid response - {data}")
                    self.results["echo"] = False
                    return False
            else:
                print(f"❌ Echo endpoint: Failed (Status: {response.status_code})")
                self.results["echo"] = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Echo endpoint: Connection failed - {e}")
            self.results["echo"] = False
            return False

    def test_math_endpoints(self) -> bool:
        """Test the math calculation endpoints"""
        try:
            # Test square endpoint
            number = 5
            response = self.session.get(f"{self.base_url}/api/math/square/{number}")
            if response.status_code == 200:
                data = response.json()
                if data.get("square") == number**2:
                    print("✅ Math square endpoint: OK")

                    # Test cube endpoint
                    response = self.session.get(
                        f"{self.base_url}/api/math/cube/{number}"
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("cube") == number**3:
                            print("✅ Math cube endpoint: OK")
                            self.results["math"] = True
                            return True
                        else:
                            print(f"❌ Math cube endpoint: Invalid response - {data}")
                    else:
                        print(
                            f"❌ Math cube endpoint: Failed (Status: {response.status_code})"
                        )
                else:
                    print(f"❌ Math square endpoint: Invalid response - {data}")
            else:
                print(
                    f"❌ Math square endpoint: Failed (Status: {response.status_code})"
                )

            self.results["math"] = False
            return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Math endpoints: Connection failed - {e}")
            self.results["math"] = False
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🧪 Running FastAPI Server Tests")
        print("=" * 50)

        tests = [
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
        print("📊 TEST SUMMARY")
        print("=" * 50)

        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")

        if failed_tests == 0:
            print("\n🎉 All tests passed! FastAPI server is working correctly.")
        else:
            print(
                f"\n⚠️  {failed_tests} test(s) failed. Please check the server configuration."
            )

        print(f"\nAccess points:")
        print(f"  Web Interface: {self.base_url}")
        print(f"  API Documentation: {self.base_url}/docs")
        print(f"  Health Check: {self.base_url}/api/health")


def main():
    """Main function to run tests"""
    # Check if requests library is available
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' library is required but not installed.")
        print("Install it with: pip install requests")
        sys.exit(1)

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Test FastAPI Server")
    parser.add_argument(
        "--url",
        default="http://localhost",
        help="Base URL of the FastAPI server (default: http://localhost)",
    )
    parser.add_argument("--port", type=int, help="Port number (overrides URL port)")

    args = parser.parse_args()

    # Construct base URL
    base_url = args.url
    if args.port:
        from urllib.parse import urlparse

        parsed = urlparse(base_url)
        base_url = f"{parsed.scheme}://{parsed.hostname}:{args.port}"

    print(f"Testing FastAPI server at: {base_url}")
    print("Make sure the server is running before testing!")
    print()

    # Run tests
    tester = FastAPITester(base_url)
    tester.run_all_tests()
    tester.print_summary()

    # Exit with appropriate code
    if all(tester.results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
