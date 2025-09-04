# Docker Deployment Guide

This guide covers deploying the Ditto TalkingHead solution using Docker containers.

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t ditto-talkinghead .
```

### 2. Run with Docker Compose (Recommended)

```bash
# Set your AWS credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# Update docker-compose.yml with your S3 bucket details
# Then run:
docker-compose up
```

### 3. Run with Docker CLI

```bash
docker run -it \
  -e S3_CHECKPOINTS_BUCKET=your-s3-bucket \
  -e S3_CHECKPOINTS_PATH=ditto-talkinghead/checkpoints \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output:rw \
  ditto-talkinghead inference
```

## Environment Variables

### Required
- `S3_CHECKPOINTS_BUCKET`: S3 bucket containing model checkpoints
- `S3_CHECKPOINTS_PATH`: Path within the bucket to checkpoints directory
- `AWS_ACCESS_KEY_ID`: AWS access key for S3 access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 access

### Optional
- `AWS_REGION`: AWS region (default: us-west-2)
- `DITTO_DEVICE`: Device to use (default: cpu)
- `AUDIO_PATH`: Path to input audio file (default: /app/input/audio.wav)
- `SOURCE_PATH`: Path to input image file (default: /app/input/image.png)
- `OUTPUT_PATH`: Path to output video file (default: /app/output/result.mp4)

## Usage Modes

### 1. Single Inference (Default)

```bash
docker run --rm -it \
  -e S3_CHECKPOINTS_BUCKET=your-bucket \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output:rw \
  ditto-talkinghead inference
```

### 2. Interactive Shell (Debugging)

```bash
docker run --rm -it \
  -e S3_CHECKPOINTS_BUCKET=your-bucket \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  ditto-talkinghead bash
```

### 3. Server Mode (Future Implementation)

```bash
docker run --rm -it \
  -p 8080:8080 \
  -e S3_CHECKPOINTS_BUCKET=your-bucket \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  ditto-talkinghead server
```

## File Structure

```
/app/
├── core/                   # Application code
├── inference.py           # Main inference script
├── entrypoint.sh         # Container entrypoint
├── checkpoints/          # Downloaded from S3
│   ├── ditto_pytorch/    # PyTorch models
│   └── ditto_cfg/        # Configuration files
├── input/                # Input files (mounted volume)
│   ├── audio.wav         # Input audio
│   └── image.png         # Input image
├── output/               # Output files (mounted volume)
│   └── result.mp4        # Generated video
└── data/                 # Example files
    ├── audio/
    └── image/
```

## Example Usage

### Prepare Input Files

```bash
mkdir -p input output
cp your_audio.wav input/audio.wav
cp your_image.jpg input/image.png
```

### Run Inference

```bash
# Using docker-compose (recommended)
docker-compose up

# Or using docker run
docker run --rm \
  -e S3_CHECKPOINTS_BUCKET=my-models-bucket \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output:rw \
  ditto-talkinghead
```

### Check Output

```bash
ls -la output/
# Should contain result.mp4
```

## Troubleshooting

### 1. S3 Access Issues
- Verify AWS credentials
- Check S3 bucket permissions
- Ensure checkpoints exist at the specified path

### 2. Memory Issues
- Increase Docker memory limits
- Use CPU device instead of GPU if running out of memory

### 3. File Permission Issues
```bash
# Fix ownership of output files
sudo chown -R $USER:$USER output/
```

### 4. Debug Container
```bash
# Get a shell inside the container
docker run --rm -it ditto-talkinghead bash

# Check if checkpoints downloaded correctly
ls -la /app/checkpoints/
```

## Performance Optimization

### CPU Usage
- Default configuration uses CPU
- Processing time: ~11-12 minutes per video
- Memory usage: ~4-6GB

### GPU Usage (Future)
```bash
# For CUDA-enabled containers
docker run --gpus all \
  -e DITTO_DEVICE=cuda \
  ditto-talkinghead
```

## Production Deployment

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ditto-talkinghead
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ditto-talkinghead
  template:
    metadata:
      labels:
        app: ditto-talkinghead
    spec:
      containers:
      - name: ditto-talkinghead
        image: ditto-talkinghead:latest
        env:
        - name: S3_CHECKPOINTS_BUCKET
          value: "your-models-bucket"
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: secret-access-key
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
```

## Security Notes

- Store AWS credentials securely (use secrets, not environment variables in production)
- Use least-privilege IAM roles for S3 access
- Regularly update base images for security patches
- Consider using AWS IAM roles for service accounts in Kubernetes
