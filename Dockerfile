FROM python:3.13-slim

WORKDIR /app
# aiohttp 3.9.0 and PyYAML 6.0.1 have no Python 3.13 wheels and are built from source
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY LlamaTale/requirements.txt LlamaTale/requirements.txt
# setuptools provides distutils, which tale imports and Python 3.12+ removed
RUN pip install --no-cache-dir -r LlamaTale/requirements.txt setuptools
COPY . .

# the hosted server can't reach our local Ollama, so use Gemma on the Gemini API (key from GEMINI_API_KEY)
ARG LLM_BACKEND=gemini
RUN sed -i "s/^BACKEND: .*/BACKEND: ${LLM_BACKEND}/" LlamaTale/llm_config.yaml

ENV PYTHONPATH=/app/LlamaTale PYTHONUNBUFFERED=1 MUD_HOST=0.0.0.0
WORKDIR /app/LlamaTale
EXPOSE 8180
CMD ["sh", "-c", "python /app/deploy/create_admin.py && exec python -m tale.main --game /app/story --mode mud"]
