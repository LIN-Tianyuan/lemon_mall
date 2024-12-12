from django.db import models

class BaseModel(models.Model):
    """Supplemental fields for model classes"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="update time")

    class Meta:
        abstract = True  # It means that it is an abstract model class, used for inheritance, and the tables of BaseModel will not be created during database migration.