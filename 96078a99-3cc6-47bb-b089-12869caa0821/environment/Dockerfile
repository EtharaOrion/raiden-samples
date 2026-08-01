# syntax=docker/dockerfile:1
ARG BASE_IMAGE=426628337772.dkr.ecr.ap-south-1.amazonaws.com/kubectl_kwok@sha256:4bcfe127e1e126b50d1fee0a5fe98d69e19751a04ea8cf63eaf15144d1370530
FROM ${BASE_IMAGE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 TZ=UTC LC_ALL=C.UTF-8 \
    KUBECONFIG=/etc/kubeconfig
WORKDIR /workspace
RUN mkdir -p /workspace/submission && touch /workspace/submission/.gitkeep
ENV PATH=/workspace/submission:$PATH
RUN git config --global --add safe.directory /workspace && \
    git init -q /workspace && \
    git -C /workspace config user.email raiden@local && \
    git -C /workspace config user.name raiden && \
    git -C /workspace add -A && \
    git -C /workspace commit -q --allow-empty -m 'raiden: baseline'
