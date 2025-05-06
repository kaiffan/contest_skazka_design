from django.http import JsonResponse
from rest_framework import status


class ContestHeaderMiddleware:
    def __init__(self, response):
        self.response = response

    def __call__(self, request):
        contest_id = request.headers.get('X-Contest-ID')

        if contest_id:
            try:
                request.contest_id = int(contest_id)
            except (ValueError, TypeError):
                return JsonResponse(
                    data={
                        "error": "X-Contest-ID is not a valid contest ID"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            request.contest_id = None

        return self.response(request)
