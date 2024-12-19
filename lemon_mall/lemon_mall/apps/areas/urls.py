from django.urls import re_path
from . import views

app_name = 'areas'

urlpatterns = [
    # Province city district three-tier linkage
    re_path(r'^areas/$', views.AreasView.as_view())
]