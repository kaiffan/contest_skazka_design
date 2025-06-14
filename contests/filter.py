from datetime import date

from django_filters import (
    FilterSet,
    ModelMultipleChoiceFilter,
    NumberFilter,
    CharFilter,
)

from age_categories.models import AgeCategories
from contest_stage.models import ContestStage
from contests.models import Contest


class ContestFilter(FilterSet):
    contest_title = CharFilter(field_name="title", lookup_expr="icontains")

    age_category = ModelMultipleChoiceFilter(
        field_name="age_category",
        queryset=AgeCategories.objects.all(),
    )

    contest_stage = ModelMultipleChoiceFilter(
        queryset=ContestStage.objects.all(),
        field_name="contestsconteststage__stage",
        to_field_name="id",
        conjoined=False,
        method="filter_contest_stage_with_current_check",
    )

    class Meta:
        model = Contest
        fields = [
            "contest_title",
            "age_category",
            "contest_stage",
        ]

    def filter_contest_stage_with_current_check(self, queryset, name, value):
        if not value:
            return queryset

        today = date.today()

        stage_ids = [
            contest_stage.id if hasattr(contest_stage, "id") else contest_stage
            for contest_stage in value
        ]

        return queryset.filter(
            contestsconteststage__stage_id__in=stage_ids,
            contestsconteststage__start_date__lte=today,
            contestsconteststage__end_date__gte=today,
        ).distinct()
