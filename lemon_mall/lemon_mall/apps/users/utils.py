# Customizing the back-end of user authentication: enabling multiple account logins
from django.contrib.auth.backends import ModelBackend
import re
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData

from users.models import User
from . import constants


def check_verify_email_token(token):
    """Deserialize token, get user"""
    s = Serializer(settings.SECRET_KEY, salt='email-confirm')
    try:
        data = s.loads(token, max_age=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    except BadData:
        return None
    else:
        # Get user_id and email from data
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user

def generate_verify_email_url(user):
    """Generate email activation link"""
    s = Serializer(settings.SECRET_KEY, salt='email-confirm')
    data = {'user_id': user.id, 'email': user.email}    # Currently logged in user
    token = s.dumps(data)
    return settings.EMAIL_VERIFY_URL + '?token=' + token

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
        if request and getattr(request, "path", "").startswith("/lemon_admin/"):
            # Back Office Login
            try:
                # is_superuser: Determine if a user is a super user
                user = User.objects.get(username=username, is_superuser=True)
            except:
                user = None

            if user is not None and user.check_password(password):
                return user
        else:
            """Rewrite the methods for user authentication"""
            # search user
            user = get_user_by_account(username)
            # # If the user can be queried, only need to verify that the password is correct.
            if user and user.check_password(password):
                # Returns user
                return user
            else:
                return None
