from rest_framework.serializers import ModelSerializer

from contest_categories.models import ContestCategories


class ContestCategoriesSerializer(ModelSerializer[ContestCategories]):
    class Meta:
        model = ContestCategories
        fields = "__all__"
