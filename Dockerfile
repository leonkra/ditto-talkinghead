# Use a PyTorch base image that supports Apple Silicon (arm64)
# The official pytorch images often have multi-platform support.
FROM pytorch/pytorch:latest

WORKDIR /app

COPY verify_gpu.py .

CMD ["python", "verify_gpu.py"]
