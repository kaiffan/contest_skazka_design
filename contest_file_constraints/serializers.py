from contest_file_constraints.models import ContestFileConstraints
from rest_framework.serializers import ModelSerializer

from file_constraints.serailizers import FileConstraintSerializer


class ContestFileConstraintsSerializer(ModelSerializer[ContestFileConstraints]):
    file_constraints = FileConstraintSerializer()

    class Meta:
        model = ContestFileConstraints
        fields = ["file_constraints"]
