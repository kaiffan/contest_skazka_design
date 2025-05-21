from datetime import date
from typing import Dict, Any

from django.core.cache import cache

from contests.models import Contest
from contests_contest_stage.models import ContestsContestStage


def get_current_contest_stage(contest: Contest) -> Dict[str, Any]:
    current_stage = cache.get(key="current_contest_stage", default=None)

    if not current_stage:
        current_stage = ContestsContestStage.objects.filter(
            contest_id=contest.id,
            start_date__lte=date.today(),
            end_date__gte=date.today(),
        ).first()

        if current_stage:
            cache.set(
                key="current_contest_stage", value=current_stage, timeout=60 * 60 * 12
            )

    if not current_stage:
        return {"name": "Contest stage is not defined"}

    return {
        "name": current_stage.stage.name,
        "start_date": current_stage.start_date,
        "end_date": current_stage.end_date,
    }
