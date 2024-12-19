# Celery's entrance
from celery import Celery

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lemon_mall.settings.dev'

# Creating a Celery Instance
celery_app = Celery('lemon')

# Load Configuration
celery_app.config_from_object('celery_tasks.config')

# Registration Task
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])