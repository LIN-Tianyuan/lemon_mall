from rest_framework import serializers
from goods.models import GoodsVisitCount

class UserGoodsCountSerializer(serializers.ModelSerializer):
    # Nested Serialization Return Field Specification
    category = serializers.StringRelatedField(read_only=True)
    class Meta:
        model=GoodsVisitCount
        fields=('category', 'count')