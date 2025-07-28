# Conversation Dashboard Specification

## Overview
This document specifies the requirements and design for a real-time conversation dashboard that visualizes speaker sentiment through animated facial expressions. The dashboard will display avatars representing speakers with facial expressions that dynamically change based on sentiment analysis results from the speech system.

## System Architecture

### Current System Components
The existing speech analysis system consists of:

1. **Audio Capture** - Real-time audio input processing
2. **Transcription Engine** - Speech-to-text conversion with speaker diarization
3. **Utterance Segmenter** - Groups transcribed segments into speaker utterances
4. **Sentiment Analyzer** - Multi-label sentiment analysis using OpenRouter API
5. **Event Emitter** - Broadcasts analysis results via WebSocket and file output
6. **Performance Dashboard** - System performance monitoring

### Data Flow
```
Audio Input → Transcription → Utterance Segmentation → Sentiment Analysis → Event Emission → Dashboard
```

## Interface Specifications

### 1. AnalysisEvent Interface
The primary data structure used for communication:

```json
{
  "timestamp": "2025-07-25T13:04:14.934913Z",
  "speaker": "SPEAKER_00",
  "text": "Hello, how are you today?",
  "scores": {
    "Happy": 0.8,
    "Joyful": 0.6,
    "Content": 0.7,
    "Sad": 0.1,
    "Angry": 0.0,
    // ... 25+ other emotion scores (0.0 to 1.0)
  },
  "duration": 3.008037,
  "confidence": 0.8,
  "performance_metrics": {
    "total_events": 54,
    "average_latency": 1268.2367727160454,
    "components": {
      "pipeline": { "average_time": 1361.596441268921 },
      "sentiment": { "average_time": 2549.989700317383 },
      "transcription": { "average_time": 1158.6723029613495 }
    }
  }
}
```

### 2. WebSocket Interface
- **Endpoint**: `ws://localhost:8765` (configurable)
- **Protocol**: JSON messages containing AnalysisEvent objects
- **Connection Handling**: Automatic reconnection, client history synchronization

### 3. REST API Interface
- **Performance Metrics**: `/api/metrics` - Real-time system performance data
- **Speaker Statistics**: `/api/speakers` - Aggregated speaker sentiment data

## Dashboard Design Specification

### Visual Layout

#### Header Section
- **Title**: "Real-time Conversation Sentiment Dashboard"
- **Connection Status**: WebSocket connection indicator (Connected/Disconnected)
- **System Status**: Overall system health and performance metrics
- **Controls**: Start/Stop recording, Clear history, Export data

#### Main Dashboard Area
- **Speaker Avatars Panel**: Grid or horizontal layout of speaker avatars
- **Conversation Timeline**: Scrollable timeline of utterances with sentiment indicators
- **Real-time Analytics**: Live sentiment distribution charts and statistics

#### Footer Section
- **System Performance**: CPU/memory usage, processing latency
- **Event Statistics**: Total events processed, speakers detected

### Speaker Avatar Design

#### Avatar Components
1. **Base Avatar**: Circular or rounded rectangular avatar container
2. **Facial Features**:
   - Eyes: Size, shape, and position based on emotional intensity
   - Mouth: Shape and curvature indicating emotional state
   - Eyebrows: Position and angle reflecting sentiment
   - Overall face expression: Dynamic based on dominant emotions

#### Emotional Expression Mapping

**Positive Emotions** (Happy, Joyful, Content, Enthusiastic):
- Eyes: Larger, brighter, slightly upturned
- Mouth: Smiling, curved upward
- Eyebrows: Relaxed or slightly raised
- Overall: Bright, open facial expression

**Negative Emotions** (Sad, Angry, Frustrated, Disappointed):
- Eyes: Smaller, downturned, or squinted
- Mouth: Frowning, downturned, or tight
- Eyebrows: Furrowed or downturned
- Overall: Closed, tense facial expression

**Complex Emotions** (Confused, Surprised, Curious):
- Eyes: Wide open, raised eyebrows
- Mouth: Open/O-shaped for surprise, neutral for confusion
- Overall: Alert, questioning expression

**Neutral State**:
- Balanced facial features
- Relaxed expression
- Subtle animation for liveliness

#### Animation Specifications
- **Transition Duration**: 300ms smooth transitions between expressions
- **Blinking**: Natural blinking animation every 3-8 seconds
- **Micro-expressions**: Subtle facial movements for realism
- **Dominant Emotion Highlight**: Primary emotion displayed prominently
- **Emotion Intensity**: Facial feature exaggeration based on score magnitude (0.0-1.0)

### Color Coding System
- **Positive Emotions**: Warm colors (yellows, oranges, greens)
- **Negative Emotions**: Cool colors (blues, purples, reds)
- **Neutral Emotions**: Grays and muted tones
- **Complex Emotions**: Mixed or unique color combinations

