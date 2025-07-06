# 🚀 Deploy to Railway - Quick Setup

## ✅ **Why Railway Over Render?**
- **Better Python Support**: Handles complex dependencies better
- **Faster Builds**: More reliable build process
- **GitHub Integration**: Seamless auto-deploy
- **Free Tier**: $5 credit monthly (usually enough for development)

## 🚀 **Quick Deployment Steps**

### Step 1: Go to Railway
Visit: https://railway.app

### Step 2: Sign Up/Login
- Click "Login"
- Sign in with GitHub (recommended)

### Step 3: Deploy from GitHub
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose: `RyvrImmersive/woocommerce-ai-recommendations`
4. Click "Deploy Now"

### Step 4: Set Environment Variables
In Railway dashboard, go to Variables tab and add:

```
OPENAI_API_KEY=your_openai_api_key_here
ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token_here
ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint_here
ASTRA_DB_KEYSPACE=enablemart
WC_KEY=your_woocommerce_consumer_key
WC_SECRET=your_woocommerce_consumer_secret
WC_BASE_URL=your_woocommerce_store_url
```

### Step 5: Get Your Live URL
After deployment (~2-3 minutes), Railway will provide a URL like:
`https://your-app.railway.app`

## ✅ **Test Your Deployed API**

```bash
# Test health endpoint
curl https://your-app.railway.app/health

# Test intelligent search
curl -X POST https://your-app.railway.app/api/intelligent-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "wheelchair for elderly parent",
    "session_id": "test123",
    "limit": 5
  }'
```

## 🎯 **Advantages of Railway**
- ✅ Better Python ecosystem support
- ✅ More reliable builds (handles astrapy better)
- ✅ Automatic HTTPS
- ✅ Custom domains on free tier
- ✅ Better logging and monitoring
- ✅ Faster deployment times

---

## 🚀 **Ready to Deploy?**
1. Go to https://railway.app
2. Login with GitHub
3. Deploy from your repository
4. Set environment variables
5. Your API will be live in ~3 minutes!

**Railway handles Python dependencies much better than Render!**
