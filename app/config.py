"""
Security configuration file
Файл конфигурации безопасности
"""

from typing import Dict, Set, List
from pathlib import Path

# Security configuration / Конфигурация безопасности
SECURITY_CONFIG = {
    # IP blocking settings / Настройки блокировки IP
    "ip_blocking": {
        "enabled": True,
        "block_duration": 3600,  # seconds / секунды
        "auto_block_suspicious": True,
        "max_blocked_ips": 1000,
    },
    # Rate limiting settings / Настройки ограничения скорости
    "rate_limiting": {
        "enabled": True,
        "max_requests_per_minute": 100,
        "max_requests_per_hour": 1000,
        "burst_protection": True,
        "burst_window": 10,  # seconds / секунды
        "burst_max_requests": 50,
    },
    # Threat detection settings / Настройки обнаружения угроз
    "threat_detection": {
        "enabled": True,
        "suspicious_request_threshold": 5,
        "enable_attack_analysis": True,
        "threat_score_threshold": 10,
        "auto_block_high_threat": True,
    },
    # Monitoring and logging settings / Настройки мониторинга и логирования
    "monitoring": {
        "enable_detailed_logging": True,
        "log_rotation_hours": 24,
        "max_log_files": 7,
        "alert_on_major_attacks": True,
        "enable_real_time_alerts": False,
    },
    # Suspicious patterns / Подозрительные паттерны
    "suspicious_patterns": {
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
    },
    # Known malicious IP ranges / Известные вредоносные диапазоны IP
    "malicious_ranges": [
        # Add known malicious IP ranges here / Добавьте известные вредоносные диапазоны IP здесь
    ],
    # Whitelist settings / Настройки белого списка
    "whitelist": {
        "enabled": False,
        "ips": set(),  # Add trusted IPs here / Добавьте доверенные IP-адреса здесь
        "user_agents": set(),  # Add trusted user agents here / Добавьте доверенные user agents здесь
    },
    # Advanced security settings / Расширенные настройки безопасности
    "advanced": {
        "enable_geo_blocking": False,
        "blocked_countries": set(),  # Add country codes to block / Добавьте коды стран для блокировки
        "enable_tor_blocking": True,
        "enable_proxy_blocking": True,
        "enable_bot_protection": True,
        "allowed_bots": {
            "googlebot",
            "bingbot",
            "slurp",
        },  # Allowed search engine bots / Разрешенные поисковые боты
    },
}

# Server configuration / Конфигурация сервера
SERVER_CONFIG = {
    "target_server": "http://127.0.0.1:8097",
    "timeout": 30.0,
    "static_root": "C:/server/httpd/data/htdocs",
    "ssl_enabled": "True",
    "host": "0.0.0.0",
    "port": 443,
}

# Logging configuration / Конфигурация логирования
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "log_dir": "logs",
    "max_log_size": "10MB",
    "backup_count": 5,
}

# Feature flags / Флаги функций
FEATURES = {
    "security_enabled": "True",
    "monitoring_enabled": "True",
    "rate_limiting_enabled": "True",
    "ip_blocking_enabled": "True",
    "threat_detection_enabled": "True",
    "static_serving_enabled": "True",
    "api_proxy_enabled": "True",
    "ssl_enabled": "True",
}


def get_config() -> Dict:
    """
    Get complete configuration / Получить полную конфигурацию
    """
    return {
        "security": SECURITY_CONFIG,
        "server": SERVER_CONFIG,
        "logging": LOGGING_CONFIG,
        "features": FEATURES,
    }


def update_config(new_config: Dict):
    """
    Update configuration with new values / Обновить конфигурацию новыми значениями
    """
    global SECURITY_CONFIG, SERVER_CONFIG, LOGGING_CONFIG, FEATURES

    if "security" in new_config:
        SECURITY_CONFIG.update(new_config["security"])
    if "server" in new_config:
        SERVER_CONFIG.update(new_config["server"])
    if "logging" in new_config:
        LOGGING_CONFIG.update(new_config["logging"])
    if "features" in new_config:
        FEATURES.update(new_config["features"])
