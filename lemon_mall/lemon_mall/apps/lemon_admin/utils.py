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