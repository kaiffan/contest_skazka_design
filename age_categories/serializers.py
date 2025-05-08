from rest_framework.serializers import ModelSerializer
from age_categories.models import AgeCategories


class AgeCategoriesSerializer(ModelSerializer[AgeCategories]):
    class Meta:
        model = AgeCategories
        fields = "__all__"
