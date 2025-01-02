from django.urls import include,re_path

from . import views

app_name = 'carts'

urlpatterns = [
    # Shopping cart
    re_path(r'^carts/$', views.CartsView.as_view(), name='info')
]