# Conversation Dashboard Implementation Plan

## System Integration Architecture

### WebSocket Communication Layer
The dashboard will integrate with the existing speech analysis system through WebSocket communication:

```javascript
// WebSocket client implementation
class SpeechAnalysisWebSocket {
    constructor(url = 'ws://localhost:8765') {
        this.url = url;
        this.ws = null;
        this.callbacks = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('Connected to speech analysis server');
            this.reconnectAttempts = 0;
            this.emit('connected');
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            this.emit('disconnected');
            this.attemptReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.emit('error', error);
        };
    }
    
    handleMessage(data) {
        if (data.type === 'initial') {
            // Handle initial data sync
            data.data.forEach(event => this.processAnalysisEvent(event));
        } else if (data.type === 'timeline') {
            // Handle real-time updates
            this.processAnalysisEvent(data.data);
        }
    }
    
    processAnalysisEvent(event) {
        // Validate event structure
        if (!event.speaker || !event.scores) {
            console.warn('Invalid analysis event received:', event);
            return;
        }
        
        this.emit('analysisEvent', event);
    }
    
    on(eventType, callback) {
        if (!this.callbacks.has(eventType)) {
            this.callbacks.set(eventType, []);
        }
        this.callbacks.get(eventType).push(callback);
    }
    
    emit(eventType, data) {
        const callbacks = this.callbacks.get(eventType);
        if (callbacks) {
            callbacks.forEach(callback => callback(data));
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, Math.pow(2, this.reconnectAttempts) * 1000); // Exponential backoff
        }
    }
}
```

### Data Processing Pipeline

#### 1. Speaker Registry Management
```javascript
class SpeakerRegistry {
    constructor() {
        this.speakers = new Map();
        this.avatarManager = new AvatarManager();
    }
    
    registerSpeaker(speakerId, name = null) {
        if (!this.speakers.has(speakerId)) {
            const speaker = {
                id: speakerId,
                name: name || speakerId,
                avatar: this.avatarManager.createAvatar(speakerId),
                sentimentHistory: [],
                lastUpdate: Date.now()
            };
            this.speakers.set(speakerId, speaker);
            this.emit('speakerRegistered', speaker);
        }
        return this.speakers.get(speakerId);
    }
    
    updateSpeakerSentiment(speakerId, sentimentScores, text, timestamp) {
        const speaker = this.speakers.get(speakerId);
        if (!speaker) {
            this.registerSpeaker(speakerId);
            return this.updateSpeakerSentiment(speakerId, sentimentScores, text, timestamp);
        }
        
        // Update sentiment history
        speaker.sentimentHistory.push({
            scores: { ...sentimentScores },
            text,
            timestamp,
            dominantEmotion: this.getDominantEmotion(sentimentScores)
        });
        
        // Keep only last 100 events
        if (speaker.sentimentHistory.length > 100) {
            speaker.sentimentHistory.shift();
        }
        
        // Update avatar expression
        speaker.avatar.updateExpression(sentimentScores);
        speaker.lastUpdate = Date.now();
        
        this.emit('speakerUpdated', speaker);
    }
    
    getDominantEmotion(scores) {
        return Object.entries(scores)
            .filter(([emotion, score]) => score > 0.1)
            .sort((a, b) => b[1] - a[1])[0]?.[0] || 'neutral';
    }
}
```

#### 2. Sentiment-to-Expression Mapping
```javascript
class ExpressionMapper {
    constructor() {
        this.emotionCategories = {
            positive: ['Happy', 'Joyful', 'Content', 'Enthusiastic', 'Helpful', 'Kind', 'Compassionate', 'Polite', 'Grateful', 'Sweet', 'Wholesome'],
            negative: ['Sad', 'Angry', 'Frustrated', 'Disappointed', 'Anxious', 'Rude', 'Ungrateful', 'Cruel', 'Hostile', 'Sleazy', 'Insulting', 'Threatening'],
            complex: ['Mischievous', 'Curious', 'Confused', 'Surprised', 'Sarcastic', 'Ironic', 'Teasing']
        };
    }
    
    mapToExpression(sentimentScores) {
        const dominantEmotion = this.getDominantEmotion(sentimentScores);
        const intensity = this.calculateIntensity(sentimentScores);
        const category = this.getEmotionCategory(dominantEmotion);
        
        return {
            emotion: dominantEmotion,
            category,
            intensity,
            facialParameters: this.calculateFacialParameters(sentimentScores, dominantEmotion, intensity)
        };
    }
    
    calculateFacialParameters(scores, dominantEmotion, intensity) {
        // Map emotion to facial feature parameters
        const parameters = {
            eyeSize: 1.0,
            eyePosition: 0,
            mouthShape: 'neutral',
            mouthCurvature: 0,
            eyebrowPosition: 0,
            eyebrowAngle: 0
        };
        
        // Adjust parameters based on emotion category and intensity
        switch (this.getEmotionCategory(dominantEmotion)) {
            case 'positive':
                parameters.eyeSize = 1.2 + (intensity * 0.3);
                parameters.eyePosition = intensity * 2;
                parameters.mouthShape = 'smile';
                parameters.mouthCurvature = intensity * 30;
                parameters.eyebrowPosition = intensity * 3;
                break;
                
            case 'negative':
                parameters.eyeSize = 0.8 - (intensity * 0.2);
                parameters.eyePosition = -intensity * 2;
                parameters.mouthShape = 'frown';
                parameters.mouthCurvature = -intensity * 25;
                parameters.eyebrowPosition = -intensity * 4;
                parameters.eyebrowAngle = -intensity * 15;
                break;
                
            case 'complex':
                parameters.eyeSize = 1.3 + (intensity * 0.4);
                parameters.eyebrowPosition = intensity * 5;
                parameters.mouthShape = 'open';
                parameters.mouthCurvature = intensity * 10;
                break;
        }
        
        return parameters;
    }
    
    getDominantEmotion(scores) {
        return Object.entries(scores)
            .filter(([emotion, score]) => score > 0.1)
            .sort((a, b) => b[1] - a[1])[0]?.[0] || 'neutral';
    }
    
    calculateIntensity(scores) {
        const dominantScore = Math.max(...Object.values(scores));
        return Math.min(dominantScore, 1.0);
    }
    
    getEmotionCategory(emotion) {
        for (const [category, emotions] of Object.entries(this.emotionCategories)) {
            if (emotions.includes(emotion)) {
                return category;
            }
        }
        return 'neutral';
    }
}
```

