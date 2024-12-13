from django.shortcuts import render, redirect
from django.views import View
from django import http
import re, json, logging
from django.db import DatabaseError
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import User
from lemon_mall.utils.response_code import RETCODE
from lemon_mall.utils.views import LoginRequiredJSONMixin
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_verify_email_url, check_verify_email_token
# Create your views here.

# Creating log exporter
logger = logging.getLogger('django')

class AddressView(LoginRequiredMixin, View):
    """User Delivery Address"""
    def get(self, request):
        return render(request, 'user_center_site.html')


class VerifyEmailView(View):
    """verification"""
    def get(self, request):
        # Receive parameter
        token = request.GET.get('token')
        # Check parameter
        if not token:
            return http.HttpResponseForbidden('Missing Token')
        # Extract user info from token  user_info => user
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseBadRequest('Invalid token')
        # Setting the user's email_active field to True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('Failed to activate mailbox')
        # Response Result: Redirect to User Center
        return redirect(reverse('users:info'))

class EmailView(LoginRequiredJSONMixin, View):
    """Add email"""
    def put(self, request):
        # Receive parameter
        json_str = request.body.decode()    # The body type is bytes
        json_dict = json.loads(json_str)
        email = json_dict.get('email')
        # Check parameter
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('The parameter email is incorrect')
        # Save the user's incoming mailbox into the email field of the database user
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Failed to add mailbox'})
        # Send Email Verification Email
        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)

        # Response result
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})




class UserInfoView(LoginRequiredMixin, View):
    """User center"""
    def get(self, request):
        """Provide user center page"""
        # If LoginRequiredMixin determines that the user is logged in, then request.user is the logged-in user object
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)



class LogoutView(View):
    """User Logout"""
    def get(self, request):
        """Implement user logout logic"""
        # Clearing stateful retention information
        logout(request)
        # Redirect to home page after logging out
        response = redirect(reverse('contents:index'))

        # Delete username from cookie
        response.delete_cookie('username')

        # Response result
        return response

class LoginView(View):
    """user login"""
    def get(self, request):
        """Provide user login page"""
        return render(request, 'login.html')

    def post(self, request):
        """Implement user login logic"""
        # Receiving parameters
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # Calibration parameters
        if not all([username, password]):
            return http.HttpResponseForbidden('Absence of mandatory parameters')
        # Determine if the username is 5-20 characters long.
        if not re.match(r'^[+a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('Please enter the correct username or cell phone number')
        # Determine if the password is 8-20 digits.
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('Password minimum 8 digits, maximum 20 digits')
        # Authenticated Users: Use the account to check if the user exists, and if the user exists, then check if the password is correct
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': 'Incorrect account number or password'})
        # Status Hold
        login(request, user)
        # Use remembered to determine the state retention period (to implement remembered login)
        if remembered != 'on':
            # No login is remembered: the state is kept until the end of the browser session and then destroyed.
            request.session.set_expiry(0)   # The unit is seconds.
        else:
            # Remember to log in: status is maintained for two weeks: Default is two weeks.
            request.session.set_expiry(None)

        # Take out the next
        next = request.GET.get('next')
        if next:
            # Redirect to next
            response = redirect(next)
        else:
            # Redirect to home page
            response = redirect(reverse('contents:index'))
        # To enable the display of username information in the upper right corner of the home page, we need to cache the username in a cookie
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # Response Result: Redirect to home page
        return response


class UsernameCountView(View):
    """Determine whether a username is a duplicate registration"""
    def get(self, request, username):
        # Implement the main business logic: use username to query the number of corresponding records.
        # (The filter returns the set of results that satisfy the condition.)
        count = User.objects.filter(username=username).count()
        # Response results
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'count': count})


class RegisterView(View):
    """User Registration"""
    def get(self, request):
        """Provide user registration page"""
        return render(request, 'register.html')

    def post(self, request):
        """Implement user registration business logic"""
        # Receive parameters
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')
        # Check parameters: Front-end and back-end checks should be separated to avoid malicious users to cross the front-end logic to send requests, to ensure the security of the back-end, the front and back-end checks should be the same logic
        # Determine if the parameters are complete: all([list]) will check whether the elements in the list are empty, as long as one is empty, return False
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('Missing mandatory parameters')
        # Determine if the username is 5-20 characters long.
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('Please enter a username of 5-20 characters')
        # Determine if the password is 8-20 digits.
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('Please enter a password of 8-20 digits')
        # Determine whether the two passwords are the same
        if password != password2:
            return http.HttpResponseForbidden('Inconsistent passwords entered twice')
        # Determine whether the cell phone number is legitimate
        if not re.match(r'^\+?(\d{1,3})?[- ]?(\d{10,11})$', mobile):
            return http.HttpResponseForbidden('Incorrectly formatted phone number')
        # Determine whether the SMS verification code is entered correctly
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': 'SMS verification code is no longer valid'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': 'Incorrectly entered SMS verification code'})
        # Determine whether to check the user agreement
        if allow != 'on':
            return http.HttpResponseForbidden('Please check the user agreement')

        # Preservation of registration data: is the heart of the registration business
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': 'Registration Failed!'})

        # Realization of state retention
        login(request, user)

        response = redirect(reverse('contents:index'))
        # To enable the display of username information in the upper right corner of the home page, we need to cache the username in a cookie
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # Response Result: Redirect to home page
        return response


