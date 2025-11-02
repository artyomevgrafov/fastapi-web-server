# Text constants for FastAPI Web Server
# Текстовые константы для FastAPI веб-сервера

# Server messages / Сообщения сервера
SERVER_TITLE = "FastAPI Web Server - Apache Replacement"
SERVER_DESCRIPTION = "Full-featured web server replacing Apache with static file serving and proxy capabilities"
SERVER_VERSION = "2.0.0"

# Configuration messages / Сообщения конфигурации
CONFIG_LOAD_ERROR = "Configuration error: {}"
SSL_CERT_ERROR = "SSL certificate error: {}"
SSL_CERT_NOT_FOUND = "SSL certificate file not found: {}"
SSL_KEY_NOT_FOUND = "SSL key file not found: {}"
SSL_CERT_EMPTY = "SSL certificate file is empty"
SSL_KEY_EMPTY = "SSL key file is empty"
SSL_CERTS_FOUND = "SSL certificates found (cert: {} bytes, key: {} bytes)"

# Server startup messages / Сообщения запуска сервера
STARTING_SERVER = "Starting FastAPI Server on Production Port 443..."
ADMIN_PRIVILEGES_REQUIRED = "Administrator privileges required for port 443"
PORT_IN_USE = "Port 443 is already in use"
SSL_CHECK_FAILED = "SSL certificate check failed"
STARTING_PRODUCTION = "Starting production server on {}:{}..."
APACHE_STOP_WARNING = "Make sure Apache is stopped before continuing"
SERVER_STOPPED = "Server stopped by user"
SERVER_ERROR = "Server error: {}"

# Proxy messages / Сообщения проксирования
PROXY_ERROR = "Proxy error: {}"
BACKEND_UNAVAILABLE = "Backend server is not available"
BACKEND_TIMEOUT = "Backend server timeout"

# Feature descriptions / Описания функций
FEATURE_WEB_SERVER = "Full web server functionality"
FEATURE_SSL = "SSL/TLS encryption on port 443"
FEATURE_STATIC = "Static file serving"
FEATURE_API = "API endpoints"
FEATURE_DOCS = "Automatic documentation"
FEATURE_APACHE_REPLACE = "Ready to replace Apache"

# Status messages / Сообщения статуса
STATUS_HEALTHY = "healthy"
STATUS_RUNNING = "running"
STATUS_ACTIVE = "active"
STATUS_ENABLED = "Enabled"
STATUS_DISABLED = "Disabled"

# Error messages / Сообщения ошибок
IMPORT_ERROR = "Error importing application: {}"
FILE_NOT_FOUND = "Static file not found, proxying to backend: {}"

# Log messages / Сообщения логирования
LOG_PROXYING_API = "Proxying API {} {} to {}/api/{}"
LOG_PROXYING_QUERY = "Proxying Query {} {} to {}/query/{}"
LOG_STATIC_MOUNTED = "Static files mounted from: {}"

# API responses / Ответы API
API_HEALTH_RESPONSE = {
    "status": "healthy",
    "server": "FastAPI Web Server",
    "features": {
        "static_serving": "Static file serving capability",
        "proxy_enabled": "Reverse proxy functionality",
        "document_root": "DocumentRoot path",
        "backend_target": "Backend server URL",
    },
}

API_SERVER_INFO = {
    "message": "FastAPI Web Server - Full Apache Replacement",
    "status": "running",
    "features": [
        "Static file serving (DocumentRoot)",
        "Reverse proxy capabilities",
        "SSL/TLS encryption",
        "API routing",
        "Health monitoring",
        "Automatic documentation",
    ],
    "config": {
        "static_root": "Static files root directory",
        "backend_server": "Backend server URL",
        "ssl_enabled": "SSL/TLS status",
    },
    "endpoints": {
        "static_files": "/* (served from DocumentRoot)",
        "api_routes": "/api/* (proxied to backend)",
        "query_routes": "/query/* (proxied to backend)",
        "health_check": "/health",
        "documentation": "/docs",
    },
}
