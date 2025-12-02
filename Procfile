web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn nexus.wsgi --bind 0.0.0.0:$PORT
