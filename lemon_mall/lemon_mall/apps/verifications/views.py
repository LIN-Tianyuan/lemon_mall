from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
import random, logging


from verifications.libs.twilio.send_sms import CCP
from verifications.libs.captcha.captcha import captcha
from . import constants
from lemon_mall.utils.response_code import RETCODE
from celery_tasks.sms.tasks import send_sms_code

# Create your views here.

# Creating a log exporter
logger = logging.getLogger('django')


class ImageCodeView(View):
    """graphical captcha"""

    def get(self, request, uuid):
        """
        :param uuid: Generic Unique Identifier, which uniquely identifies the user to whom the graphical CAPTCHA belongs
        :return: image/jpg
        """
        # Implementing the main business logic: generating, saving, and responding to graphical CAPTCHAs
        # Generate
        text, image = captcha.generate_captcha()
        # Save
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.setex('key', 'expires', 'value')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # Responding to results
        return http.HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    """SMS verification code"""
    def get(self, request, mobile):
        # Receiving parameters
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # Calibration parameters
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # Creating an object to connect to redis
        redis_conn = get_redis_connection('verify_code')
        # Determine whether the user sends SMS verification code frequently
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})
        # Extracting the markers for sending SMS verification codes

        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        # Remove graphical captcha
        redis_conn.delete('img_%s' % uuid)
        # Compare graphical CAPTCHAs
        image_code_server = image_code_server.decode()  # Convert bytes to strings and compare
        if image_code_client.lower() != image_code_server.lower():  # Lowercase and compare
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})
        # Generate SMS verification code: Random 6-digit number
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)   # Manual output logging of SMS verification codes
        # Save SMS Verification Code
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # Save the mark for sending SMS verification code
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # Create a redis pipeline
        pl = redis_conn.pipeline()
        # Adding commands to the queue
        # Save SMS Verification Code
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # Save the mark for sending SMS verification code
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # Execute
        pl.execute()

        # Send SMS Verification Code
        # CCP().send_template_sms(mobile, f"Your verification code is {sms_code}. Please enter it correctly within 5 minutes.")
        # Sending SMS CAPTCHA with Celery
        # send_sms_code(mobile, sms_code) wrong
        send_sms_code.delay(mobile, sms_code)

        # Response results
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'Send SMS successfully'})