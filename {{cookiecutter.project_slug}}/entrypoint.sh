#!/bin/sh

cd "$(dirname "$0")"

{% if "django" in cookiecutter.extra_packages -%}

if [ "$DATABASE_URL" = "" ]; then
    echo DATABASE_URL not set, aborting.
    exit 1
fi

python manage.py migrate --check
if [ $? -ne 0 ]; then
    echo running migrations before starting app
    python manage.py migrate
fi

gunicorn -w ${WORKERS:-1} core_sim.wsgi --access-logfile - --bind 0.0.0.0:8000

{% else -%}
/bin/sleep 100000
{% endif -%}
