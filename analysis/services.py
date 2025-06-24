import boto3
from botocore.exceptions import ClientError
from django.conf import settings


def detect_emotions_from_image(image_bytes: bytes) -> dict:
    """
    Отправляет изображение в Amazon Rekognition для анализа лиц и эмоций.

    Args:
        image_bytes: Изображение в виде байтовой строки.

    Returns:
        Словарь с полным ответом от API Rekognition.

    Raises:
        ClientError: В случае ошибки API, которую можно обработать выше.
        ValueError: Если не удалось настроить клиент (нет региона).
    """
    if not settings.AWS_REGION:
        raise ValueError("Необходимо указать регион AWS в настройках (AWS_REGION).")

    rekognition_client = boto3.client(
        "rekognition", region_name=settings.AWS_REGION
    )

    # ClientError будет перехвачен в Celery-задаче
    response = rekognition_client.detect_faces(
        Image={"Bytes": image_bytes},
        Attributes=["ALL"],  # 'ALL' включает в себя анализ эмоций
    )

    return response