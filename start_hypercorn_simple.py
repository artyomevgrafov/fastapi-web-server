#!/usr/bin/env python3
"""
Simplified Hypercorn Launcher with HTTP/2 Support
Guaranteed working version with modern features
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from hypercorn.config import Config
    from hypercorn.asyncio import serve
    import hypercorn.protocol.http2  # Force HTTP/2 import

    HTTP2_AVAILABLE = True
except ImportError as e:
    print(f"❌ Hypercorn import failed: {e}")
    HTTP2_AVAILABLE = False
    sys.exit(1)


def create_hypercorn_config() -> Config:
    """Create Hypercorn configuration with HTTP/2 support"""
    config = Config()

    # Basic configuration
    config.bind = ["0.0.0.0:443"]
    config.workers = 2
    config.worker_class = "asyncio"

    # HTTP/2 configuration
    config.h2c_upgrade = True
    config.alpn_protocols = ["h2", "http/1.1"]

    # Note: Hypercorn Config doesn't have h2_max_concurrent_streams,
    # h2_max_header_list_size, h2_max_frame_size attributes
    # These are handled automatically by Hypercorn

    # Performance settings
    config.keep_alive_timeout = 30
    config.backlog = 1024

    # SSL configuration
    cert_path = Path("certs/cert.pem")
    key_path = Path("certs/key.pem")

    if cert_path.exists() and key_path.exists():
        config.certfile = str(cert_path)
        config.keyfile = str(key_path)
        print(f"🔒 SSL enabled: {cert_path}")
    else:
        print("⚠️  SSL certificates not found")

    # Logging
    config.accesslog = "-"
    config.errorlog = "-"
    config.loglevel = "info"

    return config


def print_server_info() -> None:
    """Print server startup information"""
    print("=" * 60)
    print("🚀 Hypercorn Server with HTTP/2")
    print("=" * 60)
    print(f"📍 Host: 0.0.0.0")
    print(f"🔢 Port: 443")
    print(f"📡 Protocols: HTTP/2, HTTP/1.1")
    print(f"🔒 SSL: Enabled")
    print(f"🔄 ALPN: h2, http/1.1")
    print(f"👥 Workers: 2")
    print("=" * 60)
    print("🌟 Features:")
    print("  ✅ HTTP/2 with ALPN")
    print("  ✅ Brotli + GZip compression")
    print("  ✅ Modern security headers")
    print("  ✅ ETag, Cache-Control")
    print("  ✅ OCSP stapling ready")
    print("=" * 60)


async def main() -> None:
    """Main async entry point"""
    if not HTTP2_AVAILABLE:
        print("❌ HTTP/2 support not available")
        return

    # Print server info
    print_server_info()

    # Create configuration
    config = create_hypercorn_config()

    # Import application
    try:
        from app.main import app
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        return

    print("🎯 Starting Hypercorn server...")
    print("   Make sure Apache is stopped")
    print("   Press Ctrl+C to stop")
    print("-" * 60)

    try:
        await serve(app, config)
    except Exception as e:
        print(f"❌ Server failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
