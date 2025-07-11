# 🐍──────────────────────────────────────────────
# 1️⃣ Base Layer (Prod Runtime)
# 🐍──────────────────────────────────────────────
FROM python:3.12-slim AS base

# 📦 Optimize pip usage
ARG PIP_NO_CACHE_DIR=off

# 🚫 Prevent .pyc + unbuffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 🛠️ System packages for wheel builds
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential \
 && rm -rf /var/lib/apt/lists/*

# 📂 Set working directory
WORKDIR /app

# 📜 Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🐍──────────────────────────────────────────────
# 2️⃣ Dev/Test Layer (flake8, pytest, etc.)
# 🐍──────────────────────────────────────────────
FROM base AS dev

# 📜 Install development dependencies
COPY requirements.dev.txt .
RUN pip install --no-cache-dir -r requirements.dev.txt

# 🛠️ Optional: start with bash for local iteration
CMD ["bash"]

# 🐍──────────────────────────────────────────────
# 3️⃣ Final Production Image
# 🐍──────────────────────────────────────────────
FROM base AS prod

# 📂 Copy application code
COPY . .

# 🗝️ Copy entrypoint and set permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 🚀 Run entrypoint on container start
ENTRYPOINT ["/entrypoint.sh"]
