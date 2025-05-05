#!/bin/sh

cd "$(dirname "$0")"

{% if "sqlmodel" in cookiecutter.extra_packages -%}
if [ "$SQLALCHEMY_DATABASE_URI" = "" ]; then
    echo SQLALCHEMY_DATABASE_URI not set, aborting.
    exit 1
fi
{% endif -%}

{% if "alembic" in cookiecutter.extra_packages -%}
if [ "$RUN_MIGRATE" = "Y" ]; then
    # Check for pending migrations
    current_migration=$(alembic current | awk '{print $1}')
    latest_migration=$(alembic heads | awk '{print $1}')

    if [ "$current_migration" != "$latest_migration" ]; then
        echo "Running migrations before starting app"
        alembic upgrade head
    fi
fi
{% endif -%}

{% if "fastapi" in cookiecutter.extra_packages -%}
uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-1}
{% else -%}
/bin/sleep 100000
{% endif -%}
