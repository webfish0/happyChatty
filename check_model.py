#!/usr/bin/env python3
"""
Script to check OpenRouter configuration and model settings.
"""

import os
from config import config
from sentiment_analyzer import SentimentAnalyzer

def check_configuration():
    """Check and display current configuration."""
    print("🔍 Checking OpenRouter Configuration...")
    print("=" * 50)
    
    # Check API key
    api_key = config.sentiment.openrouter_api_key
    if api_key:
        print("✅ OpenRouter API Key: FOUND")
        print(f"   Key starts with: {api_key[:8]}...")
    else:
        print("❌ OpenRouter API Key: NOT FOUND")
        print("   Set OPENROUTER_API_KEY environment variable")
    
    # Check model
    model = config.sentiment.model
    print(f"📊 Model: {model}")
    
    # Check if it's a free model
    free_models = [
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-9b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "microsoft/wizardlm-2-7b:free"
    ]
    
    if ":free" in model:
        print("✅ This is a FREE OpenRouter model")
    elif model in free_models:
        print("✅ This is a FREE OpenRouter model")
    else:
        print("⚠️  This model may require payment")
    
    # Test sentiment analyzer initialization
    print("\n🧪 Testing Sentiment Analyzer...")
    try:
        analyzer = SentimentAnalyzer()
        print("✅ Sentiment analyzer initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing analyzer: {e}")
    
    print("\n" + "=" * 50)
    print("💡 To change the model, edit config.py:")
    print("   config.sentiment.model = 'your-preferred-model'")
    print("\n💡 Free OpenRouter models include:")
    for free_model in free_models:
        print(f"   - {free_model}")

if __name__ == "__main__":
    check_configuration()