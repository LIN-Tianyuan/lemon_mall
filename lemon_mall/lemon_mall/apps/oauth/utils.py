from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData

from . import constants

def check_access_token(access_token_openid):
    """Decrypt, deserialize access_token_openid"""
    # Creating Serializer Objects: The parameters of serialized and deserialized objects must be exactly the same
    s = Serializer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    # Deserialize openid ciphertext
    try:
        data = s.loads(access_token_openid)
    except BadData: # openid cipher expired
        return None
    else:
        # Returns the openid plaintext
        return data.get('openid')

def generate_access_token(openid):
    """Signed, serialized openid"""
    # Creating Serializer Objects
    # s = Serializer('Secret key, the more complex the more secure', 'expiration date')
    s = Serializer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    # Prepare the dictionary data to be serialized
    data = {'openid': openid}
    # Call the dumps method to serialize: type is bytes
    token = s.dumps(data)
    # Return the serialized data
    return token.decode()
