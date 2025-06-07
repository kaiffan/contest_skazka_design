from os import unlink
from tempfile import NamedTemporaryFile
from uuid import uuid4
from django.core.files.uploadedfile import UploadedFile

from config.settings import get_settings
from boto3.session import Session

from contest_file_constraints.models import ContestFileConstraints
from contests.models import Contest
from file_constraints.models import FileConstraint
from storage_s3.enums import TypeUploads

settings = get_settings()


def get_sesion_s3():
    session = Session()

    return session.client(
        service_name="s3",
        endpoint_url=settings.yandex_s3_credentials.ENDPOINT_URL,
        aws_access_key_id=settings.yandex_s3_credentials.ID_KEY,
        aws_secret_access_key=settings.yandex_s3_credentials.SECRET_KEY,
    )


def upload_file_to_storage(
    uploaded_file: UploadedFile, file_constraints: dict[str, list[str]]
) -> str:
    """
    Загружает файл в облако (например, S3), предварительно проверив его формат.

    Аргументы:
        uploaded_file (UploadedFile): Загруженный пользователем файл.
        file_constraints (Dict[str, List[str]]): Ограничения на форматы файлов.

    Возвращает:
        str: Публичный URL файла в хранилище.
    """
    try:
        file_extension = uploaded_file.name.rsplit(sep=".", maxsplit=1)[1].lower()
    except IndexError:
        raise ValueError("Файл не имеет расширения")

    normalized_constraints = {
        folder: {ext.lower() for ext in formats}
        for folder, formats in file_constraints.items()
    }

    target_folder = next(
        (
            folder
            for folder, formats in normalized_constraints.items()
            if file_extension in formats
        ),
        None,
    )

    if not target_folder:
        allowed_extensions = sorted(
            {ext for formats in normalized_constraints.values() for ext in formats}
        )
        raise ValueError(
            f"Формат файла '{file_extension}' не поддерживается. "
            f"Допустимые форматы: {', '.join(allowed_extensions)}"
        )

    client = get_sesion_s3()

    unique_filename = f"{uuid4()}.{file_extension}"
    file_key = f"{target_folder}/{unique_filename}"

    with NamedTemporaryFile(delete=False) as tmp_file:
        file_path = tmp_file.name

        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)

    try:
        client.upload_file(
            file_path,
            settings.yandex_s3_credentials.BACKET_NAME,
            file_key,
        )

    finally:
        unlink(file_path)

    endpoint_url: str = settings.yandex_s3_credentials.ENDPOINT_URL.rstrip("/")
    return f"{endpoint_url}/{settings.yandex_s3_credentials.BACKET_NAME}/{file_key}"


def get_file_constraint_by_type(
    type_uploads: TypeUploads, contest_id: int | None
) -> dict[str, list[str]]:
    """
    Возвращает словарь с разрешёнными форматами файлов для указанного типа загрузки.

    Пример:
        >>> get_file_constraint_by_type(TypeUploads.AVATAR, None)
        {'avatars': ['jpg', 'jpeg', 'png', 'webp']}

    Аргументы:
        type_uploads (str): Тип загрузки ('avatar', 'rules' или пользовательский).
        contest_id (Optional[int]): ID контеста для получения пользовательских ограничений.

    Возвращает:
        Dict[str, List[str]]: Словарь вида {"путь/к/папке": ["формат1", "формат2"]}
    """
    if type_uploads.value == TypeUploads.AVATAR.value:
        return {"avatars": ["jpg", "jpeg", "png", "webp"]}

    if type_uploads.value == TypeUploads.RULES.value:
        return {"rules": ["pdf", "doc", "docx"]}

    if not contest_id:
        return {"No folder": []}

    if type_uploads.value == TypeUploads.APPLICATION.value:
        contest = Contest.objects.get(id=contest_id)
        contest_constraints = ContestFileConstraints.objects.filter(
            contest=contest
        ).all()

        return {
            f"applications/{constraint.file_constraints.name}": constraint.file_constraints.file_formats.split(
                sep=","
            )
            for constraint in contest_constraints
        }
