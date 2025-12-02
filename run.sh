#!/bin/bash
# Collect static files
python3.11 manage.py collectstatic --noinput --clear

# Run Django server on 0.0.0.0:5000
python3.11 manage.py runserver 0.0.0.0:5000
