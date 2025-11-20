FROM python:3.12.8-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src:/app/tests

COPY . .

RUN python -m compileall -q src tests scripts

CMD ["python", "-m", "pixelforge_ops.cli", "--help"]
