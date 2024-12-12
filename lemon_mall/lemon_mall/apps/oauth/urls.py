from django.urls import include,re_path
from . import views

app_name = 'oauth'

urlpatterns = [
    # Provide QQ login code scanning page
    re_path(r'^qq/login/$', views.QQAuthURLView.as_view()),
    # Handle qq login callbacks
    re_path(r'^oauth_callback/$', views.QQAuthUserView.as_view())
]