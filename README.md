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
```python
# carts/views.py
class CartsView(View):
    ...
    # Determine if the user is logged in
    user = request.user
    if user.is_authenticated:
        # If the user is logged in, operate the Redis shopping cart
        redis_conn = get_redis_connection('carts')
        pl = redis_conn.pipeline()
        # Need to save commodity data in the form of incremental calculations
        pl.hincrby('carts_%s' % user.id, sku_id, count)
        # Save product check status
        if selected:
            pl.sadd('selected_%s' % user.id, sku_id)
        # Respond result
        pl.execute()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
    else:
        # Manipulate cookie shopping cart if user is not logged in
        cart_str = request.COOKIES.get('carts')
        if cart_str:
            # Convert cart_str to a string of type bytes
            cart_str_bytes = cart_str.encode()
            # Convert cart_str_bytes to dictionary of type bytes
            cart_dict_bytes = base64.b64decode(cart_str_bytes)
            # Convert cart_dict_bytes to a real dictionary
            cart_dict = pickle.loads(cart_dict_bytes)
        else:
            cart_dict = {}

        # Determine if the current product to be added exists in the cart_dict
        if sku_id in cart_dict:
            # Shopping cart already exists, incremental calculation
            origin_count = cart_dict[sku_id]['count']
            count += origin_count

        cart_dict[sku_id] = {
            'count': count,
            'selected': selected
        }

        # Convert cart_dict to dictionary of type bytes
        cart_dict_bytes = pickle.dumps(cart_dict)
        # Convert cart_dict_bytes to a string of type bytes
        cart_str_bytes = base64.b64decode(cart_dict_bytes)
        # Convert cart_str_bytes to string
        cookie_cart_str = cart_str_bytes.decode()

        # Write new cart data to cookie
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        response.set_cookie('carts', cookie_cart_str)

        # Respond result
        return response
```

## License

[MIT](https://choosealicense.com/licenses/mit/)