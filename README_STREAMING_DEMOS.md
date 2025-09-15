# 🎭 Ditto Online Streaming Demos

This directory contains demonstration scripts for using the **online streaming pipeline** (`stream_pipeline_online.py`) for real-time talking head generation.

## 📂 Demo Scripts

### 1. `simple_streaming_example.py` - Basic Usage
**Purpose**: Minimal example showing basic online streaming setup
```bash
python simple_streaming_example.py
```
- ✅ Easy to understand
- ✅ Shows essential streaming concepts
- ✅ Good starting point for beginners

### 2. `demo_online_streaming.py` - Advanced Demo
**Purpose**: Comprehensive real-time streaming demonstration with detailed logging
```bash
python demo_online_streaming.py \
    --data_root "./checkpoints/ditto_trt_Ampere_Plus" \
    --cfg_pkl "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt_online.pkl" \
    --audio_path "./data/audio/relativity.wav" \
    --source_path "./data/image/einstein_portrait.jpg" \
    --output_path "./output/streaming_demo.mp4" \
    --chunk_duration 0.5 \
    --simulate_realtime
```

**Features**:
- 🎵 Configurable chunk duration
- ⏱️ Real-time simulation mode
- 📊 Detailed progress tracking
- 🔧 Adjustable quality settings

### 3. `compare_online_offline.py` - Pipeline Comparison
**Purpose**: Side-by-side comparison of online vs offline pipelines
```bash
python compare_online_offline.py
```
- 📊 Performance benchmarking
- 🔄 Quality comparison
- 💡 Usage recommendations

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure you have the required checkpoints
ls checkpoints/ditto_trt_Ampere_Plus/
ls checkpoints/ditto_cfg/v0.4_hubert_cfg_trt_online.pkl

# Create output directory
mkdir -p output
```

### Run Simple Demo
```bash
python simple_streaming_example.py
```

### Run Advanced Demo with Real-time Simulation
```bash
python demo_online_streaming.py \
    --data_root "./checkpoints/ditto_trt_Ampere_Plus" \
    --cfg_pkl "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt_online.pkl" \
    --audio_path "./data/audio/relativity.wav" \
    --source_path "./data/image/einstein_portrait.jpg" \
    --output_path "./output/realtime_demo.mp4" \
    --simulate_realtime \
    --chunk_duration 0.3
```

## ⚙️ Configuration Options

### Model Formats (in order of streaming performance):
1. **TensorRT** (fastest): `ditto_trt_Ampere_Plus` + `v0.4_hubert_cfg_trt_online.pkl`
2. **ONNX** (balanced): `ditto_onnx` + `v0.4_hubert_cfg_trt_online.pkl`  
3. **PyTorch** (compatible): `ditto_pytorch` + `v0.4_hubert_cfg_pytorch.pkl`

### Streaming Parameters:
- `--chunk_duration`: Audio chunk size (0.2-1.0s, smaller = lower latency)
- `--sampling_timesteps`: Quality vs speed (10-50, lower = faster)
- `--simulate_realtime`: Add delays to simulate real-time constraints

## 📈 Performance Tuning

### For Low Latency (Real-time Applications):
```python
streaming_kwargs = {
    "online_mode": True,
    "sampling_timesteps": 15,    # Fast inference
    "overlap_v2": 6,             # Minimal overlap
    "chunk_duration": 0.2        # Small chunks
}
```

### For High Quality (Near Real-time):
```python
streaming_kwargs = {
    "online_mode": True,
    "sampling_timesteps": 35,    # Higher quality
    "overlap_v2": 12,            # More overlap
    "chunk_duration": 0.8        # Larger chunks
}
```

## 🎯 Use Cases

| **Application** | **Script** | **Settings** | **Expected Latency** |
|----------------|------------|-------------|---------------------|
| **Live Video Calls** | `demo_online_streaming.py` | `chunk_duration=0.2, sampling_timesteps=15` | ~200-400ms |
| **Interactive Avatars** | `simple_streaming_example.py` | `sampling_timesteps=20` | ~300-500ms |
| **Live Streaming** | `demo_online_streaming.py` | `chunk_duration=0.5, sampling_timesteps=25` | ~500-800ms |
| **Near Real-time Content** | Any script | `sampling_timesteps=35` | ~1-2s |

## 🔧 Troubleshooting

### Common Issues:

1. **"CUDA out of memory"**
   ```bash
   # Reduce sampling steps
   --sampling_timesteps 10
   ```

2. **High latency**
   ```bash
   # Use smaller chunks and fewer steps
   --chunk_duration 0.2 --sampling_timesteps 15
   ```

3. **Poor quality**
   ```bash
   # Increase sampling steps and chunk size
   --sampling_timesteps 40 --chunk_duration 0.8
   ```

4. **Audio/video sync issues**
   - Ensure consistent frame rates
   - Check audio sample rate (should be 16kHz)
   - Verify chunk timing calculations

## 💡 Integration Examples

### WebRTC Integration
```python
# Pseudocode for integrating with WebRTC
class WebRTCAvatarStream:
    def __init__(self):
        self.sdk = StreamSDK(cfg, data_root)
        self.audio_buffer = []
        
    def on_audio_frame(self, audio_data):
        self.audio_buffer.extend(audio_data)
        if len(self.audio_buffer) >= chunk_size:
            chunk = self.audio_buffer[:chunk_size]
            self.audio_buffer = self.audio_buffer[chunk_size:]
            self.sdk.run_chunk(chunk, chunksize)
```

### WebSocket Streaming
```python
# Pseudocode for WebSocket streaming
async def handle_audio_stream(websocket):
    sdk = StreamSDK(cfg, data_root)
    async for audio_chunk in websocket:
        video_frame = sdk.run_chunk(audio_chunk, chunksize)
        await websocket.send(video_frame)
```

## 📚 Additional Resources

- **Main README**: `../README.md` - Overall project documentation
- **Configuration Guide**: Check `checkpoints/ditto_cfg/` for different config options
- **Performance Guide**: See model-specific documentation in `checkpoints/`

---

**Happy Streaming! 🎉**

For questions or issues, check the main repository documentation or create an issue.
