from django.shortcuts import render, redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
import logging, re
from django.contrib.auth import login
from django.urls import reverse
from django_redis import get_redis_connection

from lemon_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token, check_access_token
from users.models import User

# Creating log exporter
logger = logging.getLogger('django')


class QQAuthUserView(View):
    """Handling qq login callbacks"""
    def get(self, request):
        """Business logic for handling qq login callbacks"""
        # Get code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('Failed to get code')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # Getting access_token with code
            access_token = oauth.get_access_token(code)

            # Get openid using access_token
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0 Authentication Failure')
        # Use openid to determine if the QQ user is bound to lemon_mall.
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # openid unbound lemonmall user
            access_token_openid = generate_access_token(openid)
            context = {'access_token_openid': access_token_openid}
            return render(request, 'oauth_callback.html', context)
        else:
            # openid is bound to the mall user: oauth_user.user means find the corresponding user from the QQ login model class
            login(request, oauth_user.user)
            next = request.GET.get('state')
            response = redirect(next)
            # To enable the display of username information in the upper right corner of the home page, we need to cache the username in a cookie
            response.set_cookie('username', oauth_user.user.username, max_age=3600 * 24 * 15)
            # Response Result: Redirect to home page
            return response

    def post(self, request):
        """Implementing the logic for binding users"""
        # Receiving parameters
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token')

        # Calibration parameters
        if not all([mobile, pwd, sms_code_client]):
            return http.HttpResponseForbidden('Absence of mandatory parameters')
        # Determine if the username is 5-20 characters long.
        if not re.match(r'^\+?(\d{1,3})?[- ]?(\d{10,11})$', mobile):
            return http.HttpResponseForbidden('Please enter the correct username or cell phone number')
        # Determine if the password is 8-20 digits.
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('Please enter a password of 8-20 digits')
        # Determine whether the SMS verification code is entered correctly
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg':'SMS verification code is no longer valid'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': 'Incorrectly entered SMS verification code'})
        # Determine if the openid is valid:The openid is only valid for 600 seconds after itsdangerous signature.
        openid = check_access_token(access_token_openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'The openid is no longer valid.'})
        # Use the cell phone number to check if the corresponding user exists
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # If the cell phone number user does not exist, create a new user
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            # If a user with a cell phone number exists, the password needs to be verified
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': 'Incorrect account number or password.'})
        # Bind user to openid
        try:
            oauth_qq_user = OAuthQQUser.objects.create(user=user, openid=openid)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'account_errmsg': 'Incorrect account number or password.'})
        # openid is bound to the mall user: oauth_user.user means find the corresponding user from the QQ login model class
        login(request, oauth_qq_user.user)
        # Response Result: Redirect to state
        next = request.GET.get('state')
        response = redirect(next)
        # To enable the display of username information in the upper right corner of the home page, we need to cache the username in a cookie
        response.set_cookie('username', oauth_qq_user.user.username, max_age=3600 * 24 * 15)
        return response

# Create your views here.
class QQAuthURLView(View):
    """Provide QQ login code scanning page"""
    def get(self, request):
        # Receive next
        next = request.GET.get('next')
        # Creating Tool Objects
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # Generate QQ login sweep link address
        login_url = oauth.get_qq_url()
        # response
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'login_url': login_url})