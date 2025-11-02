"""
Security module for IP blocking and threat detection
Модуль безопасности для блокировки IP-адресов и обнаружения угроз
"""

import time
import logging
from typing import Dict, Set, List, Optional, Any
from ipaddress import ip_address, IPv4Address
from collections import defaultdict
from fastapi import Request, HTTPException, status, FastAPI
from .monitoring import attack_monitor

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Security manager for IP blocking and threat detection
    Менеджер безопасности для блокировки IP-адресов и обнаружения угроз
    """

    def __init__(self):
        # Blocked IPs with timestamp / Заблокированные IP-адреса с временной меткой
        self.blocked_ips: Dict[str, float] = {}

        # Request counters for rate limiting / Счетчики запросов для ограничения скорости
        self.request_counts: Dict[str, List[float]] = defaultdict(list)

        # Suspicious patterns to detect / Подозрительные паттерны для обнаружения
        self.suspicious_patterns = {
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

        # Security configuration / Конфигурация безопасности
        self.config = {
            "max_requests_per_minute": 100,  # Maximum requests per minute / Максимум запросов в минуту
            "block_duration": 3600,  # Block duration in seconds (1 hour) / Длительность блокировки в секундах (1 час)
            "suspicious_request_threshold": 5,  # Threshold for suspicious requests / Порог для подозрительных запросов
            "enable_ip_blocking": True,  # Enable IP blocking / Включить блокировку IP
            "enable_rate_limiting": True,  # Enable rate limiting / Включить ограничение скорости
            "enable_threat_detection": True,  # Enable threat detection / Включить обнаружение угроз
            "log_suspicious_activity": True,  # Log suspicious activity / Логировать подозрительную активность
        }

    def is_ip_blocked(self, ip: str) -> bool:
        """
        Check if IP is blocked / Проверить, заблокирован ли IP-адрес
        """
        if not self.config["enable_ip_blocking"]:
            return False

        if ip in self.blocked_ips:
            # Check if block has expired / Проверить, истекла ли блокировка
            block_time = self.blocked_ips[ip]
            if time.time() - block_time < self.config["block_duration"]:
                return True
            else:
                # Remove expired block / Удалить истекшую блокировку
                del self.blocked_ips[ip]
        return False

    def block_ip(self, ip: str, reason: str = "Suspicious activity"):
        """
        Block an IP address / Заблокировать IP-адрес
        """
        if not self.config["enable_ip_blocking"]:
            return

        self.blocked_ips[ip] = time.time()
        logger.warning(f"Blocked IP {ip}: {reason}")
        attack_monitor.log_blocked_request(ip, reason)

    def check_rate_limit(self, ip: str) -> bool:
        """
        Check rate limit for IP / Проверить ограничение скорости для IP
        """
        if not self.config["enable_rate_limiting"]:
            return True

        current_time = time.time()
        # Remove old requests / Удалить старые запросы
        self.request_counts[ip] = [
            req_time
            for req_time in self.request_counts[ip]
            if current_time - req_time < 60
        ]

        # Check if over limit / Проверить, превышен ли лимит
        if len(self.request_counts[ip]) >= self.config["max_requests_per_minute"]:
            self.block_ip(ip, "Rate limit exceeded")
            return False

        # Add current request / Добавить текущий запрос
        self.request_counts[ip].append(current_time)
        return True

    def is_suspicious_request(self, request: Request) -> tuple[bool, str]:
        """
        Check if request is suspicious / Проверить, является ли запрос подозрительным
        Returns (is_suspicious, reason) / Возвращает (подозрительный, причина)
        """
        if not self.config["enable_threat_detection"]:
            return False, ""

        path = request.url.path.lower()
        query_string = str(request.query_params).lower()

        # Check suspicious paths / Проверить подозрительные пути
        for pattern in self.suspicious_patterns["paths"]:
            if pattern in path:
                return True, f"Suspicious path pattern: {pattern}"

        # Check suspicious file extensions / Проверить подозрительные расширения файлов
        for ext in self.suspicious_patterns["extensions"]:
            if path.endswith(ext):
                return True, f"Suspicious file extension: {ext}"

        # Check suspicious parameters / Проверить подозрительные параметры
        for param in self.suspicious_patterns["params"]:
            if param in query_string:
                return True, f"Suspicious parameter: {param}"

        # Check for directory traversal / Проверить обход директорий
        if ".." in path or "../" in path:
            return True, "Directory traversal attempt"

        # Check for SQL injection patterns / Проверить паттерны SQL-инъекций
        sql_patterns = ["union select", "select * from", "insert into", "drop table"]
        for pattern in sql_patterns:
            if pattern in query_string:
                return True, f"SQL injection pattern: {pattern}"

        return False, ""

    def analyze_request(self, request: Request) -> tuple[bool, Optional[str]]:
        """
        Analyze request for security threats / Проанализировать запрос на наличие угроз безопасности
        Returns (should_block, reason) / Возвращает (блокировать, причина)
        """
        client_ip = self.get_client_ip(request)

        # Check if IP is already blocked / Проверить, заблокирован ли IP
        if self.is_ip_blocked(client_ip):
            return True, "IP is blocked"

        # Check rate limiting / Проверить ограничение скорости
        if not self.check_rate_limit(client_ip):
            return True, "Rate limit exceeded"

        # Check for suspicious patterns / Проверить подозрительные паттерны
        is_suspicious, reason = self.is_suspicious_request(request)
        if is_suspicious:
            if self.config["log_suspicious_activity"]:
                logger.warning(
                    f"Suspicious request from {client_ip}: {reason} - {request.url}"
                )
                attack_monitor.log_suspicious_request(client_ip, reason, request)

            # Count suspicious requests / Подсчитать подозрительные запросы
            suspicious_count = self.count_suspicious_requests(client_ip)
            if suspicious_count >= self.config["suspicious_request_threshold"]:
                self.block_ip(client_ip, f"Multiple suspicious requests: {reason}")
                attack_monitor.log_attack(request, "scanning", reason, client_ip)
                return True, f"Multiple suspicious requests: {reason}"

        return False, None

    def count_suspicious_requests(self, ip: str) -> int:
        """
        Count suspicious requests from IP in last minute / Подсчитать подозрительные запросы от IP за последнюю минуту
        """
        current_time = time.time()
        recent_requests = [
            req_time
            for req_time in self.request_counts[ip]
            if current_time - req_time < 60
        ]
        return len(recent_requests)

    def get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request / Получить IP-адрес клиента из запроса
        """
        # Try common headers for real IP / Попробовать общие заголовки для реального IP
        for header in [
            "x-real-ip",
            "x-forwarded-for",
            "x-forwarded",
            "forwarded-for",
            "fwd",
        ]:
            ip = request.headers.get(header)
            if ip:
                # Handle multiple IPs in x-forwarded-for / Обработать несколько IP в x-forwarded-for
                if "," in ip:
                    ip = ip.split(",")[0].strip()
                return ip

        # Fallback to client host / Резервный вариант - хост клиента
        return request.client.host if request.client else "unknown"

    def get_security_stats(self) -> Dict[str, Any]:
        """
        Get security statistics / Получить статистику безопасности
        """
        current_time = time.time()
        active_blocks = {
            ip: int(self.config["block_duration"] - (current_time - block_time))
            for ip, block_time in self.blocked_ips.items()
            if current_time - block_time < self.config["block_duration"]
        }

        return {
            "blocked_ips_count": len(active_blocks),
            "active_blocks": active_blocks,
            "total_requests_tracked": sum(
                len(requests) for requests in self.request_counts.values()
            ),
            "unique_ips_tracked": len(self.request_counts),
            "config": self.config,
        }


# Global security manager instance / Глобальный экземпляр менеджера безопасности
security_manager = SecurityManager()


def security_middleware(request: Request, call_next):
    """
    Security middleware for FastAPI / Промежуточное ПО безопасности для FastAPI
    """
    # Analyze request for security threats / Проанализировать запрос на наличие угроз безопасности
    should_block, reason = security_manager.analyze_request(request)

    if should_block:
        client_ip = security_manager.get_client_ip(request)
        logger.warning(f"Blocked request from {client_ip}: {reason}")
        attack_monitor.log_blocked_request(
            client_ip, reason or "Unknown threat", request
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Continue with request processing / Продолжить обработку запроса
    response = call_next(request)
    return response


def setup_security(app: FastAPI) -> None:
    """
    Setup security middleware for FastAPI app / Настроить промежуточное ПО безопасности для приложения FastAPI
    """
    app.middleware("http")(security_middleware)
    logger.info("Security middleware enabled")
