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
## 2.2 Daily user statistics(Count the number of users registered on the same day)
- Interface analysis
   - request method: GET
   - request path: /lemon_admin/statistical/day_increment/
   - request parameter: Token Header Passing
   - result: {count, date}
- Business logic
   - Get the day's date: datetime
   - Get the number of users registered on the day: User
   - Return results
   - API View
## 2.3 Daily user statistics (Count the number of users who have logged in that day)
- Interface analysis
    - request method: GET
    - request path: /lemon_admin/statistical/day_active/
    - request parameter: Token Header Passing
    - result: {count, date}
- Business logic
    - Get the day's date: datetime
    - Get the number of users logged on the day: User
    - Return results
    - API View
## 2.4 Statistics of users placing orders (Count the number of users placing orders on the same day)
- Interface analysis
    - request method: GET
    - request path: /lemon_admin/statistical/day_orders/
    - request parameter: Token Header Passing
    - result: {count, date}
- Business logic
    - Get the day's date: datetime
    - Get the total number of users placing orders that day: User
    - Return results
    - API View
```python
# lemon_admin/views/statistical.py
class UserDayOrdersCountView(APIView):
    """Statistics of users placing orders"""
    # Permission
    permission_classes = [IsAdminUser]
    def get(self, request):
        # Get the day's date: datetime
        now_date = date.today()
        # Get the total number of logged users for the day
        count = len(set(User.objects.filter(orders__create_time__gte=now_date)))
        # Return results
        return Response({'count': count, 'date': now_date})
```
```python
# lemon_admin/urls.py
re_path(r'^statistical/day_orders/$', statistical.UserDayOrdersCountView.as_view()),
```
## 2.5 Monthly user increase statistics (statistics on the number of users registered per day within a month)
- Interface analysis
    - request method: GET
    - request path: /lemon_admin/statistical/month_increment/
    - request parameter: Token Header Passing
    - result: [{count, date}, {count, date}, ...]
- Business logic
    - Get the day's date: datetime
    - Get the date one month ago
    - Iterate through the loop to get the data for each day, starting with the date one month ago: User
    - Return results
    - API View
## 2.6 Daily Classifieds Visits (counting the number of visits to classifieds in a day)
- Interface analysis
  - request method: GET
  - request path: /lemon_admin/statistical/goods_day_views/
  - request parameter: Token Header Passing
  - result: {count, date}
- Business logic
  - Get the day's date: datetime
  - Query the number of visits by category based on the date of the day
  - Return results
  - API View
