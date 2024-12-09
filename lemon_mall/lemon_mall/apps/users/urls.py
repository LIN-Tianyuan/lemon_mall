from django.urls import include,re_path
from . import views

app_name = 'users'

urlpatterns = [
    # User Registration: reverse(users:register) == '/register/'
    re_path(r'^register/$', views.RegisterView.as_view(), name='register'),
    # Determine whether a username is a duplicate registration
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    # User login
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    # User logout
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # User center
    re_path(r'^info/$', views.UserInfoView.as_view(), name='info')
]