from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from block_user.permissions import IsNotBlockUserPermission
from storage_s3.enums import TypeUploads
from storage_s3.success_error_type import FileUploadResult, Success
from storage_s3.utils import upload_file_to_storage, get_file_constraint_by_type


@extend_schema(
    summary="Загрузка файла любого типа",
    description="Загружает файл на сервер с проверкой по ограничениям, зависящим от типа загрузки.",
    parameters=[
        OpenApiParameter(
            name="file",
            type=OpenApiTypes.BINARY,
            location="query",
            description="Файл для загрузки",
        ),
        OpenApiParameter(
            name="upload_type",
            type=OpenApiTypes.STR,
            location="query",
            description='Тип загрузки (например: "application", "photo")',
        ),
    ],
    responses={
        201: {
            "type": "object",
            "properties": {"link_to_file": {"type": "string", "format": "uri"}},
        },
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример запроса (multipart/form-data)",
            value={"file": "example.jpg", "upload_type": "application"},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={"link_to_file": "https://storage.example.com/files/example.jpg"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Файл не предоставлен",
            value={"error": "Файл не предоставлен"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Некорректный тип загрузки",
            value={
                "error": "Некорректный тип загрузки. Допустимые значения: ['application', 'photo', 'document']"
            },
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def upload_file_view(request: Request) -> Response:
    uploaded_file = request.FILES.get("file")
    upload_type: str = request.data.get("upload_type", None)

    if not uploaded_file:
        return Response(
            data={"error": "Файл не предоставлен"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not upload_type:
        return Response(
            data={"error": "Тип файла отсутствует"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        type_uploads: TypeUploads = TypeUploads(upload_type)
    except ValueError:
        return Response(
            data={
                "error": f"Некорректный тип загрузки. Допустимые значения: {[t.value for t in TypeUploads]}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    file_constraints: dict[str, list[str]] = get_file_constraint_by_type(
        type_uploads=type_uploads, contest_id=None
    )

    result: FileUploadResult = upload_file_to_storage(
        uploaded_file=uploaded_file, file_constraints=file_constraints
    )

    if isinstance(result, Success):
        return Response(
            data={"link_to_file": result.value}, status=status.HTTP_201_CREATED
        )
    return Response(data={"error": result.message}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Загрузка конкурсной работы",
    description="Загружает файл заявки на конкурс с учетом ограничений по типу и конкурсу.",
    parameters=[
        OpenApiParameter(
            name="file",
            type=OpenApiTypes.BINARY,
            location="path",
            description="Файл заявки",
        ),
        OpenApiParameter(
            name="upload_type",
            type=OpenApiTypes.STR,
            location="path",
            description='Тип загрузки (должен быть "application")',
        ),
        OpenApiParameter(
            name="contest_id",
            type=OpenApiTypes.INT,
            location="path",
            description="ID конкурса",
        ),
    ],
    responses={
        201: {
            "type": "object",
            "properties": {"link_to_file": {"type": "string", "format": "uri"}},
        },
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    examples=[
        OpenApiExample(
            name="Пример запроса (multipart/form-data)",
            value={"file": "work.zip", "upload_type": "application", "contest_id": 1},
            request_only=True,
        ),
        OpenApiExample(
            name="Успешный ответ",
            value={"link_to_file": "https://storage.example.com/files/work.zip"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: contest_id не задан",
            value={"error": "contest_id не задан"},
            response_only=True,
        ),
        OpenApiExample(
            name="Ошибка: Неподдерживаемый тип загрузки",
            value={"error": "Данный тип заявки не поддерживается"},
            response_only=True,
        ),
    ],
)
@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated, IsNotBlockUserPermission])
def upload_contest_work_view(request: Request) -> Response:
    uploaded_file = request.FILES.get("file")
    upload_type: str = request.data.get("upload_type", None)
    contest_id = request.data.get("contest_id", None)

    if not contest_id:
        return Response(
            data={"error": "contest_id не задан"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not uploaded_file:
        return Response(
            data={"error": "Файл не предоставлен"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        type_uploads: TypeUploads = TypeUploads(upload_type)
    except ValueError:
        return Response(
            data={
                "error": f"Некорректный тип загрузки. Допустимые значения: {[t.value for t in TypeUploads]}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if upload_type != TypeUploads.APPLICATION.value:
        return Response(
            data={"error": "Данный тип заявки не поддерживается"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    file_constraints: dict[str, list[str]] = get_file_constraint_by_type(
        type_uploads=type_uploads, contest_id=contest_id
    )

    result: FileUploadResult = upload_file_to_storage(
        uploaded_file=uploaded_file, file_constraints=file_constraints
    )

    if isinstance(result, Success):
        return Response(
            data={"link_to_file": result.value}, status=status.HTTP_201_CREATED
        )
    return Response(data={"error": result.message}, status=status.HTTP_400_BAD_REQUEST)
