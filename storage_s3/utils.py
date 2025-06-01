import os
import tempfile
import uuid
from io import BytesIO

from django.core.files.uploadedfile import UploadedFile

from config.settings import get_settings
from boto3.session import Session


def get_sesion_s3():
    settings = get_settings()

    session = Session()

    return session.client(
        service_name='s3',
        endpoint_url=settings.yandex_s3_credentials.ENDPOINT_URL,
        aws_access_key_id=settings.yandex_s3_credentials.ID_KEY,
        aws_secret_access_key=settings.yandex_s3_credentials.SECRET_KEY,
    )

def upload_file_to_storage(file_obj: UploadedFile, folder: str) -> str:
    settings = get_settings()
    client = get_sesion_s3()

    cloud_file_name = f"{uuid.uuid4()}.{file_obj.name}"
    file_key = f"{folder}/{cloud_file_name}"

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        file_path = tmp_file.name

        for chunk in file_obj.chunks():
            tmp_file.write(chunk)

    try:
        client.upload_file(
            file_path,
            "skazka-design",
            file_key,
        )

    finally:
        from os import unlink

        os.unlink(file_path)

    endpoint_url = settings.yandex_s3_credentials.ENDPOINT_URL.rstrip('/')
    public_url = f"{endpoint_url}/skazka-design/{file_key}"
    return public_url

