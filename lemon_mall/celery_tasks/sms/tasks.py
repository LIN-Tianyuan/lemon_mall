# Define the task
from celery_tasks.sms.twilio.send_sms import CCP
from celery_tasks.main import celery_app


# Decorating asynchronous tasks with decorators ensures that celery recognizes the task
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """Asynchronous Tasks for Sending SMS CAPTCHA"""
    send_result = CCP().send_template_sms(mobile, f"Your verification code is {sms_code}. Please enter it correctly within 5 minutes.")
    return send_result
