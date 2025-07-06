# 🌐 Alternative: Deploy via Railway Web Interface

## 🚀 Option A: GitHub Integration (Recommended)

### Step 1: Push to GitHub
```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/yourusername/intelligent-recommendations-api.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy via Railway Web
1. Go to [railway.app](https://railway.app)
2. Sign up/login
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway will auto-detect it's a Python app and deploy

### Step 3: Set Environment Variables
In Railway dashboard → Variables tab, add:
```
OPENAI_API_KEY=your_key
ASTRA_DB_APPLICATION_TOKEN=your_token
ASTRA_DB_API_ENDPOINT=your_endpoint
ASTRA_DB_KEYSPACE=enablemart
WC_KEY=your_wc_key
WC_SECRET=your_wc_secret
WC_BASE_URL=your_wc_url
```

## 🚀 Option B: Direct Upload

### Step 1: Create ZIP file
```bash
zip -r intelligent-api.zip . -x "*.git*" "*.env*" "__pycache__*"
```

### Step 2: Deploy via Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from local directory"
4. Upload your ZIP file
5. Set environment variables as above

## ✅ After Deployment

Your API will be available at a URL like:
`https://intelligent-recommendations-api-production.up.railway.app`

**Test it:**
```bash
curl https://your-url.railway.app/health
```

**Update your frontend:**
```javascript
const API_BASE_URL = 'https://your-url.railway.app';
```

---

## 🎯 Which method do you prefer?
1. **Command Line** (follow DEPLOY_STEPS.md)
2. **GitHub Integration** (push to GitHub first)
3. **Direct Upload** (create ZIP and upload)

All methods will give you the same result - a live API accessible from anywhere!
