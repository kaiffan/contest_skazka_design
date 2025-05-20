from django_filters import FilterSet

from contests.models import Contest


class ContestFilter(FilterSet):
    class Meta:
        model = Contest
        fields = {
            "region": ["exact"],
            "contest_stage": ["exact"],
            "age_category": ["exact"],
            "contest_category": ["exact"],
        }
