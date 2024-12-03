# Lemon Mall

## Project preparation

 - Create Project

```bash
python3 -m venv lemonmall-env
source lemonmall-env/bin/activate
pip3 install django

django-admin startproject lemon_mall
python manage.py runserver
```

 - Configure the development environment
 - Configure the Jinja2 template engine
 ```bash
 pip3 install Jinja2

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
 ```
 - Configure the MySQL Database
```bash
show databases; 

create database lemonmall charset=utf8; # Create a new MySQL database

create user alex identified by '123456'; # Create a new MySQL user

grant all on lemonmall.* to 'alex'@'%'; # Authorizing alex users to access the lemon_mall database

flush privileges; # Refresh privileges after authorization ends
```

```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.1.14',
        'PORT': 3306,
        'USER': 'alex',
        'PASSWORD': '123456',
        'NAME': 'lemonmall'
    }
}
```

```bash
pip install PyMySQL

# __init__.py
from pymysql import install_as_MySQLdb


install_as_MySQLdb()
```
 - Configure the Redis Database
```bash
pip3 install django-redis
```
```bash
CACHES = {
    "default": { # default
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.1.14:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": { # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.1.14:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"
```
 - Configuring the project log
 - 


## License

[MIT](https://choosealicense.com/licenses/mit/)