"""
Configuration module using Pydantic Settings with environment variables support
Модуль конфигурации с использованием Pydantic Settings и поддержкой переменных окружения
"""

from typing import Dict, Set, List, Optional, Any
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecurityConfig(BaseSettings):
    """Security configuration settings / Настройки конфигурации безопасности"""

    # IP blocking settings / Настройки блокировки IP
    ip_blocking_enabled: bool = Field(default=True)
    block_duration: int = Field(default=3600)  # seconds / секунды
    auto_block_suspicious: bool = Field(default=True)
    max_blocked_ips: int = Field(default=1000)

    # Rate limiting settings / Настройки ограничения скорости
    rate_limiting_enabled: bool = Field(default=True)
    max_requests_per_minute: int = Field(default=100)
    max_requests_per_hour: int = Field(default=1000)
    burst_protection: bool = Field(default=True)
    burst_window: int = Field(default=10)  # seconds / секунды
    burst_max_requests: int = Field(default=50)

    # Threat detection settings / Настройки обнаружения угроз
    threat_detection_enabled: bool = Field(default=True)
    suspicious_request_threshold: int = Field(default=5)
    enable_attack_analysis: bool = Field(default=True)
    threat_score_threshold: int = Field(default=10)
    auto_block_high_threat: bool = Field(default=True)

    # Monitoring and logging settings / Настройки мониторинга и логирования
    enable_detailed_logging: bool = Field(default=True)
    log_rotation_hours: int = Field(default=24)
    max_log_files: int = Field(default=7)
    alert_on_major_attacks: bool = Field(default=True)
    enable_real_time_alerts: bool = Field(default=False)

    # Advanced security settings / Расширенные настройки безопасности
    enable_geo_blocking: bool = Field(default=False)
    enable_tor_blocking: bool = Field(default=True)
    enable_proxy_blocking: bool = Field(default=True)
    enable_bot_protection: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class ServerConfig(BaseSettings):
    """Server configuration settings / Настройки конфигурации сервера"""

    target_server: str = Field(default="http://127.0.0.1:8097")
    timeout: float = Field(default=30.0)
    static_root: Path = Field(default=Path("C:/server/httpd/data/htdocs"))
    ssl_enabled: bool = Field(default=True)
    ssl_cert_file: Optional[Path] = Field(default=None)
    ssl_key_file: Optional[Path] = Field(default=None)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=443)

    # HTTP/2 and performance settings / Настройки HTTP/2 и производительности
    http2_enabled: bool = Field(default=True)
    workers: int = Field(default=4)
    max_requests: int = Field(default=1000)
    max_requests_jitter: int = Field(default=100)

    # Compression settings / Настройки сжатия
    gzip_enabled: bool = Field(default=True)
    gzip_min_size: int = Field(default=500)
    brotli_enabled: bool = Field(default=False)

    @field_validator("static_root", mode="before")
    @classmethod
    def validate_static_root(cls, v: Any) -> Path:
        """Validate static root path / Проверка пути к статическим файлам"""
        if isinstance(v, str):
            return Path(v)
        return v

    @field_validator("ssl_cert_file", "ssl_key_file", mode="before")
    @classmethod
    def validate_ssl_paths(cls, v: Any) -> Optional[Path]:
        """Validate SSL file paths / Проверка путей к SSL файлам"""
        if v and isinstance(v, str):
            return Path(v)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class LoggingConfig(BaseSettings):
    """Logging configuration settings / Настройки конфигурации логирования"""

    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S")
    log_dir: Path = Field(default=Path("logs"))
    max_log_size: str = Field(default="10MB")
    backup_count: int = Field(default=5)

    @field_validator("log_dir", mode="before")
    @classmethod
    def validate_log_dir(cls, v: Any) -> Path:
        """Validate log directory path / Проверка пути к директории логов"""
        if isinstance(v, str):
            return Path(v)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


class FeaturesConfig(BaseSettings):
    """Feature flags configuration / Конфигурация флагов функций"""

    security_enabled: bool = Field(default=True)
    monitoring_enabled: bool = Field(default=True)
    rate_limiting_enabled: bool = Field(default=True)
    ip_blocking_enabled: bool = Field(default=True)
    threat_detection_enabled: bool = Field(default=True)
    static_serving_enabled: bool = Field(default=True)
    api_proxy_enabled: bool = Field(default=True)
    ssl_enabled: bool = Field(default=True)
    http2_enabled: bool = Field(default=True)
    gzip_enabled: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global configuration instances / Глобальные экземпляры конфигурации
