from django.http import JsonResponse
from rest_framework import status


class ContestHeaderMiddleware:
    def __init__(self, response):
        self.response = response

    def __call__(self, request):
        contest_id = request.headers.get("X-Contest-Id", None)

        if not contest_id:
            request.contest_id = None
            return self.response(request)
        try:
            request.contest_id = int(contest_id)
        except (ValueError, TypeError):
            print("Ты дурак")
            return JsonResponse(
                data={"error": "X-Contest-Id is not a valid contest ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.response(request)
