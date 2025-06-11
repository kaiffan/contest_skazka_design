from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from block_user.permissions import IsNotBlockUserPermission
from competencies.models import Competencies
from competencies.serializers import CompetenciesSerializer


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def all_competencies_view(request):
    competencies = Competencies.objects.all()
    serializer = CompetenciesSerializer(competencies, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
