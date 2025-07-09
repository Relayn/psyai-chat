from celery import shared_task

from .models import ImageAnalysisResult
from .services import detect_emotions_from_image


@shared_task
def analyze_image_task(result_id: int):
    """
    Асинхронная задача для анализа изображения с помощью Amazon Rekognition.
    """
    try:
        result = ImageAnalysisResult.objects.get(id=result_id)

        # Безопасно открываем файл перед чтением (важно для тестов и реального кода)
        if result.source_image.closed:
            result.source_image.open("rb")
        image_bytes = result.source_image.read()
        result.source_image.close()

        # Вызываем наш сервис для получения анализа
        api_response = detect_emotions_from_image(image_bytes=image_bytes)

        # Обновляем запись в БД в случае успеха
        result.status = ImageAnalysisResult.Status.COMPLETED
        result.result_payload = api_response
        result.save()

    except ImageAnalysisResult.DoesNotExist:
        print(f"Ошибка в задаче: ImageAnalysisResult с ID {result_id} не найден.")
        # Здесь задача просто завершается, так как исправлять нечего.

    except Exception as e:
        # Ловим специфичные ошибки от boto3 и общие исключения
        print(f"Ошибка при анализе изображения (ID: {result_id}): {e}")
        if "result" in locals():
            result.status = ImageAnalysisResult.Status.FAILED
            result.error_message = str(e)
            result.save()
