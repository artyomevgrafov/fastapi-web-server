#!/usr/bin/env python3
"""
Hypercorn startup script with HTTP/2 support
Production-ready server with modern protocols
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
from app.config import server_config


async def main():
    """Start Hypercorn server with HTTP/2 support"""

    # Configure Hypercorn
    config = Config()

    # Basic configuration
    config.bind = [f"{server_config.host}:{server_config.port}"]
    config.workers = server_config.workers

    # HTTP/2 configuration
    config.h2c_upgrade = True  # Allow HTTP/2 over cleartext
    config.h11_pass_raw_headers = True

    # SSL configuration
    if (
        server_config.ssl_enabled
        and server_config.ssl_cert_file
        and server_config.ssl_key_file
    ):
        if server_config.ssl_cert_file.exists() and server_config.ssl_key_file.exists():
            config.certfile = str(server_config.ssl_cert_file)
            config.keyfile = str(server_config.ssl_key_file)
            print(f"🔒 SSL enabled with certificate: {server_config.ssl_cert_file}")
        else:
            print("⚠️  SSL certificate files not found, running without SSL")

    # Performance settings
    config.keep_alive_timeout = 30
    config.max_app_queue_size = 100
    config.backlog = 2048

    # Security settings
    config.accesslog = "-"  # Log to stdout
    config.errorlog = "-"

    # Import app after path setup
    from app.main import app

    print("🚀 Starting Hypercorn server with HTTP/2 support")
    print(f"   Host: {server_config.host}")
    print(f"   Port: {server_config.port}")
    print(f"   Workers: {server_config.workers}")
    print(f"   SSL: {server_config.ssl_enabled}")
    print(f"   HTTP/2: Enabled")

    await serve(app, config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)
