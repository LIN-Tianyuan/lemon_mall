from django.urls import re_path
from .views import login, statistical

app_name = 'lemon_admin'

urlpatterns = [
    # Login
    re_path(r'^authorizations/$', login.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # --------------------- data statistics ---------------------
    # total number of users
    re_path(r'^statistical/total_count/$', statistical.UserCountView.as_view()),

]