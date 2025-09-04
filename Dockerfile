FROM docker.repo.local.sfdc.net/sfci/docker-images/sfdc_rhel9_python3/sfdc_rhel9_python3.12

WORKDIR /app

# Note: ffmpeg is provided by imageio-ffmpeg Python package
# No additional system dependencies needed

COPY core/ ./core/
COPY inference.py .
COPY pip.conf /app/pip.conf
COPY stream_pipeline_offline.py .
COPY stream_pipeline_online.py .
COPY example/ ./example/
COPY requirements.txt .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Install Python dependencies using the correct pip version
RUN pip3.12 install --upgrade pip && \
    pip3.12 install --no-cache-dir -r requirements.txt
RUN pip3.12 install awscli

# Create necessary directories
RUN mkdir -p /app/checkpoints /app/tmp /app/input /app/output

# Set environment variables
ENV PYTHONPATH=/app
# ENV DITTO_DEVICE=cpu
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