security_config: SecurityConfig = SecurityConfig()
server_config: ServerConfig = ServerConfig()
logging_config: LoggingConfig = LoggingConfig()
features_config: FeaturesConfig = FeaturesConfig()


# Suspicious patterns (not environment-based) / Подозрительные паттерны (не на основе окружения)
SUSPICIOUS_PATTERNS: Dict[str, Set[str]] = {
    # Common attack paths / Общие пути атак
    "paths": {
        ".env",
        ".git/config",
        ".git/HEAD",
        ".git/credentials",
        "admin/config.php",
        "phpinfo.php",
        "info.php",
        "phpinfo",
        "config.json",
        "client_secrets.json",
        "appsettings.json",
        "actuator/env",
        "actuator/health",
        "debug/default/view",
        "v2/_catalog",
        "_all_dbs",
        "server-status",
        "owa/auth/logon.aspx",
        "ecp/Current/exporttool/",
        "+CSCOL+/",
        "+CSCOE+/",
        "cgi-bin/luci/",
        "vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php",
        "_profiler/phpinfo",
        "web/debug/default/view",
        ".well-known/security.txt",
        "sitemap.xml",
        "robots.txt",
        "login",
        "login.action",
        "admin",
        "wp-admin",
        "backup",
        "backup.zip",
        "dump.sql",
        "database.sql",
        "config.php",
        "settings.php",
        "wp-config.php",
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
    },
    # Suspicious file extensions / Подозрительные расширения файлов
    "extensions": {
        ".env",
        ".bak",
        ".old",
        ".backup",
        ".dist",
        ".example",
        ".pem",
        ".key",
        ".cert",
        ".crt",
        ".pfx",
        ".p12",
        ".sql",
        ".dump",
        ".back",
        ".save",
        ".log",
        ".txt",
        ".ini",
        ".conf",
        ".cfg",
        ".yml",
        ".yaml",
        ".json",
        ".xml",
        ".php",
        ".asp",
        ".aspx",
        ".jsp",
        ".py",
        ".rb",
    },
    # Suspicious parameters / Подозрительные параметры
    "params": {
        "cmd",
        "exec",
        "system",
        "eval",
        "shell",
        "bash",
        "php",
        "python",
        "perl",
        "ruby",
        "javascript",
        "union",
        "select",
        "insert",
        "update",
        "delete",
        "drop",
        "create",
        "alter",
        "truncate",
        "script",
        "alert",
        "document.cookie",
        "onload",
        "onerror",
        "onclick",
        "onmouseover",
    },
}

# Known malicious IP ranges / Известные вредоносные диапазоны IP
MALICIOUS_RANGES: List[str] = []

# Whitelist settings / Настройки белого списка
WHITELIST: Dict[str, Any] = {
    "enabled": False,
    "ips": set(),  # Add trusted IPs here / Добавьте доверенные IP-адреса здесь
    "user_agents": set(),  # Add trusted user agents here / Добавьте доверенные user agents здесь
}

# Allowed search engine bots / Разрешенные поисковые боты
ALLOWED_BOTS: Set[str] = {
    "googlebot",
    "bingbot",
    "slurp",
    "duckduckbot",
    "baiduspider",
    "yandexbot",
    "facebookexternalhit",
    "twitterbot",
    "linkedinbot",
}


def get_config() -> Dict[str, Any]:
    """
    Get complete configuration as dictionary / Получить полную конфигурацию в виде словаря
    """
    return {
        "security": security_config.model_dump(),
        "server": server_config.model_dump(),
        "logging": logging_config.model_dump(),
        "features": features_config.model_dump(),
        "patterns": SUSPICIOUS_PATTERNS,
        "malicious_ranges": MALICIOUS_RANGES,
        "whitelist": WHITELIST,
        "allowed_bots": ALLOWED_BOTS,
    }


def update_config_from_env() -> None:
    """
    Reload configuration from environment variables / Перезагрузить конфигурацию из переменных окружения
    """
    global security_config, server_config, logging_config, features_config
    security_config = SecurityConfig()
    server_config = ServerConfig()
    logging_config = LoggingConfig()
    features_config = FeaturesConfig()


# Backward compatibility aliases / Псевдонимы для обратной совместимости
SECURITY_CONFIG: Dict[str, Any] = security_config.model_dump()
SERVER_CONFIG: Dict[str, Any] = server_config.model_dump()
LOGGING_CONFIG: Dict[str, Any] = logging_config.model_dump()
FEATURES: Dict[str, Any] = features_config.model_dump()
