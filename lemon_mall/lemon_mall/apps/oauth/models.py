from django.db import models
from lemon_mall.utils.models import BaseModel

# Create your models here.

class OAuthQQUser(BaseModel):
    """QQ Login User Data"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='user')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ Login User Data'
        verbose_name_plural = verbose_name