# Celery's entrance
from celery import Celery

# Creating a Celery Instance
celery_app = Celery('lemon')

# Load Configuration
celery_app.config_from_object('celery_tasks.config')

# Registration Task
celery_app.autodiscover_tasks(['celery_tasks.sms'])