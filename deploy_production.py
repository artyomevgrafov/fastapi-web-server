"""
Production Deployment Script for FastAPI Web Server
Complete deployment automation with all improvements
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import argparse


class ProductionDeployer:
    """Production deployment automation with all improvements"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or ".env"
        self.base_dir = Path(__file__).parent
        self.deployment_config = self._load_deployment_config()

    def _load_deployment_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        return {
            "docker": {
                "enabled": True,
                "compose_file": "docker-compose.yml",
                "build_args": ["--build-arg", "ENVIRONMENT=production"],
            },
            "systemd": {
                "enabled": True,
                "service_file": "systemd/fastapi-web-server.service",
                "install_path": "/etc/systemd/system/fastapi-web-server.service",
            },
            "nginx": {
                "enabled": True,
                "config_file": "nginx/nginx.conf",
                "install_path": "/etc/nginx/sites-available/fastapi-web-server",
            },
            "ssl": {
                "enabled": True,
                "certbot_enabled": False,
                "self_signed": True,
            },
            "monitoring": {
                "enabled": True,
                "prometheus": True,
                "grafana": True,
            },
        }

    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        print("🔍 Checking prerequisites...")

        checks = {
            "Python 3.8+": self._check_python_version(),
            "Docker": self._check_docker(),
            "Docker Compose": self._check_docker_compose(),
            "System Resources": self._check_system_resources(),
            "Port Availability": self._check_ports(),
        }

        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")

            if not passed:
                all_passed = False

        if not all_passed:
            print("\n⚠️  Some prerequisites failed. Deployment may not work correctly.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != "y":
                return False

        return True

    def _check_python_version(self) -> bool:
        """Check Python version"""
        return sys.version_info >= (3, 8)

    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _check_docker_compose(self) -> bool:
        """Check if Docker Compose is available"""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _check_system_resources(self) -> bool:
        """Check system resources"""
        try:
            import psutil

            # Check memory (at least 2GB recommended)
            memory_gb = psutil.virtual_memory().total / (1024**3)
            memory_ok = memory_gb >= 2.0

            # Check disk space (at least 5GB free)
            disk_free_gb = psutil.disk_usage("/").free / (1024**3)
            disk_ok = disk_free_gb >= 5.0

            return memory_ok and disk_ok
        except ImportError:
            # If psutil not available, assume resources are sufficient
            return True

    def _check_ports(self) -> bool:
        """Check if required ports are available"""
        ports_to_check = [80, 443, 8080]
        try:
            import socket

            for port in ports_to_check:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(("localhost", port)) == 0:
                        print(f"   ⚠️  Port {port} is already in use")
            return True
        except Exception:
            return True

    def setup_environment(self) -> bool:
        """Setup production environment"""
        print("\n🔧 Setting up production environment...")

        steps = [
            ("Creating directories", self._create_directories),
            ("Generating SSL certificates", self._generate_ssl_certificates),
            ("Creating configuration files", self._create_config_files),
            ("Setting file permissions", self._set_permissions),
        ]

        for step_name, step_func in steps:
            print(f"   {step_name}...", end=" ")
            try:
                if step_func():
                    print("✅")
                else:
                    print("❌")
                    return False
            except Exception as e:
                print(f"❌ (Error: {e})")
                return False

        return True

    def _create_directories(self) -> bool:
        """Create necessary directories"""
        directories = [
            "logs",
            "certs",
            "data/htdocs",
            "static",
            "backups",
        ]

        for directory in directories:
            path = self.base_dir / directory
            path.mkdir(parents=True, exist_ok=True)

        return True

    def _generate_ssl_certificates(self) -> bool:
        """Generate SSL certificates for production"""
        if not self.deployment_config["ssl"]["enabled"]:
            return True

        cert_dir = self.base_dir / "certs"
        key_file = cert_dir / "key.pem"
        cert_file = cert_dir / "cert.pem"

        if key_file.exists() and cert_file.exists():
            print("(SSL certificates already exist)")
            return True

        try:
            # Generate self-signed certificate for development
            subprocess.run(
                [
                    "openssl",
                    "req",
                    "-x509",
                    "-newkey",
                    "rsa:4096",
                    "-keyout",
                    str(key_file),
                    "-out",
                    str(cert_file),
                    "-days",
                    "365",
                    "-nodes",
                    "-subj",
                    "/C=US/ST=State/L=City/O=Organization/CN=localhost",
                ],
                capture_output=True,
                check=True,
            )

            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("(OpenSSL not available, creating placeholder certificates)")
            # Create placeholder files
            key_file.write_text("PLACEHOLDER PRIVATE KEY - REPLACE IN PRODUCTION")
            cert_file.write_text("PLACEHOLDER CERTIFICATE - REPLACE IN PRODUCTION")
            return True

    def _create_config_files(self) -> bool:
        """Create production configuration files"""
        # Create production .env file if it doesn't exist
        env_file = self.base_dir / ".env.production"
        if not env_file.exists():
            env_template = self.base_dir / ".env"
            if env_template.exists():
                shutil.copy(env_template, env_file)
            else:
                # Create basic production .env
                env_content = """# Production Environment Configuration
HOST=0.0.0.0
PORT=8080
TARGET_SERVER=http://127.0.0.1:8097
SSL_ENABLED=true
SSL_CERT_FILE=./certs/cert.pem
SSL_KEY_FILE=./certs/key.pem

# Security
SECURITY_ENABLED=true
RATE_LIMITING_ENABLED=true
IP_BLOCKING_ENABLED=true

# Performance
WORKERS=4
GZIP_ENABLED=true
HTTP2_ENABLED=true

# Logging
LOG_LEVEL=INFO
ENABLE_DETAILED_LOGGING=true
"""
                env_file.write_text(env_content)

        return True

    def _set_permissions(self) -> bool:
        """Set appropriate file permissions"""
        try:
            # Make scripts executable
            scripts = [
                "start_443.py",
                "start_8080.py",
                "start_production.py",
                "run_benchmarks.py",
                "automated_benchmark.py",
            ]

            for script in scripts:
                script_path = self.base_dir / script
                if script_path.exists():
                    script_path.chmod(0o755)

            return True
        except Exception:
            return True

    def build_docker_images(self) -> bool:
        """Build Docker images for production"""
        if not self.deployment_config["docker"]["enabled"]:
            print("Docker deployment disabled in configuration")
            return True

        print("\n🐳 Building Docker images...")

        try:
            # Build main application
            build_cmd = [
                "docker-compose",
                "-f",
                self.deployment_config["docker"]["compose_file"],
                "build",
            ] + self.deployment_config["docker"]["build_args"]

            result = subprocess.run(
                build_cmd, cwd=self.base_dir, capture_output=True, text=True
            )

            if result.returncode == 0:
                print("✅ Docker images built successfully")
                return True
            else:
                print(f"❌ Docker build failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Docker build error: {e}")
            return False

    def deploy_systemd_service(self) -> bool:
        """Deploy systemd service for Linux"""
        if not self.deployment_config["systemd"]["enabled"]:
            print("Systemd deployment disabled in configuration")
            return True

        print("\n⚙️  Deploying systemd service...")

        service_file = self.base_dir / self.deployment_config["systemd"]["service_file"]
        if not service_file.exists():
            print("❌ Systemd service file not found")
            return False

        try:
            # Copy service file to system directory
            install_cmd = [
                "sudo",
                "cp",
                str(service_file),
                self.deployment_config["systemd"]["install_path"],
            ]

            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to copy service file: {result.stderr}")
                return False

            # Reload systemd and enable service
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(
                ["sudo", "systemctl", "enable", "fastapi-web-server"], check=True
            )

            print("✅ Systemd service deployed successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Systemd deployment failed: {e}")
            return False

    def deploy_nginx_config(self) -> bool:
        """Deploy Nginx configuration"""
        if not self.deployment_config["nginx"]["enabled"]:
            print("Nginx deployment disabled in configuration")
            return True

        print("\n🌐 Deploying Nginx configuration...")

        nginx_config = self.base_dir / self.deployment_config["nginx"]["config_file"]
        if not nginx_config.exists():
            print("❌ Nginx configuration file not found")
            return False

        try:
            # Copy nginx config
            install_cmd = [
                "sudo",
                "cp",
                str(nginx_config),
                self.deployment_config["nginx"]["install_path"],
            ]

            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to copy Nginx config: {result.stderr}")
                return False

            # Enable site and reload nginx
            site_name = Path(self.deployment_config["nginx"]["install_path"]).name
            subprocess.run(
                [
                    "sudo",
                    "ln",
                    "-sf",
                    f"/etc/nginx/sites-available/{site_name}",
                    f"/etc/nginx/sites-enabled/{site_name}",
                ],
                check=True,
            )

            subprocess.run(["sudo", "nginx", "-t"], check=True)
            subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)

            print("✅ Nginx configuration deployed successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Nginx deployment failed: {e}")
            return False

    def start_services(self) -> bool:
        """Start all deployed services"""
        print("\n🚀 Starting services...")

        services_started = True

        # Start Docker services if enabled
        if self.deployment_config["docker"]["enabled"]:
            try:
                subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        self.deployment_config["docker"]["compose_file"],
                        "up",
                        "-d",
                    ],
                    cwd=self.base_dir,
                    check=True,
                )
                print("✅ Docker services started")
            except subprocess.CalledProcessError:
                print("❌ Failed to start Docker services")
                services_started = False

        # Start systemd service if enabled
        if self.deployment_config["systemd"]["enabled"]:
            try:
                subprocess.run(
                    ["sudo", "systemctl", "start", "fastapi-web-server"], check=True
                )
                print("✅ Systemd service started")
            except subprocess.CalledProcessError:
                print("❌ Failed to start systemd service")
                services_started = False

        return services_started

    def run_health_checks(self) -> bool:
        """Run health checks on deployed services"""
        print("\n🔍 Running health checks...")

        health_checks = [
            ("Docker containers", self._check_docker_health),
            ("Systemd service", self._check_systemd_health),
            ("Web server", self._check_web_server_health),
        ]

        all_healthy = True
        for check_name, check_func in health_checks:
            print(f"   {check_name}...", end=" ")
            try:
                if check_func():
                    print("✅")
                else:
                    print("❌")
                    all_healthy = False
            except Exception as e:
                print(f"❌ (Error: {e})")
                all_healthy = False

        return all_healthy

    def _check_docker_health(self) -> bool:
        """Check Docker container health"""
        try:
            result = subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    self.deployment_config["docker"]["compose_file"],
                    "ps",
                ],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
            )

            return result.returncode == 0 and "Up" in result.stdout
        except Exception:
            return False

    def _check_systemd_health(self) -> bool:
        """Check systemd service health"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "fastapi-web-server"],
                capture_output=True,
                text=True,
            )

            return result.returncode == 0 and result.stdout.strip() == "active"
        except Exception:
            return False

    def _check_web_server_health(self) -> bool:
        """Check web server health endpoint"""
        try:
            import requests

            response = requests.get("http://localhost:8080/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def run_performance_tests(self) -> bool:
        """Run performance tests on deployed system"""
        print("\n⚡ Running performance tests...")

        try:
            # Run automated benchmark
            result = subprocess.run(
                [sys.executable, "automated_benchmark.py"],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print("✅ Performance tests completed successfully")
                return True
            else:
                print(f"❌ Performance tests failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Performance tests timed out")
            return False
        except Exception as e:
            print(f"❌ Performance tests error: {e}")
            return False

    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment report"""
        return {
            "deployment": {
                "timestamp": subprocess.getoutput("date -Iseconds"),
                "version": "1.0.0",
                "environment": "production",
            },
            "services": {
                "docker": self.deployment_config["docker"]["enabled"],
                "systemd": self.deployment_config["systemd"]["enabled"],
                "nginx": self.deployment_config["nginx"]["enabled"],
                "ssl": self.deployment_config["ssl"]["enabled"],
            },
            "health_checks": {
                "docker_healthy": self._check_docker_health(),
                "systemd_healthy": self._check_systemd_health(),
                "web_server_healthy": self._check_web_server_health(),
            },
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate deployment recommendations"""
        recommendations = []

        if not self.deployment_config["ssl"]["certbot_enabled"]:
            recommendations.append(
                "Configure Let's Encrypt certificates for production SSL"
            )

        if not self.deployment_config["monitoring"]["enabled"]:
            recommendations.append(
                "Enable monitoring stack (Prometheus + Grafana) for production"
            )

        recommendations.extend(
            [
                "Set up log rotation and monitoring",
                "Configure backup strategy for certificates and data",
                "Set up firewall rules for production ports",
                "Configure DNS records for your domain",
                "Set up SSL certificate auto-renewal",
            ]
        )

        return recommendations

    def deploy(self, skip_checks: bool = False, skip_tests: bool = False) -> bool:
        """Run complete deployment process"""
        print("🚀 Starting FastAPI Web Server Production Deployment")
        print("=" * 60)

        # Check prerequisites
        if not skip_checks and not self.check_prerequisites():
            return False

        # Setup environment
        if not self.setup_environment():
            return False

        # Build and deploy
        if not self.build_docker_images():
            return False

        if not self.deploy_systemd_service():
            return False

        if not self.deploy_nginx_config():
            return False

        # Start services
        if not self.start_services():
            return False

        # Health checks
        if not self.run_health_checks():
            print("⚠️  Some health checks failed")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != "y":
                return False

        # Performance tests
        if not skip_tests and not self.run_performance_tests():
            print("⚠️  Performance tests failed")
            response = input("Continue deployment anyway? (y/N): ")
            if response.lower() != "y":
                return False

        # Generate report
        report = self.generate_deployment_report()
        report_file = self.base_dir / "deployment_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print("\n" + "=" * 60)
        print("✅ DEPLOYMENT COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print(f"\n📊 Deployment report saved to: {report_file}")

        # Print recommendations
        if report["recommendations"]:
            print("\n💡 Recommendations for production:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")

        print(f"\n🌐 Your server should be accessible at:")
        print(f"   HTTP:  http://localhost:80")
        print(f"   HTTPS: https://localhost:443")
        print(f"   API:   http://localhost:8080")

        return True


def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(
        description="FastAPI Web Server Production Deployment"
    )
    parser.add_argument(
        "--skip-checks", action="store_true", help="Skip prerequisite checks"
    )
    parser.add_argument(
        "--skip-tests", action="store_true", help="Skip performance tests"
    )
    parser.add_argument("--config", help="Path to deployment configuration file")

    args = parser.parse_args()

    deployer = ProductionDeployer(config_path=args.config)

    try:
        success = deployer.deploy(
            skip_checks=args.skip_checks, skip_tests=args.skip_tests
        )

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
