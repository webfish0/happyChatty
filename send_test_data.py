#!/usr/bin/env python3
"""
Script to send test data to the speech analysis system for dashboard testing
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_test_data():
    """Send test data to the speech analysis WebSocket server."""
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            
            # Sample test data
            test_events = [
                {
                    "timestamp": datetime.now().isoformat() + 'Z',
                    "speaker": "SPEAKER_01",
                    "text": "Hello everyone! I'm really excited to be here today.",
                    "scores": {
                        "Happy": 0.85,
                        "Enthusiastic": 0.75,
                        "Content": 0.60,
                        "Joyful": 0.55,
                        "Sad": 0.05,
                        "Angry": 0.02
                    },
                    "duration": 3.2,
                    "confidence": 0.92
                },
                {
                    "timestamp": datetime.now().isoformat() + 'Z',
                    "speaker": "SPEAKER_02", 
                    "text": "That's wonderful! I'm feeling quite positive about this as well.",
                    "scores": {
                        "Happy": 0.78,
                        "Content": 0.70,
                        "Helpful": 0.65,
                        "Grateful": 0.60,
                        "Sad": 0.10,
                        "Anxious": 0.08
                    },
                    "duration": 2.8,
                    "confidence": 0.89
                },
                {
                    "timestamp": datetime.now().isoformat() + 'Z',
                    "speaker": "SPEAKER_01",
                    "text": "I have to admit, I'm a bit concerned about the timeline though.",
                    "scores": {
                        "Anxious": 0.65,
                        "Concerned": 0.60,
                        "Thoughtful": 0.55,
                        "Happy": 0.30,
                        "Sad": 0.25,
                        "Frustrated": 0.20
                    },
                    "duration": 3.1,
                    "confidence": 0.91
                },
                {
                    "timestamp": datetime.now().isoformat() + 'Z',
                    "speaker": "SPEAKER_02",
                    "text": "Don't worry too much about it. I'm sure we can work through it together.",
                    "scores": {
                        "Helpful": 0.80,
                        "Kind": 0.75,
                        "Compassionate": 0.70,
                        "Reassuring": 0.65,
                        "Happy": 0.40,
                        "Sad": 0.15
                    },
                    "duration": 3.5,
                    "confidence": 0.88
                }
            ]
            
            # Send test events
            for i, event in enumerate(test_events):
                await websocket.send(json.dumps(event))
                logger.info(f"Sent event {i+1}: {event['speaker']} - {event['text'][:50]}...")
                await asyncio.sleep(2)  # Wait 2 seconds between events
                
            logger.info("All test data sent successfully!")
            
    except websockets.exceptions.ConnectionClosed:
        logger.error("Connection closed by server")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_data())