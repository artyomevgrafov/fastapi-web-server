# Руководство по замене Apache на FastAPI

## Обзор

Данное руководство описывает процесс полной замены Apache HTTP Server на FastAPI как полноценного веб-сервера. FastAPI может работать напрямую на портах 80/443 и выполнять все функции Apache.

## Преимущества замены

### 🚀 Производительность
- **FastAPI** построен на асинхронном фреймворке Starlette
- В 2-3 раза быстрее традиционных синхронных серверов
- Поддержка асинхронных операций

### 🔧 Современные возможности
- Автоматическая документация OpenAPI/Swagger
- Встроенная валидация данных через Pydantic
- Поддержка WebSocket, SSE, GraphQL
- Современные стандарты (OpenAPI, JSON Schema)

### 💻 Разработка
- Автодополнение в IDE благодаря type hints
- Автоматическая генерация клиентов
- Простота тестирования и отладки

## Архитектура замены

### Текущая архитектура (Apache)
```
Клиент → Apache (443) → Proxy → FastAPI (8097)
```

### Новая архитектура (FastAPI напрямую)
```
Клиент → FastAPI (443)
```

## Подготовка к замене

### 1. Проверка текущей конфигурации

**Apache Virtual Hosts:**
```apache
<VirtualHost *:443>
    ServerName api.landmann.ua
    SSLCertificateFile "C:/server/httpd/win-acme/api.landmann.ua-crt.pem"
    SSLCertificateKeyFile "C:/server/httpd/win-acme/api.landmann.ua-key.pem"
    ProxyPass / http://127.0.0.1:8097/
</VirtualHost>
```

**FastAPI уже настроен:**
- ✅ SSL сертификаты синхронизированы
- ✅ API endpoints работают
- ✅ Статические файлы обслуживаются
- ✅ Документация доступна

### 2. Резервное копирование
```bash
# Резервная копия конфигурации Apache
copy "C:\server\httpd\Apache24\conf\*" "C:\backup\apache_config\"
```

## Пошаговая замена

### Шаг 1: Тестирование FastAPI на порту 8080

**Запуск тестового сервера:**
```bash
cd C:\server\httpd\fastapi
start_8080.bat
```

**Проверка функциональности:**
- https://localhost:8080 - веб-интерфейс
- https://localhost:8080/docs - документация API
- https://localhost:8080/api/health - проверка здоровья

### Шаг 2: Настройка порта 443 в FastAPI

**Изменение конфигурации (`config_443.py`):**
```python
class ProductionConfig443:
    PORT: int = 443
    SSL_ENABLED: bool = True
    SSL_CERT_FILE: str = "certs/cert.pem"
    SSL_KEY_FILE: str = "certs/key.pem"
```

### Шаг 3: Запуск с правами администратора

**Для работы на портах ниже 1024 требуется запуск от администратора:**
```batch
# Запуск от имени администратора
runas /user:Administrator "C:\server\httpd\fastapi\start_443.bat"
```

### Шаг 4: Остановка Apache

**Остановка службы Apache:**
```batch
sc stop "Apache2.4"
```

**Проверка остановки:**
```batch
netstat -an | find ":443"
```

## Конфигурация FastAPI для продакшена

### Основная конфигурация

**`config_production.py`:**
```python
class ProductionConfig:
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 443
    RELOAD: bool = False
    
    # SSL settings
    SSL_ENABLED: bool = True
    SSL_CERT_FILE: str = "certs/cert.pem"
    SSL_KEY_FILE: str = "certs/key.pem"
    
    # Performance
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024
    TIMEOUT: int = 60
    
    # Security
    ALLOWED_HOSTS: list = ["api.landmann.ua", "api.landmann.in.ua"]
```

### Миграция функциональности Apache

#### 1. Статические файлы
**Apache:**
```apache
DocumentRoot "C:/server/data/htdocs"
```

**FastAPI:**
```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

#### 2. Перенаправления
**Apache:**
```apache
RewriteEngine On
RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
```

**FastAPI:**
```python
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

@app.middleware("http")
async def redirect_http_to_https(request: Request, call_next):
    if request.url.scheme == "http":
        https_url = request.url.replace(scheme="https")
        return RedirectResponse(https_url, status_code=301)
    return await call_next(request)
```

#### 3. Заголовки
**Apache:**
```apache
Header set Cache-Control "no-store, no-cache"
```

**FastAPI:**
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache"
    return response
```

## Автоматизация развертывания

### Скрипт полной замены

**`replace_apache.bat`:**
```batch
@echo off
echo ========================================
echo Замена Apache на FastAPI
echo ========================================

echo 1. Остановка Apache...
sc stop "Apache2.4"
timeout /t 3

echo 2. Синхронизация сертификатов...
powershell -ExecutionPolicy Bypass -File "C:\server\httpd\win-acme\sync-certs.ps1"

echo 3. Запуск FastAPI на порту 443...
cd /d "C:\server\httpd\fastapi"
set FASTAPI_ENV=production
python start_443.py

echo ✅ Замена завершена!
```

### Сервис Windows для FastAPI

**Создание службы:**
```batch
sc create "FastAPI-Server" binPath="C:\server\httpd\fastapi\fastapi_service.exe" start=auto
sc description "FastAPI-Server" "FastAPI Web Server replacement for Apache"
```

## Мониторинг и логирование

### Логи доступа
**FastAPI предоставляет встроенное логирование:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/access.log'),
        logging.StreamHandler()
    ]
)
```

### Метрики производительности
```python
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

Instrumentator().instrument(app).expose(app)
```

## Обратная миграция (откат)

### Экстренный откат
```batch
@echo off
echo ========================================
echo Экстренный откат к Apache
echo ========================================

echo 1. Остановка FastAPI...
taskkill /F /IM python.exe

echo 2. Запуск Apache...
sc start "Apache2.4"

echo 3. Проверка статуса...
timeout /t 5
netstat -an | find ":443"

echo ✅ Откат завершен!
```

## Тестирование после замены

### Функциональные тесты
```bash
# Проверка SSL
openssl s_client -connect api.landmann.ua:443

# Проверка API
curl -k https://api.landmann.ua/api/health

# Проверка статических файлов
curl -k https://api.landmann.ua/static/index.html
```

### Нагрузочное тестирование
```bash
# Установка инструмента
pip install locust

# Запуск теста
locust -f load_test.py
```

## Оптимизация производительности

### Настройки Uvicorn
```python
uvicorn_config = {
    "host": "0.0.0.0",
    "port": 443,
    "workers": 4,  # Количество воркеров
    "loop": "uvloop",  # Использование uvloop для Linux
    "http": "httptools",  # Быстрый HTTP парсер
    "limit_max_requests": 1000,  # Перезапуск после 1000 запросов
}
```

### Кэширование
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

## Безопасность

### Защита заголовков
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["api.landmann.ua"])

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

## Заключение

### Преимущества завершенной замены:
- ✅ **Упрощение архитектуры** - убраны лишние компоненты
- ✅ **Улучшение производительности** - прямой доступ к приложению
- ✅ **Современный стек** - актуальные технологии и инструменты
- ✅ **Упрощение поддержки** - один сервер вместо двух
- ✅ **Автоматизация** - встроенная документация и валидация

### Рекомендуемый порядок действий:
1. Тестирование на порту 8080
2. Настройка продакшн конфигурации
3. Плановое окно обслуживания
4. Запуск FastAPI на порту 443
5. Мониторинг и оптимизация

FastAPI полностью готов заменить Apache и предоставляет все необходимые функции современного веб-сервера.