import base64, pickle
from django_redis import get_redis_connection


def merge_carts_cookies_redis(request, user, response):
    """Merge cart"""
    # Get shopping cart data from cookies
    cart_str = request.COOKIES.get('carts')
    # Determining if shopping cart data exists in cookies
    if not cart_str:
        return response
    # Convert cart_str to a string of type bytes
    cookie_cart_str_bytes = cart_str.encode()
    # Convert cart_str_bytes to dictionary of type bytes
    cookie_cart_dict_bytes = base64.b64decode(cookie_cart_str_bytes)
    # Convert cart_dict_bytes to a real dictionary
    cookie_cart_dict = pickle.loads(cookie_cart_dict_bytes)
    # No need to merge if it does not exist
    # If present, needs to be merged
    # Prepare new data container: save new sku_id:count, selected, unselected
    new_cart_dict = {}
    new_selected_add = []
    new_selected_rem = []
    # Iterate over the shopping cart data in the cookies
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)

    # Merge into redis based on the new data structure
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_%s' % user.id, new_cart_dict)
    if new_selected_add:
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)
    pl.execute()

    # Delete cookies
    response.delete_cookie('carts')
    return response
