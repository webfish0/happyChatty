import os
from typing import Dict, List
from pydantic import BaseModel, Field

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

class AudioConfig(BaseModel):
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    format: str = "int16"
    device_index: int = None  # None for default device

class TranscriptionConfig(BaseModel):
    model_name: str = "base"  # Whisper model size
    language: str = "en"
    max_latency: float = 2.0  # Maximum latency in seconds
    
class DiarizationConfig(BaseModel):
    model_name: str = "pyannote/speaker-diarization-3.1"
    min_speakers: int = 1
    max_speakers: int = 10
    
class SentimentConfig(BaseModel):
    openrouter_api_key: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY"))
    model: str = "google/gemma-2-9b-it:free"  # Free OpenRouter model
    max_tokens: int = 500
    temperature: float = 0.1
    
    def __post_init__(self):
        """Log the model being used."""
        if self.openrouter_api_key:
            print(f"✅ Using OpenRouter model: {self.model}")
        else:
            print("⚠️  No OpenRouter API key found - using mock sentiment analysis")
    
class AppConfig(BaseModel):
    audio: AudioConfig = AudioConfig()
    transcription: TranscriptionConfig = TranscriptionConfig()
    diarization: DiarizationConfig = DiarizationConfig()
    sentiment: SentimentConfig = SentimentConfig()
    
    # Sentiment labels with descriptions
    sentiment_labels: Dict[str, str] = {
        "Happy": "Feeling or showing pleasure or contentment",
        "Joyful": "Feeling, expressing, or causing great pleasure and happiness",
        "Content": "In a state of peaceful happiness",
        "Enthusiastic": "Having or showing intense and eager enjoyment",
        "Helpful": "Giving or ready to give help",
        "Kind": "Having or showing a friendly, generous, and considerate nature",
        "Compassionate": "Feeling or showing sympathy and concern for others",
        "Polite": "Having or showing behavior that is respectful and considerate",
        "Grateful": "Feeling or showing an appreciation for something done or received",
        "Sweet": "Pleasant, kind, and gentle toward other people",
        "Wholesome": "Conducive to or suggestive of good health and physical well-being",
        "Mischievous": "Causing or showing a fondness for causing trouble in a playful way",
        "Curious": "Eager to know or learn something",
        "Confused": "Unable to think clearly; bewildered",
        "Surprised": "Feeling or showing surprise",
        "Sarcastic": "Marked by or given to using irony in order to mock or convey contempt",
        "Ironic": "Happening in the opposite way to what is expected",
        "Teasing": "Intending to provoke or make fun of someone in a playful way",
        "Sad": "Feeling or showing sorrow; unhappy",
        "Angry": "Having a strong feeling of or showing annoyance, displeasure, or hostility",
        "Frustrated": "Feeling or expressing distress and annoyance resulting from an inability to change or achieve something",
        "Disappointed": "Sad or displeased because someone or something has failed to fulfill one's hopes or expectations",
        "Anxious": "Experiencing worry, unease, or nervousness",
        "Rude": "Offensively impolite or ill-mannered",
        "Ungrateful": "Not feeling or showing gratitude",
        "Cruel": "Willfully causing pain or suffering to others",
        "Hostile": "Unfriendly; antagonistic",
        "Sleazy": "Dirty, sordid, or disreputable",
        "Insulting": "Disrespectful or scornfully abusive",
        "Threatening": "Having a hostile or deliberately frightening quality"
    }

# Global config instance
config = AppConfig()