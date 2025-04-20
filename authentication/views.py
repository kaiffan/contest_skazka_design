from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from authentication.models import Users
from authentication.serializers import (
    RegistrationSerializer,
    LoginSerializer,
    LogoutSerializer,
)
from authentication.utils import set_refresh_cookie, delete_refresh_cookie


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        AllowAny,
    ]
)
def registration_view(request: Request) -> Response:
    serializer: RegistrationSerializer = RegistrationSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(status=status.HTTP_201_CREATED)


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        AllowAny,
    ]
)
def login_view(request: Request) -> Response:
    serializer: LoginSerializer = LoginSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    current_user: Users = serializer.validated_data

    response: Response = Response(
        data={
            "access_token": current_user.tokens.get("access"),
            "token_type": "Bearer",
            "message": "Login successful",
        },
        status=status.HTTP_200_OK,
    )

    set_refresh_cookie(response=response, value=current_user.tokens.get("refresh"))
    return response


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        AllowAny,
    ]
)
def cookie_tokens_refresh_view(request) -> Response:
    refresh_token: str = request.COOKIES.get("refresh_token")

    if not refresh_token:
        raise ValidationError("Refresh token is missing")

    token_refresh_serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

    if not token_refresh_serializer.is_valid(raise_exception=True):
        return Response(
            token_refresh_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    new_access_token: str = token_refresh_serializer.validated_data.get("access")
    new_refresh_token: str = token_refresh_serializer.validated_data.get("refresh")

    response: Response = Response(
        data={
            "access_token": new_access_token,
            "message": "Refresh successful",
        },
        status=status.HTTP_200_OK,
    )

    delete_refresh_cookie(response=response)

    set_refresh_cookie(response=response, value=new_refresh_token)

    return response


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
    ]
)
def logout_view(request: Request) -> Response:
    refresh_token: str = request.COOKIES.get("refresh_token")

    if not refresh_token:
        raise ValidationError("Refresh token not found")

    serializer = LogoutSerializer(data={}, context={"refresh_token": refresh_token})

    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    response = Response(
        data={
            "message": "Logout successful",
        },
        status=status.HTTP_200_OK,
    )
    delete_refresh_cookie(response=response)
    return response
