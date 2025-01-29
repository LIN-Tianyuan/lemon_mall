# 9. Payment
## 9.1 Alipay Introduction
```bash
python3 ../../manage.py startapp payment
```
```python
# dev.py
INSTALLED_APPS = [
    ...,
    'payment', # payment
]
```
```python
urlpatterns = [
    ...,
    # orders
    re_path(r'^', include('orders.urls', namespace='orders'))
]
```
