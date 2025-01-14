# 7. Shopping cart
## 7.1 Shopping Cart Storage Solutions
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
## 7.2 Shopping Cart Management
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
 - Merge Shopping Cart
```python
# carts/utils.py
def merge_carts_cookies_redis(request, user, response):
    """Merge cart"""
    # Get shopping cart data from cookies
    ...
    # No need to merge if it does not exist
    # If present, needs to be merged
    # Prepare new data container: save new sku_id:count, selected, unselected
    new_cart_dict = {}
    new_selected_add = []
    new_selected_rem = []
    # Iterate over the shopping cart data in the cookies
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)

    # Merge into redis based on the new data structure
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_%s' % user.id, new_cart_dict)
    if new_selected_add:
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)
    pl.execute()

    # Delete cookies
    response.delete_cookie('carts')
    return response
```
 - Merge cart
