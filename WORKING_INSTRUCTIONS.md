# FastAPI Server - Working Instructions

## ✅ Project Status: FULLY WORKING

The FastAPI server has been successfully restored and all critical errors have been fixed. The server now supports both HTTP and HTTPS with automatic SSL certificate generation.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd httpd\fastapi
pip install -r requirements.txt
```

### 2. Start Server (HTTP)
```bash
python start.py
```

### 3. Start Server with SSL (HTTPS)
```bash
set FASTAPI_ENV=development
python start.py
```

## 📁 Project Structure
```
httpd/fastapi/
├── app/
│   ├── main.py              # Main FastAPI application
│   └── api.py               # API endpoints (users, math, echo)
├── certs/                   # SSL certificates (auto-generated)
├── static/                  # Static files (CSS, JS, images)
├── templates/               # HTML templates
├── config.py               # Server configuration
├── requirements.txt        # Python dependencies
├── start.py               # Main launcher (USE THIS)
├── ssl_utils.py           # SSL certificate utilities
├── manage_ssl.py          # SSL management tool
├── test_simple.py         # Simple test script
├── test_https_server.py   # HTTPS test script
└── documentation (*.md)
```

## 🔧 Key Features

### ✅ Working Features
- **FastAPI Server** - Running on port 8000
- **SSL/TLS Support** - Automatic self-signed certificate generation
- **API Endpoints** - Complete CRUD operations, math functions, echo
- **Auto Documentation** - Swagger UI at `/docs`
- **Static File Serving** - Files from `/static/` directory
- **Health Monitoring** - Health check endpoints
- **Configuration Management** - Environment-based settings

### 🔐 SSL/TLS Support
The server automatically generates self-signed SSL certificates:
- Certificates stored in `certs/` directory
- Automatic validation and regeneration
- Support for custom certificate parameters

## 🎯 Usage Instructions

### Starting the Server

**Basic HTTP Server:**
```bash
python start.py
```

**HTTPS Server with SSL:**
```bash
set FASTAPI_ENV=development
python start.py
```

**Custom Port (edit config.py):**
```python
PORT: int = 8080  # Change from 8000
```

### Managing SSL Certificates

**Generate New Certificates:**
```bash
python manage_ssl.py generate
```

**Validate Certificates:**
```bash
python manage_ssl.py validate
```

**Show Certificate Info:**
```bash
python manage_ssl.py info
```

### Testing the Server

**Simple Test (Recommended):**
```bash
python test_simple.py
```

**HTTPS Test:**
```bash
python test_https_server.py
```

**Manual Testing:**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## ⚙️ Configuration

### Environment Settings
Set `FASTAPI_ENV` environment variable:
- `development` - SSL enabled, auto-reload, debug logging
- `production` - SSL enabled, no reload, warning logging  
- `default` - No SSL, basic settings

### SSL Configuration (config.py)
```python
SSL_ENABLED: bool = True
SSL_CERT_FILE: str = "certs/cert.pem"
SSL_KEY_FILE: str = "certs/key.pem"
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use:**
- Change port in `config.py`
- Stop other services using port 8000

**SSL Certificate Errors:**
- Run `python manage_ssl.py generate --force`
- Check OpenSSL is installed

**Import Errors:**
- Ensure you're in the `httpd/fastapi` directory
- Run `pip install -r requirements.txt`

**Server Not Responding:**
- Use `test_simple.py` which includes retry logic
- Check firewall settings
- Verify server is actually running

### Debug Mode
For detailed logging, set in `config.py`:
```python
LOG_LEVEL: str = "debug"
```

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `GET /docs` - Interactive API documentation
- `GET /api/health` - Server health check

### User Management
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Utility Endpoints
- `GET /api/echo/{message}` - Echo messages
- `GET /api/math/square/{number}` - Calculate square
- `GET /api/math/cube/{number}` - Calculate cube

## 🔄 Migration from Apache

### File Locations
| Apache | FastAPI |
|--------|---------|
| `htdocs/` | `static/` |
| `.php files` | Python routes in `app/main.py` |
| Virtual hosts | Environment configurations |

### Quick Migration
1. Stop Apache service
2. Move website files to `static/` directory
3. Convert dynamic content to FastAPI routes
4. Start FastAPI server with `python start.py`

## 🚀 Production Deployment

### Recommended Setup
1. Use reverse proxy (Nginx) in front of FastAPI
2. Use certificates from trusted CA (not self-signed)
3. Set `FASTAPI_ENV=production`
4. Configure proper logging and monitoring

### Process Management
- **Windows**: Run as Windows Service
- **Linux**: Use systemd or supervisord

## 📞 Support

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SSL/TLS Help**: Use `python manage_ssl.py --help`
- **Testing**: Use `test_simple.py` for reliable testing

## ✅ Verification

To verify everything is working:
1. Start server: `python start.py`
2. Run tests: `python test_simple.py`
3. Check documentation: Open http://localhost:8000/docs

The server is fully functional and ready for development and production use!