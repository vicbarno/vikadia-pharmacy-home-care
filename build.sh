#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py shell -c "from core.models import Product; from django.core.management import call_command; call_command('loaddata', 'core/fixtures/products.json') if Product.objects.count() == 0 else None"