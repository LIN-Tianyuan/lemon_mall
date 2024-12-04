from django.shortcuts import render
from django.views import View
# Create your views here.


class RegisterView(View):
    """User Registration"""
    def get(self, request):
        """Provide user registration page"""
        return render(request, 'register.html')

    def post(self, request):
        """Implement user registration business logic"""
