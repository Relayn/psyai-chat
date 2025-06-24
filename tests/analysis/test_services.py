from unittest.mock import MagicMock, patch
import pytest
from botocore.exceptions import ClientError

from analysis.services import detect_emotions_from_image

# Пример ответа от API, который мы будем имитировать
MOCK_API_RESPONSE = {
    "FaceDetails": [{
        "Emotions": [
            {"Type": "HAPPY", "Confidence": 99.9},
            {"Type": "CALM", "Confidence": 75.0},
        ]
    }],
    "ResponseMetadata": {"HTTPStatusCode": 200}
}


@patch('analysis.services.boto3.client')
def test_detect_emotions_success(mock_boto_client, settings):
    """
    Тестирует успешный вызов сервиса анализа эмоций.
    """
    # Arrange: Настраиваем моки
    settings.AWS_REGION = 'eu-central-1'
    mock_rekognition = MagicMock()
    mock_rekognition.detect_faces.return_value = MOCK_API_RESPONSE
    mock_boto_client.return_value = mock_rekognition

    # Act: Вызываем сервис
    image_bytes = b'fake-image-data'
    result = detect_emotions_from_image(image_bytes)

    # Assert: Проверяем, что все было вызвано как надо
    mock_boto_client.assert_called_once_with("rekognition", region_name='eu-central-1')
    mock_rekognition.detect_faces.assert_called_once_with(
        Image={"Bytes": image_bytes},
        Attributes=["ALL"]
    )
    assert result == MOCK_API_RESPONSE


@patch('analysis.services.boto3.client')
def test_detect_emotions_api_error(mock_boto_client, settings):
    """
    Тестирует обработку ошибки ClientError от API.
    """
    # Arrange
    settings.AWS_REGION = 'eu-central-1'
    error_response = {'Error': {'Code': 'InvalidParameterException', 'Message': 'Details'}}
    mock_rekognition = MagicMock()
    mock_rekognition.detect_faces.side_effect = ClientError(error_response, 'DetectFaces')
    mock_boto_client.return_value = mock_rekognition

    # Act & Assert
    with pytest.raises(ClientError):
        detect_emotions_from_image(b'fake-image-data')