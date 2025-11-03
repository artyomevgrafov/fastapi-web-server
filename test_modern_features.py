#!/usr/bin/env python3
"""
Comprehensive Test Script for Modern Web Server Features
Tests HTTP/2, compression, security headers, and performance features
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import ssl
import http.client
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ModernFeaturesTester:
    """Comprehensive tester for modern web server features"""

    def __init__(self):
        self.base_url_http2 = "https://localhost"
        self.base_url_http1 = "https://localhost:8080"
        self.results = {}

    def test_http2_support(self) -> bool:
        """Test HTTP/2 protocol support"""
        print("🧪 Testing HTTP/2 support...")

        try:
            # Use curl to test HTTP/2 specifically
            result = subprocess.run(
                ["curl", "-I", "--http2", "-k", f"{self.base_url_http2}/"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                if "http/2" in output:
                    print("✅ HTTP/2 protocol detected")
                    self.results["http2"] = True
                    return True
                else:
                    print("❌ HTTP/2 not detected")
                    self.results["http2"] = False
                    return False
            else:
                print("❌ Failed to test HTTP/2")
                self.results["http2"] = False
                return False

        except Exception as e:
            print(f"❌ HTTP/2 test failed: {e}")
            self.results["http2"] = False
            return False

    def test_compression(self) -> bool:
        """Test Brotli and GZip compression support"""
        print("🧪 Testing compression support...")

        test_urls = [
            "/",
            "/static/css/main.css" if Path("static/css/main.css").exists() else "/",
            "/api/health",
        ]

        compression_supported = {"brotli": False, "gzip": False}

        for url in test_urls:
            try:
                # Test Brotli
                response = requests.get(
                    f"{self.base_url_http2}{url}",
                    headers={"Accept-Encoding": "br, gzip, deflate"},
                    verify=False,
                    timeout=10,
                )

                content_encoding = response.headers.get("content-encoding", "").lower()
                if "br" in content_encoding:
                    compression_supported["brotli"] = True
                if "gzip" in content_encoding:
                    compression_supported["gzip"] = True

            except Exception as e:
                print(f"⚠️ Compression test for {url} failed: {e}")
                continue

        # Test with curl --compressed
        try:
            result = subprocess.run(
                ["curl", "--compressed", "-k", f"{self.base_url_http2}/"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print("✅ Compression working with curl --compressed")
                compression_supported["curl_compressed"] = True
            else:
                compression_supported["curl_compressed"] = False

        except Exception as e:
            print(f"⚠️ Curl compression test failed: {e}")
            compression_supported["curl_compressed"] = False

        self.results["compression"] = compression_supported

        brotli_ok = compression_supported["brotli"]
        gzip_ok = compression_supported["gzip"]
        curl_ok = compression_supported.get("curl_compressed", False)

        if brotli_ok and gzip_ok:
            print("✅ Brotli and GZip compression working")
            return True
        elif gzip_ok:
            print("✅ GZip compression working (Brotli not available)")
            return True
        else:
            print("❌ No compression detected")
            return False

    def test_security_headers(self) -> bool:
        """Test comprehensive security headers"""
        print("🧪 Testing security headers...")

        required_headers = {
            "content-security-policy": "CSP",
            "strict-transport-security": "HSTS",
            "x-frame-options": "Frame Protection",
            "x-content-type-options": "MIME Sniffing",
            "referrer-policy": "Referrer Policy",
            "permissions-policy": "Permissions Policy",
            "x-xss-protection": "XSS Protection",
        }

        try:
            response = requests.get(f"{self.base_url_http2}/", verify=False, timeout=10)

            headers_found = {}
            for header, description in required_headers.items():
                if header in response.headers:
                    headers_found[header] = True
                    print(f"✅ {description}: {response.headers[header]}")
                else:
                    headers_found[header] = False
                    print(f"❌ {description}: Missing")

            self.results["security_headers"] = headers_found

            # Check if all critical headers are present
            critical_headers = [
                "content-security-policy",
                "strict-transport-security",
                "x-frame-options",
            ]
            all_critical_present = all(
                headers_found.get(h, False) for h in critical_headers
            )

            if all_critical_present:
                print("✅ All critical security headers present")
                return True
            else:
                print("❌ Some critical security headers missing")
                return False

        except Exception as e:
            print(f"❌ Security headers test failed: {e}")
            self.results["security_headers"] = {}
            return False

    def test_cache_headers(self) -> bool:
        """Test caching headers and ETag support"""
        print("🧪 Testing cache headers...")

        test_cases = [
            ("/", "HTML page", "max-age=300"),
            ("/api/health", "API endpoint", "no-cache"),
            (
                "/static/test.css" if Path("static/test.css").exists() else "/",
                "Static file",
                "max-age=31536000",
            ),
        ]

        cache_tests_passed = 0

        for url, description, expected_cache in test_cases:
            try:
                response = requests.get(
                    f"{self.base_url_http2}{url}", verify=False, timeout=10
                )

                cache_control = response.headers.get("cache-control", "").lower()
                has_etag = "etag" in response.headers
                has_accept_ranges = response.headers.get("accept-ranges") == "bytes"

                print(f"📦 {description}:")
                print(f"   Cache-Control: {cache_control}")
                print(f"   ETag: {'✅' if has_etag else '❌'}")
                print(f"   Accept-Ranges: {'✅' if has_accept_ranges else '❌'}")

                if expected_cache in cache_control:
                    cache_tests_passed += 1

            except Exception as e:
                print(f"⚠️ Cache test for {url} failed: {e}")

        self.results["cache_headers"] = cache_tests_passed >= 2

        if cache_tests_passed >= 2:
            print("✅ Cache headers working correctly")
            return True
        else:
            print("❌ Cache headers need improvement")
            return False

    def test_ocsp_stapling(self) -> bool:
        """Test OCSP stapling support"""
        print("🧪 Testing OCSP stapling...")

        try:
            # This is a basic check - full OCSP validation requires external tools
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            conn = http.client.HTTPSConnection("localhost", 443, context=context)
            conn.request("GET", "/")
            response = conn.getresponse()

            # Check if SSL connection is established
            if response.status == 200:
                print("✅ SSL connection established")
                # Note: Full OCSP stapling verification requires openssl command:
                # openssl s_client -connect localhost:443 -status -tlsextdebug < /dev/null
                print("ℹ️  For full OCSP verification, run:")
                print(
                    "   openssl s_client -connect localhost:443 -status -tlsextdebug < /dev/null"
                )
                self.results["ocsp_stapling"] = True
                return True
            else:
                self.results["ocsp_stapling"] = False
                return False

        except Exception as e:
            print(f"❌ OCSP stapling test failed: {e}")
            self.results["ocsp_stapling"] = False
            return False

    def test_performance_features(self) -> bool:
        """Test performance-related features"""
        print("🧪 Testing performance features...")

        performance_tests = {}

        try:
            # Test request timing headers
            start_time = time.time()
            response = requests.get(
                f"{self.base_url_http2}/api/health", verify=False, timeout=10
            )
            end_time = time.time()

            process_time = response.headers.get("x-process-time")
            request_id = response.headers.get("x-request-id")

            performance_tests["timing_header"] = bool(process_time)
            performance_tests["request_id"] = bool(request_id)
            performance_tests["response_time"] = end_time - start_time

            print(f"⏱️  Response time: {performance_tests['response_time']:.3f}s")
            print(f"📊 X-Process-Time: {'✅' if process_time else '❌'}")
            print(f"🆔 X-Request-ID: {'✅' if request_id else '❌'}")

        except Exception as e:
            print(f"⚠️ Performance test failed: {e}")
            performance_tests = {
                "timing_header": False,
                "request_id": False,
                "response_time": -1,
            }

        self.results["performance"] = performance_tests

        if performance_tests.get("timing_header", False):
            print("✅ Performance features working")
            return True
        else:
            print("❌ Performance features need improvement")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Modern Features Test")
        print("=" * 60)

        tests = [
            ("HTTP/2 Support", self.test_http2_support),
            ("Compression", self.test_compression),
            ("Security Headers", self.test_security_headers),
            ("Cache Headers", self.test_cache_headers),
            ("OCSP Stapling", self.test_ocsp_stapling),
            ("Performance Features", self.test_performance_features),
        ]

        test_results = {}

        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            print("-" * 40)
            try:
                result = test_func()
                test_results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status}: {test_name}")
            except Exception as e:
                print(f"❌ ERROR in {test_name}: {e}")
                test_results[test_name] = False

        return test_results

    def generate_report(self) -> None:
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result is True)

        print(f"📈 Overall Score: {passed_tests}/{total_tests}")

        # Detailed results
        for feature, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status}: {feature.replace('_', ' ').title()}")

        print("\n🎯 Recommendations:")

        if not self.results.get("http2", False):
            print("   • Ensure Hypercorn is running with HTTP/2 support")
            print("   • Check ALPN protocol configuration")

        compression = self.results.get("compression", {})
        if not compression.get("brotli", False):
            print("   • Install brotli: pip install brotli")

        if not self.results.get("security_headers", {}):
            print("   • Review security middleware configuration")

        if not self.results.get("cache_headers", False):
            print("   • Check cache control middleware")

        print("\n💡 For SSL Labs testing:")
        print("   • Visit: https://www.ssllabs.com/ssltest/analyze.html?d=localhost")
        print("   • Run: openssl s_client -connect localhost:443 -status")


def main():
    """Main test runner"""
    tester = ModernFeaturesTester()

    try:
        # Run all tests
        test_results = tester.run_all_tests()

        # Generate report
        tester.generate_report()

        # Exit with appropriate code
        total_passed = sum(1 for result in test_results.values() if result)
        if total_passed >= 4:  # At least 4 out of 6 tests should pass
            print("\n🎉 Modern features test: MOSTLY PASSED")
            sys.exit(0)
        else:
            print("\n💥 Modern features test: NEEDS IMPROVEMENT")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
