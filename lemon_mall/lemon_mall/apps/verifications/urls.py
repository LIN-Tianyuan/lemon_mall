from django.urls import include,re_path
from . import views

app_name = 'verifications'

urlpatterns = [
    # graphical captcha
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    # SMS verification code
    re_path(r'^sms_codes/(?P<mobile>\+?(\d{1,3})?[- ]?(\d{9,11}))/$', views.SMSCodeView.as_view())
]