## Technical Implementation

### Frontend Architecture
- **Framework**: Vanilla JavaScript with modern ES6+ features
- **Real-time Updates**: WebSocket connection for live data streaming
- **State Management**: Centralized state for speaker data and sentiment history
- **Animation Engine**: CSS transitions and JavaScript for smooth facial animations
- **Responsive Design**: Adapts to different screen sizes and orientations

### Backend Integration Points

#### 1. WebSocket Client
```javascript
const ws = new WebSocket('ws://localhost:8765');
ws.onmessage = function(event) {
    const analysisEvent = JSON.parse(event.data);
    updateSpeakerAvatar(analysisEvent);
};
```

#### 2. Data Processing Pipeline
- **Event Reception**: Real-time AnalysisEvent processing
- **Speaker Tracking**: Maintain speaker registry with avatar states
- **Sentiment Aggregation**: Calculate rolling averages and trends
- **Expression Mapping**: Convert sentiment scores to facial parameters

#### 3. Avatar State Management
```javascript
class SpeakerAvatar {
    constructor(speakerId) {
        this.speakerId = speakerId;
        this.currentExpression = 'neutral';
        this.sentimentHistory = [];
        this.domElement = this.createAvatarElement();
    }
    
    updateExpression(sentimentScores) {
        const dominantEmotion = this.getDominantEmotion(sentimentScores);
        const intensity = this.calculateIntensity(sentimentScores);
        this.animateToExpression(dominantEmotion, intensity);
    }
}
```

### Performance Considerations
- **Frame Rate**: Maintain 60fps for smooth animations
- **Memory Management**: Efficient DOM updates and garbage collection
- **Network Resilience**: Graceful handling of connection interruptions
- **Scalability**: Support for 2-10 simultaneous speakers

## User Experience Features

### Real-time Interaction
- **Live Updates**: Immediate avatar expression changes as speech is analyzed
- **Hover Information**: Detailed sentiment breakdown on avatar hover
- **Click Actions**: Speaker-specific analytics and history views

### Historical Data Visualization
- **Sentiment Timeline**: Graph showing emotional trends over time
- **Speaker Comparison**: Side-by-side sentiment analysis
- **Key Moments**: Highlight significant emotional shifts in conversation

### Customization Options
- **Avatar Appearance**: Different avatar styles and themes
- **Display Layout**: Grid, horizontal, or vertical speaker arrangements
- **Emotion Filters**: Focus on specific emotion categories
- **Sensitivity Settings**: Adjust emotion detection thresholds

## Integration Requirements

### System Dependencies
- **WebSocket Server**: Running speech analysis system with WebSocket endpoint
- **Web Browser**: Modern browser supporting ES6, WebSocket, and CSS3
- **Network Connectivity**: Stable connection to localhost WebSocket server

### Configuration Options
- **WebSocket Port**: Configurable port for connection (default: 8765)
- **Update Frequency**: Avatar refresh rate (default: real-time)
- **History Length**: Number of events to maintain (default: 1000)
- **Animation Speed**: Facial expression transition timing

### Error Handling
- **Connection Loss**: Graceful degradation with cached data display
- **Data Corruption**: Validation and fallback to default expressions
- **Performance Issues**: Automatic quality reduction under load
- **Speaker Identification**: Handling of new/unknown speakers

## Future Enhancements
- **Voice Visualization**: Audio waveform integration with avatar
- **Multi-language Support**: Internationalization of interface
- **Export Capabilities**: Data export in various formats
- **Advanced Analytics**: Machine learning-based conversation insights
- **Mobile Support**: Touch-optimized interface for mobile devices

## Development Roadmap

### Phase 1: Core Dashboard (MVP)
- Basic avatar display with static expressions
- WebSocket integration and real-time updates
- Simple sentiment-to-expression mapping
- Basic UI layout and styling

### Phase 2: Advanced Animations
- Smooth facial expression transitions
- Micro-expression animations
- Performance optimization
- Responsive design implementation

### Phase 3: Enhanced Features
- Historical data visualization
- Advanced analytics and statistics
- Customization options
- Export and sharing capabilities

### Phase 4: Production Ready
- Comprehensive testing and optimization
- Documentation and user guides
- Performance monitoring
- Accessibility compliance

## Testing Requirements
- **Unit Tests**: Avatar state management and expression mapping
- **Integration Tests**: WebSocket communication and data flow
- **Performance Tests**: Animation smoothness and update frequency
- **Cross-browser Tests**: Compatibility across major browsers
- **Load Tests**: Multiple simultaneous speakers and high event rates

## Deployment Considerations
- **Static Hosting**: Dashboard can be served as static files
- **Security**: No sensitive data exposure, localhost-only connections
- **Maintenance**: Minimal ongoing maintenance requirements
- **Updates**: Hot-reloading of dashboard without system restart