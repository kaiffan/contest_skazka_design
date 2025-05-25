from django_filters import FilterSet, CharFilter

from applications.models import Applications


class ApplicationFilter(FilterSet):
    status = CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = Applications
        fields = ["status"]
