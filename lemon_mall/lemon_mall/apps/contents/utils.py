from collections import OrderedDict
from goods.models import GoodsChannel


def get_categories():
    """Get Product Category"""
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
    return categories