# Lemon Mall

## [6.Product](./docs/06_product.md)

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
        'HOST': '127.0.0.1',
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
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": { # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
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

## Verification code
### graphical code
 - Captcha Expansion Pack
 ```bash
 pip install Pillow
 ```
 - Preparing the Redis Database
 ```bash
 "verify_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
    }
}
 ```
 - Graphical CAPTCHA backend logic implementation
 ```python
 class ImageCodeView(View):
    """graphical captcha"""

    def get(self, request, uuid):
        """
        :param uuid: Generic Unique Identifier, which uniquely identifies the user to whom the graphical CAPTCHA belongs
        :return: image/jpg
        """
        # Implementing the main business logic: generating, saving, and responding to graphical CAPTCHAs
        # Generate
        text, image = captcha.generate_captcha()
        # Save
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.setex('key', 'expires', 'value')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # Responding to results
        return http.HttpResponse(image, content_type='image/jpg')
 ```
  - Graphical CAPTCHA front end logic
  ```bash
  mounted() { // It will be called after the page loads
    // Generate graphical codes
    this.generate_image_code();
    },
  methods: {  // Defining and implementing event methods
    // Methods for generating graphical codes: The idea of encapsulation to facilitate code reuse
    generate_image_code() {
        this.uuid = generateUUID();
        this.image_code_url = '/image_codes/' + this.uuid + '/';
    }
    // Verify graphic code
  check_image_code() {
    if (this.image_code.length != 4) {
        this.error_image_code_message = "Please fill in the graphic code";
        this.error_image_code = true;
    } else {
        this.error_image_code = false;
    }
  }
  }
 ```
### SMS verification code
```bash
Saving the SMS CAPTCHA is to prepare for registration.
In order to avoid users using graphical CAPTCHA to test maliciously, the back-end extracts the graphical CAPTCHA and then immediately deletes the graphical CAPTCHA.
Django does not have the ability to send SMS, so we use the third-party Twilio SMS platform to help us send SMS verification code.
```
 - backend
 ```python
 class SMSCodeView(View):
    """SMS verification code"""
    def get(self, request, mobile):
        # Receiving parameters
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # Calibration parameters
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('Missing mandatory parameters')
        # Extract graphical captcha
        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Graphical Code no longer works'})
        # Remove graphical captcha
        redis_conn.delete('img_%s' % uuid)
        # Compare graphical CAPTCHAs
        image_code_server = image_code_server.decode()  # Convert bytes to strings and compare
        if image_code_client.lower() != image_code_server.lower():  # Lowercase and compare
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Incorrectly entered graphical verification code'})
        # Generate SMS verification code: Random 6-digit number
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)   # Manual output logging of SMS verification codes
        # Save SMS Verification Code
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # Send SMS Verification Code
        # CCP().send_template_sms(mobile, f"Your verification code is {sms_code}. Please enter it correctly within 5 minutes.")
        # Response results
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'Send SMS successfully'})
 ```

 - front end
 ```bash
 Avoid sending frequent SMS verification codes
 ```
 ```bash
 send_sms_code() {
    // Avoid malicious users from frequently clicking on the Get SMS Verification Code tab
    if (this.send_flag == true) {
        return;
    }
    this.check_mobile();
    this.check_image_code();
    if (this.error_mobile == true || this.error_image_code == true) {
        this.send_flag = false;
        return;
    }
    this.send_flag = true;
    // Check data: mobile, image_code
    let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
        axios.get(url, {
            responseType: 'json'
        })
        .then(response => {
            if (response.data.code == '0') {
                // Show countdown 60 seconds
                let num = 60;
                let t = setInterval(() => {
                        if (num == 1) {    // The countdown is about to end.
                        clearInterval(t); // Stopping the execution of a callback function
                        this.sms_code_tip = 'Get code';  // Restore sms_code_tip hint text
                        this.generate_image_code();  // Re-generate the graphical CAPTCHA
                        this.send_flag = false;
                        } else {   // It's counting down.
                        num -= 1;
                        this.sms_code_tip = num + 's';
                        }
                }, 1000)
            } else {
                if (response.data.code == '4001') { // Graphical CAPTCHA error
                    this.error_image_code_message = response.data.errmsg;
                    this.error_image_code = true;
                }
                this.send_flag = false;
            }
        })
        .catch(error => {
            console.log(error.response);
            this.send_flag = false;
        })
},
 ```
  - pipeline operations on redis databases
  ```bash
  If the Redis server needs to handle multiple requests at the same time, coupled with network latency, then the server is underutilized and less efficient.
  Solution: pipeline

  pipleline:
  You can send multiple commands at once and return the results at once after execution.
The pipeline reduces round-trip latency by reducing the number of times the client communicates with Redis.
  ```
