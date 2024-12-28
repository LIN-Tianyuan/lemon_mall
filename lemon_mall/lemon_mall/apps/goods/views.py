from django.shortcuts import render
from django.views import View
from django import http
# Paginator (there are a million texts that need to be made into a book, first specify how many texts per page and then figure out how many pages in total)
# Records in the database are text, we need to consider the number of records per page when paging and then figure out how many pages there are in total
from django.core.paginator import Paginator, EmptyPage

from goods.models import GoodsCategory
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from goods.models import SKU
from lemon_mall.utils.response_code import RETCODE


class HotGoodsView(View):
    """top seller"""
    def get(self, request, category_id):
        # Query SKU information for a specified category, and it has to be on the shelf, then sort by sales volume from highest to lowest, and finally slice out the top two
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
        # Convert model list to dictionary list, construct JSON data
        hot_skus = []
        for sku in skus:
            sku_dict = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            }
            hot_skus.append(sku_dict)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})

# Create your views here.
class ListView(View):
    """Product List Page"""
    def get(self, request, category_id, page_num):
        """Query and render the product listings page"""
        # Check the parameter: category_id
        try:
            # Tertiary category
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id不存在')

        # Get sort(Sorting rules): If sort does not have a value, take default
        sort = request.GET.get('sort', 'default')
        # Select sorted fields based on sort, the sort field must be a property of the model class
        if sort == 'price':
            sort_field = 'price'    # Sort by price from lowest to highest
        elif sort == 'hot':
            sort_field = '-sales'   # Sort by sales volume from highest to lowest
        else:   # All other cases are categorized as default as long as they are not 'price' and 'sales'
            sort = 'default'    # When ?sort=alex appears, also set sort to default.
            sort_field = 'create_time'



        # Search by product category
        categories = get_categories()

        # Query Breadcrumb Navigation: First -> Second -> Third
        breadcrumb = get_breadcrumb(category)

        # Pagination and sorted queries: category query sku, a query for multiple, one-sided model objects. Multi-party associated fields.all/filter
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)

        # Creating a Paginator
        # Paginator('Data to be paged', 'Number of records per page')
        paginator = Paginator(skus, 5)  # Pagination of skus with 5 records per page
        try:
            # Get the page the user is currently looking at(Core data)
            page_skus = paginator.page(page_num)    # Gets the five records in the page_nums page.
        except EmptyPage:
            return http.HttpResponseNotFound('Empty Page')

        # Get Total Pages: The front-end paging plugin requires the use
        total_page = paginator.num_pages

        # construct a context
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'page_skus': page_skus,
            'total_page': total_page,
            'page_num': page_num,
            'sort': sort,
            'category_id': category_id
        }
        return render(request, 'list.html', context)
