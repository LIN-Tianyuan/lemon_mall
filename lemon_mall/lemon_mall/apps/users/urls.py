from django.urls import include,re_path
from . import views

app_name = 'users'

urlpatterns = [
    # User Registration: reverse(users:register) == '/register/'
    re_path(r'^register/$', views.RegisterView.as_view(), name='register')
]