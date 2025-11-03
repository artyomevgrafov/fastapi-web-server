"""
Enhanced Middleware for Modern Web Server
Production-ready middleware with Brotli compression, HTTP/2 optimization, and comprehensive security
"""

from fastapi import FastAPI

import time
import gzip
import brotli
from typing import Dict, Any, Optional, List, Set, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message
from pathlib import Path
import hashlib


class BrotliCompressionMiddleware(BaseHTTPMiddleware):
    """
    Modern compression middleware with Brotli and GZip support
    Prioritizes Brotli for better compression ratios
    """

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 500,
        brotli_quality: int = 4,
        gzip_level: int = 6,
    ) -> None:
        super().__init__(app)
        self.minimum_size: int = minimum_size
        self.brotli_quality: int = brotli_quality
        self.gzip_level: int = gzip_level

        # Compressible content types
        self.compressible_types: Set[str] = {
            "text/plain",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "application/json",
            "application/xml",
            "application/xhtml+xml",
            "image/svg+xml",
            "font/woff",
            "font/woff2",
            "application/font-woff",
            "application/font-woff2",
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle compression with Brotli priority"""
        # Check client compression support
        accept_encoding: str = request.headers.get("Accept-Encoding", "").lower()
        supports_brotli: bool = "br" in accept_encoding
        supports_gzip: bool = "gzip" in accept_encoding

        if not (supports_brotli or supports_gzip):
            return await call_next(request)

        response: Response = await call_next(request)

        # Skip if already compressed or streaming
        if (
            "content-encoding" in response.headers
            or not hasattr(response, "body")
            or not response.body
        ):
            return response

        # Check content size
        content_length: Optional[str] = response.headers.get("content-length")
        if content_length and int(content_length) < self.minimum_size:
            return response

        # Check content type
        content_type: str = response.headers.get("content-type", "").lower()
        should_compress: bool = any(
            ct in content_type for ct in self.compressible_types
        )

        if not should_compress:
            return response

        # Apply compression based on client support
        original_body: bytes = response.body
        compressed_body: bytes
        encoding: str

        if supports_brotli:
            compressed_body = brotli.compress(
                original_body, quality=self.brotli_quality
            )
            encoding = "br"
        elif supports_gzip:
            compressed_body = gzip.compress(
                original_body, compresslevel=self.gzip_level
            )
            encoding = "gzip"
        else:
            return response

        # Only compress if we achieve meaningful compression
        if len(compressed_body) >= len(original_body):
            return response

        # Update response with compressed content
        response.body = compressed_body
        response.headers["content-encoding"] = encoding
        response.headers["content-length"] = str(len(compressed_body))
        response.headers["vary"] = "Accept-Encoding"

        return response


class ModernSecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security headers middleware with modern best practices
    """

    def __init__(self, app: ASGIApp, enable_hsts: bool = True) -> None:
        super().__init__(app)
        self.enable_hsts: bool = enable_hsts
        self.setup_security_headers()

    def setup_security_headers(self) -> None:
        """Configure comprehensive security headers"""
        self.security_headers: Dict[str, str] = {
            # Frame protection
            "X-Frame-Options": "DENY",
            # MIME type protection
            "X-Content-Type-Options": "nosniff",
            # XSS protection
            "X-XSS-Protection": "1; mode=block",
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Permissions policy
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "payment=(), usb=(), magnetometer=(), "
                "gyroscope=(), accelerometer=()"
            ),
            # Cross-origin policies
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Cross-Origin-Embedder-Policy": "require-corp",
            # Cache control for sensitive content
            "Cache-Control": "no-cache, no-store, must-revalidate",
        }

        if self.enable_hsts:
            self.security_headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

    def get_content_security_policy(self) -> str:
        """Generate comprehensive Content Security Policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: blob: https:; "
            "connect-src 'self' ws: wss:; "
            "media-src 'self'; "
            "object-src 'none'; "
            "child-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests; "
            "block-all-mixed-content"
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply comprehensive security headers"""
        response: Response = await call_next(request)

        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value

        # Add Content Security Policy
        response.headers["Content-Security-Policy"] = self.get_content_security_policy()

        # Remove identifying headers
        headers_to_remove = {"server", "x-powered-by", "x-aspnet-version"}
        for header in headers_to_remove:
            if header in response.headers:
                del response.headers[header]

        return response


