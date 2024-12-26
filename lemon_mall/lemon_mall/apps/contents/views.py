from django.shortcuts import render
from django.views import View
from collections import OrderedDict

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from contents.models import ContentCategory, Content
# Create your views here.


class IndexView(View):
    """Home Advertisement"""
    def get(self, request):
        """Provide homepage advertisement page"""
        # Search and display product categories
        # Prepare dictionaries corresponding to product categories
        categories = OrderedDict()
        # Check all product channels: 37 first level categories
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        # Iterate over all channels
        for channel in channels:
            # Get the group of the current channel
            group_id = channel.group_id
            # Constructing a basic data framework: Only 11 groups
            if group_id not in categories:
                categories[group_id] = {
                    'channels': [],
                    'sub_cats': []
                }

            # Query the first level category corresponding to the current channel
            cat1 = channel.category
            # Add cat1 to channels
            categories[group_id]['channels'].append({
                'id': cat1.id,
                'name': cat1.name,
                'url': channel.url
            })

            # Query secondary and tertiary categories
            for cat2 in cat1.subs.all():    # Finding secondary categories from primary categories
                cat2.sub_cats = []  # Add a list to the secondary category that holds the tertiary category
                for cat3 in cat2.subs.all():    # Finding a tertiary category from a secondary category
                    cat2.sub_cats.append(cat3)  # Adding third-level categories to second-level

                # Add secondary category to primary category sub_cats
                categories[group_id]['sub_cats'].append(cat2)

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
