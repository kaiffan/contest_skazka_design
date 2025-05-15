from typing import List

from applications.models import Applications
from contests.models import Contest
from work_rate.models import WorkRate


def validate_count_criteria_by_contest(
    contest: Contest, application: Applications
) -> bool:
    all_criteria_ids: List[int] = [criteria.id for criteria in contest.criteria.all()]
    rated_criteria_ids: List[int] = list(
        WorkRate.objects.filter(application_id=application.id).values_list(
            "criteria_id", flat=True
        )
    )
    print(all_criteria_ids)
    print(rated_criteria_ids)

    if set(all_criteria_ids) != set(rated_criteria_ids):
        return False

    return True
