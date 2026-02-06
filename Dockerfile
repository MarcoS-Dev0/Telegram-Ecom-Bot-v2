# -- Stage 1: Builder --
FROM python:3.11-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install .

# -- Stage 2: Runtime --
FROM python:3.11-slim AS runtime

LABEL maintainer="MarcoS-Dev0"
LABEL description="Telegram E-Commerce Bot v2 - automated sales with Stripe payments"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd -r botuser && useradd -r -g botuser -d /app botuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY src/ ./src/
COPY locales/ ./locales/

RUN chown -R botuser:botuser /app
USER botuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
