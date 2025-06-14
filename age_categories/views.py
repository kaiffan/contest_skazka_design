from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from age_categories.serializers import AgeCategoriesSerializer
from age_categories.models import AgeCategories


@extend_schema(
    summary="Получение списка возрастных категорий",
    description="Возвращает список всех возрастных категорий, доступных в системе.",
    responses={
        200: AgeCategoriesSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            name="Пример ответа",
            value=[
                {"id": 1, "name": "Дети", "min_age": 3, "max_age": 12},
                {"id": 2, "name": "Подростки", "min_age": 13, "max_age": 19},
            ],
            response_only=True,
            media_type="application/json",
        )
    ],
)
@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def get_age_categories_view(request: Request) -> Response:
    age_categories = AgeCategories.objects.all()

    serializer = AgeCategoriesSerializer(age_categories, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)
