import torch

print(f"PyTorch version: {torch.__version__}")

# Check if MPS is available
if torch.backends.mps.is_available():
    print("Apple Metal (MPS) backend is available! ✅")
    device = torch.device("mps")

    # Create a tensor and move it to the MPS device
    x = torch.ones(5, 3, device=device)
    print("Successfully created a tensor on the MPS device:")
    print(x)
else:
    print("Apple Metal (MPS) backend is NOT available. Running on CPU. ❌")
    device = torch.device("cpu")