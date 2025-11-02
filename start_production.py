#!/usr/bin/env python3
"""
Production Server with HTTP/2 Support via Hypercorn
Производственный сервер с поддержкой HTTP/2 через Hypercorn

This script starts a production-ready FastAPI server with HTTP/2,
performance optimizations, and security features.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

import logging
from hypercorn.config import Config
from hypercorn.asyncio import serve
from app.config import server_config, security_config, features_config

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


async def main():
    """Main function to start production server with HTTP/2"""
    try:
        # Environment checks
        check_environment()

        # Configure Hypercorn
        config = Config()

        # Basic configuration
        config.bind = [f"{server_config.host}:{server_config.port}"]
        config.workers = server_config.workers

        # HTTP/2 configuration
        config.h2c_upgrade = True  # Allow HTTP/2 over cleartext
        config.h11_pass_raw_headers = True

        # Enable HTTP/2 when SSL is available
        if server_config.http2_enabled:
            logger.info("HTTP/2 support enabled")

        # SSL configuration
        if (
            server_config.ssl_enabled
            and server_config.ssl_cert_file
            and server_config.ssl_key_file
        ):
            if (
                server_config.ssl_cert_file.exists()
                and server_config.ssl_key_file.exists()
            ):
                config.certfile = str(server_config.ssl_cert_file)
                config.keyfile = str(server_config.ssl_key_file)
                logger.info(
                    f"🔒 SSL enabled with certificate: {server_config.ssl_cert_file}"
                )

                # Enable HTTP/2 with SSL
                if server_config.http2_enabled:
                    logger.info("HTTP/2 with SSL enabled")
            else:
                logger.warning("SSL certificate files not found, running without SSL")

        # Performance settings
        config.keep_alive_timeout = 30
        config.max_app_queue_size = 100
        config.backlog = 2048

        # Security settings
        config.accesslog = "-"  # Log to stdout
        config.errorlog = "-"

        # Import app after path setup
        from app.main import app

        logger.info("🚀 Starting Production FastAPI Server with HTTP/2")
        logger.info(f"   Host: {server_config.host}")
        logger.info(f"   Port: {server_config.port}")
        logger.info(f"   Workers: {server_config.workers}")
        logger.info(f"   SSL: {server_config.ssl_enabled}")
        logger.info(f"   HTTP/2: {server_config.http2_enabled}")
        logger.info(f"   Security: {features_config.security_enabled}")
        logger.info("Press Ctrl+C to stop the server")

        # Start server
        await serve(app, config)

    except KeyboardInterrupt:
        logger.info("⏹️ Production server stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start production server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
