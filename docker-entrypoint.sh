#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@darwix.com', 'adminpassword')
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec gunicorn darwix_project.wsgi:application --bind 0.0.0.0:8000