from datetime import date
from typing import Dict, Any

from django.core.cache import cache

from contests.models import Contest
from contests_contest_stage.models import ContestsContestStage


def get_current_contest_stage(contest_id: int) -> Dict[str, Any]:
    today = date.today()
    cache_key = f"current_contest_stage_{contest_id}"

    current_stage = cache.get(key=cache_key)

    if not current_stage:
        current_stage = ContestsContestStage.objects.filter(
            contest_id=contest_id,
            start_date__lte=today,
            end_date__gte=today,
        ).first()
        if current_stage:
            cache.set(cache_key, current_stage, timeout=60 * 30)

    if current_stage:
        return {
            "name": current_stage.stage.name,
            "start_date": current_stage.start_date,
            "end_date": current_stage.end_date,
        }

    future_stages_exist = ContestsContestStage.objects.filter(
        contest_id=contest_id,
        start_date__gt=today
    ).exists()

    return {"name": "Запланирован" if future_stages_exist else "Закончен"}
