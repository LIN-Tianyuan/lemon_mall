from django.db import models


# Create your models here.
class Area(models.Model):
    """Province City District"""
    name = models.CharField(max_length=20, verbose_name='Name')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='Upper administrative subdivision')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = 'Provincial City District'
        verbose_name_plural = 'Provincial City District'

    def __str__(self):
        return self.name