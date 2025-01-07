from django.urls import include,re_path
from . import views

app_name = 'users'

urlpatterns = [
    # User Registration: reverse(users:register) == '/register/'
    re_path(r'^register/$', views.RegisterView.as_view(), name='register'),
    # Determine whether a username is a duplicate registration
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    # Determine whether a cell phone number is a duplicate registration
    re_path(r'^mobiles/(?P<mobile>\+?(\d{1,3})?[- ]?(\d{10,11}))/count/$', views.MobileCountView.as_view()),
    # User login
    re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    # User logout
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # User center
    re_path(r'^info/$', views.UserInfoView.as_view(), name='info'),
    # Add email
    re_path(r'^emails/$', views.EmailView.as_view()),
    # Verify email
    re_path(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    # Show user address
    re_path(r'^addresses/$', views.AddressView.as_view(), name='address'),
    # Add user address
    re_path(r'^addresses/create/$', views.AddressCreateView.as_view()),
    # Update and delete address
    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # Set the default address
    re_path(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    # Update address title
    re_path(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    # User Browsing History
    re_path(r'^browse_histories/$', views.UserBrowseHistory.as_view())
]