from unittest.mock import patch
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from botocore.exceptions import ClientError

from analysis.models import ImageAnalysisResult
from analysis.tasks import analyze_image_task
from tests.utils import InMemoryStorage  # <-- ИМПОРТИРОВАТЬ

User = get_user_model()
pytestmark = pytest.mark.django_db

MOCK_API_RESPONSE = {
    "FaceDetails": [{"Emotions": [{"Type": "HAPPY", "Confidence": 99.9}]}]
}


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password")


@pytest.fixture
def image_analysis_result(user):
    from analysis.models import ImageAnalysisResult as Model

    Model._meta.get_field("source_image").storage = InMemoryStorage()
    with patch("django.core.files.storage.default_storage._wrapped", InMemoryStorage()):
        fake_image = SimpleUploadedFile("test.jpg", b"file_content", "image/jpeg")
        result = Model.objects.create(user=user, source_image=fake_image)
    return result


@patch("django.core.files.storage.default_storage._wrapped", InMemoryStorage())
@patch("analysis.tasks.detect_emotions_from_image")
def test_analyze_image_task_success(mock_detect_emotions, image_analysis_result):
    mock_detect_emotions.return_value = MOCK_API_RESPONSE

    analyze_image_task(image_analysis_result.id)

    image_analysis_result.refresh_from_db()
    mock_detect_emotions.assert_called_once()
    assert image_analysis_result.status == ImageAnalysisResult.Status.COMPLETED
    assert image_analysis_result.result_payload == MOCK_API_RESPONSE
    assert image_analysis_result.error_message is None


@patch("django.core.files.storage.default_storage._wrapped", InMemoryStorage())
@patch("analysis.tasks.detect_emotions_from_image")
def test_analyze_image_task_failure(mock_detect_emotions, image_analysis_result):
    error_response = {"Error": {"Code": "SomeError", "Message": "Something went wrong"}}
    mock_detect_emotions.side_effect = ClientError(error_response, "DetectFaces")

    analyze_image_task(image_analysis_result.id)

    image_analysis_result.refresh_from_db()
    assert image_analysis_result.status == ImageAnalysisResult.Status.FAILED
    assert image_analysis_result.result_payload is None
    assert "Something went wrong" in image_analysis_result.error_message
