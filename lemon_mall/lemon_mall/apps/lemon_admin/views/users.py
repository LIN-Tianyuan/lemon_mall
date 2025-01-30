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