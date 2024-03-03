#!/bin/sh

# python manage.py migrate --no-input
python manage.py collectstatic --no-input

gunicorn mcbackend.wsgi:application --bind 0.0.0.0:8000 --workers=4
