#!/usr/bin/env python3
"""
Test script for local sentiment analysis with Mistral 7B model
"""

import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from local_sentiment_analyzer import LocalSentimentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_local_sentiment():
    """Test the local sentiment analysis functionality."""
    logger.info("Starting local sentiment analysis test...")
    
    # Initialize local sentiment analyzer
    analyzer = LocalSentimentAnalyzer()
    
    # Test cases
    test_cases = [
        "I'm so happy and excited about this wonderful opportunity!",
        "This is really frustrating and disappointing.",
        "I'm feeling curious and interested in learning more.",
        "That's a bit confusing, could you explain it differently?",
        "Thank you so much for your kind and helpful assistance.",
        "I'm angry and upset about this terrible situation.",
        "I'm content and peaceful with how things are going."
    ]
    
    try:
        for i, text in enumerate(test_cases):
            logger.info(f"Analyzing text {i+1}: {text[:50]}...")
            
            # Analyze sentiment
            scores = await analyzer.analyze_utterance(text)
            
            # Get top emotions
            top_emotions = scores.get_top_emotions(3)
            
            logger.info(f"Top emotions: {top_emotions}")
            
            # Wait a bit between requests to avoid overwhelming the local model
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error during local sentiment test: {e}")
        raise
    
    logger.info("Local sentiment analysis test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_local_sentiment())