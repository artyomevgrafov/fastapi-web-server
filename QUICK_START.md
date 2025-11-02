# FastAPI Quick Start Guide

## 🚀 Fast Start (5 Minutes)

### 1. Install Dependencies
```bash
cd httpd\fastapi
pip install -r requirements.txt
```

### 2. Start Server
**Option A: Simple Start**
```bash
python start_server.py
```

**Option B: Automatic Migration (Windows)**
- Right-click `migrate.bat` → "Run as administrator"

### 3. Access Your Server
- **Web Interface**: http://localhost
- **API Documentation**: http://localhost/docs
- **Health Check**: http://localhost/api/health
- **Static Files**: http://localhost/static/

## 📋 What You Get

### ✅ Ready-to-Use Features
- **Web Server** - Serves HTML pages and static files
- **REST API** - Complete CRUD operations with users
- **Auto Documentation** - Interactive Swagger UI
- **Health Monitoring** - Built-in health checks
- **Static File Serving** - CSS, JS, images from `/static/`

### 🔧 API Endpoints Included
```
GET  /                 # Main web page
GET  /docs             # Interactive API docs
GET  /api/health       # Health status
GET  /api/users        # List all users
POST /api/users        # Create new user
GET  /api/users/{id}   # Get user by ID
PUT  /api/users/{id}   # Update user
DELETE /api/users/{id} # Delete user
GET  /api/echo/{msg}   # Echo messages
GET  /api/math/*       # Math operations
```

## 🛠️ Customization

### Add New Routes
Edit `app/main.py`:
```python
@app.get("/hello")
async def hello(name: str = "World"):
    return {"message": f"Hello, {name}!"}
```

### Serve Static Files
Place files in `static/` directory:
- CSS files → `/static/css/style.css`
- Images → `/static/images/logo.png`
- JavaScript → `/static/js/app.js`

### Change Port
Edit `config.py`:
```python
PORT: int = 8080  # Change from 80 to 8080
```

## 🧪 Testing

### Run Complete Test Suite
```bash
python test_server.py
```

### Quick Health Check
```bash
curl http://localhost/api/health
```

## ⚡ Performance Tips

1. **For Production**: Set `FASTAPI_ENV=production`
2. **Static Files**: Use CDN for high-traffic sites
3. **Database**: Add async database drivers
4. **Caching**: Implement Redis or similar

## 🔄 Migration from Apache

### File Locations
| Apache | FastAPI |
|--------|---------|
| `htdocs/` | `static/` |
| `.php` files | Python routes in `app/main.py` |
| Virtual hosts | Multiple FastAPI apps |

### Quick Migration Steps
1. Stop Apache service
2. Move website files to `static/` directory  
3. Convert PHP scripts to Python routes
4. Start FastAPI server

## 🆘 Troubleshooting

### Common Issues
- **Port 80 in use**: Stop Apache first or change port in `config.py`
- **Import errors**: Run `pip install -r requirements.txt`
- **Permission denied**: Run as Administrator (Windows) or use `sudo` (Linux)

### Debug Mode
Set environment variable:
```bash
set FASTAPI_ENV=development
```

## 📚 Next Steps

1. ✅ **Test basic functionality** - Run `test_server.py`
2. 🔧 **Customize routes** - Modify `app/main.py`
3. 📁 **Add your content** - Place files in `static/`
4. 🚀 **Deploy to production** - Use reverse proxy (Nginx)
5. 📊 **Add monitoring** - Implement logging and metrics

## 🆓 Support
- **Documentation**: https://fastapi.tiangolo.com
- **Community**: GitHub Discussions, Stack Overflow
- **Examples**: See `MIGRATION_GUIDE.md` for detailed scenarios

---

**🎉 You're ready to go! The server is running and fully functional.**