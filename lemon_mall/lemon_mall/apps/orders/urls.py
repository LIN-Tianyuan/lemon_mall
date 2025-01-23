from django.urls import re_path

from . import views

app_name = 'orders'

urlpatterns = [
    # settlement order
    re_path(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
    # submit order
    re_path(r'^orders/commit/$', views.OrderCommitView.as_view()),
    # Submit Order Success
    re_path(r'^orders/success/$', views.OrderSuccessView.as_view()),
    # Order Product Evaluation
    re_path(r'^orders/comment/$', views.OrderCommentView.as_view())
]