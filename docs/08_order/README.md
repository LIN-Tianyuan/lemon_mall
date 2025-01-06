# 8. Order
## 8.1 Settlement order
```bash
python3 ../../manage.py startapp orders
```
```python
# dev.py
INSTALLED_APPS = [
    ...,
    'orders', # Order
]
```
```python
urlpatterns = [
    ...,
    # orders
    re_path(r'^', include('orders.urls', namespace='orders'))
]
```
```python
from django.urls import re_path

from . import views

urlpatterns = [
    # settlement order
    re_path(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement')
]
```
