# 3. User Management
## 3.1 Getting user data
### 3.1.1 Get one
- Interface analysis
    - request method: GET
    - request path: /lemon_admin/users/
    - request parameter:
      - query string: keyword=username, page=pagesize
      - header: token
    - result: {id, username, mobile, email}
- Business logic
    - Get Front End Data
    - Query user
    - Return user's data
    - List
### 3.1.2 Get many
- Interface analysis
    - request method: GET
    - request path: /lemon_admin/users/
    - request parameter:
        - query string: keyword=, page=pagesize
        - header: token
    - result: {id, username, mobile, email}
- Business logic
    - Get Front End Data
    - Query all user(all)
    - Return user's data
    - List
```python
# lemon_admin/utils.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# Customizable Pagination
class PageNum(PageNumberPagination):
    page_size_query_param = 'pagesize'
    max_page_size = 10

    # Methods for specifying the results to be returned by paging
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'lists': data,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'pagesize': self.max_page_size
        })
```
```python
# lemon_admin/views/users.py
from rest_framework.generics import ListAPIView

from lemon_admin.serializers.users import UserSerializer
from lemon_admin.utils import PageNum
from users.models import User
class UserView(ListAPIView):
    """Get user data"""
    # Specify query set
    queryset = User.objects.all()
    # Specify the serializer
    serializer_class = UserSerializer
    # Pagination
    pagination_class = PageNum
```
```python
# lemon_admin/urls.py
re_path(r'^users/$', users.UserView.as_view()),
```
## 3.2 Add and Save Users