```python
# Create a redis pipeline
pl = redis_conn.pipeline()
# Adding commands to the queue
# Save SMS Verification Code
pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
# Save the mark for sending SMS verification code
pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
# Execute
pl.execute()
```
### Asynchronous program: Celery
```bash
Problem:
The code is executed synchronously from top to bottom.
Sending SMS is time consuming operation. If the SMS is blocked, the user response will be delayed.
The delayed response causes a delay in the countdown of the user interface.

Solution:
Send SMS asynchronously
Send SMS and response are executed separately to decouple sending SMS from the main business.
```
 - producer-consumer design pattern
```bash
In order to decouple sending SMS from the main business, introduce the producer-consumer design pattern.
It is one of the most commonly used decoupling methods, looking for a middleman (broker) to build a bridge to ensure that the two businesses are not directly related.

producer - broker - consumer

Producer generates messages, caches them into a message queue, consumer reads the messages in the message queue and executes them.
A send SMS message is generated by lemonmall, cached into a message queue, and the consumer reads the send SMS message in the message queue and executes it.
```
 - Celery
 ```bash
 A simple, flexible and reliable distributed system for processing large numbers of messages that can run on one or more machines.
A single Celery process can handle millions of tasks per minute.
Communication is via messages, which are coordinated between clients and consumers using message queues (brokers).

 pip3 install Celery
 ```
 ```python
 # Creating a Celery instance and loading the configuration
 # celery_tasks.main
# Celery's entrance
from celery import Celery

# Creating a Celery Instance
celery_app = Celery('lemon')

# Load Configuration
celery_app.config_from_object('celery_tasks.config')

# Registration Task
celery_app.autodiscover_tasks(['celery_tasks.sms'])

# celery_tasks.config.py
broker_url= "redis://127.0.0.1/10"


# celery_tasks.sms.tasks.py
# Define the task
from celery_tasks.sms.twilio.send_sms import CCP
from celery_tasks.main import celery_app


# Decorating asynchronous tasks with decorators ensures that celery recognizes the task
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """Asynchronous Tasks for Sending SMS CAPTCHA"""
    send_result = CCP().send_template_sms(mobile, f"Your verification code is {sms_code}. Please enter it correctly within 5 minutes.")
    return send_result
 ```
 ```bash
 Start the Celery service

$ cd ~/lemon_mall/lemon_mall
$ celery -A celery_tasks.main worker -l info
 ```
 ```python
 # Calling the Send SMS task
 ccp_send_sms_code.delay(mobile, sms_code)
 ```
