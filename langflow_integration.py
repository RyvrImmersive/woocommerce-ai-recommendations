#!/usr/bin/env python3
"""
🔄 Langflow Integration for Intelligent Product Recommendations
Connects Langflow flows with AstraDB for contextual AI recommendations
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from astra_client import IntelligentAstraClient, UserContext, SearchResult

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    products: List[Dict[str, Any]]
    conversation_response: str
    suggestions: List[str]
    session_id: str
    context_updated: bool

class ConversationMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None

class LangflowClient:
    """Client for interacting with Langflow flows"""
    
    def __init__(self, langflow_url: str = "http://localhost:7860"):
        self.base_url = langflow_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def run_flow(
        self, 
        flow_id: str, 
        inputs: Dict[str, Any],
        tweaks: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a Langflow flow with given inputs"""
        try:
            payload = {
                "inputs": inputs,
                "tweaks": tweaks or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/run/{flow_id}",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error running Langflow flow: {e}")
            return {}
    
    async def get_recommendation_response(
        self,
        user_query: str,
        products: List[SearchResult],
        user_context: Optional[UserContext] = None
    ) -> Dict[str, str]:
        """Get conversational response from Langflow recommendation flow"""
        
        # Prepare context for Langflow
        context_data = {
            "user_query": user_query,
            "products_found": len(products),
            "top_products": [
                {
                    "name": p.name,
                    "description": p.description[:200],
                    "categories": p.categories,
                    "price": p.price,
                    "rating": p.rating,
                    "similarity": p.similarity_score
                }
                for p in products[:3]  # Top 3 for context
            ]
        }
        
        # Add user context if available
        if user_context:
            context_data.update({
                "conversation_history": user_context.conversation_history[-3:],  # Last 3 messages
                "user_preferences": user_context.preferences,
                "interested_categories": user_context.interested_categories,
                "budget_range": user_context.budget_range
            })
        
        # Run the recommendation flow
        flow_result = await self.run_flow(
            flow_id="recommendation_flow",  # This would be your Langflow flow ID
            inputs={
                "query": user_query,
                "context": json.dumps(context_data)
            }
        )
        
        # Extract response from flow result
        if flow_result and "outputs" in flow_result:
            return {
                "response": flow_result["outputs"].get("response", "I found some products for you!"),
                "suggestions": flow_result["outputs"].get("suggestions", [])
            }
        
        # Fallback response generation
        return self._generate_fallback_response(user_query, products, user_context)
    
    def _generate_fallback_response(
        self,
        user_query: str,
        products: List[SearchResult],
        user_context: Optional[UserContext] = None
    ) -> Dict[str, str]:
        """Generate fallback response when Langflow is unavailable"""
        
        if not products:
            return {
                "response": f"I couldn't find any products matching '{user_query}'. Could you try different keywords or let me know more about what you're looking for?",
                "suggestions": [
                    "Try more general terms",
                    "Browse by category",
                    "Tell me about your specific needs"
                ]
            }
        
        # Generate contextual response
        product_count = len(products)
        top_product = products[0]
        
        response_templates = [
            f"I found {product_count} great options for '{user_query}'! The top match is {top_product.name} with a {top_product.rating}/5 rating.",
            f"Perfect! I discovered {product_count} products that match '{user_query}'. {top_product.name} looks particularly suitable.",
            f"Great search! Here are {product_count} products for '{user_query}'. {top_product.name} is highly recommended."
        ]
        
        import random
        response = random.choice(response_templates)
        
        # Generate suggestions based on products and context
        suggestions = []
        
        # Category suggestions
        categories = list(set([cat for p in products[:3] for cat in p.categories]))
        if categories:
            suggestions.append(f"Also explore: {', '.join(categories[:2])}")
        
        # Price range suggestions
        if user_context and user_context.budget_range:
            suggestions.append("Show products in my budget")
        else:
            suggestions.append("Set a budget range")
        
        # Stock suggestions
        in_stock_count = sum(1 for p in products if p.stock_status == "instock")
        if in_stock_count < len(products):
            suggestions.append(f"{in_stock_count} items available now")
        
        return {
            "response": response,
            "suggestions": suggestions[:3]
        }

