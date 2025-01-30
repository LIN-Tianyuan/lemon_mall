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

    # Rewrite to get query set data
    def get_queryset(self):
        if self.request.query_params.get('keyword') == '':
            return User.objects.all()
        else:
            return User.objects.filter(username__contains=self.request.query_params.get('keyword'))