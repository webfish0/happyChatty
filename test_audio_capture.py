#!/usr/bin/env python3
"""
Test script for audio capture functionality
"""

import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio_capture import AsyncAudioCapture

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_audio_capture():
    """Test the audio capture functionality."""
    logger.info("Starting audio capture test...")
    
    # List available devices
    capture = AsyncAudioCapture()
    devices = capture.list_devices()
    logger.info(f"Available input devices: {len(devices)}")
    for device in devices:
        logger.info(f"  Device {device['index']}: {device['name']} ({device['channels']} channels)")
    
    if not devices:
        logger.error("No input devices found!")
        return
    
    # Test audio capture
    try:
        await capture.start_recording()
        logger.info("Audio recording started successfully")
        
        # Collect a few seconds of audio data
        audio_chunks = []
        audio_levels = []
        
        logger.info("Collecting audio data for 5 seconds...")
        start_time = asyncio.get_event_loop().time()
        
        async for chunk in capture.get_audio_chunks():
            audio_chunks.append(chunk)
            level = capture.get_audio_level(chunk)
            audio_levels.append(level)
            
            # Print audio level for monitoring
            if len(audio_chunks) % 10 == 0:
                logger.info(f"Audio chunks collected: {len(audio_chunks)}, Current level: {level:.3f}")
            
            # Stop after 5 seconds
            if asyncio.get_event_loop().time() - start_time > 5:
                break
                
        await capture.stop_recording()
        logger.info("Audio recording stopped")
        
        # Report results
        logger.info(f"Test completed successfully!")
        logger.info(f"Total audio chunks collected: {len(audio_chunks)}")
        logger.info(f"Average audio level: {sum(audio_levels) / len(audio_levels):.3f}" if audio_levels else "No audio levels recorded")
        logger.info(f"Audio data size: {sum(len(chunk) for chunk in audio_chunks)} bytes")
        
    except Exception as e:
        logger.error(f"Error during audio capture test: {e}")
        raise
    finally:
        # Ensure recording is stopped
        try:
            await capture.stop_recording()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_audio_capture())