"""
Enhanced FastAPI Server with Security Features
Расширенный сервер FastAPI с функциями безопасности

This script starts the FastAPI server with comprehensive security features
including IP blocking, rate limiting, threat detection, and real-time monitoring.
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app
from app.security import security_manager
from app.monitoring import attack_monitor
from app.config import SERVER_CONFIG, SECURITY_CONFIG, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    datefmt=LOGGING_CONFIG["date_format"],
)

logger = logging.getLogger(__name__)


def print_security_banner():
    """Print security system banner / Вывести баннер системы безопасности"""
    banner = """
    🔒 SECURITY SYSTEM ACTIVATED 🔒
    ===============================
    IP Blocking:       {ip_blocking}
    Rate Limiting:     {rate_limiting}
    Threat Detection:  {threat_detection}
    Real-time Monitoring: {monitoring}
    ===============================
    """.format(
        ip_blocking="✅ ENABLED"
        if SECURITY_CONFIG["ip_blocking"]["enabled"]
        else "❌ DISABLED",
        rate_limiting="✅ ENABLED"
        if SECURITY_CONFIG["rate_limiting"]["enabled"]
        else "❌ DISABLED",
        threat_detection="✅ ENABLED"
        if SECURITY_CONFIG["threat_detection"]["enabled"]
        else "❌ DISABLED",
        monitoring="✅ ENABLED"
        if SECURITY_CONFIG["monitoring"]["enable_detailed_logging"]
        else "❌ DISABLED",
    )
    print(banner)


def print_server_info():
    """Print server configuration information / Вывести информацию о конфигурации сервера"""
    info = """
    🚀 SERVER CONFIGURATION 🚀
    ==========================
    Host:            {host}
    Port:            {port}
    SSL:             {ssl}
    Target Backend:  {backend}
    Timeout:         {timeout}s
    Static Root:     {static_root}
    ==========================
    """.format(
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        ssl="✅ ENABLED" if SERVER_CONFIG["ssl_enabled"] else "❌ DISABLED",
        backend=SERVER_CONFIG["target_server"],
        timeout=SERVER_CONFIG["timeout"],
        static_root=SERVER_CONFIG["static_root"],
    )
    print(info)


def check_ssl_certificates():
    """Check SSL certificate availability / Проверить доступность SSL сертификатов"""
    cert_dir = Path("certs")
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"

    if SERVER_CONFIG["ssl_enabled"]:
        if not cert_dir.exists():
            logger.warning("SSL certificates directory not found: certs/")
            return False

        if not cert_file.exists():
            logger.warning(f"SSL certificate file not found: {cert_file}")
            return False

        if not key_file.exists():
            logger.warning(f"SSL key file not found: {key_file}")
            return False

        logger.info("✅ SSL certificates found and ready")
        return True
    else:
        logger.info("ℹ️  SSL disabled in configuration")
        return True


def initialize_security_system():
    """Initialize security system components / Инициализировать компоненты системы безопасности"""
    try:
        # Security system is already initialized via imports
        # But we can perform additional setup here if needed

        # Cleanup old logs
        attack_monitor.cleanup_old_logs()

        logger.info("✅ Security system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize security system: {e}")
        return False


def main():
    """Main function to start the server / Главная функция для запуска сервера"""
    try:
        # Print startup information
        print_security_banner()
        print_server_info()

        # Check prerequisites
        if not check_ssl_certificates():
            logger.warning("SSL certificate issues detected, but continuing...")

        # Initialize security system
        if not initialize_security_system():
            logger.warning(
                "Security system initialization had issues, but continuing..."
            )

        # SSL configuration
        ssl_config = {}
        if SERVER_CONFIG["ssl_enabled"]:
            ssl_config = {
                "ssl_certfile": "certs/cert.pem",
                "ssl_keyfile": "certs/key.pem",
            }

        # Start server
        logger.info(
            f"🚀 Starting FastAPI server on {SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}"
        )
        logger.info("Press Ctrl+C to stop the server")

        uvicorn.run(
            app,
            host=SERVER_CONFIG["host"],
            port=SERVER_CONFIG["port"],
            **ssl_config,
            log_level="info",
        )

    except KeyboardInterrupt:
        logger.info("⏹️  Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
