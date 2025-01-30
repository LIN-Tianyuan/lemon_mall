from django.urls import re_path
from .views import CustomTokenObtainPairView

app_name = 'lemon_admin'

urlpatterns = [
    # Login
    re_path(r'^authorizations/$', CustomTokenObtainPairView.as_view(), name='token_obtain_pair')
]