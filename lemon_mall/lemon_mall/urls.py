"""
URL configuration for lemon_mall project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    # haystack
    re_path(r'^search/', include('haystack.urls')),
    # users
    re_path(r'^', include('users.urls', namespace='users')),
    # contents
    re_path(r'^', include('contents.urls', namespace='contents')),
    # verifications
    re_path(r'^', include('verifications.urls')),
    # oauth
    re_path(r'^', include('oauth.urls')),
    # areas
    re_path(r'^', include('areas.urls')),
    # goods
    re_path(r'^', include('goods.urls', namespace='goods')),
    # carts
    re_path(r'^', include('carts.urls', namespace='carts')),
    # orders
    re_path(r'^', include('orders.urls', namespace='orders')),
    # payment
    re_path(r'^', include('payment.urls', namespace='payment')),
    # admin
    re_path(r'^lemon_admin/', include('lemon_admin.urls'))
]
