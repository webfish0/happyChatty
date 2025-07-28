# Conversation Dashboard Visual Mockup

## Dashboard Layout Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ REAL-TIME CONVERSATION SENTIMENT DASHBOARD                     ● ○ ─        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🟢 Connected to ws://localhost:8765    📊 System: 1268ms latency    ⏹ ⚙️ 📤 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │    SPEAKER_00   │    │    SPEAKER_01   │    │    SPEAKER_02   │         │
│  │   🎤 John       │    │   🎤 Sarah      │    │   🎤 Alex       │         │
│  │                 │    │                 │    │                 │         │
│  │    ████████     │    │    ████████     │    │    ████████     │         │
│  │   ██ 😊 ██      │    │   ██ 😟 ██      │    │   ██ 😊 ██      │         │
│  │  ██  👀  ██     │    │  ██  👀  ██     │    │  ██  👀  ██     │         │
│  │  ██   👄   ██   │    │  ██   👄   ██   │    │  ██   👄   ██   │         │
│  │   ██    ██      │    │   ██    ██      │    │   ██    ██      │         │
│  │    ████████     │    │    ████████     │    │    ████████     │         │
│  │                 │    │                 │    │                 │         │
│  │ Happy: 0.85     │    │ Sad: 0.72       │    │ Content: 0.68   │         │
│  │ Joyful: 0.63    │    │ Frustrated: 0.45│    │ Curious: 0.52   │         │
│  │ Enthusiastic: 0.41│   │ Anxious: 0.38   │    │ Helpful: 0.44   │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ CONVERSATION TIMELINE                                                       │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 🕐 12:03:45 John: "That sounds like a great idea!" 😊 Happy (0.85)       │ │
│ │ 🕐 12:03:42 Sarah: "I'm not sure about that..." 😟 Sad (0.72)            │ │
│ │ 🕐 12:03:38 Alex: "What do you think we should do?" 😊 Curious (0.52)    │ │
│ │ 🕐 12:03:35 John: "Let me explain my reasoning." 😊 Content (0.68)       │ │
│ │ 🕐 12:03:32 Sarah: "This is getting frustrating." 😟 Frustrated (0.65)   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ REAL-TIME SENTIMENT ANALYTICS                                               │
│ ┌─────────────────────────────┬───────────────────────────────────────────┐ │
│ │ SENTIMENT DISTRIBUTION      │ TOP EMOTIONS                              │ │
│ │                             │                                           │ │
│ │ 😊 Positive: 45%           │ 1. Happy (0.85) - John                    │ │
│ │ 😟 Negative: 30%           │ 2. Sad (0.72) - Sarah                     │ │
│ │ 😮 Complex: 15%            │ 3. Content (0.68) - Alex                  │ │
│ │ 😐 Neutral: 10%            │ 4. Curious (0.52) - Alex                  │ │
│ │                             │ 5. Frustrated (0.45) - Sarah              │ │
│ └─────────────────────────────┴───────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📈 Performance: 60fps    📊 Events: 1,247    👥 Speakers: 3    🕒 Uptime: 25m │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Avatar Expression Details

### Happy/Positive Expression (😊)
```
    ████████
   ██ 😊 ██
  ██  👀  ██    Eyes: Bright, slightly upturned
  ██   ∪   ██   Mouth: Smiling curve
   ██    ██
    ████████
```

### Sad/Negative Expression (😟)
```
    ████████
   ██ 😟 ██
  ██  👀  ██    Eyes: Slightly downturned
  ██   ∩   ██   Mouth: Frowning curve
   ██    ██
    ████████
```

### Surprised/Confused Expression (😮)
```
    ████████
   ██ 😮 ██
  ██  ⚬ ⚬  ██    Eyes: Wide open
  ██   O   ██   Mouth: Open/O-shaped
   ██    ██
    ████████
```

### Neutral Expression (😐)
```
    ████████
   ██ 😐 ██
  ██  👀  ██    Eyes: Neutral position
  ██   —   ██   Mouth: Straight line
   ██    ██
    ████████
```

## Color Coding Legend

