from django.shortcuts import render
from lemon_mall.utils.views import LoginRequiredMixin
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal

from users.models import Address
from goods.models import SKU

# Create your views here.

class OrderSettlementView(LoginRequiredMixin, View):
    """settlement order"""

    def get(self, request):
        """Query and display order data to be billed"""
        # Get logged user
        user = request.user
        # Query user's shipping address: Query the registered user's shipping address that has not been deleted.
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            # If the address is not looked up, you can go to edit the shipping address
            addresses = None
        # Check checked items in the shopping cart
        redis_conn = get_redis_connection('carts')
        # All shopping cart data with checked and unchecked boxes: {b'1': b'1', b'2': b'2'}
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        # The sku_id of the checked item: [b'1']
        redis_selected = redis_conn.smembers('selected_%s' % user.id)
        # Construct data for checked items in the shopping cart {b'1':'1'}
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])
        # Iterate over new_cart_dict and take out the sku_id and count from it
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        total_count = Decimal(0.00)
        total_amount = 0
        # Take out all the sku
        for sku in skus:
            # Iterate over skus to replenish count and amount for each sku
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count

            # Cumulative number and amount
            total_count += sku.count
            total_amount += sku.amount  # Different types do not compute

        # Specify default postage
        freight = Decimal(10.00)

        # Construct context
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request, 'place_order.html', context)