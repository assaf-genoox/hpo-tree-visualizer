# 🚀 Railway Deployment Guide - HPO Tree Visualizer

## Quick Start (5 Minutes)

### Prerequisites ✅
- [x] GitHub repository created: `https://github.com/assaf-genoox/hpo-tree-visualizer`
- [x] All files committed and pushed
- [x] Railway configuration files added

---

## Step-by-Step Deployment

### 1. Sign Up for Railway
1. Go to [railway.app](https://railway.app)
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub account

### 2. Create New Project
1. Click **"New Project"** on Railway dashboard
2. Select **"Deploy from GitHub repo"**
3. Find and select **`assaf-genoox/hpo-tree-visualizer`**
4. Click **"Deploy Now"**

### 3. Wait for Deployment
Railway will automatically:
- ✅ Detect Python project (via `requirements.txt`)
- ✅ Install dependencies
- ✅ Start your application using `Procfile`
- ✅ Assign a public URL

### 4. Access Your App
- Railway will provide a URL like: `https://hpo-tree-visualizer-production-xxxx.up.railway.app`
- Click the URL to access your live HPO Tree Visualizer!

---

## 🔧 Configuration Details

### What Railway Detects Automatically:
- **Language**: Python (from `requirements.txt`)
- **Start Command**: From `Procfile`
- **Port**: Uses `$PORT` environment variable
- **Dependencies**: Installs from `requirements.txt`

### Files Used by Railway:
- `requirements.txt` - Python dependencies
- `Procfile` - Start command
- `railway.toml` - Railway-specific configuration
- `start_railway.py` - Optimized startup script
- `hpo_backend.py` - Main FastAPI application
- `hpo_frontend.html` - Frontend interface
- `hp.json` - HPO data (large file, ~21MB)

---

## 🌐 Custom Domain Setup

### Option 1: Railway Subdomain (Free)
- Railway provides a free subdomain
- Format: `your-app-name-production-xxxx.up.railway.app`
- No additional configuration needed

### Option 2: Custom Domain
1. Go to your project in Railway dashboard
2. Click **"Settings"** tab
3. Scroll to **"Domains"** section
4. Add your custom domain (e.g., `hpo-visualizer.yourdomain.com`)
5. Configure DNS as instructed by Railway

---

## 📊 Monitoring & Management

### View Logs
1. Go to your project dashboard
2. Click **"Deployments"** tab
3. Click on the latest deployment
4. View real-time logs

### Monitor Resources
1. Go to **"Metrics"** tab
2. View CPU, memory, and network usage
3. Monitor response times

### Environment Variables
1. Go to **"Variables"** tab
2. Add custom environment variables:
   ```
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://your-domain.com
   ```

---

## 🔄 Updates & Redeployment

### Automatic Redeployment
- Railway automatically redeploys when you push to GitHub
- No manual intervention needed

### Manual Redeployment
1. Go to your project dashboard
2. Click **"Deployments"** tab
3. Click **"Redeploy"** button

### Rollback
1. Go to **"Deployments"** tab
2. Find the working deployment
3. Click **"Rollback"** button

---

## 💰 Pricing & Limits

### Free Tier
- ✅ $5 credit per month
- ✅ 500 hours of usage
- ✅ 1GB RAM
- ✅ 1GB storage
- ✅ Custom domains
- ✅ HTTPS included

### Paid Plans
- **Hobby**: $5/month
- **Pro**: $20/month
- **Team**: $99/month

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Build Fails
**Problem**: Railway can't build your app
**Solution**: 
- Check `requirements.txt` syntax
- Ensure all dependencies are listed
- Check logs for specific error messages

#### 2. App Won't Start
**Problem**: App starts but crashes immediately
**Solution**:
- Check `Procfile` syntax
- Verify `hpo_backend.py` is correct
- Check if `hp.json` is present

#### 3. Memory Issues
**Problem**: App runs out of memory
**Solution**:
- Railway free tier has 1GB RAM limit
- Consider upgrading to paid plan
- Optimize data loading

#### 4. Slow Performance
**Problem**: App is slow to respond
**Solution**:
- Check Railway metrics
- Consider upgrading resources
- Optimize your code

### Debug Commands

#### Check Logs
```bash
# View recent logs
railway logs

# Follow logs in real-time
railway logs --follow
```

#### Connect to Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Connect to your project
railway link
```

---

## 🚀 Advanced Configuration

### Environment-Specific Settings

#### Development
```toml
[environments.development]
variables = { 
  ENVIRONMENT = "development",
  DEBUG = "true",
  ALLOWED_ORIGINS = "*"
}
```

#### Production
```toml
[environments.production]
variables = { 
  ENVIRONMENT = "production",
  DEBUG = "false",
  ALLOWED_ORIGINS = "https://your-domain.com"
}
```

### Health Checks
Railway automatically checks:
- **Path**: `/health` (defined in `railway.toml`)
- **Timeout**: 100 seconds
- **Retries**: 10 attempts

### Scaling
- **Horizontal**: Add more instances
- **Vertical**: Upgrade to higher tier
- **Auto-scaling**: Available in Pro+ plans

---

## 📈 Performance Optimization

### For Railway Deployment

1. **Optimize Startup Time**:
   - Use `start_railway.py` for faster startup
   - Minimize imports
   - Lazy load heavy modules

2. **Memory Management**:
   - Monitor memory usage
   - Use efficient data structures
   - Implement caching

3. **Response Time**:
   - Use async/await properly
   - Implement response caching
   - Optimize database queries

---

## 🔒 Security Considerations

### Production Security
1. **CORS Configuration**:
   ```python
   # In hpo_backend.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],  # Specific domains
       allow_credentials=True,
       allow_methods=["GET"],
       allow_headers=["*"],
   )
   ```

2. **Environment Variables**:
   - Never commit secrets to Git
   - Use Railway's environment variables
   - Rotate keys regularly

3. **HTTPS**:
   - Railway provides free HTTPS
   - Always use HTTPS in production

---

## 📞 Support & Resources

### Railway Support
- **Documentation**: [docs.railway.app](https://docs.railway.app)
- **Discord**: [Railway Discord](https://discord.gg/railway)
- **GitHub**: [Railway GitHub](https://github.com/railwayapp)

### HPO Visualizer Support
- **Issues**: Create GitHub issue
- **Documentation**: See `README.md`
- **Architecture**: See `HPO_ARCHITECTURE_DOCUMENTATION.md`

---

## ✅ Deployment Checklist

Before deploying:
- [ ] All files committed to GitHub
- [ ] `requirements.txt` is correct
- [ ] `Procfile` is properly formatted
- [ ] `hp.json` is included (large file)
- [ ] Environment variables configured
- [ ] CORS settings appropriate
- [ ] Health check endpoint working

After deploying:
- [ ] App loads successfully
- [ ] Search functionality works
- [ ] Visualization renders correctly
- [ ] API endpoints respond
- [ ] Performance is acceptable
- [ ] HTTPS is working
- [ ] Custom domain (if used) is configured

---

## 🎉 Success!

Your HPO Tree Visualizer is now live and accessible to anyone on the internet!

**Next Steps:**
1. Share the URL with colleagues
2. Monitor usage and performance
3. Consider adding analytics
4. Plan for scaling if needed
5. Set up monitoring and alerts

**Congratulations! 🚀**
