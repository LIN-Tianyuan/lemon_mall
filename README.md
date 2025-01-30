# Lemon Mall
Front Office - Users
## Overview
Business Model: B2C

Development mode: No front-end and back-end separation

Frontend framework: Vue.js

Backend Framework: Django + Jinja2 template engine

Proxy service: Nginx server (reverse proxy)

Static services: Nginx server (static home page, product detail page, ...)

Dynamic services: uwsgi server (Lemonmall business scenario)

Backend Services: MySQL, Redis, Celery, RabbitMQ, Docker, FastDFS, Elasticsearch, Crontab

External interfaces: Twilio, QQ Internet, Alipay

## Usage environment


User: 
 - registration
   - CAPTCHA (Third Party Image Captcha)
   - Send SMS (Twilio、Celery)
   - Duplicate Account
   - Data saving
 - login
   - Forms Login (Multi-account login)
   - Third Party Login

Commodity:

Shopping cart:

Order:

Payment:



## [1. Project preparation](docs_lemonmall/01_project/README.md)

## [2. User registration](docs_lemonmall/02_user_registration/README.md)

## [3. Captcha](docs_lemonmall/03_captcha/README.md)

## [4. User login](docs_lemonmall/04_user_login/README.md)

## [5. User center](docs_lemonmall/05_user_center/README.md)
## [6. Product](docs_lemonmall/06_product/README.md)
## [7. Shopping cart](docs_lemonmall/07_shopping_cart/README.md)
## [8. Order](docs_lemonmall/08_order/README.md)
## [9. Payment](docs_lemonmall/09_payment/README.md)
## [10. Performance optimization](docs_lemonmall/10_performance_optimization/README.md)
## [Realization](docs_lemonmall/Realization/README.md)
## Notice
### 1. MySQL Datebase install
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
### 2. Redis Install
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
### 3. Git manages project logs
The log messages generated during the development process do not need to be managed and recorded by the code repository.

The `*.log` is already ignored by default in the ignore file generated when the code repository is created.

Issue:
- The logs file directory needs to be logged and managed by the Git repository.
- When all `*.logs` are ignored, the logs file directory is empty.
- However, Git is not allowed to commit an empty directory to the repository.

Solution:
- Create a `.gitkeep` file in the empty files directory and commit.
### 4. Migrate
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
### 5. Captcha
 - Generate graphical CAPTCHA
```python
# verifications/libs/captcha/captcha.py
```
```python
from verifications.libs.captcha.captcha import captcha

text, image = captcha.generate_captcha()
```
### 6. Pipeline
 - Can send multiple commands at once and return the results at once after execution.
 - The pipeline reduces round-trip latency by reducing the number of times the client communicates with Redis.
```python
# Create a Redis Pipeline
pl = redis_conn.pipeline()
# Adding Redis requests to the queue
pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
# Execute a request
pl.execute()
```
### 7. Celery
 - celery_tasks/
