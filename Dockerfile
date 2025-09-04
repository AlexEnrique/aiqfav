FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv
RUN uv sync

FROM python:3.12-alpine AS runner

WORKDIR /app

RUN apk add --no-cache bash

COPY --from=builder /app /app

RUN pip install uv

COPY . .

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
