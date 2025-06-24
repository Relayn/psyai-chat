from unittest.mock import patch
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from analysis.models import ImageAnalysisResult
from tests.utils import InMemoryStorage

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True, scope="module")
def patch_imagefield_storage():
    from analysis.models import ImageAnalysisResult as Model

    Model._meta.get_field("source_image").storage = InMemoryStorage()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password")


@patch("django.core.files.storage.default_storage._wrapped", InMemoryStorage())
@patch("analysis.views.analyze_image_task.delay")
def test_upload_image_view_success(mock_task_delay, client, user):
    """
    Тестирует, что view успешно создает объект и запускает задачу.
    """
    client.login(username="testuser", password="password")
    upload_url = reverse("analysis:upload_image")

    img_bytes = io.BytesIO()
    image = Image.new("RGB", (10, 10), color="red")
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    fake_image = SimpleUploadedFile("test.png", img_bytes.read(), "image/png")

    response = client.post(upload_url, {"image": fake_image})

    if ImageAnalysisResult.objects.count() != 1:
        print(
            "FORM ERRORS:",
            (
                response.context["form"].errors
                if hasattr(response, "context") and response.context
                else None
            ),
        )
        print("RESPONSE CONTENT:", response.content)
    assert ImageAnalysisResult.objects.count() == 1
    result = ImageAnalysisResult.objects.first()
    assert result.user == user
    assert result.status == ImageAnalysisResult.Status.PENDING

    mock_task_delay.assert_called_once_with(result.id)

    assert response.status_code == 302
    assert response.url == reverse("analysis:analysis_result", args=[result.id])
