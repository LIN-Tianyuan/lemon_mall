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
## 8.2 Submit Order
```python
# order/model.py
class OrderInfo(BaseModel):
    ...
class OrderGoods(BaseModel):
    ...
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