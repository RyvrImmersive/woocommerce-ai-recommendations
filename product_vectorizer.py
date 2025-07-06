#!/usr/bin/env python3
"""
🤖 WooCommerce Product Vectorization Service
Fetches products from WooCommerce API and stores embeddings in AstraDB
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import requests
import openai
from astrapy.db import AstraDB
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ProductData:
    """Product data structure for vectorization"""
    id: int
    name: str
    description: str
    short_description: str
    categories: List[str]
    tags: List[str]
    price: str
    regular_price: str
    sale_price: Optional[str]
    stock_status: str
    image_url: Optional[str]
    permalink: str
    rating: float
    review_count: int
    
    def to_text_for_embedding(self) -> str:
        """Convert product to text for embedding generation"""
        text_parts = [
            f"Product: {self.name}",
            f"Description: {self.description}",
            f"Short Description: {self.short_description}",
            f"Categories: {', '.join(self.categories)}",
            f"Tags: {', '.join(self.tags)}",
            f"Price: {self.price}",
            f"Stock: {self.stock_status}",
            f"Rating: {self.rating}/5 ({self.review_count} reviews)"
        ]
        return " | ".join(filter(None, text_parts))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for AstraDB storage"""
        return {
            "product_id": self.id,
            "name": self.name,
            "description": self.description,
            "short_description": self.short_description,
            "categories": self.categories,
            "tags": self.tags,
            "price": self.price,
            "regular_price": self.regular_price,
            "sale_price": self.sale_price,
            "stock_status": self.stock_status,
            "image_url": self.image_url,
            "permalink": self.permalink,
            "rating": self.rating,
            "review_count": self.review_count,
            "updated_at": datetime.utcnow().isoformat()
        }

class WooCommerceClient:
    """WooCommerce API client"""
    
    def __init__(self):
        self.base_url = "https://enablemart.in/wp-json/wc/v3/products"
        self.auth = (os.getenv('WC_KEY'), os.getenv('WC_SECRET'))
        
    def fetch_products(self, per_page: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Fetch products from WooCommerce API"""
        try:
            response = requests.get(
                self.base_url,
                params={
                    'per_page': per_page,
                    'page': page,
                    'status': 'publish'
                },
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    def fetch_all_products(self) -> List[ProductData]:
        """Fetch all products from WooCommerce"""
        all_products = []
        page = 1
        
        while True:
            logger.info(f"Fetching products page {page}...")
            products = self.fetch_products(per_page=100, page=page)
            
            if not products:
                break
                
            for product in products:
                try:
                    product_data = ProductData(
                        id=product['id'],
                        name=product['name'],
                        description=self._clean_html(product.get('description', '')),
                        short_description=self._clean_html(product.get('short_description', '')),
                        categories=[cat['name'] for cat in product.get('categories', [])],
                        tags=[tag['name'] for tag in product.get('tags', [])],
                        price=product.get('price', '0'),
                        regular_price=product.get('regular_price', '0'),
                        sale_price=product.get('sale_price'),
                        stock_status=product.get('stock_status', 'outofstock'),
                        image_url=product['images'][0]['src'] if product.get('images') else None,
                        permalink=product.get('permalink', ''),
                        rating=float(product.get('average_rating', 0)),
                        review_count=int(product.get('rating_count', 0))
                    )
                    all_products.append(product_data)
                except Exception as e:
                    logger.warning(f"Error processing product {product.get('id')}: {e}")
            
            page += 1
            if len(products) < 100:  # Last page
                break
        
        logger.info(f"Fetched {len(all_products)} products total")
        return all_products
    
    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text"""
        import re
        if not html_text:
            return ""
        # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', html_text)
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        return clean

class AstraDBClient:
    """AstraDB client for vector operations"""
    
    def __init__(self):
        self.database = AstraDB(
            token=os.getenv('ASTRA_DB_APPLICATION_TOKEN'),
            api_endpoint=os.getenv('ASTRA_DB_API_ENDPOINT')
        )
        self.collection_name = "woo_products"
        self.collection = None
        
    def initialize_collection(self):
        """Initialize the products collection"""
        try:
            # Create collection with vector dimension for OpenAI embeddings (1536)
            self.collection = self.database.create_collection(
                self.collection_name,
                dimension=1536,
                metric="cosine"
            )
            logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            # Collection might already exist
            self.collection = self.database.collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
    
    def store_product_embedding(self, product: ProductData, embedding: List[float]):
        """Store product with its embedding in AstraDB"""
        document = product.to_dict()
        document["$vector"] = embedding
        
        try:
            self.collection.insert_one(document)
            logger.debug(f"Stored product {product.id}: {product.name}")
        except Exception as e:
            logger.error(f"Error storing product {product.id}: {e}")
    
    def search_similar_products(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar products using vector similarity"""
        try:
            results = self.collection.vector_find(
                query_embedding,
                limit=limit,
                include_similarity=True
            )
            return results
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []

class EmbeddingGenerator:
    """OpenAI embedding generation"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "text-embedding-3-small"  # More cost-effective
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

class ProductVectorizer:
    """Main product vectorization service"""
    
    def __init__(self):
        self.woo_client = WooCommerceClient()
        self.astra_client = AstraDBClient()
        self.embedding_generator = EmbeddingGenerator()
    
    def sync_all_products(self):
        """Sync all products to AstraDB with embeddings"""
        logger.info("🚀 Starting product vectorization...")
        
        # Initialize AstraDB collection
        self.astra_client.initialize_collection()
        
        # Fetch all products
        products = self.woo_client.fetch_all_products()
        
        if not products:
            logger.error("No products found!")
            return
        
        logger.info(f"Processing {len(products)} products...")
        
        # Process products in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            self._process_batch(batch)
            
            # Small delay between batches
            import time
            time.sleep(1)
        
        logger.info("✅ Product vectorization complete!")
    
    def _process_batch(self, products: List[ProductData]):
        """Process a batch of products"""
        for product in products:
            self._process_single_product(product)
    
    def _process_single_product(self, product: ProductData):
        """Process a single product"""
        try:
            # Generate text for embedding
            text = product.to_text_for_embedding()
            
            # Generate embedding
            embedding = self.embedding_generator.generate_embedding(text)
            
            if embedding:
                # Store in AstraDB
                self.astra_client.store_product_embedding(product, embedding)
                logger.info(f"✅ Processed: {product.name}")
            else:
                logger.warning(f"❌ Failed to generate embedding for: {product.name}")
                
        except Exception as e:
            logger.error(f"Error processing product {product.id}: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WooCommerce Product Vectorizer')
    parser.add_argument('--sync-all', action='store_true', help='Sync all products')
    args = parser.parse_args()
    
    vectorizer = ProductVectorizer()
    
    if args.sync_all:
        vectorizer.sync_all_products()
    else:
        print("Use --sync-all to start product vectorization")

if __name__ == "__main__":
    main()
