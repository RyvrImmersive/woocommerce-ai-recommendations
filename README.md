# 🤖 Intelligent WooCommerce Product Recommendations
## Powered by Langflow + AstraDB

### 🎯 **Overview**
This system enhances the existing WooCommerce product search with AI-powered semantic recommendations using:
- **Langflow**: Conversational AI flows and recommendation logic
- **AstraDB**: Vector storage for product embeddings and user context
- **OpenAI Embeddings**: Semantic understanding of products and queries
- **Contextual Memory**: User preference learning and conversation history

### 🏗️ **Architecture**

```
User Query → Langflow Flow → AstraDB Vector Search → Contextual Recommendations
     ↓              ↓                ↓                        ↓
 Intent Analysis → Embedding → Similarity Search → Business Logic → Response
```

### 🚀 **Features**

#### **Semantic Search**
- Vector-based product similarity
- Intent understanding beyond keywords
- Multi-modal product understanding (title, description, categories, tags)

#### **Contextual Recommendations**
- User conversation history
- Preference learning
- Cross-selling and upselling logic
- Personalized product suggestions

#### **Intelligent Conversations**
- Natural language understanding
- Follow-up questions for clarification
- Product comparison capabilities
- Accessibility-focused recommendations

### 🛠️ **Components**

1. **Product Vectorization Service** (`product_vectorizer.py`)
   - Fetches products from WooCommerce API
   - Generates embeddings using OpenAI
   - Stores vectors in AstraDB

2. **Langflow Recommendation Flow** (`recommendation_flow.json`)
   - Conversational AI logic
   - Intent classification
   - Context management
   - Recommendation generation

3. **AstraDB Integration** (`astra_client.py`)
   - Vector storage and retrieval
   - User context management
   - Similarity search operations

4. **API Gateway** (`intelligent_api.py`)
   - Bridges existing WooCommerce proxy with Langflow
   - Handles fallback to keyword search
   - Response formatting

### 📊 **Data Flow**

#### **Product Ingestion**
```
WooCommerce API → Product Data → OpenAI Embeddings → AstraDB Vector Store
```

#### **User Query Processing**
```
User Query → Langflow Flow → Intent Analysis → Vector Search → Contextual Filtering → Response
```

#### **Learning Loop**
```
User Interactions → Context Updates → Preference Learning → Improved Recommendations
```

### 🔧 **Setup Instructions**

1. **Environment Setup**
```bash
pip install langflow astrapy openai python-dotenv
```

2. **AstraDB Configuration**
```bash
# Set up AstraDB credentials
ASTRA_DB_APPLICATION_TOKEN=your_token
ASTRA_DB_API_ENDPOINT=your_endpoint
ASTRA_DB_KEYSPACE=woo_recommendations
```

3. **Product Vectorization**
```bash
python product_vectorizer.py --sync-all
```

4. **Langflow Flow Deployment**
```bash
langflow run --host 0.0.0.0 --port 7860
```

### 🎯 **Integration Points**

- **Existing WooCommerce Proxy**: Enhanced with AI recommendations
- **Frontend Chatbot**: Upgraded with contextual conversations
- **Analytics**: User interaction tracking and preference learning

### 🚀 **Next Steps**

1. Set up AstraDB vector collection
2. Create product embedding pipeline
3. Design Langflow recommendation flow
4. Integrate with existing WooCommerce proxy
5. Deploy and test intelligent recommendations

---

*This system will transform the current keyword-based search into an intelligent, context-aware product recommendation engine that learns from user interactions and provides personalized suggestions.*
