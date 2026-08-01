# syntax=docker/dockerfile:1
ARG BASE_IMAGE=426628337772.dkr.ecr.ap-south-1.amazonaws.com/aws_cli_kms@sha256:017f6a2fa8f9e04413a40bf30b2b5f0ac48808462e537d01f576227144dd695f
FROM ${BASE_IMAGE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 TZ=UTC LC_ALL=C.UTF-8 \
    AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
    AWS_DEFAULT_REGION=us-east-1 \
    AWS_ENDPOINT_URL_KMS=http://kms:8080 \
    AWS_ENDPOINT_URL=http://kms:8080
WORKDIR /workspace
RUN python3 -m venv /opt/openhands-sdk-venv && \
    /opt/openhands-sdk-venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/openhands-sdk-venv/bin/pip install --no-cache-dir \
        "openhands-sdk @ https://github.com/Ethara-Ai/software-agent-sdk/archive/refs/tags/v1.12.0.tar.gz#subdirectory=openhands-sdk" \
        "openhands-tools @ https://github.com/Ethara-Ai/software-agent-sdk/archive/refs/tags/v1.12.0.tar.gz#subdirectory=openhands-tools" \
        "fastapi==0.138.2" "google-cloud-aiplatform==1.158.0"
RUN mkdir -p /workspace/submission && touch /workspace/submission/.gitkeep
ENV PATH=/workspace/submission:$PATH
RUN git config --global --add safe.directory /workspace && \
    git init -q /workspace && \
    git -C /workspace config user.email raiden@local && \
    git -C /workspace config user.name raiden && \
    git -C /workspace add -A && \
    git -C /workspace commit -q --allow-empty -m 'raiden: baseline'
