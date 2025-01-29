# 5. User center
## 5.1 Basic User Information
```python
# users/model.py
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='Mobile number')
    email_active = models.BooleanField(default=False, verbose_name='Email Verification Status')

    class Meta:
        db_table = 'tb_users'
        verbose_name = 'User'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
```
```python
class UserInfoView(LoginRequiredMixin, View):

    def get(self, request):

        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context=context)
```
## 5.2 Add and verify mailboxes
 - Add Mailbox
```python
# users/view.py
class EmailView(LoginRequiredJSONMixin, View):
    def put(self, request):
        ...
        request.user.email = email
        request.user.save()
        ...
```
 - Send Email Verification Email
```python
# celery_tasks/email/tasks.py
from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app


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
        raise self.retry(exc=e, max_retries=3)
```
```python
# celery_tasks/main.py
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
```
```python
# users/view.py
class EmailView(LoginRequiredJSONMixin, View):
    def put(self, request):
        ...
        request.user.email = email
        request.user.save()
        ...
        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)
```
```bash
celery -A celery_tasks.main worker -l info
```
```python
def generate_verify_email_url(user):
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url
```
 - Verify Email
```python
def check_verify_email_token(token):
    """
    Verify token and extract user
    :param token: Result after signing user information
    :return: user, None
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user
```
```python
class VerifyEmailView(View):
    ...
    token = request.GET.get('token')
    user = check_verify_email_token(token)
    if not user:
        return http.HttpResponseForbidden('Invalid token')
    user.email_active = True
    user.save()
    ...
    return redirect(reverse('users:info'))
```
## 5.3 Delivery address
```python
class AddressView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'user_center_site.html')
```
```python
class Area(models.Model):
    name = models.CharField(max_length=20)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True)

    class Meta:
        db_table = 'tb_areas'

    def __str__(self):
        return self.name
```
```bash
mysql -h127.0.0.1 -ualex -p123456abcdefg lemon_mall < areas.sql
```
```python
class AreasView(View):
    ...
```
```python
from django.core.cache import cache

class AreasView(View):

    def get(self, request):
        area_id = request.GET.get('area_id')

        if not area_id:
            province_list = cache.get('province_list')

            if not province_list:
                ...
                cache.set('province_list', province_list, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            sub_data = cache.get('sub_area_' + area_id)

            if not sub_data:
                ...
                cache.set('sub_area_' + area_id, sub_data, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
```
## 5.4 Change address
```python
class ChangePasswordView(LoginRequiredJSONMixin, View):
    ...
```