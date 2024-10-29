FROM python:3.12-slim-bullseye AS builder

WORKDIR /app

## Install poetry
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 -

## generate requirements.txt
COPY pyproject.toml poetry.lock ./
RUN /root/.local/bin/poetry export --format=requirements.txt --output=requirements.txt

# Build the final image
FROM python:3.12-slim-bullseye

WORKDIR /app

## requirements
COPY --from=builder /app/requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt


WORKDIR /app/
COPY ip_reputation_indexer/ .

## create user
RUN useradd -m app
RUN chown -Rv app:app /app
USER app

## run
CMD ["python", "__main__.py"]