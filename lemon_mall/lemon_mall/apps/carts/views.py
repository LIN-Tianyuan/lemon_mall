from django.shortcuts import render
from django.views import View
import json, base64, pickle
from django import http
from django_redis import get_redis_connection
from lemon_mall.utils.response_code import RETCODE

from goods.models import SKU


# Create your views here.
class CartsView(View):
    """Shopping cart"""
    def post(self, request):
        """Save Shopping Cart"""
        # Receive parameters
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)    # selectable

        # Verify parameters
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')

        # Verify sku_id is legal
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        # Check if count is a number
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count有误')

        # Check if the checkmark is bool
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')
        # Determine if the user is logged in
        user = request.user
        if user.is_authenticated:
            # If the user is logged in, operate the Redis shopping cart
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # Need to save commodity data in the form of incremental calculations
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            # Save product check status
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            # Respond result
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # Manipulate cookie shopping cart if user is not logged in
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # Convert cart_str to a string of type bytes
                cart_str_bytes = cart_str.encode()
                # Convert cart_str_bytes to dictionary of type bytes
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # Convert cart_dict_bytes to a real dictionary
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            # Determine if the current product to be added exists in the cart_dict
            if sku_id in cart_dict:
                # Shopping cart already exists, incremental calculation
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # Convert cart_dict to dictionary of type bytes
            cart_dict_bytes = pickle.dumps(cart_dict)
            # Convert cart_dict_bytes to a string of type bytes
            cart_str_bytes = base64.b64decode(cart_dict_bytes)
            # Convert cart_str_bytes to string
            cookie_cart_str = cart_str_bytes.decode()

            # Write new cart data to cookie
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            response.set_cookie('carts', cookie_cart_str)

            # Respond result
            return response

    def get(self, request):
        """Search cart"""
        # Determine whether a user is logged in or not
        user = request.user
        if user.is_authenticated:
            # User is logged in, query redis cart
            # Create an object to connect to redis
            redis_conn = get_redis_connection('carts')
            # Query hash data
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # Query set data
            redis_selected = redis_conn.smembers('selected_%s' % user.id)
            cart_dict = {}
            # Construct redis_cart and redis_selected as a data structure, merge the data, the structure of the data is the same as the structure of the shopping cart for non-logged-in users.
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_selected
                }
            pass
        else:
            # User is not logged in, check cookies shopping cart
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # Convert cart_str to a string of type bytes
                cart_str_bytes = cart_str.encode()
                # Convert cart_str_bytes to dictionary of type bytes
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # Convert cart_dict_bytes to a real dictionary
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

        # Construct Response Data
        # Get all the keys in the dictionary
        sku_ids = cart_dict.keys()
        # Query all skus at once
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id':sku.id,
                'name':sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # Turn True, to 'True', for easier json parsing
                'default_image_url':sku.default_image.url,
                'price':str(sku.price), # Remove '10.2' from Decimal('10.2') for easy json parsing
                'amount':str(sku.price * cart_dict.get(sku.id).get('count')),
            })

        context = {
            'cart_skus':cart_skus,
        }

        return render(request, 'cart.html', context)


