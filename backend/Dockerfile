FROM python:3.14.3-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.11.2 /uv /uvx /bin/

WORKDIR /app

COPY . .
RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]