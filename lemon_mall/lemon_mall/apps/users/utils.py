# Customizing the back-end of user authentication: enabling multiple account logins
from django.contrib.auth.backends import ModelBackend
import re

from users.models import User

def get_user_by_account(account):
    """Getting Users by Account"""
    try:
        if re.match(r'^\+?(\d{1,3})?[- ]?(\d{10,11})$', account):
            # username == phone number
            user = User.objects.get(mobile=account)
        else:
            # username == username
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileBackend(ModelBackend):
    # Customizing the back-end of user authentication
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Rewrite the methods for user authentication"""
        # search user
        user = get_user_by_account(username)
        # # If the user can be queried, only need to verify that the password is correct.
        if user and user.check_password(password):
            # Returns user
            return user
        else:
            return None
