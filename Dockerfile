FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN python -m pip install --no-cache-dir ".[web]" \
    && groupadd --system filab \
    && useradd --system --gid filab --create-home filab

USER filab

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "filab.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
