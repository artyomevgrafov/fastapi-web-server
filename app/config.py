"""
Configuration module using Pydantic Settings with environment variables support
Модуль конфигурации с использованием Pydantic Settings и поддержкой переменных окружения
"""

import os
from typing import Dict, Set, List, Optional
from pathlib import Path
from pydantic import BaseSettings, Field, validator
from pydantic.networks import AnyHttpUrl


class SecurityConfig(BaseSettings):
    """Security configuration settings / Настройки конфигурации безопасности"""

    # IP blocking settings / Настройки блокировки IP
    ip_blocking_enabled: bool = Field(default=True, env="IP_BLOCKING_ENABLED")
    block_duration: int = Field(default=3600, env="BLOCK_DURATION")  # seconds / секунды
    auto_block_suspicious: bool = Field(default=True, env="AUTO_BLOCK_SUSPICIOUS")
    max_blocked_ips: int = Field(default=1000, env="MAX_BLOCKED_IPS")

    # Rate limiting settings / Настройки ограничения скорости
    rate_limiting_enabled: bool = Field(default=True, env="RATE_LIMITING_ENABLED")
    max_requests_per_minute: int = Field(default=100, env="MAX_REQUESTS_PER_MINUTE")
    max_requests_per_hour: int = Field(default=1000, env="MAX_REQUESTS_PER_HOUR")
    burst_protection: bool = Field(default=True, env="BURST_PROTECTION")
    burst_window: int = Field(default=10, env="BURST_WINDOW")  # seconds / секунды
    burst_max_requests: int = Field(default=50, env="BURST_MAX_REQUESTS")

    # Threat detection settings / Настройки обнаружения угроз
    threat_detection_enabled: bool = Field(default=True, env="THREAT_DETECTION_ENABLED")
    suspicious_request_threshold: int = Field(
        default=5, env="SUSPICIOUS_REQUEST_THRESHOLD"
    )
    enable_attack_analysis: bool = Field(default=True, env="ENABLE_ATTACK_ANALYSIS")
    threat_score_threshold: int = Field(default=10, env="THREAT_SCORE_THRESHOLD")
    auto_block_high_threat: bool = Field(default=True, env="AUTO_BLOCK_HIGH_THREAT")

    # Monitoring and logging settings / Настройки мониторинга и логирования
    enable_detailed_logging: bool = Field(default=True, env="ENABLE_DETAILED_LOGGING")
    log_rotation_hours: int = Field(default=24, env="LOG_ROTATION_HOURS")
    max_log_files: int = Field(default=7, env="MAX_LOG_FILES")
    alert_on_major_attacks: bool = Field(default=True, env="ALERT_ON_MAJOR_ATTACKS")
    enable_real_time_alerts: bool = Field(default=False, env="ENABLE_REAL_TIME_ALERTS")

    # Advanced security settings / Расширенные настройки безопасности
    enable_geo_blocking: bool = Field(default=False, env="ENABLE_GEO_BLOCKING")
    enable_tor_blocking: bool = Field(default=True, env="ENABLE_TOR_BLOCKING")
    enable_proxy_blocking: bool = Field(default=True, env="ENABLE_PROXY_BLOCKING")
    enable_bot_protection: bool = Field(default=True, env="ENABLE_BOT_PROTECTION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ServerConfig(BaseSettings):
    """Server configuration settings / Настройки конфигурации сервера"""

    target_server: AnyHttpUrl = Field(
        default="http://127.0.0.1:8097", env="TARGET_SERVER"
    )
    timeout: float = Field(default=30.0, env="TIMEOUT")
    static_root: Path = Field(
        default=Path("C:/server/httpd/data/htdocs"), env="STATIC_ROOT"
    )
    ssl_enabled: bool = Field(default=True, env="SSL_ENABLED")
    ssl_cert_file: Optional[Path] = Field(default=None, env="SSL_CERT_FILE")
    ssl_key_file: Optional[Path] = Field(default=None, env="SSL_KEY_FILE")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=443, env="PORT")

    # HTTP/2 and performance settings / Настройки HTTP/2 и производительности
    http2_enabled: bool = Field(default=True, env="HTTP2_ENABLED")
    workers: int = Field(default=4, env="WORKERS")
    max_requests: int = Field(default=1000, env="MAX_REQUESTS")
    max_requests_jitter: int = Field(default=100, env="MAX_REQUESTS_JITTER")

    # Compression settings / Настройки сжатия
    gzip_enabled: bool = Field(default=True, env="GZIP_ENABLED")
    gzip_min_size: int = Field(default=500, env="GZIP_MIN_SIZE")
    brotli_enabled: bool = Field(default=False, env="BROTLI_ENABLED")

    @validator("static_root", pre=True)
    def validate_static_root(cls, v):
        """Validate static root path / Проверка пути к статическим файлам"""
        if isinstance(v, str):
            return Path(v)
        return v

    @validator("ssl_cert_file", "ssl_key_file", pre=True)
    def validate_ssl_paths(cls, v):
        """Validate SSL file paths / Проверка путей к SSL файлам"""
        if v and isinstance(v, str):
            return Path(v)
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class LoggingConfig(BaseSettings):
    """Logging configuration settings / Настройки конфигурации логирования"""

    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S", env="LOG_DATE_FORMAT")
    log_dir: Path = Field(default=Path("logs"), env="LOG_DIR")
    max_log_size: str = Field(default="10MB", env="MAX_LOG_SIZE")
    backup_count: int = Field(default=5, env="BACKUP_COUNT")

    @validator("log_dir", pre=True)
    def validate_log_dir(cls, v):
        """Validate log directory path / Проверка пути к директории логов"""
        if isinstance(v, str):
            return Path(v)
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class FeaturesConfig(BaseSettings):
    """Feature flags configuration / Конфигурация флагов функций"""

    security_enabled: bool = Field(default=True, env="SECURITY_ENABLED")
    monitoring_enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    rate_limiting_enabled: bool = Field(default=True, env="RATE_LIMITING_ENABLED")
    ip_blocking_enabled: bool = Field(default=True, env="IP_BLOCKING_ENABLED")
    threat_detection_enabled: bool = Field(default=True, env="THREAT_DETECTION_ENABLED")
    static_serving_enabled: bool = Field(default=True, env="STATIC_SERVING_ENABLED")
    api_proxy_enabled: bool = Field(default=True, env="API_PROXY_ENABLED")
    ssl_enabled: bool = Field(default=True, env="SSL_ENABLED")
    http2_enabled: bool = Field(default=True, env="HTTP2_ENABLED")
    gzip_enabled: bool = Field(default=True, env="GZIP_ENABLED")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instances / Глобальные экземпляры конфигурации