## Avatar Implementation

### Core Avatar Class
```javascript
class SpeakerAvatar {
    constructor(speakerId, containerElement) {
        this.speakerId = speakerId;
        this.container = containerElement;
        this.currentExpression = 'neutral';
        this.targetExpression = 'neutral';
        this.expressionIntensity = 0;
        this.isAnimating = false;
        
        this.expressionMapper = new ExpressionMapper();
        this.domElement = this.createAvatarElement();
        this.container.appendChild(this.domElement);
        
        this.initializeFacialFeatures();
        this.startBlinkingAnimation();
    }
    
    createAvatarElement() {
        const avatar = document.createElement('div');
        avatar.className = 'speaker-avatar';
        avatar.innerHTML = `
            <div class="avatar-header">
                <span class="speaker-id">${this.speakerId}</span>
                <span class="speaker-name"></span>
            </div>
            <div class="avatar-face">
                <div class="avatar-eyes">
                    <div class="eye left-eye"></div>
                    <div class="eye right-eye"></div>
                </div>
                <div class="avatar-mouth"></div>
                <div class="avatar-eyebrows">
                    <div class="eyebrow left-eyebrow"></div>
                    <div class="eyebrow right-eyebrow"></div>
                </div>
            </div>
            <div class="avatar-sentiment-info"></div>
        `;
        return avatar;
    }
    
    updateExpression(sentimentScores) {
        const expressionData = this.expressionMapper.mapToExpression(sentimentScores);
        this.targetExpression = expressionData.emotion;
        this.expressionIntensity = expressionData.intensity;
        
        this.updateFacialFeatures(expressionData.facialParameters);
        this.updateSentimentInfo(sentimentScores);
        this.updateAvatarColors(expressionData.category);
    }
    
    updateFacialFeatures(parameters) {
        const leftEye = this.domElement.querySelector('.left-eye');
        const rightEye = this.domElement.querySelector('.right-eye');
        const mouth = this.domElement.querySelector('.avatar-mouth');
        const leftEyebrow = this.domElement.querySelector('.left-eyebrow');
        const rightEyebrow = this.domElement.querySelector('.right-eyebrow');
        
        // Apply CSS transforms for smooth animations
        const transitionStyle = 'all 0.3s ease-in-out';
        
        leftEye.style.cssText = `
            transform: scale(${parameters.eyeSize}) translateY(${parameters.eyePosition}px);
            transition: ${transitionStyle};
        `;
        
        rightEye.style.cssText = `
            transform: scale(${parameters.eyeSize}) translateY(${parameters.eyePosition}px);
            transition: ${transitionStyle};
        `;
        
        mouth.style.cssText = `
            border-radius: 50%;
            transition: ${transitionStyle};
        `;
        
        // Set mouth shape based on emotion
        switch (parameters.mouthShape) {
            case 'smile':
                mouth.style.border = '2px solid';
                mouth.style.borderTopColor = 'transparent';
                mouth.style.borderLeftColor = 'transparent';
                mouth.style.borderRightColor = 'transparent';
                mouth.style.transform = `rotate(0deg) translateY(-5px)`;
                break;
            case 'frown':
                mouth.style.border = '2px solid';
                mouth.style.borderBottomColor = 'transparent';
                mouth.style.borderLeftColor = 'transparent';
                mouth.style.borderRightColor = 'transparent';
                mouth.style.transform = `rotate(180deg) translateY(5px)`;
                break;
            case 'open':
                mouth.style.border = '2px solid';
                mouth.style.borderRadius = '50%';
                mouth.style.width = '15px';
                mouth.style.height = '15px';
                break;
            default:
                mouth.style.border = '2px solid';
                mouth.style.borderTopColor = 'transparent';
                mouth.style.borderLeftColor = 'transparent';
                mouth.style.borderRightColor = 'transparent';
                mouth.style.borderBottomColor = 'currentColor';
                mouth.style.transform = 'none';
        }
        
        leftEyebrow.style.cssText = `
            transform: translateY(${parameters.eyebrowPosition}px) rotate(${parameters.eyebrowAngle}deg);
            transition: ${transitionStyle};
        `;
        
        rightEyebrow.style.cssText = `
            transform: translateY(${parameters.eyebrowPosition}px) rotate(${-parameters.eyebrowAngle}deg);
            transition: ${transitionStyle};
        `;
    }
    
    updateSentimentInfo(scores) {
        const infoElement = this.domElement.querySelector('.avatar-sentiment-info');
        const topEmotions = Object.entries(scores)
            .filter(([emotion, score]) => score > 0.1)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3);
        
        const emotionElements = topEmotions.map(([emotion, score]) => 
            `<div class="emotion-item">${emotion}: ${(score * 100).toFixed(0)}%</div>`
        ).join('');
        
        infoElement.innerHTML = emotionElements;
    }
    
    updateAvatarColors(category) {
        const faceElement = this.domElement.querySelector('.avatar-face');
        faceElement.className = `avatar-face emotion-${category}`;
    }
    
    startBlinkingAnimation() {
        setInterval(() => {
            if (Math.random() < 0.3) { // 30% chance to blink
                this.blink();
            }
        }, 5000); // Average blink every 5 seconds
    }
    
    blink() {
        const eyes = this.domElement.querySelectorAll('.eye');
        eyes.forEach(eye => {
            eye.style.height = '2px';
            eye.style.transition = 'height 0.1s';
        });
        
        setTimeout(() => {
            eyes.forEach(eye => {
                eye.style.height = '8px';
            });
        }, 100);
    }
}
```