## User login
### Account Login
 - Username login
 ```bash
 class LoginView(View):
    """user login"""
    def get(self, request):
        """Provide user login page"""
        return render(request, 'login.html')

    def post(self, request):
        """Implement user login logic"""
        # Receiving parameters
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # Calibration parameters
        if not all([username, password]):
            return http.HttpResponseForbidden('Absence of mandatory parameters')
        # Determine if the username is 5-20 characters long.
        if not re.match(r'^[+a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('Please enter the correct username or cell phone number')
        # Determine if the password is 8-20 digits.
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('Password minimum 8 digits, maximum 20 digits')
        # Authenticated Users: Use the account to check if the user exists, and if the user exists, then check if the password is correct
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': 'Incorrect account number or password'})
        # Status Hold
        login(request, user)
        # Use remembered to determine the state retention period (to implement remembered login)
        if remembered != 'on':
            # No login is remembered: the state is kept until the end of the browser session and then destroyed.
            request.session.set_expiry(0)   # The unit is seconds.
        else:
            # Remember to log in: status is maintained for two weeks: Default is two weeks.
            request.session.set_expiry(None)
        # Response Result: Redirect to home page
        return redirect(reverse('contents:index'))
 ```
 - Login multi-compte
 ```bash
 Django comes with a user authentication backend that uses usernames to realize user authentication by default.

User authentication backend location: django.contrib.auth.backends.ModelBackend

If you want to realize that both username and mobile number can authenticate users, you need to customize the user authentication backend.

Steps to customize the user authentication backend

Create a new utils.py file in the users application.
Create a new class that inherits from ModelBackend.
Override the authenticate() method.
Query the user using the username and cell phone number respectively
Return the queried user instance

AUTHENTICATION_BACKENDS = ['users.utils.UsernameMobileAuthBackend']

class UsernameMobileAuthBackend(ModelBackend):...
 ```
  - Home User Name Display
 ```bash
 Vue reads a cookie to render user information
 Username written to cookie
 Vue rendering home page username

response = redirect(reverse('contents:index'))
# To enable the display of username information in the upper right corner of the home page, we need to cache the username in a cookie
response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
# Response Result: Redirect to home page
return response
 ```

  - Log out
 ```bash
 Clearing session information

 logout(request)


The core idea of logging out of login is to clean up the status hold information cached at login.
Since the username in the home page is read from a cookie. So when log out, need to clear the username from the cookie.
 ```

 - Determine whether a user is logged in or not
```bash
Access to the User Center is allowed when the user is logged in.
If the user is not logged in, access to the User Center is not allowed and the user is directed to the login screen.

LOGIN_URL = '/login/'

class LoginView(View):
    ...
    # Take out the next
    next = request.GET.get('next')
    if next:
        # Redirect to next
        response = redirect(next)
    else:
        # Redirect to home page
        response = redirect(reverse('contents:index'))

class UserInfoView(LoginRequiredMixin, View):
    """User center"""
    def get(self, request):
        """Provide user center page"""
        return render(request, 'user_center_info.html')
```
```bash
Determining whether a user is logged in or not is still implemented using stateful hold messages.
Many interfaces in the project require the user to be logged in to access them, so for coding convenience, we encapsulate the operation of determining the user's login into a decorator.
The role of the next parameter is to make it easier for the user to enter the login page from where he/she is and return to where he/she is after successfully logging in.
```
### QQ Login
 - QQ Login Development Documentation
 - Define the QQ login model class
    - Define the model class base class
    ```python
    from django.db import models

    class BaseModel(models.Model):
        """Supplemental fields for model classes"""

        create_time = models.DateTimeField(auto_now_add=True, verbose_name="create time")
        update_time = models.DateTimeField(auto_now=True, verbose_name="update time")

        class Meta:
            abstract = True  # It means that it is an abstract model class, used for inheritance, and the tables of BaseModel will not be created during database migration.
    ```
    - Define the QQ login model class
    ```bash
    python3 ../../manage.py startapp oauth
    ```
    ```python
    from django.db import models
    from lemon_mall.utils.models import BaseModel

    # Create your models here.

    class OAuthQQUser(BaseModel):
        """QQ Login User Data"""
        user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='user')
        openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

        class Meta:
            db_table = 'tb_oauth_qq'
            verbose_name = 'QQ Login User Data'
            verbose_name_plural = verbose_name
    ```
    - Migrating the QQ login model class
    ```bash
    $ python3 manage.py makemigrations
    $ python3 manage.py migrate
    ```
 - QQ Login Tool 
 - OAuth2.0 authentication to get openid
 - Handling of whether an openid is bound to a user or not
 - Openid Binding User Implementation

 ## User center
 ### Basic User Information
 ```bash
User model supplemented with email_active field
Query and render basic user information
Add mailbox
Send mailbox validation email
Validate mailbox
 ```
 - Query and render basic user information
 ```bash
 User model supplement email_active field
 ```
 ```python
 class User(AbstractUser):
    """Custom User Model Classes"""
    mobile = models.CharField(max_length=15, unique=True, verbose_name='Mobile')
    email_active = models.BooleanField(default=False, verbose_name='Email Verification Status')

    ...
 ```
 ```bash
 $ python manage.py makemigrations
$ python manage.py migrate
 ```
