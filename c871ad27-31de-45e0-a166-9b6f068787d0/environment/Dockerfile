ARG BASE_IMAGE=426628337772.dkr.ecr.ap-south-1.amazonaws.com/aws_cli_s3@sha256:4727c7b02c158f418fdf1be7cb78adfdfb40663861936ec20c2b0c1a8f16ded6
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 TZ=UTC LC_ALL=C.UTF-8 \
    AWS_ACCESS_KEY_ID=raidentest AWS_SECRET_ACCESS_KEY=raidentest \
    AWS_DEFAULT_REGION=us-east-1 \
    MINIO_ROOT_USER=raidentest MINIO_ROOT_PASSWORD=raidentest \
    MINIO_CI_CD=on MINIO_BROWSER=off \
    MINIO_KMS_SECRET_KEY="foo:IyqsE3sBqcMSlonhAxfqLK1kHhIzy+xvyJZbfFbcHT4="
WORKDIR /workspace
RUN apt-get update && apt-get install -y --no-install-recommends \
      git ca-certificates curl && rm -rf /var/lib/apt/lists/*

RUN apt-get purge -y python3-blinker 2>/dev/null || true
RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir "colorama>=0.2.5,<0.4.7" "docutils>=0.10,<0.20" "ruamel.yaml>=0.15.0,<=0.17.21" "ruamel.yaml.clib>=0.2.0,<=0.2.12" "prompt-toolkit>=3.0.24,<3.0.52" "distro>=1.5.0,<1.9.0" "awscrt==0.27.6" "python-dateutil>=2.1,<=2.9.0" "jmespath>=0.7.1,<1.1.0" "urllib3>=1.25.4,<1.27" "pytest==8.3.3" "freezegun==1.5.1" "requests==2.32.3"

# `minio` Python client is installed into a test-only site-packages dir.
# tests/test.sh prepends this to PYTHONPATH; conftest.py strips it back out
# before invoking submission/aws, so agent submissions cannot `import minio`.
RUN pip install --no-cache-dir --target=/opt/test-libs "minio==7.2.15" \
    && chmod -R a+rX /opt/test-libs

ARG MINIO_RELEASE=RELEASE.2025-04-22T22-12-26Z
RUN ARCH="$(dpkg --print-architecture)" && \
    curl -fsSL "https://dl.min.io/server/minio/release/linux-${ARCH}/archive/minio.${MINIO_RELEASE}" \
        -o /usr/local/bin/minio && \
    chmod +x /usr/local/bin/minio && \
    /usr/local/bin/minio --version

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