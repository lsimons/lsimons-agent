# Docker image for cross-platform electron builds
# Includes Python 3.12, uv, Node.js, and Wine (for Windows builds)
#
# Build: docker build -t lsimons-agent-builder -f docker/Dockerfile.builder .
# Usage: npm run build:linux:docker  or  npm run build:win:docker

FROM electronuserland/builder:18-wine

# Install Python 3.12
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -sf /root/.local/bin/uv /usr/local/bin/uv

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

WORKDIR /project
