#!/usr/bin/env bash

PYTHON_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd "$PYTHON_DIR"

print_usage() {
    echo "
    1. '-prepare-env' to build and test clean local environment
    2. '-build-docker' build docker
    3. '-run-docker' run docker
    4. '-help'"
}

if [[ "$#" -eq 0 ]]; then
    echo "No arguments provided. Usage:"
    print_usage
elif [[ $1 = "-prepare-env" ]]; then
    set -e
    echo "Creating venv and running format, linter and tests"
    rm -rf .venv
    python3.12 -m venv .venv
    source .venv/bin/activate
    pip3 install --upgrade pip
    pip3 install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0
    pip3 install -r requirements.txt
elif [[ $1 = "-build-docker" ]]; then
    set -e
    echo "Building docker"
    docker build -t ditto-talkinghead .
elif [[ $1 = "-run-docker" ]]; then
    set -e
    echo "Running docker"
    docker run -it --rm --name ditto-talkinghead --entrypoint /bin/bash ditto-talkinghead
elif [[ $1 = "-help" ]]; then
    print_usage
else
    echo "Wrong arguments provided. Usage:"
    print_usage
fi
