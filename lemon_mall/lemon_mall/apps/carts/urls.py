from django.urls import include,re_path

from . import views

app_name = 'carts'

urlpatterns = [
    # Shopping cart
    re_path(r'^carts/$', views.CartsView.as_view(), name='info'),
    # Select All Shopping Cart
    re_path(r'carts/selection/', views.CartsSelectAllView.as_view())
]