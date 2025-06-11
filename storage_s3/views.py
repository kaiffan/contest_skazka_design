from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from block_user.permissions import IsNotBlockUserPermission
from storage_s3.enums import TypeUploads
from storage_s3.success_error_type import FileUploadResult, Success
from storage_s3.utils import upload_file_to_storage, get_file_constraint_by_type


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
