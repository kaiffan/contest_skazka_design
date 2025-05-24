from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def get_vk_news_view(request: Request) -> Response:
    pass
