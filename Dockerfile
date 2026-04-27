# Stage 1: Build Python dependencies
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# Enable non-free repo for p7zip-rar, then install runtime deps
RUN echo "deb http://deb.debian.org/debian bookworm non-free" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    p7zip-full \
    p7zip-rar \
    unrar \
    unzip \
    zstd \
    curl \
    bash \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Timezone (configurable via env at runtime)
ENV TZ=Asia/Kolkata
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy project files (respects .dockerignore)
COPY . .

# Make start script executable
RUN chmod +x start.sh

CMD ["bash", "start.sh"]
