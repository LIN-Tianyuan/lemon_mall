# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = ''
auth_token = ''


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


if __name__ == '__main__':
    # Singleton class sends SMS verification code
    CCP().send_template_sms("+33768915934", "This is the ship that made the Kessel Run in fourteen parsecs?")