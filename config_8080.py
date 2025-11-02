import os
from pathlib import Path
from typing import Any, Union


class ServerConfig8080:
    """Configuration class for FastAPI server on port 8080"""

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080  # Changed from default 8000 to 8080
    RELOAD: bool = False  # Auto-reload for development
    LOG_LEVEL: str = "info"

    # Paths
    BASE_DIR: Path = Path(__file__).parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # API settings
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # Security settings
    CORS_ORIGINS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "0.0.0.0"]

    # Performance settings
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    TIMEOUT: int = 60  # seconds

    # Database settings (for future use)
    DATABASE_URL: str = "sqlite:///./app.db"

    # SSL/TLS settings
    SSL_ENABLED: bool = True  # Enable SSL by default
    SSL_CERT_FILE: str = "certs/cert.pem"
    SSL_KEY_FILE: str = "certs/key.pem"
    SSL_CERT_PASSWORD: str | None = None
    SSL_VERIFY_MODE: str | None = None
    SSL_CA_FILE: str | None = None

    @classmethod
    def get_uvicorn_config(cls) -> dict[str, Union[str, int, bool, None]]:
        """Get uvicorn configuration dictionary"""
        config = {
            "host": cls.HOST,
            "port": cls.PORT,
            "reload": cls.RELOAD,
            "log_level": cls.LOG_LEVEL,
            "access_log": True,
        }

        # Add SSL configuration if enabled
        if cls.SSL_ENABLED and cls.SSL_CERT_FILE and cls.SSL_KEY_FILE:
            ssl_config: dict[str, Union[str, int, bool, None]] = {
                "ssl_certfile": cls.SSL_CERT_FILE,
                "ssl_keyfile": cls.SSL_KEY_FILE,
                "ssl_keyfile_password": cls.SSL_CERT_PASSWORD,
                "ssl_ca_certs": cls.SSL_CA_FILE,
            }
            # Filter out None values
            ssl_config = {k: v for k, v in ssl_config.items() if v is not None}
            config.update(ssl_config)

        return config

    @classmethod
    def get_fastapi_config(cls) -> dict[str, str]:
        """Get FastAPI configuration dictionary"""
        return {
            "title": "FastAPI Web Server - Port 8080",
            "description": "FastAPI server running on port 8080 with SSL support",
            "version": "1.0.0",
            "docs_url": cls.DOCS_URL,
            "redoc_url": cls.REDOC_URL,
        }

    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [cls.STATIC_DIR, cls.TEMPLATES_DIR, cls.LOGS_DIR]
        for directory in directories:
            directory.mkdir(exist_ok=True)

    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        if cls.PORT < 1 or cls.PORT > 65535:
            raise ValueError(f"Invalid port number: {cls.PORT}")

        if not cls.STATIC_DIR.exists():
            cls.STATIC_DIR.mkdir(parents=True, exist_ok=True)

        if not cls.TEMPLATES_DIR.exists():
            cls.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

        # Validate SSL certificate files exist if SSL is enabled
        if cls.SSL_ENABLED:
            if not Path(cls.SSL_CERT_FILE).exists():
                raise FileNotFoundError(
                    f"SSL certificate file not found: {cls.SSL_CERT_FILE}"
                )
            if not Path(cls.SSL_KEY_FILE).exists():
                raise FileNotFoundError(f"SSL key file not found: {cls.SSL_KEY_FILE}")


# Development configuration for port 8080
class DevelopmentConfig8080(ServerConfig8080):
    """Development-specific configuration for port 8080"""

    RELOAD: bool = True
    LOG_LEVEL: str = "debug"
    SSL_ENABLED: bool = True
    SSL_CERT_FILE: str = "certs/cert.pem"
    SSL_KEY_FILE: str = "certs/key.pem"


# Production configuration for port 8080
class ProductionConfig8080(ServerConfig8080):
    """Production-specific configuration for port 8080"""

    RELOAD: bool = False
    LOG_LEVEL: str = "warning"
    PORT: int = 8080  # Explicitly set to 8080
    SSL_ENABLED: bool = True
    SSL_CERT_FILE: str = "certs/cert.pem"
    SSL_KEY_FILE: str = "certs/key.pem"


# Configuration mapping for port 8080
configs_8080 = {
    "development": DevelopmentConfig8080,
    "production": ProductionConfig8080,
    "default": ServerConfig8080,
}


def get_config_8080(env: str | None = None) -> ServerConfig8080:
    """Get configuration for port 8080 based on environment"""
    if env is None:
        env = os.getenv("FASTAPI_ENV", "default")

    config_class = configs_8080.get(env, configs_8080["default"])
    return config_class()
