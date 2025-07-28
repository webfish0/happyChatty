# Conversation Sentiment Dashboard

## Overview
This is a real-time conversation sentiment dashboard that visualizes speaker emotions through animated facial expressions. The dashboard connects to the speech analysis system via WebSocket and displays live sentiment analysis results.

## Features
- **Real-time Speaker Avatars**: Animated facial expressions that change based on sentiment analysis
- **Conversation Timeline**: Scrollable history of utterances with emotion indicators
- **Live Analytics**: Real-time statistics and sentiment distribution
- **Responsive Design**: Works on desktop and mobile devices
- **Export Functionality**: Export conversation data in JSON format

## System Integration

### Prerequisites
1. The speech analysis system must be running with WebSocket server enabled
2. WebSocket server should be accessible at `ws://localhost:8765`
3. Modern web browser (Chrome, Firefox, Safari, Edge)

### Starting the Speech Analysis System
Before using the dashboard, start the speech analysis system:

```bash
# Start the main speech analysis system
python main.py --host localhost --port 8765

# Optional: Start with performance dashboard
python main.py --host localhost --port 8765 --dashboard --dashboard-port 8080
```

### Running the Dashboard
The dashboard is a static web application that can be served in several ways:

#### Method 1: Python HTTP Server (Recommended for development)
```bash
# Navigate to the static directory
cd static

# Start HTTP server
python -m http.server 8000

# Open browser to http://localhost:8000
```

#### Method 2: Node.js HTTP Server
```bash
# Install http-server globally
npm install -g http-server

# Navigate to static directory
cd static

# Start server
http-server -p 8000

# Open browser to http://localhost:8000
```

#### Method 3: Using the existing performance dashboard
The speech analysis system already includes a web server. You can serve the dashboard files through it by copying them to the appropriate directory.

## Dashboard Components

### 1. Speaker Avatars
- Display animated facial expressions based on real-time sentiment analysis
- Show top 3 dominant emotions with percentage scores
- Automatic blinking and micro-expression animations
- Color-coded backgrounds based on emotion categories:
  - **Green**: Positive emotions (Happy, Joyful, Content, etc.)
  - **Red**: Negative emotions (Sad, Angry, Frustrated, etc.)
  - **Orange**: Complex emotions (Confused, Surprised, Curious, etc.)
  - **Gray**: Neutral state

### 2. Conversation Timeline
- Chronological display of all analyzed utterances
- Shows speaker ID, timestamp, and text
- Emotion indicators with dominant emotion and intensity
- Auto-scrolling with history limit (50 most recent events)

### 3. Real-time Analytics
- **Total Events**: Number of processed utterances
- **Active Speakers**: Number of detected speakers
- **Average Positivity**: Overall positive sentiment percentage
- **Processing Latency**: Current system processing time

### 4. Performance Monitoring
- **FPS Counter**: Animation frame rate
- **Memory Usage**: Browser memory consumption
- **Uptime Counter**: Dashboard running time

## WebSocket Communication

### Connection Details
- **Endpoint**: `ws://localhost:8765`
- **Protocol**: JSON messages
- **Reconnection**: Automatic with exponential backoff

### Message Format
The dashboard expects AnalysisEvent messages in this format:

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
    "Angry": 0.0
    // ... additional emotion scores
  },
  "duration": 3.008037,
  "confidence": 0.8,
  "performance_metrics": {
    "total_events": 54,
    "average_latency": 1268.2367727160454
  }
}
```

## Customization

### Configuration Options
The dashboard can be customized by modifying the JavaScript:

```javascript
// Change WebSocket URL
const websocket = new SpeechAnalysisWebSocket('ws://your-server:port');

// Adjust timeline history limit
this.maxTimelineEvents = 100; // default: 50

// Modify emotion categories in ExpressionMapper class
```

### CSS Customization
The dashboard uses CSS variables for easy theming:

```css
:root {
    --positive-color: #4caf50;    /* Positive emotions */
    --negative-color: #f44336;    /* Negative emotions */
    --complex-color: #ff9800;     /* Complex emotions */
    --neutral-color: #9e9e9e;     /* Neutral state */
    --primary-color: #2196f3;     /* Primary UI color */
}
```

## Troubleshooting

### Common Issues

1. **"Disconnected" Status**
   - Ensure the speech analysis system is running
   - Check WebSocket port configuration
   - Verify network connectivity

2. **No Speaker Avatars Displayed**
   - Wait for first utterance to be processed
   - Check console for JavaScript errors
   - Verify AnalysisEvent format

3. **Animations Not Smooth**
   - Check browser performance
   - Reduce number of simultaneous speakers
   - Close other resource-intensive applications

### Browser Console Debugging
Open browser developer tools (F12) to view:
- WebSocket connection status
- Error messages and warnings
- Performance metrics
- Debug logs

### Development Tools
```javascript
// Access dashboard instance globally for debugging
window.conversationDashboard

// View current speakers
window.conversationDashboard.speakers

// View timeline events
window.conversationDashboard.timelineEvents
```

## Architecture Overview

### Frontend Components
1. **ExpressionMapper**: Converts sentiment scores to facial parameters
2. **SpeakerAvatar**: Manages individual speaker avatar rendering
3. **SpeechAnalysisWebSocket**: Handles WebSocket communication
4. **ConversationDashboard**: Main application controller

### Data Flow
```
WebSocket Message → AnalysisEvent → SpeakerAvatar.updateExpression() → DOM Updates
```

### Performance Considerations
- Uses CSS transitions for smooth animations
- Efficient DOM updates with minimal reflows
- Automatic cleanup of old timeline events
- Memory-efficient sentiment history tracking

## Future Enhancements

### Planned Features
1. **Voice Waveform Visualization**: Audio visualization integrated with avatars
2. **Advanced Analytics**: Machine learning-based conversation insights
3. **Multi-language Support**: Internationalization of interface
4. **Mobile Optimization**: Touch-optimized interface for mobile devices
5. **Export Formats**: CSV, PDF, and image export options

### Contributing
1. Fork the repository
2. Create feature branch
3. Implement changes
4. Test thoroughly
5. Submit pull request

## License
This dashboard is part of the HappyChatty speech analysis system and is provided for educational and research purposes.