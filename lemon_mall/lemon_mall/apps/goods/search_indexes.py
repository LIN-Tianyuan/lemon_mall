from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """SKU Index Data Model Class"""
    # Receive Index Fields, defining Index Fields with Documents, and rendered using the template syntax
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """Returns the indexed model class"""
        return SKU

    def index_queryset(self, using=None):
        """Returns the query set of data to be indexed"""
        return self.get_model().objects.filter(is_launched=True)