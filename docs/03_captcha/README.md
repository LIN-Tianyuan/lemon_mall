# 3. Captcha
## 3.1 Graphical captcha
 - View
```python
# verifications/views.py
class ImageCodeView(View):
    """graphical captcha"""

    def get(self, request, uuid):
        pass
```
 - Route
```python
# lemon_mall/urls.py
urlpatterns = [
    re_path(r'^', include('verifications.urls'))
]
```
```python
# verifications/urls.py
urlpatterns = [
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
]
```
 - Captcha Expansion Pack
 ```bash
 pip install Pillow
 ```
- Preparing the Redis Database
```python
# settings/dev.py
{
 "verify_code": {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": "redis://127.0.0.1:6379/2",
    "OPTIONS": {
        "CLIENT_CLASS": "django_redis.client.DefaultClient",
    }
}
```
- backend
```python
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

```
 - frontend
```javascript
// register.js
mounted(){
    // Generate graphical CAPTCHA
    this.generate_image_code();
},
methods: {
    // Generate graphical CAPTCHA
    generate_image_code(){
        // Generate UUID。generateUUID() : Encapsulation is in the common.js file, which needs to be introduced in advance
        this.uuid = generateUUID();
        // Splice Graphics CAPTCHA Request Address
        this.image_code_url = "/image_codes/" + this.uuid + "/";
    },
    ......
}
```
```html
<!-- register.html -->
<li>
    <label>Graphical CAPTCHA:</label>
    <input type="text" name="image_code" id="pic_code" class="msg_input">
    <img :src="image_code_url" @click="generate_image_code" alt="Graphical CAPTCHA" class="pic_code">
    <span class="error_tip">Please fill in the graphic verification code</span>
</li>
```
## 3.2 SMS CAPTCHA
 - Twilio
```python
class CCP(object):
    """Singleton class for sending SMS verification codes"""
    def __new__(cls, *args, **kwargs):
        # Define the initialization method of the singleton
        # Determine if a singleton exists: what's stored in the _instance property is the singleton
        if not hasattr(cls, '_instance'):
            # If the singleton doesn't exist, initialize the singleton
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            cls._instance.client = Client(account_sid, auth_token)
        # Return to the singleton
        return cls._instance

    def send_template_sms(self, to, datas):
        """Single-case method for sending an SMS verification code"""
        message = self.client.messages.create(
            body=datas,
            from_="+17755005216",
            to=to,
        )
        if message.status == 'queued':
            return 0
        else:
            return -1
```
 - backend
```python
class SMSCodeView(View):
    """SMS verification code"""
    def get(self, request, mobile):
        # Receiving parameters
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # Calibration parameters
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('Missing mandatory parameters')

        # Creating an object to connect to redis
        redis_conn = get_redis_connection('verify_code')
        # Determine whether the user sends SMS verification code frequently
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': 'Send messages too frequently'})
        # Extracting the markers for sending SMS verification codes

        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Graphical Code no longer works'})
        # Remove graphical captcha
        redis_conn.delete('img_%s' % uuid)
        # Compare graphical CAPTCHAs
        image_code_server = image_code_server.decode()  # Convert bytes to strings and compare
        if image_code_client.lower() != image_code_server.lower():  # Lowercase and compare
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': 'Incorrectly entered graphical verification code'})
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
        # send_sms_code.delay(mobile, sms_code)

        # Response results
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'Send SMS successfully'})
```