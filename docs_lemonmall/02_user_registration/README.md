# 2. User Registration
## 2.1. Show user registration page
```bash
cd ~/projects/lemon_mall/lemon_mall/lemon_mall/apps
python3 ../../manage.py startapp users
```
 - Append package path
```python
# settings/dev.py
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))  # add new path


INSTALLED_APPS = [
    ...,
    'users'
]
```
```html
<!-- register.html -->
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    <title>LemonMall Register</title>
    <link rel="stylesheet" type="text/css" href="{{ static('css/reset.css') }}">
    <link rel="stylesheet" type="text/css" href="{{ static('css/main.css') }}">
</head>
```
 - Define the user registration view
```python
# apps/users/views.py
from django.views import View
from django.shortcuts import render

class RegisterView(View):
    """User Registration"""

    def get(self, request):
        """Provide user registration page"""
        return render(request, 'register.html')
```
- Define user registration routes
```python
# lemon_mall/urls.py
urlpatterns = [
    # users
    re_path(r'^', include('users.urls', namespace='users'))
]
```
```python
# users/urls.py
urlpatterns = [
    # User Registration: reverse(users:register) == '/register/'
    re_path(r'^register/$', views.RegisterView.as_view(), name='register'),
]
```
## 2.2 User model class
```python
# users/models.py
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
```python
# settings/dev.py
AUTH_USER_MODEL = 'users.User'
```
 - migrate
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
## 2.3 User registration business realization
```python
class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # Receive parameters
        username = request.POST.get('username')
        ...
        # Check parameters
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('Lack of mandatory parameters')
        ...
        # Save registration data
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': 'Failed to register'})

        # Respond result
        return http.HttpResponse('Successful registration, redirect to homepage.')
```
 - register.html
```html
<form method="post" class="register_form" @submit="on_submit" v-cloak>
    {{ csrf_input }}
    ...
</form>

<script type="text/javascript" src="{{ static('js/vue-2.5.16.js') }}"></script>
<script type="text/javascript" src="{{ static('js/axios-0.18.0.min.js') }}"></script>
```
 - register.js
```js
...
```
 - Create homepage ad app
```bash
cd ~/projects/lemon_project/lemon_mall/lemon_mall/apps
python ../../manage.py startapp contents
```
```python
# contents/views.py
class IndexView(View):

    def get(self, request):
        return render(request, 'index.html')
```
```python
# lemon_mall/urls.py
urlpatterns = [
    re_path(r'^', include('contents.urls', namespace='contents'))
]
```
```python
# contents/urls.py
urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
]
```
```python
# users/views.py
class RegisterView(View):
    ...
    return redirect(reverse('contents:index'))
```
 - State maintenance
```python
# settings/dev.py
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"
```
 - login()
```python
try:
    user = User.objects.create_user(username=username, password=password, mobile=mobile)
except DatabaseError:
    return render(request, 'register.html', {'register_errmsg': '注册失败'})

# Realization of state retention
login(request, user)

return redirect(reverse('contents:index'))
```
 - Duplicate registration of username (cell phone)
```python
class UsernameCountView(View):

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'count': count})
```
```python
re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
```
```javascript
if (this.error_name == false) {
  let url = '/usernames/' + this.username + '/count/';
  axios.get(url,{
    responseType: 'json'
  })
    .then(response => {
      if (response.data.count == 1) {
        this.error_name_message = '用户名已存在';
        this.error_name = true;
      } else {
        this.error_name = false;
      }
    })
    .catch(error => {
      console.log(error.response);
    })
}
```
## 2.4 State maintenance
```python
# Save registration data
try:
    user = User.objects.create_user(username=username, password=password, mobile=mobile)
except DatabaseError:
    return render(request, 'register.html', {'register_errmsg': 'Registration Failure'})

# Log in users for stateful retention
login(request, user)

# Respond to registration results
return redirect(reverse('contents:index'))
```
## 2.5 Duplicate registration of user name/mobile phone number
Core Idea: Use the user name to query whether the record corresponding to the user name exists, if it exists, it means duplicate registration, and vice versa, there is no duplicate registration.
```python
class UsernameCountView(View):
    ...

class MobileCountView(View):
    ...
```
## 2.6 Logical summary
### 2.6.1 Frontend(Vue)
 - Import Vue.js library and ajax request library
 - Prepare div box tags
 - Prepare js files
 - Html page to bind variables, events, etc.
 - Define variables, events, etc. in js file
### 2.6.2 Backend
 - Business logic analysis
 - Interface design and definition
 - Receive and check parameters
 - Realization of the main business logic
 - Response results