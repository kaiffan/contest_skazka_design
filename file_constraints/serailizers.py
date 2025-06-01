from rest_framework.serializers import ModelSerializer

from file_constraints.models import FileConstraint


class FileConstraintSerializer(ModelSerializer[FileConstraint]):
    class Meta:
        model = FileConstraint
        fields = "__all__"