class IntelligentRecommendationService:
    """Main service combining AstraDB and Langflow for intelligent recommendations"""
    
    def __init__(self):
        self.astra_client = IntelligentAstraClient()
        self.langflow_client = LangflowClient()
        self.initialized = False
    
    async def initialize(self):
        """Initialize the service"""
        if not self.initialized:
            self.astra_client.initialize()
            self.initialized = True
            logger.info("Intelligent Recommendation Service initialized")
    
    async def get_recommendations(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> RecommendationResponse:
        """Get intelligent product recommendations"""
        
        await self.initialize()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create user context
        user_context = self.astra_client.get_user_context(session_id)
        if not user_context:
            user_context = UserContext(
                session_id=session_id,
                preferences={},
                conversation_history=[],
                last_search_query=None,
                viewed_products=[],
                interested_categories=[],
                budget_range=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        # Perform semantic search
        search_results = self.astra_client.semantic_search(
            query=query,
            limit=limit,
            filters=filters,
            user_context=user_context
        )
        
        # Get conversational response from Langflow
        langflow_response = await self.langflow_client.get_recommendation_response(
            user_query=query,
            products=search_results,
            user_context=user_context
        )
        
        # Update user context
        user_context.conversation_history.append({
            "role": "user",
            "content": query,
            "timestamp": datetime.utcnow().isoformat()
        })
        user_context.conversation_history.append({
            "role": "assistant", 
            "content": langflow_response["response"],
            "timestamp": datetime.utcnow().isoformat()
        })
        user_context.last_search_query = query
        
        # Extract categories from results for user interest tracking
        result_categories = list(set([cat for result in search_results for cat in result.categories]))
        for category in result_categories:
            if category not in user_context.interested_categories:
                user_context.interested_categories.append(category)
        
        # Keep only recent conversation history (last 20 messages)
        user_context.conversation_history = user_context.conversation_history[-20:]
        user_context.interested_categories = user_context.interested_categories[-10:]
        
        # Save updated context
        self.astra_client.update_user_context(user_context)
        
        # Log interaction for analytics
        self.astra_client.log_interaction(
            session_id=session_id,
            interaction_type="search",
            data={
                "query": query,
                "results_count": len(search_results),
                "top_similarity": search_results[0].similarity_score if search_results else 0
            }
        )
        
        # Convert results to response format
        products_data = [result.to_dict() for result in search_results]
        
        return RecommendationResponse(
            products=products_data,
            conversation_response=langflow_response["response"],
            suggestions=langflow_response.get("suggestions", []),
            session_id=session_id,
            context_updated=True
        )
    
    async def get_product_recommendations(
        self,
        product_id: int,
        session_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recommendations for a specific product"""
        
        await self.initialize()
        
        # Get similar products
        recommendations = self.astra_client.get_recommendations_for_product(
            product_id=product_id,
            limit=limit
        )
        
        # Log interaction if session provided
        if session_id:
            self.astra_client.log_interaction(
                session_id=session_id,
                interaction_type="product_view",
                data={"product_id": product_id}
            )
            
            # Update user context with viewed product
            user_context = self.astra_client.get_user_context(session_id)
            if user_context:
                if product_id not in user_context.viewed_products:
                    user_context.viewed_products.append(product_id)
                    user_context.viewed_products = user_context.viewed_products[-50:]  # Keep last 50
                    self.astra_client.update_user_context(user_context)
        
        return [rec.to_dict() for rec in recommendations]
    
    async def get_trending_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending products"""
        await self.initialize()
        
        trending = self.astra_client.get_trending_products(limit=limit)
        return [product.to_dict() for product in trending]

# FastAPI app for the service
app = FastAPI(title="Intelligent Product Recommendations", version="1.0.0")
service = None

def get_service():
    """Get or create the service instance"""
    global service
    if service is None:
        service = IntelligentRecommendationService()
    return service

@app.post("/api/intelligent-search", response_model=RecommendationResponse)
async def intelligent_search(request: QueryRequest):
    """Intelligent product search with conversational AI"""
    try:
        return await get_service().get_recommendations(
            query=request.query,
            session_id=request.session_id,
            limit=request.limit,
            filters=request.filters
        )
    except Exception as e:
        logger.error(f"Error in intelligent search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/product-recommendations/{product_id}")
async def product_recommendations(
    product_id: int,
    session_id: Optional[str] = None,
    limit: int = 5
):
    """Get recommendations for a specific product"""
    try:
        recommendations = await get_service().get_product_recommendations(
            product_id=product_id,
            session_id=session_id,
            limit=limit
        )
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error getting product recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trending")
async def trending_products(limit: int = 10):
    """Get trending products"""
    try:
        trending = await get_service().get_trending_products(limit=limit)
        return {"products": trending}
    except Exception as e:
        logger.error(f"Error getting trending products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "intelligent-recommendations"}

if __name__ == "__main__":
    import uvicorn
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Handle PORT environment variable safely (Railway fix)
    port_env = os.getenv("PORT", "8001")
    logger.info(f"Raw PORT env var: '{port_env}'")
    
    try:
        port = int(port_env)
        logger.info(f"Parsed port: {port}")
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to parse PORT '{port_env}': {e}")
        port = 8001
        logger.info(f"Using default port: {port}")
    
    logger.info(f"Starting intelligent recommendations API on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
