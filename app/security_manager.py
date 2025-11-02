"""
Security Management Script
Скрипт управления безопасностью

This script provides command-line interface for managing security settings,
viewing blocked IPs, and analyzing attack patterns.
Этот скрипт предоставляет интерфейс командной строки для управления настройками безопасности,
просмотра заблокированных IP-адресов и анализа паттернов атак.
"""

import argparse
import json
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests
import time
from datetime import datetime


class SecurityManagerCLI:
    """
    Command-line interface for security management
    Интерфейс командной строки для управления безопасностью
    """

    def __init__(self, base_url: str = "http://localhost:443"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics / Получить статистику безопасности"""
        try:
            response = self.session.get(f"{self.base_url}/security/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting security stats: {e}")
            return {}

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics / Получить статистику мониторинга"""
        try:
            response = self.session.get(f"{self.base_url}/monitoring/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting monitoring stats: {e}")
            return {}

    def get_attack_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get attack analysis / Получить анализ атак"""
        try:
            response = self.session.get(
                f"{self.base_url}/monitoring/analysis?time_window_hours={hours}",
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting attack analysis: {e}")
            return {}

    def get_high_threat_ips(self, threshold: int | None = None) -> List[Dict[str, Any]]:
        """Get high threat IPs / Получить IP с высокими угрозами"""
        try:
            url = f"{self.base_url}/monitoring/high-threat-ips"
            if threshold:
                url += f"?threshold={threshold}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting high threat IPs: {e}")
            return []

    def show_security_status(self):
        """Show current security status / Показать текущий статус безопасности"""
        print("🔒 Security Status / Статус безопасности")
        print("=" * 50)

        security_stats = self.get_security_stats()
        monitoring_stats = self.get_monitoring_stats()

        if not security_stats or not monitoring_stats:
            print("❌ Unable to connect to security service")
            return

        # Security configuration / Конфигурация безопасности
        config = security_stats.get("config", {})
        print(
            f"IP Blocking: {'✅ Enabled' if config.get('enable_ip_blocking') else '❌ Disabled'}"
        )
        print(
            f"Rate Limiting: {'✅ Enabled' if config.get('enable_rate_limiting') else '❌ Disabled'}"
        )
        print(
            f"Threat Detection: {'✅ Enabled' if config.get('enable_threat_detection') else '❌ Disabled'}"
        )

        # Blocked IPs / Заблокированные IP
        blocked_count = security_stats.get("blocked_ips_count", 0)
        print(f"\nBlocked IPs: {blocked_count}")

        if blocked_count > 0:
            active_blocks = security_stats.get("active_blocks", {})
            for ip, remaining in active_blocks.items():
                print(f"  - {ip} (expires in {remaining}s)")

        # Monitoring statistics / Статистика мониторинга
        attack_stats = monitoring_stats.get("attack_statistics", {})
        print(f"\n📊 Attack Statistics / Статистика атак")
        print(f"Total Attacks: {attack_stats.get('total_attacks', 0)}")
        print(f"Blocked Requests: {attack_stats.get('blocked_requests', 0)}")
        print(f"Suspicious Requests: {attack_stats.get('suspicious_requests', 0)}")

        # High threat IPs / IP с высокими угрозами
        high_threat_count = monitoring_stats.get("high_threat_ips_count", 0)
        print(f"High Threat IPs: {high_threat_count}")

    def show_attack_analysis(self, hours: int = 24):
        """Show attack analysis / Показать анализ атак"""
        print(
            f"🔍 Attack Analysis (Last {hours} hours) / Анализ атак (последние {hours} часов)"
        )
        print("=" * 60)

        analysis = self.get_attack_analysis(hours)

        if not analysis:
            print("❌ Unable to get attack analysis")
            return

        total_attacks = analysis.get("total_attacks", 0)
        print(f"Total Attacks: {total_attacks}")

        if total_attacks == 0:
            print("No attacks detected in the specified time period")
            return

        # Attack types / Типы атак
        attack_types = analysis.get("attack_types", {})
        if attack_types:
            print(f"\nAttack Types / Типы атак:")
            for attack_type, count in sorted(
                attack_types.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  - {attack_type}: {count}")

        # Top attackers / Топ атакующих
        top_attackers = analysis.get("top_attackers", {})
        if top_attackers:
            print(f"\nTop Attackers / Топ атакующих:")
            for ip, count in sorted(
                top_attackers.items(), key=lambda x: x[1], reverse=True
            )[:10]:
                print(f"  - {ip}: {count} attacks")

        # Most targeted paths / Самые атакуемые пути
        targeted_paths = analysis.get("most_targeted_paths", {})
        if targeted_paths:
            print(f"\nMost Targeted Paths / Самые атакуемые пути:")
            for path, count in sorted(
                targeted_paths.items(), key=lambda x: x[1], reverse=True
            )[:10]:
                print(f"  - {path}: {count} attacks")

        # Threat levels / Уровни угроз
        threat_levels = analysis.get("threat_levels", {})
        if threat_levels:
            print(f"\nThreat Levels / Уровни угроз:")
            for level, count in sorted(
                threat_levels.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  - {level}: {count}")

    def show_high_threat_ips(self, threshold: int | None = None):
        """Show high threat IPs / Показать IP с высокими угрозами"""
        print("🚨 High Threat IPs / IP с высокими угрозами")
        print("=" * 50)

        high_threat_ips = self.get_high_threat_ips(threshold)

        if not high_threat_ips:
            print("No high threat IPs found")
            return

        print(f"Found {len(high_threat_ips)} high threat IPs:")
        print(f"{'IP Address':<20} {'Threat Score':<15} {'Last Seen':<20}")
        print("-" * 55)

        for ip_info in high_threat_ips:
            ip = ip_info.get("ip", "Unknown")
            score = ip_info.get("threat_score", 0)
            last_seen = ip_info.get("last_seen", "Unknown")

            # Format last seen time / Форматировать время последнего появления
            if last_seen != "Unknown":
                try:
                    last_seen_dt = datetime.fromisoformat(
                        last_seen.replace("Z", "+00:00")
                    )
                    last_seen = last_seen_dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass

            print(f"{ip:<20} {score:<15} {last_seen:<20}")

    def export_logs(self, output_file: str, days: int = 1):
        """Export security logs / Экспорт логов безопасности"""
        print(f"Exporting security logs for last {days} days...")

        log_dir = Path("logs")
        if not log_dir.exists():
            print("❌ Log directory not found")
            return

        cutoff_time = time.time() - (days * 24 * 3600)
        all_logs = []

        # Collect logs from all files / Собрать логи из всех файлов
        for log_file in log_dir.glob("*.json"):
            if log_file.stat().st_mtime >= cutoff_time:
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                all_logs.append(json.loads(line.strip()))
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")

        if not all_logs:
            print("No logs found for the specified period")
            return

        # Sort by timestamp / Сортировать по времени
        all_logs.sort(key=lambda x: x.get("timestamp", ""))

        # Export to file / Экспорт в файл
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_logs, f, indent=2, ensure_ascii=False)
            print(f"✅ Logs exported to {output_file} ({len(all_logs)} entries)")
        except Exception as e:
            print(f"❌ Error exporting logs: {e}")

    def show_real_time_monitoring(self, interval: int = 5):
        """Show real-time monitoring / Показать мониторинг в реальном времени"""
        print(
            f"🔄 Real-time Monitoring (updating every {interval}s) / Мониторинг в реальном времени (обновление каждые {interval}с)"
        )
        print("Press Ctrl+C to stop / Нажмите Ctrl+C для остановки")
        print("=" * 60)

        try:
            previous_stats = {}
            while True:
                monitoring_stats = self.get_monitoring_stats()
                attack_stats = monitoring_stats.get("attack_statistics", {})

                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{current_time}] Security Status:")
                print(f"  Total Attacks: {attack_stats.get('total_attacks', 0)}")
                print(f"  Blocked Requests: {attack_stats.get('blocked_requests', 0)}")
                print(
                    f"  Suspicious Requests: {attack_stats.get('suspicious_requests', 0)}"
                )

                # Show recent activity / Показать недавнюю активность
                if previous_stats:
                    new_attacks = attack_stats.get(
                        "total_attacks", 0
                    ) - previous_stats.get("total_attacks", 0)
                    new_blocks = attack_stats.get(
                        "blocked_requests", 0
                    ) - previous_stats.get("blocked_requests", 0)
                    if new_attacks > 0 or new_blocks > 0:
                        print(
                            f"  🔥 Recent: {new_attacks} new attacks, {new_blocks} new blocks"
                        )

                previous_stats = attack_stats.copy()
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped")


def main():
    """Main function / Главная функция"""
    parser = argparse.ArgumentParser(
        description="Security Management CLI / Интерфейс командной строки управления безопасностью",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / Примеры:
  python security_manager.py status          # Show security status
  python security_manager.py analysis        # Show attack analysis
  python security_manager.py threats         # Show high threat IPs
  python security_manager.py monitor         # Real-time monitoring
  python security_manager.py export logs.json --days 7  # Export logs
        """,
    )

    parser.add_argument(
        "command",
        choices=["status", "analysis", "threats", "monitor", "export"],
        help="Command to execute / Команда для выполнения",
    )

    parser.add_argument(
        "--url",
        default="http://localhost:443",
        help="Base URL of the security service / Базовый URL сервиса безопасности",
    )

    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Time window for analysis in hours / Временное окно для анализа в часах",
    )

    parser.add_argument(
        "--threshold", type=int, help="Threat score threshold / Порог уровня угрозы"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval for monitoring in seconds / Интервал обновления для мониторинга в секундах",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days for log export / Количество дней для экспорта логов",
    )

    parser.add_argument(
        "output_file",
        nargs="?",
        help="Output file for export / Выходной файл для экспорта",
    )

    args = parser.parse_args()

    manager = SecurityManagerCLI(base_url=args.url)

    try:
        if args.command == "status":
            manager.show_security_status()
        elif args.command == "analysis":
            manager.show_attack_analysis(args.hours)
        elif args.command == "threats":
            manager.show_high_threat_ips(args.threshold)
        elif args.command == "monitor":
            manager.show_real_time_monitoring(args.interval)
        elif args.command == "export":
            if not args.output_file:
                print("❌ Output file required for export")
                sys.exit(1)
            manager.export_logs(args.output_file, args.days)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
