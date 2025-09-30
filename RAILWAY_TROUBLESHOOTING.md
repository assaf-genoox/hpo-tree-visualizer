# 🚨 Railway Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Health Check Failures ❌

**Problem**: Railway health checks are failing during deployment.

**Symptoms**:
- Build succeeds but deployment fails
- "Health check failed" error in Railway logs
- App starts but Railway marks it as unhealthy

**Solutions**:

#### ✅ **Fixed in Latest Update**:
- Increased health check timeout to 300 seconds
- Added proper health check response handling
- Added loading state detection
- Improved error handling

#### **Manual Fix**:
1. **Check Railway logs**:
   ```bash
   # In Railway dashboard, go to your project
   # Click "Deployments" → Latest deployment → "View Logs"
   ```

2. **Verify health endpoint**:
   - Visit: `https://your-app.railway.app/health`
   - Should return: `{"status": "healthy", "nodes_loaded": 19778, ...}`

3. **Check data loading**:
   - The app needs time to load the 21MB HPO data file
   - Health check now waits for data to load

### 2. Build Failures 🔨

**Problem**: Railway build process fails.

**Common Causes**:
- Missing dependencies
- Python version issues
- File size limits

**Solutions**:

#### **Check requirements.txt**:
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
```

#### **Verify file structure**:
```
hpo-tree-visualizer/
├── hpo_backend.py          # Main backend
├── hpo_frontend.html       # Frontend
├── hp.json                 # HPO data (21MB)
├── requirements.txt        # Dependencies
├── Procfile               # Start command
├── railway.toml           # Railway config
└── start_railway.py       # Startup script
```

### 3. Memory Issues 💾

**Problem**: App runs out of memory during startup.

**Symptoms**:
- App crashes after starting
- "Out of memory" errors
- Slow performance

**Solutions**:

#### **Railway Free Tier Limits**:
- **RAM**: 1GB
- **Storage**: 1GB
- **CPU**: Shared

#### **Optimizations Applied**:
- Single worker process
- Efficient data loading
- Optimized startup script

#### **If Still Having Issues**:
1. **Upgrade to Railway Pro** ($20/month)
2. **Optimize data loading** (lazy loading)
3. **Use smaller dataset** for testing

### 4. Port Issues 🔌

**Problem**: App can't bind to the correct port.

**Symptoms**:
- "Address already in use" errors
- App starts but not accessible

**Solutions**:

#### **Railway Environment Variables**:
- Railway sets `$PORT` automatically
- App uses: `os.getenv("PORT", "8000")`

#### **Check startup script**:
```python
# start_railway.py
port = os.getenv("PORT", "8000")
host = "0.0.0.0"
```

### 5. CORS Issues 🌐

**Problem**: Frontend can't connect to backend API.

**Symptoms**:
- "CORS error" in browser console
- API calls fail
- Network errors

**Solutions**:

#### **CORS Configuration**:
```python
# hpo_backend.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### **API URL Configuration**:
```javascript
// hpo_frontend.html
const API_BASE_URL = '/api';  // Relative URL for same domain
```

### 6. Data Loading Issues 📊

**Problem**: HPO data doesn't load properly.

**Symptoms**:
- Empty visualization
- "No data" errors
- Slow loading

**Solutions**:

#### **Check hp.json**:
- File must be in root directory
- Size should be ~21MB
- Must be valid JSON

#### **Data Loading Process**:
1. App starts
2. Loads hp.json (takes 10-30 seconds)
3. Processes 19,778 nodes
4. Builds relationships
5. Health check passes

### 7. Static File Issues 📁

**Problem**: Frontend files not served correctly.

**Symptoms**:
- 404 errors for HTML/CSS/JS
- Blank page
- Missing resources

**Solutions**:

#### **Static File Serving**:
```python
# hpo_backend.py
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def root():
    return FileResponse("hpo_frontend.html")
```

## 🔍 Debugging Steps

### 1. Check Railway Logs
```bash
# In Railway dashboard:
# 1. Go to your project
# 2. Click "Deployments"
# 3. Click latest deployment
# 4. Click "View Logs"
```

### 2. Test Health Endpoint
```bash
# Test locally first:
curl http://localhost:8000/health

# Test on Railway:
curl https://your-app.railway.app/health
```

### 3. Check API Endpoints
```bash
# Test stats endpoint:
curl https://your-app.railway.app/api/stats

# Test search endpoint:
curl "https://your-app.railway.app/api/search?q=kidney"
```

### 4. Verify File Structure
```bash
# Check if all files are present:
ls -la
# Should include: hpo_backend.py, hpo_frontend.html, hp.json, etc.
```

## 🚀 Deployment Checklist

Before deploying:
- [ ] All files committed to GitHub
- [ ] `requirements.txt` is correct
- [ ] `Procfile` is properly formatted
- [ ] `hp.json` is included (21MB)
- [ ] Health check endpoint works
- [ ] API endpoints respond
- [ ] Frontend loads correctly

After deploying:
- [ ] Railway build succeeds
- [ ] Health check passes
- [ ] App is accessible via URL
- [ ] Frontend loads
- [ ] Search works
- [ ] Visualization renders

## 📞 Getting Help

### Railway Support
- **Documentation**: [docs.railway.app](https://docs.railway.app)
- **Discord**: [Railway Discord](https://discord.gg/railway)
- **GitHub**: [Railway GitHub](https://github.com/railwayapp)

### Common Error Messages

#### "Health check failed"
- **Cause**: App not responding to `/health` endpoint
- **Fix**: Check health endpoint implementation

#### "Build failed"
- **Cause**: Missing dependencies or syntax errors
- **Fix**: Check `requirements.txt` and code syntax

#### "Out of memory"
- **Cause**: App exceeds 1GB RAM limit
- **Fix**: Optimize code or upgrade plan

#### "Port already in use"
- **Cause**: Multiple processes trying to use same port
- **Fix**: Use `$PORT` environment variable

## 🎯 Quick Fixes

### If Health Check Fails:
1. Check Railway logs
2. Verify `/health` endpoint
3. Wait for data loading (up to 5 minutes)
4. Check memory usage

### If Build Fails:
1. Check `requirements.txt`
2. Verify Python version
3. Check file syntax
4. Review Railway logs

### If App Won't Start:
1. Check `Procfile`
2. Verify startup script
3. Check port configuration
4. Review error logs

### If Frontend Won't Load:
1. Check static file serving
2. Verify CORS configuration
3. Check API URL configuration
4. Test endpoints manually

## ✅ Success Indicators

Your deployment is successful when:
- ✅ Railway build completes without errors
- ✅ Health check returns `{"status": "healthy"}`
- ✅ App URL is accessible
- ✅ Frontend loads completely
- ✅ Search functionality works
- ✅ Visualization renders correctly
- ✅ API endpoints respond properly

## 🔄 Redeployment

If you need to redeploy:
1. **Automatic**: Push changes to GitHub
2. **Manual**: Railway dashboard → "Redeploy"
3. **Rollback**: Railway dashboard → "Rollback"

The latest fixes should resolve the health check issues. If you're still having problems, check the Railway logs for specific error messages.
