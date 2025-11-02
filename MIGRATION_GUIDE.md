# Migration Guide: Apache to FastAPI

## Overview

This comprehensive guide will help you migrate from Apache HTTP Server to FastAPI, a modern, high-performance web framework for building APIs and web applications with Python.

## Benefits of Migration

- **Performance**: FastAPI is built on Starlette and Uvicorn, offering excellent performance
- **Automatic Documentation**: Interactive API docs with Swagger UI and ReDoc
- **Modern Standards**: Built-in support for OpenAPI, JSON Schema, and async/await
- **Developer Experience**: Type hints, automatic validation, and excellent IDE support
- **Python Ecosystem**: Access to the rich Python library ecosystem

## Prerequisites

- Python 3.7+
- Administrative access to stop Apache service
- Basic understanding of Python and web APIs

## Migration Steps

### 1. Stop Apache Service

**Windows:**
```cmd
sc stop "Apache2.4"
```

**Linux:**
```bash
sudo systemctl stop apache2
# or
sudo service apache2 stop
```

### 2. Install Dependencies

```bash
cd httpd\fastapi
pip install -r requirements.txt
```

### 3. Test the Migration

Run the automated migration script:
```cmd
migrate.bat
```

Or manually:
```bash
python start_server.py
```

### 4. Verify Functionality

Test the server is working:
```bash
python test_server.py
```

## Configuration Mapping

### Apache vs FastAPI Equivalents

| Apache Configuration | FastAPI Equivalent |
|---------------------|-------------------|
| `DocumentRoot` | `static/` directory |
| `DirectoryIndex` | `@app.get("/")` route |
| `.htaccess` | Route handlers in `app/main.py` |
| Virtual Hosts | Multiple FastAPI apps or middleware |
| `Alias` directives | Additional route handlers |
| CGI scripts | Python route handlers |
| `ErrorDocument` | FastAPI exception handlers |

### Port Configuration

Apache typically runs on port 80. FastAPI is configured to use port 80 by default in `config.py`:

```python
PORT: int = 80
```

## File Structure Migration

### Static Files

**Apache:**
```
/htdocs/
├── index.html
├── css/
├── js/
└── images/
```

**FastAPI:**
```
/static/
├── index.html
├── css/
├── js/
└── images/
```

Static files are automatically served at `/static/` path.

### Dynamic Content

**Apache (PHP example):**
```php
<?php
echo "Hello, " . $_GET['name'];
?>
```

**FastAPI:**
```python
@app.get("/hello")
async def hello(name: str = "World"):
    return {"message": f"Hello, {name}"}
```

## Common Migration Scenarios

### 1. Simple HTML Website

**Before (Apache):**
- Files in `htdocs/` directory
- Accessed via `http://localhost/file.html`

**After (FastAPI):**
- Move files to `static/` directory
- Access via `http://localhost/static/file.html`
- Or create routes to serve files from root

### 2. REST API

**Before (Apache + PHP):**
```php
// api/users.php
$users = get_users_from_database();
header('Content-Type: application/json');
echo json_encode($users);
```

**After (FastAPI):**
```python
@app.get("/api/users")
async def get_users():
    users = get_users_from_database()
    return users
```

### 3. Form Processing

**Before (Apache + PHP):**
```php
// process_form.php
$name = $_POST['name'];
$email = $_POST['email'];
// Process form data...
```

**After (FastAPI):**
```python
from pydantic import BaseModel

class FormData(BaseModel):
    name: str
    email: str

@app.post("/process-form")
async def process_form(data: FormData):
    # Process form data...
    return {"status": "success", "message": "Form processed"}
```

## Advanced Configuration

### Custom Middleware

Replace Apache modules with FastAPI middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication

Replace Apache `.htaccess` authentication:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.get("/secure")
async def secure_endpoint(credentials: HTTPBasicCredentials = Depends(security)):
    # Verify credentials
    if not authenticate(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Access granted"}
```

## Performance Considerations

### 1. Static File Serving

For high-traffic static file serving, consider using a CDN or dedicated static file server alongside FastAPI.

### 2. Caching

Implement caching strategies:
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
```

### 3. Database Connections

Use connection pooling and async database drivers for better performance.

## Troubleshooting

### Common Issues

1. **Port 80 Already in Use**
   - Stop Apache service completely
   - Check for other services using port 80
   - Use a different port temporarily

2. **Permission Errors**
   - Run as Administrator (Windows)
   - Use `sudo` (Linux)
   - Configure proper file permissions

3. **Static Files Not Serving**
   - Verify files are in `static/` directory
   - Check file permissions
   - Verify route configuration

4. **API Endpoints Not Working**
   - Check FastAPI logs
   - Verify route definitions
   - Test with `/docs` interface

### Debugging

Enable debug mode in `config.py`:
```python
class DevelopmentConfig(ServerConfig):
    RELOAD: bool = True
    LOG_LEVEL: str = "debug"
```

Set environment variable:
```bash
set FASTAPI_ENV=development
```

## Production Deployment

### 1. Process Management

Use process managers:
- **Windows**: Windows Service
- **Linux**: systemd, supervisord

### 2. Reverse Proxy

For production, use a reverse proxy like Nginx:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. SSL/TLS

Configure SSL through reverse proxy or use FastAPI with SSL directly.

## Monitoring and Logging

### Access Logs

FastAPI provides built-in access logging. Configure in `config.py`:
```python
LOG_LEVEL: str = "info"
```

### Custom Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Rollback Plan

If you need to revert to Apache:

1. Stop FastAPI server
2. Start Apache service
3. Restore original configuration files

**Windows:**
```cmd
sc start "Apache2.4"
```

**Linux:**
```bash
sudo systemctl start apache2
```

## Support

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Community Support: GitHub Discussions, Stack Overflow
- Migration Assistance: Consult the provided examples and test scripts

## Next Steps

1. ✅ Test basic functionality with `test_server.py`
2. ✅ Migrate static files to `static/` directory
3. ✅ Convert dynamic pages to FastAPI routes
4. ✅ Configure production deployment
5. ✅ Set up monitoring and logging
6. ✅ Performance testing and optimization

Remember to test thoroughly in a development environment before deploying to production.