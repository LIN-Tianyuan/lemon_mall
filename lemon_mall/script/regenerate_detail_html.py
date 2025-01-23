#!/usr/bin/env python

import sys
sys.path.insert(0, '../')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lemon_mall.settings.dev'

import django
django.setup()

from django.template import loader
from django.conf import settings

from goods import models
from contents.utils import get_categories
from goods.utils import get_breadcrumb


def generate_static_sku_detail_html(sku_id):
    """
    Generate static product detail pages
    :param sku_id: product sku id
    """
    # Get information about the current sku
    sku = models.SKU.objects.get(id=sku_id)

    # Search by product channel
    categories = get_categories()
    # Query Breadcrumb Navigation
    breadcrumb = get_breadcrumb(sku.category)

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
        # Add records to the specification-parameters-sku dictionary
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

    # context
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,
    }

    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'detail/'+str(sku_id)+'.html')
    with open(file_path, 'w') as f:
        f.write(html_text)


if __name__ == '__main__':
    skus = models.SKU.objects.all()
    for sku in skus:
        print(sku.id)
        generate_static_sku_detail_html(sku.id)