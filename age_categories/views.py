from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from age_categories.serializers import AgeCategoriesSerializer
from age_categories.models import AgeCategories


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated])
def get_age_categories_view(request: Request) -> Response:
    age_categories = AgeCategories.objects.all()

    serializer = AgeCategoriesSerializer(age_categories, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)
