# Security System Guide / Руководство по системе безопасности

## Overview / Обзор

This security system provides comprehensive protection against web attacks, scanners, and malicious actors. The system includes IP blocking, rate limiting, threat detection, and real-time monitoring.

Эта система безопасности обеспечивает комплексную защиту от веб-атак, сканеров и злоумышленников. Система включает блокировку IP, ограничение скорости, обнаружение угроз и мониторинг в реальном времени.

## Features / Функции

### 🔒 IP Blocking / Блокировка IP
- Automatic blocking of suspicious IPs
- Configurable block duration
- Manual IP management
- Автоматическая блокировка подозрительных IP-адресов
- Настраиваемая длительность блокировки
- Ручное управление IP-адресами

### ⚡ Rate Limiting / Ограничение скорости
- Request rate limiting per IP
- Burst protection
- Configurable thresholds
- Ограничение скорости запросов на IP
- Защита от всплесков трафика
- Настраиваемые пороги

### 🚨 Threat Detection / Обнаружение угроз
- Suspicious path detection
- SQL injection detection
- XSS attack detection
- Directory traversal detection
- Обнаружение подозрительных путей
- Обнаружение SQL-инъекций
- Обнаружение XSS-атак
- Обнаружение обхода директорий

### 📊 Monitoring & Logging / Мониторинг и логирование
- Real-time attack monitoring
- Detailed logging
- Attack pattern analysis
- Threat scoring
- Мониторинг атак в реальном времени
- Детальное логирование
- Анализ паттернов атак
- Оценка уровня угроз

## Configuration / Конфигурация

### Security Settings / Настройки безопасности

Edit `app/config.py` to modify security settings:

```python
SECURITY_CONFIG = {
    "ip_blocking": {
        "enabled": True,
        "block_duration": 3600,  # 1 hour in seconds
        "auto_block_suspicious": True,
    },
    "rate_limiting": {
        "enabled": True,
        "max_requests_per_minute": 100,
        "burst_max_requests": 50,
    },
    # ... more settings
}
```

### Suspicious Patterns / Подозрительные паттерны

The system detects common attack patterns:

- **Paths**: `.env`, `.git/config`, `admin/config.php`, `phpinfo.php`, etc.
- **Extensions**: `.bak`, `.old`, `.sql`, `.env`, etc.
- **Parameters**: `cmd`, `exec`, `union select`, `script`, etc.

## API Endpoints / API Эндпоинты

### Security Statistics / Статистика безопасности
```
GET /security/stats
```
Returns current security statistics and configuration.

### Monitoring Statistics / Статистика мониторинга
```
GET /monitoring/stats
```
Returns attack monitoring statistics.

### Attack Analysis / Анализ атак
```
GET /monitoring/analysis?time_window_hours=24
```
Returns attack pattern analysis for specified time window.

### High Threat IPs / IP с высокими угрозами
```
GET /monitoring/high-threat-ips?threshold=10
```
Returns IP addresses with high threat scores.

## Command Line Interface / Интерфейс командной строки

### Security Status / Статус безопасности
```bash
python app/security_manager.py status
```

### Attack Analysis / Анализ атак
```bash
python app/security_manager.py analysis --hours 24
```

### High Threat IPs / IP с высокими угрозами
```bash
python app/security_manager.py threats --threshold 10
```

### Real-time Monitoring / Мониторинг в реальном времени
```bash
python app/security_manager.py monitor --interval 5
```

### Export Logs / Экспорт логов
```bash
python app/security_manager.py export security_logs.json --days 7
```

## Log Files / Файлы логов

The system creates three types of log files:

- `attacks_YYYYMMDD.json` - Detailed attack logs
- `blocked_YYYYMMDD.json` - Blocked request logs
- `suspicious_YYYYMMDD.json` - Suspicious activity logs

Logs are rotated daily and kept for 7 days by default.

## Common Attack Patterns / Общие паттерны атак

### Scanning & Probing / Сканирование и зондирование
- Requests to common vulnerable paths
- Directory listing attempts
- Configuration file access
- Запросы к общим уязвимым путям
- Попытки листинга директорий
- Доступ к файлам конфигурации

### Information Disclosure / Раскрытие информации
- Access to `.env` files
- Git repository access
- Database dumps
- Backup files
- Доступ к файлам `.env`
- Доступ к репозиторию Git
- Дампы баз данных
- Файлы резервных копий

### Injection Attacks / Атаки инъекций
- SQL injection attempts
- Command injection
- File inclusion
- Попытки SQL-инъекций
- Инъекции команд
- Включение файлов

## Best Practices / Рекомендации

### Regular Monitoring / Регулярный мониторинг
1. Check security status daily
2. Review high threat IPs weekly
3. Analyze attack patterns monthly
4. Export and archive logs regularly

1. Проверяйте статус безопасности ежедневно
2. Просматривайте IP с высокими угрозами еженедельно
3. Анализируйте паттерны атак ежемесячно
4. Регулярно экспортируйте и архивируйте логи

### Configuration Tuning / Настройка конфигурации
- Adjust rate limits based on normal traffic patterns
- Update suspicious patterns as new threats emerge
- Configure appropriate block durations
- Настройте ограничения скорости на основе нормальных паттернов трафика
- Обновляйте подозрительные паттерны по мере появления новых угроз
- Настройте соответствующую длительность блокировки

### Incident Response / Реагирование на инциденты
1. Identify the attack type and source
2. Check if IP is already blocked
3. Review logs for similar patterns
4. Consider permanent blocking for repeat offenders
5. Update security patterns if necessary

1. Определите тип атаки и источник
2. Проверьте, заблокирован ли IP
3. Просмотрите логи на наличие похожих паттернов
4. Рассмотрите постоянную блокировку для повторных нарушителей
5. При необходимости обновите паттерны безопасности

## Troubleshooting / Устранение неполадок

### Common Issues / Общие проблемы

**False Positives / Ложные срабатывания**
- Adjust suspicious pattern thresholds
- Add legitimate paths to whitelist
- Review and tune detection rules

**Performance Impact / Влияние на производительность**
- Optimize rate limiting settings
- Reduce log verbosity if needed
- Monitor system resources

**Connection Issues / Проблемы с подключением**
- Verify service is running
- Check firewall settings
- Validate API endpoints

## Security Modules / Модули безопасности

### `security.py`
- IP blocking and rate limiting
- Threat detection and analysis
- Security middleware

### `monitoring.py`
- Attack logging and analysis
- Threat scoring
- Real-time monitoring

### `config.py`
- Security configuration
- Suspicious patterns
- Feature flags

### `security_manager.py`
- Command-line interface
- Log management
- Real-time monitoring

## Support / Поддержка

For security issues or questions:
- Review logs in `logs/` directory
- Check security statistics via API
- Use CLI tools for analysis
- Contact system administrator

Для вопросов безопасности:
- Просмотрите логи в директории `logs/`
- Проверьте статистику безопасности через API
- Используйте инструменты CLI для анализа
- Обратитесь к системному администратору

---

**Note**: This security system is designed to protect against common web attacks but should be used as part of a comprehensive security strategy.

**Примечание**: Эта система безопасности предназначена для защиты от распространенных веб-атак, но должна использоваться как часть комплексной стратегии безопасности.