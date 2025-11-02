"""
Production Middleware for Security and Performance
Промежуточное ПО для безопасности и производительности
"""

from typing import Dict, Any, Optional, List, Tuple
from fastapi import FastAPI

import time
import gzip
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware for production
    Промежуточное ПО заголовков безопасности для продакшена
    """

    def __init__(self, app: ASGIApp, enable_hsts: bool = True) -> None:
        super().__init__(app)
        self.enable_hsts: bool = enable_hsts
        self.security_headers: Dict[str, str] = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Cross-Origin-Embedder-Policy": "require-corp",
        }

        if self.enable_hsts:
            self.security_headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value

        # Content Security Policy
        csp: str = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests"
        )
        response.headers["Content-Security-Policy"] = csp

        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]

        return response


class GZipCompressionMiddleware(BaseHTTPMiddleware):
    """
    GZip compression middleware with configurable settings
    Промежуточное ПО сжатия GZip с настраиваемыми параметрами
    """

    def __init__(
        self, app: ASGIApp, minimum_size: int = 500, compresslevel: int = 6
    ) -> None:
        super().__init__(app)
        self.minimum_size: int = minimum_size
        self.compresslevel: int = compresslevel

    async def dispatch(self, request: Request, call_next) -> Response:
        # Check if client accepts gzip encoding
        accept_encoding: str = request.headers.get("Accept-Encoding", "")
        supports_gzip: bool = "gzip" in accept_encoding

        if not supports_gzip:
            return await call_next(request)

        response: Response = await call_next(request)

        # Check if response should be compressed
        content_type: str = response.headers.get("content-type", "")
        content_length: str | None = response.headers.get("content-length")

        # Skip compression for small responses or already compressed content
        if (
            content_length and int(content_length) < self.minimum_size
        ) or "gzip" in response.headers.get("content-encoding", ""):
            return response

        # Compressible content types
        compressible_types: set[str] = {
            "text/plain",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "application/json",
            "application/xml",
            "application/xhtml+xml",
            "image/svg+xml",
        }

        should_compress: bool = any(ct in content_type for ct in compressible_types)

        if should_compress and response.body:
            compressed_body: bytes = gzip.compress(
                response.body, compresslevel=self.compresslevel
            )
            response.body = compressed_body
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed_body))
            response.headers["vary"] = "Accept-Encoding"

        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Cache control middleware for static and dynamic content
    Промежуточное ПО контроля кэширования для статического и динамического контента
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        # Skip cache control for API endpoints
        if request.url.path.startswith(("/api/", "/security/", "/monitoring/")):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        else:
            # Static files cache control
            if request.url.path.startswith(("/static/", "/css/", "/js/", "/images/")):
                response.headers["Cache-Control"] = (
                    "public, max-age=31536000, immutable"
                )
            else:
                # HTML pages - short cache
                response.headers["Cache-Control"] = "public, max-age=300"

        return response


class ForwardedHeadersMiddleware(BaseHTTPMiddleware):
    """
    Process X-Forwarded-* headers for reverse proxy setups
    Обработка заголовков X-Forwarded-* для обратного прокси
    """

    def __init__(
        self, app: ASGIApp, trusted_proxies: Optional[List[str]] = None
    ) -> None:
        super().__init__(app)
        self.trusted_proxies: List[str] = trusted_proxies or ["127.0.0.1", "localhost"]

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get client IP from X-Forwarded-For if behind proxy
        forwarded_for: str | None = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            client_ip: str = forwarded_for.split(",")[0].strip()
            request.scope["client"] = (client_ip, request.scope["client"][1])

        # Get protocol from X-Forwarded-Proto
        forwarded_proto: str | None = request.headers.get("X-Forwarded-Proto")
        if forwarded_proto:
            request.scope["scheme"] = forwarded_proto

        # Get host from X-Forwarded-Host
        forwarded_host: str | None = request.headers.get("X-Forwarded-Host")
        if forwarded_host:
            request.scope["headers"] = [
                (b"host", forwarded_host.encode()) if key == b"host" else (key, value)
                for key, value in request.scope["headers"]
            ]

        response: Response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log HTTP requests with timing information
    Логирование HTTP запросов с информацией о времени
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time: float = time.time()

        response: Response = await call_next(request)

        process_time: float = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log request details (in production, use proper logging)
        print(
            f"{request.method} {request.url.path} "
            f"{response.status_code} {process_time:.3f}s"
        )

        return response


def setup_production_middleware(app: FastAPI) -> None:
    """
    Setup all production middleware
    Настройка всего производственного промежуточного ПО
    """
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # GZip compression
    app.add_middleware(GZipCompressionMiddleware)

    # Cache control
    app.add_middleware(CacheControlMiddleware)

    # Forwarded headers for reverse proxy
    app.add_middleware(ForwardedHeadersMiddleware)

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    return None
