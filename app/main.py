from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pathlib import Path
import httpx
import logging
import hashlib
from typing import Dict, Any, List

from datetime import datetime, timezone

from .monitoring import MetricsMiddleware, metrics_endpoint

from .security import security_manager, setup_security
from .monitoring import attack_monitor
from .middleware import setup_production_middleware
from .config import SERVER_CONFIG, FEATURES
from .messages import (
    SERVER_TITLE,
    SERVER_DESCRIPTION,
    SERVER_VERSION,
    PROXY_ERROR,
    BACKEND_UNAVAILABLE,
    BACKEND_TIMEOUT,
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

app: FastAPI = FastAPI(
    title=SERVER_TITLE,
    description=SERVER_DESCRIPTION,
    version=SERVER_VERSION,
)

# Setup security middleware / Настройка промежуточного ПО безопасности
setup_security(app)

# Setup production middleware / Настройка производственного промежуточного ПО
_ = setup_production_middleware(app)

# Add Prometheus metrics middleware
# app.add_middleware(MetricsMiddleware)  # Temporarily disabled due to type issues

# Configuration / Конфигурация
TARGET_SERVER: str = str(SERVER_CONFIG["target_server"])
TIMEOUT: float = float(SERVER_CONFIG["timeout"])
STATIC_ROOT: Path = Path(
    str(SERVER_CONFIG["static_root"])
)  # Same as Apache DocumentRoot / Как в Apache DocumentRoot

# Mount static files with cache headers / Подключение статических файлов с заголовками кэширования
if STATIC_ROOT.exists():
    app.mount(
        "/static", StaticFiles(directory=str(STATIC_ROOT), html=True), name="static"
    )
    logger.info(LOG_STATIC_MOUNTED.format(STATIC_ROOT))


async def proxy_request(request: Request, path: str = "") -> Response:
    """Proxy request to backend application / Проксирование запроса к бэкенд приложению"""
    try:
        # Build target URL / Создание целевого URL
        if path:
            target_url = f"{TARGET_SERVER}/{path}"
        else:
            target_url = TARGET_SERVER

        # Prepare headers / Подготовка заголовков
        headers: Dict[str, str] = dict(request.headers)
        _ = headers.pop("host", None)
        _ = headers.pop("content-length", None)

        # Read request body / Чтение тела запроса
        body: bytes = await request.body()

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
            response_headers: Dict[str, str] = dict(response.headers)
            _ = response_headers.pop("content-length", None)

            content: bytes = response.content
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
async def serve_static_files(request: Request, filename: str = "") -> Response:
    """Serve static files directly from DocumentRoot / Обслуживание статических файлов из DocumentRoot"""
    if not filename:
        filename = "index.html"

    file_path: Path = Path(STATIC_ROOT) / filename

    # Check if file exists and serve it / Проверка существования файла и его обслуживание
    if Path(file_path).exists() and Path(file_path).is_file():
        return await serve_file_with_etag_and_range(request, file_path)

    # If file doesn't exist, proxy to backend / Если файл не существует, проксирование к бэкенду
    logger.info(FILE_NOT_FOUND.format(filename))
    return await proxy_request(request, filename)


async def serve_file_with_etag_and_range(request: Request, file_path: Path) -> Response:
    """Serve file with ETag and Range request support / Обслуживание файла с поддержкой ETag и Range запросов"""
    # Get file stats
    stat: Any = file_path.stat()
    file_size: int = stat.st_size
    last_modified: datetime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    # Generate ETag from file content hash and modification time
    etag_content: str = f"{file_path.name}-{stat.st_mtime}-{file_size}"
    etag: str = hashlib.md5(etag_content.encode()).hexdigest()

    # Check If-None-Match header for cache validation
    if_none_match: str | None = request.headers.get("if-none-match")
    if if_none_match and if_none_match == etag:
        return Response(status_code=304)

    # Check If-Modified-Since header
    if_modified_since: str | None = request.headers.get("if-modified-since")
    if if_modified_since:
        try:
            if_modified_since_dt: datetime = datetime.strptime(
                if_modified_since, "%a, %d %b %Y %H:%M:%S GMT"
            )
            if last_modified <= if_modified_since_dt.replace(tzinfo=timezone.utc):
                return Response(status_code=304)
        except ValueError:
            pass

    # Handle Range requests
    range_header: str | None = request.headers.get("range")
    if range_header and range_header.startswith("bytes="):
        try:
            # Parse range header: bytes=0-499, 500-999, etc.
            range_spec: str = range_header[6:]  # Remove "bytes="
            ranges: list[tuple[int, int]] = []

            for range_part in range_spec.split(","):
                if "-" in range_part:
                    start_end: list[str] = range_part.split("-")
                    if len(start_end) == 2:
                        start: int = int(start_end[0]) if start_end[0] else 0
                        end: int = int(start_end[1]) if start_end[1] else file_size - 1
                        ranges.append((start, min(end, file_size - 1)))

            if ranges:
                # For now, handle single range (most common case)
                start, end = ranges[0]
                content_length: int = end - start + 1

                # Read file chunk
                with open(file_path, "rb") as f:
                    _ = f.seek(start)
                    content: bytes = f.read(content_length)

                range_headers = {
                    "content-type": "application/octet-stream",
                    "content-length": str(content_length),
                    "content-range": f"bytes {start}-{end}/{file_size}",
                    "accept-ranges": "bytes",
                    "etag": etag,
                    "last-modified": last_modified.strftime(
                        "%a, %d %b %Y %H:%M:%S GMT"
                    ),
                    "cache-control": "public, max-age=3600",
                }

                return Response(
                    content=content,
                    status_code=206,  # Partial Content
                    headers=range_headers,
                )
        except (ValueError, IndexError, OSError):
            # Fall back to full file if range parsing fails
            pass

    # Serve full file with ETag and caching headers
    headers: Dict[str, str] = {
        "Accept-Ranges": "bytes",
        "ETag": etag,
        "Last-Modified": last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "Cache-Control": "public, max-age=3600",
    }

    return FileResponse(
        str(file_path),
        headers=headers,
    )


# API routes that should always proxy to backend / API маршруты, которые всегда проксируются к бэкенду
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_api_routes(request: Request, path: str = "") -> Response:
    """Proxy API routes to backend / Проксирование API маршрутов к бэкенду"""
    logger.info(
        LOG_PROXYING_API.format(request.method, request.url, TARGET_SERVER, path)
    )
    return await proxy_request(request, f"api/{path}")


@app.api_route("/query/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_query_routes(request: Request, path: str = "") -> Response:
    """Proxy query routes to backend / Проксирование query маршрутов к бэкенду"""
    logger.info(
        LOG_PROXYING_QUERY.format(request.method, request.url, TARGET_SERVER, path)
    )
    return await proxy_request(request, f"query/{path}")


# Health check endpoint / Эндпоинт проверки состояния
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint / Эндпоинт проверки состояния"""
    response: Dict[str, Any] = API_HEALTH_RESPONSE.copy()
    features: Dict[str, Any] = response["features"].copy()
    features["static_serving"] = str(STATIC_ROOT.exists())
    features["proxy_enabled"] = FEATURES["api_proxy_enabled"]
    features["document_root"] = str(STATIC_ROOT)
    features["backend_target"] = TARGET_SERVER
    features["security_enabled"] = FEATURES["security_enabled"]
    features["monitoring_enabled"] = FEATURES["monitoring_enabled"]
    features["rate_limiting_enabled"] = FEATURES["rate_limiting_enabled"]
    features["ip_blocking_enabled"] = FEATURES["ip_blocking_enabled"]
    features["threat_detection_enabled"] = FEATURES["threat_detection_enabled"]
    features["static_serving_enabled"] = FEATURES["static_serving_enabled"]
    features["ssl_enabled"] = FEATURES["ssl_enabled"]
    response["features"] = features
    return response


# Server information / Информация о сервере
@app.get("/")
async def server_info() -> Dict[str, Any]:
    """Server information page / Страница информации о сервере"""
    response: Dict[str, Any] = API_SERVER_INFO.copy()
    config: Dict[str, Any] = response["config"].copy()
    config["static_root"] = str(STATIC_ROOT)
    config["backend_server"] = TARGET_SERVER
    config["ssl_enabled"] = SERVER_CONFIG["ssl_enabled"]
    config["security_enabled"] = FEATURES["security_enabled"]
    config["timeout"] = str(SERVER_CONFIG["timeout"])
    response["config"] = config
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


# Prometheus metrics endpoint / Эндпоинт метрик Prometheus
@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint / Эндпоинт метрик Prometheus"""
    return metrics_endpoint()


# High threat IPs endpoint / Эндпоинт IP с высокими угрозами
@app.get("/monitoring/high-threat-ips")
async def high_threat_ips(threshold: int | None = None) -> List[Dict[str, Any]]:
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
