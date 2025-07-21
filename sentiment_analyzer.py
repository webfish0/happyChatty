import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from dataclasses import dataclass, asdict
from config import config

logger = logging.getLogger(__name__)

@dataclass
class SentimentScores:
    """Sentiment analysis scores for all labels."""
    Happy: float = 0.0
    Joyful: float = 0.0
    Content: float = 0.0
    Enthusiastic: float = 0.0
    Helpful: float = 0.0
    Kind: float = 0.0
    Compassionate: float = 0.0
    Polite: float = 0.0
    Grateful: float = 0.0
    Sweet: float = 0.0
    Wholesome: float = 0.0
    Mischievous: float = 0.0
    Curious: float = 0.0
    Confused: float = 0.0
    Surprised: float = 0.0
    Sarcastic: float = 0.0
    Ironic: float = 0.0
    Teasing: float = 0.0
    Sad: float = 0.0
    Angry: float = 0.0
    Frustrated: float = 0.0
    Disappointed: float = 0.0
    Anxious: float = 0.0
    Rude: float = 0.0
    Ungrateful: float = 0.0
    Cruel: float = 0.0
    Hostile: float = 0.0
    Sleazy: float = 0.0
    Insulting: float = 0.0
    Threatening: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)
    
    def get_top_emotions(self, top_k: int = 3) -> List[tuple]:
        """Get top k emotions by score."""
        scores = self.to_dict()
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_k]

class SentimentAnalyzer:
    """Multi-label sentiment analysis using OpenRouter API."""
    
    def __init__(self):
        self.config = config.sentiment
        self.api_key = self.config.openrouter_api_key
        self.model = self.config.model
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            logger.warning("OpenRouter API key not found. Using mock sentiment analysis.")
            print("⚠️  No OpenRouter API key - using mock sentiment analysis")
        else:
            print(f"✅ Using OpenRouter model: {self.model}")
            logger.info(f"Initialized sentiment analyzer with model: {self.model}")
    
    async def analyze_utterance(self, text: str, speaker: str = "unknown") -> SentimentScores:
        """Analyze sentiment of a single utterance."""
        if not text.strip():
            return SentimentScores()
        
        if not self.api_key:
            logger.debug("Using mock sentiment analysis")
            return self._mock_analysis(text)
        
        try:
            return await self._call_openrouter_api(text, speaker)
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return self._mock_analysis(text)
    
    async def _call_openrouter_api(self, text: str, speaker: str) -> SentimentScores:
        """Call OpenRouter API for sentiment analysis."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:8000",
            "X-Title": "Real-time Speech Analysis"
        }
        
        # Create prompt for multi-label classification
        labels = list(config.sentiment_labels.keys())
        labels_description = "\n".join([f"{k}: {v}" for k, v in config.sentiment_labels.items()])
        
        prompt = f"""You are a sentiment analysis assistant. Analyze the emotional tone of this text and provide numerical scores for each emotion.

Text: "{text}"

For each emotion below, provide a score from 0.0 (not present) to 1.0 (strongly present):

{labels_description}

Return a JSON object with exact emotion names as keys and float values between 0.0 and 1.0. No explanations, just the JSON.

Example format:
{{"Happy": 0.2, "Sad": 0.8, "Angry": 0.1, "Content": 0.3, "Curious": 0.0}}

JSON response:"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                
                data = await response.json()
                content = data['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    # Handle markdown code blocks
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]  # Remove ```json
                    if content.endswith('```'):
                        content = content[:-3]  # Remove ```
                    content = content.strip()
                    
                    # Try to extract JSON from text
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        scores_dict = json.loads(json_str)
                        return self._parse_scores(scores_dict)
                    else:
                        scores_dict = json.loads(content)
                        return self._parse_scores(scores_dict)
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse API response, using mock analysis")
                    logger.debug(f"API response: {content}")
                    return self._mock_analysis(text)
    
    def _parse_scores(self, scores_dict: Dict[str, float]) -> SentimentScores:
        """Parse API response into SentimentScores object."""
        scores = SentimentScores()
        
        # Map response keys to our labels (case-insensitive)
        label_mapping = {label.lower(): label for label in config.sentiment_labels.keys()}
        
        for key, value in scores_dict.items():
            key_lower = key.lower()
            if key_lower in label_mapping:
                # Clamp value between 0 and 1
                clamped_value = max(0.0, min(1.0, float(value)))
                setattr(scores, label_mapping[key_lower], clamped_value)
        
        return scores
    
    def _mock_analysis(self, text: str) -> SentimentScores:
        """Mock sentiment analysis for testing without API key."""
        text_lower = text.lower()
        scores = SentimentScores()
        
        # Simple keyword-based mock analysis
        positive_words = ['good', 'great', 'happy', 'love', 'wonderful', 'amazing', 'fantastic']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'angry', 'sad']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            scores.Happy = min(0.8, positive_count * 0.2)
            scores.Content = min(0.6, positive_count * 0.15)
        elif negative_count > positive_count:
            scores.Sad = min(0.8, negative_count * 0.2)
            scores.Frustrated = min(0.6, negative_count * 0.15)
        else:
            scores.Content = 0.5
        
        # Add some random variation for realism
        import random
        for attr in scores.to_dict().keys():
            current = getattr(scores, attr)
            if current > 0:
                variation = random.uniform(-0.1, 0.1)
                setattr(scores, attr, max(0.0, min(1.0, current + variation)))
        
        return scores
    
    async def analyze_batch(self, utterances: List[str], speakers: List[str] = None) -> List[SentimentScores]:
        """Analyze multiple utterances in batch."""
        if speakers is None:
            speakers = ["unknown"] * len(utterances)
        
        if len(utterances) != len(speakers):
            raise ValueError("Utterances and speakers lists must have same length")
        
        # Process in parallel
        tasks = [
            self.analyze_utterance(text, speaker) 
            for text, speaker in zip(utterances, speakers)
        ]
        
        return await asyncio.gather(*tasks)
    
    def validate_scores(self, scores: SentimentScores) -> bool:
        """Validate sentiment scores are within expected range."""
        scores_dict = scores.to_dict()
        
        for key, value in scores_dict.items():
            if not isinstance(value, (int, float)):
                logger.warning(f"Invalid score type for {key}: {type(value)}")
                return False
            
            if not (0.0 <= value <= 1.0):
                logger.warning(f"Score out of range for {key}: {value}")
                return False
        
        return True

class SentimentCache:
    """Simple in-memory cache for sentiment analysis results."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
    
    def get(self, text: str, speaker: str) -> Optional[SentimentScores]:
        """Get cached sentiment scores."""
        key = f"{speaker}:{text}"
        return self.cache.get(key)
    
    def set(self, text: str, speaker: str, scores: SentimentScores):
        """Cache sentiment scores."""
        key = f"{speaker}:{text}"
        
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = scores
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)
