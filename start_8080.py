#!/usr/bin/env python3
"""
FastAPI Server - Port 8080 Launcher
Simple and robust launcher for the FastAPI server on port 8080
"""

import os
import sys
import uvicorn
from pathlib import Path


def setup_environment():
    """Setup Python path"""
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))


def load_config():
    """Load configuration for port 8080"""
    setup_environment()

    try:
        from config_8080 import get_config_8080

        # Set environment if not already set
        if "FASTAPI_ENV" not in os.environ:
            os.environ["FASTAPI_ENV"] = "development"

        config = get_config_8080()
        config.create_directories()
        config.validate_config()
        return config
    except ImportError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ SSL certificate error: {e}")
        print("Please run certificate synchronization first:")
        print(
            'powershell -ExecutionPolicy Bypass -File "C:\\server\\httpd\\win-acme\\sync-certs.ps1"'
        )
        sys.exit(1)


def import_app():
    """Import FastAPI application"""
    try:
        from app.main import app

        return app
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        sys.exit(1)


def build_uvicorn_config(config) -> dict[str, str | int | bool]:
    """Build uvicorn configuration"""
    uvicorn_config: dict[str, str | int | bool] = {
        "host": config.HOST,
        "port": config.PORT,
        "reload": config.RELOAD,
        "log_level": config.LOG_LEVEL,
        "access_log": True,
    }

    if config.SSL_ENABLED and config.SSL_CERT_FILE and config.SSL_KEY_FILE:
        uvicorn_config.update(
            {
                "ssl_certfile": config.SSL_CERT_FILE,
                "ssl_keyfile": config.SSL_KEY_FILE,
            }
        )

        if config.SSL_CERT_PASSWORD:
            uvicorn_config["ssl_keyfile_password"] = config.SSL_CERT_PASSWORD
        if config.SSL_CA_FILE:
            uvicorn_config["ssl_ca_certs"] = config.SSL_CA_FILE

    return uvicorn_config


def print_server_info(config):
    """Print server startup information"""
    protocol = "https" if config.SSL_ENABLED else "http"
    port_display = (
        config.PORT if config.PORT != (443 if config.SSL_ENABLED else 80) else ""
    )
    base_url = (
        f"{protocol}://localhost{':' + str(port_display) if port_display else ''}"
    )

    print("=" * 60)
    print("🚀 FastAPI Server - Port 8080")
    print("=" * 60)
    print(f"Host: {config.HOST}")
    print(f"Port: {config.PORT}")
    print(f"Protocol: {protocol.upper()}")
    print(f"SSL: {'✅ Enabled' if config.SSL_ENABLED else '❌ Disabled'}")
    print(f"Environment: {os.environ.get('FASTAPI_ENV', 'default')}")
    print(f"Documentation: {base_url}/docs")
    print(f"Health Check: {base_url}/api/health")
    print(f"Web Interface: {base_url}/")
    print("=" * 60)
    print("📋 Server Capabilities:")
    print("  ✅ Full web server functionality")
    print("  ✅ SSL/TLS encryption")
    print("  ✅ Static file serving")
    print("  ✅ API endpoints")
    print("  ✅ Automatic documentation")
    print("  ✅ Reverse proxy ready")
    print("=" * 60)


def check_ssl_certificates():
    """Check if SSL certificates exist"""
    cert_path = Path("certs/cert.pem")
    key_path = Path("certs/key.pem")

    if not cert_path.exists() or not key_path.exists():
        print("⚠️  SSL certificates not found in certs/ directory")
        print("Please run certificate synchronization:")
        print(
            'powershell -ExecutionPolicy Bypass -File "C:\\server\\httpd\\win-acme\\sync-certs.ps1"'
        )
        return False

    # Check if files are not empty
    cert_size = cert_path.stat().st_size
    key_size = key_path.stat().st_size

    if cert_size == 0 or key_size == 0:
        print("❌ SSL certificate files are empty")
        return False

    print(f"✅ SSL certificates found (cert: {cert_size} bytes, key: {key_size} bytes)")
    return True


def main():
    """Main launcher function"""
    print("🚀 Starting FastAPI Server on Port 8080...")

    # Load configuration
    config = load_config()

    # Check SSL certificates
    if config.SSL_ENABLED:
        if not check_ssl_certificates():
            print("❌ SSL certificate check failed")
            sys.exit(1)

    # Import application
    app = import_app()

    # Print server info
    print_server_info(config)

    # Build uvicorn config
    uvicorn_config = build_uvicorn_config(config)

    # Start server
    try:
        print(f"🎯 Starting server on {config.HOST}:{config.PORT}...")
        if uvicorn_config.get("reload"):
            uvicorn.run("app.main:app", **uvicorn_config)  # type: ignore[arg-type]
        else:
            uvicorn.run(app, **uvicorn_config)  # type: ignore[arg-type]
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
