from django.urls import re_path

from . import views

app_name = 'orders'

urlpatterns = [
    # settlement order
    re_path(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement')
]