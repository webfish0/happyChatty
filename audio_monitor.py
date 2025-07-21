#!/usr/bin/env python3
"""
Simple audio level monitor to verify microphone input.
"""

import asyncio
import logging
import numpy as np
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from audio_capture import AsyncAudioCapture

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioMonitor:
    """Simple audio level monitor."""
    
    def __init__(self):
        self.running = False
        
    async def monitor(self, duration=10):
        """Monitor audio levels for specified duration."""
        logger.info("Starting audio level monitor...")
        logger.info("Speak into your microphone to see levels...")
        
        audio_capture = AsyncAudioCapture()
        
        try:
            await audio_capture.start_recording()
            self.running = True
            
            start_time = asyncio.get_event_loop().time()
            chunk_count = 0
            
            async for audio_chunk in audio_capture.get_audio_chunks():
                if not self.running or (asyncio.get_event_loop().time() - start_time) > duration:
                    break
                
                chunk_count += 1
                if audio_chunk and len(audio_chunk) > 0:
                    level = audio_capture.get_audio_level(audio_chunk)
                    
                    # Visual level indicator
                    bar_length = 50
                    filled = int(level * bar_length)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    print(f"\rAudio Level: [{bar}] {level:.3f} ({len(audio_chunk)} bytes)", end="")
                    
                    if level > 0.1:
                        logger.info(f"\n🔊 Good audio level detected: {level:.3f}")
                    elif level > 0.001:
                        logger.info(f"\n🔈 Low audio level: {level:.3f}")
                    else:
                        logger.info(f"\n🔇 No audio detected: {level:.3f}")
                
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitor error: {e}")
        finally:
            self.running = False
            await audio_capture.stop_recording()
            logger.info("\nAudio monitoring completed")

async def main():
    """Main monitor function."""
    monitor = AudioMonitor()
    await monitor.monitor(duration=30)

if __name__ == "__main__":
    asyncio.run(main())