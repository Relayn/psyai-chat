import base64
import os

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_upload_image_view(client):
    """
    Тестирует полный цикл загрузки изображения:
    1. Создает и логинит пользователя.
    2. Имитирует POST-запрос с валидным файлом-изображением.
    3. Проверяет, что форма валидна и ответ сервера корректен.
    4. Проверяет, что в контексте шаблона есть URL файла и результат анализа.
    5. Проверяет, что в HTML-ответе отображаются результаты.
    6. Проверяет, что файл физически сохранен в папке media.
    7. Удаляет созданный файл после теста.
    """
    # 1. Подготовка (Arrange)
    user = User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")

    # --- ИСПРАВЛЕНО: Используем контент реального 1x1 GIF-изображения ---
    # Причина: forms.ImageField проверяет, что файл является валидным изображением.
    # Мы создаем минимально возможное изображение, чтобы пройти эту проверку.
    gif_content = base64.b64decode(
        b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    )
    fake_image = SimpleUploadedFile(
        name="test_pixel.gif",
        content=gif_content,
        content_type="image/gif",
    )

    upload_url = reverse("mocks:image_analysis")

    # 2. Действие (Act)
    response = client.post(upload_url, {"image": fake_image})

    # 3. Проверка (Assert)
    assert response.status_code == 200, "Страница должна успешно обработать POST-запрос"
    assert "form" in response.context
    assert "uploaded_file_url" in response.context, "В контексте должен быть URL файла"
    assert "analysis_result" in response.context, "В контексте должен быть результат анализа"

    response_text = response.content.decode("utf-8")
    assert "<h3>Результаты анализа:</h3>" in response_text
    assert 'src="/media/test_pixel' in response_text

    # Проверяем, что файл действительно был сохранен
    media_dir = settings.MEDIA_ROOT
    saved_files = [f for f in os.listdir(media_dir) if f.startswith("test_pixel")]
    assert len(saved_files) > 0, "Файл должен быть сохранен на диске"
    saved_file_path = os.path.join(media_dir, saved_files[0])

    # 4. Очистка (Cleanup)
    if os.path.exists(saved_file_path):
        os.remove(saved_file_path)