security_config = SecurityConfig()
server_config = ServerConfig()
logging_config = LoggingConfig()
features_config = FeaturesConfig()


# Suspicious patterns (not environment-based) / Подозрительные паттерны (не на основе окружения)
SUSPICIOUS_PATTERNS = {
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
WHITELIST = {
    "enabled": False,
    "ips": set(),  # Add trusted IPs here / Добавьте доверенные IP-адреса здесь
    "user_agents": set(),  # Add trusted user agents here / Добавьте доверенные user agents здесь
}

# Allowed search engine bots / Разрешенные поисковые боты
ALLOWED_BOTS = {
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


def get_config() -> Dict:
    """
    Get complete configuration as dictionary / Получить полную конфигурацию в виде словаря
    """
    return {
        "security": security_config.dict(),
        "server": server_config.dict(),
        "logging": logging_config.dict(),
        "features": features_config.dict(),
        "patterns": SUSPICIOUS_PATTERNS,
        "malicious_ranges": MALICIOUS_RANGES,
        "whitelist": WHITELIST,
        "allowed_bots": ALLOWED_BOTS,
    }


def update_config_from_env():
    """
    Reload configuration from environment variables / Перезагрузить конфигурацию из переменных окружения
    """
    global security_config, server_config, logging_config, features_config
    security_config = SecurityConfig()
    server_config = ServerConfig()
    logging_config = LoggingConfig()
    features_config = FeaturesConfig()


# Backward compatibility aliases / Псевдонимы для обратной совместимости
SECURITY_CONFIG = security_config.dict()
SERVER_CONFIG = server_config.dict()
LOGGING_CONFIG = logging_config.dict()
FEATURES = features_config.dict()
