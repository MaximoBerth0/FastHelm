# syntax=docker/dockerfile:1
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install "poetry>=2.0,<3.0"

WORKDIR /app

# install runtime deps first so this layer is cached unless deps change
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

# the importable package + the demo app
COPY fasthelm ./fasthelm
COPY example ./example

EXPOSE 8000
CMD ["uvicorn", "example.app:app", "--host", "0.0.0.0", "--port", "8000"]
