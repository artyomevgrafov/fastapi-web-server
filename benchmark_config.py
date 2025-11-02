"""
Benchmark Configuration with Realistic Test Data
Configuration for comprehensive performance testing
"""

from typing import Dict, List, Any
from pathlib import Path
import json

# Test file configurations
TEST_FILES = {
    "small_html": {
        "path": "index.html",
        "content": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>Performance Test Page</h1>
    </header>
    <main>
        <section id="content">
            <p>This is a test page for benchmarking web server performance.</p>
            <div class="test-data">
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ul>
            </div>
        </section>
    </main>
    <script src="app.js"></script>
</body>
</html>""",
        "size_kb": 2.1,
    },
    "medium_css": {
        "path": "style.css",
        "content": """/* Test CSS file for benchmarking */
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --text-color: #2c3e50;
    --background-color: #ecf0f1;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
    padding: 20px;
}

header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 2rem;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.test-data {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid var(--primary-color);
}

.test-data ul {
    list-style: none;
    padding: 0;
}

.test-data li {
    padding: 0.5rem 1rem;
    margin: 0.5rem 0;
    background: white;
    border-radius: 5px;
    border: 1px solid #e9ecef;
    transition: all 0.3s ease;
}

.test-data li:hover {
    background: var(--primary-color);
    color: white;
    transform: translateX(5px);
}

/* Responsive design */
@media (max-width: 768px) {
    body {
        padding: 10px;
    }

    header {
        padding: 1rem;
    }

    h1 {
        font-size: 2rem;
    }

    main {
        padding: 1rem;
    }
}

/* Animations */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

main {
    animation: fadeIn 0.5s ease-out;
}

/* Additional utility classes */
.text-center { text-align: center; }
.mt-1 { margin-top: 1rem; }
.mb-1 { margin-bottom: 1rem; }
.p-1 { padding: 1rem; }
.border { border: 1px solid #dee2e6; }
.rounded { border-radius: 0.375rem; }
.shadow { box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); }""",
        "size_kb": 4.8,
    },
    "large_js": {
        "path": "app.js",
        "content": """/**
 * Test JavaScript file for benchmarking
 * Contains realistic application logic
 */

// Configuration
const CONFIG = {
    apiEndpoints: {
        users: '/api/users',
        products: '/api/products',
        orders: '/api/orders'
    },
    cacheTimeout: 300000, // 5 minutes
    maxRetries: 3,
    timeout: 10000
};

// Utility functions
class Utils {
    static formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// API Client
class ApiClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.cache = new Map();
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const cacheKey = `${endpoint}-${JSON.stringify(options)}`;

        // Check cache
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < CONFIG.cacheTimeout) {
                return cached.data;
            }
        }

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Cache successful response
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async getUsers() {
        return this.request(CONFIG.apiEndpoints.users);
    }

    async getProducts() {
        return this.request(CONFIG.apiEndpoints.products);
    }

    async getOrders() {
        return this.request(CONFIG.apiEndpoints.orders);
    }
}

