"""
Centralized device detection for consistent device usage across all models.
"""
import os
import torch

def get_device():
    """Get the best available device with environment override support."""
    # Allow environment override for debugging
    forced_device = os.environ.get('DITTO_DEVICE')
    if forced_device:
        print(f"Using forced device from environment: {forced_device}")
        return forced_device
    
    # Auto-detect best available device
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"
