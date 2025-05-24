from rest_framework.exceptions import Throttled
from rest_framework.throttling import AnonRateThrottle

from email_confirmation.models import EmailConfirmationLogin
from contest_backend.settings import settings


# class CodeBasedThrottle(AnonRateThrottle):
#     scope = "code_attempt"
#     rate = "5/min"
#     throttle_exception = Throttled(
#         detail="Слишком много попыток ввести этот код. Попробуйте позже."
#     )
#
#     def get_cache_key(self, request, view):
#         code = request.data.get("code")
#         if not code or len(code) != settings.email_credentials.CODE_DIGITS:
#             return None
#
#         code_hash = EmailConfirmationLogin.hash_code(code)
#         return self.cache_format % {
#             "scope": self.scope,
#             "ident": code_hash,
#         }
#
#
# class IpBasedThrottle(AnonRateThrottle):
#     scope = "ip_attempt"
#     rate = "30/min"
#     throttle_exception = Throttled(detail="Слишком много попыток. Попробуйте позже.")
#
#     def get_cache_key(self, request, view):
#         ip = request.META.get("REMOTE_ADDR")
#         if not ip:
#             return None
#
#         return self.cache_format % {
#             "scope": self.scope,
#             "ident": ip,
#         }
