# Use a PyTorch base image that supports Apple Silicon (arm64)
# The official pytorch images often have multi-platform support.
FROM pytorch/pytorch:latest

# Set the working directory
WORKDIR /app

Copy your Python script into the container
COPY verify_gpu.py .

# Command to run your script
CMD ["python", "verify_gpu.py"]
