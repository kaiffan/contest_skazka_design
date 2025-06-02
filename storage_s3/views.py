from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from participants.permissions import IsContestOwnerPermission, IsOrgCommitteePermission
from storage_s3.enums import TypeUploads
from storage_s3.utils import upload_file_to_storage, get_file_constraint_by_type


@api_view(http_method_names=["POST"])
@permission_classes(permission_classes=[IsAuthenticated])
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

    try:
        file_url: str = upload_file_to_storage(
            uploaded_file=uploaded_file, file_constraints=file_constraints
        )
        return Response(data={"link_to_file": file_url}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            data={"error": f"Ошибка при загрузке файла: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(http_method_names=["POST"])
@permission_classes(
    permission_classes=[
        IsAuthenticated,
        IsContestOwnerPermission,
        IsOrgCommitteePermission,
    ]
)
def upload_contest_work_view(request: Request) -> Response:
    uploaded_file = request.FILES.get("file")
    upload_type: str = request.data.get("upload_type", None)
    contest_id = request.contest_id

    if not uploaded_file:
        return Response(
            data={"error": "Файл не предоставлен"}, status=status.HTTP_400_BAD_REQUEST
        )

    if upload_type != TypeUploads.APPLICATION.value:
        return Response(
            data={"error": "Данный тип файла не поддерживается"},
            status=status.HTTP_400_BAD_REQUEST,
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
        type_uploads=type_uploads, contest_id=contest_id
    )

    try:
        file_url: str = upload_file_to_storage(
            uploaded_file=uploaded_file, file_constraints=file_constraints
        )
        return Response(data={"link_to_file": file_url}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            data={"error": f"Ошибка при загрузке файла: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
