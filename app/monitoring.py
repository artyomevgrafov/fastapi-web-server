"""
Attack monitoring and logging module
Модуль мониторинга и логирования атак
"""

import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from collections import defaultdict, deque
from fastapi import Request

logger = logging.getLogger(__name__)


# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Active HTTP requests'
)

SECURITY_BLOCKED_REQUESTS = Counter(
    'security_requests_blocked_total',
    'Total requests blocked by security',
    ['block_type']
)

ATTACK_DETECTED = Counter(
    'security_attacks_detected_total',
    'Total security attacks detected',
    ['attack_type']
)


class AttackMonitor:
    """
    Attack monitoring and logging system
    Система мониторинга и логирования атак
    """

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Attack statistics / Статистика атак
        self.attack_stats = {
            "total_attacks": 0,
            "blocked_requests": 0,
            "suspicious_requests": 0,
            "rate_limit_hits": 0,
            "ip_blocks": 0,
            "attack_types": defaultdict(int),
        }

        # Recent attacks for analysis / Недавние атаки для анализа
        self.recent_attacks = deque(maxlen=1000)

        # IP threat scores / Уровни угроз по IP
        self.ip_threat_scores = defaultdict(int)

        # Attack patterns database / База данных паттернов атак
        self.attack_patterns = self._load_attack_patterns()

        # Configuration / Конфигурация
        self.config = {
            "enable_detailed_logging": True,
            "log_rotation_hours": 24,
            "max_log_files": 7,
            "threat_score_threshold": 10,
            "enable_attack_analysis": True,
            "alert_on_major_attacks": True,
        }

    def _load_attack_patterns(self) -> Dict:
        """
        Load common attack patterns / Загрузить общие паттерны атак
        """
        return {
            "directory_traversal": [
                "../",
                "..\\",
                "....//",
                "....\\\\",
                "%2e%2e%2f",
                "%2e%2e%5c",
            ],
            "sql_injection": [
                "union select",
                "select * from",
                "insert into",
                "drop table",
                "delete from",
                "update set",
                "or 1=1",
                "' or '1'='1",
                "';",
                "--",
                "/*",
            ],
            "xss_attacks": [
                "<script>",
                "javascript:",
                "onload=",
                "onerror=",
                "onclick=",
                "alert(",
                "document.cookie",
                "eval(",
                "setTimeout(",
            ],
            "path_traversal": [
                "/etc/passwd",
                "/etc/shadow",
                "/windows/win.ini",
                "c:\\windows\\system32",
                "/proc/self/environ",
            ],
            "file_inclusion": [
                "php://filter",
                "phar://",
                "zip://",
                "data://",
                "expect://",
            ],
        }

    def log_attack(
        self, request: Request, attack_type: str, details: str, client_ip: str
    ):
        """
        Log an attack attempt / Записать попытку атаки
        """
        attack_entry = {
            'timestamp': datetime.now().isoformat(),
            "client_ip": client_ip,
            "attack_type": attack_type,
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent", ""),
            "details": details,
            "threat_level": self._calculate_threat_level(attack_type),
        }

        # Update statistics / Обновить статистику
        self.attack_stats["total_attacks"] += 1
        self.attack_stats["attack_types"][attack_type] += 1

        # Update IP threat score / Обновить уровень угрозы IP
        self.ip_threat_scores[client_ip] += self._get_threat_score(attack_type)

        # Add to recent attacks / Добавить в недавние атаки
        self.recent_attacks.append(attack_entry)

        # Log to file / Записать в файл
        if self.config["enable_detailed_logging"]:
            self._write_attack_log(attack_entry)

        # Log to console / Записать в консоль
        logger.warning(
            f"ATTACK DETECTED - Type: {attack_type}, IP: {client_ip}, "
            f"URL: {request.url}, Details: {details}"
        )

        # Check for alert / Проверить необходимость оповещения
        if (
            self.config["alert_on_major_attacks"]
            and attack_entry["threat_level"] == "HIGH"
        ):
            self._trigger_alert(attack_entry)

    def log_blocked_request(self, client_ip: str, reason: str, request: Request = None):
        """
        Log a blocked request / Записать заблокированный запрос
        """
        self.attack_stats["blocked_requests"] += 1

        blocked_entry = {
            "timestamp": datetime.now().isoformat(),
            "client_ip": client_ip,
            "reason": reason,
            "method": request.method if request else "UNKNOWN",
            "url": str(request.url) if request else "UNKNOWN",
            "type": "BLOCKED",
        }

        if self.config["enable_detailed_logging"]:
            self._write_blocked_log(blocked_entry)

        logger.info(f"Request blocked - IP: {client_ip}, Reason: {reason}")

    def log_suspicious_request(self, client_ip: str, reason: str, request: Request):
        """
        Log a suspicious request / Записать подозрительный запрос
        """
        self.attack_stats["suspicious_requests"] += 1

        suspicious_entry = {
            "timestamp": datetime.now().isoformat(),
            "client_ip": client_ip,
            "reason": reason,
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent", ""),
            "type": "SUSPICIOUS",
        }

        if self.config["enable_detailed_logging"]:
            self._write_suspicious_log(suspicious_entry)

        logger.info(f"Suspicious request - IP: {client_ip}, Reason: {reason}")

    def _write_attack_log(self, attack_entry: Dict):
        """
        Write attack log to file / Записать лог атаки в файл
        """
        log_file = self.log_dir / f"attacks_{datetime.now().strftime('%Y%m%d')}.json"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(attack_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write attack log: {e}")

    def _write_blocked_log(self, blocked_entry: Dict):
        """
        Write blocked request log to file / Записать лог заблокированных запросов в файл
        """
        log_file = self.log_dir / f"blocked_{datetime.now().strftime('%Y%m%d')}.json"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(blocked_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write blocked log: {e}")

    def _write_suspicious_log(self, suspicious_entry: Dict):
        """
        Write suspicious request log to file / Записать лог подозрительных запросов в файл
        """
        log_file = self.log_dir / f"suspicious_{datetime.now().strftime('%Y%m%d')}.json"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(suspicious_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write suspicious log: {e}")

    def _calculate_threat_level(self, attack_type: str) -> str:
        """
        Calculate threat level for attack type / Рассчитать уровень угрозы для типа атаки
        """
        high_threat = {"sql_injection", "rce", "path_traversal", "file_inclusion"}
        medium_threat = {"xss_attacks", "directory_traversal", "csrf"}
        low_threat = {"scanning", "probing", "information_gathering"}

        if attack_type in high_threat:
            return "HIGH"
        elif attack_type in medium_threat:
            return "MEDIUM"
        elif attack_type in low_threat:
            return "LOW"
        else:
            return "UNKNOWN"

    def _get_threat_score(self, attack_type: str) -> int:
        """
        Get threat score for attack type / Получить балл угрозы для типа атаки
        """
        score_map = {
            "HIGH": 5,
            "MEDIUM": 3,
            "LOW": 1,
            "UNKNOWN": 2,
        }
        threat_level = self._calculate_threat_level(attack_type)
        return score_map.get(threat_level, 2)

    def _trigger_alert(self, attack_entry: Dict):
        """
        Trigger alert for major attack / Запустить оповещение для серьезной атаки
        """
        alert_message = (
            f"🚨 MAJOR ATTACK ALERT 🚨\n"
            f"Time: {attack_entry['timestamp']}\n"
            f"IP: {attack_entry['client_ip']}\n"
            f"Type: {attack_entry['attack_type']}\n"
            f"URL: {attack_entry['url']}\n"
            f"Threat Level: {attack_entry['threat_level']}\n"
            f"Details: {attack_entry['details']}"
        )

        logger.critical(alert_message)

    def analyze_attack_patterns(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Analyze attack patterns over time window / Проанализировать паттерны атак за временное окно
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

        recent_attacks = {}
            attack
            for attack in self.recent_attacks
            if datetime.fromisoformat(attack["timestamp"]) > cutoff_time
        ]

        analysis = {
            'time_window_hours': time_window_hours,
            "total_attacks": len(recent_attacks),
            "attack_types": defaultdict(int),
            "top_attackers": defaultdict(int),
            "most_targeted_paths": defaultdict(int),
            "threat_levels": defaultdict(int),
        }

        for attack in recent_attacks:
            analysis["attack_types"][attack["attack_type"]] += 1
            analysis["top_attackers"][attack["client_ip"]] += 1
            analysis["threat_levels"][attack["threat_level"]] += 1

            # Extract path from URL / Извлечь путь из URL
            path = attack["url"].split("?")[
                0
            ]  # Remove query parameters / Удалить параметры запроса
            analysis["most_targeted_paths"][path] += 1

        # Convert defaultdict to regular dict for JSON serialization
        analysis["attack_types"] = dict(analysis["attack_types"])
        analysis["top_attackers"] = dict(analysis["top_attackers"])
        analysis["most_targeted_paths"] = dict(analysis["most_targeted_paths"])
        analysis["threat_levels"] = dict(analysis["threat_levels"])

        return analysis

    def get_high_threat_ips(self, threshold: int = None) -> List[Dict[str, Any]]:
        """
        Get IPs with high threat scores / Получить IP с высокими уровнями угроз
        """
        if threshold is None:
            threshold = self.config["threat_score_threshold"]

        high_threat_ips = []
        for ip, score in self.threat_scores.items():
            if score >= threshold:
                high_threat_ips.append({
                    {
                        "ip": ip,
                        'threat_score': score,
                        "last_seen": self._get_last_attack_time(ip),
                    }
                )

        # Sort by threat score / Сортировать по уровню угрозы
        high_threat_ips.sort(key=lambda x: x["threat_score"], reverse=True)
        return high_threat_ips

    def _get_last_attack_time(self, ip: str) -> Optional[str]:
        """
        Get last attack time for IP / Получить время последней атаки для IP
        """
        for attack in reversed(self.recent_attacks):
            if attack["client_ip"] == ip:
                return attack["timestamp"]
        return None

    def get_monitoring_stats(self) -> Dict:
        """
        Get comprehensive monitoring statistics / Получить комплексную статистику мониторинга
        """
        return {
            "attack_statistics": dict(self.attack_stats),
            "recent_attacks_count": len(self.recent_attacks),
            "unique_attackers_tracked": len(self.ip_threat_scores),
            "high_threat_ips_count": len(self.get_high_threat_ips()),
            "monitoring_config": self.config,
            "current_time": datetime.now().isoformat(),
        }

    def cleanup_old_logs(self):
        """
        Cleanup old log files / Очистить старые файлы логов
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=self.config["max_log_files"])

            for log_file in self.log_dir.glob("*.json"):
                if log_file.stat().st_mtime < cutoff_time.timestamp():
                    log_file.unlink()
                    logger.info(f"Cleaned up old log file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")


# Global attack monitor instance / Глобальный экземпляр монитора атак
attack_monitor = AttackMonitor()


def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


class MetricsMiddleware:
    """Middleware for collecting Prometheus metrics"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]

        # Skip metrics endpoint to avoid self-monitoring
        if path == "/metrics":
            return await self.app(scope, receive, send)

        ACTIVE_REQUESTS.inc()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            ACTIVE_REQUESTS.dec()
            REQUEST_DURATION.labels(method=method, endpoint=path).observe(time.time() - start_time)
