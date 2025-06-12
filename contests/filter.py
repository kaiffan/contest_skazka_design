from django_filters import FilterSet, ModelMultipleChoiceFilter, NumberFilter, CharFilter

from age_categories.models import AgeCategories
from contest_stage.models import ContestStage
from contests.models import Contest


class ContestFilter(FilterSet):
    contest_category = NumberFilter(field_name="contest_category__id")
    contest_title = CharFilter(field_name="title", lookup_expr="icontains")
    age_category = ModelMultipleChoiceFilter(
        field_name="age_category__id",
        to_field_name="id",
        queryset=AgeCategories.objects.all(),
    )
    contest_stage = ModelMultipleChoiceFilter(
        field_name="contest_stage__id",
        to_field_name="id",
        queryset=ContestStage.objects.all(),
    )

    class Meta:
        model = Contest
        fields = [
            "contest_title",
            "contest_category",
            "age_category",
            "contest_stage",
        ]