```bash
Querying basic user information
```
```python
class UserInfoView(LoginRequiredMixin, View):
    """User center"""
    def get(self, request):
        """Provide user center page"""
        # If LoginRequiredMixin determines that the user is logged in, then request.user is the logged-in user object
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)
```
```bash
Rendering basic user information
```
```javascript
<script type="text/javascript">
    let username = "{{ username }}";
    let mobile = "{{ mobile }}";
    let email = "{{ email }}";
    let email_active = "{{ email_active }}";
</script>
<script type="text/javascript" src="{{ static('js/common.js') }}"></script>
<script type="text/javascript" src="{{ static('js/user_center_info.js') }}"></script>

data: {
    username: username,
    mobile: mobile,
    email: email,
    email_active: email_active,
},
```
### Add and verify email
```python
class EmailView(LoginRequiredJSONMixin, View):
    """Add email"""
    def put(self, request):
        # Receive parameter
        json_str = request.body.decode()    # The body type is bytes
        json_dict = json.loads(json_str)
        email = json_dict.get('email')
        # Check parameter
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('The parameter email is incorrect')
        # Save the user's incoming mailbox into the email field of the database user
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Failed to add mailbox'})
        # Response result
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
```
```bash
Determine whether the user is logged in and return JSON
Only when the user is logged in can be allowed to bind the mailbox.
At this time, the data type of front-end and back-end interaction is JSON, so need to determine whether the user is logged in and return JSON to the user.
```
```python
# utils/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http

from lemon_mall.utils.response_code import RETCODE

class LoginRequiredJSONMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        """Direct Response JSON Data"""
        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': 'User is not logged in'})
```
#### Configuring Django to send emails
```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # Specify mail backend
EMAIL_HOST = 'smtp.gmail.com' # Email Hosting
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'sgsgkxkx@gmail.com' # Authorized mailboxes
EMAIL_HOST_PASSWORD = '' # Password obtained during mailbox authorization, not the registered login password
EMAIL_FROM = 'LemonMall<sgsgkxkx@gmail.com>' # Sender's letterhead
```
#### Send Email Verification Email
Sending email verification emails is a time-consuming operation that can't block the response from the lemon mall, so you need to send emails asynchronously.
Continue to use Celery to implement the asynchronous task.
```python
# email/tasks.py
# bind: It is guaranteed that the task object will be automatically passed as the first argument
# name: asynchronous task alias
# retry_backoff: Exception Auto-Retry Interval n times(retry_backoff x 2^(n-1))s
# max_retries: Maximum number of automatic retries for exceptions
@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """Define tasks for sending validation emails"""
    # send_mail('title', 'message', 'sender', 'receiver list', 'rich text(html)')

    subject = "Lemon Mall Email Verification"
    html_message = '<p>Dear users, </p>' \
                '<p>Thank you for using Lemon Mall.</p>' \
                '<p>Your e-mail address is: %s . Please click on this link to activate your mailbox:</p>' \
                '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        # trigger an error retry: Maximum 3 tentatives
        raise self.retry(exec, max_retries=3)
```
For the asynchronous task of sending emails, we use Django configuration files.
So we need to modify celery's startup file main.py.
In it, specify the Django configuration files that celery can read.
Finally, register the newly added email task.
```python
# main.py
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lemon_mall.settings.dev'

# Creating a Celery Instance
celery_app = Celery('lemon')

# Load Configuration
celery_app.config_from_object('celery_tasks.config')

# Registration Task
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
```
Calling the Send Mail asynchronous task
```python
# Save the user's incoming mailbox into the email field of the database user
try:
    request.user.email = email
    request.user.save()
except Exception as e:
    logger.error(e)
    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Failed to add mailbox'})
# Send Email Verification Email
verify_url = generate_verify_email_url(request.user)
send_verify_email.delay(email, verify_url)

# Response result
return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
```
Start Celery
```bash
$ celery -A celery_tasks.main worker -l info
```
#### Generate email verification link
Define a method for generating email verification links
```python
def generate_verify_email_url(user):
    """Generate email activation link"""
    s = Serializer(settings.SECRET_KEY, salt='email-confirm')
    data = {'user_id': user.id, 'email': user.email}    # Currently logged in user
    token = s.dumps(data)
    return settings.EMAIL_VERIFY_URL + '?token=' + token

EMAIL_VERIFY_URL = 'http://www.lemonmall.site:8000/emails/verification/'

verify_url = generate_verify_email_url(request.user)
send_verify_email.delay(email, verify_url)
```
#### Authentication Mailbox Backend Logic
The heart of validating an email: it's all about setting the user's email_active field to True.
```python
def check_verify_email_token(token):
    """Deserialize token, get user"""
    s = Serializer(settings.SECRET_KEY, salt='email-confirm')
    try:
        data = s.loads(token, max_age=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    except BadData:
        return None
    else:
        # Get user_id and email from data
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


class VerifyEmailView(View):
    """verification"""
    def get(self, request):
        # Receive parameter
        token = request.GET.get('token')
        # Check parameter
        if not token:
            return http.HttpResponseForbidden('Missing Token')
        # Extract user info from token  user_info => user
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseBadRequest('Invalid token')
        # Setting the user's email_active field to True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('Failed to activate mailbox')
        # Response Result: Redirect to User Center
        return redirect(reverse('users:info'))
```
### Delivery address
```bash
python3 ../../manage.py startapp areas
```
#### Province city district
```python
from django.db import models

# Create your models here.
class Area(models.Model):
    """Province city district"""
    name = models.CharField(max_length=20, verbose_name='Name')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='Upper administrative subdivision')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = 'Provincial City District'
        verbose_name_plural = 'Provincial City District'

    def __str__(self):
        return self.name
```
```bash
A self-associated field has a foreign key pointing to itself, so models.ForeignKey('self')
Syntax for querying child data using related_name specification parent:
Default Area model class object.area_set syntax
related_name='subs':
Now Area model class object.subs syntax
```
```bash
python manage.py makemigrations
python manage.py migrate
```
```python
class AddressView(LoginRequiredMixin, View):
    """User Delivery Address"""
    def get(self, request):
        return render(request, 'user_center_site.html')
```
```python
class AreasView(View):
    ...
```
 - Cache city and province data
