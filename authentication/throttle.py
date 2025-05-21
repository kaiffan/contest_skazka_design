from rest_framework.exceptions import Throttled
from rest_framework.throttling import AnonRateThrottle


class LoginAnonThrottle(AnonRateThrottle):
    rate = "5/min"
    throttle_exception = Throttled(
        detail="Слишком много попыток входа. Попробуйте позже."
    )
