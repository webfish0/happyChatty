#!/usr/bin/env python3
"""
Debug script to test OpenRouter API directly and identify 404 errors.
"""

import os
import json
import aiohttp
import asyncio
from config import config

async def test_openrouter_api():
    """Test OpenRouter API directly to identify 404 errors."""
    
    api_key = config.sentiment.openrouter_api_key
    model = config.sentiment.model
    
    print("🔍 Debugging OpenRouter API...")
    print("=" * 50)
    print(f"API Key: {api_key[:8]}..." if api_key else "No API key")
    print(f"Model: {model}")
    print(f"Base URL: https://openrouter.ai/api/v1")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost:8000",
        "X-Title": "Real-time Speech Analysis"
    }
    
    # Test 1: Check available models
    print("\n📋 Testing model availability...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers
            ) as response:
                print(f"Models endpoint status: {response.status}")
                if response.status == 200:
                    models_data = await response.json()
                    free_models = [m for m in models_data.get('data', []) 
                                 if 'free' in m.get('id', '').lower()]
                    print(f"Found {len(free_models)} free models:")
                    for m in free_models[:5]:
                        print(f"  - {m['id']}")
                else:
                    print(f"Error: {await response.text()}")
    except Exception as e:
        print(f"Error checking models: {e}")
    
    # Test 2: Test chat completion with our model
    print(f"\n🧪 Testing chat completion with model: {model}")
    test_payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Analyze sentiment: 'I love this product!'"
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=test_payload
            ) as response:
                print(f"Chat completion status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print("✅ Success!")
                    print(f"Response: {result['choices'][0]['message']['content'][:100]}...")
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {response.status}")
                    print(f"Response: {error_text}")
                    
                    # Check if it's a model issue
                    if "model" in error_text.lower():
                        print("\n💡 Suggested fix: Try a different free model")
                        print("   Available free models:")
                        print("   - meta-llama/llama-3.1-8b-instruct")
                        print("   - google/gemma-2-9b-it")
                        print("   - mistralai/mistral-7b-instruct")
                        
    except Exception as e:
        print(f"Error testing chat completion: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter_api())