# Project preparation

## 1. Introduction to the project
### 1.1 Project Requirements Analysis
#### 1.1.1 Project Main Page Introduction
 - Home Ads
 - Register
 - Sign in
 - Personal Information
 - Shipping Address
 - Order
 - Modify Password
 - Product List
 - Product Search
 - Product Details
 - Shopping Cart
 - Checkout
 - Submit Order
 - Payment
 - Order Product Evaluation

#### 1.1.2 Project Main Modules
Module |Function
---|---|
Authentication |Graphical authentication, SMS authentication
User |Registration, Login, User Center
Third party login |QQ login
Home Ads |Home Ads
Commodity |Commodity list, commodity search, commodity details
Shopping cart |Shopping cart management, shopping cart merger
Order |Confirm order, submit order
Payment |Alipay payment, order evaluation
MIS system |Data statistics, user management, rights management, product management, order management

### 1.2 Project Architecture Design
#### 1.2.1 Project Development Model
Front-end and back-end are not separated, easy SEO.

Using Django + Jinja2 template engine + Vue.js to realize the front and back end logic.

#### 1.2.2 Project Operation Mechanism
Proxy service: Nginx server (reverse proxy)

Static service: Nginx server (static home page, product detail page, ...)

Dynamic services: uwsgi server (business scenarios of lemonmall)

Backend Services: MySQL, Redis, Celery, RabbitMQ, Docker, FastDFS, Elasticsearch, Crontab

External interfaces: Twilio, QQ Internet, Alipay

## 2. Project creation and configuration
### 2.1 Create Project

```bash
$ python3 -m venv lemonmall-env
$ source lemonmall-env/bin/activate
$ pip3 install django

$ django-admin startproject lemon_mall
$ python manage.py runserver
```

### 2.2 Configure the development environment
The environment of Lemon Mall project is divided into development environment and production environment.

 - Development environment: used for writing and debugging project code.
 - Production environment: used for project online deployment and operation.
#### 2.2.1 New Configuration File
1. Prepare the configuration file directory
 - Create a new package named `settings` as the configuration file directory
2. Prepare development and production environment configuration files
 - In the configuration package `settings`, create new development and production environment configuration files.
3. Prepare the development environment configuration contents
 - Copy the contents of the default configuration file settings.py to dev.py.

#### 2.2.2 Specify the development environment configuration file
```python
# manage.py
import os
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lemon_mall.settings.dev')
    ...
```

### 2.3 Configure the Jinja2 template engine
#### 2.3.1 Configure the Jinja2 template engine
```bash
pip3 install Jinja2
```

```bash
# dev.py
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

#### 2.3.2 Supplementary Jinja2 template engine environment
```python
# jinja2_env.py
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

### 2.4 Configure the MySQL Database
```bash
# Ubuntu install mysql 8.0
## install
$ sudo apt update
$ sudo apt install mysql-server

## check the system status
$ sudo systemctl status mysql

## root login
$ sudo mysql

## External program login
GRANT ALL PRIVILEGES ON *.* TO 'administrator'@'localhost' IDENTIFIED BY 'very_strong_password';

## Modify MySQL Configuration to Allow Remote Connections
$ sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0
$ sudo systemctl restart mysql
```
#### 2.4.1 Create a new MySQL database
```bash
show databases; 

create database lemonmall charset=utf8; # Create a new MySQL database

create user alex identified by '123456abcdefg'; # Create a new MySQL user

grant all on lemonmall.* to 'alex'@'%'; # Authorizing alex users to access the lemon_mall database

flush privileges; # Refresh privileges after authorization ends
```
#### 2.4.2 Configure the MySQL Database
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
#### 2.4.3 Installing the PyMySQL Extension Pack
```bash
$ pip3 install PyMySQL
```
 - In the `__init__.py` file in the project subdirectory of the same name
```python
# __init__.py
from pymysql import install_as_MySQLdb

install_as_MySQLdb()
```

### 2.5 Configure the Redis Database
```bash
# Ubuntu install redis
## install
$ sudo apt update
$ sudo apt install redis-server

## check the system status
$ sudo systemctl status redis-server

## Modify Redis Configuration to Allow Remote Connections
$ sudo nano /etc/redis/redis.conf
bind 0.0.0.0 ::1
$ sudo systemctl restart redis-server

## Test Remote Connection
# redis-cli -h <REDIS_IP_ADDRESS> ping
$ redis-cli -h 192.168.112.134 ping # PONG
```
```bash
$ pip3 install django-redis
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
default:
 - The default Redis configuration item, using Redis library 0.

session:
 - Stateful Redis configuration item, using Redis library 1.

SESSION_ENGINE:
 - Modify the `session storage mechanism` to use Redis for saving.

SESSION_CACHE_ALIAS:
 - Use a Redis configuration item named "session" to store `session data`.

### 2.6 Configure the project log
The logging of the Lemon Mall is done using the `logging` module.
#### 2.6.1 Project log
```bash
# Configure the Redis Database
# dev.py
LOGGING = { ...
  'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/lemonmall.log')
  ...}
```
#### 2.6.2 Use of Logger
```python
import logging

# Create a logger
logger = logging.getLogger('django')
# Output the logs
logger.debug('Testing logging module debug')
logger.info('Testing the logging module info') # ☆
logger.error('Testing logging module error')
```
#### 2.6.3 Git manages project logs
The log messages generated during the development process do not need to be managed and recorded by the code repository.

The `*.log` is already ignored by default in the ignore file generated when the code repository is created.

Issue:
 - The logs file directory needs to be logged and managed by the Git repository.
 - When all `*.logs` are ignored, the logs file directory is empty.
 - However, Git is not allowed to commit an empty directory to the repository.

Solution:
 - Create a `.gitkeep` file in the empty files directory and commit.

### 2.7 Configure front-end static files
 ```bash
# Specify static file load path
# dev.py

STATIC_URL = 'static/'
# Configure static file loading path
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
 ```
