#!/usr/bin/env python3
"""
Quick test script to verify streaming setup is working correctly.

This script performs basic validation of:
1. Required files and directories
2. Import capabilities  
3. Basic SDK initialization
4. Configuration loading
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def test_imports():
    """Test if required modules can be imported."""
    print("\n🔍 Testing Imports...")
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
        print(f"   - CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   - GPU: {torch.cuda.get_device_name(0)}")
        else:
            print(f"   - MPS available: {torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import librosa
        print("✅ Librosa imported successfully")
    except ImportError as e:
        print(f"❌ Librosa import failed: {e}")
        return False
        
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
        
    try:
        from stream_pipeline_online import StreamSDK
        print("✅ Online StreamSDK imported successfully")
    except ImportError as e:
        print(f"❌ Online StreamSDK import failed: {e}")
        return False
        
    try:
        from stream_pipeline_offline import StreamSDK as OfflineSDK
        print("✅ Offline StreamSDK imported successfully")
    except ImportError as e:
        print(f"❌ Offline StreamSDK import failed: {e}")
        return False
        
    return True

def test_file_structure():
    """Test if required files and directories exist."""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        ("./stream_pipeline_online.py", "Online pipeline script"),
        ("./stream_pipeline_offline.py", "Offline pipeline script"), 
        ("./core/", "Core modules directory"),
        ("./data/audio/relativity.wav", "Sample audio file"),
        ("./data/image/einstein_portrait.jpg", "Sample image file"),
    ]
    
    all_exist = True
    for filepath, desc in required_files:
        exists = check_file_exists(filepath, desc)
        all_exist = all_exist and exists
        
    return all_exist

def test_checkpoint_files():
    """Test if model checkpoint files exist."""
    print("\n🧠 Testing Model Checkpoints...")
    
    base_checkpoints = "./checkpoints/"
    if not os.path.exists(base_checkpoints):
        print(f"❌ Checkpoints directory not found: {base_checkpoints}")
        print("   Download checkpoints from: https://huggingface.co/digital-avatar/ditto-talkinghead")
        return False
        
    checkpoint_sets = [
        ("ditto_cfg/v0.4_hubert_cfg_pytorch.pkl", "PyTorch config"),
        ("ditto_cfg/v0.4_hubert_cfg_trt.pkl", "TensorRT offline config"),
        ("ditto_cfg/v0.4_hubert_cfg_trt_online.pkl", "TensorRT online config"),
        ("ditto_pytorch/", "PyTorch models"),
        ("ditto_onnx/", "ONNX models"),
        ("ditto_trt_Ampere_Plus/", "TensorRT models"),
    ]
    
    any_exist = False
    for checkpoint_path, desc in checkpoint_sets:
        full_path = os.path.join(base_checkpoints, checkpoint_path)
        exists = check_file_exists(full_path, desc)
        if exists:
            any_exist = True
    
    if not any_exist:
        print("\n💡 To download checkpoints:")
        print("   git lfs install")
        print("   git clone https://huggingface.co/digital-avatar/ditto-talkinghead checkpoints")
        
    return any_exist

def test_basic_sdk_init():
    """Test basic SDK initialization without full setup."""
    print("\n🚀 Testing SDK Initialization...")
    
    # Find available config files
    config_files = []
    config_options = [
        "./checkpoints/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl",
        "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt.pkl", 
        "./checkpoints/ditto_cfg/v0.4_hubert_cfg_trt_online.pkl"
    ]
    
    for config in config_options:
        if os.path.exists(config):
            config_files.append(config)
    
    if not config_files:
        print("❌ No configuration files found - cannot test SDK initialization")
        return False
        
    # Find available model directories
    model_dirs = []
    model_options = [
        "./checkpoints/ditto_pytorch",
        "./checkpoints/ditto_onnx",
        "./checkpoints/ditto_trt_Ampere_Plus"
    ]
    
    for model_dir in model_options:
        if os.path.exists(model_dir):
            model_dirs.append(model_dir)
            
    if not model_dirs:
        print("❌ No model directories found - cannot test SDK initialization")
        return False
        
    try:
        from stream_pipeline_online import StreamSDK
        
        config_file = config_files[0]
        model_dir = model_dirs[0]
        
        print(f"   Testing with: {config_file}")
        print(f"   Model dir: {model_dir}")
        
        sdk = StreamSDK(config_file, model_dir)
        print("✅ SDK initialized successfully")
        
        # Test that it has expected attributes
        if hasattr(sdk, 'setup') and hasattr(sdk, 'run_chunk'):
            print("✅ SDK has expected streaming methods")
            return True
        else:
            print("❌ SDK missing expected methods")
            return False
            
    except Exception as e:
        print(f"❌ SDK initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Ditto Streaming Setup Test")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Imports", test_imports),
        ("Model Checkpoints", test_checkpoint_files),
        ("SDK Initialization", test_basic_sdk_init),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Your streaming setup is ready.")
        print("\n🚀 Next steps:")
        print("   1. Run: python simple_streaming_example.py")
        print("   2. Try: python demo_online_streaming.py --help")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        if not results.get("Model Checkpoints", False):
            print("\n💡 Most likely issue: Missing model checkpoints")
            print("   Download with: git clone https://huggingface.co/digital-avatar/ditto-talkinghead checkpoints")
    
    return passed == len(tests)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
