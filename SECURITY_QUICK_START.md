# Security System Quick Start Guide
# Руководство по быстрому запуску системы безопасности

## Overview / Обзор

This security system provides comprehensive protection against web attacks, scanners, and malicious actors. It automatically blocks suspicious requests and provides real-time monitoring.

Эта система безопасности обеспечивает комплексную защиту от веб-атак, сканеров и злоумышленников. Она автоматически блокирует подозрительные запросы и предоставляет мониторинг в реальном времени.

## Quick Start / Быстрый запуск

### 1. Automatic Integration / Автоматическая интеграция

The security system is already integrated into your FastAPI application. When you start the server, security features are automatically enabled.

Система безопасности уже интегрирована в ваше FastAPI приложение. При запуске сервера функции безопасности автоматически включаются.

### 2. Check Security Status / Проверка статуса безопасности

```bash
# Check current security status
python app/security_manager.py status
```

### 3. Monitor Attacks / Мониторинг атак

```bash
# Real-time monitoring
python app/security_manager.py monitor --interval 5

# View attack analysis
python app/security_manager.py analysis --hours 24

# View high threat IPs
python app/security_manager.py threats
```

## What's Protected / Что защищено

### 🚫 Blocked Attack Types / Типы блокируемых атак

- **Directory Traversal** - `../../../etc/passwd`
- **SQL Injection** - `' OR '1'='1`
- **XSS Attacks** - `<script>alert()</script>`
- **Path Scanning** - `.env`, `.git/config`, `phpinfo.php`
- **Rate Limiting** - Too many requests from single IP
- **File Inclusion** - Suspicious file extensions

### 📊 Monitored Patterns / Мониторируемые паттерны

- **Suspicious Paths**: `.env`, `.git/`, `admin/`, `backup/`
- **Suspicious Extensions**: `.bak`, `.old`, `.sql`, `.pem`
- **Suspicious Parameters**: `cmd`, `exec`, `union`, `script`
- **Common Attacks**: SQL injection, XSS, directory traversal

## Configuration / Конфигурация

### Basic Settings / Основные настройки

Edit `app/config.py` to modify:

```python
SECURITY_CONFIG = {
    "ip_blocking": {
        "enabled": True,
        "block_duration": 3600,  # 1 hour
    },
    "rate_limiting": {
        "enabled": True,
        "max_requests_per_minute": 100,
    },
}
```

### Common Adjustments / Общие настройки

- **Increase/Decrease Rate Limits** - Adjust based on normal traffic
- **Modify Block Duration** - Change how long IPs stay blocked
- **Add Whitelist IPs** - Add trusted IPs to avoid false positives

## API Endpoints / API Эндпоинты

### Security Monitoring / Мониторинг безопасности

```
GET /security/stats          # Security statistics
GET /monitoring/stats        # Attack statistics  
GET /monitoring/analysis     # Attack pattern analysis
GET /monitoring/high-threat-ips  # High threat IPs
```

### Health Check / Проверка состояния

```
GET /health                  # Server health with security status
GET /                        # Server information
```

## Command Line Tools / Инструменты командной строки

### Security Manager / Менеджер безопасности

```bash
# Basic commands
python app/security_manager.py status
python app/security_manager.py analysis
python app/security_manager.py threats
python app/security_manager.py monitor

# Export logs
python app/security_manager.py export logs.json --days 7
```

### Test Security / Тестирование безопасности

```bash
# Run comprehensive security test
python test_security.py
```

## Log Files / Файлы логов

Security logs are stored in `logs/` directory:

- `attacks_YYYYMMDD.json` - Detailed attack logs
- `blocked_YYYYMMDD.json` - Blocked request logs  
- `suspicious_YYYYMMDD.json` - Suspicious activity logs

Logs are automatically rotated and kept for 7 days.

## Common Scenarios / Распространенные сценарии

### 1. False Positives / Ложные срабатывания

If legitimate requests are being blocked:

1. Check logs for blocked requests
2. Identify the blocking reason
3. Adjust suspicious patterns in `config.py`
4. Add IP to whitelist if needed

### 2. High Attack Volume / Высокий объем атак

If experiencing many attacks:

1. Monitor real-time with `python app/security_manager.py monitor`
2. Check high threat IPs with `python app/security_manager.py threats`
3. Consider lowering rate limits
4. Review and update attack patterns

### 3. Performance Issues / Проблемы с производительностью

If security system impacts performance:

1. Increase rate limit thresholds
2. Disable detailed logging temporarily
3. Monitor system resources
4. Optimize suspicious pattern matching

## Best Practices / Рекомендации

### Daily Monitoring / Ежедневный мониторинг

```bash
# Quick status check
python app/security_manager.py status

# Review recent attacks
python app/security_manager.py analysis --hours 24
```

### Weekly Review / Еженедельный обзор

```bash
# Export and review logs
python app/security_manager.py export weekly_report.json --days 7

# Check persistent threats
python app/security_manager.py threats --threshold 20
```

### Monthly Maintenance / Ежемесячное обслуживание

1. Review and update suspicious patterns
2. Analyze attack trends
3. Adjust configuration based on traffic patterns
4. Clean up old log files

## Troubleshooting / Устранение неполадок

### Common Issues / Общие проблемы

**Service Not Responding** / Сервис не отвечает
- Check if FastAPI server is running
- Verify port 443 is accessible
- Check firewall settings

**Security Endpoints Not Working** / Эндпоинты безопасности не работают
- Verify security middleware is enabled
- Check application logs for errors
- Ensure all security modules are imported

**No Attacks Being Detected** / Атаки не обнаруживаются
- Test with `python test_security.py`
- Verify suspicious patterns in configuration
- Check if threat detection is enabled

## Support / Поддержка

### Quick Help / Быстрая помощь

1. **Check Logs**: Review `logs/` directory for detailed information
2. **Test System**: Run `python test_security.py` to verify functionality
3. **Monitor Real-time**: Use `python app/security_manager.py monitor`
4. **Export Data**: Export logs for analysis with security tools

### Emergency Response / Экстренное реагирование

If under active attack:

1. **Immediate**: Run `python app/security_manager.py monitor` for real-time view
2. **Block IPs**: Use security manager to view and block high threat IPs
3. **Analyze**: Use `python app/security_manager.py analysis` to understand attack patterns
4. **Adjust**: Temporarily lower rate limits or block durations

---

**Note**: This security system is designed to work alongside your existing infrastructure and provides an additional layer of protection against common web threats.

**Примечание**: Эта система безопасности предназначена для работы вместе с вашей существующей инфраструктурой и обеспечивает дополнительный уровень защиты от распространенных веб-угроз.