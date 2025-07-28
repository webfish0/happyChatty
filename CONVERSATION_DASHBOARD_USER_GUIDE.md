# Conversation Sentiment Dashboard - User Guide

## Overview
The Conversation Sentiment Dashboard is a real-time visualization tool that displays speaker emotions through animated facial expressions. It integrates with the speech analysis system to provide live feedback on conversation sentiment.

## Quick Start

### Prerequisites
1. Python 3.7+
2. Required Python packages (install via `pip install -r requirements.txt`)
3. WebSocket server running on `localhost:8765`
4. Modern web browser (Chrome, Firefox, Safari, Edge)

### Starting the System

#### 1. Start the Speech Analysis System
```bash
# Basic startup
python main.py

# Start with conversation dashboard
python main.py --dashboard

# Start with custom ports
python main.py --host localhost --port 8765 --dashboard --dashboard-port 8080
```

#### 2. Access the Dashboard
Once the system is running:
- **Conversation Dashboard**: http://localhost:8080
- **Performance Dashboard**: http://localhost:8080/performance

## Dashboard Features

### Real-time Speaker Avatars
- **Animated Facial Expressions**: Avatars automatically update their facial expressions based on detected emotions
- **Emotion Categories**:
  - **Positive** (Green): Happy, Joyful, Content, Enthusiastic
  - **Negative** (Red): Sad, Angry, Frustrated, Disappointed
  - **Complex** (Orange): Confused, Surprised, Curious
  - **Neutral** (Gray): Balanced emotional state

### Conversation Timeline
- Chronological display of all analyzed utterances
- Shows speaker ID, timestamp, and transcribed text
- Emotion indicators with dominant emotion and intensity percentage
- Auto-scrolling with 50 most recent events

### Real-time Analytics
- **Total Events**: Number of processed utterances
- **Active Speakers**: Number of detected conversation participants
- **Average Positivity**: Overall positive sentiment percentage
- **Processing Latency**: Current system processing time

### Performance Monitoring
- **FPS Counter**: Animation frame rate (target: 60 FPS)
- **Uptime Counter**: Dashboard running time
- **System Status**: Connection and latency indicators

## Command Line Options

### Main Application Arguments
```bash
python main.py [OPTIONS]

Options:
  --host HOST                 WebSocket host (default: localhost)
  --port PORT                 WebSocket port (default: 8765)
  --output FILE               Output JSON file for analysis results
  --device INDEX              Audio device index
  --list-devices              List available audio input devices
  --config FILE               Configuration file path
  --dashboard                 Start conversation dashboard
  --dashboard-port PORT       Dashboard port (default: 8080)
  --performance-dashboard     Start performance monitoring dashboard
```

### Examples
```bash
# List available audio devices
python main.py --list-devices

# Start with specific audio device
python main.py --device 2

# Start with custom configuration
python main.py --config ./my_config.json

# Start with both dashboards
python main.py --dashboard --performance-dashboard
```

## Dashboard Controls

### Header Controls
- **Clear History**: Reset conversation timeline and statistics
- **Export Data**: Download conversation analysis as JSON file

### Avatar Interactions
- **Hover**: View detailed emotion breakdown for each speaker
- **Real-time Updates**: Avatars automatically animate based on speech analysis

## System Architecture

### Data Flow
```
Audio Input → Transcription Engine → Utterance Segmentation 
→ Sentiment Analysis → Event Emission → WebSocket → Dashboard
```

### WebSocket Communication
- **Endpoint**: `ws://localhost:8765`
- **Protocol**: JSON messages containing AnalysisEvent objects
- **Reconnection**: Automatic with exponential backoff

### AnalysisEvent Structure
```json
{
  "timestamp": "2025-07-25T13:04:14.934913Z",
  "speaker": "SPEAKER_00",
  "text": "Hello, how are you today?",
  "scores": {
    "Happy": 0.8,
    "Sad": 0.1,
    "Angry": 0.0
    // ... 28 total emotion scores (0.0 to 1.0)
  },
  "duration": 3.008037,
  "confidence": 0.8,
  "performance_metrics": {
    "total_events": 54,
    "average_latency": 1268.2367727160454
  }
}
```

## Troubleshooting

### Common Issues

#### "Disconnected" Status
1. **Verify System is Running**: Ensure `python main.py --dashboard` is active
2. **Check Port Configuration**: Confirm dashboard port (default: 8080)
3. **Network Connectivity**: Verify localhost access

#### No Speaker Avatars Displayed
1. **Wait for Speech**: Speak into microphone to trigger analysis
2. **Check Console**: Open browser developer tools (F12) for errors
3. **Verify WebSocket**: Ensure WebSocket connection is established

#### Performance Issues
1. **Browser Resources**: Close other applications to free memory
2. **Multiple Speakers**: System optimized for 2-10 simultaneous speakers
3. **Animation Quality**: Automatic quality adjustment under load

### Browser Console Debugging
Access developer tools (F12) to monitor:
- WebSocket connection status
- JavaScript errors and warnings
- Performance metrics and frame rates
- Network activity and latency

### Development Access
```javascript
// Global dashboard instance for debugging
window.conversationDashboard

// View current speakers and data
window.conversationDashboard.speakers
window.conversationDashboard.timelineEvents
```

## Customization

### CSS Theming
Modify colors and styles in `static/dashboard.css`:
```css
:root {
    --positive-color: #4caf50;    /* Positive emotions */
    --negative-color: #f44336;    /* Negative emotions */
    --complex-color: #ff9800;     /* Complex emotions */
    --neutral-color: #9e9e9e;     /* Neutral state */
}
```

### JavaScript Configuration
Adjust settings in `static/dashboard.js`:
```javascript
// WebSocket configuration
const websocket = new SpeechAnalysisWebSocket('ws://custom-server:port');

// Timeline history limit
this.maxTimelineEvents = 100; // default: 50
```

## Integration with Existing Systems

### Adding to Other Projects
1. Copy the `static/` directory to your project
2. Serve files via your preferred web server
3. Ensure WebSocket endpoint matches your analysis system
4. Customize CSS/JS as needed

### API Endpoints
The dashboard expects real-time AnalysisEvent messages via WebSocket. Ensure your system sends data in the correct format.

## Performance Specifications

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum
- **Browser**: Modern browser with ES6 support
- **Network**: Localhost WebSocket connection

### Optimization Features
- **Efficient DOM Updates**: Minimal reflows and repaints
- **Memory Management**: Automatic cleanup of old events
- **Frame Rate Monitoring**: Maintains 60 FPS target
- **Connection Resilience**: Automatic reconnection handling

## Future Enhancements

### Planned Features
1. **Voice Waveform Integration**: Audio visualization with avatars
2. **Advanced Analytics**: Machine learning conversation insights
3. **Multi-language Support**: Internationalized interface
4. **Mobile Optimization**: Touch-optimized responsive design
5. **Export Formats**: CSV, PDF, and image export options

## Support and Documentation

### Additional Resources
- **Technical Specification**: `CONVERSATION_DASHBOARD_SPECIFICATION.md`
- **Implementation Details**: `CONVERSATION_DASHBOARD_IMPLEMENTATION.md`
- **Visual Mockups**: `CONVERSATION_DASHBOARD_MOCKUP.md`

### Getting Help
1. **Check Console Logs**: Browser developer tools (F12)
2. **Review Documentation**: Markdown files in project root
3. **Verify Installation**: Ensure all dependencies are installed
4. **Test Connectivity**: Confirm WebSocket server is accessible

## License and Usage
This dashboard is part of the HappyChatty speech analysis system and is provided for educational and research purposes. See project LICENSE file for details.