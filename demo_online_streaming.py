#!/usr/bin/env python3
"""
Demo script for stream_pipeline_online.py - Real-time Talking Head Streaming

This script demonstrates how to use the online streaming pipeline for:
1. Real-time audio processing in chunks
2. Low-latency video generation
3. Streaming-style inference suitable for live applications

Usage:
    python demo_online_streaming.py \
        --data_root "./checkpoints/ditto_trt_Ampere_Plus" \
        --cfg_pkl "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt_online.pkl" \
        --audio_path "./data/audio/relativity.wav" \
        --source_path "./data/image/einstein_portrait.jpg" \
        --output_path "./output/streaming_demo.mp4" \
        --chunk_duration 0.5 \
        --simulate_realtime
"""

import librosa
import math
import os
import sys
import time
import numpy as np
import argparse
from datetime import datetime

# Import the ONLINE streaming SDK
from stream_pipeline_online import StreamSDK


class RealTimeStreamer:
    def __init__(self, cfg_pkl, data_root):
        """Initialize the real-time streaming system."""
        print(f"🚀 Initializing Online Streaming SDK...")
        print(f"   Config: {cfg_pkl}")
        print(f"   Data Root: {data_root}")
        
        self.sdk = StreamSDK(cfg_pkl, data_root)
        self.start_time = None
        self.processed_chunks = 0
        
    def setup_stream(self, source_path, output_path, **kwargs):
        """Setup the streaming pipeline with online mode enabled."""
        print(f"\n📺 Setting up stream...")
        print(f"   Source: {source_path}")
        print(f"   Output: {output_path}")
        
        # Force online mode and streaming-optimized settings
        streaming_kwargs = {
            "online_mode": True,
            "sampling_timesteps": 25,  # Reduced for speed (vs 50 for quality)
            "overlap_v2": 8,           # Reduced overlap for lower latency
            **kwargs
        }
        
        self.sdk.setup(source_path, output_path, **streaming_kwargs)
        print("✅ Stream setup complete!")
        
    def process_audio_chunks(self, audio_path, chunk_duration=0.5, simulate_realtime=False):
        """
        Process audio in streaming chunks.
        
        Args:
            audio_path: Path to input audio file
            chunk_duration: Duration of each chunk in seconds
            simulate_realtime: If True, add delays to simulate real-time processing
        """
        print(f"\n🎵 Loading and processing audio: {audio_path}")
        print(f"   Chunk duration: {chunk_duration}s")
        print(f"   Real-time simulation: {simulate_realtime}")
        
        # Load audio
        audio, sr = librosa.core.load(audio_path, sr=16000)
        total_duration = len(audio) / sr
        print(f"   Total audio duration: {total_duration:.2f}s")
        
        # Calculate chunk parameters
        chunksize = (3, 5, 2)  # (pre_frames, main_frames, post_frames)
        samples_per_chunk = int(chunk_duration * sr)
        
        # Add padding for the first chunk
        audio_padded = np.concatenate([
            np.zeros((chunksize[0] * 640,), dtype=np.float32), 
            audio
        ], 0)
        
        # Calculate streaming parameters
        split_len = int(sum(chunksize) * 0.04 * 16000) + 80  # 6480 samples
        step_size = chunksize[1] * 640  # Main chunk step
        
        print(f"   Chunk size config: {chunksize}")
        print(f"   Samples per processing window: {split_len}")
        print(f"   Step size: {step_size}")
        
        self.start_time = time.time()
        chunk_count = 0
        
        print(f"\n⚡ Starting real-time streaming processing...")
        print("-" * 60)
        
        # Process audio in chunks
        for i in range(0, len(audio_padded), step_size):
            chunk_start_time = time.time()
            
            # Extract audio chunk
            audio_chunk = audio_padded[i:i + split_len]
            if len(audio_chunk) < split_len:
                # Pad the final chunk
                audio_chunk = np.pad(
                    audio_chunk, 
                    (0, split_len - len(audio_chunk)), 
                    mode="constant"
                )
            
            # Calculate timing info
            current_audio_time = i / sr
            chunk_count += 1
            
            print(f"📦 Chunk {chunk_count:3d} | "
                  f"Audio time: {current_audio_time:6.2f}s | "
                  f"Samples: {len(audio_chunk):5d} | ", end="")
            
            # Process the chunk through the streaming pipeline
            processing_start = time.time()
            try:
                self.sdk.run_chunk(audio_chunk, chunksize)
                processing_time = time.time() - processing_start
                
                print(f"Processed in {processing_time:.3f}s")
                
                # Simulate real-time constraints
                if simulate_realtime:
                    # Sleep to simulate real-time input
                    real_time_delay = chunk_duration - processing_time
                    if real_time_delay > 0:
                        time.sleep(real_time_delay)
                        
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                break
            
            self.processed_chunks += 1
            
            # Progress update every 10 chunks
            if chunk_count % 10 == 0:
                elapsed = time.time() - self.start_time
                progress = (current_audio_time / total_duration) * 100
                print(f"   📊 Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s")
        
        print("-" * 60)
        print(f"✅ Streaming processing complete!")
        print(f"   Total chunks processed: {self.processed_chunks}")
        print(f"   Total time: {time.time() - self.start_time:.2f}s")
        
    def finalize_stream(self, audio_path, output_path):
        """Finalize the stream and create the output video."""
        print(f"\n🎬 Finalizing video stream...")
        
        # Close the streaming pipeline
        self.sdk.close()
        
        # Add audio track using ffmpeg
        print(f"   Adding audio track...")
        cmd = (f'ffmpeg -loglevel error -y '
               f'-i "{self.sdk.tmp_output_path}" '
               f'-i "{audio_path}" '
               f'-map 0:v -map 1:a -c:v copy -c:a aac '
               f'"{output_path}"')
        
        print(f"   Running: {cmd}")
        result = os.system(cmd)
        
        if result == 0:
            print(f"✅ Video saved successfully: {output_path}")
        else:
            print(f"❌ Error creating final video")
            
        return result == 0


