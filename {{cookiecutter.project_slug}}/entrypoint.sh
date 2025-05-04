#!/bin/sh

cd "$(dirname "$0")"

{% if "tortoise-orm" in cookiecutter.extra_packages -%}
if [ "$DATABASE_URL" = "" ]; then
    echo DATABASE_URL not set, aborting.
    exit 1
fi
{% endif -%}


{% if "aerich" in cookiecutter.extra_packages -%}
aerich upgrade
{% endif -%}

{% if "fastapi" in cookiecutter.extra_packages -%}
uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-1}
{% else -%}
/bin/sleep 100000
{% endif -%}
