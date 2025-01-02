from django.shortcuts import render
from django.views import View
from django import http
# Paginator (there are a million texts that need to be made into a book, first specify how many texts per page and then figure out how many pages in total)
# Records in the database are text, we need to consider the number of records per page when paging and then figure out how many pages there are in total
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone   # Tools for handling time
from datetime import datetime

from goods.models import GoodsCategory
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from goods.models import SKU, GoodsVisitCount
from lemon_mall.utils.response_code import RETCODE

class DetailVisitView(View):
    """Statistics on the number of visits to categorized products"""
    def post(self, request, category_id):
        # Receive parameter, check parameter
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('category_id 不存在')

        # Get the date of the day
        t = timezone.localtime()
        # Get the time string of the day
        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        # Converts the day's time string into a datetime object, in order to match the type of the date field.
        today_date = datetime.strptime(today_str, '%Y-%m-%d')    # Time String to Time Object
        # Statistics on the number of visits to categorized products
        # Determine whether the record corresponding to the specified product category exists on the same day.
        try:
            # If it exists, get directly to the object where the record exists
            counts_data = GoodsVisitCount.objects.get(date=today_date, category=category)
        except GoodsVisitCount.DoesNotExist:
            # If it doesn't exist, the object corresponding to the record is created directly
            counts_data = GoodsVisitCount()

        try:
            counts_data.category = category
            counts_data.count += 1
            counts_data.date = today_date
            counts_data.save()
        except Exception as e:
            return http.HttpResponseServerError('统计失败')
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})



class DetailView(View):
    """Product Details Page"""

    def get(self, request, sku_id):
        """Product Details Page"""
        # Receive parameter, check parameter
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')
        # Search by product category
        categories = get_categories()
        # Breadcrumb navigation
        breadcrumb = get_breadcrumb(sku.category)
        # Check Sku
        # Construct a specification key for the current item
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # Get all SKUs of the current product
        skus = sku.spu.sku_set.all()
        # Construct sku dictionaries for different specification parameters (options)
        spec_sku_map = {}
        for s in skus:
            # Get sku specifications
            s_specs = s.specs.order_by('spec_id')
            # Keys used to form the specification-parameter-sku dictionary
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # Adding records to the specification-parameters-sku dictionary
            spec_sku_map[tuple(key)] = s.id
        # Get the specification information of the current product
        goods_specs = sku.spu.specs.order_by('id')
        # If the specification information for the current sku is incomplete, it will not be continued
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # Copy the specification key of the current sku
            key = sku_key[:]
            # Options for this specification
            spec_options = spec.options.all()
            for option in spec_options:
                # Find a sku that matches the current specification in the specification parameter sku dictionary
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options
        # Construct Context
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs
        }
        return render(request, 'detail.html', context)

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
