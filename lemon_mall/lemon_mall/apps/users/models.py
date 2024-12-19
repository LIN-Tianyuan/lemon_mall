from django.db import models
from django.contrib.auth.models import AbstractUser

from lemon_mall.utils.models import BaseModel


# Create your models here.
class User(AbstractUser):
    """Custom User Model Classes"""
    mobile = models.CharField(max_length=15, unique=True, verbose_name='Mobile')
    email_active = models.BooleanField(default=False, verbose_name='Email Verification Status')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Default address')

    class Meta:
        db_table = 'tb_users'    # Custom Table Names
        verbose_name = 'User'   # User
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='User')
    title = models.CharField(max_length=20, verbose_name='Address name')
    receiver = models.CharField(max_length=20, verbose_name='Receiver')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='Province')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='City')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='District')
    place = models.CharField(max_length=50, verbose_name='Address')
    mobile = models.CharField(max_length=11, verbose_name='Mobile')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='Telephone')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='Email')
    is_deleted = models.BooleanField(default=False, verbose_name='Logical delete')

    class Meta:
        db_table = 'tb_address'
        verbose_name = 'User address'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
