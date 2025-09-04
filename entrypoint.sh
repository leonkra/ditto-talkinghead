#!/bin/bash

set -e

echo "=== Ditto TalkingHead Container Starting ==="

# Environment variables with defaults
S3_CHECKPOINTS_BUCKET=${S3_CHECKPOINTS_BUCKET:-"your-s3-bucket"}
S3_CHECKPOINTS_PATH=${S3_CHECKPOINTS_PATH:-"ditto-talkinghead/checkpoints"}
CHECKPOINTS_DIR=${CHECKPOINTS_DIR:-"/app/checkpoints"}
AWS_REGION=${AWS_REGION:-"us-west-2"}

# Function to download checkpoints from S3
download_checkpoints() {
    echo "Downloading checkpoints from S3..."
    echo "Bucket: ${S3_CHECKPOINTS_BUCKET}"
    echo "Path: ${S3_CHECKPOINTS_PATH}"
    echo "Destination: ${CHECKPOINTS_DIR}"
    
    # Check if checkpoints already exist
    if [ -d "${CHECKPOINTS_DIR}/ditto_pytorch" ] && [ -d "${CHECKPOINTS_DIR}/ditto_cfg" ]; then
        echo "Checkpoints already exist, skipping download."
        return 0
    fi
    
    # Download using AWS CLI (assuming it's available in the base image)
    if command -v aws &> /dev/null; then
        aws s3 sync "s3://${S3_CHECKPOINTS_BUCKET}/${S3_CHECKPOINTS_PATH}/" "${CHECKPOINTS_DIR}/" --region="${AWS_REGION}"
    else
        echo "ERROR: AWS CLI not found. Please install it or use alternative download method."
        exit 1
    fi
    
    echo "Checkpoints download completed."
}

# Function to verify checkpoints
verify_checkpoints() {
    echo "Verifying checkpoints..."
    
    required_dirs=("ditto_pytorch" "ditto_cfg")
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "${CHECKPOINTS_DIR}/${dir}" ]; then
            echo "ERROR: Required directory ${CHECKPOINTS_DIR}/${dir} not found!"
            exit 1
        fi
    done
    
    # Check for key files
    if [ ! -f "${CHECKPOINTS_DIR}/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl" ]; then
        echo "ERROR: Configuration file not found!"
        exit 1
    fi
    
    echo "Checkpoints verification completed."
}

# Function to run inference
run_inference() {
    echo "Starting inference..."
    
    # Default parameters (can be overridden by environment variables)
    DATA_ROOT=${DATA_ROOT:-"${CHECKPOINTS_DIR}/ditto_pytorch"}
    CFG_PKL=${CFG_PKL:-"${CHECKPOINTS_DIR}/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl"}
    AUDIO_PATH=${AUDIO_PATH:-"/app/input/audio.wav"}
    SOURCE_PATH=${SOURCE_PATH:-"/app/input/image.png"}
    OUTPUT_PATH=${OUTPUT_PATH:-"/app/output/result.mp4"}
    
    # Create input/output directories if they don't exist
    mkdir -p /app/input /app/output
    
    # Check if input files exist
    if [ ! -f "${AUDIO_PATH}" ]; then
        echo "WARNING: Audio file not found at ${AUDIO_PATH}"
        echo "Using example audio file..."
        AUDIO_PATH="/app/example/audio.wav"
    fi
    
    if [ ! -f "${SOURCE_PATH}" ]; then
        echo "WARNING: Source image not found at ${SOURCE_PATH}"
        echo "Using example image file..."
        SOURCE_PATH="/app/example/image.png"
    fi
    
    # Run the inference using python3.12
    DITTO_DEVICE=${DITTO_DEVICE:-cpu} python3.12 inference.py \
        --data_root "${DATA_ROOT}" \
        --cfg_pkl "${CFG_PKL}" \
        --audio_path "${AUDIO_PATH}" \
        --source_path "${SOURCE_PATH}" \
        --output_path "${OUTPUT_PATH}"
    
    echo "Inference completed. Output saved to: ${OUTPUT_PATH}"
}

# Function to start web server (if needed)
start_server() {
    echo "Starting web server mode..."
    # Add your web server startup logic here
    # For example, if you have a Flask/FastAPI server:
    # python3.12 server.py
    echo "Server mode not implemented yet."
}

# Main execution logic
main() {
    echo "Arguments: $*"
    
    # Download and verify checkpoints
    download_checkpoints
    verify_checkpoints
    
    # Parse command line arguments
    case "${1:-inference}" in
        "inference")
            run_inference
            ;;
        "server")
            start_server
            ;;
        "bash")
            exec /bin/bash
            ;;
        *)
            echo "Usage: $0 [inference|server|bash]"
            echo "  inference: Run single inference (default)"
            echo "  server:    Start web server"
            echo "  bash:      Open bash shell"
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
