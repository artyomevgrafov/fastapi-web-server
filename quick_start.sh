#!/bin/bash

# FastAPI Security Proxy - Quick Start Script
# Production-ready deployment with all features

set -e

echo "🚀 FastAPI Security Proxy - Quick Start"
echo "========================================"

# Check if running as root (for Linux)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root - this is not recommended for production"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

check_command() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1: $(command -v $1)"
        return 0
    else
        echo "❌ $1: Not found"
        return 1
    fi
}

# Essential commands
check_command python3
check_command pip3
check_command docker
check_command docker-compose

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "📝 Python version: $PYTHON_VERSION"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python version compatible"
else
    echo "❌ Python 3.8+ required"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Setting up directories..."
mkdir -p logs certs data/htdocs static

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Generate self-signed SSL certificates if not present
echo ""
echo "🔐 Setting up SSL certificates..."
if [ ! -f "certs/cert.pem" ] || [ ! -f "certs/key.pem" ]; then
    echo "Generating self-signed certificates for development..."
    openssl req -x509 -newkey rsa:4096 \
        -keyout certs/key.pem \
        -out certs/cert.pem \
        -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "⚠️  OpenSSL not available - creating placeholder certificates"
    fi

    if [ ! -f "certs/key.pem" ]; then
        echo "PLACEHOLDER PRIVATE KEY - REPLACE IN PRODUCTION" > certs/key.pem
    fi
    if [ ! -f "certs/cert.pem" ]; then
        echo "PLACEHOLDER CERTIFICATE - REPLACE IN PRODUCTION" > certs/cert.pem
    fi
else
    echo "✅ SSL certificates already exist"
fi

# Create test static file
echo ""
echo "📄 Creating test files..."
mkdir -p data/htdocs
cat > data/htdocs/index.html << 'EOF'
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
    <h1>🚀 FastAPI Security Proxy</h1>
    <p>Server is running successfully!</p>
    <div class="status healthy">✅ Status: Healthy</div>
    <p><a href="/health">Health Check</a> | <a href="/docs">API Documentation</a></p>
</body>
</html>
EOF

echo "✅ Test files created"

# Setup environment variables
echo ""
echo "⚙️  Setting up environment..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Production Environment
HOST=0.0.0.0
PORT=8080
TARGET_SERVER=http://127.0.0.1:8097
SSL_ENABLED=true
SSL_CERT_FILE=./certs/cert.pem
SSL_KEY_FILE=./certs/key.pem

# Security
SECURITY_ENABLED=true
RATE_LIMITING_ENABLED=true
IP_BLOCKING_ENABLED=true

# Performance
WORKERS=4
GZIP_ENABLED=true
HTTP2_ENABLED=true

# Logging
LOG_LEVEL=INFO
ENABLE_DETAILED_LOGGING=true
EOF
    echo "✅ Environment file created"
else
    echo "✅ Environment file already exists"
fi

# Test the configuration
echo ""
echo "🧪 Testing configuration..."
python3 -c "
from app.config import server_config, security_config, features_config
print('✅ Configuration loaded successfully')
print(f'   Host: {server_config.host}')
print(f'   Port: {server_config.port}')
print(f'   SSL: {server_config.ssl_enabled}')
print(f'   Security: {features_config.security_enabled}')
"

# Choose startup method
echo ""
echo "🎯 Choose startup method:"
echo "1) Docker Compose (Recommended)"
echo "2) Hypercorn with HTTP/2"
echo "3) Uvicorn (Development)"
echo "4) Skip startup"
read -p "Enter choice [1-4]: " choice
choice=${choice:-4}

case $choice in
    1)
        echo ""
        echo "🐳 Starting with Docker Compose..."
        docker-compose up -d
        echo "✅ Docker containers started"
        echo "📊 Access the server at: http://localhost:8080"
        ;;
    2)
        echo ""
        echo "🚀 Starting with Hypercorn (HTTP/2)..."
        python3 start_hypercorn.py &
        HYPERCORN_PID=$!
        echo "✅ Hypercorn started (PID: $HYPERCORN_PID)"
        echo "📊 Access the server at: http://localhost:8080"
        echo "💡 Run 'kill $HYPERCORN_PID' to stop the server"
        ;;
    3)
        echo ""
        echo "🔧 Starting with Uvicorn..."
        python3 start_8080.py &
        UVICORN_PID=$!
        echo "✅ Uvicorn started (PID: $UVICORN_PID)"
        echo "📊 Access the server at: http://localhost:8080"
        echo "💡 Run 'kill $UVICORN_PID' to stop the server"
        ;;
    4)
        echo ""
        echo "⏹️  Skipping startup"
        ;;
    *)
        echo ""
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Health check
if [ "$choice" != "4" ]; then
    echo ""
    echo "🔍 Running health check..."
    sleep 5
    if command -v curl >/dev/null 2>&1 && curl -f http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Server is healthy and responding"
    else
        echo "⚠️  Server health check failed - check logs for details"
    fi
fi

# Final instructions
echo ""
echo "========================================"
echo "🎉 Setup Complete!"
echo ""
echo "📊 Available Endpoints:"
echo "   Main:      http://localhost:8080"
echo "   Health:    http://localhost:8080/health"
echo "   Docs:      http://localhost:8080/docs"
echo "   Security:  http://localhost:8080/security/stats"
echo "   Metrics:   http://localhost:8080/metrics"
echo ""
echo "🔧 Management Commands:"
echo "   Stop Docker:    docker-compose down"
echo "   View logs:      docker-compose logs -f"
echo "   Run tests:      python3 test_smoke.py"
echo "   Run benchmarks: python3 automated_benchmark.py"
echo ""
echo "📚 Next Steps:"
echo "   1. Configure your backend server in .env"
echo "   2. Replace SSL certificates for production"
echo "   3. Set up monitoring and logging"
echo "   4. Configure firewall and security settings"
echo ""
echo "💡 For production deployment, run: python3 deploy_production.py"
echo "========================================"
