# Real-time Speech Sentiment Analysis System

A comprehensive real-time speech analysis system that captures live audio, performs speech-to-text with speaker diarization, and analyzes sentiment using multi-label classification with 30 different emotional dimensions.

## Features

- **Live Audio Capture**: Real-time microphone audio capture with configurable parameters
- **Speech-to-Text**: Advanced transcription using Whisper with speaker diarization
- **Multi-label Sentiment Analysis**: 30-dimensional emotional analysis using OpenRouter AI models
- **Real-time Event Streaming**: WebSocket server for live JSON event emission
- **File Output**: Structured JSON logging to files
- **Speaker Identification**: Automatic speaker labeling and tracking
- **Utterance Segmentation**: Intelligent speech segmentation into meaningful utterances

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd speech-sentiment-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Required for sentiment analysis
export OPENROUTER_API_KEY="your-openrouter-api-key"

# Required for speaker diarization
export HUGGINGFACE_TOKEN="your-huggingface-token"
```

4. Run the system:
```bash
python main.py
```

### Basic Usage

```bash
# Start with default settings
python main.py

# Start with custom WebSocket port
python main.py --port 8080

# Save events to file
python main.py --output events.json

# Use specific audio device
python main.py --device 0

# List available audio devices
python main.py --list-devices
```

## Architecture

### Components

1. **Audio Capture** (`audio_capture.py`)
   - Real-time microphone input
   - Configurable sample rates and buffer sizes
   - Device enumeration and selection

2. **Transcription Engine** (`transcription_engine.py`)
   - Whisper-based speech-to-text
   - Speaker diarization using pyannote
   - Confidence scoring

3. **Utterance Segmenter** (`utterance_segmenter.py`)
   - Intelligent speech segmentation
   - Speaker continuity tracking
   - Pause-based boundary detection

4. **Sentiment Analyzer** (`sentiment_analyzer.py`)
   - 30-label emotional classification
   - OpenRouter API integration
   - Caching and fallback mechanisms

5. **Event Emitter** (`event_emitter.py`)
   - WebSocket server for real-time streaming
   - JSON file output
   - Callback system for custom processing

6. **Main Orchestrator** (`main.py`)
   - Coordinates all components
   - Graceful shutdown handling
   - Configuration management

### Data Flow

```
Microphone → Audio Capture → Transcription → Segmentation → Sentiment Analysis → Event Emission
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | API key for sentiment analysis | Yes |
| `HUGGINGFACE_TOKEN` | Token for speaker diarization | Yes |

### Configuration File

Create `config.json` to customize settings:

```json
{
  "audio": {
    "sample_rate": 16000,
    "chunk_duration": 0.5,
    "channels": 1
  },
  "transcription": {
    "model": "base",
    "language": "en"
  },
  "sentiment": {
    "model": "meta-llama/llama-3.1-8b-instruct:free",
    "max_tokens": 100,
    "temperature": 0.1
  },
  "websocket": {
    "host": "localhost",
    "port": 8765
  }
}
```

## API Reference

### Event Format

Each analysis event is emitted as JSON with the following structure:

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "speaker": "Speaker_1",
  "text": "Hello, how are you today?",
  "scores": {
    "Happy": 0.8,
    "Joyful": 0.6,
    "Content": 0.7,
    "Enthusiastic": 0.5,
    "Helpful": 0.9,
    "Kind": 0.8,
    "Compassionate": 0.7,
    "Polite": 0.9,
    "Grateful": 0.6,
    "Sweet": 0.5,
    "Wholesome": 0.8,
    "Mischievous": 0.1,
    "Curious": 0.3,
    "Confused": 0.0,
    "Surprised": 0.2,
    "Sarcastic": 0.0,
    "Ironic": 0.0,
    "Teasing": 0.1,
    "Sad": 0.0,
    "Angry": 0.0,
    "Frustrated": 0.0,
    "Disappointed": 0.0,
    "Anxious": 0.0,
    "Rude": 0.0,
    "Ungrateful": 0.0,
    "Cruel": 0.0,
    "Hostile": 0.0,
    "Sleazy": 0.0,
    "Insulting": 0.0,
    "Threatening": 0.0
  },
  "duration": 2.5,
  "confidence": 0.85
}
```

### WebSocket API

Connect to `ws://localhost:8765` to receive real-time events.

