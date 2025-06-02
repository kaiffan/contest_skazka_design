from os import unlink
from tempfile import NamedTemporaryFile
from uuid import uuid4
from django.core.files.uploadedfile import UploadedFile

from config.settings import get_settings
from boto3.session import Session

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
    Загружает файл в облако (S3), предварительно проверив его формат.

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

    allowed_formats = []
    for formats in file_constraints.values():
        allowed_formats.extend([fmt.lower() for fmt in formats])

    if not allowed_formats:
        raise ValueError("Не найдено разрешённых форматов для загрузки")

    if file_extension not in allowed_formats:
        raise ValueError(
            f"Формат файла '{file_extension}' не поддерживается. "
            f"Поддерживаемые форматы: {', '.join(set(allowed_formats))}"
        )

    client = get_sesion_s3()

    cloud_file_name = f"{uuid4()}.{uploaded_file.name}"
    file_key = f"avatar/{cloud_file_name}"

    with NamedTemporaryFile(delete=False) as tmp_file:
        file_path = tmp_file.name

        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)

    try:
        client.upload_file(
            file_path,
            "skazka-design",
            file_key,
        )

    finally:
        unlink(file_path)

    endpoint_url: str = settings.yandex_s3_credentials.ENDPOINT_URL.rstrip("/")
    return f"{endpoint_url}/skazka-design/{file_key}"


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

    if type_uploads == TypeUploads.RULES.value:
        return {"rules": ["pdf", "doc", "docx"]}

    if not contest_id:
        return {"No folder": []}

    if type_uploads.value == TypeUploads.APPLICATION.value:
        contest_constraints = FileConstraint.objects.filter(contest_id=contest_id).all()

        constraint = {
            f"applications/{constraint.id}": constraint.file_formats.split(sep=",")
            for constraint in contest_constraints
        }

    return constraint
