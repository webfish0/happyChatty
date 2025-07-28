# Audio Capture Dependency Fix for macOS

## Problem
The original audio capture implementation was experiencing FFI (Foreign Function Interface) callback memory allocation errors on macOS:
```
Cannot allocate write+execute memory for ffi.callback()
```

This error occurs because macOS security restrictions prevent the allocation of memory that is both writable and executable, which is required by some FFI callback implementations.

## Solution
The audio capture system has been rewritten to use a polling-based approach instead of callback-based streaming. This avoids the FFI callback memory allocation issues while maintaining full functionality.

## Key Changes

### 1. Audio Capture Implementation (`audio_capture.py`)
- **Before**: Used `sounddevice.InputStream` with callback function
- **After**: Uses `sounddevice.InputStream` with manual polling via `stream.read()`
- **Benefits**: 
  - Eliminates FFI callback memory allocation issues
  - Maintains cross-platform compatibility
  - Preserves all existing functionality

### 2. Technical Approach
The new implementation:
1. Opens audio stream without callbacks
2. Uses a separate thread for audio capture
3. Polls audio data in chunks using `stream.read()`
4. Processes audio data and sends to queue for async consumption
5. Properly handles stream cleanup and error recovery

## Testing
The fix has been thoroughly tested and verified to work correctly:

1. **Audio Capture Test**: `python test_audio_capture.py`
   - Successfully captures audio from input devices
   - No FFI callback errors
   - Proper audio level calculation
   - Clean stream management

2. **Dashboard Integration Test**: 
   - WebSocket communication working
   - Real-time facial expression updates
   - Conversation timeline display
   - Analytics and performance metrics

## Usage
The system works exactly as before, but now without the macOS compatibility issues:

```bash
# Start the full system
python main.py --dashboard

# List available audio devices
python main.py --list-devices

# Start with specific device
python main.py --device 1
```

## Dependencies
- `sounddevice==0.5.2` (no changes needed)
- `numpy==1.24.3` (no changes needed)
- Removed problematic PyAudio dependency

## Troubleshooting
If you encounter any audio-related issues:

1. **Check audio permissions**: Ensure the terminal/app has microphone access
2. **Verify audio devices**: Run `python main.py --list-devices`
3. **Test audio capture**: Run `python test_audio_capture.py`

## Performance
The polling approach has minimal performance impact:
- CPU usage remains low
- Audio latency is unchanged
- Real-time processing maintained
- Memory usage stable

## Compatibility
- ✅ macOS (tested on Sequoia)
- ✅ Windows (backward compatible)
- ✅ Linux (backward compatible)

The fix ensures the conversation sentiment analysis dashboard works reliably across all platforms.