### 8. Gmail
```python
# Mail Parameters
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # Specify mail backend
EMAIL_HOST = 'smtp.gmail.com' # Email Hosting
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'sgsgkxkx@gmail.com' # Authorized mailboxes
# Find the App passwords
# https://accounts.google.com/v3/signin/challenge/pwd?TL=AO-GBTch9TnaMKIgOG9WZGtoEipRq50kpVp6zG2csA69EoLO6LyvHCfNfNzljPje&cid=2&continue=https%3A%2F%2Fmyaccount.google.com%2Fapppasswords%3Frapt%3DAEjHL4NjUGNYui7C_gznx1LBGc8apn4J8UorQtO7o_CbyRxe6fie1NDyS0tCDfopemMhyhO2zJ-sk8YIkt_8mL2PgeNScEIvwhZXhQouwuIU7QZZbeAJa5g&flowName=GlifWebSignIn&followup=https%3A%2F%2Fmyaccount.google.com%2Fapppasswords%3Frapt%3DAEjHL4NjUGNYui7C_gznx1LBGc8apn4J8UorQtO7o_CbyRxe6fie1NDyS0tCDfopemMhyhO2zJ-sk8YIkt_8mL2PgeNScEIvwhZXhQouwuIU7QZZbeAJa5g&ifkv=AVdkyDmhNDjhNVRezacg9VQBm1mYFxtRHjWMcYWkuJ40NOkb_Pe4Cj_e1Lw37kQ5_6aTJYSn8wMolw&osid=1&rart=ANgoxcePLST8yBfyW30pYA8wycMl-do56TvzrEEVB5yu-iaAIKHv8mob2_g0h5qWeH2cKQocCvKuaL_QOywIRbG6Hm9o3BwPC2KIti0G0GjBdGHn83awOcE&rpbg=1&service=accountsettings
EMAIL_HOST_PASSWORD = '' # Password obtained during mailbox authorization, not the registered login password
EMAIL_FROM = 'LemonMall<sgsgkxkx@gmail.com>' # Sender's letterhead
```
```python
from django.core.mail import send_mail
def send_verify_email(self, to_email, verify_url):
    """Define tasks for sending validation emails"""
    # send_mail('title', 'message', 'sender', 'receiver list', 'rich text(html)')

    subject = "Lemon Mall Email Verification"
    html_message = '<p>Dear users, </p>'
                   '<p>Thank you for using Lemon Mall.</p>'
                   '<p>Your e-mail address is: %s . Please click on this link to activate your mailbox:</p>'
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        # trigger an error retry: Maximum 3 tentatives
        raise self.retry(exc=e, max_retries=3)
```
### 9. Cache
 - Not frequently changing data
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
### 10. Paging
```python
# Paging
from django.core.paginator import Paginator, EmptyPage
# Creating a Paginator
# Paginator('Data to be paged', 'Number of records per page')
paginator = Paginator(skus, 5)  # Pagination of skus with 5 records per page
try:
   # Get the page the user is currently looking at(Core data)
   page_skus = paginator.page(page_num)    # Gets the five records in the page_nums page.
except EmptyPage:
   return http.HttpResponseNotFound('Empty Page')

# Get Total Pages: The front-end paging plugin requires the use
total_page = paginator.num_pages
```
```html
<div class="r_wrap fr clearfix">
    ......
    <div class="pagenation">
        <div id="pagination" class="page"></div>
    </div>
</div>

<link rel="stylesheet" type="text/css" href="{{ static('css/jquery.pagination.css') }}">

<script type="text/javascript" src="{{ static('js/jquery.pagination.min.js') }}"></script>

<script type="text/javascript">
    $(function () {
        $('#pagination').pagination({
            currentPage: {{ page_num }},
            totalPage: {{ total_page }},
            callback:function (current) {
                {#location.href = '/list/115/1/?sort=default';#}
                location.href = '/list/{{ category.id }}/' + current + '/?sort={{ sort }}';
            }
        })
    });
</script>
```
### 11. ElasticSearch
```bash
sudo docker image pull delron/elasticsearch-ik:2.4.6-1.0
```
 - Change the ip address to the real ip address of the local machine.
```bash
# /home/python/elasticsearc-2.4.6/config/elasticsearch.yml
network.host: 192.168.103.158
```
```bash
sudo docker run -dti --name=elasticsearch --network=host -v /home/python/elasticsearch-2.4.6/config:/usr/share/elasticsearch/config delron/elasticsearch-ik:2.4.6-1.0
```
### 12. Transaction
```python
from django.db import transaction

# Create a save point
save_id = transaction.savepoint()  
# Rollback to save point
transaction.savepoint_rollback(save_id)
# Commit all database transaction operations from the save point to the current state
transaction.savepoint_commit(save_id)
```
```python
class OrderCommitView(LoginRequiredMixin, View):
    """Submit order"""
    def post(self, request):
        ...
        # Explicitly open of a transaction
        with transaction.atomic():
            # Savepoints need to be specified before database operations(Preserve the initial state of the database)
            save_id = transaction.savepoint()
            # brute force rollback
            try:
                ...
                order.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Failure'})

            # Successful database operation, Explicitly commit a transaction
            transaction.savepoint_commit(save_id)


        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})
```

### 13. Timed task
```bash
pip3 install django-crontab
```
```python
# settings/dev.py
INSTALLED_APPS = [    
    'django_crontab', # timed task
]

CRONJOBS = [
    # Generate homepage static files every 1 minute
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log'))
]

CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'
```
```bash
# Add timed tasks to the system
$ python manage.py crontab add

# crontab: no crontab for citron
# adding cronjob: (afe82496b5176d7774b91d3a15136d68) -> ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> /Users/citron/Documents/GitHub/lemon_mall/lemon_mall/logs/crontab.log')

# Show activated timed tasks
$ python manage.py crontab show

# Remove Timed Tasks
$ python manage.py crontab remove
```

### 14. Git
```bash
# Cancel commit
git reset --soft HEAD^
```

### 15. Quick create django project
```bash
python3 -m venv lemonmall-env
source lemonmall-env/bin/activate
pip3 install django

django-admin startproject lemon_mall
python3 manage.py runserver
```

### 16. Pycharm Configuration Django
 - Edit Configuration
 - \+ Django server
 - Fix
 - Enable Django Support
 - Django project root: lemon_mall/lemon_mall (Folders with manage.py)
 - Settings: lemon_mall/settings/dev.py
 - Apply -> Ok

### 17. Create super user
```bash
python manage.py shell
```
```python
from users.models import User 

admin_user = User.objects.create_superuser(
    username="admin",
    email="admin@example.com",
    password="admin"
)
```
```bash
exit()
```
## License

[MIT](https://choosealicense.com/licenses/mit/)