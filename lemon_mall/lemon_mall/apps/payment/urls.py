from django.urls import re_path

from . import views

app_name = 'payment'

urlpatterns = [
    # payment
    re_path(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),
    # Save Order Status
    re_path(r'^payment/status/$', views.PaymentStatusView.as_view()),
]