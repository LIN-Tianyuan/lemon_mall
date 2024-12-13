from django.contrib.auth.mixins import LoginRequiredMixin
from django import http

from lemon_mall.utils.response_code import RETCODE

class LoginRequiredJSONMixin(LoginRequiredMixin):
    """Customize the extension class that determines whether a user is logged in or not: return JSON"""

    # The reason why only handle_no_permission needs to be overridden is that the parent class has already done the work of determining whether the user is logged in or not, and the child class only needs to be concerned with the
    # What to do if the user is not logged in
    def handle_no_permission(self):
        """Direct Response JSON Data"""
        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': 'User is not logged in'})