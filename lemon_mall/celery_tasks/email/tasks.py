from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app


# bind: It is guaranteed that the task object will be automatically passed as the first argument
# name: asynchronous task alias
# retry_backoff: Exception Auto-Retry Interval n times(retry_backoff x 2^(n-1))s
# max_retries: Maximum number of automatic retries for exceptions
@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """Define tasks for sending validation emails"""
    # send_mail('title', 'message', 'sender', 'receiver list', 'rich text(html)')

    subject = "Lemon Mall Email Verification"
    html_message = '<p>Dear users, </p>' \
                '<p>Thank you for using Lemon Mall.</p>' \
                '<p>Your e-mail address is: %s . Please click on this link to activate your mailbox:</p>' \
                '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        # trigger an error retry: Maximum 3 tentatives
        raise self.retry(exc=e, max_retries=3)