## Dashboard Main Application

### Application Bootstrap
```javascript
class ConversationDashboard {
    constructor() {
        this.websocket = new SpeechAnalysisWebSocket();
        this.speakerRegistry = new SpeakerRegistry();
        this.expressionMapper = new ExpressionMapper();
        
        this.initializeUI();
        this.setupEventListeners();
        this.connectToServer();
    }
    
    initializeUI() {
        // Create main dashboard structure
        document.body.innerHTML = `
            <div class="dashboard-container">
                <header class="dashboard-header">
                    <h1>Real-time Conversation Sentiment Dashboard</h1>
                    <div class="status-indicators">
                        <span id="connection-status" class="status disconnected">🔴 Disconnected</span>
                        <span id="system-status" class="status">📊 System: --ms latency</span>
                        <div class="dashboard-controls">
                            <button id="clear-history">Clear History</button>
                            <button id="export-data">Export Data</button>
                        </div>
                    </div>
                </header>
                
                <main class="dashboard-main">
                    <div id="speakers-container" class="speakers-grid"></div>
                    <div id="timeline-container" class="conversation-timeline">
                        <h2>Conversation Timeline</h2>
                        <div id="timeline-content"></div>
                    </div>
                    <div id="analytics-container" class="realtime-analytics">
                        <h2>Real-time Analytics</h2>
                        <div class="analytics-content"></div>
                    </div>
                </main>
                
                <footer class="dashboard-footer">
                    <div id="performance-metrics"></div>
                    <div id="event-statistics"></div>
                </footer>
            </div>
        `;
        
        this.speakersContainer = document.getElementById('speakers-container');
        this.timelineContent = document.getElementById('timeline-content');
        this.analyticsContent = document.querySelector('.analytics-content');
    }
    
    setupEventListeners() {
        this.websocket.on('connected', () => {
            document.getElementById('connection-status').className = 'status connected';
            document.getElementById('connection-status').textContent = '🟢 Connected';
        });
        
        this.websocket.on('disconnected', () => {
            document.getElementById('connection-status').className = 'status disconnected';
            document.getElementById('connection-status').textContent = '🔴 Disconnected';
        });
        
        this.websocket.on('analysisEvent', (event) => {
            this.handleAnalysisEvent(event);
        });
        
        document.getElementById('clear-history').addEventListener('click', () => {
            this.clearHistory();
        });
        
        document.getElementById('export-data').addEventListener('click', () => {
            this.exportData();
        });
    }
    
    connectToServer() {
        this.websocket.connect();
    }
    
    handleAnalysisEvent(event) {
        // Register/update speaker
        const speaker = this.speakerRegistry.registerSpeaker(event.speaker);
        
        // Update speaker avatar
        this.speakerRegistry.update