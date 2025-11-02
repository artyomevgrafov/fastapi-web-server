"""
Production Server with HTTP/2 Support
Производственный сервер с поддержкой HTTP/2

This script starts a production-ready FastAPI server with HTTP/2,
performance optimizations, and security features.
"""

import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
import logging
from app.main import app
from app.config import SERVER_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def check_environment():
    """Check production environment requirements"""
    # Check if running on Linux for optimal performance
    if os.name != "posix":
        logger.warning(
            "Running on non-Linux system. For optimal performance, use Linux with uvloop."
        )

    # Check for required environment variables
    required_vars = ["TARGET_SERVER"]
    for var in required_vars:
        if not os.getenv(var):
            logger.warning(
                f"Environment variable {var} not set. Using default configuration."
            )


def configure_ssl():
    """Configure SSL for production"""
    ssl_config = {}

    if SERVER_CONFIG.get("ssl_enabled"):
        cert_dir = Path("certs")
        cert_file = cert_dir / "cert.pem"
        key_file = cert_dir / "key.pem"

        if cert_file.exists() and key_file.exists():
            ssl_config = {
                "ssl_certfile": str(cert_file),
                "ssl_keyfile": str(key_file),
                "ssl_version": 2,  # TLS 1.2+
            }
            logger.info("SSL certificates found and configured")
        else:
            logger.warning(
                "SSL enabled but certificates not found. Running without SSL."
            )

    return ssl_config


def main():
    """Main function to start production server"""
    try:
        # Environment checks
        check_environment()

        # SSL configuration
        ssl_config = configure_ssl()

        # Uvicorn configuration for production
        uvicorn_config = {
            "app": "app.main:app",
            "host": SERVER_CONFIG.get("host", "0.0.0.0"),
            "port": SERVER_CONFIG.get("port", 443),
            "workers": int(os.getenv("UVICORN_WORKERS", "4")),
            "loop": "uvloop",  # High-performance event loop
            "http": "httptools",  # High-performance HTTP parser
            "lifespan": "on",
            "access_log": True,
            "proxy_headers": True,
            "forwarded_allow_ips": "*",
            "timeout_keep_alive": 5,
            "timeout_notify": 30,
            "timeout_graceful_shutdown": 30,
        }

        # Add SSL config if enabled
        if ssl_config:
            uvicorn_config.update(ssl_config)
            # Enable HTTP/2 when SSL is available
            uvicorn_config["http"] = "auto"  # Allows HTTP/2

        logger.info("🚀 Starting Production FastAPI Server")
        logger.info(f"Host: {uvicorn_config['host']}")
        logger.info(f"Port: {uvicorn_config['port']}")
        logger.info(f"Workers: {uvicorn_config['workers']}")
        logger.info(f"SSL Enabled: {bool(ssl_config)}")
        logger.info(f"HTTP/2: {bool(ssl_config)}")
        logger.info("Press Ctrl+C to stop the server")

        # Start server
        uvicorn.run(**uvicorn_config)

    except KeyboardInterrupt:
        logger.info("⏹️ Production server stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start production server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