class SmartCacheMiddleware(BaseHTTPMiddleware):
    """
    Intelligent caching middleware with ETag, Cache-Control, and Range support
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.static_extensions: Set[str] = {
            ".css",
            ".js",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".pdf",
            ".txt",
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply intelligent caching strategies"""
        response: Response = await call_next(request)

        # Skip cache manipulation for API endpoints
        if request.url.path.startswith(("/api/", "/security/", "/monitoring/")):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response

        # Static files - long cache with versioning
        if any(request.url.path.endswith(ext) for ext in self.static_extensions):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            response.headers["Accept-Ranges"] = "bytes"

            # Generate ETag if not present
            if "etag" not in response.headers and hasattr(response, "body"):
                etag = self.generate_etag(response.body)
                response.headers["ETag"] = etag

        # HTML pages - moderate cache
        elif request.url.path.endswith((".html", ".htm")):
            response.headers["Cache-Control"] = "public, max-age=300, must-revalidate"
            response.headers["Vary"] = "Accept-Encoding"

        # Default - no cache
        else:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

        return response

    def generate_etag(self, content: bytes) -> str:
        """Generate strong ETag from content"""
        content_hash = hashlib.sha256(content).hexdigest()
        return f'"{content_hash}"'


class HTTP2OptimizationMiddleware(BaseHTTPMiddleware):
    """
    HTTP/2 optimization middleware with server push hints and connection optimization
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply HTTP/2 optimizations"""
        response: Response = await call_next(request)

        # Add HTTP/2 specific headers
        response.headers["Link"] = self.get_resource_hints(request)

        # Enable HTTP/2 server push for critical resources
        if request.url.path == "/":
            push_resources = self.get_push_resources()
            if push_resources:
                response.headers["Link"] = push_resources

        return response

    def get_resource_hints(self, request: Request) -> str:
        """Generate resource hints for HTTP/2 optimization"""
        hints = []

        if request.url.path == "/":
            # Preload critical resources
            hints.extend(
                [
                    "</static/css/main.css>; rel=preload; as=style",
                    "</static/js/app.js>; rel=preload; as=script",
                    "</static/fonts/webfont.woff2>; rel=preload; as=font; crossorigin",
                ]
            )

        return ", ".join(hints)

    def get_push_resources(self) -> str:
        """Get resources to push via HTTP/2 server push"""
        return ", ".join(
            [
                "</static/css/main.css>; rel=preload",
                "</static/js/app.js>; rel=preload",
            ]
        )


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Performance monitoring with detailed timing and HTTP/2 metrics
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Monitor request performance"""
        start_time: float = time.time()

        # Capture request details
        method: str = request.method
        path: str = request.url.path
        user_agent: str = request.headers.get("user-agent", "unknown")

        response: Response = await call_next(request)

        # Calculate timing
        process_time: float = time.time() - start_time

        # Add performance headers
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        response.headers["X-Request-ID"] = self.generate_request_id()

        # Log performance metrics
        self.log_performance(
            method, path, response.status_code, process_time, user_agent
        )

        return response

    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]

    def log_performance(
        self, method: str, path: str, status: int, duration: float, user_agent: str
    ) -> None:
        """Log detailed performance metrics"""
        print(f"📊 {method} {path} {status} {duration:.3f}s | UA: {user_agent[:50]}...")


def setup_enhanced_middleware(app: FastAPI) -> None:
    """
    Setup all enhanced middleware for modern web server
    """
    # Compression (Brotli + GZip)
    app.add_middleware(BrotliCompressionMiddleware)

    # Comprehensive security headers
    app.add_middleware(ModernSecurityHeadersMiddleware)

    # Intelligent caching
    app.add_middleware(SmartCacheMiddleware)

    # HTTP/2 optimization
    app.add_middleware(HTTP2OptimizationMiddleware)

    # Performance monitoring
    app.add_middleware(PerformanceMonitoringMiddleware)
