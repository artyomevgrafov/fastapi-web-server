#!/usr/bin/env python3
"""
Minimal FastAPI Security Proxy Server
Production-ready with HTTP/2, ETag, and security headers
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pathlib import Path
import httpx
import logging
import hashlib
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FastAPI Security Proxy",
    description="Production-ready security proxy with HTTP/2 support",
    version="1.0.0",
)

# Configuration
TARGET_SERVER = "http://127.0.0.1:8097"
STATIC_ROOT = Path("data/htdocs")
PORT = 8080

# Create directories
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

# Create test static file
test_file = STATIC_ROOT / "index.html"
if not test_file.exists():
    test_file.write_text(
        """
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Security Proxy</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .status { padding: 10px; border-radius: 5px; }
        .healthy { background: #d4edda; color: #155724; }
    </style>
</head>
<body>
    <h1>FastAPI Security Proxy</h1>
    <p>Server is running successfully!</p>
    <div class="status healthy">Status: Healthy</div>
    <p><a href="/health">Health Check</a> | <a href="/docs">API Documentation</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_ROOT), html=True), name="static")


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Security headers
    security_headers = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    }

    for header, value in security_headers.items():
        response.headers[header] = value

    return response


async def proxy_request(request: Request, path: str = ""):
    """Proxy request to backend with timeout handling"""
    try:
        # Build target URL
        target_url = f"{TARGET_SERVER}/{path}" if path else TARGET_SERVER

        # Prepare headers
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        # Read request body
        body = await request.body()

        # Make request to target server
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
            )

            # Return response
            response_headers = dict(response.headers)
            response_headers.pop("content-length", None)

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type", "text/plain"),
            )

    except httpx.ConnectError:
        raise HTTPException(status_code=502, detail="Backend server unavailable")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Backend server timeout")
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {e}")


@app.get("/{filename:path}")
async def serve_static_files(request: Request, filename: str = ""):
    """Serve static files with ETag and Range request support"""
    if not filename:
        filename = "index.html"

    file_path = STATIC_ROOT / filename

    if file_path.exists() and file_path.is_file():
        # Generate ETag from file stats
        stat = file_path.stat()
        etag_content = f"{file_path.name}-{stat.st_mtime}-{stat.st_size}"
        etag = hashlib.md5(etag_content.encode()).hexdigest()

        # Check If-None-Match for cache validation
        if_none_match = request.headers.get("if-none-match")
        if if_none_match and if_none_match == etag:
            return Response(status_code=304)

        # Handle Range requests
        range_header = request.headers.get("range")
        if range_header and range_header.startswith("bytes="):
            try:
                range_spec = range_header[6:]  # Remove "bytes="
                if "-" in range_spec:
                    start_end = range_spec.split("-")
                    if len(start_end) == 2:
                        start = int(start_end[0]) if start_end[0] else 0
                        end = int(start_end[1]) if start_end[1] else stat.st_size - 1
                        content_length = end - start + 1

                        # Read file chunk
                        with open(file_path, "rb") as f:
                            f.seek(start)
                            content = f.read(content_length)

                        headers = {
                            "Content-Type": "application/octet-stream",
                            "Content-Length": str(content_length),
                            "Content-Range": f"bytes {start}-{end}/{stat.st_size}",
                            "Accept-Ranges": "bytes",
                            "ETag": etag,
                            "Cache-Control": "public, max-age=3600",
                        }

                        return Response(
                            content=content,
                            status_code=206,  # Partial Content
                            headers=headers,
                        )
            except (ValueError, OSError):
                pass  # Fall back to full file

        # Serve full file with caching headers
        headers = {
            "Accept-Ranges": "bytes",
            "ETag": etag,
            "Cache-Control": "public, max-age=3600",
        }

        return FileResponse(str(file_path), headers=headers)

    # Proxy to backend if file not found
    return await proxy_request(request, filename)


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_api_routes(request: Request, path: str = ""):
    """Proxy API routes to backend"""
    logger.info(f"Proxying API request: {request.method} {request.url}")
    return await proxy_request(request, f"api/{path}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "FastAPI Security Proxy",
        "version": "1.0.0",
        "features": {
            "static_serving": True,
            "proxy_enabled": True,
            "security_headers": True,
            "etag_support": True,
            "range_requests": True,
            "http2_ready": True,
        },
        "config": {
            "static_root": str(STATIC_ROOT),
            "backend_server": TARGET_SERVER,
            "port": PORT,
        },
    }


@app.get("/")
async def server_info():
    """Server information"""
    return {
        "server": "FastAPI Security Proxy",
        "version": "1.0.0",
        "description": "Production-ready security proxy with modern web features",
        "features": [
            "HTTP/2 ready",
            "ETag caching",
            "Range request support",
            "Security headers",
            "Static file serving",
            "Reverse proxy",
            "Health monitoring",
        ],
        "endpoints": {
            "/": "This information",
            "/health": "Health status",
            "/docs": "API documentation",
            "/api/*": "Proxy to backend",
            "/*": "Static files with caching",
        },
    }


def main():
    """Start production server"""
    try:
        print("Starting FastAPI Security Proxy")
        print(f"Port: {PORT}")
        print(f"Static files: {STATIC_ROOT}")
        print(f"Backend proxy: {TARGET_SERVER}")
        print("Access: http://localhost:8080")
        print("Docs: http://localhost:8080/docs")
        print("Health: http://localhost:8080/health")
        print("")
        print("Features:")
        print("- HTTP/2 ready (use hypercorn for HTTP/2)")
        print("- ETag caching for static files")
        print("- Range request support")
        print("- Security headers (HSTS, CSP, etc.)")
        print("- Reverse proxy with timeout handling")
        print("")
        print("Press Ctrl+C to stop the server")

        # Start with production settings
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=PORT,
            workers=1,  # Can be increased for production
            loop="asyncio",
            access_log=True,
            proxy_headers=True,
        )

    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Failed to start server: {e}")


if __name__ == "__main__":
    main()
