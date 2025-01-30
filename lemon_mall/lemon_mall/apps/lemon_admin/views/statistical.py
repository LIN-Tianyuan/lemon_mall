from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from datetime import date, timedelta

from lemon_admin.serializers.statistical import UserGoodsCountSerializer
from users.models import User
from goods.models import GoodsVisitCount

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
    """Daily user statistics registered"""
    # Permission
    permission_classes = [IsAdminUser]
    def get(self, request):
        # Get the day's date: datetime
        now_date = date.today()
        # Get the total number of registered users for the day
        count = User.objects.filter(date_joined__gte=now_date).count()
        # Return results
        return Response({'count': count, 'date': now_date})

class UserDayActiveView(APIView):
    """Daily user statistics logged"""
    # Permission
    permission_classes = [IsAdminUser]
    def get(self, request):
        # Get the day's date: datetime
        now_date = date.today()
        # Get the total number of logged users for the day
        count = User.objects.filter(last_login__gte=now_date).count()
        # Return results
        return Response({'count': count, 'date': now_date})

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


class UserMonthCountView(APIView):
    """Monthly Increase in Users"""
    # Permission
    permission_classes = [IsAdminUser]
    def get(self, request):
        # Get the day's date: datetime
        now_date = date.today()
        # Get the date one month ago
        begin_date = now_date - timedelta(days=29)
        data_list = []
        for i in range(30):
            # Start date
            index_date = begin_date + timedelta(days=i)
            # Date of the next day(Date of the day following the starting date)
            next_date = index_date + timedelta(days=i+1)
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=next_date).count()
            data_list.append({'count': count, 'date': index_date})
        # Return results
        return Response(data_list)


class UserGoodsCountView(APIView):
    """Statistics on daily visits to categorized products"""
    # Permission
    permission_classes = [IsAdminUser]
    def get(self, request):
        # Get the day's date: datetime
        now_date = date.today()
        # Get the number of category visits for the day
        goods = GoodsVisitCount.objects.filter(date__gte=now_date)
        ser = UserGoodsCountSerializer(goods, many=True)
        # Return results
        return Response(ser.data)