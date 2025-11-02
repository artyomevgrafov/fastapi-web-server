from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pathlib import Path
import httpx
import logging
from typing import Dict, Any
from .security import security_manager, setup_security
from .monitoring import attack_monitor
from .config import SERVER_CONFIG, FEATURES
from .messages import (
    SERVER_TITLE,
    SERVER_DESCRIPTION,
    SERVER_VERSION,
    CONFIG_LOAD_ERROR,
    SSL_CERT_ERROR,
    SSL_CERT_NOT_FOUND,
    SSL_KEY_NOT_FOUND,
    SSL_CERT_EMPTY,
    SSL_KEY_EMPTY,
    SSL_CERTS_FOUND,
    STARTING_SERVER,
    ADMIN_PRIVILEGES_REQUIRED,
    PORT_IN_USE,
    SSL_CHECK_FAILED,
    STARTING_PRODUCTION,
    APACHE_STOP_WARNING,
    SERVER_STOPPED,
    SERVER_ERROR,
    PROXY_ERROR,
    BACKEND_UNAVAILABLE,
    BACKEND_TIMEOUT,
    FEATURE_WEB_SERVER,
    FEATURE_SSL,
    FEATURE_STATIC,
    FEATURE_API,
    FEATURE_DOCS,
    FEATURE_APACHE_REPLACE,
    STATUS_HEALTHY,
    STATUS_RUNNING,
    STATUS_ACTIVE,
    STATUS_ENABLED,
    STATUS_DISABLED,
    IMPORT_ERROR,
    FILE_NOT_FOUND,
    LOG_PROXYING_API,
    LOG_PROXYING_QUERY,
    LOG_STATIC_MOUNTED,
    API_HEALTH_RESPONSE,
    API_SERVER_INFO,
)

# Configure logging / Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=SERVER_TITLE,
    description=SERVER_DESCRIPTION,
    version=SERVER_VERSION,
)

# Setup security middleware / Настройка промежуточного ПО безопасности
setup_security(app)

# Configuration / Конфигурация
TARGET_SERVER = str(SERVER_CONFIG["target_server"])
TIMEOUT = float(SERVER_CONFIG["timeout"])
STATIC_ROOT = Path(
    SERVER_CONFIG["static_root"]
)  # Same as Apache DocumentRoot / Как в Apache DocumentRoot

# Mount static files (like Apache DocumentRoot) / Подключение статических файлов (как в Apache DocumentRoot)
if STATIC_ROOT.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_ROOT)), name="static")
    logger.info(LOG_STATIC_MOUNTED.format(STATIC_ROOT))


async def proxy_request(request: Request, path: str = ""):
    """Proxy request to backend application / Проксирование запроса к бэкенд приложению"""
    try:
        # Build target URL / Создание целевого URL
        if path:
            target_url = f"{TARGET_SERVER}/{path}"
        else:
            target_url = TARGET_SERVER

        # Prepare headers / Подготовка заголовков
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        # Read request body / Чтение тела запроса
        body = await request.body()

        # Make request to target server / Выполнение запроса к целевому серверу
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.request(
                method=request.method,
                url=str(target_url),
                headers=headers,
                content=body,
                params=request.query_params,
            )

            # Return response from target server / Возврат ответа от целевого сервера
            response_headers = dict(response.headers)
            response_headers.pop("content-length", None)

            content = response.content
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    import json

                    content = json.dumps(response.json()).encode("utf-8")
                except Exception:
                    content = response.text.encode("utf-8")

            return Response(
                content=content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type", "text/plain"),
            )

    except httpx.ConnectError:
        logger.error(f"Cannot connect to backend server at {TARGET_SERVER}")
        raise HTTPException(status_code=502, detail=BACKEND_UNAVAILABLE)
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to backend server at {TARGET_SERVER}")
        raise HTTPException(status_code=504, detail=BACKEND_TIMEOUT)
    except Exception as e:
        logger.error(PROXY_ERROR.format(str(e)))
        raise HTTPException(status_code=500, detail=PROXY_ERROR.format(str(e)))


