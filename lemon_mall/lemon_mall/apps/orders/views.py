from django.shortcuts import render
from lemon_mall.utils.views import LoginRequiredMixin
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django import http
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage

from users.models import Address
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from lemon_mall.utils.response_code import RETCODE
# Create your views here.
class OrderCommentView(LoginRequiredMixin, View):
    """Order Product Evaluation"""

    def get(self, request):
        """Show product evaluation page"""
        # Reception parameters
        order_id = request.GET.get('order_id')
        # Check parameters
        try:
            OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('订单不存在')

        # Check the information of the products that have not been evaluated in the order.
        try:
            uncomment_goods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        except Exception:
            return http.HttpResponseServerError('订单商品信息出错')

        # Constructing data on commodities to be evaluated
        uncomment_goods_list = []
        for goods in uncomment_goods:
            uncomment_goods_list.append({
                'order_id':goods.order.order_id,
                'sku_id':goods.sku.id,
                'name':goods.sku.name,
                'price':str(goods.price),
                'default_image_url':goods.sku.default_image.url,
                'comment':goods.comment,
                'score':goods.score,
                'is_anonymous':str(goods.is_anonymous),
            })

        # Render templates
        context = {
            'uncomment_goods_list': uncomment_goods_list
        }
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        """Evaluate Ordered Products"""
        # Receive parameters
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')
        # Check parameters
        if not all([order_id, sku_id, score, comment]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            OrderInfo.objects.filter(order_id=order_id, user=request.user, status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('参数order_id错误')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        if is_anonymous:
            if not isinstance(is_anonymous, bool):
                return http.HttpResponseForbidden('参数is_anonymous错误')

        # Saving order product evaluation data
        OrderGoods.objects.filter(order_id=order_id, sku_id=sku_id, is_commented=False).update(
            comment=comment,
            score=score,
            is_anonymous=is_anonymous,
            is_commented=True
        )

        # Cumulative comment data
        sku.comments += 1
        sku.save()
        sku.spu.comments += 1
        sku.spu.save()

        # If all orders have been evaluated, change the order status to Completed.
        if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '评价成功'})

class OrderSuccessView(LoginRequiredMixin, View):
    """Submit Order Success Page"""
    def get(self, request):
        """"""
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }

        return render(request, 'order_success.html', context)

class OrderCommitView(LoginRequiredMixin, View):
    """Submit order"""
    def post(self, request):
        """Save basic order information and order product information"""
        # Receive parameter
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # Check parameter
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        # Determine whether address_id is legal or not
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('参数address_id错误')
        # Determine if pay_method is legal
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        # Explicitly open of a transaction
        with transaction.atomic():
            # Savepoints need to be specified before database operations(Preserve the initial state of the database)
            save_id = transaction.savepoint()
            # brute force rollback
            try:
                # Get user
                user = request.user
                # Get order id: time + user_id == '202501142309000000001'
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

                # Save basic order information
                order = OrderInfo.objects.create(
                    order_id = order_id,
                    user = user,
                    address = address,
                    total_count = 0,
                    total_amount = Decimal(0.00),
                    freight = Decimal(10.00),
                    pay_method = pay_method,
                    # status = 'UNPAID' if pay_method=='ALIPAY' else 'UNSEND'
                    status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                # Save order product information
                # Find out what products are checked in the shopping cart.
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
                for sku_id in sku_ids:
                    # Each item has multiple chances to place an order until stock runs out
                    while True:
                        # Read cart product information
                        sku = SKU.objects.get(id=sku_id)    # When querying for product and inventory information, no caching can occur, so no filter(id__in=sku_ids) is used

                        # Access to raw inventory and sales
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        # Get the quantity of the item for which the order is to be submitted
                        sku_count = new_cart_dict[sku.id]
                        # Determine whether the quantity of the item is greater than the inventory, and if so, respond to insufficient inventory
                        if sku_count > origin_stock:
                            # Insufficient inventory, rollback
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # sku reduces inventory and increases sales
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        # Returns 0 if the original data changed while updating the data; indicates a resource grab
                        if result == 0:
                            # return http.JsonResponse('')
                            continue

                        # sku increases sales
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        OrderGoods.objects.create(
                            order = order,
                            sku = sku,
                            count = sku_count,
                            price = sku.price
                        )

                        # Accumulate the quantity and total price of the order items to the basic order information table.
                        order.total_count += sku_count
                        order.total_amount += sku_count * sku.price

                        # Order successful, break
                        break

                order.total_amount += order.freight
                order.save()
            except Exception as e:
                print(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # Successful database operation, Explicitly commit a transaction
            transaction.savepoint_commit(save_id)


        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})
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