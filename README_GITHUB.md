# FastAPI Web Server - Apache Replacement 🚀

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://windows.com)

A high-performance, modern web server built with FastAPI that can completely replace Apache HTTP Server. Provides SSL/TLS support, static file serving, reverse proxy capabilities, and automatic documentation.

## ✨ Features

- **🚀 High Performance** - Built on async FastAPI framework
- **🔒 SSL/TLS Support** - Automatic certificate management with win-acme
- **📁 Static File Serving** - Full DocumentRoot replacement
- **🔄 Reverse Proxy** - Intelligent routing to backend applications
- **📚 Auto Documentation** - Interactive Swagger UI out of the box
- **⚡ Modern Stack** - Python 3.7+, FastAPI, Uvicorn
- **🔧 Easy Configuration** - Simple Python configs instead of complex Apache configs
- **📊 Health Monitoring** - Built-in health checks and monitoring

## 🏗️ Architecture

```
Client → FastAPI (Port 443) → [Static Files | Proxy to Backend]
```

Replaces traditional Apache setup:
```apache
# Before: Apache config
<VirtualHost *:443>
    DocumentRoot "C:/htdocs"
    ProxyPass / http://127.0.0.1:8097/
</VirtualHost>

# After: FastAPI handles everything!
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Windows OS (Linux support planned)
- Administrative privileges for port 443

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fastapi-web-server.git
cd fastapi-web-server
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup SSL certificates**
```bash
# Using win-acme for Let's Encrypt certificates
powershell -ExecutionPolicy Bypass -File "win-acme\sync-certs.ps1"
```

4. **Start the server**
```bash
# Development mode (port 8080)
python start_8080.py

# Production mode (port 443 - requires admin)
python start_443.py
```

## 📁 Project Structure

```
fastapi-web-server/
├── app/
│   ├── main.py              # Main FastAPI application
│   └── api.py               # Additional API endpoints
├── certs/                   # SSL certificates
├── data/htdocs/            # DocumentRoot for static files
├── static/                 # Additional static assets
├── templates/              # HTML templates
├── win-acme/              # SSL certificate management
│   ├── sync-certs.ps1     # Certificate synchronization
│   ├── renew-certs.ps1    # Automatic renewal
│   └── check-certs.ps1    # Certificate status
├── config.py              # Server configuration
├── start_443.py           # Production launcher
├── start_8080.py          # Development launcher
└── requirements.txt       # Python dependencies
```

## ⚙️ Configuration

### Basic Configuration (config.py)
```python
class ProductionConfig:
    HOST: str = "0.0.0.0"
    PORT: int = 443
    SSL_ENABLED: bool = True
    SSL_CERT_FILE: str = "certs/cert.pem"
    SSL_KEY_FILE: str = "certs/key.pem"
    STATIC_ROOT: Path = Path("data/htdocs")
    BACKEND_SERVER: str = "http://127.0.0.1:8097"
```

### Environment-based Configs
- `development` - Auto-reload, debug logging
- `production` - Optimized for performance
- `default` - Basic settings

## 🔧 Usage Examples

### 1. Static File Serving
```python
# Serves files from data/htdocs/ directory
# Access: https://yoursite.com/index.html
```

### 2. Reverse Proxy
```python
# Proxies API requests to backend
# Access: https://yoursite.com/api/users → http://127.0.0.1:8097/api/users
```

### 3. Custom Routes
```python
@app.get("/custom")
async def custom_route():
    return {"message": "Custom FastAPI endpoint"}
```

## 🔒 SSL Certificate Management

### Automatic Renewal
```bash
# Setup scheduled task for automatic renewal
powershell -ExecutionPolicy Bypass -File "win-acme\setup-certs.ps1"
```

### Manual Management
```bash
# Sync certificates
.\win-acme\sync-certs.ps1

# Check certificate status
.\win-acme\check-certs.ps1

# Force renewal
.\win-acme\renew-certs.ps1
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/docs` | GET | Interactive API documentation |
| `/health` | GET | Server health status |
| `/api/*` | ANY | Proxy to backend API |
| `/query/*` | ANY | Proxy to query interface |
| `/*` | GET | Static file serving |

## 🛠️ Development

### Running Tests
```bash
# Basic functionality tests
python test_simple.py

# HTTPS tests
python test_https_server.py

# Certificate tests
powershell -ExecutionPolicy Bypass -File "win-acme\check-certs.ps1"
```

### Adding Features
1. Extend `app/main.py` for new routes
2. Modify configuration in `config.py`
3. Add tests in `test_*.py` files

## 🌐 Production Deployment

### Windows Service
```batch
# Create Windows service
sc create "FastAPI-WebServer" binPath="C:\path\to\python.exe C:\path\to\start_443.py"
```

### Reverse Proxy (Optional)
```nginx
# Nginx configuration for additional features
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The modern web framework
- [Uvicorn](https://www.uvicorn.org/) - The lightning-fast ASGI server
- [win-acme](https://www.win-acme.com/) - Windows ACME client for Let's Encrypt
- Apache HTTP Server - Inspiration and compatibility target

## 📞 Support

- 📧 Email: your-email@example.com
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/fastapi-web-server/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/fastapi-web-server/issues)

## 🚀 Future Plans

- [ ] Linux support
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Load balancing
- [ ] Advanced caching
- [ ] Rate limiting
- [ ] WebSocket support
- [ ] GraphQL endpoint

---

**⭐ Star this repo if you find it useful!**