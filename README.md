# Lemon Mall

## [1. Project preparation](./docs/01_project/README.md)
### Pivot
 - Introduction to the project
 - Project creation and configuration
```bash
# Create Project
python3 -m venv lemonmall-env
source lemonmall-env/bin/activate
pip3 install django

django-admin startproject lemon_mall
python manage.py runserver
```
```bash
# Configure mysql database
create database lemonmall charset=utf8; # Create a new MySQL database
create user alex identified by '123456abcdefg'; # Create a new MySQL user
grant all on lemonmall.* to 'alex'@'%'; # Authorizing alex users to access the lemon_mall database
flush privileges; # Refresh privileges after authorization ends
```
## [2. User Registration](./docs/02_user_registration/README.md)
### Pivot
- Show user registration page
## [6. Product](./docs/06_product/README.md)
### Pivot
- Commodity database table design
- Preparation of commodity data
- Home Ads
- Home List Page
### Notice
 - Paging
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
 - ElasticSearch

## 7. Shopping cart
### 7.1 Shopping Cart Storage Solutions
Logged-in user: redis

Unlogged-in user: cookie

```bash
# pickle
>>> import pickle

>>> dict = {'1': {'count': 10, 'selected': True}, '2': {'count': 20, 'selected': False}}
>>> ret = pickle.dumps(dict)
>>> ret
b'\x80\x03}q\x00(X\x01\x00\x00\x001q\x01}q\x02(X\x05\x00\x00\x00countq\x03K\nX\x08\x00\x00\x00selectedq\x04\x88uX\x01\x00\x00\x002q\x05}q\x06(h\x03K\x14h\x04\x89uu.'
>>> pickle.loads(ret)
{'1': {'count': 10, 'selected': True}, '2': {'count': 20, 'selected': False}}
```

```bash
# base64
>>> import base64
>>> ret
b'\x80\x03}q\x00(X\x01\x00\x00\x001q\x01}q\x02(X\x05\x00\x00\x00countq\x03K\nX\x08\x00\x00\x00selectedq\x04\x88uX\x01\x00\x00\x002q\x05}q\x06(h\x03K\x14h\x04\x89uu.'
>>> b = base64.b64encode(ret)
>>> b
b'gAN9cQAoWAEAAAAxcQF9cQIoWAUAAABjb3VudHEDSwpYCAAAAHNlbGVjdGVkcQSIdVgBAAAAMnEFfXEGKGgDSxRoBIl1dS4='
>>> base64.b64decode(b)
b'\x80\x03}q\x00(X\x01\x00\x00\x001q\x01}q\x02(X\x05\x00\x00\x00countq\x03K\nX\x08\x00\x00\x00selectedq\x04\x88uX\x01\x00\x00\x002q\x05}q\x06(h\x03K\x14h\x04\x89uu.'
```
### 7.2 Shopping Cart Management
```bash
cd lemon_mall/apps
python3 ../../manage.py startapp carts
```
```python
# dev.py
INSTALLED_APPS = [
    ...,
    'carts',  # Shopping cart
]

CACHES = {
    ...,
    "carts": { # Cart
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{IP_ADDRESS}:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```
```python
# lemon_mall/urls.py
urlpatterns = [
    # carts
    re_path(r'^', include('carts.urls', namespace='carts'))
]
```
```python
# carts/urls.py
from django.urls import include,re_path

from . import views

app_name = 'carts'

urlpatterns = [
    # Shopping cart
    re_path(r'^carts/$', views.CartsView.as_view(), name='info')
]
```
 - cart select all
```python
class CartsSelectAllView(View):
    def put(self, request):
        ...
        if user is not None and user.is_authenticated:
            ...
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # Get all the Keys in the dictionary
            redis_sku_ids = redis_cart.keys()
            if selected:
                # Select all
                redis_conn.sadd('selected_%s' % user.id, *redis_sku_ids)
            else:
                # Cancel select all
                redis_conn.srem('selected_%s' % user.id, *redis_sku_ids)
        else:
            ...
            for sku_id in cart_dict:
                cart_dict[sku_id]['selected'] = selected
            ...
```

## License

[MIT](https://choosealicense.com/licenses/mit/)