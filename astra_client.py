#!/usr/bin/env python3
"""
🗄️ AstraDB Client for Intelligent Product Recommendations
Handles vector storage, similarity search, and user context management
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from astrapy.db import AstraDB
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Search result with similarity score"""
    product_id: int
    name: str
    description: str
    categories: List[str]
    tags: List[str]
    price: str
    image_url: Optional[str]
    permalink: Optional[str]
    similarity_score: float
    stock_status: str
    rating: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.product_id,
            "name": self.name,
            "description": self.description,
            "categories": self.categories,
            "tags": self.tags,
            "price": self.price,
            "image": self.image_url,
            "permalink": self.permalink,
            "similarity": self.similarity_score,
            "inStock": self.stock_status == "instock",
            "rating": self.rating
        }

@dataclass
class UserContext:
    """User conversation context"""
    session_id: str
    preferences: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    last_search_query: Optional[str]
    viewed_products: List[int]
    interested_categories: List[str]
    budget_range: Optional[Tuple[float, float]]
    created_at: datetime
    updated_at: datetime

class IntelligentAstraClient:
    """Enhanced AstraDB client for intelligent recommendations"""
    
    def __init__(self):
        self.database = AstraDB(
            token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT')
        )
        
        # Collections
        self.products_collection = None
        self.user_context_collection = None
        self.interactions_collection = None
        
        # OpenAI for embeddings
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_model = "text-embedding-3-small"
    
    def initialize(self):
        """Initialize all collections"""
        self._initialize_products_collection()
        self._initialize_user_context_collection()
        self._initialize_interactions_collection()
    
    def _initialize_products_collection(self):
        """Initialize products collection"""
        try:
            self.products_collection = self.database.create_collection(
                "woo_products",
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine"
            )
            logger.info("Created products collection")
        except Exception:
            self.products_collection = self.database.collection("woo_products")
            logger.info("Using existing products collection")
    
    def _initialize_user_context_collection(self):
        """Initialize user context collection"""
        try:
            self.user_context_collection = self.database.create_collection(
                "user_contexts",
                dimension=1536,  # For user preference embeddings
                metric="cosine"
            )
            logger.info("Created user contexts collection")
        except Exception:
            self.user_context_collection = self.database.collection("user_contexts")
            logger.info("Using existing user contexts collection")
    
    def _initialize_interactions_collection(self):
        """Initialize interactions collection"""
        try:
            self.interactions_collection = self.database.create_collection(
                "user_interactions"
            )
            logger.info("Created interactions collection")
        except Exception:
            self.interactions_collection = self.database.collection("user_interactions")
            logger.info("Using existing interactions collection")
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []
    
    def semantic_search(
        self, 
        query: str, 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[UserContext] = None
    ) -> List[SearchResult]:
        """Perform semantic search with optional filtering and personalization"""
        
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        if not query_embedding:
            return []
        
        try:
            # Build search parameters
            search_params = {
                "limit": limit * 2,  # Get more results for filtering
                "include_similarity": True
            }
            
            # Add filters if provided
            if filters:
                search_params["filter"] = filters
            
            # Perform vector search
            results = self.products_collection.vector_find(
                query_embedding,
                **search_params
            )
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                try:
                    search_result = SearchResult(
                        product_id=result["product_id"],
                        name=result["name"],
                        description=result["description"],
                        categories=result.get("categories", []),
                        tags=result.get("tags", []),
                        price=result["price"],
                        image_url=result.get("image_url"),
                        permalink=result.get("permalink"),
                        similarity_score=result.get("$similarity", 0.0),
                        stock_status=result.get("stock_status", "outofstock"),
                        rating=result.get("rating", 0.0)
                    )
                    search_results.append(search_result)
                except Exception as e:
                    logger.warning(f"Error processing search result: {e}")
            
            # Apply personalization if user context available
            if user_context:
                search_results = self._personalize_results(search_results, user_context)
            
            # Sort by similarity and return top results
            search_results.sort(key=lambda x: x.similarity_score, reverse=True)
            return search_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _personalize_results(
        self, 
        results: List[SearchResult], 
        user_context: UserContext
    ) -> List[SearchResult]:
        """Apply personalization to search results"""
        
        # Boost results based on user preferences
        for result in results:
            # Category preference boost
            if any(cat in user_context.interested_categories for cat in result.categories):
                result.similarity_score += 0.1
            
            # Budget range filtering
            if user_context.budget_range:
                try:
                    price = float(result.price.replace(',', '').replace('₹', ''))
                    min_budget, max_budget = user_context.budget_range
                    if min_budget <= price <= max_budget:
                        result.similarity_score += 0.05
                    elif price > max_budget:
                        result.similarity_score -= 0.1
                except (ValueError, AttributeError):
                    pass
            
            # Previously viewed products (slight penalty to encourage diversity)
            if result.product_id in user_context.viewed_products:
                result.similarity_score -= 0.02
        
        return results
    
    def get_user_context(self, session_id: str) -> Optional[UserContext]:
        """Retrieve user context by session ID"""
        try:
            result = self.user_context_collection.find_one(
                {"session_id": session_id}
            )
            
            if result:
                return UserContext(
                    session_id=result["session_id"],
                    preferences=result.get("preferences", {}),
                    conversation_history=result.get("conversation_history", []),
                    last_search_query=result.get("last_search_query"),
                    viewed_products=result.get("viewed_products", []),
                    interested_categories=result.get("interested_categories", []),
                    budget_range=tuple(result["budget_range"]) if result.get("budget_range") else None,
                    created_at=datetime.fromisoformat(result["created_at"]),
                    updated_at=datetime.fromisoformat(result["updated_at"])
                )
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving user context: {e}")
            return None
    
    def update_user_context(self, user_context: UserContext):
        """Update or create user context"""
        try:
            user_context.updated_at = datetime.utcnow()
            
            document = {
                "session_id": user_context.session_id,
                "preferences": user_context.preferences,
                "conversation_history": user_context.conversation_history,
                "last_search_query": user_context.last_search_query,
                "viewed_products": user_context.viewed_products,
                "interested_categories": user_context.interested_categories,
                "budget_range": list(user_context.budget_range) if user_context.budget_range else None,
                "created_at": user_context.created_at.isoformat(),
                "updated_at": user_context.updated_at.isoformat()
            }
            
            # Generate user preference embedding for similarity matching
            if user_context.conversation_history:
                recent_queries = [msg["content"] for msg in user_context.conversation_history[-5:] 
                                if msg["role"] == "user"]
                if recent_queries:
                    preference_text = " ".join(recent_queries)
                    preference_embedding = self.generate_query_embedding(preference_text)
                    if preference_embedding:
                        document["$vector"] = preference_embedding
            
            self.user_context_collection.replace_one(
                {"session_id": user_context.session_id},
                document,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error updating user context: {e}")
    
    def log_interaction(
        self, 
        session_id: str, 
        interaction_type: str, 
        data: Dict[str, Any]
    ):
        """Log user interaction for analytics and learning"""
        try:
            interaction = {
                "session_id": session_id,
                "interaction_type": interaction_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.interactions_collection.insert_one(interaction)
            
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")
    
    def get_trending_products(self, limit: int = 10) -> List[SearchResult]:
        """Get trending products based on recent interactions"""
        try:
            # Get products with high interaction rates in the last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            # This would require aggregation pipeline in a real implementation
            # For now, return products with high ratings as a proxy
            results = self.products_collection.find(
                {"rating": {"$gte": 4.0}},
                limit=limit,
                sort={"rating": -1, "review_count": -1}
            )
            
            trending = []
            for result in results:
                search_result = SearchResult(
                    product_id=result["product_id"],
                    name=result["name"],
                    description=result["description"],
                    categories=result.get("categories", []),
                    tags=result.get("tags", []),
                    price=result["price"],
                    image_url=result.get("image_url"),
                    permalink=result.get("permalink"),
                    similarity_score=1.0,  # Max score for trending
                    stock_status=result.get("stock_status", "outofstock"),
                    rating=result.get("rating", 0.0)
                )
                trending.append(search_result)
            
            return trending
            
        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
            return []
    
    def get_recommendations_for_product(
        self, 
        product_id: int, 
        limit: int = 5
    ) -> List[SearchResult]:
        """Get product recommendations based on a specific product"""
        try:
            # Get the product
            product = self.products_collection.find_one(
                {"product_id": product_id}
            )
            
            if not product:
                return []
            
            # Use product's embedding to find similar products
            if "$vector" in product:
                results = self.products_collection.vector_find(
                    product["$vector"],
                    limit=limit + 1,  # +1 to exclude the original product
                    include_similarity=True
                )
                
                # Filter out the original product and convert to SearchResult
                recommendations = []
                for result in results:
                    if result["product_id"] != product_id:
                        search_result = SearchResult(
                            product_id=result["product_id"],
                            name=result["name"],
                            description=result["description"],
                            categories=result.get("categories", []),
                            tags=result.get("tags", []),
                            price=result["price"],
                            image_url=result.get("image_url"),
                            permalink=result.get("permalink"),
                            similarity_score=result.get("$similarity", 0.0),
                            stock_status=result.get("stock_status", "outofstock"),
                            rating=result.get("rating", 0.0)
                        )
                        recommendations.append(search_result)
                
                return recommendations[:limit]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting product recommendations: {e}")
            return []
    
    def store_product_with_embedding(self, product_data) -> bool:
        """Store product with generated embedding in AstraDB"""
        try:
            # Generate embedding for product description
            description_text = f"{product_data.name} {product_data.description} {' '.join(product_data.categories)} {' '.join(product_data.tags)}"
            embedding = self.generate_query_embedding(description_text)
            
            if not embedding:
                logger.error(f"Failed to generate embedding for product {product_data.id}")
                return False
            
            # Use the ProductData to_dict method and add vector
            document = product_data.to_dict()
            document["$vector"] = embedding
            
            # Insert or update the document
            try:
                # Try to update first
                result = self.products_collection.update_one(
                    filter={"product_id": product_data.id},
                    update={"$set": document}
                )
                if result.modified_count == 0:
                    # If no document was updated, insert new one
                    result = self.products_collection.insert_one(document)
            except Exception:
                # If update fails, try insert
                result = self.products_collection.insert_one(document)
            
            logger.info(f"Product {product_data.id} stored successfully in AstraDB")
            return True
            
        except Exception as e:
            logger.error(f"Error storing product {product_data.id}: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product from AstraDB"""
        try:
            result = self.products_collection.delete_one(
                filter={"product_id": product_id}
            )
            
            if result.deleted_count > 0:
                logger.info(f"Product {product_id} deleted successfully from AstraDB")
                return True
            else:
                logger.warning(f"Product {product_id} not found in AstraDB")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the products collection"""
        try:
            # Get total document count
            total_docs = self.products_collection.count_documents({})
            
            # Get recent products count (last 30 days)
            thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
            recent_docs = self.products_collection.count_documents({
                "date_modified": {"$gte": thirty_days_ago}
            })
            
            # Get products by status
            published_docs = self.products_collection.count_documents({
                "status": "publish"
            })
            
            return {
                "total_documents": total_docs,
                "recent_documents": recent_docs,
                "published_documents": published_docs,
                "collection_name": "woo_products",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "total_documents": 0,
                "recent_documents": 0,
                "published_documents": 0,
                "collection_name": "woo_products",
                "last_updated": datetime.utcnow().isoformat(),
                "error": str(e)
            }

# Example usage and testing
async def test_astra_client():
    """Test the AstraDB client"""
    client = IntelligentAstraClient()
    await client.initialize()
    
    # Test semantic search
    results = await client.semantic_search("wheelchair for elderly", limit=5)
    print(f"Found {len(results)} results")
    
    for result in results:
        print(f"- {result.name} (similarity: {result.similarity_score:.3f})")

if __name__ == "__main__":
    asyncio.run(test_astra_client())
