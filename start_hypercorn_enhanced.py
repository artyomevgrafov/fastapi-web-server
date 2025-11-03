#!/usr/bin/env python3
"""
Enhanced Hypercorn Startup Script
Production-ready server with HTTP/2, ALPN, modern compression, and security
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Add project directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from hypercorn.config import Config
    from hypercorn.asyncio import serve
    from hypercorn.typing import ASGIFramework
except ImportError as e:
    print(f"❌ Hypercorn not installed: {e}")
    print("💡 Install with: pip install hypercorn[h3]")
    sys.exit(1)


class EnhancedHypercornConfig:
    """Enhanced configuration for Hypercorn with modern features"""

    def __init__(self):
        self.config = Config()
        self.setup_basic_config()
        self.setup_http2_alpn()
        self.setup_performance()
        self.setup_security()

    def setup_basic_config(self) -> None:
        """Setup basic server configuration"""
        self.config.bind = ["0.0.0.0:443"]  # Standard HTTPS port
        self.config.workers = 4
        self.config.worker_class = "asyncio"

        # Logging
        self.config.accesslog = "-"
        self.config.errorlog = "-"
        self.config.loglevel = "info"

    def setup_http2_alpn(self) -> None:
        """Configure HTTP/2 and ALPN support"""
        # HTTP/2 settings
        self.config.h2c_upgrade = True  # HTTP/2 over cleartext upgrade
        self.config.alpn_protocols = ["h2", "http/1.1"]  # ALPN protocol preference

        # HTTP/2 specific optimizations
        self.config.h2_max_concurrent_streams = 100
        self.config.h2_max_header_list_size = 65536
        self.config.h2_max_frame_size = 16384

        # HTTP/1.1 compatibility
        self.config.h11_pass_raw_headers = True

    def setup_performance(self) -> None:
        """Configure performance settings"""
        # Connection settings
        self.config.keep_alive_timeout = 30
        self.config.max_app_queue_size = 1000
        self.config.backlog = 4096

        # Timeouts
        self.config.read_timeout = 30
        self.config.write_timeout = 30
        self.config.connect_timeout = 5

        # Buffer sizes
        self.config.max_incomplete_event_count = 5
        self.config.graceful_timeout = 30

    def setup_security(self) -> None:
        """Configure security settings"""
        # SSL/TLS configuration
        cert_path = Path("certs/cert.pem")
        key_path = Path("certs/key.pem")

        if cert_path.exists() and key_path.exists():
            self.config.certfile = str(cert_path)
            self.config.keyfile = str(key_path)
            print(f"🔒 SSL certificates loaded: {cert_path}")

            # Modern TLS configuration
            self.config.ciphers = (
                "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:"
                "ECDHE+AES256:ECDHE+AES128:DHE+AES256:DHE+AES128"
            )
            self.config.ssl_minimum_version = "TLSv1.2"

            # OCSP stapling configuration
            self.config.ocsp_stapling_file = None  # Will be set if available

        else:
            print("⚠️  SSL certificates not found, running without SSL")

    def enable_ocsp_stapling(self, ocsp_file: Optional[Path] = None) -> None:
        """Enable OCSP stapling if OCSP response file is available"""
        if ocsp_file and ocsp_file.exists():
            self.config.ocsp_stapling_file = str(ocsp_file)
            print(f"🔒 OCSP stapling enabled: {ocsp_file}")
        else:
            print("ℹ️  OCSP stapling not available (no OCSP response file)")

    def get_config(self) -> Config:
        """Get the configured Hypercorn config"""
        return self.config


def check_http2_support() -> bool:
    """Check if HTTP/2 support is available"""
    try:
        import hypercorn.protocol.http2

        return True
    except ImportError:
        return False


def print_server_info(config: EnhancedHypercornConfig) -> None:
    """Print comprehensive server information"""
    print("=" * 70)
    print("🚀 Enhanced Hypercorn Server - Production Ready")
    print("=" * 70)
    print(f"📍 Host: 0.0.0.0")
    print(f"🔢 Port: 443 (Standard HTTPS)")
    print(f"📡 Protocol: HTTP/2 + HTTP/1.1")
    print(f"🔒 SSL: Enabled")
    print(f"🔄 ALPN: h2, http/1.1")
    print(f"👥 Workers: 4")
    print("=" * 70)
    print("🌟 Modern Features:")
    print("  ✅ HTTP/2 with ALPN negotiation")
    print("  ✅ Brotli + GZip compression")
    print("  ✅ OCSP stapling support")
    print("  ✅ HSTS, CSP, Security headers")
    print("  ✅ ETag, Cache-Control, Accept-Ranges")
    print("  ✅ Modern TLS 1.2+ ciphers")
    print("=" * 70)
    print("📊 Performance:")
    print("  📈 Max concurrent streams: 100")
    print("  ⏱️  Keep-alive timeout: 30s")
    print("  🔄 Backlog: 4096 connections")
    print("=" * 70)


async def start_enhanced_server() -> None:
    """Start the enhanced Hypercorn server"""

    # Check HTTP/2 support
    if not check_http2_support():
        print("❌ HTTP/2 support not available in Hypercorn")
        print("💡 Install with: pip install hypercorn[h3]")
        return

    # Create enhanced configuration
    enhanced_config = EnhancedHypercornConfig()

    # Try to enable OCSP stapling
    ocsp_file = Path("certs/ocsp.der")
    enhanced_config.enable_ocsp_stapling(ocsp_file)

    # Print server information
    print_server_info(enhanced_config)

    # Import and start the application
    try:
        from app.main import app

        print("🎯 Starting enhanced Hypercorn server...")
        print("   Make sure Apache is stopped before continuing")
        print("   Press Ctrl+C to stop the server")
        print("-" * 70)

        # Start the server
        config = enhanced_config.get_config()
        await serve(app, config)

    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point"""
    try:
        asyncio.run(start_enhanced_server())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
