# 4. User login
## 4.1 Username login
```python
class LoginView(View):
    ...
```
## 4.2 Multi-user login
```python
# settings/dev.py
AUTHENTICATION_BACKENDS = ['users.utils.UsernameMobileAuthBackend']
```
```python
from django.contrib.auth.backends import ModelBackend
import re
from .models import User


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

```
## 4.3 Home Username Display
```python
response = redirect(reverse('contents:index'))

response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

return response
```
```html
<!-- index.html-->
<em>[[ username ]]</em>
```
```javascript
mounted(){
  this.username = getCookie('username');
},
```
## 4.4 Logout
```python
class LogoutView(View):

    def get(self, request):
        """Logout"""
        # Clear session
        logout(request)
        response = redirect(reverse('contents:index'))
        # Clear username from cookie when logging out
        response.delete_cookie('username')

        return response
```
## 4.5 Determine whether a user is logged in or not
```python
class UserInfoView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'user_center_info.html')
```
