FROM python:3.13-slim

WORKDIR /app
# aiohttp 3.9.0 and PyYAML 6.0.1 have no Python 3.13 wheels and are built from source
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
# ttyd serves the terminal version (deploy/terminal.sh); Debian doesn't package it
ADD --chmod=755 https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 /usr/local/bin/ttyd
COPY LlamaTale/requirements.txt LlamaTale/requirements.txt
# setuptools provides distutils, which tale imports and Python 3.12+ removed
RUN pip install --no-cache-dir -r LlamaTale/requirements.txt setuptools
COPY . .

# the hosted server can't reach our local Ollama, so use Gemma on the Gemini API (key from GEMINI_API_KEY)
ARG LLM_BACKEND=gemini
RUN sed -i "s/^BACKEND: .*/BACKEND: ${LLM_BACKEND}/" LlamaTale/llm_config.yaml

ENV PYTHONPATH=/app/LlamaTale PYTHONUNBUFFERED=1 MUD_HOST=0.0.0.0
# tale runs in the game folder and copies its images to ../../tale/web, so the game must sit in LlamaTale/stories
RUN mv /app/story /app/LlamaTale/stories/hallow_mud

# run as an unprivileged user who owns the app, since the game writes images and accounts at runtime
RUN useradd --create-home hallow && chown -R hallow /app
USER hallow
WORKDIR /app/LlamaTale
EXPOSE 8180
CMD ["sh", "/app/deploy/start.sh"]
