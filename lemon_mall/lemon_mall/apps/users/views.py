from django.shortcuts import render, redirect
from django.views import View
from django import http
import re
from django.db import DatabaseError
from django.urls import reverse
from django.contrib.auth import login
from users.models import User
from lemon_mall.utils.response_code import RETCODE
# Create your views here.

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
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('Incorrectly formatted phone number')
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
        # Response results: Redirect to home page
        # return redirect('/')
        # reverse('contents:index') == '/'
        return redirect(reverse('contents:index'))


