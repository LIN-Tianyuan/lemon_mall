from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from datetime import date
from users.models import User

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


class UserDayCountView(APIView):
    """Daily user statistics"""
    # Permission
    permission_classes = [IsAdminUser]
    def get(self, request):
        # Get the day's date: datetime
        now_date = date.today()
        # Get the total number of registered users for the day
        count = User.objects.filter(date_joined__gte=now_date).count()
        # Return results
        return Response({'count': count, 'date': now_date})