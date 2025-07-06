# 🚀 Langflow + AstraDB Integration Guide

## Quick Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run Setup**
   ```bash
   python setup.py
   ```

4. **Start Services**
   ```bash
   ./start_services.sh
   ```

## Integration with Existing WooCommerce Proxy

### 1. Add Intelligent Search Endpoint

Add to your `index.js`:

```javascript
// Add intelligent search route
app.post('/api/intelligent-search', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8001/api/intelligent-search', req.body);
    res.json(response.data);
  } catch (error) {
    console.error('Intelligent search error:', error);
    res.status(500).json({ error: 'Intelligent search failed' });
  }
});
```

### 2. Update Frontend

Replace search logic in your chatbot:

```javascript
// Use intelligent search instead of basic search
const searchProducts = async (query, sessionId) => {
  const response = await fetch('/api/intelligent-search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      query, 
      session_id: sessionId,
      limit: 10 
    })
  });
  
  const data = await response.json();
  return {
    products: data.products,
    response: data.conversation_response,
    suggestions: data.suggestions
  };
};
```

## API Endpoints

- `POST /api/intelligent-search` - AI-powered product search
- `GET /api/product-recommendations/{id}` - Product recommendations  
- `GET /api/trending` - Trending products
- `GET /health` - Health check

## Langflow Flow Import

1. Open Langflow UI: http://localhost:7860
2. Import `recommendation_flow.json`
3. Configure OpenAI API key in flow settings
4. Deploy the flow

## Testing

```bash
# Test health
curl http://localhost:8001/health

# Test search
curl -X POST http://localhost:8001/api/intelligent-search \
  -H "Content-Type: application/json" \
  -d '{"query": "wheelchair accessible products", "limit": 5}'
```

## Architecture

```
Frontend Chatbot → WooCommerce Proxy → Intelligent Service → AstraDB
                                    ↘ Langflow → OpenAI
```

The system provides:
- ✅ Semantic product search
- ✅ Conversational AI responses  
- ✅ User context tracking
- ✅ Personalized recommendations
- ✅ Trending product insights
