import os
from pathlib import Path
from typing import Any, Union, Dict, List


class ServerConfig:
    """Configuration class for FastAPI server settings / Класс конфигурации для настроек сервера FastAPI"""

    # Server settings / Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = (
        False  # Auto-reload for development / Автоперезагрузка для разработки
    )
    LOG_LEVEL: str = "info"

    # Paths / Пути
    BASE_DIR: Path = Path(__file__).parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # API settings / Настройки API
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # Security settings / Настройки безопасности
    CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]

    # Performance settings / Настройки производительности
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    TIMEOUT: int = 60  # seconds / секунды

    # Database settings (for future use) / Настройки базы данных (для будущего использования)
    DATABASE_URL: str = "sqlite:///./app.db"

    # SSL/TLS settings / Настройки SSL/TLS
    SSL_ENABLED: bool = False
    SSL_CERT_FILE: str = ""
    SSL_KEY_FILE: str = ""
    SSL_CERT_PASSWORD: str | None = None
    SSL_VERIFY_MODE: str | None = None
    SSL_CA_FILE: str | None = None

    @classmethod
    def get_uvicorn_config(cls) -> Dict[str, Union[str, int, bool, None]]:
        """Get uvicorn configuration dictionary / Получить словарь конфигурации uvicorn"""
        config: Dict[str, Union[str, int, bool, None]] = {
            "host": cls.HOST,
            "port": cls.PORT,
            "reload": cls.RELOAD,
            "log_level": cls.LOG_LEVEL,
            "access_log": True,
        }

        # Add SSL configuration if enabled / Добавить SSL конфигурацию если включена
        if cls.SSL_ENABLED and cls.SSL_CERT_FILE and cls.SSL_KEY_FILE:
            ssl_config: Dict[str, Union[str, int, bool, None]] = {
                "ssl_certfile": cls.SSL_CERT_FILE,
                "ssl_keyfile": cls.SSL_KEY_FILE,
                "ssl_keyfile_password": cls.SSL_CERT_PASSWORD,
                "ssl_ca_certs": cls.SSL_CA_FILE,
            }
            # Filter out None values / Отфильтровать значения None
            ssl_config = {k: v for k, v in ssl_config.items() if v is not None}
            config.update(ssl_config)

        return config

    @classmethod
    def get_fastapi_config(cls) -> Dict[str, str]:
        """Get FastAPI configuration dictionary / Получить словарь конфигурации FastAPI"""
        return {
            "title": "FastAPI Web Server",
            "description": "FastAPI server replacing Apache HTTP Server",
            "version": "1.0.0",
            "docs_url": cls.DOCS_URL,
            "redoc_url": cls.REDOC_URL,
        }

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist / Создать необходимые директории если они не существуют"""
        directories = [cls.STATIC_DIR, cls.TEMPLATES_DIR, cls.LOGS_DIR]
        for directory in directories:
            directory.mkdir(exist_ok=True)

    @classmethod
    def validate_config(cls) -> None:
        """Validate configuration settings / Проверить настройки конфигурации"""
        if cls.PORT < 1 or cls.PORT > 65535:
            raise ValueError(f"Invalid port number: {cls.PORT}")

        if not cls.STATIC_DIR.exists():
            cls.STATIC_DIR.mkdir(parents=True, exist_ok=True)

        if not cls.TEMPLATES_DIR.exists():
            cls.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


# Development configuration / Конфигурация разработки
class DevelopmentConfig(ServerConfig):
    """Development-specific configuration / Конфигурация для разработки"""

    RELOAD: bool = True
    LOG_LEVEL: str = "debug"
    SSL_ENABLED: bool = True
    SSL_CERT_FILE: str = "certs/cert.pem"
    SSL_KEY_FILE: str = "certs/key.pem"


# Production configuration / Конфигурация продакшена
class ProductionConfig(ServerConfig):
    """Production-specific configuration / Конфигурация для продакшена"""

    RELOAD: bool = False
    LOG_LEVEL: str = "warning"
    PORT: int = 8443  # Default to HTTPS port for production / По умолчанию HTTPS порт для продакшена
    SSL_ENABLED: bool = True
    SSL_CERT_FILE: str = "certs/cert.pem"
    SSL_KEY_FILE: str = "certs/key.pem"


# Configuration mapping / Сопоставление конфигураций
configs: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": ServerConfig,
}


def get_config(env: Union[str, None] = None) -> ServerConfig:
    """Get configuration based on environment / Получить конфигурацию на основе окружения"""
    if env is None:
        env = os.getenv("FASTAPI_ENV", "default")

    config_class = configs.get(env, configs["default"])
    return config_class()
