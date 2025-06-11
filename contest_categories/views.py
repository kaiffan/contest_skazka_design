from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from block_user.permissions import IsNotBlockUserPermission
from contest_categories.models import ContestCategories
from contest_categories.serializers import ContestCategoriesSerializer


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def all_contest_categories_view(request):
    contest_categories = ContestCategories.objects.all()
    serializer = ContestCategoriesSerializer(contest_categories, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
