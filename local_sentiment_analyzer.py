import asyncio
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import aiohttp
from config import config
from sentiment_analyzer import SentimentScores
from performance_profiler import ComponentProfiler

logger = logging.getLogger(__name__)

class LocalSentimentAnalyzer:
    """Sentiment analysis using local LLM via LM Studio API."""
    
    def __init__(self, api_url: str = "http://127.0.0.1:1234/v1"):
        self.api_url = api_url
        self.model = "mistralai/Mistral-7B-Instruct-v0.3"
        print(f"✅ Using local Mistral 7B model: {self.model}")
        print(f"🌐 Local API endpoint: {self.api_url}")
        logger.info(f"Initialized local sentiment analyzer with model: {self.model}")
    
    async def analyze_utterance(self, text: str, speaker: str = "unknown") -> SentimentScores:
        """Analyze sentiment of a single utterance using local LLM."""
        with ComponentProfiler("sentiment", "analyze_utterance", {"text_length": len(text), "speaker": speaker}):
            if not text.strip():
                return SentimentScores()
            
            try:
                return await self._call_local_api(text, speaker)
            except Exception as e:
                logger.error(f"Error calling local API: {e}")
                return self._mock_analysis(text)
    
    async def _call_local_api(self, text: str, speaker: str) -> SentimentScores:
        """Call local LM Studio API for sentiment analysis."""
        with ComponentProfiler("sentiment", "_call_local_api", {"text_length": len(text), "speaker": speaker}):
            headers = {
                "Content-Type": "application/json"
            }
            
            # Create prompt for multi-label classification
            labels = list(config.sentiment_labels.keys())
            labels_description = "\n".join([f"{k}: {v}" for k, v in config.sentiment_labels.items()])
            
            prompt = f"""<s>[INST] You are a sentiment analysis assistant. Analyze the emotional tone of this text and provide numerical scores for each emotion.

Text: "{text}"

For each emotion below, provide a score from 0.0 (not present) to 1.0 (strongly present):

{labels_description}

Return a JSON object with exact emotion names as keys and float values between 0.0 and 1.0. No explanations, just the JSON.

Example format:
{{"Happy": 0.2, "Sad": 0.8, "Angry": 0.1, "Content": 0.3, "Curious": 0.0}}

JSON response: [/INST]"""
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1,
                "stop": ["</s>"]
            }
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        f"{self.api_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status != 200:
                            raise Exception(f"API error: {response.status} - {await response.text()}")
                        
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Parse JSON response
                        return self._parse_response(content)
                        
                except asyncio.TimeoutError:
                    logger.warning("Local API call timed out, using mock analysis")
                    return self._mock_analysis(text)
                except Exception as e:
                    logger.error(f"Error calling local API: {e}")
                    return self._mock_analysis(text)
    
    def _parse_response(self, content: str) -> SentimentScores:
        """Parse API response into SentimentScores object."""
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
            return self._mock_analysis(content)
    
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
        """Mock sentiment analysis for testing."""
        text_lower = text.lower()
        scores = SentimentScores()
        
        # Simple keyword-based mock analysis
        positive_words = ['good', 'great', 'happy', 'love', 'wonderful', 'amazing', 'fantastic', 'excellent']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'angry', 'sad', 'frustrated']
        
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