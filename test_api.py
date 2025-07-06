#!/usr/bin/env python3
"""
Test script for the Intelligent Recommendations API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_trending_products():
    """Test trending products endpoint"""
    print("\n🔍 Testing trending products...")
    try:
        response = requests.get(f"{BASE_URL}/api/trending?limit=5")
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Trending products returned {len(results.get('products', []))} products")
            if results.get('products'):
                print(f"   Sample product: {results['products'][0].get('name', 'Unknown')}")
        else:
            print(f"❌ Trending products failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Trending products error: {e}")

def test_intelligent_search():
    """Test intelligent search with Langflow"""
    print("\n🔍 Testing intelligent search...")
    try:
        payload = {
            "query": "I need help finding a good wheelchair for my elderly parent",
            "user_id": "test_user_123",
            "session_id": "test_session_456"
        }
        response = requests.post(f"{BASE_URL}/api/intelligent-search", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Intelligent search successful!")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
            print(f"   Products: {len(result.get('products', []))} found")
        else:
            print(f"❌ Intelligent search failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Intelligent search error: {e}")

def test_product_recommendations():
    """Test product-specific recommendations"""
    print("\n🔍 Testing product recommendations...")
    try:
        # Use a sample product ID (assuming products exist)
        product_id = 1
        response = requests.get(f"{BASE_URL}/api/product-recommendations/{product_id}?limit=3")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Product recommendations returned {len(result.get('recommendations', []))} products")
        else:
            print(f"❌ Product recommendations failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Product recommendations error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting API tests...\n")
    
    # Test health first
    if not test_health():
        print("❌ Service not available, stopping tests")
        return
    
    # Wait a moment for service to be fully ready
    time.sleep(2)
    
    # Run other tests
    test_trending_products()
    test_intelligent_search()
    test_product_recommendations()
    
    print("\n✅ API testing complete!")

if __name__ == "__main__":
    main()
