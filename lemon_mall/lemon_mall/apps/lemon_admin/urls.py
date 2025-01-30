from django.urls import re_path
from .views import login, statistical

app_name = 'lemon_admin'

urlpatterns = [
    # Login
    re_path(r'^authorizations/$', login.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # --------------------- data statistics ---------------------
    # total number of users
    re_path(r'^statistical/total_count/$', statistical.UserCountView.as_view()),
    # daily incremental user registered
    re_path(r'^statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    # daily incremental user logged
    re_path(r'^statistical/day_active/$', statistical.UserDayActiveView.as_view()),
    # user who places an order
    re_path(r'^statistical/day_orders/$', statistical.UserDayOrdersCountView.as_view()),
    # monthly incremental user
    re_path(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    #
    re_path(r'^statistical/goods_day_views/$', statistical.UserGoodsCountView.as_view()),
]