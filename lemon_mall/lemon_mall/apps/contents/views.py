from django.shortcuts import render
from django.views import View
from collections import OrderedDict

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from contents.models import ContentCategory
from contents.utils import get_categories
# Create your views here.


class IndexView(View):
    """Home Advertisement"""
    def get(self, request):
        """Provide homepage advertisement page"""
        # Search and display product categories
        # Prepare dictionaries corresponding to product categories
        categories = get_categories()

        # Check homepage advertisement data
        # Check all advertisement categories
        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')   # Check out and sort the unlisted ads

        # Use the advertisement category to find out the content of all advertisements corresponding to the category.

        # Construct context
        context = {
            'categories': categories,
            'contents': contents
        }
        return render(request, 'index.html', context)
