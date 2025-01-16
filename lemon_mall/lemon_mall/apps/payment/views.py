from django.shortcuts import render
from django.views import View
from alipay import AliPay
from django.conf import settings
import os
from django import http

from lemon_mall.utils.views import LoginRequiredJSONMixin
from orders.models import OrderInfo
from lemon_mall.utils.response_code import RETCODE
from payment.models import Payment
# Create your views here.

class PaymentStatusView(LoginRequiredJSONMixin, View):
    """Save paid order status"""
    def get(self, request):
        # Get all the query string parameters
        query_dict = request.GET
        # Convert the types of query string parameters to standard dictionary types
        data = query_dict.dict()
        # Extracts and removes sign from the query string parameters and cannot participate in signature authentication
        signature = data.pop('sign')
        # Using the SDK object, call the authentication notification interface function, get validation results
        alipay = AliPay(    # Pass in public parameters(Docking any interface passes)
            appid=settings.ALIPAY_APPID,    # App id
            app_notify_url=None,  # Default callback url, If synchronized notifications are used they are not passed
            app_private_key_string=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem")).read(),
            alipay_public_key_string=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem")).read(),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        success = alipay.verify(data, signature)
        # If the validation passes, the paypal payment status needs to be processed(Bind the order ID of Beanie Mall with the order ID of Alipay, Modify Order Status)
        if success:
            # Order id maintained by beanie mall
            order_id = data.get('out_trade_no')
            # Order id maintained by alipay
            trade_id = data.get('trade_no')
            Payment.objects.create(
                order_id = order_id,
                trade_id = trade_id
            )
            # Modify order status from pending payment to pending evaluation
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])

            # Respond result
            context = {
                'trade_id': trade_id
            }
            return render(request, 'pay_success.html', context)
        else:
            return http.HttpResponseForbidden('非法请求')

class PaymentView(LoginRequiredJSONMixin, View):
    """Payment interface to Alipay"""
    def get(self, request, order_id):
        """
        :param order_id: Current order ID to be paid
        :return: JSON
        """
        user = request.user
        # Check order_id
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # Create SDK object to interface with Alipay interface
        alipay = AliPay(    # Pass in public parameters(Docking any interface passes)
            appid=settings.ALIPAY_APPID,    # App id
            app_notify_url=None,  # Default callback url, If synchronized notifications are used they are not passed
            app_private_key_string=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem")).read(),
            alipay_public_key_string=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem")).read(),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        # SDK object interfaces with Alipay payment to get the address of the login page
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # order id
            total_amount=str(order.total_amount),   # order Payment Amount
            subject="小帽商城%s" % order_id,    # Order Title
            return_url=settings.ALIPAY_RETURN_URL,  # Callback address for synchronized notifications
        )
        # Splice the full login page address
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})