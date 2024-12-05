# Lemon Mall

## Project preparation
 - Architecture Design
```bash
Django + Jinja2 + Vue.js
```

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
 - Configure the project log
 - Configure front-end static files
 ```bash
 STATIC_URL = 'static/'
# Configure static file loading path
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
 ```

## User Registration
### Show user registration page
 - Create User Module Sub-Applications
```bash
$ cd ~/projects/lemon_mall/lemon_mall/lemon_mall/apps
$ python ../../manage.py startapp users
```
 - View the project guide package path
 ```bash
 print(sys.path)
 ```
  - Append package path
```bash
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'users'
]
```
 - Show user registration page
### User model class
 - Custom User Model Classes
 ```python
 from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    """Custom User Model Classes"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='mobile')

    class Meta:
        db_table = 'tb_users'    # Custom Table Names
        verbose_name = 'User'   # User
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
 ```
  - Migrate user model classes
  ```bash
  # Specify custom user model classes: Syntax: subapplication.User Model Classes
  AUTH_USER_MODEL = 'users.User'

  python3 manage.py makemigrations
  python3 manage.py migrate
  ```
### User registration business realization
 - front end
 ```bash
 Binding Vue data to user registration page
 User registration JS file to implement user interaction
 User interaction event implementation
 ```
 - back end
 ```bash
 Receive parameters
 Check parameters
 Save registration data
 Respond to registration results
 ```
 - state maintenance
 ```bash
 Write the unique identifying information of the authenticated user (e.g., user ID) to the current browser's cookie and the server's session.

 login(request, user)
 ``` 

 - Duplicate user name registration
 ```bash
 Use the user name to query whether the record corresponding to the user name exists, if it exists, it means duplicate registration, on the contrary, there is no duplicate registration.

 axios:
 Handling user interactions
 Collecting request parameters
 Preparing the request address
 Sending an asynchronous request
 Getting server response
 Controlling the display of the interface
 ```


## License

[MIT](https://choosealicense.com/licenses/mit/)