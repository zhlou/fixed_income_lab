FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN python -m pip install --no-cache-dir "pip>=26.2"

COPY requirements/base.txt requirements/web.txt requirements/build.txt ./requirements/

RUN python -m pip install --no-cache-dir \
        -r requirements/base.txt -r requirements/web.txt -r requirements/build.txt \
    && groupadd --system filab \
    && useradd --system --gid filab --create-home filab

COPY pyproject.toml MANIFEST.in README.md ./
COPY requirements/dev.txt ./requirements/
COPY src/ ./src/

RUN python -m pip install --no-cache-dir --no-deps --no-build-isolation .

USER filab

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "filab.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