# Serve static files directly (like Apache) / Обслуживание статических файлов напрямую (как в Apache)
@app.get("/{filename:path}")
async def serve_static_files(request: Request, filename: str = ""):
    """Serve static files directly from DocumentRoot / Обслуживание статических файлов из DocumentRoot"""
    if not filename:
        filename = "index.html"

    file_path = Path(STATIC_ROOT) / filename

    # Check if file exists and serve it / Проверка существования файла и его обслуживание
    if Path(file_path).exists() and Path(file_path).is_file():
        return FileResponse(str(file_path))

    # If file doesn't exist, proxy to backend / Если файл не существует, проксирование к бэкенду
    logger.info(FILE_NOT_FOUND.format(filename))
    return await proxy_request(request, filename)


# API routes that should always proxy to backend / API маршруты, которые всегда проксируются к бэкенду
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_api_routes(request: Request, path: str = ""):
    """Proxy API routes to backend / Проксирование API маршрутов к бэкенду"""
    logger.info(
        LOG_PROXYING_API.format(request.method, request.url, TARGET_SERVER, path)
    )
    return await proxy_request(request, f"api/{path}")


@app.api_route("/query/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_query_routes(request: Request, path: str = ""):
    """Proxy query routes to backend / Проксирование query маршрутов к бэкенду"""
    logger.info(
        LOG_PROXYING_QUERY.format(request.method, request.url, TARGET_SERVER, path)
    )
    return await proxy_request(request, f"query/{path}")


# Health check endpoint / Эндпоинт проверки состояния
@app.get("/health")
async def health_check():
    """Health check endpoint / Эндпоинт проверки состояния"""
    response = API_HEALTH_RESPONSE.copy()
    response["features"]["static_serving"] = Path(STATIC_ROOT).exists()
    response["features"]["proxy_enabled"] = bool(FEATURES["api_proxy_enabled"])
    response["features"]["document_root"] = str(STATIC_ROOT)
    response["features"]["backend_target"] = str(TARGET_SERVER)
    response["features"]["security_enabled"] = bool(FEATURES["security_enabled"])
    response["features"]["monitoring_enabled"] = bool(FEATURES["monitoring_enabled"])
    response["features"]["rate_limiting_enabled"] = bool(
        FEATURES["rate_limiting_enabled"]
    )
    response["features"]["ip_blocking_enabled"] = bool(FEATURES["ip_blocking_enabled"])
    response["features"]["threat_detection_enabled"] = bool(
        FEATURES["threat_detection_enabled"]
    )
    response["features"]["static_serving_enabled"] = bool(
        FEATURES["static_serving_enabled"]
    )
    response["features"]["ssl_enabled"] = bool(FEATURES["ssl_enabled"])
    return response


# Server information / Информация о сервере
@app.get("/")
async def server_info():
    """Server information page / Страница информации о сервере"""
    response = API_SERVER_INFO.copy()
    response["config"]["static_root"] = str(STATIC_ROOT)
    response["config"]["backend_server"] = str(TARGET_SERVER)
    response["config"]["ssl_enabled"] = bool(SERVER_CONFIG["ssl_enabled"])
    response["config"]["security_enabled"] = bool(FEATURES["security_enabled"])
    response["config"]["timeout"] = float(SERVER_CONFIG["timeout"])
    return response


# Security statistics endpoint / Эндпоинт статистики безопасности
@app.get("/security/stats")
async def security_stats() -> Dict[str, Any]:
    """Security statistics endpoint / Эндпоинт статистики безопасности"""
    return security_manager.get_security_stats()


# Attack monitoring endpoint / Эндпоинт мониторинга атак
@app.get("/monitoring/stats")
async def monitoring_stats() -> Dict[str, Any]:
    """Attack monitoring statistics / Статистика мониторинга атак"""
    return attack_monitor.get_monitoring_stats()


# Attack analysis endpoint / Эндпоинт анализа атак
@app.get("/monitoring/analysis")
async def attack_analysis(time_window_hours: int = 24) -> Dict[str, Any]:
    """Attack pattern analysis / Анализ паттернов атак"""
    return attack_monitor.analyze_attack_patterns(time_window_hours)


# High threat IPs endpoint / Эндпоинт IP с высокими угрозами
@app.get("/monitoring/high-threat-ips")
async def high_threat_ips(threshold: int = None) -> list:
    """Get high threat IP addresses / Получить IP-адреса с высокими угрозами"""
    return attack_monitor.get_high_threat_ips(threshold)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=443,
        ssl_certfile="certs/cert.pem",
        ssl_keyfile="certs/key.pem",
    )
