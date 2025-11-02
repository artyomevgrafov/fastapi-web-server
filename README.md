# FastAPI Security Proxy Server

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A security-focused FastAPI proxy server with SSL/TLS support, static file serving, and comprehensive threat protection. Currently optimized for Windows environments with Linux support in development.

## ⚠️ Current Status: Development Preview

**This is NOT a production-ready Apache replacement.** The project is currently a security-enhanced proxy server with the following capabilities:

### ✅ Currently Implemented
- **SSL/TLS Support** - Automatic certificate management with win-acme
- **Static File Serving** - Basic DocumentRoot-style file serving
- **Reverse Proxy** - HTTP/HTTPS proxying to backend applications
- **Security Features** - IP blocking, rate limiting, threat detection
- **Health Monitoring** - Basic health checks and security analytics

### ❌ Missing Production Features
- HTTP/2 and HTTP/3 support
- Advanced caching (ETag, Range requests)
- Brotli compression
- Production TLS features (HSTS, OCSP stapling)
- Load balancing and circuit breakers
- Container orchestration (Docker/K8s)
- Comprehensive CI/CD pipeline

## Quick Start

### Prerequisites
- Python 3.8+
- Windows OS (Linux support planned)
- Administrative privileges for port 443

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fastapi-security-proxy.git
cd fastapi-security-proxy
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the server**
```bash
# Development mode (port 8080)
python start_8080.py

# Production mode (port 443 - requires admin)
python start_443.py
```

## Architecture

```
Client → FastAPI Security Proxy → [Static Files | Backend Proxy]
```

## Security Features

### Threat Detection
- Real-time pattern matching for common attacks
- Automatic IP blocking for suspicious activity
- Configurable rate limiting with burst protection
- Comprehensive attack analytics

### Monitoring Endpoints
- `/health` - Server health status
- `/security/stats` - Security statistics
- `/monitoring/analysis` - Attack pattern analysis
- `/monitoring/high-threat-ips` - Blocked IP addresses

## Configuration

Basic configuration in `config.py`:
```python
SERVER_CONFIG = {
    "target_server": "http://127.0.0.1:8097",
    "static_root": "C:/server/httpd/data/htdocs",
    "ssl_enabled": True,
}
```

## Development Roadmap

### Phase 1: Production Readiness (Current)
- [ ] Docker containerization
- [ ] HTTP/2 support via hypercorn
- [ ] Advanced caching headers
- [ ] Security headers (HSTS, CSP)

### Phase 2: Performance Optimization
- [ ] Brotli compression
- [ ] ETag and Range request support
- [ ] Connection pooling
- [ ] Load balancing

### Phase 3: Enterprise Features
- [ ] Kubernetes deployment
- [ ] Prometheus metrics
- [ ] Advanced TLS features
- [ ] WebSocket proxy support

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The modern web framework
- [Uvicorn](https://www.uvicorn.org/) - ASGI server implementation
- [win-acme](https://www.win-acme.com/) - Windows ACME client

---

**Note**: This project is actively developed. Features and APIs may change between versions.