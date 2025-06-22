import base64
import os
import tempfile

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

User = get_user_model()


# ИСПРАВЛЕНИЕ: Используем override_settings для изоляции теста
@override_settings(MEDIA_ROOT=tempfile.gettempdir())
@pytest.mark.django_db
def test_upload_image_view(client):
    """
    Тестирует полный цикл загрузки изображения.
    """
    # 1. Подготовка (Arrange)
    user = User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")

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
    # Примечание: Мы больше не проверяем путь к файлу так строго,
    # так как он теперь во временной директории.
    assert 'src="/media/test_pixel' in response_text

    # Проверяем, что файл действительно был сохранен
    # (хотя в данном случае это менее критично, так как ОС сама управляет /tmp)
    media_dir = tempfile.gettempdir()
    saved_files = [f for f in os.listdir(media_dir) if f.startswith("test_pixel")]
    assert len(saved_files) > 0, "Файл должен быть сохранен во временной директории"