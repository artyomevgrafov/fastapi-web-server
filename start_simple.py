#!/usr/bin/env python3
"""
Simple FastAPI Security Proxy Startup Script
Basic functionality test without complex dependencies
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
    description="Simple security proxy server",
    version="1.0.0",
)

# Basic configuration
TARGET_SERVER = "http://127.0.0.1:8097"
STATIC_ROOT = Path("data/htdocs")
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

# Create test static file if it doesn't exist
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

    # Add security headers
    security_headers = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    }

    for header, value in security_headers.items():
        response.headers[header] = value

    return response


async def proxy_request(request: Request, path: str = ""):
    """Simple proxy request to backend"""
    try:
        # Build target URL
        if path:
            target_url = f"{TARGET_SERVER}/{path}"
        else:
            target_url = TARGET_SERVER

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
                url=str(target_url),
                headers=headers,
                content=body,
                params=request.query_params,
            )

            # Return response from target server
            response_headers = dict(response.headers)
            response_headers.pop("content-length", None)

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type", "text/plain"),
            )

    except httpx.ConnectError:
        logger.error(f"Cannot connect to backend server at {TARGET_SERVER}")
        raise HTTPException(status_code=502, detail="Backend server unavailable")
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to backend server at {TARGET_SERVER}")
        raise HTTPException(status_code=504, detail="Backend server timeout")
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {e}")


# Serve static files
@app.get("/{filename:path}")
async def serve_static_files(request: Request, filename: str = ""):
    """Serve static files with ETag support"""
    if not filename:
        filename = "index.html"

    file_path = Path(STATIC_ROOT) / filename

    if file_path.exists() and file_path.is_file():
        # Generate ETag
        stat = file_path.stat()
        etag_content = f"{file_path.name}-{stat.st_mtime}-{stat.st_size}"
        etag = hashlib.md5(etag_content.encode()).hexdigest()

        # Check If-None-Match
        if_none_match = request.headers.get("if-none-match")
        if if_none_match and if_none_match == etag:
            return Response(status_code=304)

        headers = {
            "Accept-Ranges": "bytes",
            "ETag": etag,
            "Cache-Control": "public, max-age=3600",
        }

        return FileResponse(str(file_path), headers=headers)

    # If file doesn't exist, proxy to backend
    return await proxy_request(request, filename)


# API routes proxy
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_api_routes(request: Request, path: str = ""):
    """Proxy API routes to backend"""
    return await proxy_request(request, f"api/{path}")


# Health check endpoint
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
        },
    }


# Server information
@app.get("/")
async def server_info():
    """Server information page"""
    return {
        "server": "FastAPI Security Proxy",
        "version": "1.0.0",
        "description": "Simple security proxy with static file serving",
        "endpoints": {
            "/health": "Health check",
            "/docs": "API documentation",
            "/api/*": "Proxy to backend API",
            "/*": "Static file serving",
        },
    }


def main():
    """Start the server"""
    try:
        print("Starting FastAPI Security Proxy")
        print(f"Static files: {STATIC_ROOT}")
        print(f"Backend proxy: {TARGET_SERVER}")
        print("Access: http://localhost:8080")
        print("Docs: http://localhost:8080/docs")
        print("Press Ctrl+C to stop the server")

        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info", access_log=True)

    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Failed to start server: {e}")


if __name__ == "__main__":
    main()
