# 1. Project Environment Setup
```bash
python3 ../../manage.py startapp lemon_admin
```
```python
# settings/dev.py
INSTALLED_APPS = [
    ...,
    'lemon_admin'
]
```
## 1.1 CORS
```bash
pip install django-cors-headers
```
```python
INSTALLED_APPS = (
    ...
    'corsheaders',
    ...
)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8090",
    "http://localhost:8080",
    "http://localhost:8090"
]

CORS_ALLOW_CREDENTIALS = True  # Allow cookies
```
## 1.2 Administrator Login
 - Interface analysis
   - path: lemonmall/authorizations/
   - parameter: username, password
   - result: username, token, id
 - Business logic
   - JWT
     - Get Front End Data
     - Validate Data
       - Serializer
     - Construct Response Data
     - Return Results

```bash
# rest_framework_jwt is no longer maintained and is not available in the latest Django version.
# Old version
# pip uninstall djangorestframework-jwt

pip install djangorestframework-simplejwt
```
```python
# settings/dev.py
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # ✅ 替换旧的 JWT 认证
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}
```
```python
# lemon_admin/urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    re_path(r'^authorizations/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
]
```
```python
# lemon_mall/urls.py
re_path(r'^lemon_admin/', include('lemon_admin.urls'))
```
 - Customized JWT Response Handler Functions
```python
# lemon_admin/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'id': self.user.id,
            'username': self.user.username,
        })
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```
```python
# lemon_admin/urls.py
from django.urls import re_path
from .views import CustomTokenObtainPairView

app_name = 'lemon_admin'

urlpatterns = [
    # Using custom JWT views
    re_path(r'^authorizations/$', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
```
