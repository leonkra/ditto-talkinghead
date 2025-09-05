FROM docker.repo.local.sfdc.net/sfci/docker-images/sfdc_rhel9_python3/sfdc_rhel9_python3.12

WORKDIR /app

COPY core/ ./core/
COPY scripts/ ./scripts/
COPY inference.py .
COPY pip.conf /app/pip.conf
COPY stream_pipeline_offline.py .
COPY stream_pipeline_online.py .
COPY example/ ./example/
COPY requirements.txt .
COPY requirements-no-gpu.txt .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN dnf -y install gcc python3.12-devel \
    mesa-libGL \
    mesa-libGLU \
    libSM \
    libXext \
    libXrender \
    glib2

RUN rm -rf /usr/bin/python3; rm -rf /usr/bin/pip3;ln -s python3.12 /usr/bin/python3; ln -s pip3.12 /usr/bin/pip3

RUN python3.12 scripts/install_ffmpeg.py

RUN pip3.12 install --upgrade pip && \
    (pip3.12 install --no-cache-dir -r requirements.txt || \
     (echo "Some GPU packages failed, installing without GPU dependencies..." && \
      pip3.12 install --no-cache-dir -r requirements-no-gpu.txt))

RUN pip3.12 install awscli

RUN mkdir -p /app/checkpoints /app/output
COPY checkpoints/ /app/checkpoints/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
