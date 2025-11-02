#!/usr/bin/env python3
"""
FastAPI Server - Final Launcher
Simple and robust launcher for the FastAPI server
"""

import os
import sys
import uvicorn
from pathlib import Path
from typing import Any, Dict


def setup_environment():
    """Setup Python path"""
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))


def load_config():
    """Load configuration based on environment"""
    setup_environment()

    try:
        from .config import get_config

        # Set environment if not already set
        if "FASTAPI_ENV" not in os.environ:
            os.environ["FASTAPI_ENV"] = "development"

        config = get_config()
        config.create_directories()
        config.validate_config()
        return config
    except ImportError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)


def setup_ssl(config: Any) -> bool:
    """Setup SSL certificates"""
    if not config.SSL_ENABLED:
        return False

    try:
        from .ssl_utils import setup_ssl_certificates

        print("🔐 Setting up SSL certificates...")
        success, message = setup_ssl_certificates(
            certs_dir="certs",
            common_name="localhost",
            country="US",
            state="State",
            locality="City",
            organization="FastAPI Server",
            organizational_unit="IT",
            validity_days=365,
        )

        if success:
            print(f"✅ {message}")
            return True
        else:
            print(f"⚠️  {message}")
            return False

    except ImportError as e:
        print(f"⚠️  SSL setup failed: {e}")
        return False


def import_app():
    """Import FastAPI application"""
    try:
        from app.main import app

        return app
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        sys.exit(1)


def build_uvicorn_config(config: Any, ssl_enabled: bool) -> Dict[str, Any]:
    """Build uvicorn configuration"""
    uvicorn_config: Dict[str, Any] = {
        "host": config.HOST,
        "port": config.PORT,
        "reload": config.RELOAD,
        "log_level": config.LOG_LEVEL,
        "access_log": True,
    }

    if ssl_enabled and config.SSL_CERT_FILE and config.SSL_KEY_FILE:
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


def print_server_info(config: Any, ssl_enabled: bool) -> None:
    """Print server startup information"""
    protocol = "https" if ssl_enabled else "http"
    port_display = (
        str(config.PORT) if config.PORT != (443 if ssl_enabled else 80) else ""
    )
    base_url = f"{protocol}://localhost{':' + port_display if port_display else ''}"

    print("=" * 50)
    print("🚀 FastAPI Server")
    print("=" * 50)
    print(f"Host: {config.HOST}")
    print(f"Port: {config.PORT}")
    print(f"Protocol: {protocol.upper()}")
    print(f"SSL: {'✅ Enabled' if ssl_enabled else '❌ Disabled'}")
    print(f"Environment: {os.environ.get('FASTAPI_ENV', 'default')}")
    print(f"Documentation: {base_url}/docs")
    print(f"Health Check: {base_url}/api/health")
    print("=" * 50)


def main():
    """Main launcher function"""
    print("🚀 Starting FastAPI Server...")

    # Load configuration
    config = load_config()

    # Setup SSL
    ssl_enabled = config.SSL_ENABLED and setup_ssl(config)

    # Import application
    app = import_app()

    # Print server info
    print_server_info(config, ssl_enabled)

    # Build uvicorn config
    uvicorn_config = build_uvicorn_config(config, ssl_enabled)

    # Start server
    try:
        if uvicorn_config.get("reload"):
            uvicorn.run("app.main:app", **uvicorn_config)
        else:
            uvicorn.run(app, **uvicorn_config)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
