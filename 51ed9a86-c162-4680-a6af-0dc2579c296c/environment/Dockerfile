# syntax=docker/dockerfile:1
ARG BASE_IMAGE=426628337772.dkr.ecr.ap-south-1.amazonaws.com/aws_cli_cognito@sha256:b24fac06ef0ec589f4320bf5b1f02d1996fa527c74e57f56ac4c4f1826d6f6d0
FROM ${BASE_IMAGE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 TZ=UTC LC_ALL=C.UTF-8 \
    AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
    AWS_DEFAULT_REGION=us-east-1 \
    AWS_ENDPOINT_URL_COGNITO_IDENTITY_PROVIDER=http://cognito:9229 \
    AWS_ENDPOINT_URL=http://cognito:9229
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
