#!/usr/bin/env python3
"""
FastAPI Server - Port 443 Launcher
Production launcher for FastAPI server on standard HTTPS port 443
"""

import os
import sys
import uvicorn
from pathlib import Path
from typing import TypedDict, Union

# Import message constants / Импорт констант сообщений
from app.messages import (
    CONFIG_LOAD_ERROR,
    SSL_CERT_ERROR,
    SSL_CERT_NOT_FOUND,
    SSL_KEY_NOT_FOUND,
    SSL_CERT_EMPTY,
    SSL_KEY_EMPTY,
    SSL_CERTS_FOUND,
    STARTING_SERVER,
    ADMIN_PRIVILEGES_REQUIRED,
    PORT_IN_USE,
    SSL_CHECK_FAILED,
    STARTING_PRODUCTION,
    APACHE_STOP_WARNING,
    SERVER_STOPPED,
    SERVER_ERROR,
    IMPORT_ERROR,
    SERVER_TITLE,
    FEATURE_WEB_SERVER,
    FEATURE_SSL,
    FEATURE_STATIC,
    FEATURE_API,
    FEATURE_DOCS,
    FEATURE_APACHE_REPLACE,
    STATUS_ENABLED,
    STATUS_DISABLED,
)


def setup_environment():
    """Setup Python path / Настройка пути Python"""
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))


def load_config():
    """Load configuration for port 443 / Загрузка конфигурации для порта 443"""
    setup_environment()

    try:
        from config_443 import get_config_443

        # Set environment if not already set / Установка окружения если не установлено
        if "FASTAPI_ENV" not in os.environ:
            os.environ["FASTAPI_ENV"] = "production"

        config = get_config_443()
        config.create_directories()
        config.validate_config()
        return config
    except ImportError as e:
        print(CONFIG_LOAD_ERROR.format(e))
        sys.exit(1)
    except FileNotFoundError as e:
        print(SSL_CERT_ERROR.format(e))
        print("Please run certificate synchronization first:")
        print(
            'powershell -ExecutionPolicy Bypass -File "C:\\server\\httpd\\win-acme\\sync-certs.ps1"'
        )
        sys.exit(1)


def import_app():
    """Import FastAPI application / Импорт FastAPI приложения"""
    try:
        from app.main import app

        return app
    except ImportError as e:
        print(IMPORT_ERROR.format(e))
        sys.exit(1)


def check_administrator_privileges():
    """Check if running with administrator privileges / Проверка прав администратора"""
    try:
        import ctypes

        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def check_port_availability(port=443):
    """Check if port is available / Проверка доступности порта"""
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", port))
            return True
    except OSError:
        return False


def check_ssl_certificates():
    """Check if SSL certificates exist and are valid / Проверка существования и валидности SSL сертификатов"""
    cert_path = Path("certs/cert.pem")
    key_path = Path("certs/key.pem")

    if not cert_path.exists():
        print(SSL_CERT_NOT_FOUND.format(cert_path))
        return False

    if not key_path.exists():
        print(SSL_KEY_NOT_FOUND.format(key_path))
        return False

    # Check if files are not empty / Проверка что файлы не пустые
    cert_size = cert_path.stat().st_size
    key_size = key_path.stat().st_size

    if cert_size == 0:
        print(SSL_CERT_EMPTY)
        return False

    if key_size == 0:
        print(SSL_KEY_EMPTY)
        return False

    print(SSL_CERTS_FOUND.format(cert_size, key_size))
    return True


class UvicornConfig(TypedDict, total=False):
    host: str
    port: int
    reload: bool
    log_level: str
    access_log: bool
    ssl_certfile: Union[str, Path]
    ssl_keyfile: Union[str, Path]
    ssl_keyfile_password: str | None
    ssl_ca_certs: str | None


def build_uvicorn_config(config) -> UvicornConfig:
    """Build uvicorn configuration / Создание конфигурации uvicorn"""
    uvicorn_config: UvicornConfig = {
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
    """Print server startup information / Вывод информации о запуске сервера"""
    protocol = "https" if config.SSL_ENABLED else "http"
    base_url = f"{protocol}://localhost"

    print("=" * 70)
    print(SERVER_TITLE + " - Production (Port 443)")
    print("=" * 70)
    print(f"Host: {config.HOST}")
    print(f"Port: {config.PORT} (Standard HTTPS)")
    print(f"Protocol: {protocol.upper()}")
    print(f"SSL: {STATUS_ENABLED if config.SSL_ENABLED else STATUS_DISABLED}")
    print(f"Environment: {os.environ.get('FASTAPI_ENV', 'production')}")
    print(f"Documentation: {base_url}/docs")
    print(f"Health Check: {base_url}/api/health")
    print(f"Web Interface: {base_url}/")
    print("=" * 70)
    print("Production Features:")
    print(f"  {FEATURE_WEB_SERVER}")
    print(f"  {FEATURE_SSL}")
    print(f"  {FEATURE_STATIC}")
    print(f"  {FEATURE_API}")
    print(f"  {FEATURE_DOCS}")
    print(f"  {FEATURE_APACHE_REPLACE}")
    print("=" * 70)


def main():
    """Main launcher function / Основная функция запуска"""
    print(STARTING_SERVER)

    # Check administrator privileges / Проверка прав администратора
    if not check_administrator_privileges():
        print(ADMIN_PRIVILEGES_REQUIRED)
        print("Please run this script as Administrator")
        sys.exit(1)

    # Check if port 443 is available / Проверка доступности порта 443
    if not check_port_availability(443):
        print(PORT_IN_USE)
        print("Please stop Apache or other services using port 443")
        sys.exit(1)

    # Load configuration / Загрузка конфигурации
    config = load_config()

    # Check SSL certificates / Проверка SSL сертификатов
    if not check_ssl_certificates():
        print(SSL_CHECK_FAILED)
        sys.exit(1)

    # Import application / Импорт приложения
    app = import_app()

    # Print server info / Вывод информации о сервере
    print_server_info(config)

    # Build uvicorn config / Создание конфигурации uvicorn
    uvicorn_config = build_uvicorn_config(config)

    # Start server / Запуск сервера
    try:
        print(STARTING_PRODUCTION.format(config.HOST, config.PORT))
        print(APACHE_STOP_WARNING)
        print("Press Ctrl+C to stop the server")
        print("-" * 70)

        if uvicorn_config.get("reload"):
            uvicorn.run("app.main:app", **uvicorn_config)
        else:
            uvicorn.run(app, **uvicorn_config)
    except KeyboardInterrupt:
        print("\n" + SERVER_STOPPED)
    except Exception as e:
        print(SERVER_ERROR.format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
