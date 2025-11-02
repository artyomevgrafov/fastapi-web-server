"""
Security Test Script
Скрипт тестирования безопасности

This script tests the security system by simulating various attack patterns
and verifying that they are properly blocked or detected.
"""

import asyncio
import httpx
import time
import json
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityTester:
    """
    Security system tester
    Тестер системы безопасности
    """

    def __init__(self, base_url: str = "http://localhost:443"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []

    async def test_suspicious_paths(self) -> List[Dict[str, Any]]:
        """
        Test suspicious path detection
        Тестирование обнаружения подозрительных путей
        """
        suspicious_paths = [
            ".env",
            ".git/config",
            "admin/config.php",
            "phpinfo.php",
            "config.json",
            "actuator/env",
            "debug/default/view",
            "server-status",
            "owa/auth/logon.aspx",
            "+CSCOL+/Java.jar",
            "vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php",
            "_profiler/phpinfo",
            ".well-known/security.txt",
            "robots.txt",
            "login",
            "admin",
            "wp-admin",
            "backup.zip",
            "dump.sql",
            "config.php",
            ".DS_Store",
        ]

        results = []
        for path in suspicious_paths:
            try:
                start_time = time.time()
                response = await self.client.get(f"{self.base_url}/{path}")
                response_time = time.time() - start_time

                result = {
                    "path": path,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "blocked": response.status_code == 403,
                    "success": response.status_code == 404
                    or response.status_code == 403,
                }
                results.append(result)

                logger.info(
                    f"Tested {path}: Status {response.status_code}, Blocked: {result['blocked']}"
                )

            except Exception as e:
                logger.error(f"Error testing {path}: {e}")
                results.append(
                    {
                        "path": path,
                        "status_code": 0,
                        "response_time": 0,
                        "blocked": False,
                        "success": False,
                        "error": str(e),
                    }
                )

        return results

    async def test_suspicious_extensions(self) -> List[Dict[str, Any]]:
        """
        Test suspicious file extension detection
        Тестирование обнаружения подозрительных расширений файлов
        """
        suspicious_extensions = [
            ".env",
            ".bak",
            ".old",
            ".backup",
            ".dist",
            ".pem",
            ".key",
            ".sql",
            ".dump",
            ".log",
            ".ini",
            ".conf",
            ".yml",
            ".json",
            ".xml",
            ".php",
            ".asp",
            ".aspx",
        ]

        results = []
        for ext in suspicious_extensions:
            test_file = f"test{ext}"
            try:
                start_time = time.time()
                response = await self.client.get(f"{self.base_url}/{test_file}")
                response_time = time.time() - start_time

                result = {
                    "extension": ext,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "blocked": response.status_code == 403,
                    "success": response.status_code == 404
                    or response.status_code == 403,
                }
                results.append(result)

                logger.info(
                    f"Tested {ext}: Status {response.status_code}, Blocked: {result['blocked']}"
                )

            except Exception as e:
                logger.error(f"Error testing {ext}: {e}")
                results.append(
                    {
                        "extension": ext,
                        "status_code": 0,
                        "response_time": 0,
                        "blocked": False,
                        "success": False,
                        "error": str(e),
                    }
                )

        return results

    async def test_sql_injection(self) -> List[Dict[str, Any]]:
        """
        Test SQL injection detection
        Тестирование обнаружения SQL-инъекций
        """
        sql_payloads = [
            "?id=1' OR '1'='1",
            "?user=admin' --",
            "?query=union select 1,2,3",
            "?search=1; DROP TABLE users",
            "?param=1' OR 1=1--",
            "?input=1' UNION SELECT * FROM users--",
        ]

        results = []
        for payload in sql_payloads:
            test_path = f"search{payload}"
            try:
                start_time = time.time()
                response = await self.client.get(f"{self.base_url}/{test_path}")
                response_time = time.time() - start_time

                result = {
                    "payload": payload,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "blocked": response.status_code == 403,
                    "success": response.status_code == 404
                    or response.status_code == 403,
                }
                results.append(result)

                logger.info(
                    f"Tested SQL: {payload[:50]}... Status {response.status_code}, Blocked: {result['blocked']}"
                )

            except Exception as e:
                logger.error(f"Error testing SQL injection: {e}")
                results.append(
                    {
                        "payload": payload,
                        "status_code": 0,
                        "response_time": 0,
                        "blocked": False,
                        "success": False,
                        "error": str(e),
                    }
                )

        return results

    async def test_xss_attacks(self) -> List[Dict[str, Any]]:
        """
        Test XSS attack detection
        Тестирование обнаружения XSS-атак
        """
        xss_payloads = [
            "?input=<script>alert('XSS')</script>",
            "?param=javascript:alert('XSS')",
            "?search=onload=alert('XSS')",
            "?query=onerror=alert('XSS')",
            "?data=eval('alert')",
            "?field=document.cookie",
        ]

        results = []
        for payload in xss_payloads:
            test_path = f"form{payload}"
            try:
                start_time = time.time()
                response = await self.client.get(f"{self.base_url}/{test_path}")
                response_time = time.time() - start_time

                result = {
                    "payload": payload,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "blocked": response.status_code == 403,
                    "success": response.status_code == 404
                    or response.status_code == 403,
                }
                results.append(result)

                logger.info(
                    f"Tested XSS: {payload[:50]}... Status {response.status_code}, Blocked: {result['blocked']}"
                )

            except Exception as e:
                logger.error(f"Error testing XSS: {e}")
                results.append(
                    {
                        "payload": payload,
                        "status_code": 0,
                        "response_time": 0,
                        "blocked": False,
                        "success": False,
                        "error": str(e),
                    }
                )

        return results

    async def test_directory_traversal(self) -> List[Dict[str, Any]]:
        """
        Test directory traversal detection
        Тестирование обнаружения обхода директорий
        """
        traversal_paths = [
            "../../etc/passwd",
            "..\\..\\windows\\win.ini",
            "....//etc/shadow",
            "%2e%2e%2fetc%2fpasswd",
            "....\\\\windows\\\\system32",
            "/proc/self/environ",
        ]

        results = []
        for path in traversal_paths:
            try:
                start_time = time.time()
                response = await self.client.get(f"{self.base_url}/{path}")
                response_time = time.time() - start_time

                result = {
                    "path": path,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "blocked": response.status_code == 403,
                    "success": response.status_code == 404
                    or response.status_code == 403,
                }
                results.append(result)

                logger.info(
                    f"Tested traversal: {path} Status {response.status_code}, Blocked: {result['blocked']}"
                )

            except Exception as e:
                logger.error(f"Error testing directory traversal: {e}")
                results.append(
                    {
                        "path": path,
                        "status_code": 0,
                        "response_time": 0,
                        "blocked": False,
                        "success": False,
                        "error": str(e),
                    }
                )

        return results

    async def test_rate_limiting(self) -> Dict[str, Any]:
        """
        Test rate limiting functionality
        Тестирование функциональности ограничения скорости
        """
        test_path = "health"  # Use a valid endpoint
        requests_made = 0
        blocked_requests = 0
        start_time = time.time()

        # Make rapid requests to trigger rate limiting
        for i in range(150):  # More than the default limit of 100/min
            try:
                response = await self.client.get(f"{self.base_url}/{test_path}")
                requests_made += 1

                if response.status_code == 403:
                    blocked_requests += 1
                    logger.info(f"Rate limit triggered at request #{i + 1}")
                    break

                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Error during rate limit test: {e}")
                break

        test_duration = time.time() - start_time

        result = {
            "requests_made": requests_made,
            "blocked_requests": blocked_requests,
            "test_duration": test_duration,
            "rate_limit_triggered": blocked_requests > 0,
            "success": blocked_requests > 0,  # Success if rate limiting worked
        }

        logger.info(
            f"Rate limit test: {requests_made} requests, {blocked_requests} blocked, duration: {test_duration:.2f}s"
        )

        return result

    async def test_security_endpoints(self) -> Dict[str, Any]:
        """
        Test security monitoring endpoints
        Тестирование эндпоинтов мониторинга безопасности
        """
        endpoints = {
            "security_stats": "/security/stats",
            "monitoring_stats": "/monitoring/stats",
            "attack_analysis": "/monitoring/analysis?time_window_hours=1",
            "high_threat_ips": "/monitoring/high-threat-ips",
        }

        results = {}
        for name, endpoint in endpoints.items():
            try:
                response = await self.client.get(f"{self.base_url}{endpoint}")
                results[name] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "data_available": False,
                }

                if response.status_code == 200:
                    try:
                        data = response.json()
                        results[name]["data_available"] = bool(data)
                        logger.info(
                            f"Security endpoint {name}: OK, data available: {bool(data)}"
                        )
                    except:
                        results[name]["data_available"] = False
                        logger.info(f"Security endpoint {name}: OK, but no JSON data")
                else:
                    logger.warning(
                        f"Security endpoint {name}: Status {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"Error testing security endpoint {name}: {e}")
                results[name] = {
                    "status_code": 0,
                    "success": False,
                    "data_available": False,
                    "error": str(e),
                }

        return results

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Run comprehensive security test
        Запуск комплексного теста безопасности
        """
        logger.info("🚀 Starting comprehensive security test...")

        start_time = time.time()

        # Run all tests
        suspicious_paths = await self.test_suspicious_paths()
        suspicious_extensions = await self.test_suspicious_extensions()
        sql_injection = await self.test_sql_injection()
        xss_attacks = await self.test_xss_attacks()
        directory_traversal = await self.test_directory_traversal()
        rate_limiting = await self.test_rate_limiting()
        security_endpoints = await self.test_security_endpoints()

        test_duration = time.time() - start_time

        # Calculate statistics
        all_tests = (
            suspicious_paths
            + suspicious_extensions
            + sql_injection
            + xss_attacks
            + directory_traversal
        )

        blocked_tests = [test for test in all_tests if test.get("blocked", False)]
        successful_tests = [test for test in all_tests if test.get("success", False)]

        summary = {
            "total_tests": len(all_tests),
            "blocked_tests": len(blocked_tests),
            "successful_tests": len(successful_tests),
            "block_rate": len(blocked_tests) / len(all_tests) if all_tests else 0,
            "success_rate": len(successful_tests) / len(all_tests) if all_tests else 0,
            "test_duration": test_duration,
            "rate_limiting_working": rate_limiting.get("rate_limit_triggered", False),
            "security_endpoints_working": all(
                endpoint.get("success", False)
                for endpoint in security_endpoints.values()
            ),
        }

        # Detailed results
        detailed_results = {
            "suspicious_paths": suspicious_paths,
            "suspicious_extensions": suspicious_extensions,
            "sql_injection": sql_injection,
            "xss_attacks": xss_attacks,
            "directory_traversal": directory_traversal,
            "rate_limiting": rate_limiting,
            "security_endpoints": security_endpoints,
        }

        logger.info(f"✅ Security test completed in {test_duration:.2f}s")
        logger.info(
            f"📊 Summary: {summary['blocked_tests']}/{summary['total_tests']} attacks blocked ({summary['block_rate']:.1%})"
        )

        return {
            "summary": summary,
            "detailed_results": detailed_results,
            "timestamp": time.time(),
        }

    async def close(self):
        """Close the HTTP client / Закрыть HTTP-клиент"""
        await self.client.aclose()


async def main():
    """
    Main test function
    Главная тестовая функция
    """
    tester = SecurityTester()

    try:
        # Run comprehensive test
        results = await tester.run_comprehensive_test()

        # Print summary
        print("\n" + "=" * 60)
        print("🔒 SECURITY TEST SUMMARY / СВОДКА ТЕСТА БЕЗОПАСНОСТИ")
        print("=" * 60)

        summary = results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Blocked Attacks: {summary['blocked_tests']}")
        print(f"Block Rate: {summary['block_rate']:.1%}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(
            f"Rate Limiting: {'✅ WORKING' if summary['rate_limiting_working'] else '❌ NOT WORKING'}"
        )
        print(
            f"Security Endpoints: {'✅ WORKING' if summary['security_endpoints_working'] else '❌ NOT WORKING'}"
        )
        print(f"Test Duration: {summary['test_duration']:.2f}s")

        # Save results to file
        output_file = "security_test_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Detailed results saved to: {output_file}")

        # Overall assessment
        if summary["block_rate"] >= 0.8 and summary["rate_limiting_working"]:
            print("\n🎉 SECURITY SYSTEM: ✅ EXCELLENT PROTECTION")
        elif summary["block_rate"] >= 0.6:
            print("\n⚠️  SECURITY SYSTEM: ✅ GOOD PROTECTION")
        elif summary["block_rate"] >= 0.4:
            print("\n⚠️  SECURITY SYSTEM: ⚠️  MODERATE PROTECTION")
        else:
            print("\n🚨 SECURITY SYSTEM: ❌ NEEDS IMPROVEMENT")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")

    finally:
        await tester.close()


if __name__ == "__main__":
    # Run the test
    asyncio.run(main())
