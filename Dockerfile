FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN python -m pip install --no-cache-dir "pip>=26.2"

COPY pyproject.toml ./

# Setuptools needs these placeholders to read dependency metadata.
RUN mkdir src \
    && touch README.md \
    && python -m pip install --no-cache-dir --only-deps ".[web,build]" \
    && groupadd --system filab \
    && useradd --system --gid filab --create-home filab

COPY README.md ./
COPY src/ ./src/

RUN python -m pip install --no-cache-dir --no-deps --no-build-isolation .

USER filab

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "filab.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