def main():
    parser = argparse.ArgumentParser(
        description="Real-time streaming demo for Ditto talking head",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--data_root", type=str, required=True,
                      help="Path to model data root directory")
    parser.add_argument("--cfg_pkl", type=str, required=True,
                      help="Path to configuration pickle file (use *_online.pkl for best results)")
    parser.add_argument("--audio_path", type=str, required=True,
                      help="Path to input audio file")
    parser.add_argument("--source_path", type=str, required=True,
                      help="Path to input source image")
    parser.add_argument("--output_path", type=str, required=True,
                      help="Path for output video")
    
    # Streaming parameters
    parser.add_argument("--chunk_duration", type=float, default=0.5,
                      help="Duration of each audio chunk in seconds (smaller = lower latency)")
    parser.add_argument("--simulate_realtime", action="store_true",
                      help="Add delays to simulate real-time processing")
    parser.add_argument("--sampling_timesteps", type=int, default=25,
                      help="Diffusion sampling steps (lower = faster, higher = better quality)")
    
    args = parser.parse_args()
    
    # Validate inputs
    for path_arg, path_value in [("audio_path", args.audio_path), ("source_path", args.source_path)]:
        if not os.path.exists(path_value):
            print(f"❌ Error: {path_arg} does not exist: {path_value}")
            return 1
    
    # Create output directory
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    
    print("🎭 Ditto Real-Time Streaming Demo")
    print("=" * 50)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'Real-time simulation' if args.simulate_realtime else 'Batch streaming'}")
    
    try:
        # Initialize the streaming system
        streamer = RealTimeStreamer(args.cfg_pkl, args.data_root)
        
        # Setup the stream
        streamer.setup_stream(
            args.source_path, 
            args.output_path,
            sampling_timesteps=args.sampling_timesteps
        )
        
        # Process audio in streaming chunks
        streamer.process_audio_chunks(
            args.audio_path,
            chunk_duration=args.chunk_duration,
            simulate_realtime=args.simulate_realtime
        )
        
        # Finalize and save the video
        success = streamer.finalize_stream(args.audio_path, args.output_path)
        
        if success:
            print(f"\n🎉 Demo completed successfully!")
            print(f"   Output video: {args.output_path}")
            return 0
        else:
            print(f"\n❌ Demo failed during finalization")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
