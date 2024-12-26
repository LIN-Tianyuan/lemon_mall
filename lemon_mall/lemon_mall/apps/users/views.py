from django.shortcuts import render, redirect
from django.views import View
from django import http
import re, json, logging
from django.db import DatabaseError
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import User, Address
from lemon_mall.utils.response_code import RETCODE
from lemon_mall.utils.views import LoginRequiredJSONMixin
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_verify_email_url, check_verify_email_token
from . import constants

# Create your views here.

# Creating log exporter
logger = logging.getLogger('django')


class UpdateTitleAddressView(LoginRequiredJSONMixin, View):
    """Update address title"""
    def put(self, request, address_id):
        # Receive parameter: title
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        # Check parameter
        if not title:
            return http.HttpResponseForbidden('Missing title')
        try:
            # Query the current address of the title to be updated
            address = Address.objects.get(id=address_id)
            # Overwrite the address header with the new address header
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Failed to update address title'})
        # Response result
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'Success to update address title'})


class DefaultAddressView(LoginRequiredJSONMixin, View):
    """Set the default address"""
    def put(self, request, address_id):
        try:
            # Find out which address is currently used as the default address for logged in users.
            address = Address.objects.get(id=address_id)
            # Sets the specified address as the default address for the currently logged in user
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Failed to set default address'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'Success to set default address'})
class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """Update and delete address"""

    def put(self, request, address_id):
        """update address"""
        # Receive parameter
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # Check parameter
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('Absence of mandatory parameters')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('The parameter mobile is incorrect')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('The parameter tel is incorrect')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('The parameter email is incorrect')

        # Overwrite the specified address information with the latest address information
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse(
                {'code': RETCODE.DBERR, 'errmsg': 'Failed to change address'})

        # Responds with new address information for front-end rendering
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return http.JsonResponse(
            {'code': RETCODE.OK, 'errmsg': 'Address changed successfully', 'address': address_dict})

    def delete(self, request, address_id):
        """Delete address"""
        # Enables logical deletion of a specified address: is_delete=True
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Failed to delete address'})
        # Response result
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'Success to delete address'})

class AddressCreateView(LoginRequiredJSONMixin, View):
    """Add address"""

    def post(self, request):
        """Implement new address logic"""
        # Determine if the number of user addresses exceeds the upper limit: Queries the number of addresses of currently logged-in users
        # count = Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()  # One query for multiple, use related_name query
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': 'Exceeds user address limit'})

        # Receive parameter
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # Check parameter
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('Absence of mandatory parameters')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('The parameter mobile is incorrect')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('The parameter tel is incorrect')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('The parameter email is incorrect')

        # Hold the address information passed in by the user
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # If the user does not have a default address, we need to specify a default address
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Failed to add address'})

        # Add the new address successfully, the new address will be responded to the front-end to realize the local refreshing.
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # Responding to the added address result: the added address needs to be returned to the front-end for rendering
        return http.JsonResponse(
            {'code': RETCODE.OK, 'errmsg': 'New address added successfully', 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    """User Delivery Address"""

    def get(self, request):
        """Query and display user address information"""

        # Get the current user login object
        login_user = request.user
        # Query address data using currently logged in user and is_deleted=False as conditions
        addresses = Address.objects.filter(user=login_user, is_deleted=False)
        # Convert a model list of user addresses to a dictionary list: because JsonResponse and Vue.js don't recognize model types, only Django and the Jinja2 template engine do!
        address_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)

        # construct Context
        context = {
            'default_address_id': login_user.default_address_id or '0',
            'addresses': address_list
        }
        return render(request, 'user_center_site.html', context)


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
        json_str = request.body.decode()  # The body type is bytes
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
            request.session.set_expiry(0)  # The unit is seconds.
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
            return http.HttpResponseForbidden('缺少必传参数')
        # Determine if the username is 5-20 characters long.
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # Determine if the password is 8-20 digits.
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # Determine whether the two passwords are the same
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # Determine whether the cell phone number is legitimate
        if not re.match(r'^\+?(\d{1,3})?[- ]?(\d{10,11})$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # Determine whether the SMS verification code is entered correctly
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': 'SMS verification code is no longer valid'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': 'Incorrectly entered SMS verification code'})
        # Determine whether to check the user agreement
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # Preservation of registration data: is the heart of the registration business
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # Realization of state retention
        login(request, user)

        response = redirect(reverse('contents:index'))
        # To enable the display of username information in the upper right corner of the home page, we need to cache the username in a cookie
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # Response Result: Redirect to home page
        return response
