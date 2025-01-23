# Static Home Page
from collections import OrderedDict
from django.template import loader
import os
from django.conf import settings

from contents.utils import get_categories
from contents.models import ContentCategory

def generate_static_index_html():
    """Static Home Page"""
    # Query data on the home page
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

    # Render Templates
    # Get the template file first
    template = loader.get_template('index.html')
    # Then render the template file using the context
    html_text = template.render(context)
    # Write template files to static paths
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)