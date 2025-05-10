from datetime import date
from typing import Dict, Any

from contests.models import Contest


def get_current_contest_stage(instance: Contest) -> Dict[str, Any]:
    today = date.today()
    current_stage = next(
        (
            stage
            for stage in instance.contest_stage.through.objects.filter(contest=instance)
            if stage.start_date <= today <= stage.end_date
        ),
        None,
    )

    if current_stage:
        return {
            "name": current_stage.contest_stage.name,
            "start_date": current_stage.start_date,
            "end_date": current_stage.end_date,
        }

    return {"name": "Contest stage is not defined"}
