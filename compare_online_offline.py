#!/usr/bin/env python3
"""
Comparison script showing differences between online and offline pipelines

This script demonstrates:
1. How to use both online and offline pipelines
2. Performance differences between the two approaches
3. When to use each pipeline
"""

import time
import librosa
import numpy as np
import os
from datetime import datetime

# Import both pipelines
from stream_pipeline_online import StreamSDK as OnlineSDK
from stream_pipeline_offline import StreamSDK as OfflineSDK


class PipelineComparison:
    def __init__(self, data_root, cfg_pkl_online, cfg_pkl_offline):
        self.data_root = data_root
        self.cfg_pkl_online = cfg_pkl_online
        self.cfg_pkl_offline = cfg_pkl_offline
        
    def run_offline_pipeline(self, audio_path, source_path, output_path):
        """Run the offline (batch) pipeline."""
        print("\n🔄 Running OFFLINE Pipeline...")
        print("-" * 40)
        
        start_time = time.time()
        
        # Initialize offline SDK
        sdk = OfflineSDK(self.cfg_pkl_offline, self.data_root)
        
        # Setup (batch processing)
        sdk.setup(source_path, output_path,
                 online_mode=False,        # Batch processing
                 sampling_timesteps=50)    # Higher quality
        
        # Load and process entire audio at once
        audio, sr = librosa.core.load(audio_path, sr=16000)
        num_frames = int(len(audio) / sr * 25)
        sdk.setup_Nd(N_d=num_frames)
        
        print(f"Processing {len(audio)/sr:.2f}s of audio ({len(audio)} samples)...")
        
        # Batch processing - all at once
        audio_features = sdk.wav2feat.wav2feat(audio)
        sdk.audio2motion_queue.put(audio_features)
        sdk.close()
        
        # Add audio track
        cmd = (f'ffmpeg -loglevel error -y '
               f'-i "{sdk.tmp_output_path}" -i "{audio_path}" '
               f'-map 0:v -map 1:a -c:v copy -c:a aac '
               f'"{output_path}"')
        os.system(cmd)
        
        processing_time = time.time() - start_time
        print(f"✅ Offline processing complete in {processing_time:.2f}s")
        print(f"   Output: {output_path}")
        
        return processing_time
        
    def run_online_pipeline(self, audio_path, source_path, output_path):
        """Run the online (streaming) pipeline."""
        print("\n⚡ Running ONLINE Pipeline...")
        print("-" * 40)
        
        start_time = time.time()
        
        # Initialize online SDK
        sdk = OnlineSDK(self.cfg_pkl_online, self.data_root)
        
        # Setup (streaming processing)
        sdk.setup(source_path, output_path,
                 online_mode=True,         # Streaming processing
                 sampling_timesteps=25,    # Faster inference
                 overlap_v2=8)            # Reduced latency
        
        # Load audio
        audio, sr = librosa.core.load(audio_path, sr=16000)
        print(f"Processing {len(audio)/sr:.2f}s of audio in streaming chunks...")
        
        # Streaming processing - chunk by chunk
        chunksize = (3, 5, 2)
        split_len = int(sum(chunksize) * 0.04 * 16000) + 80
        step_size = chunksize[1] * 640
        
        # Add padding
        audio_padded = np.concatenate([
            np.zeros((chunksize[0] * 640,), dtype=np.float32), 
            audio
        ], 0)
        
        chunk_count = 0
        for i in range(0, len(audio_padded), step_size):
            chunk_count += 1
            
            # Extract and pad chunk
            audio_chunk = audio_padded[i:i + split_len]
            if len(audio_chunk) < split_len:
                audio_chunk = np.pad(
                    audio_chunk, 
                    (0, split_len - len(audio_chunk)), 
                    mode="constant"
                )
            
            # Process chunk
            sdk.run_chunk(audio_chunk, chunksize)
            
            if chunk_count % 10 == 0:
                elapsed = time.time() - start_time
                progress = (i / len(audio_padded)) * 100
                print(f"   Processed {chunk_count} chunks ({progress:.1f}%) in {elapsed:.1f}s")
        
        sdk.close()
        
        # Add audio track
        cmd = (f'ffmpeg -loglevel error -y '
               f'-i "{sdk.tmp_output_path}" -i "{audio_path}" '
               f'-map 0:v -map 1:a -c:v copy -c:a aac '
               f'"{output_path}"')
        os.system(cmd)
        
        processing_time = time.time() - start_time
        print(f"✅ Online processing complete in {processing_time:.2f}s")
        print(f"   Processed {chunk_count} chunks")
        print(f"   Output: {output_path}")
        
        return processing_time
        
    def run_comparison(self, audio_path, source_path, base_output_path):
        """Run both pipelines and compare results."""
        print("🎭 Pipeline Comparison Demo")
        print("=" * 50)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Audio: {audio_path}")
        print(f"Source: {source_path}")
        
        # Prepare output paths
        offline_output = base_output_path.replace('.mp4', '_offline.mp4')
        online_output = base_output_path.replace('.mp4', '_online.mp4')
        
        os.makedirs(os.path.dirname(offline_output), exist_ok=True)
        
        try:
            # Run offline pipeline
            offline_time = self.run_offline_pipeline(audio_path, source_path, offline_output)
            
            # Run online pipeline  
            online_time = self.run_online_pipeline(audio_path, source_path, online_output)
            
            # Compare results
            print("\n📊 COMPARISON RESULTS")
            print("=" * 50)
            print(f"{'Method':<12} {'Time (s)':<10} {'Speed':<15} {'Use Case':<20}")
            print("-" * 60)
            print(f"{'Offline':<12} {offline_time:<10.2f} {'Higher Quality':<15} {'Batch Processing':<20}")
            print(f"{'Online':<12} {online_time:<10.2f} {'Lower Latency':<15} {'Real-time Streams':<20}")
            
            speed_diff = (offline_time - online_time) / offline_time * 100
            if online_time < offline_time:
                print(f"\n⚡ Online was {speed_diff:.1f}% faster")
            else:
                print(f"\n🔄 Offline was {-speed_diff:.1f}% faster")
                
            print(f"\nOutput files:")
            print(f"  Offline: {offline_output}")
            print(f"  Online:  {online_output}")
            
            print(f"\n💡 Recommendations:")
            print("  - Use OFFLINE for: Pre-recorded videos, batch processing, maximum quality")
            print("  - Use ONLINE for: Live streaming, video calls, real-time interaction")
            
        except Exception as e:
            print(f"\n❌ Comparison failed: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Main comparison demo."""
    
    # Configuration
    data_root = "./checkpoints/ditto_trt_Ampere_Plus"
    cfg_offline = "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt.pkl"
    cfg_online = "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt_online.pkl"
    
    audio_path = "./data/audio/relativity.wav"
    source_path = "./data/image/einstein_portrait.jpg"
    output_path = "./output/comparison_demo.mp4"
    
    # Run comparison
    comparison = PipelineComparison(data_root, cfg_online, cfg_offline)
    comparison.run_comparison(audio_path, source_path, output_path)


if __name__ == "__main__":
    main()