// UI Components
class TestComponent {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.apiClient = new ApiClient();
        this.initialize();
    }

    initialize() {
        this.render();
        this.bindEvents();
        this.loadData();
    }

    render() {
        this.container.innerHTML = `
            <div class="component-header">
                <h2>Test Component</h2>
                <button id="refresh-btn" class="btn btn-primary">Refresh Data</button>
            </div>
            <div class="component-content">
                <div id="loading" class="loading">Loading...</div>
                <div id="data-container" class="data-container" style="display: none;"></div>
                <div id="error-container" class="error-container" style="display: none;"></div>
            </div>
        `;
    }

    bindEvents() {
        const refreshBtn = document.getElementById('refresh-btn');
        refreshBtn.addEventListener('click',
            Utils.debounce(() => this.loadData(), 300)
        );
    }

    async loadData() {
        this.showLoading();

        try {
            const [users, products] = await Promise.all([
                this.apiClient.getUsers(),
                this.apiClient.getProducts()
            ]);

            this.displayData({ users, products });
        } catch (error) {
            this.showError(error.message);
        }
    }

    displayData(data) {
        const container = document.getElementById('data-container');
        container.innerHTML = `
            <div class="data-section">
                <h3>Users (${data.users?.length || 0})</h3>
                <div class="user-list">
                    ${this.renderUserList(data.users)}
                </div>
            </div>
            <div class="data-section">
                <h3>Products (${data.products?.length || 0})</h3>
                <div class="product-grid">
                    ${this.renderProductGrid(data.products)}
                </div>
            </div>
        `;

        this.hideLoading();
        container.style.display = 'block';
    }

    renderUserList(users = []) {
        return users.map(user => `
            <div class="user-card">
                <div class="user-avatar">${user.name?.charAt(0) || 'U'}</div>
                <div class="user-info">
                    <div class="user-name">${user.name || 'Unknown User'}</div>
                    <div class="user-email">${user.email || 'No email'}</div>
                </div>
            </div>
        `).join('');
    }

    renderProductGrid(products = []) {
        return products.map(product => `
            <div class="product-card">
                <div class="product-image">📦</div>
                <div class="product-details">
                    <div class="product-name">${product.name || 'Unknown Product'}</div>
                    <div class="product-price">$${product.price || '0.00'}</div>
                </div>
            </div>
        `).join('');
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('data-container').style.display = 'none';
        document.getElementById('error-container').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showError(message) {
        const errorContainer = document.getElementById('error-container');
        errorContainer.innerHTML = `
            <div class="alert alert-error">
                <strong>Error:</strong> ${message}
            </div>
        `;
        errorContainer.style.display = 'block';
        document.getElementById('loading').style.display = 'none';
        document.getElementById('data-container').style.display = 'none';
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Test application initialized');

    // Initialize components
    if (document.getElementById('test-component')) {
        new TestComponent('test-component');
    }

    // Add some interactive features
    const testItems = document.querySelectorAll('.test-data li');
    testItems.forEach(item => {
        item.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    });

    // Performance monitoring
    const perfObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
            console.log(`${entry.name}: ${entry.duration}ms`);
        });
    });

    perfObserver.observe({ entryTypes: ['measure', 'navigation'] });
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiClient, TestComponent, Utils };
}""",
        "size_kb": 12.3,
    },
    "image_png": {
        "path": "logo.png",
        "content": "fake_binary_data_for_testing",
        "size_kb": 45.2,
    },
}

# API test data
API_TEST_DATA = {
    "users": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "user",
            "created_at": "2024-01-15T10:30:00Z",
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "role": "admin",
            "created_at": "2024-01-14T15:45:00Z",
        },
        {
            "id": 3,
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "role": "user",
            "created_at": "2024-01-13T09:15:00Z",
        },
    ],
    "products": [
        {
            "id": 1,
            "name": "Laptop Computer",
            "price": 999.99,
            "category": "electronics",
            "in_stock": True,
            "rating": 4.5,
        },
        {
            "id": 2,
            "name": "Wireless Mouse",
            "price": 29.99,
            "category": "electronics",
            "in_stock": True,
            "rating": 4.2,
        },
        {
            "id": 3,
            "name": "Office Chair",
            "price": 199.99,
            "category": "furniture",
            "in_stock": False,
            "rating": 4.7,
        },
    ],
    "orders": [
        {
            "id": 1001,
            "user_id": 1,
            "total": 1029.98,
            "status": "completed",
            "created_at": "2024-01-15T08:20:00Z",
        },
        {
            "id": 1002,
            "user_id": 2,
            "total": 29.99,
            "status": "pending",
            "created_at": "2024-01-15T11:45:00Z",
        },
    ],
}

# Benchmark scenarios
BENCHMARK_SCENARIOS = {
    "static_files": {
        "name": "Static File Serving",
        "description": "Test serving various static files (HTML, CSS, JS, images)",
        "concurrent_requests": 100,
        "duration": 30,
        "target_rps": 4000,
        "target_latency_ms": 5,
    },
    "api_proxy": {
        "name": "API Proxy",
        "description": "Test reverse proxy functionality to backend API",
        "concurrent_requests": 50,
        "duration": 30,
        "target_rps": 3500,
        "target_latency_ms": 8,
    },
    "concurrent_load": {
        "name": "Concurrent Load",
        "description": "Test server under high concurrent connections",
        "max_concurrent": 1000,
        "duration": 60,
        "target_rps": 3000,
        "target_latency_ms": 25,
    },
    "mixed_traffic": {
        "name": "Mixed Traffic",
        "description": "Test with mixed static and API requests",
        "concurrent_requests": 200,
        "duration": 45,
        "target_rps": 2800,
        "target_latency_ms": 15,
    },
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "excellent": {
        "static_rps": 4500,
        "api_rps": 3800,
        "concurrent_rps": 3200,
        "avg_latency_ms": 3,
        "memory_mb": 50,
    },
    "good": {
        "static_rps": 3500,
        "api_rps": 2800,
        "concurrent_rps": 2500,
        "avg_latency_ms": 8,
        "memory_mb": 80,
    },
    "acceptable": {
        "static_rps": 2500,
        "api_rps": 2000,
        "concurrent_rps": 1800,
        "avg_latency_ms": 15,
        "memory_mb": 120,
    },
    "poor": {
        "static_rps": 1500,
        "api_rps": 1200,
        "concurrent_rps": 1000,
        "avg_latency_ms": 25,
        "memory_mb": 200,
    },
}


def create_test_files(base_path: Path):
    """Create test files for benchmarking"""
    base_path.mkdir(parents=True, exist_ok=True)

    for file_config in TEST_FILES.values():
        file_path = base_path / file_config["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_config["content"])

    print(f"✅ Created test files in {base_path}")


def get_api_response(endpoint: str) -> Dict[str, Any]:
    """Get mock API response for testing"""
    if endpoint == "/api/users":
        return {"users": API_TEST_DATA["users"], "total": len(API_TEST_DATA["users"])}
    elif endpoint == "/api/products":
        return {
            "products": API_TEST_DATA["products"],
            "total": len(API_TEST_DATA["products"]),
        }
    elif endpoint == "/api/orders":
        return {
            "orders": API_TEST_DATA["orders"],
            "total": len(API_TEST_DATA["orders"]),
        }
    elif endpoint == "/api/health":
        return {"status": "healthy", "timestamp": "2024-01-15T10:30:00Z"}
    else:
        return {"error": "Endpoint not found", "status": 404}


if __name__ == "__main__":
    # Create test files when run directly
    test_dir = Path("test_files")
    create_test_files(test_dir)

    # Save API test data
    with open(test_dir / "api_data.json", "w") as f:
        json.dump(API_TEST_DATA, f, indent=2)

    print("✅ Benchmark configuration ready")
