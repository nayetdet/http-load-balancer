# Build Stage
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder
ARG PACKAGE=http_target_discovery
ENV UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-install-workspace

COPY packages/"$PACKAGE" /app/packages/"$PACKAGE"
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --package="$PACKAGE"

# Runtime Stage
FROM python:3.14-slim-trixie
ARG PACKAGE=http_target_discovery
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages/"$PACKAGE"/src /app/packages/"$PACKAGE"/src

EXPOSE 8080
CMD ["python", "-m", "http_load_balancer"]
