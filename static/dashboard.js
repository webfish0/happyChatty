// Conversation Dashboard JavaScript Implementation

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
        const parameters = {
            eyeSize: 1.0,
            eyePosition: 0,
            mouthShape: 'neutral',
            mouthCurvature: 0,
            eyebrowPosition: 0,
            eyebrowAngle: 0
        };
        
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
            <div class="avatar-face emotion-neutral">
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
    
    initializeFacialFeatures() {
        // Set initial facial feature styles
        const leftEye = this.domElement.querySelector('.left-eye');
        const rightEye = this.domElement.querySelector('.right-eye');
        const mouth = this.domElement.querySelector('.avatar-mouth');
        const leftEyebrow = this.domElement.querySelector('.left-eyebrow');
        const rightEyebrow = this.domElement.querySelector('.right-eyebrow');
        
        leftEye.style.cssText = 'width: 12px; height: 8px; background: #333; border-radius: 50%; transition: all 0.3s ease;';
        rightEye.style.cssText = 'width: 12px; height: 8px; background: #333; border-radius: 50%; transition: all 0.3s ease;';
        mouth.style.cssText = 'width: 30px; height: 15px; border: 2px solid #333; border-bottom-color: transparent; border-radius: 50%; transition: all 0.3s ease;';
        leftEyebrow.style.cssText = 'width: 20px; height: 3px; background: #333; border-radius: 2px; transition: all 0.3s ease;';
        rightEyebrow.style.cssText = 'width: 20px; height: 3px; background: #333; border-radius: 2px; transition: all 0.3s ease;';
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
        
        const transitionStyle = 'all 0.3s ease-in-out';
        
        leftEye.style.cssText = `
            width: 12px; height: 8px; background: #333; border-radius: 50%;
            transform: scale(${parameters.eyeSize}) translateY(${parameters.eyePosition}px);
            transition: ${transitionStyle};
        `;
        
        rightEye.style.cssText = `
            width: 12px; height: 8px; background: #333; border-radius: 50%;
            transform: scale(${parameters.eyeSize}) translateY(${parameters.eyePosition}px);
            transition: ${transitionStyle};
        `;
        
        mouth.style.cssText = `
            transition: ${transitionStyle};
        `;
        
        switch (parameters.mouthShape) {
            case 'smile':
                mouth.style.border = '2px solid #333';
                mouth.style.borderTopColor = 'transparent';
                mouth.style.borderLeftColor = 'transparent';
                mouth.style.borderRightColor = 'transparent';
                mouth.style.borderRadius = '50%';
                mouth.style.width = '30px';
                mouth.style.height = '15px';
                mouth.style.transform = `rotate(0deg) translateY(-5px)`;
                break;
            case 'frown':
                mouth.style.border = '2px solid #333';
                mouth.style.borderBottomColor = 'transparent';
                mouth.style.borderLeftColor = 'transparent';
                mouth.style.borderRightColor = 'transparent';
                mouth.style.borderRadius = '50%';
                mouth.style.width = '30px';
                mouth.style.height = '15px';
                mouth.style.transform = `rotate(180deg) translateY(5px)`;
                break;
            case 'open':
                mouth.style.border = '2px solid #333';
                mouth.style.borderRadius = '50%';
                mouth.style.width = '15px';
                mouth.style.height = '15px';
                mouth.style.transform = 'none';
                break;
            default:
                mouth.style.border = '2px solid #333';
                mouth.style.borderTopColor = 'transparent';
                mouth.style.borderLeftColor = 'transparent';
                mouth.style.borderRightColor = 'transparent';
                mouth.style.borderBottomColor = '#333';
                mouth.style.borderRadius = '50%';
                mouth.style.width = '30px';
                mouth.style.height = '15px';
                mouth.style.transform = 'none';
        }
        
        leftEyebrow.style.cssText = `
            width: 20px; height: 3px; background: #333; border-radius: 2px;
            transform: translateY(${parameters.eyebrowPosition}px) rotate(${parameters.eyebrowAngle}deg);
            transition: ${transitionStyle};
        `;
        
        rightEyebrow.style.cssText = `
            width: 20px; height: 3px; background: #333; border-radius: 2px;
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
            `<div class="emotion-item">
                <span>${emotion}</span>
                <span>${(score * 100).toFixed(0)}%</span>
            </div>`
        ).join('');
        
        infoElement.innerHTML = emotionElements || '<div class="emotion-item">No significant emotions detected</div>';
    }
    
    updateAvatarColors(category) {
        const faceElement = this.domElement.querySelector('.avatar-face');
        faceElement.className = `avatar-face emotion-${category}`;
    }
    
    startBlinkingAnimation() {
        setInterval(() => {
            if (Math.random() < 0.3) {
                this.blink();
            }
        }, 5000);
    }
    
    blink() {
        const eyes = this.domElement.querySelectorAll('.eye');
        eyes.forEach(eye => {
            eye.style.height = '2px';
        });
        
        setTimeout(() => {
            eyes.forEach(eye => {
                eye.style.height = '8px';
            });
        }, 100);
    }
    
    setName(name) {
        const nameElement = this.domElement.querySelector('.speaker-name');
        if (nameElement) {
            nameElement.textContent = name;
        }
    }
}

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
            document.getElementById('connection-status').className = 'status connected';
            document.getElementById('connection-status').textContent = '🟢 Connected';
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
            document.getElementById('connection-status').className = 'status disconnected';
            document.getElementById('connection-status').textContent = '🔴 Disconnected';
            this.emit('disconnected');
            this.attemptReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.emit('error', error);
        };
    }
    
    handleMessage(data) {
        // Handle both wrapped format (from performance dashboard) and raw AnalysisEvent format
        if (data.type === 'initial') {
            data.data.forEach(event => this.processAnalysisEvent(event));
        } else if (data.type === 'timeline') {
            this.processAnalysisEvent(data.data);
        } else {
            // Handle raw AnalysisEvent format directly from speech analysis system
            this.processAnalysisEvent(data);
        }
    }
    
    processAnalysisEvent(event) {
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
            }, Math.pow(2, this.reconnectAttempts) * 1000);
        }
    }
}

class ConversationDashboard {
    constructor() {
        this.websocket = new SpeechAnalysisWebSocket();
        this.speakers = new Map();
        this.timelineEvents = [];
        this.maxTimelineEvents = 50;
        this.startTime = Date.now();
        
        this.initializeUI();
        this.setupEventListeners();
        this.connectToServer();
        this.startPerformanceMonitoring();
    }
    
    initializeUI() {
        // Remove placeholder content
        const speakersContainer = document.getElementById('speakers-container');
        const timelineContent = document.getElementById('timeline-content');
        
        speakersContainer.innerHTML = '';
        timelineContent.innerHTML = '';
        
        // Add placeholder text
        const placeholder = document.createElement('div');
        placeholder.className = 'speaker-placeholder';
        placeholder.innerHTML = '<p>Waiting for conversation data...</p><p>Start the speech analysis system to begin monitoring.</p>';
        speakersContainer.appendChild(placeholder);
        
        const timelinePlaceholder = document.createElement('div');
        timelinePlaceholder.className = 'timeline-placeholder';
        timelinePlaceholder.innerHTML = '<p>No conversation data yet. Speak into the microphone to begin analysis.</p>';
        timelineContent.appendChild(timelinePlaceholder);
    }
    
    setupEventListeners() {
        this.websocket.on('connected', () => {
            console.log('WebSocket connected');
        });
        
        this.websocket.on('disconnected', () => {
            console.log('WebSocket disconnected');
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
        // Update speaker avatar
        this.updateSpeaker(event.speaker, event.scores, event.text, event.timestamp);
        
        // Add to timeline
        this.addToTimeline(event);
        
        // Update analytics
        this.updateAnalytics(event);
        
        // Update system status
        if (event.performance_metrics) {
            this.updateSystemStatus(event.performance_metrics);
        }
    }
    
    updateSpeaker(speakerId, sentimentScores, text, timestamp) {
        let speaker = this.speakers.get(speakerId);
        const speakersContainer = document.getElementById('speakers-container');
        
        // Remove placeholder if it exists
        const placeholder = speakersContainer.querySelector('.speaker-placeholder');
        if (placeholder) {
            speakersContainer.innerHTML = '';
        }
        
        if (!speaker) {
            // Create new speaker avatar
            speaker = {
                id: speakerId,
                avatar: new SpeakerAvatar(speakerId, speakersContainer),
                sentimentHistory: [],
                lastUpdate: Date.now()
            };
            this.speakers.set(speakerId, speaker);
            
            // Set speaker name if available
            if (speakerId.startsWith('SPEAKER_')) {
                speaker.avatar.setName(`Speaker ${speakerId.split('_')[1]}`);
            }
        }
        
        // Update avatar expression
        speaker.avatar.updateExpression(sentimentScores);
        
        // Update sentiment history
        speaker.sentimentHistory.push({
            scores: { ...sentimentScores },
            text,
            timestamp,
            dominantEmotion: this.getDominantEmotion(sentimentScores)
        });
        
        if (speaker.sentimentHistory.length > 100) {
            speaker.sentimentHistory.shift();
        }
        
        speaker.lastUpdate = Date.now();
    }
    
    addToTimeline(event) {
        const timelineContent = document.getElementById('timeline-content');
        const timelinePlaceholder = timelineContent.querySelector('.timeline-placeholder');
        
        if (timelinePlaceholder) {
            timelineContent.innerHTML = '';
        }
        
        // Create timeline item
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        
        const timestamp = new Date(event.timestamp).toLocaleTimeString();
        const dominantEmotion = this.getDominantEmotion(event.scores);
        const emotionCategory = this.getEmotionCategory(dominantEmotion);
        
        timelineItem.innerHTML = `
            <div class="timeline-item-header">
                <div class="timeline-speaker">${event.speaker}</div>
                <div class="timeline-timestamp">${timestamp}</div>
            </div>
            <div class="timeline-text">"${event.text}"</div>
            <div class="timeline-emotion ${emotionCategory}">${dominantEmotion} (${(event.scores[dominantEmotion] * 100).toFixed(0)}%)</div>
        `;
        
        timelineContent.insertBefore(timelineItem, timelineContent.firstChild);
        
        // Keep only last N events
        if (timelineContent.children.length > this.maxTimelineEvents) {
            timelineContent.removeChild(timelineContent.lastChild);
        }
        
        this.timelineEvents.unshift(event);
        if (this.timelineEvents.length > this.maxTimelineEvents) {
            this.timelineEvents.pop();
        }
    }
    
    updateAnalytics(event) {
        // Update event statistics
        document.getElementById('total-events').textContent = this.timelineEvents.length;
        document.getElementById('active-speakers').textContent = this.speakers.size;
        
        // Calculate average sentiment
        if (this.timelineEvents.length > 0) {
            const positiveEmotions = ['Happy', 'Joyful', 'Content', 'Enthusiastic', 'Helpful', 'Kind', 'Compassionate', 'Polite', 'Grateful', 'Sweet', 'Wholesome'];
            let totalPositivity = 0;
            let eventCount = 0;
            
            this.timelineEvents.slice(0, 20).forEach(event => {
                const positiveScore = positiveEmotions.reduce((sum, emotion) => sum + (event.scores[emotion] || 0), 0);
                totalPositivity += positiveScore / positiveEmotions.length;
                eventCount++;
            });
            
            const avgPositivity = eventCount > 0 ? (totalPositivity / eventCount) * 100 : 0;
            document.getElementById('avg-sentiment').textContent = `${Math.round(avgPositivity)}%`;
        }
        
        // Update speaker count
        document.getElementById('speaker-count').textContent = this.speakers.size;
    }
    
    updateSystemStatus(metrics) {
        if (metrics.average_latency) {
            document.getElementById('processing-latency').textContent = `${Math.round(metrics.average_latency)}ms`;
        }
        
        if (metrics.components) {
            const totalLatency = metrics.average_latency || 0;
            document.getElementById('system-status').textContent = `📊 System: ${Math.round(totalLatency)}ms latency`;
        }
    }
    
    getDominantEmotion(scores) {
        return Object.entries(scores)
            .filter(([emotion, score]) => score > 0.1)
            .sort((a, b) => b[1] - a[1])[0]?.[0] || 'neutral';
    }
    
    getEmotionCategory(emotion) {
        const expressionMapper = new ExpressionMapper();
        return expressionMapper.getEmotionCategory(emotion);
    }
    
    clearHistory() {
        // Clear timeline
        const timelineContent = document.getElementById('timeline-content');
        timelineContent.innerHTML = '<div class="timeline-placeholder"><p>Conversation history cleared.</p></div>';
        
        // Clear speaker sentiment history
        this.speakers.forEach(speaker => {
            speaker.sentimentHistory = [];
        });
        
        // Clear events array
        this.timelineEvents = [];
        
        // Reset analytics
        document.getElementById('total-events').textContent = '0';
        document.getElementById('avg-sentiment').textContent = '0%';
        
        console.log('History cleared');
    }
    
    exportData() {
        const exportData = {
            timestamp: new Date().toISOString(),
            events: this.timelineEvents,
            speakers: Array.from(this.speakers.values()).map(speaker => ({
                id: speaker.id,
                sentimentHistory: speaker.sentimentHistory
            }))
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `conversation-analysis-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
        
        console.log('Data exported');
    }
    
    startPerformanceMonitoring() {
        let frameCount = 0;
        let lastTime = performance.now();
        
        const updateFPS = () => {
            frameCount++;
            const currentTime = performance.now();
            const deltaTime = currentTime - lastTime;
            
            if (deltaTime >= 1000) {
                const fps = Math.round((frameCount * 1000) / deltaTime);
                document.getElementById('fps-counter').textContent = fps;
                frameCount = 0;
                lastTime = currentTime;
            }
            
            requestAnimationFrame(updateFPS);
        };
        
        updateFPS();
        
        // Update uptime counter
        setInterval(() => {
            const uptime = Math.floor((Date.now() - this.startTime) / 1000);
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            const seconds = uptime % 60;
            document.getElementById('uptime-counter').textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new ConversationDashboard();
    window.conversationDashboard = dashboard; // Make available globally for debugging
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Page became visible, reconnect if needed
        if (window.conversationDashboard && 
            document.getElementById('connection-status').className.includes('disconnected')) {
            window.conversationDashboard.connectToServer();
        }
    }
});