```python
from django.core.cache import cache
...
if not area_id:  
    province_list = cache.get('province_list')
else:
    sub_data = cache.get('sub_area_' + area_id)
```
## Notice
```bash
git:
git rm -r --cached .
git reset HEAD~

migrate:
python manage.py makemigrations
python manage.py migrate

celery -A celery_tasks.main worker -l info

# send gmail
import certifi, os
os.environ['SSL_CERT_FILE'] = certifi.where()

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # Specify mail backend
EMAIL_HOST = 'smtp.gmail.com' # Email Hosting
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'sgsgkxkx@gmail.com' # Authorized mailboxes
EMAIL_HOST_PASSWORD = '' # Password obtained during mailbox authorization, not the registered login password
EMAIL_FROM = 'LemonMall<sgsgkxkx@gmail.com>' # Sender's letterhead

# import data
mysql -h (database ip address) -u (database username) -p (database password) (database) < (areas.sql)
mysql -h127.0.0.1 -uroot -pmysql lemon_mall < areas.sql

```
### Virtual Machine Configuration (Ubuntu)
 - Install vmware
```bash

```
 - Install docker
```bash
sudo apt update
sudo apt install docker.io docker-compose
docker -v
```
 - Transfer of documents(FileZilla)
```bash
host: 192.168.1.15 # IP address of the virtual machine
username: lin # User name for logging into the virtual machine
password: ****** # Password for logging into the virtual machine

# Error: Could not connect to server
sudo apt update
sudo apt install openssh-server

## Check system's status
sudo systemctl status ssh

# Error: Could not connect to server
sudo apt update
sudo apt install vsftpd

## Check system's status
sudo systemctl status vsftpd

## Start service
sudo systemctl start vsftpd
sudo systemctl enable vsftpd

# Error: Critical file transfer error
sudo nano /etc/vsftpd.conf

write_enable=YES
local_enable=YES
```


## License

[MIT](https://choosealicense.com/licenses/mit/)