- **😊 Positive Emotions**: Warm colors (yellow, orange, green backgrounds)
- **😟 Negative Emotions**: Cool colors (blue, purple, red backgrounds)  
- **😮 Complex Emotions**: Mixed colors (gradient backgrounds)
- **😐 Neutral State**: Gray/muted color backgrounds

## Interactive Elements

### Hover States
When hovering over an avatar:
```
┌─────────────────────────────────────────┐
│ SPEAKER_00 - John                      │
├─────────────────────────────────────────┤
│ Current Emotion: Happy (0.85)          │
│ Top 3 Emotions:                        │
│ • Happy: 0.85                          │
│ • Joyful: 0.63                         │
│ • Content: 0.41                        │
│                                        │
│ Duration: 2.3s    Confidence: 0.92     │
└─────────────────────────────────────────┘
```

### Click Actions
Clicking an avatar opens detailed analytics:
```
┌─────────────────────────────────────────┐
│ John - Sentiment History               │
├─────────────────────────────────────────┤
│ 📈 Emotional Trend (Last 5 minutes)    │
│ [Chart showing emotion fluctuations]   │
│                                        │
│ 📊 Statistics:                         │
│ • Average Positivity: 0.72             │
│ • Most Common Emotion: Happy           │
│ • Emotional Range: 0.65                │
│ • Utterances: 24                       │
│                                        │
│ 📋 Recent Utterances:                  │
│ "That sounds great!" (Happy: 0.85)     │
│ "I'm really excited!" (Joyful: 0.78)   │
│ "This is perfect." (Content: 0.65)     │
└─────────────────────────────────────────┘
```

## Responsive Design Variations

### Mobile Layout (Portrait)
```
┌─────────────────────────────────────────┐
│ CONVERSATION DASHBOARD                 │
├─────────────────────────────────────────┤
│ SPEAKER_00                              │
│ ┌─────────────────┐                    │
│ │    ████████     │                    │
│ │   ██ 😊 ██      │                    │
│ │  ██  👀  ██     │                    │
│ │  ██   ∪   ██    │                    │
│ │   ██    ██      │                    │
│ │    ████████     │                    │
│ └─────────────────┘                    │
│ Happy: 0.85  Joyful: 0.63              │
├─────────────────────────────────────────┤
│ SPEAKER_01                              │
│ ┌─────────────────┐                    │
│ │    ████████     │                    │
│ │   ██ 😟 ██      │                    │
│ │  ██  👀  ██     │                    │
│ │  ██   ∩   ██    │                    │
│ │   ██    ██      │                    │
│ │    ████████     │                    │
│ └─────────────────┘                    │
│ Sad: 0.72  Frustrated: 0.45            │
└─────────────────────────────────────────┘
```

### Compact Layout (Multiple Speakers)
```
┌─ SPEAKER_00 ─┐┌─ SPEAKER_01 ─┐┌─ SPEAKER_02 ─┐
│    😊       ││    😟       ││    😊       │
│ Happy: 0.85 ││ Sad: 0.72   ││Content: 0.68│
└─────────────┘└─────────────┘└─────────────┘
```

## Animation Transitions

### Expression Change Sequence
1. **Fade Out** (100ms): Current expression fades to 30% opacity
2. **Morph** (150ms): Facial features smoothly transition to new positions
3. **Fade In** (50ms): New expression fades to 100% opacity
4. **Highlight** (100ms): Brief glow effect on dominant emotion

### Micro-expressions
- **Blinking**: Eyes close and open every 3-8 seconds (100ms duration)
- **Breathing**: Subtle scale pulsing (±2%) synchronized with speech
- **Attention**: Head tilt slightly toward active speaker

## Status Indicators

### Connection States
- **🟢 Connected**: Real-time data streaming
- **🟡 Connecting**: Establishing WebSocket connection
- **🔴 Disconnected**: Connection lost, showing cached data

### System Health
- **📊 Performance**: Processing latency indicator
- **📈 FPS**: Animation frame rate monitor
- **💾 Memory**: Browser memory usage tracking

This mockup provides a comprehensive visual representation of the conversation dashboard, showing how speaker avatars with animated facial expressions will display real-time sentiment analysis results from the speech system.