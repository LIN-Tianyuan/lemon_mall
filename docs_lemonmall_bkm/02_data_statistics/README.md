# 2. Data Statistics
## 2.1 Total User Statistics
 - Interface analysis
      - request method: GET
      - request path: /lemon_admin/statistical/total_count/
      - request parameter: Token Header Passing
      - result: {count, date}
 - Business logic
    - Get the day's date: datetime
    - Get total number of users: User
    - Return results
    - API View
```python
# lemon_admin/views/statistical.py
class UserCountView(APIView):
    """Total User Statistics"""
    # Permission
    permission_classes = [IsAdminUser]
    def get(self, request):
        # Get the day's date: datetime
        now_date = date.today()
        # Get total number of users: User
        count = User.objects.all().count()
        # Return results
        return Response({'count': count, 'date': now_date})
```
```python
# lemon_admin/urls.py
re_path(r'^statistical/total_count/$', statistical.UserCountView.as_view()),
```
 - Postman
```
GET http://127.0.0.1:8080/lemon_admin/statistical/total_count/

Authorization:(Bearer Token)
Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM4MzI3OTg4LCJpYXQiOjE3MzgyNDE1ODgsImp0aSI6IjNjOThiZTZjOTMyNDQzNjhhNWFiNGQwMWU3NDc4ZTY0IiwidXNlcl9pZCI6Mn0.WqjxHVGWszd2Lu-wI3cfGhKdGrklNbAKTUkgghNH4AU
```