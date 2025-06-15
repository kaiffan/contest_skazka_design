from datetime import date
from typing import Dict, Any

from django.core.cache import cache

from contests.models import Contest
from contests_contest_stage.models import ContestsContestStage


def get_current_contest_stage(contest_id: int) -> Dict[str, Any]:
    current_stage = cache.get(key=f"current_contest_stage_{contest_id}", default=None)
    today = date.today()

    if not current_stage:
        current_stage = ContestsContestStage.objects.filter(
            contest_id=contest_id,
            start_date__lte=today,
            end_date__gte=today,
        ).first()
        if current_stage:
            cache.set(
                key="current_contest_stage_{contest_id}",
                value=current_stage,
                timeout=60 * 30,
            )

    if not current_stage:
        return {"name": "Закончен"}

    if current_stage.start_date > today:
        return {"name": "Запланирован"}

    if current_stage.end_date < today:
        return {"name": "Закончен"}

    return {
        "name": current_stage.stage.name,
        "start_date": current_stage.start_date,
        "end_date": current_stage.end_date,
    }
