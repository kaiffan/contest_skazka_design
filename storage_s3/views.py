from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from storage_s3.utils import upload_file_to_storage


@api_view(http_method_names=["POST"])
def upload_file_view(request: Request) -> Response:
    uploaded_file = request.FILES.get('file')

    if not uploaded_file:
        return Response(
            data={"error": "Файл не предоставлен"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        public_url = upload_file_to_storage(file_obj=uploaded_file, folder="image")
        return Response(data={"url": public_url}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            data={"error": f"Ошибка при загрузке файла: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
