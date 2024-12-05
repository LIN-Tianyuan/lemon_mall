from django.urls import include,re_path
from . import views

app_name = 'contents'

urlpatterns = [
    # Home page advertisement
    re_path(r'^$', views.IndexView.as_view(), name='index')
]