#!/bin/bash
# Create migrations for any model changes
python3.11 manage.py makemigrations --no-input || true

# Apply migrations
python3.11 manage.py migrate --no-input

# Create groups and permissions if they don't exist
python3.11 manage.py criar_grupos || true

# Collect static files
python3.11 manage.py collectstatic --noinput --clear

# Run Django server on 0.0.0.0:5000
python3.11 manage.py runserver 0.0.0.0:5000