Example JavaScript client:

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Speaker:', data.speaker);
    console.log('Text:', data.text);
    console.log('Top emotions:', Object.entries(data.scores)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3));
};
```

## Testing

Run the test suite:

```bash
python test_pipeline.py
```

## Troubleshooting

### Common Issues

1. **No audio devices found**
   - Check microphone permissions
   - Verify audio drivers are installed
   - Run `python main.py --list-devices`

2. **API key errors**
   - Ensure `OPENROUTER_API_KEY` is set
   - Check API key validity
   - Verify network connectivity

3. **Speaker diarization fails**
   - Ensure `HUGGINGFACE_TOKEN` is set
   - Check internet connection for model downloads
   - Verify sufficient RAM (minimum 4GB)

4. **High CPU usage**
   - Reduce audio sample rate in config
   - Use smaller Whisper model
   - Increase chunk duration

### Performance Tuning

- **CPU Usage**: Use `tiny` or `base` Whisper model
- **Memory**: Reduce audio buffer size
- **Latency**: Decrease chunk duration
- **Accuracy**: Use larger Whisper model

### Performance Monitoring

The system includes comprehensive performance profiling capabilities:

- **Real-time Metrics**: Track processing times for each component
- **Component Profiling**: Monitor audio capture, transcription, sentiment analysis, and event emission
- **Performance Dashboard**: Web-based dashboard at `http://localhost:8080`
- **JSON Metrics**: Performance data included in output events

#### Performance Dashboard

Start the performance dashboard:
```bash
python main.py --dashboard
```

Access at `http://localhost:8080` to view:
- Real-time processing times
- Component performance breakdowns
- Memory usage tracking
- Event throughput metrics

#### Performance Metrics in Events

Each event now includes detailed performance metrics:

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "speaker": "Speaker_1",
  "text": "Hello, how are you today?",
  "scores": {...},
  "duration": 2.5,
  "confidence": 0.85,
  "performance_metrics": {
    "audio_capture": {
      "avg_time": 0.012,
      "total_calls": 45,
      "last_duration": 0.008
    },
    "transcription": {
      "avg_time": 0.234,
      "total_calls": 15,
      "last_duration": 0.189
    },
    "sentiment": {
      "avg_time": 0.456,
      "total_calls": 15,
      "last_duration": 0.423
    },
    "event_emission": {
      "avg_time": 0.003,
      "total_calls": 15,
      "last_duration": 0.002
    }
  }
}
```

#### Performance CLI Options

```bash
# Start with performance dashboard
python main.py --dashboard --dashboard-port 8080

# Monitor performance via logs
python main.py --output events.json --log-level DEBUG
```

## Development

### Project Structure

```
speech-sentiment-analysis/
├── audio_capture.py          # Audio input handling
├── transcription_engine.py   # Speech-to-text with diarization
├── utterance_segmenter.py    # Speech segmentation
├── sentiment_analyzer.py     # Multi-label sentiment analysis
├── event_emitter.py          # JSON event emission
├── main.py                   # Main orchestrator
├── config.py                 # Configuration management
├── performance_profiler.py   # Performance monitoring and profiling
├── performance_dashboard.py  # Web-based performance dashboard
├── test_pipeline.py          # Test suite
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

### Adding New Emotions

1. Add emotion to `config.py` in `sentiment_labels`
2. Add corresponding field to `SentimentScores` in `sentiment_analyzer.py`
3. Update prompt template in `sentiment_analyzer.py`

### Custom Event Handlers

```python
from event_emitter import event_emitter

def my_handler(event):
    print(f"Custom handler: {event.speaker} - {event.text}")

event_emitter.add_callback(my_handler)
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review the logs in `speech_analysis.log`
- Open an issue on GitHub