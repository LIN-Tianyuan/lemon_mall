# 1. Project preparation
## 1.1 Introduction to the project
Project Development Model:
 - Frontend: Vue.js

 - Backend: Django + Jinja2

Project Operation Mechanism:
 - Proxy service: Nginx server (reverse proxy)
 - Static service: Nginx server (static home page, product detail page, ...)
 - Dynamic service: uwsgi server (business scenarios of lemonmall)
 - Backend Services: MySQL, Redis, Celery, RabbitMQ, Docker, FastDFS, Elasticsearch, Crontab
 - External interfaces: Twilio, QQ Internet, Alipay

## 1.2 Project creation and configuration
 - Create Project
```bash
python3 -m venv lemonmall-env
source lemonmall-env/bin/activate
pip3 install django

django-admin startproject lemon_mall
python3 manage.py runserver
```
 - Configure the development environment
```python
# manage.py
import os
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lemon_mall.settings.dev')
    ...
```
 - Configure the Jinja2 template engine
```bash
pip3 install Jinja2
```
```python
# settings/dev.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2', # Configure the jinja2 template engine
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Configure the path for loading template files
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # Supplementary Jinja2 template engine environment
            'environment': 'lemon_mall.utils.jinja2_env.jinja2_environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```
```python
# utils/jinja2_env.py
from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def jinja2_environment(**options):
    """jinja2 environment"""
    # Creating Environment Objects
    env = Environment(**options)
    # Custom syntax: {{static('relative path to static file')}} {{url('namespace of route')}}
    env.globals.update({
        'static': staticfiles_storage.url,  # Get the prefix of a static file
        'url': reverse, # inverse resolution
    })
    # Return the environment object
    return env

"""
Make sure we can use statements like {{ url('') }} {{ static('') }} from the template engine
"""
```
 - Configure the MySQL Database
```bash
# Ubuntu install mysql 8.0
## install
sudo apt update
sudo apt install mysql-server

## check the system status
sudo systemctl status mysql

## root login
sudo mysql

## External program login
GRANT ALL PRIVILEGES ON *.* TO 'administrator'@'localhost' IDENTIFIED BY 'very_strong_password';

## Modify MySQL Configuration to Allow Remote Connections
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0
sudo systemctl restart mysql
```
```bash
show databases; 

create database lemonmall charset=utf8; # Create a new MySQL database

create user alex identified by '123456abcdefg'; # Create a new MySQL user

grant all on lemonmall.* to 'alex'@'%'; # Authorizing alex users to access the lemon_mall database

flush privileges; # Refresh privileges after authorization ends
```
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.112.134',
        'PORT': 3306,
        'USER': 'alex',
        'PASSWORD': '123456abcdefg',
        'NAME': 'lemonmall'
    }
}
```
```bash
pip3 install PyMySQL
```
```python
# __init__.py
from pymysql import install_as_MySQLdb

install_as_MySQLdb()
```
 - Configure the Redis Database
```bash
# Ubuntu install redis
## install
sudo apt update
sudo apt install redis-server

## check the system status
sudo systemctl status redis-server

## Modify Redis Configuration to Allow Remote Connections
sudo nano /etc/redis/redis.conf
bind 0.0.0.0 ::1
sudo systemctl restart redis-server

## Test Remote Connection
# redis-cli -h <REDIS_IP_ADDRESS> ping
redis-cli -h 192.168.112.134 ping # PONG
```
```bash
pip3 install django-redis
```
```bash
# Configure the Redis Database
# dev.py
CACHES = {
    "default": { 
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.112.134:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": { 
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.112.134:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"
```
```text
default:
- The default Redis configuration item, using Redis library 0.

session:
- Stateful Redis configuration item, using Redis library 1.

SESSION_ENGINE:
- Modify the `session storage mechanism` to use Redis for saving.

SESSION_CACHE_ALIAS:
- Use a Redis configuration item named "session" to store `session data`.
```
 - Configure the project log
```bash
# Configure the Redis Database
# settings/dev.py
LOGGING = { ...
  'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/lemonmall.log')
  ...}
```
```text
The way to create a logger:
logger = logging.getLogger('django')

Logger usage:
logger.info('Test logging module info')
```
 - Configure front-end static files
 ```bash
# Specify static file load path
# settings/dev.py

STATIC_URL = 'static/'
# Configure static file loading path
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
 ```