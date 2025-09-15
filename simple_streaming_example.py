#!/usr/bin/env python3
"""
Simple example showing basic usage of stream_pipeline_online.py

This is a minimal example showing how to use the online streaming pipeline.
"""

import librosa
import numpy as np
import os

# Import online streaming pipeline
from stream_pipeline_online import StreamSDK


def simple_streaming_demo():
    """Simple demonstration of online streaming."""
    
    # Configuration
    data_root = "./checkpoints/ditto_trt_Ampere_Plus"
    cfg_pkl = "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt_online.pkl"
    audio_path = "./data/audio/relativity.wav"
    source_path = "./data/image/einstein_portrait.jpg"
    output_path = "./output/simple_streaming_demo.mp4"
    
    print("🎭 Simple Streaming Demo")
    print("-" * 30)
    
    # 1. Initialize SDK with online pipeline
    print("1. Initializing online streaming SDK...")
    sdk = StreamSDK(cfg_pkl, data_root)
    
    # 2. Setup with online mode enabled
    print("2. Setting up stream...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sdk.setup(source_path, output_path, 
              online_mode=True,           # Enable online processing
              sampling_timesteps=20)      # Faster inference
    
    # 3. Load audio
    print("3. Loading audio...")
    audio, sr = librosa.core.load(audio_path, sr=16000)
    
    # 4. Process in chunks (streaming style)
    print("4. Processing audio chunks...")
    
    # Chunk configuration
    chunksize = (3, 5, 2)  # (pre, main, post) frames
    split_len = int(sum(chunksize) * 0.04 * 16000) + 80
    step_size = chunksize[1] * 640
    
    # Add initial padding
    audio = np.concatenate([
        np.zeros((chunksize[0] * 640,), dtype=np.float32), 
        audio
    ], 0)
    
    # Process chunks
    chunk_num = 0
    for i in range(0, len(audio), step_size):
        chunk_num += 1
        
        # Extract chunk
        audio_chunk = audio[i:i + split_len]
        if len(audio_chunk) < split_len:
            audio_chunk = np.pad(
                audio_chunk, 
                (0, split_len - len(audio_chunk)), 
                mode="constant"
            )
        
        # Process chunk through streaming pipeline
        print(f"   Processing chunk {chunk_num}...")
        sdk.run_chunk(audio_chunk, chunksize)
    
    # 5. Finalize
    print("5. Finalizing video...")
    sdk.close()
    
    # 6. Add audio track
    print("6. Adding audio track...")
    cmd = (f'ffmpeg -loglevel error -y '
           f'-i "{sdk.tmp_output_path}" -i "{audio_path}" '
           f'-map 0:v -map 1:a -c:v copy -c:a aac '
           f'"{output_path}"')
    
    os.system(cmd)
    
    print(f"✅ Demo complete! Video saved: {output_path}")


if __name__ == "__main__":
    simple_streaming_demo()
