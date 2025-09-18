# stage 1: build
FROM python:3.12-bookworm AS builder
LABEL org.opencontainers.image.source=https://github.com/owner/{{ cookiecutter.project_slug }}
LABEL org.opencontainers.image.description="{{ cookiecutter.project_short_description }}"

# access token for private repos
ARG PAT

# install packages needed by python packages
RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# create virtualenv and install dependencies
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

RUN if [ -n "$PAT" ]; then \
        echo "Configuring Git with PAT for private repo access..."; \
        git config --global url."https://x-access-token:${PAT}@github.com/sloppycoder/".insteadOf "https://github.com/sloppycoder/"; \
    else \
        echo "No PAT provided. Skipping Git configuration for private repos."; \
    fi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# stage 2: runtime
FROM python:3.12-slim-bookworm

# create user
RUN addgroup --system app && adduser --system --group app
USER app
WORKDIR /app

# copy virtualenv from builder
COPY --chown=app:app --from=builder /app/venv /app/venv
# copy application code. update .dockerignore to files that shouldn't be copied
COPY --chown=app:app . .

ENV PATH="/app/venv/bin:$PATH"
CMD  ["/bin/sh", "/app/entrypoint.sh"]

{% if "fastapi" in cookiecutter.extra_packages -%}
EXPOSE 8000
{% endif -%}
